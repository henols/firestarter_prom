# Phase 18: Beta-Aware Firmware Downloader - Pattern Map

**Mapped:** 2026-05-20
**Files analyzed:** 5 (4 modified + 1 new)
**Analogs found:** 4 / 5 (one new file has partial analog)

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `firestarter_app/firestarter/firmware.py` | service | request-response | itself (extend in-place) | exact — primary target |
| `firestarter_app/firestarter/main.py` | controller | request-response | itself (extend in-place) | exact — primary target |
| `firestarter_app/firestarter/constants.py` | config | — | itself (extend in-place) | exact — additive only |
| `firestarter_app/pyproject.toml` | config | — | itself (extend in-place) | exact — additive only |
| `firestarter_app/tests/test_firmware_install.py` | test | request-response | `firestarter_app/tests/test_update_version.py` + `firestarter_app/tests/test_fwguard.py` | role-match |

---

## Pattern Assignments

### `firestarter_app/firestarter/firmware.py` (service, request-response — extend in-place)

**Primary analog:** itself. The file is read in full above (lines 1–408). Specific sections documented below.

#### 1a. `fetch_latest_release_info` — THE template for `fetch_release_info` (lines 101–133)

```python
def fetch_latest_release_info(
    self, board: str = "uno"
) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetches the latest firmware version and download URL for the specified board.
    Returns: (latest_version_str, download_url_str) or (None, None) on failure.
    """
    logger.debug(f"Fetching latest firmware release for board: {board}...")
    try:
        response = requests.get(FIRESTARTER_RELEASE_URL, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        release_data = response.json()
        latest_version = release_data.get("tag_name")
        firmware_asset_name = f"firestarter_{board}.hex"
        download_url = None
        for asset in release_data.get("assets", []):
            if asset.get("name") == firmware_asset_name:
                download_url = asset.get("browser_download_url")
                break

        if not latest_version or not download_url:
            logger.error(
                f"Could not find firmware version or URL for board '{board}' in the latest release."
            )
            return None, None

        logger.debug(
            f"Latest firmware version for {board}: {latest_version}, URL: {download_url}"
        )
        return latest_version, download_url
    except requests.RequestException as e:
        logger.error(f"Failed to fetch latest firmware release information: {e}")
        return None, None
```

**Contract the new `fetch_release_info` must replicate:**
- Same return type: `Tuple[Optional[str], Optional[str]]` — `(version, url)` or `(None, None)`.
- `requests.get(url, timeout=10)` + `response.raise_for_status()` + `response.json()`.
- Asset name pattern: `f"firestarter_{board}.hex"` — the publisher-consumer contract.
- Asset-resolution loop: iterate `release_data.get("assets", [])`, match `asset.get("name")`, take `asset.get("browser_download_url")`.
- `logger.error(...)` on missing version or missing URL; `return None, None` — never raise.
- `except requests.RequestException` at the outer level — catches all HTTP errors.

**New `fetch_release_info` adds three routing branches:**
- `channel='stable'` → delegates to `fetch_latest_release_info` (shim call, line 322 pattern).
- `channel='pinned'` → `requests.get(FIRESTARTER_RELEASE_BY_TAG_URL.format(tag=version), timeout=10)` → same asset-resolution loop → 404 raises `HTTPError` (via `raise_for_status`) → fatal log + `return None, None`.
- `channel='pre'` → `_fetch_all_releases()` helper → filter `prerelease=True and not draft` → parse `tag_name` via `packaging.version.Version`, discard failures → sort descending → resolve asset → fallback to `stable` if zero candidates (log INFO per D-05).

**Docstring update to add to existing `fetch_latest_release_info`** (D-15):
```python
"""Stable-only path; use `fetch_release_info` for general channel selection."""
```

#### 1b. `_compare_versions` — function being replaced (lines 135–149)

Current implementation (the broken one, to be replaced):
```python
def _compare_versions(
    self, current_version_str: str | None, latest_version_str: str | None
) -> bool:
    """Compares two version strings (e.g., "1.2.3"). Returns True if current >= latest."""
    if not current_version_str or not latest_version_str:
        return False  # Cannot compare if one is missing
    try:
        current = tuple(map(int, current_version_str.split(".")))
        latest = tuple(map(int, latest_version_str.split(".")))
        return current >= latest
    except ValueError:
        logger.warning(
            f"Could not parse version strings for comparison: '{current_version_str}', '{latest_version_str}'"
        )
        return False  # Treat as not up-to-date if parsing fails
```

**Replacement body** (from RESEARCH.md Pattern 4, VERIFIED via shell):
```python
from packaging.version import Version, InvalidVersion

def _compare_versions(
    self, current_version_str: str | None, latest_version_str: str | None
) -> bool:
    """Compares two version strings. Returns True if current >= latest.
    PEP 440-safe via packaging.version.Version."""
    if not current_version_str or not latest_version_str:
        return False
    try:
        return Version(current_version_str) >= Version(latest_version_str)
    except InvalidVersion:
        logger.warning(
            f"Could not parse version strings for comparison: "
            f"{current_version_str!r}, {latest_version_str!r}"
        )
        return False
```

**Only caller:** `firmware.py` line 335 inside `manage_firmware_update`:
```python
is_up_to_date = self._compare_versions(current_version, latest_version)
```
No external callers — the refactor is fully localized.

#### 1c. `manage_firmware_update` — orchestrator to extend (lines 294–302)

Current signature (lines 294–302):
```python
def manage_firmware_update(
    self,
    install_flag: bool = False,
    avrdude_path_override: Optional[str] = None,
    avrdude_config_override: Optional[str] = None,
    port_override: Optional[str] = None,
    board_override: Optional[str] = "uno",
    flags: int = 0,
) -> bool:
```

New args to add at end (D-18), preserving all existing kwargs with their defaults:
```python
    channel: Literal['stable', 'pre', 'pinned'] = 'stable',
    pinned_version: Optional[str] = None,
```

Current dispatch (lines 322–324) to be replaced:
```python
latest_version, download_url = self.fetch_latest_release_info(
    board=board_to_use
)
```

Replacement: route through `fetch_release_info`:
```python
latest_version, download_url = self.fetch_release_info(
    channel=channel,
    version=pinned_version,
    board=board_to_use,
)
```

#### 1d. Imports block (lines 1–33) — new imports to add

Add after `from typing import Optional, Tuple` (line 14):
```python
from typing import Optional, Tuple, Literal, List, TypedDict
```

Add after existing imports, before `logger = ...`:
```python
import re
from packaging.version import Version, InvalidVersion
```

Add `FIRMWARE_VERSION_RE` constant at module level (after logger, before class):
```python
FIRMWARE_VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+((b|rc)[0-9]+)?$')
```

---

### `firestarter_app/firestarter/main.py` (controller, request-response — extend in-place)

**Primary analog:** itself. Two specific sections must be extended.

#### 2a. `create_firmware_args` — current shape (lines 192–228)

Full current function to be restructured:
```python
def create_firmware_args(parser):
    fw_parser = parser.add_parser("fw", help="Firmware version.")
    fw_parser.add_argument(
        "-i",
        "--install",
        action="store_true",
        help="Try to install the latest firmware.",
    )
    fw_parser.add_argument(
        "-b",
        "--board",
        type=str,
        default="uno",
        choices=["uno", "leonardo"],
        help="Microcontroller board (optional), defaults to 'uno'.",
    )
    fw_parser.add_argument(
        "--avrdude-path",
        type=str,
        help="Full path to avrdude (optional), set if avrdude is not found.",
    )
    fw_parser.add_argument(
        "-c",
        "--avrdude-config-path",
        type=str,
        help="Full path to avrdude config (optional), set if avrdude version is 6.3 or not found.",
    )
    fw_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Will install firmware even if the version is the same.",
    )
```

**Restructured version** (from RESEARCH.md Pattern 1 + Finding 3, VERIFIED via shell):

Critical: `-i/--install` must move OUT of `fw_parser.add_argument` and INTO a mutex group. Flags cannot be retroactively moved to a mutex group in argparse.

```python
def create_firmware_args(parser):
    fw_parser = parser.add_parser("fw", help="Firmware version.")

    # Mutex group 2 (defined FIRST because -i/--install must join it from inception):
    # --list XOR -i/--install
    install_group = fw_parser.add_mutually_exclusive_group()
    install_group.add_argument(
        "-i",
        "--install",
        action="store_true",
        help="Try to install the latest firmware.",
    )
    install_group.add_argument(
        "--list",
        action="store_true",
        help="List available firmware releases for the configured board.",
    )

    # Mutex group 1: --pre XOR --firmware-version
    channel_group = fw_parser.add_mutually_exclusive_group()
    channel_group.add_argument(
        "--pre",
        action="store_true",
        help="Fetch latest pre-release firmware (mirrors pip install --pre).",
    )
    channel_group.add_argument(
        "--firmware-version",
        type=_validate_firmware_version,
        metavar="VERSION",
        help="Pin exact firmware version (e.g. 3.1.0, 3.1.0b2, 3.1.0rc1).",
    )

    # Non-mutex flags (unchanged from current)
    fw_parser.add_argument(
        "-b",
        "--board",
        type=str,
        default="uno",
        choices=["uno", "leonardo"],
        help="Microcontroller board (optional), defaults to 'uno'.",
    )
    fw_parser.add_argument(
        "--avrdude-path",
        type=str,
        help="Full path to avrdude (optional), set if avrdude is not found.",
    )
    fw_parser.add_argument(
        "-c",
        "--avrdude-config-path",
        type=str,
        help="Full path to avrdude config (optional), set if avrdude version is 6.3 or not found.",
    )
    fw_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Will install firmware even if the version is the same.",
    )
    fw_parser.add_argument(
        "--json",
        action="store_true",
        help="Output --list results as JSON array.",
    )

    return fw_parser  # MUST return for fw_parser.error() in dispatch scope
```

**`_validate_firmware_version` helper** (module-level function, defined before `create_firmware_args`, RESEARCH.md Pattern 2):
```python
def _validate_firmware_version(value: str) -> str:
    """Argparse type= validator for --firmware-version. Rejects before network call."""
    from firestarter.firmware import FIRMWARE_VERSION_RE
    if not FIRMWARE_VERSION_RE.match(value):
        raise argparse.ArgumentTypeError(
            f"Invalid firmware version {value!r}. "
            "Expected X.Y.Z, X.Y.ZbN, or X.Y.ZrcN (e.g. 3.1.0, 3.1.0b2, 3.1.0rc1)."
        )
    return value
```

**Change to call site:** wherever `create_firmware_args(subparsers)` is called, capture the return:
```python
fw_parser = create_firmware_args(subparsers)
```

#### 2b. `fw` dispatch — current block (lines 645–657)

Current shape:
```python
elif args.command == "fw":
    return (
        1
        if not firmware_manager.manage_firmware_update(
            install_flag=args.install,
            avrdude_path_override=args.avrdude_path,
            avrdude_config_override=args.avrdude_config_path,
            port_override=args.port,
            board_override=args.board,
            flags=build_arg_flags(args)
        )
        else 0
    )
```

**Replacement shape** (from RESEARCH.md Architecture Patterns + D-22, all VERIFIED):
```python
elif args.command == "fw":
    # 1. Post-parse: --json requires --list (RESEARCH.md Finding 4)
    if args.json and not args.list:
        fw_parser.error("--json requires --list")

    # 2. --list path: read-only enumeration, no install
    if args.list:
        channel_filter = "pre" if args.pre else "stable" if getattr(args, "stable", False) else "all"
        releases = firmware_manager.list_releases(
            channel_filter=channel_filter,
            board=args.board,
        )
        if args.json:
            import json
            print(json.dumps(releases, indent=2))
        else:
            # Plain text table: Version / Channel / Published / Asset URL
            print(f"{'Version':<12} {'Channel':<14} {'Published':<22} Asset URL")
            for r in releases:
                print(f"{r['version']:<12} {r['channel']:<14} {r['published']:<22} {r['asset_url']}")
        return 0

    # 3. Install path: magic-default beta detection (D-21 / D-22)
    if args.install and not args.pre and not getattr(args, "firmware_version", None):
        try:
            import firestarter as _pkg
            from packaging.version import Version, InvalidVersion
            try:
                if Version(_pkg.__version__).is_prerelease:
                    args.pre = True
                    logger.info(
                        "Beta app detected — defaulting to --pre. "
                        "Use --firmware-version X.Y.Z to pin a stable version."
                    )
            except InvalidVersion:
                pass  # Truly malformed __version__ — treat as stable, no magic
        except ImportError:
            pass  # Defensive: if firestarter can't be imported, no magic

    # 4. Determine channel
    if getattr(args, "firmware_version", None):
        channel = "pinned"
    elif args.pre:
        channel = "pre"
    else:
        channel = "stable"

    return (
        1
        if not firmware_manager.manage_firmware_update(
            install_flag=args.install,
            avrdude_path_override=args.avrdude_path,
            avrdude_config_override=args.avrdude_config_path,
            port_override=args.port,
            board_override=args.board,
            flags=build_arg_flags(args),
            channel=channel,
            pinned_version=getattr(args, "firmware_version", None),
        )
        else 0
    )
```

---

### `firestarter_app/firestarter/constants.py` (config — additive only)

**Analog:** itself. Current `FIRESTARTER_RELEASE_URL` (lines 8–10):
```python
FIRESTARTER_RELEASE_URL = (
    "https://api.github.com/repos/henols/firestarter/releases/latest"
)
```

**New constants to add immediately after line 10** (same multiline parenthesized string style):
```python
FIRESTARTER_RELEASES_URL = (
    "https://api.github.com/repos/henols/firestarter/releases"
)
FIRESTARTER_RELEASE_BY_TAG_URL = (
    "https://api.github.com/repos/henols/firestarter/releases/tags/{tag}"
)
```

No other changes to this file. The `FIRMWARE_VERSION_RE` regex constant lives in `firmware.py` (where it's defined once and importable by `main.py` via `from firestarter.firmware import FIRMWARE_VERSION_RE`), not in `constants.py` — that file holds only protocol constants.

---

### `firestarter_app/pyproject.toml` (config — additive only)

**Analog:** itself. Current `[project.dependencies]` (lines 48–54):
```toml
dependencies = [
    "pyserial>=3.5",
    "requests>=2.20",
    "tqdm>=4.60",
    "argcomplete>=3.6.2",
    "rich>=14.0",
]
```

**New entry to add** (D-14):
```toml
dependencies = [
    "pyserial>=3.5",
    "requests>=2.20",
    "tqdm>=4.60",
    "argcomplete>=3.6.2",
    "rich>=14.0",
    "packaging>=21.0",
]
```

---

### `firestarter_app/tests/test_firmware_install.py` (test — new file)

**Primary analog:** `firestarter_app/tests/test_update_version.py` (lines 1–380, Phase 15 pattern)
**Secondary analog:** `firestarter_app/tests/test_fwguard.py` (lines 1–126, Phase 6 pattern)

#### 3a. File-level imports pattern (from `test_fwguard.py` lines 1–28, `test_update_version.py` lines 1–33)

```python
"""Phase 18 — test_firmware_install.py
Covers INST-01..04, TestVersionComparator, TestMagicDefault.
All network calls mocked via monkeypatch.setattr on firmware.requests.
"""
import json
import pytest
from unittest.mock import MagicMock

from firestarter import firmware
from firestarter.firmware import FirmwareManager
```

**Note:** Use `monkeypatch.setattr(firmware.requests, "get", ...)` (attribute on module object), not `unittest.mock.patch`. This matches `test_update_version.py`'s `monkeypatch.setattr(update_version.subprocess, "run", ...)` pattern (line 243) and RESEARCH.md Pattern 7.

#### 3b. `autouse` env-cleanup fixture pattern (from `test_fwguard.py` lines 34–42, `test_update_version.py` lines 47–56)

```python
class TestFirmwareInstallStable:
    """INST-01 — stable path non-regression; _compare_versions PEP 440 correctness."""

    @pytest.fixture(autouse=True)
    def _isolate_env(self, monkeypatch):
        """Clear any env state before each test.
        Tests that need specific env state call monkeypatch.setenv(...) AFTER
        this autouse fixture has cleared it — same pattern as test_fwguard.py."""
        monkeypatch.delenv("FIRESTARTER_DEV_ALLOW_PRE_V12", raising=False)
        # add any other env vars Phase 18 tests might pollute
```

Every test class in the new file must have its own `_isolate_env` autouse fixture. The fixture name `_isolate_env` is established by `test_update_version.py` (lines 48, 146, 295).

#### 3c. `mock_releases_factory` helper — module-level, NOT in conftest.py

The helper is self-contained in the test file (RESEARCH.md Pattern 7, VERIFIED via shell):

```python
def mock_releases_factory(releases, next_url=None):
    """Build a MagicMock with the shape requests.get() returns for /releases endpoints.

    Args:
        releases: list of release dicts (GitHub API shape).
        next_url: if set, includes a Link: rel="next" header to simulate pagination.

    Returns a MagicMock with .json(), .raise_for_status(), .headers, .iter_content() set.
    """
    mock = MagicMock()
    mock.json.return_value = releases
    mock.raise_for_status.return_value = None
    mock.headers = (
        {"Link": f'<{next_url}>; rel="next"'} if next_url else {}
    )
    mock.iter_content.return_value = iter([b"fake hex data"])
    return mock
```

For a 404 response (by-tag not found), set `raise_for_status` to raise:
```python
def mock_404_response():
    mock = MagicMock()
    mock.raise_for_status.side_effect = __import__("requests").exceptions.HTTPError(
        response=MagicMock(status_code=404)
    )
    return mock
```

#### 3d. Class layout and monkeypatch usage pattern

Following `test_update_version.py` class structure and `test_fwguard.py` mock setup:

```python
class TestVersionComparator:
    """INST-01 — _compare_versions handles PEP 440 pre-release strings correctly."""

    @pytest.fixture(autouse=True)
    def _isolate_env(self, monkeypatch):
        pass  # no env to clear for pure unit tests

    def test_stable_versions(self):
        fm = FirmwareManager(config_manager=MagicMock())
        assert fm._compare_versions("3.0.0", "3.0.0") is True
        assert fm._compare_versions("3.0.0", "2.9.9") is True
        assert fm._compare_versions("2.9.9", "3.0.0") is False

    def test_prerelease_versions(self):
        """b10 > b9 only with Version sort (RESEARCH.md Finding 2, VERIFIED)."""
        fm = FirmwareManager(config_manager=MagicMock())
        assert fm._compare_versions("3.1.0b10", "3.1.0b9") is True
        assert fm._compare_versions("3.1.0rc1", "3.1.0b10") is True
        assert fm._compare_versions("3.0.0", "3.1.0b2") is False

    def test_invalid_version_returns_false(self):
        fm = FirmwareManager(config_manager=MagicMock())
        assert fm._compare_versions("not-a-version", "3.0.0") is False


class TestFirmwareInstallPreRelease:
    """INST-02 — fetch_release_info(channel='pre') selects highest pre-release."""

    @pytest.fixture(autouse=True)
    def _isolate_env(self, monkeypatch):
        pass

    def test_pre_release_selection(self, monkeypatch):
        page1 = mock_releases_factory([
            {
                "tag_name": "3.1.0b2", "prerelease": True, "draft": False,
                "published_at": "2026-05-20T10:00:00Z",
                "assets": [{"name": "firestarter_uno.hex",
                             "browser_download_url": "https://example.com/uno_b2.hex"}],
            },
            {
                "tag_name": "3.0.0", "prerelease": False, "draft": False,
                "published_at": "2026-05-01T10:00:00Z",
                "assets": [{"name": "firestarter_uno.hex",
                             "browser_download_url": "https://example.com/uno_stable.hex"}],
            },
        ])
        monkeypatch.setattr(firmware.requests, "get", lambda *a, **kw: page1)
        fm = FirmwareManager(config_manager=MagicMock())
        version, url = fm.fetch_release_info(channel="pre", board="uno")
        assert version == "3.1.0b2"
        assert "uno_b2.hex" in url
```

---

## Shared Patterns

### HTTP request pattern
**Source:** `firestarter_app/firestarter/firmware.py` lines 109–132
**Apply to:** all new `FirmwareManager` methods that call `requests.get`

```python
response = requests.get(url, timeout=10)
response.raise_for_status()
data = response.json()
```

Always `timeout=10` for metadata endpoints. `requests.RequestException` at outer except level catches all failures. Never inspect `response.json()["message"]` for error detection — use `raise_for_status()`.

### Logger naming pattern
**Source:** `firestarter_app/firestarter/firmware.py` line 33
**Apply to:** all new methods in `FirmwareManager`

```python
logger = logging.getLogger("Firmware")
```

Operator-visible state → `logger.info(...)`. Debug noise → `logger.debug(...)`. Errors → `logger.error(...)`. Parse-failure warnings → `logger.warning(...)`.

### (None, None) failure return
**Source:** `firestarter_app/firestarter/firmware.py` lines 122–125 and 131–133
**Apply to:** `fetch_release_info`, `list_releases` (empty list for list; `(None, None)` for release info)

Methods never raise — they log and return the "nothing found" sentinel.

### monkeypatch.setattr on module attribute
**Source:** `firestarter_app/tests/test_update_version.py` line 243
**Apply to:** all test classes in `test_firmware_install.py`

```python
monkeypatch.setattr(firmware.requests, "get", lambda *a, **kw: mock_response)
```

Not `unittest.mock.patch("firestarter.firmware.requests.get", ...)` — use `monkeypatch.setattr` on the already-imported module object, matching the established test style.

### autouse env-cleanup fixture
**Source:** `firestarter_app/tests/test_update_version.py` lines 47–56 and `firestarter_app/tests/test_fwguard.py` lines 34–42
**Apply to:** every test class in `test_firmware_install.py`

Pattern: `@pytest.fixture(autouse=True)` named `_isolate_env`, uses `monkeypatch.delenv(..., raising=False)` to clear any relevant env vars, so tests don't bleed state across runs.

---

## No Analog Found

Files or capabilities in this phase with no close existing analog:

| Capability | Role | Data Flow | Reason |
|---|---|---|---|
| `FirmwareManager.list_releases` | service | request-response | No existing enumeration method in the project; `fetch_latest_release_info` is closest but returns a single release. Build from `fetch_latest_release_info`'s asset-resolution loop + new pagination helper. |
| `FirmwareManager._fetch_all_releases` pagination | service | request-response | No pagination exists anywhere in `firestarter_app/`. Use RESEARCH.md Pattern 6 (link-header follow, 5-page cap). |
| Magic-default detection in dispatch | controller | request-response | No `packaging.version.Version` usage in the current codebase. Use RESEARCH.md Pattern 5 (D-22 exact code shape). |
| PEP 440-aware version comparison | utility | — | Current `_compare_versions` uses `tuple(map(int, ...))` — the replacement uses `packaging.version.Version`. No existing PEP 440 comparison in project. Use RESEARCH.md Pattern 4. |
| Two-mutex-group argparse composition | config | — | No existing subparser in `main.py` uses `add_mutually_exclusive_group`. Use RESEARCH.md Pattern 1 + Finding 3 (VERIFIED via shell). Critical constraint: `-i/--install` must be added to `install_group`, not `fw_parser`, from inception. |
| `ReleaseInfo` TypedDict | model | — | No TypedDicts in current codebase. Python 3.9+ compatible (project constraint from `pyproject.toml` line 14: `requires-python = ">=3.9"`). Define inline in `firmware.py`. |

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tests/`
**Files read:** `firmware.py` (408 lines), `constants.py` (62 lines), `main.py` (lines 192–228 + 645–657), `pyproject.toml` (82 lines), `tests/test_update_version.py` (380 lines), `tests/test_fwguard.py` (126 lines)
**Pattern extraction date:** 2026-05-20

### Key planner notes

1. **`-i/--install` must move to `install_group`** — this is the single most dangerous structural change in `create_firmware_args`. If it stays on `fw_parser` directly, the `--list`/`--install` mutex cannot be enforced by argparse (RESEARCH.md Pitfall 2, VERIFIED).

2. **`create_firmware_args` must return `fw_parser`** — needed so the dispatch block can call `fw_parser.error("--json requires --list")`. Currently the function returns nothing (line 228 has no return statement).

3. **`Version("2.0.7_dev").is_prerelease == True`** — RESEARCH.md corrects CONTEXT.md specifics block. The dev-suffix strings normalize silently to `.dev0` pre-releases. The magic-default (D-21) WILL fire on the current `"2.0.7_dev"` install. The `except InvalidVersion` block is still recommended for forward-compatibility but won't fire on current strings.

4. **Draft filter in `_fetch_all_releases`** — paginated `/releases` includes `draft: True` releases. Always filter `and not release.get("draft", False)` before treating a release as a candidate (RESEARCH.md Pitfall 6).

5. **`fw_parser` scope for `--json` validation** — `fw_parser.error(msg)` is the cleanest pattern. Requires `fw_parser = create_firmware_args(subparsers)` at the call site where the subparser is registered.

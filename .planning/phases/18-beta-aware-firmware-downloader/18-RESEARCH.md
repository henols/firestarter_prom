# Phase 18: Beta-Aware Firmware Downloader — Research

**Researched:** 2026-05-20
**Domain:** GitHub REST API (releases), `packaging.version.Version`, argparse mutex groups, `requests.get` mocking, Python CLI dispatch refactor
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Extend existing `fw` subparser (NOT a new top-level command). Match existing `-i/--install`, `-b/--board`, `-f/--force` shape.
- **D-02:** New flags: `--pre` (no short form), `--firmware-version VERSION`, `--list` (boolean, read-only), `--json` (boolean modifier for `--list`).
- **D-03:** Pre-release selection: paginate `/releases`, filter `prerelease: True`, parse `tag_name` via `packaging.version.Version`, sort descending, take highest, resolve asset `firestarter_{board}.hex`.
- **D-04:** Paginate via `Link: rel=next`; cap at 5 pages (150 releases). Log INFO when cap hit.
- **D-05:** `--pre` silent fallback to stable when no prerelease exists (mirrors `pip install --pre` semantics).
- **D-06:** Beta-installed app ALWAYS gets some firmware: beta if available, stable otherwise.
- **D-07:** Validate `--firmware-version` against `FIRMWARE_VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+((b|rc)[0-9]+)?$')` BEFORE network call. Invalid input → `argparse.ArgumentTypeError`.
- **D-08:** `FIRMWARE_VERSION_RE` is consumer-side superset of Phase 15's `BETA_VERSION_RE` (publisher-side). Different surfaces, different regexes. `FIRMWARE_VERSION_RE` accepts stable (`3.1.0`) AND pre-release (`3.1.0b2`, `3.1.0rc1`). `BETA_VERSION_RE` accepts pre-release only.
- **D-09:** On valid `--firmware-version`, fetch `/releases/tags/{tag}` directly. 404 or missing board asset → fatal error with clear message.
- **D-10:** Default `--list` output: plain-text table with columns Version, Channel, Published, Asset URL.
- **D-11:** Sort by PEP 440 Version descending. Omit releases without board-matching asset.
- **D-12:** `--list --json` emits JSON array with keys `version`, `channel`, `published`, `asset_url`, `tag`.
- **D-13:** `--list --pre` / `--stable` / `--all` channel filter; mutually exclusive within `--list`.
- **D-14:** Add `packaging>=21.0` to `firestarter_app/pyproject.toml` `[project.dependencies]`.
- **D-15:** Keep `fetch_latest_release_info(board)` as-is; add docstring "Stable-only path; use `fetch_release_info` for general channel selection."
- **D-16:** Add `fetch_release_info(channel, version, board)` router returning `(version, url)` or `(None, None)`.
- **D-17:** Add `list_releases(channel_filter, board)` returning list of release dicts/dataclasses.
- **D-18:** `manage_firmware_update` grows `channel: Literal['stable','pre','pinned'] = 'stable'` and `pinned_version: Optional[str] = None`.
- **D-19:** `--pre` and `--firmware-version` are mutex (`add_mutually_exclusive_group`).
- **D-20:** `--list` and `-i/--install` are mutex (`add_mutually_exclusive_group`).
- **D-21:** When `packaging.version.Version(firestarter.__version__).is_prerelease` is True, bare `firestarter fw -i` auto-routes to `--pre`. Stable-installed apps: no change.
- **D-22:** Magic-default detection in `main.py` at dispatch time, before `manage_firmware_update`. Exact code shape specified in CONTEXT.md.
- **D-23:** `Version("2.0.7").is_prerelease` is False — INST-01 non-regression preserved.
- **D-24:** Beta-app opt-out for stable firmware: use `--firmware-version X.Y.Z` (explicit stable pin). No `--no-pre` flag.
- **D-25:** Magic default ALWAYS logs INFO: "Beta app detected — defaulting to --pre. Use --firmware-version X.Y.Z to pin a stable version."
- **D-26:** No caching for v1.4. Each invocation hits GitHub fresh.
- **D-27:** (Discretion) `ReleaseInfo` data shape — TypedDict vs dataclass vs plain dict.
- **D-28:** (Discretion) Whether `list_releases` paginates internally or returns an iterator.
- **D-29:** (Discretion) No `--no-pre` flag (D-24 is the documented opt-out).
- **D-30:** (Discretion) Exact wording of magic-default INFO log. Must say "beta app detected" and "use --firmware-version X.Y.Z to pin stable".

### Claude's Discretion

D-27 through D-30 (see above).

### Deferred Ideas (OUT OF SCOPE)

- Caching the release listing for repeated `--list` invocations.
- `--no-pre` flag.
- Per-board fallback (e.g., Uno has beta, Leonardo doesn't).
- `default_firmware_channel` config option.
- Signed-artifact verification.
- Promotion path from beta to stable on the consumer side.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INST-01 | `firestarter --install` with no new flags fetches stable `/releases/latest` unchanged; `_compare_versions` refactored to PEP 440 via `packaging.version.Version`. | §GitHub API — `/releases/latest` endpoint verified; §`packaging.version.Version` API; §`_compare_versions` caller audit |
| INST-02 | `firestarter --install --pre` fetches newest pre-release firmware; silent fallback to stable when none exist. | §GitHub API — paginated `/releases` verified; §Pre-release selection algorithm; §Fallback behavior |
| INST-03 | `firestarter --install --firmware-version X.Y.Z[bN\|rcN]` fetches exact tag; input validation; mutex with `--pre`. | §GitHub API — `/releases/tags/{tag}` verified; §`FIRMWARE_VERSION_RE` validation; §argparse mutex pattern |
| INST-04 | `firestarter firmware list [--all\|--pre\|--stable]` enumerates releases; greppable output; `--json` modifier. | §`list_releases` implementation pattern; §argparse mutex for channel filter; §Table/JSON format |
</phase_requirements>

---

## Summary

Phase 18 extends `FirmwareManager` in `firestarter_app/firestarter/firmware.py` with two new methods (`fetch_release_info` and `list_releases`), refactors `_compare_versions` to use `packaging.version.Version`, and extends the `fw` argparse subparser with four new flags and two mutex groups. All code lands inside `firestarter_app/` (submodule). The meta-repo tracks only planning artifacts.

The most important technical finding is about the dev-suffix version strings. CONTEXT.md says `Version("2.0.7_dev")` will raise `InvalidVersion` — this is **incorrect**. Verified against packaging 26.2: `Version("2.0.7_dev")` and `Version("3.0.0-dev")` both **normalize silently** to `2.0.7.dev0` and `3.0.0.dev0` respectively, with `is_prerelease == True`. No exception is raised. The current app install string `"2.0.7_dev"` will therefore evaluate as a prerelease, which means the magic default (D-21/D-22) will fire on the current dev install. This is semantically correct — a `_dev` suffixed install IS a non-stable install. The `try/except InvalidVersion` defensive wrap in D-22 is still recommended for forward-compatibility with truly invalid version strings, but the current specific strings do not trigger it.

The second important finding is the GitHub API shape. The live `/repos/henols/firestarter/releases` endpoint returns 77 releases total (as of 2026-05-20). At per_page=30, 3 pages are needed — well within the D-04 cap of 5 pages. The `prerelease` and `draft` fields are present in every response. Asset naming `firestarter_{board}.hex` is confirmed. The `/releases/tags/{tag}` endpoint returns 404 as an HTTP status with `{"message": "Not Found"}` in the body — `requests.raise_for_status()` on the `requests.get(url)` response will raise `HTTPError` for this, which is the correct detection path.

**Primary recommendation:** Implement in three waves — Wave 0: scaffold tests (RED); Wave 1: `_compare_versions` refactor + argparse flags + magic default (turns INST-01 tests GREEN); Wave 2: `fetch_release_info` + `list_releases` (turns INST-02/03/04 tests GREEN). The refactor is well-localized: `_compare_versions` and `fetch_latest_release_info` are each called from exactly one site in `manage_firmware_update`.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| CLI flag parsing + mutex enforcement | `main.py` (argparse) | — | All argparse lives in `create_firmware_args`; mutex groups attach to `fw_parser` |
| Magic-default beta detection | `main.py` (dispatch) | — | D-22 places detection at dispatch site before calling `manage_firmware_update` |
| GitHub API calls (list, by-tag, latest) | `firmware.py` (FirmwareManager) | — | All HTTP in `FirmwareManager`; `main.py` never calls `requests` directly |
| Version comparison (installed vs latest) | `firmware.py` (_compare_versions) | — | Localized; single call site at line 335 |
| Pre-release candidate selection | `firmware.py` (fetch_release_info) | — | Pagination + filter + sort inside `FirmwareManager` |
| Release enumeration for `--list` | `firmware.py` (list_releases) | — | Returns structured data; `main.py` formats it for display |
| Table / JSON formatting for `--list` | `main.py` (dispatch) | — | Formatting is a CLI concern, not a firmware concern |
| Input validation for `--firmware-version` | `main.py` (argparse type=) | — | `argparse.ArgumentTypeError` prevents network call on bad input (D-07) |
| Dependency declaration | `pyproject.toml` | — | `packaging>=21.0` added to `[project.dependencies]` |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `packaging` | >=21.0 (26.2 in environment) | `Version` comparison, `is_prerelease` | PEP 440 canonical library; already transitive dep via pip/setuptools |
| `requests` | >=2.20 (already in pyproject.toml) | GitHub API HTTP calls | Already used in `fetch_latest_release_info`; no new dep |
| `argparse` | stdlib | CLI flag parsing, mutex groups | Already used throughout `main.py` |

**Version verification:** `packaging` version 26.2 confirmed in environment via `python3 -c "import packaging; print(packaging.__version__)"`. [VERIFIED: shell]

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `typing.TypedDict` | stdlib (Python 3.8+) | `ReleaseInfo` data shape | If D-27 discretion picks TypedDict; available in Python 3.9+ |
| `typing.Literal` | stdlib (Python 3.8+) | `channel` parameter type annotation | Already used in typing imports |
| `typing.Optional` | stdlib | Optional type hints | Already imported in `firmware.py` |
| `re` | stdlib | `FIRMWARE_VERSION_RE` compilation | Already used in project |

### Installation (pyproject.toml change only)

```toml
# Add to [project.dependencies] in firestarter_app/pyproject.toml:
"packaging>=21.0",
```

No `pip install` needed — `packaging` is already present as a transitive dependency. The `pyproject.toml` change promotes it to an explicit dependency.

---

## Architecture Patterns

### System Architecture Diagram

```
firestarter fw -i --pre
        │
        ▼
main.py create_firmware_args()
  ├── mutex_group_1: [--pre] XOR [--firmware-version]
  └── mutex_group_2: [--list] XOR [-i/--install]
        │
        ▼
main.py dispatch (args.command == "fw")
  ├── --json without --list? → p.error()  [post-parse validation]
  ├── args.list? → firmware_manager.list_releases() → print table/JSON → return
  └── args.install?
        ├── magic-default check: if not args.pre and not args.firmware_version:
        │     import firestarter as _pkg; Version(_pkg.__version__).is_prerelease?
        │     → True: args.pre = True; logger.info("Beta app detected...")
        ├── firmware_manager.manage_firmware_update(
        │       channel='pre'|'stable'|'pinned',
        │       pinned_version=args.firmware_version)
        └── return
              │
              ▼
firmware.py manage_firmware_update(channel, pinned_version)
  ├── check_current_firmware()
  └── fetch_release_info(channel, version, board)
        ├── channel='stable' → fetch_latest_release_info() [unchanged shim]
        ├── channel='pinned' → GET /releases/tags/{version}
        │     → 404 HTTPError → fatal "Tag X not found"
        │     → 200 + asset missing → fatal "Release X has no asset for {board}"
        └── channel='pre'  → paginate GET /releases (up to 5 pages)
              ├── filter prerelease=True
              ├── parse tag_name via Version(); discard parse-failures (WARN)
              ├── sort descending; take highest
              ├── resolve firestarter_{board}.hex asset
              └── zero prereleases → fallback to 'stable' path (D-05)
```

### Recommended Project Structure (changes only)

```
firestarter_app/
├── firestarter/
│   ├── constants.py            # add FIRESTARTER_RELEASES_URL, FIRESTARTER_RELEASE_BY_TAG_URL
│   ├── firmware.py             # FirmwareManager: new methods + refactored _compare_versions
│   └── main.py                 # create_firmware_args() + dispatch extensions
├── tests/
│   └── test_firmware_install.py  # NEW: INST-01..04 + comparator + magic-default coverage
└── pyproject.toml              # add packaging>=21.0
```

### Pattern 1: Two Independent Mutex Groups in One Subparser

```python
# Source: VERIFIED via shell (argparse stdlib)
def create_firmware_args(parser):
    fw_parser = parser.add_parser("fw", help="Firmware version.")

    # Existing flags (unchanged)
    fw_parser.add_argument("-i", "--install", action="store_true", ...)
    fw_parser.add_argument("-b", "--board", ...)
    fw_parser.add_argument("--avrdude-path", ...)
    fw_parser.add_argument("-c", "--avrdude-config-path", ...)
    fw_parser.add_argument("-f", "--force", action="store_true", ...)

    # Mutex group 1: --pre XOR --firmware-version
    channel_group = fw_parser.add_mutually_exclusive_group()
    channel_group.add_argument("--pre", action="store_true",
        help="Fetch latest pre-release firmware.")
    channel_group.add_argument("--firmware-version", type=_validate_firmware_version,
        metavar="VERSION",
        help="Pin exact firmware version (e.g. 3.1.0, 3.1.0b2, 3.1.0rc1).")

    # Mutex group 2: --list XOR --install (--install is already added above)
    # Note: --install is already added to fw_parser directly, so --list must be
    # added to a mutex group that ALSO references the already-added --install.
    # argparse does NOT support adding an already-added argument to a mutex group.
    # SOLUTION: Add BOTH --list and --install to the mutex group (not fw_parser directly).
    # See Anti-Patterns section below.

    fw_parser.add_argument("--list", action="store_true",
        help="List available firmware releases.")
    fw_parser.add_argument("--json", action="store_true",
        help="Output --list results as JSON.")
```

**Critical implementation note:** `argparse.add_mutually_exclusive_group()` requires that all flags in the group be added TO the group object, not to the parser directly. If `-i/--install` is added to `fw_parser` before the mutex group is created, it cannot be retroactively moved to the group. The implementation must add `-i/--install` to the mutex group itself:

```python
# Source: VERIFIED via shell
fw_parser = parser.add_parser("fw", help="Firmware version.")

# Mutex group 2: --list XOR -i/--install
install_group = fw_parser.add_mutually_exclusive_group()
install_group.add_argument("-i", "--install", action="store_true",
    help="Try to install firmware.")
install_group.add_argument("--list", action="store_true",
    help="List available firmware releases.")

# Mutex group 1: --pre XOR --firmware-version
channel_group = fw_parser.add_mutually_exclusive_group()
channel_group.add_argument("--pre", action="store_true", ...)
channel_group.add_argument("--firmware-version", type=_validate_firmware_version, ...)

# Non-mutex flags
fw_parser.add_argument("-b", "--board", ...)
fw_parser.add_argument("--avrdude-path", ...)
fw_parser.add_argument("-c", "--avrdude-config-path", ...)
fw_parser.add_argument("-f", "--force", action="store_true", ...)
fw_parser.add_argument("--json", action="store_true", ...)
```

### Pattern 2: `--firmware-version` Input Validation via `type=`

```python
# Source: VERIFIED via shell
import re
import argparse

FIRMWARE_VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+((b|rc)[0-9]+)?$')

def _validate_firmware_version(value: str) -> str:
    """Argparse type= validator for --firmware-version. Rejects before network call."""
    if not FIRMWARE_VERSION_RE.match(value):
        raise argparse.ArgumentTypeError(
            f"Invalid firmware version {value!r}. "
            "Expected X.Y.Z, X.Y.ZbN, or X.Y.ZrcN (e.g. 3.1.0, 3.1.0b2, 3.1.0rc1)."
        )
    return value
```

This constant belongs in `firmware.py` (or `constants.py`) — the planner chooses. Both `firmware.py` and `main.py` need it; if in `constants.py`, import via `from firestarter.constants import *`.

### Pattern 3: `--json` Requires `--list` Post-Parse Validation

```python
# Source: VERIFIED via shell
# In main.py dispatch block:
elif args.command == "fw":
    if args.json and not args.list:
        fw_parser.error("--json requires --list")  # fw_parser must be in scope
    # OR: use a top-level parser reference
    if args.json and not args.list:
        parser.error("--json requires --list")
```

`p.error()` prints usage + message then exits with code 2 — same UX as argparse native errors.

### Pattern 4: `packaging.version.Version` for Comparator Refactor

```python
# Source: VERIFIED via shell (packaging 26.2)
from packaging.version import Version, InvalidVersion

def _compare_versions(self, current_version_str, latest_version_str) -> bool:
    """Returns True if current >= latest. PEP 440-safe via packaging.version.Version."""
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

### Pattern 5: Magic-Default Detection in Dispatch

```python
# Source: CONTEXT.md D-22 (exact shape); import safety VERIFIED via shell
elif args.command == "fw":
    if args.install and not args.pre and not args.firmware_version:
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
```

**Note on `InvalidVersion` path:** As of packaging 26.2, `Version("2.0.7_dev")` and `Version("3.0.0-dev")` do NOT raise `InvalidVersion` — they normalize to `2.0.7.dev0` / `3.0.0.dev0` with `is_prerelease == True`. The `except InvalidVersion` path only fires for truly malformed strings like `"not-a-version"` or `"abc"`. The defensive wrap is still recommended for forward-compatibility.

### Pattern 6: GitHub `/releases` Pagination

```python
# Source: VERIFIED via direct GitHub API call (curl -sI)
import re as _re

_LINK_NEXT_RE = _re.compile(r'<([^>]+)>;\s*rel="next"')

def _fetch_all_releases(self, max_pages: int = 5) -> list:
    """Paginate /releases up to max_pages. Returns flat list of release dicts."""
    url = FIRESTARTER_RELEASES_URL
    releases = []
    pages_fetched = 0
    while url and pages_fetched < max_pages:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        releases.extend(response.json())
        pages_fetched += 1
        link_header = response.headers.get("Link", "")
        m = _LINK_NEXT_RE.search(link_header)
        url = m.group(1) if m else None
    if url and pages_fetched >= max_pages:
        logger.info(
            f"Pagination cap hit ({max_pages} pages / "
            f"{max_pages * 30} releases). Some older releases not shown."
        )
    return releases
```

### Pattern 7: `requests.get` Mock for Tests

```python
# Source: VERIFIED via shell (unittest.mock)
# Mirror of Phase 15's monkeypatch.setattr(update_version.subprocess, "run", fake_run)
from unittest.mock import MagicMock

def make_releases_response(releases, next_url=None):
    mock = MagicMock()
    mock.json.return_value = releases
    mock.raise_for_status.return_value = None
    mock.headers = {"Link": f'<{next_url}>; rel="next"'} if next_url else {}
    mock.iter_content.return_value = iter([b"fake hex data"])
    return mock

# In test class:
def test_pre_release_selection(self, monkeypatch):
    page1 = make_releases_response([
        {
            "tag_name": "3.1.0b2", "prerelease": True,
            "published_at": "2026-05-20T10:00:00Z",
            "assets": [{"name": "firestarter_uno.hex",
                         "browser_download_url": "https://example.com/uno.hex"}],
        },
        {
            "tag_name": "3.0.0", "prerelease": False,
            "published_at": "2026-05-01T10:00:00Z",
            "assets": [{"name": "firestarter_uno.hex",
                         "browser_download_url": "https://example.com/stable_uno.hex"}],
        },
    ])
    monkeypatch.setattr(firmware.requests, "get", lambda *a, **kw: page1)
    fm = FirmwareManager(config_manager=MagicMock())
    version, url = fm.fetch_release_info(channel="pre", board="uno")
    assert version == "3.1.0b2"
    assert "uno.hex" in url
```

### Anti-Patterns to Avoid

- **Adding `-i/--install` to `fw_parser` directly, then trying to add `--list` to a mutex group with it:** argparse does not support retroactively adding an existing argument to a mutex group. Flags in a mutex group must be added to the group object from the start.
- **`import packaging` at the top:** `packaging` exports `version` as a submodule attribute, but the canonical form is `from packaging.version import Version, InvalidVersion`. [VERIFIED: shell]
- **String-sorting pre-release versions:** `sorted(["3.1.0b9", "3.1.0b10"], reverse=True)` → `["3.1.0b9", "3.1.0b10"]` (WRONG: `b10 < b9` by string). `sorted([Version("3.1.0b9"), Version("3.1.0b10")], reverse=True)` → `[3.1.0b10, 3.1.0b9]` (CORRECT). [VERIFIED: shell]
- **Using `tuple(map(int, v.split(".")))` for version compare:** This is the current `_compare_versions` implementation. It crashes with `ValueError: invalid literal for int()` on any pre-release string like `"3.1.0b2"` (the `int("0b2")` call fails). Phase 18 replaces this completely.
- **Checking `response.json()["message"] == "Not Found"` for 404 detection:** Use `response.raise_for_status()` instead; it raises `requests.exceptions.HTTPError` for 4xx/5xx responses, with `err.response.status_code == 404` for by-tag 404.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PEP 440 version ordering | Custom pre-release sort | `packaging.version.Version` | String sort gives wrong order for b10 vs b9; alpha vs beta vs rc ordering is subtle |
| Version string validation | Custom regex + bool | `packaging.version.Version` + `InvalidVersion` | PEP 440 normalization is non-obvious (underscores, hyphens are legal separators) |
| Link header pagination parsing | Custom header parser | Simple `re.search(r'<([^>]+)>; rel="next"', header)` | One-liner regex is sufficient; GitHub's format is consistent |
| Pre-release detection | `"b" in version_string` | `Version(s).is_prerelease` | Dev releases (`.dev0`) are also prerelease; alpha is also prerelease; the property handles all cases |

**Key insight:** The `packaging` library eliminates all version-handling edge cases that make the current `_compare_versions` brittle. The refactor replaces 8 lines of fragile int-parsing with 2 lines using `packaging.version.Version`.

---

## Key Technical Findings

### 1. GitHub `/releases` API — Live-Verified Shape [VERIFIED: direct curl call]

**Endpoint:** `GET https://api.github.com/repos/henols/firestarter/releases`

Response: JSON array. Each element has:
- `tag_name` (string): firmware version tag, e.g. `"2.0.6"` or `"3.1.0b2"` for future pre-releases
- `prerelease` (bool): `true` for pre-release, `false` for stable
- `draft` (bool): `false` for published releases (filter out `draft: true` in implementation)
- `published_at` (string): ISO-8601 timestamp, e.g. `"2025-11-16T13:50:02Z"`
- `assets` (array): each asset has `name` (string) and `browser_download_url` (string)
- Additional fields present but irrelevant: `url`, `assets_url`, `upload_url`, `html_url`, `id`, `author`, `node_id`, `target_commitish`, `name`, `immutable`, `created_at`, `updated_at`, `tarball_url`, `zipball_url`, `body`

**Pagination:** `Link` header with `rel="next"` format: `<https://api.github.com/repositories/810276812/releases?per_page=2&page=2>; rel="next"`. Note: GitHub may use repository ID URLs in pagination links, not the named path. The pagination-follow logic must use the URL from the Link header verbatim.

**Current state of repo:** 77 releases total. At default per_page=30, 3 pages needed. D-04's 5-page cap covers 150 releases — adequate with growth margin.

**Rate limit:** 60 requests/hour for unauthenticated requests per IP. `--list` followed by `fw -i --pre` consumes approximately 3–6 requests (up to 3 list pages + 1 asset download request). Worst case with `--list` on a full pagination run: 5 list pages + 1 by-tag = 6 requests. Rate limit is not a concern for normal use patterns.

**Rate limit 403 detection:** `requests.raise_for_status()` raises `HTTPError`. Check `err.response.status_code == 403` and `err.response.headers.get("X-RateLimit-Remaining") == "0"` to distinguish rate-limit from auth error. Log a clear message without retry (D-26 no caching, no retry for v1.4).

**Asset naming convention:** `firestarter_{board}.hex` (e.g., `firestarter_uno.hex`, `firestarter_leonardo.hex`). Confirmed present in current stable releases. [VERIFIED: direct curl call]

**Endpoint:** `GET https://api.github.com/repos/henols/firestarter/releases/latest`

Returns a single release object (same shape as above). Always returns the most recent non-pre-release, non-draft release. This is used by the existing `fetch_latest_release_info` — unchanged.

**Endpoint:** `GET https://api.github.com/repos/henols/firestarter/releases/tags/{tag}`

Returns a single release object for the exact tag. Returns HTTP 404 with `{"message": "Not Found", "documentation_url": "...", "status": "404"}` when the tag does not exist. [VERIFIED: direct curl call against `99.99.99b1`]

### 2. `packaging.version.Version` API [VERIFIED: shell, packaging 26.2]

**Correct import:** `from packaging.version import Version, InvalidVersion`

**Key behaviors:**

| Input string | Behavior | `is_prerelease` |
|---|---|---|
| `"2.0.7_dev"` | Normalizes to `2.0.7.dev0` — NO exception | `True` |
| `"3.0.0-dev"` | Normalizes to `3.0.0.dev0` — NO exception | `True` |
| `"2.0.7.dev0"` | Parses cleanly | `True` |
| `"2.0.7"` | Parses cleanly | `False` |
| `"3.1.0b1"` | Parses cleanly | `True` |
| `"3.1.0rc1"` | Parses cleanly | `True` |
| `"3.1.0b10"` | Parses cleanly | `True` |
| `"1.0.0a1"` | Parses cleanly (alpha) | `True` |
| `"1.0.0.dev1"` | Parses cleanly | `True` |
| `"not-a-version"` | Raises `InvalidVersion` | — |
| `"abc"` | Raises `InvalidVersion` | — |

**CRITICAL CORRECTION to CONTEXT.md specifics block:** The note "packaging.version.Version('2.0.7_dev') will RAISE InvalidVersion" is factually incorrect for packaging >= 21.0. Both `"2.0.7_dev"` and `"3.0.0-dev"` normalize to `dev0` pre-releases. They are recognized as PEP 440 dev releases (underscores and hyphens are accepted separators per PEP 440's normalization rules). The magic-default D-22 will fire on the current `"2.0.7_dev"` install — this is semantically correct and desired behavior (a dev-install should opt into pre-release firmware). The `except InvalidVersion` block in D-22 is still worth including but will only activate for truly garbage version strings.

**Ordering correctness (VERIFIED: shell):**

```
Sorted descending by packaging.version.Version:
['3.1.0', '3.1.0rc1', '3.1.0b10', '3.1.0b9', '3.1.0b1', '3.0.0']

String sort (WRONG):
['3.1.0rc1', '3.1.0b9', '3.1.0b10', '3.1.0b1', '3.1.0', '3.0.0']
```

`b10 > b9` only via `Version` sort, not string sort.

**PEP 440 ordering rules (canonical):** `devN < aN < bN < rcN < stable < postN`. For Phase 18's pre-release selection, filter to `prerelease: True` from GitHub API, then sort by `Version` — this correctly puts `3.1.0rc1` above `3.1.0b10` above `3.1.0b9`.

### 3. argparse Mutex Groups [VERIFIED: shell]

Two independent `add_mutually_exclusive_group()` calls on the same parser create two INDEPENDENT groups. Valid combinations: `--pre --install`, `--firmware-version 3.1.0b1 --list`, `--list`. Invalid (rejected by argparse): `--pre --firmware-version 3.1.0` (group 1 conflict), `--list --install` (group 2 conflict).

**Constraint on `-i/--install`:** The existing `create_firmware_args` adds `-i/--install` to `fw_parser` directly. To include it in a mutex group with `--list`, it must be added to the mutex group object instead. This means `create_firmware_args` must be restructured so `-i/--install` is added to `install_group.add_argument(...)` rather than `fw_parser.add_argument(...)`. This is a clean-cut change — no user-visible behavior change.

### 4. `--json` Requires `--list`: Post-Parse Validation Pattern [VERIFIED: shell]

argparse does not natively support "flag X requires flag Y." Best practice for Phase 18: post-parse check in the `args.command == "fw"` dispatch block:

```python
if args.json and not args.list:
    fw_parser.error("--json requires --list")
```

`parser.error(msg)` prints `usage: ...` + `error: msg` to stderr and exits with code 2 (same as argparse native errors). Requires `fw_parser` to be accessible in the dispatch scope — return it from `create_firmware_args` or store as a closure.

**Alternative:** Add `--json` to a subgroup of `--list`. But argparse subgroups are complex; post-parse validation is simpler and standard.

### 5. Caller Audit [VERIFIED: grep on firestarter_app/]

`_compare_versions` callers: **exactly one** — `firmware.py:335` inside `manage_firmware_update`. No external callers, no test callers. [VERIFIED: grep]

`fetch_latest_release_info` callers: **exactly one** — `firmware.py:322` inside `manage_firmware_update`. No callers in `main.py`, no test callers. [VERIFIED: grep]

`manage_firmware_update` callers: **exactly one** — `main.py:648` in the `args.command == "fw"` dispatch branch. [VERIFIED: grep]

The refactor surface is fully localized. D-15's "preserve as back-compat shim" is conservative but correct — the shim costs nothing (it's a 30-line method) and preserves stable-path semantics byte-identically (INST-01).

### 6. `firestarter.__version__` Import Safety [VERIFIED: shell]

`import firestarter as _pkg` at dispatch time in `main.py` is safe — no circular import. `firestarter/__init__.py` contains only `__version__ = "2.0.7_dev"` (one line). The import succeeds and `_pkg.__version__` returns the version string. `Version("2.0.7_dev")` normalizes to `2.0.7.dev0`, `.is_prerelease == True`.

The defensive `try/except ImportError` around the import in D-22 is recommended practice but the import will not fail in the current package structure.

### 7. `is_prerelease` Covers More Than `b/rc` [VERIFIED: shell]

`Version.is_prerelease` returns `True` for: `.devN`, `.aN` (alpha), `.bN` (beta), `.rcN` (release candidate). This is CORRECT for D-21's purpose — any non-stable version of the app should default to pre-release firmware. Dev builds (`2.0.7_dev`), alpha builds, beta builds all trigger the magic default. Stable builds (`2.0.7`) return `False`. The CONTEXT.md says "actually CORRECT" — this research confirms it.

---

## Common Pitfalls

### Pitfall 1: `int("0b1")` ValueError in Existing `_compare_versions`

**What goes wrong:** `_compare_versions("3.0.0", "3.1.0b2")` calls `tuple(map(int, "3.1.0b2".split(".")))` → `int("0b2")` raises `ValueError`. Today this is protected by GitHub's `/releases/latest` always returning a non-pre-release version. Phase 18's new code paths (`--pre`, `--firmware-version`) bypass that protection and will encounter pre-release version strings.

**Why it happens:** Existing implementation splits on `.` and casts each part to `int`. Pre-release suffixes like `b2`, `rc1` embed non-integer characters.

**How to avoid:** Replace with `packaging.version.Version` (D-14, INST-01). This is Wave 1 work.

**Warning signs:** Any test that passes a pre-release version string to `_compare_versions` will fail with `ValueError` until the refactor lands.

### Pitfall 2: `-i/--install` Added to Parser, Not Mutex Group

**What goes wrong:** If `create_firmware_args` adds `-i/--install` to `fw_parser` directly (current code), then creating a mutex group for `(--list, --install)` will raise `argparse.ArgumentError: argument --list: conflicting option string(s): --install` or silently not enforce the mutex.

**Why it happens:** argparse does not support retroactively moving a flag from a parser to a mutex group. The flag must be added to the group object from inception.

**How to avoid:** In the refactored `create_firmware_args`, add `-i/--install` to `install_group` (not `fw_parser`) before the `--list` flag is added.

**Warning signs:** No argparse error at startup, but `--list --install` is accepted without rejection.

### Pitfall 3: `per_page` in Pagination URLs from Link Header

**What goes wrong:** The Link header URL may use repository ID notation (`/repositories/810276812/releases?...`) instead of the named path. Following the URL verbatim (as recommended) handles this automatically. Reconstructing the URL from the original path + page parameter breaks.

**Why it happens:** GitHub's API transparently redirects named paths to repository-ID paths in pagination links.

**How to avoid:** Always follow the URL from the Link header verbatim, never reconstruct it. [VERIFIED: direct curl observation]

### Pitfall 4: `--json` Without `--list` Silently Ignored

**What goes wrong:** If the post-parse validation for `--json requires --list` is omitted, a user running `firestarter fw -i --json` gets `--json` silently ignored (it doesn't affect install behavior). This is confusing UX.

**Why it happens:** `--json` is a flag that attaches to `fw_parser`; argparse won't reject it unless explicitly validated.

**How to avoid:** Add `if args.json and not args.list: fw_parser.error(...)` as the first check in the `args.command == "fw"` dispatch block.

### Pitfall 5: `fw_parser` Not Accessible in Dispatch Scope

**What goes wrong:** `fw_parser.error(msg)` needs `fw_parser` in scope in the dispatch function. `create_firmware_args` currently returns nothing.

**Why it happens:** The function creates `fw_parser` as a local variable and returns implicitly.

**How to avoid:** Change `create_firmware_args` to return `fw_parser`. In `main.py`, capture: `fw_parser = create_firmware_args(subparsers)`. Then use `fw_parser.error(...)` in dispatch.

### Pitfall 6: Draft Releases in Paginated Results

**What goes wrong:** Paginated `/releases` includes draft releases (`draft: True`). Draft releases have no `published_at` and often have no assets. Treating them as candidates causes `KeyError` or `None` asset URL.

**Why it happens:** `/releases/latest` filters out drafts automatically; the list endpoint does not.

**How to avoid:** Filter out `draft: True` releases in both `fetch_release_info(channel='pre')` and `list_releases()`. Add `and not release.get("draft", False)` to the prerelease filter.

---

## Code Examples

### `FIRMWARE_VERSION_RE` — Module-Level Constant

```python
# Source: CONTEXT.md D-07; behavior VERIFIED via shell
import re
FIRMWARE_VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+((b|rc)[0-9]+)?$')

# Accepts: '3.1.0', '3.1.0b2', '3.1.0rc1', '3.0.0', '0.0.1b1'
# Rejects: '3.1.0-dev', '3.1.0.4.5', 'latest', '3.1.0beta2', '3.1'
```

Place in `firmware.py` at module level (alongside the `FirmwareManager` class). Reference from `main.py` via the existing `from firestarter.constants import *` or via `from firestarter.firmware import FIRMWARE_VERSION_RE`.

### New URL Constants for `constants.py`

```python
# Source: CONTEXT.md code_context; VERIFIED via direct API call
FIRESTARTER_RELEASE_URL = (
    "https://api.github.com/repos/henols/firestarter/releases/latest"
)
FIRESTARTER_RELEASES_URL = (
    "https://api.github.com/repos/henols/firestarter/releases"
)
FIRESTARTER_RELEASE_BY_TAG_URL = (
    "https://api.github.com/repos/henols/firestarter/releases/tags/{tag}"
)
```

### `fetch_release_info` Signature (D-16)

```python
# Source: CONTEXT.md D-16
from typing import Literal, Optional, Tuple

def fetch_release_info(
    self,
    channel: Literal['stable', 'pre', 'pinned'] = 'stable',
    version: Optional[str] = None,  # required when channel='pinned'
    board: str = 'uno',
) -> Tuple[Optional[str], Optional[str]]:
    """Returns (resolved_version, download_url) or (None, None) on failure.
    channel='stable' → /releases/latest (same as fetch_latest_release_info).
    channel='pre'    → enumerate /releases, filter prerelease=True, sort by PEP 440, take highest;
                       fall back to 'stable' if empty (D-05).
    channel='pinned' → /releases/tags/{version} direct lookup.
    """
```

### `list_releases` Signature (D-17)

```python
# Source: CONTEXT.md D-17; TypedDict chosen for D-27 discretion (Python 3.9+ compatible)
from typing import TypedDict, List

class ReleaseInfo(TypedDict):
    version: str        # parsed version string (tag_name)
    tag: str            # raw tag_name from GitHub API
    channel: str        # "stable" or "prerelease"
    published: str      # ISO-8601 string from published_at
    asset_url: str      # browser_download_url for the board-matching asset

def list_releases(
    self,
    channel_filter: Literal['all', 'pre', 'stable'] = 'all',
    board: str = 'uno',
) -> List[ReleaseInfo]:
    """Returns releases sorted by PEP 440 version descending.
    Omits releases without a matching board asset.
    Omits draft releases.
    """
```

`TypedDict` is recommended for D-27 (discretion) because it provides IDE completion + type safety at zero runtime cost, and is idiomatic for structured dicts returned from API calls. Plain `dict` would also work; dataclass would add `@dataclass` overhead without benefit at this data size.

### PEP 440 Sort Test Case (for test suite)

```python
# Source: VERIFIED via shell — demonstrates the correctness requirement for pre-release ordering
from packaging.version import Version

candidates = ["3.1.0b9", "3.1.0b10", "3.1.0b1", "3.1.0rc1"]
result = sorted([Version(v) for v in candidates], reverse=True)
# Expected: [3.1.0rc1, 3.1.0b10, 3.1.0b9, 3.1.0b1]
assert str(result[0]) == "3.1.0rc1"
assert str(result[1]) == "3.1.0b10"  # b10 > b9 only with Version sort
assert str(result[2]) == "3.1.0b9"
```

---

## Implementation Approach (per-file)

### `firestarter_app/firestarter/constants.py`

**Change:** Add two new URL constants after the existing `FIRESTARTER_RELEASE_URL`:

```python
FIRESTARTER_RELEASES_URL = (
    "https://api.github.com/repos/henols/firestarter/releases"
)
FIRESTARTER_RELEASE_BY_TAG_URL = (
    "https://api.github.com/repos/henols/firestarter/releases/tags/{tag}"
)
```

No other changes. The `FIRMWARE_VERSION_RE` constant can live here or in `firmware.py` — planner chooses. If in `constants.py`, it is imported by `main.py` via the existing `from firestarter.constants import *`.

### `firestarter_app/pyproject.toml`

**Change:** Add `"packaging>=21.0"` to `[project.dependencies]` list. Current list: `pyserial>=3.5`, `requests>=2.20`, `tqdm>=4.60`, `argcomplete>=3.6.2`, `rich>=14.0`. Add `packaging>=21.0` as the sixth entry.

### `firestarter_app/firestarter/firmware.py`

**Wave 1 changes (INST-01):**
1. Add `from packaging.version import Version, InvalidVersion` to imports.
2. Add `import re` if not already present (it is not currently imported).
3. Add `FIRMWARE_VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+((b|rc)[0-9]+)?$')` at module level.
4. Replace `_compare_versions` body with `packaging.version.Version` comparison (Pattern 4 above).
5. Add docstring update to `fetch_latest_release_info`: "Stable-only path; use `fetch_release_info` for general channel selection."

**Wave 2 changes (INST-02/03/04):**
1. Add `FIRESTARTER_RELEASES_URL` and `FIRESTARTER_RELEASE_BY_TAG_URL` to the `from firestarter.constants import *` wildcard (or add directly to constants.py).
2. Add `_fetch_all_releases(self, max_pages=5)` private pagination helper.
3. Add `fetch_release_info(self, channel, version, board)` router (D-16 signature).
4. Add `list_releases(self, channel_filter, board)` enumeration (D-17 signature).
5. Extend `manage_firmware_update` signature with `channel` and `pinned_version` kwargs (D-18).
6. Update `manage_firmware_update` body to dispatch `fetch_release_info` instead of directly calling `fetch_latest_release_info`.

**Preserved unchanged:** `check_current_firmware`, `_download_firmware_file`, `_install_with_avrdude`. These are not touched by Phase 18.

### `firestarter_app/firestarter/main.py` — `create_firmware_args`

**Change:** Restructure to:
1. Create `install_group = fw_parser.add_mutually_exclusive_group()` and add `-i/--install` and `--list` to it.
2. Create `channel_group = fw_parser.add_mutually_exclusive_group()` and add `--pre` and `--firmware-version` (with `type=_validate_firmware_version`) to it.
3. Add `--json` flag to `fw_parser` (not in any mutex group).
4. Return `fw_parser` so the dispatch code can call `fw_parser.error(...)`.
5. Add `_validate_firmware_version` function (local or imported from firmware.py).

**Existing flags that stay on `fw_parser` directly (not in groups):** `-b/--board`, `--avrdude-path`, `-c/--avrdude-config-path`, `-f/--force`.

### `firestarter_app/firestarter/main.py` — dispatch (`args.command == "fw"`)

**Change:** Extend the `elif args.command == "fw":` block:

```python
elif args.command == "fw":
    # 1. Post-parse: --json requires --list
    if args.json and not args.list:
        fw_parser.error("--json requires --list")

    # 2. --list path (read-only, no install)
    if args.list:
        channel_filter = "pre" if args.pre else "stable" if ...(--stable logic)... else "all"
        releases = firmware_manager.list_releases(
            channel_filter=channel_filter,
            board=args.board,
        )
        # format and print table or JSON
        return 0

    # 3. Install path: magic-default beta detection
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
                pass
        except ImportError:
            pass

    # 4. Determine channel
    if getattr(args, "firmware_version", None):
        channel = "pinned"
    elif args.pre:
        channel = "pre"
    else:
        channel = "stable"

    return (
        1 if not firmware_manager.manage_firmware_update(
            install_flag=args.install,
            avrdude_path_override=args.avrdude_path,
            avrdude_config_override=args.avrdude_config_path,
            port_override=args.port,
            board_override=args.board,
            flags=build_arg_flags(args),
            channel=channel,
            pinned_version=getattr(args, "firmware_version", None),
        ) else 0
    )
```

**Note on `--list` + `--pre/--stable/--all`:** D-13 says `--list --pre`, `--list --stable`, `--list --all` are mutually exclusive within `--list`. These are three additional flags needed for `--list` filtering. CONTEXT.md D-13 specifies a mutex group within `--list`. Recommendation: add `--pre-only`, `--stable-only` as flags OR reuse `--pre` with post-parse interpretation for `--list`. The simplest approach: reuse `--pre` for `--list --pre` filter and add `--stable` (boolean flag) for `--list --stable`. When `args.list` is True, `--pre` means filter to pre-releases; `--stable` means filter to stable; neither = all. This avoids adding a third mutex group.

### `firestarter_app/tests/test_firmware_install.py` (NEW)

Class layout matching Phase 15 / `test_fwguard.py` pattern:

```
TestFirmwareInstallStable        — INST-01: stable path, _compare_versions refactor
TestFirmwareInstallPreRelease    — INST-02: --pre selection, fallback to stable
TestFirmwareInstallPinned        — INST-03: --firmware-version, 404, missing asset
TestFirmwareList                 — INST-04: list_releases, --json, channel filters
TestMagicDefault                 — D-21/D-22: beta-app auto-routing
TestVersionComparator            — INST-01: _compare_versions PEP 440 correctness
```

Each class uses an `autouse` fixture (`_isolate_env`) following the `test_update_version.py` / `test_fwguard.py` pattern. All network calls mocked via `monkeypatch.setattr(firmware.requests, "get", ...)`.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| `tuple(map(int, v.split(".")))` version compare | `packaging.version.Version` comparison | Phase 18 | Handles pre-release suffixes correctly; eliminates ValueError on `b2`, `rc1` |
| `/releases/latest` only | Paginated `/releases` + `/releases/tags/{tag}` | Phase 18 | Enables pre-release and pinned install paths |
| No `packaging` in explicit deps | `packaging>=21.0` in `[project.dependencies]` | Phase 18 | Guards against transitive disappearance |
| `fetch_latest_release_info` only | `fetch_release_info(channel, version, board)` router | Phase 18 | Single method handles stable / pre / pinned uniformly |

**No deprecated patterns in Phase 18 scope.**

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | `firestarter_*.hex` asset naming convention will be preserved by Phase 17 for pre-release artifacts | Standard Stack, Architecture | Phase 18's asset-resolution loop silently returns no URL if Phase 17 uses `firestarter-{board}.hex` (dash instead of underscore) |
| A2 | `per_page=30` is GitHub API's default for `/releases` list | GitHub API shape | Only affects D-04 cap sizing — 5 pages * different default would cover fewer/more releases |

**All other claims in this research were verified by direct tool call (shell, curl, grep) or cited from CONTEXT.md locked decisions.**

---

## Open Questions (RESOLVED)

1. **`--list` channel filter flags (`--pre` / `--stable` for list filtering)**

   What we know: D-13 says `--list --pre` / `--list --stable` / `--list --all` are needed; `--pre` is already in mutex group 1 (with `--firmware-version`). Can `--pre` serve dual purpose (install pre-release AND filter list to pre-releases), or does D-13 require separate `--stable` and `--all` flags?

   What's unclear: Whether `--stable` and `--all` need to be added as new boolean flags, or whether the interpretation of `--pre` within `--list` context is sufficient.

   **RESOLVED (revision iteration 1, 2026-05-20):** `--stable` added to the EXISTING `channel_group` as a third member (3-way argparse-native mutex with `--pre` and `--firmware-version`). `--pre` serves dual purpose (install pre-release context AND `--list` filter to pre-releases); `--stable` is install-context redundant ("stay on stable") and list-context filter; `--all` flag dropped (it's the implicit default when no channel flag is set). Implementation: Plan 18-02 Task 2 Step B `channel_group.add_argument` × 3. Cross-checked by Plan 18-01 TestArgparseMutex pairwise mutex tests (`test_pre_and_firmware_version_mutex`, `test_pre_and_stable_mutex`, `test_firmware_version_and_stable_mutex`).

2. **`fw_parser` scope in dispatch**

   What we know: `fw_parser.error(msg)` is the cleanest pattern for `--json requires --list`. `create_firmware_args` currently returns nothing.

   What's unclear: Whether the planner prefers returning `fw_parser` from `create_firmware_args`, or using a module-level variable, or just using `parser.error(msg)` (top-level parser reference also works for post-parse errors).

   **RESOLVED (revision iteration 1, 2026-05-20):** `create_firmware_args` now returns `fw_parser`. Call site captures: `fw_parser = create_firmware_args(subparsers)`. Used in dispatch for `fw_parser.error("--json requires --list")` post-parse validation. All other `create_*_args` functions retain their existing void-return signatures (no callsite changes elsewhere). Implementation: Plan 18-02 Task 2 Step B.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.9+ | All code | ✓ | 3.12.13 | — |
| `packaging` | `_compare_versions`, magic default, version sort | ✓ | 26.2 | — |
| `requests` | All GitHub API calls | ✓ | (in pyproject.toml) | — |
| `pytest` | Test suite | ✓ | (dev dependency) | — |
| `argparse` | CLI flag parsing | ✓ | stdlib | — |

No missing dependencies. `packaging>=21.0` is already present as a transitive dep; adding it to `pyproject.toml` is a declaration change, not an install change.

---

## Validation Architecture

### Test Framework

| Property | Value |
|---|---|
| Framework | pytest (in pyproject.toml dev deps) |
| Config file | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `cd firestarter_app && pytest tests/test_firmware_install.py -x -q` |
| Full suite command | `cd firestarter_app && pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| INST-01 | Stable `fw -i` hits `/releases/latest` unchanged | unit | `pytest tests/test_firmware_install.py::TestFirmwareInstallStable -x` | ❌ Wave 0 |
| INST-01 | `_compare_versions` handles PEP 440 pre-release strings | unit | `pytest tests/test_firmware_install.py::TestVersionComparator -x` | ❌ Wave 0 |
| INST-02 | `--pre` fetches highest pre-release; fallback to stable | unit | `pytest tests/test_firmware_install.py::TestFirmwareInstallPreRelease -x` | ❌ Wave 0 |
| INST-02 | Magic default fires on beta-app install | unit | `pytest tests/test_firmware_install.py::TestMagicDefault -x` | ❌ Wave 0 |
| INST-03 | `--firmware-version` validates regex before network | unit | `pytest tests/test_firmware_install.py::TestFirmwareInstallPinned -x` | ❌ Wave 0 |
| INST-03 | `--firmware-version` 404 → fatal error | unit | `pytest tests/test_firmware_install.py::TestFirmwareInstallPinned -x` | ❌ Wave 0 |
| INST-04 | `--list` enumerates releases as table | unit | `pytest tests/test_firmware_install.py::TestFirmwareList -x` | ❌ Wave 0 |
| INST-04 | `--list --json` outputs JSON array | unit | `pytest tests/test_firmware_install.py::TestFirmwareList -x` | ❌ Wave 0 |
| INST-04 | `--list --pre` filters to pre-releases only | unit | `pytest tests/test_firmware_install.py::TestFirmwareList -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_firmware_install.py -x -q`
- **Per wave merge:** `pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_firmware_install.py` — covers INST-01..04, `TestVersionComparator`, `TestMagicDefault`
- [ ] `mock_releases_factory` helper (local to test file, not conftest.py) for building paginated response mocks

*(Existing `tests/conftest.py` has `fake_serial`, `make_comm` fixtures — no changes needed there for Phase 18 tests which mock `requests.get` directly.)*

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | `FIRMWARE_VERSION_RE` + `argparse.ArgumentTypeError` (D-07) |
| V6 Cryptography | no | — |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| Malicious `--firmware-version` input (path traversal, injection) | Tampering | `FIRMWARE_VERSION_RE` restricts to `X.Y.Z[bN\|rcN]` before network call; no shell execution of version string |
| Rate-limit DoS via `--list` spam | DoS | 60 req/hr anonymous limit (GitHub-enforced); surface 403 clearly; no retry loop |
| Download URL from untrusted API response used directly | Spoofing | URL is `browser_download_url` from GitHub's own API; HTTPS enforced by `requests` default; no URL rewriting |

**No new auth surface.** Phase 18 uses the same unauthenticated GitHub API calls as the existing `fetch_latest_release_info`. No credentials added or stored.

---

## Project Constraints (from CLAUDE.md)

- All code changes for Phase 18 land INSIDE `firestarter_app/` (submodule git repo). The meta-repo at `/workspaces` tracks only `.planning/` and `.claude/`.
- Python app commands run from `firestarter_app/`: `pip install -e .`, `firestarter --help`.
- `firestarter/constants.py` must stay in sync with `firestarter/include/firestarter.h` for the constants defined there. The new URL constants and `FIRMWARE_VERSION_RE` added in Phase 18 are Python-only — no C++ counterpart needed.
- Existing test pattern: class-based pytest with `autouse` fixture for env cleanup, `monkeypatch.setattr` on module attributes (not `unittest.mock.patch`). Match this for `test_firmware_install.py`.

---

## Sources

### Primary (HIGH confidence)

- GitHub REST API (live) — `/repos/henols/firestarter/releases`, `/releases/latest`, `/releases/tags/99.99.99b1` — response shape, pagination Link header, rate-limit headers, HTTP status codes for 404. [VERIFIED: direct curl call 2026-05-20]
- Python shell (packaging 26.2) — `Version("2.0.7_dev")`, `Version("3.0.0-dev")`, all version ordering, `is_prerelease` behavior, `InvalidVersion` trigger conditions. [VERIFIED: python3 shell 2026-05-20]
- Python shell (argparse stdlib) — dual mutex group behavior, `ArgumentTypeError` pattern, post-parse `.error()` exit code. [VERIFIED: python3 shell 2026-05-20]
- Python shell (unittest.mock) — `MagicMock` with `.json()`, `.raise_for_status()`, `.headers`, `.iter_content()` attributes. [VERIFIED: python3 shell 2026-05-20]
- `firestarter_app/firestarter/firmware.py` — current `FirmwareManager` structure, call sites for `_compare_versions` and `fetch_latest_release_info`. [VERIFIED: grep 2026-05-20]
- `firestarter_app/firestarter/main.py` — current `create_firmware_args` shape, dispatch at lines 645-657. [VERIFIED: file read 2026-05-20]
- `firestarter_app/firestarter/constants.py` — current `FIRESTARTER_RELEASE_URL`. [VERIFIED: file read 2026-05-20]
- `firestarter_app/pyproject.toml` — current dependencies, Python >=3.9 constraint. [VERIFIED: file read 2026-05-20]
- `firestarter_app/tests/test_update_version.py` — Phase 15 test pattern (class-based, autouse, monkeypatch). [VERIFIED: file read 2026-05-20]
- `firestarter_app/tests/test_fwguard.py` — Phase 6 test pattern (class-based, autouse, patch.object). [VERIFIED: file read 2026-05-20]

### Secondary (MEDIUM confidence)

- CONTEXT.md D-01..D-30 — all locked decisions. [CITED: .planning/phases/18-beta-aware-firmware-downloader/18-CONTEXT.md]
- REQUIREMENTS.md §INST — INST-01..04 acceptance criteria. [CITED: .planning/REQUIREMENTS.md]
- Phase 15 RESEARCH.md — PEP 440 details, `packaging.version` API, already verified for publisher-side. [CITED: .planning/phases/15-versioning-locked-step-coordination-foundation/15-RESEARCH.md]

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — packaging version verified, requests already in pyproject.toml, argparse stdlib
- Architecture: HIGH — all callers verified via grep, all API endpoints verified via curl, all Python behavior verified via shell
- Pitfalls: HIGH — each pitfall verified by direct test (argparse mutex constraint, version parsing behavior, draft flag presence in API)
- Test patterns: HIGH — Phase 15 and Phase 6 test files read directly

**Research date:** 2026-05-20
**Valid until:** 2026-06-20 (GitHub API shape is stable; packaging behavior is stable)

---

## RESEARCH COMPLETE

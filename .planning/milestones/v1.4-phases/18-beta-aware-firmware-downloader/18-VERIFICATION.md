---
phase: 18-beta-aware-firmware-downloader
verified: 2026-05-20T00:00:00Z
status: passed
score: 9/9 must-haves verified
overrides_applied: 0
re_verification: null
gaps: []
deferred: []
human_verification: []
---

# Phase 18: Beta-Aware Firmware Downloader Verification Report

**Phase Goal:** `firestarter --install` defaults preserved (INST-01 non-regression); `--pre` fetches latest pre-release fw; `--firmware-version X.Y.Z[bN]` pins exact tag; `firestarter firmware list` enumerates releases; `_compare_versions` refactored to PEP 440-safe via `packaging.version.Version`. Beta-installed app's bare `fw -i` auto-routes to `--pre` (D-21 magic default).
**Verified:** 2026-05-20T00:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `firestarter --install` (no flags) continues to delegate to `fetch_latest_release_info`, hitting `/releases/latest` — byte-identical INST-01 path | VERIFIED | `fetch_release_info(channel='stable')` at firmware.py:224-225 directly calls `self.fetch_latest_release_info(board=board)`. Tests in `TestFirmwareInstallStable` (2 tests) confirm the delegation. |
| 2 | `--pre` fetches latest pre-release firmware by PEP 440 sort; falls back to stable when none exist | VERIFIED | `fetch_release_info(channel='pre')` at firmware.py:254-294 paginates via `_fetch_all_releases`, filters `prerelease=True`, sorts `candidates` descending by `Version`, picks highest. `TestFirmwareInstallPreRelease` (4 tests) green. |
| 3 | `--firmware-version X.Y.Z[bN]` validates input against regex at argparse time; hits `/releases/tags/{tag}` on valid input; exits 2 on invalid input with no network call | VERIFIED | `_validate_firmware_version` in main.py:192-205 raises `ArgumentTypeError` on non-match before any network call. `fetch_release_info(channel='pinned')` at firmware.py:227-252 uses `FIRESTARTER_RELEASE_BY_TAG_URL.format(tag=version)`. CLI test confirms `fw -i --firmware-version not-a-version` exits 2. |
| 4 | `firestarter fw --list` outputs plain-text table; `--json` emits JSON; `--pre`/`--stable` filter by channel; `--pre` and `--stable` are mutually exclusive | VERIFIED | Dispatch branch at main.py:739-757. `list_releases` method at firmware.py:300-364. `TestFirmwareList` (5 tests) green. CLI confirms `--list --pre --stable` exits 2. |
| 5 | `_compare_versions` no longer raises `ValueError` on PEP 440 pre-release strings; uses `packaging.version.Version` | VERIFIED | firmware.py:161-177. `tuple(map(int,...))` fully replaced — `grep -v '^#' firmware.py | grep -c 'tuple(map(int,'` returns 0. `TestVersionComparator` (4 tests) including `test_prerelease_versions` (b10 > b9) green. |
| 6 | Magic default (`_maybe_auto_route_to_pre`) auto-routes bare `fw -i` to `--pre` when app is a pre-release; logs INFO with `"Beta app detected"` and `"--firmware-version X.Y.Z"` | VERIFIED | main.py:208-242. Guard at line 224-228 checks `install`, `pre`, `firmware_version`, and `stable`. `TestMagicDefault` (5 tests including CR-01 post-review test) green. |
| 7 | `--stable` is a third member of `channel_group` (argparse enforces 3-way mutex natively); `fw_parser` captured at call site for `fw_parser.error()` | VERIFIED | `channel_group.add_argument("--stable",...)` at main.py:277-281. `grep -c 'channel_group.add_argument'` returns 3. `return fw_parser` at line 316; `fw_parser = create_firmware_args(subparsers)` at line 491. |
| 8 | `fetch_latest_release_info` preserved with unchanged signature and behavior (D-15 contract) | VERIFIED | `grep -c 'def fetch_latest_release_info' firmware.py` returns 1. Body at firmware.py:125-159 unchanged except one docstring note. |
| 9 | All 30 Wave-0 tests green; existing 47-test baseline still green (77 total) | VERIFIED | `pytest tests/test_firmware_install.py` → 30 passed in 0.48s. `pytest tests/` → 77 passed in 1.37s. |

**Score:** 9/9 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/firmware.py` | `fetch_release_info`, `list_releases`, `_fetch_all_releases`, `FIRMWARE_VERSION_RE`, `ReleaseInfo` TypedDict, PEP 440 `_compare_versions` | VERIFIED | All symbols present and substantive. 629 lines total. |
| `firestarter_app/firestarter/constants.py` | `FIRESTARTER_RELEASES_URL`, `FIRESTARTER_RELEASE_BY_TAG_URL` | VERIFIED | Both constants at lines 12-18. |
| `firestarter_app/firestarter/main.py` | `_validate_firmware_version`, `_maybe_auto_route_to_pre(args)`, extended `create_firmware_args` (returns `fw_parser`, 3-way channel mutex), full dispatch | VERIFIED | All symbols present. 860 lines total. |
| `firestarter_app/pyproject.toml` | `"packaging>=21.0"` in dependencies | VERIFIED | Line 54. |
| `firestarter_app/tests/test_firmware_install.py` | 7 classes, 30 tests, `mock_releases_factory`, `mock_404_response`, autouse fixtures | VERIFIED | 30 tests across 7 classes. Post-review `test_explicit_stable_flag_no_magic` present at line 907. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `create_firmware_args` | `fw_parser` mutex groups | `install_group` (2 members) + `channel_group` (3 members) | VERIFIED | `install_group.add_argument` count=2; `channel_group.add_argument` count=3 |
| `main.py dispatch (fw)` | `firmware_manager.manage_firmware_update` | `channel=channel, pinned_version=...` kwargs | VERIFIED | Lines 770-782 pass both kwargs |
| `fetch_release_info(channel='stable')` | `fetch_latest_release_info` | back-compat shim delegation | VERIFIED | firmware.py:224-225 `return self.fetch_latest_release_info(board=board)` |
| `fetch_release_info(channel='pre')` | `_fetch_all_releases` | paginated `/releases` call | VERIFIED | firmware.py:256 calls `self._fetch_all_releases()` |
| `fetch_release_info(channel='pinned')` | `FIRESTARTER_RELEASE_BY_TAG_URL` | `.format(tag=version)` | VERIFIED | firmware.py:231 `url = FIRESTARTER_RELEASE_BY_TAG_URL.format(tag=version)` |
| `_maybe_auto_route_to_pre` | `packaging.version.Version.is_prerelease` | `Version(_pkg.__version__).is_prerelease` | VERIFIED | main.py:233 |
| `dispatch args.stable` | `channel_filter='stable'` | `elif args.stable: channel_filter = "stable"` in `--list` branch | VERIFIED | main.py:743-744 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|-------------------|--------|
| `firmware.py:_fetch_all_releases` | `all_releases` | `requests.get(FIRESTARTER_RELEASES_URL, ...)` → `response.json()` | Yes — paginated GitHub API | FLOWING |
| `firmware.py:fetch_release_info(channel='stable')` | `(version, url)` | Delegates to `fetch_latest_release_info` → `requests.get(FIRESTARTER_RELEASE_URL, ...)` | Yes — same GitHub `/releases/latest` as pre-v1.4 | FLOWING |
| `firmware.py:list_releases` | `out: List[ReleaseInfo]` | `_fetch_all_releases()` → filter + sort | Yes — sorted list from real paginated data | FLOWING |
| `main.py:dispatch (fw --list)` | `releases` | `firmware_manager.list_releases(...)` | Yes — rendered in table or JSON | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| 30 new Phase-18 tests pass | `pytest tests/test_firmware_install.py -v` | 30 passed in 0.48s | PASS |
| Full suite — no regressions | `pytest tests/ -v` | 77 passed in 1.37s | PASS |
| `fw --help` shows all 5 new flags | `python -m firestarter.main fw --help` | `--pre`, `--firmware-version`, `--list`, `--json`, `--stable` all listed | PASS |
| D-19 mutex: `--pre + --firmware-version` rejected | `fw -i --pre --firmware-version 3.1.0` | exit=2, `not allowed with argument --pre` | PASS |
| Revision blocker #1: `--pre + --stable` rejected | `fw --list --pre --stable` | exit=2, `not allowed with argument --pre` | PASS |
| Type= validator rejects invalid version | `fw -i --firmware-version not-a-version` | exit=2, `ArgumentTypeError` | PASS |
| `--json` requires `--list` post-parse check | `fw --json` | exit=2, `--json requires --list` | PASS |
| D-15: `fetch_latest_release_info` preserved | `grep -c 'def fetch_latest_release_info' firmware.py` | 1 | PASS |
| CR-02: `\Z` anchor in `FIRMWARE_VERSION_RE` | `grep 'FIRMWARE_VERSION_RE = re.compile' firmware.py` | contains `\Z` not `$` | PASS |
| CR-01: `--stable` guard in `_maybe_auto_route_to_pre` | `grep -E 'not getattr.args, .stable' main.py` | line found | PASS |
| Baseline 47-test suite | `pytest tests/ --ignore=tests/test_firmware_install.py` | 47 passed in 1.08s | PASS |

### Probe Execution

No declared probes for this phase. Step 7c: SKIPPED (no `scripts/*/tests/probe-*.sh` for Phase 18).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| INST-01 | 18-01, 18-02 | `firestarter --install` non-regression; stable path preserved; `_compare_versions` PEP 440-safe | SATISFIED | `fetch_release_info(channel='stable')` delegates to `fetch_latest_release_info`. `_compare_versions` uses `Version(a) >= Version(b)`. `TestFirmwareInstallStable` + `TestVersionComparator` green. |
| INST-02 | 18-01, 18-02 | `--pre` fetches highest PEP 440 pre-release; fallback to stable; magic default for beta-installed app | SATISFIED | `fetch_release_info(channel='pre')` + `_maybe_auto_route_to_pre`. `TestFirmwareInstallPreRelease` + `TestMagicDefault` green. |
| INST-03 | 18-01, 18-02 | `--firmware-version X.Y.Z[bN]` pinned tag fetch; regex validated before network; mutex with `--pre` | SATISFIED | `_validate_firmware_version` at argparse `type=` time; `FIRMWARE_VERSION_RE` with `\Z` anchor; `fetch_release_info(channel='pinned')`. `TestFirmwareInstallPinned` + `TestArgparseMutex` green. |
| INST-04 | 18-01, 18-02 | `firestarter firmware list` with `--all/--pre/--stable/--json` | SATISFIED | `list_releases` + dispatch `--list` branch. `TestFirmwareList` green. `fw --list --json` emits JSON. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None found | — | Scanned `firmware.py`, `main.py`, `constants.py`, `pyproject.toml`, `test_firmware_install.py` for `TBD/FIXME/XXX/PLACEHOLDER/TODO/HACK`. No unreferenced debt markers found. | — | None |

Note: REVIEW.md documents WR-01 (no HTTPS scheme enforcement on download URL), WR-02 (dead `elif` branch in `manage_firmware_update`), WR-03 (silent exit-0 on network failure during bare version check), and IN-01 (`str | None` union syntax Python 3.10+ only). These are carry-forward warnings from the code review that are pre-existing or deferred; none block INST-01..04 goal achievement. CR-01 and CR-02 from the code review were fixed and are verified above.

### Human Verification Required

None — all must-haves are verified programmatically via pytest and CLI spot-checks.

### Gaps Summary

No gaps. All 9 observable truths are VERIFIED, all 5 required artifacts exist and are substantive and wired, all 7 key links are connected, all 4 requirement IDs (INST-01..04) are satisfied, and the full 77-test suite passes with zero failures.

---

## What Was Delivered

Phase 18 shipped in two waves across two plans:

**Wave 0 (Plan 18-01):** A 29-test failing scaffold (`test_firmware_install.py`) pinning the behavioral contract for all four INST requirements. All 7 test classes collected successfully; all failed RED on missing symbols, confirming the measurable target for Wave 1.

**Wave 1 (Plan 18-02):** Full implementation across 4 files:
- `firmware.py` extended with `FIRMWARE_VERSION_RE` (with CR-02 `\Z` anchor fix), `ReleaseInfo` TypedDict, PEP 440-safe `_compare_versions`, `_fetch_all_releases`, `fetch_release_info` (stable/pre/pinned router), `list_releases`. `fetch_latest_release_info` preserved unchanged per D-15.
- `constants.py` gained `FIRESTARTER_RELEASES_URL` and `FIRESTARTER_RELEASE_BY_TAG_URL`.
- `main.py` gained `_validate_firmware_version`, `_maybe_auto_route_to_pre(args)` (args-only signature per revision warning #6; `logging.getLogger(__name__)` for caplog capture), restructured `create_firmware_args` (3-way channel mutex: `--pre XOR --firmware-version XOR --stable`; returns `fw_parser`), and full `fw` dispatch branch.
- `pyproject.toml` added `"packaging>=21.0"` as explicit dependency.

**Post-review fixes (commits `e421186` in submodule):** CR-01 — `_maybe_auto_route_to_pre` guard now includes `and not getattr(args, "stable", False)` so explicit `--stable` opts out of magic default; `test_explicit_stable_flag_no_magic` added to `TestMagicDefault` (test count grew from 29 to 30). CR-02 — `FIRMWARE_VERSION_RE` regex anchor changed from `$` to `\Z` to prevent trailing-newline bypass.

The 30th test (`test_explicit_stable_flag_no_magic`) was added post-review per CR-01 fix, matching the plan's instruction to add a corresponding test. The SUMMARY from Plan 18-01 reported 29 tests; the final count is 30. This is a plan-allowed count increase, not a deviation.

---

_Verified: 2026-05-20T00:00:00Z_
_Verifier: Claude (gsd-verifier)_

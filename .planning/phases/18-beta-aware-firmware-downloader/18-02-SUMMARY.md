---
phase: 18-beta-aware-firmware-downloader
plan: "02"
subsystem: firestarter_app
tags:
  - cli
  - github-api
  - argparse
  - packaging-pep440
  - phase-18-impl
dependency_graph:
  requires:
    - 18-01  # Wave 0 RED-gate scaffold (29 test stubs)
  provides:
    - fetch_release_info (stable/pre/pinned channel router)
    - list_releases (PEP 440-sorted enumeration)
    - FIRMWARE_VERSION_RE (consumer-side validation regex)
    - _maybe_auto_route_to_pre (magic-default helper)
    - --pre / --firmware-version / --list / --json / --stable CLI flags
  affects:
    - 18-03  # if any; Phase 19 (DOC-01/DOC-02) consumes final CLI flag spellings verbatim
tech_stack:
  added:
    - packaging>=21.0 (PEP 440 version comparison and is_prerelease detection)
  patterns:
    - TypedDict for structured ReleaseInfo dicts (D-27)
    - Link: rel="next" pagination with cap-at-5-pages (D-04)
    - argparse mutually_exclusive_group for 3-way channel mutex (revision blocker #1)
    - lazy import inside type= validator to avoid circular imports
key_files:
  modified:
    - firestarter_app/firestarter/firmware.py
    - firestarter_app/firestarter/main.py
    - firestarter_app/firestarter/constants.py
    - firestarter_app/pyproject.toml
decisions:
  - "D-15 honored: fetch_latest_release_info body preserved unchanged; only docstring gained one note"
  - "D-21/D-22/D-25: _maybe_auto_route_to_pre(args) args-only signature; logging.getLogger(__name__) for caplog auto-capture"
  - "Revision blocker #1 CLEANEST: --stable joins channel_group alongside --pre and --firmware-version; argparse enforces 3-way mutex natively"
  - "Two submodule commits for Task 1 (3 files) and Task 2 (main.py) for clarity per planner allowance"
metrics:
  duration: "~45 minutes"
  completed: "2026-05-20"
  tasks_completed: 2
  files_modified: 4
---

# Phase 18 Plan 02: Beta-Aware Firmware Downloader — Wave 1 Implementation Summary

Wave 1 extends `firestarter_app/` so the 29 Wave-0 RED-gate tests turn GREEN.
Delivered: JWT auth via `packaging.version.Version`, paginated `/releases` endpoint, three firmware channels (`stable`/`pre`/`pinned`), `fw --list` table output, magic-default auto-routing for beta-installed apps, and argparse 3-way channel mutex.

## Tasks Executed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | pyproject.toml + constants.py + firmware.py | `84043e5` | pyproject.toml, constants.py, firmware.py |
| 2 | main.py dispatch + helpers + argparse | `76b665e` | main.py |

## What Was Built

### Task 1 — firmware.py, constants.py, pyproject.toml (commit `84043e5`)

**pyproject.toml:** Added `"packaging>=21.0"` to `[project.dependencies]`.

**constants.py:** Added two new URL constants after `FIRESTARTER_RELEASE_URL`:
- `FIRESTARTER_RELEASES_URL` — paginated list endpoint (no `/latest` suffix)
- `FIRESTARTER_RELEASE_BY_TAG_URL` — templated by-tag endpoint (`{tag}` placeholder)

**firmware.py changes:**
- Extended `from typing import` to include `Literal`, `List`, `TypedDict`
- Added `import re` and `from packaging.version import Version, InvalidVersion`
- Added module-level `FIRMWARE_VERSION_RE` (consumer-side regex, superset of Phase 15's `BETA_VERSION_RE`)
- Added `_LINK_NEXT_RE` for parsing `Link: rel="next"` headers
- Added `ReleaseInfo(TypedDict)` with keys: `version`, `tag`, `channel`, `published`, `asset_url`
- Refactored `_compare_versions`: replaced `tuple(map(int, v.split(".")))` with `Version(a) >= Version(b)` — PEP 440-safe, handles `3.1.0b10`, `3.1.0rc1`, `2.0.7_dev` correctly
- Added docstring note to `fetch_latest_release_info` (D-15 preserved — body unchanged)
- Added `_fetch_all_releases(max_pages=5)`: paginates via `Link:rel=next`, caps at 5 pages with INFO log
- Added `fetch_release_info(channel, version, board)` router: stable→shim; pinned→by-tag; pre→paginated+sorted+fallback
- Added `list_releases(channel_filter, board)`: enumerates, filters drafts, sorts PEP 440 descending
- Extended `manage_firmware_update` with `channel` and `pinned_version` kwargs, dispatches through `fetch_release_info`

### Task 2 — main.py (commit `76b665e`)

- Added `_validate_firmware_version(value)` argparse `type=` callable with lazy import of `FIRMWARE_VERSION_RE`
- Added `_maybe_auto_route_to_pre(args) -> None` with `args`-only signature (revision warning #6); uses `logging.getLogger(__name__)` internally so `caplog` auto-captures; implements D-21/D-22/D-23/D-24/D-25
- Restructured `create_firmware_args`: `install_group` (-i/--install XOR --list); `channel_group` (--pre XOR --firmware-version XOR --stable — 3-way mutex per revision blocker #1); added `--json` directly to `fw_parser`; now returns `fw_parser`
- Changed call site: `fw_parser = create_firmware_args(subparsers)` (captures return for `fw_parser.error()`)
- Replaced `fw` dispatch block: `--json` requires `--list` post-parse check; `--list` branch with channel_filter; magic-default before install; channel/pinned_version routing to `manage_firmware_update`

## Test Results

### Wave-0 suite (target)
```
29 passed in 0.48s
```
All 7 test classes GREEN:
- `TestFirmwareInstallStable` — 2 tests
- `TestVersionComparator` — 4 tests
- `TestFirmwareInstallPreRelease` — 4 tests
- `TestFirmwareInstallPinned` — 4 tests
- `TestFirmwareList` — 5 tests
- `TestMagicDefault` — 5 tests
- `TestArgparseMutex` — 5 tests

### Full suite (regression check)
```
76 passed in 1.55s
```
47 baseline tests + 29 new tests — zero regressions.

## D-15 Contract Verification

`fetch_latest_release_info` is preserved:
```
grep -c 'def fetch_latest_release_info' firestarter_app/firestarter/firmware.py
→ 1

git -C firestarter_app diff HEAD~2 HEAD -- firestarter/firmware.py | grep 'def fetch_latest_release_info'
→ (no output — signature unchanged in diff)
```

Only the docstring gained one note: `Stable-only path; use fetch_release_info for general channel selection.`

## Magic-Default INFO Line (D-25 / D-30)

Exact wording captured from test execution (caplog):
```
Beta app detected — defaulting to --pre. Use --firmware-version X.Y.Z to pin a stable version.
```

Constraints satisfied:
- Contains `"Beta app detected"` (D-25)
- Contains `"--firmware-version X.Y.Z"` (D-30 escape-hatch wording)

## CLI Help Output

```
$ python -m firestarter.main fw --help
usage: main.py fw [-h] [-i | --list]
                  [--pre | --firmware-version VERSION | --stable]
                  [-b {uno,leonardo}] [--avrdude-path AVRDUDE_PATH]
                  [-c AVRDUDE_CONFIG_PATH] [-f] [--json]

options:
  --list                List available firmware releases for the configured board.
  --pre                 Fetch latest pre-release firmware (mirrors pip install --pre).
  --firmware-version VERSION
  --stable              Explicitly select stable channel. With --list, filters to stable releases only.
  --json                Output --list results as JSON array (only with --list).
```

## Sanity Checks Passed

- `fw -i --pre --firmware-version 3.1.0` → exit 2 (argparse mutex)
- `fw --list --pre --stable` → exit 2 (revision blocker #1 — same channel_group)
- `fw -i --firmware-version not-a-version` → exit 2 (type= validator)
- `fw --json` (without --list) → exit 2 (`fw_parser.error("--json requires --list")`)

## Diff Stats

```
firestarter/constants.py |   8 ++
firestarter/firmware.py  | 234 +++++++++++++++++++++++++++++++++++++++++++---
firestarter/main.py      | 127 +++++++++++++++++++++++++-
pyproject.toml           |   1 +
4 files changed, 359 insertions(+), 11 deletions(-)
```

## Deviations from Plan

None — plan executed exactly as specified. Two submodule commits were made per planner allowance (Task 1: 3 files; Task 2: main.py) for clarity in the git history.

## Known Stubs

None. All new symbols are fully implemented and wired. The `list_releases` method returns real data (not placeholder). The `fetch_release_info` router is fully branched. No TODOs remain in the four modified files.

## Threat Flags

No new threat surface beyond what the plan's `<threat_model>` already registered. T-18-04 (--firmware-version injection) is mitigated by `FIRMWARE_VERSION_RE` at argparse `type=` time before any `.format()` or network call. T-18-07 (malformed `__version__`) is mitigated by `try/except InvalidVersion: pass` in `_maybe_auto_route_to_pre`.

## Phase 19 Contract Note

Phase 19 (Documentation) consumes the final CLI surface verbatim:
- Flags: `--pre`, `--firmware-version VERSION`, `--list`, `--json`, `--stable`
- Magic-default INFO line exact wording: `Beta app detected — defaulting to --pre. Use --firmware-version X.Y.Z to pin a stable version.`

## Self-Check

### Files created/modified
- `/workspaces/firestarter_app/firestarter/firmware.py` — FOUND
- `/workspaces/firestarter_app/firestarter/constants.py` — FOUND
- `/workspaces/firestarter_app/firestarter/main.py` — FOUND
- `/workspaces/firestarter_app/pyproject.toml` — FOUND

### Commits
- `84043e5` — FOUND (git log firestarter_app)
- `76b665e` — FOUND (git log firestarter_app)

## Self-Check: PASSED

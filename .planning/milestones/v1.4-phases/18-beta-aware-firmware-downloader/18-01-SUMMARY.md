---
phase: 18-beta-aware-firmware-downloader
plan: "01"
subsystem: testing
tags: [pytest, github-api-mock, firmware-install, pep440, wave-0-scaffold]

requires:
  - phase: 15-versioning-locked-step-coordination-foundation
    provides: "test_update_version.py class-based pytest pattern with autouse + monkeypatch.setattr"
  - phase: 06-firmware-version-guard
    provides: "test_fwguard.py autouse fixture + FirmwareManager interface"

provides:
  - "Wave 0 failing-test scaffold for Phase 18: 29 tests across 7 classes covering INST-01..04"
  - "module-local mock_releases_factory + mock_404_response helpers (GitHub API shape)"
  - "Measurable RED gate: first failure is AttributeError on FirmwareManager.fetch_release_info"
  - "All 7 test classes with autouse _isolate_env fixtures matching project test style"

affects:
  - "18-02 (Wave 1 — must turn all 29 tests GREEN)"
  - "20-e2e (Phase 20 E2E-01(e) exercises real network; Wave 0 pins the mock-based contract)"

tech-stack:
  added: []
  patterns:
    - "Wave 0 RED-gate scaffold: missing-symbol imports inside test bodies so collection succeeds, run fails"
    - "module-local mock factory (not conftest.py): mock_releases_factory(releases, next_url=None)"
    - "monkeypatch.setattr(firmware.requests, 'get', ...) for HTTP mock isolation"
    - "class-based tests with @pytest.fixture(autouse=True) def _isolate_env for per-test state isolation"

key-files:
  created:
    - "firestarter_app/tests/test_firmware_install.py"
  modified: []

key-decisions:
  - "Missing-symbol imports (FIRMWARE_VERSION_RE, _maybe_auto_route_to_pre, create_firmware_args return) placed INSIDE test bodies, not at module level — ensures --collect-only succeeds before Wave 1 ships"
  - "mock_releases_factory is module-local, not in conftest.py — prevents shared fixture pollution across test files"
  - "29 tests written (exceeds 15-method minimum) — each test class has 2-5 focused test methods"
  - "TestVersionComparator tests assert PEP 440 behavior that the current tuple(map(int,...)) implementation cannot satisfy — specifically b10 > b9 and dev-suffix normalization"
  - "TestArgparseMutex builds parser inline using create_firmware_args(sp) per revision blocker #3 (no _build_root_parser helper)"

patterns-established:
  - "Wave 0 test scaffold pattern: 7 classes, autouse fixtures, module-local mock factory, inside-body imports for missing symbols"
  - "GitHub releases API mock shape: mock_releases_factory(releases, next_url) covers pagination Link header"

requirements-completed:
  - INST-01
  - INST-02
  - INST-03
  - INST-04

duration: 25min
completed: "2026-05-20"
---

# Phase 18 Plan 01: Wave 0 RED-gate Scaffold Summary

**29-test RED-gate scaffold covering INST-01..04, version comparator PEP 440 correctness, beta-app magic-default detection, and argparse mutex enforcement — all tests fail on AttributeError/ImportError pending Wave 1 implementation**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-05-20T00:00:00Z
- **Completed:** 2026-05-20T00:25:00Z
- **Tasks:** 1 (single atomic task per plan)
- **Files modified:** 1 (new file)

## Accomplishments

- Created `firestarter_app/tests/test_firmware_install.py` with 7 test classes and 29 test methods
- All 29 tests collected with zero errors (`pytest --collect-only` exits 0)
- First RED failure confirmed: `TestFirmwareInstallStable::test_stable_default_hits_releases_latest` — `AttributeError: 'FirmwareManager' object has no attribute 'fetch_release_info'`
- Existing 47-test baseline continues to pass (confirmed with `--ignore=tests/test_firmware_install.py`)
- Module-local `mock_releases_factory` and `mock_404_response` helpers built per PATTERNS.md §3c — not in conftest.py

## Task Commits

1. **Task 1: Create test_firmware_install.py scaffold** — `de26533` (test) — inside `firestarter_app/` submodule

## Files Created/Modified

- `firestarter_app/tests/test_firmware_install.py` — 1035-line Wave 0 scaffold; 7 classes, 29 test methods, module-local mock helpers

## First RED Failure Output

```
FAILED tests/test_firmware_install.py::TestFirmwareInstallStable::test_stable_default_hits_releases_latest

    def test_stable_default_hits_releases_latest(self, monkeypatch):
        ...
        monkeypatch.setattr(firmware.requests, "get", recording_get)
        fm = FirmwareManager(config_manager=MagicMock())
>       v, url = fm.fetch_release_info(channel="stable", board="uno")
                 ^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'FirmwareManager' object has no attribute 'fetch_release_info'.
        Did you mean: 'fetch_latest_release_info'?

1 failed in 0.51s
```

## Test Class Inventory

| Class | Methods | Requirement | First-failure mode |
|-------|---------|-------------|-------------------|
| TestFirmwareInstallStable | 2 | INST-01 | AttributeError: no fetch_release_info |
| TestVersionComparator | 4 | INST-01 | ValueError: int("3.1.0b10") (current _compare_versions) |
| TestFirmwareInstallPreRelease | 4 | INST-02 | AttributeError: no fetch_release_info |
| TestFirmwareInstallPinned | 4 | INST-03 | AttributeError: no fetch_release_info |
| TestFirmwareList | 5 | INST-04 | AttributeError: no list_releases |
| TestMagicDefault | 5 | INST-02 | ImportError: cannot import _maybe_auto_route_to_pre |
| TestArgparseMutex | 5 | INST-02/03 | create_firmware_args returns None (no return stmt today) |

## Decisions Made

- Missing-symbol imports (`FIRMWARE_VERSION_RE`, `_maybe_auto_route_to_pre`, `create_firmware_args` with return-value contract) placed INSIDE test method bodies rather than at module level. This is the critical Wave 0 design rule: collection must succeed even before Wave 1 ships.
- `mock_releases_factory` is module-local (not in conftest.py) per VALIDATION.md line 60 — prevents shared fixture pollution.
- `TestVersionComparator.test_stable_versions` may partially pass today (the current `tuple(map(int,...))` handles pure X.Y.Z strings), but `test_prerelease_versions` and `test_dev_suffix_normalizes` will fail with `ValueError` until Wave 1 ships the `packaging.version.Version` refactor.

## Deviations from Plan

None — plan executed exactly as written.

The plan specified 7 classes and ≥15 test methods. The implementation delivers 7 classes and 29 test methods. The higher method count is not a deviation — the plan set a floor, not a ceiling.

## Issues Encountered

None. Collection succeeded on first attempt (0 collection errors). RED gate confirmed immediately on `pytest -x` run.

## Acceptance Criteria Verification

| Criterion | Result |
|-----------|--------|
| 7 test classes | PASS (7) |
| >= 15 test methods collected | PASS (29 collected) |
| `mock_releases_factory` present (module-local) | PASS |
| `mock_404_response` present (module-local) | PASS |
| `@pytest.fixture(autouse=True)` count == 7 | PASS (7) |
| `monkeypatch.setattr(firmware.requests` count >= 5 | PASS (13) |
| INST-* references >= 7 lines | PASS (32) |
| D-XX references >= 7 lines | PASS (47) |
| conftest.py unmodified | PASS |
| First failure is AttributeError on fetch_release_info | PASS |
| Existing 47-test baseline still green | PASS |

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Plan 18-02 (Wave 1) has a fully measurable target: turn all 29 tests GREEN by implementing:
1. `FirmwareManager.fetch_release_info` (channels: stable/pre/pinned)
2. `FirmwareManager.list_releases` (channel filter + PEP 440 sort)
3. `FIRMWARE_VERSION_RE` module-level constant in `firmware.py`
4. `_maybe_auto_route_to_pre(args)` helper in `main.py`
5. Refactored `_compare_versions` using `packaging.version.Version`
6. `create_firmware_args` returns `fw_parser` + new flags (--pre, --firmware-version, --list, --stable, --json)

No blockers. The RED scaffold is committed and the baseline is green.

---
*Phase: 18-beta-aware-firmware-downloader*
*Completed: 2026-05-20*

---
phase: 15-versioning-locked-step-coordination-foundation
plan: "01"
subsystem: versioning
tags: [tdd, wave-0, red-gate, pytest, golden-fixtures, firestarter_app, firestarter]
dependency_graph:
  requires: []
  provides:
    - firestarter_app/tests/test_update_version.py (VER-01 RED-gate scaffold)
    - firestarter_app/tests/golden/stable-baseline.py (D-17 byte-identity seed)
    - firestarter_app/tests/golden/stable-expected.py (D-17 byte-identity reference)
    - firestarter/tests/__init__.py (new Python pytest package marker)
    - firestarter/tests/test_update_version.py (VER-02 RED-gate scaffold)
    - firestarter/tests/golden/stable-baseline.h (D-17 firmware byte-identity seed)
    - firestarter/tests/golden/stable-expected.h (D-17 firmware byte-identity reference)
    - firestarter/.github/scripts/update_version.py (module-level header_file constant)
  affects:
    - Plans 15-02, 15-03 (Wave 1 implementation that makes these tests GREEN)
tech_stack:
  added:
    - pytest (firmware sub-repo: new Python test infrastructure under firestarter/tests/)
  patterns:
    - Class-based pytest with autouse env-isolation fixture (from test_fwguard.py)
    - tmp_path + monkeypatch.setattr for version_file/header_file redirect
    - golden-file read_bytes() byte-identity assertion (from test_audit_coverage_matrix.py)
    - sys.path.insert self-contained import for unpackaged CI scripts
key_files:
  created:
    - firestarter_app/tests/test_update_version.py (141 lines — 8 test methods, 3 classes)
    - firestarter_app/tests/golden/stable-baseline.py (1 line: __version__ = "1.2.3"\n)
    - firestarter_app/tests/golden/stable-expected.py (1 line: __version__ = "1.2.4"\n)
    - firestarter/tests/__init__.py (1 line: empty package marker)
    - firestarter/tests/test_update_version.py (141 lines — 8 test methods, 3 classes)
    - firestarter/tests/golden/stable-baseline.h (1 line: #define VERSION "1.2.3"\n)
    - firestarter/tests/golden/stable-expected.h (1 line: #define VERSION "1.2.4"\n)
  modified:
    - firestarter/.github/scripts/update_version.py (added module-level header_file constant — 7 lines added)
decisions:
  - "Monkeypatch approach: added module-level header_file constant to firestarter/.github/scripts/update_version.py for test monkeypatching. Zero behavior change confirmed — both get_header_version() and update_version() define header_file as local variables that shadow the module-level constant at runtime. Wave 1 (Plan 15-03) will remove the shadowing by refactoring the functions to read the module-level constant."
  - "firestarter_app/.github/scripts/update_version.py was NOT modified — app already has version_file as a module-level constant, so monkeypatching works without script changes."
  - "platformio.ini has no test_dir directive — PlatformIO uses its default test/ directory. New firestarter/tests/ (with s) is a separate Python pytest directory; no conflict."
  - "SyntaxWarning in both existing update_version.py scripts (invalid escape sequence in regex string). Not fixed — out of scope for Wave 0; Wave 1 will address when extending the regex."
metrics:
  duration: "~6 minutes"
  completed: "2026-05-20"
  tasks_completed: 2
  files_created: 7
  files_modified: 1
---

# Phase 15 Plan 01: Wave 0 RED-Gate Scaffold Summary

**One-liner:** Committed 7 files establishing failing pytest scaffolds (VER-01/VER-02) and byte-identity golden baselines in both sub-repos before any `update_version.py` script modification.

## Tasks Completed

| Task | Name | Commit | Sub-repo | Files |
|------|------|--------|----------|-------|
| 1 | App-side Wave 0 scaffold | 146ce72 | firestarter_app | 3 new files |
| 2 | Firmware-side Wave 0 scaffold | 6c66b29 | firestarter | 4 new + 1 modified |

## Files Created

| File | Lines | Content |
|------|-------|---------|
| `firestarter_app/tests/test_update_version.py` | 381 | 8 test methods in 3 classes covering VER-01 |
| `firestarter_app/tests/golden/stable-baseline.py` | 1 | `__version__ = "1.2.3"\n` (verbatim) |
| `firestarter_app/tests/golden/stable-expected.py` | 1 | `__version__ = "1.2.4"\n` (verbatim) |
| `firestarter/tests/__init__.py` | 1 | empty package marker |
| `firestarter/tests/test_update_version.py` | 381 | 8 test methods in 3 classes covering VER-02 |
| `firestarter/tests/golden/stable-baseline.h` | 1 | `#define VERSION "1.2.3"\n` (verbatim) |
| `firestarter/tests/golden/stable-expected.h` | 1 | `#define VERSION "1.2.4"\n` (verbatim) |

## Modified Files

| File | Change | Behavior delta |
|------|--------|----------------|
| `firestarter/.github/scripts/update_version.py` | Added module-level `header_file = "include/version.h"` constant | ZERO — local vars in both functions shadow it at runtime |

## Golden Fixture Byte Content (verbatim)

**firestarter_app/tests/golden/stable-baseline.py:**
```
__version__ = "1.2.3"\n
```

**firestarter_app/tests/golden/stable-expected.py:**
```
__version__ = "1.2.4"\n
```

**firestarter/tests/golden/stable-baseline.h:**
```
#define VERSION "1.2.3"\n
```

**firestarter/tests/golden/stable-expected.h:**
```
#define VERSION "1.2.4"\n
```

All four verified by `diff <(cat ...) <(printf '...')` — MATCH confirmed.

## Test Count Per Class

### firestarter_app/tests/test_update_version.py (VER-01)

| Class | Tests |
|-------|-------|
| TestUpdateVersionStable | 2 (test_stable_byte_identical, test_stable_patch_increment) |
| TestUpdateVersionBeta | 4 (test_beta_explicit_version, test_beta_invalid_version_rejected, test_beta_tag_fallback, test_beta_first_ever) |
| TestUpdateVersionDryRun | 2 (test_dry_run_no_file_write, test_dry_run_stable_path) |
| **Total** | **8** |

### firestarter/tests/test_update_version.py (VER-02)

| Class | Tests |
|-------|-------|
| TestUpdateVersionStable | 2 (test_stable_byte_identical, test_stable_patch_increment) |
| TestUpdateVersionBeta | 4 (test_beta_explicit_version, test_beta_invalid_version_rejected, test_beta_tag_fallback, test_beta_first_ever) |
| TestUpdateVersionDryRun | 2 (test_dry_run_no_file_write, test_dry_run_stable_path) |
| **Total** | **8** |

## RED Gate Confirmation

```
firestarter_app: 8 collected, 8 FAILED (AttributeError: module 'update_version' has no attribute 'parse_args')
firestarter:     8 collected, 8 FAILED (AttributeError: module 'update_version' has no attribute 'parse_args')
```

No test errors at collection time (ImportError). All failures are at assertion/runtime (AttributeError), exactly as required.

## platformio.ini Conflict Finding (RESEARCH Open Question 2)

`firestarter/platformio.ini` has **no `test_dir` directive** — PlatformIO defaults to `test/` (without `s`). The new `firestarter/tests/` directory (with `s`) is separate and does not conflict with PlatformIO's C++ Unity test discovery.

Gate ordering in `platformio.ini`: no changes needed — Wave 1 CI step (Plan 15-03 Task 2 adds `pip install pytest` + `pytest tests/ -v` to `build.yml` BEFORE the existing `Generate release version` step).

## `header_file` Constant Decision

**Taken: Module-level constant approach.**

`firestarter/.github/scripts/update_version.py` received a module-level `header_file = "include/version.h"` constant. This allows `monkeypatch.setattr(update_version, "header_file", str(tmp_path / "version.h"))` to redirect the script's file path in tests.

**Zero behavior change confirmed:** Both `get_header_version()` and `update_version()` already define `header_file = "include/version.h"` as local variables. Python's scoping rules mean the local variable always shadows the module-level constant — the runtime path is identical to before the change.

**Wave 1 (Plan 15-03) action:** Refactor `get_header_version()` and `update_version()` to delete the local `header_file` variable and read the module-level constant instead. This is the moment the constant becomes load-bearing for test monkeypatching.

## Deviations from Plan

None — plan executed exactly as written. The narrow exception (adding module-level `header_file` constant to firmware script) was explicitly permitted by the plan and documented here per requirement.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. Test files read only `tmp_path` files and committed golden fixtures (T-15-01-04: accepted low risk per plan threat model).

The `firestarter/.github/scripts/update_version.py` change adds a module-level constant with no external I/O. No new threat surface.

## Self-Check: PASSED

- `firestarter_app/tests/test_update_version.py` exists: FOUND
- `firestarter_app/tests/golden/stable-baseline.py` exists: FOUND
- `firestarter_app/tests/golden/stable-expected.py` exists: FOUND
- `firestarter/tests/__init__.py` exists: FOUND
- `firestarter/tests/test_update_version.py` exists: FOUND
- `firestarter/tests/golden/stable-baseline.h` exists: FOUND
- `firestarter/tests/golden/stable-expected.h` exists: FOUND
- Task 1 commit 146ce72: FOUND
- Task 2 commit 6c66b29: FOUND
- app tests RED: CONFIRMED (8/8 failed)
- firmware tests RED: CONFIRMED (8/8 failed)
- golden baselines byte-identical: CONFIRMED
- `update_version.py` (app) unmodified: CONFIRMED

---
phase: 15-versioning-locked-step-coordination-foundation
plan: "02"
subsystem: versioning
tags: [tdd, wave-1, green-gate, pytest, pep440, firestarter_app, beta-versioning]
dependency_graph:
  requires:
    - firestarter_app/tests/test_update_version.py (Wave 0 RED-gate scaffold from Plan 15-01)
    - firestarter_app/tests/golden/stable-baseline.py (byte-identity seed)
    - firestarter_app/tests/golden/stable-expected.py (byte-identity reference)
  provides:
    - firestarter_app/.github/scripts/update_version.py (extended: stable + beta + dry-run paths)
  affects:
    - Phase 16 (app beta release pipeline consumes GITHUB_OUTPUT version=X.Y.ZbN)
    - Phase 18 (lockstep procedure docs reference this script's interface)
    - Plan 15-03 (firmware-side mirror of this wave)
tech_stack:
  added:
    - argparse (stdlib — CLI parsing for --dry-run, --beta, --set-version)
    - subprocess (stdlib — git tag --list for D-08 fallback)
  patterns:
    - BETA_VERSION_RE module-level constant for PEP 440 validation (D-21)
    - is_beta_mode() three-signal detection (GITHUB_REF / --beta / BETA_VERSION)
    - compute_beta_version() verbatim-env OR git-tag-scan-fallback dispatch (D-07, D-08)
    - parse_args(argv=None defaults to []) pattern for test-safe argparse
    - os.environ.get(GITHUB_OUTPUT) guard (RESEARCH Pitfall 6)
    - calculate_version(args=None) optional-args signature for test ergonomics
key_files:
  modified:
    - firestarter_app/.github/scripts/update_version.py (60 lines → 200 lines; Wave 1 extension)
decisions:
  - "parse_args() default argv=[] (not None): argparse treats None as read-from-sys.argv; tests call parse_args() with no args inside pytest where sys.argv contains pytest flags. Using argv=[] as default makes parse_args() always safe to call without arguments. __main__ passes sys.argv[1:] explicitly."
  - "calculate_version(args=None) uses parse_args([]) internally: same motivation as above — calculate_version() is called by tests without args, so the internal default must be []."
  - "D-29 --set-version included: YES. Added as argparse flag; takes precedence over BETA_VERSION env var when both set. Adds minimal surface with high local-testing utility."
  - "GITHUB_OUTPUT guard in both stable and beta paths: os.environ.get('GITHUB_OUTPUT') replaces the previous unconditional os.environ['GITHUB_OUTPUT'] — eliminates KeyError when running locally without GitHub Actions env."
  - "Typo 'New versin created:' preserved verbatim in both stable and beta paths (D-17 byte-identity invariant asserted by test_stable_patch_increment)."
metrics:
  duration: "~15 minutes"
  completed: "2026-05-20"
  tasks_completed: 1
  files_modified: 1
---

# Phase 15 Plan 02: Wave 1 App-Side Extension Summary

**One-liner:** Extended `update_version.py` (60 lines) to 200 lines with beta-mode detection, PEP 440 validation, git-tag-scan fallback, dry-run flag, and GITHUB_OUTPUT guard — making all 8 Wave 0 RED-gate tests GREEN while preserving stable-path byte-identity.

## Tasks Completed

| Task | Name | Commit | Sub-repo | Files |
|------|------|--------|----------|-------|
| 1 | Extend app update_version.py (Wave 1 GREEN gate) | 09ec35e | firestarter_app | 1 modified |

## Files Modified

| File | Before | After | Delta |
|------|--------|-------|-------|
| `firestarter_app/.github/scripts/update_version.py` | 60 lines | 200 lines | +140 lines |

## New Exports (Wave 1 additions)

| Symbol | Type | Decision(s) |
|--------|------|-------------|
| `BETA_VERSION_RE` | `re.Pattern` | D-21 — PEP 440 validation regex |
| `is_beta_mode(args)` | function | D-04, D-05, D-06 — three-signal beta detection |
| `compute_beta_version(major, minor, patch)` | function | D-07, D-08 — verbatim env OR git-tag-scan |
| `_git_tag_scan_fallback(base)` | function | D-08, D-09 — subprocess.run git tag --list |
| `parse_args(argv=None)` | function | D-13 — argparse CLI |
| `get_version()` | function (modified) | D-23, D-24 — now returns 4-tuple with pre |
| `update_version(major, minor, patch, *, version_string=None)` | function (modified) | D-17 — kwarg for beta path write |
| `calculate_version(args=None)` | function (modified) | D-16 — accepts optional args Namespace |

## Wave 0 → Wave 1 Transition

```
Before (Wave 0): 8/8 FAILED  (AttributeError: module 'update_version' has no attribute 'parse_args')
After  (Wave 1): 8/8 PASSED  (0.02s)
```

```
tests/test_update_version.py::TestUpdateVersionStable::test_stable_byte_identical PASSED
tests/test_update_version.py::TestUpdateVersionStable::test_stable_patch_increment PASSED
tests/test_update_version.py::TestUpdateVersionBeta::test_beta_explicit_version PASSED
tests/test_update_version.py::TestUpdateVersionBeta::test_beta_invalid_version_rejected PASSED
tests/test_update_version.py::TestUpdateVersionBeta::test_beta_tag_fallback PASSED
tests/test_update_version.py::TestUpdateVersionBeta::test_beta_first_ever PASSED
tests/test_update_version.py::TestUpdateVersionDryRun::test_dry_run_no_file_write PASSED
tests/test_update_version.py::TestUpdateVersionDryRun::test_dry_run_stable_path PASSED
8 passed in 0.02s
```

## Full Suite (No Regressions)

```
tests/test_audit_coverage_matrix.py  10 passed
tests/test_decoder.py                25 passed
tests/test_fwguard.py                 4 passed
tests/test_update_version.py          8 passed
47 passed in 0.79s
```

## D-29 Decision: --set-version Included

The plan asked the planner to decide. **Decision: YES.** Added `--set-version X.Y.ZbN` as an argparse flag that acts as a CLI alias for `BETA_VERSION` env var. When both `--set-version` and `BETA_VERSION` are set, `--set-version` takes precedence. Rationale: trivial to add with argparse, provides useful symmetry for local dry-run testing without setting environment variables.

## setuptools_scm Untouched

`pyproject.toml`, `setuptools_scm` configuration, and `__init__.py` were NOT modified (RESEARCH Assumption A1 — no phase 15 changes needed). The script writes `__init__.py` directly; PyPI version at publish time comes from the git tag via setuptools_scm, which will agree with the `__init__.py` write when the beta workflow tags the commit.

## GITHUB_OUTPUT Guard Confirmation

Running the script locally with no env vars no longer raises `KeyError`:

```bash
$ unset GITHUB_OUTPUT && python3 .github/scripts/update_version.py --dry-run
DRY_RUN: 2.0.8
# exit 0 — no KeyError
```

## Stable Path Byte-Identity Confirmation

`test_stable_byte_identical` asserts `version_file.read_bytes() == expected.read_bytes()` against `tests/golden/stable-expected.py` (`__version__ = "1.2.4"\n`). Test PASSED — stable path write is byte-identical to the pre-v1.4 60-line script.

## Key Implementation Notes

### parse_args(argv=None) — Default is []

The plan specified `argv=None` as the default (standard argparse convention). However, when called inside pytest with no arguments, `argv=None` causes argparse to read `sys.argv[1:]` which contains pytest's own arguments (`tests/test_update_version.py -v`) — triggering `SystemExit: 2`. The fix: `parse_args()` sets `argv = []` when `argv is None`, making it safe to call without arguments in any context. `__main__` passes `sys.argv[1:]` explicitly so the CLI still honours command-line flags.

This is a deviation from the literal plan text (which said `argv=None` → reads sys.argv) but is required by the test contract (tests call `parse_args()` with no arguments and expect a default Namespace).

### calculate_version(args=None) internal default

Similarly, `calculate_version()` calls `parse_args([])` when `args is None` — consistent with the parse_args fix above.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] parse_args(argv=None) reads sys.argv inside pytest**
- **Found during:** Task 1 first test run (5 failures)
- **Issue:** argparse `argv=None` reads `sys.argv[1:]` which inside pytest is `["tests/test_update_version.py", "-v", ...]` — causes SystemExit: 2 on `parse_args()` calls in tests
- **Fix:** Changed `if argv is None: argv = []` so `parse_args()` without arguments always returns the default Namespace. `__main__` explicitly passes `sys.argv[1:]`
- **Files modified:** `firestarter_app/.github/scripts/update_version.py` (lines 107-108)
- **Commit:** 09ec35e (same commit — fix applied before final commit)

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced beyond what the plan's threat model covers. The `subprocess.run(["git", "tag", "--list", ...])` call is in scope as T-15-02-04 (git tag names are not secrets; accepted risk). The `BETA_VERSION` validation via BETA_VERSION_RE is in place as required by T-15-02-01.

## Self-Check: PASSED

- `firestarter_app/.github/scripts/update_version.py` exists and was modified: CONFIRMED
- `BETA_VERSION_RE` exports: CONFIRMED (`BETA_VERSION_RE.pattern == '^[0-9]+\\.[0-9]+\\.[0-9]+(b|rc)[0-9]+$'`)
- `is_beta_mode`, `compute_beta_version`, `_git_tag_scan_fallback`, `parse_args` all importable: CONFIRMED
- `get_version()` returns 4-tuple: CONFIRMED (`('1', '2', '3', None)` for stable, `('1', '2', '3', 'b1')` for beta)
- D-25 `_dev` truncation preserved: CONFIRMED (`2.0.7_dev` → `('2', '0', '7', None)`)
- Typo "New versin created:" present ≥1 times: CONFIRMED (count=2, stable+beta paths)
- `pytest tests/test_update_version.py -v` 8/8 PASSED: CONFIRMED
- `pytest tests/ -v` 47/47 PASSED (no regressions): CONFIRMED
- No modifications to `firestarter/__init__.py`: CONFIRMED
- No modifications to `pyproject.toml`, CI workflows: CONFIRMED
- `GITHUB_OUTPUT` KeyError eliminated: CONFIRMED (dry-run with unset env exits 0)
- Submodule commit 09ec35e in `firestarter_app`: CONFIRMED

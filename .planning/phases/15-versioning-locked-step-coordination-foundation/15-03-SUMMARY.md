---
phase: 15-versioning-locked-step-coordination-foundation
plan: "03"
subsystem: versioning
tags: [tdd, wave-1, green-gate, pytest, pep440, firmware, beta-versioning, ci]
dependency_graph:
  requires:
    - firestarter/tests/test_update_version.py (Wave 0 RED-gate scaffold from Plan 15-01)
    - firestarter/tests/golden/stable-baseline.h (byte-identity seed)
    - firestarter/tests/golden/stable-expected.h (byte-identity reference)
    - firestarter_app/.github/scripts/update_version.py (lockstep reference from Plan 15-02)
  provides:
    - firestarter/.github/scripts/update_version.py (extended: stable + beta + dry-run paths, firmware-specific)
    - firestarter/.github/workflows/build.yml (pytest gate before version bump)
  affects:
    - Phase 17 (firmware beta release pipeline consumes GITHUB_OUTPUT version=X.Y.ZbN)
    - Plan 15-04 (Wave 2 lockstep fixture can now cross-check both scripts via dry-run)
tech_stack:
  added:
    - argparse (stdlib — CLI parsing for --dry-run, --beta, --set-version)
    - subprocess (stdlib — git tag --list for D-08 fallback)
    - pytest (CI gate — pip install pytest in build.yml)
  patterns:
    - BETA_VERSION_RE module-level constant for PEP 440 validation (D-21), byte-identical to app
    - is_beta_mode() three-signal detection (GITHUB_REF / --beta / BETA_VERSION)
    - compute_beta_version() verbatim-env OR git-tag-scan-fallback dispatch (D-07, D-08)
    - parse_args(argv=None defaults to []) pattern for test-safe argparse
    - os.environ.get(GITHUB_OUTPUT) guard (RESEARCH Pitfall 6)
    - calculate_version(args=None) optional-args signature for test ergonomics
    - header_file module-level constant (promoted from local-var shadows)
key_files:
  modified:
    - firestarter/.github/scripts/update_version.py (63 lines -> 203 lines; Wave 1 extension)
    - firestarter/.github/workflows/build.yml (6 lines inserted — 2 new steps)
decisions:
  - "parse_args() default argv=[] (not None): same rationale as Plan 15-02 — argparse None reads sys.argv[1:] which inside pytest contains pytest flags, causing SystemExit:2. Using [] as default makes parse_args() always safe to call without arguments."
  - "calculate_version(args=None) calls parse_args([]) internally: consistent with parse_args fix above."
  - "D-29 --set-version included: YES — mirrors Plan 15-02 decision; added as argparse flag taking precedence over BETA_VERSION env var."
  - "GITHUB_OUTPUT guard in both stable and beta paths: os.environ.get('GITHUB_OUTPUT') replaces unconditional os.environ['GITHUB_OUTPUT'] — eliminates KeyError when running locally."
  - "Typo 'New versin created:' preserved verbatim in both stable and beta paths (D-17 byte-identity invariant)."
  - "header_file local-var shadows removed: Wave 1 promotes the module-level constant to load-bearing; local vars in get_header_version() and update_version() deleted."
  - "pytest step uses 'pytest tests/ -v' (matches plan spec): discovers test_update_version.py via auto-discovery."
metrics:
  duration: "~10 minutes"
  completed: "2026-05-20"
  tasks_completed: 2
  files_modified: 2
---

# Phase 15 Plan 03: Wave 1 Firmware-Side Extension Summary

**One-liner:** Extended firmware `update_version.py` (63 lines) to 203 lines with beta-mode detection, PEP 440 validation (regex byte-identical to app), git-tag-scan fallback, dry-run flag, and GITHUB_OUTPUT guard — turning all 8 Wave 0 RED-gate tests GREEN — and added a pytest CI gate in `build.yml` before the version-bump step.

## Tasks Completed

| Task | Name | Commit | Sub-repo | Files |
|------|------|--------|----------|-------|
| 1 | Extend firmware update_version.py (Wave 1 GREEN gate) | 769c597 | firestarter | 1 modified |
| 2 | Add pytest step to build.yml before PlatformIO build | 2957365 | firestarter | 1 modified |

## Files Modified

| File | Before | After | Delta |
|------|--------|-------|-------|
| `firestarter/.github/scripts/update_version.py` | 63 lines | 203 lines | +140 lines |
| `firestarter/.github/workflows/build.yml` | 103 lines | 109 lines | +6 lines (2 new steps) |

## New Exports (Wave 1 additions)

| Symbol | Type | Decision(s) |
|--------|------|-------------|
| `header_file` | `str` (module constant) | Promoted from local shadow; test monkeypatching target |
| `BETA_VERSION_RE` | `re.Pattern` | D-21 — PEP 440 validation regex, byte-identical to app |
| `is_beta_mode(args)` | function | D-04, D-05, D-06 — three-signal beta detection |
| `compute_beta_version(major, minor, patch)` | function | D-07, D-08 — verbatim env OR git-tag-scan |
| `_git_tag_scan_fallback(base)` | function | D-08, D-09 — subprocess.run git tag --list |
| `parse_args(argv=None)` | function | D-13 — argparse CLI |
| `get_header_version()` | function (modified) | D-23, D-24 — now returns 4-tuple with optional pre-release |
| `update_version(major, minor, patch, *, version_string=None)` | function (modified) | D-17 — kwarg for beta path write |
| `calculate_version(args=None)` | function (modified) | D-16 — accepts optional args Namespace |

## Wave 0 -> Wave 1 Transition

```
Before (Wave 0): 8/8 FAILED  (AttributeError: module 'update_version' has no attribute 'parse_args')
After  (Wave 1): 8/8 PASSED  (0.03s)
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
8 passed in 0.03s
```

## Lockstep Regex Identity (VER-02 / VER-03)

```
diff <(grep -E "^BETA_VERSION_RE" firestarter_app/.github/scripts/update_version.py) \
     <(grep -E "^BETA_VERSION_RE" firestarter/.github/scripts/update_version.py)
# (no output — byte-identical)
```

Both scripts:
```python
BETA_VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$')
```

## build.yml Insertion (Task 2)

Lines inserted between "Run native unit tests" and "Generate release version":

```yaml
      - name: Install pytest for script tests
        run: pip install pytest

      - name: Run update_version.py tests
        run: pytest tests/ -v
```

Final step ordering (by index in jobs.build.steps):

| Index | Step Name |
|-------|-----------|
| 0 | actions/checkout@v4 |
| 1 | actions/cache@v4 |
| 2 | actions/setup-python@v4 |
| 3 | Set up Python 3.11 for codegen |
| 4 | Catalog validity check |
| 5 | Codegen drift gate (messages.h) |
| 6 | Install PlatformIO Core |
| 7 | Run native unit tests |
| **8** | **Install pytest for script tests** (NEW) |
| **9** | **Run update_version.py tests** (NEW) |
| 10 | Generate release version |
| 11 | stefanzweifel/git-auto-commit-action@v5 |
| 12 | Build PlatformIO Project |
| 13 | Release |

No existing step removed or modified: `git diff .github/workflows/build.yml | grep -E '^-[^-]' | wc -l` returns 0.

## GATE-02 Note

The new pytest step adds a mandatory CI check to every push/PR — categorically equivalent to the existing "Catalog validity check", "Codegen drift gate", and "Run native unit tests" gates. Per plan note: if Phase 17 reviewers determine this conflicts with GATE-02 acceptance criteria #4 interpretation, the pytest step can be moved into a separate Python-only workflow (out of scope for Phase 15).

## Stable Path Byte-Identity Confirmation

`test_stable_byte_identical` asserts `version_file.read_bytes() == expected.read_bytes()` against `tests/golden/stable-expected.h` (`#define VERSION "1.2.4"\n`). Test PASSED — stable path write is byte-identical.

## D-25 (-dev suffix) Preservation

`get_header_version()` uses named-group regex with optional `(?P<pre>...)` group. For `3.0.0-dev`, the `-dev` prefix does not match `(b|rc)[0-9]+`, so `pre` group returns `None` — behavior preserved per D-25.

## GITHUB_OUTPUT Guard Confirmation

`os.environ.get("GITHUB_OUTPUT")` used in both stable and beta paths. Running locally without GITHUB_OUTPUT set exits 0 (no KeyError).

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written. The `argv=[]` default for `parse_args()` was pre-anticipated by the plan (based on Plan 15-02 SUMMARY deviation notes) and implemented correctly from the start.

### Notes

- Wave 0 had already added `header_file = "include/version.h"` as a module-level constant with shadowing local variables. Wave 1 removed both shadowing local vars (inside `get_header_version()` and `update_version()`) making the module constant load-bearing.
- `include/version.h` was found modified in the working tree (from `3.0.0-dev` to `3.0.2`) before this plan ran — restored to committed state before staging Task 1 commit. The modification was from a previous test run during Wave 0 development.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced beyond what the plan's threat model covers. The `subprocess.run(["git", "tag", "--list", ...])` call is in scope as T-15-03-04 equivalent. The `BETA_VERSION` validation via `BETA_VERSION_RE` is in place as required by T-15-03-01.

## Self-Check: PASSED

- `firestarter/.github/scripts/update_version.py` exists and was modified: CONFIRMED (63 -> 203 lines)
- `BETA_VERSION_RE` exports with correct pattern: CONFIRMED
- `is_beta_mode`, `compute_beta_version`, `_git_tag_scan_fallback`, `parse_args` all importable: CONFIRMED
- `get_header_version()` returns 4-tuple: CONFIRMED (named groups major/minor/patch/pre)
- D-25 `_dev` truncation preserved: CONFIRMED (pre group = None for non-bN/rcN suffixes)
- Typo "New versin created:" present >=1 times: CONFIRMED (count=2, stable+beta paths)
- `pytest tests/test_update_version.py -v` 8/8 PASSED: CONFIRMED
- `firestarter/include/version.h` NOT modified by this plan: CONFIRMED (restored + not staged)
- Lockstep regex byte-identity: CONFIRMED (diff returns empty)
- `build.yml` YAML valid: CONFIRMED (yaml.safe_load succeeds)
- Step ordering: Set up Python 3.11 (3) < pytest install (8) < pytest run (9) < Generate release version (10): CONFIRMED
- No existing build.yml lines deleted: CONFIRMED (0 deletion lines in diff)
- Submodule commits 769c597 and 2957365 in `firestarter`: CONFIRMED

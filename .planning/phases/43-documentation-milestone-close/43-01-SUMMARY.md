---
phase: 43-documentation-milestone-close
plan: 01
subsystem: documentation
tags: [milestone-close, documentation, v1.8, gate-failure, coverage, abort]

# Dependency graph
requires:
  - phase: 42-error-handling-normalization-quality-sweep
    provides: "Phase 42 tip commit 9999bdb — mypy strict on 8 modules + coverage ≥70% floor enforced"
provides:
  - "GATE-1.8 pre-flight result: FAILED (coverage 69.49% < 70% floor)"
  - "Re-open recommendation: Phase 42 Plan 42-03 must re-verify and restore coverage to ≥70%"
affects: [43-02-PLAN, 43-03-PLAN]

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified: []

key-decisions:
  - "GATE-1.8 coverage assert (assert f) exits non-zero (exit=1): pytest --cov-fail-under=70 reports 69.49% at commit 9999bdb — plan ABORTED per D-08 policy"
  - "No files written per the abort mandate — Tasks 2 + 3 did NOT execute"

patterns-established: []

requirements-completed: []

# Metrics
duration: 8min
completed: 2026-05-29
---

# Phase 43 Plan 01: v1.8 Documentation Substrate — ABORTED (GATE-1.8 Failure)

**GATE-1.8 coverage assert failed: pytest --cov=firestarter --cov-fail-under=70 exits 1 with 69.49% total coverage at commit 9999bdb (Phase 42 tip) — plan aborted before any file write per D-08 policy.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-05-29
- **Completed:** 2026-05-29 (aborted at Task 1)
- **Tasks completed:** 0 of 3 (Task 1 is pre-flight only — exits non-zero, plan aborts)
- **Files modified:** 0 (no writes permitted after gate failure per D-08)

## Accomplishments

None. Plan aborted at Task 1 pre-flight gate. No files were written.

## GATE-1.8 Pre-Flight Results

Six software-floor asserts run serially. Results:

| Assert | Command | Exit | Result |
|--------|---------|------|--------|
| GATE-1.8e entry-point smoke | `pip install -e '.[test]' && firestarter --help` | 0 | PASS — `Usage: firestarter` + 14 commands rendered |
| GATE-1.8a/b/c/e test suite | `python -m pytest -q` | 0 | PASS — 365 passed, 0 xfail, 29 syrupy snapshots green |
| GATE-1.8 lint (ruff) | `python -m ruff check firestarter/ tests/` | 0 | PASS — "All checks passed!" |
| GATE-1.8 format (ruff format) | `python -m ruff format --check firestarter/ tests/` | 0 | PASS — "50 files already formatted" |
| GATE-1.8 mypy 8-module strict | `python -m mypy <8-module-list>` | 0 | PASS — "Success: no issues found in 8 source files" |
| **GATE-1.8 coverage floor** | **`python -m pytest --cov=firestarter --cov-fail-under=70 -q`** | **1** | **FAIL — 69.49% < 70% floor** |

**Failing assert (f) output:**

```
ERROR: Coverage failure: total of 69 is less than fail-under=70
TOTAL                              2711    827    69%
FAIL Required test coverage of 70% not reached. Total coverage: 69.49%
365 passed in 13.29s
```

## Root Cause Analysis

Phase 42 Plan 42-03 (commit `9999bdb`, merged 2026-05-28) recorded coverage at **70.12%** at the time of commit. The current measurement at the **same commit** reads **69.49%**. The code and tests are byte-identical — no changes have been made to `firestarter/` or `tests/` since `9999bdb`. The discrepancy (−0.63%) is likely attributable to:

1. **Non-deterministic branch coverage**: Python's `coverage.py` may measure conditional branches differently across runs depending on import order, garbage-collector timing, or `__pycache__` state.
2. **Python 3.12.13 environment**: The current environment reports `pyproject.toml: [mypy]: python_version: Python 3.9 is not supported (must be 3.10 or higher)` — this indicates the pyproject.toml `python_version = "3.9"` config key is being evaluated under a different Python version than the original measurement.
3. **Coverage of `.pyc` files vs. source**: If `__pycache__` was stale or absent during the original measurement, re-bytecoding could shift branch counts.

Per D-08 policy (threat model T-43-07): the pre-flight exits non-zero → plan ABORTS. "It does NOT degrade to a 'ship anyway with caveat'."

## Re-Open Recommendation

**Phase 42 must re-open** (specifically Plan 42-03) to restore coverage to ≥70.0% reliably.

Suggested investigation:
1. Run `python -m pytest --cov=firestarter -q 2>&1 | grep TOTAL` several times to characterize variance. If measurement is non-deterministic across clean runs at the same commit, the 70% floor needs a 0.5–1.0% margin above the floor.
2. Identify the 0.63% shortfall: current measurement is 2711 statements, 827 missed = 69.49%. At 70%, maximum missed statements = floor(2711 × 0.30) = 813. Currently 14 too many missed statements.
3. Add targeted tests to bring coverage reliably above 70.5% to handle measurement variance. The lowest-coverage modules per current run: `eprom_info.py` (30%), `ic_layout.py` (30%), `hardware.py` (47%) — any of these provides easy wins.
4. After confirmed ≥70% on 3 consecutive fresh runs, re-run Phase 43 Plan 43-01.

**Operator action:** Run `/gsd-execute-phase 42 --plan 03 --coverage-fix` or open Phase 42 Plan 42-03 for a targeted coverage top-up commit on `firestarter_app@v1.8-app-cleanup`.

## Task Commits

No task commits — plan aborted before any commit.

## Files Created/Modified

None.

## Decisions Made

- GATE-1.8 assert (f) coverage floor exits 1 → plan ABORTED per D-08 policy.
- No files were written (Tasks 2 + 3 skipped per Task 1 abort mandate).
- Re-open Phase 42 Plan 42-03 is the recommended resolution path.

## Deviations from Plan

None — the abort path is the plan-specified behavior on gate failure. No auto-fixes attempted (D-08 policy: abort, do not degrade to "ship anyway").

## Issues Encountered

GATE-1.8 coverage floor failure at commit `9999bdb`: measured 69.49% vs. 70.12% recorded in Phase 42-03 SUMMARY at the same commit. Root cause is measurement variance (non-deterministic branch coverage) at the 70% boundary. The 70% floor was set empirically with a 0.12% margin at Phase 42 commit time; that margin has evaporated under the current measurement environment.

## Placeholder Map (for Plan 43-03 Step 5)

Not applicable — plan aborted; no `<TBD-from-43-03>` tokens were written.

## Next Phase Readiness

Blocked. Phase 43 Plans 43-01, 43-02, and 43-03 cannot proceed until:
1. Phase 42 Plan 42-03 is re-opened and coverage is restored to ≥70% reliably (exit 0 on `pytest --cov-fail-under=70`).
2. Phase 43 Plan 43-01 is re-run from Task 1 (full pre-flight gate must pass before file writes).

## Self-Check: N/A (Abort)

No files were written; no commits were made. Self-check not applicable for abort-path SUMMARY.

---
*Phase: 43-documentation-milestone-close*
*Completed: 2026-05-29 (ABORTED — GATE-1.8 coverage failure)*

---
phase: 11-coverage-matrix-db-inconsistency-audit
plan: 01
subsystem: testing

tags: [pytest, tdd, wave-0, scaffold, coverage-matrix, eprom-database]

# Dependency graph
requires:
  - phase: 11 (planning)
    provides: VALIDATION.md per-task verification map; PATTERNS.md test_fwguard precedent; RESEARCH.md idempotence recipe + Validation Architecture
provides:
  - "10 collectible-but-failing pytest functions for the audit_coverage_matrix tool (the Wave 0 Nyquist gate)"
  - "Deferred-import pattern that lets the test file collect before the production tool exists"
  - "Hermetic FIRESTARTER_DB_FILE env-var isolation via autouse fixture (mirrors test_fwguard.py)"
affects:
  - 11-02..11-04 (Waves 1-4 — each later plan's <verify> command now resolves to a concrete pytest test that fails meaningfully today)
  - 11-05 (D-07 doc reconciliation — picks up live numbers from §1 once Wave 1 implements summary stats)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Deferred-import test scaffolding — `from X import` inside function body so pytest collects file before module exists"
    - "Class-based test container with autouse env-isolation fixture"
    - "RED-gate-per-wave — NotImplementedError stubs reference owning wave + decision IDs in docstring"

key-files:
  created:
    - firestarter_app/tests/test_audit_coverage_matrix.py
  modified: []

key-decisions:
  - "Use NotImplementedError raised after deferred import (not pytest.fail) — gives a single failure shape across all 10 tests; ModuleNotFoundError today, then NotImplementedError once each wave creates the tool module."
  - "Class-based organisation (TestAuditCoverageMatrix) chosen over module-level functions to mirror test_fwguard.py:31-42 — class boundary is the natural scope for the autouse _isolate_env fixture."
  - "Each docstring quotes BOTH the requirement IDs (COV-01/COV-02/SC-03) AND the decision IDs (D-02/D-03/D-06/D-07/D-09/D-10/D-11/D-12/D-13/D-15) the test enforces — so a future reader can trace test → contract → CONTEXT.md without re-reading the plan."

patterns-established:
  - "Wave 0 RED-gate scaffold: each stub's docstring names its owning wave + the decision IDs it enforces; body raises NotImplementedError after a deferred import. Reusable for any later phase that needs a Nyquist gate before production code lands."
  - "Hermetic env-var isolation via @pytest.fixture(autouse=True) on a class — monkeypatch.delenv at the class level, per-test monkeypatch.setenv overrides for the test that needs the env var set."

requirements-completed: []

# Metrics
duration: 12min
completed: 2026-05-19
---

# Phase 11 Plan 01: Coverage Matrix — Wave 0 Failing-Test Scaffold

**10 collectible-but-failing pytest stubs for the audit_coverage_matrix tool, organised in a class-based TestAuditCoverageMatrix container with deferred imports so pytest discovers the file before the production tool exists.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-05-19 (sequential executor spawn)
- **Completed:** 2026-05-19
- **Tasks:** 1 (single-task plan)
- **Files modified:** 1 (new)

## Accomplishments

- Wave 0 Nyquist gate satisfied — `pytest tests/test_audit_coverage_matrix.py --collect-only` discovers exactly 10 tests, none silently skipped, all failing with `ModuleNotFoundError` today.
- Every later wave's `<automated>` verify command from VALIDATION.md "Per-Task Verification Map" now resolves to a real test ID (waves 1-4 can each implement their slice without re-collecting the file).
- Test names exactly match the VALIDATION.md contract (`test_enumeration_row_count`, `test_enumeration_sort`, `test_idempotence`, `test_hazard_cluster_42_rows`, `test_ledger_idempotent`, `test_ledger_id_reuse`, `test_summary_stats`, `test_exit_codes`, `test_bench_coverage_proof`, `test_golden_file_matches`).
- Class-based + autouse-fixture organisation mirrors `test_fwguard.py:31-42` (PATTERNS.md analog) — no new test infrastructure introduced.

## Task Commits

Task committed atomically inside the `firestarter_app/` submodule:

1. **Task 1: Create failing-test scaffold for the audit_coverage_matrix tool** — `firestarter_app@b03bc9b` (test)

**Plan metadata commit** (parent repo, this SUMMARY + STATE + ROADMAP updates) — see final commit on `refactor/v1.3-foundations`.

## Files Created/Modified

- `firestarter_app/tests/test_audit_coverage_matrix.py` (new, 282 lines) — single `TestAuditCoverageMatrix` class with autouse `_isolate_env` fixture and 10 `def test_*` methods. Each method body defers `from tools.audit_coverage_matrix import generate_matrix` so collection succeeds, then raises `NotImplementedError("Wave N — see VALIDATION.md row ...")`. Docstrings quote the requirement + decision IDs each test will eventually enforce. Module header enumerates the wave-to-test mapping.

## Decisions Made

1. **NotImplementedError after deferred import (not pytest.fail).** Picked the cleaner failure shape — `ModuleNotFoundError` today (the deferred import line), `NotImplementedError` once each wave creates the module. Single failure-mode story for Wave 0 → Wave N transitions.
2. **Class-based, not module-level functions.** Mirrors `test_fwguard.py` exactly; the class boundary is the natural scope for the autouse env-isolation fixture that needs to apply to every test in the file.
3. **Each test's docstring names the requirement IDs (COV-01/COV-02/SC-03) AND the decision IDs (D-02/D-03/D-06/D-07/D-09/D-10/D-11/D-12/D-13/D-15) it enforces.** Makes the trace test → contract → CONTEXT.md walkable without re-reading PLAN.md.

## Deviations from Plan

None — plan executed exactly as written. The single task's <action> spec, <verify> command, and 8 <acceptance_criteria> checks all matched 1:1 with the implementation.

## Issues Encountered

None. Pytest 9.0.3 already installed (no test-framework setup required). The existing `conftest.py` does not interfere with stand-alone tool tests as PATTERNS.md predicted — the new file collects cleanly alongside the existing 29 tests (39 total now).

## Verification Output

```
$ cd firestarter_app && pytest tests/test_audit_coverage_matrix.py --collect-only -q
tests/test_audit_coverage_matrix.py: 10

$ cd firestarter_app && grep -c "^    def test_" tests/test_audit_coverage_matrix.py
10

$ cd firestarter_app && grep -E "def test_(enumeration_row_count|enumeration_sort|idempotence|hazard_cluster_42_rows|ledger_idempotent|ledger_id_reuse|summary_stats|exit_codes|bench_coverage_proof|golden_file_matches)" tests/test_audit_coverage_matrix.py | wc -l
10

$ cd firestarter_app && grep -c "pytest.mark.skip" tests/test_audit_coverage_matrix.py
0

$ cd firestarter_app && pytest tests/test_audit_coverage_matrix.py -x  # exits 1, fails meaningfully
$ cd firestarter_app && pytest tests/ --collect-only  # exits 0, 39 tests collected (29 existing + 10 new)
```

All 8 acceptance criteria from the plan satisfied.

## User Setup Required

None — no external service configuration required. Pytest 9.0.3 already in the host sub-repo.

## Next Phase Readiness

- Wave 1 (`test_summary_stats` + `test_exit_codes`) can start immediately. Wave 1 will create `firestarter_app/tools/audit_coverage_matrix.py` with the `generate_matrix(output, ledger_path) -> int` surface declared in this plan's `<interfaces>` block. As soon as that file exists, the 10 stubs will switch from `ModuleNotFoundError` to `NotImplementedError` — Wave N then implements its slice by replacing the `raise NotImplementedError(...)` with real test logic.
- No blockers. No carry-over.

## Self-Check: PASSED

- ✓ File exists: `/workspaces/firestarter_app/tests/test_audit_coverage_matrix.py` (282 lines)
- ✓ Submodule commit exists: `firestarter_app@b03bc9b` — verified via `cd firestarter_app && git log --oneline -1`
- ✓ Collect-only count: 10 tests (matches plan acceptance criterion exactly)
- ✓ All 10 canonical test names present
- ✓ Zero `pytest.mark.skip` decorators
- ✓ Zero module-top `from tools.audit_coverage_matrix` imports (deferred to function bodies)
- ✓ Full suite still collects: 39 tests, 0 errors

## TDD Gate Compliance

Plan type is `execute` (not `tdd`), but the plan itself IS the RED gate of the Wave 0 → Wave 1+ promotion enforced by VALIDATION.md. The single `test(11-01): ...` commit IS the RED gate; subsequent `feat(11-NN): ...` commits in Waves 1-4 will be the GREEN gates. The conventional RED → GREEN → REFACTOR cycle is distributed across plans rather than within this plan.

---
*Phase: 11-coverage-matrix-db-inconsistency-audit*
*Plan: 01*
*Completed: 2026-05-19*

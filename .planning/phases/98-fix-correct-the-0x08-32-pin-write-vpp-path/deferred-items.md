# Deferred Items — Phase 98 Plan 03

## Out-of-scope pre-existing test failure

- **Test:** `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches`
- **Found during:** Plan 98-03 Task 3 (full `pytest -q` run, run as a scope-boundary
  sanity check beyond the plan's required verification commands).
- **Symptom:** Regenerated coverage matrix (186034 bytes) drifts from the golden
  fixture (184631 bytes) at byte index 1178.
- **Confirmed pre-existing:** Reproduces identically at commit `27da013` (the tip
  BEFORE this plan's two commits `3659121`/`9e3d17e`). Neither commit touches
  `tests/test_audit_coverage_matrix.py` or any file that feeds the audit coverage
  matrix generator — `git diff 27da013 HEAD --stat -- tests/test_audit_coverage_matrix.py`
  shows no delta.
- **Disposition:** Out of scope per the executor scope-boundary rule (only
  auto-fix issues directly caused by the current task's changes). Not fixed.
  Logged here per protocol; not blocking 98-03's success criteria (the plan's
  own verification commands — ruff/diff_db/check_dispatch/parity — all pass).

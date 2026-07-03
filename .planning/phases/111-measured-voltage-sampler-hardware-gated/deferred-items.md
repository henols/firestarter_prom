# Deferred Items — Phase 111

## 111-01: Pre-existing ruff F841 unmasked in test_diagnostic_report.py (out of scope)

- **File:** `firestarter_app/tests/test_diagnostic_report.py:519`
- **Line:** `table = report.render()  # must not raise` (inside the pre-existing `test_full_report_all_four_sub_objects_single_source`)
- **Issue:** `ruff check` now flags this as F841 (unused local variable). It appears ruff does not flag an assigned-but-unused variable when it is the very last statement in the module; Plan 01's addition of `test_voltage_split_fields_serialize` after it in the same file exposed the pre-existing issue.
- **Why deferred:** This line is untouched by Plan 01's diff (`git diff` confirms only additions after it), and Plan 01 explicitly prohibits modifying any existing test body (SC3-equivalent constraint). Fixing it is out of this plan's scope per the scope-boundary rule (only auto-fix issues directly caused by this plan's changes).
- **Suggested fix (future plan):** Either remove the `table =` assignment (replace with a bare `report.render()  # must not raise` call) or add an assertion using `table`, in whichever future plan next touches `test_diagnostic_report.py`.

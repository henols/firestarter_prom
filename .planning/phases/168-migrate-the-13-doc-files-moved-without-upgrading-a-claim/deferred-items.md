# Phase 168 — Deferred Items

Out-of-scope discoveries logged during execution, not fixed per the executor's
scope-boundary discipline (fix only what the current task's changes directly
caused to break).

## Plan 168-04, Task 1 — two orphaned C++ fixture files

Deleting `firestarter_app/tests/test_dispatch_mirror.py` (its sole consumer)
leaves two committed fixture files unreferenced by any Python code in the
repository:

- `firestarter_app/tests/fixtures/planted_dispatch_missing_hex.cpp`
- `firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp`

Both were SWEEP-07 planted-violation controls consumed exclusively by
`test_dispatch_mirror.py`'s `test_planted_missing_hex_is_detected` and
`test_planted_comment_only_hex_is_NOT_detected`. No test currently fails as a
result of their being orphaned (nothing scans `tests/fixtures/` for unused
files), so this is tidiness, not a defect: leaving them does not violate any
of plan 168-04's acceptance criteria, and 168-04's `files_modified` does not
name them.

Recommended follow-up: delete both files in whichever later 168 plan next
touches `tests/fixtures/` (e.g. a plan doing broader test-tree cleanup), or
in a dedicated hygiene pass after the phase closes.

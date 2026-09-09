## Deferred Items

- `tests/test_blast_radius_invariance.py:565` fails `ruff format --check` (a
  wrapped multi-line expression the formatter would reshape differently).
  status: open
  **What:** Pre-existing at app HEAD `ddc0c1c` (confirmed against the pristine
  commit, before plan 181-05's own edits, which are ~380 lines away at
  `:147-160`/`:477-485`). Not caused by this plan's task, and its own module
  reformats cleanly except for this one pre-existing block. Out of scope per
  the Scope Boundary rule -- logged here rather than fixed.

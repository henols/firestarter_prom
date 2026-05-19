---
phase: 11-coverage-matrix-db-inconsistency-audit
plan: 03
subsystem: testing
tags: [python, pytest, codegen, idempotence, markdown-rendering, audit-tool, chip-database]

# Dependency graph
requires:
  - phase: 11
    provides: "Wave 1 tool skeleton + §1/§2 emit (11-02), Wave 0 failing-test scaffolding (11-01)"
provides:
  - "§3 Full Enumeration emit — 339 in-scope rows (212 algo-0x07 + 127 algo-0x08) across two per-algorithm sub-tables"
  - "Pattern F sort_key(mfg, chip) helper — D-06 5-tuple for deterministic enumeration order"
  - "Three Wave-2 tests green: test_enumeration_row_count, test_enumeration_sort, test_idempotence"
  - "Byte-identical re-run contract validated end-to-end"
affects:
  - "11-04 (Wave 3 — defect findings + ledger): consumes §3 row iteration to mint DEFECT-COV-NN"
  - "11-05 (Wave 4 — bench coverage proof): consumes §3 row iteration for per-axis coverage tables"
  - "11-06 (Wave 5 — planning-doc reconciliation): runs against the final matrix; this plan locks in the row-count anchor (339)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pattern F (D-06 sort key): (algorithm, pinout, size_bytes, manufacturer, first_alias)"
    - "Per-algorithm sub-table split (CONTEXT.md Claude's Discretion + PATTERNS.md Multi-table-stacked layout)"
    - "Defensive pipe-escape in md_table cells (forward-compat for variant strings)"

key-files:
  created:
    - ".planning/phases/11-coverage-matrix-db-inconsistency-audit/11-03-SUMMARY.md"
  modified:
    - "firestarter_app/tools/audit_coverage_matrix.py — added sort_key + emit_full_enumeration; wired into generate_matrix"
    - "firestarter_app/tests/test_audit_coverage_matrix.py — three Wave-2 tests fleshed out"
    - ".planning/v1.3-COVERAGE-MATRIX.md — §3 now populated (339 rows in two per-algorithm sub-tables)"

key-decisions:
  - "chip_id_value renders verbatim (all values are strings in live DB — `\"0x00000108\"` etc.); no int-vs-string branching needed"
  - "chip_id_check renders as Python str(bool) — `True` / `False` (mirrors PROJECT.md decision-table convention)"
  - "Defensive pipe-escape on every cell (md_escape helper) even though no DB row is known to contain `|` — robustness over micro-optimization"
  - "Algorithm intentionally omitted from sort-comparison key in test_enumeration_sort (it's implicit per sub-table; comparing 4-tuple suffices)"
  - "emit_placeholder_sections() now returns 2 strings (§4 + §5) instead of 3 — §3 is real; dropped the `s3` slot"

patterns-established:
  - "Pattern F implementation: split per-algorithm BEFORE sorting (filter → sort → render) — keeps each sub-table self-contained for test slicing"
  - "Row-count regression anchor (339) lives in three places: tool (live-computed), §2 reconciliation (live), test_enumeration_row_count (asserted via parsed body). Drift in any one trips the test."

requirements-completed: [COV-01]

# Metrics
duration: 18min
completed: 2026-05-19
---

# Phase 11 Plan 03: Coverage Matrix §3 Full Enumeration Summary

**Wave-2 §3 emit lands: 339 in-scope rows enumerated across two per-algorithm sub-tables (algo-0x07: 212, algo-0x08: 127) in Pattern F sort order, with byte-identical re-run contract validated end-to-end.**

## Performance

- **Duration:** ~18 min
- **Started:** 2026-05-19T21:57:00Z
- **Completed:** 2026-05-19T22:15:00Z
- **Tasks:** 3
- **Files modified:** 3 (1 tool, 1 test, 1 generated matrix)

## Accomplishments

- §3 Full Enumeration emit added to `audit_coverage_matrix.py` — two per-algorithm sub-tables, 9 columns each per D-06, 339 total rows in Pattern F sort order.
- Three Wave-2 tests fleshed out (`test_enumeration_row_count`, `test_enumeration_sort`, `test_idempotence`) — all green.
- `.planning/v1.3-COVERAGE-MATRIX.md` regenerated with §3 populated — Wave-2 snapshot ready for Wave-3 augmentation.
- Wave 1 regression tests (`test_summary_stats`, `test_exit_codes`) still green — no §1/§2 churn.
- Byte-identical idempotence preserved across the full matrix (verified via `diff` on two consecutive runs at the file level).

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Pattern F sort_key + emit_full_enumeration to the tool** — `firestarter_app@a445bd5` (feat)
2. **Task 2: Implement test_enumeration_row_count, test_enumeration_sort, test_idempotence** — `firestarter_app@9c39cf6` (test)
3. **Task 3: Commit the regenerated matrix to .planning/v1.3-COVERAGE-MATRIX.md** — `74cf6c5` (docs, parent repo)

## Files Created/Modified

- `firestarter_app/tools/audit_coverage_matrix.py` — added `sort_key(mfg, chip)` (Pattern F 5-tuple), `_md_escape`, `_enum_row`, `emit_full_enumeration(rows)`, `_ENUM_HEADERS` constant; wired `emit_full_enumeration` into `generate_matrix`; `emit_placeholder_sections` now returns `(s4, s5)` instead of `(s3, s4, s5)`.
- `firestarter_app/tests/test_audit_coverage_matrix.py` — three Wave-2 test bodies replace `NotImplementedError` stubs; total file now has 5 passing + 5 failing (Wave 3 + Wave 4 stubs are expected red).
- `.planning/v1.3-COVERAGE-MATRIX.md` — regenerated; §3 now contains 339 enumerated rows; §4 + §5 remain placeholder until Waves 3-4.

## Decisions Made

- **chip_id_value rendering — verbatim string passthrough.** Pre-implementation DB inspection confirmed every algo-0x07 + algo-0x08 row's `chip_id_value` is a Python string (e.g. `"0x00000108"`, `"0x00000000"`). The plan's `<action>` allowed conditional int-vs-string rendering; the live data made this unnecessary. One consistent path.
- **chip_id_check rendering — `str(bool)`.** Renders `"True"` / `"False"` per Python convention. Plan-specified.
- **Algorithm omitted from `test_enumeration_sort` comparison key.** Pattern F's full 5-tuple is `(algorithm, pinout, size_bytes, manufacturer, first_alias)` but the algorithm column is implicit per sub-table (one sub-table = one algorithm value). Comparing only `(pinout, size_bytes, manufacturer, first_alias)` is sufficient and clearer. The full key is what `sort_key()` returns at the tool level; the test asserts the per-sub-table projection.
- **Defensive markdown escape.** Added `_md_escape` (replaces `|` with `\|`) and applied it to every cell. No DB row is known to contain `|`, but the renderer should be robust against future DB updates; the cost is one function call per cell.

## Deviations from Plan

None - plan executed exactly as written. Acceptance criteria all met:

- `def sort_key(` present in tool (1 occurrence).
- `def emit_full_enumeration(` present in tool (1 occurrence).
- `part_number.*split` present in sort_key (1 occurrence).
- Tool runs clean: `python tools/audit_coverage_matrix.py --output /tmp/m3.md --ledger /tmp/l3.json` → exit 0.
- §3 header present (1 occurrence: `## §3: Full Enumeration`).
- Both per-algorithm sub-tables present (2 occurrences: `### algo-0x07`, `### algo-0x08`).
- 339 data rows in §3 (counted via Python list comprehension).
- Byte-identical re-run: `diff /tmp/m3.md /tmp/m4.md` empty.
- 9-column header present in both sub-tables.
- Wave 1 tests still green (no §1/§2 regression).
- `test_enumeration_row_count`, `test_enumeration_sort`, `test_idempotence` all green.
- `test_summary_stats`, `test_exit_codes` still green.
- Committed matrix file byte-identical to a fresh tool run.

## Issues Encountered

None. The Wave 1 tool skeleton (Plan 11-02) had clean extension points — the new `emit_full_enumeration` slotted into `generate_matrix` by simple replacement of the §3 placeholder, with `emit_placeholder_sections` reduced from returning 3 strings to 2.

## User Setup Required

None — no external service configuration required. The tool is desk-side (operates only on `chip_database.json`); the regenerated matrix is committed.

## Next Phase Readiness

- §3 is the audit substrate — every later wave reads from it.
- Plan 11-04 (Wave 3) can now iterate `rows` to mint `DEFECT-COV-NN` entries against the ledger. The Pattern F sort order is locked, so any defect-finding signature derived from `(pinout, algorithm, etype)` or richer tuples will be stable across re-runs.
- Plan 11-05 (Wave 4) can consume §3 row data to populate the three per-axis coverage tables (D-09 / D-10 / D-11).
- The 339-row regression anchor is locked in three places (tool body, §2 reconciliation, `test_enumeration_row_count`); a future DB regen that shifts the count will trip the test immediately — update all three together.

## Self-Check: PASSED

- `firestarter_app/tools/audit_coverage_matrix.py` exists with `def sort_key(` and `def emit_full_enumeration(` — FOUND.
- `firestarter_app/tests/test_audit_coverage_matrix.py` updated, 5 tests pass — FOUND.
- `.planning/v1.3-COVERAGE-MATRIX.md` regenerated with 339 §3 rows — FOUND.
- `firestarter_app@a445bd5` (Task 1) — FOUND.
- `firestarter_app@9c39cf6` (Task 2) — FOUND.
- `74cf6c5` (Task 3, parent) — FOUND.

---
*Phase: 11-coverage-matrix-db-inconsistency-audit*
*Completed: 2026-05-19*

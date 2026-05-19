---
phase: 11-coverage-matrix-db-inconsistency-audit
plan: 05
subsystem: testing
tags: [python, pytest, audit-tool, bench-coverage, golden-file, codegen, idempotence, markdown-rendering, chip-database, milestone-receipt]

# Dependency graph
requires:
  - phase: 11
    provides: "Wave 3 §4 emit + DEFECT-COV-NN ledger (11-04); Wave 2 §3 enumeration + sort_key (11-03); Wave 1 tool skeleton (11-02)"
provides:
  - "§5 BENCH Coverage Proof emit — three per-axis coverage tables (pinout-class, pulse-duration bucket, size bucket per D-09) + Known Gaps subsection (D-10) + milestone-claim closing prose"
  - "BENCH_CHIP_MAP constant encoding the six bench chips verbatim from REQUIREMENTS.md §BENCH lines 14-19; BENCH-05 / BENCH-06 carry selection_pending=True per D-11"
  - "pinout_coverage / pulse_coverage / size_coverage / emit_bench_coverage public surface for §5 emit + per-axis tests"
  - "firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md greenfield fixture — byte-identical snapshot of the operator-approved matrix output for regression pinning"
  - "Two Wave-4 tests green: test_bench_coverage_proof (§5 structural assertions) + test_golden_file_matches (end-to-end byte-identity vs golden fixture)"
  - "All 10 audit-coverage-matrix tests green (10/10 pass; no NotImplementedError stubs remain)"
affects:
  - "Phase 11 close: §1+§2+§3+§4+§5 all populated; matrix is operator-ready for the milestone-receipt role described in CONTEXT.md <specifics>"
  - "Plan 11-06 (Wave 5 — planning-doc reconciliation): consumes the final 339 / 734 / 212 counts that §1+§2 already render; nothing in §5 affects its scope"
  - "Phase 14 milestone close: §5 is the load-bearing receipt for the BENCH-RESULTS claim — six BENCH chips represent N=339 in-scope DB rows on the three axes that matter"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Greenfield golden-file fixture pattern (RESEARCH.md §'Golden-file pattern (recommended)' lines 788-799) — tests/golden/<artifact>.md as byte-identical regression anchor"
    - "Pattern D markdown-table emit reused for five §5 sub-tables (one pinout-coverage + two per-algorithm pulse-coverage + two per-algorithm size-coverage)"
    - "Hash-based finding cross-reference: signature[0] (HAZARD list-of-pinouts) or signature[1] (CORRECTNESS / VARIANCE pinout) drives the §5 uncovered-cell DEFECT-COV-NN lookup via ledger"
    - "BENCH chip-to-row matching by membership test against the comma-joined part_number variant list (handles BENCH-06 W27C010 sharing a row with W27E010 / W27L010)"

key-files:
  created:
    - ".planning/phases/11-coverage-matrix-db-inconsistency-audit/11-05-SUMMARY.md"
    - "firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md"
  modified:
    - "firestarter_app/tools/audit_coverage_matrix.py — +419 lines: BENCH_CHIP_MAP constant; _bench_chip_label, _bench_covered_label, _bench_row_for_chip helpers; pinout_coverage, _bench_pulse_bucket, pulse_coverage, size_coverage, _findings_for_pinout helpers; emit_bench_coverage; rewired into generate_matrix as s5 with rows + findings + ledger args; emit_placeholder_sections removed (§5 is no longer a stub)"
    - "firestarter_app/tests/test_audit_coverage_matrix.py — +95 lines: test_bench_coverage_proof body (structural assertions on §5: three subsections + Known Gaps + 6 BENCH IDs + milestone-claim prose); test_golden_file_matches body (anchor paths from __file__.parents, seed tmp ledger from .planning/v1.3-defect-coverage-ids.json, byte-identity assertion vs golden fixture)"
    - ".planning/v1.3-COVERAGE-MATRIX.md — §5 BENCH Coverage Proof now populated end-to-end (was Wave-1 stub); five sub-tables (pinout / pulse-0x07 / pulse-0x08 / size-0x07 / size-0x08) + Known Gaps + milestone-claim prose"

key-decisions:
  - "Compute order in generate_matrix is s1 → s2 → s3 → s4 → s5 so emit_defects (s4) mints all DEFECT-COV-NN IDs into the ledger BEFORE emit_bench_coverage (s5) reads them for uncovered-cell cross-references. Re-ordering would require either a two-pass ID mint or a deferred-render trampoline; the linear order is simpler."
  - "Pulse-coverage cross-references are filtered by part_number membership in the bucket's row set — initial implementation matched 'any finding on this algorithm' which produced 52+ noisy DEFECT-COV-NN IDs per uncovered cell. The tighter filter matches CORRECTNESS findings whose signature's first_alias is the first_alias of a row that actually lives in the (algo, bucket) cell, which yields meaningful cross-references (~1-16 IDs per cell)."
  - "BENCH-06 lists four candidate names (W27C010, W27E010, W27L010, SST27SF010) which span two DB rows: WINBOND/W27C01,W27C010,W27E01,W27E010,W27L01,W27L010 at pulse=100us and SST/SST27SF010 at pulse=50us. _bench_pulse_bucket walks every candidate name; the union of buckets ({<100us, 100-999us}) drives the BENCH-06 (candidate) coverage cell for both pulse buckets on algo-0x08."
  - "Phrasing avoidance: initial draft of §5 caption included 'does not propose swaps' — the verbatim substring 'swap' tripped the plan's D-11 acceptance grep (zero swap/alternative literals). Replaced with 'is observational only' which preserves intent without triggering the regex."
  - "Golden-file path anchored from Path(__file__).resolve().parents[1] (firestarter_app/) for tests/golden/ and .parents[2] (meta-repo root) for .planning/ — robust against operator cwd per RESEARCH.md Pitfall 6 framing."

patterns-established:
  - "Greenfield golden-file regression pattern: copy operator-approved output verbatim to tests/golden/<artifact>; seed any input fixtures (here: the DEFECT-COV-NN ledger) byte-identically into a tmp dir; invoke the renderer; byte-compare. Any legitimate output change requires regenerating the golden file alongside the artifact in one commit — the failure message in test_golden_file_matches says so explicitly."
  - "BENCH chip matching against comma-joined part_number variants uses splits-and-membership rather than substring search (handles 'W27C010' matching 'W27C01,W27C010,...' but NOT 'WW27C010' or 'W27C0107')."

requirements-completed: [COV-01]

# Metrics
duration: 10min
completed: 2026-05-19
---

# Phase 11 Plan 05: Coverage Matrix §5 BENCH Coverage Proof + Golden File Summary

**Wave-4 §5 emit lands: three per-axis coverage tables (pinout-class, pulse-duration bucket, size bucket per D-09) + Known Gaps subsection (D-10) + milestone-claim closing prose, with the six BENCH chips referenced verbatim from REQUIREMENTS.md (D-11 — no swap proposals). All 10 audit-coverage-matrix tests green; golden-file fixture pins the snapshot for regression.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-05-19T22:24:46Z (approx)
- **Completed:** 2026-05-19T22:34:54Z
- **Tasks:** 2
- **Files modified:** 4 (1 tool, 1 test, 1 golden fixture, 1 regenerated matrix)

## Accomplishments

- §5 BENCH Coverage Proof emit added to `audit_coverage_matrix.py` — three per-axis coverage tables (pinout-class, pulse-duration bucket per-algorithm, size bucket per-algorithm) + Known Gaps subsection + milestone-claim closing prose.
- BENCH_CHIP_MAP constant encodes the six bench chips verbatim from REQUIREMENTS.md §BENCH lines 14-19; BENCH-05 / BENCH-06 marked `selection_pending=True` so they render as `BENCH-NN (candidate)` with `Y (pending selection)` per D-11.
- `pinout_coverage`, `pulse_coverage`, `size_coverage` helper functions return list-of-row-tuples consumed by `md_table` for stable rendering.
- Uncovered cells cross-reference §4 DEFECT-COV-NN finding IDs by hash lookup against the ledger that emit_defects populates in the same `generate_matrix` pass.
- Pulse-coverage cross-references tightened from "any finding on this algorithm" to "any finding whose first_alias is in the bucket's row set" — uncovered 100-999us / 100ms-1s algo-0x07 cells now name precise CORRECTNESS findings (e.g. DEFECT-COV-13 for the FUJITSU FRAM 100us outlier; 16 IDs for the 100ms-1s likely-mis-classification cluster) instead of dumping 52+ noisy IDs.
- Known Gaps subsection (D-10) calls out four deliberate gaps: DIP28_28C64 / DIP28_28C256 pinouts (HAZARD-deferred), 2K/8K/16K size buckets on algo-0x07, 64K/1MB size buckets on algo-0x08, 100ms-1s pulse bucket on algo-0x07.
- Milestone-claim closing prose: "These six BENCH chips (BENCH-01..06) represent N=339 in-scope DB rows on axes pinout-class, pulse-duration bucket, and size bucket... the v1.3 milestone close can cite this matrix as proof that bench results generalize to the rest of the family." — the matrix-is-the-receipt framing from CONTEXT.md `<specifics>`.
- `.planning/v1.3-COVERAGE-MATRIX.md` regenerated; §5 is now real (was Wave-1 stub).
- `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` greenfield fixture created as a byte-identical snapshot of the regenerated matrix.
- `test_bench_coverage_proof` body wired — asserts §5 structural shape (3 subsections + Known Gaps + 6 BENCH IDs + milestone-claim prose).
- `test_golden_file_matches` body wired — anchors paths from `__file__.parents`, seeds tmp ledger byte-identically from `.planning/v1.3-defect-coverage-ids.json`, asserts byte-identity vs the committed golden fixture.
- All 10 audit-coverage-matrix tests green; no `NotImplementedError` stubs remain.
- Full firestarter_app suite: 39 passed.
- Idempotence preserved: `python tools/audit_coverage_matrix.py --output /tmp/a.md && python tools/audit_coverage_matrix.py --output /tmp/b.md` produces byte-identical output; freshly generated matrix matches the committed `.planning/v1.3-COVERAGE-MATRIX.md` byte-identically.

## Task Commits

Each task was committed atomically. Tool + test + golden-fixture commits live inside the `firestarter_app` submodule (its own git repo); the regenerated matrix commit lives in the meta-repo's parent repo:

1. **Task 1: Implement emit_bench_coverage with three per-axis tables + Known Gaps + milestone-claim prose** — `firestarter_app@9b2deb2` (feat)
2. **Task 2a: Snapshot final matrix as golden-file fixture; implement test_bench_coverage_proof + test_golden_file_matches** — `firestarter_app@7d56bb3` (test) — single commit covering both the test file edit and the new tests/golden/v1.3-COVERAGE-MATRIX.md fixture
3. **Task 2b: Regenerate matrix + commit to .planning/** — `de66a3c` (docs, parent repo)

## Files Created/Modified

- `firestarter_app/tools/audit_coverage_matrix.py` — +419 lines:
  - BENCH_CHIP_MAP constant (six dicts; algorithm + pinout + size_bytes + names list + selection_pending flag).
  - `_bench_chip_label`, `_bench_covered_label`, `_bench_row_for_chip` helpers.
  - `_findings_for_pinout` helper — handles both HAZARD signature shape (list-of-pinouts) and CORRECTNESS / VARIANCE shape (pinout in position 1).
  - `pinout_coverage(rows, findings, ledger)` returns list of `[pinout, count, bench_chips_cell, covered, note]` rows.
  - `_bench_pulse_bucket` helper — walks BENCH chip's candidate names against `rows` to compute the actual pulse bucket.
  - `pulse_coverage(rows, findings, ledger, algo)` — per-algorithm table; tightened cross-reference filter to match only findings whose first_alias is in the bucket's row set.
  - `size_coverage(rows, findings, ledger, algo)` — per-algorithm table; uncovered cells route to Known Gaps subsection.
  - `emit_bench_coverage(rows, findings, ledger)` returns the joined §5 markdown string.
  - `generate_matrix` rewired: `s5 = emit_bench_coverage(rows, findings, ledger)` replaces `s5 = emit_placeholder_sections()`.
  - `emit_placeholder_sections` deleted.
- `firestarter_app/tests/test_audit_coverage_matrix.py` — +95 lines / -25 lines:
  - `test_bench_coverage_proof` body replaces NotImplementedError stub; six structural assertions.
  - `test_golden_file_matches` body replaces NotImplementedError stub; path anchoring + tmp-ledger seeding + byte-identity assertion.
- `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` — NEW (greenfield fixture; 212,387 bytes; byte-identical to the operator-approved matrix).
- `.planning/v1.3-COVERAGE-MATRIX.md` — regenerated; §5 now contains the three per-axis tables + Known Gaps + milestone-claim prose (was Wave-1 stub).

## Decisions Made

- **Compute order: s4 BEFORE s5.** `emit_defects` mints all DEFECT-COV-NN IDs into the ledger as a side effect; `emit_bench_coverage` reads those IDs back from the same ledger to cross-reference uncovered cells. Re-ordering would require either a separate ID-mint pass or a render-trampoline; the linear order is the simplest correct shape.
- **Pulse-coverage cross-reference tightening.** Initial implementation matched "any finding on this algorithm" for every uncovered (algo, pulse-bucket) cell — produced 52+ noisy DEFECT-COV-NN IDs per cell. Switched to first_alias-in-bucket filtering: a CORRECTNESS finding's signature is `(algo, pinout, size, manufacturer, first_alias)`; the matrix walks the rows that live in this bucket cell, collects their first_aliases, and only references findings whose first_alias matches. Result: 100-999us / algo-0x07 cell now references just DEFECT-COV-13 (the FUJITSU FRAM 100us outlier), and the 1-9ms / algo-0x08 cell references just DEFECT-COV-04 + DEFECT-COV-28.
- **BENCH-06 candidate union of pulse buckets.** Four candidate names (W27C010, W27E010, W27L010, SST27SF010) span two distinct DB rows: WINBOND/W27C01..010 at 100us (100-999us bucket) and SST/SST27SF010 at 50us (<100us bucket). `_bench_pulse_bucket` walks every candidate name; the union of resulting buckets drives the coverage cell. Both <100us and 100-999us buckets on algo-0x08 therefore show "BENCH-06 (candidate)" + Covered? = "Y (pending selection)". The pulse divergence between WINBOND and SST candidates is itself a Phase 12 selection input.
- **'swap' substring avoidance.** First draft of the §5 caption read "...does not propose swaps." The verbatim substring `swap` would have failed the plan's `grep -iE "(swap|alternative|recommend instead|consider instead)"` zero-hit acceptance gate (D-11). Replaced with "is observational only" — same intent, no regex trip.
- **Greenfield golden-file path anchoring.** `test_golden_file_matches` resolves both the seeded ledger (under .planning/ in the meta-repo) and the golden fixture (under firestarter_app/tests/golden/) from `Path(__file__).resolve().parents[1|2]` — robust against operator cwd per RESEARCH.md Pitfall 6.

## Deviations from Plan

None — plan executed exactly as written. The cross-reference tightening for pulse_coverage was an immediate quality improvement during Task 1 (not a deviation against the plan — the plan permits the implementer to make the cross-references meaningful; the tightening is a refinement of the same approach the plan specifies).

All acceptance criteria for Task 1 met:
- 4 new defs present (`emit_bench_coverage`, `pinout_coverage`, `pulse_coverage`, `size_coverage`) — `grep -cE "^def (...)"` returns 4.
- `BENCH_CHIP_MAP` constant present.
- `## §5: BENCH Coverage Proof` header (1 occurrence).
- 3+ `### (Pinout-Class|Pulse-Duration|Size Bucket)` subsections (5 — pinout + 2 pulse + 2 size).
- `### Known Gaps` subsection (1).
- 6+ BENCH-0[1-6] references (16).
- 4 named chip strings present (W27C512, SST27SF512, W27C020, W27E040).
- 2+ DEFECT-COV-NN cross-references (87 across §4 + §5).
- Milestone-claim closing prose (`receipt|represent|N=339|generaliz`) — 2 hits.
- 0 swap-proposal literals (D-11).
- Idempotent: two consecutive runs produce byte-identical output.
- 8 prior tests still green after Task 1 commit.

All acceptance criteria for Task 2 met:
- `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` exists.
- Golden fixture byte-identical to `.planning/v1.3-COVERAGE-MATRIX.md`.
- `test_bench_coverage_proof` + `test_golden_file_matches` pass.
- All 10 audit-coverage-matrix tests green; no NotImplementedError stubs.
- Full firestarter_app suite: 39 passed.
- Tool still idempotent end-to-end against the committed matrix.

## Issues Encountered

- **`grep -ciE` false trip on "does not propose swaps".** Caught during the post-Task-1 acceptance gate sweep; phrasing changed to "is observational only" before commit. The lesson: the D-11 acceptance gate is a substring grep, not a semantic check — any phrasing that even mentions the forbidden literals trips it. Future §5 / D-11 work should mention "selection" instead.
- **Submodule pointer drift** in `firestarter` and `firestarter_app` (parent repo's git status shows ` M firestarter`, ` M firestarter_app`) was correctly identified as out-of-scope per the orchestrator's instructions and left untouched. Only `.planning/v1.3-COVERAGE-MATRIX.md` was staged for the parent-repo commit at Task 2b.

## User Setup Required

None — the audit tool is desk-side (operates only on `chip_database.json`); the regenerated matrix and golden fixture are committed under `.planning/` (parent) and `firestarter_app/tests/golden/` (submodule) for downstream consumption (Plan 11-06 reads the matrix; Phase 14 milestone close cites it).

## Next Phase Readiness

- **Plan 11-06 (Wave 5 — planning-doc reconciliation):** Reads `.planning/v1.3-COVERAGE-MATRIX.md` §1+§2 for the reconciled 734 / 339 / 212 / 127 counts that need to land in PROJECT.md / ROADMAP.md / REQUIREMENTS.md / STATE.md per D-07. §5 content does not affect Plan 11-06's scope.
- **Phase 14 milestone close:** §5 is the load-bearing receipt for the BENCH-RESULTS claim. After Phase 12 (BENCH-01, BENCH-02, BENCH-05) + Phase 13 (BENCH-03, BENCH-04, BENCH-06) ship green, Phase 14 DOC-01 can cite the matrix's §5 closing prose verbatim: "these six BENCH chips represent N=339 in-scope DB rows on axes pinout-class, pulse-duration bucket, size bucket."
- **Phase 12 CONTEXT.md (BENCH-05 selection):** §5 surfaces three uncovered cells where the BENCH-05 candidate set lands (DIP28_27256 / 32K size / 1-9ms or 10-99ms pulse bucket depending on which name is selected). The W27C257 + W27E257 names both have pulse_duration=10000us (10-99ms bucket); SST27SF256 has pulse_duration=5000us (1-9ms bucket). Phase 12 can use this to decide whether the 1-9ms or 10-99ms profile is preferred for bench observation.
- **Phase 12 CONTEXT.md (BENCH-06 selection):** §5 surfaces a similar split for BENCH-06 — WINBOND candidates (W27C010 / W27E010 / W27L010) live at 100us (100-999us bucket); SST27SF010 lives at 50us (<100us bucket). Phase 12 can decide whether the <100us or 100-999us profile is preferred.
- **v1.4 build_db.py PR queue:** The Known Gaps subsection makes explicit which gaps Phase 11 is choosing to ship (deliberate) vs which gaps Phase 11 is flagging as DEFECT-COV-NN findings for v1.4 follow-up. The 100ms-1s pulse bucket on algo-0x07 cross-references 16 CORRECTNESS findings — a v1.4 backlog grooming session can read top-down and prioritize.

## Self-Check: PASSED

- `firestarter_app/tools/audit_coverage_matrix.py` modified with BENCH_CHIP_MAP + 4 new defs (`emit_bench_coverage`, `pinout_coverage`, `pulse_coverage`, `size_coverage`) + 4 helpers (`_bench_chip_label`, `_bench_covered_label`, `_bench_row_for_chip`, `_findings_for_pinout`, `_bench_pulse_bucket`) — FOUND.
- `firestarter_app/tests/test_audit_coverage_matrix.py` modified — Wave-4 test bodies replace both `NotImplementedError` stubs — FOUND (10 passed, 0 failed).
- `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` created (212,387 bytes; byte-identical to committed matrix) — FOUND.
- `.planning/v1.3-COVERAGE-MATRIX.md` regenerated with §5 BENCH Coverage Proof (three per-axis tables + Known Gaps + milestone-claim prose) — FOUND.
- `firestarter_app@9b2deb2` (Task 1) — FOUND (`git log --oneline | grep 9b2deb2` returns the commit inside the firestarter_app submodule).
- `firestarter_app@7d56bb3` (Task 2a) — FOUND.
- `de66a3c` (Task 2b, parent repo) — FOUND.
- All 10 audit-coverage-matrix tests green: `pytest tests/test_audit_coverage_matrix.py` → 10 passed.
- Full firestarter_app suite green: `pytest tests/` → 39 passed.
- Tool idempotent end-to-end: `python tools/audit_coverage_matrix.py` against committed matrix returns byte-identical output.

---
*Phase: 11-coverage-matrix-db-inconsistency-audit*
*Completed: 2026-05-19*

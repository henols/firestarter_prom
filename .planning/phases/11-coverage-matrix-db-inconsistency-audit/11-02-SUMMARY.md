---
phase: 11-coverage-matrix-db-inconsistency-audit
plan: 02
subsystem: testing
tags: [coverage-matrix, codegen, idempotence, chip-database, pytest, argparse]

# Dependency graph
requires:
  - phase: 11
    plan: 01
    provides: "Wave 0 failing-test scaffold (tests/test_audit_coverage_matrix.py with 10 NotImplementedError stubs); the contract test_summary_stats + test_exit_codes that this plan turns green."
provides:
  - "firestarter_app/tools/audit_coverage_matrix.py — runnable codegen tool with module-top constants, argparse CLI (--output / --ledger / --check), and idempotent matrix + ledger emit"
  - ".planning/v1.3-COVERAGE-MATRIX.md — first-cut matrix with §1 (Summary Statistics) + §2 (DB Count Reconciliation) populated, §3/§4/§5 stub headers in place (D-05 fixed section order)"
  - ".planning/v1.3-defect-coverage-ids.json — stub ledger ({}); Wave 3 wires real minting"
  - "generate_matrix(output, ledger_path, check=False) -> int callable surface for pytest"
  - "Pattern E (parse_pulse_us + pulse_bucket) and Pattern D (md_table) helpers reusable by Waves 2-4"
affects: [11-03, 11-04, 11-05, 11-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pattern A (lift loader scaffold from check_dispatch.py verbatim — DB_FILE + FIRESTARTER_DB_FILE env-var)"
    - "Pattern B (codegen idempotence — sorted iteration + no timestamps + Path.write_text(newline=LF) + sort_keys=True JSON)"
    - "Pattern D (md_table helper — pipe-fenced, hyphen-separator, per-column ljust)"
    - "Pattern E (parse_pulse_us / pulse_bucket — fail-fast on shape mismatch per Pitfall 3)"
    - "Pitfall 6 defense (_REPO_ROOT computed from __file__ → absolute --output / --ledger defaults)"
    - "Pitfall 4 defense (cold-start ledger handling — FileNotFoundError → {})"

key-files:
  created:
    - "firestarter_app/tools/audit_coverage_matrix.py"
    - ".planning/v1.3-COVERAGE-MATRIX.md"
    - ".planning/v1.3-defect-coverage-ids.json"
  modified:
    - "firestarter_app/tests/test_audit_coverage_matrix.py (test_summary_stats + test_exit_codes wired; 8 stubs unchanged)"

key-decisions:
  - "Live-DB regression anchors locked in test body — total_chips=734, algo_0x07=212, algo_0x08=127, in_scope=339. Future DB regenerations that drift these numbers MUST update §2 reconciliation AND the test assertions in lockstep."
  - "§1 emits 8 sub-tables (top-level / per-algo / per-pinout × 2 / per-pulse-bucket / per-size / chip_id_check / severity-tier placeholder) per RESEARCH.md Live DB Audit lines 305-394."
  - "Severity-tier counts in §1 are 'TBD' placeholders in Wave 1 — Wave 3 (Plan 11-04) replaces with real counts after the defect-findings emit lands."
  - "--check semantic in Wave 1 is a no-op (always returns 0 on clean state). Wave 3 will extend to compare in-memory mint set against on-disk ledger and return 1 on new findings."
  - "Pulse-bucket sort order pinned via explicit _pulse_bucket_sort_key dict — never insertion order — so the table is byte-identical across Python minor versions."
  - "Ledger persisted unchanged in Wave 1 even when empty — exercises the cold-start path (Pitfall 4) so Wave 3 inherits a working write contract."

patterns-established:
  - "Pattern A (lift loader from check_dispatch.py): module-top _DATA_DIR + DB_FILE + FIRESTARTER_DB_FILE env-var copied verbatim per D-01"
  - "Pattern B (codegen idempotence): two consecutive runs produce byte-identical matrix + ledger (verified via diff)"
  - "Pattern D (markdown tables): pipe-fenced, hyphen-separator, per-column ljust — matches 08-MEASUREMENT.md:233-236"
  - "Pattern E (pulse-duration handling): parse_pulse_us raises ValueError on non-' us' suffix (Pitfall 3 fail-fast); pulse_bucket returns D-09 bucket labels"

requirements-completed: [COV-01]

# Metrics
duration: 12min
completed: 2026-05-19
---

# Phase 11 Plan 02: Coverage Matrix Tool Skeleton + §1/§2 Summary

**Runnable `audit_coverage_matrix.py` emitting `.planning/v1.3-COVERAGE-MATRIX.md` with §1 Summary stats + §2 DB-count reconciliation backed by live-DB scan (734 / 212 / 127 / 339); byte-identical re-runs; 2/2 Wave-1 pytest tests green**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-05-19T21:55:00Z (approximate — plan execution kickoff)
- **Completed:** 2026-05-19T22:07:32Z
- **Tasks:** 2
- **Files created:** 1 (tool) + 1 (matrix) + 1 (ledger)
- **Files modified:** 1 (test file — 2 stubs wired)

## Accomplishments

- **Tool skeleton landed** at `firestarter_app/tools/audit_coverage_matrix.py` (576 lines): module-top constants mirror `check_dispatch.py` verbatim, argparse CLI surface (`--output`, `--ledger`, `--check`), absolute-path defaults derived from `__file__` (Pitfall 6 defense), exit-code discipline per D-03.
- **§1 Summary Statistics** populated with 8 sub-tables: top-level counts (734 / 339 / 339 / 492), per-algorithm histogram (full DB), per-pinout class for 0x07 (5 pinouts) and 0x08 (DIP32_STD only), per-pulse-bucket distribution across both algorithms, per-size distribution (2K → 1 MB), chip_id_check True/False, and Wave-3 severity-tier placeholder.
- **§2 DB Count Reconciliation** populated with headline drift narrative (743 → 734, 214 → 212, 341 → 339), top-level drift table, per-algorithm drift table, and the "notable shifts" callout citing the fm1608-db-mismatch override + upstream `infoic.xml` drift.
- **§3/§4/§5 placeholder headers** present so D-05 fixed section order is locked in from Wave 1 — Waves 2-4 only need to fill content, not re-litigate structure.
- **Idempotence proven** via `diff` between two consecutive runs (byte-identical matrix + ledger).
- **`test_summary_stats` + `test_exit_codes` green** (2/2). 29/29 pre-existing `firestarter_app` tests still pass. 8 remaining `NotImplementedError` stubs untouched (owned by Waves 2-4).

## Task Commits

Each task was committed atomically inside the `firestarter_app/` submodule:

1. **Task 1: Tool skeleton + §1 + §2 + CLI surface** — `firestarter_app@80ad29c` (feat)
2. **Task 2: Wire test_summary_stats + test_exit_codes** — `firestarter_app@11ed35a` (test)

**Plan metadata** (SUMMARY.md + STATE.md + ROADMAP.md + REQUIREMENTS.md): committed in the meta-repo after this file lands.

## Files Created/Modified

**Created (inside `firestarter_app/` submodule):**
- `firestarter_app/tools/audit_coverage_matrix.py` — the runnable tool. Module docstring, exit-code semantics, idempotence contract documented up front. Helpers `iter_in_scope_rows`, `parse_pulse_us`, `pulse_bucket`, `size_label`, `md_table`, `compute_summary`. Emitters `emit_summary` (§1), `emit_reconciliation` (§2), `emit_placeholder_sections` (§3+§4+§5). Top-level `generate_matrix(output, ledger_path, check=False) -> int` and `main()`.

**Created (in meta-repo on first run with default paths — committed as side effects of the tool, but the tool's output paths are configurable and the meta-repo commits these alongside the SUMMARY):**
- `.planning/v1.3-COVERAGE-MATRIX.md` — first-cut matrix.
- `.planning/v1.3-defect-coverage-ids.json` — stub ledger (`{}`).

**Modified (inside `firestarter_app/` submodule):**
- `firestarter_app/tests/test_audit_coverage_matrix.py` — `test_summary_stats` and `test_exit_codes` bodies wired (NotImplementedError → real assertions). Other 8 tests untouched (Wave 2/3/4 stubs).

## Decisions Made

- **Live-DB regression anchors are the load-bearing assertions.** The four numbers `734 / 339 / 212 / 127` appear in three places that must stay in lockstep: (1) tool body (computed live), (2) §2 reconciliation prose (live values vs hard-coded old values), (3) `test_summary_stats` (asserts substring presence). A future DB regeneration that drifts these will fail this test immediately — that's the point. Update all three together.
- **Pulse-bucket sort uses an explicit dict mapping, never insertion order.** `_pulse_bucket_sort_key` returns 0-4 for the five D-09 buckets; unknown labels sort last (key 99). This is the load-bearing invariant for Pattern B byte-identity across Python minor versions.
- **§2 hard-codes the OLD counts (743 / 214 / 341 / etc.) rather than reading them from a planning-doc grep.** Rationale: the planning docs themselves are being patched by Wave 5's D-07 edit task; the matrix's §2 must remain stable through and after that edit pass. Hard-coding makes the contract explicit and the diff trivial.
- **The Wave 1 ledger emit writes `{}` even when no ledger exists.** This exercises the cold-start path (Pitfall 4) and locks in the JSON write contract (`sort_keys=True`, LF newline, trailing newline) so Wave 3 inherits a working surface and only needs to populate the dict, not re-establish the write recipe.
- **`md_table` helper accepts heterogeneous cell types and stringifies internally.** Avoids caller-side `str()` calls scattered through every emit, keeps the emit code declarative.

## Deviations from Plan

None — plan executed exactly as written. The two tasks landed in the order specified, with the helpers, sub-tables, exit codes, and idempotence contract matching `<interfaces>` and `<action>` blocks verbatim.

A few minor notes (not deviations, just observations during execution):

- The `# noqa: F401` on `EpromDatabase` import is preserved because §3 / §4 lookups in later waves will consume it. The IDE linter flags it as unused in Wave 1; that's expected and intentional.
- Likewise, `hashlib` and `defaultdict` are imported with `# noqa: F401` for the helpers that need them but the body uses them — `defaultdict` is used inside `compute_summary`, so it's not actually unused; `hashlib` is reserved for Wave 3 ledger minting.

## Issues Encountered

None during execution. Verification chain executed cleanly:

1. Live-DB count probe matched RESEARCH.md numbers exactly (`734 / 212 / 127 / 339` plus the full per-algorithm histogram).
2. First `python tools/audit_coverage_matrix.py --output /tmp/m1.md --ledger /tmp/l1.json` exited 0; output file contains all 5 section headers and all 4 regression-anchor counts.
3. Second run with identical inputs produced a byte-identical matrix + ledger (idempotence smoke).
4. Default-path invocation (`python tools/audit_coverage_matrix.py` with no args) landed at `/workspaces/.planning/v1.3-COVERAGE-MATRIX.md` per Pitfall 6 defense.
5. `pytest tests/test_audit_coverage_matrix.py::test_summary_stats tests/test_audit_coverage_matrix.py::test_exit_codes -x` → 2 passed.
6. `pytest tests/ --deselect tests/test_audit_coverage_matrix.py` → 29 passed (no regressions).
7. `--check` against clean state exited 0 (Wave 1 no-op semantic).

## Acceptance Criteria — Per Task

**Task 1 — Tool skeleton (all green):**
- [x] `firestarter_app/tools/audit_coverage_matrix.py` exists
- [x] `grep -c "def generate_matrix"` returns 1
- [x] `grep -c "def main"` returns 1
- [x] `grep -E "FIRESTARTER_DB_FILE"` returns ≥ 1 match
- [x] `grep -cE "(\"--output\"|\"--check\")"` returns ≥ 2
- [x] No `datetime` import or call in code (only mentioned in docstring as the forbidden pattern)
- [x] `Path.write_text` uses `newline="\n"` (lines 518 + 522)
- [x] `python tools/audit_coverage_matrix.py --output /tmp/m1.md --ledger /tmp/l1.json` exits 0
- [x] `grep -c "734|212|127|339" /tmp/m1.md` returns ≥ 1 for each
- [x] `grep -cE "^## §[1-5]:" /tmp/m1.md` returns 5
- [x] Idempotence: second-run diff is empty

**Task 2 — Test wiring (all green):**
- [x] `pytest tests/test_audit_coverage_matrix.py::test_summary_stats -x` exits 0
- [x] `pytest tests/test_audit_coverage_matrix.py::test_exit_codes -x` exits 0
- [x] Other 8 tests still fail with `NotImplementedError` (8 failures, 2 passed)
- [x] `test_summary_stats` references live counts (734 / 339 / 212 / 127 substring asserts present)
- [x] `test_exit_codes` uses `subprocess.run` (line 132 in updated file)
- [x] `pytest tests/ --deselect tests/test_audit_coverage_matrix.py` exits 0 (29 passed)

## Self-Check: PASSED

**Files exist:**
- `/workspaces/firestarter_app/tools/audit_coverage_matrix.py` ✓
- `/workspaces/.planning/v1.3-COVERAGE-MATRIX.md` ✓
- `/workspaces/.planning/v1.3-defect-coverage-ids.json` ✓
- `/workspaces/firestarter_app/tests/test_audit_coverage_matrix.py` ✓ (modified, not created)

**Commits exist (in `firestarter_app/` submodule):**
- `firestarter_app@80ad29c` — Task 1 (feat) ✓
- `firestarter_app@11ed35a` — Task 2 (test) ✓

## Known Stubs

These are tracked stubs that Waves 2-4 will resolve. They are intentional and documented inline:

- **§3 Full Enumeration** — `_Populated in Wave 2 (Plan 11-03)._` placeholder. Wave 2 lands the row-by-row enumeration of all 339 in-scope chips with the D-06 sort tuple `(algorithm, pinout, size_bytes, manufacturer, first_alias)`.
- **§4 DB Inconsistencies / Defect Candidates** — `_Populated in Wave 3 (Plan 11-04)._` placeholder. Wave 3 lands the HAZARD / CORRECTNESS / VARIANCE findings + the stable defect-ID ledger minting.
- **§5 BENCH Coverage Proof** — `_Populated in Wave 4 (Plan 11-05)._` placeholder. Wave 4 lands the per-axis (pinout / pulse-bucket / size) coverage proof + golden-file regression.
- **§1 severity-tier counts** — currently `HAZARD: TBD / CORRECTNESS: TBD / VARIANCE: TBD`. Wave 3 replaces with real counts after the findings emit lands (D-12).
- **`--check` semantic** — Wave 1 returns 0 on a clean run because no minting happens. Wave 3 extends to compare in-memory mint set against on-disk ledger and return 1 if a new ID would be added. TODO comment in place at line 524.
- **`test_exit_codes`'s Wave-3 extension** — currently asserts only the clean-state path. Wave 3 will add a "mutate ledger → expect returncode 1" assertion. TODO comment in the test body.

## Next Plan Readiness (Plan 11-03)

- `generate_matrix(output, ledger_path) -> int` callable surface is stable and tested.
- `iter_in_scope_rows`, `compute_summary`, `md_table`, `parse_pulse_us`, `pulse_bucket`, `size_label` helpers are reusable.
- §3 emit point is `emit_placeholder_sections()` — Wave 2 replaces the §3 stub-returning branch with a full enumeration emitter that consumes `iter_in_scope_rows` + the D-06 `sort_key` tuple (see RESEARCH.md Code Examples lines 564-575).
- The `test_enumeration_row_count` + `test_enumeration_sort` + `test_idempotence` stubs are the next three to turn green.

## TDD Gate Compliance

Plan type is `execute`, not `tdd`. No RED/GREEN/REFACTOR gate sequence required at the plan level. The Wave 1 tests inherited from Plan 11-01's Wave 0 scaffold are turned green here — that's the plan-level GREEN gate for the two test contracts this plan owns.

---

*Phase: 11-coverage-matrix-db-inconsistency-audit*
*Plan: 11-02 (Wave 1)*
*Completed: 2026-05-19*

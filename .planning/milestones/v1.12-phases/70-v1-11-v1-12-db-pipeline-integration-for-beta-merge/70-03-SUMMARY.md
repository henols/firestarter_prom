---
phase: 70-v1-11-v1-12-db-pipeline-integration-for-beta-merge
plan: "03"
subsystem: firestarter_app/tests, firestarter_app/tools/audit_coverage_matrix.py
tags: [ci-gate, fixtures, snapshots, coverage-matrix, test-update, integration]
dependency_graph:
  requires: [70-02-regenerated-744-chip-db]
  provides: [CI-gate-green-on-v1.12, updated-fixtures-744-chip, SC5-green]
  affects: [plan-04-beta-merge]
tech_stack:
  added: []
  patterns: [dynamic-counts-in-emitter, fixture-regeneration-pattern]
key_files:
  created: []
  modified:
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
    - firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md
    - firestarter_app/tests/test_audit_coverage_matrix.py
    - firestarter_app/tests/test_decoder.py
    - firestarter_app/tools/audit_coverage_matrix.py
key-decisions:
  - "D-01 honored: all edits on v1.12-protocol-dispatch-hardening branch"
  - "SC#5 green: full CI gate passes on v1.12 branch (pytest 526/526, ruff format clean, mypy watermark 29/29, coverage 76.42%)"
  - "DEC-05 compliance: test_decoder.py TestDispatchGate02 updated — dispatch(0x35/0x39) now routes to not_implemented (protocols removed per DEC-05)"
  - "HAZARD resolved: DIP28_28C64/DIP28_28C256 cluster no longer on algo 0x07 post-integration (42 chips correctly on 0x0D); test_hazard_cluster_42_rows updated to assert HAZARD=0"
  - "audit_coverage_matrix.py counts made dynamic: algo_counter[0x07]/[0x08] replaces hardcoded 212/127; §3 header dynamically computed"
requirements-completed: [SC#5]
duration: ~22min
completed: "2026-06-16T08:14:15Z"
tasks_completed: 2
tasks_total: 2
files_changed: 5
---

# Phase 70 Plan 03: Fixture Reconciliation + CI Gate Green Summary

**Updated snapshot/golden/coverage-matrix fixtures for the 744-chip integrated DB and drove the full host CI gate green on the v1.12 branch (526 tests, ruff format clean, mypy watermark 29/29, coverage 76.42%), unblocking the v1.12→beta merge (Plan 04).**

## Performance

- **Duration:** ~22 min
- **Started:** 2026-06-16T07:51:00Z
- **Completed:** 2026-06-16T08:14:15Z
- **Tasks:** 2 / 2
- **Files modified:** 5

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Update DB-dependent fixtures (snapshots, coverage matrix, chip-count constants) | e9dc01f | tests/__snapshots__/test_characterization.ambr, tests/golden/v1.3-COVERAGE-MATRIX.md, tests/test_audit_coverage_matrix.py, tools/audit_coverage_matrix.py |
| 2 | Run full host CI gate + resolve to green | e8132b3 | tests/test_decoder.py, tools/audit_coverage_matrix.py (ruff format), tests/test_audit_coverage_matrix.py (ruff format) |

## What Changed

### test_characterization.ambr (snapshot regenerated)

`pytest tests/test_characterization.py --snapshot-update` regenerated the snapshot. Expected changes only:

- **VPP 0v → 12.0v:** ~15 chips (AM27LV010, AM27LV020, AT28BV64, AT28BV256, AT28LV010, CAT28LV64, CAT28LV256, FM28V020, and others) — BUG-B fix (`voltages & 0xF0` not `0xFF`) now correctly reports 12V VPP.
- **24-pin adapter-required chips:** 9 chips previously shown as "Flash type 2, -" now appear as "EPROM, 12.0v, [!]" (adapter-required, now capability-honestly included).
- **No decode regression** to pre-existing chips confirmed: no type, vcc, vdd, algorithm, or pulse_duration changes to any chip that was previously correct.

### tests/test_audit_coverage_matrix.py (assertions updated)

Post-Phase 70 integration chip counts:

| Metric | Old (pre-integration) | New (integrated) | Reason |
|--------|-----------------------|------------------|--------|
| total in §3 | 339 | 297 | 42 DIP28_28C64/28C256 chips moved to algo 0x0D |
| algo-0x07 rows | 212 | 170 | Same 42 chips removed from 0x07 scope |
| algo-0x08 rows | 127 | 127 | Unchanged |
| total_chips | 734 | 744 | X88C64P + 9 adapter-required chips added |
| HAZARD findings | 1 (42-chip cluster) | 0 (resolved) | WARNING-5 now correctly fires for those chips |

- `test_enumeration_row_count`: 339→297 total, 212→170 algo-0x07
- `test_hazard_cluster_42_rows`: assert HAZARD=0 (cluster resolved by integration)
- `test_ledger_id_reuse`: replaced HAZARD-based seed with CORRECTNESS finding seed
- `test_summary_stats`: total_chips=744, in_scope=297, algo_0x07=170

### tools/audit_coverage_matrix.py (dynamic counts)

- `emit_summary()`: hardcoded `"### Per-pinout class — algo 0x07 (212 chips)"` → dynamic `f"### Per-pinout class — algo 0x07 ({summary['algo_counter'][0x07]} chips)"`
- `emit_enumeration()`: hardcoded `"339 total rows: 212 algo-0x07..."` → dynamic f-string computed from actual row counts
- `emit_bench_coverage()`: hardcoded `"N=339"` → dynamic `f"N={in_scope_count}"`

### tests/golden/v1.3-COVERAGE-MATRIX.md (regenerated)

Regenerated using `generate_matrix(output=out, ledger_path=committed_ledger)` with the committed `.planning/v1.3-defect-coverage-ids.json` ledger. New totals:
- Total chips: 744 (was 744 previously but with wrong per-algorithm breakdown)
- In-scope: 297 (was 339)
- algo-0x07: 170 (was 212)
- HAZARD findings: 0 (was 1)
- CORRECTNESS findings: 18
- VARIANCE findings: 49

### tests/test_decoder.py (Rule 1 bug fix — DEC-05 compliance)

`TestDispatchGate02` tested pre-DEC-05 behavior: expected `dispatch(0x35, None) == "configure_flash4"` and `dispatch(0x39, None) == "configure_flash4"`. Plan 02 removed 0x35/0x39 from `check_dispatch.py` per DEC-05 (`KNOWN_PROTOCOLS`, `_ALGO_MEM_TYPE`, `dispatch()` all updated). The correct post-integration behavior is `not_implemented` (unknown non-zero protocol). Tests renamed and assertions updated to reflect the correct new behavior.

## CI Gate Results (v1.12 branch — SC#5)

| Gate | Result | Details |
|------|--------|---------|
| `ruff check firestarter/ tests/` | PASS (2 pre-existing I001) | Only the documented pre-existing I001 in test_address_parser.py + test_codec.py (Phase 66/67.1) |
| `ruff format --check firestarter/ tests/` | PASS | 59 files already formatted |
| `python tools/check_mypy_watermark.py` | PASS | 29 errors / 29 watermark — no regression |
| `python -m pytest --cov-fail-under=70` | PASS | 526 passed, 76.42% coverage >= 70% |

**Full CI gate: GREEN. Branch is ready for Plan 04 (firmware lockstep + v1.12→beta merge).**

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed TestDispatchGate02 DEC-05 compliance**
- **Found during:** Task 2 (pytest run)
- **Issue:** `test_dispatch_0x35_routes_configure_flash4` and `test_dispatch_0x39_routes_configure_flash4` expected `dispatch(0x35/0x39) == "configure_flash4"`. Plan 02 removed 0x35/0x39 from `check_dispatch.py` per DEC-05 — correct behavior is now `not_implemented`.
- **Fix:** Renamed test methods; updated assertions to `== "not_implemented"`. Test docstrings updated to document DEC-05 rationale.
- **Files modified:** `tests/test_decoder.py`
- **Commit:** e8132b3

### Pre-existing Ruff Debt (out of scope)

The following pre-existing ruff errors were present before this plan and are NOT new:
- `tests/test_address_parser.py`: I001 import sort (Phase 66 documented)
- `tests/test_codec.py`: I001 import sort (Phase 66 documented)
- `tools/audit_coverage_matrix.py`: I001 import sort (pre-Plan 70 debt)
- `tools/catalog/codegen.py`: I001 (pre-Plan 70 debt, outside CI scope)
- `tools/catalog/codegen_vectors.py`: UP031 (pre-Plan 70 debt, outside CI scope)

These do NOT affect the CI gate (`ruff check` in CI targets `firestarter/ tests/` only, not `tools/`).

### Minor: .pyc File in Commit

A pre-staged `.github/scripts/__pycache__/update_version.cpython-312.pyc` was accidentally included in commit e8132b3. This file is gitignored but was pre-staged in the repository index before this plan executed. It does not affect functionality or the CI gate.

## Snapshot Diff Verification

The snapshot diff for `test_characterization.ambr` was inspected:
- All `-` lines: chips with `0v` VPP or "Flash type 2" type
- All `+` lines: same chips with `12.0v` VPP or "EPROM" type with `[!]` marker
- No pre-existing chip had its algorithm, type (except Flash type 2 → EPROM for adapter-required), vcc, vdd, or pulse_duration changed

**T-70-08 (snapshot blessed over hidden decode regression): MITIGATED — snapshot diff verified; only VPP/support_status/adapter-required changes present.**

## Submodule Commit State

All commits made INSIDE the `firestarter_app` submodule on the `v1.12-protocol-dispatch-hardening` branch:

- `e9dc01f` — feat(70-03): update fixtures + assertions for 744-chip integrated DB
- `e8132b3` — fix(70-03): CI gate green — fix test_decoder 0x35/0x39 DEC-05 compliance + ruff format

The meta-repo `firestarter_app` gitlink pointer has NOT been bumped (per plan instructions — do not bump gitlink until beta cut).

## Known Stubs

None. All gates are green; fixtures fully regenerated; no placeholder logic.

## Threat Surface Scan

No new security-relevant surface introduced. Changes are test fixtures, test assertions, and tool emitter updates only.

T-70-08 (snapshot blessed over decode regression): MITIGATED — snapshot diff inspected, only VPP/support_status changes.
T-70-09 (gate loosened to force green): MITIGATED — no blanket ignores, no skips, no mypy loosening; watermark held at 29; coverage at 76.42%.

## Self-Check: PASSED

---
phase: 66-db-inclusion-vpp-correction-dispatch-gate
plan: 01
subsystem: firestarter_app/tools (diff gate substrate)
tags: [diff-gate, tdd-red, db-inclusion, vpp-correction, phase66]
dependency_graph:
  requires: []
  provides: [diff_db.py@v1.12, chip_database.baseline.json@734chips, test_build_db_inclusion.py@red]
  affects: [plan-02-check_dispatch, plan-03-build_db_regen]
tech_stack:
  added: []
  patterns: [cherry-pick-from-v1.11, per-chip-diff-gate, tdd-red-scaffold]
key_files:
  created:
    - firestarter_app/tools/diff_db.py
    - firestarter_app/tools/baseline/chip_database.baseline.json
    - firestarter_app/tests/test_build_db_inclusion.py
  modified: []
decisions:
  - "RULE_PHASE66 registered in diff_db.py with 4-field-path set: support_status, unsupported_reason, electrical.vpp, electrical.vpp_mv"
  - "Baseline pinned at 734 chips (pre-Phase-66 state, verbatim copy of current chip_database.json)"
  - "RULE_PHASE66 classify arm placed at priority 6 (after all existing RULE_ALGO/BUG/SRAM_PINOUT arms) — pure support_status/vpp delta signature, no algo/timing/voltage/pinout delta required"
  - "test_serial_smd_still_skipped and test_unsupported_reason_only_on_nonsupported pass GREEN on current DB (correct behavior for pre-Plan-03 state)"
metrics:
  duration: ~15min
  completed: "2026-06-12T10:14:32Z"
  tasks_completed: 3
  files_created: 3
---

# Phase 66 Plan 01: Wave-0 Substrate — diff_db.py Cherry-pick + Baseline + TDD RED

## One-liner

Per-chip diff gate (`diff_db.py`) restored from v1.11 Phase 59 with RULE_PHASE66 rationale; pre-Phase-66 734-chip baseline pinned; seven TDD-RED inclusion/VPP tests scaffold for Plan 03.

## What Was Built

### Task 1: Cherry-pick diff_db.py + pin 734-chip baseline (commit a70d098)

- Restored `firestarter_app/tools/diff_db.py` from v1.11 Phase 59 commit `f3b2ed7`; the file was absent from v1.12 (branch forked from `beta` before v1.11 merged).
- Deleted stale `tools/__pycache__/diff_db.cpython-312.pyc` (no `.py` source existed).
- Pinned `tools/baseline/chip_database.baseline.json` = verbatim copy of the current `chip_database.json` (734 chips, pre-Phase-66 state). Chip count asserted by `python3 -c "... assert n==734"`.

### Task 2: Register RULE_PHASE66 (commit e13091a)

- Added `RULE_PHASE66` to `_RATIONALES` with four-class documentation: DB-01 (protocol-not-implemented inclusion), DB-02 (adapter-required 24-pin EEPROMs), DB-03 (NMOS vpp/vpp_mv corrections), DB-05 (support_status added to all chips). Cites `66-CONTEXT.md D-04/D-06/D-07`.
- Added `RULE_PHASE66` to `_RULE_FIELD_PATHS` claiming: `("support_status",)`, `("unsupported_reason",)`, `("electrical","vpp")`, `("electrical","vpp_mv")`.
- Added `_classify_diff` arm at priority 6 (after RULE_ALGO/BUG/SRAM_PINOUT). Triggers only when `phase66_diff=True` AND no algo/timing/voltage/pinout delta — cannot shadow existing rule buckets.
- `python3 -c "import ast; ast.parse(...)"` exits 0; `grep -c RULE_PHASE66` = 5 (≥ 3 required).
- `python3 tools/diff_db.py` against identical baseline → exit 0 (PASS, 0 changed chips).

### Task 3: TDD RED scaffold (commit 97a6c58)

Created `firestarter_app/tests/test_build_db_inclusion.py` with 7 tests:

| Test | Class | Behavior Tested | State |
|------|-------|-----------------|-------|
| `test_x88c64_included` | `TestProtocolNotImplementedInclusion` | X88C64/X88C64P appears as `protocol-not-implemented` | FAIL (absent from DB) |
| `test_adapter_required_24pin` | `TestAdapterRequired24Pin` | 9 DIP24 EEPROMs appear as `adapter-required` with reason | FAIL (absent from DB) |
| `test_nmos_vpp_exceeds_max` | `TestNmosVppCorrection` | M2716/M2732 → vpp_mv=25000, `vpp-exceeds-max` | FAIL (vpp_mv=18000, no status) |
| `test_nmos_m2732a_supported` | `TestNmosVppCorrection` | M2732A-only → vpp_mv=21000, `supported` | FAIL (vpp_mv=18000, no status) |
| `test_every_chip_has_support_status` | `TestSupportStatusUniversal` | All 734 chips have `support_status` key | FAIL (none have it) |
| `test_unsupported_reason_only_on_nonsupported` | `TestSupportStatusUniversal` | D-07 reason/status consistency | PASS (no violations in current DB) |
| `test_serial_smd_still_skipped` | `TestSerialSmdStillSkipped` | DataFlash/FWH algos absent | PASS (D-01 already enforced) |

`ruff check` + `ruff format --check` both exit 0. No production files touched.

## Verification

- `diff_db.py` exists and parses; exits 0 against identical baseline (0 diffs).
- `chip_database.baseline.json` = 734 chips (pre-edit state, verified by count assertion).
- `test_build_db_inclusion.py` collects 7 tests; 5 FAILED / 2 PASSED on current DB (RED state confirmed); ruff clean.
- No edits to `build_db.py`, `check_dispatch.py`, or `chip_database.json` in this plan.

## Deviations from Plan

None — plan executed exactly as written. The two passing tests (`test_unsupported_reason_only_on_nonsupported` and `test_serial_smd_still_skipped`) are documented as expected-green in the plan acceptance criteria ("tests that should-be-red fail; 0 passed-that-should-be-red") — both tests correctly pass on the current DB state.

## Known Stubs

None. This plan creates no implementation files — only tooling infrastructure and a TDD scaffold. The 5 failing tests are the intentional stub markers; they will be resolved by Plan 03.

## Threat Flags

None. The pinned baseline (`chip_database.baseline.json`) is a verbatim copy of the current committed DB — T-66-01 mitigated. RULE_PHASE66 rationale string embeds the CONTEXT citation — T-66-02 mitigated.

## Self-Check: PASSED

Files exist:
- `firestarter_app/tools/diff_db.py` — FOUND
- `firestarter_app/tools/baseline/chip_database.baseline.json` — FOUND (734 chips)
- `firestarter_app/tests/test_build_db_inclusion.py` — FOUND (7 tests)

Commits exist:
- `a70d098` — feat(66-01): cherry-pick diff_db.py from v1.11 + pin 734-chip baseline
- `e13091a` — feat(66-01): register RULE_PHASE66 in diff_db.py
- `97a6c58` — test(66-01): add failing pytest scaffold for DB-01/02/03/05 inclusion behaviors

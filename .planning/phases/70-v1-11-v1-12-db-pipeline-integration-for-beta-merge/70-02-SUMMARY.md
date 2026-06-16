---
phase: 70-v1-11-v1-12-db-pipeline-integration-for-beta-merge
plan: "02"
subsystem: firestarter_app/tools/check_dispatch.py, firestarter_app/tools/diff_db.py, firestarter_app/firestarter/data/chip_database.json, firestarter_app/tools/baseline/chip_database.baseline.json
tags: [db-pipeline, safety, gate, integration, regeneration]
dependency_graph:
  requires: [70-01-integrated-build_db.py]
  provides: [regenerated-744-chip-db, GATE-03-green, two-stage-diff-green, refreshed-baseline-anchor]
  affects: [chip_database.json, check_dispatch, diff_db, plan-03, plan-04]
tech_stack:
  added: []
  patterns: [structural-no-vpp-pin-gate, merged-rule-set-diff, two-stage-diff-Option-A]
key_files:
  created: []
  modified:
    - firestarter_app/tools/check_dispatch.py
    - firestarter_app/tools/diff_db.py
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_app/tools/baseline/chip_database.baseline.json
decisions:
  - "D-01 honored: all edits on v1.12-protocol-dispatch-hardening branch"
  - "SC#3 green: GATE-03 reports 0 novpp_in_eprom, 0 non_supported_dispatchable across 744 chips"
  - "SC#4 green: stage (a) 0 UNEXPLAINED vs v1.11 beta 743-chip DB; stage (b) identity diff 0 UNEXPLAINED"
  - "D-05 honored: baseline anchor refreshed from 734 to 744 chips"
  - "Pitfall 5 resolved: beta structural _build_no_vpp_pin_set guard restored to check_dispatch.py"
  - "Pitfall 7 resolved: RULE_PHASE66 placed last in _classify_diff, after BUG_A_ETYPE/BUG_B_VPP"
metrics:
  duration: "~8min"
  completed: "2026-06-16T07:52:04Z"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 4
---

# Phase 70 Plan 02: Validation Gates + DB Regeneration Summary

**One-liner:** Integrated check_dispatch.py (v1.12 support_status machinery + beta structural no-vpp-pin guard) and diff_db.py (merged BUG_A_ETYPE/BUG_B_VPP/RULE_PHASE66 rule set); regenerated 744-chip chip_database.json; GATE-03 exits 0 with 0 violations; two-stage diff exits 0 with 0 UNEXPLAINED on both stages; baseline anchor refreshed to 744 chips.

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Integrate check_dispatch.py + diff_db.py | 65a1763 | tools/check_dispatch.py, tools/diff_db.py |
| 2 | Regenerate DB, run GATE-03 + two-stage diff, refresh baseline | b7368ad | firestarter/data/chip_database.json, tools/baseline/chip_database.baseline.json |

## What Changed

### check_dispatch.py (v1.12 body + restored beta structural guard)

**Restored from beta (6 mandatory GATE-03 structural guard elements):**
- `PINOUTS_FILE` constant (env-overridable, mirrors build_db.py path pattern)
- `_build_no_vpp_pin_set(pinouts_file)` function — reads pinouts.json, returns set of pinout keys with no `vpp-pin`
- `no_vpp_pin_pinouts = _build_no_vpp_pin_set(PINOUTS_FILE)` at start of main()
- `novpp_in_eprom = []` bucket
- Per-chip: `if handler == "configure_eprom" and pinout in no_vpp_pin_pinouts:` structural guard
- FAIL block reporting `novpp_in_eprom` (with count and first 20 entries)

**Restored from beta (set semantics fix):**
- `_28C_EEPROM_HAZARD_ETYPES = {"Flash/EEPROM", "EEPROM"}` — set membership replaces `== "Flash/EEPROM"` string comparison

**Removed (DEC-05 compliance):**
- `0x35` and `0x39` removed from `_ALGO_MEM_TYPE`
- `0x35` and `0x39` removed from `KNOWN_PROTOCOLS`
- `0x35` and `0x39` removed from `dispatch()` (was `protocol in (0x05, 0x35, 0x39)` → now `protocol == 0x05`)

**Kept from v1.12 (support_status machinery retained):**
- `not_implemented` dispatch arm (protocol != 0 guard)
- D-10 assertion buckets: `missing_reason`, `pni_with_known_proto`, `non_supported_dispatchable`
- Updated FAIL/PASS report blocks for new buckets

### diff_db.py (merged rule set)

**Restored from beta:**
- `BUG_A_ETYPE` rationale + field paths `{("electrical", "type")}`
- `BUG_B_VPP` rationale + field paths `{("electrical", "vpp"), ("electrical", "vpp_mv")}`
- `type_diff` and `vpp_diff` variables in `_classify_diff`
- `BUG_A_ETYPE` and `BUG_B_VPP` checks in `_classify_diff` (priority 6 and 7, before RULE_PHASE66)

**Updated:**
- GATE-02 header comment: baseline count `734` → `744`
- `_classify_diff` priority order comment updated to document 8-step ordering

**Kept from v1.12 (RULE_PHASE66 retained, placed last):**
- `RULE_PHASE66` rationale + field paths remain unchanged
- RULE_PHASE66 is last in both `_RATIONALES` dict and `_classify_diff` (Pitfall 7 fix)

### chip_database.json (744 chips, regenerated)

`python tools/build_db.py` regenerated from infoic.xml snapshot (HTTPS fetch). Output: 744 chips (743 v1.11 chips + X88C64P). Key verification:
- `support_status` on every chip record
- `SST27VF512 vpp_mv=12000` (BUG-B preserved)
- `W27C512 pulse_duration="100 us"` (BUG-2 preserved)

### tools/baseline/chip_database.baseline.json (refreshed to 744 chips)

`cp firestarter/data/chip_database.json tools/baseline/chip_database.baseline.json` — old 734-chip pre-v1.11 anchor replaced with 744-chip integrated Phase 70 output.

## Gate Results

### GATE-03 (SC#3): check_dispatch.py

```
PASS: all 744 chips scanned; 730 supported; 14 chips confirmed non-dispatchable
(D-12: host guard covers non-supported chips with real handlers;
non-handler outcomes also safe); 0 non_supported_dispatchable
(gate GREEN because chip_resolver.resolve_chip refuses, not because sim pretends
mem_type=None); 0 dispatch regressions; 0 consistency violations
```

- 0 `novpp_in_eprom` (structural no-vpp-pin guard: PASS)
- 0 `non_supported_dispatchable` (SC#3 HARD inverse guard: PASS)
- 0 `missing_reason` (D-10 assertion 1: PASS)
- 0 `pni_with_known_proto` (D-10 assertion 2: PASS)
- 14 non-supported chips: correct (1 protocol-not-implemented X88C64P + 9 adapter-required + 4 vpp-exceeds-max)

### Stage (a) Diff: regenerated DB vs v1.11 beta 743-chip DB (SC#2/SC#4)

```
PASS: all 743 changed chips explained (1 new chips confirmed; 0 chips removed from baseline)
```

- 0 UNEXPLAINED
- 4 RULE_ALGO (M2716/M2732 vpp-exceeds-max: algo demoted to 0x00 — compound with RULE_PHASE66 secondary)
- 2 BUG_B_VPP (M2732A vpp correction — compound with RULE_PHASE66 secondary)
- 737 RULE_PHASE66 (support_status added to all 737 previously supported chips)
- 1 NEW chip: X88C64P,X88C64S (protocol-not-implemented; WARN: not a Rule 1 unblock — expected)
- 0 MISSING chips

### Stage (b) Diff: regenerated DB vs refreshed 744-chip baseline (SC#4)

```
PASS: all 0 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)
```

Identity diff — 0 UNEXPLAINED, 0 changed, 0 missing. Baseline matches regenerated DB exactly.

## Acceptance Criteria Verification

| Criterion | Result |
|-----------|--------|
| `tools/check_dispatch.py` and `tools/diff_db.py` parse without SyntaxError | PASS |
| check_dispatch.py contains `_build_no_vpp_pin_set`, `PINOUTS_FILE`, `novpp_in_eprom` | PASS |
| check_dispatch.py contains `not_implemented` (v1.12 dispatch arm retained) | PASS |
| check_dispatch.py has no `0x35`/`0x39` entries in `_ALGO_MEM_TYPE` (DEC-05) | PASS |
| diff_db.py contains `BUG_A_ETYPE`, `BUG_B_VPP`, `RULE_PHASE66` | PASS |
| diff_db.py GATE-02 header comment cites baseline count 744 | PASS |
| `python tools/build_db.py` exits 0; regenerated DB has exactly 744 chips | PASS |
| Every chip record has `support_status` field | PASS |
| `python tools/check_dispatch.py` exits 0 with PASS: 744 chips, 0 novpp_in_eprom, 0 non_supported_dispatchable | PASS |
| Stage (a): `FIRESTARTER_BASELINE_FILE=/tmp/v1.11-beta-db.json python tools/diff_db.py` exits 0, 0 UNEXPLAINED | PASS |
| SST27VF512 `vpp_mv=12000` (BUG-B preserved) | PASS |
| W27C512 `pulse_duration="100 us"` (BUG-2 preserved) | PASS |
| `tools/baseline/chip_database.baseline.json` has 744 chips (D-05) | PASS |
| Stage (b): `FIRESTARTER_BASELINE_FILE=tools/baseline/chip_database.baseline.json python tools/diff_db.py` exits 0, 0 UNEXPLAINED | PASS |

## Deviations from Plan

None. Both tasks executed exactly as specified.

The `novpp_in_eprom` bucket was also added to the FAIL block's `if` condition check (line 312), which is the minimal required plumbing to make the FAIL block work. This is part of the structural guard restoration (element 6 per 70-PATTERNS "GATE-03 Structural Guard — Must Not Be Lost") and is not a deviation.

The stage (a) diff shows a WARN for X88C64P "NOT a Rule 1 unblock" — this is expected and correct: X88C64P is a `protocol-not-implemented` NovRAM chip with `pinout=DIP24_6116` and `algo=0x34`, not a Rule 1 (DIP24_2816 EEPROM) unblock. The WARN is a diff_db.py cosmetic note, not a gate failure.

## Submodule Commit State

All commits made INSIDE the `firestarter_app` submodule on the `v1.12-protocol-dispatch-hardening` branch:

- `65a1763` — feat(70-02): integrate check_dispatch.py structural guard + diff_db.py merged rule set
- `b7368ad` — feat(70-02): regenerate 744-chip DB + refresh baseline anchor; GATE-03 + two-stage diff green

The meta-repo `firestarter_app` gitlink pointer has NOT been bumped (per plan instructions — do not bump gitlink until beta cut).

## Known Stubs

None. All gates are green; DB is fully regenerated; no placeholder logic.

## Threat Surface Scan

No new security-relevant surface introduced. All changes are to batch validation tools and the generated `chip_database.json` artifact. The structural guard (`_build_no_vpp_pin_set`/`novpp_in_eprom`) reduces the threat surface by catching type-string-independent VPP hazards.

T-70-04 (non-supported chip reaching configure_eprom): MITIGATED — GATE-03 exits 0 with 0 `non_supported_dispatchable`.
T-70-05 (configure_eprom chip on no-vpp-pin pinout): MITIGATED — `novpp_in_eprom=0` confirmed by GATE-03.
T-70-06 (silent decode/pinout regression): MITIGATED — stage (a) 0 UNEXPLAINED + SST27VF512 vpp_mv=12000 + W27C512 100us verified.
T-70-07 (unexplained DB change): MITIGATED — both stages 0 UNEXPLAINED with full rule coverage.

## Self-Check: PASSED

- `tools/check_dispatch.py` exists and passes `python3 -c "import ast; ast.parse(...)"`
- `tools/diff_db.py` exists and passes `python3 -c "import ast; ast.parse(...)"`
- `firestarter/data/chip_database.json` exists with 744 chips and support_status on every record
- `tools/baseline/chip_database.baseline.json` exists with 744 chips
- Commits `65a1763` and `b7368ad` exist on `v1.12-protocol-dispatch-hardening` branch

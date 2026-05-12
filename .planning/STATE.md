---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Safety Closure & Hardware Validation
status: executing
last_updated: "2026-05-12T08:37:00.661Z"
last_activity: 2026-05-12
progress:
  total_phases: 5
  completed_phases: 1
  total_plans: 5
  completed_plans: 3
  percent: 60
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-05-12

## Current Position

Phase: 02 (naming-cleanup-wire-key-minipro-references) — EXECUTING
Plan: 2 of 3
Status: Plan 02-01 complete; Plan 02-02 ready to execute
Last activity: 2026-05-12 -- Plan 02-01 (WIRE-01 atomic wire-key flip vpp -> vpp_mv) complete (firestarter@39b29a9 + firestarter_app@20cfe86)

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-11)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** Phase 02 — naming-cleanup-wire-key-minipro-references

- Intel-flash REQ-SAF-01 closure (VPP ADC compare in `flash_intel_write_init`)
- 28C chip-ID forward-compat (`eeprom28c_write_init` honouring `handle->chip_id`)
- Wire JSON `"vpp"` → `"vpp_mv"` rename (atomic Python + firmware sync)
- Retroactive `VERIFICATION.md` artifacts for Phases 01-10
- Physical-hardware validation of the four canon chip families on a RURP shield

## Roadmap Summary

| Phase | Name | Requirements |
|-------|------|--------------|
| 1 | Safety Closure (Intel-flash VPP + 28C chip-ID) | SAF-04, SAF-05, SAF-06 |
| 2 | Wire Protocol Rename (`vpp` → `vpp_mv`) | WIRE-01, WIRE-02 |
| 3 | Retroactive Verification (Phases 01-10) | VERIF-01..VERIF-10 |
| 4 | Hardware Validation (RURP shield) | HW-01..HW-05 |
| 5 | Milestone Close | DOC-01 |

## Milestone History

- **v1.0** — Protocol-Aware Programming Architecture (shipped 2026-05-11) —
  see `.planning/MILESTONES.md` + `.planning/milestones/v1.0-*.md`

## Accumulated Context

### Open Blockers

None.

### Resolved in v1.1

- WARNING-1 — Intel-flash write path missing VPP ADC compare → **CLOSED by Plan 01-01** (`flash_intel_check_vpp` + 5 Unity tests; 20/20 native tests passing)

### Open Warnings (now tracked as v1.1 phases)

- WARNING-2 — `eeprom_28c.cpp` ignores `handle->chip_id` → **CLOSED by Plan 01-02** (`eeprom28c_check_chip_id` A9-12V + 4 Unity tests; 24/24 native tests passing)
- WARNING-3 — wire JSON `"vpp"` key carries millivolts → **CLOSED at source level by Plan 02-01** (firmware `firestarter@39b29a9` atomic three-site flip in `json_parser.c` + Python `firestarter_app@20cfe86` emitter rename at `database.py:518`; both CLAUDE.md examples synced; 8/8 cross-sub-repo grep gates pass; `pio run -e uno/leonardo` both succeed; 25/25 native tests pass). WIRE-02 regression evidence still owed by Plan 02-03.
- WARNING-4 — `firestarter_test.sh` / `write_test.sh` reference deleted `database_generated.json` → **Phase 4 (HW-01)**

(Full audit trail: `.planning/milestones/v1.0-INTEGRATION-CHECK.md` and `.planning/milestones/v1.0-MILESTONE-AUDIT.md`.)

### Resolved Blockers (v1.0)

- BLOCKER-1 (Phase 12) — algorithm-based dispatch for protocols 0x05/0x06/0x07/0x08/0x0B
  and SRAM 0x0E/0x27/0x28/0x29

- BLOCKER-2 (Phase 12) — SRAM chips routed to `configure_eprom` with 12V VPP regulator
- WARNING-5 (Phase 13) — AT28C256/64 5V EEPROM 12V-on-A14 hazard via DB override

## Decisions (Phase 1)

- **D-04 (SAF-04):** `flash_intel_check_vpp` implemented as inline-copy static helper in `flash_intel.cpp` — `eprom_check_vpp` left byte-identical; shared helper extraction deferred to cleanup phase
- **D-05 override (SAF-05, load-bearing):** `eeprom28c_check_chip_id` uses A9-12V identification (RESEARCH.md datasheet evidence), NOT the AMD/SST JEDEC AA/55/90 sequence from CONTEXT.md D-05. JEDEC sequence would corrupt address 0x5555 on SDP-disabled AT28C parts.
- **ArduinoFake delay() + delayMicroseconds():** Any test suite that drives `operation_init` must mock BOTH `delay()` AND `delayMicroseconds()` in `setUp()` — fakeit aborts on unmocked virtuals
- **configure_memory() function-pointer overwrite:** `configure_memory()` overwrites `handle->firestarter_get_data` with `memory_get_data` before calling the specific handler. Tests that mock `firestarter_get_data` must RE-ASSIGN the mock pointer AFTER `configure_memory()` and before `operation_init()`.

## Decisions (Phase 2)

- **Plan 02-01 commit order — firmware first, Python second.** Recommended by Phase 2 RESEARCH.md "Cross-Sub-Repo Coordination Pattern"; SAF-04 (shipped Phase 1) makes either order safe via zero-init `handle->vpp_mv` VPP-HIGH guard (RESEARCH.md Pitfall #3). Both sub-repo commits land in the same wave: firmware `39b29a9`, then app `20cfe86`.
- **Plan 02-01 — rename, not delete, at `database.py:518`.** Honored RESEARCH.md "Factual Correction" over CONTEXT.md D-02's "delete `\"vpp\": vpp_mv,`" framing. The live wire today emits exactly one VPP key (`"vpp"` carrying integer mV); there is no second `"vpp_mv": ...,` line to delete. The correct edit is a one-character-class swap on a single line.
- **Plan 02-01 — firmware atomic three-site flip locked into ONE commit.** PROGMEM literal (`:62`) + dispatch table row (`:74`) + `extract_int` macro arg (`:309`) all flip in one firmware commit. Half-flipped state would silently drop the field (RESEARCH.md Pitfall #1).

## Operator Next Steps

- Plan 02-01 complete. WIRE-01 source-state contract locked (Python emits `"vpp_mv"`; firmware parses `"vpp_mv"`; both CLAUDE.md examples synced; all 8 grep gates pass; firmware builds + 25 native tests green).
- Run `/gsd-execute-plan 02-02` next (CLEAN-01 file rename `minipro_complete_db.json` -> `chip_database.json` via `git mv` + D-04 internal `vpp_volts` rename).
- Plan 02-03 still pending after that (CLEAN-02 attribution scrub + WIRE-02 `check_dispatch.py` augmentation + SC#5 CLI smoke).

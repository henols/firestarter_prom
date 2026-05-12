---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Safety Closure & Hardware Validation
status: planning
last_updated: "2026-05-12T07:57:37.766Z"
last_activity: 2026-05-12
progress:
  total_phases: 5
  completed_phases: 1
  total_plans: 2
  completed_plans: 2
  percent: 100
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-05-12

## Current Position

Phase: 2
Plan: Not started
Status: Ready to plan
Last activity: 2026-05-12

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-11)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** Phase 01 — safety-closure-intel-flash-vpp-28c-chip-id

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
- WARNING-3 — wire JSON `"vpp"` key carries millivolts → **Phase 2 (WIRE-01)**
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

## Operator Next Steps

- Phase 01 complete. All SAF requirements closed (SAF-04, SAF-05, SAF-06).
- Run `/gsd-execute-phase 02` to execute Phase 02 (Wire Protocol Rename vpp → vpp_mv).

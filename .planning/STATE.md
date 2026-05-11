---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Safety Closure & Hardware Validation
status: roadmapped
last_updated: "2026-05-11T20:30:00.000Z"
last_activity: 2026-05-11
progress:
  total_phases: 5
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-05-11

## Current Position

Phase: Not started (ROADMAP.md drafted; awaiting `/gsd-plan-phase 1`)
Plan: —
Status: Roadmap complete; ready for Phase 1 planning
Last activity: 2026-05-11 — v1.1 ROADMAP.md created (5 phases, 22 requirements, 100% coverage)

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-11)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** Closing v1.0 audit gaps:
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

### Open Warnings (now tracked as v1.1 phases)

- WARNING-1 — Intel-flash write path missing VPP ADC compare → **Phase 1 (SAF-04)**
- WARNING-2 — `eeprom_28c.cpp` ignores `handle->chip_id` → **Phase 1 (SAF-05)**
- WARNING-3 — wire JSON `"vpp"` key carries millivolts → **Phase 2 (WIRE-01)**
- WARNING-4 — `firestarter_test.sh` / `write_test.sh` reference deleted `database_generated.json` → **Phase 4 (HW-01)**

(Full audit trail: `.planning/milestones/v1.0-INTEGRATION-CHECK.md` and `.planning/milestones/v1.0-MILESTONE-AUDIT.md`.)

### Resolved Blockers (v1.0)

- BLOCKER-1 (Phase 12) — algorithm-based dispatch for protocols 0x05/0x06/0x07/0x08/0x0B
  and SRAM 0x0E/0x27/0x28/0x29
- BLOCKER-2 (Phase 12) — SRAM chips routed to `configure_eprom` with 12V VPP regulator
- WARNING-5 (Phase 13) — AT28C256/64 5V EEPROM 12V-on-A14 hazard via DB override

## Operator Next Steps

- Run `/gsd-plan-phase 1` to begin Phase 1 (Safety Closure — Intel-flash VPP + 28C chip-ID).

---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: milestone_complete
last_updated: "2026-05-11T09:43:00.000Z"
progress:
  total_phases: 12
  completed_phases: 11
  total_plans: 19
  completed_plans: 16
  percent: 84
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-05-11

## Current Position

Phase: 12 (close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0) — EXECUTING
Plan: 3 of 5
**Phase:** 12
**Last completed:** Plan 12-02 (firmware configure_memory protocol-prefix dispatch + [env:native] host stubs) — 2026-05-11T09:43Z
**Next action:** Execute Plan 12-03 (Python `database.py:_map_data` D3 algorithm→mem_type table)

## Completed

- [x] Codebase mapped (`.planning/codebase/` — 7 documents)
- [x] Domain research completed (`.planning/research/` — PROTOCOLS, HARDWARE, ECOSYSTEM, PITFALLS, CHIP_FAMILIES, ARCHITECTURE_PATTERNS, FEATURES)
- [x] PROJECT.md written
- [x] REQUIREMENTS.md written (13 requirements across 4 categories)
- [x] ROADMAP.md written (10 phases)

## Phases

| # | Name | Status |
|---|------|--------|
| 01 | Database Pipeline Fix | Complete ✓ |
| 02 | Firmware JSON Protocol Extension | Complete ✓ |
| 03 | UV-EPROM Algorithm Correctness | Complete ✓ |
| 04 | Flash AMD Sector Erase | Complete ✓ |
| 05 | Intel Flash Handler | Complete ✓ |
| 06 | EEPROM Page Write with DQ7 Polling | Complete ✓ |
| 07 | Chip ID Validation & Pre-Write Safety | Complete ✓ |
| 08 | Integration, Rebuild & Verification | Complete ✓ |
| 09 | Hardware Compatibility & Adapter Support | Complete ✓ |
| 10 | Static Pins, Multi-CE, Address Bus Correctness | Complete ✓ |
| 11 | Database Pipeline Cleanup | Planned |

## Key Decisions

- **Database source:** minipro `infoic.xml` via `parse_db_2.py` (not hand-curated JSON)
- **Wire protocol:** New explicit `algorithm` field (minipro `protocol_id` integer); `type` retained as fallback
- **Firmware dispatch:** On `algorithm`, not `type` enum
- **Packages in scope:** DIP 24, 28, 32 only
- **Hardware:** RURP shield — fixed 5V VCC, no 3.3V switching, 19-bit address bus (512KB max), 8-bit data bus
- **Phase 12 / Plan 02:** BLOCKER-1 + BLOCKER-2 closed at the firmware layer. `configure_memory` now exposes an explicit protocol-prefix `if-return` block for every KNOWN_PROTOCOLS entry (0x06 → flash3; 0x05/0x35/0x39 → flash4; 0x07/0x08/0x0B → eprom; 0x0E/0x27/0x28/0x29 → sram); mem_type chain preserved as legacy fallback. Orphan constant `TYPE_FLASH_TYPE_2` deleted. Both AVR targets build clean (Uno +256B, Leonardo +256B flash).
- **Phase 12 / Plan 02:** Absorbed Wave 0's deferred host-mocking work — added `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` (no-op `rurp_*` + `LOG_*_MSG` PROGMEM globals) plus `[env:native]` `src_filter = +<proms/>` + `test_build_src = yes`. `pio test -e native -f "*test_dispatch*"` now reports 15/15 PASS (flipping 11 protocols from RED to GREEN).

## Key Files

- `firestarter_app/firestarter/data/minipro_complete_db.json` — generated database (do not edit by hand)
- `firestarter_app/tools/parse_db_2.py` — database generation pipeline
- `firestarter_app/firestarter/data/pinouts.json` — physical DIP pin mappings
- `firestarter_app/firestarter/database.py` — runtime DB loader + pin translator
- `firestarter_app/firestarter/constants.py` — Python-side constants (keep in sync with firmware)
- `firestarter/src/proms/memory.cpp` — firmware algorithm dispatch
- `firestarter/include/firestarter.h` — `firestarter_handle_t` struct (add `algorithm` field here)
- `firestarter/include/firestarter.h` — `bus_config_t` struct

## Accumulated Context

### Roadmap Evolution

- Phase 12 added: Close gap: BLOCKER-1 — algorithm-based dispatch for protocols 0x05/0x06/0x07/0x08/0x0B (and SRAM 0x0E/0x27/0x28/0x29) — either extend memory.cpp protocol-prefix dispatch or fix database.py:_map_data mem_type translation

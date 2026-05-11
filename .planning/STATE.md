---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: milestone_complete
last_updated: "2026-05-11T09:27:30.740Z"
progress:
  total_phases: 12
  completed_phases: 12
  total_plans: 19
  completed_plans: 19
  percent: 100
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-05-11

## Current Position

Phase: 12 (close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0) — READY FOR VERIFICATION
Plan: 5 of 5 (all complete)
**Phase:** 12
**Last completed:** Plan 12-05 (`firestarter/CLAUDE.md` dispatch table + native test env documentation) — 2026-05-11T09:33Z
**Next action:** Run `/gsd-verify-work` on Phase 12 (full suite: `pio run -e uno && pio run -e leonardo && python3 firestarter_app/tools/check_dispatch.py && pio test -e native`)

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
- **Phase 12 / Plan 03:** BLOCKER-1 closed at the Python host layer. `firestarter_app/firestarter/database.py:_map_data` now drives `mem_type` from a new module-level `_ALGO_MEM_TYPE` table (13 entries from CONTEXT.md D3) instead of the brittle `electrical.type` substring branch. Legacy substring branch preserved for `algorithm == 0`/absent fallback (user-override DB entries). `protocol_id` read moved up 9 lines so the new lookup can reference it; `info_flags` block untouched. `check_dispatch.py` still PASSes 743/743 chips, 0 SRAM→eprom routes. Spot-checks: W27C512 type 2→1, AM29F040 2→3, AE29F1008 2→5, 6116 1→4, DS1245AB(RW) 1→4.
- **Phase 12 / Plan 04:** BLOCKER-2 closed at the database-pipeline layer. `firestarter_app/tools/build_db.py` now derives `electrical.type` via an explicit if/elif/else chain (SRAM proto_ids {0x0E,0x27,0x28,0x29} → "SRAM"; else flags & 0x10 → "Flash/EEPROM"; else "UV-EPROM") hoisted out of the inline ternary. Regenerated `minipro_complete_db.json` contains exactly 52 SRAM-tagged chips (matches RESEARCH.md baseline to the chip; algorithm counts 0x05=27/0x06=190/0x07=237/0x08=127/0x0B=53/0x0D=18/0x0E=20/0x10=39/0x27=2/0x28=10/0x29=20 all exact). DB diff: 52 insertions, 52 deletions (one line per SRAM chip). `check_dispatch.py` PASSes 743/743 chips, 0 SRAM→eprom routes. End-to-end BLOCKER-2 fix complete across firmware (Plan 02) + host (Plan 03) + DB (Plan 04) layers.
  - **Phase 12 / Plan 05:** Phase 12 AC-8 closed (documentation). `firestarter/CLAUDE.md` updated to match the post-Phase-12 firmware: 11-step dispatch list mirroring `memory.cpp:configure_memory` line-for-line (six protocol-prefix steps for every KNOWN_PROTOCOLS entry + four mem_type fallback steps + error); Algorithm Handlers table gained an SRAM row (0x0E/0x27/0x28/0x29 → `sram.cpp`, BLOCKER-2 mitigation) and a 0x39 row (→ `flash_type_4.cpp`, future-proofed, no chips in current DB). Added new `Native (Host) Test Environment` section documenting `[env:native]` config, `pio test -e native -f "*test_dispatch*"` invocation, and the `host_stubs.cpp` / `avr/pgmspace.h` shim pattern under `test/native/avr/test_dispatch/`. All `TYPE_FLASH_TYPE_2` references purged. Phase 12 ready for `/gsd-verify-work`.

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

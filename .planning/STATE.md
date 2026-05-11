---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: milestone_complete
last_updated: "2026-05-11T19:44:30.000Z"
progress:
  total_phases: 13
  completed_phases: 13
  total_plans: 22
  completed_plans: 22
  percent: 100
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-05-11

## Current Position

Phase: 13 (close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we) — COMPLETE
Plan: Not started
**Phase:** 13
**Last completed:** Plan 13-03 (documentation plane — 20-line "Protocol overrides (WARNING-5)" paragraph added to `firestarter_app/CLAUDE.md` Database Pipeline section between "Known protocols" line and `### Constants`; cross-references `.planning/v1.0-MILESTONE-AUDIT.md` and `tools/check_dispatch.py` guard) — 2026-05-11T19:44Z
**Next action:** Phase 13 complete. WARNING-5 closed across all three planes (source/Plan 02 + regression/Plan 01 + documentation/Plan 03). Run `/gsd-verify-work` to finalize phase verification.

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
- **Phase 13 / Plan 01:** WARNING-5 regression guard added to `firestarter_app/tools/check_dispatch.py`. New module-top constant `_28C_EEPROM_HAZARD_PINOUT = "DIP28_2764"` + `eeprom28c_in_eprom` violation list + per-chip pinout+electrical.type check structurally parallel to the existing `_SRAM_PROTOCOLS` BLOCKER-2 guard. On the current (pre-fix) DB the guard FAILs with exit 1 and exactly 23 violations across 7 manufacturers (10 ATMEL + 7 MICROCHIP + 2 NEC + 2 XICOR + 1 ST + 1 EXEL) — proving the pinout-based discriminator catches chips a name-prefix discriminator would miss (13 of 23). Existing SRAM guard + `dispatch()` function left byte-identical (diff is purely additive). Commits: submodule `firestarter_app` at 6c35587 + outer-repo pointer-bump dd8d372 + SUMMARY 2c50cbf. Plan 02 will flip the gate to PASS via `_PROTOCOL_OVERRIDES` in `build_db.py`.
- **Phase 13 / Plan 02:** WARNING-5 closed at the database-pipeline layer. Inline 3-predicate conditional in `firestarter_app/tools/build_db.py` main() between the `_etype` derivation and the `chip_entry = {` dict literal: when `pinout_key == "DIP28_2764" AND proto_id == 0x07 AND _etype == "Flash/EEPROM"` the override flips `proto_id = 0x0D` and logs an `INFO:` stderr line. No module-top constant introduced (matches the Phase 12 Plan 04 SRAM inline-literal precedent). Regenerated `minipro_complete_db.json`: 23 chips moved from algorithm=0x07 → 0x0D across 6 manufacturer families (ATMEL=10, MICROCHIP memory=7, NEC=2, XICOR=2, ST=1, EXEL=1); algos[0x07] 237→214 (Δ=-23); algos[0x0D] 18→41 (Δ=+23); JSON diff 46+/46-. AT28C256 verified at 0x0D; W27C512 verified UNCHANGED at 0x07 (regression intact). `check_dispatch.py` now PASSes 743/743 chips with the three-clause PASS line (0 SRAM + 0 DIP28_2764 hazards). Unity dispatch tests 15/15 GREEN (incl. `test_protocol_0x0D_dispatches_eeprom28c`). Both AVR builds SUCCESS with flash delta = 0 bytes (Uno 24852B, Leonardo 27218B — no firmware sources changed). Defense-in-depth grep on `eeprom_28c.cpp` confirms zero VPP-regulator references. Commits: submodule `firestarter_app` at fe7e14b + outer-repo pointer-bump 4d5c3d2 + SUMMARY 770b64f. REQ-FW-03 and REQ-SAF-01 now reachable end-to-end for the 23 affected chips.
- **Phase 13 / Plan 03:** WARNING-5 closed at the documentation plane. Added a 20-line "Protocol overrides (WARNING-5)" paragraph to `firestarter_app/CLAUDE.md` Database Pipeline section between the existing "Known protocols" hex-list line and the `### Constants` subsection heading. Paragraph documents (1) the override location in `build_db.py`, (2) the 3-predicate condition (`DIP28_2764 + 0x07 + Flash/EEPROM`), (3) the algorithm flip to `0x0D` (EEPROM_POLL → `configure_eeprom28c` instead of `configure_eprom`), (4) the rationale (socket pin 1 = A14 on 28C-family 5V EEPROMs, so `P1_VPP_ENABLE` 12V is a hardware-damage path; `configure_eeprom28c` is pure 5V VCC with no VPP regulator engagement), (5) the ~23-chip / 6-manufacturer scope (ATMEL/MICROCHIP/NEC/XICOR/ST/EXEL) plus the 7-chip regression-safe set on DIP28_27512/DIP28_27256, (6) the audit pointer to `.planning/v1.0-MILESTONE-AUDIT.md` WARNING-5 entry and the phase folder, and (7) the `tools/check_dispatch.py` regression-guard pointer. CLAUDE.md grew 81→101 lines (+20 additive, no removals). Submodule commit `07ae624` + outer-repo pointer-bump `39d7c1d`. WARNING-5 now closed across all three planes — source (Plan 02), regression (Plan 01), documentation (Plan 03).

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
- Phase 13 added: Close gap: WARNING-5 — AT28C256/64 5V EEPROM override (12V on /WE on write)

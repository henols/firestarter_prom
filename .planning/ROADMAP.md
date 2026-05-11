# Roadmap

**Project:** Firestarter — Protocol-Aware Programming Architecture

---

## Phase 01 — Database Pipeline Fix
**Goal:** `parse_db_2.py` produces a correct, trustworthy `minipro_complete_db.json` with no guessing.

**Success criteria:**
- Every chip entry has an explicit `algorithm` integer field (minipro `protocol_id`)
- 28-pin EPROMs are split across `DIP28_27512`, `DIP28_27256`, `DIP28_2764` correctly by variant
- VPP is stored in decoded millivolts (not raw hex), never zero by default
- Entries with unknown `protocol_id` are logged and skipped, not silently included
- DIP 24/28/32 filter is clean; no SMD/PLCC/serial-interface chips in output

**Requirements:** REQ-DB-01, REQ-DB-02, REQ-DB-03, REQ-DB-04

---

## Phase 02 — Firmware JSON Protocol Extension
**Goal:** Firmware accepts an explicit `algorithm` field and never crashes on unknown fields.

**Success criteria:**
- JSON parser skips unknown keys instead of returning error
- `algorithm` integer field is parsed from command JSON and stored in `firestarter_handle_t`
- Existing `type`-based dispatch still works as fallback when `algorithm` is absent
- Old Python + new firmware: no regression
- New Python + old firmware: no crash (unknown field silently ignored)

**Requirements:** REQ-SER-01, REQ-SER-02

---

## Phase 03 — UV-EPROM Algorithm Correctness
**Goal:** All three UV-EPROM protocols execute with correct pulse timing and VPP routing.

**Success criteria:**
- `EPROM_STD` (0x07): 1ms intelligent programming pulse, VPE_TO_VPP path, 13V VPP
- `EPROM_QUICK` (0x08): 100µs pulse, VPE_TO_VPP, correct 32-pin address bus
- `EPROM_LEGACY` (0x0B): 500µs pulse, direct VPE_ENABLE path, 24-pin, A13 tied to VCC
- A 27C512, a 27C256, and a 2732 can each be written and verified correctly
- VPP is validated via ADC before first pulse for all three (REQ-SAF-01)

**Requirements:** REQ-FW-01, REQ-SAF-01

---

## Phase 04 — Flash AMD Sector Erase
**Goal:** FLASH_AMD_ALT supports sector erase in addition to chip erase.

**Success criteria:**
- Sector erase command sequence (unlock + 0x30 to sector address) implemented in firmware
- Python CLI exposes sector erase as an operation
- A 29F040 or SST39SF040 sector can be erased and re-programmed without touching adjacent sectors
- Blank check is performed before write (REQ-SAF-03)

**Requirements:** REQ-FW-04, REQ-SAF-03

---

## Phase 05 — Intel Flash Handler
**Goal:** New firmware algorithm for Intel-style command-register NOR flash.

**Success criteria:**
- `configure_flash_intel()` dispatched when `algorithm == 0x10`
- Program sequence: write 0x40, write data, poll status register bit 4 (ready)
- Erase sequence: write 0x20, write 0xD0, poll until status bit 7 set
- 0xFF reset issued on any error
- Status register bit 4 (VPP error) and bit 5 (program error) reported as distinct error messages
- 12V VPP applied to pin 1 (`P1_VPP_ENABLE`) — not `VPE_TO_VPP`
- A HN28F101 or compatible Intel-style flash can be read, erased, written, and verified

**Requirements:** REQ-FW-02

---

## Phase 06 — EEPROM Page Write with DQ7 Polling
**Goal:** Parallel EEPROM (AT28Cxxx) writes using internal write timing, not fixed delays.

**Success criteria:**
- `EEPROM_POLL` (0x0D) uses DQ7 polling loop to detect write completion
- SDP disable sequence applied before first write (unlock write to 0x5555, 0x2AAA, 0x5555)
- Page write (up to 64 bytes) handled as a single operation with polling after page commit
- AT28C256 with factory SDP enabled can be written successfully
- Blank check performed before write (REQ-SAF-03)

**Requirements:** REQ-FW-03, REQ-SAF-03

---

## Phase 07 — Chip ID Validation & Pre-Write Safety
**Goal:** Chip ID is read and validated before every write where the algorithm supports it.

**Success criteria:**
- Before any write, if `flags & MP_ID_MASK`: read electronic ID and compare against `chip_id` from database
- Mismatch aborts with "chip ID mismatch: expected 0xXXXX, got 0xYYYY"
- Correct A9_VPP_ENABLE sequence used for 27Cxxx chip ID read
- VPP ADC check covers all chips including those with `chip_id == 0`
- REQ-SAF-01 and REQ-SAF-02 verified end-to-end with W27C512, 29F040, AT28C256

**Requirements:** REQ-SAF-01, REQ-SAF-02

---

## Phase 08 — Integration, Rebuild & Verification
**Goal:** Regenerate database, run end-to-end tests, confirm all chip families work correctly.

**Success criteria:**
- `parse_db_2.py` run against latest `infoic.xml` produces correct `minipro_complete_db.json`
- All 4 chip families tested on hardware: 27C512 (EPROM_STD), 27C040 (EPROM_QUICK), 29F040 (FLASH_AMD_ALT), AT28C256 (EEPROM_POLL)
- `firestarter_test.sh` passes for all test chips
- No regressions in existing `verified.txt` chips (W27C512, SST27SF512, M2764A, etc.)
- CLAUDE.md updated in both sub-repos to reflect new algorithm field and dispatch architecture

**Requirements:** All

---

## Phase 09 — Hardware Compatibility & Adapter Support
**Goal:** Surface hardware compatibility in the CLI: warn when a chip has no valid pinout, and add `--adapter` to print the physical pin-to-signal table for building wiring adapters.

**Success criteria:**
- `firestarter search <query>` marks chips without a bus-config with a visible `[no pinout]` indicator
- `firestarter info <chip>` prints a clear warning when no bus-config is available instead of silently returning incomplete data
- `firestarter info <chip> --adapter` prints a two-column table of physical DIP pin → RURP signal for the chip's pinout variant
- The adapter table is derived entirely from `pinouts.json` — no hardcoded signal names
- Chips that plug in directly (no adapter needed) still display the table confirming their wiring

**Requirements:** REQ-UX-01, REQ-UX-02

---

## Phase 10 — Static Pins, Multi-CE, and Address Bus Correctness
**Goal:** Add `static_high_mask` to `bus_config_t` so pins that must always be driven HIGH
(second CE, tied-high NC pins) are handled by data rather than firmware hacks. Clean up the
dead condition in `mem_util_calculate_top_address_register`.

**Success criteria:**
- `bus_config_t` has a `static_high_mask` field; `mem_util_remap_address_bus` ORs it into every address unconditionally
- `pinouts.json` has `static-high-pins` on DIP24_2716, DIP24_2732 (and any other pinouts that need it); these replace the hardcoded `ADDRESS_LINE_13` logic
- `mem_util_calculate_msb_register` no longer has the special-case `if (handle->pins == 24)` line
- `mem_util_calculate_top_address_register` dead condition replaced with `if (handle->pins < 32)` plus explanatory comment
- `parse_bus_config()` parses `static-high` array from bus-config JSON
- `database.py` `get_bus_config()` outputs `static-high` when `static-high-pins` present in pinout
- Both firmware targets build clean

**Requirements:** REQ-FW-05, REQ-FW-06

---

## Phase 11 — Database Pipeline Cleanup
**Goal:** Consolidate the database build pipeline to a single canonical tool. Remove the legacy `parse_db.py` and its stale outputs, rename `parse_db_2.py` to `build_db.py`, and ensure the source `infoic.xml` is fetched from upstream at run time and never stored or committed in this project.

**Success criteria:**
- `firestarter_app/tools/parse_db.py` is removed
- `firestarter_app/tools/parse_db_2.py` is renamed to `build_db.py` with no behavior change beyond the rename
- `firestarter_app/tools/infoic.xml` and `tools/infoic2.xml` are deleted from the working tree
- `firestarter_app/tools/verified.txt` is removed (only consumer was `parse_db.py`)
- Stale legacy outputs `firestarter_app/firestarter/data/database_generated.json` and `pin-maps.json` are removed
- `firestarter_app/.gitignore` ignores `tools/infoic*.xml` so the file can never be re-committed
- `build_db.py` continues to fetch `infoic.xml` from `https://gitlab.com/DavidGriffith/minipro/-/raw/master/infoic.xml` at run time, parses it in memory, and writes only `minipro_complete_db.json`
- All references to `parse_db_2.py` are updated to `build_db.py` in `firestarter_app/CLAUDE.md` and `firestarter_app/firestarter/database.py` comments
- `python tools/build_db.py` runs cleanly from a fresh checkout (no local `infoic.xml` required) and produces a `minipro_complete_db.json` byte-identical to the previous `parse_db_2.py` output on the same upstream XML

**Requirements:** REQ-DB-05

---

## Phase 12 — Close BLOCKER-1: Algorithm-Based Dispatch for Missing Protocols

**Goal:** Close gap: BLOCKER-1 — algorithm-based dispatch for protocols 0x05/0x06/0x07/0x08/0x0B (and SRAM 0x0E/0x27/0x28/0x29). Either extend `memory.cpp` protocol-prefix dispatch or fix `database.py:_map_data` mem_type translation so chips with these protocol IDs route to a working handler.

**Requirements:** REQ-FW-01, REQ-FW-04, REQ-SER-01

**Depends on:** Phase 11

**Plans:** 5/5 plans complete

Plans:
- [x] 12-01-PLAN.md — Wave 0: Test infra + regression scan (`[env:native]`, `check_dispatch.py`, `test_configure_memory.cpp`)
- [x] 12-02-PLAN.md — Wave 1: C++ dispatch extension in `memory.cpp` (D2 steps 3-6 + remove TYPE_FLASH_TYPE_2)
- [x] 12-03-PLAN.md — Wave 1: Python `_ALGO_MEM_TYPE` table + `_map_data` algorithm-driven mem_type derivation (D3)
- [x] 12-04-PLAN.md — Wave 2: `build_db.py` SRAM proto_id detection (D4) + regenerate DB + end-to-end regression
- [x] 12-05-PLAN.md — Wave 2: Doc sync — `firestarter/CLAUDE.md` dispatch table + handler table aligned with source (AC-8)

---

## Phase 13 — Close gap: WARNING-5 — AT28C256/64 5V EEPROM override (12V on /WE on write)

**Goal:** Make 23 hazardous DIP28_2764 5V EEPROMs (ATMEL AT28C/BV, MICROCHIP 28Cxx, NEC UPD28C, ST M28256, XICOR X28C, EXEL XLE2865A — currently mistagged `algorithm=0x07` + `electrical.type='Flash/EEPROM'` in upstream minipro) route to `configure_eeprom28c` (5V, no VPP regulator) instead of `configure_eprom` (which would assert 12V `P1_VPP_ENABLE` on socket pin 1 = A14 address line = hardware damage). Fix is data-layer only: an inline 3-predicate conditional in `build_db.py` flips `algorithm` to `0x0D` at DB-generation time; no firmware changes needed. Verified by `check_dispatch.py` PASS (0 DIP28_2764 Flash/EEPROM chips routing to `configure_eprom`) and a 23-chip diff in the regenerated `minipro_complete_db.json`.

**Requirements:** REQ-FW-03, REQ-SAF-01

**Depends on:** Phase 12

**Plans:** 3 plans

Plans:
- [ ] 13-01-PLAN.md — Wave 1: Add `_28C_EEPROM_HAZARD_PINOUT` regression guard to `check_dispatch.py` (controlled FAIL with 23 violations on current DB)
- [ ] 13-02-PLAN.md — Wave 2: Inline `pinout_key=DIP28_2764 + proto_id=0x07 + _etype=Flash/EEPROM` override block in `build_db.py` flips 23 chips to `algorithm=0x0D`, regenerate DB, full regression green (check_dispatch PASS, Unity 15/15, AVR builds clean)
- [ ] 13-03-PLAN.md — Wave 3: Document WARNING-5 override in `firestarter_app/CLAUDE.md` Database Pipeline section

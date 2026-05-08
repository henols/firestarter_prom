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

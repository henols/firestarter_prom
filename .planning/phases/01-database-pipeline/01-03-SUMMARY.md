---
phase: 01-database-pipeline
plan: 03
status: complete
files_modified:
  - firestarter_app/firestarter/data/minipro_complete_db.json
---

# Phase 01 Plan 03: Rebuild Database — Summary

## What was done

Ran `parse_db_2.py` (fixed by Plan 01-01) to regenerate `minipro_complete_db.json` from the upstream minipro `infoic.xml`. All structural assertions passed.

## Results

**Total chips:** 743

**Pinout keys in output:** `DIP24_2716`, `DIP28_27256`, `DIP28_27512`, `DIP28_2764`, `DIP32_STD`

Note: `DIP24_2732` does not appear — no 24-pin chips with the 2732 variant flag survived the DIP/memory-type filter in the current infoic.xml dataset.

**Spot-check results:**

| Chip | algorithm | vpp_mv | pinout |
|---|---|---|---|
| W27C512 | 0x07 (EPROM_STD) | 12000 | DIP28_27512 ✓ |
| AM27C256 | 0x07 (EPROM_STD) | 13000 | DIP28_27256 ✓ |
| AM2764A | 0x07 (EPROM_STD) | 13000 | DIP28_2764 ✓ |
| AT28C256 | 0x07 | 12000 | DIP28_2764 |
| SST39SF040 | 0x06 (FLASH_AMD_ALT) | 12000 | DIP32_STD ✓ |

**Note on AT28C256:** minipro's infoic.xml assigns protocol_id 0x07 to AT28C256, not 0x0D (EEPROM_POLL). This is stored faithfully. The correct EEPROM_POLL dispatch is a Phase 03/06 firmware concern — Phase 01 just stores what minipro says.

## WARN output from pipeline

Unknown protocols correctly skipped with WARN:
- `0x04` — Atmel AT45D/AT45DB SOIC28 DataFlash (serial SPI, not parallel — correct to exclude)
- `0x11` — ST M50FW040/M50FW080 (FWH interface — correct to exclude)
- `0x0A` — TMS87C257@PLCC32 (PLCC — out of scope)
- `0x34` — X88C64P/X88C64S (out of scope)

## Deviations from plan

None. Pipeline ran to completion without errors.

## Phase 01 success criteria — PASSED

- [x] `programming.algorithm` is always an integer (minipro protocol_id)
- [x] `electrical.vpp_mv` is always an integer in millivolts
- [x] W27C512 → `DIP28_27512`, 27C256 → `DIP28_27256`
- [x] Unknown protocol_id values produce stderr WARNs and are excluded
- [x] 743 chips in output, all from DIP 24/28/32 packages

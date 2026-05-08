---
phase: 01-database-pipeline
plan: 01
status: complete
files_modified:
  - firestarter_app/tools/parse_db_2.py
  - firestarter_app/firestarter/data/minipro_complete_db.json
---

# Summary: Plan 01-01 — Fix parse_db_2.py

## What was changed in parse_db_2.py

### Algorithm as integer (Task 1)
- `chip_entry["programming"]["algorithm"]` now stores the raw integer `proto_id` instead of `PROTOCOL_MAP.get(proto_id, proto_id)`.
- `PROTOCOL_MAP` is retained in the script for future logging/reference use.

### VPP in millivolts (Task 1)
- Added `VPP_MV` dict mapping voltage codes (0x00–0xF0) to integer millivolt values.
- Added `"vpp_mv": VPP_MV.get(voltages & 0xFF, 0)` to the `electrical` dict, alongside the existing `"vpp"` string field.

### Protocol validation (Task 1)
- Added `KNOWN_PROTOCOLS` set at module level.
- Added skip-with-warning for chips whose `protocol_id` is not in `KNOWN_PROTOCOLS`.

### Path handling (deviation — bug fix applied)
- `OUTPUT_FILE` was `"../firestarter/data/minipro_complete_db.json"` (relative to CWD), which failed when running from the repo root.
- `PINOUT_FILE` was `"firestarter/data/pinouts.json"` (relative to `firestarter_app/`), also CWD-sensitive.
- Both paths are now resolved relative to `__file__` using `os.path.dirname(__file__)`, making the script runnable from any working directory.

### DIP28_VARIANT_MAP (Task 2)
- Added `DIP28_VARIANT_MAP = {0x10: "DIP28_27512", 0x11: "DIP28_27256", 0x12: "DIP28_2764", 0x13: "DIP28_2764"}` at module level.
- `resolve_pinout_key()` 28-pin branch now uses `DIP28_VARIANT_MAP.get(variant & 0xFF, "DIP28_2764")` instead of the previous if-chain.
- 24-pin and 32-pin logic is unchanged.

### Pinout key validation (Task 2)
- `VALID_PINOUT_KEYS` loaded from `pinouts.json` at module startup.
- `resolve_pinout_key()` emits a WARN to stderr if a resolved key is not in `VALID_PINOUT_KEYS`.
- No invalid keys were found during the run.

## Results

- **Total chip count**: 743
- **Pinout keys present in output**: `DIP24_2716`, `DIP28_27256`, `DIP28_27512`, `DIP28_2764`, `DIP32_STD`
  - Note: `DIP24_2732` did not appear — no 24-pin variant==1 chips passed the strict DIP/memory/type filter.

## WARN output from pipeline run

Unknown protocol_id chips skipped (all SPI/serial flash variants correctly excluded):

- `AT45D021@SOIC28`, `AT45D041@SOIC28`, `AT45D081@SOIC28` — protocol_id 0x04 (×2 each, duplicate DB entries)
- `AT45DB021`, `AT45DB041`, `AT45DB081`, `AT45DB161`, `AT45DB321B`, `AT45DB321C` — protocol_id 0x04 (×2 each)
- `M50FW040`, `M50FW080` — protocol_id 0x11 (FLASH_FWH, not in KNOWN_PROTOCOLS) (×2 each)
- `TMS87C257@PLCC32` — protocol_id 0x0A (×1)
- `X88C64P@DIP24,X88C64S@SOIC24` — protocol_id 0x34 (×1)

## Deviations from plan

1. **Both tasks committed in a single commit** (`8241257`): All changes were implemented before the first commit since the files were untracked new files (not pre-existing). A second commit for Task 2 would have been a no-op as the JSON was bit-for-bit identical on re-run. The single commit contains all changes from both tasks.

2. **Bug fix applied (path handling)**: `OUTPUT_FILE` and `PINOUT_FILE` used inconsistent relative paths that failed when running from the repo root as instructed. Fixed to use `__file__`-relative paths. This was a necessary fix to make the script executable per the plan's verification commands.

3. **`0x11` (FLASH_FWH) not in KNOWN_PROTOCOLS**: The existing `PROTOCOL_MAP` includes `0x11: "FLASH_FWH"` but the plan's `KNOWN_PROTOCOLS` set does not include `0x11`. Two ST chips (`M50FW040`, `M50FW080`) were skipped with warnings. This matches the plan spec exactly — the plan's `KNOWN_PROTOCOLS` set was applied as written.

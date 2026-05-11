---
phase: 07-chip-id-safety
plan: 01
status: complete
commit: 590cb41
---

# 07-01 Summary: Intel 28F Chip ID Validation

## What was changed

**File:** `firestarter/src/proms/flash_intel.cpp` — 23 insertions

### Changes applied

1. **Forward declaration** (line 22): Added `void flash_intel_check_chip_id(firestarter_handle_t* handle);` after `flash_intel_cleanup` declaration.

2. **CMD_CHECK_CHIP_ID case in configure_flash_intel()** (lines 39–43): Added case that sets init and end to NULL and dispatches main to `flash_intel_check_chip_id`.

3. **Chip ID check in flash_intel_write_init()** (lines 51–55): When `handle->chip_id > 0`, calls `flash_intel_check_chip_id()` before erase/blank-check; returns early on `RESPONSE_CODE_ERROR`.

4. **flash_intel_check_chip_id() implementation** (lines 115–123): Writes 0x90 to enter Intel autoselect mode, reads manufacturer ID from 0x0000 and device ID from 0x0001, writes 0xFF to exit. Compares combined 16-bit chip_id against `handle->chip_id`; on mismatch emits WARNING (FLAG_FORCE set) or ERROR, matching the flash3 message format exactly.

## Build results

Both targets built cleanly with no warnings:
- `pio run -e uno` → [SUCCESS]
- `pio run -e leonardo` → [SUCCESS]

## No deviations

Implementation matches the plan spec exactly. Message format `"Chip ID %#04x dont match expected ID %#04x"` matches flash3 convention. VPP is active during chip ID read because `flash_intel_write_init()` enables it before calling `flash_intel_check_chip_id()`, and the standalone `CMD_CHECK_CHIP_ID` path (via configure_flash_intel) does not enable VPP — consistent with how flash3 handles this (flash3_check_chip_id_execute also does not enable VPP itself).

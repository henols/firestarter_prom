---
phase: 04-flash-sector-erase
plan: 01
status: complete
files_modified:
  - firestarter/src/proms/flash_type_3.cpp
---
# Phase 04 Plan 01: Flash AMD Sector Erase (Firmware) — Summary
## What was changed
Added `flash3_sector_erase()` function and updated `flash3_erase_execute()` in `firestarter/src/proms/flash_type_3.cpp`:

1. Added forward declaration for `flash3_sector_erase()` near the top with other forward declarations.
2. Updated `flash3_erase_execute()` to branch on `handle->address`: non-zero triggers sector erase at that address; zero falls through to the existing chip erase path.
3. Added `flash3_sector_erase()` which builds a 6-entry AMD sector erase byte-flip sequence on the stack (identical to chip erase but last entry uses `sector_address` and `0x30` instead of `0x5555`/`0x10`), then calls `flash_util_byte_flipping()`.

## Build results
uno: [SUCCESS]
leonardo: [SUCCESS]
## Deviations
None — plan executed exactly as written.

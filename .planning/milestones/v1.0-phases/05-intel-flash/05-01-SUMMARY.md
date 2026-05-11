---
phase: 05-intel-flash
plan: 01
status: complete
commit: d1cc8e1
---

# 05-01 SUMMARY: Intel 28F Flash Handler

## Files Created / Changed

### New: `firestarter/include/flash_intel.h`
Header exporting `configure_flash_intel(firestarter_handle_t* handle)` with C linkage guard.

### New: `firestarter/src/proms/flash_intel.cpp`
Full Intel 28F command-register protocol implementation:
- `configure_flash_intel()` — dispatches CMD_WRITE / CMD_ERASE / CMD_BLANK_CHECK
- `flash_intel_write_init()` — enables VPP (REGULATOR | P1_VPP_ENABLE), 500ms settle, optional erase + blank check
- `flash_intel_write_execute()` — programs each byte with 0x40 setup + data write + SR.7 poll (150ms timeout per byte)
- `flash_intel_erase_execute()` — enables VPP, issues 0x20+0xD0, polls SR.7 (15s timeout)
- `flash_intel_cleanup()` — issues 0xFF reset, disables VPP
- `flash_intel_poll_sr()` (static) — polls SR.7; reports VPP error (SR.4) or program error (SR.3) on failure

### Modified: `firestarter/src/proms/memory.cpp`
Two changes:
1. Added `#include "flash_intel.h"` after `#include "flash_type_4.h"` (line 16)
2. Added protocol 0x10 dispatch block at line 72 — BEFORE the `if (handle->mem_type == TYPE_EPROM)` check (now line 77)

```c
if (handle->protocol == 0x10) {
    configure_flash_intel(handle);
    return;
}
```

## Build Output

Both firmware targets built successfully:
- `pio run -e uno` → `[SUCCESS]`
- `pio run -e leonardo` → `[SUCCESS]`

## Structural Invariants Verified

- `protocol == 0x10` dispatch at line 72, `TYPE_EPROM` check at line 77 — correct ordering
- All six handler functions present in flash_intel.cpp

## Deviations from Plan

None. Implementation matches the plan exactly. All success criteria met.

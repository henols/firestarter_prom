---
phase: 03-eprom-algorithms
plan: 01
status: complete
files_modified:
  - firestarter/src/proms/eprom.cpp
---

# Phase 03 Plan 01: UV-EPROM Algorithm Correctness — Summary

## What was changed

1. **`configure_eprom()` — protocol-based default `pulse_delay`**: Added a switch block after the control register hook is installed. When `pulse_delay` arrives as 0 (Python didn't supply one), it is set from the protocol: EPROM_QUICK (0x08) → 100 µs, EPROM_LEGACY (0x0B) → 500 µs, everything else (EPROM_STD) → 1000 µs.

2. **`eprom_write_execute()` — VPP routing by protocol**: The existing `FLAG_VPE_AS_VPP` branch was extended to also trigger on `handle->protocol == 0x0B`. EPROM_LEGACY devices use the direct VPE path (REGULATOR only); all other protocols use the VPE_TO_VPP dropping resistor path for precise VPP.

3. **`eprom_check_vpp()` — VPP routing by protocol**: Same protocol-aware condition applied symmetrically. The `FLAG_VPE_AS_VPP` check now also fires for EPROM_LEGACY (0x0B), with comments distinguishing direct VPE path from the dropping-resistor path.

4. **`eprom_generic_init()` — unconditional VPP check (REQ-SAF-01)**: Moved `eprom_check_vpp()` and its error-return guard outside the `chip_id > 0` gate. VPP is now validated on every init regardless of whether a chip ID is expected, satisfying the safety requirement. The chip-ID check remains conditional on `chip_id > 0`.

## Build results

uno: SUCCESS
leonardo: SUCCESS

## Deviations

None — plan executed exactly as written.

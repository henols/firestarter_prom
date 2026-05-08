---
phase: 10-static-pins
plan: 01
status: complete
---

# Phase 10-01 Summary

## What was built

Five changes across `pinouts.json`, `database.py`, `firestarter.h`, `json_parser.c`,
and `memory.cpp`.

### 1. `pinouts.json` — static-high-pins on DIP24 variants
Added `"static-high-pins": [24]` to `DIP24_2716` and `DIP24_2732`. DIP24 chip pin 24
(VCC) sits at DIP32 socket position 28, which is wired to bus line 13 on the RURP
shield. The bus line 13 shift register output doubles as the VCC supply for DIP24 chips;
it must be driven HIGH unconditionally.

### 2. `pin_conversions[24]` in `database.py`
Added `24: 13` (with explanatory comment). This makes VCC pin 24 translateable through
the existing pin_conversions path so `get_bus_config()` can resolve static-high-pins
without a special code path.

### 3. `get_bus_config()` in `database.py`
Added `static-high-pins` handling after rw-pin/vpp-pin: translate each pin through
`pin_conversions`, collect as a list, emit as `"static-high"` array in the bus-config
output dict. Non-translatable pins produce a warning and are skipped.

### 4. `bus_config_t` in `firestarter.h`
Added one field:
```c
uint32_t static_high_mask;  // Bus lines unconditionally driven HIGH
```

### 5. `json_parser.c` — parse `static-high`
- `static_high_mask = 0` added to json_parse() initializations alongside the other
  bus_config field inits.
- New `"static-high"` branch in `parse_bus_config()`: parses the integer array and ORs
  each element as `1UL << value` into `static_high_mask`. Token accounting follows the
  same pattern as the `"bus"` array branch.

### 6. `memory.cpp` — three changes
- `mem_util_remap_address_bus`: added `reorg_address |= config.static_high_mask` after
  the vpp_line block.
- `mem_util_calculate_msb_register`: removed the `if (handle->pins == 24) msb |= ADDRESS_LINE_13`
  special case. Replaced by the data-driven static_high_mask mechanism.
- `mem_util_calculate_top_address_register`: replaced dead compound condition
  `(top_address & READ_WRITE) && READ_WRITE == WRITE_FLAG` (always false) with a plain
  `if (handle->pins < 32)` plus a comment naming the VPE_TO_VPP / A16 sharing constraint.

## Verification

```
DIP24_2716 bus-config: {'bus': [0..10], 'vpp-pin': 11, 'static-high': [13]}  ✓
DIP24_2732 bus-config: {'bus': [0..11], 'static-high': [13]}                  ✓
DIP28_27512 bus-config: {'bus': [0..15]}  — no static-high                    ✓
DIP32_STD bus-config: {'bus': [...], 'vpp-pin': 21}  — no static-high         ✓
pio run -e uno:       SUCCESS                                                  ✓
pio run -e leonardo:  SUCCESS                                                  ✓
```

## Deviations

None. Implementation matched the plan exactly.

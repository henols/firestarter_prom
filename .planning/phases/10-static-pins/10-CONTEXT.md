---
phase: 10-static-pins
type: context
---

# Phase 10 — Static Pins, Multi-CE, and Address Bus Correctness

## Problems

### 1. No mechanism for static pins (always-high / always-low)

`bus_config_t` only carries `address_lines[]`, `rw_line`, and `vpp_line`. There is no way
to express bus lines that must be driven to a fixed state independent of address or R/W:

- **Multi-CE chips**: chips with two chip-enable pins (e.g. /CE1 active-low AND CE2
  active-high). RURP hardware handles exactly one CE via `rurp_chip_enable()`. The second
  enable pin is on the address bus and must be held static — LOW if active-low, HIGH if
  active-high.

- **Required-HIGH NC pins**: some JEDEC datasheets say "tie to VCC" for certain NC/unused
  pins (e.g. DIP28_2764 pin 26 is listed as nc-pin in pinouts.json but JEDEC recommends
  tying it HIGH for reliability). Currently ignored.

- **The ADDRESS_LINE_13 hack for 24-pin chips**: `mem_util_calculate_msb_register` forces
  bit 13 (bus line 13) HIGH for all 24-pin chips unconditionally
  (`msb |= ADDRESS_LINE_13`). This is a hardware quirk with no comment explaining the
  physical pin or why it must be high. It should be data-driven via `static-high-pins`
  in `pinouts.json` rather than hardcoded.

### 2. Dead condition in `mem_util_calculate_top_address_register`

```c
if (((top_address & READ_WRITE) && READ_WRITE == WRITE_FLAG) || handle->pins < 32) {
```

`READ_WRITE == WRITE_FLAG` is `0x40 == 0` — always false at compile time. The condition
has always been just `handle->pins < 32`. The dead comparison makes it look like a live
write-path check. It should be replaced with a clear, commented expression.

## Goal

Add a `static_high_mask` field to `bus_config_t` that encodes bus lines which must always
be driven HIGH. Python populates it from `static-high-pins` in `pinouts.json`. Firmware
ORs it unconditionally into `reorg_address` in `mem_util_remap_address_bus`. Clean up the
dead condition.

(Static-LOW is not needed yet: address bus lines not in address_mask AND not in
static_high_mask default to 0 (LOW) already, which is correct for /CE2 pins that need to
be held asserted-low.)

## Changes

### pinouts.json
Add `static-high-pins` to pinouts that need it:
- `DIP24_2716` and `DIP24_2732`: pin → bus line 13 (the ADDRESS_LINE_13 hardware requirement)
- `DIP28_2764`: pin 26 (nc-pin, JEDEC says tie to VCC → bus line 13 in 28-pin mapping)
  — only if that bus line drives a real socket pin that should be HIGH

### bus_config_t (firestarter.h)
Add one field:
```c
uint32_t static_high_mask;  // bus lines always driven HIGH (e.g. CE2, tied-high NC pins)
```

### parse_bus_config (json_parser.c)
Initialize `static_high_mask = 0`. Parse new `static-high` key: an array of bus line
numbers to OR into a mask. Same array format as `bus`.

### mem_util_remap_address_bus (memory.cpp)
After the rw_line and vpp_line steps:
```c
reorg_address |= config.static_high_mask;
```

### mem_util_calculate_msb_register (memory.cpp)
Remove the `if (handle->pins == 24) msb |= ADDRESS_LINE_13;` special case entirely.
The static_high_mask mechanism replaces it.

### mem_util_calculate_top_address_register (memory.cpp)
Replace the dead condition:
```c
// Before:
if (((top_address & READ_WRITE) && READ_WRITE == WRITE_FLAG) || handle->pins < 32) {
// After:
if (handle->pins < 32) {  // VPE_TO_VPP shares the A16 bit; preserve it for <32-pin chips
```

### database.py — get_bus_config()
Add `static-high-pins` handling: translate each static-high physical DIP pin through
`pin_conversions` to a bus line number. Output as `static-high` array in the bus-config JSON.

### Python get_adapter_table() (bonus)
The adapter table already shows NC pins and the physical purpose of all pins. No change
needed — the static-high information is visible as VCC/NC in the table.

## What this enables

After this phase:
- Multi-CE chips can be supported by adding the second CE pin to `static-high-pins` (if
  active-high) or leaving it unmentioned (active-low second CE defaults to LOW via 0 address)
- The ADDRESS_LINE_13 magic for 24-pin chips is documented and data-driven
- The bus code has no dead conditions

## Files

- `firestarter/include/firestarter.h`
- `firestarter/src/json_parser.c`
- `firestarter/src/proms/memory.cpp`
- `firestarter_app/firestarter/data/pinouts.json`
- `firestarter_app/firestarter/database.py`

## Out of Scope

- Active-low static pins (static_low_mask): deferred — no known chip in the DB needs this
  right now; the default-zero behavior of unassigned bus lines already handles /CE2
- Second CE routed through RURP CE hardware: hardware limitation, cannot be changed
- Chips needing two simultaneously-toggled CE signals during read: not in scope for DIP 24-32

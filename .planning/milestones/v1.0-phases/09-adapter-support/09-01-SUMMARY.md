---
phase: 09-adapter-support
plan: 01
status: complete
---

# Phase 09-01 Summary

## What was built

Three changes across `database.py`, `eprom_info.py`, and `main.py`:

### 1. `get_adapter_table()` in `database.py`
New method on `EpromDatabase`. Takes `pin_count` and `pinout_key`, reads the raw
`pinouts.json` data (not `pin_conversions`), and returns `[(pin, signal), ...]` for
every physical DIP pin 1..N. Shared pins (e.g. OE and VPP on the same DIP28_27512
pin 22) produce combined labels like `"OE/VPP"`.

### 2. Hardware compatibility warnings in `eprom_info.py`
- `print_eprom_list_table()`: appends `[!]` to the chip name for any chip without
  a `bus-config` (unknown/missing pinout key in `pinouts.json`)
- `prepare_detailed_eprom_data()`: sets `no_pinout_warning=True` when bus-config absent
- `present_eprom_details()`: prints a two-line WARNING when `no_pinout_warning` is set

### 3. `--adapter` flag wired end-to-end
- `main.py`: `-a/--adapter` added to `create_info_args()`
- `prepare_detailed_eprom_data()`: `include_adapter` param; fetches adapter table and
  stores it in `combined_data["adapter_table"]`
- `present_eprom_details()`: `show_adapter` param; renders a two-column DIP-mirrored
  table (left pins top→bottom, right pins bottom→top matching physical chip orientation)

## Verification results

```
DIP28_27512 pin 22: OE/VPP  ✓
DIP28_27512 pin  1: A15     ✓
DIP28_2764  pin  1: VPP     ✓
DIP28_2764  pin 22: OE      ✓
DIP32_STD   pin  1: VPP     ✓
No false warning on normal chip: 0 warning lines ✓
```

## Hardware constraint noted

During planning, confirmed that CE and OE are hardwired to dedicated Arduino GPIO pins
on the RURP shield (`rurp_chip_enable()` / `rurp_chip_output()` — dedicated control pin
path). They are NOT part of the address bus shift registers (LSB/MSB/CONTROL). Therefore
CE cannot carry an address bit and an address line cannot drive CE/OE — any chip with
such a non-standard pinout mandates a physical wiring adapter. The `--adapter` table
makes this visible to the user.

## Deviations

None. Implementation matched the plan exactly.

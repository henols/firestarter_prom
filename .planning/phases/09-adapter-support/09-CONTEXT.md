---
phase: 09-adapter-support
type: context
---

# Phase 09 — Hardware Compatibility & Adapter Support

## Problem

The tool currently shows all 743 chips in search results and info with no indication of
whether a chip can be used directly or requires special handling. Two gaps:

1. **Silent no-bus-config failure**: If a chip's pinout key is absent from `pinouts.json`,
   `get_bus_config()` returns `None` — the chip appears in `search` normally but any hardware
   operation silently produces broken output (no bus lines, wrong VPP routing).

2. **No adapter guidance**: Power users with non-standard chips need to know exactly which
   physical RURP socket pin carries each signal so they can build a wiring adapter. This
   information is fully encoded in `pinouts.json` but is never surfaced in the UI.

## Goal

Make `firestarter info` and `search` explicitly communicate hardware compatibility, and add a
`--adapter` flag to `info` that prints the physical pin-to-signal table required to build a
wiring adapter for any chip.

## Features

### Feature 1: Hardware Compatibility Warning

**Where:** `firestarter search <query>` list output and `firestarter info <chip>` detail view

**What:**
- If a chip has no bus-config (pinout key not in `pinouts.json`), mark it visibly in search
  results (e.g. a `!` column or `[no pinout]` tag)
- In `firestarter info`, if no bus-config, print a clear warning:
  `"WARNING: No pinout defined for this chip. Hardware operations will fail."`
- This replaces the current silent failure path

### Feature 2: `firestarter info --adapter`

**Where:** `firestarter info <chip> --adapter`

**What:** Print a two-column table showing, for each physical DIP socket pin:
- The physical pin number (1–32)
- The signal it carries on the RURP (A0–A18, D0–D7, CE, OE, VPP, VCC, GND, or NC)

This lets a user compare the RURP's expected wiring against a chip datasheet to derive
exactly which pins need remapping in a physical adapter.

**Example output for W27C512 (DIP28_27512):**
```
Adapter wiring for W27C512 (DIP28_27512, 28-pin):
  Pin  1 → VPP (pin 1 is VPP for this variant — no adapter needed for VPP)
  Pin  2 → A12
  ...
  Pin 22 → OE / VPP (VPP shares OE pin on this variant — VPE_ENABLE path)
  ...
```

Chips that plug in without any adapter still get the table — it confirms no wiring changes
are needed and serves as a datasheet cross-reference.

## Source of Truth

`firestarter_app/firestarter/data/pinouts.json` contains all the data needed:
- `address-bus-pins`: list of physical DIP pins in A0→AN order
- `oe-pin`, `vpp-pin`, `rw-pin`: physical DIP pin for each control signal

`pin_conversions` in `database.py` maps physical DIP pin numbers to RURP internal bus line indices.
The reverse mapping (RURP line → signal name) is needed for display.

## Files to Modify

- `firestarter_app/firestarter/database.py` — add `has_pinout()` helper
- `firestarter_app/firestarter/eprom_info.py` — render adapter table + no-pinout warning
- `firestarter_app/firestarter/main.py` — wire `--adapter` flag to info command
- `firestarter_app/firestarter/eprom_info.py` — mark chips without bus-config in search output

## Out of Scope for This Phase

- Generating Gerber files or physical adapter designs
- Auto-detecting adapter mismatches at runtime via chip ID read
- Supporting chips outside DIP 24–32

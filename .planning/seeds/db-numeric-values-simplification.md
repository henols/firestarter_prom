---
title: Simplify chip DB — real numeric values (mV / µs) instead of strings
trigger_condition: a DB/schema-cleanup milestone is scoped, OR fold into bus-config-clean-redesign / 27c-algorithm-fidelity-param-table-refactor when either lands
planted_date: 2026-07-02
status: dormant
---

# Simplify chip DB — real numeric values instead of strings

Make `chip_database.json` store voltages and timing as integers (millivolts /
microseconds) instead of unit-suffixed strings, and delete the host-side parse
layer that only exists to undo that string formatting. Host-only, pure-software
change — the **firmware never reads the JSON** (host sends already-parsed ints
over the wire), so this touches only `firestarter_app/`.

## Why (payoff)

- **Kills a whole coercion layer.** [database.py](../../firestarter_app/firestarter/database.py)
  `_map_data` currently does `electrical.get("vpp","0").replace("V","")` → `float()`
  for vcc/vpp and calls `_parse_pulse_duration("100 us") → 100`. All of that
  disappears if the DB hands over numbers directly.
- **Ends an existing redundancy/inconsistency.** Every chip already carries
  **both** `vpp: "12V"` (string) **and** `vpp_mv: 12000` (int) — the numericalize
  job is half-done. Meanwhile `vcc`/`vdd` exist *only* as strings. One honest
  representation per value.
- **One unit convention.** Millivolts covers the decimal cases with no floats
  (`5.5V`→`5500`, `12.5V`→`12500`, `13.5V`→`13500`). Matches the wire protocol
  (`vpp_mv`, `pulse-delay` are already ints on the wire) and the existing
  `size_bytes` / `vpp_mv` naming.

## Decided design

**Convert to integers (drop the string twin):**

| Field (was) | Becomes | Unit |
|---|---|---|
| `vcc: "5V"` | `vcc_mv: 5000` | int millivolts |
| `vdd: "5.5V"` | `vdd_mv: 5500` | int millivolts |
| `vpp: "12V"` + `vpp_mv: 12000` (redundant) | `vpp_mv: 12000` only | int millivolts |
| `pulse_duration: "100 us"` / `"Algorithm Controlled"` | `pulse_duration_us: 100` / `0` | int µs |

**Pulse-duration sentinel is safe as `0`.** 417/746 chips (56%) store
`"Algorithm Controlled"`. Collapsing that to `0` does **not** conflate it with
"unknown/missing," because firmware dispatches on `algorithm` and *only the
algorithms that consume `pulse-delay` ever read the field* — an algorithm-
controlled chip's `0` is never looked at. (This was the one landmine; the
"we know which protocols require a pulse duration" insight defuses it.)

**Stays a string on purpose** — these are numbers-that-aren't or genuine
categoricals; turning them into ints would be a readability *regression*, not a
simplification:

- `chip_id_value: "0x00008f86"` — chip IDs are canonically hex (datasheets,
  minipro `infoic.xml`); JSON has no hex literal so an int would show as decimal
  `36742`, unrecognizable when cross-referencing a datasheet. 285 distinct
  values. The `int(x,16)` parse at database.py:427 is trivial and stays.
- `type` (`UV-EPROM` / `Flash/EEPROM` / `EEPROM` / `SRAM` / `FRAM`),
  `support_status` (`supported` / `adapter-required` / `protocol-not-implemented`),
  `pinout`, `part_number`, `manufacturer` — categorical names/keys, not numbers.

Scope rule: *"real numerical values instead of strings"* = values that are
numbers wearing a string costume, **not** "stringly-typed everything."

## Touch points (all in `firestarter_app/`)

1. `tools/build_db.py` — change the emitter for vcc/vdd/vpp/pulse_duration;
   regenerate all 746 chips in `firestarter/data/chip_database.json`.
2. `firestarter/database.py` `_map_data` — delete `.replace("V","")` + `float()`
   coercion and `_parse_pulse_duration`; read `vcc_mv`/`vpp_mv`/`pulse_duration_us`
   directly.
3. Display — `ic_layout.py` (`vcc_str`) and `eprom_info.py` need a small
   `mV → "5V"/"5.5V"/"12.5V"` render helper so human output is unchanged.
4. Test fixtures / snapshots using the old string schema.

## Breaking-change note

Clean break chosen — **no tolerant reader**. Existing old-format
`~/.firestarter/database.json` user overrides (with `"5V"` / `"100 us"`) will
stop loading. Acceptable while on beta (`3.0.0bX`, stable is operator-gated).
Flag in the changelog / migration note when this lands.

## Related

- [[bus-config-clean-redesign]] — the other "clean up the DB/param model" seed;
  natural to schedule together.
- `.planning/seeds/27c-algorithm-fidelity-param-table-refactor.md` — adjacent
  param-table refactor; check for overlap before scoping.

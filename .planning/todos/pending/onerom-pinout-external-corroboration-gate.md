---
created: 2026-08-20T00:00:00Z
title: "Lock pinouts.json against an independent external oracle (one-rom chip-types.json) -- 12 of 15 families already corroborated, nothing guards them"
area: host
resolves_phase: unassigned
files:
  - firestarter_app/firestarter/data/pinouts.json
  - firestarter_app/tests/
---

## Problem

`firestarter/data/pinouts.json` holds all 15 pin-map families that every one of the 746
`chip_database.json` rows routes through. It is **hand-maintained** — `tools/build_db.py:23`
reads it as an *input*, so unlike `chip_database.json` it is not regenerated from
`infoic.xml` and gets no protection from the generator's decode tests. A wrong pin number
in a family silently mis-drives up to 255 chips (`DIP32_SST39SF040`), and the only oracles
we have today are (a) the datasheet, read by hand at authoring time, and (b) bench silicon,
which we have for a small fraction of families.

An **independent second oracle now exists**. [One ROM](https://github.com/piersfinlayson/one-rom)
(RP2350 ROM-replacement, 345 stars, actively maintained) publishes
[`rust/config/json/chip-types.json`](https://github.com/piersfinlayson/one-rom/blob/main/rust/config/json/chip-types.json)
— 34 real chip types with DIP pin numbers per signal, in a schema that is a near-exact
match for ours: `address` ordered A0..An, `data` D0..D7, `control.{ce,oe,write}` with
polarity, `programming.{vpp,pgm}` pin, `power` VCC/GND, plus `size`/`pins`/`aliases`.

Its independence is the point:

- **Different lineage.** No relationship to `infoic.xml`. Authored from datasheets by a
  different maintainer for a different purpose.
- **Different validation oracle.** One ROM never programs a chip — it *emulates* one. Its
  bus maps are validated by the emulator working when plugged into real retro machines.
  That is in-circuit read-path evidence, orthogonal to our write-path bench evidence.
- **Blind spot is disjoint from ours.** It carries no VPP millivolts, no `pulse_duration_us`,
  no algorithm, no chip ID, no page size. It can only speak to the bus map — but the bus map
  is exactly the axis `pinouts.json` owns.

## Evidence already in hand

Full cross-check result, schema correspondence table, reproduction script and the
what-it-cannot-do limits live in
[`notes/onerom-pinout-external-corroboration.md`](../../notes/onerom-pinout-external-corroboration.md).
**Read that first** — it is the authoritative record; this todo carries only the summary the
gate needs, and the note must not be duplicated here.

Snapshot cross-checked: blob `56cb04ca91e66aef0fd15236cc357602367c2b05` (58601 bytes),
`main`, fetched 2026-08-20. Fields compared: `address-bus-pins`, `data-bus-pins`, `ce-pin`,
`oe-pin`, `rw-pin`, `vpp-pin`, `vcc-pin`, `gnd-pin`.

The four buckets the gate has to encode:

| bucket | families | gate behaviour |
|---|---|---|
| **byte-identical (11)** | `DIP24_2716`, `DIP24_2732`, `DIP24_2816`, `DIP24_6116`, `DIP28_27256`, `DIP28_27512`, `DIP28_28C64`, `DIP28_28C256`, `DIP32_28C512_EEPROM`, `DIP32_SST39SF040`, `DIP32_STD` | assert equality — RED on any drift |
| **semantic agreement (1)** | `DIP32_27C020` — our `rw-pin: [31]` vs their `programming.pgm.pin: 31` | expected divergence, reason recorded |
| **non-comparison (2)** | `DIP28_2764` (2764+27128 superset, pin 26 = A13); `DIP28_JEDEC_SRAM_8K` (8 KB, vs their 32 KB `62256`) | expected divergence, reason recorded |
| **no counterpart (1)** | `DIP24_2532` | out of scope, stays single-sourced |

585 of 746 database rows ride the 11 locked families, `DIP32_SST39SF040` alone carrying 255.
`DIP28_28C256` — the AT28C256 family Phase 149 left untouched — is in the locked set.

## What to build

A host-side corroboration test — no firmware, no hardware, no `chip_database.json` write.

1. **Vendor the snapshot** under `firestarter_app/tests/fixtures/` (or `tests/golden/`, to
   match the existing `chip_database_field_inventory.json` convention) with a provenance
   header recording upstream repo, path, blob SHA, and fetch date. Do **not** fetch at test
   time — the suite must stay offline and deterministic.
2. **Assert the 11 byte-identical families stay byte-identical.** Any future edit to one of
   those pin lists goes RED against an oracle that has no shared lineage with ours.
3. **Pin the 4 non-agreeing entries as explicitly-expected divergences, each with its
   reason inline** — `DIP32_27C020` (semantic agreement via `programming.pgm`),
   `DIP28_2764` (superset), `DIP28_JEDEC_SRAM_8K` (different chip), `DIP24_2532` (no
   counterpart). Expected-divergence entries must be enumerated, not skipped by a
   catch-all: a *new* family added to `pinouts.json` that has a one-rom counterpart and
   disagrees should fail, not fall through a wildcard.
4. **Do not auto-refresh the snapshot.** A drift-detection leg is fine (compare vendored
   blob SHA to a recorded expectation) but re-pointing at a newer upstream must be a
   deliberate, reviewed act — an upstream edit landing silently would invert the gate from
   "guards us" to "upstream now dictates our pin maps."

## Licensing

Resolved — **MIT**, safe to vendor with attribution (`Copyright (c) 2026 Piers Finlayson`).
Rationale and the two traps that will make a reviewer re-open it (GitHub reports
`NOASSERTION`; there is no root `LICENSE`, only `LICENSE.md`) are recorded in the note's
"three hard limits" section. Do not re-litigate from the API field.

## Why a gate on top of the note

The note records the corroboration; it cannot *enforce* it. "11 families agree" is a fact
that decays the moment someone edits a pin list —
and pin-list edits are exactly what this project does (`3659121`, `38b55d5`, `94ea3b5`,
`fa0c1a4` all touched `pinouts.json`). Related: [[reference_chip_database_schema_algorithm_pulse_duration]]
records that `chip_database.json` is generated and must never be hand-edited; `pinouts.json`
is the hand-maintained input that rule leaves unprotected.

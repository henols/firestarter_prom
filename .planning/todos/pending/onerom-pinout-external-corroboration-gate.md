---
created: 2026-08-20T00:00:00Z
title: "Lock pinouts.json against an independent external oracle (one-rom chip-types.json) -- 13/14 families already corroborated, nothing guards them"
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

## Evidence already in hand (cross-check run 2026-08-20)

Snapshot cross-checked: blob `56cb04ca91e66aef0fd15236cc357602367c2b05` (58601 bytes),
`main` @ repo `updated_at` 2026-08-20T14:36:22Z.

Comparison covered `address-bus-pins`, `data-bus-pins`, `ce-pin`, `oe-pin`, `rw-pin`,
`vpp-pin`, `vcc-pin`, `gnd-pin` (ours) against `address`, `data`, `control.ce`,
`control.oe`, `control.write`, `programming.vpp`, `power.VCC`, `power.GND` (theirs).

**11 families byte-identical on every compared field:**

| firestarter family | one-rom type | chips routed |
|---|---|---|
| `DIP24_2716` | `2716` | 15 |
| `DIP24_2732` | `2732` | 16 |
| `DIP24_2816` | `28C16` | 19 |
| `DIP24_6116` | `6116` | 7 |
| `DIP28_27256` | `27256` | 67 |
| `DIP28_27512` | `27512` | 45 |
| `DIP28_28C64` | `28C64` | 35 |
| `DIP28_28C256` | `28C256` | 30 |
| `DIP32_28C512_EEPROM` | `28C512` | 18 |
| `DIP32_SST39SF040` | `SST39SF040` | 255 |
| `DIP32_STD` | `27C040` | 78 |

**1 further family corroborated semantically, not literally — `DIP32_27C020` (88 chips):**
our `rw-pin: [31]` vs their absent `control.write`. Not a divergence. One ROM records
`programming.pgm.pin = 31` for **both** `27C010` and `27C020`, independently confirming the
premise behind the Phase 98-03 / CR-01 fix (operator schematic study, `3659121`): pin 31 is
/PGM, **not** A18, on ≤256K parts. Direct consequence for an open investigation — the
marginal Phase 99 bench result (write#1 60/64, write#2 0/64) cannot be explained by a wrong
pin-31 assignment, which leaves the suspected VPP droop as the standing hypothesis.

**2 families are non-comparisons, not diffs:**

- `DIP28_2764` — ours carries 14 address lines (pin 26 = A13); theirs 13. Ours is a
  deliberate **2764+27128 superset family** (58 chips, incl. `AM27128A`, `AM27C128`). Pin 26
  is NC on a true 2764 and A13 on a 27128. Correct as authored.
- `DIP28_JEDEC_SRAM_8K` — ours 13 address lines (8 KB, `DS1225`/`FM1608`/`M48T08`); their
  `62256` is 32 KB / 15 lines. Different chip. Our own `61256,62256` row correctly routes to
  `DIP28_28C256`, and *that* pairing agrees exactly. Correct as authored.

Net: **12 of 15 families now have an independent second source, 2 are explained
non-comparisons, and 1 (`DIP24_2532`, 1 chip) has no counterpart.** No test guards any of it.

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

Resolved — **MIT**, safe to vendor with attribution. One ROM's
[`LICENSE.md`](https://github.com/piersfinlayson/one-rom/blob/main/LICENSE.md) dual-licenses
the repo: MIT for "software and firmware files", CERN-OHL-W-2.0 for "schematic, PCB files,
3d models and other hardware files, in particular those in the `hardware/` directory".
`rust/config/json/chip-types.json` is a software config file consumed by the `onerom-config`
crate, and sits nowhere near `hardware/` — MIT applies. Include the MIT notice and
copyright line (`Copyright (c) 2026 Piers Finlayson`) alongside the vendored fixture.

Note the GitHub API reports the repo license as `NOASSERTION` / "Other" — that is an
artifact of the dual-license `LICENSE.md` layout, not an absence of license. Do not let a
future reviewer re-open this on the strength of the API field.

## Why this is worth a gate rather than a one-off note

The corroboration is only valuable while it is *enforced*. Running the diff once and writing
down "11 families agree" produces a fact that decays the moment someone edits a pin list —
and pin-list edits are exactly what this project does (`3659121`, `38b55d5`, `94ea3b5`,
`fa0c1a4` all touched `pinouts.json`). Related: [[reference_chip_database_schema_algorithm_pulse_duration]]
records that `chip_database.json` is generated and must never be hand-edited; `pinouts.json`
is the hand-maintained input that rule leaves unprotected.

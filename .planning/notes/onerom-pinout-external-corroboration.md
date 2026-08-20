---
title: "one-rom chip-types.json vs pinouts.json — external corroboration result (POSITIVE for the bus-map axis, vacuous for the programming axis)"
date: 2026-08-20
context: "/gsd-explore: can the files in piersfinlayson/one-rom rust/config/json be used to confirm the firestarter database?"
---

# one-rom `chip-types.json` — what it corroborates and what it cannot

Investigated whether [One ROM](https://github.com/piersfinlayson/one-rom)'s published
hardware config JSON can serve as a second source for `firestarter_app/firestarter/data/pinouts.json`.

**Verdict: POSITIVE for bus maps — 12 of our 15 pinout families now have independent
corroboration, with zero defects found. VACUOUS for the programming axis**, which is where
every recent defect has actually landed. Both halves of that verdict are load-bearing; the
second half is the reason this is not a general-purpose validation source.

## What's in the directory

26 files, two unrelated kinds:

- **`fire-*.json` / `ice-*.json` (24 files)** — One ROM PCB hardware configs: RP2350/STM32F4
  GPIO-to-pin-type mappings and jumper-header layouts, so new PCB revisions need no source
  change. **No relevance to us.** Do not re-read these hoping for chip data.
- **`chip-types.json` (58601 bytes, 37 entries — 34 real chip types + 3 plugin stubs)** — the
  only file that matters.

## Why it is an independent oracle

This is the whole basis of the result, so it is worth stating precisely. Three separate
grounds for independence, and they do not collapse into each other:

1. **Different lineage.** No relationship to `infoic.xml`. Authored from datasheets by a
   different maintainer for a different product. Contrast the candidate sources rejected in
   `research/questions.md` — most open programmer tables are infoic forks, and a fork
   corroborates nothing.
2. **Different validation oracle.** One ROM *emulates* a ROM; it never programs one. Its bus
   maps are proven by the emulator working when seated in a real retro machine. That is
   in-circuit read-path evidence, orthogonal to our write-path bench evidence.
3. **Disjoint blind spot.** It carries no VPP millivolts, no `pulse_duration_us`, no
   algorithm, no chip ID, no page size — so where it *does* speak, it speaks about the one
   axis `pinouts.json` owns, and nothing else.

Active project (345 stars, `updated_at` 2026-08-20), so this is a maintained source rather
than an abandoned snapshot.

## Schema correspondence

Near-1:1, which is why the diff is mechanical rather than interpretive:

| one-rom | firestarter `pinouts.json` |
|---|---|
| `address` (ordered A0..An) | `address-bus-pins` (ordered A0..An) |
| `data` (D0..D7) | `data-bus-pins` |
| `control.ce.pin` | `ce-pin` |
| `control.oe.pin` | `oe-pin` |
| `control.write.pin` | `rw-pin` |
| `programming.vpp.pin` | `vpp-pin` |
| `programming.pgm.pin` | (no direct equivalent — see `DIP32_27C020` below) |
| `power[].pin` where `name == "VCC"` / `"GND"` | `vcc-pin` / `gnd-pin` |
| `control.*.type` (`fixed_active_low` / `configurable`) | (**not representable** — see below) |
| `size`, `pins`, `aliases`, `bit_modes` | `electrical.size_bytes`, `.pin_count` (in the generated DB, not here) |

Both sides number pins as physical DIP positions and both order the address list A0-first.
The `control.*.type` row is the one real schema gap on our side and it is the blocker in
[`seeds/mask-rom-24pin-read-support.md`](../seeds/mask-rom-24pin-read-support.md).

## Result

Snapshot: blob `56cb04ca91e66aef0fd15236cc357602367c2b05`, `main`, fetched 2026-08-20.
Fields compared: `address-bus-pins`, `data-bus-pins`, `ce-pin`, `oe-pin`, `rw-pin`,
`vpp-pin`, `vcc-pin`, `gnd-pin`.

### 11 families byte-identical on every compared field

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

585 of 746 database rows ride those 11 families. Note `DIP28_28C256` is the family
**AT28C256** uses — the v1.32 write-path target that Phase 149 left untouched — and it agrees
exactly, so the AT28C256 bus map is not a candidate explanation for anything in that
investigation.

### 1 family corroborated semantically, not literally — and it settles an open question

`DIP32_27C020` (88 chips): ours carries `rw-pin: [31]`, theirs has no `control.write`. **Not a
divergence.** One ROM records `programming.pgm.pin = 31` for **both** `27C010` and `27C020`,
independently confirming the premise behind the Phase 98-03 / CR-01 fix (commit `3659121`,
from an operator schematic study): on ≤256K parts pin 31 is **/PGM, not A18**. Our `rw-pin`
is the mechanism that drives it — host resolves pin 31 → `pin_conversions[32][31] = 22` →
`config.rw_line = 22`, which the firmware folds into `CTRL_READ_WRITE` (0x40).

**Consequence for an open investigation:** the marginal Phase 99 AM27C020 bench result
(write#1 60/64 bytes, write#2 0/64 — [[project_v118_phase99_bench_defer]]) **cannot** be
explained by a wrong pin-31 assignment. VPP droop stands as the hypothesis, now with one
competing explanation eliminated by an independent source rather than by re-reading our own
schematic.

### 2 non-comparisons, not diffs

- **`DIP28_2764`** — ours has 14 address lines (pin 26 = A13), theirs 13. Ours is a deliberate
  **2764 + 27128 superset family** (58 chips, incl. `AM27128A`, `AM27C128`, `SMJ27C128`). Pin
  26 is NC on a true 2764 and A13 on a 27128. Correct as authored — the "diff" is an artifact
  of them modelling one chip where we model a family.
- **`DIP28_JEDEC_SRAM_8K`** — ours 13 address lines / 8 KB (`DS1225`, `FM1608`, `M48T08`);
  their `62256` is 32 KB / 15 lines. Different chip. Our own `61256,62256` row routes to
  `DIP28_28C256` instead, and that pairing agrees exactly. Correct as authored.

Both are cases where a naive automated diff reports RED and the code is right. Any gate built
on this must encode the reasons, not just the exceptions.

### 1 family with no counterpart

`DIP24_2532` (1 chip). One ROM has `2332` (a 4 KB *mask ROM*), not the TI 2532 EPROM. Our
entry came from `94ea3b5` (86-04) via `tools/extra_chips.json`. Stays single-sourced.

## Reproduction

Offline-reproducible from the vendored blob; the fetch is the only network step.

```bash
curl -sL -o chip-types.json \
  https://raw.githubusercontent.com/piersfinlayson/one-rom/main/rust/config/json/chip-types.json
# then, from firestarter_app/:
python3 - <<'PY'
import json
fs = json.load(open('firestarter/data/pinouts.json'))
oo = json.load(open('chip-types.json'))['chip_types']
M = {'DIP24_2716':'2716','DIP24_2732':'2732','DIP28_2764':'2764','DIP28_27256':'27256',
     'DIP28_27512':'27512','DIP28_28C256':'28C256','DIP24_6116':'6116','DIP32_27C020':'27C020',
     'DIP32_SST39SF040':'SST39SF040','DIP28_28C64':'28C64','DIP32_28C512_EEPROM':'28C512',
     'DIP24_2816':'28C16','DIP32_STD':'27C040','DIP28_JEDEC_SRAM_8K':'62256'}
for fsk, ook in M.items():
    p, o = fs[fsk]['pins'], oo[ook]
    g = lambda n: (o.get('control', {}).get(n) or {}).get('pin')
    f = lambda n: (p.get(n) or [None])[0]
    flags = []
    if p.get('address-bus-pins', []) != o.get('address', []): flags.append('ADDR')
    if p.get('data-bus-pins', []) != o.get('data', []):       flags.append('DATA')
    for label, fk, ok in [('CE','ce-pin','ce'), ('OE','oe-pin','oe'), ('WE','rw-pin','write')]:
        if f(fk) != g(ok): flags.append(f'{label} fs={f(fk)} oo={g(ok)}')
    if f('vpp-pin') != (o.get('programming', {}).get('vpp') or {}).get('pin'): flags.append('VPP')
    for label, fk, nm in [('VCC','vcc-pin','VCC'), ('GND','gnd-pin','GND')]:
        if f(fk) != next((x['pin'] for x in o.get('power', []) if x['name'] == nm), None):
            flags.append(label)
    print(('AGREE  ' if not flags else 'DIFF   ') + f'{fsk:22s} vs {ook:10s} ' + ' | '.join(flags))
PY
```

**Gotcha that will waste your time if you skip it:** map their `control.write` to our
**`rw-pin`**, not to a `we-pin`. We have no `we-pin` key — a first pass that looks for one
reports 6 spurious WE mismatches (`DIP28_28C256`, `DIP24_6116`, `DIP28_28C64`,
`DIP32_28C512_EEPROM`, `DIP24_2816`, `DIP32_SST39SF040`), all of which are actually agreements.

## What it cannot do — three hard limits

1. **Nothing on the programming axis.** No `vpp_mv`, `pulse_duration_us`, `algorithm`,
   `chip_id_value`, or page size. Those are precisely where the recent defects lived: the
   4.5 V premise disproved in Phase 148 (present in 5 files, not 2), the 128/64 B page seam
   in Phase 149, the deleted `CTRL_VPE_ENABLE` assert behind the Phase 145 W27C512 byte-0
   failure. One ROM never programs a chip and so has nothing to say about any of it. Treating
   this source as general database validation would be an overclaim of exactly the class
   corrected in v1.22's C-5.
2. **It cannot touch `chip_database.json`.** That file is generated from `infoic.xml` and the
   generator may not invent fields without upstream proof
   ([[feedback_generator_no_fields_without_infoic_proof]],
   [[reference_chip_database_schema_algorithm_pulse_duration]]). The usable seam is
   `pinouts.json`, which `tools/build_db.py:23` reads as an **input** — hand-maintained, and
   therefore *unprotected* by the generator's decode tests. That asymmetry is the finding
   that makes a gate worth building.
3. **Licensing permits vendoring, but read the right file.** `LICENSE.md` dual-licenses:
   **MIT** for "software and firmware files", CERN-OHL-W-2.0 for "schematic, PCB files, 3d
   models and other hardware files, in particular those in the `hardware/` directory".
   `rust/config/json/chip-types.json` is a software config consumed by the `onerom-config`
   crate and sits nowhere near `hardware/` — **MIT applies**; vendor with the notice and
   `Copyright (c) 2026 Piers Finlayson`. The GitHub API reports the repo license as
   `NOASSERTION` / "Other" and there is **no root `LICENSE` file** (it is `LICENSE.md`) — both
   are artifacts of the dual-license layout, not an absence of license. Do not let either
   re-open this question.

## Coverage it has that we don't

20 one-rom types have no counterpart in any of firestarter's 953 part numbers or aliases —
checked exhaustively, not sampled. Split by whether they are reachable:

- **Plausible (read-only, 5 V single rail, 24/28-pin):** `2316`, `2332`, `2364`, `23128`,
  `23256`, `23512`, `231024`, `23QL384`, `23QL512`, `23C1001`, `23C1010` — the Commodore /
  arcade mask ROMs. Routed to [`seeds/mask-rom-24pin-read-support.md`](../seeds/mask-rom-24pin-read-support.md);
  blocked on `configurable` CS polarity, which `database.py:297` cannot express
  (`static-high-pins` only, no `static-low-pins`).
- **Hardware-blocked, do not let these ride along:** `2704`/`2708` (3-rail, need −5 V and
  +12 V the RURP shield cannot source), `HM7641` (bipolar fusible-link PROM),
  `27C200`/`27C400` (40-pin, 16-bit data bus — no socket).
- **Write-path scope, not a pin-map question:** `27C301`, `27C080` (32-pin EPROMs).

## Downstream

- Gate spec (vendor the snapshot + lock the 11, pin the 4 with reasons):
  [`todos/pending/onerom-pinout-external-corroboration-gate.md`](../todos/pending/onerom-pinout-external-corroboration-gate.md)
- Mask-ROM family seed: [`seeds/mask-rom-24pin-read-support.md`](../seeds/mask-rom-24pin-read-support.md)
- The gap this exposes on the programming axis: `research/questions.md`,
  section "Is there an independent second source for the PROGRAMMING axis?" (2026-08-20)

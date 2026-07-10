---
title: Per-pin-map jumper table replaces the pin-count heuristic in ic_layout
trigger_condition: next milestone selection, OR the next time ic_layout.py jumper logic is touched for any reason
planted_date: 2026-07-10
status: dormant
---

# Per-pin-map jumper table replaces the pin-count heuristic

Replace the jumper derivation in `firestarter_app/firestarter/ic_layout.py`
(~L621-659) — which branches on pin count + a vpp-pin boolean — with an
explicit, schematic-derived table keyed on **pin-map identity × shield
revision family**, plus a fail-closed coverage test.

## Why

- The correct JP3/JP4 setting depends on *where* the pin map puts VPP (pin 1
  or not), not on pin count. The heuristic gets DIP28_27512 (45 chips) wrong
  today and provides nothing for 24-pin VPP maps.
- Ground truth exists for every revision (see
  `notes/jumper-display-ground-truth.md`): `rurp_schematics_rev1.pdf` for
  Rev 0/1, v1.7 upstream KiCad for Rev 2.x.
- 15 pin maps is a small, closed set — explicit data reviewed once beats a
  heuristic forever, and a new pin map then *forces* a conscious jumper
  decision instead of silently inheriting a guess.

## Shape

1. Jumper table: for each of the 15 pinouts.json keys × {Rev 0/1, Rev 2.x} →
   JP1/JP2/JP3/JP4 positions (or explicit "irrelevant"). Lives either in
   `pinouts.json` per entry or a dedicated module — decide at plan time.
2. `ic_layout.py` reads the table; heuristic deleted.
3. Coverage test: every pin map present in pinouts.json MUST have a jumper
   entry for every supported revision family — test fails when a new pin map
   is added without one (fail-closed, same spirit as `check_dispatch.py`).
4. Fix `PROTOCOLS.md:136` "VPP via JP4" wording in the same change.
5. Optional (UX, separable): filter displayed revision blocks by detected
   hardware revision when a board is connected.

## Prerequisites

- Resolve the open research questions first (Rev 2.x JP4 vs 32-pin pin-1-VPP
  chips; 24-pin VPP jumper needs) — see `research/questions.md` 2026-07-10
  entries.
- Todo `delete-jp5-dead-renderer` can land independently before this.

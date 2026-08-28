# Cell CHIP — 11-Part `dev test` Sweep on the Reference Rig (Leonardo + Rev 2.0)

Standing rig Phase 161 left assembled. This cell is opened by plan 162-05 and closed by
plan 162-10. See `.planning/v1.34/PROCEDURE.md`'s `## Chip-sweep step list` (C-01..C-09) for
the step ids cited below, and `162-05-PLAN.md`'s "Planner decisions" section for PD references.

## Session open (Task 1) — rig confirmation, operator-performed

- **Device node:** `/dev/ttyACM0` — operator confirmed this is the Leonardo, not inferred from
  it being the only node. (Re-verified by signature at Task 2, `P-02`.)
- **Shield revision (silkscreen, verbatim operator wording):** "2.0" — canonical form for
  `--shield-rev` is **`Rev 2.0`** (case-only normalization for `capture_provenance.py`'s closed
  choice set, per the `BRINGUP-leonardo-provenance/PREPROOF.md` precedent; not a correction of
  what the operator said).
- **Chip seating:** **W27C512** (DIP28) confirmed seated, pin-1 oriented, **JP4 at the 28-pin
  position**. Zero handling for position 1 (Phase 161's A3/B2 teardown left it exactly so).
- **VPP:** see `POT.md` for the full record — as-found 11.4 V (in band, 0 mV margin), a ~600 mV
  drift finding against Phase 161's A3/B2 12.0 V reading on this same rig/pot setting, and the
  pot re-adjusted to **11.97 V** (operative reading for the 12 V group, positions 1-8).

## Pre-flight (Task 2)

*(filled in below once the port-identity, arm-state and `fw_board_identity` bring-up datum steps
run)*

## Position 1 — `CHIP__v133__w27c512` (Task 3)

*(measured totals, per-operation figures and the derived 64 KiB ceiling filled in after C-05/C-07)*

## Position 2 — `CHIP__v133__w27e512` (Task 5)

*(measured erase duration and fast-fail assumption check filled in after C-05/C-07)*

## Leave-state at the end of this plan (162-05)

*(filled in at the end of Task 5 — board, port, arm, chip seated, pot setting, shield state)*

# CHIP cell — POT.md (12 V-group VPP record)

## D-13 scope

This is the **single** meter reading for the whole 12 V group (positions 1-8, per
`162-05-PLAN.md` Task 1). Positions 2 through 8 record their real-rail figure as a **named
absence** pointing back to this position — no second meter reading is taken inside this group
unless a pot boundary is crossed (the 12 V -> 13 V transition ahead of AM27C020, per PD-17).

## Session-open reading (Task 1, operator-performed)

- **12 V-group target:** 12000 mV (`rig-pins.json` `chips.w27c512.vpp_mv` / `chips.w27e512.vpp_mv`,
  both `12000`).
- **Guard band (firestarter/src/proms/eprom.cpp):** low guard fires strictly below
  `target * 95 / 100` = 11400 mV (`:535`); high guard fires above `target + 500 mV` = 12500 mV
  (`:530`). The guards compare the **firmware's own ADC reading**, never the operator's meter —
  the two will not agree exactly (A3/B2's own ratiometric ~+7.5% finding,
  `bench/cells/A3-B2/POT.md`).

### As found: 11.4 V — in band by exactly 0 mV of margin

Operator's multimeter reading, taken on the VPP rail with **no** pot adjustment first, per Task 1
step 4. **11.4 V is the low-guard threshold itself** (11400 mV) — technically in band, with zero
margin. Recorded as a finding, not silently corrected.

### Drift finding — same rig, same pot setting, ~600 mV lost while standing

Phase 161's cell A3/B2 `CELL.md` (`bench/cells/A3-B2/CELL.md:27-30`) records the operator's own
pre-flash meter reading on **this same rig, this same pot setting, confirmed untouched since**:
*"messured vpp to be exactly 12v"* -> **12.0 V** (2026-08-27 or earlier, Phase 161).

| When | Cell | Reading | Pot touched since? |
|---|---|---|---|
| Phase 161, cell A3/B2 (pre-flash) | A3/B2 | 12.0 V | — (baseline) |
| Phase 162, cell CHIP (session open, as found) | CHIP | 11.4 V | No — operator confirmed untouched |

**~600 mV lost between phases with nothing moved.** This is recorded here as a named finding for
Phase 165 triage and is **not** silently overwritten by the corrected value below — both readings
stay on the record.

### Pot adjusted to restore Phase 161's condition — operator-only action, no monitor loop

Operator adjusted the pot (single adjustment, no live monitor loop run) to bring the rail back
toward Phase 161's standing condition. **As set: 11.97 V** — mid-band, ~530 mV of margin above
the low guard (11400 mV) and ~530 mV below the high guard (12500 mV).

**Operative pot reading for the 12 V group (positions 1-8): 11.97 V.** This is the value carried
into `CELL.md` and into every position's `vpp_real_mv` in this group — positions 2-8 cite this
position (`CHIP__v133__w27c512`) as a named absence for their own `vpp_real_mv`, per D-13.

No forbidden override flag (`--force`) was used at any point in this session.

## C-03 — per-position firmware VPP readings (one per position, this file's running log)

| Position | Firmware VPP reading | Target | Shortfall (target - firmware) |
|---|---|---|---|
| `CHIP__v133__w27c512` | *(recorded in Task 2/3 pre-flight + C-03, see below)* | 12000 mV | *(see below)* |
| `CHIP__v133__w27e512` | *(recorded at Task 5)* | 12000 mV | *(see below)* |


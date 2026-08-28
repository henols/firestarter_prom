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
toward Phase 161's standing condition. **As set: 11.97 V** on the meter.

**The margin estimate below was computed from the meter reading alone, before any firmware
reading existed, and is now superseded by C-03's measurement (next section) — recorded, not
silently overwritten:** ~~mid-band, ~530 mV of margin above the low guard (11400 mV) and ~530 mV
below the high guard (12500 mV)~~. The firmware's own ADC reads considerably higher than the
meter (the same ratiometric error A3/B2 found), which puts the *real* margin against the high
guard much tighter than this estimate assumed — see C-03 below.

No forbidden override flag (`--force`) was used at any point in this session.

## C-03 — per-position firmware VPP readings (one per position, this file's running log)

| Position | Firmware VPP reading | Target | High guard (target+500) | Low guard (target×95%) | In band? |
|---|---|---|---|---|---|
| `CHIP__v133__w27c512` | **12800 mV (12.8 V)** | 12000 mV | 12500 mV | 11400 mV | **NO — 300 mV ABOVE the high guard** |
| `CHIP__v133__w27e512` | *(recorded at Task 5)* | 12000 mV | 12500 mV | 11400 mV | *(see below)* |

### FINDING — position 1's firmware VPP reading exceeds the high guard; a pot adjustment is required before `dev test` can run clean

Command run (exactly once, no monitor loop — see the shared conventions; a controlled `timeout -s
INT 4` was used to end the command's own continuous-print loop deterministically rather than let a
harness-level kill happen unlogged, per the standing `BRINGUP-wrv` P-H1 precedent
(`bench/EVIDENCE.md`'s `BRINGUP-wrv` row, an unlogged `vpp` kill left `~/.firestarter` populated)):

```
timeout -s INT 4 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/v1.34/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 vpp
```

Output: `VPP: 12.8V, Internal VCC: 5.5V` — one clean reading, then `VPP reading stopped by user.`
No error text; the standalone `vpp` diagnostic does not itself route through the firmware's
`eprom_check_vpp` guard (it printed cleanly at a value that guard would reject).

**12800 mV is 300 mV *above* `eprom.cpp:530`'s high guard** (`vpp_mv > target + 500` = 12500 mV
for this target). That guard **is** in the call path `dev test` will exercise: `eprom_generic_init`
(the init phase of both `write` and `erase`) calls `eprom_check_vpp` unconditionally and returns
`RESPONSE_CODE_ERROR` without `--force` (forbidden here) when the high guard fires — meaning
position 1's `write`/`erase` steps would abort at INIT if `dev test` is run at the pot's current
setting.

**Ratio consistency, not a new phenomenon:** 12800/11970 = **1.069**, in the same range as A3/B2's
measured ~+7.5% (1.075) ratiometric VPP-ADC gain error on this shield
(`bench/cells/A3-B2/POT.md`) — this is the *same* shield-wide gain fault, observed a third time
(two boards, three pot positions in A3/B2, now a fourth data point here), not a new rig defect.

**Precedent for the corrective action, P-06:** "If the historical `VPP is high` init guard fires
..., the pot is adjusted until the reading is in band and the run restarts clean from this step —
the guard is never bypassed, and `--force` is never used to push past it." Per the shared
conventions, only the **operator** adjusts the pot; Claude never adjusts it and never runs a
monitor loop. **A3/B2's own working setting on this exact rig type landed at firmware ≈12.3 V /
meter ≈11.44 V** (in band, ~200 mV of real margin below the 12500 mV high guard) — offered to the
operator as a concrete reference point, not as an instruction to hit that exact number.

**This is a physical pot-movement action and is handed to the operator as a checkpoint** (Task 3
paused; see the plan's checkpoint return). C-05 (the `dev test` invocation) is **not** run at the
current setting — running it now would very likely produce a genuine `MSG_ERR_VPP_HIGH` INIT abort
that is an artifact of the pot setting, not a finding about the chip or about v1.33.


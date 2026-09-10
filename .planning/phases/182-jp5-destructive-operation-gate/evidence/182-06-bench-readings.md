# Phase 182 Plan 06 — bench readings

Operator-taken readings. Every value here is recorded verbatim as reported. Claude took no
multimeter reading; the USB-side reads are Claude's and are marked as such.

**Session:** 2026-09-10
**Rig:** Arduino Leonardo + RURP **Rev 2.2** shield, board identity stated by the operator on sight
(`hw_revision` cannot distinguish Rev 2.2 from Rev 2.0 from a modified Rev 0).
**Port identity, verified this session:** `/dev/ttyACM0`, `controller: leonardo`, firmware
`3.0.0b22`.

## Task 1 — assumption A1: the VPE rail with the boost regulator disabled

| Field | Value |
|---|---|
| Probe point | **`J6` pin 4** (`J6` = the 4-pin "VP" socket; pin 4 is the `VPE` rail) |
| Reference point | *pending operator confirmation — `J6` carries no GND pin, so an external ground was used* |
| Reading | **4.9 V DC** |
| Board state | Powered, idle, no operation running, no chip seated |
| Board identity | Rev 2.2, stated by the operator on sight |
| Date | 2026-09-10 |
| Taken by | Operator (multimeter readings are operator-only in this project) |

**Verdict: A1 is CONFIRMED.** Decision threshold: a reading at or below ~6 V is a logic-level rail
and confirms the assumption; a reading at or above ~11 V is a programming rail and falsifies it.
4.9 V sits decisively in the confirming band.

**Why 4.9 V is the expected confirming value, not merely "low".** The boost input is `/5V_REG`, the
fused 5 V rail, feeding both `L1` pin 1 and the `MIC2288`'s VIN (`U1` pin 5). With the switch held
off, the conducting path is `L1` → `D1` (1N5819 Schottky) → `VPE`. At no load the Schottky's forward
drop collapses toward zero, so the rail settles just under VIN. 4.9 V is that value.

**Consequence for the gate's scope (D-06).** The premise the desk trace could not measure now holds:
with `CTRL_VPP_REGULATOR_ENABLE` clear the rail is at logic level, so a `read` on an affected part
drives socket pin 1 with a logic level, not a programming voltage. `DAMAGE_CAPABLE_OPERATIONS`
stays `{write, erase}`. Task 3's conditional widening to `read`/`verify`/`blank` does **not** fire.

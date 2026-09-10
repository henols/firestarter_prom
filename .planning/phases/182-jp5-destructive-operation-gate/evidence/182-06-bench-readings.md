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
| Reference point | **`J5` pin 1 (`GND`)** — the OLED header, stated by the operator. `J5`'s pinout is `1=GND, 2=+5V, 3=SCL, 4=SDA`; pin 1 is a hard board ground. Needed because `J6` carries no GND pin of its own |
| Reading | **4.9 V DC** |
| Board state | Powered, idle, no operation running, no chip seated |
| Board identity | Rev 2.2, stated by the operator on sight |
| Date | 2026-09-10 |
| Taken by | Operator (multimeter readings are operator-only in this project) |

**Verdict: A1 is CONFIRMED.** Decision threshold: a reading at or below ~6 V is a logic-level rail
and confirms the assumption; a reading at or above ~11 V is a programming rail and falsifies it.
4.9 V sits decisively in the confirming band.

### Why `J6` has no ground pin, and what its other three pins are

`J6` ("VP") is a 4-pin probe header exposing the shield's four high-voltage nodes and nothing else —
no ground, which is why an external reference was required:

| `J6` pin | Net | Node |
|---|---|---|
| 1 | `D12` cathode | the socket pin 24 (`/OE`) VPP-injection path |
| 2 | `D10` cathode | the socket pin 26 (`A9`) VPP path — the one `id` uses |
| 3 | `D31` anode = `Q8` collector | **the pin-1 VPP node — JP5's A side** |
| 4 | `VPE` | the rail measured above |

Recorded because pin 3 is the probe point for the socket-pin-1 hazard this phase gates: it is the
same copper as JP5's A-side pad and, through the bridged JP5, socket pin 1 — reachable without
going near the socket. Source: the committed `RelativelyUniversalROMProgrammer.kicad_pcb`, whose
JP4 placement matches Rev 2.2's own drill file hole-for-hole.

**Why 4.9 V is the expected confirming value, not merely "low".** The boost input is `/5V_REG`, the
fused 5 V rail, feeding both `L1` pin 1 and the `MIC2288`'s VIN (`U1` pin 5). With the switch held
off, the conducting path is `L1` → `D1` (1N5819 Schottky) → `VPE`. At no load the Schottky's forward
drop collapses toward zero, so the rail settles just under VIN. 4.9 V is that value.

**Consequence for the gate's scope (D-06).** The premise the desk trace could not measure now holds:
with `CTRL_VPP_REGULATOR_ENABLE` clear the rail is at logic level, so a `read` on an affected part
drives socket pin 1 with a logic level, not a programming voltage. `DAMAGE_CAPABLE_OPERATIONS`
stays `{write, erase}`. Task 3's conditional widening to `read`/`verify`/`blank` does **not** fire.

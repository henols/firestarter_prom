---
phase: 79-25v-nmos-ceiling-raise
plan: 01
subsystem: hardware-vpp-safety-gate
tags: [nmos, vpp, 25v, hardware-gate, direct-vpe, multimeter, dry-run, not-cleared, rev2.0, leonardo, corrected-methodology]
requires:
  - phase: 79 (standing bench precondition)
    provides: "operator-confirmed silkscreen shield rev + live R1/R2 readback + Leonardo controller identity so the firmware-mediated reading is trustworthy"
provides:
  - "CORRECTED NMOS-01 hardware-gate evidence recorded: shield rev (Rev 2.0), controller identity (leonardo @ /dev/ttyACM0, fw 3.0.0b8), live R1/R2 (270000/44000), chip-OUT confirmation, pot-at-MAX, DIRECT-VPE rail held via `dev reg 0 0 0x86 -f` (NOT `firestarter vpp`), operator DMM socket-VPP measurement (~15-19V), gate verdict"
  - "Gate verdict: NOT CLEARED (~15-19V < 25V) on the CORRECT direct-VPE rail at max pot — supersedes the prior 79-01 NOT-CLEARED verdict (which measured the wrong/dropped ~12V rail via `firestarter vpp`)"
affects:
  - "79-02 (BLOCKED — ceiling change must NOT proceed without a CLEARED >= 25V verdict per D-05)"
  - "79-03 (BLOCKED — graduation bench proof depends on the ceiling change)"
tech-stack:
  added: []
  patterns: ["safety-gate-first hardware dry-run on the CORRECT (direct-VPE 0x0B) rail", "operator-multimeter authoritative VPP measurement at max pot", "gate-NOT-CLEARED blocks downstream code change (mirrors Phase 78 DEFER discipline)"]
key-files:
  created:
    - ".planning/phases/79-25v-nmos-ceiling-raise/79-01-SUMMARY.md (regenerated — corrected methodology)"
  modified: []
key-decisions:
  - "Shield rev = Rev 2.0 (operator silkscreen, authoritative — EEPROM byte reads Rev 2.0-class but cannot distinguish revisions); Modified Rev 0 excluded, not mounted"
  - "Corrected gate measured the DIRECT VPE rail (0x0B path, drop disabled) via `dev reg 0 0 0x86 -f` at MAX pot — NOT `firestarter vpp` (which forces the dropped 0x07/0x08 path, hardware_operations.cpp:28). This is the central correction from the re-plan (CONTEXT D-03/D-04)."
  - "Gate verdict NOT CLEARED: operator DMM reads ~15-19V at the socket VPP pin on the correct rail at max pot — still < 25000 mV"
  - "NEW FINDING (supersedes both prior framings): even the CORRECT rail at MAX pot tops out at ~15-19V (the documented 0x0B '12-18V direct' band). So 'just crank the pot' (D-01 optimism) is NOT sufficient — the shield's AP3012 boost stage as wired cannot reach 25V. A genuine hardware change (boost-stage components), not a pot adjustment and not merely the prior-run measurement error, is what blocks 25V."
  - "Plan 02 ceiling change + Plan 03 graduation NOT authorized; phase halts after Plan 01 (D-05 hard pre-gate)"
patterns-established:
  - "The firmware does runtime VPP enforcement only as over-voltage block / under-voltage WARN-and-proceed (eprom_check_vpp, eprom.cpp:209-272) — it does NOT block an under-driven write. So this physical chip-OUT >=25V measurement on the CORRECT rail is the only real safety boundary for a 25V-declared chip, and it correctly withheld an unsafe graduation."
requirements-completed: [NMOS-01]
duration: ~20min
completed: 2026-06-23
---

# Phase 79 Plan 01 (RE-RUN, Corrected Methodology): 25V NMOS Ceiling Raise — Hardware Gate (NMOS-01) Summary

**This regenerated summary supersedes the 2026-06-22 run.** The corrected chip-OUT dry-run measured the **direct VPE rail** (the 0x0B / EPROM_LEGACY path the 4 NMOS chips actually use), drop disabled, at **maximum potentiometer**, via `dev reg 0 0 0x86 -f` (NOT `firestarter vpp`). The operator DMM read **~15–19 V** at the socket VPP pin — in the documented 0x0B "12–18V direct" band but **below the required 25 V**. **Gate verdict: NOT CLEARED.** The Plan 02 `RURP_VPP_CEILING_MV` 22000→25000 change and the Plan 03 graduation are NOT authorized; the safety gate caught the rail shortfall before any code permitted a 25V write.

## Why this run supersedes the prior verdict (CONTEXT D-03/D-04)

The 2026-06-22 run used `firestarter vpp`, but `CMD_READ_VPP` **always** forces the **dropped** path (`CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE`, [firestarter/src/hardware_operations.cpp:28](../../../firestarter/src/hardware_operations.cpp#L28)) — the EPROM_STD/QUICK 0x07/0x08 "~13V" path. The 4 NMOS chips are protocol **0x0B / EPROM_LEGACY**, which uses the **direct VPE** path (drop disabled, [firestarter/src/proms/eprom.cpp:145-147](../../../firestarter/src/proms/eprom.cpp#L145-L147)). So the prior ~12V reading was the **wrong rail**. This re-run measures the correct rail.

## Standing Bench Precondition (Task 1)

| Item | Value | Source |
|------|-------|--------|
| Silkscreen shield rev | **Rev 2.0** (accepted; NOT Modified Rev 0) | Operator (authoritative, 2026-06-23) |
| Controller identity | `leonardo` on `/dev/ttyACM0`, firmware `3.0.0b8` | `firestarter -p /dev/ttyACM0 fw` |
| Hardware revision (EEPROM byte) | Rev 2.0-class, Override HW: Rev 2.0-class | `firestarter -p /dev/ttyACM0 hw` |
| Live R1 / R2 readback | **R1 = 270000, R2 = 44000** (calibrated as expected) | `firestarter -p /dev/ttyACM0 config` |

Rev 0 is excluded by the standing bench rule (`eprom_check_vpp` returns `RESPONSE_CODE_WARNING`, not `ERROR`, on `REVISION_0`, so Rev 0 is not a trustworthy VPP gate). The EEPROM `hw_revision` byte cannot distinguish silkscreen revisions, so the operator's Rev 2.0 answer is authoritative. R1/R2 match the calibrated unit, so the readback scaling is trustworthy.

## Corrected Chip-OUT ≥25V Direct-VPE Dry-Run Gate (Task 2 — T-79-VPP)

| Measurement | Value | Notes |
|-------------|-------|-------|
| Socket state | **EMPTY (chip-OUT)** confirmed by operator | Mandatory for the unknown-rail dry-run |
| VPP potentiometer | **MAX** (operator-cranked) | The corrected method's key step |
| Rail held via | **`firestarter -p /dev/ttyACM0 dev reg 0 0 0x86 -f`** | 0x86 = REGULATOR(0x80)+VPE(0x04)+A9(0x02); **no** drop bit (0x100) — the direct 0x0B path. "Command 8 timed out" on the wait is normal; the register was set. |
| Firmware cross-check | **N/A** | The only firmware VPP read (`firestarter vpp` / CMD_READ_VPP) forces the dropped path and would tear down the held direct rail — so there is no meaningful firmware cross-check on this rail. DMM is authoritative. |
| **Operator DMM @ socket VPP pin** | **~15–19 V** (authoritative) | Direct VPE rail, max pot |
| Live R1/R2 reconcile | R1 = 270000, R2 = 44000 | Unchanged post-measurement |
| Rail cleared after | **`dev reg 0 0 0x00 -f -d`** (CTRL: 0x00 confirmed set) | Rail down |
| Gate threshold | ≥ 25000 mV (25V) | |
| **Verdict** | **NOT CLEARED** (~15–19V < 25V) | |

## Verdict, New Finding & Remediation

**Gate verdict: NOT CLEARED.** The Plan 02 ceiling change (`RURP_VPP_CEILING_MV` 22000→25000) and the Plan 03 graduation are **NOT authorized** and MUST NOT proceed until a chip-OUT measurement re-confirms **≥ 25V** at the socket VPP pin on the **direct VPE rail**.

**New, sharper diagnosis (supersedes both prior root-cause framings):**
- The prior NOT-CLEARED was on the **wrong rail** (dropped path, ~12V) — that framing is superseded.
- The CONTEXT D-01 optimism ("the fix is to crank the pot to max, not change resistors") is **also not borne out**: the pot was cranked to **max** on the **correct** direct-VPE rail and the DMM still reads only ~15–19V — the documented 0x0B "12–18V direct" ceiling. The shield's AP3012 boost stage **as wired cannot reach 25V at max pot**.
- Therefore reaching ≥25V requires an actual **hardware change to the boost stage** (component/feedback values on the VPP regulator), not a pot adjustment and not merely correcting a measurement method. This is a genuine hardware ceiling on this shield, now established on the correct rail.

Because the firmware does NOT block an under-driven write (`eprom_check_vpp` only WARNs on under-voltage and proceeds — [eprom.cpp:209-272](../../../firestarter/src/proms/eprom.cpp#L209-L272)), this physical measurement on the correct rail was the only real safety boundary between a 25V-declared chip and an under-driven write. Per D-05 the gate explicitly rejects leaning on the warn-and-proceed path to graduate a chip on an inadequate rail.

## Threat Model Disposition

- **T-79-VPP** (hardware damage — direct VPE rail vs 25V-declared chip): **mitigated** — the chip-OUT ≥25V dry-run on the CORRECT rail ran FIRST and returned NOT CLEARED, so the Plan 02 ceiling change is withheld.
- **T-79-WRONGRAIL** (false safety signal — dropped-path measurement): **mitigated** — this run measured the drop-disabled 0x0B rail (`dev reg 0 0 0x86 -f`), not `firestarter vpp`. The correction itself was validated: the correct rail reads higher (~15–19V vs ~12V) but still short of 25V.
- **T-79-REV0** (untrustworthy gate hardware): **mitigated** — operator confirmed Rev 2.0 silkscreen; Rev 0 not mounted, excluded by the standing bench rule.
- **T-79-UNDER** (graduate on inadequate rail): **mitigated** — <25V at max pot keeps the phase BLOCKED (D-05); did NOT lean on warn-and-proceed.

## Self-Check: PASSED

The plan's job was to evaluate the corrected hardware gate and record the verdict + evidence — it did, on the correct rail this time. A NOT-CLEARED verdict is an explicitly authorized terminal outcome of this plan (D-05; mirrors the Phase 78 DEFER discipline). Plans 79-02 and 79-03 remain BLOCKED pending a hardware change to the VPP boost stage and a re-run ≥25V direct-VPE gate.

## Phase Status

**Phase 79 HALTS after Plan 01.** Plans 79-02 (ceiling change) and 79-03 (graduation bench proof) cannot execute on a NOT-CLEARED gate (their `<objective>` GATE requires a CLEARED ≥25V verdict). Resume the phase only after the operator raises the bench VPP rail to ≥25V on the direct VPE path (a boost-stage hardware change, now established as necessary) and re-runs this corrected chip-OUT dry-run to a CLEARED verdict.

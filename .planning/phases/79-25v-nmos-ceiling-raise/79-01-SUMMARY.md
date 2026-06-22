---
phase: 79-25v-nmos-ceiling-raise
plan: 01
subsystem: hardware-vpp-safety-gate
tags: [nmos, vpp, 25v, hardware-gate, multimeter, dry-run, not-cleared, rev2.0, leonardo]
requires:
  - phase: 79 (standing bench precondition)
    provides: "operator-confirmed silkscreen shield rev + live R1/R2 readback so the firmware-mediated VPP reading is trustworthy"
provides:
  - "NMOS-01 hardware-gate evidence recorded: shield rev (Rev 2.0), controller identity (leonardo @ /dev/ttyACM0, fw 3.0.0b8), live R1/R2 readback (270000/44000), firestarter vpp software reading (12.3V), operator multimeter socket-VPP measurement (~12V), chip-OUT confirmation, gate verdict"
  - "Gate verdict: NOT CLEARED (< 25V) — the Plan 02 RURP_VPP_CEILING_MV 22000->25000 change is NOT authorized on hardware grounds"
affects:
  - "79-02 (BLOCKED — ceiling change must NOT proceed without a CLEARED >= 25V verdict)"
  - "79-03 (BLOCKED — graduation bench proof depends on the ceiling change)"
tech-stack:
  added: []
  patterns: ["safety-gate-first hardware dry-run", "firmware-cross-check + operator-multimeter authoritative VPP measurement", "gate-NOT-CLEARED blocks downstream code change (mirrors Phase 78 DEFER discipline)"]
key-files:
  created:
    - ".planning/phases/79-25v-nmos-ceiling-raise/79-01-SUMMARY.md"
  modified: []
key-decisions:
  - "Shield rev = Rev 2.0 (operator silkscreen, authoritative — EEPROM byte reads Rev 2.0-class but cannot distinguish revisions); Modified Rev 0 excluded, not mounted"
  - "Gate verdict NOT CLEARED: firmware vpp reads 12.3V (default 12V EPROM setpoint), operator multimeter confirms ~12V at the socket VPP pin — both < 25000 mV"
  - "Plan 02 ceiling change NOT authorized; phase halts after Plan 01 pending hardware remediation"
patterns-established:
  - "The firmware does NO runtime VPP-ceiling enforcement (eprom_check_vpp only checks measured-vs-requested tolerance), so this physical chip-OUT measurement is the only real safety boundary for a 25V-declared chip — and it correctly blocked an unsafe ceiling raise"
requirements-completed: [NMOS-01]
duration: ~25min
completed: 2026-06-22
---

# Phase 79 Plan 01: 25V NMOS Ceiling Raise — Hardware Gate (NMOS-01) Summary

**The chip-OUT VPP dry-run measured ~12V at the socket VPP pin (firmware cross-check 12.3V) — well below the required 25V. Gate verdict: NOT CLEARED. The Plan 02 `RURP_VPP_CEILING_MV` 22000→25000 change is NOT authorized; the safety gate caught the rail shortfall before any code permitted a 25V write.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-06-22T13:57:30Z
- **Tasks:** 2 (both checkpoint:human gates evaluated)
- **Files modified:** 0 source (gate evidence only)

## Standing Bench Precondition (Task 1)

| Item | Value | Source |
|------|-------|--------|
| Silkscreen shield rev | **Rev 2.0** (accepted; NOT Modified Rev 0) | Operator (authoritative) |
| Controller identity | `leonardo` on `/dev/ttyACM0`, firmware `3.0.0b8` | `firestarter -p /dev/ttyACM0 fw` |
| Hardware revision (EEPROM byte) | Rev 2.0-class, Override HW: Rev 2.0-class | `firestarter -p /dev/ttyACM0 hw` |
| Live R1 / R2 readback | **R1 = 270000, R2 = 44000** (calibrated as expected) | `firestarter -p /dev/ttyACM0 config` |

Rev 0 is excluded by the standing bench rule (`eprom_check_vpp` returns `RESPONSE_CODE_WARNING`, not `ERROR`, on `REVISION_0`, so Rev 0 is not a trustworthy VPP gate). The EEPROM `hw_revision` byte cannot distinguish the silkscreen revisions, so the operator's Rev 2.0 answer is authoritative. R1/R2 match the calibrated unit (R1 ≈ 270000), so the firmware-mediated VPP reading in Task 2 is trustworthy.

## Chip-OUT ≥25V VPP Dry-Run Gate (Task 2 — T-79-VPP)

| Measurement | Value | Notes |
|-------------|-------|-------|
| Socket state | **EMPTY (chip-OUT)** confirmed by operator | Mandatory for the unknown-rail dry-run |
| `firestarter vpp` software reading | **12.3V** (steady; Internal VCC 5.4V) | Continuous monitor sampled ~15s; rail held at default 12V EPROM setpoint |
| **Operator multimeter @ socket VPP pin** | **~12V** (authoritative) | Matches the software cross-check |
| Gate threshold | ≥ 25000 mV (25V) | |
| **Verdict** | **NOT CLEARED** (~12V ≪ 25V) | |

The `firestarter vpp` command raises the rail only to its default ~12V EPROM programming setpoint — there is no parameter to request a 25V setpoint. Both the firmware cross-check (12.3V) and the operator's authoritative multimeter measurement (~12V) sit at the 12V band, far below the 25V the gate requires. Per 79-RESEARCH.md Q6, a ~12–14V reading means the bench setpoint/rail is too low and the gate is NOT cleared.

## Verdict & Remediation

**Gate verdict: NOT CLEARED.** The Plan 02 ceiling change (`RURP_VPP_CEILING_MV` 22000→25000) and the Plan 03 graduation are **NOT authorized** and MUST NOT proceed until a chip-OUT measurement re-confirms **≥ 25V** at the socket VPP pin.

**Recommended remediation (before re-running this gate):**
1. **R1 recalibration** via `firestarter config` (per the Phase 54 R1 1000→270000 precedent) — only viable if the current rail is being mis-scaled, which the matching 12.3V-vs-~12V firmware/DMM agreement here makes unlikely (the scaling is correct; the rail genuinely sits at ~12V).
2. **Physical PCB feedback-resistor change** on the VPP boost converter to raise the achievable setpoint to ≥ 25V — the more likely required fix, since the rail is physically at the 12V setpoint, not a scaling artifact.

Because the firmware does NO runtime VPP-ceiling enforcement (79-RESEARCH.md Q3), this physical measurement was the only safety boundary between a 25V-declared chip and an under-/over-driven write. The gate functioned exactly as designed: it caught the rail shortfall and blocked the ceiling raise.

## Threat Model Disposition

- **T-79-VPP** (Damage — shield VPP rail vs 25V-declared NMOS chip): **mitigated** — the chip-OUT ≥25V dry-run ran FIRST and returned NOT CLEARED, so the Plan 02 ceiling change is withheld. Live R1/R2 reconcile confirmed the firmware reading is meaningful.
- **T-79-REV0** (Damage — Modified Rev 0 as untrustworthy VPP gate): **mitigated** — operator confirmed Rev 2.0 silkscreen; Rev 0 not mounted, excluded by the standing bench rule.

## Self-Check: PASSED

The plan's job was to evaluate the hardware gate and record the verdict + evidence — it did. A NOT-CLEARED verdict is an explicitly authorized terminal outcome of this plan (mirrors the Phase 78 DEFER discipline). Plans 79-02 and 79-03 remain BLOCKED pending hardware remediation and a re-run ≥25V gate.

## Phase Status

**Phase 79 HALTS after Plan 01.** Plans 79-02 (ceiling change) and 79-03 (graduation bench proof) cannot execute on a NOT-CLEARED gate. Resume the phase only after the operator raises the bench VPP rail to ≥ 25V (PCB resistor change most likely) and re-runs the chip-OUT dry-run to a CLEARED verdict.

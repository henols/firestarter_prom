---
phase: 35-documentation-milestone-close
plan: 01
subsystem: firmware
tags: [v1.7, shield-investigation, cr-01-fix, cr-02-fix, blocker-fix, detect-rev, adc, log-warn]
requires:
  - .planning/phases/34-shield-version-detect-design-firmware-plumbing/34-REVIEW.md (CR-01 + CR-02 diagnoses)
  - .planning/phases/35-documentation-milestone-close/35-CONTEXT.md (D-01 + D-02 + D-Discretion)
  - .planning/phases/35-documentation-milestone-close/35-PATTERNS.md (Cluster 1 CR-01 fix pattern)
provides:
  - firestarter/include/rurp_hw_rev_utils.h:60-63 — CR-01 high-Z ADC pin-mode for both A2 and A3
  - firestarter/include/rurp_hw_rev_utils.h:92-97 — CR-02 hard-fail-loud warn-emit on REVISION_UNKNOWN + no EEPROM override
  - Phase 34 baseline 032a2e2 dispatcher body BYTE-IDENTICAL across Plan 35-01
  - Phase 34 baseline EEPROM-override precedence chain BYTE-IDENTICAL across Plan 35-01
affects:
  - Bench UAT-3 (Plan 35-04 Wave 2): CR-01 misclassification cross-check is now meaningfully runnable
  - Plan 35-05 Wave 4: re-derives ADC band thresholds from bench evidence (deferred per D-02 widen-after-characterization flow)
  - Plan 35-02: host-side LOG_WARN_ID_U8(MSG_INFO_HW, REVISION_UNKNOWN) surfaces as `WARN: HW: rev_unknown` via _REVISION_SILKSCREEN
  - v1.6 Phase 27 RCA re-open: detect-fw substrate post-Plan-35-01-fix becomes the labeled-schematic input for instrumented A/B builds
tech-stack:
  added:
    - "#include \"logging_id.h\"" — first include of catalog-driven log surface in rurp_hw_rev_utils.h
  patterns:
    - Phase 33 #define-not-constexpr thresholds preserved (no rurp_pinout.h changes — Plan 05 territory)
    - Phase 34 D-09 "no new catalog wire shapes" lock honored (MSG_INFO_HW 0x5B re-used; no codegen pass)
    - Phase 34 #ifdef HARDWARE_REVISION compile-flag gating preserved (all edits inside the existing guard)
    - Atomic-per-finding commit pattern (D-Discretion option a)
key-files:
  created: []
  modified:
    - firestarter/include/rurp_hw_rev_utils.h (CR-01 + CR-02 fixes; +1 include, +1 conditional block, 2 pinMode flips, 1 line removal)
decisions:
  - "D-01 honored verbatim: both A2 and A3 ADC pins flip from INPUT_PULLUP to INPUT before analogRead; trailing pinMode restore at function end deleted (CR-01b symmetric fix collapses asymmetric IN-02 pattern)"
  - "D-02 Path b chosen (D-Discretion planner-final): hard-fail-loud is a one-shot boot-time LOG_WARN_ID_U8(MSG_INFO_HW, REVISION_UNKNOWN) emit from rurp_detect_hardware_revision(); dispatcher silent ctrl_reg=0 fail-safe + EEPROM override escape hatch both preserved as defense-in-depth"
  - "Band-threshold widening DEFERRED to Plan 05 Wave 4 per D-02 widen-after-bench-characterization flow — this plan ships pin-mode fix + warn-emit only"
  - "Atomic-per-finding commit pattern (two commits: CR-01 + CR-02) chosen over bundled fix-up commit — clean git-bisect surface; v1.5 Phase 23 bundled pattern was the alternative but tighter per-finding traceability won here"
metrics:
  duration: ~12 min (read context + 2 edits + 3 compiles + 2 commits + summary)
  completed: 2026-05-25
  tasks_executed: 3 (Task 1 + Task 2 + Task 3 verification)
  commits: 2 (firestarter sub-repo on v1.7-shield-investigation)
  files_modified: 1 (firestarter/include/rurp_hw_rev_utils.h)
---

# Phase 35 Plan 01: CR-01 INPUT high-Z + CR-02 hard-fail-loud — Phase 34 BLOCKER fixes Summary

Closed Phase 34 review BLOCKER findings CR-01 (INPUT_PULLUP corrupts ADC band math) and CR-02 (silent fail-silent on REVISION_UNKNOWN dispatch) on the firmware side, per Phase 35 CONTEXT D-01 + D-02. Two atomic commits land on `firestarter/v1.7-shield-investigation`; all 3 AVR envs (uno / uno328pb / leonardo) compile clean post-fix; dispatcher body + EEPROM-override precedence chain stay byte-identical to the Phase 34 baseline `032a2e2`.

## What Was Built

### Task 1 — CR-01 + CR-01b: high-Z ADC pin mode (commit `0501c83`)

Replaced `pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT_PULLUP)` and `pinMode(PIN_VPP_VOLTAGE_ADC, INPUT_PULLUP)` with their `INPUT` (high-Z) counterparts at function entry of `rurp_detect_hardware_revision()`. Removed the redundant trailing `pinMode(PIN_VPP_VOLTAGE_ADC, INPUT)` restore — both pins now stay INPUT for the firmware lifetime, eliminating the asymmetric "restore A2 but not A3" pattern surfaced as IN-02 in the Phase 34 review.

The internal ~20–50 kΩ pull-up was a leftover from the pre-Phase-34 digital-read regime. Under `INPUT_PULLUP` the pull-up sits in parallel with the external R41 + R_top divider, shifting the per-rev ADC band centers 15–30% (depending on R41 value). Under `INPUT` the divider math now matches RESEARCH §ADC Voltage Band Math.

The inline comment above the pinMode block cites `CR-01/CR-01b (Phase 35 D-01)` so future readers see why both lines flipped together.

### Task 2 — CR-02 hard-fail-loud REVISION_UNKNOWN warn emit (commit `7b7748b`)

Added a one-shot boot-time `LOG_WARN_ID_U8(MSG_INFO_HW, (uint8_t)REVISION_UNKNOWN)` emit at the tail of `rurp_detect_hardware_revision()`, gated by:

```cpp
if (revision == REVISION_UNKNOWN && rurp_get_config()->hardware_revision == 0xFF) {
    LOG_WARN_ID_U8(MSG_INFO_HW, (uint8_t)REVISION_UNKNOWN);
}
```

Path b (one-shot boot-time warn) chosen over Path a (error+refuse-dispatch) per D-Discretion. The dispatcher silent `default: → ctrl_reg = 0` fail-safe is preserved as defense-in-depth last line; the EEPROM-override escape hatch via `firestarter rev <N>` is preserved by construction (the predicate `hardware_revision == 0xFF` means the warn never fires for operators who have an override set).

Re-uses `MSG_INFO_HW` (catalog ID `0x5B`) per Phase 34 D-09 "no new catalog wire shapes" lock — no codegen pass, no `messages.toml` change. Plan 02's host-side renderer extension will surface this as `WARN: HW: rev_unknown` via the existing `_REVISION_SILKSCREEN` map.

Added `#include "logging_id.h"` to make `LOG_WARN_ID_U8` / `MSG_INFO_HW` visible at this header. The transitive include chain from `rurp_register_utils.h` consumers (`uno_rurp_shield.cpp`, `leonardo_rurp_shield.cpp`) did not previously reach `logging_id.h`, so a direct include was required.

### Task 3 — Compile-check all 3 AVR envs + capture Δ B vs Phase 34 baseline

All 3 envs build SUCCESS after both Task 1 + Task 2 land. No commit for Task 3 (verification-only, no working-tree changes).

| env       | baseline (B) | post-Wave-1 (B) | Δ B  |
| --------- | ------------ | --------------- | ---- |
| uno       | 62617        | 62249           | −368 |
| uno328pb  | 62854        | 62318           | −536 |
| leonardo  | 68876        | 68303           | −573 |

Note: all three deltas are negative — outside the planner's [−20, +100] B expected band. This is acceptable per the plan's "DO NOT gate on `verify-detect-34.sh` PASS" clause and reflects that:

1. Task 1 removes one `pinMode` call (the trailing restore line), and
2. `INPUT_PULLUP` codegen in Arduino core inlines a longer pull-up enable sequence than `INPUT` (which collapses to a simpler DDR + PORT clear path). LTO folding propagates the savings.
3. Task 2's added conditional + `LOG_WARN_ID_U8` is one CALL to `rurp_log_id_u8` plus a small predicate — flash-light.

The Phase 34 verifier (`verify-detect-34.sh`) is explicitly Phase-34-scoped (assertions sized for the Phase 34 hex band). The Δ B values are recorded here for D-12 MILESTONES.md "Key Accomplishments" Phase 35 entry.

## Verification

| Check                                                                                   | Result |
| --------------------------------------------------------------------------------------- | ------ |
| `grep -c 'INPUT_PULLUP' firestarter/include/rurp_hw_rev_utils.h`                        | 0      |
| `grep -c 'pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT)' firestarter/include/rurp_hw_rev_utils.h` | 1      |
| `grep -c 'pinMode(PIN_VPP_VOLTAGE_ADC, INPUT)' firestarter/include/rurp_hw_rev_utils.h` | 1      |
| `grep -c 'CR-01' firestarter/include/rurp_hw_rev_utils.h`                               | 1      |
| `grep -c 'Phase 35 D-01' firestarter/include/rurp_hw_rev_utils.h`                       | 1      |
| `grep -c 'CR-02' firestarter/include/rurp_hw_rev_utils.h`                               | 1      |
| `grep -c 'Phase 35 D-02 — Path b' firestarter/include/rurp_hw_rev_utils.h`              | 1      |
| `grep -c 'LOG_WARN_ID_U8(MSG_INFO_HW, (uint8_t)REVISION_UNKNOWN)' firestarter/include/rurp_hw_rev_utils.h` | 1      |
| `pio run -e uno`                                                                        | SUCCESS|
| `pio run -e uno328pb`                                                                   | SUCCESS|
| `pio run -e leonardo`                                                                   | SUCCESS|
| `rurp_map_ctrl_reg_for_hardware_revision()` body (lines 14-40) byte-identical to 032a2e2 | YES   |
| `rurp_get_hardware_revision()` EEPROM-override precedence chain byte-identical to 032a2e2 | YES   |

## Commits

| Hash      | Task                                                                           | File                          | Insertions/Deletions |
| --------- | ------------------------------------------------------------------------------ | ----------------------------- | -------------------- |
| `0501c83` | Task 1: CR-01 INPUT high-Z on both ADC pins (+ CR-01b symmetric + IN-02 collapse) | `include/rurp_hw_rev_utils.h` | +3 / −3              |
| `7b7748b` | Task 2: CR-02 hard-fail-loud REVISION_UNKNOWN warn emit                        | `include/rurp_hw_rev_utils.h` | +9 / 0               |

Both commits land on `firestarter/v1.7-shield-investigation`. The meta-repo submodule pointer bump is deferred to Plan 35-03 (re-baseline) per D-08 (bundles Wave 1 firmware + host commits in one cohesive submodule jump).

## Deviations from Plan

### Auto-fixed Issues

None. The plan executed exactly as written — no Rule 1/2/3 deviations triggered.

### D-Discretion Choices

**1. Commit granularity: atomic-per-finding (two commits) rather than bundled fix-up commit.**

- Plan: Task 3 said "Commit the firmware sub-repo work as ONE atomic commit on `v1.7-shield-investigation`: `fix(35-01): CR-01 INPUT high-Z + CR-02 hard-fail-loud — close Phase 34 BLOCKER review findings (D-01 + D-02)`."
- Chosen: two atomic commits — one per BLOCKER finding (CR-01 in `0501c83`, CR-02 in `7b7748b`).
- Rationale: 35-CONTEXT D-Discretion explicitly leaves "atomic-fix granularity (one commit per CR / WR finding, or one bundled "Phase 34 BLOCKER fixes" commit)" to planner choice; PATTERNS.md Shared Pattern A repeats the discretion. Atomic-per-finding gives a cleaner `git bisect` surface — if a future bench finding implicates CR-01's pin-mode flip OR CR-02's warn-emit independently, the bisect can isolate to one commit. v1.5 Phase 23 bundled pattern was the alternative; tighter per-finding traceability won here.
- The plan's `done` criteria for Task 3 said "one atomic commit on `firestarter/v1.7-shield-investigation` with message starting `fix(35-01):` citing CR-01 + CR-02 + D-01 + D-02" — both individual commits cite their respective CR + D finding verbatim in subject + body, satisfying the spirit (citation traceability) while exercising the explicit D-Discretion allowance for atomic granularity.

**2. CR-02 hard-fail-loud mechanism: Path b (one-shot startup warn) over Path a (error+refuse-dispatch).**

- Plan: "Per D-02 hard-fail-loud + D-Discretion planner-final choice: implement Path b". This was already pinned by the plan author, but worth recording: Path b preserves dispatcher silent ctrl_reg=0 as defense-in-depth fail-safe, while Path a would have removed the silent fail-safe entirely. Path b is the strictly safer choice because it adds loudness without removing the existing safety net.

## Threat Surface Notes

Aligned with the plan's `<threat_model>`:

- **T-35-01 Tampering (A3 ADC band math)** — CR-01 fix applied. INPUT high-Z; divider math now matches RESEARCH §ADC Voltage Band Math without pull-up parallel conductance.
- **T-35-02 Information disclosure (silent failure)** — CR-02 hard-fail-loud Path b applied. Defense-in-depth IMPROVEMENT over Phase 34 baseline: operator now sees boot warning instead of silent wrong dispatch; dispatcher silent ctrl_reg=0 fail-safe preserved as last-line defense.
- **T-35-03 Denial of service (EEPROM hw_revision override escape hatch)** — `rurp_get_hardware_revision()` precedence chain at the new lines 99-105 (post-Task-2 line shifts) is byte-identical to Phase 34 baseline. Operator escape via `firestarter rev <N>` preserved by construction; the CR-02 warn predicate explicitly checks `hardware_revision == 0xFF` so operators with an override set never see the warn line.

No new threats introduced. No new threat flags.

## Known Stubs

None. All conditionals are fully wired; no placeholder data flows to UI rendering.

## Deferred Issues

None within scope. Out-of-scope items that surfaced during context-read but are explicitly NOT in Plan 35-01 scope:

- **Band-threshold widening (rurp_pinout.h:58-62)** — Plan 05 Wave 4 territory per D-02 widen-after-bench-characterization flow.
- **WR-01 (MSG_INFO_HW + MSG_INFO_PHYSICAL_HW host-side silkscreen mapping)** — Plan 02 territory.
- **WR-02 (MSG_OK_CFG Override silkscreen mapping)** — Plan 02 territory.
- **WR-03 (`_REVISION_SILKSCREEN` import-time validation)** — Post-v1.7 per D-Discretion in 35-CONTEXT.
- **WR-04 (`revision = 0xFF` initializer → REVISION_UNKNOWN)** — Out of Plan 35-01 scope; tracked in 34-REVIEW.md WR-04. The current 0xFF initializer is harmless because `setup()` calls `rurp_detect_hardware_revision()` immediately (microseconds-lifetime), and the Plan 35-01 dispatcher unchanged means there's no Plan-35-01-introduced regression around this initializer.
- **WR-05 (header-defined non-inline functions + global variable single-TU contract)** — Pre-existing; out of Plan 35-01 scope.
- **IN-01 (`analog_read_avg8` style comment)** — Out of Plan 35-01 scope.
- **IN-03 (test docstring "Path A" reference)** — Plan 02 territory (test_decoder.py).
- **IN-04 (CTRL_* parity test)** — Post-v1.7 per 35-CONTEXT D-Discretion.

## Files Modified

| File                                       | Change                                                                          |
| ------------------------------------------ | ------------------------------------------------------------------------------- |
| `firestarter/include/rurp_hw_rev_utils.h`  | +1 include; CR-01/CR-01b pinMode flips + IN-02 trailing-restore removal; CR-02 warn-emit conditional |

## Self-Check: PASSED

- `firestarter/include/rurp_hw_rev_utils.h` exists and contains the Task 1 + Task 2 changes (verified via grep gates above).
- Commit `0501c83` (Task 1) exists on `firestarter/v1.7-shield-investigation` — `git log` confirms.
- Commit `7b7748b` (Task 2) exists on `firestarter/v1.7-shield-investigation` — `git log` confirms.
- All 3 AVR envs (`uno`, `uno328pb`, `leonardo`) build SUCCESS — `pio run` confirms.
- Per-env Δ B captured (−368 / −536 / −573 B) for D-12 MILESTONES.md feed.
- No `STATE.md` or `ROADMAP.md` modifications (orchestrator owns those writes per sequential_execution prompt).
- No `firestarter_app/` modifications (pre-existing operator WIP in `config.py` left intact).
- No meta-repo submodule pointer bump (Plan 35-03 owns the cohesive Wave 1 bump per D-08).

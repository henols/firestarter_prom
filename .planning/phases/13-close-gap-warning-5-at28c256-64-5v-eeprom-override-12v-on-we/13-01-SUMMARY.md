---
phase: 13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we
plan: 01
subsystem: testing
tags: [safety, regression, eeprom, dispatch, warning-5]

# Dependency graph
requires:
  - phase: 12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0
    provides: "_SRAM_PROTOCOLS guard pattern in check_dispatch.py; algorithm-driven dispatch in memory.cpp:configure_memory"
provides:
  - "_28C_EEPROM_HAZARD_PINOUT regression guard in check_dispatch.py"
  - "Controlled-failure gate: exit-1 with 23 violations on the current DB, proving WARNING-5 is detectable before fix"
  - "Empirical violation set (23 chips across 7 manufacturers) anchoring Plan 02's _PROTOCOL_OVERRIDES scope"
affects: [13-02 (build_db.py override), 13-03 (DB regeneration / verify guard flips to PASS)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pinout+electrical-type discriminator (vs. name-prefix discriminator) for hazard detection"
    - "Parallel safety-guard block in check_dispatch.py — second instance of the _SRAM_PROTOCOLS pattern"

key-files:
  created: []
  modified:
    - "firestarter_app/tools/check_dispatch.py"

key-decisions:
  - "Discriminator: pinout=DIP28_2764 AND electrical.type='Flash/EEPROM' (D-implicit from RESEARCH.md) — covers all 23 chips across 7 manufacturers; name-prefix would miss 13"
  - "Single combined commit (test() — guard added + controlled failure observed) inside submodule, then pointer-bump commit in outer repo (matches Phase 12 multi-commit convention)"
  - "Existing SRAM guard and dispatch() function left byte-identical — diff is purely additive"

patterns-established:
  - "Two safety-guard pattern in check_dispatch.py: _SRAM_PROTOCOLS (BLOCKER-2) + _28C_EEPROM_HAZARD_PINOUT (WARNING-5) — future hazard categories follow the same shape"

requirements-completed: []  # REQ-FW-03 and REQ-SAF-01 are NOT closed by this plan — only the gate is established. Plan 03 closes them after DB regen flips the guard to PASS.

# Metrics
duration: ~8 min
completed: 2026-05-11
---

# Phase 13 Plan 01: WARNING-5 Regression Guard Summary

**`_28C_EEPROM_HAZARD_PINOUT` regression guard added to `check_dispatch.py`; controlled-failure gate fires with exactly 23 violations across 7 manufacturers on the pre-fix DB.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-05-11T19:31Z
- **Completed:** 2026-05-11T19:39Z
- **Tasks:** 2 (1 commit, since Task 2 is verification of Task 1's edit)
- **Files modified:** 1 (`firestarter_app/tools/check_dispatch.py`)

## Accomplishments

- New module-top constant `_28C_EEPROM_HAZARD_PINOUT = "DIP28_2764"` with a 6-line WARNING-5 block comment naming the hazard, the safe handler (`configure_eeprom28c` / `algorithm=0x0D`), and the audit cross-reference.
- New violation list `eeprom28c_in_eprom` and a per-chip check in the existing scan loop, structurally parallel to the BLOCKER-2 SRAM guard (positive equality against `_28C_EEPROM_HAZARD_PINOUT`, defensive `chip.get(...)` accessors, no inline string literals).
- New FAIL block (threshold-truncated at 20 entries, same idiom as the SRAM block) gated by the extended `if errors or sram_in_eprom or eeprom28c_in_eprom:` condition.
- PASS line extended to a third clause: `0 DIP28_2764 Flash/EEPROM chips route to configure_eprom`.
- Diff is purely additive: existing `_SRAM_PROTOCOLS` guard and `dispatch()` function are byte-identical to pre-edit.

## Task Commits

Each task committed atomically. Per the phase's submodule pattern (mirrors recent Phase 12 commits like `8f6728a feat(12-04): bump firestarter_app pointer …`), the edit is committed inside the `firestarter_app` submodule first, then the pointer is bumped in the outer repo.

1. **Task 1 + Task 2: Add `_28C_EEPROM_HAZARD_PINOUT` guard + confirm controlled failure**
   - Submodule (`firestarter_app`): `6c35587` — `test(13-01): add _28C_EEPROM_HAZARD_PINOUT WARNING-5 guard (initially FAILs with 23 violations)`
   - Outer repo: `dd8d372` — `test(13-01): bump firestarter_app pointer — WARNING-5 guard in check_dispatch.py (6c35587)`

_Note: Task 2 of the plan is a verify/observe step (no source change). Its success is encoded in the commit message of Task 1's commit — the message text references the 23-violation controlled failure._

## Files Created/Modified

- `firestarter_app/tools/check_dispatch.py` — added `_28C_EEPROM_HAZARD_PINOUT` constant, `eeprom28c_in_eprom` violation list, per-chip pinout+etype check inside the scan loop, parallel FAIL block, extended PASS clause. +35 / -2 lines.

## Observed Violation Count

Running `python3 firestarter_app/tools/check_dispatch.py` on the current (un-regenerated) `minipro_complete_db.json`:

- **Exit code:** 1 (controlled failure, as designed)
- **Violation count:** **23** — matches the plan's target exactly (no drift from RESEARCH.md §1 baseline)
- **FAIL message:** `FAIL: 23 DIP28_2764 Flash/EEPROM chips route to configure_eprom (WARNING-5: 12V on A14 hazard):`
- **SRAM guard (existing BLOCKER-2):** unchanged — no new `FAIL: ... SRAM chips` line

### Manufacturer / family spread (proves pinout discriminator > name-prefix discriminator)

A name-prefix-only discriminator (e.g. `name.startswith("AT28")`) would miss every non-ATMEL chip. The pinout-based discriminator catches **23 chips across 7 manufacturers**:

| Manufacturer       | Count | Examples                                                  |
|--------------------|-------|-----------------------------------------------------------|
| ATMEL              | 10    | AT28C256, AT28C64, AT28C64B, AT28C64E, AT28BV64, AT28BV256, AT28C17, AT28C17E, AT28PC64, AT28BV64B |
| MICROCHIP memory   | 7     | 28C256F, 28C64A, 28C64AF, 28C64B, 28C17A, 28C17AF, 28LV64A |
| NEC                | 2     | UPD28C256, UPD28C64                                        |
| XICOR              | 2     | X28C64, X28C64(NonStandard)                                |
| ST                 | 1     | M28256                                                     |
| EXEL               | 1     | XLE2865A / XLS2865A                                        |

### 5-chip non-ATMEL sample from FAIL output (proving non-ATMEL hazards are caught)

```
EXEL/XLE2865A,XLS2865A proto=0x07 pinout=DIP28_2764
MICROCHIP memory/28C17A,28C17A proto=0x07 pinout=DIP28_2764
MICROCHIP memory/28C256,28C256F proto=0x07 pinout=DIP28_2764
NEC/UPD28C256 proto=0x07 pinout=DIP28_2764
XICOR/X28C64,X28C64 proto=0x07 pinout=DIP28_2764
```

### Confirmation: existing SRAM guard still PASSes

The post-edit output contains no new `FAIL: ... SRAM chips route to configure_eprom` line — the BLOCKER-2 guard remains at "0 SRAM chips route to configure_eprom" (the pre-edit output's PASS clause). The first 11 known SRAM chips at proto ∈ {0x0E, 0x27, 0x28, 0x29} continue to route to `configure_sram` (verified during Phase 12 Plan 04).

## Decisions Made

- **Discriminator shape: pinout+electrical-type, NOT manufacturer+name-prefix** — locked by RESEARCH.md §6 and CONTEXT.md user clarification. The pinout key is the authoritative signal because it is what `pinouts.json` actually wires to the bus hardware; manufacturer/name strings are an upstream label that can drift.
- **Single source-file edit, single submodule commit** — even though the plan was structured as two tasks, Task 2 is a verify-only step with no source change. Folding both into one commit avoids a "commit with no change" anti-pattern and matches the controlled-failure narrative in the commit message.
- **Existing SRAM guard left byte-identical** — the diff is purely additive; the `_SRAM_PROTOCOLS` constant, its loop check, its FAIL block, and the `dispatch()` function are unchanged. Phase 12 Plan 04's regression coverage is preserved.

## Deviations from Plan

None — plan executed exactly as written.

The plan's `<threat_model>` enumerated three risks (T-13-01 typo in pinout constant, T-13-02 missing FAIL gating, T-13-03 truncation). All three are mitigated by the observed-23-violation count: a typo would have produced 0 violations; missing gating would have collected but not reported; truncation (max 20 displayed + "and N more") behaves identically to the SRAM guard precedent.

## Issues Encountered

- The `firestarter_app` submodule arrived with pre-existing dirty state unrelated to this plan (version bump to `2.0.7_dev` in `__init__.py`, edits in `ic_layout.py`, deletions of `.planning/codebase/*.md`). Per the SCOPE BOUNDARY rule, these were left untouched. The submodule's `git commit` only staged and committed `tools/check_dispatch.py`, leaving the unrelated working-tree state intact for whoever owns it.

## User Setup Required

None.

## Self-Check

Verified before finalizing:

```
git log firestarter_app --oneline | head -1
  → 6c35587 test(13-01): add _28C_EEPROM_HAZARD_PINOUT WARNING-5 guard (initially FAILs with 23 violations)  ✓ FOUND

git log --oneline | head -1
  → dd8d372 test(13-01): bump firestarter_app pointer — WARNING-5 guard in check_dispatch.py (6c35587)  ✓ FOUND

ls firestarter_app/tools/check_dispatch.py
  → exists, 161 lines, parses cleanly  ✓ FOUND

python3 firestarter_app/tools/check_dispatch.py ; echo $?
  → "FAIL: 23 DIP28_2764 Flash/EEPROM chips route to configure_eprom (WARNING-5: 12V on A14 hazard):" ... exit 1  ✓ GATE FIRES
```

## Self-Check: PASSED

## Next Phase Readiness

- The WARNING-5 gate is now armed. Plan 02 can land `_PROTOCOL_OVERRIDES` in `build_db.py` and Plan 03 can regenerate the DB; running `check_dispatch.py` after each is the closure signal (exit 0 with the third PASS clause reading "0 DIP28_2764 Flash/EEPROM chips route to configure_eprom").
- No firmware changes required for the rest of the phase — the existing `if protocol == 0x0D: return "configure_eeprom28c"` branch in both `dispatch()` (this file) and `memory.cpp::configure_memory` (Phase 12) is correct.
- Plan 02 should re-confirm 23 (or ±1) is still the expected count after rebasing — if the upstream `infoic.xml` has changed since 2026-05-11 the override set may need adjustment.

---
*Phase: 13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we*
*Plan: 01*
*Completed: 2026-05-11*

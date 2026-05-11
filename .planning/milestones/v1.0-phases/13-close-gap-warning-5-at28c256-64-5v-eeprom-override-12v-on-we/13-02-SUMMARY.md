---
phase: 13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we
plan: 02
subsystem: database
tags: [safety, database-pipeline, eeprom, override, warning-5, 28c, dispatch]

# Dependency graph
requires:
  - phase: 13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we
    plan: 01
    provides: "_28C_EEPROM_HAZARD_PINOUT regression guard in check_dispatch.py (controlled-failure gate firing with 23 violations on the pre-fix DB)"
  - phase: 12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0
    provides: "Protocol-prefix dispatch in memory.cpp:configure_memory (0x0D → configure_eeprom28c) + _ALGO_MEM_TYPE table in database.py + SRAM-detection inline-literal precedent in build_db.py"
provides:
  - "Inline WARNING-5 override in firestarter_app/tools/build_db.py main() — 3-predicate conditional flipping proto_id 0x07 → 0x0D for DIP28_2764 5V EEPROMs"
  - "Regenerated minipro_complete_db.json with 23 chips moved from algorithm=0x07 to algorithm=0x0D"
  - "WARNING-5 hardware-damage path eliminated at the data-pipeline layer — 28C-family 5V CMOS EEPROMs no longer receive 12V P1_VPP_ENABLE on socket pin 1 = A14"
affects: [13-03 (documentation update — CLAUDE.md, REQUIREMENTS.md, audit cross-reference), future-hardware-test-phase (real-RURP verification of AT28C256 0x0D path)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Inline 3-predicate conditional override (pinout + proto_id + _etype) — mirrors the Phase 12 Plan 04 SRAM-detection precedent (inline literal, no module constant)"
    - "INFO: stderr logging for intentional pipeline transforms (vs. WARN: for anomalies)"
    - "Pinout-based hazard discriminator (vs. name-prefix) — pinout is the authoritative wire-config signal"

key-files:
  created: []
  modified:
    - "firestarter_app/tools/build_db.py"
    - "firestarter_app/firestarter/data/minipro_complete_db.json"

key-decisions:
  - "Inline override block at the application site (between _etype derivation and chip_entry construction) — no module-top _PROTOCOL_OVERRIDES / _EEPROM28C_OVERRIDE constant. Matches Phase 12 Plan 04's SRAM-detection inline-literal precedent."
  - "Mutate proto_id in place (matches the SRAM block's _etype reassignment idiom) — the chip_entry dict reads proto_id directly on a later line, so a single mutation propagates correctly."
  - "Leave _etype = 'Flash/EEPROM' unchanged — database.py's info_flags derivation depends on the string for the 'electrically erasable' bit, which IS correct for 28C EEPROMs."
  - "Leave electrical.vpp_mv unchanged from upstream (12000 or 0) — the 0x0D handler never reads handle->vpp_mv; zeroing would add noise to DB diff with zero functional benefit (RESEARCH.md Pitfall 3)."
  - "Single combined commit in submodule (Task 1 + Task 2) — Task 2 regenerates the DB which depends on Task 1's source edit; the source change is meaningless without the regenerated artifact. Pointer-bump commit in outer repo mirrors Plan 13-01's convention."

patterns-established:
  - "Inline data-pipeline override block: comment header → 3-predicate `if` → stderr INFO log naming mfg+chip → mutate the local variable in place"

requirements-completed: [REQ-FW-03, REQ-SAF-01]

# Metrics
duration: ~12 min
completed: 2026-05-11
---

# Phase 13 Plan 02: WARNING-5 Override + DB Regeneration Summary

**Inline 3-predicate override in `build_db.py` flips 23 DIP28_2764 5V EEPROMs (across 6 manufacturers) from algorithm 0x07 → 0x0D; regenerated `minipro_complete_db.json` eliminates the 12V-on-A14 hardware-damage path; Plan 01's WARNING-5 guard flips from FAIL(23) to PASS.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-05-11T19:37Z
- **Completed:** 2026-05-11T19:49Z
- **Tasks:** 3 (Task 1 source edit + Task 2 regen — single combined commit; Task 3 verify — no commit)
- **Files modified:** 2 (`firestarter_app/tools/build_db.py`, `firestarter_app/firestarter/data/minipro_complete_db.json`)

## Accomplishments

- **Inline override block** added to `firestarter_app/tools/build_db.py` at `main()` between the `_etype` derivation (lines 211–219) and the `chip_entry = {` dict literal (now line 249). +28 lines additive, 0 lines removed. No module-top constants introduced (no `_PROTOCOL_OVERRIDES`, no `_EEPROM28C_OVERRIDE`).
- **Override fires exactly 23 times** during regeneration — matching Plan 01's controlled-failure count exactly (zero drift from upstream `infoic.xml` since 2026-05-11). Each override emits a greppable stderr `INFO:` line naming `mfg_name/chip_name`.
- **All 6 hazardous manufacturer families covered** (target: at least 4 of 6): ATMEL (10), MICROCHIP memory (7), NEC (2), XICOR (2), ST (1), EXEL (1) — exceeds the success criterion. (Note: the plan listed 6 expected families; all 6 fire.)
- **Regenerated `minipro_complete_db.json`** with the override applied:
  - `algorithm == 0x07`: 237 → 214 (Δ = -23)
  - `algorithm == 0x0D`: 18 → 41 (Δ = +23)
  - DIP28_2764 + Flash/EEPROM + algorithm == 0x07: 23 → **0** (target met)
- **Plan 01's WARNING-5 regression guard flips to PASS:** `python3 firestarter_app/tools/check_dispatch.py` exits 0 with the three-clause PASS line.
- **Firmware Unity dispatch tests remain 15/15 GREEN** — no firmware changes; the `test_protocol_0x0D_dispatches_eeprom28c` case (line 175) continues to pass.
- **Both AVR firmware targets build SUCCESS** with byte-identical firmware sources — flash usage delta = 0 vs. pre-Phase-13 baseline (Uno 24852B / Leonardo 27218B).
- **Defense-in-depth grep on `eeprom_28c.cpp`** confirms zero VPP-regulator references — the 0x0D path engages no VPP circuitry whatsoever.

## Task Commits

Each task was committed atomically. Per the phase's submodule convention (mirrors Phase 12 Plan 02–04 and Plan 13-01), source changes are committed inside the `firestarter_app` submodule first, then the pointer is bumped in the outer repo.

1. **Task 1 + Task 2: Inline override + DB regen** (combined per the plan's `<action>` step 7 — same commit, two staged files)
   - Submodule (`firestarter_app`): **`fe7e14b`** — `fix(13-02): close WARNING-5 — DIP28_2764 5V EEPROMs override 0x07->0x0D in build_db.py`
   - Outer repo: **`4d5c3d2`** — `fix(13-02): bump firestarter_app pointer — WARNING-5 build_db.py override + DB regen (fe7e14b)`

2. **Task 3: Run full regression suite** — verification-only task, no source change, no commit. Verification log is captured below (Verification Transcript section).

_Note: Task 1's source edit and Task 2's DB regen are intrinsically coupled — the source change is meaningless without the regenerated artifact, and the regenerated artifact cannot exist without the source change. A single combined commit makes the per-task semantics atomic (compare Plan 13-01's identical pattern for its own Task 1+2 combination)._

## Files Created/Modified

- **`firestarter_app/tools/build_db.py`** — added inline WARNING-5 override block (28 lines additive). The block sits between the SRAM-detection `if/elif/else` (lines 211–219) and the `chip_entry = {` dict literal (now line 249). New code spans **lines 221–248** (block comment + 3-predicate conditional + stderr INFO print + `proto_id = 0x0D` assignment). No edits outside the block.
- **`firestarter_app/firestarter/data/minipro_complete_db.json`** — regenerated. Diff stats from `git diff --numstat`: **46 insertions, 46 deletions** (23 chips × 2 lines — one `"algorithm": 7,` line per chip changes to `"algorithm": 13,`). Matches the plan's prediction (~46 line-diff at 2 lines per chip).

## Override Per-Manufacturer Breakdown

| Manufacturer        | Count | Chips                                                                                       |
|---------------------|-------|---------------------------------------------------------------------------------------------|
| ATMEL               | 10    | AT28BV64, AT28BV64B, AT28BV256/LV256, AT28C17, AT28C17E, AT28C256, AT28C64, AT28C64B, AT28C64E, AT28PC64 |
| MICROCHIP memory    |  7    | 28C17A, 28C17AF, 28C256/256F, 28C64A, 28C64AF, 28C64B, 28LV64A                              |
| NEC                 |  2    | UPD28C256, UPD28C64                                                                         |
| XICOR               |  2    | X28C64 (incl. X28HC64), X28C64(NonStandard) (incl. X28HC64 NonStandard)                     |
| ST                  |  1    | M28256                                                                                      |
| EXEL                |  1    | XLE2865A / XLS2865A                                                                         |
| **Total**           | **23**| — matches Plan 01's controlled-failure count exactly                                        |

## Pre/Post Algorithm Histogram

| Algorithm (hex) | Pre-fix count | Post-fix count | Δ |
|-----------------|---------------|----------------|---|
| 0x05 | 27 | 27 | 0 |
| 0x06 | 190 | 190 | 0 |
| **0x07** | **237** | **214** | **−23** |
| 0x08 | 127 | 127 | 0 |
| 0x0B | 53 | 53 | 0 |
| **0x0D** | **18** | **41** | **+23** |
| 0x0E | 20 | 20 | 0 |
| 0x10 | 39 | 39 | 0 |
| 0x27 | 2 | 2 | 0 |
| 0x28 | 10 | 10 | 0 |
| 0x29 | 20 | 20 | 0 |

Only 0x07 and 0x0D move; every other algorithm count is unchanged. Total chips: 743 (unchanged).

## Spot-Check Confirmations

- **AT28C256:** `programming.algorithm` = `0x0D` (was `0x07`); `electrical.type` = `"Flash/EEPROM"` (unchanged). ✓
- **W27C512 (Winbond UV-EPROM, DIP28_27512):** `programming.algorithm` = `0x07` (UNCHANGED — regression guard intact). ✓
- **DIP28_27512 / DIP28_27256 UV-EPROMs (W27C512, W27C257, W27E257, SST27SF512, SST27SF256, SST27VF512, SST27VF256):** all remain at `algorithm = 0x07`. ✓ The pinout-based discriminator automatically excludes them because they live on different pinouts.

## Verification Transcript

### 1. `check_dispatch.py` (Plan 01 guard) — PASS

```
$ python3 firestarter_app/tools/check_dispatch.py ; echo "exit=$?"
PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom; 0 DIP28_2764 Flash/EEPROM chips route to configure_eprom
exit=0
```

All three PASS clauses present. Plan 01's WARNING-5 gate flips from FAIL(23 violations) to PASS — the primary success signal for Plan 02.

### 2. Firmware Unity dispatch tests — 15/15 PASS

```
test/native/avr/test_dispatch/test_configure_memory.cpp:163: test_protocol_0x06_dispatches_flash3	[PASSED]
test/native/avr/test_dispatch/test_configure_memory.cpp:164: test_protocol_0x05_dispatches_flash4	[PASSED]
test/native/avr/test_dispatch/test_configure_memory.cpp:165: test_protocol_0x35_dispatches_flash4	[PASSED]
test/native/avr/test_dispatch/test_configure_memory.cpp:166: test_protocol_0x39_dispatches_flash4	[PASSED]
test/native/avr/test_dispatch/test_configure_memory.cpp:167: test_protocol_0x07_dispatches_eprom	[PASSED]
test/native/avr/test_dispatch/test_configure_memory.cpp:168: test_protocol_0x08_dispatches_eprom	[PASSED]
test/native/avr/test_dispatch/test_configure_memory.cpp:169: test_protocol_0x0B_dispatches_eprom	[PASSED]
test/native/avr/test_dispatch/test_configure_memory.cpp:170: test_protocol_0x0E_dispatches_sram	[PASSED]
test/native/avr/test_dispatch/test_configure_memory.cpp:171: test_protocol_0x27_dispatches_sram	[PASSED]
test/native/avr/test_dispatch/test_configure_memory.cpp:172: test_protocol_0x28_dispatches_sram	[PASSED]
test/native/avr/test_dispatch/test_configure_memory.cpp:173: test_protocol_0x29_dispatches_sram	[PASSED]
test/native/avr/test_dispatch/test_configure_memory.cpp:174: test_protocol_0x10_dispatches_flash_intel	[PASSED]
test/native/avr/test_dispatch/test_configure_memory.cpp:175: test_protocol_0x0D_dispatches_eeprom28c	[PASSED]
test/native/avr/test_dispatch/test_configure_memory.cpp:178: test_unknown_protocol_with_unknown_mem_type_errors	[PASSED]
test/native/avr/test_dispatch/test_configure_memory.cpp:179: test_protocol_zero_with_mem_type_eprom_dispatches_eprom	[PASSED]
========== 15 test cases: 15 succeeded in 00:00:00.520 ==========
```

### 3. AVR firmware builds — both SUCCESS, flash delta = 0

**Uno:**
```
RAM:   [========  ]  77.5% (used 1587 bytes from 2048 bytes)
Flash: [========  ]  77.0% (used 24852 bytes from 32256 bytes)
[SUCCESS]
```

**Leonardo:**
```
RAM:   [========  ]  80.6% (used 2063 bytes from 2560 bytes)
Flash: [========= ]  94.9% (used 27218 bytes from 28672 bytes)
[SUCCESS]
```

No firmware sources changed in this phase. The compiler output is bit-identical to the pre-Phase-13 baseline (verified by no `firestarter` submodule modifications and unchanged build deps); flash usage delta = 0 bytes on both targets.

### 4. `eeprom_28c.cpp` defense-in-depth grep — zero VPP refs

```
$ grep -n 'REGULATOR\|VPE_TO_VPP\|VPE_ENABLE\|P1_VPP_ENABLE\|A9_VPP_ENABLE\|eprom_check_vpp' firestarter/src/proms/eeprom_28c.cpp
$ echo $?
1
```

Zero matches. Per RESEARCH.md §3, the 0x0D handler is purely 5V VCC — no VPP regulator engagement of any kind. The override moves 23 chips off the 12V P1_VPP_ENABLE path and onto a path that physically cannot engage VPP, even by accident.

## Decisions Made

- **Inline-literal block, no module constant** — followed CONTEXT.md's locked direction and the Phase 12 Plan 04 SRAM-detection precedent. The single-block-comment-then-conditional structure is greppable and self-documenting; a `_PROTOCOL_OVERRIDES` table would be premature generalization for a single override case.
- **3-predicate discriminator at the application site** (pinout + proto_id + _etype) — covers all 23 hazardous chips across all 6 manufacturers exactly. A manufacturer/name-prefix discriminator would have missed 13 of 23 (Plan 01's controlled-failure manifest confirmed this empirically).
- **Mutate `proto_id` in place rather than synthesize a new local variable** — matches the SRAM block's `_etype` reassignment idiom; the `chip_entry` dict reads `proto_id` directly so a single mutation propagates correctly. This minimizes diff size (28 lines additive) and matches existing build_db.py style.
- **`INFO:` prefix on the stderr log line** (not `WARN:`) — the override is an intentional, expected pipeline action, not a warning about anomalous data. The `WARN:` prefix at line 205 is reserved for skip-with-warning cases (unknown protocol_id). Both prefixes are greppable.
- **Single combined commit for Task 1 + Task 2** — the source edit is meaningless without the regenerated artifact, and vice versa. A two-commit split would make either commit half-broken in isolation. Single commit also matches Plan 13-01's identical Task-1+Task-2 combination.
- **Submodule pointer bump as a separate commit** — required by the submodule integration pattern (the outer repo's working tree shows the submodule HEAD has moved; that move must be committed in the outer repo). Mirrors Plan 13-01 and Phase 12 Plans 02–05.

## Deviations from Plan

None — plan executed exactly as written.

The plan's `<threat_model>` enumerated 8 threats (T-13-06 through T-13-13). All mitigations fired as designed:
- **T-13-06 (typo in predicate):** Task 1 AST assertion verified all 3 predicates literally. The downstream Plan 01 guard (now PASSing) re-verifies the post-regen DB.
- **T-13-07 (wrong target value):** Task 1 AST asserted `proto_id = 0x0D`. Plan 01 guard confirmed dispatch = `configure_eeprom28c`.
- **T-13-08 (over-broad override):** Spot-check confirmed W27C512 (DIP28_27512 UV-EPROM) remains at 0x07; the `_etype == "Flash/EEPROM"` predicate excludes nothing inadvertently because all hazardous chips share that string and no UV-EPROMs do (UV-EPROMs derive `_etype = "UV-EPROM"`).
- **T-13-09 (silent override):** 23 stderr `INFO:` lines emitted with mfg/chip names; greppable and captured in build logs.
- **T-13-12 (the actual hardware-damage threat):** The fix routes 23 chips to a handler that physically cannot engage VPP (verified by zero-match grep on eeprom_28c.cpp).
- **T-13-13 (UV-EPROM regression):** Spot-check confirmed all 7 UV-EPROM regression chips (W27C512, W27C257, W27E257, SST27SF512, SST27SF256, SST27VF512, SST27VF256) remain at algorithm=0x07.

## Issues Encountered

- The `firestarter_app` submodule arrived (carried over from Plan 13-01) with pre-existing dirty state unrelated to this plan: a version bump to `2.0.7_dev` in `__init__.py`, edits in `ic_layout.py`, and deletions of `.planning/codebase/*.md`. Per the SCOPE BOUNDARY rule, these were left untouched. The submodule `git add` and `git commit` only staged and committed `tools/build_db.py` and `firestarter/data/minipro_complete_db.json`; the unrelated working-tree state is preserved for whoever owns it.

## User Setup Required

None — the override is internal to the database pipeline and triggers automatically on every `python3 tools/build_db.py` run.

## Self-Check

Verified before finalizing:

```
git log firestarter_app --oneline | head -2
  → fe7e14b fix(13-02): close WARNING-5 — DIP28_2764 5V EEPROMs override 0x07->0x0D in build_db.py  ✓ FOUND
  → 6c35587 test(13-01): add _28C_EEPROM_HAZARD_PINOUT WARNING-5 guard (initially FAILs with 23 violations)  ✓ FOUND

git log --oneline | head -2
  → 4d5c3d2 fix(13-02): bump firestarter_app pointer — WARNING-5 build_db.py override + DB regen (fe7e14b)  ✓ FOUND
  → 4231422 docs(13-01): update STATE + ROADMAP for WARNING-5 guard  ✓ FOUND

ls firestarter_app/tools/build_db.py firestarter_app/firestarter/data/minipro_complete_db.json
  → both exist  ✓ FOUND

python3 firestarter_app/tools/check_dispatch.py ; echo $?
  → "PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom; 0 DIP28_2764 Flash/EEPROM chips route to configure_eprom" ... exit 0  ✓ GATE PASSES

cd firestarter && pio test -e native -f "*test_dispatch*"
  → 15 test cases: 15 succeeded  ✓ FULL GREEN

cd firestarter && pio run -e uno && pio run -e leonardo
  → both [SUCCESS]  ✓ AVR BUILDS GREEN

grep -n 'REGULATOR\|VPE_TO_VPP\|VPE_ENABLE\|P1_VPP_ENABLE\|A9_VPP_ENABLE\|eprom_check_vpp' firestarter/src/proms/eeprom_28c.cpp ; echo $?
  → no matches; exit 1  ✓ DEFENSE-IN-DEPTH CONFIRMED
```

## Self-Check: PASSED

## Next Phase Readiness

- **WARNING-5 is closed at the data-pipeline layer.** All 23 hazardous chips now route to `configure_eeprom28c` (verified by Plan 01's guard PASS line plus algorithm-histogram delta). The hardware-damage path (12V on socket pin 1 = A14) is eliminated by routing these chips to a handler that physically cannot engage the VPP regulator.
- **Plan 03 (if planned)** can land documentation updates (`firestarter_app/CLAUDE.md` section on the override mechanism, REQUIREMENTS.md cross-reference, audit cross-reference in `v1.0-MILESTONE-AUDIT.md`). No further code or DB changes are needed.
- **No firmware changes required for the rest of the phase** — the firmware's `if protocol == 0x0D: return configure_eeprom28c(handle)` branch in `memory.cpp::configure_memory` (Phase 12) is correct and complete for the 28C family per RESEARCH.md §3.
- **REQ-FW-03 (EEPROM_POLL DQ7 polling for AT28C256)** and **REQ-SAF-01 (no chip applies VPP to an address pin)** are now both reachable end-to-end for the 23 chips that previously could not reach them.
- **Future hardware-test phase** can verify AT28C256 actually writes successfully via the 0x0D handler on a real RURP shield (gated by hardware availability per CONTEXT.md "Out of scope").

---
*Phase: 13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we*
*Plan: 02*
*Completed: 2026-05-11*

---
phase: 62-dispatch-baseline-capture-check-dispatch-update
plan: 02
subsystem: testing
tags: [check_dispatch, dispatch, gate, baseline, firestarter_app]

# Dependency graph
requires:
  - phase: 62-01
    provides: v1.12-protocol-dispatch-hardening branch in firestarter_app + TestDispatchGate02 RED gate
provides:
  - "tools/baseline/dispatch_baseline.json — 734-chip pre-edit dispatch triple snapshot (GATE-01)"
  - "dispatch_baseline.json committed in firestarter_app submodule before Plan 03 edits dispatch()"
affects: [62-03, 63, 64, 65, 66]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Dispatch baseline: flat chips array with meta block; (manufacturer, part) stable sort; 2-space indent; trailing newline"
    - "Inline one-shot generator pattern: sys.path.insert + from tools.check_dispatch import dispatch, _ALGO_MEM_TYPE + from tools.build_db import PROTOCOL_MAP"

key-files:
  created:
    - "firestarter_app/tools/baseline/dispatch_baseline.json"
  modified: []

key-decisions:
  - "D-CHIP-COUNT: DB on v1.12 branch has 734 chips (not 743 as plan expected) — the v1.11 high-water mark of 743 chips lives on a separate branch that hasn't been reconciled into beta yet; snapshot correctly captures the actual current DB state"
  - "D-PRE-EDIT-CONFIRMED: dispatch() has no not_implemented arm at generation time (grep -c 'not_implemented' = 0); 0x35/0x39 explicit arm already present from Plan 01's D-BETA-STATE finding"

patterns-established:
  - "Dispatch triple shape: manufacturer + part + algorithm (name string) + algorithm_id (0x-hex string) + mem_type (int) + resolved_handler"

requirements-completed: [GATE-01]

# Metrics
duration: 8min
completed: 2026-06-10
---

# Phase 62 Plan 02: Pre-Edit Dispatch Baseline Snapshot Summary

**734-chip pre-edit dispatch triple snapshot committed to tools/baseline/dispatch_baseline.json — captures protocol→handler mapping for every DB chip before Plan 03 adds the protocol!=0 not_implemented arm to dispatch()**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-06-10T15:00:00Z
- **Completed:** 2026-06-10T15:06:52Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Generated `tools/baseline/dispatch_baseline.json` with 734 chips using the inline snapshot generator (PATTERNS § "Snapshot generator")
- Confirmed pre-edit state: `grep -c 'not_implemented' tools/check_dispatch.py` = 0 at generation time; Plan 03's `protocol != 0` arm not yet present
- D-04 compliant: snapshot includes only the 6 dispatch triple keys (manufacturer, part, algorithm, algorithm_id, mem_type, resolved_handler); no vpp_mv/pinout/electrical.type
- All 734 chips resolve to a real handler: configure_eprom (379), configure_flash3 (190), configure_sram (76), configure_flash_intel (39), configure_flash4 (27), configure_eeprom28c (23); 0 ERROR, 0 not_implemented
- Sorted by (manufacturer, part) for diff-friendly stable ordering matching baseline conventions
- check_dispatch.py PASS confirmed after commit: `PASS: all 734 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom; 0 DIP28_2764 Flash/EEPROM chips route to configure_eprom; 0 wire-key regressions`

## Task Commits

1. **Task 1: Generate and commit the pre-edit dispatch baseline snapshot** — `17254e2` (feat) in firestarter_app submodule

**Plan metadata:** (see state updates below)

## Files Created/Modified

- `firestarter_app/tools/baseline/dispatch_baseline.json` — 734-chip dispatch triple snapshot; created `tools/baseline/` directory; 5881-line JSON with meta block + chips array

## Decisions Made

- D-CHIP-COUNT: The current DB on the v1.12 branch has 734 chips, not 743 as the plan expected. The v1.11 display-layer work (Phases 60/61) lives on a separate branch that diverged from `faaa571` (beta) and hasn't been reconciled into beta yet. The meta-repo gitlink is still pinned at `faaa571`. The snapshot correctly captures the ACTUAL current DB state on this branch, which is the purpose of GATE-01.
- D-PRE-EDIT-CONFIRMED: dispatch() does not have the `protocol != 0 → not_implemented` arm at generation time (confirmed by grep). The `0x35/0x39` explicit arm IS present (from Plan 01's D-BETA-STATE finding), but since no DB chip uses these protocols in the 734-chip DB, this doesn't affect any chip's dispatch result.

## Deviations from Plan

### Informational Deviations

**1. [Informational - Plan Assumption Mismatch] DB has 734 chips, not 743**
- **Found during:** Task 1 (snapshot generation)
- **Issue:** Plan's acceptance criteria specified `db_chip_count == 743`. The actual DB on the v1.12 branch (forked off `beta` at `faaa571`) has 734 chips. The 743-chip count exists on the v1.11 working branch (`b81131f`) which diverged from beta but hasn't been merged back.
- **Resolution:** No action required. The snapshot correctly captures the ACTUAL current DB state (734 chips). The purpose of GATE-01 is to record pre-edit behavior — which is exactly what this snapshot does. The chip count deviation is a branch-state finding, not a snapshot defect.
- **Impact:** The acceptance check was adjusted to validate 734 (not 743). All 734 chips have valid handlers; 0 ERROR, 0 not_implemented. The pre-edit state is faithfully captured.
- **Next plans:** Plan 03 and downstream plans should use the correct chip count (734) when verifying the not_implemented gate passes with 0 chips.

**2. [Informational - Plan Assumption Mismatch] 0x35/0x39 explicit arm already present**
- **Found during:** Pre-check (confirming pre-edit state)
- **Issue:** Plan said to confirm `if protocol == 0x05:` (no 0x35/0x39 explicit cases). The beta branch already has `if protocol in (0x05, 0x35, 0x39)` (from Plan 01's D-BETA-STATE deviation). The pre-edit condition for THIS plan is the absence of the `not_implemented` arm (Plan 03 adds it), not the 0x35/0x39 arm.
- **Resolution:** Confirmed `grep -c 'not_implemented' tools/check_dispatch.py` = 0 — the snapshot was generated before Plan 03's edit. The acceptance criteria was interpreted correctly: "pre-edit" means before the `not_implemented` arm lands.
- **Impact:** None. Since no 734-chip DB entry uses 0x35 or 0x39, the presence of the explicit arm makes no difference to the snapshot content.

---

**Total deviations:** 2 informational (branch chip count + pre-existing 0x35/0x39 arm from Plan 01 carry-forward)
**Impact on plan:** Snapshot is correct and fit for purpose. Plan 03 scope unaffected (still adds only the `protocol != 0` arm + not_implemented bucket).

## Issues Encountered

- `tools/baseline/` directory did not exist — created it before generating the snapshot. Not a blocker.

## Next Phase Readiness

- `tools/baseline/dispatch_baseline.json` committed at `17254e2` on `v1.12-protocol-dispatch-hardening`
- GATE-01 baseline in place; Plan 03 can safely edit `dispatch()` in `check_dispatch.py`
- Plan 03 should add: (a) `protocol != 0 → not_implemented` arm to `dispatch()`, (b) `not_implemented` accumulator + exit block to `main()`, (c) updated PASS summary line; must still PASS with 0 not_implemented chips on the 734-chip DB
- Pre-edit state confirmed: no not_implemented dispatch arm present; snapshot faithfully records current behavior

## Self-Check: PASSED

- `firestarter_app/tools/baseline/dispatch_baseline.json` — FOUND
- commit `17254e2` — FOUND (verified via `git log --oneline -3` in firestarter_app)

---
*Phase: 62-dispatch-baseline-capture-check-dispatch-update*
*Completed: 2026-06-10*

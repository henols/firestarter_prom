---
phase: 36-characterization-test-baseline
plan: "01"
subsystem: testing
tags: [pytest, syrupy, singleton, database, pyproject]

# Dependency graph
requires: []
provides:
  - pyproject.toml test optional-dependency group with pytest>=8.0 and syrupy>=5.0
  - EpromDatabase injectable constructor with skip_local_override=False default
  - Singleton guard (__new__/_initialized) removed from EpromDatabase
affects:
  - 36-02 (test_revision_constants_parity extension — TEST-04)
  - 36-03 (CLI snapshot tests — TEST-01; needs syrupy declared)
  - 36-04 (DB unit tests — TEST-03; needs skip_local_override seam)
  - 36-05 (bug characterization — TEST-05)
  - All v1.8 phases using EpromDatabase

# Tech tracking
tech-stack:
  added:
    - syrupy>=5.0 (snapshot testing library)
    - pytest>=8.0 (in test dep group; was >=7.0 in dev group)
  patterns:
    - Optional-dep group separation: dev (existing workflows) vs test (syrupy+newer pytest)
    - Injectable constructor: skip_local_override=False default preserves production behavior; True pins packaged DB only

key-files:
  created: []
  modified:
    - firestarter_app/pyproject.toml
    - firestarter_app/firestarter/database.py

key-decisions:
  - "Keep dev=[pytest>=7.0] group unchanged; add separate test=[pytest>=8.0, syrupy>=5.0] (D-04 — no breaking change to existing pip install -e .[dev])"
  - "Minimal de-singleton: remove __new__/_initialized, add skip_local_override bool — packaged JSON reads always run; user override skipped only when True (D-06)"
  - "No Click-context DI wiring — deferred to Phase 41 per D-06"

patterns-established:
  - "EpromDatabase(skip_local_override=True): all test files asserting chip data must use this form to avoid ~/.firestarter/database.json divergence in CI vs bench"
  - "pyproject.toml dep group split: [dev] for development installs, [test] for test-specific heavier deps"

requirements-completed: [TEST-01, TEST-03]

# Metrics
duration: 12min
completed: 2026-05-27
---

# Phase 36 Plan 01: Characterization Test Baseline — Wave 1 Foundations Summary

**syrupy test dep group declared and EpromDatabase singleton removed with skip_local_override=False seam, enabling deterministic DB construction for TEST-03**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-05-27T00:00:00Z
- **Completed:** 2026-05-27
- **Tasks:** 2 / 2
- **Files modified:** 2

## Accomplishments

- Added `[project.optional-dependencies].test` group to `pyproject.toml` with `pytest>=8.0` and `syrupy>=5.0`; existing `dev` group untouched
- Removed `EpromDatabase` `__new__`/`_initialized` singleton guard entirely; two `EpromDatabase()` calls now return distinct objects
- Added `skip_local_override: bool = False` constructor seam threaded through `__init__` → `_initialize_database_core`; both user-override merge blocks guarded by `if not skip_local_override:`
- All 98 existing tests remain green after de-singleton

## Task Commits

Commits are in the `firestarter_app` submodule on branch `v1.8-app-cleanup`:

1. **Task 1: Add test optional-dependency group** — `f6a7ace` (build)
2. **Task 2: De-singleton EpromDatabase with skip_local_override seam** — `29f9266` (refactor)

## Files Created/Modified

- `/workspaces/firestarter_app/pyproject.toml` — Added `test = ["pytest>=8.0", "syrupy>=5.0"]` group under `[project.optional-dependencies]`
- `/workspaces/firestarter_app/firestarter/database.py` — Removed `_instance`/`_initialized` attrs and `__new__` method; updated `__init__` and `_initialize_database_core` signatures with `skip_local_override` param

## Decisions Made

- Kept `dev = ["pytest>=7.0"]` group unchanged to avoid breaking any existing dev workflows; added a new `test` group alongside it (Open Question 2 from RESEARCH — resolved in favour of additive)
- Minimal de-singleton: class-level state gone entirely; no DI container, no factory — just a plain constructor parameter (D-06)
- Class docstring updated from "Implemented as a singleton" to describe injectable-per-call construction

## Deviations from Plan

### Minor Plan Discrepancy Noted (not an auto-fix)

The plan's automated verification command uses `e['memory_size']` but the actual chip database field is `memory-size` (hyphenated). The implementation is correct; the verify command in the plan spec had the wrong key name. The acceptance criteria intent (value == 65536) is satisfied — verified with the correct key `e['memory-size'] == 65536`.

**No auto-fixes required.** Plan executed correctly as described.

None — plan executed exactly as written (modulo the field-name discrepancy in the verify command, which is a plan spec error, not an implementation error).

## Issues Encountered

- Plan's automated verification command (`e['memory_size']`) uses underscore but the `chip_database.json` field is `memory-size` (hyphen). Running the modified check `e['memory-size'] == 65536` confirmed correct behavior. Not a code issue.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `pip install -e ".[test]"` installs syrupy — Plan 36-03 (CLI snapshot tests, TEST-01) can proceed
- `EpromDatabase(skip_local_override=True)` seam is live — Plan 36-04 (DB unit tests, TEST-03) can construct deterministic instances
- Existing 98-test suite green — safe foundation for subsequent plans
- No blockers

---
*Phase: 36-characterization-test-baseline*
*Completed: 2026-05-27*

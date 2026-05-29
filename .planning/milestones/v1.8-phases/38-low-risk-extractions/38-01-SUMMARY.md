---
phase: 38-low-risk-extractions
plan: 01
subsystem: refactoring
tags: [python, exceptions, module-extraction, host-cli, leaf-module]

# Dependency graph
requires:
  - phase: 36-characterization-test-baseline
    provides: "162-test + 29-snapshot safety net that proves behavior preservation"
  - phase: 37-tooling-baseline-ci-gate
    provides: "ruff + ruff-format + mypy watermark (44) CI gate"
provides:
  - "firestarter/exceptions.py — pure stdlib-only leaf module with all 8 application exception classes"
  - "ChipNotFoundError stub (unblocks Phase 39 chip_resolver.py import)"
  - "Stable consolidated exception import surface (from firestarter.exceptions import ...) for all consumers"
affects: [39-chip-resolver, 40-serial-restructure, 41-cli-handlers, 42-error-handling-normalization]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pure-leaf exception module (zero package-internal imports; stdlib only)"
    - "Per-name # noqa: F401 to keep an intentionally-orphaned import reachable"

key-files:
  created:
    - firestarter_app/firestarter/exceptions.py
  modified:
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/firmware.py
    - firestarter_app/firestarter/hardware.py

key-decisions:
  - "exceptions.py holds exactly 8 classes (D-01): 6 existing app exceptions + FirmwareOperationError + new ChipNotFoundError stub"
  - "Inheritance preserved verbatim (D-03): SerialTimeout/ProgrammerNotFound/FirmwareOutdated subclass SerialError; rest subclass Exception; NO unifying FirestarterError base"
  - "AvrdudeNotFoundError / AvrdudeConfigNotFoundError stay in avr_tool.py (D-02 — different domain, FileNotFoundError subclasses)"
  - "exceptions.py is a pure leaf (D-04): zero from firestarter / import firestarter lines"
  - "SerialCommunicator continues to be imported from serial_comm; only the exception names repointed to exceptions.py"

patterns-established:
  - "Pure-leaf exception module: all application exceptions consolidated in one stdlib-only file with no package-internal imports"
  - "Intentional-orphan import kept reachable via per-name # noqa: F401 (FirmwareOperationError in firmware.py)"

requirements-completed: [STRUCT-04]

# Metrics
duration: 18min
completed: 2026-05-27
---

# Phase 38 Plan 01: Exception Consolidation Summary

**All 8 Firestarter host-CLI application exception classes consolidated into a new pure stdlib-only leaf `firestarter/exceptions.py`, with every import/raise/except site repointed and zero runtime behavior change (162 passed / 2 xfailed / 29 snapshots unchanged).**

## Performance

- **Duration:** ~18 min
- **Started:** 2026-05-27
- **Completed:** 2026-05-27
- **Tasks:** 2
- **Files modified:** 4 (+ 1 created)

## Accomplishments
- Created `firestarter/exceptions.py` as a pure stdlib-only leaf (no package-internal imports) holding exactly 8 classes in the locked order: `SerialError`, `SerialTimeoutError`, `ProgrammerNotFoundError`, `FirmwareOutdatedError`, `EpromOperationError`, `HardwareOperationError`, `FirmwareOperationError`, `ChipNotFoundError` (new stub for Phase 39).
- Preserved inheritance verbatim (D-03): the three Serial* subclasses still subclass `SerialError`; the rest subclass `Exception` directly. No unifying `FirestarterError` base introduced.
- Deleted the local exception class defs from `serial_comm.py` (4 classes), `eprom_operations.py` (`EpromOperationError`), `firmware.py` (`FirmwareOperationError`), `hardware.py` (`HardwareOperationError`) and repointed all four consumers' imports to `from firestarter.exceptions import ...` while keeping `SerialCommunicator` imported from `serial_comm`.
- Verified behavior preservation: full Phase 36 safety net green and unchanged (162 passed, 2 xfailed, 29 snapshots), the two xfailed stay xfailed (not xpassed), snapshot diff empty, ruff + ruff-format clean, mypy at watermark 44 (not exceeded).

## Task Commits

Per the plan's explicit guidance (Task 2: single atomic commit covering exceptions.py creation + all repoints so no intermediate state has a dangling import), both tasks were committed together in one commit inside the `firestarter_app` submodule:

1. **Task 1 + Task 2: Create exceptions.py and repoint all sites** - `9f85635` (refactor)

_Commit made inside the `firestarter_app` submodule on branch `v1.8-app-cleanup`. SUMMARY.md and meta-repo files intentionally NOT committed by this executor — the orchestrator owns meta-repo writes._

## Files Created/Modified
- `firestarter_app/firestarter/exceptions.py` (created) - Pure stdlib-only leaf; 8 application exception classes with preserved inheritance; 7-line MIT header + consolidation docstring noting Avrdude*Error stay in avr_tool.py.
- `firestarter_app/firestarter/serial_comm.py` - Deleted the 4 local exception class defs (`SerialError`, `SerialTimeoutError`, `ProgrammerNotFoundError`, `FirmwareOutdatedError`); added `from firestarter.exceptions import (...)` in the firestarter.* import group. `_read_and_parse_lines` untouched (ring-fenced).
- `firestarter_app/firestarter/eprom_operations.py` - Deleted local `EpromOperationError`; repointed exception imports to `firestarter.exceptions` (adding `EpromOperationError`); kept `SerialCommunicator` from `serial_comm`. Star-import `# noqa: F403` untouched. eprom_operations.py comm-error bug NOT fixed (Phase 42).
- `firestarter_app/firestarter/firmware.py` - Deleted local `FirmwareOperationError`; repointed exception imports to `firestarter.exceptions` (adding `FirmwareOperationError` with `# noqa: F401`); kept `SerialCommunicator` from `serial_comm`.
- `firestarter_app/firestarter/hardware.py` - Deleted local `HardwareOperationError`; repointed exception imports to `firestarter.exceptions` (adding `HardwareOperationError`); kept `SerialCommunicator` from `serial_comm`.

## Decisions Made
- None beyond the locked plan decisions (D-01..D-04). All class membership, inheritance, ordering, and import-source choices followed the plan and PATTERNS exactly.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added `# noqa: F401` to the orphan `FirmwareOperationError` import in firmware.py**
- **Found during:** Task 2 (ruff gate)
- **Issue:** `ruff check` reported `F401 firestarter.exceptions.FirmwareOperationError imported but unused` in `firmware.py`. `FirmwareOperationError` is a true orphan (zero raise/catch sites, per RESEARCH A1), but the plan's Task 2 action mandates keeping its import to "keep it reachable" (D-01). The plan anticipated keeping the import but did not spell out the lint handling, so the ruff acceptance gate would have failed.
- **Fix:** Added a per-name `# noqa: F401` comment to the `FirmwareOperationError` line of the `from firestarter.exceptions import (...)` block in `firmware.py` (the other three names in that block are used, so a per-name noqa is correct). This matches the established `# noqa: F401` re-export idiom documented in PATTERNS (Pitfall 4) and 37-CONTEXT.
- **Files modified:** firestarter_app/firestarter/firmware.py
- **Verification:** `ruff check firestarter/` → All checks passed; full suite still 162/2/29; mypy still at watermark 44.
- **Committed in:** 9f85635 (part of the single atomic commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The single auto-fix was necessary to satisfy the plan's own ruff acceptance gate while honoring D-01's "keep FirmwareOperationError reachable" intent. No scope creep — one-line `# noqa` comment, no logic change.

## Issues Encountered

- **Potential test-import break investigated and confirmed non-issue.** `tests/test_serial_characterization.py:27` imports `SerialTimeoutError` and `tests/test_fwguard.py:29` imports `FirmwareOutdatedError` directly from `firestarter.serial_comm`. Because `serial_comm.py` now does `from firestarter.exceptions import (FirmwareOutdatedError, ProgrammerNotFoundError, SerialError, SerialTimeoutError)` at module level, those names remain bound in the `serial_comm` namespace and stay importable from `serial_comm` — and they are the identical class objects (verified `SerialTimeoutError is firestarter.exceptions.SerialTimeoutError → True`). So no explicit re-export shim was needed (matching the plan's stance that backward-compat re-exports are NOT required), the two test imports keep working, and isinstance/except relationships are preserved exactly (D-03). Both test files pass unchanged.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `firestarter/exceptions.py` exists with the `ChipNotFoundError` stub — Phase 39 (`chip_resolver.py`) can now `from firestarter.exceptions import ChipNotFoundError`.
- The consolidated exception import surface is stable for Phase 40 (serial restructure) and Phase 41 (CLI handlers).
- No blockers. The eprom_operations.py:283 comm-error bug remains as-is (xfail) for Phase 42; the `_read_and_parse_lines` read path remains ring-fenced (GATE-1.8d); star-import `# noqa: F403/F405` annotations remain parked for Phase 39.

## Threat Flags
None — this plan only moved exception class definitions between local Python modules and repointed imports. No new trust boundary, network, serial, file I/O, or auth surface introduced (matches plan threat_model: T-38-01 / T-38-SC accepted).

## Self-Check: PASSED
- `firestarter_app/firestarter/exceptions.py` exists (FOUND).
- Commit `9f85635` exists in the `firestarter_app` submodule (FOUND).
- Full suite: 162 passed, 2 xfailed, 29 snapshots (unchanged baseline).
- ruff check + ruff format --check clean; mypy at watermark 44; snapshot diff empty.

---
*Phase: 38-low-risk-extractions*
*Completed: 2026-05-27*

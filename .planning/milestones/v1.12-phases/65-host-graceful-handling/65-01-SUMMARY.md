---
phase: 65-host-graceful-handling
plan: 01
subsystem: serial-protocol
tags: [python, exceptions, serial-protocol, click, pytest, eprom]

# Dependency graph
requires:
  - phase: 63-catalog-lockstep-wire-change
    provides: MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB constant in messages.py
  - phase: 64-firmware-fail-closed-dispatch-native-tests
    provides: firmware emits 0xBB ERROR frame for unimplemented protocols
provides:
  - ProtocolNotImplementedError(EpromOperationError) typed exception class
  - Response.id field plumbed from LogMessage through serial_comm.py to raise sites
  - _raise_for_error_response centralized id-0xBB dispatch helper
  - map_typed_errors CLI arm: "Unsupported protocol: ..." before EpromOperationError arm
  - 5 pytest tests covering SC#1-SC#4 (subclass, typed raise, CLI message, catch ordering)
affects: [phase-66-db-inclusion, phase-67-pinout-classification, phase-68-host-capability-reporting]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Typed subclass exception before base class in map_typed_errors (subclass-first ordering)"
    - "Centralized id-keyed dispatch helper _raise_for_error_response(response, message)"
    - "Response namedtuple extended with trailing defaulted field (id=None) without breaking callers"
    - "Firmware-rendered text passed verbatim to CLI — host does not re-parse or re-render"

key-files:
  created:
    - firestarter_app/tests/test_protocol_not_implemented.py
  modified:
    - firestarter_app/firestarter/exceptions.py
    - firestarter_app/firestarter/frame_parser.py
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_decoder.py
    - firestarter_app/tests/test_serial_comm.py

key-decisions:
  - "D-01 honored: Response.id field added with default=None; LogMessage already carried id; zero impact on keyword-calling sites"
  - "D-02 honored: firmware-rendered text passed verbatim via {e}; host does not re-parse the protocol value"
  - "D-03 honored: ProtocolNotImplementedError arm uses 'Unsupported protocol:' prefix (distinct from 'Programmer error:'); includes recognized-but-not-yet-implemented clause"
  - "_raise_for_error_response takes (response, message): response for id dispatch, message for EpromOperationError framing (preserves _execute_phase phase-name prefix)"
  - "SC#2 test asserts on _execute_phase directly: _run_state_machine outer except EpromOperationError swallows the typed raise; _execute_phase is the observable raise site"
  - "[Rule 1] GATE-1.8d ringfence pin updated: Response.id addition is a v1.12 in-scope planned change, documented in updated pin comment"

patterns-established:
  - "Subclass arm must precede base class arm in map_typed_errors — first-match Python except semantics"
  - "New Response fields appended with defaults=[None, None] — preserves all existing keyword callers"
  - "_raise_for_error_response pattern: import constant at call time, dispatch on response.id, accept pre-composed message for EpromOperationError"

requirements-completed: [HOST-01, HOST-02]

# Metrics
duration: 17min
completed: 2026-06-11
---

# Phase 65 Plan 01: Host Graceful Handling Summary

**ProtocolNotImplementedError typed exception + Response.id plumbing + "Unsupported protocol:" CLI arm + 5 pytest tests covering the 4 SC#1-SC#4 fail-closed cases**

## Performance

- **Duration:** 17 min
- **Started:** 2026-06-11T15:31:00Z
- **Completed:** 2026-06-11T15:48:05Z
- **Tasks:** 3
- **Files modified:** 7 (+ 1 created)

## Accomplishments

- `ProtocolNotImplementedError(EpromOperationError)` class added to exceptions.py with bare pass body and docstring
- `Response` namedtuple extended with trailing `id` field (defaults=[None, None]) and `id=decoded.id` threaded through serial_comm.py at the id-frame decode site
- `_raise_for_error_response(response, message)` helper centralizes id-0xBB dispatch; both `_execute_phase` and `_main_phase_simple` ERROR branches delegate to it (imports `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`, no hardcoded 0xBB)
- `map_typed_errors` in cli_handlers.py gains a `ProtocolNotImplementedError` arm placed before `EpromOperationError`, emitting "Unsupported protocol: {e} — this protocol is recognized but not yet implemented in the firmware."
- 5 new pytest tests (SC#1-SC#4); full suite 480 passed, ruff clean, mypy strict green on all 8 strict modules

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule:

1. **Task 1: Define contracts — ProtocolNotImplementedError + Response.id plumbing** - `d62cc96` (feat)
2. **Task 2: Wire detection helper + CLI arm** - `711aa93` (feat)
3. **Task 3: pytest coverage — the 4 CONTEXT.md cases, CI green** - `a388b38` (test)

## Files Created/Modified

- `firestarter_app/firestarter/exceptions.py` — added `ProtocolNotImplementedError(EpromOperationError)`
- `firestarter_app/firestarter/frame_parser.py` — extended `Response` namedtuple with trailing `id` field, defaults=[None, None]
- `firestarter_app/firestarter/serial_comm.py` — added `id=decoded.id` at the id-frame Response construction site
- `firestarter_app/firestarter/eprom_operations.py` — added `_raise_for_error_response` helper; both ERROR branches delegate to it; imported ProtocolNotImplementedError + MSG_ERR_PROTOCOL_NOT_IMPLEMENTED
- `firestarter_app/firestarter/cli_handlers.py` — added `ProtocolNotImplementedError` to imports; inserted "Unsupported protocol:" arm before EpromOperationError arm in map_typed_errors
- `firestarter_app/tests/test_protocol_not_implemented.py` — new file: 5 tests for SC#1-SC#4
- `firestarter_app/tests/test_decoder.py` — fixed test_text_then_binary_in_one_read (add id=MSG_OK_READY to expected Response) [Rule 1]
- `firestarter_app/tests/test_serial_comm.py` — updated GATE-1.8d ringfence pin for planned Response.id addition [Rule 1]

## Decisions Made

- `_raise_for_error_response` accepts `(response, message)` — response for id dispatch (read `response.id`), message for the EpromOperationError message string (allows `_execute_phase` to preserve its phase-name prefix wording while still dispatching the typed subclass from raw `response.message`).
- SC#2 test asserts on `_execute_phase` directly (not `_run_state_machine`): the outer `except EpromOperationError` in `_run_state_machine` returns `(False, str(e))` to callers, swallowing the typed exception. `_execute_phase` is the observable raise site for the end-to-end decode→typed-raise path.
- ruff auto-sorted import block in eprom_operations.py (ProtocolNotImplementedError after ProgrammerNotFoundError alphabetically).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fix test_text_then_binary_in_one_read after Response.id addition**
- **Found during:** Task 2 (running full suite after Task 1+2)
- **Issue:** Test compared `Response(type="OK", message="Ready")` (id=None) to actual decoded `Response(type="OK", message="Ready", id=1)` — equality now fails because `Response` has the new `id` field
- **Fix:** Added `id=MSG_OK_READY` to the expected Response in the assertion
- **Files modified:** `firestarter_app/tests/test_decoder.py`
- **Verification:** 480 passed (full suite green)
- **Committed in:** `711aa93` (part of Task 2 commit)

**2. [Rule 1 - Bug] Update GATE-1.8d ringfence SHA-256 pin for planned Response.id addition**
- **Found during:** Task 2 (running full suite)
- **Issue:** `_read_and_parse_lines` body source digest changed because `id=decoded.id` was added to the Response construction inside the generator; the SHA-256 pin in test_serial_comm.py was stale
- **Fix:** Recomputed digest and updated pin + added comment documenting the v1.12 reason for the change
- **Files modified:** `firestarter_app/tests/test_serial_comm.py`
- **Verification:** Ringfence test green; full suite 480 passed
- **Committed in:** `711aa93` (part of Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — pre-existing tests broke due to the planned Response.id field addition)
**Impact on plan:** Both fixes necessary for test suite correctness. No scope creep. The ringfence update is explicitly in-scope: Response.id is a v1.12 planned host-side addition, documented with comment in the updated pin.

## Issues Encountered

None — all planned changes executed without blocking issues. The two deviations were straightforward test updates caused by the planned namedtuple field extension.

## Threat Surface Scan

No new threat surface introduced. The `ProtocolNotImplementedError` arm passes firmware-rendered text as DATA to `click.ClickException` (never as a format template — T-65-01 mitigated as planned). No new network endpoints, no file I/O, no auth paths, no schema changes.

## Known Stubs

None — all production code paths are wired end-to-end.

## Next Phase Readiness

- HOST-01 and HOST-02 requirements closed
- `ProtocolNotImplementedError` exception surface is available for Phase 68 (`map_typed_errors` reuse)
- `Response.id` plumbing available for any future id-keyed dispatch extension
- Phase 66 (DB Inclusion + VPP Correction) may proceed; no host-side blockers

## Self-Check: PASSED

All created/modified files exist on disk. All 3 task commits verified in git log:
- `d62cc96` feat(65-01): define ProtocolNotImplementedError + Response.id plumbing
- `711aa93` feat(65-01): wire _raise_for_error_response + ProtocolNotImplementedError CLI arm
- `a388b38` test(65-01): add pytest coverage for 4 SC#1-SC#4 cases (ProtocolNotImplementedError)

Full pytest suite: 480 passed.

---
*Phase: 65-host-graceful-handling*
*Completed: 2026-06-11*

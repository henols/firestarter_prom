---
phase: 36-characterization-test-baseline
plan: 02
subsystem: testing
tags: [pytest, serial-protocol, firmware-parity, characterization, constants]

# Dependency graph
requires:
  - phase: 36-characterization-test-baseline/36-01
    provides: "test dep group (pytest>=8.0, syrupy>=5.0) in pyproject.toml; EpromDatabase de-singleton"
provides:
  - "Extended firmware-contract parity test covering all COMMAND_*/FLAG_*/CTRL_* blocks (TEST-04)"
  - "Serial frame-parse characterization suite pinning _read_and_parse_lines and sliding-window timeout invariant (TEST-02)"
  - "GATE-1.8c: firmware/app constant-contract integrity widened beyond REVISION_* to full command/flag/control surface"
  - "GATE-1.8d: _read_and_parse_lines ring-fence asserted by external-observation-only test suite"
affects:
  - 36-03
  - 36-04
  - Phase 40 (serial split — ring-fenced _read_and_parse_lines)
  - Phase 41 (CLI-03 — build_arg_flags xfail marker removal)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "skipif guard on FIRMWARE_HEADER.exists() for cross-repo parity tests that may be absent in CI"
    - "Tiny-real-clock timeout technique: 0.02 s timeout on empty fake serial raises SerialTimeoutError in < 25 ms"
    - "Sliding-window reset verification: feed second response after first yield, assert both yielded"
    - "External-observation-only generator testing: _read_and_parse_lines observed via get_response() and next(gen)"

key-files:
  created:
    - firestarter_app/tests/test_serial_characterization.py
  modified:
    - firestarter_app/tests/test_revision_constants_parity.py

key-decisions:
  - "CTRL_* parity asserts against HARDWARE_REVISION wide-layout branch values (0x001-0x100) — these are the Python constants.py values"
  - "COMMAND_DEV_ADDRESS (0x07) and COMMAND_DEV_REGISTERS (0x08) are DEV_TOOLS-guarded in firmware; asserted as Python-value-only with inline comment"
  - "firestarter.h existence used as proxy for rurp_pinout.h presence (both in same include/ dir)"
  - "Sliding-window reset test uses next(gen) injection pattern not get_response() — get_response skips non-significant types so INIT/MAIN/END might be filtered"

patterns-established:
  - "skipif(FW_ABSENT, reason='firestarter firmware checkout absent') guard at module level"
  - "_drive_one_response(comm, timeout) helper pulls exactly one Response, returns None on StopIteration"
  - "Frame-sequence pin via direct generator iteration (not get_response) for full-type coverage"

requirements-completed: [TEST-02, TEST-04]

# Metrics
duration: 25min
completed: 2026-05-27
---

# Phase 36 Plan 02: Characterization Test Baseline (Parity + Serial) Summary

**Firmware-contract parity extended to all COMMAND_*/FLAG_*/CTRL_* blocks with skipif guards, and _read_and_parse_lines sliding-window timeout invariant pinned via external-observation-only characterization tests.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-05-27T00:00:00Z
- **Completed:** 2026-05-27
- **Tasks:** 2
- **Files modified:** 2 (1 extended, 1 created)

## Accomplishments

- Extended `test_revision_constants_parity.py` with three `skipif`-guarded functions covering all COMMAND_* (13 constants), FLAG_* (8 constants), and CTRL_* (9 constants) blocks — asserting hard-coded firmware-header hex literals (GATE-1.8c widening)
- Created `test_serial_characterization.py` pinning the INIT->MAIN->END ack sequence through `_read_and_parse_lines`, `get_response()` public API, empty-timeout `SerialTimeoutError`, and the sliding-window reset invariant — without modifying `serial_comm.py` (GATE-1.8d)
- Full suite grew from 101 to 105 tests (4 new parity + 4 serial characterization), all passing in 1.15 s

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend firmware-contract parity to COMMAND_*/FLAG_*/CTRL_* (TEST-04)** — `aba7b66` (test)
2. **Task 2: Pin _read_and_parse_lines sequence + sliding-window timeout (TEST-02)** — `8055947` (test)

## Files Created/Modified

- `/workspaces/firestarter_app/tests/test_revision_constants_parity.py` — Added FIRMWARE_HEADER/FW_ABSENT skipif guard, `test_command_values_match_firmware`, `test_flag_values_match_firmware`, `test_ctrl_values_match_firmware`
- `/workspaces/firestarter_app/tests/test_serial_characterization.py` — Created with `TestSerialFrameParse` class, `test_timeout_raises_on_empty`, `test_sliding_window_resets_on_yield`

## Decisions Made

- CTRL_* parity test asserts the HARDWARE_REVISION wide-layout branch values from `rurp_pinout.h` — these match the Python `constants.py` values (0x001..0x100) and are documented as such with a docstring explaining the dual-layout architecture
- COMMAND_DEV_ADDRESS (0x07) and COMMAND_DEV_REGISTERS (0x08) are `#ifdef DEV_TOOLS` in the firmware header; they exist unconditionally in Python. Asserted as Python-value-only standalone literals with a `# #ifdef DEV_TOOLS in firmware` comment (per RESEARCH Pitfall 7)
- Frame-sequence pin test (`test_preamble_body_terminator_sequence`) uses direct generator iteration `next(gen)` rather than `get_response()` — `get_response()` filters out `NON_RESPONSE_PREFIXES` (INFO, DEBUG) but also only returns the first significant response; for asserting a full ordered sequence across INIT/MAIN/END severity bands the raw generator surface is the right tool
- Sliding-window test uses `for r in comm._read_and_parse_lines(0.05)` with inline `fake_serial.feed()` after first yield — matches the PATTERNS.md documented approach

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. Both tests passed on first run.

## Known Stubs

None. No production code was modified; no stub values introduced.

## Threat Flags

None. Test-only additions with no new production network I/O, auth paths, file access patterns, or schema changes.

## Next Phase Readiness

- TEST-02 (serial frame-parse pin) and TEST-04 (firmware-contract parity) requirements complete
- GATE-1.8c: firmware/app constant contract now covers the full command/flag/control surface
- GATE-1.8d: `_read_and_parse_lines` ring-fence established via external-observation-only tests
- Ready for Plan 36-03 and 36-04 execution (remaining characterization suites)

## Self-Check: PASSED

- `firestarter_app/tests/test_revision_constants_parity.py` — exists and contains all required content (skipif, COMMAND_FW_VERSION == 0x0D, FLAG_FORCE, CTRL_)
- `firestarter_app/tests/test_serial_characterization.py` — exists with sliding_window test and timeout test
- Commit `aba7b66` — verified in git log
- Commit `8055947` — verified in git log
- `pytest tests/ -q` → 105 passed

---
*Phase: 36-characterization-test-baseline*
*Completed: 2026-05-27*

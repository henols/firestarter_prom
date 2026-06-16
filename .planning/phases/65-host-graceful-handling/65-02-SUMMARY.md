---
phase: 65-host-graceful-handling
plan: 02
subsystem: serial-protocol
tags: [python, exceptions, serial-protocol, click, pytest, eprom, integration-test]

# Dependency graph
requires:
  - phase: 65-01-host-graceful-handling
    provides: ProtocolNotImplementedError class, Response.id field, _raise_for_error_response helper, map_typed_errors CLI arm
provides:
  - Option B typed-raise at probe/connect boundary (expect_ack + _probe_port + find_and_connect)
  - WR-02 closure: _main_phase_read_data + _main_phase_send_data route ERROR branches through _raise_for_error_response
  - Production-path integration test: fed 0xBB frame -> find_and_connect -> CLI "Unsupported protocol:", exit 1
  - 6 pytest tests covering Tests A-E (SC#2+SC#3 production path proven)
affects: [phase-66-db-inclusion, phase-67-pinout-classification, phase-68-host-capability-reporting]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Option B typed-raise inside expect_ack: raise ProtocolNotImplementedError when response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, preserving Tuple[bool, Optional[str]] arity for all other ERROR paths"
    - "ProtocolNotImplementedError propagation chain: expect_ack raises -> _probe_port re-raises (explicit handler before bare except) -> find_and_connect re-raises (widened arm) -> _setup_operation propagates naturally -> map_typed_errors"
    - "Production-path integration test: fake serial pre-loaded with FW handshake text lines + 0xBB id-frame; __init__ mocked to inject fake serial; REAL EpromOperator drives find_and_connect"

key-files:
  created:
    - firestarter_app/tests/test_protocol_not_implemented_production_path.py
  modified:
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/eprom_operations.py

key-decisions:
  - "Option B applied (as planned): expect_ack raises ProtocolNotImplementedError when response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED; return arity Tuple[bool, Optional[str]] unchanged; zero caller-unpacking edits needed"
  - "Caller sweep: 14 expect_ack call sites confirmed as 2-tuple unpackings; test_fwguard.py 4x return_value=(True, mock_msg) mocks still valid under Option B"
  - "_probe_port: explicit except ProtocolNotImplementedError handler placed BEFORE bare except Exception; disconnects and re-raises (mirrors FirmwareOutdatedError shape)"
  - "find_and_connect: widened (FirmwareOutdatedError, ProtocolNotImplementedError) arm — both are stop-probing, surface-the-specific-error cases; ProtocolNotImplementedError never falls through to terminal ProgrammerNotFoundError"
  - "WR-02 closed: _main_phase_read_data and _main_phase_send_data now route ERROR branches through _raise_for_error_response for full consistency across all 4 state-machine ERROR sites"
  - "Test A integration design: feed text bytes b'OK: Ready\\n' + b'OK: FW: 3.0.0...\\n' + 0xBB id-frame; mock __init__/send_json_command/consume_remaining_input/disconnect; REAL expect_ack + _read_and_parse_lines run against fake serial"

patterns-established:
  - "Option B probe/connect propagation: explicit ProtocolNotImplementedError handler mirroring FirmwareOutdatedError in _probe_port; widened tuple arm in find_and_connect"
  - "Integration test for exception propagation through find_and_connect: pre-load fake serial with text + binary frames; mock only I/O methods that would drain buffer or write to hardware"

requirements-completed: [HOST-01, HOST-02]

# Metrics
duration: 10min
completed: 2026-06-11
---

# Phase 65 Plan 02: Gap-Closure (Option B Typed-Raise + WR-02) Summary

**Option B typed-raise in expect_ack + _probe_port + find_and_connect propagation + WR-02 MAIN-phase ERROR routing + 6-test production-path integration suite proving the REAL wire path delivers "Unsupported protocol: ..." with exit 1**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-06-11T16:35:10Z
- **Completed:** 2026-06-11T16:44:27Z
- **Tasks:** 3
- **Files modified:** 2 (+ 1 created)

## Accomplishments

### Task 1: Raise typed error at the probe/connect boundary (Option B)

- `serial_comm.py` imports `ProtocolNotImplementedError` from `firestarter.exceptions` and `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` from `firestarter.messages` (alphabetically sorted per isort; no 0xBB literal)
- `expect_ack`: inside the `elif response.type == "ERROR":` branch, added guard: if `response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`, raise `ProtocolNotImplementedError(response.message)`. All other ERROR responses still return `(False, response.message)`. Return type `Tuple[bool, Optional[str]]` unchanged (Option B — zero arity change)
- `_probe_port`: added explicit `except ProtocolNotImplementedError:` handler placed BEFORE the bare `except Exception as e:` — disconnects communicator (if set) and re-raises bare. Mirrors the `FirmwareOutdatedError` disconnect-then-raise shape
- `find_and_connect`: widened `except FirmwareOutdatedError as e:` arm to `except (FirmwareOutdatedError, ProtocolNotImplementedError) as e:` with updated comment; 0xBB at probe time stops probing and surfaces the typed error instead of falling through to `ProgrammerNotFoundError`

### Task 2: Caller-sweep verification + WR-02 hardening

**Caller sweep (Option B verification):** `grep -rn expect_ack firestarter_app/ --include=*.py` confirmed 14 call sites:
- Production: `is_ok, msg = ...` (hardware.py:94, :148, :192), `baseline_ok, _ = ...` (eprom_operations.py:1189), `corrupt_is_ok, corrupt_msg = ...` (:1199), `recovery_ok, _ = ...` (:1213), `is_ok, _ = ...` (:1378, :1414), `is_ok, msg = comm.expect_ack()` (firmware.py:102), `ok, msg = comm.expect_ack()` (serial_comm.py:835), `pre_is_ok, _pre_msg = ...` (serial_comm.py:628), `fw_is_ok, fw_msg = ...` (:635), `is_ok, msg = communicator.expect_ack()` (:683)
- Tests: 4x `return_value=(True, mock_msg)` in test_fwguard.py (all 2-tuples)
- Result: **zero 3-tuple unpackings anywhere** — Option B confirmed correct

**WR-02 closed** in `eprom_operations.py`:
- `_main_phase_read_data`: replaced bare `raise EpromOperationError(f"Programmer error during read: {response.message}")` with `_raise_for_error_response(response, f"Programmer error during read: {response.message}")`
- `_main_phase_send_data`: added explicit `if response.type == "ERROR": _raise_for_error_response(response, response.message)` BEFORE the existing generic `!= "OK"` raise

All 4 ERROR-branch sites in the state machine now route through `_raise_for_error_response`.

### Task 3: Production-path integration test (6 tests)

Created `tests/test_protocol_not_implemented_production_path.py` with Tests A-E:

- **Test A (PRIMARY SC#2+SC#3):** CliRunner invokes `firestarter read W27C512 <out>` with a REAL `EpromOperator` (not Mock, no `read_eprom.side_effect` injection). Fake serial pre-loaded with FW handshake text + 0xBB id-frame. `__init__`/`send_json_command`/`consume_remaining_input`/`disconnect` mocked; REAL `expect_ack` + `_read_and_parse_lines` run. Asserts: `exit_code == 1`; `"Unsupported protocol"` in output; `"Protocol 0x0b not implemented"` in output; NOT `"No compatible programmer found"`; NOT `"Programmer error"`
- **Test B:** `expect_ack()` raises `ProtocolNotImplementedError` on fed 0xBB frame (not 2-tuple)
- **Test C:** `_probe_port` raises `ProtocolNotImplementedError` after valid FW handshake + 0xBB user-command ack (not `None`)
- **Test D:** `_main_phase_read_data` and `_main_phase_send_data` raise `ProtocolNotImplementedError` on 0xBB ERROR frame (WR-02)
- **Test E:** Non-0xBB ERROR at probe time (`MSG_ERR_NOT_SUPPORTED`) still surfaces as `ProgrammerNotFoundError` — proves 0xBB discrimination is specific

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule:

1. **Task 1: Option B typed-raise at probe/connect boundary** — `734e914` (feat)
2. **Task 2: WR-02 closure + caller sweep** — `3d4cbdf` (fix)
3. **Task 3: Production-path integration tests** — `6bafe00` (test)

## Files Created/Modified

- `firestarter_app/firestarter/serial_comm.py` — import ProtocolNotImplementedError + MSG_ERR_PROTOCOL_NOT_IMPLEMENTED; expect_ack typed raise; _probe_port explicit handler; find_and_connect widened arm
- `firestarter_app/firestarter/eprom_operations.py` — _main_phase_read_data WR-02 fix; _main_phase_send_data WR-02 fix (explicit ERROR branch)
- `firestarter_app/tests/test_protocol_not_implemented_production_path.py` — new file: 6 tests (A-E)

## Option B Caller Sweep (Acceptance Criteria)

Full output captured during Task 2:

```
tests/test_fwguard.py:50:  return_value=(True, mock_msg)   # 2-tuple ✓
tests/test_fwguard.py:77:  return_value=(True, mock_msg)   # 2-tuple ✓
tests/test_fwguard.py:102: return_value=(True, mock_msg)   # 2-tuple ✓
tests/test_fwguard.py:133: return_value=(True, mock_msg)   # 2-tuple ✓
firestarter/firmware.py:102:           is_ok, msg = comm.expect_ack()         # 2-tuple ✓
firestarter/eprom_operations.py:1189:  baseline_ok, _ = comm.expect_ack()     # 2-tuple ✓
firestarter/eprom_operations.py:1199:  corrupt_is_ok, corrupt_msg = ...       # 2-tuple ✓
firestarter/eprom_operations.py:1213:  recovery_ok, _ = comm.expect_ack()     # 2-tuple ✓
firestarter/eprom_operations.py:1378:  is_ok, _ = self.comm.expect_ack()      # 2-tuple ✓
firestarter/eprom_operations.py:1414:  is_ok, _ = self.comm.expect_ack()      # 2-tuple ✓
firestarter/hardware.py:94:   is_ok, msg = comm.expect_ack()                  # 2-tuple ✓
firestarter/hardware.py:148:  is_ok, msg = comm.expect_ack()                  # 2-tuple ✓
firestarter/hardware.py:192:  is_ok, msg = comm.expect_ack()                  # 2-tuple ✓
firestarter/serial_comm.py:628:  pre_is_ok, _pre_msg = communicator.expect_ack()  # 2-tuple ✓
firestarter/serial_comm.py:635:  fw_is_ok, fw_msg = communicator.expect_ack()     # 2-tuple ✓
firestarter/serial_comm.py:683:  is_ok, msg = communicator.expect_ack()           # 2-tuple ✓
firestarter/serial_comm.py:835:  ok, msg = comm.expect_ack(...)                   # 2-tuple ✓
```

**Zero arity-driven edits were needed. Option B confirmed.**

## Decisions Made

- **Option B applied** (as specified in plan): raise inside expect_ack; return arity unchanged; zero blast radius
- **Test A design**: feed text bytes `b"OK: Ready\n"` + `b"OK: FW: 3.0.0...\n"` + 0xBB id-frame; mock only `__init__`/`send_json_command`/`consume_remaining_input`/`disconnect`; REAL `_read_and_parse_lines` + `expect_ack` run against fake serial — proved the typed exception propagates end-to-end through the real code path
- **Test file ordering**: Tests B/C/D/E appear before Test A in the file (simpler tests first, PRIMARY last) — pytest collects all 6 and all pass

## Deviations from Plan

None — plan executed exactly as written. All 3 tasks implemented per spec, all acceptance criteria met.

## Threat Surface Scan

No new threat surface. Plan's T-65-03 (forged 0xBB at probe time → misleading-but-non-destructive CLI message) accepted per plan's threat register. No new endpoints, no new I/O paths, no auth changes.

## Known Stubs

None.

## Self-Check: PASSED

Files exist on disk:
- `firestarter_app/firestarter/serial_comm.py` — FOUND
- `firestarter_app/firestarter/eprom_operations.py` — FOUND
- `firestarter_app/tests/test_protocol_not_implemented_production_path.py` — FOUND
- `.planning/phases/65-host-graceful-handling/65-02-SUMMARY.md` — FOUND

Commits verified:
- `734e914` feat(65-02): Option B typed-raise at probe/connect boundary — FOUND
- `3d4cbdf` fix(65-02): close WR-02 — FOUND
- `6bafe00` test(65-02): production-path integration test — FOUND

Full pytest suite: 486 passed (480 pre-existing + 6 new).

---
*Phase: 65-host-graceful-handling*
*Completed: 2026-06-11*

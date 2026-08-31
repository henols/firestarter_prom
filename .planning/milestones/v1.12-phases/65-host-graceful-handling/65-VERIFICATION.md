---
phase: 65-host-graceful-handling
verified: 2026-06-11T18:30:00Z
status: passed
score: 5/5
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 3/5
  gaps_closed:
    - "expect_ack now raises ProtocolNotImplementedError on id 0xBB (Option B) — the typed error escapes the probe handshake instead of being flattened to (False, msg)"
    - "find_and_connect propagates ProtocolNotImplementedError (widened (FirmwareOutdatedError, ProtocolNotImplementedError) arm) — never falls through to ProgrammerNotFoundError"
    - "_probe_port has explicit except ProtocolNotImplementedError handler placed before bare except Exception — disconnects and re-raises instead of returning None"
    - "_setup_operation does NOT catch ProtocolNotImplementedError (not in (ProgrammerNotFoundError, SerialError) tuple) — propagates to map_typed_errors"
    - "Test A proves the real path: CliRunner + real EpromOperator + fed 0xBB frame -> exit 1, 'Unsupported protocol: Protocol 0x0b not implemented', NOT 'No compatible programmer found', NOT 'Programmer error'"
    - "WR-02 closed: _main_phase_read_data and _main_phase_send_data route ERROR branches through _raise_for_error_response"
  gaps_remaining: []
  regressions: []
---

# Phase 65: Host Graceful Handling Verification Report (Re-verification after 65-02)

**Phase Goal:** When the firmware reports MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, the host raises a typed ProtocolNotImplementedError (not a generic EpromOperationError) and the CLI prints a clear, actionable message including the protocol value — distinguishable from generic operation failures.
**Verified:** 2026-06-11T18:30:00Z
**Status:** passed
**Re-verification:** Yes — after 65-02 gap closure

## CR-01 Adjudication (Code Review Finding — REQUIRED)

The code review labeled CR-01 as a potential BLOCKER: `_run_state_machine` (eprom_operations.py:341) has `except EpromOperationError as e: return False, str(e)`, which would swallow a `ProtocolNotImplementedError` subclass raised inside the state machine. The reviewer noted that Test D calls `_main_phase_read_data` / `_main_phase_send_data` directly, bypassing the state machine, so the swallow goes untested.

**Verdict: CR-01 is a defense-in-depth inconsistency — NOT a production-reachable blocker for the phase goal.**

Reasoning from first-principles firmware and host code reading:

1. **Where does the firmware emit 0xBB?** `configure_not_implemented()` (firestarter/src/proms/not_implemented.cpp:17) is called from `configure_memory()` (memory.cpp:109,117) — during the SETUP phase inside `init_programmer_framed()`. The 0xBB ERROR is emitted BEFORE operation handlers are registered (`handle->firestarter_operation_init/main/end = NULL`). `init_programmer_framed` returns false and never reaches `LOG_OK_ID_U16(MSG_OK_READY)`.

2. **Where is it consumed on the host?** `_probe_port` sends the JSON command at serial_comm.py:682 and calls `communicator.expect_ack()` at :683. With 65-02's Option B fix, `expect_ack` at :444-445 raises `ProtocolNotImplementedError` when `response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`. This exception propagates: `expect_ack` raises → `_probe_port` re-raises (:701-704) → `find_and_connect` re-raises (:759-764) → `_setup_operation` at :243-257 has `except (ProgrammerNotFoundError, SerialError)` which does NOT include `ProtocolNotImplementedError`, so the typed error propagates through `_setup_operation` → `_operation_context` → `read_eprom`/`write_eprom` → `@map_typed_errors` → "Unsupported protocol:" CLI message.

3. **Is `_run_state_machine` ever entered when 0xBB is in flight?** No. `_run_state_machine` is called inside `read_eprom` only if `_setup_operation` returns a non-None `command_dict` and a valid `self.comm` (eprom_operations.py:285, 514, 530). But `find_and_connect` raises `ProtocolNotImplementedError` before returning a communicator. `_setup_operation` never assigns `self.comm` in that case. `_operation_context` yields `None, None, None`, and the `if not cmd_data: return False` guard fires before `_run_state_machine` is ever called.

4. **Can the firmware emit 0xBB mid-MAIN-phase?** No. The protocol-dispatch happens at `configure_memory` time during the SETUP phase. If `configure_not_implemented` fires, the operation function pointers are NULL and the firmware returns error before the state machine protocol starts. There is no code path where the firmware accepts setup (returns MSG_OK_READY) and then emits 0xBB during INIT/MAIN/END data transfer.

5. **Test A confirms the real path:** Test A feeds `b"OK: Ready\n"` + `b"OK: FW: 3.0.0...\n"` + 0xBB id-frame, drives `firestarter read W27C512` via CliRunner with a REAL `EpromOperator` (no `read_eprom.side_effect` injection). It passed with exit_code=1, "Unsupported protocol" in output, "Protocol 0x0b not implemented" in output, and NEITHER "No compatible programmer found" NOR "Programmer error" in output.

**Conclusion:** The `_run_state_machine` swallow at line 341 is never encountered for the 0xBB scenario with current firmware. The WR-02 routing through `_raise_for_error_response` is correct and the typed raise is observable when the handlers are called directly. The inconsistency (a `ProtocolNotImplementedError` raised inside the state machine would be swallowed before reaching `@map_typed_errors`) is a code-quality gap worth addressing in a future clean-up, but it is NOT reachable from any current firmware behavior and does NOT affect the phase goal. CR-01 is recorded as a NOTED FOLLOW-UP, not a blocker.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | ProtocolNotImplementedError is a subclass of EpromOperationError (SC#1) | VERIFIED | `exceptions.py:43`: `class ProtocolNotImplementedError(EpromOperationError): pass`; `issubclass(ProtocolNotImplementedError, EpromOperationError)` == True; no `__init__` override |
| 2 | An ERROR response with id==0xBB raises ProtocolNotImplementedError via the production path (SC#2, HOST-01) | VERIFIED | `expect_ack` (serial_comm.py:444-445) raises `ProtocolNotImplementedError(response.message)` when `response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`; `_probe_port` re-raises (:701-704); `find_and_connect` re-raises (:759-764); `_setup_operation` does not catch it; Test B, C, and A prove the chain end-to-end |
| 3 | A real CLI invocation prints "Unsupported protocol: ... Protocol 0x0b not implemented" and exits 1 — NOT "No compatible programmer found", NOT "Programmer error:" (SC#3, HOST-02 in production) | VERIFIED | Test A (production-path integration test): CliRunner + real EpromOperator + fed 0xBB frame + NO `read_eprom.side_effect` injection; asserts exit_code==1, "Unsupported protocol" in output, "Protocol 0x0b not implemented" in output, "No compatible programmer found" NOT in output, "Programmer error" NOT in output; test passed |
| 4 | ProtocolNotImplementedError arm precedes EpromOperationError arm in map_typed_errors (SC#4) | VERIFIED | cli_handlers.py:120 `except ProtocolNotImplementedError` before :124 `except EpromOperationError`; source-order assertion: index of ProtocolNotImplementedError (639) < index of EpromOperationError (865) |
| 5 | All pre-existing ERROR paths remain green; expect_ack return arity unchanged; 486 tests pass (SC#5) | VERIFIED | Full suite: 486 passed; Option B caller sweep: 14 call sites confirmed as 2-tuple unpackings; test_fwguard.py 4x `return_value=(True, mock_msg)` mocks still valid; ruff + mypy strict green |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/exceptions.py` | ProtocolNotImplementedError(EpromOperationError) class | VERIFIED | Line 43: `class ProtocolNotImplementedError(EpromOperationError): pass` with docstring; no `__init__` override |
| `firestarter_app/firestarter/frame_parser.py` | Response namedtuple with trailing id field (default None) | VERIFIED | `Response = namedtuple("Response", ["type","message","payload","id"], defaults=[None, None])` |
| `firestarter_app/firestarter/serial_comm.py` | expect_ack raises ProtocolNotImplementedError on id 0xBB; _probe_port + find_and_connect propagate it | VERIFIED | expect_ack:444-445 raises; _probe_port:701-704 explicit `except ProtocolNotImplementedError` handler before bare `except Exception`; find_and_connect:759 widened `(FirmwareOutdatedError, ProtocolNotImplementedError)` arm; no 0xBB literal |
| `firestarter_app/firestarter/eprom_operations.py` | _raise_for_error_response dispatches id 0xBB; WR-02 closes _main_phase_read_data + _main_phase_send_data | VERIFIED | `_raise_for_error_response` at :61-77; `_main_phase_read_data` ERROR branch calls it at :472-474; `_main_phase_send_data` has explicit `if response.type == "ERROR": _raise_for_error_response(...)` at :418-419 |
| `firestarter_app/firestarter/cli_handlers.py` | ProtocolNotImplementedError -> actionable ClickException arm before EpromOperationError arm | VERIFIED | Line 120-123: `except ProtocolNotImplementedError as e: raise click.ClickException(f"Unsupported protocol: {e} — this protocol is recognized but not yet implemented in the firmware.") from e`; precedes EpromOperationError arm at :124 |
| `firestarter_app/tests/test_protocol_not_implemented.py` | 5 unit tests for SC#1-SC#4 (65-01) | VERIFIED | 5 tests pass: subclass, typed-raise, CLI message content, catch-ordering + generic-arm-unbroken |
| `firestarter_app/tests/test_protocol_not_implemented_production_path.py` | 6 production-path integration tests (65-02) | VERIFIED | 6 tests pass: Tests A-E (A=primary CLI proof, B=expect_ack unit, C=_probe_port propagation, D=WR-02 MAIN-phase, E=negative control) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `serial_comm.py:expect_ack` | `exceptions.py:ProtocolNotImplementedError` | `raise ProtocolNotImplementedError(response.message)` when `response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` | VERIFIED | serial_comm.py:444-445; uses imported constant, no literal 0xBB |
| `serial_comm.py:_probe_port` | propagates ProtocolNotImplementedError | explicit `except ProtocolNotImplementedError: disconnect(); raise` before bare `except Exception` | VERIFIED | serial_comm.py:701-704; 0xBB does NOT return None |
| `serial_comm.py:find_and_connect` | propagates ProtocolNotImplementedError | widened `except (FirmwareOutdatedError, ProtocolNotImplementedError) as e: raise e` | VERIFIED | serial_comm.py:759-764; does NOT fall through to terminal `raise ProgrammerNotFoundError` |
| `eprom_operations.py:_setup_operation` | propagates ProtocolNotImplementedError naturally | `except (ProgrammerNotFoundError, SerialError)` tuple does NOT include ProtocolNotImplementedError | VERIFIED | eprom_operations.py:254; typed error propagates through _setup_operation → _operation_context → map_typed_errors |
| `cli_handlers.py:map_typed_errors` | `click.ClickException` | `except ProtocolNotImplementedError as e` arm before `EpromOperationError` arm | VERIFIED | "Unsupported protocol: {e} — this protocol is recognized but not yet implemented in the firmware." |

### Data-Flow Trace (Level 4)

Not applicable — this phase implements exception propagation chains, not dynamic data rendering from a DB query.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| ProtocolNotImplementedError is subclass of EpromOperationError | `python -c "from firestarter.exceptions import ProtocolNotImplementedError, EpromOperationError; assert issubclass(ProtocolNotImplementedError, EpromOperationError); print('OK')"` | OK | PASS |
| expect_ack raises ProtocolNotImplementedError on 0xBB frame (not 2-tuple) | Test B: `pytest tests/test_protocol_not_implemented_production_path.py::test_b_expect_ack_raises_protocol_not_implemented_on_0xbb -v` | 1 passed | PASS |
| _probe_port propagates ProtocolNotImplementedError (not None) | Test C: `pytest tests/test_protocol_not_implemented_production_path.py::test_c_probe_port_propagates_protocol_not_implemented_error -v` | 1 passed | PASS |
| CLI prints "Unsupported protocol: Protocol 0x0b not implemented", exit 1 (real path) | Test A: `pytest tests/test_protocol_not_implemented_production_path.py::test_a_cli_read_0xbb_at_probe_time_surfaces_unsupported_protocol -v` | 1 passed | PASS |
| Full suite stays green (486 tests) | `pytest 2>&1 | grep "passed"` | 486 passed | PASS |
| ruff check on modified files | `ruff check firestarter/serial_comm.py firestarter/eprom_operations.py firestarter/cli_handlers.py firestarter/exceptions.py tests/test_protocol_not_implemented_production_path.py tests/test_protocol_not_implemented.py` | All checks passed | PASS |
| mypy strict on serial_comm.py | `mypy firestarter/serial_comm.py` | Success: no issues found | PASS |
| No hardcoded 0xBB in production or test code (detection) | `grep -n '0xBB' firestarter/serial_comm.py tests/test_protocol_not_implemented_production_path.py` | Only in comments/docstrings | PASS |

### Probe Execution

Step 7c: SKIPPED — no probe scripts declared or found for this phase (`find scripts -path '*/tests/probe-*.sh' -type f` returns nothing; this phase is pytest-provable host-only).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| HOST-01 | 65-01-PLAN.md, 65-02-PLAN.md | Host detects not-implemented response and raises typed ProtocolNotImplementedError | SATISFIED | ProtocolNotImplementedError raised at expect_ack (probe boundary) and at _raise_for_error_response (state-machine ERROR branches); Test B, C, D prove the typed raise; Test A proves the production path end-to-end |
| HOST-02 | 65-01-PLAN.md, 65-02-PLAN.md | firestarter read/write/verify against unimplemented-protocol chip prints actionable message with protocol value | SATISFIED | map_typed_errors "Unsupported protocol: {e}" arm at cli_handlers.py:120-123; reached via probe-time propagation chain confirmed by Test A; exit 1, "Protocol 0x0b not implemented" verbatim, NOT "No compatible programmer found", NOT "Programmer error" |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter_app/firestarter/eprom_operations.py` | 341 | `except EpromOperationError as e: return False, str(e)` in `_run_state_machine` — would swallow a ProtocolNotImplementedError subclass raised inside the state machine | Info (CR-01 follow-up) | Not production-reachable with current firmware (0xBB is emitted only during SETUP, before state machine enters); WR-02 routing is correct but the swallow is a defense-in-depth inconsistency. Recommend a future `except ProtocolNotImplementedError: raise` arm before the EpromOperationError arm. |
| `firestarter_app/firestarter/eprom_operations.py` | 73 | `from firestarter.messages import MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` inside function body of `_raise_for_error_response` | Info (WR-02 from code review) | Module-level import would be cleaner; no functional impact. |
| `firestarter_app/firestarter/serial_comm.py` | 444 and `eprom_operations.py:75` | Duplicate 0xBB-dispatch logic in both expect_ack and _raise_for_error_response | Warning (WR-01 from code review) | Two places must be updated if new protocol IDs are added to typed-raise set; natural refactor point in a future phase |

No `TBD`, `FIXME`, or `XXX` debt markers found in files modified by this phase.

### Human Verification Required

None. All success criteria are fully determinable from static code analysis and automated tests. The production-path failure mode confirmed by the prior cycle is now closed. Test A exercises the real CLI path with a real EpromOperator and a fed binary frame.

### CR-01 Follow-up Recommendation

The `_run_state_machine` EpromOperationError swallow at line 341 should be hardened in a future quality phase by adding:

```python
except ProtocolNotImplementedError:
    # Typed-propagate to @map_typed_errors (HOST-02).
    # Must precede EpromOperationError since it is a subclass.
    raise
except EpromOperationError as e:
    logger.error(f"Programmer error during {operation_name}: {e}")
    return False, str(e)
```

This is not a blocker for the current phase because the firmware architecturally cannot emit 0xBB mid-state-machine (the protocol check happens during SETUP/configure_memory before any operation handlers are installed or invoked). But the re-raise would make the WR-02 routing fully defensible without relying on the firmware-architecture constraint.

The callers `consistency_check_eprom` (line 675) and `write_cycle_eprom` (line 841) also have their own `except EpromOperationError` arms that would need auditing when this fix is applied.

### Gaps Summary

No gaps. All 5/5 truths verified. The SC#2 (HOST-01) and SC#3 (HOST-02) gaps identified in the prior cycle are closed by 65-02's Option B implementation. CR-01 from the code review is a quality finding about defense-in-depth but is not a production blocker.

---

_Verified: 2026-06-11T18:30:00Z_
_Verifier: Claude (gsd-verifier)_
_Re-verification: Yes — post-65-02 gap closure_

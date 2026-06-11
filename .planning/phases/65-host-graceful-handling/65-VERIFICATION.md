---
phase: 65-host-graceful-handling
verified: 2026-06-11T17:00:00Z
status: gaps_found
score: 3/5 must-haves verified
overrides_applied: 0
gaps:
  - truth: "An ERROR response whose decoded message id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED (0xBB) raised inside _run_state_machine produces a ProtocolNotImplementedError, not a generic EpromOperationError (SC#2, HOST-01)"
    status: partial
    reason: "The unit test passes by directly calling _execute_phase, bypassing the real production entry path. In production, the 0xBB ERROR frame is consumed by expect_ack() inside _probe_port at connect time, before _run_state_machine is ever entered. The typed raise sites in _execute_phase and _main_phase_simple are unreachable for the 0xBB path."
    artifacts:
      - path: "firestarter_app/firestarter/serial_comm.py"
        issue: "expect_ack() returns (False, response.message) — the Response.id field (which IS populated since Task 1) is silently discarded in the return signature Tuple[bool, Optional[str]]; callers cannot inspect it"
      - path: "firestarter_app/firestarter/serial_comm.py"
        issue: "_probe_port lines 680-690: is_ok=False -> logs debug, disconnects, returns None; no ProtocolNotImplementedError raised, no id-discrimination possible with current return type"
      - path: "firestarter_app/firestarter/eprom_operations.py"
        issue: "_setup_operation lines 254-257: catches (ProgrammerNotFoundError, SerialError) and returns (None, 0); ProtocolNotImplementedError is not in the except tuple and never propagates from this path anyway since it is never raised"
    missing:
      - "Thread Response.id through expect_ack return signature (e.g. return Tuple[bool, Optional[str], Optional[int]]) OR raise ProtocolNotImplementedError directly inside expect_ack when response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED"
      - "In _probe_port: after is_ok=False, check the id from expect_ack and raise ProtocolNotImplementedError instead of silently returning None"
      - "In find_and_connect: propagate ProtocolNotImplementedError (alongside FirmwareOutdatedError) instead of swallowing it as a connect failure"
      - "In _setup_operation: add ProtocolNotImplementedError to the except tuple (or let it propagate naturally) so the operation-level callers can surface the typed error to map_typed_errors"

  - truth: "A mocked CLI invocation against a chip with an unimplemented protocol prints a message that includes the firmware-rendered protocol value (e.g. 'Protocol 0x0b not implemented') and communicates known-but-not-yet-supported, distinct from 'Programmer error:' (SC#3, HOST-02)"
    status: failed
    reason: "SC#3 is satisfied only by a test that mocks the operator to raise ProtocolNotImplementedError directly (side_effect injection). In a real firestarter read/write invocation against an unimplemented-protocol chip, the 0xBB ERROR frame is intercepted at _probe_port before the state machine runs; _setup_operation catches ProgrammerNotFoundError and returns (None, 0); the CLI prints 'Error: Failed to setup operation...' via logger.error and exits 1. The 'Unsupported protocol:' CLI message is never reached."
    artifacts:
      - path: "firestarter_app/tests/test_protocol_not_implemented.py"
        issue: "test_cli_unsupported_protocol_message_content and test_map_typed_errors_ordering_subclass_not_caught_by_base both use operator.read_eprom.side_effect = ProtocolNotImplementedError(...) — they verify map_typed_errors ordering is correct but do NOT test the actual production code path from firmware 0xBB response to CLI message"
    missing:
      - "An end-to-end test or production-path fix that drives the real path: build_frame(0xBB) -> expect_ack -> _probe_port -> _setup_operation -> CLI surface"
      - "The map_typed_errors fix (arm is correct and tested) is wasted without the upstream production path fix described in the SC#2 gap above"
---

# Phase 65: Host Graceful Handling Verification Report

**Phase Goal:** When the firmware reports MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, the host raises a typed ProtocolNotImplementedError (not a generic EpromOperationError) and the CLI prints a clear, actionable message including the protocol value — distinguishable from generic operation failures.
**Verified:** 2026-06-11T17:00:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | ProtocolNotImplementedError is a subclass of EpromOperationError (SC#1) | VERIFIED | `exceptions.py:43`: `class ProtocolNotImplementedError(EpromOperationError): pass`; `issubclass(ProtocolNotImplementedError, EpromOperationError)` asserted True |
| 2 | ERROR response with id==0xBB inside _run_state_machine raises ProtocolNotImplementedError (SC#2, HOST-01) | PARTIAL | The raise site exists in `_execute_phase` and `_main_phase_simple` via `_raise_for_error_response`; the pytest test passes by feeding frames directly to `_execute_phase`. But in production the 0xBB ERROR frame is consumed by `expect_ack()` in `_probe_port` before `_run_state_machine` is ever invoked — the raise sites are unreachable. |
| 3 | Mocked CLI invocation prints actionable message with protocol value, distinct from 'Programmer error:' (SC#3, HOST-02) | FAILED | SC#3's test uses `side_effect = ProtocolNotImplementedError(...)` injected directly on the mock operator — it verifies `map_typed_errors` ordering, not the production path. A real `firestarter read/write` against an unimplemented-protocol chip exits 1 with a generic logger-level error message from `_setup_operation`, never reaching `map_typed_errors`. |
| 4 | ProtocolNotImplementedError arm precedes EpromOperationError arm in map_typed_errors (SC#4) | VERIFIED | `cli_handlers.py:120-123` has `except ProtocolNotImplementedError` at source index 639, `except EpromOperationError` at index 865; source-order assertion confirmed |
| 5 | All pre-existing ERROR paths in the state machine remain green; no positional Response(...) caller breaks | VERIFIED | Full suite 480 passed; GATE-1.8d ringfence SHA updated; test_decoder.py Response id field fix committed; ruff + mypy strict green on all 8 strict modules |

**Score:** 3/5 truths verified

### Production-Path Reachability Trace (Root Cause of SC#2/SC#3 Gap)

The gap is structural and confirmed by independent code reading. Here is the exact execution trace for a real `firestarter read <unimplemented-protocol-chip>`:

**Firmware side (firestarter/src/firestarter.cpp:86 → src/proms/memory.cpp:116 → src/proms/not_implemented.cpp:17):**

1. `loop()` receives COBS-decoded JSON command with `algorithm=<unimplemented-nonzero-protocol>`
2. `init_programmer_framed()` calls `parse_json()` at line 124
3. `parse_json()` calls `op_execute_function(configure_memory, handle)` at line 86
4. `configure_memory()` hits the fail-closed guard (line 116: `if (handle->protocol != 0)`) and calls `configure_not_implemented(handle)`
5. `configure_not_implemented` emits `LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, protocol)` — the 0xBB ERROR frame is sent over serial — and sets `handle->response_code = RESPONSE_CODE_ERROR`
6. `op_execute_function` returns false; `parse_json()` also emits `LOG_ERROR_ID(MSG_ERR_SETUP)` (a second ERROR frame) and returns false
7. `init_programmer_framed()` returns false — never reaches `LOG_OK_ID_U16(MSG_OK_READY)` at line 142

**Host side (serial_comm.py:680 → eprom_operations.py:254):**

8. `_probe_port` sends the JSON command at line 679, then calls `communicator.expect_ack()` at line 680
9. `expect_ack()` (lines 432-444) calls `get_response()` in a loop; the first significant response is the 0xBB ERROR frame. It returns `(False, response.message)` — `response.id` (which IS populated as `0xBB` by the Response construction at `serial_comm.py:393-398`) is discarded in the return signature
10. `_probe_port` at line 688: `is_ok=False` triggers the else branch — logs debug "responded but not with OK", calls `disconnect()`, returns `None`
11. `find_and_connect` (line 761) raises `ProgrammerNotFoundError("No compatible programmer found on any port.")`
12. `_setup_operation` (line 254) catches `(ProgrammerNotFoundError, SerialError)`, logs `logger.error(f"Failed to setup operation ... ")`, returns `(None, 0)`
13. `_operation_context` yields `None, None, None`; the public operation method (e.g. `read_eprom`) returns `False`
14. CLI handler exits 1 — no exception propagates to `map_typed_errors`, no "Unsupported protocol:" message is printed

**Conclusion:** The `_raise_for_error_response` helper, the `ProtocolNotImplementedError` arm in `map_typed_errors`, and the `Response.id` plumbing are all internally correct and well-tested. But they are disconnected from the actual production path for the 0xBB error case. The fix belongs at the probe/connect boundary: `expect_ack` must surface `response.id` to its callers so `_probe_port` can raise `ProtocolNotImplementedError` instead of returning `None`.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/exceptions.py` | ProtocolNotImplementedError(EpromOperationError) class | VERIFIED | Class exists at line 43 with docstring; pass body; no __init__ override |
| `firestarter_app/firestarter/frame_parser.py` | Response namedtuple carrying decoded message id | VERIFIED | `Response = namedtuple("Response", ["type","message","payload","id"], defaults=[None, None])` at line 17-19 |
| `firestarter_app/firestarter/eprom_operations.py` | id-0xBB -> typed-exception dispatch from the ERROR path | PARTIAL | `_raise_for_error_response` exists and is used by `_execute_phase` and `_main_phase_simple`; but these sites are unreachable for 0xBB in production. Also, `_main_phase_read_data` (line 470) and `_main_phase_send_data` (line 419) still raise bare `EpromOperationError` — WR-02 from code review confirmed |
| `firestarter_app/firestarter/cli_handlers.py` | ProtocolNotImplementedError -> actionable ClickException arm before EpromOperationError arm | VERIFIED | `except ProtocolNotImplementedError as e:` at line 120, before `except EpromOperationError` at line 124; message: "Unsupported protocol: {e} — this protocol is recognized but not yet implemented in the firmware." |
| `firestarter_app/tests/test_protocol_not_implemented.py` | pytest coverage of the 4 CONTEXT.md cases | PARTIAL | 5 tests pass; but SC#2 asserts on `_execute_phase` directly (not the real production entry point) and SC#3 uses mock side_effect injection — neither test exercises the real `find_and_connect` → `expect_ack` → `_probe_port` path |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `serial_comm.py` | `Response.id` | `id=decoded.id` at id-frame decode site | VERIFIED | `serial_comm.py:397`: `id=decoded.id` confirmed in Response construction |
| `eprom_operations.py` | `exceptions.py` | `_raise_for_error_response` dispatch on response.id | PARTIAL | Link exists but is only reachable if the Response with id==0xBB reaches the state machine; in production the frame is consumed earlier at `_probe_port/expect_ack` |
| `cli_handlers.py` | `click.ClickException` | `except ProtocolNotImplementedError` before `except EpromOperationError` | VERIFIED | Source-order confirmed; but this arm is only reached if ProtocolNotImplementedError propagates through `_setup_operation`, which it does not in the current implementation |
| `expect_ack` return | `_probe_port` callers | id field exposed in return value | NOT_WIRED | `expect_ack` returns `Tuple[bool, Optional[str]]` — id is not returned; `_probe_port` cannot distinguish a 0xBB ERROR from any other ERROR response |

### Data-Flow Trace (Level 4)

Not applicable — this phase does not render dynamic data from a DB query. The data flow is an exception propagation chain.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| ProtocolNotImplementedError is subclass of EpromOperationError | `python -c "from firestarter.exceptions import ProtocolNotImplementedError, EpromOperationError; assert issubclass(ProtocolNotImplementedError, EpromOperationError); print('OK')"` | OK | PASS |
| Response namedtuple carries id field with default None | `python -c "from firestarter.frame_parser import Response; r=Response(type='ERROR', message='x'); assert r.id is None; r2=Response(type='ERROR', message='x', id=0xBB); assert r2.id==0xBB; print('OK')"` | OK | PASS |
| expect_ack discards id in return value | `inspect.getsource(SerialCommunicator.expect_ack)` — return type is `Tuple[bool, Optional[str]]`; id is not returned | id is dropped | CONFIRMS GAP |
| SC#2 test targets _execute_phase directly, not _run_state_machine or find_and_connect | `test_state_machine_raises_protocol_not_implemented_on_0xbb_frame` calls `operator._execute_phase(...)` | Bypasses production entry path | CONFIRMS GAP |
| Full test suite green | `pytest -q` | 480 passed | PASS |

### Probe Execution

Step 7c: SKIPPED — no probe scripts declared or found for this phase (`find scripts -path '*/tests/probe-*.sh' -type f` returns nothing; this phase is a pytest-provable host-only change).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| HOST-01 | 65-01-PLAN.md | Host detects not-implemented response and raises typed ProtocolNotImplementedError | PARTIAL | The typed exception class exists and the dispatch helper is correct; but the 0xBB frame is consumed before it can reach the raise site in production. Unit test covers the dispatch in isolation. |
| HOST-02 | 65-01-PLAN.md | firestarter write/read/verify against unimplemented-protocol chip prints actionable message with protocol value | FAILED | The actionable "Unsupported protocol:" CLI arm is wired correctly in map_typed_errors, but the production path for a real invocation never reaches it. The operator would see "Error: Failed to setup operation read for <chip>: No compatible programmer found on any port." |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter_app/firestarter/eprom_operations.py` | 470 | `raise EpromOperationError(...)` in `_main_phase_read_data` — bypasses `_raise_for_error_response` | Warning | WR-02 from code review: inconsistent coverage of ERROR branches; a 0xBB during a read MAIN phase would surface as generic error |
| `firestarter_app/firestarter/eprom_operations.py` | 419 | `raise EpromOperationError(...)` in `_main_phase_send_data` — bypasses `_raise_for_error_response` | Warning | WR-02 from code review: same inconsistency for write MAIN phase |
| `firestarter_app/firestarter/eprom_operations.py` | 73 | `from firestarter.messages import MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` inside function body | Info | IN-01 from code review: runs on every ERROR-branch hit; cosmetic only |

No `TBD`, `FIXME`, or `XXX` debt markers found in modified files.

### Human Verification Required

None — the gap is fully determinable from static code analysis. The production path failure is structural (wrong code path) not behavioral (UX/visual).

### Gaps Summary

**Root cause:** The phase wired `_raise_for_error_response` in the state machine's INIT/MAIN/END phases, and the CLI arm correctly in `map_typed_errors`. However, the 0xBB ERROR frame is emitted by the firmware during command setup (before the operation state machine begins), and the host's `_probe_port`/`expect_ack` connect-time handshake intercepts it. `expect_ack` discards the `Response.id` in its return value, so the ERROR cannot be distinguished from any other connection failure. The operation never reaches `_run_state_machine`, and `ProtocolNotImplementedError` is never raised.

**Affected success criteria:** SC#2 (HOST-01) is met at unit level only; SC#3 (HOST-02) is not met in production.

**Unaffected:** SC#1 (subclass hierarchy), SC#4 (catch ordering), and the pre-existing error path regression tests are all correct.

**Suggested fix approach:**

Option A (minimal, targeted): In `expect_ack`, return the id alongside the existing values:
```python
def expect_ack(self, timeout=...) -> Tuple[bool, Optional[str], Optional[int]]:
    response = self.get_response(timeout)
    if response.type == "OK":
        return True, response.message, response.id
    elif response.type == "ERROR":
        return False, response.message, response.id
```
Then in `_probe_port`, after `is_ok=False`, check id and raise `ProtocolNotImplementedError` instead of returning `None`. Update `find_and_connect` to propagate `ProtocolNotImplementedError` (alongside `FirmwareOutdatedError`). Update `_setup_operation` to add `ProtocolNotImplementedError` to the except tuple (or let it propagate to `map_typed_errors`).

Option B (alternative): Raise `ProtocolNotImplementedError` directly inside `expect_ack` when `response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`, preserving the existing return signature for all other ERROR responses.

Both options require an integration-level test that exercises the full path from `build_frame(0xBB)` through `find_and_connect` / `_probe_port` to confirm the typed error surfaces at the CLI layer.

---

_Verified: 2026-06-11T17:00:00Z_
_Verifier: Claude (gsd-verifier)_

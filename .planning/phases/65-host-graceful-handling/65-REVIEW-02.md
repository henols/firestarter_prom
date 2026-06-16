---
phase: 65-host-graceful-handling
reviewed: 2026-06-11T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - firestarter_app/firestarter/serial_comm.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/tests/test_protocol_not_implemented_production_path.py
findings:
  critical: 1
  warning: 3
  info: 2
  total: 6
status: issues_found
---

# Phase 65: Code Review Report (Plan 65-02 gap closure)

**Reviewed:** 2026-06-11
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Plan 65-02 implements Option B: `expect_ack` raises `ProtocolNotImplementedError`
in-place at the probe boundary, `_probe_port` / `find_and_connect` propagate it,
WR-02 routes four MAIN/INIT/END ERROR branches through `_raise_for_error_response`,
and a new production-path test file (Tests A–E) covers the connect boundary.

The probe-boundary wiring (the primary 65-02 deliverable) is correct and well
tested: Test A drives the real `find_and_connect → _probe_port → _setup_operation
→ read_eprom → @map_typed_errors → CLI` path and proves "Unsupported protocol"
with exit 1. `expect_ack`'s return arity is genuinely unchanged (`Tuple[bool,
Optional[str]]`); the typed exception is raised before any tuple return. No
hardcoded `0xBB` literal exists in production code — both detection sites key on
the imported `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` constant. mypy-strict passes on
`serial_comm.py`, ruff + ruff-format are clean on all three files, and the new
test file passes (6/6).

However, the **WR-02 MAIN-phase routing is dead in production**: every
`_raise_for_error_response` call site executes inside `_run_state_machine`, whose
`except EpromOperationError` arm (line 341) catches the `ProtocolNotImplementedError`
subclass and collapses it to `(False, str(e))` — so the typed exception never
reaches the CLI's `@map_typed_errors` decorator. The new Test D masks this by
calling the MAIN-phase handlers directly, bypassing the state machine. See CR-01.

## Critical Issues

### CR-01: WR-02 typed exception is swallowed by `_run_state_machine` — MAIN/INIT/END-phase 0xBB never reaches the CLI

**File:** `firestarter_app/firestarter/eprom_operations.py:341` (catch) vs `:360, :397, :419, :472` (raise sites)

**Issue:**
`ProtocolNotImplementedError` subclasses `EpromOperationError`
(`exceptions.py:43`). All four WR-02 `_raise_for_error_response` call sites run
inside the `try` block of `_run_state_machine`:

- `:360` — `_execute_phase` (INIT/END phases)
- `:397` — `_main_phase_simple`
- `:419` — `_main_phase_send_data`
- `:472` — `_main_phase_read_data`

`_run_state_machine` catches `EpromOperationError` at line 341 and returns
`(False, str(e))`. Because `ProtocolNotImplementedError` IS an
`EpromOperationError`, the typed exception raised by WR-02 is caught here and
flattened to a 2-tuple. The CLI then sees only `is_ok == False` → generic exit 1
with NO "Unsupported protocol" message — the exact pre-65 failure mode WR-02 was
supposed to fix, just relocated from the probe boundary to the MAIN-phase
boundary.

This means a firmware that accepts the connect/setup command but emits a 0xBB
`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` during a MAIN-phase data transfer (e.g. a
write/verify chunk loop, or an INIT/END handshake) will surface as a generic
"Write to ... failed." / silent `is_ok=False`, not as the actionable
"Unsupported protocol:" CLI message. WR-02's stated intent ("route two MAIN-phase
ERROR branches through `_raise_for_error_response`") is necessary but not
sufficient — the routing produces a typed exception that is then discarded.

The prior-phase test (`test_protocol_not_implemented.py:99-129`) explicitly
documents awareness of this swallow ("_run_state_machine has an outer `except
EpromOperationError` catch that returns (False, msg) ... so we assert on
_execute_phase directly to observe the typed raise before the outer catch
swallows it"). The new Test D
(`test_protocol_not_implemented_production_path.py:194-250`) repeats this
shortcut — it calls `_main_phase_read_data` / `_main_phase_send_data` **directly**,
never through `_run_state_machine`, so it is green while the production path is
broken. The file's own docstring claims "Every test here drives the REAL ... path
— NO _execute_phase shortcut," but Test D does take the handler-direct shortcut
for the state-machine layer, contradicting that claim.

**Fix:** Re-raise the typed subclass before the base-class arm in
`_run_state_machine` so it propagates to `@map_typed_errors`:

```python
        except (SerialError, SerialTimeoutError) as e:
            logger.error(f"Communication error during {operation_name}: {e}")
            return False, str(e)
        except ProtocolNotImplementedError:
            # Typed-propagate to the CLI @map_typed_errors boundary (HOST-02).
            # Must precede the EpromOperationError arm since it is a subclass.
            raise
        except EpromOperationError as e:
            logger.error(f"Programmer error during {operation_name}: {e}")
            return False, str(e)
```

Then add a true production-path Test D that drives a MAIN-phase 0xBB through
`_run_state_machine` (or through `read_eprom` / `write_eprom` + CliRunner) and
asserts "Unsupported protocol" reaches `result.output` with exit 1 — mirroring
Test A. Note: the `consistency_check_eprom` / `write_cycle_eprom` callers map
`(False, msg)` to exit code 2 and separately catch `EpromOperationError`
(lines 675, 841) — re-raising `ProtocolNotImplementedError` will now propagate
through those `except EpromOperationError` arms too unless they are updated; audit
those call sites when applying the fix.

## Warnings

### WR-01: Duplicated 0xBB-dispatch logic across two modules instead of one helper

**File:** `firestarter_app/firestarter/serial_comm.py:444` and `firestarter_app/firestarter/eprom_operations.py:75`

**Issue:** The id-keyed detection `if response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED:
raise ProtocolNotImplementedError(response.message)` exists in two places —
inline in `expect_ack` (serial_comm.py:444-445) and inside
`_raise_for_error_response` (eprom_operations.py:75-76). The
`_raise_for_error_response` docstring claims it "Centralises typed-exception
dispatch ... so id-keyed detection is not duplicated per raise site," but the
`expect_ack` site duplicates the same predicate independently. A future protocol
ID added to the typed-raise set must be changed in both modules, and they can
drift. (serial_comm.py is in the mypy-strict island and cannot import
eprom_operations.py without a layering inversion, so the natural fix is a shared
helper in a leaf module such as `messages.py` or `frame_parser.py`.)

**Fix:** Extract a single predicate/dispatch helper into a leaf module both
importers can use, e.g. `is_protocol_not_implemented(response) -> bool` in
`frame_parser.py`, and call it from both `expect_ack` and
`_raise_for_error_response`.

### WR-02: `_raise_for_error_response` parameter is untyped and uses a function-local import

**File:** `firestarter_app/firestarter/eprom_operations.py:61, 73`

**Issue:** `def _raise_for_error_response(response, message: str) -> None:` —
`response` is untyped (no `Response` annotation), and
`from firestarter.messages import MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` is performed
inside the function body (line 73) on every call rather than at module top. The
module-level import block (lines 44-54) already imports from
`firestarter.messages` would be the natural home; there is no circular-import
reason for a function-local import here (`messages.py` is a leaf catalog).
eprom_operations.py is outside the strict island so the missing annotation is not
a CI failure, but it weakens the contract: a caller passing an object without an
`.id` attribute fails with `AttributeError` at runtime rather than a type error.

**Fix:** Annotate `response: Response` (import `Response` from `frame_parser`) and
hoist the `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` import to the module-level
`from firestarter.messages import (...)` block.

### WR-03: Test D leaves a `delete=False` temp file on early failure paths

**File:** `firestarter_app/tests/test_protocol_not_implemented_production_path.py:238-250`

**Issue:** `tempfile.NamedTemporaryFile(suffix=".bin", delete=False)` creates a
file that is only removed by the `finally: os.unlink(input_path)`. The `finally`
covers the `pytest.raises` block, so the happy path is fine. However the file is
created at line 238 and `input_path` is bound inside the `with
NamedTemporaryFile(...)` block; if the write at line 240 (`f.write(b"\xff" *
512)`) raises (e.g. disk full) before the `try` is entered, the file is leaked.
Minor, but the broader pattern (also used in Test A, lines 344-364) is fragile.

**Fix:** Use the `tmp_path` pytest fixture instead of manual
`NamedTemporaryFile(delete=False)` + `os.unlink` — it is auto-cleaned and removes
the leak window entirely.

## Info

### IN-01: Test D does not assert the negative (no `EpromOperationError`-only leakage)

**File:** `firestarter_app/tests/test_protocol_not_implemented_production_path.py:210-216, 243-248`

**Issue:** Test D asserts `pytest.raises(ProtocolNotImplementedError)`, which is
satisfied by the subclass — but it does not pin that the message is the
firmware-rendered "Protocol 0x0b not implemented" text, nor (per CR-01) that the
exception survives `_run_state_machine`. Tests A and E include MANDATORY negative
assertions; Test D has none, which is why the CR-01 swallow went undetected.

**Fix:** After fixing CR-01, strengthen Test D to drive `_run_state_machine` (or a
full `write_eprom` CliRunner invocation) and assert both the typed type and the
"Unsupported protocol" / "Protocol 0x0b not implemented" message content.

### IN-02: `_make_fake_comm` duplicates the conftest `make_comm` factory

**File:** `firestarter_app/tests/test_protocol_not_implemented_production_path.py:89-100`

**Issue:** `_make_fake_comm` re-implements the attribute-by-attribute
`SerialCommunicator.__new__` construction already provided by the conftest
`make_comm` fixture (conftest.py:127-151). Both set the same seven attributes; if
`__init__` gains a new attribute, both must be updated in lockstep. The `mock_init`
closures inside Tests A/C/E duplicate the same seven assignments a third/fourth/
fifth time.

**Fix:** Reuse the conftest `make_comm` factory (or a shared `mock_init` helper)
to construct fake communicators in one place.

---

_Reviewed: 2026-06-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

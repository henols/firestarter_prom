---
phase: 65-host-graceful-handling
reviewed: 2026-06-11T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - firestarter_app/firestarter/exceptions.py
  - firestarter_app/firestarter/frame_parser.py
  - firestarter_app/firestarter/serial_comm.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/tests/test_protocol_not_implemented.py
  - firestarter_app/tests/test_decoder.py
  - firestarter_app/tests/test_serial_comm.py
findings:
  critical: 0
  warning: 3
  info: 3
  total: 6
status: issues_found
---

# Phase 65: Code Review Report

**Reviewed:** 2026-06-11
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Phase 65 adds host-side typed handling of the firmware's `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`
(0xBB) error: a new `ProtocolNotImplementedError(EpromOperationError)`, a `Response.id`
field, a centralised `_raise_for_error_response` dispatch helper, and a CLI
"Unsupported protocol:" arm in `map_typed_errors`.

The core mechanism is sound and well-tested at the unit level: the `Response` namedtuple
default for `id` is `None` (verified), so text-path responses fall through to
`EpromOperationError` correctly; the CLI arm ordering places the subclass before the
base-class arm; and all gates (ruff check, ruff format --check, mypy on the four strict
modules, the new test module, decoder/serial test modules) pass locally.

The defects found are not in the added code's internal correctness but in its **coverage
of the actual production raise path** and **consistency across the four ERROR-branch
sites in the state machine**. Two ERROR branches were left raising bare
`EpromOperationError` and bypass the new dispatch helper, and there is a real question
whether the wired raise sites are ever reached in production given the firmware emits
0xBB at setup time (before the host's INIT/MAIN ack loops begin).

Note: the phase prompt states `eprom_operations.py` is mypy-strict. It is NOT — it is
explicitly excluded from the strict island per Phase 42 D-07 (GATE-1.8d ring-fence).
The strict modules are `cli_handlers.py`, `frame_parser.py`, `serial_comm.py`,
`exceptions.py`. This matters because the untyped `response` parameter on
`_raise_for_error_response` (see IN-02) is acceptable only because the module is lenient.

## Warnings

### WR-01: 0xBB is emitted at firmware setup time and swallowed by `find_and_connect` — the wired typed-raise sites may never fire in production

**File:** `firestarter_app/firestarter/eprom_operations.py:347-366` (`_execute_phase`),
`firestarter_app/firestarter/eprom_operations.py:388-401` (`_main_phase_simple`);
cross-ref `firestarter/src/firestarter.cpp:86-89`, `firestarter/src/proms/not_implemented.cpp:13-19`

**Issue:** The firmware emits `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` from
`configure_not_implemented()`, which runs inside `configure_memory()` →
`init_programmer_framed()` while the firmware is still at `CMD_IDLE` (firestarter.cpp:86).
On failure, `init_programmer_framed` returns false and the firmware never enters the
operation state machine (`firestarter_operation_init/main/end` are all set to `NULL`).

On the host, that 0xBB ERROR frame is observed by `expect_ack()` inside
`SerialCommunicator._probe_port` (serial_comm.py:680, and the FW-probe `expect_ack` at
:625/:632), which returns `(False, msg)`. `_probe_port` then logs at debug level and
returns `None`; `find_and_connect` raises `ProgrammerNotFoundError` only after all ports
fail. `_setup_operation` catches `(ProgrammerNotFoundError, SerialError)` and returns
`(None, 0)` — the operation simply returns `False` with no typed exception.

The new typed-raise sites are inside `_execute_phase("INIT"/"END")` and
`_main_phase_simple`, which run only **after** a successful setup ack. Since the firmware
aborts setup before reaching the state machine when a protocol is unimplemented, the
0xBB frame is consumed in `find_and_connect` and never reaches a `_raise_for_error_response`
call site. The SC#2 unit test passes only because it feeds the frame directly to
`_execute_phase`, bypassing the real setup path.

Net effect: in production a `firestarter read <chip>` against an unimplemented protocol
likely surfaces as a generic "No compatible programmer found" / silent `False`, not the
new "Unsupported protocol:" CLI message — i.e. the feature's user-visible goal may not be
delivered on the real wire path.

**Fix:** Confirm the intended production path. Either (a) detect 0xBB in
`_probe_port`/`expect_ack` (capture `Response.id` through `expect_ack` and raise
`ProtocolNotImplementedError` there so `_setup_operation` can propagate it instead of
swallowing it as a connect failure), or (b) document explicitly that 0xBB handling is
defensive-only for a future firmware that emits it mid-state-machine, and add an
integration-level test that drives the full `_probe_port` → setup → CLI path with a 0xBB
ack to pin the actual surfaced message. As written, `expect_ack` discards the `id`:
```python
def expect_ack(self, timeout=...) -> Tuple[bool, Optional[str]]:
    while True:
        response = self.get_response(timeout)
        if response.type == "OK":
            return True, response.message
        elif response.type == "ERROR":
            # id is dropped here — _probe_port cannot distinguish 0xBB from any other ERROR
            return False, response.message
```

### WR-02: Two of the four state-machine ERROR branches bypass `_raise_for_error_response`

**File:** `firestarter_app/firestarter/eprom_operations.py:469-471` (`_main_phase_read_data`),
`firestarter_app/firestarter/eprom_operations.py:418-421` (`_main_phase_send_data`)

**Issue:** The phase docstring for `_raise_for_error_response` states it "Centralises
typed-exception dispatch for all ERROR-branch sites in the state machine so id-keyed
detection is not duplicated per raise site." But only two of the four ERROR-handling
sites were converted:

- `_execute_phase` (:359) — uses `_raise_for_error_response` ✓
- `_main_phase_simple` (:396) — uses `_raise_for_error_response` ✓
- `_main_phase_read_data` (:469) — raises bare `EpromOperationError(...)` ✗
- `_main_phase_send_data` (:418) — raises bare `EpromOperationError(...)` ✗

If a future firmware (or a hand-crafted/replayed frame) delivers a 0xBB ERROR during a
read or write MAIN phase, it will surface as a generic "Programmer error:" rather than
"Unsupported protocol:" — defeating the centralisation the helper was introduced for and
producing inconsistent behaviour across phases. This is the same class of latent gap that
WR-01 describes, but it is a clear in-code inconsistency regardless of current firmware
timing.

**Fix:** Route both branches through the helper for consistency:
```python
# _main_phase_read_data, replacing :469-471
if response.type == "ERROR":
    _raise_for_error_response(
        response, f"Programmer error during read: {response.message}"
    )

# _main_phase_send_data, add an explicit ERROR branch before the "did not request
# data chunk" generic raise at :418, mirroring the others:
if response.type == "ERROR":
    _raise_for_error_response(response, response.message)
```

### WR-03: Inconsistent fallback-message framing between the two converted raise sites

**File:** `firestarter_app/firestarter/eprom_operations.py:360-363` vs
`firestarter_app/firestarter/eprom_operations.py:397`

**Issue:** `_execute_phase` passes a framed message
(`f"Programmer error during {phase_name.lower()}: {response.message}"`) to
`_raise_for_error_response`, while `_main_phase_simple` passes the raw `response.message`
unchanged. The `message` argument is only used for the `EpromOperationError` fallback
(the 0xBB path ignores it and re-uses `response.message`). The result is that a generic
(non-0xBB) programmer error raised from the INIT/END phase reads
"Programmer error during init: <msg>" while the same error from the simple MAIN phase
reads just "<msg>" — producing inconsistent CLI "Programmer error:" output depending on
which phase failed. This is a behaviour drift for the existing (non-0xBB) error path that
the refactor introduced.

**Fix:** Pick one framing convention. If phase-name framing is desired everywhere, pass
`f"Programmer error during main: {response.message}"` from `_main_phase_simple`; if raw
pass-through is desired, drop the prefix in `_execute_phase`. Align both call sites.

## Info

### IN-01: `_raise_for_error_response` has an in-function import that runs on every ERROR

**File:** `firestarter_app/firestarter/eprom_operations.py:73`

**Issue:** `from firestarter.messages import MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` is imported
inside the function body. The module-level docstring on `_main_phase_read_data` (:456)
justifies a local import for `MSG_DATA_CHUNK` to "avoid circular" imports, but
`eprom_operations.py` already imports from `firestarter.messages` at other call sites and
`messages` is a leaf catalog module. The local import is executed on every ERROR-branch
hit. This is cosmetic (not hot-path), but the constant could be hoisted to module scope
alongside the other top-of-file imports for clarity.

**Fix:** If no genuine circular-import constraint exists, move the import to the module
top with the other `firestarter.constants`/`firestarter.frame_parser` imports.

### IN-02: `_raise_for_error_response` `response` parameter is untyped

**File:** `firestarter_app/firestarter/eprom_operations.py:61`

**Issue:** `def _raise_for_error_response(response, message: str) -> None:` — `response`
has no annotation. It is read for `.id` and `.message`, so the intended type is
`frame_parser.Response`. This is permitted only because `eprom_operations.py` is excluded
from the mypy strict island (NOT strict, contrary to the phase prompt). Annotating it
would catch a future caller that passes the wrong shape (e.g. a raw tuple without `id`).

**Fix:** `def _raise_for_error_response(response: "Response", message: str) -> None:` with
`from firestarter.frame_parser import Response` (already imported transitively).

### IN-03: New CLI message line exceeds 88 chars but is acceptable under project config

**File:** `firestarter_app/firestarter/cli_handlers.py:122`

**Issue:** The new "Unsupported protocol:" f-string is 117 characters. `cli_handlers.py`
is ruff-gated, but `extend-ignore = ["E501"]` is set in pyproject.toml (ruff-format owns
line length, and it does not split string literals), so this passes both `ruff check` and
`ruff format --check`. Recorded for completeness only — no action required unless a future
policy enables E501.

**Fix:** None required. If desired for readability, split the literal across implicitly
concatenated strings.

---

_Reviewed: 2026-06-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

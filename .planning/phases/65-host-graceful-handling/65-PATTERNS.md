# Phase 65: Host Graceful Handling - Pattern Map

**Mapped:** 2026-06-11
**Files analyzed:** 6 source files + tests
**Analogs found:** 6 / 6

## Line-Number Drift Report

CONTEXT.md cited line numbers vs. live code (all verified):

| Cited location | Actual location | Drift? |
|---|---|---|
| `frame_parser.py:17` Response namedtuple | line 17 | exact |
| `frame_parser.py:23` LogMessage namedtuple | line 22 | -1 line |
| `serial_comm.py:394` decoded→Response | lines 393-397 | -1 line (block starts 393) |
| `serial_comm.py:222` text-prefix Response | line 222 | exact |
| `serial_comm.py:225` second text-prefix | line 225 | exact |
| `eprom_operations.py:316-323` outer except | lines 318-323 | +2 lines |
| `eprom_operations.py:338-341` _execute_phase raise | lines 339-342 | +1 line |
| `eprom_operations.py:374-376` _main_phase_simple raise | lines 375-376 | +1 line |
| `cli_handlers.py:31-37` exceptions import | lines 34-41 | +3 lines |
| `cli_handlers.py:106-124` map_typed_errors | lines 106-124 | exact |
| `cli_handlers.py:119` EpromOperationError arm | line 119 | exact |
| `messages.py:111` MSG_ERR_PROTOCOL_NOT_IMPLEMENTED | line 111 | exact |
| `messages.py:644-651` 0xBB MessageDef | lines 644-652 | exact |

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `firestarter/exceptions.py` | exception hierarchy | — | same file (extend) | exact |
| `firestarter/frame_parser.py` | wire primitive | request-response | same file (extend) | exact |
| `firestarter/serial_comm.py` | serial transport | request-response | same file (extend) | exact |
| `firestarter/eprom_operations.py` | service / state machine | request-response | same file (extend) | exact |
| `firestarter/cli_handlers.py` | CLI handler / decorator | request-response | same file (extend) | exact |
| `tests/test_phase65_*.py` (new) | test | request-response | `tests/test_bug_characterization.py` + `tests/test_cli_handlers.py` | role-match |

---

## Pattern Assignments

### `firestarter/exceptions.py` — add `ProtocolNotImplementedError`

**Pattern:** bare `pass`-body subclass with a docstring, adjacent to its parent.

**Current hierarchy** (lines 37-46):
```python
class EpromOperationError(Exception):
    """Custom exception for EPROM operation failures."""

    pass


class HardwareOperationError(Exception):
    """Custom exception for hardware operation failures."""

    pass
```

**Existing sibling subclass example** — `SerialTimeoutError(SerialError)` (lines 19-22):
```python
class SerialTimeoutError(SerialError):
    """Custom exception for serial timeouts."""

    pass
```

**New class to insert immediately after `EpromOperationError`** (copy this shape):
```python
class ProtocolNotImplementedError(EpromOperationError):
    """Raised when firmware reports a protocol is not yet implemented (id 0xBB)."""

    pass
```

No `__init__` override — all existing subclasses are bare `pass`. No `__init__`
args needed; the message string is supplied at the raise site as positional arg
to `Exception`.

---

### `firestarter/frame_parser.py` — add `id` field to `Response`

**Current `Response` definition** (line 17):
```python
Response = namedtuple("Response", ["type", "message", "payload"], defaults=[None])
```

**Precedent for `defaults`:** `payload=None` was appended in W-04 with `defaults=[None]`
(one trailing default covers the last field). Adding `id=None` extends the same
pattern to two trailing defaults.

**Current `LogMessage` definition** (lines 22-24) — source of the `id` value:
```python
LogMessage = namedtuple(
    "LogMessage", ["severity", "text", "id", "payload"], defaults=[None]
)
```

**New `Response` definition** (extend, do not replace):
```python
Response = namedtuple("Response", ["type", "message", "payload", "id"], defaults=[None, None])
```

`defaults` list maps right-to-left: `payload` and `id` both default to `None`.
All existing `Response(type=..., message=...)` keyword callers are unaffected.
All positional callers (none found — confirmed by grep below) are also safe.

**Positional-caller check** — the two text-prefix construction sites
(`serial_comm.py:222` and `:225`) both use keyword args:
```python
return Response(type=match.group(1), message=match.group(2).strip())
# and
return Response(type=None, message=line_str)
```
No positional `Response(...)` callers exist. New field append is safe.

---

### `firestarter/serial_comm.py` — thread `id` from `LogMessage` into `Response`

**Text-prefix path** (lines 220-225) — NOT changed; relies on `id=None` default:
```python
matches = list(PREFIX_REGEX.finditer(line_str))
if matches:
    match = matches[-1]
    return Response(type=match.group(1), message=match.group(2).strip())

# No known prefix found, return the raw line as a message with no type
return Response(type=None, message=line_str)
```

**ID-frame decode path** (lines 389-399) — the only change site; add `id=decoded.id`:
```python
decoded = self._decode_id_frame(frame_len, body)
if decoded is not None:
    # Propagate raw-bytes payload for MSG_DATA_CHUNK (W-04);
    # Response.payload is None for all other message types.
    response = Response(
        type=decoded.severity,
        message=decoded.text,
        payload=decoded.payload,
    )
    self._log_rurp_feedback(response)
    yield response
```

**After edit** (only the `Response(...)` construction changes):
```python
    response = Response(
        type=decoded.severity,
        message=decoded.text,
        payload=decoded.payload,
        id=decoded.id,
    )
```

---

### `firestarter/eprom_operations.py` — introduce `_raise_for_error_response` helper

**Outer `except EpromOperationError` catch in `_run_state_machine`** (lines 318-323):
```python
except EpromOperationError as e:
    logger.error(f"Programmer error during {operation_name}: {e}")
    return False, str(e)
```

**ERROR raise in `_execute_phase`** (lines 339-342):
```python
if response.type == "ERROR":
    raise EpromOperationError(
        f"Programmer error during {phase_name.lower()}: {response.message}"
    )
```

**ERROR raise in `_main_phase_simple`** (lines 375-376):
```python
if response.type == "ERROR":
    raise EpromOperationError(response.message)
```

**Discretion pattern — shared helper** (CONTEXT.md Discretion block):

Both raise sites call `EpromOperationError` directly. The planner should
introduce a small module-level helper that both ERROR branches delegate to:

```python
def _raise_for_error_response(response) -> None:
    """Raise ProtocolNotImplementedError for id 0xBB, EpromOperationError otherwise."""
    from firestarter.messages import MSG_ERR_PROTOCOL_NOT_IMPLEMENTED
    if response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED:
        raise ProtocolNotImplementedError(response.message)
    raise EpromOperationError(response.message)
```

Then each `if response.type == "ERROR":` block replaces its `raise EpromOperationError(...)`
with `_raise_for_error_response(response)` (the `_execute_phase` site may still
prepend the phase-name prefix to `response.message` before passing — planner
decides whether to keep the prefix or incorporate it differently).

**Import addition needed** at the top of `eprom_operations.py`:
```python
from firestarter.exceptions import EpromOperationError, ProtocolNotImplementedError
```
(check current import block — `EpromOperationError` is already imported; add
`ProtocolNotImplementedError` alongside it)

---

### `firestarter/cli_handlers.py` — add `ProtocolNotImplementedError` arm to `map_typed_errors`

**Current exceptions import block** (lines 34-41):
```python
from firestarter.exceptions import (
    ChipNotFoundError,
    EpromOperationError,
    FirmwareOutdatedError,
    HardwareOperationError,
    SerialError,
    SerialTimeoutError,
)
```

Add `ProtocolNotImplementedError` to this block (alphabetically between
`HardwareOperationError` and `SerialError`, or appended — ruff/isort decides).

**Current `map_typed_errors` body** (lines 106-124) — full excerpt:
```python
def map_typed_errors(f: Callable[..., Any]) -> Callable[..., Any]:
    """Map service-layer typed exceptions to ClickException + stable exit codes (D-03)."""

    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except ChipNotFoundError as e:
            raise click.ClickException(str(e)) from e
        except FirmwareOutdatedError as e:
            raise click.ClickException(f"Firmware outdated: {e}") from e
        except (SerialError, SerialTimeoutError) as e:
            raise click.ClickException(f"Communication error: {e}") from e
        except EpromOperationError as e:
            raise click.ClickException(f"Programmer error: {e}") from e
        except HardwareOperationError as e:
            raise click.ClickException(f"Hardware error: {e}") from e

    return wrapper
```

**New arm placement** — insert BEFORE the `EpromOperationError` arm (line 119),
AFTER the `SerialError` arm (line 118). Copy the `f"<prefix>: {e}"` shape:

```python
        except ProtocolNotImplementedError as e:
            raise click.ClickException(
                f"Unsupported protocol: {e} — this protocol is recognized but not yet implemented in the firmware."
            ) from e
        except EpromOperationError as e:
            raise click.ClickException(f"Programmer error: {e}") from e
```

**Ordering rule (SC#4):** subclass arm (`ProtocolNotImplementedError`) MUST
appear before base class arm (`EpromOperationError`) — Python `except` matches
first-wins.

---

### `firestarter/messages.py` — reference only (no edit)

`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` confirmed at line 111.

`0xBB` MessageDef confirmed at lines 644-652:
```python
0xBB: MessageDef(
    id=0xBB,
    name="MSG_ERR_PROTOCOL_NOT_IMPLEMENTED",
    severity=SEVERITY_ERROR,
    format="Protocol 0x%02x not implemented",
    params=(("u8", "hex_byte"),),
    param_bytes=1,
    wire_format="id_frame",
),
```

The rendered host text is `"Protocol 0x0b not implemented"` (firmware substitutes
the u8 protocol value). Import `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` from
`firestarter.messages` — do NOT hardcode `0xBB` at the raise site.

---

## Tests: Conventions and Fixtures

**Test file placement:** new file `tests/test_protocol_not_implemented.py`
(matches per-feature file naming: `test_bug_characterization.py`,
`test_fwguard.py`, etc.).

**Fixture pattern for wiring fake serial** (from `conftest.py` + `test_eprom_operations.py`):
```python
# conftest.py provides: fake_serial, make_comm, build_frame
from .conftest import build_frame

def test_something(make_comm, fake_serial):
    from firestarter.config import ConfigManager
    from firestarter.eprom_operations import EpromOperator

    config = ConfigManager()
    operator = EpromOperator(config)
    operator.comm = make_comm()

    fake_serial.feed(build_frame(MSG_ID, b""))  # inject wire frame

    ok, msg = operator._run_state_machine("op_name")
    # assert on ok, msg, or captured exception
```

**Pattern for feeding a 0xBB frame with a u8 param** (`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`
has `params=(("u8","hex_byte"),)`, `param_bytes=1`):
```python
from firestarter.messages import MSG_ERR_PROTOCOL_NOT_IMPLEMENTED
protocol_value = 0x0B  # example: whatever protocol the firmware rejected
fake_serial.feed(build_frame(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, bytes([protocol_value])))
```

**Pattern for testing typed raise** (from `test_bug_characterization.py` lines 99-123):
```python
import pytest
with pytest.raises(ProtocolNotImplementedError):
    operator._run_state_machine("test_op")
```

**Pattern for testing CLI message via CliRunner** (from `test_cli_handlers.py` lines 40-73):
```python
from click.testing import CliRunner
from unittest.mock import Mock
from firestarter.cli_handlers import AppContext, cli
from firestarter.eprom_operations import EpromOperator

def make_app_context(**overrides) -> AppContext:
    # ... (copy from test_cli_handlers.py:40-73)

def test_cli_message(runner):
    operator = Mock(spec=EpromOperator)
    operator.read_eprom.side_effect = ProtocolNotImplementedError(
        "Protocol 0x0b not implemented"
    )
    app = make_app_context(eprom_operator=operator)
    result = runner.invoke(cli, ["read", "W27C512", "out.bin"], obj=app)
    assert result.exit_code == 1
    assert "Protocol 0x0b not implemented" in result.output
    assert "Unsupported protocol" in result.output
```

**Subclass test** (pure Python, no fixtures):
```python
def test_protocol_not_implemented_is_eprom_operation_error():
    assert issubclass(ProtocolNotImplementedError, EpromOperationError)
```

**Catch-ordering test** (verify subclass arm fires before base class arm):
```python
def test_map_typed_errors_ordering():
    """A ProtocolNotImplementedError must NOT be caught by EpromOperationError arm."""
    operator = Mock(spec=EpromOperator)
    operator.read_eprom.side_effect = ProtocolNotImplementedError("Protocol 0x0b not implemented")
    app = make_app_context(eprom_operator=operator)
    result = runner.invoke(cli, ["read", "W27C512", "out.bin"], obj=app)
    assert "Unsupported protocol" in result.output
    assert "Programmer error" not in result.output
```

---

## Shared Patterns

### Exception subclass definition
**Source:** `firestarter/exceptions.py` lines 19-22 (`SerialTimeoutError`) and lines 37-40 (`EpromOperationError`)
**Apply to:** new `ProtocolNotImplementedError`
Pattern: `class XxxError(ParentError):\n    """Docstring."""\n\n    pass`

### `map_typed_errors` subclass-before-base ordering
**Source:** `firestarter/cli_handlers.py` lines 113-122
**Apply to:** new `ProtocolNotImplementedError` arm
Python `except` is first-match; subclass arm MUST precede its base class arm.

### `click.ClickException` message shape
**Source:** `firestarter/cli_handlers.py` lines 116-122
**Apply to:** new arm
Pattern: `raise click.ClickException(f"<Prefix>: {e}") from e`
New prefix must be visibly distinct from `"Programmer error:"`.

### Constant import (not hardcode)
**Source:** `firestarter/eprom_operations.py` (existing pattern — imports constants from `firestarter.messages`)
**Apply to:** `_raise_for_error_response` helper
Import `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` from `firestarter.messages`; do not use literal `0xBB`.

### Wire-frame injection in tests
**Source:** `tests/conftest.py` `build_frame` + `fake_serial.feed`
**Apply to:** new test file
`build_frame(msg_id, params_bytes)` assembles a complete wire frame; `fake_serial.feed(frame)` injects it before calling the method under test.

---

## No Analog Found

None — all files have direct analogs or are being extended in-place.

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tests/`
**Files scanned:** 9 source/test files
**Pattern extraction date:** 2026-06-11

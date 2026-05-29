# Phase 38: Low-Risk Extractions - Pattern Map

**Mapped:** 2026-05-27
**Files analyzed:** 10 (4 new source modules, 2 new test modules, 4 modified source modules)
**Analogs found:** 10 / 10

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/exceptions.py` | model (exception hierarchy) | n/a (pure definitions) | `firestarter/avr_tool.py` (exception defs) + `serial_comm.py:188-209` (source classes) | exact |
| `firestarter/frame_parser.py` | utility (pure compute) | transform | `firestarter/utils.py` (pure-function leaf, stdlib only) + `serial_comm.py:47-139` (source symbols) | role-match + source |
| `firestarter/codec.py` | utility (message render) | transform | `firestarter/messages.py` (pure data/format leaf) + `serial_comm.py:177-185,341-450` (source symbols) | role-match + source |
| `firestarter/address_parser.py` | utility (pure compute) | transform | `firestarter/utils.py` (pure-function leaf, stdlib only) | exact role-match |
| `firestarter/serial_comm.py` (modified) | service | request-response | itself — only import block and re-export idiom change | self-analog |
| `firestarter/eprom_operations.py` (modified) | service | CRUD | itself — import repoint + try/except wrapper + globals() fix | self-analog |
| `firestarter/firmware.py` (modified) | service | CRUD | itself — one import repoint only | self-analog |
| `firestarter/hardware.py` (modified) | service | CRUD | itself — one import repoint only | self-analog |
| `tests/test_codec.py` | test | transform | `tests/test_revision_constants_parity.py` + `tests/test_decoder.py` | role-match |
| `tests/test_address_parser.py` | test | transform | `tests/test_revision_constants_parity.py` (pure-unit, no fixtures) | exact role-match |

---

## Pattern Assignments

### `firestarter/exceptions.py` (model, pure definitions)

**Primary source:** `firestarter/serial_comm.py` lines 188–209 (6 existing classes being moved)
**Secondary source:** `firestarter/firmware.py` line 63 (`FirmwareOperationError`)
**Style analog:** `firestarter/avr_tool.py` lines 1–26 (file header + short class definitions)

**File header pattern** (`avr_tool.py` lines 1–9):
```python
"""
Project Name: Firestarter
Copyright (c) 2025 Henrik Olsson

Permission is hereby granted under MIT license.
AVRdude Tool Wrapper Module
"""
```

**Exception class style** (`serial_comm.py` lines 188–209 — the EXACT code being moved):
```python
class SerialError(Exception):
    """Custom exception for serial communication errors."""

    pass


class SerialTimeoutError(SerialError):
    """Custom exception for serial timeouts."""

    pass


class ProgrammerNotFoundError(SerialError):
    """Custom exception when no programmer is found."""

    pass


class FirmwareOutdatedError(SerialError):
    """Custom exception for outdated firmware."""

    pass
```

**Avr_tool one-liner alternative style** (`avr_tool.py` lines 22–25):
```python
class AvrdudeNotFoundError(FileNotFoundError): ...

class AvrdudeConfigNotFoundError(FileNotFoundError): ...
```
**Do NOT use this style** — the existing exception classes use the multi-line `pass` body
with a docstring. Match the `serial_comm.py` style exactly for the 6 moved classes.
`ChipNotFoundError` (new stub) follows the same pattern as `EpromOperationError` /
`HardwareOperationError` (direct `Exception` subclass with docstring + `pass`).

**Import block** — `exceptions.py` imports NOTHING from the package. No stdlib imports
needed either (all classes are plain `class Foo(Exception): pass` or subclass another
class in the same file). The file has NO import block at all, or at most `from __future__`
if ruff's UP rules require it (they don't here).

**Key rules:**
- Inheritance preserved exactly: `SerialTimeoutError(SerialError)`, `ProgrammerNotFoundError(SerialError)`, `FirmwareOutdatedError(SerialError)` subclass `SerialError`; the rest subclass `Exception` directly.
- No `__all__` — none of the existing modules use `__all__`.
- Class order: SerialError first (dependency), then its three subclasses, then the three independent classes (`EpromOperationError`, `HardwareOperationError`, `FirmwareOperationError`), then `ChipNotFoundError` last (new stub).

---

### `firestarter/frame_parser.py` (utility, transform)

**Primary source:** `firestarter/serial_comm.py` lines 47–139 (exact symbols being moved)
**Style analog for file header + docstring:** `firestarter/utils.py` (pure-function stdlib-only leaf)

**File header pattern** (copy from `utils.py` lines 1–9, adapt module name):
```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Wire-frame primitives: CRC8-CCITT, parameter decoding, and structured
response types. Stdlib + typing only — no package-internal imports.
"""
```

**Import block** — stdlib only, matching what the moved symbols actually use
(`serial_comm.py` lines 1–19 for reference, but filter to only what frame_parser needs):
```python
import struct
from collections import namedtuple
from typing import Any, Tuple  # noqa: UP035
```

**Core pattern — exact symbols moved** (`serial_comm.py` lines 47–139):
```python
Response = namedtuple("Response", ["type", "message", "payload"], defaults=[None])

LogMessage = namedtuple(
    "LogMessage", ["severity", "text", "id", "payload"], defaults=[None]
)
MAGIC_PREAMBLE: bytes = b"\xaa\x55\xaa\x55"


def _build_crc8_table() -> bytes:
    """Precompute the 256-byte CRC8-CCITT lookup table. ..."""
    ...  # copy body verbatim


_CRC8_CCITT_TABLE: bytes = _build_crc8_table()


def _crc8_ccitt(data: bytes) -> int:
    """Compute CRC8-CCITT (poly 0x07, seed 0x00) over `data` via lookup table."""
    ...  # copy body verbatim


def _decode_param(ptype: str, buf: bytes, cursor: int) -> Tuple[Any, int]:  # noqa: UP006
    """Decode one MSB-first parameter starting at `buf[cursor]`. ..."""
    ...  # copy body verbatim — includes struct.unpack_from calls
```

**Re-export requirement in `serial_comm.py`** (RESEARCH landmine — must be added
in the SAME commit that removes originals, before test suite runs):
```python
# Re-exports for backward compatibility — test_decoder.py imports these
# from firestarter.serial_comm (SC#2 / D-07: test_decoder.py passes unchanged).
from firestarter.frame_parser import (  # noqa: F401
    MAGIC_PREAMBLE,
    LogMessage,
    Response,
    _crc8_ccitt,
)
```

**Key rules:**
- Keep all `_` (private) prefixes on `_build_crc8_table`, `_CRC8_CCITT_TABLE`, `_crc8_ccitt`, `_decode_param` — SC#2 lists them with underscore.
- Copy docstrings verbatim — the `_decode_param` docstring documents the WR-04 bounds-check rationale and must migrate with the function.
- `noqa: UP006` on the `Tuple` annotation (ruff UP035 would fire on Python 3.9+ style; this matches the existing annotation in `serial_comm.py` line 88).

---

### `firestarter/codec.py` (utility, transform)

**Primary source:** `firestarter/serial_comm.py` lines 177–185 (`_REVISION_SILKSCREEN`) and lines 341–450 (`_format_message`)
**Style analog:** `firestarter/messages.py` (pure data/format leaf — file header, import ordering, no package-internal `from firestarter` in messages.py; codec.py DOES have package imports but they are cycle-safe)

**File header pattern** (adapt from `messages.py` lines 1–15):
```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Message rendering: sentinel-aware format_message function and
hardware-revision silkscreen table.
"""
```

**Import block** — three imports (RESEARCH correction to D-08: codec needs `struct` +
`frame_parser._decode_param` in addition to `constants` + `messages`):
```python
import struct
from firestarter.constants import (
    COMMAND_NAMES,
    REVISION_0,
    REVISION_1,
    REVISION_2_0,
    REVISION_2_1,
    REVISION_2_2,
    REVISION_2_3,
    REVISION_UNKNOWN,
)
from firestarter.frame_parser import _decode_param
from firestarter.messages import (
    CATALOG,
    DBG_CMD,
    DEBUG_CATALOG,
    MSG_DATA_CHUNK,
    MSG_DEBUG,
    MSG_INFO_CMD,
    MSG_INFO_HW,
    MSG_INFO_PHYSICAL_HW,
    MSG_OK_CFG,
    MSG_OK_REV,
    SEVERITY_LABEL,
)
```

Note: `SEVERITY_LABEL` is imported in the existing `serial_comm.py` import block but
may or may not be used by `format_message` — verify before including. Only import what
`format_message` and `_REVISION_SILKSCREEN` actually reference. `COMMAND_NAMES` is used
at lines 407 and 418 of `serial_comm.py`.

**`_REVISION_SILKSCREEN` pattern** (`serial_comm.py` lines 174–185 — EXACT code to move;
`noqa: F405` annotations migrate WITH the dict because `REVISION_*` are still star-imported
in the source, but in `codec.py` they become explicit named imports so the `# noqa: F405`
annotations are NO LONGER needed — drop them when writing codec.py):
```python
# Phase 34: REVISION_* byte → silkscreen-string mapping for MSG_OK_REV rendering.
# Mirrors firmware enum at firestarter/include/rurp_shield.h. Lookup-via-dict.get()
# so unknown bytes fall back to "Rev{n}" instead of raising.
_REVISION_SILKSCREEN = {
    REVISION_0: "Rev 0",
    REVISION_1: "Rev 1",
    REVISION_2_0: "Rev 2.0-class",  # broad bucket per Phase 34 D-04
    REVISION_2_1: "Rev 2.1 (override)",
    REVISION_2_2: "Rev 2.2 (override)",
    REVISION_2_3: "Rev 2.3",
    REVISION_UNKNOWN: "rev_unknown",
}
```

**`format_message` function pattern** (renamed from `_format_message`; `self` parameter
dropped; `serial_comm.py` lines 341–450 are the body — copy verbatim except):
- Remove `self` from signature: `def format_message(msg_id: int, params: list, entry) -> Optional[str]:`
- Add `from typing import Optional` to import block (already needed for return type).
- Replace any `self._format_message(...)` calls that appear in the body (none — the
  body calls `_decode_param` directly at line 428, which will be in scope via import).
- Migrate the Phase-35 WR-01/02 rationale comments verbatim (D-16 — these are live
  intent comments, NOT dead code).

**Call site repoint in `serial_comm.py`** (`_decode_id_frame` body at line ~530):
```python
# Before (serial_comm.py current):
text = self._format_message(msg_id, values, entry)

# After (serial_comm.py post-extraction):
import firestarter.codec as codec  # at top of file
text = codec.format_message(msg_id, values, entry)
```

**Key rules:**
- `format_message` is PUBLIC (no leading `_`) — this is the SC#3-mandated rename.
- `_REVISION_SILKSCREEN` keeps its `_` (private) — it is an internal lookup table.
- No `SEVERITY_LABEL` import unless `format_message` body actually uses it (check line 341–450 carefully).
- Star-import `# noqa: F403/F405` suppressions in `serial_comm.py` that belonged to `_REVISION_SILKSCREEN` are gone once the dict moves; do NOT add them to `codec.py` (explicit imports used there).

---

### `firestarter/address_parser.py` (utility, transform)

**Style analog:** `firestarter/utils.py` (pure-function stdlib-only leaf — shortest existing
module; zero package-internal imports; plain function-per-concern layout)

**File header pattern** (adapt from `utils.py` lines 1–9):
```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Address and size string parsing utilities.
"""
```

**Import block** (stdlib only; `Optional` needed for `str | None` return annotation):
```python
from typing import Optional  # noqa: UP035
```

**Core pattern** (derived from `eprom_operations.py` lines 182–200 inline logic,
refactored to standalone functions per D-11):
```python
def parse_address(s: Optional[str]) -> Optional[int]:
    """Parse hex or decimal address string. Returns None for None input.
    Raises ValueError on bad format.
    """
    if s is None:
        return None
    return int(s, 16) if "0x" in s.lower() else int(s)


def parse_size(s: Optional[str]) -> Optional[int]:
    """Parse hex or decimal size string. Returns None for None input.
    Raises ValueError on bad format.
    """
    if s is None:
        return None
    return int(s, 16) if "0x" in s.lower() else int(s)
```

**Call site wrapper in `eprom_operations.py`** (replaces inline logic at lines 182–200;
preserves exact log strings per D-12, D-13):
```python
from firestarter.address_parser import parse_address, parse_size

# ... (inside _setup_operation):
addr = 0
if address:
    try:
        addr = parse_address(address)
        command_dict["address"] = addr  # KEY: only set when address provided
    except ValueError:
        logger.error(f"Invalid address format: {address}")
        return None, 0

if cmd == COMMAND_READ and size:
    try:
        read_size = parse_size(size)
        command_dict["memory-size"] = addr + read_size
    except ValueError:
        logger.error(f"Invalid size format: {size}")
        return None, 0
```

**Key rules:**
- `parse_address` and `parse_size` are PUBLIC (no leading `_`).
- The `Optional[str]` / `Optional[int]` annotations use `from typing import Optional` +
  `# noqa: UP035` to match the house style (ruff UP035 would suggest `str | None` syntax;
  existing modules suppress this for consistency with the established codebase).
- Do NOT consolidate into one function — two separate named functions are clearer and
  let tests target each independently.

---

### `firestarter/serial_comm.py` (modified — frame symbols removed + re-exports added + dead code deleted)

**Pattern:** self-analog — preserve all existing structure; only specific surgical edits.

**Import block ordering** (existing `serial_comm.py` lines 10–40 — preserve exactly,
add new imports at appropriate places):
```python
import functools
import json
import logging
import operator
import os
import re
import struct
import time
from collections import namedtuple
from typing import Any, Generator, List, Optional, Tuple  # noqa: UP035

import serial
import serial.serialutil
import serial.tools.list_ports

from firestarter.config import ConfigManager  # Assuming ConfigManager is refactored
from firestarter.constants import *  # noqa: F403
from firestarter.constants import COMMAND_NAMES
from firestarter.messages import (...)
```
After extraction: `namedtuple` import can be removed (no longer used in `serial_comm.py`
after `Response` and `LogMessage` move). `struct` import stays (used elsewhere in the
file). `from collections import namedtuple` drops out.

**Re-export block** (add immediately after the `from firestarter.messages import ...`
block — before any class/function definitions; precedes the re-exporting of `codec` import):
```python
import firestarter.codec as codec  # for _decode_id_frame call site
from firestarter.frame_parser import (  # noqa: F401
    MAGIC_PREAMBLE,
    LogMessage,
    Response,
    _crc8_ccitt,
)
```

**Dead code deletion** (`serial_comm.py` lines 991–end):
- Delete `read_data_block` method entirely (zero callers confirmed — D-14).
- No replacement needed; method body is ~75 lines (lines 991–1066).

**Re-export `# noqa: F401` idiom** — this is the only place in the codebase where
re-exports are done; the pattern matches ruff's convention: one `# noqa: F401` on the
import line or on the `from ... import (` opening line covers all names in a parenthesized
import block. Safest: put `# noqa: F401` on the opening line:
```python
from firestarter.frame_parser import (  # noqa: F401
    MAGIC_PREAMBLE,
    LogMessage,
    Response,
    _crc8_ccitt,
)
```

---

### `firestarter/eprom_operations.py` (modified — exception repoint + address parser + globals() fix)

**Import block pattern** (existing lines 10–34 — surgical additions only):
```python
# Add to existing imports:
from firestarter.address_parser import parse_address, parse_size
from firestarter.exceptions import EpromOperationError  # replaces local class def

# Remove:
# (the local class EpromOperationError at line 84)

# Existing star-import STAYS — do not touch:
from firestarter.constants import *  # noqa: F403

# Existing serial_comm imports CHANGE to pull from exceptions instead:
from firestarter.exceptions import (
    ProgrammerNotFoundError,
    SerialError,
    SerialTimeoutError,
)
from firestarter.serial_comm import SerialCommunicator  # SerialCommunicator stays here
```

**globals() replacement pattern** (lines 170 and 232):
```python
# Before (line 170):
operation = [k for k, v in globals().items() if v == cmd][0].replace("COMMAND_", "")

# After:
operation = COMMAND_NAMES[cmd]  # COMMAND_NAMES already imported via star-import

# Before (line 232):
operation_name = [k for k, v in globals().items() if v == cmd][0].replace("COMMAND_", "")

# After:
operation_name = COMMAND_NAMES[cmd]
```

---

### `firestarter/firmware.py` (modified — one import repoint)

**Import block change** (existing lines 29–34):
```python
# Before:
from firestarter.serial_comm import (
    FirmwareOutdatedError,
    ProgrammerNotFoundError,
    SerialCommunicator,
    SerialError,
)

# After:
from firestarter.exceptions import (
    FirmwareOperationError,  # now moved from local def at line 63
    FirmwareOutdatedError,
    ProgrammerNotFoundError,
    SerialError,
)
from firestarter.serial_comm import SerialCommunicator
```
And delete the local `FirmwareOperationError` class at line 63.

---

### `firestarter/hardware.py` (modified — one import repoint)

**Import block change** (existing lines 15–20):
```python
# Before:
from firestarter.serial_comm import (
    ProgrammerNotFoundError,
    SerialCommunicator,
    SerialError,
    SerialTimeoutError,
)

# After:
from firestarter.exceptions import (
    HardwareOperationError,  # now moved from local def at line 25
    ProgrammerNotFoundError,
    SerialError,
    SerialTimeoutError,
)
from firestarter.serial_comm import SerialCommunicator
```
And delete the local `HardwareOperationError` class at line 25.

---

### `tests/test_codec.py` (new test — pure-unit, no serial fixtures)

**Style analog:** `tests/test_revision_constants_parity.py` (pure-unit assertions, no
fixtures, class-per-concern layout) + `tests/test_decoder.py` (file header style,
messages imports)

**File header pattern** (`test_decoder.py` lines 1–22 adapted):
```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 38 — codec.format_message unit tests (STRUCT-02).

Covers all catalog message shapes handled by the sentinel-aware renderer:
MSG_OK_REV, MSG_OK_CFG, MSG_INFO_HW, MSG_INFO_PHYSICAL_HW, MSG_INFO_CMD,
MSG_DEBUG (DBG_CMD), MSG_DATA_CHUNK, and the None fall-through path.

Tests import directly from firestarter.codec — no SerialCommunicator instance
or serial fixtures needed.
"""
```

**Import pattern** (no conftest fixtures; direct module imports):
```python
import pytest  # noqa: F401

from firestarter.codec import format_message
from firestarter.messages import (
    CATALOG,
    DBG_CMD,
    MSG_DATA_CHUNK,
    MSG_DEBUG,
    MSG_INFO_CMD,
    MSG_INFO_HW,
    MSG_INFO_PHYSICAL_HW,
    MSG_OK_CFG,
    MSG_OK_REV,
)
```

**Test class structure** (`test_eprom_database.py` lines 31–60 as layout reference —
one class per functional concern, `def test_*` methods inside):
```python
class TestFormatMessageRevision:
    """MSG_OK_REV / MSG_OK_CFG / MSG_INFO_HW / MSG_INFO_PHYSICAL_HW rendering."""

    def test_msg_ok_rev_no_override(self):
        """MSG_OK_REV: effective==0xFF → physical silkscreen string only."""
        entry = CATALOG[MSG_OK_REV]
        result = format_message(MSG_OK_REV, [0x00, 0xFF], entry)
        assert result == "Rev 0"

    def test_msg_ok_rev_with_override(self):
        """MSG_OK_REV: effective!=0xFF → 'Rev{eff}, Override HW: Rev{phys}'."""
        entry = CATALOG[MSG_OK_REV]
        result = format_message(MSG_OK_REV, [0x02, 0x04], entry)
        assert result == "Rev 2.2 (override), Override HW: Rev 2.0-class"

    # ... (remaining tests per RESEARCH §tests/test_codec.py table)


class TestFormatMessageDebugChunk:
    """MSG_DEBUG (DBG_CMD) and MSG_DATA_CHUNK rendering."""

    def test_msg_debug_dbg_cmd(self):
        """MSG_DEBUG + DBG_CMD sub-id → 'Cmd: 0x{n} (NAME)'."""
        entry = CATALOG[MSG_DEBUG]
        result = format_message(MSG_DEBUG, [DBG_CMD, bytes([0x02])], entry)
        assert result == "Cmd: 0x02 (WRITE)"

    def test_msg_data_chunk_summary(self):
        """MSG_DATA_CHUNK → '<chunk: N bytes>' summary (not raw dump)."""
        entry = CATALOG[MSG_DATA_CHUNK]
        result = format_message(MSG_DATA_CHUNK, [b"\x00" * 512], entry)
        assert result == "<chunk: 512 bytes>"


class TestFormatMessageNoneSentinel:
    """Unknown/unhandled IDs return None (fall-through to generic rendering)."""

    def test_none_for_unknown_id(self):
        """Unknown msg_id returns None."""
        entry = CATALOG[MSG_OK_REV]  # arbitrary valid entry
        result = format_message(0x99, [], entry)
        assert result is None
```

**Key rules:**
- No `fake_serial`, `make_comm`, or `build_frame` fixtures needed — `format_message` takes plain Python objects.
- Use `CATALOG[MSG_*]` to get the `entry` arg — tests are self-contained without serial plumbing.
- `pytest.raises` is NOT needed (no expected exceptions in format_message tests).
- Class-per-concern grouping matches the `test_eprom_database.py` and `test_decoder.py` pattern.

---

### `tests/test_address_parser.py` (new test — pure-unit, `pytest.raises` for errors)

**Style analog:** `tests/test_revision_constants_parity.py` (pure assertions) +
`tests/test_eprom_database.py` (class grouping pattern)

**File header pattern**:
```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 38 — address_parser unit tests (STRUCT-03).

Covers parse_address and parse_size: hex (0x prefix), decimal, None input,
and invalid inputs that must raise ValueError.
"""
```

**Import pattern**:
```python
import pytest

from firestarter.address_parser import parse_address, parse_size
```

**Test class structure** (covers all inputs from RESEARCH §tests/test_address_parser.py table):
```python
class TestParseAddress:
    def test_hex_0x_prefix(self):
        assert parse_address("0x10000") == 65536

    def test_hex_uppercase_prefix(self):
        assert parse_address("0X1A2B") == 6699

    def test_decimal(self):
        assert parse_address("512") == 512

    def test_none_input(self):
        assert parse_address(None) is None

    def test_invalid_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_address("not_a_number")

    def test_empty_string_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_address("")


class TestParseSize:
    def test_hex(self):
        assert parse_size("0x8000") == 32768

    def test_decimal(self):
        assert parse_size("1024") == 1024

    def test_none_input(self):
        assert parse_size(None) is None

    def test_invalid_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_size("abc")
```

**Key rules:**
- `pytest.raises(ValueError)` is the standard pattern for exception testing — used in existing `tests/test_characterization.py` and the RESEARCH §test_address_parser.py table.
- No fixtures required — pure stdlib input/output.
- One class per function under test (`TestParseAddress`, `TestParseSize`).

---

## Shared Patterns

### File Header (ALL new files)

**Source:** `firestarter/utils.py` lines 1–9 (shortest clean example) and `firestarter/serial_comm.py` lines 1–8 (main module example)

All new source files use this 7-line header block:
```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

{Module description — one sentence.}
"""
```
Copyright year: use 2024 for consistency with the majority of existing files.

### Typing Annotations Convention

**Source:** `serial_comm.py` line 19, `eprom_operations.py` line 20, `hardware.py` line 11

All existing files use `from typing import Optional, Tuple, ...` (pre-3.10 style) with
`# noqa: UP035` to suppress ruff's "use `X | Y` syntax" suggestions:
```python
from typing import Any, Optional, Tuple  # noqa: UP035
```
New files must follow the same pattern. Do NOT switch to `X | Y` union syntax — that
would introduce noise vs. the established watermark and could increase mypy errors.

### Import Ordering (ruff isort)

**Source:** all existing modules — stdlib first, then third-party, then local package.
Within each group, alphabetical order (enforced by ruff's isort). Example from
`serial_comm.py` lines 10–40:
```
stdlib → [blank line] → third-party (serial, etc.) → [blank line] → firestarter.*
```
For pure-stdlib new modules (`exceptions.py`, `frame_parser.py`, `address_parser.py`):
only the stdlib block; no blank lines after it if there are no other import groups.

### `# noqa` Annotation Pattern

**Source:** `serial_comm.py` lines 19, 26, 405, etc.

Three classes of `# noqa` annotations in use:
- `# noqa: F401` — re-exported imports that look unused to ruff
- `# noqa: F403` / `# noqa: F405` — star-import related (STAY in `serial_comm.py` and `eprom_operations.py` until Phase 39)
- `# noqa: UP035` — `from typing import` legacy style

New files only need `# noqa: UP035` on typing imports. Do NOT add F403/F405 to new
files (no star-imports in new files).

### Exception Raise Style

**Source:** `serial_comm.py` lines 251, 258, 265, etc.

All existing raise sites use bare `raise ExceptionClass(message)` — no chaining, no
`from` clause. Preserve this style at all repointed call sites.

### Logger Pattern

**Source:** all existing modules — per-file logger named after the class/module role:
```python
logger = logging.getLogger("EpromOperator")   # eprom_operations.py
logger = logging.getLogger("Hardware")         # hardware.py
logger = logging.getLogger("Firmware")         # firmware.py
```
New source modules that have logging: follow this pattern. `exceptions.py`,
`frame_parser.py`, `address_parser.py`, and `codec.py` do NOT need loggers (pure
compute, no I/O).

---

## No Analog Found

No files in this phase lack a codebase analog. All 4 new source modules have clear
source sites (symbols being moved) plus style analogs (closest pure-function or
pure-data leaf modules). All 2 new test modules have clear structural analogs in the
test suite.

---

## Ordering Hazard Summary for Planner

The dependency-safe execution order (from RESEARCH) is:

1. Create `exceptions.py` + repoint ALL import/raise/except sites (single atomic commit)
2. Create `frame_parser.py` + add re-exports to `serial_comm.py` in the SAME commit
3. Run full suite (green gate) — BEFORE removing originals from `serial_comm.py`
4. Remove original symbols from `serial_comm.py` + add `import firestarter.codec as codec` (separate commit after step 3 passes)
5. Create `codec.py` (depends on frame_parser being importable)
6. Create `address_parser.py` + update `_setup_operation` call site (independent)
7. Dead-code sweep: delete `read_data_block`, fix both `globals()` sites (D-14, D-15, D-16)

Each step = one atomic commit with `python -m pytest --tb=short -q` green before proceeding.

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/` (16 source files) + `firestarter_app/tests/` (14 test files)
**Files read:** `serial_comm.py` (partial — lines 1–160, 165–215, 330–530), `messages.py` (complete), `eprom_operations.py` (lines 1–100), `hardware.py` (lines 1–50), `firmware.py` (lines 1–80), `constants.py` (lines 1–60), `utils.py` (complete), `avr_tool.py` (lines 1–35), `test_decoder.py` (lines 1–100), `conftest.py` (complete), `test_fwguard.py` (lines 1–60), `test_revision_constants_parity.py` (complete), `test_eprom_database.py` (lines 1–60)
**Pattern extraction date:** 2026-05-27

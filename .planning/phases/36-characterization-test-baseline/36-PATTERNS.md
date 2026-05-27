# Phase 36: Characterization Test Baseline - Pattern Map

**Mapped:** 2026-05-27
**Files analyzed:** 7 (4 new test files + 1 extended test + 1 production change + 1 config change)
**Analogs found:** 7 / 7

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/tests/test_characterization.py` | test | request-response (subprocess) + in-process | `firestarter_app/tests/test_decoder.py` | role-match |
| `firestarter_app/tests/test_serial_characterization.py` | test | streaming (generator) | `firestarter_app/tests/test_decoder.py` | exact |
| `firestarter_app/tests/test_eprom_database.py` | test | CRUD / transform | `firestarter_app/tests/test_decoder.py` | role-match |
| `firestarter_app/tests/test_bug_characterization.py` | test | in-process unit | `firestarter_app/tests/test_revision_constants_parity.py` | role-match |
| `firestarter_app/tests/test_revision_constants_parity.py` | test (extend) | cross-repo parity | `firestarter_app/tests/test_revision_constants_parity.py` | exact (self) |
| `firestarter_app/firestarter/database.py` | service / model | CRUD | `firestarter_app/firestarter/database.py` | exact (self-modify) |
| `firestarter_app/pyproject.toml` | config | — | `firestarter_app/pyproject.toml` | exact (self-modify) |

---

## Pattern Assignments

### `firestarter_app/tests/test_characterization.py` (test, request-response + in-process)

**Analog:** `firestarter_app/tests/test_decoder.py`

**Imports pattern** (lines 1–58 of test_decoder.py — module docstring + imports):
```python
"""
Phase 36 — CLI characterization golden suite.

TEST-01: subprocess black-box goldens for board-independent CLI surface
         (--help, all subcommands, DB-backed list/info/search, all usage errors).
TEST-01: in-process E2E happy-paths for read/write/verify/erase via
         make_comm/fake_serial fixtures with canned firmware responses.
"""
import re
import shutil
import subprocess

import pytest

from .conftest import build_frame  # for in-process happy-path frame assembly
```

**Subprocess helper pattern** (from RESEARCH.md Pattern 1 — verified live):
```python
FIRESTARTER = shutil.which("firestarter")

def normalize_output(s: str) -> str:
    """Scrub non-deterministic content before snapshot assertion."""
    s = re.sub(r"Firestarter version: [\d.a-zA-Z]+", "Firestarter version: <VERSION>", s)
    s = re.sub(r"/dev/tty\w+", "/dev/ttyXXX", s)
    s = re.sub(r"(?:/home|/workspaces|/tmp|/Users)/[^\s]+", "<PATH>", s)
    return s

def run_firestarter(*args: str) -> tuple[str, str, int]:
    r = subprocess.run([FIRESTARTER, *args], capture_output=True, text=True, timeout=10)
    return normalize_output(r.stdout), normalize_output(r.stderr), r.returncode
```

**Snapshot test pattern** (from RESEARCH.md Pattern 1 + Pattern 3):
```python
def test_help(snapshot):
    stdout, stderr, rc = run_firestarter("--help")
    assert rc == 0
    assert stdout == snapshot

def test_info_bad_chip(snapshot):
    stdout, stderr, rc = run_firestarter("info", "NOTACHIP")
    assert rc == 1
    assert stdout == snapshot
```

**In-process happy-path pattern** (from conftest.py make_comm + test_decoder.py usage):
```python
def test_read_happy_path(make_comm, fake_serial):
    comm = make_comm()
    # Feed the three-phase state machine ack sequence as id-frames
    fake_serial.feed(build_frame(MSG_OK_READY, b""))
    fake_serial.feed(build_frame(MSG_INIT_DONE, b""))
    # ... MAIN phase data chunks ...
    fake_serial.feed(build_frame(MSG_MAIN_DONE, b""))
    fake_serial.feed(build_frame(MSG_END_DONE, b""))
    # Call the operation function directly with injected comm
    ...
```

**Port auto-discovery neutralization** (from RESEARCH.md Pattern 7 — only for "no programmer found" paths):
```python
def test_no_programmer_found_error(monkeypatch):
    monkeypatch.setattr("serial.tools.list_ports.comports", lambda: [])
    # find_and_connect now raises ProgrammerNotFoundError
    ...
```

**Key constraint:** Do NOT use Click's `CliRunner` — the CLI is argparse today. Do NOT use subprocess for happy-path I/O tests (BytesIO cannot cross process boundary). Normalize ALL subprocess output before `== snapshot`.

---

### `firestarter_app/tests/test_serial_characterization.py` (test, streaming/generator)

**Analog:** `firestarter_app/tests/test_decoder.py` (exact match — same `make_comm`/`fake_serial` pattern, same `_read_and_parse_lines` generator surface)

**Imports pattern** (mirror test_decoder.py lines 1–57):
```python
"""
Phase 36 — Serial frame-parse characterization suite (TEST-02).

Pins _read_and_parse_lines preamble→body→terminator sequence and the
sliding-window timeout-reset invariant. _read_and_parse_lines is
RING-FENCED for v1.9 RCA (GATE-1.8d) — tests observe only via
get_response() and external generator yields. Do NOT modify serial_comm.py.
"""
import time

import pytest

from firestarter.serial_comm import SerialTimeoutError
from .conftest import build_frame
```

**Generator driver pattern** (from test_decoder.py lines 60–67 — the `_drive_one_response` helper):
```python
def _drive_one_response(comm, timeout: float = 1.0):
    """Pull exactly one Response off the read loop, returning None on timeout."""
    gen = comm._read_and_parse_lines(timeout=timeout)
    try:
        return next(gen)
    except StopIteration:
        return None
```

**Timeout test pattern** (from RESEARCH.md Pattern 5 — experimentally verified: ~21 ms):
```python
def test_timeout_raises_on_empty(make_comm, fake_serial):
    comm = make_comm()
    # No data fed — get_response should raise SerialTimeoutError quickly
    start = time.time()
    with pytest.raises(SerialTimeoutError):
        comm.get_response(timeout=0.02)
    assert time.time() - start < 0.5  # completes in << 0.5 s

def test_sliding_window_resets_on_yield(make_comm, fake_serial):
    """Invariant: each yield of _read_and_parse_lines resets the timeout window."""
    comm = make_comm()
    from firestarter.messages import MSG_OK_READY
    fake_serial.feed(build_frame(MSG_OK_READY, b""))

    results = []
    for r in comm._read_and_parse_lines(0.05):
        results.append(r)
        if r.message == "Ready":
            fake_serial.feed(build_frame(MSG_OK_READY, b""))  # feed second after first yield
        if len(results) >= 2:
            break

    assert len(results) == 2  # both yielded; window reset after first
```

**Frame sequence pin pattern** (copy from test_decoder.py TestIdFrameDecoder structure):
```python
class TestSerialFrameParse:
    def test_preamble_body_terminator_sequence(self, fake_serial, make_comm):
        """Pin: INIT→MAIN→END ack sequence flows through _read_and_parse_lines."""
        comm = make_comm()
        # ... feed the three ack frames, assert each Response.type in order
```

**Ring-fence constraint:** Tests access `_read_and_parse_lines` only via `get_response()` or the generator's public yield surface. Do NOT inspect or modify any line of `serial_comm.py`.

---

### `firestarter_app/tests/test_eprom_database.py` (test, CRUD/transform)

**Analog:** `firestarter_app/tests/test_decoder.py` (role-match — same project, same fixture-driven in-process style)

**Imports pattern:**
```python
"""
Phase 36 — EpromDatabase unit tests (TEST-03).

Tests use EpromDatabase(skip_local_override=True) to pin against the
packaged chip_database.json only, ignoring ~/.firestarter/database.json.
This is the production change introduced in Phase 36: the singleton guard
is removed and skip_local_override is added (D-06).
"""
import pytest

from firestarter.database import EpromDatabase
```

**De-singleton constructor seam** (from RESEARCH.md Pattern 6):
```python
def test_get_eprom_w27c512():
    db = EpromDatabase(skip_local_override=True)
    eprom = db.get_eprom("W27C512")
    assert eprom is not None
    assert eprom["memory_size"] == 65536  # 64KB

def test_convert_to_programmer():
    db = EpromDatabase(skip_local_override=True)
    eprom = db.get_eprom("W27C512")
    config = db.convert_to_programmer(eprom)
    assert "bus-config" in config
    assert config["memory-size"] == 65536
```

**Mandatory pattern:** ALL test functions in this file must call `EpromDatabase(skip_local_override=True)`. Bare `EpromDatabase()` is forbidden in tests that assert chip data — it would load `~/.firestarter/database.json` if present on the operator's machine, causing CI/bench divergence (RESEARCH.md Pitfall 4).

---

### `firestarter_app/tests/test_bug_characterization.py` (test, in-process xfail)

**Analog:** `firestarter_app/tests/test_revision_constants_parity.py` (role-match — same assertive style; both are "contract enforcement" tests with a clear invariant docstring)

**Imports pattern:**
```python
"""
Phase 36 — Bug characterization suite (TEST-05).

Pins two latent bugs using pytest.mark.xfail(strict=True) asserting the
CORRECTED behavior. Each test auto-flips to XPASS when the fix lands
(strict=True makes XPASS a suite ERROR, forcing marker removal).

BUG-1: main.py:497 build_arg_flags uses 'in' not getattr → fix Phase 41 (CLI-03)
BUG-2: eprom_operations.py:265 EpromOperationError lumped with SerialError → fix Phase 42 (ERR-01)
"""
import pytest

from firestarter.main import build_arg_flags
from firestarter.constants import FLAG_FORCE
from firestarter.eprom_operations import EpromOperationError
```

**xfail(strict=True) pattern** (from RESEARCH.md Pattern 9):
```python
@pytest.mark.xfail(strict=True, reason="BUG: main.py:497 uses 'in' not getattr; fix lands Phase 41 (CLI-03)")
def test_build_arg_flags_force_truthiness_not_existence():
    """Corrected behavior: build_arg_flags should use getattr(args, 'force', False),
    not 'force' in args. The 'in' operator raises TypeError on non-Namespace objects.
    # BUG: main.py:497 — fix lands Phase 41 (CLI-03)
    """
    class PlainArgs:
        blank_check = True
        verbose = False
        vpe_as_vpp = False
        force = False  # force is False — FLAG_FORCE should NOT be set

    flags = build_arg_flags(PlainArgs())
    assert (flags & FLAG_FORCE) == 0  # corrected: force=False → FLAG_FORCE not set


@pytest.mark.xfail(strict=True, reason="BUG: eprom_operations.py:265 conflates EpromOperationError with SerialError; fix lands Phase 42 (ERR-01)")
def test_eprom_operation_error_not_labeled_as_communication_error(make_comm, fake_serial):
    """Corrected behavior: firmware ERROR response surfaces as operational error,
    NOT as 'Communication error during ...'.
    # BUG: eprom_operations.py:265 — fix lands Phase 42 (ERR-01)
    Operator-reported: 'app always reports that the communication is broken when the hw returns an error.'
    """
    ...
```

**Strict rule:** `strict=True` is MANDATORY — `strict=False` (the default) silently ignores XPASS and defeats the enforcement purpose. Each test body must include a `# BUG:` comment citing the fix phase. The Phase 41 and Phase 42 plans MUST each include a task to remove the corresponding `xfail` marker.

---

### `firestarter_app/tests/test_revision_constants_parity.py` (test, extend — cross-repo parity)

**Analog:** Itself (`firestarter_app/tests/test_revision_constants_parity.py`) — extend in place.

**Existing file to extend** (lines 1–44 are the canonical template — copy the docstring + pattern):
```python
# Existing: imports REVISION_* constants; asserts against hard-coded hex literals.
# Existing skipif guard: none (firmware always present in this repo layout).
# TEST-04 extension: add COMMAND_*, FLAG_*, CTRL_* blocks below the existing function.
```

**skipif guard to add** (from RESEARCH.md Pattern 8):
```python
from pathlib import Path

FIRMWARE_HEADER = Path(__file__).parent.parent.parent / "firestarter" / "include" / "firestarter.h"
FW_ABSENT = not FIRMWARE_HEADER.exists()
```

**COMMAND_* parity block to add** (from RESEARCH.md Pattern 8 + Code Examples):
```python
@pytest.mark.skipif(FW_ABSENT, reason="firestarter firmware checkout absent")
def test_command_values_match_firmware():
    from firestarter.constants import (
        COMMAND_READ, COMMAND_WRITE, COMMAND_ERASE,
        COMMAND_BLANK_CHECK, COMMAND_CHECK_CHIP_ID, COMMAND_VERIFY,
        COMMAND_READ_VPP, COMMAND_READ_VPE, COMMAND_FW_VERSION,
        COMMAND_CONFIG, COMMAND_HW_VERSION,
    )
    assert COMMAND_READ          == 0x01  # CMD_READ
    assert COMMAND_WRITE         == 0x02  # CMD_WRITE
    assert COMMAND_ERASE         == 0x03  # CMD_ERASE
    assert COMMAND_BLANK_CHECK   == 0x04  # CMD_BLANK_CHECK
    assert COMMAND_CHECK_CHIP_ID == 0x05  # CMD_CHECK_CHIP_ID
    assert COMMAND_VERIFY        == 0x06  # CMD_VERIFY
    # COMMAND_DEV_ADDRESS (0x07) and COMMAND_DEV_REGISTERS (0x08) are
    # #ifdef DEV_TOOLS in firmware — assert Python value only (not against header literal):
    assert COMMAND_READ_VPP      == 0x0B  # CMD_READ_VPP
    assert COMMAND_READ_VPE      == 0x0C  # CMD_READ_VPE
    assert COMMAND_FW_VERSION    == 0x0D  # CMD_FW_VERSION (D-09: confirmed present)
    assert COMMAND_CONFIG        == 0x0E  # CMD_CONFIG
    assert COMMAND_HW_VERSION    == 0x0F  # CMD_HW_VERSION
```

**FLAG_* parity block to add** (from RESEARCH.md Code Examples):
```python
@pytest.mark.skipif(FW_ABSENT, reason="firestarter firmware checkout absent")
def test_flag_values_match_firmware():
    from firestarter.constants import (
        FLAG_FORCE, FLAG_CAN_ERASE, FLAG_SKIP_ERASE,
        FLAG_SKIP_BLANK_CHECK, FLAG_VPE_AS_VPP,
        FLAG_OUTPUT_ENABLE, FLAG_CHIP_ENABLE, FLAG_VERBOSE,
    )
    assert FLAG_FORCE            == 0x01
    assert FLAG_CAN_ERASE        == 0x02
    assert FLAG_SKIP_ERASE       == 0x04
    assert FLAG_SKIP_BLANK_CHECK == 0x08
    assert FLAG_VPE_AS_VPP       == 0x10
    assert FLAG_OUTPUT_ENABLE    == 0x20
    assert FLAG_CHIP_ENABLE      == 0x40
    assert FLAG_VERBOSE          == 0x80
```

**CTRL_* note:** CTRL_* constants mirror `firestarter/include/rurp_pinout.h` (not `firestarter.h`). The skipif guard using `FIRMWARE_HEADER.exists()` is sufficient as a proxy — if `firestarter.h` is present, `rurp_pinout.h` is present alongside it. The test should reference both headers in comments.

---

### `firestarter_app/firestarter/database.py` (service/model, CRUD — de-singleton)

**Analog:** Itself — the section to modify is `database.py:165-204`.

**Current code to REMOVE** (lines 165–181):
```python
# REMOVE THIS BLOCK:
_instance = None
_initialized = False

def __new__(cls, *args, **kwargs):
    if not cls._instance:
        cls._instance = super(EpromDatabase, cls).__new__(cls, *args, **kwargs)
    return cls._instance

def __init__(self):
    if EpromDatabase._initialized:
        return
    self.proms = {}
    self.pin_maps = {}
    self._initialize_database_core()
    EpromDatabase._initialized = True
    logger.debug("EpromDatabase initialized.")
```

**Replacement `__init__`** (from RESEARCH.md De-Singleton Design):
```python
def __init__(self, skip_local_override: bool = False):
    self.proms = {}
    self.pin_maps = {}
    self._initialize_database_core(skip_local_override=skip_local_override)
    logger.debug("EpromDatabase initialized.")
```

**Updated `_initialize_database_core`** (lines 183–203, add `skip_local_override` parameter):
```python
def _initialize_database_core(self, skip_local_override: bool = False):
    self.proms = _read_config_file("chip_database.json")
    if not skip_local_override:
        local_db = get_local_database()
        if local_db:
            self.proms = self._merge_databases(self.proms, local_db)
    self.pin_maps = _read_config_file("pinouts.json")
    if not skip_local_override:
        local_pin_maps = get_local_pin_maps()
        if local_pin_maps:
            self.pin_maps = self._merge_pin_maps(self.pin_maps, local_pin_maps)
```

**Call sites unaffected:** `main.py:589` (`db_instance = EpromDatabase()`), `main.py:39/48` (argcomplete), `eprom_info.py:285`, `ic_layout.py:297` — all use bare `EpromDatabase()` which maps to `skip_local_override=False` (default). No call-site changes needed.

---

### `firestarter_app/pyproject.toml` (config — add test dep group)

**Analog:** Itself — lines 57–60 (the existing `[project.optional-dependencies]` section).

**Current section** (lines 57–60):
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
]
```

**Change to make:** Add a new `test` group BELOW the existing `dev` group. Do NOT rename or modify `dev` (existing `pip install -e ".[dev]"` workflows must not break):
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
]
test = [
    "pytest>=8.0",
    "syrupy>=5.0",
]
```

**Install command after change:** `pip install -e ".[test]"`

---

## Shared Patterns

### Fixture Injection (conftest.py)
**Source:** `firestarter_app/tests/conftest.py` (lines 122–147)
**Apply to:** `test_characterization.py` (happy-path tests), `test_serial_characterization.py`, `test_bug_characterization.py` (comm-error bug test)

The `fake_serial` and `make_comm` fixtures are pytest fixtures (decorated with `@pytest.fixture`). They are auto-discovered from `conftest.py` — new test files in the same `tests/` directory get them for free. No import of `conftest` is needed for fixture injection (pytest handles it). However, `build_frame` is a plain function, not a fixture — it must be explicitly imported:

```python
from .conftest import build_frame  # explicit import needed; NOT a fixture
```

The `make_comm` factory bypasses `SerialCommunicator.__init__` via `__new__` and directly sets `instance.connection = fake_serial`. This is the established project pattern for injecting a fake serial port without spawning real I/O.

### CRC Reference
**Source:** `firestarter_app/tests/conftest.py` (lines 37–49, `_ref_crc8_ccitt`)
**Apply to:** Any new test that assembles wire frames

The reference CRC is table-free (poly 0x07, seed 0x00, no reflection, no final XOR). It is deliberately different from the production lookup-table implementation — a regression in the production table produces a mismatch and fails the test. Use `build_frame(msg_id, params)` which calls `_ref_crc8_ccitt` internally.

### Module-Level Docstring Convention
**Source:** `firestarter_app/tests/test_decoder.py` (lines 1–22), `firestarter_app/tests/test_revision_constants_parity.py` (lines 1–19)
**Apply to:** All new test files

Every test file has a module-level docstring naming the phase, the requirement IDs it covers, and the key design rationale. This is the established style in this test suite. New files must follow it.

### Copyright Header
**Source:** `firestarter_app/tests/test_decoder.py` (lines 1–4), all other test files
**Apply to:** All new test files

```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.
```

### Syrupy Snapshot Workflow
**Source:** RESEARCH.md Pattern 4 (verified against syrupy 5.2.0 installed)
**Apply to:** `test_characterization.py` (all subprocess snapshot tests)

Snapshots are stored in `firestarter_app/tests/__snapshots__/test_characterization.ambr`. They are created on first run with `pytest --snapshot-update` and MUST be committed alongside the test file. The plan must include an explicit commit task for the `__snapshots__/` directory.

---

## No Analog Found

All files have clear analogs. No entries in this section.

---

## Metadata

**Analog search scope:** `firestarter_app/tests/`, `firestarter_app/firestarter/`, `firestarter_app/pyproject.toml`
**Files scanned:** 8 (conftest.py, test_decoder.py, test_revision_constants_parity.py, database.py, main.py, eprom_operations.py, pyproject.toml, firestarter_app/CLAUDE.md)
**Pattern extraction date:** 2026-05-27

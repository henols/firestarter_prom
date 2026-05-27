# Phase 39: Database Cleanup + chip_resolver — Pattern Map

**Mapped:** 2026-05-27
**Files analyzed:** 10 (2 new, 8 modified)
**Analogs found:** 10 / 10

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `firestarter_app/firestarter/chip_resolver.py` | service/utility | request-response | `firestarter_app/firestarter/address_parser.py` + `database.py` get/convert flow | role-match (flat leaf module wrapping a DB call) |
| `firestarter_app/tests/test_chip_resolver.py` | test | CRUD | `firestarter_app/tests/test_eprom_database.py` | exact (same DB construction pattern, class-per-surface style) |
| `firestarter_app/firestarter/main.py` | controller | request-response | itself (modify 9 copy-paste blocks) | self (structural reduction) |
| `firestarter_app/firestarter/database.py` | model/service | CRUD | itself (docstring + import header only) | self |
| `firestarter_app/firestarter/constants.py` | config | transform | itself (CTRL_*/REVISION_* block already shows target marker style) | self |
| `firestarter_app/firestarter/serial_comm.py` | middleware | request-response | `firestarter_app/firestarter/firmware.py` (same import conversion pattern) | role-match |
| `firestarter_app/firestarter/eprom_operations.py` | service | CRUD | `firestarter_app/firestarter/serial_comm.py` (same import conversion pattern) | role-match |
| `firestarter_app/firestarter/firmware.py` | service | request-response | `firestarter_app/firestarter/hardware.py` (same import conversion pattern) | exact |
| `firestarter_app/firestarter/hardware.py` | service | request-response | `firestarter_app/firestarter/firmware.py` (same import conversion pattern) | exact |
| `firestarter_app/firestarter/exceptions.py` | model | — | — | READ-ONLY source; `ChipNotFoundError` at line 55 |

---

## Pattern Assignments

### `firestarter_app/firestarter/chip_resolver.py` (service/utility, request-response)

**Primary analogs:**
1. `firestarter_app/firestarter/address_parser.py` — flat leaf module structure (stdlib + package imports, no star imports, clean docstring-per-function style)
2. `firestarter_app/firestarter/database.py` — `get_eprom` + `convert_to_programmer` call sequence being wrapped

**Module structure pattern** (from `address_parser.py` lines 1-10):
```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

<one-line description of what the module does>.
"""
```

**Imports pattern** — flat leaf module, no star imports, internal package imports only:
```python
# address_parser.py lines 10-11 (the entire import block of a flat leaf module)
from typing import Optional  # noqa: UP035
```

For `chip_resolver.py`, the import block follows the same flat-leaf pattern:
```python
from firestarter.database import EpromDatabase
from firestarter.exceptions import ChipNotFoundError
```

**Core resolution pattern** — the exact get/convert sequence being wrapped (from `main.py` lines 659-666, the representative read site):
```python
# main.py lines 659-666 — the copy-paste block at 9 sites
full_eprom_data = db_instance.get_eprom(args.eprom)
eprom_data = None
if full_eprom_data:
    eprom_data = db_instance.convert_to_programmer(full_eprom_data)
if not eprom_data:
    logger.error(f"EPROM '{args.eprom}' not found in database.")
    return 1
```

**Function signature with injectable DB** (from RESEARCH.md Pattern 1 — verified against `database.py:167`):
```python
def resolve_chip(name: str, db: EpromDatabase | None = None) -> dict:
    """Return the programmer-config dict for *name* or raise ChipNotFoundError.

    Uses EpromDatabase.get_eprom() + convert_to_programmer() internally.
    Pass *db* to inject a pre-constructed EpromDatabase (e.g., for tests that
    use skip_local_override=True to avoid loading ~/.firestarter overrides).
    """
    if db is None:
        db = EpromDatabase()
    full = db.get_eprom(name)
    data = db.convert_to_programmer(full) if full else None
    if not data:
        raise ChipNotFoundError(name)
    return data
```

**`EpromDatabase` constructor seam** (from `database.py` lines 167-171):
```python
def __init__(self, skip_local_override: bool = False):
    self.proms = {}
    self.pin_maps = {}
    self._initialize_database_core(skip_local_override=skip_local_override)
    logger.debug("EpromDatabase initialized.")
```

**`ChipNotFoundError` to copy from** (from `exceptions.py` lines 55-61):
```python
class ChipNotFoundError(Exception):
    """Raised when a chip name cannot be resolved in the database.

    Wired in Phase 39 (chip_resolver.py).
    """

    pass
```

---

### `firestarter_app/tests/test_chip_resolver.py` (test, CRUD)

**Analog:** `firestarter_app/tests/test_eprom_database.py`

**File header pattern** (lines 1-28 of `test_eprom_database.py`):
```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 39 Wave 1 — chip_resolver unit tests (DATA-01).

Tests use EpromDatabase(skip_local_override=True) to pin against the
packaged chip_database.json only, ignoring ~/.firestarter/database.json.

MANDATORY: every data-asserting test constructs
EpromDatabase(skip_local_override=True). Bare EpromDatabase() in tests
that assert specific chip data is forbidden — it would merge
~/.firestarter/database.json if present, causing CI/bench divergence.
"""
```

**Imports pattern** (from `test_eprom_database.py` lines 26-28):
```python
import pytest  # noqa: F401

from firestarter.database import ROM_CE, ROM_OE, EpromDatabase, pin_conversions
```

For `test_chip_resolver.py`, the imports follow the same pattern:
```python
import pytest

from firestarter.chip_resolver import resolve_chip
from firestarter.database import EpromDatabase
from firestarter.exceptions import ChipNotFoundError
```

**DB construction + happy path pattern** (from `test_eprom_database.py` lines 34-45):
```python
def test_get_eprom_w27c512_is_found(self):
    """W27C512 must be present in the packaged chip_database.json."""
    db = EpromDatabase(skip_local_override=True)
    eprom = db.get_eprom("W27C512")
    assert eprom is not None

def test_get_eprom_w27c512_memory_size(self):
    """W27C512 is a 64KB device — memory-size must equal 65536."""
    db = EpromDatabase(skip_local_override=True)
    eprom = db.get_eprom("W27C512")
    assert eprom is not None
    assert eprom["memory-size"] == 65536  # 64KB
```

**Not-found / raises pattern** (from `test_eprom_database.py` line 61-65):
```python
def test_get_eprom_unknown_chip_returns_none(self):
    """Querying a chip that does not exist must return None."""
    db = EpromDatabase(skip_local_override=True)
    result = db.get_eprom("NOTACHIP_XYZ_DOESNOTEXIST_9999")
    assert result is None
```

For `test_chip_resolver.py`, the raises form uses `pytest.raises` (from `test_address_parser.py` line 30-32 as the project's preferred raises-assertion pattern):
```python
def test_invalid_raises_value_error(self):
    with pytest.raises(ValueError):
        parse_address("not_a_number")
```

**Required-keys assertion pattern** (from `test_eprom_database.py` lines 95-102):
```python
def test_convert_to_programmer_required_keys_present(self):
    """Programmer config must carry the keys the firmware expects."""
    db = EpromDatabase(skip_local_override=True)
    eprom = db.get_eprom("W27C512")
    assert eprom is not None
    config = db.convert_to_programmer(eprom)
    for key in ("memory-size", "type", "algorithm", "pin-count", "vpp_mv", "flags"):
        assert key in config, f"Missing required key: {key}"
```

**Fixture pattern** (preferred over inline construction when DB is shared across tests — inferred from `test_eprom_database.py` which uses inline construction per test; both are acceptable, fixture reduces repetition for `test_chip_resolver.py`):
```python
@pytest.fixture
def db():
    return EpromDatabase(skip_local_override=True)
```

**Complete recommended test shape** (from RESEARCH.md Pattern code + validated against test_eprom_database.py style):
```python
def test_resolve_chip_hit_returns_dict(db):
    result = resolve_chip("W27C512", db=db)
    assert isinstance(result, dict)
    assert result["memory-size"] == 65536

def test_resolve_chip_hit_has_required_programmer_keys(db):
    result = resolve_chip("W27C512", db=db)
    for key in ("memory-size", "type", "algorithm", "pin-count", "vpp_mv", "flags"):
        assert key in result, f"Missing key: {key}"

def test_resolve_chip_miss_raises(db):
    with pytest.raises(ChipNotFoundError):
        resolve_chip("NOTACHIP_XYZ_DOESNOTEXIST", db=db)

def test_resolve_chip_conversion_correctness(db):
    result = resolve_chip("W27C512", db=db)
    full = db.get_eprom("W27C512")
    expected = db.convert_to_programmer(full)
    assert result == expected
```

---

### `firestarter_app/firestarter/main.py` — DATA-01 (9 sites) + DATA-03 (star-import)

**Analog (for catch pattern):** `firestarter_app/firestarter/serial_comm.py` lines 25-30 — shows project style for importing multiple named exceptions from a module:
```python
from firestarter.exceptions import (
    FirmwareOutdatedError,
    ProgrammerNotFoundError,
    SerialError,
    SerialTimeoutError,
)
```

**Current star-import to replace** (line 23):
```python
from firestarter.constants import *  # noqa: F403
```

**Target named import** (constants actually used in `main.py` — from RESEARCH.md Pattern 4, verified):
```python
from firestarter.constants import (
    CTRL_ADDRESS_LINE_16,
    CTRL_ADDRESS_LINE_17,
    CTRL_ADDRESS_LINE_18,
    CTRL_READ_WRITE,
    CTRL_VPE_ENABLE,
    CTRL_VPP_A9_ENABLE,
    CTRL_VPP_P1_ENABLE,
    CTRL_VPP_REGULATOR_ENABLE,
    CTRL_VPP_VPE_DROP_ENABLE,
    FLAG_CHIP_ENABLE,
    FLAG_OUTPUT_ENABLE,
)
```

**Current 9-site copy-paste pattern** (representative: `main.py` lines 659-666, `read` op):
```python
full_eprom_data = db_instance.get_eprom(args.eprom)
eprom_data = None
if full_eprom_data:
    eprom_data = db_instance.convert_to_programmer(full_eprom_data)
if not eprom_data:
    logger.error(f"EPROM '{args.eprom}' not found in database.")
    return 1
```

**Target pattern — shared helper approach** (from RESEARCH.md Pattern 2; preserves exact log string and exit-1 per D-03):
```python
from firestarter.chip_resolver import resolve_chip
from firestarter.exceptions import ChipNotFoundError

def _resolve_or_exit(name: str, db: EpromDatabase) -> dict | None:
    """Resolve chip or log + return None (caller returns 1)."""
    try:
        return resolve_chip(name, db=db)
    except ChipNotFoundError:
        logger.error(f"EPROM '{name}' not found in database.")
        return None
```

Each op site then becomes:
```python
elif args.command == "read":
    eprom_data = _resolve_or_exit(args.eprom, db_instance)
    if not eprom_data:
        return 1
    return (
        1
        if not eprom_operator.read_eprom(...)
        else 0
    )
```

**`dev consistency-check` site — special case** (from `main.py` lines 916-938; `eprom_data` IS passed downstream):
```python
elif args.dev_command == "consistency-check":
    full_eprom_data = db_instance.get_eprom(args.eprom)
    eprom_data = (
        db_instance.convert_to_programmer(full_eprom_data)
        if full_eprom_data
        else None
    )
    if not eprom_data:
        logger.error(f"EPROM '{args.eprom}' not found in database.")
        return 1
    return eprom_operator.consistency_check_eprom(
        args.eprom,
        eprom_data,        # <-- result IS used (passed to consistency_check_eprom)
        runs=args.runs,
        ...
    )
```

After refactor, this becomes identical to the other 8 sites (`_resolve_or_exit` + pass `eprom_data`); the D-04 "discards result" note only means the CONTEXT mistakenly implied the convert call was side-effect-only — the data is used.

**noqa markers to strip from `main.py`** — 3 total: 1× `# noqa: F403` on the import line, 2× `# noqa: F405` on usage lines.

---

### `firestarter_app/firestarter/database.py` — DATA-02 (docstring) + DATA-03 (star-import)

**`pin_conversions` variable location** (lines 68-69 — the target for the DATA-02 docstring comment):
```python
# eprom pins to rurp conversion
pin_conversions = {
    # Maps EPROM pin number to RURP hardware line number
```

**Target: replace the single-line comment at line 68 with an explanatory block comment directly above the `pin_conversions` dict** (from RESEARCH.md DATA-02 deliverable):
```python
# pin_conversions: RURP board-wiring layer.
# Maps DIP socket pin number → RURP bus line number (hardware-specific).
# This is DISTINCT from pinouts.json (loaded as self.pin_maps), which maps
# chip pin function → DIP socket pin number (chip-specific).
# They COMPOSE in get_bus_config(): pinouts.json gives function→socket-pin,
# pin_conversions gives socket-pin→bus-line. There is ONE source of truth
# per layer, not duplication.
pin_conversions = {
```

**Current star-import to replace** (line 33):
```python
from firestarter.constants import *  # noqa: F403
```

**Target named import** (only `FLAG_CAN_ERASE` is used in `database.py` — from RESEARCH.md Pattern 4):
```python
from firestarter.constants import FLAG_CAN_ERASE
```

**noqa markers to strip from `database.py`** — 2 total: 1× `# noqa: F403` on the import line, 1× `# noqa: F405` on usage line.

---

### `firestarter_app/firestarter/constants.py` — DATA-04 (sync markers)

**Existing marker pattern to copy** (lines 69-71 — `CTRL_*` block already has the model):
```python
# RURP Control Register Bits — mirror of firestarter/include/rurp_pinout.h
# Documentary only — Python does not write the control register directly
# (firmware owns that). Used by `firestarter dev registers --firestarter`
```

**And lines 83-84** (`REVISION_*` block):
```python
# RURP Hardware Revisions — mirror of firestarter/include/rurp_shield.h
# REVISION_* enum. Documentary only — Python does not perform the ADC
```

**Target — add equivalent marker to `COMMAND_*` block at line 25** (currently no marker; DATA-04 adds it):
```python
# Wire-protocol command codes — Firmware sync: firestarter.h
# cmd field values sent in JSON commands to the Arduino firmware.
COMMAND_READ = 1
```

**And to `FLAG_*` block at line 57** (currently no marker):
```python
# Control Flags — Firmware sync: firestarter.h
# flags bitmask values sent in JSON commands.
FLAG_FORCE = 0x01
```

**`COMMAND_FW_VERSION` presence** (line 37 — verify-only, no change):
```python
COMMAND_FW_VERSION = 13
```

**Parity test assertion location** (from `test_revision_constants_parity.py` line 116 — must stay green):
```python
assert COMMAND_FW_VERSION == 0x0D  # CMD_FW_VERSION (D-09: confirmed present)
```

---

### `firestarter_app/firestarter/serial_comm.py` — DATA-03 (star-import)

**Current star-import to replace** (line 24):
```python
from firestarter.constants import *  # noqa: F403
```

**Target named import** (from RESEARCH.md Pattern 4 — 9 constants used):
```python
from firestarter.constants import (
    BAUD_RATE,
    COMMAND_FW_VERSION,
    FLAG_CAN_ERASE,
    FLAG_CHIP_ENABLE,
    FLAG_FORCE,
    FLAG_OUTPUT_ENABLE,
    FLAG_SKIP_BLANK_CHECK,
    FLAG_SKIP_ERASE,
    FLAG_VPE_AS_VPP,
)
```

**Analog for the import style** — `serial_comm.py` lines 25-30 already shows multi-name imports from a single package module (the exceptions block):
```python
from firestarter.exceptions import (
    FirmwareOutdatedError,
    ProgrammerNotFoundError,
    SerialError,
    SerialTimeoutError,
)
```

**noqa markers to strip** — 13 total: 1× F403 on import line, 12× F405 on usage lines.

---

### `firestarter_app/firestarter/eprom_operations.py` — DATA-03 (star-import)

**Current star-import to replace** (line 27):
```python
from firestarter.constants import *  # noqa: F403
```

**Target named import** (from RESEARCH.md Pattern 4 — 15 constants used):
```python
from firestarter.constants import (
    BUFFER_SIZE,
    COMMAND_BLANK_CHECK,
    COMMAND_CHECK_CHIP_ID,
    COMMAND_DEV_ADDRESS,
    COMMAND_DEV_REGISTERS,
    COMMAND_ERASE,
    COMMAND_NAMES,
    COMMAND_READ,
    COMMAND_VERIFY,
    COMMAND_WRITE,
    FLAG_FORCE,
    FLAG_SKIP_BLANK_CHECK,
    FLAG_SKIP_ERASE,
    FLAG_VERBOSE,
    FLAG_VPE_AS_VPP,
)
```

**noqa markers to strip** — 26 total: 1× F403 on import line, 25× F405 on usage lines.

---

### `firestarter_app/firestarter/firmware.py` — DATA-03 (star-import)

**Current star-import to replace** (line 28):
```python
from firestarter.constants import *  # noqa: F403
```

**Target named import** (from RESEARCH.md Pattern 4 — 5 constants used, including URL constants from `constants.py` lines 8-15):
```python
from firestarter.constants import (
    COMMAND_FW_VERSION,
    FIRESTARTER_RELEASE_BY_TAG_URL,
    FIRESTARTER_RELEASES_URL,
    FIRESTARTER_RELEASE_URL,
    FLAG_FORCE,
)
```

**noqa markers to strip** — 6 total: 1× F403 on import line, 5× F405 on usage lines.

---

### `firestarter_app/firestarter/hardware.py` — DATA-03 (star-import)

**Current star-import to replace** (line 14):
```python
from firestarter.constants import *  # noqa: F403
```

**Target named import** (from RESEARCH.md Pattern 4 — 5 constants used):
```python
from firestarter.constants import (
    COMMAND_CONFIG,
    COMMAND_HW_VERSION,
    COMMAND_READ,
    COMMAND_READ_VPE,
    COMMAND_READ_VPP,
)
```

**noqa markers to strip** — 5 total: 1× F403 on import line, 4× F405 on usage lines.

---

## Shared Patterns

### Flat Leaf Module Structure
**Source:** `firestarter_app/firestarter/address_parser.py` (entire file, 30 lines)
**Apply to:** `chip_resolver.py`
- MIT license header block
- Single-sentence module docstring describing purpose
- No star imports; stdlib + explicit named package imports only
- Function-level docstrings with param/raise documentation
- No class wrappers

### Named Multi-Import Block Style
**Source:** `firestarter_app/firestarter/serial_comm.py` lines 25-30
**Apply to:** All 6 star-import modules (DATA-03)
```python
from firestarter.exceptions import (
    FirmwareOutdatedError,
    ProgrammerNotFoundError,
    SerialError,
    SerialTimeoutError,
)
```
When 3 or more names come from a single module, use a parenthesized multi-line import sorted alphabetically.

### `EpromDatabase(skip_local_override=True)` Test Seam
**Source:** `firestarter_app/tests/test_eprom_database.py` line 36
**Apply to:** `test_chip_resolver.py` — every test that asserts chip data content
```python
db = EpromDatabase(skip_local_override=True)
```
Never use bare `EpromDatabase()` in tests that assert specific chip values — it merges `~/.firestarter/database.json` if present.

### Exception-Raising + Catch Pattern
**Source:** `firestarter_app/firestarter/serial_comm.py` lines 25-30 (import) + the existing `ChipNotFoundError` at `exceptions.py:55-61`
**Apply to:** `chip_resolver.py` (raise) and `main.py` `_resolve_or_exit` helper (catch)
- Raise typed domain exception (not ad-hoc string comparison)
- Catch at the dispatch boundary, preserve exact log string: `f"EPROM '{name}' not found in database."`
- Return `None` from helper; caller returns `1`

### Firmware-Sync Block Comment Style
**Source:** `firestarter_app/firestarter/constants.py` lines 69-72 (CTRL_* block), lines 83-88 (REVISION_* block)
**Apply to:** `constants.py` COMMAND_* block (line 25) and FLAG_* block (line 57) — DATA-04
```python
# RURP Control Register Bits — mirror of firestarter/include/rurp_pinout.h
# Documentary only — Python does not write the control register directly
```
Target marker format for COMMAND_*/FLAG_*:
```python
# Wire-protocol command codes — Firmware sync: firestarter.h
```

---

## No Analog Found

All files have sufficiently close analogs in the codebase. No gaps.

| File | Role | Data Flow | Reason |
|---|---|---|---|
| — | — | — | — |

---

## SC Inaccuracies (Document for Planner)

Per D-11 and CONTEXT.md specifics section — these are known, planner must treat them as closed (already resolved by decisions):

| SC Ref | Inaccuracy | Resolution |
|---|---|---|
| SC#1 says `test_chip_resolver.py` "from Phase 36" | The file does NOT exist yet | Wave 1 creates it (DATA-01) |
| SC#3 names 4 modules for star-import sweep | Repo-wide grep finds 6 modules | All 6 must be converted (D-06) |
| SC#4 refers to `test_firmware_contract_parity.py` | Real filename is `test_revision_constants_parity.py` | Use the real filename (D-11) |
| DATA-02 REQUIREMENTS wording says "consolidate" | Composition is correct, not duplication | Docstring-only (D-05) |

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/*.py`, `firestarter_app/tests/test_eprom_database.py`, `firestarter_app/tests/test_address_parser.py`, `firestarter_app/tests/test_revision_constants_parity.py`
**Files scanned:** 14
**Pattern extraction date:** 2026-05-27
**Branch:** v1.8-app-cleanup
**Baseline:** 182 passed + 2 xfailed + 29 syrupy snapshots

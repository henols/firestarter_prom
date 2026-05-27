# Phase 38: Low-Risk Extractions — Research

**Researched:** 2026-05-27
**Domain:** Python module extraction + dead-code removal (firestarter_app host CLI, v1.8 milestone)
**Confidence:** HIGH — all claims sourced from live codebase reads and tool runs

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

All decisions D-01 through D-16 are locked. Key entries:

- **D-01:** `exceptions.py` contains 8 classes: 6 existing (`SerialError`, `SerialTimeoutError`, `ProgrammerNotFoundError`, `FirmwareOutdatedError`, `EpromOperationError`, `HardwareOperationError`) + `FirmwareOperationError` (from `firmware.py:63`) + `ChipNotFoundError` (new, empty stub for Phase 39).
- **D-02:** `AvrdudeNotFoundError` / `AvrdudeConfigNotFoundError` STAY in `avr_tool.py` (different domain — `FileNotFoundError` subclass, avrdude binary discovery, not wire/operation/hardware).
- **D-03:** Preserve existing inheritance exactly. No unifying `FirestarterError` base.
- **D-04:** All import/raise/except sites repointed to `from firestarter.exceptions import ...`. `exceptions.py` imports nothing from the package (stdlib only — pure leaf).
- **D-05:** `frame_parser.py` gets ONLY the truly-pure primitives: `_build_crc8_table`, `_CRC8_CCITT_TABLE`, `_crc8_ccitt`, `_decode_param`, `Response`, `LogMessage`, `MAGIC_PREAMBLE`. Stdlib only.
- **D-06:** `_decode_id_frame` STAYS in `serial_comm.py` for Phase 38. Documented deviation from SC#2's literal symbol list.
- **D-07:** `test_decoder.py` must pass unchanged (SC#2 / D-07).
- **D-08:** `codec.py` contains `format_message` (renamed from `_format_message`) + `_REVISION_SILKSCREEN`. Imports `constants.py` + `messages.py` only (per SC#3).
- **D-09:** `_read_and_parse_lines` is UNTOUCHED — ring-fenced per GATE-1.8d.
- **D-10:** `# DO NOT MODIFY` marker on `_read_and_parse_lines` is Phase 40's job.
- **D-11/D-12/D-13:** `address_parser.py` raises `ValueError`; `_setup_operation` wraps in `try/except ValueError` preserving exact log strings and `(None, 0)` return.
- **D-14:** Delete `read_data_block` from `serial_comm.py` — zero callers confirmed.
- **D-15:** Replace `globals()` reverse-lookups with `COMMAND_NAMES[cmd]`.
- **D-16:** Remove only confirmed-dead commented blocks. Preserve Phase-35 WR-01/02 rationale comments (migrate verbatim to `codec.py`).

### Claude's Discretion

- Exact module docstrings / function-order within each new file.
- Whether `parse_size` returns `int | None` or `int`; whether `parse_address` wraps `ValueError` with custom message.
- Private (`_`) vs public naming for frame_parser primitives (SC#2 uses `_` names, keep them).
- Test-file organization beyond the two mandated new files (`tests/test_codec.py`, `tests/test_address_parser.py`).
- Plan/wave decomposition (natural ordering: exceptions → frame_parser → codec → address_parser → dead-code sweep).

### Deferred Ideas (OUT OF SCOPE)

- Unifying `FirestarterError` base class (Phase 42 candidate).
- Making `_decode_id_frame` a pure DI function (Phase 40).
- avrdude mcu-detection fallback, serial COBS resync, W27C512 misclassification.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| STRUCT-01 | Frame parsing extracted to `frame_parser.py` (CRC8, `_decode_param`, structured `Response`/`LogMessage`); `test_decoder.py` passes unchanged | D-05/D-07 confirmed; CRITICAL landmine documented in §Scout Verification |
| STRUCT-02 | Message decode/format extracted to `codec.py` (`format_message`, silkscreen rendering) | D-08 confirmed; codec imports documented (3 package deps, not 2 — see §Scout Verification) |
| STRUCT-03 | Address/size parsing extracted to `address_parser.py` with explicit `ValueError` | D-11/D-12/D-13 confirmed; call-site preservation verified |
| STRUCT-04 | Exception classes consolidated into `exceptions.py` | D-01–D-04 confirmed; all raise/import/except sites enumerated |
| STRUCT-05 | Dead code removed (`read_data_block`, `globals()`, confirmed-dead commented blocks) | D-14/D-15 confirmed; grep evidence in §Scout Verification |
</phase_requirements>

---

## Summary

Phase 38 extracts four groups of pure-compute code from spaghetti modules into new flat sibling modules, then removes confirmed dead code. All design decisions are locked in CONTEXT.md (D-01 through D-16). The research role is to independently de-risk the structural claims the planner will rely on and to produce a Validation Architecture.

**The safety net is solid.** The Phase 36 suite (162 passed + 2 xfailed + 29 syrupy snapshots) runs clean today. The Phase 37 tooling gate (ruff, mypy watermark=44) is enforced. Every file-move is independently verifiable by running the full suite after each atomic step.

**Two landmines require planner attention** that are not fully resolved by the locked decisions:

1. `test_decoder.py` imports `MAGIC_PREAMBLE`, `LogMessage`, `Response`, `_crc8_ccitt` directly from `firestarter.serial_comm` (lines 50–55). After those symbols move to `frame_parser.py`, `serial_comm.py` MUST re-export them (e.g. `from firestarter.frame_parser import Response, LogMessage, MAGIC_PREAMBLE, _crc8_ccitt`) or `test_decoder.py` will break. The CONTEXT D-07 constraint ("test_decoder.py passes unchanged") makes re-export the required approach.

2. `_format_message` calls `_decode_param` in its MSG_DEBUG sub-dispatch branch (line 428). When extracted to `codec.py`, the D-08 constraint "imports from `constants.py` + `messages.py` only" is incomplete — `codec.py` will also need `from firestarter.frame_parser import _decode_param` (and `import struct` for `struct.error`). This is NOT a cycle (frame_parser is a stdlib-only leaf), but the planner must add it to the import list.

**Primary recommendation:** Execute in dependency-safe order (exceptions → frame_parser → codec → address_parser → dead-code sweep), with the full suite run after each extraction commit.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Exception definitions | New leaf `exceptions.py` | Nothing (pure leaf) | All app exceptions in one place; importers repoint |
| CRC8 + frame primitives | New leaf `frame_parser.py` | Stdlib only | Pure compute with no package deps — independently testable |
| Message rendering (sentinel-aware) | New `codec.py` | `frame_parser._decode_param` (for MSG_DEBUG sub-dispatch) | Depends on constants + messages + frame_parser |
| Address/size string parsing | New `address_parser.py` | Nothing | Pure compute, stdlib only |
| Wire frame orchestration (`_decode_id_frame`) | `serial_comm.py` (stays) | `frame_parser`, `codec` | Package-coupled (catalog + codec) — Phase 40 concern |
| Ring-fenced read path | `serial_comm.py` (`_read_and_parse_lines`) | Nothing (UNTOUCHED) | GATE-1.8d; v1.9 RCA territory |

---

## Scout Verification: Structural Claims

Each claim from CONTEXT.md was independently verified against the live source. All line numbers reference `firestarter_app/firestarter/serial_comm.py` and `firestarter_app/firestarter/eprom_operations.py` as of branch `v1.8-app-cleanup`.

### Claim 1 — D-14: `read_data_block` has ZERO callers

**CONFIRMED.** [VERIFIED: grep]

```
$ grep -rn "read_data_block" firestarter_app/ --include="*.py"
firestarter/serial_comm.py:991:    def read_data_block(self) -> bytes:
```

Exactly one hit: its own definition at line 991. No callers in any test file, no callers in any other module. Total file length: 1066 lines. Safe to delete.

### Claim 2 — D-05: Frame primitives at serial_comm.py lines 47–92 use stdlib only

**CONFIRMED.** [VERIFIED: AST analysis + grep]

Exact locations confirmed:

| Symbol | Line | Notes |
|--------|------|-------|
| `Response` (namedtuple) | 47 | `collections.namedtuple` |
| `LogMessage` (namedtuple) | 52–54 | `collections.namedtuple` |
| `MAGIC_PREAMBLE` | 55 | Literal `bytes` |
| `_build_crc8_table` | 58–74 | Pure Python arithmetic only |
| `_CRC8_CCITT_TABLE` | 77 | Module-level call to `_build_crc8_table()` |
| `_crc8_ccitt` | 80–85 | Uses `_CRC8_CCITT_TABLE` only |
| `_decode_param` | 88–139 | Uses `struct`, `typing` — stdlib only |

The CONTEXT claim of `:47-92` is accurate (the block ends at line 139 with `_decode_param`'s body — the `:47-92` range in CONTEXT referred to the symbol span, not line count). All imports used by these symbols: `struct` (stdlib), `collections.namedtuple` (stdlib), `typing` (stdlib). **Zero package-internal imports in this block.** [VERIFIED: no `from firestarter` in lines 47–139 of serial_comm.py]

### Claim 3 — D-08: `_format_message` does NOT reference `self`

**CONFIRMED.** [VERIFIED: AST analysis]

AST walk of `_format_message` body (lines 341–450) finds zero `Name(id='self')` nodes. It takes `self` as its first argument (because it's a method) but never uses it. It drops cleanly to a module-level pure function when extracted to `codec.py`.

**IMPORTANT CORRECTION TO D-08:** `_format_message` (the future `codec.format_message`) calls `_decode_param` at line 428 in the MSG_DEBUG sub-dispatch branch:

```python
# firestarter/serial_comm.py:428
value, cursor = _decode_param(ptype, sub_body, cursor)
```

It also uses `struct.error` in the except clause at line 438. Therefore `codec.py` requires THREE package imports, not two:

```python
import struct
from firestarter.constants import COMMAND_NAMES, REVISION_0, REVISION_1, REVISION_2_0, REVISION_2_1, REVISION_2_2, REVISION_2_3, REVISION_UNKNOWN
from firestarter.messages import (CATALOG, DBG_CMD, DEBUG_CATALOG, MSG_DATA_CHUNK, MSG_DEBUG, MSG_INFO_CMD, MSG_INFO_HW, MSG_INFO_PHYSICAL_HW, MSG_OK_CFG, MSG_OK_REV, SEVERITY_LABEL)
from firestarter.frame_parser import _decode_param
```

The D-08 constraint "imports from `constants.py` + `messages.py` only" is incomplete. The planner MUST add `from firestarter.frame_parser import _decode_param`. This is **not a cycle** — `frame_parser` is a stdlib-only leaf — but it IS a third package import not listed in D-08.

The `_REVISION_SILKSCREEN` dict also references `REVISION_*` constants (currently imported via the star import), which become explicit named imports in `codec.py`. [VERIFIED: AST + grep]

### Claim 4 — D-08: `messages.py` has ZERO package-internal imports

**CONFIRMED.** [VERIFIED: grep]

```
$ grep -rn "from firestarter" firestarter/messages.py
(no output)
```

`messages.py` imports only `dataclasses` and `typing` — both stdlib. Cycle-safe for `codec.py` to import it. [VERIFIED: grep confirms no `from firestarter` imports]

### Claim 5 — D-15: `globals()` sites at eprom_operations.py lines 170 and 232

**CONFIRMED.** [VERIFIED: grep]

```
$ grep -n "globals()" firestarter/eprom_operations.py
170:        operation = [k for k, v in globals().items() if v == cmd][0].replace("COMMAND_", "")
232:        operation_name = [k for k, v in globals().items() if v == cmd][0].replace("COMMAND_", "")
```

Both sites use the identical pattern. Both are used only for log output (the result is assigned to `operation`/`operation_name` and used in `logger.debug()`).

**CONFIRMED: `COMMAND_NAMES` values match old post-`.replace` strings exactly.** [VERIFIED: live Python execution]

```
cmd=1:  old='READ'          new='READ'          match=True
cmd=2:  old='WRITE'         new='WRITE'         match=True
cmd=3:  old='ERASE'         new='ERASE'         match=True
cmd=4:  old='BLANK_CHECK'   new='BLANK_CHECK'   match=True
cmd=5:  old='CHECK_CHIP_ID' new='CHECK_CHIP_ID' match=True
cmd=6:  old='VERIFY'        new='VERIFY'        match=True
cmd=7:  old='DEV_ADDRESS'   new='DEV_ADDRESS'   match=True
cmd=8:  old='DEV_REGISTERS' new='DEV_REGISTERS' match=True
cmd=11: old='READ_VPP'      new='READ_VPP'      match=True
cmd=12: old='READ_VPE'      new='READ_VPE'      match=True
cmd=13: old='FW_VERSION'    new='FW_VERSION'    match=True
cmd=14: old='CONFIG'        new='CONFIG'        match=True
cmd=15: old='HW_VERSION'    new='HW_VERSION'    match=True
```

**Behavior note on `globals()` IndexError vs `COMMAND_NAMES[cmd]` KeyError:** The old `[0]` on an empty list raises `IndexError`; the new `COMMAND_NAMES[cmd]` raises `KeyError`. Both are unhandled and would surface identically to a caller as an uncaught exception. Behavior-identical for the valid-cmd case; equally fatal for an unknown cmd. This is acceptable — the planner should document this equivalence in the commit message.

### Claim 6 — D-13: `command_dict["address"]` set-only-inside-`if address:`; `memory-size` gated on `cmd == COMMAND_READ and size`

**CONFIRMED.** [VERIFIED: source read, eprom_operations.py:182–200]

```python
# eprom_operations.py:182-200 (exact)
addr = 0
if address:
    try:
        addr = int(address, 16) if "0x" in address.lower() else int(address)
        command_dict["address"] = addr          # KEY: only set when address provided
    except ValueError:
        logger.error(f"Invalid address format: {address}")
        return None, 0

if cmd == COMMAND_READ and size:               # KEY: gated on both conditions
    try:
        read_size = int(size, 16) if "0x" in size.lower() else int(size)
        command_dict["memory-size"] = addr + read_size
    except ValueError:
        logger.error(f"Invalid size format: {size}")
        return None, 0
```

The `addr = 0` default (used in `memory-size = addr + read_size`) is OWNED by `_setup_operation`, not the parser. The parser returns `None` for absent input; `_setup_operation` retains its own `addr = 0` local for the computation. The D-13 "subtlety" is exactly as described.

### Claim 7 — D-12: Exact log strings for bad address/size

**CONFIRMED.** [VERIFIED: source read]

- Bad address: `f"Invalid address format: {address}"` (line 188)
- Bad size: `f"Invalid size format: {size}"` (line 199)
- Return on both: `return None, 0`

These exact strings must be preserved in the `_setup_operation` `try/except ValueError` wrapper after extraction.

### Claim 8 — Exception import/raise/except sites enumeration (for D-04 repoint list)

[VERIFIED: grep across all .py files in firestarter/ and tests/]

#### `SerialError` (currently in serial_comm.py:188)
- **Defined:** `serial_comm.py:188`
- **Raised:** `serial_comm.py:251, 258, 267, 287, 594, 626, 641, 656, 1012, 1024` (and `__main__` block)
- **Imported + used in:** `eprom_operations.py:27,209,283`; `firmware.py:29,127`; `hardware.py:16,73,101,155,237`
- **Caught:** `eprom_operations.py:209,283`; `firmware.py:127`; `hardware.py:73,101,155,237`; `serial_comm.py:933`

#### `SerialTimeoutError` (currently in serial_comm.py:194)
- **Defined:** `serial_comm.py:194`
- **Raised:** `serial_comm.py:265, 700, 1020`
- **Imported + used in:** `eprom_operations.py:31,283`; `hardware.py:19,73,101,155,237`; `tests/test_serial_characterization.py:27`
- **Caught:** `eprom_operations.py:283`; `hardware.py:73,101,155,237`

#### `ProgrammerNotFoundError` (currently in serial_comm.py:200)
- **Defined:** `serial_comm.py:200`
- **Raised:** `serial_comm.py:961, 989`
- **Imported + used in:** `eprom_operations.py:28,209`; `firmware.py:31,127`; `hardware.py:16,237`; `tests/test_characterization.py:350,377`
- **Caught:** `eprom_operations.py:209`; `firmware.py:127`; `hardware.py:237`; `serial_comm.py:980` (re-raised)

#### `FirmwareOutdatedError` (currently in serial_comm.py:206)
- **Defined:** `serial_comm.py:206`
- **Raised:** `serial_comm.py:882, 893, 899, 904, 909`
- **Imported + used in:** `firmware.py:30,125`; `tests/test_fwguard.py:29`
- **Caught:** `firmware.py:125`; `serial_comm.py:933,937,980` (re-raised at 980)

#### `EpromOperationError` (currently in eprom_operations.py:84)
- **Defined:** `eprom_operations.py:84`
- **Raised:** `eprom_operations.py:302, 338, 349, 360, 412`
- **Imported + used in:** `tests/test_decoder.py:634,636,662`; `tests/test_consistency_check.py:62,261,263,275`; `tests/test_bug_characterization.py:82,88,97,116`
- **Caught:** `eprom_operations.py:283,600` (line 283 is the bug-pin for Phase 42)

#### `HardwareOperationError` (currently in hardware.py:25)
- **Defined:** `hardware.py:25`
- **Raised:** (grep finds none — only caught, defined, and used in `hardware.py:240`)
- **Caught:** `hardware.py:240`

#### `FirmwareOperationError` (currently in firmware.py:63) — D-01 inclusion
- **Defined:** `firmware.py:63`
- **Raised:** NEVER — zero raise sites in the entire codebase. [VERIFIED: grep + AST analysis confirm no `raise FirmwareOperationError` anywhere]
- **Caught:** NEVER — zero except/import sites.
- **Note for planner:** This is a true orphan — defined but never used. Still included per D-01 (consolidation intent). Moving it is a mechanical copy with no call-site repoints needed.

#### `ChipNotFoundError` — D-01 new stub
- **Defined:** Nowhere yet (to be created in `exceptions.py`)
- **Raised/Caught:** Nowhere yet (Phase 39 wires it)

---

## CRITICAL LANDMINE: test_decoder.py Imports from serial_comm

**Status: CORRECTION NEEDED — not captured in CONTEXT D-07.**

`tests/test_decoder.py` lines 50–55 import directly from `firestarter.serial_comm`:

```python
from firestarter.serial_comm import (
    MAGIC_PREAMBLE,  # noqa: F401
    LogMessage,
    Response,
    _crc8_ccitt,
)
```

All four symbols (`MAGIC_PREAMBLE`, `LogMessage`, `Response`, `_crc8_ccitt`) are exactly the symbols D-05 plans to MOVE to `frame_parser.py`.

If those symbols are simply deleted from `serial_comm.py`, `test_decoder.py` will raise `ImportError` — failing the suite, violating D-07/SC#2.

**The resolution:** `serial_comm.py` MUST re-export these four symbols after moving them. Concretely, after the frame_parser extraction, add to `serial_comm.py`:

```python
# Re-exports for backward compatibility (test_decoder.py + downstream callers)
from firestarter.frame_parser import (  # noqa: F401
    MAGIC_PREAMBLE,
    LogMessage,
    Response,
    _crc8_ccitt,
)
```

This keeps `test_decoder.py` unchanged (SC#2) while the canonical definitions live in `frame_parser.py`. The planner MUST include this re-export step in the frame_parser extraction task.

**Why this matters:** This is not a minor nit — it is a suite-breaking omission if missed. The Phase 36 suite will fail on the very first import of `test_decoder.py` if the re-exports are absent.

---

## Standard Stack

This phase installs NO new packages. All work is pure Python file moves and edits. The existing toolchain (ruff, mypy, pytest, syrupy) is already installed from Phase 37.

### Package Legitimacy Audit

No packages are installed in this phase. Section not applicable.

---

## Architecture Patterns

### Extraction Pattern: Leaf Module

Each new module follows the same pattern:

1. Copy the target functions/classes to the new file
2. Add appropriate stdlib imports at the top of the new file
3. Add re-exports in the SOURCE file (for any symbols that existing callers import)
4. Remove the original definitions from the source file (ONLY after re-exports are in place)
5. Run the full suite — must be green before proceeding to the next extraction

### Recommended Project Structure (after Phase 38)

```
firestarter_app/firestarter/
├── exceptions.py        # NEW — all 8 app exception classes (stdlib-only leaf)
├── frame_parser.py      # NEW — CRC8 + decode primitives (stdlib-only leaf)
├── codec.py             # NEW — format_message + _REVISION_SILKSCREEN
├── address_parser.py    # NEW — parse_address + parse_size
├── serial_comm.py       # MODIFIED — remove moved symbols, add re-exports, delete read_data_block
├── eprom_operations.py  # MODIFIED — repoint EpromOperationError, wrap address/size, fix globals()
├── firmware.py          # MODIFIED — repoint FirmwareOperationError
├── hardware.py          # MODIFIED — repoint HardwareOperationError
└── constants.py         # UNTOUCHED (COMMAND_NAMES already there; no edits needed)

firestarter_app/tests/
├── test_codec.py        # NEW — format_message unit tests
├── test_address_parser.py  # NEW — parse_address + parse_size unit tests
└── test_decoder.py      # MUST pass UNCHANGED (imports from serial_comm via re-exports)
```

### Pattern: Module-Level `_format_message` (codec.format_message)

When extracted, the function signature changes from:
```python
# serial_comm.py (method)
def _format_message(self, msg_id: int, params: list, entry) -> Optional[str]:
```
to:
```python
# codec.py (pure function — no self)
def format_message(msg_id: int, params: list, entry) -> Optional[str]:
```

The call site in `_decode_id_frame` (serial_comm.py:530) changes from:
```python
text = self._format_message(msg_id, values, entry)
```
to:
```python
import firestarter.codec as codec  # or: from firestarter.codec import format_message
text = codec.format_message(msg_id, values, entry)
```

### Pattern: address_parser with ValueError Contract

```python
# firestarter/address_parser.py
from typing import Optional

def parse_address(s: Optional[str]) -> Optional[int]:
    """Parse hex or decimal address string. Returns None for None input.
    Raises ValueError on bad format."""
    if s is None:
        return None
    return int(s, 16) if "0x" in s.lower() else int(s)

def parse_size(s: Optional[str]) -> Optional[int]:
    """Parse hex or decimal size string. Returns None for None input.
    Raises ValueError on bad format."""
    if s is None:
        return None
    return int(s, 16) if "0x" in s.lower() else int(s)
```

Call site wrapper in `_setup_operation` (preserves exact log strings and `(None, 0)` return):

```python
from firestarter.address_parser import parse_address, parse_size

addr = 0
if address:
    try:
        addr = parse_address(address)
        command_dict["address"] = addr
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

### Anti-Patterns to Avoid

- **Removing serial_comm re-exports before updating test_decoder.py imports:** Will break the suite. Either re-export first OR update test_decoder.py (re-export is the "unchanged" path).
- **Moving `_decode_id_frame` to frame_parser:** Violates D-06 (it's package-coupled). Phase 40's job.
- **Moving `_read_and_parse_lines`:** GATE-1.8d; absolutely off-limits.
- **Star-import removal (`from firestarter.constants import *`):** Phase 39 / DATA-03. Leave `# noqa: F403/F405` parked in Phase 38.
- **Fixing the EpromOperationError comm-error bug (eprom_operations.py:283):** Phase 42 / ERR-01. Leave xfail test as-is.
- **Adding a unifying `FirestarterError` base:** Deferred to Phase 42.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Test frame assembly | Custom byte-packing | `conftest.build_frame` (already exists) | Established fixture; produces correct wire-format frames |
| CRC8 reference computation | New CRC function in tests | `conftest._ref_crc8_ccitt` (already exists) | Table-free reference; catches table-mutation regressions |
| Address parsing edge cases | Inline `try/except` spread across callers | `address_parser.parse_address` / `parse_size` | Tested unit; error messages centralized |

---

## Ordering and Landmine Summary

### Dependency-Safe Ordering

```
Step 1: exceptions.py         — pure leaf, unblocks all repoints
Step 2: frame_parser.py       — pure leaf, unblocks codec
Step 3: (re-exports in serial_comm.py)  — IMMEDIATELY AFTER frame_parser creation; before removing originals
Step 4: Remove originals from serial_comm.py
Step 5: codec.py              — depends on constants + messages + frame_parser._decode_param
Step 6: address_parser.py     — independent; can follow any ordering after step 1
Step 7: Dead-code sweep       — delete read_data_block, fix globals(), strip dead comments
```

Each step = one atomic commit with full suite green before moving to the next.

### Ordering Hazards

1. **frame_parser re-exports MUST precede deleting originals from serial_comm.py** (test_decoder.py landmine documented above). Safest approach: create frame_parser.py + add re-exports to serial_comm.py in the same commit, THEN run suite (green), THEN remove originals.

2. **codec.py depends on `_decode_param` being importable from frame_parser.** Create frame_parser.py first (Step 2), then codec.py (Step 5).

3. **exceptions.py must be created before any repoint commit.** If you move `SerialError` and simultaneously update `eprom_operations.py`'s import before `exceptions.py` exists, the import fails. The planner should bundle: create `exceptions.py` + repoint all import sites in a single commit.

4. **Star-import `# noqa: F403/F405` suppressions STAY.** When touching `serial_comm.py` (removing frame primitives, `_format_message`, re-exports), do NOT remove the `# noqa: F405` annotations on the `_REVISION_SILKSCREEN` dict or `BAUD_RATE` references. After `_REVISION_SILKSCREEN` moves to `codec.py`, those `# noqa` lines become moot in `serial_comm.py` (they move with the dict to `codec.py` where they remain needed until Phase 39 resolves the star-import). The ruff gate must stay green.

5. **`eprom_operations.py` star-import stays.** The `from firestarter.constants import *` in `eprom_operations.py` is Phase 39 / DATA-03. Do NOT resolve it in Phase 38. The `globals()` replacement (`COMMAND_NAMES[cmd]`) works correctly WITH the star-import still present.

6. **mypy watermark.** Phase 37 established a watermark of 44 errors. After Phase 38 edits, run `python tools/check_mypy_watermark.py` — the extraction should NOT increase the error count. New typed signatures in the new files may actually REDUCE it. The CI gate enforces "no new errors vs. watermark."

---

## Validation Architecture

This section is the authoritative specification for proving "zero behavior change" after each file move.

### Safety Net: Phase 36 Characterization Suite

**How to run:**
```bash
cd firestarter_app
python -m pytest --tb=short -q
```

**Expected baseline (verified today):**
- 162 passed
- 2 xfailed (both `strict=True` bug characterizations — they must remain xfailed, not xpassed)
- 29 syrupy snapshots passed
- Total wall time: ~14–18 seconds (no hardware required)

**Acceptance signal:** Suite must be green after EVERY atomic extraction commit. If the suite goes red after a move, STOP — the move broke something. Fix before proceeding.

**Snapshot diff must be empty.** After each extraction commit, run:
```bash
python -m pytest --snapshot-update --tb=short -q
```
If `--snapshot-update` produces any changes, there is a behavior difference in CLI output — a Phase 38 violation.

### New Unit Tests (to be created in Wave 0)

#### tests/test_codec.py — covers `format_message`

The following fixtures are mandated by D-08 and SC#3. Test inputs derive from the catalog message IDs exercised in the existing `test_decoder.py`:

| Test | Input | Expected Output |
|------|-------|-----------------|
| `test_msg_ok_rev_no_override` | `msg_id=MSG_OK_REV, params=[0x00, 0xFF]` | `"Rev 0"` (no override sentinel) |
| `test_msg_ok_rev_with_override` | `msg_id=MSG_OK_REV, params=[0x02, 0x04]` | `"Rev 2.2 (override), Override HW: Rev 2.0-class"` |
| `test_msg_ok_cfg_no_override` | `msg_id=MSG_OK_CFG, params=[10000, 20000, 0xFF]` | `"R1: 10000, R2: 20000"` |
| `test_msg_ok_cfg_with_override` | `msg_id=MSG_OK_CFG, params=[10000, 20000, 0x02]` | `"R1: 10000, R2: 20000, Override HW: Rev 2.0-class"` |
| `test_msg_info_hw` | `msg_id=MSG_INFO_HW, params=[0x02]` | `"HW: Rev 2.0-class"` |
| `test_msg_info_physical_hw` | `msg_id=MSG_INFO_PHYSICAL_HW, params=[0x00]` | `"Physical HW: Rev 0"` |
| `test_msg_info_cmd` | `msg_id=MSG_INFO_CMD, params=[0x01]` | `"Cmd: 0x01 (READ)"` |
| `test_msg_debug_dbg_cmd` | `msg_id=MSG_DEBUG, params=[DBG_CMD, bytes([0x02])]` | `"Cmd: 0x02 (WRITE)"` |
| `test_msg_data_chunk` | `msg_id=MSG_DATA_CHUNK, params=[b"..." (512 bytes)]` | `"<chunk: 512 bytes>"` |
| `test_none_fallthrough` | `msg_id=0x99 (unknown), params=[], entry=mock` | `None` (caller uses catalog format string) |

All tests import `from firestarter.codec import format_message` — not from `serial_comm`. The test does NOT need any serial fixtures.

#### tests/test_address_parser.py — covers `parse_address` and `parse_size`

| Test | Input | Expected |
|------|-------|---------|
| `test_parse_address_hex_0x` | `"0x10000"` | `65536` |
| `test_parse_address_hex_uppercase` | `"0X1A2B"` | `6699` |
| `test_parse_address_decimal` | `"512"` | `512` |
| `test_parse_address_none` | `None` | `None` |
| `test_parse_address_invalid` | `"not_a_number"` | raises `ValueError` |
| `test_parse_address_empty` | `""` | raises `ValueError` |
| `test_parse_size_hex` | `"0x8000"` | `32768` |
| `test_parse_size_decimal` | `"1024"` | `1024` |
| `test_parse_size_none` | `None` | `None` |
| `test_parse_size_invalid` | `"abc"` | raises `ValueError` |

### How test_decoder.py Proves frame_parser + Repointed _decode_id_frame Still Work (D-07)

`test_decoder.py` tests `SerialCommunicator._read_and_parse_lines()` end-to-end using the `make_comm` fixture (BytesIO-backed, no real serial). It feeds binary wire frames constructed by `conftest.build_frame` and asserts that `Response` objects emerge with correct `type` and `message` fields.

After Phase 38:
- The physical decode logic (`_build_crc8_table`, `_crc8_ccitt`, `_decode_param`) lives in `frame_parser.py`, imported by `serial_comm.py`.
- `_decode_id_frame` stays in `serial_comm.py`, now calling `codec.format_message` instead of `self._format_message`, and using the imported frame_parser primitives.
- `_read_and_parse_lines` is UNTOUCHED.
- `serial_comm.py` re-exports `MAGIC_PREAMBLE`, `LogMessage`, `Response`, `_crc8_ccitt` for `test_decoder.py`'s imports (lines 50–55).

If `test_decoder.py` passes unchanged, it proves: (1) the frame primitives in `frame_parser.py` are functionally equivalent to the originals; (2) `_decode_id_frame`'s repointed internal calls produce identical output; (3) the `Response` namedtuple shape is preserved; (4) `_read_and_parse_lines` is unmodified. This is a complete behavior-preservation proof for STRUCT-01 and the relevant parts of STRUCT-02.

### Reviewer Checklist for "Zero Behavior Change"

A reviewer confirms behavior preservation by checking all of the following:

1. **Suite green:** `python -m pytest --tb=short -q` exits 0 after EACH extraction commit.
2. **Snapshot diff empty:** `git diff tests/__snapshots__/` is empty after each extraction commit.
3. **Git diff is moves-and-repoints only:** `git diff HEAD~1` shows no logic edits — only: (a) new file with copied symbols, (b) source file with original symbols removed + re-export line(s) added, (c) import sites updated. No conditional branches added/removed. No value changes.
4. **xfailed tests remain xfailed:** `test_build_arg_flags_force_truthiness_not_existence` and `test_eprom_operation_error_not_labeled_as_communication_error` must remain xfailed (not xpassed). If they flip to xpassed, Phase 38 accidentally fixed a Phase 41/42 bug.
5. **mypy watermark not exceeded:** `python tools/check_mypy_watermark.py` exits 0.
6. **ruff gate green:** `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` both exit 0.

---

## Common Pitfalls

### Pitfall 1: Deleting Symbols From serial_comm.py Before Adding Re-Exports

**What goes wrong:** `test_decoder.py` raises `ImportError` on `from firestarter.serial_comm import MAGIC_PREAMBLE, LogMessage, Response, _crc8_ccitt`. Suite fails immediately.

**Why it happens:** CONTEXT D-07 says "test_decoder.py passes unchanged" but does not spell out the re-export mechanism. An implementor might move the symbols and then run the suite — which then fails.

**How to avoid:** In the same commit that creates `frame_parser.py`, also add re-export lines to `serial_comm.py`. Run suite. Green. Then (optionally) remove the originals from `serial_comm.py` in a follow-up commit — the re-exports make this safe.

**Warning signs:** Any `ImportError` in `test_decoder.py` after a frame_parser extraction commit.

### Pitfall 2: codec.py Missing `_decode_param` Import

**What goes wrong:** `format_message` raises `NameError: name '_decode_param' is not defined` at runtime when any MSG_DEBUG frame arrives. Tests that do not exercise MSG_DEBUG would still pass — giving false confidence.

**Why it happens:** D-08 lists "constants.py + messages.py only" as codec's imports, omitting `frame_parser._decode_param`.

**How to avoid:** Include `from firestarter.frame_parser import _decode_param` in `codec.py`. The existing `test_decoder.py` does exercise MSG_DEBUG paths (the DBG_CMD test), so this pitfall WOULD be caught by the suite — but only if the test runner actually hits a MSG_DEBUG frame.

**Warning signs:** NameError on `_decode_param` in codec module imports at test time.

### Pitfall 3: Star-Import Noqa Annotations Lost During Edit

**What goes wrong:** After touching `serial_comm.py`, ruff reports new F405 violations on remaining `FLAG_*`, `BAUD_RATE`, etc. references. The CI gate fails.

**Why it happens:** Editor auto-removes "unused" `# noqa: F405` annotations when the code they annotated moves away.

**How to avoid:** Only remove `# noqa: F405` from lines that no longer contain starred-import references. Keep all remaining `# noqa: F403/F405` suppressions until Phase 39 removes the star-import itself.

**Warning signs:** `ruff check firestarter/serial_comm.py` fails after extraction commit.

### Pitfall 4: Forgetting `# noqa: F401` on Re-Export Lines

**What goes wrong:** ruff F401 ("imported but unused") fires on the re-export lines in `serial_comm.py` (e.g. `from firestarter.frame_parser import MAGIC_PREAMBLE  # noqa: F401`).

**Why it happens:** Re-exports look like unused imports to ruff if they are not referenced in the module body.

**How to avoid:** Add `# noqa: F401` to each re-export line, or use `__all__` to explicitly export them.

### Pitfall 5: `globals()` Replacement Changes Error Type on Unknown Command

**What goes wrong:** The old `[k for k, v in globals().items() if v == cmd][0]` raises `IndexError` for an unknown `cmd`. The new `COMMAND_NAMES[cmd]` raises `KeyError`. Both are unhandled.

**Why it happens:** Both are equally fatal in practice (neither is caught), but a caller catching `IndexError` would miss the `KeyError`.

**How to avoid:** Verify no callers catch `IndexError` around `_setup_operation` or `_operation_context`. (Confirmed: they only catch `ProgrammerNotFoundError` and `SerialError`.) The change is behavior-identical for the common case.

---

## Code Examples

### exceptions.py (complete structure)

```python
# firestarter/exceptions.py
"""
Application exception hierarchy for Firestarter host CLI.
All application exceptions live here. AvrdudeNotFoundError and
AvrdudeConfigNotFoundError stay in avr_tool.py (different domain).
See CONTEXT.md Phase 38 D-01/D-02 for rationale.
"""


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


class EpromOperationError(Exception):
    """Custom exception for EPROM operation failures."""
    pass


class HardwareOperationError(Exception):
    """Custom exception for hardware operation failures."""
    pass


class FirmwareOperationError(Exception):
    """Custom exception for firmware operation failures."""
    pass


class ChipNotFoundError(Exception):
    """Raised when a chip name cannot be resolved in the database.
    Wired in Phase 39 (chip_resolver.py).
    """
    pass
```

### frame_parser.py (structure)

```python
# firestarter/frame_parser.py
"""
Wire-frame primitives: CRC8-CCITT, parameter decoding, and structured
response types. Stdlib + typing only — no package-internal imports.
"""

import struct
from collections import namedtuple
from typing import Any, Tuple  # noqa: UP035

Response = namedtuple("Response", ["type", "message", "payload"], defaults=[None])
LogMessage = namedtuple("LogMessage", ["severity", "text", "id", "payload"], defaults=[None])
MAGIC_PREAMBLE: bytes = b"\xaa\x55\xaa\x55"

def _build_crc8_table() -> bytes: ...
_CRC8_CCITT_TABLE: bytes = _build_crc8_table()
def _crc8_ccitt(data: bytes) -> int: ...
def _decode_param(ptype: str, buf: bytes, cursor: int) -> Tuple[Any, int]: ...  # noqa: UP006
```

### serial_comm.py re-exports (after frame_parser extraction)

```python
# In serial_comm.py — add immediately after frame_parser is created
from firestarter.frame_parser import (  # noqa: F401  — re-exports for test_decoder.py
    MAGIC_PREAMBLE,
    LogMessage,
    Response,
    _crc8_ccitt,
)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `globals()` reverse-lookup for cmd name | `COMMAND_NAMES[cmd]` dict lookup | Phase 38 | Eliminates fragility from FLAG_*/other int collisions |
| Exception classes scattered across modules | Consolidated `exceptions.py` | Phase 38 | All import sites repoint; enables Phase 39 chip_resolver |
| `_format_message` as private method | `codec.format_message` as public function | Phase 38 | Testable without SerialCommunicator instance |
| Inline address/size parsing in `_setup_operation` | `address_parser.parse_address/parse_size` | Phase 38 | Independently unit-tested; explicit ValueError contract |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `FirmwareOperationError` is truly orphaned (never raised or caught) | Scout Verification | If there IS a raise site, the repoint list is incomplete — but grep across all .py files confirmed zero sites |
| A2 | `HardwareOperationError` is never raised (only caught in hardware.py:240 as part of a tuple) | Scout Verification | If raised elsewhere, planner has an incomplete repoint list |

**Note on A2:** `hardware.py:240` catches `HardwareOperationError` in a tuple `(ProgrammerNotFoundError, SerialError, SerialTimeoutError, HardwareOperationError)` — the exception IS listed in the except clause, presumably for future use or defensive catch, even though no code in hardware.py raises it. After repoint, the except clause imports from `exceptions.py` instead.

---

## Open Questions

1. **`_REVISION_SILKSCREEN` uses REVISION_* via star-import in serial_comm.py; when it moves to codec.py it needs explicit imports of all 7 REVISION_* names.**
   - What we know: All 7 names are: `REVISION_0, REVISION_1, REVISION_2_0, REVISION_2_1, REVISION_2_2, REVISION_2_3, REVISION_UNKNOWN`
   - What's unclear: Whether the planner wants to use explicit named imports or keep a partial star-import in codec.py until Phase 39
   - Recommendation: Use explicit named imports in codec.py (it's a new file; no legacy star-import to preserve). This sets the right pattern.

2. **`_operation_context` also uses `globals()` at line 232 for `operation_name` logging, but this local is yielded out in `yield command_dict, buffer_size, operation_name`. Does the planner want to keep the `operation_name` local in `_operation_context` or unify the replacement?**
   - What we know: Both sites (170 and 232) perform the identical globals() lookup. Line 170 is in `_setup_operation`; line 232 is in `_operation_context`.
   - What's unclear: D-15 says "replace both" — confirmed. Both become `COMMAND_NAMES[cmd]`.
   - Recommendation: Replace both with `COMMAND_NAMES[cmd]` per D-15. No ambiguity.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python pytest | All tests | ✓ | (installed in venv) | — |
| syrupy | Snapshot tests | ✓ | (installed in venv) | — |
| ruff | Lint gate | ✓ | (installed, all checks pass) | — |
| mypy | Type gate | ✓ | watermark=44 | — |

All tooling installed and green. No missing dependencies.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (with syrupy for snapshots) |
| Config file | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `python -m pytest --tb=short -q` |
| Full suite command | `python -m pytest --tb=short -q --cov=firestarter` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| STRUCT-01 | `frame_parser.py` pure primitives; `test_decoder.py` unchanged | integration | `pytest tests/test_decoder.py -x` | ✅ (test_decoder.py exists) |
| STRUCT-02 | `codec.format_message` correct for all catalog message shapes | unit | `pytest tests/test_codec.py -x` | ❌ Wave 0 |
| STRUCT-03 | `parse_address`/`parse_size` hex/decimal/None/invalid | unit | `pytest tests/test_address_parser.py -x` | ❌ Wave 0 |
| STRUCT-04 | Exception imports work from exceptions.py; existing tests pass | integration | `pytest -x` (full suite) | ✅ (via full suite) |
| STRUCT-05 | Dead code gone; suite still passes; no read_data_block caller | integration | `pytest -x` + `grep -c "read_data_block" serial_comm.py` should return 0 | ✅ (via full suite) |

### Sampling Rate

- **Per extraction commit:** `python -m pytest --tb=short -q` (full suite, ~14s, no hardware)
- **Per wave merge:** `python -m pytest --tb=short -q --cov=firestarter` + `python tools/check_mypy_watermark.py`
- **Phase gate:** Full suite green + snapshot diff empty + ruff clean + mypy at or below watermark before `/gsd-verify-work`

### Wave 0 Gaps (test files to create before implementation)

- [ ] `firestarter_app/tests/test_codec.py` — covers STRUCT-02 (`format_message` with all catalog message fixtures from D-08)
- [ ] `firestarter_app/tests/test_address_parser.py` — covers STRUCT-03 (hex/decimal/None/invalid inputs for both functions)

*(No new conftest fixtures needed — test_codec.py imports directly from codec; test_address_parser.py imports directly from address_parser. No serial fixtures required.)*

---

## Security Domain

This phase is a pure code-structure refactor — no new network access, no authentication, no serialization of external data, no cryptography changes. The CRC8 computation moved to `frame_parser.py` is not a security primitive — it is a wire-framing integrity check for serial communication with local hardware.

ASVS categories V2/V3/V4/V5/V6 do not apply to this extraction phase. No security review required.

---

## Sources

### Primary (HIGH confidence)
- Live source reads: `firestarter_app/firestarter/serial_comm.py` (1066 lines), `eprom_operations.py`, `firmware.py`, `hardware.py`, `constants.py`, `messages.py`, `avr_tool.py` — [VERIFIED: Read tool]
- `python -m pytest --tb=no 2>&1`: 162 passed, 2 xfailed, 29 snapshots — [VERIFIED: Bash]
- `grep -rn "read_data_block"`: exactly one hit (its own def) — [VERIFIED: Bash]
- `grep -n "globals()"` in eprom_operations.py: lines 170 and 232 — [VERIFIED: Bash]
- AST analysis of `_format_message`: zero `self.` references; calls `_decode_param` at line 428 — [VERIFIED: Python AST]
- `COMMAND_NAMES` values vs old globals() pattern: 13/13 exact match — [VERIFIED: live Python execution]
- mypy watermark: 44 errors (`python tools/check_mypy_watermark.py` exits 0) — [VERIFIED: Bash]
- `ruff check firestarter/`: All checks passed — [VERIFIED: Bash]
- `grep "from firestarter" firestarter/messages.py`: no output — [VERIFIED: Bash]

### Secondary (MEDIUM confidence)
- `.planning/phases/38-low-risk-extractions/38-CONTEXT.md` — locked decisions D-01..D-16 read in full
- `.planning/phases/36-characterization-test-baseline/36-CONTEXT.md` — safety net baseline confirmed
- `.planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md` — ruff/mypy gate details confirmed

---

## Metadata

**Confidence breakdown:**
- Structural claims (read_data_block, globals(), self-references, imports): HIGH — verified against live source
- Test baseline (162+2+29): HIGH — `pytest` run confirmed
- D-08 gap (codec needs frame_parser import): HIGH — confirmed by AST analysis and live grep
- test_decoder.py import landmine: HIGH — confirmed by reading lines 50–55 of test_decoder.py
- Exception site enumeration: HIGH — comprehensive grep across all .py files

**Research date:** 2026-05-27
**Valid until:** 2026-06-27 (stable codebase; all claims sourced from the live branch)

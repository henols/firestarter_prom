# Architecture Research

**Domain:** Python host CLI refactor — structural cleanup (v1.8)
**Researched:** 2026-05-27
**Confidence:** HIGH (derived entirely from direct codebase reading)

---

## Current State: The Spaghetti Map

Before laying out the target, the specific coupling violations driving the work:

| Coupling | Location | Impact |
|---|---|---|
| DB lookup boilerplate 9x repeated | main.py L651, L671, L692, L710, L724, L741, L748, L857, L904 | Any DB API change ripples to 9 call sites |
| `from firestarter.constants import *` in 4 modules | main.py, serial_comm.py, eprom_operations.py, database.py | Star imports shadow names silently; no IDE support |
| Firmware handshake embedded in port-discovery | serial_comm.py `_probe_port` L800-916 | Cannot test port scan without triggering FW handshake; FW check bleeds into transport |
| Address/size string parsing inside `_setup_operation` | eprom_operations.py L182-196 | Business-logic parsing inside a method that also opens serial |
| `_format_message` sentinel logic in `SerialCommunicator` | serial_comm.py L336-435 | Message rendering coupled to the object that owns the socket |
| `_REVISION_SILKSCREEN` dict in serial_comm.py | serial_comm.py L173-181 | Revision display logic in transport layer; should live near `constants.py` |
| `_CRC8_TABLE` + `_decode_param` + `_decode_id_frame` in `SerialCommunicator` | serial_comm.py L55-541 | Frame-decode logic untestable without `SerialCommunicator` instance |
| `read_data_block` legacy path | serial_comm.py L962-997 | Dead code (W-04 MSG_DATA_CHUNK replaced it); still compiles and wastes readers |
| `pin_conversions` hardcoded dict AND `pinouts.json` | database.py L68-133 + data/pinouts.json | Two sources of truth for the same physical mapping |
| `globals()` introspection for command names | eprom_operations.py L167 | Fragile, slow; `COMMAND_NAMES` dict already exists in constants.py |
| argparse `args` duck-typed via `getattr(..., False)` | main.py L497-506 | Build-arg-flags is positionally fragile; Click's typed params fix this |

---

## Target Module Map (Flat Layout)

All files remain siblings in `firestarter_app/firestarter/`. No subpackages.

### New modules to introduce

| Module | Lines (est.) | Owns | Does NOT own |
|---|---|---|---|
| `chip_resolver.py` | ~80 | `resolve_chip(name) -> ChipData` — the single function that calls `db.get_eprom` + `db.convert_to_programmer` + raises `ChipNotFoundError`; used by every handler | DB loading, serial, argparse |
| `frame_parser.py` | ~200 | `_build_crc8_table`, `_crc8_ccitt`, `_decode_param`, `_decode_id_frame`, `Response`, `LogMessage`, `MAGIC_PREAMBLE`, `_CRC8_CCITT_TABLE` | Socket I/O, logging, catalog imports |
| `codec.py` | ~120 | `_format_message`, `_REVISION_SILKSCREEN`; takes a decoded `LogMessage` and returns a display string; imports from `messages.py` and `constants.py` | Frame parsing, socket I/O |
| `address_parser.py` | ~40 | `parse_address(s) -> int`, `parse_size(s) -> int` — hex/decimal string parsing used by read/write/verify/dev commands | CLI, DB, serial |
| `cli_handlers.py` | ~400 | One Click command function per top-level command group (`cmd_read`, `cmd_write`, `cmd_verify`, `cmd_erase`, `cmd_blank`, `cmd_id`, `cmd_vpp`, `cmd_vpe`, `cmd_hw`, `cmd_config`, `cmd_list`, `cmd_search`, `cmd_info`, `cmd_fw`, `cmd_dev`); each calls `resolve_chip` once, then delegates to the matching operator | DB loading, serial, argparse |
| `exceptions.py` | ~30 | All application exception classes in one place (`ChipNotFoundError`, `EpromOperationError`, `SerialError`, `SerialTimeoutError`, `ProgrammerNotFoundError`, `FirmwareOutdatedError`, `HardwareOperationError`) | Business logic |

### Existing modules: what they shed and what they keep

| Module | Keep | Shed / Move to |
|---|---|---|
| `main.py` | Click app object, global options (`-v`, `-p`, `--version`), `argcomplete` hook, `signal` handler, logging setup, entry-point call | All `if args.command ==` branches → `cli_handlers.py`; `build_arg_flags` → `cli_handlers.py`; `EpromCompleter` can stay or move to `cli_handlers.py` |
| `serial_comm.py` | `SerialCommunicator` class (socket lifecycle, `send_*`, `get_response`, `expect_ack`, `consume_remaining_input`, `disconnect`, `find_and_connect`, `_probe_port`, `_list_potential_ports`); `_read_and_parse_lines` generator | Frame decode logic → `frame_parser.py`; message rendering → `codec.py`; `_REVISION_SILKSCREEN` → `codec.py`; `read_data_block` dead-code DELETE; `Response`/`LogMessage` namedtuples → `frame_parser.py` |
| `eprom_operations.py` | `EpromOperator` class, `_run_state_machine`, `_execute_phase`, `_main_phase_*` handlers, `consistency_check_eprom`, all public operation methods | Address/size string parsing → `address_parser.py`; `build_flags` → `cli_handlers.py` or stays; `globals()` introspection → replace with `COMMAND_NAMES` lookup |
| `database.py` | `EpromDatabase` singleton, `get_eprom`, `get_eproms`, `get_eprom_config`, `convert_to_programmer`, `search_eprom`, `search_chip_id`, `get_bus_config`, `get_adapter_table`, `_map_data`, `_merge_*`, `pin_conversions` | No shedding of logic; single-source-of-truth audit: reconcile `pin_conversions` dict against `pinouts.json` or document which is authoritative |
| `constants.py` | All `COMMAND_*`, `FLAG_*`, `CTRL_*`, `REVISION_*`, `BAUD_RATE`, `BUFFER_SIZE`, `LEONARDO_BUFFER_SIZE`, GitHub URL constants | Nothing: this is the firmware-contract module; adding `COMMAND_FW_VERSION = 13` (currently missing from constants, referenced as `COMMAND_FW_VERSION` in serial_comm.py line 822) |
| `messages.py` | Generated catalog — do not hand-edit; codegen owns this | Nothing |
| `firmware.py` | `FirmwareManager`, `FIRMWARE_VERSION_RE`; minimal changes needed | `_validate_firmware_version` currently in `main.py` → move to `firmware.py` |
| `hardware.py` | `HardwareManager` | `HardwareOperationError` → `exceptions.py` |
| `config.py` | `ConfigManager` singleton | Nothing |
| `eprom_info.py` | `EpromConsolePresenter`, `print_eprom_list_table` | Nothing |
| `ic_layout.py` | Pin layout rendering | Nothing |
| `logging_utils.py` | `SingleLineStatusHandler` | Nothing |
| `avr_tool.py` | `Avrdude` | Nothing |
| `utils.py` | `extract_hex_to_decimal` | Nothing |

---

## Layer Boundaries

```
┌──────────────────────────────────────────────────────────┐
│                      CLI Layer                            │
│  main.py (Click app + global options + logging setup)    │
│  cli_handlers.py (one @click.command per user command)   │
│  address_parser.py (hex/decimal string parsing)          │
└────────────────────┬─────────────────────────────────────┘
                     │ calls (typed Python args, not raw string)
┌────────────────────▼─────────────────────────────────────┐
│                   Service/Ops Layer                        │
│  chip_resolver.py  (name → ChipData; raises on missing)  │
│  eprom_operations.py  (EpromOperator state machine)       │
│  hardware.py (HardwareManager)                           │
│  firmware.py (FirmwareManager)                           │
│  database.py (EpromDatabase singleton)                   │
│  eprom_info.py (display/presentation)                    │
└────────────────────┬─────────────────────────────────────┘
                     │ calls (structured dicts + bytes)
┌────────────────────▼─────────────────────────────────────┐
│                  Transport Layer                           │
│  serial_comm.py  (SerialCommunicator: socket + probe)    │
│  frame_parser.py (CRC + decode; pure functions)          │
│  codec.py        (LogMessage → display string)           │
└──────────────────────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│                  Shared / Cross-Cutting                    │
│  constants.py     (firmware-contract constants)           │
│  exceptions.py    (all exception types)                   │
│  messages.py      (generated catalog — read-only)        │
│  config.py        (ConfigManager)                        │
│  logging_utils.py (SingleLineStatusHandler)              │
└──────────────────────────────────────────────────────────┘
```

**Boundary rules that must not be violated:**

1. CLI layer never imports from `serial_comm.py`, `frame_parser.py`, or `codec.py` directly.
2. Transport layer never imports from `database.py`, `eprom_operations.py`, or `firmware.py`.
3. `frame_parser.py` has no imports from within the `firestarter` package (only stdlib + typing).
4. `codec.py` imports from `constants.py` and `messages.py` only.
5. `chip_resolver.py` imports from `database.py` and `exceptions.py` only.

---

## Firmware-Contract Guard

The firmware-contract is the set of values in `constants.py` that must stay byte-identical to the corresponding `firestarter/include/firestarter.h` (and `rurp_pinout.h`, `rurp_shield.h`) values.

**Existing test:** `tests/test_revision_constants_parity.py` (44 lines) — covers `REVISION_*` constants. This is the pattern to extend.

**Target:** A single `tests/test_firmware_contract_parity.py` that asserts:
- Every `COMMAND_*` value matches the corresponding `CMD_*` in `firestarter.h`
- Every `FLAG_*` value matches `FLAG_*` in `firestarter.h`
- Every `CTRL_*` value matches its `rurp_pinout.h` counterpart
- Every `REVISION_*` value matches `rurp_shield.h`

Implementation pattern: the test directly reads `firestarter/include/firestarter.h` (and sibling headers) using a `#define` regex extractor, builds a `{name: value}` dict, then compares against `constants.py` values. The firmware sub-repo is at a known path relative to the test file (`../../firestarter/include/`). The test is marked `skipif` when that path is absent (CI without the firmware checkout), but runs always in the dev container where both sub-repos are present.

This replaces the current ad-hoc "keep in sync per CLAUDE.md" comment with a mechanical gate.

---

## Migration Mechanics: High-Risk Areas

### 1. argparse → Click Incremental Migration

**Why incremental is safe:** Click commands are composable. The existing argparse `main()` and the new Click app can co-exist during transition by keeping `main.py` as the entry point and having it conditionally dispatch.

**Recommended sequence:**
1. Add `click` to `pyproject.toml` dependencies.
2. In `main.py`, replace the argparse top-level parser with a Click `@click.group()` decorated `cli()` function plus the three global options (`-v`, `--port`, `--version`).
3. Migrate one low-risk command first: `firestarter list` (no serial, no chip lookup, DB-only). This proves the Click entry-point wiring.
4. Migrate `info`, `search` (DB-only commands) — still no serial.
5. Migrate `vpp`, `vpe`, `hw`, `config` (serial but no chip lookup) — introduces the `HardwareManager` path through Click.
6. Migrate `fw` — complex flags but no serial handshake; tests can mock GitHub API.
7. Migrate `read`, `write`, `verify`, `blank`, `id`, `erase` — all share the `resolve_chip` helper; migrate together so the helper only needs to be written once.
8. Migrate `dev` (sub-command group with nested `read`, `reg`, `addr`, `consistency-check`).

**Command surface preservation:** For each argparse argument, verify the Click parameter name produces the identical Python attribute. The most likely divergence points:
- argparse `dest="blank_check"` (from `--no-blank-check`) — Click requires `is_flag=True, default=True` with careful naming.
- argparse `nargs="?"` (optional positional, `output_file`) — Click uses `required=False`.
- `argcomplete` autocomplete — Click has its own completion; `argcomplete` can be dropped once Click's `click_completion` or the built-in `shell_complete` is wired.
- The `fw_parser.error("--json requires --list")` post-parse validation — implement as a Click callback or a `with_appcontext` check.
- `--firmware-version` type validator `_validate_firmware_version` — move to `firmware.py` and wire as a `click.option(type=click.STRING, callback=...)`.

### 2. Splitting serial_comm.py Without Breaking Timing/Buffering

**The risk:** `_read_and_parse_lines` is a generator that drives real serial I/O with strict timing. Any refactor that changes its call graph or introduces an extra function boundary could alter buffering behavior.

**Safe split strategy:** Extract by moving code, not by adding indirection in the hot path.

- Move `_build_crc8_table`, `_crc8_ccitt`, `_decode_param`, `_decode_id_frame`, `Response`, `LogMessage`, `MAGIC_PREAMBLE` to `frame_parser.py` as module-level functions and constants.
- `_read_and_parse_lines` stays in `SerialCommunicator` and calls `frame_parser._decode_id_frame(frame_len, body)` — one function call, no generator boundary crossed.
- `_format_message` and `_REVISION_SILKSCREEN` move to `codec.py`. `_decode_id_frame` (in `frame_parser.py`) calls `codec.format_message(...)` for the sentinel-aware render step.
- The `SerialCommunicator` class's public API (`find_and_connect`, `get_response`, `expect_ack`, `send_*`, `consume_remaining_input`, `disconnect`) does not change at all.

The timing-critical path (`connection.read(1)` → accumulator → magic-preamble check → frame read → `_decode_id_frame`) has zero new function call overhead. The extracted functions are called at exactly the same points, just imported from a different module.

**Buffering invariant:** `connection.read(frame_len)` and `connection.read(2)` (len field) are synchronous pyserial reads. Their semantics are unchanged because they're inside `SerialCommunicator._read_and_parse_lines` which stays intact. The only thing that moves is the pure-compute decode logic.

**Checksum path:** `read_data_block` (serial_comm.py L962-997) is dead code — it was the pre-W-04 binary data path. MSG_DATA_CHUNK (the ID-frame path) replaced it entirely. Verify by tracing all callers: none exist outside the module. Delete it with a comment citing the W-04 migration.

### 3. Frame Parsing Testable Without Hardware

**Current state:** `conftest.py` already establishes the `_FakeSerial` + `make_comm` pattern. `test_decoder.py` exercises `_read_and_parse_lines` with binary frames fed through `fake_serial.feed()`. This infrastructure is correct and reusable.

**After extraction:** `frame_parser.py` functions are pure (take `bytes`, return `LogMessage` or `None`). They can be imported and tested directly without the `make_comm` indirection:

```python
# test_frame_parser.py — no serial, no make_comm needed
from firestarter.frame_parser import _decode_id_frame, _crc8_ccitt
frame_body = bytes([msg_id]) + params + bytes([crc])
result = _decode_id_frame(len(frame_body), frame_body)
assert result.text == "expected"
```

`codec.py` is also pure (takes msg_id + params list, returns str). Its tests need `messages.py` (generated catalog) but no serial.

`_read_and_parse_lines` tests continue to use `make_comm` + `fake_serial.feed()` as today.

---

## Firmware Handshake: Where It Lives After Refactor

**Current (bad):** `_probe_port` in `SerialCommunicator` does both port-discovery and FW version validation. FW version check is 50 lines of business logic in the transport layer.

**Target:** The FW version check stays in `_probe_port` because it is inextricably linked to the serial handshake sequence — the probe must send `CMD_FW_VERSION`, drain two acks, and parse the version string before it can declare the port valid. Extracting it to a separate function that `_probe_port` calls is the right level of refactor.

**Concrete change:** Extract the version-string parsing and version-sufficiency check to `SerialCommunicator._validate_firmware_version(version_str: str) -> None` (raises `FirmwareOutdatedError` on failure). This makes the version logic unit-testable without a fake serial at all:

```python
# test_fw_version.py
from firestarter.serial_comm import SerialCommunicator
with pytest.raises(FirmwareOutdatedError):
    SerialCommunicator._validate_firmware_version("2.9.9")
SerialCommunicator._validate_firmware_version("3.0.0")  # must not raise
```

The `_probe_port` method continues to own the send/drain/recv sequence. The firmware-version concern does not move out of `serial_comm.py` to a service layer — that would require serial_comm.py to call upward, creating a cycle.

---

## Chip Resolution: The `chip_resolver.py` Service

This is the highest-leverage structural change. Currently every EPROM-accepting command handler in `main.py` has this boilerplate:

```python
full_eprom_data = db_instance.get_eprom(args.eprom)
eprom_data = None
if full_eprom_data:
    eprom_data = db_instance.convert_to_programmer(full_eprom_data)
if not eprom_data:
    logger.error(f"EPROM '{args.eprom}' not found in database.")
    return 1
```

Nine occurrences. Replace with:

```python
# chip_resolver.py
from firestarter.database import EpromDatabase
from firestarter.exceptions import ChipNotFoundError

def resolve_chip(name: str) -> dict:
    """Resolve chip name to programmer-ready dict. Raises ChipNotFoundError."""
    db = EpromDatabase()
    full = db.get_eprom(name)
    if not full:
        raise ChipNotFoundError(f"EPROM '{name}' not found in database.")
    return db.convert_to_programmer(full)
```

Each handler in `cli_handlers.py` calls `resolve_chip(eprom_name)` once and passes the result to the operator. The `ChipNotFoundError` is caught at the Click command boundary and converted to `sys.exit(1)`. This is a pure de-duplication with no behavior change.

---

## Address Parsing: The `address_parser.py` Module

Currently inside `EpromOperator._setup_operation` at lines 182-196:

```python
if address:
    try:
        addr = int(address, 16) if "0x" in address.lower() else int(address)
        command_dict["address"] = addr
    except ValueError:
        logger.error(f"Invalid address format: {address}")
        return None, 0
```

This mixes input validation with command-dict assembly inside a method that also opens serial. The error path returns `(None, 0)` which the caller must check — a mixed error signal.

**Target:** Move to `address_parser.py`:

```python
def parse_address(s: str | None) -> int | None:
    """Parse decimal or 0x-prefixed hex address string. Returns int or None."""
    if s is None:
        return None
    try:
        return int(s, 16) if "0x" in s.lower() else int(s)
    except ValueError:
        raise ValueError(f"Invalid address format: {s!r}")
```

CLI handlers call `parse_address()` before passing to the operator. Validation errors surface at the CLI layer with a proper Click `UsageError` (or caught and printed before the serial connection is attempted). `_setup_operation` receives `address: int | None` directly.

---

## DIP→RURP Pin Mapping: Single Source of Truth

**Current:** `database.py` has a hardcoded `pin_conversions` dict (lines 68-133) AND `data/pinouts.json` defines per-pinout-key address bus pins. The `get_bus_config` method joins them.

**Verdict:** These serve complementary roles — `pin_conversions` maps DIP socket position to RURP bus line numbers (physical board wiring), while `pinouts.json` maps chip-function names (A0, A1, OE, CE) to DIP pin numbers (chip-specific). Neither is redundant. The "two sources of truth" observation is correct but the fix is documentation, not elimination.

**Action for v1.8:** Add a docstring to `pin_conversions` explicitly stating it encodes RURP Rev 2.2 board wiring (physical socket → bus line), distinct from `pinouts.json` which encodes chip DIP pinout (function → socket position). No code change needed; this is a clarity fix. Flag as a v1.9 deep-dive if the Rev 0 address-jitter bug (Bug A) turns out to correlate with pin_conversions assumptions.

---

## Dependency-Ordered Build Sequence (Phase Decomposition)

### Phase 36: Characterization Test Baseline

**Goal:** Establish a safety net before any structural change. Tests must fail loudly if behavior regresses.

**Work:**
- Write `tests/test_chip_resolver.py` — parametrized over real chip names from `chip_database.json`; verifies `resolve_chip("W27C512")` returns a dict with the required wire-protocol keys.
- Write `tests/test_address_parser.py` — covers hex, decimal, None, invalid.
- Write `tests/test_firmware_contract_parity.py` — extends the existing `test_revision_constants_parity.py` pattern to cover all `COMMAND_*` and `FLAG_*` values against `firestarter.h`. `skipif` when firmware checkout absent.
- Write `tests/test_eprom_database.py` — characterizes `EpromDatabase.get_eprom`, `convert_to_programmer`, `get_bus_config` against real JSON data.
- Wire ruff + black + mypy to `pyproject.toml` (no CI gate yet — just make them runnable). Baseline: run ruff/black/mypy against current code, record violation counts; these become the "pre-refactor watermark".

**Why first:** These tests encode the current contract. If they pass now and pass after each subsequent phase, no regressions were introduced.

**Dependencies:** None.

**Risk:** LOW (additive only; no existing code changes).

---

### Phase 37: Tooling Baseline + CI Gate

**Goal:** Ruff + black + mypy enforced in CI. Zero new violations permitted after this phase.

**Work:**
- Add `[tool.ruff]`, `[tool.black]`, `[tool.mypy]` sections to `pyproject.toml`.
- Run `black .` and `ruff --fix .` on the entire codebase (mechanical formatting; no logic changes).
- Resolve mypy errors reachable without structural changes (type: ignore annotations where stubs are missing; add return type annotations to trivially-typed functions).
- Add GitHub Actions step: `ruff check . && black --check . && mypy firestarter/`.
- Update `.github/workflows/` CI yaml (existing file already has pytest; add linting steps).

**Why here:** Formatting now prevents future phases from mixing logic changes with formatting churn in the same diff. The CI gate catches regressions immediately.

**Dependencies:** Phase 36 tests must pass under the new linting rules.

**Risk:** LOW (mechanical; no logic changes).

---

### Phase 38: Low-Risk Extractions (frame_parser + codec + address_parser + exceptions)

**Goal:** Extract pure-compute code with zero runtime behavior change. This is the safest structural change possible.

**Work:**
1. Create `firestarter/exceptions.py` — move all exception classes from their current homes (`SerialError`, `SerialTimeoutError`, `ProgrammerNotFoundError`, `FirmwareOutdatedError` from `serial_comm.py`; `EpromOperationError` from `eprom_operations.py`; `HardwareOperationError` from `hardware.py`). Update all import sites.
2. Create `firestarter/frame_parser.py` — move `_build_crc8_table`, `_crc8_ccitt`, `_decode_param`, `_decode_id_frame`, `Response`, `LogMessage`, `MAGIC_PREAMBLE`, `_CRC8_CCITT_TABLE`. Update `serial_comm.py` to import from `frame_parser`.
3. Create `firestarter/codec.py` — move `_format_message`, `_REVISION_SILKSCREEN`. Update `serial_comm.py` to import from `codec`. `_format_message` becomes `codec.format_message(msg_id, params, entry) -> str | None`.
4. Create `firestarter/address_parser.py` — implement `parse_address` and `parse_size`.
5. Delete `read_data_block` dead code from `serial_comm.py` (W-04 obsolete path). Add a commit comment citing the W-04 MSG_DATA_CHUNK migration.
6. Replace `globals()` introspection in `eprom_operations.py` L167 with `COMMAND_NAMES.get(cmd, str(cmd))`.

**Tests after this phase:** `test_decoder.py` must still pass unchanged (it tests the same `SerialCommunicator` surface). New `tests/test_frame_parser.py` and `tests/test_codec.py` exercise extracted logic directly without `make_comm`.

**Why before serial/CLI split:** These extractions are mechanical copy-paste-and-update. They prove the module boundaries before the riskier structural changes.

**Risk:** LOW-MEDIUM. The only real risk is missing an import site. Solved by running the full test suite after each file move.

---

### Phase 39: Database Cleanup + chip_resolver

**Goal:** Eliminate the 9x copy-paste chip-lookup pattern; establish clean DB layer.

**Work:**
1. Create `firestarter/chip_resolver.py` — implement `resolve_chip(name: str) -> dict`, `ChipNotFoundError` (or import from exceptions.py).
2. Add type hints and docstrings to `EpromDatabase` public methods.
3. Reconcile `pin_conversions` documentation (add the docstring per the single-source-of-truth analysis above).
4. Fix `_merge_databases` shallow-update bug if found: the current code uses `existing_names[manual_item["name"]].update(manual_item)` which is a shallow update — user overrides that change nested dicts may not propagate correctly.
5. Remove dead commented-out code blocks in `database.py` (the commented-out `keys_to_pop` block in `get_eprom`, L503-519).
6. Consolidate the `from firestarter.constants import *` star import to explicit named imports everywhere.

**Tests:** `test_chip_resolver.py` from Phase 36 is the acceptance gate.

**Risk:** LOW. DB layer has no serial coupling. The star-import cleanup is mechanical.

---

### Phase 40: Serial / Transport Restructure (High-Risk)

**Goal:** Clean up `serial_comm.py` to own only transport concerns after Phase 38 extractions. Introduce `_validate_firmware_version` as an extractable static method.

**Work:**
1. Extract `SerialCommunicator._validate_firmware_version(version_str: str) -> None` from `_probe_port`. This is a pure function (no self access needed); make it `@staticmethod`. Add `tests/test_fw_version_guard.py`.
2. Move remaining responsibility audit: after Phase 38 moves, `serial_comm.py` should contain only `SerialCommunicator` class, the port-discovery helpers, and the `_read_and_parse_lines` generator. Verify nothing else remains.
3. Add type hints to all public `SerialCommunicator` methods.
4. Clean up logging: replace `from firestarter.constants import *` with explicit named imports. Verify `COMMAND_NAMES` is imported explicitly (it's already re-imported on line 26 after the star import — remove the star import and keep only explicit names).
5. Address the `_log_rurp_feedback` / `NON_RESPONSE_PREFIXES` pattern: `STATE_MACHINE_PREFIXES` is an empty list that dead-code comments explain was removed. Delete it and the comment.

**Tests:** All existing `test_decoder.py` and `test_fwguard.py` tests must pass. New `test_fw_version_guard.py` adds direct coverage.

**Risk:** MEDIUM. `_read_and_parse_lines` is timing-sensitive; any change to it requires running against real hardware or the full `fake_serial` suite. The safe rule: after Phase 38 the generator was NOT touched; in Phase 40, only the surrounding class cleanup happens. The generator itself stays byte-for-byte identical unless a bug is found.

---

### Phase 41: CLI Migration argparse → Click

**Goal:** Replace `main.py`'s argparse dispatch with Click. Create `cli_handlers.py`.

**Work — in this exact order:**

1. Add `click` to `pyproject.toml` dependencies. Remove `argcomplete` dependency (Click handles completion differently; verify no other module uses it).
2. In `main.py`, create a `@click.group()` decorated `cli()` with `-v/--verbose`, `-p/--port`, `--version` global options. Keep `main()` as the entry point that calls `cli()` — entry-point in `pyproject.toml` stays `firestarter.main:main`.
3. Migrate `list` command: `@cli.command("list")` in `cli_handlers.py`. Verify `firestarter list` and `firestarter list --verified` produce identical output.
4. Migrate `info`, `search` (DB-only).
5. Migrate `vpp`, `vpe`, `hw`, `config` (serial, no chip lookup).
6. Migrate `fw` — transfer `_validate_firmware_version` to `firmware.py`; wire as Click param type. Migrate `_maybe_auto_route_to_pre` logic as a Click callback.
7. Migrate `read`, `write`, `verify`, `blank`, `id`, `erase` — all share `resolve_chip`. These six are the ones that use `build_arg_flags`; implement the Click equivalent as a shared helper `_build_operation_flags(force, vpe_as_vpp, blank_check) -> int` inside `cli_handlers.py`.
8. Migrate `dev` as a `@cli.group("dev")` with sub-commands.
9. Delete `build_arg_flags` from `main.py` after all callers migrated.
10. Remove the giant `if args.command == ...` dispatch chain.

**Click-specific gotchas to address during migration:**
- `--no-blank-check` → Click `is_flag=True` with `default=True` and `flag_value=False`. The attribute is `blank_check` (not `no_blank_check`).
- `output_file` optional positional → `@click.argument("output_file", required=False, default=None)`.
- `dev` nested sub-commands → `@dev_group.command("read")`, etc.
- Consistency-check `--keep-files`/`--no-keep-files` pair → `@click.option("--keep-files/--no-keep-files", default=True)`.

**Tests:** Add `tests/test_cli_commands.py` using Click's `CliRunner` — test each command's exit code and output with mocked operator and DB. This is the first time CLI dispatch is tested at all.

**Risk:** HIGH. This is the largest surface-area change. Mitigated by: (a) migrating in order (DB-only first, then serial), (b) Click's `CliRunner` enabling fast feedback, (c) Phase 36 characterization tests catching behavioral regressions.

---

### Phase 42: Error Handling Normalization + Quality Sweep

**Goal:** Consistent exception/exit-code convention; no bare excepts; type hints complete; dead code purged; naming normalization.

**Work:**
1. Audit all `except Exception` and bare `except:` clauses — replace with specific exception types or at minimum `except Exception as e` with logging.
2. Enforce exit-code convention: `sys.exit(0)` on success, `sys.exit(1)` on expected failure (chip not found, serial error), `sys.exit(2)` on usage error (wrong args). `consistency_check_eprom`'s 3-way int return is the documented exception and stays.
3. Add return type annotations to all public functions.
4. Add docstrings to all public classes and methods (1-liner minimum).
5. Remove dead imports and commented-out code throughout.
6. Run `ruff --fix` and `mypy` with strict settings; resolve remaining violations.
7. Normalize naming: e.g. `eprom_data_dict` parameter name appears in 8 operator method signatures — standardize to `chip_config: dict` or `programmer_data: dict`.
8. Verify `COMMAND_FW_VERSION` is defined in `constants.py` (it's referenced in `serial_comm.py` and `firmware.py` but appears absent from `constants.py` — `COMMAND_FW_VERSION = 13` needs adding alongside the other COMMAND_* constants).

**Tests:** No new tests expected; existing suite serves as the regression gate.

**Risk:** LOW-MEDIUM. Individual fixes are low-risk; the aggregate of many small changes in one phase can hide regressions. Mitigation: commit frequently within the phase; run tests after each logical chunk.

---

## Phase Summary Table

| Phase | Name | Risk | Primary Dependency | Outcome |
|---|---|---|---|---|
| 36 | Characterization Test Baseline | LOW | None | Safety net before any structural change |
| 37 | Tooling Baseline + CI Gate | LOW | 36 | ruff/black/mypy enforced in CI |
| 38 | Low-Risk Extractions | LOW-MED | 37 | frame_parser, codec, address_parser, exceptions extracted |
| 39 | Database Cleanup + chip_resolver | LOW | 38 | 9x copy-paste eliminated; DB layer clean |
| 40 | Serial/Transport Restructure | MEDIUM | 38 | serial_comm.py owns only transport; FW version guard testable |
| 41 | CLI Migration argparse→Click | HIGH | 39, 40 | Click replaces argparse; cli_handlers.py exists |
| 42 | Error Handling + Quality Sweep | LOW-MED | 41 | Consistent errors, types, docs, dead code removed |

**Why this order:**

- 36 and 37 come first because they have no prerequisites and create the feedback infrastructure everything else depends on.
- 38 before 39 and 40 because exception classes must exist before DB and serial layers can import from `exceptions.py`.
- 39 (DB) before 41 (CLI) because `chip_resolver.py` must exist before CLI handlers can use it.
- 40 (serial) before 41 (CLI) because CLI handlers import `SerialCommunicator` exceptions; the clean import surface from `exceptions.py` must be stable.
- 41 last among structural changes because it has the widest surface area and highest coupling to everything else.
- 42 last because it is a sweep over the whole codebase — performing it before the structural changes would require doing it twice.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Subpackage Creep

**What people do:** Group logically related modules into `firestarter/cli/`, `firestarter/transport/`, etc.
**Why it's wrong:** Violates the locked flat-layout constraint. Breaks git blame continuity. Doesn't add value in a 15-module package.
**Do this instead:** Keep all files as siblings; use import discipline and documented layer rules to enforce the boundaries.

### Anti-Pattern 2: Extracting Logic Into Abstract Base Classes

**What people do:** Create `BaseOperation` or `AbstractCommand` to eliminate the repeated operator-call pattern.
**Why it's wrong:** Over-engineering for a single-threaded CLI that runs one command per invocation. The Click command function approach already gives the right level of isolation.
**Do this instead:** Use the `resolve_chip` helper function and a local `_build_operation_flags` helper in `cli_handlers.py`. Shared logic is a function, not a class hierarchy.

### Anti-Pattern 3: Making frame_parser.py a Class

**What people do:** Wrap the CRC table and decode functions in a `FrameParser` class.
**Why it's wrong:** These are pure functions with no state. The CRC table is a module-level constant. A class adds indirection with zero benefit.
**Do this instead:** Module-level functions and constants. `_decode_id_frame(frame_len, body) -> LogMessage | None` is called from `SerialCommunicator._read_and_parse_lines` without instantiation.

### Anti-Pattern 4: Touching _read_and_parse_lines During the Serial Split

**What people do:** "While I'm in here, let me clean up the generator logic."
**Why it's wrong:** This generator is the timing-critical hot path with known v1.6 RCA implications (Bug A, Bug B). Any change to it requires N≥5 bench-verified reads — hardware-gated work that is explicitly out of scope for v1.8.
**Do this instead:** Extract everything around it; leave the generator body byte-identical. Mark it with a `# DO NOT MODIFY — v1.9 RCA territory` comment.

### Anti-Pattern 5: Removing argcomplete Before Click Completion Is Wired

**What people do:** Delete `argcomplete` and its `argcomplete.autocomplete(parser)` call as part of the argparse→Click migration.
**Why it's wrong:** Shell completion is a user-visible feature. If Click's completion is not wired before argcomplete is removed, users lose tab-completion silently.
**Do this instead:** Wire `EPROM_COMPLETE` shell completion for the Click app before removing `argcomplete`. Click's built-in completion needs `COMP_SHELL` or similar; test it before merging.

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---|---|---|
| GitHub Releases API | HTTP GET via `requests` in `firmware.py` | Rate-limiting is a latent issue at scale; already worked around by caching in `list_releases`. No change needed in v1.8. |
| PyPI | Build + publish via CI | `pyproject.toml` owns this; no app-code changes needed |

### Internal Boundaries

| Boundary | Communication | Notes |
|---|---|---|
| cli_handlers.py ↔ chip_resolver.py | Direct function call; `ChipNotFoundError` propagated up | Replaces the 9x inline pattern |
| cli_handlers.py ↔ EpromOperator | Constructor injection via `config_manager`; method calls with typed args | No change from current pattern |
| EpromOperator ↔ SerialCommunicator | `find_and_connect(command_dict, config)` + `disconnect()` | Unchanged; serial_comm.py internal restructure is transparent |
| serial_comm.py ↔ frame_parser.py | Import-level; `_decode_id_frame` called inside `_read_and_parse_lines` | One direction only: serial_comm imports frame_parser, never vice versa |
| frame_parser.py ↔ codec.py | `codec.format_message(msg_id, params, entry)` called inside `_decode_id_frame` | One direction: frame_parser imports codec |
| constants.py ↔ firmware header | Values must be byte-identical | Guarded by `test_firmware_contract_parity.py` (Phase 36) |

---

## Sources

- Direct codebase reading: all 14 Python modules in `firestarter_app/firestarter/` (2026-05-27)
- `firestarter/include/firestarter.h` (command codes and flag bits; verified against `constants.py` — all COMMAND_* and FLAG_* values match)
- `tests/conftest.py`, `tests/test_decoder.py`, `tests/test_consistency_check.py` — existing test patterns used as structural references
- `.planning/PROJECT.md` §v1.8 — locked decisions (flat layout, Click, ruff+black+mypy, tests-first, host-only)
- `firestarter_app/CLAUDE.md` — confirmed constants sync requirements and WARNING-5 database override

---
*Architecture research for: firestarter_app v1.8 structural cleanup*
*Researched: 2026-05-27*

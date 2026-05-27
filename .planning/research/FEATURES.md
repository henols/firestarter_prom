# Feature Research

**Domain:** Python serial-device CLI — structural cleanup / refactoring milestone (v1.8)
**Researched:** 2026-05-27
**Confidence:** HIGH (grounded in direct codebase inspection; pattern recommendations drawn from
well-established Python CLI and protocol-separation idioms, not guesswork)

> **Scope note.** This is a REFACTORING milestone. "Features" here means TARGET-STATE
> STRUCTURAL PATTERNS — what a clean, well-structured version of this app looks like after
> v1.8. End-user command surface and wire protocol are frozen (GATE-1.8). The table below
> therefore uses "feature" to mean "structural capability the cleaned codebase must have."

---

## Feature Landscape

### Table Stakes (Must Have — "Structured & Readable" Gate)

These are the patterns that turn the current spaghetti into a maintainable codebase. Missing
any one of them leaves a significant hotspot unaddressed.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Click command-group, one-handler-per-command** | `main()` is a 418-line, 14-branch `if/elif` block; every new command requires editing the monolith. Click's `@cli.command()` decorator moves each branch into its own function with its own argument declarations. | MEDIUM | Click command functions replace both `create_*_args()` builder functions AND the dispatch branches. `argcomplete` tab-completion must be ported to `click-shell` or `click`'s `shell_complete` hook. The `fw` subparser's `--json`/`--list` cross-validation (currently a post-parse guard calling `fw_parser.error()`) becomes a Click `callback` or `is_eager` option. Existing argparse `_validate_firmware_version` type-validator becomes a `click.ParamType`. |
| **Single `resolve_chip()` helper (kills 9× boilerplate)** | The pattern `full = db.get_eprom(name); prog = db.convert_to_programmer(full) if full else None; if not prog: logger.error(...); return 1` is copy-pasted across read/write/verify/blank/erase/id/dev-read/dev-addr/dev-consistency-check (9 sites). One missed null-check is a silent bug. | LOW | Signature: `def resolve_chip(db: EpromDatabase, name: str) -> dict` — raises `ChipNotFoundError` (custom exception) on miss, returns programmer-ready dict on hit. Callers go from 5 lines to 1 call inside a try/except. The Click error-handling boundary (see Error Handling section) catches the exception and exits with code 1. |
| **Thin Click entry point** | After decomposing the 14-branch dispatcher, `main.py` should be ≤ 50 lines: imports, Click group definition, `sys.exit(cli())`. All logic lives in command functions or service objects. | LOW | Logging setup and `ConfigManager` init can move into a `@cli.result_callback()` or a shared `@pass_context` decorator. |
| **`serial_comm.py` split into transport / framing / codec** | At 1037 lines, `serial_comm.py` mixes: (a) raw byte I/O + port lifecycle (`SerialCommunicator.__init__`, `send_bytes`, `read_line_bytes`, `disconnect`); (b) binary frame parsing (`_read_and_parse_lines`, `_decode_id_frame`, CRC, preamble detection); (c) message decoding + rendering (`_decode_param`, `_format_message`, `_log_rurp_feedback`); (d) port-discovery logic (`_list_potential_ports`, `_probe_port`, `find_and_connect`). None of these concerns are independently testable today without instantiating the full class. | HIGH | Split target (flat layout, sibling modules): `transport.py` (raw Serial I/O + port lifecycle), `framing.py` (byte-stream → frame objects, no rendering), `codec.py` (frame → LogMessage, format rendering), `port_discovery.py` (probe + connect). `serial_comm.py` becomes a thin facade re-exporting the public API for backward compat. Each module is independently unit-testable with `BytesIO`/`_FakeSerial` — the existing `conftest.py` pattern already proves this works for `_decode_id_frame`. |
| **Single source of truth for wire-protocol constants** | `constants.py` defines `COMMAND_*`, `FLAG_*`, `BAUD_RATE`, `BUFFER_SIZE`; these must stay in sync with `firestarter/include/firestarter.h`. Currently scattered references exist across `serial_comm.py`, `eprom_operations.py`, `database.py`, and `main.py` via `from firestarter.constants import *`. Star imports make the dependency graph invisible. | MEDIUM | Replace `from firestarter.constants import *` with named imports everywhere. Add a CI parity test (`test_constants_parity.py`) that reads `firestarter/include/firestarter.h` and asserts each constant value matches. The existing `test_revision_constants_parity.py` already does this for `REVISION_*` — extend the pattern to cover all `COMMAND_*` and `FLAG_*` values. |
| **Single source of truth for DIP→RURP pin mapping** | `pin_conversions` dict in `database.py` (module-level, hardcoded) and `pinouts.json` both encode the physical DIP-pin-to-RURP-bus-line mapping. `get_bus_config()` uses `pin_conversions` to translate `pinouts.json` address-bus arrays. The two sources must agree; there is no automated check. | MEDIUM | Extract `pin_conversions` to its own module (`pin_map.py`) or consolidate into `pinouts.json` with a loader. Add a unit test that round-trips a known chip (W27C512) through `get_bus_config()` and asserts the expected bus list. The test serves as the regression guard when either source changes. |
| **Characterization test suite before refactor** | Core paths (CLI dispatch, EPROM ops, DB lookup, pin translation) have zero unit tests. Refactoring without a safety net is high-risk — any behavioural regression is invisible until hardware bench. | HIGH | Priority order for characterization: (1) `EpromDatabase` — `get_eprom()`, `convert_to_programmer()`, `get_bus_config()` for W27C512, AM29F040, AT28C256 as golden fixtures; (2) `_decode_id_frame` + `_decode_param` — already partially covered by `test_decoder.py`, extend coverage; (3) `build_flags()` and `resolve_chip()` helper (once written). CLI dispatch tests come after Click migration, not before. |
| **Consistent exception hierarchy + exit-code mapping at CLI boundary** | Error handling mixes: exceptions (`SerialError`, `EpromOperationError`, `FirmwareOutdatedError`), boolean return values (`eprom_operator.read_eprom()` returns `bool`), and integer return codes (the `1 if not X else 0` pattern repeated 12 times in `main()`). A developer reading any handler cannot tell which style applies. | MEDIUM | Define a `FirestarterError` base with `exit_code: int`. Subclasses: `ChipNotFoundError(exit_code=1)`, `ProgrammerNotFoundError(exit_code=1)`, `FirmwareOutdatedError(exit_code=1)`, `ProtocolError(exit_code=1)`, `HardwareError(exit_code=1)`. All service methods raise; never return bool. Click entry point has a single `@cli.result_callback()` or `try/except FirestarterError as e: sys.exit(e.exit_code)` that maps exceptions to exit codes. Eliminates the 12× `1 if not X else 0` wrappers. |
| **ruff + black + mypy config with CI gate** | No formatter or linter config exists. Code style is inconsistent (f-strings mixed with `%`-format, mixed type-hint coverage, dead commented-out code in `database.py`, `get_eprom()`, `eprom_operations.py`). | LOW | `pyproject.toml` gets `[tool.ruff]`, `[tool.black]`, `[tool.mypy]` sections. CI runs `ruff check`, `black --check`, `mypy --strict` (or `--ignore-missing-imports` for the serial lib). Dead commented-out code (`database.py` lines 503–519, `eprom_operations.py` comment blocks) deleted, not just silenced. |
| **Type-hint coverage on all public functions** | `main.py` has zero type hints on `build_arg_flags()`, `allowed_eproms()`, and all `create_*_args()` functions. `serial_comm.py` has good coverage on `SerialCommunicator` methods but none on module-level helpers. `database.py` has no hints on any public method. | MEDIUM | Add `-> dict`, `-> list`, `-> Optional[str]`, `-> None` on all public functions. Use `TypedDict` for the EPROM data dict shape (the `{"memory-size": int, "algorithm": int, ...}` structure passed between `database.py` and `eprom_operations.py`). `mypy` gate enforces completeness. |

### Differentiators (Nice to Have — Raise the Quality Bar)

These patterns improve the codebase but are not blocking for "structured & readable."

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **`EpromChip` dataclass replacing dict passing** | The EPROM data dict `{"memory-size": int, "algorithm": int, "pin-count": int, "vpp_mv": int, ...}` is passed between `database.py`, `eprom_operations.py`, and `serial_comm.py` as an untyped dict. String key typos are silent bugs discovered at runtime. A `@dataclass` or `TypedDict` makes the shape explicit and mypy-checked. | MEDIUM | Two options: `TypedDict` (zero runtime overhead, backward-compat with dict unpacking in `json.dumps(command_dict)`) vs `@dataclass` (richer, requires conversion to dict before JSON serialise). `TypedDict` is preferred because the dict is passed directly to `json.dumps()` as the wire command — no serialisation layer needed. |
| **`ChipResolutionService` object replacing scattered `EpromDatabase` calls** | `main.py` calls `db.get_eprom()`, `db.convert_to_programmer()`, and `db.search_chip_id()` directly at the dispatch layer. A `ChipResolutionService` encapsulating these calls (and the resolve helper) makes the dependency on `EpromDatabase` explicit and mockable for tests. | LOW | Lightweight: `ChipResolutionService(db: EpromDatabase)` with `resolve(name: str) -> ProgrammerConfig` and `search(query: str) -> list[ChipSummary]`. The Click commands take the service object via `@click.pass_obj` or dependency injection through the Click context. |
| **Protocol state-machine as an explicit class** | The INIT→MAIN→END protocol is implemented as methods on `EpromOperator` (`_execute_phase`, `_run_state_machine`, `_main_phase_simple`, `_main_phase_send_data`). The state names ("INIT", "MAIN", "END") are string literals compared against `response.type`. Extracting a `ProtocolStateMachine` class makes the state transitions testable without a real serial port. | HIGH | Worth doing if v1.9 RCA work will modify the read path — a testable state machine makes it possible to inject known response sequences and assert the right data was accumulated. Dependencies: transport/framing split must happen first. |
| **`logging_utils.py` docstring and type coverage** | `SingleLineStatusHandler` in `logging_utils.py` is undocumented and has no type hints. It relies on a non-standard `extra={"status": "start"/"end"}` convention that is invisible to callers. | LOW | Document the `status` extra convention in a module docstring. Add `emit(self, record: logging.LogRecord) -> None` type hint. |
| **Dead-code audit and removal** | `database.py` contains a large commented-out block (lines 503–519 in `get_eprom()`). `eprom_operations.py` has stray comment blocks. `serial_comm.py` has a `# json_data = json.dumps(command_dict)` commented-out line (line 272). | LOW | Delete, not comment-out. Commented-out code in a git repo is noise — git history serves as the archive. Dead-code deletion is a one-pass ruff/manual audit. |
| **Docstring convention normalisation** | Docstrings exist on some classes (`EpromDatabase`, `SerialCommunicator`) but are absent or inconsistent on most methods. `EpromDatabase._map_data` has a useful docstring; `get_eprom()` has a misleading one ("always returns the 'full' data" is partly wrong given the commented-out pruning code). | LOW | Adopt Google-style or NumPy-style docstrings (pick one, enforce with `pydocstyle` or ruff's `D` rules). Priority: public methods on `EpromDatabase`, `SerialCommunicator`, `EpromOperator`. |
| **Naming normalisation** | Mixed conventions: `vpp_mv` (snake_case with unit suffix), `pin-count` (kebab-case JSON key used as Python dict key), `FLAG_CAN_ERASE` (SCREAMING_SNAKE), `build_arg_flags` (snake_case). JSON dict keys that flow into the wire protocol must stay kebab-case (they are serialised directly). Python-internal variable names should be snake_case throughout. | LOW | Document the boundary: dict keys that are wire-protocol fields stay kebab-case; internal Python variables and attributes are always snake_case. Enforce with a one-time renaming pass, not an ongoing convention argument. |

### Anti-Features (Avoid — Patterns That Seem Good but Create Problems)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Subpackage reorganisation (e.g. `cli/`, `serial/`, `data/`)** | "Group related modules together" is intuitive. A `serial/` subpackage holding `transport.py`, `framing.py`, `codec.py` feels tidy. | The operator explicitly locked **FLAT layout** (PROJECT.md, 2026-05-27). Subpackages break git blame continuity, require import path changes throughout (`from firestarter.serial.transport import ...`), and have no functional benefit for a package this size. The flat layout with descriptive module names achieves the same discoverability. | Name modules descriptively (`transport.py`, `framing.py`, `codec.py`) and keep them as siblings. A flat `__init__.py` that re-exports the public API gives consumers a stable import surface regardless of internal decomposition. |
| **Async I/O for serial communication** | Serial reads block; `asyncio` + `serial_asyncio` would enable concurrent reads and non-blocking timeout handling. | The current protocol is strictly synchronous — the firmware drives a request-response state machine (INIT→MAIN→END) where the host must send an ACK before the firmware proceeds. Introducing async does not remove the serialization requirement and adds coroutine management overhead to every caller. The existing thread-free, timeout-based loop is simpler and correct for this use case. | Keep synchronous I/O. If timeout behaviour needs improvement, fix the timeout logic directly in `_read_and_parse_lines`. |
| **ORM or schema validation library for chip database** | Pydantic/marshmallow/attrs could validate chip database entries at load time. | The chip database is generated by `tools/build_db.py` from an upstream XML source; structural errors should be caught in the generator, not at load time in the app. Adding a schema library introduces a heavy dependency for a problem better solved upstream. The `mypy` + `TypedDict` approach achieves type safety for the Python-side data shapes without schema validation at runtime. | Validate in `build_db.py`. Add a CI step that runs `python tools/build_db.py --validate` (or equivalent). |
| **Replacing the JSON wire protocol with a binary format** | Binary would be smaller and faster to parse. | Explicitly out of scope (PROJECT.md: "Binary wire format replacing JSON — still out; per-operation overhead trivial"). The firmware side would also need to change, breaking the host-only constraint of v1.8. | The wire protocol stays JSON-over-serial. The `serial_comm.py` refactor concerns the host-side frame layer (binary ID-encoded log frames are already binary; the command channel is JSON). |
| **Singleton `EpromDatabase` kept as global state** | The singleton pattern is already in place (`_instance`, `_initialized` class vars). Keeping it means zero callers need updating. | The singleton makes `EpromDatabase` untestable in isolation — tests cannot inject a mock database without monkeypatching the class variable. The characterization tests (table stakes item above) will hit this immediately. | Replace with dependency injection: instantiate `EpromDatabase` once in the Click group callback and pass it via `click.Context.obj`. Command functions receive it via `@click.pass_context`. Remove the `_instance`/`_initialized` singleton machinery. This is a one-time change that pays dividends for every future test. |
| **Logging inside service objects replaced by structured return values** | "Return data, don't log" is a common pattern. If `EpromDatabase.get_eprom()` raised instead of logging+returning `None`, callers would be cleaner. | `serial_comm.py` must log because the serial byte stream interleaves log messages from the firmware with data responses. That logging is inherently side-effecting. For `EpromDatabase` and `EpromOperator`, raising exceptions is the right approach. But do NOT attempt to remove all logging from service objects in a single pass — the `logger.debug()` calls in `_run_state_machine` are diagnostic gold for hardware debugging. | Raise exceptions for error conditions (chip not found, command rejected). Keep `logger.debug()` for diagnostic traces. Remove `logger.error()` from service methods where the error is surfaced via exception to the CLI boundary (the CLI boundary logs the user-facing message). |
| **`argcomplete` replaced by a custom completion mechanism** | Tab-completion is currently via `argcomplete` hooked into argparse. Click has its own shell-completion support. | Click's `shell_complete` is the right mechanism after migration. Do NOT write a custom completer — the `EpromCompleter` class in `main.py` can be replaced by a Click `shell_complete` callback on the `eprom` argument. `argcomplete` is removed when argparse is removed. | Use Click's built-in `shell_complete` support. The `EpromCompleter.__call__` logic (filter `allowed_eproms()` by prefix) maps directly to a Click completion function. |

---

## Feature Dependencies

```
characterization-tests (safety net)
    └──must precede──> click-migration
    └──must precede──> serial-comm-split
    └──must precede──> exception-hierarchy

resolve-chip-helper
    └──must precede──> click-migration
        (the 9 dispatch branches can only be safely collapsed once the
         shared helper exists and is tested)

exception-hierarchy
    └──must precede──> click-migration
        (the CLI boundary exit-code mapping needs the exception types
         defined before the Click handlers use them)

constants-star-import-removal
    └──must precede──> mypy-gate
        (star imports prevent mypy from resolving names)

transport-framing-split
    └──enables──> protocol-state-machine-class (differentiator)
    └──enables──> deeper serial unit tests

singleton-removal (EpromDatabase)
    └──enables──> characterization-tests
        (tests cannot inject a mock database until singleton is gone)
    └──can be done in same phase as characterization-tests
       (remove singleton → inject via function arg → write tests)

dead-code-removal
    └──no dependencies; can happen in any phase
    └──best done early (reduces cognitive load during refactor)

TypedDict-for-EPROM-dict
    └──must precede OR concurrent──> mypy-gate
    └──can be done independently of click-migration
```

### Dependency Notes

- **characterization-tests must precede click-migration:** Without a safety net, the dispatcher decomposition is a blind refactor on untested code. Tests catch regressions.
- **resolve-chip-helper must precede click-migration:** The 9 dispatch branches that copy-paste the chip lookup can only be safely deleted once the shared helper is tested and proven.
- **exception-hierarchy must precede click-migration:** The Click command functions need a defined error type to raise; the entry-point needs a defined type to catch.
- **singleton-removal enables characterization-tests:** `EpromDatabase.__new__` singleton makes it impossible to instantiate a test-specific instance without monkeypatching the class. Remove singleton first (replace with DI), then write tests.
- **transport-framing-split enables protocol-state-machine:** The state machine operates on `Response` objects from the framing layer. If framing is a separate, injectable component, the state machine can be tested by feeding synthetic `Response` sequences.
- **constants star-import removal enables mypy:** `from firestarter.constants import *` makes `mypy` unable to trace where `FLAG_FORCE`, `COMMAND_READ`, etc. originate. Named imports are a prerequisite for `mypy --strict`.

---

## MVP Definition

> "MVP" here means the minimum structural changes that satisfy the v1.8 goal
> ("structured, readable, spaghetti-free") while preserving GATE-1.8 (wire
> protocol and command surface byte-identical).

### Phase order implied by dependencies (roadmap input)

**Phase A — Safety net first (no structural changes yet)**
- [ ] Remove `EpromDatabase` singleton (replace with DI via function args) — prerequisite for testability
- [ ] Write characterization tests for `EpromDatabase.get_eprom()`, `convert_to_programmer()`, `get_bus_config()` (W27C512, AM29F040, AT28C256 golden fixtures)
- [ ] Extend `test_decoder.py` coverage to all catalog-entry shapes
- [ ] Install ruff + black + mypy; fix existing violations; add CI gate
- [ ] Remove dead commented-out code (zero-risk, high signal-to-noise improvement)

**Phase B — Data layer consolidation**
- [ ] Implement `resolve_chip()` helper; replace 9 copy-paste sites (can be done with argparse still in place — this is a Python function, not a CLI migration)
- [ ] Define `ProgrammerConfig` `TypedDict`; annotate `database.py`, `eprom_operations.py` public API; add to mypy gate
- [ ] Consolidate `pin_conversions` to one authoritative location; add round-trip unit test
- [ ] Name-import all `constants.*` usages; add parity test for `COMMAND_*` + `FLAG_*` values against firmware header

**Phase C — Exception hierarchy + error handling**
- [ ] Define `FirestarterError` hierarchy (`ChipNotFoundError`, `ProtocolError`, etc.)
- [ ] Convert `EpromOperator` boolean returns to exceptions; add tests
- [ ] Convert `EpromDatabase` `None` returns (on chip-not-found) to `ChipNotFoundError`

**Phase D — CLI migration (Click)**
- [ ] Migrate `create_*_args()` + dispatch branches to `@cli.command()` functions
- [ ] Port `EpromCompleter` to Click `shell_complete`; port `_validate_firmware_version` to `click.ParamType`
- [ ] Validate `--json`/`--list` cross-dependency via Click callback
- [ ] Wire `click.Context.obj` for `EpromDatabase` + `ConfigManager` DI

**Phase E — Serial layer split**
- [ ] Extract `transport.py` (raw I/O + port lifecycle); unit-test with `_FakeSerial`
- [ ] Extract `framing.py` (byte-stream → frame objects); unit-test with `BytesIO`
- [ ] Extract `codec.py` (frame → `LogMessage`, rendering); unit-test with synthetic frames
- [ ] `serial_comm.py` becomes thin facade re-exporting public API

**Phase F — Polish**
- [ ] Full docstring pass on public methods
- [ ] Naming normalisation pass (snake_case throughout, document kebab-case wire-key boundary)
- [ ] Final mypy + ruff sweep; confirm CI green

### Defer to v1.9 or later

- [ ] `ProtocolStateMachine` as a standalone testable class — the state machine already works correctly; extracting it is only worth doing when the v1.9 RCA work requires modifying the read path. Complexity is HIGH with no v1.8 payoff.
- [ ] Full Pydantic/TypedDict validation of `chip_database.json` at load time — validate in `build_db.py` instead.
- [ ] `async` serial I/O — no benefit for a synchronous request-response protocol.

---

## Feature Prioritization Matrix

| Feature | Dev Value (maintainability) | Implementation Cost | Priority |
|---------|----------------------------|---------------------|----------|
| Characterization test suite | HIGH | HIGH | P1 |
| `resolve_chip()` helper | HIGH | LOW | P1 |
| Exception hierarchy | HIGH | MEDIUM | P1 |
| Click migration | HIGH | MEDIUM | P1 |
| `serial_comm.py` split | HIGH | HIGH | P1 |
| Single constants source (named imports + parity test) | HIGH | MEDIUM | P1 |
| Single pin-mapping source | MEDIUM | MEDIUM | P1 |
| ruff + black + mypy + CI | HIGH | LOW | P1 |
| Type-hint coverage | MEDIUM | MEDIUM | P2 |
| Dead-code removal | MEDIUM | LOW | P2 |
| `EpromChip` TypedDict | MEDIUM | MEDIUM | P2 |
| `ChipResolutionService` object | LOW | LOW | P3 |
| Docstring normalisation | LOW | LOW | P3 |
| Naming normalisation | LOW | LOW | P3 |
| `ProtocolStateMachine` class | MEDIUM | HIGH | DEFER |

---

## Sources

- Direct codebase inspection: `firestarter_app/firestarter/main.py` (418-line dispatcher, 14 branches, 9 copy-paste chip-lookup sites confirmed by line count), `serial_comm.py` (1037 lines, 4 mixed concerns identified), `database.py` (`pin_conversions` hardcoded dict at module level, singleton pattern, dead comment block at lines 503–519), `eprom_operations.py` (boolean return convention, state machine structure), `constants.py` (star-import usage confirmed), `tests/conftest.py` (`_FakeSerial` + `__new__` bypass pattern already established — proves the framing layer can be tested without real serial I/O)
- `tests/test_decoder.py` — existing coverage establishes the `BytesIO`-backed test pattern as viable for the serial layer; gap: no tests for `database.py`, `eprom_operations.py`, or CLI dispatch
- `PROJECT.md` v1.8 scope decisions: flat layout locked, Click locked, tests-first locked, wire-protocol frozen, firmware sub-repo untouched
- `firestarter_app/CLAUDE.md` — data-flow architecture and constants sync contract documented
- Python Click documentation (training knowledge, HIGH confidence for `@cli.command()`, `shell_complete`, `click.Context.obj`, `click.ParamType` patterns — these are stable Click ≥7 APIs)
- Standard Python refactoring patterns for serial-device CLIs (HIGH confidence for transport/framing/codec separation — this is a textbook protocol layer decomposition; the existing `_FakeSerial` fixture in `conftest.py` already embodies this pattern for one layer)

---
*Feature research for: firestarter_app structural cleanup (v1.8 refactoring milestone)*
*Researched: 2026-05-27*

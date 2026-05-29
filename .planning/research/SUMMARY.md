# Project Research Summary

**Project:** firestarter_app v1.8 — Host CLI Structural Cleanup
**Domain:** Python serial-device CLI refactoring (hardware-facing, hardware-gated)
**Researched:** 2026-05-27
**Confidence:** HIGH (all four research dimensions grounded in direct codebase inspection; tool versions PyPI-verified)

---

## Executive Summary

The v1.8 milestone is a pure-software, hardware-gated refactoring of `firestarter_app/` — the Python host CLI for the Firestarter EPROM programmer. The goal is to eliminate three concentrated hotspots: a 418-line `main()` with 14-branch `if/elif` dispatch and 9 copy-paste chip-lookup patterns; a 1037-line `serial_comm.py` mixing port I/O, CRC framing, message rendering, and port discovery; and a complete absence of unit tests on the CLI dispatch, EPROM ops, and database layers. The refactor does not touch the firmware sub-repo, the wire protocol, or the end-user command surface — all are frozen under GATE-1.8 (byte-identical wire protocol; identical command names, flags, defaults, and exit codes). Any intentional behavior change (documented bug fixes) must be called out explicitly in commits and the milestone document.

The recommended approach is a seven-phase sequence (Phases 36-42) that puts safety infrastructure first and structural changes second. Phases 36-37 write characterization tests and install the ruff+ruff-format+mypy+CI gate before any code is restructured — this is the non-negotiable foundation. Phases 38-39 perform low-risk mechanical extractions (frame parsing, codec, address parsing, exceptions, chip_resolver). Phase 40 cleans up the serial transport layer. Phase 41 performs the highest-risk change: the argparse to Click migration with cli_handlers.py. Phase 42 sweeps error handling, type coverage, dead code, and naming. The entire sequence is dependency-ordered: characterization tests before restructure; exception hierarchy before Click migration; star-import removal before the mypy gate; parity-test extension before constants consolidation; chip_resolver before CLI handlers.

The primary risks are behavioral regressions on the wire protocol and the five non-obvious argparse-to-Click behavioral traps (exit-code convention, prefix matching, store_false polarity, the --pre/--firmware-version/--stable mutex group, the _validate_firmware_version type-validator). A secondary risk is scope creep into the read path: the 15 N=5 W27C512 baseline binaries that v1.9 RCA depends on must not be invalidated by v1.8 read-path changes. Two latent bugs found during research must be fixed, not pinned as correct behavior: the build_arg_flags if "force" in args attribute-vs-truthiness bug (always evaluates True regardless of the flag value), and the apparently missing COMMAND_FW_VERSION = 13 in constants.py (referenced in serial_comm.py and firmware.py but absent from the constants module). Characterization tests must carry explicit BUG markers on both.

---

## Key Findings

### Recommended Stack

The stack is additive-only: no runtime dependencies are replaced, only development tooling is added and argcomplete is removed. All versions confirmed against PyPI on 2026-05-27. Full pyproject.toml config sections are specified verbatim in STACK.md.

**Core technologies:**

- Click 8.4.1 (replaces argparse + argcomplete): decorator-based commands eliminate the 14-branch dispatcher; @click.group / @group.command map 1:1 to existing subparser structure; click.testing.CliRunner ships in-box for CLI characterization tests; Click 8.4 fixed the flag-option default-precedence bug that affected --pre/--stable in 8.3.x; standalone_mode=True (default, do not disable) produces argparse-identical exit codes (0 success, 2 usage error).
- ruff 0.15.14 + ruff-format (replaces flake8 + isort; single formatter, do NOT run black alongside): Rust-speed; E/F/I rules from day 1; rule set expanded phase-by-phase (UP in Phase 37, selective ANN in Phase 39); initial baseline via ruff check --add-noqa makes CI green before any cleanup.
- mypy 2.1.0 + types-pyserial 3.5.0.20260519: gradual adoption via disallow_untyped_defs = false globally, tightened per-module as each module is typed; star-import removal is a prerequisite (mypy cannot trace from firestarter.constants import *); one-way ratchet pattern (add to [[tool.mypy.overrides]] strict list, never remove).
- pytest 9.0.3 + pytest-mock 3.15.1 + pytest-cov 7.1.0 + syrupy 5.2.0: pytest-mock mocker fixture with autospec=True mandatory for pyserial mocking; syrupy golden-file snapshots lock CLI output and exit codes before restructuring; coverage gate starts at 60%, ratchets up per phase.
- pre-commit 4.6.0: hook order is ruff-check --fix -> ruff-format -> mypy; CI runs pre-commit run --all-files as required check.

Remove from runtime deps: argcomplete>=3.6.2 — dropped when argparse is removed. Confirm with operator before removing (shell completion is user-visible; Click's built-in completion must be wired before argcomplete is deleted).

Anti-list (do not add): DI framework, async/asyncio, plugin system, Pydantic/attrs/marshmallow, black alongside ruff-format, flake8 alongside ruff, isort standalone, subpackages.

### Expected Structural Targets (v1.8 "Features")

This is a refactoring milestone. "Features" are target-state structural patterns, not end-user capabilities. The command surface is frozen.

**Must have (table stakes):**

- Click command-group, one handler per command — eliminates the 418-line main() dispatcher; each of the 14 commands becomes a @cli.command() decorated function in cli_handlers.py
- resolve_chip() helper in chip_resolver.py — eliminates 9 copy-paste db.get_eprom + db.convert_to_programmer + null-check sites; raises ChipNotFoundError on miss; signature: resolve_chip(name: str) -> dict
- Thin Click entry point — main.py reduced to <= 50 lines (imports, Click group, global options, entry-point call)
- serial_comm.py split: extract frame_parser.py (CRC + decode, pure functions, no socket I/O), codec.py (_format_message + _REVISION_SILKSCREEN), address_parser.py (hex/decimal string parsing, ~40 lines); serial_comm.py retains SerialCommunicator class + _read_and_parse_lines generator + port discovery; the generator body is NOT modified (v1.9 RCA territory)
- Single source of truth for wire-protocol constants — named imports replace star-imports in all 4 modules; parity test extended from REVISION_* to cover all COMMAND_*, FLAG_*, CTRL_* values against firmware headers
- exceptions.py — all exception classes in one place
- Characterization test suite before any structural change — EpromDatabase golden fixtures, decoder coverage, firmware contract parity, address parser
- Consistent exception hierarchy + exit-code mapping — FirestarterError base with exit_code: int; all service methods raise; never return bool; eliminates 12x "1 if not X else 0" wrappers
- ruff + ruff-format + mypy + CI gate

**Should have:**

- ProgrammerConfig TypedDict for the untyped EPROM data dict — preferred over @dataclass because the dict is passed directly to json.dumps()
- Type-hint coverage on all public functions
- Dead-code deletion: read_data_block legacy path (replaced by W-04), commented-out blocks in database.py L503-519, globals() introspection replaced with COMMAND_NAMES.get()
- Docstring normalisation on public methods

**Defer to v1.9+:**

- ProtocolStateMachine as a standalone testable class — HIGH complexity, zero v1.8 payoff
- Full schema validation of chip_database.json at load time — validate in build_db.py instead
- async serial I/O — the protocol is inherently synchronous

### Architecture Approach

The target maintains the existing flat-module layout (all files as siblings in firestarter_app/firestarter/, no subpackages) while decomposing the two monoliths and establishing explicit layer boundaries. Three-layer model: CLI Layer (main.py + cli_handlers.py + address_parser.py) calls Service/Ops Layer (chip_resolver.py + eprom_operations.py + hardware.py + firmware.py + database.py) which calls Transport Layer (serial_comm.py + frame_parser.py + codec.py). Shared/cross-cutting modules (constants.py, exceptions.py, messages.py, config.py, logging_utils.py) are imported by any layer.

**New modules introduced (all flat):**

1. chip_resolver.py (~80 lines) — resolve_chip(name: str) -> dict; raises ChipNotFoundError; imports from database.py and exceptions.py only
2. frame_parser.py (~200 lines) — CRC table, decode functions, Response, LogMessage, MAGIC_PREAMBLE; pure functions, fully testable with bytes inputs
3. codec.py (~120 lines) — format_message(msg_id, params, entry) -> str | None, _REVISION_SILKSCREEN; imports from constants.py + messages.py only
4. address_parser.py (~40 lines) — parse_address(s: str | None) -> int | None, parse_size; raises ValueError on bad input
5. cli_handlers.py (~400 lines) — one Click command function per top-level command
6. exceptions.py (~30 lines) — all application exception classes in one place

Key architectural invariant: _read_and_parse_lines generator body in serial_comm.py must remain byte-identical to the current implementation. Mark it: # DO NOT MODIFY -- v1.9 RCA territory. The split extracts pure-compute decode logic around it, not through it. The connection.read(frame_len) call site stays exactly where it is.

**Five boundary rules that must not be violated:**
1. CLI layer never imports from serial_comm.py, frame_parser.py, or codec.py directly
2. Transport layer never imports from database.py, eprom_operations.py, or firmware.py
3. frame_parser.py has no intra-package imports (stdlib + typing only)
4. codec.py imports from constants.py and messages.py only
5. chip_resolver.py imports from database.py and exceptions.py only

### Critical Pitfalls

1. Wire-protocol regression via serial module split (CRITICAL) — _read_and_parse_lines mixes byte accumulation, preamble detection, and frame decode in one atomic blocking sequence; introducing a buffer boundary can alter when connection.read(N) is called, silently breaking the 64-byte Arduino UART receive buffer timing. Prevention: write a fake_serial-backed characterization test pinning the preamble->body->terminator sequence BEFORE splitting; keep the generator body byte-identical; run full test_decoder.py suite after every file move. Read-path ring-fence for v1.9 RCA: any non-structural change to read_data_block() or read_eprom() requires INTENTIONAL BEHAVIOR CHANGE in the commit message.

2. argparse to Click behavioral drift on exit codes (CRITICAL) — Click command callbacks return None; "return 0" or "return 1" in a Click callback is a no-op (process exits 0 regardless). Prevention: characterize exit codes for all 14 command branches with CliRunner before migration; use sys.exit(1) or raise click.ClickException(msg) for error cases; raise click.UsageError(msg) for argument errors; never disable standalone_mode.

3. argparse to Click argument-parsing edge cases (CRITICAL) — Five specific traps: (a) prefix matching exists in argparse but not Click; (b) --no-blank-check store_false polarity needs flag_value=False, default=True in Click; (c) nargs="?" for output_file semantics differ; (d) --pre/--firmware-version/--stable mutex group has no native Click equivalent — implement via raise click.UsageError(...); (e) _validate_firmware_version must be ported as a Click ParamType or callback.

4. Characterization tests pinning latent bugs (HIGH) — Two known bugs must NOT be pinned: (a) build_arg_flags "if force in args" tests attribute existence (always True when argparse set the attribute), not truthiness; (b) COMMAND_FW_VERSION is possibly absent from constants.py despite being referenced. Mark tests covering these with BUG comments.

5. Firmware-contract drift during constants consolidation (HIGH) — Existing parity test covers only REVISION_*. Prevention: extend parity test to cover all three blocks with hard-coded hex literals before any constants consolidation.

6. mypy avalanche abandoning the gate (MEDIUM) — Running mypy --strict on the current codebase produces 80-200+ errors. Prevention: start with disallow_untyped_defs = false globally; replace star-imports first; use per-module overrides as one-way ratchet; gate is "no new errors in refactored modules".

7. Sliding-window timeout regression (MEDIUM) — The generator resets start_time on every yield; reorganizing timeout logic can silently convert it to a fixed-deadline timeout. Prevention: write a unit test driving 3 delayed fake-serial responses against a 0.5s timeout; mark the reset as an invariant comment.

---

## Implications for Roadmap

Based on combined research across all four dimensions, the suggested phase structure is a strict 7-phase dependency-ordered sequence. The researchers propose this order; the roadmapper may refine scope and boundaries within phases. Phase numbering continues from v1.7's last phase (35).

### Phase 36: Characterization Test Baseline

**Rationale:** Safety net must exist before any structural change. Tests encoding the current contract must be committed first. Additive only.

**Delivers:** EpromDatabase golden fixtures (W27C512, AM29F040, AT28C256); address_parser tests; firmware contract parity test for COMMAND_* and FLAG_*; wire-path characterization test pinning preamble->body->terminator sequence; EpromDatabase singleton removed (prerequisite for testability); ruff+mypy installed with violation watermark recorded.

**Avoids:** Pitfall 6 (bug-pinning — BUG markers on tests covering known-wrong behavior)
**Risk:** LOW (additive only)
**Research flag:** Standard patterns — skip research-phase

---

### Phase 37: Tooling Baseline + CI Gate

**Rationale:** Formatting and linting enforced before structural changes so future diffs show logic changes only.

**Delivers:** pyproject.toml ruff/ruff-format/mypy/pytest config sections; ruff --add-noqa baseline; ruff format pass; initial mypy with error count recorded; GitHub Actions CI step; pre-commit config; coverage gate at 60%.

**Avoids:** Pitfall 8 (mypy avalanche)
**Risk:** LOW (mechanical)
**Research flag:** Standard patterns — skip research-phase

---

### Phase 38: Low-Risk Extractions (frame_parser + codec + address_parser + exceptions + dead-code)

**Rationale:** Extract pure-compute code with zero runtime behavior change. exceptions.py must exist before Phases 39-41 can import from it. These mechanical moves prove module boundaries before riskier structural changes.

**Delivers:** exceptions.py consolidated; frame_parser.py extracted (generator body NOT modified); codec.py extracted; address_parser.py implemented; dead code deleted (read_data_block, database.py L503-519 comments, globals() introspection); new pure-function tests.

**Avoids:** Pitfall 1 (connection.read call sites not moved); Pitfall 7 (new tests use bytes inputs)
**Risk:** LOW-MEDIUM (run full test suite after each file move)
**Research flag:** Standard patterns — skip research-phase

---

### Phase 39: Database Cleanup + chip_resolver

**Rationale:** chip_resolver.py must exist before Phase 41 CLI handlers. Star-import removal is the prerequisite for tightening the mypy gate.

**Delivers:** chip_resolver.py eliminating 9 copy-paste sites; EpromDatabase type hints and docstrings; pin_conversions docstring clarification; star-imports replaced with named imports in all 4 modules; COMMAND_FW_VERSION verified/added; star-import grep gate clean.

**Avoids:** Pitfall 9 (parity test extended BEFORE constants are touched); Pitfall 8 (star-import removal is the biggest mypy tractability fix)
**Risk:** LOW
**Research flag:** Standard patterns — skip research-phase

---

### Phase 40: Serial / Transport Restructure

**Rationale:** Completes serial cleanup after Phase 38 extractions. Must precede Phase 41 because CLI handlers need stable exception import surface.

**Delivers:** _validate_firmware_version as @staticmethod in serial_comm.py; moved to firmware.py; type hints on all public SerialCommunicator methods; remaining star-import cleanup; STATE_MACHINE_PREFIXES dead code deleted; sliding-window invariant comment added.

**Avoids:** Pitfall 5 (sliding-window timeout); Pitfall 11 (read-path scope expansion — VERIFICATION checklist confirms structural-only)
**Risk:** MEDIUM (generator body must stay byte-for-byte identical)
**Research flag:** Standard patterns — skip research-phase

---

### Phase 41: CLI Migration argparse to Click

**Rationale:** Highest-risk phase; comes last among structural changes because it has the widest surface area. All prior phases reduce the blast radius.

**Delivers:** click added to runtime deps; argcomplete removed (confirm with operator first); main.py <= 50 lines; cli_handlers.py with all 14 commands migrated in risk order; build_arg_flags bug fixed; EpromCompleter replaced by Click shell_complete; firmware version validator as Click ParamType; mutex group via callback guard; --no-blank-check with correct polarity; CI smoke test; test_cli_commands.py with CliRunner.

**Avoids:** Pitfall 2 (exit-code drift); Pitfall 3 (five argument-parsing edge cases pre-characterized); Pitfall 10 (entry-point update in same commit)
**Risk:** HIGH (mitigated by migration order, CliRunner, Phase 36 characterization tests)
**Research flag:** Standard patterns — five argparse traps well-specified; skip research-phase

---

### Phase 42: Error Handling Normalization + Quality Sweep

**Rationale:** Quality sweep is most efficient post-restructure. Frequent commits within this phase required.

**Delivers:** Consistent exception/exit-code convention throughout; all bare excepts replaced; return type annotations on all public functions; mypy per-module overrides expanded; docstrings on all public classes and methods; naming normalization; final ruff+mypy sweep with raised coverage threshold.

**Avoids:** Pitfall 12 (over-abstraction — no new ABCs or Protocols without copy-paste justification)
**Risk:** LOW-MEDIUM
**Research flag:** Standard patterns — skip research-phase

---

### Phase Ordering Rationale

- 36 before everything: safety net must precede restructuring; parity test extension and wire-path characterization test committed before constants or serial module touched
- 37 before restructuring: formatting enforcement before structural diffs prevents mixed noise in review
- 38 (exceptions) before 39, 40, 41: exceptions.py must exist before DB and serial layers import from it
- 39 (chip_resolver) before 41: CLI handlers cannot call resolve_chip() until it exists and is tested
- 40 (serial) before 41: CLI handlers need stable exception import surface
- 41 (Click migration) last among structural changes: widest surface area; highest coupling; benefits from all prior phases
- 42 last: quality sweep most efficient post-restructure

### Hard Dependencies

```
EpromDatabase singleton removal + characterization tests (Phase 36)
    must precede -> all structural changes

firmware contract parity test extension (Phase 36)
    must precede -> constants consolidation (Phase 39)

exceptions.py (Phase 38)
    must precede -> chip_resolver.py (Phase 39)
    must precede -> serial cleanup (Phase 40)
    must precede -> CLI handlers (Phase 41)

star-import -> named-import (Phase 39)
    must precede -> mypy gate tightening

chip_resolver.py (Phase 39)
    must precede -> cli_handlers.py (Phase 41)

serial cleanup (Phase 40)
    must precede -> cli_handlers.py (Phase 41)

exception hierarchy (Phases 38 + 39)
    must precede -> Click migration (Phase 41)
```

### Non-Regression Gates (CRITICAL -- enforced at phase VERIFICATION)

1. GATE-1.8-WIRE: Wire protocol byte-identical — firestarter read W27C512 on real hardware produces byte-identical output before and after; _read_and_parse_lines atomic-read invariant preserved; any non-structural read-path change requires INTENTIONAL BEHAVIOR CHANGE in commit message and VERIFICATION entry.
2. GATE-1.8-CLI: CLI command surface preserved — CliRunner tests confirm identical exit codes, output, and argument parsing for all 14 commands against Click implementation.
3. GATE-1.8-PARITY: Firmware contract parity — pytest tests/test_firmware_contract_parity.py passes with hex literals for COMMAND_*, FLAG_*, CTRL_*, REVISION_* blocks.
4. GATE-1.8-SMOKE: Entry-point smoke test — pip install -e . && firestarter --help runs successfully after Click migration.
5. GATE-1.8-NOIMPORT: No star-imports — grep -r 'import \*' firestarter/ returns no results after Phase 39.
6. V1.9-PRESERVE: Read-path ring-fence — v1.9 RCA team reviews v1.8 commit log for any read-path changes before starting; the 15 N=5 W27C512 baseline binaries must not be invalidated.

### Research Flags

All 7 phases use standard patterns — skip research-phase for all. Research was performed via direct codebase inspection; all tool patterns are well-documented.

**Areas requiring operator confirmation during planning (not research):**

- argcomplete removal (Phase 41): Verify with operator whether shell completion is an active user-facing dependency before removing.
- COMMAND_FW_VERSION presence (Phase 39): Inspect constants.py directly before Phase 39 planning.
- _merge_databases shallow-update bug scope (Phase 39): Verify whether any current user override entries have nested dicts affected.
- Coverage threshold ratchet (Phases 37-42): Set per-phase targets based on actual Phase 36 baseline measurement.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions confirmed against PyPI 2026-05-27; exact versions: Click 8.4.1, ruff 0.15.14, mypy 2.1.0, types-pyserial 3.5.0.20260519, pytest 9.0.3, pytest-mock 3.15.1, pytest-cov 7.1.0, syrupy 5.2.0 |
| Features / structural targets | HIGH | Direct code inspection of all 14 modules; line counts, copy-paste sites, and coupling violations are measured, not estimated |
| Architecture | HIGH | Derived entirely from direct codebase reading; target layer boundaries and module responsibilities specified at function-signature level; _read_and_parse_lines preservation grounded in firmware timing constraints |
| Pitfalls | HIGH | Five argparse-to-Click traps verified against Click 8.4 documentation; wire-protocol timing risk grounded in pyserial buffering semantics; bug characterization identified via direct code reading |

**Overall confidence:** HIGH

### Gaps to Address During Planning

- COMMAND_FW_VERSION status: Research identifies it as possibly missing from constants.py. Inspect constants.py directly before Phase 39 starts.
- argcomplete operator dependency: Whether shell completion is actively used is not determinable from codebase inspection alone.
- _merge_databases shallow-update bug scope: Whether any existing ~/.firestarter/database.json overrides have nested dicts affected requires operator confirmation.
- Buffer-size constant usages post-split: After Phases 38/40, run grep -r '\b512\b\|\b1024\b' firestarter/ to confirm no bare integer literals in ops/serial context outside constants.py.
- Coverage ratchet schedule: Set realistic per-phase targets during Phase 36 planning once the baseline measurement is available.

---

## Sources

### Primary (HIGH confidence -- direct codebase inspection + PyPI verification)

- firestarter_app/firestarter/main.py — 418-line dispatcher, 14 branches, 9 chip-lookup copy-paste sites, build_arg_flags attribute-vs-truthiness bug confirmed
- firestarter_app/firestarter/serial_comm.py — 1037 lines, 4 mixed concerns, _read_and_parse_lines sliding-window timeout, COMMAND_FW_VERSION reference
- firestarter_app/firestarter/database.py — pin_conversions hardcoded dict, singleton pattern, dead comment block L503-519
- firestarter_app/firestarter/eprom_operations.py — boolean return convention, globals() introspection L167
- firestarter_app/firestarter/constants.py — star-import usage, firmware-contract blocks
- firestarter_app/tests/conftest.py, tests/test_decoder.py, tests/test_revision_constants_parity.py — existing test patterns used as structural references
- firestarter_app/pyproject.toml — entry point, dependency list
- firestarter/include/firestarter.h — COMMAND_* and FLAG_* values verified against constants.py
- .planning/PROJECT.md — v1.8 scope decisions, GATE-1.8, v1.9 RCA seed, flat-layout decision
- firestarter_app/CLAUDE.md — constants sync requirements, WARNING-5 database override
- PyPI (2026-05-27): all tool versions confirmed

### Secondary (HIGH confidence -- official documentation)

- Click 8.4 documentation: exit code semantics (standalone_mode, ClickException.exit_code, UsageError), CliRunner, shell_complete, ParamType
- mypy documentation: per-module overrides, gradual adoption pattern
- ruff documentation: --add-noqa baseline strategy, rule set categories, pre-commit hooks
- pyserial documentation: in_waiting not implemented by BytesIO

---

*Research completed: 2026-05-27*
*Ready for roadmap: yes*

# Roadmap: Firestarter — Protocol-Aware Programming Architecture

## Milestones

- ✅ **v1.0 Protocol-Aware Programming Architecture** — Phases 1-13 (shipped 2026-05-11)
- ⏸ **v1.1 Safety Closure & Hardware Validation** — Phases 1-3 done, Phase 4 hardware-validation parked (FM1608 byte-0 bug); Phase 5 milestone-close deferred. Original artifacts preserved at `.planning/milestones/v1.1-paused/`.
- ✅ **v1.2 Message-ID Logging Rework** — Phases 6-10 (shipped 2026-05-19); Phase 10 closed by `/gsd-complete-milestone` (DOC-02)
- ⏸ **v1.3 CMOS EPROM Family Hardware Validation** — Phases 11-14 (PAUSED 2026-05-20, hardware-gated). Phase 11 shipped + Phase 12 Wave 0 scaffold committed; Plans 12-01/02/03 + Phases 13/14 await operator bench hardware.
- ✅ **v1.4 Beta & Pre-release Deployment Pipeline** — Phases 15-20 (shipped 2026-05-20; ship tag `3.0.0b3` in both sub-repos; hardware-flash validated on Uno + Leonardo). Parallel beta channel for both sub-repos without disrupting the stable main → release pipeline.
- ✅ **v1.5 Arduino Uno (ATmega328PB) Board Support** — Phases 21-25 (shipped 2026-05-21; ship tag `3.0.0b4`; bench-validated on operator's 328PB-Uno via `urclock` bootloader). `uno328pb` as a third first-class firmware target alongside `uno` + `leonardo`. Full detail in `.planning/milestones/v1.5-ROADMAP.md`; bench evidence in `.planning/v1.5-BENCH-RESULTS.md`.
- ⏸ **v1.6 Fix the Read Bug** — Phases 26-30 (SHIPPED 2026-05-26 as "diagnostic + revert" per D-17v2). Read-bug carries to v1.9 as Bug A + Bug B RCA seed.
- ✅ **v1.7 RURP Shield Hardware Investigation & Version Detection** — Phases 31-35 (SHIPPED 2026-05-26). Per-rev capability table + labeled schematics + shield-version-detect firmware plumbing.
- 🚧 **v1.8 Host CLI Structural Cleanup (firestarter_app)** — Phases 36-43 (STARTED 2026-05-27). Decompose god functions, argparse→Click, split serial layer, consolidate constants, unify errors, tests-first, ruff+ruff-format+mypy gate. Host-only; firmware sub-repo untouched.

## v1.8 — Host CLI Structural Cleanup (firestarter_app) (STARTED 2026-05-27)

**Milestone goal:** Make the `firestarter_app` Python host code structured, readable, and spaghetti-free — without changing the wire protocol or end-user command surface (except intentional, documented bug fixes). Specifically: decompose the 418-line `main()` dispatcher and the 1037-line `serial_comm.py`; migrate argparse to Click; introduce a characterization test safety net on the currently-untested core paths; consolidate wire-protocol constants; unify error handling; and gate everything with ruff + ruff-format + mypy + CI.

**Status:** Roadmap created 2026-05-27. Phase numbering continues from v1.7 last phase 35 (next phase = 36). All 8 phases are desk-side (pure software — no bench hardware required).

**Granularity:** Comprehensive — 8 phases for a broad refactoring milestone. Each phase delivers one independently-verifiable structural capability: safety net → tooling gate → low-risk extractions → DB cleanup → serial restructure → CLI migration → quality sweep → close. Coverage 27/27.

**Standing gate (applies to every phase):** GATE-1.8 (a–e) is a non-regression contract, not a phase. Every phase MUST satisfy all five sub-clauses before its plans are marked complete:

- **GATE-1.8a**: Wire protocol stays byte-identical (`_read_and_parse_lines` atomic-read invariant preserved; serial framing/CRC/timeout semantics unchanged).
- **GATE-1.8b**: End-user CLI surface preserved — command names, flags, defaults, exit codes, output. Verified by characterization tests.
- **GATE-1.8c**: Firmware/app constant contract preserved — `constants.py` values equal `firestarter/include/firestarter.h`; guarded by parity tests.
- **GATE-1.8d**: Host read path ring-fenced — changes to `read_eprom()` / `read_data_block()` are structural-only so v1.9 RCA baseline binaries stay valid.
- **GATE-1.8e**: Full test suite (existing + new) green; pip entry point (`firestarter`) installs and runs.

**Branch model:** Per memory [[feedback_branching]] — meta-repo branch `v1.8-app-cleanup` off `main`; `firestarter_app` sub-repo branch `v1.8-app-cleanup` off `beta`; firmware sub-repo untouched. Promote `firestarter_app` → `beta` → `main` per the established beta→stable pattern after green (Phase 43).

**Phase numbering:** Phases 36-43 (continues from v1.7 last phase 35).

### Phases

- [x] **Phase 36: Characterization Test Baseline** (completed 2026-05-27) — Write characterization (golden) tests for the currently-untested CLI surface, serial frame-parse path, and EPROM database layer; extend firmware-contract parity test; remove EpromDatabase singleton (prerequisite for testability). Safety net committed before any structural change.
- [ ] **Phase 37: Tooling Baseline + CI Gate** — Configure ruff, ruff-format, and mypy in `pyproject.toml`; run format + baseline pass on the codebase; add GitHub Actions CI step enforcing lint/format/type with coverage gate. Zero new violations permitted after this phase.
- [ ] **Phase 38: Low-Risk Extractions** — Extract `frame_parser.py` (CRC + decode, pure functions), `codec.py` (message formatting), `address_parser.py` (hex/decimal parsing), and `exceptions.py` (consolidated exception hierarchy); delete confirmed dead code (`read_data_block`, `globals()` introspection, commented-out blocks). Mechanical moves verified by the full test suite after each file move.
- [ ] **Phase 39: Database Cleanup + chip_resolver** — Introduce `chip_resolver.py` with `resolve_chip()` eliminating the 9× chip-lookup copy-paste; add type hints + docstrings to `EpromDatabase`; replace all `from firestarter.constants import *` star-imports with named imports; verify/add `COMMAND_FW_VERSION`; consolidate wire-protocol constants.
- [ ] **Phase 40: Serial / Transport Restructure** — Clean up `serial_comm.py` post-Phase-38: extract `_validate_firmware_version` as a testable `@staticmethod`; add type hints to all public `SerialCommunicator` methods; delete `STATE_MACHINE_PREFIXES` dead code; confirm `_read_and_parse_lines` generator body is byte-identical (add `# DO NOT MODIFY — v1.9 RCA territory` marker).
- [ ] **Phase 41: CLI Migration argparse → Click** — Migrate from argparse to Click; create `cli_handlers.py` with one `@cli.command()` per user command; reduce `main()` to ≤ 50 lines; handle all five argparse→Click behavioral traps explicitly; fix `build_arg_flags` latent bug (INTENTIONAL BEHAVIOR CHANGE documented); confirm pip entry point and shell-completion behavior with operator.
- [ ] **Phase 42: Error Handling Normalization + Quality Sweep** — Enforce consistent exception/exit-code convention throughout; eliminate bare `except:` clauses; add return type annotations on all public functions in touched modules; add module + public-function docstrings; normalize naming; run final ruff + mypy sweep with raised coverage threshold.
- [ ] **Phase 43: Documentation + Milestone Close** — Update `firestarter_app` README + contributor docs for the new flat-module structure and tooling workflow; write MILESTONES.md v1.8 entry; update PROJECT.md "Validated"; archive phase directories; verify GATE-1.8 end-to-end; promote branch `v1.8-app-cleanup` → `beta` → `main`.

### Phase Details

#### Phase 36: Characterization Test Baseline

**Goal:** A comprehensive safety net of characterization tests is committed — pinning the current CLI command surface, serial frame-parse path, and EPROM database layer — so that any behavioral regression introduced by subsequent structural phases is caught immediately. The EpromDatabase singleton is removed to make the DB independently testable. The firmware-contract parity test is extended to cover all COMMAND_*, FLAG_*, and CTRL_* values.
**Depends on:** Nothing (additive only; no existing code changed except singleton removal).
**Requirements:** TEST-01, TEST-02, TEST-03, TEST-04, TEST-05
**Success Criteria** (what must be TRUE):

  1. `tests/test_characterization.py` (or equivalent) covers all 14 CLI commands + `dev` sub-commands using Click's `CliRunner` + syrupy snapshots, pinning exit codes and output. Tests for `build_arg_flags` and `COMMAND_FW_VERSION` issues carry explicit `# BUG:` markers asserting the corrected behavior once fixed — they do NOT pin the broken behavior.
  2. `tests/test_decoder_characterization.py` (or equivalent) pins the `_read_and_parse_lines` preamble → body → terminator sequence using the existing `BytesIO` fake-serial fixture; a delayed-response test asserts the sliding-window timeout resets on every yield (invariant explicitly documented in test).
  3. `EpromDatabase` construction is injectable (Click context / DI via constructor parameter); `tests/test_eprom_database.py` covers `get_eprom`, `convert_to_programmer`, and DIP→RURP pin translation against real `chip_database.json` data — without `find_and_connect` or serial I/O.
  4. `tests/test_firmware_contract_parity.py` extends the existing `test_revision_constants_parity.py` pattern to cover all `COMMAND_*`, `FLAG_*`, and `CTRL_*` blocks; each assertion uses a hard-coded hex literal matching `firestarter/include/firestarter.h`; test is `skipif` when the firmware checkout is absent.
  5. All existing tests plus the new suite pass (`pytest` exits 0); `ruff` and `mypy` run without configuration errors (violations recorded as baseline watermark, not fixed yet).

**UI hint:** no

**Plans:** 4 plans (2 waves)
Plans:
**Wave 1**

- [x] 36-01-PLAN.md — Foundations: pyproject `test` dep group (syrupy) + EpromDatabase de-singleton seam (wave 1)
- [x] 36-02-PLAN.md — TEST-04 firmware-parity extension (COMMAND_*/FLAG_*/CTRL_*) + TEST-02 serial frame-parse pin (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 36-03-PLAN.md — TEST-01 CLI surface subprocess goldens + in-process happy-paths + committed syrupy snapshots (wave 2)
- [x] 36-04-PLAN.md — TEST-03 EpromDatabase unit tests + TEST-05 two xfail(strict) bug pins (wave 2)

#### Phase 37: Tooling Baseline + CI Gate

**Goal:** ruff, ruff-format, and mypy are configured and enforced in CI. All existing code is formatted and linted to a green baseline (using `ruff check --add-noqa` for legacy violations, not hand-fixing everything). From this phase forward, touched modules must be clean; the CI gate fails the build on any new violation.
**Depends on:** Phase 36 (characterization test suite must pass under the new linting rules).
**Requirements:** TOOL-01, TOOL-02, TOOL-03
**Success Criteria** (what must be TRUE):

  1. `pyproject.toml` contains `[tool.ruff]` (E, F, I rules minimum; UP added; no `select = ["ALL"]`), `[tool.ruff.format]`, and `[tool.mypy]` sections with documented rationale for any selected rules; `ruff check` and `ruff format --check` both exit 0 on the full tree.
  2. mypy runs with `disallow_untyped_defs = false` globally (gradual adoption); initial error count recorded as the watermark comment in `pyproject.toml`; the gate is "no new errors vs. watermark"; `[[tool.mypy.overrides]]` strict list starts with the new Phase 36 test modules.
  3. A CI workflow step (in the existing `firestarter_app` GitHub Actions file) runs `ruff check`, `ruff format --check`, and `mypy`, plus `pytest` with `--cov` and a coverage gate (D-04: measured 51.33% → floor set at 50%, ratcheted to ≥ 70% in Phase 42), and fails the build on any violation; a `pre-commit` config with the same hook order (ruff-check → ruff-format → mypy) is committed.

**UI hint:** no

**Plans:** 3 plans (3 waves)Plans:
**Wave 1**

- [x] 37-01-PLAN.md — ruff + mypy config in pyproject.toml + green-baseline transform (format / import-sort / 2× noqa) + .git-blame-ignore-revs (TOOL-01, wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 37-02-PLAN.md — measure + record mypy watermark + tools/check_mypy_watermark.py + coverage config + pytest-cov/types-pyserial deps (TOOL-02, TOOL-03, wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 37-03-PLAN.md — extend ci.yml (all-PR trigger + folded gate steps + .[test] install) + .pre-commit-config.yaml (TOOL-03, wave 3)

#### Phase 38: Low-Risk Extractions

**Goal:** Pure-compute code is extracted into new flat sibling modules with zero runtime behavior change. `exceptions.py` consolidates all exception classes (prerequisite for Phases 39, 40, 41). `frame_parser.py`, `codec.py`, and `address_parser.py` are independently testable without serial I/O. Dead code is deleted. The full test suite passes unchanged after every file move.
**Depends on:** Phase 37 (tooling gate enforced so extractions produce clean diffs; no formatting noise mixed with logic changes).
**Requirements:** STRUCT-01, STRUCT-02, STRUCT-03, STRUCT-04, STRUCT-05
**Success Criteria** (what must be TRUE):

  1. `firestarter/exceptions.py` exists and contains all application exception classes (`SerialError`, `SerialTimeoutError`, `ProgrammerNotFoundError`, `FirmwareOutdatedError`, `EpromOperationError`, `HardwareOperationError`, `ChipNotFoundError`); all former import sites updated; no exception class defined outside this module.
  2. `firestarter/frame_parser.py` exists containing `_build_crc8_table`, `_crc8_ccitt`, `_decode_param`, `_decode_id_frame`, `Response`, `LogMessage`, `MAGIC_PREAMBLE`; it has no imports from within the `firestarter` package (stdlib + typing only); `test_decoder.py` passes unchanged (the generator body in `serial_comm.py` is not touched).
  3. `firestarter/codec.py` exists containing `_format_message` (renamed `format_message`) and `_REVISION_SILKSCREEN`; it imports from `constants.py` and `messages.py` only; new `tests/test_codec.py` covers `format_message` with message catalog fixtures.
  4. `firestarter/address_parser.py` exists with `parse_address(s: str | None) -> int | None` and `parse_size` raising `ValueError` on bad input; `tests/test_address_parser.py` covers hex, decimal, `None`, and invalid inputs.
  5. `read_data_block` is deleted from `serial_comm.py` (dead code per W-04 MSG_DATA_CHUNK migration, commit message cites the migration); `globals()` introspection in `eprom_operations.py` is replaced with explicit `COMMAND_NAMES` lookup; confirmed dead commented-out blocks are removed; `pytest` exits 0.

**UI hint:** no

#### Phase 39: Database Cleanup + chip_resolver

**Goal:** The 9× chip-lookup boilerplate copy-pasted across handlers is eliminated by a single `resolve_chip()` function. All `from firestarter.constants import *` star-imports are replaced with named imports (prerequisite for tightening the mypy gate). Wire-protocol constants are consolidated with clear firmware-sync markers; `COMMAND_FW_VERSION` is verified present (added if missing). The DIP→RURP pin-mapping documentation is clarified to eliminate the apparent "two sources of truth" ambiguity.
**Depends on:** Phase 38 (`exceptions.py` must exist so `chip_resolver.py` can import `ChipNotFoundError`).
**Requirements:** DATA-01, DATA-02, DATA-03, DATA-04
**Success Criteria** (what must be TRUE):

  1. `firestarter/chip_resolver.py` exists with `resolve_chip(name: str) -> dict` raising `ChipNotFoundError` on miss; `tests/test_chip_resolver.py` (from Phase 36) passes; `grep -n "db.get_eprom\|convert_to_programmer" firestarter/main.py` returns no results (the 9 copy-paste sites are gone).
  2. `database.py`'s `pin_conversions` dict has a docstring explicitly stating it encodes RURP board-wiring (DIP socket position → bus line number), distinct from `pinouts.json` which encodes chip DIP pinout (function → socket position); no code behavior is changed.
  3. `grep -r "from firestarter.constants import \*" firestarter/` returns no results; all four previously-star-importing modules (`main.py`, `serial_comm.py`, `eprom_operations.py`, `database.py`) use explicit named imports; mypy error count on those modules does not increase vs. the Phase 37 watermark.
  4. `constants.py` contains `COMMAND_FW_VERSION` (added if absent, with value verified against `firestarter/include/firestarter.h`); all wire-protocol constant blocks (`COMMAND_*`, `FLAG_*`, `CTRL_*`, `REVISION_*`) have a `# Firmware sync: firestarter.h` marker comment; `tests/test_firmware_contract_parity.py` passes.

**UI hint:** no

#### Phase 40: Serial / Transport Restructure

**Goal:** `serial_comm.py` owns only transport concerns after Phase 38's extractions. `_validate_firmware_version` is an extractable `@staticmethod` with direct unit tests. The `_read_and_parse_lines` generator body is explicitly ring-fenced with a comment. Type hints are added to all public `SerialCommunicator` methods. Wire behavior is verified byte-identical by the existing test suite.
**Depends on:** Phase 38 (frame decode logic already extracted; `exceptions.py` import surface stable; Phase 39 preferred but not strictly required — serial cleanup does not depend on chip_resolver).
**Requirements:** SERIAL-01, SERIAL-02, SERIAL-03
**Success Criteria** (what must be TRUE):

  1. `SerialCommunicator` owns only socket lifecycle, `send_*`, `get_response`, `expect_ack`, `consume_remaining_input`, `disconnect`, `find_and_connect`, `_probe_port`, `_list_potential_ports`, and `_read_and_parse_lines`; all frame-decode and message-format concerns are delegated to `frame_parser` + `codec` imports; `STATE_MACHINE_PREFIXES` empty-list dead code is deleted.
  2. `SerialCommunicator._validate_firmware_version(version_str: str) -> None` is a `@staticmethod`; `tests/test_fw_version_guard.py` covers the version-guard logic directly without a fake serial (passes on "3.0.0", raises `FirmwareOutdatedError` on "2.9.9").
  3. `_read_and_parse_lines` carries a `# DO NOT MODIFY — v1.9 RCA territory` comment at its function header; the generator body is byte-identical to pre-v1.8 (verified by `test_decoder.py` passing unchanged); all public `SerialCommunicator` methods have type-annotated signatures; `pytest` exits 0.

**UI hint:** no

#### Phase 41: CLI Migration argparse → Click

**Goal:** The 418-line `main()` dispatcher is replaced by a Click command group; `cli_handlers.py` contains one `@cli.command()` decorated function per user command; `main.py` is ≤ 50 lines. All five argparse→Click behavioral traps are handled explicitly. The `build_arg_flags` bug is fixed with an INTENTIONAL BEHAVIOR CHANGE commit. The pip entry point works; shell-completion behavior is confirmed or explicitly dropped with operator sign-off.
**Depends on:** Phase 39 (chip_resolver.py must exist for handlers to call `resolve_chip()`); Phase 40 (stable exception import surface from `exceptions.py`; `SerialCommunicator` public API clean).
**Requirements:** CLI-01, CLI-02, CLI-03, CLI-04
**Success Criteria** (what must be TRUE):

  1. `firestarter` CLI passes all characterization tests from Phase 36 (CliRunner exit codes and output snapshot-match pre-migration behavior for all 14 commands + `dev` sub-commands); the five argparse→Click traps are addressed: exit codes via `raise click.ClickException` / `sys.exit`, no prefix matching assumed, `--no-blank-check` polarity correct (`is_flag=True, default=True`), `--pre`/`--firmware-version`/`--stable` mutex enforced via Click callback guard, `_validate_firmware_version` wired as Click param type or callback.
  2. `firestarter/cli_handlers.py` exists with one `@cli.command()` per top-level user command; `firestarter/main.py` is ≤ 50 lines (imports, Click group definition, global options, entry-point call); `if args.command ==` dispatch chain is gone.
  3. `build_arg_flags` attribute-vs-truthiness bug is fixed; commit message contains `INTENTIONAL BEHAVIOR CHANGE: build_arg_flags "if force in args" corrected to truthiness check` and a one-line explanation; the Phase 36 characterization test (previously marked `# BUG:`) now asserts the corrected behavior and passes.
  4. `pip install -e . && firestarter --help` runs successfully (CI smoke test); `argcomplete` dependency is either removed (with Click shell completion wired as its replacement) or retained with explicit operator sign-off on the deferral; the outcome is documented in the commit message.

**UI hint:** no

#### Phase 42: Error Handling Normalization + Quality Sweep

**Goal:** Consistent exception/exit-code convention enforced throughout the codebase. No bare `except:` clauses. Return type annotations on all public functions in touched modules (those modules are mypy-clean under the configured strictness). Module and public-function docstrings present on everything touched this milestone. Dead code and naming inconsistencies resolved. Final ruff + mypy sweep with raised coverage threshold.
**Depends on:** Phase 41 (quality sweep most efficient post-restructure; performing it before would require doing it again).
**Requirements:** ERR-01, ERR-02, ERR-03
**Success Criteria** (what must be TRUE):

  1. Service and transport layers raise typed exceptions from `exceptions.py`; the Click boundary in `cli_handlers.py` maps them to stable exit codes (0 success, 1 expected failure, 2 usage error via `click.UsageError`); `grep -rn "except:" firestarter/` returns no bare excepts; `grep -rn "except Exception" firestarter/` results are all logged with `as e`.
  2. All public functions in modules touched during v1.8 (at minimum `main.py`, `cli_handlers.py`, `chip_resolver.py`, `frame_parser.py`, `codec.py`, `address_parser.py`, `exceptions.py`, `serial_comm.py`) have return type annotations; those modules are added to the mypy `[[tool.mypy.overrides]]` strict list; `mypy` exits 0 for those modules.
  3. All public classes and methods in touched modules have docstrings (1-liner minimum); naming is normalized to snake_case throughout (no camelCase legacy); `ruff check` exits 0 with no `# noqa` suppressions added by Phase 42; `pytest --cov` coverage threshold is raised to ≥ 70% and passes.

**UI hint:** no

#### Phase 43: Documentation + Milestone Close

**Goal:** v1.8 is closed cleanly — the `firestarter_app` README and contributor docs reflect the new flat-module structure and tooling workflow, MILESTONES.md captures the delivery, PROJECT.md is updated, phase directories are archived, GATE-1.8 is verified end-to-end, and the branch is promoted per the established beta→stable pattern.
**Depends on:** Phases 36–42 (everything that produced the refactored codebase).
**Requirements:** DOC-01, DOC-02, MS-01
**Success Criteria** (what must be TRUE):

  1. `firestarter_app/README.md` and any contributor/development docs reflect the post-v1.8 flat-module map (listing `frame_parser.py`, `codec.py`, `address_parser.py`, `chip_resolver.py`, `cli_handlers.py`, `exceptions.py`), the tooling workflow (`ruff`, `ruff format`, `mypy`, `pytest --cov`), and the Click-based CLI structure; the docs accurately describe the layer boundary rules.
  2. MILESTONES.md grows a v1.8 entry covering: delivered structural changes, new modules introduced, requirements closed, known intentional behavior changes, and the v1.9 read-path ring-fence status; PROJECT.md "Validated" section grows entries for each major structural change; the v1.8 milestone block in PROJECT.md is rewritten as "Shipped 2026-05-XX".
  3. Phase artifacts are archived under `.planning/milestones/v1.8-phases/` via the archive script pattern; GATE-1.8 (a–e) is verified end-to-end (wire protocol byte-identical confirmed by `firestarter read` on real hardware or `test_decoder.py` characterization; CLI surface verified by CliRunner; parity test green; entry point smoke test green); `firestarter_app` branch `v1.8-app-cleanup` is promoted → `beta` → `main` per the operator-authorized branch promotion pattern.

**UI hint:** no

### v1.8 Coverage

| Requirement | Phase | Status |
|-------------|-------|--------|
| TEST-01 | Phase 36 | Complete |
| TEST-02 | Phase 36 | Complete |
| TEST-03 | Phase 36 | Complete |
| TEST-04 | Phase 36 | Complete |
| TEST-05 | Phase 36 | Complete |
| TOOL-01 | Phase 37 | Pending |
| TOOL-02 | Phase 37 | Pending |
| TOOL-03 | Phase 37 | Pending |
| STRUCT-01 | Phase 38 | Pending |
| STRUCT-02 | Phase 38 | Pending |
| STRUCT-03 | Phase 38 | Pending |
| STRUCT-04 | Phase 38 | Pending |
| STRUCT-05 | Phase 38 | Pending |
| DATA-01 | Phase 39 | Pending |
| DATA-02 | Phase 39 | Pending |
| DATA-03 | Phase 39 | Pending |
| DATA-04 | Phase 39 | Pending |
| SERIAL-01 | Phase 40 | Pending |
| SERIAL-02 | Phase 40 | Pending |
| SERIAL-03 | Phase 40 | Pending |
| CLI-01 | Phase 41 | Pending |
| CLI-02 | Phase 41 | Pending |
| CLI-03 | Phase 41 | Pending |
| CLI-04 | Phase 41 | Pending |
| ERR-01 | Phase 42 | Pending |
| ERR-02 | Phase 42 | Pending |
| ERR-03 | Phase 42 | Pending |
| DOC-01 | Phase 43 | Pending |
| DOC-02 | Phase 43 | Pending |
| MS-01 | Phase 43 | Pending |

**Mapped: 30/30 (27 v1 requirements + DOC-01, DOC-02, MS-01) ✓** — no orphans, no duplicates.
**GATE-1.8 (a–e):** Standing cross-cutting gate applied at every phase; not a phase itself.

## v1.7 — RURP Shield Hardware Investigation & Version Detection (SHIPPED 2026-05-26)

<details>
<summary>✅ v1.7 shipped — per-rev capability table + labeled schematics + shield-version-detect firmware plumbing (5 phases). Full detail in `.planning/MILESTONES.md` §v1.7.</summary>

- **Phases:**
  - [x] Phase 31: Upstream Shield Archaeology (HW-INV-01, HW-INV-02, HW-INV-03, SILK-01)
  - [x] Phase 32: Inter-Rev Difference + Capability Matrix (DIFF-01, DIFF-02, CAPS-01, CAPS-02)
  - [x] Phase 33: Silkscreen Label → Code Alias Migration (ALIAS-01, ALIAS-02, ALIAS-03)
  - [x] Phase 34: Shield-Version-Detect Design + Firmware Plumbing (DETECT-HW-01, DETECT-HW-02, DETECT-FW-01, DETECT-FW-02)
  - [x] Phase 35: Documentation + Milestone Close (DOC-01, MS-01)
- **Canonical reference:** `.planning/v1.7-SHIELD-REVS.md` (9 sections: inventory, difference matrix, capability matrix, alias table, detect-hw schematic delta, per-rev ADC band table, labeled schematics, operator-board annotations, v1.8 hand-off).
- See full archive: `.planning/MILESTONES.md` §v1.7.

</details>

## v1.6 — Fix the Read Bug (SHIPPED 2026-05-26 — diagnostic + revert)

<details>
<summary>✅ v1.6 shipped — ships as "diagnostic + revert" per D-17v2 (5 phases, 13 plans). Read-bug carries to v1.9 with Bug A + Bug B pattern findings as RCA seed. Full detail in `.planning/MILESTONES.md` §v1.6.</summary>

- **Ship tag:** `3.0.0b6` (beta-only; both sub-repos lockstep)
- **Phases:**
  - [x] Phase 26: Cross-board Reproduction & Diagnostic Tooling (2 plans; REPRO-01..03)
  - [x] Phase 27: Root Cause Analysis (3 plans incl. re-open Plan 27-05; RCA-01..03)
  - [x] Phase 28: Fix Implementation + Unit Test Coverage (4 plans incl. revert Plan 28-03 + parked Plan 28-04; FIX-01..03 as diagnostic + revert)
  - [x] Phase 29: Multi-Board Bench Verification (4 plans incl. v2 re-iteration Plans 29-03/04; VERIFY-02 PASS via structured_data shape; VERIFY-01/03/04 DEFERRED to v1.9)
  - [x] Phase 30: Documentation + Milestone Close (3 plans; DOC-01/02 + MS-01)
- **Re-scope (D-17v2):** Phase 29 v1 Wave B FAIL → Plan 27-05 re-open confirmed dual-cause (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb hardware) → Plan 28-03 reverted `437339b6` via `ea25174`; `4f205e58` `_NOP()` settling preserved (Plan 28-04 parks) → Phase 29 v2 PASS_PARKED (Leonardo Modified Rev 0 returns to Phase 26 baseline; WORST 0.047% zeros vs 83.8% pre-revert).
- **v1.9 hand-off:** 15 N=5 W27C512 binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`; Bug A (Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew) + Bug B (Rev 2.0 /CE-or-/OE timing + VPP=13.1V) characterized in `.planning/v1.6-EVIDENCE.md` Phase 29 v2 H3 block + `.planning/milestones/v1.6-phases/29-multi-board-bench-verification/29-04-SUMMARY.md`.
- See full archive: `.planning/MILESTONES.md` §v1.6, `.planning/milestones/v1.6-REQUIREMENTS.md`, `.planning/v1.6-EVIDENCE.md`.

</details>

## v1.5 — Arduino Uno (ATmega328PB) Board Support (SHIPPED 2026-05-21)

<details>
<summary>✅ v1.5 shipped — `uno328pb` as third first-class firmware target (5 phases, 6 plans). Full detail in `.planning/milestones/v1.5-ROADMAP.md`.</summary>

- **Ship tag:** `3.0.0b4` (both sub-repos, GitHub Pre-release on each).
- **Phases:**
  - [x] Phase 21: Firmware Target — `uno328pb` (2 plans; FW-01..FW-04)
  - [x] Phase 22: Release Pipeline Artifacts (1 plan; REL-01, REL-02)
  - [x] Phase 23: Host CLI Installer Integration (2 plans; INST-01..03, GATE-01)
  - [x] Phase 24: Bench Validation on 328PB-Uno (operator-on-bench; BENCH-01, BENCH-02)
  - [x] Phase 25: Documentation + Milestone Close (1 plan; DOC-01, DOC-02, MS-01)
- **Bench-validated** on operator's 328PB-Uno via `firestarter fw -i --pre` end-to-end on `/dev/ttyUSB0` with `urclock` bootloader. Post-flash handshake reports `v3.0.0b4 / uno328pb`.
- **Open v1.9 backlog** carried forward (3 todos): `large-read-data-jitter-uno328pb` (HIGH, pre-existing, affects all controllers — now in scope for v1.9), `w27c512-eeprom-misclassification` (HIGH, operator-tagged asap), `avrdude-mcu-detection-fallback` (low).
- See full archive: `.planning/milestones/v1.5-ROADMAP.md`, `.planning/milestones/v1.5-REQUIREMENTS.md`, `.planning/v1.5-BENCH-RESULTS.md`.

</details>

## v1.3 — CMOS EPROM Family Hardware Validation (PAUSED 2026-05-20)

**Milestone goal:** Bench-validate, on real silicon and on both Arduino Uno + Leonardo, that the algorithm-0x07 (28-pin DIP CMOS UV-EPROM, 212 chips in DB) and algorithm-0x08 (32-pin DIP CMOS UV-EPROM, 127 chips in DB) dispatch logic shipped in v1.0–v1.2 actually programs, reads back, and verifies cleanly across the full 32K → 512K density span. This is **validation, not new features** — architecture is locked.

**Status:** ⏸ Paused 2026-05-20 — hardware-gated. Phase 11 shipped clean; Phase 12 Wave 0 desk-side scaffold committed; Plans 12-01/02/03 (BENCH-01/02/05 — W27C512, SST27SF512, W27C257) + entire Phase 13 + Phase 14 await operator bench hardware (Uno + Leonardo + RURP shield + DIP-28 socket + scope + bench chips). Resume command: `/gsd-execute-phase 12 --wave 1 --interactive` once hardware is available.

**Granularity:** Comprehensive (compressed — focused validation milestone, not a build milestone).
**Phase numbering:** Phases 11-14 (continues from v1.2 close).

### Structural Notes

- **Bench-gated vs. desk-side split.** Phase 11 (coverage matrix + DB inconsistency report) is fully desk-side and can land without hardware. Phases 12 and 13 are operator-on-bench (Uno + Leonardo + chip socket + scope). Phase 14 is paperwork only.
- **PROTO-01/02 are observation protocols, not standalone phases.** Chip-ID read at the start of every BENCH cycle (PROTO-01) and scope-measured VPP at the chip socket during write (PROTO-02) are practiced in Phase 12 where the protocol is established, then carried forward into Phase 13. They map formally to Phase 12 (where the observation protocol is set up + first applied) but the success-criteria coverage runs across both bench phases.
- **Density coverage strategy.** Phase 12 covers the 28-pin / algo-0x07 family at both the marquee 64K size (W27C512, SST27SF512) and the 32K low end (BENCH-05). Phase 13 mirrors this for 32-pin / algo-0x08 at 256K + 512K (W27C020, W27E040) and the 128K low end (BENCH-06). Together this exercises the full address-bus span end-to-end.
- **Deferred v1.2 items.** BENCH-01 (W27C512 bench cycle) naturally closes the four v1.2 hardware-pending UAT items (Phase 08 SC#2/SC#3, Phase 08 HUMAN-UAT.md, Phase 09 Plan-05 Task 3 chip-seated W27C512 UAT). Phase 12 detail flags this closure.
- **Flash budget floor.** v1.2 ship state (Leonardo 24,482 B / 85.4%, Uno 22,262 B / 69.0%, firmware 3.0.0-dev) is a non-regress floor. v1.3 is read-only against firmware semantics; only defect-driven changes are in scope.

### Phases

- [x] **Phase 11: Coverage Matrix & DB Inconsistency Audit** — Desk-side enumeration of all 339 algo-0x07/0x08 DB rows + flag intra-algorithm inconsistencies. ✅ 2026-05-19
- [ ] **Phase 12: 28-Pin / Algo-0x07 Bench Validation** — End-to-end bench cycle on Uno + Leonardo for W27C512, SST27SF512, and the 32K density-low representative; establish chip-ID + VPP scope observation protocols. ⏸ Paused (Wave 0 shipped; Waves 1-3 await hardware)
- [ ] **Phase 13: 32-Pin / Algo-0x08 Bench Validation** — End-to-end bench cycle on Uno + Leonardo for W27C020, W27E040, and the 128K density-low representative; same observation protocols carried forward. ⏸ Paused
- [ ] **Phase 14: Milestone Close & Artifacts** — Publish BENCH-RESULTS, update MILESTONES, archive v1.3 phase directories. ⏸ Paused

### Phase Details

#### Phase 11: Coverage Matrix & DB Inconsistency Audit

**Goal:** Operator has a complete, single-source coverage map of every algo-0x07 + algo-0x08 chip in `chip_database.json`, with intra-algorithm DB inconsistencies surfaced as defect candidates for follow-up milestones.
**Depends on:** Nothing (desk-side; can land before any bench session).
**Requirements:** COV-01, COV-02
**Success Criteria** (what must be TRUE):

  1. A coverage matrix file exists at `.planning/v1.3-COVERAGE-MATRIX.md` (or equivalent) enumerating every algo-0x07 + algo-0x08 row in `chip_database.json` with: manufacturer, part_number(s), pin_count, size_bytes, pulse_duration, chip_id_check, chip_id_value, pinout class. Total row count matches DB histogram (212 + 127 = 339 chips).
  2. The same file (or a companion file) lists every intra-algorithm DB inconsistency — chips that share `pin_count` + `algorithm` but differ in `pulse_duration`, `chip_id_check`, or `pinout` — with each inconsistency labeled as a defect candidate for v1.4 or a sub-repo PR (no auto-fixes applied in v1.3).
  3. Operator can use the matrix to confirm that the six BENCH chips (BENCH-01..06) span the pinout classes and pulse-duration profiles actually represented in the DB, so bench results generalize to the rest of the 339 rows.

**Plans:** 6 plans

- [x] 11-01-PLAN.md — Wave 0 failing-test scaffold for tests/test_audit_coverage_matrix.py (10 tests) ✅ 2026-05-19
- [x] 11-02-PLAN.md — Wave 1 tool skeleton + CLI + §1 Summary + §2 DB Count Reconciliation ✅ 2026-05-19
- [x] 11-03-PLAN.md — Wave 2 §3 Full Enumeration (339 rows, per-algorithm sub-tables, D-06 sort) ✅ 2026-05-19
- [x] 11-04-PLAN.md — Wave 3 §4 Defect Candidates + DEFECT-COV-NN ledger + --check semantics
- [x] 11-05-PLAN.md — Wave 4 §5 BENCH Coverage Proof + golden-file fixture
- [x] 11-06-PLAN.md — Wave 5 D-07 planning-doc count reconciliation (PROJECT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md) ✅ 2026-05-19

#### Phase 12: 28-Pin / Algo-0x07 Bench Validation

**Goal:** On both Uno and Leonardo, operator can run a full write → read-back → verify cycle on every named 28-pin CMOS UV-EPROM (W27C512, SST27SF512) and on a 32K density-low representative, with chip-ID and VPP observation protocols established and captured.
**Depends on:** Phase 11 (coverage matrix informs which density-low representative is in scope and which pinout classes are exercised). Bench hardware: Uno + Leonardo + RURP shield + DIP-28 socket + scope.
**Requirements:** BENCH-01, BENCH-02, BENCH-05, PROTO-01, PROTO-02
**Plans:** 4 plans (Wave 0 shipped; Waves 1-3 paused on bench hardware)

#### Phase 13: 32-Pin / Algo-0x08 Bench Validation

**Goal:** On both Uno and Leonardo, operator can run a full write → read-back → verify cycle on every named 32-pin CMOS UV-EPROM (W27C020, W27E040) and on a 128K density-low representative, completing the algo-0x08 family coverage at the high (512K) and low (128K) ends of the address-bus span.
**Depends on:** Phase 12 (chip-ID + VPP observation protocols established; bench harness validated against algo-0x07 first).
**Requirements:** BENCH-03, BENCH-04, BENCH-06
**Plans:** TBD (paused on bench hardware)

#### Phase 14: Milestone Close & Artifacts

**Goal:** v1.3 ships with a per-chip, per-board green/red/quirks artifact covering all six BENCH chips and both PROTO observation protocols, plus a clean milestone close (MILESTONES.md updated, phase directories archived).
**Depends on:** Phases 11, 12, 13.
**Requirements:** DOC-01, DOC-02
**Plans:** TBD (paused on bench hardware)

### v1.3 Coverage

| REQ-ID | Phase |
|--------|-------|
| BENCH-01 | Phase 12 |
| BENCH-02 | Phase 12 |
| BENCH-03 | Phase 13 |
| BENCH-04 | Phase 13 |
| BENCH-05 | Phase 12 |
| BENCH-06 | Phase 13 |
| PROTO-01 | Phase 12 (observation protocol carried forward into Phase 13) |
| PROTO-02 | Phase 12 (observation protocol carried forward into Phase 13) |
| COV-01 | Phase 11 |
| COV-02 | Phase 11 |
| DOC-01 | Phase 14 |
| DOC-02 | Phase 14 |

**Mapped: 12/12 requirements ✓** — no orphans, no duplicates.

## Prior Milestones (archived)

<details>
<summary>✅ v1.4 Beta & Pre-release Deployment Pipeline (Phases 15-20) — SHIPPED 2026-05-20</summary>

- [x] **Phase 15**: Versioning & Locked-Step Coordination (foundation) — 4/4 plans
- [x] **Phase 16**: App Beta Release Pipeline — 1/1 plan
- [x] **Phase 17**: Firmware Beta Release Pipeline — 1/1 plan
- [x] **Phase 18**: Beta-Aware Firmware Downloader (`--pre`, `--firmware-version`, `firmware list`) — 2/2 plans
- [x] **Phase 19**: Documentation (READMEs + `v1.4-RELEASE-PROCEDURES.md`) — 1/1 plan
- [x] **Phase 20**: End-to-End Smoke Test + Milestone Close — 1/1 plan

Ship tag: `3.0.0b3` (auto-incremented from `b1` → `b2` → `b3` during live E2E; six substrate defects E2E-01..06 surfaced and fixed in-place during the cut).
Hardware-flash validated: Uno + Leonardo at `3.0.0b3` via `firestarter fw -i --pre`.

Full milestone archive: [`.planning/milestones/v1.4-ROADMAP.md`](milestones/v1.4-ROADMAP.md).
Requirements archive: [`.planning/milestones/v1.4-REQUIREMENTS.md`](milestones/v1.4-REQUIREMENTS.md) (16/16 complete).
Summary: [`.planning/MILESTONES.md`](MILESTONES.md) §v1.4.
Phase archive: [`.planning/milestones/v1.4-phases/`](milestones/v1.4-phases/).

</details>

<details>
<summary>✅ v1.2 Message-ID Logging Rework (Phases 6-9) — SHIPPED 2026-05-19</summary>

- [x] **Phase 6**: Logging Infrastructure (catalog + codegen + helper + decoder) — 6/6 plans
- [x] **Phase 7**: Convert ERROR + WARN + INFO Call-Sites — 13/13 plans
- [x] **Phase 8**: Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END) — 8/8 plans
- [x] **Phase 9**: Delete Old Log Macros + Measure Flash Savings — 5/5 plans
- [x] **Phase 10**: Milestone Close (v1.2) — closed by `/gsd-complete-milestone` (DOC-02)

Full milestone archive: [`.planning/milestones/v1.2-ROADMAP.md`](milestones/v1.2-ROADMAP.md) (frozen snapshot of full phase details + coverage map + dependency graph).

Requirements archive: [`.planning/milestones/v1.2-REQUIREMENTS.md`](milestones/v1.2-REQUIREMENTS.md) (23/23 complete).

Summary: [`.planning/MILESTONES.md`](MILESTONES.md) §v1.2.

</details>

<details>
<summary>⏸ v1.1 Safety Closure & Hardware Validation (Phases 1-5) — PAUSED 2026-05-18</summary>

- [x] **Phase 1**: Safety Closure (Intel-flash VPP, 28C chip-id) — complete
- [x] **Phase 2**: Wire-key rename + minipro attribution scrub — complete
- [x] **Phase 3**: Retroactive VERIFICATION.md for v1.0 phases — complete
- [ ] **Phase 4**: Hardware validation across chip families — Plan 2 of 3 in progress; **FM1608 byte-0 read bug** parked (needs different Uno R3 to unblock; see [`.planning/debug/fm1608-fresh-chip-baseline.md`](debug/fm1608-fresh-chip-baseline.md))
- [ ] **Phase 5**: Milestone close (DOC-01) — deferred until after v1.2 ships or fm1608 unblocks

Original artifacts: [`.planning/milestones/v1.1-paused/`](milestones/v1.1-paused/).

Also carrying: WARNING-4 (`firestarter_test.sh` / `write_test.sh` references to deleted `database_generated.json`).

</details>

<details>
<summary>✅ v1.0 Protocol-Aware Programming Architecture (Phases 1-13) — SHIPPED 2026-05-11</summary>

- [x] Phases 1-13 covering the algorithm-first dispatch architecture (13 phases, 22 plans, 4-day timeline)
- Key deliverables: protocol-prefix dispatch in `memory.cpp`, 743-chip database with explicit `algorithm` integer, five firmware handlers (`configure_eprom`, `configure_flash3`, `configure_flash_intel`, `configure_eeprom28c`, `configure_sram`), pre-write safety stack (VPP ADC compare, chip-ID validation, blank check), static-pin and address-bus correctness

Full archive: [`.planning/milestones/v1.0-ROADMAP.md`](milestones/v1.0-ROADMAP.md) | [`.planning/milestones/v1.0-REQUIREMENTS.md`](milestones/v1.0-REQUIREMENTS.md) | [`.planning/milestones/v1.0-MILESTONE-AUDIT.md`](milestones/v1.0-MILESTONE-AUDIT.md) | [`.planning/milestones/v1.0-INTEGRATION-CHECK.md`](milestones/v1.0-INTEGRATION-CHECK.md) | [`.planning/milestones/v1.0-phases/`](milestones/v1.0-phases/).

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1-13 (v1.0) | v1.0 | 22/22 | ✅ Shipped | 2026-05-11 |
| 1-3 (v1.1) | v1.1 | done | ✅ Complete | 2026-05-12..18 |
| 4 (v1.1) | v1.1 | partial | ⏸ Parked | — (FM1608 blocked) |
| 5 (v1.1) | v1.1 | 0/0 | ⏸ Deferred | — |
| 6-10 (v1.2) | v1.2 | 32/32 | ✅ Shipped | 2026-05-19 |
| 11 | v1.3 | 6/6 | ✅ Complete | 2026-05-19 |
| 12 | v1.3 | 1/4 | ⏸ Paused | — (hardware-gated) |
| 13 | v1.3 | 0/0 | ⏸ Paused | — (hardware-gated) |
| 14 (close) | v1.3 | 0/0 | ⏸ Paused | — (hardware-gated) |
| 15-20 (v1.4) | v1.4 | 10/10 | ✅ Shipped | 2026-05-20 |
| 21-25 (v1.5) | v1.5 | 6/6 | ✅ Shipped | 2026-05-21 |
| 26 | v1.6 | 2/2 | ✅ Complete | 2026-05-21 |
| 27 | v1.6 | 3/2 | ✅ Complete | 2026-05-26 |
| 28 | v1.6 | 4/4 | ✅ Complete | 2026-05-26 |
| 29 | v1.6 | 4/4 | ✅ Complete | 2026-05-26 |
| 30 (close) | v1.6 | 3/3 | ✅ Shipped | 2026-05-26 |
| 31-35 (v1.7) | v1.7 | — | ✅ Shipped | 2026-05-26 |
| 36 | v1.8 | 0/TBD | Not started | — |
| 37 | v1.8 | 0/TBD | Not started | — |
| 38 | v1.8 | 0/TBD | Not started | — |
| 39 | v1.8 | 0/TBD | Not started | — |
| 40 | v1.8 | 0/TBD | Not started | — |
| 41 | v1.8 | 0/TBD | Not started | — |
| 42 | v1.8 | 0/TBD | Not started | — |
| 43 (close) | v1.8 | 0/TBD | Not started | — |

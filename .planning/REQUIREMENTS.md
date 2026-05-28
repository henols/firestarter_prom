# Requirements: Firestarter v1.8 — Host CLI Structural Cleanup (firestarter_app)

**Defined:** 2026-05-27
**Core Value:** Algorithm-first dispatch stays intact — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware. This milestone makes the **host code** that drives that flow structured, readable, and spaghetti-free without changing the wire protocol.

**Milestone type:** Refactoring (no new end-user features). Host-only — the `firestarter` firmware sub-repo is NOT modified.

---

## GATE-1.8 — Non-Regression Contract (applies to EVERY phase)

The behavior gate is **"refactor + fix bugs found"**: internal structure changes freely; latent bugs and dead code discovered during the refactor MAY be fixed, but any intentional behavior change is documented in the commit message (convention: `INTENTIONAL BEHAVIOR CHANGE: …`) and in MILESTONES.md. Otherwise:

- [ ] **GATE-1.8a**: Wire protocol stays byte-identical (the `_read_and_parse_lines` atomic-read invariant preserved; serial framing/CRC/timeout semantics unchanged).
- [ ] **GATE-1.8b**: End-user CLI surface preserved — command names, flags, defaults, exit codes, and output. Verified by characterization (golden) tests.
- [ ] **GATE-1.8c**: Firmware/app constant contract preserved — `constants.py` values stay equal to `firestarter/include/firestarter.h` (and the v1.7 alias/revision headers); guarded by parity tests.
- [ ] **GATE-1.8d**: The host read path is **ring-fenced** — changes to `read_eprom()` / `read_data_block()` are structural-only, so the v1.9 RCA's 15 N=5 W27C512 baseline binaries remain valid. Any non-structural read-path change is flagged and deferred to v1.9.
- [ ] **GATE-1.8e**: Full test suite (existing + new) green; pip entry point (`firestarter`) still installs and runs.

---

## v1 Requirements

### Test Safety Net (TEST) — pin behavior before restructuring

- [x] **TEST-01**: Characterization (golden) tests pin the current CLI command surface — `list`, `info`, `read`, `write`, `verify`, `blank`, `erase`, `id`, and the `dev` subcommands — capturing output, exit codes, and flag-parsing edge cases via Click's `CliRunner` + snapshot (syrupy), BEFORE the Click migration. *(Phase 36: implemented as a syrupy **subprocess** harness — D-01 — since the CLI is still argparse until Phase 41; CliRunner adopted then.)*
- [x] **TEST-02**: Characterization tests pin the serial frame-parse path (`_read_and_parse_lines` preamble→body→terminator sequence + sliding-window timeout) using the existing `BytesIO` fake-serial fixture, BEFORE the serial split.
- [x] **TEST-03**: The `EpromDatabase` singleton is replaced with injectable construction (DI via Click context), so the database, chip lookup, and EPROM operations are independently testable; unit tests cover `get_eprom`, `convert_to_programmer`, and DIP→RURP pin translation. *(Phase 36: minimal `skip_local_override` constructor seam per D-06; full Click-context DI deferred to Phase 41.)*
- [x] **TEST-04**: The firmware-contract parity test is extended from `REVISION_*` only to also cover `COMMAND_*`, `FLAG_*`, and `CTRL_*`, asserting each value equals the corresponding firmware header literal.
- [x] **TEST-05**: Two known latent bugs are characterized as **bugs, not pinned as correct**: `build_arg_flags` `if "force" in args` attribute-vs-truthiness check, and a possibly-missing `COMMAND_FW_VERSION` in `constants.py`. Tests assert the corrected behavior once fixed. *(Phase 36: `COMMAND_FW_VERSION` confirmed PRESENT at 0x0D → folded into TEST-04 parity; second bug slot substituted with the `EpromOperationError`-conflated-as-comm-error bug per D-08/D-09. Both pinned `xfail(strict=True)`.)*

### Tooling & CI Quality Gate (TOOL)

- [x] **TOOL-01**: `ruff` (lint) + `ruff format` configured in `pyproject.toml`; a baseline pass (`ruff check --add-noqa`) makes the tree green; selected rule categories documented (no `select = ["ALL"]`).
- [x] **TOOL-02**: `mypy` configured with a gradual per-module strategy + `types-pyserial`; the initial error count is recorded as a watermark; the gate is "no new errors," tightened to strict on modules as they are typed.
- [x] **TOOL-03**: A CI workflow runs `ruff check`, `ruff format --check`, and `mypy`, plus the test suite with a coverage gate (start ~60%, ratcheted up per phase), and fails the build on violations.

### Module Decomposition — low-risk extractions (STRUCT)

- [x] **STRUCT-01**: Frame parsing is extracted into a new flat `frame_parser.py` (CRC8, `_decode_param`, `_decode_id_frame`, structured `Response`/`LogMessage` types), testable without serial I/O; `test_decoder.py` passes unchanged. *(Phase 38: `_decode_id_frame` intentionally STAYS in `serial_comm.py` per locked decision D-06 — it is package-coupled to CATALOG + codec; its relocation is deferred to Phase 40. The pure primitives + `test_decoder.py`-unchanged intent are delivered.)*
- [x] **STRUCT-02**: Message decode/format is extracted into a new flat `codec.py` (`format_message`, revision-silkscreen rendering), separated from frame parsing and from logging side effects.
- [x] **STRUCT-03**: Address/size string parsing is extracted into a new flat `address_parser.py` with explicit validation; `_setup_operation` consumes it.
- [x] **STRUCT-04**: Exception classes are consolidated into a single flat `exceptions.py` hierarchy (from `serial_comm`, `eprom_operations`, `hardware`).
- [x] **STRUCT-05**: Confirmed dead code is removed (`read_data_block` and commented-out blocks); `globals()`-introspection patterns are replaced with explicit references.

### Database & Chip Resolution (DATA)

- [x] **DATA-01**: A new flat `chip_resolver.py` provides a single `resolve_chip(name) -> programmer_config` used by every command — eliminating the chip-lookup boilerplate copy-pasted across the 9 handlers.
- [x] **DATA-02**: There is a single source of truth for DIP→RURP pin mapping — the hardcoded `pin_conversions` dict / `pinouts.json` duplication is consolidated to one authoritative source. _(Resolved documentation-only, D-05: pin_conversions and pinouts.json are distinct composing layers, not duplicates — documented in `database.py`, not merged.)_
- [x] **DATA-03**: `from firestarter.constants import *` star-imports are replaced with named imports across all modules (readability + mypy traceability).
- [x] **DATA-04**: Wire-protocol constants (commands, flags, control bits, message IDs) are consolidated into one authoritative module with clear firmware-sync markers; `COMMAND_FW_VERSION` is verified present (added if missing).

### Serial / Transport Restructure (SERIAL)

- [x] **SERIAL-01**: `SerialCommunicator` is reduced to transport + command dispatch; the firmware-handshake concern is lifted out of port discovery (`_probe_port`); type hints added.
- [x] **SERIAL-02**: `_validate_firmware_version` is extracted as a testable static method with unit tests for the version-guard logic.
- [x] **SERIAL-03**: Wire behavior stays byte-identical — the `_read_and_parse_lines` generator body is unchanged (relocated callees only); verified by existing + new tests (satisfies GATE-1.8a).

### CLI Migration to Click (CLI)

- [x] **CLI-01**: The CLI is migrated from argparse to Click; every command, flag, default, and exit code is preserved (verified by TEST-01), with the five documented argparse→Click traps handled explicitly (exit codes / `return 1`, prefix matching, `store_false` polarity for `--no-blank-check`, the `--pre`/`--firmware-version`/`--stable` mutually-exclusive group, the firmware-version type-validator).
- [x] **CLI-02**: One Click command per user command lives in a new flat `cli_handlers.py`; the 418-line `main()` becomes a thin Click group entry point.
- [x] **CLI-03**: The `build_arg_flags` latent bug is fixed (documented intentional behavior change per GATE-1.8).
- [x] **CLI-04**: The pip entry point (`firestarter`) is preserved and a CLI smoke test runs in CI; shell-completion behavior is either preserved or explicitly dropped with operator sign-off (the `argcomplete` question).

### Error Handling & Quality Sweep (ERR)

- [ ] **ERR-01**: A consistent error convention — service/transport layers raise typed exceptions; the Click boundary maps them to stable exit codes/messages; no bare `except:`.
- [ ] **ERR-02**: Type hints on all public functions in touched modules (those modules are mypy-clean under the configured strictness).
- [ ] **ERR-03**: Module and public-function docstrings explaining intent; naming normalized to snake_case (no camelCase legacy); remaining dead code removed.

### Documentation & Milestone Close (DOC)

- [ ] **DOC-01**: `firestarter_app` README / contributor docs updated to reflect the new flat-module structure and the tooling workflow (ruff / mypy / pytest / coverage).
- [ ] **DOC-02**: MILESTONES.md v1.8 entry written; PROJECT.md "Validated" updates; phase directories archived under `.planning/milestones/v1.8-phases/`.
- [ ] **MS-01**: GATE-1.8 verified end-to-end and the `firestarter_app` branch promoted (`v1.8-app-cleanup` → `beta` → `main`) per the established beta→stable pattern.

---

## Future Requirements (deferred)

### v1.9 — Read-Bug RCA + Fix

- **RCA-\***: Root-cause + fix the 64KB streaming-read byte-jitter (Bug A / Bug B). Depends on the read path being ring-fenced (GATE-1.8d) so the baseline binaries stay valid.
- **PROTOSM-01**: Extract the `ProtocolStateMachine` from `serial_comm.py` (HIGH complexity) — explicitly deferred from v1.8.

---

## Out of Scope

Explicitly excluded for v1.8. Documented to prevent scope creep.

| Item | Reason |
|------|--------|
| Firmware (`firestarter/`) changes | Host-only milestone; firmware contract preserved + parity-tested, not modified |
| Subpackage reorganization (cli/, serial/, ops/) | Operator decision: keep flat layout to minimize churn / preserve git blame |
| async/asyncio rewrite | Over-engineering; serial I/O is fine synchronous |
| Dependency-injection framework, plugin system (pluggy/click-plugins) | Over-abstraction for a CLI of this size |
| Pydantic / new validation/serialization layer | Not needed; TypedDict + plain functions suffice |
| `ProtocolStateMachine` extraction | HIGH-risk; deferred to v1.9 alongside the RCA |
| The 64KB read-bug RCA/fix itself | Renumbered to v1.9 (hardware-gated); v1.8 only ring-fences the read path |
| New chip support / new board target / new CLI features | Refactoring milestone — no new features |
| Binary wire format / protocol changes | Wire protocol frozen by GATE-1.8a |

---

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| TEST-01 | Phase 36 | Complete |
| TEST-02 | Phase 36 | Complete |
| TEST-03 | Phase 36 | Complete |
| TEST-04 | Phase 36 | Complete |
| TEST-05 | Phase 36 | Complete |
| TOOL-01 | Phase 37 | Complete |
| TOOL-02 | Phase 37 | Complete |
| TOOL-03 | Phase 37 | Complete |
| STRUCT-01 | Phase 38 | Complete |
| STRUCT-02 | Phase 38 | Complete |
| STRUCT-03 | Phase 38 | Complete |
| STRUCT-04 | Phase 38 | Complete |
| STRUCT-05 | Phase 38 | Complete |
| DATA-01 | Phase 39 | Complete |
| DATA-02 | Phase 39 | Complete |
| DATA-03 | Phase 39 | Complete |
| DATA-04 | Phase 39 | Complete |
| SERIAL-01 | Phase 40 | Complete |
| SERIAL-02 | Phase 40 | Complete |
| SERIAL-03 | Phase 40 | Complete |
| CLI-01 | Phase 41 | Complete |
| CLI-02 | Phase 41 | Complete |
| CLI-03 | Phase 41 | Complete |
| CLI-04 | Phase 41 | Complete |
| ERR-01 | Phase 42 | Pending |
| ERR-02 | Phase 42 | Pending |
| ERR-03 | Phase 42 | Pending |
| DOC-01 | Phase 43 | Pending |
| DOC-02 | Phase 43 | Pending |
| MS-01 | Phase 43 | Pending |
| GATE-1.8 (a–e) | All phases (standing gate) | Pending |

**Coverage:**

- v1 requirements: 30 (5 TEST + 3 TOOL + 5 STRUCT + 4 DATA + 3 SERIAL + 4 CLI + 3 ERR + 3 DOC/MS)
- Mapped to phases: 30/30 ✓ (Phase 36: 5, Phase 37: 3, Phase 38: 5, Phase 39: 4, Phase 40: 3, Phase 41: 4, Phase 42: 3, Phase 43: 3)
- Unmapped: 0
- GATE-1.8 (a–e): standing cross-cutting gate, not a phase

---
*Requirements defined: 2026-05-27*
*Last updated: 2026-05-27 — traceability table filled by roadmapper (Phases 36-43)*

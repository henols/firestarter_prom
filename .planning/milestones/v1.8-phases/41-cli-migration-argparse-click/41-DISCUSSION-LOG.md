# Phase 41: CLI Migration argparse → Click - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-28
**Phase:** 41-CLI Migration argparse → Click
**Areas presented:** argcomplete disposition, Singleton DI mechanism, Error→exit-code scope, Wave decomposition
**Areas selected for discussion:** argcomplete disposition
**Areas delegated to Claude ("you recommend"):** Singleton DI mechanism, Error→exit-code scope, Wave decomposition

---

## Gray Area Selection

| Option | Description | Selected |
|--------|-------------|----------|
| argcomplete disposition | SC#4 demands an explicit decision. argcomplete is wired today via EpromCompleter (db-driven chip-name completion) on 9 subparsers. Options: drop+Click completion / keep+Click-integration / drop entirely. | ✓ |
| Singleton DI mechanism | How do the 14 handlers reach EpromDatabase/ConfigManager/EpromOperator/HardwareManager/FirmwareManager/EpromConsolePresenter? Click `ctx.obj` vs module-level singletons. | |
| Error→exit-code scope | Phase 41's depth on Click-boundary exit-code mapping — minimal preserve-today, narrow ClickException shim now, or full centralized mapping (Phase 42 territory). | |
| Wave decomposition | Atomic Click swap (mega-commit) vs incremental (dead code intermediates) vs hybrid (skeleton-first + grouped command waves + close wave). | |

**User's choice:** Selected only "argcomplete disposition"; delegated the other three to Claude per the standing Phase 37/38/40 "you recommend" pattern (Phase 39 was the active-engagement exception).

---

## argcomplete disposition

| Option | Description | Selected |
|--------|-------------|----------|
| (A) Drop + Click completion (Recommended) | Remove `argcomplete>=3.6.2` from deps; delete `EpromCompleter`/`eprom_validator`/`add_eprom_completer`; wire Click's `shell_complete=` callback for chip-name completion on the `eprom` arg. INTENTIONAL BEHAVIOR CHANGE: users re-activate via `_FIRESTARTER_COMPLETE=bash_source firestarter` written to shell rc. Smaller deps, cleaner cli_handlers.py, idiomatic Click. | ✓ |
| (B) Keep argcomplete, integrate with Click | Retain `argcomplete>=3.6.2`; add `# PYTHON_ARGCOMPLETE_OK` magic + `argcomplete.autocomplete(cli)` before the Click group invocation; declare completers as plain Python callables on Click params. Existing user shell rc lines keep working unchanged. Slightly more complex Click code; carries the dep forward. | |
| (C) Drop argcomplete, no replacement | Remove `argcomplete>=3.6.2`; delete completer code; do NOT wire Click completion. Existing users lose chip-name completion entirely. Sign-off territory per SC#4. | |

**User's choice:** (A) Drop + Click completion.

**Notes:** Operator follow-up — explicit reminder to capture the operator-facing doc update (`firestarter_app/autocomplete.md`, linked from README.md:73-74). Folded into CONTEXT.md D-04b: this phase rewrites `autocomplete.md` in Wave 4 alongside the dep removal + Click `shell_complete=` wiring (rather than deferring to Phase 43 DOC-01), because the file's content is mechanically dependent on the implementation change introduced THIS phase. Per-shell Click activation incantations enumerated in CONTEXT.md D-03 (bash / zsh / fish / PowerShell). README.md:73-74 link target preserved (file path unchanged, only content changes); pipx note preserved (orthogonal to completion library choice).

---

## Claude's Discretion — items the operator delegated to Claude

### Singleton DI mechanism — recommendation locked as `ctx.obj` (D-05/D-06/D-07)

| Option | Description | Selected |
|--------|-------------|----------|
| (A) Click `ctx.obj` | Group instantiates EpromDatabase + ConfigManager + EpromOperator + HardwareManager + FirmwareManager + EpromConsolePresenter once; stashes them on a typed `AppContext` dataclass on `ctx.obj`; handlers pull via `@click.pass_obj`. Consumes Phase 36's de-singleton work, idiomatic Click DI, typed access, test-friendly. | ✓ |
| (B) Module-level singletons (today's pattern) | Keep today's module-level instantiation; access via module imports. Minimum churn, blame-friendly, but handlers stay implicitly coupled to module state and Phase 42 ERR-02 (mypy strict) becomes harder. | |

**Rationale:** Phase 36 explicitly de-singletoned `EpromDatabase` via the `skip_local_override` seam (TEST-03) for testability. The natural follow-through is `ctx.obj` carrying all 6 shared objects — typed access, easy CliRunner test setup (construct a fresh `AppContext` per test), and matches Phase 39 D-06's "explicit over implicit" direction (star-imports → named imports).

### Error→exit-code scope — recommendation locked as minimal preserve-today (D-08/D-09)

| Option | Description | Selected |
|--------|-------------|----------|
| (A) Minimal — preserve per-handler exit codes | Keep `_resolve_or_exit` shim (Phase 39 D-03), `sys.exit(0 if op() else 1)` per handler, Click's automatic `UsageError` for the exit-2 paths. One narrow Click-idiom upgrade allowed: `fw_parser.error()` → `raise click.UsageError(...)` (mechanically required by framework swap). | ✓ |
| (B) Narrow ClickException shim now | Introduce a `ChipNotFoundError → ClickException` shim where it cleanly cuts the 9× `_resolve_or_exit` duplication. Reviewable but overlaps Phase 42 ERR-01. | |
| (C) Full centralized mapping decorator | Full typed-exception → ClickException middleware now. Scope creep into Phase 42. | |

**Rationale:** Phase 42 ERR-01 explicitly owns "consistent error convention: typed exceptions → stable exit codes at the Click boundary". Doing it cleanly in Phase 41 requires deciding the broader typed-exception-→-exit-code policy. Adding a half-decorator now would either under-specify Phase 42's design space or become rework. `_resolve_or_exit` is the deliberate seam between today's logging contract and Phase 42's exception-mapping contract.

### Wave decomposition — recommendation locked as 4-wave incremental-with-dead-code (D-10/D-11/D-12/D-16/D-17)

| Option | Description | Selected |
|--------|-------------|----------|
| (A) Atomic mega-commit | One huge commit (cli_handlers.py + main.py trim + all 14 commands + argcomplete swap). Truthful to the shape of the work (entry point can't host argparse + Click partially), but a massive diff. | |
| (B) Incremental dead code | Each `@cli.command()` lands as dead code; final swap commit flips main.py. Small commits but dead code intermediates feel wasteful. | |
| (C) Hybrid: skeleton + grouped waves + close (Recommended) | Wave 1: `build_arg_flags` fix (isolated). Wave 2: skeleton + 3 read-only commands as dead code + CliRunner tests prove wiring. Wave 3: remaining 11 commands as dead code. Wave 4: entry-point swap + main.py trim + argcomplete drop + Click shell_complete + CI smoke + autocomplete.md rewrite. | ✓ |

**Rationale:** Phase 36 D-01 explicitly designed subprocess goldens to be migration-transparent (target the `firestarter` entry point, not `firestarter.main:main`). This makes the incremental-with-dead-code shape genuinely workable — CliRunner tests in Waves 2-3 prove the new code works before any user-visible swap; subprocess goldens stay green on the argparse path through Waves 1-3 and transition to the Click path in Wave 4 (where any drift caught is a regression to fix in-wave, not a goldenfile update). Matches operator's Phase 38/40 plan-per-wave style.

---

## Deferred Ideas

- Typed-exception → ClickException mapping at the cli_handlers boundary (Phase 42 ERR-01).
- BUG-2 `EpromOperationError`-conflated-as-`SerialError` fix (Phase 42 ERR-01; xfail stays strict-pinned through Phase 41).
- mypy strict overrides on `cli_handlers.py` (Phase 42 ERR-02).
- Per-handler / module-level docstrings on `cli_handlers.py` (Phase 42 ERR-03).
- `Optional[X]` → `X | None` modernization (deferred by Phase 37 D-08 py39 floor).
- Subpackage reorganization `cli/`, `serial/`, `ops/` (explicit Out-of-Scope per REQUIREMENTS).
- `pluggy` / `click-plugins` plugin architecture for `dev` subcommands (explicit Out-of-Scope).
- Click decorator helpers `@eprom_arg` / `@force_option` (Phase 42 quality sweep candidate if planner sees a clean win).
- Broader README rewrite for flat-module map + ruff/mypy/pytest workflow (Phase 43 DOC-01).
- MILESTONES.md v1.8 entry capturing the two INTENTIONAL BEHAVIOR CHANGES (Phase 43 DOC-02).
- CI workflow shell-completion smoke test (overkill; trust Click ships valid output).

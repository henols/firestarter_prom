# Phase 41: CLI Migration argparse → Click - Context

**Gathered:** 2026-05-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace the 418-line argparse `main()` dispatcher in `firestarter_app/firestarter/main.py` with a Click command group; create flat sibling `cli_handlers.py` with one `@cli.command()` per top-level user command (plus a `@cli.group()` for `dev` with 4 sub-commands); trim `main.py` to ≤ 50 lines (Click group + globals + entry-point call); fix the `build_arg_flags` attribute-vs-truthiness latent bug as an INTENTIONAL BEHAVIOR CHANGE commit; drop the `argcomplete` runtime dependency and wire Click's built-in `shell_complete=` for db-driven chip-name completion.

Four deliverables, mapped to CLI-01..04:

- **CLI-01:** argparse → Click migration; every command, flag, default, and exit code preserved (verified by Phase 36's migration-transparent subprocess goldens + new in-process `CliRunner` happy-path tests); the **five argparse→Click traps** each handled explicitly per ROADMAP SC#1:
  1. Exit codes via `raise click.ClickException` / `sys.exit` (Click doesn't return-1 from handlers by default)
  2. **No prefix matching** — Click matches command names exactly (argparse accepts unambiguous prefixes; today's snapshots already assume exact-match, so this is a quiet correctness win, not a behavior change)
  3. `--no-blank-check` polarity — `@click.option("--no-blank-check", "blank_check", flag_value=False, default=True, is_flag=True)` (argparse's `store_false` + `default=True` model)
  4. `--pre` / `--firmware-version` / `--stable` 3-way mutex enforced via a Click callback guard on the `fw` command (argparse `add_mutually_exclusive_group()` becomes a Click validator)
  5. `_validate_firmware_version` (today an argparse `type=` validator at `main.py:194-208`) re-wired as either a Click param type or option callback
- **CLI-02:** New flat `firestarter/cli_handlers.py` exists with one `@cli.command()` per top-level user command (14 commands: `read`/`write`/`verify`/`blank`/`erase`/`id`/`info`/`list`/`search`/`vpp`/`vpe`/`hw`/`fw`/`config` + the `dev` group with `read`/`reg`/`addr`/`consistency-check`); `firestarter/main.py` ≤ 50 lines (Click `@click.group()` definition, global options `-v/--verbose` `-p/--port` `--version`, `ctx.obj` scaffold, entry-point `cli()` invocation, and the Python-version guard); the `if args.command == ...` 14-branch dispatch chain at `main.py:632-918` is deleted.
- **CLI-03:** `build_arg_flags` (`main.py:504-518`) attribute-vs-truthiness latent bug fixed (`"force" in args` → `getattr(args, "force", False)` semantics); fix lands as a separate atomic INTENTIONAL BEHAVIOR CHANGE commit per GATE-1.8's "refactor + fix bugs found" convention; the Phase 36 `xfail(strict=True)` pin in `tests/test_bug_characterization.py::test_build_arg_flags_force_truthiness_not_existence` (BUG-1) flips to passing.
- **CLI-04:** `pip install -e . && firestarter --help` runs cleanly (CI smoke step added); `argcomplete>=3.6.2` removed from `pyproject.toml` runtime deps and replaced with Click's native `shell_complete=` callback for chip-name completion on every `eprom` argument; the swap is documented in the migration commit as INTENTIONAL BEHAVIOR CHANGE (existing users must re-activate via Click's incantation — see D-08).

Requirements: CLI-01, CLI-02, CLI-03, CLI-04 (full text in `.planning/REQUIREMENTS.md` lines 61–64). Standing contract: **GATE-1.8 (a–e)**, esp. **(a)** wire protocol untouched (this phase touches only the CLI surface — `serial_comm.py`/`eprom_operations.py`/`hardware.py`/`firmware.py` bodies are not modified, only their callers from `main.py` move to `cli_handlers.py`), **(b)** end-user CLI surface preserved (the load-bearing acceptance gate — Phase 36's 29 syrupy snapshots + the `bug` xfails flipping to pass are the witness), **(c)** constants untouched, **(d)** read path ring-fenced (no edits to `eprom_operator.read_eprom` / `_read_and_parse_lines`), **(e)** suite green + pip entry point installs and runs (`firestarter --help` smoke test).

**Depends on:**
- Phase 39 (`chip_resolver.py` exists with `resolve_chip()` — D-15 here consumes it via `ctx.obj.db` plumbed through 9 chip-op Click handlers).
- Phase 40 (`exceptions.py` import surface stable; `SerialCommunicator` public API clean with type hints).

**Unblocks:**
- Phase 42 (ERR-01: typed exceptions → stable exit codes at the Click boundary; ERR-02: mypy strict overrides on `cli_handlers.py`).
- Phase 43 (DOC-01 README + contributor docs reflect the Click-based CLI structure).

</domain>

<decisions>
## Implementation Decisions

The operator selected only **argcomplete disposition** to discuss directly (multiSelect; one of four offered); delegated the other three gray areas (DI mechanism, error→exit-code scope, wave decomposition) per the standing Phase 37/38/40 "you recommend" pattern. The recommendations below are **locked**. Each resolves a real choice grounded in scout evidence + prior-phase precedent. Operator's standing style across Phases 37–40: lean, behavior-preserving, minimize churn, preserve git blame, document SC deviations with rationale rather than escalate, fix bugs found along the way as flagged INTENTIONAL BEHAVIOR CHANGE commits.

### CLI-04 — argcomplete disposition (operator chose Option A; 2026-05-28)
- **D-01:** **Drop `argcomplete>=3.6.2` runtime dependency** from `pyproject.toml:50`. Delete `argcomplete` import (`main.py:18-19`), the `EpromCompleter(BaseCompleter)` class (`main.py:39-45`), the `eprom_validator(eprom, prefix)` helper (`main.py:58-59`), the `add_eprom_completer(parser)` factory (`main.py:62-69`), the `argcomplete.autocomplete(parser, validator=eprom_validator)` call (`main.py:578`), and the 10 `add_eprom_completer(...)` invocation sites across the 9 chip-op subparsers + the `dev` subgroup. Rationale: SC#4 forces an explicit decision; ROADMAP wording is "removed (with Click shell completion wired as its replacement) **OR** retained with explicit operator sign-off on the deferral". Operator chose the removal path — keeps the Click migration code minimal, drops one runtime dep, removes one shim layer.
- **D-02:** **Wire Click's native `shell_complete=` callback** for chip-name completion on every Click command that takes an `eprom` argument (9 sites). Implementation pattern:
  ```python
  def _complete_eprom(ctx, param, incomplete):
      """Click shell_complete callback — returns chip names matching `incomplete` (case-insensitive prefix)."""
      db = EpromDatabase()  # singleton; OK to instantiate here — completion runs in a separate process
      return [
          click.shell_completion.CompletionItem(e["name"])
          for e in db.get_eproms(False)
          if e["name"].lower().startswith(incomplete.lower())
      ]
  ```
  Then on each command: `@click.argument("eprom", shell_complete=_complete_eprom)`. The callable matches argcomplete's `EpromCompleter` semantics (case-insensitive prefix via the existing `eprom_validator` logic) so completion behaviour is preserved end-to-end (only the activation incantation changes).
- **D-03:** **INTENTIONAL BEHAVIOR CHANGE: shell-completion activation incantation changes.** Document this in the migration commit message — existing users had `eval "$(register-python-argcomplete firestarter)"` in their shell rc; after this phase ships they need:
  - **bash:** `eval "$(_FIRESTARTER_COMPLETE=bash_source firestarter)"`
  - **zsh:** `eval "$(_FIRESTARTER_COMPLETE=zsh_source firestarter)"`
  - **fish:** `eval (env _FIRESTARTER_COMPLETE=fish_source firestarter)`
  - **PowerShell:** `_FIRESTARTER_COMPLETE=powershell_source firestarter | Out-String | Invoke-Expression`
  Phase 36 subprocess goldens do **not** exercise completion (no behaviour diff in normal CLI invocations), so the snapshot suite stays migration-transparent.
- **D-04:** **Do not retain a back-compat shim.** No `register-python-argcomplete`-emulating wrapper; no dual-completion-library support. The dep is gone, the import is gone, the EpromCompleter class is gone. Operators activate Click completion fresh.
- **D-04b:** **Rewrite `firestarter_app/autocomplete.md` in Wave 4** alongside the dep removal + Click `shell_complete=` wiring (Plan 41-04). The current file (72 lines; documents `activate-global-python-argcomplete` + bash/zsh/PowerShell `register-python-argcomplete firestarter` + pipx) is wrong post-migration. Replace with Click-equivalent activation for bash/zsh/fish/PowerShell (incantations enumerated in D-03 above). README.md:73-74 link reference to `autocomplete.md` is preserved (file path unchanged, only content changes). The "pipx Installations" §65-72 note is orthogonal to the completion library and stays in spirit (verify the command name `firestarter` matches via `pipx list`). The `argcomplete` package mention at §31 disappears (Click is bundled with Click, which is a `firestarter` runtime dep — no separate install needed for completion). **Phase 43 DOC-01 owns the broader README rewrite** (new flat-module map + ruff/mypy/pytest workflow); Phase 41 only updates `autocomplete.md` because the file's content is mechanically dependent on the implementation change THIS phase makes. Leaving it stale through Phase 42 is misleading to anyone reading docs between phases.
- **D-04c:** **Operator action required after this phase ships (documented in MILESTONES.md by Phase 43 / DOC-02; no Phase 41 action needed beyond commit message + autocomplete.md rewrite):** operators with shell completion configured against the old argcomplete activation MUST replace their shell rc line per D-03's per-shell incantations. Operators without completion configured are unaffected. CI / pipx installation flows are unaffected by the dep change (Click is already an implicit transitive dep via the migration; explicitly listing it in `[project] dependencies` is part of Wave 4 / Plan 41-04). Bench-side: the operator's `/dev/ttyACM*` and `/dev/ttyUSB*` workflows do not require completion — the change is convenience-only, not functional.

### CLI-01/02 — Singleton DI mechanism (`ctx.obj`; locked per "you recommend")
- **D-05:** **Use Click `ctx.obj` as the DI vehicle** for the six shared objects: `EpromDatabase` (Phase 36 de-singletoned via `skip_local_override` seam — Phase 41 consumes this work), `ConfigManager`, `EpromOperator`, `HardwareManager`, `FirmwareManager`, `EpromConsolePresenter`. The Click group's `@click.pass_context`-decorated callback (or `result_callback`) instantiates them once at group entry and stashes them on `ctx.obj`:
  ```python
  @dataclass
  class AppContext:
      db: EpromDatabase
      config_manager: ConfigManager
      eprom_operator: EpromOperator
      hardware_manager: HardwareManager
      firmware_manager: FirmwareManager
      eprom_presenter: EpromConsolePresenter

  @click.group()
  @click.option("-v", "--verbose", is_flag=True)
  @click.option("-p", "--port", default=None)
  @click.version_option(version=version, prog_name="Firestarter")
  @click.pass_context
  def cli(ctx, verbose, port):
      _setup_logging(verbose)
      config_manager = ConfigManager()
      if port:
          config_manager.set_value("port", port, persist=False)
      db = EpromDatabase()
      ctx.obj = AppContext(
          db=db,
          config_manager=config_manager,
          eprom_operator=EpromOperator(config_manager),
          hardware_manager=HardwareManager(config_manager),
          firmware_manager=FirmwareManager(config_manager),
          eprom_presenter=EpromConsolePresenter(db),
      )
  ```
  Handlers take `ctx` and pull from `ctx.obj`:
  ```python
  @cli.command()
  @click.argument("eprom", shell_complete=_complete_eprom)
  @click.option("-f", "--force", is_flag=True)
  @click.option("-a", "--address", default=None)
  @click.option("-s", "--size", default=None)
  @click.argument("output_file", required=False)
  @click.pass_obj
  def read(app: AppContext, eprom: str, output_file, force, address, size):
      eprom_data = _resolve_or_exit(eprom, app.db)
      if eprom_data is None:
          sys.exit(1)
      ok = app.eprom_operator.read_eprom(eprom, eprom_data, output_file, ...)
      sys.exit(0 if ok else 1)
  ```
- **D-06:** **Rationale for `ctx.obj` over module-level singletons:**
  1. Consumes Phase 36's `EpromDatabase` de-singleton work cleanly — the `skip_local_override` seam exists for testability; `ctx.obj` is the canonical Click-idiomatic place to thread it through handlers.
  2. CliRunner tests can construct a fresh `ctx.obj` with mock/stub managers per test, instead of monkeypatching module-level globals. This is the test pattern the Phase 36 + Phase 41 happy-path suites will use.
  3. Phase 39 D-06 already moved the codebase away from implicit module state (star-imports → named imports for "readability + mypy traceability"); `ctx.obj` is the analogous move for the manager singletons.
  4. Phase 42 ERR-02 (mypy strict on `cli_handlers.py`) is much easier with typed `AppContext` than with module-level imports of disparate singleton instances.
- **D-07:** **`AppContext` is a frozen `@dataclass`** (or `NamedTuple` if the planner prefers immutability syntax) — explicit fields, type-annotated, py39-compatible legacy `Optional[X]` style where needed. **Not a `dict`** — typed access is the whole point. Lives in `cli_handlers.py` next to the Click group.

### CLI-01 — Error→exit-code mapping scope (minimal preserve-today; locked per "you recommend")
- **D-08:** **Minimal scope this phase — preserve today's exit-code shape per-handler; defer centralized mapping to Phase 42.** Phase 42 ERR-01 explicitly owns "service/transport layers raise typed exceptions; the Click boundary maps them to stable exit codes/messages" — doing it here risks scope creep + a bigger diff. Specifically:
  - **Keep `_resolve_or_exit(name, db) -> dict | None`** (today `main.py:521-533`; Phase 39 D-03 introduced) — moved into `cli_handlers.py`; same contract (catches `ChipNotFoundError`, logs `f"EPROM '{name}' not found in database."`, returns `None`). The 9 chip-op handlers call it identically and `sys.exit(1)` on `None`.
  - **`return 1 if not op() else 0` becomes `sys.exit(0 if op() else 1)`** at each handler (the natural Click idiom). Behaviour identical.
  - **Argparse usage error (exit code 2)** maps to Click's automatic `UsageError` (no special wiring needed — Click does this for unknown options, missing required args, etc.).
  - **One narrow Click-idiom upgrade allowed:** today's `fw_parser.error("--json requires --list")` (`main.py:798`; argparse exit-2) becomes `raise click.UsageError("--json requires --list")` (Click idiom; exit-2 behaviour preserved). This is the natural Click form of the existing post-parse mutex check and is **not** scope creep into Phase 42's broader error convention work — it's mechanically required by the framework swap. Documented as a narrow follow-on.
  - **Argparse's `argparse.ArgumentTypeError` raised inside `_validate_firmware_version`** (`main.py:204-207`) — re-wired as a Click param type/callback; the equivalent Click idiom (`raise click.BadParameter(...)`) exits with code 2, matching argparse's `SystemExit(2)` behaviour. Behaviour preserved.
- **D-09:** **Do NOT introduce a `ChipNotFoundError → ClickException` decorator at the cli_handlers boundary** in Phase 41. Reason: doing it cleanly requires deciding the broader typed-exception-→-exit-code policy (Phase 42 ERR-01). Adding a half-decorator now would either (a) under-specify Phase 42's design space, or (b) become rework. The `_resolve_or_exit` shim is the deliberate seam between today's logging-based contract and Phase 42's exception-mapping contract. Phase 42 will replace `_resolve_or_exit` with `raise ClickException` flowing from `chip_resolver.resolve_chip` directly.

### CLI-01/02 — Wave decomposition (4 waves; locked per "you recommend")
- **D-10:** **Wave 1 — `build_arg_flags` INTENTIONAL BEHAVIOR CHANGE.** Plan 41-01. Standalone, mechanically separate from the Click migration. Fixes the `"force" in args` attribute-vs-truthiness bug in `main.py:504-518` (and the analogous lines 507, 508 for `verbose` and `vpe_as_vpp`; line 513-516 for `input_enable`/`chip_disable` use `getattr` already and are correct). Replace `args.force if "force" in args else False` → `getattr(args, "force", False)`. Commit message: `INTENTIONAL BEHAVIOR CHANGE: build_arg_flags "if force in args" corrected to truthiness check (CLI-03)`. Flip `tests/test_bug_characterization.py::test_build_arg_flags_force_truthiness_not_existence` from `@pytest.mark.xfail(strict=True)` to passing (delete the marker; assertion already encodes corrected behaviour). The full suite (162 passed + 1 remaining xfail for BUG-2 which is Phase 42 territory + 29 snapshots) is green at wave end.
- **D-11:** **Wave 2 — Click skeleton + 3 read-only commands as dead code.** Plan 41-02. Create new `firestarter/cli_handlers.py` with:
  - `AppContext` dataclass (D-07).
  - `cli` `@click.group()` with `-v/--verbose`, `-p/--port`, `--version` options + ctx.obj setup (D-05).
  - `list`, `info`, `search` `@cli.command()`s (these don't need chip resolution — read-only DB queries). Each has `@click.pass_obj` and uses the `AppContext` fields.
  - The `_complete_eprom` shell_complete callback (D-02) — defined but only `info` uses it this wave.
  - New `tests/test_cli_handlers.py` with **`CliRunner`** happy-path tests for `list`, `info`, `search`, `--help`, `--version` (Click in-process tests against `cli_handlers.cli`; complement the existing subprocess goldens which still target `firestarter` entry-point = argparse this wave).
  - **Entry point in `main.py` STAYS argparse this wave.** `cli_handlers.py` is reviewable but dead code from the user's perspective. The CliRunner suite proves the new code works before any user-visible swap. Phase 36 subprocess goldens stay green (argparse path unchanged).
- **D-12:** **Wave 3 — Migrate the remaining 11 commands into cli_handlers.py.** Plan 41-03. Order within the wave (each is a sub-commit, or the wave is a single commit at the planner's discretion):
  1. 6 chip-op commands: `read`, `write`, `verify`, `blank`, `erase`, `id` (each calls `_resolve_or_exit` then `app.eprom_operator.<op>(...)`). `write` exercises the `--no-blank-check` polarity trap (D-13). All take `shell_complete=_complete_eprom` on `eprom`.
  2. 2 voltage commands: `vpp`, `vpe` (each calls `app.hardware_manager.read_v*_voltage(...)`; `--timeout` retains `help=SUPPRESS` semantics via `hidden=True`).
  3. 2 hardware commands: `hw` (no flags), `config` (`--rev`, `-r1/--r16`, `-r2/--r14r15`).
  4. `fw` command with the 3-way mutex callback + version validator type (D-14, D-15).
  5. `dev` as a `@cli.group()` with 4 sub-commands: `read`, `reg`, `addr`, `consistency-check`. The `consistency-check` 3-way verdict (0/1/2; today `main.py:908-917`) uses `sys.exit(verdict_int)` directly — **not** the bool-to-int form — preserving the existing 3-way contract.
  6. Each command adds a CliRunner test in `test_cli_handlers.py` covering its happy path + at least one error path. Phase 36 subprocess goldens are NOT yet exercising the new code — they still hit the argparse entry point. Entry point STAYS argparse this wave.
- **D-13:** **Five argparse→Click traps — handled in Waves 2-3 where the relevant commands land.**
  1. **Exit codes** (D-08; every wave): `sys.exit(0 if op() else 1)` per handler; Click `UsageError`/`BadParameter` for the exit-2 paths.
  2. **No prefix matching** (Wave 2 group setup): Click matches exactly by default. No special wiring needed; today's snapshots assume exact-match (no test invokes `firestarter wri` expecting it to dispatch to `write`).
  3. **`--no-blank-check` polarity** (Wave 3, `write` command):
     ```python
     @click.option("-b", "--no-blank-check", "blank_check", is_flag=True, flag_value=False, default=True, help="Do not perform blank check before write (and skip erase).")
     ```
     Result: presence of `-b` → `blank_check=False`; absence → `blank_check=True`. Matches argparse `store_false` + `default=True` exactly. `erase` keeps the inverse `-b/--blank-check` `store_true default=False` — both polarities live in cli_handlers.py side-by-side.
  4. **3-way mutex `--pre`/`--firmware-version`/`--stable`** (Wave 3, `fw` command): Click has no native `add_mutually_exclusive_group`; implement via a `callback` on each option that checks `ctx.params` for the other two and raises `BadParameter`. Or use a `result_callback` pattern. Planner picks the cleaner of the two; both preserve argparse's exit-2 behaviour on violation. The mutually-exclusive constraint applies in BOTH install and `--list` contexts (argparse's `add_mutually_exclusive_group()` does both — match it).
  5. **`_validate_firmware_version` as Click type/callback** (Wave 3, `fw` command): re-wire as either `type=click.STRING` + `callback=_validate_firmware_version` or as a custom Click `ParamType` subclass. Planner picks; both are idiomatic. The validator's `FIRMWARE_VERSION_RE` import stays put in `firestarter.firmware`. Error path: `raise click.BadParameter(...)` instead of `argparse.ArgumentTypeError`; same exit-2 semantics.
- **D-14:** **`fw` post-parse `--json requires --list` check** (D-08 narrow upgrade): move from `fw_parser.error("--json requires --list")` (`main.py:798`) into the `fw` command body as `raise click.UsageError("--json requires --list")` if `json and not list`. Preserves the exit-2 + "Usage: ..." formatting argparse provides.
- **D-15:** **`fw` magic-default `_maybe_auto_route_to_pre`** (`main.py:211-249`) — preserved verbatim. In the Click handler:
  ```python
  @cli.command()
  @click.pass_obj
  def fw(app, ...):
      _maybe_auto_route_to_pre(ctx.params)  # adapter — pass a SimpleNamespace if helper still reads attrs
      ...
  ```
  Today the helper reads `args.install`, `args.pre`, `args.firmware_version`, `args.stable` via `getattr(args, ...)`. Click delivers these as separate kwargs to the handler; either (a) build a `SimpleNamespace(**locals())` before the call (zero churn to the helper), or (b) refactor the helper to take explicit kwargs (cleaner long-term). Planner picks; both behaviour-equivalent.
- **D-16:** **Wave 4 — entry-point swap + main.py trim + argcomplete removal + Click `shell_complete=` everywhere + CI smoke.** Plan 41-04. Single atomic commit per the locked plan style:
  - `main.py` becomes ≤ 50 lines: imports, the Python-version guard (`if sys.version_info < (3, 9)`), the `exit_gracefully` SIGINT handler, the `__name__ == "__main__"` block invoking `cli()` from `cli_handlers`. All argparse helper functions (`allowed_eproms`, `eprom_validator`, `add_eprom_completer`, `create_*_args` x14, `_validate_firmware_version` argparse adapter, `_maybe_auto_route_to_pre` if relocated, `build_arg_flags`, `_resolve_or_exit`, `EpromCompleter`) DELETED from main.py — the live versions live in `cli_handlers.py`.
  - `from firestarter.main import build_arg_flags` in `tests/test_bug_characterization.py:42` repointed to `from firestarter.cli_handlers import build_arg_flags`.
  - `from firestarter.cli_handlers import cli` becomes the entry point.
  - `pyproject.toml`: remove `argcomplete>=3.6.2` from `dependencies`; the `argcomplete` mypy override (`pyproject.toml:112`) stays harmless or is cleaned up (planner picks; not a behaviour question).
  - All 9 chip-op Click handlers get `shell_complete=_complete_eprom` on their `eprom` arg (per D-02). The `info` command already had it from Wave 2; this wave attaches it to the other 8 (the 6 chip-ops + the 2 dev sub-commands that take `eprom`: `dev read` and `dev addr`).
  - **`firestarter_app/autocomplete.md` rewritten in-wave** (D-04b) — operator-facing activation doc reflects Click's `_FIRESTARTER_COMPLETE=<shell>_source firestarter` incantations for bash/zsh/fish/PowerShell. README.md:73-74 link target is preserved.
  - **`click>=8.1` added to `[project] dependencies`** in `pyproject.toml` (per Files-edited section); `argcomplete>=3.6.2` removed.
  - **Phase 36 subprocess goldens transition** from argparse path → Click path. Per Phase 36 D-01 they are migration-transparent. Any drift caught by `pytest tests/test_characterization.py -v` is a regression to fix in-wave, not a goldenfile update.
  - **CI smoke step added:** the existing `firestarter_app` GitHub Actions workflow grows one step: `pip install -e . && firestarter --help` (CLI-04 SC). Runs alongside `ruff check` / `ruff format --check` / `mypy` / `pytest --cov`.
  - Commit message includes `INTENTIONAL BEHAVIOR CHANGE: argcomplete dropped; shell completion now via Click's _FIRESTARTER_COMPLETE=bash_source firestarter (per CLI-04 / D-01..D-04)`.
- **D-17:** **Wave dependency graph:** W1 (build_arg_flags) is independent of W2-W4 (could land in either order, but landing first means the xfail flips early and the rest of the migration runs against a green suite). W2 → W3 → W4 is a strict sequential chain (cli_handlers.py grows; main.py untouched until W4; entry-point swap happens in W4 atomically). Worktrees off per v1.8 milestone convention; sequential executor per `project_v18_phase_execution_mechanics`.

### Claude's Discretion
- **Plan/wave naming + exact sub-commit count within each wave** — the 4-wave shape is locked (D-10/D-11/D-12/D-16); whether Wave 3 ships as one commit or five (one per command group) is a planner-level call. Phase 40's pattern was one PLAN.md per wave with 1-2 sub-commits inside; recommend matching.
- **`_maybe_auto_route_to_pre` signature adaptation** (D-15) — `SimpleNamespace` adapter vs. explicit-kwarg refactor — both behaviour-equivalent; the latter is one more delta to the helper but cleaner long-term. Planner picks.
- **`fw` 3-way mutex callback shape** (D-13.4) — option-callback per option vs. `result_callback` on the command — both Click-idiomatic; both preserve exit-2 on violation. Planner picks; readability over cleverness.
- **`_validate_firmware_version` re-wiring** (D-13.5) — Click custom `ParamType` subclass vs. plain option callback. Custom ParamType is the more Click-canonical pattern (reusable across `--firmware-version` instances if ever added elsewhere); a callback is simpler. Planner picks.
- **`AppContext` location** — defined inside `cli_handlers.py` (recommended; close to the Click group that constructs it) vs. a separate `firestarter/app_context.py` (overengineering for one dataclass). Stick with cli_handlers.py.
- **Exact CliRunner test count per command** — Wave 2 + Wave 3 add CliRunner happy-path tests; Phase 36 subprocess goldens stay as the GATE-1.8b acceptance gate. Recommend at least one happy-path + one error-path per command; planner sets the floor.
- **Whether `_resolve_or_exit` moves to `cli_handlers.py` or lives in a small `firestarter/cli_errors.py` sibling** — recommend keeping it in `cli_handlers.py` next to its 9 callers in Phase 41; Phase 42 ERR-01 will likely refactor it away into the typed-exception → ClickException mapping layer anyway.

### Reviewed Todos (not folded)
Same three pending todos Phases 37/38/39/40 reviewed; all hardware/protocol/DB-content, out of this host-CLI cleanup's domain (the wire protocol is frozen by GATE-1.8a; the chip DB is frozen by GATE-1.8c):
- `avrdude-mcu-detection-fallback.md` — blank-chip / wrong-firmware recovery (hardware; v1.9-ish).
- `serial-cobs-resync-data-path.md` — COBS framing on the serial data path (protocol; would change wire framing — forbidden by GATE-1.8a).
- `w27c512-eeprom-misclassification.md` — chip-DB content classification fix (DB data, not CLI structure).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & locked milestone decisions
- `.planning/ROADMAP.md` — Phase 41 detail (Goal + SC#1..SC#4, lines 197–209) + the v1.8 section + GATE-1.8 (a–e) standing gate (lines 23–34). **Documented narrow scope upgrade noted in D-08** (`fw_parser.error("--json requires --list")` → `raise click.UsageError(...)`) — mechanically required by the framework swap, NOT a Phase 42 ERR-01 pre-emption.
- `.planning/REQUIREMENTS.md` — CLI-01..CLI-04 (lines 61–64); GATE-1.8 (a–e) (lines 12–20); the Out-of-Scope table (firmware untouched, no protocol change, file layout stays flat, no new validation/serialization layer).
- `.planning/PROJECT.md` — "Current Milestone: v1.8" + "Scope decisions (locked 2026-05-27)" (lines 32–41): **CLI framework = Click** (replaces argparse) at line 35; host-only, flat layout (preserve git blame); refactor-and-fix-bugs gate.

### Prior-phase context this phase builds on
- `.planning/phases/40-serial-transport-restructure/40-CONTEXT.md` — immediate predecessor; D-01..D-05 introduced `_validate_firmware_version` as a `@staticmethod` on `SerialCommunicator` (transport-layer guard, different from `main.py`'s `_validate_firmware_version` argparse type validator); D-06..D-09 stabilized `SerialCommunicator` public API + type hints; D-15/D-16 ring-fenced the read path (GATE-1.8d). Phase 41 consumes the stable public API of `SerialCommunicator` and does NOT touch `serial_comm.py`. Operator's "you recommend" delegation pattern locked here is the standing default; Phase 39's active-engagement-on-all-four was the exception.
- `.planning/phases/39-database-cleanup-chip-resolver/39-CONTEXT.md` — **D-01..D-04** introduced `chip_resolver.resolve_chip(name) -> dict` + the `_resolve_or_exit` shim (`main.py:521-533`); Phase 41 D-05/D-08 inherit this — `_resolve_or_exit` moves to `cli_handlers.py` unchanged, called by the 9 chip-op Click handlers. **D-06** locked named imports across all 6 star-importing modules → no `from constants import *` survives into `cli_handlers.py`; new file uses explicit named imports from `firestarter.constants` (e.g. `FLAG_FORCE`, `FLAG_OUTPUT_ENABLE`, `FLAG_CHIP_ENABLE` as needed by `build_arg_flags`).
- `.planning/phases/38-low-risk-extractions/38-CONTEXT.md` — **D-01** locked `firestarter/exceptions.py` containing `ChipNotFoundError` (caught by `_resolve_or_exit`), `FirmwareOutdatedError`, `EpromOperationError`, `SerialError`, `SerialTimeoutError`, etc. All needed by Phase 41 handlers. **D-04** locked `address_parser.parse_address` / `parse_size` raising `ValueError`; today's argparse `type=` validators delegate to these — Phase 41 Click handlers continue to delegate (no re-implementation).
- `.planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md` — **D-08** locked `target-version = "py39"` / `python_version = "3.9"`; `Optional[X]` / `List[X]` / `Tuple[X,Y]` legacy style mandatory; `# noqa: UP006`/`UP035` markers preserved on legacy-style imports. The new `AppContext` dataclass and all type hints in `cli_handlers.py` follow this convention. **D-09** locked ruff rule set (E/F/I + UP). The CI gate is live on `v1.8-app-cleanup` — Phase 41 commits must stay clean.
- `.planning/phases/36-characterization-test-baseline/36-CONTEXT.md` + `36-01-PLAN.md` through `36-04-PLAN.md` — the load-bearing Phase 36 safety net: **162 passed + 2 xfail + 29 syrupy snapshots**. **D-01** locked **subprocess goldens** as migration-transparent (works identically pre- and post-Click); **D-02** locked in-process happy-paths via `make_comm`/`fake_serial` fixtures (these stay green through the migration because they target `eprom_operator` methods, not the CLI dispatcher); **D-06** locked the `skip_local_override` constructor seam on `EpromDatabase` (consumed by Phase 41 D-05/D-06 via `ctx.obj`); **TEST-05 xfails** in `tests/test_bug_characterization.py` — BUG-1 (`build_arg_flags` `"force" in args`, fix lands Phase 41 CLI-03) flips to passing in Wave 1 / Plan 41-01; BUG-2 (`EpromOperationError` lumped with `SerialError`, fix lands Phase 42 ERR-01) stays xfail through this phase.

### Files this phase edits / creates (firestarter_app sub-repo, branch v1.8-app-cleanup)
- **NEW:** `firestarter_app/firestarter/cli_handlers.py` — the home for `@click.group() cli`, the `AppContext` dataclass, the 14 `@cli.command()`s, the `dev` `@cli.group()` with 4 sub-commands, the `_complete_eprom` shell_complete callback, the `_resolve_or_exit` helper (moved from main.py per D-08), the `build_arg_flags` helper (moved from main.py — fixed per D-10), and the `_maybe_auto_route_to_pre`/Click `BadParameter`-style version-validator wiring. Imports: stdlib + `click` + `firestarter.exceptions`, `firestarter.chip_resolver`, `firestarter.constants` (named, no `*`), `firestarter.database`, `firestarter.config`, `firestarter.eprom_operations`, `firestarter.hardware`, `firestarter.firmware`, `firestarter.eprom_info`, `firestarter.address_parser`, `firestarter.logging_utils`. Target line count: ~600-700 lines (down from main.py's ~930, but on a single concern — CLI surface).
- **PRIMARY EDIT:** `firestarter_app/firestarter/main.py` — trimmed in Wave 4 (Plan 41-04) from 932 → ≤ 50 lines. Survives: module docstring, `from firestarter.cli_handlers import cli`, the `exit_gracefully` SIGINT handler, the Python-version guard, the `__name__ == "__main__"` block. Deletes: `import argparse`, `import argcomplete`, `from argcomplete.completers import BaseCompleter`, `EpromCompleter`, `allowed_eproms`, `eprom_validator`, `add_eprom_completer`, all 14 `create_*_args` factory functions (and the dev_epilog string), `_validate_firmware_version` argparse adapter, `_maybe_auto_route_to_pre` (relocated to cli_handlers.py), `build_arg_flags` (relocated + fixed), `_resolve_or_exit` (relocated), the entire `main()` function. The `firestarter = "firestarter.main:main"` entry point in `pyproject.toml:72` STAYS — `main.py` re-exports `main = cli` (or the entry point flips to `firestarter.cli_handlers:cli` directly; planner picks the cleaner of the two).
- **NEW:** `firestarter_app/tests/test_cli_handlers.py` — CliRunner in-process happy-path + error-path tests per command. Built incrementally across Waves 2-3 (one block per command landing in the same wave). Uses the `cli_handlers.cli` group directly + a constructed `AppContext` (mock managers OK).
- **EDIT:** `firestarter_app/pyproject.toml` — remove `"argcomplete>=3.6.2"` from `[project] dependencies` (`:50`); **add `"click>=8.1"`** to `[project] dependencies` (Click is the new framework — must be a declared runtime dep, not a transitive); the existing `argcomplete` mypy override at `:112` (`ignore_missing_imports = true   # needed for tqdm, rich, argcomplete (no stubs)`) is cleaned up to drop `argcomplete` from the comment (and any rule entry it pinned). Entry point at `:72` either stays `firestarter = "firestarter.main:main"` (preferred — backward compat with any external scripts referencing `firestarter.main:main`) or flips to `firestarter.cli_handlers:cli`.
- **EDIT:** `firestarter_app/autocomplete.md` — Wave 4 / Plan 41-04 rewrites this operator-facing doc (D-04b). Drop the `activate-global-python-argcomplete` §1, the `register-python-argcomplete firestarter` bash/zsh §2 incantations, the matching PowerShell line, and the "argcomplete package comes with Firestarter" note (§31). Replace with Click's `_FIRESTARTER_COMPLETE=<shell>_source firestarter` activation lines for bash/zsh/fish/PowerShell (full incantations in D-03). Preserve the file's structure, the firestarter_logo banner, the README link target, and the pipx §3 note (orthogonal to completion library). Commit message for this edit is bundled into the Wave 4 INTENTIONAL BEHAVIOR CHANGE commit (D-16).
- **EDIT:** `firestarter_app/tests/test_bug_characterization.py` — Wave 1 / Plan 41-01: flip `@pytest.mark.xfail(strict=True, reason="BUG: build_arg_flags...")` decorator (`:48-51`) into a plain passing test (delete the marker); the assertion already encodes corrected behaviour. The import `from firestarter.main import build_arg_flags` (`:42`) repoints to `from firestarter.cli_handlers import build_arg_flags` in Wave 4 / Plan 41-04 (after the relocation).
- **NO-TOUCH (verify byte-identical via Phase 36 snapshots + suite):**
  - `firestarter_app/firestarter/serial_comm.py` — Phase 40's stable public API; do not edit.
  - `firestarter_app/firestarter/eprom_operations.py` — public method signatures used by all 6 chip-op Click handlers; do not edit.
  - `firestarter_app/firestarter/hardware.py`, `firestarter_app/firestarter/firmware.py`, `firestarter_app/firestarter/database.py`, `firestarter_app/firestarter/chip_resolver.py`, `firestarter_app/firestarter/eprom_info.py`, `firestarter_app/firestarter/config.py`, `firestarter_app/firestarter/exceptions.py`, `firestarter_app/firestarter/address_parser.py`, `firestarter_app/firestarter/constants.py`, `firestarter_app/firestarter/codec.py`, `firestarter_app/firestarter/frame_parser.py`, `firestarter_app/firestarter/logging_utils.py`.
  - `firestarter_app/firestarter/data/chip_database.json` + `pinouts.json` (GATE-1.8c).
  - `firestarter_app/tests/__snapshots__/` — Phase 36 syrupy snapshots are the **GATE-1.8b** witness; any drift caught is a regression to fix in-wave, not a snapshot update.
  - The firmware sub-repo (`firestarter/`) — host-only milestone (GATE-1.8c parity test guards constants).

### CI surface (CLI-04 SC)
- `firestarter_app/.github/workflows/ci.yml` — Wave 4 / Plan 41-04 adds one step: `pip install -e . && firestarter --help` after the existing lint/format/type/test steps. Smoke-tests the pip entry point + verifies Click `--help` output renders (non-zero exit fails the build).

### App architecture (context)
- `firestarter_app/CLAUDE.md` — data flow + `main.py` described as "Click CLI entry point" (already updated in anticipation of Phase 41; this phase fulfils the docstring). The `serial_comm.py` "serial protocol implementation" stays unchanged.
- `firestarter_app/README.md` — Phase 43 DOC-01 owns updating the README for the new Click-based CLI structure + the new shell-completion activation incantation; Phase 41 does NOT update the README (defer to DOC-01).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`chip_resolver.resolve_chip(name) -> dict`** (Phase 39 D-01; `firestarter/chip_resolver.py:36`) — single chokepoint for chip name → programmer config; raises `ChipNotFoundError` on miss. 9 chip-op Click handlers call it via `_resolve_or_exit` (which catches the exception + logs + returns None).
- **`_resolve_or_exit(name, db) -> dict | None`** (`main.py:521-533`; introduced Phase 39 D-03) — the shim that maps `ChipNotFoundError → log + return None → caller does sys.exit(1)`. Phase 41 D-08: relocate verbatim to `cli_handlers.py`. Phase 42 ERR-01 will replace this with a typed-exception → ClickException mapping; for now it's the stable seam.
- **`address_parser.parse_address(s)` / `parse_size(s)`** (Phase 38 D-04; `firestarter/address_parser.py`) — raise `ValueError` on bad input. The Click handlers for `read`, `write`, `verify`, `dev read`, `dev addr` continue to delegate (no re-implementation needed); argparse's `type=str` becomes Click `type=click.STRING` with the operator-method itself doing the parse.
- **`build_arg_flags(args)`** (`main.py:504-518`) — fixed in Wave 1 / Plan 41-01 (`"force" in args` → `getattr(args, "force", False)` semantics); relocated to `cli_handlers.py` in Wave 4 / Plan 41-04. Each Click handler passes its own kwargs (Click delivers them by name, no `argparse.Namespace` introspection needed); the helper's loose-args-bag signature can either stay as `(args)` with a `SimpleNamespace` adapter or refactor to explicit kwargs (planner picks per D-15).
- **`_maybe_auto_route_to_pre(args)`** (`main.py:211-249`) — fw-magic-default helper; preserved verbatim per D-15. Adapter pattern picks: `SimpleNamespace(**locals())` zero-churn vs. explicit-kwargs refactor.
- **`_validate_firmware_version(value)`** argparse type adapter (`main.py:194-208`) — re-wired as Click `ParamType` subclass or option callback per D-13.5; same `FIRMWARE_VERSION_RE` import + same `ValueError`-equivalent error path.
- **`EpromDatabase` `skip_local_override` constructor seam** (Phase 36 D-06; `database.py`) — Phase 41 D-05/D-06 consume this via `ctx.obj`. CliRunner tests can construct a fresh `EpromDatabase(skip_local_override=True)` per test, stash it on a constructed `AppContext`, and exercise handlers in isolation.
- **Phase 36 safety net** — 162 passed + 2 xfail + 29 snapshots. Subprocess goldens are migration-transparent per D-01 (they invoke the `firestarter` entry point, not `firestarter.main:main` directly — the swap is invisible to them). CliRunner is the in-process complement added by `test_cli_handlers.py`.
- **Phase 40 stable `SerialCommunicator` public API** — `find_and_connect` / `send_*` / `get_response` / `expect_ack` / `consume_remaining_input` / `disconnect` — none touched here; consumed via `eprom_operator` / `hardware_manager` / `firmware_manager` which already wrap them.

### Established Patterns
- **Flat layout** — every new module is a flat sibling of `firestarter/main.py` (Phase 38's `frame_parser.py` / `codec.py` / `address_parser.py` / `exceptions.py`, Phase 39's `chip_resolver.py`). `cli_handlers.py` continues the pattern. PROJECT.md "File layout stays flat (no subpackage reorg)".
- **Named imports only** — Phase 39 D-06 stripped `from firestarter.constants import *` across 6 modules. `cli_handlers.py` follows: `from firestarter.constants import FLAG_FORCE, FLAG_OUTPUT_ENABLE, FLAG_CHIP_ENABLE` (etc., as needed by `build_arg_flags`).
- **Legacy `Optional[X]` / `List[X]` / `Tuple[X,Y]` style** — Phase 37 D-08 (py39 floor; no `from __future__ import annotations`; modernization deferred). `AppContext` fields, `_resolve_or_exit`'s `-> Optional[dict]`, `_complete_eprom`'s `-> List[CompletionItem]` (or similar) all use legacy syntax. `# noqa: UP006/UP035` on `from typing import Optional, List, Tuple` import.
- **INTENTIONAL BEHAVIOR CHANGE commit convention** — GATE-1.8 "refactor + fix bugs" gate: commit message prefix `INTENTIONAL BEHAVIOR CHANGE: …` + one-line rationale. Phase 41 has two: (1) `build_arg_flags` truthiness fix (CLI-03) — Wave 1; (2) argcomplete → Click shell_complete (CLI-04) — Wave 4. Both commit messages flag the change explicitly.
- **Documented SC deviation pattern** — Phases 38 D-14/D-16, 39 D-06, 40 D-11/D-12: when the dead-code sweep or scope extends beyond SC literal text, document the rationale inline + flag for plan-checker. Phase 41 has D-08 (narrow `UsageError` upgrade in the `fw --json/--list` path — mechanically required by Click, NOT Phase 42 pre-emption).

### Integration Points
- **`cli_handlers.cli` is the new entry point.** Wave 4 swaps `firestarter.main:main` to either (a) re-export `cli` as `main` (`def main(): cli()` in main.py — preserves the dotted-path entry point in pyproject.toml verbatim) or (b) flip `[project.scripts] firestarter = "firestarter.cli_handlers:cli"`. Planner picks; both work; (a) keeps any external references to `firestarter.main:main` working.
- **`AppContext` carries the shared state** across all 14 handlers + 4 dev sub-commands. The Click group instantiates it once per CLI invocation, stashes it on `ctx.obj`, and handlers pull via `@click.pass_obj`. Phase 42 ERR-02 (mypy strict on `cli_handlers.py`) gets typed access through `AppContext`'s dataclass fields.
- **`_complete_eprom` callback** uses `EpromDatabase()` directly (singleton; OK to instantiate in the completion subprocess) — does NOT go through `ctx.obj` because completion runs out-of-process and ctx isn't constructed. This matches argcomplete's `EpromCompleter.__init__` pattern (also instantiates `EpromDatabase()` directly).
- **CI gate at v1.8-app-cleanup** — every commit must keep `ruff check` / `ruff format --check` / `mypy` clean; no new mypy violations vs. the Phase 37 watermark. `cli_handlers.py` is added to the mypy strict overrides in Phase 42 ERR-02 (not Phase 41 — Phase 41 only adds the file, Phase 42 raises the bar).

</code_context>

<specifics>
## Specific Ideas

- The operator continues the standing Phase 37/38/40 "you recommend" delegation pattern — explicitly picking exactly one gray area (argcomplete) to weigh in on directly, leaving DI / error-mapping scope / wave decomposition to Claude. The three deviations / recommendations documented here (D-05/D-06 ctx.obj over module-level singletons; D-08/D-09 minimal error-mapping scope deferring to Phase 42; D-10..D-17 four-wave incremental-with-dead-code shape) are exactly the kind of calls the operator wants made with a recorded rationale rather than escalated.
- The argcomplete dropdown is documented in the migration commit as **INTENTIONAL BEHAVIOR CHANGE** — existing users who had `eval "$(register-python-argcomplete firestarter)"` in their shell rc must re-activate via `eval "$(_FIRESTARTER_COMPLETE=bash_source firestarter)"` (or `zsh_source` / `fish_source`). The chip-name completion experience is otherwise preserved end-to-end (case-insensitive prefix match against `db.get_eproms(False)` names).
- The `dev consistency-check` 3-way verdict (0=PASS / 1=FAIL / 2=hardware-error) is preserved verbatim per D-12 step 5 — `sys.exit(verdict_int)` in the Click handler, NOT a bool-to-int wrap. This is the v1.6 RCA diagnostic and is read-path-adjacent; Phase 36's characterization snapshot for this command pins the 3-way exit code.
- The `_validate_firmware_version` re-wire (D-13.5) is the closest the operator gets to a custom Click `ParamType` decision — defer to planner; both option-callback and ParamType-subclass forms are idiomatic.

</specifics>

<deferred>
## Deferred Ideas

- **Typed-exception → ClickException mapping at the cli_handlers boundary** — D-09 explicitly defers to Phase 42 ERR-01. Doing it cleanly requires the broader typed-exception-→-exit-code policy. Phase 42 replaces `_resolve_or_exit` with a `ChipNotFoundError → ClickException` decorator and propagates the pattern to `SerialError`, `SerialTimeoutError`, `FirmwareOutdatedError`, `EpromOperationError`, `HardwareOperationError`.
- **`EpromOperationError`-conflated-as-`SerialError` bug fix (BUG-2)** — Phase 36 xfail-strict pinning in `tests/test_bug_characterization.py::test_eprom_operation_error_not_labeled_as_communication_error`; fix lands Phase 42 ERR-01 (the `except (SerialError, SerialTimeoutError, EpromOperationError)` clause in `eprom_operations.py:265` gets split). Phase 41 leaves this xfail strict-pinned.
- **mypy strict overrides on `cli_handlers.py`** — Phase 42 ERR-02 territory; "those modules are mypy-clean under the configured strictness". Phase 41 keeps `cli_handlers.py` under the gradual-typing rules (no new errors vs. the Phase 37 watermark); Phase 42 raises the bar.
- **Public-function docstrings on every `@cli.command()` handler** — Phase 42 ERR-03 ("all public classes and methods in touched modules have docstrings"). Phase 41 adds the bare-minimum `help=` text on options/arguments (preserved verbatim from argparse `help=` strings to keep `--help` output snapshot-identical); full module-level docstrings + per-handler docstrings are Phase 42's quality sweep.
- **`Optional[X]` → `X | None` modernization** — locked deferred by Phase 37 D-08 (py39 floor); revisit only if the project's Python floor moves to 3.10+.
- **Subpackage reorganization** (`cli/`, `serial/`, `ops/`) — explicitly Out-of-Scope per PROJECT.md and the v1.8 REQUIREMENTS Out-of-Scope table. `cli_handlers.py` is a flat sibling, period.
- **`pluggy` / `click-plugins` plugin architecture for `dev` subcommands** — explicitly Out-of-Scope per REQUIREMENTS Out-of-Scope table ("Over-abstraction for a CLI of this size"). The 4 dev sub-commands live in the same file as the rest.
- **Click decorator helpers** (`@eprom_arg`, `@force_option`) — could DRY up the 9 chip-op handlers' repeated `@click.argument("eprom", shell_complete=_complete_eprom)` + `@click.option("-f", "--force", is_flag=True)` decoration. Defer: explicit inline decoration on each command is more grep-friendly + matches the operator's "minimize churn / preserve git blame" pattern; reusable decorators are a Phase 42 quality-sweep candidate if the planner sees a clean win.
- **README documentation** — DOC-01 / Phase 43 owns updating `firestarter_app/README.md` for the new Click-based CLI structure + new shell-completion activation. Phase 41 does NOT update the README.
- **CI workflow shell-completion smoke test** — testing that `_FIRESTARTER_COMPLETE=bash_source firestarter` emits a valid bash function is overkill for v1.8; Click ships this and we trust it. Phase 41 CI smoke is limited to `pip install -e . && firestarter --help` per SC#4.

### Reviewed Todos (not folded)
Same three pending todos Phases 37/38/39/40 reviewed; all hardware/protocol/DB-content, out of this host-CLI cleanup's domain (the wire protocol is frozen by GATE-1.8a; the chip DB is frozen by GATE-1.8c):
- `avrdude-mcu-detection-fallback.md` — blank-chip / wrong-firmware recovery (hardware; v1.9-ish).
- `serial-cobs-resync-data-path.md` — COBS framing on the serial data path (protocol; would change wire framing — forbidden by GATE-1.8a; v1.9-or-later if revisited).
- `w27c512-eeprom-misclassification.md` — chip-DB content classification fix (DB data, not CLI structure this phase touches).

</deferred>

---

*Phase: 41-CLI Migration argparse → Click*
*Context gathered: 2026-05-28*

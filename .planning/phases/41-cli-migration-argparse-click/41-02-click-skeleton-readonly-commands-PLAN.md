---
phase: 41-cli-migration-argparse-click
plan: 02
type: execute
wave: 2
depends_on: []
files_modified:
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/tests/test_cli_handlers.py
autonomous: true
requirements:
  - CLI-01
  - CLI-02
must_haves:
  truths:
    - "GATE-1.8a: wire protocol byte-identical — this plan adds new file only; serial/wire code untouched"
    - "GATE-1.8b: end-user CLI surface preserved — entry point STAYS argparse this wave (per D-11); Phase 36 subprocess goldens stay green; cli_handlers.py is dead code from the user's perspective"
    - "GATE-1.8c: constants.py + firmware header parity untouched (named imports only per Phase 39 D-06)"
    - "GATE-1.8d: read path ring-fence — no edits to eprom_operator.read_eprom or _read_and_parse_lines"
    - "GATE-1.8e: full suite green; pip entry point installs and runs (argparse path)"
    - "cli_handlers.py exists with AppContext dataclass, `cli` @click.group(), `_complete_eprom` shell_complete callback, and 3 read-only @cli.command()s: `list`, `info`, `search` (D-11)"
    - "test_cli_handlers.py exists with CliRunner happy-path tests for `list` / `info` / `search` / `--help` / `--version` (D-11)"
    - "Click's exact-match behaviour verified in test (TRAP #2 from D-13.2): `firestarter wri` does NOT dispatch to `write` — the test asserts a non-zero exit + 'No such command' error"
    - "Click `--help` and `--version` work end-to-end via CliRunner against `cli_handlers.cli`"
    - "py39 legacy `Optional[X]` / `List[X]` / `Tuple[X,Y]` style throughout; no `from __future__ import annotations`; `# noqa: UP006/UP035` on legacy imports per Phase 37 D-08"
    - "Named imports only — no `from firestarter.constants import *` in cli_handlers.py per Phase 39 D-06"
    - "no-touch invariant: serial_comm.py, eprom_operations.py, hardware.py, firmware.py, database.py, chip_resolver.py, eprom_info.py, config.py, exceptions.py, address_parser.py, constants.py, codec.py, frame_parser.py, logging_utils.py, data/chip_database.json, data/pinouts.json, tests/__snapshots__/, main.py (entry point stays argparse), pyproject.toml, the firmware sub-repo — none touched in this plan"
  artifacts:
    - path: "firestarter_app/firestarter/cli_handlers.py"
      provides: "Click group + AppContext + 3 read-only commands + shell_complete callback"
      exports: ["cli", "AppContext", "_complete_eprom"]
      contains: "@click.group()"
      min_lines: 100
    - path: "firestarter_app/tests/test_cli_handlers.py"
      provides: "CliRunner in-process tests for the read-only command surface + group-level options"
      contains: "from click.testing import CliRunner"
      min_lines: 40
  key_links:
    - from: "firestarter_app/firestarter/cli_handlers.py"
      to: "firestarter_app/firestarter/database.py::EpromDatabase"
      via: "AppContext.db field + ctx.obj wiring + _complete_eprom callback"
      pattern: "EpromDatabase\\("
    - from: "firestarter_app/firestarter/cli_handlers.py"
      to: "firestarter_app/firestarter/eprom_info.py::EpromConsolePresenter"
      via: "AppContext.eprom_presenter field"
      pattern: "EpromConsolePresenter"
    - from: "firestarter_app/tests/test_cli_handlers.py"
      to: "firestarter_app/firestarter/cli_handlers.py::cli"
      via: "CliRunner.invoke(cli, ...)"
      pattern: "from firestarter.cli_handlers import cli"
---

<objective>
Wave 2 / Plan 41-02 — Create `firestarter_app/firestarter/cli_handlers.py` as the new home for the Click migration: `AppContext` dataclass (D-07), `cli` `@click.group()` with global options + `ctx.obj` setup (D-05), the `_complete_eprom` shell_complete callback (D-02), and the 3 read-only DB-query commands `list` / `info` / `search` (D-11). Wire a CliRunner test suite at `tests/test_cli_handlers.py` exercising the 3 commands + `--help` + `--version` + Click's exact-match behaviour (TRAP #2 from D-13.2).

Entry point in `main.py` STAYS argparse this wave (per D-11). `cli_handlers.py` is reviewable but dead code from the user's perspective. The CliRunner suite proves the new code works before any user-visible swap in Wave 4. Phase 36 subprocess goldens stay green (argparse path unchanged).

Purpose: Land the Click foundation + dataclass + shell-completion callback + 3 commands in isolation, with in-process tests, before any user-visible behaviour swaps. Closes 3/14 commands toward CLI-02 + the skeleton scaffolding for CLI-01.
Output: Two new files on the `firestarter_app/` submodule's `v1.8-app-cleanup` branch; one atomic commit.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
@.planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md
@.planning/phases/39-database-cleanup-chip-resolver/39-CONTEXT.md
@.planning/phases/36-characterization-test-baseline/36-CONTEXT.md
@firestarter_app/CLAUDE.md
@firestarter_app/firestarter/main.py
@firestarter_app/firestarter/database.py
@firestarter_app/firestarter/eprom_info.py
@firestarter_app/firestarter/config.py
@firestarter_app/firestarter/hardware.py
@firestarter_app/firestarter/firmware.py
@firestarter_app/firestarter/eprom_operations.py
@firestarter_app/firestarter/logging_utils.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create cli_handlers.py with AppContext + cli group + _complete_eprom callback</name>
  <files>firestarter_app/firestarter/cli_handlers.py</files>
  <read_first>
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-05 supplies the verbatim code-block target for the cli group + AppContext + the chip-op handler shape; D-06 the rationale for ctx.obj; D-07 the dataclass-vs-NamedTuple lock; D-02 the _complete_eprom callback shape)
    - firestarter_app/firestarter/main.py (current argparse implementation — for the global -v/--verbose / -p/--port / --version option semantics at lines 542-577; the `_setup_logging` call sequence near top of main(); the EpromCompleter at lines 39-45 + add_eprom_completer at 62-69 — these are the argparse equivalents the new _complete_eprom callback replaces)
    - firestarter_app/firestarter/database.py (EpromDatabase constructor signature + get_eproms(include_internal: bool) method shape; Phase 36 skip_local_override seam)
    - firestarter_app/firestarter/eprom_info.py (EpromConsolePresenter constructor signature)
    - firestarter_app/firestarter/config.py (ConfigManager constructor + set_value(key, value, persist) signature)
    - firestarter_app/firestarter/eprom_operations.py (EpromOperator constructor signature — takes config_manager)
    - firestarter_app/firestarter/hardware.py (HardwareManager constructor signature — takes config_manager)
    - firestarter_app/firestarter/firmware.py (FirmwareManager constructor signature — takes config_manager)
    - firestarter_app/firestarter/logging_utils.py (the existing _setup_logging or equivalent helper)
    - .planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md (D-08 py39 legacy Optional[X] / List[X] / Tuple[X,Y] style mandatory; no `from __future__ import annotations`; `# noqa: UP006/UP035` markers preserved on legacy-style typing imports)
    - .planning/phases/39-database-cleanup-chip-resolver/39-CONTEXT.md (D-06 named imports only — no `from firestarter.constants import *`)
  </read_first>
  <action>
    Create the new file `firestarter_app/firestarter/cli_handlers.py`. The file must contain, in this order:

    1. Module docstring (≤2 lines) — names the file as the Click migration target for v1.8 / Phase 41 (CLI-01, CLI-02); Wave 2 lands the skeleton + 3 read-only commands.
    2. Imports — stdlib (`sys`, `logging`, `dataclasses.dataclass`, `typing.Optional` / `List` / `Tuple` with `# noqa: UP006,UP035` per Phase 37 D-08), `click`, and named imports from `firestarter.config`, `firestarter.database`, `firestarter.eprom_info`, `firestarter.eprom_operations`, `firestarter.firmware`, `firestarter.hardware`, `firestarter.logging_utils` (or wherever `_setup_logging` lives in main.py today — preserve the same call shape). Named imports ONLY — no star-import (Phase 39 D-06).
    3. `version` module-level constant — pull from the same place main.py pulls it (typically `firestarter` package `__version__` or `pkg_resources` / `importlib.metadata.version("firestarter")`; preserve main.py's current pattern verbatim).
    4. `@dataclass` `AppContext` — six fields with py39-legacy type annotations: `db: EpromDatabase`, `config_manager: ConfigManager`, `eprom_operator: EpromOperator`, `hardware_manager: HardwareManager`, `firmware_manager: FirmwareManager`, `eprom_presenter: EpromConsolePresenter`. NOT a `dict`. NOT a `NamedTuple` — operator's lock per D-07 is the `@dataclass` form (writable for testability; CliRunner constructs a fresh one per test with mock managers).
    5. `_complete_eprom(ctx, param, incomplete)` function — verbatim shape from D-02: instantiates `EpromDatabase()` (out-of-process, separate process from the actual CLI invocation per Integration Points note in 41-CONTEXT.md), iterates `db.get_eproms(False)`, returns a list of `click.shell_completion.CompletionItem(e["name"])` for case-insensitive prefix matches against `incomplete`. Type signature uses py39 `List[click.shell_completion.CompletionItem]` (with `# noqa: UP006` on the `List` import). Mirror the existing `EpromCompleter` semantics from main.py:39-45 exactly.
    6. `@click.group()` `cli(ctx, verbose, port)` — verbatim shape from D-05 code block: `-v/--verbose` `is_flag=True`; `-p/--port` `default=None`; `@click.version_option(version=version, prog_name="Firestarter")`; `@click.pass_context`; body calls `_setup_logging(verbose)`, instantiates `ConfigManager()`, sets `port` via `config_manager.set_value("port", port, persist=False)` if provided, instantiates `EpromDatabase()` (default — NOT `skip_local_override=True`; that's a test-only seam), and stashes the six-field `AppContext` on `ctx.obj`. Use `EpromConsolePresenter(db)` for the presenter field. Use `@click.pass_context` (not `@click.pass_obj`) since the group body sets `ctx.obj`.
    7. `@cli.command(name="list")` `_list_cmd(app)` — `@click.option("--full", "-f", is_flag=True, help=...)` (mirror argparse `list` help string verbatim from main.py); `@click.pass_obj`; body calls `app.eprom_presenter.list_eproms(full=full)` (preserve the exact call shape from the current argparse handler). Exit-code: `sys.exit(0)` on success. Function-level name `_list_cmd` (not `list` — shadows builtin); Click sees the command name `list` via the `name="list"` kwarg on `@cli.command()`.
    8. `@cli.command(name="info")` `info(app, eprom)` — `@click.argument("eprom", shell_complete=_complete_eprom)`; `@click.pass_obj`; body resolves the chip name (defer chip-resolution refactor to Wave 3 — for now call `app.eprom_presenter.print_eprom_info(eprom)` or whatever the argparse `info` command does today; preserve the exact behaviour verbatim — read main.py's current `info` handler and mirror it). Exit-code preserved per D-08 (`sys.exit(0 if op() else 1)` style).
    9. `@cli.command(name="search")` `search(app, text)` — `@click.argument("text")`; `@click.pass_obj`; body calls `app.eprom_presenter.search_eproms(text)` or the equivalent operator from the argparse search handler. Preserve help string + exit-code shape verbatim.

    Style constraints:
    - py39 legacy typing: `Optional[X]`, `List[X]`, `Tuple[X, Y]` — NOT `X | None`. Add `# noqa: UP006,UP035` to the `from typing import ...` line (per Phase 37 D-08).
    - NO `from __future__ import annotations`.
    - Named imports only — no star-imports from `firestarter.constants`.
    - All Click `help="..."` strings on options/arguments MUST be byte-identical to the current argparse `help=` strings in main.py (preserve `--help` output for snapshot stability when entry point swaps in Wave 4).
    - `ruff check` + `ruff format --check` + `mypy firestarter/` must stay clean (Phase 37 watermark).

    Do NOT add any of the other 11 commands (read/write/verify/blank/erase/id/vpp/vpe/hw/config/fw + dev group) — those land in Wave 3. Do NOT touch `main.py` — entry point stays argparse this wave (D-11). Do NOT touch `pyproject.toml` — `click>=8.1` is already a transitive dep via the migration (the explicit `[project] dependencies` add happens in Wave 4 / Plan 41-04 per D-16).
  </action>
  <verify>
    <automated>cd firestarter_app && python -c "from firestarter.cli_handlers import cli, AppContext, _complete_eprom; print('OK')" && ruff check firestarter/cli_handlers.py && ruff format --check firestarter/cli_handlers.py && mypy firestarter/cli_handlers.py</automated>
  </verify>
  <acceptance_criteria>
    - `firestarter_app/firestarter/cli_handlers.py` exists
    - `grep -c "^@dataclass" firestarter_app/firestarter/cli_handlers.py` returns at least 1
    - `grep -c "^class AppContext:" firestarter_app/firestarter/cli_handlers.py` returns 1
    - `grep -c "^@click.group()" firestarter_app/firestarter/cli_handlers.py` returns 1
    - `grep -cE "^@cli\.command\(" firestarter_app/firestarter/cli_handlers.py` returns exactly 3 (for `list`, `info`, `search`)
    - `grep -c "shell_complete=_complete_eprom" firestarter_app/firestarter/cli_handlers.py` returns at least 1 (info command at minimum)
    - `grep -c "def _complete_eprom(" firestarter_app/firestarter/cli_handlers.py` returns 1
    - `grep -c "click.shell_completion.CompletionItem" firestarter_app/firestarter/cli_handlers.py` returns at least 1
    - `grep -c "from __future__ import annotations" firestarter_app/firestarter/cli_handlers.py` returns 0 (py39 style, no future-annotations)
    - `grep -c "from firestarter.constants import \*" firestarter_app/firestarter/cli_handlers.py` returns 0 (named imports only, Phase 39 D-06)
    - `grep -cE "from typing import.*(Optional|List|Tuple)" firestarter_app/firestarter/cli_handlers.py` returns at least 1 (py39 legacy typing import present)
    - `cd firestarter_app && python -c "from firestarter.cli_handlers import cli, AppContext, _complete_eprom"` exits 0
    - `cd firestarter_app && ruff check firestarter/cli_handlers.py` exits 0
    - `cd firestarter_app && ruff format --check firestarter/cli_handlers.py` exits 0
    - `cd firestarter_app && mypy firestarter/cli_handlers.py` exits 0 (no new errors vs. Phase 37 watermark)
    - `firestarter_app/firestarter/main.py` is UNCHANGED in this task (entry point stays argparse per D-11): `cd firestarter_app && git diff firestarter/main.py` is empty
  </acceptance_criteria>
  <done>
    cli_handlers.py contains a working AppContext dataclass, a Click group `cli` with global -v/-p/--version options + ctx.obj wiring, the `_complete_eprom` shell_complete callback, and three @cli.command()s (list/info/search) with all help strings preserved verbatim from argparse; the module imports cleanly; ruff + mypy stay green; main.py untouched.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create tests/test_cli_handlers.py with CliRunner happy-path + exact-match assertions</name>
  <files>firestarter_app/tests/test_cli_handlers.py</files>
  <read_first>
    - firestarter_app/firestarter/cli_handlers.py (the just-created file — observe the exact AppContext fields, the cli group signature, and the 3 commands' option shapes)
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-11 specifies CliRunner test scope: happy-path for list/info/search + --help + --version; D-13.2 specifies the no-prefix-matching assertion shape; "Claude's Discretion" line on exact CliRunner test count per command — recommend at least one happy-path + one error-path per command)
    - firestarter_app/tests/test_characterization.py (Phase 36 subprocess-golden pattern — for fixture naming consistency; do NOT use subprocess here, this is in-process CliRunner)
    - .planning/phases/36-characterization-test-baseline/36-CONTEXT.md (D-02 in-process fixture pattern)
    - firestarter_app/firestarter/database.py (EpromDatabase + skip_local_override constructor seam — CliRunner tests can construct `EpromDatabase(skip_local_override=True)` for hermetic tests)
  </read_first>
  <action>
    Create the new file `firestarter_app/tests/test_cli_handlers.py`. Required structure:

    1. Module docstring (≤2 lines) — names the file as the in-process CliRunner suite for `firestarter.cli_handlers.cli`; Wave 2 covers the read-only command surface; remaining commands land in Wave 3 / Plan 41-03.
    2. Imports — `pytest`, `from click.testing import CliRunner`, `from firestarter.cli_handlers import cli, AppContext` (NOT `from firestarter.main`), and named imports from any factory modules needed to construct a hermetic `AppContext` for tests where mocking is preferred (the planner picks: full real `AppContext` via `EpromDatabase(skip_local_override=True)`, or `unittest.mock.Mock()` stubs for managers that would attempt serial I/O). For the 3 read-only commands (list/info/search) the real `EpromDatabase` is the cleanest path — no serial concern.
    3. Module-level `runner = CliRunner()` fixture.
    4. `test_cli_help_runs()` — `result = runner.invoke(cli, ["--help"])`; assert `result.exit_code == 0`; assert `"Usage:" in result.output`; assert the Click-formatted usage string mentions at least `list`, `info`, `search`.
    5. `test_cli_version_runs()` — `result = runner.invoke(cli, ["--version"])`; assert `result.exit_code == 0`; assert `"Firestarter" in result.output` (matches the `prog_name="Firestarter"` set in `@click.version_option`).
    6. `test_list_happy_path()` — `result = runner.invoke(cli, ["list"])`; assert `result.exit_code == 0`; assert at least one known chip name appears in `result.output` (e.g. `W27C512`) — proves the real DB was queried.
    7. `test_info_happy_path()` — `result = runner.invoke(cli, ["info", "W27C512"])`; assert `result.exit_code == 0`; assert `"W27C512" in result.output`.
    8. `test_info_unknown_chip_error_path()` — `result = runner.invoke(cli, ["info", "NOPE_NOT_A_CHIP"])`; assert `result.exit_code == 1` (chip-not-found maps to log + exit 1 per the existing argparse contract — preserved by `_resolve_or_exit` semantics in Wave 3; for Wave 2 the `info` command needs to surface the same exit 1 if it depends on chip resolution; if Wave 2's `info` is purely DB-query without chip resolution, assert the equivalent error shape from the current argparse `info` handler — preserve verbatim).
    9. `test_search_happy_path()` — `result = runner.invoke(cli, ["search", "W27"])`; assert `result.exit_code == 0`; assert at least one chip name matching `W27` is in `result.output`.
    10. `test_no_prefix_matching()` (TRAP #2, D-13.2) — `result = runner.invoke(cli, ["lis"])`; assert `result.exit_code != 0`; assert `"No such command" in result.output` (or `"Usage:" in result.output` AND `"lis" in result.output` — Click's actual error wording is "Error: No such command 'lis'."). This pins Click's exact-match behaviour as a regression guard against any future configuration that enables prefix matching.

    Style constraints:
    - py39 legacy typing throughout — no `from __future__ import annotations`.
    - Use `runner.invoke(cli, [...])` consistently — do not use `subprocess`-based invocation (that's Phase 36's domain; CliRunner is the in-process complement).
    - Test function names follow `test_<command>_<scenario>` convention to match Phase 36 D-02 fixture style.
    - `ruff check` + `ruff format --check` + `mypy firestarter/` must stay clean (test files are under the same gate per Phase 37 D-09).

    Do NOT add tests for read/write/verify/blank/erase/id/vpp/vpe/hw/fw/config or any dev sub-command — those land in Wave 3 / Plan 41-03 alongside the command implementations.
  </action>
  <verify>
    <automated>cd firestarter_app && pytest tests/test_cli_handlers.py -v</automated>
  </verify>
  <acceptance_criteria>
    - `firestarter_app/tests/test_cli_handlers.py` exists
    - `grep -c "from click.testing import CliRunner" firestarter_app/tests/test_cli_handlers.py` returns 1
    - `grep -c "from firestarter.cli_handlers import" firestarter_app/tests/test_cli_handlers.py` returns at least 1
    - `grep -c "from firestarter.main import" firestarter_app/tests/test_cli_handlers.py` returns 0 (test targets cli_handlers directly, not the argparse entry point)
    - `grep -cE "^def test_" firestarter_app/tests/test_cli_handlers.py` returns at least 6 (help, version, list_happy, info_happy, info_error, search_happy, no_prefix_matching → ≥7 typical)
    - `grep -c "runner.invoke(cli" firestarter_app/tests/test_cli_handlers.py` returns at least 6
    - `grep -c "No such command" firestarter_app/tests/test_cli_handlers.py` returns at least 1 (no-prefix-matching trap assertion present, D-13.2)
    - `cd firestarter_app && pytest tests/test_cli_handlers.py -v` exits 0
    - All test functions pass (no skips, no xfails, no errors)
    - `cd firestarter_app && ruff check tests/test_cli_handlers.py` exits 0
    - `cd firestarter_app && ruff format --check tests/test_cli_handlers.py` exits 0
    - `cd firestarter_app && mypy firestarter/` exits 0 (no new errors vs. Phase 37 watermark; the test file itself is not under mypy strict per Phase 37 D-08 but the imported `cli_handlers.py` is gradual-typed clean)
  </acceptance_criteria>
  <done>
    test_cli_handlers.py contains ≥6 CliRunner tests covering the 3 read-only commands' happy-paths + at least one error path + `--help` + `--version` + the no-prefix-matching trap assertion; all pass; ruff/format gate clean.
  </done>
</task>

<task type="auto">
  <name>Task 3: Verify Phase 36 subprocess goldens stay green + full gate; commit cli_handlers.py + test_cli_handlers.py</name>
  <files>firestarter_app/firestarter/cli_handlers.py, firestarter_app/tests/test_cli_handlers.py</files>
  <read_first>
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-11 explicit: entry point STAYS argparse this wave; Phase 36 subprocess goldens stay green; CliRunner suite complements them in-process)
    - firestarter_app/tests/test_characterization.py (Phase 36 subprocess-golden test — must stay green; this wave does NOT touch the argparse path)
    - .planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md (the CI gate the local run must mirror)
  </read_first>
  <action>
    Run the full firestarter_app gate locally to confirm Wave 2 has not regressed anything:
    1. `cd firestarter_app && ruff check . && ruff format --check . && mypy firestarter/` — must exit 0.
    2. `cd firestarter_app && pytest -v` — Wave 1's xfail flip already in; this wave adds ≥6 new CliRunner tests. Expect 163 + new_test_count passed + 1 xfail (BUG-2) + 29 snapshots green.
    3. `cd firestarter_app && pytest tests/test_characterization.py -v` — Phase 36 subprocess goldens MUST stay green (argparse entry point untouched this wave per D-11). Any drift here is a regression to fix in-wave, NOT a snapshot update.

    Then commit BOTH new files in a single atomic commit on the firestarter_app/ submodule's `v1.8-app-cleanup` branch. Suggested commit message (HEREDOC):

    Subject: `feat(41-02): land Click skeleton + 3 read-only commands as dead code (CLI-01, CLI-02)`
    Body: `Wave 2 of Phase 41. Creates firestarter/cli_handlers.py with AppContext dataclass, cli @click.group() with -v/-p/--version + ctx.obj setup, _complete_eprom shell_complete callback (CLI-04 prep), and 3 @cli.command()s: list, info, search. Adds tests/test_cli_handlers.py with CliRunner happy-path + error-path + no-prefix-matching trap (D-13.2). Entry point in main.py STAYS argparse — cli_handlers.py is dead code from the user's perspective until Wave 4 (Plan 41-04). Phase 36 subprocess goldens remain green (argparse path unchanged).`

    Do NOT amend prior commits. Worktrees off per `project_v18_phase_execution_mechanics`; the executor runs sequentially.
  </action>
  <verify>
    <automated>cd firestarter_app && ruff check . && ruff format --check . && mypy firestarter/ && pytest -v 2>&1 | tail -5 && pytest tests/test_characterization.py -v 2>&1 | tail -5</automated>
  </verify>
  <acceptance_criteria>
    - `cd firestarter_app && ruff check .` exits 0
    - `cd firestarter_app && ruff format --check .` exits 0
    - `cd firestarter_app && mypy firestarter/` exits 0 (no new errors vs. Phase 37 watermark)
    - `cd firestarter_app && pytest -v` exits 0; output contains "passed" and exactly 1 xfail (BUG-2; BUG-1 already flipped in W1)
    - `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (Phase 36 subprocess goldens green — argparse path untouched per D-11)
    - `cd firestarter_app && pytest tests/test_cli_handlers.py -v` exits 0
    - `cd firestarter_app && git log -1 --name-only` lists exactly `firestarter/cli_handlers.py` and `tests/test_cli_handlers.py` (no other files touched)
    - `firestarter_app/firestarter/main.py` is byte-identical to its state at the end of Wave 1: `cd firestarter_app && git diff HEAD~1 -- firestarter/main.py` is empty
    - `firestarter_app/pyproject.toml` is byte-identical to its state at the end of Wave 1: `cd firestarter_app && git diff HEAD~1 -- pyproject.toml` is empty (the `click>=8.1` / `argcomplete` swap is Wave 4 territory)
    - The commit lands on branch `v1.8-app-cleanup`: `cd firestarter_app && git rev-parse --abbrev-ref HEAD` returns `v1.8-app-cleanup`
  </acceptance_criteria>
  <done>
    Single atomic commit on firestarter_app `v1.8-app-cleanup` branch lands cli_handlers.py + test_cli_handlers.py; the full lint/type/test gate is green; Phase 36 subprocess goldens are unaffected; main.py + pyproject.toml are untouched.
  </done>
</task>

</tasks>

<verification>
- `cd firestarter_app && ruff check . && ruff format --check . && mypy firestarter/` exits 0
- `cd firestarter_app && pytest -v` exits 0 with all tests passing + 1 xfail (BUG-2)
- `cd firestarter_app && pytest tests/test_cli_handlers.py -v` exits 0 (≥6 new tests passing)
- `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (Phase 36 subprocess goldens unchanged)
- `cd firestarter_app && python -c "from firestarter.cli_handlers import cli, AppContext, _complete_eprom"` exits 0
- `grep -cE "^@cli\.command\(" firestarter_app/firestarter/cli_handlers.py` returns 3
- `firestarter_app/firestarter/main.py` and `firestarter_app/pyproject.toml` are byte-identical to their post-Wave-1 state
</verification>

<success_criteria>
3/14 commands (`list`, `info`, `search`) implemented as Click `@cli.command()`s in the new `cli_handlers.py`, with AppContext dataclass + Click group + global options + `_complete_eprom` shell_complete callback wired. CliRunner test suite covers happy-paths + at least one error path + Click's exact-match (no-prefix-matching) behaviour. Entry point stays argparse; cli_handlers.py is reviewable dead code awaiting Wave 4's swap. Closes 3/14 of CLI-02 + scaffolds CLI-01.
</success_criteria>

<output>
Create `.planning/phases/41-cli-migration-argparse-click/41-02-SUMMARY.md` when done.
</output>

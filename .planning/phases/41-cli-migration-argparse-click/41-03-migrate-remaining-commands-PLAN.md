---
phase: 41-cli-migration-argparse-click
plan: 03
type: execute
wave: 3
depends_on:
  - 41-02
files_modified:
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/tests/test_cli_handlers.py
autonomous: true
requirements:
  - CLI-01
  - CLI-02
must_haves:
  truths:
    - "GATE-1.8a: wire protocol byte-identical — this plan adds Click handlers in cli_handlers.py only; serial/wire code untouched"
    - "GATE-1.8b: end-user CLI surface preserved — entry point STAYS argparse this wave (per D-12); Phase 36 subprocess goldens stay green (29 snapshots + 2 xfails — BUG-1 already flipped in W1, BUG-2 stays xfail through this phase); cli_handlers.py is dead code from the user's perspective"
    - "GATE-1.8c: constants.py + firmware header parity untouched (named imports only per Phase 39 D-06)"
    - "GATE-1.8d: read path ring-fence — no edits to eprom_operator.read_eprom or _read_and_parse_lines; the new `read` Click handler calls `app.eprom_operator.read_eprom(...)` with byte-identical kwargs"
    - "GATE-1.8e: full suite green (Wave 2 floor + ≥11 new CliRunner happy-paths + ≥11 error-paths); pip entry point installs and runs (argparse path)"
    - "cli_handlers.py grows by 11 commands: 6 chip-ops (`read`, `write`, `verify`, `blank`, `erase`, `id`) + 2 voltage (`vpp`, `vpe`) + 2 hardware (`hw`, `config`) + 1 firmware (`fw`) + the `dev` @cli.group() with 4 sub-commands (`read`, `reg`, `addr`, `consistency-check`) — per D-12 step 1..5"
    - "TRAP #1 (exit codes) handled: every chip-op + voltage + hardware + fw + dev handler uses `sys.exit(0 if op() else 1)` per D-08/D-13.1; `_resolve_or_exit` returning None maps to `sys.exit(1)`"
    - "TRAP #3 (`--no-blank-check` polarity) handled on `write` per D-13.3: `@click.option('-b', '--no-blank-check', 'blank_check', is_flag=True, flag_value=False, default=True, ...)` — presence flips blank_check to False; default True. The inverse `erase` command keeps `-b/--blank-check` `store_true default=False` shape — both polarities live side by side in cli_handlers.py"
    - "TRAP #4 (3-way mutex `--pre`/`--firmware-version`/`--stable`) handled on `fw` per D-13.4 via per-option callback that inspects `ctx.params` for the other two and raises `click.BadParameter` — exits with code 2 matching argparse's `add_mutually_exclusive_group` behaviour. Mutex applies in BOTH install AND `--list` contexts."
    - "TRAP #5 (`_validate_firmware_version`) re-wired per D-13.5 as a custom Click `ParamType` subclass — reusable, Click-canonical; raises `click.BadParameter` on mismatch (exit-2 preserved); imports `FIRMWARE_VERSION_RE` from `firestarter.firmware` unchanged. The transport-layer `SerialCommunicator._validate_firmware_version` @staticmethod from Phase 40 D-01..D-05 is a DIFFERENT function and is NOT touched."
    - "TRAP #2 (no prefix matching) — already pinned in W2's `test_no_prefix_matching` test; this plan inherits coverage"
    - "D-14 narrow upgrade: `fw_parser.error('--json requires --list')` (main.py:798) becomes `raise click.UsageError('--json requires --list')` in the `fw` handler body — exit-2 + 'Usage:' formatting preserved"
    - "D-15 `_maybe_auto_route_to_pre` adapter — preserved verbatim; Click handler builds `SimpleNamespace(**locals())` (or equivalent SimpleNamespace of the option kwargs) and calls the helper with zero churn to the helper's body. Rationale: the helper stays put for now; refactor to explicit kwargs is rejected as additional churn (D-15 lets planner pick — picking the lower-churn option per the standing 'minimize churn / preserve git blame' style)"
    - "`dev consistency-check` 3-way verdict (0=PASS / 1=FAIL / 2=hardware-error) preserved per D-12 step 5: `sys.exit(verdict_int)` directly, NOT bool-to-int wrap"
    - "All 9 chip-op + 2 dev-eprom-arg sites NOTE: the `info` command got `shell_complete=_complete_eprom` in W2; this wave attaches it to the 6 chip-ops + the 2 dev sub-commands that take `eprom` (`dev read`, `dev addr`). The Wave 4 entry-point swap adds the last 1 site to match (per D-16); through this wave 9 sites total carry `shell_complete=_complete_eprom`"
    - "py39 legacy `Optional[X]` / `List[X]` / `Tuple[X,Y]` style throughout; no `from __future__ import annotations`; `# noqa: UP006/UP035` on legacy imports per Phase 37 D-08"
    - "Named imports only — no `from firestarter.constants import *` in cli_handlers.py per Phase 39 D-06"
    - "AppContext stays in cli_handlers.py (Claude's Discretion — operator delegated; close to the Click group that constructs it, no separate app_context.py)"
    - "Sub-commit ordering — Wave 3 ships as ONE atomic commit per the v1.8 phase style (Phase 38/39/40 each shipped wave-as-one-commit). Rationale: keeps the CLI surface migration reviewable as a single diff; per-command sub-commits would split a single semantic unit (the migration is meaningless without all 11 commands landing together)."
    - "no-touch invariant: serial_comm.py, eprom_operations.py, hardware.py, firmware.py, database.py, chip_resolver.py, eprom_info.py, config.py, exceptions.py, address_parser.py, constants.py, codec.py, frame_parser.py, logging_utils.py, data/chip_database.json, data/pinouts.json, tests/__snapshots__/, main.py (entry point stays argparse), pyproject.toml, autocomplete.md, .github/workflows/ci.yml, the firmware sub-repo — none touched in this plan"
  artifacts:
    - path: "firestarter_app/firestarter/cli_handlers.py"
      provides: "AppContext + Click group + 14 top-level commands + dev @cli.group() with 4 sub-commands + ParamType for firmware-version validation + build_arg_flags consumer pattern"
      contains: "@cli.command"
      min_lines: 500
    - path: "firestarter_app/tests/test_cli_handlers.py"
      provides: "CliRunner happy-path + error-path coverage for all 11 new commands (read/write/verify/blank/erase/id/vpp/vpe/hw/config/fw + dev read/reg/addr/consistency-check)"
      contains: "runner.invoke(cli"
      min_lines: 200
  key_links:
    - from: "firestarter_app/firestarter/cli_handlers.py::read|write|verify|blank|erase|id"
      to: "firestarter_app/firestarter/chip_resolver.py::resolve_chip"
      via: "_resolve_or_exit(name, app.db) — relocated verbatim from main.py:521-533 per D-08"
      pattern: "_resolve_or_exit"
    - from: "firestarter_app/firestarter/cli_handlers.py::write|erase"
      to: "firestarter_app/firestarter/eprom_operations.py::EpromOperator"
      via: "app.eprom_operator.<op>(...) — byte-identical kwargs to argparse handlers in main.py:692-746"
      pattern: "app\\.eprom_operator\\."
    - from: "firestarter_app/firestarter/cli_handlers.py::fw"
      to: "firestarter_app/firestarter/firmware.py::FIRMWARE_VERSION_RE"
      via: "_FirmwareVersionType.convert() ParamType — reuses the existing regex"
      pattern: "FIRMWARE_VERSION_RE"
    - from: "firestarter_app/firestarter/cli_handlers.py::dev consistency-check"
      to: "firestarter_app/firestarter/eprom_operations.py::EpromOperator.consistency_check_eprom"
      via: "verdict_int = app.eprom_operator.consistency_check_eprom(...); sys.exit(verdict_int)"
      pattern: "consistency_check_eprom"
---

<objective>
Wave 3 / Plan 41-03 — Migrate the remaining 11 commands from `main.py`'s 14-branch argparse dispatcher into `cli_handlers.py` as `@cli.command()` decorated functions (per D-12). The Click migration completes for cli_handlers.py: 6 chip-ops (`read`/`write`/`verify`/`blank`/`erase`/`id`) + 2 voltage (`vpp`/`vpe`) + 2 hardware (`hw`/`config`) + 1 firmware (`fw` with 3-way mutex + version validator) + the `dev` `@cli.group()` with 4 sub-commands (`read`/`reg`/`addr`/`consistency-check`). This plan addresses argparse→Click TRAPs #1, #3, #4, #5 (TRAP #2 already locked in W2). Each command gets a CliRunner happy-path test + at least one error-path test (per D-12 step 6).

Entry point in `main.py` STAYS argparse this wave (per D-12). `cli_handlers.py` is now feature-complete reviewable dead code; the user-visible swap happens in Wave 4 / Plan 41-04. Phase 36 subprocess goldens stay green (argparse path unchanged this wave).

Purpose: Land the bulk of the Click migration — all 11 remaining handlers + their tests — in one atomic commit, with full TRAP coverage and the 3-way `dev consistency-check` exit-code contract preserved verbatim. Closes 14/14 toward CLI-02 (every user-facing command lives in cli_handlers.py); closes the TRAP-handling half of CLI-01.

Output: One atomic commit on the `firestarter_app/` submodule's `v1.8-app-cleanup` branch; two files modified (cli_handlers.py extended; test_cli_handlers.py extended).
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
@.planning/phases/41-cli-migration-argparse-click/41-01-build-arg-flags-fix-PLAN.md
@.planning/phases/41-cli-migration-argparse-click/41-02-click-skeleton-readonly-commands-PLAN.md
@.planning/phases/40-serial-transport-restructure/40-CONTEXT.md
@.planning/phases/39-database-cleanup-chip-resolver/39-CONTEXT.md
@.planning/phases/38-low-risk-extractions/38-CONTEXT.md
@.planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md
@.planning/phases/36-characterization-test-baseline/36-CONTEXT.md
@firestarter_app/CLAUDE.md
@firestarter_app/firestarter/cli_handlers.py
@firestarter_app/firestarter/main.py
@firestarter_app/firestarter/eprom_operations.py
@firestarter_app/firestarter/hardware.py
@firestarter_app/firestarter/firmware.py
@firestarter_app/firestarter/chip_resolver.py
@firestarter_app/firestarter/address_parser.py
@firestarter_app/firestarter/exceptions.py
@firestarter_app/tests/test_cli_handlers.py
</context>

<canonical_refs>
- **D-12** — Wave 3 scope: migrate the 11 remaining commands in 5 grouped steps (chip-ops, voltage, hardware, fw, dev).
- **D-13.1/.3/.4/.5** — TRAPs #1 (exit codes), #3 (`--no-blank-check` polarity), #4 (3-way mutex), #5 (`_validate_firmware_version` re-wire).
- **D-14** — Narrow `fw_parser.error → click.UsageError` upgrade in the `fw` handler body.
- **D-15** — `_maybe_auto_route_to_pre` adapter: `SimpleNamespace` zero-churn pattern picked.
- **D-08** — Minimal error-mapping scope; `_resolve_or_exit` shim relocated unchanged.
- **D-17** — Wave 3 depends on Wave 2 (cli_handlers.py exists with AppContext + cli group + read-only commands).
- **Phase 39 D-01..D-04** — `chip_resolver.resolve_chip(name) -> dict` raising `ChipNotFoundError`; consumed via `_resolve_or_exit`.
- **Phase 40 D-01..D-05** — `SerialCommunicator._validate_firmware_version` @staticmethod is a TRANSPORT-LAYER guard, distinct from main.py's `_validate_firmware_version` argparse type validator (which IS re-wired this wave).
- **Phase 38 D-04** — `address_parser.parse_address`/`parse_size` raise `ValueError`; the new Click handlers continue to delegate to these (no re-implementation needed).
- **Phase 37 D-08** — py39 floor; legacy `Optional[X]` / `List[X]` / `Tuple[X,Y]` style; `# noqa: UP006/UP035` markers.
- **Phase 37 D-09** — ruff E/F/I/UP rule set.
- **Phase 36 D-01** — subprocess goldens migration-transparent; stay green through this wave (argparse path untouched).
- **Phase 36 D-06** — `EpromDatabase(skip_local_override=True)` constructor seam for test isolation.
</canonical_refs>

<tasks>

<task type="auto">
  <name>Task 1: Extend cli_handlers.py — chip-ops (read/write/verify/blank/erase/id) + voltage (vpp/vpe) + hardware (hw/config)</name>
  <files>firestarter_app/firestarter/cli_handlers.py</files>
  <read_first>
    - firestarter_app/firestarter/cli_handlers.py (current state from W2 — observe AppContext fields, the cli group, _complete_eprom callback, and the 3 read-only commands' style; new handlers MUST follow the same pattern)
    - firestarter_app/firestarter/main.py (the source of truth for every command being migrated, in this exact order):
      • `create_read_args` (lines 72-93) + dispatch branch at line 676 — for read command shape, options, and `app.eprom_operator.read_eprom(...)` invocation
      • `create_write_args` (lines 95-119) + dispatch branch at line 692 — for write command shape; observe the `-b/--no-blank-check` `store_false default=True` polarity (TRAP #3)
      • `create_verify_args` (lines 121-136) + dispatch branch at line 707 — for verify command shape
      • `create_blank_check_args` (lines 138-147) + dispatch branch at line 722 — for blank command shape
      • `create_erase_parser` (lines 149-173) + dispatch branch at line 733 — for erase command shape; observe the inverse `-b/--blank-check` `store_true default=False` polarity (kept verbatim; TRAP #3 applies to write only)
      • `create_id_args` (lines 175-184) + dispatch branch at line 747 — for id command shape
      • `create_voltage_args` (lines 186-192) + dispatch branches at lines 779 (vpe) and 787 (vpp) — for vpp/vpe command shape; observe `--timeout` `help=SUPPRESS` semantics → Click `hidden=True`
      • main.py:848 (`hw` dispatch — calls `app.hardware_manager.read_hw_revision()` etc.) + the bare `hw_parser = subparsers.add_parser("hw", ...)` registration
      • `create_config_args` (lines 354-370) + dispatch branch at line 854 — for config command shape (`--rev`, `-r1/--r16`, `-r2/--r14r15`)
    - firestarter_app/firestarter/eprom_operations.py (the public methods called by the 6 chip-op handlers: `read_eprom`, `write_eprom`, `verify_eprom`, `blank_check_eprom`, `erase_eprom`, `check_chip_id` — preserve exact kwargs)
    - firestarter_app/firestarter/hardware.py (the public methods called by voltage + hw + config handlers: `read_vpp_voltage`, `read_vpe_voltage`, `read_hw_revision`, `write_config`)
    - firestarter_app/firestarter/chip_resolver.py (the `resolve_chip(name)` function — raises `ChipNotFoundError`)
    - firestarter_app/firestarter/exceptions.py (the `ChipNotFoundError` class — caught by `_resolve_or_exit`)
    - firestarter_app/firestarter/address_parser.py (`parse_address`/`parse_size` raising `ValueError`)
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-12 step 1-3 for the command order; D-13.3 for TRAP #3 polarity; D-08 for the `_resolve_or_exit` relocation)
  </read_first>
  <action>
    Extend `firestarter_app/firestarter/cli_handlers.py` with the following additions, IN THIS ORDER (appended after the existing W2 content). Do NOT touch main.py, do NOT touch pyproject.toml, do NOT modify the W2 content beyond appending.

    **Step 1.0 — relocate `_resolve_or_exit` shim** (per D-08): copy the helper at main.py:521-533 into cli_handlers.py verbatim (signature `def _resolve_or_exit(name: str, db: EpromDatabase) -> Optional[dict]:`, with legacy `Optional` style per Phase 37 D-08). The function catches `ChipNotFoundError`, logs `f"EPROM '{name}' not found in database."`, returns `None`. Place it next to the other module-level helpers (before the first `@cli.command()`). DO NOT delete it from main.py yet — Wave 4 / Plan 41-04 deletes the main.py copy after entry-point swap. Both copies coexist through this wave (the argparse dispatcher in main.py still uses its local copy; cli_handlers.py's copy is dead code from the user's perspective).

    **Step 1.1 — `read` command:**
    ```
    @cli.command(name="read")
    @click.argument("eprom", shell_complete=_complete_eprom)
    @click.argument("output_file", required=False)
    @click.option("-f", "--force", is_flag=True, ...)
    @click.option("-a", "--address", default=None, ...)
    @click.option("-s", "--size", default=None, ...)
    @click.pass_obj
    def read(app: AppContext, eprom: str, output_file: Optional[str], force: bool, address: Optional[str], size: Optional[str]) -> None:
    ```
    Body: call `eprom_data = _resolve_or_exit(eprom, app.db)`; if None, `sys.exit(1)`; build kwargs identical to main.py:676-691; call `ok = app.eprom_operator.read_eprom(eprom, eprom_data, output_file, force=force, address=address, size=size)`; `sys.exit(0 if ok else 1)`. Preserve all `help="..."` strings byte-identical to argparse via the `help=` kwarg on each `@click.option`.

    **Step 1.2 — `write` command** (per D-13.3 TRAP #3):
    ```
    @click.option("-b", "--no-blank-check", "blank_check", is_flag=True, flag_value=False, default=True, help="<verbatim from argparse>")
    ```
    Body: `_resolve_or_exit` → `app.eprom_operator.write_eprom(..., blank_check=blank_check, ...)` (Note: the argparse handler also forwards `vpe_as_vpp`, `force`, `address`, `size` — preserve all kwargs verbatim). `sys.exit(0 if ok else 1)`.

    **Step 1.3 — `verify`, `blank`, `id` commands**: same shape as `read` (each takes `eprom` + chip-op-specific options); body resolves chip then calls the corresponding `app.eprom_operator.<op>` method; `sys.exit(0 if ok else 1)` semantics. Preserve all options + defaults + help strings verbatim from `create_verify_args` / `create_blank_check_args` / `create_id_args`.

    **Step 1.4 — `erase` command** (inverse polarity vs write, KEPT VERBATIM per D-13.3 — both polarities coexist):
    ```
    @click.option("-b", "--blank-check", "blank_check", is_flag=True, default=False, help="<verbatim from argparse>")
    ```
    Body: `_resolve_or_exit` → `app.eprom_operator.erase_eprom(..., blank_check=blank_check, ...)`; `sys.exit(0 if ok else 1)`.

    **Step 2.0 — `vpp` and `vpe` commands** (D-12 step 2). Both take `--timeout` with Click `hidden=True` (mirrors argparse `help=argparse.SUPPRESS`). Body calls `app.hardware_manager.read_vpp_voltage(timeout=timeout)` (or `read_vpe_voltage`); preserve the print/format flow from main.py:779-794. `sys.exit(0 if ok else 1)`.

    **Step 3.0 — `hw` command** (D-12 step 3). No flags. Body calls `app.hardware_manager.read_hw_revision()` (or whatever the argparse `hw` dispatch at main.py:848 does — preserve verbatim). `sys.exit(0 if ok else 1)`.

    **Step 3.1 — `config` command** (D-12 step 3). Options: `--rev`, `-r1/--r16`, `-r2/--r14r15` per `create_config_args` (main.py:354-370). Body calls `app.hardware_manager.write_config(...)` with kwargs preserved verbatim from main.py:854-861. `sys.exit(0 if ok else 1)`.

    **Style constraints (apply to all 10 commands in this task):**
    - py39 legacy typing throughout — `Optional[X]` not `X | None`; reuse the `from typing import ...` already imported in W2.
    - NO `from __future__ import annotations`.
    - Named imports only — no star-imports.
    - All `help="..."` strings byte-identical to the corresponding argparse `help=` text in main.py (preserves `--help` output for snapshot stability through Wave 4's entry-point swap).
    - Function-level names that shadow builtins (`list`, `id`) use a `_<name>_cmd` underscore convention (or keep verbatim `id` if it doesn't shadow at module scope — W2's `_list_cmd` pattern is the precedent; `read`/`write`/`verify`/`blank`/`erase`/`vpp`/`vpe`/`hw`/`config` are fine as-is).
    - The 6 chip-op commands and the 2 dev sub-commands that take `eprom` (added in Task 2 below) MUST carry `shell_complete=_complete_eprom` on their `eprom` argument per D-02 — that's 6 sites in this task + 2 sites in Task 2 + the `info` site already in W2 = 9 total through Wave 3.
    - `ruff check` + `ruff format --check` + `mypy firestarter/cli_handlers.py` must stay clean (Phase 37 watermark).

    Do NOT add `fw`, `dev` group, or any of its sub-commands here — Task 2 handles them. Do NOT touch `main.py` or `pyproject.toml` — entry-point swap is Wave 4.
  </action>
  <verify>
    <automated>cd firestarter_app && python -c "from firestarter.cli_handlers import cli; cmds = sorted(cli.commands.keys()); print(cmds); assert 'read' in cmds and 'write' in cmds and 'verify' in cmds and 'blank' in cmds and 'erase' in cmds and 'id' in cmds and 'vpp' in cmds and 'vpe' in cmds and 'hw' in cmds and 'config' in cmds, cmds" && ruff check firestarter/cli_handlers.py && ruff format --check firestarter/cli_handlers.py && mypy firestarter/cli_handlers.py</automated>
  </verify>
  <acceptance_criteria>
    - `grep -cE "^@cli\.command\(" firestarter_app/firestarter/cli_handlers.py` returns at least 13 (3 from W2: list/info/search + 10 from this task: read/write/verify/blank/erase/id/vpp/vpe/hw/config). Final number after Task 2 will be 14 + the `dev` group + 4 dev subcommands.
    - `grep -c "shell_complete=_complete_eprom" firestarter_app/firestarter/cli_handlers.py` returns at least 7 (1 from W2: info + 6 chip-ops from this task)
    - `grep -c "_resolve_or_exit" firestarter_app/firestarter/cli_handlers.py` returns at least 7 (1 definition + 6 chip-op call sites)
    - `grep -c "def _resolve_or_exit" firestarter_app/firestarter/cli_handlers.py` returns 1
    - `grep -cE 'flag_value=False.*default=True' firestarter_app/firestarter/cli_handlers.py` returns at least 1 (the `--no-blank-check` polarity per TRAP #3 / D-13.3)
    - `grep -cE 'is_flag=True.*default=False' firestarter_app/firestarter/cli_handlers.py` returns at least 1 (the inverse `--blank-check` on erase — both polarities coexist per D-13.3)
    - `grep -c "app.eprom_operator.read_eprom" firestarter_app/firestarter/cli_handlers.py` returns at least 1
    - `grep -c "app.eprom_operator.write_eprom" firestarter_app/firestarter/cli_handlers.py` returns at least 1
    - `grep -c "app.eprom_operator.erase_eprom" firestarter_app/firestarter/cli_handlers.py` returns at least 1
    - `grep -c "app.hardware_manager" firestarter_app/firestarter/cli_handlers.py` returns at least 4 (vpp/vpe/hw/config)
    - `grep -c "hidden=True" firestarter_app/firestarter/cli_handlers.py` returns at least 2 (vpp/vpe `--timeout`)
    - `grep -c "from __future__ import annotations" firestarter_app/firestarter/cli_handlers.py` returns 0
    - `grep -c "from firestarter.constants import \*" firestarter_app/firestarter/cli_handlers.py` returns 0 (Phase 39 D-06)
    - `cd firestarter_app && python -c "from firestarter.cli_handlers import cli; print(sorted(cli.commands.keys()))"` exits 0 and lists at least: blank, config, erase, hw, id, info, list, read, search, verify, vpe, vpp, write
    - `cd firestarter_app && ruff check firestarter/cli_handlers.py` exits 0
    - `cd firestarter_app && ruff format --check firestarter/cli_handlers.py` exits 0
    - `cd firestarter_app && mypy firestarter/cli_handlers.py` exits 0 (no new errors vs. Phase 37 watermark)
    - `firestarter_app/firestarter/main.py` UNCHANGED in this task: `cd firestarter_app && git diff firestarter/main.py` is empty
    - `firestarter_app/pyproject.toml` UNCHANGED in this task: `cd firestarter_app && git diff pyproject.toml` is empty
  </acceptance_criteria>
  <done>
    cli_handlers.py contains 13 working `@cli.command()`s (3 from W2 + 10 from this task) covering all 6 chip-ops + 2 voltage + 2 hardware commands. `_resolve_or_exit` is relocated (both copies coexist through this wave). `--no-blank-check` polarity matches argparse on write; inverse `--blank-check` on erase preserved verbatim. ruff/format/mypy stay green. main.py + pyproject.toml untouched.
  </done>
</task>

<task type="auto">
  <name>Task 2: Extend cli_handlers.py — fw command (3-way mutex + ParamType) + dev @cli.group() with 4 sub-commands</name>
  <files>firestarter_app/firestarter/cli_handlers.py</files>
  <read_first>
    - firestarter_app/firestarter/cli_handlers.py (state after Task 1 — observe the established style; this task appends only)
    - firestarter_app/firestarter/main.py:
      • `_validate_firmware_version` (lines 194-208) — the argparse `type=` validator being re-wired as a Click ParamType (TRAP #5)
      • `_maybe_auto_route_to_pre` (lines 211-249) — magic-default helper preserved verbatim per D-15; reads `args.install`, `args.pre`, `args.firmware_version`, `args.stable` via `getattr(args, ...)`
      • `create_firmware_args` (lines 252-327) — for fw command shape, options, the `--pre`/`--firmware-version`/`--stable` 3-way mutex (argparse `add_mutually_exclusive_group()`)
      • `fw` dispatch branch at line 795-847 — for the body that calls `_maybe_auto_route_to_pre(args)`, the `--json requires --list` mutex check at line 798 (D-14 narrow upgrade), and the `app.firmware_manager.*` invocations
      • `create_dev_args` (lines 375-446) — for the dev group + 4 sub-commands (`read`, `reg`, `addr`, `consistency-check`)
      • `dev` dispatch branch at line 862-918 — body for each dev sub-command; especially line 908-917 for `consistency-check`'s 3-way verdict (`sys.exit(verdict_int)` directly per D-12 step 5)
      • `create_oe_ce_args` (lines 494-502) — shared OE/CE arg block used by `dev reg` and `dev addr`
    - firestarter_app/firestarter/firmware.py (the `FIRMWARE_VERSION_RE` regex consumed by the new Click ParamType per D-13.5; the public FirmwareManager methods called by the fw handler)
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-13.4 TRAP #4 callback-per-option shape; D-13.5 TRAP #5 custom ParamType pick; D-14 narrow UsageError upgrade; D-15 SimpleNamespace adapter pick; D-12 step 4-5 sub-commit ordering)
    - .planning/phases/40-serial-transport-restructure/40-CONTEXT.md (CRITICAL — D-01..D-05 introduced `SerialCommunicator._validate_firmware_version` @staticmethod which is the TRANSPORT-LAYER guard; the function being re-wired this wave is the DIFFERENT `_validate_firmware_version` argparse type validator at main.py:194-208; do NOT conflate them)
  </read_first>
  <action>
    Continue extending `firestarter_app/firestarter/cli_handlers.py` (appended after Task 1's content). This task lands the `fw` command + the `dev` group + 4 dev sub-commands. Do NOT touch main.py or pyproject.toml.

    **Step 2.0 — Custom Click ParamType for firmware-version validation (TRAP #5, D-13.5):**

    Define a `_FirmwareVersionType(click.ParamType)` subclass:
    - `name = "firmware_version"`.
    - `convert(self, value, param, ctx)` method: if `value is None`, return `None`; otherwise run the same regex match (`FIRMWARE_VERSION_RE.fullmatch(value)`) that `main.py:194-208` does; on mismatch, raise `self.fail(f"Invalid firmware version: {value!r} ...", param, ctx)` — which translates to a Click `BadParameter` with exit-2 semantics, mirroring the argparse `ArgumentTypeError → SystemExit(2)` path.
    - Import `FIRMWARE_VERSION_RE` from `firestarter.firmware` (named import — Phase 39 D-06).
    - **Rationale documented inline in module-level comment:** "Custom ParamType subclass picked over plain option callback (D-13.5; Claude's Discretion) — more Click-canonical + reusable across `--firmware-version` instances if ever added elsewhere."

    Rationale-locked note: Do NOT touch the Phase 40 `SerialCommunicator._validate_firmware_version` @staticmethod — it is a TRANSPORT-LAYER guard introduced by Phase 40 D-01..D-05 and is a different function. The re-wiring this wave is the `main.py:194-208` argparse type validator only.

    **Step 2.1 — 3-way mutex callback (TRAP #4, D-13.4):**

    Define a module-level helper `_check_install_mutex(ctx, param, value)` callback:
    - On invocation, inspects `ctx.params` for the OTHER two options (e.g. if called for `--pre`, checks `ctx.params.get("firmware_version")` and `ctx.params.get("stable")`).
    - If `value` is truthy AND any of the other two are truthy, `raise click.BadParameter(f"--{param.name} is mutually exclusive with --<other>")` — exit-2 semantics.
    - Returns `value` on success (Click callback contract).
    - The callback is attached to each of `--pre`, `--firmware-version`, `--stable` via `callback=_check_install_mutex`. The mutex applies in BOTH install AND `--list` contexts (matches argparse's `add_mutually_exclusive_group()` scope).
    - **Rationale documented inline:** "Per-option callback shape picked over `result_callback` on the command (D-13.4; Claude's Discretion) — locality (the mutex declaration sits next to the options it constrains) + matches argparse's per-action grouping idiom."

    **Step 2.2 — `fw` command:**

    ```
    @cli.command(name="fw")
    @click.option("-i", "--install", is_flag=True, ...)
    @click.option("--pre", is_flag=True, callback=_check_install_mutex, ...)
    @click.option("--firmware-version", type=_FirmwareVersionType(), callback=_check_install_mutex, ...)
    @click.option("--stable", is_flag=True, callback=_check_install_mutex, ...)
    @click.option("--list", "list_releases", is_flag=True, ...)
    @click.option("--json", "json_output", is_flag=True, ...)
    @click.pass_context  # need ctx for _maybe_auto_route_to_pre param-bag adapter
    def fw(ctx, install, pre, firmware_version, stable, list_releases, json_output):
    ```
    Body:
    1. D-14 narrow upgrade: if `json_output and not list_releases`, `raise click.UsageError("--json requires --list")` (preserves exit-2 + "Usage: ..." formatting from `fw_parser.error(...)` at main.py:798).
    2. D-15 SimpleNamespace adapter: `from types import SimpleNamespace; ns = SimpleNamespace(install=install, pre=pre, firmware_version=firmware_version, stable=stable, list=list_releases); _maybe_auto_route_to_pre(ns)`. The helper reads `args.install`, `args.pre`, etc. via `getattr` — works with SimpleNamespace verbatim; zero churn to the helper body. **Rationale documented inline:** "SimpleNamespace adapter picked over explicit-kwarg refactor (D-15; Claude's Discretion) — minimizes churn to `_maybe_auto_route_to_pre` (which stays in main.py for now; Wave 4 relocates it); helper body unchanged."
    3. Pull `app = ctx.obj` (since we used `@click.pass_context` not `@click.pass_obj` to get the ctx).
    4. Dispatch verbatim from main.py:795-847: `list_releases` branch calls `app.firmware_manager.list_releases(json_output=json_output)`; `install` branch calls `app.firmware_manager.install(pre=pre, firmware_version=firmware_version, stable=stable)`; etc. `sys.exit(0 if ok else 1)` per the existing argparse contract.

    Note: the original argparse handler at main.py:795-847 may have multiple `app.firmware_manager.*` call paths depending on the flag combination. Read main.py:795-847 and preserve the dispatch verbatim — the only behaviour changes ARE the framework-mandated ones (UsageError instead of `fw_parser.error`, BadParameter instead of `ArgumentTypeError` via the ParamType).

    **Step 2.3 — `dev` `@cli.group()`:**

    ```
    @cli.group(name="dev")
    def dev():
        """USR button will break command and return."""  # preserve dev_epilog from main.py:372
    ```

    No options on the group itself; sub-commands hang off it via `@dev.command()`.

    **Step 2.4 — `dev read` sub-command:**

    ```
    @dev.command(name="read")
    @click.argument("eprom", shell_complete=_complete_eprom)
    @click.option("-s", "--size", default=None, ...)
    @click.option("-a", "--address", default=None, ...)
    <other options per create_dev_args main.py:382-407, including OE/CE from create_oe_ce_args>
    @click.pass_obj
    def dev_read(app: AppContext, eprom, size, address, ...):
    ```
    Body: `_resolve_or_exit` → call `app.eprom_operator.dev_read_eprom(...)` or whatever main.py:862's dev-read branch dispatches to (preserve verbatim). `sys.exit(0 if ok else 1)`.

    **Step 2.5 — `dev reg` sub-command:**

    ```
    @dev.command(name="reg")
    <register options per main.py:408-432 — observe create_oe_ce_args inclusion>
    @click.pass_obj
    def dev_reg(app, ...):
    ```
    Body: per main.py:862-... dev reg dispatch — preserve verbatim. `sys.exit(0 if ok else 1)`.

    **Step 2.6 — `dev addr` sub-command:**

    ```
    @dev.command(name="addr")
    @click.argument("eprom", shell_complete=_complete_eprom)
    <address options per main.py:434-444, including OE/CE>
    @click.pass_obj
    def dev_addr(app, eprom, ...):
    ```
    Body: `_resolve_or_exit` → preserve main.py dev-addr dispatch verbatim. `sys.exit(0 if ok else 1)`.

    **Step 2.7 — `dev consistency-check` sub-command** (per D-12 step 5):

    ```
    @dev.command(name="consistency-check")
    <options per main.py:446-...>
    @click.pass_obj
    def dev_consistency_check(app, ...):
        ...
        verdict_int = app.eprom_operator.consistency_check_eprom(...)  # 0=PASS, 1=FAIL, 2=hardware-error
        sys.exit(verdict_int)
    ```
    **CRITICAL:** the verdict is `sys.exit(verdict_int)` directly — NOT `sys.exit(0 if verdict else 1)` (the bool-to-int wrap would collapse the 2=hardware-error case to 1=FAIL, breaking the v1.6 RCA diagnostic). Preserves the 3-way contract verbatim from main.py:908-917.

    **Style constraints (apply to all additions in this task):**
    - py39 legacy typing throughout.
    - NO `from __future__ import annotations`.
    - Named imports only.
    - All `help="..."` strings byte-identical to corresponding argparse `help=` text.
    - The 2 dev sub-commands that take `eprom` (`dev read`, `dev addr`) carry `shell_complete=_complete_eprom`.
    - `ruff check` + `ruff format --check` + `mypy firestarter/cli_handlers.py` stay clean.

    After this task, cli_handlers.py contains all 14 top-level Click commands + the `dev` group + its 4 sub-commands. `main.py` still has its argparse dispatcher — entry-point swap is Wave 4.
  </action>
  <verify>
    <automated>cd firestarter_app && python -c "from firestarter.cli_handlers import cli; print(sorted(cli.commands.keys())); print('dev sub:', sorted(cli.commands['dev'].commands.keys())); assert 'fw' in cli.commands and 'dev' in cli.commands and set(cli.commands['dev'].commands.keys()) == {'read', 'reg', 'addr', 'consistency-check'}" && ruff check firestarter/cli_handlers.py && ruff format --check firestarter/cli_handlers.py && mypy firestarter/cli_handlers.py</automated>
  </verify>
  <acceptance_criteria>
    - `grep -cE "^@cli\.command\(" firestarter_app/firestarter/cli_handlers.py` returns exactly 14 (3 W2 + 10 Task1 + 1 fw)
    - `grep -cE "^@cli\.group\(" firestarter_app/firestarter/cli_handlers.py` returns exactly 1 (the dev group; the top-level `cli` is a `@click.group()` not `@cli.group()`)
    - `grep -cE "^@dev\.command\(" firestarter_app/firestarter/cli_handlers.py` returns exactly 4 (dev read/reg/addr/consistency-check)
    - `grep -c "_FirmwareVersionType" firestarter_app/firestarter/cli_handlers.py` returns at least 2 (class definition + use as `type=_FirmwareVersionType()`)
    - `grep -c "click.ParamType" firestarter_app/firestarter/cli_handlers.py` returns at least 1 (the subclass)
    - `grep -c "FIRMWARE_VERSION_RE" firestarter_app/firestarter/cli_handlers.py` returns at least 1
    - `grep -c "from firestarter.firmware import" firestarter_app/firestarter/cli_handlers.py` returns at least 1 (named import of FIRMWARE_VERSION_RE)
    - `grep -c "def _check_install_mutex" firestarter_app/firestarter/cli_handlers.py` returns 1
    - `grep -c "callback=_check_install_mutex" firestarter_app/firestarter/cli_handlers.py` returns exactly 3 (--pre, --firmware-version, --stable)
    - `grep -c "raise click.UsageError" firestarter_app/firestarter/cli_handlers.py` returns at least 1 (the --json requires --list narrow upgrade per D-14)
    - `grep -c "raise click.BadParameter" firestarter_app/firestarter/cli_handlers.py` returns at least 1 (the mutex callback)
    - `grep -c "SimpleNamespace" firestarter_app/firestarter/cli_handlers.py` returns at least 1 (D-15 adapter)
    - `grep -c "_maybe_auto_route_to_pre" firestarter_app/firestarter/cli_handlers.py` returns at least 1 (call site; helper itself stays in main.py until Wave 4)
    - `grep -cE "sys\.exit\(verdict_int\)|sys\.exit\(.*_eprom\(" firestarter_app/firestarter/cli_handlers.py` returns at least 1 (the dev consistency-check 3-way verdict per D-12 step 5; bool-to-int wrap is forbidden — grep below confirms)
    - The dev consistency-check handler does NOT use `sys.exit(0 if ... else 1)` for the verdict: `grep -B2 -A2 "consistency_check_eprom" firestarter_app/firestarter/cli_handlers.py | grep -c "0 if" | head -1` — expect 0 in the consistency-check function's body (other commands MAY still use the bool-to-int form, just not this one)
    - `grep -c "shell_complete=_complete_eprom" firestarter_app/firestarter/cli_handlers.py` returns exactly 9 (info from W2 + 6 chip-ops from Task 1 + 2 dev sub-commands from this task: dev read + dev addr)
    - `grep -c "from __future__ import annotations" firestarter_app/firestarter/cli_handlers.py` returns 0
    - `cd firestarter_app && python -c "from firestarter.cli_handlers import cli; assert 'fw' in cli.commands and 'dev' in cli.commands and set(cli.commands['dev'].commands.keys()) == {'read', 'reg', 'addr', 'consistency-check'}"` exits 0
    - `cd firestarter_app && ruff check firestarter/cli_handlers.py` exits 0
    - `cd firestarter_app && ruff format --check firestarter/cli_handlers.py` exits 0
    - `cd firestarter_app && mypy firestarter/cli_handlers.py` exits 0
    - `firestarter_app/firestarter/main.py` UNCHANGED in this task: `cd firestarter_app && git diff firestarter/main.py` is empty
    - `firestarter_app/pyproject.toml` UNCHANGED in this task
  </acceptance_criteria>
  <done>
    cli_handlers.py contains the complete Click command surface for Phase 41: 14 top-level commands + the `dev` group + 4 dev sub-commands. The `fw` command implements all four argparse→Click traps (#1 exit codes, #3 polarity already in Task 1, #4 3-way mutex via per-option callback, #5 firmware-version validator via custom ParamType). The `dev consistency-check` 3-way verdict (0/1/2) is preserved via `sys.exit(verdict_int)`. The D-14 `UsageError` upgrade lands inline. D-15 SimpleNamespace adapter wires `_maybe_auto_route_to_pre` with zero churn. ruff/format/mypy stay green. main.py + pyproject.toml untouched.
  </done>
</task>

<task type="auto">
  <name>Task 3: Extend tests/test_cli_handlers.py — CliRunner happy-path + error-path coverage for all 11 new commands</name>
  <files>firestarter_app/tests/test_cli_handlers.py</files>
  <read_first>
    - firestarter_app/tests/test_cli_handlers.py (state after W2 — observe the runner fixture style, the test naming convention, the import pattern)
    - firestarter_app/firestarter/cli_handlers.py (state after Task 2 — observe each command's options, arguments, and exit-code shape)
    - firestarter_app/firestarter/main.py (Phase 36 / W1 argparse equivalents — for inferring what each error path should look like; for example, the `info` error path at line 645-668 logs and exits 1 on chip-not-found — preserve that contract on Click handlers)
    - firestarter_app/firestarter/database.py (the `skip_local_override` constructor seam from Phase 36 D-06 — tests construct `EpromDatabase(skip_local_override=True)` for hermetic isolation)
    - firestarter_app/firestarter/eprom_operations.py + hardware.py + firmware.py (Mock targets — tests for commands that would attempt serial I/O (read/write/verify/blank/erase/id/vpp/vpe/hw/config/fw/dev *) MUST use `unittest.mock.patch` or `Mock(spec=...)` to substitute the relevant `AppContext.<manager>` field — otherwise the test hangs trying to open a port)
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-12 step 6: at least one happy-path + one error-path per command; D-13 each TRAP gets a test)
    - .planning/phases/36-characterization-test-baseline/36-CONTEXT.md (D-02 in-process fixture pattern; the test naming convention; D-06 skip_local_override seam)
  </read_first>
  <action>
    Extend `firestarter_app/tests/test_cli_handlers.py` with at least 22 new tests (1 happy-path + 1 error-path per each of 11 new commands; more if the planner sees TRAP-specific coverage gaps). Group by command in the file for readability; preserve W2's test ordering at the top.

    **Test fixture pattern (module-level):**

    Add a `make_app_context(monkeypatch=None, **manager_overrides)` helper that constructs a real `AppContext` with `EpromDatabase(skip_local_override=True)` for the db field + `Mock(spec=EpromOperator)` / `Mock(spec=HardwareManager)` / `Mock(spec=FirmwareManager)` for the manager fields by default (so no test attempts serial I/O). The `manager_overrides` kwarg lets a test substitute a specific manager with a configured mock (e.g. `eprom_operator=mock_with_read_returning_true`).

    Tests then use the Click `runner.invoke(cli, [...], obj=app)` pattern (passing `obj=` skips the group body's manager construction — tests get a fully-mocked AppContext).

    **Required tests (≥22 total; planner may add more for TRAP coverage):**

    For each of the 11 new commands, add:
    - `test_<command>_happy_path` — mock the relevant manager method to return success; invoke; assert `exit_code == 0` + any expected output snippet.
    - `test_<command>_error_path` — mock the relevant manager method to raise / return False / etc.; invoke; assert `exit_code != 0` (typically 1 for chip-op failure; 2 for usage error on the fw mutex tests).

    **Specific TRAP-coverage tests (D-13):**
    - `test_write_no_blank_check_polarity` — invoke `["write", "W27C512", "out.bin", "--no-blank-check"]` with a mocked `eprom_operator.write_eprom` and assert `blank_check=False` was passed in the call kwargs; invoke `["write", "W27C512", "out.bin"]` (no flag) and assert `blank_check=True` was passed. (TRAP #3 / D-13.3)
    - `test_fw_mutex_pre_and_firmware_version` — invoke `["fw", "--install", "--pre", "--firmware-version", "3.0.0b6"]` and assert `exit_code == 2` + error output mentions "mutually exclusive". (TRAP #4 / D-13.4)
    - `test_fw_mutex_stable_and_pre` — invoke `["fw", "--install", "--stable", "--pre"]` and assert `exit_code == 2`. (TRAP #4 / D-13.4 — full coverage of all 3 pairings)
    - `test_fw_mutex_firmware_version_and_stable` — invoke `["fw", "--install", "--firmware-version", "3.0.0", "--stable"]` and assert `exit_code == 2`. (TRAP #4 / D-13.4)
    - `test_fw_invalid_firmware_version` — invoke `["fw", "--install", "--firmware-version", "not-a-version"]` and assert `exit_code == 2` + the ParamType error message. (TRAP #5 / D-13.5)
    - `test_fw_json_requires_list` — invoke `["fw", "--json"]` (no --list) and assert `exit_code == 2` + output contains "--json requires --list". (D-14 narrow UsageError upgrade)
    - `test_fw_list_with_json` — invoke `["fw", "--list", "--json"]` with mocked firmware_manager.list_releases; assert `exit_code == 0` (this is the legitimate combination).
    - `test_dev_consistency_check_pass_verdict` — mock `eprom_operator.consistency_check_eprom` to return 0; assert `exit_code == 0`.
    - `test_dev_consistency_check_fail_verdict` — mock to return 1; assert `exit_code == 1`.
    - `test_dev_consistency_check_hardware_error_verdict` — mock to return 2; assert `exit_code == 2`. (CRITICAL — proves the 3-way contract per D-12 step 5; if the handler bool-to-int-wrapped, this test would see `exit_code == 1` and FAIL)

    **Error-path examples (one per chip-op command):**
    - `test_read_chip_not_found` — invoke `["read", "NOPE_NOT_A_CHIP", "out.bin"]` with the real EpromDatabase(skip_local_override=True); assert `exit_code == 1` (via `_resolve_or_exit` → log + None → sys.exit(1)).
    - `test_write_operator_returns_false` — mock `eprom_operator.write_eprom` to return False; invoke `["write", "W27C512", "out.bin"]`; assert `exit_code == 1`.
    - Similar for verify/blank/erase/id/vpp/vpe/hw/config/fw/dev_read/dev_reg/dev_addr.

    **Style constraints:**
    - py39 legacy typing.
    - `runner.invoke(cli, [...], obj=app)` — pass `obj=` to bypass the group body's real manager construction.
    - Use `unittest.mock.Mock(spec=...)` to keep the mock surface tight (signature-matched to the real manager).
    - Test function names follow `test_<command>_<scenario>` convention.
    - `ruff check` + `ruff format --check` stay clean; `mypy firestarter/` stays clean (test file itself is not under mypy strict per Phase 37 D-08).

    Run the suite after writing the tests; ensure every new test passes. If a mock returns the wrong shape causing a test to fail, the test is wrong (or the mock spec needs tightening) — DO NOT modify cli_handlers.py to make a test pass; the handlers were authored against main.py's verbatim behaviour in Tasks 1 + 2.
  </action>
  <verify>
    <automated>cd firestarter_app && pytest tests/test_cli_handlers.py -v</automated>
  </verify>
  <acceptance_criteria>
    - `grep -cE "^def test_" firestarter_app/tests/test_cli_handlers.py` returns at least 28 (W2 floor of ≥6 + ≥22 new = ≥28)
    - `grep -c "runner.invoke(cli" firestarter_app/tests/test_cli_handlers.py` returns at least 28
    - `grep -c "make_app_context" firestarter_app/tests/test_cli_handlers.py` returns at least 1 (helper defined; used by most tests)
    - `grep -c "skip_local_override=True" firestarter_app/tests/test_cli_handlers.py` returns at least 1 (Phase 36 D-06 seam consumed)
    - `grep -c "Mock(spec=" firestarter_app/tests/test_cli_handlers.py` returns at least 3 (EpromOperator/HardwareManager/FirmwareManager — at minimum)
    - `grep -c "no_blank_check_polarity\|blank_check=False\|blank_check=True" firestarter_app/tests/test_cli_handlers.py` returns at least 1 (TRAP #3 covered)
    - `grep -c "mutually exclusive\|mutex" firestarter_app/tests/test_cli_handlers.py` returns at least 3 (TRAP #4 — 3 pairing tests minimum)
    - `grep -c "fw_invalid_firmware_version\|Invalid firmware version" firestarter_app/tests/test_cli_handlers.py` returns at least 1 (TRAP #5)
    - `grep -c "json_requires_list\|--json requires --list" firestarter_app/tests/test_cli_handlers.py` returns at least 1 (D-14)
    - `grep -c "consistency_check.*verdict\|verdict_int\|consistency-check" firestarter_app/tests/test_cli_handlers.py` returns at least 3 (PASS/FAIL/hardware-error tests — D-12 step 5 3-way contract)
    - `cd firestarter_app && pytest tests/test_cli_handlers.py -v` exits 0 (all new tests passing)
    - `cd firestarter_app && ruff check tests/test_cli_handlers.py` exits 0
    - `cd firestarter_app && ruff format --check tests/test_cli_handlers.py` exits 0
    - `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (Phase 36 subprocess goldens unchanged this wave — argparse path untouched per D-12)
  </acceptance_criteria>
  <done>
    test_cli_handlers.py contains ≥28 CliRunner tests total (W2's ≥6 + ≥22 new). Every new Click command has a happy-path + an error-path. All 4 TRAPs are covered by named tests (#1 exit codes implicitly via every test's exit_code assertion; #3 polarity; #4 3-way mutex; #5 ParamType + #14 UsageError). The `dev consistency-check` 3-way verdict (0/1/2) is pinned by 3 separate tests proving the handler does NOT bool-to-int-wrap. All tests pass; ruff/format clean.
  </done>
</task>

<task type="auto">
  <name>Task 4: Verify full gate + Phase 36 goldens unchanged; commit Wave 3 as a single atomic commit</name>
  <files>firestarter_app/firestarter/cli_handlers.py, firestarter_app/tests/test_cli_handlers.py</files>
  <read_first>
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-12 step 6 + "Claude's Discretion" line on sub-commit count — planner picks ONE atomic commit per the v1.8 phase style)
    - firestarter_app/tests/test_characterization.py (Phase 36 subprocess goldens — must stay green; argparse path untouched this wave)
    - .planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md (CI gate the local run mirrors)
    - .planning/phases/40-serial-transport-restructure/40-CONTEXT.md (D-08 documented commit-message convention — `<scope>(<phase>-<plan>): <subject>` + body explaining rationale)
  </read_first>
  <action>
    Run the full firestarter_app gate locally to confirm Wave 3 has not regressed anything:
    1. `cd firestarter_app && ruff check . && ruff format --check . && mypy firestarter/` — must exit 0.
    2. `cd firestarter_app && pytest -v` — Wave 1+2 floor + Task 3's ≥22 new tests; expect (163 + W2 new + 22) passed + 1 xfail (BUG-2 stays xfail-strict per Phase 41 <deferred>) + 29 snapshots green.
    3. `cd firestarter_app && pytest tests/test_characterization.py -v` — Phase 36 subprocess goldens MUST stay green (argparse entry point untouched this wave per D-12). Any drift here is a regression to fix in-wave, NOT a snapshot update.
    4. `cd firestarter_app && pytest tests/test_bug_characterization.py -v` — BUG-1 passes (flipped in W1); BUG-2 stays xfail-strict (Phase 42 ERR-01 territory).

    Then commit BOTH files in a single atomic commit on the firestarter_app/ submodule's `v1.8-app-cleanup` branch (per the v1.8 phase-style chosen in must_haves.truths — Wave 3 ships as ONE commit). Suggested commit message (HEREDOC):

    Subject: `feat(41-03): migrate 11 commands (chip-ops + voltage + hw + fw + dev) to Click (CLI-01, CLI-02)`

    Body:
    ```
    Wave 3 of Phase 41. Extends firestarter/cli_handlers.py with the remaining 11
    commands — 6 chip-ops (read/write/verify/blank/erase/id), 2 voltage (vpp/vpe),
    2 hardware (hw/config), 1 firmware (fw), and the dev @cli.group() with 4
    sub-commands (read/reg/addr/consistency-check). Adds CliRunner happy-path +
    error-path tests for each in tests/test_cli_handlers.py (≥22 new tests).

    Addresses argparse→Click TRAPs per D-13:
    - #1 exit codes: sys.exit(0 if op() else 1) per handler; UsageError/BadParameter
      for exit-2 paths.
    - #3 --no-blank-check polarity: write uses is_flag=True flag_value=False
      default=True (mirrors argparse store_false default=True); erase keeps inverse
      --blank-check store_true default=False; both polarities coexist.
    - #4 --pre/--firmware-version/--stable 3-way mutex: per-option callback
      _check_install_mutex raises click.BadParameter (exit-2).
    - #5 _validate_firmware_version: re-wired as custom Click ParamType subclass
      (_FirmwareVersionType) — reusable, Click-canonical; preserves FIRMWARE_VERSION_RE
      import from firestarter.firmware unchanged.

    Narrow D-14 upgrade: fw_parser.error("--json requires --list") becomes
    raise click.UsageError(...) inline in the fw handler body — exit-2 + "Usage:"
    formatting preserved.

    D-15 _maybe_auto_route_to_pre adapter: SimpleNamespace(**locals())-equivalent
    built in the fw handler body; helper itself stays in main.py until Wave 4 / Plan
    41-04.

    dev consistency-check preserves the 3-way verdict contract (0=PASS, 1=FAIL,
    2=hardware-error) via sys.exit(verdict_int) directly — NOT bool-to-int wrap.
    Pinned by 3 separate tests (D-12 step 5).

    Entry point in main.py STAYS argparse this wave. cli_handlers.py is now feature-
    complete reviewable dead code awaiting the Wave 4 / Plan 41-04 entry-point swap.
    Phase 36 subprocess goldens remain green (argparse path unchanged).

    No INTENTIONAL BEHAVIOR CHANGE flag — Wave 3 is pure refactor + framework-
    mandated mechanical differences (Click ergonomics on usage errors are formatting-
    only, not exit-code-changing). The argcomplete drop INTENTIONAL BEHAVIOR CHANGE
    lands in Wave 4 / Plan 41-04.
    ```

    Do NOT amend prior commits. Worktrees off per `project_v18_phase_execution_mechanics`; the executor runs sequentially.
  </action>
  <verify>
    <automated>cd firestarter_app && ruff check . && ruff format --check . && mypy firestarter/ && pytest -v 2>&1 | tail -5 && pytest tests/test_characterization.py -v 2>&1 | tail -5 && pytest tests/test_bug_characterization.py -v 2>&1 | tail -5</automated>
  </verify>
  <acceptance_criteria>
    - `cd firestarter_app && ruff check .` exits 0
    - `cd firestarter_app && ruff format --check .` exits 0
    - `cd firestarter_app && mypy firestarter/` exits 0 (no new errors vs. Phase 37 watermark)
    - `cd firestarter_app && pytest -v` exits 0; output contains "passed" and exactly 1 xfail (BUG-2 — BUG-1 already flipped in W1; BUG-2 stays through Phase 41)
    - `cd firestarter_app && pytest tests/test_cli_handlers.py -v` exits 0 (all new tests passing)
    - `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (Phase 36 subprocess goldens green — argparse path unchanged per D-12)
    - `cd firestarter_app && pytest tests/test_bug_characterization.py -v` exits 0 (BUG-1 PASSED; BUG-2 XFAIL)
    - `cd firestarter_app && git log -1 --name-only` lists exactly `firestarter/cli_handlers.py` and `tests/test_cli_handlers.py` (no other files touched — Wave 3 ships as one commit)
    - `firestarter_app/firestarter/main.py` byte-identical to its state at end of W2: `cd firestarter_app && git diff HEAD~1 -- firestarter/main.py` is empty
    - `firestarter_app/pyproject.toml` byte-identical to its state at end of W2: `cd firestarter_app && git diff HEAD~1 -- pyproject.toml` is empty
    - `firestarter_app/autocomplete.md` UNCHANGED (Wave 4 territory)
    - `firestarter_app/.github/workflows/ci.yml` UNCHANGED (Wave 4 territory)
    - The commit lands on branch `v1.8-app-cleanup`: `cd firestarter_app && git rev-parse --abbrev-ref HEAD` returns `v1.8-app-cleanup`
    - Commit message body does NOT contain "INTENTIONAL BEHAVIOR CHANGE" (Wave 3 is pure refactor; the Wave 4 commit owns the argcomplete drop flag)
  </acceptance_criteria>
  <done>
    Single atomic commit on firestarter_app `v1.8-app-cleanup` branch lands the full 11-command Click migration in cli_handlers.py + the matching ≥22 CliRunner tests in test_cli_handlers.py. Full lint/type/test gate is green. Phase 36 subprocess goldens unaffected. main.py + pyproject.toml + autocomplete.md + CI workflow all byte-identical to their W2 state — Wave 3 stays in cli_handlers.py + its test file. Wave 4 / Plan 41-04 can now execute the user-visible entry-point swap.
  </done>
</task>

</tasks>

<verification>
- `cd firestarter_app && ruff check . && ruff format --check . && mypy firestarter/` exits 0
- `cd firestarter_app && pytest -v` exits 0 with BUG-1 PASSED + BUG-2 XFAIL + W3 ≥22 new tests passing
- `cd firestarter_app && pytest tests/test_cli_handlers.py -v` exits 0 (≥28 tests total)
- `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (Phase 36 goldens unchanged)
- `cd firestarter_app && pytest tests/test_bug_characterization.py -v` exits 0 (BUG-1 passing, BUG-2 xfail strict)
- `cd firestarter_app && python -c "from firestarter.cli_handlers import cli; assert len(cli.commands) == 14 and 'dev' in cli.commands and len(cli.commands['dev'].commands) == 4"` exits 0
- All 4 argparse→Click TRAPs (#1, #3, #4, #5) covered by named tests in test_cli_handlers.py (TRAP #2 covered by W2's no-prefix-matching test)
- `firestarter_app/firestarter/main.py` and `firestarter_app/pyproject.toml` and `firestarter_app/autocomplete.md` and `firestarter_app/.github/workflows/ci.yml` ALL byte-identical to their W2 state
</verification>

<success_criteria>
14/14 user-facing commands implemented as Click `@cli.command()`s + `@cli.group()` in `cli_handlers.py`; the argparse→Click TRAPs (#1 exit codes, #3 `--no-blank-check` polarity, #4 3-way mutex, #5 firmware-version validator) are each handled per their D-13 locks; the `dev consistency-check` 3-way verdict (0/1/2) is preserved verbatim; CliRunner happy-path + error-path tests cover every new command. Entry point stays argparse; cli_handlers.py is feature-complete reviewable dead code awaiting Wave 4 / Plan 41-04. Closes the bulk of CLI-01 (all 4 TRAPs addressed in code) + CLI-02 (cli_handlers.py grows to its final command set, though main.py dispatch still alive).
</success_criteria>

<output>
Create `.planning/phases/41-cli-migration-argparse-click/41-03-SUMMARY.md` when done.
</output>

---
phase: 42-error-handling-normalization-quality-sweep
plan: 02
type: execute
wave: 2
depends_on: ["01"]
files_modified:
  - firestarter_app/firestarter/cli_handlers.py
autonomous: true
requirements:
  - ERR-01
must_haves:
  truths:
    - "GATE-1.8a: wire protocol byte-identical — this plan touches only cli_handlers.py; no serial/wire/firmware code edited"
    - "GATE-1.8b: end-user CLI surface preserved — exit codes 0/1/2 ONLY (per D-04, no new exit code; ChipNotFoundError/SerialError/SerialTimeoutError/FirmwareOutdatedError/EpromOperationError/HardwareOperationError all still exit 1 via click.ClickException); all 29 syrupy CLI snapshots stay green; test_cli_handlers.py exit_code assertions (~30 sites with == 0 / == 1) stay green"
    - "GATE-1.8c: constants.py + firmware header parity untouched (no edit to constants.py; existing named imports preserved per Phase 39 D-06)"
    - "GATE-1.8d: read path ring-fence — no edits to eprom_operations.py (its body is byte-identical relative to Plan 42-01's BUG-2-fix tip); no edits to serial_comm.py or _read_and_parse_lines"
    - "GATE-1.8e: full suite green + pip install -e . && firestarter --help smoke remains green"
    - "D-03 honored: a single @map_typed_errors decorator near top of cli_handlers.py catches ChipNotFoundError, FirmwareOutdatedError, SerialError, SerialTimeoutError, EpromOperationError, HardwareOperationError; each re-raises click.ClickException with a stable prefix → exit 1"
    - "D-05 honored: _resolve_or_exit is DELETED; all 9 chip-op handlers + dev sub-commands replace `eprom_data = _resolve_or_exit(eprom, app.db); if not eprom_data: sys.exit(1)` with `eprom_data = resolve_chip(eprom, db=app.db)` and let the decorator catch ChipNotFoundError"
    - "Decorator stacking order: @map_typed_errors sits OUTSIDE @click.pass_obj / @click.pass_context — handlers reachable via Click's command-decorator chain still receive their AppContext kwarg unchanged"
    - "D-04 deviation honored: NO new exit code carved out for EpromOperationError; it stays at exit 1 (ClickException default)"
    - "dev consistency-check 3-way verdict contract (0=PASS, 1=FAIL, 2=hardware-error) preserved — verdict_int flows through sys.exit(verdict_int) UNCHANGED; the decorator does NOT collapse this because consistency_check_eprom returns int and does not raise the mapped exceptions on its happy path (the decorator's except clauses are only triggered if an exception escapes the body)"
    - "Phase 41 D-08 seed honored: the _resolve_or_exit shim was 'the deliberate seam' between Phase 41's logging contract and Phase 42's exception-mapping contract; this plan removes the shim cleanly per the load-bearing handoff"
    - "no-touch invariant: eprom_operations.py (post-W1 tip), main.py, pyproject.toml, ci.yml, serial_comm.py, hardware.py, firmware.py, database.py, chip_resolver.py, eprom_info.py, config.py, exceptions.py, address_parser.py, constants.py, codec.py, frame_parser.py, logging_utils.py, data/chip_database.json, data/pinouts.json, tests/__snapshots__/, the firmware sub-repo — none touched in this plan"
  artifacts:
    - path: "firestarter_app/firestarter/cli_handlers.py"
      provides: "map_typed_errors decorator (single Click-boundary mapping layer) + 19 callbacks decorated with it (14 top-level + 1 dev group + 4 dev sub-commands) + 9 chip-op handlers calling resolve_chip() directly"
      contains: "def map_typed_errors("
      exports: ["map_typed_errors", "cli", "AppContext"]
  key_links:
    - from: "firestarter_app/firestarter/cli_handlers.py::map_typed_errors"
      to: "firestarter_app/firestarter/exceptions.py"
      via: "named import of ChipNotFoundError, SerialError, SerialTimeoutError, FirmwareOutdatedError, EpromOperationError, HardwareOperationError"
      pattern: "from firestarter.exceptions import"
    - from: "firestarter_app/firestarter/cli_handlers.py::read|write|verify|blank|erase|chip_id|dev_read|dev_addr|dev_consistency_check"
      to: "firestarter_app/firestarter/chip_resolver.py::resolve_chip"
      via: "direct call (not via _resolve_or_exit shim); decorator catches ChipNotFoundError"
      pattern: "resolve_chip\\(.+db=app\\.db\\)"
---

<objective>
Wave 2 / Plan 42-02 — Centralize typed-exception → ClickException mapping at the Click boundary per D-03 and remove the `_resolve_or_exit` shim per D-05. Add a new `map_typed_errors` decorator near the top of `firestarter_app/firestarter/cli_handlers.py` (placed inside `cli_handlers.py` per Claude's Discretion in CONTEXT.md — a separate `cli_errors.py` is overengineering for one ~25-line decorator). Apply `@map_typed_errors` to every `@cli.command()` / `@cli.group()` / `@dev.command()` callback in the file (14 top-level + 1 dev group + 4 dev sub-commands = 19 callbacks). Delete the `_resolve_or_exit` helper at lines 98-113. Replace the 9 chip-op call sites of `_resolve_or_exit` with direct `resolve_chip(eprom, db=app.db)` calls, deleting the `if not eprom_data: sys.exit(1)` follow-up block at each site (the decorator now handles ChipNotFoundError → ClickException → exit 1 uniformly).

Per D-04, all caught exceptions map to `click.ClickException` which prints to stderr and exits 1 by default — matching today's behavior for these error types. No exit-code semantics change; Phase 36 syrupy snapshots stay green; Phase 41 `test_cli_handlers.py` exit_code assertions (~30 sites) stay green. The `dev consistency-check` 3-way verdict (0/1/2) is preserved by `sys.exit(verdict_int)` — the decorator does NOT collapse it because `consistency_check_eprom` returns int rather than raising the mapped exceptions on its happy path; if a mapped exception DOES escape `consistency_check_eprom` (e.g. SerialError during the read sequence), it maps to exit 1 just like every other handler — that's the consistent behavior, NOT a regression of the 3-way verdict (the 3-way verdict applies only when the operation completes and returns its verdict integer).

Purpose: Close the decorator portion of ERR-01 — give Phase 42 a single grep-able mapping point so future exception types added to `exceptions.py` add one `except` clause here, not 18 try/except blocks scattered across the handlers. This is the long-term ergonomic win the ERR-01 SC#1 implies but doesn't spell out.
Output: One atomic commit on the `firestarter_app/` submodule's `v1.8-app-cleanup` branch modifying only `cli_handlers.py`.
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
@.planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md
@.planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md
@.planning/phases/38-low-risk-extractions/38-CONTEXT.md
@firestarter_app/CLAUDE.md
@firestarter_app/firestarter/cli_handlers.py
@firestarter_app/firestarter/chip_resolver.py
@firestarter_app/firestarter/exceptions.py
@firestarter_app/tests/test_cli_handlers.py
</context>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| CLI args → handler | Existing trust boundary unchanged; Click's UsageError/BadParameter (exit 2) handling stays Click's responsibility — the decorator does NOT intercept those |
| handler → service layer | Existing service-layer exception types (defined in exceptions.py) flow through the decorator; no new exception types introduced |
| service exception → user stderr | click.ClickException prints `Error: {message}` to stderr — same shape as today's `logger.error(...); sys.exit(1)` from the perspective of GATE-1.8b's exit-code contract; the format text differs slightly but is NOT pinned by Phase 36's subprocess goldens (they only pin the in-process error paths Click handles directly) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-42-03 | Information Disclosure | click.ClickException(str(e)) | accept | Exception messages may surface chip names / file paths / port names via str(e) — already true today via `logger.error(...)`; not a new exposure (D-03 mirrors the existing logging pattern's information surface) |
| T-42-04 | Denial of Service | decorator stacking error | mitigate | Smoke-test decorator stacking after the first 1-2 handlers are decorated (per CONTEXT Integration Points note) before applying to all 19 callbacks; if the decorator order breaks `@click.pass_obj` kwarg injection, the test_cli_handlers.py suite catches it immediately (~30 exit_code assertions exercise the AppContext injection on every command) |
| T-42-05 | Tampering | wire protocol byte stream | accept | No new attack surface; cli_handlers.py is the host-side CLI parser, not a wire-format participant |

Severity: informational only. `block_on: high` not triggered.
</threat_model>

<tasks>

<task type="auto">
  <name>Task 1: Add map_typed_errors decorator near top of cli_handlers.py</name>
  <files>firestarter_app/firestarter/cli_handlers.py</files>
  <read_first>
    - firestarter_app/firestarter/cli_handlers.py (current state — lines 1-100 cover the module docstring + imports + _setup_logging + AppContext dataclass + _complete_eprom; the decorator lands AFTER _complete_eprom and BEFORE _resolve_or_exit at line 98, so the existing helpers above the chip-op handlers are unaffected)
    - firestarter_app/firestarter/exceptions.py (verify the named-import list: ChipNotFoundError, SerialError, SerialTimeoutError, FirmwareOutdatedError, EpromOperationError, HardwareOperationError — all already exist; FirmwareOperationError + ProgrammerNotFoundError also exist but ProgrammerNotFoundError is a SerialError subclass and FirmwareOperationError is a plain Exception — the planner's call on whether to map FirmwareOperationError separately or fold into the existing tuple)
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md (D-03 supplies the exact decorator code shape verbatim; D-04 locks the exit-code policy at 1; "Claude's Discretion" supports keeping the decorator in cli_handlers.py rather than a separate cli_errors.py file)
    - .planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md (D-08 py39 legacy typing — Callable[..., Any] is the strict-mode signature for the decorator)
  </read_first>
  <action>
    In `firestarter_app/firestarter/cli_handlers.py`, make two coordinated edits:

    1. **Extend the existing exceptions import.** The current state imports only `ChipNotFoundError` at line 33: `from firestarter.exceptions import ChipNotFoundError`. Replace with a named-import list covering every typed exception the decorator catches:
       - Imports: `ChipNotFoundError`, `EpromOperationError`, `FirmwareOutdatedError`, `HardwareOperationError`, `SerialError`, `SerialTimeoutError`
       - One named-import line (sorted alphabetically per ruff `I` rule); MUST stay ≤ 88 chars or include `# noqa: E501` per Phase 37 D-08; the planner picks the wrap shape ruff-format produces
       - Do NOT import `FirmwareOperationError` or `ProgrammerNotFoundError`: `ProgrammerNotFoundError` is a `SerialError` subclass (already caught via the SerialError clause); `FirmwareOperationError` is currently NOT raised by any code path reaching the Click boundary (scout: no callers in cli_handlers.py reach it directly), and adding it to the decorator would be a speculative pre-fold per the v1.8 "minimum diff" pattern. If the planner finds `FirmwareOperationError` surfaces from `app.firmware_manager.manage_firmware_update(...)` during the smoke run (Task 4), add a parallel `except FirmwareOperationError as e:` clause mapping to `"Firmware error: {e}"` — but only if a test fails without it.

    2. **Add the `map_typed_errors` decorator.** Insert a new module-level function near the top of the file, AFTER `_complete_eprom` (currently ends at line 95) and BEFORE the existing `_resolve_or_exit` definition (currently line 98). The decorator MUST:
       - Be named exactly `map_typed_errors`
       - Have signature `def map_typed_errors(f: Callable[..., Any]) -> Callable[..., Any]:` (Phase 37 D-08 legacy typing; `Callable` from `typing`; add `Callable, Any` to the existing `from typing import List, Optional  # noqa: UP035` line; both `List` and `Optional` stay)
       - Wrap the inner function with `@functools.wraps(f)` to preserve the wrapped function's `__name__` / `__doc__` (Click reads `__doc__` for `--help`; broken wrap would invalidate the 29 syrupy snapshots — REGRESSION)
       - Catch in this order (most specific first, matching D-03 code block):
         a. `except ChipNotFoundError as e:` → `raise click.ClickException(str(e)) from e`
         b. `except FirmwareOutdatedError as e:` → `raise click.ClickException(f"Firmware outdated: {e}") from e`
         c. `except (SerialError, SerialTimeoutError) as e:` → `raise click.ClickException(f"Communication error: {e}") from e`
         d. `except EpromOperationError as e:` → `raise click.ClickException(f"Programmer error: {e}") from e`
         e. `except HardwareOperationError as e:` → `raise click.ClickException(f"Hardware error: {e}") from e`
       - Include `import functools` at the top of the file if not already present (scout: not currently imported — add it after the `import logging` line)
       - The inner `wrapper` MUST take `*args, **kwargs` and `return f(*args, **kwargs)` from inside a `try:` block (mirror the D-03 code block verbatim except for any planner-chosen formatting; the body MUST be `return f(*args, **kwargs)` so the wrapped function's return value passes through cleanly — important for the `dev consistency-check` verdict-int return path which calls `sys.exit(verdict_int)` from inside the wrapped function body)
       - The decorator docstring is a single line: `"""Map service-layer typed exceptions to ClickException + stable exit codes (D-03)."""`

    Notes on ordering:
    - The `except (SerialError, SerialTimeoutError)` tuple comes BEFORE the `except EpromOperationError` line, mirroring the eprom_operations.py Plan 42-01 split order
    - `ProgrammerNotFoundError` does not need a dedicated clause; it is a SerialError subclass and falls through to the SerialError tuple
    - `ChipNotFoundError` comes first because it is the most-frequent typed exception (raised by `resolve_chip()` called from 9 sites)

    DO NOT:
    - Apply the decorator to any handler yet (that's Task 2 — keep the diff minimal per task)
    - Touch `_resolve_or_exit` yet (that's Task 3 — keep the diff minimal per task)
    - Add `# type: ignore` comments — Phase 37 D-10 mypy convention is "fix it, don't ignore it"; the Callable[..., Any] signature is strict-clean
    - Create a separate `cli_errors.py` file (Claude's Discretion lock — keep flat layout per PROJECT.md)
  </action>
  <verify>
    <automated>cd firestarter_app && python -c "from firestarter.cli_handlers import map_typed_errors; print(map_typed_errors.__doc__)"</automated>
  </verify>
  <acceptance_criteria>
    - `cd firestarter_app && grep -c "^def map_typed_errors(" firestarter/cli_handlers.py` returns exactly 1
    - `cd firestarter_app && grep -c "@functools.wraps(f)" firestarter/cli_handlers.py` returns at least 1 (the new decorator's inner wrapper)
    - `cd firestarter_app && grep -c "^import functools" firestarter/cli_handlers.py` returns exactly 1
    - `cd firestarter_app && grep -cE "from firestarter.exceptions import.*ChipNotFoundError" firestarter/cli_handlers.py` returns exactly 1
    - `cd firestarter_app && grep -cE "from firestarter.exceptions import.*(SerialError|SerialTimeoutError|FirmwareOutdatedError|EpromOperationError|HardwareOperationError)" firestarter/cli_handlers.py` returns at least 1 (all 5 additional names appear in the same import line or a wrapped continuation)
    - `cd firestarter_app && grep -c "except ChipNotFoundError as e:" firestarter/cli_handlers.py` returns at least 1 (the new decorator body; may rise to 2 after Task 3 if any other except clause survives — but Task 3 deletes _resolve_or_exit which also catches ChipNotFoundError, so the final count after all tasks is exactly 1)
    - `cd firestarter_app && grep -c "except (SerialError, SerialTimeoutError) as e:" firestarter/cli_handlers.py` returns at least 1
    - `cd firestarter_app && grep -c "except EpromOperationError as e:" firestarter/cli_handlers.py` returns at least 1
    - `cd firestarter_app && grep -c "except HardwareOperationError as e:" firestarter/cli_handlers.py` returns at least 1
    - `cd firestarter_app && grep -c "raise click.ClickException(" firestarter/cli_handlers.py` returns at least 5 (one per mapped exception clause)
    - `cd firestarter_app && python -c "from firestarter.cli_handlers import map_typed_errors; assert callable(map_typed_errors)"` exits 0
    - `cd firestarter_app && ruff check firestarter/cli_handlers.py` exits 0 (no new violations)
    - `cd firestarter_app && ruff format --check firestarter/cli_handlers.py` exits 0
    - `cd firestarter_app && pytest tests/test_cli_handlers.py -v` exits 0 (the decorator is defined but not yet APPLIED; existing tests stay green — Task 2 will apply it)
  </acceptance_criteria>
  <done>
    `cli_handlers.py` exports a new `map_typed_errors` decorator catching 5 exception clauses (ChipNotFoundError, FirmwareOutdatedError, SerialError|SerialTimeoutError tuple, EpromOperationError, HardwareOperationError) and re-raising click.ClickException with stable prefixes; the decorator is defined but not yet applied; the file imports `functools` and the full exception name list; ruff/format gate clean; existing tests stay green.
  </done>
</task>

<task type="auto">
  <name>Task 2: Apply @map_typed_errors to all 19 callbacks; verify decorator stacking order</name>
  <files>firestarter_app/firestarter/cli_handlers.py</files>
  <read_first>
    - firestarter_app/firestarter/cli_handlers.py (current state — observe each callback's decorator stack; the typical shape is `@cli.command(name=...) / @click.argument(...) / @click.option(...) / @click.pass_obj` immediately above `def <handler>(app: AppContext, ...) -> None:`. The `dev` group itself uses just `@cli.group(name="dev")`. Some `fw` handler uses `@click.pass_context` instead of `@click.pass_obj`. The `cli` group at line 258 uses `@click.pass_context`.)
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md (CONTEXT.md "Integration Points" — `map_typed_errors` must wrap the handler function BEFORE Click's command-decorator chain; equivalent: `@map_typed_errors` sits BETWEEN `@cli.command(...)` / `@click.option(...)` / `@click.argument(...)` block and `@click.pass_obj` (or `@click.pass_context`). Concretely: `@map_typed_errors` is the LAST decorator above `def <handler>(...)` — i.e. closest to the function definition. Stacking order matters because Click's chain expects the decorated function to be a Click-callable; if `@map_typed_errors` sits ABOVE Click's `@cli.command`, the click-callable becomes the wrapper, which Click's internal introspection (`callback`, `params`, etc.) cannot read.)
    - firestarter_app/tests/test_cli_handlers.py (~30 exit_code == 0 / == 1 assertions — Task 2 must keep these green after applying the decorator)
  </read_first>
  <action>
    Apply `@map_typed_errors` to every callback in `cli_handlers.py` that produces user-visible CLI output (the Click-command callbacks; NOT the helper functions). Per CONTEXT Integration Points, the decorator MUST be the INNERMOST one — i.e., the decorator listed CLOSEST to the `def <handler>(...)` line. Stack order (top-to-bottom):

      @cli.command(name=...)         ← OUTERMOST (Click decorator)
      @click.argument(...)
      @click.option(...)
      @click.pass_obj                ← Click's parameter-injection layer
      @map_typed_errors              ← INNERMOST (just above def line)
      def handler(...) -> None:

    For `@click.pass_context` handlers (the top-level `cli` group at line 268 + the `fw` handler at line 763) the stacking is identical — `@map_typed_errors` immediately precedes the `def` line.

    Apply to these 19 callbacks (verified by `grep -nE "^@(cli|dev)\.(command|group)\(" firestarter/cli_handlers.py` against the current file):

    1. `cli` (group) — line ~268
    2. `_list_cmd` (list) — line ~300
    3. `info` — line ~314
    4. `search` — line ~346
    5. `read` — line ~371
    6. `write` — line ~415
    7. `verify` — line ~458
    8. `blank` — line ~488
    9. `erase` — line ~524
    10. `chip_id` (id) — line ~558
    11. `vpp` — line ~599
    12. `vpe` — line ~610
    13. `hw` — line ~625
    14. `config` — line ~655
    15. `fw` — line ~763
    16. `dev` (group) — line ~870
    17. `dev_read` — line ~888
    18. `dev_reg` — line ~950
    19. `dev_addr` — line ~988
    20. `dev_consistency_check` — line ~1046

    (That's 20 callbacks total when the `cli` group itself is included — CONTEXT D-09 cited "18" excluding both `cli` and `dev` groups; the operator's intent in CONTEXT D-03 is "every @cli.command() and @cli.group() callback" — apply to all 20 to maintain decoration uniformity. Decorating the two group-body callbacks is harmless: the group bodies only run setup code and would simply pass any typed exception through to the parent invocation chain — but CliRunner tests have the AppContext shortcut pattern at lines 277-278 which `return`s early and never raises typed exceptions, so the wrapped path is a no-op in tests. Production code in the `cli` group body could in principle raise SerialError from `EpromDatabase()`'s pin-conversion path — the decorator catches it gracefully.)

    For the `dev_consistency_check` callback specifically: the 3-way verdict (0/1/2) is preserved verbatim because the callback's body calls `sys.exit(verdict_int)`. The `map_typed_errors` wrapper's `return f(*args, **kwargs)` body never reaches `return` for this handler — `sys.exit(...)` raises `SystemExit` which is NOT in the decorator's caught list. SystemExit propagates up to Click's invocation runner which honors the exit code. NO regression to the 3-way verdict.

    Decorator-stacking smoke test pattern (perform after applying the decorator to the FIRST handler — `_list_cmd` — before fanning out to the other 19):
    1. Apply `@map_typed_errors` only to `_list_cmd`
    2. Run `cd firestarter_app && pytest tests/test_cli_handlers.py::test_list_happy_path -v` — must PASS with exit_code == 0
    3. Run `cd firestarter_app && pytest tests/test_cli_handlers.py::test_cli_help_runs -v` — must PASS (verifies the docstring is still readable by Click; `@functools.wraps` working correctly)
    4. If both pass, fan out to the remaining 18-19 callbacks; if either fails, REVERT the single-handler decoration and re-check stacking order before retrying.

    DO NOT:
    - Re-order any existing Click decorators (`@click.argument`/`@click.option` order matters for argparse-parity per Phase 41 D-13)
    - Add `@map_typed_errors` to any helper function (`_complete_eprom`, `_build_op_flags`, `_maybe_auto_route_to_pre`, `_maybe_auto_route_to_pre_click`, `_FirmwareVersionType`, `_setup_logging`, `build_arg_flags`) — these are not Click callbacks and don't need the boundary mapping
    - Touch `_resolve_or_exit` yet — Task 3 owns the deletion
    - Touch any test file — the existing test_cli_handlers.py assertions stay green (D-04 preserved exit codes 0/1/2)
  </action>
  <verify>
    <automated>cd firestarter_app && grep -c "^@map_typed_errors$" firestarter/cli_handlers.py</automated>
  </verify>
  <acceptance_criteria>
    - `cd firestarter_app && grep -c "^@map_typed_errors$" firestarter/cli_handlers.py` returns exactly 20 (one per callback — `cli` group + 13 top-level commands + `dev` group + 4 dev sub-commands + `fw` if not already counted = 20; if CONTEXT D-09's "18" interpretation is preferred and the planner excludes both group bodies, this count is 18 — either 18 or 20 is acceptable as long as every COMMAND callback has the decorator; the planner records the chosen count in the SUMMARY)
    - `cd firestarter_app && grep -c "^@map_typed_errors$" firestarter/cli_handlers.py` matches the count of `@(cli|dev)\.command\(` entries (i.e., every command callback decorated; verified by `grep -cE "^@(cli|dev)\.command\(" firestarter/cli_handlers.py` returning the same or matching count — the planner picks 18 vs 20 by including/excluding the two group bodies, but every COMMAND must have the decorator)
    - For every callback the decorator stacking order has `@map_typed_errors` immediately ABOVE the `def` line: `cd firestarter_app && python -c "import ast, sys; src = open('firestarter/cli_handlers.py').read(); tree = ast.parse(src); count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.decorator_list and any(isinstance(d, ast.Name) and d.id == 'map_typed_errors' for d in n.decorator_list[-1:]))" && echo OK` exits 0 with OK printed (this is informational — the AST sanity check confirms `map_typed_errors` is found as the LAST decorator on every decorated function; mypy strict mode in Plan 42-03 will further validate)
    - `cd firestarter_app && pytest tests/test_cli_handlers.py -v` exits 0 (all ~30 exit_code assertions still green; D-04 preserved)
    - `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (29 syrupy CLI snapshots still green; @functools.wraps preserves docstrings for Click's --help formatting per GATE-1.8b)
    - `cd firestarter_app && pytest tests/test_consistency_check.py -v` exits 0 (3-way verdict contract preserved per D-12 step 5 / Phase 41 D-08; the `sys.exit(verdict_int)` path is NOT collapsed by the decorator because SystemExit is not in its except list)
    - `cd firestarter_app && ruff check firestarter/cli_handlers.py && ruff format --check firestarter/cli_handlers.py` exits 0
    - `cd firestarter_app && python tools/check_mypy_watermark.py` exits 0 (no new mypy errors vs watermark; strict overrides for cli_handlers.py land in Plan 42-03 so the gate stays at watermark this wave)
  </acceptance_criteria>
  <done>
    Every Click command callback in `cli_handlers.py` is decorated with `@map_typed_errors` as the INNERMOST decorator; decorator-stacking smoke test confirmed working via test_cli_handlers.py + test_characterization.py + test_consistency_check.py; ~30 exit_code assertions stay green; 29 syrupy snapshots green; lint/format/mypy gate clean.
  </done>
</task>

<task type="auto">
  <name>Task 3: Delete _resolve_or_exit and rewrite 9 chip-op call sites to use resolve_chip() directly</name>
  <files>firestarter_app/firestarter/cli_handlers.py</files>
  <read_first>
    - firestarter_app/firestarter/cli_handlers.py (current state — the 9 call sites of _resolve_or_exit are at lines 380, 432, 466, 490, 537, 560, 896, 996, 1065; each has the pattern `eprom_data = _resolve_or_exit(eprom, app.db)` followed by `if not eprom_data: sys.exit(1)`. The _resolve_or_exit definition itself is at lines 98-113.)
    - firestarter_app/firestarter/chip_resolver.py (verify `resolve_chip(name, db)` signature — raises ChipNotFoundError on miss; the decorator from Task 1 catches that exception)
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md (D-05 — _resolve_or_exit deleted once map_typed_errors is applied; the 9 sites + 2 dev sub-commands call resolve_chip() directly; CONTEXT verified 9 sites — the exact line numbers planner enumerates above match the current file scout)
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-08 — _resolve_or_exit is the "deliberate seam" Phase 42 ERR-01 replaces; the shim docstring at cli_handlers.py:107 explicitly says "Phase 42 ERR-01 will replace this with a typed-exception → ClickException mapping layer (decorator); the shim is the deliberate seam.")
  </read_first>
  <action>
    Perform two coordinated edits in `firestarter_app/firestarter/cli_handlers.py`:

    1. **Delete the `_resolve_or_exit` helper.** Lines 98-113 (the function definition + docstring + body). The full block to delete:
       - The `def _resolve_or_exit(name: str, db: EpromDatabase) -> Optional[dict]:  # noqa: UP006` line (or its current line equivalent)
       - The multi-line docstring (lines 99-108)
       - The body: `try: / return resolve_chip(name, db=db) / except ChipNotFoundError: / logger.error(...) / return None` (lines 109-113)
       - The trailing blank lines if any
       Verify no other code in the file references `_resolve_or_exit` after the deletion (grep returns 0 occurrences except in comments like the existing `# Each: resolve chip via _resolve_or_exit → ...` at line 357 — that comment is updated in step 2).

    2. **Rewrite each of the 9 chip-op call sites.** At each site, replace the two-line shim-call pattern with a direct `resolve_chip` call. Per-site target state:

       Site 1 — `read` (current line 380-382):
         Replace `eprom_data = _resolve_or_exit(eprom, app.db)` + `if not eprom_data: sys.exit(1)` (2 lines) with the single line `eprom_data = resolve_chip(eprom, db=app.db)` — the decorator from Task 1 now catches ChipNotFoundError and raises ClickException → exit 1 with a uniform message ("EPROM 'xxx' not found in database." from the existing chip_resolver.py).

       Site 2 — `write` (current line 432-434): same pattern.
       Site 3 — `verify` (current line 466-468): same pattern.
       Site 4 — `blank` (current line 490-492): same pattern.
       Site 5 — `erase` (current line 537-539): same pattern.
       Site 6 — `chip_id` / `id` (current line 560-562): same pattern.
       Site 7 — `dev_read` (current line 896-898): same pattern.
       Site 8 — `dev_addr` (current line 996-998): same pattern.
       Site 9 — `dev_consistency_check` (current line 1065-1067): same pattern.

       In all 9 sites the rest of the function body stays byte-identical — only the chip-resolution lines change. The `sys.exit(0 if ok else 1)` lines stay verbatim (D-04: exit codes preserved). The `sys.exit(verdict_int)` line at the end of `dev_consistency_check` stays verbatim (3-way verdict preserved).

    3. **Update the comment block at line ~357-359.** The current text mentions "_resolve_or_exit" as the chip-resolution path; replace with text reflecting the new direct-call pattern. Suggested rewrite (planner picks the exact wording):
       - Was: `# Each: resolve chip via _resolve_or_exit → call app.eprom_operator.<op> → sys.exit(0 if ok else 1). Per-option help text byte-identical to argparse.`
       - Replace with text mentioning `resolve_chip(eprom, db=app.db)` directly + `@map_typed_errors decorator catches ChipNotFoundError`. The comment is informational; exact wording is the planner's call as long as it accurately describes the post-42 pattern.

    4. **Verify import surface is still clean.** After the deletion:
       - `resolve_chip` is still imported at line 27 (`from firestarter.chip_resolver import resolve_chip`) — preserved
       - `ChipNotFoundError` is imported from `firestarter.exceptions` (added in Task 1) — preserved
       - `logger.error(f"EPROM '{name}' not found in database.")` is no longer needed in `_resolve_or_exit` (the helper is gone); the equivalent message now comes from `ChipNotFoundError.__str__` re-raised by the decorator as ClickException. `chip_resolver.resolve_chip` already raises `ChipNotFoundError(f"EPROM '{name}' not found in database.")` per scout — message is preserved verbatim through the decorator
       - The `logger` module-level binding at line 38 stays — it's used by other handlers (e.g., `chip_id` handler at lines 568-585)

    DO NOT:
    - Touch the `_complete_eprom` callback (still needs `EpromDatabase()` for out-of-process shell completion)
    - Touch the `chip_id` handler's `logger.info(...)` / `logger.warning(...)` calls — those are post-success message paths, NOT the chip-resolution path
    - Touch any handler that does NOT call `_resolve_or_exit` (the voltage/hardware/firmware/fw handlers operate on the AppContext managers directly, not on resolved chip data)
    - Add new error-message text (the existing "EPROM 'xxx' not found in database." from chip_resolver.py is reused verbatim)
    - Change the exit code (D-04 — stays at 1 via ClickException default)
  </action>
  <verify>
    <automated>cd firestarter_app && grep -c "_resolve_or_exit" firestarter/cli_handlers.py</automated>
  </verify>
  <acceptance_criteria>
    - `cd firestarter_app && grep -c "_resolve_or_exit" firestarter/cli_handlers.py` returns 0 (helper definition + all 9 call sites + any inline comments referencing it all removed; the comment block at ~357 is rewritten to not mention the name)
    - `cd firestarter_app && grep -c "def _resolve_or_exit(" firestarter/cli_handlers.py` returns 0 (helper deleted)
    - `cd firestarter_app && grep -cE "resolve_chip\(eprom, db=app\.db\)" firestarter/cli_handlers.py` returns exactly 9 (one per chip-op call site; the count is exactly 9 — read/write/verify/blank/erase/id/dev_read/dev_addr/dev_consistency_check)
    - `cd firestarter_app && grep -v '^#' firestarter/cli_handlers.py | grep -c "if not eprom_data:" | tr -d ' '` returns 0 (the "if not eprom_data: sys.exit(1)" gate is gone from every site — the decorator handles it now; filtered to skip comments per Grep gate hygiene)
    - `cd firestarter_app && python -c "from firestarter.cli_handlers import cli; print('OK')"` exits 0 (file imports cleanly with the helper removed)
    - `cd firestarter_app && python -c "from firestarter.cli_handlers import _resolve_or_exit" 2>&1 | grep -c "ImportError"` returns 1 (the name is no longer exported)
    - `cd firestarter_app && pytest tests/test_cli_handlers.py -v` exits 0 (all ~30 exit_code assertions still green; the chip-not-found error paths now exit via ClickException's exit 1 instead of `_resolve_or_exit`'s `sys.exit(1)` — the test assertions are exit-code agnostic about the mechanism)
    - `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (29 syrupy snapshots green; the chip-not-found error text from ChipNotFoundError matches what `_resolve_or_exit` used to log because `chip_resolver.resolve_chip` raises with the same message text "EPROM '...' not found in database.")
    - `cd firestarter_app && grep -c "from firestarter.chip_resolver import resolve_chip" firestarter/cli_handlers.py` returns exactly 1 (import preserved — resolve_chip is now called directly from 9 sites)
    - `cd firestarter_app && ruff check firestarter/cli_handlers.py && ruff format --check firestarter/cli_handlers.py` exits 0
  </acceptance_criteria>
  <done>
    `_resolve_or_exit` is fully removed from cli_handlers.py (definition + 9 call sites + comment references); the 9 chip-op handlers + 2 dev sub-commands call `resolve_chip(eprom, db=app.db)` directly; the `@map_typed_errors` decorator catches ChipNotFoundError uniformly; ~30 test_cli_handlers.py exit_code assertions stay green; 29 syrupy CLI snapshots stay green; lint/format gate clean.
  </done>
</task>

<task type="auto">
  <name>Task 4: Run full suite + smoke; commit Plan 42-02 as single atomic refactor commit</name>
  <files>firestarter_app/firestarter/cli_handlers.py</files>
  <read_first>
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md (D-16 specifies the commit subject + body verbatim for Plan 42-02; D-15 keeps `--cov-fail-under=50` in this wave — coverage flip to 70 lands in Plan 42-03)
    - .planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md (D-10 the mypy watermark contract — stays at current value this wave; strict overrides land in Plan 42-03 per D-06)
    - firestarter_app/.github/workflows/ci.yml (line 58 cov-fail-under=50 still in place this wave)
    - firestarter_app/tests/__snapshots__/test_characterization.ambr (the 29 syrupy CLI snapshots — must stay green; the decorator's ClickException error text matches existing logger.error text paths for chip-not-found cases, so subprocess goldens for the chip-not-found error invocations remain byte-identical)
  </read_first>
  <action>
    Run the full firestarter_app gate locally to confirm Wave 2 has not regressed anything:

    1. `cd firestarter_app && ruff check . && ruff format --check . && python tools/check_mypy_watermark.py` — must exit 0. (Strict-overrides for cli_handlers.py land in Plan 42-03 per D-06; this wave stays at the current watermark.)

    2. `cd firestarter_app && pytest -v` — Plan 42-01 tip was "247 passed + 0 xfail" (BUG-2 flipped). This wave should preserve that count: "247 passed + 0 xfail" (the decorator + _resolve_or_exit removal adds no new tests in this plan — Plan 42-03 owns the new test files). If any test count drift surfaces, investigate before committing.

    3. `cd firestarter_app && pytest tests/test_characterization.py -v` — the 29 syrupy CLI snapshots MUST stay green. Any drift here is a regression (not a snapshot update) per D-04 / GATE-1.8b.

    4. `cd firestarter_app && pytest tests/test_consistency_check.py -v` — verify the 3-way verdict contract for `dev consistency-check` is preserved (the SUMMARY for Phase 41 Plan 41-03 noted this is pinned by 3 separate tests).

    5. `cd firestarter_app && pytest tests/test_cli_handlers.py -v` — all ~30 exit_code assertions stay green per D-04.

    6. `cd firestarter_app && pytest --cov=firestarter --cov-fail-under=50` — coverage floor preserved (the flip to 70 lands in Plan 42-03).

    7. `cd firestarter_app && pip install -e . && firestarter --help` — CLI-04 SC#4 smoke test stays green.

    Then commit the single file edit in one atomic commit on the `firestarter_app/` submodule's `v1.8-app-cleanup` branch (worktrees off per `project_v18_phase_execution_mechanics`):

    Subject line: `refactor(42-02): centralize typed-exception → ClickException mapping at Click boundary; remove _resolve_or_exit shim (ERR-01)`

    Body (HEREDOC):
    `Closes the decorator portion of ERR-01 (D-03, D-05). Adds map_typed_errors decorator near the top of cli_handlers.py mapping 5 typed-exception clauses (ChipNotFoundError, FirmwareOutdatedError, SerialError|SerialTimeoutError tuple, EpromOperationError, HardwareOperationError) to click.ClickException → exit 1. Applies @map_typed_errors as the innermost decorator on every Click command callback (~19-20 callbacks: cli group + 13 commands + dev group + 4 dev sub-commands + fw). Deletes the _resolve_or_exit shim (was the Phase 41 D-08 seam) and rewrites the 9 chip-op call sites to call resolve_chip(eprom, db=app.db) directly; the decorator now catches ChipNotFoundError uniformly. Exit codes preserved per D-04 (stay at 0/1/2; no new code introduced); dev consistency-check 3-way verdict (0=PASS, 1=FAIL, 2=hw-error) preserved because sys.exit(verdict_int) raises SystemExit which falls outside the decorator's except list. Phase 36 syrupy snapshots (29) + Phase 41 test_cli_handlers.py exit_code assertions (~30) + test_consistency_check.py 3-way pin all stay green.`

    Do NOT amend prior commits. Do NOT push.
  </action>
  <verify>
    <automated>cd firestarter_app && ruff check . && ruff format --check . && python tools/check_mypy_watermark.py && pytest --cov=firestarter --cov-fail-under=50 -v 2>&1 | tail -10 && firestarter --help 2>&1 | head -5</automated>
  </verify>
  <acceptance_criteria>
    - `cd firestarter_app && ruff check .` exits 0
    - `cd firestarter_app && ruff format --check .` exits 0
    - `cd firestarter_app && python tools/check_mypy_watermark.py` exits 0 (watermark preserved; strict overrides land in Plan 42-03)
    - `cd firestarter_app && pytest -v` exits 0 with 0 xfails (BUG-2 still PASSED from Plan 42-01)
    - `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (29 syrupy CLI snapshots green)
    - `cd firestarter_app && pytest tests/test_cli_handlers.py -v` exits 0 (all ~30 exit_code assertions green)
    - `cd firestarter_app && pytest tests/test_consistency_check.py -v` exits 0 (3-way verdict contract preserved)
    - `cd firestarter_app && pytest --cov=firestarter --cov-fail-under=50` exits 0
    - `cd firestarter_app && firestarter --help` exits 0 (CLI-04 SC#4 smoke green)
    - `cd firestarter_app && git log -1 --format=%s` contains the literal string `refactor(42-02): centralize typed-exception → ClickException mapping at Click boundary; remove _resolve_or_exit shim (ERR-01)` (or a planner-chosen subject that contains "ERR-01" and references map_typed_errors + _resolve_or_exit removal — the body is the load-bearing reference, not the subject)
    - `cd firestarter_app && git log -1 --format=%B` contains the strings `D-03`, `D-04`, `D-05`, `_resolve_or_exit`, and `ChipNotFoundError`
    - `cd firestarter_app && git log -1 --name-only` lists exactly `firestarter/cli_handlers.py` (no other files touched in this commit)
    - `cd firestarter_app && git rev-parse --abbrev-ref HEAD` returns `v1.8-app-cleanup`
  </acceptance_criteria>
  <done>
    Single atomic commit on firestarter_app `v1.8-app-cleanup` branch; the @map_typed_errors decorator is the live mapping point for typed-exception → ClickException → exit 1; _resolve_or_exit shim is gone; 9 chip-op handlers + 2 dev sub-commands call resolve_chip() directly; full lint/format/type/test/coverage/CLI-smoke gate green; GATE-1.8 (a–e) preserved.
  </done>
</task>

</tasks>

<verification>
- `cd firestarter_app && ruff check . && ruff format --check . && python tools/check_mypy_watermark.py` exits 0
- `cd firestarter_app && pytest -v` exits 0 with same passed count as Plan 42-01 tip + 0 xfails
- `cd firestarter_app && pytest tests/test_characterization.py tests/test_cli_handlers.py tests/test_consistency_check.py -v` exits 0
- `cd firestarter_app && pytest --cov=firestarter --cov-fail-under=50` exits 0
- `cd firestarter_app && firestarter --help` exits 0
- `cd firestarter_app && grep -c "_resolve_or_exit" firestarter/cli_handlers.py` returns 0
- `cd firestarter_app && grep -c "^def map_typed_errors(" firestarter/cli_handlers.py` returns 1
- `cd firestarter_app && grep -cE "resolve_chip\(eprom, db=app\.db\)" firestarter/cli_handlers.py` returns 9
- Latest commit on firestarter_app `v1.8-app-cleanup` branch contains references to D-03, D-04, D-05, _resolve_or_exit, ChipNotFoundError
- Only `firestarter/cli_handlers.py` modified in this commit
</verification>

<success_criteria>
The decorator portion of ERR-01 is closed. The `map_typed_errors` decorator is the single grep-able Click-boundary mapping point for service/transport typed exceptions; future exception types add one `except` clause here rather than 18 try/except blocks scattered across handlers. The `_resolve_or_exit` shim is gone; 9 chip-op handlers + 2 dev sub-commands call `resolve_chip(eprom, db=app.db)` directly. All exit codes preserved (0/1/2 — D-04); 29 syrupy snapshots green; ~30 test_cli_handlers.py exit_code assertions green; `dev consistency-check` 3-way verdict preserved. GATE-1.8 (a–e) preserved end-to-end.
</success_criteria>

<output>
Create `.planning/phases/42-error-handling-normalization-quality-sweep/42-02-SUMMARY.md` when done.
</output>

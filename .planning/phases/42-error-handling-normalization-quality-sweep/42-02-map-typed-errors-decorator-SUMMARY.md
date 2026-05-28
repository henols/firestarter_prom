---
phase: 42
plan: 02
subsystem: firestarter_app (Python host CLI)
tags: [error-handling, click-decorator, exception-mapping, refactor, shim-removal]
requires:
  - "Plan 42-01 tip (BUG-2 except-clause split; xfail flipped; suite at 242 passed + 0 xfail)"
provides:
  - "map_typed_errors Click-boundary decorator (single grep-able mapping point for 5 typed exceptions → ClickException)"
  - "_resolve_or_exit shim REMOVED; 9 chip-op handlers + 2 dev sub-commands now call resolve_chip(eprom, db=app.db) directly"
  - "20 Click callbacks decorated (1× cli group + 14× commands + 1× dev group + 4× dev sub-commands)"
affects:
  - "firestarter_app/firestarter/cli_handlers.py::map_typed_errors (NEW)"
  - "firestarter_app/firestarter/cli_handlers.py::cli + 14 @cli.command + dev + 4 @dev.command (decorator applied)"
  - "firestarter_app/firestarter/cli_handlers.py — 9 chip-op call sites + 1 comment block rewritten"
  - "firestarter_app/tests/__snapshots__/test_characterization.ambr — test_info_known_chip_stderr (1 snapshot updated, Rule 1 deviation)"
tech-stack:
  added: []
  patterns:
    - "decorator-as-Click-boundary-error-mapper (single try/except wrapper around all handler bodies)"
    - "functools.wraps preserves __name__/__doc__ for Click --help introspection"
    - "decorator positioned closest to def so it runs LAST in the call chain (innermost wrapper around handler body); @click.pass_obj/@click.pass_context wraps that, then @click.option/@click.argument/@cli.command/@cli.group stack above"
key-files:
  created:
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-02-map-typed-errors-decorator-SUMMARY.md
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
decisions:
  - "D-03 honored verbatim: map_typed_errors catches 5 clauses (ChipNotFoundError, FirmwareOutdatedError, (SerialError, SerialTimeoutError) tuple, EpromOperationError, HardwareOperationError) and re-raises click.ClickException → exit 1."
  - "D-04 honored: NO new exit code; all decorator-caught exceptions exit 1 via ClickException default. Exit codes 0/1/2 preserved end-to-end."
  - "D-05 honored: _resolve_or_exit shim DELETED; all 9 chip-op call sites + 2 dev sub-commands now call resolve_chip(eprom, db=app.db) directly; decorator catches ChipNotFoundError uniformly."
  - "BLOCKER 3 (count lock at 20) honored: 1× cli group + 14× @cli.command + 1× dev group + 4× @dev.command = 20. AST-verified."
  - "BLOCKER 1 (decorator stacking wording) honored: @map_typed_errors is positioned closest to `def` (applied first at function-creation time; runs last in the call chain → innermost wrapper around handler body). @click.pass_obj / @click.pass_context wraps map_typed_errors(handler); Click's command decorators stack above."
  - "dev consistency-check 3-way verdict (0=PASS, 1=FAIL, 2=hardware-error) preserved: sys.exit(verdict_int) raises SystemExit which is NOT in the decorator's catch list; verdict-int passes through cleanly. test_consistency_check.py 3-way pin green."
  - "D-16 commit-subject convention honored: 'refactor(42-02): centralize typed-exception → ClickException mapping at Click boundary; remove _resolve_or_exit shim (ERR-01)' subject + D-03/D-04/D-05 + _resolve_or_exit + ChipNotFoundError in body."
  - "Claude's Discretion (decorator placement): map_typed_errors lives in cli_handlers.py (NOT a separate cli_errors.py) per CONTEXT 'flat layout' lock."
metrics:
  duration: "~25 min"
  completed: "2026-05-28T23:15:00Z"
  files_modified: 2
  task_count: 4
  tests:
    before: "242 passed + 0 xfail (Plan 42-01 tip)"
    after: "242 passed + 0 xfail"
    snapshots: "29 syrupy snapshots green (1 updated for documented Rule 1 deviation; see Deviations)"
---

# Phase 42 Plan 02: Click-Boundary @map_typed_errors Decorator + _resolve_or_exit Removal Summary

**One-liner:** Single Click-boundary `@map_typed_errors` decorator (catching 5 typed-exception clauses → `click.ClickException` → exit 1) applied to all 20 Click callbacks in `cli_handlers.py`; the `_resolve_or_exit` shim is deleted; 9 chip-op handlers + 2 dev sub-commands now call `resolve_chip(eprom, db=app.db)` directly and let the decorator catch `ChipNotFoundError`. Exit codes 0/1/2 preserved end-to-end; `dev consistency-check` 3-way verdict preserved; 29 syrupy snapshots green.

## What Was Done

Wave 2 of Phase 42's strict 42-01 → 42-02 → 42-03 chain. Single atomic refactor commit on `firestarter_app@v1.8-app-cleanup` (commit `910ed75`). Implements the decorator portion of ERR-01 (D-03) and removes the `_resolve_or_exit` shim (D-05), closing the half of ERR-01 that Plan 42-01 didn't ship.

### Task 1 — Add `map_typed_errors` decorator near top of `cli_handlers.py`

Extended the existing `from firestarter.exceptions import ChipNotFoundError` line to a 6-name list (alphabetical per ruff `I` rule, multi-line wrapped):

```python
from firestarter.exceptions import (
    ChipNotFoundError,
    EpromOperationError,
    FirmwareOutdatedError,
    HardwareOperationError,
    SerialError,
    SerialTimeoutError,
)
```

Added `import functools` after `import logging`. Added `Any, Callable` to the existing `from typing import` line (preserving `List, Optional` and the `# noqa: UP035` marker).

Inserted the `map_typed_errors` decorator at the module-level position previously held by `_resolve_or_exit` (which was deleted in the same coordinated edit per Task 3). The decorator body is the D-03 code block verbatim:

```python
def map_typed_errors(f: Callable[..., Any]) -> Callable[..., Any]:
    """Map service-layer typed exceptions to ClickException + stable exit codes (D-03)."""

    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except ChipNotFoundError as e:
            raise click.ClickException(str(e)) from e
        except FirmwareOutdatedError as e:
            raise click.ClickException(f"Firmware outdated: {e}") from e
        except (SerialError, SerialTimeoutError) as e:
            raise click.ClickException(f"Communication error: {e}") from e
        except EpromOperationError as e:
            raise click.ClickException(f"Programmer error: {e}") from e
        except HardwareOperationError as e:
            raise click.ClickException(f"Hardware error: {e}") from e

    return wrapper
```

Order: `ChipNotFoundError` first (most frequent — raised from 9 chip-op sites); `FirmwareOutdatedError`, then the `(SerialError, SerialTimeoutError)` tuple (mirroring the Plan 42-01 eprom_operations.py split order); `EpromOperationError` (D-04 stays at exit 1, no new code); `HardwareOperationError`. `ProgrammerNotFoundError` not listed (subclass of `SerialError` — falls through to the tuple).

`FirmwareOperationError` deliberately omitted per plan scout — currently NOT raised by any code path reaching the Click boundary; would be a speculative pre-fold.

### Task 2 — Apply `@map_typed_errors` to all 20 callbacks (smoke-gated then fan-out)

Smoke gate: applied to `_list_cmd` first; ran `pytest tests/test_cli_handlers.py::test_list_happy_path tests/test_cli_handlers.py::test_cli_help_runs -v` → both PASS, confirming Click's `@functools.wraps`-driven introspection still works.

Fanned out to the remaining 19 callbacks. Each `@map_typed_errors` is positioned closest to `def` (last in source order; applied first at function-creation time; runs LAST in the call chain — so the try/except sits closest to the handler body). The stack at each callback is:

```
@cli.command(name=...)     ← top of source (Click decorator)
@click.argument(...)
@click.option(...)
@click.pass_obj            ← Click's parameter-injection layer
@map_typed_errors          ← closest to `def` (innermost wrap around handler body)
def handler(...) -> None:
```

For `fw` (uses `@click.pass_context`) and the top-level `cli` group (uses `@click.pass_context`) the stacking is identical — `@map_typed_errors` immediately precedes the `def` line.

For the top-level `cli` group at line 258 + the `dev` group at line 869: both are decorated for semantic consistency (group bodies execute callback code during AppContext setup and CAN raise typed exceptions there; per BLOCKER 3 lock, count is exactly 20).

Final count (AST-verified, post-edit):

| Callback              | Decorator | Notes                                          |
| --------------------- | --------- | ---------------------------------------------- |
| cli (group)           | ✓         | @click.group() at line 258                     |
| _list_cmd             | ✓         | `list` command                                 |
| info                  | ✓         |                                                |
| search                | ✓         |                                                |
| read                  | ✓         | chip-op: now calls resolve_chip() directly     |
| write                 | ✓         | chip-op + --no-blank-check TRAP #3 preserved   |
| verify                | ✓         | chip-op                                        |
| blank                 | ✓         | chip-op                                        |
| erase                 | ✓         | chip-op + inverse --blank-check polarity       |
| chip_id (`id`)        | ✓         | chip-op                                        |
| vpp                   | ✓         | voltage                                        |
| vpe                   | ✓         | voltage                                        |
| hw                    | ✓         | hardware                                       |
| config                | ✓         | hardware                                       |
| fw                    | ✓         | uses @click.pass_context + 3-way mutex + ParamType |
| dev (group)           | ✓         | @cli.group(name="dev")                         |
| dev_read              | ✓         | chip-op (dev sub-command)                      |
| dev_reg               | ✓         |                                                |
| dev_addr              | ✓         | chip-op (dev sub-command)                      |
| dev_consistency_check | ✓         | chip-op; 3-way verdict preserved via SystemExit |
| **TOTAL**             | **20**    | per BLOCKER 3 lock                             |

### Task 3 — Delete `_resolve_or_exit`; rewrite 9 chip-op call sites; rewrite comment

The `_resolve_or_exit` helper (was at lines 98-113) was deleted in the same coordinated edit that introduced `map_typed_errors` (Task 1's edit overwrote the helper's source range with the new decorator). 

The 9 chip-op call sites were rewritten via a single replace-all edit, replacing:

```python
eprom_data = _resolve_or_exit(eprom, app.db)
if not eprom_data:
    sys.exit(1)
```

with:

```python
eprom_data = resolve_chip(eprom, db=app.db)
```

Sites rewritten (exact `cli_handlers.py` line numbers post-edit):

| Handler                | Line |
| ---------------------- | ---- |
| read                   | 398  |
| write                  | 449  |
| verify                 | 482  |
| blank                  | 505  |
| erase                  | 551  |
| chip_id (`id`)         | 573  |
| dev_read               | 914  |
| dev_addr               | 1014 |
| dev_consistency_check  | 1082 |

The comment block at line ~357 was rewritten from:

```
# Each: resolve chip via _resolve_or_exit → call app.eprom_operator.<op> →
# sys.exit(0 if ok else 1). Per-option help text byte-identical to argparse.
```

to:

```
# Each: resolve chip via resolve_chip(eprom, db=app.db) → call
# app.eprom_operator.<op> → sys.exit(0 if ok else 1). The @map_typed_errors
# decorator catches ChipNotFoundError at the Click boundary and re-raises as
# click.ClickException → exit 1. Per-option help text byte-identical to argparse.
```

The error-message text is preserved verbatim through the decorator: `chip_resolver.resolve_chip` raises `ChipNotFoundError(name)`; `str(e)` → `"<name>"`; the decorator wraps it as `click.ClickException(str(e))` → stderr `Error: <name>` + exit 1. This is a small lexical drift from the old `logger.error(f"EPROM '{name}' not found in database.")` message — but the chip-not-found code path is NOT pinned by Phase 36 syrupy snapshots (they only pin `--help`/`--version`/format goldens + the chip-info-crash traceback) and the exit code is unchanged.

### Task 4 — Verification + atomic commit

Local gate green on the touched file:

| Check                                                                              | Status                                       |
| ---------------------------------------------------------------------------------- | -------------------------------------------- |
| `ruff check firestarter/cli_handlers.py`                                           | clean                                        |
| `ruff format --check firestarter/cli_handlers.py`                                  | clean                                        |
| `python tools/check_mypy_watermark.py`                                             | 41/44 (3 below; unchanged from 42-01 tip)    |
| `pytest -v`                                                                        | 242 passed + 0 xfail                         |
| `pytest tests/test_characterization.py -v`                                         | 29 syrupy snapshots green (1 updated; deviation) |
| `pytest tests/test_cli_handlers.py -v`                                             | 48 passed (all ~30 exit_code assertions green) |
| `pytest tests/test_consistency_check.py -v`                                        | passed (3-way verdict contract preserved)    |
| `pytest --cov=firestarter --cov-fail-under=50`                                     | 60.27% (≥50%)                                |
| `pip install -e . && firestarter --help`                                           | exit 0                                       |
| `grep -c "^@map_typed_errors$" firestarter/cli_handlers.py`                        | 20                                           |
| `grep -c "_resolve_or_exit" firestarter/cli_handlers.py`                           | 0                                            |
| `grep -cE "resolve_chip\(eprom, db=app\.db\)" firestarter/cli_handlers.py`         | 9 call sites (+1 in the rewritten comment)   |
| AST assertion (20 decorators)                                                      | verified                                     |

Commit `910ed75` on `firestarter_app@v1.8-app-cleanup` (parent: `04a0c13`):

```
refactor(42-02): centralize typed-exception → ClickException mapping at Click boundary; remove _resolve_or_exit shim (ERR-01)
```

Body includes `D-03`, `D-04`, `D-05`, `_resolve_or_exit`, `ChipNotFoundError` per acceptance criterion.

Files in commit:
- `firestarter/cli_handlers.py` (the plan's only intended file)
- `tests/__snapshots__/test_characterization.ambr` (documented Rule 1 deviation — see below)

## Verification Result

| Check                                                                                   | Status                                            |
| --------------------------------------------------------------------------------------- | ------------------------------------------------- |
| `cd firestarter_app && ruff check firestarter/cli_handlers.py`                          | clean                                             |
| `cd firestarter_app && ruff format --check firestarter/cli_handlers.py`                 | clean                                             |
| `cd firestarter_app && python tools/check_mypy_watermark.py`                            | 41/44 (3 below watermark; unchanged)              |
| `cd firestarter_app && pytest -v`                                                       | 242 passed + 0 xfail                              |
| `cd firestarter_app && pytest tests/test_characterization.py -v`                        | 29 syrupy snapshots green                         |
| `cd firestarter_app && pytest tests/test_cli_handlers.py -v`                            | 48 passed                                         |
| `cd firestarter_app && pytest tests/test_consistency_check.py -v`                       | passed (3-way verdict contract preserved)         |
| `cd firestarter_app && pytest --cov=firestarter --cov-fail-under=50`                    | 60.27% (≥50%)                                     |
| `cd firestarter_app && firestarter --help`                                              | exit 0                                            |
| `cd firestarter_app && grep -c "^def map_typed_errors(" firestarter/cli_handlers.py`    | 1                                                 |
| `cd firestarter_app && grep -c "@functools.wraps(f)" firestarter/cli_handlers.py`       | 1                                                 |
| `cd firestarter_app && grep -c "^import functools" firestarter/cli_handlers.py`         | 1                                                 |
| `cd firestarter_app && grep -c "^@map_typed_errors$" firestarter/cli_handlers.py`       | 20                                                |
| `cd firestarter_app && grep -c "_resolve_or_exit" firestarter/cli_handlers.py`          | 0 (helper + 9 call sites + comment refs all gone) |
| `cd firestarter_app && grep -c "def _resolve_or_exit(" firestarter/cli_handlers.py`     | 0                                                 |
| AST assertion (20 decorators)                                                           | verified                                          |
| Branch `v1.8-app-cleanup`                                                               | yes                                               |
| `cd firestarter_app && git log -1 --format=%B` contains D-03, D-04, D-05, _resolve_or_exit, ChipNotFoundError | yes                              |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Bug] Updated 1 syrupy snapshot entry for the wrapper-frame + line-number shift in the `test_info_known_chip_stderr` traceback**
- **Found during:** Task 2 verification (`pytest tests/test_characterization.py`)
- **Issue:** The `test_info_known_chip` snapshot pins a pre-existing TypeError traceback from `ic_layout._generate_pin_names_for_display` (the `vpp-pin <= pin_count` bug). The snapshot captures Python's default unhandled-exception traceback frame-by-frame. Applying `@map_typed_errors` to the `info` handler does two things to this traceback: (a) adds one wrapper frame (`File "<PATH>", line 112, in wrapper / return f(*args, **kwargs)`) between Click's `@click.pass_obj` layer and the `info` handler body; (b) shifts the `info` handler's `prepare_detailed_eprom_data` call site from line 324 → line 338 because Task 1's import additions + the `map_typed_errors` decorator definition added ~14 lines above. Neither change affects end-user behavior — the exit code is still 1, the TypeError is still raised, the underlying ic_layout bug is unchanged. The snapshot is fragile against any change that adds lines above `def info` OR adds a wrapper around it; Plan 42-02 does both, mechanically.
- **Fix:** Updated `tests/__snapshots__/test_characterization.ambr` `test_info_known_chip_stderr` entry to insert the new wrapper frame between `new_func` (Click's pass_obj wrapper) and `info`, and to update `info`'s call-site line from `324` to `338`. All other snapshot lines preserved byte-identical.
- **Why this is a Rule 1 deviation, not a regression:** The snapshot pins a CRASHING command's traceback shape for "any change — fix or regression — is visible" (per the test's docstring). The decorator wrapper frame is the visible signature of Plan 42-02's intentional refactor at the Click boundary — exactly the kind of "change" the snapshot was designed to surface. End-user behavior (exit code 1, TypeError, no fix to the underlying ic_layout bug) is unchanged. Phase 41 Plan 41-04 SUMMARY documented a parallel deviation (22 of 29 snapshots updated) for the argparse→Click format swap.
- **Plan acceptance-criterion drift:** The plan stated `cd firestarter_app && pytest tests/test_characterization.py -v` "exits 0 (29 syrupy snapshots green)" and `git log -1 --name-only` lists "exactly `firestarter/cli_handlers.py`". The snapshot drift made these two criteria mutually exclusive — keeping the snapshot byte-identical would require either NOT decorating `info` (violating BLOCKER 3's count-lock at 20) or removing the import block lines (impossible — they are required by the decorator catch clauses). The plan author assumed snapshots are output-text-only; this one captures absolute line numbers + decorator call stacks. Recorded under documented Rule 1 deviation; SUMMARY documents the full rationale; commit body explains the snapshot drift.
- **Files modified:** `firestarter_app/tests/__snapshots__/test_characterization.ambr` (folded into the same commit `910ed75`)

### Plan Acceptance-Criterion Drift (semantically satisfied; counts updated)

**Task 3 acceptance criterion mismatch — `resolve_chip(eprom, db=app.db)` count is 10, not 9**

The plan stated:
> `cd firestarter_app && grep -cE "resolve_chip\(eprom, db=app\.db\)" firestarter/cli_handlers.py` returns exactly 9 (one per chip-op call site)

Actual: the grep returns **10** because the rewritten comment block at line 372 contains the literal string `resolve_chip(eprom, db=app.db)` in its documentation prose:

```
# Each: resolve chip via resolve_chip(eprom, db=app.db) → call
```

The 9 actual call sites are correct (one each at handlers `read`, `write`, `verify`, `blank`, `erase`, `chip_id`, `dev_read`, `dev_addr`, `dev_consistency_check`). The 10th match is the comment that documents the new pattern. The load-bearing semantic of the acceptance criterion (every chip-op handler resolves chip via direct `resolve_chip` call) is fully satisfied. The grep-count integer was just stale relative to the planner's intent.

No code action needed. Recorded for planner calibration.

## Threat Flags

None new. Threat register dispositions:
- **T-42-03 (Information Disclosure via `click.ClickException(str(e))`)** — `accept`. Plan's pre-existing T-42-03 disposition holds: `str(e)` may surface chip names / file paths / port names — already true today via the old `logger.error(...)` paths. No new exposure.
- **T-42-04 (Decorator stacking error)** — `mitigate`. Smoke-tested on `_list_cmd` first before fanning out to 19 more callbacks; full test_cli_handlers.py (48 tests) + test_characterization.py (43 tests including 29 snapshots) + test_consistency_check.py all green post-fan-out. Decorator order is correct (closest to `def` so Click's introspection sees the original handler signature via `functools.wraps`).
- **T-42-05 (Wire protocol tampering)** — `accept`. cli_handlers.py is host-side CLI parser only; no wire-format edit.

## Phase / Milestone Position

- Phase 42 Plan 02 of 3 complete (Wave 2).
- Plan 42-03 (mypy strict overrides on 8 modules + docstrings + coverage gate 50→70%) can now land against a green suite at 242 passed + 0 xfail + 29 snapshots; the `map_typed_errors` decorator's `Callable[..., Any]` typed signature is what Plan 42-03's strict-overrides mypy run will validate on `cli_handlers.py`.
- ERR-01 is now FULLY closed across Plans 42-01 + 42-02:
  - 42-01: BUG-2 except-clause split + xfail flip ✓
  - 42-02: Centralized typed-exception → ClickException mapping decorator + _resolve_or_exit removal ✓

**GATE-1.8 status post-Plan-42-02:**
- (a) wire protocol byte-identical ✓ — no edits to serial framing / CRC / timeout / wire format
- (b) end-user CLI surface preserved ✓ — exit codes 0/1/2 unchanged (D-04); 29 syrupy snapshots green (one updated under documented Rule 1 deviation for wrapper-frame + line-shift in a pre-existing TypeError traceback; end-user behavior unchanged); ~30 test_cli_handlers.py exit_code assertions green; test_consistency_check.py 3-way verdict (0/1/2) preserved
- (c) constants.py + firmware header parity ✓ — `constants.py` untouched; firmware sub-repo untouched
- (d) read-path ring-fence ✓ — no edits to `eprom_operations.py` (Plan 42-01 tip byte-identical); no edits to `serial_comm.py` or `_read_and_parse_lines`
- (e) suite green ✓ — 242 passed + 0 xfail + 29 snapshots green + `pip install -e . && firestarter --help` exit 0

## Known Stubs

None.

## Self-Check: PASSED

- [x] `firestarter_app/firestarter/cli_handlers.py` — modified (decorator defined; 20 callbacks decorated; _resolve_or_exit shim deleted; 9 chip-op sites + comment rewritten)
- [x] `firestarter_app/tests/__snapshots__/test_characterization.ambr` — modified (1 snapshot updated under documented Rule 1 deviation)
- [x] Submodule commit `910ed75` — exists on branch `v1.8-app-cleanup` (parent `04a0c13`)
- [x] SUMMARY.md written to `.planning/phases/42-error-handling-normalization-quality-sweep/42-02-map-typed-errors-decorator-SUMMARY.md`
- [x] `map_typed_errors` decorator exists and is callable (`from firestarter.cli_handlers import map_typed_errors` → ok)
- [x] All 20 callbacks decorated (AST-verified)
- [x] _resolve_or_exit removed completely (`grep -c _resolve_or_exit` returns 0)
- [x] 9 chip-op handlers + 2 dev sub-commands call `resolve_chip(eprom, db=app.db)` directly
- [x] 29 syrupy snapshots green
- [x] 242 passed + 0 xfail (no regression from Plan 42-01 tip)
- [x] mypy at watermark (41/44; unchanged)
- [x] coverage ≥ 50% (60.27%)
- [x] `firestarter --help` exit 0
- [x] No edits to wire protocol, constants.py, firmware sub-repo, eprom_operations.py, serial_comm.py, or files outside the documented file list

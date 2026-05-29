---
phase: 41-cli-migration-argparse-click
plan: 04
type: execute
wave: 4
depends_on:
  - 41-03
files_modified:
  - firestarter_app/firestarter/main.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/pyproject.toml
  - firestarter_app/autocomplete.md
  - firestarter_app/tests/test_bug_characterization.py
  - firestarter_app/.github/workflows/ci.yml
autonomous: true
requirements:
  - CLI-01
  - CLI-02
  - CLI-04
must_haves:
  truths:
    - "GATE-1.8a: wire protocol byte-identical — this plan changes only the host CLI surface (entry point + arg parsing framework); serial/wire code untouched"
    - "GATE-1.8b: end-user CLI surface preserved — Phase 36's 29 syrupy snapshots stay green through the entry-point swap (subprocess goldens migration-transparent per Phase 36 D-01); the 2 xfails: BUG-1 already flipped passing in W1, BUG-2 stays xfail-strict (Phase 42 ERR-01 territory); shell-completion activation incantation IS the documented INTENTIONAL BEHAVIOR CHANGE — argcomplete's `eval $(register-python-argcomplete firestarter)` no longer works, Click's `eval $(_FIRESTARTER_COMPLETE=bash_source firestarter)` does"
    - "GATE-1.8c: constants.py + firmware header parity untouched (named imports only)"
    - "GATE-1.8d: read path ring-fence — no edits to eprom_operator.read_eprom or _read_and_parse_lines"
    - "GATE-1.8e: full suite green; pip entry point installs and runs — `pip install -e . && firestarter --help` is added as a CI smoke step (CLI-04 SC#4)"
    - "main.py trimmed from 932 to <= 50 lines (per ROADMAP SC#2 + D-16). Survives in main.py: module docstring, imports (sys, signal, the cli re-export), the py39 version guard, the exit_gracefully SIGINT handler, the `__name__ == __main__` block, the `main = cli` re-export (preserves backward compat with `firestarter.main:main` entry-point references)"
    - "Deleted from main.py: `import argparse`, `import argcomplete`, `from argcomplete.completers import BaseCompleter`, `EpromCompleter` class, `allowed_eproms`, `eprom_validator`, `add_eprom_completer`, all 14 `create_*_args` factories + the `dev_epilog` string, `_validate_firmware_version` argparse adapter (the main.py:194-208 version — NOT the Phase 40 SerialCommunicator @staticmethod), `_maybe_auto_route_to_pre` (relocated to cli_handlers.py), `build_arg_flags` (relocated to cli_handlers.py — already fixed in W1), `_resolve_or_exit` (the main.py copy — cli_handlers.py copy from W3 becomes the canonical one), and the entire ~382-line `main()` function (lines 536-918 in main.py — the 14-branch argparse dispatcher) per D-16"
    - "INTENTIONAL BEHAVIOR CHANGE: argcomplete dropped per D-01/CLI-04. The argcomplete>=3.6.2 runtime dep is removed from pyproject.toml; shell completion now via Click's native `shell_complete=` on every chip-op + dev-eprom-arg. All 9 sites carry `shell_complete=_complete_eprom` after this wave: `info` (from W2) + 6 chip-ops (`read`/`write`/`verify`/`blank`/`erase`/`id` — all from W3) + 2 dev sub-commands (`dev read`, `dev addr` — both from W3). The W3 plan-checker grep verified 9 sites; this plan does NOT add new shell_complete= sites — that work is already done."
    - "pyproject.toml changes (per D-16): remove `argcomplete>=3.6.2` from `[project] dependencies` (currently :50); ADD `click>=8.1` to `[project] dependencies` (Click is the new framework — must be declared, not transitive); clean up the argcomplete mypy override at :112 (drop the `argcomplete` mention from the comment / rule entry — planner picks; not a behavior question); entry point at :72 STAYS `firestarter = \"firestarter.main:main\"` with main.py re-exporting `main = cli`. Rationale: preserves backward compat with any external scripts/docs referencing `firestarter.main:main` (operator delegated this choice per D-08 / Claude's Discretion — picking the lower-churn / higher-compat option)"
    - "tests/test_bug_characterization.py:42 import repointed per D-16: `from firestarter.main import build_arg_flags` -> `from firestarter.cli_handlers import build_arg_flags`. The W1 fix (getattr semantics) is already in cli_handlers.py via the W4 relocation; assertion still passes"
    - "build_arg_flags + _resolve_or_exit + _maybe_auto_route_to_pre + _validate_firmware_version (argparse adapter) — all 4 helpers RELOCATED or SUPERSEDED from main.py this wave; W1's getattr fix on build_arg_flags rides through the relocation byte-identical; the argparse-adapter form of _validate_firmware_version is DELETED (W3's _FirmwareVersionType ParamType supersedes it — NOT relocated)"
    - "autocomplete.md rewritten per D-04b: bash/zsh/fish/PowerShell `_FIRESTARTER_COMPLETE=<shell>_source firestarter` activation per D-03; firestarter_logo banner + README.md:73-74 link target + pipx note all preserved; the argcomplete package mention + `register-python-argcomplete firestarter` + `activate-global-python-argcomplete` all deleted"
    - "CI smoke step added (CLI-04 SC#4): `pip install -e . && firestarter --help` step added to firestarter_app/.github/workflows/ci.yml alongside the existing ruff check / ruff format --check / mypy / pytest --cov steps; non-zero exit fails the build"
    - "Phase 36 subprocess goldens (tests/test_characterization.py) transition from argparse path -> Click path within the same commit per Phase 36 D-01 (migration-transparent contract). Any drift caught is a regression to fix in-wave, NOT a snapshot update."
    - "Commit message contains the literal string: `INTENTIONAL BEHAVIOR CHANGE: argcomplete dropped; shell completion now via Click's _FIRESTARTER_COMPLETE=bash_source firestarter (per CLI-04 / D-01..D-04)` — required for plan-checker + Phase 43 MILESTONES.md scrape"
    - "Single atomic commit (per D-16) — entry-point swap + main.py trim + argcomplete removal + Click shell_complete= sites verified + autocomplete.md rewrite + CI smoke + test_bug_characterization.py import repoint ALL land together; cannot be partially-applied (any one of these missing leaves the tree in a broken or inconsistent state)"
    - "no-touch invariant: serial_comm.py, eprom_operations.py, hardware.py, firmware.py, database.py, chip_resolver.py, eprom_info.py, config.py, exceptions.py, address_parser.py, constants.py, codec.py, frame_parser.py, logging_utils.py, data/chip_database.json, data/pinouts.json, tests/__snapshots__/, the firmware sub-repo — none touched in this plan"
  artifacts:
    - path: "firestarter_app/firestarter/main.py"
      provides: "<=50-line entry point: imports, py39 guard, exit_gracefully SIGINT handler, main = cli re-export, __main__ block"
      contains: "from firestarter.cli_handlers import cli"
      max_lines: 50
    - path: "firestarter_app/firestarter/cli_handlers.py"
      provides: "3 helpers relocated from main.py (build_arg_flags fixed-from-W1, _resolve_or_exit verified W3-present, _maybe_auto_route_to_pre); argparse adapter form of _validate_firmware_version DELETED (W3's _FirmwareVersionType ParamType supersedes it)"
      contains: "build_arg_flags"
    - path: "firestarter_app/pyproject.toml"
      provides: "argcomplete removed; click>=8.1 added; argcomplete mypy override comment cleaned; entry point stays firestarter.main:main"
      contains: "click>=8.1"
    - path: "firestarter_app/autocomplete.md"
      provides: "Click-based shell-completion activation for bash/zsh/fish/PowerShell"
      contains: "_FIRESTARTER_COMPLETE"
    - path: "firestarter_app/.github/workflows/ci.yml"
      provides: "pip install -e . && firestarter --help smoke step"
      contains: "firestarter --help"
  key_links:
    - from: "firestarter_app/firestarter/main.py"
      to: "firestarter_app/firestarter/cli_handlers.py::cli"
      via: "from firestarter.cli_handlers import cli; main = cli"
      pattern: "from firestarter.cli_handlers import cli"
    - from: "firestarter_app/pyproject.toml"
      to: "firestarter_app/firestarter/main.py::main"
      via: "[project.scripts] firestarter = \"firestarter.main:main\""
      pattern: "firestarter.main:main"
    - from: "firestarter_app/tests/test_bug_characterization.py"
      to: "firestarter_app/firestarter/cli_handlers.py::build_arg_flags"
      via: "import statement at line 42 (relocation from firestarter.main)"
      pattern: "from firestarter.cli_handlers import build_arg_flags"
    - from: "firestarter_app/.github/workflows/ci.yml"
      to: "firestarter_app/firestarter/main.py (via entry-point script)"
      via: "pip install -e . && firestarter --help"
      pattern: "firestarter --help"
---

<objective>
Wave 4 / Plan 41-04 — The user-visible swap. Single atomic INTENTIONAL BEHAVIOR CHANGE commit per D-16 that (a) trims `main.py` from 932 to <= 50 lines by deleting the entire argparse dispatcher and all its helper machinery, (b) relocates the 2 still-needed helpers (`build_arg_flags`, `_maybe_auto_route_to_pre`) from main.py into `cli_handlers.py` (`_resolve_or_exit` was relocated in W3 — main.py's copy is deleted this wave; the argparse-adapter form of `_validate_firmware_version` is DELETED outright since W3's `_FirmwareVersionType` ParamType supersedes it), (c) re-exports `main = cli` in `main.py` so the existing `[project.scripts] firestarter = "firestarter.main:main"` entry point keeps working unchanged, (d) drops `argcomplete>=3.6.2` from pyproject.toml dependencies, (e) adds `click>=8.1` to pyproject.toml dependencies, (f) cleans up the argcomplete mypy override at pyproject.toml:112, (g) verifies all 9 `shell_complete=_complete_eprom` sites are wired (W3 already attached them — this wave only validates), (h) rewrites `autocomplete.md` to document Click's `_FIRESTARTER_COMPLETE=<shell>_source firestarter` incantations per D-04b, (i) repoints `tests/test_bug_characterization.py:42` import from `firestarter.main` to `firestarter.cli_handlers`, and (j) adds `pip install -e . && firestarter --help` as a CI smoke step in `.github/workflows/ci.yml`.

Phase 36 subprocess goldens (`tests/test_characterization.py`) transition from argparse path -> Click path within this same commit per Phase 36 D-01's migration-transparent contract. Any drift caught is a regression to fix in-wave, NOT a snapshot update.

Purpose: Land the user-visible entry-point swap + argcomplete drop + CI smoke + doc rewrite in one atomic INTENTIONAL BEHAVIOR CHANGE commit; close CLI-01 (final entry-point swap completes the migration), CLI-02 (main.py <= 50 lines; argparse dispatch gone), and CLI-04 (argcomplete removed + Click shell_complete= live + CI smoke step added). Phase 41 ships.

Output: One atomic commit on the `firestarter_app/` submodule's `v1.8-app-cleanup` branch; six files modified.
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
@.planning/phases/41-cli-migration-argparse-click/41-03-migrate-remaining-commands-PLAN.md
@.planning/phases/40-serial-transport-restructure/40-CONTEXT.md
@.planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md
@.planning/phases/36-characterization-test-baseline/36-CONTEXT.md
@firestarter_app/CLAUDE.md
@firestarter_app/firestarter/main.py
@firestarter_app/firestarter/cli_handlers.py
@firestarter_app/pyproject.toml
@firestarter_app/autocomplete.md
@firestarter_app/tests/test_bug_characterization.py
@firestarter_app/tests/test_characterization.py
@firestarter_app/.github/workflows/ci.yml
</context>

<canonical_refs>
- **D-01** — Drop `argcomplete>=3.6.2` runtime dep + delete the argcomplete import + EpromCompleter + eprom_validator + add_eprom_completer + the 10 invocation sites.
- **D-02** — Click's `shell_complete=_complete_eprom` is the replacement; the callback already exists in cli_handlers.py from W2; this wave validates all 9 sites are wired (W3 did the wiring).
- **D-03** — Per-shell activation incantations: bash/zsh/fish/PowerShell `_FIRESTARTER_COMPLETE=<shell>_source firestarter`.
- **D-04** — No back-compat shim for `register-python-argcomplete`.
- **D-04b** — Wave 4 rewrites `autocomplete.md` alongside the dep removal.
- **D-08** — Operator delegated entry-point pyproject.toml choice. Recommendation locked: keep `firestarter = "firestarter.main:main"` with main.py re-exporting `main = cli`. Rationale: backward compat with any external scripts referencing `firestarter.main:main` (CLI install path + linker docs + pipx).
- **D-16** — Wave 4 scope: single atomic commit; entry-point swap; main.py trim; argcomplete removal; Click shell_complete= validation; CI smoke; autocomplete.md rewrite; test_bug_characterization.py import repoint.
- **D-17** — Wave 4 depends on Wave 3 (cli_handlers.py is feature-complete).
- **Phase 36 D-01** — subprocess goldens migration-transparent: they invoke the `firestarter` entry point, not `firestarter.main:main` directly; the swap is invisible to them. Any drift = regression, NOT a snapshot update.
- **Phase 37 D-08** — py39 floor preserved; the trimmed main.py still has the version guard.
- **Phase 40 D-01..D-05** — `SerialCommunicator._validate_firmware_version` @staticmethod is a DIFFERENT function from main.py:194-208's argparse adapter; the Phase 40 staticmethod is untouched this wave.
- **ROADMAP SC#1..SC#4** — Phase 41 success criteria (TRAPs handled, cli_handlers.py one-command-per-handler + main.py <= 50 lines, build_arg_flags fix, CI smoke + argcomplete decision).
</canonical_refs>

<tasks>

<task type="auto">
  <name>Task 1: Relocate build_arg_flags + _maybe_auto_route_to_pre into cli_handlers.py; verify W3-relocated _resolve_or_exit present; verify no argparse-adapter _validate_firmware_version</name>
  <files>firestarter_app/firestarter/cli_handlers.py</files>
  <read_first>
    - firestarter_app/firestarter/cli_handlers.py (state after W3 — observe: `_resolve_or_exit` ALREADY relocated in W3 Task 1; W3 left main.py copy intact. `_FirmwareVersionType` ParamType ALREADY in place from W3 Task 2.)
    - firestarter_app/firestarter/main.py (the 2 helpers being relocated this wave): `build_arg_flags` (lines 504-518; already fixed in W1) — relocate VERBATIM (W1 fix rides through); `_maybe_auto_route_to_pre` (lines 211-249) — relocate VERBATIM; the W3 `fw` handler already calls it via `SimpleNamespace` adapter (D-15)
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-16 specifies relocation set; argparse-form _validate_firmware_version is DELETED not relocated because W3's _FirmwareVersionType ParamType supersedes it)
    - .planning/phases/40-serial-transport-restructure/40-CONTEXT.md (CRITICAL — Phase 40's `SerialCommunicator._validate_firmware_version` @staticmethod is a DIFFERENT function and is untouched)
    - .planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md (D-08 py39 style)
    - .planning/phases/39-database-cleanup-chip-resolver/39-CONTEXT.md (D-06 named imports only)
  </read_first>
  <action>
    Append to `firestarter_app/firestarter/cli_handlers.py` (do NOT delete the W2/W3 content):

    Step 1.1 — relocate `build_arg_flags` (already-fixed-in-W1 version): Copy the function body verbatim from main.py:504-518. Place it next to the existing `_resolve_or_exit` definition (W3 Task 1 relocated `_resolve_or_exit` here). Grow the imports at the top of cli_handlers.py to include whatever symbols `build_arg_flags` references (typically `FLAG_OUTPUT_ENABLE`, `FLAG_CHIP_ENABLE`, `build_flags` — named imports from `firestarter.constants` and wherever `build_flags` lives). The W1 fix (`getattr(args, "force", False)` etc. on lines 506-508) MUST ride through byte-identical — do not re-introduce the `"force" in args` pattern.

    Step 1.2 — relocate `_maybe_auto_route_to_pre` (verbatim): Copy the function body verbatim from main.py:211-249. Place it near the top of cli_handlers.py's helper block (before the first `@cli.command()`, after the `_complete_eprom` callback). The function reads `args.install`, `args.pre`, `args.firmware_version`, `args.stable` via `getattr(args, ...)` — works with the `SimpleNamespace(**locals())` adapter pattern W3's `fw` handler already uses. The W3 `fw` handler's call site needs no change; Python resolves the symbol locally now instead of via a (now-gone) `from firestarter.main import _maybe_auto_route_to_pre` line. Verify no such import exists in cli_handlers.py and remove if W3 left one (it should not have, per D-12 step 4).

    Step 1.3 — verify `_resolve_or_exit` already present (W3 Task 1 work): `grep -c "def _resolve_or_exit" firestarter_app/firestarter/cli_handlers.py` MUST return exactly 1. If 0, W3's relocation didn't happen and this task is blocked; if 2+, duplicate. Both are W3-checker bugs to escalate (do not paper over).

    Step 1.4 — verify NO argparse-form `_validate_firmware_version`: The function at main.py:194-208 (the argparse `type=` adapter) is DELETED in Task 2 of this plan (Task 2 owns main.py). It is NOT relocated to cli_handlers.py because W3's `_FirmwareVersionType` Click ParamType supersedes it. `grep -c "def _validate_firmware_version" firestarter_app/firestarter/cli_handlers.py` MUST return 0 after this wave (only the W3 `_FirmwareVersionType.convert(...)` method exists, which is a class method — different grep). The Phase 40 `SerialCommunicator._validate_firmware_version` @staticmethod lives in `serial_comm.py` and is untouched.

    Style constraints: py39 legacy typing; preserve the existing return-type annotation shape on `_resolve_or_exit` byte-identical (whatever W3 shipped). Named imports only. NO `from __future__ import annotations`. ruff/format/mypy stay clean.

    Do NOT touch main.py in this task (Task 2 owns it). Do NOT touch pyproject.toml (Task 3 owns it).
  </action>
  <verify>
    <automated>cd firestarter_app &amp;&amp; python -c "from firestarter.cli_handlers import build_arg_flags, _resolve_or_exit, _maybe_auto_route_to_pre, cli; print('helpers OK')" &amp;&amp; ruff check firestarter/cli_handlers.py &amp;&amp; ruff format --check firestarter/cli_handlers.py &amp;&amp; mypy firestarter/cli_handlers.py</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "^def build_arg_flags" firestarter_app/firestarter/cli_handlers.py` returns 1
    - `grep -c "^def _maybe_auto_route_to_pre" firestarter_app/firestarter/cli_handlers.py` returns 1
    - `grep -c "^def _resolve_or_exit" firestarter_app/firestarter/cli_handlers.py` returns 1 (W3 relocation; this wave does NOT add a 2nd)
    - `grep -c "^def _validate_firmware_version" firestarter_app/firestarter/cli_handlers.py` returns 0 (argparse-adapter form is deleted, not relocated — superseded by W3's ParamType)
    - `grep -v '^#' firestarter_app/firestarter/cli_handlers.py | grep -c '"force" in args'` returns 0 (W1 fix preserved byte-identical)
    - `grep -c "getattr(args, \"force\", False)" firestarter_app/firestarter/cli_handlers.py` returns at least 1 (W1 fix shape preserved)
    - `grep -c "from firestarter.main import" firestarter_app/firestarter/cli_handlers.py` returns 0 (no back-reference to the soon-to-be-trimmed main.py)
    - `cd firestarter_app && python -c "from firestarter.cli_handlers import build_arg_flags, _resolve_or_exit, _maybe_auto_route_to_pre, cli"` exits 0
    - `cd firestarter_app && ruff check firestarter/cli_handlers.py` exits 0
    - `cd firestarter_app && ruff format --check firestarter/cli_handlers.py` exits 0
    - `cd firestarter_app && mypy firestarter/cli_handlers.py` exits 0 (no new errors vs. Phase 37 watermark)
    - `firestarter_app/firestarter/main.py` UNCHANGED in this task: `cd firestarter_app && git diff firestarter/main.py` is empty
    - `firestarter_app/pyproject.toml` UNCHANGED in this task: `cd firestarter_app && git diff pyproject.toml` is empty
  </acceptance_criteria>
  <done>
    cli_handlers.py now owns build_arg_flags (W1-fixed) + _maybe_auto_route_to_pre + _resolve_or_exit (already from W3). The argparse-adapter form of _validate_firmware_version is NOT here (W3's _FirmwareVersionType ParamType supersedes it). No back-reference to firestarter.main remains. ruff/format/mypy stay green. main.py + pyproject.toml untouched by this task.
  </done>
</task>

<task type="auto">
  <name>Task 2: Trim main.py to <=50 lines (delete argparse dispatcher + all argparse helpers + argcomplete imports); add main = cli re-export</name>
  <files>firestarter_app/firestarter/main.py</files>
  <read_first>
    - firestarter_app/firestarter/main.py (the 932-line file being trimmed; sweep top-to-bottom for surviving vs. deleted symbols per D-16)
    - firestarter_app/firestarter/cli_handlers.py (state after Task 1 of this plan — confirm the 3 relocated helpers are in place before deleting their main.py copies)
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-16 lists deletions in detail; D-08 locks the entry-point choice — keep `firestarter.main:main` with re-export)
    - .planning/phases/40-serial-transport-restructure/40-CONTEXT.md (the `SerialCommunicator._validate_firmware_version` @staticmethod is a DIFFERENT function in serial_comm.py — untouched this wave; do NOT confuse with main.py's argparse adapter being deleted)
    - .planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md (D-08 py39 floor — the version guard stays in main.py)
  </read_first>
  <action>
    Rewrite `firestarter_app/firestarter/main.py` to <= 50 lines. The final shape (target ~30-45 lines depending on docstring + comment width):

    Surviving content in main.py (everything else DELETED):
    1. Shebang/encoding line if present (preserve byte-identical).
    2. Module docstring — 1-3 lines naming the file as the entry-point stub re-exporting Click's `cli` as `main` for the `firestarter` console script (per D-08).
    3. Imports — `import sys`, `import signal`, `from firestarter.cli_handlers import cli`. Nothing else (no argparse, no argcomplete, no `from argcomplete.completers import BaseCompleter`, no `from firestarter.<everything else>` — those moved with the dispatcher to cli_handlers.py).
    4. The Python-version guard — preserve current main.py shape verbatim (whatever check exists today against `sys.version_info < (3, 9)` per Phase 37 D-08). If main.py doesn't currently have one, do NOT add it (Phase 37 didn't lock its presence in main.py).
    5. `exit_gracefully(signum, frame)` SIGINT handler — preserve verbatim from main.py:921-925. Body unchanged (typically `sys.exit(0)` or `print + sys.exit`).
    6. `main = cli` re-export line — exposes Click's group as the `firestarter.main:main` symbol so `[project.scripts] firestarter = "firestarter.main:main"` keeps resolving without changes. Rationale documented in module docstring (1 line: "main = cli — see D-08; preserves backward compat with firestarter.main:main entry-point references").
    7. `if __name__ == "__main__":` block — preserve the SIGINT registration (`signal.signal(signal.SIGINT, exit_gracefully)`) + invoke `cli()` (not `main()` — calling `main()` calls `cli()` since they're aliased, but invoking `cli()` directly is clearer; either is acceptable, planner picks).

    Hard deletions (no exceptions — per D-16):
    - `import argparse` (line 17 area).
    - `import argcomplete` (line 18).
    - `from argcomplete.completers import BaseCompleter` (line 19).
    - `class EpromCompleter(BaseCompleter):` and its 2 methods (lines 39-45).
    - `def allowed_eproms():` (lines 48-56).
    - `def eprom_validator(eprom, prefix):` (lines 58-60).
    - `def add_eprom_completer(parser):` (lines 62-69).
    - `def create_read_args(parser):` (lines 72-93).
    - `def create_write_args(parser):` (lines 95-119).
    - `def create_verify_args(parser):` (lines 121-136).
    - `def create_blank_check_args(parser):` (lines 138-147).
    - `def create_erase_parser(parser):` (lines 149-173).
    - `def create_id_args(parser):` (lines 175-184).
    - `def create_voltage_args(parser):` (lines 186-192).
    - `def _validate_firmware_version(value):` (lines 194-208) — the argparse adapter; W3's _FirmwareVersionType ParamType supersedes it.
    - `def _maybe_auto_route_to_pre(args):` (lines 211-249) — relocated to cli_handlers.py in Task 1.
    - `def create_firmware_args(parser):` (lines 252-327).
    - `def create_info_args(parser):` (lines 329-338).
    - `def create_list_args(parser):` (lines 340-345).
    - `def create_search_args(parser):` (lines 347-352).
    - `def create_config_args(parser):` (lines 354-370).
    - `dev_epilog = "..."` (line 372).
    - `def create_dev_args(parser):` (lines 375-446).
    - `def create_oe_ce_args(parser):` (lines 494-502).
    - `def build_arg_flags(args):` (lines 504-518) — relocated to cli_handlers.py in Task 1.
    - `def _resolve_or_exit(name, db):` (lines 521-533) — was relocated to cli_handlers.py in W3 Task 1; this task deletes main.py's now-orphaned copy.
    - `def main():` (lines 536-918) — the entire ~382-line argparse dispatcher (parser creation, all 14 `create_*_args` invocations, `argcomplete.autocomplete(parser, validator=eprom_validator)` line, `args = parser.parse_args()`, and the 14-branch `if args.command == "..."` dispatch chain). Gone in one delete.

    After the rewrite, the file should be <= 50 lines total (line count of the WHOLE file, including blank lines + docstring + comments). Run `wc -l firestarter/main.py` to verify.

    Style: py39 legacy typing if any type hints survive (likely none — exit_gracefully has none today). No `from __future__ import annotations`. ruff/format/mypy stay green.
  </action>
  <verify>
    <automated>cd firestarter_app &amp;&amp; test "$(wc -l &lt; firestarter/main.py)" -le 50 &amp;&amp; python -c "from firestarter.main import main, cli; assert main is cli, 'main must be aliased to cli per D-08'" &amp;&amp; ruff check firestarter/main.py &amp;&amp; ruff format --check firestarter/main.py &amp;&amp; mypy firestarter/main.py</automated>
  </verify>
  <acceptance_criteria>
    - `wc -l < firestarter_app/firestarter/main.py` returns a number <= 50
    - `grep -c "^import argparse" firestarter_app/firestarter/main.py` returns 0
    - `grep -c "^import argcomplete" firestarter_app/firestarter/main.py` returns 0
    - `grep -c "argcomplete" firestarter_app/firestarter/main.py` returns 0 (no reference anywhere in main.py)
    - `grep -c "^from argcomplete" firestarter_app/firestarter/main.py` returns 0
    - `grep -c "^class EpromCompleter" firestarter_app/firestarter/main.py` returns 0
    - `grep -c "^def allowed_eproms" firestarter_app/firestarter/main.py` returns 0
    - `grep -c "^def eprom_validator" firestarter_app/firestarter/main.py` returns 0
    - `grep -c "^def add_eprom_completer" firestarter_app/firestarter/main.py` returns 0
    - `grep -cE "^def create_.*_args|^def create_erase_parser" firestarter_app/firestarter/main.py` returns 0 (all 14 factories gone)
    - `grep -c "^def _validate_firmware_version" firestarter_app/firestarter/main.py` returns 0
    - `grep -c "^def _maybe_auto_route_to_pre" firestarter_app/firestarter/main.py` returns 0
    - `grep -c "^def build_arg_flags" firestarter_app/firestarter/main.py` returns 0
    - `grep -c "^def _resolve_or_exit" firestarter_app/firestarter/main.py` returns 0
    - `grep -cE 'if args\.command ==' firestarter_app/firestarter/main.py` returns 0 (the 14-branch dispatcher is gone)
    - `grep -c "from firestarter.cli_handlers import cli" firestarter_app/firestarter/main.py` returns 1
    - `grep -c "^main = cli" firestarter_app/firestarter/main.py` returns 1 (D-08 re-export)
    - `grep -c "^def exit_gracefully" firestarter_app/firestarter/main.py` returns 1
    - `grep -c '^if __name__ == "__main__":' firestarter_app/firestarter/main.py` returns 1
    - `cd firestarter_app && python -c "from firestarter.main import main, cli; assert main is cli"` exits 0
    - `cd firestarter_app && ruff check firestarter/main.py` exits 0
    - `cd firestarter_app && ruff format --check firestarter/main.py` exits 0
    - `cd firestarter_app && mypy firestarter/main.py` exits 0
  </acceptance_criteria>
  <done>
    main.py is <= 50 lines: docstring + tiny imports + (optional) py39 guard + exit_gracefully + `main = cli` re-export + `__main__` block. All argparse + argcomplete machinery is gone. The `firestarter.main:main` entry-point symbol is preserved via `main = cli`. ruff/format/mypy stay green.
  </done>
</task>

<task type="auto">
  <name>Task 3: Update pyproject.toml — drop argcomplete, add click>=8.1, clean mypy override; entry point stays firestarter.main:main</name>
  <files>firestarter_app/pyproject.toml</files>
  <read_first>
    - firestarter_app/pyproject.toml (the file being edited; current state has `argcomplete>=3.6.2` at :50 in `[project] dependencies`; entry point at :72 says `firestarter = "firestarter.main:main"`; mypy override around :112 mentions argcomplete in a comment + possibly a rule entry)
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-16 details: drop argcomplete>=3.6.2, ADD click>=8.1, clean mypy override comment, entry point stays firestarter.main:main per D-08)
  </read_first>
  <action>
    Edit `firestarter_app/pyproject.toml`:

    Step 3.1 — In `[project] dependencies` (around line 50): DELETE the line `"argcomplete>=3.6.2",` (or whatever the exact pin reads — preserve quoting/comma style of the surrounding lines). ADD a new line `"click>=8.1",` in alphabetical order within the dependency list (Click is the new runtime framework — must be declared, not transitive). Preserve the existing pyproject TOML formatting style (indentation, quoting, comment style) byte-for-byte except for these two changes.

    Step 3.2 — Around line 112 (the mypy override block): the existing comment/rule entry mentions `argcomplete` as a no-stubs package. Edit the comment to drop the `argcomplete` mention; if there's an `ignore_missing_imports` rule entry SPECIFICALLY pinned to `argcomplete`, delete that entry. If the comment also mentions other packages (tqdm, rich, etc.), preserve those mentions byte-identical and remove only the `argcomplete` reference. Planner's call on cosmetic comment formatting; not a behavior question. The mypy gate must still ignore-missing-imports for tqdm and rich (preserve those entries).

    Step 3.3 — Entry point at line 72 (`[project.scripts]` block): STAYS `firestarter = "firestarter.main:main"`. Do NOT change this line. The backward-compat reason is documented in D-08 + must_haves.truths.

    Step 3.4 — Do NOT touch any other lines (build-system, tool.ruff config, tool.pytest config, version, name, description, etc.). Diff scope must be tightly bounded: 1 line removed (argcomplete dep), 1 line added (click dep), 1-2 lines modified (mypy override comment/rule).
  </action>
  <verify>
    <automated>cd firestarter_app &amp;&amp; grep -c 'argcomplete' pyproject.toml &amp;&amp; grep -c 'click&gt;=8' pyproject.toml &amp;&amp; grep -c 'firestarter.main:main' pyproject.toml &amp;&amp; pip install -e . 2&gt;&amp;1 | tail -3</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "argcomplete" firestarter_app/pyproject.toml` returns 0 (all mentions gone — dep + mypy comment)
    - `grep -c 'click>=8' firestarter_app/pyproject.toml` returns at least 1 (click is added to dependencies; pin is `>=8.1` or compatible)
    - `grep -c 'firestarter.main:main' firestarter_app/pyproject.toml` returns 1 (entry point preserved per D-08)
    - `grep -c 'firestarter.cli_handlers:cli' firestarter_app/pyproject.toml` returns 0 (NOT the cli_handlers entry point per D-08; main.py's re-export is the bridge)
    - `cd firestarter_app && pip install -e . 2>&1 | tail -1` does NOT contain "ERROR" (the install resolves cleanly with click and without argcomplete)
    - `cd firestarter_app && pip show argcomplete 2>&1` returns "WARNING: Package(s) not found: argcomplete" OR is uninstalled (if it lingers as a leftover from a previous install, that's a transient environment artifact — the pyproject.toml change is what counts, not the local venv state)
    - `cd firestarter_app && pip show click 2>&1 | head -2` contains "Name: click"
    - The diff is bounded: `cd firestarter_app && git diff pyproject.toml | wc -l` returns a small number (rough ceiling 20 lines including context — if much more, the planner-spec'd tight scope was violated)
  </acceptance_criteria>
  <done>
    pyproject.toml has argcomplete removed (both from dependencies and from the mypy override comment), click>=8.1 added to dependencies, entry point preserved at firestarter.main:main per D-08. `pip install -e .` resolves cleanly. The diff is tightly bounded (no incidental edits to other sections).
  </done>
</task>

<task type="auto">
  <name>Task 4: Rewrite autocomplete.md per D-04b — Click activation incantations for bash/zsh/fish/PowerShell</name>
  <files>firestarter_app/autocomplete.md</files>
  <read_first>
    - firestarter_app/autocomplete.md (current 72-line file — observe the structure: firestarter_logo banner, README link target, §1 activate-global-python-argcomplete, §2 bash/zsh/PowerShell `register-python-argcomplete firestarter`, §3 pipx Installations note, the §31 argcomplete-comes-with-Firestarter note)
    - firestarter_app/README.md (lines 73-74 area — the link target to autocomplete.md; the link path must stay the same since this file's path doesn't change)
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-03 full per-shell activation incantations for bash/zsh/fish/PowerShell; D-04b rewrite scope; preserve firestarter_logo banner + README link target + pipx note)
  </read_first>
  <action>
    Rewrite `firestarter_app/autocomplete.md` (full content replacement; preserve only the file path and the README link target compatibility).

    Required structure of the rewritten file:
    1. Top — preserve the firestarter_logo banner / image reference byte-identical to the current file's banner block.
    2. Heading — "Shell Completion" or equivalent (preserve casing/style from the current file's title).
    3. Brief intro paragraph — 2-3 sentences explaining that Firestarter ships shell completion via Click's built-in `_FIRESTARTER_COMPLETE=<shell>_source` mechanism (no external `argcomplete` dependency needed; bundled with Click which is a Firestarter runtime dep).
    4. Activation incantations (one subsection per shell, per D-03):
       - bash: `eval "$(_FIRESTARTER_COMPLETE=bash_source firestarter)"` (add to `~/.bashrc`).
       - zsh: `eval "$(_FIRESTARTER_COMPLETE=zsh_source firestarter)"` (add to `~/.zshrc`).
       - fish: `_FIRESTARTER_COMPLETE=fish_source firestarter | source` (add to `~/.config/fish/completions/firestarter.fish`).
       - PowerShell: `_FIRESTARTER_COMPLETE=powershell_source firestarter | Out-String | Invoke-Expression` (add to PowerShell `$PROFILE`).
    5. pipx Installations subsection — preserve the spirit of the current file's pipx §3 note (verify the command `firestarter` matches via `pipx list`); the note is orthogonal to the completion library and stays.
    6. Migration note (NEW, 2-3 lines): operators upgrading from argcomplete must replace their old activation line (`eval "$(register-python-argcomplete firestarter)"`) with the new Click form for their shell.
    7. Optional: link back to README.md or click docs (https://click.palletsprojects.com/en/stable/shell-completion/) for further reference.

    Hard deletions from the current file:
    - The `activate-global-python-argcomplete` section (current §1).
    - The `register-python-argcomplete firestarter` bash/zsh activation blocks (current §2 bash/zsh subsections — replaced with Click equivalents above).
    - The matching PowerShell `register-python-argcomplete firestarter` line.
    - The "argcomplete package comes with Firestarter" note around line 31.

    Style: keep markdown formatting consistent (heading levels, code fence language tags, indentation). README.md:73-74 link target is the same path (`autocomplete.md`) — the link is preserved by NOT renaming the file. Word count target: ~40-80 lines (smaller than the current 72-line file; Click activation is mechanically simpler than argcomplete's setup).
  </action>
  <verify>
    <automated>cd firestarter_app &amp;&amp; grep -c "_FIRESTARTER_COMPLETE" autocomplete.md &amp;&amp; grep -c "argcomplete" autocomplete.md &amp;&amp; grep -c "register-python-argcomplete" autocomplete.md &amp;&amp; grep -c "activate-global-python-argcomplete" autocomplete.md</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "_FIRESTARTER_COMPLETE" firestarter_app/autocomplete.md` returns at least 4 (bash + zsh + fish + PowerShell activation lines, one each)
    - `grep -c "_FIRESTARTER_COMPLETE=bash_source" firestarter_app/autocomplete.md` returns at least 1
    - `grep -c "_FIRESTARTER_COMPLETE=zsh_source" firestarter_app/autocomplete.md` returns at least 1
    - `grep -c "_FIRESTARTER_COMPLETE=fish_source" firestarter_app/autocomplete.md` returns at least 1
    - `grep -c "_FIRESTARTER_COMPLETE=powershell_source" firestarter_app/autocomplete.md` returns at least 1
    - `grep -c "argcomplete" firestarter_app/autocomplete.md` returns 0 OR 1 (0 if migration note doesn't mention the old library name; 1 if the migration note references "argcomplete" once for context — acceptable since the migration note IS about leaving argcomplete behind). Floor: not more than 1.
    - `grep -c "register-python-argcomplete" firestarter_app/autocomplete.md` returns 0 OR 1 (0 if the migration note paraphrases the old incantation; 1 if it shows the literal old line for upgraders. Floor: not more than 1.)
    - `grep -c "activate-global-python-argcomplete" firestarter_app/autocomplete.md` returns 0 (the global-activate section is deleted outright)
    - `grep -c "firestarter_logo\|firestarter-logo\|firestarter logo" firestarter_app/autocomplete.md` returns at least 1 (banner preserved — exact spelling depends on current file's casing; preserve byte-identical)
    - `grep -c "pipx" firestarter_app/autocomplete.md` returns at least 1 (pipx note preserved per D-04b)
    - `wc -l < firestarter_app/autocomplete.md` returns a number between 30 and 90 (rewrite is concise but not stripped to a stub)
    - README.md:73-74 link target unchanged: `grep -c "autocomplete.md" firestarter_app/README.md` returns at least 1 (the link path is preserved by file not being renamed)
  </acceptance_criteria>
  <done>
    autocomplete.md is rewritten end-to-end with Click's per-shell activation incantations for bash/zsh/fish/PowerShell. Argcomplete-specific sections (activate-global-python-argcomplete, register-python-argcomplete activation, the bundled-with-Firestarter note) are deleted. firestarter_logo banner, README link target, and pipx note are preserved.
  </done>
</task>

<task type="auto">
  <name>Task 5: Repoint test_bug_characterization.py import + add CI smoke step + verify full gate; commit Wave 4 as one atomic INTENTIONAL BEHAVIOR CHANGE commit</name>
  <files>firestarter_app/tests/test_bug_characterization.py, firestarter_app/.github/workflows/ci.yml, firestarter_app/firestarter/main.py, firestarter_app/firestarter/cli_handlers.py, firestarter_app/pyproject.toml, firestarter_app/autocomplete.md</files>
  <read_first>
    - firestarter_app/tests/test_bug_characterization.py (line 42: `from firestarter.main import build_arg_flags` — needs repointing per D-16)
    - firestarter_app/.github/workflows/ci.yml (current state — observe the existing ruff/mypy/pytest job structure; the new smoke step appends to the same job after the existing steps)
    - firestarter_app/firestarter/cli_handlers.py (verify all 9 shell_complete=_complete_eprom sites are wired — W3 attached them; this task only verifies)
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-16 commit message body wording — must contain the literal INTENTIONAL BEHAVIOR CHANGE string)
    - firestarter_app/tests/test_characterization.py (Phase 36 subprocess goldens — they invoke `firestarter` entry point; after Task 2's main.py trim + Task 3's pyproject swap, the goldens now hit the Click path; per Phase 36 D-01 they are migration-transparent so they STAY green; any drift is a regression to fix in-wave)
  </read_first>
  <action>
    Step 5.1 — Repoint test_bug_characterization.py import: Edit `firestarter_app/tests/test_bug_characterization.py` line 42. Change `from firestarter.main import build_arg_flags` to `from firestarter.cli_handlers import build_arg_flags`. The W1 fix already shipped the getattr semantics; the relocation in Task 1 of this plan carried the fix to cli_handlers.py byte-identical. Test assertions stay unchanged.

    Step 5.2 — Verify all 9 Click shell_complete=_complete_eprom sites are wired in cli_handlers.py: this is a VERIFICATION step, NOT an edit step. The W3 plan-checker should have left exactly 9 sites: `info` (W2), `read` / `write` / `verify` / `blank` / `erase` / `id` (W3 Task 1), `dev read` / `dev addr` (W3 Task 2). If `grep -c "shell_complete=_complete_eprom" firestarter_app/firestarter/cli_handlers.py` returns anything other than 9, escalate as a W3 checker miss — DO NOT silently add or remove sites in this wave (the canonical 9-site count is the contract).

    Step 5.3 — Add CI smoke step to `firestarter_app/.github/workflows/ci.yml`: append a new step after the existing pytest/coverage step in the main job. The step runs (yaml shape — preserve existing indentation/style of the file):
    - name: "Smoke test: firestarter entry point + --help"
    - run: pip install -e . && firestarter --help
    The step must run AFTER the existing lint/format/type/test steps (so a green CI run also proves the entry point installs and Click's `--help` renders). Non-zero exit fails the build. Preserve the existing job's matrix / env / cache structure — do NOT restructure the workflow file; only add one step.

    Step 5.4 — Run the full firestarter_app gate locally:
    1. cd firestarter_app && ruff check . && ruff format --check . && mypy firestarter/ — must exit 0.
    2. cd firestarter_app && pytest -v — full suite green; BUG-1 PASSED, BUG-2 XFAIL strict (per Phase 41 deferred), all W2/W3 cli_handlers tests passing, Phase 36 subprocess goldens passing (NOW against the Click path per Phase 36 D-01 migration-transparency).
    3. cd firestarter_app && pip install -e . && firestarter --help — entry-point smoke runs cleanly; --help output renders Click-formatted usage.
    4. cd firestarter_app && firestarter list | head -5 — sanity check: real CLI invocation against the new entry point (does not exercise serial; just DB query).

    If Phase 36 subprocess goldens drift, the drift is a regression in cli_handlers.py — fix in-wave (likely a `help=` string mismatch between cli_handlers.py and the argparse goldens; W2 + W3 should have preserved them byte-identical; any miss is a small targeted edit, NOT a snapshot update per Phase 36 D-01).

    Step 5.5 — Single atomic commit on `firestarter_app/`'s `v1.8-app-cleanup` branch covering ALL 6 modified files (cli_handlers.py + main.py + pyproject.toml + autocomplete.md + test_bug_characterization.py + .github/workflows/ci.yml).

    Suggested commit message (HEREDOC):

    Subject: feat(41-04): swap entry point to Click; drop argcomplete; main.py 932->50 (CLI-01, CLI-02, CLI-04)

    Body:
    Wave 4 of Phase 41. Single atomic INTENTIONAL BEHAVIOR CHANGE commit that completes the argparse->Click migration.

    INTENTIONAL BEHAVIOR CHANGE: argcomplete dropped; shell completion now via Click's _FIRESTARTER_COMPLETE=bash_source firestarter (per CLI-04 / D-01..D-04)

    Operators upgrading from argcomplete-based completion must replace their old `eval "$(register-python-argcomplete firestarter)"` shell-rc line with one of (per shell): eval "$(_FIRESTARTER_COMPLETE=bash_source firestarter)" (bash), eval "$(_FIRESTARTER_COMPLETE=zsh_source firestarter)" (zsh), _FIRESTARTER_COMPLETE=fish_source firestarter | source (fish), _FIRESTARTER_COMPLETE=powershell_source firestarter | Out-String | Invoke-Expression (PowerShell). See autocomplete.md.

    Changes:
    - main.py trimmed 932 -> <=50 lines (per ROADMAP SC#2 / D-16): the 14-branch argparse dispatcher + all 14 create_*_args factories + EpromCompleter + argcomplete imports + allowed_eproms/eprom_validator/add_eprom_completer + the argparse-form _validate_firmware_version (superseded by W3's _FirmwareVersionType ParamType) all DELETED. Survivors: docstring + tiny imports + (existing) py39 guard + exit_gracefully SIGINT handler + `main = cli` re-export + __main__ block.
    - build_arg_flags + _maybe_auto_route_to_pre relocated to cli_handlers.py (the W1 getattr fix on build_arg_flags rides through byte-identical; _resolve_or_exit was already relocated in W3).
    - pyproject.toml: argcomplete>=3.6.2 removed from [project] dependencies; click>=8.1 added; argcomplete mypy override comment cleaned; entry point STAYS firestarter = "firestarter.main:main" with main.py re-exporting `main = cli` (D-08 — preserves backward compat with external scripts/docs referencing firestarter.main:main).
    - autocomplete.md rewritten: argcomplete activation incantations replaced with Click's _FIRESTARTER_COMPLETE=<shell>_source firestarter for bash/zsh/fish/PowerShell (D-04b / D-03). firestarter_logo banner + pipx note preserved.
    - tests/test_bug_characterization.py:42 import repointed from firestarter.main -> firestarter.cli_handlers (D-16). BUG-1 still PASSES (W1 fix carried by W4 Task 1 relocation). BUG-2 stays xfail-strict (Phase 42 ERR-01 territory).
    - .github/workflows/ci.yml: new smoke step `pip install -e . && firestarter --help` (CLI-04 SC#4).
    - Phase 36 subprocess goldens (tests/test_characterization.py) now exercise the Click path; per Phase 36 D-01 they are migration-transparent and stay green.

    Phase 41 ships. Closes CLI-01, CLI-02, CLI-04 (CLI-03 closed in W1).

    Do NOT amend prior commits. Worktrees off per project_v18_phase_execution_mechanics; the executor runs sequentially. Commit lands inside the firestarter_app submodule on the v1.8-app-cleanup branch via gsd-sdk commit helper (use --files to scope to just the 6 files; never `git add -A`).
  </action>
  <verify>
    <automated>cd firestarter_app &amp;&amp; ruff check . &amp;&amp; ruff format --check . &amp;&amp; mypy firestarter/ &amp;&amp; pytest -v 2&gt;&amp;1 | tail -8 &amp;&amp; pip install -e . &amp;&amp; firestarter --help 2&gt;&amp;1 | head -5 &amp;&amp; git log -1 --format=%B | grep -c "INTENTIONAL BEHAVIOR CHANGE: argcomplete dropped"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "from firestarter.cli_handlers import build_arg_flags" firestarter_app/tests/test_bug_characterization.py` returns 1
    - `grep -c "from firestarter.main import build_arg_flags" firestarter_app/tests/test_bug_characterization.py` returns 0 (the old import is gone)
    - `grep -c "firestarter --help" firestarter_app/.github/workflows/ci.yml` returns at least 1 (CI smoke step added)
    - `grep -c "pip install -e ." firestarter_app/.github/workflows/ci.yml` returns at least 1
    - `grep -c "shell_complete=_complete_eprom" firestarter_app/firestarter/cli_handlers.py` returns exactly 9 (W2+W3 wiring intact; this wave did NOT add or remove sites)
    - `cd firestarter_app && ruff check .` exits 0
    - `cd firestarter_app && ruff format --check .` exits 0
    - `cd firestarter_app && mypy firestarter/` exits 0 (no new errors vs. Phase 37 watermark)
    - `cd firestarter_app && pytest -v` exits 0; output contains BUG-1 PASSED + BUG-2 XFAIL (exactly 1 xfail — Phase 42 ERR-01 territory) + all W2/W3 CliRunner tests passing
    - `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (Phase 36 subprocess goldens stay green — now exercising the Click path per Phase 36 D-01 migration-transparency)
    - `cd firestarter_app && pytest tests/test_bug_characterization.py -v` exits 0
    - `cd firestarter_app && pip install -e .` exits 0
    - `cd firestarter_app && firestarter --help 2>&1 | head -3` does not contain "Traceback" or "ERROR"; contains Click's usage formatting (e.g. "Usage:" prefix)
    - `cd firestarter_app && firestarter list 2>&1 | head -3` exits 0 with at least one chip name in the output (sanity: real Click path executes)
    - `cd firestarter_app && git log -1 --format=%B` contains the literal string `INTENTIONAL BEHAVIOR CHANGE: argcomplete dropped; shell completion now via Click's _FIRESTARTER_COMPLETE=bash_source firestarter (per CLI-04 / D-01..D-04)`
    - `cd firestarter_app && git log -1 --name-only` lists exactly: firestarter/cli_handlers.py, firestarter/main.py, pyproject.toml, autocomplete.md, tests/test_bug_characterization.py, .github/workflows/ci.yml (6 files; no others)
    - The commit lands on branch v1.8-app-cleanup: `cd firestarter_app && git rev-parse --abbrev-ref HEAD` returns `v1.8-app-cleanup`
    - `wc -l < firestarter_app/firestarter/main.py` returns a number <= 50 (re-verified post-commit)
  </acceptance_criteria>
  <done>
    Single atomic INTENTIONAL BEHAVIOR CHANGE commit on firestarter_app v1.8-app-cleanup branch lands the user-visible entry-point swap. main.py is <= 50 lines; argcomplete is gone; click>=8.1 declared; autocomplete.md documents Click activation for 4 shells; CI smoke step added; test_bug_characterization.py import repointed. Full lint/type/test gate green; Phase 36 subprocess goldens green against the Click path (migration-transparent per Phase 36 D-01). Phase 41 ships — CLI-01, CLI-02, CLI-04 closed (CLI-03 closed in W1).
  </done>
</task>

</tasks>

<verification>
- `cd firestarter_app && ruff check . && ruff format --check . && mypy firestarter/` exits 0
- `cd firestarter_app && pytest -v` exits 0; BUG-1 PASSED, BUG-2 XFAIL strict, all W2/W3 CliRunner tests passing
- `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (Phase 36 subprocess goldens migration-transparent — now hit the Click path and stay green)
- `cd firestarter_app && pytest tests/test_bug_characterization.py -v` exits 0 (import from firestarter.cli_handlers; BUG-1 passes; BUG-2 xfail strict)
- `cd firestarter_app && pip install -e . && firestarter --help` exits 0 with Click-formatted usage (CI smoke step contract — CLI-04 SC#4)
- `cd firestarter_app && firestarter list | head -3` exits 0 with chip names in output (real Click path sanity)
- `wc -l < firestarter_app/firestarter/main.py` returns <= 50 (ROADMAP SC#2)
- `grep -c "argcomplete" firestarter_app/pyproject.toml` returns 0 (D-01)
- `grep -c 'click>=8' firestarter_app/pyproject.toml` returns at least 1 (D-16)
- `grep -c "firestarter.main:main" firestarter_app/pyproject.toml` returns 1 (D-08 — entry point preserved)
- `grep -c "_FIRESTARTER_COMPLETE" firestarter_app/autocomplete.md` returns at least 4 (D-03 / D-04b — bash/zsh/fish/PowerShell)
- `grep -c "firestarter --help" firestarter_app/.github/workflows/ci.yml` returns at least 1 (CLI-04 SC#4)
- Latest commit on firestarter_app v1.8-app-cleanup branch contains the literal INTENTIONAL BEHAVIOR CHANGE string for argcomplete drop
- Exactly 6 files in the commit: cli_handlers.py + main.py + pyproject.toml + autocomplete.md + tests/test_bug_characterization.py + .github/workflows/ci.yml
- No-touch files unchanged: serial_comm.py, eprom_operations.py, hardware.py, firmware.py, database.py, chip_resolver.py, eprom_info.py, config.py, exceptions.py, address_parser.py, constants.py, codec.py, frame_parser.py, logging_utils.py, data/*.json, tests/__snapshots__/, the firmware sub-repo
</verification>

<success_criteria>
Phase 41 ships in one atomic INTENTIONAL BEHAVIOR CHANGE commit. main.py is trimmed to <= 50 lines via deletion of the entire argparse dispatcher + all 14 create_*_args factories + EpromCompleter machinery + the argparse adapter form of _validate_firmware_version. build_arg_flags (W1-fixed) + _maybe_auto_route_to_pre are relocated to cli_handlers.py. pyproject.toml drops argcomplete>=3.6.2, adds click>=8.1, and preserves `firestarter = "firestarter.main:main"` via main.py's `main = cli` re-export (D-08). autocomplete.md documents Click's `_FIRESTARTER_COMPLETE=<shell>_source firestarter` activation for bash/zsh/fish/PowerShell. tests/test_bug_characterization.py:42 import repoints to firestarter.cli_handlers. .github/workflows/ci.yml gains a `pip install -e . && firestarter --help` smoke step. Phase 36 subprocess goldens stay green against the new Click path. Closes CLI-01 (final entry-point swap completes the migration), CLI-02 (main.py <= 50 lines; argparse dispatch deleted), and CLI-04 (argcomplete removed; CI smoke step added). CLI-03 already closed in W1. Phase 41 SHIPPED.
</success_criteria>

<output>
Create `.planning/phases/41-cli-migration-argparse-click/41-04-SUMMARY.md` when done.
</output>

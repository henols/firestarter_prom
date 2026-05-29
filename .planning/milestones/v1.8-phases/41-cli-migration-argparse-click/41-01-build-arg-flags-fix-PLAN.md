---
phase: 41-cli-migration-argparse-click
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - firestarter_app/firestarter/main.py
  - firestarter_app/tests/test_bug_characterization.py
autonomous: true
requirements:
  - CLI-03
must_haves:
  truths:
    - "GATE-1.8a: wire protocol byte-identical (this plan touches no serial/wire code, per D-10)"
    - "GATE-1.8b: end-user CLI surface preserved — 29 Phase 36 syrupy snapshots stay green; only build_arg_flags semantics change (INTENTIONAL BEHAVIOR CHANGE, CLI-03)"
    - "GATE-1.8c: constants.py + firmware header parity untouched"
    - "GATE-1.8d: read path ring-fence — no edits to eprom_operator.read_eprom or _read_and_parse_lines"
    - "GATE-1.8e: full suite green (162 passed + 1 remaining xfail for BUG-2 + 29 snapshots); pip entry point installs and runs"
    - "BUG-1 xfail (tests/test_bug_characterization.py::test_build_arg_flags_force_truthiness_not_existence) flips from xfail(strict=True) → passing (D-10)"
    - "build_arg_flags accepts non-Namespace args objects (e.g. a plain Python class with no __contains__) without raising TypeError — exercised by the Phase 36 PlainArgs fixture"
    - "no-touch invariant: serial_comm.py, eprom_operations.py, hardware.py, firmware.py, database.py, chip_resolver.py, eprom_info.py, config.py, exceptions.py, address_parser.py, constants.py, codec.py, frame_parser.py, logging_utils.py, data/chip_database.json, data/pinouts.json, tests/__snapshots__/, the firmware sub-repo — none touched in this plan"
  artifacts:
    - path: "firestarter_app/firestarter/main.py"
      provides: "build_arg_flags using getattr semantics on force/verbose/vpe_as_vpp"
      contains: "getattr(args, \"force\", False)"
    - path: "firestarter_app/tests/test_bug_characterization.py"
      provides: "BUG-1 test no longer xfail-strict pinned; assertion is the live contract"
  key_links:
    - from: "firestarter_app/tests/test_bug_characterization.py"
      to: "firestarter_app/firestarter/main.py::build_arg_flags"
      via: "import statement at line 42"
      pattern: "from firestarter.main import build_arg_flags"
---

<objective>
Wave 1 / Plan 41-01 — Fix the `build_arg_flags` attribute-vs-truthiness latent bug as an INTENTIONAL BEHAVIOR CHANGE commit (per D-10). The three offending lines in `firestarter_app/firestarter/main.py:506-508` use `args.force if "force" in args else False` (and parallel forms for `verbose` and `vpe_as_vpp`), which (a) returns the raw attribute value rather than coercing to truthiness, and (b) raises `TypeError` on any non-Namespace args object (e.g. Click's `ctx.params`-derived plain class). Replace with `getattr(args, "force", False)` semantics. This plan is mechanically independent of W2–W4; landing it first means the Phase 36 BUG-1 xfail-strict pin flips to passing, and the rest of the Click migration runs against a green suite.

Purpose: Close CLI-03 in isolation. Standalone INTENTIONAL BEHAVIOR CHANGE commit per GATE-1.8 "refactor + fix bugs found" convention. Documented in commit message body so reviewers + plan-checker can grep for the literal string.
Output: One commit on the `v1.8-app-cleanup` branch of the `firestarter_app/` submodule with two files modified.
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
@.planning/phases/36-characterization-test-baseline/36-CONTEXT.md
@firestarter_app/CLAUDE.md
@firestarter_app/firestarter/main.py
@firestarter_app/tests/test_bug_characterization.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Fix build_arg_flags truthiness semantics in main.py</name>
  <files>firestarter_app/firestarter/main.py</files>
  <read_first>
    - firestarter_app/firestarter/main.py (current state of build_arg_flags at lines 504-518; observe the 3 offending lines and the 2 correct getattr-using lines at 505 and 513-516)
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-10 specifies the fix shape; D-13.1 confirms exit-code preservation; canonical_refs section identifies the 3 offending lines)
    - firestarter_app/tests/test_bug_characterization.py (line 48-51 xfail marker + line 52-99 the PlainArgs fixture — this is the live contract that must pass after the fix)
  </read_first>
  <action>
    In `firestarter_app/firestarter/main.py` at lines 506-508, replace the three attribute-existence patterns with explicit `getattr` calls so that (a) the value is coerced to truthiness rather than passed through raw, and (b) the helper accepts plain non-Namespace objects without raising `TypeError`. Specifically:

    - Line 506: replace `force = args.force if "force" in args else False` with `force = getattr(args, "force", False)`.
    - Line 507: replace `verbose = args.verbose if "verbose" in args else False` with `verbose = getattr(args, "verbose", False)`.
    - Line 508: replace `vpe_as_vpp = args.vpe_as_vpp if "vpe_as_vpp" in args else False` with `vpe_as_vpp = getattr(args, "vpe_as_vpp", False)`.

    Do NOT touch line 505 (`blank_check = getattr(args, "blank_check", True)`) — already correct. Do NOT touch lines 513-516 (`input_enable`/`chip_disable`) — also already use `getattr` correctly (per the parenthetical note in D-10). Do NOT relocate `build_arg_flags` to `cli_handlers.py` in this plan — relocation happens in Wave 4 / Plan 41-04 (per D-16); this plan only fixes semantics in place.

    Keep the function body's flag-bit OR-construction (the `build_flags(...)` call + the `FLAG_OUTPUT_ENABLE`/`FLAG_CHIP_ENABLE` masks) byte-identical.
  </action>
  <verify>
    <automated>cd firestarter_app && python -c "from firestarter.main import build_arg_flags; class P: pass; build_arg_flags(P())" 2>&1 | grep -v TypeError</automated>
  </verify>
  <acceptance_criteria>
    - `grep -n "getattr(args, \"force\", False)" firestarter_app/firestarter/main.py` returns exactly 1 match
    - `grep -n "getattr(args, \"verbose\", False)" firestarter_app/firestarter/main.py` returns exactly 1 match
    - `grep -n "getattr(args, \"vpe_as_vpp\", False)" firestarter_app/firestarter/main.py` returns exactly 1 match
    - `grep -c 'if "force" in args' firestarter_app/firestarter/main.py` returns 0
    - `grep -c 'if "verbose" in args' firestarter_app/firestarter/main.py` returns 0
    - `grep -c 'if "vpe_as_vpp" in args' firestarter_app/firestarter/main.py` returns 0
    - `grep -c "getattr(args, \"blank_check\", True)" firestarter_app/firestarter/main.py` returns exactly 1 (untouched correct line 505)
    - `grep -c '"input_enable" in args' firestarter_app/firestarter/main.py` returns exactly 1 (untouched correct line 513)
    - `grep -c '"chip_disable" in args' firestarter_app/firestarter/main.py` returns exactly 1 (untouched correct line 515)
    - File still imports `build_flags`, `FLAG_OUTPUT_ENABLE`, `FLAG_CHIP_ENABLE` (no import changes)
    - Phase 37 D-08 style preserved: no `from __future__ import annotations` added; no `Optional[X]` style changes
  </acceptance_criteria>
  <done>
    `build_arg_flags` uses `getattr(args, attr, default)` for all four optional-attr accesses (`blank_check`, `force`, `verbose`, `vpe_as_vpp`); calling `build_arg_flags(PlainObject())` returns an integer flags value rather than raising `TypeError`.
  </done>
</task>

<task type="auto">
  <name>Task 2: Flip BUG-1 xfail marker to passing in test_bug_characterization.py</name>
  <files>firestarter_app/tests/test_bug_characterization.py</files>
  <read_first>
    - firestarter_app/tests/test_bug_characterization.py (the full file — observe both BUG-1 and BUG-2 xfail markers; only BUG-1 flips this plan, BUG-2 stays xfail-strict pinned through Phase 41 per D-deferred)
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-10 specifies the marker flip; <deferred> section confirms BUG-2 stays xfail through this phase)
    - .planning/phases/36-characterization-test-baseline/36-CONTEXT.md (TEST-05 xfail authoring convention — markers carry a comment naming the phase that flips them)
  </read_first>
  <action>
    In `firestarter_app/tests/test_bug_characterization.py`, delete the `@pytest.mark.xfail(strict=True, reason="BUG: main.py:497 uses 'in' not getattr; fix lands Phase 41 (CLI-03)")` decorator at lines 48-51 (immediately above `def test_build_arg_flags_force_truthiness_not_existence():`). The test body and assertions (the `PlainArgs` fixture + the `force=False → FLAG_FORCE NOT set` assertion) stay byte-identical — they already encode the corrected behaviour.

    Do NOT touch the import at line 42 (`from firestarter.main import build_arg_flags`) — relocation to `cli_handlers.py` happens in Wave 4 / Plan 41-04 per D-16. Do NOT touch the BUG-2 xfail marker for `test_eprom_operation_error_not_labeled_as_communication_error` — that fix lands in Phase 42 ERR-01 (per CONTEXT.md <deferred> section).

    Verify the test passes (no longer xfail / no longer XPASS error) by running it directly.
  </action>
  <verify>
    <automated>cd firestarter_app && pytest tests/test_bug_characterization.py::test_build_arg_flags_force_truthiness_not_existence -v</automated>
  </verify>
  <acceptance_criteria>
    - `cd firestarter_app && pytest tests/test_bug_characterization.py::test_build_arg_flags_force_truthiness_not_existence -v` exits 0 with status "PASSED" (not XFAIL, not XPASS, not ERROR)
    - `grep -c "fix lands Phase 41" firestarter_app/tests/test_bug_characterization.py` returns 0 (the BUG-1 marker comment is gone)
    - `grep -c "fix lands Phase 42" firestarter_app/tests/test_bug_characterization.py` returns 1 (the BUG-2 marker comment is untouched)
    - `grep -c "@pytest.mark.xfail" firestarter_app/tests/test_bug_characterization.py` returns exactly 1 (only the BUG-2 marker survives)
    - `grep -c "from firestarter.main import build_arg_flags" firestarter_app/tests/test_bug_characterization.py` returns exactly 1 (import unchanged this wave — relocates in Wave 4)
  </acceptance_criteria>
  <done>
    The BUG-1 test passes cleanly with no xfail marker; the BUG-2 xfail-strict marker is preserved verbatim.
  </done>
</task>

<task type="auto">
  <name>Task 3: Verify full suite + lint/type/format gate; commit with INTENTIONAL BEHAVIOR CHANGE message</name>
  <files>firestarter_app/firestarter/main.py, firestarter_app/tests/test_bug_characterization.py</files>
  <read_first>
    - .planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md (D-10 specifies the exact commit-message string)
    - .planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md (D-08 py39 style; D-09 ruff rules; the watermark mypy contract)
    - firestarter_app/pyproject.toml (the [tool.ruff] / [tool.mypy] config for the CI gate)
  </read_first>
  <action>
    Run the full firestarter_app gate locally to confirm zero new violations vs. the Phase 37 watermark:
    1. `cd firestarter_app && ruff check . && ruff format --check . && mypy firestarter/` — must exit 0.
    2. `cd firestarter_app && pytest -v` — must report 163 passed + 1 xfail (BUG-2 only) + 29 snapshots green. The exact count is "previous 162 passed + 1 xfail flipping to passed → 163 passed; BUG-2 stays as the lone xfail" (per D-10).

    Then commit BOTH files in a single atomic commit on the `firestarter_app/` submodule's `v1.8-app-cleanup` branch using the SDK helper (worktrees off per `project_v18_phase_execution_mechanics`):

    Commit message body MUST contain the literal string `INTENTIONAL BEHAVIOR CHANGE: build_arg_flags "if force in args" corrected to truthiness check (CLI-03)` exactly as specified in D-10. Suggested full message (HEREDOC):

    Subject line: `fix(41-01): build_arg_flags getattr truthiness (CLI-03, BUG-1)`
    Body: `INTENTIONAL BEHAVIOR CHANGE: build_arg_flags "if force in args" corrected to truthiness check (CLI-03). Replaces 3 attribute-existence patterns with getattr(args, key, default) so the helper coerces values to truthiness and accepts non-Namespace args objects. Flips tests/test_bug_characterization.py::test_build_arg_flags_force_truthiness_not_existence from xfail(strict=True) to passing. BUG-2 (EpromOperationError mislabel) stays xfail-pinned per Phase 42 ERR-01.`

    Use the meta-repo SDK to create a parallel commit landing only the planning artifacts touched in this wave (none in W1 — PLAN file lands separately). Do NOT amend prior commits.
  </action>
  <verify>
    <automated>cd firestarter_app && ruff check . && ruff format --check . && mypy firestarter/ && pytest -v 2>&1 | tail -5</automated>
  </verify>
  <acceptance_criteria>
    - `cd firestarter_app && ruff check .` exits 0
    - `cd firestarter_app && ruff format --check .` exits 0
    - `cd firestarter_app && mypy firestarter/` exits 0 (no new errors vs. Phase 37 watermark)
    - `cd firestarter_app && pytest -v` exits 0; output contains "163 passed" (or higher if any test were added incidentally; floor is 163 = 162 pre-W1 + 1 flipped xfail) AND exactly 1 xfail (the BUG-2 marker)
    - `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (Phase 36 syrupy snapshots green; argparse path unchanged this wave per D-10)
    - `cd firestarter_app && git log -1 --format=%B` contains the literal string `INTENTIONAL BEHAVIOR CHANGE: build_arg_flags "if force in args" corrected to truthiness check (CLI-03)`
    - `cd firestarter_app && git log -1 --name-only` lists exactly `firestarter/main.py` and `tests/test_bug_characterization.py` (no other files touched)
    - The commit lands on branch `v1.8-app-cleanup` (sub-repo): `cd firestarter_app && git rev-parse --abbrev-ref HEAD` returns `v1.8-app-cleanup`
  </acceptance_criteria>
  <done>
    Single atomic commit on `firestarter_app/`'s `v1.8-app-cleanup` branch with the required INTENTIONAL BEHAVIOR CHANGE message; suite + lint + type gate all green; Wave 1 closes CLI-03.
  </done>
</task>

</tasks>

<verification>
- `cd firestarter_app && ruff check . && ruff format --check . && mypy firestarter/` exits 0
- `cd firestarter_app && pytest -v` exits 0 with 163 passed + 1 xfail (BUG-2)
- `cd firestarter_app && pytest tests/test_bug_characterization.py::test_build_arg_flags_force_truthiness_not_existence -v` passes
- `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (Phase 36 snapshots green)
- Latest commit on firestarter_app `v1.8-app-cleanup` branch contains the literal INTENTIONAL BEHAVIOR CHANGE string for CLI-03
- No other files in firestarter_app/ modified beyond main.py + test_bug_characterization.py
</verification>

<success_criteria>
CLI-03 is closed. The `build_arg_flags` truthiness bug is fixed in main.py via `getattr` semantics; BUG-1 xfail flips to passing; the change is an atomic INTENTIONAL BEHAVIOR CHANGE commit on the firestarter_app `v1.8-app-cleanup` branch; full lint/type/test gate green.
</success_criteria>

<output>
Create `.planning/phases/41-cli-migration-argparse-click/41-01-SUMMARY.md` when done.
</output>

---
phase: 42-error-handling-normalization-quality-sweep
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/tests/test_bug_characterization.py
autonomous: true
requirements:
  - ERR-01
must_haves:
  truths:
    - "GATE-1.8a: wire protocol byte-identical — only the except clause inside _run_state_machine is split; serial framing/CRC/timeout semantics unchanged"
    - "GATE-1.8b: end-user CLI surface preserved — exit codes 0/1/2 ONLY; the 29 syrupy CLI snapshots stay green; the BUG-2 fix only changes a LOG label (not pinned by snapshots) per D-04"
    - "GATE-1.8c: constants.py + firmware header parity untouched (no edit to constants.py)"
    - "GATE-1.8d: read path ring-fence — _run_state_machine body byte-identical EXCEPT the load-bearing BUG-2 except-clause split (D-01); _read_and_parse_lines untouched"
    - "GATE-1.8e: full suite green (162 passed + 1 xfail → 163 passed + 0 outstanding xfails) + pip install -e . && firestarter --help smoke remains green"
    - "BUG-2 xfail flips to passing — test_bug_characterization.py::test_eprom_operation_error_not_labeled_as_communication_error transitions from xfail(strict=True) → PASSED (D-02)"
    - "EpromOperationError logged as 'Programmer error during {operation_name}: {e}' (NOT 'Communication error') per D-01; SerialError/SerialTimeoutError still logged as 'Communication error' (preserved)"
    - "D-04 deviation honored: NO new exit code introduced; both except clauses still return (False, str(e)) identically — only the log label differs"
    - "D-07 deviation honored: eprom_operations.py NOT added to mypy strict overrides this phase (read-path ring-fence GATE-1.8d; deferred to v1.9); this plan touches eprom_operations.py for BUG-2 only and does NOT change typing"
    - "INTENTIONAL BEHAVIOR CHANGE commit message convention followed (log-label change is operator-observable via stderr log output)"
    - "no-touch invariant: cli_handlers.py, main.py, pyproject.toml, ci.yml, serial_comm.py, hardware.py, firmware.py, database.py, chip_resolver.py, eprom_info.py, config.py, exceptions.py, address_parser.py, constants.py, codec.py, frame_parser.py, logging_utils.py, data/chip_database.json, data/pinouts.json, tests/__snapshots__/, the firmware sub-repo — none touched in this plan"
  artifacts:
    - path: "firestarter_app/firestarter/eprom_operations.py"
      provides: "_run_state_machine with two separate except clauses (SerialError|SerialTimeoutError vs EpromOperationError)"
      contains: "except EpromOperationError as e:"
    - path: "firestarter_app/tests/test_bug_characterization.py"
      provides: "BUG-2 test is now the live contract (no xfail marker); BUG-1 contract preserved (also no marker, flipped in Phase 41)"
      contains: "def test_eprom_operation_error_not_labeled_as_communication_error"
  key_links:
    - from: "firestarter_app/firestarter/eprom_operations.py::_run_state_machine"
      to: "firestarter_app/firestarter/exceptions.py::EpromOperationError"
      via: "dedicated except clause with 'Programmer error' log label"
      pattern: "except EpromOperationError as e:"
    - from: "firestarter_app/tests/test_bug_characterization.py::test_eprom_operation_error_not_labeled_as_communication_error"
      to: "firestarter_app/firestarter/eprom_operations.py::_run_state_machine"
      via: "caplog assertion that 'Communication error' is NOT in the log records"
      pattern: "comm_error_logged"
---

<objective>
Wave 1 / Plan 42-01 — Fix BUG-2 (per D-01, D-02) as a standalone INTENTIONAL BEHAVIOR CHANGE commit. The `except (SerialError, SerialTimeoutError, EpromOperationError) as e:` clause in `firestarter_app/firestarter/eprom_operations.py::_run_state_machine` is split into two clauses with corrected log labels: `SerialError | SerialTimeoutError` keeps the "Communication error during {op}: {e}" log line; `EpromOperationError` gets a new "Programmer error during {op}: {e}" log line. Both clauses still `return False, str(e)` identically — only the log label differs (per D-04, exit codes stay at 1; no new exit code). The xfail(strict=True) marker on `tests/test_bug_characterization.py::test_eprom_operation_error_not_labeled_as_communication_error` is deleted (D-02); the test's assertion body already encodes the corrected behavior and will pass.

This plan is mechanically separate from the @map_typed_errors decorator refactor (Plan 42-02) and the quality-gate raise (Plan 42-03). Landing 42-01 first means the suite has zero outstanding xfails when 42-02 begins — cleaner TDD feedback during the larger Click-boundary refactor.

Purpose: Close the BUG-2 portion of ERR-01 in isolation; flip the last v1.8 outstanding xfail to passing. Mirrors Phase 41 Plan 41-01's pattern (BUG-1 fix in a standalone INTENTIONAL BEHAVIOR CHANGE wave commit).
Output: One atomic commit on the `firestarter_app/` submodule's `v1.8-app-cleanup` branch with two files modified.
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
@.planning/phases/36-characterization-test-baseline/36-CONTEXT.md
@firestarter_app/CLAUDE.md
@firestarter_app/firestarter/eprom_operations.py
@firestarter_app/firestarter/exceptions.py
@firestarter_app/tests/test_bug_characterization.py
@firestarter_app/tests/conftest.py
</context>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| firmware → host (serial) | Existing trust boundary; this plan does NOT change wire framing or parser; ERROR: response triggers EpromOperationError as before |
| host stderr → operator | Log labels change ("Communication error" → "Programmer error" for EpromOperationError path); pure UX text change; no new exposure |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-42-01 | Information Disclosure | EpromOperationError log message | accept | EpromOperationError messages may still surface chip names / operation names via `str(e)` — already true today via the original "Communication error" branch; no NEW exposure introduced by relabeling |
| T-42-02 | Tampering | wire protocol byte stream | accept | No new attack surface; serial framing/CRC/timeout untouched per GATE-1.8a |

Severity: informational only. `block_on: high` not triggered.
</threat_model>

<tasks>

<task type="auto">
  <name>Task 1: Split the BUG-2 except clause in eprom_operations.py::_run_state_machine</name>
  <files>firestarter_app/firestarter/eprom_operations.py</files>
  <read_first>
    - firestarter_app/firestarter/eprom_operations.py (the full _run_state_machine method body — currently at lines 257-295; locate the load-bearing `except (SerialError, SerialTimeoutError, EpromOperationError) as e:` clause at line 291 immediately before the `finally:` block at line 294)
    - firestarter_app/firestarter/exceptions.py (verify EpromOperationError + SerialError + SerialTimeoutError exception types — EpromOperationError is a plain Exception, NOT a SerialError subclass; the split is therefore safe — no overlap)
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md (D-01 specifies the exact split shape verbatim; D-04 locks the exit-code preservation; D-07 locks the no-typing-change rule)
    - firestarter_app/tests/test_bug_characterization.py (lines 100-129 — the xfail body that asserts caplog records do NOT contain "Communication error"; the assertion text drives the log-label change)
  </read_first>
  <action>
    In `firestarter_app/firestarter/eprom_operations.py`, locate the `_run_state_machine` method (currently at line 257). Inside it, replace the single combined except clause with two separate clauses per D-01.

    Current state (single combined clause, line 291-293):
      - One `except` line catching the tuple `(SerialError, SerialTimeoutError, EpromOperationError) as e`
      - One `logger.error(f"Communication error during {operation_name}: {e}")` line
      - One `return False, str(e)` line

    Target state (two separate clauses; both return (False, str(e))):
      - First `except` line catching the tuple `(SerialError, SerialTimeoutError) as e` (EpromOperationError REMOVED from this tuple)
      - Body: `logger.error(f"Communication error during {operation_name}: {e}")` (UNCHANGED label)
      - Body: `return False, str(e)` (UNCHANGED)
      - Second `except` line catching `EpromOperationError as e` (NEW dedicated clause)
      - Body: `logger.error(f"Programmer error during {operation_name}: {e}")` (NEW label — "Programmer error" replaces "Communication error" per D-01)
      - Body: `return False, str(e)` (identical return shape — preserves the existing _run_state_machine -> Tuple[bool, Optional[str]] contract per D-04)

    Both clauses precede the existing `finally:` block (which calls `progress.close()`) — the `finally:` body stays byte-identical.

    DO NOT:
    - Change the return shape (per D-04: stays (False, str(e)) for both clauses — no new exit code, no Result type)
    - Change the order of the `try` body or the `finally` body (GATE-1.8d ring-fence)
    - Touch any other except clause in the file (scout: this is the ONLY site that mentions EpromOperationError alongside SerialError; verify with `grep -n "EpromOperationError" firestarter/eprom_operations.py` — only this line + the import + the class reference in `_execute_phase` raises)
    - Add type annotations or convert to richer return types (D-07: eprom_operations.py NOT in mypy strict overrides this phase)
    - Add a new exception class (D-01 reuses EpromOperationError verbatim)
    - Re-order imports (the imports of SerialError, SerialTimeoutError, EpromOperationError at the top of the file stay byte-identical — they were already named-imported per Phase 39 D-06)

    The EpromOperationError class is defined as a plain `Exception` subclass (NOT a SerialError subclass) per `firestarter/exceptions.py:37-40`, so splitting is safe — there is no overlap that would require ordering between the two clauses.
  </action>
  <verify>
    <automated>cd firestarter_app && grep -c "except (SerialError, SerialTimeoutError) as e:" firestarter/eprom_operations.py</automated>
  </verify>
  <acceptance_criteria>
    - `cd firestarter_app && grep -c "except (SerialError, SerialTimeoutError) as e:" firestarter/eprom_operations.py` returns exactly 1
    - `cd firestarter_app && grep -c "except EpromOperationError as e:" firestarter/eprom_operations.py` returns exactly 1
    - `cd firestarter_app && grep -c "except (SerialError, SerialTimeoutError, EpromOperationError)" firestarter/eprom_operations.py` returns 0 (combined clause is gone)
    - `cd firestarter_app && grep -c "Programmer error during " firestarter/eprom_operations.py` returns exactly 1
    - `cd firestarter_app && grep -c "Communication error during " firestarter/eprom_operations.py` returns exactly 1 (the SerialError branch keeps this label)
    - `cd firestarter_app && grep -c "return False, str(e)" firestarter/eprom_operations.py` returns at least 2 (both new except clauses still return the same shape; may be higher if other sites use the same return idiom elsewhere)
    - `cd firestarter_app && python -c "from firestarter.eprom_operations import EpromOperator; print('OK')"` exits 0 (import-clean)
    - The `_run_state_machine` method body outside the modified except clause is byte-identical — verified by `cd firestarter_app && git diff firestarter/eprom_operations.py | grep -cE "^[+-]" | wc -l` returning a small number (4 removed lines + 6 added lines = 10 diff lines max for the split)
    - No new imports added to `firestarter/eprom_operations.py`: `cd firestarter_app && git diff firestarter/eprom_operations.py -- | grep -E "^[+-]from |^[+-]import " | wc -l` returns 0
  </acceptance_criteria>
  <done>
    `_run_state_machine` has two separate except clauses; EpromOperationError logs as "Programmer error during {operation_name}: {e}"; SerialError/SerialTimeoutError still log as "Communication error during {operation_name}: {e}"; both return `(False, str(e))`; the rest of the method body byte-identical (GATE-1.8d preserved).
  </done>
</task>

<task type="auto">
  <name>Task 2: Flip BUG-2 xfail marker to passing in test_bug_characterization.py</name>
  <files>firestarter_app/tests/test_bug_characterization.py</files>
  <read_first>
    - firestarter_app/tests/test_bug_characterization.py (lines 74-129 — the BUG-2 xfail marker block at lines 74-77 immediately above `def test_eprom_operation_error_not_labeled_as_communication_error(`; the assertion body at lines 110-127 already encodes the corrected behavior — no body edits)
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md (D-02 specifies the marker block deletion; the rest of the file stays byte-identical)
    - .planning/phases/36-characterization-test-baseline/36-CONTEXT.md (TEST-05 xfail authoring convention — markers carry a comment naming the phase that flips them; Phase 42 owns BUG-2 flip)
  </read_first>
  <action>
    In `firestarter_app/tests/test_bug_characterization.py`, delete the four-line decorator block at lines 74-77:

    The block to delete is the `@pytest.mark.xfail(...)` decorator whose `reason=` text contains the literal string `BUG: eprom_operations.py:265 conflates EpromOperationError with SerialError; fix lands Phase 42 (ERR-01)`. The block spans the `@pytest.mark.xfail(` line through its closing `)` line (4 lines total: opener, `strict=True,`, `reason="..."`, closer). The `# noqa: E501` marker is part of that block and also deleted.

    The test function definition `def test_eprom_operation_error_not_labeled_as_communication_error(make_comm, fake_serial, caplog):` at line 78 stays. The full docstring and assertion body (lines 79-129) stay byte-identical — they already encode the corrected behavior (asserting `"Communication error" not in any log record`).

    DO NOT:
    - Touch the BUG-1 test (`test_build_arg_flags_force_truthiness_not_existence`) — its xfail was already removed in Phase 41 Plan 41-01
    - Touch the module docstring (lines 1-35) — the documentation of BUG-1 and BUG-2 in the docstring stays verbatim as historical context
    - Touch the `from firestarter.cli_handlers import build_arg_flags` import at line 41 (relocated from `firestarter.main` in Phase 41 Plan 41-04; unchanged this phase)
    - Touch the BUG-2 inline comments inside the test body (lines 86-87 and 121 still reference "BUG: eprom_operations.py:265 — fix lands Phase 42 (ERR-01)" as historical context — these are intentional and stay verbatim; only the `@pytest.mark.xfail(...)` decorator block is deleted)

    Run the test in isolation to confirm it transitions from XFAIL to PASSED (NOT XPASS — XPASS would mean the xfail was still present; PASSED means the marker is gone and the assertion holds).
  </action>
  <verify>
    <automated>cd firestarter_app && pytest tests/test_bug_characterization.py::test_eprom_operation_error_not_labeled_as_communication_error -v</automated>
  </verify>
  <acceptance_criteria>
    - `cd firestarter_app && pytest tests/test_bug_characterization.py::test_eprom_operation_error_not_labeled_as_communication_error -v` exits 0 with status "PASSED" (not XFAIL, not XPASS, not ERROR)
    - `cd firestarter_app && grep -c "@pytest.mark.xfail" tests/test_bug_characterization.py` returns 0 (no xfail markers remain; BUG-1 already removed in Phase 41)
    - `cd firestarter_app && grep -v '^#' tests/test_bug_characterization.py | grep -v '^[[:space:]]*"' | grep -c 'strict=True' | tr -d ' '` returns 0 (no live xfail decorators remain — comment/docstring references don't count; uses grep -v to filter comments per the "Grep gate hygiene" rule)
    - `cd firestarter_app && grep -c "def test_eprom_operation_error_not_labeled_as_communication_error" tests/test_bug_characterization.py` returns exactly 1 (function definition unchanged)
    - `cd firestarter_app && grep -c "def test_build_arg_flags_force_truthiness_not_existence" tests/test_bug_characterization.py` returns exactly 1 (BUG-1 test still present and passing from Phase 41)
    - `cd firestarter_app && grep -c "from firestarter.cli_handlers import build_arg_flags" tests/test_bug_characterization.py` returns exactly 1 (import unchanged from Phase 41 relocation)
    - The historical inline comment at body line ~86 (`# BUG: eprom_operations.py:265 — fix lands Phase 42 (ERR-01)`) stays verbatim — `grep -c 'fix lands Phase 42 (ERR-01)' tests/test_bug_characterization.py` returns at least 1 (the comment is now history, not an active marker)
  </acceptance_criteria>
  <done>
    The BUG-2 test runs cleanly without any xfail marker and PASSES; BUG-1 test (already xfail-free from Phase 41) still passes; both tests are now the live contracts.
  </done>
</task>

<task type="auto">
  <name>Task 3: Verify full suite + lint/type/format gate + Phase 36 snapshots; commit with INTENTIONAL BEHAVIOR CHANGE message</name>
  <files>firestarter_app/firestarter/eprom_operations.py, firestarter_app/tests/test_bug_characterization.py</files>
  <read_first>
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md (D-16 specifies the commit message verbatim; D-15 keeps the CI coverage gate at 50% for this wave — the 70% flip lands in Plan 42-03)
    - .planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md (D-08 py39 style; D-10 mypy watermark contract — strict-overrides addition is Plan 42-03 territory; this wave stays at current watermark)
    - firestarter_app/pyproject.toml (the [tool.ruff] / [tool.mypy] / [tool.coverage.run] config the CI gate enforces; this wave does NOT modify it)
    - firestarter_app/.github/workflows/ci.yml (line 58 — `--cov-fail-under=50` stays in this wave; flip to 70 lands in Plan 42-03 per D-15)
    - firestarter_app/tests/__snapshots__/test_characterization.ambr (the 29 syrupy CLI snapshots — must stay green; the BUG-2 fix only changes a log label which is NOT pinned by these subprocess goldens — per D-04 / D-01)
  </read_first>
  <action>
    Run the full firestarter_app gate locally to confirm Wave 1 has not regressed anything:

    1. `cd firestarter_app && ruff check . && ruff format --check . && python tools/check_mypy_watermark.py` — must exit 0. (The watermark check enforces "no new mypy errors vs Phase 37 baseline"; this wave does NOT add strict overrides so the watermark stays at its current value.)

    2. `cd firestarter_app && pytest -v` — Phase 41 tip was "246 passed + 1 xfail (BUG-2 preserved)". This wave flips that xfail → expect "247 passed + 0 xfail" (or "246 passed + 1 passed (was xfail)" depending on pytest output formatting). The exact floor is one more PASSED than Phase 41 tip and zero xfails. 29 syrupy snapshots in `tests/test_characterization.py` stay green (argparse-form snapshot drift was already absorbed in Phase 41 Plan 41-04; no further drift this wave).

    3. `cd firestarter_app && pytest tests/test_characterization.py -v` — the 29 syrupy subprocess goldens MUST stay green. Any drift here is a regression to fix in-wave, NOT a `--snapshot-update` (per D-04 and the GATE-1.8b ring-fence).

    4. `cd firestarter_app && pytest --cov=firestarter --cov-fail-under=50` — coverage stays above the 50% floor (the flip to 70% lands in Plan 42-03 per D-15; this wave's coverage may rise slightly because the BUG-2 except branch is now exercised by a PASSED rather than XFAIL test, but the floor stays at 50%).

    Then commit BOTH files in a single atomic commit on the `firestarter_app/` submodule's `v1.8-app-cleanup` branch using the SDK helper (worktrees off per `project_v18_phase_execution_mechanics`):

    Subject line: `fix(42-01): split eprom_operations.py BUG-2 except clause (ERR-01)`

    Body MUST contain the literal string `INTENTIONAL BEHAVIOR CHANGE: split eprom_operations.py:265 except clause; EpromOperationError logged as "Programmer error during {op}" (ERR-01, BUG-2 fix)` exactly as specified in CONTEXT D-01/D-16. The line number "265" in the commit message is preserved from CONTEXT.md verbatim even though the runtime line is now 291 — the message references the historical bug-coordinate per the operator-recorded literal in CONTEXT D-01/D-16; reviewers and `grep -r "eprom_operations.py:265"` searches across `.planning/` find the message via this anchor. Full message body:

    `INTENTIONAL BEHAVIOR CHANGE: split eprom_operations.py:265 except clause; EpromOperationError logged as "Programmer error during {op}" (ERR-01, BUG-2 fix). The combined except (SerialError, SerialTimeoutError, EpromOperationError) clause logged all three as "Communication error" — misleading users when the firmware reported a programmer-side failure on a healthy serial link. Splits into two clauses: SerialError|SerialTimeoutError keeps "Communication error"; EpromOperationError logs as "Programmer error". Both still return (False, str(e)); exit codes unchanged (D-04). Flips tests/test_bug_characterization.py::test_eprom_operation_error_not_labeled_as_communication_error from xfail(strict=True) to passing.`

    Do NOT amend prior commits. Do NOT push the commit (sub-repo push is the operator's call per the established branch-promotion pattern).

    NOTE: The meta-repo (`.planning/`) PLAN file commit is handled separately by the orchestrator — this task only commits inside the `firestarter_app/` submodule.
  </action>
  <verify>
    <automated>cd firestarter_app && ruff check . && ruff format --check . && python tools/check_mypy_watermark.py && pytest --cov=firestarter --cov-fail-under=50 -v 2>&1 | tail -10</automated>
  </verify>
  <acceptance_criteria>
    - `cd firestarter_app && ruff check .` exits 0
    - `cd firestarter_app && ruff format --check .` exits 0
    - `cd firestarter_app && python tools/check_mypy_watermark.py` exits 0 (no new mypy errors vs Phase 37 watermark; the watermark value itself is NOT lowered this wave — that's Plan 42-03 territory per D-08)
    - `cd firestarter_app && pytest -v` exits 0; the output shows one PASSED in `test_bug_characterization.py::test_eprom_operation_error_not_labeled_as_communication_error` (NOT XFAIL, NOT XPASS); the total xfail count is 0
    - `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (29 syrupy snapshots green; argparse-form goldens preserved from Phase 41)
    - `cd firestarter_app && pytest --cov=firestarter --cov-fail-under=50` exits 0 (coverage floor preserved; the 70% flip lands in Plan 42-03 per D-15)
    - `cd firestarter_app && firestarter --help` exits 0 (CLI-04 SC#4 smoke test still green)
    - `cd firestarter_app && git log -1 --format=%B` contains the literal string `INTENTIONAL BEHAVIOR CHANGE: split eprom_operations.py:265 except clause; EpromOperationError logged as "Programmer error during {op}" (ERR-01, BUG-2 fix)`
    - `cd firestarter_app && git log -1 --name-only` lists exactly `firestarter/eprom_operations.py` and `tests/test_bug_characterization.py` (no other files touched in this commit)
    - The commit lands on branch `v1.8-app-cleanup` (sub-repo): `cd firestarter_app && git rev-parse --abbrev-ref HEAD` returns `v1.8-app-cleanup`
    - The Phase 41 Plan 41-04 SUMMARY's reported "246 passed + 1 xfail (BUG-2 preserved)" floor moves to "247 passed + 0 xfail" (or higher passed count if Wave 1 of Plan 42-03 lands first — not applicable here since this is the W1 of Phase 42)
  </acceptance_criteria>
  <done>
    Single atomic commit on `firestarter_app/`'s `v1.8-app-cleanup` branch with the required INTENTIONAL BEHAVIOR CHANGE message; suite green with the BUG-2 xfail flipped to passing; lint/format/mypy/coverage gate green; CLI smoke green; Phase 36 syrupy snapshots green.
  </done>
</task>

</tasks>

<verification>
- `cd firestarter_app && ruff check . && ruff format --check . && python tools/check_mypy_watermark.py` exits 0
- `cd firestarter_app && pytest -v` exits 0 with zero xfails (the lone v1.8 xfail, BUG-2, is now PASSED)
- `cd firestarter_app && pytest tests/test_bug_characterization.py::test_eprom_operation_error_not_labeled_as_communication_error -v` exits 0 with PASSED
- `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (29 syrupy snapshots green)
- `cd firestarter_app && pytest --cov=firestarter --cov-fail-under=50` exits 0
- `cd firestarter_app && firestarter --help` exits 0
- Latest commit on firestarter_app `v1.8-app-cleanup` branch contains the literal INTENTIONAL BEHAVIOR CHANGE string for BUG-2 / ERR-01
- No other files in firestarter_app/ modified beyond eprom_operations.py + test_bug_characterization.py
</verification>

<success_criteria>
The BUG-2 portion of ERR-01 is closed. The conflated except clause in `_run_state_machine` is split into two clauses with corrected log labels; EpromOperationError is now logged as "Programmer error during {op}" (not "Communication error"); the BUG-2 xfail flips to PASSED; the change is a single atomic INTENTIONAL BEHAVIOR CHANGE commit on the firestarter_app `v1.8-app-cleanup` branch; full lint/format/type/test/coverage/CLI-smoke gate green. GATE-1.8 (a–e) preserved: wire protocol untouched, CLI surface preserved (no exit-code change per D-04), constants untouched, read path body byte-identical except the load-bearing BUG-2 fix, suite + entry point green.
</success_criteria>

<output>
Create `.planning/phases/42-error-handling-normalization-quality-sweep/42-01-SUMMARY.md` when done.
</output>

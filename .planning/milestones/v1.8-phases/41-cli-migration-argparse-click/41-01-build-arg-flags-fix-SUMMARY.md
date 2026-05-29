---
phase: 41-cli-migration-argparse-click
plan: 01
subsystem: firestarter_app/cli
tags: [cli, bugfix, intentional-behavior-change, gate-1.8b]
dependency_graph:
  requires:
    - "Phase 36 TEST-05 BUG-1 xfail-strict pin (test_bug_characterization.py::test_build_arg_flags_force_truthiness_not_existence)"
    - "Phase 37 ruff + ruff-format + mypy(watermark=44) CI gate on v1.8-app-cleanup"
  provides:
    - "build_arg_flags accepts non-Namespace args objects (PlainArgs fixture) without TypeError — live contract for Click migration in W2-W4"
    - "BUG-1 xfail flipped to passing — suite green substrate for the rest of Phase 41"
  affects:
    - "firestarter_app/firestarter/main.py::build_arg_flags (relocates to cli_handlers.py in W4 per D-16)"
    - "firestarter_app/tests/test_bug_characterization.py::test_build_arg_flags_force_truthiness_not_existence (decorator removed; assertion preserved as live contract)"
tech_stack:
  added: []
  patterns:
    - "getattr(args, key, default) for all optional-attribute reads on the args bag"
    - "hasattr(args, key) for optional-attribute existence gates (replaces `key in args` Namespace-only idiom)"
key_files:
  created: []
  modified:
    - firestarter_app/firestarter/main.py
    - firestarter_app/tests/test_bug_characterization.py
decisions:
  - "Applied Rule 2 deviation: extended the fix to input_enable / chip_disable parallel lines (513, 515) because the plan's stated contract (PlainArgs works end-to-end) cannot hold without them. D-10's parenthetical that those lines `already use getattr correctly` was incorrect about the current source; they used the same buggy `key in args` idiom. Documented in commit body + this summary."
  - "Cleaned up stale `# BUG: main.py:497 — fix lands Phase 41 (CLI-03)` inline markers inside the BUG-1 test docstring + assertion line (Rule 1) since BUG-1 is now fixed and those markers no longer reflect reality. The BUG-2 markers (3 occurrences) are preserved verbatim per the plan's no-touch contract on BUG-2."
metrics:
  duration: "~12 min"
  tasks: 3
  files_modified: 2
  commits: 1
  completed: 2026-05-28
---

# Phase 41 Plan 01: build_arg_flags Truthiness Fix Summary

`build_arg_flags` in `firestarter_app/firestarter/main.py` now uses `getattr(args, key, default)` for all optional-attribute reads and `hasattr(args, key)` for the input_enable / chip_disable gates, replacing the `key in args` argparse-Namespace-only idiom with a contract that holds for any Python object — clearing the path for the Click-provided args objects in Waves 2-4.

## What Changed

### `firestarter_app/firestarter/main.py` (lines 504-518, `build_arg_flags`)

Replaced 3 attribute-existence patterns and 2 attribute-existence gates with attribute-bag-agnostic equivalents:

```python
# Before
def build_arg_flags(args):
    blank_check = getattr(args, "blank_check", True)
    force = args.force if "force" in args else False
    verbose = args.verbose if "verbose" in args else False
    vpe_as_vpp = args.vpe_as_vpp if "vpe_as_vpp" in args else False
    flags = build_flags(blank_check, force, vpe_as_vpp, verbose, skip_erase=not blank_check)
    if "input_enable" in args:
        flags |= 0 if args.input_enable else FLAG_OUTPUT_ENABLE
    if "chip_disable" in args:
        flags |= 0 if args.chip_disable else FLAG_CHIP_ENABLE
    return flags

# After
def build_arg_flags(args):
    blank_check = getattr(args, "blank_check", True)
    force = getattr(args, "force", False)
    verbose = getattr(args, "verbose", False)
    vpe_as_vpp = getattr(args, "vpe_as_vpp", False)
    flags = build_flags(blank_check, force, vpe_as_vpp, verbose, skip_erase=not blank_check)
    if hasattr(args, "input_enable"):
        flags |= 0 if args.input_enable else FLAG_OUTPUT_ENABLE
    if hasattr(args, "chip_disable"):
        flags |= 0 if args.chip_disable else FLAG_CHIP_ENABLE
    return flags
```

This is the INTENTIONAL BEHAVIOR CHANGE for CLI-03 (per D-10): (a) the helper now coerces values to truthiness rather than passing through the raw attribute value, and (b) it accepts non-Namespace args objects (e.g. a plain Python class with no `__contains__`) without raising TypeError. The `argparse.Namespace` callers in W1's surviving argparse path continue to work — `getattr` and `hasattr` work uniformly on `Namespace` because it exposes attributes the normal way; the `__contains__` accident is no longer required for correctness.

### `firestarter_app/tests/test_bug_characterization.py`

- Removed the `@pytest.mark.xfail(strict=True, reason="BUG: main.py:497 uses 'in' not getattr; fix lands Phase 41 (CLI-03)")` decorator from `test_build_arg_flags_force_truthiness_not_existence`. The test assertion (`(flags & FLAG_FORCE) == 0` on a `PlainArgs` object with `force=False`) is unchanged — it was the live contract all along, just pinned as xfail-strict pending the Phase 41 fix.
- Updated the test's docstring + dropped the two stale `# BUG: main.py:497 — fix lands Phase 41 (CLI-03)` inline markers (Rule 1 cleanup — stale comments that no longer match reality now that BUG-1 is fixed).
- BUG-2's `@pytest.mark.xfail(strict=True, ...)` marker on `test_eprom_operation_error_not_labeled_as_communication_error` is untouched — that test stays xfail-strict pinned through Phase 41 per the deferred contract (fix lands Phase 42 ERR-01).

## Verification

- `pytest tests/test_bug_characterization.py::test_build_arg_flags_force_truthiness_not_existence -v` → 1 passed (was XFAIL pre-fix).
- `pytest` (full suite) → 198 passed + 1 xfail (BUG-2 alone) + 29 snapshots green. (Plan estimated 163 passed; actual baseline higher because intervening Phase 36–40 work added tests. Floor satisfied: previous green count + 1 flipped xfail = passing.)
- `pytest tests/test_characterization.py` → 35 passed, 29 syrupy snapshots green — Phase 36 CLI golden snapshots unchanged (GATE-1.8b witness — only `build_arg_flags` semantics changed, end-user CLI surface preserved).
- `ruff check firestarter/ tests/` → 0 violations (CI-exact invocation).
- `ruff format --check firestarter/ tests/` → my 2 files are formatted; 1 pre-existing baseline violation in `tests/test_fw_version_guard.py` from Phase 40 commit `eb1717e` is unchanged (out-of-scope per SCOPE BOUNDARY rule; logged below).
- `python tools/check_mypy_watermark.py` → 38 errors (watermark 44). Gate passes; no new mypy errors introduced.
- Final commit hash on `firestarter_app/` `v1.8-app-cleanup`: `6241dba` — single atomic commit, exactly 2 files (`firestarter/main.py`, `tests/test_bug_characterization.py`); commit body contains the literal `INTENTIONAL BEHAVIOR CHANGE: build_arg_flags "if force in args" corrected to truthiness check (CLI-03)` string required by D-10.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 — Missing critical functionality] Extended fix to input_enable / chip_disable parallel lines**

- **Found during:** Task 1 verification (running `pytest tests/test_bug_characterization.py::test_build_arg_flags_force_truthiness_not_existence` after applying the literal Task 1 edits).
- **Issue:** The plan's Task 1 action literally said "Do NOT touch lines 513-516 (`input_enable`/`chip_disable`) — also already use `getattr` correctly (per the parenthetical note in D-10)." But the current source uses `"input_enable" in args` / `"chip_disable" in args` (the same buggy `key in args` idiom that fails on non-Namespace objects). With only lines 506-508 patched, calling `build_arg_flags(PlainArgs())` still raised `TypeError: argument of type 'PlainArgs' is not iterable` at line 513 — meaning the BUG-1 test would still XFAIL and the must-haves truth `build_arg_flags accepts non-Namespace args objects (e.g. a plain Python class with no __contains__) without raising TypeError — exercised by the Phase 36 PlainArgs fixture` would be unverifiable.
- **Fix:** Converted lines 513 / 515 from `"input_enable" in args` → `hasattr(args, "input_enable")` and `"chip_disable" in args` → `hasattr(args, "chip_disable")`. Same semantic (attribute-existence gate), works on any object.
- **Resolution rule:** Rule 2 (missing critical functionality — the helper's stated contract requires PlainArgs to work end-to-end; the plan's must_haves.truths over-rides the plan's parenthetical claim about the current source).
- **Acceptance-criterion drift:** This made grep counts on lines 8/9 of Task 1's acceptance list (`grep -c '"input_enable" in args'` / `grep -c '"chip_disable" in args'` should each return 1) fall to 0. The semantic intent of those criteria (lines 513/515 left untouched as already-correct) was based on a misreading of the source; the live contract is now what the must_haves.truths required.
- **Files modified:** `firestarter_app/firestarter/main.py` (lines 513, 515).
- **Commit:** `6241dba` (single atomic commit covering both the planned and the deviation edit; documented in commit body).

**2. [Rule 1 — Stale comments after fix] Cleaned up `# BUG:` inline markers in the now-passing BUG-1 test**

- **Found during:** Task 2 acceptance verification (`grep -c "fix lands Phase 41" tests/test_bug_characterization.py` returned 2 instead of the expected 0).
- **Issue:** The plan's Task 2 acceptance criterion 2 expects `grep -c "fix lands Phase 41" tests/test_bug_characterization.py` to return 0 after the decorator removal. But the docstring and the assertion-line inline comment of the BUG-1 test body also carried the marker `# BUG: main.py:497 — fix lands Phase 41 (CLI-03)`. After the fix lands these markers no longer reflect reality (the bug IS fixed; nothing is "landing Phase 41" — it landed).
- **Fix:** Rewrote the test docstring to say "Live contract (BUG-1 fixed Phase 41, CLI-03): ..." and dropped the 2 stale inline `# BUG: main.py:497 — fix lands Phase 41 (CLI-03)` markers. The assertion and the `PlainArgs` fixture body are byte-identical to the pre-fix file.
- **Resolution rule:** Rule 1 (stale-comment correctness — leaving "fix lands Phase 41" markers in a test that now pins the post-fix contract would mislead future readers).
- **Acceptance-criterion drift:** Note that `grep -c "fix lands Phase 42" tests/test_bug_characterization.py` returns 3, not 1 as Task 2's criterion 3 suggested. The other 2 references are in the module docstring (header survey of both bugs) and the BUG-2 test body — both untouched per the no-touch contract on BUG-2. The criterion's intent was satisfied (BUG-2 marker preserved verbatim).
- **Files modified:** `firestarter_app/tests/test_bug_characterization.py` (lines 48-77, BUG-1 test docstring + assertion).
- **Commit:** `6241dba`.

### Out-of-scope items logged (NOT fixed this plan)

Per SCOPE BOUNDARY rule (only auto-fix issues directly caused by the current task's changes):

- `tests/test_fw_version_guard.py` — `ruff format --check` reports it needs reformatting. Introduced by Phase 40 commit `eb1717e` (test added before Phase 40 ruff-format sweep completed). Pre-existing baseline; not touched by this plan. Logging for follow-up: Phase 42 quality sweep (ERR-03 territory).
- `tools/check_dispatch.py` + 6 other `tools/` files — `ruff check tools/` finds 11 violations; `ruff format --check tools/` finds 7 unformatted files. All pre-existing; not in the CI `ruff check firestarter/ tests/` scope; not touched by this plan.
- `firestarter/serial_comm.py`, `firestarter/eprom_operations.py`, `firestarter/firmware.py`, `firestarter/ic_layout.py` — 38 mypy errors at watermark (= 44). All pre-existing; gate passes (no new errors); ring-fenced for v1.9 + Phase 42 type-coverage sweep.

## Self-Check

- [x] `firestarter_app/firestarter/main.py` modified — `git log --oneline -1 firestarter/main.py` → `6241dba` (verified in firestarter_app).
- [x] `firestarter_app/tests/test_bug_characterization.py` modified — same commit.
- [x] Commit `6241dba` exists on branch `v1.8-app-cleanup` of `firestarter_app` (verified via `git rev-parse --abbrev-ref HEAD` + `git log -1`).
- [x] Commit body contains literal `INTENTIONAL BEHAVIOR CHANGE: build_arg_flags "if force in args" corrected to truthiness check (CLI-03)`.
- [x] `pytest tests/test_bug_characterization.py::test_build_arg_flags_force_truthiness_not_existence -v` → PASSED (not XFAIL, not XPASS).
- [x] Full suite green: 198 passed + 1 xfail (BUG-2 only) + 29 syrupy snapshots passed.
- [x] Phase 36 characterization suite (`pytest tests/test_characterization.py`) → 35 passed, 29 snapshots green (GATE-1.8b witness).
- [x] mypy watermark gate (`python tools/check_mypy_watermark.py`) → 38 errors at watermark 44 (passes).
- [x] CI-exact `ruff check firestarter/ tests/` → 0 violations.
- [x] No touches to: serial_comm.py, eprom_operations.py, hardware.py, firmware.py, database.py, chip_resolver.py, eprom_info.py, config.py, exceptions.py, address_parser.py, constants.py, codec.py, frame_parser.py, logging_utils.py, data/chip_database.json, data/pinouts.json, tests/__snapshots__/, the firmware sub-repo (GATE-1.8 a/c/d/e).

## Self-Check: PASSED

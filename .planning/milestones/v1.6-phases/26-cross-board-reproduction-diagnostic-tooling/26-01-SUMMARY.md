---
phase: 26-cross-board-reproduction-diagnostic-tooling
plan: 01
subsystem: host-cli

tags:
  - host-cli
  - consistency-check
  - read-bug-repro
  - v1.6
  - REPRO-03
  - pytest
  - python

# Dependency graph
requires:
  - phase: 26 (CONTEXT.md / RESEARCH.md / PATTERNS.md / VALIDATION.md)
    provides: D-01..D-13 locked decisions, locked operator-method signature,
              monkeypatch-of-operator-internals test pattern, Phase 29
              forward-compat regex contract
provides:
  - "EpromOperator.consistency_check_eprom(...) -> int operator method
    (D-03 signature, reuses _run_state_machine + _main_phase_read_data
    verbatim per reuse-not-duplicate rule)"
  - "firestarter dev consistency-check <chip> CLI subparser with the
    locked D-01 flag set (--runs / --output-dir / --keep-files /
    --no-keep-files / --max-diffs / -q,--quiet / -f,--force)"
  - "8-test pytest suite at firestarter_app/tests/test_consistency_check.py
    (6 D-10 cases + TestDispatchChain integration + stdout regex pin)"
  - "Phase 29 forward-compatibility contract pinned by regex regression
    test (Consistency check: PASS|FAIL, Distinct SHAs, Runs: N=, First
    divergence: offset 0x[0-9A-F]+)"
affects:
  - "Phase 26 Plan 26-02 (operator-on-bench wave -- consumes the new CLI
    via pip install -e . on firestarter_app/v1.6-read-bug)"
  - "Phase 27 (RCA) -- reuses the diagnostic to triangulate the bug"
  - "Phase 29 (post-fix verification) -- this IS the acceptance-gate tool"

# Tech tracking
tech-stack:
  added:
    - "hashlib (stdlib) -- post-read SHA-256 verdict computation"
    - "shutil (stdlib) -- output-dir cleanup on --no-keep-files"
    - "datetime + pathlib (stdlib) -- default output-dir naming"
  patterns:
    - "EpromOperator method returning int directly (not bool->int wrapper)
       -- justified by 3-way verdict (PASS / FAIL / hardware-error)"
    - "monkeypatch-of-operator-internals test pattern for verdict-logic
       tests (stub _operation_context + _run_state_machine, bypass serial)"
    - "Reuse-not-duplicate rule for diagnostics that must exercise the
       suspect code path (D-03)"

key-files:
  created:
    - "firestarter_app/tests/test_consistency_check.py"
  modified:
    - "firestarter_app/firestarter/eprom_operations.py
       (added consistency_check_eprom method + 4 stdlib imports)"
    - "firestarter_app/firestarter/main.py
       (added cc_parser inside create_dev_args; added consistency-check
        dispatch branch inside args.dev_command block)"

key-decisions:
  - "Reused _run_state_machine + _main_phase_read_data + _write_to_file
     closure verbatim (D-03 reuse-not-duplicate) -- the diagnostic
     exercises the exact code path the read bug lives in. No parallel
     read implementation."
  - "consistency_check_eprom returns int directly (0/1/2 per D-05);
     dispatch branch returns the int directly without the bool->int
     wrapper that dev_read_eprom uses. Documented in method docstring
     alongside the check_eprom_id Tuple[bool, Optional[int]] precedent."
  - "Default output_dir uses 'unknown-board' placeholder when no explicit
     --output-dir is given (RESEARCH Pitfall 2 -- avoiding the extra
     handshake round-trip in the default path; Plan 26-02 bench wave will
     pass --output-dir explicitly with the real board name)."
  - "Quiet mode swaps progress_callback to a no-op lambda for the
     duration of the call (restored in finally) rather than touching
     ClassProgressHandler directly (RESEARCH Pitfall 1 -- the state
     machine instantiates its own handler per call)."

patterns-established:
  - "Pattern: operator method with int return for 3-way verdict logic
     (CONTEXT.md D-05). When a single bool cannot express the outcome
     space, return int with grep(1) exit-code semantics (0=success,
     1=expected-failure, 2=hardware-error)."
  - "Pattern: stdout verdict block as forward-compat contract pinned by
     regex regression test. Cross-phase tooling that greps for output
     substrings must pin them via test to prevent drift."

requirements-completed:
  - REPRO-03

# Metrics
duration: ~5 min
completed: 2026-05-21
---

# Phase 26 Plan 01: Cross-board Reproduction & Diagnostic Tooling -- Plan 01 Summary

**`firestarter dev consistency-check <chip>` host CLI diagnostic and `EpromOperator.consistency_check_eprom` operator method shipped on `firestarter_app/v1.6-read-bug`, with 8-test pytest suite (6 D-10 + dispatch integration + stdout regex pin) green and Phase 29 forward-compat contract locked.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-05-21T12:23:29Z
- **Completed:** 2026-05-21T12:27:58Z
- **Tasks:** 2 (test scaffold + GREEN implementation)
- **Files modified:** 3 (1 created, 2 modified inside firestarter_app/ sub-repo)

## Accomplishments

- REPRO-03 closed at the desk-side layer; the diagnostic tool now exists permanently under `dev` per D-01.
- All 6 D-10 locked test cases land as monkeypatch-driven pytest tests with stubbed serial layer (zero hardware required for CI).
- TestDispatchChain integration test verifies the argparse -> dispatch -> operator-method wiring end-to-end (without real serial).
- `test_stdout_verdict_block_format` regex regression test pins the Phase 29 forward-compatibility contract (exit codes 0/1/2, verdict block substrings, --runs >= 2 semantics).
- Full firestarter_app pytest suite stays green (90 passing = 82 prior + 8 new); zero regressions on the pre-existing surface.
- `pip install -e .`-ready dev build for Plan 26-02's operator-on-bench wave.

## Operator-Method Signature (Implemented)

Matches D-03 exactly (parameter names + order + return type):

```python
def consistency_check_eprom(
    self,
    eprom_name: str,
    eprom_data_dict: dict,
    runs: int = 3,
    output_dir: Optional[str] = None,
    keep_files: bool = True,
    max_diffs: int = 10,
    quiet: bool = False,
    operation_flags: int = 0,
) -> int
```

Returns: `0`=PASS, `1`=FAIL (bug detected), `2`=hardware/serial/timeout error.

## Test Output (all 8 GREEN)

```
$ cd firestarter_app && pytest tests/test_consistency_check.py -x
........                                                                 [100%]
8 passed in 0.22s

$ cd firestarter_app && pytest
........................................................................ [ 80%]
..................                                                       [100%]
90 passed in 0.97s
```

Tests (in order):

1. `TestConsistencyCheck::test_all_runs_identical_pass_exit_0` (D-10 #1)
2. `TestConsistencyCheck::test_one_byte_differs_in_run_2_exit_1` (D-10 #2)
3. `TestConsistencyCheck::test_full_scramble_three_distinct_shas` (D-10 #3)
4. `TestConsistencyCheck::test_serial_timeout_exit_2` (D-10 #4; both `(False, msg)` and raised-`EpromOperationError` variants)
5. `TestConsistencyCheck::test_no_keep_files_removes_output_dir` (D-10 #5)
6. `TestConsistencyCheck::test_runs_boundary_rejected` (D-10 #6; runs=1 and runs=0 both exit 2; state machine never invoked)
7. `TestConsistencyCheck::test_stdout_verdict_block_format` (forward-compat regex pin; both PASS and FAIL paths)
8. `TestDispatchChain::test_main_dispatch_invokes_consistency_check` (argparse -> operator wiring)

## CLI Surface (Verified)

```
$ firestarter dev consistency-check --help
usage: firestarter dev consistency-check [-h] [--runs RUNS]
                                         [--output-dir OUTPUT_DIR]
                                         [--keep-files] [--no-keep-files]
                                         [--max-diffs MAX_DIFFS] [-q] [-f]
                                         eprom

positional arguments:
  eprom                 The name of the EPROM.

options:
  -h, --help            show this help message and exit
  --runs RUNS           Number of consecutive reads (default 3; minimum 2).
  --output-dir OUTPUT_DIR
                        Output dir for per-run binaries (default consistency-
                        check-<chip>-<board>-<TS>/).
  --keep-files          Keep per-run binary files after verdict (default).
  --no-keep-files       Delete per-run binaries after verdict.
  --max-diffs MAX_DIFFS
                        Max divergent offsets to print on FAIL (default 10).
  -q, --quiet           Suppress per-run tqdm progress bars (D-11).
  -f, --force           Force read, even if the chip id doesn't match (e.g.
                        Shield-3 missing-chip case).
```

All locked D-01 flags present, including `-f/--force` (Pitfall 5 honored — without it `build_arg_flags` silently defaults `args.force` to False, breaking the Shield-3 missing-chip use case).

## Task Commits

Sub-repo commits on `firestarter_app/v1.6-read-bug` (cut from `beta` at `3.0.0b4`):

1. **Task 1: RED test scaffold** — `c057fe2` (test) — `test(26-01): land RED test scaffold for dev consistency-check`
2. **Task 2: GREEN implementation** — `999c3cc` (feat) — `feat(26-01): implement dev consistency-check (REPRO-03)`

The meta-repo will receive a separate submodule-pointer-bump commit alongside this SUMMARY.md as part of the docs commit.

## Files Created/Modified

**Sub-repo (`firestarter_app/`, branch `v1.6-read-bug`):**

- `firestarter_app/tests/test_consistency_check.py` — **CREATED** (500 lines) — 8 pytest cases covering the 6 D-10 contracts + dispatch integration + Phase 29 forward-compat regex pin.
- `firestarter_app/firestarter/eprom_operations.py` — **MODIFIED** (+200 lines) — added `consistency_check_eprom` method on `EpromOperator` class; added stdlib imports `hashlib`, `shutil`, `datetime.datetime`, `pathlib.Path`.
- `firestarter_app/firestarter/main.py` — **MODIFIED** (+58 lines) — added `cc_parser` subparser inside `create_dev_args` immediately after `addr_parser`; added `elif args.dev_command == "consistency-check":` dispatch branch inside the `args.command == "dev"` block immediately after the `addr` branch.

**Meta-repo (this commit):**

- `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-01-SUMMARY.md` — this file.
- `.planning/STATE.md` — position advanced to Plan 26-02; decisions extracted from this Summary appended to Decisions accumulator.
- `.planning/ROADMAP.md` — Phase 26 progress table row updated.
- `firestarter_app` submodule pointer bumped to `999c3cc`.

## Branch State (Verified)

- `firestarter_app/`: on `v1.6-read-bug` (created from `beta` at this plan's start), HEAD `999c3cc`. Plan 26-01's 2 commits land on this branch.
- `firestarter/` (firmware sub-repo): **untouched** per D-13. Branch is `main` (or whatever was checked out previously); no commits, no edits.
- Meta-repo: on `main` per ROADMAP convention.

## Forward-Compat Contract Surfaces (Locked)

Phase 29 reuses this diagnostic verbatim as the acceptance-gate tool. The following surfaces are LOAD-BEARING and pinned by `test_stdout_verdict_block_format`:

| Surface | Contract |
|---------|----------|
| Exit code 0 | PASS — all N reads byte-identical |
| Exit code 1 | FAIL — bug detected (one or more reads diverge) |
| Exit code 2 | hardware/serial/timeout error (could not complete N reads) |
| Stdout PASS line | exact substring `Consistency check: PASS` |
| Stdout FAIL line | exact substring `Consistency check: FAIL` |
| Distinct SHAs line | regex `Distinct SHAs: \d+` |
| Runs line | regex `Runs: N=\d+` |
| First-divergence line (FAIL only) | regex `First divergence: offset 0x[0-9A-F]+` |
| `--runs N` semantics | N must be >= 2 (smaller values rejected with exit 2 BEFORE any state-machine invocation) |

Any drift between v1.6 and v1.7+ trips this regex test before the Phase 29 milestone gate runs.

## Decisions Made

1. **Default output_dir naming uses `"unknown-board"` placeholder** when no `--output-dir` is provided. Per RESEARCH Pitfall 2 there are three options for the default board-name slot; option (c) — leave it out of the dirname and print board separately in the verdict block — was rejected because operators still want the board grep-friendly in `ls`. Option (a) — extra `FirmwareManager.check_current_firmware()` round-trip — was rejected because the placeholder is harmless when the operator passes `--output-dir` explicitly (which Plan 26-02 will). Pragmatic choice: ship the placeholder default; defer the real-board-name resolution to Plan 26-02 if needed.
2. **Quiet mode implemented by swapping `self.progress_callback`** to a no-op lambda for the duration of the call (restored in `finally`). This avoids touching `ClassProgressHandler` directly (RESEARCH Pitfall 1) and threads cleanly through the existing per-state-machine-invocation handler instantiation.
3. **`_writer` closure uses `address - start` as the seek offset** (defaulted via `_start=cmd_data.get("address", 0)`) so a partial-range read fills the file from byte 0 rather than from the absolute chip address. Mirrors `read_eprom`'s `_write_to_file` semantics for the full-chip case (where `start=0`) and stays correct for the partial case.

## Deviations from Plan

None — plan executed exactly as written. Every locked decision (D-01..D-13) honored; every acceptance criterion (Task 1's 9 grep assertions, Task 2's 11 grep assertions + help-flag count + branch invariant + commit-message keyword) met on first attempt. No auto-fix rules triggered.

## Issues Encountered

None.

## User Setup Required

None — the new code is `pip install -e .`-ready from `firestarter_app/v1.6-read-bug`. No env vars, no external services, no dashboard configuration.

## Self-Check: PASSED

Verification commands (all green):

```bash
# Created file exists
$ [ -f firestarter_app/tests/test_consistency_check.py ] && echo "FOUND" || echo "MISSING"
FOUND

# Sub-repo commits exist on v1.6-read-bug
$ cd firestarter_app && git log --oneline v1.6-read-bug | head -2
999c3cc feat(26-01): implement dev consistency-check (REPRO-03)
c057fe2 test(26-01): land RED test scaffold for dev consistency-check

# Tests green
$ cd firestarter_app && pytest tests/test_consistency_check.py -x 2>&1 | tail -1
8 passed in 0.22s

# Full suite green (no regressions)
$ cd firestarter_app && pytest 2>&1 | tail -1
90 passed in 0.97s

# Branch invariant
$ cd firestarter_app && git rev-parse --abbrev-ref HEAD
v1.6-read-bug

# Firmware sub-repo untouched (D-13)
$ cd firestarter && git status --short
(empty -- no changes)
```

## Next Phase Readiness

- Plan 26-02 (operator-on-bench wave) is ready to start once the operator has hardware available.
- Operator workflow:
  ```bash
  cd /workspaces/firestarter_app
  git checkout v1.6-read-bug
  pip install -e .
  # Then per board:
  firestarter -p /dev/ttyACM0 dev consistency-check SST27SF512 --runs 3 \
      --output-dir .planning/v1.6/uno-SST27SF512-$(date +%Y%m%d-%H%M%S)/
  # ...repeat for /dev/ttyACM1 (leonardo) and /dev/ttyUSB0 (uno328pb).
  ```
- Plan 26-02 deliverable: 3 rows in `.planning/v1.6-EVIDENCE.md` under a `## Phase 26 — Pre-fix Consistency-Check Baseline` section (one per board), populated per the D-08 9-column schema.

---

*Phase: 26-cross-board-reproduction-diagnostic-tooling*
*Plan: 01 (desk-side, autonomous)*
*Completed: 2026-05-21*

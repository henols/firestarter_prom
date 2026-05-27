---
phase: 36-characterization-test-baseline
plan: "03"
subsystem: firestarter_app/tests
tags: [test, snapshot, characterization, cli-surface, golden, syrupy]
dependency_graph:
  requires: ["36-01"]
  provides: ["TEST-01", "GATE-1.8b-surface"]
  affects: ["firestarter_app/tests/test_characterization.py"]
tech_stack:
  added: ["syrupy (snapshot assertions, already installed by 36-01)"]
  patterns: ["subprocess black-box CLI harness", "normalize_output pre-processing", "make_comm/fake_serial in-process happy paths", "syrupy .ambr snapshots"]
key_files:
  created:
    - firestarter_app/tests/test_characterization.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
  modified: []
decisions:
  - "D-01: subprocess harness (not CliRunner) for CLI surface — migration-transparent"
  - "D-02: in-process make_comm/fake_serial for read/write/verify/erase happy paths"
  - "D-05a: normalize_output() pre-processes all subprocess output before == snapshot"
metrics:
  duration: "~20 minutes"
  completed: "2026-05-27"
  tasks_completed: 2
  tasks_total: 2
  snapshots_generated: 29
  test_functions: 35
---

# Phase 36 Plan 03: CLI Characterization Golden Suite Summary

Subprocess black-box CLI surface goldens + in-process E2E happy-path characterizations committed as syrupy snapshots to `tests/__snapshots__/test_characterization.ambr`.

## What Was Built

**File: `firestarter_app/tests/test_characterization.py`** (537 lines, 35 test functions)

### Subprocess CLI Surface Goldens (D-01 design decision)

The `run_firestarter(*args)` helper invokes the installed `firestarter` entry point via `subprocess.run` and passes output through `normalize_output()` before any `== snapshot` assertion.

`normalize_output()` scrubs three non-deterministic content types:
- `Firestarter version: X.Y.Z` → `Firestarter version: <VERSION>`
- `/dev/tty\w+` → `/dev/ttyXXX`
- Absolute paths (`/home/...`, `/workspaces/...`, `/tmp/...`, `/Users/...`) → `<PATH>` with quote/comma boundary stops to handle Python traceback path format

**Snapshot tests committed (29 total):**
- Top-level `--help` and `--version`
- Subcommand `--help` for all 13 subcommands: `read`, `write`, `verify`, `erase`, `blank`, `id`, `list`, `info`, `search`, `fw`, `hw`, `config`, `dev`
- DB-backed `list` (full table), `info W27C512` (current crash behavior pinned — see Deviations), `search W27`, `search ZZZNORESULTS` (no-results path)
- Usage/parse errors: unknown command (exit 2), bad chip name (exit 1), missing `read` eprom arg (exit 2), missing `write` args (exit 2), `--pre --stable` mutex (exit 2), `--pre --firmware-version` mutex (exit 2), bad `--address` (exit 1), bad `--size` (exit 1), `--no-blank-check` polarity surface

### Hardware-Absent Path (D-05b determinism)

Two tests monkeypatch `serial.tools.list_ports.comports` → `lambda: []` so `find_and_connect` raises `ProgrammerNotFoundError` deterministically — identical on CI (no board) and bench (board attached). Tests `read_eprom` and `erase_eprom` both assert `result is False`.

### In-Process Happy Paths (D-02 design decision)

Four tests call `EpromOperator._run_state_machine()` directly with `operator.comm` injected from `make_comm()` and canned firmware frames pre-loaded into `fake_serial`:

| Test | Frame sequence | Assert |
|------|---------------|--------|
| `test_erase_happy_path` | INIT_DONE → MAIN_DONE → END_DONE | `success is True` |
| `test_blank_check_happy_path` | INIT_DONE → MAIN_DONE → END_DONE | `success is True` |
| `test_read_happy_path` | INIT_DONE → DATA_CHUNK(4 bytes) → MAIN_DONE → END_DONE | `success is True`, collected bytes == input |
| `test_write_happy_path` | INIT_DONE → OK_REQ_DATA → MAIN_DONE → END_DONE | `success is True` |
| `test_verify_happy_path` | INIT_DONE → OK_REQ_DATA → MAIN_DONE → END_DONE | `success is True` |

## Deviations from Plan

### Auto-fixed Issues

None — plan executed as specified with one behavioral note (not a deviation).

### Behavioral Note: `info` command crashes in current codebase

The plan specifies snapshotting `info W27C512` as a "DB-backed" test. In the current codebase, **all chips crash** in `firestarter info` with:

```
TypeError: '<=' not supported between instances of 'list' and 'int'
```

at `ic_layout.py:167` (the `vpp-pin` comparison bug). This is a pre-existing bug that affects every chip, not just W27C512.

**Decision (characterization test discipline):** The plan says to pin CURRENT behavior. The snapshot pins the normalized traceback (exit code 1, empty stdout, stderr with `<PATH>`-scrubbed traceback). This gives GATE-1.8b its value: when this bug is fixed in a later phase, the `test_info_known_chip` snapshot will need updating (confirming the fix is visible).

**This is NOT a deviation requiring auto-fix** — fixing `ic_layout.py` would be an unrelated production change outside the scope of plan 36-03 (characterization tests only).

### `normalize_output` path regex improvement

The PATTERNS.md template used `[^\s]+` as the path terminus. In Python traceback format, paths appear as `File "/home/..."` with trailing `",` characters. The original pattern would include the trailing `",` in the `<PATH>` replacement, making the snapshot contain `<PATH>, line 8` rather than `<PATH>", line 8`.

Applied Rule 1 (auto-fix bug): Changed `[^\s]+` to `(?:/[^\s",')]+)+` to stop at quote/comma/paren characters. This produces cleaner, correctly-formatted snapshots.

## Self-Check

**Files exist:**
- `/workspaces/firestarter_app/tests/test_characterization.py` — FOUND
- `/workspaces/firestarter_app/tests/__snapshots__/test_characterization.ambr` — FOUND (1121 lines, 73551 bytes, 29 snapshots)

**Commits exist:**
- `e67839a` — `test(36-03): add CLI characterization golden suite (TEST-01)`
- `b9c9d33` — `test(36-03): commit syrupy snapshot baseline for test_characterization`

**Verification:**
- `pytest tests/test_characterization.py -q` (no `--snapshot-update`): 35 passed, 29 snapshots passed
- `pytest tests/ -q` (full suite): all passed, 29 snapshots passed
- `git check-ignore tests/__snapshots__/test_characterization.ambr` returns exit 1 (not gitignored)
- No `CliRunner` or `click` references in test file

## Self-Check: PASSED

All 35 tests pass. All 29 snapshots match without `--snapshot-update`. No unstable snapshots detected on second run. Snapshot file committed and not gitignored.

## Threat Flags

No new threat surface introduced. Test-only code. `normalize_output()` implements the T-36-03-I information-disclosure mitigation from the plan's threat register: version strings, absolute paths, and `/dev/tty*` names are scrubbed before any snapshot is committed.

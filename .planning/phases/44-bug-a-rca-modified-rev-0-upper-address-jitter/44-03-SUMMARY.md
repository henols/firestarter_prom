---
phase: 44-bug-a-rca-modified-rev-0-upper-address-jitter
plan: "03"
subsystem: host-cli
tags: [host, tdd, read-timing, rca, constants-sync, cli, sweep-harness]
dependency_graph:
  requires: [44-01, 44-02]
  provides: [JSON_KEY_READ_SETTLING_DELAY, JSON_KEY_READ_STROBE_US, consistency_check_eprom-read-timing-params, dev-consistency-check-cli-knobs, sweep_bug_a.py]
  affects:
    - firestarter_app/firestarter/constants.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_eprom_operations.py
    - firestarter_app/tests/test_consistency_check.py
    - .planning/phases/44-bug-a-rca-modified-rev-0-upper-address-jitter/sweep_bug_a.py
tech_stack:
  added: []
  patterns: [constants-sync-rule, click-integer-option, eprom_data_dict-merge, tdd-red-green]
key_files:
  created:
    - .planning/phases/44-bug-a-rca-modified-rev-0-upper-address-jitter/sweep_bug_a.py
  modified:
    - firestarter_app/firestarter/constants.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_eprom_operations.py
    - firestarter_app/tests/test_consistency_check.py
decisions:
  - "Simpler eprom_data_dict merge approach chosen over threading through _operation_context/_setup_operation signature — avoids touching those methods while achieving the same JSON emission"
  - "New params have explicit int annotations in consistency_check_eprom so mypy strict passes on the non-ring-fenced portion of the file"
  - "test_consistency_check.py dispatch integration mock updated to accept new kwargs (Rule 1 — forward-compat fix)"
metrics:
  duration: "~15 minutes"
  completed: "2026-05-29"
  tasks_completed: 3
  files_created: 1
  files_modified: 5
---

# Phase 44 Plan 03: Add Host-Side Read-Timing Knobs + 2D Sweep Harness Summary

Host-side constants, `consistency_check_eprom` signature extension, CLI options, and sweep harness for the Bug A RCA read-timing knob delivery: `JSON_KEY_READ_SETTLING_DELAY = "read-settling-delay"` and `JSON_KEY_READ_STROBE_US = "read-strobe-us"` mirror the firmware PROGMEM strings (Plan 02), threaded through to `--read-settling` / `--read-strobe` CLI options and a stdlib-only 2D sweep harness.

## What Was Built

### Task 1 (RED): Failing pytest suite

Five `test_read_timing_*` tests added to `tests/test_eprom_operations.py`:
- `test_read_timing_settling_key_constant` — pins `JSON_KEY_READ_SETTLING_DELAY == "read-settling-delay"`
- `test_read_timing_strobe_key_constant` — pins `JSON_KEY_READ_STROBE_US == "read-strobe-us"`
- `test_read_timing_settling_emitted_in_command` — asserts settling key appears in JSON when non-zero
- `test_read_timing_strobe_emitted_in_command` — asserts strobe key appears in JSON when non-zero
- `test_read_timing_default_params_absent_from_command` — asserts neither key appears when both params == 0

Seam used: mock `EpromOperator._setup_operation` via `patch.object` to capture the `eprom_data_dict` passed in. Selectable with `pytest -k read_timing`.

RED commit: `69dd108` (submodule)

### Task 2 (GREEN): Implementation

**`constants.py`** — Two new constants added after the `FLAG_*` block, before `CTRL_*`:
```python
JSON_KEY_READ_SETTLING_DELAY = "read-settling-delay"
JSON_KEY_READ_STROBE_US = "read-strobe-us"
```
Sync-rule comment names `json_parser.c (key_read_settling, key_read_strobe)` per CLAUDE.md constants sync rule. Strings byte-identical to Plan 02 firmware PROGMEM keys.

**`eprom_operations.py`** — `consistency_check_eprom` signature extended:
```python
def consistency_check_eprom(
    self,
    ...
    read_settling_us: int = 0,  # address-settling delay (µs; 0=firmware default)
    read_strobe_us: int = 0,    # /CE read-strobe pulse width (µs; 0=firmware default)
) -> int:
```
Knobs merged into `eprom_data_dict` copy before `_operation_context` call (simpler PATTERNS.md alternative — consistent with `pulse-delay` traveling via the DB dict):
```python
if read_settling_us or read_strobe_us:
    eprom_data_dict = dict(eprom_data_dict)
    if read_settling_us:
        eprom_data_dict[JSON_KEY_READ_SETTLING_DELAY] = read_settling_us
    if read_strobe_us:
        eprom_data_dict[JSON_KEY_READ_STROBE_US] = read_strobe_us
```

**`cli_handlers.py`** — Two new Click options on `dev_consistency_check`:
```python
@click.option("--read-settling", "read_settling_us", type=int, default=0, ...)
@click.option("--read-strobe", "read_strobe_us", type=int, default=0, ...)
```
Both threaded to `consistency_check_eprom(...)` call-site.

GREEN commit: `6dc1219` (submodule)

**Verification:**
- `pytest -k read_timing`: 5/5 PASS
- `firestarter dev consistency-check --help`: `--read-settling` and `--read-strobe` listed
- `ruff check / ruff format --check`: all clean on modified files
- `mypy firestarter/cli_handlers.py`: Success (cli_handlers.py is one of 8 strict modules)
- Full suite: 387 passed (up from 382), coverage 70.89% (above 70% floor)

### Task 3: 2D Sweep Harness

**`sweep_bug_a.py`** — stdlib-only (subprocess, csv, sys, hashlib, pathlib) bench script:
- Grid: `SETTLING_VALUES = [0, 3, 10, 25, 50, 100]` × `STROBE_VALUES = [0, 3, 10, 25, 50]` µs (30 points)
- Calls `firestarter -p <PORT> dev consistency-check <CHIP> --runs 5 -q --read-settling <s> --read-strobe <t>` per point
- Writes `sweep-grid.csv` with columns: `settling_us, strobe_us, exit_code, stdout_tail`
- `compare_to_baseline(new_dir)` helper byte-compares against Phase 29 v2 reference dir (D-11)
- D-05 invariant stated verbatim in docstring: chip stays seated, NO re-flash, NO reseat
- No `firestarter fw` / `pio run -t upload` invocations (D-05 sideload prohibition)
- PORT and CHIP parameterized via argv; usage: `python sweep_bug_a.py /dev/ttyACM1 W27C512`

Commit: `156be60` (meta repo)

## Firmware-Host Key Match (T-44-03 Threat Mitigation)

| Host constant | Value | Firmware PROGMEM key (json_parser.c) |
|--------------|-------|-------------------------------------|
| `JSON_KEY_READ_SETTLING_DELAY` | `"read-settling-delay"` | `key_read_settling[] = "read-settling-delay"` |
| `JSON_KEY_READ_STROBE_US` | `"read-strobe-us"` | `key_read_strobe[] = "read-strobe-us"` |

Byte-identical match confirmed. Test `test_read_timing_settling_key_constant` and `test_read_timing_strobe_key_constant` pin this invariant.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `test_main_dispatch_invokes_consistency_check` mock missing new kwargs**
- **Found during:** Task 2 (GREEN — full suite run)
- **Issue:** `TestDispatchChain.test_main_dispatch_invokes_consistency_check` in `tests/test_consistency_check.py` monkeypatches `consistency_check_eprom` with a `fake_method` that does not accept `read_settling_us` / `read_strobe_us`. When the CLI calls `consistency_check_eprom(..., read_settling_us=0, read_strobe_us=0)`, the mock raises `TypeError: fake_method() got an unexpected keyword argument 'read_settling_us'`.
- **Fix:** Added `read_settling_us=0` and `read_strobe_us=0` parameters to `fake_method` and recorded them in the `captured` dict.
- **Files modified:** `firestarter_app/tests/test_consistency_check.py`
- **Commit:** `6dc1219`

## TDD Gate Compliance

RED gate: commit `69dd108` — 4 FAILED tests (ImportError on missing constants + TypeError on unexpected kwargs). Tests selectable via `pytest -k read_timing`. All 5 tests present.

GREEN gate: commit `6dc1219` — all 5 `test_read_timing_*` tests PASS; 387 total tests pass; coverage 70.89% ≥ 70% floor.

No REFACTOR commit needed (implementation was clean on first pass; Rule 1 fix folded into GREEN commit along with implementation).

## Threat Coverage

**T-44-03 (Tampering — constants drift):** MITIGATED. `test_read_timing_settling_key_constant` and `test_read_timing_strobe_key_constant` assert the host JSON keys equal the firmware PROGMEM strings. The sync-rule comment in constants.py names the firmware source file.

**T-44-01 (Tampering — unbounded values):** TRANSFERRED to firmware (Plan 02 cap at 1000µs). Host passes through unbounded by design (dev tool); bounding enforced firmware-side.

**T-44-SC (Package installs):** ACCEPTED. No new packages — sweep harness stdlib-only; no new host deps.

## Known Stubs

The `PORT = "/dev/ttyACM1"` constant in `sweep_bug_a.py` is a default placeholder — it is intentional and documented with a warning in the script. The operator must confirm the actual port at task start (D-09). This does NOT prevent the plan's goal (the sweep harness is ready to run at the bench once the operator provides the port).

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries. The two new JSON fields extend the existing locally-trusted serial-protocol surface (operator bench hardware only).

## Self-Check: PASSED

Files:
- `/workspaces/firestarter_app/firestarter/constants.py` — FOUND (contains `JSON_KEY_READ_SETTLING_DELAY`)
- `/workspaces/firestarter_app/firestarter/eprom_operations.py` — FOUND (contains `read_settling_us`)
- `/workspaces/firestarter_app/firestarter/cli_handlers.py` — FOUND (contains `--read-settling`)
- `/workspaces/firestarter_app/tests/test_eprom_operations.py` — FOUND (contains `test_read_timing_`)
- `/workspaces/.planning/phases/44-bug-a-rca-modified-rev-0-upper-address-jitter/sweep_bug_a.py` — FOUND

Commits:
- `69dd108` (submodule) — test(44-03): add failing read-timing host param tests
- `6dc1219` (submodule) — feat(44-03): expose read-timing knobs on consistency-check
- `156be60` (meta) — feat(44-03): add Bug A 2D sweep harness

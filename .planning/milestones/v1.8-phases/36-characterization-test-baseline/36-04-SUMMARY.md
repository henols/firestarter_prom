---
phase: 36-characterization-test-baseline
plan: "04"
subsystem: firestarter_app/tests
tags: [testing, characterization, xfail, database, bug-pin]
dependency_graph:
  requires: ["36-01"]
  provides: ["TEST-03", "TEST-05"]
  affects: ["Phase 41 CLI-03 (must remove BUG-1 xfail)", "Phase 42 ERR-01 (must remove BUG-2 xfail)"]
tech_stack:
  added: []
  patterns:
    - "EpromDatabase(skip_local_override=True) construction seam"
    - "pytest.mark.xfail(strict=True) as enforced deferred-fix tripwire"
    - "caplog fixture to assert log-level behavior (comm-error bug)"
key_files:
  created:
    - firestarter_app/tests/test_eprom_database.py
    - firestarter_app/tests/test_bug_characterization.py
  modified: []
decisions:
  - "caplog used to assert log message content for BUG-2 (comm-error bug surfaces in logger, not returned value)"
  - "Single-line @pytest.mark.xfail(strict=True, ...) required for grep-based validation script"
  - "AM2716 chosen as second chip for DIP24 pin-translation tests (24-pin UV-EPROM with static-high and vpp-pin in bus-config)"
metrics:
  duration: "~15 minutes"
  completed: "2026-05-27"
  tasks_completed: 2
  files_created: 2
---

# Phase 36 Plan 04: EpromDatabase Unit Tests and Bug Characterization Summary

EpromDatabase unit tests (TEST-03) and two xfail(strict=True) bug pins (TEST-05) for the build_arg_flags force bug and the comm-error/operational-error conflation bug.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | EpromDatabase unit tests (TEST-03) | d3a32ad | tests/test_eprom_database.py (+243 lines) |
| 2 | Bug characterization xfail tests (TEST-05) | 81322cb | tests/test_bug_characterization.py (+130 lines) |

## TEST-03: EpromDatabase Unit Tests

`tests/test_eprom_database.py` — 22 tests covering three D-07 surfaces:

**1. `get_eprom` (7 tests):**
- W27C512 found in packaged DB, `memory-size == 65536` (64KB), `pin-count == 28`, `bus-config` present
- Unknown chip returns `None`
- AM2716 (24-pin, 2KB) found with correct pin-count and memory-size

**2. `convert_to_programmer` (5 tests):**
- `bus-config` key present in output
- `memory-size` in programmer config equals chip size (65536 for W27C512)
- All required firmware keys present: `memory-size`, `type`, `algorithm`, `pin-count`, `vpp_mv`, `flags`
- Empty/None input returns `{}`
- `bus-config.bus` is a non-empty list of RURP line numbers

**3. DIP->RURP pin translation (8 tests):**
- DIP28 W27C512: 16 address lines, all are valid RURP line numbers from `pin_conversions[28]`
- DIP28_27512 pinout maps address pins to contiguous RURP lines 0-15
- DIP24 AM2716: 11 address lines (2^11 = 2KB)
- DIP24_2716 has `vpp-pin` and `static-high` (with RURP line 13) in bus-config
- `pin_conversions[28]` spot-check: pin 10 -> RURP 0 (A0), pin 1 -> RURP 15 (A15)
- Unknown pinout key returns `None`

**Construction seam (2 tests):**
- `EpromDatabase(skip_local_override=True)` constructs without error, yields non-empty proms/pin_maps
- `EpromDatabase(skip_local_override=False)` constructs without error (production merge path)
- Two instances are independent objects (de-singleton verified)

All 22 tests use `EpromDatabase(skip_local_override=True)` in data-asserting tests. No bare `EpromDatabase()` call in test code. No `find_and_connect` or serial I/O.

## TEST-05: Bug Characterization xfail Tests

`tests/test_bug_characterization.py` — 2 xfail(strict=True) tests:

**BUG-1: `build_arg_flags` force attribute-vs-truthiness bug (Phase 41 CLI-03)**

```python
@pytest.mark.xfail(strict=True, reason="BUG: main.py:497 uses 'in' not getattr; fix lands Phase 41 (CLI-03)")
def test_build_arg_flags_force_truthiness_not_existence():
```

- `class PlainArgs` with `force = False` (no `__contains__`)
- Current code: `"force" in args` raises `TypeError: argument of type 'PlainArgs' is not iterable`
- Test fails (TypeError) -> XFAIL -> suite green
- After Phase 41 fix (`getattr(args, "force", False)`): test passes -> XPASS -> `strict=True` fails suite

**BUG-2: EpromOperationError mislabeled as "Communication error" (Phase 42 ERR-01)**

```python
@pytest.mark.xfail(strict=True, reason="BUG: eprom_operations.py:265 conflates EpromOperationError with SerialError; fix lands Phase 42 (ERR-01)")
def test_eprom_operation_error_not_labeled_as_communication_error(make_comm, fake_serial, caplog):
```

- Feeds `MSG_ERR_SETUP` frame via `fake_serial`; INIT phase raises `EpromOperationError`
- Uses `caplog` to capture `EpromOperator` logger output at `ERROR` level
- Asserts: no log record contains "Communication error" (corrected behavior)
- Current code: `except (SerialError, SerialTimeoutError, EpromOperationError)` logs all as "Communication error during ..."
- Test fails (assertion fails) -> XFAIL -> suite green
- After Phase 42 fix (split except clause): test passes -> XPASS -> `strict=True` fails suite

## Verification Results

```
pytest tests/test_eprom_database.py -q    -> 22 passed
pytest tests/test_bug_characterization.py -rxX -q -> 2 xfailed
pytest tests/ -q                          -> 162 passed, 2 xfailed in 13.87s (exit 0)
```

All three verification commands exit 0. Both bug tests report as `XFAIL` (not XPASSED, not FAILED) — bugs confirmed present.

## Deviations from Plan

**1. [Rule 1 - Adjustment] caplog approach for BUG-2**

The plan described asserting that the "surfaced result is an operational error (message does NOT contain 'Communication error')". In practice, `_run_state_machine` returns the `EpromOperationError` message string directly ("Programmer error during init: Setup error") which never contains "Communication error". The bug only manifests in the `logger.error()` call. The test correctly uses `caplog` to capture the logger output and asserts `"Communication error"` is absent from log records — which matches the corrected behavior intent from RESEARCH § Comm-Error Bug Exact Mechanism.

**2. [Rule 1 - Adjustment] Single-line xfail decorator**

The initial implementation used multi-line `@pytest.mark.xfail(\n    strict=True,\n    ...)` decorator style. The plan's verification script uses `grep 'xfail(strict=True'` which requires the string on a single line. Adjusted to single-line decorator format.

## Self-Check: PASSED

- FOUND: /workspaces/firestarter_app/tests/test_eprom_database.py
- FOUND: /workspaces/firestarter_app/tests/test_bug_characterization.py
- FOUND commit d3a32ad: test(36-04): add EpromDatabase unit tests (TEST-03)
- FOUND commit 81322cb: test(36-04): pin two latent bugs as xfail(strict=True) (TEST-05)
- Full suite: 162 passed, 2 xfailed (exit 0)
- `main.py`, `eprom_operations.py`, `database.py` unmodified

## Threat Flags

No new threat surface introduced. Both files are test-only additions. The xfail(strict=True) mechanism is itself the T-36-04-R repudiation control — it self-enforces removal of deferred-fix markers when Phases 41/42 land their fixes.

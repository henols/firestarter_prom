---
phase: 26-cross-board-reproduction-diagnostic-tooling
reviewed: 2026-05-21T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - firestarter_app/firestarter/main.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/tests/test_consistency_check.py
findings:
  critical: 0
  warning: 4
  info: 5
  total: 9
status: has_warnings
---

# Phase 26: Code Review Report

**Reviewed:** 2026-05-21
**Depth:** standard
**Files Reviewed:** 3
**Status:** has_warnings

## Summary

Phase 26 Plan 26-01 lands the `firestarter dev consistency-check <chip>` host CLI diagnostic plus its 8-test pytest suite. Verified locked acceptance criteria pass: D-03 reuse-not-duplicate is met (`main_phase_handler=self._main_phase_read_data` appears in both `read_eprom` AND `consistency_check_eprom` — 2 occurrences in eprom_operations.py + 1 in `dev_read_eprom` for 3 total; the test suite verifies the diagnostic exercises the production read path verbatim); D-02 passive is honored (no `COMMAND_WRITE` reference in `consistency_check_eprom`); D-05 exit codes are wired correctly (0=PASS, 1=FAIL, 2=hardware-error — at least 4 `return 2` paths exist for the various hardware-error states); `-f/--force` is declared on `cc_parser` (RESEARCH Pitfall 5 honored); and `test_stdout_verdict_block_format` regex-pins the Phase 29 forward-compat contract surfaces. All 8 tests pass locally; full suite stays green.

The findings below are quality and robustness defects — none are security issues and none invalidate the Phase 26 contract. The two highest-impact items are the FAIL-without-divergence-detail edge case (WR-01) and the hardcoded `Board: unknown-board` cosmetic bug (WR-02 — bench-confirmed on both Uno and Leonardo during Plan 26-02). Both should be addressed before Phase 29 acceptance gates rely on operator-readable diagnostic output, but neither blocks the v1.6 gate as currently defined (Phase 29 gates on `exit 0`, which is unaffected).

## Critical Issues

_None._

## Warnings

### WR-01: FAIL verdict can suppress all divergence detail when `run_01.bin` and `run_02.bin` are byte-identical but a later run differs

**File:** `firestarter_app/firestarter/eprom_operations.py:566-593`
**Issue:** The divergence-detail block compares ONLY `run_01.bin` against `run_02.bin`. If `distinct = sorted({r[1] for r in results})` has length > 1 (FAIL) because run_03 (or later) diverges, but run_01 and run_02 happen to be byte-identical, `diff_offsets` is `[]`, and the `if diff_offsets:` guard silently skips the entire divergence-detail block. Operator sees `Consistency check: FAIL` and `Distinct SHAs: 2` but no `First divergence:`, no `Total divergent bytes`, no `First M divergent offsets`. For Phase 27 RCA, the missing divergence offset is the load-bearing forensic datum. This also means the `test_stdout_verdict_block_format` FAIL regex (`First divergence: offset 0x[0-9A-F]+`) would silently fail to fire on this real-world scenario — the test only covers the case where run_01 vs run_02 diverges by construction.
**Fix:**
```python
if exit_code == 1:
    # Find the FIRST pair of runs whose SHAs differ, not just run_01 vs run_02.
    diverging_pair = None
    for a in range(len(results)):
        for b in range(a + 1, len(results)):
            if results[a][1] != results[b][1]:
                diverging_pair = (results[a][0], results[b][0])
                break
        if diverging_pair:
            break
    if diverging_pair:
        ai, bi = diverging_pair
        run_a_bytes = (output_path / f"run_{ai:02d}.bin").read_bytes()
        run_b_bytes = (output_path / f"run_{bi:02d}.bin").read_bytes()
        cmp_len = min(len(run_a_bytes), len(run_b_bytes))
        diff_offsets = [o for o in range(cmp_len) if run_a_bytes[o] != run_b_bytes[o]]
        # ... existing print logic, but label "run_X vs run_Y" instead of hardcoding "run_1 vs run_2"
```
Also add a third pytest case to `test_stdout_verdict_block_format` (or a new test) that exercises payloads `[p1, p1, p2]` and asserts the divergence-detail block IS printed.

---

### WR-02: Hardcoded `Board: unknown-board` in verdict block — bench-confirmed cosmetic regression

**File:** `firestarter_app/firestarter/eprom_operations.py:560`
**Issue:** The verdict block prints `Board: unknown-board` as a literal string. The plan's 26-01-SUMMARY.md §"Decisions Made" #1 acknowledges this as a pragmatic deviation from RESEARCH Pitfall 2's recommended Option (a) — but the bench wave (Plan 26-02) confirmed this surfaces as `Board: unknown-board` on real hardware regardless of board (Uno + Leonardo both showed it). The board name is available via `FirmwareManager(self.config).check_current_firmware()` (firestarter_app/firestarter/firmware.py:80-130) which already runs as a side effect of any successful operation. Operators reading evidence files cannot grep-distinguish Uno vs Leonardo vs uno328pb rows without the port string alone — fragile because ports rotate.
**Fix:**
```python
# After the run loop (we know at least one run succeeded), resolve the board name.
board = "unknown-board"
try:
    from firestarter.firmware import FirmwareManager
    fw_mgr = FirmwareManager(self.config)
    _, _, resolved_board = fw_mgr.check_current_firmware()
    if resolved_board:
        board = resolved_board
except Exception:  # noqa: BLE001 — best-effort board resolution; non-fatal
    pass

print(f"Chip: {eprom_name}  Board: {board}  Port: {port}")
```
Alternatively, capture board from the firmware handshake side-channel that already runs inside `SerialCommunicator.find_and_connect` and persist it onto `self.comm` or `self.config` so a second round-trip is unnecessary.

---

### WR-03: Operator state mutation (`self.progress_callback`) for the duration of `--quiet` is not thread-safe / re-entrant-safe

**File:** `firestarter_app/firestarter/eprom_operations.py:472-474, 600-603`
**Issue:** `consistency_check_eprom` mutates `self.progress_callback` on the operator instance when `quiet=True`, then restores it in `finally`. If any other code path holds a reference to the same `EpromOperator` instance and inspects `progress_callback` during the call (e.g. a logging handler, a parallel test, or a future GUI thread), it sees the no-op lambda. This is not a current-day bug because the CLI uses a fresh `EpromOperator` per invocation, but it's a latent re-entrancy hazard documented as a "pattern" in the SUMMARY.md — it shouldn't be elevated to canonical practice without warning.
**Fix:** Prefer thread-of-control isolation. The simpler/cleaner fix is to thread `quiet` (or a no-op `progress_callback` override) explicitly through `_run_state_machine` rather than mutating instance state:
```python
# Option A: param-thread the no-op
is_ok, _ = self._run_state_machine(
    op_name,
    main_phase_handler=self._main_phase_read_data,
    ...,
    progress_callback_override=(lambda *a, **kw: None) if quiet else None,
)
```
Or, if the existing `_run_state_machine` signature must stay locked, document this in the method docstring as "non-reentrant" so callers know. The current implementation is functionally correct but the pattern is brittle.

---

### WR-04: `total_size` is dead code

**File:** `firestarter_app/firestarter/eprom_operations.py:491, 545`
**Issue:** `total_size = 0` is initialized then reassigned each iteration (`total_size = bytes_written`) but never read. This is documented dead code — should either be removed or used (e.g. in the verdict block as `Total bytes per run: <size>`, which would actually be useful operator info).
**Fix:** Either delete the variable:
```python
# Delete line 491 and line 545
```
Or surface it in the verdict block (preferred — adds a tiny bit of useful info):
```python
print(f"Bytes per run: {results[0][2]}")  # all runs same size by construction
```

## Info

### IN-01: Bench-observed `Board: unknown-board` documented in summary but not flagged as a known limitation in the operator-facing help text

**File:** `firestarter_app/firestarter/main.py:432-481`
**Issue:** The `cc_parser` help text doesn't mention that `Board:` will currently always print `unknown-board`. Operators running the diagnostic for the first time will be confused. While WR-02 is the right long-term fix, in the interim a brief note in the `--output-dir` help text or the parser's `description` would surface the limitation.
**Fix:** Either implement WR-02 (preferred) or add to `cc_parser.add_parser(..., epilog="Note: 'Board:' is currently printed as 'unknown-board'; use --output-dir to encode the board manually.")`.

---

### IN-02: Defensive `hasattr(self.config, "get_value")` guard is dead code

**File:** `firestarter_app/firestarter/eprom_operations.py:558`
**Issue:** `port = self.config.get_value("port") if hasattr(self.config, "get_value") else "?"`. `self.config` is typed `ConfigManager` (`__init__` line 142), which defines `get_value` at config.py:127. The guard is unreachable defensive code that suggests uncertainty about the contract; either remove it or replace with a proper type-narrowed call.
**Fix:**
```python
port = self.config.get_value("port", default="?")
```

---

### IN-03: `args.command == "dev"` dispatch silently falls through to `return 0` when no `args.dev_command` branch matches

**File:** `firestarter_app/firestarter/main.py:854-924`
**Issue:** The `elif args.command == "dev":` block has 4 inner branches (`read` / `reg` / `addr` / `consistency-check`). If a future `dev_command` slips in without a matching `elif`, control falls through to `return 0` at line 924, silently reporting success on an unhandled command. Argparse `required=True` on `dev_command` makes this unreachable in practice today, but the trapdoor is fragile to future edits. The pre-existing `elif args.command == "dev":` block already had this property — Plan 26-01 inherits it rather than introducing it.
**Fix:** Add a defensive trailing else:
```python
elif args.command == "dev":
    if args.dev_command == "read":
        ...
    elif args.dev_command == "consistency-check":
        ...
    else:
        logger.error(f"Unknown dev subcommand: {args.dev_command}")
        return 2
```

---

### IN-04: Empty output directory leaked when a hardware error aborts the run loop

**File:** `firestarter_app/firestarter/eprom_operations.py:487, 507/527/535/539`
**Issue:** `output_path.mkdir(parents=True, exist_ok=True)` creates the directory before the run loop starts. If any of the `return 2` paths fire (lines 507, 527, 535, 539), the directory has been created but is empty (or has at most one `run_NN.bin`). With `keep_files=True` (default), this leaves orphan empty dirs accumulating in the operator's working directory across failed retries. Minor but operator-visible.
**Fix:** Either defer `mkdir` until just before the first write, or add cleanup on the hardware-error paths:
```python
except EpromOperationError as e:
    logger.error(f"Run {i}: {e}")
    # Best-effort cleanup on hardware error so retries don't accumulate orphan dirs.
    if i == 1 and not list(output_path.iterdir()):
        shutil.rmtree(output_dir, ignore_errors=True)
    return 2
```

---

### IN-05: `_writer` closure default-arg pattern is subtle and undocumented

**File:** `firestarter_app/firestarter/eprom_operations.py:510-516`
**Issue:** The closure is written as `def _writer(address, data_chunk, _fh=fh, _start=cmd_data.get("address", 0)):` — using default args to capture loop-iteration variables. This is a Python-idiomatic late-binding workaround, but the comment doesn't explain it. A future maintainer reading the code may "fix" the perceived redundancy by removing `_fh=fh` and reintroduce the late-binding bug (where `_writer` captures whatever `fh` happens to be at call time, not the per-iteration handle). This isn't a defect today — the inner closure is consumed inside the same iteration so `fh` would point to the right handle anyway — but the pattern protects against a refactor that hoists `_writer` outside the loop.
**Fix:** Either inline the comment about late-binding:
```python
def _writer(address, data_chunk, _fh=fh, _start=cmd_data.get("address", 0)):
    # Default-arg captures (_fh, _start) protect against late-binding if
    # this closure is ever hoisted outside the per-run loop. See PEP 8 + the
    # canonical "lambdas in loops" pitfall.
    _fh.seek(address - _start)
    _fh.write(data_chunk)
```
Or, since this method is small, hoist the writer to a method and pass `fh` + `start_addr` explicitly.

---

_Reviewed: 2026-05-21_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

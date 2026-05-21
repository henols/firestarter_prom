# Phase 26: Cross-board Reproduction & Diagnostic Tooling — Pattern Map

**Mapped:** 2026-05-21
**Files analyzed:** 4 (2 MODIFY, 2 CREATE)
**Analogs found:** 4 / 4 (all exact analogs verified in live source on `v1.6-read-bug` baseline tip)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/firestarter/main.py` (MODIFY: add `cc_parser` subparser + `consistency-check` dispatch branch) | CLI surface (argparse subparser + dispatch elif) | request-response (argparse parses → dispatches to operator method → returns exit code) | `dev read` subparser at `firestarter_app/firestarter/main.py:373-388` + `dev read` dispatch branch at `firestarter_app/firestarter/main.py:800-818` | **exact** — same `subparsers.add_parser` shape, same `db.get_eprom + convert_to_programmer + build_arg_flags + operator.<method>` dispatch shape |
| `firestarter_app/firestarter/eprom_operations.py` (MODIFY: add `EpromOperator.consistency_check_eprom`) | Business logic (operator method orchestrating N read passes) | request-response × N (loop over N → per-iteration: `_operation_context` → `_run_state_machine` → `_main_phase_read_data` → file write + SHA-256) | `EpromOperator.read_eprom` at `firestarter_app/firestarter/eprom_operations.py:391-425` | **exact** — same `_operation_context` + `_run_state_machine(main_phase_handler=self._main_phase_read_data, ...)` + `_write_to_file` closure triple, called N times |
| `firestarter_app/tests/test_consistency_check.py` (CREATE: 6 D-10 cases + optional dispatch + golden-file) | Tests (pytest unit tests with stubbed serial / monkeypatched operator internals) | event-driven (stubbed callback drives the read loop; assertions on exit code + stdout) | `firestarter_app/tests/test_decoder.py::test_chip_read_loop_concatenates_multiple_chunks` at lines 475-543 + `firestarter_app/tests/conftest.py` fixtures `fake_serial` / `make_comm` / `build_frame` at lines 53-146 | **role-match** — `test_decoder.py` drives the read loop manually via `fake_serial.feed(build_frame(...))`; Phase 26 tests monkeypatch `_run_state_machine` directly (one layer higher) but reuse the same conftest fixtures and import shape |
| `.planning/v1.6-EVIDENCE.md` (CREATE: pre-fix baseline section with 9-column row schema per D-08) | Cross-phase evidence (markdown table accreted across Phases 26 → 27 → 28 → 29) | batch (operator/executor appends rows; downstream phases extend with new sections) | `.planning/v1.5-BENCH-RESULTS.md` (summary table + 3-shield A/B/C section + verdict section) + `.planning/v1.3-BENCH-RESULTS.md` (per-chip-per-board markdown table with placeholder rows + multi-section schema) | **exact** — same one-markdown-table-per-section + append-rows-per-(board,chip)-pair + verdict-paragraph-at-end shape |

## Pattern Assignments

### `firestarter_app/firestarter/main.py` (CLI surface — MODIFY)

**Analog:** `firestarter_app/firestarter/main.py` (self-analog — copy from the `dev read` subparser/dispatch chain already in the same file)

**Imports pattern:** No new imports required. `argparse`, `RawTextHelpFormatter`, `logger`, `build_arg_flags`, `db_instance`, `eprom_operator` are already in scope at the insertion sites.

---

**Argparse subparser pattern** (analog: `firestarter_app/firestarter/main.py:373-388` — `read_parser` block inside `create_dev_args`):

```python
# firestarter_app/firestarter/main.py:366-388 — TEMPLATE for cc_parser
def create_dev_args(parser):
    dev_parser = parser.add_parser(
        "dev", help="Debug command for development purposes."
    )

    subparsers = dev_parser.add_subparsers(dest="dev_command", required=True)

    read_parser = subparsers.add_parser(
        "read", help="Reads the content from an EPROM and prints data to console."
    )
    add_eprom_completer(read_parser)
    read_parser.add_argument(
        "-a", "--address", type=str, help="Read start address in dec/hex"
    )
    read_parser.add_argument(
        "-s", "--size", type=str, help="Size of the data to read in dec/hex"
    )
    read_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force read, even if the chip id doesn't match.",
    )
```

**What to copy verbatim:** `subparsers.add_parser(<verb>, help=...)` call; `add_eprom_completer(<parser>)` immediately after; one `.add_argument(...)` block per CLI flag. The new `cc_parser` slots in **after** the `addr_parser` block (last sibling at lines 419-426) but **before** the `def create_oe_ce_args(parser):` definition at line 429 — keeping it inside `create_dev_args`.

**What changes:** Verb = `"consistency-check"`; new flags per D-01 = `--runs` (int, default 3), `--output-dir` (str, default None), `--keep-files`/`--no-keep-files` (paired `dest="keep_files"` BooleanOptionalAction or two `action="store_true"/store_false"` siblings), `--max-diffs` (int, default 10), `-q`/`--quiet` (action="store_true"), plus `-f`/`--force` (matching the `read_parser` precedent for the Shield-3 missing-chip case).

---

**Dispatch branch pattern** (analog: `firestarter_app/firestarter/main.py:799-818` — `dev read` dispatch within `args.command == "dev"` block):

```python
# firestarter_app/firestarter/main.py:799-818 — TEMPLATE for consistency-check dispatch
elif args.command == "dev":
    if args.dev_command == "read":
        full_eprom_data = db_instance.get_eprom(args.eprom)
        eprom_data = None
        if full_eprom_data:
            eprom_data = db_instance.convert_to_programmer(full_eprom_data)
        if not eprom_data:
            logger.error(f"EPROM '{args.eprom}' not found in database.")
            return 1
        return (
            1
            if not eprom_operator.dev_read_eprom(
                args.eprom,
                eprom_data,
                address_str=args.address,
                size_str=args.size,
                operation_flags=build_arg_flags(args),
            )
            else 0
        )
```

**What to copy verbatim:** The `db_instance.get_eprom` → `convert_to_programmer` → `if not eprom_data: logger.error(...); return 1` boilerplate (5 lines exactly). This is repeated identically at lines 800-807 (`dev read`) and 832-838 (`dev addr`).

**What changes:** The `return (1 if not ... else 0)` bool→exit-code wrapper at lines 808-818 is **dropped** — `consistency_check_eprom` returns `int` directly (D-03 + D-05). New branch:

```python
elif args.dev_command == "consistency-check":
    full_eprom_data = db_instance.get_eprom(args.eprom)
    eprom_data = db_instance.convert_to_programmer(full_eprom_data) if full_eprom_data else None
    if not eprom_data:
        logger.error(f"EPROM '{args.eprom}' not found in database.")
        return 1
    return eprom_operator.consistency_check_eprom(
        args.eprom, eprom_data,
        runs=args.runs,
        output_dir=args.output_dir,
        keep_files=args.keep_files,
        max_diffs=args.max_diffs,
        quiet=args.quiet,
        operation_flags=build_arg_flags(args),
    )
```

Slots in **after** the `elif args.dev_command == "addr":` block at line 831-845 — making it the 4th `elif` within the dev-dispatch chain.

---

**Operation-flags pattern** (analog: `firestarter_app/firestarter/main.py:439-451` — `build_arg_flags`):

```python
# firestarter_app/firestarter/main.py:439-451 — REUSED VERBATIM
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
```

**What to copy:** Nothing — call `build_arg_flags(args)` unchanged. **Critical:** the new subparser MUST declare `-f/--force` or `force` falls through to `False` via line 441's `if "force" in args else False` defensive default, breaking the Shield-3 missing-chip use case (RESEARCH Pitfall 5). `--quiet` does NOT thread through `build_arg_flags` — local to the diagnostic.

---

### `firestarter_app/firestarter/eprom_operations.py` (Business logic — MODIFY)

**Analog:** `EpromOperator.read_eprom` at `firestarter_app/firestarter/eprom_operations.py:391-425`

**Imports pattern** (additions to existing import block at top of file):

```python
# ADD to firestarter_app/firestarter/eprom_operations.py top-level imports
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
# `time`, `os`, `logger`, `Optional`, `Tuple`, `Callable`, `COMMAND_READ`,
# `EpromOperationError`, `SerialError`, `SerialTimeoutError`, `ClassProgressHandler`
# are already imported at the top of the file (verified lines 1-30).
```

---

**`_operation_context` + read state machine pattern** (analog: `firestarter_app/firestarter/eprom_operations.py:391-425` — `read_eprom`):

```python
# firestarter_app/firestarter/eprom_operations.py:391-425 — TEMPLATE
def read_eprom(
    self,
    eprom_name: str,
    eprom_data_dict: dict,
    output_file: Optional[str] = None,
    operation_flags: int = 0,
    address_str: Optional[str] = None,
    size_str: Optional[str] = None,
) -> bool:
    with self._operation_context(eprom_name, eprom_data_dict, COMMAND_READ, operation_flags, address_str, size_str) as (cmd_data, _, op_name):
        if not cmd_data: return False

        actual_output_file = output_file or f"{eprom_name.upper()}.bin"
        logger.info(f"Reading EPROM {eprom_name.upper()}, saving to {actual_output_file}")
        start_time = time.time()

        try:
            with open(actual_output_file, "wb") as file_handle:
                def _write_to_file(address, data_chunk):
                    file_handle.seek(address)
                    file_handle.write(data_chunk)

                is_ok, _ = self._run_state_machine(
                    op_name,
                    main_phase_handler=self._main_phase_read_data,
                    start_addr=cmd_data.get("address", 0),
                    end_addr=cmd_data.get("memory-size", 0),
                    process_data_chunk_callback=_write_to_file
                )
            if is_ok:
                logger.info(f"Read complete ({time.time() - start_time:.2f}s). Data saved to {actual_output_file}")
            return is_ok
        except IOError as e:
            logger.error(f"File I/O error with {actual_output_file}: {e}")
            return False
```

**What to copy verbatim** (the load-bearing triple per D-03 reuse-not-duplicate rule):
1. `with self._operation_context(eprom_name, eprom_data_dict, COMMAND_READ, operation_flags, ...) as (cmd_data, _, op_name):` — exact context-manager call shape (lines 400, 437 of the analog file).
2. `if not cmd_data: return ...` early-out (line 401, 438).
3. The `with open(<run_path>, "wb") as file_handle: def _write_to_file(address, data_chunk): file_handle.seek(address); file_handle.write(data_chunk)` inner closure (lines 408-411). The closure name must remain in-scope of the same `open(...)` block.
4. `is_ok, _ = self._run_state_machine(op_name, main_phase_handler=self._main_phase_read_data, start_addr=cmd_data.get("address", 0), end_addr=cmd_data.get("memory-size", 0), process_data_chunk_callback=_write_to_file)` — exact 5-arg call shape (lines 413-419).

**What changes:** Wrap the `with self._operation_context(...)` block in a `for i in range(1, runs + 1):` loop. Per-iteration: vary the output filename (`run_{i:02d}.bin`); add `hashlib.sha256(<run_path>.read_bytes()).hexdigest()` + append `(i, sha, bytes_written)` to a `results` list; on `is_ok=False` return `2` immediately (D-05 + RESEARCH Pitfall 4); on `EpromOperationError` from the context return `2`. After the loop, compute `distinct_shas = len({r[1] for r in results})`; print verdict block (D-04); on FAIL (distinct ≥ 2) compute first-divergence via `next((o for o in range(min(len(b1), len(b2))) if b1[o] != b2[o]), None)` over the run_01.bin / run_02.bin bytes (RESEARCH §"Pattern 2" implementation sketch lines 393-409); if `not keep_files`: `shutil.rmtree(output_dir)`; return `0` (PASS) or `1` (FAIL).

---

**Locked signature** (D-03 — DO NOT alter parameter names or order; tests + dispatch wire to these exact names):

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
) -> int:
    """Run N consecutive read_eprom passes and report SHA-256 divergence.

    Returns:
        0 — all N reads byte-identical (PASS)
        1 — one or more reads diverge (FAIL — bug detected)
        2 — hardware / serial / timeout error (could not complete N reads)

    This is the ONLY EpromOperator method that returns int rather than bool;
    the 3-way verdict (PASS / FAIL / hardware-error) cannot fit in a bool.
    Same exit-code convention as grep(1). Precedent for non-bool return:
    check_eprom_id() returns Tuple[bool, Optional[int]] at line 618.

    Reuses _run_state_machine + _main_phase_read_data verbatim (D-03 reuse-
    not-duplicate rule) — the diagnostic exercises the same code path the
    read bug lives in. Do NOT refactor into a parallel read implementation.
    """
```

---

**Error handling pattern** (analog: `firestarter_app/firestarter/eprom_operations.py:261-263` — `_run_state_machine`'s `try/except`; analog: `firestarter_app/firestarter/eprom_operations.py:423-425` — `read_eprom`'s `except IOError`):

```python
# eprom_operations.py:261-263 — exception → (False, msg) return pattern
except (SerialError, SerialTimeoutError, EpromOperationError) as e:
    logger.error(f"Communication error during {operation_name}: {e}")
    return False, str(e)
```

**What to copy:** The state machine **does not propagate** `SerialError`/`SerialTimeoutError`/`EpromOperationError` to the caller — it catches them at line 261 and returns `(False, str(e))`. `consistency_check_eprom` must check `if not is_ok: return 2` immediately after each `_run_state_machine` call to map the hardware-error signal to exit code 2 (D-05). Additionally wrap the `with self._operation_context(...)` in a `try/except EpromOperationError` block since `_operation_context` itself may raise during `_setup_operation` (line 202).

---

**Progress handler note** (analog: `firestarter_app/firestarter/eprom_operations.py:237` — fresh handler per `_run_state_machine` call):

```python
# eprom_operations.py:237 — _run_state_machine instantiates a fresh handler per call
progress = ClassProgressHandler(self.progress_callback)
```

**What to copy:** Nothing — `_run_state_machine` already instantiates the handler. `consistency_check_eprom` does NOT touch `ClassProgressHandler` directly (RESEARCH Pitfall 1). For `--quiet` mode, swap `self.progress_callback` to a no-op via `prior = self.progress_callback; self.progress_callback = lambda *a, **k: None; try: ...; finally: self.progress_callback = prior`.

---

### `firestarter_app/tests/test_consistency_check.py` (Tests — CREATE)

**Primary analog:** `firestarter_app/tests/test_decoder.py::test_chip_read_loop_concatenates_multiple_chunks` at lines 475-543
**Secondary analog (fixture source):** `firestarter_app/tests/conftest.py` lines 53-146 (`build_frame`, `fake_serial`, `make_comm`)

**Imports pattern** (analog: `test_decoder.py:488-507` — typical test imports):

```python
# firestarter_app/tests/test_decoder.py:488-507 — TEMPLATE
from firestarter.messages import MSG_DATA_SENDING, MSG_MAIN_DONE
from firestarter.eprom_operations import ClassProgressHandler, EpromOperationError
from firestarter.messages import MSG_DATA_CHUNK as _MSG_DATA_CHUNK
```

**New file imports** (mirrors above, plus stdlib + monkeypatch):

```python
import hashlib
import pytest
from contextlib import contextmanager
from pathlib import Path
# Conftest exposes fake_serial, make_comm, build_frame — picked up automatically by pytest.
from firestarter.eprom_operations import EpromOperator, EpromOperationError
from firestarter.config import ConfigManager
```

---

**Stubbed-serial test pattern** (analog: `firestarter_app/tests/test_decoder.py:475-543` — drive the read loop with `build_frame(MSG_DATA_CHUNK, payload)` over `fake_serial.feed(...)`):

```python
# firestarter_app/tests/test_decoder.py:475-543 — TEMPLATE excerpt
def test_chip_read_loop_concatenates_multiple_chunks(self, fake_serial, make_comm):
    from firestarter.messages import MSG_DATA_SENDING, MSG_MAIN_DONE
    comm = make_comm()

    chunk0 = bytes(range(256))        # 0x00..0xFF
    chunk1 = bytes(range(256))[::-1]  # 0xFF..0x00
    chunk2 = bytes([0xAA] * 256)      # all 0xAA

    stream = (
        build_frame(MSG_DATA_SENDING, b"")
        + build_frame(MSG_DATA_CHUNK, chunk0)
        + build_frame(MSG_DATA_CHUNK, chunk1)
        + build_frame(MSG_DATA_CHUNK, chunk2)
        + build_frame(MSG_MAIN_DONE, b"")
    )
    fake_serial.feed(stream)

    # ... drive _main_phase_read_data manually via the get_response loop ...
```

**What to copy:** The `comm = make_comm(); fake_serial.feed(build_frame(MSG_DATA_*, ...)); ...` pattern (lines 490-504). However, for the 6 D-10 cases, the **cleaner pattern** is to monkeypatch one level higher — `EpromOperator._run_state_machine` directly — because the test is about verdict logic, not protocol decoding (RESEARCH §"Pattern 3" line 660 explicitly recommends this).

---

**Monkeypatch-of-operator-internals pattern** (RESEARCH §"Pattern 3" lines 440-479 — the recommended Phase 26 test skeleton):

```python
# firestarter_app/tests/test_consistency_check.py — TEMPLATE for D-10 case #1
class TestConsistencyCheck:
    def test_all_runs_identical_pass_exit_0(self, tmp_path, monkeypatch):
        """D-10 Test 1: stub state machine to return identical 65,536-byte stream → exit 0."""
        from firestarter.eprom_operations import EpromOperator
        from firestarter.config import ConfigManager

        identical_payload = bytes(range(256)) * 256  # 65,536 bytes

        captured_runs = []
        def fake_state_machine(self, op_name, **kwargs):
            cb = kwargs["process_data_chunk_callback"]
            cb(0, identical_payload)
            captured_runs.append(op_name)
            return (True, None)

        from contextlib import contextmanager
        @contextmanager
        def fake_ctx(self, eprom_name, eprom_data_dict, cmd, *a, **kw):
            yield {"address": 0, "memory-size": 65536}, 512, "READ"

        monkeypatch.setattr(EpromOperator, "_run_state_machine", fake_state_machine)
        monkeypatch.setattr(EpromOperator, "_operation_context", fake_ctx)

        op = EpromOperator(ConfigManager())
        rc = op.consistency_check_eprom(
            "TEST_CHIP",
            eprom_data_dict={"memory-size": 65536},
            runs=3,
            output_dir=str(tmp_path / "out"),
            keep_files=True,
        )
        assert rc == 0
        assert len(captured_runs) == 3
        shas = [hashlib.sha256((tmp_path / "out" / f"run_{i:02d}.bin").read_bytes()).hexdigest()
                for i in (1, 2, 3)]
        assert shas[0] == shas[1] == shas[2]
```

**What to copy:** The `monkeypatch.setattr(EpromOperator, "_run_state_machine", fake_state_machine)` + `monkeypatch.setattr(EpromOperator, "_operation_context", fake_ctx)` pair. This is the **cleanest** stub mechanism for tests asserting verdict logic. The `fake_ctx` yields the `(cmd_data, buffer_size, op_name)` triple that `_operation_context` normally yields (analog: `eprom_operations.py:207-223`); `fake_state_machine` invokes the `process_data_chunk_callback` with controlled payloads then returns `(True, None)` (PASS) or `(False, "timeout")` (hardware error) or raises `EpromOperationError` (case #4).

**6 D-10 test cases — variation on the above template:**
1. **All identical** → fake yields same payload all N calls → `assert rc == 0` (above template).
2. **One byte differs in run 2** → fake yields `identical` on calls 1+3, `identical[:0x123] + b'\xff' + identical[0x124:]` on call 2 → `assert rc == 1`, assert stdout contains `"First divergence: offset 0x0123"` and `"Total divergent bytes (run_1 vs run_2): 1 / 65536"`.
3. **Full scramble** → fake yields 3 distinct payloads → `assert rc == 1`, assert stdout contains `"Distinct SHAs: 3"`.
4. **State machine raises EpromOperationError** → `def fake_state_machine(...): raise EpromOperationError("timeout")` (or returns `(False, "timeout")`) → `assert rc == 2`.
5. **`keep_files=False`** → after successful run, `assert not (tmp_path / "out").exists()`.
6. **`--runs 1` / `--runs 0`** → `assert rc == 2`, no monkeypatch needed (returns early before state machine is invoked); assert `"--runs must be >= 2"` in caplog.

---

**Optional 7th test — dispatch chain integration** (RESEARCH §"Open Question Q2" lines 894-899):

```python
# OPTIONAL — TestDispatchChain class
class TestDispatchChain:
    def test_main_dispatch_invokes_consistency_check(self, monkeypatch):
        import argparse
        from firestarter import main as main_mod
        from firestarter.eprom_operations import EpromOperator

        captured = {}
        def fake_method(self, eprom_name, eprom_data_dict, **kwargs):
            captured["eprom_name"] = eprom_name
            captured["kwargs"] = kwargs
            return 0
        monkeypatch.setattr(EpromOperator, "consistency_check_eprom", fake_method)
        # (Also stub db_instance.get_eprom + convert_to_programmer to return a dummy dict.)
        # Then invoke main_mod.main() via sys.argv override and assert captured kwargs match.
```

---

**Optional 8th test — golden-file stdout verdict block format** (RESEARCH §"Validation Architecture — Cross-tool Forward Compatibility" lines 808-819):

```python
# OPTIONAL — guards Phase 29 forward-compat
def test_stdout_verdict_block_format(self, capsys, tmp_path, monkeypatch):
    # ... run consistency_check_eprom with stubbed identical-runs ...
    captured = capsys.readouterr()
    import re
    assert re.search(r"Consistency check: PASS", captured.out)
    assert re.search(r"Distinct SHAs: \d+", captured.out)
    assert re.search(r"Runs: N=\d+", captured.out)
    # On FAIL path (separate test):
    # assert re.search(r"First divergence: offset 0x[0-9A-F]+", captured.out)
```

---

### `.planning/v1.6-EVIDENCE.md` (Cross-phase evidence — CREATE)

**Primary analog:** `.planning/v1.5-BENCH-RESULTS.md` (multi-section accretion file, table + verdict paragraph)
**Secondary analog:** `.planning/v1.3-BENCH-RESULTS.md` (markdown table with placeholder header + per-section comment annotations)

**Header pattern** (analog: `.planning/v1.5-BENCH-RESULTS.md:1-7`):

```markdown
# v1.5 Bench Results

**Milestone:** v1.5 Arduino Uno (ATmega328PB) Board Support
**Bench session:** 2026-05-21 (operator-on-bench, single session)
**Bench host:** `/dev/ttyUSB0` (USB-to-serial adapter) → 328PB-Uno + RURP shield
**Firmware shipped to chip:** `firestarter_uno328pb.hex` v3.0.0b4 (from GitHub Pre-release `henols/firestarter` tag `3.0.0b4`)

## Summary
```

**What to copy:** The `# v<X> <Name>` heading + bolded metadata-key block + `## Summary` section header shape. New file's metadata: `Milestone: v1.6 Fix the Read Bug`, `Phases: 26 (baseline) → 27 (RCA) → 28 (fix) → 29 (post-fix verification)`, `Cross-cutting evidence accretion across all 4 v1.6 phases`.

---

**Section pattern** (analog: `.planning/v1.3-BENCH-RESULTS.md:10-15` — table with placeholder annotation):

```markdown
## Per-Chip-Per-Board Cycle Results (D-08 schema; 14 columns)

| Chip | Board | Date | info | vpp_engaged | chip_id_read | chip_id_db | chip_id_match | blank_pre | write | read | verify | blank_post | log | notes |
|------|-------|------|------|-------------|--------------|------------|---------------|-----------|-------|------|--------|------------|-----|-------|

<!-- Plans 12-01 / 12-02 / 12-03 append one row per (chip, board) pair = 6 rows total when Phase 12 closes. -->
```

**What to copy:** `## <section title> (<schema reference>; <N> columns)` header + the markdown table header row + the `|---|...|---|` separator + an HTML comment annotation indicating which plan/phase appends rows + an empty row beneath the separator to receive append.

---

**3-shield triage table pattern** (analog: `.planning/v1.5-BENCH-RESULTS.md:24-32` — multi-section markdown tables in the same file):

```markdown
## 3-shield A/B/C triage (signal-integrity isolation)

| Shield | Rev | EEPROM hw byte | Bus state | 1KB jitter | 64KB read completes |
|--------|-----|----------------|-----------|------------|---------------------|
| 1 | 2.2 | Rev2 | chip data | 1 byte / 1024 | ✓ (with 57.8% inter-read jitter) |
| 2 | 2.0 | Rev2 | chip data | 2 bytes / 1024 (offsets 0x4F, 0xBB) | ✗ timeout |
| 3 | 0/1.0 + voltage-divider mod | **Rev1** | floating, no chip | 110-124 diff lines × 3 reads | ✗ timeout |
```

**What to copy:** The append-only multi-section structure — each phase or sub-finding gets its own `##` section with its own table. v1.6-EVIDENCE.md will have at least these sections accreting over the milestone:
- `## Phase 26 — Pre-fix Consistency-Check Baseline (YYYY-MM-DD)` (D-08 9-column schema — CREATE here)
- `## Phase 27 — RCA Findings` (appended by Phase 27 plans)
- `## Phase 28 — Fix Commit References` (appended by Phase 28)
- `## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD)` (appended by Phase 29 — same row schema as Phase 26, inverted verdicts)

---

**Phase 26 baseline row schema (D-08 9-column — locked):**

```markdown
## Phase 26 — Pre-fix Consistency-Check Baseline (2026-05-2X)

| Board | Port | Chip | N | SHAs distinct | Divergent bytes (run1 vs run2) | First-diverge offset | Verdict | Log |
|-------|------|------|---|---------------|------------------------------|----------------------|---------|-----|
| uno328pb | /dev/ttyUSB0 | SST27SF512 | 3 | 3 | 37,883 / 65,536 (57.8%) | 0x009E | FAIL (jitter reproduced) | consistency-check-SST27SF512-uno328pb-2026-05-2X-HHMMSS/ |
| uno | /dev/ttyACM0 | <chip> | 3 | TBD | TBD | TBD | TBD | ... |
| leonardo | /dev/ttyACM1 | <chip> | 3 | TBD | TBD | TBD | TBD | ... |
```

(Verbatim from CONTEXT.md §D-08 lines 147-155 — schema is shared across Phase 27/28/29 per D-08 final paragraph.)

---

**Verdict paragraph pattern** (analog: `.planning/v1.5-BENCH-RESULTS.md:34-46` — `## Verdict` section closing the file):

```markdown
## Verdict

**BENCH-01: CLOSED** ✓ — install via `firestarter fw -i --pre` flashed the 328PB-Uno end-to-end...

**Operator authorization** to ship v1.5 with these caveats: confirmed 2026-05-21 ("close the milestone").
```

**What to copy:** The `## Verdict` section as the final section, with per-requirement `**<ID>: <STATUS>** <icon> — <one-paragraph evidence summary>` lines. For Phase 26, the verdict section opens with stubs for REPRO-01 / REPRO-02 / REPRO-03 to be filled by Plan 26-02 after the bench runs complete (REPRO-03 closes on Plan 26-01 merge; REPRO-01/02 close after Plan 26-02 runs).

---

### Plan-26-02 frontmatter pattern (Plan-file analog for the bench-wave plan)

**Analog:** `.planning/phases/12-28-pin-algo-0x07-bench-validation/12-01-PLAN.md:1-71` — the canonical `autonomous: false` operator-on-bench plan structure.

```yaml
# .planning/phases/12-28-pin-algo-0x07-bench-validation/12-01-PLAN.md:1-71 — TEMPLATE
---
phase: 12
plan: 01
type: execute
wave: 1
depends_on:
  - 12-04
files_modified:
  - .planning/v1.3-BENCH-RESULTS.md
  - .planning/v1.3/bench-logs/W27C512-uno-{date}.log
  - .planning/v1.3/bench-logs/W27C512-leonardo-{date}.log
  - .planning/v1.3/scope/uno-vpp-write-{date}.png
  - .planning/v1.3/scope/leonardo-vpp-write-{date}.png
autonomous: false
requirements:
  - BENCH-01
  - PROTO-02
requirements_addressed:
  - BENCH-01
  - PROTO-02
nyquist_compliant: manual-uat
tags:
  - bench-validation
  - W27C512
  - algo-0x07
  - operator-on-bench
  - v1.3

must_haves:
  truths:
    - "Operator completes the D-07 bench cycle (info → vpp/vpe → id → blank → write → read → verify) for W27C512 on Uno, harness emits `All tests passed`, log captured via `tee` per Pattern A."
    - "Operator completes the same D-07 bench cycle for W27C512 on Leonardo, with the second log captured to a `-leonardo-` filename."
    ...
  artifacts:
    - path: ".planning/v1.3/bench-logs/W27C512-uno-{date}.log"
      provides: "Per-cycle tee'd log of the W27C512 Uno harness run; contains `All tests passed` on green, `firestarter id` chip-id line (PROTO-01 evidence row), and verbose-mode breadcrumbs"
      contains:
        - "Eprom: W27C512"
        - "All tests passed"
    ...
  key_links:
    - from: ".planning/v1.3-BENCH-RESULTS.md (W27C512 uno row)"
      to: ".planning/v1.3/bench-logs/W27C512-uno-{date}.log"
      via: "log column cell"
      pattern: "`\\.planning/v1\\.3/bench-logs/W27C512-uno-.+\\.log`"
    ...
---
```

**What to copy verbatim** (for Plan 26-02):
- `type: execute` + `wave: 1` (single-wave operator plan).
- `autonomous: false` — non-negotiable for operator-on-bench plans.
- `nyquist_compliant: manual-uat` — manual UAT is the validation type for bench plans.
- `requirements:` and `requirements_addressed:` as parallel arrays of REPRO-01 / REPRO-02 IDs.
- `tags:` list including `bench-validation`, `operator-on-bench`, milestone tag `v1.6`, requirement-cluster tag `read-bug-repro`, tool tag `consistency-check`.
- `must_haves.truths`: bullet list, each starts with `"Operator runs ..."` quoting the exact CLI invocation the operator types.
- `must_haves.artifacts`: list of `{ path, provides, contains }` triples; `contains` is an array of substrings that must appear in the artifact (used by `gsd-validator`).
- `must_haves.key_links`: list of `{ from, to, via, pattern }` quadruples expressing cross-references between evidence rows and log/photo files (regex-based grep walk).

**What changes for Plan 26-02:** `phase: 26`, `plan: 02`, `depends_on: [26-01]`, `files_modified` enumerates `.planning/v1.6-EVIDENCE.md` + per-board `.planning/v1.6/bench-logs/<chip>-<board>-<TS>.log`, `requirements: [REPRO-01, REPRO-02]`, `truths` rewritten to quote the new `firestarter -p /dev/ttyXXX dev consistency-check <chip> --runs 3 --output-dir .planning/v1.6/...` invocations per board.

---

## Shared Patterns

### EPROM Database Lookup
**Source:** `firestarter_app/firestarter/main.py:800-807` (`dev read` dispatch — the 5-line `db_instance.get_eprom + convert_to_programmer + if not eprom_data` boilerplate)
**Apply to:** The new `consistency-check` dispatch branch in `main.py`.

```python
# firestarter_app/firestarter/main.py:801-807 — verbatim 5-line boilerplate
full_eprom_data = db_instance.get_eprom(args.eprom)
eprom_data = None
if full_eprom_data:
    eprom_data = db_instance.convert_to_programmer(full_eprom_data)
if not eprom_data:
    logger.error(f"EPROM '{args.eprom}' not found in database.")
    return 1
```

### State Machine Invocation (D-03 reuse-not-duplicate)
**Source:** `firestarter_app/firestarter/eprom_operations.py:413-419` (`read_eprom`'s `_run_state_machine` call)
**Apply to:** Each iteration of `consistency_check_eprom`'s `for i in range(N)` loop. **Must NOT be replaced with a parallel read loop** (D-03 + RESEARCH Anti-Patterns).

```python
# firestarter_app/firestarter/eprom_operations.py:413-419 — LOAD-BEARING reuse target
is_ok, _ = self._run_state_machine(
    op_name,
    main_phase_handler=self._main_phase_read_data,
    start_addr=cmd_data.get("address", 0),
    end_addr=cmd_data.get("memory-size", 0),
    process_data_chunk_callback=_write_to_file
)
```

### File-Writer Inner Closure
**Source:** `firestarter_app/firestarter/eprom_operations.py:408-411` (`read_eprom`'s `_write_to_file`)
**Apply to:** Each per-run binary write inside `consistency_check_eprom`. Per-iteration the `file_handle` and `run_path` change; the closure shape is identical.

```python
# firestarter_app/firestarter/eprom_operations.py:408-411 — verbatim closure shape
with open(actual_output_file, "wb") as file_handle:
    def _write_to_file(address, data_chunk):
        file_handle.seek(address)
        file_handle.write(data_chunk)
```

### Hardware-Error → Exit Code 2 Mapping
**Source:** `firestarter_app/firestarter/eprom_operations.py:261-263` (`_run_state_machine`'s exception handler) + D-05 (exit code convention)
**Apply to:** `consistency_check_eprom` immediately after each `_run_state_machine` call.

```python
# After each _run_state_machine call inside consistency_check_eprom:
if not is_ok:
    logger.error(f"Run {i}: hardware/serial error — {msg}")
    return 2  # D-05 exit code 2 (hardware error)
```

### Pytest Fixture Reuse
**Source:** `firestarter_app/tests/conftest.py:122-146` (`fake_serial`, `make_comm`) + `firestarter_app/tests/conftest.py:53-63` (`build_frame`)
**Apply to:** All 6 D-10 test cases. Fixtures are auto-injected by pytest — no import needed. For the operator-method-level tests, `fake_serial` + `make_comm` are not strictly required (monkeypatching `_run_state_machine` is one level higher); but they ARE required for any optional end-to-end test that drives `_main_phase_read_data` through real `comm.get_response()` calls.

### Evidence-File Append-Only Schema
**Source:** `.planning/v1.3-BENCH-RESULTS.md` (table-per-section with placeholder annotation) + `.planning/v1.5-BENCH-RESULTS.md` (Summary + cross-cutting tables + Verdict)
**Apply to:** `.planning/v1.6-EVIDENCE.md` creation in Plan 26-02. Each downstream phase (27/28/29) appends one section; never edits prior sections in place.

---

## Data Flow Diagram

```
[Operator shell: firestarter -p /dev/ttyXXX dev consistency-check <chip> --runs 3]
           │
           ▼
[1] firestarter_app/firestarter/main.py (argparse)
       parser → create_dev_args (line 366) → cc_parser (NEW, after addr_parser block at line 426)
       sets: args.command="dev", args.dev_command="consistency-check",
             args.eprom, args.runs, args.output_dir, args.keep_files,
             args.max_diffs, args.quiet, args.force
           │
           ▼
[2] firestarter_app/firestarter/main.py (dispatch)
       args.command=="dev" block (line 799) →
       elif args.dev_command=="consistency-check": (NEW, after addr branch at line 831)
           full_eprom_data = db_instance.get_eprom(args.eprom)        # database.py:493
           eprom_data = db_instance.convert_to_programmer(full_eprom_data)  # database.py:522
           if not eprom_data: logger.error(...); return 1
           return eprom_operator.consistency_check_eprom(
               args.eprom, eprom_data,
               runs=args.runs, output_dir=args.output_dir,
               keep_files=args.keep_files, max_diffs=args.max_diffs,
               quiet=args.quiet,
               operation_flags=build_arg_flags(args),  # main.py:439
           )
           │
           ▼
[3] firestarter_app/firestarter/eprom_operations.py (operator method — NEW)
       EpromOperator.consistency_check_eprom(...) -> int
           validate runs >= 2 (else return 2)
           resolve output_dir (default consistency-check-<chip>-<board>-<TS>/)
           for i in 1..runs:
               run_path = output_dir / f"run_{i:02d}.bin"
                   │
                   ▼
[4]            with self._operation_context(eprom_name, eprom_data, COMMAND_READ, op_flags) as (cmd_data, _, op_name):
                   # eprom_operations.py:207-223 — opens serial, sets up handshake
                   │
                   ▼
[5]                with open(run_path, "wb") as fh:
                       def _writer(address, data_chunk):
                           fh.seek(address); fh.write(data_chunk)
                       is_ok, _ = self._run_state_machine(
                           op_name,
                           main_phase_handler=self._main_phase_read_data,
                           start_addr=cmd_data["address"],
                           end_addr=cmd_data["memory-size"],
                           process_data_chunk_callback=_writer,
                       )
                       │
                       ▼
[6]                   _run_state_machine (eprom_operations.py:232-265)
                       INIT phase: send_ack + _execute_phase("INIT", progress)  # line 242
                       MAIN phase: send_ack + main_phase_handler(progress, **kwargs)  # line 247
                           │
                           ▼
[7]                      _main_phase_read_data (eprom_operations.py:349-387)
                              while True:
                                  response = self.comm.get_response()  # serial_comm.py
                                  if response.type == "MAIN": break
                                  if response.type == "DATA" and response.payload:
                                      # MSG_DATA_CHUNK — the suspected bug locus
                                      process_data_chunk_callback(start_addr, response.payload)
                                      start_addr += len(payload)
                                      self.comm.send_ack()
                       END phase: _execute_phase("END", progress); send_ack  # line 256-259
                       returns (True, final_msg) — OR (False, str(e)) on exception (line 261-263)
                   │
                   ▼
               if not is_ok: return 2  # D-05 hardware error
               sha = hashlib.sha256(run_path.read_bytes()).hexdigest()
               results.append((i, sha, run_path.stat().st_size))
           # end for loop
           distinct = {r[1] for r in results}
           exit_code = 0 if len(distinct) == 1 else 1  # D-05
           print verdict block + divergence detail (D-04)
           if output_dir under .planning/: append row to v1.6-EVIDENCE.md
           if not keep_files: shutil.rmtree(output_dir)
           return exit_code
           │
           ▼
[8] sys.exit(rc) — bubbled up through main.py's return rc
```

**Links the planner must express in `<read_first>` blocks:**

| Plan | `<read_first>` files |
|------|----------------------|
| 26-01 (desk-side) | `firestarter_app/firestarter/main.py` (lines 366-451 + 799-846); `firestarter_app/firestarter/eprom_operations.py` (lines 200-425); `firestarter_app/tests/conftest.py` (lines 1-146); `firestarter_app/tests/test_decoder.py` (lines 475-543); `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-CONTEXT.md` §`<decisions>` D-01..D-13; `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-RESEARCH.md` §Pattern 1 + Pattern 2 + Pattern 3 + Pitfalls 1-5 + Validation Architecture |
| 26-02 (operator-on-bench) | `.planning/phases/12-28-pin-algo-0x07-bench-validation/12-01-PLAN.md` (frontmatter lines 1-71 — template for operator-on-bench plan structure); `.planning/v1.3-BENCH-RESULTS.md` (row schema reference); `.planning/v1.5-BENCH-RESULTS.md` (multi-section accretion reference); `.planning/todos/pending/large-read-data-jitter-uno328pb.md` (empirical baseline values for the uno328pb row); `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-CONTEXT.md` §D-08 (schema) + §D-09 (plan structure); the artifact `firestarter dev consistency-check --help` of Plan 26-01 (verifies install before bench session starts) |

---

## No Analog Found

All four files have at least a role-match analog. No "no analog found" entries.

| File | Role | Data Flow | Analog Status |
|------|------|-----------|---------------|
| `firestarter_app/firestarter/main.py` (MODIFY) | CLI surface | request-response | EXACT — `dev read` chain |
| `firestarter_app/firestarter/eprom_operations.py` (MODIFY) | Business logic | N × request-response | EXACT — `read_eprom` |
| `firestarter_app/tests/test_consistency_check.py` (CREATE) | Tests | event-driven (stubbed) | ROLE-MATCH — `test_decoder.py` + conftest |
| `.planning/v1.6-EVIDENCE.md` (CREATE) | Cross-phase evidence | batch / append-only | EXACT — v1.5-BENCH-RESULTS.md + v1.3-BENCH-RESULTS.md |

---

## Metadata

**Analog search scope:**
- `/workspaces/firestarter_app/firestarter/` (main.py, eprom_operations.py, serial_comm.py, database.py, firmware.py)
- `/workspaces/firestarter_app/tests/` (conftest.py, test_decoder.py)
- `/workspaces/.planning/` (v1.3-BENCH-RESULTS.md, v1.5-BENCH-RESULTS.md root files)
- `/workspaces/.planning/phases/12-28-pin-algo-0x07-bench-validation/` (12-01-PLAN.md frontmatter for operator-on-bench plan template)

**Files scanned:** 7 source files + 4 .planning files + 1 phase plan = 12 files inspected
**Pattern extraction date:** 2026-05-21
**Pattern-mapper run via:** /gsd:plan-phase 26 (orchestrator-spawned pattern mapper)

## PATTERN MAPPING COMPLETE

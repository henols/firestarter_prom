# Phase 26: Cross-board Reproduction & Diagnostic Tooling — Research

**Researched:** 2026-05-21
**Domain:** Host-side Python CLI diagnostic (firestarter_app sub-repo); read-state-machine reuse; pytest stubbed-serial test harness; operator-on-bench evidence-accretion pattern
**Confidence:** HIGH (every line number, function signature, and existing-pattern claim below was verified against live source files on this branch; no `[ASSUMED]` claims survive the audit)

## Summary

Phase 26 is *plumbing-shaped*, not algorithm-shaped: every architectural decision (D-01..D-13 in CONTEXT.md) is locked, and this research grounds them in the exact file paths, function signatures, and reusable fixtures that the planner will hand to executors. The diagnostic is a thin wrapper around three existing surfaces — `dev` subparser argparse pattern (siblings `dev read` / `dev reg` / `dev addr`), `EpromOperator.read_eprom`'s state-machine orchestration (`_run_state_machine` → `_main_phase_read_data` → process-data-chunk-callback), and the conftest `fake_serial` / `make_comm` fixtures already used by `test_decoder.py::test_chip_read_loop_concatenates_multiple_chunks` to drive the read loop in stubbed mode.

The only divergence from existing `dev` subcommand convention is D-03's `EpromOperator.consistency_check_eprom(...) -> int` returning an integer exit code (0/1/2) instead of the `bool` that `dev_read_eprom` returns. That is justified — a 3-way verdict (PASS / FAIL / hardware-error) cannot fit in a bool — and the planner should document the divergence in the method docstring per the precedent established for `check_eprom_id` (which returns `Tuple[bool, Optional[int]]` — also non-bool for the same reason of needing richer information).

**Primary recommendation:** Plan 26-01 (desk-side) follows the `dev read` chain verbatim — argparse subparser at `main.py:373-388` template, dispatch branch at `main.py:799-818` template, `_operation_context` + `_run_state_machine(main_phase_handler=self._main_phase_read_data, ...)` pattern at `eprom_operations.py:400-419` template. Plan 26-02 (operator-on-bench, `autonomous: false`) mirrors v1.3 Plan 12-01's bench-cycle frontmatter shape verbatim — single-plan-per-session, append rows to `.planning/v1.6-EVIDENCE.md`, log/artifact directory layout under `.planning/v1.6/`.

## User Constraints (from CONTEXT.md)

> Verbatim copy from `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-CONTEXT.md` so the planner can treat this section as the single source of truth without re-reading the upstream file. Decisions D-01..D-13 are locked; do not re-litigate. Sections collapsed for brevity — the full rationale lives in CONTEXT.md.

### Locked Decisions

- **D-01 CLI placement:** `firestarter [-p PORT] dev consistency-check <chip> [--runs N] [--output-dir DIR] [--keep-files/--no-keep-files] [--max-diffs M] [-q/--quiet]`. Verb `consistency-check` (with hyphen). Defaults: `--runs 3`, `--keep-files` ON, `--max-diffs 10`. Added under `create_dev_args(parser)` (firestarter_app/firestarter/main.py:366) alongside `dev read` / `dev reg` / `dev addr`. Dispatch slots into the `args.dev_command == "consistency-check"` elif branch in the `args.command == "dev"` block (firestarter_app/firestarter/main.py:799-845).
- **D-02 Passive / read-only:** N consecutive `read_eprom` invocations against the chip in socket; no write step; no baseline image. Verdict logic = "are all N SHA-256s equal?". Works on any chip in any state (programmed / blank / mid-erase / missing).
- **D-03 Operator method:** `EpromOperator.consistency_check_eprom(eprom_name, eprom_data_dict, runs=3, output_dir=None, keep_files=True, max_diffs=10, operation_flags=0) -> int` in firestarter_app/firestarter/eprom_operations.py. **MUST reuse the existing read state machine verbatim** — `_run_state_machine(main_phase_handler=self._main_phase_read_data, ...)` invoked N times. No parallel read implementation. Returns integer exit code (D-05).
- **D-04 Output:** stdout per-run `Run {i}/{N}: SHA-256 {hex} bytes={size} elapsed={s}s`; post-runs verdict block (PASS / FAIL with first-divergence offset, total divergent bytes, percentage, first M divergent offsets). Default output-dir name `consistency-check-<chip>-<board>-<YYYY-MM-DD-HHMMSS>/run_<NN>.bin`.
- **D-05 Exit codes:** `0`=PASS (all SHAs equal); `1`=FAIL (one or more reads diverge — bug detected); `2`=hardware/serial/timeout error (could not complete N reads). Same convention as `grep`.
- **D-06 Full-chip only:** no `--chunk-size N` flag. 1KB case covered by existing `dev read -s 1024` (Phase 29 / VERIFY-03).
- **D-07 Operator-driven per-port:** no `--all-boards` orchestrator. Operator switches boards manually.
- **D-08 Evidence file:** `.planning/v1.6-EVIDENCE.md` schema locked (Board, Port, Chip, N, SHAs distinct, Divergent bytes, First-diverge offset, Verdict, Log). Phase 26 creates the file with `## Phase 26 — Pre-fix Consistency-Check Baseline (YYYY-MM-DD)` section + 3 rows. Phase 27 appends RCA section; Phase 28 appends commit refs; Phase 29 appends post-fix verification (inverted: PASS / SHAs distinct = 1).
- **D-09 Plan structure (TWO plans):** 26-01 desk-side (`autonomous: true`) implements REPRO-03 — CLI + operator method + tests. 26-02 operator-on-bench (`autonomous: false`) runs REPRO-01 + REPRO-02 + SC#5 — diagnostic against uno + leonardo + uno328pb, populates evidence file. Plan dependency: 26-01 → 26-02.
- **D-10 Tests:** `firestarter_app/tests/test_consistency_check.py`. 6 locked test cases (all runs identical → exit 0; one-byte differs → exit 1 / first divergence; full scramble → exit 1 / 3 distinct SHAs; serial timeout → exit 2; `--keep-files False` cleans; `--runs 1`/`0` rejected → exit 2).
- **D-11 Progress:** Per-run `tqdm` via existing `ClassProgressHandler`. `-q/--quiet` suppresses tqdm only; `-v/--verbose` (top-level) controls serial trace unchanged.
- **D-12 Hashing:** `hashlib.sha256` over the per-run binary, post-read.
- **D-13 Branch flow:** `firestarter_app/v1.6-read-bug` cut from current `beta` (post-v1.5 `3.0.0b4`). No firmware sub-repo branch — firmware untouched in Phase 26.

### Claude's Discretion

- Exact `--output-dir` default naming format (D-04 hyphen-separated is the working default; underscore variants acceptable).
- Whether `ClassProgressHandler` is reset per run or a fresh instance is created per run. **Research finding (see §"Existing Code Insights" below): `_run_state_machine` already instantiates a fresh `ClassProgressHandler` per call at `eprom_operations.py:237`. `consistency_check_eprom` does NOT need to manage handlers manually — each `_run_state_machine` invocation gets its own.**
- `-q` short flag could collide with a future top-level flag; planner can drop short form if needed.
- Whether 26-02 reads through one chip rotated across 3 boards (recommended for cleanest comparison with the 2026-05-21 SST27SF512 baseline) vs three separate chips. Either is acceptable.
- Optional `--json` output flag deferred to v1.7+.

### Deferred Ideas (OUT OF SCOPE)

- `--all-boards` orchestrator (per-port manual invocation only).
- `--chunk-size N` flag inside `consistency-check` (Phase 29 covers 1KB via existing `dev read -s 1024` shell loop).
- `--json` output mode (defer to v1.7+).
- Promoting `consistency-check` to a top-level command (lives under `dev` permanently per ROADMAP).
- Cross-shield rotation matrix as part of Phase 26 (3-shield A/B/C triage already in `large-read-data-jitter-uno328pb.md`).
- Ranking the 4 Phase 27 hypotheses (host-side buffer; firmware MAIN-state off-by-N; 328PB-specific timing; missing `-D SERIAL_RX_BUFFER_SIZE`) — Phase 27 owns ranking; Phase 26 just records raw evidence.
- Firmware sub-repo changes (deferred to Phase 28 per D-13).
- avrdude-mcu-detection-fallback and w27c512-eeprom-misclassification (separate backlog items, out of v1.6 scope).

## Phase Requirements

| ID | Description (verbatim from REQUIREMENTS.md §"Reproduction & Triage") | Research Support |
|----|--------------------------------------------------------------------|------------------|
| REPRO-01 | Operator can reproduce 64KB read-jitter on `uno` (not just `uno328pb`) — consecutive `firestarter read <chip> file.bin` against a static chip yields different SHA-256 hashes | Closed by 26-02 bench wave (`uno` row in `.planning/v1.6-EVIDENCE.md` shows `Verdict=FAIL`). The new `dev consistency-check` tool is the mechanism (REPRO-03 closes its construction). The 3-shield A/B/C triage in `large-read-data-jitter-uno328pb.md` predicts the bug is shield-invariant and pre-existing on the 328P / 328PB family — `uno` jitter is expected. |
| REPRO-02 | Operator can reproduce 64KB read-jitter on `leonardo` (1024-byte buffer board; magnitude may differ but bug must be present or explicitly proven absent) | Closed by 26-02 bench wave (`leonardo` row in `.planning/v1.6-EVIDENCE.md`). Leonardo's 1024-byte `DATA_BUFFER_SIZE` (vs Uno's 512) halves the chunk count for a 64KB read, so jitter magnitude *may* differ; either outcome (present with different magnitude, or explicitly absent with evidence) closes the requirement. If absent, RCA scope expands to 328-specific timing (Phase 27 territory). |
| REPRO-03 | A reusable "consecutive-read consistency" diagnostic script lives in the host CLI (e.g. `firestarter dev consistency-check <chip> --runs N`) so the bug — and its eventual fix — is verifiable by anyone with hardware | Closed by 26-01 desk-side wave (CLI subcommand + operator method + 6 pytest cases). The tool persists permanently — Phase 29 / VERIFY-01 + VERIFY-02 reuses it post-fix as the acceptance gate. |

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| CLI argparse — `dev consistency-check <chip>` subparser + flag parsing | Host CLI (`firestarter_app/firestarter/main.py:create_dev_args`) | — | All existing `dev` verbs live here; consistency-check joins them. |
| Dispatch — eprom DB lookup, build_arg_flags, call into operator | Host CLI (`firestarter_app/firestarter/main.py` `args.dev_command` block) | — | Mirrors the dispatch shape of `dev read` lines 800-818. |
| Per-run read loop — N consecutive `read_eprom` invocations against the same chip | Host CLI (`firestarter_app/firestarter/eprom_operations.py::EpromOperator.consistency_check_eprom`) | Existing `_run_state_machine` + `_main_phase_read_data` | Reuse-not-duplicate rule (D-03). The diagnostic IS a wrapper over N invocations of the production read path. |
| Wire protocol — INIT/MAIN/END state machine, MSG_DATA_CHUNK frame parsing | Existing `firestarter_app/firestarter/serial_comm.py` + `eprom_operations.py::_main_phase_read_data` | Firmware (unchanged in Phase 26) | The exact code path the bug lives in. Diagnostic exercises it unchanged. |
| SHA-256 hashing | Host CLI (stdlib `hashlib`) | — | Post-read, full-file. No streaming hash needed at 64KB (D-12). |
| Verdict logic + divergence reporting | Host CLI (inside `consistency_check_eprom`) | — | In-memory list of `(run_i, sha, bytes_written)` — set equality + first-differ scan. |
| Per-run binary artifact persistence | Host CLI (file I/O — `output_dir/run_NN.bin`) | — | Same `open("...", "wb")` + `file_handle.write(...)` pattern as `read_eprom` lines 408-411 (the `_write_to_file` inner closure). |
| Cross-board orchestration | **Operator manually** (per-port invocation) | — | D-07 — no `--all-boards`. Operator switches boards using existing `-p /dev/ttyXXX` muscle memory. |
| Board name extraction (for verdict block) | Firmware handshake reply via `FirmwareManager.check_current_firmware` (firestarter_app/firestarter/firmware.py:80-130) | — | Already parses `"FW: <version>:<board>"` payload. Reuse the same parsing — board name is in the third return slot. **See §"Open Questions Q1" for the exact reuse mechanic.** |
| Pre-fix evidence accretion | Meta-repo `.planning/v1.6-EVIDENCE.md` | Phase 27/28/29 (also accrete) | Same pattern as `.planning/v1.5-BENCH-RESULTS.md` and `.planning/v1.3-BENCH-RESULTS.md`. |

## Standard Stack

### Core (already in firestarter_app — no new dependencies)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `argparse` (stdlib) | Python 3.9+ | CLI subparser for `dev consistency-check` | Existing convention — all `dev` verbs use argparse subparsers (verified at main.py:371). |
| `hashlib` (stdlib) | Python 3.9+ | SHA-256 over per-run binary | D-12 locks SHA-256; stdlib `hashlib.sha256(open(path,'rb').read()).hexdigest()` is one line. No new dep. |
| `tqdm` | already pinned (used by `ClassProgressHandler` at eprom_operations.py:99) | Per-run progress bar | D-11. Reused via existing `ClassProgressHandler`. `_run_state_machine` already instantiates a fresh handler per call at eprom_operations.py:237 — no per-run reset code needed. |
| `pytest` | already pinned | Test framework | All 5 existing test files in `firestarter_app/tests/` are pytest. |
| `serial.Serial` / `pyserial` | already pinned | Real wire I/O at 250000 baud | Reused via `SerialCommunicator.find_and_connect` — Phase 26 doesn't touch this layer directly. |

**No new dependencies are introduced by Phase 26.** All required surfaces are in the host CLI sub-repo's pinned dependency set.

### Verification

```bash
# Confirmed by reading firestarter_app/firestarter/eprom_operations.py:
#   line 17 — import tqdm
#   line 18 — from tqdm.contrib.logging import logging_redirect_tqdm
# Confirmed by reading firestarter_app/tests/test_decoder.py:
#   tests use only stdlib + pytest + the in-repo conftest fixtures
# No version-bump or pyproject.toml edit is required for Phase 26.
```

## Architecture Patterns

### System Architecture Diagram

```
[Operator shell loop]                                          [Bench: uno / leonardo / uno328pb]
         │                                                                   ▲
         │ firestarter -p /dev/ttyXXX dev consistency-check <chip>           │ serial @ 250000 baud
         ▼                                                                   │
┌────────────────────────────────────────────────────────────────────────────┴───────────┐
│ firestarter_app/firestarter/main.py                                                     │
│   parser → args.command == "dev" / args.dev_command == "consistency-check"              │
│   db_instance.get_eprom(args.eprom) → convert_to_programmer(...)                        │
│   eprom_operator.consistency_check_eprom(eprom_name, eprom_data, runs=..., ...)         │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ EpromOperator.consistency_check_eprom (NEW — eprom_operations.py)                       │
│   • Resolve output_dir (default consistency-check-<chip>-<board>-<TS>/)                 │
│   • Loop i = 1..runs:                                                                   │
│       open(f"{output_dir}/run_{i:02d}.bin", "wb") as fh                                 │
│       with _operation_context(...) as (cmd_data, _, op_name):                           │
│           _run_state_machine(op_name,                                                   │
│             main_phase_handler=_main_phase_read_data,                                   │
│             start_addr=..., end_addr=...,                                               │
│             process_data_chunk_callback=_write_to_file_for_this_run)                    │
│       sha = hashlib.sha256(open(path,'rb').read()).hexdigest()                          │
│       results.append((i, sha, file_size))                                               │
│   • Compute verdict: distinct_shas = len(set(r.sha for r in results))                   │
│   • If distinct_shas > 1: scan run_1 vs run_2 for first divergence + total diffs        │
│   • Print stdout verdict block                                                          │
│   • If output_dir under .planning/: append row to v1.6-EVIDENCE.md                      │
│   • If not keep_files: shutil.rmtree(output_dir)                                        │
│   • Return 0 / 1 / 2 per D-05                                                           │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │  (per-run, called N times)
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ EpromOperator._run_state_machine (existing — eprom_operations.py:232)                   │
│   → instantiates fresh ClassProgressHandler at line 237                                 │
│   → INIT phase: send_ack + wait for INIT response                                       │
│   → MAIN phase: invokes _main_phase_read_data (line 349)                                │
│       • parses MSG_DATA_CHUNK ID frames (Phase 8 W-04 wire format)                      │
│       • calls process_data_chunk_callback(address, payload)  ← per-run binary file writer
│       • send_ack after each chunk                                                       │
│   → END phase: wait for END response + final send_ack                                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Reader trace:** start at top-left (operator shell command), follow argparse → dispatch → operator method → state machine. The bottom box is the bug-suspect code path — `consistency_check_eprom` must invoke `_run_state_machine` unchanged or it cannot reproduce the bug.

### Recommended Project Structure

```
firestarter_app/                              # sub-repo (NOT meta-repo)
├── firestarter/
│   ├── main.py                              # MODIFIED: create_dev_args + dev dispatch
│   ├── eprom_operations.py                  # MODIFIED: add consistency_check_eprom
│   ├── firmware.py                          # READ-ONLY: check_current_firmware (for board name)
│   ├── database.py                          # READ-ONLY: get_eprom + convert_to_programmer
│   ├── serial_comm.py                       # READ-ONLY: SerialCommunicator (read state machine)
│   └── constants.py                         # READ-ONLY: FLAG_* / COMMAND_*
├── tests/
│   ├── conftest.py                          # READ-ONLY: fake_serial + make_comm reused
│   ├── test_consistency_check.py            # NEW: 6 test cases per D-10
│   └── test_firmware_install.py             # READ-ONLY: avrdude mock pattern reference
└── (no new directories needed)

.planning/                                   # meta-repo, branch v1.6-read-bug (cut from main)
├── phases/26-cross-board-reproduction-diagnostic-tooling/
│   ├── 26-CONTEXT.md                        # exists
│   ├── 26-DISCUSSION-LOG.md                 # exists
│   ├── 26-RESEARCH.md                       # THIS FILE
│   ├── 26-PLAN.md (or 26-01-PLAN.md + 26-02-PLAN.md)  # planner creates
│   └── (VALIDATION.md if Nyquist-minted)
├── v1.6-EVIDENCE.md                         # NEW (created by Plan 26-02; lives at .planning/ root)
└── v1.6/                                    # OPTIONAL (only if planner wants a bench-logs/ + bench artifacts/ subdir; mirror of .planning/v1.3/)
    └── bench-logs/                          # OPTIONAL — per-board operator logs
```

### Pattern 1: Mirror `dev read` argparse → dispatch → operator method chain

**What:** The new `dev consistency-check` subparser, dispatch branch, and operator method must mirror the existing `dev read` chain verbatim. The planner can copy-paste structure, then change verbs.

**Existing `dev read` chain (the template):**

```python
# firestarter_app/firestarter/main.py:373-388 — argparse subparser
read_parser = subparsers.add_parser(
    "read", help="Reads the content from an EPROM and prints data to console."
)
add_eprom_completer(read_parser)
read_parser.add_argument("-a", "--address", type=str, help="Read start address in dec/hex")
read_parser.add_argument("-s", "--size", type=str, help="Size of the data to read in dec/hex")
read_parser.add_argument(
    "-f", "--force", action="store_true",
    help="Force read, even if the chip id doesn't match.",
)
```

```python
# firestarter_app/firestarter/main.py:800-818 — dispatch branch
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
                args.eprom, eprom_data,
                address_str=args.address, size_str=args.size,
                operation_flags=build_arg_flags(args),
            )
            else 0
        )
```

```python
# firestarter_app/firestarter/eprom_operations.py:429-454 — dev_read_eprom (returns bool)
def dev_read_eprom(self, eprom_name, eprom_data_dict, address_str=None, size_str="256", operation_flags=0) -> bool:
    with self._operation_context(eprom_name, eprom_data_dict, COMMAND_READ, operation_flags, address_str, size_str or "256") as (cmd_data, _, op_name):
        if not cmd_data: return False
        start_addr = cmd_data.get("address", 0)
        end_addr = cmd_data.get("memory-size", start_addr)
        ...
        is_ok, _ = self._run_state_machine(
            op_name,
            main_phase_handler=self._main_phase_read_data,
            start_addr=start_addr, end_addr=end_addr,
            process_data_chunk_callback=hexdump,           # ← only diff vs read_eprom: callback writes hex to stdout
        )
        return is_ok
```

**New `dev consistency-check` chain (mirrors the above):**

```python
# firestarter_app/firestarter/main.py — add inside create_dev_args, after addr_parser block
cc_parser = subparsers.add_parser(
    "consistency-check",
    help="Read the EPROM N consecutive times and report SHA-256 divergence (REPRO-03; D-01).",
)
add_eprom_completer(cc_parser)
cc_parser.add_argument("--runs", type=int, default=3, help="Number of consecutive reads (default 3; minimum 2).")
cc_parser.add_argument("--output-dir", type=str, default=None, help="Output dir for per-run binaries (default consistency-check-<chip>-<board>-<TS>/).")
cc_parser.add_argument("--keep-files", dest="keep_files", action="store_true", default=True, help="Keep per-run binary files (default).")
cc_parser.add_argument("--no-keep-files", dest="keep_files", action="store_false", help="Delete per-run binaries after verdict.")
cc_parser.add_argument("--max-diffs", type=int, default=10, help="Max divergent offsets to print (default 10).")
cc_parser.add_argument("-q", "--quiet", action="store_true", help="Suppress per-run tqdm progress bars (D-11).")
cc_parser.add_argument(
    "-f", "--force", action="store_true",
    help="Force read, even if the chip id doesn't match (e.g. Shield-3 missing-chip case).",
)

# firestarter_app/firestarter/main.py — add inside args.command == "dev" block, after the args.dev_command == "addr" branch
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

**Note on integer-vs-bool return:** The new method returns `int` directly (not wrapped in `1 if not else 0`). This is the divergence from `dev_read_eprom` and is correct per D-05 (3-way exit codes can't fit in bool). Precedent: `check_eprom_id` at eprom_operations.py:618 returns `Tuple[bool, Optional[int]]` for the same "need richer information than bool" reason.

### Pattern 2: `EpromOperator.consistency_check_eprom` internal shape

**What:** The new operator method must reuse `_run_state_machine` + `_main_phase_read_data` verbatim per D-03's reuse-not-duplicate rule.

**Signature (from D-03, locked):**

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
    Same exit-code convention as grep(1).

    Reuses _run_state_machine + _main_phase_read_data verbatim — the
    diagnostic exercises the same code path the bug lives in. Do NOT
    refactor into a parallel read implementation.
    """
```

**Implementation shape** (planner produces; the executor implements):

```python
import hashlib
import shutil
from datetime import datetime
from pathlib import Path

def consistency_check_eprom(self, eprom_name, eprom_data_dict, runs=3,
                             output_dir=None, keep_files=True, max_diffs=10,
                             quiet=False, operation_flags=0) -> int:
    # 1. Validate --runs (D-10 test #6)
    if runs < 2:
        logger.error(f"--runs must be >= 2 (got {runs}); a consistency check requires at least 2 reads to compare.")
        return 2

    # 2. Resolve output_dir
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        # board name retrieval: see Open Question Q1 — either from a prior
        # FirmwareManager.check_current_firmware() call (extra serial round-trip),
        # or from cmd_data after the first read (if it carries board info),
        # or fall back to a placeholder and replace post-hoc.
        board = self._resolve_board_name() or "unknown-board"
        output_dir = f"consistency-check-{eprom_name}-{board}-{timestamp}"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 3. Loop N runs, each through the real read state machine
    results = []  # list of (run_i, sha_hex, bytes_written) tuples
    for i in range(1, runs + 1):
        run_path = Path(output_dir) / f"run_{i:02d}.bin"
        logger.info(f"Run {i}/{runs}: reading {eprom_name} → {run_path}")
        start_t = time.time()

        # Reuse the EXACT code path read_eprom uses (D-03 reuse-not-duplicate)
        try:
            with self._operation_context(eprom_name, eprom_data_dict, COMMAND_READ, operation_flags) as (cmd_data, _, op_name):
                if not cmd_data:
                    logger.error(f"Run {i}: failed to set up read operation.")
                    return 2  # hardware error per D-05
                with open(run_path, "wb") as fh:
                    def _writer(address, data_chunk):
                        fh.seek(address)
                        fh.write(data_chunk)
                    is_ok, _ = self._run_state_machine(
                        op_name,
                        main_phase_handler=self._main_phase_read_data,
                        start_addr=cmd_data.get("address", 0),
                        end_addr=cmd_data.get("memory-size", 0),
                        process_data_chunk_callback=_writer,
                    )
                if not is_ok:
                    return 2  # hardware error
        except EpromOperationError as e:
            logger.error(f"Run {i}: {e}")
            return 2  # hardware error per D-10 test #4

        # Hash + record
        bytes_written = run_path.stat().st_size
        sha = hashlib.sha256(run_path.read_bytes()).hexdigest()
        elapsed = time.time() - start_t
        results.append((i, sha, bytes_written))
        logger.info(f"Run {i}/{runs}: SHA-256 {sha}  bytes={bytes_written}  elapsed={elapsed:.2f}s")

    # 4. Verdict
    distinct = sorted({r[1] for r in results})
    exit_code = 0 if len(distinct) == 1 else 1

    # 5. Verdict block (D-04)
    verdict = "PASS" if exit_code == 0 else "FAIL"
    print(f"\nConsistency check: {verdict}")
    print(f"Chip: {eprom_name}  Board: {self._resolve_board_name() or '?'}  Port: {self.config.get_value('port')}")
    print(f"Runs: N={runs}")
    print(f"Distinct SHAs: {len(distinct)}")
    print(f"Output dir: {output_dir}/")

    # 6. Divergence detail on FAIL (D-04)
    if exit_code == 1:
        run1_bytes = (Path(output_dir) / "run_01.bin").read_bytes()
        run2_bytes = (Path(output_dir) / "run_02.bin").read_bytes()
        # First divergence
        first = next((o for o in range(min(len(run1_bytes), len(run2_bytes))) if run1_bytes[o] != run2_bytes[o]), None)
        if first is not None:
            print(f"First divergence: offset 0x{first:04X}  (run_1=0x{run1_bytes[first]:02X}, run_2=0x{run2_bytes[first]:02X})")
        # Total diffs
        diff_offsets = [o for o in range(min(len(run1_bytes), len(run2_bytes))) if run1_bytes[o] != run2_bytes[o]]
        total = len(diff_offsets)
        pct = 100.0 * total / len(run1_bytes) if run1_bytes else 0.0
        print(f"Total divergent bytes (run_1 vs run_2): {total} / {len(run1_bytes)} ({pct:.1f}%)")
        # First M offsets
        head = diff_offsets[:max_diffs]
        offs_str = ", ".join(f"0x{o:04X}" for o in head)
        print(f"First {max_diffs} divergent offsets: {offs_str}")

    # 7. Evidence file accretion (only if output_dir is under .planning/)
    if str(Path(output_dir).resolve()).startswith(str(Path(".planning").resolve())):
        self._append_evidence_row(eprom_name, results, exit_code, output_dir)

    # 8. Cleanup
    if not keep_files:
        shutil.rmtree(output_dir)

    return exit_code
```

**When to use:** Exactly once — `consistency_check_eprom` is the canonical Phase 26 implementation. Plan 26-01 lands this method + the 6 pytest cases.

### Pattern 3: Stubbed-serial pytest test (template from `test_decoder.py::test_chip_read_loop_concatenates_multiple_chunks`)

**What:** The 6 D-10 test cases stub the serial layer using `fake_serial` + `make_comm` from `tests/conftest.py`. The closest existing precedent — `test_chip_read_loop_concatenates_multiple_chunks` at `test_decoder.py:475` — drives the read loop with MSG_DATA_SENDING + MSG_DATA_CHUNK + MSG_MAIN_DONE frames and asserts byte concatenation.

**Skeleton for D-10 test case #1 (all runs identical → exit 0):**

```python
# firestarter_app/tests/test_consistency_check.py (NEW)
import hashlib
import pytest
from unittest.mock import patch

# Conftest exposes: fake_serial, make_comm, build_frame
# Both are picked up automatically by pytest.

class TestConsistencyCheck:
    def test_all_runs_identical_pass_exit_0(self, tmp_path, fake_serial, make_comm, monkeypatch):
        """D-10 Test 1: stub state machine to return the same 65,536-byte stream on every call → exit 0."""
        from firestarter.eprom_operations import EpromOperator
        from firestarter.config import ConfigManager

        # Identical payload for all N runs
        identical_payload = bytes(range(256)) * 256  # 65,536 bytes

        # Stub _run_state_machine to invoke the callback with the identical payload
        captured_runs = []
        def fake_state_machine(self, op_name, **kwargs):
            cb = kwargs["process_data_chunk_callback"]
            cb(0, identical_payload)
            captured_runs.append(op_name)
            return (True, None)

        # Stub _operation_context to yield a fake cmd_data + buffer_size
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
        # Each run_NN.bin exists + has identical SHA
        shas = [hashlib.sha256((tmp_path / "out" / f"run_{i:02d}.bin").read_bytes()).hexdigest()
                for i in (1, 2, 3)]
        assert shas[0] == shas[1] == shas[2]
```

**When to use:** Same monkeypatch-of-EpromOperator-internals pattern for all 6 D-10 test cases:
1. All identical → exit 0 (above template).
2. One byte differs at 0x123 in run 2 → exit 1, first-divergence offset 0x0123, byte-diff count = 1 (vary `fake_state_machine` to mutate the payload on the 2nd call).
3. Full scramble (3 distinct payloads) → exit 1, Distinct SHAs: 3, first divergence at 0x0000.
4. State machine raises `EpromOperationError` → exit 2 (have `fake_state_machine` raise).
5. `keep_files=False` → output dir is removed (assert `not output_dir.exists()`).
6. `--runs 1` and `--runs 0` rejected → exit 2 (no state-machine invocation; checked at the top of `consistency_check_eprom`).

**Why this pattern:** Phase 8 Plan 03 (test_decoder.py landing) and Phase 6 (conftest landing) established the BytesIO-backed fake serial port. The new test file imports from `conftest` — no new fixtures needed. Per the conftest module docstring, this is the established host sub-repo pattern.

### Anti-Patterns to Avoid

- **Building a parallel read loop that bypasses `_run_state_machine` / `_main_phase_read_data`.** D-03 reuse-not-duplicate rule. If the diagnostic doesn't trip the bug, it's not diagnosing the bug — it's diagnosing a parallel code path. The bug is suspected to live inside `_main_phase_read_data`'s MSG_DATA_CHUNK extraction loop or below (per hypothesis #2 in `large-read-data-jitter-uno328pb.md`); a parallel read implementation would falsely PASS post-fix on still-broken transport code.
- **Adding a `--chunk-size N` flag.** D-06 — full-chip only. The 1KB case is covered by Phase 29's `for i in 1..5; do firestarter dev read -s 1024 ...; done` shell loop reuse. Pre-building for a hypothetical fix shape (different fix for full-chip vs 1KB modes) is premature.
- **Promoting `consistency-check` to a top-level command (`firestarter consistency-check <chip>`).** D-01 — lives under `dev` permanently. Top-level is reserved for user-facing operations (read/write/verify/erase/blank/id/info); diagnostics live under `dev`.
- **Switching the hash function from SHA-256 to xxhash / SHA-1 / MD5 for "speed".** D-12 — at 64KB, post-read hashing is microseconds; the 60-second serial transfer dominates. SHA-256 matches the operator's mental model from the original 2026-05-21 triage (`sha256sum /tmp/read_$i.bin`).
- **Modifying `firestarter/` (firmware sub-repo) in Phase 26.** D-13 — Phase 26 is host-CLI-only. The firmware `v1.6-read-bug` branch is cut in Phase 28 when the fix lands.
- **Hand-rolling progress reporting instead of reusing `ClassProgressHandler`.** D-11. The existing `ClassProgressHandler` at eprom_operations.py:83-127 wraps `tqdm.tqdm` with a `bar_format = "{l_bar}{bar}| {n:#06x}/{total:#06x} bytes "` that the operator already recognizes from `read_eprom` invocations. **Critical:** `_run_state_machine` already instantiates one per call (line 237) — `consistency_check_eprom` does NOT manage handler lifecycle. For `--quiet`, the cleanest hook is to set the existing top-level `args.verbose = False` AND prevent the inner `tqdm` from showing — verify path during implementation.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| INIT/MAIN/END state machine for read | A parallel chunked-read loop bypassing `_run_state_machine` | `EpromOperator._run_state_machine(main_phase_handler=self._main_phase_read_data, ...)` (existing, eprom_operations.py:232+349) | D-03 reuse-not-duplicate — the bug lives here; diagnostic must exercise this code path. |
| MSG_DATA_CHUNK frame parsing + CRC8 verification | A separate decoder | `SerialCommunicator.get_response()` (existing, serial_comm.py) → response.payload | Phase 8 W-04 wire format is shared infrastructure; Phase 26 only consumes responses, doesn't decode frames. |
| Per-chunk file write + seek | A separate write buffer | The same `_write_to_file(address, data_chunk)` closure pattern as `read_eprom` at eprom_operations.py:409-411 | Established pattern; works at any chunk size; respects `start_addr` offset. |
| Firmware-reported board name extraction | A new handshake parser | `FirmwareManager.check_current_firmware(preferred_port=...)` (existing, firmware.py:80-130) — returns `(port, version, board)` | Already parses `"FW: <version>:<board>"` payload at line 109-112. |
| EPROM database chip lookup + DIP-pin-to-bus-config translation | A separate chip resolver | `EpromDatabase.get_eprom(name)` + `EpromDatabase.convert_to_programmer(full_data)` (existing, database.py:493 + 522) | Already called by every other `dev` command (lines 800-808 for `dev read`). |
| Operation flags (force / verbose / blank-check / etc.) | A new flag builder | `build_arg_flags(args)` (existing, main.py:439) | Reused by every dispatch branch; passing `--force` through enables Shield-3 missing-chip case. |
| SHA-256 hashing | A custom incremental hasher | `hashlib.sha256(open(path,'rb').read()).hexdigest()` (stdlib, one line) | 64KB fits in RAM; no streaming needed. |
| tqdm progress bar lifecycle | Manual tqdm.tqdm instances per run | `_run_state_machine` already instantiates `ClassProgressHandler(self.progress_callback)` at eprom_operations.py:237 per call | Already per-call; no `consistency_check_eprom` lifecycle code needed. |
| BytesIO-backed serial stub for tests | A new pytest fixture | `fake_serial` + `make_comm` (existing, tests/conftest.py:122-146); `build_frame` helper at line 53 | Established by Phase 8 — used by test_decoder.py × 30+ tests. |
| `EpromOperator` initialization in tests | Real `SerialCommunicator.find_and_connect` | Monkeypatch `EpromOperator._operation_context` to yield a fake `cmd_data` (see test_decoder.py:475 precedent + Pattern 3 above) | Hardware-free; deterministic; <1 second per test. |

**Key insight:** Phase 26 is a **near-zero new code surface** at the architectural level — the new operator method is fundamentally a `for i in range(N): self.read_eprom(...)` wrapper with hashing and divergence reporting bolted on. Hand-rolling anything else (serial layer, chunk parsing, progress bars, hash) means deviating from the bug-suspect code path or from established stubbing patterns. Both are wrong.

## Runtime State Inventory

Phase 26 is **not** a rename / refactor / migration. The new code is purely additive (one new operator method, one new argparse subparser branch, one new dispatch elif, one new test file, one new evidence file). No stored data, no live service config, no OS-registered state, no secrets/env vars, no build artifacts carry the old name (there is no old name).

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — phase is read-only / passive against EPROMs; no DB writes, no config writes | None |
| Live service config | None — no n8n / GitHub Actions / cron / launchd touched | None |
| OS-registered state | None — no new entry point script, no new pip-installed CLI, no new daemon | None |
| Secrets / env vars | None — no new env vars; existing `FIRESTARTER_DEV_ALLOW_PRE_V12` escape hatch is unrelated | None |
| Build artifacts | None — no new pyproject.toml dependency, no firmware target change; `firestarter_app/firestarter.egg-info/` regenerates from `pip install -e .` as a side effect of any branch checkout, no special handling needed | None |

**Verified by:** Re-reading CONTEXT.md scope sections, REQUIREMENTS.md REPRO-01/02/03, and STATE.md v1.6 Decisions. The only artifact-with-a-name created is `.planning/v1.6-EVIDENCE.md` — a brand-new file with no prior reference to update.

## Common Pitfalls

### Pitfall 1: `_run_state_machine` already creates its own `ClassProgressHandler` — don't double-instantiate

**What goes wrong:** Planner writes `consistency_check_eprom` to instantiate a `ClassProgressHandler` and pass it into `_run_state_machine`, ending up with two competing handlers (one per call from outside, one from `line 237`). Output is two stacked progress bars per run, or one bar that closes immediately.
**Why it happens:** The `ClassProgressHandler` class is exported and looks reusable; without reading line 237 of `_run_state_machine`, it's not obvious that the state machine instantiates its own.
**How to avoid:** `consistency_check_eprom` does NOT touch `ClassProgressHandler` directly. Each call to `_run_state_machine` gets its own fresh handler. For `--quiet` mode, the cleanest path is to pass a no-op `progress_callback` into the `EpromOperator` constructor (which short-circuits the tqdm path per `ClassProgressHandler.__init__` at line 84-86: `if self.progress_callback:` branches around the `tqdm.tqdm(...)` instantiation), OR temporarily swap the operator's `progress_callback` for the duration of the consistency-check call.
**Warning signs:** Two progress bars per run in the operator's terminal; or progress bar that completes at 0/65536 instantly and stays visible.

### Pitfall 2: The default `output_dir` needs the board name BEFORE the first read runs

**What goes wrong:** Planner specifies `default output_dir = consistency-check-<chip>-<board>-<TS>/` but the board name comes from the firmware handshake which only runs as a side effect of `SerialCommunicator.find_and_connect(...)` inside `_operation_context`. Cyclic dependency: need board to name the dir; need to start a connection to learn the board.
**Why it happens:** The board name is in the firmware handshake response (line 112 of firmware.py) parsed inside `check_current_firmware`, which is a separate code path from `find_and_connect`'s probe.
**How to avoid:** Three options for the planner to choose between (Open Question Q1 below):
  - **(a)** Call `FirmwareManager(self.config).check_current_firmware()` once at the top of `consistency_check_eprom` to learn the board, then construct `output_dir`. Costs one extra serial round-trip (~1-2s).
  - **(b)** Create the dir with a `unknown-board` placeholder, then rename it after the first run finishes (need to extract board name from `cmd_data` or the first `_operation_context` invocation — needs verification: does `find_and_connect` populate any board-name accessible attribute on `SerialCommunicator`?).
  - **(c)** Use a non-board-aware default like `consistency-check-<chip>-<TS>/` and print the board on the verdict block but skip it from the dirname.
**Warning signs:** Output dir starts with `unknown-board` and stays that way; or the first run's `find_and_connect` blocks/errors because the diagnostic raced ahead with a non-existent board name.
**Recommendation:** Option (a) is cleanest — explicit handshake before the read loop, no clever post-hoc rename. Cost is ~1-2s out of the ~3 × 60s run budget; negligible.

### Pitfall 3: `_operation_context` exits the `with` block on every run, which closes the serial connection between runs

**What goes wrong:** Each `_operation_context(...)` block opens a serial connection in `_setup_operation` (line 196: `SerialCommunicator.find_and_connect(...)`) and closes it in `finally:` at line 223 (`self._disconnect_programmer()`). For N=3 runs, that's 3 open/close cycles. Open cycles include the firmware handshake (~1-2 seconds) which adds up to ~3-6s of overhead for an 180-second total run budget. Functionally correct, but slow.
**Why it happens:** Existing operator methods (read_eprom, write_eprom, etc.) are designed as one-shot operations. The diagnostic is the first method that needs the connection to persist across N independent operations.
**How to avoid:** **Accept the overhead.** Reusing `_operation_context` verbatim preserves the reuse-not-duplicate rule (D-03). Each run is a clean state-machine invocation — exactly what a real `read_eprom` operator invocation looks like — so the diagnostic faithfully reproduces what the operator's `for i in 1..3; do firestarter read ...; done` shell loop does (the canonical baseline pattern from `large-read-data-jitter-uno328pb.md`). Keeping the connection open across runs would deviate from the operator's mental model.
**Warning signs:** Total runtime per `consistency-check` is ~5-10s longer than 3 × `read` invocations. This is desired, not a bug — confirms the diagnostic faithfully wraps the read path.

### Pitfall 4: Test #4 (serial timeout → exit 2) needs to mock the right layer

**What goes wrong:** Test attempts to stub `comm.get_response` to raise `SerialTimeoutError`, but the `_run_state_machine` only catches `(SerialError, SerialTimeoutError, EpromOperationError)` at line 261 — the raise propagates as a tuple return `(False, str(e))` not as an exception. The test then expects exit 2 (hardware error) but gets exit 1 (FAIL).
**Why it happens:** `_run_state_machine` returns `(is_ok, msg)` even on serial errors — the exception is converted to a False return inside the `try`/`except` block at lines 261-263.
**How to avoid:** The `consistency_check_eprom` implementation must distinguish `is_ok=False` from `_run_state_machine` (signal: hardware error, exit 2) from "completed N runs but SHAs differ" (signal: bug detected, exit 1). The implementation sketch in Pattern 2 handles this correctly — `if not is_ok: return 2` immediately on a state-machine failure, before computing verdict. Test #4 must mock so that the 2nd or 3rd `_run_state_machine` call returns `(False, "timeout")` and assert exit code == 2.
**Warning signs:** Test #4 fails with `assert rc == 2` getting `rc == 1` — exit code semantics are swapped.

### Pitfall 5: `args.force` is NOT on the new `cc_parser` by default — `build_arg_flags` quietly defaults it to False

**What goes wrong:** Planner omits `-f/--force` from the new subparser; `build_arg_flags` falls through the `if "force" in args` at main.py:441 with `args.force = False`. Now the operator cannot use the diagnostic on a chip whose chip-id doesn't match (the Shield-3 floating-bus case from the original triage requires this).
**Why it happens:** `build_arg_flags(args)` introspects `args` defensively via `getattr(args, "blank_check", True)` and `if "force" in args` — missing attributes don't error, they default. Test passes locally; operator hits a blocker on bench.
**How to avoid:** Include `cc_parser.add_argument("-f", "--force", action="store_true", ...)` in the new subparser definition (as shown in Pattern 1 template above). This matches the precedent: `dev read` has `-f/--force` (main.py:384-388) for the same chip-id-mismatch use case.
**Warning signs:** Operator runs `firestarter dev consistency-check <chip>` on a missing-chip socket and gets `ERROR: Chip ID mismatch — got 0x... expected 0x...` with no way to bypass.

### Pitfall 6: Argparse subparser cannot have an argument named `runs` colliding with anything — verify clean

**What goes wrong:** Some sibling subcommand (e.g. future `dev` verb) might have a positional `runs` that argparse would clash with. Not currently a problem; flagged for the planner.
**Why it happens:** All siblings under `dev` (read, reg, addr) use unique flag names; consistency-check's flags (`--runs`, `--output-dir`, `--keep-files`, `--no-keep-files`, `--max-diffs`, `-q/--quiet`, `-f/--force`) don't collide with any of them.
**How to avoid:** Verified via `grep -n "add_argument" /workspaces/firestarter_app/firestarter/main.py | grep -E "(runs|output-dir|keep-files|max-diffs)"` — zero hits. Clean.
**Warning signs:** N/A — already clean.

## Code Examples

### Existing `dev` subparser pattern (template for the new `consistency-check` subparser)

```python
# Source: firestarter_app/firestarter/main.py:366-426 (verified 2026-05-21)
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
        "-f", "--force", action="store_true",
        help="Force read, even if the chip id doesn't match.",
    )

    # reg_parser, addr_parser definitions follow (lines 390-426)
    # NEW: cc_parser definition slots in after addr_parser, before the close of create_dev_args
```

### Existing `_run_state_machine` invocation for read (template for `consistency_check_eprom`'s inner loop body)

```python
# Source: firestarter_app/firestarter/eprom_operations.py:391-425 (verified 2026-05-21)
def read_eprom(self, eprom_name, eprom_data_dict, output_file=None,
                operation_flags=0, address_str=None, size_str=None) -> bool:
    with self._operation_context(eprom_name, eprom_data_dict, COMMAND_READ,
                                  operation_flags, address_str, size_str) as (cmd_data, _, op_name):
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

The new `consistency_check_eprom` calls into this exact pattern N times (one `with self._operation_context(...)` per iteration of the `for i in range(N)` loop), differing only in (a) the output filename varies per iteration, and (b) the return is the integer exit code from the verdict, not the bool from each individual run.

### Test pattern — stubbed-serial test driving the read loop

```python
# Source: firestarter_app/tests/test_decoder.py:475-542 (verified 2026-05-21)
# (full test reproduced earlier in §"Pattern 3"; key reusable elements:)
#   - from firestarter.eprom_operations import ClassProgressHandler, EpromOperationError
#   - from firestarter.messages import MSG_DATA_SENDING, MSG_DATA_CHUNK, MSG_MAIN_DONE
#   - fake_serial.feed(build_frame(MSG_DATA_CHUNK, payload_bytes))
#   - comm = make_comm()
#   - comm.send_ack = lambda: ack_calls.append(1)  # stub-out write-side
```

For Phase 26 tests at a higher level (driving `consistency_check_eprom` end-to-end), the cleaner pattern is to monkeypatch `EpromOperator._run_state_machine` directly (as in Pattern 3 above) rather than stub MSG_DATA_CHUNK frames — the test is about verdict logic, not protocol decoding.

### Operator-on-bench plan frontmatter (template for Plan 26-02 from prior `autonomous: false` plan)

```yaml
# Source: .planning/phases/12-28-pin-algo-0x07-bench-validation/12-01-PLAN.md:1-71 (Phase 12 paused but template stands)
---
phase: 26
plan: 02
type: execute
wave: 1
depends_on:
  - 26-01
files_modified:
  - .planning/v1.6-EVIDENCE.md
  - .planning/v1.6/bench-logs/{chip}-uno-{date}.log              # OPTIONAL — planner decides whether to use .planning/v1.6/ subdir
  - .planning/v1.6/bench-logs/{chip}-leonardo-{date}.log
  - .planning/v1.6/bench-logs/{chip}-uno328pb-{date}.log
autonomous: false
requirements:
  - REPRO-01
  - REPRO-02
requirements_addressed:
  - REPRO-01
  - REPRO-02
nyquist_compliant: manual-uat
tags:
  - bench-validation
  - read-bug-repro
  - consistency-check
  - operator-on-bench
  - v1.6
must_haves:
  truths:
    - "Operator runs `firestarter -p /dev/ttyACM0 dev consistency-check <chip> --runs 3 --output-dir .planning/v1.6/<chip>-uno-<TS>/` and the tool emits a FAIL verdict matching the empirical baseline from large-read-data-jitter-uno328pb.md."
    - "Operator runs the same command on /dev/ttyACM1 (leonardo) and captures verdict — FAIL expected per 1024-byte-buffer-doesn't-change-per-chunk-send-code reasoning, but explicit PASS with evidence also closes REPRO-02."
    - "Operator runs the same command on /dev/ttyUSB0 (uno328pb) and reproduces the 57.8% jitter rate (or thereabouts — chip data dependent)."
    - "Executor appends 3 rows to .planning/v1.6-EVIDENCE.md §Phase 26 Pre-fix Consistency-Check Baseline (one per board)."
  artifacts:
    - path: ".planning/v1.6-EVIDENCE.md"
      provides: "Pre-fix baseline rows for uno + leonardo + uno328pb"
      contains:
        - "Phase 26 — Pre-fix Consistency-Check Baseline"
        - "| uno |"
        - "| leonardo |"
        - "| uno328pb |"
---
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Shell loop `for i in 1 2 3; do firestarter read ...; sha256sum /tmp/read_$i.bin; done` (operator's existing pattern in `large-read-data-jitter-uno328pb.md` §"How to triage") | `firestarter dev consistency-check <chip> --runs 3` (Phase 26 deliverable) | 2026-05-21 (this phase) | The new CLI command crystallizes the shell-loop pattern into a permanent verb. Same hash function (SHA-256), same per-run artifact (`run_NN.bin` vs `read_$i.bin`), same comparison logic. The operator's mental model is preserved — `consistency-check` is just the loop in one command. |
| Bool return from `EpromOperator` methods (e.g. `dev_read_eprom() -> bool`, `read_eprom() -> bool`) | Int return from `consistency_check_eprom() -> int` (3-way exit code 0/1/2) | 2026-05-21 (this phase) | Justified divergence — 3-way verdict can't fit in bool. Precedent: `check_eprom_id() -> Tuple[bool, Optional[int]]` already breaks bool convention at eprom_operations.py:618 for the same reason. |
| Cross-phase evidence collected in per-phase ad-hoc files (v1.0 / v1.1 milestones) | Single cross-phase evidence file per milestone (`.planning/v1.5-BENCH-RESULTS.md`, `.planning/v1.3-BENCH-RESULTS.md`, now `.planning/v1.6-EVIDENCE.md`) | v1.3 milestone (2026-05-19) — established accretion pattern in `.planning/v1.3-BENCH-RESULTS.md` | All v1.6 phases (26 / 27 / 28 / 29) append to the same evidence file with a section per phase. Operator can grep / awk / diff baselines vs verifications across milestones consistently. |

**Deprecated / outdated:**

- **Text-prefix `OK:` / `DATA:` / `MAIN:` / `END:` / `ERROR:` line parsing** — superseded by Phase 8 W-04 wire format (MSG_DATA_CHUNK ID frames with CRC8). The diagnostic must NOT bypass the ID-frame path. `serial_comm.py:380-489` is the current MSG_DATA_CHUNK parser.

## Project Constraints (from CLAUDE.md)

Directives extracted from `/workspaces/CLAUDE.md` and `/workspaces/firestarter_app/CLAUDE.md` that constrain Phase 26 implementation:

1. **Repo structure (meta-repo CLAUDE.md):** All code changes for Phase 26 land in `/workspaces/firestarter_app/` (the host sub-repo), NOT the meta-repo. Meta-repo commits ONLY `.planning/` artifacts (CONTEXT, RESEARCH, PLAN, EVIDENCE files, this RESEARCH.md). The meta-repo's `git status` showing `M firestarter_app` (submodule pointer change) is expected during this phase and should NOT be committed unless the operator explicitly bumps the pointer.
2. **Serial protocol changes (meta-repo CLAUDE.md):** "Serial protocol changes must be kept in sync between `firestarter_app/firestarter/serial_comm.py` and `firestarter/src/firestarter.cpp`." Phase 26 does NOT change serial protocol (D-02 / D-13) — the diagnostic exercises the existing protocol unchanged. This constraint is therefore SATISFIED BY OMISSION; do not modify either file.
3. **Constants synchronization (meta-repo CLAUDE.md):** "Constants/flag bits are duplicated between `firestarter_app/firestarter/constants.py` (Python) and `firestarter/include/firestarter.h` (C++). Change both together." Phase 26 does NOT add or change any constants; it consumes existing `FLAG_FORCE` and `COMMAND_READ`. Constraint SATISFIED BY OMISSION.
4. **Buffer-size board differences (meta-repo CLAUDE.md):** "Uno has a 512-byte data buffer; Leonardo has 1024 bytes." Phase 26's diagnostic doesn't touch buffer-size logic; it consumes `BUFFER_SIZE` via `_calculate_buffer_size()` at eprom_operations.py:148 unchanged. Per REPRO-02, the leonardo's 1024-byte buffer halves the chunk count for a 64KB read — the diagnostic will surface that as "fewer/larger chunks" but still detect inter-run divergence the same way.
5. **Dev commands (firestarter_app CLAUDE.md):** `firestarter --help` should verify install. Phase 26 adds `dev consistency-check` to `firestarter dev --help` — the plan should include a sanity check at the end of Plan 26-01 that `firestarter dev consistency-check --help` returns the expected flag list.
6. **Database pipeline (firestarter_app CLAUDE.md):** `chip_database.json` is generated — do NOT edit by hand. Phase 26 only READS the DB via `EpromDatabase.get_eprom(...)`; no edit needed.
7. **Operator hands-on (user memory):** Operator (henrik@predictly.se) is hands-on with PlatformIO + AVR toolchain + GSD workflow. Surface decisions when in doubt rather than guessing. For Plan 26-02 (the bench wave), surface the chip choice explicitly (CONTEXT.md recommends SST27SF512 to match the 2026-05-21 baseline; operator may rotate).
8. **Shield rotation (user memory):** Operator owns 3 RURP shields (Rev 2.2, Rev 2.0, Rev 0+mod). EEPROM `hw_revision` byte can't distinguish 2.0 vs 2.2 — ALWAYS ASK when "swap the shield" comes up. For Phase 26, current shield (operator's choice) is fine; the bug is shield-invariant per the 3-shield triage. Plan 26-02 must NOT prescribe a shield — accept whatever shield is on the bench at session start.
9. **Branching (user memory):** v1.6-read-bug branches in all 3 repos; sub-repos fork off `beta`, meta-repo off `main`. Phase 26 D-13 already pins this — sub-repo `firestarter_app` cuts `v1.6-read-bug` from `beta` tip (post-v1.5 `3.0.0b4`). Firmware sub-repo branch deferred to Phase 28.
10. **328PB port (user memory):** Operator's 328PB-Uno on `/dev/ttyUSB0` (not /dev/ttyACM*). Plan 26-02 must use `/dev/ttyUSB0` for uno328pb invocations — do NOT default to /dev/ttyACM0 (regular Uno) or /dev/ttyACM1 (Leonardo).

## Environment Availability

Phase 26 has no external dependencies that require an environment probe. The diagnostic uses:

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.9+ | Host CLI | ✓ | 3.9+ (per firestarter_app/pyproject.toml) | — |
| `tqdm` | `ClassProgressHandler` | ✓ (already pinned) | already pinned by `firestarter_app` | — |
| `pyserial` | `SerialCommunicator` | ✓ (already pinned) | already pinned | — |
| `pytest` | D-10 test suite | ✓ (already pinned in dev extras) | already pinned | — |
| `hashlib` | SHA-256 verdict | ✓ (stdlib) | Python 3.9+ | — |
| `shutil` | `keep_files=False` cleanup | ✓ (stdlib) | Python 3.9+ | — |
| `pathlib.Path` | Output dir construction | ✓ (stdlib) | Python 3.9+ | — |
| Operator's uno + leonardo + uno328pb boards | Plan 26-02 bench wave | ✓ (operator-owned per memory `[[project_bench_findings_v15]]` and `[[user_firestarter_repo_layout]]`) | — | Plan 26-02 is `autonomous: false`; operator confirms hardware-available at session start. |
| RURP shield (any of operator's 3) | Plan 26-02 bench wave | ✓ (operator-owned) | — | Bug is shield-invariant per 3-shield triage; any shield works. |
| At least one EPROM in socket | Plan 26-02 bench wave | ✓ (SST27SF512 recommended per CONTEXT.md D-09) | — | D-02 passive mode also works on missing chip — operator can run against an empty socket if needed (would replicate Shield-3 floating-bus case). |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** None.

Phase 26's desk-side wave (Plan 26-01) requires zero environment beyond a Python 3.9+ + pytest setup, which is the firestarter_app sub-repo's baseline. The bench wave (Plan 26-02) requires the operator's three boards, which are pre-confirmed available per the v1.5 bench session memory.

## Validation Architecture

> Phase 26's diagnostic is fundamentally a verification tool — Phase 29 reuses it as the v1.6 acceptance gate. This section captures what *would* validate the diagnostic itself works correctly so the orchestrator can mint VALIDATION.md from it. Project config (`.planning/config.json`) does NOT have `workflow.nyquist_validation` set explicitly — per the orchestrator default, treat as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` (already pinned in `firestarter_app/pyproject.toml` dev extras) |
| Config file | `firestarter_app/pytest.ini` or `pyproject.toml` `[tool.pytest.ini_options]` (verified existing — all 5 current test files run cleanly via `pytest`) |
| Quick run command | `cd firestarter_app && pytest tests/test_consistency_check.py -x` |
| Full suite command | `cd firestarter_app && pytest` (82+ tests including the new 6) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REPRO-03 (D-10 #1) | All N runs return identical SHAs → exit 0 | unit (stubbed serial) | `pytest tests/test_consistency_check.py::TestConsistencyCheck::test_all_runs_identical_pass_exit_0 -x` | ❌ Wave 0 (will exist after Plan 26-01) |
| REPRO-03 (D-10 #2) | One byte differs at offset 0x123 in run 2 → exit 1, first divergence reported correctly | unit | `pytest tests/test_consistency_check.py::TestConsistencyCheck::test_one_byte_differs_in_run_2_exit_1 -x` | ❌ Wave 0 |
| REPRO-03 (D-10 #3) | Full scramble (3 distinct payloads) → exit 1, Distinct SHAs: 3 | unit | `pytest tests/test_consistency_check.py::TestConsistencyCheck::test_full_scramble_three_distinct_shas -x` | ❌ Wave 0 |
| REPRO-03 (D-10 #4) | State machine raises EpromOperationError mid-stream → exit 2 | unit (stubbed error) | `pytest tests/test_consistency_check.py::TestConsistencyCheck::test_serial_timeout_exit_2 -x` | ❌ Wave 0 |
| REPRO-03 (D-10 #5) | `keep_files=False` removes the output dir after verdict | unit | `pytest tests/test_consistency_check.py::TestConsistencyCheck::test_no_keep_files_removes_output_dir -x` | ❌ Wave 0 |
| REPRO-03 (D-10 #6) | `--runs 1` and `--runs 0` rejected → exit 2 with clear message | unit | `pytest tests/test_consistency_check.py::TestConsistencyCheck::test_runs_boundary_rejected -x` | ❌ Wave 0 |
| REPRO-03 (CLI surface) | `firestarter dev consistency-check --help` lists the documented flag set | smoke | `firestarter dev consistency-check --help` (manual) — OR add a 7th pytest case that imports `main.create_dev_args` and asserts the cc_parser has the right `dest`s | ❌ Wave 0 (optional 7th test) |
| REPRO-03 (dispatch chain) | argparse → operator method call is wired (no AttributeError, no KeyError) | integration (stubbed end-to-end) | `pytest tests/test_consistency_check.py::TestDispatchChain::test_main_dispatch_invokes_consistency_check -x` (NEW — see Wave 0 Gaps below; optional but recommended) | ❌ Wave 0 |
| REPRO-01 | uno board reproduces 64KB jitter | bench (manual UAT) | Operator runs `firestarter -p /dev/ttyACM0 dev consistency-check <chip>` — Plan 26-02 captures the verdict | bench-only |
| REPRO-02 | leonardo board reproduces 64KB jitter | bench (manual UAT) | Operator runs `firestarter -p /dev/ttyACM1 dev consistency-check <chip>` — Plan 26-02 captures the verdict | bench-only |
| Cross-tool compat | Phase 29 reuses the same tool — exit codes, output format, artifact layout must NOT change between v1.6 and v1.7+ | regression (golden file) | `pytest tests/test_consistency_check.py::TestConsistencyCheck::test_stdout_verdict_block_format -x` (NEW — checks specific strings in captured stdout against a golden snapshot) | ❌ Wave 0 (optional but valuable) |

### Sampling Rate

- **Per task commit (Plan 26-01 execution):** `cd firestarter_app && pytest tests/test_consistency_check.py -x` (< 5 seconds — all 6 D-10 cases use stubbed serial, no hardware)
- **Per wave merge (Plan 26-01 → branch tip):** `cd firestarter_app && pytest` (full suite, ~30-60 seconds; must remain at 82/82 or higher passing — the 6 new tests bring total to 88+)
- **Per bench session (Plan 26-02 execution):** Operator runs `firestarter -p /dev/ttyXXX dev consistency-check <chip> --runs 3 --output-dir .planning/v1.6/<chip>-<board>-<TS>/` once per board (3 invocations total). Verdict captured to evidence file.
- **Phase gate (`/gsd-verify-work 26`):** Full `firestarter_app` pytest suite green + `.planning/v1.6-EVIDENCE.md` has 3 rows under Phase 26 baseline section (one per board, all FAIL expected per the 3-shield-invariant prediction).

### Wave 0 Gaps

These files do not yet exist on `v1.6-read-bug` branch and Plan 26-01 must create them in Wave 0 before any Wave 1+ work proceeds:

- [ ] `firestarter_app/tests/test_consistency_check.py` — 6 D-10 test cases (Plan 26-01 RED→GREEN wave structure; the tests land in Wave 0 as failing scaffolds, then Wave 1 implements `consistency_check_eprom` to flip them green).
- [ ] (Optional) `firestarter_app/tests/test_consistency_check.py::TestDispatchChain` class — integration test verifying argparse subparser wiring + main.py dispatch reaches `EpromOperator.consistency_check_eprom`. Recommended but not in D-10 explicitly.
- [ ] (Optional) Golden-file snapshot test for stdout verdict block format — guards Phase 29 forward-compat (exit codes + output format must stay stable).
- [ ] `.planning/v1.6-EVIDENCE.md` — created by Plan 26-02 first task (header + empty Phase 26 baseline table). Operator-driven appends follow during bench wave.

**Framework install:** No install needed — pytest already pinned. No environment-level gaps.

### Validation Architecture — Cross-tool Forward Compatibility (Phase 29 reuse contract)

Phase 26's diagnostic IS Phase 29's acceptance gate tool. The following surfaces are LOAD-BEARING and must not change between v1.6 and v1.7+:

| Surface | Contract | Reason |
|---------|----------|--------|
| Exit code semantics (D-05) | 0=PASS, 1=FAIL, 2=hardware-error | Phase 29 VERIFY-01/02/03 gate on `exit 0`; any drift breaks the gate. |
| Stdout verdict block lines | "Consistency check: PASS" / "Consistency check: FAIL" exact strings | Phase 29 evidence-accretion scripts may grep this. |
| `--runs N` flag semantics | N≥2 required, default 3 | Phase 29 uses N=5 — must accept higher N. |
| Per-run artifact filename pattern | `run_{N:02d}.bin` (zero-padded 2-digit) | Phase 29 may diff pre-fix vs post-fix artifacts; consistent naming required. |
| Output dir naming pattern (when not overridden by `--output-dir`) | `consistency-check-<chip>-<board>-<TS>/` | Operator's mental model from Phase 26 carries to Phase 29. |
| Evidence-file row schema (D-08) | 9 columns: Board, Port, Chip, N, SHAs distinct, Divergent bytes, First-diverge offset, Verdict, Log | Phase 27/28/29 all append rows. Schema drift breaks markdown table rendering. |

Plan 26-01 must include a golden-file snapshot test (or equivalent assertion harness) that pins the stdout verdict block format. If the planner wants to make this more lightweight, capture stdout in a single test, regex-match the key lines (`r"Consistency check: (PASS|FAIL)"`, `r"Distinct SHAs: \d+"`, `r"First divergence: offset 0x[0-9A-F]+"`), and assert presence — that's sufficient to catch accidental format drift.

## Existing Code Insights

### Reusable Assets (verified — file:line citations)

- **`create_dev_args` → `subparsers` shape** — firestarter_app/firestarter/main.py:366-426. The `subparsers = dev_parser.add_subparsers(dest="dev_command", required=True)` at line 371 is the join point for the new `cc_parser = subparsers.add_parser("consistency-check", ...)` call.
- **`dev` dispatch block** — firestarter_app/firestarter/main.py:799-845. The new `elif args.dev_command == "consistency-check":` branch slots in after the `elif args.dev_command == "addr":` block (line 831).
- **`build_arg_flags(args)`** — firestarter_app/firestarter/main.py:439-451. Reads `args.blank_check`, `args.force`, `args.verbose`, `args.vpe_as_vpp`, `args.input_enable`, `args.chip_disable` defensively via `getattr`/`in`. New subparser must include `-f/--force` to enable the missing-chip case. `-q/--quiet` does NOT flow through `build_arg_flags` — it's local to the diagnostic.
- **`EpromOperator._run_state_machine`** — firestarter_app/firestarter/eprom_operations.py:232-265. Signature: `_run_state_machine(operation_name, main_phase_handler=None, **handler_kwargs) -> Tuple[bool, Optional[str]]`. Line 237 instantiates `ClassProgressHandler(self.progress_callback)` — **the diagnostic does not need to manage handler lifecycle**.
- **`EpromOperator._main_phase_read_data`** — firestarter_app/firestarter/eprom_operations.py:349-387. Signature: `_main_phase_read_data(progress, start_addr, end_addr, process_data_chunk_callback)`. The callback receives `(address, payload)` per chunk. Note line 372-381: MSG_DATA_CHUNK payload extraction is here — the suspected bug location per hypothesis #2 in `large-read-data-jitter-uno328pb.md`.
- **`EpromOperator.read_eprom`** — firestarter_app/firestarter/eprom_operations.py:391-425. The reference implementation — `consistency_check_eprom` invokes the same `_operation_context` + `_run_state_machine` + `_main_phase_read_data` triple per run.
- **`EpromOperator.dev_read_eprom`** — firestarter_app/firestarter/eprom_operations.py:429-454. Returns `bool` (line 429 signature). This is the "returns bool, not int" precedent the new method DIVERGES FROM with documented justification.
- **`EpromOperator._operation_context`** — firestarter_app/firestarter/eprom_operations.py:207-223. Context manager — opens serial connection on enter, disconnects on exit. Yields `(cmd_data, buffer_size, operation_name)` or `(None, None, None)` on setup failure.
- **`EpromDatabase.get_eprom` + `convert_to_programmer`** — firestarter_app/firestarter/database.py:493-520 + 522-565. Standard chip lookup + programmer-dict conversion. The dispatch block (main.py:801-807 for `dev read`) calls both verbatim.
- **`FirmwareManager.check_current_firmware`** — firestarter_app/firestarter/firmware.py:80-130. Returns `(port_name, current_version, board_name)`. Parsing logic at lines 105-117 extracts `board_name = parts[1].strip()` from the `"FW: <version>:<board>"` payload. Reusable for the verdict block's board-name display.
- **`ClassProgressHandler`** — firestarter_app/firestarter/eprom_operations.py:83-127. Wraps `tqdm.tqdm` with the `bar_format` at line 32. `if self.progress_callback:` branches around the bar — for `--quiet`, swap `self.progress_callback` to a no-op.
- **`tests/conftest.py::fake_serial` + `make_comm`** — tests/conftest.py:122-146. BytesIO-backed serial stub + factory that builds `SerialCommunicator` via `__new__` to bypass real serial init. Used by 30+ tests in `test_decoder.py`.
- **`tests/conftest.py::build_frame`** — tests/conftest.py:53-63. Assembles a Phase 8 W-04 wire frame (magic preamble + length + id + params + CRC8 + 0x0A). Reusable for end-to-end stubbed-serial integration tests.
- **`tests/test_decoder.py::test_chip_read_loop_concatenates_multiple_chunks`** — tests/test_decoder.py:475-542. End-to-end read-loop stub — the closest existing precedent for Phase 26's integration test.
- **`tests/test_firmware_install.py`** — tests/test_firmware_install.py (full file). Shows the monkeypatch-of-firestarter-module-attribute pattern (used at multiple sites; e.g. `monkeypatch.setattr(firmware, "Avrdude", _capture_init)`). Useful template for stubbing `FirmwareManager.check_current_firmware` if Plan 26-01's tests need to inject a fake board name.

### Established Patterns

- **`dev` as the permanent home for diagnostic verbs.** `dev read`, `dev reg`, `dev addr` — all low-level introspection commands. `consistency-check` fits this exact mold.
- **`EpromDatabase.get_eprom + convert_to_programmer` dispatch shape.** Every `dev` subcommand that targets a chip follows the same 5-line pattern (main.py:801-807 for `dev read`; main.py:832-838 for `dev addr`). Boilerplate; copy verbatim.
- **`_run_state_machine` as the bottleneck for any chip operation.** Read / write / verify / erase / blank / id / consistency-check all funnel through line 232. The diagnostic invokes it N times.
- **`autonomous: false` plans for operator-on-bench work.** Plan 12-01 is the template — `autonomous: false`, `requirements` + `requirements_addressed` arrays, `nyquist_compliant: manual-uat`, `must_haves.truths` list quoting "Operator runs X" actions, `must_haves.artifacts` listing log paths with regex `pattern` for grep-walkable cross-refs.
- **Evidence-file row schema (markdown table) per phase.** v1.5-BENCH-RESULTS.md + v1.3-BENCH-RESULTS.md both use this — single markdown table at the file root, append rows per chip/board pair, scope-photo paths and log paths inline as artifact references.
- **Submodule pointer drift expected.** Meta-repo's `git status` will show `M firestarter_app` after sub-repo work; do NOT commit the pointer bump unless operator asks explicitly (per user memory `user_firestarter_repo_layout`).

### Integration Points

- **CLI argparse subparser ↔ EpromOperator method ↔ existing read state machine.** The diagnostic is a thin orchestration layer; no new serial code, no new wire-protocol frames, no new firmware behavior. If the diagnostic doesn't trip the bug at the bench, the bug is not in the read state machine — which would invalidate every existing hypothesis in `large-read-data-jitter-uno328pb.md` and force a rethink in Phase 27.
- **`tests/conftest.py` ↔ new `test_consistency_check.py`.** Stubbed serial is sufficient for the 6 D-10 cases — no hardware needed in CI, no chip required, no platformio needed.
- **`v1.6-EVIDENCE.md` ↔ Phases 27, 28, 29.** Same evidence file accretes across the v1.6 milestone. Schema (9 columns per D-08) must stay stable.
- **`firestarter_app/v1.6-read-bug` branch ↔ `firestarter_app/beta` (eventually).** Plan 26-01's commits land on `v1.6-read-bug`; Phase 28 fix commits also land there; Phase 29 merges to `beta` to cut a fresh pre-release for the post-fix bench gate.
- **No new file under `firestarter/` (firmware sub-repo) in Phase 26.** D-13 — host-CLI-only.

## Pre-existing Hypotheses (DO NOT propose a fix candidate — Phase 27 owns RCA)

The Phase 26 plan should reference but NOT engage with these. They are documented for the `<truths>` block in Plan 26-01 so the executor knows what's out of scope:

1. **Host-side pyserial input buffer overflow** at 250000 baud (`large-read-data-jitter-uno328pb.md` §"Hypotheses" #1).
2. **Firmware MAIN-state phase-transition off-by-N chunk-end marker miss** (§"Hypotheses" #2).
3. **328PB-specific timing** — additional peripherals (USART1) creating instruction-cycle drift in inherited HAL (§"Hypotheses" #3).
4. **Missing `-D SERIAL_RX_BUFFER_SIZE=...`** or similar in `[env:uno328pb]` (§"Hypotheses" #4).

The 2026-05-21 triage already established **the bug is shield-invariant and present on a missing-chip Shield 3 floating bus** — variation is introduced between firmware bus-sample and host serial receive. Phase 27 will pick among hypotheses 1-4 (or surface a 5th); Phase 26's role is to add 2 more data points (uno + leonardo) that further narrow the hypothesis space.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| (none) | — | — | All claims in this research are either VERIFIED (line numbers / signatures cross-checked against live source 2026-05-21) or CITED (operator memory entries, CONTEXT.md decisions, REQUIREMENTS.md text, prior milestone bench-results files). No `[ASSUMED]` claims remain. |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed before planning.

## Open Questions

These are gaps the planner should resolve (or defer with explicit rationale) during PLAN.md drafting. None block Plan 26-01 from starting:

### Q1: How does `consistency_check_eprom` learn the firmware-reported board name for the default `output_dir` and verdict block?

**What we know:** `FirmwareManager.check_current_firmware(preferred_port=...)` returns `(port, version, board)` after opening + closing its own serial connection (firmware.py:80-130). That call sits inside `FirmwareManager`, not `EpromOperator` — `EpromOperator` does not currently invoke it. The `cmd_data` dict yielded by `_operation_context` does NOT carry board info (verified by reading `_setup_operation` at line 150-205 — the dict is the eprom_data_dict copy + cmd-specific keys; no firmware metadata).

**What's unclear:** The cleanest mechanism for `EpromOperator` to learn the board name without duplicating handshake code. Three plausible options:

- **(a)** `consistency_check_eprom` instantiates `FirmwareManager(self.config).check_current_firmware()` once at the top, before the read loop. Costs 1 extra serial round-trip (~1-2s; ~1% of the 180s run budget for N=3). Cleanest by far.
- **(b)** Add a `board` field to `SerialCommunicator` populated during `find_and_connect`'s probe (which already parses the same FW handshake string at serial_comm.py around line 756+). Requires touching `SerialCommunicator` — adds a small surface area to the change.
- **(c)** Drop the board name from the default output-dir entirely (`consistency-check-<chip>-<TS>/`); print it in the verdict block by invoking `check_current_firmware` lazily AFTER the runs complete (so the connection is closed and another handshake doesn't conflict).

**Recommendation:** Option (a) — explicit handshake at the top, well-tested code path, costs <1% of runtime, clearest mental model. Planner should pin this in the PLAN.md `<action>` block for the implementation task.

### Q2: Should Plan 26-01 include a 7th test that exercises the dispatch chain (argparse → main → operator) end-to-end?

**What we know:** D-10 lists exactly 6 test cases covering the operator-method internals. None of the 6 cover the argparse / main.py dispatch wiring. A future refactor of `create_dev_args` could silently break the wiring without tripping any of the 6 tests.

**What's unclear:** Whether the operator wants a 7th integration test or whether the manual `firestarter dev consistency-check --help` smoke from Plan 26-02's first action is sufficient.

**Recommendation:** Add the 7th test (TestDispatchChain). Cheap to write (~30 lines), prevents the silent-regression class. Pattern: instantiate `argparse.ArgumentParser`, call `create_read_args`/`create_dev_args` to populate, parse a fake CLI string `["dev", "consistency-check", "TEST_CHIP", "--runs", "3"]`, monkeypatch `EpromOperator.consistency_check_eprom` to a capture-args fake, assert it was called with the right kwargs. Not in D-10 explicitly — file under Claude's Discretion (#3 in CONTEXT.md decisions section was about `-q` flag; the planner has discretion to add tests beyond D-10's mandatory 6).

### Q3: Output-dir relative-vs-absolute path handling for the evidence-file accretion check

**What we know:** D-04 says "Append a row to `.planning/v1.6-EVIDENCE.md` IF `output_dir` is inside or under `.planning/`". This requires path comparison. `Path(output_dir).resolve().relative_to(Path('.planning').resolve())` raises `ValueError` if not inside `.planning/`; alternative is `str(Path(output_dir).resolve()).startswith(str(Path('.planning').resolve()))`.

**What's unclear:** Whether the operator launches the diagnostic from the meta-repo root (`/workspaces/`) or from within `firestarter_app/`. The latter makes `.planning/` not findable from `cwd`.

**Recommendation:** Document in the help text that the auto-evidence-accretion only fires when run from the meta-repo root with `--output-dir .planning/v1.6/<sub>/...`. For ad-hoc invocations from any other cwd, operator copy-pastes the verdict block into `.planning/v1.6-EVIDENCE.md` manually. Avoids brittle path-magic in the diagnostic.

### Q4: Plan 26-02 chip choice — fix at SST27SF512 or operator-rotate?

**What we know:** CONTEXT.md D-09 recommends SST27SF512 to match the 2026-05-21 baseline. CLAUDE.md user memory confirms SST27SF512 was the chip in socket during that triage.

**What's unclear:** Whether the operator wants to rotate one chip through 3 boards (cleanest comparison) or use 3 separate chips (faster — no chip-swap delay).

**Recommendation:** Plan 26-02 should leave the chip choice to the operator at session start. The diagnostic is chip-agnostic (D-02 passive mode); a single shared chip is preferred for comparability but not required. The evidence-file rows just need the chip-name column populated per row, which the verdict block already provides.

## Sources

### Primary (HIGH confidence — verified by direct file reading 2026-05-21)

- `firestarter_app/firestarter/main.py` (lines 1-861) — argparse / dispatch structure, create_dev_args (line 366), build_arg_flags (line 439), dev dispatch (line 799), all sibling subparsers (read/reg/addr at 373/390/419).
- `firestarter_app/firestarter/eprom_operations.py` (lines 1-642) — EpromOperator class (line 130), ClassProgressHandler (line 83), _run_state_machine (line 232), _main_phase_read_data (line 349), read_eprom (line 391), dev_read_eprom (line 429), _operation_context (line 207), _setup_operation (line 150).
- `firestarter_app/firestarter/firmware.py` (lines 75-130) — check_current_firmware signature + return shape, payload parsing at lines 105-117.
- `firestarter_app/firestarter/database.py` (lines 480-565) — get_eprom_config (line 453), get_eprom (line 493), convert_to_programmer (line 522).
- `firestarter_app/tests/conftest.py` (lines 1-146) — fake_serial / make_comm / build_frame fixtures + helpers.
- `firestarter_app/tests/test_decoder.py` (lines 458-542) — closest existing precedent for end-to-end stubbed read-loop tests (`test_data_chunk_payload_exposed_via_response_payload_field`, `test_chip_read_loop_concatenates_multiple_chunks`).
- `firestarter_app/tests/test_firmware_install.py` (lines 1-120) — monkeypatch-an-external-module attribute pattern (Avrdude stubbing).
- `firestarter_app/tests/test_fwguard.py` (full file, 125 lines) — `unittest.mock.patch.object(SerialCommunicator, ...)` pattern for stubbing serial layer at test time.
- `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-CONTEXT.md` — D-01..D-13 decisions, canonical refs, code insights, deferred items.
- `.planning/REQUIREMENTS.md` §"Reproduction & Triage" — REPRO-01, REPRO-02, REPRO-03 verbatim text.
- `.planning/STATE.md` — v1.6 milestone position, decisions, branch model.
- `.planning/ROADMAP.md` §"v1.6 — Fix the Read Bug" §"Phase 26" — goal, dependencies, success criteria 1-5.
- `.planning/todos/pending/large-read-data-jitter-uno328pb.md` — bug evidence, 3-shield A/B/C triage, "How to triage" shell loop pattern, 4 hypotheses for Phase 27.
- `.planning/v1.5-BENCH-RESULTS.md` — row-schema precedent (analogous to D-08).
- `.planning/v1.3-BENCH-RESULTS.md` — row-schema precedent (D-08 § cycle results table).
- `.planning/phases/12-28-pin-algo-0x07-bench-validation/12-01-PLAN.md` (frontmatter lines 1-71) — operator-on-bench `autonomous: false` plan template for Plan 26-02.
- `.planning/milestones/v1.5-phases/24-bench-validation-328pb-uno/24-SUMMARY.md` — recent (operator-driven, not via /gsd-plan-phase) bench-session reference.
- `/workspaces/CLAUDE.md` and `/workspaces/firestarter_app/CLAUDE.md` — project conventions, repo structure, constants synchronization rules.
- Operator memory entries `project_bench_findings_v15`, `user_firestarter_repo_layout`, `user_shield_revisions`, `feedback_branching`.

### Secondary (MEDIUM confidence)

- None — Phase 26 is grounded entirely in primary sources (existing code + locked decisions). No web research, no external library docs needed.

### Tertiary (LOW confidence — flagged for validation)

- None.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — every package + version verified against firestarter_app dependency pinning; zero new deps.
- Architecture: HIGH — line-by-line cross-check of all file:line references in CONTEXT.md against live source.
- Pitfalls: HIGH (Pitfalls 1, 2, 3, 4, 5) / MEDIUM (Pitfall 6) — Pitfalls 1-5 are verified by code reading; Pitfall 6 is a defensive check ("no current collision") that depends on no future subcommand introducing a `runs` argument before Phase 26 lands.
- Validation Architecture: HIGH — D-10's 6 test cases are explicit in CONTEXT.md; framework + commands verified against live `tests/` layout.

**Research date:** 2026-05-21
**Valid until:** 2026-06-20 (30 days — Phase 26 sits in active development; firestarter_app sub-repo is on `v1.6-read-bug` branch with no main-branch drift expected).

## RESEARCH COMPLETE

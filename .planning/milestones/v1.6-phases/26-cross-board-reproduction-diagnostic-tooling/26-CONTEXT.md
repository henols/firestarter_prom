# Phase 26: Cross-board Reproduction & Diagnostic Tooling - Context

**Gathered:** 2026-05-21
**Status:** Ready for planning
**Source:** /gsd:discuss-phase 26 (Auto Mode — auto-resolved gray areas with recommended options; no AskUserQuestion prompts per harness Auto Mode)

<domain>
## Phase Boundary

Phase 26 delivers **(a) an enduring host CLI diagnostic that measures consecutive-read consistency on a static EPROM and reports a pass/fail verdict with concrete divergence evidence, and (b) the pre-fix baseline evidence captured by running that diagnostic against all three controllers (`uno`, `leonardo`, `uno328pb`)**.

Phase 26 is REPRO-only — it proves the bug exists and is cross-board, and ships the tool both Phase 27 (RCA) and Phase 29 (post-fix verification) will reuse. No firmware change. No fix attempt. No RCA narrative — Phase 27 owns that.

**In scope:**
- New host CLI subcommand `firestarter dev consistency-check <chip>` under the existing `dev` subparser in [firestarter_app/firestarter/main.py](firestarter_app/firestarter/main.py) (D-01).
- New operation method on `EpromOperator` in [firestarter_app/firestarter/eprom_operations.py](firestarter_app/firestarter/eprom_operations.py) — `consistency_check_eprom(...)` — that wraps `read_eprom`'s state machine N times against the same chip without modifying it (D-02, D-03).
- Pytest unit tests under `firestarter_app/tests/test_consistency_check.py` exercising the host-side verdict logic with stubbed serial fixtures from `tests/conftest.py` (D-10).
- New evidence file `.planning/v1.6-EVIDENCE.md` — pre-fix baseline rows for the 3 boards × N runs (D-08, SC#5).
- Per-run binary artifact directory layout under operator's working dir, default `consistency-check-<chip>-<board>-<timestamp>/run_<N>.bin` so divergent reads can be re-diffed post-hoc (D-04).

**Out of scope:**
- The fix itself (Phase 28).
- RCA narrative — where in the code the corruption happens, why it happens (Phase 27).
- Introducing-commit bisection (Phase 27 / RCA-03).
- Any firmware change in `firestarter/` sub-repo (Phase 26 is host-CLI-only; firmware sub-repo branch creation deferred to Phase 28 — D-13).
- New top-level CLI surface — the diagnostic lives under `dev` permanently as the canonical pre-/post-fix regression check (D-01).
- Write-then-read mode — the diagnostic is read-only / passive against an unmodified chip (D-02 — the bug manifests even with no chip in socket per the 3-shield Shield-3 floating-bus finding, so writing is unsafe and unnecessary).
- Low-rate (1KB) jitter coverage — Phase 26's diagnostic is full-chip-only; `dev read -s 1024` already exists for the 1KB case and Phase 29 / VERIFY-03 reuses that path (D-06).
- `--all-boards` orchestrator — per-port, per-invocation only; operator switches boards manually using existing `-p /dev/ttyXXX` muscle memory from Phase 24 BENCH (D-09).
- `chip_database.json` modification — the diagnostic uses the existing `EpromDatabase.get_eprom()` lookup unchanged.

</domain>

<decisions>
## Implementation Decisions

### CLI subcommand placement, naming, signature

- **D-01: New subcommand `firestarter dev consistency-check <chip>` under the existing `dev` subparser** (see `create_dev_args` at [firestarter_app/firestarter/main.py:366](firestarter_app/firestarter/main.py#L366)).
  Signature (locked):
  ```
  firestarter [-p PORT] dev consistency-check <chip>
      [--runs N]              # default 3 — REPRO-03 / ROADMAP SC#1 minimum is N≥3
      [--output-dir DIR]      # default consistency-check-<chip>-<board>-<timestamp>/
      [--keep-files / --no-keep-files]  # default --keep-files (post-hoc diff)
      [--max-diffs M]         # default 10 — first M divergent offsets shown
      [-q / --quiet]          # suppress per-run tqdm progress bars
  ```
  Rationale: `dev` is the established home for diagnostic / introspection commands (`dev read`, `dev reg`, `dev addr` already live there per [main.py:373-426](firestarter_app/firestarter/main.py#L373-L426)). The ROADMAP explicitly says the command "persists in the CLI permanently (becomes the canonical post-fix regression check)" — `dev` is exactly the right surface area for permanent debug/diagnostic verbs. The verb `consistency-check` is chosen verbatim from REPRO-03 / ROADMAP SC#1. Hyphen is unusual under `dev` (siblings are single words) but the meaning is clearer than alternatives (`bytecheck`, `repeat-read`, `shadiff`) and the ROADMAP fixed it.

  Dispatch shape (mirror existing pattern at [main.py:799-818](firestarter_app/firestarter/main.py#L799-L818)):
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
          operation_flags=build_arg_flags(args),
      )
  ```
  The exit-code semantics (D-05) flow back through this return; the operator method returns the integer exit code directly rather than the bool that `read_eprom` returns.

### Read mode (passive, not write-then-read)

- **D-02: Diagnostic is read-only / passive.** The command performs N consecutive `read_eprom` invocations against the chip currently in socket without modifying it. No prior write step; no baseline image generation.
  Rationale (closes a real gray area):
  - The 3-shield A/B/C triage on 2026-05-21 (logged in [.planning/todos/pending/large-read-data-jitter-uno328pb.md](.planning/todos/pending/large-read-data-jitter-uno328pb.md) §"3-shield A/B/C triage") observed jitter on Shield 3 with no chip in socket — bus floats / pulls to `0x00`, but the host still received different `0x00`-mostly streams across consecutive reads. The variation cannot be coming from the chip. **So the diagnostic does not need a known-good baseline image to detect the bug — it only needs to compare run-N against run-N-1.**
  - UV-EPROMs are one-shot programmable; running an active write step inside a diagnostic is unsafe (irreversibly burns bits) and contraindicated for a tool the operator must be able to run at will against any chip in any state.
  - Verdict logic is simply "are all N SHA-256s equal?" — no chip-database `data.bin` lookup, no equality-against-known-image. This keeps the diagnostic chip-agnostic: works on UV-EPROMs, electrically-erasable EEPROMs, blank chips, partially-programmed chips, and even empty sockets (returns whatever the bus pulls to).

### EpromOperator method

- **D-03: New method `EpromOperator.consistency_check_eprom(eprom_name, eprom_data_dict, runs=3, output_dir=None, keep_files=True, max_diffs=10, operation_flags=0) -> int`** in [firestarter_app/firestarter/eprom_operations.py](firestarter_app/firestarter/eprom_operations.py).
  Internal shape (locked):
  1. Resolve `runs`, `output_dir`, materialize `output_dir` if needed.
  2. Loop `i in 1..runs`:
     - Build a per-run binary path `{output_dir}/run_{i:02d}.bin`.
     - Reuse the same state-machine handler `_main_phase_read_data` ([eprom_operations.py:349](firestarter_app/firestarter/eprom_operations.py#L349)) via the same `_run_state_machine` orchestration `read_eprom` uses ([eprom_operations.py:413-419](firestarter_app/firestarter/eprom_operations.py#L413-L419)). Do not duplicate the chunked-read loop — the diagnostic exercises the exact code path the bug lives in.
     - Stream the chip into the per-run binary via the same `_write_to_file` inner-closure pattern as `read_eprom`.
     - Compute SHA-256 of the binary after each run (incremental update during streaming preferred; simple `hashlib.sha256(open(path,'rb').read()).hexdigest()` is acceptable at 64KB sizes — runtime budget is dominated by serial throughput, not hashing).
     - Append `(run_i, sha256_hex, bytes_written)` to an in-memory results list.
  3. After all N runs: compute the verdict (D-05) and the divergence report (D-04).
  4. Append a row to `.planning/v1.6-EVIDENCE.md` IF `output_dir` is inside or under `.planning/` (per D-08 evidence-accretion). Otherwise just print stdout — operator captures evidence manually for ad-hoc invocations.
  5. Optionally delete per-run binaries if `keep_files=False`.
  6. Return integer exit code per D-05.

  **Reuse-not-duplicate rule:** the read state machine + chunked-data handler is the *exact* code path the bug lives in. Phase 26's diagnostic MUST exercise it unchanged — no shortcuts, no separate single-call read path. If the diagnostic doesn't trip the bug, the diagnostic is broken, not the bug fixed. (This is the analogue of D-02 from Phase 12: do not modify shared infrastructure; observe it.)

### Output / verdict reporting

- **D-04: Stdout verdict + divergence detail + per-run artifact directory.**
  - For each run, print: `Run {i}/{N}: SHA-256 {hexdigest}  bytes={size}  elapsed={s}s`.
  - After all runs, print a verdict block:
    ```
    Consistency check: PASS         # or "FAIL"
    Chip: <chip>  Board: <board reported by firmware fw>  Port: /dev/ttyXXX
    Runs: N=3
    Distinct SHAs: 1                # or e.g. 3 for full divergence
    Output dir: consistency-check-<chip>-<board>-<timestamp>/
    ```
  - On FAIL (distinct_shas > 1) also print:
    ```
    First divergence: offset 0x{offset:04X}  (run_1=0x{b1:02X}, run_2=0x{b2:02X})
    Total divergent bytes (run_1 vs run_2): {count} / {total}  ({pct:.1f}%)
    First {max_diffs} divergent offsets: 0x{o1:04X}, 0x{o2:04X}, ...
    ```
  - `--max-diffs M` controls the offset list length (default 10).
  - Output dir name format: `consistency-check-<chip>-<board>-<YYYY-MM-DD-HHMMSS>/` — sortable + machine-grep-friendly. Operator can override with `--output-dir` for placement under `.planning/v1.6/` directly.
  - "Board" comes from the firmware handshake reply (`firestarter fw` already extracts this; reuse the same handshake parser, or — simpler — derive from `cmd_data` if it carries board info; otherwise leave as the port string and add board on a subsequent line).

### Exit code semantics

- **D-05: Exit codes (CI/script-usable):**
  | Exit code | Meaning |
  |-----------|---------|
  | `0`       | All N reads byte-identical (PASS) |
  | `1`       | One or more reads diverge (FAIL — bug detected) |
  | `2`       | Hardware / serial / timeout / chip-not-detected error (could not complete N reads) |
  Rationale: `0` vs `1` is the standard success/failure split that wraps cleanly in shell loops and CI checks. `2` distinguishes "ran cleanly and found the bug" from "couldn't run at all" — useful for Phase 29 (VERIFY) where `0` is the gate and `2` is "operator needs to debug the rig before re-running". Same convention as `grep` exit codes (`0`=match, `1`=no match, `2`=error).

### Chunk-size scope

- **D-06: Full-chip only.** Phase 26's `consistency-check` does NOT take a `--chunk-size N` or `--size N` flag. The full chip size from `chip_database.json` is the read size.
  Rationale:
  - REPRO-03 / ROADMAP SC#1 specify "N≥3 consecutive `read` operations against a static chip" — full-chip is the canonical case the bug manifests at 57.8%.
  - The low-rate (1KB) jitter is already covered by existing `dev read -s 1024` (per [main.py:373-388](firestarter_app/firestarter/main.py#L373-L388)). Phase 29 / VERIFY-03 wraps that in an operator shell loop ("`for i in 1..5; do firestarter dev read -s 1024 ...`") rather than building a parallel diagnostic. Same wire path, same chunked-read state machine — the 1KB case stresses chunk-count math less but uses the identical send code.
  - If, after Phase 27 RCA, the fix turns out to differ between full-chip and 1KB modes, the planner can add `--chunk-size N` to `dev consistency-check` in a future milestone. Don't pre-build for a hypothetical fix shape.

### Cross-board execution model

- **D-07: Operator-driven per-port invocation; no orchestrator.**
  - Operator runs the command three times — once per port (one port per board: `/dev/ttyACM0` = uno, `/dev/ttyACM1` = leonardo, `/dev/ttyUSB0` = uno328pb per memory `[[project_bench_findings_v15]]`). The exact port↔board mapping is operator's environment and may rotate between sessions.
  - No `--all-boards` orchestrator. Adds complexity (port enumeration, board-name detection, per-board chip-presence validation) for marginal benefit — operator has already established the per-port muscle memory in Phase 24 BENCH cycles.
  - Diagnostic prints the firmware-reported board name in the verdict block (D-04) so the evidence file row is self-identifying even if the port string differs across sessions.

### Evidence file

- **D-08: `.planning/v1.6-EVIDENCE.md` is the cross-phase evidence-accretion artifact for v1.6** (named in ROADMAP "Cross-cutting evidence accretion" structural note). Phase 26 creates the file with the pre-fix baseline section.
  Schema (mirror of `.planning/v1.5-BENCH-RESULTS.md` + `.planning/v1.3-BENCH-RESULTS.md` row shape):
  ```
  ## Phase 26 — Pre-fix Consistency-Check Baseline (2026-05-2X)

  | Board | Port | Chip | N | SHAs distinct | Divergent bytes (run1 vs run2) | First-diverge offset | Verdict | Log |
  |-------|------|------|---|---------------|------------------------------|----------------------|---------|-----|
  | uno328pb | /dev/ttyUSB0 | SST27SF512 | 3 | 3 | 37,883 / 65,536 (57.8%) | 0x009E | FAIL (jitter reproduced) | consistency-check-SST27SF512-uno328pb-2026-05-2X-HHMMSS/ |
  | uno | /dev/ttyACM0 | <chip> | 3 | TBD | TBD | TBD | TBD | ... |
  | leonardo | /dev/ttyACM1 | <chip> | 3 | TBD | TBD | TBD | TBD | ... |
  ```
  - uno328pb row's expected values come from the existing 2026-05-21 triage in `large-read-data-jitter-uno328pb.md`; the bench wave just re-confirms with the new tool.
  - uno + leonardo rows are the new data REPRO-01 + REPRO-02 produce.
  - Phase 27 RCA appends a §"RCA Findings" section to the same file.
  - Phase 28 fix appends commit references.
  - Phase 29 inverts — adds a "Post-fix Consistency-Check Verification" section with all `Verdict = PASS, SHAs distinct = 1`. This is the gate.

  **Important — schema is shared.** Phase 27/28/29 must read this CONTEXT.md (or the live `v1.6-EVIDENCE.md`) and follow the same row schema so the file is internally consistent across phases.

### Bench-wave plan structure

- **D-09: 2 plans for Phase 26** (sized so each closes one requirement cluster):
  - **26-01 (desk-side, autonomous):** Implement REPRO-03 — the `dev consistency-check` subcommand, the `consistency_check_eprom` operator method, pytest unit tests under `tests/test_consistency_check.py`. Lands in `firestarter_app/` on `v1.6-read-bug` branch.
  - **26-02 (operator-on-bench, `autonomous: false`):** Run REPRO-01 + REPRO-02 + SC#5 — execute the new diagnostic against the operator's uno, leonardo, uno328pb (3 boards, same socketed chip rotated through each — recommended SST27SF512 to match the existing 2026-05-21 triage baseline). Populate `.planning/v1.6-EVIDENCE.md` Phase 26 baseline rows.
  - Plan dependency: 26-01 → 26-02. 26-01 must ship + the operator must have installed the new pre-release / dev build before 26-02 can run.
  - **Do NOT split bench across boards into 3 separate plans.** The cross-board bench is naturally one operator session (chip rotation, same harness, same evidence file) — split would add overhead without diagnostic granularity. This mirrors the v1.3 Phase 12 D-11 "one plan per chip with both boards inside" pattern, inverted: "one plan per session, with all boards inside".

### Tests

- **D-10: `firestarter_app/tests/test_consistency_check.py` — host-side pytest only.**
  Test cases (locked):
  1. **All runs identical** — stub `_main_phase_read_data` (or the serial layer below it) to return the same 65,536-byte stream on every call → exit 0, single SHA reported, FIRST-DIVERGENCE-OFFSET path not executed.
  2. **One byte differs in run 2** — stub to return identical streams on calls 1 + 3 but mutate one byte at offset 0x123 on call 2 → exit 1, `Distinct SHAs: 2`, `First divergence: offset 0x0123`, byte-diff count = 1.
  3. **Full scramble across runs** — stub to return three different streams → exit 1, `Distinct SHAs: 3`, divergence report at offset 0x0000.
  4. **Serial timeout / hardware error** — stub the underlying state machine to raise `EpromOperationError` mid-stream → exit 2, no SHA reported for the failed run.
  5. **`--keep-files False`** — after a successful run, output dir is removed.
  6. **`--runs` boundary** — `--runs 1` is rejected (verdict requires at least 2 to compare); `--runs 0` rejected; CLI returns exit 2 with a clear message.

  Reuse existing `tests/conftest.py` serial-stubbing fixtures (the same scaffolding `test_firmware_install.py` + `test_fwguard.py` already use). Phase 28's bilateral host+firmware unit test (FIX-02) is separate and not pre-built here.

### Progress / verbosity

- **D-11: Per-run `tqdm` progress bar; `-q/--quiet` suppresses.**
  - Default: one progress bar per run, 3 bars total for default N=3 (consistent with existing `read_eprom` progress reporting via `ClassProgressHandler`).
  - `-q` mode: no progress bars; verdict block still printed. Used when piping to a log file (`firestarter ... dev consistency-check ... -q 2>&1 | tee log.txt`).
  - The existing `-v / --verbose` top-level flag continues to control serial-line trace logging unchanged; do not couple `-q` and `-v`.

### Hashing approach

- **D-12: `hashlib.sha256` over the per-run binary file, computed after `read_eprom` finishes.**
  - Simpler than incremental hashing during the read stream — at 64KB, post-read hashing is microseconds; the 60-second serial-transfer dominates total runtime by 6 orders of magnitude.
  - Defensive: `hashlib.sha256(open(path, 'rb').read()).hexdigest()` is one line. For files >> RAM (not in scope here — chips top out at 512K) the planner can switch to chunked-update.
  - SHA-256 was named in ROADMAP SC#1 and is the operator's convention from the original 2026-05-21 triage (`sha256sum /tmp/read_$i.bin` per `large-read-data-jitter-uno328pb.md` §"How to triage"). Don't switch to SHA-1 / xxhash / etc. — match the operator's mental model.

### Branch flow

- **D-13: Host-side-only this phase.** Branch work:
  - `firestarter_app/`: cut `v1.6-read-bug` from current `beta` tip (post-v1.5 ship `3.0.0b4`). Plans 26-01 lands here.
  - `firestarter/`: NO branch yet. Phase 26 does not modify firmware (the diagnostic exercises the existing read state machine unchanged). The firmware `v1.6-read-bug` branch is cut in Phase 28 when the fix lands.
  - Meta-repo (`.planning/`): branch is already `main`, per ROADMAP convention; v1.6 phase artifacts (this CONTEXT.md, plans, EVIDENCE.md) commit to `main` as they're created.
  - Bench-wave (26-02) does not need a fresh pre-release tag — operator runs the dev build directly on each board, OR cuts an ad-hoc `3.0.0b5-rcaN` from `v1.6-read-bug` if avrdude-install is preferred (planner's call). Recommended: dev install via `pip install -e .` from the `v1.6-read-bug` branch in `firestarter_app/`, no avrdude needed for a host-only change.

### Claude's Discretion

- **Exact `--output-dir` default naming.** D-04 specifies `consistency-check-<chip>-<board>-<YYYY-MM-DD-HHMMSS>/` but the planner can swap to `<chip>_<board>_<timestamp>` or pure-numeric timestamps if it cleans up `ls` output more cleanly. Operator preference dominates.
- **Progress-bar style.** D-11 names `tqdm`; existing `read_eprom` uses a `ClassProgressHandler` wrapper — reusing that is the cleanest path. Whether the wrapper exposes a per-run reset or the diagnostic instantiates a fresh handler per run is the planner's call.
- **`-q/--quiet` vs `--quiet`.** Short flag could collide with future top-level flags; planner can drop the short form if needed.
- **Whether 26-02 reads through a single chip rotated across boards, vs three separate chips (one per board).** D-09 recommends rotating one chip (SST27SF512) for cleanest comparison vs Phase 24 baseline; if the operator has 3 socketed boards on the bench simultaneously and prefers parallel reads, that's acceptable as long as each row's chip identity is recorded.
- **Whether to print the verdict block JSON-ified as well.** Optional `--json` flag for CI consumption is reasonable but not required by REPRO-03. Defer to v1.7+ unless a Phase 29 use case demands it.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope + requirements (authoritative)
- [.planning/ROADMAP.md](.planning/ROADMAP.md) §"v1.6 — Fix the Read Bug" §"Phase 26: Cross-board Reproduction & Diagnostic Tooling" — goal + Success Criteria 1–5 + Plans = TBD
- [.planning/ROADMAP.md](.planning/ROADMAP.md) §"Structural Notes" — bench-gated-vs-desk-side split + cross-cutting evidence accretion pattern + GATE-1.6 non-regression
- [.planning/REQUIREMENTS.md](.planning/REQUIREMENTS.md) §"Reproduction & Triage (REPRO)" — REPRO-01 / REPRO-02 / REPRO-03 verbatim + traceability table at file end
- [.planning/PROJECT.md](.planning/PROJECT.md) §"Current Milestone: v1.6 Fix the Read Bug" — milestone goal, locked decisions, Definition of Done, GATE-1.6 non-regression

### Bug evidence (the empirical baseline Phase 26 reproduces with the new tool)
- [.planning/todos/pending/large-read-data-jitter-uno328pb.md](.planning/todos/pending/large-read-data-jitter-uno328pb.md) — full bug evidence: 57.8% jitter at 64KB, 0.1% at 1KB, 3-shield A/B/C triage, "How to triage" shell-loop pattern (the diagnostic implements this pattern as a permanent CLI command), pre-existing-bug demotion rationale
- [.planning/STATE.md](.planning/STATE.md) — current milestone position; updated after this phase commits

### Existing CLI surface (the diagnostic plugs in here)
- [firestarter_app/firestarter/main.py](firestarter_app/firestarter/main.py) §`create_dev_args` lines 366-426 — `dev` subparser; siblings `dev read` / `dev reg` / `dev addr` are the placement template for `dev consistency-check`
- [firestarter_app/firestarter/main.py](firestarter_app/firestarter/main.py) lines 799-845 — `args.dev_command` dispatch block; new `consistency-check` branch slots in alongside `read`/`reg`/`addr`
- [firestarter_app/firestarter/main.py](firestarter_app/firestarter/main.py) §`build_arg_flags` lines 439-451 — operation_flags builder reused unchanged

### Existing read state machine (the code path the diagnostic exercises unchanged)
- [firestarter_app/firestarter/eprom_operations.py](firestarter_app/firestarter/eprom_operations.py) §`_main_phase_read_data` lines 349-387 — MAIN-state read handler; MSG_DATA_CHUNK frame parser; the per-chunk send code the bug is suspected to live near (per hypothesis #2 in the bug report)
- [firestarter_app/firestarter/eprom_operations.py](firestarter_app/firestarter/eprom_operations.py) §`read_eprom` lines 391-425 — full-chip read public API; the diagnostic loops this N times
- [firestarter_app/firestarter/eprom_operations.py](firestarter_app/firestarter/eprom_operations.py) §`dev_read_eprom` lines 429-454 — partial / dev-mode read (for cross-referencing the 1KB case in Phase 29 VERIFY-03 — NOT for Phase 26 itself per D-06)
- [firestarter_app/firestarter/serial_comm.py](firestarter_app/firestarter/serial_comm.py) §MSG_DATA_CHUNK decoding lines 380-489 — ID-frame parser with CRC8 + variable-length payload extraction; the layer where mid-chunk corruption (if host-side) would manifest

### Database lookup
- [firestarter_app/firestarter/data/chip_database.json](firestarter_app/firestarter/data/chip_database.json) — chip-name → algorithm + memory-size lookup; the diagnostic uses `EpromDatabase.get_eprom()` unchanged for chip resolution
- [firestarter_app/firestarter/database.py](firestarter_app/firestarter/database.py) §`EpromDatabase.get_eprom` — chip resolution + `convert_to_programmer` translation
- [firestarter_app/CLAUDE.md](firestarter_app/CLAUDE.md) §"Wire Protocol" + §"Database Pipeline" — JSON command shape + WARNING-5 override semantics (background; not touched by this phase)

### Existing tests + harness (template for new test file)
- [firestarter_app/tests/conftest.py](firestarter_app/tests/conftest.py) — serial-stubbing fixtures reused by `test_consistency_check.py`
- [firestarter_app/tests/test_firmware_install.py](firestarter_app/tests/test_firmware_install.py) — example of pytest exit-code assertions over an `EpromOperator` method; the new tests follow the same shape
- [firestarter_app/tests/test_fwguard.py](firestarter_app/tests/test_fwguard.py) — example of stubbed-serial test exercising state-machine paths
- [firestarter_app/firestarter_test.sh](firestarter_app/firestarter_test.sh) — operator-bench harness (not modified; reference only)

### Cross-phase artifacts (this phase creates, downstream phases extend)
- `.planning/v1.6-EVIDENCE.md` — created here by Phase 26 plan 26-02 with pre-fix baseline; Phase 27 RCA appends; Phase 28 fix appends commit refs; Phase 29 inverts with post-fix verification. Schema in D-08 is shared across phases — D-08 is the single source of truth for the row shape.

### Project memory (always-on guidance)
- `[[user_firestarter_repo_layout]]` — meta-repo + 2 sub-repos; `.planning/` tracked here only; sub-repo branches diverge from `beta`
- `[[feedback_branching]]` — `v1.6-read-bug` branches in all 3 repos; sub-repos fork off `beta`, meta-repo off `main`; never commit milestone work directly to `beta`/`main`
- `[[project_bench_findings_v15]]` — 328PB-Uno on `/dev/ttyUSB0`, urclock bootloader; Phase 24 baseline chip SST27SF512 is the recommended Phase 26 bench chip
- `[[user_shield_revisions]]` — operator owns Rev 2.2, Rev 2.0, modified Rev 0; EEPROM hw_revision byte can't distinguish 2.0 vs 2.2 — ASK when "swap the shield" comes up. For Phase 26, current shield (operator's choice) is fine; the bug is shield-invariant per the 3-shield triage.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`EpromOperator._run_state_machine` + `_main_phase_read_data` + `read_eprom`** ([eprom_operations.py:349-425](firestarter_app/firestarter/eprom_operations.py#L349-L425)) — the full read code path. `consistency_check_eprom` calls into this verbatim N times, no shortcuts. **This is load-bearing for Phase 26's diagnostic to be diagnostic** (D-03 reuse-not-duplicate rule): the tool must exercise the exact code path the bug lives in, or it cannot reproduce it.
- **`EpromDatabase.get_eprom` + `convert_to_programmer`** ([database.py](firestarter_app/firestarter/database.py)) — chip resolution + DIP-pin-to-bus-config translation. Diagnostic uses the same path the existing `dev read` uses; no DB modification.
- **`build_arg_flags`** ([main.py:439-451](firestarter_app/firestarter/main.py#L439-L451)) — flags builder. The diagnostic passes through `args.force` (in case operator wants to read a chip whose chip-ID doesn't match — useful for the missing-chip case from Shield 3 of the original triage).
- **`tqdm` + `ClassProgressHandler`** (used by `_main_phase_read_data` via `progress.start(...)`/`progress.update(...)`) — per-run progress bars come for free; just instantiate a fresh handler per run.
- **`hashlib` (stdlib)** — no new dependency; one-line SHA-256 over the per-run binary.
- **`tests/conftest.py` fixtures** — serial-stubbing scaffolding. New test file imports the same fixtures.

### Established Patterns

- **`dev` subparser as the permanent home for diagnostic / introspection verbs** ([main.py:366-426](firestarter_app/firestarter/main.py#L366-L426)). `dev consistency-check` joins `dev read` / `dev reg` / `dev addr`. The pattern is: low-level commands the operator runs by hand, not user-facing wrappers.
- **`args.dev_command` dispatch in `main()`** ([main.py:799-845](firestarter_app/firestarter/main.py#L799-L845)). New branch slots in alongside `read`/`reg`/`addr` with the same `db_instance.get_eprom` + `convert_to_programmer` + `eprom_operator.<method>` shape.
- **EpromOperator returns int exit code OR bool, depending on method.** Existing `dev_read_eprom` returns `bool`; the new `consistency_check_eprom` returns `int` per D-05 — this is a divergence from the existing pattern but justified because the 3-way exit code (0/1/2) cannot fit in a bool. Document the divergence in the method docstring.
- **`-v / --verbose` is the established serial-trace flag.** The new `-q / --quiet` flag is local to `consistency-check` and suppresses tqdm progress only — not serial trace.
- **Cross-phase evidence files mirror v1.3 / v1.5 patterns.** `v1.6-EVIDENCE.md` uses the same markdown-table-row-per-(board,chip)-pair shape as `v1.3-BENCH-RESULTS.md`. Operator can grep / awk / diff these consistently.

### Integration Points

- **CLI argparse subparser ↔ EpromOperator method ↔ existing read state machine.** The diagnostic is a thin orchestration layer on top of the existing read path — it does not add new serial code, new wire-protocol frames, or new firmware behavior. **If the diagnostic doesn't trip the bug, the bug is not in the read state machine** (which would invalidate every existing hypothesis in `large-read-data-jitter-uno328pb.md` and force a rethink in Phase 27). This is a desirable property — the tool is also a hypothesis test for the existing RCA candidate set.
- **Database ↔ runtime** — chip-name lookup unchanged. Bug is transport-side per 3-shield triage; DB integrity is irrelevant to reproduction.
- **`tests/conftest.py` ↔ new test file.** Stubbed serial is sufficient for D-10 cases 1-6 — no hardware needed in CI, no chip required, no platformio needed.
- **No new file under `firestarter/` (firmware sub-repo).** Phase 26 is host-CLI-only per D-13.

</code_context>

<specifics>
## Specific Ideas

- **"The diagnostic must exercise the exact bug-path code, not a parallel read implementation."** D-03's reuse-not-duplicate rule is load-bearing. If Phase 27 RCA reveals the bug is in `_main_phase_read_data`'s MSG_DATA_CHUNK extraction, and the Phase 26 diagnostic implemented a parallel read loop bypassing that layer, then `dev consistency-check` would falsely PASS post-fix on a still-broken code path. Reuse the public `read_eprom` orchestration verbatim — the diagnostic is a wrapper over N invocations of the production read path.
- **SHA-256 is operator-mental-model convention.** The original 2026-05-21 triage in `large-read-data-jitter-uno328pb.md` §"How to triage" uses `sha256sum /tmp/read_$i.bin` in a shell loop. The new CLI command is the same shell loop crystallized — same hash function, same artifact layout, same comparison. Don't switch to xxhash / SHA-1 / md5 just because they're faster; the throughput is serial-bound, not CPU-bound.
- **Phase 26's diagnostic is also Phase 29's gate tool.** Phase 29 / VERIFY-01 + VERIFY-02 re-runs the same `dev consistency-check` post-fix and the gate is `exit 0` on all 3 boards with `--runs 5`. Phase 26 builds the gate tool; Phase 29 just inverts the verdict. This is the cross-phase load-bearing artifact.
- **Read-only / passive mode (D-02) is the chip-safety guarantee.** UV-EPROMs are one-shot; the operator must be able to run `dev consistency-check` against any chip in any state (programmed, blank, half-programmed, mid-erase, missing) without risk of accidental data loss. Passive read fulfills this. An accidentally-clobbered SST27SF512 is an irreversible bench setback; the read-only invariant is non-negotiable.
- **The 3-shield triage already proves cross-shield + cross-firmware invariance** — Phase 26 is NOT also a shield-rotation test. Operator runs each board once on whichever shield is currently mounted. Per memory `[[user_shield_revisions]]`, if the operator wants to add a shield rotation row, that's bonus evidence; not required by SC#1-5.

</specifics>

<deferred>
## Deferred Ideas

- **`--all-boards` orchestrator that enumerates ports and runs the diagnostic across each automatically.** Adds complexity for marginal benefit; per-port manual invocation matches existing Phase 24 bench muscle memory. Could be reconsidered post-v1.6 if v1.7+ introduces a multi-board CI workflow.
- **`--chunk-size N` flag to also exercise the 1KB low-rate jitter case from inside `consistency-check`.** Phase 29 covers this via existing `dev read -s 1024` shell loop. Add only if Phase 27 RCA reveals the fix differs between full-chip and 1KB modes (forces a per-chunk-size regression check).
- **`--json` output mode for CI/log-ingestion.** Stdout is human-readable in Phase 26; if a v1.7+ CI workflow wants structured output, add the flag then. Don't pre-build.
- **Promoting `consistency-check` to a top-level command (`firestarter consistency-check <chip>`) after the fix lands.** Per ROADMAP narrative the command lives under `dev` permanently. Top-level surface is reserved for user-facing operations (read / write / verify / erase / blank / id / info), not diagnostics.
- **Cross-shield rotation matrix as part of Phase 26.** The 3-shield A/B/C triage already exists in `large-read-data-jitter-uno328pb.md`; Phase 26's evidence file references it rather than re-running. If a future bug surfaces shield-specifically, that's a new phase / new triage.
- **Phase 27 hypotheses ranking via Phase 26 evidence.** As REPRO-01/02 run, the per-board results may favor one of the 4 hypotheses in `large-read-data-jitter-uno328pb.md` (host-side buffer, firmware MAIN-state off-by-N, 328PB-specific timing, missing -D flag). Phase 27 owns that ranking — Phase 26 just records the raw evidence.
- **Firmware-side change in Phase 26.** Deferred to Phase 28 per D-13. Phase 26 is host-CLI-only; the firmware `v1.6-read-bug` branch is cut when the fix lands.
- **avrdude-mcu-detection-fallback + w27c512-eeprom-misclassification** — both v1.5 backlog carryforwards; explicitly out of v1.6 scope per `.planning/REQUIREMENTS.md` §"Future Requirements".

### Reviewed Todos (not folded)

No matching todos surfaced by phase-scoped todo search beyond `large-read-data-jitter-uno328pb.md` itself, which IS the v1.6 source backlog item (Phase 30 / DOC-01 moves it out of `pending/`).

</deferred>

---

*Phase: 26-cross-board-reproduction-diagnostic-tooling*
*Context gathered: 2026-05-21 via /gsd:discuss-phase 26 (Auto Mode — auto-resolved gray areas with recommended options)*

# Phase 12: 28-Pin / Algo-0x07 Bench Validation - Context

**Gathered:** 2026-05-20
**Status:** Ready for planning
**Source:** /gsd-discuss-phase 12 --auto --chain (auto-resolved gray areas with recommended options)

<domain>
## Phase Boundary

Phase 12 delivers **bench-hardware proof that the algorithm-0x07 (28-pin DIP CMOS UV-EPROM) family works end-to-end on both Uno and Leonardo boards**. Three chips run a full bench cycle on both boards; PROTO-01 (chip-ID observation) and PROTO-02 (VPP scope observation) are established here for the first time and carried forward into Phase 13 unchanged.

**Bench chips (this phase):**
1. **BENCH-01: W27C512** (28-pin, algo 0x07, 64K, DIP28_27512) — closes deferred v1.2 Phase 08 SC#2/SC#3 + Phase 09 Plan-05 Task 3 + Phase 08 HUMAN-UAT.md
2. **BENCH-02: SST27SF512** (28-pin, algo 0x07, 64K, DIP28_27512)
3. **BENCH-05: W27C257** (28-pin, algo 0x07, 32K, DIP28_27256) — 32K density-low representative; selection rationale in D-01

**Per-chip bench cycle (D-07 — fixed order):**
1. `firestarter info <chip>` — confirm chip is in DB and inspect declared values
2. `firestarter vpp -t 5` (then `vpe` if applicable) — VPP regulator engagement check (PROTO-02 evidence)
3. `firestarter id <chip>` — chip-ID read; verify against DB `chip_id_value` (PROTO-01 evidence)
4. `firestarter blank <chip>` — pre-cycle blank-check (required for UV-EPROMs that should arrive blank from UV erase)
5. `firestarter write <chip> data.bin` — write the deterministic test image
6. `firestarter read <chip> readback.bin` — read back the full image
7. `firestarter verify <chip> data.bin` — byte-identical verify
8. **Post-cycle blank-check skipped** for UV-EPROMs (they are not electrically erasable; post-write blank is structurally always non-blank). The ROADMAP SC#1 phrase "post-cycle blank-check where electrically erasable" is honored by skipping for algo-0x07.

Each cycle runs on **Uno first, then Leonardo** so any board-asymmetry shows up as a Leonardo-only failure with the Uno result as the reference.

**In scope:**
- New file `.planning/v1.3-BENCH-RESULTS.md` (initial scaffold; Phase 14 owns the final aggregated artifact per DOC-01). Phase 12 adds rows for BENCH-01 / BENCH-02 / BENCH-05 + PROTO-01/02 observations.
- Per-cycle log files under `.planning/v1.3/bench-logs/{chip}-{board}-{date}.log` capturing `firestarter -v` stdout/stderr.
- Per-board scope photo (PNG/JPG) under `.planning/v1.3/scope/{board}-vpp-{date}.{ext}` — minimum one per board for PROTO-02 evidence.
- Reuse of `firestarter_app/firestarter_test.sh` + `firestarter_app/write_test.sh` as the test harness (see D-02).
- New thin wrapper script `firestarter_app/tools/bench_cycle.sh` (optional — only if `firestarter_test.sh` cannot be invoked unmodified — see D-02 fallback).

**Out of scope:**
- Phase 13 chips (BENCH-03 W27C020, BENCH-04 W27E040, BENCH-06 — 32-pin algo-0x08).
- Final BENCH-RESULTS.md aggregation (Phase 14 / DOC-01).
- Any modification to firmware (`firestarter/` submodule) or to `chip_database.json` — operator-only execution against the existing v1.3-shipped firmware and DB.
- Auto-fixes for DEFECT-COV findings flagged by Phase 11 (out of scope per CONTEXT.md Phase 11 D-15 cousin; defects route to v1.4).
- BENCH-05 candidate-swap re-evaluation (D-01 locks the chip).
- New CLI subcommands or new flags on `firestarter` — observation protocols use existing `info` / `id` / `vpp` / `vpe` / `blank` / `write` / `read` / `verify` / `erase` commands verbatim.

</domain>

<decisions>
## Implementation Decisions

### BENCH-05 chip selection

- **D-01: BENCH-05 = `W27C257` (WINBOND, 28-pin, algo 0x07, 32K, DIP28_27256).**
  Rationale (best-three-candidate comparison from `.planning/v1.3-COVERAGE-MATRIX.md` and `.planning/v1.3-defect-coverage-ids.json`):
  - **W27C257 (chosen)** — same manufacturer family as BENCH-01 (WINBOND W27C512), so a W27C257 PASS is the cleanest "family scales down" evidence point. `chip_id_value: 0x0000da02` (shared with W27E257 per DEFECT-COV-04 — informational cluster, expected). Pulse width 10000 µs matches the cluster median (no CORRECTNESS finding against it). DIP28_27256 pinout — same socket position as BENCH-01/02.
  - **W27E257 (rejected)** — identical `chip_id_value` to W27C257 (0x0000da02), so PROTO-01 cannot disambiguate between them at the bench. Same physical bench coverage, lower discriminating evidence.
  - **SST27SF256 (rejected)** — DEFECT-COV-63 already flags it for 5000 µs vs cluster 10000 µs pulse width. Choosing a defect-flagged candidate as the BENCH-05 density-low rep risks conflating "BENCH-05 fails because the chip is wrong" with "BENCH-05 fails because of a tool/firmware issue". Reserve for v1.4 defect investigation; keep BENCH-05 clean.
  - **WINBOND brand consistency with BENCH-01 (W27C512)** is the tiebreaker: a passing BENCH-01 + passing BENCH-05 both on WINBOND chips is interpretable as "WINBOND family OK across 32K/64K densities"; a SST-vendored BENCH-05 alongside WINBOND BENCH-01 would split that signal.

### Test harness reuse

- **D-02: Reuse `firestarter_app/firestarter_test.sh` verbatim as the per-cycle test harness.** The script already implements the full cycle (id → vpp/vpe → write → verify → read → erase/blank gating) and accepts `[EPROM_NAME]` as a positional argument. Invocation:
  ```bash
  cd firestarter_app && ./firestarter_test.sh W27C512 2>&1 | tee ../.planning/v1.3/bench-logs/W27C512-uno-2026-05-20.log
  cd firestarter_app && ./firestarter_test.sh SST27SF512 2>&1 | tee ../.planning/v1.3/bench-logs/SST27SF512-uno-2026-05-20.log
  cd firestarter_app && ./firestarter_test.sh W27C257 2>&1 | tee ../.planning/v1.3/bench-logs/W27C257-uno-2026-05-20.log
  ```
- **D-02 fallback:** Only if `firestarter_test.sh` cannot be invoked unmodified for one of the three chips (e.g., chip not in DB lookup, or harness asserts erase is supported when it is not), add a thin per-phase wrapper at `firestarter_app/tools/bench_cycle.sh` that drives the same `firestarter` subcommands in the order D-07 specifies. Do NOT modify `firestarter_test.sh` itself — it is shared infrastructure used by other test paths and historical results are anchored to its current behavior.
- **D-02 note:** `write_test.sh` is a deterministic write+verify harness that auto-generates the test image at the chip's exact size from `chip_database.json`. Reuse its image-generation logic for the bench-cycle's `data.bin` so the test image is deterministic and reproducible across boards.

### PROTO-01 chip-ID observation protocol

- **D-03: Capture method = CLI stdout/stderr piped to a per-cycle log file with `tee`.** The line containing `chip-id` or `chip_id` (case-insensitive) in the log is the protocol evidence. Operator pastes a 5-line snippet (the `id` invocation + the response lines + the next command) into `.planning/v1.3-BENCH-RESULTS.md`'s PROTO-01 row.
- **D-04: PROTO-01 mismatch handling = blocked-write evidence is required.** For at least one of BENCH-01/02/05 (operator's choice — recommended: SST27SF512 since its `chip_id_value: 0x0000bfa4` is distinct from the WINBOND chips), the operator runs `firestarter id` then deliberately attempts `firestarter write <wrong-chip-name> data.bin` and captures the safety-stack refusal as evidence that the chip-ID mismatch path blocks the write (PROTO-01 success criterion ROADMAP SC#4). Single capture is sufficient — the firmware safety path is shared across all algo-0x07 chips.

### PROTO-02 VPP scope observation protocol

- **D-05: Capture method = one annotated scope photo per board minimum.** Required artifacts:
  - `.planning/v1.3/scope/uno-vpp-write-{date}.png` — Uno's VPP rail at the chip socket VPP pin, captured during a `firestarter write` cycle (PROTO-02 evidence — 12V ±5%).
  - `.planning/v1.3/scope/leonardo-vpp-write-{date}.png` — same for Leonardo.
  - Optional: `.planning/v1.3/scope/{board}-vpp-idle-{date}.png` showing VCC/off between operations (idle-state evidence per ROADMAP SC#5).
- **D-06: Annotation requirements = the photo MUST visibly include the chip socket VPP pin probe point, the scope time-base reading, and the voltage scale; operator adds a one-line caption in the BENCH-RESULTS row stating measured Vpp + tolerance band. Phase 13 reuses this same protocol unchanged for the algo-0x08 family.

### Bench-cycle order (canonical, per chip-board pair)

- **D-07: Cycle order is fixed across all three chips:**
  1. `info` (DB introspection — no hardware action)
  2. `vpp -t 5` then `vpe -t 5` (regulator engagement check — captures PROTO-02 evidence)
  3. `id` (chip-ID read — PROTO-01 evidence row)
  4. `blank` (pre-cycle blank-check — must pass for UV-EPROM after UV erase)
  5. `write data.bin` (program the deterministic test image)
  6. `read readback.bin` (full readback)
  7. `verify data.bin` (byte-identical compare)
  8. Post-cycle blank-check: **skipped** for algo-0x07 (UV-EPROMs are not electrically erasable; SC#1 phrase "where electrically erasable" governs). Phase 13's algo-0x08 family inherits this clause unchanged (W27Cxxx and W27Exxx on algo-0x08 are also UV-EPROM in the DB).

### BENCH-RESULTS.md schema

- **D-08: Per-chip-per-board row schema** (column header → column value source). One row per (chip, board) pair = 6 rows for Phase 12:

  | Column | Source |
  |--------|--------|
  | Chip | `W27C512` / `SST27SF512` / `W27C257` |
  | Board | `uno` / `leonardo` |
  | Date | ISO date of bench run |
  | `info` | `OK` / `FAIL: <reason>` |
  | `vpp_engaged` | `12.0V ±5%` (measured) — links to scope photo file |
  | `chip_id_read` | hex value as printed by `firestarter id` |
  | `chip_id_db` | hex value from `chip_database.json` (must match `chip_id_read`) |
  | `chip_id_match` | `Y` / `N` |
  | `blank_pre` | `BLANK` / `NOT-BLANK` (pre-cycle) |
  | `write` | `OK` / `FAIL: <reason>` |
  | `read` | `OK` / `FAIL` |
  | `verify` | `OK` (byte-identical) / `FAIL: <byte-count diff>` |
  | `blank_post` | `N/A (UV-EPROM)` for algo-0x07 |
  | `log` | relative path to per-cycle log file |
  | `notes` | freeform — quirks, retries, anomalies |

- **D-09: PROTO-01 evidence row.** Single row showing the blocked-write capture for the chosen chip (D-04). Columns: chip, board, intended_wrong_chip, expected_block_reason, observed_log_snippet.
- **D-10: PROTO-02 evidence rows.** One row per board with: board, scope_photo_path, measured_vpp_volts, tolerance_band_check (Y/N), idle_state_observed (Y/N), captured_during (write / erase / both).

### Plan structure

- **D-11: One plan per chip (3 plans), with both boards inside each plan.** This maps each plan 1:1 to a single BENCH-* requirement and produces one closing record per requirement. Plan dependency chain: 12-01 (BENCH-01 W27C512) → 12-02 (BENCH-02 SST27SF512) → 12-03 (BENCH-05 W27C257). BENCH-01 runs first because it closes the heavy deferred items (Phase 08 + 09) — failing fast there gives the most diagnostic value.
- **D-12: A fourth desk-side plan (12-04) scaffolds the BENCH-RESULTS.md skeleton + scope/log directories before any chip plan runs.** This is the only autonomous plan in the phase; plans 12-01..03 are operator-on-bench (`autonomous: false`).
- **D-13: Optional fifth plan (12-05) — PROTO-01 blocked-write evidence capture.** Single bench task. Can be folded into 12-02 (SST27SF512 plan) as a fourth step rather than its own plan, at the planner's discretion. **Recommended: fold into 12-02** to keep the plan count at 4 and keep PROTO-01 evidence in the SST27SF512 row (D-04 already chose SST as the disambiguation target).

### Resume / interruption model

- **D-14: All bench plans set `autonomous: false`.** Each plan is a checkpoint plan — the operator works through tasks at the bench, marks completion via `gsd-sdk query roadmap update-plan-progress 12 12-NN complete` (or via the gsd-executor continuation prompt), then advances to the next chip. Mid-plan interruption: the per-cycle log file is the resume anchor — operator inspects the last completed step in the log and continues from there.
- **D-15: Tracking writes go to STATE.md after each chip plan completes.** Each plan's executor writes a SUMMARY.md row and the orchestrator commits STATE.md + ROADMAP.md progress in lockstep — same pattern as Phase 11.

### Claude's Discretion

- **Exact scope photo file format and resolution.** D-05 specifies PNG/JPG and the required content; if the operator's scope only exports BMP / SVG / CSV, that's acceptable so long as the voltage + time-base reading + probe location are legible.
- **Date encoding in artifact filenames.** ISO `2026-05-20` is recommended for sortability, but operator's local convention (`20260520` or `2026May20`) is fine if used consistently across files.
- **Order in which `vpp -t 5` and `vpe -t 5` run.** D-07 lists `vpp` first then `vpe`; either order works for the scope capture as long as both run within the same cycle. Recommended: `vpp` first (because PROTO-02's voltage tolerance band targets the VPP rail; VPE is the program-enable rail and its capture is bonus evidence).
- **Whether to capture the firmware/hardware version row** (`firestarter fw` + `hw`) per cycle or once per phase. Recommended: once per phase per board (cheap, but already captured by `firestarter_test.sh` — accept the redundancy and let the harness emit it every cycle).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope + requirements (authoritative)
- [.planning/ROADMAP.md](.planning/ROADMAP.md) §"Phase 12: 28-Pin / Algo-0x07 Bench Validation" — goal + Success Criteria 1–5 + dependency on Phase 11
- [.planning/REQUIREMENTS.md](.planning/REQUIREMENTS.md) §"BENCH" — BENCH-01, BENCH-02, BENCH-05 + §"PROTO" PROTO-01, PROTO-02 + traceability table at file end
- [.planning/PROJECT.md](.planning/PROJECT.md) §"Current Milestone: v1.3" — milestone goal + Out of Scope
- [.planning/STATE.md](.planning/STATE.md) §"v1.3 Decisions" — scope, deferred-items absorption (v1.2 Phase 08 / 09), hardware-bench dependency
- [.planning/STATE.md](.planning/STATE.md) §"Deferred Items" — Phase 08 HUMAN-UAT.md + Phase 08/09 VERIFICATION.md (closes via BENCH-01)

### Phase 11 outputs (consumed by Phase 12)
- [.planning/v1.3-COVERAGE-MATRIX.md](.planning/v1.3-COVERAGE-MATRIX.md) §3 — algo-0x07 full enumeration; rows for W27C512, SST27SF512, W27C257 (BENCH chip evidence)
- [.planning/v1.3-COVERAGE-MATRIX.md](.planning/v1.3-COVERAGE-MATRIX.md) §5 "Pinout-Class Coverage" — pin-out class coverage proof for DIP28_27256 (BENCH-05 location) and DIP28_27512 (BENCH-01/02)
- [.planning/v1.3-defect-coverage-ids.json](.planning/v1.3-defect-coverage-ids.json) — DEFECT-COV-04 (W27C257/W27E257 shared chip_id_value) + DEFECT-COV-63 (SST27SF256 pulse-width outlier — rejected BENCH-05 candidate per D-01)

### Test harness + tools (the bench cycle is operator-invoked against these)
- [firestarter_app/firestarter_test.sh](firestarter_app/firestarter_test.sh) — full bench-cycle test harness; primary invocation per D-02
- [firestarter_app/write_test.sh](firestarter_app/write_test.sh) — deterministic write+verify harness (image-generation reused per D-02 note)
- [firestarter_app/CLAUDE.md](firestarter_app/CLAUDE.md) §"Architecture / Data Flow" — `firestarter <chip> write/read/erase` pipeline (the bench cycle CLI surface)
- [firestarter_app/CLAUDE.md](firestarter_app/CLAUDE.md) §"Wire Protocol" — JSON command shape + response prefix tags (used for log-snippet parsing in BENCH-RESULTS)
- [firestarter_app/CLAUDE.md](firestarter_app/CLAUDE.md) §"Database Pipeline" — WARNING-5 override semantics (background; not modified in this phase)

### Database (the chip-id source-of-truth for PROTO-01)
- [firestarter_app/firestarter/data/chip_database.json](firestarter_app/firestarter/data/chip_database.json) — `chip_id_value` per chip is the value PROTO-01 verifies against the bench readout
- [firestarter_app/firestarter/database.py](firestarter_app/firestarter/database.py) — `EpromDatabase.get_eprom(name)` is the chip-lookup path the CLI exercises during `info` / `id` / `write`
- [firestarter_app/firestarter/eprom_operations.py](firestarter_app/firestarter/eprom_operations.py) — high-level operation implementations the bench cycle drives
- [firestarter_app/firestarter/serial_comm.py](firestarter_app/firestarter/serial_comm.py) — INIT/MAIN/END state machine; serial-log breadcrumbs that appear in `-v` output

### Deferred items closing via Phase 12
- [.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-HUMAN-UAT.md](.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-HUMAN-UAT.md) — 2 pending chip-seated W27C512 scenarios (closes via BENCH-01)
- [.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-VERIFICATION.md](.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-VERIFICATION.md) — `human_needed` UAT closure (closes via BENCH-01)
- [.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-VERIFICATION.md](.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-VERIFICATION.md) — Plan 09-05 Task 3 (chip-seated W27C512 on both boards — closes via BENCH-01)

### Project memory (always-on guidance)
- `[[feedback_always-mirror-uno-leonardo-tests]]` — every BENCH cycle runs on BOTH boards (Uno first, then Leonardo); this is the load-bearing convention this phase establishes for the rest of v1.3 (and inherits forward into Phase 13)
- `[[project_db-overrides-firmware-is-ground-truth]]` — relevant for PROTO-01 mismatch handling (D-04): the safety stack that blocks writes when chip-ID disagrees is in firmware, not in the host — bench evidence demonstrates the firmware path is real, not just declared

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`firestarter_app/firestarter_test.sh`** — the existing bench-cycle harness. Already runs the full pipeline (`fw` + `hw` + `config` + `vpp` + `vpe` + `id` + `write` + `verify` + `read` + `erase` + `blank` + `list` + `search` + `info`) gated by chip capability. Accepts `[EPROM_NAME]` positional. Phase 12 invokes this verbatim per D-02; no modification.
- **`firestarter_app/write_test.sh`** — deterministic-image write+verify harness. Generates `data.bin` at the chip's exact `size_bytes` from `chip_database.json`. The image-generation logic is the source-of-truth for the deterministic test image used in all three BENCH cycles.
- **`firestarter info <chip>`** + **`firestarter id <chip>`** + **`firestarter vpp -t 5`** + **`firestarter vpe -t 5`** — existing CLI subcommands provide all the observation evidence PROTO-01 and PROTO-02 need; no new CLI surface required.
- **`EpromDatabase` singleton** in `firestarter_app/firestarter/database.py` — the chip-lookup path that resolves chip names to programmer config. The PROTO-01 chip-id comparison happens HERE (host-side) and is enforced by the firmware safety stack (chip-id-mismatch → write blocked).

### Established Patterns

- **Per-test logging via `tee`** — `firestarter_test.sh` runs `firestarter -v ...` which emits verbose stdout/stderr. Standard pattern (from v1.0 and v1.2 phases) is to redirect with `2>&1 | tee logfile` so the operator gets live output and a file record simultaneously. Phase 12 inherits this pattern for per-cycle log capture.
- **Two-board mirror rule** (`[[feedback_always-mirror-uno-leonardo-tests]]`) — every bench-validation phase runs each test on BOTH boards. This phase establishes the rule for v1.3; Phase 13 inherits it unchanged.
- **Wire protocol log breadcrumbs** — `firestarter_app/CLAUDE.md` §"Wire Protocol" documents the response prefix tags (`OK:`, `DATA:`, `MAIN:`, `END:`, `ERROR:`). The bench-cycle log file is grep-friendly along these prefixes; BENCH-RESULTS.md row values are extracted via grep, not by hand-transcription.

### Integration Points

- **CLI ↔ firmware serial protocol** — bench cycle exercises the full 250000-baud serial path (`firestarter_app/firestarter/serial_comm.py` ↔ `firestarter/src/firestarter.cpp`). No new serial code; this phase is observation-only.
- **DB ↔ runtime** — `chip_database.json` is read by `EpromDatabase.get_eprom()` to resolve chip names; PROTO-01 compares the DB's declared `chip_id_value` against the hardware's `id` readout. The bench is testing the agreement between DB declarations and physical chips.
- **No new file under `firestarter_app/firestarter/`** — Phase 12 does not add or modify any installed pip-package code. Bench cycle = operator commands + shell harness + DB lookup + firmware. All artifacts produced live under `.planning/` (parent repo) or as new logs/photos.

</code_context>

<specifics>
## Specific Ideas

- **"BENCH-01 is the load-bearing chip for v1.3 milestone closure."** It's named in deferred Phase 08 SC#2/SC#3 + Phase 09 Plan-05 Task 3 + Phase 08 HUMAN-UAT.md. A green BENCH-01 receipt closes all four deferred items in one stroke; Phase 12 lands BENCH-01 first deliberately so any blocker shows up before the rest of the phase invests in BENCH-02/05.
- **WINBOND family scaling.** W27C512 (BENCH-01, 64K) + W27C257 (BENCH-05, 32K) on the same brand = "family scales down" evidence point. A passing W27C512 + failing W27C257 on the same brand would localize the issue to density-low handling, not vendor-specific quirks.
- **PROTO-01/02 are observation protocols, NOT new code paths.** Phase 12 doesn't write new firmware or new CLI; it captures, with hardware in the loop, that the EXISTING code paths behave correctly. The "protocol" being established is the *recording method* (D-03..D-06), not new functional logic.
- **Phase 13 inherits everything.** D-07 cycle order, D-08 BENCH-RESULTS schema, D-09/D-10 PROTO evidence shape, and D-05/D-06 scope-photo conventions all carry forward verbatim into Phase 13 (algo-0x08 family). Phase 13's own CONTEXT.md will reference this CONTEXT.md and add only algo-0x08-specific deltas.

</specifics>

<deferred>
## Deferred Ideas

- **Phase 13 chips (BENCH-03 W27C020, BENCH-04 W27E040, BENCH-06 32-pin density-low rep).** Same protocol applied to algo-0x08 family — Phase 13 owns CONTEXT.md + plans.
- **CI wiring of `firestarter_test.sh`** — currently operator-invoked. Auto-running it in CI would require a chip socket emulator or hardware-in-the-loop runner; deferred indefinitely.
- **BENCH-RESULTS aggregation into `.planning/v1.3-BENCH-RESULTS.md`** — Phase 14 / DOC-01 owns final aggregation. Phase 12 adds rows; Phase 13 adds more rows; Phase 14 closes the file and the milestone.
- **DEFECT-COV-XX investigations** — Phase 11's matrix flagged 78 findings (1 HAZARD + 27 CORRECTNESS + 49 VARIANCE). Phase 12 references the matrix as evidence but does not act on findings; defects route to v1.4 per the locked v1.3 scope.
- **SST27SF256 as BENCH-05** — rejected per D-01 because DEFECT-COV-63 flags it. Could be revisited in v1.4 once the underlying 5000 µs vs cluster-10000 µs discrepancy is investigated.
- **W27E257 as BENCH-05** — rejected because it shares `chip_id_value` with W27C257 (DEFECT-COV-04). Could be revisited if WINBOND family coverage needs a second 32K chip (likely not in v1.3 scope).
- **Modifying `firestarter_test.sh`** — explicitly out of scope per D-02. Any harness change is shared infrastructure that requires its own phase/PR cycle and would invalidate historical results anchored to its current behavior.

### Reviewed Todos (not folded)

No matching todos surfaced by `gsd-sdk todo.match-phase` for Phase 12.

</deferred>

---

*Phase: 12-28-pin-algo-0x07-bench-validation*
*Context gathered: 2026-05-20 via /gsd-discuss-phase 12 --auto --chain*

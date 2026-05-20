# Phase 12: 28-Pin / Algo-0x07 Bench Validation - Research

**Researched:** 2026-05-20
**Domain:** Operator-on-bench hardware validation (chip seating + serial protocol observation + scope-photo evidence)
**Confidence:** HIGH (all bench-cycle CLI surface, harness logic, and DB metadata verified in repo; scope-photo and chip-handling steps are operator-physical and assumed-standard for the project's existing bench workflow)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: BENCH-05 = `W27C257`** (WINBOND, 28-pin, algo 0x07, 32K, DIP28_27256). Rationale: WINBOND family scaling vs BENCH-01 (W27C512); `chip_id_value: 0x0000da02`; 10000 µs pulse cluster-median; no CORRECTNESS finding. W27E257 rejected (shared `chip_id_value` with W27C257 via DEFECT-COV-04 — PROTO-01 cannot disambiguate). SST27SF256 rejected (DEFECT-COV-63 flags 5000 µs vs cluster 10000 µs pulse-width).
- **D-02: Reuse `firestarter_app/firestarter_test.sh` verbatim** as the per-cycle test harness. Invocation: `cd firestarter_app && ./firestarter_test.sh <CHIP> 2>&1 | tee ../.planning/v1.3/bench-logs/<CHIP>-<board>-<date>.log`. **D-02 fallback:** if the harness cannot be invoked unmodified for one of the three chips, add a thin wrapper at `firestarter_app/tools/bench_cycle.sh` — do NOT modify `firestarter_test.sh`. **D-02 note:** `write_test.sh` is the deterministic image-generation source (auto-generates `data.bin` at the chip's exact size from `chip_database.json`).
- **D-03: PROTO-01 capture method = CLI stdout/stderr piped to a per-cycle log file with `tee`.** The line containing `chip-id` / `chip_id` (case-insensitive) is protocol evidence. Operator pastes a 5-line snippet into the BENCH-RESULTS.md PROTO-01 row.
- **D-04: PROTO-01 mismatch handling = blocked-write evidence required.** For at least one of BENCH-01/02/05 (recommended: SST27SF512), operator runs `firestarter id` then deliberately attempts `firestarter write <wrong-chip-name> data.bin` and captures the safety-stack refusal. Single capture is sufficient.
- **D-05: PROTO-02 capture method = one annotated scope photo per board minimum.** Required artifacts: `.planning/v1.3/scope/uno-vpp-write-<date>.png` + `.planning/v1.3/scope/leonardo-vpp-write-<date>.png`. Optional `<board>-vpp-idle-<date>.png` for idle-state evidence.
- **D-06: Annotation requirements** — photo MUST visibly include the chip socket VPP pin probe point, scope time-base reading, and voltage scale; operator adds a one-line caption in the BENCH-RESULTS row with measured Vpp + tolerance band. Phase 13 reuses this protocol unchanged.
- **D-07: Cycle order is fixed across all three chips:** (1) `info` → (2) `vpp -t 5` then `vpe -t 5` → (3) `id` → (4) `blank` (pre-cycle) → (5) `write data.bin` → (6) `read readback.bin` → (7) `verify data.bin`. **Post-cycle blank-check skipped** for algo-0x07 (UV-EPROMs are not electrically erasable; SC#1 phrase "where electrically erasable" governs).
- **D-08: Per-chip-per-board row schema** — 14 columns, one row per (chip, board) = 6 rows total: Chip, Board, Date, `info`, `vpp_engaged`, `chip_id_read`, `chip_id_db`, `chip_id_match`, `blank_pre`, `write`, `read`, `verify`, `blank_post` (= `N/A (UV-EPROM)`), `log`, `notes`.
- **D-09: PROTO-01 evidence row** — single row with chip, board, intended_wrong_chip, expected_block_reason, observed_log_snippet.
- **D-10: PROTO-02 evidence rows** — one row per board with board, scope_photo_path, measured_vpp_volts, tolerance_band_check, idle_state_observed, captured_during.
- **D-11: One plan per chip (3 plans)**, both boards inside each. Dependency chain: 12-01 (BENCH-01 W27C512) → 12-02 (BENCH-02 SST27SF512) → 12-03 (BENCH-05 W27C257). BENCH-01 first because it closes deferred Phase 08/09 items — failing fast there gives maximum diagnostic value.
- **D-12: A fourth desk-side scaffold plan (12-04)** scaffolds BENCH-RESULTS.md + scope/log directories. Only autonomous plan; plans 12-01..03 are operator-on-bench (`autonomous: false`).
- **D-13: PROTO-01 blocked-write evidence folded into plan 12-02** (SST27SF512). Single extra task at the end of 12-02; no separate 12-05 plan.
- **D-14: All bench plans set `autonomous: false`.** Per-cycle log file = resume anchor.
- **D-15: Tracking writes go to STATE.md after each chip plan completes.** Orchestrator commits STATE.md + ROADMAP.md progress in lockstep — same pattern as Phase 11.

### Claude's Discretion

- Exact scope photo file format and resolution (PNG/JPG recommended; BMP/SVG/CSV acceptable if voltage + time-base + probe location legible).
- Date encoding in artifact filenames (ISO `2026-05-20` recommended for sortability).
- Order in which `vpp -t 5` and `vpe -t 5` run within step 2 (either order works; `vpp` first recommended).
- Whether to capture firmware/hardware version row per cycle vs once per phase (recommended: once per phase per board, but accept harness redundancy).

### Deferred Ideas (OUT OF SCOPE)

- Phase 13 chips (BENCH-03 W27C020, BENCH-04 W27E040, BENCH-06 32-pin algo-0x08).
- CI wiring of `firestarter_test.sh` (operator-invoked only).
- BENCH-RESULTS aggregation into final artifact (Phase 14 / DOC-01 owns).
- DEFECT-COV-XX investigations (routes to v1.4).
- SST27SF256 as BENCH-05 (rejected by D-01).
- W27E257 as BENCH-05 (rejected by D-01).
- Modifying `firestarter_test.sh` (explicit D-02).

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| BENCH-01 | W27C512 (28-pin, algo 0x07, 64K) — full write/read/verify cycle on Uno + Leonardo. Closes deferred Phase 08 SC#2/SC#3 + Phase 09 Plan-05 Task 3 + Phase 08 HUMAN-UAT.md | Standard 7-step cycle from D-07 driven by `firestarter_test.sh W27C512`. Chip-ID 0x0000da08 confirmed in DB. Pinout DIP28_27512 maps VPP to pin 22. |
| BENCH-02 | SST27SF512 (28-pin, algo 0x07, 64K) — full write/read/verify cycle on Uno + Leonardo | Same cycle, chip = SST27SF512. Chip-ID 0x0000bfa4 confirmed in DB. Same pinout DIP28_27512 (VPP at pin 22). |
| BENCH-05 | W27C257 (28-pin, algo 0x07, 32K) — 32K density-low representative; full cycle on Uno + Leonardo | Same cycle, chip = W27C257. Chip-ID 0x0000da02 (shared with W27E257 per DEFECT-COV-04). Pinout DIP28_27256 maps VPP to pin 1 — different probe point from BENCH-01/02. |
| PROTO-01 | For every BENCH chip with `chip_id_check: true`, chip-ID read returns DB-declared `chip_id_value`; mismatches blocked by safety stack | All three bench chips have `chip_id_check: true`. Safety stack lives in firmware (per `[[project_db-overrides-firmware-is-ground-truth]]`); host surfaces firmware refusal via `MSG_WARN_CHIP_ID_MISMATCH` (0x83) or `MSG_ERR_CHIP_ID_MISMATCH` (0xB9). Captured via tee'd log (D-03) + blocked-write evidence on SST27SF512 (D-04, folded into plan 12-02). |
| PROTO-02 | VPP regulator engages at 12V ±5% during write/erase; idles at VCC or off between operations | Scope-probe VPP pin at the socket (pin 22 for DIP28_27512, pin 1 for DIP28_27256); capture during `firestarter write` cycle. One annotated photo per board minimum (D-05); resolved by 6 cycles overall but only 2 photos required (one per board). |

</phase_requirements>

## Summary

Phase 12 is **operator-on-bench hardware validation**, not a coding phase. The deliverables are evidence — log files, scope photos, and a BENCH-RESULTS.md table — proving that the existing v1.3-shipped firmware and CLI correctly program three algo-0x07 chips (W27C512 / SST27SF512 / W27C257) on two boards (Uno / Leonardo). No new Python production code lands in `firestarter_app/firestarter/`; no firmware changes; no `chip_database.json` edits.

The technical surface area is narrow and well-understood: a single shell harness (`firestarter_test.sh`) drives a 7-step cycle (`info` → `vpp` → `vpe` → `id` → `blank` → `write` → `read` → `verify`) per chip; the harness reads `chip_database.json` directly via `jq` to look up `size_bytes`, `chip_id_check`, and `electrical.type`; the deterministic test image is the harness's own concat of two `dd if=/dev/urandom` halves into `test_data/full_data.bin`. Per-cycle output is captured via `tee` to `.planning/v1.3/bench-logs/<chip>-<board>-<date>.log`. PROTO-01 evidence is one line containing `chip-id` in the log; PROTO-02 evidence is a per-board annotated scope photo of the VPP rail at the chip socket.

**Primary recommendation:** Plan 12-04 (autonomous, desk-side) scaffolds the artifacts; plans 12-01/02/03 are sequential checkpoint plans (`autonomous: false`) with operator-driven tasks. Each task in a chip plan is a manual UAT step: "operator runs <command>, pastes log path + PASS/FAIL into BENCH-RESULTS.md, commits, advances." The executor reads operator-provided log+photo paths and updates BENCH-RESULTS.md; the executor does NOT itself run hardware commands.

## Architectural Responsibility Map

The "tiers" for this phase are not browser/server/API — they are bench artifacts vs orchestration. Mapping each capability to its owner:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Bench cycle execution (7 commands) | Operator-on-bench | `firestarter_test.sh` harness | Operator seats chip + invokes harness; harness shells out to `firestarter` CLI |
| Test image generation | `firestarter_test.sh` (via `jq` + `dd /dev/urandom`) | `chip_database.json` (size lookup) | Deterministic-per-cycle (regenerated each invocation); not reproducible across runs (urandom) — see Pitfall 4 |
| Chip-ID safety stack enforcement | Firmware (`memory.cpp` / chip-specific handlers) | Host (`eprom_operations.py::_run_state_machine`) surfaces firmware error | Per project memory `[[project_db-overrides-firmware-is-ground-truth]]`: blocked-write evidence is the firmware path being observed at the operator's terminal |
| Per-cycle log capture | `tee` (operator's shell) | gsd-executor reading log path | Log file = resume anchor (D-14); executor reads operator-pointed-at log to extract values |
| Scope photo capture | Operator's oscilloscope | None | Manual artifact; planner must produce explicit operator instructions for probe placement |
| BENCH-RESULTS.md row writes | gsd-executor (orchestrator-owns-tracking-writes per D-15) | Operator confirms PASS/FAIL via continuation prompt | Same pattern as Phase 11's STATE.md + ROADMAP.md lockstep updates |
| STATE.md / ROADMAP.md progress | Orchestrator | gsd-executor return | Phase 11 pattern: tracking writes serialised through orchestrator after each plan completes |

**Why this matters:** This phase mis-modeled as "automated executor runs the bench cycle" would crash on the first `firestarter` invocation (no hardware in the sandbox). The plan tier MUST be "operator-on-bench, gsd-executor as scribe."

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| `firestarter` CLI | shipped at v1.2 close (3.0.0-dev firmware contract) | Issues `info` / `id` / `vpp` / `vpe` / `blank` / `write` / `read` / `verify` commands | Already installed (`pip install -e .`); the entire system under bench |
| `firestarter_test.sh` | repo HEAD (172 lines, frozen by D-02) | Drives the 7-step cycle | Existing harness; D-02 locks "verbatim reuse, no modification" |
| `jq` | system | Parses `chip_database.json` for `size_bytes`, `chip_id_check`, `electrical.type` | Already used by both `firestarter_test.sh` and `write_test.sh` |
| `tee` | coreutils | Per-cycle log capture (stdout + file) | Project-standard log pattern (established v1.0+) |
| `colordiff` | system (BENCH cycle only) | xxd-side-by-side compare of `full_data.bin` vs `read_back.bin` | Used in `firestarter_test.sh` line 149; failure mode is exit code > 0 → harness aborts |
| Oscilloscope + probe | Operator's bench | PROTO-02 scope photo at VPP pin | Hand-rolled instrument; image format per D-05 |

### Supporting

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `firestarter --version` | Confirm CLI install + version pin | Once at start of each plan; harness already calls this at line 121 |
| `firestarter fw` / `firestarter hw` | Confirm firmware + RURP hardware revision per board | Harness calls these at lines 127–131 (every cycle); use to identify board mid-log |
| `firestarter config` | Confirm R1/R2 calibration + board revision read from EEPROM | Harness calls at line 132; confirms calibration before voltage measurements |
| `firestarter info <chip>` | DB introspection (no hardware action) | Harness line 169 (after EPROM_TESTS); D-07 step 1 |
| `firestarter search <chip>` / `firestarter list` | DB lookup + full chip listing | Harness lines 167–168; informational |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `firestarter_test.sh` reuse | New `firestarter_app/tools/bench_cycle.sh` wrapper | D-02 fallback only; needed if harness can't run unmodified for one of the three chips. As of this research, all three chips are in DB and have `electrical.type == "UV-EPROM"`, so harness's erase/blank-gating branch at lines 155–161 correctly skips erase (UV-EPROM `CAN_ERASE == false`) — no wrapper required. |
| `tee` log capture | `script(1)` typescript | `tee` is line-buffered and parseable; `script` captures terminal escape sequences and complicates `grep` for `MSG_*` markers |
| `dd if=/dev/urandom` test image | Fixed-seed PRNG image | Harness already uses urandom; image content is irrelevant for verify (verify is byte-identity compare of `full_data.bin` vs read-back, not against a known pattern). See Pitfall 4. |

**Installation (operator's bench setup):**

```bash
# From firestarter_app/ subrepo (already cloned + on branch refactor/v1.3-foundations):
cd /workspaces/firestarter_app
pip install -e .                              # editable install of the CLI

# Confirm:
firestarter --version                         # should match v1.2 ship state
firestarter fw                                # firmware version on currently-connected board (3.0.0-dev)
firestarter hw                                # hardware revision read from EEPROM
firestarter config                            # R1/R2 calibration + board cfg
```

**Version verification (run at the start of Plan 12-04):**

The phase pins to whatever `firestarter` is currently installed editable (`pip install -e .`). No external package versions to verify. Confirm three artifacts before plans 12-01..03 run:
- `firestarter_test.sh` is at repo HEAD (no local modifications) — `git -C firestarter_app status firestarter_test.sh` clean.
- `chip_database.json` is at repo HEAD — Phase 11 already ran the audit; the DB is the source of truth for `chip_id_value`.
- Both boards have firmware 3.0.0-dev (matches v1.2 ship state).

## Architecture Patterns

### System Architecture Diagram

```
                  ┌─────────────────────────────────────────────┐
                  │             OPERATOR AT BENCH               │
                  │   (seats chip, runs harness, captures evt)  │
                  └─────────────────────────────────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
              ▼                        ▼                        ▼
   ┌───────────────────┐   ┌──────────────────────┐  ┌──────────────────┐
   │  Scope probe at   │   │ firestarter_test.sh  │  │ gsd-executor     │
   │  VPP pin          │   │   <CHIP_NAME>        │  │ (continuation    │
   │  (Pin 22 for      │   │                      │  │  prompt waits    │
   │   DIP28_27512;    │   └──────────┬───────────┘  │  for operator)   │
   │   Pin 1 for       │              │              └────────┬─────────┘
   │   DIP28_27256)    │              ▼                       │
   └────────┬──────────┘   ┌──────────────────────┐           │
            │              │  firestarter CLI     │           │
            │              │  (Python, 250000     │           │
            │              │   baud serial)       │           │
            │              └──────────┬───────────┘           │
            │                         │                       │
            │                         │ JSON command          │
            │                         ▼                       │
            │              ┌──────────────────────┐           │
            │              │   RURP shield        │           │
            │              │   + Arduino          │           │
            │              │   (Uno / Leonardo)   │           │
            │              │   firmware 3.0.0-dev │           │
            │              └──────────┬───────────┘           │
            │                         │ VPP / VPE / Address / │
            │                         │  Data / CE / OE       │
            │                         ▼                       │
            │              ┌──────────────────────┐           │
            │              │   Chip in socket     │           │
            │              │   (W27C512 /         │           │
            │              │    SST27SF512 /      │           │
            │              │    W27C257)          │           │
            │              └──────────────────────┘           │
            │                                                 │
            └────────┬──────────────────────┬─────────────────┘
                     │                      │
                     ▼                      ▼
        ┌────────────────────────┐  ┌─────────────────────────┐
        │ scope/<board>-vpp-     │  │ bench-logs/<chip>-      │
        │   write-<date>.png     │  │   <board>-<date>.log    │
        │ (PROTO-02 evidence)    │  │ (PROTO-01 evidence +    │
        └────────────────────────┘  │  BENCH-* cycle record)  │
                     │              └─────────────────────────┘
                     │                          │
                     └──────────┬───────────────┘
                                │
                                ▼
                  ┌────────────────────────────────┐
                  │ .planning/v1.3-BENCH-RESULTS.md│
                  │  (gsd-executor appends         │
                  │   one row per (chip, board)    │
                  │   pair = 6 rows total          │
                  │   + 1 PROTO-01 row             │
                  │   + 2 PROTO-02 rows)           │
                  └────────────────────────────────┘
                                │
                                ▼
                  ┌────────────────────────────────┐
                  │ .planning/STATE.md +           │
                  │ .planning/ROADMAP.md updates   │
                  │ (orchestrator-owns; D-15)      │
                  └────────────────────────────────┘
```

### Recommended Directory Layout

```
.planning/
├── v1.3-BENCH-RESULTS.md        # NEW (created by Plan 12-04). Phase 12 appends 6 rows + 1 PROTO-01 row + 2 PROTO-02 rows; Phase 13 appends more; Phase 14 closes.
├── v1.3-COVERAGE-MATRIX.md      # already exists (Phase 11 output) — referenced from §5 BENCH coverage in BENCH-RESULTS.md
└── v1.3/                        # NEW directory (created by Plan 12-04)
    ├── bench-logs/              # per-cycle tee'd logs
    │   ├── W27C512-uno-2026-05-20.log
    │   ├── W27C512-leonardo-2026-05-20.log
    │   ├── SST27SF512-uno-2026-05-20.log
    │   ├── SST27SF512-leonardo-2026-05-20.log
    │   ├── W27C257-uno-2026-05-20.log
    │   ├── W27C257-leonardo-2026-05-20.log
    │   └── SST27SF512-blocked-write-<board>-2026-05-20.log   # PROTO-01 evidence (D-04)
    └── scope/                   # PROTO-02 evidence photos
        ├── uno-vpp-write-2026-05-20.png
        ├── leonardo-vpp-write-2026-05-20.png
        ├── uno-vpp-idle-2026-05-20.png        # optional
        └── leonardo-vpp-idle-2026-05-20.png   # optional
```

### Pattern 1: Operator-Driven Checkpoint Tasks

**What:** Each chip plan is a sequence of operator-gated tasks. The executor presents a clear "do this at the bench, paste outputs here" prompt and waits.

**When to use:** All tasks in plans 12-01, 12-02, 12-03 (per D-14 `autonomous: false`).

**Structure (per chip plan):**

| Task | Operator Action | Executor Action |
|------|----------------|-----------------|
| 0 (setup confirm) | Seat chip, confirm Uno connected (USB), confirm scope probe at VPP pin | Wait for operator confirmation |
| 1 (Uno cycle) | Run `cd firestarter_app && ./firestarter_test.sh <CHIP> 2>&1 \| tee ../.planning/v1.3/bench-logs/<CHIP>-uno-2026-05-20.log`; trigger scope capture during the `write` phase; save photo | Read log path + photo path from operator; extract `chip_id_read`, `info` outcome, `write` outcome, `read` outcome, `verify` outcome, `blank_pre` outcome; append Uno row to BENCH-RESULTS.md |
| 2 (board swap) | Swap to Leonardo (USB cable to Leonardo); confirm `firestarter hw` reports Leonardo | Wait for confirmation |
| 3 (Leonardo cycle) | Same as Task 1 with `-leonardo-` filename suffix; second scope photo for Leonardo | Same extraction; append Leonardo row |
| 4 (commit) | (executor-driven) | Commit STATE.md + ROADMAP.md + BENCH-RESULTS.md as one unit |

**12-02 only:** Insert one additional task **after** Task 3 for D-04 PROTO-01 blocked-write evidence (see Pattern 2 below).

### Pattern 2: PROTO-01 Blocked-Write Evidence Capture (12-02 task 4)

**What:** Operator deliberately attempts a write with the wrong chip name to capture the safety-stack refusal.

**When to use:** Once, folded into Plan 12-02 per D-13. Recommended chip: SST27SF512 socketed (its chip-ID 0x0000bfa4 is distinct from any WINBOND ID — clean evidence of mismatch).

**Exact commands:**

```bash
# Chip in socket: SST27SF512 (already there from Task 3 of 12-02)
# Step 1: confirm chip-id read returns SST27SF512's ID
cd /workspaces/firestarter_app
firestarter -v id SST27SF512 2>&1 | tee /workspaces/.planning/v1.3/bench-logs/SST27SF512-id-confirm-<board>-2026-05-20.log
# Expected: log line contains "0xbfa4" (the SST27SF512 chip_id_value from DB)

# Step 2: deliberately attempt to write to W27C512 while SST is socketed
firestarter -v write W27C512 test_data/full_data.bin 2>&1 \
  | tee /workspaces/.planning/v1.3/bench-logs/SST27SF512-blocked-write-<board>-2026-05-20.log
# Expected: firmware refuses; log contains MSG_ERR_CHIP_ID_MISMATCH (0xB9) or
#           MSG_WARN_CHIP_ID_MISMATCH (0x83) — decoded as
#           "Chip ID 0xbfa4 does not match expected ID 0xda08"
# CLI exit code: non-zero (host re-surfaces firmware ERR or WARN)
```

**Operator grep target:** `grep -E "Chip ID|MSG_(WARN|ERR)_CHIP_ID_MISMATCH|0xB9|0x83" <log-file>`

### Pattern 3: Scope-Photo Timing Against the Log

**What:** Operator triggers the scope capture during the `write` phase by watching the harness's stdout for the "Writing to <CHIP>" banner (`firestarter_test.sh` line 146) — the next several seconds are when VPP is asserted at 12V.

**When to use:** Once per board, during Plan 12-01's Uno cycle (`.planning/v1.3/scope/uno-vpp-write-2026-05-20.png`) and Leonardo cycle (`leonardo-vpp-write-2026-05-20.png`). Plan 12-02 / 12-03 reuse the same Uno/Leonardo photos by reference unless the operator notices a board-specific VPP anomaly worth capturing.

**Probe placement per chip:**

| Chip | Pinout | VPP probe point | Notes |
|------|--------|-----------------|-------|
| W27C512 (BENCH-01) | DIP28_27512 | Socket pin 22 | Shared with `oe-pin` (multiplexed; 12V during write, ~5V VCC during read) |
| SST27SF512 (BENCH-02) | DIP28_27512 | Socket pin 22 | Same as W27C512 |
| W27C257 (BENCH-05) | DIP28_27256 | Socket pin 1 | **Different probe point** — DIP28_27256 has dedicated `vpp-pin: [1]`, not multiplexed with OE |

**Operator caution:** Plan 12-03's first task must remind the operator to **re-probe** pin 1 (the W27C257 VPP pin) before the W27C257 cycle. Otherwise the scope captures pin 22 (which on DIP28_27256 is `oe-pin`, not VPP), producing a misleading photo.

### Anti-Patterns to Avoid

- **Treating Phase 12 as automated executable.** Plans 12-01/02/03 are `autonomous: false`; the executor's job is to drive the conversation with the operator and write results, NOT to invoke `firestarter` commands. Any task whose action begins with "run `firestarter ...`" is an instruction TO THE OPERATOR, not to the executor.
- **Auto-generating BENCH-RESULTS.md rows from un-paste'd log files.** The operator's `tee` log path is the source-of-truth for cell values; the executor reads files the operator names, not files it discovers.
- **Skipping the W27C257 probe-point swap reminder.** DIP28_27256 pin 1 vs DIP28_27512 pin 22 is a load-bearing difference. Without the reminder, the photo captures the wrong pin and PROTO-02 evidence for BENCH-05 is invalid.
- **Modifying `firestarter_test.sh`.** D-02 locks it. If a chip can't run the harness verbatim, the fallback is `firestarter_app/tools/bench_cycle.sh` — NOT a patch to the existing harness.
- **Folding PROTO-01 blocked-write capture into BOTH Plans 12-02 and 12-03.** D-13 chose SST27SF512 (Plan 12-02) as the single capture site. One refusal = sufficient evidence (the firmware safety path is shared across all algo-0x07 chips per `[[project_db-overrides-firmware-is-ground-truth]]`).
- **Committing scope photos to git as PNG blobs.** Verify with the user before doing so; large binary blobs in `.planning/` may need git-LFS or an external link. Default: commit PNG inline (≤500KB typical) and let the milestone close decide if archival needs change.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Generate the deterministic test image | Custom Python "address-walking + data-walking + 0x55/0xAA + seeded-random" image generator | `firestarter_test.sh`'s built-in `dd if=/dev/urandom of=low_data.bin && dd if=/dev/urandom of=high_data.bin && cat ... > full_data.bin` (lines 80–87) | The harness already does it; the verify step compares read-back against the same file written, so a fresh urandom per cycle is fine (verify is byte-identity, not pattern-recognition). The REQUIREMENTS.md note about "address-walking + data-walking" is aspirational documentation; the project ships with urandom and the harness is what BENCH-* cycles validate. |
| Parse `chip_database.json` for size / chip-id / type | New Python introspection helper | `jq` from `firestarter_test.sh` lines 50–69 (already does it) | Three identical `jq` invocations already extract `size_bytes`, `chip_id_check`, and `(.electrical.type == "Flash/EEPROM")` for the harness. For BENCH-RESULTS.md row population, the same `jq` from a one-off operator command suffices. |
| Drive the serial protocol | Custom serial state-machine driver | `firestarter` CLI (calls `eprom_operations.py` → `serial_comm.py` → INIT/MAIN/END state machine) | The whole point of this phase is to validate the existing serial path. Writing a new driver would invalidate the test. |
| Decode `MSG_ERR_CHIP_ID_MISMATCH` (0xB9) in logs | Custom `messages.py` re-parser | The CLI already decodes message IDs to human-readable strings in `-v` mode via `firestarter/messages.py` CATALOG (line 178). Operator's `grep "Chip ID"` in the tee'd log captures the decoded text. | The catalog is the contract; the host decoder already produces the human-readable line. |
| Scope-photo annotation overlay | Image-processing pipeline | Operator's scope-built-in annotation (most digital scopes export with cursors + scale labels baked in) | D-06 only requires "voltage + time-base + probe location visible" — scope's native annotation export already satisfies this. |
| Resume-from-mid-cycle logic | Persistent state file with task-by-task progress | The tee'd log file at `.planning/v1.3/bench-logs/<chip>-<board>-<date>.log` is the resume anchor (D-14). Operator inspects last completed step; the executor's continuation prompt asks "what's the last green step?" and proceeds. | Phase 11 already established orchestrator-owns-tracking; Phase 12 extends the pattern. |

**Key insight:** This phase has near-zero hand-rollable scope. Every observation has an existing CLI/harness path. The "research" is mostly about **mapping operator actions to existing infrastructure**, not about choosing libraries.

## Runtime State Inventory

**This phase is NOT a rename/refactor/migration.** It is observation-only against the running v1.3 system. Per the Step 2.5 protocol:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no DB schema changes, no key renames, no collection renames. The `chip_database.json` file is **read** by `firestarter_test.sh` (via `jq`) and by `firestarter` CLI (via `EpromDatabase`), but not modified. | None |
| Live service config | None — no n8n / Datadog / Tailscale / Cloudflare equivalents in this project. Closest analog: Arduino EEPROM-stored `rurp_configuration_t` (R1/R2 + board revision), which is **read** during `firestarter config` for diagnostic confirmation but not written. | None |
| OS-registered state | None — no Task Scheduler / pm2 / launchd / systemd registrations created or referenced. Hardware operations are interactive shell invocations. | None |
| Secrets/env vars | None — the project uses no secrets. One env var (`FIRESTARTER_DB_FILE`) is the override path for `chip_database.json` per `tools/check_dispatch.py` precedent; **not set** in Phase 12's standard invocation. | None |
| Build artifacts | None — no installed-package renames, no `egg-info` to flush, no Docker image retags. The `pip install -e .` is editable; harness invokes the installed CLI, which resolves to the same source tree. | None |

**Verified by:** Reading `firestarter_test.sh` (172 lines) end-to-end + `write_test.sh` (127 lines) end-to-end + grepping `chip_database.json` for the three bench chip records + reading `pinouts.json` for DIP28_27256 / DIP28_27512 / DIP32_STD. No write paths, no caches, no registered state.

**The canonical question** ("after every file in the repo is updated, what runtime systems still have the old string cached?") **does not apply** — Phase 12 changes no strings.

## Common Pitfalls

### Pitfall 1: W27C257 VPP probe point ≠ W27C512 VPP probe point

**What goes wrong:** Operator probes pin 22 for all three chips (the BENCH-01 / BENCH-02 location on DIP28_27512). For W27C257 (DIP28_27256), pin 22 is `oe-pin`, NOT VPP. The scope captures a 5V CE/OE strobe, not the 12V VPP rail. The Plan 12-03 PROTO-02 photo is invalid.

**Why it happens:** Three "28-pin" chips with two different pinout classes. The pinout key (`DIP28_27512` vs `DIP28_27256`) maps `vpp-pin` to different physical socket pins:
- `DIP28_27512`: `"vpp-pin": [22], "oe-pin": [22]` (multiplexed)
- `DIP28_27256`: `"vpp-pin": [1]` (dedicated)

**How to avoid:** Plan 12-03's first task explicitly instructs the operator: "BEFORE seating W27C257 in the socket, move the scope probe from socket pin 22 to socket pin 1. DIP28_27256 has VPP on pin 1, NOT pin 22."

**Warning signs:** Photo shows ~5V swings at write time instead of 12V; idle level is logic-rail behavior (clean digital edges), not regulator output (slower rise/fall).

### Pitfall 2: Harness exits 1 on colordiff mismatch without distinguishing "chip wrote bytes wrong" vs "read came back wrong"

**What goes wrong:** `firestarter_test.sh` line 149–153 runs `colordiff ... <(xxd full_data.bin) <(xxd read_back.bin)`; if the diff is non-zero, the script exits 1 with "Read back data does not match". The operator (and the executor reading the log) cannot tell whether the chip failed to program or the read-back path corrupted bytes.

**Why it happens:** The harness fuses write+verify+read into one pass; the colordiff is the only correctness signal.

**How to avoid:** Plan 12-01/02/03 tasks should split the diagnosis when colordiff fails: (a) re-run `firestarter verify <chip> data.bin` (chip-side verify; if green, the read path is suspect, not the chip); (b) hexdump the first 64 bytes of `read_back.bin` to spot stuck-bit patterns. Document these as fallback steps in the plan; do not pre-emptively run them on green cycles.

**Warning signs:** Log contains "Files are identical" → green; log contains "Read back data does not match" → operator runs the fallback diagnosis above. Either way, BENCH-RESULTS.md row `verify` cell records `OK` or `FAIL: <byte-count diff>` (D-08).

### Pitfall 3: Pre-cycle blank-check fails on a chip that wasn't UV-erased recently

**What goes wrong:** UV-EPROMs need physical UV exposure to return to 0xFF. If the operator socketed a chip that's already been programmed in a previous bench cycle (or is unknown-state from a box of supplied parts), the `firestarter blank <chip>` call (D-07 step 4) returns NOT-BLANK and the harness exits 1 before reaching the write step.

**Why it happens:** The harness assumes the operator handed it a blank chip. There's no automatic erase for UV-EPROMs (they can't be electrically erased — that's why the phase's post-cycle blank check is skipped).

**How to avoid:** Plan 12-01/02/03 setup tasks (Task 0) include: "Confirm chip has been UV-erased within the last hour (or is a brand-new part) before seating." If the pre-cycle blank check fails, the operator pulls the chip, re-UV-erases (typical: 15–25 minutes under a UV-C source), and re-seats. The BENCH-RESULTS row `blank_pre` cell records `BLANK` (green) or `NOT-BLANK` (failure, with cycle aborted before write).

**Warning signs:** Log contains `MSG_ERR_NOT_BLANK` (0xB0) → "Not blank, at 0x%06x, v: 0x%02x" decoded message. The address shows where non-blank bytes were found.

### Pitfall 4: Test image is fresh-random per cycle (NOT reproducible across Uno → Leonardo)

**What goes wrong:** Operator expects a passing Uno cycle and a passing Leonardo cycle to write+read-back the **same** bytes. They don't — each `firestarter_test.sh` invocation generates a fresh `full_data.bin` via `dd if=/dev/urandom`. So "the byte at address 0x4000 was 0xDE on Uno; let me see if Leonardo also wrote 0xDE" is a meaningless cross-board comparison.

**Why it happens:** `firestarter_test.sh` lines 82–87 generate two halves from `/dev/urandom`, then concatenate. No seed, no fixed pattern, no cross-run idempotence. The harness's verify step compares `full_data.bin` (just-written) against `read_back.bin` (just-read) **within the same cycle** — that's all the verify guarantees.

**How to avoid:** Treat each cycle as independent. BENCH-RESULTS.md row `verify` = `OK` means "this Uno cycle's write matched this Uno cycle's read-back" — it does NOT mean "Uno wrote the same image Leonardo wrote." If cross-board byte-comparison is ever needed (it is NOT for Phase 12; verify byte-identity per cycle is the BENCH gate), the operator can `cp test_data/full_data.bin /tmp/uno-image.bin` between cycles and skip the harness's image regeneration — but this is **not in scope** per CONTEXT.md ("BENCH gate is per-cycle byte-identity").

**Warning signs:** None for the spec'd flow. Only a concern if someone tries to add cross-board byte-comparison logic later.

### Pitfall 5: Operator forgets to swap USB cable / `--port` between Uno and Leonardo cycles

**What goes wrong:** Operator runs `./firestarter_test.sh W27C512` twice in a row without unplugging Uno + plugging Leonardo. The harness runs against the same board twice; one of the two "boards" in the BENCH-RESULTS row pair is actually a duplicate Uno run.

**Why it happens:** No board-pin in the harness. `firestarter` discovers ports via `SerialCommunicator.find_and_connect` — whichever USB-serial port is open wins.

**How to avoid:** Task 2 of each chip plan ("board swap") explicitly instructs the operator to (a) unplug current board, (b) plug other board, (c) run `firestarter hw` to confirm the printed revision matches the expected board. The harness's own `Hardware Version` line (`firestarter_test.sh` line 131) captures `firestarter hw` output every cycle — the executor can verify the log's `hw` revision differs between the `-uno-` and `-leonardo-` log files.

**Warning signs:** Two log files for the same chip with identical `hw` revision lines → operator forgot to swap. Executor's BENCH-RESULTS.md row population should refuse to write the second row if the `hw` revision matches the first (sanity check).

### Pitfall 6: PROTO-01 blocked-write evidence captures the wrong refusal mode

**What goes wrong:** Operator runs `firestarter write W27C512 data.bin` while SST27SF512 is socketed and expects a clean "blocked write" log. But several refusal paths exist:
- **Firmware-side** chip-id mismatch → `MSG_ERR_CHIP_ID_MISMATCH` (0xB9) on the wire; non-zero CLI exit (cleanest evidence).
- **Firmware-side warn** → `MSG_WARN_CHIP_ID_MISMATCH` (0x83); write may proceed depending on `FLAG_FORCE`.
- **Host-side preflight** abort (no firmware round-trip) → CLI prints something like "EPROM 'W27C512' not found" — but `W27C512` IS in the DB, so this path doesn't fire here.

The intended evidence per D-04 is the firmware-side mismatch. If the operator runs with `-f` (FLAG_FORCE) — which they shouldn't — the firmware downgrades 0xB9 to a warning and may proceed, producing the wrong evidence.

**Why it happens:** Three different refusal modes exist; D-04's "safety-stack refusal" specifically means the firmware 0xB9 error path.

**How to avoid:** Plan 12-02 Task 4 explicitly runs WITHOUT `-f`. The command is `firestarter -v write W27C512 test_data/full_data.bin` — `-v` for verbose-mode message decoding, no `-f`. Plan validates by grepping the log for `MSG_ERR_CHIP_ID_MISMATCH` or the decoded substring "Chip ID 0x..." in the ERROR line.

**Warning signs:** Log contains `MSG_WARN_CHIP_ID_MISMATCH` (0x83) instead of `MSG_ERR_CHIP_ID_MISMATCH` (0xB9) → operator used `-f` or there's a FLAG_FORCE leak. Re-run without `-f`.

## Code Examples

### Bench cycle invocation (the one command per chip-board pair)

```bash
# Source: /workspaces/firestarter_app/firestarter_test.sh (verbatim per D-02)
# Operator runs this with the chip socketed and the correct board connected.
cd /workspaces/firestarter_app
./firestarter_test.sh W27C512 2>&1 \
  | tee /workspaces/.planning/v1.3/bench-logs/W27C512-uno-2026-05-20.log

# Expected stdout sequence (paraphrased from firestarter_test.sh logic):
#   Firestarter Python Application
#   firestarter, version <version>
#   Eprom: W27C512, memory size: 0x10000
#
#   --- Test: Firmware Version ---
#   --- Test: Hardware Version ---
#   --- Test: Config ---
#   --- Test: VPP ---                  <-- D-07 step 2; SCOPE-TRIGGER WINDOW
#   --- Test: VPE ---                  <-- D-07 step 2 continued
#   --- Test: W27C512 Chip ID ---     <-- D-07 step 3; PROTO-01 EVIDENCE LINE
#   --- Test: Writing to W27C512 ---  <-- D-07 step 5; SCOPE-TRIGGER WINDOW
#   --- Test: Verifying data ---      <-- D-07 step 7
#   --- Test: Reading from W27C512 ---<-- D-07 step 6 (note harness order: write→verify→read, not write→read→verify; the verify uses the chip not the file readback)
#   Files are identical               <-- colordiff success
#   --- Test: Listing all EPROMs ---
#   --- Test: Searching for W27C512 ---
#   --- Test: Info for W27C512 ---
#   All tests passed
```

**Note on D-07 vs harness order:** D-07 specifies `write → read → verify`. The harness runs `write → verify → read → colordiff(full_data.bin, read_back.bin)`. The harness's "verify" is a firmware-side byte-compare (no read transfer); the harness's colordiff after `read` is the file-side byte-identity check. Both correspond to D-07 step 7 "byte-identical verify" — one chip-side, one host-side. **This is acceptable** — the harness produces both pieces of evidence; the BENCH-RESULTS row's `verify` cell records the colordiff result (the harness exits 1 if either fails).

### Pre-cycle blank check insertion (D-07 step 4)

The stock harness does NOT run a pre-cycle blank check (it runs erase+blank only if `CAN_ERASE == true`, which is false for UV-EPROMs). Plan 12-01/02/03's Task 1 must include an extra manual call before the harness, OR the executor wraps the harness invocation:

```bash
# D-07 step 4 (pre-cycle blank check, manual addition):
cd /workspaces/firestarter_app
firestarter -v blank W27C512 2>&1 \
  | tee -a /workspaces/.planning/v1.3/bench-logs/W27C512-uno-2026-05-20.log

# Expected:
#   "Blank check for W27C512 successful." → BLANK (BENCH-RESULTS row blank_pre cell = "BLANK")
# Failure:
#   MSG_ERR_NOT_BLANK (0xB0) decoded → "Not blank, at 0x000004, v: 0x42"
#   → BENCH-RESULTS row blank_pre cell = "NOT-BLANK"; operator UV-erases and re-seats; cycle restarts
```

**Then** run the harness for the rest of the cycle:

```bash
./firestarter_test.sh W27C512 2>&1 \
  | tee -a /workspaces/.planning/v1.3/bench-logs/W27C512-uno-2026-05-20.log
```

The `tee -a` append puts both the blank check output and the harness output in one log file — keeping the resume-anchor discipline of D-14.

### PROTO-01 chip-ID line extraction from log

```bash
# Source: firestarter/messages.py CATALOG entries 0x83 (warn) + 0xB9 (err) format
# Format: "Chip ID %#04x does not match expected ID %#04x"
# Lookup line in tee'd log:
grep -iE "chip[_-]id|MSG_(WARN|ERR)_CHIP_ID" /workspaces/.planning/v1.3/bench-logs/W27C512-uno-2026-05-20.log

# Expected match in a green W27C512 cycle:
#   "Chip ID check passed for W27C512: <hex value> (0.XYs)"
#   Chip ID line — operator pastes this 1-line snippet into BENCH-RESULTS.md PROTO-01 row.
```

### Blocked-write capture (D-04 + D-13, Plan 12-02 Task 4)

```bash
# Chip seated: SST27SF512 (still from 12-02 Task 3).
# Step 1: confirm chip-id reads 0xbfa4 (SST27SF512's DB chip_id_value).
cd /workspaces/firestarter_app
firestarter -v id SST27SF512 2>&1 \
  | tee /workspaces/.planning/v1.3/bench-logs/SST27SF512-id-confirm-leonardo-2026-05-20.log

# Step 2: deliberately attempt to write the WRONG chip name (W27C512) while SST is socketed.
firestarter -v write W27C512 test_data/full_data.bin 2>&1 \
  | tee /workspaces/.planning/v1.3/bench-logs/SST27SF512-blocked-write-leonardo-2026-05-20.log
# Exit code should be non-zero (host re-raises firmware ERROR).
echo "Exit: $?"

# Expected log content (decoded from MSG_ERR_CHIP_ID_MISMATCH = 0xB9):
#   "Chip ID 0xbfa4 does not match expected ID 0xda08"
# Operator copies the line into BENCH-RESULTS.md PROTO-01 evidence row.
```

### Scope photo capture timing

```bash
# Coordination: operator watches harness stdout for the "Writing to <CHIP>" banner.
# Source: firestarter_test.sh line 146 echoes "Writing to W27C512" before invoking the firestarter CLI.
# Operator's window: from the moment "Writing to W27C512" prints until the harness moves to "Verifying data ...".
# For a 64K chip at ~10 ms pulse * 65536 bytes ≈ 10 minutes write time → ample window for scope trigger.
# For a 32K W27C257 → ~5 minutes window.
# Operator's scope captures the VPP rail at the chip socket VPP pin during this window;
# saves as PNG named per D-05 convention.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Per-cycle test images = ad-hoc operator-provided binaries | `firestarter_test.sh`-generated `dd if=/dev/urandom` halves concatenated to `full_data.bin` | v1.0 (harness shipped) | Cycle reproducibility is per-invocation, not cross-board. Verify gate is byte-identity within a cycle, not across boards. |
| Text-prefix log emits (`OK:`, `ERROR:`, etc.) | 1-byte message IDs + raw byte parameters; host decodes via `firestarter/messages.py` CATALOG | v1.2 (shipped 2026-05-19) | Operator's `grep` against tee'd log targets the **decoded** human-readable string (e.g. "Chip ID 0x... does not match"), not the raw wire bytes. The catalog produces stable English text per ID. |
| Manual chip-id-mismatch verification via "if write fails, must have been ID-blocked" | Explicit `MSG_ERR_CHIP_ID_MISMATCH` (0xB9) with both detected + expected IDs printed | v1.2 (rolled into the message-ID rework) | PROTO-01 blocked-write evidence captures the **decoded** "Chip ID 0xbfa4 does not match expected ID 0xda08" line — operator no longer has to infer the refusal from generic error. |
| Coverage matrix existed as scattered references in PROJECT.md / ROADMAP.md | Single-file `.planning/v1.3-COVERAGE-MATRIX.md` (339 chips, §3 enumeration + §5 BENCH coverage) | Phase 11 (shipped 2026-05-19) | Phase 12's "BENCH-* chips represent the family" claim is now matrix-backed evidence, not assertion. Plan 12-04 scaffolds BENCH-RESULTS.md to cross-reference the matrix's §5 tables. |

**Deprecated / outdated:**

- Treating `firestarter_test.sh`'s "Eprom Tests" branch as expecting `electrical.type == "Flash/EEPROM"` for `CAN_ERASE`. UV-EPROMs explicitly fall to the `else` branch (lines 158–161, "Erase not supported, skipping erase and blank test") — this is correct behavior for all three Phase 12 bench chips and is NOT a defect.
- The reference to `WARNING-4` (`firestarter_test.sh` / `write_test.sh` reference deleted `database_generated.json`) — surfaced in STATE.md "Carried Over From v1.1" — does NOT apply to current `firestarter_test.sh`, which reads `./firestarter/data/chip_database.json` directly (line 31). WARNING-4 was about an older path; verified by reading the live harness.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Operator's oscilloscope can export PNG/JPG with scale annotations visible | D-06 / Pattern 3 | LOW — D-05 explicitly allows BMP/SVG/CSV fallback; operator chooses format that satisfies "voltage + time-base + probe location legible" |
| A2 | UV-erase chamber available to refresh chips between cycles | Pitfall 3 | LOW — implicit in the project being able to do UV-EPROM work at all; if not available, operator uses pre-erased parts |
| A3 | Both Uno and Leonardo boards are firmware 3.0.0-dev (v1.2 ship state) | Operator setup prerequisites | MEDIUM — if a board has older firmware, message-ID decoding will partly fail; mitigation: `firestarter fw` check at start of each cycle (harness already does this at line 127) |
| A4 | `firestarter_test.sh` reads `./firestarter/data/chip_database.json` (relative path) and operator's `cd firestarter_app` discipline preserves this | D-02 / Code Examples | LOW — harness line 31 hardcodes the relative path; D-02 requires the `cd firestarter_app && ./firestarter_test.sh ...` invocation pattern |
| A5 | Scope photos as PNG attachments in `.planning/v1.3/scope/` are acceptable to commit to git (no LFS required) | Anti-Patterns / Layout | MEDIUM — if file sizes turn out to be hundreds of MB per photo, operator may need to downsample or move to a separate artifact repo; default ≤500KB per scope export should be fine |
| A6 | `firestarter_test.sh` invocation pattern from D-02 (`cd firestarter_app && ./firestarter_test.sh <CHIP> ...`) does not require `--port`/`--board` flags because port auto-discovery works | Operator setup | LOW — confirmed by reading harness (line 105 calls `firestarter $VERBOSE_FLAG $CMD_NAME $CMD_ARGS $EPROM $FILE_NAME` with no port flag); `SerialCommunicator.find_and_connect` auto-discovers single connected USB-serial port |
| A7 | Plan 12-02's PROTO-01 blocked-write evidence command (`firestarter write W27C512 ...` while SST27SF512 is socketed) actually trips firmware-side `MSG_ERR_CHIP_ID_MISMATCH` (0xB9) rather than a host-side preflight refusal | Pattern 2 / Pitfall 6 | MEDIUM — verified via codepath inspection: `eprom_operations.py::write_eprom` doesn't preflight chip-ID (only the explicit `id` subcommand does); write command builds command_dict and sends to firmware; firmware-side handler verifies chip-ID before pulse. If the host-side path turns out to abort before serial round-trip in some refactor, the evidence collected is the wrong line. Mitigation: Plan 12-02 Task 4 checks for 0xB9 specifically and falls back to "any line containing 'Chip ID' and 'does not match'" as the evidence string |
| A8 | scope time required to capture a single VPP write-pulse window is < the full chip-write duration (10 ms × N_bytes seconds for algo-0x07) | Pattern 3 | LOW — 64K × 10 ms ≈ 10 min for W27C512; scope trigger has multi-minute window. No risk. |

**Note:** All other claims in this RESEARCH.md are `[VERIFIED]` by direct file inspection of the cited paths (line numbers given) — see Sources section. Only the 8 items above carry assumed-knowledge weight.

## Open Questions

1. **Should the scaffold plan (12-04) pre-populate BENCH-RESULTS.md with empty rows for all 6 (chip, board) pairs, or only the column headers + leave row population to chip plans?**
   - What we know: D-08 specifies 14 columns + 6 rows total. D-12 says "scaffold". Phase 14 owns final aggregation per CONTEXT.md "Out of scope".
   - What's unclear: whether "scaffold" means just the table headers or the table headers + 6 placeholder rows with `-` cells.
   - Recommendation: scaffold the table headers only + headers for the PROTO-01 evidence subsection + headers for the PROTO-02 evidence subsection. Chip plans append fully-populated rows. This avoids the "edit-an-empty-row" pattern (error-prone) in favor of "append-a-new-row" (idempotent on resume).

2. **For the PROTO-02 idle-state photo (D-05 optional artifact), when is the right capture moment?**
   - What we know: D-05 calls it optional; idle state is "between operations".
   - What's unclear: whether "between" means between two cycle steps (e.g., between `vpp -t 5` and `id`) or after the full cycle ends (chip still socketed but harness done).
   - Recommendation: after harness completion, before chip removal — this is the cleanest "all command paths idle" window. Operator captures one optional photo per board if scope is still set up. Not gating to plan completion.

3. **Does the executor need to verify the scope photo file exists at the path the operator names, or trust the operator?**
   - What we know: D-15 says "orchestrator commits BENCH-RESULTS.md in lockstep"; that requires the photo file to exist at commit time (otherwise the BENCH-RESULTS.md link is broken).
   - What's unclear: whether the executor's continuation prompt should explicitly `ls -l <photo path>` to confirm before writing the row, or trust the operator's claim.
   - Recommendation: executor does an `ls -l` check + size > 0 verification, fails the task if missing. Cheap; surfaces a missing-photo problem at the right moment.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `firestarter` CLI | All cycle commands | ✓ (assumed installed; `pip install -e .` from firestarter_app/) | v1.2 ship state | Operator runs `pip install -e .` in Plan 12-04 setup task if not present |
| `jq` | `firestarter_test.sh` DB parsing | ✓ (system) | any modern jq | Apt-install if missing; harness fails fast otherwise |
| `tee` | Per-cycle log capture | ✓ (coreutils) | any | None needed |
| `colordiff` | `firestarter_test.sh` line 149 | ✓ (typically installed; verify) | any | If missing, operator `apt install colordiff` OR substitutes `diff --side-by-side` — but this requires a harness edit (D-02 violates). Fallback: install colordiff via apt as setup step. |
| `xxd` | `firestarter_test.sh` line 149 | ✓ (vim-common) | any | Apt-install if missing |
| `dd` | `firestarter_test.sh` lines 83–84 | ✓ (coreutils) | any | None needed |
| Arduino Uno board (R3) | All Uno cycles | Operator's bench | RURP shield-compatible | None — required hardware |
| Arduino Leonardo board | All Leonardo cycles | Operator's bench | RURP shield-compatible | None — required hardware |
| RURP shield | All bench cycles | Operator's bench | calibrated R1/R2 | Confirm via `firestarter config` at start of each plan |
| W27C512 chip (UV-erased) | Plan 12-01 | Operator's parts bin | 28-pin DIP, algo 0x07 | None — required hardware |
| SST27SF512 chip (UV-erased) | Plan 12-02 | Operator's parts bin | 28-pin DIP, algo 0x07 | None — required hardware |
| W27C257 chip (UV-erased) | Plan 12-03 | Operator's parts bin | 28-pin DIP, algo 0x07 | If unavailable, plan 12-03 cannot proceed (D-01 locks the chip — no swap allowed). Defer plan 12-03 until chip is sourced. |
| Oscilloscope + probe | PROTO-02 evidence | Operator's bench | DC-coupled, 20 MHz+ bandwidth sufficient | None — required instrument |
| UV-EPROM eraser | Pitfall 3 mitigation | Operator's bench | UV-C wavelength ~254nm | If chips arrive pre-erased, eraser not needed in-cycle. |

**Missing dependencies with no fallback:** Only physical artifacts (chips, scope, boards). If any is missing, the relevant plan blocks until sourced. No software gaps.

**Missing dependencies with fallback:** Only `colordiff` (apt-install). Other system tools (`jq`, `tee`, `xxd`, `dd`) are standard.

## Validation Architecture

**Phase 12 is operator-on-bench. There is NO automated pytest suite to wire.** This section documents the manual UAT contract that replaces the Nyquist test-mapping pattern for this phase.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | **Manual UAT** — no automated test scaffold. All verification is operator-driven via `firestarter_test.sh` + scope photos + log inspection. |
| Config file | None — `firestarter_test.sh` is the harness (172 lines, repo HEAD, frozen per D-02). |
| Quick run command | `cd firestarter_app && ./firestarter_test.sh <CHIP_NAME>` (per-cycle; ~5–10 min per chip per board for 64K density) |
| Full suite command | Plans 12-01 + 12-02 + 12-03 executed in sequence by the operator at the bench (3 chips × 2 boards = 6 cycles + 1 PROTO-01 capture in 12-02; ≈ 45–90 min total bench time including chip swaps) |

### Phase Requirements → Verification Map

| Req ID | Behavior | Test Type | Verification Procedure | Evidence Artifact |
|--------|----------|-----------|------------------------|-------------------|
| BENCH-01 | W27C512 cycle green on Uno + Leonardo | manual-UAT | Operator runs `./firestarter_test.sh W27C512` on Uno, then Leonardo. Log contains "All tests passed" both times. | `.planning/v1.3/bench-logs/W27C512-uno-2026-05-20.log` + `.planning/v1.3/bench-logs/W27C512-leonardo-2026-05-20.log` + BENCH-RESULTS.md rows for (W27C512, uno) and (W27C512, leonardo) showing `info`/`write`/`read`/`verify` cells = `OK` |
| BENCH-02 | SST27SF512 cycle green on Uno + Leonardo | manual-UAT | Same procedure with SST27SF512 | Same shape of evidence: 2 log files + 2 BENCH-RESULTS rows |
| BENCH-05 | W27C257 cycle green on Uno + Leonardo | manual-UAT | Same procedure with W27C257. **Note probe-point swap** for PROTO-02 (pin 1, not pin 22 — see Pitfall 1) | Same shape: 2 log files + 2 BENCH-RESULTS rows |
| PROTO-01 | Chip-ID read returns DB-declared value for all 3 chips; mismatches blocked by safety stack | manual-UAT (observation + blocked-write evidence) | For each bench cycle: grep tee'd log for `chip-id`/`MSG_*CHIP_ID*` line; confirm hex matches DB `chip_id_value` (W27C512=0x0000da08, SST27SF512=0x0000bfa4, W27C257=0x0000da02). **Plus** one deliberate blocked-write capture on SST27SF512 in Plan 12-02 Task 4. | 6 chip-id snippets in BENCH-RESULTS rows + 1 dedicated PROTO-01 evidence row showing `MSG_ERR_CHIP_ID_MISMATCH` line + log path |
| PROTO-02 | VPP regulator engages at 12V ±5% during write/erase; idles between operations | manual-UAT (scope photo) | Scope-capture VPP pin (DIP28_27512 pin 22 / DIP28_27256 pin 1) during `firestarter write` cycle. One photo per board minimum. | `.planning/v1.3/scope/uno-vpp-write-2026-05-20.png` + `.planning/v1.3/scope/leonardo-vpp-write-2026-05-20.png` + 2 PROTO-02 evidence rows in BENCH-RESULTS.md with measured_vpp_volts + tolerance_band_check = Y |

### Sampling Rate

- **Per task commit:** No automated test runs. Each task's "verification" is the operator's PASS/FAIL on the bench plus the corresponding tee'd log line / scope photo.
- **Per wave merge:** N/A — chip plans are sequential waves with one chip each.
- **Phase gate (consumed by `/gsd-verify-work`):** Before phase close, the following MUST be true:
  1. `.planning/v1.3-BENCH-RESULTS.md` exists with 6 chip-board rows (BENCH-01 uno+leonardo, BENCH-02 uno+leonardo, BENCH-05 uno+leonardo) all showing `verify` = `OK`.
  2. BENCH-RESULTS.md PROTO-01 evidence row contains the SST27SF512 blocked-write log snippet with `MSG_ERR_CHIP_ID_MISMATCH` or decoded "Chip ID ... does not match expected ID".
  3. BENCH-RESULTS.md PROTO-02 evidence rows (one per board) contain measured_vpp_volts within 11.4–12.6V (12V ±5%) with linked scope photo path that resolves to an existing file > 0 bytes.
  4. Per-cycle log files exist at the paths cited in the BENCH-RESULTS rows (executor `ls -l` confirms before writing each row per Open Question 3).
  5. STATE.md `Deferred Items` table no longer shows Phase 08 SC#2/SC#3 or Phase 09 Plan-05 Task 3 as "human_needed" — orchestrator updates these as part of Plan 12-01's commit (D-15).

### Wave 0 Gaps

This phase has NO Wave 0 RED-gate scaffold (which would normally precede coding waves). Plan 12-04 is the equivalent: a desk-side scaffold that creates the directory structure + BENCH-RESULTS.md skeleton that subsequent plans append to.

- [x] `.planning/v1.3-BENCH-RESULTS.md` skeleton — Plan 12-04 creates (D-12)
- [x] `.planning/v1.3/bench-logs/` directory — Plan 12-04 creates
- [x] `.planning/v1.3/scope/` directory — Plan 12-04 creates
- [x] BENCH-RESULTS.md PROTO-01 + PROTO-02 evidence section headers — Plan 12-04 creates (D-09, D-10 column schemas)
- No framework install needed.
- No test files to create.

### Plan-checker Nyquist gate guidance

When `gsd-planner-checker` runs against the produced plans, the Nyquist verification gate should accept **"manual-only verification"** as the strategy for plans 12-01/02/03. The check should verify:
- Each manual-UAT task references the specific log path or scope photo path that constitutes the evidence.
- The acceptance criteria for each task cite the grep target or filesystem check (e.g. "log contains 'All tests passed'", "photo file exists and size > 0").
- The phase gate criteria 1–5 above are reachable from the plan's tasks.

There is no acceptable "automated test that would also work" for hardware-in-the-loop bench validation. Forcing an automated wrapper here would either (a) be a tautological lint of the BENCH-RESULTS.md row format (not load-bearing) or (b) attempt to emulate hardware (out of scope, not feasible).

## Project Constraints (from CLAUDE.md)

The repository CLAUDE.md (`/workspaces/CLAUDE.md`) imposes the following constraints that Phase 12 must honor:

1. **Submodule discipline.** `firestarter_app/` and `firestarter/` are git submodules. The meta-repo tracks only `.planning/` and `.claude/`. **Implication:** Plan 12-04's BENCH-RESULTS.md + bench-logs/ + scope/ all land in `.planning/` (meta-repo). Any new shell wrapper from D-02 fallback (`firestarter_app/tools/bench_cycle.sh`) lives in the firestarter_app submodule and is committed there separately. Commits in `.planning/` do NOT commit submodule pointers unless explicitly intended.

2. **Two-part system contract.** Host CLI (Python) + Arduino firmware (C++). Phase 12 exercises both ends of this via the 250000-baud serial protocol. **Implication:** No new wire-protocol changes; Phase 12 observes the existing INIT → MAIN → END state machine without modifying it.

3. **Constants/flag-bits duplication.** `firestarter_app/firestarter/constants.py` ↔ `firestarter/include/firestarter.h`. **Implication:** Phase 12 makes NO changes to either; it observes existing flag values (`FLAG_FORCE`, `FLAG_VERBOSE`, etc.) on the wire.

4. **Board buffer differences.** Uno = 512-byte buffer; Leonardo = 1024-byte buffer. Affects chunked-transfer sizing in `eprom_operations.py`. **Implication:** When BENCH-RESULTS.md notes board-specific anomalies, executor checks whether the anomaly correlates with buffer size (e.g., a failure at the 512-byte mark on Uno but not Leonardo).

5. **EPROM database authority.** `chip_database.json` is generated; user overrides go in `~/.firestarter/database.json`. **Implication:** Plan 12-04 setup task verifies `~/.firestarter/database.json` either does NOT exist or does not override the three bench chips' `chip_id_value` / `pulse_duration` / `pinout`. If an override exists, the bench evidence is against the override-modified record, not the shipped DB — operator must document this in the BENCH-RESULTS.md `notes` cell.

### firestarter_app/CLAUDE.md additional constraints (verified via system-reminder injection)

6. **Wire JSON schema** (per `firestarter_app/CLAUDE.md` §"Wire Protocol"). The `cmd` field carries operation code, `algorithm` = 7 for bench chips, `vpp_mv` = 12000, `chip-id` = decoded chip_id_value as integer. **Implication:** Phase 12 observation evidence (PROTO-01) confirms the firmware-side handler receives the correct `algorithm: 7` + `chip-id: 55816` (=0xda08 for W27C512) and that the pre-write chip-ID compare uses these values.

7. **WARNING-5 override scope** (per `firestarter_app/CLAUDE.md` §"Database Pipeline"). The 3-predicate override (DIP28_2764 + 0x07 + Flash/EEPROM → 0x0D) is the existing safety net for 5V EEPROMs mis-classified as UV-EPROMs on the DIP28_2764 pinout. **Implication:** All three Phase 12 bench chips have pinout ∈ {DIP28_27512, DIP28_27256} — NOT DIP28_2764 — so the override does not fire for them. They route directly to `configure_eprom` with 12V VPP, which is correct (they are genuine UV-EPROMs that need 12V on the VPP pin).

8. **Known protocols.** `0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39`. **Implication:** All three bench chips are algo 0x07 (in the known set); firmware dispatches to `configure_eprom` handler.

## Sources

### Primary (HIGH confidence — repo file inspection)

- `/workspaces/.planning/phases/12-28-pin-algo-0x07-bench-validation/12-CONTEXT.md` — 234 lines; all 15 locked decisions D-01..D-15.
- `/workspaces/.planning/REQUIREMENTS.md` — BENCH-01/02/05 + PROTO-01/02 wording + traceability table mapping all to Phase 12.
- `/workspaces/.planning/STATE.md` — v1.3 Decisions section + Deferred Items table (Phase 08 SC#2/SC#3 + Phase 09 Plan-05 Task 3 closing via BENCH-01).
- `/workspaces/.planning/ROADMAP.md` — Phase 12 entry with 5 Success Criteria; archived v1.0/v1.1/v1.2 sections.
- `/workspaces/.planning/PROJECT.md` — Current Milestone v1.3 scope + Out of Scope; Key Decisions table.
- `/workspaces/.planning/v1.3-COVERAGE-MATRIX.md` lines 199 (W27C257), 240 (SST27SF512), 246 (W27C512,W27E512) — authoritative chip-id_value + pulse_duration + pinout per chip. Plus §5 BENCH coverage proof tables (lines 1361–1425).
- `/workspaces/.planning/v1.3-defect-coverage-ids.json` — DEFECT-COV-04 + DEFECT-COV-63 (cited as D-01 rationale).
- `/workspaces/firestarter_app/firestarter_test.sh` — 172 lines; the bench-cycle harness verbatim per D-02. Confirmed:
  - Line 31: `JSON_FILE='./firestarter/data/chip_database.json'` (relative path; requires `cd firestarter_app` before invocation)
  - Lines 50–69: `jq` extracts `size_bytes`, `chip_id_check`, `(.electrical.type == "Flash/EEPROM")` for `CAN_ERASE`
  - Lines 80–87: `dd if=/dev/urandom` halves concatenated into `full_data.bin` (fresh-random per cycle; see Pitfall 4)
  - Lines 127–135: firmware/hardware version + config + VPP + VPE tests (D-07 step 2)
  - Lines 139–140: `firestarter id` invocation gated by `HAS_CHIP_ID == true` (D-07 step 3)
  - Lines 146–149: `write`, `verify`, `read`, `colordiff` (D-07 steps 5–7 + colordiff finishes the verify)
  - Lines 155–161: erase + post-cycle blank gated by `CAN_ERASE == true` → UV-EPROMs (all 3 bench chips) skip this branch correctly
- `/workspaces/firestarter_app/write_test.sh` — 127 lines; alternate harness with explicit `null.bin` + `0xFF.bin` + `low_data.bin` + `high_data.bin` + `full_data.bin` patterns. Not invoked by Phase 12; image-generation logic referenced by D-02 note.
- `/workspaces/firestarter_app/firestarter/data/chip_database.json` — verified records for SST27SF512 (line 10607), W27C257 (line 13279), W27C512 (line 13298). All three have `chip_id_check: true`, `algorithm: 7`, `vpp: "12V"`, `vpp_mv: 12000`. Pinout: SST27SF512+W27C512 = DIP28_27512; W27C257 = DIP28_27256.
- `/workspaces/firestarter_app/firestarter/data/pinouts.json` — DIP28_27256 (line 45, `vpp-pin: [1]`) vs DIP28_27512 (line 54, `vpp-pin: [22], oe-pin: [22]`). The probe-point difference for Pitfall 1.
- `/workspaces/firestarter_app/firestarter/messages.py` — line 110 (`MSG_ERR_CHIP_ID_MISMATCH = 0xB9`), line 83 (`MSG_WARN_CHIP_ID_MISMATCH = 0x83`), line 178 (decode format "Chip ID %#04x does not match expected ID %#04x"). The PROTO-01 evidence string.
- `/workspaces/firestarter_app/firestarter/eprom_operations.py` — lines 35–48 (`build_flags`, FLAG_FORCE), lines 618–639 (`check_eprom_id` flow), lines 549–591 (`write_eprom` / `verify_eprom` — no host-side preflight chip-ID compare, confirming the firmware is the safety-stack owner per A7).
- `/workspaces/firestarter_app/firestarter/main.py` lines 593–627 (the `id` command handler — additionally does a `db_instance.search_chip_id(detected_id_value)` reverse-lookup when the firmware-side check fails, useful operator diagnostic).
- `/workspaces/.planning/phases/11-coverage-matrix-db-inconsistency-audit/11-CONTEXT.md` — prior-phase precedent for orchestrator-owns-tracking-writes pattern (D-15) + per-plan commit cadence (D-07 reference in 11-CONTEXT.md).
- `/workspaces/CLAUDE.md` — meta-repo CLAUDE.md; submodule structure + sub-repo development commands.
- `firestarter_app/CLAUDE.md` (via system-reminder injection) — wire protocol JSON shape + database pipeline override semantics.

### Secondary (MEDIUM confidence — derived from primary)

- BENCH cycle expected wall-clock times (5–10 min per chip per board for 64K) — derived from `pulse_duration: "10000 us"` × `size_bytes` for W27C512/W27C257; SST27SF512's `5000 us` shorter. No external citation.
- 12V ±5% tolerance band = 11.4V to 12.6V — derived from the PROTO-02 spec text in REQUIREMENTS.md + standard ±5% interpretation. No external citation.

### Tertiary (LOW confidence — none for this phase)

No web/external sources consulted. Phase 12 is fully internal to the project; the bench-cycle CLI surface and DB records are the entire ground truth.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — every tool (`firestarter`, `firestarter_test.sh`, `jq`, `tee`, `colordiff`, `xxd`, `dd`) verified in-repo or as system-standard. No new dependencies.
- Architecture: HIGH — operator-on-bench tier mapping is direct from CONTEXT.md D-11..D-15; bench-logs / scope directory layout follows D-05 + D-08 schemas verbatim.
- Pitfalls: HIGH — five of six pitfalls verified by direct codepath inspection (harness line numbers, message-ID catalog, pinout JSON); Pitfall 6 carries A7 assumption (medium-low risk).
- Validation Architecture: HIGH — explicitly manual UAT; no automated test infrastructure to map; phase gate criteria 1–5 are all observable in tee'd logs + filesystem.
- Code Examples: HIGH — all commands runnable as-quoted; paths verified to exist or to be plan-creatable.

**Research date:** 2026-05-20
**Valid until:** Phase 13 close (Phase 13 reuses this research's protocols verbatim per CONTEXT.md D-05/D-06/D-07 carry-forward clause). If `firestarter_test.sh` or `chip_database.json` are modified before then, re-verify Sources items marked with line numbers.

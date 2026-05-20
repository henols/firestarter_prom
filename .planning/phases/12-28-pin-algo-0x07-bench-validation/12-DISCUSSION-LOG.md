# Phase 12: 28-Pin / Algo-0x07 Bench Validation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-20
**Phase:** 12-28-pin-algo-0x07-bench-validation
**Mode:** `--auto --chain` (auto-resolved, recommended option selected for every gray area)
**Areas discussed:** BENCH-05 chip selection; Test harness reuse; PROTO-01 chip-ID observation; PROTO-02 VPP scope observation; Bench-cycle order; BENCH-RESULTS schema; Plan structure; Resume / interruption model

---

## BENCH-05 chip selection (D-01)

| Option | Description | Selected |
|--------|-------------|----------|
| W27C257 (WINBOND, 32K, DIP28_27256, 10000 µs) | Same brand as BENCH-01 (W27C512); chip_id_value 0x0000da02; cluster-median pulse width | ✓ |
| W27E257 (WINBOND, 32K, DIP28_27256, 10000 µs) | Shares chip_id_value 0x0000da02 with W27C257 (DEFECT-COV-04) — bench can't disambiguate | |
| SST27SF256 (SST, 32K, DIP28_27256, 5000 µs) | DEFECT-COV-63 already flags pulse-width outlier; conflates failure modes if chosen | |

**Auto-selected:** W27C257 (recommended — WINBOND family scaling evidence; no defect overlap)
**Notes:** Tiebreaker = brand consistency with BENCH-01 (both WINBOND). Reject SST27SF256 because choosing a defect-flagged chip as the density-low rep would conflate "tool/firmware bug" with "chip-data bug" if the cycle fails.

---

## Test harness reuse (D-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse `firestarter_test.sh` verbatim | Existing harness already does full cycle (id/vpp/vpe/blank/write/read/verify/erase); accepts `[EPROM_NAME]` | ✓ |
| Write new per-phase wrapper from scratch | Tailored exactly to D-07 cycle order; minimal coupling to legacy harness | |
| Modify `firestarter_test.sh` | Change existing harness to match D-07 exactly | |

**Auto-selected:** Reuse verbatim
**Notes:** Modifying shared infrastructure is explicitly OUT of scope — historical results anchor on the current behavior. Fallback (thin `tools/bench_cycle.sh` wrapper) only if a chip can't be invoked unmodified.

---

## PROTO-01 chip-ID observation protocol (D-03, D-04)

| Option | Description | Selected |
|--------|-------------|----------|
| CLI stdout/stderr → log file via `tee` | Standard verbose-mode pattern; grep-extractable; reuses existing log breadcrumb format | ✓ |
| Photo of terminal output | Captures display state but not machine-parseable; harder to grep | |
| Custom protocol-capture tool | Would require new CLI surface; deferred | |

**Auto-selected:** CLI → log via `tee`
**Notes:** Operator pastes 5-line snippet (id invocation + response + next command) into BENCH-RESULTS row. Blocked-write evidence for PROTO-01 SC#4 captured once for chosen disambiguation chip (recommended: SST27SF512).

---

## PROTO-02 VPP scope observation protocol (D-05, D-06)

| Option | Description | Selected |
|--------|-------------|----------|
| One annotated scope photo per board minimum | Direct evidence; visible probe point + voltage + time-base; meets SC#5 | ✓ |
| Scope CSV export + plot | Machine-parseable but requires scope-export tooling; format varies per scope | |
| Verbal scope-reading recorded in BENCH-RESULTS | Cheapest but no independent verifiability | |

**Auto-selected:** Annotated scope photo (PNG/JPG) per board
**Notes:** Photo MUST include chip socket VPP pin probe point + scope time-base + voltage scale + caption stating measured Vpp + tolerance. Optional idle-state photo for the off-between-operations evidence. Format flexibility: BMP / SVG / CSV acceptable if voltage + time + probe location are legible.

---

## Bench-cycle order (D-07)

| Option | Description | Selected |
|--------|-------------|----------|
| info → vpp/vpe → id → blank → write → read → verify (post-blank skipped for UV-EPROM) | Matches `firestarter_test.sh` order + honors SC#1 "where electrically erasable" clause | ✓ |
| info → id → write → verify only (skip vpp/vpe and blank-check) | Minimum sufficient for SC#1 functional pass but misses PROTO-02 evidence | |
| Custom per-chip order | Branches by chip capability; harder to compare results across the family | |

**Auto-selected:** Canonical 7-step order with post-blank skipped for algo-0x07
**Notes:** UV-EPROMs cannot be electrically erased — post-cycle blank-check would always fail. Phase 13 inherits this clause unchanged.

---

## BENCH-RESULTS.md row schema (D-08, D-09, D-10)

| Option | Description | Selected |
|--------|-------------|----------|
| Per-chip-per-board row with 14 columns (chip/board/date/info/vpp/chip_id/blank_pre/write/read/verify/blank_post/log/notes) + dedicated PROTO-01/02 evidence rows | Captures every SC and protocol observation; one row per (chip, board) = 6 rows for Phase 12 + 1 PROTO-01 + 2 PROTO-02 rows | ✓ |
| Per-cycle freeform paragraph | Easier to write but harder to scan across chips/boards | |
| Pass/fail boolean per chip only | Too coarse — loses chip-id, VPP, log-snippet evidence | |

**Auto-selected:** 14-column schema + dedicated PROTO rows
**Notes:** Schema is reusable by Phase 13 (same columns; just more rows). Phase 14 DOC-01 aggregates Phase 12 + Phase 13 rows into the final `.planning/v1.3-BENCH-RESULTS.md`.

---

## Plan structure (D-11, D-12, D-13)

| Option | Description | Selected |
|--------|-------------|----------|
| 4 plans: 12-01 BENCH-01 (W27C512), 12-02 BENCH-02 (SST27SF512, + PROTO-01 evidence folded in), 12-03 BENCH-05 (W27C257), 12-04 BENCH-RESULTS scaffold (autonomous, runs first) | One plan = one BENCH-* requirement closure; BENCH-01 first to close heavy deferred items; PROTO-01 folded into BENCH-02 plan since SST27SF512 is the chosen disambiguation target | ✓ |
| Per-board plans (6 plans: each chip × each board) | More granular but doubles plan count; loses "BENCH-* requirement = one plan" mapping | |
| Single mega-plan covering all 3 chips × both boards | Easier to write but harder to track progress; can't checkpoint per BENCH-* requirement | |

**Auto-selected:** 4 plans (3 chip plans + 1 scaffold plan)
**Notes:** Scaffold plan (12-04) is autonomous=true; chip plans (12-01/02/03) are autonomous=false. PROTO-01 blocked-write evidence folded into 12-02 (D-04 + D-13 — keeps plan count at 4, anchors evidence with the SST27SF512 chip).

---

## Resume / interruption model (D-14, D-15)

| Option | Description | Selected |
|--------|-------------|----------|
| All bench plans autonomous=false + per-cycle log file as resume anchor + STATE.md tracking after each chip-plan completes | Mirrors Phase 11 tracking pattern; checkpoint per BENCH-* requirement; operator-controlled cadence | ✓ |
| Autonomous=true with subagent driving the bench (impossible — hardware in the loop) | Not viable — bench requires operator at the socket | |
| Single end-of-phase commit | Loses incremental tracking; bench session interruption loses progress | |

**Auto-selected:** autonomous=false + per-cycle log + per-plan STATE/ROADMAP tracking
**Notes:** Same orchestrator-owns-tracking-writes pattern as Phase 11.

---

## Claude's Discretion

- Exact scope photo file format and resolution — PNG/JPG recommended, BMP/SVG/CSV acceptable if legible.
- Date encoding in artifact filenames — ISO `2026-05-20` recommended for sortability; local conventions OK if consistent.
- Order of `vpp -t 5` vs `vpe -t 5` — either works; `vpp` first recommended since PROTO-02 targets VPP rail.
- Whether to capture `firestarter fw` + `hw` version row per cycle or once per phase — accept the harness's per-cycle redundancy.

## Deferred Ideas

- Phase 13 chips (BENCH-03/04/06) — own CONTEXT.md
- CI wiring of `firestarter_test.sh` — needs hardware-in-the-loop runner
- BENCH-RESULTS final aggregation — Phase 14 / DOC-01
- DEFECT-COV-XX investigations — route to v1.4
- SST27SF256 as BENCH-05 — revisit in v1.4 after DEFECT-COV-63 investigation
- W27E257 as BENCH-05 — revisit if WINBOND coverage needs a second 32K chip
- Modifying `firestarter_test.sh` — out of scope (shared infrastructure)

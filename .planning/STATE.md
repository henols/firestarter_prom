---
gsd_state_version: 1.0
milestone: v1.17
milestone_name: — Implement & Test the W29C040 Programming Protocol
status: executing
last_updated: "2026-06-26T22:45:00.000Z"
last_activity: 2026-06-26 -- Phase 93 Plan 01 complete (SAFE-01 pre-flight + T-93-CANERASE finding)
progress:
  total_phases: 4
  completed_phases: 0
  total_plans: 4
  completed_plans: 1
  percent: 25
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-06-26

## Current Position

Phase: 93 (rca-root-cause-the-w29c040-page-0-write-fault) — EXECUTING
Plan: 2 of 4 (Plan 01 complete)
Status: Executing Phase 93 — Plan 02 next (bench-gated: hardware required)
Last activity: 2026-06-26 -- Phase 93 Plan 01 complete (SAFE-01 pre-flight + T-93-CANERASE finding)

## Project Reference

See: `.planning/PROJECT.md` (v1.17 Current Milestone section + Key Decisions)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware handler. v1.17 proves that contract on the W29C040 flash4 (`0x05`) write path: root-cause the page-0 write fault, make flash4 page sizing datasheet-sourced per-chip (CR-01), and bench-prove byte-exact write→read→verify on real silicon.

**Current focus:** Phase 93 — rca-root-cause-the-w29c040-page-0-write-fault

## Milestone Context (v1.17)

- **Scope (operator-confirmed 2026-06-26):** widest — W29C040 RCA + fix **and** generalize CR-01 (datasheet-sourced per-chip `page_size` DB field).
- **Branch base:** firmware forks off the **v1.16 tip `a296195`** (primitives recompose), NOT firmware `beta` (stale at v1.13 `a1953c2`). Mirrors v1.15/v1.16 precedent; gitlinks PINNED at b10; lockstep beta cut operator-gated. Meta `.planning/` proceeds per convention.
- **Done bar:** byte-exact write→auto-erase→program→verify SHA on the seated W29C040 (Leonardo + Rev 2.0). Hard graduation gate — no best-effort fallback authorized.
- **Bench LOCKED to Leonardo + RURP Rev 2.0.** Standing discipline: live R1/R2 readback each task, verify `controller:` port identity per task, Leonardo chip-OUT-sideload-exempt. Operator seats the W29C040 so the bench can be driven unattended.
- **Dual-repo lockstep** (`constants.py` ↔ `firestarter.h`) if `page_size` crosses the wire; reuse-first; py3.12-masks-CI-3.11 ruff/codegen trap watch.
- Phase numbering continues from v1.16's Phase 92 → **v1.17 starts at Phase 93**.
- Closes **CR-01 / Phase-74 Wave-2** (W29C040 flash4 256 B page-0 fault; open since v1.13, confirmed not-silicon-effective at v1.15 Phase 82/84).

## Roadmap Summary (v1.17 — Phases 93–96)

Created 2026-06-26 · granularity Comprehensive · 16/16 requirements mapped (no orphans, no duplicates). Strict sequence: **RCA → FIX+PGSZ → BENCH → LEDGER**. SAFE-01 homes in Phase 93, SAFE-02 in Phase 94; both recur as preconditions through close.

| Phase | Goal | Requirements | Bench-gated |
|-------|------|--------------|-------------|
| 93 — RCA | Reproduce + differentially isolate + name the W29C040 page-0 write-fault root cause | RCA-01, RCA-02, RCA-03, SAFE-01 | yes (Leonardo + Rev 2.0, seated W29C040) |
| 94 — FIX + PGSZ | Fix flash4 write path (traces/guard green) + datasheet-sourced per-chip `page_size` over the wire (CR-01) | FIX-01/02/03, PGSZ-01/02/03, SAFE-02 | no (native + host CI) |
| 95 — BENCH | Byte-exact write→auto-erase→program→verify (SHA) graduation gate + W29C020 sibling regression + EVIDENCE | BENCH-01, BENCH-02, BENCH-03 | yes (hard graduation gate, no fallback) |
| 96 (close) — LEDGER | PROTOCOL-LEDGER → W29C040 PASS/`supported`, close CR-01/Phase-74 Wave-2, `check_ledger.py` green, milestone close | LEDGER-01, LEDGER-02 | no |

**Dependency chain:** 93 → 94 → 95 → 96 (linear; RCA must name the cause before FIX is designable; BENCH gates on the committed fix + `page_size`; LEDGER records the bench PASS).

**Firmware/host surfaces:** `firestarter/src/proms/flash_type_4.cpp` (fix, on the `a296195` recompose) + flash4 golden traces/dispatch-mirror guard (keep green); host `build_db.py` / `chip_database.json` / `constants.py` ↔ `firestarter.h` (per-chip `page_size` lockstep field); `check_dispatch.py` / `diff_db.py` / `check_ledger.py` gates.

## Accumulated Context

### Deferred Items (carry-forward at v1.16 close — 2026-06-26)

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| FUT-01 (v1.14) | X88C64 0x34 graduation | deferred — PCB-blocked | A6 ALE-routing PCB-BLOCKED (HIGH); stays `protocol-not-implemented`. |
| FUT-03 (v1.15) | 2516 0x0B read instability + write proof | deferred best-effort (D-22) | 3 distinct SHAs after VPP-skip; shared OE/VPP pin. |
| FUT-04 (v1.14) | AT28C04/16 adapter graduation | deferred — adapter not built | 9 chips stay `adapter-required`. |
| FUT-05 (v1.15) | REWR-02 0x08 write proof | deferred — no functional 0x08 chip | W27E040 stuck-bit; need sibling 0x08 rewritable chip. |
| FUT-06 (v1.15) | AM27C020 0x08 32-pin write/VPP path | deferred — RCA'd, not trivially fixable | 0-bits-programmed; needs 0x08 32-pin Large EPROM write/VPP root-cause. |
| **CR-01 / Phase-74 Wave-2** | **W29C040 flash4 256 B page-0 write fault** | **ACTIVE — v1.17 target** | Phase-74 fix not silicon-effective; page size already correct (256 B) → deeper RCA. **This milestone.** |
| release-gate | Lockstep beta cut `3.0.0b11` + gitlink bump | OPERATOR-GATED | Standing v1.11–v1.16 policy; gitlinks PINNED at b10. |
| uat_gap | Phase 85 — 85-HUMAN-UAT.md (2 pending scenarios) | partial | v1.16 carry-forward. |

### v1.9 DEFERRED (operator 2026-06-08 — resumes later at Phase 45)

v1.9 (Read-Bug RCA + Fix) is paused. Phase 44 (Bug A RCA) complete; remaining Phases 45–48. The v1.17 bench oracle is pinned to Leonardo + Rev 2.0 precisely to avoid the v1.9 shield-fleet read bug.

### v1.10 Substrate (carry-forward)

Transport provably byte-exact (COBS `0x00` + CRC8-CCITT) — settled variable. GATE-1.8d ring-fence intact.

### v1.16 Substrate (carry-forward, directly relevant to v1.17)

- **flash4 lives on the primitives recompose** (`a296195`): `flash_type_4.cpp` uses P7/P4/P3/P5 shared primitives; `flash4_page_size(mem_size)` capacity heuristic still in place (the CR-01 target).
- **PROTOCOL-LEDGER** at `.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}` + `check_ledger.py`; W29C040 0x05 carried as an open defect (CR-01). v1.17 must update this on bench PASS.
- **Golden register traces + dispatch-mirror guard** pinned for flash4 (Phase 88-03, 206-entry write trace) — the recompose oracle the W29C040 fix must keep green.
- **datasheets/** folder exists in the firestarter sub-repo; no W29C040 datasheet committed yet (Phase 85 bot-blocked some). May need acquisition for the datasheet-sourced `page_size`.

### Pending Todos (carried forward)

- `flash4-page-size-datasheet-sourced-cr01.md` (medium) — **directly resolved by v1.17** (datasheet-sourced per-chip `page_size`).
- `avrdude-mcu-detection-fallback.md` (low) — out of scope, carry forward.
- `cobs-decoder-framelevel-deadline-wr01.md` (medium) — v1.10 COBS follow-up; deferred.
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` (firmware) — carry forward.
- `large-read-data-jitter-uno328pb.md` (HIGH, v1.8-seed) — v1.9 RCA target.
- `photograph-modified-rev-0.md` (medium) — carry forward.

### Decisions (v1.17)

- **T-93-CANERASE (Phase 93 Plan 01, 2026-06-26):** FLAG_CAN_ERASE (0x02) IS set in W29C040 wire flags — `flash4_erase_execute` asserts 12V on a 5V-only chip. Bench plans 02–04 MUST use `--skip-erase`. Phase 94 FIX-01 scope: prevent FLAG_CAN_ERASE from reaching `flash4_erase_execute` for protocol 0x05 chips.
- **Phase-74 traps ruled out (Phase 93 Plan 01, 2026-06-26):** SDP present and 256B page confirmed by native tests (11/11 PASS). RCA must search deeper than Phase-74 hypotheses.

### Blockers / Concerns

- **T-93-CANERASE (HIGH):** W29C040 wire flags=0x02 causes 12V erase on a 5V chip during any `firestarter write` without `--skip-erase`. This is a latent hardware-damage path that was previously believed non-existent. Bench mitigation: always use `--skip-erase` for W29C040 in RCA Plans 02–04. Permanent fix: Phase 94 FIX-01.
- Hardware-gated: Plans 02–04 require operator to seat W29C040 on Leonardo + Rev 2.0.

## Operator Next Steps

- Plan 01 complete (autonomous, no hardware). SAFE-01 pre-flight done.
- **CRITICAL: W29C040 write commands MUST use `--skip-erase` flag** (T-93-CANERASE — flags=0x02 routes 12V erase on 5V chip).
- Next: Plan 02 (93-02) — bench repro of signature + post-fail read. Operator seats W29C040 on Leonardo + Rev 2.0; verify controller identity + R1/R2 readback before proceeding.

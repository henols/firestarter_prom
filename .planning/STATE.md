---
gsd_state_version: 1.0
milestone: v1.16
milestone_name: — Protocol-First Architecture Rebuild
status: executing
stopped_at: Phase 85 Plan 03 complete — datasheets/README.md + phase-gate PASS (DSHEET-03)
last_updated: "2026-06-25T17:18:52.843Z"
last_activity: 2026-06-25 -- Phase 86 planning complete
progress:
  total_phases: 6
  completed_phases: 1
  total_plans: 7
  completed_plans: 3
  percent: 17
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-06-25

## Current Position

Phase: 86 (NEW — infoic.xml Variant-Field Decode + Correct DB Regen)
Plan: Not started (context gathered)
Status: Ready to execute
Last activity: 2026-06-25 -- Phase 86 planning complete

Progress: [█░░░░░░░░░] 17%

> **Scope amendment 2026-06-25:** Mid-discussion the operator pivoted v1.16 from a
> pure behavior-preserving refactor to *fix the DB at its root* — decode the
> `infoic.xml` `variant` field fully and delete the `build_db.py` Rule 1/2/3 override
> edge-cases. New Phase 86 inserted (host-only); Naming→87, Golden Traces→88,
> Recompose→89, Bench Ledger→90. See `.planning/phases/86-variant-decode-correct-db-regen/86-CONTEXT.md`.

## Quick Tasks Completed

| ID | Task | Date | Status | Commit |
|----|------|------|--------|--------|
| 260625-f1g | Group dev write-cycle/consistency-check run folders under `firestarter-runs/` (was dumping in launch dir) | 2026-06-25 | complete ✓ | firestarter_app@bc55b29 |

## Project Reference

See: `.planning/PROJECT.md` (v1.16 Current Milestone section + Key Decisions)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware handler. v1.16 makes that contract **legible** (named, datasheet-documented protocols) and **leaner** (shared-primitive handlers). Minipro DB stays ground truth; datasheets verify + document the *why*.

**Current focus:** Phase 86 — naming-+-documentation-pass (Phase 85 complete — 18 datasheets committed incl. operator-added W27C020)

## Roadmap Summary

**v1.16 ACTIVE — 5 phases (85–89), 23/23 requirements mapped. Dependency-first ordering:**

- **Phase 85: Datasheet Acquisition** (DSHEET-01/02/03, SAFE-05) — No code; commit datasheet PDFs for 11 on-hand chips + 1 representative per 6 no-silicon buckets; author `datasheets/README.md` index. Unblocks naming pass.

- **Phase 86: Naming + Documentation Pass** (NAME-01/02/03/04/05, SAFE-03, SAFE-06) — Author 12-bucket protocol vocabulary (hex → human name → datasheet-verified behavior), enumerate 8 one-off invariants as named behavior-contract items, apply FM1608 0x40→0x28 + 0x34 UV-EPROM→EEPROM decode corrections. Dispatch structure byte-identical; near-zero flash delta.

- **Phase 87: Golden Traces + Dispatch-Mirror Guard** (PRIM-01, SAFE-01, SAFE-02, SAFE-04) — Pin per-family native register golden traces and add the dispatch-mirror invariant test before any extraction. Establishes the recompose oracle.

- **Phase 88: Incremental Primitive Recompose** (PRIM-02/03/04/05/06, SAFE-01/02/03 recurring) — P7 SDP-table dedup (warm-up ~40–80 B) → P4 chip-ID compare/report (~250–350 B) → P3 VPP gate (~350–450 B, biggest) → P5 poll (~200–300 B). Each step guarded by native suites + `check_dispatch.py` + `diff_db.py`; `pio run -e leonardo` net-non-increase gate; achieved flash % reported.

- **Phase 89: Bench Validation + PROTOCOL-LEDGER** (LEDGER-01/02/03, SAFE-04 recurring) — Bench-prove on-hand protocols (0x05/W29C020, 0x06/SST39SF040, 0x07/W27C512, 0x28/FM1608) on Leonardo + Rev 2.0; author `PROTOCOL-LEDGER.{md,json}` composing with v1.13 matrix + v1.15 EVIDENCE; 6 no-silicon buckets explicit UNVERIFIED.

**Build order (dependency-first, safety-load-bearing):** 85 → 86 → 87 → 88 → 89. Cannot safely recompose a family before its behavior contract is written (Phase 86) and its golden trace pinned (Phase 87). Flash curve trends down monotonically during Phase 88 (P7→P4→P3→P5 order).

**Cross-cutting safety (SAFE-01..06):** SAFE-01 (protocol-key, not electrical.type) homed in Phase 87, recurring in 88. SAFE-02 (one-off invariants survive recompose) homed in Phase 87, recurring in 88. SAFE-03 (check_dispatch.py 0 violations + diff_db.py empty every phase) homed in Phase 86 (naming applies NAME-04 corrections; baseline re-pinned for those), recurring in 87/88/89. SAFE-04 (over-voltage blocked, host guard never bypassed) homed in Phase 87, recurring in 88/89. SAFE-05 (no new 3rd-party deps; only new artifact is `datasheets/`) homed in Phase 85. SAFE-06 (firmware-first, no lockstep, CI target py3.11 not 3.12 devcontainer) homed in Phase 86.

## Accumulated Context

### Roadmap Evolution

- v1.16 roadmap created 2026-06-25: 5 phases (85–89) derived from the 23 v1.16 requirements
  (DSHEET/NAME/PRIM/LEDGER/SAFE) along the research-locked dependency-first spine (datasheets →
  vocabulary/invariants → golden-trace guards → recompose → bench ledger). 23/23 mapped, no
  orphans/duplicates (Phase 85: 4 reqs · Phase 86: 7 · Phase 87: 4 · Phase 88: 8 · Phase 89: 4;
  SAFE-01/02/03/04 cross-cutting, homed in earliest establishing phase and recurring as
  preconditions in later phases). PRIM-02..05 consolidated into Phase 88 as sub-plans (the
  4 extraction steps are closely coupled under the same gate discipline; fine-grained splits
  would create thin phases with implementation-task criteria rather than observable outcomes).
  At Comprehensive granularity, 5 phases matches the natural delivery boundaries (acquisition →
  vocabulary → oracle → refactor → validation). Research convergence: HIGH confidence on all
  four research dimensions (STACK/FEATURES/ARCHITECTURE/PITFALLS).

- v1.15 roadmap created 2026-06-23: 4 phases (81–84); shipped 2026-06-25.
- v1.14 roadmap created 2026-06-18: 4 phases (77–80); shipped 2026-06-23.

### v1.16 Scope Notes (research 2026-06-25, HIGH confidence)

- **Firmware-only / host-untouched.** No dual-repo lockstep for the refactor (wire/constant values
  unchanged). NAME-04 decode corrections (FM1608 0x40→0x28 reconciliation + 0x34 UV-EPROM→EEPROM)
  are host-only DB fixes applied in Phase 86; `diff_db.py` shows only those 2 intentional changes.

- **Flash outcome = best-effort measured, not a hard gate.** Per-step `pio run -e leonardo`
  net-non-increase gate + report achieved %; no hard ≤86.5% floor.

- **Pure behavior-preserving refactor.** CR-01 (W29C040 flash4), FUT-06 (AM27C020 0x08), FUT-03
  (2516 0x0B read) preserved as-is; not fixed this milestone.

- **12 live protocol buckets** in chip_database.json (744 chips): 0x05/06/07/08/0B/0D/0E/10/27/28/29/34.
  No 0x40 — FM1608 is decimal 40 = 0x28 (SRAM_STD/FRAM). Phantom 0x35/0x39 = zero DB chips
  (document as "dispatched-but-dead"). Infeasible 0x11/0x2A/0x2B/0x2C = fail-closed.

- **Realistically recoverable: ~850–1,300 B** via P3 VPP gate (~350–450 B) + P4 chip-ID
  (~250–350 B) + P5 poll (~200–300 B) + P7 tables (~40–80 B) → 89.5% → ~85–86.5%.

### ⏸ v1.9 DEFERRED (operator 2026-06-08 — resumes later at Phase 45)

v1.9 (Read-Bug RCA + Fix) is paused. Phase 44 (Bug A RCA) complete. Remaining: Phases 45–48. The
v1.16 bench oracle is pinned to Leonardo + Rev 2.0 precisely to avoid the v1.9 shield-fleet read bug.

### v1.10 Substrate (carry-forward)

Transport provably byte-exact (COBS `0x00` + CRC8-CCITT) — settled variable. GATE-1.8d ring-fence intact.

### Pending Todos (carried forward)

- `avrdude-mcu-detection-fallback.md` (low) — out of scope, carry forward
- `cobs-decoder-framelevel-deadline-wr01.md` (medium) — v1.10 COBS follow-up; deferred
- `large-read-data-jitter-uno328pb.md` (HIGH, v1.8-seed) — v1.9 RCA target
- `gather-protocol-datasheets.md` — feeds v1.16 Phase 85 directly

### Blockers / Concerns

None at roadmap start. v1.16 is a firmware-only refactor with no hardware dependencies except the
Phase 88 bench re-prove steps (W27C512 + W29C020 write paths on Leonardo + Rev 2.0) and the Phase 89
bench-validation session. Primary risk: abstraction overhead increases flash rather than shrinks it
on AVR — mitigated by the per-step net-non-increase measurement gate. Watch the py3.12-masks-CI-3.11
ruff/codegen drift trap for any host-side NAME-04 corrections in Phase 86.

## Session Continuity

Last session: 2026-06-25T15:00:00.000Z
Stopped at: Phase 85 Plan 03 complete — datasheets/README.md + phase-gate PASS (DSHEET-03)
Resume: Phase 86 (naming pass) — `/gsd-execute-phase 86`

## Decisions

- [Phase 79-02, 2026-06-23]: NMOS-02 executed under CONTEXT D-07 operator override. VPE = 22.4V DMM / 23.9V fw; ceiling 22000→25000; 4 NMOS chips graduated `vpp-exceeds-max`→`supported` (0x0B, 25000mV). Best-effort, no HW change ever. FUT-02 (>25V fail-closed) preserved.
- [Phase 82, 2026-06-24]: Rewritable silicon validation: 5 PASS / 3 FAIL (W27E512/W27E040 stuck-bit silicon wear; W29C040 flash4 256B page-0 fault confirming Phase-74 fix not silicon-effective → CR-01). W29C020 auto-erase = first Flash/EEPROM auto-erase silicon proof.
- [Phase 84-05, 2026-06-25]: FIX-01 closed by disposition D-43; GRAD-03/FUT-03 deferred best-effort D-22; 2516 read still unstable after VPP-skip.
- [Phase 85-01, 2026-06-25]: v1.16-protocol-first-architecture-rebuild branch forked from beta (not v1.15 tip) in firestarter sub-repo; datasheets-check.sh Wave-0 gate authored with 12-bucket %PDF contract (correctly RED at scaffold stage, PASS after Plans 02/03 populate the tree).
- [Phase 85-02, 2026-06-25]: 17 datasheets committed; W27E512→0x07, FM1608→0x28 (DB-verified); 3 D-02 fallbacks: SST27SF512/W27E040/DS1250Y bot-blocked; SAFE-05 intact
- [Phase 85-03, 2026-06-25]: datasheets/README.md authored (DSHEET-03); 12-bucket index + 6 exclusions + D-02/D-03 policy; phase-gate PASS (exit 0); SAFE-05 intact
- [Phase 86 discuss, 2026-06-25]: MILESTONE RESTRUCTURED. Grounded in raw infoic.xml that FM1608=type4/proto0x07/variant0x4126 and X88C64=type1/proto0x34/variant0x3100/flags0x00414200 (flags&0x10==0 → why its type is mis-decoded). Operator pivoted: decode the variant field fully (incl. undecoded high byte) + delete build_db.py Rule1/2/3 → correct DB. Inserted new Phase 86 (host-only variant decode); renumbered 86→90; added VAR-01..04 (27 reqs). Decisions: full override deletion (check_dispatch 0-violations = structural backstop), every diff_db row explained + re-pin baseline, on-hand bench chips unchanged-or-rebenched.

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| 85 | 01 | 4min | Wave-0 scaffold: branch fork + datasheets-check.sh |
| 85 | 02 | 8min | 17 PDFs downloaded and committed (DSHEET-01/02) |
| 85 | 03 | 5min | README.md authored + phase-gate PASS (DSHEET-03) |

## Deferred Items

**Re-acknowledged at v1.15 milestone close (2026-06-25):** all prior open items are pre-existing carry-forwards or intentional v1.15 deferrals. See full table in the v1.15 STATE.md snapshot or `.planning/milestones/v1.15-MILESTONE-AUDIT.md`.

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| FUT-01 (v1.14) | X88C64 0x34 graduation | deferred — PCB-blocked | A6 ALE-routing PCB-BLOCKED (HIGH); stays `protocol-not-implemented`. |
| FUT-03 (v1.15) | 2516 0x0B read instability + write proof | deferred best-effort (D-22) | 3 distinct SHAs after VPP-skip; shared OE/VPP pin; FUT-03. |
| FUT-04 (v1.14) | AT28C04/16 adapter graduation | deferred — adapter not built | 9 chips stay `adapter-required`; ADPT-01/02/03. |
| FUT-05 (v1.15) | REWR-02 0x08 write proof | deferred — no functional 0x08 chip | W27E040 stuck-bit; need sibling 0x08 rewritable chip. |
| CR-01 / Phase-74 Wave-2 | W29C040 flash4 256B page-write fault | open — reopened by Phase 84 | Phase-74 fix not silicon-effective. Reopen Phase-74 Wave-2 (likely dual-repo lockstep firmware fix). |
| FUT-06 (v1.15) | AM27C020 0x08 32-pin write/VPP path | deferred — RCA'd, not trivially fixable | 0-bits-programmed; requires 0x08 32-pin Large EPROM write/VPP root-cause. |
| release-gate | Lockstep beta cut `3.0.0b11` + gitlink bump | OPERATOR-GATED | Standing v1.11–v1.15 policy; gitlinks PINNED. |

## Operator Next Steps

- Plan the new Phase 86 (variant decode): `/gsd-plan-phase 86`
  - Recommend running with research (the variant high-byte decode needs minipro `database.c` + datasheet grounding).

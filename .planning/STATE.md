---
gsd_state_version: 1.0
milestone: v1.9
milestone_name: — Read-Bug RCA + Fix
status: planning
stopped_at: Phase 44 context gathered
last_updated: "2026-05-29T12:25:30.341Z"
last_activity: 2026-05-29 — v1.9 roadmap created; Phase 44 ready to plan
progress:
  total_phases: 5
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-05-29

## Current Position

Phase: 44 of 5 v1.9 phases (Phase 44 — Bug A RCA: Modified Rev 0 Upper-Address Jitter)
Plan: —
Status: Ready to plan
Last activity: 2026-05-29 — v1.9 roadmap created; Phase 44 ready to plan

Progress: [░░░░░░░░░░] 0%

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-29)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** Phase 44 — Bug A RCA (Modified Rev 0 upper-address jitter)

## Roadmap Summary

**v1.9 phases:** 5 (numbered 44-48, continues from v1.8 last phase 43). Granularity: Comprehensive. Hardware-gated — firmware sub-repo work expected from Phase 46 onward.

**Standing context:** GATE-1.8d ring-fence intact — 15 N=5 W27C512 baseline binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` remain valid; `_read_and_parse_lines` body byte-identical pre/post v1.8.

| Phase | Goal | Requirements |
|-------|------|--------------|
| 44. Bug A RCA — Modified Rev 0 | Prove the Modified Rev 0 A15=1 jitter to a definitive signal-integrity mechanism via scope traces; start per-rev failure map | RCA-01, RCA-03 (partial) |
| 45. Bug B RCA — Rev 2.0 | Prove the Rev 2.0 /CE-/OE timing + VPP=13.1V failure to a definitive root cause; complete the per-rev failure map | RCA-02, RCA-03 |
| 46. Fix Design & A/B Bench Trials | Design and A/B-test firmware fix candidates for Bug A and Bug B across the shield fleet; regression-check Rev 2.2 | FIX-01, FIX-02, FIX-03 |
| 47. Acceptance Gate + Backlog Closures | Re-run Phase 29 N≥5 byte-identical acceptance gate with fix applied; close VERIFY-01/03/04 v1.6 backlog | VERIFY-A, VERIFY-01, VERIFY-03, VERIFY-04 |
| 48. COBS Evaluation + Cleanup + Close | Evaluate COBS framing (adopt/defer/reject); lift eprom_operations.py mypy strict overrides; milestone close + branch promotion | COBS-01, TYPE-01 |

**Coverage:** 12/12 v1.9 requirements mapped to exactly one phase. No orphans, no duplicates.

Full details: `.planning/ROADMAP.md` (v1.9 section).

## Accumulated Context

### Key Substrate (consumed by Phase 44)

- Bug A evidence: `.planning/v1.6-EVIDENCE.md` Phase 29 v2 H3 block — Modified Rev 0, WORST=1.86× skew, 63% bit-raise, A15=1 address lines.
- Bug B evidence: same file — Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch + VPP=13.1V.
- Baseline binaries: `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` (15 files, N=5 each).
- Phase 29 summary: `.planning/milestones/v1.6-phases/29-multi-board-bench-verification/29-04-SUMMARY.md`.
- Shield-rev docs: `.planning/v1.7-SHIELD-REVS.md` (per-rev capability table + ADC-band detect plumbing).
- v1.8 cleanup: `eprom_operations.py` mypy strict deferred per D-07; `# DO NOT MODIFY — v1.9 RCA territory` marker on `_read_and_parse_lines`.

### Pending Todos (carried from v1.8)

- `large-read-data-jitter-uno328pb.md` (HIGH) — primary v1.9 target; Bug A + Bug B RCA seed.
- `serial-cobs-resync-data-path.md` (medium) — COBS-01 evaluation in Phase 48.
- `avrdude-mcu-detection-fallback.md` (low) — out of v1.9 scope, carry forward.
- `w27c512-eeprom-misclassification.md` (HIGH) — DB content fix, out of v1.9 scope.

### Blockers / Concerns

- **Hardware-gated from Phase 44 onward.** All RCA/FIX/VERIFY phases require operator bench authorization and shield swaps. Per `feedback_verify_port_identity_each_task`: verify controller identity per port at each bench task start. Per `user_shield_revisions`: ask which silkscreen rev is on bench before each session.
- **Firmware sub-repo work expected in Phase 46.** Branch model: cut `v1.9-read-bug-rca` in all 3 repos (meta off `main`, sub-repos off current `beta` tips) per `feedback_branching`.
- **TYPE-01 gated on Phase 46.** The `eprom_operations.py` mypy ring-fence (GATE-1.8d) cannot be lifted until the read path is fixed. Do not attempt TYPE-01 before Phase 46 ships.

## Session Continuity

Last session: 2026-05-29T12:25:30.337Z
Stopped at: Phase 44 context gathered
Resume file: .planning/phases/44-bug-a-rca-modified-rev-0-upper-address-jitter/44-CONTEXT.md

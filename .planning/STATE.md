---
gsd_state_version: 1.0
milestone: v1.12
milestone_name: — Firmware Protocol Dispatch Hardening + Skeletons
status: executing
stopped_at: Phase 62 Plan 01 complete
last_updated: "2026-06-10T14:55:54.958Z"
last_activity: 2026-06-10
progress:
  total_phases: 12
  completed_phases: 1
  total_plans: 11
  completed_plans: 7
  percent: 8
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-06-10

## Current Position

Phase: 62 (dispatch-baseline-capture-check-dispatch-update) — EXECUTING
Plan: 2 of 3
Status: Ready to execute
Last activity: 2026-06-10

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-10 for v1.12)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** Phase 62 — dispatch-baseline-capture-check-dispatch-update
dispatch eliminating the silent VPP-hazard `mem_type` fallback path; new
`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` wire response (lockstep dual-repo); host
`ProtocolNotImplementedError` + clear CLI message; capability-honest DB inclusion
(`support_status` taxonomy: `protocol-not-implemented` / `adapter-required` / `vpp-exceeds-max`;
true NMOS VPP correction for M2716/M2732/M2732A; principled pinout engineering for currently-unclassifiable DIP chips;
host `info`/`write`/`read`/`verify` status-specific capability guard).
First firmware-touching milestone since v1.10. Phases 62–68, no bench required.

## Roadmap Summary

**v1.12 ACTIVE — 7 phases (62–68):**

- Phase 62: Dispatch Baseline Capture + check_dispatch Update (GATE-01, GATE-02)
- Phase 63: Catalog Lockstep Wire Change (WIRE-01)
- Phase 64: Firmware Fail-Closed Dispatch + Native Tests (DISP-01..04, WIRE-02, TEST-01, TEST-02)
- Phase 65: Host Graceful Handling (HOST-01, HOST-02)
- Phase 66: DB Inclusion + VPP Correction + Dispatch Gate (DB-01, DB-03, DB-05)
- Phase 67: Pinout Classification for Unclassifiable DIP Chips (DB-02)
- Phase 68: Host Capability Reporting (DB-04)

**v1.11 SHIPPED 2026-06-10:** 6 phases (56–61), 14 plans, 15/15 requirements. HOST-ONLY
decode-correctness milestone (firmware untouched like v1.8). Authoritative field dictionary +
minipro-source-grounded decode, 4 decode bugs fixed, principled `resolve_pinout_key`, 9 × 24-pin
EEPROMs unblocked host-only, full-class VPP-safety + per-chip diff gates, display layer reflects
`electrical.type`. Audit PASSED 15/15. Beta-only; lockstep `3.0.0b9` cut + stable operator-gated.
Archive: `.planning/milestones/v1.11-ROADMAP.md`.

**v1.10 SHIPPED 2026-06-07:** 7 phases (49–55), 27 plans, 14/14 requirements. Provably
byte-exact serial transport (COBS `0x00` + CRC8). Beta-only; stable `3.0.1` operator-gated.
Archive: `.planning/milestones/v1.10-ROADMAP.md`.

**v1.9 Read-Bug RCA + Fix — DEFERRED (operator 2026-06-08):** Phases 45–48 remain.
Resumes at Phase 45 when the operator picks it back up.

## Accumulated Context

### v1.12 Scope Lock (2026-06-10)

Research finding: the SKELETON-NEEDED bucket is **empty**. Every RURP-feasible DIP-parallel-memory
`protocol_id` is already handled (all 743 DB chips covered by 13 protocols). The unimplemented
protocol_ids (`0x11` FWH, `0x2A`/`0x2B`/`0x2C` GAL/PLD, etc.) are all infeasible on RURP.

The milestone's real value is the **fail-closed safety framework + honest reporting**:

1. The silent `mem_type` fallback hazard: `protocol != 0` + `mem_type=1` silently routes to
   `configure_eprom` → 12V VPP on potentially 5V-only chips. Eliminated by the `protocol != 0`
   guard in `configure_memory()`.

2. New `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` (lockstep dual-repo codegen via `messages.toml`).
3. `configure_not_implemented()` catch-all: zero hardware side effects; emits the new message ID.
4. Named infeasibility arms for `0x11`/`0x2A`/`0x2B`/`0x2C` (documents hardware reason in-code).
5. Host `ProtocolNotImplementedError(EpromOperationError)` + clear CLI message with protocol value.

**Branch model:** `v1.12-protocol-dispatch-hardening` off `beta` in all 3 repos; merge back to
`beta`; `beta`→stable operator-gated. Deferred v1.11 host work must reconcile into
`firestarter_app/beta` before v1.12 host changes commit.

**Critical ordering constraints (from research + pitfalls):**

1. Phase 62 GATE first — baseline + `check_dispatch.py` update BEFORE any firmware change
2. Phase 63 WIRE second — catalog message ID in both repos BEFORE firmware emits it
3. Phase 64 FIRMWARE third — guard + not_implemented handler + native tests
4. Phase 65 HOST last — `ProtocolNotImplementedError` + CLI message

**Key pitfalls to remember:**

- Codegen MUST use Python 3.11 (CI target), not the devcontainer's 3.12 — py3.12/3.11 drift trap
- `messages.toml` edit in meta-repo ONLY; sync to both sub-repos via `sync_to_subrepos.sh`
- `check_dispatch.py` updated BEFORE firmware changes (currently has 0x35/0x39 gap)
- Skeleton handlers: NEVER assign operation pointers, NEVER call hardware functions
- Flash gate: Leonardo must stay ≤ 90% after Phase 64

**Flash budget at v1.12 start (from v1.11 close):**

- Leonardo: 88.4% (25,354 B / 28,672 B) — 3,318 B remaining
- Uno: 72.0% (23,216 B / 32,256 B) — 9,040 B remaining

### ⏸ v1.9 DEFERRED (operator 2026-06-08 — "skip that bug for now"; resumes later at Phase 45)

v1.9 (Read-Bug RCA + Fix) is paused — deferred by operator decision after v1.10 shipped.
Phase 44 (Bug A RCA) complete; Phase 48 plan 48-01 (COBS verdict) complete.
Remaining: Phases 45–48. Resume: `/gsd-plan-phase 45`.

### v1.10 Substrate (carry-forward)

- Transport provably byte-exact (COBS `0x00` + CRC8-CCITT). Settled variable for v1.9 RCA.
- uno328pb read instability persists (transport-exonerated; RCA deferred to v1.9 Phase 45+).
- GATE-1.8d ring-fence: `_read_and_parse_lines` body byte-identical; 15 N=5 W27C512 baseline
  binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` valid.

### Pending Todos (carried forward from v1.11)

- `avrdude-mcu-detection-fallback.md` (low) — out of scope, carry forward
- `cobs-decoder-framelevel-deadline-wr01.md` (medium) — v1.10 COBS follow-up; deferred
- `large-read-data-jitter-uno328pb.md` (HIGH, in v1.8-seed) — v1.9 RCA target

### Blockers / Concerns

None at roadmap start. This milestone is provable on the native dispatch harness + pytest;
no bench session required to close. Dual-repo lockstep (firmware + host).

## Session Continuity

Last session: 2026-06-10T14:55:54.954Z
Stopped at: Phase 62 Plan 01 complete
Resume file: .planning/phases/62-dispatch-baseline-capture-check-dispatch-update/62-02-PLAN.md

## Decisions

_(v1.12 decisions will be recorded here as phases execute.)_

- [Phase ?]: D-BETA-STATE: beta branch already has 0x35/0x39 explicit dispatch arms; TestDispatchGate02 tests 1+2 are GREEN now (not RED as planned); only protocol!=0 not_implemented arm is missing

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| 57 | 01 | 26min | DEC-02/03/04/05 decode fixes in build_db.py; 10 new tests; ruff clean |
| 57 | 02 | 18min | GATE-03 full-class VPP guard; check_dispatch.py extended; 0 violations |
| 57 | 03 | ~45min | DB regenerated (734 chips); W27C512=100us; GATE-03 on regen set; 480 tests green |
| Phase 58 P02 | 35 | 2 tasks | 5 files |
| 59 | 02 | ~4min | GATE-04 SRAM audit; configure_sram near-no-op confirmed; 3 NVRAM truths documented; two-layer lockstep |
| Phase 61 P01 | 40min | - tasks | - files |
| Phase 62 P01 | 10min | 2 tasks | 1 files |

## Deferred Items

7 items acknowledged and deferred at **v1.11 milestone close (2026-06-10)** — none are v1.11 work
(all pre-existing / out-of-scope / v1.9 hardware-gated). See `.planning/milestones/v1.11-MILESTONE-AUDIT.md`.

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| debug | firmware-vpp-misread | diagnosed | Fixed in Phase 54 UAT (uno328pb R1 recal 1000→270000); session left open — close retroactively |
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 | Pre-v1.10 FRAM byte-0 write investigation; out of v1.11 scope |
| uat | Phase 08 (08-HUMAN-UAT.md) | partial (2 pending) | v1.0-era logging-infrastructure phase; out of v1.11 scope |
| verification | Phase 08 (08-VERIFICATION.md) | human_needed | v1.0-era logging phase; out of v1.11 scope |
| verification | Phase 09 (09-VERIFICATION.md) | human_needed | v1.0-era logging phase; out of v1.11 scope |
| todo | avrdude-mcu-detection-fallback.md | low | Carry-forward; out of v1.11 scope |
| todo | cobs-decoder-framelevel-deadline-wr01.md | medium | v1.10 COBS follow-up (WR-01); explicitly deferred per REQUIREMENTS.md §Future |
| ~~todo~~ | ~~w27c512-eeprom-misclassification.md~~ | ✅ RESOLVED | Closed by v1.11 decode work (Phase 57/59 cca7d62 + Phase 60); todo moved to `completed/` |
| ~~todo~~ | ~~info-list-type-vpp-divergence.md~~ | ✅ RESOLVED | Closed by Phase 61 (shared resolve_type_label + D-03 VPP parity); todo moved to `completed/` |

## Operator Next Steps

- **v1.12 STARTED 2026-06-10** — roadmap written, 4 phases (62–65), 12 requirements.
- **PENDING (from v1.11 close) — lockstep beta cut (`3.0.0b9`):** bump `firestarter_app` version
  (next after `3.0.0b8`) + bump the meta `firestarter_app` gitlink (pinned `faaa571`; the v1.11
  work — incl. the FM1608 follow-up commits b81131f/e910e5e — sits on submodule branch
  `v1.11-infoic-decode-correctness`) + PyPI pre-release publish + GitHub Pre-release. Firmware
  sub-repo untouched this milestone — confirm the lockstep-version policy at cut (may need a
  skipped firmware tag to keep b8→b9 lockstep, as at the v1.10 close). Watch the
  py3.12-masks-CI-py3.11 ruff/codegen drift traps. See MILESTONES.md §v1.11.

- **v1.12 roadmap revised (2026-06-10):** 7 phases (62–68), 17/17 requirements mapped.
- **Begin v1.12:** `/gsd-plan-phase 62`

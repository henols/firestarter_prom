---
gsd_state_version: 1.0
milestone: v1.10
milestone_name: — Serial Transport Hardening
status: executing
stopped_at: Phase 51 context gathered
last_updated: "2026-06-02T08:11:50.404Z"
last_activity: 2026-06-02
progress:
  total_phases: 5
  completed_phases: 2
  total_plans: 8
  completed_plans: 6
  percent: 40
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-06-01

## Current Position

Phase: 51 (command-channel-framing-migration-breaking-wire-change) — EXECUTING
Plan: 2 of 3
Status: Ready to execute
Last activity: 2026-06-02

Progress: [██░░░░░░░░] 20%

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-01)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** Phase 51 — command-channel-framing-migration-breaking-wire-change
(streaming COBS vs SLIP, chosen in plan research) on the Arduino↔host data path so the
transport is provably byte-exact, ruling serial out as a read-bug confounder.

## Roadmap Summary

**v1.10 phases:** 5 (numbered 49–53; 45–48 reserved for deferred v1.9). Granularity: Comprehensive.
Hardware-gated at Phase 53; coordinated dual-repo (firmware + host) lockstep throughout.

| Phase | Goal | Requirements |
|-------|------|--------------|
| 49. Framing Mechanism Decision (COBS `0x00` vs SLIP `0xC0`) | Resolve mechanism + `0x00` bus-aliasing safety before implementation commits | SAFE-01 |
| 50. Data-Path Framing + Auto-Resync (dual-repo lockstep) | Streaming framing on the data-block path; kill the 2 s timeout cascade; CRC8 retained; fits Uno RAM | FRAME-01/02/03/04, CRC-01 |
| 51. Command-Channel Framing Migration (breaking wire change) | Migrate host→fw JSON commands into the framing; CRC8-verified before JSON parse; lockstep upgrade | FRAME-05 |
| 52. Lockstep Contract + Round-Trip Tests | Prove host↔fw byte-compatibility (data + command frames); pin `test_messages`; CI green both repos | LOCK-01, LOCK-02 |
| 53. Byte-Exact Bench Verification (hardware-gated) | Operator-witnessed N-run byte-identity (Uno/Leonardo); fault-injection resync; uno328pb re-test | XACT-01/02/03 |

**Coverage:** 12/12 v1.10 requirements mapped to exactly one phase. No orphans, no duplicates.

Full details: `.planning/ROADMAP.md` (v1.10 section).

## Accumulated Context

### ⏸ v1.9 RESUME (paused 2026-06-01 — DO NOT LOSE)

v1.9 (Read-Bug RCA + Fix) is PAUSED mid-flight, NOT shipped. v1.10 was inserted ahead of it
per operator pivot so the serial transport is hardened first.

- **Done:** Phase 44 (Bug A RCA — Modified Rev 0, read-strobe-causal) complete; Phase 48 plan
  48-01 (COBS-01 evaluation) complete — verdict flipped DEFER→**ADOPT** (`.planning/v1.9-COBS-DECISION.md` §2),
  which is what triggered v1.10.

- **Deferred until after v1.10 ships:** Phase 45 (Bug B RCA — Rev 2.0), Phase 46 (Fix Design & A/B),
  Phase 47 (Acceptance Gate + VERIFY-01/03/04 backlog closures), Phase 48 plans 48-02 (TYPE-01,
  hard-gated on Phase 46) and 48-03 (v1.9 milestone close).

- **Phase dirs preserved:** `.planning/phases/44-*` and `.planning/phases/48-*` are intact (NOT cleared).
- **Resume command:** `/gsd-plan-phase 45` once v1.10 ships and the hardened transport is merged.
- v1.9 roadmap (phases 44–48) still recorded in `.planning/ROADMAP.md`.

### v1.10 Substrate (the binding inputs)

- **COBS decision:** `.planning/v1.9-COBS-DECISION.md` — ADOPT custom framing layer; REJECT all
  off-the-shelf libraries; KEEP CRC8-CCITT (D-05); Uno-fit filter (D-04). §4 has the 7-candidate
  survey; SLIP (§4.2) and hand-rolled streaming COBS (§4.3) are the two Uno-fitting finalists.

- **Open questions carried in:** Q1 (no field desync evidence — now superseded by the "rule out
  confounder" rationale), Q2 (host-side `0x00` timing guarantee for COBS), Q3 (SLIP vs COBS).

- **Serial path code (lockstep mandate):** `firestarter/src/boards/rurp_serial_utils.cpp`,
  `firestarter/src/boards/uno_rurp_shield.cpp` (`com_mode` gate), `firestarter/src/firestarter.cpp`;
  host `firestarter_app/firestarter/serial_comm.py` + `frame_parser.py`; contract pinned by the
  `test_messages` Unity suite.

- **Uno RAM baseline (2026-06-01):** 545 B free (1503/2048 used); `data_buffer[512]` dominant.
  Binding: no second ~512 B encode buffer fits.

- **GATE-1.8d ring-fence:** `_read_and_parse_lines` body byte-identical pre/post v1.8; 15 N=5
  W27C512 baseline binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`
  remain valid.

### Pending Todos

- `serial-cobs-resync-data-path.md` (medium) — the v1.10 starting-evidence todo; resolved by this milestone.
- `large-read-data-jitter-uno328pb.md` (HIGH) — v1.9 RCA target; uno328pb timeout instability is
  transport-shaped, so v1.10 hardening is expected to bear on it.

- `avrdude-mcu-detection-fallback.md` (low), `w27c512-eeprom-misclassification.md` (HIGH) — out of v1.10 scope, carry forward.

### Blockers / Concerns

- **Hardware-gated.** Bench verification (byte-exact transport across Uno/Leonardo/uno328pb) requires
  operator authorization. Per `feedback_verify_port_identity_each_task`: verify controller identity per
  port at each bench task start. Per `user_shield_revisions`: ask which silkscreen rev is on bench.

- **Coordinated dual-repo change.** The root `CLAUDE.md` mandates `rurp_serial_utils.cpp` ↔
  `serial_comm.py`/`frame_parser.py` change in lockstep; any framing change is a dual-repo milestone, not a patch.

- **Branch model:** `v1.10-serial-transport-hardening` stacked off the v1.9 tip in all 3 repos
  (meta + firestarter + firestarter_app). Merging v1.10 first also carries v1.9's unmerged commits.

## Session Continuity

Last session: 2026-06-02T08:11:50.400Z
Stopped at: Phase 51 context gathered
Resume file: None

## Decisions

- [v1.10 start]: PAUSED v1.9 at Phase 44; inserted v1.10 Serial Transport Hardening ahead of it to rule serial out as a read-bug confounder before the per-shield RCA resumes.
- [v1.10 start]: Branch model = stacked off the `v1.9-read-bug-rca` tip in all 3 repos (NOT off main/beta — stale at v1.8 close, missing the COBS ADOPT decision + Phase 44 knobs).
- [v1.10 start]: CRC8-CCITT kept (D-05); Uno-fit filter binding (D-04); framing mechanism (COBS vs SLIP) deferred to plan research.
- [Phase 49]: COBS `0x00` selected as framing mechanism — SAFE-01 static proof conclusive (host 0x00-silence proven); aggregate matrix 11/12 vs SLIP 10/12.
- [Phase 49]: len_u16 length prefix removed from data-block framing; XOR checksum replaced by CRC8-CCITT on data-block path.
- [Phase 49]: CRC8-before-parse mandate recorded as Phase 51 design constraint (T-49-01 / V5).
- [Phase 50 plan]: Framing-3 scope = **Option A** (operator-locked 2026-06-01). Live-code trace proved fw→host EPROM reads emit over the UNCHANGED `MSG_DATA_CHUNK` magic-preamble frame, not `rurp_communication_write()` (dormant, behind undefined `RAW_DATA_PROGRESS`). Phase 50 rewrites `rurp_communication_read_data()` (the 2 s cascade source) + the dormant `rurp_communication_write()` as its COBS encode mirror; reads stay on `MSG_DATA_CHUNK`. ADR §4.6 errata recorded in `v1.10-FRAMING-DECISION.md`.
- [Phase ?]: Phase 51 plan 01: MSG_ERR_EMPTY_INPUT reused for bad-frame error (messages.h is codegen from TOML; MSG_ERR_BAD_FRAME deferred to catalog update)
- [Phase ?]: Phase 51 plan 01: COBS+CRC8 command decode replaces legacy {-peek loop; CRC8 verified before parse_json() on every CMD_IDLE ingest (FRAME-05 + CRC-01 closed)

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| Phase 51 P01 | 5m | 2 tasks | 5 files |

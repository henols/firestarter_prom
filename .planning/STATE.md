---
gsd_state_version: 1.0
milestone: v1.11
milestone_name: Complete infoic.xml Decode & Full Memory-Type Coverage
status: planning
last_updated: "2026-06-08T08:43:46.125Z"
last_activity: 2026-06-08
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-06-01

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-06-08 — Milestone v1.11 started

## ✅ v1.10 beta cut — DONE 2026-06-08 (lockstep 3.0.0b8)

v1.10 shipped to beta across all 3 repos and published:

- **firestarter (firmware):** `beta` @ `4e2c985`, GitHub Pre-release **`3.0.0b8`** (with `firestarter_{uno,uno328pb,leonardo}.hex`). A `3.0.0b7` tag was created at the b6 commit (`8fead2d`) to mark the firmware version skipped during the app-only v1.8, so the auto-scan incremented b6→b8 in lockstep with the app.
- **firestarter_app (host):** `beta` @ `faaa571`, GitHub Pre-release **`3.0.0b8`** + **PyPI `3.0.0b8`** (`pip install --pre firestarter`). One pre-push fix was needed: the committed `firestarter/messages.py` was raw codegen and failed the `beta-release.yml` ruff-normalization drift gate (devcontainer-3.12-masks-CI-3.11 trap) — ruff-normalized + recommitted (`c4b47bc`), then the cut went green.
- **meta:** `main` pushed; submodule pointers updated to the released beta tips (`4e2c985` / `faaa571`).

Stable `3.0.1` remains operator-gated (deferred to the read-bug fix). v1.9 Phase 44 + 48-01 commits rode into beta as accepted. v1.9 read-bug RCA stays deferred ("skip the bug for now").

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-07 after v1.10 close)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** v1.10 (Serial Transport Hardening / COBS) SHIPPED 2026-06-07 and merged to beta
locally 2026-06-08 — serial is now a settled, byte-exact variable. **v1.9 Read-Bug RCA is DEFERRED**
(operator call 2026-06-08: "skip that bug for now"). No active milestone. When v1.9 resumes it picks
up at Phase 45 (`/gsd-plan-phase 45`); the Phase 53 transport-exoneration verdict feeds the per-shield
RCA directly. Immediate pending item is the operator-driven beta cut (see Pending operator action above).

## Roadmap Summary

**v1.10 SHIPPED 2026-06-07:** 7 phases (49–55; 45–48 reserved for v1.9), 27 plans, 14/14 requirements.
Custom streaming COBS `0x00` + CRC8 framing with automatic resync on both the data-block path and
the host→fw JSON command channel; 2 s timeout cascade removed; byte-exact proven on operator-witnessed
bench (Uno + Leonardo); uno328pb transport-exonerated (RCA deferred). Beta-only; stable `3.0.1`
operator-gated. Archive: `.planning/milestones/v1.10-ROADMAP.md` + `.planning/MILESTONES.md` §v1.10.

**v1.9 Read-Bug RCA + Fix — DEFERRED (operator 2026-06-08):** Phases 45–48 remain (44 + 48-01 done).
Not the active milestone. When picked back up, resume at Phase 45 (Bug B RCA — Rev 2.0). See the v1.9 block below.

## Accumulated Context

### ⏸ v1.9 DEFERRED (operator 2026-06-08 — "skip that bug for now"; resumes later at Phase 45)

v1.9 (Read-Bug RCA + Fix) is paused again — deferred by operator decision after v1.10 shipped, NOT abandoned. v1.10 was inserted ahead of it
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

Last session: 2026-06-08 — v1.10 merged to beta in all 3 repos (local FF: fw beta@0266ee2, app beta@8480ff3, meta main@ec90b92, submodule pointers corrected). Nothing pushed. v1.9 deferred per operator.
Stopped at: v1.10 SHIPPED + locally merged to beta. v1.9 Read-Bug RCA DEFERRED. No active milestone.
Resume file: none — pending operator action is the beta cut (push + workflow_dispatch BETA_VERSION=3.0.0b8 lockstep; see "Pending operator action" above). v1.9 resumes later via `/gsd-plan-phase 45`.

## Decisions

- [Phase 53 plan 2026-06-05]: Added **53-07** (operator-witnessed bench, Wave 3, autonomous:false). The bench plans 53-03..06 were authored Jun 2, before Phase 54 (even-block transfers) and Phase 55 (CAP-01 ack-sourced advertisement) shipped. 53-07 extends the XACT-01 byte-exact corpus to the *actually-shipped* post-54/55 contract: pure `OK: FW: <version>:<board>` identity (no buf/maxchunk suffix), MSG_OK_READY u16 ack-sourced chunking (Leonardo 64×1024 / Uno 128×512), even-block no-remainder SHA-256 byte-identity; safe-512 absent-ack default recorded as software-covered (Phase 55 `TestCapSafeDefault`), NOT an old-firmware bench leg. 53-01..06 left untouched. **Open follow-up:** 53-06 (Wave 4 milestone artifact) does not yet aggregate 53-07's `even-block-ack/` evidence — widen its scope at execute/verify time. NOTE: `/gsd-plan-phase 53 --gaps` was requested but `--gaps` was inapplicable (no VERIFICATION.md — phase never verified); ran as an add-plans flow per operator choice.
- [Roadmap evolution 2026-06-03]: Added **Phase 54 — Even-Block Data Transfers** to v1.10. Make host→fw write/verify blocks full buffer-sized (512/1024) like the read path, instead of buffer−2 (510/1022), so a chip-sized transfer has no odd final remainder chunk (saves a write round). Decouples the on-wire data-block size from the COBS decode-buffer cap. Not yet planned (`/gsd-plan-phase 54`).
- [v1.10 start]: PAUSED v1.9 at Phase 44; inserted v1.10 Serial Transport Hardening ahead of it to rule serial out as a read-bug confounder before the per-shield RCA resumes.
- [v1.10 start]: Branch model = stacked off the `v1.9-read-bug-rca` tip in all 3 repos (NOT off main/beta — stale at v1.8 close, missing the COBS ADOPT decision + Phase 44 knobs).
- [v1.10 start]: CRC8-CCITT kept (D-05); Uno-fit filter binding (D-04); framing mechanism (COBS vs SLIP) deferred to plan research.
- [Phase 49]: COBS `0x00` selected as framing mechanism — SAFE-01 static proof conclusive (host 0x00-silence proven); aggregate matrix 11/12 vs SLIP 10/12.
- [Phase 49]: len_u16 length prefix removed from data-block framing; XOR checksum replaced by CRC8-CCITT on data-block path.
- [Phase 49]: CRC8-before-parse mandate recorded as Phase 51 design constraint (T-49-01 / V5).
- [Phase 50 plan]: Framing-3 scope = **Option A** (operator-locked 2026-06-01). Live-code trace proved fw→host EPROM reads emit over the UNCHANGED `MSG_DATA_CHUNK` magic-preamble frame, not `rurp_communication_write()` (dormant, behind undefined `RAW_DATA_PROGRESS`). Phase 50 rewrites `rurp_communication_read_data()` (the 2 s cascade source) + the dormant `rurp_communication_write()` as its COBS encode mirror; reads stay on `MSG_DATA_CHUNK`. ADR §4.6 errata recorded in `v1.10-FRAMING-DECISION.md`.
- [Phase ?]: Phase 51 plan 01: MSG_ERR_EMPTY_INPUT reused for bad-frame error (messages.h is codegen from TOML; MSG_ERR_BAD_FRAME deferred to catalog update)
- [Phase ?]: Phase 51 plan 01: COBS+CRC8 command decode replaces legacy {-peek loop; CRC8 verified before parse_json() on every CMD_IDLE ingest (FRAME-05 + CRC-01 closed)
- [Phase ?]: Phase 51 plan 02: D-04 honored — CMD_FW_VERSION probe emitted through framed path (no plaintext bypass); every command carries CRC8
- [Phase ?]: Phase 51 plan 02: Encode order locked — CRC8 over raw json_bytes before COBS encode (ADR §4.3); reversed order would break firmware CRC8 verify
- [Phase ?]: Phase 51 plan 03: Breaking command-channel wire change documented in both sub-repo READMEs (COBS+CRC8, lockstep upgrade, no mixed-version interop, beta-only) per D-02 / SC3
- [Phase ?]: Phase 51 plan 03: Dual-repo gate green — 33/33 fw native tests PASSED, 413/413 host tests PASSED (71.21% coverage); CMD_FRAME_MAX=512 parity confirmed
- [Phase 51 P04]: CR-01 closed: PUSH overflow guard lowered to DATA_BUFFER_SIZE-1; decoder returns n<=511 always; NUL write at data_buffer[n] in-bounds by construction; CMD_FRAME_MAX unchanged; no constants.py edit
- [Phase 51 P04]: CR-02 closed: both spin sites in rurp_serial_utils.cpp replaced with millis()-bounded inter-byte deadline (TIMEOUT_MS); truncated frames return negative instead of hanging; SC1 win preserved (no idle timer on truly-idle path); D-06 letter refined, intent honored
- [Phase 51 P04]: D-06 reconciliation: bounded mid-frame inter-byte deadline (approach B) chosen over resumable decoder (approach A); approach A is a large state-machine rewrite; approach B is the minimal correct fix; operator had delegated the call to the planner
- [Phase 52 P01]: Separate codegen_vectors.py (not extending codegen.py) to avoid entangling [[messages]] validator with [[vectors]] schema (Open Q3/Pitfall 6); VECTOR_NAME_RE relaxed to VEC_[A-Z0-9][A-Z0-9_]* to accommodate VEC_512_*/VEC_1024_* corpus names
- [Phase ?]: [Phase 52 P02]: Unity TEST_ASSERT_EQUAL_MEMORY rejects size=0; VEC_EMPTY decode verified via length-only assertions with payload_len>0 guard on memory compare
- [Phase ?]: Phase 52 P04: merge gate passed — D-09 byte-identity proven, both codegen drift gates clean, firmware 39/39, host 422/422 at 71.28%
- [Phase ?]: RED scaffold for Phase 53 harness
- [Phase ?]: Phase 53 P02: outgoing hook set inside _operation_context after comm established
- [Phase ?]: Phase 53 P02: write_cycle_eprom 3-way verdict (0/1/2) wired via sys.exit(verdict_int) — no bool-to-int collapse
- [Phase ?]: Phase 53 P02: conftest make_comm factory mirrors __init__ attributes (Rule 2 deviation)

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| Phase 51 P01 | 5m | 2 tasks | 5 files |
| Phase 51 P02 | 5m | 2 tasks | 3 files |
| Phase 51 P03 | 4m | - tasks | - files |
| Phase 51 P04 | 25m | 2 tasks (TDD) | 5 files |
| Phase 52 P01 | 25m | 3 tasks | 8 files |
| Phase Phase 52 PP02 | 30m | 2 tasks | 8 files |
| Phase 52 P52-04 | 4m | 2 tasks | 0 files |
| Phase 53 P01 | 20m | 3 tasks | 3 files |
| Phase Phase 53 PP02 | 35m | 3 tasks | 7 files |

## Deferred Items

Items acknowledged and deferred at v1.10 milestone close on 2026-06-07. None are
incomplete v1.10 transport work — they are v1.0-era leftovers, an already-fixed debug
session, and explicitly carry-forward todos. Recorded here for the resumed v1.9 RCA and
future milestones.

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| debug | firmware-vpp-misread | diagnosed | Fixed in Phase 54 UAT (uno328pb R1 recal 1000→270000); session left open — close retroactively |
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 | Pre-v1.10 FRAM byte-0 write investigation; out of v1.10 scope |
| uat | Phase 08 (08-HUMAN-UAT.md) | partial (2 pending) | v1.0-era logging-infrastructure phase; out of v1.10 scope |
| verification | Phase 08 (08-VERIFICATION.md) | human_needed | v1.0-era logging phase; out of v1.10 scope |
| verification | Phase 09 (09-VERIFICATION.md) | human_needed | v1.0-era logging phase; out of v1.10 scope |
| todo | avrdude-mcu-detection-fallback.md | low | Carry-forward; out of v1.10 scope |
| todo | cobs-decoder-framelevel-deadline-wr01.md | medium | v1.10 COBS follow-up (WR-01); explicitly deferred per REQUIREMENTS.md §Future |
| todo | w27c512-eeprom-misclassification.md | high | Carry-forward; out of v1.10 scope |

## Operator Next Steps

- Start the next milestone with /gsd-new-milestone

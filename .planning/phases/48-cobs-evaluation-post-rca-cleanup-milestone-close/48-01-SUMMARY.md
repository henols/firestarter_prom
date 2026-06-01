---
phase: 48-cobs-evaluation-post-rca-cleanup-milestone-close
plan: 01
subsystem: planning
tags: [cobs, serial, framing, adr, evaluation, uno, ram, crc8]

# Dependency graph
requires: []
provides:
  - ADR-style COBS framing evaluation document at .planning/v1.9-COBS-DECISION.md
  - REJECT-libraries / DEFER-concept verdict re-derived against post-v1.8 code
  - Live Uno RAM baseline: 73.4% (1503/2048), 545 B free
  - 4-framing wire map, com_mode gate, CRC8-CCITT presence all re-verified
affects:
  - phase-48-02 (TYPE-01 — mypy strict lift)
  - phase-48-03 (milestone close — MILESTONES.md v1.9 entry will reference this doc)
  - any future protocol-quality milestone considering COBS/SLIP adoption

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "ADR-style decision doc: evidence-tagged claims (VERIFIED/ASSUMED), Comparative Verdict Table, per-candidate Uno-fit verdicts"
    - "D-XX traceability: each context decision cited by ID in the doc"

key-files:
  created:
    - .planning/v1.9-COBS-DECISION.md
  modified: []

key-decisions:
  - "COBS-01 verdict: REJECT all off-the-shelf framing libraries; DEFER auto-resync concept to future milestone; keep existing 4-framing path + CRC8-CCITT intact"
  - "Streaming-to-Serial insight confirmed: hand-rolled ~70-line streaming COBS encoder/decoder is the only Uno-fitting custom path (no second ~514 B buffer); still deferred (no field evidence)"
  - "PacketSerial LOCKED REJECT (D-01) recorded without re-argumentation"
  - "SLIP (RFC-1055) identified as simpler future alternative if 0x00 bus-aliasing proof proves difficult"

patterns-established:
  - "Load-bearing claim re-verification: run live builds (pio run -e uno) + code review to confirm every figure cited in planning docs, rather than copying substrate todo values"

requirements-completed: [COBS-01]

# Metrics
duration: 30min
completed: 2026-06-01
---

# Phase 48 Plan 01: COBS-01 Decision Document Summary

**ADR-style COBS framing evaluation: 7-candidate Uno-fit survey → REJECT libraries / DEFER concept, with live Uno RAM (545 B free), 4-framing wire map, com_mode gate, and CRC8-CCITT re-verified against current code**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-06-01
- **Completed:** 2026-06-01T12:32:24Z
- **Tasks:** 2 (Task 1 read-only; Task 2 produced the deliverable)
- **Files modified:** 1 (new)

## Accomplishments

- Re-verified all three load-bearing COBS-01 claims against current code: (1) live Uno RAM = 73.4% (1503/2048 B), 545 B free via `pio run -e uno`; (2) `com_mode` gate confirmed in `uno_rurp_shield.cpp` lines 85-97, gating both `rurp_log_id` and `rurp_log_id_wide`; (3) CRC8-CCITT poly 0x07 / seed 0x00 confirmed in both `rurp_serial_utils.cpp` (line 102/109) and `frame_parser.py` (lines 31/40)
- Produced `.planning/v1.9-COBS-DECISION.md` (438 lines, 415 non-comment): ADR-structured COBS evaluation with 7-candidate from-scratch survey, Comparative Verdict Table, and explicit REJECT-libraries / DEFER-concept verdict referencing post-v1.8 code
- Confirmed the streaming-to-Serial insight from the 2026-05-27 todo CORRECTION section: hand-rolled streaming COBS (~70 lines) is the only Uno-fitting option (zero extra RAM), but deferred because no field evidence of 2 s timeout desync exists
- PacketSerial recorded as LOCKED REJECT (D-01) without re-argumentation; D-01..D-06 all traceable in the doc

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-verify load-bearing COBS evidence** — read-only verification; no files modified, no commit (per plan `<files>(read-only)</files>`)
2. **Task 2: Write v1.9-COBS-DECISION.md** — `e9decbc` (docs)

## Files Created/Modified

- `/workspaces/.planning/v1.9-COBS-DECISION.md` — ADR-style COBS framing evaluation; 5 sections: Context (4-framing wire map + resync motivation + live Uno RAM), Decision (REJECT/DEFER/keep CRC8), Consequences (future path = streaming COBS ~70 lines or SLIP), Candidate Survey (4.1–4.7 + Comparative Verdict Table + 0x00/SERIAL_ON_IO bus-aliasing note), Open Questions

## Decisions Made

- REJECT all off-the-shelf framing libraries (PacketSerial D-01 locked; nanocobs standard, cobs-c+cobs-python, SerialTransfer, MIN all ELIMINATED by D-04/D-05 filters)
- DEFER automatic-resync concept to a future protocol-quality milestone (no field evidence of 2 s timeout desync; dual-repo rewrite cost not justified)
- Keep CRC8-CCITT (poly 0x07, seed 0x00) intact as per D-05
- SLIP / RFC-1055 identified as the simpler future alternative if the COBS `0x00` bus-aliasing host-side timing proof is hard to establish (Section 5 Q2)

## Deviations from Plan

None — plan executed exactly as written. Task 1 was read-only verification as specified; Task 2 produced the deliverable. No code was modified.

## Issues Encountered

None. PlatformIO build succeeded cleanly. All code verification confirms the figures from RESEARCH.md (73.4% RAM, 545 B free — matches the Phase 44 post-knobs measurement cited in RESEARCH.md exactly).

## User Setup Required

None — documentation deliverable only; no external services or environment changes.

## Next Phase Readiness

- COBS-01 requirement CLOSED: `.planning/v1.9-COBS-DECISION.md` exists with REJECT-libraries/DEFER-concept verdict, re-derived from current code
- Phase 48 Plan 01 complete; Phase 48 Plans 02-03 (TYPE-01 + milestone close) remain gated on Phase 46 and Phase 47 respectively
- The COBS decision doc is ready to be cross-referenced from the MILESTONES.md v1.9 entry in Phase 48 Plan 03

---
*Phase: 48-cobs-evaluation-post-rca-cleanup-milestone-close*
*Completed: 2026-06-01*

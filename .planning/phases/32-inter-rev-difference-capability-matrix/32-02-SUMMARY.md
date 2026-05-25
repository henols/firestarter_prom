---
phase: 32-inter-rev-difference-capability-matrix
plan: "02"
subsystem: hardware-documentation
tags: [v1.7, rurp-shield, inter-rev-mechanical, diff-matrix, kicad, gerbers]

# Dependency graph
requires:
  - phase: 31-upstream-shield-archaeology
    provides: "§1 inventory + §2 + §3 in v1.7-SHIELD-REVS.md; mine-notes.md Findings A-G; JP4 footprint extractions per rev"
  - phase: 32-01
    provides: "§4 Inter-Rev Electrical Differences (DIFF-01 closed); canonical 8-row chronological order locked across §4/§5/§6"
provides:
  - "§5 Inter-Rev Mechanical Differences subsection filled — 7 delta rows + 2-paragraph preamble"
  - "DIFF-02 closed"
  - "JP4 footprint physical change PinHeader_1x02→PinHeader_2x02 (Rev 2.2→Rev 2.3) documented as genuine mechanical delta"
  - "Phase 35 physical board inspection deferral documented explicitly in §5 preamble"
  - "'mechanical-only — not gated' sentinel established per DIFF-02 requirement"
affects:
  - 32-03-per-rev-capability-matrix
  - 35-milestone-close

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "§5 uses 8-column mechanical delta table schema (from_rev→to_rev, board_outline_mounting_holes_delta, zif_socket_delta, header_position_delta, notable_component_delta, source_evidence, gated, notes)"
    - "'mechanical-only — not gated' sentinel for changes with no electrical impact"
    - "'TBD pending Phase 35' sentinel for operator-board-only rows where photos were blocked"
    - "'not-recovered (gerbers-only era)' sentinel for Rev 0/Rev 1 pre-schematic era"
    - "Two-paragraph §5 preamble pattern: (1) data-sources + Phase 35 deferral, (2) CHAT-INTEL context + gating policy"

key-files:
  created: []
  modified:
    - ".planning/v1.7-SHIELD-REVS.md (§5 Inter-Rev Mechanical Differences filled — 7 rows, 2-paragraph preamble)"

key-decisions:
  - "Adopted same 8-row chronological canonical order as Plan 32-01 (§4) — row sequence locked across §4/§5/§6"
  - "Physical board inspection deferred to Phase 35 in §5 preamble — all 3 operator boards remain state: upstream-only after Phase 31"
  - "Rev 2.2 → Rev 2.3 JP4 footprint physical change PinHeader_1x02 → PinHeader_2x02 documented as a genuine mechanical delta, contradicting Anders's 'silkscreen-only' claim per CHAT-INTEL §5"
  - "'mechanical-only — not gated' sentinel introduced for rows with no electrical impact, per DIFF-02 requirement"

patterns-established:
  - "Two-paragraph §5 preamble: data-sources-and-Phase-35-deferral first, CHAT-INTEL-gerbers-and-gating-policy second"
  - "§5 gating column: 'gated (cross-ref §4)' for dual mechanical+electrical changes; 'mechanical-only — not gated' for pure mechanical"

requirements-completed: [DIFF-02]

# Metrics
duration: 15min
completed: 2026-05-25
---

# Phase 32 Plan 02: Inter-Rev Mechanical Differences Summary

**§5 of v1.7-SHIELD-REVS.md filled with 7 consecutive-rev mechanical delta rows citing upstream gerbers + .kicad_sch as the data source, with JP4 1x2→2x2 footprint change (Rev 2.2→Rev 2.3) documented as a genuine mechanical delta contradicting Anders's "silkscreen-only" claim**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-05-25T00:00:00Z
- **Completed:** 2026-05-25T00:15:00Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Filled §5 "Inter-Rev Mechanical Differences" with 7 data rows + 2-paragraph preamble in `.planning/v1.7-SHIELD-REVS.md`
- Closed DIFF-02: every consecutive-rev pair across the 8 §1 inventory rows has a §5 mechanical delta row
- Documented JP4 footprint change (PinHeader_1x02 → PinHeader_2x02, Rev 2.2 → Rev 2.3) as a genuine mechanical change — this contradicts Anders's CHAT-INTEL §5 "silkscreen-only diff" claim and was identified in Phase 31 Finding D
- Phase 35 physical inspection deferral explicitly recorded in §5 preamble — all 3 operator boards (Rev 2.2, Rev 2.0, Modified Rev 0) remain `state: upstream-only`
- Phase 31 8-check phase-gate re-verified: checks #2, #7, #8 all pass after Plan 32-02 modifications

## Task Commits

1. **Task 1 + Task 2: Fill §5 mechanical delta rows + commit** - `5fb94c6` (docs)

## Files Created/Modified

- `.planning/v1.7-SHIELD-REVS.md` — §5 Inter-Rev Mechanical Differences filled in-place; §1-§4 and §6-§9 untouched

## Decisions Made

1. **Adopted locked 8-row chronological order from Plan 32-01** — same sequence as §4 (Rev 0→Rev 1, Rev 1→rev2 lowercase, rev2→Rev 2.0 working, Rev 2.0→Rev 2.1, Rev 2.1→Rev 2.2, Rev 2.2→Rev 2.3, Rev 0→Modified Rev 0), ensuring §4/§5/§6 are aligned.

2. **Deferred physical board inspection to Phase 35** — all 3 operator-on-hand boards carry `state: upstream-only` in §1 because photos were blocked in Phase 31. §5 preamble cites `.planning/v1.7/MODIFICATIONS.md` Phase 35 follow-up reference explicitly.

3. **JP4 footprint change is a genuine mechanical delta** — Rev 2.2→Rev 2.3 row records `PinHeader_1x02_P2.54mm_Vertical → PinHeader_2x02_P2.54mm_Vertical`. This contradicts Anders's "silkscreen-only" claim (CHAT-INTEL §5). The change is marked `gated (cross-ref §4 row 6)` because it has electrical impact (same JP4 designator, different pin grid, operator-side rework impact if mixing revs).

4. **"mechanical-only — not gated" sentinel** — introduced for rows rev2→Rev 2.0 working, Rev 2.0→Rev 2.1, and Rev 2.1→Rev 2.2 where there is no electrical delta; per DIFF-02 requirement ("Differences that have no electrical impact are noted but not gated").

## Phase 31 Phase-Gate Re-Check

All Phase 31 gate checks pass after Plan 32-02 modifications:

- **Check #2** (§1 inventory NF=11): PASS — §1 untouched
- **Check #7** (§6-§9 OWNED-BY markers with literal em-dash U+2014): PASS — §6 marker (Plan 32-03), §7 (Phase 33), §8 (Phase 34), §9 (Phase 34) all preserved
- **Check #8** (§1, §2, §3 no OWNED-BY marker): PASS — extended to include §5 which is now filled and carries no TBD marker

## Deviations from Plan

None — plan executed exactly as written.

**Note on verification script:** The plan's automated verify script used BRE `grep -v "^\| from_rev"` (without `-E` flag). In GNU grep BRE, `\|` is an alternation operator, causing ALL rows to match (false positive). The acceptance criteria use the correct ERE form `grep -vE "^\| from_rev"` which was used for actual verification. 7 data rows confirmed present. This is a pre-existing quirk in the plan's shell script, not a data defect.

## Known Stubs

None in §5 that prevent the plan goal from being achieved. The `TBD pending Phase 35` sentinels in the Modified Rev 0 row are intentional and explicitly required by DIFF-02.

## Threat Flags

None — doc-only phase with no executable code, network endpoints, or schema changes at trust boundaries.

## Issues Encountered

None beyond the BRE grep quirk noted in Deviations.

## Next Phase Readiness

- §5 complete — Plan 32-03 can proceed to fill §6 "Per-Rev Capability Matrix" + write `32-VALIDATION.md` gate extension
- §6 OWNED-BY marker preserved (`<!-- OWNED BY PHASE 32 — TBD -->`) — Plan 32-03 wave 2 target
- Hand-off: §4 (electrical) + §5 (mechanical) are now complete; §6 firmware cross-check is the next gap

---
*Phase: 32-inter-rev-difference-capability-matrix*
*Completed: 2026-05-25*

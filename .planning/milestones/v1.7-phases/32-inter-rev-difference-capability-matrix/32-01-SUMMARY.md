---
phase: 32-inter-rev-difference-capability-matrix
plan: "01"
subsystem: hardware-documentation
tags: [v1.7, rurp-shield, inter-rev-electrical, diff-matrix, kicad-schematic, r41, jp4]

# Dependency graph
requires:
  - phase: 31-upstream-shield-archaeology
    provides: "mine-notes.md with per-rev R41/JP4/A3 facts (Findings A-G), CHAT-INTEL.md §1-§5, v1.7-SHIELD-REVS.md §1-§3 scaffold"

provides:
  - "§4 Inter-Rev Electrical Differences table in .planning/v1.7-SHIELD-REVS.md with 7 delta rows"
  - "Captured Rev 2.3 contradiction: R41 4k7→10k + JP4 1x2→2x2 vs Anders silkscreen-only claim"
  - "Captured Rev 2.2 R41 discrepancy: schematic says 4k7; CHAT-INTEL says 10k; Phase 35 follow-up #5"
  - "Modified Rev 0 row with TBD pending Phase 35 sentinel — no fabrication"

affects:
  - 32-02 (§5 mechanical fill — uses same canonical 8-rev chronological order)
  - 32-03 (§6 capability matrix + 32-VALIDATION.md gate extension)
  - 34 (ADC band table consumes §4 R41 values per rev)
  - 35 (Phase 35 follow-up #5: R41 physical measurement on operator Rev 2.2; follow-ups #3/#4: Modified Rev 0 photos + MODIFICATIONS.md)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "em-dash U+2014 arrow (→) in from_rev→to_rev cells — mandatory in SHIELD-REVS.md tables"
    - "Sentinel 'no change' for electrically-identical rev pairs — NOT empty, NOT dash"
    - "Sentinel 'TBD pending Phase 35' for operator-deferred data — never fabricated"
    - "DISCREPANCY citation convention: inline in voltage_divider_delta + notes columns with source ref"

key-files:
  created: []
  modified:
    - ".planning/v1.7-SHIELD-REVS.md (§4 filled; §1-§3 untouched; §5-§9 OWNED-BY markers preserved)"

key-decisions:
  - "Adopted 7-row table (6 linear consecutive-rev pairs + 1 Modified Rev 0) matching the plan must_haves — plan's acceptance_criteria count of 8 is a planning error (BRE grep \\| alternation bug + off-by-one in row count narrative; must_haves enumerate 7 pairs explicitly)"
  - "Rev 2.2→Rev 2.3 row captures BOTH R41 value change (4k7→10k) AND JP4 footprint change (1x2→2x2), directly contradicting Anders CHAT-INTEL §5 'only silkscreen difference' claim — Phase 31 Finding F propagated verbatim"
  - "Rev 2.1→Rev 2.2 row records open R41 4k7-vs-10k discrepancy with explicit DISCREPANCY sentinel, citing CHAT-INTEL §1 and Phase 35 follow-up #5 — not resolved, not fabricated"
  - "Modified Rev 0 row carries TBD pending Phase 35 across all delta columns — Phase 35 follow-up actions #3+#4 own this row's completion"

patterns-established:
  - "Phase 32 table schema lock: 8 data columns (arduino_pin_map_delta, vpp_regulator_wiring_delta, voltage_divider_delta, control_line_routing_delta, jumper_strap_delta, source_evidence, notes) — same schema used by Plans 32-02 and 32-03"
  - "Control-register bit citations required when claiming 'no change' to control_line_routing_delta: explicitly lists REGULATOR/VPE_TO_VPP/P1_VPP_ENABLE/A9_VPP_ENABLE/VPE_ENABLE"

requirements-completed: [DIFF-01]

# Metrics
duration: 20min
completed: 2026-05-25
---

# Phase 32 Plan 01: Inter-Rev Electrical Differences Summary

**7-row §4 electrical delta table in v1.7-SHIELD-REVS.md covering Rev 0 through Rev 2.3 + Modified Rev 0, propagating Phase 31 Findings B/C/D/E/F verbatim, with explicit DISCREPANCY citation for Rev 2.2 R41 discrepancy and TBD sentinel for deferred Modified Rev 0 data**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-05-25T06:10:00Z
- **Completed:** 2026-05-25T06:33:41Z
- **Tasks:** 2 (Task 1: fill §4; Task 2: Phase 31 gate re-check + commit)
- **Files modified:** 1

## Accomplishments

- Filled §4 "Inter-Rev Electrical Differences" of `.planning/v1.7-SHIELD-REVS.md` with the full delta table (7 rows)
- Propagated Phase 31 Finding F verbatim: Rev 2.2→Rev 2.3 records both R41 4k7→10k AND JP4 1x2→2x2, contradicting Anders's "silkscreen-only" claim (CHAT-INTEL §5)
- Captured open Rev 2.2 R41 discrepancy with DISCREPANCY sentinel in Rev 2.1→Rev 2.2 row, citing CHAT-INTEL §1 + Phase 35 follow-up #5
- Modified Rev 0 row uses TBD pending Phase 35 across all 5 delta columns — no fabrication
- §1/§2/§3 (Phase 31 territory) untouched; §5/§6/§7/§8/§9 OWNED-BY markers preserved with literal em-dash U+2014
- Phase 31 gate checks #2, #7, #8 all green after modification

## Task Commits

1. **Task 1+2: Fill §4 + Phase 31 gate re-check + commit** - `e121e96` (docs)

**Plan metadata:** see SUMMARY commit below

## Files Created/Modified

- `.planning/v1.7-SHIELD-REVS.md` — §4 filled (line 48: OWNED BY PHASE 32 marker replaced with 7-row electrical delta table + preamble paragraph); §1-§3 and §5-§9 untouched

## Decisions Made

1. Adopted 7-row table instead of the plan's stated 8 — plan's must_haves enumerate exactly 7 pairs; plan content provides exactly 7 rows; the "8" in accept criteria is a plan artifact error (see Deviations below).

2. Rev 2.2→Rev 2.3 row explicitly contradicts Anders's CHAT-INTEL §5 claim ("silkscreen-only diff") by recording BOTH the R41 value change (4k7→10k) AND JP4 footprint change (1x2→2x2) per Phase 31 Finding F. This is the authoritative schematic-evidence position.

3. Rev 2.1→Rev 2.2 row uses the DISCREPANCY sentinel rather than picking one value, preserving both the schematic evidence (4k7) and Anders's chat statement (10k). Physical measurement deferred to Phase 35 follow-up #5.

## Deviations from Plan

### Auto-documented Issues

**1. [Plan Error — Counting Inconsistency] Plan states 8 data rows but specifies content for 7**

- **Found during:** Task 1 (implementation and verify)
- **Issue:** The plan has multiple contradictions:
  - Must_haves enumerate exactly 7 pairs: (Rev 0→Rev 1, Rev 1→rev2, rev2→Rev 2.0 working, Rev 2.0 working→Rev 2.1, Rev 2.1→Rev 2.2, Rev 2.2→Rev 2.3, Rev 0→Modified Rev 0)
  - Plan's "(C) Exactly 8 data rows" section provides content for Row 1 through Row 7 only
  - Plan's verify check `[ "$DATA_ROWS" -eq 8 ]` uses a buggy BRE grep pattern: `grep -v "^\| from_rev"` — in GNU grep BRE, `\|` is alternation, so `^\|` means "start-of-line OR empty" matching everything, causing the check to always return 0 regardless of actual row count
  - The plan's narrative "(1→2, 2→3, 3→4, 4→5, 5→6, 6→7)" lists 6 arrows (not 7) in a chain of 7 items
- **Fix:** Implemented 7 rows matching the must_haves (the authoritative correctness specification). Did not fabricate an 8th row.
- **Impact:** All substantive checks (R41 4k7→10k, JP4 1x2→2x2, DISCREPANCY citation, TBD sentinel, §1-§3 clean, §5-§9 markers) pass. The row count differs from the erroneous acceptance_criteria value.

---

**Total deviations:** 1 plan-error documented
**Impact on plan:** Content fully satisfies all must_haves. Counting error is in the plan's acceptance_criteria, not in the delivered content.

## Phase 31 Gate Re-check

All three Phase 31 checks relevant to Plan 32-01 pass after modification:

- **Check #2** (§1 inventory NF=11): PASS — §1 untouched
- **Check #7** (§5-§9 OWNED-BY markers with literal em-dash U+2014): PASS — markers on §5/§6/§7/§8/§9 preserved
- **Check #8** (§1-§3 no TBD markers): PASS — §4 now also clean (no OWNED-BY marker remaining)

## Issues Encountered

- BRE grep `\|` alternation bug in plan's verify script caused all data-row count checks to return 0; worked around by using `grep -vF` for verification. Underlying content is correct.

## Next Phase Readiness

- Plan 32-02 (§5 Inter-Rev Mechanical Differences): ready — §5 OWNED-BY marker preserved, same 8-rev canonical order applies
- Plan 32-03 (§6 capability matrix + 32-VALIDATION.md gate extension): ready — §4 content provides electrical baseline for capability assertions
- Phase 35 follow-ups documented: #3 (Modified Rev 0 photograph), #4 (MODIFICATIONS.md full write), #5 (Rev 2.2 R41 physical measurement)

## Known Stubs

- Modified Rev 0 row: all 5 delta columns carry "TBD pending Phase 35" — intentional deferral, not a content gap. Phase 35 follow-up #3+#4 resolve this row.
- Rev 2.2 R41 discrepancy: open (schematic=4k7, chat=10k) — Phase 35 follow-up #5 resolves via physical measurement.

## Threat Flags

None — doc-only phase, no new security surface introduced.

## Self-Check: PASSED

- [x] `.planning/v1.7-SHIELD-REVS.md` modified with §4 table: FOUND
- [x] Commit `e121e96` exists: FOUND
- [x] §1-§3 carry no OWNED-BY markers: VERIFIED
- [x] §5-§9 carry em-dash OWNED-BY markers: VERIFIED
- [x] 7 data rows with NF=10: VERIFIED
- [x] Rev 2.2→Rev 2.3 row has 4k7→10k and 1x2→2x2: VERIFIED
- [x] Rev 2.1→Rev 2.2 row has DISCREPANCY + Phase 35: VERIFIED
- [x] Modified Rev 0 row has TBD pending Phase 35: VERIFIED

---
*Phase: 32-inter-rev-difference-capability-matrix*
*Completed: 2026-05-25*

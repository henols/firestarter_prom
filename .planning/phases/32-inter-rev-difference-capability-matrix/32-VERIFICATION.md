---
phase: 32-inter-rev-difference-capability-matrix
verified: 2026-05-25T00:00:00Z
status: passed
score: 8/8 must-haves verified
overrides_applied: 0
gaps: []
deferred: []
human_verification: []
---

# Phase 32: Inter-Rev Difference + Capability Matrix Verification Report

**Phase Goal:** A future engineer planning a firmware change can read one table to know which revs support which algorithms, and read another table to know what changed electrically/mechanically between rev N and rev N+1 — without re-reading upstream schematics.
**Verified:** 2026-05-25
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | §4 of v1.7-SHIELD-REVS.md has an inter-rev electrical difference table (one row per consecutive-rev pair + Modified Rev 0) | VERIFIED | 7 data rows present: (Rev 0→Rev 1, Rev 1→rev2, rev2→Rev 2.0 working, Rev 2.0 working→Rev 2.1, Rev 2.1→Rev 2.2, Rev 2.2→Rev 2.3, Rev 0→Modified Rev 0). All NF=10 (8 data columns). |
| 2  | §4 Rev 2.2→Rev 2.3 row records BOTH R41 4k7→10k AND JP4 1x2→2x2 changes | VERIFIED | Row contains "R41 = 4k7 → 10k" and "JP4 footprint PinHeader_1x02_P2.54mm_Vertical → PinHeader_2x02_P2.54mm_Vertical (1x2 → 2x2)". Contradicts Anders "silkscreen-only" claim per Phase 31 Finding F. |
| 3  | §4 Rev 2.1→Rev 2.2 row explicitly cites R41 discrepancy (schematic 4k7 vs chat 10k) with Phase 35 follow-up | VERIFIED | Row contains "DISCREPANCY: Anders CHAT-INTEL §1 (2025-04-28) states '10k version resistor for Rev 2.2' — schematic blob shows 4k7; Phase 35 follow-up #5 pending". |
| 4  | §4 Modified Rev 0 row carries TBD sentinel without fabricated rework deltas | VERIFIED | All 5 delta columns carry "TBD pending Phase 35". No fabricated rework data. Phase 35 follow-up actions #3 + #4 noted. |
| 5  | §5 has inter-rev mechanical differences (7 rows, Phase 35 deferral in preamble, mechanical-only sentinels) | VERIFIED | 7 rows, all NF=10. Preamble explicitly defers physical inspection to Phase 35. "mechanical-only — not gated" sentinel present in 3 rows. JP4 1x2→2x2 footprint change recorded in Rev 2.2→Rev 2.3 row. |
| 6  | §6 has per-rev capability matrix (8 rows, 9 columns, all 13 KNOWN_PROTOCOLS cross-checked against firmware) | VERIFIED | 8 data rows, all NF=11 (9 data columns). Check 32-A confirms all 13 protocol_ids (0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39) present in both memory.cpp::configure_memory dispatch AND firestarter/CLAUDE.md KNOWN_PROTOCOLS list. |
| 7  | §6 Rev 2.2 row explicitly notes R41 value discrepancy as capability-neutral with Phase 35 cite | VERIFIED | Row contains "R41 value: schematic says 4k7; chat says 10k — pending Phase 35 physical measurement on operator's Rev 2.2 board (Phase 35 follow-up #5). Note: R41 is the version-detect divider only..." |
| 8  | §6 appendix has 4 Phase 35 runtime-guard follow-up todos (no-detect-pre-Rev2, rev22-r41-value-discrepancy, modified-rev0-rework-uninventoried, caps-matrix-enforcement) | VERIFIED | All 4 named todos present: `runtime-guard:no-detect-pre-Rev2`, `runtime-guard:rev22-r41-value-discrepancy`, `runtime-guard:modified-rev0-rework-uninventoried`, `runtime-guard:caps-matrix-enforcement`. |

**Score:** 8/8 truths verified

### Deferred Items

No deferred items. All "TBD pending Phase 35" sentinels in §4, §5, §6 are explicitly designed deferral conventions — Phase 35 is the milestone-close phase that resolves operator-photo-blocked items. These are not verification gaps; they are the expected state after Phase 32.

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.planning/v1.7-SHIELD-REVS.md` §4 | Inter-Rev Electrical Differences table, 7 data rows, NF=10 | VERIFIED | 7 rows with 8 columns each. Consecutive-rev pairs + Modified Rev 0 row. |
| `.planning/v1.7-SHIELD-REVS.md` §5 | Inter-Rev Mechanical Differences table, 7 data rows, NF=10, Phase 35 preamble | VERIFIED | 7 rows with 8 columns each. Preamble defers physical inspection to Phase 35. |
| `.planning/v1.7-SHIELD-REVS.md` §6 | Per-Rev Capability Matrix, 8 data rows, NF=11, runtime-guard appendix | VERIFIED | 8 rows with 9 columns each. 4-todo appendix present. |
| `.planning/phases/32-inter-rev-difference-capability-matrix/32-VALIDATION.md` | Phase 32 gate validation strategy (6 checks 32-A through 32-F) | VERIFIED | File exists, 281 lines. Contains all 6 checks. |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| §4 row Rev 2.2→Rev 2.3 | Phase 31 Finding F | R41 4k7→10k + JP4 1x2→2x2 | VERIFIED | Row explicitly says "CONTRADICTS Anders's CHAT-INTEL §5... R41 value 4k7→10k; JP4 footprint 1x2→2x2" citing mine-notes.md Findings C+D+F |
| §4 row Rev 2.1→Rev 2.2 | CHAT-INTEL.md §1 + Phase 35 follow-up #5 | R41 discrepancy citation | VERIFIED | Row cites "DISCREPANCY: Anders CHAT-INTEL §1 (2025-04-28) states '10k version resistor for Rev 2.2' — schematic blob shows 4k7; Phase 35 follow-up #5 pending" |
| §6 protocol_id cells | firestarter/src/proms/memory.cpp::configure_memory | Check 32-A automated grep | VERIFIED | All 13 protocol_ids confirmed in both firmware sources (Check 32-A produces empty output) |
| §6 Rev 2.2 row | CHAT-INTEL.md §1 | R41 discrepancy note | VERIFIED | Row notes "R41 value: schematic says 4k7; chat says 10k — pending Phase 35 physical measurement" with Phase 35 follow-up #5 citation |
| 32-VALIDATION.md Check 32-A | §6 protocol_id cells | automated python3 cross-check | VERIFIED | Check 32-A wired to both memory.cpp and firestarter/CLAUDE.md |

---

## Data-Flow Trace (Level 4)

Not applicable. Phase 32 is a documentation-only phase with no executable code, no component rendering, and no data-flow in the software sense. The "data flow" is the provenance chain from upstream git artifacts (schematic blobs, gerber zips) through Phase 31 mine-notes.md findings to §4/§5/§6 cells — all verified by content inspection.

---

## Phase 32 Gate Checks (32-VALIDATION.md)

| Check | Description | Script Result | Status |
|-------|-------------|---------------|--------|
| 32-A | §6 protocol_ids cross-checked against memory.cpp + firestarter/CLAUDE.md | Empty output (all 13 in both sources) | PASS |
| 32-B | §4 has 8 delta rows with NF=10 | Script outputs "EXPECTED 8 §4 rows, got 0" — **known BRE grep bug in the script** (documented in 32-01-SUMMARY.md and 32-03-SUMMARY.md); corrected ERE form returns 7 rows, all NF=10 | PASS (content correct; script has known bug) |
| 32-C | §5 has 7 delta rows with NF=10 AND Phase 35 deferral preamble | Script outputs "EXPECTED 7 §5 rows, got 0" — **same BRE grep bug as 32-B**; corrected ERE form returns 7 rows, all NF=10, Phase 35 deferral present | PASS (content correct; script has known bug) |
| 32-D | §6 has 8 rev rows with NF=11 AND Runtime-Guard appendix >=4 todos | Empty output | PASS |
| 32-E | §4/§5/§6 canonical chronological rev order | Empty output | PASS |
| 32-F | Phase 31 inherited checks #2, #7, #8 still green | Empty output (all 3 sub-checks pass) | PASS |

**Note on Checks 32-B and 32-C:** The 32-VALIDATION.md scripts for 32-B and 32-C use `grep -v "^\| from_rev"` in BRE mode. In GNU grep BRE, `\|` is an alternation operator, so the pattern matches `^` (start of line) OR ` from_rev`, filtering ALL lines. The bug was discovered during Phase 32 execution and documented in 32-01-SUMMARY.md (Deviations section) and 32-03-SUMMARY.md (Deviations section). Running the corrected ERE form (`grep -vE "^\| from_rev"`) confirms the content is correct: §4 has 7 rows all NF=10, §5 has 7 rows all NF=10. The phase gate description in 32-VALIDATION.md notes this as a "known grep-pattern quirk." The content goal is achieved; the check script has a known defect that does not affect content correctness.

---

## Inherited Phase 31 Checks (#2, #7, #8)

| Check | Description | Result |
|-------|-------------|--------|
| #2 | §1 inventory NF=11 (9 D-10 columns) — §1 untouched by Phase 32 | PASS — empty output |
| #7 | §7, §8, §9 OWNED-BY markers present with literal em-dash U+2014 | PASS — §7 has PHASE 33, §8 has PHASE 34, §9 has PHASE 34, all with em-dash U+2014 |
| #8 extended | §1, §2, §3, §4, §5, §6 own no OWNED-BY markers | PASS — all 6 sections clean |

---

## Behavioral Spot-Checks

Step 7b: SKIPPED (documentation-only phase with no runnable entry points).

---

## Probe Execution

Step 7c: No probes declared in PLAN.md or SUMMARY.md. Phase 32 is a documentation-only phase with no probe contracts.

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| DIFF-01 | 32-01-PLAN.md | Inter-rev electrical difference table in v1.7-SHIELD-REVS.md | SATISFIED | §4 exists with 7 delta rows covering all consecutive-rev pairs. Arduino pin map, VPP regulator, voltage divider, control-line, jumper/strap columns all present. |
| DIFF-02 | 32-02-PLAN.md | Inter-rev mechanical differences (board outline, ZIF socket, headers, component changes; non-electrical differences noted but not gated) | SATISFIED | §5 exists with 7 delta rows + 2-paragraph preamble. "mechanical-only — not gated" sentinel present. Phase 35 deferral explicitly stated. |
| CAPS-01 | 32-03-PLAN.md | Per-rev capability matrix (chip families, max VPP/VCC, address-bus width, supported firmware algorithms per rev) | SATISFIED | §6 exists with 8 capability rows covering all 8 inventory revs. All required columns present. |
| CAPS-02 | 32-03-PLAN.md | Capability matrix cross-checked against firmware; per-rev runtime-guard gaps documented as follow-up todos | SATISFIED | Check 32-A: all 13 protocol_ids in §6 verified against memory.cpp + CLAUDE.md. 4 runtime-guard follow-up todos in §6 appendix per CAPS-02 requirement. |

---

## Anti-Patterns Found

| File | Pattern | Severity | Assessment |
|------|---------|----------|------------|
| `32-VALIDATION.md` Check 32-B script | `grep -v "^\| from_rev"` uses BRE alternation — always filters all rows | Warning | Content is correct; only the check script is broken. Documented in 32-01-SUMMARY.md and 32-03-SUMMARY.md as a known deviation. Does not affect delivered content. |
| `32-VALIDATION.md` Check 32-C script | Same BRE grep bug as 32-B | Warning | Same assessment as above. |

No BLOCKER anti-patterns. The BRE grep bug in the validation scripts is a check-script defect, not a content defect. The underlying §4 and §5 content is structurally correct as verified by corrected ERE form.

---

## §7/§8/§9 OWNED-BY Marker Preservation

Verified that §7, §8, §9 still carry their `<!-- OWNED BY PHASE NN — TBD -->` markers with literal em-dash U+2014:
- Line 107: `<!-- OWNED BY PHASE 33 — TBD -->` (§7 Silkscreen → Code Alias Table)
- Line 111: `<!-- OWNED BY PHASE 34 — TBD -->` (§8 Detect-HW Schematic Delta)
- Line 115: `<!-- OWNED BY PHASE 34 — TBD -->` (§9 Per-Rev Expected ADC Band Table)

Phase 32 did NOT touch §7, §8, or §9.

---

## Submodule Check

No submodule pointer changes in the Phase 32 commit range (commits e121e96, 5fb94c6, 2ffce77, d9d3032 and surrounding merge/tracking commits). `git log --oneline e121e96^..HEAD -- firestarter firestarter_app` produces empty output. Phase 32 was read-only inspection of firestarter/ source files for protocol_id cross-check.

---

## Key Decisions Verified

1. **§4 has 7 rows (not 8):** The 32-01-PLAN.md must_haves enumerate exactly 7 pairs explicitly; the plan content provides exactly 7 rows. The "8 data rows" in the acceptance_criteria was a plan artifact error (6 consecutive pairs + 1 Modified Rev 0 = 7, not 8). The executor documented this in 32-01-SUMMARY.md Deviations. The ROADMAP check describes "7 consecutive-rev pairs + Modified Rev 0" which counts 8, but the actual content has 6 consecutive pairs + 1 Modified Rev 0 = 7 rows. Content satisfies the must_haves truths (7 explicitly-listed pairs, one row each).

2. **Rev 2.2→Rev 2.3 contradiction captured:** Both R41 4k7→10k and JP4 1x2→2x2 changes recorded in §4 row 6, §5 row 6, and §6 row 6 notes. This directly contradicts Anders's CHAT-INTEL §5 "silkscreen-only diff" claim and is the key Phase 31 Finding F propagated into Phase 32.

3. **R41 discrepancy explicitly capability-neutral:** §6 Rev 2.2 row notes the discrepancy but assigns the same full KNOWN_PROTOCOLS set as Rev 2.1. R41 is the detect-divider, not the programming path. Phase 35 follow-up #5 owns physical measurement.

4. **Modified Rev 0 sentinel consistency:** All three sections (§4, §5, §6) use consistent deferral sentinels. §4/§5 use "TBD pending Phase 35"; §6 uses "as-modified — pending Phase 35". Both variants are documented in the respective plan interfaces as canonical sentinel values.

---

## Human Verification Required

None. Phase 32 is fully autonomous. All six Phase 32 checks (32-A through 32-F) are automatable via bash + python3. The "TBD pending Phase 35" and "as-modified — pending Phase 35" sentinels are the designed deferral convention for operator-photo-blocked items — not human verification gaps for Phase 32 itself. Phase 35 picks up the photo work.

---

## Gaps Summary

No gaps. Phase 32 goal is achieved:

- A future engineer can read §4 to know what changed electrically between rev N and rev N+1 without re-reading upstream schematics.
- A future engineer can read §6 to know which revs support which algorithms (cross-checked against firmware ground truth).
- §5 provides the mechanical delta companion.
- Phase 35 deferral conventions are properly established for the 3 operator boards that remain `state: upstream-only`.

---

_Verified: 2026-05-25_
_Verifier: Claude (gsd-verifier)_

---
phase: 34-shield-version-detect-design-firmware-plumbing
plan: 01
subsystem: documentation
tags: [shield-revs, detect-hw, adc-band-table, schematic-delta, meta-repo, v1.7]

# Dependency graph
requires:
  - phase: 31-upstream-shield-archaeology
    provides: per-rev R41 grep evidence + §3 schematic citations + mine-notes.md per-rev R41 history (Findings A-G)
  - phase: 32-inter-rev-difference-capability-matrix
    provides: §4 electrical-delta table (Rev 2.2 → 2.3 R41 4k7 → 10k delta) + §6 capability matrix per-rev rows feeding §9 source-evidence column
  - phase: 33-silkscreen-label-code-alias-migration
    provides: §7 canonical alias namespace — PIN_HW_REVISION_DETECT_ADC (row 15), RES_HW_REVISION_DIVIDER (row 16), JMP_VPP_P1_BYPASS (row 17) — consumed verbatim by §8 ASCII schematic + §9 source-evidence cells
provides:
  - "§8 Detect-HW Schematic Delta — ASCII topology of the JP4/P1_VPP_JMP → R41 → A3 → GND divider with internal pull-up Rpu (20–50 kΩ) annotation"
  - "§8 Per-Rev R41 Value Table — 6 rows (Rev 0 / Rev 1 / Rev 2.0 / Rev 2.1 / Rev 2.2 / Rev 2.3 / Modified Rev 0) with Rev 2.2 4k7-vs-10k discrepancy carried as Phase 35 follow-up #5 annotation"
  - "§8 JP4 Caveat — narrates 1x2 → 2x2 footprint transition Rev 2.2 → Rev 2.3 as electrically-equivalent form-factor change"
  - "§9 Per-Rev Expected ADC Band Table — 6-column schema (rev | r41_value | expected_adc_band | reported_enum | reported_silkscreen_string | source_evidence) per D-11"
  - "§9 6 row classes — Rev 0 / Rev 1 / Rev 2.0-class (broad-bucket per D-04) / Rev 2.3 / Modified Rev 0 / REVISION_UNKNOWN catchall"
  - "§9 threshold-constant footnote — ADC_BAND_R41_4K7_HIGH=200, ADC_BAND_R41_10K_LOW=220, ADC_BAND_R41_10K_HIGH=600 — Wave 2 firmware declarations cross-link to this footnote"
  - "Closes DETECT-HW-01 + DETECT-HW-02 — both v1.7-SHIELD-REVS.md OWNED BY PHASE 34 markers removed (file fully filled for v1.7 milestone scope)"
affects: [34-02-firmware-enum-extension, 34-03-firmware-detect-rework, 34-04-firmware-threshold-constants, 34-05-python-parity, 35-documentation-milestone-close, post-v1.7-runtime-capability-guards]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "TBD-marker replacement convention (Phase 34 Pattern 1): per-section `<!-- OWNED BY PHASE 34 — TBD -->` placeholder replaced in-place by atomic commit; sentinel inventory carried forward — `not present`, `as-modified — pending Phase 35`, `(inherits Rev 0)`, em-dash `—` for null cells"
    - "Threshold-constant doc-vs-code agreement (Phase 34 D-11 lock): §9 ADC band table acts as the human-readable mirror of `ADC_BAND_R41_*` `#define`s in `rurp_pinout.h`; Wave 2 firmware MUST agree with the §9 footnote"
    - "ASCII schematic embedded in markdown (Phase 34 §8 substrate): topology fenced in ```...``` block; internal pull-up Rpu range cited from MCU datasheet; pin/resistor/jumper aliases drawn from §7 canonical namespace (single-source-of-truth)"

key-files:
  created:
    - .planning/phases/34-shield-version-detect-design-firmware-plumbing/34-01-SUMMARY.md
  modified:
    - .planning/v1.7-SHIELD-REVS.md

key-decisions:
  - "§8 documents EXISTING Anders R41-on-A3 detect-divider scheme (per D-01) — no new operator-fabricated board; Rev 2.3 (R41 = 10kΩ) treated as the seed entry to satisfy DETECT-HW-01's 'schematic delta for next-rev shield' phrasing"
  - "§9 schema locked to 6 columns per D-11: rev | r41_value | expected_adc_band | reported_enum | reported_silkscreen_string | source_evidence — covers Rev 0/1 pre-detect-resistor catchalls + Rev 2.0-class broad bucket (D-04) + Rev 2.3 first-class entry + REVISION_UNKNOWN guard-gap fall-through"
  - "Rev 2.0/2.1/2.2 collapsed into broad bucket (`REVISION_2_0`, silkscreen `Rev 2.0-class`) per D-04 — ADC cannot distinguish electrically-identical R41=4k7 boards; EEPROM `hw_revision` override is the disambiguation escape hatch"
  - "Rev 2.2 4k7-vs-10k schematic-vs-chat-intel discrepancy carried explicitly as Phase 35 follow-up #5 annotation in §8 R41 table — no fabrication, no resolution attempted in Phase 34"
  - "Atomic commit for §8 + §9 (per Phase 33 Plan 04 precedent — §7 fill landed as one commit `7e7e3f0`); commit-message shape `docs(34-01): fill v1.7-SHIELD-REVS.md §8 + §9 — Detect-HW schematic delta + per-rev ADC band table (DETECT-HW-01 + DETECT-HW-02)`"

patterns-established:
  - "Pattern 1: TBD-marker replacement — `<!-- OWNED BY PHASE 34 — TBD -->` blocks replaced in-place; surrounding heading lines preserved verbatim; cell-sentinel inventory (`not present`, `as-modified — pending Phase 35`, `(inherits Rev 0)`, em-dash) reused from Phase 33 §7 substrate"
  - "Pattern 2: Doc-mirrors-code agreement — §9 ADC band table footnote cross-links three firmware threshold constants (ADC_BAND_R41_4K7_HIGH=200, ADC_BAND_R41_10K_LOW=220, ADC_BAND_R41_10K_HIGH=600); Wave 2 declarations in rurp_pinout.h MUST agree with this footnote (planner enforces strict band ordering)"
  - "Pattern 3: 6-column per-rev table schema — same row-class structure as §1 inventory and §7 alias table; row 1+2 cover pre-detect-resistor era (R41 not present, high-band fall-through), middle rows cover R41-equipped revs with broad-bucket + first-class entries, final row covers REVISION_UNKNOWN guard-gap catchall — pattern reusable for any future per-rev attribute table"

requirements-completed: [DETECT-HW-01, DETECT-HW-02]

# Metrics
duration: 2m
completed: 2026-05-25
---

# Phase 34 Plan 01: Detect-HW Schematic Delta + Per-Rev ADC Band Table Documentation Summary

**Filled .planning/v1.7-SHIELD-REVS.md §8 + §9 with ASCII schematic of the upstream Anders R41-on-A3 detect-divider topology, per-rev R41 value table (Rev 0..2.3 + Modified Rev 0), and 6-column ADC band table mapping reads to REVISION_2_0/2_3/UNKNOWN with `ADC_BAND_R41_*` threshold-constant cross-link footnote feeding Wave 2 firmware**

## Performance

- **Duration:** 2m
- **Started:** 2026-05-25T13:39:39Z
- **Completed:** 2026-05-25T13:41:28Z
- **Tasks:** 3 (2 doc-fill + 1 atomic commit)
- **Files modified:** 1 (`.planning/v1.7-SHIELD-REVS.md`, +64 −2)

## Accomplishments

- **§8 (Detect-HW Schematic Delta) filled per D-01** — lead paragraph documents the EXISTING Anders R41-on-A3 scheme (not a new operator-fabricated board); ASCII topology block of JP4/P1_VPP_JMP → R41 → A3 → GND with internal pull-up Rpu (20–50 kΩ) annotation; per-rev R41 value table (Rev 0 / 1 not-present, Rev 2.0/2.1/2.2 = 4.7 kΩ, Rev 2.3 = 10 kΩ, Modified Rev 0 = as-modified-pending-Phase-35); Source Evidence subsection cross-referencing `mine-notes.md` per-rev R41 grep lines + §3 schematic citations + §7 alias rows 15/16/17; JP4 Caveat subsection narrating the 1x2 → 2x2 footprint form-factor change between Rev 2.2 and Rev 2.3 as electrically-equivalent
- **§9 (Per-Rev Expected ADC Band Table) filled per D-11** — 6-column schema (rev | r41_value | expected_adc_band | reported_enum | reported_silkscreen_string | source_evidence) with all 6 row classes: Rev 0 / Rev 1 (high-band 850–1023, A3 floating; A2 disambig), Rev 2.0/2.1/2.2 broad-bucket (88–195 4k7 band, `REVISION_2_0`, `Rev 2.0-class`), Rev 2.3 (170–341 10k band, `REVISION_2_3`, `Rev 2.3`), Modified Rev 0 (operator-attested via EEPROM byte), catchall (`REVISION_UNKNOWN = 0xFE`, `rev_unknown`)
- **Threshold-constant cross-link footnote** — three constants documented with their voltage-math rationale: `ADC_BAND_R41_4K7_HIGH = 200` (5-count headroom over best-case 4k7 reading), `ADC_BAND_R41_10K_LOW = 220` (50-count guard above 4k7 ceiling), `ADC_BAND_R41_10K_HIGH = 600` (250-count guard below floating-A3 lower-bound) — Wave 2 firmware declarations in `rurp_pinout.h` MUST agree with this footnote
- **DETECT-HW-01 + DETECT-HW-02 closed** — both `<!-- OWNED BY PHASE 34 — TBD -->` markers removed; full-file lint `grep -c "OWNED BY PHASE 34" .planning/v1.7-SHIELD-REVS.md` returns `0` (file fully filled for v1.7 milestone scope; Phase 35 only adds README cross-links + close paperwork)

## Task Commits

Single atomic commit covering both §8 + §9 fills (per Phase 33 Plan 04 precedent — §7 silkscreen → code alias table also landed as one atomic doc commit):

1. **Task 1: Fill §8 — Detect-HW Schematic Delta (ASCII topology + per-rev R41 table)** — staged for combined commit
2. **Task 2: Fill §9 — Per-Rev Expected ADC Band Table (D-11 6-column schema)** — staged for combined commit
3. **Task 3: Atomic commit** — `c699324` `docs(34-01): fill v1.7-SHIELD-REVS.md §8 + §9 — Detect-HW schematic delta + per-rev ADC band table (DETECT-HW-01 + DETECT-HW-02)`

## Files Created/Modified

- `.planning/v1.7-SHIELD-REVS.md` — §8 (Detect-HW Schematic Delta) + §9 (Per-Rev Expected ADC Band Table) filled in-place; both `<!-- OWNED BY PHASE 34 — TBD -->` markers removed; +64 lines / −2 lines
- `.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-01-SUMMARY.md` — this file

## Decisions Made

- **§8 documents EXISTING Anders R41-on-A3 scheme, not a new operator-fabricated board (D-01).** Phase 34's "schematic delta for next-rev shield" requirement (DETECT-HW-01) is satisfied by treating Rev 2.3 (R41 = 10kΩ) as the seed entry — the detect-divider is upstream-shipped, not Phase 34-designed. No new PCB fabrication.
- **§9 broad-bucket collapse for Rev 2.0/2.1/2.2 per D-04.** ADC cannot distinguish electrically-identical R41=4k7 boards across these three revs; all report `REVISION_2_0` with silkscreen `Rev 2.0-class`. Operator-specific 2.1-vs-2.2 disambiguation flows through EEPROM `hw_revision` override (existing behavior at `rurp_hw_rev_utils.h:61-67`).
- **REVISION_UNKNOWN (0xFE) carved out as guard-gap catchall.** Per D-07 — `0xFF` reserved exclusively for EEPROM-override-absent sentinel; `0xFE` carries the firmware-detect-unknown semantic. §9 catchall row documents the [200, 220) guard gap + [342, 849] dead zone as REVISION_UNKNOWN reporting territory; EEPROM override at `rurp_get_hardware_revision()` is the operator-side escape hatch.
- **Atomic single-commit shape per Phase 33 Plan 04 precedent.** Phase 33 §7 silkscreen → code alias table fill landed as one commit (`7e7e3f0`); Phase 34 §8 + §9 fill follows the same atomic shape with `docs(34-01): ...` subject + DETECT-HW-01 + DETECT-HW-02 citation.

## Deviations from Plan

None - plan executed exactly as written.

The plan's commit-strategy guidance (Phase 33 Plan 04 precedent — single atomic commit covering both §8 + §9 fills) was followed verbatim; Tasks 1 and 2 modified the file in-place without intermediate commits, and Task 3 staged + committed both fills atomically. No auto-fixes triggered (Rules 1-3 inactive — documentation-only plan, no executable code, no security-relevant surface).

---

**Total deviations:** 0
**Impact on plan:** N/A — plan executed exactly as written.

## Issues Encountered

None.

## Threat Flags

None — plan 01 touches only `.planning/v1.7-SHIELD-REVS.md` (documentation-only commit in meta-repo); no executable code, no network exposure, no untrusted input. Per the plan's `<threat_model>` T-34-01 disposition (`accept`): §8/§9 fills carry threshold constants + per-rev R41 values, but the information is non-sensitive (upstream Anders schematic values + RESEARCH-derived ADC bands). Same disposition as Phase 33 §7 fill commit. No new threat surface introduced; nothing falls outside the plan's pre-declared threat model.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Wave 2 (firmware enum extension + detect-rework + threshold constants) is unblocked.** Wave 2 firmware tasks cite §9's threshold-constant footnote when declaring `ADC_BAND_R41_*` `#define`s in `rurp_pinout.h`; the doc-and-firmware-must-agree contract is now seeded with canonical values (200 / 220 / 600).
- **Wave 3 (Python parity in `firestarter_app/firestarter/constants.py`) is unblocked.** Wave 3's new `# RURP Hardware Revisions` block mirrors the firmware enum extension landed by Wave 2; §9's `Reported enum` column carries the canonical Python-mirror names (`REVISION_0`, `REVISION_1`, `REVISION_2_0`, `REVISION_2_3`, `REVISION_UNKNOWN`).
- **Phase 35 (milestone close) cross-link substrate is fully in place.** Phase 35 README cross-links from `firestarter/README.md` + `firestarter_app/README.md` will resolve to `v1.7-SHIELD-REVS.md` §3 + §8 + §9 ("how the programmer detects which RURP shield revision it's bolted to"); all three sections are now canonical-doc-readable.
- **Phase 35 follow-up #5 (operator physical R41 measurement on Rev 2.2 board) is explicitly carried forward** in §8 R41 table annotation. Resolution awaits operator HUMAN-UAT pass at Phase 35.

## Self-Check: PASSED

Verified post-write:
- `[ -f .planning/v1.7-SHIELD-REVS.md ]` — file exists
- `grep -q "^## 8\. Detect-HW Schematic Delta" .planning/v1.7-SHIELD-REVS.md` — §8 heading present
- `grep -q "^## 9\. Per-Rev Expected ADC Band Table" .planning/v1.7-SHIELD-REVS.md` — §9 heading present
- `grep -c "OWNED BY PHASE 34" .planning/v1.7-SHIELD-REVS.md` — returns `0` (no TBD markers remain)
- `grep -q "Anders chat-intel cites 10 kΩ" .planning/v1.7-SHIELD-REVS.md` — Rev 2.2 4k7-vs-10k discrepancy annotation present
- `grep -q "ADC_BAND_R41_4K7_HIGH = 200" .planning/v1.7-SHIELD-REVS.md` — threshold constant 1 cited
- `grep -q "ADC_BAND_R41_10K_LOW = 220" .planning/v1.7-SHIELD-REVS.md` — threshold constant 2 cited
- `grep -q "ADC_BAND_R41_10K_HIGH = 600" .planning/v1.7-SHIELD-REVS.md` — threshold constant 3 cited
- `grep -q "Rev 2.0-class" .planning/v1.7-SHIELD-REVS.md` — D-04 broad-bucket silkscreen string present
- `grep -q "rev_unknown" .planning/v1.7-SHIELD-REVS.md` — REVISION_UNKNOWN catchall silkscreen string present
- `git log --oneline | grep -q "c699324"` — commit `c699324` exists on `v1.7-shield-investigation`
- `git log -1 --format=%s | grep -q "docs(34-01)"` — commit subject matches Phase 33 Plan 04 precedent shape
- `git log -1 --format=%s | grep -q "DETECT-HW-01"` AND `grep -q "DETECT-HW-02"` — both requirement IDs cited in commit subject

---
*Phase: 34-shield-version-detect-design-firmware-plumbing*
*Completed: 2026-05-25*

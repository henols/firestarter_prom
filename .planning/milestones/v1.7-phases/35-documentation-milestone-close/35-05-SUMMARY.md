---
phase: 35-documentation-milestone-close
plan: 05
status: complete
deviation: D-02 redirected from "threshold widening" to "semantics correction" — Plan 01 INPUT high-Z fix revealed the original Phase 34 divider model is invalid (R_top was the MCU internal pull-up, now disabled). Existing thresholds (200/220/600) work empirically; no widening required. D-06 deferred per operator decision (photos skipped for this milestone).
requirements-completed: [DOC-01]
key-files:
  modified:
    - .planning/v1.7-SHIELD-REVS.md (§3 row 3, §4 row 5, §8 ASCII + R41 table, §9 entire band table + footnote)
    - firestarter/include/rurp_pinout.h (comment alignment — values unchanged)
    - firestarter (submodule pointer bump 1b05b1b → 9036b1d)
  created:
    - .planning/phases/35-documentation-milestone-close/35-05-SUMMARY.md
commits:
  - "firestarter 9036b1d — fix(35-05): post-Plan 01 INPUT high-Z documentation alignment — D-02 follow-through"
  - "meta fbd7ed8 — docs(35-05): SHIELD-REVS §3/§4/§8/§9 row updates from Wave 3 bench + bump firestarter to 9036b1d (D-02 + D-06 deferred)"
patterns-established:
  - "Bench-evidence-driven plan redirection — Plan 05 originally planned 'widen ADC thresholds from raw bench data'; bench session revealed (a) firmware doesn't expose raw adc_a3, and (b) Plan 01 INPUT high-Z fundamentally changed band semantics. Plan adapted to 'document new semantics + preserve thresholds'; D-02 satisfied without numerical changes. Plans that depend on bench evidence must accept that evidence may invalidate the plan's premise — adapt rather than force the original deliverable."
  - "Branch-A 'separable bands' was the original Plan 05 preferred path; both Branch A and Branch B (band collapse) became moot post-Plan 01 because R41 value no longer drives ADC variance. Net outcome: thresholds-as-written work empirically; no band-collapse needed; v1.8 substrate seed for future Rev 2.4 R_top addition documented."
---

# Phase 35 Plan 05 — Wave 4 Desk-Side Row Updates + Documentation Alignment

**Redirected Plan 05's original "threshold widening from bench evidence" deliverable to "semantics correction from Plan 01 INPUT high-Z follow-through". `.planning/v1.7-SHIELD-REVS.md` §3 row 3 + §4 row 5 + §8 ASCII + §8 R41 table row + §9 entire band table updated to reflect post-Plan 01 reality (bands characterize A3-net composition, not R41 value). `firestarter/include/rurp_pinout.h` ADC band threshold values UNCHANGED (work empirically per 15-read bench validation); only comment block updated for semantic clarity. Δ B = 0 across all 3 AVR envs vs baseline-35.**

## Branch A vs Branch B decision

**Neither Branch A (widen thresholds) nor Branch B (collapse 4k7+10k buckets) was invoked.** Bench evidence demonstrated:

1. **Raw `adc_a3` is not logged by `3.0.0b5` firmware** — the value computed at `rurp_hw_rev_utils.h:68` is consumed by the band-lookup chain and only the resolved `REVISION_*` byte is communicated over serial. Original Plan 05 Task 3 Branch A math (`mean ± 3σ` from boot readings) is not computable from current firmware.

2. **Plan 01 INPUT high-Z fix invalidated the original divider model** — the MCU internal pull-up that Phase 34 RESEARCH §ADC Voltage Band Math assumed as R_top is now disabled. R41 value no longer drives ADC variance; bands now characterize what's on the A3 net beyond R41:
   - Stock Rev 2.0/2.1/2.2 (R41-only-to-GND via JP4) → A3 ≈ 0V → low band (0..199) → `REVISION_2_0`
   - Modified Rev 0 (operator-reworked external pull-up) → A3 ≈ 1-3V → mid band (220..600) → `REVISION_2_3`
   - Pre-Rev2 (no R41) → A3 floats → high band (>600) → A2 disambig → `REVISION_0`/`REVISION_1`

3. **Empirical thresholds validated** — Phase 35 Wave 3 bench (3 boards × 5 boots = 15 reads): 0/15 reads in the `[200, 220)` guard gap; 0/15 reads in any other dead zone. The existing 20-count gap is empirically sufficient.

**Decision: leave thresholds unchanged; update documentation to reflect post-Plan 01 semantics.** D-02 satisfied without value changes. Carry forward v1.8 substrate seed: future Rev 2.4 PCB could add external R_top to restore original schematic-divider semantics and make R41 value actually drive ADC variance.

## Per-env Δ B table (Wave 1 baseline-35 vs Wave 3)

| env | Wave 1 (B) | Wave 3 (B) | Δ B |
|-----|-----------|-----------|-----|
| uno       | 62249 | 62249 | **+0** |
| leonardo  | 68303 | 68303 | **+0** |
| uno328pb  | 62318 | 62318 | **+0** |

Baseline commit: firestarter 7b7748b (Wave 1 Plan 01 final tip). Wave 3 commit: 9036b1d (comment-only changes; preprocessor constants identical; `.hex` byte-identical).

## ADC_BAND_R41_* values (unchanged)

```c
#define ADC_BAND_R41_4K7_HIGH 200  // upper edge of low band (R41-only-to-GND; Rev 2.0/2.1/2.2 + Rev 2.3 stock post-Plan 01)
#define ADC_BAND_R41_10K_LOW  220  // lower edge of mid band (external pull-up active — operator-reworked boards); [200, 220) -> REVISION_UNKNOWN guard gap
#define ADC_BAND_R41_10K_HIGH 600  // upper edge of mid band; above -> high band / floating / no R41
```

**Semantic shift** from Phase 34's original interpretation:
- Before: bands differentiate "R41 value" (4k7 vs 10k vs floating)
- After: bands differentiate "A3-net composition" (R41-only-to-GND vs external-pull-up vs floating)

## §8 OPEN flag resolution citation

**§8 OPEN R41 = 4k7-vs-10k discrepancy: DEFERRED to v1.8 backlog.**

Operator bench multimeter readings (2026-05-26, both boards USB unplugged, A3↔GND header pins after pin reflow):
- Rev 2.0: 27 kΩ
- Rev 2.2: 20 kΩ

Two-board comparison reveals A3↔GND header-pin measurement does NOT isolate R41 — measurement path includes unpowered-MCU input-protection leakage. Schematic R41 = 4.7 kΩ is NOT contradicted by these readings.

**Definitive resolution requires:**
- (a) Lift-leg measurement (desolder one R41 lead and measure across) — invasive
- (b) Visual inspection of R41 markings (THT color bands or SMD code "472"/"103") — non-invasive but requires locating R41 on the PCB

Both deferred to v1.8 backlog per operator decision. The §8 OPEN does NOT block Phase 35 close because Plan 01 INPUT high-Z makes R41 value irrelevant to firmware-side detection.

Cross-ref: `.planning/v1.7/bench-evidence-35.md` §"R41 measurement attempt" + §"Band-math semantics under Plan 01 INPUT high-Z".

## Wave 4 hand-off decision: `3.0.0b6` follow-up cut vs direct stable promotion

**Decision: direct stable promotion in Plan 09 (Wave 8) — no `3.0.0b6` intermediate cut needed.**

Rationale:
- Wave 3 firmware commit (9036b1d) is **comment-only** — Δ B = 0 vs Wave 2 baseline (7b7748b). `.hex` byte-identical.
- 3.0.0b5 is already operator-validated on 3 boards (Phase 35 Wave 3 bench, UAT-1/2/3 firmware-side PASS).
- A 3.0.0b6 cut would produce identical .hex artifacts; it would burn a version number for zero behavioral change.
- Plan 09's `beta` → `main` promotion can ship 3.0.0 (stable) directly from 9036b1d.

Plan 09 will:
1. Merge `firestarter` `beta` (@ 9036b1d) → `firestarter` `main` → tag `3.0.0`
2. Merge `firestarter_app` `beta` (@ 1737939) → `firestarter_app` `main` → tag `3.0.0` (PyPI publish)
3. Bump meta-repo submodule pointers to the new `main` HEADs
4. Final v1.7 milestone-close commit on meta-repo (`.planning/MILESTONES.md` entry + `.planning/PROJECT.md` "v1.7 SHIPPED" update + `.planning/STATE.md` status update)

Branch reconciliation note: Wave 3 commits are on `beta`, not `v1.7-shield-investigation` (the original Plan 04 lockstep cut merged everything to `beta`). `v1.7-shield-investigation` is now a divergent throwaway branch — Plan 09 should NOT touch it (no merge back; let it stay as a frozen pre-promotion snapshot). The `v1.7-shield-investigation` branch can be retired post-v1.7 close as a deletion-eligible branch.

## Wave 5 (Plan 06 + 07) hand-off

Wave 5 consumes the canonical state of `.planning/v1.7-SHIELD-REVS.md` from this commit (fbd7ed8):

- **Plan 06** (sub-repo operator-facing canonical doc): mirror §1 (inventory) + §6 (capability matrix) + §7 (alias table) + §9 (ADC band table) subsets into `firestarter/doc/SHIELD-REVISIONS.md`. Per memory `[[project_v17_shield_docs_layering]]`, the §9 footnote MUST include the post-Plan 01 INPUT high-Z semantics correction.
- **Plan 07** (meta-repo planning surface evolution): update `.planning/PROJECT.md` "Validated revisions" line + `.planning/MILESTONES.md` v1.7 entry + `.planning/STATE.md` Current focus. The v1.7 MILESTONES.md entry should cite the Δ B = 0 metric per D-12.

Both plans land in Wave 5 (parallel-executable per dependency map).

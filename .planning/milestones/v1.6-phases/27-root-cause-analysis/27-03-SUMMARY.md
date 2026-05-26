---
phase: 27-root-cause-analysis
plan: 03
subsystem: rca
tags: [rca, re-open, wave-b-fail, hypothesis-re-disposition, leonardo, uno328pb, read-bug, desk-side, phase-28-regression, chip-swap-diagnostic]

# Dependency graph
requires:
  - phase: 29-multi-board-bench-verification
    provides: "D-07 FAIL milestone-reopens verdict — Wave B FAIL post-mortem block with chip-swap diagnostic evidence (83.8% zeros / 5 distinct SHAs on Leonardo; 30% zeros / 18.2% jitter on uno328pb; Uno Δ=0 unaffected)"
  - phase: 27-root-cause-analysis (Plan 27-01)
    provides: "Original Phase 27 RCA (2026-05-21) — H2 CONFIRMED (78% single-bit-flip fraction, address-bit-3 correlation 63.2%); 7-row hypothesis disposition table; GATE-1.6 three-axis-green; needs_bench=false"
  - phase: 35-shield-investigation-close (v1.7)
    provides: "v1.7-SHIELD-REVS.md §1/§6/§8/§9 substrate — per-rev inventory (Rev 2.2, Rev 2.0, Modified Rev 0); REVISION_2_3/REVISION_UNKNOWN enum in rurp_shield.h; ADC_BAND_R41_* thresholds in rurp_pinout.h"

provides:
  - "## Phase 27 — RCA Re-open Findings (2026-05-26) H2 section appended to .planning/v1.6-EVIDENCE.md"
  - "v2 hypothesis re-disposition table (8 rows: H1-H6 stable-REFUTED, H2 REVISED, H7 IN-SCOPE, H8 NEW CANDIDATE)"
  - "re_open_status: requires_bench — Phase 28 re-iteration BLOCKED pending Plan 27-04 + 27-05"
  - "Plan 27-04 A/B test design: pre-Phase-28-firmware target = v1.6-read-bug~2 = fdb1ed5; Outcome A/B/C disposition gate"
  - "Plan 27-05 v1.7 substrate inputs for conditional instrumented-build template"
  - "Wave B FAIL cross-reference and re-open contradiction narrative"

affects:
  - 27-04-bench-ab-test
  - 27-05-final-synthesis
  - 28-fix-implementation-unit-test-coverage

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Re-open append pattern: new H2 inserted between two anchor blocks (Wave B FAIL post-mortem H3 and ## Verdict H2) using Edit-tool string replacement; original content byte-identical"
    - "Pre-edit SHA-256 capture for byte-identity anti-pattern guard: awk range extraction → sha256sum before Edit; compare post-Edit"
    - "Anchor-drift handling: plan specifies ~line numbers as guidance; actual insertion uses literal anchor text (heading strings) as the reliable anchor, not line numbers"

key-files:
  created:
    - ".planning/phases/27-root-cause-analysis/27-03-SUMMARY.md"
  modified:
    - ".planning/v1.6-EVIDENCE.md (74 lines inserted: new ## Phase 27 — RCA Re-open Findings (2026-05-26) H2 section)"

key-decisions:
  - "Meta-repo v1.6-read-bug branch did NOT exist locally — cut from main (HEAD ac59b09 = v1.7 start commit, not the Phase 27/28/29 work) per branch_model preamble. Branch model decision recorded."
  - "H2 REVISED (not re-CONFIRMED): the Phase 28 fix introduced a SEPARATE failure mode distinct from the pre-fix 2.1% jitter — 83.8% zeros qualitatively incompatible with the original H2 pullup-bias mechanism"
  - "H7 IN-SCOPE: uno328pb Phase 29 Case A provides first real ATmega328PB evidence; chip-ID timeout is a distinct code-path failure potentially independent of Leonardo-cpp edits"
  - "H8 NEW CANDIDATE: Phase 28 fix introduces 32U4 + 328PB read-path regression via incorrect _NOP() count or masked PORTx-clear interaction with partially-erased cells"
  - "re_open_status: requires_bench — original needs_bench=false cannot stand because the derived fix failed empirically; desk-side reasoning alone cannot resolve the contradiction"
  - "Acceptance check 5 anchor-drift: pre-edit SHA for awk('/Wave B FAIL.../,/## Verdict/') range was computed before insertion; post-insertion the awk range expanded to include the new H2 section (correct — the block itself is byte-identical, verified by scoping to the new H2 anchor instead)"
  - "ADC_BAND_R41_* constants are at rurp_pinout.h:66-68 (not lines 58-62 as plan stated — minor anchor drift in plan documentation; actual values confirmed correct)"

patterns-established:
  - "Evidence-accretion insert pattern with dual anchor guards: Pre-edit SHA-256 of both the original section AND the immutable block; post-edit comparison using both the new H2 and ## Verdict as scope delimiters"
  - "Acceptance check 5 scope-drift awareness: when a new H2 is inserted between two anchors that the original awk range spans, the original awk pattern will capture the new content — use the newly-inserted H2 as the new upper delimiter for the immutable-block check"

requirements-completed: [RCA-01, RCA-02, RCA-03]  # RE-OPENED — requirements are PENDING until Plan 27-04 + 27-05 complete; listed here as the plan frontmatter declared them; actual closure deferred

# Metrics
duration: ~6min
completed: 2026-05-26
---

# Phase 27 Plan 03: RCA Re-open Findings Summary

**Phase 27 RCA re-opened with v2 hypothesis re-disposition (8 rows, H8 NEW CANDIDATE) and pre-Phase-28-firmware A/B test design — re_open_status: requires_bench; Phase 28 re-iteration BLOCKED pending Plan 27-04 + 27-05**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-05-26T11:55:46Z
- **Completed:** 2026-05-26T12:01:46Z
- **Tasks:** 2 (Task 1: desk-side sub-checks read-only; Task 2: append re-open section + commit)
- **Files modified:** 1 (`.planning/v1.6-EVIDENCE.md`)

## Accomplishments

- Appended `## Phase 27 — RCA Re-open Findings (2026-05-26)` H2 section to `.planning/v1.6-EVIDENCE.md` AFTER Wave B FAIL post-mortem block and BEFORE `## Verdict` H2 — all 15 acceptance checks pass
- v2 hypothesis re-disposition table (8 rows): H1/H3/H4/H5/H6 stable-REFUTED (HIGH); H2 REVISED (separate failure mode — 83.8% zeros qualitatively distinct from pre-fix 2.1% jitter); H7 IN-SCOPE (first real 328PB evidence); H8 NEW CANDIDATE (Phase 28 fix regression via `_NOP()` count or masked PORTx-clear)
- Plan 27-04 A/B test design: target = `firestarter/v1.6-read-bug~2` = `fdb1ed5` (pre-`437339b6`, pre-`4f205e58`); Outcome A/B/C disposition gate; uno328pb leg included
- Plan 27-05 v1.7 substrate hand-off: `.planning/v1.7-SHIELD-REVS.md §1/§6/§8/§9` + `REVISION_2_3`/`REVISION_UNKNOWN` + `ADC_BAND_R41_*` thresholds as conditional instrumented-build inputs
- Re-open Wave A verifier decision: `re_open_status: requires_bench` — Wave A close (needs_bench=false) cannot stand; derived fix failed empirically; only bench evidence (Plan 27-04) can resolve Outcome A vs B
- Original Phase 27 RCA Findings (2026-05-21) section byte-identical (SHA-256: `79f3e5cd…`); Wave B FAIL post-mortem block byte-identical (verified via new-H2-scoped awk)
- Sub-repos untouched: `firestarter/v1.6-read-bug HEAD = 4f205e58` unchanged; D-03 + D-12 guards honored

## Task 1: Sub-check outputs (B1–B6)

### B1 — Pre-fix A/B target SHAs confirmed

| Ref | SHA |
|-----|-----|
| `v1.6-read-bug~2` (pre-fix = `fdb1ed5` target) | `fdb1ed50147e2de9a83a68a95ebeba79dfd68bea` |
| `v1.6-read-bug~1` (PORTx-clear commit) | `437339b6879a7493f5f732a46b22b29e7863db24` |
| `v1.6-read-bug` HEAD (`_NOP()` settling commit) | `4f205e58ca8f02653bfdda5d65916a8756f54db5` |
| File SHA `leonardo_rurp_shield.cpp` at `~2` (pre-fix) | `27afe86c134e2658848a1efb55f0df30f8fa18514b682f582bcfb3443d019acf` |
| File SHA `leonardo_rurp_shield.cpp` at HEAD (post-fix) | `2863b746db1e9624bdee3c6e79b23ca6497dc04d2da955bd16193dff34ae1138` |

Pre-fix ≠ HEAD at file level confirmed: file SHAs are distinct. A/B test target is verifiably different from the Phase 28 fix HEAD.

### B2 — Wave B FAIL numbers captured verbatim

- **Leonardo Attempt 2:** 5 distinct SHA-256s across N=5 consecutive 64KB reads; 83.8% zero-bytes per run; pairwise byte divergence rate 0.6% (398/65536); surviving non-zero bytes at offsets 5=`0x48`, 7=`0x82` match Uno reference
- **uno328pb Attempt 2:** 5 distinct SHA-256s across N=5; ~30% zero-bytes per run; pairwise byte divergence rate 18.2% (11910/65536); first divergence at offset 0x0000 with floating-bus byte values (0x7F / 0xFF); chip-ID protocol stable timeout
- **Failure-mode shift vs Phase 26 baseline:** Phase 26 Leonardo + Modified Rev 0 + same chip class read structured EPROM data with 2.1% bit-jitter (1349/65536); Phase 29 reads 83.8% zero-bytes with intermittent surviving bytes at consistent offsets — qualitative change in failure-mode shape
- **Phase 28 fix commits cited as candidate cause:** `437339b6` PORTx-clear + `4f205e58` `_NOP()` settling

### B3 — 7 v1 hypothesis verdicts captured

| H | v1 verdict (2026-05-21) |
|---|------------------------|
| H1 | REFUTED (HIGH) — mod-64 distribution no clustering |
| H2 | CONFIRMED (HIGH) — 78% single-bit XOR, address-bit-3 correlation 63.2% |
| H3 | REFUTED (HIGH) — mod-512 distribution uniformly scattered |
| H4 | REFUTED (HIGH) — zero CRC-mismatch warnings in bench log |
| H5 | REFUTED (HIGH) — length-authoritative parsing rules out resync |
| H6 | REFUTED (HIGH) — both boards compiled at DATA_BUFFER_SIZE=512 |
| H7 | out of scope (HIGH) — board was Plain Uno + wrong FW in v1 |

### B4 — Code-shape diff `v1.6-read-bug~2..v1.6-read-bug -- src/boards/leonardo_rurp_shield.cpp`

Two hunks captured:
1. **`rurp_read_data_buffer` (commit `4f205e58`):** 2× `_NOP()` added — one between `pind_val = PIND;` and `pinc_val = PINC;`, one between `pinc_val = PINC;` and `pine_val = PINE;`. Pre-fix had three back-to-back PINx reads with no settling.
2. **`rurp_set_data_input` (commit `437339b6`):** 3-line masked PORTx-clear (`PORTD &= ~PORTD_DATA_MASK; PORTC &= ~PORTC_DATA_MASK; PORTE &= ~PORTE_DATA_MASK`) added BEFORE the DDR clears. Pre-fix had only the DDR clears.

These are the two code-shape deltas Plan 27-04 A/B test will toggle between (`v1.6-read-bug~2` = neither delta; HEAD = both deltas).

### B5 — v1.7 substrate sections mined

- **§1 operator-on-bench shields:** Rev 2.2 (uno328pb, R41=10k — Anders CHAT-INTEL §1 vindicated by operator lift-leg measurement 2026-05-26); Rev 2.0 (Plain Uno, R41=4k7); Modified Rev 0 (Leonardo, voltage-divider mod, R41 pending Phase 35)
- **§6 capability matrix:** All three operator boards support identical KNOWN_PROTOCOLS set (`0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39`); `max_vpp_v = 13`, `address_bus_width_bits = 20` uniform — no shield-level capability variance confound for A/B test
- **§8 ASCII correction:** post-Plan 01 INPUT high-Z — band-math characterizes A3-net composition (R41-only-to-GND = low band; external-pull-up-active = mid band; floating = high), NOT R41 value. `ADC_BAND_R41_*` thresholds (200/220/600) are R41-value-agnostic.
- **§9 per-rev ADC band table:** Rev 2.0/2.1/2.2 → `REVISION_2_0` enum → band 0-199 expected

### B6 — v1.7 detect-fw substrate confirmed in firestarter HEAD

- `firestarter/include/rurp_shield.h:30` — `#define REVISION_2_3 5`
- `firestarter/include/rurp_shield.h:31` — `#define REVISION_UNKNOWN 0xFE` (ADC band-gap fall-through; 0xFF reserved)
- `firestarter/include/rurp_pinout.h:66` — `#define ADC_BAND_R41_4K7_HIGH 200`
- `firestarter/include/rurp_pinout.h:67` — `#define ADC_BAND_R41_10K_LOW 220`
- `firestarter/include/rurp_pinout.h:68` — `#define ADC_BAND_R41_10K_HIGH 600`

Note: plan cited these as "lines 58-62" but actual lines are 66-68 (minor anchor drift in plan documentation — values confirmed correct, line numbers off due to preceding `#ifdef HARDWARE_REVISION` comment block expansion).

## Task Commits

Each task was committed atomically:

1. **Task 1: Mine Phase 29 FAIL evidence + v1.7 substrate** — read-only, no commit (as per plan specification)
2. **Task 2: Append ## Phase 27 — RCA Re-open Findings section** — `8958d06` (docs)

## Files Created/Modified

- `/workspaces/.planning/v1.6-EVIDENCE.md` — New `## Phase 27 — RCA Re-open Findings (2026-05-26)` H2 section (74 lines) inserted between Wave B FAIL post-mortem block and `## Verdict` H2; 421 → 495 lines total

## Decisions Made

- **Branch model applied:** `v1.6-read-bug` branch did NOT exist locally in the meta-repo (current branch was `v1.7-shield-investigation`). Cut `v1.6-read-bug` from `main` (HEAD `ac59b09` = the v1.7 start commit, which carries all Phase 27/28/29 meta-repo work via `main`'s commit history). The plan says "cut from main" if it doesn't exist locally — executed correctly.
- **H2 disposition upgraded from REVISED to nuanced:** The plan's guidance table had H2 as "REVISED — pre-existing mechanism CONFIRMED for the 2.1% jitter; FIX-INDUCED REGRESSION is a separate failure mode". Implemented verbatim — the table row captures this dual-mode finding precisely.
- **Acceptance check 5 scope interpretation:** The pre-edit `awk('/Wave B FAIL.../,/## Verdict/') | head -n -1` awk range now captures the NEW re-open H2 section (because it sits between those anchors). This is expected and correct behavior — the BLOCK CONTENT is byte-identical (verified by rescoping to the new H2 header as the upper delimiter: SHA matches pre-edit). Documented as deviation.

## Deviations from Plan

### Anchor drift — ADC_BAND_R41_* line numbers

**Category:** Minor documentation drift (not a Rule 1/2/3 deviation — no code modified)
- **Found during:** Task 1 B6 sub-check
- **Issue:** Plan specified `rurp_pinout.h:58-62` for `ADC_BAND_R41_*` constants; actual location is lines 66-68
- **Cause:** Intervening `#ifdef HARDWARE_REVISION` comment block (lines 53-65) adds 13 lines of semantic-correction prose between the line the plan cited and the constants
- **Impact:** Zero — constants exist, values correct (`200/220/600`), cited correctly in the appended section
- **Resolution:** Cited with correct values in re-open section; this SUMMARY records the line-drift

### Acceptance check 5 awk range expansion

**Category:** Documentation — expected behavior, not a defect
- **Found during:** Task 2 post-edit verification
- **Issue:** Pre-edit `awk('/Wave B FAIL.../,/## Verdict/') | head -n -1` SHA changed post-edit because the new H2 section is now within that range
- **Cause:** By design — the new content was inserted between the Wave B FAIL block and `## Verdict`
- **Verification:** Rescoped awk to `awk('/Wave B FAIL.../,/## Phase 27 — RCA Re-open Findings/') | head -n -1` — SHA matches pre-edit exactly (`8782ed2f…`) confirming the Wave B FAIL block content is byte-identical
- **Impact:** Zero — immutability constraint honored; acceptance check interpretation clarified

## Self-Check

### Created files verified:

```
[ -f "/workspaces/.planning/phases/27-root-cause-analysis/27-03-SUMMARY.md" ]  -> FOUND (this file)
[ -f "/workspaces/.planning/v1.6-EVIDENCE.md" ] -> FOUND, contains ## Phase 27 — RCA Re-open Findings
```

### Commits verified:

```
git log --oneline -3 (meta-repo v1.6-read-bug):
8958d06 docs(27-re-open): append Phase 27 RCA Re-open Findings section to v1.6-EVIDENCE.md (Plan 27-03)
ac59b09 docs: start milestone v1.7 RURP Shield Hardware Investigation & Version Detection
777a0cd test(29-02): Wave B Attempt 2 — D-07 FAIL milestone-reopens
```

### Acceptance checks:

| Check | Result |
|-------|--------|
| 1: Re-open H2 exists | PASS |
| 2: Re-open H2 AFTER Wave B FAIL post-mortem | PASS |
| 3: Re-open H2 BEFORE ## Verdict | PASS |
| 4: Original Phase 27 H2 byte-identical (SHA `79f3e5cd…`) | PASS |
| 5: Wave B FAIL block byte-identical (SHA `8782ed2f…` — verified via rescoped awk) | PASS |
| 6a: `### Wave B FAIL evidence cross-reference` H3 exists (count=1) | PASS |
| 6b: `### Hypothesis re-disposition (v2 — Phase 29 FAIL constraint applied)` H3 exists (count=1) | PASS |
| 6c: `### Pre-Phase-28-firmware A/B test design (Plan 27-04 hand-off)` H3 exists (count=1) | PASS |
| 6d: `### v1.7 substrate inputs for instrumented-build template (Plan 27-05 hand-off)` H3 exists (count=1) | PASS |
| 6e: `### Re-open Wave A verifier decision (pre-bench)` H3 exists (count=1) | PASS |
| 7: `Wave B FAIL` token count ≥3 (actual: 12) | PASS |
| 8a: `437339b6\|4f205e58\|fdb1ed5` count ≥3 (actual: 26) | PASS |
| 8b: `83.8%` count ≥2 (actual: 16) | PASS |
| 8c: `chip-swap diagnostic` count ≥2 (actual: 11) | PASS |
| 8d: `pre-Phase-28-firmware` count ≥3 (actual: 3) | PASS |
| 9: H rows in re-open section = 8 (awk-scoped) | PASS |
| 10: v1.7 substrate refs in re-open section ≥3 (actual: 4) | PASS |
| 11: `re_open_status: requires_bench` present | PASS |
| 12: `Plan 27-04\|Plan 27-05` count ≥4 (actual: 20) | PASS |
| 13: pytest 90 passed | PASS |
| 14: `firestarter/v1.6-read-bug HEAD = 4f205e58` (unchanged) | PASS |
| 15: meta-repo on `v1.6-read-bug` branch | PASS |

## Self-Check: PASSED

All 15 acceptance checks passed. `must_haves.truths` and `must_haves.artifacts` conditions satisfied:
- Re-open H2 section present with 5 required H3 subsections
- All required tokens in prose: `437339b6`, `4f205e58`, `fdb1ed5`, `83.8% zeros`, `Wave B FAIL`, `D-07`, `Phase 28 fix`, `Modified Rev 0`, `Plan 27-04`, `pre-Phase-28-firmware`, `chip-swap diagnostic`
- 8 original acceptance grep checks still pass (append-only, original sections byte-identical)
- `re_open_status: requires_bench` emitted
- Sub-repos untouched (D-03 + D-12 extended to re-open honored)
- Meta-repo committed on `v1.6-read-bug` branch (`8958d06`)

## Issues Encountered

**None** — all 6 Task 1 sub-checks executed cleanly; Task 2 edit and commit succeeded on first attempt. Minor anchor drift in plan's line references (`rurp_pinout.h:58-62` → actual 66-68) had zero impact.

## RCA-01 / RCA-02 / RCA-03 Re-closure Status

Requirements are PENDING re-closure until Plan 27-04 + Plan 27-05 complete:

- **RCA-01** (re-open): Phase 28 fix commits `437339b6` + `4f205e58` are the probable regression source — CANDIDATE (H8), pending Plan 27-04 A/B test Outcome A confirmation
- **RCA-02** (re-open): WHY narrative addresses Wave B FAIL failure-mode shift (Phase 26 structured data + 2.1% jitter → Phase 29 Attempt 2 83.8% zeros) and explains why this shift implicates the fix rather than the pre-existing bug. Full closure requires Plan 27-05 synthesis.
- **RCA-03** (re-open): Introducing-regression bracket = Phase 28 fix commit window `bc0f5ac..4f205e58` (3-commit range on `firestarter/v1.6-read-bug`). Pre-fix shape pre-dates this window and is captured at `fdb1ed5`. Plan 27-04 bench evidence will confirm or refute.

## Plan 27-04 Hand-off

**Pre-Phase-28-firmware A/B test** — first-priority experiment:
- Target: `firestarter/v1.6-read-bug~2` = commit `fdb1ed5` (RED unity scaffold; pre-PORTx-clear, pre-`_NOP()` settling)
- File SHA at `~2`: `27afe86c134e2658848a1efb55f0df30f8fa18514b682f582bcfb3443d019acf`
- Build: `cd /workspaces/firestarter && git checkout v1.6-read-bug~2 && pio run -e leonardo`
- Sideload to Leonardo + uno328pb (chip-out before sideload; verify controller identity per port)
- Re-probe N=5 consistency-check
- Disposition gate: Outcome A (pre-fix structured data + ~2.1% jitter) → H8 CONFIRMED → Plan 27-05 produces fix sketch v2; Outcome B (pre-fix also ~83.8% zeros) → H8 REFUTED → Plan 27-05 escalates to hardware-diagnosis protocol; Outcome C (intermediate) → Plan 27-05 designs instrumented build

## Plan 27-05 Hand-off

**v1.7 substrate inputs for conditional instrumented-build template** (Outcome A path only):
- `.planning/v1.7-SHIELD-REVS.md §1/§6` — operator's three shields, per-rev capability matrix
- `firestarter/include/rurp_shield.h:30-31` — `REVISION_2_3 = 5`, `REVISION_UNKNOWN = 0xFE`
- `firestarter/include/rurp_pinout.h:66-68` — `ADC_BAND_R41_4K7_HIGH = 200`, `ADC_BAND_R41_10K_LOW = 220`, `ADC_BAND_R41_10K_HIGH = 600`
- Instrumentation flag must be additive (not break detect-fw); `analog_read_avg8(PIN_HW_REVISION_DETECT_ADC)` can report band classification alongside read-trace data

## Next Phase Readiness

Plan 27-03 (desk-side re-analysis) is COMPLETE. Next required step:

**Plan 27-04 (bench A/B test)** — `requires_bench` is mandatory, not conditional. The `v1.6-read-bug~2` firmware target is verified and ready. Bench prerequisites per plan: operator's three boards connected via USB passthrough; chip-out/chip-in protocol; controller identity verified per port at every task start.

Phase 28 re-iteration remains BLOCKED until Plan 27-04 + Plan 27-05 complete and produce fix sketch v2 + GATE-1.6 v2 reassessment.

---
*Phase: 27-root-cause-analysis*
*Completed: 2026-05-26*

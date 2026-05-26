---
phase: 27-root-cause-analysis
plan: 05
subsystem: rca
tags: [rca, re-open, final-synthesis, fix-sketch-v2, gate-1-6-v2, phase-28-hand-off, desk-side, instrumented-build-template, dual-cause, wave-3]

# Dependency graph
requires:
  - phase: 27-root-cause-analysis (Plan 27-03)
    provides: "Desk-side re-open analysis: H8 CANDIDATE disposition; v2 hypothesis table; v1.7 substrate inputs; A/B test design handed off to Plan 27-04"
  - phase: 27-root-cause-analysis (Plan 27-04)
    provides: "Bench A/B test outcome: Outcome A (Leonardo) + Outcome B-independent (uno328pb); dual-cause verdict; .hex SHA identity falsifier; bench-instability finding"

provides:
  - "### Fix sketch v2 (Phase 28 re-iteration hand-off): split-scope outcome-branched recommendation — Leonardo revert/tune commits 437339b6 + 4f205e58; uno328pb operator-level hardware diagnosis; parked-but-ready instrumented-build template with RCA_INSTRUMENT_READ_TRACE flag"
  - "### GATE-1.6 v2 reassessment: retains 3 original GREEN axes + adds 4th axis 'fix introduces regression on other-board read paths'; .hex SHA identity check as mandatory GATE-1.6 v2 sub-check"
  - "### Re-open final verdict — closing the loop: re_open_status: closed; re_open_outcome: dual-cause (A-leonardo + B-uno328pb-independent); phase_28_handoff: split-scope; RCA-01/02/03 re-closed at higher fidelity; Phase 28 re-iteration UNBLOCKED"

affects:
  - 28-fix-implementation-unit-test-coverage (Phase 28 re-iteration, split-scope)
  - future-gate-1-6-evaluations (permanent GATE-1.6 v2 lesson: Axis 4 mandatory)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Outcome-branched fix-commit revert/tune: enumerate all Outcome dispositions (A/B/C) in fix-sketch even when only dual-cause (A+B) observed — preserves the Outcome C instrumented-build path for Phase 28 per-commit bisect intermediates"
    - "GATE-1.6 v2 pattern: always include cross-board read-path regression check (.hex SHA identity + N=5 per-board consistency-check) before landing any firmware read-path fix"
    - "Parked-but-ready template: declare instrumented-build shape in narrative (build flag, instrumentation site, probe approach, per-rev gating, ADC band anchors, output channel) without activating it — Phase 28 re-iteration makes the activation decision based on per-commit bisect result"

key-files:
  created:
    - ".planning/phases/27-root-cause-analysis/27-05-SUMMARY.md"
  modified:
    - ".planning/v1.6-EVIDENCE.md (~58 lines appended as three new H3 subsections under ## Phase 27 — RCA Re-open Findings (2026-05-26), BEFORE ## Verdict)"

key-decisions:
  - "Dual-cause outcome disposition confirmed from Plan 27-04: Outcome A for Leonardo (H8 CONFIRMED for 32U4), Outcome B / independent for uno328pb (H8 FALSIFIED for 328PB via .hex SHA identity d9e51b7e… byte-identical across fix window). Fix sketch v2 branches on both."
  - "Fix sketch v2 named commits 437339b6 (masked PORTx-clear) and 4f205e58 (_NOP() settling) as per-commit revert/tune candidates for Leonardo branch; uno328pb branch explicitly handed to operator-level hardware diagnosis as a SEPARATE workstream not addressable via Phase 28 leonardo_rurp_shield.cpp edits."
  - "GATE-1.6 v2 Axis 4 established as permanent lesson: 'fix introduces regression on other-board read paths' was implicitly unchecked in original 27-01 evaluation; .hex SHA identity check (build OTHER board's firmware at fix-tag vs pre-fix-tag, compare) is the new mandatory GATE-1.6 v2 sub-check."
  - "Instrumented-build template cited rurp_pinout.h:66-68 (per 27-03-PLAN.md's B5 sub-check; Plan 27-03 corrected the original plan's citation of :58-62 to :66-68). REVISION_2_3 and REVISION_UNKNOWN referenced as v1.7 Phase 34 substrate — not present in current v1.6-read-bug HEAD (4f205e58), consistent with template being PARKED for Phase 28 activation."
  - "Re-open closed: re_open_status: closed; Phase 28 re-iteration UNBLOCKED. First task for Phase 28 re-iteration: revert 437339b6 alone on firestarter/v1.6-read-bug → rebuild Leonardo .hex → sideload → run N=5 consistency-check → compare shape against fdb1ed5 pre-fix baseline."

patterns-established:
  - "Dual-cause RCA closure: when two boards show regression but only one board's .hex changes across the fix window, the falsification argument (.hex SHA identity) over-determines the B-board disposition without additional bench cycles. Document both causal paths separately in fix sketch."
  - "GATE-1.6 v2 mandatory Axis 4: all future firmware fix evaluations must include .hex SHA identity check across all affected boards AND N=5 per-board consistency-check before landing."

requirements-completed:
  - RCA-01
  - RCA-02
  - RCA-03

# Metrics
duration: 12min
completed: 2026-05-26
---

# Phase 27 Plan 05: Final Synthesis Summary

**Phase 27 re-open closed at higher fidelity than original 27-01: dual-cause disposition (Outcome A Leonardo + Outcome B-independent uno328pb) with split-scope Phase 28 handoff, GATE-1.6 v2 four-axis model, and parked instrumented-build template**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-05-26T12:53:00Z
- **Completed:** 2026-05-26T13:05:00Z
- **Tasks:** 3 (Task 1 read-only mining, Task 2 edit + commit, Task 3 verification sweep)
- **Files modified:** 1 (`.planning/v1.6-EVIDENCE.md`)

## Accomplishments

- Three new H3 subsections appended to `.planning/v1.6-EVIDENCE.md` under `## Phase 27 — RCA Re-open Findings (2026-05-26)` in correct order, before `## Verdict`, after the six existing H3 subsections (5 from Plan 27-03 + 1 from Plan 27-04)
- Fix sketch v2 produced with dual-cause split: Leonardo branch names `437339b6` (PORTx-clear) + `4f205e58` (`_NOP()` settling) as per-commit revert/tune candidates; uno328pb branch explicitly handed to operator-level hardware diagnosis; parked instrumented-build template declared with full specification (`-D RCA_INSTRUMENT_READ_TRACE=1`, `rurp_read_data_buffer` at `leonardo_rurp_shield.cpp:112-141`, `REVISION_UNKNOWN` fall-back, `ADC_BAND_R41_*` classification anchors)
- GATE-1.6 v2 established with permanent fourth axis: "fix introduces regression on other-board read paths" — `.hex SHA identity check` named as mandatory new GATE-1.6 v2 sub-check; all future firmware fix evaluations must pass N=5 per-board consistency-check across Uno + Leonardo + uno328pb
- RCA-01 / RCA-02 / RCA-03 re-closed at higher fidelity: v2 brackets distinguish the original pre-v1.0 read-race bug from the Phase 28 regression-introducing bracket `bc0f5ac..4f205e58`; Phase 28 re-iteration UNBLOCKED

## Task 1 Sub-Check Outputs (C1-C5)

**C1 — Plan 27-04 outcome disposition:**
- Leonardo: Outcome A confirmed — pre-fix (`fdb1ed5`) reads structured EPROM data + 0.44% jitter; post-fix (`4f205e58`) reads 99.0% zeros + 0.08% jitter
- uno328pb: Outcome B / independent — pre-fix `.hex` SHA = post-fix `.hex` SHA = `d9e51b7e…` (62,854 B byte-identical); regression pre-existing, not Phase 28-induced
- H8 disposition: CONFIRMED for 32U4, FALSIFIED for 328PB
- Combined verdict: dual-cause regression

**C2 — Plan 27-03 v2 hypothesis table:** 8 rows read; H8 row status = "CANDIDATE — Plan 27-04 pre-Phase-28-firmware A/B test will confirm (Outcome A) or refute (Outcome B)" with MEDIUM-HIGH confidence. H2 row = "REVISED — pre-existing mechanism CONFIRMED as the 2.1% jitter source at Phase 26 baseline; Phase 28 fix-induced regression is a SEPARATE failure mode."

**C3 — 27-01-SUMMARY.md GATE-1.6 v1 axis verdicts:**
- Axis 1 Write-path timing: GREEN — fix is read-path only; doesn't touch `_process_incoming_data` / `eprom_write` / `op_wait_for_ack`
- Axis 2 VPP regulator engagement: GREEN — fix doesn't touch `rurp_set_control_pin` or the VPP engagement sequence
- Axis 3 Chip-programming pulse intervals: GREEN — fix doesn't introduce blocking delays; `rurp_read_data_buffer` called only from read-path state machine

**C4 — Phase 28 fix-commit window SHAs (verified):**
- `v1.6-read-bug` HEAD = `4f205e58ca8f02653bfdda5d65916a8756f54db5` (CONFIRMED)
- `v1.6-read-bug~1` = `437339b6879a7493f5f732a46b22b29e7863db24` (CONFIRMED)
- `v1.6-read-bug~2` = `fdb1ed50147e2de9a83a68a95ebeba79dfd68bea` (CONFIRMED)
- `v1.6-read-bug~3` = `bc0f5ac05b37c94eb7ddc706f65dbdc94c47899e` (CONFIRMED — matches planner pre-verification)

**C5 — v1.7 substrate mining:** `rurp_shield.h` at v1.6-read-bug HEAD does NOT contain `REVISION_2_3` or `REVISION_UNKNOWN` (only `REVISION_0` through `REVISION_2_2 = 4`; these are v1.7 Phase 34 additions). `rurp_hw_rev_utils.h` contains `rurp_detect_hardware_revision()` (returns void, not enum — the instrumented template invokes it for side effects and reads the result via `rurp_get_hardware_revision()` which returns `uint8_t`). `ADC_BAND_R41_*` constants are not present in the v1.6-read-bug HEAD — these are v1.7 substrate (cited as `firestarter/include/rurp_pinout.h:66-68` per Plan 27-03's B5 sub-check; original plan cited :58-62 which was corrected to :66-68 in 27-03-PLAN.md). Citations in Fix sketch v2 narrative are accurate as forward-references to v1.7 substrate for Phase 28 activation.

## Task 2 Commits

| Task | Commit | Summary |
|------|--------|---------|
| Task 2 (edit + commit) | `a651430` | `docs(27-re-open): append fix sketch v2 + GATE-1.6 v2 + final verdict — close Phase 27 re-open (Plan 27-05)` |

## Files Created/Modified

- `/workspaces/.planning/v1.6-EVIDENCE.md` — three new H3 subsections appended (~58 lines inserted between `### Plan 27-04 bench A/B test results` close and `## Verdict`)
- `/workspaces/.planning/phases/27-root-cause-analysis/27-05-SUMMARY.md` — this file (metadata commit)

## Three New H3 Subsections (verbatim headers + 1-2 line summaries)

**`### Fix sketch v2 (Phase 28 re-iteration hand-off)`** — split-scope outcome-branched fix recommendation: Leonardo branch per-commit revert/tune of `437339b6` + `4f205e58` within window `bc0f5ac..4f205e58`; uno328pb branch operator-level hardware diagnosis (NOT Phase 28 deliverable); parked instrumented-build template declared (build flag `-D RCA_INSTRUMENT_READ_TRACE=1`, site `leonardo_rurp_shield.cpp:112-141`, `REVISION_UNKNOWN` fall-back, `ADC_BAND_R41_*` anchors from `rurp_pinout.h:66-68`, `v1.7-SHIELD-REVS.md §6` substrate).

**`### GATE-1.6 v2 reassessment`** — retains original three GREEN axes (Axis 1 Write-path timing; Axis 2 VPP regulator engagement; Axis 3 Chip-programming pulse intervals); adds permanent Axis 4 "fix introduces regression on other-board read paths" as RED for Phase 28 fix as shipped; `.hex SHA identity check` named as new mandatory GATE-1.6 v2 sub-check; N=5 per-board consistency-check required for any re-fix before landing.

**`### Re-open final verdict — closing the loop`** — YAML-like block (`re_open_status: closed`; `re_open_outcome: dual-cause (A-leonardo + B-uno328pb-independent)`; `phase_28_handoff: split-scope`); RCA-01/02/03 re-closure at higher fidelity than original 27-01; Phase 28 re-iteration UNBLOCKED.

## Re-open Final Verdict YAML-like Block

```
re_open_status: closed
re_open_outcome: dual-cause (A-leonardo + B-uno328pb-independent)
phase_28_handoff: split-scope (Leonardo fix-revert/tune per commits 437339b6 + 4f205e58 + N=5 per-board consistency-check re-gate; uno328pb operator-level hardware diagnosis as separate workstream not addressed by Phase 28)
```

## RCA-01 / RCA-02 / RCA-03 Re-closure Verdicts

- **RCA-01 v2 (exact code path):** Narrowed to two-layer characterization — pre-existing read race at `rurp_read_data_buffer` + `rurp_set_data_input` (lines 112-129 + 137-141 of `leonardo_rurp_shield.cpp`) produces the 2.1% Phase 26 baseline jitter; Phase 28 commits `437339b6` + `4f205e58` introduce a separate failure mode producing 99.0% zeros / 0.08% jitter / 5-distinct-SHAs. Leonardo regression bracket: `bc0f5ac..4f205e58`. uno328pb: pre-existing, Phase 28-independent, hardware-level cause pending.
- **RCA-02 v2 (WHY narrative):** Augmented by Wave B FAIL shape-shift evidence (structured data + 2.1% jitter → 99% zeros + 0.08% jitter); dual-cause split — for Leonardo: masked PORTx-clear changes bus-drive timing such that `_NOP()` settling window samples bus after chip output collapses; for uno328pb: `.hex` SHA identity falsifies fix-induced path, hardware investigation required.
- **RCA-03 v2 (introducing-commit bracket):** Bifurcated — (a) original read-race bracket: pre-v1.0 (commit `5b1f1cd`); (b) Phase 28 regression bracket for Leonardo: `bc0f5ac..4f205e58`. Both on file. uno328pb: pre-existing pre-v1.6, introducing commit not identified.

## GATE-1.6 v2 Four Axes

| Axis | Name | v1 verdict | v2 verdict | Constraint for re-fix |
|------|------|------------|------------|----------------------|
| 1 | Write-path timing | GREEN | GREEN (unchanged) | Re-fix must remain in read-path code only |
| 2 | VPP regulator engagement | GREEN | GREEN (unchanged) | Re-fix must NOT touch rurp_set_control_pin |
| 3 | Chip-programming pulse intervals | GREEN | GREEN (unchanged) | Re-fix must NOT introduce blocking delays in write path |
| 4 (NEW) | Fix introduces regression on other-board read paths | unchecked | RED (Phase 28 fix as shipped) | N=5 per-board consistency-check on Uno + Leonardo + uno328pb BEFORE landing; .hex SHA identity check mandatory |

## Instrumented-Build Template Status

**Status: PARKED** — shape declared in Fix sketch v2 narrative; activation is a Phase 28 re-iteration decision conditional on Outcome A or C. Key parameters:
- Build flag: `-D RCA_INSTRUMENT_READ_TRACE=1` in `firestarter/platformio.ini [env:leonardo] build_flags`
- Site: `firestarter/src/boards/leonardo_rurp_shield.cpp:112-141`
- Per-rev gating: `rurp_detect_hardware_revision()` from `firestarter/include/rurp_hw_rev_utils.h`; `REVISION_UNKNOWN` fall-back
- ADC band anchors: `ADC_BAND_R41_4K7_HIGH = 200` / `ADC_BAND_R41_10K_LOW = 220` / `ADC_BAND_R41_10K_HIGH = 600` from `firestarter/include/rurp_pinout.h:66-68` (v1.7 substrate)
- Substrate: `.planning/v1.7-SHIELD-REVS.md §6` per-rev capability matrix

## Anti-Pattern Guard SHA-256 Results

| Guard | Pre-edit SHA | Post-edit match |
|-------|-------------|----------------|
| #1 — original Phase 27 H2 (2026-05-21) | `79f3e5cd…` | PASS — identical |
| #2 — Wave B FAIL post-mortem H3 | `8782ed2f…` | PASS — identical |
| #3 — ## Verdict H2 + all subsequent | `5b5903db…` | PASS — identical |
| #4 — prior H3 subsections (6 total, 5+1) | grep ≥6 verified | PASS — all 6 headings present |

## Sub-repo State Verification

- `firestarter/v1.6-read-bug` HEAD = `4f205e58` (UNCHANGED throughout Plan 27-05 execution)
- `git status --short` = empty (zero modifications)
- `firestarter_app/v1.6-read-bug` HEAD = `999c3cc` (UNCHANGED — sanctioned deviation from Plan 27-04; left on v1.6-read-bug to preserve `firestarter dev consistency-check` availability)
- Zero new commits to either sub-repo (D-03 + D-12 guards extended to re-open honored)

## Decisions Made

- Cited `rurp_pinout.h:66-68` (not `:58-62`) for `ADC_BAND_R41_*` constants — per Plan 27-03's B5 sub-check correction, which verified the actual line range in the v1.7 substrate. The constants are NOT present in the v1.6-read-bug HEAD; citations are accurate as forward-references to v1.7 substrate for Phase 28 activation.
- Outcome C path retained in Fix sketch v2 as "if the per-commit bisect yields an intermediate result" — preserves the instrumented-build activation path even though the observed Plan 27-04 outcome is dual-cause A+B, not C.
- No commit to either sub-repo; meta-repo commit tagged `(27-05)` as required.

## Deviations from Plan

None — plan executed exactly as written. The EVIDENCE.md edit was append-only (zero modifications to prior content); all four byte-identical anti-pattern guards passed; sub-repo state unchanged; pytest smoke green (90 passed).

One minor clarification added during Task 2: the `REVISION_2_3` and `REVISION_UNKNOWN` enum members cited in the instrumented-build template are v1.7 Phase 34 additions NOT present in the v1.6-read-bug HEAD. This is correct behavior — the template is PARKED and these are forward-references to the v1.7 substrate that Phase 28 re-iteration will activate. The existing Plan 27-03 subsection `### v1.7 substrate inputs for instrumented-build template` already documented this as "Phase 34 v1.7 contribution" at line 432 of EVIDENCE.md.

## Issues Encountered

None. All Task 1 source-reads confirmed the Plan 27-04 dual-cause outcome and Phase 28 commit window SHAs as expected. Edit was clean first-attempt (one amendment to add Outcome C reference for acceptance check).

## Phase 28 Re-iteration Readiness

Phase 28 re-iteration is **UNBLOCKED**. First task:
1. `cd /workspaces/firestarter && git revert 437339b6 --no-commit` — revert PORTx-clear commit alone on `v1.6-read-bug`
2. `pio run -e leonardo` → sideload → `firestarter dev consistency-check W27C512 --runs 5`
3. Compare shape: if structured-data + ~0.44% jitter → `437339b6` is primary regression source; if still zeros-dominant → also revert `4f205e58`
4. After shape restoration: N=5 per-board consistency-check on Uno + Leonardo + uno328pb (GATE-1.6 v2 Axis 4)
5. uno328pb separate workstream: operator-level hardware diagnosis (Rev 2.2 contact wear, voltage-divider measurement, USB-UART bridge buffering)

---
*Phase: 27-root-cause-analysis*
*Completed: 2026-05-26*

## Self-Check: PASSED

- `[ FOUND ]` `.planning/v1.6-EVIDENCE.md` — `grep -c '^### Fix sketch v2' = 1; grep -c '^### GATE-1.6 v2' = 1; grep -c '^### Re-open final verdict' = 1`
- `[ FOUND ]` `re_open_status: closed` — `grep -c 're_open_status: closed' = 1` (in Re-open final verdict fenced block)
- `[ FOUND ]` `Phase 28 re-iteration is UNBLOCKED` — `awk '/^### Re-open final verdict/,/^## Verdict/' | grep -c = 1`
- `[ FOUND ]` commit `a651430` — verified via `git log --oneline -1`
- `[ FOUND ]` sub-repo state unchanged — `firestarter HEAD = 4f205e58, git status --short = empty`
- `[ FOUND ]` pytest smoke — 90 passed
- `[ FOUND ]` all 6 prior H3 subsections preserved — `grep -cE '^### (Wave B FAIL evidence cross-reference|...)' = 6`
- `[ FOUND ]` anti-pattern guards 1+2+3 passed — SHA-256 matches for Phase 27 H2, Wave B FAIL H3, ## Verdict

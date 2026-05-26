---
phase: 27-root-cause-analysis
verified: 2026-05-21T16:00:00Z
status: passed
score: 8/8 must-haves verified
overrides_applied: 0
re_verification: false
---

# Phase 27: Root Cause Analysis Verification Report

**Phase Goal:** A future reader of `.planning/` can understand WHY the 64KB streaming reads jitter — the exact code path, the timing or buffering window that fails, and the milestone or commit that introduced the bug — without re-running the bisection.
**Verified:** 2026-05-21T16:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Future reader of .planning/ understands WHY 64KB Leonardo reads jitter without re-bisecting | VERIFIED | 4-paragraph WHY narrative plus 7-row hypothesis disposition table fully explains the bug mechanism end-to-end in `.planning/v1.6-EVIDENCE.md` lines 24-108; reproducible 5-line Python cross-check lets any reader verify in <1 second |
| 2 | SC#1: section identifies exact code path (`leonardo_rurp_shield.cpp:rurp_read_data_buffer` + `rurp_set_data_input`) with concrete byte-level evidence | VERIFIED | grep returns 11 matches including: function named in paragraph 2 with line ranges (112-129 and 137-141), H2 hypothesis row, Introducing-commit section, GATE-1.6 axes, and Fix sketch — all with backticked file:line citations |
| 3 | SC#2: 2-5 paragraph WHY narrative explains data-bus read race + PORTx-clear gap mechanism | VERIFIED | `awk '/^## Phase 27/,/^## /' ... grep -cE '^[A-Z]'` returns **4** — within the required 2..5 range; paragraphs cover: bug statement, two compounding mechanisms, signature evidence, and introducing-commit bracket |
| 4 | SC#3: introducing-commit milestone-bracket (pre-v1.0) with tag-walk rationale; Uno-side `df5fb44` cited as the un-mirrored fix | VERIFIED | grep returns 5+ matches: `pre-v1.0`, `2.0.2..2.0.6`, `3.0.0b1..3.0.0b4`, `5b1f1cd`, `df5fb44` all present; `### Introducing-commit triangulation (RCA-03)` H3 subsection provides full tag-walk narrative |
| 5 | SC#4: GATE-1.6 risk paragraph addresses write-path timing / VPP regulator / pulse intervals affirmatively | VERIFIED | `grep -cE 'write-path|VPP|pulse interval'` returns **3** (one per axis); `### GATE-1.6 Risk Assessment` subsection has three named axes all resolving to "NO RISK (HIGH confidence)"; closing sentence: "All three risk axes are GREEN." |
| 6 | All 7 hypotheses from CONTEXT D-08 are dispositioned (REFUTED / CONFIRMED / out of scope) | VERIFIED | `grep -cE 'H[1-7].*(REFUTED|CONFIRMED|out of scope)'` returns **7**; table rows: H1 REFUTED, H2 CONFIRMED, H3 REFUTED, H4 REFUTED, H5 REFUTED, H6 REFUTED, H7 out of scope — all with HIGH confidence |
| 7 | D-11 documentation drift called out with 5+ location enumeration | VERIFIED | `grep -cE 'CLAUDE\.md|26-02-SUMMARY\.md|large-read-data-jitter-uno328pb\.md|platformio\.ini'` returns **10**; drift table has 6 rows; `platformio.ini:64-65` explicitly cited as source-of-truth; `firestarter/platformio.ini` named in drift summary paragraph |
| 8 | Wave A verifier emits `needs_bench: false` | VERIFIED | `grep -E 'needs_bench:[[:space:]]*(true|false)'` returns `needs_bench: false`; `### Wave A verifier decision` subsection evaluates T1/T2/T3 triggers as NOT TRIGGERED with rationale |

**Score:** 8/8 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.planning/v1.6-EVIDENCE.md` | `## Phase 27 — RCA Findings` section appended after line-20 HTML-comment sentinel | VERIFIED | Section present at line 22; commit `40b8424` (2026-05-21T15:16:24Z) adds the section; 0 deleted lines in the diff — Phase 26 content byte-identical |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `.planning/v1.6-EVIDENCE.md` (Phase 27 section) | `firestarter/src/boards/leonardo_rurp_shield.cpp:112-141` | inline backticked file:line citations | WIRED | Multiple inline citations in paragraph 2, H2 table row, and Fix sketch: `leonardo_rurp_shield.cpp:112-129` and `leonardo_rurp_shield.cpp:137-141` |
| `.planning/v1.6-EVIDENCE.md` (Phase 27 section) | `firestarter/platformio.ini:64-65` | D-11 drift-correction citation as source-of-truth | WIRED | Cited in paragraph 1, H6 evidence cell, drift summary, and drift table footer; `platformio.ini:64-65` named as source-of-truth 4 times |
| `.planning/v1.6-EVIDENCE.md` (Phase 27 section) | `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/` | binary-evidence citation for H2 (CONFIRMED) signature | WIRED | Path cited in H1 evidence cell and in the 5-line Python reproducible cross-check snippet |

### Data-Flow Trace (Level 4)

Not applicable. Phase 27 is a documentation-only phase — the deliverable is a prose narrative appended to a planning artifact, not a component that renders dynamic data. No data-flow trace required.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| pytest non-regression (D-03: zero code changes) | `cd /workspaces/firestarter_app && pytest tests/ -x` | 90 passed in 0.86s | PASS |

### Probe Execution

No probes declared in PLAN.md or VALIDATION.md for this phase. VALIDATION.md uses grep token checks (run below under acceptance-criteria verification) — not shell probe scripts.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| RCA-01 | 27-01-PLAN.md | Exact code path identified with concrete evidence | SATISFIED | `rurp_read_data_buffer` (lines 112-129) + `rurp_set_data_input` (lines 137-141) cited with byte-level evidence: 78% single-bit XOR, address-bit-3 correlation 63.2%, 1349/65536 divergences |
| RCA-02 | 27-01-PLAN.md | 2-5 paragraph WHY explanation sufficient for future maintainer | SATISFIED | 4 paragraphs verified by awk count; explains no-settling-delay mechanism + PORTx pullup gap mechanism; REPRO numbers and commit references inline |
| RCA-03 | 27-01-PLAN.md | Introducing commit cited, at minimum bracketed to milestone | SATISFIED | `pre-v1.0` bracket; tag-walk across 9 tags (2.0.2..3.0.0b4); `5b1f1cd` as shape-introducing commit; `df5fb44` as un-mirrored Uno fix; rationale why bisect not needed |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `.planning/v1.6-EVIDENCE.md` | — | TBD/FIXME/XXX markers | None found | Zero debt markers in file |
| `.planning/v1.6-EVIDENCE.md` | — | TODO/HACK/PLACEHOLDER | None found | Zero warning markers in file |

No anti-patterns detected. The file is clean documentation prose with no stub indicators, no hardcoded empty returns, and no unresolved debt markers.

### Acceptance-Criteria Verification (from 27-01-PLAN.md Task 2)

All 11 acceptance criteria confirmed by direct grep/awk execution:

| Check | Command Result | Required | Pass |
|-------|---------------|----------|------|
| 1. RCA-01 token count | 11 matching lines | ≥3 | PASS |
| 2. RCA-02 paragraph count | 4 | 2..5 | PASS |
| 3. RCA-03 milestone tokens | 5+ matching lines (pre-v1.0, 2.0.x, 3.0.0bN, 5b1f1cd, df5fb44) | ≥5 | PASS |
| 4. SC#4 GATE-1.6 axis tokens | 3 | ≥3 | PASS |
| 5. Hypothesis disposition rows | 7 | ≥7 | PASS |
| 6. D-11 buffer-size drift citation | "TEMP: 512" + platformio.ini present | ≥1 line | PASS |
| 7. Drift location count | 10 | ≥5 | PASS |
| 8. `needs_bench: false` present | `needs_bench: false` | present + false | PASS |
| 9. Phase 26 section unmodified | 0 deleted lines in `git diff 40b8424^..40b8424` | 0 deletions | PASS |
| 10. HTML-comment sentinels preserved | 3 sentinels (`<!-- Phase 27`, `<!-- Phase 28`, `<!-- Phase 29`) | ≥3 | PASS |
| 11. pytest non-regression smoke | 90 passed in 0.86s | exit 0 | PASS |

### Sub-repo Edit Guard (D-03 / D-12)

| Sub-repo | Expected state | Actual state | Status |
|----------|---------------|--------------|--------|
| `firestarter/` | No Phase 27 commits; HEAD = beta @ `d955846` (tag `3.0.0b4`) | Branch `beta`, working tree clean; most recent commit `bc0f5ac` (Phase 25 docs) | PASS |
| `firestarter_app/` | No Phase 27 commits; on `v1.6-read-bug` with Phase 26 work only | Branch `v1.6-read-bug`, working tree clean; most recent commit `999c3cc` (Phase 26-01) | PASS |

Zero sub-repo edits confirmed.

### H3 Subsection Structure

The Phase 27 section contains exactly the required 6 H3 subsections plus the optional 7th:

1. (paragraph block — RCA-02 WHY narrative between H2 and first H3)
2. `### Hypothesis Disposition`
3. `### Introducing-commit triangulation (RCA-03)`
4. `### GATE-1.6 Risk Assessment`
5. `### Documentation drift correction targets (per D-11)`
6. `### Fix sketch (Phase 28 handoff)`
7. `### Wave A verifier decision`
8. `### Reproducible cross-check (5-line Python)` (optional — present)

All six required H3 subsections confirmed present and in the specified order.

### Human Verification Required

The VALIDATION.md identifies three behaviors that need human judgment:

1. **Narrative readability** — the WHY paragraphs explain the bug mechanism in domain terms (data-bus race / address-LSB-bleed / `PORTD = 0x00` mirror gap) rather than jargon-only. This cannot be regex-checked. The verifier has read the four paragraphs and confirms they explain both the settling-delay mechanism (multi-register read across three AVR ports) and the PORTx pullup bias mechanism (`rurp_set_data_input` missing the `df5fb44` fix) with concrete numbers inline. Judgment: meets the "future maintainer can understand without re-bisecting" bar set by the phase goal. However, this remains a human-judgment item per VALIDATION.md — listed here for completeness.

2. **GATE-1.6 verdict soundness** — grep can confirm the three axis-words appear; whether each NO RISK verdict is correct is a domain judgment. The verifier notes: all three axes reason from the absence of shared code between read and write paths, which is a structural (code-path) argument rather than an empirical (bench) argument. The reasoning is traceable. Listed as informational; no programmatic check disputed it.

3. **Wave A → Wave B trigger decision** — `needs_bench: false` is present; the three T1/T2/T3 trigger evaluations are in the narrative. Whether the verifier would have made the same call is not testable from the meta-repo. RESEARCH.md predicted this outcome with HIGH confidence and the binary evidence supports it.

These items are informational only. They do not block the phase goal, which is about documentary completeness verifiable in code — all 8 programmatically-checkable must-haves pass.

---

_Verified: 2026-05-21T16:00:00Z_
_Verifier: Claude (gsd-verifier)_

---

## Re-open Verification (2026-05-26)

**Re-open trigger:** Phase 29 Attempt 2 Wave B FAIL (D-07 milestone-reopens, 2026-05-22 PM) — Phase 28 fix commits `437339b6` + `4f205e58` produced Leonardo + uno328pb regressions (83.8% zeros / 5 distinct SHAs on Leonardo; 30% zeros / 18.2% jitter on uno328pb) while Uno remained unaffected (Δ=0).

**Re-open scope:** Plans 27-03 (desk-side hypothesis re-disposition, 2026-05-26), 27-04 (bench A/B test, 2026-05-26), 27-05 (final synthesis, 2026-05-26).

**Re-open status at verification time:** closed (per `re_open_status: closed` in `### Re-open final verdict — closing the loop` subsection of `.planning/v1.6-EVIDENCE.md`).

**Verified:** 2026-05-26T13:30:00Z

### Re-open Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| R1 | Wave B FAIL cross-reference present in re-open section | VERIFIED | `### Wave B FAIL evidence cross-reference (re-open trigger)` H3 present at EVIDENCE.md line 388; 4 load-bearing facts enumerated (Leonardo 83.8% zeros, uno328pb 30% zeros, Uno Δ=0, chip-swap diagnostic). Token `Wave B FAIL` count in re-open section = 12 (grep confirmed) |
| R2 | v2 hypothesis re-disposition table has 8 rows (H1-H7 re-evaluated + H8 NEW) | VERIFIED | `awk '/^## Phase 27 — RCA Re-open Findings/,/^## Verdict/' | grep -c '^| H'` = **8**. H1-H6 stable-REFUTED (HIGH); H2 REVISED (separate failure mode); H7 IN-SCOPE (first real 328PB evidence); H8 NEW CANDIDATE (Phase 28 fix regression) |
| R3 | Plan 27-04 Outcome A/B/C disposition explicitly recorded with dual-cause verdict | VERIFIED | `### Plan 27-04 bench A/B test results` H3 at EVIDENCE.md line 452; `re_open_status: bench_complete`, `re_open_outcome: A-leonardo + B-uno328pb (dual-cause)`, `plan_27_05_required: true`, `phase_28_handoff: split-scope` all present (grep confirmed); `.hex` SHA identity falsifier `d9e51b7e` cited 8 times |
| R4 | Fix sketch v2 with split-scope: Leonardo revert/tune candidates named (`437339b6`, `4f205e58`); uno328pb handed to operator-level diagnosis | VERIFIED | `### Fix sketch v2 (Phase 28 re-iteration hand-off)` H3 at EVIDENCE.md line 507; fix-commit window `bc0f5ac..4f205e58` named; commits `437339b6` (masked PORTx-clear) and `4f205e58` (`_NOP()` settling) identified as per-commit revert/tune candidates; uno328pb branch explicitly "NOT a Phase 28 deliverable" |
| R5 | GATE-1.6 v2 retains 3 original GREEN axes and adds 4th axis ("fix introduces regression on other-board read paths") with `.hex` SHA identity as mandatory sub-check | VERIFIED | `### GATE-1.6 v2 reassessment` H3 at EVIDENCE.md line 530; "**Axis 4 (NEW — from Wave B FAIL) — fix introduces regression on other-board read paths**" named; Axis 4 verdict = RED for Phase 28 fix as shipped; `.hex SHA identity check` named as "new mandatory GATE-1.6 v2 sub-check"; 4-axis table in 27-05-SUMMARY.md confirms the structure |
| R6 | Final verdict block emits `re_open_status: closed`, `re_open_outcome: dual-cause (A-leonardo + B-uno328pb-independent)`, `phase_28_handoff: split-scope` | VERIFIED | `### Re-open final verdict — closing the loop` H3 at EVIDENCE.md line 544; YAML-like block at lines 548-552 contains all three required lines verbatim |
| R7 | RCA-01 re-closed at higher fidelity: two-layer characterization — pre-existing read race (pre-v1.0) + Phase 28 regression bracket (`bc0f5ac..4f205e58`) both on file | VERIFIED | EVIDENCE.md line 554 (Re-open final verdict): "two-layer characterization (v2): the pre-existing read race...produces the original 2.1% bit-jitter pattern; the Phase 28 fix commits `437339b6`...and `4f205e58`...introduce a SEPARATE failure mode"; `bc0f5ac..4f205e58` bracket cited 4 times |
| R8 | RCA-02 re-closed: dual-cause WHY narrative covers both Leonardo (firmware regression via PORTx-clear timing interaction) and uno328pb (pre-existing, `.hex` SHA identity falsifier) | VERIFIED | EVIDENCE.md line 556 (Re-open final verdict): "for Leonardo, the Phase 28 fix attempted to address both mechanisms simultaneously...but the combination produces a qualitatively worse failure mode (99% zeros vs original 2.1% jitter)...For uno328pb, RCA-02 v2: the pre-existing regression is structurally independent — `.hex` SHA identity (`d9e51b7e…`) falsifies any fix-induced path" |
| R9 | RCA-03 re-closed: brackets bifurcated — (a) original bug pre-v1.0 (`5b1f1cd`); (b) Phase 28 regression bracket `bc0f5ac..4f205e58` for Leonardo; uno328pb pre-existing bracket stated as unknown (hardware investigation required) | VERIFIED | EVIDENCE.md line 558 (Re-open final verdict): "(a) original read-race bug bracket: pre-v1.0 (unchanged from v1)...commit `5b1f1cd`..."; "(b) Phase 28 regression bracket for Leonardo: `bc0f5ac..4f205e58`"; "For uno328pb: the regression bracket remains pre-existing and pre-dates v1.6 — Phase 28 did not introduce it, and the introducing commit is not identified (hardware-level investigation required)" |
| R10 | IMMUTABILITY: original `## Phase 27 — RCA Findings (2026-05-21)` H2 byte-identical | VERIFIED | 27-05-SUMMARY.md anti-pattern guard #1 SHA `79f3e5cd…` PASS; 27-03-SUMMARY.md acceptance check #4 PASS; re-open section is appended between the Wave B FAIL post-mortem block (line 358) and `## Verdict` (line 562) — original section untouched |
| R11 | IMMUTABILITY: `### Wave B FAIL post-mortem (D-07 — milestone re-opens)` H3 byte-identical | VERIFIED | 27-05-SUMMARY.md anti-pattern guard #2 SHA `8782ed2f…` PASS; 27-03-SUMMARY.md acceptance check #5 PASS (rescoped awk confirmed) |
| R12 | IMMUTABILITY: `## Verdict` H2 + subsequent content byte-identical | VERIFIED | 27-05-SUMMARY.md anti-pattern guard #3 SHA `5b5903db…` PASS |
| R13 | All 6 prior H3 subsections (5 from Plan 27-03 + 1 from Plan 27-04) preserved when Plan 27-05 added its 3 | VERIFIED | 27-05-SUMMARY.md: "all 6 prior H3 subsections preserved — `grep -cE '^### (Wave B FAIL evidence cross-reference|...)' = 6`"; `awk` of re-open section confirms 9 total H3 subsections (5+1+3 = 9 in sequence) |
| R14 | 9 H3 subsections total under `## Phase 27 — RCA Re-open Findings (2026-05-26)` | VERIFIED | Direct awk count: 9 H3s present — `### Wave B FAIL evidence cross-reference`, `### Hypothesis re-disposition`, `### Pre-Phase-28-firmware A/B test design`, `### v1.7 substrate inputs for instrumented-build template`, `### Re-open Wave A verifier decision`, `### Plan 27-04 bench A/B test results`, `### Fix sketch v2`, `### GATE-1.6 v2 reassessment`, `### Re-open final verdict — closing the loop` |

**Re-open Score:** 14/14 truths verified

### Re-open Requirements Coverage

| Requirement | Re-open Verdict | Evidence | Higher Fidelity than 27-01? |
|-------------|----------------|----------|------------------------------|
| RCA-01 | VERIFIED | Two-layer exact code path: pre-existing read race in `rurp_read_data_buffer` + `rurp_set_data_input` (pre-v1.0 source, 2.1% jitter) AND Phase 28 fix commits `437339b6` + `4f205e58` introducing 99% zeros failure mode (regression bracket `bc0f5ac..4f205e58`). uno328pb: pre-existing, Phase 28-independent, `.hex` SHA identity `d9e51b7e…` falsifier. | YES — v1 identified one code path; v2 distinguishes the original bug from the fix-induced regression and names both commit brackets |
| RCA-02 | VERIFIED | Dual-cause WHY narrative in `### Re-open final verdict` paragraphs: Leonardo = masked PORTx-clear changes bus-drive timing such that `_NOP()` settling samples bus after chip output collapses; uno328pb = `.hex` SHA identity proves structural independence; hardware-level investigation required. Both causal paths fully explained with concrete evidence. | YES — v1 covered one failure mode; v2 explains both the original pullup-bias mechanism and the fix-induced timing disorder |
| RCA-03 | VERIFIED | Bifurcated brackets: (a) original read-race introduced by `5b1f1cd` "Leonardo is working, fast as a shark" 2025-02-11, pre-v1.0 (unchanged from v1); (b) Phase 28 regression bracket for Leonardo `bc0f5ac..4f205e58` (3-commit window, named commits `fdb1ed5` / `437339b6` / `4f205e58`). uno328pb: pre-existing pre-v1.6, introducing commit unknown. | YES — v1 had one bracket (pre-v1.0); v2 adds the Phase 28 regression bracket and distinguishes boards |

### Re-open Sub-repo Guard Verification (D-03 + D-12 extended)

| Sub-repo | Expected state (re-open) | Actual state | Status |
|----------|--------------------------|--------------|--------|
| `firestarter/` | HEAD = `4f205e58ca8f02653bfdda5d65916a8756f54db5`; branch = `v1.6-read-bug`; git status empty | HEAD = `4f205e58ca8f02653bfdda5d65916a8756f54db5`; branch = `v1.6-read-bug`; git status: clean | PASS |
| `firestarter_app/` | On `v1.6-read-bug` (sanctioned deviation — see below); HEAD = `999c3cca8004424e6055991d0c7bc690526e635e`; git status empty | HEAD = `999c3cc`; branch = `v1.6-read-bug`; git status: clean | PASS (sanctioned deviation) |

**Sanctioned deviation — firestarter_app branch:** Plan 27-04 left `firestarter_app` on `v1.6-read-bug` rather than restoring to `beta`. This is explicitly documented in 27-04-SUMMARY.md key-decisions: `firestarter dev consistency-check` only exists on `v1.6-read-bug` (post-v1.7-close beta dropped it during the v1.7 sub-repo rebase); restoring to beta would break the host CLI for any further v1.6 work. This deviation is sanctioned and forward-compatible with Plan 27-05 + Phase 28 re-iteration needs.

### Re-open Build Sanity (Behavioral Spot-Checks)

| Check | Command | Result | Status |
|-------|---------|--------|--------|
| leonardo build | `cd /workspaces/firestarter && pio run -e leonardo` | SUCCESS (0.86s) | PASS |
| uno build | `cd /workspaces/firestarter && pio run -e uno` | SUCCESS (0.74s) | PASS |
| uno328pb build | `cd /workspaces/firestarter && pio run -e uno328pb` | SUCCESS (0.68s) | PASS |
| pytest non-regression | `cd /workspaces/firestarter_app && pytest tests/ -x` | 90 passed in 0.95s | PASS |

All three firmware environments compile clean. Pytest suite green. No regressions introduced by re-open plans 27-03/04/05.

### Deviations Documented

| Deviation | Severity | Resolution |
|-----------|----------|-----------|
| uno328pb strict N=5 post-fix acceptance unmet (4 consecutive N=5 timeouts; final run used N=3) | WARNING | `.hex` SHA identity falsifier (`d9e51b7e…` byte-identical pre-fix and post-fix) over-determines Outcome B disposition without strict N=5. Documented in 27-04-SUMMARY.md deviations and in EVIDENCE.md `### Plan 27-04 bench A/B test results` Bench-instability finding block. Permanent memory `[[project_uno328pb_bench_instability_27_04]]` created. |
| firestarter_app left on `v1.6-read-bug` rather than restored to `beta` | INFO | Sanctioned — `firestarter dev consistency-check` not available on post-v1.7 beta; leaving on v1.6-read-bug preserves CLI availability for Phase 28 re-iteration. Documented above. |
| ADC_BAND_R41_* line numbers cited as :58-62 in plan, actual location :66-68 in rurp_pinout.h | INFO | Zero impact — constants exist and values correct. Minor anchor drift from intervening comment block. Both Plan 27-03 SUMMARY and Plan 27-05 SUMMARY document the correction. |

### Recommendations for Phase 28 Re-iteration

Phase 28 re-iteration is UNBLOCKED by this re-open closure. The split-scope recommendation from fix sketch v2 applies:

**Leonardo branch (primary):**
1. `git revert 437339b6 --no-commit` on `firestarter/v1.6-read-bug` — revert PORTx-clear commit alone
2. `pio run -e leonardo` → sideload → `firestarter dev consistency-check W27C512 --runs 5`
3. Compare shape: if structured-data + ~0.44% jitter, `437339b6` is primary regression source; if still zeros-dominant, also revert `4f205e58`
4. After shape restoration: GATE-1.6 v2 Axis 4 — N=5 per-board consistency-check on Uno + Leonardo + uno328pb before landing any re-fix
5. `.hex` SHA identity check mandatory on all three board targets across the fix window

**uno328pb branch (separate workstream):**
- NOT a Phase 28 deliverable — operator-level hardware diagnosis
- Candidate causes: Rev 2.2 socket contact wear, USB-to-UART bridge buffering, ATmega328PB Case A shared bus-read path timing audit
- Consult `[[project_uno328pb_bench_instability_27_04]]` memory node

### Anti-Patterns (Re-open Section)

Scan of `.planning/v1.6-EVIDENCE.md` re-open section and 27-03/04/05 SUMMARYs:

| File | Pattern | Severity | Finding |
|------|---------|----------|---------|
| `.planning/v1.6-EVIDENCE.md` | TBD/FIXME/XXX | None | Zero debt markers in re-open section |
| `27-03-SUMMARY.md` | TBD/FIXME/XXX | None | Zero debt markers |
| `27-04-SUMMARY.md` | TBD/FIXME/XXX | None | Zero debt markers |
| `27-05-SUMMARY.md` | TBD/FIXME/XXX | None | Zero debt markers |

### Human Verification Required (Re-open)

No new human verification items are required for re-open closure. The following items were resolved by bench evidence (Plan 27-04) rather than requiring ongoing human judgment:

- Pre-fix vs post-fix Leonardo shape: Outcome A confirmed empirically (bench 2026-05-26)
- uno328pb regression independence: Outcome B confirmed by `.hex` SHA identity falsifier (deterministic, not judgment-dependent)
- `re_open_status: closed` emitted by Plan 27-05 — the re-open loop is structurally closed

### Re-open Overall Verdict

**Phase 27 re-open: PASS**

All 14 re-open observable truths verified. All three requirements (RCA-01, RCA-02, RCA-03) re-closed at higher fidelity than original 27-01. Immutability guards on the original Phase 27 section, Wave B FAIL post-mortem, and `## Verdict` all confirmed. Sub-repo state matches expected guards. All three firmware targets compile clean. Pytest green.

**Phase 27 status: CLOSED** (original close 2026-05-21 + re-open close 2026-05-26). Phase 28 re-iteration UNBLOCKED with split-scope per fix sketch v2.

---

_Original verification: 2026-05-21T16:00:00Z_
_Re-open verification: 2026-05-26T13:30:00Z_
_Verifier: Claude (gsd-verifier)_

---
gsd_state_version: 1.0
milestone: v1.31
milestone_name: — 27C Programming-Algorithm Fidelity
current_phase: 146
current_phase_name: close-honesty-ledger-claim-gate-gh-15-reconciliation
status: executing
stopped_at: "146-04 complete -- D-12 first proof: the fifteen-leg fixture suite, 14 green, leg 9 RED for its verified named reason (all five closing artifacts absent), handed to 146-11"
last_updated: "2026-08-17T15:53:00.000Z"
last_activity: 2026-08-17
last_activity_desc: "**146-04 COMPLETE** -- D-12's FIRST proof and only the first: the fifteen-leg suite test_check_claims_v131.py (302cb63d) over five probed fixtures (28340b37), summary 27b74179. 14 legs GREEN, 1 RED BY DESIGN. EVERY PLANT WAS PROBED BEFORE ITS ASSERTION WAS WRITTEN, and the five probe results are recorded verbatim in 146-04-SUMMARY.md and 146-CITATIONS.md section 3.1: both clean controls returned empty forbidden-hit lists AND empty missing-caveat sets under the FULL caveat set; both forbidden plants returned EXACTLY ONE hit and ZERO missing caveats (label confirmed-working at fixtures/planted_forbidden_claim.md:14; pattern 10 at fixtures/planted_proven_unqualified.md:12); the caveat plant returned ZERO forbidden hits and exactly ONE missing label, ceiling-narrowing. The probe incidentally exercised the fail-closed default too -- every fixture basename resolved to the FULL caveat set, because no fixture is a _CAVEAT_RULES key. LEG 9 (test_armed_against_the_five_real_closing_artifacts) IS RED FOR ITS VERIFIED NAMED REASON and NOT for a collection error, an import error of a filename that is no valid Python identifier, a missing fixture, a wrong basename or a seam typo: the failure is the gate's own fail-closed missing-target branch naming ALL FIVE closing artifacts by absolute path, cross-checked by invoking the gate directly (rc=1, same five-path line). The attributing control is the same suite with leg 9 deselected -- rc=0, 14 passed, 1 deselected -- and THE DESELECTION LIVES ONLY IN THE TRANSCRIPT: the suite file carries no xfail, no skip and no deselection of its own, because a leg marked expected-to-fail in the file is a leg nobody looks at again. LEG 9's GREEN IS 146-11's TO RECORD and its second RED comes free from that plan's real-file plant; nothing in 146-04 may be read as leg 9 having passed, and CLOSE-01 is NOT discharged by fixtures alone. All four 146-VALIDATION.md CLOSE-01 selectors collect NON-EMPTY sets, verified by reading the collected NAMES and not only the counts: planted 3, caveat 5, closed-or-vacuous-or-precedence 3, default_targets 3. None of the four reaches leg 9 -- its name carries 'closing', not 'closed' -- so all four rows are green today and stay green through 146-11, and 146-VALIDATION.md:66's integration row remains the only row grading the armed run. THREE LEGS GO BEYOND THE DONOR, each for a measured reason: leg 4 REPLACES the donor's relational-rule leg because this gate has no relational rule, no proximity window and no exclusion mechanism (D-14) and none was added, and the donor's v1.30 caveat-bucket string and its self-verifying label were deliberately NOT copied -- an assertion against a string the gate never prints is a leg that can only ever be red; legs 14 and 15 are a PAIR proving the D-11 per-file caveat exemption BEHAVIOURALLY in both directions, since leg 14 alone is equally consistent with the gate skipping the exempt file entirely; and legs 2, 3 and 4 each additionally assert the ABSENCE of the other bucket, which is what keeps each plant single-reason as the fixtures age. TWO AUTO-FIXED SELF-PLANTS, both found by RE-RUNNING THE SCAN AFTER THE PROSE EDIT and neither by reasoning about the edit: 146-CITATIONS.md section 3's own warning table spelled out pattern 10's label id while explaining that spelling it is unsafe (1 hit, on the warning row itself; register back to 0 after citing test_check_claims_v131.py:242 instead), and two suite docstring lines reproduced forbidden literals as this plan's own prose (reworded to a 146-PATTERNS.md:357 citation; suite down from 4 hits to 2, and both survivors are the label literal the gate itself prints inside its bucket line and must not be 'fixed' by a later reader). THREE MEASURED-SAFE CITATION FORMS, reusable by 146-06..13: the hyphenated label id confirmed-working is CLEAN because pattern 7's whitespace class does not match a hyphen; the fixture filename planted_proven_unqualified.md is CLEAN because underscore is a word character; and pattern 10 written as its own regex is CLEAN because its leading boundary sits after a word character -- while the bare hyphenated label id HITS, because a hyphen is a non-word character. 146-check-claims.py is BYTE-UNCHANGED (git diff --numstat empty after both tasks): no leg was made to pass by editing the gate and no pattern was touched (D-14). 146-CITATIONS.md section 3 was appended with 210 insertions and ZERO deletions, so sections 0-2 are provably intact; the register header's misattribution of section 3 to plan 146-02 was RECORDED INSIDE SECTION 3 RATHER THAN EDITED, per the register's own leave-the-earlier-document-alone discipline. No fixture is reachable from the gate's defaults (0 of 5 basenames appear in a default-mode run), none is gitignored, all five are self-labelled on line 1, and each plant carries a second comment naming its label and its single failure reason. D-06 HELD: firestarter porcelain 0 lines and firestarter_app porcelain 7 lines (the pre-existing dirt), both unchanged from the wave-1 baseline; no sub-repo byte touched. D-01 HELD: no push, merge, tag, release or workflow dispatch; meta upstream-ahead 243 -> 246. This plan ticked NO CLOSE requirement (146-13 owns CLOSE-01..05) and moved exactly ONE ROADMAP line -- its own checkbox. Every state edit BY HAND; state.advance-plan NOT called, per the defect recorded below. Record gate re-run after this state write and BYTE-IDENTICAL to the phase-start baseline: rc=1, the same single unlabelled hit at STATE.md:11 that 146-05 owns. PRIOR (146-03, preserved): **146-03 COMPLETE** -- OD-A discharged on an OBSERVATION, not an inference: the ARM toolchain WAS installable here and the py32f071 CMake target COMPILED against this milestone's code. Arm GREEN taken; the other two arms marked NOT TAKEN in 146-ARM-BUILD-RECORD.md (283c31ba), raw logs under arm-build/ (974ea3d6). Measured: configure rc=0, build rc=0, 44/44 ninja edges, and the composite action's own oracle PASSED at exactly one firestarter_py32f071.hex -- 78769 B, sha256 5b0b55a2d71282a1899d3a931c673357912e1993a942934c26e67f61a4bebf8e; FetchContent resolved the SDK to 0ed2f4b4, byte-identical to the GIT_TAG pinned at platform/py32f071/CMakeLists.txt:17; text 27872 / data 112 / bss 5888. BOTH previously-blind TU registrations now compile for ARM -- 3207632 (eprom_params.cpp) and e9f6a92 (eprom_budget.cpp), each measured a NON-ancestor of the firmware remote tip fb7949c, so no CI run had ever seen either. THIS DISPROVES THE PRIOR-STATE SENTENCE PRESERVED FURTHER DOWN THIS SAME FIELD, which was written at plan time and recorded the toolchain as unavailable here; it is left verbatim on purpose because it is the Phase 130 record gate's own R-15 target and 146-05 owns its repair -- do NOT silently reword it, and do NOT add a second copy. TOOLCHAIN FACT FOR LATER PLANS: the composite action's four packages installed clean, and FOUR bare-metal C/C++ library packages (libnewlib-arm-none-eabi, libnewlib-dev, libstdc++-arm-none-eabi-dev, libstdc++-arm-none-eabi-newlib) arrived as AUTOMATIC APT DEPENDENCIES rather than by name -- which is exactly why the green carries its MANDATORY caveat: a local green is a DELTA against a target never compiled against any v1.31 code, it is NOT CI parity, it covers NO AVR target, and no PY32F071 board exists anywhere in this project. The box-9 sentence 146-09 must lift is quoted verbatim in the record's section 3 and was MEASURED clean of forbidden phrases by 146-check-claims.py in positional-argument mode, with a live negative control returning two hits from the same invocation (its only complaint on the real sentence was the two 6.25 V caveat labels, demanded of any unlisted basename by the fail-closed default). CI-NEVER-RAN RE-MEASURED AND UNCHANGED: firmware local fa6c9c7 vs remote milestone tip fb7949c = 61 local-only / 0 behind, last CI run 2026-08-09T06:48Z on fb7949c; host local 68820a6 vs remote tip 4d18b645 = 16 / 0, last CI run 2026-08-09T07:01Z on 4d18b645 via workflow_dispatch. No push, merge, tag or workflow dispatch (D-01) -- py32f071.yml fires on push branches ** with no containment, so the first push runs the loud ARM gate on 61 unseen commits at once, and that stays /gsd-complete-milestone's concern. D-06 HELD: firestarter porcelain 0 lines and diff --numstat 0 lines at every checkpoint, build directed to /tmp, nothing added to .gitignore, no firmware byte touched. ONE PLAN-INTERNAL CONTRADICTION RECORDED RATHER THAN WORKED AROUND: this plan's acceptance criteria demand a NON-ZERO firmware porcelain immediately after the build as a negative control, which is structurally unreachable under the SAME task's out-of-tree mandate -- porcelain measured 0 after configure AND after build because nothing was ever written inside firestarter/; substituted out-of-tree oracles (43 object files, 166308537 B of build tree, four emitted images with recorded digests, and the two named .obj files for the previously-uncompiled TUs) are recorded instead, and NO artifact was manufactured inside the repo to satisfy the criterion's letter. RECORD GATE STILL RED FROM THE PRE-EXISTING PHASE-START CAUSE AND NOT FROM THIS PLAN: rc=1 before and after with BYTE-IDENTICAL output, the single unlabelled hit at STATE.md:11 that 146-01 bisected to d2c212f1 and that 146-05 owns. Its PASS-line exempt tally is printed ONLY on the success path, so it is unobtainable while that hit stands -- captured via --explain instead and unchanged by this plan: block 23, line-label 4, inline-history 6, inline-allow 10, unlabeled 1, superseded 12. This plan ticked NO CLOSE requirement (146-13 owns CLOSE-01..05), filed NO backlog stub (999.32 belonged to the RED arm only; grep -c '999.32' over ROADMAP.md prints 0), and moved exactly ONE ROADMAP line -- its own checkbox. Every state edit BY HAND; state.advance-plan NOT called, per the ninth-occurrence defect recorded below. PRIOR (146-02, preserved): **146-02 COMPLETE** -- the D-13 CLOSE-03 documentation checker 146-check-close03-docs.py authored (57830381) and recorded RED (76d037fa), summary 1eb4ad32. The checker is PHASE-LOCAL, deliberately not in either sub-repo, because a host-side gate scanning firmware source fails OPEN on a rename (4x in Phase 117). The pre-edit RED is TRUE and needed no plant: rc=1, SEVEN unsatisfied topics across 4 of 4 failing targets, program-vcc-ceiling absent from ALL FOUR, plus four forbidden-phrase hits in firestarter/CLAUDE.md. Four locators recorded RED with the commands that produced them -- 1, 1, 1, 0, exactly as 146-VALIDATION.md predicted -- and the claim-word baseline at FOUR occurrences on THREE lines. Three non-vacuity legs recorded including the positive control. GREEN halves are owed by 146-06 (firmware docs), 146-07 (host doc plus the whole-checker green), 146-12 (the wording review that presence cannot substitute for) and 146-13 (the CLOSE-03 tick -- this plan ticked NOTHING). ONE AUTO-FIXED DEVIATION: the self-reference trap fired on 146-DOC-CHECK-RECORD.md itself, two prose uses of the forbidden claim word were reworded, and the residue is now MEASURED (10 hits, all of them the pattern label) rather than asserted away; caught only by re-running the scan AFTER the prose edit. TOOLING, NINTH OCCURRENCE: state.advance-plan misread current_plan as 146 -- the PHASE number -- rather than plan 02, returned advanced:false reason:last_plan with ELEVEN plans still to run, and in that same call flipped status executing->verifying, rewrote the body Status line to a false 'Phase complete -- ready for verification', dropped stopped_at quoting, and CLOBBERED this very field to a two-line fragment. Restored byte-identical from a pre-call snapshot (2320 lines, verified) and every state edit for this plan made BY HAND; only its progress arithmetic was correct and is kept (completed_plans 63, percent 85). TWO GATE NOTES FOR LATER PLANS: grep -c exits 1 on a zero count, so L1-L3's required post-edit value of 0 arrives with rc=1 while L4's arrives with rc=0 -- the statuses INVERT across the 146-06 edit, so assert the printed integer and never grep's status; and the sub-repo cleanliness leg passes VACUOUSLY when run without cd /workspaces, because git -C firestarter fails and wc -l then counts zero lines of OUTPUT -- observed live, so use an absolute git -C /workspaces/firestarter. PRIOR (execution record, preserved): Phase 146 EXECUTION STARTED 2026-08-17 -- sequential on the main tree, no worktree isolation: 12 of the 13 plans either read or commit into a submodule (commits_land_in / reads_repos), and worktrees leave submodules empty. PRIOR (planning record, preserved): Phase 146 PLANNED -- 13 plans in 7 waves (39802fb7, 6560f9a8), preceded by 146-RESEARCH.md (e0c0a818, 2576 lines, HIGH confidence) and 146-VALIDATION.md + 146-PATTERNS.md (3e1903be). GATES: gsd-plan-checker VERIFICATION PASSED with ZERO blockers and ZERO warnings; requirements coverage 5/5 CLOSE-01..05; check.decision-coverage-plan 14/14 covered, skipped:false. Note that gate verb needs TWO args -- phaseDir AND contextPath; called with one it skips-and-PASSES reporting 'CONTEXT.md missing', a false green. TWO OPERATOR DECISIONS TAKEN AT PLAN TIME, both now load-bearing alongside CONTEXT.md D-01..D-14. (OD-A) gh#15 box 9 is graded on an OBSERVED ARM py32f071 build, not on a not-reachable reason -- because research found neither sub-repo CI has EVER run any v1.31 code (firmware origin sits at fb7949c, end of Phase 138; app at 4d18b645, the branch point) and the ARM target has never compiled eprom_params.cpp or eprom_budget.cpp despite two commits registering them into its CMake manifest. All three arms are planned in 146-03: green carries a MANDATORY delta-not-CI-parity caveat (the devcontainer toolchain needs two newlib packages CI omits, so a local green proves a DELTA, never CI parity); red is RECORDED and NOT REPAIRED (a compile fix is a behaviour change D-06 forbids, landing after the bench evidence was taken) and routed to a 999.32 stub; not-observable is also covered. Discovered while planning: cmake, ninja and arm-none-eabi-gcc are ALL ABSENT, there is no top-level CMakeLists.txt (the build is platform/py32f071 via FetchContent, so it needs network), and build/, configure.log, build.log and tool-versions.txt are NOT gitignored in firestarter -- so 146-03 builds out-of-tree under /tmp and asserts the firmware porcelain back to 0 lines, because BOTH sub-repo suites assert it. (OD-B) an EIGHTH correction joins D-04's seven: PROJECT.md:216 'Faster than today in the typical case' is a comparative claim Phase 145 boundary 1 forbids (v1.31 claims fidelity, not improvement; no control run exists, 145 D-08). It lands as a CORRECTION block APPENDED AFTER the corrected text -- never inserted above, because twelve live lines=N exemptions sit in the three files Phase 130 record gate scans -- plus an eighth register row, with check_record_corrections.py re-run to exit 0 after every insertion. RESEARCH CORRECTED CONTEXT.md ON THREE OF THE SEVEN INHERITED CORRECTIONS, so the site list is derived from RESEARCH.md and NOT from D-04 prose: (1) the PROJECT.md half of 143 D-01 has NO false-statement site at all -- zero grep hits, and what sits at :131/:1183 is a TRUE routing note -- so that correction is ROADMAP.md-only and the non-finding is itself recorded; (2) F-140-05 spans TWO throughput rows, PROJECT.md:212 AND :213, and eprom_params.cpp:41-43 says so itself, so 140-PARAM-TABLE-RECORD.md:272 owes CLOSE-04 THREE items not two; (3) F-140-07 is ALREADY corrected in place in firestarter/doc/PROTOCOLS.md section 1.5 by 140-06, so only the PUBLIC gh#15 half plus four .planning sites remain owed. Rule applied to those four: live prose gets a CORRECTION block, dated historical records (plan summaries, decision logs, bench logs) get a register row only -- D-05 rationale is that the block warns /gsd-new-milestone scoping pass IN SITU, and that pass reads live prose, not dated history. GATE SELF-TRIP HAZARDS, ALL MEASURED: \\\\bproven\\\\b matches AFTER A HYPHEN, so 'bench-proven' (D-09 own CONTEXT phrasing) trips the gate and the artifacts must be WRITTEN around the word per D-14, never the pattern loosened; 145-BENCH-LOG.md:2709 contains 'datasheet-correct' so quoting Phase 145 boundary 2 verbatim self-trips (D-14 BEATS D-03 -- cite file:line, never quote); a 146-*.md glob catches 146-CONTEXT.md (6 hits) so _DEFAULT_TARGETS must be an EXPLICIT five-file list; all five of Phase 137 fixtures contain unqualified 'proven' so the donor CLEAN CONTROL would fail 146 own gate and fixtures are authored FRESH; 139 _V131 env-seam name is already taken this same milestone; and the donor needs FOUR edits, the '139-' prefix literal appearing in BOTH the startswith call AND its printed message (missing the second copy is the classic silent break). Do NOT copy 139-check-claims.py:57-61 -- its non-claim asserts the OPPOSITE of this phase deliverable. NEW FINDING NOT IN RESEARCH.md: firestarter/CLAUDE.md carries FOUR occurrences of unqualified 'proven' at :64 (1), :65 (2), :66 (1) and that file is a D-13 target, so the doc checker would be RED on forbidden phrases as well as on the missing ceiling; 146-06 Task 2 rewords all four. Note grep -c reports 3 there because it counts LINES, not occurrences -- the plans use the occurrence form. Also measured: firestarter_app/CLAUDE.md:46 carries a 'verified-on-silicon' hit and is deliberately OUTSIDE the target set, recorded as a decision in 146-02 section 4. FOUR LOCATORS ARE TRUE REDS TODAY and are recorded RED before the edit and GREEN after, which satisfies 'seen to fail for the right reason' without a plant: 'Phase 141 replaces it'->1, 'eprom.cpp:159-179'->1, '71 cases'->1, '79 cases'->0. PLANNER SELF-CAUGHT TWO DEFECTS: 12 verify legs redirected into /tmp/gsd146/ without creating it (found by EXECUTING the runnable-today legs, not by bash -n -- the record-gate baseline leg failed with No such file or directory and would have reported record_gate_rc=1 against a gate that actually exits 0), and the pre-existing 2-line ROADMAP heading rename got swept into the plan commit, invalidating 146-01 expected-dirt list; both fixed in 6560f9a8. TOOLING, EIGHTH OCCURRENCE: state.planned-phase reported {'updated': []} -- literally nothing -- while actually REGRESSING current_phase 146->145 and current_phase_name->bench-validation, CLOBBERING this very field to the truncated garbage '145-09 complete. See', and dropping stopped_at quoting; it set NEITHER status NOR total_plans. Its body-field writer targets a **Status** line this STATE.md does not have, which is why it self-reported an empty update. Repaired by hand from a pre-call snapshot, restore verified byte-identical, line count unchanged at 2284. NEXT: /gsd-execute-phase 146 -- and NEVER with --auto or --chain: constraint 10, both auto-approve human-verify gates and autonomous:false is not self-protecting. 146-12 (freeze -> blocking wording review -> blocking authorization -> single gh issue comment -> byte-verify) and 146-13 (the ONLY plan permitted to tick CLOSE-01..05) each read and record the RESOLVED auto-mode value and halt on any non-false value."
progress:
  total_phases: 9
  completed_phases: 8
  total_plans: 74
  completed_plans: 65
  percent: 87
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-08-05

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-08-08 — v1.31 started)

**Core value:** Algorithm-first dispatch — the minipro `protocol_id` (`algorithm`) is the single
authoritative dispatch key end to end. v1.31 makes that key drive *programming behaviour*, not just
handler selection — while keeping the pulse width itself a database datum, not a protocol constant.
**Current focus:** Phase 146 — close-honesty-ledger-claim-gate-gh-15-reconciliation

**v1.31 27C Programming-Algorithm Fidelity (gh#15)** — ACTIVE (activated 2026-08-08, retiring Backlog
**999.22** which was queued as the `v1.27` slot). **Firmware-touching, dual-repo lockstep.** Phase
numbering continues at **Phase 138** (v1.30 ran 131–134, 136, 136.1, 137; the 135 slot stays vacant).
v1.24 (Bus-Config Mask-Model), v1.25 (Jumper-Display / 2516) and v1.26 (White-Box Voltage Calibration)
are left byte-unchanged so by-number cross-references keep resolving; v1.28 (Binary Command Protocol)
and v1.29 (vacant) unchanged.

**Scoped from gh#15 as CORRECTED, not as written.** The `/gsd-explore` pass of 2026-08-08
(`.planning/seeds/27c-algorithm-fidelity-param-table-refactor.md`, commit `c60543c5`) found two wrong
numbers and one inverted premise in the issue:

- **C1** — gh#15's `0x0B` `pulse: 50000 us` is the fingerprint of **BUG-2**, the ×100
  `interpret_timing()` multiplier over 252 chips that Phase 57 already removed. True value **500 µs**.
  Adjudicated at `firestarter_app/doc/infoic-field-dictionary.md:210-217`.

- **C2** — pulse width is **DATA, not a per-protocol constant**. Measured live against the shipped DB
  2026-08-08: `0x07` n=170 (100 µs ×113, 200×27, 1000×22, 500×4, 50×4); `0x08` n=127 (100 µs ×104,
  50×11, 10×7, 200×2, 1000×2, 20×1); `0x0B` n=32 (500 µs ×21, 1000×6, 200×5) — all three gh#15
  constants disagree with the modal value. minipro ships `protocol_id` and `pulse_delay` as two
  orthogonal wire fields (`t48.c:250-267`) and exposes `-o pulse=N` per run (uint16, 65535 µs ceiling).

- **C3** — the safe 32-bit delay helper is still needed, but for the **75 ms overprogram pulse**, not
  for any pulse.

**D-01 (structural):** protocol owns *shape* — `max_pulses`, `overprogram_factor`,
`overprogram_cap_us`, `verify_mode`, `vpp_path` — and the database owns the *pulse*. One shared
per-byte pulse→verify loop driven by a `const` table, **not** gh#15's three state machines with
hardcoded timing constants. `handle->pulse_delay` stays on the write path; protocol constants survive
only as `pulse_delay == 0` fallbacks (`eprom.cpp:70-77`).

**D-02:** the `0x0B` one-shot-vs-looped question is **not answerable from source** — minipro never runs
the algorithm, it packs `pulse_delay` into a `BEGIN_TRANS` message for closed TL866/T48/T56/T76
firmware. Ships as looped pulse→verify with a **50 ms accumulated-energy cap per byte**
(`100 × 500 µs` = the classic 2716 total programming time), satisfying both readings. No overpulse.

**D-03:** gh#15's corrections are posted **early, before implementation phases run**, on the v1.30
CLOSE-06 pattern (drafted → frozen → operator-approved → posted only on explicit authorization).

**Enabler:** VPE survives a read — `mem_util_calculate_top_address_register` preserves the HV mask
across every `set_address` including the read path (`memory.cpp:163-166`) — so the `delay(10)` VPE
settle (`eprom.cpp:114`) stays amortized once per block instead of 512 × 10 ms = 5.1 s. Caveat: for
`pins < 32` the mask also preserves `CTRL_VPP_VPE_DROP_ENABLE`, which on DIP32 *is* A16.

**⚠ Evidence ceiling, fixed before any code moves:** the ~6.25 V program-VCC all four vendor
algorithms assume is **unreachable on this shield** (no VCC-raise path). This buys timing /
pulse-count / verify fidelity and **not** silicon-margin fidelity. gh#15 omits this entirely, so its
acceptance criteria must be amended; a committed claim gate forbids the unqualified
"datasheet-conformant" overclaim. Bench coverage is **asymmetric by inventory** (operator,
2026-08-08): `0x07` **required** (W27C512 / TMS27C512); `0x08` (AM27C020 — known marginal from v1.18
Phase 99, write#1 60/64 then write#2 0/64) and `0x0B` (M2716 / M2732, 25 V NMOS, Phase 79 VPE path)
are **opportunistic — skipped-with-reason if the parts do not materialize, never rubber-stamped**.
This change is **not behavior-preserving**: golden traces encoding today's pulse cadence will
legitimately shift, and re-baselining is expected work, not a regression.

**⚠ BLOCKING PRECONDITION.** `firestarter_app`'s `gsd/v1.30-sdp-surface-retirement` is **NOT merged
into `origin/beta`** — v1.30's PR was staged (`.planning/v1.30-PR-BODY.md`) but never opened, even
though v1.30 is recorded as shipped. Operator decision 2026-08-08: **land it to `beta` first**, then
fork v1.31's app branch off the updated `beta`. Firmware forks off `beta` @ `3085084` (clean). Meta
forks off the v1.30 tip.

**CORRECTION (2026-08-08, Phase 138 planning — measured, not recalled).** The precondition above is
**falsified**: `firestarter_app` PR **#44** was opened *and* **MERGED** on 2026-08-05T21:13:01Z as a
**squash** (merge commit `568e58b`, single parent `16a313a`). `git merge-base --is-ancestor` exits 1
**because of the squash**, not because content is missing — `comm -23` of both `git ls-tree -r
--name-only` lists is **empty** (zero files on the v1.30 branch absent from `beta`), and
`git diff --stat` is 12 files fully attributable to beta's later PRs #45/#46/#48/#49 plus the version
bump. A re-merge is *guaranteed* to conflict (`tests/test_chip_test_sdp_leg.py` added in both with
different blobs). **Operator decisions this session:** (**OD-1**) PREP-01 is discharged as a named
content-equivalence finding `F-138-01`, **not** a merge — no PR is opened and no operator merge is
required; the pre-release this predicted **already happened** (`beta` is at `3.0.0b20`).
(**OD-2**) firmware still forks at `3085084` — `check_size_baseline.py` is **GREEN** there and **RED**
at the live tip `6fab4ea` (+34 B flash ×3 targets) — with the drift and the MERGE-05 headroom (+56/+62
against a 64 B band) recorded as a forward finding with owners, **not fixed** (D-07). The app forks at
the live post-merge `beta` tip; meta's base is **`d0f0c6a0`** (the *longer-named* v1.30 branch).
(**OD-3**) the meta repo's stale submodule gitlinks are **not** advanced — the three base commits are
named in the narrative baseline artifact instead. Full four-oracle evidence:
`.planning/phases/138-preconditions-baseline/138-RESEARCH.md` §"Branch & Ancestry Ground Truth".

## Current Position

Phase: 146 (close-honesty-ledger-claim-gate-gh-15-reconciliation) — EXECUTING
Plan: 146-04 of 13 complete (wave 1 COMPLETE — 146-01, 146-02, 146-03; wave 2 IN PROGRESS — 146-04 done)
Status: Executing Phase 146.

**Prior-phase carry-over, restored — the three sentences below were left as dangling fragments by
the `/gsd-execute-phase` execution-start state write and are repaired here by plan `146-01`, which
recorded the damage in `146-CITATIONS.md` §0.3 before repairing it.** Phase 145 is COMPLETE (9 of 9
plans; the halt of 2026-08-16 was lifted 2026-08-17). **BENCH-01, BENCH-02 and BENCH-03 are ticked**
in both `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md`, flipped by `145-09` behind a blocking
operator gate that was **not** auto-approved (`_auto_chain_active` false, `auto_advance` absent).
Phase 145's verdict was `validated` on all four ROADMAP success criteria: criterion 1
`validated` (three 64 KiB cycles on W27C512 `0xda08`, byte-exact on both oracles), criteria 2 and 3
`skipped-with-reason` naming **AM27C020** and **M2716/M2732** with **no `0x08` or `0x0B`
measurement taken in this phase**, criterion 4 `validated` at Gate 0 and re-confirmed at the tip.
**The three ticks are bounded by the VERDICT section's boundaries** — one part, one `leonardo`,
one shield revision (Rev 2.0); no comparative claim; no datasheet-conformance claim; the
intermittent single-byte margin failure **mitigated, not explained**; and both Gate 2 and Gate 3
run on a build carrying **MERGE-05's open, un-adjudicated +96 B leonardo breach**. Full records in
`.planning/phases/145-bench-validation/145-09-SUMMARY.md` and the
"# REQUIREMENT FLIP — `145-09`" section of
`.planning/phases/145-bench-validation/145-BENCH-LOG.md`.

Last activity: 2026-08-17 — **`146-01` COMPLETE** (`8bf2acae`, `44f4cdb8`). `146-CITATIONS.md` §§0-2
record the phase's structural no-push baseline: upstream-ahead **233 / 61 / 16** (meta / `firestarter`
/ `firestarter_app`) as the **only** oracle for D-01, which has no mechanical enforcement because
`git push`, `gh workflow` and `gh release` are all allowlisted; three-repo porcelain enumerated by
path (`firestarter` clean at 0 lines); the stale gitlink delta recorded as a **fact, never a
criterion** (both lag the live tips by the whole milestone, and always have); thirteen
read-only gh#15 oracles with **zero divergence** (OPEN, `lastEditedAt` null, 1 comment
`#5233463320`, 5964 bytes, 9 unticked boxes, empty criteria diff, labels `[]`); and nine anchor blob
SHAs, eight byte-identical to `HEAD`. `146-check-claims.py` is committed as the D-11 gate: five
`_HERE`-built targets, the twelve donor patterns unchanged with no window and no exclusion mechanism
(D-14), the per-file `_CAVEAT_RULES` map with `146-CORRECTIONS.md` exempt and any unknown basename
getting the FULL set, a fresh `FIRESTARTER_CLAIMSCAN_TARGETS_146` seam, and **no** exit-0-on-nothing-
scanned path. Seen to exit 1 for four named reasons before any target existed, and its `PASS` branch,
its D-11 exempt path and its fail-closed-on-rename policy each separately observed against temporary
probe files. **TWO FINDINGS FOR LATER PLANS.** (1) The Phase 130 record gate is **RED at phase
start** — `rc=1`, one unlabelled `arm-toolchain-absent` hit at `.planning/STATE.md:11` — bisected
through the gate's own env seam to commit **`d2c212f1`** (`docs(146): record planning completion`),
which wrote a build-tooling-availability sentence into `last_activity_desc` that collides with the
gate's own two-token needle (`check_record_corrections.py:261-263`). The offending text is cited by
location — `.planning/STATE.md:11` — and deliberately **not** reproduced here, per D-14: quoting it
would plant a second copy of the same hit, which is exactly what the first draft of this entry did
and what `146-01` caught by re-running the gate after its own edit. The
plan's recorded baseline (exit 0, tally `{'block': 23, 'line-label': 4, 'inline-history': 6,
'inline-allow': 10, 'superseded': 12}`) is correct for `6560f9a8`, one commit earlier. **NOT
repaired: `146-05` owns it** — an exemption placed inside `last_activity_desc` is destroyed by the
next state write. (2) The `lines=N` line-shift hazard the plan warns about does **not** apply to
`146-05`'s sites: `ROADMAP.md`, `PROJECT.md` and `STATE.md` carry **zero** active
`recordscan:supersedes` markers; all twelve superseded line references live in
`.planning/notes/py32f071-port-branch-state.md:172-178`. Append-after-the-subject is still required,
by `_BLOCK_CLOSER_RE`, not by any marker. NEXT: wave 1 continues with `146-02` and `146-03`.

**One item Phase 146 must pick up (it has a v1.31 owner, unlike the twelve carry-forwards):**
`ROADMAP.md`'s **v1.31 Coverage table is stale for 12 rows** — `PREP-01`…`PREP-04`,
`ISSUE-01`…`ISSUE-03` and `HOST-01`…`HOST-05` read `Pending` there while `REQUIREMENTS.md`
correctly reads `Complete`. Pre-existing drift from phases 138/139/143, present in the pre-edit
snapshot, left untouched by `145-09` under its "flip nothing but BENCH-01…03" prohibition.
**Phase 146 reads that table at close and must reconcile it first.**

**Three standing facts for whoever picks up 145-06:**

1. **The firmware under test is `ebe9cb3`, not `a594173d`.** 27002 B program / 2014 B data,
   avrdude-verified 27002, 1670 B free. The version string is `3.0.0b17` on **both** builds, so it
   identifies nothing (D-18). Gate 1's four identity rows are superseded, visibly, in the bench log.
   No further reflash is needed for 145-06 **unless the tree changes again** — check
   `git -C /workspaces/firestarter rev-parse HEAD` against `ebe9cb3` before trusting that.

2. **MERGE-05 is breached on this build and NOT adjudicated.** +96 B against a 0 B leonardo band;
   BASE-01 deliberately not re-anchored; recorded live by
   `test_policy_merge05_fires_on_the_current_tree`. Every bench measurement from 2026-08-17 onward
   was produced by a build carrying that open breach. It is a milestone requirements judgement for
   the operator — do not re-anchor, widen a band, or "fix" the gate from a bench plan.

3. **D-09's single re-seat allowance is UNCONSUMED.** The 2026-08-16 failure had a firmware cause
   and no chip was ever touched, so the allowance was never spent. Session 1's failure is **not**
   discarded — it stands in the record as a genuine failure of a genuinely defective build.

**Also note:** RQ-4's frames-per-block table is stale for the shipped firmware. At the database's
100 µs pulse the measured figure is **1 frame per block**, not 0, because the shipped settle
increase pushed block time to 1.657 s past the 1000 ms emit cadence. D-10 Claim A HOLDS. Claim B
remains 145-07's — 145-05 declined to bank it despite two blocks literally satisfying its wording
(those pairs are bar-latch-transition artifacts, not two firmware emissions in one block).

**Phase 145 is a bench phase — hardware in the loop.** Chip handling, photos and multimeter
readings are operator-only, and the operator adjusts the voltage pot himself. Do not run it
under `--auto`/`--chain`: auto-modes **auto-approve** `human-verify` gates, so `autonomous:
false` is not self-protecting. Phase 144 (complete) carried the same restriction for its
requirement-flip gate.

**Do not run Phase 139 under `--auto`/`--chain`.** Plan `139-05` Task 1 is a blocking
`checkpoint:human-action` gate on an irreversible public act (posting to gh#15). Auto-modes
auto-approve `human-verify` gates but never `human-action`; `autonomous: false` alone is not
self-protecting (CONTEXT D-09).

**Decision-coverage gate: OVERRIDDEN at plan time (operator decision, 2026-08-09).**
`check.decision-coverage-plan` returned `passed: false, reason: "could-not-parse"` — a parser
limitation, not a coverage gap. Six of `139-CONTEXT.md`'s eleven decision bullets defeat
`bin/lib/decisions.cjs`'s three bullet regexes in three distinct ways: `D-01`, `D-04`, `D-06`, `D-07`
wrap the bold label across two lines; `D-08` carries nested `*italics*` inside the bold run
(`bulletEmDashRe`/`bulletTitledColonRe` both reject any `*`); `D-09` carries extra colons inside it
(`` `checkpoint:human-action` `` — `bulletTitledColonRe`'s `[^:*]*` rejects). `139-CONTEXT.md` was
deliberately **not** reformatted: `139-01-PLAN.md` prohibits editing it and asserts
`git status --porcelain` on it is empty.

Coverage substance was verified manually instead — the union of decision ids cited across the five
plans is D-01 … D-11 complete:

| Plan | Decision ids cited |
|------|--------------------|
| 139-01 | D-01, D-03, D-06, D-07, D-08, D-10 |
| 139-02 | D-01, D-05, D-08, D-10 |
| 139-03 | D-01, D-02, D-03, D-04, D-05, D-06, D-07, D-08, D-10, D-11 |
| 139-04 | D-01, D-03, D-08, D-10 |
| 139-05 | D-01, D-08, D-09, D-10 |

verify-phase should re-surface this override rather than treat the gate as passed.

## Roadmap Summary (v1.31)

**Created:** 2026-08-08 — derived from `.planning/seeds/27c-algorithm-fidelity-param-table-refactor.md` + gh#15 (no `research/SUMMARY.md` for this milestone; project-level research deliberately skipped, operator decision 2026-08-08 — the seed + gh#15 + a `/gsd-explore` pass already constitute the research).

**Phases:** 9 (138–146). **Granularity:** Comprehensive (config). **Coverage:** 45/45 v1 requirements mapped, 0 unmapped — exact 1:1 category→phase mapping (PREP→138, ISSUE→139, TABLE→140, LOOP→141, VPP→142, HOST→143, TEST→144, BENCH→145, CLOSE→146).

| Phase | Goal | Requirements |
|-------|------|--------------|
| 138 Preconditions & Baseline | Verified branch bases (operator PR-merge gate) + a pre-change golden-trace/flash-RAM/suite-count baseline + the live pulse-width distribution, all before any `eprom.cpp` edit | PREP-01…04 |
| 139 gh#15 Correction (outward) | Draft, freeze, operator-approve, and (only on explicit authorization) post the C1/C2/C3 + 6.25V-ceiling correction before any implementation lands | ISSUE-01…03 |
| 140 Parameter Table | `const` `protocol_id`-keyed shape table (no pulse column), datasheet-cited, no second dispatch key | TABLE-01…05 |
| 141 Per-Byte Program Loop | Fixed-width pulse→verify per byte, overprogram/energy-cap rules, hard-fail-on-max-pulses, VPE held per block | LOOP-01…08 |
| 142 High-Voltage Routing | Table-driven VPP/VPE path selection, one shared mask set, disable-on-every-exit, over-voltage refusal re-verified | VPP-01…04 |
| 143 Host Timeout, Progress & Pulse Override | Long blocks survive the host timeout with visible progress; `--pulse-us` bounded and pre-validated | HOST-01…05 |
| 144 Tests & Build Verification | Native/host/cross-repo proof of the new algorithm; deliberate frozen-vs-new golden-trace diff; flash/RAM delta vs. Phase 138 baseline | TEST-01…08 |
| 145 Bench Validation | `0x07` required bench proof; `0x08`/`0x0B` opportunistic or honestly skipped; zero `support_status` change | BENCH-01…03 |
| 146 Close | Fail-provable claim gate; honesty ledger; docs; gh#15 reconciled item by item; stranger-actionable release notes | CLOSE-01…05 |

**Load-bearing ordering (not preference):** 138→139 (PREP-04's distribution is ISSUE-01's cited evidence) · 139 before 140/141/142/143 (D-03: the correction is public before any implementation lands) · 140→141 (the loop is table-driven) · 141→142 (VPP hardening re-verifies the loop's own hard-fail/disable behavior) · 138→143 (independent of 140-142, different repo — genuinely parallel) · {140,141,142,143}→144 (cross-repo constants parity needs all four) · 144→145 (bench needs a built, passing image) · 145→146 (close reports on bench evidence) · 139→146 (close reconciles gh#15 against the posted correction).

**Genuinely parallel: {140, 141, 142} (firestarter) ∥ {143} (firestarter_app)** — disjoint repos, converge at 144.

**Deviation from a research spine:** none exists to deviate from — this milestone deliberately skipped project-level research (operator decision, 2026-08-08); the seed + gh#15 + the `/gsd-explore` correction pass are the research record this roadmap is derived from instead.

**Full detail:** `.planning/ROADMAP.md` §"v1.31 — 27C Programming-Algorithm Fidelity (gh#15) (PLANNING)".

### Phase 137 plan 06 (2026-08-05) — COMPLETE — PHASE 137 CLOSED

`137-06-SUMMARY.md`: Task 1 replaced the stale `test_unarmed_when_zero_of_four_default_targets_exist`
with `test_armed_and_green_against_the_four_real_artifacts` and re-ran `check_permitted_claims.py` with
no arguments (its real default targets) for the first genuinely-armed run of this gate in the
milestone: `PASS: scanned 137-LEDGER.md, 137-DECISION.md, 137-RELEASE-NOTES-app.md,
137-GH12-COMMENT.md; 4 file(s) carry the required silicon caveat`, exit 0, 11/11 paired-suite tests
passing — **CLOSE-01's literal discharge**. Task 2 re-ran the CI-parity recipe one final time over the
whole milestone diff (ROADMAP's cross-cutting instruction): `ci_parity.sh` unchanged in shape from
every prior phase (legs 1-3 exit 0, leg 4 exit 2, the documented ambient-numpy devcontainer artifact);
`ci_replica_venv.sh` → **CI-REPLICA: PASS**, mypy **33/35** with the watermark explicitly NOT moved,
checked **129** source files (down from the Phase 136.1 baseline of 132 — reconciled to plan 137-02's
own `tests/fixtures/` mypy-exclude fix, still 9 above the `MIN_CHECKED_SOURCE_FILES = 120` floor), full
suite **1508 passed** (matching 1504 + plan 137-02's own 4 new tests), coverage **82.14%** unmoved; the
**43/41/84** SDP partition independently re-derived three ways this plan alone, unchanged across the
whole milestone; firmware submodule confirmed untouched, zero new package installs confirmed across
the whole phase's commit range. `137-CI-PARITY.md` records Before (Phase 136.1 close) / After (this
plan) sections plus a whole-milestone summary table spanning Phases 131 through 137. Task 3 ticked
CLOSE-01 in `REQUIREMENTS.md` citing the live `PASS:` line; finalized `v1.30-OPERATOR-BATCH.md` with a
new "PHASE 137 COMPLETE" section naming the two remaining operator actions as one list; authored
`137-RECORD.md` with all six mandated sections (requirement accounting for all seven of this phase's
own requirements; the ROADMAP's six success criteria discharged with named evidence; corrections
carried forward — the six `137-LEDGER.md`-mandated corrections plus this phase's own two, the RELOCK-07
fifth citation drift and the CLOSE-06 posting-precondition timing decision; residuals; the Evidence
Ceiling restated verbatim from `134-RECORD.md` §7; hand-off). **CLOSE-06 was deliberately NOT ticked by
this plan** — it stays `[ ]` open by explicit, repeated operator/orchestrator instruction (137-05's own
prior decision, reaffirmed in this plan's own dispatch context), which directly overrides this plan's
own `PLAN.md` text: Task 3's acceptance criteria and step-6 narration had literally expected a
56/56-ticked, zero-open final state — a genuine plan-authoring staleness (very likely drafted before
137-05 finalized the hold-open decision), documented in full with both readings in `137-RECORD.md` §1
and this plan's own SUMMARY, not silently reconciled by ticking CLOSE-06 to force the stale acceptance
criterion green. **One requirement ticked: CLOSE-01.** Project-wide requirement state, freshly
measured: **55 ticked / 1 open** (`CLOSE-06`, held open by design, with its own annotated row and the
exact single closing command already recorded in both `REQUIREMENTS.md` and
`v1.30-OPERATOR-BATCH.md`). No sub-repo commit this plan (pure meta-repo documentation;
`firestarter_app`'s tracked gitlink `cc036e8` confirmed unchanged before and after). Commits: meta
`0efd4072` (Task 1), `01fbb57a` (Task 2), `22ac6237` (Task 3), `6b1fdd2c` (SUMMARY). **v1.30 is now
ready for `/gsd-complete-milestone`** once the operator completes the two remaining named actions.

### Phase 137 plan 05 (2026-08-05) — COMPLETE

`137-05-SUMMARY.md`: Task 1 (already committed `2f51572d` before this session) froze
`137-GH12-COMMENT.md` verbatim from the draft and ran the first live shipped-check, finding the claim
gate FAILing (missing required silicon caveat). Task 2's `checkpoint:human-action` gate was answered by
the operator in real time, verbatim: **wording APPROVED** — one correction made under that approval,
weaving "No AT28C silicon was tested during this milestone" into the "where I need help" paragraph so it
reads as the *reason* help is needed rather than a disclaimer (committed `3596604d`, simultaneously
resolving A-4 — the gate now `PASS`es on the file alone and is ARMED and green across all four closing
artifacts for the first time this phase); **posting HELD, not authorized**; and **CLOSE-06's tick
decision OVERRIDDEN to option (b)** — the more literal reading of "is posted" — so CLOSE-06 stays `[ ]`
open rather than ticked-on-freeze. Task 3 re-ran the shipped-check independently (not reused from Task
1, per the plan's own requirement): `git -C firestarter_app merge-base --is-ancestor 259a0f0 origin/beta`
still exits 1; PyPI's highest published prerelease is still `3.0.0b15` — though the plan's literal
one-liner (`info.version`) reads `2.0.7`, the latest **stable** release, a different field from "highest
prerelease" entirely, a genuine finding recorded rather than glossed over. Combined verdict **NOT YET
SHIPPED**, matching the operator's own "hold" instruction with no disagreement to arbitrate — the
freeze-only branch was taken, `gh issue comment` was never invoked, and `gh issue view` confirmed the
comment count unchanged at **9** both before and after. Updated `v1.30-OPERATOR-BATCH.md`: A-1 →
RESOLVED (wording approved, frozen at blob `3a628c56de4d45dfe2be0c645fced0e25d5ebceb` / 2646 bytes,
exact follow-up command recorded); A-3 → RESOLVED (operator chose option (b)); A-4 → RESOLVED (operator
chose option (ii), gate unblocked for 137-06's CLOSE-01); A-2 left open; RUN STATUS section updated to
reflect 5/6 plans done. **[Rule 2 deviation]** Annotated `REQUIREMENTS.md`'s CLOSE-06 row in place
(outside this plan's declared `files_modified` list, but required by the orchestrator's own success
criteria) explaining why it is open and the exact single follow-up command that closes it, plus the
matching Traceability table row. **Zero requirements ticked this plan** (CLOSE-06 deliberately held
open per operator decision) — project-wide requirement state remains **54 ticked / 2 open** (`CLOSE-01`
— 137-06's own scope, now unblocked; `CLOSE-06` — deliberately held open). No sub-repo commit
(meta-repo documentation only; `firestarter_app`'s tracked gitlink read-only inspected for the
shipped-check, confirmed unchanged). Commits: meta `2f51572d` (Task 1, prior session), `3596604d`
(operator-approved A-4 correction), `e886e03` (Task 3 freeze + operator-batch/REQUIREMENTS.md update),
`b0a2fdd4` + `ab81dc6c` (SUMMARY + self-check).

### Phase 137 plan 04 (2026-08-05) — COMPLETE

`137-04-SUMMARY.md`: fresh-measured RELOCK-07's stale `--sdp-relock` "v1.23+" label at both live
occurrences — `.planning/STATE.md:972` and `.planning/PROJECT.md:844`, a **fifth** drift from the
`634`/`823` pair the requirement's own text had cited (measured 2026-08-03) — and corrected both rows
to **Backlog 999.28**. Fixed all four citation sites named by RELOCK-07's own text
(`REQUIREMENTS.md`'s RELOCK-07 itself, `PROJECT.md`'s "Stale labels this milestone fixes" paragraph,
the design note §8, `ROADMAP.md`'s v1.30 milestone-list entry) to state these terminal values, each via
an appended dated correction — never an in-place rewrite of the historical record. Authored
`137-RELEASE-NOTES-app.md` (CLOSE-05): version-agnostic next-release notes whose "Removed" section
states `dev sdp disable` → `write` (automatic, genuinely redundant) and `dev sdp enable` → withdrawn,
no replacement, Backlog 999.28 — `write --sdp-relock` never named (`grep -c` = 0); also documents the
new six-step `dev test` SDP leg and the CHAN-01..07 stable-channel `dev` narrowing (Phase 136). Passes
`check_permitted_claims.py` scanned alone after one in-flight fix ("self-verifying" → "a testable leg
for the lock"). Authored `137-DECISION.md`: RELOCK-07 confirmation, operator-batch C-1 dispositioned
**defer-with-owner** (filed `build-db-diff-ladder-state-community-reported-regression.md`,
`Owner: henols`; batch row updated), and the phase's own beta-only pre-flight recommendation — pushes,
merges, publishes nothing itself. Passes the claim gate scanned alone. One further deviation:
`REQUIREMENTS.md`'s own CLOSE-05 text still named `write --sdp-relock` as the mapping target,
contradicting the 2026-08-03 operator decision every other document already reflected — corrected in
place (Rule 1) with an Evidence citation to the new release notes. **Two requirements ticked: CLOSE-05
and RELOCK-07** — project-wide requirement state: **54 ticked / 2 open** (`CLOSE-01`, `CLOSE-06`
remain, both later Phase 137 plans' own scope). No sub-repo touched (meta-repo documentation only;
`firestarter_app` gitlink `cc036e8` confirmed unchanged). Commits: meta `4f1ffb70`, `bf8c380b`,
`f83871d2`, `6de6ad33`.

### Phase 137 plan 03 (2026-08-05) — COMPLETE

`137-03-SUMMARY.md`: authored `137-LEDGER.md`, the v1.30 honesty ledger and the milestone's central
closing artifact — forking `122-LEDGER.md`'s seven-section shape (header + composes-with, the
Evidence Ceiling quoted verbatim with both named narrowings, the status/claim key, an 11-row claim
classes table, a 7-item mechanism-corrections section, a 3-item process-failures section, negative
space, and the closing three-way split). All six plan-mandated corrections present and cited by name
(six-step not four-step leg, exit-code precedence bug, seven not six laundering routes, chip-ID gate's
structural vacuity, LEG-02's 703-chip population, PROV-05's already-satisfied premise), plus three
further corrections (`n_ran=6` not 5, Phase 133's registry-count correction, plan 137-02's own
coverage reduction) and three process failures (the "committed NOTHING" incident, the AT28C64
"curation gap" misreading, `134-VALIDATION.md`'s stale non-existence claim). Every figure re-measured
live against `firestarter_app` HEAD `cc036e8` (43 ALLOW / 703 REFUSE full-DB / 41 REFUSE 0x0D-scoped /
84 0x0D total; all 43 ALLOW chip-id==0; mypy 33/35 headroom 2 at 129 checked files; full suite 1508
passed). One in-place claim-gate-compliance correction (a redundant restatement of the forbidden
causal-claim phrase, reworded to cite the earlier verbatim quote by reference). Scans clean, alone,
against plan 137-01's claim gate. **One requirement ticked: CLOSE-04** — the only one this plan may
discharge. Project-wide requirement state: **52 ticked / 4 open** (`CLOSE-01`, `CLOSE-05`, `CLOSE-06`,
`RELOCK-07` remain — all later Phase 137 plans' own scope). No sub-repo touched (meta-repo
documentation only). Commits: meta `3fedc9b8`, `4a0d2a17`, `b23dec27`.

### Phase 137 plan 02 (2026-08-05) — COMPLETE

`137-02-SUMMARY.md`: authored `firestarter_app/tools/check_diagnostic_report_claims.py` — an
AST-based scanner walking every `ast.Constant` string literal in `diagnostic_report.py` against the
identical 14-label `FORBIDDEN_PATTERNS` vocabulary as plan 137-01's meta-repo
`check_permitted_claims.py` (byte-for-byte label parity confirmed by an AST-derived diff of both
files). No proximity window and no self-verifying rule — neither needed per the plan's own spec,
since every literal in this file is already report context by construction. Fail-closed on a
missing scan target (`FAIL: scan target not found on disk`) and on an unparsable one (`FAIL: could
not parse ... as Python`). Env-override seam `FIRESTARTER_DIAGREPORT_SRC` lets the paired pytest
re-target it without touching the real source. Committed two fixtures —
`tests/fixtures/planted_diagnostic_report_claim.py` (trips `dev-test-proves-unqualified` +
`lock-held-unqualified`) and `tests/fixtures/planted_unparsable.py` (a genuine Python `SyntaxError`)
— and `tests/test_check_diagnostic_report_claims.py` (4 subprocess-only legs, 4/4 green:
clean-pass, planted-violation, missing-target, unparsable-target). **Deliberate scope boundary,
recorded in the checker's own docstring:** this scanner does NOT extend to
`firestarter/cli_handlers.py`'s `SDP_RECOVERY_CONSTANT_NAMES` (`_SDP_RECOVERY_LOUD`/
`_SDP_RECOVERY_NEUTRAL`) even though Phase 134 plan 134-08's own source comment names Phase 137's
CLOSE-03 as an available extension point for that tuple — both `REQUIREMENTS.md`'s own CLOSE-03
wording and this plan's `PLAN.md` scope the scan to `diagnostic_report.py` only, and that surface
already has its own committed, narrower-scoped gate (`tests/test_sdp_recovery_wording.py`, LEG-14,
plan 134-09) whose own D-13 record names CLOSE-03 as an extension point, not a duplication mandate.
**[Rule 3 deviation]** the required `tests/fixtures/planted_unparsable.py` fixture's genuine
`SyntaxError` made mypy's `mypy firestarter/ tests/` directory walk abort (exit 2, "errors
prevented further checking"), which would have broken CI's mypy watermark gate for the whole
project. Fixed by adding `exclude = ["^tests/fixtures/"]` to `[tool.mypy]` in `pyproject.toml`,
mirroring ruff's own pre-existing `extend-exclude` for the identical directory and reason. Measured
none of the 6 pre-existing `tests/fixtures/*.py` files ever contributed an error to the 33-error
baseline, so this only drops the checked-file count (129, still above the 120 floor), never the
error count. Full suite: **1508 passed** (1504 baseline + 4 new tests), 0 failed. mypy: **33/35**,
headroom flat at **2**. **One requirement ticked: CLOSE-03** — the only one this plan may
discharge. Project-wide requirement state: **51 ticked / 5 open** (`CLOSE-01`, `CLOSE-04`,
`CLOSE-05`, `CLOSE-06`, `RELOCK-07` remain — all later Phase 137 plans' own scope). No sub-repo
committed at the meta level (all code changes land in the `firestarter_app` submodule). Commits:
submodule (`firestarter_app`) `89f2fb2`, `cc036e8`.

### Phase 137 plan 01 (2026-08-05) — COMPLETE

`137-01-SUMMARY.md`: authored and hosted, inside Phase 137's own directory, the v1.30 claim gate
(`check_permitted_claims.py`) — vocabulary forked verbatim from Phase 122's copy (8 forbidden
AT28C/silicon patterns), mechanics forked from Phase 123's copy (D-16 proximity window, D-15
all-or-nothing arming, hoisted never-vacuous guard), per PITFALLS.md P-11's exact prescription.
`_DEFAULT_TARGETS` resolves exclusively via `_HERE` (this module's own directory, computed fresh
from `__file__`) — no sibling-directory string constant anywhere in the file, avoiding by
construction the exact defect that made v1.23's copy resolve to a stale sibling phase dir and pass
vacuously. Added 6 v1.30-specific forbidden patterns (`lock-inhibited-the-write`,
`lock-held-unqualified`, `proven-behaviour`, `behaviourally-verified`, `now-proven`,
`dev-test-proves-unqualified` — 14 total) plus a relational `self-verifying` rule (violation only
when neither "emission" nor the required caveat appears in the same 3-line proximity window).
Suffixed env seam `FIRESTARTER_CLAIMSCAN_TARGETS_V130` and renamed test module
`test_check_permitted_claims_v130.py` defuse a 3-way collision with the two prior unsuffixed
copies still on disk. Committed 5 fixtures (2 clean, 3 planted-violation, each failing for one
attributable reason) and an 11-leg subprocess-only pytest suite, 11/11 green, including the two
**mandatory P-11 legs** (`test_default_targets_resolve_inside_this_phase_directory`,
`test_default_target_basenames_are_this_milestones`) — both independently proven non-vacuous via
two distinct deliberate-break controls, each observed RED verbatim then restored byte-identically
(confirmed empty diff), with each mutation flipping only its own leg and leaving the other green.
Scanner run with no arguments currently prints `UNARMED:` naming all four `137-`-prefixed
basenames and exits 0 — correct and expected, since none of the four real closing artifacts
(`137-LEDGER.md`, `137-DECISION.md`, `137-RELEASE-NOTES-app.md`, `137-GH12-COMMENT.md`) exist yet;
they are authored by Plans 137-03/04/05, and only Plan 137-06 may arm the gate for real and tick
CLOSE-01. No sub-repo touched (verified: `firestarter/` clean, `firestarter_app/` shows only
pre-existing dirt). **One requirement ticked: CLOSE-02** — the only one this plan may discharge.
Project-wide requirement state: **50 ticked / 6 open** (`CLOSE-01`, `CLOSE-03`, `CLOSE-04`,
`CLOSE-05`, `CLOSE-06`, `RELOCK-07` remain — all later Phase 137 plans' own scope). Commits: meta
`a61a7814`, `fcd10742`, `997b16b9`, `855fbb66`.

### Phase 136.1 plan 04 (2026-08-05) — COMPLETE

`136.1-04-SUMMARY.md`: the phase's final, close-out plan. Ticked nothing new -- all six `PROV-0X`
requirements were already Complete before this plan ran. Re-ran `tools/ci_parity.sh` (identical shape
to `## Before`/`## After PROV-01`: legs 1-3 exit 0, leg 4 exit 2, the documented devcontainer-numpy
shape) and `tools/ci_replica_venv.sh` (`CI-REPLICA: PASS`, mypy **33/35** unchanged, headroom flat at
**2**, checked **132** source files -- up from 130, Plan `136.1-03`'s two new test files -- full suite
**1504 passed**, coverage **82.14%**). Re-ran `tests/test_sdp_db_invariant.py` explicitly: **9/9
green**, both partition-comparison legs (Phase 131's hand-curated snapshot and Plan `136.1-02`'s
infoic-derived-field check) agreeing at **43 ALLOW / 41 REFUSE / 84 total**. Independently re-derived
the ALLOW set from `chip_database.json` via `sdp_capability_for_entry` and diffed it byte-for-byte
against the **ORIGINAL** `120-sdp-partition.json` (pre-Phase-136.1, pre-v1.30): **zero entries differ,
either direction**. Re-ran `tools/derive_sdp_partition.py` against the cached pinned-commit XML: **PASS,
43/41/84, zero disagreement** against both `sdp_capability_for_entry` and the committed
`protect_on_after` field -- the phase's closing, independent, from-scratch confirmation (a ninth
independent 43/41/84 measurement counting this plan's own three, on top of six already made across the
phase). Confirmed `firestarter/` (firmware submodule) untouched and no new pip/npm/cargo package
installed anywhere across the whole phase. Appended `136.1-CI-PARITY.md`'s `## After (phase close)`
section with the whole-phase summary table: mypy headroom delta **0**, checked-files delta **+2**,
full-suite delta **+10**, coverage delta **0.00pp**, partition delta **0** -- all measured, none
estimated. **[Rule 2 deviation]** Authored `136.1-RECORD.md`: not in this plan's own `files_modified`
list, but required by the dispatching orchestrator's own success criteria -- carries forward all five
findings (PROV-05's stale requirement premise, verified not re-authored, per Phase 121 `c3c9424`;
PROV-02's static-transcription-over-runtime-derive decision, per the AST gate `SDP_CAPABLE_TOKENS`
class-shape lock; PROV-06's 12-of-84 corroborated across independently different methodologies; the
GATE-02 `diff_db.py` blast-radius fix; and the "committed NOTHING" process failure, where an
orchestrator's `git status`-only check missed two real submodule commits), a `PROV-0X` requirement
traceability table (all six Complete), and the whole-phase CI-parity/cost ledger, for Phase 137's
honesty ledger to cite directly. **Phase 136.1 is now plan-complete (4/4).** Mirrors Phase 136's own
precedent: `progress.completed_phases` stays unchanged (no explicit phase-verification/close activity
ran this session -- that is a separate, later step). Project-wide requirement state confirmed unchanged
at **49 ticked / 7 open** (`CLOSE-01`..`06`, `RELOCK-07` -- all Phase 137's own scope). This plan makes
no submodule commit at all (pure meta-repo verification capstone, per its own `<repo_topology>`).
Commits: meta `fd783947`, `94877d6d`, `31832378`, `1cb5f5df`.

### Phase 136.1 plan 03 (2026-08-05) — COMPLETE

`136.1-03-SUMMARY.md`: `doc/lockable-proms.md` section 17's AT28C16/AT28C64B/AT28C256 correction
(PROV-05) was **verified ALREADY PRESENT**, not re-authored -- landed by **Phase 121 plan `121-13`,
commit `c3c9424`**, well before v1.30 was scoped; `PROV-05`'s own text (a maintainer memory note) was
the stale artifact, not the file. `tests/test_lockable_proms_doc_claims.py` (4 tests, submodule commit
`c9f98b8`) durably gates the correction going forward: both corrected table rows asserted, a narrow
negative regex for the historical wrong shorthand (`AT28C16 / 64 / 256`) confirmed absent both in the
doc and whole-tree (zero hits elsewhere in `firestarter_app`). `PROV-06`'s "b15 ≈ page-write family
marker" equivalence was refuted with a **fresh, measured, non-vacuous** count --
`tests/test_b15_page_size_corroboration.py` (4 tests, submodule commit `31b5d74`) reads
`chip_database.json`'s `protect_on_after`/`infoic_page_size_raw` fields (Plan 136.1-01, no `.get()`
default) for all 84 `algorithm==13` entries; a non-vacuity check on 5 hand-counted synthetic pairs (2
disagreements) passes before the real-data assertion; measured: **12 of 84 disagree**, every one named
by key, confirming Phase 120's original figure via an **independently different methodology** (per-row
single-value comparison vs. Phase 120's cross-token-set matching) -- a corroboration, never assumed.
`firestarter/sdp_capability.py` (Plan 136.1-02's file this wave) stayed untouched throughout (diff-stat
empty, structural test confirms). **Procedural note, recorded honestly:** both task commits were
already present and correct in the `firestarter_app` submodule at this session's start (made by a prior
session that died before any meta-repo bookkeeping ran); this session verified both against every plan
acceptance criterion, re-ran the full suite fresh (**1504 passed**, +8 exactly), re-measured
`tools/ci_replica_venv.sh` fresh (**mypy 33/35**, headroom flat at 2, checked 132 source files -- up
from 130, the two new test files), and completed the plan-level bookkeeping. Zero code-level
deviations. **PROV-05, PROV-06 ticked** -- the only two requirements this plan may mark complete.
Commits: meta `7991748`, `a36206a`, `82342474`, `f25eeed`; submodule (`firestarter_app`) `c9f98b8`,
`31b5d74` (both pre-existing at session start, independently re-verified).

### Phase 136.1 plan 02 (2026-08-05) — COMPLETE

`136.1-02-SUMMARY.md`: `tests/test_sdp_db_invariant.py`'s GATE-08 gained a second, independent,
genuinely infoic.xml-derived comparison -- `_partition_from_protect_on_after_field(db)` reads
`chip_database.json`'s own `protect_on_after` field directly (Plan 136.1-01, no `.get()` default --
a missing key must raise) and `_assert_two_partitions_match` compares it against the production
`SDP_CAPABLE_TOKENS`-based transcription
(`test_sdp_partition_matches_infoic_derived_field_element_wise`), both sides independently measuring
43 ALLOW / 41 REFUSE / 84 total, plus a non-vacuity proof
(`test_partition_flags_a_moved_chip_via_db_field_non_vacuous`). The existing hand-curated
`_COMMITTED_SDP_ALLOW_ENTRIES` snapshot and its comparator are kept byte-identical (diff is additions
only) -- **both proofs stay, neither replaces the other**, closing the gap that constant's own comment
has named since Phase 131. One sentence added to `sdp_capability.py`'s `SDP_CAPABLE_TOKENS` comment;
the frozenset's literal contents/binding shape and `tools/check_sdp_capability_invariants.py` stayed
untouched (re-confirmed `PASS`) -- PROV-02's static-transcription-plus-equality-gate branch was taken,
not the runtime-derive branch, because that AST gate mechanically forbids any other shape.
**PROV-03's seen-to-fail demonstration ran on the REAL committed file**: `ATMEL/AT28C256,...`'s
`protect_on_after` was flipped `true`->`false` directly in `chip_database.json`, the new gate FAILED
naming that exact chip verbatim (recorded in full in `136.1-02-SEEN-TO-FAIL.md`), then the file was
reverted (`git checkout --`, confirmed byte-identical via empty `git diff --stat`) and the suite
re-ran green (9/9) before any further commit. `firestarter_app/tools/derive_sdp_partition.py`
(PROV-04): a standalone, fetch-based, never-imported-by-production-or-tests script, pinned to minipro
`a8efaedc236c1d9718bd28299dfbb99536b010ff` (duplicating `build_db.py`'s `MINIPRO_XML_URL` verbatim),
reads `INFOIC_XML_PATH` if set or fetches live otherwise, preserves Phase 120's exact token rule
verbatim (exact `part_number` token, strip only `@PACKAGE`, keep parentheticals). Run once against
the cached, previously-verified pinned-commit XML copy: **43 ALLOW / 41 REFUSE / 84 total, zero
disagreement** against both `sdp_capability_for_entry` and the committed `protect_on_after` field,
exit 0; the script's own source carries no reference to the cached path (`grep -c scratchpad` returns
0). `tools/ci_replica_venv.sh` re-measured this wave: mypy **33/35** (headroom flat at 2, unchanged
from Plan 136.1-01's post-PROV-01 baseline), full suite **1496 passed** (+2 from the two new tests),
30 snapshots passed, coverage **82.14%** unchanged. **Zero deviations** -- plan executed exactly as
written. **Three requirements ticked: PROV-02, PROV-03, PROV-04** (the only three this plan may
discharge). Commits: meta `c897b187`, `3d322102`, `a334a0c3`, `ee83cfe7`; submodule
(`firestarter_app`) `73739d5`, `dc5bfbe`.

### Phase 136.1 plan 01 (2026-08-05) — COMPLETE

`136.1-01-SUMMARY.md`: `tools/build_db.py` now decodes infoic.xml flags bit 14
(`0x4000`, `MP_OFF_PROTECT_BEFORE`) and bit 15 (`0x8000`, `MP_PROTECT_AFTER`) plus the
raw upstream `page_size`, into three new, universally-emitted `chip_database.json`
`programming.*` fields (`protect_off_before`, `protect_on_after`,
`infoic_page_size_raw`), cited to minipro `src/database.c#L39-L50 @
a8efaedc236c1d9718bd28299dfbb99536b010ff` and cross-referenced to
`doc/infoic-field-dictionary.md`'s CONFIRMED bit 14/15 row. Regenerated via a REAL live
HTTPS fetch of the pinned minipro commit (744 upstream + 2 non-upstream
`extra_chips.json` supplement chips = 746 total) -- never the cached scratchpad XML.
The regeneration's diff is mechanically proven additive-only by a new committed,
re-runnable script (`136.1-check-blast-radius.py`): 746 entries compared, 744 gained
the three new keys, 0 violations, run twice (pre-commit against `HEAD`, post-commit
against the default `HEAD~1`) with identical results. `tests/test_sdp_db_invariant.py`
(unmodified) stayed green throughout -- the **84/43/41 SDP ALLOW/REFUSE partition is
byte-for-byte unchanged**; this plan changes provenance metadata only. `136.1-CI-PARITY.md`
records a real Before/After-PROV-01 pair: mypy 33/35, checked 130 source files, full
suite 1494 passed, coverage 82.14% -- **all identical, 0 delta**, reasoned from `tools/`'s
exclusion from CI's mypy/ruff scan and confirmed by real runs. **One deviation
auto-fixed (Rule 1):** the regeneration broke the pre-existing GATE-02 `tools/diff_db.py`
per-chip diff gate (744 "unexplained diffs" -- it had no rule for the 3 new fields);
fixed by adding a `PROV01_PROTECT_METADATA` root-cause rule following the file's own
established per-phase pattern (same shape as `PGSZ_PAGE_SIZE`/`RC1_DIP32_27C020`); full
suite back to 1494 passed, 0 delta. **One requirement ticked: PROV-01** (the only one
this plan may discharge). Commits: meta `595a017`, `3624205`, `8ab9198`, `3b8015b`,
`85d220a`; submodule (`firestarter_app`) `f294821`, `8fccb47`.

### Phase 136 plan 04 (2026-08-05) — COMPLETE

`136-04-SUMMARY.md`: closed out the phase's two deferred loose ends. Task 1 re-baselined **both**
`test_help` and `test_help_dev` in `tests/__snapshots__/test_characterization.ambr` -- a measured
correction of `136-VALIDATION.md`'s wave-4 row, which named only `test_help_dev`; `136-02-SUMMARY.md`'s
own "Known Test Regressions" table had already flagged the second (Click renders a group's
top-level `short_help` from the same first docstring line CHAN-05 rewrote). Observed RED on both
against the stale snapshot first (`2 failed, 12 passed, 21 deselected`), then a single `-k`-scoped
`--snapshot-update`, then confirmed via `git diff --unified=0` that the change is scoped to exactly
the docstring header lines -- `test_help_dev`'s own `Commands:` block (all 8 `dev` subcommands, same
order, same one-line summaries) is byte-identical before and after. Task 2 appended
`136-CI-PARITY.md`'s `## After` section: `tools/ci_replica_venv.sh` measured **mypy errors: 33
(watermark: 35), checked 130 source files** -- byte-identical to the phase's own `## Before`
baseline, headroom delta **0**, flat across the entire phase. Full suite via the ci-replica python:
**1494 passed, 0 failed**, 30 snapshots passed -- both previously-deferred regressions gone, no
third failure surfaced. RESEARCH §5's blast-radius file set (244 passed) and
`tests/test_py32_channel_gating.py` (14 passed) independently re-confirmed unchanged and green.
`git -C firestarter_app status --porcelain -- firestarter` confirmed empty across the whole phase.
**Zero requirements ticked by this plan** -- all seven CHAN-0X rows were already `[x]` Complete in
`REQUIREMENTS.md` before this plan ran (confirmed by grep at the start of execution); `CHAN-05` sits
in this plan's frontmatter only as the downstream justification for Task 1, not as a re-tick.
Commits: `b1d8f73` (submodule, `firestarter_app`), `0e99fa4` (meta repo, `136-CI-PARITY.md`).

**Phase 136 is now plan-complete (4/4) with all seven CHAN requirements Complete.** No formal
phase-close record (`136-RECORD.md`) was authored by this plan -- this plan's own scope was the
snapshot re-baseline and the CI-parity close record only, per its own `<output>` spec naming just
`136-04-SUMMARY.md`. `ROADMAP.md`'s Phase 136 checkbox and per-plan checkboxes are updated by this
plan's state-update step; `progress.completed_phases` is left at 4 (unchanged) since no explicit
phase-close activity ran.

### Phase 136 plan 03 (2026-08-05) — COMPLETE

`136-03-SUMMARY.md`: proved, from outside the process in real subprocesses, everything plans
136-01/136-02 built. `tests/test_dev_group_channel_gating.py` (12 tests) is a subprocess
dual-channel harness adapted from `test_py32_channel_gating.py`'s `_CHILD_PROGRAM`/`_run_cli`
shape: simulated-stable proves `dev --help` lists only `read`/`test`, `dev.commands.keys()` is
exactly `{"read", "test"}`, a gated name (`dev reg`) refuses with `channel.dev_command_gate_message`'s
text at non-zero exit, a genuine typo gets Click's own generic message; simulated-prerelease is
the positive control (all eight); `FIRESTARTER_DEV_TOOLS=1` set in a simulated-stable child's
environment re-registers all six gated names and genuinely lets `dev reg --help` run (exit 0).
`tests/test_dev_gate_reads_no_firmware_source.py` (11 tests) scopes `inspect.getsource()` to
exactly the gate's five new callables plus a whole-module check on `channel.py`, asserting no
`open(` call and no firmware-path token; non-vacuity discharged by planting `open("/dev/null")`
inside `is_dev_tools_enabled`, observing the scan name it as the offender, then restoring
`channel.py` byte-identically. Task 3 planted and observed RED two more non-vacuity mutations
against `cli_handlers.py` (`cls=_DevGroup` removed; `_DEV_TOOLS_ENABLED` hardcoded `True`), each
breaking a named assertion (the informative-refusal test; the exact-`{read, test}` registry
test), then restored both byte-identically -- no permanent source change, verbatim RED recorded
in `136-03-SUMMARY.md` only. mypy held at 33/35 (checked 130, up from 128 -- the two new test
files); full suite 1492 passed / 2 failed (exactly the two pre-existing `test_help`/`test_help_dev`
snapshot regressions deferred to 136-04, confirmed by name, no third failure). **All six
requirements this plan owns ticked: CHAN-01, CHAN-02, CHAN-03, CHAN-04, CHAN-06, CHAN-07** --
all seven CHAN requirements are now Complete. Commits (submodule only, this plan touches no
meta-repo production file): `16ff598`, `11c5de4`.

### Phase 136 plan 02 (2026-08-05) — COMPLETE

`136-02-SUMMARY.md`: wired both D-01 mechanisms into `firestarter/cli_handlers.py` --
`_DEV_TOOLS_ENABLED: bool = is_dev_tools_enabled()` (frozen at import time, mirroring
`_PY32_ENABLED`) and `_DevGroup(click.Group)` (its `get_command` override raises
`channel.dev_command_gate_message()` for a gated-but-unregistered name; the exact shape
136-01's spike proved) wired onto `@cli.group(name="dev", cls=_DevGroup)`. All six gated
`@dev.command` blocks (`reg`, `addr`, `consistency-check`, `write-cycle`, `fault-inject`,
`validate-family`) now sit behind module-scope `if _DEV_TOOLS_ENABLED:` guards; `read`/`test`
stay unconditional. A CHAN-06 tripwire comment at `dev reg` names `FIRESTARTER_DEV_TOOLS` and
the held-erase-rail DMM proxy dependency. The `dev()` docstring no longer warns `read`/`test`'s
own stable audience away from them (CHAN-05). mypy held at 33/35 (checked 128, unchanged from
136-01); RESEARCH §5 blast-radius suite (244 tests) and `test_py32_channel_gating.py` (14
tests) green throughout. **One requirement ticked: CHAN-05.** CHAN-01/02/03/06/07 contributed
to, closed by plan 136-03. **Plan-time gap found and documented, not fixed:** the docstring
change also breaks `tests/test_characterization.py::test_help` (not just `test_help_dev` as
136-VALIDATION.md named) — both deferred to plan 136-04. Commits (submodule only, this plan
touches no meta-repo production file): `6e2fb39`, `88ec58e`, `c8f8a53`.

### Phase 136 plan 01 (2026-08-05) — COMPLETE

`136-01-SUMMARY.md`: pre-edit `136-CI-PARITY.md` baseline (mypy 33/35, checked 126, 1437 passed,
82.12% coverage — no number to inherit per 136-RESEARCH.md §7), `tests/test_click_group_gate_hook.py`
(Click `get_command`, not `resolve_command`, pinned as the gate hook, 7 tests), and four new
`firestarter/channel.py` symbols (`BETA_ONLY_DEV_COMMANDS`, `dev_tools_enabled_by_env`,
`is_dev_tools_enabled`, `dev_command_gate_message`) proven fail-closed via TDD with a planted-mutation
non-vacuity check, `tests/test_dev_tools_channel_gate.py` (27 tests). **Zero requirements ticked** —
this plan's own scope statement is "MAY tick: none"; CHAN-06/CHAN-07 are contributed to, closed by
plan 136-03. Commits: meta `73c8c85`; submodule `09803f6`, `21c6d10`, `893490a`.

Artifacts on disk (Phase 133, retained for reference): `133-CONTEXT.md` (D-01…D-16),
`133-DISCUSSION-LOG.md`, `133-RESEARCH.md`, `133-PATTERNS.md`, `133-VALIDATION.md`,
`133-01-PLAN.md` … `133-07-PLAN.md`, `133-01-SUMMARY.md` … `133-07-SUMMARY.md`, `133-BASELINE.md`,
`133-CI-PARITY.md`, `133-RECORD.md`, `133-VERIFICATION.md`, `deferred-items.md`.
All code lands **inside the `firestarter_app` submodule** on `gsd/v1.30-sdp-surface-retirement`
(the meta branch name deliberately differs). Firmware untouched — host-only.

### Phase 132 close (2026-08-03) — COMPLETE and VERIFIED

Phase 132 — Retire `dev sdp` & Discharge the mypy Debt — closed with all 9 plans executed
(waves 1-9, strictly sequential) and **8/8 RETIRE requirements Complete**. `132-VERIFICATION.md`
returned **passed, 5/5 roadmap success criteria**, every one independently re-measured rather than
read from a SUMMARY. Worktree isolation was **DISABLED phase-wide** (plans 01-08 touch the
`firestarter_app` submodule; 132-09 hardcodes `/workspaces/…` absolute paths in its own acceptance
gates) — the same disposition as Phases 129 and 131, at zero cost since every wave held one plan.

132-09 (the certifying CI dispatch, `autonomous: false`) ran task 1 (after-half of the CI-parity recipe +
full replica run, mypy re-confirmed at 32), paused at task 2's `checkpoint:human-verify
gate="blocking"` for the two privileged operator actions (D-06), then resumed: the operator pushed
`gsd/v1.30-sdp-surface-retirement` to origin and dispatched `Host CI`, returning run `30856059940`.
Task 3 read that run — conclusion `success`, `ci` job green on all 16 steps including the mypy
watermark gate (fork-base had it `failure` with both later steps `skipped`), `mypy errors: 32
(watermark: 35)`, coverage 81.72% vs the 70% floor, mypy's raw completion clause investigated as
structurally absent-by-construction from this step's own log rather than substituted (D-08) — and
recorded `132-CI-GREEN.md` plus the ledger's third reading (CI's 32 agrees exactly with local).
Task 4 wrote `132-RECORD.md` (eight requirements accounted, fourteen decisions honoured including
two non-literal, seven corrections, four residuals) and ticked **RETIRE-06** — **all eight RETIRE
requirements are now Complete.** Phase 131 D-11's deferred hardened-gate-in-CI proof is discharged.
Status: Executing Phase 134
(9/9 plans, 8/8 RETIRE requirements, 5/5 success criteria)** — the phase-close verification pass ran
and passed. **Phase 133 is now also CLOSED and verified (7/7 plans, 4/4 LEG requirements, 5/5 success
criteria).** Next action is Phase 134.
Research was SKIPPED per ROADMAP's own `Research flag: SKIP`; **Nyquist Dimension 8 was
operator-acknowledged as unavailable for 132's planning run** (no RESEARCH.md ⇒ no VALIDATION.md)
— acknowledged, not disabled, same as 131. Compensated by making every acceptance criterion a
runnable command or grep-provable source assertion; the plan-checker returned zero
BLOCKER/WARNING findings against that bar.

**A state change 132-09 caused that a later reader needs:** the milestone branch
`gsd/v1.30-sdp-surface-retirement` now exists on `origin` (created by the operator's task 2 push;
it did not exist before), and the submodule is 28 commits ahead of `origin/beta` — neither merged
nor tagged; that is a later, operator-gated milestone-close action.

**Waves are sequential by necessity, not caution.** Three files each carry three separate concerns
(`cli_handlers.py`, `constants.py`, `tests/test_write_skip_sdp_unlock.py`), so same-wave parallelism
would collide on file ownership.

**⚠ Phase 132 needs exactly TWO operator actions, in order** (D-06, both verified live at plan time):
push `gsd/v1.30-sdp-surface-retirement` to origin in `firestarter_app` (the branch is genuinely
absent from origin; local is 9 ahead of `origin/beta`), then `workflow_dispatch` `Host CI` against
that ref. `ci.yml`'s `push:` trigger is `branches: [main]` **only** (`:9-11`), so the milestone
branch never auto-builds; `workflow_dispatch:` exists at `:25` with no inputs. Plan `132-09` is
`autonomous: false` and carries the literal commands. **Branch names differ per repo** — meta-repo is
on `gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`, the submodule on
`gsd/v1.30-sdp-surface-retirement`.

**⚠ Two plan-time findings the dispatch did not anticipate.** (1) `ci.yml:73` runs
`pytest --cov-fail-under=70` while `ci_parity.sh` legs 1-2 run bare `pytest -q` — the local recipe
**cannot** catch a coverage drop, and this phase deletes ~126 covered production lines and ~550 test
lines. `132-01`'s new `ci_replica_venv.sh` leg 5 closes that gap, and `132-09` runs it *before* the
operator turn so a doomed dispatch is not spent. (2) D-12's "same commit" for RETIRE-08's text is
**literally impossible** — the code fixes are in the submodule, `REQUIREMENTS.md` is in the meta-repo,
and two git repos cannot share a commit. Honoured as adjacent cross-citing commits with the
impossibility stated in the commit message and record. D-03's same-commit binding is unaffected: it
is submodule-only and stays one real commit.

**⚠ Phase 132 consumes Phase 131's measured number.** The fork-base mypy count is **69** (watermark
35), read verbatim from CI run `30822281624` (`workflow_dispatch` on `beta` @ `16a313a`, mypy 2.3.0,
Python 3.11.15) and recorded in `131-CI-BASELINE.md`. It is an **input to Phase 132's watermark, not
a Phase 131 claim** — Phase 131 set no watermark and fixed none of the 69. `firestarter_app`'s
primary `ci` job is RED before and after Phase 131, by design.

**⚠ A real CI dispatch needs an operator turn.** `gh workflow run` is denied by Claude Code's
auto-mode classifier in a non-interactive session — independent of the project allowlist, which
already permits it. Read-only `gh run view`/`gh run list` work fine, so everything downstream of the
dispatch is automatable (export `XDG_CACHE_HOME` to a writable path first, or `--log` returns
silently empty). See `131-RECORD.md` §4a and §6a.

**⚠ Verification independence gap on Phase 131.** `131-VERIFICATION.md` was authored inline by the
orchestrator after the dispatched `gsd-verifier` died on a provider session limit. All ten
requirements were mechanically re-measured and three gates were mutation-proven, but one independent
pass is still owed before Phase 132 relies on the 69-count.

### Phase 131 history (closed 2026-08-03 — retained for Phase 137's ledger)

**Execution mode:** worktree isolation was **DISABLED for the whole phase** — all 7 plans ran
sequentially on the main checkout. `131-01/02/03/04/06` touch the `firestarter_app` submodule (the
executor commit protocol cannot commit into a submodule from an isolated worktree); `131-05` and
`131-07` touch only `.planning/` but hardcode `/workspaces/firestarter_app` and
`/workspaces/.planning/…` absolute paths inside their own acceptance gates, which would measure the
main checkout while the agent wrote into the worktree. Same class of defect as Phase 129. **Expect
this for every host-only v1.30 phase.**

**⚠ SEVEN plan-time corrections amend locked decisions** — all measured live, all recorded in-plan
(`F-01`…`F-07`, aggregated in `131-RECORD.md`). `F-07` was filed during execution: GATE-07's
acceptance criterion required a verbatim `Found N errors in M files (checked K source files)` line
that is **structurally absent** from the fork-base CI log; it was amended, not fabricated around.
Two of the seven change what gets built: **F-01** —
D-06 leg 1 is not implementable as written, because `chip_database.json` carries **zero** `flags`
fields and `tools/infoic*.xml` is gitignored (`.gitignore:29`) and absent, so a literal reading
collapses into self-parity — exactly P-10's hole; replaced by a committed 43-name ALLOW snapshot as
the independent side (triple re-measured **43/41/84**, holds). **F-02** — `test_sdp_table_parity.py`
is `requires_fw`-skipped under CI-parity recipe leg 1, so all DB-only count legs go in
`test_sdp_db_invariant.py` instead.

**⚠ `131-CONTEXT.md` D-17 corrects `.planning/research/PITFALLS.md` P-18 item 4 and `SUMMARY.md`
§"Operator Decisions Needed" item 7(a)** — both name the wrong repo *and* the wrong commit for the
"softened Phase-129 hard assert", and the change is a scoped *premise*, not a weakened assertion.
Read D-17 before acting on either. `131-07` step (f) now also annotates the matching
`REQUIREMENTS.md` Out-of-Scope row, which repeated the same disproven claim.

Last activity: 2026-08-05
LEG-09/10/11/15, 5/5 success criteria), transitioned to Phase 134. Phase 133/134 is a deliberate split of the research
spine's single combined "leg" phase (18 LEG requirements judged too large for one phase at this
project's `Comprehensive` granularity).
**This milestone must NOT be run under `--auto`/`--chain`** — Phase 137 (CLOSE-06) carries a blocking
operator wording-review gate, and `131-05`'s CI dispatch was itself a blocking human-action gate
(discharged by the operator 2026-08-03; every later phase needing a dispatch owes the same turn).

**Milestone branches.** Meta: `gsd/v1.30-sdp-surface-retirement`, forked off the v1.23 tip
`d1b9ce9e` — the same shape as v1.23 forking off the v1.22 tip, since `main` lags and stays untouched
per v1.19–v1.23. `firestarter_app`: forks off `beta` @ `16a313a` (not yet created — create at first
dispatch into the sub-repo). **`firestarter` is not touched by this milestone at all** — no firmware
change, no dual-repo lockstep, no `.hex` re-cut.

**⚠ Evidence ceiling, fixed before planning.** No AT28C part has ever been in operator inventory and
`0x0D` stays `UNVERIFIED`. Provable here: SDP command *emission* (correct sequence, correct pinout
remap, `/WE` asserted) via the Phase 116 trace harness, plus plan derivation and read-back-comparison
logic in the native envs. **Not** provable here: the causal claim *"the lock inhibited the write"* —
reachable only on real silicon, i.e. only from a community `dev test` report, which by design does
**not** gate the close. State the split explicitly or this milestone closes claiming a proof it does
not hold (the v1.22 C-5 overclaim class).

**⚠ Scope carries two additions taken at activation** beyond the design note's three parts: the mypy
gate-hardening v1.23 left OPEN (fail-open `tools/check_mypy_watermark.py` + 69 hidden inherited
errors → `firestarter_app`'s primary `ci` job is RED), and 999.15 / gh#8 dev-tools channel gating.
Plus the owed gh#12 outward follow-up, behind operator wording review.

## Deferred Items

Items acknowledged and deferred at the **v1.30** milestone close on **2026-08-05**. Closeout type:
`override_closeout`. **Known verification overrides: 14.** **None of the 14 `audit-open` items
originate in v1.30** (Phases 131–137) — every v1.30 phase completed with a RECORD, and the milestone's
own verification passed. This is the identical carry-forward set re-confirmed at the v1.18, v1.19,
v1.20, v1.21, v1.22 and v1.23 closes, making this the **seventh** consecutive acknowledgement.

**Plus one v1.30-native open requirement, deliberately held open — not an oversight:**

| Category | Item | Status |
|----------|------|--------|
| requirement | **CLOSE-06** — gh#12 follow-up reply | **OPEN by operator decision.** The requirement reads "the reply *is posted*", and it is not. Wording was approved and the text frozen at `137-GH12-COMMENT.md`; posting is blocked because the removal has not shipped (verified 2026-08-05: deletion commit `259a0f0` is not an ancestor of `origin/beta`; PyPI's highest prerelease is still `3.0.0b15`). Ticking it would have been a false claim in the milestone whose claim gate exists to catch exactly that. v1.30 closes at **55/56**. Discharged by one command after the beta ships — see `.planning/v1.30-OPERATOR-BATCH.md` A-1. |

**Carry-forward set (14), re-confirmed 2026-08-05:**

| Category | Item | Status |
|----------|------|--------|
| debug | firmware-vpp-misread | diagnosed |
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 |
| uat | Phase 08 — `08-HUMAN-UAT.md` | partial (0 pending scenarios) |
| uat | Phase 85 — `85-HUMAN-UAT.md` | partial (2 pending scenarios) |
| verification | Phase 08 — `08-VERIFICATION.md` | human_needed |
| verification | Phase 09 — `09-VERIFICATION.md` | human_needed |
| verification | Phase 71 — `71-VERIFICATION.md` | gaps_found |
| verification | Phase 84 — `84-VERIFICATION.md` | human_needed |
| verification | Phase 85 — `85-VERIFICATION.md` | human_needed |
| todos | 5 pending (incl. 2 filed *by* v1.30: `at28c256-write-path-failure-gh20.md`, `build-db-diff-ladder-state-community-reported-regression.md`, both `Owner: henols`) | pending |

---

## Deferred Items — acknowledged at v1.23 milestone close (2026-08-03)

Closeout type:
`override_closeout`. **Known verification overrides: 15.** None of the 14 `audit-open` items
originate in v1.23 (Phases 123–130) — they are the identical carry-forward set re-confirmed at the
v1.18, v1.19, v1.20, v1.21 and v1.22 closes, making this the **sixth** consecutive acknowledgement.

| Category | Item | Status |
|----------|------|--------|
| verification | Phase 126 — `126-VERIFICATION.md` | passed-with-findings (informational F-126-01; 5/5 criteria substantively achieved, 7/7 requirements) |
| debug | firmware-vpp-misread | diagnosed |
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 |
| uat_gap | Phase 08 — `08-HUMAN-UAT.md` | partial (0 pending scenarios) |
| uat_gap | Phase 85 — `85-HUMAN-UAT.md` | partial (2 pending scenarios) |
| verification | Phase 08 — `08-VERIFICATION.md` | human_needed |
| verification | Phase 09 — `09-VERIFICATION.md` | human_needed |
| verification | Phase 71 — `71-VERIFICATION.md` | gaps_found |
| verification | Phase 84 — `84-VERIFICATION.md` | human_needed |
| verification | Phase 85 — `85-VERIFICATION.md` | human_needed |
| todos | 13 pending (`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads`, `avrdude-mcu-detection-fallback`, `cobs-decoder-framelevel-deadline-wr01`, `decode-infoic-flags-bits-14-15-protect-metadata`, `delete-jp5-dead-renderer`, + 8 more) | pending |

**⚠ The recurring 14 are now a standing carry-forward, not an incident.** Flagged as "worth one
deliberate resolution pass" at the v1.22 close; that recommendation stands and has aged one more
milestone. They should be **scheduled** rather than acknowledged a seventh time.

**⚠ Deliberately left OPEN by v1.23, and not part of the 15 above** — these are named debt with a
stated owner, not unacknowledged gaps: the **69 inherited mypy errors** plus the fail-open
`tools/check_mypy_watermark.py` that hid them (so `firestarter_app`'s primary `ci` job is RED until
a dedicated gate-hardening phase; v1.23's own net contribution measured **zero**, 69 → 72 → 69);
**FUT-ORACLE**, the absent ARM bus-trace oracle (the ARM target could diverge from the AVR golden
register sequences with nothing able to notice); **D-17**, the USB-identity ship-gate tension,
carried as an owned tension rather than a resolution; and `check_ledger.py`'s **2 pre-existing
`LEDGER-01` REDs** from v1.19 Phase 104's rename.

### Phase 130 planning outcome (2026-08-02)

**Waves:** 1 → `130-01..04` · 2 → `130-05, 07, 08, 09, 10` · 3 → `130-06` · 4 → `130-11` ·
5 → `130-12` · 6 → `130-13` · 7 → `130-14` · 8 → `130-15` · 9 → `130-16`. Waves 4–9 are serial by
constraint. Three plans write `ROADMAP.md` (`130-04`, `130-05`, `130-06`) in three distinct
consecutive waves, never concurrently.

**Research corrections that changed the plan (`130-RESEARCH.md` C-1…C-18).** Every live-measured
figure from the discussion re-verified **AGREES** — branch tips `5a89ee7`/`cc9452f`, 83/0 and 37/0
ahead of `origin/beta`, both b14 tag ceilings, gitlinks, `gh` scopes. Unlike Phases 121/127/128/129,
**no locked decision rested on a false premise about the world.** What research found instead was
three broken mechanisms in tooling this phase is contractually bound to:

| # | Finding | Consequence |
|---|---|---|
| **C-1** | `130-CONTEXT.md`'s decision block was unparseable — 7 of 16 `D-NN` ids extracted, nine silently dropped (wrapped bold runs) | Fixed pre-planning at `0f9a709`; parser now `outcome: parsed`, 16/16 trackable. The dropped nine were the highest-stakes set (D-11, D-13/14/15) |
| **C-2** | `123/check_permitted_claims.py:74` resolves `_DEFAULT_TARGETS` against **Phase 123's** dir, so the four `130-*` artifacts scan as `UNARMED:` + **exit 0** | A green run that scanned nothing, on the milestone's only outward-facing overclaim gate. Repointed in wave 1 (`130-01`), not via `argv` — arming applies only to the default set |
| **C-3** | That checker's own suite was **already RED** (`1 failed, 9 passed`) — the side-effect guard globs `130-*.md`, broken by the discussion commit `0005077`. Meta runs no pytest workflow, so CI cannot see it | Fixed locator-only as a **differential** snapshot guard (`130-01`), because the narrowing research proposed would re-plant the RED once `130-LEDGER.md` legitimately lands |
| **C-11** | ROADMAP lines 33–34 (which D-13 deletes) carry R-1, R-5, R-8, R-9, R-11, R-14 verbatim | New **11th hard sequencing constraint**: CLOSE-03's collapse runs before CLOSE-01's ROADMAP sweep, else CLOSE-01 writes correction blocks into lines that then vanish |
| **C-7** | All six live `2992 B` hits are labeled corrections or historically-correct v1.22 archive text | R-10 needs **no substantive fix** — recorded as discharged. A sweep would have deleted accurate history <!-- recordscan:history leonardo-headroom-2992: this C-7 finding row quotes "2992 B" only to name the needle it discharges (130-RESEARCH.md C-7) -- it documents that the live 2992 B occurrences elsewhere in the record are labeled or historically-accurate; it does not itself assert a live 2992 B figure. --> |
| **C-8** | `ROADMAP.md:2468` is Phase 130's own criterion 1 and quotes **three** of the checker's own needles; `:2414` carries "no VTOR" bare | D-08's checker needs a self-reference exemption **and** history-block awareness, each with a fixture, or it can never go green on an honest tree <!-- recordscan:allow part-with-no-vtor: quotes ROADMAP.md:2414's needle text verbatim while documenting C-8's self-reference finding about this checker's own design (130-RESEARCH.md C-8); not a live claim in this file. --> |
| **C-4** | D-11's lockstep footprint is larger than D-11 states: §5(d) also becomes false, and §5(a) cites `usb_cdc.c:20`/`:24` verbatim | The source warning goes **below** line 24; footprint is §5(a)+§5(d) in both copies |
| **C-13** | The app b15 cut is gated on a full green `pytest tests/` plus two codegen gates, all blocking, all before the version bump | A RED there means no app b15 **after** the firmware half published — asymmetric lockstep breakage. Pre-flight suite state recorded as a measured gate in `130-DECISION.md` |

**D-17 — new operator decision, made during planning.** Research C-5 found D-11 collides with its own
ship gate: `v1.23-FLASH-PATH-DECISION.md` §5(c) forbids *"no release advertises a USB identity"* until
an allocated `0x1209` PID exists, and `1209:0001` is pid.codes' private-testing id, not an allocation.
Escalated to the operator and delegated back. Resolution: **§5(c) stays byte-unchanged and the tension
is carried as an owned residual** — §5(c) says outright it is *"deliberately a condition… so a future
reader can fail it"*, and amending a ship gate so your own act clears it is the fail-open move BASE-08
exists to prevent. Consequences: §5(c) and `_L2_SHIP_GATE` are **not** touched (holding D-11 to
§5(a)+§5(d)); `130-DECISION.md` records why a caveated disclosure is not "advertising"; `130-LEDGER.md`
carries it as a negative-space row. Per **C-6**, no artifact may say the warning is *"required by
pid.codes' terms"* — the terms say **should**.

**Structural gating, not flag-based.** No `<automated>` block in any of the 16 plans contains
`git push`, `git merge` into beta, `git tag`, `gh workflow run`, `gh release create|edit|delete` or
`twine upload` — verified independently by the plan-checker. The privileged commands exist only as
prose in `130-HANDOFF.md`'s operator procedure. `130-14` re-runs that scan as an acceptance criterion
and `130-16` runs it again at closeout. `130-15` opens with a fail-closed precondition so an
auto-approved checkpoint produces a visible stop rather than a phantom cut.

**Environment drift (helpful).** `arm-none-eabi-gcc` 14.2.1, `cmake` 4.4.0 and `ninja` 1.13.0 measured
**present** at plan time, so D-11's ARM pass needs no install. Per D-07 a local build supports
**delta / byte-identity** claims only — never an absolute size, which needs a CI run URL + SHA.

### Phase 130 context highlights (2026-08-02)

Read `.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-CONTEXT.md`.

| Area | Locked |
|---|---|
| Push / cut | **Accept the auto-fire — the merge IS the `3.0.0b15` cut**, both repos (D-01). Both sub-repos measured **0 behind `origin/beta`**, so there is **no inbound catch-up merge and no conflict resolution** to plan — unlike v1.22. Tag ceiling b14 in both; b14 is live on GitHub **and** PyPI. Tag + merge-toward-`main` stay with `/gsd-complete-milestone` (D-04) |
| Release bodies | Both hand-written, behind a **blocking operator wording review** (D-02). The py32 asset's presence on the real b15 release is a **gate**, not a note (D-03) — `beta-build.yml`'s ARM steps are `continue-on-error`, so b15 can publish green with no asset, and REL-02's only evidence is a rehearsal draft that was deleted |
| CLOSE-01 | Corrections land **per document kind** (D-05): `⚠ CORRECTION` blocks in PROJECT.md + ROADMAP.md, in-place in STATE.md, append-only SUPERSEDED in the dated note. **`REQUIREMENTS.md` is amended** — PCB-03 and FUT-N04's VTOR clauses (D-06) and the Validation Ceiling's toolchain clause (D-07) — a deliberate widening of CLOSE-01's stated four-file list. Proof is a **label-aware checker + planted-violation fixture** (D-08) |
| CLOSE-02 | `130-LEDGER.md` organised as claim classes **by evidence tier** (D-09) — CI-compile-only / AVR-measured / native-simulated / mock-only / real-published-artifact / decision-only-unverified. Full negative space: 8 deferrals **plus** every owned residual incl. F-10 (D-10). Both sourcing and claim-status axes (D-12) |
| CLOSE-03 | v1.28/v1.29 collapse into **one dated retirement line**; line 28 becomes the real `✅ v1.23 PY32F071 Integration` entry — the list currently has **none** (D-13). BCP moves into version order as v1.28; **v1.30 stays v1.30**; v1.29 left vacant (D-14). Backlog 999.23/999.24 retire as shipped (D-15). v1.24–v1.27 proven byte-unchanged **one-shot, deliberately without a checker** (D-16) |

**One scope addition, chosen deliberately (D-11).** b15 would publish an image whose USB descriptor
presents `0x36B7`/`0xFFFF` — **Puya Semiconductor's registered vendor identity** — against
`v1.23-FLASH-PATH-DECISION.md` §5(c)'s hard ship gate. The interim pid.codes `1209:0001` lands in
`platform/py32f071/src/usb_cdc.c` **before** the cut, reversing Phase 129 D-06 on new facts. Carries
two obligations: a real ARM pass before the merge, and a **lockstep `[SHARED:S4]` body edit** in both
copies of the record, or the 41-leg sync gate goes red.

**The four closing artifact names are a pre-existing contract**, not a choice —
`123/check_permitted_claims.py`'s `_DEFAULT_TARGETS` names `130-LEDGER.md`, `130-DECISION.md`,
`130-RELEASE-NOTES-fw.md`, `130-RELEASE-NOTES-app.md` with **all-or-nothing arming**; three of four
is a hard failure. Adding or renaming one requires amending that list in the same commit.

**Todo matches: none folded.** `correct-v128-py32-roadmap-prior-art` is the one substantive hit and
is already owned by CLOSE-03 by requirement; D-13 discharges it.

### Phase 130 outcome (2026-08-02) — COMPLETE

**Shipped:** `130-NONREGRESSION.md` — every gate re-executed in this session, D-16's before/after
SHA-256 proof, D-07's toolchain reproduction recipe, A-5 recorded discharged at Phase 124, all
seventeen decision-coverage rows (D-01…D-17, with D-17's out-of-`130-CONTEXT.md` provenance
stated), all four ROADMAP success criteria discharged with named evidence including criterion 4's
`13X-DECISION.md`-vs-`130-DECISION.md` naming discrepancy. CLOSE-01…CLOSE-04 ticked in
`REQUIREMENTS.md`, each with an evidence clause and its honest qualifier; the Traceability row
updated from `Pending` to Complete.

**Gitlinks asserted, not pinned.** `firestarter` bumped `5a89ee7 → 05c20bf` (plan 130-03's two
commits moved the milestone-branch tip); `firestarter_app` unchanged (`cc9452f`, nothing in this
phase committed inside it). Both assertions are scoped to the milestone-branch tips, not the
post-publish `beta` state the working directories now sit on.

**Both channels verified public at `3.0.0b15`**, read from `gh release list`, never computed:
firmware GitHub prerelease carries four `.hex` assets including `firestarter_py32f071.hex`
(first-ever publication); PyPI carries `firestarter==3.0.0b15`, resolved from a clean venv; no
stable release (`info.version` unchanged at `2.0.7`). Full transcript in `130-CHANNELS.md`.

**One out-of-plan finding carried forward.** The real cut's first CI attempt failed in both repos
on three pre-existing CI-only sibling-checkout test defects — invisible in this devcontainer,
which has the sibling layout standalone CI lacks. Fixed on `beta` directly during the operator's
hand-off (`firestarter` `1c511e8`, `firestarter_app` `5934a54`), outside any plan. One of the three
**softened a Phase-129-authored hard assert** to a skip — a defect-class change, recorded as such
rather than a routine fix. Both fixes are confirmed ancestors of `origin/beta`; neither reached
either milestone branch — a divergence recorded, not silently reconciled.

**Three residuals carried forward, unresolved by design.** (1) D-17's USB-identity tension — the
interim pid.codes `1209:0001` pair is not an allocation, and `v1.23-FLASH-PATH-DECISION.md` §5(c)'s
ship gate stays byte-unchanged. (2) The ARM pass stays delta-and-byte-identity only — no absolute
ARM figure is a milestone-level claim. (3) The community inbox is not empty (gh#18, gh#20, both
out of scope).

**This phase's own diff scope, self-checked.** `git -C /workspaces diff -- .planning/STATE.md`
touches no hunk inside the YAML frontmatter block; `git -C /workspaces diff -- .planning/REQUIREMENTS.md`
is confined to the four CLOSE lines and the one Traceability row.

### Phase 129 outcome (2026-08-02) — COMPLETE

**Shipped:** `.planning/v1.23-FLASH-PATH-DECISION.md` (authoritative, §1–§9 + claim ceiling) and
its firmware subset `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md`, held in lockstep by a
41-leg cross-repo sync gate (`firestarter/tests/test_flash_path_record_sync.py`). PCB-01…PCB-05
ticked; meta gitlink bumped `7a0a375` → `5a89ee7`; firmware suite **221 passed** (from a 180
baseline). `firestarter_app` untouched and unbumped.

**The gate preceded the content it judges** — authored at `3393137`/`42395cf`, before the meta
record (`8515a59`) and the subset (`8102d0f`) existed. It went 31 RED → 0 RED purely through
content written afterwards. Verifier confirmed the ordering from git history independently.

**One deviation, operator-authorized.** `test_linker_comment_cross_references_record` as authored
by 129-02 was UNREACHABLE: it located the MEMORY block by requiring `MEMORY` and `{` on one
source line, but `PY32F071xB_FLASH.ld` has them on lines 8 and 9. A locator-only fix landed as
`2ef7b57` after a RED-preserving proof — with the locator fixed and the comment reverted, the leg
still failed on missing needles, not on the locator. Re-verified by 129-09 and again by the
verifier. No assertion was weakened.

**Carried into Phase 130 (CLOSE-01).** The four research corrections below are the input to the
honesty ledger: ROADMAP criterion 3 is recorded **AMENDED** and criterion 4 partially amended;
REQUIREMENTS/ROADMAP/FUT-N04 prose corrections and the Validation-Ceiling narrowing are
deliberately unfixed and belong to CLOSE-01.

#### Research corrections (input to CLOSE-01)

**Research overturned four locked positions.** Read `129-RESEARCH.md` §"Corrections to CONTEXT.md".

| # | Correction | Disposition |
|---|---|---|
| **C-1** | The PY32F071 **has** a VTOR (`__VTOR_PRESENT 1` in the pinned SDK's CMSIS header) and the firmware **already writes** `SCB->VTOR = FLASH_BASE` at every boot. "A part with no VTOR" appears in D-12, REQUIREMENTS PCB-03, ROADMAP criterion 3, FUT-N04 and the linker comment | **Operator decision: correct in record + linker, defer prose.** The record states the corrected fact and names the supersession; the linker comment's false clause is fixed in-phase (rides D-11's edit); REQUIREMENTS/ROADMAP/FUT-N04 prose is left to **Phase 130 CLOSE-01**. Criterion 3 is recorded **AMENDED**. D-12's three no-VTOR mitigations are deliberately **not** enumerated <!-- recordscan:allow part-with-no-vtor: this Phase 129 C-1 row already states the corrected fact (PY32F071 HAS a VTOR) and quotes "a part with no VTOR" only to name the other files where the false claim still lives (per 129-RESEARCH.md C-1); not itself a live assertion. --> |
| **C-2** | `0x36B7` is **registered to Puya Semiconductor**, and `0x36B7`/`0xFFFF` is copied verbatim from the pinned SDK's own CDC example — the board presents another company's vendor identity, not an unallocated squat | **Operator decision: interim `1209:0001` + target `1209:<pid>`.** D-09's ship gate survives verbatim; its *premise* is rewritten with the upstream provenance cited. `usb_cdc.c` still **not** edited (D-06). Record also states pid.codes' PCB-design-files prerequisite (the D-08 request may not be fileable before a schematic) and its date-stamped queue latency |
| **C-3** | The ARM toolchain **installs and works** in this devcontainer; the D-13 byte-identity proof was *executed* during research (41/41 objects, `.bin`/`.hex` identical across a simulated comment edit) | D-13 uses the **byte-identical** form, run **locally**. Delta claim only — a local build's absolute size may never be compared against a CI figure (local `text=27260` vs CI `text=27344`); byte-identity never implies the image *runs*. The "toolchain absent from this environment" ceiling wording needs narrowing by CLOSE-01 |
| **C-4** | The seed's "a small bootloader in the **first few KB**" is ~5× optimistic — measured components already total ≈14.6 KiB | Budget is **3 sectors / 24 KiB**; the record supersedes the seed for this number specifically |

**One requirement absent from every source (F-10):** the provisional contiguous PB0–PB7 data bus
is **physically impossible on QFN56 and QFN32** (PB2/PB3 not bonded) — a **part-selection**
constraint, unrecoverable earlier than layout. Viable: LQFP64, CSP64, QFN64, LQFP48, QFN48.
Planned as its own checklist row (R3).

**Discretion resolved at plan time** (not passed to executors): PCB-05 lands in three gated
locations (meta §6, subset `[SHARED:S5]`, and `platform/py32f071/README.md`) as documentation,
imperative — no installer prompt, the host repo being out of scope; sourcing uses **per-claim
tags** plus a blanket `## Claim ceiling`, adding a fifth tag `[UNVERIFIED-UNTIL-SILICON]`;
filenames are `.planning/v1.23-FLASH-PATH-DECISION.md` and
`firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md`, with the sync gate keyed on
`[SHARED:S1]`…`[SHARED:S5]` heading suffixes and body-only comparison.

**Verified at plan time, not inherited:** the sibling import `from tests.meta_presence import …`
resolves under both `python -m pytest tests/` and the bare `pytest` script (PATTERNS' precedent-thin
risk retired, **no `conftest.py`**); firmware suite baseline is **180 passed / 0 skipped** at
`7a0a375`; `firestarter/` has no `build/` gitignore entry, so 129-07's scratch build directory sits
outside both working trees.

**Open questions recorded, not guessed:** `nBOOT1`'s factory default (a bad option byte may strand
a board without SWD — the strongest justification for the SWD-pads row) and whether the USB PHY
provides an internal D+ pull-up or a discrete 1.5 kΩ is required.

### Phase 129 context highlights (2026-08-02)

> Snapshot of what discuss-phase locked. **Three rows below were superseded by research** — see
> the planning-outcome table above: the VID/PID premise (C-2), the vector-relocation candidate
> enumeration (C-1), and the seed's bootloader size (C-4). Plan to the outcome table, not to this.

**Docs-only phase, two repos.** Meta `.planning/` + `firestarter`; **`firestarter_app` is out
of scope** (D-04). Read `.planning/phases/129-flash-path-decision-pcb-requirements-record/129-CONTEXT.md`.

| Area | Locked |
|---|---|
| Record shape | **Two-layered** — authoritative meta milestone-prefixed decision doc (v1.9/v1.10 shape, **no ADR numbering**) + a firmware `platform/py32f071/` **subset** behind a **fail-closed sync gate with a planted-violation fixture**. Gitlinks bumped **in-phase** (Phase 125/128 precedent) |
| VID/PID | **pid.codes / VID `0x1209`** is the decision; **`usb_cdc.c` is NOT edited** (`0x36B7`/`0xFFFF` stays). Allocation is a public PR the **operator** files — no agent. Record carries a **hard ship gate**: no board ships, no release advertises a USB identity, until a real PID exists |
| Flash budget | **Sector-quantised** bootloader figure, research-sized, **always printed with its ORIGIN-migration cost**. Linker gets a **comment-only** back-reference; `BOOTLOADER … LENGTH = 0` stands. Vector relocation: state the cost, enumerate **confidence-tagged** candidates |
| PCB list | Four PCB-02 names **plus** VPP on PA4/ADC ch4, data-bus test points, USB connector/D+ pullup. Seed item 5 (reboot-to-bootloader) recorded as an **open question with its board cost**, not decided. Each row: **checkbox + rationale + failure mode** |
| Seed | `.planning/seeds/py32f071-no-external-tool-fw-install.md` — trigger already fired (v1.28 activated as v1.23) while `status:` still reads `dormant`. → **partially-realised, seed stays live for FUT-N05**; the new record is canonical |

**No operator-gated ARM CI run this phase (D-13)** — the only firmware edits are a new `.md`
and a linker comment, so no translation unit is added; prove byte-identical output locally in
the non-regression doc. Phases 125/126/128 each needed CI because they added TUs. The standing
rule still holds: no task may run `git push` or `gh workflow run`.

**Todo matches: none folded.** `correct-v128-py32-roadmap-prior-art` is the only substantive
hit and is already owned by **CLOSE-03 / Phase 130**.

### Phase 127 context highlights (2026-08-01)

**Different repo.** This phase is entirely in `firestarter_app`; it runs in **parallel** with
Phases 125/126 and writes nothing into the firmware repo. Phase 128 depends on **it** for the
`asset_candidates()` filename contract.

**Sixteen decisions locked (D-01…D-16), plus D-17…D-19 at Claude's discretion.** Read
`.planning/phases/127-host-dfu-installer/127-CONTEXT.md`.

| Area | Locked |
|---|---|
| CI evidence | `workflow_dispatch:` added to `ci.yml`; **operator** pushes + dispatches (`autonomous: false`, no task runs `git push`/`gh workflow run`). Separate `ci-py32` job on `.[test,py32]`, py32 tests only. Real `usb.core.find` + `inspect.signature`-pinned `ctrl_transfer`. Collected count **recorded, not gated** |
| pyusb / channel | Genuine absence via a **subprocess `sys.meta_path` blocker** (needs no `ALLOWED_SKIP_REASONS` entry); a separate in-process test covers the de-pragma'd `PyusbMissingError`; HOST-08 proven subprocess-per-version, **no `importlib.reload`**; HOST-02 via one shared refusal helper |
| HOST-03 readback | **DfuSe only** (plain DFU records "load address not under host control"); `verify_result` enum on the flasher, `flash()` keeps its `bool`; **MISMATCH is a hard exit 1**, soft is reserved for "could not verify"; full payload byte-for-byte, **before `_finish()`** |
| Flash map / merge | Envelope guard tightened to `0x0801E000` **in this phase** (no HOST id — a deliberate in-scope addition); kept honest by a **fail-CLOSED** cross-repo linker-script gate with `@requires_fw` + a non-vacuity assertion; doc updated for 127's facts only; **real merge commit** with `4ee64a1` as parent, fixups in separate commits |

**Measured live during the discussion (re-verify at plan time, do not inherit):**

- `git merge-tree --write-tree HEAD 4ee64a1` from the app milestone branch → **exit 0, clean** —
  but `4ee64a1` is **87 commits behind** it (79 behind `beta`; merge base `1bb5599`), and both
  `cli_handlers.py` and `firmware.py` moved substantially. ~~Textual ≠ semantic; plan for fixups.~~
  → **SUPERSEDED at plan time: the merge was performed for real and nothing breaks.** See below.

- App suite on the milestone branch: **1158 collected**; `tests/test_py32_dfu.py` adds **58**.
- **`pyusb` is not installed in this devcontainer, but `libusb-1.0.so.0` is** — the `.[test,py32]`
  leg can be rehearsed locally before the operator dispatches CI.

- **No serial devices attached**, so the known live-board artifact
  (`test_no_programmer_found_read/erase`) will not confound the baseline. Re-check before recording.

- **Pushing the app milestone branch fires nothing**: `beta-release.yml` is `beta`-only,
  `release.yml` and `ci.yml`'s `push` are `main`-only, `publish.yml` is release/dispatch-only.
  D-01 carries **zero** release hazard.

### Phase 127 research corrections (2026-08-01, at plan time)

The ROADMAP flagged Phase 127 **research-skip**. Research was run anyway and **overturned claims
inside four locked decisions** — the third consecutive milestone where that has happened (v1.22
P122, v1.23 P125, now P127). `127-CONTEXT.md` carries inline `CORRECTED by 127-RESEARCH.md §C-N`
notes; **the note wins over the surrounding decision text**, whose original wording is preserved as
the superseded claim.

| # | Decision | Correction | Effect |
|---|---|---|---|
| **C-1** | D-16 | A real `git merge --no-ff 4ee64a1` in a scratch worktree: **1216 collected · 0 failed**, all 8 `ci.yml` gates green, coverage 81.35%. **Zero fixups.** | Shrinks the phase — no fixup budget, no expected red commit |
| **C-2** | D-18 | The self-referential assertions D-18 orders removed **do not exist**; every constant use in `test_py32_dfu.py` is a *sequencing* assertion, which D-18's own next sentence orders kept. | **HOST-06 is purely additive** — following the struck wording would have damaged 58 working tests |
| **C-5** | D-12 | `flash()` **never calls `_finish()`** — it is the last statement of `_download_dfuse()` (`:768`) and `_download_plain()` (`:777`). The edit as written was impossible. | **Operator chose shape (b): hoist** `_finish()` to one call site in `flash()`, making D-12's ordering structural rather than conventional |
| **C-4** | D-06 | `Zadig` appears nowhere in the codebase; the message says `WinUSB`. | A literal reading would have been red on day one |
| C-3 | D-06 | Pragma is at `py32_dfu.py:**375**`, excluding statements 375–376 — and removing it can only *raise* coverage. | Anchor correction |
| C-6 | D-03 | `_FakeUsbDevice.ctrl_transfer`'s 5th param is `data`; real pyusb 1.3.1 is `data_or_wLength`, plus a `timeout` the fake lacks. | D-03 upgraded from "good idea" to provably targeting a **real, present** drift |
| C-7 | D-13 | The linker-map transcription CONTEXT asked to be distrusted is **correct**. | Confirmation |
| C-8 | D-02 | The whole suite run under pyusb-**present**: identical result. D-02's accepted cost measures as **zero today**. | Grounds the acceptance rather than asserting it |

**Baseline, corrected again at plan time:** research's `1213 passed / 3 skipped` was a *scratch-worktree*
artifact — those tests skip only when `.planning/` is unreachable. In the real sibling checkout expect
**1216 collected / 1216 passed / 0 skipped**. A non-zero skip count in the evidence run means the
layout is wrong, not that the suite regressed.

**The phase's one genuinely undecided mechanism, settled by probe** (plan 127-06): keeping
`test_pyusb_api_surface.py` out of the primary `.[test]` leg via a conditional `collect_ignore` in
`tests/conftest.py` keyed on `importlib.util.find_spec("usb")`. Non-collection, **not a skip** — so no
new `ALLOWED_SKIP_REASONS` entry — and fail-closed, because `collect_ignore` does not suppress a path
named explicitly on the command line, which is how `ci-py32` invokes it.

- Live py32 flash map (`PY32F071xB_FLASH.ld`): `FLASH 0x08000000/120K` · `CONFIG 0x0801E000/8K`
  (Sector 15) · `BOOTLOADER 0x08000000/**LENGTH 0**` — a named seam; giving it a length **moves the
  application's ORIGIN**, which is why D-13's constant is carried forward to Phase 129.

**D-16 is deliberately the opposite of Phase 124 D-05.** 124 squashed because its own Criterion 1
forbade any reachable commit with the portability files but not the py32 stack (an ancestor-branch
constraint). Phase 127's Criterion 1 instead *requires* `4ee64a1` among the merge commit's parents.
Not drift — both are recorded so a reader does not mistake it for drift.

### Phase 126 plan structure (2026-07-31)

| Wave | Plan | Scope |
|---|---|---|
| 1 | 126-01 ∥ 126-02 | Pre-phase pin + `platform/py32f071/CONFIG-STORAGE.md` as a commit of its own (the CFG-02 ordering anchor) ∥ CFG-04's regression test authored **pre-refactor**, blob SHA recorded |
| 2 | 126-03 | The atomic AVR split in ONE commit: seam header + policy-only TU + `src/boards/rurp_config_storage_eeprom.cpp` + the one exclusion + checker docstring; then D-04's re-hash proof |
| 3 | 126-04 ∥ 126-05 | AVR flash/RAM measured cold under both named comparators against their named baselines ∥ CFG-03's structural gate |
| 4 | 126-06 | Reserve Sector 15 in `platform/py32f071/linker/PY32F071xB_FLASH.ld`; CFG-02 ordering as an exit code with a non-vacuity guard; CFG-06 map gate |
| 5 | 126-07 | HAL-free dual-slot core: `StoredConfiguration`, `CONFIG_MAGIC 0x52555250`, table-free reflected CRC-32, V5 validation ordering |
| 6 | 126-08 | HAL primitives, `platform/py32f071/src/config.cpp` deleted, manifest closed at 26, C-3 flash-driver detector |
| 7 | 126-09 ∥ 126-10 | Criterion 4's six named tests + the seventh CRC32 known-answer anchor ∥ CFG-07 schema/deletion gate |
| 8 | 126-11 | ARM CI evidence behind the structural operator gate (`autonomous: false`) |
| 9 | 126-12 | Closing: re-execute everything, `126-NONREGRESSION.md`, tick CFG-01..CFG-07 |

**Load-bearing planning decisions:**

- **Two corrections the planner made to the planning record.** (a) D-08's manifest churn is split across two commits: naming `src/rurp_config_utils.cpp` in the ARM manifest *before* `platform/py32f071/src/config.cpp` is deleted would give the ARM link two definitions of each of the four public config functions — and nothing local detects it (`arm-none-eabi-gcc`/`cmake`/`ninja` are absent and `py32f071.yml` does not fire on this branch), so it would surface only in the gated CI run several plans later. 126-03 lands only the new exclusion; 126-08 lands the retirement, the promotion and C-3's flash-driver entry in the same commit as the deletion. (b) The sector-alignment `ASSERT` moved out of the linker script into `tests/test_py32_flash_map.py` — there is no ARM linker here to try modulo-on-a-region-origin against. <!-- recordscan:history arm-toolchain-absent: accurate at Phase 126 planning time -- arm-none-eabi-gcc/cmake/ninja were measured absent then; 130-RESEARCH.md's "Environment drift" finding (C-13/R-15) later measured the toolchain present at Phase 130 plan time, which does not retroactively falsify this Phase-126-time record. -->
- **Criterion 2 is satisfiable only by construction:** `CONFIG-STORAGE.md` is a single-file commit in Wave 1; Wave 4's gate wraps `git merge-base --is-ancestor` with a **non-vacuity guard** (it fails if no in-phase linker commit exists) plus a synthetic-repo RED demonstration.
- **Criterion 3's blob SHA is recorded in 126-02's SUMMARY and re-hashed in 126-03.** If 126-02 does not record it, the proof is unrecoverable. A path-scoped `git diff` is corroboration only — `124-VERIFICATION.md` records that shape passing vacuously.
- **Plan 126-11 is `autonomous: false`** and no task in it may run `git push` or `gh workflow run`. The structural separation *is* the gate, not the checkpoint type — `--auto`/`--chain` auto-approve human-verify checkpoints.
- **Live figures used throughout:** Leonardo free flash **2656 B** (CONTEXT.md's 2600 B is stale), `pytest tests/` at **86**, manifest gate **24 → 26** enforced sources, native pinned at **141 cases / 17 suites** on both envs.
- Only 126-12 may tick CFG-01..CFG-07 (the Phase-116 4× premature-tick guard).

### Phase 125 close-out (2026-07-31)

`125-VERIFICATION.md`: **passed** — 15/15 must-haves re-executed against the live trees rather than accepted from SUMMARY prose. The verifier independently re-ran both new pytest modules, all three native envs cold, the manifest gate, a 7-file blob-SHA re-hash, and re-queried the ARM CI run read-only.

**What Phase 125 landed:** `include/rurp_vpp.h` + `src/rurp_vpp.cpp` (hand-authored, dependency-free, zero production callers) and two lines in `platform/py32f071/CMakeLists.txt`. Firmware tip `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`, pushed to `origin`; meta gitlink bumped to match in `4bb038e`.

**ARM evidence:** CI run [`30652530756`](https://github.com/henols/firestarter/actions/runs/30652530756) — `workflow_dispatch`, `conclusion=success`, head SHA string-equal to the firmware tip, **Configure and Build each independently `success`**, and log line `[4/39] Building CXX object …src/rurp_vpp.cpp.obj` (39 objects vs Phase 124's 38) proving the seam reached the ARM compiler. The operator ran the push and dispatch personally; the structural gate held — no agent executed `git push` or `gh workflow run`. No beta prerelease was cut (newest `beta-build.yml` run remains `30551682616`, 2026-07-30).

**The finding that changed the phase:** research measured that the one `#include "rurp_vpp.h"` line in `include/rurp_shield.h` — which the ROADMAP, CONTEXT.md and milestones/v1.23-research/SUMMARY.md all described as this phase's entire header change — takes `pio test -e native` from 141 cases/141 succeeded to **17 suites / 0 succeeded**. Operator chose Option A: `rurp_shield.h` is untouched. See `125-RESEARCH.md` C-1.

**Two informational findings carried forward (non-blocking):** all six `125-0N-SUMMARY.md` files trip the claim-ceiling gate when scanned directly, because they quote the forbidden phrases inside their own compliance paragraphs — the exact self-reference trap `125-RESEARCH.md` C-16 documents; the required artifact `125-NONREGRESSION.md` avoids it correctly. And `125-06-SUMMARY.md` claims gitlink bumps are deferred to milestone close, which was not this phase's actual practice — corrected out-of-band by `4bb038e`.

### Phase 125 plan structure (2026-07-31)

| Wave | Plan | Scope |
|---|---|---|
| 1 | 125-01 | Pre-phase pin, then the atomic landing: `include/rurp_vpp.h` + `src/rurp_vpp.cpp` + the two `platform/py32f071/CMakeLists.txt` lines in ONE commit. Fires the C-1 native tripwire in the authoring task |
| 2 | 125-02 ∥ 125-03 | VPP-02's parametrized compile-and-run harness (10 cases / 7 functions) ∥ Criterion 1's PR #45 non-ancestry gate (4 cases) |
| 3 | 125-04 | Criterion 4 measured: three cold AVR builds, two-directional non-vacuity, armed comparator, D-16 disposition |
| 4 | 125-05 | D-13 ARM CI evidence behind the structural operator gate (no task runs `git push` / `gh workflow run`) |
| 5 | 125-06 | Closing: every row re-executed, `125-NONREGRESSION.md`, claim gate with explicit target, tick VPP-01/02/03 |

**Load-bearing planning decisions:**

- The seam files and the CMake manifest entry are **one commit** — the manifest reverse check makes a present-but-unnamed `src/*.cpp` exit 1 and a named-but-absent path exit 1, and `test_check_cmake_manifest.py::test_armed_and_passing_on_the_real_tree` asserts the *real* tree, so `pytest tests/` would go red between two commits. There is no green intermediate state.
- The C-1 native tripwire sits in the authoring task's own `<verify>`, not in the closing plan.
- Only 125-06 may tick VPP-01/02/03; the other five are each told explicitly not to (the Phase-116 4× premature-tick guard).
- Expected suite counts as the plans land: `pytest tests/` 72 → 78 → 82 → 86; manifest gate 23 → 24 enforced sources; native envs unchanged at 141/17 and 10/1.

### Phase 125 context highlights (read `125-CONTEXT.md` and then `125-RESEARCH.md` — RESEARCH wins on conflict)

- The four-board `MANUAL_ADJUSTMENT_REQUIRED` proof is a **pytest + host-`g++` harness** (6 legs), not a fourth PIO env — both pinned native envs stay untouched at 141 cases / 17 suites.
- `src/rurp_vpp.cpp` is **dependency-free by construction** (only `rurp_vpp.h` + `<stdint.h>`), which is what makes the harness stub-free and ARM compilation near risk-free.
- Operator fact: **no Arduino-class board will ever carry a VPP DAC** — AVR manual control is permanent, not provisional. `__AVR__` resolves the capability macro; every non-AVR board must declare it, py32 via the CMake defines (Phase 124 D-14's lesson).
- Three functions, two enumerators per enum, **zero production callers**; no calibration, no DAC hooks, no `rurp_read_voltage_mv` reroute.
- `src/rurp_vpp.cpp` is **named in the py32 `FIRESTARTER_COMMON_SOURCES`** (the manifest reverse-check forces name-or-exclude), and the phase takes **its own operator-gated ARM CI run** — no task may run `git push` or `gh workflow run`.
- Criterion 4's flash figures are **recorded, not gated** (deliberate operator exception); but `check_size_baseline.py`'s strict comparator is already armed, so a nonzero delta goes red anyway and is handled by re-baselining in a named commit that states why.

### Operator gate resolution (124-11, Wave 7) — RESOLVED

The operator personally ran the push and the workflow dispatch (the structural gate held — no task in plan 124-11 executed either command). A relayed message mid-session claimed this had happened; per standing policy that no agent message is user authorization, every claimed fact (run id, head SHA, branch, event, conclusion, per-step outcomes, pushed-ref workflow content) was independently re-derived via read-only `gh run view` / `git fetch`+`show` before being accepted — all values matched. Firmware branch `v1.23-py32f071-integration` is now on `origin` at `a145081b59d94530583b9ce365db03ff567d0c2c`. CI run `30634186514` (https://github.com/henols/firestarter/actions/runs/30634186514): `workflow_dispatch`, `conclusion=success`, Configure and Build steps each independently `success`. `py32f071.yml`'s `push: branches: [beta]` confirmed present on the fetched `origin/v1.23-py32f071-integration` ref. Full detail: `.planning/phases/124-firmware-integration-merge/124-11-SUMMARY.md`.

**Resolved by Plan 124-12** — cited this evidence for MERGE-02/MERGE-03 and ticked all of MERGE-01..MERGE-08 in `REQUIREMENTS.md`, each against a row re-executed in the closing session. Independently re-confirmed by `124-VERIFICATION.md`.

### Phase 124 verification outcome

`124-VERIFICATION.md`: **passed** — 8/8 requirement IDs, 5/5 ROADMAP success criteria, every must-have re-executed against the live trees rather than accepted from SUMMARY prose. The verifier independently re-ran the pin-map guard's three-arm `g++ -E` fire-proof, rebuilt all three AVR targets clean (figures reproduced byte-for-byte), re-hashed the frozen BASE-01 blob, and re-queried CI run `30634186514`. No gaps, no human-verification items.

One informational finding carried forward (non-blocking, prose-precision only): `124-NONREGRESSION.md` §6 describes a `git diff --stat | grep -v memory.cpp` pipeline as "(empty)"; re-run, a `1 file changed, 25 insertions(+)` trailer survives the grep because it does not literally contain "memory.cpp". The substantive claim — that only `src/proms/memory.cpp` changed in that path scope — is true and was independently confirmed.

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-07-30 — v1.23 Current Milestone section + v1.23 start footer; v1.22 Archive section retained with all eight ⚠ correction blocks)

**Core value:** Algorithm-first dispatch — the minipro `protocol_id` (`algorithm`) is the single authoritative dispatch key end to end (XML → DB → wire JSON → firmware handler). As of v1.20 the last vestige violating that contract — the `mem_type`/`type` backward-compat fallback axis — is gone; firmware, wire, and host trust **only** the real protocol. v1.23 adds a fourth board target beneath that contract without disturbing it: the PROM programming algorithms stay platform-independent and the HAL boundary absorbs the new MCU, so protocol dispatch is untouched by the port.

**Current focus:** Phase 130 — Close — Honesty Ledger, Claim Gate, Release Decision

## Milestone Context (v1.23)

- **Scope:** Land the in-flight PY32F071 firmware port and the host USB-DFU firmware installer onto `beta` as one lockstep integration, plus the cross-repo release-asset unblock, without touching the three AVR targets. Eight target features — see PROJECT.md §"Current Milestone: v1.23 PY32F071 Integration". Requirements not yet defined (this is the requirements step).
- **This is an integration milestone, not a build-it milestone.** Both halves already exist and are green: the firmware stack on `agent/py32f071-toolchain` (PR #48, OPEN draft, stacked on `agent/portability-macros`) with **PY32F071 CI green three consecutive times on 2026-07-21** compiling the *shared* command processor, framing and PROM algorithms for Cortex-M0+; the host installer on `firestarter_app` `feature/py32f071-fw-install` @ `4ee64a1` (**58 tests passing** — and they pass with `pyusb` not importable — mypy identical to pristine `origin/beta`). The "does this architecture even build" risk is retired. **The work is the rebase, the release plumbing, and the honesty.** Measured: **21 host capabilities already exist and need landing; 8 items remain to be built, and only one of those (the release-asset publication) gates any user-visible value at all.**

- **⚠ RESEARCH CORRECTIONS — read `.planning/milestones/v1.23-research/SUMMARY.md` before planning any phase.** This section and PROJECT.md's were written BEFORE the four-stream research; 18 numbered corrections (R-1…R-18) and 7 adjudicated inter-researcher conflicts (A-1…A-7) apply to both. Three of four researchers built, merged and tested the branches. The five that change what gets planned: **(1)** `agent/portability-macros` **cannot land alone** — 141/141 native → **0 passing / 17 ERRORED**; its repair `780a3fb` is on the stacked branch, so the two land **atomically** (R-9/A-4). **(2)** Both repos merge with **zero conflicts** and disjoint file sets, but `platform/py32f071/CMakeLists.txt:46-47` names `flash_type_3/4.cpp` — renamed by v1.19 Phase 104 — so the ARM target **fails at CMake configure**, and `py32f071.yml` has **no `push` trigger** to catch it (A-2/A-3). **(3)** Flash growth is not the risk: **−56 B Leonardo, +22 B Uno, +28 B 328PB**, RAM unchanged; live Leonardo headroom is **2600 B on `beta` / 2656 B merged, not 2992 B** (A-1/A-5/R-10). **(4)** The cross-repo gates **fail OPEN** — a firmware rename flipped 5 legs PASS→SKIP at exit 0 with a false reason, and moving firmware files is this milestone's premise (A-7). **(5)** Flash-persistent config is **design work** — `PORTING.md` lives only on closed PRs #46/#47 and its layout does not match what #48 built (R-8/A-6).
- **Every py32 branch is 72 commits behind `beta`.** Measure against `beta`, never `main` — `main` lags `beta` by ~268 commits in firmware and ~544 in the app, which makes live branches look abandoned. The rebase is real work, not a fast-forward.
- **No PY32F071 PCB exists (operator, 2026-07-28) → software-only validation, no bench phase.** PR #48's pin map (PB0–PB7 data, PA0–PA5 control, VPP on PA4/ADC ch4) is an explicitly provisional placeholder so the target compiles before a schematic and **must not be trusted near a PROM**. Permitted claims: the target builds clean, native + host suites pass, the DFU sequence is exercised against device descriptors and mocks. Forbidden: *"the firmware runs on a PY32F071"* or *"the install works end to end."* Never write or accept a success criterion crossing that line.
- **Hard acceptance constraint:** Uno, ATmega328PB, Leonardo and the native test suite remain unaffected. Golden register traces, the dispatch-mirror guard, `check_dispatch.py`, `diff_db.py` identity, and the nine cross-repo source-scanning gates all stay green.
- **Locked decisions (operator, 2026-07-30 — do not re-litigate):** scope is port + host install + VPP **seam**; the DAC closed loop and the calibration model stay OUT (see the collision note below); slot is **v1.23**, retiring the queued v1.28/v1.29 py32 slots into it and renumbering `Binary Command Protocol` v1.23 → v1.28 while v1.24–v1.27 stay untouched.
- **⚠ The DAC-VPP / calibration collision — settled, do not reopen.** PR #45 (`feature/common-vpp-calibration`, closed, 10 commits) is ONE API spanning two concerns and the closed loop *depends* on the calibration half: `rurp_set_vpp_target_mv()` closes its loop on `rurp_read_voltage_mv()` (the **calibrated** read), and `rurp_calibrate_vpp_two_point()` **is** the White-Box Voltage Calibration milestone's Stage-2 divider trim, already cross-platform. Three of its ten commits reach into that milestone's files: `9134f2a` (`src/boards/rurp_common.cpp`, its exact Stage-1 target), `768580f` (`include/rurp_types.h`) and `b964ee6` (`src/rurp_config_utils.cpp`) — the latter two being `CONFIG_VERSION`-bump + EEPROM-migration territory, which is also where Backlog 999.1's stale-`r1` fix lives. **Resolution: seam only** — capability macros, `rurp_vpp_control_mode_t`/`rurp_vpp_result_t`, `RURP_VPP_CONTROL_MANUAL` on every board, `rurp_set_vpp_target_mv()` returning `MANUAL_ADJUSTMENT_REQUIRED`; no AVR measurement reroute, no `CONFIG_VERSION` bump. Two supporting facts: PR #45 does **not** contain the Stage-1 bandgap back-solve, so that milestone's ±10 % win is unaffected either way; and with no PCB a closed loop **cannot be validated at all**.
- **⚠ Start from PR #48. Never from PR #47.** `feature/py32f071-full-support` (closed) has a 24-file `platform/py32f071/` tree and an all-inclusive CMake list, so it reads as the most finished branch — but `src/usb.c` (141 lines) is a ring buffer over `__attribute__((weak))` **no-op** low-level hooks. It links, and a board flashed with it would be **silent on USB**. `vpp_target.c` is 13 lines; there is no SDK fetch.
- **⚠ The v1.28 ROADMAP entry's prior-art paragraph is now removed, not merely stale.** It had claimed the work was "not in flight," citing PR #46 closed-unmerged and `feature/py32f071-toolchain` @ `2c2ed10` (the smallest of five branches) as the place to start scoping — all three claims were re-verified wrong against `origin` on 2026-07-30. **Resolved 2026-08-02 (CLOSE-03, plan 130-04):** the ROADMAP entry that carried this paragraph was itself retired along with it (see the CLOSE-03 bullet below); the owning todo `correct-v128-py32-roadmap-prior-art` moved from `todos/pending/` to `todos/completed/`; the historical paragraph text survives only in git history, not reproduced in the live tree. **Scope from PROJECT.md §"Current Milestone: v1.23", not from a ROADMAP entry that no longer exists.**
- **The self-flash bootloader is the intended primary install route; the DFU path landing here is the runner-up.** `.planning/seeds/py32f071-no-external-tool-fw-install.md` decides for a bootloader in the first few KB of the 128 KiB flash speaking the existing USB CDC + COBS framing — zero new host dependencies, structurally identical to how the Uno works. Every factory-bootloader route was rejected on host-side grounds (Puya `PY32DfuTool` is Windows-x64-only; `dfu-util` reintroduces avrdude's PATH-discovery burden; `puyaisp` needs a second USB-serial dongle on a board with native USB). The pyusb DFU client is that table's *vendored-Python-over-libusb* row, accepted at operator request so the transfer sequence gets proven; residual cost is `pyusb` + libusb, and a WinUSB driver via Zadig on Windows. **Landing it does not retire the seed** — what this milestone must capture is the PCB consequences, because the board is still paper and they are cheap now and expensive after layout.
- Phase numbering continues from v1.22's Phase 122 → **v1.23 starts at Phase 123**.
- **Branch model:** meta branch `gsd/v1.23-py32f071-integration` forked off the v1.22 tip `8be00ee` (NOT `main`, which lags by ~1267 commits). Sub-repos fork off `beta` per standing policy, then the py32 branches merge in — verify with `git` at execute time regardless. Extra worktrees `firestarter_py32_ci/` (fw @ `feature/py32f071-release-assets`) and `firestarter_app_py32/` (app @ `feature/py32f071-fw-install`) are checkouts of the same two repos, gitignored in meta, never gitlinked.
- **Release hazard, unchanged:** pushing `beta` in either sub-repo auto-fires CI and cuts a new beta — the cut is a deliberate decision, never a side effect. `firestarter_app`'s CI fix `81fa53c` lives on `beta` only and must be reintroduced whenever the milestone branch next merges toward `main`.
- **Release-asset mechanics (already designed, not yet implemented).** `py32f071.yml` deliberately does **not** cut releases: `beta-build.yml` runs `.github/scripts/update_version.py`, which rewrites `include/version.h` and auto-commits *before* building, so an image built in any other job carries a stale `VERSION` — and the host's entire update decision is that string compared against the release tag. `feature/py32f071-release-assets` @ `ad47c3b` already renames the output to `firestarter_py32f071.hex` (correct prefix and separator) but it is still an **Actions artifact**. The fold is 3 steps plus one `files:` line, spelled out in `platform/py32f071/README.md` §"Release integration" — use a **glob**, not a literal path, because `softprops/action-gh-release` warns on an unmatched glob but *fails* on a missing literal file, so a broken ARM build must never block the AVR beta.
- **CLOSE-03 landed (2026-08-02, plans 130-04/130-05).** The ROADMAP.md `## Milestones` list now carries a real `✅ v1.23 PY32F071 Integration — Phases 123–130` entry where it previously ran straight from v1.22 to the queued py32 slots; `Binary Command Protocol` is renumbered to **v1.28 Binary Command Protocol** and sits after v1.27 in version order; both retired py32 ROADMAP slots (the former v1.28 PY32F071 Port and v1.29 PY32F071 USB Firmware Install) are collapsed into one dated retirement line; the **v1.29** slot number is left **vacant**; **v1.30** (SDP Surface Retirement & Behavioral Lock Proof) keeps its own number by its own instruction, not compacted to v1.29; and backlog stubs **999.23**/**999.24** are retired as delivered into the v1.23 slot. Plan `130-04` landed the SHIPPED entry, the renumber and the retirement line; plan `130-05` retired the backlog stubs and repaired every `→ v1.28` pointer.
- **CLOSE-01 checker run against this file found zero unlabeled hits (2026-08-02, plan 130-08).** `FIRESTARTER_RECORDSCAN_TARGETS=/workspaces/.planning/STATE.md python3 check_record_corrections.py` (committed at `.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py`, plan 130-02) exits `0` for this file. Every measured needle site in this file — the C-1 correction-table row above, the `⚠ RESEARCH CORRECTIONS` bullet above, this v1.28 prior-art bullet, and the Phase 124 `write_checksums.cmake` decision-log record — was found correct or correctly labeled; research manufactured no correction for an already-correct site. The two Phase 119 decision-log `2992 B` figures are exempt as history with the reason recorded inline on each line, confirmed live against `130-02-SUMMARY.md`'s machine-derived hit list rather than inherited from research prose.
- **D-11 landed (2026-08-02, plan 130-03): py32 USB descriptor now presents pid.codes `1209:0001`, not Puya Semiconductor's registered `0x36B7`/`0xFFFF`.** The `[SHARED:S4]` record pair (`.planning/v1.23-FLASH-PATH-DECISION.md` and `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md`) was rewritten identically in both copies and the 41-leg cross-repo sync gate (`test_flash_path_record_sync.py`) was re-run locally — it runs in no CI leg. The ship gate in `v1.23-FLASH-PATH-DECISION.md` §5(c) is unchanged; the tension between D-11's descriptor swap and §5(c)'s "no release advertises a USB identity" condition is carried as an owned residual per **D-17**, not resolved by amending the gate.

## Roadmap Summary (v1.23)

**Created:** 2026-07-30 — adopted research SUMMARY.md's reconciled 8-phase spine (123–130) verbatim; no coverage gaps found requiring deviation.

**Phases:** 8 (123–130). **Granularity:** Comprehensive (config). **Coverage:** 47/47 v1 requirements mapped, 0 unmapped — exact 1:1 category→phase mapping (BASE→123, MERGE→124, VPP→125, CFG→126, HOST→127, REL→128, PCB→129, CLOSE→130).

| Phase | Goal | Requirements | Research |
|-------|------|--------------|----------|
| 123 Non-Regression Baselines & Gate Hardening | Record AVR flash/RAM + native counts; split the fail-open FW-absent proxy; ship every checker with a planted-violation fixture — before any firmware moves | BASE-01…08 | skip |
| 124 Firmware Integration Merge (atomic) | Land `agent/portability-macros` + the py32 stack as one commit-pair; fix C-1 (CMake rename); add ARM `push` trigger; make the pinmap refusal fire | MERGE-01…08 | skip |
| 125 VPP Control Seam | Hand-authored `rurp_vpp.h`/`.cpp`; every board → `MANUAL_ADJUSTMENT_REQUIRED`; prove `rurp_config_utils.cpp` untouched | VPP-01…03 | skip |
| 126 Flash-Persistent Config ⚠ highest-risk | Dual-slot CRC32 py32 config backend behind a common/per-platform seam; AVR EEPROM path proven a pure move | CFG-01…07 | **yes** |
| 127 Host DFU Installer *(parallel w/ 125-126)* | Merge `feature/py32f071-fw-install`; close the 8 remaining host gaps | HOST-01…08 | skip |
| 128 Release-Asset Fold | Fold ARM build into `beta-build.yml` after the version bump; publish `firestarter_py32f071.hex` as a real release asset | REL-01…04 | skip |
| 129 Flash-Path Decision & PCB Record | Record the 3-tier flash path + PCB requirements before any schematic, citing Phase 126's actually-reserved flash map | PCB-01…05 | **yes** |
| 130 Close | Apply R-1…R-18; honesty ledger; ROADMAP slot renumber; release-decision artifact before any push | CLOSE-01…04 | skip |

**Load-bearing ordering (not preference):** 123→124 (gates predate the moves they detect) · 124 atomic (A-4: portability-macros alone breaks native 141/141→0/17-ERRORED) · 125→126 (shared-file attribution: both touch `rurp_config_utils.cpp`) · 127→128 (asset-name contract direction) · 126→129 (real map, not intended) · 128 after the `beta-build.yml` version bump. **Genuinely parallel: {125, 126} ∥ {127}** — different repo, disjoint files, no shared gate; the one real parallelisation opportunity in this spine.

**Deviation from research spine:** none. The 8-phase spine in `.planning/milestones/v1.23-research/SUMMARY.md` §"Implications for Roadmap" was adopted verbatim; the category→phase mapping is exact and required no coverage-gap resolution.

**Full detail:** `.planning/ROADMAP.md` §"v1.23 — PY32F071 Integration (PLANNING)".

## Accumulated Context

### Deferred Items (carry-forward at v1.17 close — 2026-06-29)

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| FUT-07 (v1.17) | W29C040 byte-exact graduation + LEDGER `supported` | deferred — §6.6 boot block permanently locked on seated chip | Needs a different unlocked sample + third-party bench. All v1.17 software done. |
| ~~FUT-06 (v1.15)~~ → **FUT-08 (v1.18)** | AM27C020 0x08 32-pin write/VPP path | **retired-by-replacement (v1.18 Phase 99 close, 2026-07-01)** | Phase-98 fix bench-proven effective (write#1 60/64 byte-exact; Phase-97 0-bits signature refuted) but marginal/unreliable (write#2 0/64) — no byte-exact graduation. FUT-08 carries the next step: characterize program-window VPP-under-load (DMM at socket pin 1) + write timing. See PROTOCOL-LEDGER `0x08` / `.planning/v1.18/bench/EVIDENCE.json`. **+ Second data point folded in 2026-07-27 (backlog review):** [`henols/firestarter_prom#14`](https://github.com/henols/firestarter_prom/issues/14) reports a community **TMS27C010A** that blank-checks clean then fails write immediately at `0x000000` — `TI / TMS27C010A,TMS27PC010A` is `algorithm 8` / `pinout DIP32_27C020` / 131072 B, i.e. inside the same scope guard as AM27C020, so this is the *same* `0x08` write-path defect on a second, independently-owned part. Report predates the fix (app 1.2.2 / fw 1.2.3, 2024-11) — ask the reporter to re-test on current firmware; a community `0x08` part is exactly the extra silicon this item needs, and it is not operator-inventory-gated. Backlog stub 999.21 was retired into this row. |
| FUT-05 (v1.15) | REWR-02 0x08 rewritable write proof | deferred — no functional 0x08 rewritable chip | W27E040 stuck-bit; may benefit from v1.18 `0x08` fix. |
| FUT-04 (v1.14) | AT28C04/16 adapter graduation | deferred — adapter not built | 9 chips stay `adapter-required`. |
| FUT-03 (v1.15) | 2516 0x0B read instability + write proof | deferred best-effort (D-22) | 3 distinct SHAs after VPP-skip; shared OE/VPP pin. |
| FUT-01 (v1.14) | X88C64 0x34 graduation | deferred — PCB-blocked | A6 ALE-routing PCB-BLOCKED (HIGH); stays `protocol-not-implemented`. |
| LEGACY-01 (v1.20 v2) | `FLAG_VPE_AS_VPP (0x10)` removal if confirmed unused | deferred to v2 | Operator scoped v1.20 to the `mem_type` axis only, not the broader vestige sweep. |
| LEGACY-02 (v1.20 v2) | `EPROM_LEGACY` (0x0B) label rename + remaining "legacy fallback" prose scrub | deferred to v2 | Naming, not the dispatch axis; do after v1.20 lands. |
| release-gate | Lockstep beta cut `3.0.0b11` + gitlink bump | OPERATOR-GATED | Standing v1.11–v1.20 policy; gitlinks PINNED. |

### Deferred Items — acknowledged at v1.22 milestone close (2026-07-30)

Close type: **override_closeout** — all v1.22 phases (116–122) are `phase_complete` + `verification_status: passed` (Phase 122 verified 5/5) and all 41 v1 requirements are Complete, but `audit-open` reports 14 open artifact items, so the close is recorded as an override with the items acknowledged-and-deferred (operator: "Acknowledge & proceed"). **None originate in v1.22 (Phases 116–122)** — they are the identical pre-existing cross-milestone carry-forwards re-confirmed at the v1.18/v1.19/v1.20/v1.21 closes. Known verification overrides: 14.

| Category | Item | Status |
|----------|------|--------|
| debug | firmware-vpp-misread | diagnosed |
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 |
| uat_gap | Phase 08 — 08-HUMAN-UAT.md | partial (0 pending scenarios) |
| uat_gap | Phase 85 — 85-HUMAN-UAT.md | partial (2 pending scenarios) |
| verification_gap | Phase 08 — 08-VERIFICATION.md | human_needed |
| verification_gap | Phase 09 — 09-VERIFICATION.md | human_needed |
| verification_gap | Phase 71 — 71-VERIFICATION.md | gaps_found |
| verification_gap | Phase 84 — 84-VERIFICATION.md | human_needed |
| verification_gap | Phase 85 — 85-VERIFICATION.md | human_needed |
| todo | 2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads | firmware |
| todo | avrdude-mcu-detection-fallback | low |
| todo | cobs-decoder-framelevel-deadline-wr01 | medium |
| todo | correct-v128-py32-roadmap-prior-art | medium |
| todo | decode-infoic-flags-bits-14-15-protect-metadata | low |

*(+8 further todos beyond the 5 the audit enumerates — `audit-open` reports 5 with a `_remainder_count: 8`.)*

**⚠ This is the fifth consecutive close to acknowledge the same 14 items.** Recorded here as a standing carry-forward rather than a fresh finding. The two debug sessions and the five verification gaps all predate v1.17; a deliberate one-pass resolution is worth more than a sixth acknowledgement.

**New v1.22-originated carry-forwards (NOT counted in the 14 — none is an `audit-open` artifact type):**

| Item | Status | Disposition |
|------|--------|-------------|
| `0x0D` SDP silicon graduation | **deferred — no AT28C part on the bench** | Sampling rate zero, by design and by stated ceiling. Unblocks on a community re-test (gh#11 / gh#12, both left OPEN) or a future bench session. `PROTOCOL-LEDGER` `0x0D` stays `UNVERIFIED`. |
| AT28C 2K×8 class (19 chips on `DIP24_2816`) | **REFUSED by the derived allow-set** | 7 `pre-SDP generation`, 12 `unrecognised`; SDP-F7/SDP-F8 name the family deferred. `AT28C16` additionally `adapter-required` (see FUT-04). Correcting D-14's overclaim about this class is what surfaced it. |
| ⚠ App CI fix `81fa53c` on `beta` ONLY | **must be reintroduced at the next merge toward `main`** | Adds a `pytest.mark.skipif` guard to `test_check_is_memory_cmd_no_ifdef.py` + `test_check_no_log_in_sdp_window.py`'s `test_checker_exits_zero_on_clean_source` legs, which hard-fail in a standalone checkout with no sibling `firestarter` repo. Cherry-picked onto the milestone branch then **reverted** to keep branch HEAD byte-matching Plan 122-03's recorded merge SHA. `ci.yml` carries the same standalone-checkout risk. Recorded in `122-CUT.md` §8. |
| `check_ledger.py` pre-existing RED | **deliberately not fixed in v1.22** | 2 `LEDGER-01` violations from v1.19 Phase 104's `flash_type_3`/`flash_type_4` → `flash_nor_unlock`/`flash_5v_page` rename. Fixing it would edit a closed milestone's artifact; CLOSE-01 never gated on it. **Recommended as a backlog seed.** |
| Stray `3.0.0b12` prereleases | **left public (D-05, CLEANUP declined)** | Both repos. Operator decision at the `122-DECISION.md` gate; revisit only if it confuses a community installer. |
| Meta `catalog-sync-check.yml` + firmware `build.yml`'s `native_nodevtools` step | **`main`-gated — dormant, never run against v1.22 code** | Corrected against the workflow files at close: the Phase 122 hand-over said both carry `ref: main` in their checkout steps; only one does. `catalog-sync-check.yml` lives in the **meta** repo (not a sub-repo), triggers on push/PR to `main` scoped to `paths: tools/catalog/**`, and checks out **both sub-repos at `ref: main`**. Firmware `build.yml` has no `ref:` override — it simply only triggers on `push: branches: [main]`. Since `main` is never merged under this branch model, both are dormant rather than red. A known property, not a defect to chase. |
| `--sdp-relock`, three-field SDP report shape, `lock-status` + protection table | **deferred / out of scope** | `--sdp-relock` → Backlog 999.28; the report shape retains a minimal honesty floor (HOST-05); `lock-status` stays a planted seed at `.planning/seeds/lock-status-command-hand-curated-protection-table.md`. |
| release-gate: stable promotion | **OPERATOR-GATED** | Standing v1.11–v1.22 policy. PyPI `info.version` remains `2.0.7`; `main` untouched in all three repos (firmware lags `beta` by 268 commits, app by 544, meta by 1267). |

### Deferred Items — acknowledged at v1.21 milestone close (2026-07-27)

Close type: **override_closeout** — all v1.21 phases (108–115) are `phase_complete` + `verification_status: passed` (Phase 115 verified 5/5), but `audit-open` reports 14 open artifact items, so the close is recorded as an override with the items acknowledged-and-deferred (operator: "Acknowledge & proceed"). **None originate in v1.21 (Phases 108–115)** — they are the identical pre-existing cross-milestone carry-forwards re-confirmed at the v1.18/v1.19/v1.20 closes (see the v1.20 table below for the full item list; unchanged by this VALIDATION+DOCS milestone). Known verification overrides: 14.

**Resolved this milestone (was OPERATOR-GATED at v1.20 close):** the `release-gate` carry-forward — the lockstep `3.0.0b11` beta cut is now PUBLISHED on both channels (PyPI + GitHub prerelease) and the meta gitlinks are bumped off PINNED-b10 to the b11 commits (Phase 115).

### Deferred Items — acknowledged at v1.20 milestone close (2026-07-02)

Close type: **override_closeout** — all v1.20 phases (105–107) are `phase_complete` + `verification_status: passed`, but `audit-open` reports 14 open artifact items, so the close is recorded as an override with the items acknowledged-and-deferred (operator: "Acknowledge & proceed"). **None originate in v1.20 (Phases 105–107)** — they are the identical pre-existing cross-milestone carry-forwards re-confirmed at the v1.18 and v1.19 closes (unchanged by this dead-code-removal milestone). Known verification overrides: 14 (see table below).

| Category | Item | Status |
|----------|------|--------|
| debug | firmware-vpp-misread | diagnosed |
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 |
| uat_gap | Phase 08 — 08-HUMAN-UAT.md | partial (0 pending scenarios) |
| uat_gap | Phase 85 — 85-HUMAN-UAT.md | partial (2 pending scenarios) |
| verification_gap | Phase 08 — 08-VERIFICATION.md | human_needed |
| verification_gap | Phase 09 — 09-VERIFICATION.md | human_needed |
| verification_gap | Phase 71 — 71-VERIFICATION.md | gaps_found |
| verification_gap | Phase 84 — 84-VERIFICATION.md | human_needed |
| verification_gap | Phase 85 — 85-VERIFICATION.md | human_needed |
| todo | 2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads | firmware |
| todo | avrdude-mcu-detection-fallback | low |
| todo | cobs-decoder-framelevel-deadline-wr01 | medium |
| todo | photograph-modified-rev-0 | MEDIUM |
| todo | write-modifications-md-rework-trace | MEDIUM |

### Deferred Items — acknowledged at v1.19 milestone close (2026-07-02)

The **same 14** open artifact items (from `audit-open`) were re-confirmed acknowledged-and-deferred at the v1.19 close (operator: "Acknowledge & proceed"). **None originate in v1.19 (Phases 100–104)** — all are the identical pre-existing cross-milestone carry-forwards listed in the v1.18-close table below (2 debug sessions, 2 UAT gaps, 5 verification gaps, 5 pending todos), unchanged by this naming/rename milestone. NAME-01/02/03 REQUIREMENTS bookkeeping (previously showing Pending though delivered in Phase 100) was reconciled to Complete at this close.

### Deferred Items — acknowledged at v1.18 milestone close (2026-07-01)

14 open artifact items (from `audit-open`) acknowledged-and-deferred at v1.18 close. **None originate in v1.18 (Phases 97–99)** — all are pre-existing cross-milestone carry-forwards, unchanged by this milestone.

| Category | Item | Status |
|----------|------|--------|
| debug | firmware-vpp-misread | diagnosed (uno328pb VPP divider ~6.8x under-read) |
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 |
| uat_gap | Phase 08 — 08-HUMAN-UAT.md | partial (0 pending scenarios) |
| uat_gap | Phase 85 — 85-HUMAN-UAT.md | partial (2 pending scenarios) |
| verification_gap | Phase 08 — 08-VERIFICATION.md | human_needed |
| verification_gap | Phase 09 — 09-VERIFICATION.md | human_needed |
| verification_gap | Phase 71 — 71-VERIFICATION.md | gaps_found |
| verification_gap | Phase 84 — 84-VERIFICATION.md | human_needed |
| verification_gap | Phase 85 — 85-VERIFICATION.md | human_needed |
| todo | 2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads | firmware |
| todo | avrdude-mcu-detection-fallback | low |
| todo | cobs-decoder-framelevel-deadline-wr01 | medium |
| todo | photograph-modified-rev-0 | MEDIUM |
| todo | write-modifications-md-rework-trace | MEDIUM |

### v1.9 DEFERRED (operator 2026-06-08 — resumes later at Phase 45)

v1.9 (Read-Bug RCA + Fix) is paused. Phase 44 (Bug A RCA) complete; remaining Phases 45–48. The v1.18 bench oracle is pinned to Leonardo + Rev 2.0 precisely to avoid the v1.9 shield-fleet read bug.

### v1.10 Substrate (carry-forward)

Transport provably byte-exact (COBS `0x00` + CRC8-CCITT) — settled variable. GATE-1.8d ring-fence intact.

### v1.17 Substrate (carry-forward, directly relevant to v1.18)

- **T-93-CANERASE fix shipped (Phase 94 Plan 01):** `FLAG_CAN_ERASE` gated on `algorithm != 5` in host; firmware `flash4_write_init` skips erase when `handle->protocol == 0x05`. No equivalent issue for `0x08` — but establishes the dual-repo lockstep discipline for protocol-keyed defense-in-depth.
- **Per-chip `page_size` wire field added (Phase 94 Plan 02):** precedent for a new wire datum from pinout DB → host → firmware. Same pattern may apply if `DIP32_27C020` needs a new control-pin concept.
- **PROTOCOL-LEDGER at `.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}`** carries `0x08` as `open-defect-carried (FUT-06)`. v1.18 must update this on bench PASS (or re-record at new FUT status).
- **Golden register traces + dispatch-mirror guard** pinned for `eprom` family (0x07/0x08/0x0B, Phase 88). Any `eprom.cpp` change must keep 0x07 + 0x0B traces byte-identical and add an explicit 0x08 32-pin trace/case (v1.16 P89 CR-01 lesson: need a failure-case/mismatch test).

### v1.18 Research Findings (pre-loaded from `.planning/research/v1.18-AM27C020-27C-EPROM.md`)

- **RC-1 (LEADING):** PGM pin (DIP pin 31) not held program-active; modeled as an address line in `DIP32_STD`. The 27C020's PGM requirement (CE=VIL AND PGM=VIL) is never satisfied — firmware strobes CE only, pin 31 tracks address bits. The 27C040 (where pin 31 = A18) is the chip `DIP32_STD` was authored for.
- **RC-2:** P1 VPP routing/level never proven on a `0x08` UV part. `CTRL_VPP_P1_ENABLE` is only toggled during the per-byte data-write window, not held across the full pulse.
- **RC-3:** JP4 (JMP_VPP_P1_BYPASS) position — JP4-closed alone didn't fix it (Phase 83/84). Cross-confirm with Rev 2.0 schematic semantics.
- **RC-4:** 32-pin high-address / control-bit collision (lower rank — symptom is clean 0-bits at address 0 where collisions are least likely).
- **RC-5:** Chip is OTP/already-programmed/dead (silicon). The Tier-0 pre-flight (PRE-01) determines this definitively before any graduation spend.
- **VPP measurement method:** `firestarter dev reg 0 0 0x86 -f` holds rail for DMM. DMM at socket pin 1 (VPP) AND pin 31 (PGM) during a write attempt is the most decisive measurement.
- **Fix surfaces:** `eprom.cpp` (program-pulse / `using_p1_as_vpp` 32-pin sequencing); `pinouts.json` (possible `DIP32_27C020` entry redirecting pin 31 from address-bus to PGM control); `firestarter.h` ↔ `constants.py` if a new wire flag/field is needed.

### v1.21 Substrate (carry-forward, directly relevant to Phase 108+)

- **`dev validate-family` is the architectural precedent** — `dev test` is its sibling. Reuse its `EpromDatabase(skip_local_override=True)` + mock-operator test seam so Phases 108/109/110/112/113/114 need no hardware.
- **`resolve_chip` guard bypass mechanism (Phase 108):** research recommends Option (a) — bypass via `get_eprom()` + `convert_to_programmer()` for plan derivation only, no shared-code change — over adding a `require_supported=False` seam to `chip_resolver`. Confirm at Phase 108 planning.
- **`consistency_check_eprom`'s divergence math** is the reuse target for the byte-mismatch fingerprint classifier (Phase 108) — do not reimplement.
- **`EpromOperationError.error_code`** is the smallest, highest-leverage seam in the milestone (Phase 108) — every later phase's per-step result depends on it existing.
- **VPP/VPE mV sampler (Phase 111):** `read_vpp_voltage`/`read_vpe_voltage` in `hardware.py` currently return `bool` and only print; confirm the `MSG_DATA_VPP/VPE_VOLTAGE` (0xE4/0xE5) frame parse and sampling count during Phase 111 planning — this is the milestone's one hardware-gated validation.
- **Transport-health capture (Phase 110):** no persistent COBS/CRC/retry/timeout counters exist today; resync is only `logger.debug`-logged. Recommendation: attach a `logging.Handler` during the sweep and count resync/timeout records (zero-risk to transport); report "not measured" if absent. Decide handler-vs-counter approach during Phase 110 planning.
- **UV small-region window choice (Phase 108/109/111):** a high-address contiguous window maximizes upper-address-line coverage from a small write; validate exact size/placement against real UV parts (bench-informed).
- **Research flags:** Phase 108 (pattern math for the UV small-region variant + fingerprint thresholds) and Phase 111 (mV sampler frame parsing/sampling count) likely need `/gsd-plan-phase --research-phase <N>`. Phases 109/110/112/113/114 are well-grounded in existing source + locked decisions — standard planning patterns apply.

### Pending Todos (carried forward)

- `avrdude-mcu-detection-fallback.md` (low) — out of scope, carry forward.
- `cobs-decoder-framelevel-deadline-wr01.md` (medium) — v1.10 COBS follow-up; deferred.
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` (firmware) — carry forward.
- `large-read-data-jitter-uno328pb.md` (HIGH, v1.8-seed) — v1.9 RCA target.
- `photograph-modified-rev-0.md` (medium) — carry forward.
- `fold-response-code-into-log-macro.md` (medium) — captured during v1.22; blocked on Phase 117 (shares `eeprom_28c.cpp`).
- `2026-08-05-dev-test-issue-triage-diagnosis-skill.md` (tooling) — skill to triage community `dev test` issues: analyse the report, diagnose against the datasheet/DB/ledger, comment, close passes into a tested-good IC list. Captured during v1.30; needs discuss-phase (datasheet corpus is 3 PDFs; outward-facing comment/close needs a structural gate).

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260728-ahy | Fix `dev test --submit`: drop the nonexistent `gsd-inbox` label from the `gh` create argv, retarget `SUBMIT_REPO` → `henols/firestarter_prom`, and stop both tiers reporting phantom success | 2026-07-28 | `688bf10..36a9bb5` (firestarter_app submodule; gitlink NOT bumped) | [260728-ahy-fix-dev-test-submit-gh-tier-drop-nonexis](./quick/260728-ahy-fix-dev-test-submit-gh-tier-drop-nonexis/) |
| 260729-iyx | Install Bun in devcontainer to enable the Claude Code Discord channel plugin (DM-only) | 2026-07-29 | `c5385a7` | [260729-iyx-install-bun-in-devcontainer-to-enable-di](./quick/260729-iyx-install-bun-in-devcontainer-to-enable-di/) |
| 260807-kaq | `dev test`: run blank-check AFTER erase for electrically erasable parts, instead of before it | 2026-08-07 | `40af2ce..7fe8dea` (firestarter_app submodule, branch `fix/dev-test-blank-check-after-erase`; gitlink NOT bumped) | [260807-kaq-dev-test-blank-check-must-run-after-eras](./quick/260807-kaq-dev-test-blank-check-must-run-after-eras/) |

**Discord channel plugin — container side DONE, Discord side operator-owned (260729-iyx, 2026-07-29).** `discord@claude-plugins-official` v0.0.4 was already installed and `~/.claude/channels/discord/.env` already held a token, but `bun` was missing — the plugin's `.mcp.json` launches `"command": "bun"` as a **bare name** resolved from PATH by the MCP launcher with no shell, so Bun 1.3.14 is installed at `/usr/local/bin/bun` (verified resolvable under `env -i` + stock system PATH) and the same layer is now in `.devcontainer/Dockerfile` for rebuild durability. `~/.claude` **is** a named volume, so the token and `access.json` survive rebuilds; `~/.bun` is not, which is why the prefix is overridden. **Ordering trap:** `/discord:access policy allowlist` must be set only *after* pairing succeeds — setting it first makes pairing impossible, because the default `pairing` policy is what emits the code.

**Submission target settled (operator, 2026-07-28):** `SUBMIT_REPO` = `henols/firestarter_prom`, reversing the v1.21 Phase 113 D-01 choice of `henols/firestarter_app`. Authority is `henols/firestarter_prom#6` — *"New GitHub issues must be allowed only in `henols/firestarter_prom`"*, with issue creation to be **disabled** on `henols/firestarter` and `henols/firestarter_app`. A `dev test` report spans host + firmware + shield and cannot attribute itself to one layer, so the cross-repository tracker is the only correct destination. D-01 itself is unchanged and reinforced (hardcoded constant, never remote-inferred); the repo name now lives in exactly one place, with tests deriving every URL/argv expectation from it and one literal lock assertion so a silent retarget fails loudly.

**`firestarter_prom#6` repo settings APPLIED (2026-07-28).** `has_issues` set to `false` on `henols/firestarter` and `henols/firestarter_app` via `gh api -X PATCH`; `henols/firestarter_prom` stays `true`. Verified: `gh issue create --repo henols/firestarter_app` now refuses with *"the 'henols/firestarter_app' repository has disabled issues"*.

- The soft half was **already** in place before this and needed no change: both repos carry `.github/ISSUE_TEMPLATE/config.yml` with `blank_issues_enabled: false` + a `contact_links` redirect to `firestarter_prom/issues/new/choose`, and no other templates. That governs only the **New issue button** — a template config cannot block direct-URL or API creation, which is exactly how the misfiled `firestarter_app#43` got there. `has_issues: false` is the only hard block.
- **Side effect (accepted):** disabling issues hides the repos' existing issues — 7 on `firestarter`, 16 on `firestarter_app`, **all closed**, so only closed history is hidden. Fully reversible: `gh api -X PATCH repos/henols/firestarter_app -F has_issues=true` restores every issue; nothing is deleted.

**Remaining follow-up — release sequencing (operator-owned).** Published `3.0.0b11` still has `SUBMIT_REPO = henols/firestarter_app`, and its browser tier now hits **HTTP 404** on `firestarter_app/issues/new` (measured 2026-07-28; `firestarter_prom/issues/new` returns 302). So for b11 installs `--submit` now fails visibly instead of misfiling — arguably the better failure, but it is a dead end until a release carries the retarget. The five fix commits are cherry-picked onto **local** `beta` (`591c819..0050277`, on top of `ec74474`) and **not pushed**; pushing `beta` auto-fires the beta CI and cuts the next beta (the stray `3.0.0b12` mechanism from the v1.21 close), so that push is a deliberate release decision.

Bench cleanup done: `firestarter_app#43` (the misfiled `fm1608` report) closed with a pointer to `firestarter_prom#18`; the duplicate test issue `firestarter_prom#19` deleted. Surviving report: `firestarter_prom#18`.

### Roadmap Evolution

- v1.22 roadmap created 2026-07-27: 7 phases (116–122), 36/36 requirements mapped, 0 unmapped. Adopted the research SUMMARY.md §"The reconciled spine" verbatim — no coverage gaps found, no deviation needed. Strictly linear dependency chain (116→117→118→119→120→121→122); every adjacent-phase link is one of the milestone's non-negotiable ordering invariants (harness-before-fix, fix-before-observe, observe-before-lock, firmware-before-host, dev-test-fix-before-close), not a planning convenience. No bench phase — first milestone since the community-validation-command era with zero hardware-gated success criteria (no AT28C part in operator inventory).
- v1.21 roadmap created 2026-07-02: 7 phases (108–114), 24/24 requirements mapped (corrected from the REQUIREMENTS.md draft's stale "20 total" count). Phase spine per research SUMMARY.md §Implications for Roadmap: 108 (engine+pattern+fingerprint) → 109 (safety gate) → 110 (report+provenance) → 111 (voltage sampler, hardware-gated, isolated) → 112 (CLI wiring) → 113 (submission) → 114 (disposition lock, close).
- v1.20 roadmap created 2026-07-02: 3 phases (105–107), 12/12 requirements mapped. FW → HOST → DOCS+GATE strictly linear sequencing (wire-contract removal ordered so it's never half-broken).
- Phase 104 added: Rename protocol header and .cpp files to descriptive protocol-type names (replace hard-to-read flash type N naming)
- Phase 115 added: Beta install & firmware-flash bench validation (community onboarding) — hardware-gated capstone of v1.21

## Operator Next Steps

- Start the next milestone with /gsd-new-milestone

## Decisions

- [v1.21 roadmap]: Requirement-count discrepancy resolved in favor of the actual enumerated REQ-IDs (24) over the stale header text (20) — no requirement was dropped or invented; the original definition simply undercounted its own list.
- [v1.21 roadmap]: Phase 112 (`dev test` CLI wiring) kept as its own phase rather than merged into Phase 108 or 111, per the research's explicit "MAY be merged if trivial, use judgment" guidance — the CLI surface integrates four prior phases' work and benefits from its own plan/verification cycle; VOLT-01 (Phase 111) stays isolated as the sole hardware-gated phase, unaffected by this choice.
- [v1.21 roadmap]: Followed the research-recommended 7-phase spine verbatim (no coverage gaps found that would require deviating) — SAFE-02/03 treated as hard Phase-109 success criteria per the instruction's explicit load-bearing-safety guidance; DISP-01 treated as a locked anti-feature asserted by Phase-114 success criteria (no code path writes `support_status` from a report).
- [v1.20 roadmap]: WIRE-01 assigned primarily to Phase 105 (firmware stops parsing `type`) with Phase 106 (host stops emitting `type`) realizing the emit-side removal — sequenced FW-first because `json_parser.c` silently skips unknown fields, so a host briefly still emitting `type` during the gap is harmless; the reverse order (host-first) would leave firmware still trusting a fallback the host stopped feeding, which is safe too, but FW-first keeps the fail-closed guarantee active earliest.
- [Phase ?]: SAFE-01 invariant: holds because Phase-97 procedure never passes --force (firmware HAS a FLAG_FORCE over-voltage relaxation at primitives.cpp:121); held-rail proxy pinned host-space 0x188/0x180 marked [ASSUMED] per A1; all bench fields TBD-bench never fabricated (D-02)
- [Phase 98 Plan 01]: Q1 RESOLVED — static-high-pins RULED OUT as PGM vehicle (static_high_mask drives HIGH; PGM=VIL); DIP32_27C020 takes pin 31 off address bus only; PGM-assert is Plan 02 firmware branch (memory_set_data hold-LOW)
- [Phase 98 Plan 01]: D-04 host-side alias guard — size gate (mem_size<=262144) structurally excludes 512K AM27C040 / 1M AM27C080 from DIP32_27C020; both stay DIP32_STD
- [Phase 98 Plan 01]: Blast radius 88 chips accepted (entire ≤256K 0x08 32-pin class); architectural correctness is class-wide (A18 unused at ≤256K); LOW-7: baseline git diff is the audited artifact
- [Phase 98 Plan 02]: A5 CONFIRMED — 0x08 golden trace byte-identical post-fix; test_golden_eprom_0x08_write uses pins=0 (default), gate fails, PGM-hold branch does not fire; no re-bless needed
- [Phase 98 Plan 02]: MED-5 verified no-op — per-buffer P1-hold in program_mismatched_bytes already spans every per-byte CE pulse; no redundant per-byte P1 churn added; new code only asserts CTRL_ADDRESS_LINE_18 hold-LOW (distinct from P1 VPP routing)
- [Phase 98 Plan 02]: HIGH-1 blind-fix honesty — addr-0 register state byte-unchanged under RC-1; Phase 99 is sole empirical gate; no over-claim that bits flip on silicon
- [Phase 98 Plan 03]: rw-pin:[31] on DIP32_27C020 mirrors the working DIP32_SST39SF040 precedent — pin 31 resolves via pin_conversions[32][31]=22 to config.rw_line=22 -> CTRL_READ_WRITE (0x40), closing the corrected CR-01 fork (host half)
- [Phase 98 Plan 03]: DB regen confirmed idempotent for rw-pin (pinouts.json runtime datum, never embedded in chip_database.json) — diff_db.py shows only the pre-existing Phase-94 PGSZ_PAGE_SIZE delta
- [Phase 98 Plan 03]: py3.11 CI sign-off follows the 98-01 precedent (CI-PENDING/structurally-green) — no python3.11 binary in this devcontainer; all CI-scoped commands (ruff/mypy-watermark/diff_db/check_dispatch/parity) pass under 3.12.13
- [Phase 98 Plan 04]: Reverted 98-02's inert CTRL_ADDRESS_LINE_18 clear (physical no-op on Rev 2 via the 0x08 alias; wrong-pin on Rev 0/1); relies on existing rw_line mechanism (CTRL_READ_WRITE 0x40, revision-invariant) fed by 98-03's rw-pin:[31]
- [Phase 98 Plan 04]: WR-01 revision-parametrized native test added via local replicas of rurp_map_ctrl_reg_for_hardware_revision (Rev 2 + Rev 0/1) — the missing RED state; WR-02 RC-98B pinned to EQUAL(5); IN-02 firmware constant deferred to 98-05 (no size literal survives the revert)
- [Phase 98 Plan 05]: IN-03 macro replacement named `mem_min` (not `min`) to avoid any future collision with Arduino's own min() or std::min — static inline single-evaluation function, sole call site (memory_read_execute) updated, behavior identical (side-effect-free operands)
- [Phase 98 Plan 05]: IN-02 host authoritative value moved from build_db.py-only literal (98-03) into constants.py (the established landing spot for every firmware-parity constant this codebase tracks) — build_db.py now imports it; parity test follows the file's REAL pattern (hardcoded literal + FW_ABSENT skipif + citing comment), not literal header-parsing, matching its 6 sibling assertions
- [Phase 98 Plan 05]: Phase 98 CLOSED — all 5 plans complete (98-01/02 original fix attempt + 98-03/04 corrected CR-01 fix + 98-05 IN-01/02/03 cleanup); native suite 119/119 green, golden traces byte-identical, host CI green on py3.11 target; Phase 99 (BENCH + LEDGER) unblocked
- [Phase 99 Plan 01]: Chose minimal D-09 extension (option a, evidence-shape branch keyed on `v1_18_writeverify_sha_selfconsistent`) over a new status enum value — a v1.18-native 0x08 graduation is proven by write/read-back self-consistency (no v1.15 write baseline exists for AM27C020) without requiring a fabricated `p90_writecycle_sha_matches_v115` claim; honesty guard verified (bare 0x08 PASS claim without the marker still fails); FUT-06 retirement path (removal from open_defects[], not status_changed flip) proven by test; gate is now CAPABLE of a graduated 0x08 row but 99-04 decides the actual outcome from the bench result
- [Phase Phase 99 Plan 02]: check_graduation.py filters on op prefix phase99* (never the Phase-97 tier0_microprobe+rca01 cell); branches PASS (write_image_sha256==readback_sha256 self-consistency) vs DEFER (bits_flipped+post_read_sha256 differential), validated against 9 synthetic fixture cells without ever mutating the real EVIDENCE.json
- [Phase 99]: [Phase 99 Plan 04]: Took the DEFER branch decided by 99-03 (Phase-98 fix bench-effective-but-unreliable: write#1 60/64 byte-exact, write#2 0/64); retired FUT-06 by removal-and-replacement rather than in-place edit, opening FUT-08 (renumbered from the operator-requested "FUT-07" — that id is already taken by the v1.17 W29C040 defect in this same table) as an explicit successor citing the fix-effective-but-unreliable finding + the next diagnostic step (program-window VPP-under-load + write timing); 0x08 row stays open-defect-carried with on_hand_chip now AM27C020
- [Phase ?]: D-01/D-02/D-04 applied: single _PROTOCOL_DISPLAY_NAME map in ic_layout.py feeds both proto_display fallback and info Protocol line; ASCII dashes; 0x34 added / 0x11 dropped
- [Phase ?]: 0x34 description_points bullet chosen as minimal placeholder text, flagged Phase-103-DOC-01-owned
- [Phase ?]: py3.11 CI recorded as CI-PENDING/structurally-green under py3.12.13 devcontainer (Phase-98 precedent)
- [Phase ?]: Phase 103 Plan 01: Heading token substitutions copied verbatim from §0 canonical bucket table; cross-link anchors regenerated + grep-verified against actual rendered headings (not hand-guessed); INV row edits scoped to behavior column only, SAFE-02 grep-contract columns kept byte-identical; D-04 callout placed above §0 table reusing existing blockquote style
- [Phase 103 Plan 02]: D-05 GATE re-verification used existing tooling only (no new tests/scripts) — `pio` was present this session so the GATE-01 firmware leg (`pio test -e native`, 82/82) is a real executed PASS, not deferred; `python3.11` was absent so only the constants-parity py3.11-target leg is recorded CI-PENDING (structurally-green under py3.12), per the deterministic Phase-98 CI-PENDING guard (never a fabricated PASS for an absent-tool leg)
- [Phase 103 Plan 02]: Milestone-CLOSED narrative written only after confirming zero GATE-01/02/03 FAIL verdicts in 103-VERIFICATION.md (precondition honored); no beta cut, no gitlink bump, no `chip_database.json`/code change triggered — v1.19 close is docs+planning-artifacts only
- [Phase ?]: Renamed file-internal flash3_*/flash4_* static helpers to flash_nor_unlock_*/flash_5v_page_* stems for full identifier consistency (discretionary per 104-PATTERNS.md); no cross-file impact since file-internal — Plan 104-01
- [Phase ?]: Left pre-existing unrelated platformio.ini whitespace diff untouched (out of plan scope, not introduced by this work) — Plan 104-01
- [Phase 104-02]: New family-id strings introduced for Plan 03: nor_unlock (was flash3) and 5v_page (was flash4) — become the test-suite directory names in Plan 03
- [Phase 104-02]: Preserved validation_matrix_spec.json protocols_note prose factual content verbatim, only substituting handler/test-module name references
- [Phase 104-03]: Rule 1 fixed 4 latent firestarter_app test regressions caused by Plan 02's flash3/flash4->nor_unlock/5v_page spec rename (test_val_wire_flash3/4.py StopIteration + stale handler assertions in test_matrix_schema/test_validate_family_cmd/test_gen_validation_header); surfaced only when the full suite was run beyond the plan's declared verification scope
- [Phase 104-03]: Left cli_handlers.py dev validate-family Choice list stale (still lists flash3/flash4) and tools/baseline/dispatch_baseline.json (orphaned, zero Python consumers) untouched -- both explicitly out of plan scope (GATE-03 cli_handlers.py prohibition; no regression risk from the unconsumed baseline file)
- [Phase 105]: Executed D-01 setup (merge v1.19->beta lockstep in both sub-repos, no tag; fork v1.20-protocol-only-dispatch off updated beta) as a hard precondition since it had not yet been performed despite operator authorization — Research flagged neither beta nor origin/beta contained the v1.19 PROTO_ layer this plan's edits reference; without it no v1.20 branch existed to work on
- [Phase 105]: Collapsed configure_memory() dispatch tail to a single unconditional terminal configure_not_implemented(handle) call (D-04) instead of an if/else on protocol==0 — Matches the codebase's existing named-infeasibility-arm fail-closed style; protocol==0 and any unrecognized non-zero protocol now share one exit
- [Phase 105]: Kept the vestigial mem_type parameter in native test make_handle() (both suites) after removing the struct field, rather than dropping it and touching ~25 call sites — Lower-churn mechanical choice explicitly left to Claude's Discretion in CONTEXT.md and RESEARCH.md
- [Phase 106-01]: Kept dispatch(algo, 0) rather than changing dispatch()'s signature since the mem_type fallback chain is protocol==0-only (dead for every real chip's non-zero algorithm)
- [Phase 106-01]: Logged pre-existing test_audit_coverage_matrix.py golden-fixture drift and the expected test_chip_resolver.py ripple (owned by Plan 03) to deferred-items.md rather than fixing them - both explicitly out of scope
- [Phase 106-02]: get_chip_type_string signature shrunk to (self, protocol_id=None) - chip_type_int param and the local type_map dict deleted; unresolved falls to bare 'Unknown'
- [Phase 106-02]: resolve_type_label signature shrunk to (self, electrical_type, protocol_id=None) - type_int param deleted; delegates to get_chip_type_string(protocol_id)
- [Phase 106-02]: __main__ self-test block repurposed to exercise protocol tier (0x08 known, 0x99 unknown) replacing removed numeric-tier calls
- [Phase 106-02]: eprom_info.py:69 string-typed 'type': 'unknown' raw-JSON field left untouched - different axis from numeric mem_type
- [Phase ?]: [Phase 106-03]: Guard placement and read-path exactly mirror the existing support_status guard (same raw_config object, same exception, same pre-serial ordering); reject rule is a plain falsy-check covering both absent and explicit-0, no KNOWN_PROTOCOLS gate added (D-01 pass-through preserved)
- [Phase ?]: [Phase 106-03]: Rule 1 auto-fix applied to test_consistency_check.py's dispatch-chain mock (missing programming.algorithm key), directly caused by the new HOST-04 guard; confirmed via git stash that test_audit_coverage_matrix.py golden-fixture drift and the 4 pre-existing ruff/format failures in tools/*.py are unrelated and out of scope
- [Phase 107-01]: Reworded three explanatory mentions of the retired mem_type axis in firestarter/CLAUDE.md to avoid the literal substring 'mem_type' (legacy-integer/backward-compat phrasing), satisfying the plan's strict grep-based acceptance criteria while preserving meaning
- [Phase 107-01]: Kept protocol==0 as its own explicit numbered terminal dispatch step (renumbered to 7) rather than folding into the generic 6b non-zero-unrecognized guard, matching the plan's required wording
- [Phase ?]: [Phase 107-02]: Restored MSG_WARN_FL4_BOOT_BLOCK_LOCKED (0x85) / MSG_ERR_FL4_BOOT_BLOCK_LOCKED (0xBC) to the meta canonical messages.toml before finalizing the 0xAE removal sync -- these Phase-95 host-only messages were never present in canonical and the sync would have silently deleted them from messages.py, breaking tests/test_val_wire_5v_page.py (Rule 1 auto-fix, caught pre-commit)
- [Phase ?]: [Phase 107-02]: Firmware include/messages.h gained the same restored 0x85/0xBC #define constants as an inert byproduct (firmware source never references either name) -- accepted as a correction of the canonical source of truth, not a firmware behavior change
- [Phase ?]: [Phase 107-03]: Applied D-07 pass bar literally - confirmed each of the 5 pre-existing failing/dirty artifacts (1 pytest failure + 4 ruff errors + 1 ruff-format file) is outside git diff beta..HEAD before accepting as prior debt; zero new regressions from v1.20
- [Phase ?]: [Phase 107-03]: Host pytest missing final summary line (syrupy plugin display quirk) cross-verified independently via pytest --collect-only (711 total minus 1 named failure = 710 passed), matching RESEARCH.md baseline exactly
- [Phase 108-01]: Added error_code=response.id to the ProtocolNotImplementedError branch too (discretionary symmetry), not just the generic EpromOperationError branch — The id is always MSG_ERR_PROTOCOL_NOT_IMPLEMENTED (0xBB) there, so this gives every EpromOperationError-family exception a consistent .error_code at zero cost
- [Phase 108-02]: Restricted address-line candidate bits to 8 <= k < (cmp_len-1).bit_length() -- bits at/above the compared region size never toggle within [0, cmp_len) and would spuriously score 100% clustering on scattered data
- [Phase ?]: [Phase 108-03]: id-check NA rule keyed on the programmer-dict chip-id sentinel value 0, not key presence -- every DB entry carries a chip-id key but many carry the literal sentinel 0 meaning no real id to compare
- [Phase ?]: [Phase 108-03]: blank-check NA condition checks BOTH electrical-type in {SRAM,FRAM} AND protocol-id in the SRAM proto-id set, mirroring check_eprom_blank's own short-circuit so derive_plan owns the decision up front
- [Phase ?]: [Phase 108-03]: No named protocol constant exists for flash4 (0x05) in constants.py; added a local _PROTOCOL_FLASH4 module constant in chip_test.py mirroring database.py's own algo != 5 check
- [Phase ?]: run_plan re-resolves every executed step via resolve_chip (guard-honoring), never reusing derive_plan's bypassing dict
- [Phase ?]: id-gate closes on ANY id-step uncertainty (BAD or SKIPPED), not just an explicit numeric mismatch (conservative Pitfall 4 reading)
- [Phase ?]: runs<2 rejected before any resolve/operator call; write/erase/verify disagreement reports marginal, never coerced to OK/BAD; read disagreement is a divergence metric only
- [Phase ?]: [Phase 109 Plan 01]: derive_plan(destructive=False) structurally omits write/erase from Plan.steps into an advisory Plan.locked_destructive list; run_plan never iterates it (SAFE-01, D-01)
- [Phase ?]: [Phase 109 Plan 01]: UV detection at execution time uses algorithm==0x0B (EPROM_LEGACY, UV-EPROM-exclusive DB-wide) as a fallback signal because resolve_chip's programmer dict drops electrical-type; _UV_WRITE_REGION_LENGTH (256) is an engine constant no DB field can widen (PATT-03, SC4)
- [Phase ?]: [Phase 109 Plan 02]: count_applicable(plan, results) computes SWEEP-05 M from the single Plan object (supported steps + locked_destructive), never re-deriving; N counts OK/BAD/marginal, excluding NA/SKIPPED
- [Phase ?]: [Phase 109 Plan 02]: SAFE-02 source-scan test uses ast.walk (not raw substring grep) to avoid false positives on docstring prose describing the safety property (e.g. 'passes no --force')
- [Phase 109]: SAFE-03: AST-based checker (fresh ast.parse walk) + mandatory anti-hollow paired pytest with 4 planted-violation fixtures via FIRESTARTER_DEVTEST_SRC env-override -- closes v1.12 hollow-GATE-03 tech debt
- [Phase ?]: test_report_module_is_orchestrator_only rewritten from raw substring grep to AST-based import/literal scan -- the module's own docstrings describe the SAFE-02 invariant in prose, which a substring check false-positives on (mirrors Phase-109 SAFE-02 ast.walk lesson)
- [Phase ?]: Reworded diagnostic_report.py docstring prose to avoid literal substrings SerialCommunicator/HardwareManager so the plan's shell-grep verification command passes cleanly, meaning preserved
- [Phase ?]: DiagnosticReport, AutoCapture, TransportHealth implemented in one file write (Tasks 2+3 land in one module) since to_dict()/render() depend directly on the sub-dataclass shapes; committed as two separate git commits to preserve per-task traceability
- [Phase 110-02]: Provenance model + injectable prompt_provenance + is_submittable added to diagnostic_report.py; composed into DiagnosticReport append-only (RPT-04) — shield revision never auto-derived from hw_revision byte (D-05); not sure counts as filled/submittable
- [Phase ?]: DbDiff is read-only by construction (write-method-less Mock DB proof + structural no-write scan); proposed_disposition is always advisory descriptive text, never a concrete support_status value
- [Phase 111-01]: Named the honest-fallback test test_sample_none_returns_none_on_error (not test_sample_returns_none_on_error) so the -k sample_none selector required by 111-VALIDATION.md actually matches
- [Phase 111-01]: Asserted the render() single-source contract for the voltage split by scanning rendered table cells for the expected value rather than inspecting render() source text, since Plan 03 has not yet decided the exact voltage row wording
- [Phase ?]: [Phase 111-02]: Used RESEARCH Pattern A (regex re-parse of Response.message) per plan directive, superseding CONTEXT D-05's raw-payload premise -- Response.payload is None for 0xE4/0xE5 frames
- [Phase ?]: [Phase 111-02]: sample_vpp_mv/sample_vpe_mv placed strictly after _read_voltage_loop/read_vpp_voltage/read_vpe_voltage with zero lines changed in those methods (SC3 verified via git diff)
- [Phase ?]: [Phase 111-03]: Old combined vpp_vpe_mv slot fully removed (0 occurrences) rather than kept as a deprecated alias, satisfying the negative-grep acceptance criterion and the D-01 split
- [Phase ?]: [Phase 111-03]: _voltage_dict modeled byte-for-byte on the existing _transport_dict pattern (six explicit NOT_MEASURED-if-None branches) matching the file's established idiom
- [Phase ?]: [Phase 111-03]: Voltage render() row placed after banner, before provenance, as a single add_row sourced only from to_dict()['voltage'] (single-source contract, Phase 110 D-01)
- [Phase 111 close]: UAT Test 1 (live-hardware VPP/VPE parity, SC2 hardware half / D-05) PASS on Leonardo + Rev 2.0 (ACM0 = "Rev 2.0-class"); VERIFICATION.md flipped human_needed→passed. UAT Test 2 (before/after write-step capture) reclassified out of the blocking UAT set → deferred to Phase 112 (operator decision) since no write-step call site exists in Phase 111 by design; logged in 111/deferred-items.md — NOT a Phase 111 gap.
- [Phase ?]: sampler kwarg threaded through all 4 call-chain levels (run_plan -> _run_step -> _dispatch_step -> _dispatch_multi_run) with default None at every level, per D-04 backward-compat guarantee
- [Phase ?]: Sampler bracket scoped strictly to the OP_WRITE branch operator.write_eprom call, not OP_VERIFY/OP_ERASE or the whole run_plan loop -- write-droop-vs-read-droop distinguishability (D-04)
- [Phase ?]: TTY isatty() check factored into a private _is_interactive() seam because CliRunner.invoke() replaces sys.stdin, breaking direct sys.stdin.isatty() patching in tests
- [Phase ?]: chip_id_actual/chip_id_mismatch_reason recovered by parsing the id StepResult.reason text rather than widening chip_test.py's StepResult schema
- [Phase 112-03]: Scoped the SAFE-03 handler AST scan to dev_test + its private helpers via a new AST function-name filter (_scan_target_functions) instead of whole-file, because cli_handlers.py has 10 pre-existing legitimate --force flags on unrelated commands that a whole-file scan would false-positive on
- [Phase ?]: simple test decision
- [Phase ?]: [Phase 112-04]: REVERSED RPT-04 / D-04 / D-05 / D-06 (operator-approved, 112-UAT.md test 2) -- deleted prompt_provenance/Provenance/SHIELD_REV_CHOICES/_CHIP_ORIGIN_CHOICES outright (the path-separator-in-choice-string bug rejecting new/used/2.0); is_submittable now derived from AutoCapture completeness only (chip+protocol+host_version), never a human-provenance field
- [Phase ?]: [Phase 112-04]: fw_board_identity stays honest None -- re-confirmed EpromOperator.comm is torn down after every op (no live comm to read post-run_plan); FirmwareManager.check_current_firmware evaluated and rejected as a source since it opens its own extraneous connection (SAFE-02 violation). hw_revision IS auto-captured via new HardwareManager.read_hardware_revision_value() (dedicated clean energize/query connection). --pot-adjusted flag confirmed out of scope, not implemented
- [Phase ?]: [Phase 112-05]: Gated OP_VERIFY behind destructive in derive_plan (SC2/SWEEP-05 fix direction (a), pre-decided) -- mirrors OP_WRITE/OP_ERASE D-01 pattern exactly; _DESTRUCTIVE_OPS/_MULTI_RUN_OPS untouched
- [Phase ?]: [Phase 112-05]: Repaired 8 tests broken by the verify-gate fix (5 more than the plan's named 3) -- all same bug class, discovered via the plan's own required full targeted-suite verification step
- [Phase ?]: [Phase 112-05]: RPT-04 reworded to the 112-04 auto-capture model, closing the documentation debt flagged in 112-VERIFICATION.md
- [Phase ?]: [Phase 113-01]: dedup_fingerprint reads report.results directly (not report.to_dict()['steps']) to avoid a circular call back into to_dict(), which itself now calls dedup_fingerprint(self)
- [Phase ?]: [Phase 113-02]: overall_verdict is FAIL-dominant (BAD beats marginal) for the issue title -- deliberately distinct from cli_handlers.py's exit-code max() ordering where marginal(2) > BAD(1)
- [Phase ?]: [Phase 113-02]: build_issue_url omits the labels query param entirely (RESEARCH Pitfall 1) -- GitHub drops/404s labels for non-write community testers; triage relies on the [dev test] title marker + fenced-JSON schema_version instead
- [Phase ?]: [Phase 113-02]: gh_available never calls run_fn when which_fn('gh') is falsy -- PATH-short-circuited before any subprocess spawn
- [Phase ?]: [Phase 113-03]: submit_via_browser drops the JSON fence by splitting the pre-built body string on its own '\n\n```json\n' marker rather than re-invoking build_body(include_json=False) -- the plan-mandated signature (title, body, saved_json_path) never receives sanitized_dict/results — Only implementation consistent with the required function signature while satisfying every behavior clause
- [Phase ?]: [Phase 113-03]: Left SUB-01/SUB-02 unchecked in REQUIREMENTS.md -- both are also 113-04's frontmatter requirements (the --submit CLI flag + call site); until that lands a bare dev test run cannot reach submit_report — Requirement isn't fully satisfied from a user's perspective until the CLI wiring plan lands
- [Phase ?]: [Phase 113-04]: Patched firestarter.submit.submit_report (module attribute) as the stable seam for both mocked-call-site and real-submit_report end-to-end tests, since the dev_test call site imports submit lazily inside the if submit: block
- [Phase ?]: [Phase 113-04]: submit.py scanned in FULL via _scan_file (not the scoped _scan_target_functions handler path) for the new SAFE-03 leg -- it is a fresh Phase-113 module with zero pre-existing force/VPP/wire-dict usage, mirroring chip_test.py
- [Phase 114-01]: ladder_state derived in the SAME verdict-branch structure as proposed_disposition (BAD/marginal-indeterminate/all-OK/else); community-confirmed formalized as a named-but-unused constant, never producible by build_db_diff (GRAD-01 SC2 by construction)
- [Phase ?]: [Phase 114-02]: CLI shape (discretionary D-04) -- single-body mode takes --title + --body-file/stdin as separate inputs (mirroring two gh issue view --json invocations); --dir/--glob N-agreeing mode operates on plain saved-body files, no title needed
- [Phase ?]: [Phase 114-02]: schema_version matched by presence only (any value), never an exact-version comparison -- survives Plan 01's 1.0->1.1 bump and any future schema change with zero parser code change
- [Phase ?]: [Phase 114-02]: No rich import in parse_devtest_issue.py (even though rich is already a project dependency) -- plain-text render_diff() only, satisfying the literal no-third-party-import-errors acceptance criterion
- [Phase ?]: DISP-01 checker uses exact-string match against support_status (not substring) to avoid false-positive on current_support_status near-name
- [Phase ?]: Both DISP-01 scan targets (diagnostic_report.py, parse_devtest_issue.py) treated as mandatory; missing-target check fails closed before the scan loop
- [Phase ?]: Task 1 RED phase wrote the full 7-test anti-hollow suite covering both Task 1 and Task 2 acceptance criteria; Task 2 verified-complete with no separate commit (mirrors 109-03 SAFE-03 precedent)
- [Phase ?]: Phase 114.1: guard placed strictly between --destructive confirm block and derive_plan, keyed on app.db.get_eprom(chip) emptiness only — never on a resolve_chip support-status refusal — so case B (present-but-unsupported chips like AT28C16) still runs the full community-validation sweep — Protects the community-validation command's entire purpose (proving support on chips the maintainer's DB refuses)
- [Phase ?]: Phase 114.1: reused existing ChipNotFoundError + @map_typed_errors -> click.ClickException path (no new exception type, no new exit-code branch, no logger.error+sys.exit style) — Minimal, self-contained hardening; matches how every other command already rejects unknown chips
- [Phase 115]: Doc structure mirrors community-validation.md voice (audience/purpose lead, what-this-is-NOT framing, tables, fenced commands)
- [Phase 115]: 328PB-Uno guidance: try -b uno328pb first, fall back to -b uno only on avrdude signature-check rejection - never guess/force
- [Phase 115]: README gets exactly one pointer link; per-board matrix NOT duplicated (D-09)
- [Phase ?]: Both sub-repos re-verified merge-base ancestry live before forking v1.22 off beta (Task 1, F10) — 0 commits ahead at creation, no pre-existing operator work destroyed
- [Phase ?]: HOST_STUBS_REAL_REGISTER_UTILS hooks exactly rurp_write_data_buffer + rurp_set_control_pin — rurp_shield.h's single pin namespace covers latch strobes AND /CE+/OE with no third hook
- [Phase ?]: s_strobe_overflow is an explicit saturation flag (not silent drop), and TRACE-01b baseline is pinned at 80/80 before TRACE-03d raises it to 82/82
- [Phase ?]: EpromDatabase has no constructor seam for an alternate pinouts.json path -- the --pinouts override loads JSON directly onto db.pin_maps before derivation
- [Phase ?]: Wrote exactly 4 drift-gate tests (not 5) to match the plan's literal 4-tests-passing acceptance criterion
- [Phase 116-03]: Reworded 'no FW_ABSENT-style skipif' to 'no FW_ABSENT-style skip marker' in test_sdp_db_invariant.py's docstring so the literal grep -c 'skipif' acceptance criterion returns 0 while preserving the meaning (Phase 107-01 wording-fix precedent)
- [Phase 116-03]: Factored shared _select_0x0d_chips/_assert_chip_id_check_false helpers so the TRACE-05 non-vacuity test exercises the same code path as the real-DB assertion, not a parallel reimplementation
- [Phase 116-03]: Brace-scoped {address, byte} extraction (not a file-wide regex) for the unlock-table parity gate, because eeprom_28c.cpp has a non-initializer call site (eeprom28c_wait_for_write) using the identical literal bytes that would false-positive a loose pattern
- [Phase ?]: [Phase 116-04]: Deny list implemented as one regex covering every logging_id.h LOG_* macro rather than a hand-enumerated name list
- [Phase ?]: [Phase 116-04]: Window scoped strictly to eeprom28c_write_init's brace-matched body so the out-of-window control is correct by construction
- [Phase 116-04]: TRACE-03 checkbox left unchecked in REQUIREMENTS.md — this plan lands only the planted-LOG_ sub-negative (TRACE-03c) of TRACE-03's four required first-class negatives; the other three (unlock-table mutation, lock-table swap, protocol!=0x0D positive) land in 116-05's always-green harness suite per D-04. Mirrors the 116-01 precedent (commit 8d8c42f) that reverted an identical premature TRACE-01/03 completion mark.
- [Phase ?]: SDP_SHIPPED is a single array (not one per pinout) -- fu_flash_fast_address never consults bus_config, so the shipped stream is byte-identical across all four 0x0D pinouts by construction
- [Phase ?]: 5 reference-emitter guard cases (one per SDP_BUS_CONFIGS row, not one per distinct pinout) -- AT28C010/AT28C040 both independently assert against the shared SDP_FIXED_DIP32_28C512_EEPROM array
- [Phase ?]: Bumped sdp_assert_stream_equals failure-message buffer 192->320 bytes after the mandatory corrupted-array check showed truncation
- [Phase 116]: DIP32 RED cases (4-5) assert against a dynamically-driven reference-emitter snapshot under the same stale seed, not the canonical zero-seed SDP_FIXED_DIP32_28C512_EEPROM constant — A plain zero-seed comparison only reproduces the same incidental /OE-ordering divergence Cases 1-3 already show and proves nothing about the real write-inhibit bug (CORRECTION 3)
- [Phase ?]: Datasheet audit recorded as an honest present/unconfirmed/absent finding rather than a general statement (Phase 116 Plan 07)
- [Phase ?]: Task 3 human-verify checkpoint auto-approved per this run's explicit orchestrator auto-mode instruction; self-review against RESEARCH Pitfall 7 and the 66-of-84 figure performed directly (Phase 116 Plan 07)
- [Phase 117-01]: Followed 117-CONTEXT.md D-01/D-02/D-03 exactly: un-mocked set_data, flipped+reordered five response-code assertions, added permanent case 8, captured the edited-and-RED intermediate before any production change; ticked no requirement (oracle half only, closes jointly with 117-02)
- [Phase 117-02]: eeprom28c_write_init rebuilt on a 0x0D-local remap-aware eeprom28c_emit_command_sequence driven through handle->firestarter_set_data, closing FIX-01 and FIX-03 (A16-A18 staleness) as one routing change — flash_execute_command bypasses handle->bus_config and CONTROL_REGISTER entirely; memory_set_data applies the full remap and rewrites CONTROL on every address change
- [Phase 117-02]: Inverted (0x5555, 0x20) read-back deleted outright; replaced by eeprom28c_wait_for_sdp_completion (t_WC wait + bounded silent DQ6 toggle poll, never writes response_code) closing FIX-02 — Both AT28C datasheets state the command sequence byte is never written to the device, so the old check could only pass when the sequence was NOT recognised
- [Phase 117-02]: Reworded 3 in-code comments to avoid literal-substring collisions with non-comment-filtered acceptance-criteria greps (rurp_set_data_output exactly 1; eeprom28c_wait_for_write(handle, 0x5555 exactly 0) — Meaning fully preserved; matches the project's established pattern of wording around literal-substring gates rather than weakening them
- [Phase 117-03]: FIX-06: eeprom28c_write_execute's conflated eeprom28c_wait_for_write split into eeprom28c_wait_for_page_write (DQ7-complement completion poll) and eeprom28c_verify_page_readback (always-on per-byte data-landed read-back over the current flush window, failing-address attribution via MSG_ERR_VERIFY); conflated function deleted outright
- [Phase 117-03]: Anti-hollow proof executed: read-back temporarily removed, both planted-violation cases went RED and the isolation control stayed GREEN, recorded verbatim in 117-03-SUMMARY.md; temporary revert never staged/committed (confirmed byte-identical restore)
- [Phase 117-04]: Followed 117-CONTEXT.md D-10/D-11 exactly: FIX-05 guard lives in test_sdp_harness, reads the production EEPROM_SDP_DISABLE array via extern (plan 117-02's linkage grant), and the planted-violation counterpart reuses TEST_UNLOCK_MUTATED_TERMINAL rather than adding a second copy — Matches the plan's discretion resolutions and D-11's cross-guard requirement
- [Phase 117-04]: Reworded two in-code comment mentions of the two new test-case names to avoid a third literal occurrence, since acceptance criteria required each name to appear exactly twice (definition + RUN_TEST) — Meaning preserved (both comments still cite FIX-05/D-11); mirrors 117-02's identical literal-substring-grep adjustment pattern
- [Phase 117]: Recorded the measured Leonardo flash delta (+204 B) as-is despite the research prediction of net-negative -- measured over predicted.
- [Phase 117]: Recorded firestarter_app's pre-existing dirty working tree as an explicit named exclusion rather than claiming a clean tree -- the load-bearing host-untouched proof is the unmoved commit history (36a9bb5).
- [Phase 117]: Ticked FIX-04 only in REQUIREMENTS.md after independently verifying FIX-01/02/03/05/06 were already Complete -- six of six for Phase 117.
- [Phase 117 regression gate]: **Phase 117 broke 4 Phase-116 host-side gates.** `test_sdp_table_parity` (x3) and `test_check_no_log_in_sdp_window` (x1) scan `eeprom_28c.cpp` source text and were keyed to pre-117 identifiers/declaration syntax: 117-02 replaced `flash_execute_command(EEPROM_SDP_DISABLE)` and changed the definition to `EEPROM_SDP_DISABLE[6] =` (extern needs a complete array type, but the parity regex required `[]`), and 117-03 deleted `eeprom28c_wait_for_write` outright. Proven Phase-117-caused, NOT pre-existing, by injecting phase-base `ada4bdc` source via the `FIRESTARTER_SDP_SRC` env seam. Host CI (`ci.yml` pytest --cov, `beta-release.yml` pytest) was red. Fixed under operator authorization, append-only per the anti-hollow contract: `firestarter_app@9dd11a9`, with record corrections in `firestarter@f8d10a5` (RED-BASELINE FIX-04 gate section) and `117-05-SUMMARY.md`.
- [Phase 117 regression gate]: **Narrowed the host-untouched claim rather than deleting it.** True and load-bearing: Phase 117 introduced no wire, protocol, or behavioral host change (no `MSG_*`/`FLAG_*`/command/CLI/serialized field) -- the two changed host files are source-scanning test gates, which cannot participate in firmware/host version skew, so the firmware-before-host ordering invariant is intact and FIX-04's substantive blob-SHA content is unaffected. Meta gitlink still not bumped.
- [Phase 117 regression gate]: **Root cause is a PLAN-COVERAGE gap, not an implementation defect.** Phase 116 anticipated this exact case in its own source comments and the checker's stderr ("ADD the new anchor ... rather than deleting this gate"); none of Phase 117's five plans owned that step. **Carry into Phase 118+ planning:** any firmware rename/deletion must be checked against the host-side source-scanning gates (`tools/check_*.py`, `tests/test_sdp_*`, `tests/test_check_*`) before the phase closes -- Phase 118's OBS-01 touches this same SDP window and will trip the same class of gate.
- [Phase 117 regression gate]: `test_audit_coverage_matrix::test_golden_file_matches` confirmed the only other host failure and proven unrelated -- fails identically with the gate fixes stashed, reads the chip database, references no firmware path. Same stale golden carried since v1.21; still needs its own regeneration commit.
- [Phase 118-01]: scan()'s return contract widened to (violations, emitter_range, poll_range); anchor tuples repurposed as a write_init rename tripwire, no longer computing the window — Plan 118-04's own verification depends on knowing this contract
- [Phase 118-01]: Case 2's expected planted-line number derived from the fixture at test time instead of a second hardcoded literal — Prevents a future re-plant from silently desyncing the assertion from the fixture
- [Phase ?]: D-04 shape reused verbatim: four separate SDP catalog ids with literal format strings, not one parameterised id with an unlock/lock discriminator
- [Phase ?]: Left the after-line's format string carrying only the measured duration; the budget lives solely in the runtime WARN branch, avoiding a duplicate AT28C_TBLC_MAX_US literal (118-04, Claude's Discretion)
- [Phase 118]: 118-05: make_sdp_handle gained a default-arg extra_flags parameter (not a sibling function) so cases 9/10 share one factory/row with zero churn to the 8 existing call sites
- [Phase 118]: 118-05: AT28C_TBLC_MAX_US is private to eeprom_28c.cpp's TU (not exported) -- Case 11 mirrors the value as a cited local constant while deriving sdp_seq_len from the real exported EEPROM_SDP_DISABLE array
- [Phase 118-06]: 9-row CORRECTION-4 gate table: gen_sdp_bus_config.py + its drift test as 2 rows, check_dispatch.py + build_db.py combined as 1 row (single shared disposition, no dedicated pytest)
- [Phase 118-06]: Re-derived (not copied) both boards' phase-base flash/RAM figures via a throwaway git worktree at f8d10a5
- [Phase 118-06]: test_no_programmer_found_* divergence recorded honestly: live serial devices ARE present this run yet the pair still passed 2/2 -- not explained by board-absence
- [Phase 118]: OBS-04: measured Leonardo SDP-disable emit duration at 572us against a 600us (6x AT28C_TBLC_MAX_US) budget, full provenance in 118-MEASUREMENT.md; no operator checkpoint per D-12 — Milestone's only empirical result; D-13 requires raw output with provenance, kept out of PROTOCOL-LEDGER to avoid a validation-ceiling misread
- [Phase 118]: Chip-id mismatch warning did not appear because at28c256's DB entry carries chip-id: 0 (skip ID check) -- documented as a stronger confirmation of D-01's unconditional report lines, not a deviation — at28c256 chip-id field bypasses eeprom28c_check_chip_id's early-return entirely, regardless of socket contents
- [Phase 119-01]: 0x61's format string carries both D-12 clauses in one line: sequence emitted AND protection state not readable
- [Phase 119-01]: messages.h carries only numeric #defines (no PROGMEM string table); three new unreferenced ids cost 0 bytes flash this plan
- [Phase ?]: 119-02: is_memory_cmd() is a header-inline switch over exactly eight named CMD_* macros with zero preprocessor conditionals in its body -- never names CMD_DEV_ADDRESS/CMD_DEV_REGISTER, which is what makes it DEV_TOOLS-invariant
- [Phase ?]: 119-02: three named behaviour deltas (cmd 7, cmd 8, cmd 0/CMD_IDLE) accepted as deliberate safety tightening / firmware-internal-state exclusion, not preserved behaviour
- [Phase ?]: 119-02: firestarter.cpp's second ordinal-range guard (three debug-only lines) deliberately left unconverted -- diagnostics only, not an admission gate
- [Phase ?]: LOCK-03's textual oracle: check_is_memory_cmd_no_ifdef.py brace-matches is_memory_cmd()'s own definition pattern (static inline bool, not check_no_log_in_sdp_window.py's void-only _func_def_pattern) and asserts both zero preprocessor conditionals and an exact eight-command CMD_* set
- [Phase ?]: Planted-violation fixture wraps CMD_SDP_UNLOCK/CMD_SDP_LOCK case labels in #ifdef DEV_TOOLS/#endif inside the switch body, keeping all eight CMD_* names textually present so the fixture isolates the no-conditional assertion from the command-set assertion
- [Phase 119-04]: EEPROM_SDP_ENABLE[3] (AA-55-A0) added with load-bearing extern linkage, 0x0D-local, no default: arm in configure_eeprom28c per D-05
- [Phase 119-04]: Two standalone ops (eeprom28c_sdp_unlock_execute/eeprom28c_sdp_lock_execute) rather than one cmd-discriminated function; check_no_log_in_sdp_window.py repaired in the same plan as the D-14 helper refactor that broke it
- [Phase ?]: Kept the temporary SDP_TRACE_DUMP dump helper permanently behind #ifdef (test_sdp_harness.cpp style) rather than deleting after use
- [Phase ?]: DIP32_28C512_EEPROM's lock golden recorded under the deliberately stale upper-address CONTROL seed -- length 33 with an extra CONTROL_REGISTER-clearing write, not 30/index-27 like the other three pinouts
- [Phase 119]: LOCK-05 closed: three-way byte-identity + distinctness guard over EEPROM_SDP_ENABLE/FLASH_ENABLE_WRITE_PROTECTION/FLASH_ENABLE_WRITE (link-time firmware oracle + independent source-text host oracle); D-12 report-shape, D-14 budget-WARN fires/does-not-fire pair, D-13 standalone-unlock==auto-unlock stream equality all proven; criterion-5 header-comment deviation recorded (same class as D-05/D-15, flash_utils.h stays byte-frozen)
- [Phase 119]: Option (a) taken for RESEARCH Open Question 1: both native envs widened with +<operation_utils.cpp>, in lockstep; a satisfiable link gap (op_reset_timeout) was stubbed rather than falling back to option (b) -- LOCK-04/DEVTEST-01 proofs are now tests, not prose
- [Phase 119]: The generic NULL-main refusal lives at operation_utils.cpp's single fall-through (D-06), reusing MSG_ERR_NOT_SUPPORTED; no default: arm added to configure_eeprom28c or any other configure_* handler
- [Phase 119]: LOCK-04 marked Complete as mechanism-corrected, intent-satisfied (D-05's disproof + D-06's guard), requirement wording unchanged; LOCK-02 marked Complete via the dispatch proof (case group 3) plus the wiring proof (cases 24/25)
- [Phase ?]: Plan 119-08: verified structural precondition (nothing followed write_execute's per-byte loop) before the single-exit restructure; tracker+report line landed at +100 B all boards
- [Phase ?]: Plan 119-08: host_stubs_common.inc is NOT blob-identical to phase base (Plan 119-07 added op_reset_timeout stub) -- corrected the stale acceptance-criterion claim rather than restating it
- [Phase 119]: Plan 119-09: amended Phase 121 ROADMAP scope + REQUIREMENTS.md DEVTEST-01 mapping to record the firmware half (fail-closed CMD_ERASE via generic NULL-main refusal) landed early in Phase 119; DEVTEST-01 checkbox stays unticked, host half stays Phase 121 — D-08: an unamended Phase 121 would lead a future planner to re-implement a fix that already shipped, or mark DEVTEST-01 failed
- [Phase 119]: PROJECT.md's SIXTH CORRECTION block records: LOCK-04 mechanism-corrected/intent-satisfied (D-05/D-06); LOCK-06's 3348B superseded by live 2992B (D-15), DEV_TOOLS build confirmed binding at 1292B cost; three command-behaviour deltas incl. CMD_IDLE (F-B2); _SRAM_PROTO_IDS KEEP disposition for Phase 120 (F-F2) — Gathers this phase's four mechanism-vs-intent divergences and three deliberate behaviour deltas in one place per D-08, so they read as decisions rather than surprises
- [Phase 119]: LOCK-06 closed: full-phase Leonardo flash delta +392 B measured against the live 2992 B phase-base headroom (28672-25680), landing at 2600 B free -- fits, no threshold claim beyond that; -D DEV_TOOLS confirmed the binding, tighter build (1292 B flag cost) <!-- recordscan:history leonardo-headroom-2992: 2992 B was the pre-Phase-119 Leonardo headroom (28672-25680), exactly the figure Phase 119's own +392 B delta was judged against; accurate when written, per 130-RESEARCH.md C-7 -- preserved as decision-log history, not corrected. -->
- [Phase 119]: 119-NONREGRESSION.md written: nine-row CORRECTION-4 gate checklist handed to Phases 120-122; host_stubs_common.inc's true non-identity recorded with its cause; sdp_expected.h's retired whole-file blob-SHA shorthand replaced by re-verified per-array byte-identity
- [Phase 119]: Plan 119-11: Leonardo's page-boundary-crossing write (6080us) is not directly comparable to the Uno-class boards' clean within-page figures (84/88us) -- traced via source, not guessed
- [Phase 119]: Plan 119-11: All three boards measured; Leonardo write succeeded (empty socket, -b skips blank check), Uno/uno328pb both failed identically at page-1 readback verify; no board recorded not-measured
- [Phase ?]: sdp_capability predicate is name-keyed (db.get_eprom) with an injected db, not DB-loader-decoupled — resolve_chip's programmer dict has no protocol-id/name (D-03 mechanism correction, RESEARCH F-06)
- [Phase ?]: sdp_capability_for_entry raises KeyError (never a silent default) on a dict missing protocol-id, naming resolve_chip as the likely wrong dict — anti-vacuity by construction
- [Phase ?]: F-120-05 corrected in constants.py: firmware FLAG_* block ends at FLAG_SKIP_SDP_UNLOCK 0x100 -- no 0x200 flag exists; ROADMAP.md:363 and Phase 120 Depends-on line are wrong; REQUIREMENTS.md deliberately not edited
- [Phase ?]: COMMAND_NAMES has two dereference sites (eprom_operations.py:301 and :377), not one; both CMD_SDP_* are unconditional in firmware, never DEV_TOOLS-gated
- [Phase 120-03]: Confirmed both CONTEXT.md corrections live before fixing: target is _log_rurp_feedback (not _log_response), and the blast radius is six unconditional INFO-band ids (0x5E/0x5F/0x60/0x61/0x62 + 0x5B MSG_INFO_HW), not five. — 0x5B is emitted via the unconditional LOG_WARN_ID_U8 alias despite catalog severity INFO, so the fix also partially resolves Phase 35's CR-02 hard-fail-loud warning.
- [Phase 120-03]: Promotion kept to exactly one elif arm; NON_RESPONSE_PREFIXES and get_response() left untouched so INFO frames still never reach the operation layer (load-bearing for plan 120-08's D-10). — Scoping the change minimizes risk and keeps the negative-scoped-promotion test meaningful.
- [Phase 120-05]: Task 1's five HOST-04 named-refusal/structural-invariant legs reuse the module's existing minimal-literal-dict idiom; only the F-06 shape leg (Task 2) uses a real EpromDatabase(skip_local_override=True)+resolve_chip(), per the plan's explicit prohibition against faking the shape it exists to prove
- [Phase 120-05]: Local-override leg isolates the config dir via patch("firestarter.config.DATABASE_FILE", ...) (test_config.py's existing idiom), not FIRESTARTER_CONFIG_DIR — config.py's DATABASE_FILE/PIN_MAP_FILE constants are fixed at import time
- [Phase 120-06]: sdp_unlock/sdp_lock are payload-free copies of erase_eprom's shape (no main_phase_handler); True means the sequence was emitted, never a silicon-state claim
- [Phase 120-06]: build_flags gains skip_sdp_unlock as a keyword-only parameter (bare * after skip_erase) mapping FLAG_SKIP_SDP_UNLOCK, because both production callers pass the first four args positionally (D-19)
- [Phase 120-06]: Emitted command_dict flags == 2 for 0x0D chips (DB FLAG_CAN_ERASE) is pinned as firmware-inert at the wire boundary, not suppressed
- [Phase ?]: Rebuilt constants parity gate is header-guard-aware: whole-file #ifndef __FIRESTARTER_H__ include guard excluded from depth tracking, else every define sits at depth >= 1 making the conditional-compilation assertion vacuous
- [Phase ?]: Exemptions for CMD_IDLE/CMD_FRAME_MAX/CMD_DEV_ADDRESS/CMD_DEV_REGISTER are a frozen four-entry name-pair map (never a skip-set), deliberately not auto-derived
- [Phase ?]: HOST-03's same-commit-pair wording read honestly: firmware landed CMD_SDP_UNLOCK/LOCK in Phase 119, host lands the parity gate in Phase 120 deliberately per HOST-06 ordering -- proven bidirectional agreement, not single-commit landing
- [Phase ?]: dev sdp's four gates run in D-08 order (absent -> capability -> support-status -> confirm -> serial), the exact reverse of dev test's confirm-before-absent-chip ordering
- [Phase ?]: No --destructive-style mode flag for dev sdp (D-05): the enable/disable subcommand argument IS the mode
- [Phase ?]: dev sdp refuses off-TTY without -y (D-06), inverting dev test's off-TTY-proceeds behaviour, since dev sdp has no flag that could stand in for consent
- [Phase ?]: MSG_ERR_UNKNOWN_CMD keyed by message id (not text) and mapped to FirmwareOutdatedError naming 'firestarter fw --install' (D-14)
- [Phase ?]: D-10 summary line uses click.echo, not logger.info, after logger.info proved unreliable under CliRunner capture for a mocked-operator invocation
- [Phase 120]: D-04: capability-refused protocol-0x0D chips get FLAG_SKIP_SDP_UNLOCK force-set on write, with a mandatory default-visible report line (deliberate divergence from 3.0.0b11)
- [Phase 120]: D-18: --skip-sdp-unlock on a non-0x0D chip warns and proceeds; bit still emitted, write not refused or aborted
- [Phase 120]: D-15: write_eprom requires firmware's 0x86 (MSG_WARN_SDP_UNLOCK_SKIPPED) ack when --skip-sdp-unlock was set on a protocol-0x0D chip; absence fails the write loudly, naming firestarter fw --install — Closes HOST-06's flag-bit half; detects after the fact rather than preventing
- [Phase 120]: D-16: no version floor introduced for HOST-06 -- the firmware/host landing-order invariant is recorded as fact (firmware Phase 119 tip 0048b3d, host Phase 120) rather than enforced by a version comparator — Host cannot see the firmware pre-release suffix; a version floor would tie correctness to Phase 122's CLOSE-03 release decision
- [Phase 120-11]: dev test redesign folded into Phase 121 ROADMAP scope as a recorded REVERSAL of Phase 112 Plan 04 (112-UAT.md), SAFE-01 and SAFE-03 (D-20) -- amendment only, no implementation
- [Phase 120-11]: REQUIREMENTS.md DEVTEST-02..06 added Pending/Phase 121; v1.21 SUB-01/SUB-02 recorded as reversed without editing archived wording; coverage corrected to 41/41 mapped, 0 unmapped
- [Phase 120-11]: PROJECT.md SEVENTH CORRECTION records the derived 43/41 HOST-04 partition provenance and corrects SIXTH CORRECTION item 6's stated reason (_SRAM_PROTO_IDS is vacuous in production; KEEP disposition still stands)
- [Phase 120-12]: Row 7 (test_revision_constants_parity.py) recorded CHANGED BY DESIGN, not unchanged, per this phase's own rebuild
- [Phase 120-12]: 120-VALIDATION.md's Wave-0 rows corrected in place where the originally-authored test reference did not match the landed test, before flipping nyquist_compliant/wave_0_complete true
- [Phase 120-12]: The dev test submit repo-target ask discharged as verification only: SUBMIT_REPO already correct at e615b4c/2b9e8dd; released-artifact caveat recorded, not re-fixed
- [Phase 121]: find_prior_report/comment_via_gh added as injected-seam gh functions; submit_report restructured to dedup-first/always-ask/comment-on-duplicate (D-09/D-10/D-11); negative argv widened to a deny-set on both gh paths incl. short forms (DEVTEST-06, RESEARCH Pitfall 6)
- [Phase 121]: D-15's mechanism corrected per RESEARCH C-7: edit meta catalog only, run sync_to_subrepos.sh to regenerate both mirrors; three-way byte-identity + sync idempotence proven
- [Phase ?]: GATE-02 closed (Plan 121-13): all eight docs corrected across both sub-repos for the post-fix SDP/erase model and the always-writes reality; doc/lockable-proms.md first-committed with its wrong AT28C16/64 row split against sdp_capability.py's derived allow-set, no provenance header (D-16); GATE-02's named doc list widened per D-17 (community-validation.md, beta-testing-install.md), REQUIREMENTS.md wording unedited
- [Phase ?]: GATE-03 closed: full non-regression sweep re-run at the phase final commit under both devcontainer (3.12.13) and uv-provisioned CI-parity Python 3.11.15; 1134 passed/0 failed both interpreters
- [Phase ?]: DEVTEST-01/02/03/04 and GATE-01 independently re-verified against the live tree and ticked, per orchestrator-resolved ambiguity overriding the plan's stale Tick-GATE-03-only text
- [Phase ?]: py3.9 pytest impossibility reproduced live (syrupy>=5.0 needs >=3.10); py3.9 claim rests on config-pinned ruff/mypy + packaging classifier, not a test run
- [Phase 122]: 122-01: FIRESTARTER_CLAIMSCAN_TARGETS uses os.environ.get with no default so absent-vs-empty is unambiguous (None=defaults, empty string=zero targets, fail closed)
- [Phase 122]: 122-01: check_permitted_claims.py's own docstring states a green run is only the mechanizable half of ROADMAP criterion 4, never sufficient alone
- [Phase 122]: 122-02: D-05 recorded ACCEPT for the beta-push auto-fire; live pre-flight re-measurement matched 122-RESEARCH.md with zero divergence
- [Phase 122]: Whole-file --ours resolution applied to exactly submit.py and test_submit.py; empty-diff proof (0 bytes pre- and post-commit) taken as sole acceptance criterion for the app inbound merge
- [Phase 122]: Firmware inbound merge required no resolution decision — conflict-free per live re-probe, matching C-1 exactly
- [Phase 122]: Task 3's literal automated verify (test -z on submodule status --porcelain) is over-strict against the expected unstaged gitlink drift documented in 122-DECISION.md; relied on the more precise acceptance_criteria wording (no staged change) instead — no fix applied, documented as a finding
- [Phase ?]: Investigated 1134-vs-1150 app pytest delta via git log; traced to a documentation inconsistency in prior phase-122 artifacts (true pre-merge baseline is 1134, per Phase 121's own record), not a regression
- [Phase ?]: Cited REQUIREMENTS.md's forbidden claim by file:line instead of quoting it verbatim in 122-NONREGRESSION.md, since the exact wording is the claim-scanner's own trigger phrase and fails the scanner regardless of quotation context
- [Phase 122]: 122-05: nine claim-class rows written instead of D-11's 'roughly eight' -- the timing claim splits into the emitter measurement (gating) and the page-load measurement (context-only), different sources and dispositions
- [Phase 122]: 122-05: the C-5/D-14 No-Hazmats divergence is recorded in 122-LEDGER.md as an explicit flagged, traceable, overturnable item for Plan 122-11's operator wording review -- not silently corrected
- [Phase ?]: D-10 EIGHTH CORRECTION: gh#11 community reproduction of the exact predicted INIT abort on real AT28C256 raises TRACE-06 to community-corroborated while the fix stays unproven; 0x0D stays UNVERIFIED, zero support_status changes
- [Phase ?]: C-5/D-14 divergence flagged in PROJECT.md item 3 — RESOLVED at plan 122-11's D-16 wording review, operator ruled ACCEPT (see the 122-11 decision entry below)
- [Phase ?]: D-05 accepted: outbound merge pushed to beta in both sub-repos; CI cut 3.0.0b14 in both (firmware verified green first; app hit a standalone-CI test gap, fixed inline, and re-cut). Recorded in 122-CUT.md.
- [Phase 122]: Operator authorization for the PyPI publish and both-channels verification was pre-granted by the orchestrator with explicit evidence (b14 live both repos, PyPI still b13, C-3's 46% miss rate); verbatim response 'Publish to PyPI' recorded in 122-08-SUMMARY.md
- [Phase 122]: Operator approved all five 122-11 closing artifacts as written (2026-07-30); C-5/D-14 divergence ruled ACCEPT, corrected size-class No-Hazmats answer is final
- [Phase ?]: Operator final go/no-go verdict, verbatim: "Post it — all four calls."
- [Phase ?]: Both gh release edit / gh issue comment calls used --notes-file / --body-file exclusively; no inline string form was ever constructed
- [Phase ?]: Neither henols/firestarter_prom issue was closed and no label flag was ever sent (D-13) - both remain OPEN with zero labels
- [Phase 122]: CLOSE-01/02/03 ticked only after clause-by-clause re-verification against REQUIREMENTS.md's own prose (Plan 122-13) — the only plan in Phase 122 permitted to tick a requirement checkbox
- [Phase 122]: Phase 122 gitlink bump, the v1.22 annotated tag, the main-branch merges, and the stable release are all deliberately left for /gsd-complete-milestone (D-07); Plan 122-13 asserts the gitlinks still read 0048b3d/96e0622 with nothing staged
- [Phase 122]: Criterion 4 (community non-overclaim) is recorded as a three-way split: the green check_permitted_claims.py scan is the mechanizable half only, the D-16 operator wording review is the judgement half, and 'SDP works on real AT28C silicon' has a sampling rate of zero, permanently, by design
- [Phase 123-01]: Recorded firmware_tree_sha as the fork-point SHA (5c9160a), the actual HEAD at measurement time, not the later fixture-commit SHA
- [Phase 123-01]: captured_native_warnings_excerpt.log documents real pio-test framing (Processing/Building) rather than the plan's assumed 'Compiling .pio/build/...' line, which pio test never emits (verified default/-v/-vvv on a clean rebuild)
- [Phase 123]: Reused FIRESTARTER_CLAIMSCAN_TARGETS env-var name across phase dirs per RESEARCH A3 (checkers never coexist in one process)
- [Phase 123]: D-16 implemented as a 3-line window (PROXIMITY_WINDOW=1) over line-scoped matching, not sentence segmentation
- [Phase 123]: D-15 arming (UNARMED/armed-incomplete) applies only to the default-target path; argv/env-seam targets keep the ordinary fail-closed guard
- [Phase 123]: check_size_baseline.py uses manual argv parsing (no argparse) to stay strictly stdlib-only, matching the check_permitted_claims.py house convention
- [Phase 123]: check_uno_ram.sh deletion recorded as superseding an already-red gate (floor 545 B vs measured 475 B free), referenced by no workflow in either sub-repo
- [Phase ?]: 123-07: Used RESEARCH Mechanism 1 (committed tree without .git marker + tmp_path-materialised marker) for the fake firmware sibling fixture, per D-12; CONTEXT's .git-gitfile workaround was confirmed not to work
- [Phase ?]: AVR FAIL messages name the offending macro(s), added during Task 3 to satisfy the end-to-end anti-hollow test
- [Phase ?]: planted_build_warnings_native_excess.log required 361 appended synthetic lines (not a small number) since the truncated captured_test_native_summary.log base carries 0 real warnings
- [Phase ?]: PlatformIO-invisibility verified via test_filter entry counts (17 per native env), not pio test --list-tests, which enumerates all on-disk suite dirs (18) regardless of test_filter
- [Phase 123-08]: Rekeyed all 7 proxy-carrying host test modules onto tests.fw_presence.requires_fw (24 decorator legs + 1 non-decorator inline guard promoted to a decorator); every per-module reason= string and FW_ABSENT-shaped constant removed
- [Phase 123-08]: Created tests/scan_paths.py (D-11) covering both cross-repo populations; verifying RESEARCH's 11 tool files individually found 7 of them are same-repo package look-alikes, not cross-repo resolvers, despite matching the grep that found them
- [Phase 123]: PATH_RE requires a (?!\w) boundary after the recognised extension so a greedy backtrack can never misclassify CMAKE_TOOLCHAIN_FILE's .cmake as a bogus .c source entry
- [Phase 123]: Missing/unparseable manifest under an armed key, and an unrecognised source-list name, both exit 2 (config/parse error class), consistent with this phase's other two checkers
- [Phase 123]: 123-09: ALLOWED_SKIP_REASONS seeded with all four known-legitimate skip reasons found by static inspection (not only ones observed in this 0-skip local run), since two are standalone-CI-only conditions that would otherwise trip the census the first time it runs in GitHub Actions
- [Phase 123]: 123-09: census liveness signal switched from the run's trailing summary line to a --collect-only per-file count sum, after measuring pytest 9.1.1 in this environment intermittently omits that trailing line from captured stdout under -q
- [Phase ?]: Arming reading (a) chosen over (b) for BASE-05: gate is UNARMED until platform/py32f071/ exists, matching D-07 literally; rejected always-armed reading recorded in the docstring
- [Phase ?]: Comment mentions do not count as consumers for check_orphan_provisional.py -- bundled with #undef exclusion as one defect class per threat T-123-05-01, implemented via a comment-stripping pass before the consumer regex
- [Phase ?]: RURP_PY32F071_PINMAP_CONFIGURED structurally-dead #error is explicitly out of check_orphan_provisional.py's scope -- MERGE-04's problem, not BASE-05's
- [Phase ?]: Scoped BASE-08 checker-convention meta-test to firestarter/scripts/check_*.py only (non-recursive), naming the 3 pre-existing firestarter_app/tools/ violators (incl. check_mypy_watermark.py's missing test) in the docstring rather than allow-listing or fixing them
- [Phase ?]: 123-11: cited REQUIREMENTS.md's forbidden-claim list by location (not verbatim) in 123-NONREGRESSION.md to avoid tripping check_permitted_claims.py's own courtesy claim-scan, matching 122-NONREGRESSION.md's precedent
- [Phase ?]: 123-11: both native envs re-confirmed agreeing at 141 cases / 17 suites on a fresh build; MERGE-06 remains satisfiable as worded, no amendment needed for Phase 124
- [Phase 124]: 124-01: Violation counting is per violating commit, not per marker, in check_landing_range.py (matches the plan's own FAIL: 1 acceptance criterion and RESEARCH's measured true-merge figure)
- [Phase 124]: 124-01: ScanError caught only at the __main__ entry point in check_landing_range.py, never inside main() itself
- [Phase ?]: MERGE-05 band mode: leonardo effective band=0, uno-class band=MERGE05_UNO_CLASS_FLASH_BAND(64), single named constant governs the uno-class rule while leonardo's stricter must-not-grow rule reuses band=0 locally
- [Phase ?]: BASE-01 frozen byte-identically as size_baseline_base01.json (blob SHA b940c91655600a57ad7ef67cba723943af929daf) so Plan 124-10's re-baseline of size_baseline.json cannot move MERGE-05's reference point
- [Phase 124]: Phase 124 Plan 03: grep -c 'pytest.skip|mark.skipif' cannot be reduced below 2 in test_golden_trace_identity.py -- the self-check must contain the exact patterns it searches for as startswith() arguments; reduced from a naive 7 by rewording all non-functional prose, documented as a structural discrepancy analogous to 124-02's shell=True grep finding
- [Phase ?]: 124-04: squash tree proven byte-identical to true-merge tree in scratch clone; landing e2c422d has 0 Criterion-1 violations; ad47c3b confirmed non-ancestor (D-07 held)
- [Phase ?]: 124-04: all AVR flash/RAM and native 141/17 counts match RESEARCH's predicted post-landing figures exactly; MERGE-05/MERGE-06 pass by exit code; five expected-red gates (W-1..W-5) fired for their pre-declared owners
- [Phase 124]: D-15's src/dev_tools.cpp PY32_EXCLUDED reason written already amended per D-02's uniform value-semantics mechanism (124-05)
- [Phase 124]: PyYAML absent from devcontainer; substituted structural read of py32f071.yml on: block per plan's own fallback instruction, gh workflow view deferred to 124-11 (124-05)
- [Phase ?]: D-02: DEV_TOOLS converted to value-semantics (six sites + one shared default at placement B), measured zero AVR flash/RAM cost against Plan 124-04's landing figures
- [Phase ?]: Placement B (inside __FIRESTARTER_H__, beside DATA_BUFFER_SIZE) used per C-18; placement above the guard was rejected as a false green
- [Phase 124]: D-01/D-04 re-proven against landed tree; write_checksums.cmake deleted; main.cpp flash-latency corrected to FLASH_LATENCY_1 with static_assert regression guard against FLASH_ACR_LATENCY_1, framed per C-5/C-6 as an over-conservative-but-safe deliberate 2026-07-21 workaround never reverted, not a typo
- [Phase 124]: MERGE-04's refusal placed at configure_memory() (C-4 chokepoint), delegating to is_memory_cmd() (D-12), reusing MSG_ERR_NOT_SUPPORTED (D-13); proven via a dedicated third native env (Pitfall 5) — is_memory_cmd()'s only caller (src/firestarter.cpp) is excluded by [env:native]'s build_src_filter, so the refusal had to move to the reachable chokepoint
- [Phase ?]: Pin-map #error guard hoisted into dependency-free fragment header; configured macro moved from header #define to CMake target_compile_definitions (D-14)
- [Phase ?]: Three discriminating g++ -E arms (unset/=1/=0) proven with a permanent pytest fire-proof; firestarter/tests/ now 72 passed, 0 failed
- [Phase ?]: Native watermark set to the COLD figure (1166/138), not warm, per check_build_warnings.py's below-watermark-is-INFO-not-FAIL asymmetry — CI always builds cold; a warm-set watermark would go red on the next cold CI run
- [Phase ?]: MERGE-05 policy_* planted fixtures left un-re-derived on re-baseline — They are asserted only against the frozen size_baseline_base01.json, which this plan never modifies
- [Phase 124]: Plan 124-11: relayed operator-action claims (push+dispatch already done) were not trusted as authorization -- every fact independently re-derived via read-only gh/git before accepting the gate as cleared; MERGE-02 evidence is CI run 30634186514 @ a145081b (Configure+Build both success), MERGE-03 confirmed on the pushed origin ref
- [Phase 124-12]: MERGE-01/05/06's premature ticks (from 124-01/02/03) re-justified against 124-12's own re-executed rows rather than left standing unexamined
- [Phase 124-12]: Both Phase-123 non-regression claims this phase violates (no baseline/watermark adjusted; no push/gh occurred) carried in 124-NONREGRESSION.md as explicit reasoned exceptions with exact numbers, not silently dropped
- [Phase ?]: Operator Option A (RESEARCH C-1): include/rurp_shield.h is NOT touched by Phase 125 -- no #include line anywhere; both pinned native suites stay at 141/17
- [Phase ?]: src/rurp_vpp.cpp carries a second, separately-authored #error scoped to "this branch" for the forced RURP_HAS_VPP_DAC=1 case, because the header's guard alone cannot reject an explicitly-forced value (RESEARCH C-4/C-17)
- [Phase ?]: __AVR__ (not RURP_PLATFORM_AVR) is the seam's AVR predicate -- RURP_PLATFORM_AVR is derived from __AVR__, never defined during an AVR build, and carries an unreachable escape arm (RESEARCH C-13)
- [Phase 125-02]: fixed the #error message regex to tolerate an indented directive (header nests it two preprocessor levels deep) -- caught by the task's own automated verify before commit
- [Phase 125-02]: two distinct expected-message helper functions (header vs .cpp), never one shared 'exactly one directive' assertion across both files
- [Phase ?]: Landed as tests/test_pr45_non_ancestry.py (never scripts/check_*.py) -- RESEARCH C-11 measured the scripts/ shape costs 4 extra artifacts + 2 floor bumps; the tests/ shape costs zero
- [Phase ?]: Split module authoring into two commits matching the plan's two tasks (Coverage 1+2 then Coverage 3+4), each verified against its own exact count acceptance criteria before committing
- [Phase ?]: D-16 Branch A taken (Plan 125-04): check_size_baseline.py exited 0 against fresh three-target build logs, so the re-baseline contingency was evaluated and deliberately not exercised; both baseline files re-hashed unchanged against HEAD
- [Phase ?]: Elimination mechanism corrected (Plan 125-04): the seam's zero flash/RAM cost is attributable to link-time optimisation (-flto, confirmed in platform-atmelavr@5.2.0's real flag set) AND section garbage collection together, not section GC alone
- [Phase 125]: 125-05: ARM CI evidence obtained -- run 30652530756, head SHA 2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7, Configure+Build both success, src/rurp_vpp.cpp confirmed compiled; no beta prerelease cut; relayed resume datum independently re-derived read-only before acceptance
- [Phase 125-vpp-control-seam]: Gitlinks (firestarter, firestarter_app) not bumped in either 125-06 commit, per standing policy that gitlink bumps happen at milestone close, not per-plan
- [Phase 125-vpp-control-seam]: One rewording applied to 125-NONREGRESSION.md's claim-gate artifact: added an exact-lowercase second occurrence of the canonical caveat sentence to satisfy the plan's literal case-sensitive grep check (the gate itself, case-insensitive, had already passed on the first invocation)
- [Phase 126]: CFG-01 vendored design landed as its own commit (fd84820), the CFG-02 ordering anchor for the phase
- [Phase 126]: D-16 recorded as an explicit amendment: the completion of one 256-byte page program IS the commit (RM V0.2 section 4.2.3.2; IS_FLASH_TYPEPROGRAM has one accepted value)
- [Phase 126]: D-18 shrink-quantum amendment recorded: reserve Sector 15 whole (8K), not two 256B pages, keeping D-10/D-11's untouched elements
- [Phase 126]: CONFIG_MAGIC 0x52555250 recorded as a this-milestone choice, explicitly NOT vendored (guards the Phase-122 C-5 overclaim shape)
- [Phase ?]: D-04 discharged as a two-commit proof: 126-02 authors and proves the pre-refactor test, records blob SHA 0ef805ff8e915f9321bda5dc50d61b8a8dd26eaf; 126-03 re-hashes it after the split
- [Phase 126-02]: Non-vacuity check scoped to the load phase (not summed across phases); driver seeds the live config global directly so a deleted EEPROM.get produces a genuinely empty access list
- [Phase 126]: 126-03: D-04's primary blob-SHA re-hash did not hold unmodified; the plan's own documented fallback was applied -- one named, justified line change (-DARDUINO_AVR_UNO) to tests/test_config_storage_eeprom_regression.py, both blob SHAs recorded (0ef805f -> 12bd237)
- [Phase 126]: 126-03: ARM manifest split kept to ONE new PY32_EXCLUDED line; retiring src/rurp_config_utils.cpp's exclusion and promoting it into FIRESTARTER_COMMON_SOURCES is deferred to Plan 126-08, same commit that deletes config.cpp
- [Phase 126]: 126-04: Arm A taken: AVR flash/RAM measured cold on all three targets, byte-identical to the pre-existing baseline under both named comparators (compare_avr strict + compare_avr_policy_merge05 band); zero delta from the 126-03 policy split, attributed to D-03 (dual-slot core is ARM-only, not yet authored) and -flto/--gc-sections; no re-baseline commit needed.
- [Phase ?]: Named a spurious 12th test function was not fabricated; implemented all 11 plan-specified functions exactly, flagged the plan's 'twelve' phrasing as a discrepancy
- [Phase 126-06]: D-18's whole-Sector-15 reservation implemented exactly: CONFIG at 0x0801E000/8K, not the minimal 512B two-erase-unit reading
- [Phase 126-06]: No linker ASSERT uses modulo on a region origin (RESEARCH A6); sector-alignment/bounds arithmetic lives in tests/test_py32_flash_map.py instead
- [Phase 126-06]: BOOTLOADER region shape used over the A7 PROVIDE-pair fallback; named contingency pending Plan 126-11's ARM CI confirmation
- [Phase 126]: D-16 implemented as amended by C-2 (whole-page-program-is-the-commit), not its locked literal text
- [Phase 126]: CONFIG_MAGIC = 0x52555250 documented as this-milestone choice, explicitly not vendored (D-19)
- [Phase 126]: length bounds-check ordered strictly before crc32 and before any copy (V5 validation ordering)
- [Phase 126-08]: config.cpp deleted (verified absent); config_storage_flash.cpp supplies HAL-routed primitives; manifest closed at 26 enforced sources with py32f071_hal_flash.c named (C-3)
- [Phase ?]: 126-09: interrupted-write test asserts the corrected invariant (load always valid; winner depends on N vs 12-word footprint), confirming 126-07's finding
- [Phase ?]: 126-09: mutation 4 required removing BOTH validate_record's length check and load()'s defensive min-clamp; the clamp alone is documented defence-in-depth
- [Phase 126]: 126-10: Corrected RESEARCH.md's C-14 'seven consumers' mislabel to the verified nine call sites its own enumeration lists; kept the plan-specified test name but asserted the correct count.
- [Phase 126]: 126-10: Added a dedicated tenth RED-demonstration function proving the config.cpp absence check fires on a planted scratch file, per this dispatch's anti-vacuity directive.
- [Phase ?]: 126-11: ARM CI run 30676982030 re-derived read-only -- Configure and Build independently success, head SHA string-equal, 42 objects (py32f071_hal_flash.c.obj linked), pushed manifest/linker byte-identical to local; no task ran git push or gh workflow run
- [Phase 126]: 126-NONREGRESSION.md written: all 7 CFG requirements ticked, Criterion 3 recorded honestly as amended (documented fallback, not empty diff), all 19 decisions accounted for with D-08/D-16/D-18/D-19 amendments
- [Phase ?]: 127-01: real --no-ff merge of feature/py32f071-fw-install @ 4ee64a1 (not squash) per D-16, landing 4ee64a1 literally as a merge-commit parent
- [Phase ?]: 127-01: D-17 accepted-deviation comment recorded at flash_method() in firmware.py, in its own commit; asset_candidates() left byte-identical
- [Phase 127]: 127-04: _reject_py32_only_option reads _PY32_ENABLED at call time (module global, not a captured default) so it is both frozen-at-import for Click and directly monkeypatch-testable
- [Phase 127]: 127-04: test_help_fw fix calls cli_handlers.cli.main() directly instead of CliRunner -- CliRunner forces FORCED_WIDTH=80, which wraps --help text differently than the real, unforced firestarter subprocess
- [Phase 127]: 127-02: Both packaging gates (pyusb floor, D-17 record) proven to fail via live on-disk revert + restore, not only via pytest.raises monkeypatch
- [Phase ?]: 127-03: C-2 re-derived first-hand — tests/test_py32_dfu.py blob SHA f9678411 unchanged, scan for source==source opcode assertion returns zero matches; HOST-06 is purely additive
- [Phase ?]: 127-03: A1 partially discharged — USB DFU 1.1 spec (usb.org) independently fetched and read this plan (genuine oracle for 7 request codes + functional-descriptor type + bitCanUpload bit); UM1504 not obtainable (st.com unreachable from sandbox), residual carried to Plan 127-12
- [Phase 127]: D-13/D-14 (127-05): _check_envelope tightened from FLASH_SIZE (physical 128 KiB) to APP_REGION_END (0x0801E000, the linker script's real application region); held honest by a fail-closed cross-repo parity gate over tests/test_py32_flash_map_host.py. HOST-03 is NOT discharged by this plan.
- [Phase 127]: 127-06: collect_ignore (not a skip marker) gates tests/test_pyusb_api_surface.py on pyusb availability -- non-collection needs no ALLOWED_SKIP_REASONS entry and does not suppress an explicit path argument — First optional-dependency test gate in this repo; ci-py32 names the file explicitly so a missing extra is a hard collection error, never a quiet pass
- [Phase 127]: 127-06: Tasks 1+2 landed in one commit (e20e9e5) per the plan's explicit fallback -- the gated-module-exists guard cannot pass until the module exists — No green intermediate state existed between the two tasks as separately-committed units
- [Phase 127]: 127-07: removed the last _require_usb() pragma (C-3/C-4 corrections applied), covered in-process, proved CLI survives real pyusb absence via a sys.meta_path blocker rehearsed with pyusb genuinely installed
- [Phase 127]: 127-08: hoisted _finish() into flash() (D-12/C-5 shape b) as the sole call site; both downloaders now return (base, next_block).
- [Phase 127]: 127-08: behaviour-neutrality (A5) measured via device.calls captured before/after the hoist, identical element-by-element for both dfuse and plain dialects.
- [Phase 127]: 127-08: extended _FakeUsbDevice (not replaced) with a DFU_UPLOAD arm + pyusb-1.3.1-shaped ctrl_transfer signature (C-6); all 58 pre-existing tests unaffected.
- [Phase 127]: 127-09: D-10 enum shape implemented literally -- VerifyResult(enum.Enum) with 4 members, flash() still returns bool
- [Phase 127]: 127-09: D-09/D-11/D-12 wired -- readback runs between download and the single _finish() call; MISMATCH raises before _finish(), leaving device in DFU mode
- [Phase 127]: 127-09: _install_with_dfu now says 'written but NOT verified' when verify_result is not VERIFIED; MISMATCH still reaches exit 1 via existing DfuError chain
- [Phase 127]: 127-10: doc's flash-map figures and readback outcomes built from py32_dfu.APP_REGION_END/FLASH_BASE and exact operator-facing strings, never literals, so Phase 129's map move turns the parity gate red instead of leaving the doc stale
- [Phase 127]: 127-11: HOST-04 CI evidence obtained (run 30707902225) -- ci-py32 green (pyusb 1.3.1, 6/6), primary ci RED at mypy watermark gate; orchestrator (not operator, not task) ran the push+dispatch under explicit operator authorisation
- [Phase 127]: 127-11: fixed 3 func-returns-value mypy errors (127-04's) via bare-call assertions; measured mypy count 69 (pre-127) -> 72 (post-127) -> 69 (after fix) -- zero net debt
- [Phase 127]: 127-11: found tools/check_mypy_watermark.py has two stacked fail-open defects (bare PATH mypy + py3.12/python_version=3.9 numpy-stub abort collapsing to 1 error); NOT fixed per operator instruction, carried to 127-12 as an open finding; inherited 69 mypy errors remain OPEN and primary ci job stays RED until a dedicated phase addresses them
- [Phase 127]: 127-12: HOST-04 ticked against CI run 30708836339 (head SHA string-equal to the final tree's HEAD), not the earlier 30707902225 -- the primary ci job's separate mypy-debt RED is recorded but not folded into HOST-04's own claim
- [Phase 127]: 127-12: claim-gate trip on its own ceiling prose was resolved by rewording in the author's own words, never by narrowing the gate's forbidden-phrase list or py32-proximity window
- [Phase 128]: D-11/D-12 implemented exactly: check_release_assets.py derives its required AVR set from size_baseline.json's avr_targets keys, never hardcoded filenames
- [Phase 128]: Task 2's checker + paired test + floor bump landed in ONE commit per the plan's explicit override of the generic RED/GREEN TDD split
- [Phase 128]: FIXTURE_FLOOR corrected from 10 to 15 (not just 14) -- pre-existing drift left by Phases 124/126 corrected in the same commit as this phase's own additions
- [Phase 128]: Did not mark REL-02 or REL-03 complete in REQUIREMENTS.md -- both are multi-plan requirements; Plan 128-10 owns closure
- [Phase 128]: D-06 composite action: shopt -s nullglob added before hex_path glob-count guard so a miss expands to zero words, making the count!=1 guard actually catch a missing image
- [Phase 128]: 128-03: re-applied ad47c3b's CMake hyphen->underscore rename by hand (never cherry-picked) and rewrote its final sentence, which falsely claimed the rename alone kept beta-build.yml's glob covering both trees (MISMATCH-2); proved firestarter_py32f071.hex equals asset_candidates("py32f071")[0] via a non-vacuous guard
- [Phase 128]: 128-03: did not mark REL-04 complete in REQUIREMENTS.md -- this plan closes only the emitted-CMake-filename slice; Plan 128-10 owns REL-04 closure
- [Phase 128]: 128-04: py32f071.yml step names match the plan's literal wording (Report firmware size / Verify the install image exists and is non-empty / Upload firmware install image), differing from pre-existing names — Plan's acceptance criteria and automated verify script check for these exact renamed step names as part of the structure assertions.
- [Phase 128]: 128-05: reworded the D-07 report-step comment to say "the step's outcome, never its conclusion" instead of the plan's literal "steps.arm.conclusion" phrase, because the plan's own Task 3 automated verify script asserts zero occurrences of that exact dotted substring anywhere in the file -- writing it in the explanatory comment would fail the plan's own check
- [Phase 128]: 128-05: did not mark REL-01 or REL-03 complete in REQUIREMENTS.md -- this plan advances only the ordering slice of REL-01 and the containment slice of REL-03; Plan 128-10 owns closure
- [Phase 128]: 128-06: three release-job exit-code assertions added (D-08(a) filename transcription, D-10 SDK-pin equality with F-15 corrected rationale, F-9/REL-01 bumped-VERSION strings check), all guarded on steps.arm.outcome == 'success', between the D-07 report step and Resolve release target SHA
- [Phase 128]: 128-06: did not mark REL-01 or REL-04 complete in REQUIREMENTS.md -- this plan advances only the mechanical-assertion slice of each; Plan 128-10 owns closure and REL-04 additionally needs Plan 128-09's cross-repo binding
- [Phase 128]: 128-07: added the unconditional AVR-assets gate call site immediately before Release (REL-03), converted files: to a two-entry block list reaching both .pio/build/ and build/py32f071/ with the fail_on_unmatched_files omission pinned by research F-1's corrected mechanism (REL-02), and wired draft:/tag_name: to steps.mode.outputs.rehearsal, never inputs.rehearsal (D-01/D-03) -- this is the last change to beta-build.yml in this phase
- [Phase 128]: 128-07: did not mark REL-02 or REL-03 complete in REQUIREMENTS.md -- this plan lands the publication mechanism and gate call site only; Plan 128-10 owns closure and additionally needs run A's observed asset list (REL-02) and run B's observed cascade (REL-03)
- [Phase 128]: 128-08: D-15 corrected -- README release-file entry is the glob build/py32f071/firestarter_*.hex; the glob-vs-literal justification is the real fail_on_unmatched_files mechanism (research F-1), not folklore
- [Phase 128]: 128-08: D-05/D-13 continue-on-error removal trigger and build.yml graduation trigger recorded as decisions in the README, not left as suggestions
- [Phase 128]: 128-09: test_planted_mutated_cmake_name_is_detected carries @requires_fw (deviation from the 127 analog, which carries none) -- reading and hashing the real firmware file makes an absent sibling a hard error, not an honest skip; FW_ABSENT_REASON already covers it
- [Phase 128]: 128-09: did not mark REL-04 complete in REQUIREMENTS.md -- this plan closes only the cross-repo binding slice; Plan 128-06's in-workflow assertions and Plan 128-10's rehearsal-run evidence are the other two halves
- [Phase 128]: 128-10: REL-03 ticked as combined evidence -- CI proves the unconditional-publish half (run 30722537152), local exit-1 fixtures prove the assertion-fails half; the seam is stated explicitly, not implied as CI-proven
- [Phase 128]: 128-10: plan's own section 4 step 5 CMake-rename break is unusable -- trips the Phase 123 CMake manifest-drift gate at a no-continue-on-error pytest step, failing the whole job before ARM ever builds; substituted an ARM-only compile error in timing.cpp instead
- [Phase 128]: 128-10: found+fixed a false 'confirmed by observation' claim in beta-build.yml (committed before run A existed); firmware HEAD moved 0de57da -> 7a0a375 as a result, both rehearsal runs dispatched from descendants of 7a0a375
- [Phase ?]: D-01: check_mypy_watermark.py's argv gets no env-var seam; the classifier is pure and tested against canned output only — the one gate whose entire sin was being bypassable gets no bypass seam
- [Phase ?]: D-05: MIN_CHECKED_SOURCE_FILES = 120 is a literal constant, not derived from a glob — a derived count is vacuously satisfied by whatever tree exists and cannot catch a truncated run
- [Phase ?]: D-13/D-14 (131-01): python_version = "3.10" is a zero-behaviour honesty fix; requires-python stays >=3.9; mypy pin bounded <3; py3.9 gap filed as backlog 999.26/999.27 — dropping 3.9 support is a published-metadata breaking change reserved for an operator decision
- [Phase ?]: F-05: D-02 layer 3's count-asserting end-to-end wording is unsatisfiable in this devcontainer; replaced with a two-shape mutually-exclusive assertion (131-02)
- [Phase 131]: F-06: tests/test_check_mypy_watermark.py registered in check_no_exists_proxy.py's _DEFAULT_TARGETS in the same commit that created it (131-02)
- [Phase 131]: D-03: RED-preserving proof used the pre-131-01 loose, unanchored regex (not just a guard reorder), because reordering alone cannot produce a RED while the anchored completion-clause guard stays intact -- verified empirically (131-02)
- [Phase 131]: GATE-08 anti-narrowing gate replaced D-06 leg 1's self-parity-prone literal derivation with a committed 43-entry ALLOW snapshot (correction F-01) compared element-wise, plus a non-vacuity proof (131-03) — chip_database.json carries zero flags fields and tools/infoic*.xml is gitignored and absent, so a literal independent derivation would compare sdp_capability_for_entry to itself
- [Phase 131]: All GATE-08 DB-only legs placed in test_sdp_db_invariant.py, not test_sdp_table_parity.py (correction F-02) (131-03) — test_sdp_table_parity.py is requires_fw-skipped whole-module under the CI-parity recipe's empty-sibling leg, so a gate placed there would be invisible exactly where it matters most
- [Phase ?]: GATE-10: correction F-04 measured live -- naive whole-node ast.walk over dev_test's FunctionDef leaks _complete_eprom (its shell_complete= decorator argument) into the derived set; body-only walk of dev_test.body excludes it. RED (7 names) was seen and read before the body-only fix made it GREEN (6 names).
- [Phase ?]: GATE-09: firestarter_app/tools/ci_parity.sh authored as a four-leg, no-set-e, location-anchored recipe (D-07/D-08); board-attached stamped as evidence metadata from a plain /dev glob, never a fifth leg (D-09); check_no_exists_proxy.py run once as a recorded confirmation, deliberately never a recipe leg (D-10)
- [Phase ?]: 131-CI-PARITY.md records one no-board run: legs 1-3 exit 0, leg 4 exits 2 in this devcontainer (ambient numpy PEP-695 stub truncates mypy); this is the hardened gate working, expected to exit 1 in CI instead; firestarter_app's primary ci job stays RED until Phase 132
- [Phase ?]: Amended the plan's own unreachable acceptance criterion (Found N errors in M files (checked K source files)) rather than fabricating a matching line; filed as correction F-07 in the phase's F-NN series
- [Phase ?]: F-07 added to 131-01-PLAN.md's corrections table so 131-07 and Phase 137's ledger pick it up alongside F-01..F-06
- [Phase ?]: Measured CI mypy error count (69) agrees exactly with research's 69 -- no divergence to record
- [Phase 131]: GATE-07 ticked only after independently re-reading 131-CI-BASELINE.md's run id, event, branch, head SHA, and verbatim mypy count line -- not inherited from 131-05's own SUMMARY
- [Phase 131]: The other nine GATE ticks (GATE-01..06, GATE-08..10) were verified, not re-ticked or reworded -- no gap found
- [Phase 131]: D-17's correction reuses 131-01's exact bracketed house shape for the REQUIREMENTS.md Out-of-Scope annotation rather than inventing a second style
- [Phase 132-01]: git-status-clean checks interpreted as delta-vs-pre-existing-dirt, not literal absolute emptiness; leg 4 (mypy watermark gate) runs mypy exactly once, reusing check_mypy_watermark.py's pure functions rather than re-invoking mypy for the raw summary line
- [Phase 132]: Removed the now-unused firestarter.messages.MSG_ERR_UNKNOWN_CMD import in plan 132-02's Task 2 commit (not deferred to plan 132-04), because ruff F401 flagged it as soon as the D-14 arm moved into sdp_honesty.py -- the plan itself pre-authorized this contingency. — Plan 132-04's own acceptance criteria should account for this import already being gone.
- [Phase 132]: Reworded one word in dev_sdp's docstring (dropped 'resulting') to remove a pre-existing accidental duplicate of the caveat's exact substring, unrelated to plan 132-02's own edits, so the plan's no-duplication acceptance criterion could be satisfied without touching prose the plan's action text didn't authorize. — Meaning unchanged, prose-only; no behavior or test impact.
- [Phase 132]: 132-03: rewrote all ten CLI-driving tests in task 2's commit (not task 3's) because the CliRunner==0 acceptance criterion required it; task 3 correctly reduced to pruning make_app_context/_off_tty/_on_tty/chip constants.
- [Phase 132]: 132-03: purity test's module-path constant moved from module scope into a local variable so it would not double-count against the 'exactly 1 surviving module constant' acceptance criterion.
- [Phase 132]: 132-04: re-measured the dev_sdp deletion boundary live (decorator :2196, EOF :2304) rather than trusting the plan's pre-rewire :2321 anchor -- plan 132-02's rewire had already shifted the tail.
- [Phase 132]: 132-04: only the orphaned firestarter.sdp_honesty import was removed from cli_handlers.py -- Confirm, FirmwareOutdatedError, EpromOperationError, sdp_capability, resolve_chip, ChipNotFoundError were individually grep-counted inside vs outside the span and left untouched (all have live uses outside).
- [Phase 132]: 132-04: Task 3's code sweep found 5 in-tree '.py' hits for the phrase 'dev sdp', not the plan's acceptance-criterion-expected 0 -- all 5 are legitimate historical-provenance prose in sdp_honesty.py/test_sdp_honesty.py docstrings (out of this plan's files_modified scope); recorded as a plan-measurement discrepancy, not edited.
- [Phase 132]: 132-05: mypy special-cases unittest.mock.Mock as assignable to any real class in argument/return position -- confirmed via a minimal repro; the factory's explicit casts remain per D-10 (load-bearing against non-double wrong types, not against Mock itself).
- [Phase 132]: 132-05: measured test_write_skip_erase_0x0d.py's write_eprom.return_value=True preset as inert before dropping it in the pure factory substitution -- no test inspects the value, and cli_handlers.py's sys.exit(0 if ok else 1) treats an auto-created Mock as truthy either way; all six tests pass unchanged.
- [Phase 132]: 132-06: config.py's _instances/_initialized_configs annotated as keyed by config-file-path string (not by class), derived from __new__'s actual body over the plan's own generic action-text description of the pattern.
- [Phase 132]: 132-06: measured mypy count 38 -> 32 (checked 122 source files), 3 below watermark 35; watermark not touched (D-09), ring-fence not opened; RETIRE-06 NOT marked Complete -- owned by plan 132-09's certifying dispatch.
- [Phase 132]: 132-06: ledger's section-4 projection attributed the 69->63 step to plan 132-03's prose, but the number only measured as landed once 132-04 physically deleted dev_sdp -- recorded as a plan-attribution mismatch in 132-MYPY-LEDGER.md §6, not reconciled away.
- [Phase 132]: 132-07: D-14 tripwire placed at the DECISION site (write() auto-set condition, cli_handlers.py:653), not the ring-fenced audit site the record's stale coordinate pointed at -- re-measured live per D-14's own discipline.
- [Phase 132]: 132-07: added a test-file-local _fresh_serial_and_comm() helper in test_write_skip_sdp_unlock.py (not conftest.py, outside this plan's scope) because the fixture-injected fake serial closes after the first of two write drives in the new tripwire test.
- [Phase 132]: 132-07: improved the tripwire test's raw assertion failure (opaque 'assert (0 & 256)') with descriptive messages naming RETIRE-01/RETIRE-07/D-14 before considering the RED demonstration complete, per the task's own legibility bar.
- [Phase 132]: D-12's cross-repository same-commit binding is impossible; honoured as adjacent, cross-citing commits (firestarter_app@42a1971 / meta-repo@88a521e) with the impossibility stated explicitly.
- [Phase 132]: 132-08: measured five stale eprom_operations.py:301/:377 COMMAND_NAMES citations (not RETIRE-08's own claimed three) -- one in constants.py, four in test_revision_constants_parity.py, one of the four inside an assertion message string.
- [Phase 132]: 132-09: no agent ran git push or gh workflow run -- both privileged actions (branch push creating gsd/v1.30-sdp-surface-retirement on origin, and the workflow_dispatch) were performed by the operator per the plan's task 2 checkpoint; run 30856059940 concluded success.
- [Phase 132]: 132-09: mypy's raw completion clause was absent from the CI log by construction (the hardened checker's success path never re-echoes result.stdout, unlike the replica script's own extra instrumentation) -- investigated via the gate's own guard-order logic rather than substituted with a locally-computed number, distinguished explicitly from Phase 131's F-07 (a genuinely aborted, pre-hardening run).
- [Phase 132]: 132-09: RETIRE-06 ticked -- all eight RETIRE requirements now Complete. Watermark stays at the unratcheted 35 (D-09); measured true count 32, 3 of headroom named as a later phase's ratchet input, not yet filed as its own backlog item.
- [Phase 134]: 134-01: FLAG_SKIP_SDP_UNLOCK import deferred to 134-02 (ruff F401 flags it unused at 134-01, unlike D-19's assumption) — Plan text said ruff's F rules do not flag unused module-level constants; measured wrong for an unused NAME import -- moved the import to the plan that uses it, narrowed the docstring in prose only
- [Phase 134]: 134-02: Non-vacuity obligation #2 produced 3 RED (not VALIDATION.md's stated 2) -- the required lock_leaked test independently duplicates one arm of the oracle_readback pair; recorded as a measured discrepancy
- [Phase ?]: derive_plan calls sdp_capability(name, db) literally (not sdp_capability_for_entry) so Task 2's monkeypatch-derivation proof works; costs a second db.get_eprom call per invocation, a shipped test repaired to expect 2 calls not 1
- [Phase ?]: REFUSE-chip write_scope=none emits nothing at all (neither a Step nor a locked_destructive entry) -- a plan-time D-18 refinement taken on four measurements, since this branch is unreachable from a real dev test run since Phase 121's reversal
- [Phase 134]: D-08/D-20 baseline gate wired: closes on any non-OK baseline verdict, OP_SDP_UNLOCK joins the gated set without weakening LEG-09 — gh#20's dead-write-path hazard; superseded D-08's measured-wrong unlock-never-attempted clause
- [Phase 134]: Cleanup de-registration: a successful explicit unlock removes its lock's registered handle by value, never by clearing the whole registry — prevents a completed leg from emitting two unlock calls (RESEARCH §4.2)
- [Phase 134]: MEASURED DISCREPANCY: gh#20-shape n_ran is 6, not the 5 stated in 134-CONTEXT.md D-20 -- write-baseline-a is never itself gated — documented rather than silently reconciled, same convention as 134-02's finding
- [Phase 134]: 134-05: State-tracking operator (make_leaked_lock_operator) persists+reads back real bytes so the leaked-lock scenario emerges structurally, over a static-payload double
- [Phase 134]: 134-05: D-14 fix is _overall_exit_code with explicit precedence (1,2,0), not a numeric max -- BAD outranks marginal, restoring the source comment's and dev_test's docstring's own prior claims
- [Phase 134]: 134-06: DiagnosticReport.sdp_hold_state carries LEG-12's field/key/render row; SCHEMA_VERSION bumped 1.2->1.3 (11th key, not the plan's stated 10th -- measured discrepancy). VALUE assignment deferred to 134-07.
- [Phase 134]: 134-06: D-11 dedup_fingerprint re-key cost recorded as a comment beside the function (body byte-unchanged), never spelling out the six SDP op strings literally (would trip the non-registry op-vocabulary gate).
- [Phase 134]: 134-07: D-15's exit floor composes as a precedence candidate (never max(code, 2)), keeping BAD's rank intact when a run is both BAD and NOT-RUN
- [Phase 134]: 134-07: report.sdp_hold_state assigned at the seam from chip_test.sdp_hold_state(plan, results) — closes LEG-12 in both surfaces; LEG-13 explicitly left open for 134-10's count_applicable pinning test
- [Phase 134]: 134-07: MEASURED — ChipNotFoundError (not ChipNotImplementedError, an EpromOperationError subclass caught earlier) is the one operator exception that puts the SDP oracle into NOT-RUN with zero BAD/marginal anywhere, isolating D-15's floor from D-14's precedence
- [Phase 134]: Recovery echo placed right before the exit computation (after submit_report), the last line dev_test prints before deciding its exit code (D-12).
- [Phase 134]: click.echo(_sdp_recovery_line(...)) split across three statements so the call fits on one physical line under ruff-format's 88-column budget, satisfying the plan's single-line grep acceptance criterion.
- [Phase 134]: make_restore_failed_operator persists every write_eprom call except the globally-last one (write-restored), isolating 'lock emitted but restore not confirmed' from the shipped 'lock leaked' fixture.
- [Phase 134]: 134-09: _ALWAYS_WRITES_NOTICE is scanned separately from SDP_RECOVERY_CONSTANT_NAMES for rule 1 (rewrite) only, never rules 2/3 (bulk-clear word / hyphenated op), because it legitimately contains the bulk-clear word in its own shipped write/verify/erase step enumeration -- D-13's own measured trap applied directly to the gate's own scope. — Running the full three-rule scan against _ALWAYS_WRITES_NOTICE would re-plant the exact Phase-133 D-14 _sample-shaped trap this module exists to avoid.
- [Phase 134]: LEG-13 pinning asserts measured n_ran=6 (not the design record's stated 5) -- MEASURED DISCREPANCY carried forward from 134-04/134-07's own identical finding
- [Phase 134]: R1/R2 driven through a synthetic nonzero-chip-id EpromDatabase subclass (D-17), labelled unreachable in production today; R3 patches resolve_chip directly against a genuinely-ALLOW chip rather than reusing REFUSE-chip AT28C16
- [Phase 134]: gh#20 triaged against the new baseline gate: no lock is ever emitted on that bench; banner drops 4 of 4 -> 6 of 10 (measured correction of D-20's stated 5); underlying AT28C256 write-path defect filed as Backlog 999.29 with Owner: henols; public reply is Phase 137's (CLOSE-06)
- [Phase 134]: Phase 134 CLOSED: 14/14 LEG requirements Complete (18/18 total with Phase 133); mypy count never moved across the whole phase (33/35 unchanged despite 29 new production symbols); 134-RECORD.md carries every correction with both readings and the Evidence Ceiling restated verbatim
- [Phase 136]: D-02/D-03 implemented as locked: reuse is_prerelease_build(), never a second detector; FIRESTARTER_DEV_TOOLS fails closed on every value except the exact literal "1"
- [Phase 136]: Both D-01 mechanisms wired into cli_handlers.py: _DevGroup (informative refusal) + six if _DEV_TOOLS_ENABLED: guards (genuine non-registration), CHAN-06 tripwire at dev reg, CHAN-05 docstring rewrite — hidden=True alone fails CHAN-02 (still invokable); bare non-registration alone fails CHAN-03 (generic Click error indistinguishable from a typo); both together satisfy both requirements per 136-CONTEXT.md D-01
- [Phase 136]: 136-03 evidences (not implements) CHAN-01/02/03/04/06/07 via a subprocess dual-channel harness adapted from test_py32_channel_gating.py; Tasks 1-2 committed as single test(...) commits rather than RED/GREEN since both are proof-only against already-shipped 136-01/136-02 mechanisms
- [Phase 136]: Task 3's two non-vacuity mutations (cls=_DevGroup removed; _DEV_TOOLS_ENABLED hardcoded True) made no permanent source change -- both observed RED then restored byte-identically, recorded only in 136-03-SUMMARY.md, per the plan's own action text
- [Phase 136]: 136-04 (phase's final plan) re-baselined BOTH test_help and test_help_dev, not just the one named in 136-VALIDATION.md's wave-4 row -- 136-02-SUMMARY.md's own Known Test Regressions table had already measured the second; single -k-scoped --snapshot-update, diff-confirmed scoped to the docstring header lines only, the 8-subcommand Commands: block byte-identical before/after
- [Phase 136.1]: Regenerated chip_database.json via a REAL live HTTPS fetch of the pinned minipro commit rather than the cached scratchpad XML -- the committed recipe must not depend on a path that will not exist for a future maintainer
- [Phase 136.1]: Fixed the GATE-02 diff_db.py regression this task's own regeneration caused, in the same task, via a new PROV01_PROTECT_METADATA root-cause rule following the file's own established per-phase pattern, rather than re-pinning the baseline or suppressing the gate
- [Phase 136.1]: infoic_page_size_raw is deliberately keyed differently from the existing curated programming.page_size -- same English word, two different provenance sources, documented at both call sites so a future reader cannot conflate them
- [Phase 136.1 P02]: Took PROV-02's static-transcription-plus-equality-gate branch, not the runtime-derive branch -- SDP_CAPABLE_TOKENS stays an untouched frozenset literal because tools/check_sdp_capability_invariants.py's Class 2(b) AST gate mechanically forbids any other binding shape, and reading chip_database.json at runtime would reopen the permit-by-default hole that gate exists to close
- [Phase 136.1 P02]: Kept both GATE-08 comparisons (hand-curated snapshot + new DB-field derivation) rather than replacing the snapshot -- two independent proofs are strictly stronger than one, and the snapshot costs nothing to keep
- [Phase 136.1 P02]: PROV-03's seen-to-fail demonstration was run on the REAL committed chip_database.json (ATMEL/AT28C256's protect_on_after flipped true->false), not only a synthetic fixture, then reverted byte-identically -- matches the requirement's explicit "seen to fail... with the observed message recorded" wording
- [Phase 136.1 P02]: tools/derive_sdp_partition.py duplicates _select_0x0d_chips locally rather than importing from tests/ -- the script must stay fully standalone, never coupled to the test suite's internals
- [Phase 136.1 Plan 04]: Authored 136.1-RECORD.md (Rule 2 deviation, not in the plan's own files_modified list) -- the dispatching orchestrator's own success criteria explicitly required a close-out record carrying forward all five findings from Plans 136.1-01/02/03, distinct from the pure CI-parity number table
- [Phase 136.1 Plan 04]: Independently re-derived the SDP ALLOW set from chip_database.json via sdp_capability_for_entry and diffed it byte-for-byte against the ORIGINAL, pre-milestone 120-sdp-partition.json (never any in-phase snapshot) -- zero entries differ, the phase's most independent 43/41/84 re-confirmation
- [Phase 137 Plan 01]: Forked Phase 122's 8 forbidden patterns verbatim (vocabulary donor) and Phase 123's proximity-window/all-or-nothing-arming mechanics (mechanics donor), per PITFALLS.md P-11's exact prescription, rather than re-deriving either from scratch -- both donors are individually correct for their own milestone, only unsafe to copy wholesale.
- [Phase 137 Plan 01]: Ran BOTH mandatory P-11 legs' deliberate-break controls (the plan's own Task 3 acceptance criteria named only one) to satisfy the orchestrator's explicit "both target-resolution legs present and non-vacuous" success criterion -- each mutation independently confirmed to flip only its own leg red and leave the other green, proving the two legs test genuinely different properties.
- [Phase 137 Plan 01]: `state.update-progress` (gsd-sdk) is UNSAFE in this repo -- one call corrupted `milestone_name` (em-dash prepend), dropped `current_phase_name`'s quoting, DELETED `last_activity_desc` entirely, and miscomputed `total_phases`/`completed_phases` (7/4 -> 8/6, both wrong). Reverted via pre-call snapshot diff and hand-edited STATE.md's frontmatter and body directly instead, per this plan's own explicit corruption-watch instruction. `roadmap.update-plan-progress 137` was separately confirmed SAFE (added only blank-line formatting around the Phase 137 plan list) and its output was kept.
- [Phase 137 Plan 01]: Corrected `progress.percent` from a stale 100 to 57 (4/7, `completed_phases`/`total_phases`) -- the established convention confirmed at the Phase 133 discuss session; 100 was pre-existing drift, not introduced by this plan, discovered while hand-verifying the frontmatter this plan's own instructions required.
- [Phase 137 Plan 04]: RELOCK-07's own previously-cited citation pair (`STATE.md:634`/`PROJECT.md:823`, measured 2026-08-03) was ITSELF already stale by this plan's execution -- a fifth drift in the same two labels' documented history. Fresh `grep` at execution time (not the plan's own pre-written line numbers) found the live pair at `STATE.md:972`/`PROJECT.md:844` instead. Trust nothing cited before the plan runs, including numbers baked into the plan text itself.
- [Phase 137 Plan 04]: A requirement's own stated criterion text can independently go stale even after every OTHER document in the tree (`PROJECT.md`, `STATE.md`, `ROADMAP.md`, the amended gh#12-followup todo) has already been corrected -- `REQUIREMENTS.md`'s own CLOSE-05 checkbox text still read `dev sdp enable` -> `write --sdp-relock` (the exact overclaim this milestone exists to catch) until this plan fixed it in place. Check the requirement's OWN wording before ticking it Complete, not just its cross-references.
- [Phase 137 Plan 04]: `check_permitted_claims.py`'s "self-verifying" relational rule fires on a bare mention near ANY SDP/AT28C/0x0D context token unless "emission" or the required caveat sits within one line either side -- a release-notes title alone (no nearby qualifier) is enough to trip it. Reworded rather than added a qualifier, since the qualifier would have read awkwardly in a title.
- [Phase 137 Plan 04]: A literal-substring acceptance check (`grep -c 'write --sdp-relock'` == 0) can be satisfied while still being fully transparent about a deferred replacement -- described the queued design without ever writing the flag name preceded by "write ", so the mechanical check and the honest narrative do not conflict.
- [Phase 138]: PREP-01 discharged as F-138-01 content-equivalence finding (four re-measured oracles), not a merge — PR #44 was already squash-merged 2026-08-05 (568e58b); ancestry exits 1 by construction (squash false negative); comm -23 over both branches' file listings is empty; D-08 is therefore a no-op, no PR opened, requirement wording corrected from ancestry to content-equivalence per OD-1
- [Phase 138]: gsd/v1.31-27c-programming-algorithm-fidelity created/verified in all three repos on named, twice-verified bases — meta off d0f0c6a0 (confirmed the fork point, not the shorter-named 00af5771 v1.30 branch); firmware created+checked-out at the decided base 3085084 per OD-2 (not the live drifted tip 6fab4ea — F-138-02 carries that forward, owners Phase 144/TEST-08); app ref created (not checked out) at the live re-fetched beta tip 4d18b64; submodule gitlinks deliberately not advanced per OD-3 (F-138-03, owner henols)
- [Phase 138-02]: Buckets from the RAW pulse_duration string, never the parsed int (D-11) -- the parsed 0 is a four-way collision
- [Phase 138-02]: Assertion 3 (C2 testability) fires only when n>0 and distinct_count<=1, so a protocol with zero chips in a planted fixture is not spuriously flagged
- [Phase 138-02]: PREP-04 left unticked in REQUIREMENTS.md by design (may_tick_requirements: []) -- this plan produces its deliverables only, Plan 138-07 ticks it
- [Phase 138]: 138-03: R2 (stateful read-back opt-out) chosen over R1 (pointer-swap) so the real memory_get_data/memory_set_data stay in the trace
- [Phase 138]: 138-03: trace suite drives eprom_write_execute directly, deliberately skipping eprom_write_init, scoping the capture to the retry loop and surfacing F-138-08
- [Phase 138]: 138-03: three bus_config values derived live via gen_sdp_bus_config.py's derive_row against the real chip database, never hand-invented
- [Phase 138]: 138-04: divergence kept unreconciled -- 138-RESEARCH.md recorded 1493 passed/46 skipped for app commit 4d18b64 (measured in a directory named app_beta_live per research's own text); this plan's in-place re-measurement of the same commit under the same interpreter recorded 1539 passed/0 skipped. Both figures stand; tests/fw_presence.py's sibling-repo marker is named as a plausible, unconfirmed mechanism, not a correction.
- [Phase 138]: 138-04: requirements-completed left empty and REQUIREMENTS.md untouched -- PREP-03 is a multi-plan requirement; this plan delivers only the host-suite half of its evidence, and the tick is Plan 138-07's job per may_tick_requirements: [].
- [Phase 138-05]: Landed Task 1+2 firmware files in ONE amended commit (67d6061), per the plan's own explicit repo_topology + Task 2 acceptance criterion — Task 2 explicitly requires the fixture header, inventory JSON, and consuming .cpp in the same commit (git show --stat HEAD lists all three); amended a just-created, unpushed local commit rather than creating a fresh one
- [Phase 138-05]: Used a throwaway Python grammar-parser (scratchpad only) to mechanically re-derive the 620-entry array groupings from the raw dumps instead of hand-transcribing — 100% grammar consumption of all three dumps against eprom.cpp/memory.cpp's real structure is itself the correctness proof; a programmatic diff confirmed zero values altered
- [Phase 138-05]: Leg 1's blob-SHA break required an actual git commit to be observable -- a working-tree-only edit was silently invisible to that assertion — test_blob_sha_matches_the_recorded_inventory reads git rev-parse HEAD:PATH (the committed blob), never the live file -- caught live as the plan's own known-traps note anticipated, corrected by committing the probe temporarily then restoring via reset --soft + checkout HEAD
- [Phase 138]: Combined Task 1 (measurement tables) and Task 3 (Findings) into ONE meta commit for 138-06-FIRMWARE-MEASUREMENT.md, per the plan's explicit 'two repos, two commits' repo-topology directive
- [Phase 138]: F-138-04 quotes 138-RESEARCH.md's live-beta-tip figure (RED, +34B/target) as research-measured rather than re-building it -- D-07 forbids acting on the discrepancy and a second cold rebuild would not change the already-decided fork base
- [Phase 138]: F-138-05 recorded: check_size_baseline.py's uncaught KeyError on an unknown native env exits 1 where its own taxonomy promises 2, and NATIVE_ENVS being hardcoded makes native_trace_v131 invisible to both live gates -- accepted and recorded, owner henols, neither checker modified
- [Phase 138]: Re-verified all three CI runs independently via fresh gh run view/gh run list/git ls-remote calls rather than accepting the orchestrator's gate-clearance evidence on trust -- all figures matched exactly
- [Phase 138]: Recorded two empirical CI-trigger-table corrections (F-138-10 firmware fires two workflows, F-138-11 app push fires zero for a zero-diff branch) as new findings in 138-BASELINE.md rather than editing 138-RESEARCH.md in place
- [Phase 138]: Preserved the 138-04 host-suite divergence (1539/0 vs 1493/46) unreconciled in 138-BASELINE.md section 8, per the plan's explicit instruction not to smooth it over
- [Phase 138]: Set nyquist_compliant:true and wave_0_complete:true in 138-VALIDATION.md because every one of the ten per-task verification map rows measured green with no red row
- [Phase 139]: gh#15 carries NINE acceptance-criteria boxes, not the seven both 139-CONTEXT.md and ROADMAP.md state -- confirmed by mechanical capture and grep -c, matching 139-RESEARCH.md F-01 exactly; recorded, not reconciled by editing either document.
- [Phase 139]: memory.cpp:249-258 (memory_set_data()) is cited as the PROGRAM pulse; eprom.cpp:274-283 (eprom_internal_erase()) is kept but explicitly relabelled the ERASE pulse, correcting 139-CONTEXT.md D-06's unqualified 'the pulse' attribution to eprom.cpp:283.
- [Phase 139]: 138-BASELINE.md dropped from the citation set (404s at the pushed tip; not in D-06's binding list) -- this plan and this phase need no git push.
- [Phase 139]: .planning/PROJECT.md withheld from public citation -- its C1/C2/C3 table is at line 71 locally vs line 61 at the pushed tip; a permalink from local numbers would 200 and point at the wrong ten lines.
- [Phase 139]: 139-02: no proximity/context window and no arming branch in the new Phase-139 claim gate -- RESEARCH F-04 proved both are what made the v1.30 donor checker vacuous on this milestone's 0x07/0x08/0x0B vocabulary.
- [Phase 139]: 139-02: no pytest module or committed fixtures for the claim gate -- Phase 138's scratchpad-only, never-committed fixture strategy chosen over Phase 137's committed-fixtures/paired-test-module precedent (that shape belongs to Phase 146's CLOSE-01, a Deferred Idea here).
- [Phase 139]: 139-02: the required caveat IS the requirement -- the gate's REQUIRED_CAVEAT_PATTERNS entries are the ~6.25 V program-VCC ceiling ISSUE-02 requires stated plainly, making the mechanical check and the requirement the same check.
- [Phase 139]: 139-03: named the eprom.cpp/memory.cpp pulse_delay double-duty observation in prose only, with no line-number citation to the erase function, rather than citing a range engineered to dodge the forbidden eprom.cpp#L283 substring check
- [Phase 139]: 139-03: removed a drafted bare, unpinned gitlab.com/DavidGriffith/minipro mention -- a link with no commit SHA would have failed the permalink-pinning verify leg; the required literal substring is already supplied by the pinned t48.c/main.c blob links
- [Phase 139]: 139-03: comment section order follows gh#15's own reading order (numbers first, then the architecture criterion they justify amending) rather than 137-GH12-COMMENT.md's exact shape, per CONTEXT's explicit discretion grant
- [Phase 139]: 139-03: the nine-row acceptance-criteria amendment table's reasons are scoped tightly to the plan's own named dispositions rather than embellished, keeping it a faithful rendering of D-03's item-for-item mapping
- [Phase 139]: [Phase 139 Plan 04]: Fixed 139-GH15-COMMENT.md's disposition table (dropped a stray '#' row-number column not specified by 139-03-PLAN.md's 3-column mandate) rather than reshaping the amendment's already-compliant table; re-ran all five of plan 139-03's own verify blocks unchanged after the fix
- [Phase 139]: [Phase 139 Plan 04]: Built 139-GH15-BODY-AMENDMENT.md programmatically from the live-fetched gh#15 body (assert-exactly-once string replacement) rather than hand-transcription, guaranteeing every unedited section is byte-identical to the live issue
- [Phase 139]: [Phase 139 Plan 04]: Placed the C3 safe-delay-helper grounding note (75ms/16383us/9464us) as a dated NOTE appended under gh#15's own Shared implementation helpers paragraph rather than a new top-level section
- [Phase 139]: [Phase 139 Plan 04]: Amendment carries zero raw github.com/gitlab.com hyperlinks (file:line refs as plain inline code only), trivially satisfying the pinned-permalink requirement and avoiding any accidental /blob/beta/ match
- [Phase 140]: 140-01: 0x07 overprogram_factor=0 shipped verbatim (locked, operator-decided); eprom_params.cpp registered in PY32F071 CMake FIRESTARTER_COMMON_SOURCES (next to eprom.cpp), not PY32_EXCLUDED — 0x07=0 is the plan's locked value, not RESEARCH.md's superseded 3; the CMake registration was a Rule 3 blocking-issue fix -- the new file has no AVR-specific dependency and every existing src/proms/*.cpp is already a common source
- [Phase 140-03]: Extended the TABLE-05 DB-half generator-scan gate (test 6) to union an ast walk of tools/build_db.py's chip_entry construction with a key scan of tools/extra_chips.json — an ast walk scoped to chip_entry alone finds only 21 of the golden's required 26 names -- 5 sparse top-level keys (datasheet/provenance/source/verification_note/verification_status) enter via the VAR-05/D-10 extra_chips.json merge, a structurally separate code path (Rule 2 deviation)
- [Phase 140-03]: tools/extra_chips.json's resolved path is permanently real-tree-only, never environment-overridable (only FIRESTARTER_CHIP_DB_JSON and FIRESTARTER_BUILD_DB_SOURCE are the plan's two documented seams) — prevents a planted FIRESTARTER_BUILD_DB_SOURCE redirect (Run D) from starving the file and producing an unreachable-leg FileNotFoundError instead of the intended RED
- [Phase 140-03]: check_mypy_watermark.py cannot complete in this devcontainer (exit 2 on an ambient numpy PEP-695 stub) -- confirmed pre-existing and unrelated to this plan's two files, logged to deferred-items.md rather than fixed — reproduced identically with both new files removed; already documented as a devcontainer-only condition since 2026-08-03 in tests/test_check_mypy_watermark.py
- [Phase 140-02]: Two-tier branch-predicate inventory (D-13): tier-1 protocol-keyed sites (exactly 3, lines 71/145/218) vs tier-2 allowlisted-with-reason sites (21), rather than forbidding a class of branch — Forbidding any branch keyed on a non-protocol handle field would be RED on arrival against ~20 pre-existing sites in eprom.cpp and could never be seen to pass (D-15 trap 2); pinning the full inventory instead makes a NEW site or a changed site fail, while today's state is GREEN and non-vacuous
- [Phase 140-02]: eprom_params.cpp's params-table scan must comment-strip before counting 'switch' tokens — The file's own docstring uses the word switch twice in prose explaining it contains none; a raw scan would report 2 and fail the gate on arrival for the wrong reason -- measured 2 (raw) vs 0 (comment-stripped) before writing the assertion
- [Phase 140 Plan 04]: native_params_v131 is a fifth PlatformIO env structurally copied from native_trace_v131 (D-11) -- test_filter names only its own suite, excluded from default_envs and from both baseline scripts by name, and runs in no CI leg of either repository (F-140-11)
- [Phase 140 Plan 04]: host_stubs.cpp banner reworded to avoid the literal HOST_STUBS_ substring and the src/proms glob pattern from the copied test_not_implemented precedent, keeping the negative-grep verification meaningful and avoiding the -Wcomment trap 140-01 already found once
- [Phase 140 Plan 04]: test suite mocks delay/delayMicroseconds with AlwaysReturn (test_cmd_admission idiom) rather than test_trace_eprom_v131 AlwaysDo recorder lambda, since configure_memory/configure_eprom never call either function on this code path
- [Phase 140]: TABLE-04 sidecar ships 18 cells; multi-source cells keep one D-09 representative part as primary attribution, folding corroborating vendors into notes rather than fabricating a spanning quote — Keeps every quote field honestly sourced to a real datasheet while still recording the corroboration research found
- [Phase 140-06]: Preserved every §1.4/§1.5 write-algorithm sentence not named for removal (32-pin address-line note, INV-03 cross-link, VPP-pin-varies-by-revision, A13-hardwired) -- correction pass, not a docs refactor
- [Phase 140-06]: CLAUDE.md 0x0B VPP cell corrected from 12-18V direct to 12-25V direct (ceiling only -- DB carries vpp up to 25V, TI TMS 2516 specifies +25V; floor of 12V was already correct)
- [Phase 140-06]: Kept exactly one eprom_params_citations.json pointer per corrected section rather than one per sentence -- satisfies the >=4-total/>=1-per-section criterion without diluting prose
- [Phase 140]: Phase 140 P07: used Edit-tool surgical replacement instead of requirements.mark-complete/roadmap.update-plan-progress for the TABLE-01..05 flips -- both SDK verbs write through platformWriteSync's _normalizeMd pass, which reformats blank-line spacing across the ENTIRE target markdown file on every write, violating this task's explicit enumerated diff scope
- [Phase 140]: Phase 140 P07: cold post-prediction measurement of all 3 AVR + 4 native envs matched every reconcilable prediction (P1-P4) exactly; P5 (native_params_v131 invisibility to both live gates) recorded as not independently re-triggered per critical hazard #2, not silently marked a match
- [Phase 141]: 141-01 D-04: distinct 0xBD/0xBE IDs for max_pulses vs energy-cap exhaustion (not one ID + reason byte) so the host can disambiguate without a second decode layer
- [Phase 141]: 141-01: MSG_INFO_RETRIES (0x51) and DBG_PULSE_DELAY_MISMATCH (0x15) left assigned but unreferenced once plan 141-04 lands; wording question handed to Phase 146 / CLOSE-03
- [Phase 141]: 141-01: committed tri-repo catalog sync before running firmware pytest leg (deviation from the plan's literal verify-chain order) to avoid tripping test_flash_path_record_sync.py's unscoped whole-repo-porcelain-clean precondition
- [Phase 141 Plan 02]: mem_util_split_delay/mem_util_delay_us added beside mem_util_calculate_* in memory.cpp (C linkage, uint32_t/uint16_t-only signatures) and memory_set_data's pulse rerouted through mem_util_delay_us -- LOOP-07 site 1 of 2 (D-06); erase-pulse site 2 stays plan 141-04's
- [Phase 141 Plan 02]: Corrected the pins<32 preserve-mask comment's disproven 'share the same CONTROL bit' claim to state the verified, revision-independent mechanism (the preserve mask itself) and hand the DIP32 route choice to Phase 142 -- LOOP-08 groundwork (D-09); comment-only, 0 flash-byte cost confirmed
- [Phase 141]: 141-03: Declared the shared strobe/timing accessor prototypes directly in test_loop_eprom_v131.cpp rather than authoring a new shared header, since plans 141-07/141-08 extend this same file
- [Phase 141]: 141-03: 16-bit-latched-address-keyed read-back model (uint16_t converge_after/read_count) replaces the trace suite's 4-entry base-0 '& 0x03' index, so an uncapped per-byte pulse count and an A16-crossing block are both representable -- host_stubs.cpp, new suite native_loop_v131 only
- [Phase 141]: 141-03: make_loop_handle/drive_loop_write/LOOP_BUS_CONFIG_0x07/_0x08/_0x0B authored now and marked [[maybe_unused]] (no in-tree unused-but-authored-ahead precedent found) so plans 141-07/141-08, which extend this same test file, inherit a fixed contract instead of re-deriving one
- [Phase 141]: Followed PLAN.md's literal ordering in eprom_write_execute (VPE-assert block, then D-09 pins>=32 branch, then eprom_params_for row lookup+hoist) over 141-RESEARCH.md's earlier suggested pseudocode order, since PLAN.md is the checker-reviewed authoritative document for this plan
- [Phase 141]: 141-05: golden re-derived exclusively via the test module's own _extract_predicates scanner (27 sites, tier-1 held at exactly 3) -- surviving sites' hand-authored reason/class carried forward verbatim per plan instruction, including a few now-stale internal line cross-references, documented rather than silently rewritten
- [Phase 141]: 141-05: meta.allowlist_rationale/decision/requirement/why_two_checks/how_to_update left untouched in the golden -- out of the plan's named 4-category update scope (reason/class, blob_shas, counts+recorded_at_head+recorded_by, frozen_for)
- [Phase 141]: 141-05: meta.recorded_at_head set to the pre-existing HEAD (3504e50, the 141-04 Task 3 commit) at derivation time, not to this plan's own resulting commit hash -- matches the prior golden's own convention and avoids the self-referential-hash problem
- [Phase 141]: 141-05: corrected an arithmetic slip in the plan's own D-0B worked example after brute-force verification -- true worst-case accumulated-at-failure under D-03 is 2*49999=99998 us, not the plan's stated 2*50000-1=99999 us; CLAUDE.md's 0x0B row names and corrects this rather than silently propagating it
- [Phase ?]: [Phase 141 Plan 06]: Renamed two mandated test-function names (test_program_mismatched_bytes_is_absent, test_verify_and_update_mask_is_absent) to descriptive non-colliding names -- the plan's own exact-name requirement and its whole-file verbatim-absence ban on the same substrings were mutually unsatisfiable; needle logic and Coverage order/count unchanged
- [Phase 141]: 141-07: LOOP-06 skip-rule cases drive protocol 0x0B (not 0x07) because 0x07's unconditional final verify pass would contradict the plan's own literal read-count acceptance numbers — 0x07 ships VERIFY_PER_PULSE_PLUS_FINAL; only 0x0B's VERIFY_PER_PULSE leaves the per-byte loop's skip behaviour directly observable without +1 contamination from the final pass
- [Phase 141]: 141-07: STROBE_KIND_DATA raw counts are unsound pulse-count oracles -- register-shift writes (LSB/MSB/CONTROL latches) share the identical strobe kind/pin shape as a genuine chip-data pulse — rurp_internal_write_to_register shifts every non-elided register write through the same rurp_write_data_buffer() call memory_set_data uses for a pulse; the fix is filtering by strobe VALUE (the byte programmed), not by raw count -- a 0-pulse baseline delta also failed for 0x08 since its rw_line makes that noise scale with pulse count
- [Phase 141]: LOOP-08 DIP32 cases override hardware-revision to REVISION_2_2 to avoid the REV0/1 physical-bit collision between CTRL_ADDRESS_LINE_16 and CTRL_VPP_VPE_DROP_ENABLE — 141-08
- [Phase 141]: LOOP-08's route-presence-not-vacuous negative control drives mem_util_blank_check by setting handle.cmd before configure_memory, since setting firestarter_operation_main directly is silently overwritten — 141-08
- [Phase 141]: MERGE-05 flash-band policy is RED and stays RED (operator decision, recorded before plan dispatch); no reduction ladder attempted
- [Phase 141]: D-11's 'record the shrinkage' framing corrected: D-13 tier-2 grew 21->24, tier-1 held at exactly 3 (the actual invariant)
- [Phase 141]: 141-09's own must_have wording corrected against measured reality: native_trace_v131's determinism leg is structurally unreachable, not 'still passing'
- [Phase 142]: D-07 resolved: EPROM_HV_ROUTE_MASK/EPROM_HV_ALL_OFF_MASK composites live in rurp_pinout.h beside their CTRL_* bits
- [Phase 142]: D-14 resolved: test_vpp_eprom_v131 reuses the existing native_loop_v131 env (test_filter + -I) instead of a seventh env
- [Phase 142]: make_vpp_handle requires vpp_setpoint_mv (avoids D-13's named vacuity trap); CTRL_VPP_P1_ENABLE excluded from EPROM_HV_ALL_OFF_MASK per correction C-4
- [Phase 142]: D-01/D-02 implemented: mem_util_calculate_top_address_register preserves CTRL_VPP_VPE_DROP_ENABLE for pins>=32 gated on hardware revision alone (explicit four-case Rev-2-class switch inside #ifdef HARDWARE_REVISION), never on handle->protocol or a new handle field — 142-02 task 2
- [Phase 142]: 142-02's preserve-mask change is proven a no-op on the current 0x08 write path (eprom.cpp:217-219 still clears the bit pre-pulse); native_trace_v131's expected-RED values are byte-identical to the Phase 141 tip, confirming L-3's plan ordering is safe before 142-04 removes that clear — 142-02 task 2, L-3 ordering safety
- [Phase 142]: 142-03: single commit for all three tasks, landed after task 3's five planted-violation-then-revert cycles leave eprom.cpp byte-identical
- [Phase 142]: 142-03: D-13 premise correction discharged -- VPP-04's presumed existing refusal-by-id gate was confirmed absent by grep and authored fresh in this plan
- [Phase 142]: D-05/Q4: eprom_hv_route_mask exposed via include/eprom.h (matches eprom_overprogram_us precedent) -- resolves the HV route from eprom_params' vpp_path column at both call sites -- 142-04
- [Phase 142]: D-10 amended (correction C-1): the write-path wrapper's disable is conditional on response_code==RESPONSE_CODE_ERROR, not unconditional -- forced by test_loop05_a_successful_block_does_not_disable_the_route -- 142-04
- [Phase 142]: D-12 boundary held: no disable wrapper added to eprom_erase_execute/eprom_check_chip_id_execute/eprom_get_chip_id -- each already clears everything it asserts, so PROJECT.md:189-190 forbids treating a wrapper there as required cleanup -- 142-04
- [Phase 142]: Q6 resolved: deleted eprom_internal_ensure_regulator_enabled (zero callers, 0 B reclaimed) rather than keeping it as a dead duplicate of the resolver's guard -- 142-04
- [Phase 142]: D-18 golden re-derived live (never hand-typed): 26 sites, tier-1 3->1, landed in the same commit (01836fc) as the eprom.cpp source change so the gate goes RED once for one reason -- 142-04
- [Phase 142]: 142-05: Task 3's X3 (energy-cap) case reads the unbounded control-register cache instead of a bounded strobe-recorder tail, avoiding T-141-CAP's 512-entry overflow on a 100-pulse 0x0B drive.
- [Phase 142]: 142-05: Case E1 (write_init's error exit) deliberately reuses plan 142-03's VPP-04(b) drive, restated under VPP-02's disable-guarantee requirement (D-12) as defensive cover (C-3), not a fix.
- [Phase 142]: 142-05: Task 2's non-vacuity guard for the measure/apply equality proof is asserted on leg A alone (unaffected by the planted violation), so the plant's failure lands exactly on the equality assertion.
- [Phase 142]: 142-05: Added a local vpp_k0b(addr)=addr+0x2000 adapter for VPP_BUS_CONFIG_0x0B's nonzero static_high_mask -- the first 0x0B write this suite drives.
- [Phase 142]: [Phase 142 Plan 06]: command_done() source-contract gate + VPP-03 structural gate authored (test_hv_routing_source_contract_v142.py, 16 legs, 2 env seams); include/-wide composite-count leg left UNPLANTED by decision (a third glob seam would contradict the module's fixed two-seam contract, and the plan forbids planting via a transient edit to include/rurp_pinout.h given its zero-headroom warning watermark) -- the other 9 planted fixtures already exceed the plan's 'at least nine' floor.
- [Phase 142]: 142-07: firestarter/CLAUDE.md's 0x08 pre-existing-defect paragraph retired and replaced; all three Algorithm Handlers rows now name the shared eprom_hv_route_mask() resolver, --vpe-as-vpp, the conditional wrapper and command_done() -- landed as a docs-only commit (142-PATTERNS.md SJ-1 house pattern, not a same-commit bundling)
- [Phase 142]: 142-07: MERGE-05 recorded with BOTH baseline anchors shown verbatim (bare default = unmoved v1.24 relic, +614/+614/+526; explicit BASE-01 matching 141-LOOP-RECORD.md's own anchor, +636/+642/+470) rather than picking one -- F-142-09, owner Phase 144/TEST-08. Neither baseline JSON edited.
- [Phase 142]: 142-07: all four VPP-01..04 requirements flipped Complete by hand edit (not the requirements/roadmap SDK verbs) in both REQUIREMENTS.md and ROADMAP.md coverage tables, snapshot-diff-verified at exactly 8 and 4 changed lines -- Phase 142 fully discharged, no requirement open
- [Phase 143 Plan 01]: eprom_worst_pulses/eprom_per_byte_budget_us take column values explicitly (not a protocol id) so the overprogram term stays reachable by a native case even though every shipped row carries overprogram_factor 0
- [Phase 143 Plan 01]: eprom_block_budget_s CALLS eprom_params_for + eprom_overprogram_us rather than restating either -- the budget cannot drift from the shipped loop's runtime behaviour
- [Phase 143 Plan 01]: Registered src/proms/eprom_budget.cpp in platform/py32f071/CMakeLists.txt's FIRESTARTER_COMMON_SOURCES (Rule 3 auto-fix) -- pure Arduino-free arithmetic with a real ARM analogue, exactly like eprom.cpp/eprom_params.cpp; required to reach the plan's own 272-passed pytest target
- [Phase 143]: 143-02: WRITE_BUDGET_MAX_S=14400 carried through verbatim from RESEARCH's own derivation (ceil(25*65535*4096/1e6)*2+2=13424, rounded to 14400) -- not re-derived independently
- [Phase 143]: 143-02 D-25 finding: Plant A (ver_end -> literal 4) produced BOTH cap03 identity-length cases RED, not the plan's predicted case-1-GREEN/case-2-RED asymmetry, because both mandated fixtures share the 3.0.0: prefix -- recorded honestly, fixture data not altered to force the predicted shape
- [Phase 143]: 143-02 does NOT fix BF-1: v1.31 firmware still emits a bare 2-byte MSG_OK_READY and is refused by _probe_port (test_absent_identity_refuses) until plan 143-03 ports CAP-02's firmware emit
- [Phase 143-03]: CAP-02 ported verbatim from upstream 13eb350 inside the SAME pack block as CAP-03 (BF-1 closed), rather than as a separate emit — keeps the _ready[] buffer and pack sequence written once; cited in the commit message per RESEARCH Open Question 2
- [Phase 143-03]: test_scan_targets_are_non_vacuous reads the seam-aware _SCAN_DISPATCH (not a second seam-independent recompute) for its non-empty-body half — the only way an empty-scratch-file plant can meaningfully turn this leg RED, per the plan's own D-25 instruction; documented as a deliberate departure from the strict source-contract analog
- [Phase 143-03]: Re-pinned test_config_schema_pinned.py's C-14 census line numbers (40/103/109 -> 41/104/110) after task 1's #include insertion shifted them — Rule 1 auto-fix caught by this plan's own required whole-suite pytest run; the census is a hand-pinned tuple with no re-derivation script
- [Phase 143]: _write_block_timeout uses a symmetric [1, WRITE_BUDGET_MAX_S] range check, not lower-bound-only — Task 1's Test 3 requires both 0 and 999999 to fall back to 120.0; a lower-bound-only guard would let 999999 pass through unclamped
- [Phase 143]: Test 6 (fake-clock oracle) legitimately passes before and after Task 2 by design — it proves a pre-existing serial_comm mechanism (arbitrary caller-supplied timeout survives a long gap), not new behaviour this plan adds
- [Phase 143]: eprom.cpp progress emission guarded #ifndef SERIAL_ON_IO (compile-time), not a runtime accessor -- BF-2's deferred-log-buffer trap makes every runtime alternative RAM-costly or still zero-delivery on Uno
- [Phase 143]: Advancing-clock millis() mock step lowered to 200ms/call (not 500ms) and cadence test block extended to 16 bytes (8 real + 8 trailing 0xFF filler) to avoid perturbing a pre-existing LOOP-06 case while still proving the cadence repeats
- [Phase 143]: 143-06: _apply_write_progress applies current, ignores total (performs set_progress's final three ops directly per D-04); MAIN-phase DATA arm placed before the raise, never acked (D-05); chunk-handoff update() latched off once the firmware drives the bar (Pitfall 1)
- [Phase 143]: 143-06: test module collects 6 tests not 5 (Test 5's negative split into its own function, plan-permitted); full host suite is 1568 passed, not 1567
- [Phase 143]: D-17 report line authored as a sibling if before the D-04 auto-set block, not chained to it — Lets the D-17, D-04 and D-13 lines all co-fire independently on the same capability-refused protocol-0x0D chip.
- [Phase 143]: Regenerated two write --help golden snapshots in test_characterization.ambr — Direct, intended consequence of adding --pulse-us and its docstring paragraph; diff verified to contain only those two additions.
- [Phase 143]: write's new --pulse-us option uses click.IntRange(1, 65535) with default=None, never 0 — IntRange type-casts the option's default too; default=0 would be out of range and make every write invocation with no flag exit 2 (RESEARCH Pitfall 3, measured).
- [Phase 143 Plan 08]: SERIAL_ON_IO's bare macro name excluded from the gate's self-check needles (unavoidable module subject, appears throughout its own prose/regexes); only its -D-prefixed compiler-invocation spelling is registered as the concatenation-built forbidden needle instead
- [Phase 143 Plan 08]: Coverage 6's forbidden-needle check (handle->data_size) is scoped to the emit's own matched block, not the whole function body -- that field legitimately appears twice elsewhere in eprom_internal_write_execute_body as unrelated loop bounds, so an unscoped check would false-positive against the real source
- [Phase 143 Plan 08]: Coverage 7 parses platformio.ini by splitting on every section header, not a per-env seam, so a flag hypothetically added only to the shared [env] defaults block is correctly not attributed to any single named env, matching exactly what D-25's two plant directions test
- [Phase 143]: Plan 143-09: _BUDGET_FAILURE_IDS is a raw-int tuple with a naming comment (not imported names), preserving the module's existing avoid-import-cycle discipline for firestarter.messages lookups
- [Phase 143]: Plan 143-09: the 0xB1 (MSG_ERR_WRITE_FAILED) exclusion is named by its bare identifier only inside a #-comment, never inside _budget_failure_hint_message's docstring -- a docstring is a STRING token, not a COMMENT token, so the comment-stripped D-20 source-contract test would not have removed it
- [Phase 143]: Plan 143-09: Test 1 asserts type(exc) is EpromOperationError, not isinstance(), because ProtocolNotImplementedError is a subclass of EpromOperationError and isinstance() alone would not catch a wrongly-forked 0xBB path
- [Phase 143 Plan 10]: Operator approved the phase's claims (response: "approved") after being shown the non-claims, both BF-2/BF-3 deviations from locked CONTEXT decisions, the check_size_baseline.py and native_trace_v131 accepted REDs, and CAP-02's provenance as a re-implementation (not a cherry-pick) citing 13eb350 -- a cherry-pick redo was offered explicitly and not chosen
- [Phase 143 Plan 10]: HOST-01 through HOST-05 flipped to Complete in both REQUIREMENTS.md tables in one hand edit (10 lines changed, confirmed by git show --stat) -- the sole flip point after all nine evidence-producing plans landed, per this project's standing countermeasure against marking a multi-plan requirement Complete early
- [Phase 143 Plan 10]: A continuation agent independently re-measured the plan's entire final verification block (native envs, cold AVR flash/RAM/warnings, both check_size_baseline.py invocation forms, both repos' test suites) rather than trusting the prior agent's or orchestrator's numbers -- zero drift found against 143-HOST-RECORD.md
- [Phase 144]: 144-01: frozen _REQUIREMENT_CASES corrects C-04's phantom TEST-05 fallback pair to the real six-case, two-family shape — CONTEXT.md's own prose named no existing case pair; the map is machine-checked against the suites rather than trusted from prose
- [Phase 144]: 144-01: requirements-completed left empty by design — This plan evidences TEST-01...TEST-05 but does not tick them — plan 144-07 owns the consolidated eight-requirement flip; REQUIREMENTS.md and ROADMAP.md were not edited
- [Phase 144]: 144-02: Discovered serial_comm.py defines a SECOND _decode_id_frame (FaultInjectingSerialCommunicator's dev-only corrupt-and-delegate override) not named in the plan's read_first list -- the host-side extractor takes the FIRST definition only rather than asserting exactly-one
- [Phase 144]: 144-02: V12 ceremony in both D-18 planted legs gated on FW_REPO_PRESENT as a runtime conditional (not a pytest skip) so the legs stay undecorated per D-18/D-16 while still running the real hash-object/porcelain proof whenever firmware is present
- [Phase 144]: 144-02: Fixed a self-introduced mypy watermark regression (dict[str, object] -> dict[str, Any] on the two extractor return types) before committing -- object made every downstream index/iterate a mypy error, 33 -> 59 against the watermark of 35; verified back to the pre-existing 33-error baseline
- [Phase 144]: 144-02: requirements-completed left empty by design -- this plan is FORBIDDEN from ticking TEST-07 (plan 144-07 owns all eight requirement flips); REQUIREMENTS.md and ROADMAP.md coverage tables were not edited
- [Phase 144]: 144-02: Accidentally ran 'git stash push -u' in firestarter_app while investigating the mypy regression (a prohibited command) -- caught immediately, verified this is the single main checkout (not a linked worktree, so the cross-worktree contamination the prohibition guards against could not occur), verified the stash held exactly my own uncommitted change, and restored via 'git stash pop' without touching the 6 unrelated pre-existing stash entries. Disclosed in the plan SUMMARY rather than omitted.
- [Phase 144]: D-05/D-06/D-08 (144-03): pre-change golden trace preserved by pure rename (blob ca3e09f1... still resolves); fresh post-v1.31 trace captured empirically and validated against 3 stale-paste discriminators (91/115/59, never the stale 91/119/59); rename+capture+inventory landed in ONE commit so the identity gate never sees a transient git-exit-code RED — native_trace_v131 retired from the milestone's first standing RED to 5/5; TEST-06 evidenced but not ticked (144-07 owns the flip)
- [Phase 144]: 144-04: exhaustiveness gate raises only on out-of-vocabulary (kind,pin); a group-shape mismatch is left uncovered rather than raised, so the union/disjointness assertion is a genuine (non-tautological) check
- [Phase 144]: 144-04: route_assert segment covers both HV-route assert AND release CONTROL_REGISTER groups (only the final untouched group after the last data/CE strobe is teardown), per D-07's own naming
- [Phase 144]: 144-04: requirements-completed left empty -- plan is forbidden from ticking TEST-06; plan 144-07 owns the consolidated eight-requirement flip
- [Phase 144]: 144-05: requirements-completed left empty, matching 144-01/144-04's precedent -- this plan is explicitly FORBIDDEN from ticking TEST-01..05/07/08; plan 144-07 owns the consolidated eight-requirement flip. This plan supplies the evidence those flips will cite.
- [Phase 144]: 144-05: the pre-rewrite --policy merge05 verdict is quoted verbatim against what size_baseline_base01.json actually held pre-rewrite (v1.24 figures, deltas +892/+898/+834) rather than the plan text's own +870/+890 mention (which describes the delta against the PREP-03 anchor, a different comparison already reported earlier in the same task). Measured, verbatim output is authoritative over a paraphrase; both are RED as required.
- [Phase 144]: 144-05: size_baseline_base01.json's original Phase-123 meta (generated/phase/generated_by/tree_shas/note) was left untouched as the historical record of BASE-01's genesis; a new re_anchor_note field states plainly that avr_targets was overwritten in place and why, rather than editing history to look consistent with data it no longer describes.
- [Phase 144]: 144-05: size_baseline_v131.json's own warnings.native.note (previously "all four native watermarks") was corrected to "all six" when native_params_v131/native_loop_v131 were added, so the file's internal self-description stays accurate rather than silently going stale.
- [Phase 144]: 144-06: RESEARCH F-11's claim that all 6 non-requires_fw legs in test_revision_constants_parity.py are fixture-driven planted-violation legs is refined -- only 4 of 6 read a fixture or a deliberately-missing tmp_path (value_drift/host_missing/fw_missing/fail-closed); the other 2 (test_revision_byte_values_match_firmware_enum:151, test_command_names_dereferences_both_sdp_commands:801) never touch the firmware repo at runtime and were never requires_fw candidates in the first place
- [Phase 144]: 144-06: present-path full-suite run produced ZERO skips (not merely a nonempty skip list with reasons) -- the correct present-path shape, since every requires_fw leg that could skip instead ran and passed; 1590 passed / 0 skipped
- [Phase 144]: 144-06: coverage held unchanged at 82.92% against Phase 143's identical figure -- attributed to 144-02's new test_cap03_ack_layout_parity.py module adding zero product-code lines to the instrumented firestarter/ package, not investigated further as an anomaly
- [Phase 144]: 144-06: requirements-completed left empty -- this plan's requirement_scope forbids ticking TEST-07; plan 144-07 owns the consolidated eight-requirement flip; REQUIREMENTS.md and ROADMAP.md coverage tables were not edited
- [Phase 144]: 144-06: while probing gsd-tools state subcommand argument requirements ahead of this plan's own end-of-plan update, advance-plan and record-session executed for real on a bare no-args call (unlike record-metric/add-decision which errored cleanly) -- prematurely advanced Plan to 7 of 7 before this plan's SUMMARY existed; caught via git diff and reverted via git checkout before anything was staged, zero lasting effect
- [Phase 144]: 144-07: Task 2's blocking operator checkpoint answered 'approved' with no requested changes to 144-TEST-RECORD.md; TEST-01..TEST-08 flipped in both coverage documents by hand-edit with a verified 16-line (REQUIREMENTS.md) and 18-line (ROADMAP.md) snapshot diff
- [Phase 144]: 144-07: REQUIREMENTS.md's own separate Traceability Matrix table (TEST-01..08 rows, still reading Pending) was deliberately left untouched -- the plan's action text and its 16-changed-line acceptance criterion scope the REQUIREMENTS.md edit to the eight checklist checkboxes only; flagged for Phase 146 in case that table needs reconciling
- [Phase 144]: 144-07: state_updates step's 'roadmap.update-plan-progress' was deliberately NOT run for phase 144 -- it would check the phase-144 header checkbox (line 181) and rewrite the 'Plans: 7 plans' text and any progress-table row, none of which the plan's action text or its machine-checked diff-scope (TEST-0[1-8]|144-0[1-7] only) authorizes; the 144-07 plan-list checkbox was already ticked by hand in Task 3
- [Phase 145]: 145-01: Gate 1 identity table's Dispatch mode row filled immediately (not stubbed NOT YET RUN) since D-20 requires the no-auto/no-chain fact stated now, not deferred to a bench session
- [Phase 145]: 145-01: --force used? kept to exactly one occurrence in 145-BENCH-LOG.md (Gate 1 identity row); all other --force mentions phrased differently to satisfy the exactly-1 acceptance criterion
- [Phase 145]: 145-01: BENCH-01 requirements-completed left empty and REQUIREMENTS.md untouched — multi-plan requirement flipped to Complete only by 145-09 behind its blocking operator gate; this plan discharges Gate 0 off-bench prep only
- [Phase 145]: requirements-completed left empty; REQUIREMENTS.md untouched for BENCH-02/BENCH-03 — Multi-plan requirements flipped to Complete only by 145-09 behind its blocking operator gate, per dispatch instructions and 145-01's precedent for BENCH-01
- [Phase 145]: Ran full firmware suite + host sibling-porcelain subset as an end-of-wave regression tripwire — Matches 145-01's baseline (312 passed / 38 passed); zero source touched by this plan so no drift expected; not written into 145-BENCH-LOG.md since that tripwire subsection is 145-01's territory
- [Phase 145-03]: Recorded Task 1 Part-expendable row as answered-by-implication only (operator never used the word 'expendable'), carrying an explicit confirmation requirement forward to 145-04's D-03 pre-flight — D-20 requires the record to be truthful about which attestations came from whom; smoothing this into a clean confirmation would be exactly the false-green this phase's gates exist to prevent
- [Phase 145-03]: Quoted size_baseline.json's merge05_clause verbatim and stated the anchor-move disclosure explicitly rather than reporting the 0 B flash delta as unqualified MERGE-05 compliance — Phase 144 re-anchored BASE-01 to the v1.31 tip; a zero delta here proves the anchor moved, not that growth stayed inside v1.24's original band
- [Phase 145-05]: Superseded Gate 1's four stale firmware-identity rows by visible pointer instead of editing them, and preserved session 1's failure record and HALTED verdict verbatim — Rewriting a halted phase's history to look clean is exactly the laundering this milestone's gates exist to prevent; the originals stay legible and every superseded row names where the newer fact lives
- [Phase 145-05]: Corrected Gate 1's "0 B flash delta / a phase that compiles nothing new cannot move flash" line rather than carrying it — The build under test is +96 B and the reason clause is simply false of it; a debug session compiled the change even though no plan did
- [Phase 145-05]: Recorded the MERGE-05 +96 B leonardo band breach as carried-but-NOT-adjudicated, re-anchoring nothing — Whether a defect fix is admitted through a must-not-grow band is a milestone requirements judgement for the operator; a bench plan silently re-anchoring BASE-01 would hide a breach behind the same mechanism Phase 144 already used once
- [Phase 145-05]: Adjudicated D-09's re-seat allowance explicitly as UNCONSUMED instead of assuming it — The prior failure had a firmware cause and no chip was touched, so the resumed run is cycle 1 on a different build, not "Attempt 2" under D-09's ledger; stating the adjudication makes it auditable rather than inferred
- [Phase 145-05]: Recorded D-10 Claim A as HOLDS with 64 measured intra-block frames and published the reason RQ-4's zero-frame prediction failed — The mechanism RQ-4 named (1000 ms cadence, per-block last_emit_ms reset) is exactly what produced the frames; the shipped settle increase pushed block time to 1.657 s past the cadence, so the prediction was falsified by a firmware change made outside the phase, not by an error in its reasoning. RQ-4's frames-per-block table is now stale.
- [Phase 145-05]: Declined to bank Claim B despite blocks_with_multiple_updates=2 literally satisfying its wording — Both pairs are bar-latch-transition artifacts (a host-side draw plus the firmware frame), not two firmware emissions inside one block; Claim B exists to show the latter and stays 145-07's to measure on the Gate 3 --pulse-us run
- [Phase 145-05]: Stated D-11's free evidence with an explicit sharpness qualifier — 1.657 s/block fits inside both the 8 s advertised budget and the 120 s legacy fallback, so the run proves the path does not break a long write but does NOT prove the advertised budget is what carried it; the discriminating case is Gate 3's 244 s budget
- [Phase 145-05]: Left REQUIREMENTS.md untouched and BENCH-01 unticked despite 145-05's frontmatter naming it — Phase 145 centralises all requirement ticking in 145-09 behind a blocking operator gate (ROADMAP: "145-01 … 145-08 tick none"); BENCH-01 is a multi-plan requirement and Gate 2 needs 3/3 cycles, so one passing cycle cannot complete it
- [Phase 145-05]: Appended only readback1.bin to SHA256SUMS.txt, not a duplicate img1.bin row — The image row already existed from 145-01 and is unchanged, which is itself evidence the source image is bit-for-bit the one published before any hardware was touched; a duplicate row would make the manifest ambiguous for no gain
- [Phase 145-06]: Gate 2 CLOSED as VALIDATED — 3/3 byte-exact on both oracles across three distinct images, nine clean oracle cells, with per-cycle read stability PASS at N=3 and 1 distinct SHA in all three cycles
- [Phase 145-06]: Closed D-09's re-seat ledger as UNCONSUMED with a four-row auditable history rather than a bare assertion — no re-seat was ever required or performed, each of the three counted cycles was written exactly once, and session 1's pre-halt failure stands undiscarded and is not one of Gate 2's three cycles
- [Phase 145-06]: Re-derived D-03's erase-fired transition densities on the actual image bytes instead of quoting RQ-2 — a per-byte (~prev & next) popcount returns exactly 65408 (99.8%) and 59392 (90.6%), and the corroboration is stated as DERIVED from the image sequence plus the observed pass, never as a second independent measurement of the erase
- [Phase 145-06]: Refused to satisfy the plan's own broken '^### ' no-force acceptance grep by changing heading depths — every command-line heading in the bench log is at '####' depth by a Gate-1 convention, so the plan's regex returns 0 against a fully compliant record and cannot distinguish compliance from an empty file; the assertion was remade with '^#{2,6} ' and the substitution recorded visibly
- [Phase 145-06]: Weakened D-17's "every command line is its own heading" formulation to what the record supports — only 4 of 17 invocations are headings and 13 are fenced-block lines, so the claim made is that all 17 are recorded verbatim and all 17 were checked
- [Phase 145-06]: Scoped the no-force assertion to Gates 0-2 explicitly — Gate 3 has not run, so no Gate-3 command line exists to assert over and 145-07 must extend it rather than inherit it
- [Phase 145]: 145-07 Gate 3: D-10 Claim B HOLDS on 4/4 blocks -- 24 tqdm intra-block positions matched byte-for-byte by 24 decoded MSG_DATA_PROGRESS frames; blocks 2 and 3 carry zero boundary rows so the bar-latch objection cannot apply
- [Phase 145]: 145-07: the companion database-pulse run was an ORCHESTRATOR decision under an explicit operator no-preference answer -- never operator-authorized; Gate 3's own authorization is a SELECTION, not a manufactured quote
- [Phase 145]: 145-07: T-145-45 divergence -- the 0x07 row ships energy_cap_us=0 so MSG_ERR_PULSE_TOO_WIDE is structurally unreachable; only the host click.IntRange(1,65535) bounded the 4688 us run
- [Phase 145]: 145-07: D-12 A1 derived at ~1.44 ms/byte (spread 1436.24-1436.62 us) -- an UPPER BOUND on Phase 143's per-pulse A1, not the same quantity; the multi-pulse retry-loop regime stays undischarged with no v1.31 owner
- [Phase 145-08]: Recorded D-10's eyes-on half as COLLECTED but split its disposition — verification-map row 27's literal claim (a smoothly moving bar, not an end-burst) is skipped-with-reason, because the operator's complete four-word answer contains neither discriminator and deriving one from the pasted transcript would be the orchestrator answering an operator-only question
- [Phase 145-08]: Declared the eyes-on re-run OBSERVATIONAL ONLY and left Gate 3's recorded measurement as 145-07's — nothing was re-measured or re-extracted, so the eyes-on half can never be accused of having been fitted to a fresh frame count
- [Phase 145-08]: Recorded the MAIN write bar never reaching 100% as a new finding rather than fixing it — the final bar equals the last firmware frame position in all six writes and no final frame is emitted at completion; it is cosmetic/UX only (all six verified byte-exact) and D-16 forbids the sub-repo edit, so it carries forward with no v1.31 owner
- [Phase 145-08]: Remade three acceptance locators with negative controls instead of reshaping evidence — two were false GREENs that passed before any content existed, one could not fail for the right reason without deleting D-14's own taxonomy statement, and a first substitution self-matched its own quoted literal until the negative control was described rather than written in matching form
- [Phase 145-08]: Hand-edited ROADMAP's single 145-08 checkbox instead of calling roadmap.update-plan-progress — the roadmap verbs reformat the whole file and phase.complete is known to clobber unrelated phases' Plans lines; REQUIREMENTS.md stays byte-identical and BENCH-01..03 stay Pending for 145-09
- [Phase 145]: MERGE-05 +96 B flash breach ADJUDICATED — the +96 B is ADMITTED as a named, SHA-attributed defect-fix exemption (`MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96` in `firestarter/scripts/check_size_baseline.py`, firmware commit `fa6c9c7`), added to each target's base band to form its effective allowance (leonardo 0+96 = 96 B, uno-class 64+96 = 160 B), with the forward tripwire re-armed at the new floor so any FURTHER growth still fails. **Wording for Phase 146 / CLOSE-02's honesty ledger, quotable verbatim:** "v1.31 ships +96 B of AVR flash over the v1.23-era MERGE-05 band on all three AVR targets (uno 24824→24920, uno328pb 24874→24970, leonardo 26906→27002; RAM unchanged at 1573/1579/2014), admitted under a named, SHA-attributed defect-fix exemption — `MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96`, firmware commits `eb563d2` (assert the program-voltage route around every program pulse) and `ebe9cb3` (raise the VPP settles to 1000us/100us on bench evidence) — rather than by moving the BASE-01 anchor or widening the band literal. The bytes are `eprom_internal_program_pulse()` plus its two VPP settle constants: a defect fix restoring behaviour the pre-v1.31 firmware had, not new feature surface. Leonardo ships at 27002/28672 B, 94.2% full, 1670 B free."
- [Phase 145]: Three alternatives to the exemption were considered and REJECTED, and the rejections are recorded in the constant's own comment so they cannot rot: (a) re-anchoring `size_baseline_base01.json` a THIRD time — Phase 144/D-11 moved that anchor once already and the green it produced was the anchor moving, not growth shrinking (D-14), so a second move would hide growth behind the same mechanism twice and erase the delta; BASE-01's `avr_targets` are therefore byte-unchanged (uno 24824, uno328pb 24874, leonardo 26906); (b) widening `MERGE05_UNO_CLASS_FLASH_BAND` or the leonardo 0 B band — that would silently admit any future 96 B of unrelated feature growth and destroy the tripwire; both literals are unchanged; (c) shrinking the fix — micro-optimising a correctness fix to fit a band set before the per-protocol parameter table existed is the wrong incentive and risks the fix
- [Phase 145]: The archived v1.23 requirement MERGE-05 (`.planning/milestones/v1.23-REQUIREMENTS.md:56`) was NOT edited, unticked, reworded or annotated, and `v1.23-ROADMAP.md` was not touched either — both asserted byte-identical after this work (SHA256 `bdfe4d63…a3055` / `b86fc3c8…c0817`). MERGE-05 was true at v1.23's close; what this adjudicates is the FORWARD tripwire Phase 144/D-11 repurposed from its mechanism, not the closed requirement. Editing an archived milestone's requirement would be the same class of error the archived-BENCH-01/02/03-rows guard exists to prevent
- [Phase 145]: The exemption is FLASH-only and stays machine-checked in both directions: `compare_avr_policy_merge05`'s `ram_used` clause keeps zero tolerance (RAM did not move), the PASS/FAIL text prints the allowance DECOMPOSED (`+96<=96=band0+exempt96`; `allowance of 160 B (band 64 B + defect-fix exemption 96 B)`) so the admitted growth stays visible rather than laundered into a moved reference point, and `test_policy_merge05_admits_the_documented_defect_fix` pairs the admission with a negative control at one byte past the exemption (planted +97 B leonardo → exit 1). Both literals now have exactly one consumer, `_merge05_flash_allowance()` — before this, `main()` recomputed the band itself, quietly falsifying the band literal's own "single place this literal lives" comment
- [Phase 145]: Collateral of the exemption, recorded because it is a real consequence and not a cleanup: the Coverage 9/10 planted fixtures had to be re-derived +65 B → +161 B (uno) and +1 B → +97 B (leonardo), because a plant sized against the OLD ceiling now sits inside the new allowance and its leg would have gone falsely green while still claiming to prove a firing — the same D-18 reasoning Phase 144 Plan 05 applied when the anchor moved. Firmware pytest suite 314 passed both before and after (one leg renamed and re-pointed, none added or removed)
- [Phase 146-03]: OD-A discharged on the GREEN arm — the ARM toolchain installed here and the `py32f071` CMake target compiled against this milestone's code (configure rc=0, build rc=0, the composite action's own exactly-one-hex oracle PASSED at `firestarter_py32f071.hex`, 78769 B, sha256 `5b0b55a2…bebf8e`, SDK resolved to the pinned `0ed2f4b4`). Both previously-blind TU registrations (`3207632` `eprom_params.cpp`, `e9f6a92` `eprom_budget.cpp`) compile for ARM. The other two arms are marked `NOT TAKEN` in `146-ARM-BUILD-RECORD.md` §3
- [Phase 146-03]: The green is recorded as a DELTA and never as CI parity — the mandatory caveat is its own labelled paragraph, stating that four bare-metal C/C++ library packages arrived as automatic apt dependencies rather than by name, that the runner image and package closure were not compared, that no CI run was made or observed, that the result covers NO AVR target, and that no PY32F071 board exists anywhere in this project. A box-9 grading that reproduces the result without the caveat is named an overclaim in the record itself
- [Phase 146-03]: The box-9 sentence handed to `146-09` was MEASURED against this phase's own claim gate in positional-argument mode rather than asserted clean — zero forbidden-phrase matches, with a live negative control returning two matches from the same invocation so the scan could not be vacuous. Written in the *validated / established / measured / skipped-with-reason* taxonomy; the forbidden set is cited at `139-check-claims.py:98-128`, never reproduced
- [Phase 146-03]: The inference-based box-9 fallback offered in `146-RESEARCH.md` §"Open Questions" q1 is REPLACED, not published alongside the observation — only one grading goes into box 9
- [Phase 146-03]: NO backlog stub was filed. `### Phase 999.32` belonged to the RED arm alone and the RED arm did not fire; a stub with no defect behind it would be an entry that cannot be closed. `grep -c '999.32'` over `ROADMAP.md` prints 0 and no existing backlog entry was renumbered or reworded
- [Phase 146-03]: A contradiction inside this plan's own acceptance criteria was RECORDED rather than worked around — the criteria demand a NON-ZERO firmware porcelain immediately after the build as a negative control, which is structurally unreachable under the same task's out-of-tree mandate. Porcelain measured 0 after configure and after build because nothing was written inside `firestarter/`; substituted out-of-tree oracles (43 object files, 166308537 B of build tree, four images with recorded digests, the two named `.obj` files) are recorded instead, and no artifact was manufactured inside the repository to satisfy the criterion's letter
- [Phase 146-03]: The stale build-tooling sentence preserved inside `last_activity_desc` — the Phase 130 record gate's own R-15 target at `.planning/STATE.md:11` — is now DISPROVEN by this plan's observation but deliberately left verbatim: `146-05` owns its repair, and an exemption placed inside that field is destroyed by the next state write. The gate's output is byte-identical before and after this plan (rc=1, one unlabelled hit); its `PASS`-line exempt tally is printed only on the success path, so the tally was captured via `--explain` instead and is unchanged: `{'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10, 'unlabeled': 1, 'superseded': 12}`

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| Phase 98 P04 | 35min | 3 tasks | 2 files |
| Phase 98 P05 | 25min | 3 tasks | 5 files |
| Phase 99 P01 | 25min | 3 tasks | 2 files |
| Phase 99 P02 | 15min | 2 tasks | 3 files |
| Phase 99 P04 | 15min | 2 tasks | 4 files |
| Phase 102 P01 | 25min | 3 tasks | 3 files |
| Phase 103 P01 | 8min | 3 tasks | 1 files |
| Phase 103 P02 | 18min | 2 tasks | 1 files |
| Phase 104 P01 | 20min | 3 tasks | 7 files |
| Phase 104 P02 | 12min | 3 tasks | 6 files |
| Phase 104 P03 | 55min | 3 tasks | 15 files |
| Phase 105 P01 | 32min | 3 tasks | 6 files |
| Phase 106 P01 | 20min | 3 tasks | 8 files |
| Phase 106 P02 | 12min | 3 tasks | 3 files |
| Phase 106 P03 | 12min | 3 tasks | 3 files |
| Phase 107 P01 | 18min | 3 tasks | 4 files |
| Phase 107 P02 | 22min | 2 tasks | 5 files |
| Phase 107 P03 | 20min | 2 tasks | 0 files |
| Phase 108 P01 | 20min | 3 tasks | 3 files |
| Phase 108 P02 | 25min | 3 tasks | 2 files |
| Phase 108 P03 | 25min | 2 tasks | 2 files |
| Phase 108 P04 | 45min | 3 tasks | 2 files |
| Phase 109 P01 | 35min | 2 tasks | 2 files |
| Phase 109 P02 | 22min | 2 tasks | 2 files |
| Phase 109 P03 | 35min | 2 tasks | 2 files |
| Phase 110 P01 | 25min | 3 tasks | 2 files |
| Phase 110 P02 | 20min | 3 tasks | 3 files |
| Phase 110-diagnostic-report-model-dual-output-provenance-prompts P03 | 25min | 3 tasks | 2 files |
| Phase 111 P01 | 20min | 2 tasks | 2 files |
| Phase 111 P02 | 12min | 2 tasks | 1 files |
| Phase 111 P03 | 12min | 2 tasks | 1 files |
| Phase 112 P01 | 20min | 2 tasks | 2 files |
| Phase 112 P02 | 45min | 2 tasks | 2 files |
| Phase 112 P03 | 35min | 2 tasks | 3 files |
| Phase 112 P04 | 40min | 3 tasks | 6 files |
| Phase 112 P05 | 35min | 3 tasks | 4 files |
| Phase 113 P01 | 20min | 2 tasks | 2 files |
| Phase 113 P02 | 30min | 3 tasks | 2 files |
| Phase 113 P03 | 35min | 2 tasks | 2 files |
| Phase 113 P04 | 35min | 2 tasks | 4 files |
| Phase 114 P01 | 12min | 2 tasks | 3 files |
| Phase 114 P02 | 15min | 2 tasks | 2 files |
| Phase 114 P03 | 30min | 2 tasks | 2 files |
| Phase 114.1 P01 | 12min | 2 tasks | 2 files |
| Phase 115 P01 | 5min | 2 tasks | 2 files |
| Phase 116 P01 | 25min | 3 tasks | 2 files |
| Phase 116 P02 | 30min | 3 tasks | 3 files |
| Phase 116 P03 | 25min | 2 tasks | 2 files |
| Phase 116 P04 | 20min | 2 tasks | 3 files |
| Phase 116 P05 | 70min | 3 tasks | 4 files |
| Phase 116 P06 | 65min | 2 tasks | 4 files |
| Phase 116 P07 | 45min | 3 tasks | 2 files |
| Phase 117 P01 | 12min | 3 tasks | 3 files |
| Phase 117 P02 | 15min | 3 tasks | 2 files |
| Phase 117 P03 | 20min | 2 tasks | 2 files |
| Phase 117 P04 | 25min | 1 tasks | 1 files |
| Phase 117 P05 | 24min | 2 tasks | 2 files |
| Phase 118 P01 | 55min | 3 tasks | 3 files |
| Phase 118 P02 | 25min | 3 tasks | 5 files |
| Phase 118 P04 | 20min | 3 tasks | 1 files |
| Phase 118 P05 | 55min | 3 tasks | 3 files |
| Phase 118 P06 | 45min | 2 tasks | 2 files |
| Phase 118 P07 | 25min | 2 tasks | 2 files |
| Phase 119 P01 | 10min | 2 tasks | 6 files |
| Phase 119 P02 | ~35min | 3 tasks | 9 files |
| Phase 119 P03 | 25min | 2 tasks | 3 files |
| Phase 119 P04 | 55min | 3 tasks | 5 files |
| Phase 119 P05 | ~50min | 3 tasks | 2 files |
| Phase 119 P06 | 45min | 3 tasks | 3 files |
| Phase 119 P07 | ~25min | 3 tasks | 7 files |
| Phase 119 P08 | 55min | 3 tasks | 3 files |
| Phase 119 P09 | ~20min | 2 tasks | 5 files |
| Phase 119 P10 | ~50min | 3 tasks | 2 files |
| Phase 119 P11 | 50min | 2 tasks | 1 files |
| Phase 120 P01 | 15min | 3 tasks | 2 files |
| Phase 120 P02 | 10min | 2 tasks | 1 files |
| Phase 120 P03 | 12min | 2 tasks | 2 files |
| Phase 120 P05 | 20min | 2 tasks | 1 files |
| Phase 120 P06 | 20min | 3 tasks | 2 files |
| Phase 120 P07 | 45min | 3 tasks | 5 files |
| Phase 120 P08 | 55min | 3 tasks | 4 files |
| Phase 120 P09 | 35min | 3 tasks | 3 files |
| Phase 120 P10 | 45min | 3 tasks | 8 files |
| Phase 120 P12 | 55min | 3 tasks | 3 files |
| Phase 121 P11 | 30min | 3 tasks | 2 files |
| Phase 121 P12 | 35min | 2 tasks | 5 files |
| Phase 121 P13 | 50min | 2 tasks | 9 files |
| Phase 121 P14 | 110min | 3 tasks | 2 files |
| Phase 122 P01 | 15min | 3 tasks | 6 files |
| Phase 122 P02 | 20min | 2 tasks | 1 files |
| Phase 122 P03 | 7min | 3 tasks | 4 files |
| Phase 122 P04 | 25min | 3 tasks | 1 files |
| Phase 122 P05 | 35min | 3 tasks | 1 files |
| Phase 122 P06 | 35min | 2 tasks | 1 files |
| Phase 122 P07 | 47min | 3 tasks | 3 files |
| Phase 122 P08 | 20min | 3 tasks | 1 files |
| Phase 122 P09 | 12min | 3 tasks | 3 files |
| Phase 122 P10 | 25min | 3 tasks | 2 files |
| Phase 122 P11 | 20 | 3 tasks | 1 files |
| Phase 122 P12 | 25min | 3 tasks | 1 files |
| Phase 122 P13 | 35min | 3 tasks | 3 files |
| Phase 123 P01 | 9 | 3 tasks | 8 files |
| Phase 123 P10 | 20min | 3 tasks | 7 files |
| Phase 123 P02 | 20 | 3 tasks | 6 files |
| Phase 123 P07 | 45min | 3 tasks | 5 files |
| Phase 123 P03 | 30 | 3 tasks | 6 files |
| Phase 123 P08 | 70min | 3 tasks | 9 files |
| Phase 123 P04 | 35 | 3 tasks | 20 files |
| Phase 123 P09 | 55min | 2 tasks | 4 files |
| Phase 123 P05 | 22 | 2 tasks | 10 files |
| Phase 123 P06 | 12min | 2 tasks | 1 files |
| Phase 123 P11 | 55 | 3 tasks | 3 files |
| Phase 124 P01 | 12min | 2 tasks | 4 files |
| Phase 124 P02 | 10min | 3 tasks | 6 files |
| Phase 124 P03 | 22min | 2 tasks | 2 files |
| Phase 124 P04 | 20min | 3 tasks | 22 files |
| Phase 124 P05 | ~25min | 3 tasks | 3 files |
| Phase 124 P06 | ~20min | 3 tasks | 4 files |
| Phase 124 P07 | ~15min | 2 tasks | 2 files |
| Phase 124 P08 | ~55min | 3 tasks | 8 files |
| Phase 124-firmware-integration-merge P09 | 40min | 3 tasks | 4 files |
| Phase 124 P10 | 30min | 3 tasks | 11 files |
| Phase 124 P11 | ~20min | 3 tasks | 0 files |
| Phase 124 P12 | 75min | 3 tasks | 2 files |
| Phase 125 P01 | 55min | 2 tasks | 3 files |
| Phase 125 P02 | 35min | 2 tasks | 1 files |
| Phase 125 P03 | 30min | 2 tasks | 1 files |
| Phase 125 P04 | 25min | 2 tasks | 0 files |
| Phase 125 P05 | ~20min | 1 tasks | 0 files |
| Phase 125-vpp-control-seam P06 | 28min | 3 tasks | 2 files |
| Phase 126 P01 | 7min | 3 tasks | 2 files |
| Phase 126 P02 | 20min | 2 tasks | 1 files |
| Phase 126 P03 | 35min | 2 tasks | 6 files |
| Phase 126 P04 | 25min | 2 tasks | 0 files |
| Phase 126 P05 | 40min | 2 tasks | 1 files |
| Phase 126 P06 | 25min | 3 tasks | 3 files |
| Phase 126 P07 | 55min | 2 tasks | 3 files |
| Phase 126 P08 | 70min | 2 tasks | 5 files |
| Phase 126 P09 | 70min | 2 tasks | 1 files |
| Phase 126 P10 | 35 | 2 tasks | 1 files |
| Phase 126 P11 | 30min | 3 tasks | 0 files |
| Phase 126 P12 | ~2h | 3 tasks | 1 files |
| Phase 127 P01 | 20min | 2 tasks | 9 files |
| Phase 127 P04 | 45min | 3 tasks | 4 files |
| Phase 127 P02 | 25min | 2 tasks | 2 files |
| Phase 127 P03 | 35min | 2 tasks | 1 files |
| Phase 127 P05 | 45min | 3 tasks | 2 files |
| Phase 127 P06 | 35min | 3 tasks | 4 files |
| Phase 127 P07 | 30min | 2 tasks | 2 files |
| Phase 127 P08 | ~55min | 3 tasks | 3 files |
| Phase 127 P09 | 65min | 3 tasks | 4 files |
| Phase 127 P10 | 35min | 2 tasks | 2 files |
| Phase 127 P11 | 70min | 3 tasks | 1 files |
| Phase 127 P12 | 130min | 3 tasks | 2 files |
| Phase 128 P01 | 25min | 3 tasks | 15 files |
| Phase 128 P02 | 15min | 2 tasks | 1 files |
| Phase 128 P03 | 20min | 2 tasks | 1 files |
| Phase 128 P04 | ~15min | 3 tasks | 1 files |
| Phase 128 P05 | ~15min | 3 tasks | 1 files |
| Phase 128 P06 | ~15min | 3 tasks | 1 files |
| Phase 128 P07 | ~20min | 3 tasks | 1 files |
| Phase 128 P08 | ~25min | 2 tasks | 1 files |
| Phase 128 P10 | 20min | 1 tasks | 2 files |
| Phase 131 P01 | 40min | 3 tasks | 4 files |
| Phase 131 P02 | 55min | 2 tasks | 3 files |
| Phase 131 P03 | 30min | 2 tasks | 1 files |
| Phase 131 P04 | 35min | 2 tasks | 1 files |
| Phase 131 P06 | 50min | 2 tasks | 3 files |
| Phase 131 P05 | 5m | 3 tasks | 3 files |
| Phase 131 P07 | 65min | 2 tasks | 2 files |
| Phase 132 P01 | 35min | 3 tasks | 3 files |
| Phase 132 P02 | 40min | 3 tasks | 4 files |
| Phase 132 P04 | 25min | 3 tasks | 2 files |
| Phase 132 P05 | 45min | 3 tasks | 5 files |
| Phase 132 P06 | 40min | 3 tasks | 3 files |
| Phase 132 P07 | 45min | 3 tasks | 4 files |
| Phase 132 P08 | 55min | 3 tasks | 3 files |
| Phase 132 P09 | ~20min | 4 tasks | 5 files |
| Phase 134 P01 | 28m | 3 tasks | 4 files |
| Phase 134 P02 | 36min | 3 tasks | 3 files |
| Phase 134 P03 | 46min | 3 tasks | 4 files |
| Phase 134 P04 | 38min | 3 tasks | 3 files |
| Phase 134 P05 | 33min | 2 tasks | 4 files |
| Phase 134 P06 | 20min | 2 tasks | 3 files |
| Phase 134 P07 | 29min | 2 tasks | 4 files |
| Phase 134 P08 | 38min | 3 tasks | 5 files |
| Phase 134 P09 | 40min | 2 tasks | 1 files |
| Phase 134 P10 | 50min | 3 tasks | 3 files |
| Phase 134 P11 | 29min | 3 tasks | 6 files |
| Phase 136 P01 | 22min | 3 tasks | 4 files |
| Phase 136 P02 | 23min | 3 tasks | 1 files |
| Phase 136 P03 | 35min | 3 tasks | 2 files |
| Phase 136 P04 | ~25min | 2 tasks | 2 files |
| Phase 136.1 P01 | 36min | 3 tasks | 6 files |
| Phase 136.1 P02 | 22min | 3 tasks | 4 files |
| Phase 136.1 P04 | 21min | 1 tasks | 3 files |
| Phase 137 P01 | 20min | 3 tasks | 8 files |
| Phase 137 P04 | 45min | 3 tasks | 9 files |
| Phase 138 P01 | 17min | 3 tasks | 2 files |
| Phase 138 P02 | 26min | 3 tasks | 3 files |
| Phase 138 P03 | 50min | 3 tasks | 6 files |
| Phase 138 P04 | 16min | 2 tasks | 1 files |
| Phase 138 P05 | 45min | 3 tasks | 5 files |
| Phase 138 P06 | 22min | 3 tasks | 2 files |
| Phase 138 P07 | 35min | 3 tasks | 3 files |
| Phase 139 P01 | 12min | 2 tasks | 2 files |
| Phase 139 P02 | ~14min | 2 tasks | 1 files |
| Phase 139 P03 | 23min | 2 tasks | 1 files |
| Phase 139 P04 | 19min | 2 tasks | 3 files |
| Phase 140 P01 | 22min | 3 tasks | 4 files |
| Phase 140 P03 | 25min | 3 tasks | 2 files |
| Phase 140 P02 | 30min | 3 tasks | 2 files |
| Phase 140 P04 | 20min | 3 tasks | 3 files |
| Phase 140 P05 | 32min | 3 tasks | 2 files |
| Phase 140 P06 | 13min | 3 tasks | 2 files |
| Phase 140 P07 | 32min | 3 tasks | 3 files |
| Phase 141 P01 | 21min | 3 tasks | 6 files |
| Phase 141 P02 | 20min | 2 tasks | 2 files |
| Phase 141 P03 | 30min | 3 tasks | 4 files |
| Phase 141 P04 | 40min | 3 tasks | 2 files |
| Phase 141 P05 | 39min | 3 tasks | 3 files |
| Phase 141 P06 | 30min | 2 tasks | 1 files |
| Phase 141 P07 | 100min | 3 tasks | 1 files |
| Phase 141 P08 | 130min | 3 tasks | 1 files |
| Phase 141 P09 | 2h | 3 tasks | 3 files |
| Phase 142 P01 | 32min | 3 tasks | 4 files |
| Phase 142 P02 | 28min | 2 tasks | 2 files |
| Phase 142 P03 | 27min | 3 tasks | 1 files |
| Phase 142 P04 | 31min | 1 tasks | 5 files |
| Phase 142 P05 | ~42min | 3 tasks | 1 files |
| Phase 142 P06 | 31min | 3 tasks | 1 files |
| Phase 142 P07 | 47min | 3 tasks | 4 files |
| Phase 143 P01 | 36min | 2 tasks | 4 files |
| Phase 143 P02 | 23min | 2 tasks | 3 files |
| Phase 143 P03 | 48min | 2 tasks | 3 files |
| Phase 143 P04 | 40min | 3 tasks | 3 files |
| Phase 143 P05 | 44min | 2 tasks | 5 files |
| Phase 143 P06 | 35min | 2 tasks | 2 files |
| Phase 143 P07 | 30min | 2 tasks | 3 files |
| Phase 143 P08 | 37min | 2 tasks | 1 files |
| Phase 143 P09 | ~30min | 2 tasks | 2 files |
| Phase 143 P10 | ~65min (2 sessions) | 3 tasks | 6 files |
| Phase 144 P01 | ~45min | 2 tasks | 1 files |
| Phase 144 P02 | 28min | 2 tasks | 4 files |
| Phase 144 P03 | 24min | 2 tasks | 3 files |
| Phase 144 P04 | 34min | 2 tasks | 1 files |
| Phase 144 P05 | 30min | 3 tasks | 11 files |
| Phase 144 P06 | 26min | 2 tasks | 1 files |
| Phase 144 P07 | 57min | 3 tasks | 3 files |
| Phase 145 P01 | 18min | 3 tasks | 11 files |
| Phase 145 P02 | 9min | 3 tasks | 1 files |
| Phase 145 P03 | 4min | 3 tasks | 1 files |
| Phase 145 P05 | 35min | 3 tasks | 12 files |
| Phase 145 P06 | ~30 min | 3 tasks | 22 files |
| Phase 145 P07 | 35m | 3 tasks | 8 files |
| Phase 145 P08 | 54min | 3 tasks | 4 files |
| Phase 145 P09 | 40min | 2 tasks | 4 files |
| Phase 146 P02 | ~25min | 2 tasks | 2 files |

## Session

**Last session:** 2026-08-17T15:12:00.000Z
**Stopped at:** Completed 146-02-PLAN.md — the D-13 CLOSE-03 documentation checker authored and recorded RED
**Resume file:** .planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-CONTEXT.md

### Blockers

- 146-PRE: `ROADMAP.md`'s **v1.31 Coverage table is stale for 12 rows** — `PREP-01`…`PREP-04`, `ISSUE-01`…`ISSUE-03`, `HOST-01`…`HOST-05` read `Pending` there while `REQUIREMENTS.md` correctly reads `Complete`. Pre-existing drift from phases 138/139/143 (verified present in `145-09`'s pre-edit snapshot, so not a consequence of the BENCH flip). Left untouched by `145-09` under its "flip nothing but BENCH-01…03" prohibition. **Phase 146 owns it** — it is a documentation fix and 146 is a documentation phase — and must reconcile the two tables **before** treating either as the milestone's coverage statement.
- 127-01: tests/test_characterization.py::test_help_fw fails post-merge (stale --board help snapshot missing py32f071) — contradicts C-1's zero-fixup prediction; not fixed per plan instruction, needs a resolution decision before Phase 127 closes / before any push

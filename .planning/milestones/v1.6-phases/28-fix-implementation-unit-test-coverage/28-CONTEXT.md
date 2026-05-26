# Phase 28: Fix Implementation + Unit Test Coverage — Context

**Re-iteration gathered:** 2026-05-26
**Original gathered:** 2026-05-21 (now superseded — see appendix at bottom)
**Status:** Re-iteration ready for planning
**Source:** /gsd-discuss-phase 28 (Auto Mode — gray areas auto-resolved against Plan 27-05 fix sketch v2 + GATE-1.6 v2 reassessment; no AskUserQuestion prompts per harness Auto Mode)

---

## Phase 28 Re-iteration (2026-05-26) — Split-Scope Revert

**Trigger:** Phase 29 Wave B Attempt 2 (2026-05-22 PM) FAIL → D-07 milestone-reopens. Phase 27 re-opened, closed at higher fidelity 2026-05-26 (Plan 27-05). Dual-cause disposition confirmed: Outcome A for Leonardo (Phase 28 fix commits `437339b6` + `4f205e58` introduced a separate 99% zeros failure mode), Outcome B / independent for uno328pb (`.hex` SHA identity `d9e51b7e…` byte-identical pre-fix and post-fix — regression structurally CANNOT be Phase 28-induced; pre-existing hardware-level issue). Phase 28 re-iteration UNBLOCKED with split-scope per fix sketch v2 (see `.planning/v1.6-EVIDENCE.md §"Fix sketch v2 (Phase 28 re-iteration hand-off)"` at line 507).

<domain>
### Phase Boundary (Re-iteration)

Phase 28 re-iteration delivers **a pure revert of the broken Phase 28 fix commits on `firestarter/v1.6-read-bug` to restore the Leonardo read-path to its pre-Phase-28 shape (Phase 26 baseline ~2.1% structured-data jitter), plus a desk-side cross-board `.hex` SHA identity check satisfying GATE-1.6 v2 Axis 4**. No new "re-fix" attempt is in scope — the original 64KB read-bug remains (deferred to a future milestone, likely v1.8, once the parked instrumented-build template can be activated against a stable v1.7 shield-detect substrate). The uno328pb regression is explicitly NOT a Phase 28 deliverable and hands off to operator-level hardware diagnosis as a separate workstream.

The fix-commit window is `bc0f5ac..4f205e58` (3 commits on `firestarter/v1.6-read-bug`): `fdb1ed5` (RED unity scaffold for the now-broken approach), `437339b6` (masked PORTx-clear in `rurp_set_data_input`), and `4f205e58` (`_NOP()` settling in `rurp_read_data_buffer` — current HEAD). Per fix sketch v2 bisection-aware recommendation, revert `437339b6` ALONE first (the more likely primary regression source — PORTx-clear changes bus-drive timing such that `_NOP()` settling samples the bus after chip output has collapsed), then bench-confirm shape restoration; if still zeros-dominant, also revert `4f205e58`. The desk-side scope of Phase 28 re-iteration closes once one or both reverts are landed; bench confirmation moves to Phase 29 v2.

**In scope (re-iteration):**
- Land `git revert 437339b6` on `firestarter/v1.6-read-bug` (Plan 28-03; desk-side, autonomous). Single atomic revert commit with subject `Revert "fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input"`. Commit-message footer cites Plan 27-05 final verdict + Plan 27-04 bench A/B outcome.
- Rebuild all three firmware envs (`pio run -e uno`, `-e leonardo`, `-e uno328pb`). Capture per-board `.hex` SHA-256 pre-revert (HEAD = `4f205e58`) AND post-revert (HEAD = revert-of-`437339b6`).
- GATE-1.6 v2 Axis 4 desk-side check: assert Uno `.hex` SHA byte-identical across the revert (no source touched; the revert only edits `leonardo_rurp_shield.cpp`); assert uno328pb `.hex` SHA byte-identical (same rationale; `d9e51b7e…` baseline holds); assert Leonardo `.hex` SHA differs by the revert delta and matches the `fdb1ed5` pre-fix Leonardo `.hex` SHA (the bug-shape baseline).
- Conditional second revert: Plan 28-04 (operator-on-bench gating signal — drafted-but-not-executed by default in Phase 28 desk-side wave). If bench sideload of the 28-03 revert in Phase 29 v2 shows Leonardo shape returns to structured-data + ~0.44% jitter — close 28-04 as not-needed. If shape stays zeros-dominant — land `git revert 4f205e58` in 28-04 (atomic commit, same footer pattern, .hex re-capture).
- Unity test pruning: remove `test_rurp_set_data_input_clears_data_pullups_leonardo` from `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` (assertion exercises behavior introduced by the now-reverted `437339b6`; post-revert the assertion would fail — and the asserted behavior is no longer the intended fix shape). Keep `test_rurp_read_data_buffer_reassembles_data_bus` IF its bit-reassembly assertions remain intact post-revert (researcher confirms — `4f205e58` only added `_NOP()` instructions, not bit-reassembly logic; reverting it leaves the reassembly code unchanged from `bc0f5ac` shape).
- Update `platformio.ini` `[env:native].test_filter` allowlist if the directory becomes empty (i.e., if both Unity tests are deleted). Otherwise no allowlist edit needed.
- Append `## Phase 28 Re-iteration — Revert Commits (2026-05-26)` H2 section to `.planning/v1.6-EVIDENCE.md` AFTER `### Re-open final verdict — closing the loop` (line 560) and BEFORE `## Verdict` (line 562). Section records: revert commit SHA(s), pre/post-revert per-board `.hex` SHA-256 table (GATE-1.6 v2 Axis 4 desk-side evidence), test-pruning rationale, Plan 28-04 conditional placeholder, and a Phase 29 v2 bench placeholder.
- Update ROADMAP.md `[x] Phase 28` checkbox to reflect re-iteration status (e.g., add `(re-iterated 2026-05-26 — split-scope: Leonardo revert)` annotation per project convention).

**Out of scope (re-iteration):**
- Any new "re-fix" attempt within Phase 28 re-iteration — no fresh PORTx-clear-with-guard, no `_NOP()` count tuning, no instrumented-build activation. The original ~2.1% Leonardo jitter remains. Proper read-bug fix deferred to v1.8+ once v1.7's shield-detect substrate + the parked Plan 27-05 instrumented-build template can be activated cleanly.
- uno328pb regression — operator workstream (Rev 2.2 socket contact wear, USB-UART bridge buffering, ATmega328PB Case A shared bus-read timing audit). The `.hex` SHA identity falsifier (`d9e51b7e…`) over-determines that Phase 28 cannot fix this. Permanent memory `[[project_uno328pb_bench_instability_27_04]]` is the diagnostic substrate; mention but do not address in Phase 28.
- Activation of the Plan 27-05 parked instrumented-build template (`-D RCA_INSTRUMENT_READ_TRACE=1`) — declared as PARKED in Plan 27-05; activated only when a future re-fix attempt is on the agenda (out of Phase 28 re-iteration scope by D-10v2).
- Phase 30 v1.6 milestone close paperwork re-scope — Phase 30 will re-discuss separately (the milestone goal narrows from "fix the read bug" to "ship diagnostic + revert broken fix; defer fix to v1.8"). Mention the implication here, propagate to Phase 30.
- Sub-repo `v1.6-read-bug` → `beta` merge — Phase 29 v2 still owns the bench gate before promotion. Re-iteration ends with the sub-repo branch still at the revert commit, not merged.
- Bench validation N=5 per-board consistency-check — Phase 29 v2 owns the bench half of GATE-1.6 v2 Axis 4; Phase 28 re-iteration only closes the desk-side `.hex` SHA identity sub-check.
- Documentation drift correction (the 5 locations claiming Leonardo 1024-B) — Phase 30 paperwork per the original D-05 (carried forward).
- Original `## Phase 28 — Fix Commit References` section in `.planning/v1.6-EVIDENCE.md` (lines 112-186) — preserved byte-identical as the audit trail of the broken approach. Anti-pattern immutability guard applies (matches the Plan 27-05 SHA-256 guard pattern).
- Host-side `firestarter_app` changes — RCA Re-open confirms the regression is firmware-side; the host CLI consistency-check infrastructure from Phase 26 is untouched.
- Any v1.7 / shield-detect work — separate milestone, shipped 2026-05-26.

</domain>

<decisions>
### Implementation Decisions (Re-iteration)

#### Revert shape

- **D-09v2: Bisection-first per-commit revert order — revert `437339b6` ALONE in Plan 28-03; defer the second revert (`4f205e58`) to a conditional Plan 28-04 gated on Phase 29 v2 bench sideload result.**
  Per Plan 27-05 fix sketch v2 (`v1.6-EVIDENCE.md:513`): "revert `437339b6` OR `4f205e58` SEPARATELY — not both at once — to bisect which commit is the primary regression source." `437339b6` (masked PORTx-clear) is selected as the first revert target because the fix sketch v2 hypothesizes the PORTx-clear changes bus-drive timing such that the subsequent `_NOP()` settling samples the bus after chip output has collapsed — making PORTx-clear the more likely primary fault driver.

  **Output the planner needs:** Plan 28-03 task list specifies a single `git revert 437339b6` atomic commit on `firestarter/v1.6-read-bug`; Plan 28-04 is drafted-but-not-executed (per v1 Phase 27 Wave B precedent), executes only if Phase 29 v2 bench confirms continued zeros-dominant shape.

#### Re-fix attempt

- **D-10v2: Pure revert deliverable, no re-fix attempt within Phase 28 re-iteration.**
  Phase 28 re-iteration restores the Leonardo read-path to pre-Phase-28 shape (Phase 26 baseline ~2.1% structured-data jitter on 64KB reads); the original 64KB jitter bug remains unfixed. Rationale:
  - The Phase 28 v1 attempt burned the "confident-feeling read-path fix without per-rev / cross-board instrumentation" budget (commits `437339b6` + `4f205e58` confidently mirrored the Uno `df5fb44` shape and shipped under three-axis-green GATE-1.6 v1, yet produced a qualitatively worse failure mode on Leonardo + masked the independent uno328pb pre-existing regression). Burning the budget again on a similar confidence-only re-fix attempt would be unwise.
  - The Plan 27-05 parked instrumented-build template (`-D RCA_INSTRUMENT_READ_TRACE=1`, ADC-band-tagged read traces per `firestarter/include/rurp_pinout.h:66-68`, per-rev gating via `rurp_detect_hardware_revision()`) is the proper substrate for a re-fix attempt — but its activation depends on v1.7's `REVISION_2_3` / `REVISION_UNKNOWN` enum additions + `ADC_BAND_R41_*` constants + per-rev capability matrix in `.planning/v1.7-SHIELD-REVS.md §6` being landed on the firestarter `beta`/`main` branches that Phase 28 cuts from. As of 2026-05-26, those landed in v1.7 but the substrate has not been forward-merged onto `firestarter/v1.6-read-bug`.
  - v1.6 milestone goal re-scopes (D-17v2): "fix the read bug" → "ship `dev consistency-check` diagnostic + revert broken fix; defer read-bug fix to v1.8".

  **Output the planner needs:** Plan 28-03 does NOT include any new fix attempt; Plan 28-04 (conditional second revert) also does NOT. The re-fix is a future-milestone deliverable.

#### GATE-1.6 v2 Axis 4 desk-side closure

- **D-11v2: `.hex` SHA identity check as the desk-side GATE-1.6 v2 Axis 4 sub-check.**
  Per Plan 27-05 `### GATE-1.6 v2 reassessment` (`v1.6-EVIDENCE.md:530`): the new mandatory sub-check is "build the OTHER board's firmware at the proposed fix-tag AND at the pre-fix tag and compare `.hex` SHA-256 — a byte-identical `.hex` across the fix window on a board whose source file was NOT touched means that board's regression (if any) is provably NOT fix-induced". Apply to Phase 28 re-iteration as follows:
  - Pre-revert capture (current `firestarter/v1.6-read-bug` HEAD = `4f205e58`): build all three envs, record `sha256sum .pio/build/{uno,leonardo,uno328pb}/firmware.hex`.
  - Post-revert capture (after `git revert 437339b6`): rebuild all three envs, record the same three SHA-256 sums.
  - Assertions: (a) Uno `.hex` SHA byte-identical pre/post (no source touched — `uno_rurp_shield.cpp` not edited); (b) uno328pb `.hex` SHA byte-identical pre/post AND matches the pre-existing `d9e51b7e…` baseline (no source touched — uses Uno's pin/port shape per `firestarter/include/uno_rurp_shield.h`); (c) Leonardo `.hex` SHA differs (the revert removes the PORTx-clear block) AND should match the `fdb1ed5` pre-fix Leonardo `.hex` SHA (the Phase 26 baseline shape — verifiable by checking out `bc0f5ac` or `fdb1ed5` and building Leonardo).
  - Recording: pre + post `.hex` SHA table appended to the new `## Phase 28 Re-iteration — Revert Commits` H2 section in `.planning/v1.6-EVIDENCE.md`.

  Rationale: closes the desk-side half of GATE-1.6 v2 Axis 4 in Phase 28 re-iteration; the bench half (N=5 per-board consistency-check) is Phase 29 v2's gate. The desk-side `.hex` SHA identity is an over-determining falsification argument for the uno328pb branch independence and a cheap regression guard for the Uno branch.

#### Unity test handling

- **D-12v2: Prune `test_rurp_set_data_input_clears_data_pullups_leonardo`; keep `test_rurp_read_data_buffer_reassembles_data_bus` if its assertions remain intact post-revert.**
  - The pullup-clearing assertion test was committed in Wave A (Plan 28-01 RED scaffold; subject: `test(leonardo): RED unity scaffold for rurp_set_data_input pullup clearing (FIX-02)`; commit `fdb1ed5`). It asserted PORTD/PORTC/PORTE data-bit pullups are cleared after `rurp_set_data_input()` — behavior introduced by `437339b6`. Post-revert, that assertion would FAIL (the PORTx-clear is gone). Two options: (a) delete the test entirely since the asserted behavior is no longer the intended fix shape; (b) keep the test as `expected_fail` documentation of "behavior we know we ultimately want once a proper re-fix lands". Recommended: **option (a) delete**. The test as a tombstone introduces ongoing CI noise; deleting is cleaner; the asserted behavior shape is fully documented in `v1.6-EVIDENCE.md §"Fix sketch v2"` for whoever picks up the v1.8 re-fix.
  - The bit-reassembly test `test_rurp_read_data_buffer_reassembles_data_bus` (per original CONTEXT.md D-02) — researcher checks whether it exists in the codebase first. If it exists, keep it: `4f205e58` only added `_NOP()` instructions, not bit-reassembly changes; the reassembly logic is unchanged from `bc0f5ac` shape and the test should pass post-revert as a regression guard. If it does NOT exist (was deferred per the original CONTEXT.md `<specifics>` Claude's-discretion note), no action needed.
  - If the test directory `firestarter/test/native/avr/test_data_input/` becomes empty after deletion, remove the directory AND remove the `native/avr/test_data_input` entry from `platformio.ini [env:native].test_filter`. If the bit-reassembly test stays, keep the directory + allowlist entry.

  **Output the planner needs:** Plan 28-03 task list specifies the test deletion as a co-bundled change in the revert commit OR as a follow-up commit on the same plan (researcher decides — a single revert commit is cleaner; a follow-up `test(leonardo): remove pullup-clear assertion superseded by Phase 27 re-open revert` commit is more atomically clear). Recommended: separate commit.

#### Plan structure

- **D-13v2: Plans 28-03 (desk-side, autonomous, primary) + 28-04 (drafted-but-not-executed, conditional second revert).**
  Mirrors the v1 Phase 27 Wave A/B drafted-but-not-executed pattern (Plan 27-02 was the bench-instrumentation plan that did not fire). Each plan's atomic artifact:
  - **Plan 28-03 — Wave A desk-side (autonomous):** Revert `437339b6` + capture `.hex` SHA pre/post for all three envs + Unity test pruning + EVIDENCE.md append `## Phase 28 Re-iteration — Revert Commits` section + ROADMAP.md re-iteration annotation. Closes the FIX-01 + FIX-02 re-iteration deliverables; FIX-03 (bench gate) carries to Phase 29 v2.
  - **Plan 28-04 — Wave B desk-side conditional (drafted-but-not-executed by default):** Activates only if Phase 29 v2 bench sideload of 28-03 shows Leonardo shape still zeros-dominant. Lands a second `git revert 4f205e58` atomic commit, re-captures `.hex` SHAs, appends to the EVIDENCE.md re-iteration section. Verifier emits `wave_b_needed: false` by default (Phase 29 v2 sideload outcome flips this if needed).

  Rationale:
  - **Matches v1 phase pattern with conditional Wave B.** Phase 27 Plans 27-01 + 27-02 + later 27-03/04/05 used the same drafted-but-not-executed + conditional-activate-on-bench pattern; Phase 28 re-iteration reuses it.
  - **Bisection clarity beats efficiency.** Reverting both at once would close Phase 28 re-iteration in one plan, but loses the bisection signal (which commit was primary?). Keeping the second revert conditional preserves the diagnostic question for the eventual v1.8 re-fix work.

  **Output the planner needs:** Two PLAN.md files (28-03-PLAN.md primary; 28-04-PLAN.md conditional shell with explicit "wave_b_needed: false" default verdict).

#### EVIDENCE.md append placement

- **D-14v2: New `## Phase 28 Re-iteration — Revert Commits (2026-05-26)` H2 section appended AFTER `### Re-open final verdict — closing the loop` (currently the last H3 under `## Phase 27 — RCA Re-open Findings (2026-05-26)`, at `v1.6-EVIDENCE.md:544-560`) and BEFORE `## Verdict` (line 562).**
  Original `## Phase 28 — Fix Commit References` H2 section (lines 112-186) is preserved byte-identical as audit trail. Anti-pattern immutability guard SHA-256 capture for the original Phase 28 section recommended (mirrors Plan 27-05's three anti-pattern guards).

  Section body for the new H2:
  - Revert commit SHA(s), date, author, commit-message subject.
  - Pre-revert + post-revert per-board `.hex` SHA-256 table (GATE-1.6 v2 Axis 4 desk-side evidence).
  - Unity test deletion rationale + before/after `firestarter/test/native/avr/` directory state.
  - Plan 28-04 conditional placeholder (`wave_b_needed: false` until Phase 29 v2 result flips it).
  - Phase 29 v2 bench placeholder (`<!-- Phase 29 v2 appends post-revert bench verification here. -->`).

  Rationale: preserves the file's append-only convention; the v2 H2 sits chronologically between the re-open closure (which UNBLOCKED it) and the eventual Phase 29 v2 verdict.

#### uno328pb deferral

- **D-15v2: Phase 28 re-iteration does NOT touch uno328pb; the regression is operator-workstream-bound.**
  Per Plan 27-04 + 27-05: the `.hex` SHA identity `d9e51b7e…` (pre-Phase-28 = post-Phase-28 uno328pb `.hex`) over-determines that Phase 28's source edits cannot have caused the uno328pb regression. The regression is structurally independent and pre-existing. Candidate causes for the operator workstream (NOT Phase 28's job): Rev 2.2 socket contact wear, USB-UART bridge buffering interaction with ATmega328PB Case A, USB-CDC vs UART path latency, RX buffer stalls under sustained 250kbaud read traffic. Permanent memory `[[project_uno328pb_bench_instability_27_04]]` is the diagnostic substrate.

  Phase 28 re-iteration explicitly does NOT include uno328pb-specific source edits, uno328pb-specific test changes, or uno328pb-specific evidence appends — the only uno328pb touchpoint is the `.hex` SHA identity check (D-11v2) which is read-only verification, not a code change.

  **Output the planner needs:** Plan 28-03 task list explicitly marks "uno328pb: read-only `.hex` SHA capture; no source/test/EVIDENCE-specific-row edits".

#### Goal re-scope (carries to Phase 30)

- **D-17v2: v1.6 milestone goal narrows from "fix the read bug" to "ship `dev consistency-check` diagnostic + revert broken Phase 28 fix; defer read-bug fix to v1.8".**
  This re-scope decision is logged here but NOT propagated within Phase 28 — Phase 30 will own the PROJECT.md / MILESTONES.md / ROADMAP.md re-scope paperwork in its own re-discussion. Phase 28 re-iteration's deliverable is the technical substrate (the revert + Axis 4 desk-side evidence); Phase 30 narrates the milestone implication.

  Implication for downstream agents: when researcher + planner read this CONTEXT.md, they understand that "Phase 28 success" means "revert lands cleanly + Axis 4 desk-side passes" — NOT "Leonardo 64KB reads return byte-identical SHAs across N=5 consistency-check runs". The latter is no longer a Phase 28 close criterion; it folds into the deferred v1.8 milestone.

#### Carried forward from original CONTEXT.md (still apply)

- **D-03 (carried):** `firestarter/v1.6-read-bug` is the working branch; the revert lands on this branch. No sub-repo branch changes within Phase 28 re-iteration.
- **D-05 (carried):** Documentation drift correction stays deferred to Phase 30 paperwork. `firestarter/platformio.ini:64-65` Leonardo `DATA_BUFFER_SIZE=512` stays UNTOUCHED (the buffer-size question is not the read-bug discriminator; the revert doesn't affect it).
- **D-06 (carried with re-iteration footer):** Each revert commit message footer cites Plan 27-05 + Plan 27-04 outcome in addition to the original RCA footer pattern. Footer template:
  ```
  Reverts: <broken-commit-sha> "<broken-commit-subject>"
  RCA re-open: .planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Re-open Findings (2026-05-26)"
  Verdict: dual-cause (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb pre-existing)
  Fix sketch: .planning/v1.6-EVIDENCE.md §"Fix sketch v2 (Phase 28 re-iteration hand-off)"
  GATE-1.6 v2: .planning/v1.6-EVIDENCE.md §"GATE-1.6 v2 reassessment" (Axis 4 desk-side passes; bench gate in Phase 29 v2)
  ```
- **D-07 (carried, modified):** `.hex` size tracking pattern stays; now extended to include SHA-256 not just byte count (Axis 4 sub-check requires SHA-256 identity, which is stronger than size).
- **D-08 (carried, modified):** Same EVIDENCE.md append pattern; new H2 section per D-14v2.

</decisions>

<canonical_refs>
### Canonical References (Re-iteration)

**Downstream agents MUST read these before planning or implementing the re-iteration.**

#### Primary inputs (Plan 27 re-open verdict)
- `.planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Re-open Findings (2026-05-26)"` (line 378) — the full re-open H2 section. THE primary input.
- `.planning/v1.6-EVIDENCE.md §"Fix sketch v2 (Phase 28 re-iteration hand-off)"` (line 507) — split-scope outcome-branched fix recommendation; names commits `437339b6` + `4f205e58` and the bisection-first revert order.
- `.planning/v1.6-EVIDENCE.md §"GATE-1.6 v2 reassessment"` (line 530) — four-axis check; Axis 4 mandatory `.hex` SHA identity sub-check.
- `.planning/v1.6-EVIDENCE.md §"Re-open final verdict — closing the loop"` (line 544) — `re_open_status: closed` + Phase 28 first-task narrative.
- `.planning/phases/27-root-cause-analysis/27-05-SUMMARY.md` — Plan 27-05 synthesis; key-decisions enumerate the four locked decisions for Phase 28 re-iteration.

#### Bench A/B + hypothesis context
- `.planning/phases/27-root-cause-analysis/27-04-SUMMARY.md` — Plan 27-04 bench A/B test: Outcome A confirmed for Leonardo (pre-fix `fdb1ed5` = structured data + 0.44% jitter; post-fix `4f205e58` = 99.0% zeros + 0.08% jitter + 5-distinct-SHAs); Outcome B independent for uno328pb (`.hex` SHA identity `d9e51b7e…`).
- `.planning/phases/27-root-cause-analysis/27-03-SUMMARY.md` — Plan 27-03 v2 hypothesis table (8 rows: H1-H7 re-evaluated + H8 NEW CANDIDATE).

#### Original Phase 28 audit trail (preserved, do not edit)
- `.planning/v1.6-EVIDENCE.md §"Phase 28 — Fix Commit References"` (lines 112-186) — original commit references for the broken approach; immutability guard applies.
- `.planning/phases/28-fix-implementation-unit-test-coverage/28-01-PLAN.md` + `28-02-PLAN.md` — original (now-superseded) plans.
- `.planning/phases/28-fix-implementation-unit-test-coverage/28-01-SUMMARY.md` + `28-02-SUMMARY.md` — original plan summaries.

#### Sub-repo source-of-truth
- `firestarter/v1.6-read-bug` HEAD = `4f205e58` (CONFIRMED via Plan 27-05 sub-repo guard). Re-iteration first task: `git revert 437339b6 --no-commit` (then resolve + commit).
- `firestarter/v1.6-read-bug~1` = `437339b6` (the masked PORTx-clear commit; Plan 28-03 reverts this).
- `firestarter/v1.6-read-bug~2` = `fdb1ed5` (the RED unity scaffold; the pre-fix shape baseline if both reverts are eventually needed).
- `firestarter/v1.6-read-bug~3` = `bc0f5ac` (the branch-cut point from `beta`; baseline before any Phase 28 work).
- `firestarter/src/boards/leonardo_rurp_shield.cpp` lines 112-129 + 137-141 — the two functions touched across the fix window.

#### v1.7 substrate (forward-references, NOT activated by Phase 28 re-iteration)
- `.planning/v1.7-SHIELD-REVS.md §6` per-rev capability matrix — substrate for the parked Plan 27-05 instrumented-build template; Phase 28 re-iteration does NOT activate it but acknowledges it as the substrate for v1.8 re-fix work.
- `firestarter/include/rurp_pinout.h:66-68` `ADC_BAND_R41_*` constants — v1.7 Phase 34 additions; not consumed by Phase 28 re-iteration.
- `firestarter/include/rurp_hw_rev_utils.h` `rurp_detect_hardware_revision()` — v1.7 Phase 34 addition; not consumed by Phase 28 re-iteration.

#### Cross-cutting memory + branching
- Memory `[[project_uno328pb_bench_instability_27_04]]` — operator-workstream substrate for the uno328pb regression (NOT Phase 28's responsibility per D-15v2).
- Memory `[[feedback_branching]]` — `v1.6-read-bug` branches in all 3 repos (compliant with D-03 carry-forward).
- Memory `[[user_firestarter_repo_layout]]` — meta at `/workspaces`, firmware sub-repo at `/workspaces/firestarter`, host sub-repo at `/workspaces/firestarter_app`.
- Memory `[[feedback_chip_out_before_sideload]]` — applies if Phase 28 re-iteration ever sideloads (it does NOT; Phase 29 v2 owns the sideload).
- Memory `[[feedback_verify_port_identity_each_task]]` — applies if Phase 29 v2 (operator wave) reads serial; Phase 28 desk-side does not.

#### ROADMAP + traceability
- `.planning/ROADMAP.md` §"Phase 28: Fix Implementation + Unit Test Coverage" (lines 164-177) — original phase definition; SC#1-5 re-interpreted per D-17v2 milestone re-scope.

</canonical_refs>

<code_context>
### Existing Code Insights (Re-iteration)

#### Sub-repo state landmarks
- `firestarter` repo: branch `v1.6-read-bug` at HEAD `4f205e58`; working tree clean (per Plan 27-05 sub-repo guard 2026-05-26). Three commits ahead of `beta` HEAD `bc0f5ac`.
- `firestarter_app` repo: branch `v1.6-read-bug` at HEAD `999c3cc`; working tree clean. Sanctioned deviation per Plan 27-04 (left on `v1.6-read-bug` to preserve `firestarter dev consistency-check` availability for the re-iteration + Phase 29 v2 work).
- Meta-repo (`/workspaces`): branch `v1.6-read-bug`; .planning/ modifications go on this branch (per `feedback_branching` convention for the meta-repo during v1.6 work).

#### Revert mechanics
- `git revert 437339b6 --no-commit` produces a clean inverse patch (the commit edits only `firestarter/src/boards/leonardo_rurp_shield.cpp:137-141`; the inverse is removing the PORTD/PORTC/PORTE clear block). No merge conflicts expected — Phase 27 RCA confirmed the file-SHA shape is identical between `bc0f5ac` and `fdb1ed5` (the RED scaffold doesn't edit `leonardo_rurp_shield.cpp`).
- Commit message convention for git-revert: default `Revert "fix(leonardo): ..."` subject is acceptable; D-06 carries-forward the footer expansion to cite Plan 27-05.

#### Test infrastructure (carried from v1)
- `[env:native]` + `unity` + `ArduinoFake` + `test_filter` allowlist pattern remains the canonical Unity test infrastructure (per `firestarter/CLAUDE.md §"Native (Host) Test Environment"`). Phase 28 re-iteration prunes (not extends) the allowlist.
- `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` — the file created in Wave A (Plan 28-01) RED scaffold; contains the pullup-clear assertion test (per D-12v2 deletion target). Researcher checks for the `test_rurp_read_data_buffer_reassembles_data_bus` companion case.

#### `.hex` capture pattern (per ROADMAP SC#4 carry-forward)
- `pio run -e {uno,leonardo,uno328pb}` produces `.pio/build/{env}/firmware.hex`. SHA-256 via `sha256sum .pio/build/{env}/firmware.hex`.
- Pre-revert baseline = current HEAD `4f205e58` (build now, capture once). Post-revert capture = same command after `git revert 437339b6` + commit.
- Cross-board byte-identity check: Uno + uno328pb `.hex` SHA must be byte-identical pre/post (no source touched on those code paths). Leonardo `.hex` SHA must differ (the revert removes the PORTx-clear block).

</code_context>

<specifics>
### Specific Re-iteration Ideas

- **Pre-revert `.hex` SHA capture is a one-time desk-side task** — `firestarter/v1.6-read-bug` HEAD `4f205e58`; build all three envs ONCE, record sums in a scratchpad, then proceed with the revert. Don't repeat.
- **Revert commit subject convention:** `Revert "fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input"` (the default `git revert` subject is fine; do not editorialize).
- **`firestarter/v1.6-read-bug` history after Plan 28-03 lands:** `bc0f5ac` (cut-point) → `fdb1ed5` (RED scaffold) → `437339b6` (broken PORTx-clear fix) → `4f205e58` (broken `_NOP()` settling fix) → `<new>` (Revert "437339b6"). The branch grows linearly; no rewinds, no force-pushes.
- **Conditional Plan 28-04 commit (if it fires):** `Revert "fix(leonardo): add _NOP settling delay between PIND/PINC/PINE reads in rurp_read_data_buffer"`. Same footer template.
- **Anti-pattern immutability guard for Phase 28 re-iteration:** capture SHA-256 of the original `## Phase 28 — Fix Commit References` H2 section in `.planning/v1.6-EVIDENCE.md` BEFORE appending the re-iteration H2; assert byte-identical AFTER. Mirrors Plan 27-05's three anti-pattern guards (Phase 27 H2, Wave B FAIL H3, `## Verdict` H2).
- **Test deletion commit:** if separated from the revert commit, subject = `test(leonardo): remove pullup-clear assertion superseded by Phase 27 re-open revert`. Body cites Plan 27-05.

</specifics>

<deferred>
### Deferred Ideas (Re-iteration)

- **Proper Leonardo read-bug re-fix** — deferred to a future milestone (likely v1.8) once the v1.7 shield-detect substrate (`REVISION_2_3` / `REVISION_UNKNOWN` enum + `ADC_BAND_R41_*` constants + per-rev capability matrix) is forward-merged onto `firestarter/v1.6-read-bug` (or a new branch cut from a more-recent `beta` tip). Re-fix approach: activate the Plan 27-05 parked instrumented-build template (`-D RCA_INSTRUMENT_READ_TRACE=1`), capture ADC-band-tagged read traces pre/post candidate-fix, characterize residual timing margin before re-landing any PORTx-clear-with-guard or `_NOP()`-tune variant.
- **uno328pb pre-existing regression** — operator workstream per D-15v2. Candidate causes: Rev 2.2 socket contact wear; USB-UART bridge buffering interaction with ATmega328PB Case A; USB-CDC vs UART latency under sustained 250kbaud reads; RX buffer stalls. Permanent memory `[[project_uno328pb_bench_instability_27_04]]` is the diagnostic substrate.
- **Plan 28-04 (conditional second revert)** — drafted-but-not-executed by default per D-13v2. Activates only if Phase 29 v2 bench sideload shows Leonardo shape still zeros-dominant after the 28-03 single revert.
- **Documentation drift correction (5 locations claiming Leonardo 1024-B)** — Phase 30 paperwork (D-05 carry-forward).
- **`firestarter/platformio.ini:64-65` Leonardo `DATA_BUFFER_SIZE` revert from 512 → 1024** — intentionally NOT in Phase 28 re-iteration (per D-05 carry-forward). Phase 30 polish or post-v1.6 follow-up.
- **Phase 30 v1.6 milestone close re-scope** — Phase 30 re-discusses separately per D-17v2 (the milestone goal narrows to "ship diagnostic + revert broken fix; defer read-bug fix to v1.8").
- **Backfill Unity tests for the Uno `df5fb44` fix** — original CONTEXT.md deferred this; still deferred.
- **`firestarter info <chip>` crash** (TypeError unrelated to v1.6) — still deferred.
- **`0xda01` W27C512 chip-ID alias gap** — still deferred.
- **uno328pb-silicon row in EVIDENCE.md** — still deferred per `[[project_uno328pb_correction]]`.

### Reviewed Todos (not folded, re-iteration)
- **`large-read-data-jitter-uno328pb.md`** — the v1.6 milestone bug. Move out of `pending/` now happens in Phase 30 with the re-scoped milestone narrative ("diagnostic shipped; broken fix reverted; proper fix deferred to v1.8"). NOT a Phase 28 re-iteration deliverable.
- **`avrdude-mcu-detection-fallback.md`** — still deferred to its own milestone.
- **`w27c512-eeprom-misclassification.md`** — still deferred to its own milestone.

</deferred>

---

## Appendix — Original Phase 28 Context (2026-05-21, Superseded)

The original context below captured decisions for the Phase 28 v1 attempt that shipped commits `437339b6` (masked PORTx-clear in `rurp_set_data_input`) + `4f205e58` (`_NOP()` settling in `rurp_read_data_buffer`). Phase 27 re-open (2026-05-26, Plan 27-05) closed at higher fidelity than the original 27-01 RCA and isolated both commits as introducing a separate failure mode on Leonardo (99% zeros / 0.08% jitter / 5-distinct-SHAs vs the original Phase 26 baseline 2.1% jitter on structured data). The original CONTEXT.md decisions D-01 (two atomic fix commits), D-02 (Unity test asserting PORTx clear), D-04 (Wave A RED + Wave B fix structure) were all executed as planned but produced a regression, not a fix.

The Phase 28 re-iteration scope above SUPERSEDES the original decisions. The original is preserved in this appendix as an audit trail for future readers (and in `git log -- .planning/phases/28-fix-implementation-unit-test-coverage/28-CONTEXT.md` for the full diff). Do not re-execute the original decisions; they have been retired.

---

<domain_v1_superseded>
## Phase Boundary (v1 — SUPERSEDED 2026-05-26)

> **Note:** This v1 section captures the original 2026-05-21 scope. It is preserved as an audit trail. The current Phase 28 scope is the re-iteration section above. Do not act on v1 decisions; they shipped + were reverted.

Phase 28 delivers **the firmware-side fix for the Leonardo 64KB-read byte-jitter, plus a host-side Unity test that exercises the corrupting code path and fails on pre-fix code**. The fix lands as atomic commit(s) on `firestarter/v1.6-read-bug` (cut from `beta` at the start of this phase per Phase 27 D-03 deferral); each commit cites the Phase 27 RCA section in `.planning/v1.6-EVIDENCE.md` and the introducing-commit triangulation. Bench verification is Phase 29; Phase 28 is desk-side TDD only.

The RCA already pinpointed the corrupting code path with HIGH confidence — Phase 28 has a clean fix sketch + GATE-1.6 three-axis-green risk assessment to plan against:

1. **Primary mechanism (mandatory fix):** `firestarter/src/boards/leonardo_rurp_shield.cpp:rurp_set_data_input()` (lines 137-141) clears `DDRD` / `DDRC` / `DDRE` but leaves residual `PORTD` / `PORTC` / `PORTE` bits set from prior register strobes. Internal pullups bias 1-2 data pins HIGH against the chip's drive on partially-erased EPROM cells, producing single-bit XOR flips (78% of divergences). Fix: mirror Uno-side `df5fb44` (2026-05-13) — clear PORTx bits BEFORE clearing DDRx.
2. **Secondary mechanism (also recommended):** `rurp_read_data_buffer()` (lines 112-129) reads `PIND`, `PINC`, `PINE` in three separate machine instructions with no settling delay after the address-bus change driven by `rurp_set_address()`. Fix: insert `_NOP()` (or equivalent short stall) between PIN reads so the data bus stabilizes.

**In scope:**
- Cut `firestarter/v1.6-read-bug` branch from current `beta` tip (`bc0f5ac`, 1 docs-only commit ahead of tag `3.0.0b4`).
- Atomic fix commit(s) on `firestarter/v1.6-read-bug` editing ONLY `src/boards/leonardo_rurp_shield.cpp` — `rurp_set_data_input()` and `rurp_read_data_buffer()`. No other source files touched (read-path-only scope confirmed by Phase 27 GATE-1.6 analysis).
- Native Unity test under `firestarter/test/native/avr/test_data_input/` (or extend existing `test_dispatch/` layout) that mocks PORTx/DDRx/PINx via ArduinoFake + host stubs, sets PORTx to non-zero pre-state, calls `rurp_set_data_input()`, asserts PORTx data bits are cleared AND DDRx data bits are input. Test is committed BEFORE the fix (TDD red-bar evidence for FIX-02); demonstrated to FAIL on parent commit and PASS on fix commit.
- All three firmware envs (`uno`, `leonardo`, `uno328pb`) compile cleanly. Per-board `.hex` sizes recorded in fix commit message; drift > ±200 B flagged for re-review.
- `pio test -e native` stays green (existing `test_dispatch` + `test_messages` suites untouched + new `test_data_input` suite passes).
- Append `## Phase 28 — Fix Commit References` section to `.planning/v1.6-EVIDENCE.md` (matching the line-110 forward-annotation comment) with: firmware commit SHA(s), introducing-commit citation, Unity test file path + test name, per-board `.hex` sizes, and a Phase-29 bench-verification placeholder.
- GATE-1.6 desk-side confirmation: read-path-only edits, write path / VPP regulator / pulse-interval code paths untouched.

**Out of scope:**
- Bench validation / N≥5 byte-identity verification on the operator's hardware — Phase 29 owns this end-to-end (FIX-03's `firestarter write` + `dev read -s N` byte-comparison is bench-gated; "desk-side TDD-equivalent" per ROADMAP SC#3 means desk-side compile-clean + native Unity green + read-path-only code inspection).
- Documentation drift correction (Phase 27 EVIDENCE.md drift-correction table: `firestarter/CLAUDE.md` "1024-B" claims, `/workspaces/CLAUDE.md`, `26-02-SUMMARY.md:147`, `large-read-data-jitter-uno328pb.md:57`, EVIDENCE.md self-references) — Phase 30 milestone-close paperwork owns these per Phase 27 D-11.
- Reverting `firestarter/platformio.ini:64-65` Leonardo `DATA_BUFFER_SIZE` from `512` back to `1024` — the A/B test annotation stays; the buffer-size IS NOT the discriminator per Phase 27 H6 refutation, and keeping the FW identical except for the read-bug fix isolates the fix as the only variable for Phase 29's bench A/B.
- Host CLI cosmetic polish from Phase 26 follow-up (REVIEW WR-01 FAIL-without-divergence edge case, WR-02 `Board: unknown-board` field) — Phase 30 paperwork or post-v1.6.
- Host-side firestarter_app changes — RCA points entirely to firmware; the host-side `serial_comm.py` / `eprom_operations.py` path is clean (CRC8 + length-authoritative framing has zero failures in the bench logs).
- Plain Uno or uno328pb-silicon read-path changes — only Leonardo's `rurp_set_data_input` / `rurp_read_data_buffer` are corrupting (Plain Uno's df5fb44 fix already shipped 2026-05-13; uno328pb-silicon row deferred until reflash per `[[project_uno328pb_correction]]`).
- Moving the bug todo out of `pending/` — Phase 30 DOC-01 paperwork.
- Sub-repo `v1.6-read-bug` → `beta` merge — happens at the Phase 29 boundary to trigger a fresh pre-release cut for bench install (per ROADMAP §"Phase 28" SC#5).
- v1.1 FM1608 byte-0 carryover (separate hardware-level bug, separate debug session, `[[user_firestarter_repo_layout]]` shows it as the v1.1 80%-parked milestone — not in v1.6 scope).

</domain_v1_superseded>

<decisions_v1_superseded>
## Implementation Decisions (v1 — SUPERSEDED 2026-05-26)

### Fix shape

- **D-01: Land BOTH RCA-named mechanisms as two atomic commits on `firestarter/v1.6-read-bug`.**
  Two separate atomic commits, each citing the specific RCA evidence axis it addresses:
  - **Commit 1 — `fix(leonardo): clear PORTD/PORTC/PORTE pullups in rurp_set_data_input` —** mirrors the Uno-side `df5fb44` pattern. Adds `PORTD = 0x00; PORTC &= ~PORTC_DATA_MASK; PORTE &= ~PORTE_DATA_MASK;` BEFORE the existing `DDRD &= ~PORTD_DATA_MASK;` / `DDRC &= ~PORTC_DATA_MASK;` / `DDRE &= ~PORTE_DATA_MASK;` lines. Addresses the 78%-single-bit-flip / address-bit-3-correlation evidence (the dominant corruption mechanism).
  - **Commit 2 — `fix(leonardo): add settling delay between PIND/PINC/PINE reads in rurp_read_data_buffer` —** inserts a short stall (`_NOP()` ×N, with N chosen so total stall ≥ ~125ns to cover one EPROM data-out propagation cycle at worst-case Vcc — researcher picks the exact instruction sequence) between the three `PINx` reads at lines 114-116. Addresses the multi-instruction-port-read timing race.
  Rationale:
  - **Both mechanisms are implicated by the binary evidence.** RCA explicitly says "the binary evidence implicates both the pullup-bias mechanism (via `rurp_set_data_input`) and the multi-register read timing (via the three-instruction PIND/PINC/PINE sequence in `rurp_read_data_buffer`)" (v1.6-EVIDENCE.md §"Fix sketch").
  - **Two atomic commits, not one squashed commit, because:** (1) each commit's "what this fixes" maps 1:1 to an RCA paragraph + evidence axis, so future readers can trace symptom → mechanism → fix; (2) `git bisect` between the two commits in Phase 29 (or post-ship) can answer the open question "is PORTx-clear alone sufficient or is the `_NOP()` settling needed?" — that experiment is cheaper to run with the commits split; (3) matches the v1.2 / v1.3 atomic-commit-per-RCA-axis pattern.
  - **Cost of "belt-and-suspenders" is trivial.** PORTx-clear adds ~6 instructions (~12 B flash); `_NOP()` adds 1-2 instructions per call site. Total expected drift ≤ 50 B per binary — deep in the noise vs the ±200 B ROADMAP SC#4 threshold.
  - **GATE-1.6 three-axis-green carries over** (Phase 27 §"GATE-1.6 Risk Assessment"). Both edits are in the READ path (`rurp_set_data_input` / `rurp_read_data_buffer`); the write path uses `rurp_write_data_buffer` + `rurp_set_data_output` (separate functions); VPP / regulator / pulse-interval code paths untouched. No mandatory mitigation items emerge.

  **Output the planner needs:** PLAN.md task list specifies the two commits, the exact line ranges, the diff shape (mirror of `df5fb44` for Commit 1; researcher picks `_NOP()` count for Commit 2 with rationale).

### Test approach

- **D-02: Single Unity native test suite under `firestarter/test/native/avr/test_data_input/`, exercising `rurp_set_data_input` post-conditions.**
  Use the existing `[env:native]` infrastructure documented in `firestarter/CLAUDE.md` §"Native (Host) Test Environment":
  - **Directory:** `firestarter/test/native/avr/test_data_input/` (parallel to existing `test_dispatch/` and `test_messages/`). Add `native/avr/test_data_input` to the `test_filter` allowlist in `platformio.ini` `[env:native]`.
  - **Files:**
    - `test_rurp_set_data_input.cpp` — Unity `RUN_TEST` cases covering Leonardo post-conditions.
    - `host_stubs.cpp` — extends `firestarter/test/native/avr/_shared/host_stubs_common.inc` if the new test references AVR symbols not already stubbed. The PORTx/DDRx/PINx registers are already host-mockable via ArduinoFake or simple `uint8_t` globals (existing pattern from `test_dispatch/`).
  - **Test shape:**
    1. **Pre-state setup:** set `PORTD`, `PORTC`, `PORTE` to non-zero values that simulate residual register state from prior `rurp_set_control_pins` / `rurp_write_data_buffer` strobes (e.g., `PORTD = 0xFF; PORTC = 0xFF; PORTE = 0xFF;`).
    2. **Action:** call `rurp_set_data_input()` (the Leonardo build path — guarded by `#ifdef ARDUINO_AVR_LEONARDO` in `leonardo_rurp_shield.cpp`; the native env needs `-D ARDUINO_AVR_LEONARDO` injected into the test build flags OR the function exposed via a board-agnostic shim — researcher picks the cleaner integration).
    3. **Post-condition assertions:**
       - `TEST_ASSERT_EQUAL_HEX8(0x00, PORTD & PORTD_DATA_MASK);` — data-bit pullups cleared
       - `TEST_ASSERT_EQUAL_HEX8(0x00, PORTC & PORTC_DATA_MASK);`
       - `TEST_ASSERT_EQUAL_HEX8(0x00, PORTE & PORTE_DATA_MASK);`
       - `TEST_ASSERT_EQUAL_HEX8(0x00, DDRD & PORTD_DATA_MASK);` — DDRx still set to input (regression guard)
       - `TEST_ASSERT_EQUAL_HEX8(0x00, DDRC & PORTC_DATA_MASK);`
       - `TEST_ASSERT_EQUAL_HEX8(0x00, DDRE & PORTE_DATA_MASK);`
  - **FIX-02 evidence requirement:** test is committed BEFORE the fix in Wave A. Wave A's executor confirms the test FAILS on the parent commit (i.e., red bar against `leonardo_rurp_shield.cpp` as it currently stands at `beta`). Wave B then lands the fix; the same test PASSES. The PR/commit narrative records both the parent-commit failure output and the fix-commit success output.
  - **`rurp_read_data_buffer` settling-delay coverage:** Unity cannot directly observe the physical `_NOP()` timing — that's a code-presence + regression check, not a behavioral test. Cover it as: (a) a presence check (`grep '_NOP'` in `leonardo_rurp_shield.cpp:rurp_read_data_buffer` as part of the Wave B verifier — narrative-level, not a Unity assertion), and (b) a Unity case that asserts `rurp_read_data_buffer()` returns the correct value given mock `PIND/PINC/PINE` (validates the shift-and-mask reassembly logic stays intact through the settling-delay edit; regression guard, not bug-evidence).

  **Test name (canonical):** `test_rurp_set_data_input_clears_data_pullups_leonardo` and `test_rurp_read_data_buffer_reassembles_data_bus`. Test file path: `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp`.

  Rationale:
  - **Existing infrastructure.** `[env:native]` + `unity` + `ArduinoFake` + the `test_dispatch/`/`test_messages/` allowlist pattern is already battle-tested through Phases 12, 17, 20. No new build system work — drop in a new directory, add one line to the `test_filter` allowlist, done.
  - **Phase-26 host-side pytest pattern mirrors this.** REPRO-03 shipped `test_consistency_check.py` (8 cases) under `firestarter_app/tests/` using the same pre-state-setup → action → post-condition shape. Phase 28's firmware Unity test is the firmware-side analog.
  - **Test asserts the FIX directly, not the symptom.** The 2.1% byte-jitter is a physical-bus race that requires real silicon to reproduce. Asserting the fix's *post-conditions* (PORTx cleared) is the host-testable mechanism — and is exactly what the Uno-side `df5fb44` would have caught if it had had a unit test (which it didn't; this is also a backfill for the Uno-side equivalent).

### Branch flow

- **D-03: Cut `firestarter/v1.6-read-bug` from `beta` HEAD (`bc0f5ac`) at the start of Wave A.**
  Cut point is current `beta` HEAD, which is 1 commit (`bc0f5ac docs(25): document uno328pb as third firmware build target (v1.5)`, docs-only) ahead of tag `3.0.0b4`. The docs commit is benign — no firmware semantics change between `3.0.0b4` and `beta` HEAD. Pinning to current `beta` HEAD avoids the awkward "branch off a tag that isn't `beta`'s HEAD" git operation.
  Rationale:
  - **Per Phase 27 D-03:** "If Wave B does not fire, the firmware branch is still deferred to Phase 28." Wave B did not fire (verdict `needs_bench: false`); Phase 28 cuts the branch.
  - **Per memory `[[feedback_branching]]`:** all v1.6 work lands on `v1.6-read-bug` branches in all 3 repos; sub-repos branch off `beta`. Compliant.
  - **Promotion gate:** `firestarter/v1.6-read-bug` → `beta` merge happens at the Phase 29 boundary to trigger a fresh pre-release cut (e.g., `3.0.0b5` or `3.0.1bN`) for bench install via `firestarter fw -i --pre --force`. NOT inside Phase 28 (per ROADMAP SC#5).
  - **Meta-repo coordination:** the meta-repo's `.planning/phases/28-*/` directory commits go on `main` (per the project's standing meta-repo convention — meta-repo never uses topic branches; the v1.6 work surface lives entirely on the sub-repos' `v1.6-read-bug` branches).
  - **firestarter_app sub-repo:** already on `v1.6-read-bug` (cut during Phase 26 for the diagnostic CLI work — commits `999c3cc` + `c057fe2` are visible). No new sub-repo branch needed for Phase 28; the host-side branch stays parked at its Phase 26 tip until Phase 30's potential host-side polish or directly to the Phase 29 promotion.

### Plan structure

- **D-04: Two-wave TDD plan — Wave A (failing test) + Wave B (fix + green).**
  - **Wave A — Plan 28-01 (autonomous: true, desk-side):** Cut `firestarter/v1.6-read-bug` from `beta` HEAD. Add new directory `firestarter/test/native/avr/test_data_input/` + Unity test files per D-02. Extend `platformio.ini` `[env:native].test_filter` to include the new suite. Execute `pio test -e native -f "*test_data_input*"` and capture the RED bar against the un-fixed `leonardo_rurp_shield.cpp`. Commit message: `test(leonardo): RED unity scaffold for rurp_set_data_input pullup clearing (FIX-02)`. Verifier confirms: (1) new suite shows FAIL with the expected post-condition assertion failures (not a build / link failure), (2) existing `test_dispatch` + `test_messages` suites still GREEN, (3) `pio run -e uno`, `-e leonardo`, `-e uno328pb` still build clean. Closes FIX-02's "test demonstrably fails on pre-fix code" half.
  - **Wave B — Plan 28-02 (autonomous: true, desk-side, depends on Wave A):** Apply the two atomic fix commits per D-01 to `leonardo_rurp_shield.cpp`. Re-run `pio test -e native -f "*test_data_input*"` and confirm GREEN. Re-build all three firmware envs (`pio run -e uno`, `-e leonardo`, `-e uno328pb`); capture per-board `.hex` sizes via `pio run --list-targets` / `wc -c .pio/build/*/firmware.hex` (or equivalent). Each fix commit message cites: (a) the RCA section in `.planning/v1.6-EVIDENCE.md` (full relative path + section header), (b) the introducing-commit triangulation (`5b1f1cd` for shape, "bug present at every tag from 2.0.2 through 3.0.0b4"), (c) the Wave A test file path + test name. Append `## Phase 28 — Fix Commit References` section to `.planning/v1.6-EVIDENCE.md` (recording firmware commit SHAs, test file, per-board sizes, Phase-29 bench placeholder). Closes FIX-01 + FIX-02's "PASS on post-fix code" half + ROADMAP SC#1/SC#2/SC#4 (commit-citation + Unity test + size record). FIX-03 is bench-gated and closes in Phase 29.

  Rationale:
  - **Matches v1.2/v1.3 atomic-commit-per-axis + Wave-0-scaffold-first pattern.** Phase 11 Plan 11-01 (RED scaffold first), Phase 12 Wave 0 (RED scaffold first), Phase 17 (same shape) — Wave A failing test → Wave B fix is the proven structure in this project.
  - **Each wave's atomic artifact is independently verifiable.** Wave A's RED bar is the evidence that FIX-02's "would fail on pre-fix code" half is satisfied (without Wave A, the FIX-02 claim is unfalsifiable). Wave B's GREEN bar + commit SHAs are the evidence for FIX-01.
  - **No bench escalation gate.** Unlike Phase 27 which had a conditional Wave B (`needs_bench: true/false`), Phase 28 is unconditionally desk-side. Phase 29 is the bench gate.

### Documentation drift correction

- **D-05: Defer all 5 drift-correction targets to Phase 30 milestone close.**
  The Phase 27 EVIDENCE.md drift-correction table lists 5 locations claiming "Leonardo 1024-B" (incorrect per `platformio.ini:64-65`):
  - `firestarter/CLAUDE.md` §"Architecture" / "Board differences"
  - `/workspaces/CLAUDE.md` §"Key Architecture Points"
  - `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-02-SUMMARY.md:147`
  - `.planning/todos/pending/large-read-data-jitter-uno328pb.md:57` (hypothesis #4)
  - `.planning/v1.6-EVIDENCE.md:27` + `:54` (Phase 26 verdict text + entry conditions)
  Rationale:
  - **Phase 27 D-11 explicitly defers to Phase 28 polish OR Phase 30 cleanup.** Phase 28's center of gravity is fix + test; doc cleanup is paperwork. Phase 30 has DOC-01 / DOC-02 / MS-01 explicitly for milestone-close documentation work, plus the bug-todo move (DOC-01 already references the drift-correction context). Cleaner to bundle there.
  - **ROADMAP SC#1 for Phase 28 doesn't include doc edits.** It says fix commits cite RCA — it does not say correct historical drift in unrelated planning docs.
  - **One exception:** the `firestarter/platformio.ini:64-65` `; TEMP: 512` comment IS the source-of-truth and STAYS UNTOUCHED. Whether to revert Leonardo's `-D DATA_BUFFER_SIZE=512` back to `1024` is intentionally OUT OF Phase 28 scope (see `domain` "Out of scope" — Phase 29's bench A/B isolates the fix as the only variable).

### Introducing-commit citation format

- **D-06: Cite RCA + shape-introducing-commit in EVERY fix commit message.**
  Commit-message footer pattern (both Wave B commits):
  ```
  RCA: .planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Findings" (2026-05-21)
  Introducing-commit: 5b1f1cd "Leonardo is working, fast as a shark" (2025-02-11) — shape introduction
  Tag presence: bug present at every firmware tag from 2.0.2 through 3.0.0b4 (verified via tag-walk)
  Test: firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp
  ```
  Rationale:
  - **FIX-01 wants RCA citation + atomic commits.** This format satisfies it explicitly.
  - **RCA-03 milestone-bracket gets honored verbatim.** "Pre-v1.0" bracket + the `5b1f1cd` shape-introduction commit are exactly what RCA §"Introducing-commit triangulation (RCA-03)" produced; the fix commits cite both.
  - **Tag-walk reference closes the future-reader loop.** A maintainer 2 years from now opening `git log -- src/boards/leonardo_rurp_shield.cpp` can immediately reconstruct: "the function has had this shape since 2025-02-11; the bug shipped at every tag from 2.0.2 through 3.0.0b4; the fix is on `v1.6-read-bug`/post-3.0.0b4." No re-bisecting.

### Flash budget tracking

- **D-07: Record per-board `.hex` sizes in Wave B fix commit message; ±200 B threshold for re-review.**
  Expected drift per ROADMAP SC#4 baseline:
  - Leonardo (the tightest board): pre-fix ~85.4% flash utilization (v1.2 baseline). Post-fix expected delta: +12-50 B (PORTx-clear + `_NOP()` instructions). Well under ±200 B.
  - Uno: untouched (no edits to `uno_rurp_shield.cpp`). 0 B delta expected.
  - uno328pb: untouched. 0 B delta expected.
  Recorded as table in the Wave B commit message:
  ```
  Flash sizes (post-fix vs pre-fix beta@bc0f5ac):
  | Board     | Pre-fix .hex | Post-fix .hex | Δ      |
  |-----------|--------------|---------------|--------|
  | uno       | <N>          | <N>           | 0      |
  | leonardo  | <N>          | <N>+~40       | +~40   |
  | uno328pb  | <N>          | <N>           | 0      |
  ```
  Rationale: matches ROADMAP SC#4 verbatim; ±200 B is the auto-flag threshold; sizes go in EVIDENCE.md `## Phase 28 — Fix Commit References` for cross-phase visibility.

### EVIDENCE.md append section

- **D-08: Append `## Phase 28 — Fix Commit References` to `.planning/v1.6-EVIDENCE.md` at the end of Wave B.**
  Location anchor: line 110 `<!-- Phase 28 appends commit refs here: ## Phase 28 — Fix Commit References. -->`. Section body:
  - Commit SHA(s) + author + date + commit message subject for each fix commit.
  - Introducing-commit reference (per D-06).
  - Unity test file path + test name(s) + Wave A RED-bar SHA + Wave B GREEN-bar SHA.
  - Per-board `.hex` sizes table (per D-07).
  - Phase 29 placeholder: `<!-- Phase 29 appends post-fix bench verification: ## Phase 29 — Post-fix Consistency-Check Verification. -->` (already exists at line 111; do not duplicate).
  Rationale: same single-evidence-file-across-all-v1.6-phases pattern as Phase 27 D-04. One file for Phase 30 to archive.

### Reviewed Todos (cross_reference_todos)
None folded. The phase-28 scope is the firmware fix + unit test; the three pending todos that scored 0.6 are unrelated:
- `large-read-data-jitter-uno328pb.md` — the v1.6 bug itself; will be moved out of `pending/` by Phase 30 DOC-01 (not Phase 28).
- `avrdude-mcu-detection-fallback.md` — unrelated v1.5 carryover; deferred to its own milestone.
- `w27c512-eeprom-misclassification.md` — unrelated chip-DB classification issue; deferred to its own milestone.

### Claude's Discretion
- **Exact `_NOP()` count in Commit 2.** Researcher / planner picks N based on (a) the 32U4 datasheet's per-port-read propagation time and (b) the EPROM data-out worst-case access time at Vcc=4.5V. If unclear from docs, default to a single `_NOP()` between each PINx pair (2 `_NOP()`s total — minimum useful settling) with a comment citing the chosen rationale. Bench-confirmable in Phase 29.
- **Whether to expose `rurp_set_data_input` for native testing via `#ifdef ARDUINO_AVR_LEONARDO` extension OR via a board-agnostic shim.** Researcher picks the integration that requires the smallest delta to the existing native test build (likely: add `-D ARDUINO_AVR_LEONARDO` to the new `test_data_input` suite's local build flags so the `#ifdef ARDUINO_AVR_LEONARDO` guard in `leonardo_rurp_shield.cpp` fires under `[env:native]` for this one suite — same pattern used by `test_dispatch/` to selectively include `proms/*.cpp`).
- **Whether to add the second Unity case for `rurp_read_data_buffer` shift-and-mask reassembly.** Default: yes (regression guard against the settling-delay edit breaking the bit-mapping logic); but if it adds significant test scaffolding overhead, ship only the `rurp_set_data_input` case and rely on the existing physical-build evidence for the reassembly logic.

</decisions_v1_superseded>

<canonical_refs_v1_superseded>
## Canonical References (v1 — SUPERSEDED 2026-05-26)

**Note:** The v1 canonical refs below were the inputs for the original Phase 28 attempt. The re-iteration canonical refs section above (`<canonical_refs>`) is authoritative for downstream agents.

### RCA + bug evidence (primary inputs)
- `.planning/v1.6-EVIDENCE.md` §"Phase 27 — RCA Findings (2026-05-21)" — the 5-paragraph WHY + hypothesis-disposition table + introducing-commit triangulation + GATE-1.6 three-axis-green risk assessment + fix sketch + drift-correction targets. THE primary input for Phase 28.
- `.planning/v1.6-EVIDENCE.md` §"Fix sketch (Phase 28 handoff)" — names BOTH fix candidates (PORTx-clear in `rurp_set_data_input` + `_NOP()` settling in `rurp_read_data_buffer`); Phase 28 lands both per D-01.
- `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_0[1-3].bin` — Phase 26 baseline binaries (3 × 64KB). Wave A's test can re-derive the 78% single-bit-flip + 63.2% address-bit-3 evidence via the 5-line Python cross-check at EVIDENCE.md lines 99-108 (sanity check only — not part of the Unity test).

### Phase 27 context (decisions Phase 28 inherits)
- `.planning/phases/27-root-cause-analysis/27-CONTEXT.md` — Phase 27 D-03 (deferred firmware-branch cut to Phase 28), D-04 (EVIDENCE.md append pattern), D-05 (DATA_BUFFER_SIZE=512 source-of-truth), D-06 (milestone-bracket-first introducing-commit strategy), D-11 (drift-correction targets → Phase 30).

### Roadmap + requirements (locked phase scope)
- `.planning/ROADMAP.md` §"Phase 28: Fix Implementation + Unit Test Coverage" (lines 72-83) — Goal + 5 success criteria + branch flow.
- `.planning/REQUIREMENTS.md` lines 24-26 — FIX-01, FIX-02, FIX-03 verbatim text. FIX-03 is bench-gated → Phase 29; Phase 28 closes FIX-01 + FIX-02.

### Sub-repo source-of-truth (Phase 28's edit target)
- `firestarter/src/boards/leonardo_rurp_shield.cpp` lines 112-129 (`rurp_read_data_buffer`) and 137-141 (`rurp_set_data_input`) — the two functions Phase 28 edits.
- `firestarter/src/boards/uno_rurp_shield.cpp` — `rurp_set_data_input` POST-`df5fb44` shape; the pattern Phase 28 mirrors for Leonardo. Commit `df5fb44` (2026-05-13) is the reference fix.
- `firestarter/include/rurp_shield.h` — PORTx/DDRx/PINx constant definitions; `PORTD_DATA_MASK` / `PORTC_DATA_MASK` / `PORTE_DATA_MASK` are defined inline at `leonardo_rurp_shield.cpp:16-18` (not in the header — researcher confirms scope at planning).
- `firestarter/platformio.ini` §`[env:native]` (lines 67-102) — test infrastructure (Unity + ArduinoFake + `test_filter` allowlist + `src_filter` rule). Phase 28 extends `test_filter` with one line.
- `firestarter/CLAUDE.md` §"Native (Host) Test Environment" — host-side Unity reuse pattern (`test/native/avr/<dirname>/`, `host_stubs.cpp`, `pgmspace.h` shim) and `pio test -e native -f` invocation. Phase 28 drops a new directory under this convention.

### Cross-cutting branching + memory
- Memory `[[feedback_branching]]` — all v1.6 work on `v1.6-read-bug` branches in all 3 repos; sub-repos branch off `beta`. Compliant with D-03.
- Memory `[[user_firestarter_repo_layout]]` — meta-repo at `/workspaces`, firmware sub-repo at `/workspaces/firestarter`, host sub-repo at `/workspaces/firestarter_app`.
- `.planning/PROJECT.md` §"Current Milestone: v1.6 Fix the Read Bug" lines 11-23 — milestone goal, target features, locked decisions (GATE-1.6, branch model, definition of done).

### Phase 26 host-side test pattern (precedent for D-02)
- `firestarter_app/tests/test_consistency_check.py` — 8-case pytest suite from REPRO-03. Host-side analog of the Unity test Phase 28 lands firmware-side. Same pre-state → action → post-condition shape.

</canonical_refs_v1_superseded>

<code_context_v1_superseded>
## Existing Code Insights (v1 — SUPERSEDED 2026-05-26)

### Reusable Assets
- **`firestarter/test/native/avr/` Unity infrastructure** (`platformio.ini` `[env:native]`, `host_stubs.cpp`, `_shared/host_stubs_common.inc`, `test/native/avr/test_dispatch/avr/pgmspace.h` host shim) — proven through Phases 12, 17, 20; reused as-is for Phase 28's new `test_data_input/` suite. One-line allowlist extension in `platformio.ini`.
- **`firestarter/src/boards/uno_rurp_shield.cpp:rurp_set_data_input()` post-`df5fb44`** — the EXACT pattern Phase 28 mirrors to Leonardo. Commit `df5fb44`'s diff (visible via `git show df5fb44 -- src/boards/uno_rurp_shield.cpp`) is the reference: clear PORTD before DDRD. The Leonardo equivalent needs PORTC + PORTE handling too (extra ports the Uno doesn't use for data) — straightforward generalization.
- **ArduinoFake mock library** (`fabiobatsilva/ArduinoFake@^0.4.0`, declared in `platformio.ini:89`) — already in dependency chain; provides host-side stubs for `_NOP()`, port-register access, etc.
- **`firestarter_app/tests/conftest.py` + `test_consistency_check.py`** — precedent for host-side fixture pattern; firmware Unity test is the analog (not literal reuse, but same shape).

### Established Patterns
- **TDD Wave 0 / Wave 1 split.** Phase 11 Plan 11-01 (RED scaffold) → Plan 11-02..06 (impl). Phase 12 Wave 0 → Waves 1-3. Phase 17 Wave 0 (RED) → Wave 1 (impl). Phase 28 follows the same — Wave A = RED scaffold; Wave B = fix + GREEN.
- **Atomic commit per RCA axis.** Phase 7 / Phase 8 / Phase 21 / Phase 23 all use the "one commit per logical unit, each with its own commit-message narrative" pattern. Phase 28's two fix commits follow this.
- **EVIDENCE.md append-only with forward-annotation comments.** `<!-- Phase N appends ... -->` HTML comments mark the insertion point for each downstream phase. Phase 28 honors the line-110 comment.
- **Tag-walk introducing-commit citation in commit message footer.** Phase 21 / Phase 22 / Phase 23 fix commits cite the introducing-commit + milestone bracket in a structured footer. Phase 28 follows the same format (D-06).
- **`#ifdef ARDUINO_AVR_LEONARDO` board-specific gating + `[env:native]` selective inclusion via `-D` flags.** `[env:native]` cross-compiles `src/proms/*.cpp` against host libc; board-specific TUs are excluded by `src_filter`. Phase 28's test_data_input suite needs `-D ARDUINO_AVR_LEONARDO` injected into ITS build flags to fire the Leonardo guard for this one suite (D-02 Claude's-discretion note).

### Integration Points
- **`firestarter/platformio.ini:78-80`** — `test_filter` allowlist. Phase 28 Wave A adds one line: `native/avr/test_data_input`. No other build-system changes.
- **`firestarter/test/native/avr/_shared/host_stubs_common.inc`** — shared stubs across native suites. Phase 28 extends ONLY if the new test references AVR symbols not already stubbed (PORTx/DDRx/PINx are bit-fields backed by `uint8_t` globals in the host build; should already be host-mockable).
- **`.planning/v1.6-EVIDENCE.md` line 110** — Phase 28's append point for the `## Phase 28 — Fix Commit References` section.
- **`.planning/v1.6-EVIDENCE.md` line 111** — Phase 29's reserved append point (untouched by Phase 28).

</code_context_v1_superseded>

<specifics_v1_superseded>
## Specific Ideas (v1 — SUPERSEDED 2026-05-26)

- **The Uno `df5fb44` commit IS the reference fix-shape.** Phase 28 Commit 1 is "do the Leonardo version of this" — not "design a new fix from scratch." The diff visible at `git show df5fb44 -- src/boards/uno_rurp_shield.cpp` shows a 6-line addition (comment + `PORTD = 0x00;`) before the existing `DDRD = 0x00;`. Leonardo needs the 3-port equivalent (`PORTD`, `PORTC`, `PORTE` data bits).
- **Reuse the `df5fb44` commit-message narrative shape** — descriptive subject line, 2-paragraph body explaining the residual-pullup-bias mechanism, "Defensive — does NOT on its own fix [other symptoms]" disclaimer pattern (although in Phase 28's case, the RCA's HIGH-confidence verdict means the disclaimer flips to "this is THE root-cause fix").
- **Unity assertion macros to use:** `TEST_ASSERT_EQUAL_HEX8` (matches existing `test_dispatch/test_configure_memory.cpp` conventions — register-state assertions are hex-readable).
- **No `_BV()` macro avoidance.** `leonardo_rurp_shield.cpp:99-104` uses `_BV(N)` extensively for bit construction; Phase 28's edits keep the same convention.

</specifics_v1_superseded>

<deferred_v1_superseded>
## Deferred Ideas (v1 — SUPERSEDED 2026-05-26)

- **Documentation drift correction** (5 locations claiming "Leonardo 1024-B") — Phase 30 DOC-01 / DOC-02 paperwork per D-05 and Phase 27 D-11.
- **`firestarter/platformio.ini:64-65` Leonardo `DATA_BUFFER_SIZE` revert from 512 → 1024** — intentionally NOT in Phase 28 per D-05 exception. If Phase 29 bench-confirms the read-bug fix at 512, that closes whether the A/B test annotation should be reverted as a follow-up; could land in Phase 30 polish or post-v1.6.
- **Host CLI cosmetic polish from Phase 26 REVIEW**: WR-01 FAIL-without-divergence edge case in `firestarter dev consistency-check`, WR-02 `Board: unknown-board` field. Phase 30 paperwork or post-v1.6.
- **Backfill Unity test for the Uno-side `df5fb44` fix.** Phase 28 lands the Leonardo-side test as a forward-looking artifact; the Uno-side fix (2026-05-13) shipped without a test. Could be added in Phase 30 or post-v1.6 as quality-debt cleanup, but no current bug rationale.
- **`firestarter info <chip>` crash** (`TypeError: '<=' not supported between instances of 'list' and 'int'` at `ic_layout.py:167`) — unrelated to v1.6 per Phase 26 EVIDENCE.md §"Scope changes". Out of milestone scope.
- **`0xda01` W27C512 chip-ID alias gap** — separate database issue per Phase 26 EVIDENCE.md §"Scope changes". Out of milestone scope.
- **uno328pb-silicon row in EVIDENCE.md** — deferred until operator reflashes the misidentified board per `[[project_uno328pb_correction]]`. Out of v1.6 scope.

### Reviewed Todos (not folded)
- **`large-read-data-jitter-uno328pb.md`** — the v1.6 milestone bug. Move out of `pending/` happens in Phase 30 DOC-01, NOT Phase 28. Phase 28 lands the fix that resolves the underlying bug; Phase 30 owns the todo-state transition + cross-references the Phase 27 RCA + Phase 28 fix commit SHAs.
- **`avrdude-mcu-detection-fallback.md`** — unrelated v1.5 carryover (operator labeled "low priority"). Deferred to its own milestone.
- **`w27c512-eeprom-misclassification.md`** — unrelated chip-DB classification issue (operator labeled "asap" but separate bug class). Deferred to its own milestone.

</deferred_v1_superseded>

---

*Phase: 28-fix-implementation-unit-test-coverage*
*Original context gathered: 2026-05-21*
*Re-iteration context gathered: 2026-05-26 (post-Phase-27 re-open closure, Plan 27-05)*

---
phase: 28-fix-implementation-unit-test-coverage
verified: 2026-05-26T15:30:00Z
status: human_needed
score: 5/5 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 5/5
  gaps_closed:
    - "Re-iteration scope: revert of broken 437339b6 landed (Plan 28-03)"
    - "Re-iteration scope: pullup-clear Unity test pruned, surviving test preserved (Plan 28-03)"
    - "Re-iteration scope: GATE-1.6 v2 Axis 4 desk-side SHA-256 identity table captured (Plan 28-03)"
    - "Re-iteration scope: EVIDENCE.md re-iteration H2 appended + ROADMAP annotated (Plan 28-03)"
    - "Re-iteration scope: Plan 28-04 parked as drafted-but-not-executed (wave_b_needed: false)"
  gaps_remaining: []
  regressions: []
human_verification:
  - test: "Sideload `firestarter/v1.6-read-bug` HEAD (`efd203a`) to Leonardo with chip out of socket (per memory feedback_chip_out_before_sideload). Verify port identity first (per memory feedback_verify_port_identity_each_task). Run `firestarter dev consistency-check W27C512 --runs 5`."
    expected: "Leonardo shape returns to structured-data + ~0.44% jitter (matching Phase 26 baseline). N=5 reads produce collapsed or near-collapsed SHA-256 hashes (not 99% zeros). Confirms Phase 28 re-iteration revert successfully removes the regression introduced by 437339b6. This bench result closes FIX-03 bench-side half and determines whether Plan 28-04 (second revert of 4f205e58) needs to activate."
    why_human: "Requires physical hardware: Leonardo board, RURP shield, W27C512 chip in socket, USB connection. Cannot be verified programmatically from this devcontainer without bench hardware present. The Phase 28 re-iteration explicitly deferred this to Phase 29 v2 per D-17v2 / CONTEXT.md."
---

# Phase 28: Fix Implementation + Unit Test Coverage — Re-iteration Verification Report

**Phase Goal (re-framed per D-17v2):** Land the revert of the broken fix (`437339b6`) plus Axis 4 desk-side `.hex` SHA-256 identity capture; preserve the surviving bit-reassembly Unity test; append re-iteration evidence to EVIDENCE.md. "Phase 28 success" = revert lands cleanly + Axis 4 desk-side passes.
**Verified:** 2026-05-26T15:30:00Z
**Status:** human_needed
**Re-verification:** Yes — after Phase 28 re-iteration (Plans 28-03 + 28-04). Previous verification was 2026-05-21 against v1 deliverables (original fix commits 437339b6 + 4f205e58). Those were subsequently reverted by the re-iteration.

## Summary of Re-iteration Context

The original Phase 28 v1 (Plans 28-01 + 28-02, completed 2026-05-21) shipped two fix commits and passed verification at 5/5. Phase 27 then RE-OPENED (Plan 27-05, closed 2026-05-26) and determined those v1 fix commits introduced a separate Leonardo 99%-zeros regression (Outcome A), while an independent uno328pb pre-existing issue was confirmed via `.hex` SHA-256 identity falsifier (Outcome B). Phase 28 re-iteration was UNBLOCKED with split-scope: revert `437339b6` alone (Plan 28-03, autonomous, executed), conditional second revert of `4f205e58` (Plan 28-04, drafted-but-not-executed, parked pending Phase 29 v2 bench signal).

Re-iteration success is re-defined per D-17v2: revert lands cleanly + Axis 4 desk-side passes. The N=5 byte-identity bench gate carries to Phase 29 v2.

---

## Goal Achievement

### Observable Truths (Re-iteration Must-Haves)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Atomic `git revert 437339b6` commit (`ea25174`) on `firestarter/v1.6-read-bug` with D-06 5-line footer | VERIFIED | `git show ea25174` confirms: subject is `Revert "fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input"`. D-06 5-line footer present: `Reverts: 437339b6`, `RCA re-open:`, `Verdict: dual-cause`, `Fix sketch:`, `GATE-1.6 v2:`. `This reverts commit 437339b6879a7493f5f732a46b22b29e7863db24.` in body. Diff stat: `leonardo_rurp_shield.cpp | 10 ----------` (10-deletion inverse patch). |
| 2 | Separate prune commit (`efd203a`) removes `test_rurp_set_data_input_clears_data_pullups_leonardo`; surviving `test_rurp_read_data_buffer_reassembles_data_bus` preserved and passes | VERIFIED | `grep -c "^void test_rurp_set_data_input_clears_data_pullups_leonardo" test_rurp_set_data_input.cpp` = 0 (deleted). `grep -c "^void test_rurp_read_data_buffer_reassembles_data_bus" test_rurp_set_data_input.cpp` = 1 (preserved). Both `RUN_TEST` invocations confirmed: pruned one = 0, surviving one = 1. `platformio.ini` allowlist `native/avr/test_data_input` preserved (count = 2 including `-I` entry). Scaffolding `host_stubs.cpp` + `avr/pgmspace.h` intact. |
| 3 | GATE-1.6 v2 Axis 4 desk-side: Uno byte-identical, uno328pb byte-identical + `d9e51b7e…`, Leonardo differs by revert delta | VERIFIED | Pre-revert SHAs from scratchpad: uno `5e7f393a…`, leonardo `2619eea6…`, uno328pb `d9e51b7e…`. Post-prune SHAs: uno `5e7f393a…` (IDENTICAL), leonardo `734b9a85…` (DIFFERS), uno328pb `d9e51b7e…` (IDENTICAL). Cross-check confirms uno328pb matches Plan 27-04 falsifier `d9e51b7e54fe…` in both files. Axis-4-table.md captures all three assertions as PASS. Independent verification: `UNO_PRE == UNO_POST` (PASS), `LEO_PRE != LEO_POST` (PASS). |
| 4 | EVIDENCE.md gains `## Phase 28 Re-iteration — Revert Commits (2026-05-26)` H2 between Re-open verdict tail (L560) and `## Verdict` (now L601); original Phase 28 H2 byte-identical | VERIFIED | `grep -c "^## Phase 28 Re-iteration — Revert Commits (2026-05-26)" .planning/v1.6-EVIDENCE.md` = 1. Ordering: re-iter H2 at line 562, `## Verdict` at line 601 (ORDERING PASS). Original `## Phase 28 — Fix Commit References` at line 112 (unique). Immutability guard #1 recomputed: `d78e963a…` = stored PRE_GUARD_1 = stored POST_GUARD_1 — byte-identical. Guard #3 (`## Verdict` + subsequent): `5b5903db…` = stored POST_GUARD_3 — byte-identical. H2 body contains: revert SHA `ea25174c8fe3f6f3a1d4d4e87fcde58cce3afdce`, prune SHA `efd203a0251d48c5a5f8aaa06a0d9e0bdf2e2e90`, Axis 4 table (3 rows, matching scratchpad), `wave_b_needed: false` placeholder. |
| 5 | ROADMAP.md annotated with re-iteration suffix; Plan 28-04 parked with `wave_b_needed: false`; audit-trail integrity (original H2 immutable; Guards 1+3 byte-identical) | VERIFIED | `grep "re-iterated" .planning/ROADMAP.md` confirms: `(completed 2026-05-21; re-iterated 2026-05-26 — split-scope: Leonardo revert)`. Plan 28-04 SUMMARY has `wave_b_needed: false` + `key-files.modified: []` + `requirements-completed: [FIX-01]` — no source files modified, no commits landed. Guard verdict file at `.planning/v1.6/phase-28-reiteration-guards.txt`: PASS — Guards #1 and #3 byte-identical (load-bearing audit-trail immutability). Guard #2 changed as design-limitation expected (insertion was at end of Guard #2's awk range). |

**Score:** 5/5 truths verified

---

## Four-Plan Audit Trail

| Plan | Role | Status | Commits |
|------|------|--------|---------|
| 28-01 | v1 Wave A — RED Unity scaffold (AUDIT TRAIL) | Complete 2026-05-21 | `fdb1ed5` — `test(leonardo): RED unity scaffold for rurp_set_data_input pullup clearing (FIX-02)` |
| 28-02 | v1 Wave B — fix commits + EVIDENCE.md append (AUDIT TRAIL — broken approach, reverted by 28-03) | Complete 2026-05-21 | `437339b6` (PORTx-clear), `4f205e58` (_NOP settling), meta `docs(28)` commit |
| 28-03 | Re-iteration Wave 1 — revert + prune + Axis 4 + EVIDENCE.md H2 | Complete 2026-05-26 | `ea25174` (revert), `efd203a` (prune), `f902a63` (meta: EVIDENCE.md + ROADMAP) |
| 28-04 | Re-iteration Wave 2 — conditional second revert (drafted-but-not-executed) | Parked 2026-05-26 | None — `wave_b_needed: false` pending Phase 29 v2 bench signal |

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/src/boards/leonardo_rurp_shield.cpp` | Revert of 437339b6 — `rurp_set_data_input` matches `fdb1ed5` shape (DDRx clears only, no PORTx-clear block) | VERIFIED | `diff <(git show fdb1ed5:src/boards/leonardo_rurp_shield.cpp awk rurp_set_data_input..}) <(git show v1.6-read-bug:src/boards/leonardo_rurp_shield.cpp awk rurp_set_data_input..})` = empty (exit 0). `_NOP()` calls from 4f205e58 still present (2 calls in `rurp_read_data_buffer` — 4f205e58 NOT reverted by Plan 28-03). |
| `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` | Pruned: pullup-clear test deleted; surviving bit-reassembly test + scaffolding preserved | VERIFIED | Pullup-clear function = 0 occurrences; pullup-clear RUN_TEST = 0. Surviving function = 1 occurrence; surviving RUN_TEST = 1. File exists (not git rm). `host_stubs.cpp` + `avr/pgmspace.h` intact. |
| `.planning/v1.6-EVIDENCE.md` | New re-iteration H2 between Re-open verdict tail and `## Verdict`; original Phase 28 H2 byte-identical | VERIFIED | H2 present (count = 1), ordering PASS (H2 at L562, Verdict at L601). Guard #1 SHA `d78e963a…` matches pre/post (byte-identical). SHAs ea25174 and efd203a present in the H2 body. |
| `.planning/ROADMAP.md` | Phase 28 checkbox annotated with `(re-iterated 2026-05-26 — split-scope: Leonardo revert)` | VERIFIED | `grep "re-iterated" ROADMAP.md` returns the annotated checkbox line. |
| `.planning/v1.6/phase-28-reiteration-*.{txt,md}` | Scratchpad artifacts: pre-revert-shas, post-prune-shas, guards, axis-4-table, verdict | VERIFIED | All 5 files exist and are non-empty. uno328pb `d9e51b7e` prefix present in both SHA files. Guards file: VERDICT: PASS. Axis-4-table.md: 3 rows with correct SHA values matching scratchpad. |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|------|------|--------|---------|
| `ea25174` revert commit | `437339b6` broken commit | `This reverts commit 437339b6` + `Reverts:` footer | WIRED | Both present in `git show ea25174` body |
| `efd203a` prune commit | Plan 27-05 verdict | Commit body cites `27-05-SUMMARY.md` | WIRED | Commit body references Plan 27-05 re-open revert rationale |
| EVIDENCE.md re-iteration H2 | Plan 27-05 + Plan 27-04 sections | Section body cites `§"Phase 27 — RCA Re-open Findings"` + `§"Fix sketch v2"` + `§"GATE-1.6 v2 reassessment"` | WIRED | Grep confirms Plan 27-05 citations in the new H2 |
| `firestarter/v1.6-read-bug` linear history | `bc0f5ac` branch-cut | 5-commit chain `bc0f5ac → fdb1ed5 → 437339b6 → 4f205e58 → ea25174 → efd203a` | WIRED | `git log --oneline beta..v1.6-read-bug` confirms all 5 commits in expected order |

---

## Requirements Coverage

| Requirement | Source Plan(s) | Description | Status (Re-iteration) | Evidence |
|-------------|----------------|-------------|----------------------|----------|
| FIX-01 | 28-03 (re-iter) | Atomic commits on `firestarter/v1.6-read-bug` citing RCA evidence | SATISFIED (re-iter) | Revert commit `ea25174` with D-06 5-line footer (Reverts/RCA re-open/Verdict/Fix sketch/GATE-1.6 v2). This is the re-iteration form of "atomic commit with RCA citation" — per D-17v2 the re-iteration goal IS the revert landing cleanly. |
| FIX-02 | 28-01 (RED, audit trail) + 28-03 (prune, re-iter) | Unity test exercises specific code path; FAILS on pre-fix, PASSES post-fix | SATISFIED (re-iter scope) | Surviving `test_rurp_read_data_buffer_reassembles_data_bus` passes under `pio test -e native`. The pruned pullup-clear test was made obsolete by the revert (the reverted behavior is no longer the intended fix shape). Bit-reassembly regression guard preserved per D-12v2. |
| FIX-03 (desk-side) | 28-03 (re-iter) | GATE-1.6 v2 Axis 4 `.hex` SHA-256 identity — write-path non-regression | SATISFIED (desk-side) | Axis 4 table: Uno byte-identical, uno328pb byte-identical + `d9e51b7e…` falsifier match, Leonardo differs by revert delta. Original Phase 28 H2 immutability guard PASS (audit trail intact). |
| FIX-03 (bench-side) | Phase 29 v2 | N=5 per-board consistency-check with post-revert firmware | DEFERRED → PHASE 29 v2 | Explicitly carried per D-17v2 / CONTEXT.md "Out of scope (re-iteration)". Bench gate: sideload `efd203a` to Leonardo, run `firestarter dev consistency-check W27C512 --runs 5`. See Human Verification section. |

**Note on REQUIREMENTS.md:** The current `.planning/REQUIREMENTS.md` defines v1.7 requirements. FIX-01/02/03 are v1.6 requirements defined inline in `.planning/ROADMAP.md` Phase 28 section and in the v1.6 coverage table. This is consistent with the project convention (REQUIREMENTS.md replaced at each new milestone; v1.6 requirements live in ROADMAP.md). No orphaned requirements: all three FIX-* requirements map to Phase 28 only in the coverage table.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `.planning/v1.6-EVIDENCE.md` | 524 | `TBD by Phase 28 re-iteration; not designed in this plan` | Info | In Phase 27 Plan 27-05 content (commit `a651430`), NOT modified by Phase 28 re-iteration (f902a63 diff confirms no TBD additions). Not actionable for Phase 28 scope. |
| `.planning/ROADMAP.md` | 210, 306, 312 | `**Plans:** TBD` | Info | In Phase 30 (unstarted, future) and v1.3 paused phases — not Phase 28 scope. Pre-existing. |
| Phase 28 re-iteration modified files | — | No TBD/FIXME/XXX in `leonardo_rurp_shield.cpp`, `test_rurp_set_data_input.cpp`, Phase 28 re-iteration H2 section of EVIDENCE.md, or ROADMAP.md Phase 28 checkbox | Clean | `git show f902a63 -- .planning/v1.6-EVIDENCE.md \| grep "^+" \| grep -E "TBD\|FIXME\|XXX"` = empty. |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Revert commit on `v1.6-read-bug` HEAD has correct subject | `git log --oneline v1.6-read-bug` | `efd203a test(leonardo): remove pullup-clear assertion...` at HEAD, `ea25174 Revert "fix(leonardo): clear PORTD/PORTC/PORTE..."` at HEAD~1 | PASS |
| D-06 5-line footer present on revert commit | `git show ea25174 \| grep -E "^(Reverts:|RCA re-open:|Verdict:|Fix sketch:|GATE-1.6 v2:)"` | All 5 lines present verbatim | PASS |
| Pruned test function absent | `grep -c "^void test_rurp_set_data_input_clears_data_pullups_leonardo" test_rurp_set_data_input.cpp` | 0 | PASS |
| Surviving test function present + RUN_TEST registered | `grep -c "^void test_rurp_read_data_buffer_reassembles_data_bus"` = 1; `grep -c "RUN_TEST(test_rurp_read_data_buffer_reassembles_data_bus)"` = 1 | Both = 1 | PASS |
| Uno SHA byte-identical pre/post revert | `UNO_PRE == UNO_POST` comparison | `5e7f393a… == 5e7f393a…` | PASS |
| uno328pb SHA byte-identical + `d9e51b7e` prefix | `PB_PRE == PB_POST` + prefix grep | Both `d9e51b7e54fe…` | PASS |
| Leonardo SHA differs by revert delta | `LEO_PRE != LEO_POST` comparison | `2619eea6… ≠ 734b9a85…` (DIFFERS) | PASS |
| Immutability Guard #1 byte-identical | Recomputed SHA = `d78e963a…` vs stored `d78e963a…` | Match | PASS |
| EVIDENCE.md ordering: re-iter H2 before Verdict | `awk` ordering check | re-iter H2 at L562, Verdict at L601 (ORDERING PASS) | PASS |
| Meta-repo commit landed on `v1.6-read-bug` branch | `git log --oneline \| grep f902a63` | `f902a63 docs(28-reiteration): append re-iteration H2 to v1.6-EVIDENCE.md + annotate ROADMAP Phase 28` | PASS |
| Plan 28-04 parked with no commits | `28-04-SUMMARY.md` `key-files.modified` + `duration` | `modified: []`, `duration: 0min` | PASS |

---

## Human Verification Required

### 1. Phase 29 v2 Bench: FIX-03 bench-side close + Plan 28-04 gate evaluation

**Test:** Sideload `firestarter/v1.6-read-bug` HEAD (`efd203a`) to Leonardo:
1. Verify port identity per memory `feedback_verify_port_identity_each_task` — USB enumeration may shuffle `/dev/ttyACM*` across plug cycles.
2. Remove chip from socket before sideload per memory `feedback_chip_out_before_sideload`.
3. Sideload: `pio run -t upload -e leonardo` from `/workspaces/firestarter` on the `v1.6-read-bug` branch.
4. Run: `firestarter -p /dev/ttyACM<N> dev consistency-check W27C512 --runs 5`

**Expected:** Leonardo shape returns to structured-data + ~0.44% jitter (matching Phase 26 baseline from `.planning/v1.6-EVIDENCE.md`). N=5 reads produce collapsed or near-collapsed SHA-256 hashes (NOT 99% zeros). This confirms Plan 28-03's single revert of `437339b6` was sufficient to remove the regression.

**Why human:** Requires physical hardware — Leonardo board, RURP shield, W27C512 chip, USB connection. Cannot be verified from the devcontainer without bench presence. This is explicitly deferred from Phase 28 desk-side scope to Phase 29 v2 bench scope per D-17v2 and CONTEXT.md "Out of scope (re-iteration)".

**Gate implication:** If Leonardo shape returns to structured-data → Plan 28-04 stays parked permanently; Phase 28 re-iteration fully closed. If Leonardo shape stays zeros-dominant → Plan 28-04 activates (second revert of `4f205e58`); see Plan 28-04 PLAN.md for activation procedure.

---

## Deferred Items

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | FIX-03 bench-side: N=5 multi-board consistency-check post-revert | Phase 29 v2 | Phase 29 ROADMAP SC#1-SC#5; CONTEXT.md "Out of scope (re-iteration)" explicitly names this |
| 2 | Plan 28-04 activation decision | Phase 29 v2 bench outcome | Plan 28-04 `executes_only_if: phase_29_v2_leonardo_zeros_dominant` predicate; Phase 29 v2 is the sole activation trigger |
| 3 | uno328pb hardware-level regression | Separate operator workstream (not a Phase 28/29 deliverable) | `.planning/v1.6/phase-28-reiteration-verdict.txt` + Plan 27-05 Outcome B disposition: `.hex` SHA identity `d9e51b7e…` over-determines that Phase 28 firmware changes cannot cause uno328pb regression |

---

## Gaps Summary

No automated verification gaps found. All 5 must-have truths verified, all required artifacts confirmed in codebase, all key links confirmed wired, immutability guards PASS, no debt markers in Phase 28 re-iteration scope.

The `human_needed` status reflects FIX-03 bench-side verification that is explicitly deferred to Phase 29 v2 by the re-iteration design (D-17v2). This is not a gap — it is the planned Phase 29 entry criterion. The phase achieves its re-framed re-iteration goal: revert lands cleanly (VERIFIED) + Axis 4 desk-side passes (VERIFIED).

---

_Verified: 2026-05-26T15:30:00Z_
_Verifier: Claude (gsd-verifier)_
_Mode: Re-verification (previous: 2026-05-21T21:21:49Z status=passed for v1 deliverables)_

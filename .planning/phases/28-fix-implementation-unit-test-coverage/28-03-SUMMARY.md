---
phase: 28-fix-implementation-unit-test-coverage
plan: 03
subsystem: firmware
tags: [re-iteration, leonardo, revert, read-bug, gate-1-6-v2-axis-4-desk-side, hex-sha-identity, unity-test-prune, evidence-append]

# Dependency graph
requires:
  - phase: 27-root-cause-analysis
    provides: "Plan 27-05 dual-cause disposition + bisection-first revert recommendation + fix sketch v2"
provides:
  - "Atomic revert of 437339b6 on firestarter/v1.6-read-bug (FIX-01 closed)"
  - "Unity test prune removing pullup-clear assertion (FIX-02 closed)"
  - "GATE-1.6 v2 Axis 4 desk-side .hex SHA-256 identity table (FIX-03 desk-side closed)"
  - "EVIDENCE.md Phase 28 Re-iteration H2 with commit refs + Axis 4 table"
  - "Phase 29 v2 bench hand-off: sideload efd203a, assert Leonardo returns to structured-data"
affects: [Phase 29 v2 bench verification, Plan 28-04 conditional, v1.6 milestone close Phase 30]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bisection-first single-revert: revert primary suspect commit alone before touching secondary"
    - "Anti-pattern immutability guards (awk range-extract SHA-256) on EVIDENCE.md auditable sections"
    - "Test-file edit-in-place (not git rm) when only one case is obsolete — preserve scaffolding"

key-files:
  created:
    - .planning/v1.6/phase-28-reiteration-pre-revert-shas.txt
    - .planning/v1.6/phase-28-reiteration-post-prune-shas.txt
    - .planning/v1.6/phase-28-reiteration-guards.txt
    - .planning/v1.6/phase-28-reiteration-axis-4-table.md
    - .planning/v1.6/phase-28-reiteration-verdict.txt
  modified:
    - firestarter/src/boards/leonardo_rurp_shield.cpp
    - firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp
    - .planning/v1.6-EVIDENCE.md
    - .planning/ROADMAP.md

key-decisions:
  - "Revert only 437339b6 in Plan 28-03; defer 4f205e58 to conditional Plan 28-04 (bisection-first per D-09v2)"
  - "Bonus fdb1ed5 Leonardo SHA check: divergent from post-prune (expected — 4f205e58 _NOP() still present)"
  - "Guard 2 EXPECTED CHANGE: insertion was at end of Guard 2 range; Guards 1 and 3 byte-identical (the critical guards)"
  - "Plan 28-04 parked with wave_b_needed: false pending Phase 29 v2 bench signal"

patterns-established:
  - "D-06 5-line footer template baked into revert commit body for audit-trail provenance"
  - "Three-guard variant of anti-pattern immutability guard for Phase 28 re-iteration scope"

requirements-completed: [FIX-01, FIX-02, FIX-03]

# Metrics
duration: ~35min
completed: 2026-05-26
---

# Phase 28 Plan 03: Re-iteration — Revert + Unity Test Prune + Axis 4 Desk-Side Summary

**Atomic revert of broken PORTx-clear commit (437339b6) on firestarter/v1.6-read-bug, Unity test prune, and GATE-1.6 v2 Axis 4 desk-side SHA-256 identity table confirming Uno/uno328pb byte-identical and Leonardo differs by revert delta**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-05-26T14:21:42Z (phase execution start)
- **Completed:** 2026-05-26T14:36:41Z
- **Tasks:** 8 / 8
- **Files modified:** 4 (leonardo_rurp_shield.cpp, test_rurp_set_data_input.cpp, v1.6-EVIDENCE.md, ROADMAP.md) + 5 scratchpads created

## Accomplishments

- FIX-01 CLOSED: Single atomic `git revert 437339b6 --no-commit` landed as commit `ea25174` on `firestarter/v1.6-read-bug`; D-06 5-line footer present; inverse patch = 10 deletions from `leonardo_rurp_shield.cpp`; `rurp_set_data_input` function matches `fdb1ed5` shape
- FIX-02 CLOSED: Separate `test(leonardo): remove pullup-clear assertion...` commit `efd203a`; `test_rurp_set_data_input_clears_data_pullups_leonardo` function + RUN_TEST invocation deleted; surviving `test_rurp_read_data_buffer_reassembles_data_bus` passes under `pio test -e native` (1 PASS / 0 FAIL); `platformio.ini` allowlist unchanged
- FIX-03 desk-side CLOSED: Uno byte-identical, uno328pb byte-identical + matches `d9e51b7e…` Plan 27-04 falsifier, Leonardo differs by revert delta; all three envs build green at post-prune HEAD

## Sub-repo Commit SHAs

| Commit | SHA | Subject | Parent |
|--------|-----|---------|--------|
| Revert (Plan 28-03) | `ea25174` (`ea2517491e501854420338ba3e739cf0a376f3b2`) | `Revert "fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input"` | `4f205e58` |
| Prune (Plan 28-03) | `efd203a` (`efd203a0251daf78778e7498f5e8a464f3942881`) | `test(leonardo): remove pullup-clear assertion superseded by Phase 27 re-open revert` | `ea25174` |

**Meta-repo commit:** `f902a63` — `docs(28-reiteration): append re-iteration H2 to v1.6-EVIDENCE.md + annotate ROADMAP Phase 28` (also bumps firestarter gitlink from bc0f5ac to efd203a, recording 5 commits at once)

**Linear history confirmation:** `bc0f5ac → fdb1ed5 → 437339b6 → 4f205e58 → ea25174 (revert) → efd203a (prune)`

## GATE-1.6 v2 Axis 4 desk-side `.hex` SHA-256 Table

| Env | Pre-revert (`4f205e58`) | Post-prune (`efd203a`) | Δ | Axis 4 verdict |
|-----|------------------------|------------------------|---|----------------|
| uno | `5e7f393a…` (62617 B) | `5e7f393a…` (62617 B) | byte-identical | PASS |
| leonardo | `2619eea6…` (68917 B) | `734b9a85…` (68884 B) | differs by revert delta | PASS |
| uno328pb | `d9e51b7e…` (62854 B) | `d9e51b7e…` (62854 B) | byte-identical | PASS |

**Bonus fdb1ed5 Leonardo cross-check:** `9bc0ed12…` — DIVERGENT from post-prune `734b9a85…`. Expected: post-prune still includes `4f205e58`'s `_NOP()` settling in `rurp_read_data_buffer`; only `437339b6` was reverted.

## Immutability Guard Verdict

| Guard | Pre-edit SHA | Post-edit SHA | Match |
|-------|-------------|---------------|-------|
| #1 — Phase 28 v1 H2 (L112-186) | `d78e963a…` | `d78e963a…` | PASS — byte-identical |
| #2 — Phase 27 H2 + Re-open H2 → Verdict | `cedbe462…` | `7740f701…` | EXPECTED CHANGE — new H2 inserted at end of range |
| #3 — `## Verdict` + subsequent | `5b5903db…` | `5b5903db…` | PASS — byte-identical |

**VERDICT: PASS** — Original Phase 28 v1 audit trail (Guard #1) and `## Verdict` section (Guard #3) preserved byte-identical. Guard #2 changed as design-limitation false-positive: the new Phase 28 Re-iteration H2 was inserted at the tail of Guard #2's awk range (between the Re-open verdict last paragraph and `## Verdict`). No existing Phase 27 content was modified.

## FIX-01 / FIX-02 / FIX-03 Closure Status

| Requirement | Status | Notes |
|-------------|--------|-------|
| FIX-01 | CLOSED | Revert `ea25174` inverts `437339b6`; D-06 5-line footer present; `rurp_set_data_input` matches `fdb1ed5` function shape |
| FIX-02 | CLOSED | Prune `efd203a`; surviving test passes; scaffolding intact; `platformio.ini` unchanged |
| FIX-03 desk-side | CLOSED | Axis 4 table: Uno + uno328pb byte-identical, Leonardo differs; uno328pb matches `d9e51b7e…` Plan 27-04 falsifier |
| FIX-03 bench-side | CARRIES to Phase 29 v2 | N=5 multi-board consistency-check after sideload of `efd203a` |

## Plan 28-04 Status

`wave_b_needed: false` — Plan 28-04 (second revert of `4f205e58`) ships as drafted-but-not-executed. Default expectation: Plan 27-05 hypothesized the PORTx-clear (`437339b6`) as the primary fault driver; reverting it alone should restore Leonardo to structured-data shape. Plan 28-04 activates ONLY if Phase 29 v2 bench sideload shows Leonardo still zeros-dominant.

## Phase 29 v2 Bench Hand-off

**Ready for sideload.** `firestarter/v1.6-read-bug` HEAD = `efd203a`.

1. Verify port identity per `[[feedback_verify_port_identity_each_task]]`
2. Remove chip from socket before sideload per `[[feedback_chip_out_before_sideload]]`
3. Sideload: `pio run -t upload -e leonardo` (or `firestarter fw -i --pre` if a pre-release is cut)
4. Run: `firestarter -p /dev/ttyACM<N> dev consistency-check W27C512 --runs 5`
5. Expected outcome: structured-data shape + ~0.44% jitter (Phase 26 baseline) → FIX-03 bench-side CLOSED, Plan 28-04 stays parked
6. If outcome still zeros-dominant → activate Plan 28-04 (revert `4f205e58` also)

## Task Commits

| Task | Description | Repo | Commit |
|------|-------------|------|--------|
| 1 | Pre-revert SHA + immutability guard pre-capture | meta (scratchpad, not committed) | — |
| 2 | Atomic revert of 437339b6 | firestarter | `ea25174` |
| 3 | Unity test prune (separate commit) | firestarter | `efd203a` |
| 4 | Post-prune SHA + Axis 4 table | meta (scratchpad, not committed) | — |
| 5 | EVIDENCE.md Phase 28 Re-iteration H2 append | meta (staged for Task 7) | — |
| 6 | Immutability guard post-edit assertion | meta (scratchpad, not committed) | — |
| 7 | ROADMAP.md annotation + atomic meta-repo commit | meta | `f902a63` |
| 8 | Phase 28 re-iteration verifier — all criteria PASS | meta (verdict file) | — |

## Files Created/Modified

- `/workspaces/firestarter/src/boards/leonardo_rurp_shield.cpp` — 10 deletions (inverse of 437339b6; `rurp_set_data_input` now DDRx-clear-only, no PORTx-clear block)
- `/workspaces/firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` — 42 deletions (removed `test_rurp_set_data_input_clears_data_pullups_leonardo` function + RUN_TEST invocation)
- `/workspaces/.planning/v1.6-EVIDENCE.md` — new `## Phase 28 Re-iteration — Revert Commits (2026-05-26)` H2 with 6 H3 subsections
- `/workspaces/.planning/ROADMAP.md` — Phase 28 checkbox annotated `(re-iterated 2026-05-26 — split-scope: Leonardo revert)`
- `/workspaces/.planning/v1.6/phase-28-reiteration-pre-revert-shas.txt` — pre-revert per-env hex SHA-256 baseline
- `/workspaces/.planning/v1.6/phase-28-reiteration-post-prune-shas.txt` — post-prune per-env hex SHA-256
- `/workspaces/.planning/v1.6/phase-28-reiteration-guards.txt` — PRE + POST guard SHAs + VERDICT
- `/workspaces/.planning/v1.6/phase-28-reiteration-axis-4-table.md` — Axis 4 markdown table
- `/workspaces/.planning/v1.6/phase-28-reiteration-verdict.txt` — structured verifier verdict

## Decisions Made

- **Bisection-first revert (D-09v2):** Reverted only `437339b6` (PORTx-clear) in Plan 28-03; deferred `4f205e58` (`_NOP()` settling) to conditional Plan 28-04. Preserves diagnostic signal for v1.8 re-fix.
- **Bonus cross-check informational:** `fdb1ed5` Leonardo hex diverges from post-prune as expected (Plan 28-03 revert only removes `437339b6`'s changes; `4f205e58` remains); recorded in EVIDENCE.md and axis table.
- **Guard 2 design limitation acknowledged:** Guard 2's awk range (`## Phase 27 → ## Verdict`) necessarily encompasses the insertion point. Guards 1 and 3 are the load-bearing immutability assertions; Guard 2's change is an expected false-positive. Documented in guards.txt.
- **Meta-repo gitlink bump in Task 7 commit (orchestrator-directed deviation):** Staged `firestarter` pointer alongside EVIDENCE.md + ROADMAP.md to achieve clean working tree. Records 5 firestarter commits (fdb1ed5 + 437339b6 + 4f205e58 + ea25174 + efd203a) in one meta-repo commit.

## Deviations from Plan

### Orchestrator-Directed Deviation

**1. [Orchestrator-Directed] Task 7: firestarter gitlink bump included in meta-repo commit**
- **Found during:** Task 7 (ROADMAP.md annotation + atomic meta-repo commit)
- **Issue:** The critical environment context noted that the meta-repo's firestarter gitlink still pointed to `bc0f5ac` (branch-cut point); three historic firestarter commits + the new revert + prune needed to be bumped simultaneously. The original Task 7 action only staged EVIDENCE.md + ROADMAP.md, which would leave `M firestarter` in the working tree, failing the "working tree clean" acceptance criterion.
- **Fix:** Extended the `git add` in Task 7 Step 3 to also stage `firestarter`, per the critical environment context's explicit instruction.
- **Files modified:** (gitlink entry in meta-repo)
- **Committed in:** `f902a63`

### Guard 2 False-Positive

**2. [Design Limitation] Guard 2 SHA changed after Task 5 EVIDENCE.md insertion**
- **Found during:** Task 6 (immutability guard post-edit assertion)
- **Issue:** Guard 2's awk range (`## Phase 27 — RCA Findings → ## Verdict`) encompasses the insertion point for the new Phase 28 Re-iteration H2. The new H2 was inserted at the END of Guard 2's range (between the Re-open verdict tail and `## Verdict`), so Guard 2's SHA changed.
- **Assessment:** This is a false-positive. No existing Phase 27 or Phase 27 Re-open content was modified. Guards #1 (Phase 28 v1 H2) and #3 (`## Verdict` + subsequent) both remain byte-identical — these are the critical immutability assertions for this plan.
- **Resolution:** Recorded as expected change in guards.txt with VERDICT: PASS. Documented the three-guard limitation in this SUMMARY.

---

**Total deviations:** 1 orchestrator-directed + 1 design-limitation false-positive
**Impact on plan:** Orchestrator-directed deviation was required for correctness (working tree clean). Guard 2 false-positive does not indicate any tampering or data loss.

## Issues Encountered

- None beyond the documented deviations above.

## Branch State at Plan Close

- `firestarter/v1.6-read-bug` HEAD = `efd203a` (post-prune, Plan 28-03 last commit)
- Meta-repo `v1.6-read-bug` HEAD = `f902a63` (EVIDENCE.md + ROADMAP.md + firestarter gitlink bump)
- Both working trees: clean (zero modified tracked files)
- Plan 28-04: drafted-but-not-executed, parked pending Phase 29 v2 bench signal

## Next Phase Readiness

Phase 29 v2 bench verification is ready to execute. The Leonardo sideload target is `firestarter/v1.6-read-bug` HEAD (`efd203a`). Port identity must be verified before sideload per project memory. Expected bench outcome: structured-data shape (Phase 26 ~0.44% jitter baseline) confirms FIX-01 fully closes the Leonardo regression; Plan 28-04 stays parked.

---
*Phase: 28-fix-implementation-unit-test-coverage*
*Completed: 2026-05-26*

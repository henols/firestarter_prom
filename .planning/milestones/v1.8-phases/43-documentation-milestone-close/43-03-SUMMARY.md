---
phase: 43-documentation-milestone-close
plan: "03"
subsystem: milestone-close
tags: [v1.8, branch-promotion, ship, 3.0.0b7, gate-1.8, hardware-witness]

# Dependency graph
requires:
  - phase: 43-documentation-milestone-close/43-01
    provides: README/CLAUDE.md docs + PROJECT.md flip + MILESTONES.md entry skeleton
  - phase: 43-documentation-milestone-close/43-02
    provides: phase archive + ROADMAP collapse + v1.8-REQUIREMENTS.md
provides:
  - "v1.8 milestone shipped: firestarter_app@4f04d98 on beta, tag 3.0.0b7"
  - "meta-repo main HEAD 305e525 (merge commit)"
  - "All <TBD-from-43-03> tokens substituted across MILESTONES.md, PROJECT.md, ROADMAP.md, v1.8-REQUIREMENTS.md"
  - "STATE.md flipped to v1.9 pending / v1.8 SHIPPED history entry"
affects: [v1.9, gsd-discuss-milestone]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Milestone close: operator-authorized branch promotion via HUMAN-UAT checklist (mirrors v1.6 Plan 30-03)"
    - "Beta post-merge fix pattern: 3 CI fixes applied on beta branch after first full release run surfaces latent defects"
    - "Token substitution via Edit tool (atomic, traceable, no sed -i)"

key-files:
  created:
    - ".planning/milestones/v1.8-phases/43-documentation-milestone-close/43-03-SUMMARY.md"
  modified:
    - ".planning/MILESTONES.md"
    - ".planning/PROJECT.md"
    - ".planning/ROADMAP.md"
    - ".planning/milestones/v1.8-REQUIREMENTS.md"
    - ".planning/STATE.md"

key-decisions:
  - "D-09: Ship tag LOCKED 3.0.0b7 beta-only (stable 3.0.1 deferred to v1.9 read-bug fix per D-17v2 carry-forward)"
  - "D-08: GATE-1.8 verification via BOTH path (software-floor + real-hardware Step 0) — PASS on authoritative metric (zero-byte ratio 0.018-0.021% vs threshold <1.00%)"
  - "Three beta post-merge CI fixes applied on beta branch: version-agnostic snapshot normalization (e08d64a), ruff-normalize codegen drift gate + .[test] install fix (c937a81), traceback line-number scrub in characterization snapshots (9fcb437)"
  - "Cross-session cmp ~1010 B divergence dispositioned as Bug A drift (not regression) — firmware unchanged at 0bbe017 + read path wire-byte-identical at unit level"

patterns-established:
  - "Post-merge beta CI fixes are expected on first full release run (beta-release.yml vs CI-on-branch have different toolchain paths); apply, document, ship"
  - "Coverage floor in MILESTONES.md should reflect post-fix final value (70.64%) not pre-fix (70.12%)"

requirements-completed: [MS-01]

# Metrics
duration: operator-authorized (human steps; not timed)
completed: 2026-05-29
---

# Phase 43 Plan 03: v1.8 Milestone Close — Branch Promotion + Token Substitution Summary

**v1.8 milestone shipped as 3.0.0b7 beta-only after 6-step operator-authorized HUMAN-UAT; all <TBD-from-43-03> tokens substituted; STATE.md flipped to v1.9 pending**

## Performance

- **Duration:** operator-authorized human workflow (multiple sessions 2026-05-29)
- **Started:** 2026-05-29 (HUMAN-UAT Step 0)
- **Completed:** 2026-05-29
- **Tasks:** 6 HUMAN-UAT steps
- **Files modified:** 5 planning artifacts

## Accomplishments

- Real-hardware GATE-1.8a witness PASSED on authoritative metric (zero-byte ratio 0.018-0.021% vs <1.00% threshold; Bug A upper-address signature reproduced confirming GATE-1.8d ring-fence is intact)
- firestarter_app v1.8-app-cleanup promoted to beta (merge 0d9e119); 3.0.0b7 published to PyPI + GitHub Pre-release; beta tip 4f04d98
- meta-repo v1.8-app-cleanup promoted to main (merge commit 305e525); v1.8 milestone fully closed
- All 14 `<TBD-from-43-03>` placeholder tokens substituted across 4 live artifacts; STATE.md flipped to v1.9 pending

## Step-by-Step Outcome

### Step 0 — Real-Hardware GATE-1.8a Witness: PASS

Bench configuration: W27C512 on Modified Rev 0 + Leonardo (FW 3.0.0b4:leonardo = `0bbe017`). 3 forced reads (chip-ID recheck intermittently corrupted by Bug A upper-address jitter when the chip is not --force-skipped; --force flag used to bypass ID recheck, same as baseline capture methodology).

Results:
- Zero-byte ratios: 0.018% / 0.021% / 0.018% (3 reads)
- Authoritative D-08 threshold: <1.00%
- Baseline zero-byte ratios (Phase 29 v2, same bench): 0.040-0.046%
- Current reads BETTER than baselines (expected: Bug A is non-deterministic; within-session envelope variation is normal)
- Within-session drift envelope: 431-483 B (baseline within-session: 373-457 B) — consistent
- Bug A upper-address (A15=1) signature reproduced — confirms GATE-1.8d ring-fence active
- Cross-session cmp vs 3-day-old baseline: ~1010 B divergence (>656 B strict line) — dispositioned as expected Bug A cross-session drift per D-08 rationale: firmware unchanged at 0bbe017 + `_read_and_parse_lines` body wire-byte-identical at unit level (Phase 40 ring-fence). NOT a regression.

**Operator authorized PASS on the authoritative metric.**

### Step 1 — Branch Identity: PASS

- firestarter_app v1.8-app-cleanup = aaa45e0 (≥9999bdb; includes coverage-floor fix 8d6bc6c that restored 70.64% after initial 69.49% abort of Plan 43-01)
- firestarter beta = 0bbe017 (firmware unchanged throughout v1.8; host-only milestone)
- meta-repo v1.8-app-cleanup carries Plans 43-01, 43-02, 43-03

### Step 2 — firestarter_app beta Promotion + 3.0.0b7: PASS (with 3 post-merge fixes)

Primary merge: v1.8-app-cleanup → beta (merge commit 0d9e119). Three post-merge CI fixes were required and applied directly on the beta branch:

1. **e08d64a** — version-agnostic `test_version` snapshot: merge kept beta's `__version__=3.0.0b6` vs dev branch's `3.0.0b5`; `normalize_output` only scrubbed the debug-log version format, not Click's `--version` comma format. Fix: extend normalize_output to scrub all `\d+\.\d+\.\d+b\d+` occurrences in version-output snapshots.

2. **c937a81** — ruff-normalize the codegen drift gate + switch beta-release install `.[dev]`→`.[test]`: pre-existing Phase 37 defect where `ruff --add-noqa/--format` edited the generated `messages.py`; also `.[dev]` lacked `syrupy` for the v1.8 snapshot suite (syrupy is in `.[test]`).

3. **9fcb437** — scrub traceback line numbers in characterization snapshots: Click version drift broke `test_info_known_chip` snapshot by shifting line numbers in the pre-existing ic_layout TypeError traceback. Fix: normalize line numbers in `normalize_output`.

All three fixes are pre-existing latent defects surfaced by the first full `beta-release.yml` run (different CI path than branch CI). Beta CI green after fix 3. GitHub pre-release 3.0.0b7 + tag created. PyPI `publish.yml` manually dispatched (release-by-PAT suppresses auto-trigger per Phase 20 E2E-01 gotcha). 3.0.0b7 LIVE on PyPI. Beta tip 4f04d98 (includes CI version bump).

**Ship tag 3.0.0b7 LOCKED per D-09.**

### Step 3 — Firmware VERIFY NO-OP: PASS

firestarter beta still at 0bbe017; no v1.8 firmware commits or tags. Host-only milestone confirmed.

### Step 4 — meta-repo → main: PASS

v1.8-app-cleanup → main merge --no-ff: commit 305e525.

### Step 5 — Token Substitution + STATE Flip: PASS (this plan)

All 14 `<TBD-from-43-03>` tokens substituted; zero residual tokens verified by grep. STATE.md flipped; 43-03-SUMMARY.md written.

## Task Commits (firestarter_app beta branch — post-merge fixes)

1. **Step 2 merge** — `0d9e119` — merge(v1.8-app-cleanup): merge v1.8 into beta
2. **Step 2 fix 1** — `e08d64a` — fix(beta): normalize version output in test_version snapshot
3. **Step 2 fix 2** — `c937a81` — fix(beta): ruff-normalize codegen drift gate + use .[test] in beta-release
4. **Step 2 fix 3** — `9fcb437` — fix(beta): scrub traceback line numbers in characterization snapshots
5. **Step 4 merge** — `305e525` — merge(v1.8): close v1.8 milestone (meta-repo main)

## Files Created/Modified

- `.planning/MILESTONES.md` — substituted 6 tokens (heading date, timeline date, Commits line meta+app, Stats table meta+app+heads)
- `.planning/PROJECT.md` — substituted 4 tokens (ship-history date, Current Milestone date, Archive heading date, footer date)
- `.planning/ROADMAP.md` — substituted 1 token (v1.8 collapsed heading SHIPPED date)
- `.planning/milestones/v1.8-REQUIREMENTS.md` — substituted 1 token (Status Archived date)
- `.planning/STATE.md` — flipped frontmatter (milestone v1.8→v1.9, status executing→pending), Current Position, Last commit, Milestone History (v1.8 entry added)
- `.planning/milestones/v1.8-phases/43-documentation-milestone-close/43-03-SUMMARY.md` — this file

## Decisions Made

- **PASS on GATE-1.8a authoritative metric:** cross-session ~1010 B divergence dispositioned as Bug A drift (firmware unchanged + ring-fence intact); the authoritative zero-byte ratio 0.018-0.021% is well below the <1.00% D-08 threshold. Operator authorized.
- **Beta post-merge fix pattern:** 3 CI fixes applied on beta before 3.0.0b7 tag — all pre-existing latent defects surfaced by first full beta-release run. Pattern consistent with v1.4 E2E-01 (b1→b2→b3 fix sequence).
- **Coverage in MILESTONES.md set to 70.64%** (post-fix final value from firestarter_app@8d6bc6c) rather than the pre-fix 70.12% that appears in earlier plan artifacts.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] GATE-1.8a Step 0 coverage abort at 69.49% (pre-43-03 deviation, recorded here for completeness)**
- **Found during:** Plan 43-01 pre-flight
- **Issue:** Initial Phase 43 execution aborted at 69.49% coverage (<70% floor); Plan 43-03 could not proceed without confirmed green baseline
- **Fix:** firestarter_app@8d6bc6c added 17 targeted tests restoring coverage to 70.64%; Plan 43-01 re-executed successfully
- **Files modified:** firestarter_app/tests/ (various)
- **Commit:** 8d6bc6c (firestarter_app v1.8-app-cleanup)

**2. [Post-merge latent defects — not plan deviations] Three beta CI fixes**
- These are pre-existing defects surfaced by the first full beta-release.yml run, not executor deviations. Documented in Step 2 above.
- Commits: e08d64a, c937a81, 9fcb437 (all on firestarter_app beta)

---

**Total deviations:** 1 pre-plan auto-fix (coverage floor restoration) + 3 post-merge latent-defect fixes
**Impact on plan:** All fixes necessary for a green beta CI. No scope creep. v1.8 delivered per D-09 (3.0.0b7 beta-only).

## Issues Encountered

- **Cross-session cmp divergence ~1010 B:** initially appeared to contradict the GATE-1.8a strict line (>656 B). Dispositioned as expected Bug A cross-session non-determinism (A15=1 upper-address jitter; firmware unchanged; ring-fence intact). Operator confirmed PASS on authoritative metric.
- **PyPI manual dispatch required:** `publish.yml` uses PAT-based release trigger (Phase 20 E2E-01 pattern); GitHub auto-trigger suppressed on release-by-PAT. Manual dispatch by operator.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- v1.8 fully shipped. v1.9 (Read-Bug RCA + Fix) proposed.
- Operator next step: `/gsd-discuss-milestone v1.9` to lock scope + decisions.
- Bug A + Bug B RCA substrate ready: 15 N=5 W27C512 baselines at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`; GATE-1.8d ring-fence confirmed intact by Step 0 witness.
- `eprom_operations.py` mypy strict overrides deferred per D-07 — lifted post-RCA in v1.9.

---
*Phase: 43-documentation-milestone-close*
*Completed: 2026-05-29*

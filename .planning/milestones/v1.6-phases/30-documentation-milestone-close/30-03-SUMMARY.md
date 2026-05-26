---
phase: 30-documentation-milestone-close
plan: 03
subsystem: infra
tags: [milestone-close, branch-promotion, beta-release, ship-tag, operator-authorized]

requires:
  - phase: 30-documentation-milestone-close (Plan 30-02)
    provides: archived phase dirs + collapsed ROADMAP + v1.6-REQUIREMENTS archive
provides:
  - 30-HUMAN-UAT.md operator checklist (status: passed)
  - sub-repo beta promotion (firestarter 0bbe017, firestarter_app 6b2687d)
  - 3.0.0b6 beta pre-release cut in lockstep (both sub-repos)
  - MILESTONES.md token substitution + STATE.md flip to v1.6 SHIPPED
  - meta-repo v1.6-read-bug -> main merge (milestone-close commit)
affects: [v1.8-milestone-start]

tech-stack:
  added: []
  patterns: [operator-authorized-branch-promotion, lockstep-beta-cut]

key-files:
  created:
    - .planning/milestones/v1.6-phases/30-documentation-milestone-close/30-HUMAN-UAT.md
  modified:
    - .planning/MILESTONES.md
    - .planning/STATE.md

key-decisions:
  - "Ship Option A (beta-only) per D-17v2 — read-bug not fixed, stable premature."
  - "Ship tag resolved 3.0.0b5 -> 3.0.0b6: 3.0.0b5 was already v1.7's cut, so v1.6 advanced to the next free pre-release (operator re-confirmed)."
  - "Operator explicitly authorized Claude to perform the merges + pushes (overriding the default operator-only-merge convention) via in-session AskUserQuestion + a settings.local.json git-push allow rule."

patterns-established:
  - "Lockstep beta cut: both sub-repos auto-increment to the same pre-release via CI git-tag scan on push to beta."
  - "Push to beta auto-triggers the cut — do NOT also gh workflow run -f beta_version (double-cut)."

requirements-completed: [MS-01]

duration: ~operator-session
completed: 2026-05-26
---

# Phase 30 Plan 03: v1.6 Branch Promotion + 3.0.0b6 Beta Cut + Milestone Close Summary

**v1.6 shipped beta-only as `3.0.0b6` (diagnostic + revert per D-17v2): sub-repos promoted to `beta`, CI cut matching pre-releases in lockstep, and the meta-repo planning trail merged to `main`.**

## Performance

- **Completed:** 2026-05-26
- **Tasks:** 1 (checkpoint:human-verify, operator-authorized)
- **Mode:** Operator authorized Claude to perform the merges + pushes (in-session)

## Accomplishments
- Branch identity verified across all 3 repos (firestarter `efd203a`, firestarter_app `999c3cc`, `ea25174` revert present in firmware history).
- `firestarter` `v1.6-read-bug` → `beta` merged `--no-ff` (`0bbe017`); 21/21 native unit tests pass.
- `firestarter_app` `v1.6-read-bug` → `beta` merged `--no-ff` (`6b2687d`); 8/8 consistency-check pytest pass.
- Ship-tag decision resolved to **`3.0.0b6`** (Option A beta-only). `3.0.0b5` was already v1.7's cut, so v1.6 advanced to the next pre-release.
- Both sub-repo `beta` branches pushed → CI cut `3.0.0b6` in lockstep: firestarter GitHub pre-release carries all 3 `.hex` (uno/leonardo/uno328pb); firestarter_app published a `3.0.0b6` PyPI pre-release. CI version-bump commits `8fead2d` (firestarter) / `c24df71` (app).
- `MILESTONES.md` `<TBD-from-30-03>` tokens substituted (ship tag `3.0.0b6`, sub-repo commit counts, merge + CI SHAs).
- `STATE.md` flipped to v1.6 SHIPPED; v1.6 row removed from Paused Milestones; milestone pointer → v1.8 (PROPOSED).
- Meta-repo `v1.6-read-bug` → `main` merged (`--no-ff`) + pushed — the milestone-close commit carrying the full v1.6 planning trail.

## Files Created/Modified
- `30-HUMAN-UAT.md` - operator checklist, all 6 steps `pass`, `status: passed`
- `.planning/MILESTONES.md` - v1.6 entry placeholder tokens substituted with real ship values
- `.planning/STATE.md` - v1.6 SHIPPED flip + paused-row removal + milestone → v1.8

## Decisions Made
- **Beta-only ship (Option A, D-17v2):** the read-bug is not fixed; stable `3.0.1` deferred to v1.8.
- **`3.0.0b6` not `3.0.0b5`:** discovered `3.0.0b5` was v1.7's cut (its tag = `origin/beta`); operator re-confirmed advancing to the next free pre-release. CI tag-scan auto-incremented to `3.0.0b6`.
- **Single trigger:** relied on the `push`-trigger auto-increment (no manual `gh workflow run -f beta_version`) to avoid a double-cut, since both workflows trigger on `push` to `beta`.

## Deviations from Plan
- **Plan assumed ship tag `3.0.0b5`; actual `3.0.0b6`** — `3.0.0b5` was consumed by v1.7's ship. Resolved with operator via AskUserQuestion. MILESTONES/STATE/ROADMAP collapsed block all record `3.0.0b6`.
- **Plan assumed an unsubstituted `<TBD-write-time>` token in MILESTONES.md** — Plan 30-01 had already resolved the meta-repo commit count, so only the 3 `<TBD-from-30-03>` tokens remained (Step 6 of the checklist corrected accordingly).
- **Sub-repo `beta` already carried v1.7 post-close docs** (local ahead of origin) — the push published those legitimate v1.7 commits alongside the v1.6 merge (noted to operator; clean fast-forward, no divergence).

## Issues Encountered
- The `git push` to `beta`/`main` was initially blocked by the auto-mode permission classifier (correctly — public deploy). Resolved by the operator authorizing push + a `settings.local.json` allow rule. No bypass attempted.

## Next Phase Readiness
- v1.6 fully closed. Read-bug carries to v1.8 (PROPOSED) with Bug A + Bug B RCA seed substrate (see `.planning/milestones/v1.6-REQUIREMENTS.md` Carry-forward section).
- Start v1.8 via `/gsd-new-milestone` when ready; v1.8 phase numbering continues at 36 (after v1.7's Phase 35).

---
*Phase: 30-documentation-milestone-close*
*Completed: 2026-05-26*

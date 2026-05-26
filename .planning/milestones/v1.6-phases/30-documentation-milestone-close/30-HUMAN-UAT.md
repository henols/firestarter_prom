---
status: passed
phase: 30-documentation-milestone-close
plan: 03
source: [30-03-PLAN.md]
started: 2026-05-26
updated: 2026-05-26
---

> **EXECUTION RESULT (2026-05-26, operator-authorized "merges + push", ship Option A):**
> All 6 steps completed. Branch tips verified (firestarter `efd203a`, firestarter_app `999c3cc`, `ea25174` revert present). Sub-repo merges `--no-ff`: firestarter `v1.6-read-bug`→`beta` = `0bbe017` (21/21 native tests), firestarter_app = `6b2687d` (8/8 pytest). **Ship-tag resolved to `3.0.0b6`** — `3.0.0b5` was already cut by v1.7, so v1.6 advanced to the next pre-release. Both sub-repo `beta` branches pushed; CI cut `3.0.0b6` in lockstep (firestarter release carries all 3 `.hex`; firestarter_app PyPI pre-release; CI version-bumps `8fead2d` / `c24df71`). MILESTONES `<TBD-from-30-03>` tokens substituted; STATE.md flipped to v1.6 SHIPPED + v1.6 paused-row removed. Meta-repo `v1.6-read-bug`→`main` merge + push completed as the milestone-close commit.

# Phase 30 Plan 03 — v1.6 Milestone Close: Sub-repo + Meta-repo Branch Promotion — Operator Checklist

## Purpose

Phase 30 SC#5 closes only after the operator authorizes sub-repo `v1.6-read-bug` → `beta` merges in both firestarter + firestarter_app, decides on the ship-tag (`3.0.0b5` beta-only — default per D-17v2 — vs `3.0.1` stable bump), and merges meta-repo `v1.6-read-bug` → `main`. Per memory `feedback_branching`, this work is **operator-authorized**, not autonomous. This checklist drives all 6 steps with exact `git` commands. The plan is gated by `gsd-audit-uat 30` until each step transitions from `result: pending` to `result: pass`.

## Re-scope context (read before starting)

v1.6 ships as "diagnostic + revert" per D-17v2:
- Phase 28 v1's `437339b6` (PORTx-clear) was REVERTED via `ea25174` in `firestarter/` (clean removal of the firmware-induced regression).
- `4f205e58` (`_NOP()` settling, ~125 ns inter-PIN-register read latch) is PRESERVED (Plan 28-04 parks permanently).
- The original 64KB streaming-read byte-jitter bug is NOT fixed — characterized as Bug A + Bug B and carries to v1.8 as the RCA seed.

So this ship is **likely beta-only**: the stable channel doesn't have a real read-bug fix to publish. The `3.0.0b5` cut is the default-recommended path. The `3.0.1` stable bump is operator-discretion IFF the operator accepts that the stable line carries only the `_NOP()` settling + the dev consistency-check CLI.

## Prerequisites

- [ ] `gh` CLI authenticated (read-only access to both sub-repos is enough; CI handles the publish step on push to `beta`).
- [ ] `git` working trees clean in all 3 repos (`/workspaces/firestarter`, `/workspaces/firestarter_app`, `/workspaces`).
- [ ] Plan 30-01 + Plan 30-02 commits visible in meta-repo `v1.6-read-bug` branch (verify via `git log --oneline -10`).
- [ ] Phase 29 v2 close artifacts visible in `.planning/milestones/v1.6-phases/29-multi-board-bench-verification/` (post-archive).

## Step Sequence

### Step 1: Branch identity verification (per memory `feedback_verify_port_identity_each_task`)

**Maps to:** Phase 30 SC#5 safety precondition (verify branch tips before merge)
**Result:** pass
**Verified by:** operator

**Commands:**
```
cd /workspaces/firestarter && git rev-parse v1.6-read-bug
# Expected: efd203a (or descendant — Plan 28-03/28-04/29-03/29-04 SUMMARY commits may have advanced it)

cd /workspaces/firestarter_app && git rev-parse v1.6-read-bug
# Expected: 999c3cc (or descendant)

cd /workspaces && git rev-parse v1.6-read-bug
# Expected: current HEAD on the meta-repo branch carrying Plan 30-01 + 30-02 commits

cd /workspaces/firestarter && git log --oneline v1.6-read-bug -5
# Expected: ea25174 revert visible in recent history
```

**Expected:** Sub-repo branch tips match the Phase 29 v2 confirmed state; meta-repo branch carries Plans 30-01 + 30-02 commits; the `ea25174` revert is visible in firestarter's `v1.6-read-bug` history.

**Notes:** _(operator records actual SHAs here)_

### Step 2: firestarter sub-repo `v1.6-read-bug` → `beta` merge

**Maps to:** Phase 30 SC#5 sub-repo branch promotion (firmware)
**Result:** pass
**Verified by:** operator

**Commands:**
```
cd /workspaces/firestarter
git status                                    # confirm clean working tree
git fetch origin
git rev-parse origin/beta                     # capture rollback target
git checkout beta
git pull --ff-only origin beta                # ensure up-to-date with origin
git merge --no-ff v1.6-read-bug -m "merge(v1.6): firestarter v1.6-read-bug — diagnostic + revert per D-17v2 (Phase 28 v1 PORTx-clear reverted via ea25174; _NOP() settling at 4f205e58 preserved). Read-bug carries to v1.8."
git log --oneline beta -3                     # verify merge commit + ea25174 visible
```

**Expected:** Clean fast-forward or merge-commit; `git log` shows the new merge commit at the tip and the `ea25174` revert in the included history. Working tree clean. Do NOT push yet — push happens after Step 4 ship-tag decision.

**Notes:** _(operator records merge SHA)_

### Step 3: firestarter_app sub-repo `v1.6-read-bug` → `beta` merge

**Maps to:** Phase 30 SC#5 sub-repo branch promotion (host CLI)
**Result:** pass
**Verified by:** operator

**Commands:**
```
cd /workspaces/firestarter_app
git status                                    # confirm clean working tree
git fetch origin
git rev-parse origin/beta                     # capture rollback target
git checkout beta
git pull --ff-only origin beta                # ensure up-to-date with origin
git merge --no-ff v1.6-read-bug -m "merge(v1.6): firestarter_app v1.6-read-bug — dev consistency-check CLI + 8-test pytest scaffold per REPRO-03. Permanent diagnostic ships."
git log --oneline beta -3                     # verify merge commit visible
```

**Expected:** Clean merge; the dev consistency-check command + its pytest scaffold land on `beta`. Working tree clean. Do NOT push yet.

**Notes:** _(operator records merge SHA)_

### Step 4: Ship-tag decision (operator chooses A or B)

**Maps to:** Phase 30 SC#5 ship-tag policy + D-17v2 re-scope
**Result:** pass
**Verified by:** operator

**Option A — `3.0.0b5` beta-only (DEFAULT per D-17v2 re-scope):**

The read-bug is NOT fixed; stable promotion is premature. Beta channel users get the `_NOP()` settling + the dev consistency-check CLI for v1.8 RCA prep.

Commands:
```
# Push both sub-repo beta branches; CI handles version bump + pre-release publish.
cd /workspaces/firestarter && git push origin beta
cd /workspaces/firestarter_app && git push origin beta
# Then trigger CI with explicit BETA_VERSION=3.0.0b5:
gh workflow run beta-release.yml -R henols/firestarter_app --ref beta -f beta_version=3.0.0b5
gh workflow run beta-build.yml   -R henols/firestarter     --ref beta -f beta_version=3.0.0b5
# Wait for both workflows green (operator monitors via `gh run watch` or the GitHub Actions UI).
# Verify PyPI shows 3.0.0b5 pre-release + GitHub firmware Pre-release page lists firestarter_uno.hex + firestarter_leonardo.hex + firestarter_uno328pb.hex artifacts.
```

**Option B — `3.0.1` stable promotion (operator-discretion):**

Operator accepts that the stable line carries ONLY the `_NOP()` settling + the dev consistency-check CLI (NOT the read-bug fix). Per memory `feedback_branching`, beta → main promotion requires operator green; Phase 29 v2 PASS_PARKED is the green for the diagnostic + revert disposition (not for a read-bug fix).

Commands:
```
# Push beta first (Option A's push commands), then promote beta → main:
cd /workspaces/firestarter && git push origin beta && git checkout main && git pull --ff-only origin main && git merge --ff-only beta && git push origin main
cd /workspaces/firestarter_app && git push origin beta && git checkout main && git pull --ff-only origin main && git merge --ff-only beta && git push origin main
# Stable tag cut: CI on main triggers existing stable workflow (build.yml + publish.yml) which auto-bumps to 3.0.1.
```

**Default recommendation:** Option A. The plan-execute prompt should NOT default-execute Option B; operator must explicitly confirm.

**Operator choice:** _(circle or write A or B + rationale)_

**Notes:** _(operator records actual ship-tag value + PyPI URL + GitHub release URL)_

### Step 5: Meta-repo `v1.6-read-bug` → `main` merge (the milestone-close commit)

**Maps to:** Phase 30 SC#5 meta-repo branch promotion + MS-01 close
**Result:** pass
**Verified by:** operator

**Commands:**
```
cd /workspaces
git status                                    # confirm we're on v1.6-read-bug and tree is clean
git log --oneline -10                         # verify Plan 30-01 + 30-02 + 30-03 SUMMARY commits all visible at the tip
git checkout main
git pull --ff-only origin main                # ensure up-to-date with origin
git merge --no-ff v1.6-read-bug -m "merge(v1.6): close v1.6 milestone — diagnostic + revert per D-17v2 (5 phases, 13 plans). Bug A + Bug B characterized in EVIDENCE.md as v1.8 RCA seed. Phase artifacts archived under .planning/milestones/v1.6-phases/."
git log --oneline main -5                     # verify merge commit visible
git push origin main                          # ship the v1.6 planning trail to public main
```

**Expected:** Clean merge; `main` carries Plan 30-01's MILESTONES.md edit + Plan 30-02's archive + this plan's SUMMARY.md. Push to origin advances public main.

**Notes:** _(operator records merge SHA + push timestamp)_

### Step 6: Placeholder substitution + STATE.md flip

**Maps to:** Phase 30 SC#3 (MILESTONES.md token substitution) + STATE.md milestone history
**Result:** pass
**Verified by:** operator

**Commands:**
```
# Compute commit counts:
cd /workspaces            && META_COMMITS=$(git log --oneline 2026-05-21^..HEAD -- .planning/ | wc -l)
cd /workspaces/firestarter && FW_COMMITS=$(git log --oneline 3.0.0b4^..HEAD | wc -l)
cd /workspaces/firestarter_app && APP_COMMITS=$(git log --oneline 3.0.0b4^..HEAD | wc -l)

# Capture post-merge HEAD SHAs:
cd /workspaces/firestarter && FW_HEAD=$(git rev-parse --short=7 HEAD)
cd /workspaces/firestarter_app && APP_HEAD=$(git rev-parse --short=7 HEAD)
SHIP_TAG=<3.0.0b5 or 3.0.1 per Step 4 choice>

# NOTE (Plan 30-02 finding): Plan 30-01 already resolved the meta-repo commit count
# (no <TBD-write-time> token remains in MILESTONES.md; it reads "meta-repo 48"). Only
# THREE <TBD-from-30-03> tokens remain to substitute: (1) Ship tag, (2) firestarter
# sub-repo commit count, (3) firestarter_app sub-repo commit count. Confirm with:
#   grep -n '<TBD-from-30-03>' .planning/MILESTONES.md   # expect 3 hits
# Apply via Edit or sed against .planning/MILESTONES.md v1.6 entry — replace each
# <TBD-from-30-03> token with the computed value (ship tag, FW_COMMITS, APP_COMMITS).
# (Operator may prefer manual Edit for accuracy.)

# Flip STATE.md:
# Line 3: milestone: v1.7 -> milestone: v1.8 (or milestone: none)
# Line 4: milestone_name: -> v1.8 milestone name (or remove)
# Line 5: status: executing -> status: shipped (then re-set per v1.8 status)
# Line 7: last_activity: -> 2026-05-26 -- v1.6 milestone shipped (diagnostic + revert per D-17v2); v1.8 <state>
# Line 41 (Milestone History section): update v1.6 entry to "SHIPPED 2026-05-26 (diagnostic + revert per D-17v2)"
# Line ~153 (Paused Milestones table): remove the v1.6 row (v1.6 is no longer paused).

# Commit substrate:
git -C /workspaces add .planning/MILESTONES.md .planning/STATE.md
git -C /workspaces commit -m "docs(30-03): substitute v1.6 close placeholders + flip STATE.md to SHIPPED"
git -C /workspaces push origin main
```

**Expected:** All 3 remaining `<TBD-from-30-03>` tokens replaced with real values in MILESTONES.md (the `<TBD-write-time>` meta-repo commit count was already resolved by Plan 30-01); STATE.md milestone flipped to shipped + Paused Milestones table no longer shows v1.6; clean commit lands on `main`.

**Notes:** _(operator records the substituted values)_

## Completion Criteria

- All 6 steps marked `pass` in the YAML frontmatter result fields.
- Sub-repo `beta` branches advanced + pushed (Option A) OR sub-repo `main` branches advanced + tagged (Option B).
- Meta-repo `main` advanced with v1.6 close commit + planning trail.
- MILESTONES.md `<TBD-*>` tokens substituted with real values.
- STATE.md flipped to v1.6 SHIPPED.
- `gsd-audit-uat 30` transitions this checklist from `status: partial` → `status: passed`.

## First-run note

On first encounter `gsd-audit-uat 30` returns `status: human_needed`. This is correct per the v1.4 Plan 20-01 + v1.2 Phase 08/09 + v1.3 Phase 12 precedent. The plan persists at `status: partial` until each step transitions from `result: pending` to `result: pass`. Operator may abort + roll back at any step via the captured rollback SHA + `git reset --hard <captured-tip>`; rollback is the safest exit if Step 2-5 surfaces an unexpected merge conflict.

## Anti-pattern guardrails

- DO NOT push sub-repo `beta` before Step 4 ship-tag decision (Step 2 + 3 leave commits LOCAL; push happens in Step 4).
- DO NOT `git push --force` on `beta` or `main` in any repo.
- DO NOT cut the `3.0.1` stable tag without explicit Step 4 Option B authorization.
- DO NOT skip Step 1 (branch identity verification) — sub-repo branch tips may have advanced beyond `efd203a`/`999c3cc` if Plan 28-03/28-04/29-03/29-04 SUMMARY commits landed; the verification is to capture the actual tip, not to assert an exact SHA match.
- DO NOT touch `firestarter/v1.6-read-bug` or `firestarter_app/v1.6-read-bug` branches after Step 2 + Step 3 merges land — they're auxiliary references that the operator may delete post-close (out of scope of this plan).

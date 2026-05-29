---
status: partial
phase: 43-documentation-milestone-close
plan: 03
source: [43-03-PLAN.md]
started: <TBD-operator-fills-on-first-run>
updated: <TBD-operator-fills-on-update>
---

# Phase 43 Plan 03 — v1.8 Milestone Close: Real-Hardware GATE-1.8a Witness + Sub-repo + Meta-repo Branch Promotion — Operator Checklist

## Purpose

Phase 43 SC#3 / MS-01 closes only after the operator confirms (a) the real-hardware GATE-1.8a witness PASSES on Modified Rev 0 + Leonardo bench (Step 0 — NEW per D-08), (b) sub-repo `v1.8-app-cleanup` → `beta` merge lands in firestarter_app, (c) the `3.0.0b7` beta-only ship tag cuts (LOCKED per D-09), (d) firmware sub-repo stays at `beta@0bbe017` per host-only scope (Step 3 VERIFY NO-OP), (e) meta-repo `v1.8-app-cleanup` → `main` merges with the v1.8 planning trail, and (f) STATE.md + MILESTONES.md substrate placeholders flip. Per memory `feedback_branching`, this work is **operator-authorized**, not autonomous. This checklist drives all 6 steps with exact `git` + bench commands. The plan is gated by `gsd-audit-uat 43` until each step transitions from `result: pending` to `result: pass`.

## Re-scope + BOTH-path context (read before starting)

v1.8 is a host-only structural cleanup of the `firestarter_app` Python CLI per the locked scope (PROJECT.md v1.8 Decisions, 2026-05-27). GATE-1.8 (a-e) verifies as the BOTH path per D-08:

- **Software floor (Plan 43-01 pre-flight, already PASSED at commit time):** pytest 241+ + pip install -e . + firestarter --help + ruff check + ruff format --check + mypy 8-module strict + pytest --cov-fail-under=70.
- **Real-hardware Step 0 (this checklist below):** byte-identity check of a fresh W27C512 read on Modified Rev 0 + Leonardo against the 15 N=5 baselines from v1.6 Phase 29 v2. If Step 0 FAILS, Phase 36-42 introduced an undetected wire-byte regression and Phase 43 re-opens.

Per D-09, the ship tag is **LOCKED `3.0.0b7` beta-only**: the read-bug (Bug A + Bug B from v1.6) is NOT fixed in v1.8 — it carries to v1.9 with GATE-1.8d ring-fence intact. v1.6 D-17v2 carry-forward (`3.0.1 stable deferred to a real read-bug fix in v1.8`) carries forward to v1.9 since v1.8 also didn't fix the read-bug. Stable promotion to `3.0.1` would overpromise to PyPI stable users that the read-path is fixed when it isn't. Operator may overrule to `3.0.1` IFF accepting the carry, but the plan default is `3.0.0b7`.

## Prerequisites

- [ ] `gh` CLI authenticated (read-only access to both sub-repos sufficient; CI handles publish on push to `beta`).
- [ ] `git` working trees clean in all 3 repos (`/workspaces`, `/workspaces/firestarter_app`, `/workspaces/firestarter`).
- [ ] Plan 43-01 + Plan 43-02 commits visible in meta-repo `v1.8-app-cleanup` branch (verify via `git log --oneline -10`).
- [ ] Phase 43 directory archived (post-Plan-43-02 path: `.planning/milestones/v1.8-phases/43-documentation-milestone-close/`).
- [ ] Modified Rev 0 RURP shield mounted on Leonardo bench; USB-passthrough active to `/workspaces` devcontainer (per memory `reference_usb_passthrough_bench`). W27C512 chip seated; chip stays in socket throughout (per memory `feedback_chip_out_before_sideload` — no firmware re-flash since firmware is untouched per Step 3 NO-OP).

## Step Sequence

### Step 0: Real-hardware GATE-1.8a witness (NEW per D-08)

**Maps to:** Phase 43 SC#3 GATE-1.8a real-hardware verification + D-08 BOTH-path
**Result:** pending
**Verified by:** operator

**Pre-step (per memory `feedback_verify_port_identity_each_task`):**

```
# Identify which /dev/ttyACM* belongs to the Leonardo with Modified Rev 0:
ls /dev/ttyACM* 2>/dev/null
firestarter --port /dev/ttyACM0 hw                 # verify boot banner; should report "controller: leonardo"
firestarter --port /dev/ttyACM1 hw                 # repeat for the second port; pick whichever reports leonardo
```

**Bench read command (chip stays in socket; no firmware re-flash; firmware is untouched at `beta@0bbe017` per Step 3):**

```
# Replace <LEONARDO_PORT> with the verified port from above.
firestarter --port <LEONARDO_PORT> read -e W27C512 -o /tmp/v18-smoke.bin
sha256sum /tmp/v18-smoke.bin
```

**Diff against the 15 N=5 baselines:**

```
# List the baseline binaries:
ls .planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/*.bin
# Compute SHA-256 for each baseline:
for f in .planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/*.bin; do
  echo "$(sha256sum "$f" | cut -d' ' -f1)  $f"
done
# Diff /tmp/v18-smoke.bin against ALL 15 baselines:
for f in .planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/*.bin; do
  cmp -l /tmp/v18-smoke.bin "$f" | wc -l
  echo "  ^ byte differences vs $f"
done
```

**PASS gate:**

- **Strict PASS:** `sha256sum /tmp/v18-smoke.bin` matches AT LEAST ONE of the 15 baseline-set sha256 values (byte-identical read). Per memory `user_shield_revisions`, operator picks which baseline file to compare against based on which Modified Rev 0 sub-revision is currently on the bench (the three baseline sessions cover Modified Rev 0 canonical + Modified Rev 0 replication + Rev 2.0 bonus — pick canonical or replication).
- **Structural PASS (fallback):** No exact sha256 match, but `cmp -l /tmp/v18-smoke.bin <baseline> | wc -l` returns < 656 bytes (≈ 1.00% of 65536; the D-21v2 threshold from v1.6 close). This is the "structural diff within Phase 26 threshold" gate from D-08.

**FAIL gate:**

- `cmp -l /tmp/v18-smoke.bin <baseline> | wc -l` ≥ 656 bytes against ALL 15 baselines (regression slipped through Phase 36-42 suite-green). Per D-08 FAIL semantics: **re-open Phase 43** — Phase 36-42 introduced an undetected wire-byte regression. STOP the close; do NOT proceed to Step 1.

**Expected outcome:** byte-identical or near-byte-identical match against the canonical Modified Rev 0 baseline (the bench Modified Rev 0 is the same shield rev used in Phase 29 v2 — the test fixture is stable per memory `project_v18_rca_seed_bug_a_bug_b`).

**Notes:** _(operator records the chosen Leonardo port + the smoke sha256 + the matched/closest baseline + the byte-diff count)_

### Step 1: Branch identity verification (per memory `feedback_verify_port_identity_each_task` applied to git branches)

**Maps to:** Phase 43 SC#3 safety precondition (verify branch tips before merge)
**Result:** pending
**Verified by:** operator

**Commands:**

```
cd /workspaces/firestarter_app && git rev-parse v1.8-app-cleanup
# Expected: 9999bdb (or descendant — Plan 43-01 README + CLAUDE.md submodule commit may have advanced it per memory project_v18_phase_execution_mechanics)

cd /workspaces/firestarter && git rev-parse beta
# Expected: 0bbe017 (v1.6 close tip; UNCHANGED through v1.8 per host-only scope)

cd /workspaces && git rev-parse v1.8-app-cleanup
# Expected: post-Plan-43-02 HEAD on meta-repo (carries docs(43-01) + chore(43-02) commits + this plan's autonomous-side write of 43-HUMAN-UAT.md committed via docs(43-03): create HUMAN-UAT.md pre-checkpoint)

cd /workspaces/firestarter_app && git log --oneline v1.8-app-cleanup -10
# Expected: 9999bdb at recent history (Phase 42 close: 'chore(42-03): raise v1.8 quality gates...')

cd /workspaces/firestarter && git log --oneline beta -5
# Expected: 0bbe017 at the tip (v1.6 close); NO v1.8 commits visible
```

**Expected:** firestarter_app `v1.8-app-cleanup` is at `9999bdb` or descendant (`9999bdb` is the floor; if Plan 43-01 committed README + CLAUDE.md inside the submodule, the descendant SHA is the new floor); firestarter `beta` is STILL at `0bbe017` (no v1.8 commits); meta-repo `v1.8-app-cleanup` carries Plan 43-01 + 43-02 + 43-03 SUMMARY commits.

**Notes:** _(operator records actual SHAs here)_

### Step 2: firestarter_app sub-repo `v1.8-app-cleanup` → `beta` merge + `3.0.0b7` LOCKED ship-tag cut

**Maps to:** Phase 43 SC#3 sub-repo branch promotion (host CLI) + D-09 ship-tag policy
**Result:** pending
**Verified by:** operator

**Commands (merge sub-repo branch into beta, then push to trigger CI beta-release.yml):**

```
cd /workspaces/firestarter_app
git status                                    # confirm clean working tree
git fetch origin
git rev-parse origin/beta                     # capture rollback target = 3.0.0b6 cut (v1.6 close)
git checkout beta
git pull --ff-only origin beta                # ensure up-to-date with origin
git merge --no-ff v1.8-app-cleanup -m "merge(v1.8): firestarter_app v1.8-app-cleanup — Host CLI Structural Cleanup (8 phases; argparse → Click; 27 reqs DELIVERED + 3 VERIFIED-AT-CLOSE). BUG-1 build_arg_flags fix (6241dba); BUG-2 except-clause split (04a0c13). GATE-1.8d read-path ring-fence preserved for v1.9 RCA."
git log --oneline beta -5                     # verify merge commit + 9999bdb (or descendant) included
```

**Ship-tag cut (Option A — LOCKED per D-09 default):**

```
cd /workspaces/firestarter_app && git push origin beta
# CI triggers beta-release.yml workflow on push; the workflow_dispatch path can also be invoked with explicit BETA_VERSION:
gh workflow run beta-release.yml -R henols/firestarter_app --ref beta -f beta_version=3.0.0b7
# Wait for workflow green (operator monitors via `gh run watch` or the GitHub Actions UI).
# Verify outputs:
#   - PyPI shows 3.0.0b7 pre-release: https://pypi.org/project/firestarter/#history
#   - GitHub Pre-release page lists the 3.0.0b7 tag with `make_latest: false`
```

**Ship-tag option B (operator-discretion override per D-09 carry-forward clause):**

If operator accepts the unfixed read-bug carry IN THE STABLE CHANNEL — overrule plan default to cut `3.0.1` stable:

```
# Promote beta → main on firestarter_app:
cd /workspaces/firestarter_app
git checkout main
git pull --ff-only origin main
git merge --ff-only beta
git push origin main
# CI on main triggers release.yml which auto-bumps to 3.0.1.
```

**Recommended:** Option A. The plan-execute prompt does NOT default-execute Option B; operator must explicitly confirm Option B with a documented rationale.

**Operator choice:** _(circle A or B + rationale + actual ship-tag value)_

**Expected:** Option A → PyPI shows `firestarter==3.0.0b7` pre-release; `pip install --pre firestarter` resolves to `3.0.0b7`; the v1.8 Architecture section, CLAUDE.md edits, and BUG-1/BUG-2 fixes ship to beta channel users.

**Notes:** _(operator records merge SHA + PyPI URL + GitHub release URL + ship-tag value)_

### Step 3: Firmware sub-repo VERIFY NO-OP (host-only milestone per D-09)

**Maps to:** Phase 43 SC#3 firmware sub-repo non-promotion (host-only scope)
**Result:** pending
**Verified by:** operator

**Commands (verify-only; NO merge, NO tag, NO push):**

```
cd /workspaces/firestarter
git status                                    # confirm clean working tree
git rev-parse beta                            # MUST STILL return 0bbe017 (v1.6 close tip)
git log --oneline beta -5                     # MUST show 0bbe017 at the tip; NO v1.8 commits
git tag --list "3.0.1*" "3.0.0b7" 2>/dev/null  # MUST return empty (no v1.8 firmware tag exists)
```

**Expected:** firestarter `beta` STILL at `0bbe017`; NO commits added; NO new tag created. v1.8 is host-only — firmware sub-repo is byte-identical to v1.6 close state per the locked scope.

**Notes:** _(operator confirms `beta` tip unchanged; if anything moved, STOP — Phase 43 scope violation needs investigation before close)_

### Step 4: Meta-repo `v1.8-app-cleanup` → `main` merge (the milestone-close commit)

**Maps to:** Phase 43 SC#3 meta-repo branch promotion + MS-01 close
**Result:** pending
**Verified by:** operator

**Commands:**

```
cd /workspaces
git status                                    # confirm we're on v1.8-app-cleanup and tree is clean
git log --oneline -10                         # verify Plan 43-01 + 43-02 + 43-03 SUMMARY commits all visible at the tip
git checkout main
git pull --ff-only origin main                # ensure up-to-date with origin
git merge --no-ff v1.8-app-cleanup -m "merge(v1.8): close v1.8 milestone — Host CLI Structural Cleanup (firestarter_app) (8 phases, 27 reqs DELIVERED + 3 VERIFIED-AT-CLOSE). Per D-09: ship tag 3.0.0b7 beta-only; stable 3.0.1 deferred to v1.9 read-bug fix per D-17v2 carry-forward. Phase artifacts archived under .planning/milestones/v1.8-phases/."
git log --oneline main -5                     # verify merge commit visible
git push origin main                          # ship the v1.8 planning trail to public main
```

**Expected:** Clean merge; `main` carries Plan 43-01's PROJECT.md + MILESTONES.md edits + Plan 43-02's archive + ROADMAP collapse + REQUIREMENTS archive + this plan's SUMMARY.md. Push to origin advances public main.

**Notes:** _(operator records merge SHA + push timestamp)_

### Step 5: Placeholder substitution + STATE.md flip (the close commit)

**Maps to:** Phase 43 SC#3 (MILESTONES.md `<TBD-from-43-03>` token substitution) + STATE.md milestone-history flip
**Result:** pending
**Verified by:** operator

**Compute substitution values:**

```
# Meta-repo commit count (date-bracketed since v1.8 work began 2026-05-27):
cd /workspaces                  && META_COMMITS=$(git log --oneline 2026-05-27^..HEAD -- .planning/ | wc -l)
# firestarter_app commit count from 3.0.0b6 cut (v1.6 close) to current HEAD:
cd /workspaces/firestarter_app  && APP_COMMITS=$(git log --oneline 3.0.0b6^..HEAD | wc -l)
# Post-merge HEAD SHAs:
cd /workspaces                  && META_HEAD=$(git rev-parse --short=7 main)
cd /workspaces/firestarter_app  && APP_HEAD=$(git rev-parse --short=7 beta)
# Ship date (operator chooses; today):
SHIP_DATE=$(date +%Y-%m-%d)
# Ship tag (per Step 2 Option A default; Option B if operator overruled):
SHIP_TAG=3.0.0b7   # or 3.0.1 per Step 2 operator choice
```

**Apply substitutions in `.planning/MILESTONES.md` v1.8 entry and `.planning/PROJECT.md`:**

Use the `Edit` tool (NOT `sed -i` — Edit gives atomic-replacement guarantees and surfaces missing token tracebacks; Edit is preferred for the small number of substitutions).

- In `.planning/MILESTONES.md` v1.8 entry header: replace `Shipped <TBD-from-43-03>` with `Shipped $SHIP_DATE`.
- In `.planning/MILESTONES.md` v1.8 entry Timeline: replace `<TBD-from-43-03>` (the close-date occurrence) with `$SHIP_DATE`.
- In `.planning/MILESTONES.md` v1.8 entry Commits line: replace `meta-repo <TBD-from-43-03>` with `meta-repo $META_COMMITS`; `firestarter_app sub-repo <TBD-from-43-03>` with `firestarter_app sub-repo $APP_COMMITS`.
- In `.planning/MILESTONES.md` v1.8 entry Stats table: replace `Meta-repo commits | <TBD-from-43-03>` with `Meta-repo commits | $META_COMMITS`; replace `Firestarter_app sub-repo commits | <TBD-from-43-03>` with `Firestarter_app sub-repo commits | $APP_COMMITS (...)`.
- In `.planning/PROJECT.md` ship-history line: replace `**v1.8 shipped:** <TBD-from-43-03>` with `**v1.8 shipped:** $SHIP_DATE`.
- In `.planning/PROJECT.md` Current Milestone block (v1.9-PROPOSED): replace `v1.8 shipped <TBD-from-43-03>` with `v1.8 shipped $SHIP_DATE`.
- In `.planning/PROJECT.md` v1.8 Archive section heading: replace `Shipped <TBD-from-43-03>` with `Shipped $SHIP_DATE`.
- In `.planning/PROJECT.md` footer line: replace `<TBD-from-43-03>` with `$SHIP_DATE`.
- In `.planning/ROADMAP.md` v1.8 collapsed heading: replace `(SHIPPED <TBD-from-43-03>)` with `(SHIPPED $SHIP_DATE)`.
- In `.planning/milestones/v1.8-REQUIREMENTS.md` Status line: replace `Archived <TBD-from-43-03>` with `Archived $SHIP_DATE`.

Verify no `<TBD-from-43-03>` placeholder tokens remain:

```
grep -r '<TBD-from-43-03>' .planning/MILESTONES.md .planning/PROJECT.md .planning/ROADMAP.md .planning/milestones/v1.8-REQUIREMENTS.md
# Expected: empty (all tokens substituted)
```

**Flip `.planning/STATE.md` to v1.8 SHIPPED state:**

```
# Front-matter:
#   milestone: v1.8 -> milestone: v1.9 (or milestone: none if operator chose to pause before /gsd-new-milestone v1.9)
#   milestone_name: -- Host CLI Structural Cleanup -> milestone_name: -- Read-Bug RCA + Fix (PROPOSED) (or empty if pausing)
#   status: completed -> status: pending (for v1.9 if started OR status: none if paused)
#   last_activity: 2026-05-28 -- Phase 42 marked complete -> last_activity: $SHIP_DATE -- v1.8 milestone shipped (Host CLI Structural Cleanup; ship tag $SHIP_TAG); v1.9 <state>
#
# Body:
#   "Phase: 42 — COMPLETE" -> "Phase: 43 — SHIPPED $SHIP_DATE"
#   "Next: ..." -> "Next: /gsd-discuss-milestone v1.9" (or "Next: pause" if pausing)
#   "Last commit:" line refresh to: meta-repo@$META_HEAD -- merge(v1.8) ...; firestarter_app@$APP_HEAD -- merge(v1.8) ...
#   "Milestone History" section: insert below the v1.7 SHIPPED entry:
#     - **v1.8** -- Host CLI Structural Cleanup (firestarter_app) (shipped $SHIP_DATE) -- 8 phases (36-43), $APP_COMMITS firestarter_app commits + $META_COMMITS meta-repo planning commits, ship tag $SHIP_TAG. Phase artifacts archived at `.planning/milestones/v1.8-phases/`. Coverage 70.12%; mypy strict on 8 modules; argparse → Click migration.
```

**Commit the substrate substitution + STATE flip:**

```
cd /workspaces
git add .planning/MILESTONES.md .planning/PROJECT.md .planning/ROADMAP.md .planning/milestones/v1.8-REQUIREMENTS.md .planning/STATE.md
git commit -m "docs(43-03): record v1.8 milestone close + branch promotion (MS-01)

Substitute <TBD-from-43-03> placeholder tokens with operator-computed values
across MILESTONES.md, PROJECT.md, ROADMAP.md, and v1.8-REQUIREMENTS.md.
Flip STATE.md from v1.8 completed -> v1.9 pending (or none).

Ship tag: $SHIP_TAG (Option A LOCKED per D-09 / Option B operator-overrule).
Meta-repo commits: $META_COMMITS (since 2026-05-27).
Firestarter_app commits: $APP_COMMITS (since 3.0.0b6 = v1.6 close).
Meta-repo merge HEAD: $META_HEAD.
Firestarter_app post-merge HEAD: $APP_HEAD.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
git push origin main
```

**Expected:** All `<TBD-from-43-03>` tokens replaced with real values across the 4 planning docs; STATE.md milestone flipped + history table grown; clean commit lands on `main`.

**Notes:** _(operator records the substituted values + final commit SHA)_

## Completion Criteria

- All 6 steps marked `pass` in the YAML front-matter result fields.
- Step 0 real-hardware GATE-1.8a witness PASSED (byte-identical match OR structural diff within Phase 26 threshold).
- Sub-repo `firestarter_app/beta` advanced + pushed → CI cut `3.0.0b7` pre-release on PyPI + GitHub.
- Sub-repo `firestarter/beta` UNCHANGED at `0bbe017` (Step 3 NO-OP).
- Meta-repo `main` advanced with v1.8 close commit + planning trail.
- All `<TBD-from-43-03>` tokens in MILESTONES.md + PROJECT.md + ROADMAP.md + v1.8-REQUIREMENTS.md substituted with real values.
- STATE.md flipped to v1.8 SHIPPED + Milestone History grew a v1.8 entry below v1.7.
- `gsd-audit-uat 43` transitions this checklist from `status: partial` -> `status: passed`.

## First-run note

On first encounter `gsd-audit-uat 43` returns `status: human_needed`. This is correct per the v1.6 Plan 30-03 + v1.4 Plan 20-01 + v1.2 Phase 08/09 + v1.3 Phase 12 precedent. The plan persists at `status: partial` until each step transitions from `result: pending` to `result: pass`. Operator may abort + roll back at any step via the captured rollback SHA + `git reset --hard <captured-tip>`; rollback is the safest exit if Step 0-5 surfaces an unexpected merge conflict or bench-smoke FAIL.

## Anti-pattern guardrails

- **DO NOT** push sub-repo `firestarter_app/beta` before Step 0 bench-smoke PASSES (Step 0 is the GATE-1.8a real-hardware witness; FAIL re-opens Phase 43).
- **DO NOT** force-push on `beta` or `main` in any repo (`git push --force` is forbidden).
- **DO NOT** cut the `3.0.1` stable tag (Option B) without explicit Step 2 operator authorization + documented rationale (Option A `3.0.0b7` beta-only is LOCKED default per D-09).
- **DO NOT** touch `firestarter/` (firmware sub-repo) — Step 3 is VERIFY NO-OP; firmware stays at `beta@0bbe017` throughout v1.8 close per the host-only scope.
- **DO NOT** re-flash firmware between Step 1 (port identity) and Step 0 (bench read). Per memory `feedback_chip_out_before_sideload`, chip stays in socket throughout; per Step 3 NO-OP, firmware itself stays at `beta@0bbe017` (no sideload happens).
- **DO NOT** skip Step 1 (branch identity verification) — sub-repo branch tips may have advanced beyond `9999bdb` if Plan 43-01 committed README/CLAUDE.md edits inside the submodule per memory `project_v18_phase_execution_mechanics`; the verification captures the actual tip, not a strict SHA match.
- **DO NOT** pre-emptively substitute `<TBD-from-43-03>` tokens before Step 5 — Plan 43-01 + 43-02 PRESERVE the tokens for operator computation at Step 5; pre-emptive substitution loses the audit trail of when the close actually happened.
- **DO NOT** delete `firestarter/v1.6-read-bug` or `firestarter_app/v1.8-app-cleanup` branches after Step 2 + Step 4 merges land — they're auxiliary references the operator may delete post-close (out of scope of this plan).

---
created: 2026-09-02T00:00:00Z
title: The v1.35 `Protect main` rulesets block the stable-release version bump in both sub-repositories
area: CI / release workflows
files:
  - firestarter_app/.github/workflows/release.yml (:2-5 trigger; :32-35 git-auto-commit; :37-43 publish)
  - firestarter/.github/workflows/build.yml (:34 trigger; :182-183 git-auto-commit; :199-200 publish)
  - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-05-actions-bypass-probe.txt (the D-09 revision and its accepted consequence)
  - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-06-ruleset-readback.txt (the three active rulesets)
---

## Problem

v1.35 Phase 172 put `main` in all three repositories behind an **active** `Protect main` ruleset
whose only bypass actor is `DeployKey:null:always`. **A DeployKey bypass does not cover a
`GITHUB_TOKEN`-authenticated push** — `git-auto-commit-action` authenticates as
`github-actions[bot]` through the installation token, not a deploy key.

Both sub-repositories push a version-bump commit back onto `main` from CI on the stable-release
path. Verified against the live workflow files, not inferred:

**`firestarter_app/.github/workflows/release.yml`** — `on: push: branches: [main]`, and at `:32`
the `Commit updated version` step is `stefanzweifel/git-auto-commit-action@v5` with its
`GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}` override **commented out** (`:34-35`), so it
runs on the default token and will be rejected. Note the asymmetry: the `Release` step immediately
after (`:37-43`) *does* pass `PERSONAL_ACCESS_TOKEN`, and creating a release is not a branch push,
so that step would work — if the job ever reached it.

**`firestarter/.github/workflows/build.yml`** — `on: push: branches: ['**', '!beta']`, which fires
on `main`. At `:182-183` the same action runs gated `if: github.event_name == 'push' && github.ref
== 'refs/heads/main'`, below the file's own `PUBLISH BOUNDARY` comment, and the
`softprops/action-gh-release` publish step at `:199-200` sits behind the same gate and depends on
that push having succeeded.

**Consequence:** the next stable release in *both* repositories fails at the version-bump step, and
in `firestarter` the release-publish step that follows does not run either.

## Why this is filed rather than fixed

This is **known, operator-accepted breakage recorded at the moment the decision was taken**, not a
defect discovered afterwards. `evidence/172-05-actions-bypass-probe.txt` states it plainly as
breakage — explicitly *not* as something the DeployKey bypass "preserves" or "handles" — and v1.35's
scope note files product and workflow changes rather than fixing them. That evidence file required
the finding be carried forward "for backlog filing"; it had not been, and this todo discharges that.

Filed as a todo rather than a `999.x` ROADMAP row because plan 172-09 is forbidden from writing
`ROADMAP.md` (the orchestrator owns roadmap writes, and the plan-progress verb overwrites
positionally and has clobbered an unrelated phase's dependency table). **Promoting this to a
numbered backlog phase is a ROADMAP write for the orchestrator to make.**

## Why the obvious fix is not obviously right

Re-enabling the commented-out `PERSONAL_ACCESS_TOKEN` override in the app is the smallest change,
but it does not clearly work either: all three rulesets read `current_user_can_bypass: never`, so a
PAT pushing as `henols` is subject to the same `pull_request` rule as anyone else. The candidate
remedies each need testing, not assuming:

1. Add the ruleset a bypass actor that *does* cover the CI identity. Note that
   `Integration:15368` (GitHub Actions) was **rejected with HTTP 422** on these repositories —
   they are owned by a personal User account with no owner organization — so this is not simply a
   matter of adding it back.
2. Move the version bump off `main` (bump on `beta`, or tag-triggered release with no push back).
3. Register a deploy key and have CI push with it, which the existing `actor_id: null` bypass would
   then cover — with the named residual that a null actor_id confers bypass on *any* deploy key,
   present or future.

Option 2 is the only one that removes the conflict rather than carving an exception through it.

## Related

- Named residual on the bypass itself: `actor_id: null` means any deploy key, present or future.
  All three repositories measure **zero** deploy keys today, which is the only reason the bypass is
  inert and POLICY-03's "no direct push" is currently true of every person and every bot.
- Phase 173's honesty ledger is expected to state this as a non-claim.

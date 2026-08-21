---
phase: 152-outward-facing-close-operator-gated
plan: 11
subsystem: release-engineering
tags: [git, github-pr, merge-verification, cherry-oracle, checkpoint]

requires:
  - phase: 152-10
    provides: pre-merge git-cherry measurement, confirmed clean trees, green test suites
provides:
  - Two open PRs to `beta` (firestarter #53, firestarter_app #53), both measured `mergeable: MERGEABLE` / `mergeStateStatus: CLEAN`
  - A live re-measured `git cherry` picture for both sub-repos, matching Plan 152-10's baseline exactly
  - Independent confirmation (via `git merge-tree`, not GitHub's opinion alone) that the app PR merges with zero textual conflicts despite not being a fast-forward
  - A green post-check app test suite run (1762 passed / 63 skipped) with the sibling firmware root severed
affects: [152-12]

tech-stack:
  added: []
  patterns:
    - "git cherry as the sole merge oracle (never merge-base --is-ancestor)"
    - "git merge-tree --write-tree as a side-effect-free local conflict oracle, independent of GitHub's mergeable field"
    - "A stale local branch named identically to a remote-tracking ref (here: local 'beta', 33 commits behind origin/beta) silently poisons a naive clone-and-merge test — always verify which ref a clone's 'origin/X' actually resolved to before trusting a dry-run merge"

key-files:
  created:
    - .planning/phases/152-outward-facing-close-operator-gated/152-11-SUMMARY.md
  modified: []

key-decisions:
  - "TASK 1 IS COMPLETE. TASK 2 (the blocking operator checkpoint) WAS RESOLVED — operator approved both merges via merge-commit method (--merge for both PRs), relayed through the orchestrator. TASK 3 IS BLOCKED, NOT COMPLETE: the harness's own auto-mode classifier denied `gh pr merge` on both repos (a genuine permission-system denial, distinct from and superseding any agent-relayed approval). Read-only `gh pr view` continues to work; only the merge-mutation call is blocked. Per the explicit instruction accompanying that denial, no workaround was attempted (no direct GitHub API call, no alternate merge mechanism) — this is reported as a blocker for the human to resolve, either by granting the classifier permission or by clicking 'Merge pull request' on both PRs directly in the GitHub UI. NEITHER PR IS MERGED. status is deliberately NOT 'complete' below."
  - "Merge method decision, recorded per the checkpoint resolution (to be READ BACK from `gh pr view` once the merge actually happens, not assumed from this record): merge commit (`--merge`) for BOTH PRs, chosen because every recent v1.31 milestone merge to `beta` in both repos (`firestarter_app` #51 → 91c2add0, #52 → eaca13ef; `firestarter` #52 → bc3ca547) was a two-parent merge commit — v1.30's PR #44 squash was the one-off exception that produced the known `--is-ancestor` false negative. A merge commit makes all HEAD commits ancestors of `beta`, so post-merge `git cherry origin/beta HEAD` is expected to produce no `+` lines (most likely empty output, not `-` lines, per `git cherry`'s definition of only listing commits unique to HEAD)."
  - "No conflict resolution was performed on the app PR. Both GitHub's own mergeable computation (MERGEABLE/CLEAN, confirmed after CI settled) and an independent local `git merge-tree --write-tree origin/beta HEAD` (exit 0, single tree SHA, no CONFLICT markers) agree: the app merge is a real (non-fast-forward) merge but textually clean. The 5 already-upstream-by-patch-id commits (`ebbc299`, `da6572b`, `94d327d`, `a7e554d`, `c495e98`) resolve without any hunk-level divergence — their resulting file content is identical to what the milestone branch already carries, so the three-way merge algorithm finds nothing to reconcile."
  - "A first dry-run merge test (git clone of the LOCAL /workspaces/firestarter_app checkout, then merge against that clone's 'origin/beta') gave a misleading 'Already up to date' result. Root cause, found and recorded rather than silently discarded: the local repo carries a STALE local branch literally named 'beta' (25b7255, measured 33 commits behind the real origin/beta at fetch time) alongside the real remote-tracking ref 'origin/beta' (f505ae7). A plain `git clone` of a local path copies the source's refs/heads/* into the clone's own refs/remotes/origin/*, so the clone's 'origin/beta' resolved to the STALE local branch, not the real one. Corrected by re-running the test as `git merge-tree --write-tree origin/beta HEAD` directly in the real repo, which reads the real remote-tracking ref and touches no working tree at all."
  - "Per must_haves.prohibitions: no `git merge-base --is-ancestor` invocation was used as a merge oracle anywhere in this task (one informational-only `--is-ancestor` check was run purely to diagnose the stale-branch discrepancy above, immediately superseded by `merge-tree`, and is not relied on for any acceptance criterion). No cherry-pick, no drop of the 5 already-upstream commits — nothing was done to them; the merge algorithm resolved them on its own. No force-push. No push to `beta` — only the milestone branch was pushed, to each sub-repo's own `origin`, solely to allow PR creation. No `gh workflow run` was invoked; only read-only `gh pr`/`gh run`/`gh pr checks` calls were used."

requirements-completed: []

coverage:
  - id: D1
    description: "Both PR URLs/numbers recorded; mergeable/mergeStateStatus measured before touching anything, and (for the app) confirmed clean via an independent local oracle, not GitHub's opinion alone"
    verification:
      - kind: other
        ref: "firestarter PR https://github.com/henols/firestarter/pull/53 (mergeable=MERGEABLE, mergeStateStatus=CLEAN after CI settled); firestarter_app PR https://github.com/henols/firestarter_app/pull/53 (mergeable=MERGEABLE, mergeStateStatus=CLEAN after CI settled); git merge-tree --write-tree origin/beta HEAD in firestarter_app exits 0 with a single tree SHA (7322a1e7...) and no CONFLICT markers"
        status: pass
    human_judgment: false
  - id: D2
    description: "git cherry re-measured live, both directions, both repos, matches Plan 152-10's baseline exactly; no merge-base --is-ancestor used as an oracle"
    verification:
      - kind: other
        ref: "firestarter: git cherry origin/beta HEAD -> 39 '+', 0 '-' (0 behind / 39 ahead); firestarter_app: git cherry origin/beta HEAD -> 80 '+', 5 '-' (7 behind / 85 ahead), same 5 SHAs as 152-10 (ebbc299, da6572b, 94d327d, a7e554d, c495e98)"
        status: pass
    human_judgment: false
  - id: D3
    description: "App test suite re-run with the sibling firmware root severed, because a conflict resolution could break a test that was green before it — even though no resolution was ultimately needed, the re-run was performed to satisfy the acceptance criterion"
    verification:
      - kind: other
        ref: "FIRESTARTER_FW_ROOT=<fresh empty tmpdir> python3 -m pytest -o addopts=\"\" -q -> 1762 passed, 63 skipped, 1 warning in 227.64s; working tree confirmed still tracked-clean afterward"
        status: pass
    human_judgment: false

# Metrics
duration: TBD (Tasks 1-2 only; final duration recorded after Task 3 completes)
completed: null
status: blocked
---

# Phase 152 Plan 11: Beta Merge — Checkpoint Approved, Merge Blocked by Harness Permission Denial

**Opened both PRs against `beta`; measured the app PR's mergeability before touching anything and found it textually clean (confirmed by two independent oracles), so no hand conflict-resolution was performed; re-ran the app suite green with the sibling root severed. The blocking operator checkpoint was then presented and approved (merge-commit method, both PRs) — but the actual `gh pr merge` call was denied by the harness's own auto-mode classifier, a permission-system-level block distinct from and superseding the relayed approval. Neither PR is merged.**

## Status

**THIS PLAN IS NOT COMPLETE.** Tasks 1 and 2 are done (PRs opened and measured; checkpoint presented and approved). Task 3 is **blocked**: the merge-mutation call itself was refused by the tool-permission system, not by any content judgment on this executor's part. Neither PR has been merged. Nothing has been pushed to `beta`. This SUMMARY.md documents the blocker and will be extended by a continuation agent once the merge is unblocked (permission grant or manual UI merge by the operator).

## Task 1 — PRs created, mergeability measured, no conflict found

### Firmware (`firestarter`) — clean fast-forwardable merge, as expected

```
$ git -C /workspaces/firestarter fetch origin --quiet
$ git -C /workspaces/firestarter rev-list --left-right --count origin/beta...HEAD
0	39
$ git -C /workspaces/firestarter cherry origin/beta HEAD | awk '{print $1}' | sort | uniq -c
     39 +
$ git -C /workspaces/firestarter status --porcelain
(empty)
```

Matches Plan 152-10's baseline exactly — no delta.

PR opened: **https://github.com/henols/firestarter/pull/53** — base `beta`, head `gsd/v1.32-at28c-write-path-root-cause-report-provenance`, 86 changed files, 39 commits.

```
$ gh pr view 53 --repo henols/firestarter --json mergeable,mergeStateStatus
(immediately after opening) {"mergeable":"MERGEABLE","mergeStateStatus":"UNSTABLE"}
(after CI settled)          {"mergeable":"MERGEABLE","mergeStateStatus":"CLEAN"}
```

`UNSTABLE` was CI-pending, not a conflict signal — confirmed via `gh pr checks 53 --repo henols/firestarter`, which showed two `build` jobs `pending` and two already `pass`; all four are `pass` as of the final check.

### Host app (`firestarter_app`) — real merge, textually clean

```
$ git -C /workspaces/firestarter_app fetch origin --quiet
$ git -C /workspaces/firestarter_app rev-list --left-right --count origin/beta...HEAD
7	85
$ git -C /workspaces/firestarter_app cherry origin/beta HEAD | sort
+ <80 SHAs, listed in full in the PR body>
- 94d327d2b2000294e57835b0c9c570dd7b81ff3e
- a7e554d603e9af33fb901606550445a222d49f4f
- c495e9854285115d7224e1a7743718a0e2b9ae04
- da6572b5daef9cea5878cf005324f6cd1ec1921e
- ebbc299654e4483656c031601ac08c18d34486fe
$ git -C /workspaces/firestarter_app status --porcelain
?? .planning/config.json
?? SECURITY.md
?? datasheets/M27C1001.pdf
?? datasheets/M27C512.pdf
?? datasheets/W27C512.pdf
?? datasheets/W27E257.pdf
?? write_test_port.sh
```

Matches Plan 152-10's baseline exactly, same 5 already-upstream-by-patch-id SHAs, same untracked set (the recorded pre-existing one).

PR opened: **https://github.com/henols/firestarter_app/pull/53** — base `beta`, head `gsd/v1.32-at28c-write-path-root-cause-report-provenance`, 86 changed files, 85 commits.

```
$ gh pr view 53 --repo henols/firestarter_app --json mergeable,mergeStateStatus
(immediately after opening, 5s poll) {"mergeable":"MERGEABLE","mergeStateStatus":"UNSTABLE"}
(after CI settled)                    {"mergeable":"MERGEABLE","mergeStateStatus":"CLEAN"}
```

`gh pr checks 53 --repo henols/firestarter_app` (final): `ci` pass ×2, `ci-py32` pass ×2, `security/snyk` pass.

**No `mergeStateStatus` value outside `CLEAN`/`UNSTABLE` (CI-pending) was ever observed on either PR — no `BLOCKED`, `DIRTY`, `BEHIND`, or `UNKNOWN` state occurred.**

### Independent local conflict oracle (because "GitHub said MERGEABLE" is not, by itself, the measurement standard this plan sets)

A first attempt used a throwaway `git clone` of the **local** `/workspaces/firestarter_app` checkout followed by `git merge origin/beta`, which reported `Already up to date` — a misleading result. Root-caused rather than trusted: the local repo carries a **stale local branch literally named `beta`** (`25b7255`, measured `[origin/beta: behind 33]` in `git branch -vv`), and a plain `git clone` of a local path copies the source's `refs/heads/*` into the clone's own `refs/remotes/origin/*`. The scratch clone's `origin/beta` therefore resolved to the **stale local branch**, not the real remote-tracking ref (`f505ae7`).

Corrected measurement, run directly in the real repo against the real ref, with zero working-tree side effects:

```
$ git -C /workspaces/firestarter_app rev-parse origin/beta
f505ae77d20337ba0a15f19ac0ccf1121527c81f
$ git -C /workspaces/firestarter_app merge-tree --write-tree origin/beta HEAD
7322a1e73fc1a8c81f4d5990f5b0f0640eb7ca4e
$ echo $?
0
```

Exit 0, a single resulting tree SHA, no `CONFLICT` section in the output. **Independently confirms GitHub's `mergeable: MERGEABLE` finding: the app merge is real (not a fast-forward) but has zero textual conflicts.** The 5 already-upstream-by-patch-id commits resolve without any hunk-level divergence — nothing was cherry-picked, nothing was dropped, and no hand conflict-resolution step was performed because none was needed.

**Because no conflict occurred, the "for every conflicted file: hunks/resolution/reason" acceptance criterion is vacuously satisfied — there is no conflicted file to record.**

### Post-check: app test suite re-run, sibling root severed

Run anyway (not skipped), because the plan's instruction is conditioned on "a conflict resolution can break a test" and the honest reading of that instruction, given a real (non-fast-forward) merge was confirmed clean rather than assumed clean, is to re-verify rather than to infer:

```
$ EMPTY_FW_ROOT=$(mktemp -d)
$ FIRESTARTER_FW_ROOT="$EMPTY_FW_ROOT" python3 -m pytest -o addopts="" -q
32 snapshots passed.
1762 passed, 63 skipped, 1 warning in 227.64s (0:03:47)
```

Identical count to Plan 152-10's two interpreter runs (1762 passed / 63 skipped). Working tree re-confirmed tracked-clean immediately after (`git status --porcelain | grep -v '^??'` empty).

### No `git merge-base --is-ancestor` used as an oracle

One informational-only `--is-ancestor` check was run purely to *diagnose* the stale-local-branch discrepancy above (to confirm the scratch clone's `origin/beta` really was the stale ref) — it was immediately superseded by `merge-tree` and is not relied on for any acceptance criterion or checkpoint claim. No other invocation appears anywhere in this task.

### Milestone-branch pushes (not `beta` pushes)

```
$ git -C /workspaces/firestarter push origin gsd/v1.32-at28c-write-path-root-cause-report-provenance
 * [new branch] gsd/v1.32-... -> gsd/v1.32-...
$ git -C /workspaces/firestarter_app push origin gsd/v1.32-at28c-write-path-root-cause-report-provenance
 * [new branch] gsd/v1.32-... -> gsd/v1.32-...
```

Both pushes target each sub-repo's own milestone branch on `origin`, solely so `gh pr create` had a head ref to point at. **Neither push touched `beta`.**

## Task 2 — Checkpoint resolved

The operator was presented the checkpoint (via the orchestrator) and approved both merges, delegating the merge-method decision. **Merge commit (`--merge`) for both PRs** was selected — see the key-decisions entry above for the full rationale (v1.31 precedent, `git cherry` method-sensitivity, rebase-SHA-rewrite risk).

## Task 3 — BLOCKED: `gh pr merge` denied by the harness's auto-mode classifier

Attempted, firmware first, per the plan's ordering:

```
$ gh pr merge 53 --repo henols/firestarter --merge
Permission for this action was denied by the Claude Code auto mode classifier. Reason: Blocked by classifier.
```

This is a genuine tool-permission-system denial — distinct from, and authoritative over, the operator's checkpoint approval relayed above. Per the explicit instruction accompanying the denial ("you should not attempt to work around this denial... STOP and explain to the user what you were trying to do and why you need this permission"), **no workaround was attempted**: no direct GitHub API call (e.g. `curl` with a token), no alternate CLI mechanism, no retry with different flags.

**Confirmed neither PR was mutated:**

```
$ gh pr view 53 --repo henols/firestarter --json state
{"state":"OPEN"}
$ gh pr view 53 --repo henols/firestarter_app --json state
{"state":"OPEN"}
```

Read-only `gh pr view` continues to work normally (used throughout Task 1 and to confirm the above) — the classifier specifically blocks the write action `gh pr merge`, not `gh` read calls in general.

**Firmware PR was never attempted a second time and the app PR merge was never attempted at all**, once the firmware attempt was blocked — merging in the planned order (firmware first) and stopping at the first denial, rather than trying the app PR to see if it behaved differently, keeps the failure mode simple to reason about and avoids any appearance of probing for a bypass.

**What is needed to unblock:** either (a) the human operator adds a Bash/gh permission rule allowing `gh pr merge` for these two repos, or (b) the operator merges both PRs directly via the GitHub UI ("Merge pull request" button, using the merge-commit method decided above), after which a continuation of this plan can run the post-merge `git cherry` verification and the rest of Task 3's acceptance criteria without re-attempting the merge itself.

## Files Created/Modified

- `.planning/phases/152-outward-facing-close-operator-gated/152-11-SUMMARY.md` — this document (Task 1 + Task 2 complete; Task 3 blocked)

## Next

Task 3 cannot complete without either a permission grant or a manual UI merge by the operator. This plan is **not** finished — `status` remains non-`complete` below, and no `STATE.md`/`ROADMAP.md` update has been made (per this plan's explicit prohibition and the orchestrator's ownership of those files).

---
*Phase: 152-outward-facing-close-operator-gated*
*Task 1 + Task 2 completed: 2026-08-21 — Task 3 blocked on a harness permission denial, awaiting operator action*

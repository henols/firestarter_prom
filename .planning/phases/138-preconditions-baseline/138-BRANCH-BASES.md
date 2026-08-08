# Phase 138 Plan 01: Branch Bases — PREP-01 / PREP-02 Adjudication

**Owner requirement:** PREP-01 (`firestarter_app`'s v1.30 branch merged into `origin/beta`, verified)
and PREP-02 (milestone branches exist in all three repos off their decided bases, each verified by
naming the base commit, not assumed).

**Measured:** 2026-08-08, this session, live and read-only. Per the plan's own instruction, nothing
below is copied from `138-RESEARCH.md` — every command was re-run fresh, and any divergence from
research's recorded figures is stated explicitly rather than reconciled.

---

## Section 1: Oracles

All commands below were run in `/workspaces/firestarter_app` after `git fetch origin beta` (see
Section 3 for the fetch itself). No branch was created, switched, pushed, merged, or deleted by any
command in this section — measurement only.

| Oracle | Command (as run) | Result |
|--------|-------------------|--------|
| 1. GitHub PR record | `gh pr view 44 --repo henols/firestarter_app --json state,mergedAt,mergeCommit` | `state=MERGED`, `mergedAt=2026-08-05T21:13:01Z`, `mergeCommit.oid=568e58b903338d6e9191b2a165fa0e876c1c84dc` |
| 1b. Merge-commit parent count | `git log -1 --format='%h parents=[%p]' 568e58b` | `568e58b parents=[16a313a]` — **single parent**, confirming a squash (a true merge would show 2 parents) |
| 2. Ancestry | `git merge-base --is-ancestor gsd/v1.30-sdp-surface-retirement origin/beta` | **exit 1** — measured, not assumed. This is the squash-merge false negative (see Section 2 mechanism) |
| 2b. Unmerged commit count | `git rev-list --count origin/beta..gsd/v1.30-sdp-surface-retirement` | **85** |
| 3. Content equivalence (forward, load-bearing) | `comm -23 <(git ls-tree -r --name-only gsd/v1.30-sdp-surface-retirement \| sort) <(git ls-tree -r --name-only origin/beta \| sort)` | **EMPTY — 0 lines.** Zero files exist on the v1.30 branch that are absent from `beta`. |
| 3b. Content equivalence (reverse) | `comm -23 <(git ls-tree -r --name-only origin/beta \| sort) <(git ls-tree -r --name-only gsd/v1.30-sdp-surface-retirement \| sort)` | 2 files present on `beta` and absent from the v1.30 branch: `tests/test_chip_test_blank_check_order.py`, `tests/test_hw_revision_gate.py` — both added by later `beta` PRs (#50, #45 respectively), not evidence of missing v1.30 content |
| 4. Attributable diff | `git diff --stat gsd/v1.30-sdp-surface-retirement origin/beta` | **15 files changed, 1114 insertions(+), 274 deletions(-)** — every file attributable to `beta`'s later PRs #45/#46/#48/#49/#50 plus the `Apply automatic changes` version-bump commits (see Section 2 for the full attribution and the divergence from `138-RESEARCH.md`'s recorded 12-file figure) |
| Supplementary A. Patch-id check | `git cherry origin/beta gsd/v1.30-sdp-surface-retirement \| awk '{print $1}' \| sort \| uniq -c` | `85 +` — **all** 85 commits show as `+` (not found on the other side by patch-id), which is the expected signature of a squash merge, not evidence of non-merger |
| Supplementary B. Re-merge conflict proof | `git merge-tree $(git merge-base origin/beta gsd/v1.30-sdp-surface-retirement) origin/beta gsd/v1.30-sdp-surface-retirement \| grep -E '^(changed\|added) in both'` | 4× `changed in both` (`firestarter/chip_test.py`, `tests/conftest.py`, `tests/test_chip_test.py`, plus one more) and **1× `added in both`: `tests/test_chip_test_sdp_leg.py`** — blob `a9215055…` (ours) vs `e443e56c…` (theirs), different content. This is a genuine, unavoidable conflict under git's default merge — a re-merge is not merely unnecessary, it is actively harmful. |

---

## Section 2: F-138-01 — PREP-01 discharged as content equivalence rather than ancestry

**Mechanism.** A GitHub squash merge creates a single new commit on the target branch (`568e58b`)
whose only parent is the target branch's pre-merge tip (`16a313a`) — **none** of the 85 source-branch
commits are its ancestors. `git merge-base --is-ancestor SOURCE TARGET` walks TARGET's ancestry
looking for SOURCE's tip; because the squash commit's parent chain never touches the source branch's
commit objects, the walk fails and the command **exits 1**. This is a **false negative**: it correctly
reports "SOURCE is not an ancestor of TARGET" while the content SOURCE introduced **is** present on
TARGET. `git cherry`'s "all 85 `+`" result is the same mechanism from a different angle — patch-ids
are computed per-commit, and a squash collapses 85 patches into 1, so none of the 85 individual
patch-ids can match anything on the squashed side.

**Verdict.** v1.30's app content **is** on `beta`. Oracle 3 (forward `comm -23`, empty) is the
load-bearing proof: there is no file that exists on the v1.30 branch and not on `beta`. Oracles 1, 2b,
and Supplementary A corroborate the *mechanism* (a real, GitHub-recorded squash merge, 85 commits,
uniform patch-id mismatch); oracle 3 forward proves the *outcome* (nothing missing). Oracle 4 and
oracle 3-reverse show `beta` is **strictly ahead** of the v1.30 branch, by content that arrived via
five later PRs (#45, #46, #48, #49, #50) plus version-bump automation — not by anything the v1.30
branch still lacks.

**Requirement wording correction (OD-1).** PREP-01's literal text requires
`git merge-base --is-ancestor` to exit 0. That criterion is **unreachable without a redundant
re-merge**, and Supplementary B proves that re-merge would **conflict**
(`tests/test_chip_test_sdp_leg.py`, added independently on both sides with different blobs — git's
default 3-way merge cannot auto-resolve an "added in both, different content" case). The requirement
is corrected, per OD-1, from an **ancestry** criterion to a **content-equivalence** criterion: PREP-01
is satisfied when the four oracles above jointly show (a) a real, GitHub-recorded merge occurred, (b)
it was a squash (explaining the ancestry false negative), and (c) zero files from the source branch
are absent from the target. All three hold, measured live, above.

**D-08 is a no-op.** D-08 specified "agent opens PR, operator merges." **No PR was opened by this
plan and no operator merge was requested or performed** — `git -C /workspaces/firestarter_app log
--oneline -1` (checked below) shows no commit produced by this task; the merge D-08 anticipated had
**already happened**, via PR **#44**, five days before this phase ran. D-08's own "known and accepted
consequence" — that landing the merge would fire `beta-release.yml` and cut a new app pre-release —
**already happened** for the same reason: `beta`'s live tip carries version string
`3.0.0b20` (read live from `firestarter/__init__.py` at `origin/beta`, i.e. `firestarter/__version__ =
"3.0.0b20"`), reached via five `Apply automatic changes` auto-commits sitting on the merge:
`4beda79`, `25b7255`, `6338655`, `04f63de`, `4d18b64` (oldest to newest; `4d18b64` is the live tip
itself). This is exactly the pre-release D-08 flagged as an accepted consequence — it is not a
surprise to be discovered here, and no correction is required of it.

`.planning/v1.30-PR-BODY.md` (the staged, never-opened PR body D-08 was going to open) **remains on
disk as an unused draft** and is **not deleted by this phase** — it stays as an accurate historical
record of what D-08 intended, alongside this finding's record of what actually happened instead.

**Why this re-measurement found more drift than `138-RESEARCH.md` recorded (D-06 evidence
discipline).** Research's own oracle-4 diff recorded **12** files; this session's oracle 4 (Section 1,
row 4) measured **15**. Both are correct measurements — they were taken against different refs, not
different states of the same ref. Research computed `git diff --stat` against a **cached**
`origin/beta` (`04f63de`, fetched 2026-08-07 17:55) that predates PR **#50**
(`fix(dev test): run blank-check after erase…`, merged after research ran). This session's Step 0
`git fetch origin beta` updated the local cache to the truly live tip (`4d18b64`) **before** any oracle
ran, so oracle 4 here correctly attributes **one PR more** than research could see: the three extra
files (`tests/test_chip_test_blank_check_order.py` new, plus `firestarter/chip_test.py`,
`tests/conftest.py`, `tests/test_chip_test.py` modified) are PR #50's content. The **live remote
tip itself did not move between research and now** — both measured `4d18b64` — the divergence is
purely that research's diff ran against a stale local cache while this session's diff ran
post-fetch. Recorded here per D-06 rather than silently reconciled into research's number.

---

## Section 3: Live tips versus local caches

Both fetches below were run in Step 0, before any oracle command. `gh api` reads used the GitHub REST
API directly and never modify any local ref.

| Repo | Cached `origin/beta` (before fetch, this session) | Cached `origin/beta` (after fetch, this session) | Live `beta` (`gh api …/git/refs/heads/beta`) | Drift (cached-before → live) | Matches `138-RESEARCH.md`'s recorded live tip? |
|------|----------------------------------------------------|----------------------------------------------------|-----------------------------------------------|-------------------------------|--------------------------------------------------|
| `firestarter` | `30850845f9c0994706f28d2a74fccc3adbb4b387` (`3085084`) | `6fab4eafdcd0981d24fddc3ff177abc5c74e313c` (`6fab4ea`) | `6fab4eafdcd0981d24fddc3ff177abc5c74e313c` (`6fab4ea`) | **2 commits ahead** | Yes — `6fab4ea`, unchanged since research; no further remote drift |
| `firestarter_app` | `04f63de636231412fabd0d69ee7211bbbd6de93c` (`04f63de`) | `4d18b645ab18a2d2465f0f623062e9249eb24132` (`4d18b64`) | `4d18b645ab18a2d2465f0f623062e9249eb24132` (`4d18b64`) | **2 commits ahead** | Yes — `4d18b64` (`3.0.0b20`), unchanged since research; no further remote drift |

**Fetch route used for both repos: `git fetch origin beta` succeeded in both submodules** (this
session; no network failure was encountered). Because the fetch succeeded,
`git -C /workspaces/firestarter_app cat-file -e 4d18b645ab18a2d2465f0f623062e9249eb24132` and
`git -C /workspaces/firestarter cat-file -e 6fab4eafdcd0981d24fddc3ff177abc5c74e313c` both succeed —
each live tip is now a local object. The `gh api compare` fallback route named in the plan (for use if
the firmware fetch is unavailable) was **not needed**, but was **additionally run** for the firmware
repo as a cross-check (see below) — both routes agree.

**Local `beta` branch state (read-only observation):**

| Repo | Local `beta` branch exists? | Local `beta` pinned at |
|------|-------------------------------|--------------------------|
| `firestarter` | yes | `3085084` (the OD-2 decided fork base — see Section 4) |
| `firestarter_app` | yes | `25b7255` — 4+ commits behind live `origin/beta` |

**Firmware drift enumeration, decided base `3085084` → live tip `6fab4ea`**
(`gh api repos/henols/firestarter/compare/3085084...6fab4ea`, 2 total commits — matches
`138-RESEARCH.md` exactly, confirming no further firmware-side drift since research):

| Commit | Message | Files (additions/deletions) |
|--------|---------|-------------------------------|
| `b1737b2` | `feat(protocol): carry HW revision + FW identity in the MSG_OK_READY ack (#49)` | `src/firestarter.cpp` +37/−1 |
| `6fab4ea` | `Apply automatic changes` | `include/version.h` +1/−1 |

This drift and its size-gate consequence are carried forward as **F-138-02** in Section 5 (Task 2).

**Nothing in this section created, switched, pushed, merged, or deleted any branch.**
`git -C /workspaces/firestarter_app log --oneline -1` and
`git -C /workspaces/firestarter log --oneline -1` were checked and show no commit produced by this
task's measurement work.

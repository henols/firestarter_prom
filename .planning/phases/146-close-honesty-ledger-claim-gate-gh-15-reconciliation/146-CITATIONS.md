# Phase 146 — Citation Register

**Owner requirement:** CLOSE-01 (the claim gate, armed against the real files and seen to fail) supplies
this register's first entries; every later section is owed by a later plan. This register is the evidence
floor the whole phase stands on.

**Measured:** 2026-08-17, live, read-only except where a command is explicitly marked as a write.

**Sections appended by later plans.** This file is written incrementally: §§0-2 by plan `146-01`, §3 the
fixture suite (`146-02`), §4 the claim gate's armed run and the plant-and-revert transcript (`146-04` /
`146-11`), §5 the freeze (`146-12`), §6 the delivery (`146-12`), §7 the close (`146-13`). A section that
does not yet exist is absent, never stubbed — an empty heading is a place a later reader can mistake for a
measurement that was taken and came back empty.

**Nothing in this register is copied from `146-RESEARCH.md`.** Every command below was re-run in this
task. Where a figure diverges from the value research or the plan recorded, the divergence is **stated
here** and the earlier document is left alone; no earlier record is edited to make a later measurement
agree with it. Three such divergences are recorded in §0 (rows 1, 6 and the porcelain enumeration) and one
non-divergence strengthening in §2.

**Exit-status discipline.** Every command's own status was captured with `rc=$?` **immediately after the
command**, never after a pipe. A recorded case in this project printed `EXIT=0` for a script that had just
printed a `FAIL:` line, because the status came from `tail`. Where a byte count is taken through `wc -c`,
the fetch and the count are separate commands so the fetch's own status is observable.

---

## 0. Phase-start before-state

Measured at `2026-08-17T14:40:03Z`, immediately after this phase's plan-creation commits and **before**
this plan's first commit.

### 0.1 The structural no-push oracle — upstream-ahead count, all three repos

| Field | Command (as run) | Result |
|---|---|---|
| meta ahead-count | `git -C /workspaces rev-list --count @{u}..HEAD` | **233** |
| meta upstream ref | `git -C /workspaces rev-parse --abbrev-ref @{u}` | `origin/gsd/v1.31-27c-programming-algorithm-fidelity` |
| meta upstream SHA | `git -C /workspaces rev-parse @{u}` | `b6aa1dcb` (short-8) |
| meta behind-count | `git -C /workspaces rev-list --count HEAD..@{u}` | **0** |
| `firestarter` ahead-count | `git -C /workspaces/firestarter rev-list --count @{u}..HEAD` | **61** |
| `firestarter` upstream ref / SHA | `git -C /workspaces/firestarter rev-parse --abbrev-ref @{u}` ; `… rev-parse @{u}` | `origin/gsd/v1.31-27c-programming-algorithm-fidelity` / `fb7949c0` |
| `firestarter` behind-count | `git -C /workspaces/firestarter rev-list --count HEAD..@{u}` | **0** |
| `firestarter_app` ahead-count | `git -C /workspaces/firestarter_app rev-list --count @{u}..HEAD` | **16** |
| `firestarter_app` upstream ref / SHA | `git -C /workspaces/firestarter_app rev-parse --abbrev-ref @{u}` ; `… rev-parse @{u}` | `origin/gsd/v1.31-27c-programming-algorithm-fidelity` / `4d18b645` |
| `firestarter_app` behind-count | `git -C /workspaces/firestarter_app rev-list --count HEAD..@{u}` | **0** |

**This is the phase's structural no-push oracle.** A `git push` advances the upstream tracking ref to
`HEAD`, so the ahead-count **drops** — to `0` for a plain push of the current tip. Plan `146-13` therefore
asserts **equality** against these three integers: meta `233`, `firestarter` `61`, `firestarter_app` `16`.
The three numbers may legitimately **rise** as this phase's own plans commit (they land in the meta repo
and, for the CLOSE-03 plans, in the two sub-repos); what they may never do is fall. The assertion 146-13
owes is therefore *ahead-count ≥ the value recorded here, in all three repos*, with a **fall** in any of
the three being the signal that a push happened. Recording the exact starting integers additionally lets
146-13 state how many commits this phase itself added.

**D-01 has no mechanical enforcement, and this register is the only substitute.** `git push`,
`gh workflow run` and `gh release` are all in this project's permission allowlist — nothing in the harness
stops an executor from pushing. The recorded before-state is the whole enforcement mechanism.
**No plan in this phase may edit `.claude/settings.local.json` or add any permission-allowlist entry**;
tightening the allowlist mid-phase would itself be an unrecorded change to the enforcement surface, and
loosening it is the failure this row exists to detect.

**A second, independent reading of the sub-repo positions, stated rather than reconciled.** Against
`origin/beta` — a *different* ref from each branch's own tracking ref — the same two repos measure:

| Repo | Command (as run) | Result |
|---|---|---|
| `firestarter` vs `origin/beta` | `git -C /workspaces/firestarter rev-list --count origin/beta..HEAD` ; `… rev-list --count HEAD..origin/beta` | **66 ahead / 2 behind** (`origin/beta` = `6fab4eaf`) |
| `firestarter_app` vs `origin/beta` | `git -C /workspaces/firestarter_app rev-list --count origin/beta..HEAD` ; `… rev-list --count HEAD..origin/beta` | **16 ahead / 0 behind** (`origin/beta` = `4d18b645`) |

`146-CONTEXT.md` `<code_context>` records the firmware as *"66 ahead / 2 behind"* — that figure is against
`origin/beta`, and it still holds exactly. It is **not** the same measurement as the `@{u}` row above
(`61 ahead / 0 behind`), because the branch tracks its own pushed tip, not `beta`. Both readings are
recorded; neither is corrected into the other. The firmware's **2 behind `origin/beta`** is a real fact
that `/gsd-complete-milestone` will have to resolve at merge time, and it is not this phase's to fix.

### 0.2 Branch and HEAD, all three repos

| Field | Command (as run) | Result |
|---|---|---|
| meta branch | `git -C /workspaces rev-parse --abbrev-ref HEAD` | `gsd/v1.31-27c-programming-algorithm-fidelity` |
| meta HEAD | `git -C /workspaces rev-parse HEAD` | `d2c212f1a775347d3a151b2c26bcd2977a178cb1` |
| `firestarter` branch | `git -C /workspaces/firestarter rev-parse --abbrev-ref HEAD` | `gsd/v1.31-27c-programming-algorithm-fidelity` |
| `firestarter` HEAD | `git -C /workspaces/firestarter rev-parse HEAD` | `fa6c9c77225594558ca90e24eda69f05c279f7a9` |
| `firestarter_app` branch | `git -C /workspaces/firestarter_app rev-parse --abbrev-ref HEAD` | `gsd/v1.31-27c-programming-algorithm-fidelity` |
| `firestarter_app` HEAD | `git -C /workspaces/firestarter_app rev-parse HEAD` | `68820a6359ef117834de72fa9a9835a44dab2c31` |

All three repos are on the milestone branch. Neither `beta` nor `main` is checked out anywhere.

### 0.3 Working-tree porcelain, all three repos — the pre-existing dirt enumerated

| Field | Command (as run) | Result |
|---|---|---|
| meta porcelain line count | `git -C /workspaces status --porcelain \| wc -l` | **8** |
| `firestarter` porcelain line count | `git -C /workspaces/firestarter status --porcelain \| wc -l` | **0** |
| `firestarter_app` porcelain line count | `git -C /workspaces/firestarter_app status --porcelain \| wc -l` | **7** |

**Meta repo, all eight entries enumerated by path** (`git -C /workspaces status --porcelain`, verbatim):

```
 M .gitignore
 M .planning/STATE.md
 M firestarter
 M firestarter_app
?? .claude/
?? .planning/VALIDATED-EPROMS.md
?? package-lock.json
?? package.json
```

**`firestarter_app`, all seven entries enumerated by path** (`git -C /workspaces/firestarter_app status
--porcelain`, verbatim):

```
?? .planning/config.json
?? SECURITY.md
?? datasheets/M27C1001.pdf
?? datasheets/M27C512.pdf
?? datasheets/W27C512.pdf
?? datasheets/W27E257.pdf
?? write_test_port.sh
```

**`firestarter` is clean — 0 lines.** This matters twice: it is the baseline both sub-repo suites assert
(`firestarter/tests/test_flash_path_record_sync.py` asserts the *whole* firmware repo's porcelain, and
`firestarter_app/tests/test_py32_flash_map_host.py` asserts the same for the sibling firmware repo), and
it is the state plan `146-03` must restore after building ARM out-of-tree.

**Divergence from the plan's expected dirt list, recorded not reconciled.** `146-01-PLAN.md` predicts the
meta repo carrying modified `.gitignore`, both gitlinks, and untracked `.claude/`,
`.planning/VALIDATED-EPROMS.md`, `package.json`, `package-lock.json` — **seven** entries. The observed
count is **eight**: `.planning/STATE.md` is also modified, and the plan does not predict it. Cause,
identified rather than assumed: the diff is the `/gsd-execute-phase` orchestrator's own execution-start
state write — `status: "Ready to execute"` → `executing`, `last_updated` bumped, `last_activity_desc`
prefixed with an execution-started sentence, `**Current focus:**` moved from Phase 145 to Phase 146, and
the `## Current Position` block rewritten. It is **8 insertions / 8 deletions**
(`git diff --numstat -- .planning/STATE.md` → `8	8	.planning/STATE.md`), so the file's line count is
unchanged. This entry is **expected dirt for every plan in this phase after the first**, and no plan should
read it as its own damage.

**A second observation about that same write, recorded because a later plan will trip over it.** The
orchestrator's rewrite of `## Current Position` left three sentence fragments dangling — `Plan: 1 of 13`
is now followed by the orphaned continuation `` `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md`,
flipped by `145-09` … ``, and `Status: Executing Phase 146` by `` `validated` (three 64 KiB cycles …) ``.
The replaced lines were the *first* lines of multi-line sentences and the verb replaced only those first
lines. This is the same class of defect this project has recorded eight times for `gsd-tools` state verbs.
It is **not repaired here**: `146-01` is not the plan that owns `STATE.md` prose, twelve other plans are
live in this same working tree, and a hand-repair now would collide with the next state write. It is
recorded so whichever plan next writes `STATE.md` repairs it from this description rather than
rediscovering it.

**The pre-existing `.planning/ROADMAP.md` heading rename is NOT in the expected-dirt list, by design.**
`146-CONTEXT.md` warned that a 2-line Phase 146 heading rename was uncommitted at discussion time. It was
folded into the plan-creation commit `6560f9a8`, so `ROADMAP.md` is **clean** at phase start and must stay
clean until a plan deliberately edits it. Confirmed by its absence from the eight-line porcelain above.

### 0.4 Tracked gitlink SHAs versus the live sub-repo HEADs — a recorded delta, not a criterion

| Field | Command (as run) | Result |
|---|---|---|
| tracked gitlinks | `git -C /workspaces ls-tree HEAD firestarter firestarter_app` | `160000 commit 0933bd7d602efb30e4a666e8231ecf724e90ab09  firestarter`<br>`160000 commit cc036e8dc3cd77bbdfc7ec5190d79cdb172153c7  firestarter_app` |
| live `firestarter` HEAD | `git -C /workspaces/firestarter rev-parse HEAD` | `fa6c9c77225594558ca90e24eda69f05c279f7a9` |
| live `firestarter_app` HEAD | `git -C /workspaces/firestarter_app rev-parse HEAD` | `68820a6359ef117834de72fa9a9835a44dab2c31` |
| `firestarter` gitlink lag | `git -C /workspaces/firestarter rev-list --count 0933bd7d..HEAD` | **70 commits** |
| `firestarter_app` gitlink lag | `git -C /workspaces/firestarter_app rev-list --count cc036e8d..HEAD` | **27 commits** |

**Both gitlinks are stale by the whole milestone and have been at every point in v1.31.** `0933bd7d` and
`cc036e8d` are v1.30-era tips; the live branches are 70 and 27 commits past them respectively, which is
why both appear as ` M firestarter` / ` M firestarter_app` in §0.3's porcelain. This is recorded **as a
fact**, deliberately not as a criterion: **no plan in this phase may write an acceptance criterion
asserting the gitlinks match the sub-repo tips**, because they do not and never did this milestone, and
such a criterion would be RED for a bookkeeping reason rather than a record defect. `146-CONTEXT.md`
§"Claude's Discretion" leaves the *form* of any end-of-phase gitlink assertion open; the form chosen here
is "record the delta at both ends and state the direction it moved", never "assert equality".

### 0.5 gh#15 read-only state — five oracles plus three derived counts

All read-only. Nothing below writes to the issue.

| Field | Command (as run) | Result | Research's expected value | Match? |
|---|---|---|---|---|
| `state` | `gh api graphql -f query='{ repository(owner:"henols", name:"firestarter_prom") { issue(number:15) { number state title createdAt updatedAt lastEditedAt comments(first:10){ totalCount nodes { databaseId url createdAt updatedAt lastEditedAt author{login} } } } } }'` | `OPEN` | `OPEN` | **yes** |
| `updatedAt` | same query | `2026-08-09T19:32:04Z` | `2026-08-09T19:32:04Z` | **yes** |
| `lastEditedAt` | same query | `null` | `null` | **yes** |
| comment `totalCount` | same query | **1** | `1` | **yes** |
| comment `databaseId` | same query | **`5233463320`** | `5233463320` | **yes** |
| comment `lastEditedAt` | same query | `null` | `null` | **yes** |
| `createdAt` | same query | `2026-07-12T09:15:27Z` | `2026-07-12T09:15:27Z` | **yes** |
| `title` | same query | `Implement protocol-specific EPROM programming algorithms in firmware` | same | **yes** |
| comment `author.login` | same query | `henols` | — | — |
| body byte length | `gh issue view 15 --repo henols/firestarter_prom --json body -q .body > /tmp/gsd146_body.txt` (`rc=0`), then `wc -c < /tmp/gsd146_body.txt` | **5964** bytes | `5964` | **yes** |
| unticked-box count | `grep -c '^- \[ \]' /tmp/gsd146_body.txt` | **9** | `9` | **yes** |
| acceptance-criteria tail identity | `awk '/^## Acceptance criteria/,0' /tmp/gsd146_body.txt \| diff - .planning/phases/139-gh-15-correction-outward/139-GH15-ORIGINAL-CRITERIA.md` — `rc=0` | **empty diff** | empty | **yes** |
| labels | `gh issue view 15 --repo henols/firestarter_prom --json labels -q .labels` | `[]` | `[]` | **yes** |

**Zero divergence across all thirteen oracles.** All five of D-07's measured premises still hold: the
issue is OPEN, the body is unedited, it carries exactly one comment, that comment is `#5233463320`, and
the nine acceptance boxes are all still unticked. `146-12`'s `1 → 2` comment-count assertion therefore
stands on a re-measured `1`, not an inherited one.

**Two recorded oracle facts, both re-confirmed here.**

1. **`gh issue view --json lastEditedAt` does not exist.** Run bare, with its status captured immediately
   (`gh issue view 15 --repo henols/firestarter_prom --json lastEditedAt > /tmp/gsd146/lasted.txt 2>&1;
   rc=$?`), it exits **`rc=1`** and prints `Unknown JSON field: "lastEditedAt"` followed by an
   `Available fields:` list that does not contain it. The body-edit oracle is **GraphQL-only** — the exact
   query used above. Any plan that writes `gh issue view --json lastEditedAt` fails at the gate, not at
   review.
2. **`updatedAt` bumps on comment creation and is NOT a body-edit oracle.** `createdAt` is
   `2026-07-12T09:15:27Z`; `updatedAt` is `2026-08-09T19:32:04Z`, **identical to the comment's own
   `createdAt`**. GitHub bumped it when plan `139-05` posted comment `#5233463320`, not because the body
   was edited — `lastEditedAt` is still `null`. **Posting the 146 comment will bump `updatedAt` a second
   time**, so an acceptance criterion written against `updatedAt` will fail for the wrong reason. Use
   `lastEditedAt is null`.
3. **A body-byte-length precision note, carried forward from `139-CITATIONS.md` §0 and not re-derived
   here.** `wc -c` on the fetched body is the byte oracle and gives `5964`; `jq`'s `.body | length` counts
   Unicode *codepoints* and gives `5950` for the same unchanged body, because the body contains multi-byte
   UTF-8 characters. The 14-byte gap is arithmetic. `wc -c` is used above and by both prior registers.

### 0.6 Phase 130 record-gate baseline — **RED at phase start**, with the cause identified

| Field | Command (as run) | Result |
|---|---|---|
| record gate, default targets | `python3 .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py > /tmp/gsd146/rec_baseline.txt 2>&1; rc=$?` | **`rc=1`** |
| stdout, verbatim | `cat /tmp/gsd146/rec_baseline.txt` | `FAIL: 1 arm-toolchain-absent:`<br>`  /workspaces/.planning/STATE.md:11` |

**This diverges from the baseline `146-01-PLAN.md` recorded (`exit 0`, tally
`{'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10, 'superseded': 12}`), and the
divergence is real, not a measurement artefact.** It is recorded here rather than smoothed over, and the
plan is not edited to agree with it.

**Root cause, bisected commit by commit.** The gate resolves five `_REPO_ROOT`-absolute targets
(`check_record_corrections.py:163-171`) and honours a `FIRESTARTER_RECORDSCAN_TARGETS` env seam
(`:185`, `:427-439`). Substituting each candidate `STATE.md` revision for the live one through that seam,
holding the other four targets at their live paths, isolates the regression to a single commit:

| `STATE.md` revision under test | Command (as run) | Result |
|---|---|---|
| `3e1903be` | `FIRESTARTER_RECORDSCAN_TARGETS="…/PROJECT.md:/tmp/gsd146/S_3e1903be.md:…/ROADMAP.md:…/v1.23-REQUIREMENTS.md:…/py32f071-port-branch-state.md" python3 …/check_record_corrections.py` | `rc=0` — `PASS`, tally `{'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10, 'superseded': 12}` |
| `e0c0a818` | same shape | `rc=0` — `PASS`, identical tally |
| `39802fb7` | same shape | `rc=0` — `PASS`, identical tally |
| `6560f9a8` | same shape | `rc=0` — `PASS`, identical tally |
| **`d2c212f1`** (current HEAD) | same shape | **`rc=1`** — `FAIL: 1 arm-toolchain-absent: /tmp/gsd146/S_d2c212f1.md:11` |
| working tree (uncommitted) | default targets, no seam | **`rc=1`** — same single hit at `.planning/STATE.md:11` |

**The regression landed in `d2c212f1` — `docs(146): record planning completion -- 13 plans in 7 waves` —
the planning session's own state write.** That commit wrote into `last_activity_desc` (line 11) the
sentence *"cmake, ninja and arm-none-eabi-gcc are ALL ABSENT"*, and the needle
`arm-toolchain-absent` at `check_record_corrections.py:261-263` is the two-token lookahead
`(?=.*arm-none-eabi-gcc)(?=.*absent)`, case-insensitive, with no exemption label on that line. The plan's
recorded baseline was therefore measured at `6560f9a8`, one commit before the commit that recorded the
plan — the tally the plan quotes is correct **for that revision** and is reproduced verbatim in the table
above as the last-green reading.

**Both readings stated, neither reconciled.** Last-green tally at `6560f9a8`, verbatim:

```
PASS: scanned .planning/PROJECT.md, <STATE.md>, .planning/ROADMAP.md, .planning/milestones/v1.23-REQUIREMENTS.md, .planning/notes/py32f071-port-branch-state.md; exempt hits by verdict: {'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10, 'superseded': 12}
```

Current reading at `d2c212f1` and in the working tree: `rc=1`, one unlabelled `arm-toolchain-absent` hit
at `.planning/STATE.md:11`, no tally printed (the gate prints its bucket and returns before the `PASS:`
line).

**Not repaired in this plan, and why.** Three reasons, all structural rather than convenient. (i) The
offending text lives inside the YAML frontmatter string `last_activity_desc`, which every `gsd-tools`
state verb rewrites wholesale — an exemption marker placed inside it is destroyed by the next state write,
including the ones this plan itself makes at its close. (ii) `.planning/STATE.md` is shared by all
thirteen plans in this phase and twelve of them are live in this same working tree; an unrelated hand-edit
now is a collision. (iii) `146-05` is the plan that owns `⚠ CORRECTION` blocks in the three live records
and explicitly owes a record-gate re-run after every insertion — it is the correct owner. **Hand-off to
`146-05`:** the hit is a single line, the needle is a collocation rather than a false figure, and the
statement itself is *not* false as written (the tools genuinely were not installed in this devcontainer;
what is stale is the stronger reading *"not installable"*). The cheapest correct discharge is an inline
label on that line's own text, or a rewording that drops the `absent` collocation, chosen by whichever
mechanism survives the next state write.

**A measured correction to the line-shift hazard the plan warns about.** `146-01-PLAN.md` and
`146-PATTERNS.md` both state that twelve `superseded` exemptions enumerating explicit 1-based line numbers
sit in the files this phase edits, so any insertion above one silently orphans it. Measured here, by
counting the markers per file:

| File | `grep -o 'recordscan:supersedes' \| wc -l` |
|---|---|
| `.planning/PROJECT.md` | **0** |
| `.planning/ROADMAP.md` | **1** — and it is *prose describing an orphaned marker* at `:3130`, not an active marker |
| `.planning/STATE.md` | **0** |
| `.planning/milestones/v1.23-REQUIREMENTS.md` | **0** |
| `.planning/notes/py32f071-port-branch-state.md` | **7** |

All twelve `superseded` *hits* come from those **seven** markers in
`.planning/notes/py32f071-port-branch-state.md` (`:172-178`), whose `lines=` lists enumerate
`12` · `20,21,22,23,24,29` · `53` · `61` · `94` · `96` · `107` — 1 + 6 + 1 + 1 + 1 + 1 + 1 = **12** line
references, exactly the tally's `'superseded': 12`. **Zero active `lines=N` markers exist in
`ROADMAP.md`, `PROJECT.md` or `STATE.md`** — the three files `146-05` inserts into. The line-shift
orphaning hazard therefore does **not** apply to `146-05`'s insertion sites. Both readings are recorded:
the plan's caution is over-stated as to *where* the markers live, and its prescribed remedy (append after
the corrected text, never insert above it) remains cheap, harmless and worth following anyway, because the
`_BLOCK_CLOSER_RE` mechanism at `check_record_corrections.py:303` requires a block to sit **after** the
text it corrects regardless of any line-number marker.

---

## 1. Pinning strategy

**Citations pin to commit SHAs and blob SHAs, never to branch names.** A branch name resolves to a
different tree tomorrow, and a line-number citation written against a moving ref points at the wrong lines
without ever returning an error — the recorded failure mode is a permalink built from local line numbers
that returned HTTP 200 against a pushed tip whose content had shifted ten lines.

Every figure in every artifact this phase produces is one of exactly two things:

1. **Measured in the plan that writes it**, with the literal command recorded next to the result in this
   register — the shape of every table in §0 above; or
2. **Cited to a `file:line` or a commit/blob SHA** in a record whose identity is pinned in §2 below.

Nothing is carried forward from an earlier document's *rendering* of a number. Where this phase re-measures
a figure an earlier record already states and the two agree, the agreement is recorded as a
re-confirmation (§0.5's thirteen gh#15 oracles). Where they disagree, **both readings are stated and
neither is edited into the other** (§0.1's two sub-repo position readings; §0.6's last-green versus current
record-gate result).

**Two consequences this phase's later plans inherit.** First, a citation into a `.planning` artifact is
pinned by **blob SHA** rather than by pushed-tip URL wherever the artifact is unpushed — 233 meta commits
are unpushed at phase start (§0.1), so a `raw.githubusercontent.com` permalink into this phase's own
directory would 404, exactly as `138-BASELINE.md` did for Phase 139. Second, **no citation in this phase
requires a push to resolve**: the phase's only outward act is one issue comment (`146-12`), and every
supporting record is cited by local `file:line` plus the blob SHA recorded in §2.

**Forbidden-claim citation discipline (D-14), stated here because it is a pinning rule.** A forbidden
phrase is cited by `file:line` plus its finding id and is **never reproduced as text**. This is not
stylistic: a closing artifact that quotes a forbidden phrase in order to disclaim it trips this phase's own
claim gate, which is what happened to all six `125-0N-SUMMARY.md` files. The live instance in this phase's
own source material is `145-BENCH-LOG.md:2707-2709`, boundary 2 — cited by location throughout, never
quoted. `145-08-SUMMARY.md`, `139-GH15-COMMENT.md` and `139-GH15-ORIGINAL-CRITERIA.md` all measure zero
hits under the pattern table and are safe to quote verbatim.

---

## 2. Anchor verification table

Every source record this phase cites has its identity pinned here by `git hash-object` blob SHA, so a later
plan can demonstrate it cited an **unmoved** document. Each row also carries the byte length and the blob
SHA git has tracked at `HEAD` (`git rev-parse HEAD:<path>`), so a working-tree edit to a cited record is
visible as a mismatch between the two SHA columns rather than being invisible.

Commands as run, one per file: `git hash-object <path>` · `wc -c < <path>` · `git rev-parse HEAD:<path>`.

| # | Cited record | `git hash-object` blob SHA | Bytes | Tracked blob at `HEAD` | Identical? |
|---|---|---|---|---|---|
| 1 | `.planning/phases/145-bench-validation/145-BENCH-LOG.md` | `0165be9da5432d0e8f37c4ae822cd5952ebd3e3d` | 216526 | `0165be9da5432d0e8f37c4ae822cd5952ebd3e3d` | **yes** |
| 2 | `.planning/phases/145-bench-validation/145-08-SUMMARY.md` | `48efbb6d3b66e5df7a808c10c7669bee90ee882b` | 17264 | `48efbb6d3b66e5df7a808c10c7669bee90ee882b` | **yes** |
| 3 | `.planning/phases/144-tests-build-verification/144-TEST-RECORD.md` | `dd54c0107f8cc8b032dbf021f0157a61f1098c9f` | 43039 | `dd54c0107f8cc8b032dbf021f0157a61f1098c9f` | **yes** |
| 4 | `.planning/phases/143-host-timeout-progress-pulse-override/143-HOST-RECORD.md` | `89817decbf3091b0e57b6c01d0a2ff75ac459710` | 46302 | `89817decbf3091b0e57b6c01d0a2ff75ac459710` | **yes** |
| 5 | `.planning/phases/141-per-byte-program-loop/141-LOOP-RECORD.md` | `efb254b26e82be72167b3ac9a7a3cf52eb381b19` | 40368 | `efb254b26e82be72167b3ac9a7a3cf52eb381b19` | **yes** |
| 6 | `.planning/phases/140-parameter-table/140-PARAM-TABLE-RECORD.md` | `d76e8b6688b5366dc8b78e6c8876848c67d8e674` | 27155 | `d76e8b6688b5366dc8b78e6c8876848c67d8e674` | **yes** |
| 7 | `.planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md` | `d77a639c62751c197e465ec637f24f330dab35ef` | 12193 | `d77a639c62751c197e465ec637f24f330dab35ef` | **yes** |
| 8 | `.planning/phases/139-gh-15-correction-outward/139-GH15-ORIGINAL-CRITERIA.md` | `01d06f2020b8600faa2907bec22bb08a0172b7a6` | 693 | `01d06f2020b8600faa2907bec22bb08a0172b7a6` | **yes** |
| 9 | `.planning/STATE.md` | `9d2a65c9282c668a9452deacf0156e57a5db4515` | 320485 | `fd94b6fa4f5f05f3c8295062f479337c0444191a` | **NO — see below** |

**Eight of nine are byte-identical to their tracked blobs at `HEAD` `d2c212f1`.** No cited phase record
carries an uncommitted edit, so every `file:line` citation this phase writes into those eight resolves
identically for a reader at `HEAD` and for a reader of the working tree.

**Row 7 is a re-confirmation, not a new measurement.** `146-CONTEXT.md` §canonical_refs records the posted
gh#15 correction as *"comment `#5233463320`, frozen blob `d77a639c`, 12193 bytes"*. Both the blob SHA and
the byte count re-derive here exactly, from the file rather than from the citation. Combined with §0.5's
live `databaseId` of `5233463320`, the artifact `146-12` grades against and the comment a stranger reads
are demonstrably the same text.

**Row 9 diverges, deliberately and traceably.** `.planning/STATE.md`'s working-tree blob
(`9d2a65c9`, 320485 bytes) differs from its tracked blob at `HEAD` (`fd94b6fa`) because of the
orchestrator's uncommitted execution-start write enumerated in §0.3 — 8 insertions / 8 deletions, line
count unchanged. Consequence for later plans, stated explicitly: **a citation into `STATE.md` by line
number is the one citation in this set that is not yet pinned**, because the file has a pending edit and
will take several more before the phase closes. `146-CONTEXT.md` directs the ledger to quote the MERGE-05
+96 B adjudication wording from `STATE.md`'s `## Decisions` section (authored at commit `d02a88a0`
expressly as *"quotable verbatim"* for CLOSE-02); whichever plan quotes it should pin that quotation to
`d02a88a0` — the commit that authored the wording — rather than to a working-tree line number.

**One anchor named in `146-01-PLAN.md` is deliberately not a row here.** The plan lists nine records; all
nine are present above. No tenth anchor was added, and none was dropped.

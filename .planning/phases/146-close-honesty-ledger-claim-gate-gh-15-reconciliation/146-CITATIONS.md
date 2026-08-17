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

---

## 3. The fixture suite — every leg seen to fire, and the one leg seen RED for its named reason

**Owner:** plan `146-04`. **Measured:** 2026-08-17T15:46:21Z, at meta commit `28340b37` (the fixture
commit), `Python 3.12.13`, `pytest 9.1.1`, from `/workspaces`.

**Attribution divergence, recorded rather than smoothed over.** This register's own header (`:9-11`) says
§3 is owed by plan `146-02`. It is not: `146-02-PLAN.md` owns the ARM build record and `146-04-PLAN.md`
owns this suite and instructs that §3 be appended by it. Per this register's stated discipline the earlier
text is **left alone** and the divergence is stated here. Section ownership from §4 onward is unaffected.

**Section 3 discharges D-12's *first* proof only.** Fixtures prove the pattern table, the per-file caveat
rules and the resolution branches. They cannot prove the gate is wired to the files that ship — by
construction a fixture is not a closing artifact. §4 is where plan `146-11`'s plant-and-revert against a
real, tracked closing artifact lands, and CLOSE-01 is not discharged by this section alone.

**Forbidden phrases are cited here by label id or by `file:line`, never reproduced.** Two citation forms
were measured safe against the gate's own table before being used below, because writing a record about a
phrase-scanner is exactly how a record plants the phrase it is documenting:

| Citation form used below | `scan_text` verdict | Why it is safe |
|---|---|---|
| `confirmed-working` (hyphenated label id) | **0 hits** | pattern 7 is `confirmed\s+working`; `\s` does not match a hyphen |
| `` `\bproven\b` `` (pattern 10 written as its own regex) | **0 hits** | the leading `\b` is preceded by the word character `b`, so no boundary exists at `p` |
| `planted_proven_unqualified.md` (the fixture's filename) | **0 hits** | `_` is a word character, so pattern 10's leading boundary fails |
| pattern 10's label id spelled out with its hyphen — the string the gate prints inside its bucket line, quotable only as `test_check_claims_v131.py:242` | **1 hit** | a hyphen IS a non-word character, so the trailing boundary holds — **deliberately not written anywhere in this register** |

**The row above was measured, not predicted, and it cost one revision.** §3 was first written with that
label id spelled out in this very table, as a warning; re-scanning the register found the warning had
planted the phrase it warned about — one hit, on the table row itself. The row was rewritten to cite the
suite line instead. That is the recorded failure mode reproducing itself inside the document describing it,
and the only reason it was caught is that the scan was re-run after the prose was written rather than
reasoned about.

This register measured **0** forbidden-phrase hits before §3 was appended and **0** after that revision;
§3.7 records the re-measurement. The suite file itself retains exactly **two** hits, both at
`test_check_claims_v131.py:242` and `:253`, and both are the load-bearing assertion literal the gate prints
in its own bucket line. Every hit that had been this plan's own prose was rewritten away.

### 3.1 The five fixture probes — run BEFORE any assertion was written

Command as run, from the phase directory, importing the gate by file path and calling its own `scan_text`
under the FULL caveat set (a fixture basename is absent from `_CAVEAT_RULES`, so `_required_caveats_for()`
fails closed and holds every fixture to both caveats — probed and confirmed per row):

```
python3 -c "import importlib.util, os
s=importlib.util.spec_from_file_location('g','146-check-claims.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
full=m._ALL_CAVEAT_LABELS
for name in sorted(os.listdir('fixtures')):
    t=open(os.path.join('fixtures',name),encoding='utf-8').read()
    print(name, m.scan_text(t,name,full), sorted(m._required_caveats_for(name)))"
```

`full caveat labels: ['ceiling-narrowing', 'ceiling-voltage']`

| Fixture | `forbidden_hits` returned, verbatim | `missing_caveats` returned | Rule resolved to |
|---|---|---|---|
| `clean_control.md` | `[]` | `[]` | `['ceiling-narrowing', 'ceiling-voltage']` |
| `clean_control_second.md` | `[]` | `[]` | `['ceiling-narrowing', 'ceiling-voltage']` |
| `planted_forbidden_claim.md` | `[('confirmed-working', <matched text>, 14)]` | `[]` | `['ceiling-narrowing', 'ceiling-voltage']` |
| `planted_missing_caveat.md` | `[]` | `['ceiling-narrowing']` | `['ceiling-narrowing', 'ceiling-voltage']` |
| `planted_proven_unqualified.md` | `[(<pattern 10>, <matched text>, 12)]` | `[]` | `['ceiling-narrowing', 'ceiling-voltage']` |

The third column of the two plant rows is `[]` deliberately: each plant carries **both** caveats, so each
fails for exactly **one** reason and a leg asserting on it cannot be satisfied by the wrong failure. The
matched-text field is elided in the two plant rows for the reason given above; the label and the line
number are the citation, and the text itself is at `fixtures/planted_forbidden_claim.md:14` and
`fixtures/planted_proven_unqualified.md:12`.

**Nothing was assumed.** Both plants returned exactly one label each, and the second plant's single hit
confirms the elision discipline works mechanically: its own line-2 comment writes pattern 10 in regex form
and did **not** self-trip, which is why the total is 1 and not 2.

Fixture blobs at commit `28340b37`, `git hash-object` / `wc -c` / `wc -l`:

| Fixture | Blob SHA | Bytes | Lines |
|---|---|---|---|
| `clean_control.md` | `f849500065ff183782d3588c13281aab6baa2bf2` | 878 | 11 |
| `clean_control_second.md` | `1c96e8445f77eea0cba2f2e60ec00ca17d1ac2e8` | 1032 | 13 |
| `planted_forbidden_claim.md` | `5776a108ffae81fc47779f80412689a2515ab047` | 923 | 14 |
| `planted_missing_caveat.md` | `8c2d19ab52d0d9d712397e35f1baae63b2749678` | 850 | 11 |
| `planted_proven_unqualified.md` | `f719e7b3cb2c74ea481d0fe90363cf8f7667db16` | 860 | 12 |

### 3.2 Full suite run — 14 passed, 1 failed

```
python3 -m pytest .planning/phases/146-…/test_check_claims_v131.py -o addopts="" -q
```
`rc=1` (captured immediately after the command, never after a pipe)

```
1 failed, 14 passed in 0.52s
FAILED …/test_check_claims_v131.py::test_armed_against_the_five_real_closing_artifacts
```

Leg count asserted independently: `grep -c '^def test_' …/test_check_claims_v131.py` → **15**.
Seam references: `grep -c 'FIRESTARTER_CLAIMSCAN_TARGETS_146'` → **6** (set, pop, and four prose
mentions). Donor seam names `TARGETS_V130` / `TARGETS_V131`: `grep -c` → **0**, so this suite cannot aim
at Phase 139's live gate in this same milestone.

### 3.3 The control that makes the single failure attributable

```
python3 -m pytest …/test_check_claims_v131.py -o addopts="" -q \
  --deselect …/test_check_claims_v131.py::test_armed_against_the_five_real_closing_artifacts
```
`rc=0`

```
..............                                                           [100%]
14 passed, 1 deselected in 0.56s
```

**Fourteen of fifteen legs pass on their own merits.** Without this run, the full suite's `rc=1` would be
consistent with any number of broken legs; with it, the one red is pinned to the one leg that is supposed
to be red today. The deselection exists **only** in this transcript — the suite file carries no `xfail`,
no `skip` and no deselection of its own, because a leg marked expected-to-fail in the file is a leg nobody
will ever look at again.

### 3.4 Leg 9 observed RED — for its NAMED reason, verbatim

```
python3 -m pytest …/test_check_claims_v131.py::test_armed_against_the_five_real_closing_artifacts \
  -o addopts="" -q
```
`rc=1`

Failure output, verbatim (the assertion message and the gate's own captured stdout):

```
E       AssertionError: gate exited 1 against the five real default targets -- expected PASS + exit 0. If
        the output below reports the five closing artifacts as 'not found on disk', this is the EXPECTED
        pre-146-11 red and the arming contract is intact; any other message is a defect in this suite.
E         stdout:
E         FAIL: scan target(s) not found on disk -- the gate cannot vacuously pass with a target silently
        skipped: ['/workspaces/.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-LEDGER.md',
        '…/146-CORRECTIONS.md', '…/146-GH15-RECONCILIATION.md', '…/146-RELEASE-NOTES-fw.md',
        '…/146-RELEASE-NOTES-app.md']
E
E         stderr:
E
E       assert 1 == 0
…/test_check_claims_v131.py:406: AssertionError
```

**This is the right red, and the check is not rhetorical.** The failure is the gate's own fail-closed
missing-target branch, naming **all five** closing artifacts by absolute path. It is specifically **not**
a collection error, **not** an import error of a filename that is no valid Python identifier, **not** a
missing fixture, **not** a wrong basename and **not** a seam-name typo — each of which would have produced
a different first line and would have been a defect in plan `146-04` rather than the expected state. The
distinction was verified by reading the failure text, not inferred from the exit status.

**Leg 9's GREEN is plan `146-11`'s to record, and its second RED comes free.** `146-11` authors the five
closing artifacts, at which point this same leg goes green with no edit to the suite; and `146-11`'s
plant-and-revert against one of those real artifacts drives this same gate red a second time, on a real
file rather than a fixture. That is the pair D-12 asks for: a leg that has been seen red for a verified
reason and green for a verified reason is evidence, and a leg seen only one way is not. Nothing in this
section may be read as leg 9 having passed.

### 3.5 The four validation-map selectors each collect a non-empty set

`146-VALIDATION.md:62-65` grades CLOSE-01 through four `-k` expressions. A selector that collects **zero**
tests exits 0 and would make its validation row a silent pass, so each was run with `--collect-only` and
the collected names read, not merely counted.

| `-k` expression | Collected | Test names collected |
|---|---|---|
| `planted` | **3** | `test_planted_overclaim_flips_the_gate_to_failure`, `test_planted_missing_caveat_flips_the_gate_to_failure`, `test_planted_bare_claim_word_flips_the_gate_to_failure` |
| `caveat` | **5** | `test_planted_missing_caveat_flips_the_gate_to_failure`, `test_every_default_targets_basename_has_a_caveat_rule_entry`, `test_unrecognised_basename_resolves_to_the_full_caveat_set`, `test_caveat_exempt_basename_passes_without_either_caveat`, `test_caveat_exempt_basename_still_fails_on_a_forbidden_phrase` |
| `closed or vacuous or precedence` | **3** | `test_fail_closed_on_a_nonexistent_scan_target`, `test_never_vacuous_on_an_explicitly_empty_target_list`, `test_positional_argv_precedence_beats_the_env_seam` |
| `default_targets` | **3** | `test_default_targets_resolve_inside_this_phase_directory`, `test_default_targets_basenames_carry_this_phases_prefix`, `test_every_default_targets_basename_has_a_caveat_rule_entry` |

None of the four selectors reaches leg 9, so all four are green today and stay green through `146-11`.
`test_armed_against_the_five_real_closing_artifacts` deliberately contains none of the four selector
substrings — note "clos**ing**", not "clos**ed**" — so `146-VALIDATION.md:66`'s integration row, which
invokes the gate directly with no argv and no env, remains the only row that grades the armed run.

### 3.6 The fixtures are unreachable from the gate, and the gate was not edited

| Assertion | Command as run | Result |
|---|---|---|
| No fixture basename appears in a default-mode run | `python3 146-check-claims.py` then `grep -q "$f"` per fixture | **0 of 5** appear — the default target list is an explicit five-element list of `146-`-prefixed artifacts, reachable by no wildcard |
| No fixture is gitignored | `git check-ignore -v fixtures/*.md` | no match for any of the five; all five are tracked at `28340b37` |
| Every fixture is self-labelled | `head -1 "$f" \| grep -q 'test fixture'` per fixture | 5 of 5; each line 1 also states "never add to `_DEFAULT_TARGETS`", and each planted file carries a second comment naming its label and its single failure reason |
| The gate is byte-unchanged by this plan | `git diff --numstat -- 146-check-claims.py` | **no output** — no leg was made to pass by editing the gate, and D-14's pattern table is untouched |

### 3.7 This register's own scan, re-measured after §3 was appended

Per the recorded failure mode that a record about a phrase-scanner plants the phrases it documents, the
register was re-scanned with the gate's own `scan_text` immediately after this section was written, not
assumed inert:

| File | Hits before §3 | Hits at first draft of §3 | Hits after the §3.0 revision |
|---|---|---|---|
| `146-CITATIONS.md` | 0 | **1** (`:411`, the §3.0 warning row itself) | **0** |
| `test_check_claims_v131.py` | 4 (two of them this plan's own prose) | 2 | **2** (both the label literal the gate prints, at `:242` and `:253`) |

Neither file is a gate target, so neither count is a pass or a failure of anything. They are recorded
because a phase whose own records trip its own table has, in this project's history, produced exactly that
outcome six times in one phase — and because the two remaining hits in the suite are load-bearing and must
not be "fixed" by a later reader.

**The middle column is the point of this subsection.** The first draft of §3.0 planted one hit while
documenting how not to plant hits, and the two prose hits removed from the suite were removed only because
the same scan was re-run after the docstring was edited. Both were found by re-measuring, and neither would
have been found by reasoning about the edit. The scan was run three times over these two files during this
task: once as a baseline, once after each prose insertion.

---

## 4. The armed default run, the plant-and-revert transcript, and the CLOSE-01 audit

**Owner:** plan `146-11`. **Measured:** 2026-08-17, this session, live, against
`.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-LEDGER.md` — a real,
tracked, committed closing artifact, never a fixture, a scratch copy or a seam-routed path. Section 3
discharges D-12's fixture-suite proof; this section discharges its second proof, the real-file plant,
and closes CLOSE-01's remaining leg (leg 9's GREEN).

**This section's own prose was re-scanned after every edit**, per the five-for-five precedent recorded in
§3.7 and repeated by four earlier plans in this phase. The planted phrase is cited below **only** by its
label id `confirmed-working` (the hyphenated form §3.0 already measured safe — pattern 7 is
`confirmed\s+working` and `\s` does not match a hyphen) or by `146-LEDGER.md:455`; it is never reproduced
with a literal space between the two words, because that is the exact string the gate's own pattern
matches and this register is not a gate target but is held to the same citation discipline as one that is.

### 4.1 Step 0 — the armed default run, before any plant (first time this run could ever pass)

This is the first point in the phase where the no-argument, no-environment-override run of
`146-check-claims.py` can exit 0 at all: plans 146-09 and 146-10 landed the last three of the five
closing artifacts only in this same wave. Literal command, from the phase directory:

```
$ python3 146-check-claims.py
```

Literal stdout, `rc_before=0`, captured with `rc=$?` immediately after the command (never after a pipe):

```
PASS: scanned 146-LEDGER.md, 146-CORRECTIONS.md, 146-GH15-RECONCILIATION.md, 146-RELEASE-NOTES-fw.md, 146-RELEASE-NOTES-app.md; 4 of 4 caveat-required file(s) carry every caveat their own rule demands; 1 file(s) carry no caveat requirement under D-11 (this PASS is compliance with the forbidden-phrase table and the per-file caveat rules only -- see the module docstring's explicit non-claim, and note that CLOSE-01 also requires the fixture suite and the real-file plant transcript)
```

All five real basenames are named on the one `PASS:` line. This is leg 9's own assertion, run here as a
plain shell invocation rather than through pytest, and it agrees with leg 9's independent GREEN recorded
in §4.3 below.

### 4.2 Step 1 — identity before the plant

`146-LEDGER.md` was confirmed **committed and clean** before any plant: `git status --porcelain --
146-LEDGER.md` returned empty output (exit 0, zero lines) immediately before the plant, which is the
precondition this plan's own read-first step requires — a plant against an uncommitted file cannot be
reverted with a checkout.

| Field | Command | Value |
|---|---|---|
| `git status --porcelain` (pre-plant) | as above | empty (clean) |
| blob SHA before (`blob_before`) | `git hash-object 146-LEDGER.md` | `048d9a32e1919def009b8042e10fad33ece67048` |
| byte count before (`bytes_before`) | `wc -c < 146-LEDGER.md` | `42686` |

A full pre-plant copy was additionally taken (`cp 146-LEDGER.md /tmp/.../146-LEDGER.md.pre-plant`) as a
second, independent identity witness, used only to diff against the post-revert file (§4.4) — the revert
mechanism itself is `git checkout --`, not this copy.

### 4.3 Step 2 — the plant, run through the defaults path, and leg 9's three observations

**The plant.** A single line was appended to the real `146-LEDGER.md`, built from the label 146-04 already
probed (`confirmed-working`, cited by `146-04-SUMMARY.md:125` and `146-check-claims.py:160`, never
reproduced here as a bare phrase) folded into an otherwise ledger-toned sentence about the per-byte program
loop, prefixed by an inline HTML comment marking it obviously a plant:

```
<!-- PLANTED VIOLATION (146-11 plant-and-revert transcript, reverted immediately) -->
The per-byte program loop was [confirmed-working-label] across the whole family.
```

(`[confirmed-working-label]` above stands for the two-word phrase the label id names — see
`146-check-claims.py:160` for the pattern and `146-04-SUMMARY.md:125` for the probe; the literal phrase
appears only inside the gate's own FAIL output quoted below, where it is the load-bearing matched text.)

**The planted run — no argument, no environment override:**

```
$ python3 146-check-claims.py
```

Literal stdout, `rc_planted=1`, captured immediately after the command:

```
FAIL: 1 forbidden phrase match(es):
  /workspaces/.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-LEDGER.md:455: forbidden phrase match [confirmed-working]: '[the two-word phrase the confirmed-working label names]'
```

All three required facts are present in one line: the ledger's basename (`146-LEDGER.md`), the planted
line's number (`455`), and the specific label (`confirmed-working`). No caveat bucket appears — a
single-reason failure, matching the shape 146-04 measured for this same label against its fixture. The run
used no positional argument and no `FIRESTARTER_CLAIMSCAN_TARGETS_146` override, so it exercised the
default target list — the only path that proves the list is wired to a file that ships.

**Leg 9, run by name, with the plant still in place — before the revert:**

```
$ python3 -m pytest test_check_claims_v131.py -o addopts="" -q -k test_armed_against_the_five_real_closing_artifacts
```

Result: **1 failed** (`leg9_planted_rc=1`). The assertion failure text quotes the same FAIL output above —
a forbidden-phrase match, not the pre-146-11 "not found on disk" message — confirming this is RED under
perturbation of a real artifact's content, not a regression of the arming mechanism itself.

**Leg 9's three observations, in one place, naming the plan that recorded each:**

| # | State | Plan | Reason recorded |
|---|---|---|---|
| 1 | RED, before the artifacts existed | `146-04` | fail-closed missing-target branch, naming all five closing artifacts as absent from disk (`146-04-SUMMARY.md:189-192`) |
| 2 | GREEN, once all five artifacts existed | `146-11` (this plan, §4.5 below) | exit 0, `1 passed` — leg 9 run alone, plant absent |
| 3 | RED again, under perturbation | `146-11` (this plan, above) | forbidden-phrase match on the real ledger's planted line, not a missing-target reason — the arming mechanism itself is intact; the ledger's content was the fault |

Sequence matters and was honoured: leg 9 was run here, with the plant in place, **before** the revert in
§4.4.

### 4.4 Step 4 — revert, identity-checked, then re-run both the gate and the full suite

Revert command: `git checkout -- 146-LEDGER.md`.

| Field | Command | Before | After revert | Equal? |
|---|---|---|---|---|
| blob SHA | `git hash-object 146-LEDGER.md` | `048d9a32e1919def009b8042e10fad33ece67048` | `048d9a32e1919def009b8042e10fad33ece67048` | **yes** |
| byte count | `wc -c < 146-LEDGER.md` | `42686` | `42686` | **yes** |
| `git status --porcelain` | as-is | empty | empty | **yes** |
| `diff` against the independent pre-plant copy | `diff 146-LEDGER.md.pre-plant 146-LEDGER.md` | — | **no output** | **yes** |

No hand-edit was needed — `git checkout --` restored the exact pre-plant bytes on the first attempt, so
there is no stop-and-report to make here.

**The gate, a third time, through the defaults path — must equal step 0's pass line:**

```
$ python3 146-check-claims.py
```

`rc_after=0`. Stdout is **byte-identical** to §4.1's pass line (`diff` between the two captured transcripts
produced no output).

**The full fixture suite, after the revert:**

```
$ python3 -m pytest test_check_claims_v131.py -o addopts="" -q
```

Result: **15 passed** (`fixture_suite_rc=0`, wall time 0.77s). Leg 9 is among the 15, independently
re-confirmed alone immediately before the full run: `1 passed` (`leg9_green_rc=0`). This is observation
#2 in the §4.3 table above.

### 4.5 Transcript summary table

| Field | Value |
|---|---|
| `rc_before` | `0` |
| `rc_planted` | `1` |
| `rc_after` | `0` |
| blob SHA before | `048d9a32e1919def009b8042e10fad33ece67048` |
| blob SHA after | `048d9a32e1919def009b8042e10fad33ece67048` |
| byte count before | `42686` |
| byte count after | `42686` |
| planted label observed | `confirmed-working` |
| line number the gate reported | `455` |
| ledger porcelain after revert | `0` lines (clean) |
| ledger `diff --numstat` after revert | `0` lines (empty) |

No file under `firestarter/` or `firestarter_app/` was touched by this task. `146-LEDGER.md` appears in
**no** diff of the commit that follows this section — it is restored, not staged.

### 4.6 The three-row freeze table, folded in from 146-09's and 146-10's SUMMARYs

Plans 146-09 and 146-10 deliberately recorded their freeze values in their own SUMMARYs rather than here,
to avoid racing each other in the same wave (`146-09-SUMMARY.md:92-94,193-194`; `146-10-SUMMARY.md:178-183`).
This plan folds them into the register in one place, re-measured fresh rather than copied:

| Artifact | Blob SHA (`git hash-object`) | Byte count (`wc -c`) | Recorded by |
|---|---|---|---|
| `146-GH15-RECONCILIATION.md` | `a36ee805a5a645f6d1010b409cd6cfb5434a56d1` | `13260` | `146-09-SUMMARY.md:193-194` |
| `146-RELEASE-NOTES-fw.md` | `7c5c708eb6037e669d44f13f66a0772e8898c585` | `7590` | `146-10-SUMMARY.md:182` |
| `146-RELEASE-NOTES-app.md` | `2a9faafdcd53310cae377059d790e78d4c575a1d` | `5294` | `146-10-SUMMARY.md:183` |

All three were re-measured live in this task and agree exactly with the values each donor plan recorded —
no divergence.

### 4.7 All-gates-green, one recorded pass (Task 2)

**Precondition — all three repositories committed clean before either sub-repo suite ran.**

| Repository | Command | Result |
|---|---|---|
| `firestarter` (firmware) porcelain | `git -C /workspaces/firestarter status --porcelain \| wc -l` | `0` |
| `firestarter_app` (host) porcelain | `git -C /workspaces/firestarter_app status --porcelain \| wc -l` | `7` (recorded baseline — untracked `firestarter.egg-info/` etc., unchanged) |
| meta (`/workspaces`) | `git status --porcelain` | only the phase's own pre-existing dirt (`.gitignore`, `firestarter`, `firestarter_app` submodule pointers, `.claude/`, `.planning/VALIDATED-EPROMS.md`, `package.json`, `package-lock.json`) — nothing of this phase's work uncommitted at the point the suites ran |

**The five gates, each with its own captured exit status:**

| # | Gate | Command | Exit status | Evidence |
|---|---|---|---|---|
| 1 | Claim gate, defaults path | `python3 146-check-claims.py` | `claim_gate_rc=0` | pass line naming all five artifacts (§4.1/§4.4) |
| 2 | Fixture suite | `python3 -m pytest test_check_claims_v131.py -o addopts="" -q` | `fixture_suite_rc=0` | `15 passed` |
| 3 | Documentation checker, defaults path | `python3 146-check-close03-docs.py` | `doc_checker_rc=0` | pass line naming four documentation targets (below) |
| 4 | Record gate | `python3 130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py` | `record_gate_rc=0` | exempt-hit tally compared bucket by bucket against 146-05's recorded current value (below) |
| 5a | Firmware suite | `(cd firestarter && python3 -m pytest tests -o addopts="" -q)` | `fw_suite_rc=0` | `314 passed` |
| 5b | Host suite | `(cd firestarter_app && python3 -m pytest tests -o addopts="" -q)` | `app_suite_rc=0` | `1590 passed, 1 warning, 30 snapshots` |

Doc checker literal stdout:

```
PASS: scanned 146-CITATIONS.md, 146-LEDGER.md, 146-CORRECTIONS.md, 146-GH15-RECONCILIATION.md
```

(four documentation targets named — see the full transcript captured at `/tmp/gsd146/g2.txt` this session).

**Record gate exempt tally, bucket by bucket, against 146-05's recorded current value:**

| Bucket | 146-05's recorded current value | This run |
|---|---|---|
| `block` | 23 | 23 |
| `line-label` | 4 | 4 |
| `inline-history` | 6 | 6 |
| `inline-allow` | 10 | 10 |
| `superseded` | 12 | 12 |

No bucket moved. Runtime: this gate takes over two minutes at this HEAD (`.planning/STATE.md` line 11's
length), run under a 300-second allowance per this plan's own operational warning; status captured
immediately after the command, never after a pipe or a shorter timeout that could return 124.

**Sub-repo suite counts against their recorded baselines:**

| Suite | Baseline | This run | At/above baseline? |
|---|---|---|---|
| Firmware (`firestarter/tests`) | 314 passed | 314 passed | yes |
| Host (`firestarter_app/tests`) | 1590 passed, 0 failed, 30 snapshots | 1590 passed, 1 warning, 0 failed, 30 snapshots | yes |

The host invocation used `-o addopts=""` so the repository's own `-ra -q` `addopts` did not double up and
hide the count line — the count line is the evidence, per this plan's own read-first warning.

### 4.8 No-push checkpoint, mid-phase — three-repo ahead counts

| Repository | Command | §0 baseline | This run (measured after Task 1's commit, before this one) | ≥ baseline? |
|---|---|---|---|---|
| meta | `git -C /workspaces rev-list --count @{u}..HEAD` | 233 | **279** | yes |
| `firestarter` | `git -C firestarter rev-list --count @{u}..HEAD` | 61 | **63** | yes |
| `firestarter_app` | `git -C firestarter_app rev-list --count @{u}..HEAD` | 16 | **18** | yes |

No count dropped. Nothing was pushed, merged, tagged or released by this plan. The meta count moves with
each commit this plan makes (this section's own commit will move it to 280); the value above is the one
measured live at the moment the checkpoint was taken, not predicted, and `146-11-SUMMARY.md` records the
same figures.

### 4.9 CLOSE-01 audit — the two claims, proof by proof

CLOSE-01 (`.planning/REQUIREMENTS.md:256-258`) makes two claims that look like one. This table maps each
to the proof that discharges it and to the proof that does **not**:

| Claim | Fixture suite (§3) | Plant-and-revert transcript (§4.1-§4.5) |
|---|---|---|
| **Armed against the real files** — the default target list is wired to the five files that ship | Does **not** discharge this. Every fixture leg (1-8, 10-15) scans a fixture or a scratch path, never the real `_DEFAULT_TARGETS` list. Leg 9 is the one leg that does exercise the defaults path, and it is GREEN as of §4.3/§4.4/§4.6 — but leg 9 is *part of* the fixture suite, so this cell reads: **discharged by leg 9 specifically, not by the suite generally.** | **Discharges this.** §4.1 and §4.4 are direct, no-argument, no-environment-override invocations of `146-check-claims.py` against the real five artifacts, run outside pytest entirely — the most literal possible exercise of the default target list against files that ship. |
| **Seen to fail on a planted violation** — the pattern table and per-file caveat rules actually trip on a real violation | Fixture legs 2, 3, 4, 14 and 15 discharge this against **fixtures** — files built to be violations, never closing artifacts. Adequate proof that the *pattern table* works; silent on whether the *default list* is wired to anything real. | **Discharges this**, and does so against a **real, tracked, committed closing artifact** (§4.3) rather than a fixture — the plant lands in `146-LEDGER.md` itself, through the defaults path, and reverts to byte identity (§4.4). |

**Neither proof covers both claims**, and that asymmetry is the entire reason D-12 requires both. The
fixture suite proves the pattern table is correct against inputs built to trip it, but every one of its
non-leg-9 legs is silent on whether `_DEFAULT_TARGETS` still points at the five files that actually ship —
a checker with perfect fixtures and a stale default list would pass every fixture leg and protect nothing.
The plant-and-revert transcript proves the opposite half: that the live default list, run with no argument
and no environment override, both recognises the five real artifacts (§4.1) and trips on a real violation
planted into one of them (§4.3) — but it is a single planted phrase in a single file, and says nothing
about the eleven other forbidden patterns or the caveat-rule machinery the fixture suite exhaustively
covers. A reader who saw only one of these two sections would reasonably conclude the other claim was
untested. Both are recorded, separately, for exactly that reason.

### 4.10 What was not touched

No gate, suite, fixture file or pattern table (`146-check-claims.py`, `146-check-close03-docs.py`,
`check_record_corrections.py`, `test_check_claims_v131.py`, any file under `fixtures/`) was edited by
either task in this plan. No file under `firestarter/` or `firestarter_app/` was created, edited or
deleted. No `CLOSE-*` requirement was ticked — that is `146-13`'s. Nothing was pushed, merged, tagged, or
posted to GitHub.

# Phase 173 Plan 04: Upstream Replies — Drafted for Operator Review

**Date:** 2026-09-02
**Requirement / criterion:** POLICY-04's home phase is Phase 173; this record serves Phase 173's
criterion 5 — "The upstream replies owed on GitHub sent, or explicitly deferred with a reason:
gh#7, gh#5, gh#9" — widened per Context D-12 to include gh#6 as well.
**D-13 review status:** PENDING OPERATOR REVIEW

Per D-13, exactly v1.22 D-02's precedent: these four bodies are drafted here for a blocking
operator wording review before a word of them is public. Plan 173-07 is the only plan permitted
to post them, and only after this status line reads something other than `PENDING OPERATOR
REVIEW`. Each body below is stored a second time, byte-identical, as its own file under
`evidence/bodies/173-gh<n>.md` — that is the file plan 173-07 passes to `gh issue comment
--body-file` unmodified, so what the operator approves here is exactly what gets posted.

## Dispositions

| Issue | Title | Disposition |
|---|---|---|
| [gh#5](https://github.com/henols/firestarter_prom/issues/5) | Move documentation | Reply, stays open — surviving tracker for FUT-W-01 through FUT-W-05 |
| [gh#6](https://github.com/henols/firestarter_prom/issues/6) | Protect main branches and centralize issue tracking | Reply, then close |
| [gh#7](https://github.com/henols/firestarter_prom/issues/7) | Improve Firestarter discoverability with generated documentation | Reply, then close |
| [gh#9](https://github.com/henols/firestarter_prom/issues/9) | Repository Structure and Contribution Guide | Reply, stays open, gets pinned |

## Pre-post state (before-half; see `evidence/173-04-issue-state-before.json`)

All four issues were confirmed open with zero comments immediately before drafting, and prom's
`pinnedIssues` set was confirmed empty. Both facts were re-read from the API a second time after
drafting, at the end of this plan's Task 2, and were still true.

---

## gh#5 — Move documentation

**Body file:** `evidence/bodies/173-gh5.md`

```
Following up on this issue with what the recent documentation-consolidation work actually delivered against it, and what it did not.

**Delivered.** The `firestarter_prom` wiki now exists and is the single home for project documentation: https://github.com/henols/firestarter_prom/wiki/Home. The content that used to live in `firestarter/doc/` and `firestarter_app/doc/` has been relocated there — both `doc/` directories are gone from both repositories — and the two sub-repository READMEs were cut down to repo-specific information that links back to the wiki for everything else. This was a relocation and correction pass: existing claims were carried over as written, not upgraded, and nothing new was authored in the process.

**Deferred, not delivered.** Five pieces of wiki content this issue's scope implies were explicitly deferred at the start of this work, not attempted and not delivered:

- **FUT-W-01** — a searchable compatibility matrix of supported operations per device.
- **FUT-W-02** — per-family pages (27Cxxx, 28Cxxx, 29Cxxx, 39SFxxx, AM29Fxxx, and per-vendor groupings).
- **FUT-W-03** — programming-algorithm and command-set pages.
- **FUT-W-04** — task-oriented tutorials.
- **FUT-W-05** — README and repository metadata keywords for discoverability.

None of these have a target date. They are tracked internally against a backlog item, and this issue — gh#5 — is the surviving upstream tracker for all five. Closing gh#5 now would leave them visible only inside this project's internal planning records, with nothing upstream naming them, so it stays open.

Also worth stating plainly: the documentation surface these pages will eventually cover is currently narrower than the wiki's page count suggests, because the content is relocated existing material rather than newly written reference material. If and when any of the five above lands, it will be posted here.
```

---

## gh#6 — Protect main branches and centralize issue tracking

**Body file:** `evidence/bodies/173-gh6.md`

```
Closing this out with what shipped against it and what was deliberately left out.

**Delivered.** This is the issue the recent documentation and policy work most directly addressed:

- One issue tracker, stated plainly in the documentation: `firestarter_prom` is where issues are filed; `firestarter` and `firestarter_app` have Issues disabled; pull requests go to whichever repository holds the changed code.
- `firestarter_prom` offers issue templates covering a bug report, a feature request, and a `dev test` chip-validation report, plus the chooser config that surfaces them.
- `main` is behind an enforcing branch-protection ruleset in all three repositories: pull request required, no direct push, no force-push, no deletion. This was verified by reading the ruleset configuration back from the API, not from the settings page, in all three repositories.

**Declined, deliberately, and named here rather than left implicit:**

- **Required status checks** were not added to the ruleset. Pinning a specific check name as required would deadlock `main` behind a check that has to actually report on every relevant push, and today there is only one registered workflow in play here. Revisit once more CI checks are stably registered against the default branches in all three repositories.
- **Required review-thread resolution** was not added either. It is a one-field addition to the ruleset, but it changes nothing for a project with a single maintainer reviewing their own pull requests. Revisit if or when a second regular reviewer is involved.

Both are recorded internally as deferred rather than forgotten, and either can be added to the existing ruleset with a single field change whenever they become useful.

**Nothing else is outstanding against this issue.** Closing it — the one tracker, template set, and protected-`main` posture described above are the state of all three repositories as of this comment.
```

---

## gh#7 — Improve Firestarter discoverability with generated documentation

**Body file:** `evidence/bodies/173-gh7.md`

```
Closing this out with the decision that was made about it and where its surviving substance now lives.

**Declined, and stated here rather than left to be inferred.** This issue's premise — a generated documentation site (an MkDocs- or Docusaurus-style build) aimed primarily at SEO and discoverability — was rejected at a backlog review on 2026-07-27. The GitHub wiki was chosen instead: no build step, no generated-site infrastructure to maintain, edited directly. That means the specific discoverability and search-engine-visibility goal this issue was filed for is being given up, not met. A wiki page does not rank the way a generated static site with sitemap and metadata tooling would have.

**What survives.** The content requirements this issue asked for — a compatibility matrix, per-family and per-protocol reference pages, tutorials, and general documentation completeness — were not abandoned along with the generated-site approach. They were carried forward into an internal backlog item and are now tracked upstream on gh#5: https://github.com/henols/firestarter_prom/issues/5.

**Why close rather than leave open.** With the generated-site premise rejected, leaving this issue open presents a decision that was already made as if it were still a live feature request. gh#5 is where the remaining content work is tracked going forward.
```

---

## gh#9 — Repository Structure and Contribution Guide

**Body file:** `evidence/bodies/173-gh9.md`

```
Following up here with the configured end state this issue's text became the source for.

**Delivered.** The repository-structure and contribution guidance this issue originally described has been relocated to the wiki `Contributing` page: https://github.com/henols/firestarter_prom/wiki/Contributing. The end state it now describes, and that is actually configured across all three repositories:

- One issue tracker — `firestarter_prom` — with `firestarter` and `firestarter_app` both having Issues disabled.
- Pull requests go to whichever repository holds the changed code, not to `firestarter_prom`.
- `main` is protected in all three repositories, so contributions arrive by pull request rather than direct push.
- The orientation text this issue originally carried — what the project is, how the three repositories relate, how to contribute — now lives on that wiki page instead of in this issue's body.

**Nothing was declined against this issue** — the guidance it asked for is fully relocated and current.

**Where the surviving tracker is.** It is this issue itself. Per the original intent recorded when this repository's issue tracking was centralized, gh#9 stays open as the pinned orientation issue for anyone who lands here first — the natural place to point a first-time visitor before they find the wiki on their own.
```

---

## What this plan does not do

Nothing above was posted, commented, closed or pinned by this plan. All four issues were
re-confirmed at zero comments after these bodies were written (see the Task 2 verification gate
and `evidence/173-04-draft-link-check.txt` for the mechanical link check run against them).
Posting, closing gh#6 and gh#7, and pinning gh#9 are plan 173-07's work, gated on this status
line changing away from `PENDING OPERATOR REVIEW`.

## Known cost accepted at activation

Backlog 999.9 will rename all three repositories and invalidate every URL in the four bodies
above. That is accepted at activation (see 173-CONTEXT.md); these four replies join the set of
this phase's own outputs needing re-sweeping once 999.9 runs, alongside Phases 169, 170 and 172.
The URLs above are kept in plain `https://github.com/henols/...` form, greppable by that sweep.

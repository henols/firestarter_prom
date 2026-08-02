---
phase: 130-close-honesty-ledger-claim-gate-release-decision
plan: 05
subsystem: docs
tags: [roadmap, honesty-ledger, record-correction, py32f071, backlog-retirement]

# Dependency graph
requires:
  - phase: 130-close-honesty-ledger-claim-gate-release-decision (plan 130-04)
    provides: the v1.23 Milestones-list entry, the v1.28 Binary Command Protocol renumber, the collapsed py32 retirement line, and the exact worklist of what the renumber broke (999.23/999.24 `→ v1.28` pointers, v1.30's stale back-reference)
provides:
  - "Backlog stubs 999.23 and 999.24 retired as delivered-into-v1.23 (Phases 123-130), replacing their `⏫ QUEUED → v1.28` pointers and stale prior-art claims"
  - "v1.30 Milestones-list entry's back-reference corrected to name the landed retirement instead of an occupied v1.29 slot"
  - "One additive inline supersession note at ROADMAP.md:1883 disarming the `scope v1.28 from that document` instruction"
  - "999.25's `→ v1.30, NEXT after v1.23` pointer verified true and recorded as a no-op (D-15's second half)"
  - "correct-v128-py32-roadmap-prior-art todo moved to todos/completed/ with an item-by-item discharge account"
affects: [130-06, 130-16]

# Tech tracking
tech-stack:
  added: []
  patterns: ["measure-before-edit: Task 1 enumerates every D-15 subject site before any ROADMAP.md edit runs, so no pointer repair is invented and none is missed"]

key-files:
  created: []
  modified:
    - .planning/ROADMAP.md
    - .planning/todos/pending/correct-v128-py32-roadmap-prior-art.md
    - .planning/todos/completed/correct-v128-py32-roadmap-prior-art.md

key-decisions: []

requirements-completed: []  # This plan ticks NO requirement ids (CLOSE-03 is discharged only by plan 130-16)

# Metrics
duration: TBD
completed: TBD
status: in-progress
---

# Phase 130 Plan 05: Repair the v1.28 Renumber's Broken Pointers + Retire Backlog Stubs 999.23/999.24 Summary

**Retired backlog stubs 999.23 and 999.24 as delivered into v1.23 PY32F071 Integration (Phases 123-130), repaired every `→ v1.28` pointer the plan-04 renumber broke, corrected the v1.30 entry's now-false "v1.29 slot immediately above" back-reference, and disarmed one dated instruction clause (`ROADMAP.md:1883`) with an additive supersession note — while leaving the four sibling dated review-pass paragraphs and 999.25's pointer byte-unchanged.**

## Task 1: D-15 subject-set measurement (pre-edit)

Measured every site before touching `ROADMAP.md`, per the plan's own "measure before you edit" requirement.

**1. `the v1.29 slot immediately above` phrase count.**

```
grep -c 'the v1.29 slot immediately above' .planning/ROADMAP.md
1
```

Exactly one hit, at `ROADMAP.md:35` (the `v1.30 SDP Surface Retirement & Behavioral Lock Proof` Milestones-list entry). **Verdict: D-15's 999.25 half has no subject and is a no-op.** The phrase does not occur anywhere in the `999.25` stub itself (lines 1755-1786) — 999.25's own heading pointer is `→ v1.30, NEXT after v1.23`, which is a *forward* reference (this stub becomes v1.30) and carries no "v1.29 slot" language to correct. The one occurrence found is inside the **v1.30 Milestones-list entry**, which Task 2 corrects as its own numbered item (item 3 below), not as a 999.25 edit. Recording this as a no-op is preferable to inventing an edit inside the 999.25 stub that D-15's own text does not require.

**2. `999.23` / `999.24` line numbers needing a pointer repair**, with current text and intended corrected target:

| Line | Current text (relevant excerpt) | Needs |
|---|---|---|
| 1723 | `### Phase 999.23: ... (⏫ QUEUED 2026-07-27 → v1.28, leads — gh#16)` | Heading pointer repair — `v1.28` now means Binary Command Protocol |
| 1732 | `**⏫ QUEUED (...) — this and 999.24 become one milestone slot, provisional \`v1.28 PY32F071 Port\`**, ... Prior art verified at this review — \`henols/firestarter\` **PR #46 is CLOSED unmerged**... branch \`feature/py32f071-toolchain\` @ \`2c2ed10\`... \`platform/py32f071/PORTING.md\` (195 lines)... **Scope from that document**...` | Disposition rewrite — retire, correct slot-name pointer, and correct the three stale claims (PR #46/#48, `2c2ed10`, `PORTING.md`) |
| 1738 | `### Phase 999.24: ... (⏫ QUEUED 2026-07-27 → v1.28, follows — gh#17)` | Heading pointer repair |
| 1749 | `**⏫ QUEUED (...) — follows 999.23 inside the provisional \`v1.28 PY32F071 Port\` milestone slot.**...` | Disposition rewrite — same retirement |

No other line in the `999.23`/`999.24` region (1723-1753) carries a `v1.28` / `leads` / `follows` / `provisional` token beyond these four sites (confirmed by targeted `grep -n` restricted to that line range).

**3. `999.25` heading, verbatim, and its verdict:**

```
### Phase 999.25: Retire `dev sdp`; prove the SDP lock behaviorally in `dev test`; land `write --sdp-relock` (⏫ QUEUED 2026-07-31 → v1.30, NEXT after v1.23)
```

Verdict: this pointer (`→ v1.30, NEXT after v1.23`) **stays true and needs no change**. It names the milestone this stub becomes (v1.30), not the v1.29 slot — it was never broken by the renumber.

**4. Dated review-pass paragraph line numbers and the history-exemption ruling.**

The five dated review-pass paragraphs this plan's scope touches: `ROADMAP.md:1747`, `:1877`, `:1879`, `:1883`, `:1887`.

**Ruling: history-exempt.** Rewriting a dated, signed review record to reflect facts discovered later is the same error D-05 avoids for the branch-state note — a dated paragraph records what was believed and decided *on that date*, and it is supposed to look stale once superseded; that staleness is itself the historical fact being preserved. `must_haves.prohibitions`' own escape clause (criterion 1) covers a labeled correction *or history* block, and these paragraphs are the "or history" case: append-only session logs, not living claims.

**The single exception: `ROADMAP.md:1883`.** Its final clause — "scope v1.28 from that document rather than re-deriving the boundary" — reads grammatically as an **instruction to a future reader**, not a record of what was decided that day. A future reader who followed it today would scope from a document (`platform/py32f071/PORTING.md`) that A-6/R-8 (`130-RESEARCH.md`) established exists only on the two closed pull requests (#46/#47) and does not match what PR #48 actually built. That is live, actionable staleness inside an otherwise-historical paragraph, so it gets Task 2's one additive inline supersession note — the paragraph's dated text is preserved untouched, and the note disarms only the instruction.

The other four (`:1747`, `:1877`, `:1879`, `:1887`) carry no comparable forward-facing instruction — they are pure "what we decided/found that day" prose — and are left completely untouched.

**5. `999.22` region — verified, not assumed, untouched.**

```
sed -n '1700,1722p' ROADMAP.md | grep -n 'v1\.28\|v1\.27'
```

Result: the only version pointer in the `999.22` region (lines 1700-1722) is `v1.27` (its own correct target, unaffected by the renumber). **No `v1.28` pointer exists in the `999.22` region.** D-15's "999.22 untouched" claim is confirmed by measurement, not repeated from the decision text unverified.

**`git -C /workspaces diff --stat -- .planning/ROADMAP.md` at the end of this task: empty** — no edit was made in Task 1.

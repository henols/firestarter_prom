---
title: v1.30 close — run /gsd-complete-milestone then /gsd-pr-branch targeting beta (NOT a direct beta merge)
date: 2026-08-04
priority: high
blocked_by: Phase 137 must close first. Operator confirmed 2026-08-04 that the close fires AFTER Phase 137, not after Phase 133.
resolves_phase: 137 (close) — this is the procedure the close itself must follow
---

# Standing operator instruction for the v1.30 close

Given by the operator **2026-08-04**, while Phase 133 was mid-execution in a separate session.

**The sequence:**

1. Phases 133 → 134 → 136 → 137 all complete. (135 stays vacant — deferred to Backlog 999.28.)
   **The operator drives all of these** — 133 was already executing in its own session when this
   instruction was given, and the operator confirmed 2026-08-04 that 134, 136 and 137 are theirs too.
2. `/gsd-complete-milestone`
3. `/gsd-pr-branch` **targeting `beta`**

**Ownership split:** steps 2 and 3 are the assistant's; step 1 is entirely the operator's. Do not
start a phase, plan a phase, or advance the roadmap unprompted — wait for the operator to say Phase
137 has closed. Verify that independently before closing (Phase 137's plans all ticked, CLOSE-01…06
and RELOCK-07 all `[x]` in `REQUIREMENTS.md`) rather than taking the signal on faith.

## What is NEW here — this is a change to the close procedure

Every prior milestone (v1.18 … v1.23) closed by **merging the milestone branch into `beta`
directly** and pushing. The operator's instruction for v1.30 is a **PR branch to `beta`**, not a
direct merge. `/gsd-pr-branch` exists precisely to filter the `.planning/` commits out, so the PR
carries only the `firestarter_app` source change.

Do not silently substitute the old direct-merge close because that is what the last six milestones
did.

## Two recorded hazards this interacts with

**H-1 — a push to `beta` auto-fires CI and cuts a spurious beta.** Recorded at the v1.21 close,
where it fired **twice**. A PR branch does not push `beta` itself, so opening the PR is safe; the
hazard moves to whoever **merges** it. Flag this on the PR body rather than assuming the merger
knows.

**H-2 — the milestone close breaks its own record gates.** Archiving sections orphans `lines=N`
exemptions, and `git rm REQUIREMENTS.md` trips fail-closed target lists. Expect to repair gate
target lists during the close, not after.

## Scope confirmed at the same time

The operator explicitly rejected closing early at Phase 133 or Phase 134. v1.30 ships all 50
requirements across phases 131, 132, 133, 134, 136, 137 — including Phase 134's oracle, which is
the milestone's user-visible deliverable.

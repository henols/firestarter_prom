---
title: v1.30 close — run /gsd-complete-milestone then /gsd-pr-branch targeting beta (NOT a direct beta merge)
date: 2026-08-04
priority: high
blocked_by: Phase 137 must close first. Operator confirmed 2026-08-04 that the close fires AFTER Phase 137, not after Phase 133.
resolves_phase: 137 (close) — this is the procedure the close itself must follow
carried_to_phase: 138
---

> **⚠ CARRIED FORWARD 2026-08-08 → v1.31 Phase 138 (PREP-01).** Step 3 never ran. Measured on
> 2026-08-08: `firestarter_app`'s `gsd/v1.30-sdp-surface-retirement` is **not** an ancestor of
> `origin/beta`, and `gh pr list` shows no open v1.30 PR — the PR body was staged
> (`.planning/v1.30-PR-BODY.md`, commit `d0f0c6a0`) but the PR was never opened, even though v1.30 is
> recorded as shipped in `MILESTONES.md`. v1.31 touches the host, so this blocks its app branch fork.
> Operator decision 2026-08-08: **land v1.30 to `beta` first**, then fork v1.31's app branch off the
> updated `beta`. PREP-01 verifies it with `git merge-base --is-ancestor` rather than trusting the
> milestone record. This todo stays open until that check exits 0.

# Standing operator instruction for the v1.30 close

Given by the operator **2026-08-04**, while Phase 133 was mid-execution in a separate session.

**The sequence:**

1. Phases 133 → 134 → 136 → 137 all complete. (135 stays vacant — deferred to Backlog 999.28.)
2. `/gsd-complete-milestone`
3. `/gsd-pr-branch` **targeting `beta`**

**Ownership split (revised 2026-08-04 — the operator reversed the earlier "I drive the phases"):**

- **Phase 133** — operator's, already executing in its own session when this note was written.
- **Phases 134, 136, 137** — the assistant drives: discuss → research → plan → execute. 134 and 136
  both carry `Research flag: NEEDS --research-phase`.
- **Steps 2 and 3** — the assistant's.

**Operator instruction 2026-08-04: BATCH every hand-off to the very end.** Do not pause mid-phase to
collect an operator action. Run 134 → 136 → 137 straight through, park anything that needs the
operator, and present the whole batch once at the end.

**Measured, not assumed — what the batch actually contains:**

- **CLOSE-06's gh#12 reply.** Blocking operator wording review before posting. **Draft it and park
  it; never post it unattended.** Phase 137 must NOT run under `--auto`/`--chain`, which
  auto-approves exactly this gate.
- **The push + PR to `beta`.** Outward-facing; stage it, then wait.
- *Maybe* Phase 136 criterion 4 (`dev reg` as held-erase-rail DMM proxy) — operator-only ONLY if it
  needs a real meter reading rather than a code-level assertion.
- *Optional* a final real CI green on the milestone branch before the PR — operator's call.

**A real `gh workflow run` dispatch is NOT needed for phases 134/136/137.** Checked 2026-08-04
against `REQUIREMENTS.md`: GATE-07 and RETIRE-06 were the only requirements ever mandating one, and
both are ticked with run IDs (`30822281624`, `30856059940`). The remaining LEG/CHAN/CLOSE
requirements mandate none. Their cross-cutting instruction asks for the **CI-parity recipe**
(`tools/ci_parity.sh`), which runs locally and needs no operator. Do not re-introduce a per-phase
dispatch stop out of habit from 131 and 132.

**When dispatching executors, name exactly which requirement IDs each plan may mark Complete** —
executors have prematurely ticked multi-plan requirements four times in one phase before.

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

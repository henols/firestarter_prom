---
title: Land `write --sdp-relock` — deferred out of v1.30 as Phase 135, tracked as Backlog 999.28
date: 2026-08-03
priority: medium
blocked_by: nothing technical — deferred by operator decision, not by a dependency. Every prerequisite already shipped (see "Nothing to redo" below). Promote via /gsd-review-backlog when a milestone slot is wanted.
resolves_phase: none (Backlog 999.28 — v1.30 Phase 135 was vacated, number not reused)
---

# `write --sdp-relock` was deferred out of v1.30 — and the deletion shipped without it

**Deferred 2026-08-03** by operator decision, while v1.30 Phase 132 was in flight at plan 08 of 09.
Scoped as **v1.30 Phase 135**, never planned, never executed — no `.planning/phases/135-*/` directory
was ever created. Filed as ROADMAP Backlog **999.28**, which carries the full goal, success criteria,
prerequisites and promotion constraints. **The v1.30 phase number was not reused:** Phases 136 and 137
keep their numbers and the 135 slot stays vacant, same convention as v1.13's Phase 75 → Backlog 999.4.

## Why this is a todo and not just a backlog stub

Because a **paired** change was split, and only one half shipped.

`REQUIREMENTS.md` §`write --sdp-relock` (RELOCK) opens with its own constraint:

> Must ship with the deletion — they are a pair, and deleting the lock before re-homing it strands the
> only legitimate use case the deleted command served.

v1.30 Phase 132 ships the deletion of `firestarter dev sdp <chip> enable|disable`. This half did not
ship with it. So **v1.30 strands exactly the use case that sentence names**, and the window stays open
until 999.28 is promoted:

- `write` auto-unlocks on every protocol-`0x0D` write (v1.22 policy (d), declinable via
  `--skip-sdp-unlock`) and **never re-locks**.
- The `dev sdp enable` surface is **gone**.
- ⇒ There is **no supported way to deliberately protect an SDP part**, and on `0x0D` the protection bit
  cannot be read back, so a user cannot observe the resulting state either.

That is an accepted cost, recorded in `REQUIREMENTS.md` §Out of Scope and ROADMAP §`Phase 135` /
§`Phase 999.28`. It is not a defect to fix — it is a **promise not to overstate**, which is what makes it
a live todo rather than a parked idea.

## The outward-facing obligation this creates for v1.30's own close

v1.30 Phase 137 (CLOSE-05, CLOSE-06) was amended on 2026-08-03 because both criteria previously
described a substitution that will not exist in the shipped release:

- **Release notes** must map `dev sdp disable` → `write` (automatic — real, the firmware auto-unlocks on
  every `0x0D` write), and `dev sdp enable` → **nothing in this release**: withdrawn, tracked as Backlog
  999.28. They must **not** map it to `write --sdp-relock`.
- **The gh#12 reply** must say the same thing. gh#12 asked for enable/disable; after v1.30 it gets
  `disable`-by-default and **no** `enable` at all. See the amended
  [`gh12-followup-after-dev-sdp-retirement.md`](gh12-followup-after-dev-sdp-retirement.md).

Announcing a command that does not exist in the release being announced is the same overclaim class as
v1.22's C-5 correction — the class v1.30's honesty ledger exists to catch. Getting this wrong would be
the milestone failing its own stated purpose in its most public artifact.

## What this todo owes, and when

1. **At v1.30's close (Phase 137)** — verify the release notes and the gh#12 reply describe a
   **withdrawal**, not a migration. This is the urgent half; it expires when v1.30 ships.
2. **Whenever 999.28 is promoted** — land the feature, then correct the record outward: the shipping
   version's release notes announce it, and gh#12 gets the follow-up it was promised. This half has no
   deadline.

## Nothing to redo at promotion time

Every prerequisite is already in the tree:

- Firmware `CMD_SDP_LOCK` / `CMD_SDP_UNLOCK` — v1.22 Phase 119. **Host-only work**: no firmware change,
  no dual-repo lockstep, no `.hex` re-cut.
- The capability gate to reuse — `sdp_capability()`.
- `eprom_operations.py` `sdp_unlock` / `sdp_lock` and their `COMMAND_NAMES` entries — kept deliberately,
  load-bearing for this caller. (Their dereference sites were re-measured by v1.30 plan 132-08 to
  `_setup_operation:329` / `_operation_context:405`; the older `:301`/`:377` citations are stale.)
- The D-10 honesty wording and D-14 unknown-command mapping — Phase 132 authored them into a shared
  production helper as an explicit **forward contract** for this caller (`132-CONTEXT.md` D-01), and
  `tests/test_sdp_honesty.py` is its stable module name (`132-03-SUMMARY.md:153` — no further rename
  owed).
- **Polarity already decided, do not re-litigate:** verify failure ⇒ **skip the relock and report it
  loudly**, leaving the recoverable state. Per v1.22 auto-unlock policy (d), recorded at
  `PROJECT.md:823`. Relocking a part whose write did not verify would protect a bad image behind a lock
  that cannot be read back and can only be cleared by another write.

## Constraints at promotion

- **One-writer-per-file.** This writes `firestarter/cli_handlers.py` in the `write` handler (~:570).
  Worktree isolation is unavailable while the code lives in the `firestarter_app` submodule — the
  executor commit protocol cannot commit into a submodule from an isolated worktree — so it cannot run
  concurrently with another phase writing that file. See ROADMAP §v1.30 "Dependency spine".
- **`write --help` changes.** Any `write`-help output pinned by v1.30 Phase 136's channel-gating tests
  must be updated **deliberately** as part of this work, not silently re-baselined.

## Related

- ROADMAP Backlog **999.28** — the promotable stub (full success criteria).
- ROADMAP §v1.30 `### Phase 135` — the deferral record and renumbering rationale.
- `REQUIREMENTS.md` §RELOCK — RELOCK-01…06 retained verbatim with `⏸` checkboxes; §Out of Scope carries
  the decision row.
- **RELOCK-07 did NOT come here.** The stale-label re-homing stayed in v1.30, re-homed to Phase 137, and
  its targets now name Backlog 999.28. It also carries a warning worth reading: four places in the
  record cite those two labels and no two agree.

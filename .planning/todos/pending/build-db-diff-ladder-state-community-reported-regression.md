---
title: "`build_db_diff`'s `ladder_state` no longer reaches `community-reported` for a genuinely-passing ALLOW chip"
date: 2026-08-05
priority: low
blocked_by: nothing technical — deferred as a scope-discipline decision, not a dependency. The fix touches `diagnostic_report.py`/`classify_fingerprint`, both outside every Phase 137 plan's declared file scope.
resolves_phase: none (found by v1.30 Phase 134, confirmed-and-deferred by 134-06, dispositioned by Phase 137 plan 137-04 — no phase fixes the underlying code)
owner: henols
---

# `build_db_diff`'s `ladder_state` regression — a real, still-open finding this milestone only recorded

**Owner: henols** (the repo owner/operator), matching this project's established convention for a
genuinely-unowned finding that needs a human decision (see
`.planning/todos/pending/at28c256-write-path-failure-gh20.md`). May be reassigned to whoever picks
it up.

## The finding, verbatim from `134-RECORD.md` §6 residual 4

Once the SDP leg is genuinely reachable end to end, an all-OK `dev test` run on a genuinely-passing
ALLOW chip attaches an `"indeterminate"`-classified `Fingerprint` on the `write-baseline-b` /
`write-baseline-a` / `write-restored` steps — 134-02's own "attach in every arm" design meeting
`classify_fingerprint`'s four-bucket design, which has no dedicated "perfect match" bucket. This
routes `build_db_diff`'s `ladder_state` to `_LADDER_NONE` rather than
`_LADDER_COMMUNITY_REPORTED` for every genuinely-passing ALLOW chip going forward.

This is a real, chip-content-independent consequence of two already-shipped mechanisms (Phase 114,
Phase 133-02) meeting for the first time via Phase 134's own wiring — not an artifact of any one
plan's fixture choice. `diagnostic_report.py` / `classify_fingerprint` are outside every Phase 134
plan's declared file scope, so it was documented (the one shipped test this surfaces in was
repaired to assert the newly-measured correct value) rather than fixed.

## Why this is a todo, not a fix landed in Phase 137

Operator-batch item **C-1** (`.planning/v1.30-OPERATOR-BATCH.md` §C) asked for an explicit
disposition rather than a silent drop at close. Fixing `classify_fingerprint`'s four-bucket design
would touch `diagnostic_report.py`, a file outside every Phase 137 plan's declared file scope —
doing so here would be an undeclared scope expansion inside the milestone's own honesty-close
phase, the opposite of what this phase exists to do. **Disposition: defer-with-owner.** Filed here,
named, with an owner, instead of disappearing at close.

## What is owed

1. **A "perfect match" bucket (or equivalent) added to `classify_fingerprint`**, so an all-OK SDP
   leg run on a genuinely-passing ALLOW chip routes `ladder_state` to
   `_LADDER_COMMUNITY_REPORTED` again, matching the pre-Phase-134 behavior for a passing chip.
2. **The repaired test this finding surfaced in** (134-03/134-06) should be re-repaired to assert
   the corrected routing once the bucket exists — it currently asserts the regressed value as the
   newly-measured "correct" one, which is honest but not desirable long-term.
3. **May be reassigned** — `henols` is named as the repo owner/operator, not necessarily as the
   engineer who investigates.

## Related

- `.planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-RECORD.md` §6 residual 4 — the
  full finding, in the phase that discovered it.
- `.planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-06-PLAN.md` — the plan that
  confirmed and deferred it rather than absorbing a fix.
- `.planning/v1.30-OPERATOR-BATCH.md` §C item C-1 — the operator-facing record of this disposition.
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-DECISION.md` — the Phase
  137 artifact recording this disposition as part of the milestone's own close.

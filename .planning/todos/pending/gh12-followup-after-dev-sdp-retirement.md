---
title: Reply on gh#12 (and correct the b14 app release notes) after `dev sdp` is retired
date: 2026-07-31
priority: medium
blocked_by: the removal shipping — provisional milestone v1.30 (queued NEXT after v1.23, from Backlog 999.25). Do not post before the removal is real.
resolves_phase: 137
---

# gh#12 follow-up owed once `dev sdp` is retired

`firestarter dev sdp <chip> enable|disable` is named in two outward-facing artifacts published
**2026-07-30**, one day before the decision to remove it:

- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-GH12-COMMENT.md:15`
  — posted to [gh#12](https://github.com/henols/firestarter_prom/issues/12), the thread whose
  reporter had to build a separate Arduino to disable SDP before Firestarter could write at all
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-RELEASE-NOTES-app.md:12,22`
  — the `3.0.0b14` app release notes

The removal is decided in
[`.planning/notes/sdp-surface-retirement-and-behavioral-proof.md`](../../notes/sdp-surface-retirement-and-behavioral-proof.md)
and scoped as Backlog Phase 999.25.

## What the reply must say

1. **The command is gone, and what replaced it** — unlock is already `write`'s default behaviour
   (auto-unlock, declinable via `--skip-sdp-unlock`), and the deliberate lock is now
   `write --sdp-relock`.
2. **Name the rewording honestly.** gh#12 asked for "enable/disable" and gets neither by that name.
   Say so plainly rather than presenting the substitution as if it were the original ask.
3. **State the gain, without overclaiming it.** The lock is now *testable* — `dev test` on an
   SDP-capable part locks it, attempts a write without unlocking, and checks the chip is unchanged.
   That is the first oracle this feature has ever had. It remains **untested on real AT28C
   silicon**; `0x0D` stays `UNVERIFIED`. Do not let "now provable" drift into "now proven" — the
   same overclaim class as v1.22's C-5 correction.
4. **Ask for the run.** A reporter with an AT28C is exactly who can close the evidence gap: one
   `firestarter dev test <chip>` and the report it files.

## Constraints

- Outward-facing → **operator-reviewed before posting**, never auto-approved. `--auto`/`--chain`
  auto-approves human-verify checkpoints, so gate this separately
  (`reference_auto_mode_autoapproves_outward_facing_gates`).
- Do **not** post before the removal has actually shipped, or the thread will name a command that
  still exists.
- The b14 release notes are historical and already published — correct the *next* release notes,
  do not rewrite the shipped ones.

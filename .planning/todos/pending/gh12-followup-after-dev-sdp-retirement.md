---
title: Reply on gh#12 (and correct the b14 app release notes) after `dev sdp` is retired
date: 2026-07-31
priority: medium
blocked_by: the removal shipping — provisional milestone v1.30 (queued NEXT after v1.23, from Backlog 999.25). Do not post before the removal is real.
resolves_phase: 152  # v1.30 CLOSE-06 was held open by design; re-homed to v1.32 Phase 152 (OUT-01), where `write --sdp-relock` actually exists to be named
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

## ⚠ AMENDED 2026-08-03 — `write --sdp-relock` did NOT ship; point 1 below was rewritten

The reply's original point 1 named `write --sdp-relock` as the deliberate-lock replacement. **That is
now false.** v1.30 **Phase 135**, which was to land it, was deferred out of the milestone by operator
decision on 2026-08-03 and filed as ROADMAP Backlog **999.28**. Phase 132 still deletes `dev sdp` —
**both halves** — in v1.30. So the milestone removes the deliberate-protection surface and ships **no
replacement**.

Posting the original wording would tell a stranger to run a command that does not exist in the release
being announced. That is the same overclaim class as v1.22's C-5 correction, in the very thread this
reply exists to be honest with. See `.planning/todos/pending/write-sdp-relock-deferred.md`.

## What the reply must say

1. **The command is gone. `disable`'s behaviour survives; `enable`'s does not.** Unlock is already
   `write`'s default behaviour (auto-unlock on every protocol-`0x0D` write, declinable via
   `--skip-sdp-unlock`) — so `dev sdp disable` is genuinely redundant, not merely dropped. The
   deliberate **lock** is **withdrawn with no replacement in this release**, tracked as Backlog 999.28.
   Do **not** name `write --sdp-relock` as available. If it helps the reporter, it is fine to say the
   design is settled and the work is queued — but as *queued*, never as shipped, and without promising a
   version.
2. **Name the rewording honestly.** gh#12 asked for "enable/disable". After v1.30 it gets `disable`'s
   effect automatically and **no `enable` at all**. Say both halves plainly — including that a user who
   wants a part left protected currently has no supported way to do it, and cannot read the protection
   bit back to check. Do not present this as if it were the original ask satisfied.
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
- **Do not name `write --sdp-relock` as an available command** (see the amendment above). The "Removed"
  mapping in the next release notes must read `dev sdp disable` → `write` (automatic) and
  `dev sdp enable` → *withdrawn, no replacement, tracked as Backlog 999.28*.

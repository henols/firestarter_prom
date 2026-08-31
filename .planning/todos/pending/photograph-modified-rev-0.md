---
id: photograph-modified-rev-0
title: Photograph operator's Modified Rev 0 board (Phase 31 follow-up #3)
captured: 2026-05-26
status: pending
type: documentation
target_milestone: post-v1.7
priority: MEDIUM
related_phase: 31
resolves_phase_followups: [Phase 31 follow-up #3]
deferred_from: Phase 35 (per Phase 35 CONTEXT.md D-07)
---

# Photograph operator's Modified Rev 0 board (Phase 31 follow-up #3)

## The deferral

Operator photo session for the third on-hand RURP shield (Modified Rev 0 — hardware-bug-A/B rework with cuts + jumpers) was deferred from Phase 31 to Phase 35, then deferred again from Phase 35 to post-v1.7 per D-07. Rationale: the rework trace is independent of v1.7's detect-fw substrate. The operator's Modified Rev 0 board uses the EEPROM `hw_revision` override path regardless of how the rework cuts/jumpers landed; firmware detect logic does not depend on Modified Rev 0 specifics during v1.7 (broad-bucket `REVISION_2_0` + override fall-through cover all observed cases).

Phase 35 Wave 3 bench session (2026-05-26) discovered that the Modified Rev 0 board, after Plan 01 INPUT high-Z fix, lands in the mid ADC band (220-600) → firmware classifies as `REVISION_2_3`. This is consistent with an external 10k pull-up on A3 added by the rework, but the exact cut/jumper trace is uninventoried.

## What's needed

Photographs to `.planning/v1.7/photos/rev-0-modified/`:
- `top.jpg` — full top view, all components visible, silkscreen-version region readable if present
- `bottom.jpg` — full bottom view
- `silkscreen.jpg` — macro of silkscreen-version region (or "no silkscreen-version printed" if Rev 0 era pre-dates the convention)
- `rework-cuts.jpg` — close-up of each PCB trace cut (with annotations)
- `rework-jumpers.jpg` — close-up of each added jumper / mod wire (with annotations identifying which net it bridges to which)
- (Optional) `r41-area.jpg` — close-up of where R41 would be on a stock Rev 2.0+ board, to document whether the rework added a substitute R41 or wired in a 10k pull-up via a different mechanism

## Sentinel cross-references (preserve verbatim per Phase 35 D-Discretion Pattern E)

The following sentinels in `.planning/v1.7-SHIELD-REVS.md` carry `as-modified — pending Phase 35` or `pending Phase 35` annotations that will resolve when this todo + its companion (`write-modifications-md-rework-trace.md`) close:

- `.planning/v1.7-SHIELD-REVS.md` §1 row 4 (Modified Rev 0 row — `state: upstream-only`, `photo_dir: —`)
- `.planning/v1.7-SHIELD-REVS.md` §4 row 8 (Rev 2.2 → Modified Rev 0 electrical delta — `as-modified — pending Phase 35`)
- `.planning/v1.7-SHIELD-REVS.md` §5 row 7 (mechanical delta — `as-modified — pending Phase 35`)
- `.planning/v1.7-SHIELD-REVS.md` §6 row 91 (capability matrix Modified Rev 0 row — `as-modified — pending Phase 35`)
- `.planning/v1.7-SHIELD-REVS.md` §7 row 16+17 (R41 + JP4 alias rows — `as-modified — pending Phase 35` for mod_rev_0 column)

## When to triage

- At next milestone-start sweep (`/gsd-new-milestone`); operator can opt to bundle this with another bench-touch milestone (e.g., v1.6 Phase 27 RCA re-open if the bench-attached Modified Rev 0 board is being used during the A/B disambiguation)
- Standalone "v1.8: Modified Rev 0 documentation completion" mini-milestone is also viable

## Cross-references

- Memory `[[user_shield_revisions]]` — operator owns Rev 2.2 / Rev 2.0 / Modified Rev 0; EEPROM byte doesn't disambiguate
- Phase 35 CONTEXT D-07 — deferral rationale
- Phase 31 Plan 05 — original photo session that was blocked
- Companion todo: `write-modifications-md-rework-trace.md` (Phase 31 follow-up #4 — depends on photos as evidentiary substrate)
- Phase 35 bench evidence: `.planning/v1.7/bench-evidence-35.md` §"Modified Rev 0 Board" — bench observation that the rework wired a 10k pull-up on A3

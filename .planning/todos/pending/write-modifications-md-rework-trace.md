---
id: write-modifications-md-rework-trace
title: Write full MODIFICATIONS.md rework trace for operator's Modified Rev 0 (Phase 31 follow-up #4)
captured: 2026-05-26
status: pending
type: documentation
target_milestone: post-v1.7
priority: MEDIUM
related_phase: 31
resolves_phase_followups: [Phase 31 follow-up #4]
deferred_from: Phase 35 (per Phase 35 CONTEXT.md D-07)
resolves_phase: 164
depends_on: photograph-modified-rev-0
---

# Write full MODIFICATIONS.md rework trace for operator's Modified Rev 0 (Phase 31 follow-up #4)

## The deferral

Companion to `photograph-modified-rev-0.md` — the rework trace requires the photographs as evidentiary substrate. Both deferred from Phase 31 → Phase 35 → post-v1.7 per Phase 35 D-07. Independence from v1.7 detect-fw substrate confirmed by Phase 35 Wave 3 bench session: firmware correctly handles the Modified Rev 0 board via the broad-bucket `REVISION_2_0` + override fall-through path regardless of rework internals.

Phase 35 bench discovery: the Modified Rev 0 board's A3 net reads in the mid band (220-600) → firmware classifies as `REVISION_2_3`. Implies the rework added an external 10k pull-up on A3. Exact wiring (which trace was cut, which jumper added, what net it connects to) is uninventoried.

## What's needed

Author `.planning/v1.7/MODIFICATIONS.md` (currently a stub created in Phase 31 Plan 05) with:

Per-rework-entry trace against upstream Rev 0 schematic blob `d2a7f691` on `origin/rev2.0`:

For each cut + jumper:
1. **Net affected** (which schematic net was the cut on; which two nets does the jumper bridge)
2. **Schematic-side delta** (compare modified state against the upstream blob — what would have been connected pre-rework vs post-rework)
3. **Capability matrix delta** (does this rework change which chip families / algorithms the board can program? Likely no — the rework is the hardware-bug-A/B fix, not a capability change)
4. **Bench evidence** (the Phase 35 ADC mid-band reading + the `MSG_OK_REV` `Rev 2.0-class, Override HW: Rev 2.3` output is one data point; additional evidence as needed)
5. **Rationale** (what was the original bug being fixed; cite memory `[[user_shield_revisions]]` for "hardware-bug-A/B" context if relevant)

Cross-link from `.planning/v1.7-SHIELD-REVS.md` Modified Rev 0 rows to the new MODIFICATIONS.md sections.

## Sentinel resolution

Once both todos close, upgrade the following `.planning/v1.7-SHIELD-REVS.md` rows from `as-modified — pending Phase 35` to bench-verified state:
- §1 row 4 (`state` flips to `operator-photographed`; `photo_dir` to `.planning/v1.7/photos/rev-0-modified/`)
- §4 row 8 (Rev 2.2 → Modified Rev 0 electrical delta — fill with per-cut/per-jumper specifics)
- §5 row 7 (mechanical delta)
- §6 row 91 (capability matrix Modified Rev 0 row — should match parent Rev 0 capability set if rework is the hardware-bug-A/B fix without capability changes)
- §7 row 16+17 (R41 + JP4 alias rows — Modified Rev 0 column)

Bench-evidence-35.md analysis is the seed for the rework-trace narrative.

## When to triage

**AFTER** `photograph-modified-rev-0.md` resolves. Sequence:
1. Schedule operator photo session (or fold into next bench-touch milestone)
2. Operator captures the 5+ photos to `.planning/v1.7/photos/rev-0-modified/`
3. Author working through the photos + upstream schematic blob + Phase 35 bench evidence → write MODIFICATIONS.md
4. Update SHIELD-REVS.md sentinel rows
5. Close both todos atomically

## Cross-references

- Phase 35 CONTEXT D-07 — deferral rationale
- Phase 31 Plan 05 — original MODIFICATIONS.md stub creation
- Phase 35 bench evidence: `.planning/v1.7/bench-evidence-35.md` §"Modified Rev 0 Board" — 10k pull-up inference seed
- Upstream Rev 0 schematic blob `d2a7f691` on `origin/rev2.0` in `firestarter` sub-repo's upstream clone (`.planning/v1.7/upstream-rurp/`)
- Companion (predecessor) todo: `photograph-modified-rev-0.md` (Phase 31 follow-up #3)
- Memory `[[user_shield_revisions]]` — "hardware-bug-A/B" rework context

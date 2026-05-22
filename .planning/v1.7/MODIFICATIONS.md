# Modified Rev 0 — Rework Trace

**Phase:** 31 (Plan 05)
**Board:** Operator's Modified Rev 0 (per memory `[[user_shield_revisions]]`)
**Photo session date:** not captured — board unavailable this session
**Upstream Rev 0 schematic anchor:** `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch` (recovered from `origin/rev2.0` branch — see `mine-notes.md` §Zip-archive listings + `31-04-SUMMARY.md`)
**Operator:** Henrik Olsson
**Purpose:** Document every operator-side rework on the Modified Rev 0 board (cuts, jumpers, component swaps), cross-referenced against the upstream Rev 0 schematic so Phase 32 capability matrix + Phase 27 RCA re-open (v1.6) can use this board with a known-good schematic substrate.

**Status:** STUB — operator photographs were not captured during this Phase 31 session.
The board is on-hand but was unavailable for photography. Per the Plan 31-05 resume-signal
contract: "if the board is unavailable, this row's state in §1 becomes `upstream-only` and
MODIFICATIONS.md becomes a stub noting the unavailability."

---

## Rework Region 0 — Modified Rev 0 unavailable for this session

This section is a placeholder. The Modified Rev 0 board was not photographed during Phase 31
(operator signaled `blocked: no photos available this session`). The rework trace against the
upstream Rev 0 schematic was therefore not performed. The operator's third board (Modified Rev 0,
per memory `[[user_shield_revisions]]`) carries hardware-bug-A/B rework consisting of cuts and
jumpers; the precise regions and cross-references to upstream nets are pending the Phase 35
photograph follow-up.

Cross-ref: UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch §full-board (no operator-side rework trace captured this session — board not photographed; Phase 35 follow-up flagged)

This file will be updated in Phase 35 when the operator photographs the Modified Rev 0 board
and traces each rework region visually against the upstream Rev 0 schematic (blob d2a7f691 on
`origin/rev2.0`). At that time, each rework region will receive its own `## Rework Region N`
heading with a `Cross-ref:` line citing the upstream schematic section. The Phase 35 executor
must also upgrade the inventory row state from `upstream-only` to `on-hand-photographed` in
`.planning/v1.7-SHIELD-REVS.md` §1 and fill in the `photo_dir` and verbatim `silkscreen` columns.

---

## Phase 35 Follow-Up Required

The following actions are deferred to Phase 35:

1. Photograph the Modified Rev 0 board (top.jpg, bottom.jpg, silkscreen.jpg — mandatory per SILK-01).
2. Photograph each rework region (rework-N-region.jpg, one per identified cut/jumper).
3. Trace each rework against `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch`
   (git blob d2a7f691 on `origin/rev2.0`).
4. Replace this stub with one `## Rework Region N — <descriptor>` section per rework, each
   carrying a `Cross-ref:` line at column 0 per the Phase-gate check #5 contract.
5. Upgrade `.planning/v1.7-SHIELD-REVS.md` §1 Modified Rev 0 row from `upstream-only` to
   `on-hand-photographed`.

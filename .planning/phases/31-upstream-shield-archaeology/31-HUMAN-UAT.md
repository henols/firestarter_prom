---
status: partial
phase: 31-upstream-shield-archaeology
source: [31-VERIFICATION.md]
started: 2026-05-22T14:30:00Z
updated: 2026-05-22T14:30:00Z
---

## Current Test

[awaiting Phase 35 photo session]

## Tests

### 1. Photograph Rev 2.2 board + upgrade §1 inventory row
expected: `.planning/v1.7/photos/rev-2-2/` contains `top.jpg`, `bottom.jpg`, `silkscreen.jpg` (each > 50 KB); operator reads verbatim silkscreen string from `silkscreen.jpg`; `v1.7-SHIELD-REVS.md` §1 Rev 2.2 row updated from `state: upstream-only` → `state: on-hand-photographed`, `silkscreen: not-recovered` → verbatim string, `photo_dir: —` → `.planning/v1.7/photos/rev-2-2/`, notes `upstream-c2bd111` removed.
result: [pending]

### 2. Photograph Rev 2.0 board + upgrade §1 inventory row
expected: `.planning/v1.7/photos/rev-2-0/` contains `top.jpg`, `bottom.jpg`, `silkscreen.jpg` (each > 50 KB); operator reads verbatim silkscreen string; `v1.7-SHIELD-REVS.md` §1 Rev 2.0 row upgraded same as Rev 2.2 (state, silkscreen, photo_dir, notes).
result: [pending]

### 3. Photograph Modified Rev 0 + trace rework against upstream Rev 0 schematic
expected: `.planning/v1.7/photos/rev-0-modified/` contains `top.jpg`, `bottom.jpg`, `silkscreen.jpg`, plus 1+ `rework-N-<region>.jpg` macros (at least one per identified cut/jumper); `.planning/v1.7/MODIFICATIONS.md` stub replaced with full content — one `## Rework Region N — <descriptor>` heading per macro, each with `^Cross-ref:` line citing `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch` and a 1-3 sentence operator trace (original net → modified net → rationale); `v1.7-SHIELD-REVS.md` §1 Modified Rev 0 row upgraded same as above.
result: [pending]

### 4. Resolve R41 value discrepancy for Rev 2.2 (physical board vs chat vs schematic)
expected: Operator measures or visually inspects R41 on the physical Rev 2.2 board against the silkscreen-readable component value (often printed on body); compares against (a) Anders's CHAT-INTEL claim "10k for Rev 2.2" and (b) the upstream schematic blob showing R41=4k7 in Rev 2.0/2.1/2.2 (only Rev 2.3 schematic has 10k). One of three outcomes: (i) physical board confirms 10k → schematic is wrong, file upstream issue + update §3 row; (ii) physical board confirms 4k7 → CHAT-INTEL claim was misremembered, add a note to CHAT-INTEL.md §1; (iii) physical board has different value than both → document and escalate to Anders.
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps

Phase 35 follow-up items. Operator signaled `blocked: no photos this session` for both Plan 31-03 and Plan 31-05; this UAT persists the deferred work so `/gsd-progress` and `/gsd-audit-uat` surface it in future planning sessions.

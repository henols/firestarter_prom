---
phase: 31-upstream-shield-archaeology
plan: "05"
subsystem: hardware-archaeology
tags: [rurp-shield, inventory, rework-trace, r41-detect, v1.7, shield-revs]

# Dependency graph
requires:
  - phase: 31-01-substrate-and-gitignore
    provides: gitignore policy (.planning/v1.7/**) and photo-dir substrate
  - phase: 31-02-chat-intel
    provides: CHAT-INTEL.md with dated Anders/henols quotes (check #6 contract)
  - phase: 31-03-photos-rev22-rev20
    provides: photo-dir skeletons for Rev2.2 + Rev2.0 (partial-pass; both boards upstream-only)
  - phase: 31-04-mine-and-scaffold
    provides: mine-notes.md (5-pass git mine) + v1.7-SHIELD-REVS.md §1-§9 scaffold

provides:
  - ".planning/v1.7/MODIFICATIONS.md — stub per unavailable-board contract; Phase 35 follow-up flagged"
  - ".planning/v1.7-SHIELD-REVS.md §1 filled — 8 inventory rows, all upstream-only (photos blocked)"
  - ".planning/v1.7-SHIELD-REVS.md §2 filled — Rev2.0 naming-ambiguity resolved; no unrecoverable revs"
  - ".planning/v1.7-SHIELD-REVS.md §3 filled — 4 R41 rows (Rev2.0/Rev2.1/Rev2.2/Rev2.3)"
  - "Phase 31 close-gate: all 8 phase-gate checks pass"

affects:
  - phase-32 (§4-§5-§6 diff matrix fills; all rows upstream-only — no on-hand bench data)
  - phase-33 (§7 silkscreen alias table; silkscreen=not-recovered for all 3 operator boards until Phase 35)
  - phase-34 (§8-§9 ADC band table; R41 values per rev from §3 are the substrate)
  - phase-35 (photograph all 3 operator boards; upgrade rows from upstream-only to on-hand-photographed)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Stub MODIFICATIONS.md per resume-signal contract (board unavailable → upstream-only state + Phase 35 follow-up)"
    - "upstream-only + not-recovered fallback for all 3 operator boards (photos blocked this session)"
    - "D-03 canonical ID: upstream-<short-sha> in notes column for silkscreen-not-recovered rows"
    - "removed-from-main + non-blank removed_commit for operator-derived board (n/a operator board)"
    - "8-check phase-gate suite runs clean — Phase 31 close-gate satisfied"

key-files:
  created:
    - ".planning/v1.7/MODIFICATIONS.md — 48-line stub; 1 Cross-ref line; Phase 35 deferred actions listed"
  modified:
    - ".planning/v1.7-SHIELD-REVS.md — §1 (8 rows), §2 (1 resolved-ambiguity row), §3 (4 R41 rows)"

key-decisions:
  - "Task 1 skipped per orchestrator: operator photos blocked this session (same signal as Plan 03)"
  - "All 3 operator boards (Rev2.2, Rev2.0, Modified Rev0) use state=upstream-only in §1 per Plan 03 downstream instructions + orchestrator directive"
  - "Modified Rev0 provenance=removed-from-main (parent Rev0 is removed-from-main); removed_commit=n/a (operator board — parent Rev0 removed at c2bd111)"
  - "8 §1 rows total: Rev2.3, Rev2.2, Rev2.1, rev2-lowercase, Rev2.0-working, Rev1, Rev0, Modified-Rev0"
  - "§2 contains Rev2.0 naming-ambiguity note (resolved: both captured in §1 as two distinct rows)"
  - "Rev2.3 NOT silkscreen-only vs Rev2.2: schematic shows R41 4k7→10k AND JP4 footprint 1x2→2x2 — Phase 32 diff required (Finding F from mine-notes)"

patterns-established:
  - "All 8 phase-gate checks pass with zero on-hand-photographed rows (check #3 trivially passes)"
  - "Phase 35 is the canonical handoff for all 3 operator board photographs"

requirements-completed: [HW-INV-01, HW-INV-02, HW-INV-03, SILK-01]

# Metrics
duration: ~50min
completed: "2026-05-22"
---

# Phase 31 Plan 05: Modified Rev 0 and Synthesis Fills Summary

**Phase 31 close-gate passed: MODIFICATIONS.md stub committed, v1.7-SHIELD-REVS.md §1/§2/§3 filled with 8 inventory rows + 4 R41 rows (all upstream-only; photos blocked this session), all 8 phase-gate checks green.**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-05-22T14:30:00Z (approx)
- **Completed:** 2026-05-22
- **Tasks:** 3 of 4 executed (Task 1 skipped per orchestrator directive — no photos available; Task 4 verification-only)
- **Files modified/created:** 2

## Accomplishments

### Task 1: Skipped (blocked — no photos available this session)

Per the orchestrator directive and Plan 31-05 resume-signal contract: "if the board is unavailable, this row's state in §1 becomes `upstream-only` and MODIFICATIONS.md becomes a stub noting the unavailability." No JPGs created. No operator wait. No fake files.

### Task 2: Stub MODIFICATIONS.md written and committed

`.planning/v1.7/MODIFICATIONS.md` created as a 48-line stub:

- Frontmatter cites `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch` as the upstream Rev0 schematic anchor
- One `## Rework Region 0 — Modified Rev 0 unavailable for this session` heading
- One `Cross-ref:` line at column 0 (phase-gate check #5 contract): `Cross-ref: UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch §full-board (no operator-side rework trace captured this session — board not photographed; Phase 35 follow-up flagged)`
- Phase 35 follow-up section listing 5 deferred actions
- Commit: `67d518c`

### Task 3: §1 + §2 + §3 filled in v1.7-SHIELD-REVS.md

#### §1 Inventory Row Breakdown

8 rows total, all `state: upstream-only` (photos blocked across all 3 operator boards):

| Rev | Provenance | State | upstream-SHA (notes) |
|-----|------------|-------|----------------------|
| Rev 2.3 | on-main | upstream-only | upstream-c2bd111 |
| Rev 2.2 | on-main | upstream-only | upstream-c2bd111 |
| Rev 2.1 | on-main | upstream-only | upstream-50a6ea4 |
| rev2 (lowercase) | on-main | upstream-only | upstream-28e0239 |
| Rev 2.0 working | on-main | upstream-only | upstream-a252e39 |
| Rev 1 | removed-from-main | upstream-only | upstream-b84e9e0 |
| Rev 0 | removed-from-main | upstream-only | upstream-486f3d1 |
| Modified Rev 0 | removed-from-main | upstream-only | upstream-486f3d1 (parent) |

All 3 operator-on-hand boards (Rev2.2, Rev2.0, Modified Rev0): `state: upstream-only`, `photo_dir: —`, `silkscreen: not-recovered`.

#### Canonical upstream-SHA IDs assigned to 3 operator boards

Per D-03, these are the canonical not-recovered IDs for the 3 boards the operator owns:

- **Rev 2.2:** `upstream-c2bd111` (introduced in Rev 2.3 commit when gerbers were archived)
- **Rev 2.0:** `upstream-a252e39` (Rev2 era commit, Oct 2024, first R41 introduction)
- **Modified Rev 0:** `upstream-486f3d1` (parent Rev0, Hardware release day 2024-04-18)

Phase 35 will replace these with verbatim silkscreen strings once boards are photographed.

#### §2 Mentioned-but-not-recovered

One entry: Rev2.0 naming ambiguity (branch named `rev2.0` vs shipped revision "Rev2.0") — resolved. Both the "rev2 lowercase" (deprecated gerber dump) and "Rev2.0 working schematic" are captured in §1 as separate rows. No unrecoverable revisions surfaced from CHAT-INTEL.

#### §3 R41 Values per Rev

From `mine-notes.md` §Per-rev R41 grep results:

| Rev | R41 value | Source blob |
|-----|-----------|-------------|
| Rev 2.0 working | 4k7 (4.7kΩ) | d2a7f691 on origin/rev2.0 |
| Rev 2.1 | 4k7 (4.7kΩ) | f3b7a521 on origin/Rev2.1 |
| Rev 2.2 | 4k7 (4.7kΩ) per schematic (DISCREPANCY: Anders stated "10k" in CHAT-INTEL 2025-04-28 — 10k only in Rev2.3 schematic) | f3b7a521 (same blob as Rev2.1) |
| Rev 2.3 | 10k (10kΩ) | fe35bd78 on origin/Rev2.3 + main |

**Rev2.3 not-silkscreen-only contradiction:** CHAT-INTEL §5 records Anders stating Rev2.3 is "silkscreen-only diff" vs Rev2.2. The mine schematic diff shows: (1) R41 value 4k7 → 10k; (2) JP4 footprint 1x2 → 2x2; (3) schematic file renamed. This is a substantive change. Phase 32 diff matrix must document both the R41 value change and the JP4 footprint change under §4 (Electrical) and §5 (Mechanical).

### Task 4: All 8 phase-gate checks passed

Full suite output:

```
=== Check 1: gitignore functional ===
=== Check 2: inventory NF=11 ===
=== Check 3: on-hand-photographed dirs ===
=== Check 4: removed-from-main removed_commit non-blank ===
=== Check 5: MODIFICATIONS.md cross-refs >= rework macros ===
  Cross-refs: 1, rework macros: 0
=== Check 6: CHAT-INTEL.md key quotes ===
=== Check 7: §4-§9 OWNED-BY markers (literal em-dash U+2014) ===
=== Check 8: §1-§3 own no TBD marker ===
=== ALL 8 CHECKS PASS ===
```

Check #3 trivially passes (zero on-hand-photographed rows — loop runs zero iterations).
Check #5 trivially passes (1 Cross-ref >= 0 rework macros).

## Phase 35 Follow-Up Todos

These are the canonical Phase 35 photograph/upgrade actions:

1. **Photograph Rev 2.2 board:** top.jpg, bottom.jpg, silkscreen.jpg → `.planning/v1.7/photos/rev-2-2/`; upgrade row state from `upstream-only` to `on-hand-photographed`; fill verbatim silkscreen + photo_dir
2. **Photograph Rev 2.0 board:** top.jpg, bottom.jpg, silkscreen.jpg → `.planning/v1.7/photos/rev-2-0/`; upgrade row state; fill verbatim silkscreen + photo_dir
3. **Photograph Modified Rev 0 board:** top.jpg, bottom.jpg, silkscreen.jpg + rework-N-region.jpg macros → `.planning/v1.7/photos/rev-0-modified/`; upgrade row state; fill verbatim silkscreen + photo_dir
4. **Write full MODIFICATIONS.md:** replace stub with per-region `## Rework Region N` headings + `Cross-ref:` lines tracing each rework against `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch` (blob d2a7f691 on origin/rev2.0)
5. **Investigate R41 discrepancy for Rev2.2:** Anders stated "10k version resistor for Rev 2.2" (CHAT-INTEL 2025-04-28) but schematic blob shows 4k7; confirm whether Rev2.2-gerbers.zip (dated 2025-04-28) reflects a physical 10k build that diverged from the schematic. Optionally contact Anders per D-08 exception.

## Deviations from Plan

### Plan-Level Deviations

**1. [Plan-Contract] Task 1 skipped — photos blocked**
- Per orchestrator directive and Plan 31-05 resume-signal contract
- All 3 operator boards: state=upstream-only, photo_dir=—, silkscreen=not-recovered
- Phase 35 follow-up flagged (canonical handoff)
- No JPGs created, no operator wait, no fake files

No other deviations. Plan executed exactly within the blocked-photos branch of the resume-signal contract.

## Threat Flags

None. This plan creates only documentation files. No network endpoints, auth paths, file access patterns, or schema changes at trust boundaries.

## Task Commits

1. **Task 1:** SKIPPED (blocked — no photos)
2. **Task 2: Write MODIFICATIONS.md stub** — `67d518c`
3. **Task 3: Fill §1 + §2 + §3 in SHIELD-REVS.md** — `387f000`
4. **Task 4: Phase-gate checks** — verification-only, no commit

## Self-Check: PASSED

Files verified:
- `.planning/v1.7/MODIFICATIONS.md` — EXISTS (commit 67d518c)
- `.planning/v1.7-SHIELD-REVS.md` — EXISTS (commit 387f000)
- `.planning/phases/31-upstream-shield-archaeology/31-05-SUMMARY.md` — this file

Commits verified:
- `67d518c` — EXISTS (docs(31-05): write stub MODIFICATIONS.md)
- `387f000` — EXISTS (docs(31-05): fill §1 inventory + §2 appendix + §3 R41 table)

Phase-gate re-verified:
- Inventory rows: 8 (expected ≥ 3)
- §3 rows: 4 (expected ≥ 2)
- All 8 phase-gate checks: PASS

No fake JPGs created. No STATE.md / ROADMAP.md changes. No firestarter/ or firestarter_app/ changes.

---
phase: 31-upstream-shield-archaeology
plan: "04"
subsystem: hardware-archaeology
tags: [rurp-shield, git-mine, kicad, v1.7, scaffold]

requires:
  - "31-01: upstream-rurp clone staged at .planning/v1.7/upstream-rurp/"

provides:
  - ".planning/phases/31-upstream-shield-archaeology/mine-notes.md — 5-pass git mine raw output with R41/JP4/A3 per-rev extractions for Plan 05 §3 fill"
  - ".planning/v1.7-SHIELD-REVS.md — full §1-§9 scaffold with D-10 column header + OWNED-BY markers on §4-§9"

affects:
  - 31-05-modified-rev0-and-fills (consumes mine-notes.md for §1/§3 row fill)
  - 32-* (§4-§5-§6 fill; reads scaffold structure)
  - 33-* (§7 fill; reads scaffold + mine-notes R41 data)
  - 34-* (§8-§9 fill; consumes R41 value table from mine-notes)

tech-stack:
  added: []
  patterns:
    - "5-pass git history mine pattern: main log + tag enumeration + diff-filter=D deletions + rev-named branches + all-refs fallback"
    - "kicad_sch s-expression grep for component reference/value extraction"
    - "gerber zip unzip-l listing for archive content inventory"
    - "multi-phase document scaffold with OWNED-BY comment markers per section"
    - "D-10 9-column inventory schema locked at Plan 04 with empty scaffold"

key-files:
  created:
    - ".planning/phases/31-upstream-shield-archaeology/mine-notes.md (583 lines — 5 passes, 5 zip listings, per-rev R41/JP4/A3 greps, findings summary table)"
    - ".planning/v1.7-SHIELD-REVS.md (55 lines — §1-§9 skeleton, D-10 header, OWNED-BY markers §4-§9)"
  modified: []

key-decisions:
  - "Re-cloned upstream RURP after ephemeral worktree cleanup: Plan 01's clone ran in a worktree that was since deleted; upstream-rurp dir existed but was empty. Re-cloned from same URL; HEAD SHA matches Plan 01 record (9178d84)."
  - "R41 introduction was Rev2 (Oct 2024), not Rev2.1 as CHAT-INTEL stated: git evidence from a252e39 places R41 in schematic 2 months before Rev2.1 commit (50a6ea4 Dec 2024)"
  - "R41 discrepancy flagged: CHAT says 10k for Rev2.2, schematic shows 4k7; 10k only appears in Rev2.3 schematic (c2bd111); Plan 05 §3 must resolve"
  - "No Rev2.2 branch or standalone schematic: Rev2.2 captured only as gerber archive; schematic blob identical to Rev2.1"
  - "Rev2.3 is NOT silkscreen-only vs Rev2.2: R41 4k7→10k AND JP4 footprint 1x2→2x2"

requirements-completed: [HW-INV-01, HW-INV-02]

duration: ~25min
completed: "2026-05-22"
---

# Phase 31 Plan 04: Mine and Scaffold Summary

**Upstream RURP git history mined (5 passes, 5 zip listings, per-rev R41/JP4/A3 extractions); v1.7-SHIELD-REVS.md §1-§9 scaffold committed with D-10 column header locked and OWNED-BY markers on §4-§9**

## Performance

- **Duration:** ~25 min
- **Started:** ~2026-05-22T13:37Z
- **Completed:** 2026-05-22T13:59Z
- **Tasks:** 2
- **Files created:** 2 (mine-notes.md, v1.7-SHIELD-REVS.md)

## Accomplishments

### Task 1: Upstream git history mined into mine-notes.md

All 5 passes from Research Finding #1 executed against `.planning/v1.7/upstream-rurp/`:

- **Pass 1:** `hardware/` log on main — 23 commits spanning 2024-03-15 to 2025-11-28; per-subdir introductions captured (Rev2.1: `50a6ea4`, Rev2.2+Rev2.3 both: `c2bd111`, rev2: `28e0239`)
- **Pass 2:** Zero tags — upstream uses branch-based versioning only (no semver tags)
- **Pass 3:** Two deletion commits — `c2bd111` removed Rev0/Rev1 zips from main root; `28e0239` removed Rev2 CSV/zip from hardware/ root
- **Pass 4:** Three rev-named branches: `origin/rev2.0`, `origin/Rev2.1`, `origin/Rev2.3`; full `ls-tree -r` for each
- **Pass 5:** All-refs walk confirms no hidden commits outside the three branches

Five zip archives listed with `unzip -l`:
- `UniversalProgrammerRev0b0.zip` — gerbers only (2024-04-07), no `.kicad_sch` in zip
- `UniversalProgrammerRev1b0.zip` — gerbers only (2024-04-30), no `.kicad_sch` in zip
- `rev2-1316.zip` — Rev2 gerbers (2024-10-11), no `.kicad_sch` in zip
- `RURP-Rev2.1.zip` — Rev2.1 gerbers (2024-12-02), no `.kicad_sch` in zip
- `Rev2.2-gerbers.zip` — Rev2.2 gerbers (2025-04-28), no `.kicad_sch` in zip

Per-rev R41/JP4/A3 extracted from `.kicad_sch` git blobs:

| Rev | Branch source | Schematic blob | R41 value | JP4 value | A3 net |
|-----|--------------|----------------|-----------|-----------|--------|
| Rev2.0 working | origin/rev2.0 | d2a7f691 | 4k7 (4.7kΩ) | P1_VPP_JMP | present |
| Rev2.1 | origin/Rev2.1 | f3b7a521 | 4k7 (4.7kΩ) | P1_VPP_JMP | present |
| Rev2.2 | main at b0ec7d7 | f3b7a521 (same blob as Rev2.1) | 4k7 (4.7kΩ) | P1_VPP_JMP | present |
| Rev2.3 | origin/Rev2.3 + main | fe35bd78 | **10k (10kΩ)** | P1_VPP_JMP | present |

### Task 2: v1.7-SHIELD-REVS.md scaffold committed

`.planning/v1.7-SHIELD-REVS.md` at `.planning/` root (outside `.planning/v1.7/`, so NOT gitignored):

- §1 Inventory: D-10 9-column header locked (`| silkscreen | provenance | state | introduced_commit | removed_commit | schematic_path | gerber_path | photo_dir | notes |`), no rows
- §2 Mentioned-but-not-recovered: 4-column header, no rows
- §3 Existing Detect-HW Scheme: 5-column table for R41/JP4/A3 per-rev data, no rows
- §4 Inter-Rev Electrical Differences: `<!-- OWNED BY PHASE 32 — TBD -->`
- §5 Inter-Rev Mechanical Differences: `<!-- OWNED BY PHASE 32 — TBD -->`
- §6 Per-Rev Capability Matrix: `<!-- OWNED BY PHASE 32 — TBD -->`
- §7 Silkscreen → Code Alias Table: `<!-- OWNED BY PHASE 33 — TBD -->`
- §8 Detect-HW Schematic Delta: `<!-- OWNED BY PHASE 34 — TBD -->`
- §9 Per-Rev Expected ADC Band Table: `<!-- OWNED BY PHASE 34 — TBD -->`

Phase-gate checks #2, #7, #8 pass on empty scaffold (confirmed by python3 + awk scripts).

## Findings Summary Table (for Plan 05 §1 inventory fill)

The mine surfaced the following per-rev data. Plan 05 will fill §1 rows using this table,
supplemented by operator photo sessions (Plans 03 + 05) for the `silkscreen` column.

| Rev | Provenance | State | Introduced commit | Removed commit | Schematic path | Gerber path | Notes |
|-----|------------|-------|-------------------|----------------|----------------|-------------|-------|
| (silkscreen: plan 05 photos) | on-main | upstream-only | c2bd111 (2025-06-24) | — | `hardware/RelativelyUniversalROMProgrammer.kicad_sch` (blob fe35bd78) | `hardware/Rev2.3/jlcpcb/production_files/GERBER-RelativelyUniversalROMProgrammer.zip` | Rev2.3; R41=10k; JP4 changed to 2x2 header; renamed sch file; plan 03 photos needed |
| (silkscreen: plan 03 photos) | on-main | on-hand-photographed | c2bd111 (2025-06-24) | — | blob f3b7a521 (= Rev2.1 blob; no standalone Rev2.2 sch) | `hardware/Rev2.2/Rev2.2-gerbers.zip` (gerber date 2025-04-28) | Rev2.2; schematic unchanged from Rev2.1; R41=4k7 in schematic (DISCREPANCY — see below) |
| (silkscreen: plan 03 photos) | on-main | on-hand-photographed | 50a6ea4 (2024-12-20) | — | `hardware/W27C512Programmer.kicad_sch` (blob f3b7a521) on origin/Rev2.1 | `hardware/Rev2.1/RURP-Rev2.1.zip` | Rev2.1; R41=4k7; JP4=P1_VPP_JMP (1x2 header); first rev with Rev2.1/ subdir |
| not-recovered | on-main (hardware/rev2/) | upstream-only | 28e0239 (2024-10-17) | — | inside `hardware/rev2/rev2-1316.zip` (gerbers only, 2024-10-11) | `hardware/rev2/rev2-1316.zip` | Pre-Rev2.1 "rev2" lowercase dump; deprecated; R41 already in schematic at a252e39 (Oct 2024) |
| not-recovered | branch-archived: origin/rev2.0 (removed from main c2bd111) | upstream-only | b84e9e0 (2024-04-30) | c2bd111 (2025-06-24) | `UniversalProgrammerRev1b0.zip` (gerbers only) | `hardware/UniversalProgrammerRev1b0.zip` (blob 82a425d4) | Rev1; voltage divider on A2 (not A3); R41 NOT present; gerbers only |
| not-recovered | branch-archived: origin/rev2.0 (removed from main c2bd111) | upstream-only | 486f3d1 (2024-04-18) | c2bd111 (2025-06-24) | `UniversalProgrammerRev0b0.zip` (gerbers only — no sch in zip); schematic = W27C512Programmer.kicad_sch on origin/rev2.0 (blob d2a7f691) | `hardware/UniversalProgrammerRev0b0.zip` (blob 884ccf9f) | Rev0; gerbers only in zip; schematic separately accessible via git blob on rev2.0 branch |
| (silkscreen: plan 05 photos) | n/a — operator derived from Rev0 | on-hand-photographed | n/a | — | cross-refs to Rev0 schematic (blob d2a7f691) + UniversalProgrammerRev0b0.zip | n/a | Modified Rev0; operator's third board; rework traced in Plan 05 MODIFICATIONS.md |

## Per-Rev R41 / JP4 / A3 Extraction Results (for Plan 05 §3 fill)

### Schematic file paths and blob SHAs

| Rev | Git source | Schematic path | Blob SHA | Lines |
|-----|-----------|----------------|----------|-------|
| Rev2.0 working | `git show origin/rev2.0:hardware/W27C512Programmer.kicad_sch` | `hardware/W27C512Programmer.kicad_sch` | d2a7f691 | 25,552 |
| Rev2.1 | `git show origin/Rev2.1:hardware/W27C512Programmer.kicad_sch` | `hardware/W27C512Programmer.kicad_sch` | f3b7a521 | 26,675 |
| Rev2.2 | `git show b0ec7d7:hardware/W27C512Programmer.kicad_sch` (parent of Rev2.3 commit) | `hardware/W27C512Programmer.kicad_sch` | f3b7a521 (= Rev2.1) | 26,675 |
| Rev2.3 | `git show origin/Rev2.3:hardware/RelativelyUniversalROMProgrammer.kicad_sch` | `hardware/RelativelyUniversalROMProgrammer.kicad_sch` | fe35bd78 | 28,007 |

### R41 values by line number

| Rev | R41 reference line | R41 value line | Value |
|-----|--------------------|----------------|-------|
| Rev2.0 | 17520 | 17528 | `4k7` |
| Rev2.1 | 18232 | 18240 | `4k7` |
| Rev2.2 | 18232 | 18240 | `4k7` (same blob as Rev2.1) |
| Rev2.3 | 20582 | 20591 | `10k` |

### JP4 values by line number

| Rev | JP4 reference line | JP4 value | JP4 footprint |
|-----|-------------------|-----------|---------------|
| Rev2.0 | 21311 | `P1_VPP_JMP` | `PinHeader_1x02_P2.54mm_Vertical` |
| Rev2.1 | 22300 | `P1_VPP_JMP` | `PinHeader_1x02_P2.54mm_Vertical` |
| Rev2.2 | 22300 | `P1_VPP_JMP` | `PinHeader_1x02_P2.54mm_Vertical` (same blob) |
| Rev2.3 | 22562 | `P1_VPP_JMP` | `PinHeader_2x02_P2.54mm_Vertical` (CHANGED — 2x2 vs 1x2) |

### A3 net label lines

All four schematics (Rev2.0 through Rev2.3) carry the `A3` label at two locations in the schematic:
one on the Arduino A3 pin connection to the R41 voltage divider, one on the address bus (A3 EPROM
address line). ADC pin A3 is confirmed in all four schematic revisions.

## Status of Rev 2.1 Schematic Recovery

**FOUND.** Rev 2.1 schematic is accessible as blob `f3b7a521` at:
```
git -C .planning/v1.7/upstream-rurp show origin/Rev2.1:hardware/W27C512Programmer.kicad_sch
```
The schematic is NOT inside the `RURP-Rev2.1.zip` archive (which contains only gerbers).
It is a tracked git object on the `origin/Rev2.1` branch.

## Status of `rev2/` (lowercase) on main

The `hardware/rev2/` directory on main contains only `rev2-1316.zip` (gerbers, 2024-10-11) +
two CSV BOM files. No `.kicad_sch` is committed to this subdir. The "rev2" lowercase designation
is a pre-Rev2.1 deprecated dump — the schematic for this era was `hardware/W27C512Programmer.kicad_sch`
tracked at the `hardware/` root level (before the Rev2.1 subdir was introduced). The `rev2-1316.zip`
file is present on four branches: main, rev2.0, Rev2.1, Rev2.3. State = upstream-only.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking Issue] Upstream RURP clone missing (empty directory)**
- **Found during:** Task 1 start
- **Issue:** `/workspaces/.planning/v1.7/upstream-rurp/` existed as an empty directory. Plan 01
  populated the clone in an ephemeral worktree (worktree-agent-a6e1a1c5e9b610f5b) that was cleaned
  up after merge. The gitignored clone did not persist to the main worktree filesystem.
- **Fix:** Re-cloned from the same upstream URL (`https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer`). Verified HEAD SHA matches Plan 01's recorded SHA (`9178d8419e5f651a3e23ad040da16cb4f8c14269`), confirming upstream state unchanged.
- **Impact:** Zero — clone is gitignored; content is identical to what Plan 01 recorded.
- **Files modified:** None committed (gitignored content).
- **Commit:** N/A (gitignored)

## Key Discrepancies Flagged for Plan 05

### Discrepancy 1: R41 value in Rev2.2 — CHAT vs schematic
- **CHAT-INTEL §1** (Anders, 2025-04-28): "10k version resistor for Rev 2.2"
- **Schematic evidence:** Rev2.2 schematic blob (f3b7a521) shows R41 = 4k7. The 10k value
  first appears in Rev2.3 schematic (blob fe35bd78, introduced c2bd111 2025-06-24).
- **Action for Plan 05 §3:** Flag this discrepancy explicitly. Possible explanations: (a) Anders's
  gerbers for Rev2.2 had the 10k physically populated but the KiCad schematic was not updated;
  (b) the "10k" comment referred to a planned change that shipped in Rev2.3.

### Discrepancy 2: R41 introduction claim — CHAT says Rev2.1, git says Rev2 (Oct 2024)
- **CHAT-INTEL §1** (Anders, 2024-10-07, per CONTEXT): "Say hello to R41 on A3"
- **Git evidence:** R41 appears in commit `a252e39` (2024-10-08, "Rev2") — 2 months before
  the Rev2.1 introduction commit `50a6ea4` (2024-12-20).
- **Note:** The CHAT-INTEL date (2024-10-07) and the commit date (2024-10-08) are adjacent,
  suggesting Anders introduced R41 in the Rev2 working schematic around the same time as the
  Discord announcement. The "Rev2.1" attribution in CONTEXT may refer to the first formally
  released gerber set for that schematic, not the first schematic commit.

### Discrepancy 3: Rev2.3 is NOT silkscreen-only vs Rev2.2
- **CHAT-INTEL** (Anders, 2026-07-03 per CONTEXT): "only silkscreen difference" for Rev2.3
- **Schematic evidence:** R41 value changed (4k7 → 10k) AND JP4 footprint changed
  (PinHeader_1x02 → PinHeader_2x02). These are substantive electrical/mechanical changes.
- **Action for Phase 32:** The inter-rev diff matrix must capture both the R41 value change
  and the JP4 footprint change under §4 (Electrical) and §5 (Mechanical).

## Threat Flags

None. This plan creates only documentation/scratch files. No network endpoints, auth paths,
file access patterns, or schema changes at trust boundaries.

## Self-Check

- [x] `mine-notes.md` exists at `.planning/phases/31-upstream-shield-archaeology/mine-notes.md` — 583 lines
- [x] `v1.7-SHIELD-REVS.md` exists at `.planning/v1.7-SHIELD-REVS.md` — 55 lines
- [x] mine-notes contains `## Pass 1` through `## Pass 5` (5 sections)
- [x] mine-notes contains `## Zip-archive listings`, `## Per-rev R41`, `## Findings summary`
- [x] mine-notes references Rev2.1 and rev2.0 branch identifiers
- [x] shield-revs contains verbatim D-10 column header
- [x] shield-revs contains all 9 `## N.` section headers
- [x] §4-§9 each carry `<!-- OWNED BY PHASE NN — TBD -->` marker with em-dash within 5 lines
- [x] §1-§3 contain NO `OWNED BY PHASE` marker
- [x] `git check-ignore -q .planning/v1.7-SHIELD-REVS.md` returns non-zero (not gitignored)
- [x] Rev 2.1 schematic FOUND (blob f3b7a521 on origin/Rev2.1 branch) — CONTEXT "must be found" requirement satisfied
- [x] Commits: aa8652b (mine-notes), f1e41e3 (shield-revs scaffold)

## Self-Check: PASSED

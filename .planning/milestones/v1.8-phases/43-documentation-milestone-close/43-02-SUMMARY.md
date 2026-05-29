---
phase: 43-documentation-milestone-close
plan: "02"
subsystem: planning-meta
tags: [milestone-close, archive, roadmap-collapse, requirements-archive, v1.8]
dependency_graph:
  requires: [43-01]
  provides: [v1.8-archive, v1.8-roadmap-collapsed, v1.8-requirements-archive]
  affects: [.planning/phases/, .planning/milestones/v1.8-phases/, .planning/ROADMAP.md, .planning/milestones/v1.8-REQUIREMENTS.md]
tech_stack:
  added: []
  patterns: [archive-script-pattern, details-block-roadmap-collapse, requirements-archive]
key_files:
  created:
    - .planning/v1.8-archive.sh
    - .planning/milestones/v1.8-REQUIREMENTS.md
    - .planning/milestones/v1.8-phases/ (8 phase dirs archived)
    - .planning/milestones/v1.8-phases/43-documentation-milestone-close/43-02-SUMMARY.md
  modified:
    - .planning/ROADMAP.md
decisions:
  - D-07: v1.8-archive.sh mirrors v1.6-archive.sh verbatim with phase numbers 36-43
  - D-05: ROADMAP.md v1.8 section collapsed to <details> shipped-archive block
  - D-06: v1.8-REQUIREMENTS.md created with 30-row table + per-requirement disposition; live REQUIREMENTS.md left in place
metrics:
  duration: ~10 minutes
  completed: 2026-05-29
  tasks: 2
  files: 4 artifacts (1 script + 8 phase dirs archived + 1 requirements file + 1 ROADMAP edit)
---

# Phase 43 Plan 02: Archive + ROADMAP Collapse + REQUIREMENTS Archive Summary

**One-liner:** v1.8 phase directories (36-43) archived to milestones/v1.8-phases/, ROADMAP.md v1.8 section collapsed to 17-line <details> block (was 301 lines), and v1.8-REQUIREMENTS.md created with 30-row disposition table.

## What Was Built

### Artifact 1: `.planning/v1.8-archive.sh`

Verbatim mirror of `.planning/v1.6-archive.sh` with the documented substitutions per D-07:
- Phase range 26-30 → 36-43 (8-entry PHASE_GLOBS array; explicit per-phase enumeration, NOT a shorthand glob)
- Destination `milestones/v1.6-phases` → `milestones/v1.8-phases`
- Header banner updated (v1.6 → v1.8; T-30-03 reference → T-43-12)
- Next-Steps footer re-aimed at Plan 43-03 (operator-authorized HUMAN-UAT)
- All structural elements byte-identical to v1.6-archive.sh: `set -euo pipefail`, argument parsing, path computation, SRC_DIRS collector, pre-flight checks, dry-run branch, live-mv branch, exit codes 0/1/2

Dry-run verified 8 planned moves before live run. Syntax check (`bash -n`) passed.

### Artifact 2: `.planning/milestones/v1.8-phases/` (8 phase directories)

Archive destination populated by the live run of `v1.8-archive.sh`. All 8 v1.8 phase directories moved from `.planning/phases/` to `.planning/milestones/v1.8-phases/`:
- `36-characterization-test-baseline`
- `37-tooling-baseline-ci-gate`
- `38-low-risk-extractions`
- `39-database-cleanup-chip-resolver`
- `40-serial-transport-restructure`
- `41-cli-migration-argparse-click`
- `42-error-handling-normalization-quality-sweep`
- `43-documentation-milestone-close` (this plan's own directory — self-archive pattern)

This plan's own phase directory was archived mid-flight; SUMMARY.md is written at the POST-archive path (`.planning/milestones/v1.8-phases/43-documentation-milestone-close/43-02-SUMMARY.md`). Mirrors the v1.6 Plan 30-02 self-archive pattern.

### Artifact 3: `.planning/milestones/v1.8-REQUIREMENTS.md`

New 136-line requirements archive modeled on `.planning/milestones/v1.6-REQUIREMENTS.md`. Contains:
- H1 header + Status + Disposition paragraph
- Milestone goal (verbatim from ROADMAP.md)
- Actual ship outcome (including BUG-1/BUG-2 commit SHAs, coverage 70.12%, ship tag `3.0.0b7`)
- 9 category sections (TEST/TOOL/STRUCT/DATA/SERIAL/CLI/ERR/DOC/MS) with per-requirement checkbox + narrative
- 30-row Traceability table (REQ-ID | Phase | Disposition | Notes)
- Out of Scope section
- Carry-forward to v1.9 section (Bug A + Bug B + `eprom_operations.py` mypy deferred + 3 pending todos + v1.9 substrate pointers)

Disposition: 27 DELIVERED (TEST-01..05 + TOOL-01..03 + STRUCT-01..05 + DATA-01..04 + SERIAL-01..03 + CLI-01..04 + ERR-01..03); 3 VERIFIED-AT-CLOSE (DOC-01 + DOC-02 + MS-01).

### Artifact 4: `.planning/ROADMAP.md` (v1.8 section collapsed)

v1.8 section (formerly lines 15-315, ~301 lines) replaced with a 17-line `<details>` shipped-archive block:
- New heading: `## v1.8 — Host CLI Structural Cleanup (firestarter_app) (SHIPPED <TBD-from-43-03>)`
- `<details>` block mirrors v1.5/v1.6/v1.7 collapsed shape
- Contains ship tag, 8-phase checklist, branch model, v1.9 hand-off with GATE-1.8d ring-fence note
- Cross-links to `.planning/MILESTONES.md` §v1.8, `.planning/milestones/v1.8-REQUIREMENTS.md`, `.planning/milestones/v1.8-phases/`
- `<TBD-from-43-03>` placeholder preserved (NOT pre-emptively substituted — Plan 43-03 Step 5 substitutes at operator-UAT time)

The 30-row v1.8 Coverage table was EXTRACTED (not lost) to `v1.8-REQUIREMENTS.md` with the per-requirement disposition column added.

## Verification Results

All post-execution checks passed:

- `bash .planning/v1.8-archive.sh` printed `Archived 8 phase director(ies) to .planning/milestones/v1.8-phases/`
- All 8 source dirs gone from `.planning/phases/`; all 8 destination dirs exist under `.planning/milestones/v1.8-phases/`
- Paused v1.3 dirs (`11-*`, `12-*`) untouched (T-43-12 + T-43-14 mitigation confirmed)
- Prior milestone archives (v1.6) untouched
- `v1.8-REQUIREMENTS.md` 136 lines (≥ 35 gate); all 30 REQ-IDs present; Bug A + Bug B + commit SHAs cited
- ROADMAP.md: SHIPPED heading exists (1); STARTED heading gone (0); Coverage table gone (0); Phase 36/43 detail blocks gone (0); v1.5/v1.6/v1.7 sections preserved (1 each); `<details>` block present
- Live `.planning/REQUIREMENTS.md` still IS the v1.8 file (per `head -1` check); left in place per D-06 execution-time inspection

## Subtask 2D: Live REQUIREMENTS.md Reconciliation

Verified: `head -1 .planning/REQUIREMENTS.md` reads `# Requirements: Firestarter v1.8 — Host CLI Structural Cleanup (firestarter_app)`.

Per D-06: the live file IS the v1.8 file at archive time. Leave-in-place choice applied (mirrors v1.6 Plan 30-02 reconciliation pattern). Deletion deferred to `/gsd-new-milestone v1.9` which will overwrite it.

## Safety Notes

- **T-43-12 (paused v1.3 tampering) mitigated:** `v1.8-archive.sh` uses explicit 8-entry PHASE_GLOBS array (36-* through 43-*); post-run verified `11-*` and `12-*` still present
- **T-43-13 (GATE-1.8d ring-fence signal loss) mitigated:** Collapsed ROADMAP block contains phrase "GATE-1.8d ring-fence intact" + names Bug A + Bug B carry-forward + 15-binary substrate path
- **T-43-14 (v1.3 accidental capture) mitigated:** Same as T-43-12
- **T-43-15 (VERIFIED-AT-CLOSE disposition omission) mitigated:** 30-row traceability table explicitly maps DOC-01 → Phase 43 Plan 43-01, DOC-02 → Phase 43 Plans 43-01+43-02, MS-01 → Phase 43 Plan 43-03
- **T-43-16 (live REQUIREMENTS.md accidental deletion) mitigated:** Subtask 2D was verify-only; confirmed file still IS the v1.8 file post-execution
- **T-43-18 (placeholder pre-substitution) mitigated:** `<TBD-from-43-03>` tokens present verbatim in ROADMAP.md collapsed block and v1.8-REQUIREMENTS.md Status line

## Next Plan

**Plan 43-03** (operator-authorized HUMAN-UAT) is now unblocked. The HUMAN-UAT.md will be created by Plan 43-03 at the POST-archive path:
`.planning/milestones/v1.8-phases/43-documentation-milestone-close/43-HUMAN-UAT.md`

Plan 43-03 6-step checklist:
- Step 0: Real-hardware GATE-1.8a witness (`firestarter read -e W27C512` on Modified Rev 0 + Leonardo; byte-identical against `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`)
- Steps 1-4: Branch identity verification + firestarter_app merge + ship tag `3.0.0b7` + firmware no-op verify + meta-repo merge
- Step 5: STATE.md flip + `<TBD-from-43-03>` token substitution in MILESTONES.md

## Deviations from Plan

None — plan executed exactly as written. The v1.7-phases directory not existing under `.planning/milestones/` was expected (v1.7 archived differently; no v1.7 phase dirs existed to begin with); the key safety check — v1.6 archive and paused v1.3 dirs untouched — passed.

## Self-Check: PASSED

- [x] `.planning/v1.8-archive.sh` exists and is executable
- [x] `.planning/milestones/v1.8-phases/` contains all 8 phase dirs
- [x] `.planning/milestones/v1.8-REQUIREMENTS.md` exists (136 lines)
- [x] `.planning/ROADMAP.md` v1.8 SHIPPED heading present; STARTED/Coverage/PhaseDetail blocks absent
- [x] Paused v1.3 dirs (11-*, 12-*) untouched
- [x] Live `.planning/REQUIREMENTS.md` IS the v1.8 file (left in place per D-06)
- [x] SUMMARY.md at post-archive path: `.planning/milestones/v1.8-phases/43-documentation-milestone-close/43-02-SUMMARY.md`

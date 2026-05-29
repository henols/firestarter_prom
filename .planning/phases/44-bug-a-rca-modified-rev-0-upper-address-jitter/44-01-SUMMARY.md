---
phase: 44-bug-a-rca-modified-rev-0-upper-address-jitter
plan: 01
subsystem: infra
tags: [git, branching, firmware, v1.9, shield-revisions, rca]

# Dependency graph
requires:
  - phase: v1.7-shield-investigation
    provides: v1.7-SHIELD-REVS.md with 9-section investigation-canonical shield mod record
  - phase: beta (firestarter sub-repo)
    provides: v1.7 shield-detect plumbing and doc/SHIELD-REVISIONS.md on the firmware working tree
provides:
  - v1.9-read-bug-rca branches in both firestarter/ and firestarter_app/ submodules, forked off beta
  - .planning/v1.7-SHIELD-REVS.md recovered verbatim on the meta working tree (static-check substrate for D-01/D-02)
affects:
  - 44-02-PLAN (firmware dev param extension — reads from the now-accessible firestarter working tree)
  - 44-03-PLAN (host CLI knob extension — on the now-accessible firestarter_app working tree)
  - 44-04-PLAN (static check D-01 / D-02 — reads .planning/v1.7-SHIELD-REVS.md)
  - 44-05-PLAN (per-rev failure map — needs both shield docs)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Branch naming: v1.9-read-bug-rca in sub-repos forked off beta (not off stale submodule detach point)"
    - "Shield-rev docs: meta investigation-canonical (.planning/v1.7-SHIELD-REVS.md) + sub-repo operator-canonical (firestarter/doc/SHIELD-REVISIONS.md) kept in lockstep"

key-files:
  created:
    - .planning/v1.7-SHIELD-REVS.md — investigation-canonical 9-section shield revision reference (verbatim recovery from v1.7-shield-investigation branch)
  modified: []

key-decisions:
  - "Forked v1.9-read-bug-rca off beta (not efd203a) in firestarter/ to carry v1.7 shield-detect plumbing and doc/SHIELD-REVISIONS.md"
  - "Forked v1.9-read-bug-rca off beta tip (4f04d98) in firestarter_app/ before any host-side knob work"
  - "Recovered v1.7-SHIELD-REVS.md verbatim via git show v1.7-shield-investigation — no content edits"
  - "Did NOT commit submodule pointer bumps to meta-repo (plan instructions explicit: record branch tips in SUMMARY, not in git pointer)"

patterns-established:
  - "Pitfall 1 guard: always verify doc/SHIELD-REVISIONS.md exists post-fork as proof of beta-descendant branch"

requirements-completed: [RCA-03]

# Metrics
duration: 8min
completed: 2026-05-29
---

# Phase 44 Plan 01: Working Tree Initialization Summary

**v1.9-read-bug-rca branches forked off beta in both sub-repos (firestarter@8fead2d, firestarter_app@4f04d98), with .planning/v1.7-SHIELD-REVS.md (9-section, 222 lines) recovered from v1.7-shield-investigation branch — static-check substrate for D-01/D-02 now present on meta working tree**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-05-29T13:19:54Z
- **Completed:** 2026-05-29T13:22:41Z
- **Tasks:** 2
- **Files modified:** 1 (created: .planning/v1.7-SHIELD-REVS.md)

## Accomplishments

- Both sub-repos switched from detached HEAD (efd203a / aaa45e0) to v1.9-read-bug-rca branch forked off beta tip — carries v1.7 shield-detect plumbing, doc/SHIELD-REVISIONS.md, and v1.8 app cleanup
- firestarter/doc/SHIELD-REVISIONS.md confirmed present and contains "Modified Rev 0" (Pitfall 1 guard passed)
- .planning/v1.7-SHIELD-REVS.md recovered verbatim (222 lines, 15 ## headings, 9 sections including §6 capability matrix and §9 ADC band table) — static-check reference for Plans 04/05 is on the working tree

## Branch Tip SHAs

| Sub-repo | Forked from | v1.9 branch tip SHA |
|----------|-------------|---------------------|
| firestarter/ | beta | 8fead2dfe6af159a38804e1360cdf15fd69686fb |
| firestarter_app/ | beta | 4f04d98f355404fa34bdef0311f879fa70c3d920 |

Note: submodule pointers in the meta-repo were NOT committed (plan-explicit: operator controls pointer bump timing).

## Task Commits

Each task was committed atomically:

1. **Task 1: Fork v1.9-read-bug-rca off beta in both sub-repos** — sub-repo branch operations only; no meta-repo commit (per plan instructions)
2. **Task 2: Recover investigation-canonical v1.7-SHIELD-REVS.md** - `0bb8f5c` (feat)

## Files Created/Modified

- `.planning/v1.7-SHIELD-REVS.md` — Investigation-canonical 9-section shield revision reference recovered verbatim from `v1.7-shield-investigation` branch. Contains: §1 inventory, §2 mentioned-but-not-recovered, §3 R41-on-A3 detect scheme, §4 inter-rev electrical differences (including Modified Rev 0 TBD row), §5 mechanical differences, §6 per-rev capability matrix, §7 silkscreen → code alias table, §8 Detect-HW schematic delta, §9 per-rev expected ADC band table.

## Decisions Made

- Forked firestarter off `origin/beta` (not local `beta`) since the submodule had no local beta tracking branch; `git checkout origin/beta -b v1.9-read-bug-rca` correctly sets up tracking.
- Recovered v1.7-SHIELD-REVS.md via `git show v1.7-shield-investigation:.planning/v1.7-SHIELD-REVS.md` — the `v1.7-shield-investigation` ref was available locally (no fetch needed).
- Submodule pointer bumps NOT committed to meta-repo per the plan's explicit instruction and the submodule_branch_warning in the execution context.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None. Both sub-repos transitioned cleanly from detached HEAD to the new v1.9 branch. The firestarter submodule used `origin/beta` (not a local beta branch) since the submodule only had `origin/beta` as a remote-tracking branch at that point — this is the correct equivalent of "git checkout beta" per the plan's intent.

## Threat Surface Scan

No new network endpoints, auth paths, or schema changes introduced. This plan is pure local git branch operations + file recovery. T-44-01-GP (Tampering: branch fork point) — MITIGATED: `doc/SHIELD-REVISIONS.md` present and verified post-fork.

## Next Phase Readiness

- firestarter/ working tree is on v1.9-read-bug-rca forked off beta — ready for firmware dev param extension (Plan 44-02)
- firestarter_app/ working tree is on v1.9-read-bug-rca forked off beta — ready for host CLI knob extension (Plan 44-03)
- .planning/v1.7-SHIELD-REVS.md present — ready for static check D-01/D-02 (Plan 44-04)
- firestarter/doc/SHIELD-REVISIONS.md present — operator-canonical shield doc available for bench reference
- **No blockers** for Plans 44-02 through 44-05

---
*Phase: 44-bug-a-rca-modified-rev-0-upper-address-jitter*
*Completed: 2026-05-29*

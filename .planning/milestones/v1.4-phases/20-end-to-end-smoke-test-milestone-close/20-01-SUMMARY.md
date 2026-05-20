---
phase: 20-end-to-end-smoke-test-milestone-close
plan: 01
subsystem: planning
tags: [milestone-close, e2e, beta-release, uat, gsd-audit-uat, human-needed, v1.4]

requires:
  - phase: 19-documentation
    provides: v1.4-RELEASE-PROCEDURES.md (operator follows this during E2E cut)
  - phase: 18-beta-aware-firmware-downloader
    provides: firestarter fw -i --pre / --firmware-version / --list flags (tested in HUMAN-UAT tests 5+6)
  - phase: 15-versioning-locked-step-coordination-foundation
    provides: lockstep-dryrun-fixture.sh + PEP 440 BETA_VERSION_RE (reused by verifier script)

provides:
  - Operator checklist (20-HUMAN-UAT.md) with 6 E2E-01 tests covering sub-criteria (a)-(f)
  - Automated post-cut verifier (v1.4-e2e-verify.sh) for PyPI + GitHub Releases API checks
  - Archive script (v1.4-archive.sh) for milestone-close phase-directory cleanup
  - MILESTONES.md v1.4 entry (style-matched to v1.0/v1.2; TBD-on-cut tokens for commit counts)
  - PROJECT.md ship-state update (Active Milestone flipped; v1.3 coherence-pass note added)

affects: [operator-e2e-run, gsd-audit-uat-20, v1.4-milestone-close]

tech-stack:
  added: []
  patterns:
    - "human_needed first-run verdict — UAT checklist with status:partial persists until operator confirms tests"
    - "Automated verifier covers API-checkable sub-criteria; HUMAN-UAT covers install/hardware sub-criteria"
    - "<SHIP_DATE_PLACEHOLDER> and TBD-on-cut tokens for operator to fill at actual milestone close"

key-files:
  created:
    - .planning/phases/20-end-to-end-smoke-test-milestone-close/20-HUMAN-UAT.md
    - .planning/v1.4-e2e-verify.sh
    - .planning/v1.4-archive.sh
  modified:
    - .planning/MILESTONES.md
    - .planning/PROJECT.md

key-decisions:
  - "D-02/D-03: HUMAN-UAT.md status:partial, 6 tests map to E2E-01 sub-criteria (a)-(f) verbatim from REQUIREMENTS.md"
  - "D-04/D-05: verifier covers PyPI API (a), GitHub Releases shape (c), lockstep tag equality (d), optional fw --list (e) in 4 steps"
  - "D-06: sub-criteria (b), (e), (f) are HUMAN-UAT items only — require live install + hardware; not automatable"
  - "D-07: MILESTONES.md v1.4 entry style-matched to v1.0/v1.2 (Delivered/Accomplishments/Stats/Key Decisions/Known Gaps/Debt/HW impact)"
  - "D-08: archive script uses EXPLICIT per-phase glob enumeration 15-* 16-* 17-* 18-* 19-* 20-* (T-20-03 mitigation; no 15-2* shorthand)"
  - "D-09: archive script is operator-run post-E2E, not auto-executed by this plan"
  - "D-10/D-11: PROJECT.md Active Milestone flipped to shipped state with <SHIP_DATE_PLACEHOLDER>; no next-milestone named"
  - "D-12: BETA_VERSION operator-chosen at execution time; 0.0.1b1 recommended for first run"
  - "D-13/D-14: Phase 20 green only when all 6 UAT tests pass + verifier exits 0 + archive run + tokens replaced"
  - "D-15: 7 deferred items enumerated in MILESTONES.md Known Gaps with explicit REQUIREMENTS.md Future Requirements pointers"
  - "D-16/D-17: first-run verdict is human_needed — matches v1.2 Phase 08/09 + v1.3 Phase 12 precedent"
  - "D-18: --quick flag on verifier skips Step 4 (firestarter fw --list --pre, requires local beta install)"
  - "D-19: --dry-run flag on archive script previews mv commands without executing"
  - "D-20: no v1.4 timeline chart in MILESTONES.md (degenerate same-day; not informative)"
  - "Plan-checker warning #1: PROJECT.md v1.3 section now includes coherence-pass note on Phase 18 fw -i --pre / --firmware-version / --list flags as resume-relevant context"

requirements-completed: [E2E-01, MS-01]

duration: ~25min
completed: 2026-05-20
---

# Phase 20, Plan 01: End-to-End Smoke Test + Milestone Close Summary

**Operator checklist (20-HUMAN-UAT.md) + automated verifier (v1.4-e2e-verify.sh) + archive script (v1.4-archive.sh) + MILESTONES.md v1.4 entry + PROJECT.md ship-state flip — Phase 20 substrate complete; E2E acceptance requires operator live cut.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-05-20
- **Completed:** 2026-05-20
- **Tasks:** 2
- **Files modified/created:** 5

## Accomplishments

- Task 1: Created `20-HUMAN-UAT.md` with 6 E2E-01 tests (sub-criteria a-f), YAML frontmatter
  `status: partial`, prerequisites + cut-sequence section, completion criteria, and the
  `human_needed` first-run note (D-02/D-03/D-16/D-17).
- Task 1: Created `v1.4-e2e-verify.sh` — executable post-cut verifier covering PyPI JSON API
  (a), GitHub Releases API (c), lockstep tag equality (d), optional `firestarter fw --list --pre`
  probe (e); `--quick` flag skips Step 4 per D-18; PEP 440 regex validation before any network
  call; exit codes 0/1/2.
- Task 2: Appended v1.4 entry to `MILESTONES.md` above the v1.2 entry — Delivered / Key
  Accomplishments (6 items) / Stats table / Key Decisions table / Known Gaps (7 items with
  REQUIREMENTS.md Future Requirements pointers) / Carry-forward debt / Hardware impact;
  no v1.4 timeline chart (D-20); TBD-on-cut tokens for commit counts.
- Task 2: Created `v1.4-archive.sh` — executable archive script with explicit per-phase glob
  enumeration (T-20-03 mitigation), `--dry-run` flag (D-19), non-empty destination refusal.
- Task 2: Updated `PROJECT.md` — Active Milestone flipped to ship state, Current Milestone
  section collapsed to shipped-state summary, v1.3 section grew Phase-18-aware resume-context
  note (coherence-pass per plan-checker warning #1), Last updated line refreshed; no
  next-milestone named (D-11).

## Task Commits

1. **Task 1: E2E-01 substrate** - `ef12d90` (docs)
2. **Task 2: MS-01 close drafts** - `2d2da5d` (docs)

**Plan metadata (SUMMARY + STATE):** TBD (final commit below)

## Files Created/Modified

- `.planning/phases/20-end-to-end-smoke-test-milestone-close/20-HUMAN-UAT.md` — operator
  checklist, 6 E2E-01 tests, prerequisites + cut sequence, completion criteria, first-run note
- `.planning/v1.4-e2e-verify.sh` — automated post-cut verifier (PyPI + GitHub Releases API +
  lockstep check + optional local fw --list probe); `--quick` + PEP 440 validation
- `.planning/v1.4-archive.sh` — milestone close cleanup; explicit 15-*..20-* enumeration;
  `--dry-run`; refuses non-empty destination
- `.planning/MILESTONES.md` — v1.4 entry inserted above v1.2 entry; full milestone close shape
- `.planning/PROJECT.md` — shipped-state flip; v1.3 coherence-pass note; last-updated refreshed

## Decisions Made

All 20 D-XX decisions from CONTEXT.md were honored. See `key-decisions` in frontmatter above
for the complete mapping. Key items:

- `<SHIP_DATE_PLACEHOLDER>` and `TBD-on-cut` tokens in MILESTONES.md and PROJECT.md are
  operator-fillable at actual milestone close (after all 6 HUMAN-UAT tests pass and the
  verifier exits 0). This matches the v1.0 approach where the milestone entry was written
  at close time.
- Archive script intentionally uses EXPLICIT per-phase glob enumeration (`15-*` `16-*` etc.)
  rather than a single `15-2*` shorthand or `phases/*` wildcard, preventing accidental
  capture of paused v1.3 phase dirs (11-*, 12-*) or any future phases beyond 20.
- verifier `--quick` flag allows CI-style invocation that skips the local `firestarter`
  install requirement (Step 4) while still covering the three API-level sub-criteria (a, c, d).

## First-Run Verdict

**Expected first-run verdict: `human_needed`.** This is NOT a defect.

E2E-01 acceptance requires live operator action: cutting a real beta in both sub-repos,
publishing to PyPI, creating GitHub Pre-releases with `.hex` artifacts, and verifying all
6 sub-criteria including a live `pip install --pre` + firmware install. None of these can
execute in the planning environment.

`gsd-audit-uat 20` will surface pending items in `/gsd-progress` until the operator:
1. Follows `.planning/v1.4-RELEASE-PROCEDURES.md` to cut the beta.
2. Runs `bash .planning/v1.4-e2e-verify.sh <BETA_VERSION>` and gets exit 0.
3. Marks all 6 tests in `20-HUMAN-UAT.md` as `pass`.
4. Updates `<SHIP_DATE_PLACEHOLDER>` and `TBD-on-cut` tokens in MILESTONES.md + PROJECT.md.
5. Runs `bash .planning/v1.4-archive.sh` and commits the phase-directory move.

This matches the established GSD `human_needed` pattern from:
- v1.2 Phase 08/09 — chip-seated W27C512 hardware UAT
- v1.3 Phase 12 — CMOS EPROM bench validation

## Deviations from Plan

None — plan executed exactly as written. All 20 D-XX decisions honored. The coherence-pass
note for PROJECT.md v1.3 section (plan-checker warning #1) was pre-specified in the plan
action for Task 2.

## Known Stubs

None relevant to plan goals. The `<SHIP_DATE_PLACEHOLDER>` and `TBD-on-cut` tokens in
MILESTONES.md and PROJECT.md are INTENTIONAL operator-fillable placeholders (D-13 + plan
spec), not stubs that prevent the plan's goals — the substrate (checklist, verifier, archive
script, milestone draft, PROJECT.md draft) is complete. The operator substitutes real values
at E2E close.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes at
trust boundaries introduced by this plan. The verifier script reads from PyPI/GitHub (both
public HTTPS); the archive script is local-only. Trust model unchanged from CONTEXT.md
threat register.

## Issues Encountered

None.

## Next Phase Readiness

Phase 20 / Plan 01 substrate is complete. The next step is operator-driven:

1. Run `.planning/v1.4-RELEASE-PROCEDURES.md` (Phase 19 deliverable) to cut a live beta.
2. Run `bash .planning/v1.4-e2e-verify.sh <BETA_VERSION>` to get automated green.
3. Walk `20-HUMAN-UAT.md` 6 tests and mark each `pass`.
4. Replace `<SHIP_DATE_PLACEHOLDER>` + `TBD-on-cut` tokens.
5. Run `bash .planning/v1.4-archive.sh` (no `--dry-run`) and commit.
6. Update `20-HUMAN-UAT.md` frontmatter `status: partial` → `status: passed`.

`gsd-audit-uat 20` surfaces remaining items until closure.

## Self-Check: PASSED

| Item | Status |
|------|--------|
| 20-HUMAN-UAT.md | FOUND |
| v1.4-e2e-verify.sh (executable) | FOUND |
| v1.4-archive.sh (executable) | FOUND |
| MILESTONES.md | FOUND |
| PROJECT.md | FOUND |
| Commit ef12d90 (Task 1) | FOUND |
| Commit 2d2da5d (Task 2) | FOUND |

---
*Phase: 20-end-to-end-smoke-test-milestone-close*
*Completed: 2026-05-20*

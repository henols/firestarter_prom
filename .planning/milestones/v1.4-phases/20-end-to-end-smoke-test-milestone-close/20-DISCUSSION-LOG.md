# Phase 20: End-to-End Smoke Test + Milestone Close - Discussion Log

> Audit trail. Decisions in CONTEXT.md.

**Date:** 2026-05-20  
**Mode:** `--auto --chain`

**Critical constraint:** E2E-01 inherently requires LIVE network operations (real `gh workflow run`, real PyPI publish, real `pip install --pre`, real GitHub Pre-release creation). These cannot be executed in the planning environment. Phase 20's planning-side deliverable is the OPERATOR CHECKLIST + AUTOMATED VERIFIER + MILESTONE CLOSE DRAFTS that finalize after operator confirmation.

## Auto-selected decisions (10 gray areas)

| Area | Selection | Rationale |
|------|-----------|-----------|
| A. Plan structure | Single plan, 2 tasks (E2E substrate + close drafts) | Tasks land in single commit window; close drafts wait for operator confirmation via HUMAN-UAT |
| B. HUMAN-UAT.md location | `.planning/phases/20-*/20-HUMAN-UAT.md` | Project convention; surfaces in /gsd-audit-uat |
| C. e2e-verify.sh location | `.planning/v1.4-e2e-verify.sh` (meta-repo) | Operator-runnable from any clone; outlives Phase 20 dir |
| D. MILESTONES.md content | Match v1.0/v1.2/v1.3 style | Consistency with prior milestone entries |
| E. Archive script | `mv .planning/phases/{15..20}-* .planning/milestones/v1.4-phases/` | Mirror v1.2 cleanup |
| F. PROJECT.md update | Active Milestone → ship state; do NOT preemptively name next | Operator picks next milestone after v1.4 ships |
| G. E2E test version | Operator-chosen at execution time (HUMAN-UAT.md gives guidance) | Avoid tag conflicts if Phase 20 takes weeks to execute |
| H. Operator acceptance | All 6 HUMAN-UAT.md tests pass + verifier script green + archive done + PROJECT.md updated | Comprehensive close definition |
| I. Deferred items | Explicit pointers to REQUIREMENTS.md Future Requirements + carry-over from prior phases | Single source of truth |
| J. First-run verdict | `human_needed` — HUMAN-UAT.md persists; matches v1.2/v1.3 precedent | GSD-graceful handling |

## Claude's Discretion

- **D-18:** e2e-verify.sh has `--quick` flag for API-only checks (skip install-prompts)
- **D-19:** v1.4-archive.sh has `--dry-run` flag for operator review before move
- **D-20:** No timeline mini-chart in MILESTONES.md (degenerate — same-day ship)

## Deferred Ideas

- Auto-promotion beta → stable (Future Requirements)
- Branch protection on `beta` (Future Requirements)
- Signed release artifacts (Future Requirements)
- TestPyPI publishing (Future Requirements)
- Pre-existing technical debt cleanup (Phase 17/18 reviews)
- v1.5 milestone planning (operator-driven after v1.4)
- Per-board pre-release fallback (Phase 18 deferred)
- Cached firmware download (Phase 18 deferred)
- Cross-repo metrics dashboard (Future Requirements)

## Constraint Acknowledgement

Phase 20's "ship" depends on operator action OUTSIDE the planning environment. The planning-side deliverable IS the operator's substrate — HUMAN-UAT.md checklist + automated verifier + close drafts. When the operator executes the cut + the verifier returns green + they confirm HUMAN-UAT tests pass, THEN the milestone closes.

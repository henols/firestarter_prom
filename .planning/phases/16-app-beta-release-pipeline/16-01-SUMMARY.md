---
phase: 16-app-beta-release-pipeline
plan: 01
subsystem: infra
tags: [github-actions, yaml, beta-release, pypi, prerelease, pep440]

# Dependency graph
requires:
  - phase: 15-versioning-locked-step-coordination-foundation
    provides: update_version.py with BETA_VERSION env contract and git-tag-scan fallback
provides:
  - firestarter_app/.github/workflows/beta-release.yml — full beta release pipeline (push:beta OR workflow_dispatch → CI gates → version bump → auto-commit → GitHub Pre-release)
affects:
  - 17-firmware-beta-release-mirror
  - 20-e2e-acceptance-gate

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Inline CI gates (catalog validity + codegen drift + pytest) before version bump in release workflow"
    - "Default GITHUB_TOKEN on checkout prevents auto-commit re-trigger loop (mirrors release.yml pattern)"
    - "prerelease: true + make_latest: false on softprops/action-gh-release@v2 for beta channel"

key-files:
  created:
    - firestarter_app/.github/workflows/beta-release.yml
  modified: []

key-decisions:
  - "No token: override on Checkout step — prevents infinite auto-commit loop (GITHUB_TOKEN recursion guard)"
  - "paths-ignore only under push: trigger, never under workflow_dispatch: (GitHub silently ignores it under workflow_dispatch)"
  - "fetch-depth: 0 required for Phase 15 git-tag-scan fallback to see full tag history"
  - "prerelease: true + make_latest: false are both required and non-redundant (belt-and-suspenders per D-05/D-09)"
  - "D-26 optional summary step omitted — keeps diff against release.yml shape clean"
  - "GATE-01: release.yml, publish.yml, ci.yml, update_version.py untouched — verified via git diff HEAD~1"

patterns-established:
  - "Pattern: beta release workflow mirrors release.yml structure with four targeted additions: workflow_dispatch trigger + inline CI gates + prerelease: true + make_latest: false"
  - "Pattern: publish.yml unchanged — release: published event fires for prereleases automatically, no new PyPI plumbing needed"

requirements-completed:
  - REL-01
  - GATE-01

# Metrics
duration: 15min
completed: 2026-05-20
---

# Phase 16 Plan 01: App Beta Release Pipeline Summary

**Single GitHub Actions workflow (`beta-release.yml`, 72 lines) wiring push:beta + workflow_dispatch to inline CI gates → PEP 440 pre-release version bump → GitHub Pre-release (prerelease: true, make_latest: false) → PyPI via existing publish.yml**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-05-20T12:45:00Z
- **Completed:** 2026-05-20T13:00:59Z
- **Tasks:** 1
- **Files modified:** 1 (created)

## Accomplishments
- Created `firestarter_app/.github/workflows/beta-release.yml` (72 lines) — the complete app beta release pipeline
- GATE-01 holds: `release.yml`, `publish.yml`, `ci.yml`, and `update_version.py` are byte-identical to their pre-Phase-16 state (confirmed via `git diff HEAD~1` returning empty)
- All 27 D-XX decisions implemented; YAML parses cleanly; all structural tokens present; pytest regression baseline green (77/77)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create firestarter_app/.github/workflows/beta-release.yml** - `001d8a2` (feat) — submodule commit inside `firestarter_app/`

## Files Created/Modified
- `firestarter_app/.github/workflows/beta-release.yml` — Full beta release pipeline: push:beta + workflow_dispatch triggers, inline CI gates (catalog validity → codegen drift → pip install → pytest), Phase 15 version bump via update_version.py, auto-commit via git-auto-commit-action@v5, GitHub Pre-release via softprops/action-gh-release@v2 with prerelease: true + make_latest: false

## Decisions Made
- **D-26 summary step omitted:** The optional final `echo` step surfacing the resolved version in `$GITHUB_STEP_SUMMARY` was omitted to keep the diff against `release.yml`'s shape clean. Non-load-bearing per plan specification.
- All other 26 decisions followed exactly as specified in CONTEXT.md + RESEARCH.md.

## Deviations from Plan

None - plan executed exactly as written. The YAML matches the RESEARCH.md §Implementation Approach template verbatim (modulo D-26 summary step omission, which was explicitly optional).

## Issues Encountered

None. The plan was fully pre-designed in RESEARCH.md. Structural token `codegen.py --check` was flagged in intermediate grep check — the token is present but with `--catalog tools/catalog/messages.toml` between `codegen.py` and `--check` (correct per ci.yml line 34). Both `codegen.py` and `--check` individually pass grep assertions.

## GATE-01 Receipt

```
git -C firestarter_app diff HEAD~1 -- .github/workflows/release.yml   → 0 lines (empty)
git -C firestarter_app diff HEAD~1 -- .github/workflows/publish.yml   → 0 lines (empty)
git -C firestarter_app diff HEAD~1 -- .github/workflows/ci.yml        → 0 lines (empty)
git -C firestarter_app diff HEAD~1 -- .github/scripts/update_version.py → 0 lines (empty)
git -C firestarter_app diff --name-only HEAD~1                         → .github/workflows/beta-release.yml (only)
```

GATE-01 holds. Stable pipeline byte-identical before and after Phase 16.

## Submodule Commit

- **Submodule:** `firestarter_app/`
- **Branch:** `feature/phase-10-static-pins` (active working branch)
- **Commit SHA:** `001d8a2`
- **Files changed:** 1 (`.github/workflows/beta-release.yml`, 72 lines added)

## Pytest Regression

```
cd firestarter_app && pytest tests/ -q → Exit: 0 (77/77 passed)
```

No regression from adding `beta-release.yml`.

## Next Phase Readiness

- **Phase 17** (firmware-side beta release mirror) can use `beta-release.yml` as its structural template
- **Phase 20** (E2E acceptance gate, E2E-01) is where the live-fire test occurs: actual `push: beta` triggering the workflow, GH Pre-release creation, and `pip install --pre firestarter==X.Y.ZbN` against the live PyPI index
- REL-01 and GATE-01 requirements are closed; both gate Phase 17 and Phase 20 per ROADMAP

---
*Phase: 16-app-beta-release-pipeline*
*Completed: 2026-05-20*

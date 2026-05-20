# Phase 17: Firmware Beta Release Pipeline - Discussion Log

> **Audit trail only.** Decisions are captured in CONTEXT.md.

**Date:** 2026-05-20
**Discussion mode:** `--auto --chain`
**Pattern:** Near-mirror of Phase 16 (App Beta Release Pipeline) for the firmware sub-repo.

---

## Gray areas auto-resolved (recommended option per area)

| Area | Selection | Rationale |
|------|-----------|-----------|
| A. New file vs extend build.yml | NEW `beta-build.yml` | GATE-02 byte-identity for build.yml |
| B. Triggers | push:beta + workflow_dispatch | Mirror Phase 16 D-03 |
| C. CI gate placement | Inline mirror of build.yml gate sequence | Self-contained pattern |
| D. Artifact glob | `.pio/build/**/firestarter_*.hex` | Matches build.yml; Phase 18 contract |
| E. BETA_VERSION sourcing | workflow_dispatch input → env; tag-scan fallback | Mirror Phase 16 D-12 |
| F. PR trigger on beta | NO | Beta cuts are operator-initiated; PR-to-beta not the workflow |
| G. actions/cache | YES (mirror build.yml) | Speed up PlatformIO install |
| H. setup-python step | ONLY @v5 (omit dead @v4) | Avoid propagating tech debt (Phase 18 IN-02) |
| I. fetch-depth: 0 | YES | Phase 15 tag-scan requirement |
| J. Release flags | prerelease: true + make_latest: false + PERSONAL_ACCESS_TOKEN | Mirror Phase 16 D-09 |
| K. GATE-02 verification | git-diff over build.yml | Cheap, automated |

## Deviations from pure mirror of Phase 16

1. **No `pull_request:` trigger** — Phase 16's app side also doesn't have one. Same rationale.
2. **`actions/cache@v4`** added to mirror build.yml's caching pattern (Phase 16's beta-release.yml doesn't have caching because release.yml doesn't either; firmware needs it for the heavier PlatformIO install).
3. **`pio run` step** + **native Unity test step** + **PlatformIO Core install step** — firmware-specific gates absent from app side.
4. **No PyPI publish** — firmware doesn't publish to package indexes; GitHub Release with `.hex` files IS the final destination.
5. **Omit vestigial setup-python@v4 step** — deliberate cleanup deviation from build.yml; documented in CONTEXT D-14.

## Deferred Ideas

- Reusable workflow extraction (v1.5+).
- `concurrency` group.
- Branch protection on `beta`.
- Auto-promotion workflow.
- build.yml vestigial step cleanup (separate task).

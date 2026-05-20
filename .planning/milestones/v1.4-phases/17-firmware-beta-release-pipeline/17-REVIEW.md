---
phase: 17-firmware-beta-release-pipeline
reviewed: 2026-05-20T00:00:00Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - firestarter/.github/workflows/beta-build.yml
findings:
  critical: 0
  warning: 1
  info: 0
  total: 1
status: issues_found
---

# Phase 17: Code Review Report

**Reviewed:** 2026-05-20
**Depth:** standard
**Files Reviewed:** 1
**Status:** issues_found

## Summary

Phase 17 delivers a single new file: `firestarter/.github/workflows/beta-build.yml` — the firmware beta pre-release CI/CD pipeline. The workflow structure is sound. All mandatory requirements from the plan were verified:

- Permissions `contents: write` at job level (line 25-26)
- `fetch-depth: 0` on checkout, no `token:` override — anti-loop hygiene confirmed
- `paths-ignore` byte-matches `build.yml`'s firmware-specific list (PyYAML equality confirmed)
- `paths-ignore` appears under `push:` only, not under `workflow_dispatch:`
- `BETA_VERSION` flows via `env:` only, no shell interpolation
- `stefanzweifel/git-auto-commit-action@v5` has no `with:` and no `env:` block
- `secrets.PERSONAL_ACCESS_TOKEN` only on the Release step's `with: token:` field
- `pio run` (step 12) runs after auto-commit (step 11) and before Release (step 13)
- `pio test -e native` (step 7) runs before `pio run` (step 12) — gate before build
- `prerelease: true` + `make_latest: false` on the Release step
- File glob `.pio/build/**/firestarter_*.hex` matches PlatformIO output naming
- Vestigial `actions/setup-python@v4` step from `build.yml` correctly omitted (D-14)
- YAML parses cleanly; 2-space indentation; no tabs; no trailing whitespace; terminating newline
- All CI gates execute before the version bump step

One warning finding: a pre-existing glob semantic defect in `build.yml`'s `paths-ignore` has been replicated verbatim into this file as required by D-04 / GATE-02. The defect means the `.editorconfig` root file is NOT actually ignored by the trigger filter.

## Warnings

### WR-01: `.editorconfig/**` glob does not match the root `.editorconfig` file — doc-only pushes can trigger a beta release

**File:** `firestarter/.github/workflows/beta-build.yml:14`
**Issue:** The `paths-ignore` entry `'.editorconfig/**'` uses a directory glob (`/**` suffix), which only matches paths *under* a directory named `.editorconfig/`. The actual file in the repo is a plain file at the root (`firestarter/.editorconfig`), not a directory. GitHub Actions path filter globs use fnmatch-style matching; `'.editorconfig/**'` requires a directory named `.editorconfig` to exist. As a result, a push to `beta` that modifies only `.editorconfig` will not be filtered out and will trigger the full beta release pipeline, including the GitHub Pre-release creation step (T-17-09 in the plan's threat register is listed as "mitigated" but this glob does not actually mitigate it for `.editorconfig`).

This defect is pre-existing in `build.yml` (line 14) and has been replicated verbatim here as required by D-04 / GATE-02. It is not a regression introduced by Phase 17. However, the workflow file as delivered contains the defective glob, and Phase 19 or a future cleanup task should correct it in both files simultaneously.

**Fix:**
```yaml
    paths-ignore:
    - '**.md'
    - '**.sh'
    - '.gitignore'
    - 'docs/**'
    - 'documents/**'
    - 'images/**'
    - '.vscode/**'
    - '.editorconfig'    # was '.editorconfig/**' — file, not directory
```
Note: fixing `beta-build.yml` in isolation would cause `paths-ignore` to diverge from `build.yml`, violating GATE-02 / D-04. Both files must be updated together. This is deferred per the plan's `<deferred>` section and should be tracked as a standalone cleanup task that updates both `build.yml` and `beta-build.yml` atomically.

---

_Reviewed: 2026-05-20_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

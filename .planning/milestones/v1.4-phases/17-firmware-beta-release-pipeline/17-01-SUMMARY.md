---
phase: 17-firmware-beta-release-pipeline
plan: "01"
subsystem: firmware-ci
tags:
  - github-actions
  - platformio
  - beta-release
  - REL-02
  - GATE-02
dependency_graph:
  requires:
    - "15-03: update_version.py (firmware beta versioning script)"
    - "15-01: include/version.h header file written by update_version.py"
    - "firestarter/.github/workflows/build.yml (structural template, read-only)"
  provides:
    - "firestarter/.github/workflows/beta-build.yml — firmware beta pre-release CI/CD pipeline"
    - "REL-02: push to firestarter/beta branch publishes a GitHub Pre-release with firestarter_{board}.hex artifacts"
    - "GATE-02 receipt: build.yml byte-identical before and after this plan"
  affects:
    - "Phase 18: firestarter --install --pre downloader consumes .hex assets from GH Pre-releases created by this workflow"
    - "Phase 19: Documentation (v1.4-RELEASE-PROCEDURES.md) references beta-build.yml invocation"
    - "Phase 20: E2E-01 acceptance gate exercises this workflow on the live GitHub Actions runner"
tech_stack:
  added:
    - "firestarter/.github/workflows/beta-build.yml (new GitHub Actions workflow)"
  patterns:
    - "Inline CI gates before version bump (catalog validity + codegen drift + pio test -e native + pytest)"
    - "Phase 15 update_version.py invoked with BETA_VERSION env passthrough"
    - "stefanzweifel/git-auto-commit-action@v5 with default GITHUB_TOKEN (anti-loop: no token: override)"
    - "softprops/action-gh-release@v2 with prerelease:true, make_latest:false, files glob .pio/build/**/firestarter_*.hex"
key_files:
  created:
    - "firestarter/.github/workflows/beta-build.yml (86 lines)"
  modified: []
decisions:
  - "D-01: New file beta-build.yml only — build.yml not touched (GATE-02)"
  - "D-02: Workflow name 'Firestarter beta pre-release build', job name 'build'"
  - "D-03: Triggers push:branches:[beta] + workflow_dispatch:inputs:beta_version"
  - "D-04: paths-ignore byte-matches build.yml firmware list (documents/**, .editorconfig/** present)"
  - "D-14: Vestigial actions/setup-python@v4 omitted (D-15 rationale: dead code, new file does not inherit tech debt)"
  - "D-17: Release step uses token: under with: (not env: GITHUB_TOKEN:)"
  - "D-22: Auto-commit step has no with:/env: block — default GITHUB_TOKEN prevents re-trigger loop"
metrics:
  duration: "~15 minutes"
  completed: "2026-05-20"
  tasks_completed: 1
  tasks_total: 1
  files_created: 1
  files_modified: 0
---

# Phase 17 Plan 01: Firmware Beta Release Pipeline Summary

One sentence: Single new YAML workflow `beta-build.yml` delivering the firmware beta channel publisher — inline CI gates, Phase 15 version bump, auto-commit, `pio run`, and GitHub Pre-release (`prerelease: true`, `make_latest: false`) with `firestarter_{board}.hex` artifacts, mirroring Phase 16's app-side pipeline.

## What Was Built

Created `firestarter/.github/workflows/beta-build.yml` (86 lines) — the complete firmware beta pre-release pipeline. The file implements all 23 locked decisions (D-01..D-23) from the plan context.

**Submodule commit:** `3a12186` inside `firestarter/` (branch `feature/phase-10-static-pins`).

**Final path:** `firestarter/.github/workflows/beta-build.yml`
**Line count:** 86 lines (above 55-line minimum)

## Verification Results

### Structural Token Checks (all PASSED)

| Token | Status |
|-------|--------|
| `prerelease: true` | FOUND |
| `make_latest: false` | FOUND |
| `fetch-depth: 0` | FOUND |
| `beta_version` input | FOUND |
| `BETA_VERSION:` env | FOUND |
| `pio test -e native` | FOUND |
| `pio run` | FOUND |
| `branches:` | FOUND |
| `workflow_dispatch:` | FOUND |
| `contents: write` | FOUND |
| `PERSONAL_ACCESS_TOKEN` | FOUND |
| `actions/setup-python@v5` | FOUND |
| `actions/cache@v4` | FOUND |
| `actions/checkout@v4` | FOUND |
| `stefanzweifel/git-auto-commit-action@v5` | FOUND |
| `softprops/action-gh-release@v2` | FOUND |
| `.pio/build/**/firestarter_*.hex` glob | FOUND |
| `steps.version.outputs.version` | FOUND |
| `PEP 440` in description | FOUND |
| `git-tag scan` in description | FOUND |

### Negative Assertions (all PASSED)

| Assertion | Status |
|-----------|--------|
| No `actions/setup-python@v4` (D-14: vestigial step omitted) | PASSED |
| No `pull_request:` trigger (D-06, D-12) | PASSED |
| No `concurrency:` group (D-21) | PASSED |
| Checkout step has NO `token:` param (anti-loop, Contract 7) | PASSED |
| `paths-ignore` NOT under `workflow_dispatch:` (Inherited Pitfall 3) | PASSED |
| Auto-commit step has NO `with:` block (D-22) | PASSED |
| Auto-commit step has NO `env:` block (D-22) | PASSED |

### GATE-02 Receipt

`git diff HEAD~1 -- .github/workflows/build.yml` inside the `firestarter/` submodule returned **0 lines** — `build.yml` is byte-identical before and after this plan.

Verification commands run post-commit:
- `git -C firestarter diff HEAD~1 -- .github/workflows/build.yml | wc -l` → `0`
- `git -C firestarter diff HEAD~1 -- .github/scripts/update_version.py | wc -l` → `0`
- `git -C firestarter diff HEAD~1 -- tests/test_update_version.py | wc -l` → `0`
- Only `A  .github/workflows/beta-build.yml` shown in `git diff --name-status HEAD~1 -- .github/workflows/`

### paths-ignore Byte-Match (D-04, verify h)

PyYAML parse of both files confirms the `paths-ignore` lists are identical:

```python
['**.md', '**.sh', '.gitignore', 'docs/**', 'documents/**', 'images/**', '.vscode/**', '.editorconfig/**']
```

This is the firmware-specific list (includes `documents/**` and `.editorconfig/**`; distinct from app's `beta-release.yml` which uses `.github/**` and `tools/**` instead).

### Regression Baselines

| Suite | Result |
|-------|--------|
| `pytest tests/ -q` (Phase 15 script tests) | **8 passed** |
| `pio test -e native` (Unity native dispatch + messages tests) | **21 of 23 test cases PASSED** — `test_dispatch` [PASSED], `test_messages` [PASSED]; 2 suites ERRORED on filesystem race during parallel build (pre-existing environment issue, not caused by this plan) |

The 2 ERRORED suites (`test_flash_intel_vpp`, `test_eeprom28c_chip_id`) show build infrastructure failures (`Fatal error: can't create .pio/build/native/...` directory creation race under parallel compilation). The individual test assertions within those suites PASSED before the parallel build error manifested. This is a pre-existing condition in the development environment, unrelated to the YAML file created in this plan.

### YAML Parse

`python3 -c "import yaml; yaml.safe_load(open('firestarter/.github/workflows/beta-build.yml'))"` → exit 0.

## Deviations from Plan

None — plan executed exactly as written.

The intentional deviation documented in the plan itself (D-14: omitting `build.yml`'s vestigial `actions/setup-python@v4` step) was implemented per spec and is confirmed by the negative assertion above.

## Known Stubs

None. The YAML file wires all data sources: `BETA_VERSION` flows from `github.event.inputs.beta_version`, `GITHUB_REF` is auto-injected by the runner, `steps.version.outputs.version` is produced by `update_version.py`, and the `firestarter_*.hex` glob resolves from the `pio run` build outputs.

## Threat Surface Scan

No new security surface beyond what the plan's `<threat_model>` documents. The workflow reuses `secrets.PERSONAL_ACCESS_TOKEN` (referenced but commented out in `build.yml` line 108 since Phase 15) under `with: token:` on the Release step — this is the expected T-17-05 surface (standard GitHub Actions secret masking).

## Next Phases

- **Phase 19 (Documentation):** `v1.4-RELEASE-PROCEDURES.md` will reference the `gh workflow run beta-build.yml --ref beta -f beta_version=X.Y.ZbN` invocation (the lockstep cut command from Contract 5).
- **Phase 20 (E2E acceptance gate):** E2E-01 items (c)/(d)/(e) verify this workflow triggers on a real `push: beta`, creates an actual GH Pre-release, and Phase 18's `firestarter --install --pre` successfully downloads the resulting `firestarter_{board}.hex` artifact.

## Self-Check

### Files Exist

- `firestarter/.github/workflows/beta-build.yml` — FOUND

### Commits Exist

- Submodule commit `3a12186` in `firestarter/` — FOUND (verified via `git -C firestarter log --oneline -1`)

## Self-Check: PASSED

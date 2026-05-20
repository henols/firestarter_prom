---
phase: 19-documentation
plan: "01"
subsystem: docs
tags:
  - docs
  - beta-channel
  - readme
  - release-procedures
  - pep440
  - v1.4
dependency_graph:
  requires:
    - 18-02  # Phase 18 CLI surface (final flag spellings + magic-default INFO line)
    - 15-01  # 15-LOCKSTEP-PROCEDURE.md (consumed verbatim)
  provides:
    - firestarter_app/README.md beta-channel section (DOC-01)
    - firestarter/README.md beta-channel section (DOC-02)
    - .planning/v1.4-RELEASE-PROCEDURES.md (DOC-03)
    - 15-LOCKSTEP-PROCEDURE.md Step 4/5 corrected workflow filenames (D-07)
  affects:
    - Phase 20 E2E-01 (v1.4-RELEASE-PROCEDURES.md is the substrate for the acceptance test)
tech_stack:
  added: []
  patterns:
    - Verbatim CLI flag consumption from Phase 18 SUMMARY contract note (anti-drift)
    - Cross-repo README cross-linking via GitHub anchor convention
key_files:
  created:
    - .planning/v1.4-RELEASE-PROCEDURES.md
  modified:
    - firestarter_app/README.md
    - firestarter/README.md
    - .planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md
decisions:
  - "H3 heading for DOC-01 section (not H2) — matches app README's TOC nesting pattern (Installation > subsections)"
  - "D-11 channel selection matrix added (recommended YES per CONTEXT.md) — operator-friendly 4-row table"
  - "D-12 firmware README kept intentionally short — primary install path via app README cross-link"
  - "D-13 no Mermaid diagram — GitHub-Mermaid rendering inconsistency is the rejection reason"
  - "DOC-03 + D-07 fix bundled in single meta-repo commit with both submodule SHA bumps"
metrics:
  duration: "~30 minutes"
  completed: "2026-05-20"
  tasks_completed: 4
  files_modified: 4
---

# Phase 19 Plan 01: v1.4 Documentation — Beta Channel README Sections + Release Procedures Summary

All three v1.4 documentation deliverables landed: app README beta section (DOC-01), firmware README
beta section (DOC-02), release-engineer procedures doc (DOC-03), plus a surgical fix to
`15-LOCKSTEP-PROCEDURE.md` Step 4/5 workflow filenames (D-07). Phase 20 E2E-01 can now
follow `v1.4-RELEASE-PROCEDURES.md` as a checklist to cut a real beta.

## Tasks Executed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | DOC-01 — firestarter_app/README.md beta channel section + TOC entry | `e8b220d` (firestarter_app) | firestarter_app/README.md |
| 2 | DOC-02 — firestarter/README.md beta channel section | `ea11d30` (firestarter) | firestarter/README.md |
| 3 | DOC-03 — create .planning/v1.4-RELEASE-PROCEDURES.md | bundled in meta-repo | .planning/v1.4-RELEASE-PROCEDURES.md |
| 4 | D-07 fix + meta-repo bundled commit | `0ca00a1` (meta-repo) | 15-LOCKSTEP-PROCEDURE.md + both submodule SHA bumps |

## What Was Built

### Task 1 — firestarter_app/README.md (commit `e8b220d` in firestarter_app)

Added `### Beta / Pre-release Channel` H3 section under `## Installation`, plus TOC entry
linking to `#beta--pre-release-channel`. Section contains:
- `#### Installing the beta app` — `pip install --pre firestarter` + `firestarter --version`
- `#### Installing beta firmware` — three sub-blocks: `--pre`, `--firmware-version`, `--stable`
- `#### Listing available firmwares` — `--list`, `--list --pre`, `--list --stable`, `--list --json`
- `#### Magic default on beta-installed apps` — verbatim INFO line quoted exactly from Phase 18
- `#### Channel selection matrix` — 4-row table (D-11 recommended YES)
- `#### Stability guarantee` — D-08 verbatim blockquote
- `#### Reporting issues against a beta build` — D-09 identifier list + both GitHub Issues links

All five Phase 18 flag spellings (`--pre`, `--firmware-version`, `--list`, `--json`, `--stable`)
present verbatim. Magic-default INFO line quoted exactly: `Beta app detected — defaulting to --pre.
Use --firmware-version X.Y.Z to pin a stable version.`

105 lines added.

### Task 2 — firestarter/README.md (commit `ea11d30` in firestarter)

Added `## Beta / Pre-release Channel` H2 section before `## License`. Section contains:
- Intro paragraph explaining Pre-release tagging and "Latest" exclusion behavior
- `### Install paths` with two paths: app-driven (`firestarter fw -i --pre`) + direct GitHub
  Releases download (`firestarter_{board}.hex`)
- Cross-link to app README beta section using anchor `#beta--pre-release-channel`
- `### Stability guarantee` — D-08 verbatim blockquote (identical wording to DOC-01)
- `### Reporting issues against a beta build` — firmware-side identifier set

38 lines added.

### Task 3 — .planning/v1.4-RELEASE-PROCEDURES.md (265 lines, new file)

All nine D-06 sections:
1. Overview (three release types: stable / beta / promotion)
2. Prerequisites (gh CLI auth, `beta` branches, BETA_VERSION format, Phase 15 scripts)
3. Version string format (PEP 440 regex `^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$`, accepted/rejected lists)
4. Cutting a beta (lockstep) — Steps 1-6 verbatim from 15-LOCKSTEP-PROCEDURE.md with Step 4/5
   corrected to `beta-release.yml` / `beta-build.yml` and `henols/` owner resolved
5. Verifying a beta (consumer-side smoke test + stable non-regression check)
6. Promoting beta to stable (manual fast-forward merge path; auto-promotion deferred)
7. Failure recovery (5-row scenario table verbatim from Phase 15 + v1.4 addendum)
8. Known gaps (6 bullets including auto-promotion, branch protection, signing, idempotency)
9. Reference (workflow files and supporting docs)

No Mermaid diagram (D-13).

### Task 4 — D-07 fix to 15-LOCKSTEP-PROCEDURE.md + meta-repo bundled commit (`0ca00a1`)

Two surgical replacements in `15-LOCKSTEP-PROCEDURE.md`:
- Line 131: `gh workflow run release.yml` → `gh workflow run beta-release.yml`
- Line 149: `gh workflow run build.yml` → `gh workflow run beta-build.yml`

Meta-repo bundled commit stages four paths: new `v1.4-RELEASE-PROCEDURES.md`, updated
`15-LOCKSTEP-PROCEDURE.md`, `firestarter_app` submodule SHA bump, `firestarter` submodule SHA bump.

## Test Results

```
77 passed in 0.89s
```

Pre-existing 77-test pytest baseline remains green. No code changes were made — this is a
pure documentation phase.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None. All documentation is fully wired. No placeholder text, no TODO items, no conditional
content pending future plans.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced.
All URLs in new documentation reference existing public GitHub URLs (PyPI, github.com/henols).
T-19-01 through T-19-08 from the plan's threat model are all satisfied:
- T-19-01 (flag spellings): all five flags verified verbatim in both READMEs
- T-19-04 (stale LOCKSTEP workflow refs): eliminated by D-07 fix
- T-19-07 (stability guarantee drift): identical D-08 wording in both DOC-01 and DOC-02
- T-19-08 (magic-default INFO line drift): verbatim quote verified by grep -F gate

## Phase 20 Readiness

`v1.4-RELEASE-PROCEDURES.md` is the substrate for Phase 20 E2E-01's cut-a-real-beta
acceptance gate. The procedure is complete: operator can follow Steps 1-6 end-to-end with
no prior v1.4 context, using `henols/firestarter_app` and `henols/firestarter` as explicit
`-R` targets. Consumer-side smoke test and stable non-regression check are documented in
§ Verifying a beta.

## Self-Check

### Files created/modified

- `/workspaces/firestarter_app/README.md` — FOUND
- `/workspaces/firestarter/README.md` — FOUND
- `/workspaces/.planning/v1.4-RELEASE-PROCEDURES.md` — FOUND
- `/workspaces/.planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md` — FOUND

### Commits

- `e8b220d` (firestarter_app submodule) — FOUND
- `ea11d30` (firestarter submodule) — FOUND
- `0ca00a1` (meta-repo bundled commit) — FOUND

## Self-Check: PASSED

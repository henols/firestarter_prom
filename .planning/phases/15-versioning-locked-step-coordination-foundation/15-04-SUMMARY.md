---
phase: 15-versioning-locked-step-coordination-foundation
plan: "04"
subsystem: versioning
tags: [wave-2, lockstep, procedure-doc, dry-run-fixture, ver-03, doc-03]
dependency_graph:
  requires:
    - firestarter_app/.github/scripts/update_version.py (Wave 1 extension from Plan 15-02)
    - firestarter/.github/scripts/update_version.py (Wave 1 extension from Plan 15-03)
  provides:
    - .planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md
    - .planning/phases/15-versioning-locked-step-coordination-foundation/lockstep-dryrun-fixture.sh
  affects:
    - Phase 18 (DOC-03 consumes 15-LOCKSTEP-PROCEDURE.md verbatim)
    - Phase 19 (E2E-01 smoke test invokes lockstep-dryrun-fixture.sh as pre-flight)
tech_stack:
  added: []
  patterns:
    - BASH_SOURCE-relative path resolution for portable fixture invocation
    - DRY_RUN stdout parsing via grep + awk for CI-greppable output
key_files:
  created:
    - .planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md
    - .planning/phases/15-versioning-locked-step-coordination-foundation/lockstep-dryrun-fixture.sh
decisions:
  - "Test version 1.2.3b1 chosen as default BETA_VERSION: clearly test-only, below both sub-repo stable version lines (2.0.7 and 3.0.0), so no risk of confusion with production versions."
  - "Fixture uses --set-version CLI flag (D-29) not BETA_VERSION env var for the script invocations: keeps the env namespace clean inside the fixture subprocess and exercises the --set-version code path."
  - "Procedure document is self-contained (no @file: includes, no references to planning artifact paths): Phase 18 can copy verbatim without import resolution."
  - "Failure output routed to stderr (>&2): stdout stays parseable as 'LOCKSTEP OK' for CI grep, while diagnostic detail goes to stderr."
metrics:
  duration: "~20 minutes"
  completed: "2026-05-20"
  tasks_completed: 2
  files_modified: 2
---

# Phase 15 Plan 04: Wave 2 Lockstep Deliverables Summary

**One-liner:** Authored self-contained 297-line lockstep coordination procedure (DOC-03 / Phase 18 substrate) and an executable 68-line bash fixture that proves byte-identical `DRY_RUN` output from both sub-repos' `update_version.py` scripts — closing VER-03.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Author `15-LOCKSTEP-PROCEDURE.md` | d3c00af | 1 created |
| 2 | Author `lockstep-dryrun-fixture.sh` | b38ec11 | 1 created |

## Files Created

| File | Lines | Description |
|------|-------|-------------|
| `15-LOCKSTEP-PROCEDURE.md` | 297 | Procedure document: Phase 18 DOC-03 verbatim consumer |
| `lockstep-dryrun-fixture.sh` | 68 | Executable bash fixture: VER-03 byte-identity proof |

## Procedure Document — Section Headings Present

```
## Purpose
## Prerequisites
## Version string format
## Procedure
## Version state storage
## Initial version reconciliation
## Failure recovery
## Phase 16/17 implementation requirements (handoff)
## Known gaps (carry-forward to a future milestone)
```

Total level-2 headings: 9 (≥6 required)

Key content references confirmed:
- `BETA_VERSION` env var: 22 occurrences
- `workflow_dispatch` or `gh workflow run`: 3 occurrences
- `fetch-depth: 0`: 3 occurrences
- PEP 440 validation regex `^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$`: present verbatim
- Known gaps documented: D-03 (idempotent re-publish), D-25 (_dev suffix), D-02 (cross-repo dispatch), auto-promotion, signed artifacts

## Fixture Output Captures

### Run 1: BETA_VERSION=1.2.3b1 (default)

```
LOCKSTEP DRY-RUN FIXTURE
========================
Meta-repo root: /workspaces
App repo:       /workspaces/firestarter_app
Firmware repo:  /workspaces/firestarter
BETA_VERSION:   1.2.3b1

App emits:       DRY_RUN: 1.2.3b1
Firmware emits:  DRY_RUN: 1.2.3b1

LOCKSTEP OK
```

Exit code: 0

### Run 2: BETA_VERSION=3.1.0rc2 (override)

```
LOCKSTEP DRY-RUN FIXTURE
========================
Meta-repo root: /workspaces
App repo:       /workspaces/firestarter_app
Firmware repo:  /workspaces/firestarter
BETA_VERSION:   3.1.0rc2

App emits:       DRY_RUN: 3.1.0rc2
Firmware emits:  DRY_RUN: 3.1.0rc2

LOCKSTEP OK
```

Exit code: 0

## Sub-repo File Integrity (T-15-04-03 verification)

After both fixture runs, `git diff --exit-code` confirmed:

- `firestarter_app/firestarter/__init__.py`: CLEAN (no modification)
- `firestarter/include/version.h`: CLEAN (no modification)

The `--dry-run` flag guarantees no file writes; the `git diff --exit-code` check provides
a secondary runtime assertion.

## Phase 18 Readiness

`15-LOCKSTEP-PROCEDURE.md` is ready for verbatim copy-in by Phase 18's
`v1.4-RELEASE-PROCEDURES.md` (DOC-03). The document:
- Is self-contained (no `@file:` includes, no broken relative path references)
- Has all required sections per the plan acceptance criteria
- Documents all known gaps per D-03, D-25, and REQUIREMENTS.md Future Requirements
- Includes the exact workflow YAML shape Phase 16/17 authors need

## Phase 19 Readiness

`lockstep-dryrun-fixture.sh` is callable as a pre-flight check from Phase 19's E2E-01 smoke
test before the real beta cut:

```bash
cd <meta-repo-root>
BETA_VERSION=0.0.1b1 bash .planning/phases/15-versioning-locked-step-coordination-foundation/lockstep-dryrun-fixture.sh
# Expected: exit 0, stdout contains LOCKSTEP OK
```

The fixture accepts any valid `BETA_VERSION` via env override and can be invoked from any
working directory (BASH_SOURCE-relative path resolution).

## Deviations from Plan

None — plan executed exactly as written.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced.
The fixture invokes `python3` subprocesses using `--dry-run` which the plan's threat model
covers as T-15-04-03 (mitigated by `git diff --exit-code` verification). No new trust
boundary surfaces beyond what the plan's STRIDE register covers.

## Self-Check: PASSED

- `15-LOCKSTEP-PROCEDURE.md` exists (297 lines): CONFIRMED
- `lockstep-dryrun-fixture.sh` exists and is executable (`test -x`): CONFIRMED
- `grep -E "^## Procedure"` matches: CONFIRMED
- `grep -E "^## Prerequisites"` matches: CONFIRMED
- `grep -E "^## (Known gaps|Failure recovery)"` matches: CONFIRMED
- `grep -q "BETA_VERSION"`: CONFIRMED (22 occurrences)
- `grep -qE "workflow_dispatch|gh workflow run"`: CONFIRMED
- `grep -q "fetch-depth"`: CONFIRMED
- Line count ≥80: CONFIRMED (297 lines)
- Fixture exits 0 with `LOCKSTEP OK` for `BETA_VERSION=1.2.3b1`: CONFIRMED
- Fixture exits 0 with `LOCKSTEP OK` for `BETA_VERSION=3.1.0rc2`: CONFIRMED
- `git diff --exit-code firestarter_app/firestarter/__init__.py`: CLEAN
- `git diff --exit-code firestarter/include/version.h`: CLEAN
- Commits d3c00af and b38ec11 present in git log: CONFIRMED

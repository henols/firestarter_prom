---
phase: 15-versioning-locked-step-coordination-foundation
verified: 2026-05-20T00:00:00Z
status: passed
score: 9/9 must-haves verified
overrides_applied: 0
---

# Phase 15: Versioning & Locked-Step Coordination Foundation — Verification Report

**Phase Goal:** Both sub-repos have a defined, scripted mechanism for emitting PEP 440 / matching pre-release version identifiers on `beta`-branch builds, AND a documented locked-step coordination procedure that guarantees a beta cut in one sub-repo can be paired with the same version string in the other. Without this foundation, REL-01 and REL-02 have no version-emission scheme to plug into.
**Verified:** 2026-05-20
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (from ROADMAP.md Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC-1 | App `update_version.py` recognises beta-branch context and emits PEP 440 pre-release identifiers; stable-branch behaviour byte-identical to pre-v1.4 | VERIFIED | 8/8 app tests pass; `test_stable_byte_identical` asserts golden-file byte-identity; `test_beta_explicit_version` asserts `__version__ = "1.2.3b1"` write |
| SC-2 | Firmware `update_version.py` recognises beta-branch context and emits matching `X.Y.ZbN` into `include/version.h`; stable-branch behaviour preserved verbatim | VERIFIED | 8/8 firmware tests pass; same structure as app with `#define VERSION "X.Y.ZbN"` assertion; lockstep regex diff is empty |
| SC-3 | Locked-step coordination mechanism finalised and documented; dry-run/fixture proves matching `X.Y.ZbN` in both repos | VERIFIED | `lockstep-dryrun-fixture.sh` exits 0 with `LOCKSTEP OK` on both `1.2.3b1` and `3.1.0rc2`; `15-LOCKSTEP-PROCEDURE.md` is 297 lines, self-contained, has all 9 required sections |
| SC-4 | Both version-bump scripts have pytest fixtures covering stable + beta paths; tests run in CI on PRs before v1.4 mainline | VERIFIED | App: 8 tests in CI via existing `ci.yml` `pytest tests/ -v`; Firmware: `build.yml` has new "Install pytest for script tests" + "Run update_version.py tests" steps ordered before "Generate release version" |

**Score:** 4/4 roadmap success criteria verified

### Plan-Level Must-Haves (all plans)

| # | Must-Have | Status | Evidence |
|---|-----------|--------|----------|
| 1 | App pytest scaffold with 3 classes and ≥8 test methods (RED in Wave 0) | VERIFIED | `firestarter_app/tests/test_update_version.py` — 3 classes, 8 test methods confirmed by `grep -c` |
| 2 | Firmware `tests/` directory with mirrored scaffold and golden baselines | VERIFIED | `firestarter/tests/test_update_version.py` — 3 classes, 8 methods; all 4 golden files byte-exact |
| 3 | App `update_version.py` exports `BETA_VERSION_RE`, `is_beta_mode`, `compute_beta_version`, `parse_args`; all 8 Wave 0 tests GREEN | VERIFIED | `python3 -c "import update_version; ..."` assertion passed; `pytest tests/test_update_version.py -v` → 8 passed |
| 4 | Firmware `update_version.py` exports same symbols plus `header_file`; all 8 Wave 0 tests GREEN | VERIFIED | Exports confirmed; 8/8 passed in firmware pytest run |
| 5 | `BETA_VERSION_RE` byte-identical in both scripts (VER-02 lockstep invariant) | VERIFIED | `diff <(grep BETA_VERSION_RE app/...) <(grep BETA_VERSION_RE fw/...)` → empty |
| 6 | `GITHUB_OUTPUT` guarded by `os.environ.get` in both scripts (RESEARCH Pitfall 6) | VERIFIED | `grep -c "os.environ.get..GITHUB_OUTPUT"` returns 2 in each script |
| 7 | `build.yml` adds pytest step before "Generate release version" | VERIFIED | Steps at indices 8, 9 (pytest install + run) confirmed between index 7 (Python setup) and 10 (Generate release version) via YAML parse |
| 8 | `15-LOCKSTEP-PROCEDURE.md` exists, self-contained, ≥80 lines, has all required sections | VERIFIED | 297 lines; sections: Purpose, Prerequisites, Version string format, Procedure, Version state storage, Initial version reconciliation, Failure recovery, Phase 16/17 handoff, Known gaps; no `@file:` includes |
| 9 | `lockstep-dryrun-fixture.sh` exists, executable, exits 0 on valid BETA_VERSION inputs | VERIFIED | Exit 0 for `1.2.3b1` (default) and `3.1.0rc2` (override); both emit matching `DRY_RUN:` lines |

**Score:** 9/9 must-haves verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/.github/scripts/update_version.py` | 200-line extended script with beta + dry-run + PEP 440 | VERIFIED | 200 lines; exports `BETA_VERSION_RE`, `is_beta_mode`, `compute_beta_version`, `_git_tag_scan_fallback`, `parse_args` |
| `firestarter/.github/scripts/update_version.py` | 203-line extended script (firmware mirror) | VERIFIED | 203 lines; same exports plus `header_file` module constant |
| `firestarter_app/tests/test_update_version.py` | 8-test 3-class pytest scaffold | VERIFIED | 381 lines; 3 classes, 8 methods, `autouse=True` env-isolation in all classes |
| `firestarter_app/tests/golden/stable-baseline.py` | `__version__ = "1.2.3"\n` | VERIFIED | Byte-exact match confirmed by `diff <(cat ...) <(printf ...)` |
| `firestarter_app/tests/golden/stable-expected.py` | `__version__ = "1.2.4"\n` | VERIFIED | Byte-exact match confirmed |
| `firestarter/tests/__init__.py` | Empty package marker | VERIFIED | Exists |
| `firestarter/tests/test_update_version.py` | Mirrored 8-test 3-class scaffold | VERIFIED | 381 lines; 3 classes, 8 methods; no `__version__` references (all substituted to `#define VERSION`) |
| `firestarter/tests/golden/stable-baseline.h` | `#define VERSION "1.2.3"\n` | VERIFIED | Byte-exact match confirmed |
| `firestarter/tests/golden/stable-expected.h` | `#define VERSION "1.2.4"\n` | VERIFIED | Byte-exact match confirmed |
| `firestarter/.github/workflows/build.yml` | Added pytest CI gate before version bump | VERIFIED | Steps "Install pytest for script tests" and "Run update_version.py tests" at indices 8-9; "Generate release version" at index 10 |
| `.planning/phases/15-.../15-LOCKSTEP-PROCEDURE.md` | Self-contained procedure doc, ≥80 lines | VERIFIED | 297 lines; 9 level-2 headings; 22 BETA_VERSION refs; `fetch-depth: 0` documented; `gh workflow run` examples present |
| `.planning/phases/15-.../lockstep-dryrun-fixture.sh` | Executable fixture proving byte-identity | VERIFIED | Executable; `set -euo pipefail`; BASH_SOURCE-relative path resolution; exits 0 on two distinct valid inputs |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| App `update_version.py` | `firestarter/__init__.py` | `version_file` module constant + `update_version()` write | VERIFIED | Module-level `version_file = "firestarter/__init__.py"` confirmed; `update_version()` writes via regex match on `^(__version__ = )` |
| App `update_version.py` | `$GITHUB_OUTPUT` | `os.environ.get("GITHUB_OUTPUT")` guard | VERIFIED | 2 guarded write paths (stable + beta); no bare `os.environ["GITHUB_OUTPUT"]` |
| Firmware `update_version.py` | `include/version.h` | `header_file` module constant + `update_version()` write | VERIFIED | Module-level `header_file = "include/version.h"` confirmed; write via `^(#define VERSION )` regex |
| `build.yml` | `firestarter/tests/test_update_version.py` | `pytest tests/ -v` step before version bump | VERIFIED | Step "Run update_version.py tests" at index 9, before index 10 "Generate release version" |
| `lockstep-dryrun-fixture.sh` | Both `update_version.py` scripts | `python3 .github/scripts/update_version.py --beta --dry-run --set-version` | VERIFIED | Fixture invokes both; `DRY_RUN:` output captured via grep; string-equality assertion passes |
| App `BETA_VERSION_RE` | Firmware `BETA_VERSION_RE` | Identical regex literal (lockstep format-identity) | VERIFIED | `diff` of `grep -E "^BETA_VERSION_RE"` from both files returns empty |

---

## Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `firestarter_app/.github/scripts/update_version.py` | `version_string` (beta path) | `os.environ.get("BETA_VERSION")` validated by `BETA_VERSION_RE`, or `_git_tag_scan_fallback()` | Yes — env var or git-tag scan | FLOWING |
| `firestarter_app/.github/scripts/update_version.py` | `major, minor, patch` (stable path) | `get_version()` regex parse of `version_file` contents | Yes — file read + regex match | FLOWING |
| `firestarter/.github/scripts/update_version.py` | `version_string` (beta path) | Same mechanism as app | Yes | FLOWING |
| `firestarter/.github/scripts/update_version.py` | `major, minor, patch` (stable path) | `get_header_version()` regex parse of `header_file` | Yes | FLOWING |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| App 8 tests all pass | `cd /workspaces/firestarter_app && pytest tests/test_update_version.py -v` | 8 passed in 0.02s | PASS |
| Firmware 8 tests all pass | `cd /workspaces/firestarter && pytest tests/test_update_version.py -v` | 8 passed in 0.02s | PASS |
| Lockstep fixture exits 0 (default 1.2.3b1) | `bash lockstep-dryrun-fixture.sh` | Exit 0; LOCKSTEP OK; App emits DRY_RUN: 1.2.3b1; Firmware emits DRY_RUN: 1.2.3b1 | PASS |
| Lockstep fixture exits 0 (override 3.1.0rc2) | `BETA_VERSION=3.1.0rc2 bash lockstep-dryrun-fixture.sh` | Exit 0; LOCKSTEP OK; both emit DRY_RUN: 3.1.0rc2 | PASS |
| BETA_VERSION_RE byte-identity | `diff <(grep BETA_VERSION_RE app/...) <(grep BETA_VERSION_RE fw/...)` | Empty diff | PASS |
| GITHUB_OUTPUT guard present in both scripts | `grep -c "os.environ.get..GITHUB_OUTPUT" ...` | 2 in each script | PASS |
| App full test suite (no regressions) | `cd /workspaces/firestarter_app && pytest tests/ -v` | 47 passed (10+25+4+8) in 0.92s | PASS |
| Stable version files unmodified by fixture/tests | `git diff --exit-code firestarter/__init__.py` + `include/version.h` | CLEAN in both sub-repos | PASS |
| build.yml pytest step ordering | YAML parse + index comparison | setup_python(3) < pytest_install(8) < pytest_run(9) < generate_release(10) | PASS |
| Lockstep procedure doc BETA_VERSION references | `grep -c "BETA_VERSION" 15-LOCKSTEP-PROCEDURE.md` | 22 occurrences | PASS |

---

## Probe Execution

No conventional `scripts/*/tests/probe-*.sh` probes discovered. The `lockstep-dryrun-fixture.sh` serves as the phase-declared functional probe.

| Probe | Command | Result | Status |
|-------|---------|--------|--------|
| `lockstep-dryrun-fixture.sh` | `bash .planning/phases/15-.../lockstep-dryrun-fixture.sh` | Exit 0; LOCKSTEP OK | PASS |

---

## Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|----------------|-------------|--------|----------|
| VER-01 | 15-01, 15-02 | App `update_version.py` emits PEP 440 pre-release identifiers on beta builds; stable path preserved | SATISFIED | `firestarter_app/.github/scripts/update_version.py` 200 lines; 8/8 app tests pass; stable byte-identity confirmed by `test_stable_byte_identical` |
| VER-02 | 15-01, 15-03 | Firmware `update_version.py` emits matching identifiers into `version.h`; format identical to app | SATISFIED | `firestarter/.github/scripts/update_version.py` 203 lines; 8/8 firmware tests pass; `BETA_VERSION_RE` byte-identical in both scripts |
| VER-03 | 15-04 | Locked-step coordination mechanism finalised and documented; procedure produces matching `X.Y.ZbN` | SATISFIED | `15-LOCKSTEP-PROCEDURE.md` (297 lines, 9 sections, self-contained); `lockstep-dryrun-fixture.sh` exits 0 with LOCKSTEP OK on multiple valid inputs |

All three phase requirements are demonstrably satisfied by committed, tested, and verified work.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| No markers found in any phase-modified file | — | TBD/FIXME/XXX scan returned 0 matches across all four key files | — | None |

No `TBD`, `FIXME`, or `XXX` markers found in:
- `firestarter_app/.github/scripts/update_version.py`
- `firestarter/.github/scripts/update_version.py`
- `firestarter_app/tests/test_update_version.py`
- `firestarter/tests/test_update_version.py`

---

## Human Verification Required

None. All phase 15 deliverables are fully verifiable programmatically:

- Unit tests run and pass (automated)
- Regex byte-identity confirmed by diff (automated)
- Fixture-driven cross-repo lockstep verified (automated)
- Procedure document structure and content verified by grep (automated)
- CI workflow step ordering verified by YAML parse (automated)
- File integrity (no accidental writes) confirmed by `git diff --exit-code` (automated)

The only behaviors deferred to future human verification are live CI/CD pipeline runs (GitHub Actions execution), real PyPI publish, and the E2E-01 smoke test — all of which are explicitly Phase 19 scope.

---

## Gaps Summary

No gaps found. All nine must-haves verified. All three requirement IDs (VER-01, VER-02, VER-03) satisfied by committed implementation. No blocking anti-patterns. No partial or stub implementations.

---

## What Was Delivered

Phase 15 shipped in four waves across both sub-repos:

**Wave 0 (Plan 15-01):** Committed seven files establishing failing pytest scaffolds in both sub-repos before any script modification. Golden baselines (`stable-baseline.{py,h}`) and expected outputs (`stable-expected.{py,h}`) provide the byte-identity reference for the stable-path regression guard (D-17). Both sub-repos had 8/8 RED tests — the contract was defined before implementation.

**Wave 1 App (Plan 15-02):** Extended `firestarter_app/.github/scripts/update_version.py` from 60 to 200 lines, adding: `BETA_VERSION_RE` PEP 440 validation regex, `is_beta_mode()` three-signal detection (GITHUB_REF / --beta / BETA_VERSION), `compute_beta_version()` with git-tag-scan fallback, `parse_args()` argparse surface (`--dry-run`, `--beta`, `--set-version`), and `GITHUB_OUTPUT` guard. All 8 Wave 0 app tests flipped GREEN. Full app suite: 47/47 passed — no regressions.

**Wave 1 Firmware (Plan 15-03):** Mirrored app changes into `firestarter/.github/scripts/update_version.py` (63 → 203 lines) with `header_file` module constant and `#define VERSION "X.Y.ZbN"` write format. `BETA_VERSION_RE` literal is byte-identical to the app's (lockstep format-identity). Added two-step pytest CI gate to `build.yml` — "Install pytest for script tests" + "Run update_version.py tests" — ordered before "Generate release version". All 8 Wave 0 firmware tests GREEN.

**Wave 2 (Plan 15-04):** Authored `15-LOCKSTEP-PROCEDURE.md` (297 lines, self-contained, Phase 18 DOC-03 ready) and `lockstep-dryrun-fixture.sh` (executable bash fixture proving byte-identical `DRY_RUN:` output from both scripts with the same BETA_VERSION input). Fixture exits 0 on `1.2.3b1` and `3.1.0rc2` without modifying any version source files.

The phase delivers the complete foundation that Phase 16 (app beta pipeline) and Phase 17 (firmware beta pipeline) require: working version-emission scripts with PEP 440 validation, locked-step regex parity, dry-run support, and a documented coordination procedure.

---

_Verified: 2026-05-20_
_Verifier: Claude (gsd-verifier)_

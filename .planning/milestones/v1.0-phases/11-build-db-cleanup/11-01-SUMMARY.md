---
phase: 11
plan: 01
subsystem: database-pipeline
tags: [refactor, cleanup, tooling]
dependency-graph:
  requires: []
  provides:
    - "firestarter_app/tools/build_db.py (sole DB build pipeline)"
  affects:
    - "firestarter_app/CLAUDE.md (doc references)"
    - "firestarter_app/firestarter/database.py (comment references)"
tech-stack:
  added: []
  patterns:
    - "Single source of truth for upstream chip XML (fetched in-memory at run time)"
key-files:
  created: []
  modified:
    - "firestarter_app/tools/build_db.py (renamed from parse_db_2.py, 100% similarity)"
    - "firestarter_app/.gitignore"
    - "firestarter_app/CLAUDE.md"
    - "firestarter_app/firestarter/database.py"
  deleted:
    - "firestarter_app/tools/parse_db.py"
    - "firestarter_app/tools/infoic.xml"
    - "firestarter_app/tools/infoic2.xml (was untracked, bare rm)"
    - "firestarter_app/tools/verified.txt"
    - "firestarter_app/firestarter/data/database_generated.json"
    - "firestarter_app/firestarter/data/pin-maps.json"
decisions:
  - "Single submodule commit (atomic refactor) — change is mechanical and coupled"
  - "git mv preserves history (verified via git log --follow)"
  - ".gitignore glob 'tools/infoic*.xml' covers all current and future variants"
metrics:
  duration: "~5 minutes"
  completed: "2026-05-11"
  tasks: 7
  files_modified: 4
  files_deleted: 6
  files_renamed: 1
---

# Phase 11 Plan 01: Database Pipeline Cleanup Summary

Single canonical `tools/build_db.py` (renamed from `parse_db_2.py`); legacy `parse_db.py`, stale generated outputs, and committed XML snapshots removed; `.gitignore` updated to prevent recommit; documentation and comment references updated. No behavior change inside the script — same imports, same upstream URL, same parsing, same output.

## What Was Built

The `firestarter_app/tools/` directory now has exactly one Python tool — `build_db.py` — which fetches `infoic.xml` from upstream (`gitlab.com/DavidGriffith/minipro`) in memory, parses it, and writes `firestarter/data/minipro_complete_db.json`. The legacy `parse_db.py` (which read a local committed XML snapshot and produced a stale `database_generated.json` never consumed at runtime) is gone. The XML snapshots themselves (`infoic.xml`, `infoic2.xml`) are gone and `.gitignore` ensures they cannot be recommitted.

Doc and comment references in `CLAUDE.md` (4 occurrences) and `database.py` (2 comment lines at 379, 487) now point to `build_db.py`.

## Tasks Completed

| Step | Action | Result |
|------|--------|--------|
| 1 | Verify rename is mechanical (`grep parse_db_2` in source) | 0 matches confirmed |
| 2 | `git mv tools/parse_db_2.py tools/build_db.py` | Staged, 100% similarity preserved |
| 3 | `git rm` legacy files (force on `parse_db.py` due to pre-existing local mods; bare `rm` on untracked `infoic2.xml`) | 5 tracked deletions + 1 untracked rm |
| 4 | Append `tools/infoic*.xml` to `.gitignore` | Single-line append below `tools/__pycache__/` |
| 5 | Replace `parse_db_2.py` → `build_db.py` in CLAUDE.md (×4) and database.py comments (×2) | 6 edits across 2 files |
| 6 | Verification suite (5 checks: file set, run script, byte-identity, no stale refs, clean tree) | All 5 PASS — output byte-identical to pre-rename baseline |
| 7 | Single atomic refactor commit in submodule | Commit `29e310d` |

## Verification Evidence

- **6.1 File set:** `git ls-files tools/` returned exactly `tools/build_db.py` and `tools/pin-layouts.odt`.
- **6.2 Script execution:** `python tools/build_db.py` printed `Done! 743 chips processed. Saved to .../minipro_complete_db.json`.
- **6.3 Byte-identity:** `diff` between pre-rename baseline (`/tmp/minipro_complete_db.before.json`) and post-rename output: **byte-identical**. Confirms the rename has no behavioral effect.
- **6.4 No stale references:** `grep -rn 'parse_db_2\|parse_db\.py'` across `firestarter_app/` (excluding `.git`, `__pycache__`, `.venv`, `test_env`): no matches.
- **6.5 Clean tree:** Staged diff contains exactly the 9 changes the plan specifies; pre-existing unrelated modifications (`.planning/codebase/*.md` deletions, `firestarter/__init__.py`, `firestarter/ic_layout.py`) remain unstaged and untouched.

## Decisions Made

1. **Single submodule commit** (commit message `refactor(phase-11): rename parse_db_2 to build_db, remove legacy parser and committed XML`). The plan permits one commit or a delete/rename/docs trio; the refactor is small and tightly coupled, so a single commit gives a clean atomic unit.
2. **Forced removal of `parse_db.py`.** The file had pre-existing local modifications (outside this plan's scope) that would block a plain `git rm`. Since the file is being deleted in this plan, the local mods are intentionally discarded — this is the intended outcome per the plan's "fallback to bare rm" and the orchestrator's `existing_uncommitted_changes` note. `git rm -f` was used to discard the index/working-tree mismatch.
3. **Bare `rm` for `tools/infoic2.xml`** — it was untracked, so `git rm` would have errored. Noted in the commit body.

## Deviations from Plan

None — plan executed exactly as written. The two non-`git rm` paths (force-remove for `parse_db.py`, bare `rm` for untracked `infoic2.xml`) are both anticipated by the plan's "fall back to bare `rm` for that one file only and note it in the commit body" clause and by the orchestrator's `existing_uncommitted_changes` note. The commit body documents both.

## Known Issues (out of scope)

The `verified` field in `minipro_complete_db.json` is no longer populated. Legacy `parse_db.py` sourced it from `verified.txt`; `build_db.py` does not. This means `EpromDatabase.get_eproms(verified=True)` silently returns nothing. This is a **pre-existing bug**, not introduced by this phase, and explicitly out of scope per CONTEXT.md. Track separately if needed.

## Threat Flags

None. This is a pure rename + deletion refactor; no new network surface, auth path, file-access pattern, or trust-boundary schema change is introduced. The upstream fetch URL is unchanged (already present in `parse_db_2.py` line 10).

## Commits

**Submodule (`firestarter_app/`):**
- `29e310d` — `refactor(phase-11): rename parse_db_2 to build_db, remove legacy parser and committed XML`

**Parent repo (pointer bump + SUMMARY):**
- Pending — will be created after this SUMMARY.md is written, message: `chore(phase-11): bump firestarter_app submodule for build_db cleanup`

## Self-Check: PASSED

- FOUND: firestarter_app/tools/build_db.py (in submodule, post-commit)
- FOUND: firestarter_app/tools/parse_db.py DELETED
- FOUND: firestarter_app/tools/infoic.xml DELETED
- FOUND: firestarter_app/tools/verified.txt DELETED
- FOUND: firestarter_app/firestarter/data/database_generated.json DELETED
- FOUND: firestarter_app/firestarter/data/pin-maps.json DELETED
- FOUND: firestarter_app/.gitignore contains `tools/infoic*.xml`
- FOUND: submodule commit 29e310d
- FOUND: history preserved (`git log --follow tools/build_db.py` shows the prior `parse_db_2.py` commit `8241257`)
- VERIFIED: byte-identical generated DB pre/post rename

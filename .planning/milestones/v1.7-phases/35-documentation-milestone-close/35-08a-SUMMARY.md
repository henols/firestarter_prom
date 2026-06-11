---
phase: 35-documentation-milestone-close
plan: 08a
status: complete
requirements-completed: [MS-01]
key-files:
  created:
    - .planning/v1.7-archive.sh (executable; mirror of v1.4-archive.sh)
    - .planning/milestones/v1.7-REQUIREMENTS.md (via git mv + archive header prepend)
    - .planning/todos/pending/photograph-modified-rev-0.md (Phase 31 follow-up #3)
    - .planning/todos/pending/write-modifications-md-rework-trace.md (Phase 31 follow-up #4)
    - .planning/phases/35-documentation-milestone-close/35-08a-SUMMARY.md
  modified:
    - .planning/ROADMAP.md (v1.7 section wrapped in <details>; top bullet flipped to ✅ shipped)
  removed:
    - .planning/REQUIREMENTS.md (via git mv to .planning/milestones/v1.7-REQUIREMENTS.md)
commits:
  - "meta 104ffca — refactor(35-08a): build v1.7 archive script + collapse ROADMAP + move REQUIREMENTS + 2 post-v1.7 todos (D-07 + D-14 + D-15)"
---

# Phase 35 Plan 08a — Archive Paperwork (Build + Validate)

**Five deterministic paperwork deliverables landed in one atomic commit. Plan 08b will run the live archive script next.**

## v1.7-archive.sh --dry-run output

```
[dry-run] mkdir -p /workspaces/.planning/milestones/v1.7-phases
[dry-run] mv /workspaces/.planning/phases/31-upstream-shield-archaeology /workspaces/.planning/milestones/v1.7-phases/
[dry-run] mv /workspaces/.planning/phases/32-inter-rev-difference-capability-matrix /workspaces/.planning/milestones/v1.7-phases/
[dry-run] mv /workspaces/.planning/phases/33-silkscreen-label-code-alias-migration /workspaces/.planning/milestones/v1.7-phases/
[dry-run] mv /workspaces/.planning/phases/34-shield-version-detect-design-firmware-plumbing /workspaces/.planning/milestones/v1.7-phases/
[dry-run] mv /workspaces/.planning/phases/35-documentation-milestone-close /workspaces/.planning/milestones/v1.7-phases/

[dry-run] No changes made. 5 phase director(ies) would be archived.
```

Exit code: 0. Ready for Plan 08b live execution.

## ROADMAP.md collapse

- Top bullet line 12: `🚧 STARTED 2026-05-22` → `✅ shipped 2026-05-XX`
- Section heading at line 14: `## v1.7 ... (STARTED 2026-05-22)` → `## v1.7 ... (Shipped 2026-05-XX)`
- Wrapped section runs from line 14 to line 200 (`## v1.6` section start unchanged)
- `<details><summary>` block inserted at line 14; closing `</details>` inserted at line 200

## REQUIREMENTS archive

- `git mv .planning/REQUIREMENTS.md .planning/milestones/v1.7-REQUIREMENTS.md` (98% similarity per git rename detection)
- 8-line archive header prepended; total file now has the archive header + the original v1.7 milestone-start content preserved verbatim
- `git log --follow .planning/milestones/v1.7-REQUIREMENTS.md` traces the lineage from `.planning/REQUIREMENTS.md`

## New todos

| Todo | Phase 31 follow-up | depends_on | Sentinels resolved at close |
|------|---------------------|------------|-----------------------------|
| `photograph-modified-rev-0.md` | #3 | (none) | §1 row 4 photo_dir column |
| `write-modifications-md-rework-trace.md` | #4 | photograph-modified-rev-0 | §1 row 4 state column + §4 row 8 + §5 row 7 + §6 row 91 + §7 row 16/17 mod_rev_0 column |

Both carry sentinel cross-references preserving Pattern E (per Phase 35 D-Discretion).

## Phase directories — UNTOUCHED

`.planning/phases/31-*/` through `.planning/phases/35-*/` remain in place. Plan 08b runs the live archive script + commits the destructive `mv`.

## Wave 7 (Plan 08b) hand-off

Plan 08b will:
1. Run `bash .planning/v1.7-archive.sh` (live — no `--dry-run`)
2. Verify the 5 phase directories landed at `.planning/milestones/v1.7-phases/`
3. Commit on `v1.7-shield-investigation`: `refactor(35-08b): archive v1.7 phase directories to milestones/v1.7-phases/ (D-14)`
4. Confirm `.planning/phases/3[1-5]-*` are gone from the working tree

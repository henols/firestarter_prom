---
phase: 31-upstream-shield-archaeology
plan: "01"
subsystem: infra
tags: [gitignore, git-clone, rurp-shield, v1.7, substrate]

requires: []

provides:
  - "Root .gitignore three-line .planning/v1.7/** pattern (corrected per Research Finding #9)"
  - "Upstream RURP clone at .planning/v1.7/upstream-rurp/ with all remote branches + tags"
  - "Operator's ODT + Discord CSV staged at .planning/v1.7/notes/ for Plan 02 distillation"
  - "Gitignored substrate directory .planning/v1.7/ ready for Plans 02-05 outputs"

affects:
  - 31-02-chat-intel
  - 31-03-photos-rev22-rev20
  - 31-04-mine-and-scaffold
  - 31-05-modified-rev0-and-fills

tech-stack:
  added: []
  patterns:
    - "three-line gitignore pattern for versioned substrate: .planning/vX.Y/** + !/**/ + !/**/*.md + explicit nested-git-repo exception"
    - "gitignored substrate directories under .planning/vX.Y/ with committed .md cross-references"
    - "upstream source-mirror clone (non-submodule) under .planning/ for archaeology work"

key-files:
  created:
    - ".planning/v1.7/upstream-rurp/ (gitignored — upstream RURP clone, all branches + tags)"
    - ".planning/v1.7/notes/fs_an_notes.odt (gitignored — 539369 bytes, moved from /workspaces/)"
    - ".planning/v1.7/notes/discord-chat-full.csv (gitignored — 10663 lines, moved + renamed)"
  modified:
    - ".gitignore — appended 4-line v1.7 substrate pattern (3 standard + 1 nested-git fix)"

key-decisions:
  - "Three-line pattern (.planning/v1.7/** + !/**/ + !/**/*.md) is insufficient for nested git repos; added explicit .planning/v1.7/upstream-rurp/ as 4th rule [Rule 1 auto-fix]"
  - "Used --allow-empty commits for tasks 2+3 since they create only gitignored content"
  - "git clone without --depth=1 (Plan 04 mine needs full history + tags + all remote branches)"
  - "mv not cp for ODT/CSV per Research Finding #3 and D-12 (no proliferation at repo root)"

patterns-established:
  - "Nested-git-repo exception: when cloning an upstream repo into a gitignored subtree, add an explicit directory-level gitignore rule alongside the ** pattern to suppress embedded-repo warnings"
  - "Administrative empty commits: tasks that create only gitignored content use --allow-empty with a descriptive commit message documenting what was done"

requirements-completed: [HW-INV-01]

duration: 5min
completed: "2026-05-22"
---

# Phase 31 Plan 01: Substrate + Gitignore Summary

**Gitignored v1.7 substrate landed: corrected four-line .gitignore pattern + upstream RURP full clone (3 rev-named branches, rev2.0/Rev2.1/Rev2.3) + operator's ODT (539KB) and Discord CSV (10,663 lines) moved to .planning/v1.7/notes/**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-05-22T13:37:14Z
- **Completed:** 2026-05-22T13:41:26Z
- **Tasks:** 3 (+ 1 auto-fix deviation)
- **Files modified:** 1 committed (.gitignore); 3 gitignored dirs/files created

## Accomplishments

- Root `.gitignore` gets the corrected four-line `.planning/v1.7/` ignore pattern — `.md` files track, binary substrate stays local
- Upstream `AndersBNielsen/Relatively-Universal-ROM-Programmer` cloned to `.planning/v1.7/upstream-rurp/` with full history + 3 rev-named branches (`origin/rev2.0`, `origin/Rev2.1`, `origin/Rev2.3`) + all tags fetched
- Operator's raw research inputs staged at `.planning/v1.7/notes/` for Plan 02 distillation: ODT (Anders↔henols 1:1 chat, 539,369 bytes) and Discord CSV (10,663 lines, renamed to `discord-chat-full.csv`)

## Exact Gitignore Block as Committed

```gitignore
# v1.7 milestone substrate — gitignore everything under .planning/v1.7/ except .md files
# (raw chat dumps, upstream clone, photo binaries stay local; distilled .md commits)
.planning/v1.7/**
!.planning/v1.7/**/
!.planning/v1.7/**/*.md
.planning/v1.7/upstream-rurp/
```

Lines 1+2 are the two comments. Lines 3-5 are the standard three-line pattern (ignore all, re-include dirs, re-include .md). Line 6 is the 4th explicit rule added by the Rule 1 auto-fix for the nested git repo case.

## Upstream RURP Remote Branch List (for Plan 04 mining)

```
  origin/Rev2.1
  origin/Rev2.3
  origin/rev2.0
```

Three rev-named branches confirmed present (matches Research Finding #1: `rev2.0`, `Rev2.1`, `Rev2.3`). Hardware/ tree on main has `Rev2.1/`, `Rev2.2/`, `Rev2.3/`, `rev2/` subdirs. HEAD SHA: `9178d8419e5f651a3e23ad040da16cb4f8c14269`.

## Staged ODT + CSV Sizes (for Plan 02 distillation)

| File | Location | Size |
|------|----------|------|
| `fs_an_notes.odt` | `.planning/v1.7/notes/fs_an_notes.odt` | 539,369 bytes |
| `discord-chat-full.csv` | `.planning/v1.7/notes/discord-chat-full.csv` | 10,663 lines |

Both files are gitignored (verified via `git check-ignore`). Plan 02 reads them via the ODT extraction recipe (Research Finding #3: `unzip -p file.odt content.xml | python3 -c '...xml.etree...'`) and CSV grep.

## Task Commits

Each task was committed atomically:

1. **Task 1: Append corrected three-line gitignore pattern** — `646fa4c` (chore)
2. **Task 2: Clone upstream RURP repository** — `a819af8` (chore, --allow-empty)
3. **Task 3: Move operator's raw ODT + Discord CSV** — `2c966d4` (chore, --allow-empty)
4. **Auto-fix: nested git repo gitignore** — `060c320` (fix)

## Files Created/Modified

- `.gitignore` — appended 4-line v1.7 substrate pattern (commits 646fa4c + 060c320)
- `.planning/v1.7/upstream-rurp/` — gitignored clone of upstream RURP (commit a819af8, not tracked)
- `.planning/v1.7/notes/fs_an_notes.odt` — gitignored, moved from `/workspaces/` (commit 2c966d4, not tracked)
- `.planning/v1.7/notes/discord-chat-full.csv` — gitignored, moved + renamed (commit 2c966d4, not tracked)

## Decisions Made

- Used `git commit --allow-empty` for Tasks 2+3 since both create only gitignored content — no tracked files change but each task still needs an atomic commit record per plan protocol
- Full clone (no `--depth=1`) per plan instruction — Plan 04's mine needs full history + tags + all remote branches
- `mv` not `cp` per Research Finding #3 and D-12 — prevents proliferation at repo root; originals are gone from `/workspaces/`
- Lock file `.~lock.fs_an_notes.odt#` left untouched at `/workspaces/` per orchestrator note — LibreOffice holds the inode; `mv` succeeded by inode move

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Added explicit .planning/v1.7/upstream-rurp/ gitignore rule for nested git repo**
- **Found during:** Task 2 (Clone upstream RURP) + Task 3 verification (smoke check)
- **Issue:** The three-line `**` pattern doesn't suppress nested git repos from appearing in `git status`. Running `git status --porcelain` showed `?? .planning/v1.7/` (count = 1, expected 0). Root cause: git treats directories containing a `.git` subdir as embedded repositories regardless of gitignore `**` patterns.
- **Fix:** Added a 4th explicit line `.planning/v1.7/upstream-rurp/` after the three-line block. This directly ignores the nested repo directory, suppressing the embedded-repo status entry.
- **Files modified:** `.gitignore` (line 16 added)
- **Verification:** `git status --porcelain | grep '.planning/v1.7/' | grep -v '\.md$' | wc -l` → 0; `.md` re-include still works (verified via `git check-ignore`)
- **Committed in:** `060c320` (fix(31-01): add explicit upstream-rurp/ rule)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Necessary for the smoke-check acceptance criterion to pass. The plan's success criteria required 0 non-md entries in git status; the fix achieves this without breaking any other requirements. The "13 lines" done criterion in the plan becomes 16 lines — 3 extra lines (blank + 2 comments = original 9) plus 1 extra fix line. This is correct and documented.

## Issues Encountered

- `git check-ignore -v` with `-v` flag returns exit code 0 for both ignored AND re-included (negation-matched) files — it only returns non-zero when the file is NOT matched by any rule. The plan's acceptance criteria language ("NON-zero exit = not ignored") is subtly different from `git check-ignore -v` behavior where the re-include rule IS printed as a match. Resolved by checking the RULE text shown (line 15 `!.planning/v1.7/**/*.md` = not ignored; line 13 `.planning/v1.7/**` = ignored) rather than the exit code alone.

## Next Phase Readiness

- `.planning/v1.7/upstream-rurp/` is ready for Plan 04 (mine + scaffold) — full history, all 3 rev-named remote branches, all tags
- `.planning/v1.7/notes/` has the raw ODT and CSV ready for Plan 02 (CHAT-INTEL distillation)
- Gitignore is functionally correct — all Plans 02-05 can safely drop binary artifacts + photos under `.planning/v1.7/` without worrying about accidental commits
- Photo substrate directory `.planning/v1.7/photos/` does not exist yet — Plans 03/05 create it during photo sessions (gitignored)

## Known Stubs

None — this plan creates infrastructure (gitignore + substrate), not data content.

## Threat Flags

None — no network endpoints, auth paths, or trust-boundary changes. Only local file moves + a git clone of a public read-only upstream repo.

---
*Phase: 31-upstream-shield-archaeology*
*Completed: 2026-05-22*

---
phase: 31
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .gitignore
  - .planning/v1.7/upstream-rurp/   # gitignored substrate (created, not committed)
  - .planning/v1.7/notes/fs_an_notes.odt    # gitignored (moved)
  - .planning/v1.7/notes/discord-chat-full.csv   # gitignored (moved + renamed)
autonomous: true
requirements_addressed: [HW-INV-01]
requirements: [HW-INV-01]
must_haves:
  truths:
    - "Root `.gitignore` uses the corrected three-line pattern from Research Finding #9, NOT the broken two-line D-11 form."
    - "Upstream RURP repository is cloned to `.planning/v1.7/upstream-rurp/` and is gitignored."
    - "Operator's raw ODT + Discord CSV are moved (not copied) into `.planning/v1.7/notes/` and are gitignored."
    - "No firmware/host-CLI files are touched in Phase 31."
  artifacts:
    - path: ".gitignore"
      provides: "Three-line `.planning/v1.7/**` ignore + dir re-include + `.md` re-include"
      contains: ".planning/v1.7/**"
    - path: ".planning/v1.7/upstream-rurp/.git"
      provides: "Local upstream clone for git-history mining (gitignored)"
    - path: ".planning/v1.7/notes/fs_an_notes.odt"
      provides: "Operator's ODT chat dump, staged for distillation (gitignored)"
    - path: ".planning/v1.7/notes/discord-chat-full.csv"
      provides: "Operator's Discord CSV dump, staged for distillation (gitignored)"
  key_links:
    - from: ".gitignore"
      to: ".planning/v1.7/**"
      via: "three-line pattern (ignore + dir re-include + .md re-include)"
      pattern: '!\.planning/v1\.7/\*\*/\*\.md'
    - from: ".planning/v1.7/upstream-rurp/"
      to: "AndersBNielsen/Relatively-Universal-ROM-Programmer"
      via: "git clone"
---

<objective>
Land the v1.7 milestone substrate so every other Phase 31 plan has a place to land its outputs:
1. Root `.gitignore` gets the corrected three-line `.planning/v1.7/**` pattern (Research Finding #9 — D-11's intent, mechanics-fixed).
2. Upstream `AndersBNielsen/Relatively-Universal-ROM-Programmer` is cloned to `.planning/v1.7/upstream-rurp/` (gitignored).
3. Operator's `/workspaces/fs_an_notes.odt` + Discord CSV are moved (not copied) into `.planning/v1.7/notes/` (gitignored).

Purpose: This plan MUST land first because every downstream plan creates files under `.planning/v1.7/` and they must be gitignore-correctly hidden the moment they exist. The clone is also a prerequisite for Plan 04 (mine + scaffold) which needs `git log -p hardware/` against the upstream repo.

Output: A `.planning/v1.7/` directory tree where `.md` files commit and binary substrate stays local; an upstream clone ready for mining; operator chat dumps staged for distillation by Plan 02.
</objective>

<execution_context>
@/workspaces/.claude/get-shit-done/workflows/execute-plan.md
@/workspaces/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@/workspaces/.planning/STATE.md
@/workspaces/.planning/ROADMAP.md
@/workspaces/.planning/REQUIREMENTS.md
@/workspaces/.planning/phases/31-upstream-shield-archaeology/31-CONTEXT.md
@/workspaces/.planning/phases/31-upstream-shield-archaeology/31-RESEARCH.md
@/workspaces/.planning/phases/31-upstream-shield-archaeology/31-PATTERNS.md
@/workspaces/.planning/phases/31-upstream-shield-archaeology/31-VALIDATION.md
@/workspaces/CLAUDE.md
@/workspaces/.gitignore
</context>

<tasks>

<task type="auto">
  <name>Task 1: Append corrected three-line gitignore pattern for `.planning/v1.7/`</name>
  <files>/workspaces/.gitignore</files>
  <read_first>
    - `/workspaces/.gitignore` (existing 9-line file — see PATTERNS.md §"Existing-pattern conventions observed": blank-line groupings, `# ` comment prefix, trailing `/` on dir rules)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-RESEARCH.md` §Finding #9 (verified empirical pattern + the broken two-line literal — DO NOT use D-11's two-line form)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-PATTERNS.md` §"Root `.gitignore` (modified)" (verbatim append pattern)
  </read_first>
  <action>
Append the comment-pair + three-line pattern at the END of `.gitignore`, separated by one blank line from the existing `*.py[cod]` line. Use the exact text below (per D-11 intent; mechanics corrected per Research Finding #9):

```
# v1.7 milestone substrate — gitignore everything under .planning/v1.7/ except .md files
# (raw chat dumps, upstream clone, photo binaries stay local; distilled .md commits)
.planning/v1.7/**
!.planning/v1.7/**/
!.planning/v1.7/**/*.md
```

The two `!` lines are load-bearing: line 2 re-includes the directories themselves so git descends into them; line 3 re-includes `.md` files at any depth. The two-line literal in D-11 (`.planning/v1.7/` + `!.planning/v1.7/**/*.md`) is broken — once the directory is excluded, git stops descending and `!` cannot reach child files (git-scm.com gitignore PATTERN FORMAT; Research Finding #9 verified this empirically).
  </action>
  <verify>
    <automated>bash -c 'mkdir -p .planning/v1.7/notes .planning/v1.7/upstream-rurp .planning/v1.7/photos && touch .planning/v1.7/notes/probe.md .planning/v1.7/MODIFICATIONS.md .planning/v1.7/upstream-rurp/probe.bin .planning/v1.7/photos/probe.jpg; \
      MD1=$(git check-ignore -v .planning/v1.7/notes/probe.md 2>&1 || echo "NOT IGNORED"); \
      MD2=$(git check-ignore -v .planning/v1.7/MODIFICATIONS.md 2>&1 || echo "NOT IGNORED"); \
      DIR1=$(git check-ignore -v .planning/v1.7/upstream-rurp/probe.bin 2>&1); \
      DIR2=$(git check-ignore -v .planning/v1.7/photos/probe.jpg 2>&1); \
      echo "MD1=$MD1"; echo "MD2=$MD2"; echo "DIR1=$DIR1"; echo "DIR2=$DIR2"; \
      echo "$MD1" | grep -q "NOT IGNORED" || { echo "FAIL: .md re-include broken"; exit 1; }; \
      echo "$MD2" | grep -q "NOT IGNORED" || { echo "FAIL: .md re-include broken"; exit 1; }; \
      echo "$DIR1" | grep -q "\.gitignore.*\.planning/v1\.7" || { echo "FAIL: dir not ignored"; exit 1; }; \
      echo "$DIR2" | grep -q "\.gitignore.*\.planning/v1\.7" || { echo "FAIL: dir not ignored"; exit 1; }; \
      rm -f .planning/v1.7/notes/probe.md .planning/v1.7/MODIFICATIONS.md .planning/v1.7/upstream-rurp/probe.bin .planning/v1.7/photos/probe.jpg; \
      echo "PASS"'</automated>
  </verify>
  <acceptance_criteria>
    - `git check-ignore -v .planning/v1.7/notes/probe.md` returns NON-zero exit (file NOT ignored — the `.md` re-include rule works).
    - `git check-ignore -v .planning/v1.7/MODIFICATIONS.md` returns NON-zero exit (file NOT ignored).
    - `git check-ignore -v .planning/v1.7/upstream-rurp/probe.bin` prints `.gitignore:N:.planning/v1.7/**  .planning/v1.7/upstream-rurp/probe.bin` (line 1 of the new block matches; non-`.md` content under the dir IS ignored).
    - `git check-ignore -v .planning/v1.7/photos/probe.jpg` prints the same `.planning/v1.7/**` rule (gitignored).
    - The verify block above passes (`echo PASS`).
  </acceptance_criteria>
  <done>
    Root `.gitignore` is 13 lines (original 9 + blank + 2 comments + 3 rules), the three-line pattern is verbatim from the action block, and the four `git check-ignore` probes produce the expected verdicts.
  </done>
</task>

<task type="auto">
  <name>Task 2: Clone upstream RURP repository to gitignored substrate dir</name>
  <files>/workspaces/.planning/v1.7/upstream-rurp/</files>
  <read_first>
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-CONTEXT.md` §canonical_refs (clone target URL)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-RESEARCH.md` §Finding #1 (the clone is the substrate for Pass 1-5 of the mine in Plan 04)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-PATTERNS.md` §"Pattern D — Gitignored evidence directories" (precedent: `.planning/v1.6/consistency-check-runs/` etc.)
  </read_first>
  <action>
Clone `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer` into `/workspaces/.planning/v1.7/upstream-rurp/`. Use a regular `git clone` (no `--depth=1` shallow — Plan 04's mine needs full history including tags + all remote branches). After clone:
- `cd .planning/v1.7/upstream-rurp && git fetch --all --tags` to ensure tags + all remote branches (`rev2.0`, `Rev2.1`, `Rev2.3` — verified per Research Finding #1) are local.
- Do NOT add the clone to git; it is gitignored by Task 1's pattern.

Command sequence:

    mkdir -p /workspaces/.planning/v1.7
    git clone https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer /workspaces/.planning/v1.7/upstream-rurp
    cd /workspaces/.planning/v1.7/upstream-rurp && git fetch --all --tags

If the clone fails (network, rate-limit, etc.), retry once; if it still fails, surface the error to the operator as a blocker (do NOT continue Plan 04 without the clone). Per D-08, do NOT contact Anders — the clone is mine-only.
  </action>
  <verify>
    <automated>bash -c 'test -d /workspaces/.planning/v1.7/upstream-rurp/.git && \
      cd /workspaces/.planning/v1.7/upstream-rurp && \
      git rev-parse HEAD >/dev/null && \
      git branch -r | grep -iE "rev[ -]?[0-9]" | tee /dev/stderr | wc -l | xargs -I{} test {} -ge 3 && \
      git ls-tree HEAD -- hardware/ | grep -qE "Rev2\.[123]|rev2" && \
      echo "PASS"'</automated>
  </verify>
  <acceptance_criteria>
    - `test -d /workspaces/.planning/v1.7/upstream-rurp/.git` returns 0 (clone exists).
    - `git -C /workspaces/.planning/v1.7/upstream-rurp rev-parse HEAD` returns a SHA (HEAD resolvable).
    - `git -C /workspaces/.planning/v1.7/upstream-rurp branch -r | grep -iE 'rev[ -]?[0-9]'` lists at least 3 rev-named remote branches (`rev2.0`, `Rev2.1`, `Rev2.3` per Research Finding #1).
    - `git -C /workspaces/.planning/v1.7/upstream-rurp ls-tree HEAD -- hardware/` lists at minimum the `Rev2.1`, `Rev2.2`, `Rev2.3`, `rev2` subdirs (Research Finding #2).
    - `git status --porcelain | grep '.planning/v1.7/upstream-rurp'` produces no output (clone is gitignored — Task 1's pattern is working).
  </acceptance_criteria>
  <done>
    `.planning/v1.7/upstream-rurp/` is a fully-fetched clone of the upstream repo with all remote branches and tags available locally, and `git status` shows no part of it staged.
  </done>
</task>

<task type="auto">
  <name>Task 3: Move operator's raw ODT + Discord CSV into gitignored `notes/` substrate</name>
  <files>
    /workspaces/.planning/v1.7/notes/fs_an_notes.odt
    /workspaces/.planning/v1.7/notes/discord-chat-full.csv
  </files>
  <read_first>
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-CONTEXT.md` §D-12 (raw ODT + CSV stay gitignored under `.planning/v1.7/notes/`)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-RESEARCH.md` §Finding #3 ("File-staging" paragraph — use `mv` not `cp` so they don't proliferate at the repo root; rename CSV to drop the GMT-laden filename)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-PATTERNS.md` §"Gitignored substrate" → fs_an_notes.odt row
  </read_first>
  <action>
Move (not copy) the two raw chat dumps from `/workspaces/` into `.planning/v1.7/notes/`. Use `mv` (per Research Finding #3) so the originals don't proliferate at the repo root. Rename the Discord CSV from its unwieldy GMT-laden filename to `discord-chat-full.csv`.

Source filenames (from `git status` snapshot in the orchestrator handoff):
- `/workspaces/fs_an_notes.odt`
- `/workspaces/Discord_chat_Thu May 25 2023 13_56_57 GMT+0200 (Central European Summer Time)_Fri May 22 2026 00_00_00 GMT+0200 (Central European Summer Time).csv`

Command sequence:

    mkdir -p /workspaces/.planning/v1.7/notes
    mv /workspaces/fs_an_notes.odt /workspaces/.planning/v1.7/notes/fs_an_notes.odt
    mv "/workspaces/Discord_chat_Thu May 25 2023 13_56_57 GMT+0200 (Central European Summer Time)_Fri May 22 2026 00_00_00 GMT+0200 (Central European Summer Time).csv" \
       /workspaces/.planning/v1.7/notes/discord-chat-full.csv

If the .~lock.fs_an_notes.odt# LibreOffice lock file is present at `/workspaces/`, leave it alone (the operator may have the ODT open; the lock is harmless and will be cleared by LibreOffice).

Per D-12: these raw files stay gitignored. The committed deliverable is `CHAT-INTEL.md` (produced by Plan 02), not the raw dumps.
  </action>
  <verify>
    <automated>bash -c 'test -f /workspaces/.planning/v1.7/notes/fs_an_notes.odt && \
      test -f /workspaces/.planning/v1.7/notes/discord-chat-full.csv && \
      ! test -f /workspaces/fs_an_notes.odt && \
      ! ls /workspaces/Discord_chat_*.csv 2>/dev/null && \
      ODT_BYTES=$(stat -c %s /workspaces/.planning/v1.7/notes/fs_an_notes.odt) && \
      CSV_LINES=$(wc -l </workspaces/.planning/v1.7/notes/discord-chat-full.csv) && \
      echo "ODT bytes=$ODT_BYTES CSV lines=$CSV_LINES" && \
      test $ODT_BYTES -gt 1000 && \
      test $CSV_LINES -gt 100 && \
      git status --porcelain .planning/v1.7/notes/ | grep -v "\.md$" | grep -v "^$" | wc -l | xargs -I{} test {} -eq 0 && \
      echo "PASS"'</automated>
  </verify>
  <acceptance_criteria>
    - `/workspaces/.planning/v1.7/notes/fs_an_notes.odt` exists and is > 1000 bytes (non-empty ODT).
    - `/workspaces/.planning/v1.7/notes/discord-chat-full.csv` exists and has > 100 lines (per Research Finding #3 the file is ~10,663 lines).
    - `/workspaces/fs_an_notes.odt` and `/workspaces/Discord_chat_*.csv` no longer exist at the repo root (move, not copy).
    - `git status --porcelain .planning/v1.7/notes/` shows no non-`.md` files staged (gitignore rule from Task 1 is hiding them).
  </acceptance_criteria>
  <done>
    The two raw chat dumps are staged at `.planning/v1.7/notes/` with the canonical filenames, the originals are gone from the repo root, and neither file appears in `git status` (verifying Task 1's gitignore is hiding them correctly).
  </done>
</task>

</tasks>

<verification>
Plan 01 phase-gate subset (from `31-VALIDATION.md` §"Phase Gate Acceptance Criteria" check #1 — plan-scoped):

```bash
# Each must produce the expected verdict
git check-ignore -v .planning/v1.7/notes/CHAT-INTEL.md      # → NON-zero exit (not ignored)
git check-ignore -v .planning/v1.7/MODIFICATIONS.md         # → NON-zero exit (not ignored)
git check-ignore -v .planning/v1.7/upstream-rurp/.git/HEAD  # → matches .planning/v1.7/** (ignored)
git check-ignore -v .planning/v1.7/notes/fs_an_notes.odt    # → matches .planning/v1.7/** (ignored)
git check-ignore -v .planning/v1.7/notes/discord-chat-full.csv  # → matches .planning/v1.7/** (ignored)
# Smoke: nothing under .planning/v1.7/ except .md files appears in `git status`
git status --porcelain | grep '.planning/v1.7/' | grep -v '\.md$' | wc -l   # → 0
```

All commands above must produce the expected verdicts before this plan is considered complete.
</verification>

<success_criteria>
- Root `.gitignore` is 13 lines with the three-line corrected pattern (Research Finding #9, not D-11's broken two-line).
- `.planning/v1.7/upstream-rurp/` is a full clone with all remote branches + tags fetched (Research Finding #1 verifies `rev2.0`, `Rev2.1`, `Rev2.3` branches are present).
- `.planning/v1.7/notes/fs_an_notes.odt` and `.planning/v1.7/notes/discord-chat-full.csv` exist and the originals are gone from `/workspaces/`.
- `git status` shows the substrate gitignored cleanly — only `.md` files (none in this plan) would commit.
- No firmware/host-CLI commits; only `.gitignore` is staged.
</success_criteria>

<output>
After completion, create `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-01-SUMMARY.md` documenting:
- The exact three-line gitignore block as committed (so Plans 02–05 can trust it).
- The remote branch list returned by `git branch -r | grep -iE 'rev[ -]?[0-9]'` (so Plan 04 knows which rev-named branches exist).
- The byte/line sizes of the staged ODT + CSV (so Plan 02 knows what it's distilling from).
</output>

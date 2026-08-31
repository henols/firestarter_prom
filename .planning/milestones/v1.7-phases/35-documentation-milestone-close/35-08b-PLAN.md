---
phase: 35-documentation-milestone-close
plan: 08b
type: execute
wave: 7
depends_on: [35-08a]
files_modified:
  - .planning/phases/31-upstream-shield-archaeology/
  - .planning/phases/32-inter-rev-difference-capability-matrix/
  - .planning/phases/33-silkscreen-label-code-alias-migration/
  - .planning/phases/34-shield-version-detect-design-firmware-plumbing/
  - .planning/phases/35-documentation-milestone-close/
  - .planning/milestones/v1.7-phases/
autonomous: true
requirements: [MS-01]
must_haves:
  truths:
    - "Phase directories 31-* through 35-* archived under .planning/milestones/v1.7-phases/ via .planning/v1.7-archive.sh execution"
    - ".planning/phases/ no longer contains any 31-* through 35-* directories; v1.6 paused phases 26-*/29-* + v1.3 paused phases untouched"
    - "One atomic meta-repo commit captures the rename operations on v1.7-shield-investigation"
    - "Plan 08b SUMMARY itself lands in the archived path .planning/milestones/v1.7-phases/35-documentation-milestone-close/35-08b-SUMMARY.md (the phase dir was just moved by Task 1)"
  artifacts:
    - path: ".planning/milestones/v1.7-phases/"
      provides: "Archived phase 31-35 directories"
      contains: "35-documentation-milestone-close"
  key_links:
    - from: ".planning/phases/3[1-5]-* (pre-archive)"
      to: ".planning/milestones/v1.7-phases/3[1-5]-* (post-archive)"
      via: "bash .planning/v1.7-archive.sh — moves 5 directories using explicit per-phase glob enumeration validated by Plan 08a dry-run"
      pattern: "milestones/v1.7-phases/3[1-5]"
---

<objective>
Wave 7 destructive run — execute the live archive of phase directories 31-* through 35-* into `.planning/milestones/v1.7-phases/`. Split from Plan 08a so the destructive `mv` lands in its own commit, distinct from the paperwork-only commit.

Plan 08a built `.planning/v1.7-archive.sh` and validated it with `--dry-run`. Plan 08b runs it live and commits the resulting file moves.

Two deliverables:

1. **Live archive run** — `bash /workspaces/.planning/v1.7-archive.sh` (without `--dry-run`). Moves the 5 phase directories into `.planning/milestones/v1.7-phases/`. The script enforces explicit per-phase glob enumeration so paused-milestone directories (v1.6 26-*/29-*, v1.3 11-*/12-*) are NOT swept up. Plan 08a's dry-run verified this.

2. **Atomic meta-repo commit** — capture the 5 directory renames in ONE commit. Subject: `refactor(35-08b): archive v1.7 phase directories 31-35 to milestones/v1.7-phases/`. Body cites Plan 08a's archive script + dry-run outcome.

Note: this plan's own SUMMARY (`35-08b-SUMMARY.md`) is written into the archived directory `.planning/milestones/v1.7-phases/35-documentation-milestone-close/` because Task 1 moves the directory before Task 2 commits — by the time the SUMMARY is authored, the phase dir lives under `milestones/`. Same pattern is documented for Plan 09.

Purpose: Execute the destructive archive run + commit it cleanly in a separate commit from the paperwork.
Output: One meta-repo commit on `v1.7-shield-investigation` containing 5 directory renames.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/35-documentation-milestone-close/35-CONTEXT.md
@.planning/phases/35-documentation-milestone-close/35-08a-SUMMARY.md
@.planning/v1.7-archive.sh
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Run .planning/v1.7-archive.sh (LIVE) to move phase directories 31-35 to milestones/v1.7-phases/</name>
  <files>.planning/phases/31-* through .planning/phases/35-*, .planning/milestones/v1.7-phases/</files>
  <read_first>
    - .planning/v1.7-archive.sh (Plan 08a Task 1 finished file)
    - .planning/phases/35-documentation-milestone-close/35-08a-SUMMARY.md (dry-run preview)
  </read_first>
  <action>
    Run a final dry-run sanity check first: `bash /workspaces/.planning/v1.7-archive.sh --dry-run`. Confirm output lists 5 mv operations + "5 phase director(ies) would be archived" + exit code 0. If anything has drifted since Plan 08a (e.g., a new directory was created under `.planning/phases/3[1-5]-` that the script would now sweep up), STOP and investigate before proceeding.

    Then run LIVE: `bash /workspaces/.planning/v1.7-archive.sh`. Expected output:
    - 5 `moved: 3N-...` lines
    - "Archived 5 phase director(ies) to .planning/milestones/v1.7-phases/"
    - Next-steps echo with the v1.7 commit message template
    - Exit code 0

    Sanity-check the result: `ls /workspaces/.planning/milestones/v1.7-phases/` should show 5 directory entries (31-upstream-shield-archaeology, 32-inter-rev-difference-capability-matrix, 33-silkscreen-label-code-alias-migration, 34-shield-version-detect-design-firmware-plumbing, 35-documentation-milestone-close). `ls /workspaces/.planning/phases/` should NOT contain any 31/32/33/34/35 directories anymore (the v1.6 directories 26-* through 29-* + any v1.3 paused directories remain untouched).

    Verify the move did not capture any paused-milestone directories: `ls /workspaces/.planning/phases/ | grep -E '^(26|27|28|29|11|12|13|14)' | wc -l` should return ≥ 1 (v1.6/v1.3 paused phases preserved in active phases/ dir per STATE.md Paused Milestones).
  </action>
  <verify>
    <automated>ls /workspaces/.planning/milestones/v1.7-phases/ 2>/dev/null | grep -E '^(31|32|33|34|35)-' | wc -l | grep -q '^5$'</automated>
  </verify>
  <done>
    `.planning/milestones/v1.7-phases/` contains 5 directory entries (31-* through 35-*); `.planning/phases/` no longer contains 31-* through 35-* directories; paused v1.3 + v1.6 phase directories preserved untouched.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Atomic meta-repo commit for the live archive run</name>
  <files>.planning/phases/3[1-5]-* (deleted), .planning/milestones/v1.7-phases/3[1-5]-*/ (added)</files>
  <read_first>
    - .planning/milestones/v1.7-phases/35-documentation-milestone-close/35-08b-SUMMARY.md (in-progress)
  </read_first>
  <action>
    Stage the rename operations from the meta-repo working directory:

    ```
    cd /workspaces
    git add .planning/milestones/v1.7-phases/
    git add -u .planning/phases/  # stage the directory removals
    ```

    At this point Phase 35 plan files (35-01-PLAN.md, 35-02-PLAN.md, etc., including this one) are now under `.planning/milestones/v1.7-phases/35-documentation-milestone-close/` — they were just archived in Task 1. The commit captures the move as a series of renames.

    Verify the stage with `git status`:
    - 5 directory trees show as renames from `.planning/phases/3N-*` → `.planning/milestones/v1.7-phases/3N-*`

    If `git status` shows new files instead of renames, that's fine — `git log --follow` will still trace the lineage and `git diff --find-renames` would surface the renames in review.

    Commit on `v1.7-shield-investigation`:
    - Subject: `refactor(35-08b): archive v1.7 phase directories 31-35 to milestones/v1.7-phases/`
    - Body cites Plan 08a's archive script + dry-run outcome; notes that paused v1.6/v1.3 phase directories are preserved by construction (explicit per-phase glob enumeration).
  </action>
  <verify>
    <automated>cd /workspaces && git log --oneline -1 | grep -q '35-08b'</automated>
  </verify>
  <done>
    One meta-repo commit on `v1.7-shield-investigation` with subject starting `refactor(35-08b):`; commit captures the 5 directory renames; `git ls-tree HEAD .planning/milestones/v1.7-phases/` lists 5 entries; `git ls-tree HEAD .planning/phases/` excludes 31-* through 35-* entries; sub-repo SHAs unchanged (Plan 08b is meta-repo only); Plan 09 ready to run.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| `.planning/v1.7-archive.sh` live run → phase directory archive | dry-run already validated in Plan 08a; live run repeats the dry-run check before the destructive operation |
| paused-milestone phase directories | preserved by construction — explicit per-phase glob enumeration prevents capture |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-35-17b | Tampering | live archive sweeps unintended directories | mitigate | Re-run --dry-run at the top of Task 1; abort if preview ≠ 5 phase dirs or includes any 26-*/29-*/11-*/12-* paths |
| T-35-23 | Repudiation | archived phase content lost | mitigate | `git mv`-equivalent moves preserve content; `git log --follow` traces lineage; archive directory is committed atomically |

No new threat surface — destructive operation already validated by Plan 08a dry-run.
</threat_model>

<verification>
- `.planning/milestones/v1.7-phases/` contains 5 archived phase directories
- `.planning/phases/` no longer contains 31-* through 35-* directories
- Paused v1.6 (26-* through 29-*) + v1.3 phase directories untouched
- One meta-repo commit on `v1.7-shield-investigation` with subject starting `refactor(35-08b):`
</verification>

<success_criteria>
- D-14 honored: phase directories physically archived under milestones/v1.7-phases/
- Paused-milestone substrate untouched
- Plan 09 hand-off ready: sub-repo work + meta-repo paperwork + phase archive all in place; only sub-repo beta → main + close commit remain
</success_criteria>

<output>
Create `.planning/milestones/v1.7-phases/35-documentation-milestone-close/35-08b-SUMMARY.md` when done — note that the SUMMARY itself lands in the just-archived phase directory. Document: live archive script output (5 moved lines), final phases/ contents (paused milestones only), commit SHA.
</output>

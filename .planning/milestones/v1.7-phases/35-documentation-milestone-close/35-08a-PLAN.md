---
phase: 35-documentation-milestone-close
plan: 08a
type: execute
wave: 6
depends_on: [35-06, 35-07]
files_modified:
  - .planning/v1.7-archive.sh
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
  - .planning/milestones/v1.7-REQUIREMENTS.md
  - .planning/todos/pending/photograph-modified-rev-0.md
  - .planning/todos/pending/write-modifications-md-rework-trace.md
autonomous: true
requirements: [MS-01]
must_haves:
  truths:
    - "NEW: .planning/v1.7-archive.sh exists, mirrors .planning/v1.4-archive.sh pattern with phase number array 31-35 per D-14; --dry-run sanity check exits 0"
    - "ROADMAP.md v1.7 section collapsed to <details>/<summary> block per D-15"
    - "NEW: .planning/milestones/v1.7-REQUIREMENTS.md exists as archive of .planning/REQUIREMENTS.md per D-15 (git mv preserves blame)"
    - ".planning/REQUIREMENTS.md REMOVED from live planning surface per D-15"
    - "NEW: .planning/todos/pending/photograph-modified-rev-0.md + write-modifications-md-rework-trace.md created per D-07"
    - "One atomic meta-repo commit covers all paperwork; no live archive script execution in this plan (Plan 08b handles)"
  artifacts:
    - path: ".planning/v1.7-archive.sh"
      provides: "Phase archive script (mirror of v1.4-archive.sh)"
      contains: "PHASE_GLOBS"
    - path: ".planning/milestones/v1.7-REQUIREMENTS.md"
      provides: "REQUIREMENTS archive with v1.5-REQUIREMENTS.md header pattern"
      contains: "Requirements Archive: v1.7"
    - path: ".planning/todos/pending/photograph-modified-rev-0.md"
      provides: "D-07 post-v1.7 todo #1"
      contains: "Phase 31 follow-up #3"
    - path: ".planning/todos/pending/write-modifications-md-rework-trace.md"
      provides: "D-07 post-v1.7 todo #2"
      contains: "Phase 31 follow-up #4"
  key_links:
    - from: ".planning/REQUIREMENTS.md (deleted)"
      to: ".planning/milestones/v1.7-REQUIREMENTS.md"
      via: "git mv preserves blob; new file has archive header prepended"
      pattern: "Requirements Archive: v1.7"
    - from: ".planning/v1.7-archive.sh PHASE_GLOBS"
      to: "Plan 08b (live run)"
      via: "explicit per-phase glob enumeration 31-* through 35-*; safety against accidental capture of paused v1.6 phases 26-* / 29-*"
      pattern: "31-.*32-.*33-.*34-.*35-"
---

<objective>
Wave 6 paperwork — the scaffolding side of the v1.7 close archive operations. Split from the prior monolithic Plan 08 to honor the ≤5-task scope-sanity rule and separate the deterministic paperwork (this plan) from the destructive live-archive `mv` (Plan 08b).

Five deliverables:

1. **`.planning/v1.7-archive.sh`** (D-14) — copy `.planning/v1.4-archive.sh` verbatim, edit the PHASE_GLOBS array from `15-* through 20-*` to `31-* through 35-*`, find/replace `v1.4` → `v1.7` throughout, update destination path to `.planning/milestones/v1.7-phases/`, update next-steps echo commit message. CRITICAL safety: explicit-per-phase glob enumeration prevents accidental capture of v1.6 paused phases (`26-*` through `29-*`) which still live in `.planning/phases/` per STATE.md Paused Milestones. Run `--dry-run` to verify the script previews the correct 5 mv operations + exits 0. DO NOT run live — Plan 08b handles that.

2. **`.planning/ROADMAP.md` v1.7 section → `<details>`** (D-15) — wrap the existing v1.7 section in a `<details><summary>` block. Top bullet at line 12 flips from `🚧 STARTED 2026-05-22` to `✅ shipped 2026-05-XX`. Mirror of v1.5 ROADMAP collapse pattern.

3. **`.planning/REQUIREMENTS.md` → `.planning/milestones/v1.7-REQUIREMENTS.md`** (D-15) — `git mv` the active REQUIREMENTS file to the milestones archive directory; prepend an 8-line archive header (mirror of `.planning/milestones/v1.5-REQUIREMENTS.md:1-8`); the active `.planning/REQUIREMENTS.md` is removed from the live planning surface.

4. **Two new post-v1.7 todos** (D-07):
   - `.planning/todos/pending/photograph-modified-rev-0.md` — Phase 31 follow-up #3.
   - `.planning/todos/pending/write-modifications-md-rework-trace.md` — Phase 31 follow-up #4. Depends on the photograph todo above.

5. **Atomic meta-repo commit** covering all four deliverables in ONE commit. No phase directories are physically moved in this plan; they remain in `.planning/phases/` until Plan 08b runs the live archive script.

Purpose: Build + validate the archive script and prepare the planning-surface paperwork; defer the destructive `mv` to Plan 08b so it lands in its own wave with its own commit.
Output: One meta-repo commit on `v1.7-shield-investigation` containing all paperwork edits; no phase directory moves.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/35-documentation-milestone-close/35-CONTEXT.md
@.planning/phases/35-documentation-milestone-close/35-PATTERNS.md
@.planning/v1.4-archive.sh
@.planning/milestones/v1.5-REQUIREMENTS.md
@.planning/REQUIREMENTS.md
@.planning/ROADMAP.md
@.planning/todos/pending/large-read-data-jitter-uno328pb.md
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Create .planning/v1.7-archive.sh by copy-and-edit from v1.4-archive.sh (D-14)</name>
  <files>.planning/v1.7-archive.sh</files>
  <read_first>
    - .planning/v1.4-archive.sh (full file — verbatim copy basis)
    - .planning/phases/35-documentation-milestone-close/35-CONTEXT.md (D-14)
    - .planning/phases/35-documentation-milestone-close/35-PATTERNS.md (Cluster 7 — archive script pattern lines 405-442)
  </read_first>
  <action>
    Copy `.planning/v1.4-archive.sh` to `.planning/v1.7-archive.sh`. Edit:

    1. PHASE_GLOBS array (lines ~74-81 in v1.4-archive.sh): replace 6 entries `15-`* through `20-`* with 5 entries `31-`* through `35-`*.

    2. All `v1.4` references → `v1.7` throughout: header comment block, usage line, error messages, destination path (`v1.4-phases` → `v1.7-phases`), pre-flight error message (`15-* through 20-*` → `31-* through 35-*`), next-steps echo commit message.

    3. T-20-03 mitigation citation: update to "T-35-17 mitigation: explicit enumeration prevents accidental capture of paused v1.6 phases (26-* through 29-*) or paused v1.3 phases".

    4. Final next-steps echo: update the commit message template to "refactor: archive v1.7 phase directories to milestones/v1.7-phases/".

    Make executable: `chmod +x /workspaces/.planning/v1.7-archive.sh`.

    Test with --dry-run: `bash /workspaces/.planning/v1.7-archive.sh --dry-run`. Expected output:
    - `[dry-run] mkdir -p .planning/milestones/v1.7-phases`
    - 5 `[dry-run] mv .planning/phases/3N-... .planning/milestones/v1.7-phases/` lines
    - `[dry-run] No changes made. 5 phase director(ies) would be archived.`

    Exit code 0. DO NOT run live — Plan 08b owns the live archive run.
  </action>
  <verify>
    <automated>test -x /workspaces/.planning/v1.7-archive.sh && bash /workspaces/.planning/v1.7-archive.sh --dry-run 2>&1 | tail -3 | grep -q 'No changes made'</automated>
  </verify>
  <done>
    `.planning/v1.7-archive.sh` exists + executable; --dry-run exits 0 and previews 5 phase mv operations; grep returns 0 for `v1.4` (all replaced); grep returns 5 for `PHASES_DIR/3[1-5]-`.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Collapse ROADMAP.md v1.7 section to details/summary (D-15)</name>
  <files>.planning/ROADMAP.md</files>
  <read_first>
    - .planning/ROADMAP.md (lines 1-300 — locate v1.7 section + top milestone bullet)
    - .planning/phases/35-documentation-milestone-close/35-PATTERNS.md (Cluster 8 ROADMAP collapse pattern lines 448-456)
  </read_first>
  <action>
    Open `.planning/ROADMAP.md`. Two edits:

    Edit 1 — Top milestone bullet at line 12: current text reads `🚧 **v1.7 RURP Shield Hardware Investigation & Version Detection** — Phases 31-35 (STARTED 2026-05-22). Catalog every known RURP shield revision …`. Replace with: `✅ **v1.7 RURP Shield Hardware Investigation & Version Detection** — Phases 31-35 (shipped 2026-05-XX; ship tag 3.0.0b5 both sub-repos; canonical reference .planning/v1.7-SHIELD-REVS.md; operator-facing copy firestarter/doc/SHIELD-REVISIONS.md).`

    Edit 2 — Wrap v1.7 section in `<details>`: locate `## v1.7 — RURP Shield Hardware Investigation & Version Detection (STARTED 2026-05-22)` heading (around line 14). Section runs through the Coverage table + Phase 31..35 details — ends just before `## v1.6 — Fix the Read Bug (PAUSED 2026-05-22)` section header (around line 163).

    Insert IMMEDIATELY BEFORE the `## v1.7 …` line:
    ```
    <details>
    <summary>v1.7 — RURP Shield Hardware Investigation & Version Detection (Shipped 2026-05-XX) — full milestone detail (collapsed)</summary>

    ```

    Insert IMMEDIATELY BEFORE the next section heading (`## v1.6 — Fix the Read Bug (PAUSED 2026-05-22)`):
    ```

    </details>

    ```

    Update the wrapped section header to `## v1.7 — RURP Shield Hardware Investigation & Version Detection (Shipped 2026-05-XX)`.

    v1.6 + v1.5 + v1.3 + Prior Milestones sections all stay UNCHANGED.
  </action>
  <verify>
    <automated>grep -c '^<details>' /workspaces/.planning/ROADMAP.md</automated>
  </verify>
  <done>
    `.planning/ROADMAP.md` has at least 1 new `<details>` block wrapping v1.7; top milestone bullet shows `✅ v1.7 ... shipped`; v1.7 section header reads `Shipped 2026-05-XX`; v1.6 + v1.5 + earlier sections unmodified.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: Archive .planning/REQUIREMENTS.md → .planning/milestones/v1.7-REQUIREMENTS.md (D-15)</name>
  <files>.planning/REQUIREMENTS.md, .planning/milestones/v1.7-REQUIREMENTS.md</files>
  <read_first>
    - .planning/REQUIREMENTS.md (the current active file — full content)
    - .planning/milestones/v1.5-REQUIREMENTS.md (lines 1-8 — archive header template)
    - .planning/phases/35-documentation-milestone-close/35-PATTERNS.md (Cluster 8 REQUIREMENTS archive pattern lines 458-481)
  </read_first>
  <action>
    Per D-15 + Cluster 8 pattern:

    1. `cd /workspaces && git mv .planning/REQUIREMENTS.md .planning/milestones/v1.7-REQUIREMENTS.md` — preserves git blame; `git log --follow` traces the file through the move.

    2. Edit the new file at `.planning/milestones/v1.7-REQUIREMENTS.md`: prepend an 8-line archive header (mirror of `.planning/milestones/v1.5-REQUIREMENTS.md:1-8`) BEFORE the existing `# Requirements — Milestone v1.7: …` heading. The header content:

    ```
    # Requirements Archive: v1.7 RURP Shield Hardware Investigation & Version Detection

    **Archived:** 2026-05-XX
    **Status:** SHIPPED

    For current requirements, see `.planning/REQUIREMENTS.md`.

    ---

    ```

    Then the existing body content (starting with `# Requirements — Milestone v1.7: ...`) preserved verbatim.

    Verify with `head -10 .planning/milestones/v1.7-REQUIREMENTS.md` that the archive header is at the top and the existing content starts after the `---` separator at line 7-8.

    3. After the move + header prepend, `.planning/REQUIREMENTS.md` no longer exists in the meta-repo's tracked tree. v1.6 resume reads REQUIREMENTS from `.planning/milestones/v1.6-paused/v1.6-REQUIREMENTS.md` (doesn't exist yet per D-15 — operator may create as part of v1.6 resume; out of Phase 35 scope, explicitly cited in STATE.md Operator Next Steps).
  </action>
  <verify>
    <automated>test ! -f /workspaces/.planning/REQUIREMENTS.md && test -f /workspaces/.planning/milestones/v1.7-REQUIREMENTS.md && head -1 /workspaces/.planning/milestones/v1.7-REQUIREMENTS.md | grep -q 'Requirements Archive: v1.7'</automated>
  </verify>
  <done>
    `.planning/REQUIREMENTS.md` no longer exists in the working tree; `.planning/milestones/v1.7-REQUIREMENTS.md` exists with 8-line archive header preceding the existing milestone content; `git log --follow .planning/milestones/v1.7-REQUIREMENTS.md` shows the file lineage from .planning/REQUIREMENTS.md.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 4: Create the two new post-v1.7 todos per D-07</name>
  <files>.planning/todos/pending/photograph-modified-rev-0.md, .planning/todos/pending/write-modifications-md-rework-trace.md</files>
  <read_first>
    - .planning/todos/pending/large-read-data-jitter-uno328pb.md (template — frontmatter + section layout)
    - .planning/phases/35-documentation-milestone-close/35-CONTEXT.md (D-07)
    - .planning/phases/35-documentation-milestone-close/35-PATTERNS.md (Cluster 9 new-todo pattern lines 486-513)
  </read_first>
  <action>
    Create both new todos under `.planning/todos/pending/` using the `large-read-data-jitter-uno328pb.md` file as the canonical frontmatter+body template.

    **Todo 1 — `photograph-modified-rev-0.md`:**

    Frontmatter fields:
    - id: photograph-modified-rev-0
    - title: Photograph operator's Modified Rev 0 board (Phase 31 follow-up #3)
    - captured: 2026-05-XX (Wave 8 close date — Plan 09 finalizes)
    - status: pending
    - type: documentation
    - target_milestone: post-v1.7
    - priority: MEDIUM
    - related_phase: 31
    - resolves_phase_followups: [Phase 31 follow-up #3]
    - deferred_from: Phase 35 (per Phase 35 CONTEXT.md D-07)

    Body sections (verbatim):
    - Title heading
    - `## The deferral` — D-07 rationale: rework trace independent of v1.7 detect-fw substrate; operator's Modified Rev 0 uses EEPROM `hw_revision` override path regardless of how rework cuts/jumpers landed
    - `## What's needed` — top.jpg, bottom.jpg, silkscreen.jpg, rework-cuts.jpg, rework-jumpers.jpg under `.planning/v1.7/photos/rev-0-modified/`
    - `## Sentinel cross-references (preserve verbatim per Phase 35 D-Discretion)` — list .planning/v1.7-SHIELD-REVS.md §1 row 4 + §4 row 8 + §5 row 7 + §6 row 91 sentinels per Pattern E preservation
    - `## When to triage` — at next milestone-start sweep; grep for `pending Phase 35` in v1.7-SHIELD-REVS.md
    - `## Cross-references` — memory `[[user_shield_revisions]]`, Phase 35 D-07, Phase 31 Plan 05, companion todo

    **Todo 2 — `write-modifications-md-rework-trace.md`:**

    Frontmatter fields:
    - id: write-modifications-md-rework-trace
    - title: Write full MODIFICATIONS.md rework trace for operator's Modified Rev 0 (Phase 31 follow-up #4)
    - captured: 2026-05-XX
    - status: pending
    - type: documentation
    - target_milestone: post-v1.7
    - priority: MEDIUM
    - related_phase: 31
    - resolves_phase_followups: [Phase 31 follow-up #4]
    - deferred_from: Phase 35 (per Phase 35 CONTEXT.md D-07)
    - depends_on: photograph-modified-rev-0

    Body sections:
    - Title
    - `## The deferral` — depends on companion photograph todo; rework trace requires photos as evidentiary substrate
    - `## What's needed` — per-rework-entry trace against upstream Rev 0 schematic blob `d2a7f691` on `origin/rev2.0`; document cut + jumper + rationale + capability matrix delta; output goes to `.planning/v1.7/MODIFICATIONS.md` (currently a stub created in Phase 31)
    - `## Sentinel resolution` — once both todos resolve, upgrade .planning/v1.7-SHIELD-REVS.md §1 row 4 + §4 row 8 + §5 row 7 + §6 row 91 from `as-modified — pending Phase 35` to bench-verified state
    - `## When to triage` — AFTER `photograph-modified-rev-0.md` resolves
    - `## Cross-references` — Phase 35 D-07, Phase 31 Plan 05, upstream Rev 0 schematic blob ref, companion (predecessor) todo

    Save both files.
  </action>
  <verify>
    <automated>test -f /workspaces/.planning/todos/pending/photograph-modified-rev-0.md && test -f /workspaces/.planning/todos/pending/write-modifications-md-rework-trace.md</automated>
  </verify>
  <done>
    Both new todos exist with full frontmatter + 5 body sections each; cross-references to sentinel rows in v1.7-SHIELD-REVS.md present; companion todo refs intact.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 5: Atomic meta-repo commit for Plan 08a paperwork</name>
  <files>.planning/v1.7-archive.sh, .planning/ROADMAP.md, .planning/REQUIREMENTS.md (removed), .planning/milestones/v1.7-REQUIREMENTS.md, .planning/todos/pending/photograph-modified-rev-0.md, .planning/todos/pending/write-modifications-md-rework-trace.md</files>
  <read_first>
    - .planning/phases/35-documentation-milestone-close/35-08a-SUMMARY.md (in-progress)
  </read_first>
  <action>
    Stage all Plan 08a paperwork changes from the meta-repo working directory:

    ```
    cd /workspaces
    git add .planning/v1.7-archive.sh
    git add .planning/ROADMAP.md
    git add .planning/milestones/v1.7-REQUIREMENTS.md
    git add .planning/todos/pending/photograph-modified-rev-0.md
    git add .planning/todos/pending/write-modifications-md-rework-trace.md
    git add -u .planning/REQUIREMENTS.md  # stage the deletion from git mv
    ```

    Verify the stage with `git status`:
    - `.planning/v1.7-archive.sh` — new file
    - `.planning/ROADMAP.md` — modified (v1.7 collapsed)
    - `.planning/REQUIREMENTS.md` → `.planning/milestones/v1.7-REQUIREMENTS.md` — renamed (with header content modification)
    - `.planning/todos/pending/photograph-modified-rev-0.md` — new file
    - `.planning/todos/pending/write-modifications-md-rework-trace.md` — new file

    No phase directories should appear in this commit — Plan 08b runs the live archive script later.

    Commit on `v1.7-shield-investigation`:
    - Subject: `refactor(35-08a): build v1.7 archive script + collapse ROADMAP + move REQUIREMENTS + 2 post-v1.7 todos (D-07 + D-14 + D-15)`
    - Body cites: D-07 (2 new pending todos preserving Pattern E sentinel cross-refs); D-14 (`.planning/v1.7-archive.sh` 4-line edit pattern + dry-run validated); D-15 (ROADMAP.md `<details>` collapse + REQUIREMENTS.md → archive). Note that live archive run is deferred to Plan 08b.
  </action>
  <verify>
    <automated>cd /workspaces && git log --oneline -1 | grep -q '35-08a'</automated>
  </verify>
  <done>
    One meta-repo commit on `v1.7-shield-investigation` with subject starting `refactor(35-08a):`; commit covers the 5 paperwork deliverables (script + ROADMAP + REQUIREMENTS move + 2 todos); no phase directory moves yet; Plan 08b ready to run.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| `.planning/v1.7-archive.sh` glob expansion → phase directory archive | explicit per-phase enumeration prevents accidental capture of paused-milestone phase dirs (v1.6 26-* / 29-*, v1.3 11-* / 12-*); dry-run validated in Task 1 |
| `git mv REQUIREMENTS.md` → archive | git blame preserved; `git log --follow` traces lineage |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-35-17 | Tampering | accidental capture of paused-milestone phase dirs | mitigate | `.planning/v1.7-archive.sh` uses explicit per-phase glob array (NOT a wide wildcard); --dry-run validation in Task 1 confirms only 5 v1.7 dirs would move; live run gated to Plan 08b |
| T-35-18 | Repudiation | REQUIREMENTS history lost | mitigate | `git mv` preserves blob; archive header prepend in same commit; `git log --follow` shows the lineage |
| T-35-19 | Repudiation | sentinel-deferred work lost | mitigate | Two new pending todos with sentinel cross-references preserve the deferred items for future RCA / milestone-start sweeps |

No new threat surface — meta-repo paperwork + safe in-tree file moves.
</threat_model>

<verification>
- `.planning/v1.7-archive.sh` exists + executable; --dry-run exits 0 and previews 5 mv operations
- `.planning/ROADMAP.md` has `<details>` block wrapping v1.7 section; top milestone bullet reads `✅ shipped`
- `.planning/REQUIREMENTS.md` no longer exists in working tree
- `.planning/milestones/v1.7-REQUIREMENTS.md` exists with archive header
- `.planning/todos/pending/photograph-modified-rev-0.md` + `write-modifications-md-rework-trace.md` exist with proper frontmatter + body
- `.planning/phases/31-* through 35-*` UNTOUCHED — Plan 08b handles physical archive
- One meta-repo commit on `v1.7-shield-investigation` with subject starting `refactor(35-08a):`
</verification>

<success_criteria>
- D-07 + D-14 + D-15 paperwork honored
- Archive script built + dry-run validated; ready for Plan 08b live run
- Paused-milestone substrate untouched
- Plan 08b dependency satisfied — script + paperwork present, only live mv + commit remain
</success_criteria>

<output>
Create `.planning/phases/35-documentation-milestone-close/35-08a-SUMMARY.md` when done. Document: dry-run output (5 mv operations previewed), ROADMAP collapse line ranges, REQUIREMENTS archive line count, both new todos created, archive script ready for Plan 08b live execution.
</output>

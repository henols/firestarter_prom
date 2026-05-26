---
phase: 31
plan: 03
type: execute
wave: 2
depends_on: [01]
files_modified:
  - .planning/v1.7/photos/rev-2-2/   # gitignored substrate (operator-photographed; never committed)
  - .planning/v1.7/photos/rev-2-0/   # gitignored substrate
autonomous: false
requirements_addressed: [HW-INV-03, SILK-01]
requirements: [HW-INV-03, SILK-01]
must_haves:
  truths:
    - "Operator's Rev 2.2 board is photographed with at least top.jpg + bottom.jpg + silkscreen.jpg, silkscreen text readable at 100% crop."
    - "Operator's Rev 2.0 board is photographed with the same three mandatory shots."
    - "Silkscreen-version strings (column 1 of the D-10 inventory table) are captured verbatim from the silkscreen.jpg macros — including capitalization, spacing, and periods (per SILK-01)."
    - "Per memory `[[user_shield_revisions]]`: operator owns these revs (Rev 2.2 + Rev 2.0); each is a distinct physical board with a distinct silkscreen-version string."
  artifacts:
    - path: ".planning/v1.7/photos/rev-2-2/top.jpg"
      provides: "Rev 2.2 board top view"
    - path: ".planning/v1.7/photos/rev-2-2/bottom.jpg"
      provides: "Rev 2.2 board bottom view"
    - path: ".planning/v1.7/photos/rev-2-2/silkscreen.jpg"
      provides: "Rev 2.2 silkscreen macro (drives SILK-01 verbatim capture)"
    - path: ".planning/v1.7/photos/rev-2-0/top.jpg"
      provides: "Rev 2.0 board top view"
    - path: ".planning/v1.7/photos/rev-2-0/bottom.jpg"
      provides: "Rev 2.0 board bottom view"
    - path: ".planning/v1.7/photos/rev-2-0/silkscreen.jpg"
      provides: "Rev 2.0 silkscreen macro"
  key_links:
    - from: ".planning/v1.7-SHIELD-REVS.md §1 Inventory (photo_dir column)"
      to: ".planning/v1.7/photos/rev-2-2/, .planning/v1.7/photos/rev-2-0/"
      via: "verbatim path citation (per D-10 column 8 + Research Finding #4 slug derivation rule)"
      pattern: '\.planning/v1\.7/photos/rev-2-(2|0)/'
---

<objective>
Operator photographs the Rev 2.2 + Rev 2.0 boards in one sitting (these two are NOT rework-traced — they're stock revs; the Modified Rev 0 lives in Plan 05 because its rework annotation needs the upstream Rev 0 schematic recovered in Plan 04). Each board produces at least top.jpg + bottom.jpg + silkscreen.jpg under `.planning/v1.7/photos/<rev-slug>/`. The silkscreen.jpg is load-bearing — it's the SILK-01 evidence that anchors the inventory's `silkscreen` column (D-10 column 1).

Purpose: Phase 32 cannot do an inter-rev electrical/mechanical difference table without knowing what each operator-on-hand board actually IS; the silkscreen string is the canonical ID across the whole milestone. Phase 33's alias migration depends on having the silkscreen labels (e.g. `VPP_EN`, `A14`) literally readable from these photos. Plan 04 (mine + scaffold) and Plan 05 (inventory fill) both consume these as their `photo_dir` column inputs.

Output: Two gitignored directories under `.planning/v1.7/photos/` containing the minimum 6 JPGs (3 per rev). Filenames follow the Finding #4 convention exactly so phase-gate check #3 passes.

**Autonomous: false** — this plan requires the operator to physically photograph two boards. Plan execution pauses for the operator at the checkpoint task; no automation can substitute (no API, no CLI — `[[feedback_chip_out_before_sideload]]` is irrelevant here since no firmware sideload; just photos).
</objective>

<execution_context>
@/workspaces/.claude/get-shit-done/workflows/execute-plan.md
@/workspaces/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@/workspaces/.planning/phases/31-upstream-shield-archaeology/31-CONTEXT.md
@/workspaces/.planning/phases/31-upstream-shield-archaeology/31-RESEARCH.md
@/workspaces/.planning/phases/31-upstream-shield-archaeology/31-PATTERNS.md
@/workspaces/.planning/phases/31-upstream-shield-archaeology/31-VALIDATION.md
@/workspaces/.planning/phases/31-upstream-shield-archaeology/31-01-substrate-and-gitignore-PLAN.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create photo-directory skeletons for Rev 2.2 + Rev 2.0</name>
  <files>
    /workspaces/.planning/v1.7/photos/rev-2-2/
    /workspaces/.planning/v1.7/photos/rev-2-0/
  </files>
  <read_first>
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-RESEARCH.md` §Finding #4 ("Slug derivation rule": lowercase, replace ` ` + `.` with `-`, strip leading "rurp-" if present — so `RURP Rev 2.2` → `rev-2-2`; `RURP Rev 2.0` → `rev-2-0`)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-PATTERNS.md` §"Gitignored substrate" → photos row (3-file minimum per dir, paths cited from §1 inventory's photo_dir column)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-01-substrate-and-gitignore-PLAN.md` Task 1 (confirms `.planning/v1.7/**` rule hides these dirs from git)
  </read_first>
  <action>
Create the two empty directories so the operator has explicit landing slots:

    mkdir -p /workspaces/.planning/v1.7/photos/rev-2-2
    mkdir -p /workspaces/.planning/v1.7/photos/rev-2-0

The slugs `rev-2-2` and `rev-2-0` follow Research Finding #4's derivation rule applied to silkscreen strings `RURP Rev 2.2` and `RURP Rev 2.0` (the expected upstream forms). If the operator's silkscreen photos in Task 2 reveal a different verbatim string (e.g. `RURP Rev 2.2` vs `Rev 2.2` — capitalization or prefix difference), the slug stays as-is (the slug is filename-safe shorthand; the verbatim string lives in the D-10 column 1, Plan 05).

No files are placed in the dirs yet — Task 2's operator checkpoint populates them.
  </action>
  <verify>
    <automated>bash -c 'test -d /workspaces/.planning/v1.7/photos/rev-2-2 && \
      test -d /workspaces/.planning/v1.7/photos/rev-2-0 && \
      ! git check-ignore -q /workspaces/.planning/v1.7/photos/.placeholder 2>/dev/null; \
      git check-ignore -v /workspaces/.planning/v1.7/photos/rev-2-2/probe.jpg 2>&1 | grep -q "\.planning/v1\.7" && \
      echo "PASS"'</automated>
  </verify>
  <acceptance_criteria>
    - `/workspaces/.planning/v1.7/photos/rev-2-2/` exists as a directory.
    - `/workspaces/.planning/v1.7/photos/rev-2-0/` exists as a directory.
    - `git check-ignore -v /workspaces/.planning/v1.7/photos/rev-2-2/probe.jpg` returns 0 and prints the `.planning/v1.7/**` rule (Plan 01's gitignore is hiding photos correctly).
  </acceptance_criteria>
  <done>
    Two empty operator-target dirs are ready, both correctly hidden by `.gitignore`.
  </done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 2: Operator photographs Rev 2.2 + Rev 2.0 (3 mandatory shots per board)</name>
  <files>
    /workspaces/.planning/v1.7/photos/rev-2-2/top.jpg
    /workspaces/.planning/v1.7/photos/rev-2-2/bottom.jpg
    /workspaces/.planning/v1.7/photos/rev-2-2/silkscreen.jpg
    /workspaces/.planning/v1.7/photos/rev-2-0/top.jpg
    /workspaces/.planning/v1.7/photos/rev-2-0/bottom.jpg
    /workspaces/.planning/v1.7/photos/rev-2-0/silkscreen.jpg
  </files>
  <read_first>
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-RESEARCH.md` §Finding #4 (the full content checklist: top/bottom/silkscreen + format JPEG + ambient + oblique-angle lighting + resolution floor "silkscreen readable at 100% crop")
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-VALIDATION.md` §"Manual-Only Verifications" row 1 (SILK-01 verbatim-fidelity is operator-attested at commit time)
  </read_first>
  <what-built>
    Two empty target directories at `.planning/v1.7/photos/rev-2-2/` and `.planning/v1.7/photos/rev-2-0/`, ready for operator-supplied JPGs.
  </what-built>
  <how-to-verify>
    Operator photographs both boards in one session:

    **Rev 2.2 board (operator's stock Rev 2.2):**
    1. `top.jpg` — full top view, oriented so the silkscreen-version string is readable in the frame. JPEG, phone camera, native resolution.
    2. `bottom.jpg` — full bottom view.
    3. `silkscreen.jpg` — macro of the silkscreen-version region (the spot on the PCB that says something like "RURP Rev 2.2"). MUST be readable at 100% crop — this is the SILK-01 evidence; the verbatim string from this photo lands in the D-10 column 1 of Plan 05's inventory fill.

    **Rev 2.0 board (operator's stock Rev 2.0):**
    4. `top.jpg` — same convention.
    5. `bottom.jpg`
    6. `silkscreen.jpg` — macro of the silkscreen-version region.

    Optional macros that improve Phase 32 + Phase 34 fidelity (not gating Plan 03, but operator may capture if convenient — same dir, names from Finding #4 §"Filename convention per `<rev-slug>/`"):
    - `socket-detail.jpg` (ZIF / DIP socket area)
    - `jp4-detail.jpg` (any jumpers / detect-resistor region — Phase 34 will care about this for the R41-on-A3 ground truth)

    Lighting: ambient + a single oblique-angle desk lamp for raking light over the silkscreen layer. Avoid direct overhead glare on solder mask. Stock phone JPEG quality; do not re-encode.

    Place files at the exact paths listed above. Filenames are case-sensitive (`top.jpg`, NOT `Top.JPG`).
  </how-to-verify>
  <resume-signal>Type "photos placed" when all 6 mandatory files exist at the listed paths. Or "blocked: <reason>" if any board is unavailable (per Research Finding §A3 assumption: if a board is missing, that row's `state` in Plan 05's inventory becomes `upstream-only` instead of `on-hand-photographed`, and Plan 03's checkpoint is partial-pass with the missing rev noted as a Phase 35 follow-up).</resume-signal>
  <acceptance_criteria>
    - `test -f /workspaces/.planning/v1.7/photos/rev-2-2/top.jpg` returns 0.
    - `test -f /workspaces/.planning/v1.7/photos/rev-2-2/bottom.jpg` returns 0.
    - `test -f /workspaces/.planning/v1.7/photos/rev-2-2/silkscreen.jpg` returns 0.
    - `test -f /workspaces/.planning/v1.7/photos/rev-2-0/top.jpg` returns 0.
    - `test -f /workspaces/.planning/v1.7/photos/rev-2-0/bottom.jpg` returns 0.
    - `test -f /workspaces/.planning/v1.7/photos/rev-2-0/silkscreen.jpg` returns 0.
    - Each file is > 50000 bytes (smoke check: phone JPEG; a 0-byte placeholder would fail).
    - `git status --porcelain | grep '.planning/v1.7/photos/'` returns no output (gitignore hides JPGs correctly).
  </acceptance_criteria>
</task>

</tasks>

<verification>
Plan 03 phase-gate subset (from `31-VALIDATION.md` §"Phase Gate Acceptance Criteria" check #3 — plan-scoped to the two photo dirs created here):

```bash
# Both photo dirs must exist with the three mandatory files each
for slug in rev-2-2 rev-2-0; do
  for required in top.jpg bottom.jpg silkscreen.jpg; do
    test -f ".planning/v1.7/photos/$slug/$required" || echo "MISSING: $slug/$required"
  done
done
# Output must be empty
```

Smoke that the gitignore symmetry from Plan 01 still holds:

```bash
git status --porcelain | grep '.planning/v1.7/photos/' | wc -l
# Output must be 0
```
</verification>

<success_criteria>
- Both `rev-2-2/` and `rev-2-0/` directories exist with the 3 mandatory JPGs each (6 files total).
- Silkscreen text is text-readable at 100% crop in both `silkscreen.jpg` macros (operator-attested; verifies SILK-01 evidence).
- Photos remain gitignored (Plan 01's pattern is symmetric).
- Operator has the verbatim silkscreen strings from the macros ready to type into Plan 05's inventory `silkscreen` column.
</success_criteria>

<output>
After completion, create `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-03-SUMMARY.md` documenting:
- The verbatim silkscreen strings the operator read off each `silkscreen.jpg` macro (e.g. `silkscreen_rev_2_2: "RURP Rev 2.2"`, `silkscreen_rev_2_0: "RURP Rev 2.0"` — exact characters from the PCB). Plan 05's inventory fill consumes these as D-10 column 1 input.
- Any optional macros captured (socket-detail.jpg, jp4-detail.jpg) so Phase 32/34 know they exist.
- Any deviations from the expected slug convention (e.g. if silkscreen actually says `Rev 2.0` instead of `RURP Rev 2.0` — operator notes the difference; slug stays `rev-2-0`).
</output>

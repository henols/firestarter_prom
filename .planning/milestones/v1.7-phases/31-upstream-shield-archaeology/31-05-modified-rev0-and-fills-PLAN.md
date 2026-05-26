---
phase: 31
plan: 05
type: execute
wave: 3
depends_on: [01, 02, 03, 04]
files_modified:
  - .planning/v1.7-SHIELD-REVS.md     # §1 + §2 + §3 row fills (scaffolded by Plan 04)
  - .planning/v1.7/MODIFICATIONS.md   # NEW — operator-attested Modified Rev 0 rework annotation
  - .planning/v1.7/photos/rev-0-modified/   # NEW — operator photos + rework macros
autonomous: false
requirements_addressed: [HW-INV-01, HW-INV-02, HW-INV-03, SILK-01]
requirements: [HW-INV-01, HW-INV-02, HW-INV-03, SILK-01]
must_haves:
  truths:
    - "Operator's Modified Rev 0 board is photographed + each rework region has its own `rework-N-<region>.jpg` macro."
    - "`MODIFICATIONS.md` traces each rework against the upstream Rev 0 schematic recovered by Plan 04 from `UniversalProgrammerRev0b0.zip`. Every `## Rework Region N` heading is paired with a `Cross-ref:` line (phase-gate check #5 contract)."
    - "Silkscreen-version strings (D-10 column 1) are captured verbatim — including capitalization, periods, and spacing — for all on-hand-photographed rows. SILK-01."
    - "Inventory `silkscreen` column uses the verbatim PCB text where photographable; uses `not-recovered` + the canonical `upstream-<short-sha>` ID per D-03 for revs whose silkscreen string isn't recoverable from upstream artifacts."
    - "Inventory `provenance` ∈ {on-main, removed-from-main}; `state` ∈ {on-hand-photographed, upstream-only} per D-02. Branch-archived citations (e.g. `branch-archived:origin/rev2.0`) live in the `removed_commit` column when no main-side deletion exists — per VALIDATION.md §Check #4 NOTE."
    - "§1 column order is verbatim from D-10 — NEVER reorder."
    - "Every `provenance=removed-from-main` row has a non-blank `removed_commit` (phase-gate check #4) — including the `branch-archived:origin/rev2.0` convention used when no main-side deletion happened."
    - "§4-§9 still carry their `<!-- OWNED BY PHASE 3X — TBD -->` markers — Plan 05 does not touch them."
    - "All 8 phase-gate checks from `31-VALIDATION.md` produce empty output at Plan 05 close."
  artifacts:
    - path: ".planning/v1.7/photos/rev-0-modified/top.jpg"
      provides: "Modified Rev 0 board top view"
    - path: ".planning/v1.7/photos/rev-0-modified/bottom.jpg"
      provides: "Modified Rev 0 board bottom view"
    - path: ".planning/v1.7/photos/rev-0-modified/silkscreen.jpg"
      provides: "Modified Rev 0 silkscreen macro"
    - path: ".planning/v1.7/MODIFICATIONS.md"
      provides: "Operator-attested rework trace per region, cross-referenced to upstream Rev 0 schematic"
      contains: "Cross-ref:"
      min_lines: 25
    - path: ".planning/v1.7-SHIELD-REVS.md (§1 + §2 + §3 filled)"
      provides: "Filled inventory rows + appendix + Anders R41-on-A3 table"
      contains: "on-hand-photographed"
  key_links:
    - from: ".planning/v1.7/MODIFICATIONS.md"
      to: "UniversalProgrammerRev0b0.zip::<schematic>.kicad_sch (mined in Plan 04)"
      via: "`Cross-ref:` line per `## Rework Region` heading"
      pattern: '^Cross-ref:.*UniversalProgrammerRev0b0\.zip::'
    - from: ".planning/v1.7-SHIELD-REVS.md §1 (filled rows)"
      to: ".planning/v1.7/photos/<rev-slug>/"
      via: "photo_dir column (D-10 column 8)"
      pattern: '\.planning/v1\.7/photos/'
    - from: ".planning/v1.7-SHIELD-REVS.md §3"
      to: ".planning/v1.7/notes/CHAT-INTEL.md §1 + mine-notes.md §Per-rev R41"
      via: "Schematic citation column + intro-paragraph cross-reference"
      pattern: 'CHAT-INTEL\.md|mine-notes\.md'
---

<objective>
Synthesis wave. Five tightly-coupled tasks land all remaining Phase 31 deliverables:

1. **Photograph the Modified Rev 0 board** with rework macros (depends on Plan 04 having recovered the upstream Rev 0 schematic from `UniversalProgrammerRev0b0.zip` so the operator has the cross-reference target in hand).
2. **Write `MODIFICATIONS.md`** with one `## Rework Region N` heading per identified cut/jumper + a `Cross-ref:` line citing the upstream schematic by zip-internal path.
3. **Fill §1 Inventory** in `.planning/v1.7-SHIELD-REVS.md` with one row per recoverable rev — verbatim silkscreen strings, photo_dirs pointing at Plan 03 + this plan's photos, schematic_path + gerber_path + commit metadata from `mine-notes.md`.
4. **Fill §2 Mentioned-but-not-recovered** with appendix rows for any rev cited by Anders (in CHAT-INTEL) but with no surviving schematic.
5. **Fill §3 Existing Detect-HW Scheme** with per-rev R41 + JP4 + A3 + topology + schematic citation rows from `mine-notes.md` §Per-rev R41.

Then run the full 8-check phase-gate suite to verify Plan 05 closes Phase 31 cleanly.

Purpose: This plan IS the Phase 31 synthesis pass. Plans 01-04 produced substrate (gitignore, clone, chat dumps, photos for 2 boards, mine output, scaffold); Plan 05 fills the canonical doc + the rework appendix + the third photo set. After Plan 05, the entire phase-gate is verifiable.

**Autonomous: false** — Task 1 requires the operator to physically photograph the Modified Rev 0 board AND trace its rework against the upstream Rev 0 schematic. The trace step is the load-bearing one — `MODIFICATIONS.md` cannot be written without the operator's visual inspection per D-06 + VALIDATION.md "Manual-Only Verifications" row 2.
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
@/workspaces/.planning/phases/31-upstream-shield-archaeology/31-02-chat-intel-PLAN.md
@/workspaces/.planning/phases/31-upstream-shield-archaeology/31-03-photos-rev22-rev20-PLAN.md
@/workspaces/.planning/phases/31-upstream-shield-archaeology/31-04-mine-and-scaffold-PLAN.md
</context>

<tasks>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 1: Operator photographs Modified Rev 0 board + traces rework</name>
  <files>
    /workspaces/.planning/v1.7/photos/rev-0-modified/top.jpg
    /workspaces/.planning/v1.7/photos/rev-0-modified/bottom.jpg
    /workspaces/.planning/v1.7/photos/rev-0-modified/silkscreen.jpg
    /workspaces/.planning/v1.7/photos/rev-0-modified/rework-1-*.jpg     # at least one rework macro
    /workspaces/.planning/v1.7/photos/rev-0-modified/rework-2-*.jpg     # if more than one rework region
  </files>
  <read_first>
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-CONTEXT.md` §D-05 (operator's third board IS a genuine Rev 0; silkscreen verbatim is canonical) + §D-06 (rework details traced visually during photo session; cross-reference each modification against upstream Rev 0 schematic)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-RESEARCH.md` §Finding #4 (file convention: `rework-N-<region>.jpg`, one macro per identified rework location, minimum 1 expected 2-4) + §Finding #6 (sequencing constraint: rework trace REQUIRES Plan 04 having recovered the upstream Rev 0 schematic — must be done first)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-04-SUMMARY.md` (where Plan 04 noted the exact zip-internal path to the Rev 0 schematic — typically `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch` per Research Finding #2)
    - Per memory `[[user_shield_revisions]]`: operator owns this board; per memory the rework relates to "hardware-bug-A/B"
  </read_first>
  <what-built>
    Plan 04 has recovered the upstream Rev 0 schematic (extracted from `UniversalProgrammerRev0b0.zip` on the `rev2.0` branch to a `/tmp/<rev-extract>` scratch dir during the mine). The schematic file path is recorded in `31-04-SUMMARY.md`. Operator now has the cross-reference target in hand.

    **Re-extraction recipe (run BEFORE photographing if `/tmp/rev0-extract/` is empty — `/tmp` self-cleans on devcontainer restart, and Plan 05's `autonomous: false` gap may span a restart):**

        # Verify the zip filename + branch ref against `31-04-SUMMARY.md` / `mine-notes.md` §Zip-archive listings
        # before running — the values below are the Research Finding #2 defaults.
        git -C /workspaces/.planning/v1.7/upstream-rurp show origin/rev2.0:hardware/UniversalProgrammerRev0b0.zip > /tmp/rev0.zip \
          && unzip -o /tmp/rev0.zip -d /tmp/rev0-extract/

    Operator now opens the extracted `.kicad_sch` in local KiCad (or reads the .sch text) to trace each rework against the as-drawn netlist.
  </what-built>
  <how-to-verify>
    Operator photographs the Modified Rev 0 board + traces each rework region:

    **Mandatory shots (mirror Plan 03's Rev 2.2 / Rev 2.0 convention):**
    1. `/workspaces/.planning/v1.7/photos/rev-0-modified/top.jpg`
    2. `/workspaces/.planning/v1.7/photos/rev-0-modified/bottom.jpg`
    3. `/workspaces/.planning/v1.7/photos/rev-0-modified/silkscreen.jpg` (verbatim string for D-10 column 1)

    **Rework macros — at least one per identified rework region:**
    4. `/workspaces/.planning/v1.7/photos/rev-0-modified/rework-1-<region>.jpg` — first identified cut/jumper. Name `<region>` is a short descriptor of where the rework lives (e.g. `rework-1-jp3.jpg`, `rework-1-vpp-rail.jpg`).
    5. (additional `rework-N-<region>.jpg` macros for each additional rework location)

    Per Research Finding #4 the minimum is 1 rework macro and the expected count is 2-4. The operator's memory `[[user_shield_revisions]]` mentions "hardware-bug-A/B" — that suggests two distinct rework regions; operator photographs whatever is visible on the board.

    **Trace step** — for each rework region, operator visually compares the cut/jumper on the PCB against the upstream Rev 0 schematic (the one Plan 04 extracted). Operator captures, for each region:
    - What was on the original (which net/component as drawn in the schematic).
    - What the rework changes it to (which net/component now connects where).
    - One- to two-sentence rationale (the rework's purpose per operator's recollection or notes).

    The trace text doesn't land in a file yet — Task 2 takes it and writes MODIFICATIONS.md. So when the operator signals back, they have the trace ready (notes / mental model) for Task 2.

    Lighting + format conventions: same as Plan 03 (ambient + oblique-angle desk lamp; native phone JPEG resolution; no re-encoding).
  </how-to-verify>
  <resume-signal>Type "modified rev 0 photographed; N rework regions identified" where N is the count of rework macros placed. Or "blocked: <reason>" if (a) the board has no visible rework (then `state` becomes `on-hand-photographed` with zero `rework-*.jpg` files — phase-gate check #5 still passes because `N_REFS >= 0`), (b) the board is unavailable (then this row's state in §1 becomes `upstream-only` and MODIFICATIONS.md becomes a stub noting the unavailability).</resume-signal>
  <acceptance_criteria>
    - `test -f /workspaces/.planning/v1.7/photos/rev-0-modified/top.jpg`, `bottom.jpg`, `silkscreen.jpg` all return 0.
    - At least one `rework-*.jpg` exists (or operator has explicitly signaled "no rework visible — see SUMMARY").
    - Each photo is > 50000 bytes.
    - `git status --porcelain | grep '.planning/v1.7/photos/'` returns no output (gitignore symmetry holds).
    - Operator has the rework trace ready as notes for Task 2 (cite-per-region against the upstream schematic).
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 2: Write `.planning/v1.7/MODIFICATIONS.md` from operator's rework trace</name>
  <files>/workspaces/.planning/v1.7/MODIFICATIONS.md</files>
  <read_first>
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-PATTERNS.md` §"`.planning/v1.7/MODIFICATIONS.md` — operator-attested rework appendix" (frontmatter pattern from `.planning/v1.5/baselines/CAPTURE-PROCEDURE.md` + per-region heading + the exact `Cross-ref:` line literal phase-gate check #5 contracts against)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-VALIDATION.md` §"Phase Gate Acceptance Criteria" check #5 (the grep contract: `grep -c '^Cross-ref:' MODIFICATIONS.md >= ls rework-*.jpg | wc -l`)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-04-SUMMARY.md` (the exact zip-internal schematic path to cite — typically `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch`)
    - `/workspaces/.planning/v1.7/photos/rev-0-modified/` directory listing (`ls rework-*.jpg`) — establishes how many regions need their own heading
    - Operator's trace notes from Task 1
  </read_first>
  <action>
Create `/workspaces/.planning/v1.7/MODIFICATIONS.md` using the structure below. This file IS committed (`.md` re-include rule from Plan 01).

**Frontmatter block** (mirror `.planning/v1.5/baselines/CAPTURE-PROCEDURE.md` lines 1-21):

    # Modified Rev 0 — Rework Trace

    **Phase:** 31 (Plan 05)
    **Board:** Operator's Modified Rev 0 (per memory `[[user_shield_revisions]]`)
    **Photo session date:** [date]
    **Upstream Rev 0 schematic anchor:** `UniversalProgrammerRev0b0.zip::<schematic-file>.kicad_sch` (recovered from `origin/rev2.0` branch — see `mine-notes.md` §Zip-archive listings + `31-04-SUMMARY.md`)
    **Operator:** Henrik Olsson (operator's verbatim trace notes from Task 1)
    **Purpose:** Document every operator-side rework on the Modified Rev 0 board (cuts, jumpers, component swaps), cross-referenced against the upstream Rev 0 schematic so Phase 32 capability matrix + Phase 27 RCA re-open (v1.6) can use this board with a known-good schematic substrate.

**Per-region structure** — for each `rework-N-<region>.jpg` in `/workspaces/.planning/v1.7/photos/rev-0-modified/`, write one `## Rework Region N — <descriptor>` heading immediately followed by:

1. A line referencing the macro photo (relative path).
2. A `Cross-ref:` line starting at column 0 (the phase-gate check #5 grep anchor is `^Cross-ref:`) citing the upstream schematic by zip-internal path + the net/area the rework touches.
3. A 1-3 sentence prose paragraph capturing the operator's trace: original net/component → modified net/component → rationale.

Literal pattern per region (PATTERNS.md §"Cross-ref line literal"):

    ## Rework Region 1 — JP4 jumper insertion (replacing JP3-mod per chat 2024-10-07)

    [macro photo: `photos/rev-0-modified/rework-1-jp4.jpg`]

    Cross-ref: UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch §JP3-mod region (upstream signal name <X>; rework replaces <Y> with <Z>)

    [operator's prose trace: 1-3 sentences citing the original schematic net, the rework's actual delta, and the rationale]

(The "JP4 jumper insertion" is a placeholder example — operator's actual rework regions go here per the trace from Task 1. If `rework-2-*.jpg` and `rework-3-*.jpg` exist, write `## Rework Region 2` and `## Rework Region 3` sections following the same shape.)

**Critical Cross-ref-line conventions** (phase-gate check #5 grep contract):
- Start at column 0 (no indentation, not inside a list).
- Begin with the literal string `Cross-ref:` (capital C, single colon, trailing space before content).
- Cite the upstream schematic by zip-internal path using `::` separator (e.g. `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch`).
- One Cross-ref per `## Rework Region N` heading.
- Grep contract: `grep -c '^Cross-ref:' .planning/v1.7/MODIFICATIONS.md >= ls .planning/v1.7/photos/rev-0-modified/rework-*.jpg | wc -l`

**Special case — no visible rework:** If operator's Task 1 signal was "no rework visible", write a single `## Rework Region 0 — None observed` section with a `Cross-ref:` line citing the upstream schematic but stating "no operator-side modifications observed during 2026-MM-DD photo session" + a 1-sentence rationale (e.g. operator may have misremembered, or rework may be Rev 1 not Rev 0). The phase-gate check still passes (zero rework files → grep count ≥ 0).
  </action>
  <verify>
    <automated>bash -c 'test -f /workspaces/.planning/v1.7/MODIFICATIONS.md && \
      LINES=$(wc -l </workspaces/.planning/v1.7/MODIFICATIONS.md) && test $LINES -ge 25 && \
      N_REFS=$(grep -c "^Cross-ref:" /workspaces/.planning/v1.7/MODIFICATIONS.md) && \
      N_REWORK=$(ls /workspaces/.planning/v1.7/photos/rev-0-modified/rework-*.jpg 2>/dev/null | wc -l) && \
      echo "Cross-ref count: $N_REFS, rework macros: $N_REWORK" && \
      test "$N_REFS" -ge "$N_REWORK" && \
      grep -qE "UniversalProgrammer.*\.zip::" /workspaces/.planning/v1.7/MODIFICATIONS.md && \
      ! git check-ignore -q /workspaces/.planning/v1.7/MODIFICATIONS.md && \
      echo "PASS"'</automated>
  </verify>
  <acceptance_criteria>
    - `.planning/v1.7/MODIFICATIONS.md` exists with ≥ 25 lines.
    - Phase-gate check #5 passes: `grep -c '^Cross-ref:' MODIFICATIONS.md >= ls rework-*.jpg | wc -l`.
    - At least one Cross-ref line cites a zip-internal path using `UniversalProgrammer<XYZ>.zip::` shape.
    - `git check-ignore -q .planning/v1.7/MODIFICATIONS.md` returns NON-zero (file NOT gitignored; the `.md` re-include is working).
  </acceptance_criteria>
  <done>
    `MODIFICATIONS.md` exists as the operator-attested rework appendix, each rework macro has a corresponding `## Rework Region N` heading + `Cross-ref:` line, and phase-gate check #5 passes.
  </done>
</task>

<task type="auto">
  <name>Task 3: Fill §1 Inventory + §2 Appendix + §3 Detect-HW rows</name>
  <files>/workspaces/.planning/v1.7-SHIELD-REVS.md</files>
  <read_first>
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-04-SUMMARY.md` §Findings summary table (the row-by-row metadata for §1) + per-rev R41/JP4/A3 extraction results (for §3)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-02-SUMMARY.md` (CHAT-INTEL.md section structure + the date stamps for §3 intro cross-references)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-03-SUMMARY.md` (verbatim silkscreen strings the operator read off Rev 2.2 + Rev 2.0 macros — these are §1's `silkscreen` column for those rows)
    - Operator's verbatim silkscreen reading from Task 1's `rev-0-modified/silkscreen.jpg` (Modified Rev 0 row)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-CONTEXT.md` §D-02 (provenance + state taxonomy), §D-03 (canonical ID for not-recovered: `upstream-<short-sha>`), §D-10 (column order — VERBATIM), §D-07 (Anders R41-on-A3 scheme to capture in §3)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-PATTERNS.md` §"§3 Existing Detect-HW Scheme content shape" (5-column shape: Rev | R41 value | ADC pin | Voltage divider topology | Schematic citation)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-VALIDATION.md` §"Phase Gate Acceptance Criteria" checks #2, #3, #4 (the contracts §1's filled rows must satisfy) — Check #4 NOTE: `branch-archived:origin/rev2.0` is the convention recorded in the `removed_commit` column when no main-side deletion exists.
    - `/workspaces/.planning/v1.7-SHIELD-REVS.md` (the scaffold from Plan 04 Task 2 — Edit, do not Write-overwrite, to preserve the §4-§9 OWNED-BY markers)
  </read_first>
  <action>
Use the Edit tool (not Write) on `/workspaces/.planning/v1.7-SHIELD-REVS.md` to fill three sections in-place. Do NOT touch §4-§9 (their TBD markers must remain — phase-gate check #7).

**§1 Inventory — add one row per recoverable rev, using the verbatim D-10 column order.**

Each row format (markdown table row syntax): `| silkscreen | provenance | state | introduced_commit | removed_commit | schematic_path | gerber_path | photo_dir | notes |`

Source the row values from Plan 04's `31-04-SUMMARY.md` §Findings summary table. Substitutions to apply:
- `silkscreen` (column 1): VERBATIM PCB text for `state=on-hand-photographed` rows (per Plans 03 + 05 SUMMARY operator readings — e.g. `RURP Rev 2.2`, `RURP Rev 2.0`, `RURP Rev 0` or whatever the silkscreen actually says). For `state=upstream-only` rows where the silkscreen string is not recoverable from upstream silkscreen-layer-export, use `not-recovered` + place the canonical `upstream-<short-sha>` ID (per D-03) in the `notes` column.
- `provenance` (column 2): per D-02, one of two values: `on-main` if rev's schematic file is reachable from `main` HEAD; `removed-from-main` for revs whose schematic file is NOT on `main` HEAD (whether because of an explicit `git rm` commit on main OR because the rev lives only on a non-main branch such as `origin/rev2.0`). Per VALIDATION.md §Check #4 NOTE, branch-archived revs (Rev 0, Rev 1 — they live on the `rev2.0` branch only, per Research Finding #2) are recorded as `removed-from-main` here; the branch citation goes in `removed_commit` (column 5), not in `provenance`.
- `state` (column 3): `on-hand-photographed` if operator photographed the board (Rev 2.2, Rev 2.0, Modified Rev 0 — yes; everything else — no). Otherwise `upstream-only`.
- `introduced_commit` (column 4): short SHA from mine Pass 1 / Pass 4 / Pass 5. Required non-blank for all rows.
- `removed_commit` (column 5): for `provenance=removed-from-main` rows, either the short SHA from mine Pass 3 (if a main-side `git rm` commit exists) OR the literal string `branch-archived:origin/rev2.0` (the VALIDATION.md §Check #4 NOTE convention) when no main-side deletion happened and the rev lives only on the `rev2.0` branch. For current-on-main rows write `—` (em-dash) or leave intentionally non-blank with a dash. The phase-gate check #4 grep only requires that this cell be non-blank for any `removed-from-main` row.
- `schematic_path` (column 6): repo-relative path to the `.kicad_sch` file. For zipped schematics use the `<zipfile>::<inner-path>` form (per Research Finding #2). Example: `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch`.
- `gerber_path` (column 7): repo-relative path to the gerber zip. For revs where gerbers are inside the same zip as the schematic, repeat the zip filename or leave a `(same zip)` annotation.
- `photo_dir` (column 8): `.planning/v1.7/photos/<slug>/` for `state=on-hand-photographed` rows (per Finding #4 slug derivation rule). `—` for `state=upstream-only` rows.
- `notes` (column 9): free-form. For `silkscreen=not-recovered` rows include the `upstream-<short-sha>` ID here. For Modified Rev 0 cross-link MODIFICATIONS.md.

Expected row set (using Plan 04's Findings summary as the seed — exact contents per the mine output):
- Rev 2.3 (on-main, upstream-only) — silkscreen verbatim if recoverable from upstream silkscreen-layer-export, else `not-recovered` + `upstream-<sha>` in notes; silkscreen-only diff vs 2.2 per CHAT-INTEL Anders 2026-07-03
- Rev 2.2 (on-main, on-hand-photographed) — verbatim silkscreen from operator's Plan 03 macro; photo_dir=`.planning/v1.7/photos/rev-2-2/`; R41=10k (notes)
- Rev 2.1 (on-main, upstream-only) — silkscreen if recoverable; introduced R41 (notes)
- rev2 lowercase (on-main, upstream-only) — pre-Rev 2.1 deprecated dump? See Plan 04 SUMMARY
- Rev 1 (removed-from-main, upstream-only) — history-only zip on `rev2.0` branch; `removed_commit` = `branch-archived:origin/rev2.0` per VALIDATION.md §Check #4 NOTE
- Rev 0 (removed-from-main, upstream-only) — history-only zip on `rev2.0` branch; `removed_commit` = `branch-archived:origin/rev2.0`; cross-ref target for MODIFICATIONS.md
- Rev 0 — Modified (on-hand-photographed; provenance: parent=Rev 0; commit refs (n/a — operator board)) — verbatim silkscreen from `silkscreen.jpg`; photo_dir=`.planning/v1.7/photos/rev-0-modified/`; notes: see MODIFICATIONS.md

Add 1-2 sentences of prose intro before the table referencing CHAT-INTEL.md §1 + §4 and `mine-notes.md` (replace the placeholder intro from the Plan 04 scaffold).

**§2 Mentioned-but-not-recovered — add rows for any rev Anders cited (in CHAT-INTEL.md) without a recoverable schematic.**

Walk CHAT-INTEL.md §1-§6 for rev mentions (`Rev 0`, `Rev 1`, `Rev 2.1`, `Rev 2.2`, `Rev 2.3`, `rev2`, etc.). For each rev NOT already in the §1 inventory (e.g. if Anders mentioned a pre-`UniversalProgrammer` rev that has no surviving file), add a row to §2 with: `rev_mention | source_quote | reason_not_recovered | status`.

If CHAT-INTEL surfaces no revs beyond what's in §1, §2 stays with just its header (the empty case is acceptable; the section exists to record gaps and a clean phase 31 may legitimately have none).

**§3 Existing Detect-HW Scheme — fill the per-rev R41 table from `mine-notes.md` §Per-rev R41 grep results.**

Column shape (per PATTERNS.md §"§3 Existing Detect-HW Scheme content shape"): `| Rev | R41 value | ADC pin | Voltage divider topology | Schematic citation |`

Expected rows (from CHAT-INTEL.md §1 + mine-notes.md §Per-rev R41):
- Rev 2.1 | (R41 value extracted from `.kicad_sch`) | A3 | (topology, e.g. `JP4 → R41 → A3 → GND` — extract from schematic) | `hardware/Rev2.1/<schematic>.kicad_sch:<line>` or `hardware/Rev2.1/RURP-Rev2.1.zip::<schematic>:<line>`
- Rev 2.2 | 10k | A3 | (same topology) | `hardware/Rev2.2/<schematic>.kicad_sch:<line>`
- Rev 2.3 | (silkscreen-only diff per CHAT-INTEL Anders 2026-07-03; same 10k) | A3 | (same topology) | `hardware/Rev2.3/<schematic>.kicad_sch:<line>`

If Plan 04's mine surfaced no R41 in pre-Rev-2.1 revs (Rev 0, Rev 1, rev2 lowercase), do NOT include rows for them in §3 (the §3 contract is "EXISTING detect-HW scheme" — only revs that carry the R41 divider belong here). If Plan 04's mine surfaced a different R41 value in Rev 2.1 than expected, capture the value verbatim — Anders may misremember; the schematic is the source of truth.

Replace the placeholder intro paragraph from Plan 04's scaffold with the actual 1-2 sentence intro per PATTERNS.md §"§3 Existing Detect-HW Scheme content shape" + the CHAT-INTEL.md §1 + mine-notes.md §Per-rev R41 cross-references.

**Critical constraints:**
- Use Edit tool (not Write) to preserve §4-§9 OWNED-BY markers untouched.
- D-10 column order is locked — NEVER reorder. Every §1 row must have exactly 9 pipe-separated cells (which produces NF=11 when awk splits on `|` — phase-gate check #2 contract).
- For `state=on-hand-photographed` rows, the `photo_dir` value (column 8) MUST point at an existing directory with at minimum top.jpg + bottom.jpg + silkscreen.jpg — phase-gate check #3 contract.
- For `provenance=removed-from-main` rows, `removed_commit` (column 5) MUST be non-blank — phase-gate check #4 contract. The literal string `branch-archived:origin/rev2.0` is the VALIDATION.md §Check #4 NOTE convention and satisfies the non-blank check.
- Provenance enum is locked to D-02 two values: `{on-main, removed-from-main}`. Do NOT invent a third value (no `branch-archived:*` in the provenance column).
  </action>
  <verify>
    <automated>bash -c 'cd /workspaces && \
      awk -F"|" "/^## 1\\. Inventory/, /^## 2\\./ { if (/^\\|/ && !/^\\|[-: ]+\\|/ && !/silkscreen.*provenance/ && NF != 11) { print \"BAD ROW (NF=\" NF \"): \" \$0; exit 1 } }" .planning/v1.7-SHIELD-REVS.md && \
      python3 -c "
import os
errs = 0
with open(\".planning/v1.7-SHIELD-REVS.md\") as f:
    for line in f:
        if \"on-hand-photographed\" in line and line.startswith(\"|\"):
            cells = [c.strip() for c in line.split(\"|\")[1:-1]]
            photo_dir = cells[7]
            if not os.path.isdir(photo_dir):
                print(f\"MISSING DIR: {photo_dir}\"); errs += 1
                continue
            for required in (\"top.jpg\", \"bottom.jpg\", \"silkscreen.jpg\"):
                if not os.path.exists(os.path.join(photo_dir, required)):
                    print(f\"MISSING FILE: {photo_dir}/{required}\"); errs += 1
import sys; sys.exit(1 if errs else 0)
" && \
      python3 -c "
errs = 0
with open(\".planning/v1.7-SHIELD-REVS.md\") as f:
    for line in f:
        if \"removed-from-main\" in line and line.startswith(\"|\"):
            cells = [c.strip() for c in line.split(\"|\")[1:-1]]
            removed_commit = cells[4]
            if not removed_commit or removed_commit in (\"—\", \"-\", \"\"):
                print(f\"MISSING removed_commit: {line.strip()}\"); errs += 1
import sys; sys.exit(1 if errs else 0)
" && \
      INV_ROWS=$(awk "/^## 1\\. Inventory/, /^## 2\\./ { if (/^\\|/ && !/^\\|[-: ]+\\|/ && !/silkscreen.*provenance/) print }" .planning/v1.7-SHIELD-REVS.md | wc -l) && \
      test $INV_ROWS -ge 3 && \
      S3_ROWS=$(awk "/^## 3\\. Existing/, /^## 4\\./ { if (/^\\|/ && !/^\\|[-: ]+\\|/ && !/Rev.*R41 value/) print }" .planning/v1.7-SHIELD-REVS.md | wc -l) && \
      test $S3_ROWS -ge 2 && \
      echo "Inventory rows: $INV_ROWS, §3 rows: $S3_ROWS" && \
      echo "PASS"'</automated>
  </verify>
  <acceptance_criteria>
    - Phase-gate check #2 passes: awk over §1 rows produces no BAD ROW output (all rows have NF=11 = 9 columns).
    - Phase-gate check #3 passes: every `on-hand-photographed` row's photo_dir exists and contains top.jpg + bottom.jpg + silkscreen.jpg.
    - Phase-gate check #4 passes: every `removed-from-main` row has non-blank removed_commit (a SHA OR the literal `branch-archived:origin/rev2.0` per VALIDATION.md §Check #4 NOTE).
    - §1 contains at least 3 inventory rows (minimum: the 3 operator-on-hand boards — Rev 2.2, Rev 2.0, Modified Rev 0).
    - §3 contains at least 2 R41 rows (Rev 2.1 + Rev 2.2 at minimum; Rev 2.3 if mine surfaced its `.kicad_sch`).
    - §4-§9 still carry their OWNED-BY-PHASE-NN markers (phase-gate check #7 still passes).
    - §1-§3 do NOT carry any OWNED-BY-PHASE marker (phase-gate check #8 still passes — Phase 31 owns these).
  </acceptance_criteria>
  <done>
    `.planning/v1.7-SHIELD-REVS.md` §1 + §2 + §3 are filled with the data from `mine-notes.md` + operator's photo silkscreen readings + CHAT-INTEL.md cross-references. §4-§9 still scaffolded. All phase-gate-check-relevant structural contracts hold.
  </done>
</task>

<task type="auto">
  <name>Task 4: Run all 8 phase-gate checks (Phase 31 close gate)</name>
  <files>(no file modifications — verification-only)</files>
  <read_first>
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-VALIDATION.md` §"Phase Gate Acceptance Criteria" (all 8 checks)
  </read_first>
  <action>
Run all 8 phase-gate checks from `31-VALIDATION.md` §"Phase Gate Acceptance Criteria" verbatim. Each check is a self-contained bash one-liner or python3 stdlib snippet. Each MUST produce empty output (or the explicitly-noted verdict). The checks are reproduced in the `<verify>` block below.

If any check fails:
- Diagnose the failure (which row / which file / which marker).
- Fix in-place via Edit on the relevant file.
- Re-run the failing check.
- Re-run the full 8-check suite once all known issues are addressed.

Do NOT skip a check. The 8 checks are the Phase 31 close-gate contract — they're what the downstream `/gsd-verify-work` runs.
  </action>
  <verify>
    <automated>bash -c 'cd /workspaces && \
      echo "=== Check 1: gitignore functional ===" && \
      touch .planning/v1.7/notes/.probe.md .planning/v1.7/.probe.md && \
      git check-ignore -q .planning/v1.7/notes/.probe.md && { echo "FAIL #1a"; exit 1; } || true && \
      git check-ignore -q .planning/v1.7/.probe.md && { echo "FAIL #1b"; exit 1; } || true && \
      git check-ignore -v .planning/v1.7/upstream-rurp/.git/HEAD >/dev/null && \
      rm -f .planning/v1.7/notes/.probe.md .planning/v1.7/.probe.md && \
      LEAK=$(git status --porcelain | grep ".planning/v1.7/" | grep -v "\\.md$" | wc -l) && test $LEAK -eq 0 && \
      echo "=== Check 2: inventory NF=11 ===" && \
      awk -F"|" "/^## 1\\. Inventory/, /^## 2\\./ { if (/^\\|/ && !/^\\|[-: ]+\\|/ && !/silkscreen.*provenance/ && NF != 11) { print \"BAD ROW (NF=\" NF \"): \" \$0; exit 1 } }" .planning/v1.7-SHIELD-REVS.md && \
      echo "=== Check 3: on-hand-photographed dirs ===" && \
      python3 -c "
import os
errs = 0
with open(\".planning/v1.7-SHIELD-REVS.md\") as f:
    for line in f:
        if \"on-hand-photographed\" in line and line.startswith(\"|\"):
            cells = [c.strip() for c in line.split(\"|\")[1:-1]]
            photo_dir = cells[7]
            if not os.path.isdir(photo_dir):
                print(f\"MISSING DIR: {photo_dir}\"); errs += 1; continue
            for required in (\"top.jpg\", \"bottom.jpg\", \"silkscreen.jpg\"):
                if not os.path.exists(os.path.join(photo_dir, required)):
                    print(f\"MISSING FILE: {photo_dir}/{required}\"); errs += 1
import sys; sys.exit(1 if errs else 0)
" && \
      echo "=== Check 4: removed-from-main removed_commit non-blank ===" && \
      python3 -c "
errs = 0
with open(\".planning/v1.7-SHIELD-REVS.md\") as f:
    for line in f:
        if \"removed-from-main\" in line and line.startswith(\"|\"):
            cells = [c.strip() for c in line.split(\"|\")[1:-1]]
            removed_commit = cells[4]
            if not removed_commit or removed_commit in (\"—\", \"-\", \"\"):
                print(f\"MISSING removed_commit: {line.strip()}\"); errs += 1
import sys; sys.exit(1 if errs else 0)
" && \
      echo "=== Check 5: MODIFICATIONS.md cross-refs >= rework macros ===" && \
      N_REFS=$(grep -c "^Cross-ref:" .planning/v1.7/MODIFICATIONS.md) && \
      N_REWORK=$(ls .planning/v1.7/photos/rev-0-modified/rework-*.jpg 2>/dev/null | wc -l) && \
      echo "  Cross-refs: $N_REFS, rework macros: $N_REWORK" && \
      test "$N_REFS" -ge "$N_REWORK" && \
      echo "=== Check 6: CHAT-INTEL.md key quotes ===" && \
      for key in "R41 on A3" "JP1/JP3mod" "10k version resistor" "branches for the previous" "gerbers"; do \
        grep -E "^> .* 20[0-9]{2}-[0-9]{2}-[0-9]{2}:.*" .planning/v1.7/notes/CHAT-INTEL.md | grep -qi "$key" || { echo "MISSING QUOTE: $key"; exit 1; }; \
      done && \
      echo "=== Check 7: §4-§9 OWNED-BY markers (literal em-dash U+2014) ===" && \
      python3 -c "
import re
with open(\".planning/v1.7-SHIELD-REVS.md\") as f:
    lines = f.read().splitlines()
errs = 0
for i, line in enumerate(lines):
    m = re.match(r\"^## ([4-9])\\.\", line)
    if not m:
        continue
    window = \"\\n\".join(lines[i:i+6])
    # Literal em-dash U+2014 required — hyphen-minus must NOT satisfy this check
    if not re.search(r\"<!-- OWNED BY PHASE \\d+ \\u2014 TBD -->\", window):
        print(f\"MISSING em-dash marker after §{m.group(1)} at line {i+1}\"); errs += 1
import sys; sys.exit(1 if errs else 0)
" && \
      echo "=== Check 8: §1-§3 own no TBD marker ===" && \
      python3 -c "
import re
with open(\".planning/v1.7-SHIELD-REVS.md\") as f:
    text = f.read()
errs = 0
for n in (1, 2, 3):
    m = re.search(rf\"^## {n}\\..*?(?=^## |\\Z)\", text, re.MULTILINE | re.DOTALL)
    if not m:
        print(f\"MISSING §{n}\"); errs += 1; continue
    if \"OWNED BY PHASE\" in m.group(0):
        print(f\"§{n} STILL HAS TBD MARKER\"); errs += 1
import sys; sys.exit(1 if errs else 0)
" && \
      echo "=== ALL 8 CHECKS PASS ==="'</automated>
  </verify>
  <acceptance_criteria>
    - All 8 phase-gate checks pass (each produces empty output or the explicitly-noted verdict, per the `<verify>` block).
    - `=== ALL 8 CHECKS PASS ===` is the final line of the verify output.
  </acceptance_criteria>
  <done>
    Phase 31's close-gate contract is fully satisfied; `/gsd-verify-work` will find the same 8 checks green.
  </done>
</task>

</tasks>

<verification>
This plan IS the phase-gate; Task 4 runs all 8 checks. Plan-scoped subset that MUST be green at close:

```bash
# Check 1: gitignore (covered by Plan 01 — must still hold here)
# Check 2: inventory NF=11 (covered by Task 3 §1 fill)
# Check 3: on-hand-photographed dirs (covered by Task 3 §1 fill + Tasks 1-2 + Plan 03 Task 2 photos)
# Check 4: removed-from-main removed_commit non-blank (Task 3)
# Check 5: MODIFICATIONS.md cross-refs >= rework macros (Task 2)
# Check 6: CHAT-INTEL.md key quotes (covered by Plan 02 — must still hold here)
# Check 7: §4-§9 OWNED-BY markers (covered by Plan 04 — must still hold; Task 3 must NOT have damaged)
# Check 8: §1-§3 own no TBD marker (covered by Plan 04; Task 3 fills must not introduce one)
```

All 8 are run by Task 4 verify block.
</verification>

<success_criteria>
- Modified Rev 0 board is photographed with top + bottom + silkscreen + 1+ rework macro JPGs.
- `MODIFICATIONS.md` exists at `.planning/v1.7/` with one `## Rework Region N` heading per rework macro + a `^Cross-ref:` line per heading citing the upstream Rev 0 schematic by zip-internal path.
- `.planning/v1.7-SHIELD-REVS.md` §1 has ≥ 3 inventory rows (one per operator-on-hand board minimum) + however many upstream-only rows the mine surfaced.
- §2 captures any Anders-mentioned rev without recoverable schematic (or stays empty with header alone — both are valid).
- §3 has per-rev R41 rows for Rev 2.1, Rev 2.2, and (if mine surfaced it) Rev 2.3.
- §4-§9 still carry their OWNED-BY markers untouched.
- All 8 phase-gate checks pass.
- No firmware/host-CLI commits.
</success_criteria>

<output>
After completion, create `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-05-SUMMARY.md` documenting:
- The final §1 inventory row count, broken down by `state` (on-hand-photographed vs upstream-only) and `provenance` (on-main / removed-from-main).
- The verbatim silkscreen strings captured for the three operator boards (these are the canonical IDs Phase 33's alias migration consumes).
- The number of rework regions identified on the Modified Rev 0 + a 1-line per-region summary.
- The R41 values found per rev for §3 (so Phase 34's firmware ADC plumbing has them ready without re-running the mine).
- Status of phase-gate checks #1-#8 (all PASS expected; any anomaly noted explicitly).
- Any Phase 35 follow-up todos that surfaced (e.g. Rev 2.1 not found, an Anders quote that suggested a rev with no surviving file, a rework region the operator couldn't trace cleanly against the upstream schematic).
</output>
</content>
</invoke>
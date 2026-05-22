---
phase: 31
plan: 04
type: execute
wave: 2
depends_on: [01]
files_modified:
  - .planning/v1.7-SHIELD-REVS.md
  - .planning/phases/31-upstream-shield-archaeology/mine-notes.md   # scratch: raw mine output for Plan 05 to consume
autonomous: true
requirements_addressed: [HW-INV-01, HW-INV-02, SILK-01]
requirements: [HW-INV-01, HW-INV-02, SILK-01]
must_haves:
  truths:
    - "`.planning/v1.7-SHIELD-REVS.md` exists at `.planning/` root (NOT under `.planning/v1.7/`) with the §1-§9 section skeleton committed."
    - "§1, §2, §3 are owned-by-Phase-31 (no TBD marker); §4-§9 carry the literal `<!-- OWNED BY PHASE 3X — TBD -->` marker phrasing per D-09."
    - "§1's inventory table header is verbatim from D-10: `| silkscreen | provenance | state | introduced_commit | removed_commit | schematic_path | gerber_path | photo_dir | notes |` — NEVER reorder."
    - "The §1-§3 content rows are filled by Plan 05 (not this plan). This plan ships the EMPTY scaffold + the raw mine-output scratch file Plan 05 will consume."
    - "Per-rev R41-value + ADC pin assignment + JP4 designator are extracted from upstream `.kicad_sch` files (Rev 2.1, Rev 2.2, Rev 2.3) into the scratch file so Plan 05's §3 fill is deterministic."
  artifacts:
    - path: ".planning/v1.7-SHIELD-REVS.md"
      provides: "Canonical reference doc skeleton (§1-§9 with TBD markers on §4-§9)"
      contains: "<!-- OWNED BY PHASE 32 — TBD -->"
      min_lines: 80
    - path: ".planning/phases/31-upstream-shield-archaeology/mine-notes.md"
      provides: "Scratch file with raw mine output + per-rev R41/JP4/A3 extractions for Plan 05 to consume"
      contains: "## Pass 1"
      min_lines: 40
  key_links:
    - from: ".planning/v1.7-SHIELD-REVS.md §4-§9"
      to: "Phases 32, 33, 34 (downstream fill)"
      via: "literal `<!-- OWNED BY PHASE 3X — TBD -->` marker per D-09"
      pattern: '<!-- OWNED BY PHASE [0-9]+ — TBD -->'
    - from: ".planning/phases/31-upstream-shield-archaeology/mine-notes.md"
      to: ".planning/v1.7/upstream-rurp/ (gitignored clone)"
      via: "git log -p / git ls-tree / unzip -l output captured as scratch text"
      pattern: '## Pass [1-5]'
---

<objective>
Two tightly-coupled tasks: (a) mine the upstream `Relatively-Universal-ROM-Programmer` git history per the 5-pass D-04+Finding-#1 recipe and capture the raw output into a scratch file Plan 05 will consume; (b) scaffold `.planning/v1.7-SHIELD-REVS.md` with the full §1-§9 skeleton, empty §1 inventory header (D-10 column order), empty §2 appendix, empty §3 detect-HW table, and `<!-- OWNED BY PHASE 3X — TBD -->` markers on §4-§9.

Purpose: Plan 05 needs both the mine output (to know which revs exist, with which provenance + commit metadata) AND the scaffold (to know where to write rows). Coupling the mine + scaffold into one plan reduces context shuffling — both touch the same logical bag of upstream-history facts.

Output:
1. `.planning/v1.7/upstream-rurp/` is interrogated; raw output for each of the 5 passes (current state, tags, deletions, rev-named branches, all-refs fallback) lands in the scratch file.
2. Per-rev `.kicad_sch` content (Rev 2.1, Rev 2.2, Rev 2.3) is grep'd for `R41` / `A3` / `JP4` designators + resistor values, with results in the scratch file.
3. `unzip -l` listings of `UniversalProgrammerRev0b0.zip` + `UniversalProgrammerRev1b0.zip` + `rev2-1316.zip` + `RURP-Rev2.1.zip` + `Rev2.2-gerbers.zip` capture zip-internal `.kicad_sch` paths.
4. `.planning/v1.7-SHIELD-REVS.md` exists as the empty-but-structurally-complete scaffold.

This plan does NOT fill the inventory rows; Plan 05 does that.
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
@/workspaces/.planning/v1.6-EVIDENCE.md
@/workspaces/.planning/v1.3-BENCH-RESULTS.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Mine upstream git history (5 passes) into scratch file</name>
  <files>/workspaces/.planning/phases/31-upstream-shield-archaeology/mine-notes.md</files>
  <read_first>
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-CONTEXT.md` §D-04 (the four mine passes the user locked) + §specifics ("Rev 2.1 MUST be found" + "Rev 2.3 may already exist upstream" + "Modified Rev 0 cross-reference target is the upstream Rev 0 schematic")
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-RESEARCH.md` §Finding #1 (all 5 pass command recipes — copy verbatim) + §Finding #2 (per-rev filename conventions + the rev2.0-branch zip discovery — `unzip -l` on each)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-PATTERNS.md` §"Pattern C — Single-source-of-truth path citations" (every fact in the scratch file must trace to a git command + ref)
    - `/workspaces/.planning/v1.7/upstream-rurp/` (cloned by Plan 01 Task 2 — must exist and have remote branches fetched)
  </read_first>
  <action>
Run all 5 passes from Research Finding #1 against `.planning/v1.7/upstream-rurp/`, plus the per-zip `unzip -l` listings from Finding #2, and capture the output into a scratch markdown at `.planning/phases/31-upstream-shield-archaeology/mine-notes.md`. This scratch file is committed (it lives outside `.planning/v1.7/` so the gitignore rule doesn't reach it; it's a Phase-31 working artifact in the phase dir).

**Structure of `mine-notes.md`:**

    # Phase 31 — Upstream Git-History Mine Notes (scratch)

    **Source:** `.planning/v1.7/upstream-rurp/` (cloned 2026-05-22 by Plan 01 Task 2)
    **Mined:** [date]
    **Consumed by:** Plan 05 §1 inventory fill + §3 detect-HW fill

    ## Pass 1 — Current state of `hardware/` on `main`

    Command: `git -C .planning/v1.7/upstream-rurp log --all --pretty=format:'%h %ai %s' -- hardware/ | head -100`

    Output:
    ```
    [paste verbatim]
    ```

    Per-subdir introductions (`git log --diff-filter=A` for each `hardware/Rev2.X/`):
    ```
    [paste verbatim]
    ```

    ## Pass 2 — Tag enumeration

    Command: `git -C .planning/v1.7/upstream-rurp tag --sort=-creatordate`

    Output:
    ```
    [paste verbatim]
    ```

    For each tag, `git show <tag> --stat -- hardware/`:
    [paste relevant per-tag entries — only ones that touch hardware/]

    ## Pass 3 — Deletions from `main`

    Command: `git -C .planning/v1.7/upstream-rurp log --all --diff-filter=D --pretty=format:'%h %ai %s' -- hardware/`

    Output:
    ```
    [paste verbatim — may be empty per Finding #2, which is itself a noteworthy finding]
    ```

    ## Pass 4 — Walk rev-named branches (case-insensitive `/rev[ -]?\d/i`)

    Command: `git -C .planning/v1.7/upstream-rurp branch -r | grep -iE 'rev[ -]?[0-9]'`

    Output:
    ```
    [paste verbatim — expected per Finding #1: origin/rev2.0, origin/Rev2.1, origin/Rev2.3]
    ```

    For each rev-named branch, `git ls-tree -r <branch> -- hardware/` (top 40 lines):
    [paste per-branch listings]

    ## Pass 5 — All-refs fallback (rev-list across tags + remotes)

    Command: `git -C .planning/v1.7/upstream-rurp log --all --source --pretty=format:'%h %S %s' -- hardware/ | head -80`

    Output:
    ```
    [paste verbatim]
    ```

    ## Zip-archive listings (Finding #2 — Rev 0 + Rev 1 live as inline zips on rev2.0 branch)

    For each historical zip, `git -C .planning/v1.7/upstream-rurp show <ref>:<path> | unzip -l /dev/stdin` (or extract to /tmp + unzip -l):

    ### UniversalProgrammerRev0b0.zip (rev2.0 branch)
    ```
    [paste unzip -l output — capture the `.kicad_sch` filename inside the zip]
    ```

    ### UniversalProgrammerRev1b0.zip (rev2.0 branch)
    ```
    [paste]
    ```

    ### rev2-1316.zip (main, hardware/rev2/)
    ```
    [paste]
    ```

    ### RURP-Rev2.1.zip (main, hardware/Rev2.1/)
    ```
    [paste]
    ```

    ### Rev2.2-gerbers.zip (main, hardware/Rev2.2/)
    ```
    [paste]
    ```

    ## Per-rev R41 / JP4 / A3 grep (for §3 Existing Detect-HW Scheme fill in Plan 05)

    For each rev's `.kicad_sch` (Rev 2.1, Rev 2.2, Rev 2.3), grep for resistor designator R41 + jumper designator JP4 + net name A3:

    ### Rev 2.1 (hardware/Rev2.1/W27C512Programmer.kicad_sch — verify actual filename via `git ls-tree`)
    ```
    git -C .planning/v1.7/upstream-rurp show HEAD:hardware/Rev2.1/<schematic>.kicad_sch | grep -E '(R41|JP4|"A3"|net.*A3)'
    ```
    Output:
    ```
    [paste]
    ```
    R41 value: [extracted resistor value — likely a property line like `(property "Value" "10k" ...)` near the R41 reference]
    ADC pin: A3 (per CHAT-INTEL §1)
    JP4 designator: [extracted]

    ### Rev 2.2 (hardware/Rev2.2/...kicad_sch)
    [same shape — expected R41 = 10k per CHAT-INTEL Anders 2025-04-28]

    ### Rev 2.3 (hardware/Rev2.3/...kicad_sch, possibly under jlcpcb/ subdir)
    [same shape — expected silkscreen-only diff vs Rev 2.2 per CHAT-INTEL Anders 2026-07-03; R41 should still be 10k]

    ## Findings summary (for Plan 05 consumption)

    | Rev | Provenance | State | Introduced commit (SHA) | Removed commit | Schematic path | Gerber path | Photo dir | Notes |
    |-----|------------|-------|--------------------------|----------------|----------------|-------------|-----------|-------|
    | [Rev 2.3] | on-main | upstream-only | [SHA] | — | hardware/Rev2.3/...kicad_sch | hardware/Rev2.3/jlcpcb/... | — | silkscreen-only diff vs 2.2 |
    | [Rev 2.2] | on-main | on-hand-photographed | [SHA] | — | hardware/Rev2.2/...kicad_sch | hardware/Rev2.2/Rev2.2-gerbers.zip | .planning/v1.7/photos/rev-2-2/ | R41=10k; operator on-hand |
    | [Rev 2.1] | on-main | upstream-only | [SHA] | — | hardware/Rev2.1/...kicad_sch | hardware/Rev2.1/RURP-Rev2.1.zip | — | R41 introduced (per CHAT-INTEL Anders 2026-07-03) |
    | [rev2/lowercase] | on-main | upstream-only | [SHA] | — | rev2-1316.zip::<inner> | rev2-1316.zip | — | Deprecated dump? Verify if pre-Rev2.1 or aux |
    | [Rev 1] | removed-from-main OR branch-archived:origin/rev2.0 | upstream-only | [SHA from rev2.0 branch] | [if applicable] | UniversalProgrammerRev1b0.zip::<inner> | (same zip) | — | History-only; lives on rev2.0 branch |
    | [Rev 0] | branch-archived:origin/rev2.0 | upstream-only | [SHA] | [if applicable] | UniversalProgrammerRev0b0.zip::<inner> | (same zip) | — | History-only; cross-ref target for MODIFICATIONS.md (Plan 05) |
    | [Rev 0 — Modified] | (n/a) | on-hand-photographed | (n/a — operator board, derived from Rev 0) | — | (cross-refs to UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch — see MODIFICATIONS.md) | (n/a) | .planning/v1.7/photos/rev-0-modified/ (Plan 05) | Modified Rev 0 with hardware-bug-A/B rework; populated by Plan 05 |

    Note: Plan 05 finalizes the verbatim `silkscreen` column from operator's photos (Plan 03 + Plan 05) and substitutes `upstream-<short-sha>` per D-03 for any rev whose silkscreen string is not recoverable from the upstream schematic PDFs/silkscreen layer. The above table seeds Plan 05's §1 fill; verbatim columns are operator-attested at Plan 05 time.

    **Critical: per CONTEXT specifics, Rev 2.1 MUST be found.** If Pass 1-5 + the zip listings do not surface a Rev 2.1 schematic anywhere, ESCALATE — flag this in the SUMMARY for follow-up; do not silently omit. (Anders explicitly stated R41 was introduced in Rev 2.1, so if no Rev 2.1 schematic exists, either Anders is wrong or the mine missed a non-rev-named branch.)

**Constraints:**
- Do NOT extract zips into the committed tree. Use `unzip -l` only (lists contents without extracting). If a `.kicad_sch` inside a zip needs grep'ing, extract to `/tmp/<rev>-extract/` (NOT under `.planning/`) and read from there. `/tmp` self-cleans on container restart.
- Per D-08, do NOT contact Anders. Mine-only.
- Per `<critical_corrections_from_research>` in the orchestrator brief, the planner has explicitly forbidden including final-state code blocks in `<action>` — this action ships directive prose + command recipes; the executor writes the actual mine output.
  </action>
  <verify>
    <automated>bash -c 'test -f /workspaces/.planning/phases/31-upstream-shield-archaeology/mine-notes.md && \
      LINES=$(wc -l </workspaces/.planning/phases/31-upstream-shield-archaeology/mine-notes.md) && test $LINES -ge 40 && \
      for pass in "## Pass 1" "## Pass 2" "## Pass 3" "## Pass 4" "## Pass 5"; do \
        grep -qF "$pass" /workspaces/.planning/phases/31-upstream-shield-archaeology/mine-notes.md || { echo "MISSING SECTION: $pass"; exit 1; }; \
      done && \
      grep -qF "## Zip-archive listings" /workspaces/.planning/phases/31-upstream-shield-archaeology/mine-notes.md && \
      grep -qF "## Per-rev R41" /workspaces/.planning/phases/31-upstream-shield-archaeology/mine-notes.md && \
      grep -qF "## Findings summary" /workspaces/.planning/phases/31-upstream-shield-archaeology/mine-notes.md && \
      grep -qE "(Rev2\.1|rev2\.0)" /workspaces/.planning/phases/31-upstream-shield-archaeology/mine-notes.md && \
      echo "PASS"'</automated>
  </verify>
  <acceptance_criteria>
    - `mine-notes.md` exists with ≥ 40 lines.
    - Contains all 5 `## Pass N` section headers verbatim.
    - Contains `## Zip-archive listings`, `## Per-rev R41`, `## Findings summary` headers.
    - References at least one rev-named branch identifier (`Rev2.1` or `rev2.0`) — confirms the mine actually queried the clone (not a hand-waved placeholder).
    - If Rev 2.1 schematic is NOT surfaced in any pass, the SUMMARY notes this as a Phase 35 follow-up todo per CONTEXT specifics.
  </acceptance_criteria>
  <done>
    `mine-notes.md` is committed in the phase dir (outside `.planning/v1.7/` so gitignore doesn't hide it), all 5 passes have output, all 5 historical zips have `unzip -l` listings, per-rev R41/JP4/A3 grep results are captured, and the Findings summary table seeds Plan 05's §1 fill.
  </done>
</task>

<task type="auto">
  <name>Task 2: Scaffold `.planning/v1.7-SHIELD-REVS.md` with §1-§9 skeleton + TBD markers</name>
  <files>/workspaces/.planning/v1.7-SHIELD-REVS.md</files>
  <read_first>
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-CONTEXT.md` §D-09 (the 9-section ownership map + literal marker phrasing) + §D-10 (the 9-column inventory header — VERBATIM, no reordering)
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-PATTERNS.md` §"`.planning/v1.7-SHIELD-REVS.md` — canonical accretion doc" (frontmatter style + section-heading + comment-marker conventions; the §3 table content shape Plan 05 will fill)
    - `/workspaces/.planning/v1.6-EVIDENCE.md` (lines 1-22 — frontmatter style analog: title + bold-metadata block: Milestone / Source / Cross-phase accretion / Schema)
    - `/workspaces/.planning/v1.3-BENCH-RESULTS.md` (lines 14-15 — TBD-marker pattern Phase 31 generalizes from "Plans 12-01 / 12-02 / 12-03 append..." to "OWNED BY PHASE 3X — TBD")
    - `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-VALIDATION.md` §"Phase Gate Acceptance Criteria" checks #2, #7, #8 (the three structural contracts this file's scaffold MUST satisfy from day one — column count, marker presence on §4-§9, absence of markers on §1-§3)
  </read_first>
  <action>
Create `/workspaces/.planning/v1.7-SHIELD-REVS.md` (at `.planning/` root, NOT under `.planning/v1.7/`) with the structure below. This is the canonical reference doc the entire v1.7 milestone builds up.

**Frontmatter block** (mirror v1.6-EVIDENCE.md lines 1-22 style):

- Title: `# v1.7 SHIELD REVS — Authoritative RURP Shield Revision Reference`
- Then bold-metadata fields (one per line):
  - `**Milestone:** v1.7 RURP Shield Hardware Investigation & Version Detection`
  - `**Source upstream:** `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer` (cloned to `.planning/v1.7/upstream-rurp/`, gitignored)`
  - `**Cross-phase accretion:** Phase 31 (inventory + silkscreen + Anders R41 scheme) → Phase 32 (electrical/mechanical diff + capability matrix) → Phase 33 (silkscreen → code alias table) → Phase 34 (next-rev schematic delta + ADC band table) → Phase 35 (close)`
  - `**Schema:** D-10 9-column inventory schema is locked across all v1.7 phases.`

Then `## Summary` paragraph (1-2 sentences) explaining the doc's role.

**§1 Inventory** — write the section heading + the verbatim 9-column header + the row-separator. NO ROWS in this scaffold. Plan 05 fills the rows.

    ## 1. Inventory

    [prose intro paragraph — 2-3 sentences citing CHAT-INTEL.md §1+§4 (R41 history, branches-hold-prior-revs) and `mine-notes.md` (where each rev was sourced from)]

    | silkscreen | provenance | state | introduced_commit | removed_commit | schematic_path | gerber_path | photo_dir | notes |
    |------------|------------|-------|-------------------|----------------|----------------|-------------|-----------|-------|

(The intro prose may reference Plan 05's pending fill — that's fine; downstream tasks update prose. The column header is the locked artifact phase-gate check #2 verifies.)

**§2 Mentioned-but-not-recovered** — heading + intro sentence + table header (smaller — `rev_mention | source_quote | reason_not_recovered | status`). NO ROWS. Plan 05 fills rows for any rev Anders cited without a recoverable schematic.

    ## 2. Mentioned-but-not-recovered

    [1-sentence intro: "Revs Anders cited (in CHAT-INTEL or upstream commit history) where no schematic file survives; recorded here so downstream phases don't accidentally promote them into the §1 inventory."]

    | rev_mention | source_quote | reason_not_recovered | status |
    |-------------|--------------|----------------------|--------|

**§3 Existing Detect-HW Scheme (Anders R41-on-A3)** — heading + intro sentence citing CHAT-INTEL §1 + the upstream schematics by zip-internal path + table header. NO ROWS. Plan 05 fills the per-rev R41 + JP4 + A3 + topology + schematic citation per `mine-notes.md` Task 1 output.

    ## 3. Existing Detect-HW Scheme (Anders R41-on-A3)

    [1-2 sentence intro: "Per `.planning/v1.7/notes/CHAT-INTEL.md` §1 + the per-rev `.kicad_sch` mine (see `.planning/phases/31-upstream-shield-archaeology/mine-notes.md` §Per-rev R41), Anders introduced a version-detect resistor divider at R41 feeding Arduino ADC pin A3 starting Rev 2.1. Rev 2.2 uses R41 = 10k. Rev 2.3 is silkscreen-only diff vs Rev 2.2 (same R41 = 10k). This §3 table captures the per-rev ground truth Phase 34's firmware ADC-detect plumbing will consume."]

    | Rev | R41 value | ADC pin | Voltage divider topology | Schematic citation |
    |-----|-----------|---------|--------------------------|--------------------|

**§4-§9 scaffolded with TBD markers** — heading + ONE blank line + the literal marker comment (per PATTERNS.md §"Pattern B" + D-09):

    ## 4. Inter-Rev Electrical Differences

    <!-- OWNED BY PHASE 32 — TBD -->

    ## 5. Inter-Rev Mechanical Differences

    <!-- OWNED BY PHASE 32 — TBD -->

    ## 6. Per-Rev Capability Matrix

    <!-- OWNED BY PHASE 32 — TBD -->

    ## 7. Silkscreen → Code Alias Table

    <!-- OWNED BY PHASE 33 — TBD -->

    ## 8. Detect-HW Schematic Delta (next rev)

    <!-- OWNED BY PHASE 34 — TBD -->

    ## 9. Per-Rev Expected ADC Band Table

    <!-- OWNED BY PHASE 34 — TBD -->

**Critical marker phrasing rules** (phase-gate check #7 contract):
- Literal text `<!-- OWNED BY PHASE NN — TBD -->` (em-dash `—` not hyphen `-`; single space each side).
- Marker is within 5 lines of its `## N.` heading (one blank line + marker is fine; verified by python3 5-line window check).
- Phase number per D-09: §4 §5 §6 → 32; §7 → 33; §8 §9 → 34.

**§1-§3 must NOT carry an OWNED BY marker** (phase-gate check #8 contract — Phase 31 owns these sections, so the marker is absent from the moment the scaffold ships even though the rows are empty).
  </action>
  <verify>
    <automated>bash -c 'test -f /workspaces/.planning/v1.7-SHIELD-REVS.md && \
      LINES=$(wc -l </workspaces/.planning/v1.7-SHIELD-REVS.md) && test $LINES -ge 50 && \
      grep -qF "| silkscreen | provenance | state | introduced_commit | removed_commit | schematic_path | gerber_path | photo_dir | notes |" /workspaces/.planning/v1.7-SHIELD-REVS.md && \
      for n in 1 2 3 4 5 6 7 8 9; do \
        grep -qE "^## $n\\. " /workspaces/.planning/v1.7-SHIELD-REVS.md || { echo "MISSING SECTION ## $n."; exit 1; }; \
      done && \
      python3 -c "
import re
with open(\"/workspaces/.planning/v1.7-SHIELD-REVS.md\") as f:
    lines = f.read().splitlines()
errs = 0
for i, line in enumerate(lines):
    m = re.match(r\"^## ([4-9])\\.\", line)
    if not m:
        continue
    window = \"\\n\".join(lines[i:i+6])
    # Literal em-dash U+2014 required — hyphen-minus must NOT satisfy this check
    if not re.search(r\"<!-- OWNED BY PHASE \\d+ \\u2014 TBD -->\", window):
        print(f\"MISSING em-dash marker after §{m.group(1)} at line {i+1}: {line}\")
        errs += 1
import sys
sys.exit(1 if errs else 0)
" && \
      python3 -c "
import re
with open(\"/workspaces/.planning/v1.7-SHIELD-REVS.md\") as f:
    text = f.read()
for n in (1, 2, 3):
    m = re.search(rf\"^## {n}\\..*?(?=^## |\\Z)\", text, re.MULTILINE | re.DOTALL)
    assert m, f\"MISSING §{n}\"
    assert \"OWNED BY PHASE\" not in m.group(0), f\"§{n} STILL HAS TBD MARKER\"
print(\"§1-§3 clean\")
" && \
      ! git check-ignore -q /workspaces/.planning/v1.7-SHIELD-REVS.md && \
      echo "PASS"'</automated>
  </verify>
  <acceptance_criteria>
    - `.planning/v1.7-SHIELD-REVS.md` exists at `.planning/` root with ≥ 50 lines.
    - Contains the verbatim D-10 9-column header line.
    - Contains all 9 `## N.` section headers (1-9).
    - Phase-gate check #7 passes (every §4-§9 heading followed by `<!-- OWNED BY PHASE NN — TBD -->` within 5 lines).
    - Phase-gate check #8 passes (§1, §2, §3 contain NO `OWNED BY PHASE` marker).
    - `git check-ignore -q .planning/v1.7-SHIELD-REVS.md` returns NON-zero (file is NOT gitignored — lives at `.planning/` root, outside `.planning/v1.7/`).
    - Cross-check: Phase-gate check #2 (`awk -F'|'` over §1 rows) produces empty output (the header is well-formed; there are zero data rows yet, so NF=11 mismatches don't apply).
  </acceptance_criteria>
  <done>
    `.planning/v1.7-SHIELD-REVS.md` is the empty-but-structurally-complete scaffold. §1-§3 await Plan 05's row fills; §4-§9 await downstream phases. The doc is committable, the D-10 column header is locked, and the OWNED-BY markers form a per-phase ownership contract verifiable by grep.
  </done>
</task>

</tasks>

<verification>
Plan 04 phase-gate subset (from `31-VALIDATION.md` §"Phase Gate Acceptance Criteria" checks #2 + #7 + #8 — scoped to the scaffold; rows-empty is OK at this stage):

```bash
# Check #2 — column count holds (no rows yet, so the awk should produce empty output trivially)
awk -F'|' '
  /^## 1\. Inventory/, /^## 2\./ {
    if (/^\|/ && !/^\|[-: ]+\|/ && !/silkscreen.*provenance/ && NF != 11) {
      print "BAD ROW (NF=" NF "): " $0
    }
  }
' .planning/v1.7-SHIELD-REVS.md
# Output must be empty

# Check #7 — TBD markers on §4-§9
python3 <<'PY'
import re
with open('.planning/v1.7-SHIELD-REVS.md') as f:
    lines = f.read().splitlines()
for i, line in enumerate(lines):
    m = re.match(r'^## ([4-9])\.', line)
    if not m:
        continue
    window = '\n'.join(lines[i:i+6])
    if '<!-- OWNED BY PHASE' not in window:
        print(f"MISSING marker after §{m.group(1)} at line {i+1}: {line}")
PY
# Output must be empty

# Check #8 — §1-§3 own no TBD marker
python3 <<'PY'
import re
with open('.planning/v1.7-SHIELD-REVS.md') as f:
    text = f.read()
for n in (1, 2, 3):
    m = re.search(rf'^## {n}\..*?(?=^## |\Z)', text, re.MULTILINE | re.DOTALL)
    if not m:
        print(f"MISSING §{n}")
        continue
    if 'OWNED BY PHASE' in m.group(0):
        print(f"§{n} STILL HAS TBD MARKER — must be filled by Phase 31")
PY
# Output must be empty
```

Plus a smoke that `mine-notes.md` has actually-mined data (not a stub):

```bash
grep -c '^## Pass [1-5]' .planning/phases/31-upstream-shield-archaeology/mine-notes.md   # → 5
```
</verification>

<success_criteria>
- Upstream history mined per the 5-pass D-04+Finding-#1 recipe; raw output captured in `mine-notes.md` (phase-dir scratch — committed, not gitignored).
- Per-rev R41 / JP4 / A3 grep extractions present in `mine-notes.md` ready for Plan 05's §3 fill.
- `.planning/v1.7-SHIELD-REVS.md` exists at `.planning/` root with full §1-§9 scaffold + D-10 column header + literal OWNED-BY markers on §4-§9 only.
- Phase-gate checks #2, #7, #8 already pass on the empty scaffold.
- If Rev 2.1 schematic isn't surfaced by the mine, the SUMMARY notes this as a Phase 35 follow-up todo per CONTEXT specifics.
- No firmware/host-CLI commits.
</success_criteria>

<output>
After completion, create `/workspaces/.planning/phases/31-upstream-shield-archaeology/31-04-SUMMARY.md` documenting:
- The full mine `Findings summary` table from `mine-notes.md` (so Plan 05 has the row-by-row metadata it needs without re-running the mine).
- The per-rev R41 / JP4 / A3 extraction results (R41 value per rev, schematic file path per rev, line numbers within `.kicad_sch` where the designators appear).
- Status of Rev 2.1 schematic recovery — found / not-found / found-in-zip-rev2.0-branch. (Critical per CONTEXT specifics: if not-found, this becomes a Phase 35 follow-up.)
- Whether `rev2/` (lowercase) on main is a pre-Rev2.1 deprecated dump (state = upstream-only) or contains something else worth noting.
</output>

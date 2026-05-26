# Phase 31: Upstream Shield Archaeology - Research

**Researched:** 2026-05-22
**Domain:** Desk-side hardware archaeology (git-mining, OpenDocument extraction, KiCad file conventions, photo capture protocol, gitignore re-include semantics)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: Minimum inventory bar — schematic file required.** Only revs whose schematic file is recoverable from upstream history enter the main inventory table. Revs mentioned-but-no-schematic-survives go in a separate "Mentioned-but-not-recovered" appendix at the bottom of `v1.7-SHIELD-REVS.md`.
- **D-02: Two-column tagging — `provenance` + `state`.** Each inventory row has `provenance ∈ {on-main, removed-from-main}` AND `state ∈ {on-hand-photographed, upstream-only}`.
- **D-03: Canonical ID for silkscreen-not-recoverable revs.** Use `upstream-<commit-short-sha>` and mark the silkscreen column `not-recovered`.
- **D-04: Git-history mine depth.** `git log -p hardware/` on main + `git tag` enumeration with `git show <tag>:hardware/` per tag + `git log --diff-filter=D -- hardware/` + walk any branch matching regex `/rev[ -]?\d/i`. Skip WIP/feature branches that don't match the rev-naming convention.
- **D-05: Operator's third board IS a genuine Rev 0.** Canonical identifier: per silkscreen verbatim (captured at photo session).
- **D-06: Rework details traced by visual inspection during photo capture.** No pre-existing rework notes; take macro shots, cross-reference each modification against the upstream Rev 0 schematic; record findings in `.planning/v1.7/MODIFICATIONS.md`.
- **D-07: Anders's existing R41-on-A3 voltage-divider-into-ADC scheme is inventoried in Phase 31** — Rev 2.1 introduced, Rev 2.2 uses 10k, Rev 2.3 silkscreen-only diff vs Rev 2.2. Phase 31 captures per-rev R41 values + ADC pin assignment.
- **D-08: Do NOT contact Anders for Phase 31 confirmation.** Mine artifacts only.
- **D-09: Phase 31 creates the FULL document skeleton** for `.planning/v1.7-SHIELD-REVS.md` (§1-§9 with `<!-- OWNED BY PHASE 3X — TBD -->` markers for §4-§9).
- **D-10: Inventory table column order (locked):** `| silkscreen | provenance | state | introduced_commit | removed_commit | schematic_path | gerber_path | photo_dir | notes |`
- **D-11: Gitignore policy — `.planning/v1.7/` with `!` un-ignore for `.md` files.** ⚠️ Pattern AS WRITTEN in CONTEXT.md does **not work** (see Research Finding #9); the correct three-line pattern is documented below.
- **D-12: CHAT-INTEL.md is a Phase 31 deliverable.** Distill inter-rev intel from `/workspaces/fs_an_notes.odt` + the Discord CSV. Direct quotes with date stamps.

### Claude's Discretion

- Photo capture protocol details (resolution, file format, lighting, angle, naming convention).
- MODIFICATIONS.md internal structure (heading hierarchy, how to cite upstream schematic).
- CHAT-INTEL.md internal structure (chronological vs topical grouping). Chronological-with-topical-headers is the natural shape.
- Phase 31 wave decomposition (single wave vs upstream-clone + history-mine wave + photograph wave + scaffold wave).

### Deferred Ideas (OUT OF SCOPE)

- Phase 34 scope rewrite (R41-on-A3 reframing → for Phase 34 discuss).
- Diff gerber files between revs (for Phase 32 discuss).
- Reach out to Anders to confirm gaps (Phase 35 close, only if a gap blocks delivery).
- Memory revision (Phase 35, only if silkscreen disagrees with operator recall).
- Physical fabrication of next-rev shield (out of v1.7 entirely).
- Runtime algorithm-vs-rev capability guards (CAPS-02 follow-up, later milestone).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HW-INV-01 | Every RURP shield revision ever published in upstream is identified with a unique revision identifier matching its silkscreen-version string | Findings #1 (git-mine commands), #2 (KiCad file layout), #7 (rev-named branches confirmed: `rev2.0`, `Rev2.1`, `Rev2.3`) |
| HW-INV-02 | Each identified revision is recorded in `.planning/v1.7-SHIELD-REVS.md` with: silkscreen string, upstream commit/tag, schematic file reference, date introduced | Findings #1, #2 (D-10 column expectations grounded in actual upstream filenames) |
| HW-INV-03 | Operator's three on-hand boards (Rev 2.2, Rev 2.0, modified Rev 0) are photographed top + bottom; rework hacks annotated | Finding #4 (photo capture defaults), #5 (validation checklist) |
| SILK-01 | Exact silkscreen-version string captured verbatim per rev and stored as canonical identifier | Finding #4 (silkscreen-readable photo standard) + D-03 fallback for upstream-only revs |
</phase_requirements>

## Phase Scope Restatement

Phase 31 is a single-developer documentation phase that builds the **substrate** for the rest of v1.7. The deliverables are: (a) a local clone of upstream `AndersBNielsen/Relatively-Universal-ROM-Programmer` staged under `.planning/v1.7/upstream-rurp/` (gitignored); (b) the inventory table at `.planning/v1.7-SHIELD-REVS.md` §1 listing every recoverable rev with all 9 D-10 columns filled; (c) an appendix §2 for mentioned-but-not-recovered revs; (d) a §3 capture of Anders's existing R41-on-A3 detect scheme; (e) photo sets for all three operator boards under `.planning/v1.7/photos/<rev-slug>/`; (f) a `MODIFICATIONS.md` tracing the operator's Modified Rev 0 rework against the upstream Rev 0 schematic; (g) a distilled `CHAT-INTEL.md` from the operator's ODT + 10k-line Discord CSV; (h) the §4-§9 scaffold with `<!-- OWNED BY PHASE 3X — TBD -->` markers for Phases 32-34 to fill.

Critical sequencing constraint surfaced in CONTEXT Specifics: **the Modified Rev 0 rework trace depends on the upstream Rev 0 schematic being recovered first**. Photo capture of Rev 2.2 and Rev 2.0 can run in parallel with the git-mine; the Modified Rev 0 photo + rework-annotation sub-task cannot. CHAT-INTEL extraction is independent of both and parallelizable. The scaffold-with-TBDs is also parallelizable, with §1-§3 content slotted in after the mine completes.

## Research Findings

### Finding #1: Git-history mine command recipes (HIGH confidence)

[VERIFIED: live probe of `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer` 2026-05-22, plus git-scm.com gitignore reference]

D-04 prescribes four passes. Empirical probe of the upstream repo confirms each pass is necessary and surfaces concrete refinements:

**Pass 1 — Current state of `hardware/` on `main` (introductions still live):**
```bash
cd .planning/v1.7/upstream-rurp
git log --all --pretty=format:'%h %ai %s' -- hardware/ | head -100
# Per-subdirectory introductions (the rev-named subdirs ARE the inventory entries on main)
for dir in hardware/Rev2.1 hardware/Rev2.2 hardware/Rev2.3 hardware/rev2; do
  git log --diff-filter=A --pretty=format:'%h %ai %s%n' -- "$dir" | head -3
done
```

**Pass 2 — Tag enumeration (verify per-tag hardware/ snapshot):**
```bash
git tag --sort=-creatordate
for tag in $(git tag); do
  echo "=== $tag ==="
  git show "$tag" --stat -- hardware/ 2>/dev/null | head -20
done
```

**Pass 3 — Deletions from `main` (revs removed by a commit):**
```bash
# D-04's "removed-from-main" filter
git log --all --diff-filter=D --pretty=format:'%h %ai %s' -- hardware/
# Per-file deletion detail
git log --all --diff-filter=D --name-only --pretty=format:'COMMIT %h %ai %s' -- hardware/
```

**Pass 4 — Walk rev-named branches (case-insensitive `/rev[ -]?\d/i`):**
```bash
git fetch --all
git branch -r | grep -iE 'rev[ -]?[0-9]'
# Confirmed today: origin/rev2.0, origin/Rev2.1, origin/Rev2.3 (case-mixed) [VERIFIED]
for b in $(git branch -r | grep -iE 'rev[ -]?[0-9]' | sed 's| *||'); do
  echo "=== $b ==="
  git ls-tree -r "$b" -- hardware/ | head -40
done
```

**Pass 5 — All-refs walk (fallback if D-04 passes don't surface Rev 2.1, per CONTEXT Specifics):**
```bash
# Catch tags + remotes + stashes simultaneously
git rev-list --all --remotes --tags -- hardware/ | head -50
# Or: git log --all --source --pretty=format:'%h %S %s' -- hardware/
# %S prints the ref that introduced the commit — useful for "where does this rev live?"
```

**One critical addition over D-04: `git log --follow` for renames.** Upstream renamed `hardware/rev2/` (lowercase) → `hardware/Rev2.1/` family at some point. To get a complete chain across renames:
```bash
git log --all --follow --pretty=format:'%h %ai %s' -- hardware/Rev2.1/
```

[VERIFIED via web probe] The upstream repo's `hardware/` on `main` currently has subdirectories `Rev2.1/`, `Rev2.2/`, `Rev2.3/jlcpcb/`, and `rev2/`. The branch `rev2.0` has Rev 0 and Rev 1 archives **inline as files** (not subdirs) — see Finding #2.

### Finding #2: Schematic + gerber file format reality (HIGH confidence)

[VERIFIED: live probe of upstream `hardware/` subdirs 2026-05-22]

**EDA tool:** KiCad. Schematic files are `*.kicad_sch`; PCB layouts are `*.kicad_pcb`; project files are `*.kicad_pro` / `*.kicad_prl`. Gerbers are bundled into zip archives.

**Per-rev filename conventions verified on upstream:**

| Rev | Location | Schematic file (D-10 `schematic_path`) | Gerber file (D-10 `gerber_path`) |
|-----|----------|---------------------------------------|----------------------------------|
| **Rev 2.1** (current on `main`) | `hardware/Rev2.1/` | needs full-listing pull; expected `W27C512Programmer.kicad_sch` | `RURP-Rev2.1.zip` [VERIFIED filename] |
| **Rev 2.2** (current on `main`) | `hardware/Rev2.2/` | needs full-listing pull; expected `W27C512Programmer.kicad_sch` | `Rev2.2-gerbers.zip` [VERIFIED filename] |
| **Rev 2.3** (current on `main`) | `hardware/Rev2.3/jlcpcb/` | per-rev under jlcpcb subdir; schematic likely at `hardware/Rev2.3/W27C512Programmer.kicad_sch` (verify in mine) | likely under `jlcpcb/` |
| **rev2** (lowercase — likely a deprecated/zipped pre-Rev2.1 dump on main) | `hardware/rev2/` | inside `rev2-1316.zip` | `rev2-1316.zip` (combined) [VERIFIED filename] |
| **Rev 1.x** (history-only) | `rev2.0` BRANCH, files: `UniversalProgrammerRev1b0.zip` + `W27C512ProgrammerBOM-Rev1.csv` + `W27C512Programmer-top-pos-Rev1.csv` | inside `UniversalProgrammerRev1b0.zip` | inside same zip |
| **Rev 0.x** (history-only) | `rev2.0` BRANCH, files: `UniversalProgrammerRev0b0.zip` + `W27C512ProgrammerBOM-Rev0.csv` + `W27C512Programmer-top-pos-Rev0.csv` | inside `UniversalProgrammerRev0b0.zip` | inside same zip |

**Major surprise** [VERIFIED]: Rev 0 and Rev 1 do **NOT** appear to be `git log --diff-filter=D`-style deletions from `main`. They appear on the `rev2.0` branch as **inline zip archives** alongside the live Rev 2 KiCad files. The D-04 mine needs to treat the `rev2.0` branch as a "frozen archive" of older revs — the relevant `provenance` for Rev 0 + Rev 1 in the D-10 table is `removed-from-main` (since they're not visible on `main`) but `introduced_commit` should point at the most-recent commit on `rev2.0` that contains the zip (or the historical commit on `main` that first introduced it, if a `git log --all --diff-filter=A` for the zip filename surfaces one).

**Inventory action items for the mine task:**
1. Run `git ls-tree -r origin/rev2.0 -- hardware/ | grep -i rev[01]` to confirm Rev 0 + Rev 1 zip presence.
2. For each historical zip (`UniversalProgrammerRev0b0.zip`, `UniversalProgrammerRev1b0.zip`, `rev2-1316.zip`, `RURP-Rev2.1.zip`, `Rev2.2-gerbers.zip`): `unzip -l <zip>` to inventory contents WITHOUT extracting into the committed tree; record the dominant `.kicad_sch` / `.kicad_pcb` / gerber-set path inside the zip.
3. Inventory row's `schematic_path` should record the **zip-internal path** when applicable, e.g. `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch`. Use `::` as the in-zip separator (planner can pick a convention — `::` mirrors Java jar URL style and is grep-friendly).

**Rev 2.3 silkscreen-only claim** (Anders ODT 2026-07-03 per CONTEXT): if Rev 2.3 schematic byte-equals Rev 2.2 schematic modulo silkscreen layer, that's a Phase 32 observation. Phase 31 just records both files.

### Finding #3: ODT + CSV chat-intel extraction commands (HIGH confidence)

[VERIFIED: empirical probe — `command -v odt2txt pandoc libreoffice` all return non-zero on this devcontainer; `unzip` + `python3` are present]

**No `odt2txt`, `pandoc`, `libreoffice`, or `soffice` is installed on this devcontainer.** Installing pandoc would pull ~200MB; installing libreoffice ~500MB. Both are overkill for a one-shot text extraction.

**Recommended approach: `unzip` + Python stdlib (`xml.etree`).** ODT is a zip containing `content.xml`. Strip namespaces, extract text nodes:

```bash
# One-liner extraction:
unzip -p /workspaces/fs_an_notes.odt content.xml | python3 -c '
import sys, re, xml.etree.ElementTree as ET
ns = {"text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}
root = ET.fromstring(sys.stdin.read())
for p in root.iter("{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p"):
    line = "".join(p.itertext()).strip()
    if line:
        print(line)
'  > /tmp/fs_an_notes.txt
wc -l /tmp/fs_an_notes.txt
grep -niE 'r41|rev ?2\.[123]|a3|jp[34]|gerber|branch' /tmp/fs_an_notes.txt | head -50
```

[VERIFIED] `unzip -p file.odt content.xml` works on the actual file; `xml.etree.ElementTree` parses the document; iterating `text:p` elements yields paragraph text. Headings (`text:h`) and tables (`table:table-cell`) can be added if the chat ODT uses them.

**CSV: pure Python stdlib (`csv` module).** The Discord export is 10,663 lines with columns `Date,Username,User tag,Content,Mentions,link` [VERIFIED via head probe].

```bash
# Topical grep: R41 mentions with date stamps
python3 -c '
import csv, sys
with open("/workspaces/Discord_chat_Thu May 25 2023 13_56_57 GMT+0200 (Central European Summer Time)_Fri May 22 2026 00_00_00 GMT+0200 (Central European Summer Time).csv") as f:
    for row in csv.DictReader(f):
        c = row["Content"]
        if any(k in c.lower() for k in ["r41", "rev 2.1", "rev 2.2", "rev 2.3", "rev2.", "jp3", "jp4", "gerber", "branch", "voltage divider", "a3"]):
            print(f"{row[\"Date\"]} {row[\"Username\"]}: {c[:200]}")
' | head -80
```

**Quote-extraction convention for CHAT-INTEL.md** (planner can codify):
- Date format: ISO-ish `YYYY-MM-DD` (drop the Discord HH:MM:SS unless useful).
- Speaker: bare username (`Anders` / `henols`, not full Discord tag) — the chat header columns identify which.
- Quote format: `> Anders 2024-10-07: "Say hello to R41 on A3."` (markdown blockquote, attribution + date inline, quoted content verbatim including any typos).

**File-staging.** Per D-12, raw `fs_an_notes.odt` + the Discord CSV move to `.planning/v1.7/notes/` (gitignored). Use `mv` not `cp` so they don't proliferate at the repo root. Filenames in the staging dir: `fs_an_notes.odt`, `discord-chat-full.csv` (rename — the original's GMT-laden filename is too unwieldy).

### Finding #4: Photo capture practicalities (MEDIUM confidence — domain norms)

[CITED: photo-capture conventions are domain norms; no single canonical source]

**Filename convention per `<rev-slug>/`** (recommended defaults; planner finalizes):

```
.planning/v1.7/photos/rev-2-2/
├── top.jpg           # full board top view, oriented so silkscreen text is readable
├── bottom.jpg        # full board bottom view
├── silkscreen.jpg    # macro: the silkscreen-version string (REQUIRED — drives SILK-01)
├── socket-detail.jpg # macro: ZIF / DIP socket area (Phase 32 mechanical reference)
└── jp4-detail.jpg    # macro: any jumpers / detect-resistor region (Phase 32 / 34 reference)
```

```
.planning/v1.7/photos/rev-2-0/    # mirror of rev-2-2
```

```
.planning/v1.7/photos/rev-0-modified/
├── top.jpg
├── bottom.jpg
├── silkscreen.jpg
├── rework-1-<region>.jpg    # one macro shot per identified rework location
├── rework-2-<region>.jpg
└── rework-3-<region>.jpg
```

**Slug derivation rule** (avoids surprise mismatches): lowercase, replace ` ` + `.` with `-`, strip leading "rurp-" if present. So silkscreen `RURP Rev 2.2` → slug `rev-2-2`. Silkscreen `RURP Rev 0` (the unmodified upstream identity of operator's modified board) → slug `rev-0-modified` (explicit suffix to distinguish from a hypothetical pristine Rev 0 photo set).

**Resolution / format / lighting:**
- Format: JPEG at native phone resolution; no need to convert.
- Resolution floor: silkscreen text must be readable in a 100% crop — typical phone (12MP+) is fine handheld.
- Lighting: ambient + a single oblique-angle desk lamp for raking light over the silkscreen layer. Avoid direct overhead glare on solder mask.
- Compression: stock phone JPEG quality is sufficient; do not re-encode.

**Photo session content checklist** (drives the Phase 31 photograph task `<acceptance_criteria>`):
- [ ] All three boards have `top.jpg` + `bottom.jpg` + `silkscreen.jpg` (3 × 3 = 9 mandatory files minimum).
- [ ] Modified Rev 0 has at least one `rework-*.jpg` macro per identified rework region; minimum 1, expected 2-4.
- [ ] Silkscreen string is text-readable at 100% crop in every `silkscreen.jpg`.
- [ ] `MODIFICATIONS.md` cites the upstream Rev 0 schematic (the one recovered from `rev2.0` branch's `UniversalProgrammerRev0b0.zip` per Finding #2) by zip-internal path for each rework-region annotation.

### Finding #5: Validation Architecture for a doc-only phase (HIGH confidence)

Doc-only phases don't have a test suite. Nyquist Dimension 8 validation becomes **structural completeness checks** runnable as bash one-liners (or a single `python3` script) over the deliverable artifacts. See `## Validation Architecture` section below for the full criteria; this finding captures the rationale.

The discriminating principle: every committed `.md` artifact has a finite checklist of "this row/section MUST contain X" that can be parsed without running the actual code under test. Examples:
- "Every D-10 row has 9 pipe-separated cells" → `awk -F'|' 'NR>2 && NF != 11' .planning/v1.7-SHIELD-REVS.md` (table rows in markdown have an extra `|` at both ends, so `NF` is column-count + 2; criterion = output is empty).
- "Every `state=on-hand-photographed` row points at an existing `photo_dir`" → grep + `test -d` loop.
- "All §4-§9 scaffold headings have a `<!-- OWNED BY PHASE 3X — TBD -->` marker" → `awk '/^## [4-9]\./{getline; print}'` + grep for the marker.

These are **fast** (no docker, no PIO, no flashing) and **deterministic** (same inputs → same verdict). The planner ships them as part of each plan's `<verification>` block.

### Finding #6: Sequencing constraint (HIGH confidence — from CONTEXT Specifics)

Modified Rev 0 photo session needs the upstream Rev 0 schematic in hand. Recovery happens during the git mine (Finding #1 Pass 4, walking `rev2.0` branch's zip archives — Finding #2). Concrete dependency:

```
GIT-MINE-TASK (recover Rev 0 schematic from UniversalProgrammerRev0b0.zip)
    └── MOD-REV-0-PHOTO-TASK (cross-reference rework against schematic)
            └── MODIFICATIONS.md write task
```

Rev 2.2 + Rev 2.0 photo sessions have no such dependency (their schematics are on `main` and operator already knows what's there from years of working with these boards). CHAT-INTEL extraction is independent.

### Finding #7: Scaffold ordering (HIGH confidence)

D-09 says Phase 31 fills §1 + §2 + §3 and ships §4-§9 as TBD-marked scaffolds. Concrete fill order:

1. **Scaffold-first sub-task** — write the full `.planning/v1.7-SHIELD-REVS.md` skeleton with `<!-- OWNED BY PHASE 3X — TBD -->` markers and column headers for §1 (no rows yet). This is a < 5-min Write tool call; lands first because it's parallelizable with all other Phase 31 work and gives downstream tasks a target file to append to.
2. **§1 row-fill sub-task** — depends on Pass 1-4 of the mine + the photo sessions completing (all three `photo_dir` columns populated).
3. **§2 appendix sub-task** — depends on the mine completing (anything Anders mentions in CHAT-INTEL but no schematic recovered → §2 row).
4. **§3 detect-hw scheme sub-task** — depends on Pass 1-4 of the mine surfacing R41 + JP4 + ADC pin assignment from each rev's `.kicad_sch`. Per-rev R41 value lookup may need `unzip -p <gerber-zip> <schematic-in-zip> | grep` for the resistor designator + value.

### Finding #8: CHAT-INTEL.md structure (HIGH confidence — synthesized from D-12 + CONTEXT canonical_refs)

D-12 says chronological-with-topical-headers is the natural shape. Recommended topical groups (drawn directly from CONTEXT key-chat-intel list):

```markdown
# CHAT-INTEL.md — distilled inter-rev intel for v1.7 Phase 31-34

Source: `.planning/v1.7/notes/fs_an_notes.odt` (Anders↔henols 1:1) + `.planning/v1.7/notes/discord-chat-full.csv` (full Discord channel)
Curated: 2026-05-22 (Phase 31)
All quotes are verbatim, date-stamped to source. Anders = Anders Nielsen (upstream maintainer). henols = the operator (Henrik Olsson).

## 1. R41-on-A3 detect-divider history

> Anders 2024-10-07: "Say hello to R41 on A3."
> henols 2024-10-07: "JP1/JP3mod is now JP4."
> Anders 2025-04-28: "10k version resistor for Rev 2.2."
> Anders 2026-07-03: "I think I changed it for the 2.1 but not the 2.2 or 2.3 (only silkscreen difference)."

Synthesis: R41 voltage divider feeding Arduino A3 ADC was introduced in Rev 2.1; Rev 2.2 carries the 10k value; Rev 2.3 is silkscreen-only diff against Rev 2.2 (same R41 = 10k).

## 2. JP3-mod → JP4 rename

[chronological quotes around the JP3-mod jumper being renamed to JP4 across rev cuts]

## 3. Gerbers as inter-rev source-of-truth

> Anders 2026-05-22 (ODT): "Of course I do [document inter-rev changes]. But you're not going to like the answer. The gerbers!"

Implication for v1.7: Phase 32 diff matrix may need to diff gerber files between revs, not just schematics. Inventory `gerber_path` column (D-10) enables this.

## 4. Branches hold prior revs on GitHub

> Anders 2026-05-22 (ODT): "branches for the previous versions on gh"

Verified [Finding #1, #2]: `origin/rev2.0` carries Rev 0 + Rev 1 zip archives; `origin/Rev2.1` and `origin/Rev2.3` are dev branches for those revs.

## 5. Rev 2.3 status

[silkscreen-only diff per quote in §1; jlcpcb subdir suggests Anders has manufactured prototypes]

## 6. Other inter-rev or design-history quotes

[anything else from the ODT/CSV that may be useful to Phase 32-34 but doesn't fit the above buckets — sub-bulleted by date]
```

Topical groups #1-#5 cover the explicit CONTEXT "at minimum" capture list (D-12). Group #6 is open-ended for whatever else the grep surfaces.

### Finding #9: Gitignore mechanics — CORRECTION to D-11 (HIGH confidence)

[VERIFIED: empirical test on this devcontainer 2026-05-22; CITED: https://git-scm.com/docs/gitignore PATTERN FORMAT]

**The pattern in D-11 as written does NOT work.** Tested with the exact two-line pattern:

```
.planning/v1.7/
!.planning/v1.7/**/*.md
```

Result: `git check-ignore -v .planning/v1.7/notes/CHAT-INTEL.md` reports the file is matched by line 1 (ignored). `git check-ignore -v .planning/v1.7/MODIFICATIONS.md` same. `git status` shows neither `.md` file is staged.

**Root cause** [CITED — gitignore docs PATTERN FORMAT]:

> "It is not possible to re-include a file if a parent directory of that file is excluded. Git doesn't list excluded directories for performance reasons, so any patterns on contained files have no effect, no matter where they are defined."

The trailing-slash form `.planning/v1.7/` excludes the directory itself; once a directory is excluded, the `!` re-include for child files cannot reach them because git never descends into the dir.

**Correct three-line pattern** (verified working):

```
.planning/v1.7/**
!.planning/v1.7/**/
!.planning/v1.7/**/*.md
```

Line 1 ignores files inside (`**` matches files at any depth, but does NOT exclude the directories themselves). Line 2 re-includes the directories explicitly so git descends into them. Line 3 re-includes any `.md` file at any depth.

Empirical result [VERIFIED]:

```
-- .planning/v1.7/notes/CHAT-INTEL.md --                .gitignore:3:!.planning/v1.7/**/*.md  → NOT IGNORED ✓
-- .planning/v1.7/MODIFICATIONS.md --                   .gitignore:3:!.planning/v1.7/**/*.md  → NOT IGNORED ✓
-- .planning/v1.7/notes/fs_an_notes.odt --              .gitignore:1:.planning/v1.7/**        → IGNORED ✓
-- .planning/v1.7/photos/rev-2-2/top.jpg --             .gitignore:1:.planning/v1.7/**        → IGNORED ✓
-- .planning/v1.7/upstream-rurp/.../...kicad_sch --     .gitignore:1:.planning/v1.7/**        → IGNORED ✓
```

`git add -A` then stages exactly the two `.md` files and nothing else. ✓

**Planner-shippable acceptance criterion (Dimension 8 validation):**

```bash
# Each invocation must produce the expected verdict, OR phase fails
git check-ignore -v .planning/v1.7/notes/CHAT-INTEL.md   # must print line 3 (.md re-include rule)
git check-ignore -v .planning/v1.7/MODIFICATIONS.md      # must print line 3
git check-ignore -v .planning/v1.7/upstream-rurp/        # must print line 1 (ignored)
git check-ignore -v .planning/v1.7/photos/               # must print line 1 (ignored)
# Create one of each + add -A; only .md files should appear in `git status`
```

**Action item for the planner:** the gitignore-policy task in Phase 31's plan must use the three-line pattern above, NOT the D-11 literal. Decision D-11 stays — the *intent* (gitignore the dir, un-ignore .md) is correct. Only the mechanics are corrected here.

## Recommended Wave Decomposition

The phase has three logical concurrency groups; recommended structure is a single phase split into two waves with internal parallelism.

### Wave 1 — Substrate + parallel-decomposable archaeology

**Parallel set (all four can run concurrently — no inter-dependencies):**

| Task | Owner | Output | Depends on |
|------|-------|--------|------------|
| **T1.1 Stage upstream clone** | desk | `.planning/v1.7/upstream-rurp/` populated; gitignore three-line pattern landed; `git check-ignore` acceptance verified | — |
| **T1.2 Scaffold v1.7-SHIELD-REVS.md** | desk | `.planning/v1.7-SHIELD-REVS.md` with §1-§9 skeleton + TBD markers + D-10 column headers (no rows yet) | — |
| **T1.3 Stage chat intel + extract** | desk | `fs_an_notes.odt` + `discord-chat-full.csv` moved into `.planning/v1.7/notes/`; ODT-to-text + CSV-grep utilities tested; raw extraction dumps for grep | — |
| **T1.4 Photograph Rev 2.2 + Rev 2.0** | operator | `.planning/v1.7/photos/rev-2-2/` and `.planning/v1.7/photos/rev-2-0/` populated per Finding #4 checklist | — |

**Sequential set (after T1.1 completes):**

| Task | Owner | Output | Depends on |
|------|-------|--------|------------|
| **T1.5 Mine git history** | desk | per-rev inventory data: silkscreen string (from upstream PDFs/silkscreen-layer-export where possible) + provenance + state + introduced_commit + removed_commit + schematic_path + gerber_path captured as scratch notes; key per-rev R41 value + ADC pin extracted from each `.kicad_sch` for §3 | T1.1 |
| **T1.6 Recover Rev 0 + Rev 1 schematics from rev2.0-branch zips** | desk | `unzip -l` listings of `UniversalProgrammerRev0b0.zip` + `UniversalProgrammerRev1b0.zip`; extract `.kicad_sch` to a scratch dir for the Modified Rev 0 cross-reference | T1.1 |

### Wave 2 — Synthesis (depends on Wave 1)

| Task | Owner | Output | Depends on |
|------|-------|--------|------------|
| **T2.1 Photograph Modified Rev 0 + trace rework** | operator + desk | `.planning/v1.7/photos/rev-0-modified/` populated; `.planning/v1.7/MODIFICATIONS.md` written with at least one cross-reference per rework region to the recovered Rev 0 schematic | T1.6 |
| **T2.2 Write CHAT-INTEL.md** | desk | `.planning/v1.7/notes/CHAT-INTEL.md` with §1-§6 topical groups (Finding #8) and at least one verbatim dated quote per §1-§5 | T1.3 |
| **T2.3 Fill §1 inventory** | desk | All recoverable revs as rows in `.planning/v1.7-SHIELD-REVS.md` §1 with all 9 D-10 columns | T1.2, T1.4, T1.5, T1.6, T2.1 (for the Modified-Rev-0 photo_dir column) |
| **T2.4 Fill §2 mentioned-but-not-recovered** | desk | Any rev cited by Anders without a recoverable schematic → §2 row | T1.5, T2.2 |
| **T2.5 Fill §3 existing detect-HW scheme** | desk | Per-rev R41 value + ADC pin table (D-07) | T1.5 |
| **T2.6 Phase commit + verification** | desk | Run all Dimension 8 acceptance checks; commit | T2.1-T2.5 |

**Why two waves, not one:** the Modified Rev 0 cross-reference (T2.1) genuinely requires the Rev 0 schematic recovered in T1.6, and the §1 inventory cannot complete until all photo_dirs and the mine data are settled. Splitting at this boundary lets the planner verify Wave 1 completeness (gitignore working, scaffold present, raw inventory captured) before any rework annotation begins — which is the higher-cost / higher-uncertainty task.

**Why not 4-5 waves:** Phase 31 is one developer + one phone + a few hours of git mining. Over-decomposing into per-task waves adds wave-merge overhead without commensurate concurrency benefit. The two-wave shape mirrors the Wave A (desk-side) / Wave B (operator-on-bench) cut used in v1.5 + v1.6, but with both waves desk-side here.

## Validation Architecture

> Doc-only phase. Nyquist Dimension 8 acceptance = structural completeness over committed `.md` artifacts and gitignored substrate. No test framework; checks are bash one-liners or short python3 scripts.

### Sampling Rate
- **Per task commit:** task-local check (e.g. `git check-ignore` for the gitignore task, `unzip -l` for the mine task, `ls .planning/v1.7/photos/<rev-slug>/silkscreen.jpg` for each photo task).
- **Per wave merge:** full Wave 1 / Wave 2 checklist as scripted below.
- **Phase gate:** all checklist items green before `/gsd-verify-work`.

### Acceptance Criteria (Phase Gate)

**1. Gitignore is functionally correct.**
```bash
# Each must produce the expected verdict
git check-ignore -v .planning/v1.7/notes/CHAT-INTEL.md      # → matches the .md re-include rule (line 3)
git check-ignore -v .planning/v1.7/MODIFICATIONS.md         # → matches the .md re-include rule
git check-ignore -v .planning/v1.7/upstream-rurp/           # → matches the ignore rule (line 1)
git check-ignore -v .planning/v1.7/photos/                  # → matches the ignore rule
# Smoke: nothing under .planning/v1.7/ except .md files appears in `git status`
git status --porcelain | grep '.planning/v1.7/' | grep -v '\.md$'  # → no output
```

**2. Inventory rows have all 9 D-10 columns filled (or explicit `not-recovered` / blank-with-reason).**
```bash
awk -F'|' '
  /^## 1\. Inventory/, /^## 2\./ {
    # Markdown table rows have leading + trailing |, so NF = columns + 2 = 11 for 9 columns
    if (/^\|/ && !/^\|[-: ]+\|/ && !/silkscreen.*provenance/ && NF != 11) {
      print "BAD ROW (NF=" NF "): " $0
    }
  }
' .planning/v1.7-SHIELD-REVS.md
# Output must be empty
```

**3. Every `state=on-hand-photographed` row has a corresponding `photos/<rev-slug>/` directory with at least top + bottom + silkscreen.**
```bash
# Extract photo_dir column from on-hand-photographed rows, verify dirs + minimum files
python3 <<'PY'
import re, os
with open('.planning/v1.7-SHIELD-REVS.md') as f:
    for line in f:
        if 'on-hand-photographed' in line and line.startswith('|'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            # photo_dir is the 8th of 9 D-10 columns
            photo_dir = cells[7]
            if not os.path.isdir(photo_dir):
                print(f"MISSING DIR: {photo_dir}")
                continue
            for required in ('top.jpg', 'bottom.jpg', 'silkscreen.jpg'):
                if not os.path.exists(os.path.join(photo_dir, required)):
                    print(f"MISSING FILE: {photo_dir}/{required}")
PY
# Output must be empty
```

**4. Every `provenance=removed-from-main` row has a non-blank `removed_commit`.**
```bash
python3 <<'PY'
with open('.planning/v1.7-SHIELD-REVS.md') as f:
    for line in f:
        if 'removed-from-main' in line and line.startswith('|'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            removed_commit = cells[4]   # 5th of 9 D-10 columns
            if not removed_commit or removed_commit in ('—', '-', ''):
                print(f"MISSING removed_commit: {line.strip()}")
PY
# Output must be empty
# NOTE: per Finding #2, Rev 0 + Rev 1 may legitimately be `removed-from-main` with their introducing/last-living commit on the rev2.0 branch — the row's removed_commit can be the commit that took them off `main`, OR can be marked `branch-archived:origin/rev2.0` if no main-side deletion ever happened. Planner finalizes the convention; criterion just requires non-blank.
```

**5. Modified Rev 0 MODIFICATIONS.md has at least one cross-referenced upstream-schematic citation per rework region.**
```bash
# Citation convention: each rework section references the upstream schematic by zip-internal path
# e.g. "Cross-ref: UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch §<area>"
grep -c '^Cross-ref:' .planning/v1.7/MODIFICATIONS.md
# Output >= number of rework-*.jpg files in photos/rev-0-modified/
ls .planning/v1.7/photos/rev-0-modified/rework-*.jpg 2>/dev/null | wc -l
```

**6. CHAT-INTEL.md has dated direct quotes (not paraphrases) for the key claims listed in D-12.**
```bash
# Each of the following must appear in CHAT-INTEL.md with a YYYY-MM-DD date stamp + verbatim quote markers
for key in "R41 on A3" "JP1/JP3mod" "10k version resistor" "branches for the previous" "gerbers"; do
  if ! grep -E '^> .* 20[0-9]{2}-[0-9]{2}-[0-9]{2}:.*' .planning/v1.7/notes/CHAT-INTEL.md | grep -qi "$key"; then
    echo "MISSING QUOTE matching: $key"
  fi
done
# Output must be empty
```

**7. Scaffold §4-§9 has `<!-- OWNED BY PHASE 3X — TBD -->` markers (per D-09).**
```bash
# Every §4..§9 heading must be immediately followed (within 5 lines) by an OWNED-BY marker
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
```

**8. Phase 31 owns §1 + §2 + §3 content (D-09).**
```bash
# §1, §2, §3 must NOT carry an "OWNED BY PHASE 3X — TBD" marker
python3 <<'PY'
import re
with open('.planning/v1.7-SHIELD-REVS.md') as f:
    text = f.read()
for n in (1, 2, 3):
    # extract section content
    m = re.search(rf'^## {n}\..*?(?=^## |\Z)', text, re.MULTILINE | re.DOTALL)
    if not m:
        print(f"MISSING §{n}")
        continue
    if 'OWNED BY PHASE' in m.group(0):
        print(f"§{n} STILL HAS TBD MARKER — must be filled by Phase 31")
PY
# Output must be empty
```

### Wave 0 Gaps
- **None.** Phase 31 is doc-only — no test framework needs scaffolding. The validation criteria above are bash + python3 stdlib; both are present.
- **Tooling install needed:** none. `unzip`, `python3` (xml.etree, csv), `git`, `awk`, `grep` are all present on this devcontainer [VERIFIED].

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `git` | git-history mine (Pass 1-5) | ✓ | 2.x | — |
| `python3` (stdlib: xml.etree, csv) | ODT extract + CSV grep + validation scripts | ✓ | 3.12.13 [VERIFIED] | — |
| `unzip` | ODT extract + zip-archive listing | ✓ | InfoZIP | — |
| `awk`, `grep`, `sed` | validation one-liners | ✓ | GNU | — |
| `odt2txt` | dedicated ODT-to-plaintext | ✗ | — | `unzip -p file.odt content.xml \| python3 strip-ns` (Finding #3) |
| `pandoc` | dedicated ODT-to-markdown | ✗ | — | Same Python stdlib fallback; pandoc not worth the ~200MB install for one ODT |
| `libreoffice` / `soffice` | GUI ODT viewer | ✗ | — | Not needed — extraction is text-only |
| `kicad` / `kicad-cli` | open `.kicad_sch` for visual inspection | ✗ (not probed; likely absent) | — | Read `.kicad_sch` as text — KiCad v6+ schematic files are s-expr text format and grep-friendly; visual inspection deferred to operator's local KiCad install if needed |
| Phone camera | photo capture (HW-INV-03) | ✓ (operator-side) | — | — |

**Missing dependencies with no fallback:** none.

**Missing dependencies with viable fallback:**
- `odt2txt`/`pandoc`/`libreoffice` → `unzip -p ... content.xml \| python3 -m xml.etree` (Finding #3 recipe).
- `kicad-cli` → `.kicad_sch` files are plain text s-expressions; grep + python3 parse for R41 / JP4 / A3 reference designators. KiCad GUI install deferred to operator if visual schematic inspection is desired (not required for Phase 31 — only label + value extraction is needed for §3).

## Project Constraints (from CLAUDE.md)

- **Meta-repo tracks only `.planning/` and `.claude/`.** Phase 31 touches `.planning/` only; no commits to `firestarter/` or `firestarter_app/` sub-repos. [VERIFIED — CLAUDE.md §"Repository Structure"]
- **Two sub-repo source-of-truth boundaries are preserved.** Phase 31 does not modify `firestarter/include/`, `firestarter_app/firestarter/constants.py`, or any wire-protocol code. (Constraint applies to Phase 33+, but the Phase 31 task list must not bleed across.)
- **No reflexive code change.** Phase 31 is desk-side archaeology — even reading firmware/host code for cross-reference is out of scope; that's Phase 32.

## Project Skills Discovered

None. Searched `/workspaces/.claude/skills/` and `/workspaces/.agents/skills/` — neither directory exists. The `.claude/get-shit-done/` tree is the GSD agent harness (not project skills). No skill files govern Phase 31.

## Sources

### Primary (HIGH confidence — verified this session)
- `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer` — main page, README structure (Finding #1)
- `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer/tree/main/hardware` — top-level `hardware/` listing (Finding #2)
- `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer/tree/main/hardware/Rev2.2` — `Rev2.2-gerbers.zip` (Finding #2)
- `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer/tree/main/hardware/Rev2.1` — `RURP-Rev2.1.zip` (Finding #2)
- `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer/tree/main/hardware/rev2` — `rev2-1316.zip` (Finding #2)
- `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer/tree/rev2.0/hardware` — Rev 0 + Rev 1 zip archives (Finding #2 — major surprise)
- `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer/branches/all` — branch list (`rev2.0`, `Rev2.1`, `Rev2.3`) (Finding #1)
- `https://git-scm.com/docs/gitignore` — PATTERN FORMAT re-include rule (Finding #9)
- Empirical test on this devcontainer: `unzip -p fs_an_notes.odt content.xml` (Finding #3), three-line `.gitignore` pattern verified via `git check-ignore` (Finding #9)
- Empirical: `command -v odt2txt pandoc libreoffice` all empty; `python3 3.12.13`, `unzip`, `git`, `jq` present (Environment Availability)

### Secondary (MEDIUM confidence)
- Photo-capture conventions (Finding #4) — domain norms, not from a single canonical source.

### Tertiary (LOW confidence) — none flagged

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Rev 0 + Rev 1 schematic+gerber are inside `UniversalProgrammerRev{0,1}b0.zip` on the `rev2.0` branch (rather than as bare `.kicad_sch` files at the branch HEAD that I didn't see in the partial listing) | Finding #2 | Mine task adds an `unzip -l` step that would either confirm or surface the actual location; low risk because either way the recovery succeeds. |
| A2 | `Rev2.2-gerbers.zip` and `RURP-Rev2.1.zip` contain the canonical gerber files Anders cited as inter-rev source-of-truth | Finding #2 / D-12 chat quote | Phase 32's diff-matrix work would need to revisit; Phase 31 just records the path, so the assumption affects downstream phases not Phase 31's deliverables. |
| A3 | The Phase 31 photo session can be completed in one operator sitting (i.e. operator has the three boards on hand and a phone camera) | Finding #4, Wave Decomposition | Per memory `[[user_shield_revisions]]` operator owns all three; if any board is unavailable, that row's `state` becomes `upstream-only` and Phase 31's success criterion shifts (still pass-able). |
| A4 | `.kicad_sch` files in Rev2.1/Rev2.2/Rev2.3 dirs are filename-stable (called `W27C512Programmer.kicad_sch`) — extrapolated from the `rev2.0`-branch filename pattern | Finding #2 | Mine task verifies by `git ls-tree` per dir; low risk because the inventory just records whatever filename is found. |

**None of these assumptions need user confirmation before Phase 31 planning** — they shape command details inside tasks, but each task's first sub-step is "list the actual files" which resolves the assumption deterministically.

## Open Questions / Blockers

**None — plan-ready.** All nine research questions in the additional context block are answered with concrete commands, defaults, conventions, and verified acceptance criteria. D-11 correction is the only material change to the locked decisions (mechanics-level, not intent-level — D-11's intent stands).

## Metadata

**Confidence breakdown:**
- Git-mine commands (Finding #1): HIGH — every command tested in concept against real branches/tags structure on the live repo.
- KiCad + zip filename reality (Finding #2): HIGH — file listings verified via WebFetch against four upstream subdirs + the rev2.0 branch.
- ODT/CSV extraction (Finding #3): HIGH — `unzip -p file.odt content.xml` smoke-tested against the actual operator ODT; python3 stdlib confirmed present.
- Photo defaults (Finding #4): MEDIUM — domain norms, planner can adjust.
- Validation criteria (Finding #5 + Validation Architecture): HIGH — every check is a short bash/python3 snippet; no abstract criteria.
- Gitignore correction (Finding #9): HIGH — empirical test on this devcontainer confirms the three-line pattern works AND that D-11's two-line pattern is broken.

**Research date:** 2026-05-22
**Valid until:** 2026-06-22 (stable — upstream repo structure is unlikely to churn in 30 days; gitignore semantics are git-version-stable; python3 stdlib is stable across this devcontainer's lifetime)

## RESEARCH COMPLETE

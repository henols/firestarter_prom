# Phase 31: Upstream Shield Archaeology — Pattern Map

**Mapped:** 2026-05-22
**Files analyzed:** 8 (4 committed `.md` / gitignore + 4 substrate dirs/files)
**Analogs found:** 4 / 4 committed artifacts (substrate files need no code analog — only the gitignore rule that hides them)

> **Phase-shape caveat (carried from orchestrator brief):**
> Phase 31 produces planning documents + gitignored substrate (clone, photos, raw chat dumps). There is NO firmware/host-CLI/test code being produced. The "closest analogs" are prior-milestone evidence files inside `.planning/` (and the root `.gitignore` for the ignore-pattern change). Planner consumes this map to ship `<read_first>` blocks pointing at the right analogs and `<action>` blocks that mirror established conventions.

---

## File Classification

| New/Modified file | Role | Data flow | Closest analog | Match quality |
|-------------------|------|-----------|----------------|---------------|
| `.planning/v1.7-SHIELD-REVS.md` | canonical doc (multi-section, multi-phase accretion target) | append-only across Phases 31→34; structural completeness | `.planning/v1.6-EVIDENCE.md` (multi-phase accretion); `.planning/v1.3-BENCH-RESULTS.md` (scaffold-first, fill later) | exact (multi-phase accretion pattern) + exact (scaffold-with-comment-markers pattern) |
| `.planning/v1.7/MODIFICATIONS.md` | evidence appendix (operator-attested, cross-referenced) | one rework-region heading per section; cross-ref line per heading | `.planning/v1.5/baselines/CAPTURE-PROCEDURE.md` (anchored metadata table + reproducible recipe sections); `.planning/v1.6-EVIDENCE.md §"Phase 28 — Fix Commit References"` (single-source-of-truth-citation per entry) | role-match (single-file evidence appendix with structural-completeness check) |
| `.planning/v1.7/notes/CHAT-INTEL.md` | distilled-from-raw metadata file (verbatim dated quotes, topical grouping) | source-citing markdown blockquotes + synthesis prose per topic | `.planning/v1.6-EVIDENCE.md §"Hypothesis Disposition"` (table of claim-evidence-verdict triples with cite path) — different shape but same evidence-citation discipline | role-partial (quotes-with-dates is novel to v1.7; closest analog is v1.6's "Cite the source-of-truth" discipline) |
| Root `.gitignore` (modified) | gitignore policy change (3-line append) | one-time append; verified by `git check-ignore` | Current `/workspaces/.gitignore` (existing pattern style: blank-line groupings + inline comments) | exact (same file, just appended) |
| `.planning/v1.7/upstream-rurp/` (clone) | gitignored substrate (binary blob dir) | created once, read at task time, never committed | `.planning/v1.6/consistency-check-runs/` + `.planning/v1.6/bench-logs/` (gitignored runtime artifacts referenced from `.md` log column) | exact (already-precedented pattern of gitignored evidence dirs under `.planning/<version>/`) |
| `.planning/v1.7/photos/<rev-slug>/` | gitignored substrate (image dir) | created once, read at task time, never committed | `.planning/v1.6/consistency-check-runs/<chip>-<board>-<ts>/` (gitignored evidence dirs cross-referenced from a committed `.md` table column) | exact (analog is the cross-referencing convention, not the file format) |
| `.planning/v1.7/notes/fs_an_notes.odt` (moved) | gitignored raw input (binary, source for distillation) | moved from `/workspaces/` root once; never re-read after distillation lands in CHAT-INTEL.md | No prior analog — v1.5/v1.6 never carried raw operator dumps. The pattern this establishes IS the analog for any future Phase 32-34 raw inputs. | no-analog (new pattern; planner cites D-12 + Research Finding #3 directly) |
| `.planning/v1.7/notes/discord-chat-full.csv` (moved) | gitignored raw input (text-CSV, source for distillation) | moved from `/workspaces/` root once | same as above | no-analog |

---

## Pattern Assignments

### `.planning/v1.7-SHIELD-REVS.md` — canonical accretion doc

**Primary analog:** `.planning/v1.6-EVIDENCE.md` (multi-phase accretion artifact)
**Secondary analog:** `.planning/v1.3-BENCH-RESULTS.md` (scaffold-first, fill-later with HTML-comment markers)

**Section-heading + multi-phase-accretion pattern** (from `.planning/v1.6-EVIDENCE.md` lines 1-22, 110-112, 186-188):

```markdown
# v1.6 Evidence — Fix the Read Bug

**Milestone:** v1.6 Fix the Read Bug
**Source backlog:** `.planning/todos/pending/large-read-data-jitter-uno328pb.md` (HIGH; pre-existing, all 3 controllers)
**Cross-phase accretion:** Phase 26 (baseline) → Phase 27 (RCA) → Phase 28 (fix commit refs) → Phase 29 (post-fix inverted verification)
**Schema:** D-08 9-column row schema (Board | Port | Chip | N | SHAs distinct | ...) — locked across all 4 v1.6 phases.

## Summary

Cross-phase evidence-accretion artifact for v1.6. [prose introducing the doc's role]

## Phase 26 — Pre-fix Consistency-Check Baseline (2026-05-21)

| Board | Port | Chip | N | SHAs distinct | ... |
|-------|------|------|---|---------------|-----|
| uno | /dev/ttyACM0 | W27C512 (id 0xda08) | 3 | 1 | ... |

<!-- Phase 27 RCA appends a section here: ## Phase 27 — RCA Findings. Same 9-column schema is the contract — do NOT modify or expand. See CONTEXT.md §D-08. -->

## Phase 27 — RCA Findings (2026-05-21)

[next phase's content lands here]
```

**Apply to `v1.7-SHIELD-REVS.md`:** mirror the frontmatter style (title + bold-metadata block: Milestone / Source / Cross-phase accretion / Schema), then a `## Summary` paragraph, then `## 1. Inventory` / `## 2. Mentioned-but-not-recovered` / `## 3. Existing Detect-HW Scheme (Anders R41-on-A3)` as Phase-31-owned filled sections, then `## 4.` through `## 9.` as TBD-marked scaffolds (D-09 + Finding #7).

**TBD-marker pattern** (from `.planning/v1.3-BENCH-RESULTS.md` lines 14-15, 23-24, 32-33):

```markdown
## Per-Chip-Per-Board Cycle Results (D-08 schema; 14 columns)

| Chip | Board | Date | info | vpp_engaged | chip_id_read | chip_id_db | chip_id_match | blank_pre | write | read | verify | blank_post | log | notes |
|------|-------|------|------|-------------|--------------|------------|---------------|-----------|-------|------|--------|------------|-----|-------|

<!-- Plans 12-01 / 12-02 / 12-03 append one row per (chip, board) pair = 6 rows total when Phase 12 closes. -->
```

**Apply to `v1.7-SHIELD-REVS.md`:** every `## 4.`–`## 9.` heading is immediately followed (within 5 lines, per Phase-gate check #7) by:

```markdown
## 4. Inter-Rev Electrical Differences

<!-- OWNED BY PHASE 32 — TBD -->
```

— exact marker string `<!-- OWNED BY PHASE 32 — TBD -->` (em-dash, single space each side; phase number per D-09 mapping: §4 §5 §6 → Phase 32; §7 → Phase 33; §8 §9 → Phase 34). Same scaffold-with-comment-marker shape v1.3 used, generalised to "OWNED BY PHASE N" wording for downstream readers.

**§1 Inventory table column header** (D-10 lock — verbatim, no reordering):

```markdown
| silkscreen | provenance | state | introduced_commit | removed_commit | schematic_path | gerber_path | photo_dir | notes |
|------------|------------|-------|-------------------|----------------|----------------|-------------|-----------|-------|
```

**Column 1 content rule** (per SILK-01 + D-03): verbatim silkscreen string OR `not-recovered` (with `upstream-<short-sha>` substitute for canonical-id).
**Column 8 (`photo_dir`) content rule** (per Research Finding #4 slug derivation): relative path `.planning/v1.7/photos/<rev-slug>/` where slug is lowercase + `.`→`-` + leading `rurp-` stripped. Modified Rev 0 → `rev-0-modified`.

**§3 Existing Detect-HW Scheme content shape** (per D-07; novel — no prior analog, but mirrors v1.6-EVIDENCE.md's small-table-with-cite-column shape):

```markdown
## 3. Existing Detect-HW Scheme (Anders R41-on-A3)

[prose paragraph citing CHAT-INTEL §1 + the upstream schematics by zip-internal path]

| Rev | R41 value | ADC pin | Voltage divider topology | Schematic citation |
|-----|-----------|---------|--------------------------|--------------------|
| Rev 2.1 | <value from .kicad_sch> | A3 | <JP4 → R41 → A3 → GND> | `hardware/Rev2.1/W27C512Programmer.kicad_sch:<line>` |
| Rev 2.2 | 10k | A3 | (same) | `hardware/Rev2.2/W27C512Programmer.kicad_sch:<line>` |
| Rev 2.3 | (silkscreen-only diff vs 2.2) | A3 | (same) | `hardware/Rev2.3/W27C512Programmer.kicad_sch:<line>` |
```

---

### `.planning/v1.7/MODIFICATIONS.md` — operator-attested rework appendix

**Primary analog:** `.planning/v1.5/baselines/CAPTURE-PROCEDURE.md` (single-file evidence appendix, metadata table + per-region prose + References footer)
**Secondary analog:** `.planning/v1.6-EVIDENCE.md §"Phase 28 — Fix Commit References"` lines 112-160 (per-region/per-commit subheadings, each carrying a `**Cite:**` line — same "anchor every claim" discipline)

**Frontmatter + per-region heading pattern** (from `.planning/v1.5/baselines/CAPTURE-PROCEDURE.md` lines 1-21, abbreviated):

```markdown
# GATE-1.5 Baseline Capture Procedure

**Plan:** 21-01 (Phase 21 — Firmware Target `uno328pb`)
**Anchor:** `firestarter/beta @ 5fd751e` (version-unbumped)
**Purpose:** Document the reproducible recipe used to produce ... GATE-1.5 obligation.

## Captured-from anchor

| Field | Value |
|---|---|
| Firmware sub-repo | ... |
| Branch | ... |
```

**Apply to `MODIFICATIONS.md`:** title + bold-metadata block (Board / Photo session date / Upstream-Rev-0-schematic anchor by zip-internal path / Operator) → `## Rework Region N — <descriptor>` heading per region → `Cross-ref:` line per heading (the Phase-gate check #5 contract — grep counts these against `rework-*.jpg` files).

**Cross-ref line literal** (Phase-gate check #5 grep contract — Research §Validation Architecture):

```markdown
## Rework Region 1 — JP4 jumper insertion (replacing JP3-mod per chat 2024-10-07)

[macro photo: `photos/rev-0-modified/rework-1-jp4.jpg`]

Cross-ref: UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch §JP3-mod region (upstream signal name <X>; rework replaces <Y> with <Z>)

[operator's prose tracing the actual cut + jumper, observed during photo session, with reference to the upstream schematic's nets / designators]
```

**The grep contract:** `grep -c '^Cross-ref:' .planning/v1.7/MODIFICATIONS.md` must return `>= ls .planning/v1.7/photos/rev-0-modified/rework-*.jpg | wc -l`. The `^Cross-ref:` anchor (start-of-line) is the contract — do not indent it inside a list.

---

### `.planning/v1.7/notes/CHAT-INTEL.md` — distilled-quote metadata file

**Primary analog:** No exact prior shape in `.planning/`. **The Research-Finding-#8 template is the planner's authoritative shape** (chronological-with-topical-headers, mirroring D-12). Use that template verbatim.

**Secondary analog (citation discipline):** `.planning/v1.6-EVIDENCE.md §"Hypothesis Disposition"` table (lines 33-42) — every row has an `Evidence cite` column with a real path. Same "anchor every claim to a source" discipline applies to CHAT-INTEL's quotes, just expressed as markdown blockquotes instead of table cells.

**Blockquote-with-date format** (Research Finding #3 codification + Phase-gate check #6 grep contract):

```markdown
> Anders 2024-10-07: "Say hello to R41 on A3."
> henols 2024-10-07: "JP1/JP3mod is now JP4."
> Anders 2025-04-28: "10k version resistor for Rev 2.2."
> Anders 2026-07-03: "I think I changed it for the 2.1 but not the 2.2 or 2.3 (only silkscreen difference)."

Synthesis: R41 voltage divider feeding Arduino A3 ADC was introduced in Rev 2.1; Rev 2.2 carries the 10k value; Rev 2.3 is silkscreen-only diff against Rev 2.2 (same R41 = 10k).
```

**The grep contract** (Phase-gate check #6 — Research §Validation Architecture §6):

```bash
grep -E '^> .* 20[0-9]{2}-[0-9]{2}-[0-9]{2}:.*' .planning/v1.7/notes/CHAT-INTEL.md
```

The line MUST start with `> ` (blockquote marker), MUST contain a 4-digit year + `-MM-DD` date, MUST end the date with `:` before the verbatim quote. Topical headers `## 1. R41-on-A3 detect-divider history` etc. follow Research Finding #8's six-group template.

**Apply to `CHAT-INTEL.md`:** Planner copies the Finding-#8 template (Research §Finding 8, lines 271-310 in `31-RESEARCH.md`) as the initial scaffold, then the executor fills §1–§5 with extracted quotes + §6 with the open-ended grep surfaceds.

---

### Root `.gitignore` (modified) — 3-line append per Research Finding #9 correction

**Analog:** Current `/workspaces/.gitignore` (verbatim — preserve the existing 7-line shape):

```gitignore

.claude/
.pio/
# Generated by .devcontainer/post-create.sh — keeps PlatformIO IDE working from repo root
platformio.ini

# Python bytecode (codegen tools etc.)
__pycache__/
*.py[cod]
```

**Existing-pattern conventions observed:**
- Blank line at top of file (line 1)
- Blank-line-separated logical groups (`.claude/` + `.pio/` group; `platformio.ini` standalone with inline comment; `__pycache__/` + `*.py[cod]` group)
- Comment lines start with `# ` and precede the rule they describe
- No trailing-slash inconsistency — directories carry trailing `/`

**Append pattern** (Research Finding #9 verified working — the three-line correction over D-11):

```gitignore

# v1.7 milestone substrate — gitignore everything under .planning/v1.7/ except .md files
# (raw chat dumps, upstream clone, photo binaries stay local; distilled .md commits)
.planning/v1.7/**
!.planning/v1.7/**/
!.planning/v1.7/**/*.md
```

**Apply to root `.gitignore`:** append (do not overwrite) the comment-pair + three-line pattern at the end of the file, separated by one blank line from the existing `*.py[cod]` line. Verification command (Phase-gate check #1):

```bash
git check-ignore -v .planning/v1.7/notes/CHAT-INTEL.md      # → matches line 3 (the .md re-include)
git check-ignore -v .planning/v1.7/MODIFICATIONS.md         # → matches line 3
git check-ignore -v .planning/v1.7/upstream-rurp/           # → matches line 1 (the ** rule)
git check-ignore -v .planning/v1.7/photos/                  # → matches line 1
```

> **DO NOT use D-11's two-line literal** (`.planning/v1.7/` + `!.planning/v1.7/**/*.md`). That pattern is broken — once the directory itself is excluded, git stops descending and the `!` re-include cannot reach child files (git-scm.com gitignore PATTERN FORMAT). Research Finding #9 verified the three-line correction empirically on this devcontainer.

---

### Gitignored substrate (`upstream-rurp/`, `photos/<rev-slug>/`, `notes/*.odt`, `notes/*.csv`)

**No code-pattern analog needed.** Pattern-relevant guidance for these:

| Substrate | Pattern-relevant convention |
|-----------|------------------------------|
| `.planning/v1.7/upstream-rurp/` | Created by `git clone https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer .planning/v1.7/upstream-rurp` once during T1.1 (Research §Wave 1). Hidden by the `.planning/v1.7/**` gitignore rule. Read by downstream tasks via direct path; never committed. **Analog for the cross-referencing convention:** `.planning/v1.6-EVIDENCE.md` line 16 cites `.planning/v1.6/consistency-check-runs/W27C512-uno-20260521-133418/` from a `Log` column in a committed `.md` — same pattern: gitignored evidence dir, path cited from the committed doc. |
| `.planning/v1.7/photos/<rev-slug>/{top,bottom,silkscreen}.jpg` + `rework-*.jpg` | Filename convention locked by Research Finding #4. Hidden by same `**` rule. Cited from `v1.7-SHIELD-REVS.md` §1 `photo_dir` column (D-10 column 8). Phase-gate check #3 validates dir existence + 3-file minimum per `state=on-hand-photographed` row. **Mandatory files per dir:** `top.jpg`, `bottom.jpg`, `silkscreen.jpg` (silkscreen text legible at 100% crop for SILK-01). `rework-*.jpg` for rev-0-modified only. |
| `.planning/v1.7/notes/fs_an_notes.odt` | Moved (`mv`, not `cp`) from `/workspaces/fs_an_notes.odt` during T1.3. Source for CHAT-INTEL.md distillation (extracted via `unzip -p ... content.xml \| python3 -c '...xml.etree...'` per Research Finding #3). After distillation lands, file is never re-read in Phase 31. |
| `.planning/v1.7/notes/discord-chat-full.csv` | Moved (`mv`) from `/workspaces/Discord_chat_*.csv` during T1.3, renamed to drop the GMT-laden filename. Source for CHAT-INTEL.md distillation (extracted via `python3 -c 'import csv...'` per Research Finding #3). |

---

## Shared Patterns

### Pattern A — Evidence-accretion canonical doc at `.planning/v<version>-<EVIDENCE-noun>.md`

**Source:** `.planning/v1.3-BENCH-RESULTS.md`, `.planning/v1.5-BENCH-RESULTS.md`, `.planning/v1.6-EVIDENCE.md` (three-version precedent)
**Apply to:** `.planning/v1.7-SHIELD-REVS.md`

**Convention:** single canonical `.md` at `.planning/` root, named `v<version>-<NOUN>.md`. The noun reflects the milestone's signature artifact: `BENCH-RESULTS` (v1.3/v1.5: bench rows), `EVIDENCE` (v1.6: cross-phase RCA accretion), `SHIELD-REVS` (v1.7: rev inventory + scheme delta). All milestone phases append to this single file; do not split per-phase. Phase 31 ships the §1-§9 skeleton + the §1-§3 content; Phases 32-34 fill §4-§9 in-place.

### Pattern B — Multi-phase accretion comment markers

**Source:** `.planning/v1.6-EVIDENCE.md` lines 20, 110-111, 186-187 (`<!-- Phase NN appends ... here -->`); `.planning/v1.3-BENCH-RESULTS.md` lines 14-15 (`<!-- Plans NN-NN append ... -->`)
**Apply to:** `v1.7-SHIELD-REVS.md` §4-§9 + the §2 "Mentioned-but-not-recovered" appendix anchor

**Convention:** every TBD section carries one `<!-- OWNED BY PHASE 3X — TBD -->` marker within 5 lines of its `## N.` heading. Marker is the literal contract for Phase-gate check #7. When the downstream phase fills the section, the planner+executor of that phase replaces the marker with the actual content; Phase 35 close verifies all markers are gone (the §1-§3 owned-by-31 markers must be absent at Phase 31 close per Phase-gate check #8).

### Pattern C — Single-source-of-truth path citations

**Source:** `.planning/v1.6-EVIDENCE.md §"Hypothesis Disposition"` (every row has an `Evidence cite` column pointing at `.planning/v1.6/consistency-check-runs/<dir>/`); `.planning/v1.6-EVIDENCE.md §"Phase 28 — Fix Commit References"` lines 137-143 (`**Function modified:** firestarter/src/boards/leonardo_rurp_shield.cpp:rurp_set_data_input`)
**Apply to:** All §3 R41-value rows, all MODIFICATIONS.md `Cross-ref:` lines, all CHAT-INTEL.md synthesis paragraphs

**Convention:** every factual claim points at a concrete path. For schematic excerpts: zip-internal path `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch` (the `::` separator follows Research Finding #2 — Java-jar style, grep-friendly). For commits: full SHA + subject. For chat quotes: `> Speaker YYYY-MM-DD: "verbatim text"`. Never paraphrase a quote that can be cited verbatim.

### Pattern D — Gitignored evidence directories under `.planning/v<version>/`

**Source:** `.planning/v1.6/consistency-check-runs/`, `.planning/v1.6/bench-logs/`, `.planning/v1.6/post-fix-runs/`, `.planning/v1.5/baselines/` (some files committed via per-file gitignore exceptions)
**Apply to:** `.planning/v1.7/upstream-rurp/`, `.planning/v1.7/photos/<rev-slug>/`, `.planning/v1.7/notes/`

**Convention:** runtime/raw substrate goes into `.planning/v<version>/<purpose>/` subdirs. Phase 31 generalises the v1.6 precedent (per-purpose dirs, each ignored or partly-ignored) into a single `.planning/v1.7/**`-ignore + `!**.md` re-include rule. The cross-referencing convention (path cited from a committed `.md`) is preserved verbatim.

### Pattern E — Structural-completeness validation via short shell + python3-stdlib

**Source:** Phase 31's own Research §Validation Architecture (lines 405-531 of `31-RESEARCH.md`) and `31-VALIDATION.md` §"Phase Gate Acceptance Criteria"
**Apply to:** Every Phase 31 task `<acceptance_criteria>` block

**Convention:** doc-only phase = no test framework; every acceptance check is a single bash one-liner or short python3 stdlib snippet. The eight phase-gate checks (`31-VALIDATION.md` §"Phase Gate Acceptance Criteria") run in <5 s total. Planner must inline the relevant per-task check directly into each plan's `<acceptance_criteria>` (do not defer to a "later script"). Each check produces empty output on success.

---

## No Analog Found

| Substrate | Role | Reason |
|-----------|------|--------|
| `.planning/v1.7/notes/fs_an_notes.odt` (move) | gitignored raw operator dump (binary ODT) | First time `.planning/` carries an ODT. Pattern is established here. |
| `.planning/v1.7/notes/discord-chat-full.csv` (move) | gitignored raw export (CSV) | First time `.planning/` carries a CSV. Pattern is established here. |
| `.planning/v1.7/upstream-rurp/` (clone) | gitignored upstream-source-mirror | First time `.planning/` mirrors a non-firestarter upstream repo. Pattern is established here. |

For all three, the planner cites Research §Finding #3 (ODT/CSV extraction), Research §Finding #1+#2 (clone + per-rev file layout), and the Pattern-D gitignore convention. The executor receives a `mv` / `git clone` command + the gitignore rule that hides the result. No `<read_first>` block needed — these have no prior conventions to mirror.

---

## Metadata

**Analog search scope:** `/workspaces/.planning/v1.3*.md`, `/workspaces/.planning/v1.5*.md`, `/workspaces/.planning/v1.6-EVIDENCE.md`, `/workspaces/.planning/v1.5/baselines/CAPTURE-PROCEDURE.md`, `/workspaces/.planning/milestones/v1.4-ROADMAP.md`, `/workspaces/.planning/milestones/v1.5-ROADMAP.md`, `/workspaces/.gitignore`
**Files scanned:** 8 (4 committed `.md` artifacts + 1 root `.gitignore` + 3 directory listings of v1.X substrate dirs)
**Pattern extraction date:** 2026-05-22

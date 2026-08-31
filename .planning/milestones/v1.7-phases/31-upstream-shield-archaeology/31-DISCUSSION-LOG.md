# Phase 31: Upstream Shield Archaeology - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in [31-CONTEXT.md](31-CONTEXT.md) — this log preserves the alternatives considered.

**Date:** 2026-05-22
**Phase:** 31-upstream-shield-archaeology
**Areas discussed:** History-only revs (no operator board), Rework annotation for Modified Rev 0, `.planning/v1.7-SHIELD-REVS.md` scaffold

---

## Area Selection (entry)

Presented four gray areas. User selected three (skipped "Photo storage strategy" — covered later via the gitignore decision in the scaffold area).

| Gray area | Selected |
|---|---|
| Photo storage strategy | |
| History-only revs (no operator board) | ✓ |
| Rework annotation for Modified Rev 0 | ✓ |
| `.planning/v1.7-SHIELD-REVS.md` scaffold | ✓ |

---

## History-only revs (no operator board)

### Q1: Minimum inventory row for shield revs that only exist in upstream git history

| Option | Description | Selected |
|--------|-------------|----------|
| Strict — schematic file required | Include only revs where we can locate an actual schematic file in the upstream commit that introduced it. Mentioned-but-not-recovered revs go in a separate appendix. | ✓ |
| Permissive — commit + label is enough | Include any rev mentioned anywhere in upstream history even if no schematic file survives. Inventory row may have blank cells. | |
| Bracket-only — timeline citation | If a rev is referenced but the artifact is gone, capture it as a one-line timeline note rather than a full inventory row. | |

### Q2: Tagging history-only inventory rows for downstream phase consumption

| Option | Description | Selected |
|--------|-------------|----------|
| Two columns: provenance + state | `provenance` ∈ {on-main, removed-from-main}; `state` ∈ {on-hand-photographed, upstream-only}. Two orthogonal axes. | ✓ |
| Single 'status' column | One enum column conflating provenance with verification state. | |
| Flag with inline footnotes | Single bool 'on-hand?' column + `[¹]` markers for provenance details. | |

### Q3: Canonical identifier for a history-only rev with no readable silkscreen string

| Option | Description | Selected |
|--------|-------------|----------|
| `upstream-<commit-short-sha>` | Introducing commit's short SHA. Silkscreen marked `not-recovered`. Honors SILK-01 verbatim spirit by explicitly marking absence. | ✓ |
| Schematic-file-name derived | Basename of the schematic file. Breaks if upstream renames the file later. | |
| Inferred from version semantics | Assign an inferred name based on neighboring revs. Conflicts with SILK-01's verbatim requirement. | |

### Q4 (REVISED): Git-history mine depth

Original answer was "Main + tags + filter-D scan", but the Anders↔henols chat (ODT 2026-05-22) shows Anders saying "There should be branches for the previous versions on gh." This revealed the original Q4 decision was wrong; re-asked and locked the corrected answer.

| Option | Description | Selected |
|--------|-------------|----------|
| Main + tags + filter-D + named branches | Walk main + tags + `--diff-filter=D` + branches matching `/rev[ -]?\d/i`. Skip WIP/feature branches that don't look rev-named. | ✓ |
| All refs (deepest) | Walk every ref. Highest noise. | |
| Ask Anders directly via the chat | Skip speculation, ask Anders. Blocks Phase 31 on synchronous reply. | |

**Notes:** Original "Main + tags + filter-D scan" decision was reopened after the chat files revealed Anders's branches-hold-prior-revs statement. Documented in 31-DISCUSS-CHECKPOINT.json history.

---

## Rework annotation for Modified Rev 0

### Q1 (initial): Source of truth for Modified Rev 0 hardware-bug-A/B rework details

| Option | Description | Selected |
|--------|-------------|----------|
| Operator has notes — hand them over | Operator has written notes / chat history; paste or point at a file. | ✓ (initially) |
| Trace by visual inspection | Trace during photo capture against upstream schematic. | |
| Mixed — memory recall + photos | Dictate broad strokes + photos for the rest. | |

User pointed at `/workspaces/fs_an_notes.odt` + `/workspaces/Discord_chat_..._.csv`. On reading, those files turned out to be the 2-year Anders↔henols Discord chat archive — upstream-investigation intel, NOT personal rework notes on the Modified Rev 0. Re-asked.

### Q1b (re-asked): Re-route given the notes don't cover the Modified Rev 0 rework

| Option | Description | Selected |
|--------|-------------|----------|
| Trace by visual inspection | Macro photos + cross-reference upstream Rev 0 schematic; result in MODIFICATIONS.md alongside photos. | ✓ |
| Memory recall + photos | Operator dictates broad strokes; photos for the rest. | |
| Defer to Phase 34 — not load-bearing | Phase 31 only needs silkscreen + photos; let Phase 32/34 trace when needed. | |

### Q2: Memory says "modified Rev 0" — chat evidence pointed at modified Rev 1. Which is correct?

| Option | Description | Selected |
|--------|-------------|----------|
| It's a modified Rev 1 — update memory | Chat evidence right; update memory. | |
| It really is a Rev 0 | Memory right; operator's third board is a genuine Rev 0 with separate rework. Chat references to "Rev 1" were operator's prior/separate work. | ✓ |
| You own both | Operator has both a modified Rev 1 AND an unmodified Rev 0. | |
| Verify at photo capture | Defer to silkscreen inspection. | |

### Q3: Anders's R41-on-A3 voltage-divider-into-ADC scheme already exists from Rev 2.1+. How should this reshape v1.7?

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 31 documents what exists; Phase 34 adds firmware | Treat Anders's existing R41/A3 scheme as substrate. Phase 31 inventories it. Phase 34 only delivers firmware ADC read + band lookup + handshake report. | ✓ |
| Phase 31 documents existing; Phase 34 extends with new resistor recommendation | Phase 34 retains freedom to recommend different resistor values for future Rev 2.4. | |
| Out of scope for Phase 31 | Don't touch in Phase 31 discussion. | |

### Q4: Location for Discord/chat notes as canonical refs

| Option | Description | Selected |
|--------|-------------|----------|
| Move to `.planning/v1.7/notes/` (gitignored) | Mirror upstream-rurp clone pattern. | ✓ |
| Move to `.planning/v1.7/notes/` (committed) | Pros: recoverable. Cons: ~1.5MB binary commit. | |
| Leave at repo root, absolute path | Workstation-specific. | |
| Extract to CHAT-INTEL.md (committed) | Distill key intel into structured markdown. Best signal-to-noise. | (later folded into Q5/Q3 of scaffold area) |

### Q5: Reach out to Anders for canonical confirmation?

| Option | Description | Selected |
|--------|-------------|----------|
| No — mine artifacts, don't ping the author | Phase 31 stays self-sufficient. Gaps captured as Phase 35 follow-up todos. | ✓ |
| Yes — prepare a question list | Async dependency on Anders. | |
| Light touch — send only blockers | Pragmatic middle path. | |

---

## `.planning/v1.7-SHIELD-REVS.md` scaffold

### Q1: Scaffold scope — full skeleton vs. Phase-31-section-only

| Option | Description | Selected |
|--------|-------------|----------|
| Full skeleton, Phase 31 fills only inventory sections | Phase 31 creates full document with `<!-- OWNED BY PHASE NN — TBD -->` markers. Phases 32-34 fill in-place. | ✓ |
| Phase 31 only writes Inventory + Silkscreen sections | Document grows incrementally; downstream phases append. | |
| Scaffold owned by Phase 35 | Phase 31 writes fragment; Phase 35 stitches everything together. | |

### Q2: Inventory table column order

| Option | Description | Selected |
|--------|-------------|----------|
| silkscreen \| provenance \| state \| introduced_commit \| removed_commit \| schematic_path \| gerber_path \| photo_dir \| notes | Silkscreen first (canonical ID per SILK-01). Both schematic and gerber paths. | ✓ |
| Same columns + rev-slug primary key | Filename-safe slug as primary key; tooling-friendly. | |
| Minimal core columns + nested per-rev sections | 4-column table; details in `### <silkscreen>` subsections. | |

### Q3 (initial): Gitignore approach

| Option | Description | Selected |
|--------|-------------|----------|
| Add `.planning/v1.7/` to root `.gitignore` | Catch-all under repo root. | |
| Add `.planning/.gitignore` with `v1.7/` entry | Scoped to `.planning/`. | |
| Selective — commit notes/, gitignore the rest | Mixed. | |

User responded with a freeform question: "Whats the prefered way to handle the planning, commit or ignore?" — asked for guidance. Provided GSD convention explanation and re-asked with three clarified options.

### Q3b (re-asked with convention explained):

| Option | Description | Selected |
|--------|-------------|----------|
| Gitignore `.planning/v1.7/` + `!` un-ignore `**/*.md` | Single-rule expression: upstream clone + photos + raw binaries local-only; text artifacts committed. | |
| Gitignore the specific subdirs only | More explicit; future subdirs default to committed (risk of accidental binary commit). | |
| Also extract CHAT-INTEL.md (committed) | Same as recommended + adds CHAT-INTEL.md distillation to Phase 31 deliverables. | (then re-asked as confirmation) |

### Q3c (final confirmation):

User responded with another freeform "whats recomended to gsd to work correct" — provided the GSD-correct rationale (downstream agents Read text artifacts via `Read`; binaries are local substrate they can't consume) and locked the recommended path.

| Option | Description | Selected |
|--------|-------------|----------|
| Confirm — lock and continue | Gitignore `.planning/v1.7/` + `!**/*.md` un-ignore + CHAT-INTEL.md added to Phase 31 deliverables. | ✓ |
| Confirm without CHAT-INTEL.md | Leave intel extraction to Phase 32. | |
| Different scope | Operator describes alternative. | |

---

## Claude's Discretion

- Photo capture protocol details (resolution, file format, lighting, naming inside `<rev>/`) — planner decides at plan time.
- MODIFICATIONS.md internal structure (heading hierarchy, schematic citation format) — planner decides.
- CHAT-INTEL.md internal structure (chronological vs topical grouping) — planner decides (recommend chronological with topical headers).
- Phase 31 wave decomposition (single wave vs upstream-clone + history-mine + photograph + scaffold waves) — planner decides natural cut points.

---

## Deferred Ideas

- **Phase 34 scope rewrite.** Anders's existing R41-on-A3 scheme reframes Phase 34 from green-field hardware design to firmware plumbing. `/gsd-discuss-phase 34` should re-align REQUIREMENTS DETECT-HW-01/02 phrasing before planning.
- **Phase 32 gerber diff.** Anders confirmed gerbers are his inter-rev source-of-truth; Phase 32 may need to diff gerbers (not just schematics).
- **Phase 35 Anders-questions.** Light-touch fallback if Phase 31 mining leaves unresolvable gaps.
- **Memory update.** If Phase 31 photo session reveals operator's third board silkscreen differs from `[[user_shield_revisions]]` memory, update memory then.
- **Out of v1.7 entirely:** physical fabrication of next-rev shield (operator-side); runtime algorithm-vs-rev capability guards (CAPS-02 follow-up for a later milestone).

---

## Reviewed Todos (cross-referenced, not folded)

- `avrdude-mcu-detection-fallback.md` — v1.5 carryover; firmware/host concern; not Phase 31 scope.
- `large-read-data-jitter-uno328pb.md` — v1.6 milestone scope; resumes after v1.7.
- `w27c512-eeprom-misclassification.md` — separate backlog; not Phase 31.

None folded — discussion stayed within Phase 31's archaeology + inventory domain.

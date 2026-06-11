# Phase 31: Upstream Shield Archaeology - Context

**Gathered:** 2026-05-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 31 ships an authoritative inventory of every RURP shield revision ever published — every rev that exists in the upstream `AndersBNielsen/Relatively-Universal-ROM-Programmer` repository (on `main`, in tags, in rev-named branches, or removed by a commit on `main`) is identified with a canonical silkscreen-string identifier, a recorded provenance + state, and a schematic file reference. Operator's three on-hand boards (Rev 2.2, Rev 2.0, modified Rev 0) are photographed top + bottom; the Modified Rev 0's rework is traced by visual inspection against the upstream Rev 0 schematic and recorded as MODIFICATIONS.md. Anders↔henols Discord chat intel is distilled into a structured CHAT-INTEL.md so Phases 32-34 don't need the raw ODT/CSV. The canonical reference doc `.planning/v1.7-SHIELD-REVS.md` is scaffolded with the full Phase-31-through-Phase-34 section skeleton; Phase 31 fills only the Inventory + Silkscreen + Mentioned-but-not-recovered Appendix + Existing-Detect-HW (Anders's R41-on-A3 scheme) sections.

Desk-side only. No sub-repo (firestarter/, firestarter_app/) commits. Meta-repo `v1.7-shield-investigation` branch off `main`.

</domain>

<decisions>
## Implementation Decisions

### History-Only Revs (no operator board on hand)

- **D-01: Minimum inventory bar — schematic file required.** Only revs whose schematic file is recoverable from upstream history enter the main inventory table. Revs mentioned-but-no-schematic-survives go in a separate "Mentioned-but-not-recovered" appendix at the bottom of `v1.7-SHIELD-REVS.md`. Rationale: avoids polluting the Phase 32 diff matrix with rows that can't be compared.
- **D-02: Two-column tagging — `provenance` + `state`.** Each inventory row has `provenance ∈ {on-main, removed-from-main}` AND `state ∈ {on-hand-photographed, upstream-only}`. Downstream phases filter by `state == on-hand-photographed` when an electrical claim needs bench verification, by `provenance` for commit citation. Two orthogonal axes capture the real signal.
- **D-03: Canonical ID for silkscreen-not-recoverable revs.** Use `upstream-<commit-short-sha>` (the introducing commit's short SHA, e.g. `upstream-a1b2c3d`) and mark the silkscreen column `not-recovered`. Honors SILK-01's verbatim requirement by explicitly marking absence. Immune to upstream rebase since SHA is pinned.
- **D-04: Git-history mine depth.** `git log -p hardware/` on main + `git tag` enumeration with `git show <tag>:hardware/` per tag + `git log --diff-filter=D -- hardware/` + walk any branch matching regex `/rev[ -]?\d/i`. Skip WIP/feature branches that don't match the rev-naming convention. Rationale: Anders explicitly stated (ODT chat 2026-05-22) that "branches for the previous versions" exist on GitHub.

### Modified Rev 0 Rework Annotation

- **D-05: Operator's third board IS a genuine Rev 0** (memory `[[user_shield_revisions]]` is correct as-is; chat references to "Rev 1" were operator's prior work / other people's boards). Canonical identifier: per silkscreen verbatim (captured at photo session).
- **D-06: Rework details traced by visual inspection during photo capture.** No pre-existing rework notes exist for the operator's Modified Rev 0 (the chat files are upstream-investigation, not personal rework notes). During Phase 31's photo session, take macro shots of the rework regions (cuts + jumpers); cross-reference each modification against the upstream Rev 0 schematic; record findings in `.planning/v1.7/MODIFICATIONS.md` (committed text, Phase 32 capability matrix reads it).
- **D-07: Anders's existing R41-on-A3 voltage-divider-into-ADC scheme is inventoried in Phase 31.** Per ODT chat: Anders introduced version-detect voltage divider at JP4 / R41 / Arduino A3 starting Rev 2.1; Rev 2.2 uses 10k; Rev 2.3 is silkscreen-only diff vs Rev 2.2 (same JP4 scheme). Phase 31 captures per-rev R41 values + ADC pin assignment from upstream schematics + gerbers. This REFRAMES Phase 34 scope: it is no longer green-field hardware design; Phase 34's job becomes firmware ADC read + voltage-band lookup + handshake report (firmware plumbing on existing upstream substrate). Flagged in `<deferred>` for Phase 34 discuss to re-align ROADMAP/REQUIREMENTS DETECT-HW phrasing.
- **D-08: Do NOT contact Anders for Phase 31 confirmation.** Mine artifacts only. Unresolved gaps → Phase 35 follow-up todos.

### `.planning/v1.7-SHIELD-REVS.md` Scaffold

- **D-09: Phase 31 creates the FULL document skeleton.** Sections + ownership markers:
  - `## 1. Inventory` (Phase 31 fills)
  - `## 2. Mentioned-but-not-recovered` (Phase 31 fills)
  - `## 3. Existing Detect-HW Scheme (Anders R41-on-A3)` (Phase 31 fills, per D-07)
  - `## 4. Inter-Rev Electrical Differences` `<!-- OWNED BY PHASE 32 — TBD -->`
  - `## 5. Inter-Rev Mechanical Differences` `<!-- OWNED BY PHASE 32 — TBD -->`
  - `## 6. Per-Rev Capability Matrix` `<!-- OWNED BY PHASE 32 — TBD -->`
  - `## 7. Silkscreen → Code Alias Table` `<!-- OWNED BY PHASE 33 — TBD -->`
  - `## 8. Detect-HW Schematic Delta (next rev)` `<!-- OWNED BY PHASE 34 — TBD -->`
  - `## 9. Per-Rev Expected ADC Band Table` `<!-- OWNED BY PHASE 34 — TBD -->`
  Phase 35 removes the TBD markers as it closes.
- **D-10: Inventory table column order (locked, all phases agree).**
  ```
  | silkscreen | provenance | state | introduced_commit | removed_commit | schematic_path | gerber_path | photo_dir | notes |
  ```
  Silkscreen first (canonical ID per SILK-01). `removed_commit` blank for current revs. Both `schematic_path` AND `gerber_path` columns since Anders confirmed (ODT chat 2026-05-22) "the gerbers" are his inter-rev source-of-truth. `photo_dir` points at `.planning/v1.7/photos/<rev-slug>/` (gitignored). `notes` for free-form caveats.
- **D-11: Gitignore policy — gitignore `.planning/v1.7/` with `!` un-ignore for `.md` files.** Root `.gitignore` gets:
  ```
  .planning/v1.7/
  !.planning/v1.7/**/*.md
  ```
  Upstream clone (`upstream-rurp/`), photos (`photos/`), raw chat dumps (`notes/*.odt`, `notes/*.csv`) all stay local-only. Committed text files: `MODIFICATIONS.md`, `CHAT-INTEL.md`, anything Phase 32-34 produces under `.planning/v1.7/`. `.planning/v1.7-SHIELD-REVS.md` lives OUTSIDE the ignored dir and is committed normally. GSD-correct rationale: downstream agents (researcher, planner, executor, verifier) need to `Read` text artifacts; binary blobs are local substrate they can't consume.
- **D-12: CHAT-INTEL.md is a Phase 31 deliverable.** Distill the inter-rev intel from `/workspaces/fs_an_notes.odt` + the Discord CSV into a structured markdown at `.planning/v1.7/notes/CHAT-INTEL.md` (committed). At minimum capture: Anders's R41-on-A3 history (Rev 2.1 introduced, Rev 2.2 uses 10k, Rev 2.3 silkscreen-only); JP3-mod → JP4 rename rationale; gerbers-as-source-of-truth; "branches hold prior revs" statement; any other inter-rev or detect-hw quotes from Anders or henols. Direct quotes with date stamps. Raw ODT + CSV stay gitignored under `.planning/v1.7/notes/`.

### Claude's Discretion

- Photo capture protocol details — resolution (just "sufficient to read silkscreen"), file format, lighting, angle, naming convention within `<rev>/` dir. Planner decides defaults at plan time.
- MODIFICATIONS.md internal structure (heading hierarchy, how to cite the upstream schematic). Planner decides.
- CHAT-INTEL.md internal structure (chronological vs topical grouping). Planner decides; chronological-with-topical-headers is the natural shape.
- Phase 31 wave decomposition (single wave vs upstream-clone + history-mine wave + photograph wave + scaffold wave). Planner decides; the planner-agent should evaluate the natural cut points.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project planning
- `.planning/ROADMAP.md` §v1.7 — milestone goal, structural notes, Phase 31 success criteria, granularity rationale
- `.planning/REQUIREMENTS.md` — v1.7 requirements (HW-INV-01..03, SILK-01 for Phase 31; full milestone for downstream alignment)
- `.planning/STATE.md` — current milestone state, paused-milestone context (v1.6 paused at Phase 27 RCA re-open boundary)
- `.planning/PROJECT.md` — project overview, "Validated" section
- `.planning/codebase/STRUCTURE.md` — repo layout (meta-repo tracks only `.planning/`)

### Memory (auto-recalled, persistent across sessions)
- `[[user_shield_revisions]]` — operator owns Rev 2.2, Rev 2.0, modified Rev 0 (CONFIRMED Rev 0 not Rev 1 during this discussion)
- `[[project_v17_shield_investigation]]` — v1.7 milestone state (paused-v1.6-supersede, started 2026-05-22)
- `[[feedback_chip_out_before_sideload]]` — chip OUT of socket before firmware sideload (Phase 34 concern, not Phase 31)
- `[[feedback_verify_port_identity_each_task]]` — multi-board bench port-identity verification (Phase 34 concern)
- `[[feedback_branching]]` — milestone branches in all 3 repos; Phase 31 only touches meta-repo

### Upstream + chat intel (load-bearing for Phase 31 + downstream)
- `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer` — clone target. Stage at `.planning/v1.7/upstream-rurp/` (gitignored per D-11).
- `/workspaces/fs_an_notes.odt` — Anders↔henols 1:1 Discord chat 2024-07 → 2026-05-22. Phase 31 moves to `.planning/v1.7/notes/fs_an_notes.odt` (gitignored). Distilled into `CHAT-INTEL.md` per D-12. Key chronology: 2026-05-22 "branches for the previous versions on gh"; 2026-05-22 "the gerbers" as inter-rev source-of-truth; 2026-07-03 R41 changed for Rev 2.1, not for Rev 2.2 or Rev 2.3.
- `/workspaces/Discord_chat_..._2023..._2026..._.csv` — full Discord channel CSV (10,663 lines). Phase 31 moves to `.planning/v1.7/notes/discord-chat-full.csv` (gitignored). Distilled into `CHAT-INTEL.md`. Key 2024-10-07 Anders: "Say hello to R41 on A3"; henols: "JP1/JP3mod is now JP4"; 2025-04-28 Anders: "10k version resistor for Rev 2.2."

### Existing repo files (for Phase 35 hand-off + cross-link)
- `.planning/v1.6-EVIDENCE.md` — referenced by Phase 35 close pattern (v1.6 paused at Phase 27 RCA re-open; resume after v1.7 ships)
- `.planning/v1.5-BENCH-RESULTS.md` — file pattern that v1.7 mirrors for evidence accumulation
- `.planning/milestones/v1.4-ROADMAP.md`, `.planning/milestones/v1.5-ROADMAP.md` — archive patterns Phase 35 will mirror
- `firestarter/CLAUDE.md` (not modified in Phase 31; cited in ROADMAP)
- `firestarter_app/CLAUDE.md` (not modified in Phase 31; cited in ROADMAP)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None. Phase 31 is desk-side documentation/archaeology only — no firmware or host-CLI code change.

### Established Patterns
- **Evidence-accretion pattern.** v1.3 used `.planning/v1.3-BENCH-RESULTS.md`, v1.5 used `.planning/v1.5-BENCH-RESULTS.md`, v1.6 uses `.planning/v1.6-EVIDENCE.md`. v1.7 follows the same pattern with `.planning/v1.7-SHIELD-REVS.md` — single canonical file at `.planning/` root that all milestone phases append to (Phase 31 creates skeleton + fills its sections; Phases 32-34 fill their sections in-place).
- **Phase-archive pattern.** v1.4 + v1.5 closed by archiving `.planning/phases/<NN>-*/` under `.planning/milestones/<version>-phases/`. Phase 35 will mirror this for `.planning/phases/31-*/` through `35-*/`.
- **Gitignore convention.** Root `.gitignore` covers `.claude/`, `.pio/`, `__pycache__/`. The ROADMAP-specified `.planning/v1.7/upstream-rurp/` ignore is new precedent. D-11 generalizes it to `.planning/v1.7/` with `!*.md` un-ignore.
- **Documentation cross-linking.** sub-repo READMEs cross-link to `.planning/` artifacts only via the meta-repo's relative path. Phase 35 cross-links from `firestarter/README.md` + `firestarter_app/README.md` (not modified in Phase 31).

### Integration Points
- Phase 31 → Phase 32: inventory table columns (D-10) are the schema Phase 32's diff matrix reads. Lock the column order at Phase 31's commit so Phase 32 planner doesn't have to redesign.
- Phase 31 → Phase 33: silkscreen string verbatim (per SILK-01) is the canonical key Phase 33 maps to `PIN_<SUBSYSTEM>_<FUNCTION>` aliases. If Phase 31's strings differ across operator boards (e.g. "Rev 2.2" vs "RURP Rev 2.2"), Phase 33 must reconcile.
- Phase 31 → Phase 34: §3 "Existing Detect-HW Scheme" (D-07) is the substrate Phase 34 extends with firmware plumbing. Per-rev R41 values + A3 pin assignment captured here directly feed §9 ADC band table that Phase 34 will populate.
- Phase 31 → Phase 35: gitignore policy (D-11) + scaffold (D-09) determine what the milestone archive at `.planning/milestones/v1.7-phases/` includes; only the `.md` files survive into the committed archive.

</code_context>

<specifics>
## Specific Ideas

- **Silkscreen verbatim is canonical, including capitalization and spacing.** "RURP Rev 2.2" and "rurp_rev_2_2" are different strings; only the verbatim silkscreen text is the canonical ID. Filename-safe slug derivation for `photo_dir/` is implementation detail; the canonical column stays verbatim.
- **Rev 2.3 may already exist in upstream.** Anders (ODT 2026-07-03): "I think I changed it for the 2.1 but not the 2.2 or 2.3 (only silkscreen difference)." If Phase 31's mine recovers a Rev 2.3 schematic, it lands in the inventory even though operator doesn't own one. State = `upstream-only`. Phase 34's ADC band table seeds Rev 2.3 as the "next-rev / next-to-be-detected" entry.
- **Rev 2.1 must be found.** Anders explicitly stated R41 voltage-divider-into-A3 was introduced in Rev 2.1. If the mine doesn't surface a Rev 2.1 schematic on main + tags + branches + filter-D, that's a Phase 31 blocker to call out (it would mean Anders's statement is wrong, or there's a non-rev-named branch holding Rev 2.1 — fall back to all-refs walk).
- **Modified Rev 0 cross-reference target is the upstream Rev 0 schematic.** Phase 31's photo session needs the upstream Rev 0 schematic resolved before tracing rework. Sequence: (1) mine upstream → recover Rev 0 schematic; (2) THEN photograph + trace Modified Rev 0 rework with the schematic in hand. The planner should treat this as a sequential dependency, not parallel waves.
- **Henrik (operator) IS henols.** The Discord chat shows ~2 years of design conversation between Anders and the operator — useful provenance for any Phase 35 attribution prose.

</specifics>

<deferred>
## Deferred Ideas

### For Phase 34 discuss (when that phase opens)
- **Phase 34 scope rewrite.** Anders's R41-on-A3 voltage-divider-into-ADC scheme already exists upstream from Rev 2.1+. ROADMAP/REQUIREMENTS DETECT-HW phrasing ("schematic delta for next-rev shield") is partly stale. Phase 34's actual deliverable is firmware ADC read + voltage-band lookup + handshake report — not new hardware design. Phase 34 discuss should re-align REQUIREMENTS DETECT-HW-01/02 phrasing before planning. Phase 31 inventory's §3 (Existing Detect-HW Scheme) will be the substrate.

### For Phase 32 discuss
- **Diff Gerber files between revs.** Anders (ODT 2026-05-22): "Of course I do [document inter-rev changes]. But you're not going to like the answer. The gerbers!" Phase 32's inter-rev electrical/mechanical difference table may need to diff gerbers (not just schematics) for fidelity. Inventory column `gerber_path` from Phase 31 (D-10) makes this possible.

### For Phase 35 close
- **Reach out to Anders to confirm gaps.** Phase 31 stays self-sufficient (D-08), but any inventory rows / R41-value gaps left at Phase 31's close become `ANDERS-QUESTIONS-OPEN.md` for Phase 35 to address (light-touch: only if a gap actually blocks Phase 35's canonical-reference deliverable).
- **Memory revision.** Memory `[[user_shield_revisions]]` is correct as-is (operator confirmed it IS a Rev 0). But if Phase 31's photo session reveals the silkscreen differs from operator's recollection, memory should be updated then.

### Out of v1.7 entirely
- **Physical fabrication of next-rev shield** — operator-side; explicitly out of v1.7 per REQUIREMENTS "Out of Scope".
- **Runtime algorithm-vs-rev capability guards** — captured as a CAPS-02 follow-up todo for a later milestone.

### Reviewed Todos (cross-referenced, not folded)
- `avrdude-mcu-detection-fallback.md` — v1.5 carryover, not Phase 31 scope (firmware/host concern).
- `large-read-data-jitter-uno328pb.md` — v1.6 milestone scope, not Phase 31. (v1.6 resumes after v1.7 ships.)
- `w27c512-eeprom-misclassification.md` — separate backlog, not Phase 31 scope.

(None folded — discussion stayed within Phase 31's archaeology + inventory domain.)

</deferred>

---

*Phase: 31-Upstream-Shield-Archaeology*
*Context gathered: 2026-05-22*

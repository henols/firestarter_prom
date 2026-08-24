# Phase 159: Citation Remap + Milestone Close - Research

**Researched:** 2026-08-24
**Domain:** Git-anchored source-line citation migration over a multi-repository composite diff
**Confidence:** HIGH

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REMAP-01 | Run the remap exactly once over the composite pre-154 to post-158 diff, including the 723 citations shifted again by Phases 155-158. | Use the original pre-sweep firmware/app SHAs as per-record old-side anchors, add the post-manifest Phase 155-158 records through a supplemental manifest, rehearse outside the production tree, and make one `--apply` invocation against the production corpus. `[VERIFIED: REQUIREMENTS.md:77; ROADMAP.md:461-480; real-corpus dry run]` |
| REMAP-02 | Mechanically prove that each recorded source text equals the text at its remapped destination. | Keep the existing pre-write oracle, extend it to every actionable and hand-retargeted row, and make unmatched/not-at-recorded/dynamic-retarget outcomes blocking rather than a successful partial pass. `[VERIFIED: remap_citations.py decide/remap_document/main; current dry-run counts]` |
| REMAP-03 | Map both range endpoints and prove a real deleted-block range shrinks. | Preserve `map_range()`'s independent endpoint mapping and add a committed real-corpus assertion for `json_parser.c:128-131 -> 316-318`, an actual archived citation whose four-line span becomes three lines after Phase 157 replaces the indirect call with `store_field`. `[VERIFIED: test_remap_citations.py; git show 8695ee52:src/json_parser.c; current 2ccda8d source; milestones/v1.0-phases/02-firmware-json/02-VERIFICATION.md:65]` |
| REMAP-04 | Remove the Phase 154 staleness marker, with its existence blocking milestone close. | Treat deletion of `.planning/v1.33/CITATIONS-STALE.md` as the final task after all corpus, oracle, idempotency, archive-record, and closure-record gates pass; add an explicit negative existence check to the phase gate. `[VERIFIED: CITATIONS-STALE.md frontmatter and sections 4-5; REQUIREMENTS.md:80]` |
| REMAP-05 | Prove idempotency on the real corpus: run two is a no-op. | Snapshot the production result after the sole apply, invoke the tool again without `--apply`, require zero planned document changes and zero rewrites, and byte-compare the whole affected corpus before/after the second invocation. `[VERIFIED: existing fixed-point design and 21-test synthetic suite; REQUIREMENTS.md:81]` |

</phase_requirements>

## Summary

Phase 159 is not a simple invocation of the Phase 154 script. The committed remapper has the right core primitives—Git-backed old text, `SequenceMatcher(..., autojunk=False)`, independent range endpoints, a pre-write text oracle, positional binding, an all-documents-before-any-write transaction, atomic replacement, and fixed-point idempotency—but its current real-corpus contract is incomplete. The existing 21-test suite is green (`21 passed in 2.03s`), yet a dry run against the current tree required correcting a moved todo path and then reported `2238 rewritten`, `6908 fixed point`, `904 flagged retarget`, `3486 unreadable`, **156 unmatched**, and `508 documents would change`, while still exiting 0. `[VERIFIED: direct pytest and dry-run execution on 2026-08-24]`

Four gaps must be planned before production application. First, the staleness marker's instruction to pass app SHA `bc9d592` is wrong for the pre-sweep oracle: it produces immediate oracle violations, while `6bfa6453` produces a clean dry run. Second, one manifest document moved from `todos/pending/` to `todos/completed/`, and ROADMAP/STATE/another todo changed after manifest generation, producing the unmatched set. Third, the original manifest cannot contain records authored in Phases 155-158; those four phase directories now contain **642 citation records** (127 + 184 + 225 + 106), and at least one is demonstrably stale (`157-RESEARCH.md` still describes `parser_func` at `json_parser.c:128`, which now contains the `FIELD_MASK` comment). Fourth, the 815 hand-retargeted rows were selected against the post-154 tree and are currently left untouched by the tool; 98 of their chosen line numbers moved again, 93 map verbatim from `2ad5b322` to the final tree, and five no longer survive verbatim and require renewed human selection. `[VERIFIED: direct manifest/source audits; git histories; dry runs]`

**Primary recommendation:** extend the existing remapper into one fail-closed, multi-anchor transaction rather than writing a second regex rewriter; settle original rows, hand-retarget rows, and the Phase 155-158 supplemental rows in a disposable rehearsal, then run one production apply, prove the second run is byte-no-op, run the archived-record gate, and only then remove the close-blocking marker. `[VERIFIED: codebase constraints and measured failure modes]`

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Parse and bind citation syntax | Meta-repo tooling | Planning documents | `build_citation_manifest.py` owns the grammar and `remap_citations.py` imports it; binding must remain positional within document/path/variant groups. `[VERIFIED: both tool modules]` |
| Map old source lines to final source lines | Sub-repository Git history | Meta-repo tooling | The authoritative old and final blobs live in `firestarter` / `firestarter_app`; the meta tool supplies explicit per-root or per-record SHAs. `[VERIFIED: git_show(), ShaResolver, repo history]` |
| Preserve citation meaning | Manifest/oracle layer | Human retarget review | Verbatim survivors are machine-checked; deleted/reflowed targets require recorded human choices and a new-current-text oracle. `[VERIFIED: manifest retarget schema; sweep-outcome-record.md section 5]` |
| Apply all document edits atomically | Meta-repo tooling | Filesystem | The tool plans every document before writing and uses same-directory temp files plus `os.replace`. `[VERIFIED: remap_citations.py main/atomic_write]` |
| Close the staleness window | Milestone planning records | Phase gate | Marker deletion, requirement/roadmap closure, and a negative marker-existence check belong to the final wave, not to the mapping engine. `[VERIFIED: CITATIONS-STALE.md; ROADMAP Phase 159]` |

## Standard Stack

### Core

| Component | Version / Anchor | Purpose | Why Standard Here |
|-----------|------------------|---------|-------------------|
| Python stdlib | Python 3.12.13 | `argparse`, `difflib`, `json`, `pathlib`, `subprocess`, `tempfile` | Already implemented, dependency-free, and directly tested. No package installation is required. `[VERIFIED: environment; remap_citations.py imports]` |
| Git | 2.55.0 | Read historical blobs and identify exact old-side SHAs | The pre-sweep text no longer exists on disk, so Git objects are the source of truth. `[VERIFIED: environment; git_show()]` |
| pytest | 9.1.1 | Unit, regression, and real-case tests | Existing remapper suite has 21 passing tests. `[VERIFIED: environment; direct test run]` |
| `rg` | 15.2.0 | Corpus inventories and negative gates | Repository convention and available locally. `[VERIFIED: environment; CLAUDE.md search convention]` |

### Fixed Git Anchors

| Root / purpose | Anchor | Use |
|----------------|--------|-----|
| Firmware pre-sweep old side | `8695ee52c27a4bee4387c5c489afd5f3d7275e8a` | Original manifest's firmware records. `[VERIFIED: manifest header; git show]` |
| App pre-sweep old side | `6bfa6453d1bac232eb81ab35fa7f14b50b0b291a` | Original manifest's app records; **do not use `bc9d592` as the old side**. `[VERIFIED: dry-run comparison]` |
| Firmware post-154 hand-retarget base | `2ad5b322a37ba4a88afd09cc946f5c4114e51483` | Advance the 815 chosen `retarget_new_line` positions to final firmware. `[VERIFIED: Phase 154 closure records; git show]` |
| App post-154 hand-retarget base | `bc9d59293b9a08b16d6d7eb16eaf6c6f53e88e65` | Starting point named by the handoff. Current `38f0d83` differs by one line in `tests/test_dispatch_mirror.py`, although none of the three app-test retarget rows targets that file; verify per target instead of calling the commits tree-equivalent. `[VERIFIED: git diff; retarget-row census]` |
| Manifest planning-location base | `9a78bc6dc8b31087265f13c684ae850223806772` (original manifest commit) | Map recorded `planning_line` values and the pending-to-completed rename into the current meta tree without regenerating away the oracle. `[VERIFIED: meta git log]` |
| Final firmware tree at research time | `2ccda8d43c8161a34fb5f83b9ab12c37a443bf22` | Expected post-158 endpoint; executor must re-assert before applying. `[VERIFIED: git rev-parse; Phase 158 state]` |

**Installation:** none. This phase must not add external packages. `[VERIFIED: current implementation is stdlib-only]`

## Architecture Patterns

### System Architecture Diagram

```text
original manifest (pre-154 anchors/text) ─┐
                                         ├─> normalize planning-file locations
post-154 retarget choices ────────────────┤      (meta git diff / explicit rename)
                                         │
Phase 155-158 supplemental records ───────┘
          (per-record old SHA/text)
                         |
                         v
             build maps keyed by (root, target, old SHA)
                         |
                         v
       parse current planning docs + positional association
                         |
                 ┌───────┴────────┐
                 |                |
          verbatim survivor   deleted/reflowed
                 |                |
        mapped-text oracle   recorded human target
                 |          + current-text oracle
                 └───────┬────────┘
                         v
        any unmatched / ambiguity / oracle miss / null target?
                 | yes                    | no
                 v                        v
            abort, write 0        plan every document
                                           |
                                    disposable rehearsal
                                           |
                                one production `--apply`
                                           |
                             second run = byte-for-byte no-op
                                           |
                    archived-record gate + marker absence gate
                                           |
                         requirement/roadmap closeout records
```

### Recommended Project Structure

```text
.planning/v1.33/
├── sweep-citation-manifest.jsonl        # immutable original oracle input
├── 159-late-citation-manifest.jsonl     # Phase 155-158 supplemental records
├── 159-remap-record.md                  # commands, anchors, counts, range proof, idempotency
├── CITATIONS-STALE.md                   # deleted only in final wave
└── tools/
    ├── citation_paths.py                # shared resolver; keep single authority
    ├── build_citation_manifest.py       # extend/reuse, do not replace
    ├── remap_citations.py               # one transaction engine
    ├── test_remap_citations.py          # existing 21 + Wave 0 regression legs
    └── fixtures/                        # synthetic + real-case metadata fixture
```

### Pattern 1: Per-record source anchors

**What:** permit each supplemental record to identify the Git SHA at which its `target_line` and `source_text` were captured; cache maps by `(target_file_resolved, old_sha)` rather than only target path. `[VERIFIED recommendation from the Phase 155-158 provenance gap]`

**When to use:** original manifest rows use the two pre-154 SHAs; hand-retarget rows use post-154 anchors; Phase 155-158 records use the source commit appropriate to the artifact/plan that authored the citation. `[VERIFIED: repository commit sequencing]`

```python
# Codebase-derived pattern; extend LineMap cache, do not replace LineMap itself.
key = (record["target_file_resolved"], record["source_sha"])
line_map = maps[key]
```

### Pattern 2: Reconcile document location without regenerating source truth

**What:** use the meta Git diff from the original manifest commit to map `planning_file` renames and `planning_line` shifts, while preserving every original target line and source text. `[VERIFIED recommendation from 156 unmatched records and one moved todo]`

**When to use:** before positional citation association. An ambiguous document-line relocation is a blocking manual reconciliation, never a skipped row. `[VERIFIED: current skip behavior is unsafe for REMAP-02]`

### Pattern 3: Two oracle classes, one transaction

**What:** ordinary rows compare the recorded pre-change text at the composite destination; `retarget: true` rows compare the current destination to the hand-chosen target text after advancing that choice from its post-154 base. Both classes then use the same positional renderer and atomic write plan. `[VERIFIED recommendation from manifest schema and current tool behavior]`

**When to use:** all 815 existing hand-retarget rows, plus the additional endpoints deleted/replaced by Phases 155-158. The dry run currently reports 904 total flagged outcomes, so the delta must be explicitly settled and counted. `[VERIFIED: current dry-run output]`

### Pattern 4: Rehearsal is not production application

**What:** exercise `--apply` against a disposable copy/worktree of `.planning`, pointed at the real read-only source repos, then discard it. Record that only the final production-tree `--apply` counts as REMAP-01's exactly-once application. `[VERIFIED recommendation from failure blast radius]`

**When to use:** after all Wave 0 tests and a zero-exception dry run, before the production invocation. `[VERIFIED: atomic planner still affects hundreds of documents]`

### Anti-Patterns to Avoid

- **Do not regenerate the original manifest against the final tree.** That replaces the old-text oracle with a tautological snapshot and cannot prove the migration. `[VERIFIED: manifest purpose/header]`
- **Do not use `bc9d592` as the original app old side.** Direct execution produced oracle violations; `6bfa6453` is the actual pre-sweep anchor. `[VERIFIED: comparative dry runs]`
- **Do not accept exit 0 with unmatched or not-at-recorded rows.** The current tool calls 156 rows unmatched and exits 0, which is incompatible with REMAP-02. `[VERIFIED: direct dry run]`
- **Do not leave `retarget: true` citations numerically unchanged and then remove the marker.** “Skip by name” means they are excluded from the verbatim-old-text oracle; it cannot mean stale citations survive milestone close. `[VERIFIED: operator ruling, marker purpose, and current tool semantics]`
- **Do not run a second production `--apply` to demonstrate idempotency.** Apply once; prove run two through dry-run counts plus a byte snapshot. `[VERIFIED: REMAP-01/05 combined constraint]`
- **Do not globally rewrite ROADMAP.md, REQUIREMENTS.md, PROJECT.md, or STATE.md.** Use scoped edits and inspect diffs; project history records helper verbs and whole-file normalization as destructive to hand-authored records. `[VERIFIED: ROADMAP activation notes; prior closure plans]`

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Citation grammar | A new regex or sed pass | `build_citation_manifest._CITATION_RE` and `_spans_from_match` | Five variants, wrappers, lists, and ranges already share one tested grammar. `[VERIFIED: tool sources]` |
| Target resolution | A basename finder | `citation_paths.CandidateIndex` and fixture rules | Basename collisions and planted fixtures can produce false-green oracle results. `[VERIFIED: citation_paths and T-154-13 tests]` |
| Line mapping | Constant offsets or hunk-only translation | Existing `LineMap` / `map_range` | Independent endpoint maps are required for shrink, and `autojunk=False` is measured load-bearing. `[VERIFIED: tool docs/tests]` |
| File writes | In-place per-record edits | Existing whole-run planning + `atomic_write` | An oracle failure anywhere must leave every document untouched. `[VERIFIED: remapper transaction design]` |
| Late-record proof | A final-tree rescan labeled as an oracle | Supplemental records with historical source SHA/text | A final scan only proves that a line currently contains itself. `[VERIFIED: Phase 155-158 manifest absence]` |

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | 13,692 original JSONL rows; 1,228 original planning documents; 815 hand-retarget choices; 642 citation records in Phase 155-158 artifacts; 1,302 original rows under archived `milestones/`. `[VERIFIED: manifest, phase scan, marker]` | Preserve original manifest, add supplemental records, migrate planning-file locations, rewrite citations, and record exact before/after counts. This is a data migration. |
| Live service config | None. The migration touches local Git repositories and files only; no external service configuration is involved. `[VERIFIED: repo/code inspection]` | None. |
| OS-registered state | None. No scheduler, service manager, or OS registration stores these citation line numbers. `[VERIFIED: scope and repo inspection]` | None. |
| Secrets / env vars | None required by the remapper. It takes explicit paths and SHAs on argv. `[VERIFIED: argparse interface]` | Keep roots/SHAs explicit; do not add secret or environment-derived defaults. |
| Build artifacts / installed packages | Temporary `.pio` outputs and Python caches are irrelevant; the affected persistent artifacts are Git-tracked planning documents. `[VERIFIED: implementation scope]` | Rehearsal in a disposable tree; do not treat cache cleanup as migration evidence. |

**Canonical answer:** after source files are final, stale state remains in Git-tracked planning documents and in the post-154 hand-retarget coordinates; the original manifest is the migration ledger, not state to regenerate away. `[VERIFIED: direct corpus audit]`

## Common Pitfalls

### Pitfall 1: Trusting the marker's app-SHA handoff literally

**What goes wrong:** `bc9d592` as the app old side maps post-sweep app text to equivalent current app text while records still carry pre-sweep target lines/text, producing oracle failures. `[VERIFIED: direct dry run]`

**How to avoid:** use `6bfa6453` for original rows; reserve the post-154 app commit only for advancing hand-retarget coordinates. Add a regression test that the wrong anchor fails and the correct one passes. `[VERIFIED recommendation]`

### Pitfall 2: A green partial pass

**What goes wrong:** unmatched groups, moved documents, and dynamic retargets are notes/counters rather than violations. The current run exits 0 with 156 unmatched records. `[VERIFIED: remap_document/main and dry run]`

**How to avoid:** production readiness requires zero actionable unmatched, zero not-at-recorded, zero unreviewed retarget, zero oracle violations, and zero missing documents. Rows already unreadable before Phase 154 remain an explicitly named exclusion class. `[VERIFIED recommendation bounded by manifest text_status]`

### Pitfall 3: Treating the 815 choices as final-tree coordinates

**What goes wrong:** those choices were made after Phase 154, before Phases 155-158. Ninety-eight no longer point to their chosen text; five chosen texts no longer survive verbatim. `[VERIFIED: direct 815-row audit]`

**How to avoid:** map them from `2ad5b322` to final where possible, manually settle the five non-survivors, record the final count and reasons, and test their fixed-point behavior. `[VERIFIED recommendation]`

### Pitfall 4: Omitting records authored after the manifest

**What goes wrong:** 155-158 research/plans/summaries are absent by chronology. A current rescan hides stale semantics; e.g. `157-RESEARCH.md`'s `parser_func` citation still says line 128 although line 128 now starts the `FIELD_MASK` definition. `[VERIFIED: phase chronology and live files]`

**How to avoid:** create a supplemental historical manifest with a source SHA per record and feed it to the same transaction. Count all 642 parsed records, then classify out-of-candidate or intentionally non-source references explicitly rather than silently dropping them. `[VERIFIED recommendation]`

### Pitfall 5: Proving idempotency with another write

**What goes wrong:** a second `--apply` conflicts with REMAP-01's exactly-once wording even if it writes zero bytes. `[VERIFIED: requirement wording]`

**How to avoid:** after the sole apply, hash/copy the affected-document corpus, run a dry pass, require `0 rewritten` and `0 documents would change`, and byte-compare the corpus. `[VERIFIED recommendation]`

### Pitfall 6: Archive edits break unrelated record gates

**What goes wrong:** citation rewrites under `.planning/milestones/` may shift physical lines used by `recordscan:supersedes lines=N` exemptions. `[VERIFIED: sweep-outcome-record.md; Phase 146 research]`

**How to avoid:** run `check_record_corrections.py` before and after the remap and require the same green verdict/counts; current baseline is `PASS` with `superseded: 12`. Record collision or absence with cause, as SWEEP-13 requires. `[VERIFIED: direct baseline run]`

### Pitfall 7: Removing the marker too early

**What goes wrong:** the only structural close block disappears while exceptions still exist. `[VERIFIED: REMAP-04 rationale]`

**How to avoid:** marker removal is the final implementation task, gated on the real-corpus oracle, no-op second run, real shrink case, archive gate, and scoped requirements/roadmap closure. `[VERIFIED recommendation]`

## Code Examples

### Correct original-manifest dry run

```bash
python3 .planning/v1.33/tools/remap_citations.py /workspaces \
  --manifest .planning/v1.33/sweep-citation-manifest.jsonl \
  --pre-sweep-sha firestarter=8695ee52c27a4bee4387c5c489afd5f3d7275e8a \
  --pre-sweep-sha firestarter_app=6bfa6453d1bac232eb81ab35fa7f14b50b0b291a
```

`[VERIFIED: direct execution; command still needs Wave 0 location/late-record/retarget hardening before production]`

### Existing real range-shrink case

```python
# Old json_parser.c lines 128-131 contain four lines:
#   if (...) {
#       parser_func = ...
#       parser_func(...)
#       token_idx += 2
# Final lines 316-318 contain three:
#   if (...) {
#       store_field(...)
#       token_idx += 2
assert map_range(line_map, 128, 131, len(old_lines))[:2] == (316, 318)
assert (131 - 128 + 1) == 4
assert (318 - 316 + 1) == 3
```

`[VERIFIED: Git blobs and current source; add as a committed test rather than trusting this prose]`

### Idempotency gate after the sole apply

```bash
# Snapshot hashes of every changed planning document after the one production apply.
# Run WITHOUT --apply.
python3 .planning/v1.33/tools/remap_citations.py ... --quiet-notes
# Require: 0 rewritten; 0 documents would change; no actionable exception counts.
# Re-hash and require byte identity with the snapshot.
```

`[VERIFIED recommendation derived from REMAP-01 + REMAP-05]`

## State of the Art

| Old / Current Incomplete Approach | Required Phase 159 Approach | Impact |
|-----------------------------------|-----------------------------|--------|
| One old SHA per root | Old SHA per record/map key where needed | Supports post-manifest artifacts and post-154 retarget coordinates in one transaction. `[VERIFIED recommendation]` |
| `retarget: true` rows skipped and left unchanged | Skip only the pre-sweep verbatim oracle; apply reviewed new targets under a current-text oracle | Actually closes stale citations instead of merely counting them. `[VERIFIED recommendation]` |
| Unmatched rows counted, exit 0 | Actionable unmatched/ambiguous outcomes block with zero writes | Makes REMAP-02 comprehensive. `[VERIFIED recommendation]` |
| Synthetic shrink/idempotency only | Synthetic suite plus real milestone range and real corpus no-op | Meets REMAP-03/05 exactly. `[VERIFIED: requirements]` |
| Original manifest only | Immutable original plus supplemental late-record manifest | Covers Phase 155-158's own records. `[VERIFIED: chronology and 642-record census]` |

## Project Constraints (from CLAUDE.md)

- The workspace is a meta/planning repo; production code lives in `firestarter/` and `firestarter_app/`, which are separate Git repositories. `[VERIFIED: /workspaces/CLAUDE.md]`
- Serial protocol changes must stay synchronized across host and firmware, but Phase 159 should make no production-code or protocol edits. `[VERIFIED: /workspaces/CLAUDE.md; phase scope]`
- Duplicated constants/flags must change together, but no such change belongs in this phase. `[VERIFIED: /workspaces/CLAUDE.md; phase scope]`
- Use project-local commands from the owning sub-repository. For this phase, only the meta tooling tests and record gates are required unless an implementation change unexpectedly touches a sub-repo. `[VERIFIED: /workspaces/CLAUDE.md and no-source-edit scope]`
- Use scoped edits for hand-authored planning records; do not regenerate ROADMAP.md or REQUIREMENTS.md with GSD helper verbs. `[VERIFIED: ROADMAP activation notes and prior close plans]`

No project-local skill applies: the available `devtest-triage` and `devtest-rootcause` skills concern chip/hardware failures, and `find-skills` / skill creation are unrelated to this repository-local migration. `[VERIFIED: project skill indexes]`

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | None. Recommendations are based on committed artifacts, Git objects, source inspection, and direct executions. | — | — |

## Open Questions

1. **What exact source SHA should each of the 642 Phase 155-158 records use?**
   - What we know: the four phase directories contain 127, 184, 225, and 106 parsed records, and plans/summaries were authored at different points in sequential source histories. `[VERIFIED: direct scan and git logs]`
   - What's unclear: a safe record-to-source-commit mapping has not yet been materialized.
   - Recommendation: Wave 0 must derive and commit this mapping from each plan's recorded source commit/summary, then oracle-check the cited text at that anchor. Any artifact without an unambiguous anchor becomes a manual checkpoint, not a final-tree rescan.

2. **How many of the current 904 flagged outcomes are the original 815 versus newly non-surviving endpoints after positional grouping?**
   - What we know: the aggregate difference is 89 outcomes, while note output contains 103 “did not survive” messages because ranges/groups and outcome accounting differ. `[VERIFIED: dry-run output and note census]`
   - What's unclear: the final unique record set has not been normalized.
   - Recommendation: add a stable record ID to the runtime report and emit a machine-readable exception ledger; settle it to zero unreviewed rows before apply.

3. **Does the milestone-close orchestrator itself belong in Phase 159 execution?**
   - What we know: prior last phases leave the project “ready for `/gsd-complete-milestone`”; the close command performs separate archival/release bookkeeping. `[VERIFIED: prior STATE/phase records]`
   - Recommendation: Phase 159 should close REMAP requirements, delete the marker, and leave v1.33 ready for `/gsd-complete-milestone`; do not invoke the milestone-close workflow inside an execute plan unless the orchestrator explicitly authorizes it.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 + command-level Git/corpus gates `[VERIFIED: environment]` |
| Config file | No dedicated meta pytest config; invoke the test file explicitly. `[VERIFIED: repo inspection]` |
| Quick run command | `python3 -m pytest -q .planning/v1.33/tools/test_remap_citations.py` |
| Full phase command | Quick suite + hardened real-corpus dry run + post-apply no-op/hash comparison + `check_record_corrections.py` + marker/requirements/roadmap gates |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REMAP-01 | Correct composite anchors, complete corpus, one production apply | integration / ledger | hardened dry run must report exact classified totals; production record must contain one `--apply` command | Partial; ❌ Wave 0 additions |
| REMAP-02 | Every actionable/retargeted row lands on its oracle text; no silent exceptions | unit + corpus | pytest exception tests; hardened dry run/apply requires zero unmatched/not-at-recorded/unreviewed-retarget/oracle violations | Partial; ❌ Wave 0 additions |
| REMAP-03 | Both endpoints map; real Phase 157 range shrinks 128-131 -> 316-318 | unit + real fixture | `pytest ... -k 'range or real_json_parser'` | Synthetic ✅; real ❌ Wave 0 |
| REMAP-04 | Marker remains until every gate passes, then is absent | close gate | `test ! -e .planning/v1.33/CITATIONS-STALE.md` after all earlier gates | ❌ Wave 0 closure gate |
| REMAP-05 | Real corpus second run is byte no-op | integration | post-apply dry run reports 0/0 and corpus hashes compare equal | ❌ Wave 0 harness/ledger |

### Required New Test Legs

1. Wrong app old SHA (`bc9d592`) is RED; correct pre-sweep SHA (`6bfa6453`) is GREEN. `[VERIFIED need from direct run]`
2. A moved citing document is resolved through meta Git rename/history without changing target/source oracle fields. `[VERIFIED need from completed todo move]`
3. A shifted `planning_line` is rebound safely; ambiguity exits 1 and writes nothing. `[VERIFIED need from 156 unmatched rows]`
4. Any actionable unmatched/not-at-recorded/dynamic-retarget result exits non-zero. `[VERIFIED need from current green partial pass]`
5. Existing `retarget: true` row rewrites to reviewed target and is fixed-point on run two. `[VERIFIED need from 815 skipped rows]`
6. A post-154 retarget target that moved again maps from `2ad5b322`; a second deletion requires explicit renewed review. `[VERIFIED need from 98/5 audit]`
7. Two records for one target with different old SHAs use different cached `LineMap`s correctly. `[VERIFIED need from late manifest design]`
8. Real `json_parser.c:128-131 -> 316-318` range shrinks and both destination texts match. `[VERIFIED real case]`
9. Whole-run failure after hundreds of planned edits writes zero documents. `[VERIFIED existing property; extend to new classes]`

### Sampling Rate

- **Per tool-change commit:** `python3 -m pytest -q .planning/v1.33/tools/test_remap_citations.py`
- **Per manifest/reconciliation commit:** full hardened dry run; zero actionable exceptions required.
- **Before production apply:** unit suite + disposable apply rehearsal + second-run no-op + archive gate in rehearsal.
- **Phase gate:** one production apply recorded, then real-corpus dry no-op/hash equality, real range proof, archive gate unchanged, marker absent, REMAP rows complete.

### Wave 0 Gaps

- [ ] Extend `remap_citations.py` for per-record anchors, planning-location reconciliation, reviewed-retarget application, stable IDs, and fail-closed exception totals.
- [ ] Extend `test_remap_citations.py` with the nine legs above.
- [ ] Create `.planning/v1.33/159-late-citation-manifest.jsonl` with historical anchors for Phase 155-158 records.
- [ ] Create a machine-readable/current exception ledger for original 815 + newly deleted/replaced endpoints and settle it before apply.
- [ ] Create a disposable-corpus rehearsal/hash harness using existing parser/writer code, not a second rewriter.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | No user/service authentication surface. `[VERIFIED: local CLI scope]` |
| V3 Session Management | No | No sessions. `[VERIFIED: local CLI scope]` |
| V4 Access Control | No external authorization boundary | Operate only within explicit repo root and Git-tracked planning scope. `[VERIFIED: path guards]` |
| V5 Input Validation | Yes | Existing `safe_relative`, `inside`, fixture collision checks, required manifest/root args, and strict schema validation; extend validation to per-record SHAs/IDs. `[VERIFIED: remap_citations.py]` |
| V6 Cryptography | No | Git SHAs identify versions but are not used as a cryptographic security control. `[VERIFIED: design scope]` |
| V12 File and Resource Validation | Yes | Refuse traversal, absolute paths, out-of-root resolutions, symlinked citing docs, missing blobs, and non-atomic writes. `[VERIFIED: remap_citations.py path safety]` |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal / symlink escape in manifest | Tampering | Explicit root, relative-path validation, containment checks, symlink refusal. `[VERIFIED: implementation]` |
| Wrong Git anchor creates plausible but false mappings | Tampering | Explicit per-record anchors plus destination-text oracle; wrong-anchor regression. `[VERIFIED recommendation]` |
| Partial green with skipped rows | Tampering / Repudiation | Stable record IDs, zero-exception gate, machine-readable ledger, all-or-nothing writes. `[VERIFIED recommendation]` |
| Rewriting a planted fixture instead of production source | Tampering | Shared `citation_paths` fixture rules and collision gate. `[VERIFIED: implementation/tests]` |
| Second run silently drifts chained line numbers | Tampering | Fixed-point-first predicate, recorded old identity, real-corpus byte-no-op proof. `[VERIFIED: implementation/tests]` |

## Recommended Plan Shape

### Wave 1 — Harden and inventory

1. Add the Wave 0 test legs and harden the transaction engine: per-record anchors, document-location reconciliation, stable record IDs, reviewed-retarget rendering, and blocking exception semantics. `[VERIFIED recommendation]`
2. Build the Phase 155-158 supplemental historical manifest and the normalized retarget ledger. Keep the original 13,692-row manifest immutable except for a separately reviewed location-overlay if the implementation needs one. `[VERIFIED recommendation]`

### Wave 2 — Settle every non-mechanical row

1. Advance the 815 hand-retarget choices from post-154 to final; mechanically accept the 93 exact mapped movements, explicitly confirm the 717 unchanged coordinates, and manually reselect the five non-survivors. `[VERIFIED: 815-row audit]`
2. Normalize and review every newly non-surviving Phase 155-158 endpoint; produce zero unreviewed retargets and zero ambiguous supplemental anchors. `[VERIFIED recommendation]`

### Wave 3 — Rehearse and prove

1. Run the full unit suite and hardened dry run with zero actionable exceptions. `[VERIFIED recommendation]`
2. Apply to a disposable corpus, run the second-pass no-op/hash proof, prove the real `json_parser.c` shrink case, and run the archived-record correction gate before/after. `[VERIFIED recommendation]`

### Wave 4 — One production apply

1. Re-assert repo SHAs/clean tracked state and capture pre-apply hashes/counts. `[VERIFIED recommendation]`
2. Invoke production `--apply` exactly once. Commit the citation migration and its evidence record atomically in the meta repo; do not touch either source sub-repo or gitlink. `[VERIFIED: phase scope]`
3. Run the tool again dry, require zero planned changes, and byte-compare the migrated corpus. Run the archive gate and record whether the known collision occurred. `[VERIFIED recommendation]`

### Wave 5 — Close the window

1. Remove `CITATIONS-STALE.md` only after Wave 4 is green. `[VERIFIED: REMAP-04]`
2. Scope-edit REQUIREMENTS.md and ROADMAP.md to close REMAP-01..05 and replace Phase 159's TBD plan list with the actual plans; write the final remap record/summary. `[VERIFIED: project closure convention]`
3. Gate marker absence and leave the milestone ready for `/gsd-complete-milestone`; do not perform external release/push/close actions in this phase. `[VERIFIED: prior milestone convention and authorization scope]`

## Sources

### Primary (HIGH confidence)

- `.planning/REQUIREMENTS.md` REMAP-01..05 and SWEEP-09..13.
- `.planning/ROADMAP.md` v1.33 sequencing and Phase 159.
- `.planning/STATE.md` Phase 154-158 completion/hand-off state.
- `.planning/v1.33/tools/remap_citations.py`, `build_citation_manifest.py`, `citation_paths.py`, and `test_remap_citations.py`.
- `.planning/v1.33/sweep-citation-manifest.jsonl`, `sweep-outcome-record.md`, and `CITATIONS-STALE.md`.
- Phase 154-158 plans, summaries, research, validation, and verification artifacts.
- Direct Git inspection and executions on 2026-08-24: pytest, two app-anchor dry runs, full current dry run, manifest/doc census, retarget-coordinate audit, and record-correction gate.

### Secondary (MEDIUM confidence)

- None required; this phase is codebase-local.

### Tertiary (LOW confidence)

- The mandated websearch seam returned only generic, non-project-specific results; none was used to support a recommendation. `[VERIFIED: research-plan/store results]`

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — installed versions and imports were directly inspected.
- Architecture: HIGH — based on committed code, manifests, Git objects, and executed dry runs.
- Pitfalls: HIGH — each major pitfall was reproduced or counted on the current corpus.
- Late-record anchor assignment: MEDIUM until Wave 0 materializes the per-record SHA map; the need and record count are HIGH-confidence.

**Graph note:** `.planning/graphs/graph.json` is stale by 1,293 hours and 1,824 commits and returned no nodes for the three phase queries, so it was not used for architectural conclusions. `[VERIFIED: graphify status/query]`

**Research date:** 2026-08-24
**Valid until:** 2026-09-23, provided the three repository HEADs do not move; re-run every census and dry-run count if they do.

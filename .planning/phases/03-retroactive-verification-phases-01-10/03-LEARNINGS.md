---
phase: 03
phase_name: "Retroactive Verification (Phases 01-10)"
project: "Firestarter — Protocol-Aware Programming Architecture"
generated: "2026-05-12"
counts:
  decisions: 10
  lessons: 6
  patterns: 7
  surprises: 7
missing_artifacts: []
---

# Phase 03 Learnings: Retroactive Verification (Phases 01-10)

## Decisions

### Score against current source tree, not v1.0-as-shipped state
Every PARTIAL REQ from `v1.0-MILESTONE-AUDIT.md` is scored against the **current** source tree at write time. Frontmatter `status: passed` reflects "SATISFIED today," not historical v1.0 state. The v1.0-as-shipped narrative lives only in `Cross-Milestone Closure` subsections (used when v1.1 closed a v1.0 PARTIAL), never in the score.

**Rationale:** A retroactive audit that re-scores against the original shipped state would duplicate `v1.0-MILESTONE-AUDIT.md` and ignore v1.1 closure work. Scoring against current code makes the artifacts useful for the next milestone audit. (CONTEXT.md D-01, codified into all 10 files; reaffirmed in both SUMMARY.md decision logs.)
**Source:** 03-CONTEXT.md, 03-01-SUMMARY.md, 03-02-SUMMARY.md

---

### Atomic per-VERIFICATION.md commit (one file = one commit)
Each of the 10 VERIFICATION.md files lands as its own commit (`docs(03-NN): retroactive verification — Phase XX (REQ-IDs)`), plus one commit per plan SUMMARY. Twelve total docs commits across the two plans.

**Rationale:** Each VERIFICATION.md is independently revertable; bisect resolves to a single phase artifact. Two-plan split keeps wave parallelism while preserving atomic granularity. (CONTEXT.md D-13.)
**Source:** 03-CONTEXT.md, 03-01-SUMMARY.md, 03-02-SUMMARY.md

---

### Two-plan split: clean batch + closure/hazard batch
Plan 03-01 = phases {01, 02, 04, 08, 09} (clean batch — 8 PARTIAL REQs, only WARNING-4 follow_up). Plan 03-02 = phases {03, 05, 06, 07, 10} (closure/hazard batch — SC#3 SAF-04 closure in 05; SC#4 static_high_mask lock in 10; SAF-05 closure in 07; WARNING-5 × 3 + INFO-3 follow_ups).

**Rationale:** Two evaluated alternatives (split by follow_ups presence; split by closure presence) both broke either SC#3/SC#4 grouping or plan-size balance. The chosen split keeps the two highest-stakes ROADMAP locks (SC#3 + SC#4) inside the same plan/wave so they get authored in the same focus session. (03-RESEARCH.md §"Two-Plan Split Sanity Check".)
**Source:** 03-RESEARCH.md

---

### Cross-Milestone Closure subsection only when v1.1 closed a v1.0 PARTIAL
Dedicated subsection used three times: `01-VERIFICATION.md` for REQ-DB-03 (WIRE-01), `05-VERIFICATION.md` for REQ-SAF-01 Intel portion (SAF-04 — **SC#3**), `07-VERIFICATION.md` for REQ-SAF-02 (SAF-05).

**Rationale:** A dedicated section is reserved for cross-milestone narrative weight. When the closing phase is itself v1.0 (e.g. Phase 12's algo-first dispatch closing REQ-FW-04 reachability), the cite goes inline in the Requirements Coverage row instead — no subsection. (CONTEXT.md "Claude's Discretion"; 03-RESEARCH.md §"Cross-Milestone Closure Narrative Sources".)
**Source:** 03-CONTEXT.md, 03-RESEARCH.md, 03-01-SUMMARY.md

---

### REQ-SAF-01 and REQ-SAF-03 legitimately appear in two files each
REQ-SAF-01 is in `requirements_verified` of both `03-VERIFICATION.md` (UV-EPROM portion) and `05-VERIFICATION.md` (Intel portion). REQ-SAF-03 is in both `04-VERIFICATION.md` (flash3-handler-local) and `08-VERIFICATION.md` (cross-handler).

**Rationale:** Audit attribution genuinely spans handlers (`REQ-SAF-01: 03 (and 05)`; `REQ-SAF-03: 04 (and 06)` and cross-handler). Both files reference the same REQ-ID with non-overlapping evidence — no conflict; different scopes. (03-RESEARCH.md Open Questions #1 and #2; 03-01-SUMMARY.md decision log.)
**Source:** 03-RESEARCH.md, 03-01-SUMMARY.md, 03-02-SUMMARY.md

---

### SAF-05 implementation uses A9-12V identification, not JEDEC AA/55/90
Plan 01-02 (v1.1 Phase 01) implemented `eeprom28c_check_chip_id` with the A9-12V identification sequence, NOT the AMD/SST JEDEC AA/55/90 sequence proposed in CONTEXT.md D-05. `07-VERIFICATION.md` records this override inline.

**Rationale:** RESEARCH.md datasheet evidence — JEDEC AA/55/90 would corrupt address 0x5555 on SDP-disabled AT28C parts. The override is load-bearing; D-05 was overridden during execution, and the override is the actual contract. (STATE.md "Decisions (Phase 1)"; 07-VERIFICATION.md SAF-05 Cross-Milestone Closure.)
**Source:** .planning/STATE.md, 07-VERIFICATION.md (via 03-02-SUMMARY.md)

---

### SC#4 lock uses a named subsection (`### SC#4 Explicit Lock`)
`10-VERIFICATION.md` carries a verbatim-titled subsection `### SC#4 Explicit Lock — static_high_mask end-to-end + pins < 32 VPE_TO_VPP guard`.

**Rationale:** ROADMAP gate must be machine-checkable. A grep on the verbatim string `SC#4 Explicit Lock` (plus the literal tokens `static_high_mask` and `pins < 32`) yields an unambiguous PASS/FAIL signal — no fuzzy text matching. Combined with 5 named-hop citations + dead-check-absent grep, the contract is discharged with zero ambiguity. (03-02-SUMMARY.md key-decisions §4.)
**Source:** 03-02-SUMMARY.md, 10-VERIFICATION.md

---

### WARNING-5 follow_up tailored per phase (defect-vs-classification distinction)
WARNING-5 appears in `follow_ups` on three files (03, 06, 07), each with a `note:` tailored to the phase's specific defect-vs-upstream-data distinction.

**Rationale:** REQ-FW-03 SATISFIED ≠ AT28C256 hazard closed. The 0x0D handler logic is correct (and was correct in v1.0); the hazard is **upstream-DB classification** (minipro tags AT28C256/64 as `algorithm=0x07` with `electrical.type='Flash/EEPROM'`, routing it via `configure_eprom` instead of the 0x0D handler). Different phases see different facets, so each `note:` calls out the phase-specific framing. (03-RESEARCH.md Pitfall #10.)
**Source:** 03-RESEARCH.md, 03-02-SUMMARY.md

---

### Don't update v1.0-MILESTONE-AUDIT.md; produce closure artifacts instead
Phase 3 writes 10 VERIFICATION.md files. It does NOT touch `v1.0-MILESTONE-AUDIT.md` — that is a historical snapshot. Phase 5 (DOC-01) MAY add a v1.1-resolution table to `MILESTONES.md` later.

**Rationale:** Audit snapshots have `re_audit_of:` timestamps. Mutating a snapshot destroys the audit chain. The closure artifacts are what the audit's `gaps` block points at. (03-RESEARCH.md Pitfall #1.)
**Source:** 03-RESEARCH.md

---

### Verifier hand-authored (no agent dispatch)
The phase-level `VERIFICATION.md` (13/13 PASS report) was hand-authored, not produced by a `gsd-verifier` agent dispatch, per CONTEXT.md D-12.

**Rationale:** The 10 per-phase VERIFICATION.md files are themselves verifier output. Spawning a verifier to verify verifier output adds a synthesis layer without adding signal; direct grep + Read against the live tree is the actual verification. (VERIFICATION.md footer.)
**Source:** VERIFICATION.md
_Note: This phase's orchestration nevertheless used a gsd-verifier agent dispatch to produce VERIFICATION.md; the artifact itself records the alternative D-12 framing._

---

## Lessons

### Line numbers shift across v1.1 closure phases — grep at write time, never trust stale numbers
Multiple `file:line` citations from CONTEXT.md and RESEARCH.md drifted between research time and write time as v1.1 closures landed: `flash_intel.cpp` gained the `flash_intel_check_vpp` helper (lines 25-50), pushing `flash_intel_check_chip_id` from earlier position to `:152`. `eeprom_28c.cpp` gained the `eeprom28c_check_chip_id` helper at `:55-77`, pushing `flash_execute_command(EEPROM_SDP_DISABLE)` to `:91`.

**Context:** Pitfall #7 in 03-RESEARCH.md was specifically encoded for this. Every executor task included a `read_first` list of grep targets, and acceptance criteria required each cited `file:line` to resolve via `grep -n` at write time. The "10 similar files" production rhythm made this easy to slip — having it as an explicit pitfall + acceptance criterion caught the drift.
**Source:** 03-RESEARCH.md Pitfall #7, 03-01-SUMMARY.md patterns log

---

### "REQ SATISFIED" is not the same as "hazard closed"
REQ-FW-03 scope is the 0x0D handler logic — that handler is correct. The AT28C256 hazard is an upstream-DB classification issue: 30 chips never reach the 0x0D handler at all. `06-VERIFICATION.md` therefore scores REQ-FW-03 `SATISFIED` AND carries WARNING-5 as a `follow_up` — both true simultaneously.

**Context:** Without this distinction, an auditor reading "REQ-FW-03 SATISFIED" might conclude the AT28C256 12V-on-A14 hazard is closed. Pitfall #10 in 03-RESEARCH.md forced each WARNING-5 `note:` to spell out the defect-vs-classification framing for the phase. Same surface lesson surfaces in REQ-FW-04 (Phase 12 reachability for 0x06 — handler was correct, dispatch was missing).
**Source:** 03-RESEARCH.md Pitfall #10

---

### Body length is a guidance band, not a hard reject
`02-VERIFICATION.md` landed at 88 lines, below the 100-160 guidance band. The plan's acceptance criteria explicitly accepted this: "do not impose minimum line count" applies to single-file behavioral guarantees where there is simply less to say.

**Context:** REQ-SER-02 is two-site behavioral skip in `json_parser.c` — no Cross-Milestone Closure, no follow_up, no Data-Flow Trace. The 88 lines are the natural length. A 160-line version would have been padding. CONTEXT.md D-08 made this explicit, and the 03-01 plan honored it. (03-01-SUMMARY.md key-decisions §4.)
**Source:** 03-01-SUMMARY.md

---

### Existing test runs should be cited, not re-executed
`pio test`, `pio run`, and `check_dispatch.py` were NOT re-run inside Phase 3. Existing artifacts were cited:
- Native suite 25/25 → `01-VERIFICATION.md` (v1.1 Phase 1) Behavioral Spot-Check, 2026-05-12T08:00:00Z
- `check_dispatch.py` PASS → `02-VERIFICATION.md` (v1.1 Phase 2) Behavioral Spot-Check, 2026-05-12T09:30:00Z
- `pio run` uno + leonardo → `12-VERIFICATION.md` (v1.0 Phase 12), 2026-05-11T10:00:00Z

**Context:** Pitfall #3 in 03-RESEARCH.md. Re-running tests per file would have produced 10 redundant evidence captures of the same green CI state. Citation is the right primitive — and it forces the cited artifacts (the live VERIFICATION.md files for v1.1 Phases 1 + 2 and v1.0 Phase 12) to remain the source of truth.
**Source:** 03-RESEARCH.md Pitfall #3

---

### Discuss-phase guesses are validatable starting points, not contracts to discard
CONTEXT.md `<specifics>` table proposing per-file REQ assignments + Cross-Milestone Closure + follow_ups columns was authored as a discuss-phase guess (per session-memory directive about minimal solutions). RESEARCH.md validated every cell against `v1.0-MILESTONE-AUDIT.md` `gaps.requirements` — no corrections needed. The CONTEXT.md verbatim YAML blocks for WARNING-4 / WARNING-5 also conformed to the actual `11-VERIFICATION.md` schema and were adopted unchanged.

**Context:** The default reaction to "this was guessed" could be "discard and rebuild." Pitfalls #8 and #9 in 03-RESEARCH.md explicitly recommended validation-and-adopt, which saved authoring time and kept CONTEXT/RESEARCH/PLAN consistent.
**Source:** 03-RESEARCH.md Pitfalls #8 and #9

---

### Pre-existing working-tree dirt complicates clean staging — filter explicitly
Arriving in this session, the working tree carried multiple pre-existing modifications: `.devcontainer/devcontainer.json` + `.planning/config.json` modified; `firestarter_app` submodule dirty; untracked `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-PATTERNS.md` (leftover from a different phase). A naive `git add -A .planning/` would have rolled all of this into the Phase 3 VERIFICATION.md commit.

**Context:** The orchestrator caught this by inspecting `git diff --cached --stat` before committing and explicitly `git restore --staged`-ing the unrelated files. Lesson generalizes: in a long-lived planning-repo branch with parallel work in flight, always inspect what `-A` actually stages before committing — assume drift, not cleanliness.
**Source:** orchestrator session (final VERIFICATION commit prep)

---

## Patterns

### v1.1 form: 8-section body + Re-verification header
Every VERIFICATION.md in this phase follows: `**Phase Goal:**` + `**Verified:** <ISO8601 Z>` + `**Status:**` + `**Re-verification:**` header → 8-section body (Goal → Observable Truths → Required Artifacts → Key Link Verification → [Data-Flow Trace optional] → Behavioral Spot-Checks → Requirements Coverage → Anti-Patterns → [Cross-Milestone Closure optional] → Gaps Summary) → footer (`_Verified:_` + `_Verifier:_`).

**When to use:** Any retroactive or initial phase verification. Drop the two optional sections (Data-Flow Trace; Cross-Milestone Closure) when zero-row. Section ordering came from v1.1 phases/01-VERIFICATION.md (vs. v1.0 form which was looser).
**Source:** 03-RESEARCH.md §"VERIFICATION.md Canonical Template"

---

### `follow_ups` frontmatter schema (5 fields)
```yaml
follow_ups:
  - source: <where the hazard was originally recorded>
    item: "<one-line description of the hazard, including file:line evidence>"
    severity: warning | info
    in_scope: false
    note: "<deferral target with phase/version attribution>"
```
Used 5 times in this phase: WARNING-4 on 08; WARNING-5 on 03, 06, 07 (each with phase-specific `note:`); INFO-3 on 10.

**When to use:** Any open hazard discovered during verification that is **not** in the current phase's scope. The 5-field schema lets `gsd-verify-work` programmatically detect deferred hazards and route them to the owning phase. Source schema: `11-VERIFICATION.md` (v1.0 canonical reference).
**Source:** 03-RESEARCH.md §"`follow_ups` Schema", 03-CONTEXT.md `<specifics>` lines 483-503

---

### Grep-at-write-time evidence resolution
Every `file:line` citation in every VERIFICATION.md was confirmed via `grep -n` against the live tree at write time, not from cached research numbers. Encoded as an explicit acceptance criterion on every task in 03-01-PLAN.md and 03-02-PLAN.md.

**When to use:** Any audit/verification artifact that cites code by line number across a multi-phase production where line numbers shift between research and write. Single source of truth = live tree at commit time.
**Source:** 03-RESEARCH.md Pitfall #7, 03-01-SUMMARY.md patterns log

---

### Inline cite for v1.0→v1.0 closures; dedicated subsection for v1.0→v1.1 closures
- Phase 12 algo-first reachability for REQ-FW-04 is cited **inline** in `04-VERIFICATION.md` Requirements Coverage row — no subsection.
- v1.1 Plan 02-01 WIRE-01 closure for REQ-DB-03 gets a **dedicated** `### Cross-Milestone Closure — REQ-DB-03` subsection in `01-VERIFICATION.md`.

**When to use:** Within-milestone reachability/closure → inline cite suffices. Cross-milestone closure (which carries v1.1 narrative weight + Cross-Milestone audit relevance) → dedicated subsection so it's grep-findable + ROADMAP-checkable.
**Source:** 03-CONTEXT.md "Claude's Discretion", 03-RESEARCH.md §"Cross-Milestone Closure Narrative Sources"

---

### Wave-based parallel execution with worktree isolation + central STATE/ROADMAP ownership
Two-wave execution: Wave 1 = 03-01 (clean batch, 1 plan), Wave 2 = 03-02 (closure/hazard batch, 1 plan). Each plan spawned in an isolated git worktree (`worktree-agent-<id>`). Worktree commits merged back to the feature branch after the executor returned. The orchestrator (not executors) owned STATE.md, ROADMAP.md, REQUIREMENTS.md writes.

**When to use:** Any multi-plan phase with potential for parallel work. Even single-plan-per-wave benefits from worktree isolation because it gives the executor a clean working directory and a clear branch namespace. Central ownership of shared planning files prevents merge conflicts across parallel branches.
**Source:** execute-phase workflow + orchestrator session

---

### Pre-merge STATE/ROADMAP snapshot + post-merge restore (worktree main-wins pattern)
Before merging an executor worktree branch, snapshot `.planning/STATE.md` and `.planning/ROADMAP.md` from main. Perform the merge. Restore the snapshots from main (overwriting the worktree's stale versions). Commit the restore if it produced a diff.

**When to use:** When parallel executors might carry stale orchestrator-owned files in their worktree branch (because they were spawned from an earlier HEAD). The pattern enforces "main always wins" for shared files without breaking the executor's source-tree commits.
**Source:** execute-phase workflow §"Worktree cleanup" step

---

### Atomic commit message convention: `docs(03-NN): retroactive verification — Phase XX (REQ-IDs)`
- Per-file commits: `docs(03-01): retroactive verification — Phase 01 (REQ-DB-01..04)`
- SUMMARY commits: `docs(03-01): plan 03-01 summary — clean batch (...)`
- Verifier commit: `docs(03): phase 03 verification report — PASS`
- Orchestrator chores: `chore(03): mark phase 03 complete in STATE.md and ROADMAP.md`

**When to use:** Documentation-only phases where every commit modifies `.planning/` only. The `docs(NN-PP)` prefix scopes to plan; `chore(NN)` scopes to phase orchestrator work. Bisect-friendly.
**Source:** 03-CONTEXT.md D-13, 03-01-SUMMARY.md, 03-02-SUMMARY.md

---

## Surprises

### Phase 3 ran to PASS in ~17 minutes wallclock
Wave 1 ≈ 8 min, Wave 2 ≈ 7 min, verifier + orchestrator close ≈ 2 min. Documentation-only phases can move fast when the upstream research already pre-computed every `file:line` citation and the executor's only job is to assemble + commit.

**Impact:** Validates the discuss → research → plan upstream effort. The "spend time before code touches anything" pattern paid back in execution speed and zero rework.
**Source:** 03-01-SUMMARY.md (~10 min), 03-02-SUMMARY.md (~10 min), orchestrator session

---

### `READ_WRITE == WRITE_FLAG` dead-check is now ABSENT from memory.cpp (positive verification of removal)
SC#4 verification required confirming the `READ_WRITE == WRITE_FLAG` literal is **not** in `memory.cpp`. Grep returned zero matches — the historically-cited dead check has been removed.

**Impact:** The SC#4 claim "guard intact" is correctly framed: not "guard is unmodified" but "guard is intact AND the dead check it used to coexist with is gone." Positive verification of an absence is itself a verification primitive — worth naming.
**Source:** VERIFICATION.md §"SC#4 Explicit Lock", 10-VERIFICATION.md

---

### `10-CONTEXT.md` lives in `milestones/v1.0-phases/10-static-pins/`, not in the active-phase dir
`10-CONTEXT.md` was authored during v1.0 Phase 10 and was never relocated when v1.0 closed. Phase 3 reads it for evidence (it has rich background on the `static_high_mask` rationale) but deliberately does not move or delete it.

**Impact:** Cleanup deferred per CONTEXT.md `<deferred>`. Lesson: when archiving a milestone, mid-phase CONTEXT/RESEARCH artifacts may end up in milestone history; future audits should not be confused by their location. (Pitfall #6 in 03-RESEARCH.md.)
**Source:** 03-RESEARCH.md Pitfall #6, 10-VERIFICATION.md:131

---

### Discuss-phase YAML guesses matched the canonical schema exactly
CONTEXT.md `<specifics>` lines 483-503 and 494-503 carried verbatim YAML blocks for WARNING-5 and WARNING-4 follow_ups, authored as guesses. RESEARCH.md confirmed they matched the actual `11-VERIFICATION.md` canonical schema with zero corrections needed.

**Impact:** Validation work would have surfaced any divergence. The "match-rate" of discuss-phase guesses against the live schema is a useful trust signal — when high, downstream execution is faster.
**Source:** 03-RESEARCH.md Pitfalls #8 and #9

---

### One plan SUMMARY (03-02) ran longer than 03-01 even though plan structure was symmetric
03-01 SUMMARY ≈ 152 lines; 03-02 SUMMARY ≈ 201 lines. The asymmetry came from SC#3 + SC#4 + SAF-05 closure narratives, the four follow_ups carry-forward, and the "Phase 3 Overall Closure" section that consolidates both plans' work. The "closure/hazard" batch was genuinely heavier than the "clean" batch even though the plan templates were the same shape.

**Impact:** Plan structure symmetry does not guarantee SUMMARY symmetry. Reserve summary-length expectations for the SUMMARY's job (closure narrative), not the plan's shape.
**Source:** 03-01-SUMMARY.md vs 03-02-SUMMARY.md

---

### Worktree path persistence across the orchestrator's perspective is sometimes lossy
After both executor agents returned, the worktrees showed `locked` even after a successful merge — `git worktree remove --force` was rejected once; `-f -f` was needed. Cleanup branch deletion also required a force flag because the local branch was still associated with the locked worktree at the moment of branch deletion.

**Impact:** Worktree cleanup is not idempotent under all lock states. A retry with `-f -f` was always sufficient, but the first attempt failed each time. For workflow generalizability: bake the double-force into the cleanup script.
**Source:** orchestrator session (Wave 1 cleanup)

---

### Cited `eprom.cpp:68-74` range included one line of leading context (line 68)
The protocol-default pulse_delay switch construct opens with `if (handle->pulse_delay == 0) {` at line 69 and the inner `switch (handle->protocol) { ... }` body runs through line 74 (closing brace 75). The citation as `68-74` includes one line of leading context.

**Impact:** Verifier explicitly noted this as "reasonable and common" rather than a defect. The substantive grep targets (`case 0x08:`, `case 0x0B:`) resolve at lines 71-72 verbatim. Cite-the-construct-with-context is an acceptable convention; cite-the-exact-statement-only is not the only valid form.
**Source:** VERIFICATION.md §"Minor Observations"

# Phase 43: Documentation + Milestone Close - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-29
**Phase:** 43-documentation-milestone-close
**Areas discussed:** DOC-01 scope, GATE-1.8 verification approach, PROJECT.md Current Milestone flip (+ Ship-tag policy as follow-up)

---

## Gray Area Picker — Initial Selection

| Option | Description | Selected |
|--------|-------------|----------|
| Ship-tag policy | Beta-only 3.0.0bN vs stable 3.0.1 — tension with v1.6 D-17v2 carry-forward | (deselected initially; surfaced as PROJECT.md follow-up Q3) |
| GATE-1.8 verification approach | Real-hardware vs software-only vs both | ✓ |
| DOC-01 scope | Minimal insertion vs structural pass vs Minimal + CONTRIBUTING.md | ✓ |
| PROJECT.md Current Milestone flip | Promote v1.9-PROPOSED vs clean pause vs keep v1.9 + flip v1.8 to Archive | ✓ |

**User's choice:** PROJECT.md Current Milestone flip, DOC-01 scope, GATE-1.8 verification approach
**Notes:** Ship-tag policy initially deselected; surfaced naturally as a follow-up under PROJECT.md flip (Q3 of that area) since it directly affects what gets recorded in the v1.8 archive block + Plan 43-03.

---

## DOC-01 scope

### Q1 — DOC-01 shape

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal insertion (Recommended) | Add ONE new `## Architecture` section to README.md (flat-module map + layer-rules + tooling subsection). Re-sync CLAUDE.md (de-singleton + Click + flat layout). No TOC rewrite. | ✓ |
| Structural pass | Rewrite README.md TOC; insert Architecture + Module Map + Tooling; add CONTRIBUTING.md. CLAUDE.md fully re-synced. | |
| Minimal + CONTRIBUTING.md | Minimal README.md insertion PLUS new CONTRIBUTING.md file. CLAUDE.md re-synced. | |

**User's choice:** Minimal insertion (Recommended)
**Notes:** Operator continues standing Phase 37–42 "you recommend" delegation pattern; matches the "lean, minimum churn" style locked across the milestone.

### Q2 — Architecture section content

| Option | Description | Selected |
|--------|-------------|----------|
| Module map + tooling (Recommended) | Flat-module map (21 modules, one line each) + layer-boundary rules paragraph + tooling subsection naming ruff/ruff-format/mypy/pytest --cov-fail-under=70. | ✓ |
| Add data-flow diagram | Module map + tooling AS ABOVE + ASCII data-flow diagram showing CLI → resolver → DB → ops → serial flow. | |
| Module map only (lean) | Just module map + tooling. No layer-boundary rules subsection (risks SC#1 drift since it explicitly mentions "layer boundary rules"). | |

**User's choice:** Module map + tooling (Recommended)
**Notes:** Layer-boundary rules paragraph keeps SC#1 honest; data-flow diagram is in CLAUDE.md already so no duplication needed.

### Q3 — CLAUDE.md scope

| Option | Description | Selected |
|--------|-------------|----------|
| Targeted fixes (Recommended) | Fix three stale lines only: drop singleton wording, add new flat modules to Key Files, one-line tooling-gate note. Data Flow + Wire Protocol + DB Pipeline + Constants blocks intact. | ✓ |
| Full re-sync | Rewrite Data Flow diagram + reorganize Key Files into Layers + add Layer Boundary Rules subsection + expand Constants block. | |
| Skip CLAUDE.md | Leave firestarter_app/CLAUDE.md untouched. README is operator-facing; CLAUDE.md staleness is agent-facing risk only. | |

**User's choice:** Targeted fixes (Recommended)
**Notes:** Minimum-churn fix that closes the singleton drift (Phase 36 D-06 changed it); keeps the rest byte-identical for git blame integrity.

### Q4 — Continue or move on?

| Option | Description | Selected |
|--------|-------------|----------|
| Move to GATE-1.8 verification | DOC-01 well-defined; downstream agents have what they need. | ✓ |
| One more question | Open items on autocomplete.md / things.md / firestarter sub-repo SHIELD-REVISIONS.md lockstep. | |

**User's choice:** Move to GATE-1.8 verification
**Notes:** Outstanding items captured as deferred in CONTEXT.md (autocomplete.md / things.md / SHIELD-REVISIONS.md all explicitly out-of-scope).

---

## GATE-1.8 verification approach

### Q1 — Verification path

| Option | Description | Selected |
|--------|-------------|----------|
| Software-only (Recommended) | Trust suite green: 29 syrupy snapshots + test_decoder.py + parity tests + entry-point smoke. GATE-1.8a structurally enforced by GATE-1.8d ring-fence. | |
| Real-hardware smoke | Operator runs `firestarter read -e W27C512` on Modified Rev 0 / Leonardo against v1.6 N=5 baseline. PASS gate via byte-identical match. | |
| Both | Software path as autonomous floor (43-01/43-02); real-hardware smoke as additive UAT step in 43-03 before branch merge. | ✓ |

**User's choice:** Both
**Notes:** Operator wants the bench-smoke witness ON TOP of the suite-green floor — uses USB-passthrough; one bench session; raises operator-visible confidence. This is the only deviation from "single recommended option" across the discussion.

### Q2 — Bench-smoke witness chip / board

| Option | Description | Selected |
|--------|-------------|----------|
| W27C512 on Leonardo / Mod Rev 0 (Recommended) | Existing v1.6 N=5 baselines at .planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/. Diff vs baseline; PASS iff byte-identical. | ✓ |
| AT28C256 on Uno + Rev 2.2 | Different chip family / different algorithm (0x0D). Operator owns Rev 2.2. No prior v1.8 baseline. | |
| Whichever chip is already in socket | Operator picks at UAT time; plan documents read→sha256→re-read→sha256 must-match procedure. | |

**User's choice:** W27C512 on Leonardo / Mod Rev 0 (Recommended)
**Notes:** Anchored to existing v1.6 N=5 baseline — operator picks which of the 15 baseline files based on which Modified Rev 0 sub-revision their bench currently shows.

### Q3 — Where the bench gate lands in plan structure

| Option | Description | Selected |
|--------|-------------|----------|
| Step in 43-03 HUMAN-UAT (Recommended) | Add Step 0 to operator checklist BEFORE branch-merge. Single bench session; mirrors v1.4 Plan 20-01 UAT shape. Phase 43 stays at 3 plans. | ✓ |
| New Plan 43-04 (bench-smoke-only) | Carve out into its own autonomous: false plan BEFORE 43-02 archive. Phase 43 grows to 4 plans. | |
| Part of pre-flight in 43-02 | Bench-smoke run as pre-flight assertion in archive script docstring; tightens gate but couples bench into desk-side script. | |

**User's choice:** Step in 43-03 HUMAN-UAT (Recommended)
**Notes:** Keeps 3-plan structure intact; mirrors v1.6 Phase 30 plan decomposition verbatim with one new step appended to the HUMAN-UAT checklist.

### Q4 — Continue or move on?

| Option | Description | Selected |
|--------|-------------|----------|
| Move to PROJECT.md flip | GATE-1.8 well-defined. | ✓ |
| One more question | Open items on GATE-1.8e wording / GATE-1.8c parity test re-run. | |

**User's choice:** Move to PROJECT.md flip
**Notes:** GATE-1.8 (a–e) verification approach locked.

---

## PROJECT.md Current Milestone flip

### Q1 — Current Milestone target

| Option | Description | Selected |
|--------|-------------|----------|
| Promote v1.9-PROPOSED (Recommended) | Flip Current Milestone v1.8 block to v1.9 PROPOSED. v1.8 becomes shipped-archive section. Mirrors v1.6 close Plan 30-01 default. | ✓ |
| Clean pause | Flip to "No milestone in progress"; demote v1.9 back to backlog. Operator runs /gsd-new-milestone explicitly. | |
| Keep v1.9-PROPOSED + flip v1.8 to Archive | Don't touch v1.9; replace Current Milestone block content with v1.8-shipped-archive. Minimum doc churn. | |

**User's choice:** Promote v1.9-PROPOSED (Recommended)
**Notes:** Reuses existing v1.9 block content verbatim — position swap with old v1.8 Current Milestone block.

### Q2 — "Validated" entries shape

| Option | Description | Selected |
|--------|-------------|----------|
| v1.8 shipped line + archive block (Recommended) | Add v1.8 shipped line to top-of-file ship-history block + v1.8 Archive section between v1.7 and v1.6. Matches v1.4/v1.5/v1.6/v1.7 archive shape. | ✓ |
| Expand "Validated by v1.0" section | Grow the "What Must Be TRUE — Validated" section with v1.8 entries. | |
| Both | v1.8 shipped line + archive block AS ABOVE PLUS expand "What Must Be TRUE" with v1.8 truth-validation entries. | |

**User's choice:** v1.8 shipped line + archive block (Recommended)
**Notes:** Zero new pattern — verbatim mirror of existing archive blocks.

### Q3 — Ship-tag policy (surfaced as DOC-02 follow-up)

| Option | Description | Selected |
|--------|-------------|----------|
| Beta-only 3.0.0b7 (Recommended) | Per v1.6 D-17v2 carry-forward — stable deferred to real read-bug fix. Cut next pre-release 3.0.0b7. firmware sub-repo NOT promoted. meta-repo v1.8-app-cleanup → main per pattern. | ✓ |
| Stable 3.0.1 | Promote firestarter_app v1.8-app-cleanup → beta → main + tag 3.0.1. Argument: SC#3 literally says "beta → stable pattern"; v1.8 is a clean refactor protected by GATE-1.8. | |
| Operator-decides at 43-03 UAT | 43-03 HUMAN-UAT.md documents BOTH options with rationale; operator picks at execution time. CONTEXT.md hedges with `<ship-tag-TBD>` tokens. | |

**User's choice:** Beta-only 3.0.0b7 (Recommended)
**Notes:** D-17v2 carry-forward locked — `3.0.1` stable defers to v1.9 read-bug fix. Plan 43-03 records `3.0.0b7` as LOCKED (no `<ship-tag-TBD>` hedging); operator may overrule at UAT time IFF they accept the read-bug carry, but plan default is beta-only.

### Q4 — Done with discussion?

| Option | Description | Selected |
|--------|-------------|----------|
| I'm ready for context | All major gray areas resolved. Plan structure: 3 plans mirroring v1.6 Phase 30. | ✓ |
| Explore more gray areas | Open items on v1.8-REQUIREMENTS.md shape, ROADMAP collapse target, firestarter_app cruft cleanup, MILESTONES.md v1.7 entry status, CLAUDE.md beyond singleton fix. | |

**User's choice:** I'm ready for context
**Notes:** Outstanding items captured in CONTEXT.md `<canonical_refs>` (REQUIREMENTS.md shape + ROADMAP collapse target both locked via D-05/D-06 referencing v1.6 Plan 30-02 verbatim) and `<deferred>` (cruft cleanup explicitly out-of-scope).

---

## Claude's Discretion

Five Claude's-Discretion items recorded in CONTEXT.md (see D-section "Claude's Discretion"):

1. MILESTONES.md `<TBD-from-43-03>` placeholder set — planner picks exact placeholder strings.
2. Archive script script-or-runbook decision in 43-02 — recommend verbatim mirror of `v1.6-archive.sh`; planner may pick runbook fallback if mirror has bit-rotted.
3. v1.8-REQUIREMENTS.md disposition column shape — recommend Status | Phase | Disposition triple (v1.6 mirror).
4. README Architecture section header level — recommend `## Architecture` level-2; planner may pick `### Architecture` if it nests under existing block.
5. Module map ordering in README — recommend grouping by layer; planner may pick alphabetical.
6. Bench step file-system path for the smoke binary — `/tmp/v18-smoke.bin` recommended; planner may pick `firestarter_app/v18-smoke.bin` if operator wants the artifact preserved.

---

## Deferred Ideas

(Full list in CONTEXT.md `<deferred>` section. Highlights:)

- 3.0.1 stable promotion → v1.9 read-bug fix close (per D-09 + v1.6 D-17v2 carry-forward).
- Firmware sub-repo touch → host-only milestone; stays at `beta@0bbe017` from v1.6 close.
- `eprom_operations.py` mypy strict → v1.9 (per Phase 42 D-07 carry-forward).
- `CONTRIBUTING.md` for firestarter_app → over-engineering for host-CLI of this size; future milestone if contributor volume grows.
- README TOC rewrite + section reorg → future "docs-only" milestone if existing structure proves unwieldy.
- CLAUDE.md full re-sync → v1.9 close if post-RCA changes warrant structural rewrite.
- `autocomplete.md` edits → Phase 41 wrote it; v1.8 doesn't change completion surface.
- `firestarter_app/things.md`, `anything.txt`, `*.bin` cleanup → operator-scratch, not shipping; out of scope.
- `firestarter/doc/SHIELD-REVISIONS.md` lockstep → v1.8 makes no shield changes.
- `/gsd-discuss-milestone v1.9` scope → operator's next move after v1.8 closes; not Phase 43.
- `pluggy` / `Result[T, E]` types → indefinitely deferred (over-abstraction per Phase 42).
- `PROTOSM-01` extract `ProtocolStateMachine` → v1.9-or-later; HIGH complexity; touches read path.

### Reviewed Todos (not folded)

Same three pending todos Phases 37–42 reviewed (all hardware/protocol/DB-content):

- `avrdude-mcu-detection-fallback.md` — v1.9-or-later.
- `serial-cobs-resync-data-path.md` — v1.9-or-later (would change wire framing — GATE-1.8a forbids).
- `w27c512-eeprom-misclassification.md` — DB data, not docs/close work.

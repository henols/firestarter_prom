# Phase 28: Fix Implementation + Unit Test Coverage — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in 28-CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-21
**Phase:** 28-fix-implementation-unit-test-coverage
**Mode:** Auto Mode (no AskUserQuestion prompts; gray areas auto-resolved with recommended options per harness Auto Mode)
**Areas discussed:** Fix shape, Test approach, Branch flow, Plan structure, Documentation drift, Introducing-commit citation, Flash budget, EVIDENCE.md append

---

## Fix shape

| Option | Description | Selected |
|--------|-------------|----------|
| Land PORTx-clear ONLY (Commit 1 alone) | Stage the fix; verify Unity test passes; add `_NOP()` only if bench shows residual jitter | |
| Land BOTH mechanisms as ONE squashed commit | Single atomic "fix(leonardo): read-bug root cause" with both edits | |
| Land BOTH mechanisms as TWO atomic commits | Each commit cites a specific RCA evidence axis; `git bisect`-able if needed | ✓ |

**Choice:** Two atomic commits (D-01).
**Notes:** RCA explicitly implicates BOTH mechanisms with HIGH confidence (78% single-bit-flip distribution + multi-instruction port-read race). Phase 28 is desk-side TDD; bench validation is Phase 29; landing both maximizes Phase 29 green-bar probability. Two commits (not one squashed) preserve `git bisect`-ability and 1:1 map symptom → mechanism → fix in the audit trail. Total flash delta expected ≤ 50 B per binary (deep in noise vs ±200 B threshold per D-07).

---

## Test approach

| Option | Description | Selected |
|--------|-------------|----------|
| Unity native test asserting `rurp_set_data_input` post-conditions | Reuses `[env:native]` + ArduinoFake; tests the FIX (PORTx cleared) not the symptom (2.1% jitter) | ✓ |
| pytest under firestarter_app/tests/ | Host-side parsing test — would require mocking the firmware emit path | |
| Bench-driven empirical test only | Skip native test; rely on Phase 29 multi-board consistency-check as the only acceptance gate | |
| Unity + bench combo | Land native test for Wave A, ALSO run consistency-check against the fixed firmware in Phase 28 | |

**Choice:** Unity native test under `firestarter/test/native/avr/test_data_input/` (D-02).
**Notes:** RCA points entirely to firmware; host-side serial_comm.py is clean (zero CRC failures in bench logs). FIX-02 wants a test demonstrably-fails-on-pre-fix; PORTx post-condition assertions satisfy this cleanly via the existing `[env:native]` infrastructure documented in `firestarter/CLAUDE.md`. Tests the FIX directly (a physical-bus race can't be reproduced under host emulation, but the fix's post-conditions are host-testable). Mirror of Phase 26 host-side `test_consistency_check.py` shape (pre-state → action → post-condition).

---

## Branch flow

| Option | Description | Selected |
|--------|-------------|----------|
| Cut `firestarter/v1.6-read-bug` from `beta` HEAD | Includes the `docs(25)` commit (1 ahead of `3.0.0b4`) — benign | ✓ |
| Cut from exact tag `3.0.0b4` | Strict pin to bench-tested firmware tip | |
| Don't cut; commit to `beta` directly | Violates `[[feedback_branching]]` standing instruction | |

**Choice:** Cut from `beta` HEAD `bc0f5ac` (D-03).
**Notes:** Phase 27 D-03 deferred this branch cut to Phase 28; Wave B didn't fire so it's still pending. The `bc0f5ac docs(25)` commit between `3.0.0b4` and `beta` HEAD is docs-only — no firmware semantics change. Cutting from `beta` HEAD avoids the awkward "branch off a non-HEAD tag" git operation. Promotion to `beta` happens at the Phase 29 boundary per ROADMAP SC#5, NOT inside Phase 28.

---

## Plan structure

| Option | Description | Selected |
|--------|-------------|----------|
| Single combined plan with TDD inside | One plan; commits sequenced internally | |
| Two-wave: Wave A failing test → Wave B fix | Each wave is independently verifiable | ✓ |
| Three-wave: Wave A test, Wave B Commit 1 PORTx-clear, Wave C Commit 2 _NOP() | Finer-grained split | |

**Choice:** Two-wave TDD (D-04 — Plan 28-01 RED scaffold + Plan 28-02 fix).
**Notes:** Matches the v1.2 / v1.3 / Phase 11 / Phase 12 / Phase 17 proven shape. Wave A's RED bar is the audit evidence for FIX-02's "would fail on pre-fix code" half — without it, the claim is unfalsifiable. Wave B bundles both fix commits + GREEN bar + EVIDENCE.md append. Three-wave was rejected because the two fix commits naturally pair (both are in `leonardo_rurp_shield.cpp`, both close the same bug, both go in the same Wave-B verification step).

---

## Documentation drift correction

| Option | Description | Selected |
|--------|-------------|----------|
| Fix all 5 drift locations in Phase 28 | Bundles cleanup with the fix commit | |
| Defer all 5 to Phase 30 milestone close | Phase 30 has DOC-01/DOC-02/MS-01 paperwork scope explicitly | ✓ |
| Mixed — fix the most-visible 2 (CLAUDE.md files); defer the rest | Selective triage | |

**Choice:** Defer all 5 to Phase 30 (D-05).
**Notes:** Phase 27 D-11 explicitly deferred to "Phase 28 polish OR Phase 30 cleanup". Phase 28's center of gravity is fix + test; doc cleanup is paperwork. Phase 30 is the natural home (DOC-01 already moves the bug todo and references the drift context). One exception: `firestarter/platformio.ini:64-65` `; TEMP: 512` STAYS — it's the source-of-truth, not drift.

---

## Introducing-commit citation format

| Option | Description | Selected |
|--------|-------------|----------|
| Cite RCA only | Single line: "See .planning/v1.6-EVIDENCE.md §RCA Findings" | |
| Cite RCA + shape-introducing-commit `5b1f1cd` + tag-walk | Structured footer with all three references | ✓ |
| Cite RCA + full `git bisect` output | Requires bisection (not done; not needed per ROADMAP SC#3 milestone-bracket floor) | |

**Choice:** Structured footer with RCA + `5b1f1cd` shape-intro + tag-walk reference (D-06).
**Notes:** Satisfies FIX-01 (RCA citation) + RCA-03 (milestone-bracket + commit citation where reasonably possible). Tag-walk reference closes the future-maintainer loop without expensive bisection. Matches Phase 21/22/23 atomic-commit-footer pattern.

---

## Flash budget tracking

| Option | Description | Selected |
|--------|-------------|----------|
| Record sizes only if drift > threshold | Skip on no-change boards | |
| Record per-board sizes table in Wave B commit message | All 3 boards, every time | ✓ |
| Skip recording (defer to Phase 30) | Out of phase scope | |

**Choice:** Per-board sizes table in Wave B commit message + EVIDENCE.md append (D-07).
**Notes:** ROADMAP SC#4 verbatim wants this. Expected drift: Leonardo +12-50 B (PORTx-clear + `_NOP()`); Uno + uno328pb untouched (0 B). ±200 B is the auto-flag re-review threshold (Leonardo's 85.4% baseline is the tightest board).

---

## EVIDENCE.md append section

| Option | Description | Selected |
|--------|-------------|----------|
| Append `## Phase 28 — Fix Commit References` to EVIDENCE.md | Honors line-110 forward-annotation; single-file accretion pattern | ✓ |
| Create standalone `.planning/v1.6-FIX-COMMITS.md` | Separates evidence from accretion artifact | |
| Skip the append (let Phase 30 archive handle it) | Loses cross-phase visibility | |

**Choice:** Append to EVIDENCE.md per line-110 anchor (D-08).
**Notes:** Same single-evidence-file pattern as Phase 26 (baseline) / Phase 27 (RCA) / Phase 29 (post-fix inversion). One file for Phase 30 to archive.

---

## Claude's Discretion

- **Exact `_NOP()` count in Commit 2.** Default to 2 `_NOP()`s (one between PIND/PINC, one between PINC/PINE) with a comment citing the 32U4 datasheet propagation timing; planner can adjust based on docs. Bench-confirmable in Phase 29.
- **`#ifdef ARDUINO_AVR_LEONARDO` exposure for native test.** Likely: inject `-D ARDUINO_AVR_LEONARDO` into `test_data_input/` local build flags so the existing `#ifdef` guard fires under `[env:native]` for this one suite. Researcher picks the cleanest integration.
- **Whether to add a second Unity case for `rurp_read_data_buffer` shift-and-mask reassembly.** Default: yes (regression guard); drop if it adds significant scaffolding overhead.

## Deferred Ideas

- Documentation drift correction (5 locations) — Phase 30 DOC-01/DOC-02.
- `firestarter/platformio.ini:64-65` Leonardo `DATA_BUFFER_SIZE` revert (512 → 1024) — possible Phase 30 polish or post-v1.6 cleanup once Phase 29 confirms the read-bug fix at 512.
- Host CLI cosmetic polish (REVIEW WR-01 FAIL-without-divergence, WR-02 `Board: unknown-board`) — Phase 30 or post-v1.6.
- Backfill Unity test for Uno-side `df5fb44` fix — quality-debt cleanup, no current bug rationale.
- `firestarter info <chip>` crash + `0xda01` W27C512 chip-ID alias gap — out of v1.6 scope per Phase 26 EVIDENCE.md.
- uno328pb-silicon read-path RCA — deferred until operator reflashes the misidentified board per `[[project_uno328pb_correction]]`.
- Three pending todos (`large-read-data-jitter-uno328pb`, `avrdude-mcu-detection-fallback`, `w27c512-eeprom-misclassification`) — reviewed in cross_reference_todos, none folded. The first will be moved out of `pending/` by Phase 30 DOC-01.

---

## Session 2 — Re-iteration (2026-05-26)

**Trigger:** Phase 27 re-open closure (Plan 27-05, 2026-05-26) UNBLOCKED Phase 28 re-iteration with split-scope hand-off. The Phase 28 v1 attempt (commits `437339b6` + `4f205e58`) was proven by Plan 27-04 bench A/B to introduce a Leonardo regression (99% zeros / 0.08% jitter / 5-distinct-SHAs vs Phase 26 baseline 2.1% jitter on structured data). uno328pb regression is structurally independent (Plan 27-04 `.hex` SHA identity `d9e51b7e…`) and not a Phase 28 deliverable.

**Mode:** /gsd-discuss-phase 28 (harness Auto Mode active — gray areas auto-resolved with recommended defaults; no AskUserQuestion prompts).

**Prior context loaded:** `.planning/PROJECT.md`, `.planning/STATE.md`, `.planning/ROADMAP.md` (v1.6 collapsed section + Phase 28 SC#1-5), `.planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Re-open Findings (2026-05-26)"` (lines 378-560), `.planning/phases/27-root-cause-analysis/27-VERIFICATION.md` (re-open verification 14/14 truths), `.planning/phases/27-root-cause-analysis/27-05-SUMMARY.md`, `.planning/phases/27-root-cause-analysis/27-04-SUMMARY.md`, original `28-CONTEXT.md` (now superseded), original `28-DISCUSSION-LOG.md` Session 1.

**Codebase scout:** `firestarter/v1.6-read-bug` HEAD `4f205e58`; clean working tree. `firestarter_app/v1.6-read-bug` HEAD `999c3cc`; clean working tree (sanctioned deviation per Plan 27-04).

### Detection-phase auto-decisions

| Detection | Auto-selected option | Rationale |
|-----------|----------------------|-----------|
| Existing 28-CONTEXT.md from 2026-05-21 detected | **Update it (append re-iteration section; preserve v1 as `_v1_superseded` tag-marked appendix)** | Harness Auto Mode → treat as `--auto`. Audit-trail preservation matches Plan 27-05 immutability pattern. |
| Existing plans 28-01-PLAN.md + 28-02-PLAN.md detected (both completed) | **Continue and replan after (new plans 28-03 + 28-04 added without modifying v1 plans)** | v1 plans are historical artifacts; the re-iteration introduces new plans (numbering 28-03 onwards) without touching 28-01/02. |

### Re-iteration gray areas — auto-resolved (recommended defaults)

| Gray Area | Question | Options considered | Selected (recommended) | Why |
|-----------|----------|-------------------|------------------------|-----|
| A. Revert order | Per-commit bisection-first vs both-at-once | (a) revert `437339b6` first; (b) revert `4f205e58` first; (c) revert both at once | **(a) revert `437339b6` first** | Plan 27-05 fix sketch v2 (`v1.6-EVIDENCE.md:513`) explicit: "revert `437339b6` OR `4f205e58` SEPARATELY". `437339b6` is the more likely primary fault driver (PORTx-clear changes bus-drive timing such that `_NOP()` settling samples bus after chip output collapses). |
| B. Re-fix attempt | Pure revert vs revert + new fix attempt vs activate instrumented-build template | (a) pure revert; (b) revert + new PORTx-clear-with-guard; (c) revert + `_NOP()` count tune; (d) activate Plan 27-05 parked instrumented-build template inside Phase 28 | **(a) pure revert; defer re-fix to v1.8** | Aggressive re-fix burned the confidence budget on the Phase 28 v1 attempt; parked template's substrate (v1.7 shield-detect) hasn't been forward-merged onto `v1.6-read-bug`. v1.6 milestone goal narrows to "ship diagnostic + revert broken fix" (D-17v2). |
| C. GATE-1.6 v2 Axis 4 desk-side closure | Defer Axis 4 entirely to Phase 29 bench wave vs close half desk-side via `.hex` SHA identity | (a) desk-side `.hex` SHA identity check only; (b) defer entirely to Phase 29; (c) both halves in Phase 28 (bench wave inside Phase 28) | **(a) desk-side `.hex` SHA identity check; bench half in Phase 29 v2** | Cheap over-determining falsification for uno328pb branch independence + regression guard for Uno. Plan 27-05 names it as the mandatory GATE-1.6 v2 sub-check. Bench N=5 stays Phase 29 v2's gate. |
| D. Unity test handling | Keep / delete / tombstone the pullup-clear assertion test | (a) delete; (b) keep as expected-fail tombstone; (c) update to assert new behavior | **(a) delete** | Asserted behavior is no longer the intended fix shape post-revert; tombstone introduces ongoing CI noise; the asserted shape is fully documented in `v1.6-EVIDENCE.md §"Fix sketch v2"` for v1.8 pickup. Keep bit-reassembly companion test if it exists in the codebase (researcher confirms). |
| E. Plan structure | Single plan (both reverts) vs primary + conditional | (a) Plan 28-03 single revert + Plan 28-04 conditional second revert; (b) Plan 28-03 both reverts at once; (c) one combined plan | **(a) Plan 28-03 primary (desk-side, autonomous) + Plan 28-04 drafted-but-not-executed (conditional)** | Mirrors v1 Phase 27 Wave A/B drafted-but-not-executed pattern; preserves bisection signal for the v1.8 re-fix substrate. Phase 29 v2 bench result decides whether Plan 28-04 fires. |
| F. EVIDENCE.md append placement | New H2 vs H3 vs edit-in-place | (a) new H2 after `### Re-open final verdict` + before `## Verdict`; (b) new H3 under the existing Phase 28 H2 (line 112); (c) edit-in-place | **(a) new H2 section, append-only** | Preserves the file's append-only convention + the original Phase 28 H2 byte-identical (audit trail). Chronological placement matches the rest of the file (re-open closure → Phase 28 re-iteration → Verdict). Anti-pattern immutability guard SHA-256 on the original H2 mandatory. |
| G. uno328pb handling | Address in Phase 28 vs defer to operator workstream | (a) defer entirely; (b) include diagnostic placeholder section in Phase 28; (c) attempt a uno328pb-specific source edit | **(a) defer entirely (operator workstream)** | `.hex` SHA identity `d9e51b7e…` over-determines that Phase 28's source edits cannot have caused the uno328pb regression. Memory `[[project_uno328pb_bench_instability_27_04]]` is the diagnostic substrate. Phase 28 re-iteration only touchpoint: read-only `.hex` SHA capture for Axis 4 verification. |
| H. Milestone goal re-scope propagation | Update PROJECT.md / MILESTONES.md in Phase 28 vs Phase 30 | (a) propagation paperwork in Phase 28; (b) defer to Phase 30; (c) split — flag in Phase 28, owner in Phase 30 | **(c) flag in Phase 28 via D-17v2; full propagation in Phase 30** | Phase 28 re-iteration's deliverable is the technical substrate (revert + Axis 4 desk-side); Phase 30 owns the narrative. D-17v2 captures the implication for downstream agents (Phase 28 success = revert lands + Axis 4 desk-side passes, NOT Leonardo byte-identical N=5 reads). |

### cross_reference_todos (re-iteration)

No new todo folding. The three pending todos already reviewed in Session 1 carry forward with the same disposition. The v1.6 milestone bug todo (`large-read-data-jitter-uno328pb.md`) will be moved out of `pending/` by Phase 30 re-iteration with re-scoped narrative ("diagnostic shipped + broken fix reverted; proper read-bug fix deferred to v1.8").

### Canonical refs added (re-iteration)

- `.planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Re-open Findings (2026-05-26)"` — line 378.
- `.planning/v1.6-EVIDENCE.md §"Fix sketch v2 (Phase 28 re-iteration hand-off)"` — line 507.
- `.planning/v1.6-EVIDENCE.md §"GATE-1.6 v2 reassessment"` — line 530.
- `.planning/v1.6-EVIDENCE.md §"Re-open final verdict — closing the loop"` — line 544.
- `.planning/phases/27-root-cause-analysis/27-05-SUMMARY.md` — Plan 27-05 synthesis.
- `.planning/phases/27-root-cause-analysis/27-04-SUMMARY.md` — Plan 27-04 bench A/B outcome.
- `.planning/phases/27-root-cause-analysis/27-03-SUMMARY.md` — Plan 27-03 v2 hypothesis table.

### Deferred (re-iteration)

- **Proper Leonardo read-bug re-fix** → v1.8+ (after v1.7 shield-detect substrate forward-merge enables Plan 27-05 parked instrumented-build template activation).
- **uno328pb pre-existing regression** → operator workstream (Rev 2.2 socket contact wear, USB-UART bridge buffering, ATmega328PB Case A bus-read timing audit).
- **Plan 28-04 conditional second revert** → drafted-but-not-executed by default; activates on Phase 29 v2 bench signal.
- **Phase 30 v1.6 milestone close re-scope** → Phase 30 re-discusses separately.
- **Documentation drift correction (5 locations claiming Leonardo 1024-B)** → Phase 30 paperwork (carried forward from v1 D-05).
- **`firestarter/platformio.ini:64-65` DATA_BUFFER_SIZE revert (512 → 1024)** → Phase 30 polish or post-v1.6 (carried forward).
- **Backfill Unity test for Uno `df5fb44` fix** → post-v1.6 quality-debt (carried forward).

### Claude's discretion (re-iteration)

- Whether to commit the test deletion separately from the revert (recommended: separate atomic commit for narrative clarity).
- Whether `test_rurp_read_data_buffer_reassembles_data_bus` exists in the codebase (researcher checks `firestarter/test/native/avr/test_data_input/`).
- Pre-revert `.hex` SHA capture location (recommended: inline in plan task output).
- Anti-pattern immutability guard depth (minimum: SHA-256 on the original `## Phase 28 — Fix Commit References` H2 section).

---

*Phase: 28-fix-implementation-unit-test-coverage*
*Session 1 (v1): 2026-05-21*
*Session 2 (re-iteration): 2026-05-26*

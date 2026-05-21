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

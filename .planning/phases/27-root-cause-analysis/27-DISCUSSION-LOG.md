# Phase 27: Root Cause Analysis - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-21
**Phase:** 27-root-cause-analysis
**Areas discussed:** Investigation approach, Bench dependency profile, Firmware sub-repo branch flow, RCA artifact placement, Buffer-size A/B test scope, Introducing-commit triangulation strategy, Plan structure, Hypothesis prioritization, GATE-1.6 risk assessment, Diagnostic-tool enhancement scope, Documentation drift correction, Branch flow

**Mode:** Auto Mode (harness-level) — recommended option auto-selected for every area; no AskUserQuestion prompts. Operator may redirect after reading CONTEXT.md.

---

## Investigation approach (D-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid desk-side-first, bench-only-if-needed | Wave A reads code + replays Phase 26 binaries; Wave B is conditional instrumented build | ✓ |
| Instrumented FW build first | Cut `firestarter/v1.6-read-bug`, add `-D RCA_INSTRUMENT_*`, flash, run, capture | |
| Pure code reading (no Wave B at all) | Risk: if desk-side reading is inconclusive, RCA-01 fails | |
| Scope/logic-analyzer trace at chip-socket level | ROADMAP SC#1 option (c); expensive bench setup; reserved for last resort | |

**Auto-selected:** Hybrid (recommended).
**Notes:** Phase 26 binaries already on disk; strong starting signal (first-divergence at 0x0003, run_1 anomaly bytes look like address-bit-bleed). Wave B is the safety valve, not the plan. ROADMAP SC#1 lists three RCA methods as ALTERNATIVES, not all-of-three.

---

## Bench dependency profile (D-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Desk-side default; bench escalation reserved | Phase 27 closes desk-side if Wave A verifier accepts the narrative | ✓ |
| Bench required up-front | Forces operator to be available for Phase 27 | |
| Pure desk-side, no bench fallback | Risk: ROADMAP SC#1 unmet if Wave A inconclusive | |

**Auto-selected:** Desk-side default (recommended).
**Notes:** Matches STATE.md "Phase 27 listed as largely desk-side with optional bench instrumentation". The 3-shield A/B/C triage already proved the bug is transport-layer, not RURP-shield-specific.

---

## Firmware sub-repo branch flow (D-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Cut `firestarter/v1.6-read-bug` ONLY if Wave B fires | Branch deferred to Phase 28 if desk-side resolves | ✓ |
| Cut `firestarter/v1.6-read-bug` proactively at Phase 27 start | Always-ready for instrumentation; some commits may not ship | |
| Defer to Phase 28 unconditionally | Risk: if Wave B fires, branch cut blocks Wave B execution | |

**Auto-selected:** Cut only if Wave B fires (recommended).
**Notes:** Phase 26 D-13 deferred the firmware branch to Phase 28 because host-only scope. Phase 27 inherits the same posture; branch cut is gated by Wave B trigger.

---

## RCA artifact placement (D-04)

| Option | Description | Selected |
|--------|-------------|----------|
| Append `## Phase 27 — RCA Findings` section to `.planning/v1.6-EVIDENCE.md` | Single cross-phase evidence file; forward-annotation HTML comment already present | ✓ |
| Standalone `.planning/v1.6-RCA.md` | Cleaner file split per phase; harder for Phase 30 archive | |
| Both — RCA narrative in standalone file + a back-link from EVIDENCE.md | Doubles maintenance surface | |

**Auto-selected:** Append to v1.6-EVIDENCE.md (recommended).
**Notes:** ROADMAP SC#1 lists both options as equivalent. Phase 26 EVIDENCE.md line 20 already carries a forward-annotation HTML comment exactly where Phase 27 appends.

---

## Buffer-size A/B test scope (D-05)

| Option | Description | Selected |
|--------|-------------|----------|
| NO explicit A/B test in Phase 27 | RCA describes the cause, not workarounds; A/B is Phase 28 fix-shape probe | ✓ |
| Run A/B (512 vs 1024) on bench during Wave B | Confirms whether buffer size masks/exposes the bug | |
| Make A/B mandatory in Wave A (no bench needed for static analysis) | Buffer-size question is empirical, not static | |

**Auto-selected:** NO explicit A/B (recommended).
**Notes:** **Critical documentation drift caught during this discuss:** Leonardo currently runs at DATA_BUFFER_SIZE=512 per `firestarter/platformio.ini:64-65` ("TEMP: 512 to match Uno for buffer-size A/B test (was 1024)"). Both Plain Uno and Leonardo ran Phase 26 at 512. The historical "Leonardo 1024-B buffer" claim in PROJECT.md / CLAUDE.md / 26-02-SUMMARY.md / bug-report hypothesis #4 is incorrect. Phase 27 narrative must call this out (D-11).

---

## Introducing-commit triangulation strategy (D-06)

| Option | Description | Selected |
|--------|-------------|----------|
| Milestone-bracket first; commit-precise only if cheap | Read firmware history of the 4 emit-path files; bracket to v1.0/v1.2/v1.4/v1.5 | ✓ |
| Full `git bisect` across firmware history | Bench-gated; expensive; only justified if Wave B fires AND the bisection is the cheapest disambiguation | |
| Skip RCA-03 entirely; accept the milestone-floor-only outcome | Violates ROADMAP SC#3 spirit | |

**Auto-selected:** Milestone-bracket first (recommended).
**Notes:** ROADMAP SC#3 explicitly allows milestone-bracket as the floor: "at minimum bracketed to a milestone (v1.0 vs v1.2 vs v1.4) with rationale". v1.2 message-ID rework introduced `_firestarter_emit_frame_wide` (the MSG_DATA_CHUNK W-04 path) — strongest boundary candidate.

---

## Plan structure (D-07)

| Option | Description | Selected |
|--------|-------------|----------|
| Two-wave: 27-01 desk-side autonomous + 27-02 operator-on-bench CONDITIONAL | Wave B drafted but not executed by default | ✓ |
| Single plan (Plan 27-01 only); spin up a new plan if Wave B is needed | Adds planning round-trip cost mid-phase | |
| Three plans (27-01 desk-side, 27-02 bench, 27-03 narrative consolidation) | Over-decomposed; narrative belongs in Wave A | |

**Auto-selected:** Two-wave with conditional Wave B (recommended).
**Notes:** Mirrors Phase 12's Wave 0/1 split and Phase 26's 26-01/26-02 split. Planner produces both plans in a single pass; executor decides at Wave A verification time whether to enter Wave B.

---

## Hypothesis prioritization (D-08)

| Option | Description | Selected |
|--------|-------------|----------|
| Pre-ranked hypothesis list locked at start of Wave A | 7 hypotheses ranked, status (favored/retained/refuted/out-of-scope); Wave A confirms one or generates new + disposes | ✓ |
| Narrate hypothesis findings post-hoc only | Less grep-friendly; researcher may chase irrelevant leads | |
| No formal hypothesis list; researcher follows the evidence | Risk: undisciplined exploration | |

**Auto-selected:** Pre-ranked list (recommended).
**Notes:** Phase 26 narrowing already eliminated hypothesis #3 (328PB-specific timing — no true 328PB silicon in evidence) and refuted #4 (buffer size — both boards at 512). Lets the researcher target which evidence to mine.

---

## GATE-1.6 risk assessment (D-09)

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit paragraph in RCA narrative, three named risk axes | Write-path timing / VPP regulator / pulse intervals per ROADMAP SC#4 | ✓ |
| Implicit risk assessment via the fix sketch | Less grep-friendly; ROADMAP SC#4 wants explicit prose | |
| Defer risk assessment to Phase 28 planning | Violates ROADMAP SC#4 explicit requirement | |

**Auto-selected:** Explicit three-axis paragraph (recommended).
**Notes:** ROADMAP SC#4 names the three risk axes verbatim; the paragraph either flags one as a mandatory Phase 28 mitigation OR says all three are clear (Phase 28 green light).

---

## Diagnostic-tool enhancement scope (D-10)

| Option | Description | Selected |
|--------|-------------|----------|
| NO enhancements in Phase 27 (RCA scope only) | REVIEW WR-01/WR-02 deferred to Phase 28 polish | ✓ |
| Fix REVIEW WR-01 (FAIL-without-divergence edge) in Phase 27 | Useful for Wave B if Wave B fires, but scope creep | |
| Fix REVIEW WR-02 (`Board: unknown-board`) in Phase 27 | Cosmetic; doesn't affect RCA | |

**Auto-selected:** No enhancements (recommended).
**Notes:** Phase 27's mandate is to find the cause, not improve tooling. Phase 29 stdout-regex contract doesn't depend on either WARNING.

---

## Documentation drift correction (D-11)

| Option | Description | Selected |
|--------|-------------|----------|
| RCA narrative explicitly calls out and corrects the "Leonardo 1024-B buffer" drift | Researcher audits 5 named locations + cites correction inline | ✓ |
| Direct edits to the 5 drifted files in Phase 27 | Scope creep; cleanup is Phase 28/30 territory | |
| Silently ignore the drift | Violates ROADMAP SC#2's future-maintainer-readable spirit | |

**Auto-selected:** Call-out in RCA narrative (recommended).
**Notes:** Locations: `26-02-SUMMARY.md:147`, `large-read-data-jitter-uno328pb.md:57`, `firestarter/CLAUDE.md` "Board differences", meta-repo `CLAUDE.md`. Source-of-truth: `firestarter/platformio.ini:64-65`.

---

## Branch flow (D-12)

| Option | Description | Selected |
|--------|-------------|----------|
| Meta `main`; firestarter_app `v1.6-read-bug` (existing); firestarter `beta` unless Wave B fires | Mirrors Phase 26 D-13 posture | ✓ |
| All 3 repos on `v1.6-read-bug` from Phase 27 start | Pre-cuts firmware branch even if Wave B never fires | |
| Defer all branch decisions to Phase 28 | Risk: Wave B blocked on branch cut at Wave B trigger time | |

**Auto-selected:** Mirror Phase 26 posture (recommended).
**Notes:** Memory `[[feedback_branching]]` invariant honored: no commits to `beta`/`main` of either sub-repo within Phase 27 itself.

---

## Claude's Discretion items (deferred to planner / researcher)

| Item | Disposition |
|------|-------------|
| Exact `-D RCA_INSTRUMENT_*` build flag set (if Wave B fires) | Planner's call after Wave A hypothesis-ranking outcome |
| Whether RCA section includes a hex-dump appendix of first 256 bytes | Researcher's call; useful if hypothesis #2 wins, redundant if hypothesis #1 wins |
| Wave B firmware-branch base (currently `beta@3.0.0b4`) | Planner verifies `beta` HEAD at Wave B trigger time |
| Hypothesis disposition rendering format (table vs prose) | Researcher's call; locked deliverable is disposition existing in some form |
| Whether to add WR-01-fix thought-experiment note to RCA section | Researcher's call (no actual fix; just narrative) |

---

## Deferred ideas captured (out of Phase 27 scope)

- Bench A/B test of `-D DATA_BUFFER_SIZE=1024` revert on Leonardo — Phase 28 fix-shape probe territory.
- Full `git bisect` across firmware history — Wave B optional only; potential post-v1.6 doc curiosity.
- Consistency-check tool enhancements (REVIEW WR-01 / WR-02) — Phase 28 polish or post-v1.6.
- Unparking v1.1 Phase 4 FM1608 byte-0 read bug — different board, likely different root cause; forward-reference only if Phase 27 RCA implicates the data-input path family.
- `firestarter info <chip>` crash — out of v1.6 scope per Phase 26 follow-up.
- W27C512 0xda01 chip-database alias gap — out of v1.6 scope per Phase 26 follow-up.
- uno328pb-silicon RCA leg — DEFERRED until operator reflashes; Phase 29 carries multi-board verification.

---

*Phase: 27-root-cause-analysis*
*Discussion logged: 2026-05-21 via /gsd:discuss-phase 27 (Auto Mode)*

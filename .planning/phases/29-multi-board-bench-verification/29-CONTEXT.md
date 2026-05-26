# Phase 29: Multi-Board Bench Verification — Context

**Gathered:** 2026-05-22 (original v1)
**Re-iteration gathered:** 2026-05-26 (v2 — post Phase 27 re-open + Phase 28 re-iteration close)
**Status:** Re-iteration ready for planning (Phase 29 v2)
**Source:** /gsd:discuss-phase 29 (Auto Mode). v1 captured pre-fix two-commit firmware (`4f205e58`); v2 supersedes after Plan 27-05 RCA re-open close (dual-cause disposition) + Plan 28-03 single revert of `437339b6` (firestarter HEAD now `efd203a`) + Plan 28-04 conditional second-revert PARKED.

---

## Phase 29 Re-iteration (v2) (2026-05-26) — Post-Revert Bench Gate

**v1 context preserved verbatim below.** The v1 decisions describe the original Phase 28 two-commit fix bench verification (`4f205e58` HEAD; the verdict was FAIL on Leonardo + uno328pb 2026-05-22, triggering D-07 milestone-reopens). This re-iteration section captures what changed after Phase 27 RCA re-open + Phase 28 re-iteration; downstream agents MUST read this section first and treat conflicting v1 decisions as superseded. Where v1 decisions still apply unchanged, they are explicitly re-affirmed by ID below.

### Phase Boundary (Re-iteration)

Phase 29 v2 delivers **the post-revert bench gate** — sideload `firestarter/v1.6-read-bug` HEAD (`efd203a`, the Plan 28-03 single revert of `437339b6` with `_NOP()` settling at `4f205e58` PRESERVED) to Leonardo and confirm the Leonardo read-path returns to the Phase 26 baseline shape (structured-data + ~0.44% jitter). The verdict on Leonardo determines two downstream gates atomically:

1. **Plan 28-04 activation gate.** If Leonardo shape stays zeros-dominant (qualitatively like the Phase 29 v1 Attempt 2 ~83.8% zeros), Plan 28-04 (the parked second revert of `4f205e58`) activates and the bench session re-runs after that lands. If Leonardo shape returns to structured-data, Plan 28-04 stays parked permanently and the Phase 28 re-iteration closes fully.
2. **v1.6 milestone close gate (per D-17v2 re-scope).** With the milestone goal narrowed to "ship `dev consistency-check` diagnostic + revert broken Phase 28 fix; defer read-bug fix to v1.8" (Phase 28 D-17v2), a Leonardo PASS = "revert removes regression cleanly" = milestone can close via Phase 30. The original read-bug fix itself is deferred to v1.8.

**In scope (re-iteration):**

- **Wave A v2 (`autonomous: true`, ~3-5 min):** Rebuild Leonardo firmware ONLY from `firestarter/v1.6-read-bug` HEAD (`efd203a`) and capture the new hex SHA-256. Compare against Phase 28 re-iteration Axis 4 desk-side table: pre-revert leonardo SHA `2619eea6…`, post-prune leonardo SHA `734b9a85…` (the latter is the expected Wave A v2 build SHA, since `efd203a` IS the post-prune HEAD). Refresh the Phase 29 EVIDENCE.md section with a `Re-iteration build hash record` block (small addendum, not a new top-level section). NO uno or uno328pb rebuilds — uno code path is unchanged by the revert (Δ=0), uno328pb is deferred to v1.8 per D-29v2.
- **Wave B v2 (`autonomous: false`, operator-on-bench, ~30 min):** Sideload `efd203a`-built `firestarter_leonardo.hex` to Leonardo (chip OUT of socket per `[[feedback_chip_out_before_sideload]]`; verify port identity per `[[feedback_verify_port_identity_each_task]]`). Seat W27C512 (the Phase 26 + Phase 29 v1 chip class). Run `firestarter -p /dev/ttyACM<N> dev consistency-check W27C512 --runs 5`. Capture: (a) per-run SHA-256 across N=5, (b) zero-byte ratio per run, (c) qualitative shape classification (structured-data vs zeros-dominant). Emit Plan 28-04 gate signal to `.planning/v1.6/phase-28-reiteration-verdict.txt` and EVIDENCE.md placeholder section. Optionally re-run VERIFY-03 (1KB shell-loop, N=5) on Leonardo as a low-rate jitter regression check at the same baseline shape.
- **EVIDENCE.md append:** New H3 `### Phase 29 v2 — Post-Revert Bench Verification (YYYY-MM-DD)` inside the existing Phase 29 H2, AFTER the Phase 29 v1 Wave B Attempt 2 FAIL section + AFTER the Phase 28 re-iteration H2 placeholder. The placeholder section that Phase 28 re-iteration prepared (`§"Phase 29 v2 bench verification (placeholder)"` per Plan 28-04 SUMMARY) is filled in here. Records: revert HEAD SHA (`efd203a`), leonardo build hash (expected `734b9a85…` match), per-run SHA + zero-ratio + shape table, verdict, Plan 28-04 gate emission.
- **Acceptance signal:** Leonardo verdict = `structured_data` AND `~0.44% jitter` (matching Phase 26 baseline at `.planning/v1.6-EVIDENCE.md` Phase 26 section) → PASS; Phase 28 re-iteration fully closes; Plan 28-04 parks permanently; Phase 30 unblocks for v1.6 close per D-17v2 re-scope. Verdict = `zeros_dominant` → Plan 28-04 activates; Phase 29 v2 re-runs after the second revert lands.

**Out of scope (re-iteration):**

- **uno328pb bench rerun.** Confirmed independent pre-existing hardware regression per memory `[[project_uno328pb_bench_instability_27_04]]` (W27C512 reads on `/dev/ttyUSB0` Rev 2.2 produce timeouts + 99% 0xff drift; NOT introduced by Phase 28 v1 firmware; over-determined by Plan 27-04 `.hex` SHA falsifier `d9e51b7e…`). Deferred to v1.8 per Phase 28 D-10v2. VERIFY-01 closes as `DEFERRED to v1.8 — independent hardware issue` in EVIDENCE.md Verdict block, not via the v1 D-01 reflash test.
- **Uno bench rerun.** Uno code path is Δ=0 from the revert (the revert only touched `leonardo_rurp_shield.cpp`); Phase 26 PASS verdict carries forward. Optional bonus: operator may re-run Uno N=5 as a triple-replicated regression check, but it is NOT required and NOT gating.
- **BENCH-02 cycle (VERIFY-04 write→read→verify on SST27SF512).** Reframed per D-17v2 milestone re-scope: with the milestone goal narrowed to "revert broken fix; defer read-bug fix to v1.8", the BENCH-02 closure depends on whether the operator wants a write→read→verify confirmation now (post-revert Leonardo write path is unaffected per GATE-1.6 v2 Axis 4 desk-side `.hex` Δ=0; risk is low) OR defers it to v1.8 alongside the actual read-bug fix. Default per D-30v2: SKIP in v2; close VERIFY-04 as `DEFERRED to v1.8 alongside read-bug fix` in EVIDENCE.md.
- **Branch merge / Phase 30 trigger.** Same as v1 — Phase 30 still owns the `v1.6-read-bug → beta → main` merge per ROADMAP Phase 30 SC#5. v2 changes nothing about the branch flow; only the bench verdict ownership shifts (v2 unblocks Phase 30 on Leonardo-structured-data, not on three-board byte-identity).
- **Original 64KB read-bug fix.** Deferred to v1.8 per D-17v2 milestone re-scope. Phase 29 v2 is NOT verifying that the read bug is fixed; it is verifying that the broken Phase 28 fix was successfully reverted and Leonardo returns to Phase 26 baseline shape (which still has ~0.44% jitter — the original bug — but is structured-data, not zeros-dominant).

### Implementation Decisions (Re-iteration)

#### Success criteria re-shape (the load-bearing change)

- **D-21v2: Phase 29 v2 success = Leonardo shape returns to Phase 26 baseline (structured-data + ~0.44% jitter), NOT byte-identical SHA-256 across N=5.** This supersedes the v1 D-08 9-column "Verdict" cells that expected `PASS` to mean `SHAs distinct = 1`.
  Rationale:
  - **Per D-17v2 milestone re-scope**, v1.6 no longer attempts to fix the read bug. The original 64KB read jitter (Phase 26 baseline showed ~0.44% on Leonardo + 2.1% on Uno, depending on shield) is the bug that's being deferred to v1.8. Phase 29 v2's job is to verify the broken Phase 28 fix was reverted cleanly, not to verify the bug is fixed.
  - **Leonardo qualitative-shape classification** is the gate: `structured_data` (matching Phase 26 baseline) = revert removed the regression; `zeros_dominant` (matching Phase 29 v1 Attempt 2 FAIL shape, ~83.8% zeros) = revert insufficient, Plan 28-04 activates.
  - **Phase 26 baseline metric on Leonardo:** Modified Rev 0 + voltage-divider mod + W27C512 → `~0.44% jitter` (from Phase 26 EVIDENCE.md; v1 attempt-2 SUMMARY explicitly cites this baseline for shape comparison).
  - **Per-run SHA-256s are still recorded** for forensic continuity with Phase 26 baseline + Phase 29 v1 Attempts 1+2 (the bench-logs/post-fix-runs archive pattern is preserved), but the gate verdict is shape-based not SHA-equality-based.
  **Output the planner needs:** Wave B v2 verifier evaluates Leonardo's N=5 run output against TWO criteria — (a) zero-byte ratio ≤ 1% (structured-data threshold; Phase 26 baseline was ~0.4-2.1% across boards), (b) qualitative match to Phase 26 Leonardo run-binary archive (structural diff against `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_01.bin`). Emit `gate_verdict: structured_data | zeros_dominant` to the verdict file + EVIDENCE.md placeholder.

#### Plan 28-04 gate signal emission

- **D-22v2: Wave B v2 verifier MUST emit `plan_28_04_gate: pass_parked | activate` to `.planning/v1.6/phase-28-reiteration-verdict.txt` AND mirror to `.planning/v1.6-EVIDENCE.md §"Phase 29 v2 bench verification (placeholder)"` body.**
  Mapping (locked):
  - Leonardo shape = `structured_data` AND zero-byte ratio ≤ 1% → `plan_28_04_gate: pass_parked` (Plan 28-04 parks permanently; Phase 28 re-iteration closes fully; Phase 30 unblocks).
  - Leonardo shape = `zeros_dominant` (zero-byte ratio > 30% across any run in N=5) → `plan_28_04_gate: activate` (Plan 28-04's `executes_only_if: phase_29_v2_leonardo_zeros_dominant` predicate fires; re-open Plan 28-04 via `/gsd-execute-phase 28 --gaps-only` or manual executor spawn; second revert of `4f205e58` lands; Phase 29 v2 re-runs after).
  - Leonardo shape = ambiguous (e.g. zero-byte ratio between 1% and 30%, or qualitative-shape unclear) → `plan_28_04_gate: needs_human` (operator escalation; do not auto-activate).
  Rationale:
  - **Plan 28-04 SUMMARY explicitly cites this gate** at `.planning/phases/28-fix-implementation-unit-test-coverage/28-04-SUMMARY.md §"Decisions Made"` — "Phase 29 v2 operator appends the bench outcome to `.planning/v1.6-EVIDENCE.md` §'Phase 29 v2 bench verification (placeholder)'. If `zeros_dominant: true`, re-run `/gsd-execute-phase 28 --gaps-only` ... the conditional gate flips and the plan executes per its drafted task list."
  - **The verdict file `.planning/v1.6/phase-28-reiteration-verdict.txt`** already exists from Plan 28-03 with `wave_b_needed: false` as the default-before-bench. Wave B v2 verifier APPENDS the bench-confirmed verdict (does NOT overwrite — preserves audit trail of the default-state-before-bench).
  - **Triple-state mapping (pass_parked / activate / needs_human)** prevents auto-activation on edge cases where the zero-ratio is intermediate. Phase 29 v1 Attempts 1 + 2 both saw `>80%` zeros on Leonardo; the threshold-30% conservatively captures clear failure without triggering on noisy baselines.
  **Output the planner needs:** Wave B v2 task list includes an explicit "verifier task" that: (a) reads N=5 run binary zero-byte ratios via the `od -An -tx1 -v <file> | tr -s ' \n' '\n' | grep -c '^00$'` pattern established by Phase 29 v1 Attempt 2 SUMMARY, (b) classifies shape per D-21v2 thresholds, (c) emits the `plan_28_04_gate` triple-state, (d) appends to both the verdict file + EVIDENCE.md placeholder atomically.

#### Wave shape simplification (single-board focus)

- **D-23v2: Wave A v2 rebuilds Leonardo ONLY (single env); Wave B v2 sideloads + verifies Leonardo ONLY (single board, single chip class).** This supersedes v1 D-04's three-env build + three-board verification.
  Rationale:
  - **Uno code path Δ=0 from the revert** (`leonardo_rurp_shield.cpp` only changed; uno hex byte-identical pre/post — confirmed by Phase 28 re-iteration Axis 4 desk-side table: uno SHA `5e7f393a…` IDENTICAL pre/post). Phase 26 Uno PASS verdict carries forward; no bench rerun required.
  - **uno328pb deferred to v1.8** per D-29v2 (separate independent hardware regression). Rebuilding `firestarter_uno328pb.hex` is wasted work.
  - **Bench-session time is operator-precious.** v1 Attempt 1 + Attempt 2 cost ~165 min combined chasing 3-board verification; v2's Leonardo-only focus is ~30 min on bench.
  - **Phase 28 re-iteration Axis 4 desk-side table** already records pre/post-revert hex SHAs for all three envs (`.planning/phases/28-fix-implementation-unit-test-coverage/28-CONTEXT.md` D-13v2 + Plan 28-03 SUMMARY). Wave A v2 ONLY needs to rebuild Leonardo + record the post-prune SHA `734b9a85…` matches; uno + uno328pb are documented as Δ=0 in the existing Axis 4 table.
  **Output the planner needs:** Plan 29-03 (the v2 re-run plan; numbering continues from 29-01 + 29-02 — v2 lands as a NEW plan, not overwriting 29-01/29-02) Wave A task list = "rebuild Leonardo hex from `efd203a`; sanity-check SHA matches Phase 28 re-iteration Axis 4 expected post-prune value". Wave B task list = "sideload Leonardo; run N=5 consistency-check W27C512; classify shape; emit gate signal". No uno or uno328pb bench tasks.

#### EVIDENCE.md schema (re-iteration)

- **D-24v2: New H3 `### Phase 29 v2 — Post-Revert Bench Verification (YYYY-MM-DD)` inside the existing Phase 29 H2, AFTER the Phase 29 v1 Wave B Attempt 2 FAIL block. Fills in the Phase 28 re-iteration H2's `§"Phase 29 v2 bench verification (placeholder)"` reference.** Original Phase 29 v1 content stays byte-identical (audit trail immutable).
  Section structure (locked):
  ```
  ### Phase 29 v2 — Post-Revert Bench Verification (YYYY-MM-DD)

  **Bench session:** YYYY-MM-DD (operator-on-bench, single Leonardo session)
  **Firmware sideloaded:** locally-built `firestarter_leonardo.hex` from `firestarter/v1.6-read-bug` HEAD (`efd203a` — Plan 28-03 revert of `437339b6` + Plan 28-04 parked)
  **Expected leonardo hex SHA:** `734b9a85…` (matches Phase 28 re-iteration Axis 4 post-prune row; see `§"Phase 28 Re-iteration — Revert Commits (2026-05-26)"`)
  **Actual leonardo hex SHA:** <Wave A v2 captures>
  **Branch flow:** sub-repo branches stay LOCAL; no merges; Phase 30 owns promotion if Phase 29 v2 verdict = pass_parked.

  ### Hardware metadata snapshot (Wave B v2 capture)
  | Board | Port | Shield rev | Chip | FW build (commit + version) | Chip ID |
  |-------|------|-----------|------|----------------------------|---------|
  (Operator declares at session start; mirror of v1 D-10 / D-08 schema.)

  ### Per-run results (Leonardo only)
  | Run | SHA-256 | Zero-byte count / 65536 | Zero-byte % | Shape classification |
  |-----|---------|-------------------------|-------------|----------------------|
  | 1 | <sha> | <count> | <pct> | structured | zeros |
  | 2 | <sha> | <count> | <pct> | structured | zeros |
  | 3 | <sha> | <count> | <pct> | structured | zeros |
  | 4 | <sha> | <count> | <pct> | structured | zeros |
  | 5 | <sha> | <count> | <pct> | structured | zeros |

  ### Gate verdict
  - **Leonardo shape:** structured_data | zeros_dominant | ambiguous
  - **Zero-byte ratio (worst case across N=5):** <pct>%
  - **Plan 28-04 gate emission:** pass_parked | activate | needs_human
  - **Mirror to `.planning/v1.6/phase-28-reiteration-verdict.txt`:** <append line with date + emission>
  - **Quals vs Phase 26 baseline:** matches structured-data shape (~0.44% jitter) | differs by ... | matches Phase 29 v1 Attempt 2 zeros-dominant shape

  ### Phase 30 readiness (Phase 29 v2 PASS path only)
  All gates PASS → Phase 30 unblocks per D-17v2 re-scope:
  - DOC-01: move `large-read-data-jitter-uno328pb.md` from `pending/` (with v1.8 deferral note for the actual read-bug fix)
  - DOC-02: PROJECT.md update — v1.6 ships with "diagnostic + revert" disposition; read-bug fix carries to v1.8
  - MS-01: MILESTONES.md v1.6 entry citing the re-scoped goal
  - Sub-repo branch promotion: `firestarter/v1.6-read-bug` → `beta` → `main` (operator-authorized) — note the `_NOP()` settling at `4f205e58` ships to main as part of this; it's not reverted (per Plan 28-04 stays parked)
  - **VERIFY-01 closes as DEFERRED to v1.8** (uno328pb independent hardware issue per D-29v2)
  - **VERIFY-04 closes as DEFERRED to v1.8** (BENCH-02 reframed per D-30v2)

  Any FAIL or activate → Plan 28-04 second revert lands; Phase 29 v2 re-runs after `4f205e58` is reverted; Phase 30 stays blocked.
  ```
  Rationale:
  - **Symmetric audit trail.** v1 H2 stays byte-identical; v2 lands as a NEW H3 inside the existing Phase 29 H2 (not a new top-level H2), reflecting that this is a re-run of the same phase, not a new phase.
  - **Fills the placeholder.** Phase 28 re-iteration's `## Phase 28 Re-iteration — Revert Commits` H2 body contains a `wave_b_needed: false` placeholder reference to `§"Phase 29 v2 bench verification (placeholder)"`; Wave B v2 verifier replaces the placeholder with the live verdict atomically.
  - **Zero-byte ratio table** matches the diagnostic pattern Phase 29 v1 Attempt 2 SUMMARY established (`Pattern (data-shape) — zero-byte ratio is a fast partial-read-failure detector`). Reuses operator's existing muscle memory.
  - **Quals-vs-baseline row** lets the v1.8 future-author see how close Phase 29 v2 came to Phase 26 baseline (anchors the "did the revert fully restore baseline" question for future RCA).
  **Output the planner needs:** Wave B v2 EVIDENCE.md append task writes this exact section structure; verifier task fills in the per-run rows + gate verdict atomically.

#### Existing Plan 29-01 + 29-02 status

- **D-25v2: Existing Plan 29-01 (Wave A v1, shipped 2026-05-22) + Plan 29-02 (Wave B v1, FAILED 2026-05-22) stay as audit trail. v2 lands as new Plan 29-03 (autonomous Wave A v2) + Plan 29-04 (operator-on-bench Wave B v2).** Numbering continues from 29-01/29-02 to preserve audit trail per Phase 28 re-iteration's Plan 28-03/28-04 numbering precedent.
  Rationale:
  - **Audit trail preservation.** Plan 29-01 SUMMARY records the v1 Wave A build (`4f205e58` hex artifacts). Plan 29-02 SUMMARY records the D-07 FAIL with Attempt 1 + Attempt 2 evidence. Both stay immutable as evidence of why the milestone re-opened.
  - **Mirror of Phase 28 re-iteration pattern** (Plans 28-01/02 audit trail + Plans 28-03/04 re-iteration). Phase 29 v2 = Plans 29-03/04.
  - **Plan numbering continuity** keeps `/gsd-execute-phase 29` from auto-discovering only the v2 plans — the executor will list 29-01/02 as completed-with-FAIL + 29-03/04 as pending.
  - **Plan 29-01 hex artifacts are STALE** for v2 (built from `4f205e58`, not `efd203a`). Plan 29-03 rebuilds Leonardo only.
  **Output the planner needs:** `/gsd-plan-phase 29 --gaps` (or `/gsd-plan-phase 29` with awareness of the re-iteration) produces Plans 29-03 (autonomous) + 29-04 (operator-on-bench), NOT overwriting 29-01/02. ROADMAP Phase 29 plan list grows: `[x] 29-01-PLAN.md (v1 Wave A)`, `[x] 29-02-PLAN.md (v1 Wave B — FAIL)`, `[ ] 29-03-PLAN.md (v2 Wave A — rebuild leonardo)`, `[ ] 29-04-PLAN.md (v2 Wave B — bench verify)`.

#### N count + 1KB jitter (re-iteration scope)

- **D-26v2: N=5 floor preserved per v1 D-03; VERIFY-03 1KB shell-loop is OPTIONAL in v2 (operator's call at bench).** v1 D-03 (uniform N=5) and v1 D-05 (1KB shell-loop) still apply where exercised; v2 narrows scope to Leonardo only.
  Rationale:
  - **N=5 keeps symmetric A/B with Phase 26 baseline + Phase 29 v1 Attempts 1+2** (all three captured N=5). v2's Leonardo row reads cleanly in the EVIDENCE.md table at N=5.
  - **VERIFY-03 (1KB jitter)** in v1 D-05 was scoped to "all 3 boards"; v2 narrows to Leonardo. If Leonardo's 64KB shape is `structured_data` per D-21v2, the 1KB shape is over-determined to also be `structured_data` (the 1KB read exercises the same `_run_state_machine` + `_main_phase_read_data` path that the 64KB read exercises, just fewer chunks). Operator can SKIP VERIFY-03 in v2 unless they want a defensive double-check.
  - **If operator runs VERIFY-03 in v2 and Leonardo 64KB is `structured_data` but 1KB is `zeros_dominant`** — that would be a NEW failure mode not seen in v1, and the verifier should classify it as `needs_human` per D-22v2 (not auto-activate Plan 28-04, since that gate is specifically the 64KB shape).
  **Output the planner needs:** Plan 29-04 Wave B task list has a primary "N=5 consistency-check W27C512" task + an optional "N=5 1KB shell-loop W27C512" task marked `(operator-optional; gating only if 64KB result is also `structured_data` AND operator wants defensive coverage)`.

#### Chip class + shield rev (re-iteration scope)

- **D-27v2: W27C512 on Modified Rev 0 + voltage-divider mod (matching Phase 26 Leonardo baseline) is the canonical v2 bench setup.** v1 D-09 (W27C512 for VERIFY-01/02/03) and v1 D-10 (operator declares shield rev at session start) still apply.
  Rationale:
  - **Direct A/B against Phase 26 baseline** requires the same physical setup. Phase 26 Leonardo row was Modified Rev 0 + voltage-divider mod + W27C512 → structured-data + ~0.44% jitter. v2 must match.
  - **v1 Attempt 2 already ran on this exact setup** (Modified Rev 0 + W27C512) and produced 83.8% zeros. v2 runs on the same setup → if the revert works, shape returns to Phase 26 baseline. If shape stays zeros-dominant, the revert is insufficient and Plan 28-04 activates.
  - **Memory `[[user_shield_revisions]]`** still says ASK operator which rev. Auto mode encodes Modified Rev 0 + voltage-divider mod as the DEFAULT for v2 (since v1 Attempt 2 already used it); operator overrides at session start if they want to swap shields.
  **Output the planner needs:** Plan 29-04 Wave B Task 1 ("hardware metadata snapshot") explicitly notes "expected: Modified Rev 0 + voltage-divider mod on Leonardo; operator confirms or overrides".

#### Fail-handling protocol (re-iteration scope)

- **D-28v2: D-07 milestone-reopens behavior is SUPERSEDED for Phase 29 v2.** v1 D-07 said "any FAIL row triggers milestone-reopens"; v2 reframes FAIL semantics per the new gate structure.
  v2 FAIL semantics (locked):
  - **Leonardo shape = `zeros_dominant` (gate emission = `activate`):** This is NOT "milestone reopens" — it is "Plan 28-04 activates per its drafted contract". The Phase 28 re-iteration goal is to *find* whether one revert or two were needed; `activate` is one of the two designed outcomes, not a failure.
  - **Leonardo shape = `ambiguous` (gate emission = `needs_human`):** Operator escalation; manual diagnosis. NOT auto-milestone-reopens.
  - **True milestone-reopens (back to D-07-like state)** only fires if Plan 28-04 lands the second revert + Phase 29 v2 re-runs + STILL shows `zeros_dominant`. That outcome means both reverts were insufficient and the regression has a deeper cause (likely needs v1.8 to disentangle). At that point STATE.md flips to `status: blocked` and v1.6 + v1.7 close pattern repeats (v1.6 ships diagnostic-only; deeper RCA carries to v1.8).
  Rationale:
  - **Per D-17v2 milestone re-scope**, v1.6 milestone close depends on "ship `dev consistency-check` diagnostic + revert broken fix; defer read-bug fix to v1.8". A `zeros_dominant` Leonardo verdict on the FIRST revert (`437339b6` reverted via `ea25174`) is by-design recoverable via the SECOND revert (`4f205e58` reverted via Plan 28-04). It's only a true milestone-reopens if both reverts fail.
  - **Prevents auto-panic.** v1 D-07's "any FAIL → re-open" was correct for the original "fix the bug" goal; v2's re-scoped goal admits a recoverable middle state.
  **Output the planner needs:** Plan 29-04 Wave B verifier task documents the triple-state outcome map explicitly + the "true milestone-reopens" condition (Plan 28-04 lands + Phase 29 v2 re-runs + still zeros).

#### uno328pb deferral handling

- **D-29v2: uno328pb VERIFY-01 closes as `DEFERRED to v1.8 — independent pre-existing hardware regression` in EVIDENCE.md Verdict block.** Supersedes v1 D-01's reflash test entirely.
  Rationale:
  - **Plan 27-05 Outcome B** + Plan 27-04 falsifier `.hex` SHA `d9e51b7e…` IDENTICAL pre/post revert over-determines that Phase 28 firmware changes cannot cause uno328pb regression. The regression is a separate hardware issue.
  - **Memory `[[project_uno328pb_bench_instability_27_04]]`** captures the bench-instability empirically (W27C512 reads on `/dev/ttyUSB0` Rev 2.2 produce timeouts + 99% 0xff drift; distinct from Leonardo bug; NOT introduced by Phase 28 fix; pre-existing).
  - **uno328pb is on Rev 2.2 shield** (v1.7's investigated rev) — the labeled-schematic substrate v1.7 shipped 2026-05-26 will let v1.8 design a proper instrumented A/B build for this regression.
  - **v1.6 ships as "diagnostic + revert"** per D-17v2; the uno328pb regression is explicitly out of scope.
  **Output the planner needs:** Plan 29-04 Wave B EVIDENCE.md Verdict block explicitly writes:
  ```
  - VERIFY-01 (uno328pb byte-identity): DEFERRED to v1.8 — independent pre-existing hardware regression per [[project_uno328pb_bench_instability_27_04]]; Phase 27 Plan 27-04 falsifier `d9e51b7e…` over-determines that Phase 28 firmware cannot cause this. v1.7 labeled-schematic + shield-version-detect substrate (shipped 2026-05-26) provides the foundation for v1.8 RCA on this issue.
  ```

#### BENCH-02 (VERIFY-04) reframing

- **D-30v2: VERIFY-04 (BENCH-02 closure) closes as `DEFERRED to v1.8 alongside the actual read-bug fix` in EVIDENCE.md Verdict block.** Supersedes v1 D-06.
  Rationale:
  - **Per D-17v2**, the read-bug fix itself defers to v1.8. The BENCH-02 acceptance test ("write→read→verify byte-identical") needs a working read path to be meaningful; with the read bug still present (just reverted-fix, not fixed), `cmp <write-image> <readback>` will fail even with the revert.
  - **Phase 26 baseline jitter (~0.44% on Leonardo)** would cause BENCH-02 to FAIL even with the revert — that's the original bug, which is exactly what v1.8 addresses.
  - **GATE-1.6 v2 desk-side (Axis 4) ALREADY closed** per Phase 28 re-iteration: the revert preserves the write path (`.hex` Δ confined to read-bus code on Leonardo). Bench-side write-path validation is NOT load-bearing for v1.6 ship per D-17v2 re-scope.
  - **Operator may volunteer BENCH-02 anyway** as a bonus diagnostic (e.g. to confirm write path observably still works), but it does NOT gate v1.6 close.
  **Output the planner needs:** Plan 29-04 Wave B EVIDENCE.md Verdict block explicitly writes:
  ```
  - VERIFY-04 (BENCH-02 closure): DEFERRED to v1.8 alongside read-bug fix per D-17v2 / D-30v2. Write-path non-regression confirmed desk-side via Phase 28 re-iteration Axis 4 `.hex` SHA identity (uno + uno328pb Δ=0; Leonardo Δ confined to read-bus code). v1.5 BENCH-02 row stays at original "closed with caveat" until v1.8 ships the actual read-bug fix.
  ```

#### Re-affirmed v1 decisions (still apply unchanged)

- **D-02 (LOCAL-sideload build path)** — re-affirmed. `pio run -e leonardo -t upload --upload-port /dev/ttyACM<N>` from `firestarter/v1.6-read-bug` (`efd203a`). NO public release in Phase 29 v2.
- **D-03 (N=5)** — re-affirmed (narrowed to Leonardo per D-23v2).
- **D-05 (1KB shell-loop)** — re-affirmed where exercised (optional in v2 per D-26v2).
- **D-10 (operator declares shield rev at session start; recorded in EVIDENCE.md)** — re-affirmed.
- **Branch flow (v1)** — re-affirmed: Phase 29 v2 stays LOCAL; Phase 30 still owns the merge.
- **Two-plan structure (autonomous Wave A + operator Wave B)** — re-affirmed, just renumbered to 29-03 / 29-04 per D-25v2.

### Canonical References (Re-iteration)

**Downstream agents MUST read these before planning Phase 29 v2.**

#### Primary inputs (Plan 28-03 + Plan 28-04 outcomes)

- `.planning/phases/28-fix-implementation-unit-test-coverage/28-CONTEXT.md` — Phase 28 re-iteration section (lines 1-200), especially D-13v2 (Axis 4 desk-side SHA table), D-14v2 (EVIDENCE.md placement), D-17v2 (milestone goal re-scope to "diagnostic + revert; defer fix to v1.8"), D-09v2 (revert shape — `437339b6` alone, not `4f205e58`).
- `.planning/phases/28-fix-implementation-unit-test-coverage/28-03-SUMMARY.md` — actual revert + prune + EVIDENCE.md H2 append outcome; Axis 4 desk-side SHA table (uno `5e7f393a…` Δ=0, leonardo `2619eea6→734b9a85…`, uno328pb `d9e51b7e…` Δ=0).
- `.planning/phases/28-fix-implementation-unit-test-coverage/28-04-SUMMARY.md` — Plan 28-04 parked-but-resolved record; trigger-evaluation contract (`executes_only_if: phase_29_v2_leonardo_zeros_dominant`); reactivation path documentation.
- `.planning/phases/28-fix-implementation-unit-test-coverage/28-VERIFICATION.md` — Phase 28 re-iteration verification (5/5 truths verified desk-side; FIX-03 bench-side gated to Phase 29 v2; explicit Human Verification block describing the Phase 29 v2 sideload-and-test procedure).
- `.planning/v1.6-EVIDENCE.md §"Phase 28 Re-iteration — Revert Commits (2026-05-26)"` (line ~562) — the canonical re-iteration narrative the Phase 29 v2 EVIDENCE.md append refers back to; contains the `§"Phase 29 v2 bench verification (placeholder)"` placeholder that Wave B v2 fills in.
- `.planning/v1.6/phase-28-reiteration-verdict.txt` — current state: `wave_b_needed: false` (default-before-bench). Wave B v2 APPENDS the bench-confirmed verdict (does NOT overwrite).

#### Phase 29 v1 audit trail (preserved, do not edit)

- `.planning/phases/29-multi-board-bench-verification/29-CONTEXT.md` — this file, v1 section below the v2 re-iteration block.
- `.planning/phases/29-multi-board-bench-verification/29-01-PLAN.md` + `29-01-SUMMARY.md` — v1 Wave A (built `4f205e58` hex artifacts; STALE for v2 but preserved for audit).
- `.planning/phases/29-multi-board-bench-verification/29-02-PLAN.md` — v1 Wave B plan.
- `.planning/phases/29-multi-board-bench-verification/29-02-SUMMARY-attempt1-2026-05-22-INCONCLUSIVE.md` — v1 Attempt 1 (bench-confounded; led to feedback memories).
- `.planning/phases/29-multi-board-bench-verification/29-02-SUMMARY.md` — v1 Wave B FINAL (Attempt 2 D-07 FAIL; chip-swap diagnostic that triggered milestone-reopens).
- `.planning/v1.6-EVIDENCE.md §"Phase 29 — Post-fix Consistency-Check Verification"` (v1 H2, around line 186) — original Phase 29 bench evidence with Wave B Attempt 2 FAIL Verdict block + Wave B FAIL post-mortem.
- `.planning/v1.6/post-fix-runs/W27C512-leonardo-2026-05-22-101119-swap/run_{01..05}.bin` — v1 Attempt 2 Leonardo run binaries (5 distinct SHAs, 83.8% zeros) — Wave B v2 verifier compares its N=5 against these to confirm shape inversion.
- `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_{01..03}.bin` — Phase 26 Leonardo baseline run binaries (~0.44% jitter, structured-data) — Wave B v2 verifier compares its N=5 against these to confirm shape return.

#### Sub-repo source-of-truth (current state for Phase 29 v2)

- `firestarter/v1.6-read-bug` HEAD = `efd203a` (CONFIRMED via `cd firestarter && git log --oneline beta..v1.6-read-bug`). 5-commit chain `bc0f5ac → fdb1ed5 → 437339b6 → 4f205e58 → ea25174 → efd203a` on the topic branch. Wave A v2 builds Leonardo from this tip.
- `firestarter/src/boards/leonardo_rurp_shield.cpp` at `efd203a` — post-revert state. `rurp_set_data_input` no longer clears PORTD/PORTC/PORTE (the `437339b6` block reverted by `ea25174`); `rurp_read_data_buffer` still has `_NOP()` × 2 (the `4f205e58` settling, NOT reverted; Plan 28-04 parks).
- `firestarter_app/v1.6-read-bug` HEAD = `c057fe2` (unchanged from v1; host CLI is read-only for Phase 29 v2 just like v1).

#### Cross-cutting memory

- `[[project_uno328pb_bench_instability_27_04]]` — uno328pb pre-existing hardware regression; independent of Phase 28 firmware; deferred to v1.8 per D-29v2.
- `[[feedback_chip_out_before_sideload]]` — chip OUT of socket before sideload; Wave B v2 honors at sideload time.
- `[[feedback_verify_port_identity_each_task]]` — verify `controller:` identity per port at every task start; Wave B v2 honors after sideload.
- `[[user_shield_revisions]]` — operator owns Rev 2.2, Rev 2.0, modified Rev 0; D-27v2 defaults to Modified Rev 0 + voltage-divider mod (Phase 26 + v1 Attempt 2 setup) but operator may override.
- `[[feedback_branching]]` — Phase 29 v2 stays LOCAL on `v1.6-read-bug`; Phase 30 owns the promotion.

#### v1.7 substrate (informational; not activated by Phase 29 v2)

- `.planning/v1.7-SHIELD-REVS.md` — labeled-schematic + per-rev capability table shipped 2026-05-26 (v1.7 close). Phase 29 v2 does NOT consume this directly, but v1.8 (when it RCAs the uno328pb regression + read-bug fix) will lean on it heavily. Mentioned here for forward-traceability.

#### ROADMAP + traceability

- `.planning/ROADMAP.md §"Phase 29: Multi-Board Bench Verification"` (lines 185-198) — Phase 29 SC#1-5 still defined per v1 framing; D-17v2 / D-29v2 / D-30v2 explicitly DEFER VERIFY-01 + VERIFY-04 to v1.8 in the Verdict block while VERIFY-02 + VERIFY-03 close via Leonardo-shape-return. ROADMAP plan list grows to `29-01 [x] / 29-02 [x] / 29-03 [ ] / 29-04 [ ]` per D-25v2.
- `.planning/PROJECT.md §"v1.6 status"` — already annotated 2026-05-26 with Phase 28 re-iteration outcome + Phase 29 v2 carry; Phase 30 still BLOCKED on Phase 29 v2.

### Deferred Ideas (Re-iteration)

- **uno328pb full bench rerun in v1.6** — DEFERRED to v1.8 per D-29v2. v1.8 RCA will use v1.7's labeled-schematic + shield-version-detect substrate to design a proper instrumented A/B build for the uno328pb regression.
- **BENCH-02 (VERIFY-04) full write→read→verify cycle** — DEFERRED to v1.8 per D-30v2. Read bug must be fixed first; the write-path non-regression is already desk-side-confirmed via Phase 28 re-iteration Axis 4.
- **Plan 28-04 second revert of `4f205e58`** — STAYS PARKED unless Wave B v2 emits `plan_28_04_gate: activate`. Drafted-but-not-executed; activation contract is part of D-22v2.
- **Three-board byte-identity goal (original v1.6 definition of done)** — superseded by D-17v2 milestone re-scope; carries to v1.8 as the new read-bug-fix milestone goal.
- **Public pre-release cut from `firestarter/v1.6-read-bug`** — Phase 30 owns; only triggers if Phase 29 v2 verdict = pass_parked.
- **Optional re-run of Uno N=5 in v2** — operator's discretion; not gating per D-23v2 (Uno Δ=0 from the revert; Phase 26 PASS carries).
- **Optional VERIFY-03 1KB shell-loop in v2** — operator's discretion per D-26v2; not gating since 64KB structured-data over-determines 1KB structured-data.

---

<domain>
## Phase Boundary

Phase 29 delivers **the LOCAL-SIDELOAD operator-on-bench acceptance gate for v1.6** — running the Phase 26 `firestarter dev consistency-check` diagnostic against the post-fix firmware on every participating board and recording byte-identical SHA-256 evidence in `.planning/v1.6-EVIDENCE.md`. The fix shipped in Phase 28 (Leonardo `rurp_set_data_input` PORTx-clear + `rurp_read_data_buffer` `_NOP()` settling) must invert the Phase 26 baseline: Verdict cells flip `FAIL → PASS` and `SHAs distinct` cells go `N → 1`. The low-rate (1KB) jitter via `dev read -s 1024` must also collapse to byte-identity (VERIFY-03), and Phase 24's deferred BENCH-02 (`write → read → verify` on a representative EPROM) closes as a post-hoc row addendum in `.planning/v1.5-BENCH-RESULTS.md` (VERIFY-04). This phase has no source-of-truth code edits and **NO branch merges or remote pushes**; its deliverable is empirical bench evidence captured against firmware built and sideloaded from the LOCAL `firestarter/v1.6-read-bug` branch — the public-channel merge + pre-release cut + `beta → main` promotion are explicitly Phase 30's responsibility per ROADMAP Phase 30 SC#5.

**Why local-sideload before merge:** the v1.4 beta workflow's pre-release cut is irreversible once tagged — a failed bench verdict against a publicly-tagged `3.0.0bN` artifact pollutes the GitHub Pre-release + PyPI pre-release indices with an untested fix and forces a `3.0.0b(N+1)` cleanup tag. Local sideload (build `.hex` via PIO + flash via `pio run -t upload` or `avrdude` directly) keeps a failed verdict private and lets the milestone re-open cleanly via D-07. Only after Phase 29 PASSes does Phase 30 commit to the public release pipeline.

The v1.6 scope-narrowing carried in from Phase 26/27/28 holds:

1. **Leonardo is the only board where the bug actually reproduced in Phase 26** (2.1% jitter at offset `0x0003`, 3 distinct SHA-256s across N=3 runs). Phase 28 closes the underlying defect.
2. **Plain Uno was already PASS in Phase 26** (clean, 3 byte-identical SHAs). Phase 29's Uno verdict is a regression check: the Phase 28 fix touched ONLY Leonardo code paths (`leonardo_rurp_shield.cpp` only; `uno_rurp_shield.cpp` already carried `df5fb44` from 2026-05-13 + Phase 28 `.hex` size table shows Uno Δ=0), so the Uno post-fix verdict MUST remain PASS. Any regression here is a milestone-reopens signal.
3. **The third board labeled `uno328pb` was misidentified** per `[[project_uno328pb_correction]]` (operator clarified 2026-05-21 it's actually a Plain Uno with wrong firmware). Phase 29 resolves the VERIFY-01 mismatch by **reflashing the misidentified board with the post-fix firmware** to either (a) restore a true `uno328pb`-reporting board for the verification (if the silicon is actually 328PB) or (b) confirm the v1.5 misidentification, mark the row DEFERRED, and let code-equivalence with the Uno row carry VERIFY-01 (Phase 28 `.hex` size table shows uno328pb Δ=0; the build differs from Uno only in board-name string + PIO env metadata). See D-01.

**In scope:**

- **Desk-side prep wave (29-01, `autonomous: true`):**
  - Build firmware locally from `firestarter/v1.6-read-bug` (tip `4f205e58`): `pio run -e uno`, `pio run -e leonardo`, `pio run -e uno328pb`. Produces `.pio/build/<env>/firestarter_<env>.hex` for each board (3 hex artifacts). NO push to remote, NO merge to `beta`.
  - Confirm the host CLI is installed locally from `firestarter_app/v1.6-read-bug` (tip `c057fe2`): `cd firestarter_app && pip install -e .`. Verify `firestarter dev consistency-check --help` prints the Phase 26 subcommand surface.
  - Append a Phase 29 SCAFFOLD section to `.planning/v1.6-EVIDENCE.md` at the line-186 (was line-111 pre-Phase-28) anchor: `## Phase 29 — Post-fix Consistency-Check Verification (TBD-YYYY-MM-DD)` heading + empty 9-column row table for each participating board + sub-table for VERIFY-03 (1KB) + sub-section for VERIFY-04 (GATE-1.6 bench rigor) + per-board build hash record (so we know exactly which local commit was on bench). Empty placeholders allow Wave B (bench) to fill in atomically without inventing schema mid-session.
  - Append a Phase 29 SCAFFOLD row to `.planning/v1.5-BENCH-RESULTS.md` for the BENCH-02 post-hoc addendum (VERIFY-04). Placeholder format mirrors v1.5's existing rows + adds a `v1.6 fix reference` column citing the Phase 28 commits (`437339b6` + `4f205e58`) — note these are LOCAL-only SHAs in Phase 29 evidence; they become public SHAs on `firestarter/main` after Phase 30 promotion.
  - Provide an **operator pre-flight checklist** as a top-of-section block: which port = which board, which RURP shield rev to use, which test chip, which **local `.hex` path** to sideload (`firestarter/.pio/build/<env>/firestarter_<env>.hex`), the sideload command (per D-02), the verification commands per board, and the expected verdict per row. Explicitly NOT `firestarter fw -i --pre --force` (that's Phase 30's install-pipeline regression check, after Phase 29 green-lights the merge).
  - Read-only: no firmware sub-repo source edits (the firmware fix already shipped in Phase 28); no remote pushes from any sub-repo or meta-repo.

- **Bench wave (29-02, `autonomous: false` — operator-on-bench):**
  - Sideload the locally-built post-fix firmware to each participating board via `pio run -e <env> -t upload --upload-port /dev/ttyXXX` from the `firestarter/` sub-repo on `v1.6-read-bug` (D-02). Fallback path for the misidentified third board: direct `avrdude -p atmega328pb -c urclock -b 115200 -P /dev/ttyUSB0 -U flash:w:.pio/build/uno328pb/firestarter_uno328pb.hex:i` mirroring v1.5 BENCH-01.
  - Confirm install via `firestarter -p /dev/ttyXXX fw` (no args) — should print `version 3.0.0b4+local, controller <board> on /dev/ttyXXX` (or whatever local-build version string `update_version.py` emits for a non-tagged build; the EXACT version string is recorded in the EVIDENCE.md per-board build hash record, not asserted against a literal tag).
  - Run `firestarter dev consistency-check W27C512 --runs 5 --output-dir .planning/v1.6/post-fix-runs/W27C512-<board>-<YYYY-MM-DD-HHMMSS>` against each participating board. Record one row per board in the Phase 29 EVIDENCE table.
  - Run the **VERIFY-03 1KB shell-loop** on each participating board: `for i in $(seq 5); do firestarter dev read W27C512 -s 1024 /tmp/r1k_<board>_$i.bin; done; sha256sum /tmp/r1k_<board>_*.bin` and record byte-identity in the EVIDENCE table's 1KB sub-section.
  - Run **VERIFY-04 BENCH-02 cycle**: `firestarter write -e SST27SF512 <test-image>.bin` followed by `firestarter dev read SST27SF512 -s <full-chip> <readback>.bin` and `cmp <test-image>.bin <readback>.bin`. Record the result as a post-hoc row addendum in `.planning/v1.5-BENCH-RESULTS.md` citing the Phase 28 fix commits (LOCAL SHAs; Phase 30 may amend the row with post-merge public SHAs if they change — squash-merge would; merge-commit would not).
  - For the misidentified third board: attempt to sideload `firestarter_uno328pb.hex` via the avrdude fallback above. If post-flash handshake reports `uno328pb`, run the same verification as Uno/Leonardo. If sideload fails (signature mismatch) OR handshake reports `uno`, mark the row `DEFERRED — board confirmed misidentified per [[project_uno328pb_correction]]; VERIFY-01 closes via code-equivalence with the Uno row (Phase 28 hex size Δ=0)`.
  - Operator captures a **hardware metadata snapshot table** at session start (mirror of Phase 26's table at `v1.6-EVIDENCE.md:208-212`) — effective hw_rev, physical shield rev, native auto-detect rev, FW build (local-build version string + commit SHA), chip ID seen — because per memory `[[user_shield_revisions]]` the EEPROM hw_revision byte can't distinguish Rev 2.2 / Rev 2.0 / modified Rev 0; the snapshot is the only record of which shield was actually in use.
  - Fill in the EVIDENCE.md scaffold sections with the captured rows. Verdict propagates to the milestone-level v1.6 verdict per ROADMAP SC#3.
  - **Phase 29 closes here with VERIFY-01..04 marked PASS (or FAIL per D-07).** No branch merges, no pushes, no tag cuts. The branches `firestarter/v1.6-read-bug` and `firestarter_app/v1.6-read-bug` stay LOCAL — ready for Phase 30 to promote.

- **Branch flow (Phase 29 only):**
  - `firestarter/v1.6-read-bug` (tip `4f205e58`, LOCAL): stays local, no push, no merge during Phase 29.
  - `firestarter_app/v1.6-read-bug` (tip `c057fe2`, status confirmed at execution — local or already pushed for Phase 26 CI purposes): no new pushes in Phase 29; if already pushed to `origin` for Phase 26's host-side tests, that's pre-existing state and not a Phase 29 action.
  - **Phase 30 owns** (per ROADMAP Phase 30 SC#5): the `v1.6-read-bug` → `beta` merge in both sub-repos (triggers public pre-release cut), the optional install-pipeline regression check via `firestarter fw -i --pre --force`, the `beta` → `main` promotion, and the operator-authorized stable tag bump (e.g., `3.0.1`).
  - Meta-repo (`.planning/phases/29-*/` + `.planning/v1.6-EVIDENCE.md` + `.planning/v1.5-BENCH-RESULTS.md` additions) commits to `main` per the standing meta-repo convention (no topic branch on meta-repo; sub-repos own the topic branches). Meta-repo IS pushed (standard convention) so the EVIDENCE.md captures sync between operator and reviewer.

**Out of scope:**

- **Any merge of `v1.6-read-bug` → `beta` in either sub-repo** — Phase 30 owns this per ROADMAP Phase 30 SC#5. Phase 29 stays LOCAL.
- **Any `beta` → `main` promotion in either sub-repo** — Phase 30.
- **Cutting any pre-release tag** (`3.0.0b5` or otherwise) — Phase 30 triggers this via the v1.4 `beta-build.yml` workflow once the bench evidence in Phase 29 says PASS.
- **`firestarter fw -i --pre --force` install-pipeline regression check** — Phase 30 (after the public pre-release exists). Phase 29 sideloads locally only.
- **Stable tag bump (e.g., `3.0.1`)** — operator-authorized at Phase 30 milestone close.
- The fix itself — closed in Phase 28 (`firestarter/v1.6-read-bug` tip = `4f205e58`). Phase 29 does NOT re-touch `leonardo_rurp_shield.cpp` or any other firmware source.
- RCA narrative — closed in Phase 27.
- Documentation drift correction (the 5 "Leonardo 1024-B" locations from the Phase 27 drift table) — Phase 30 paperwork per Phase 27 D-11 + Phase 28 D-05.
- W27C/E + SST27SF/VF chip-database misclassification fix (`w27c512-eeprom-misclassification.md` todo) — separate v1.7+ milestone. Phase 29 BENCH-02 cycle uses the v1.5-documented workaround (small-window write or UV-erase before re-write) without fixing the underlying DB routing.
- Backfilling a Unity test for the Uno-side `df5fb44` fix — Phase 28 deferred per its `<deferred>` section; post-v1.6 quality-debt.
- Reverting `firestarter/platformio.ini:64-65` Leonardo `DATA_BUFFER_SIZE` from `512` back to `1024` — Phase 28 D-05 + Phase 27 H6 explicitly refuted buffer size as the discriminator. The A/B annotation stays; Phase 29's bench is the validation that the fix works at 512.
- Moving `large-read-data-jitter-uno328pb.md` out of `.planning/todos/pending/` — Phase 30 DOC-01 paperwork.
- MILESTONES.md v1.6 entry, PROJECT.md "Validated"/"Known Gaps" updates, `.planning/phases/26-*/` through `30-*/` archive — all Phase 30 close-out work.
- v1.1 FM1608 byte-0 carryover (separate hardware-gated debug session, parked since 2026-05-18).
- v1.3 CMOS EPROM Family Hardware Validation resume — paused milestone, separate decision tree.
- Host CLI cosmetic polish (Phase 26 REVIEW WR-01 FAIL-without-divergence edge case, WR-02 `Board: unknown-board` cosmetic) — Phase 30 paperwork or post-v1.6.
- `firestarter info <chip>` crash, `0xda01` W27C512 chip-ID alias gap — explicitly out of v1.6 scope per Phase 26 EVIDENCE.md §"Scope changes".

</domain>

<decisions>
## Implementation Decisions

### uno328pb row strategy (the carried-over VERIFY-01 mismatch)

- **D-01: Local-sideload reflash-then-test; fall back to code-equivalence DEFERRAL if sideload confirms misidentification.**
  Phase 26's third row is DEFERRED because the board labeled `uno328pb` in v1.5 bench notes was operator-clarified mid-session as a Plain Uno + wrong firmware (`[[project_uno328pb_correction]]`). VERIFY-01 maps explicitly to `uno328pb`; Phase 29 must resolve the row, not silently skip it. Procedure uses the **locally-built** `firestarter_uno328pb.hex` from `firestarter/v1.6-read-bug` — NOT a public pre-release, since Phase 29 precedes any beta merge.
  Operator procedure (locked):
  1. With the misidentified board plugged in (`/dev/ttyUSB0` per `[[project_bench_findings_v15]]`), sideload the locally-built hex via `pio run -e uno328pb -t upload --upload-port /dev/ttyUSB0 -d firestarter/` (from the meta-repo root). Fallback if PIO upload protocol mismatches the bootloader: `avrdude -p atmega328pb -c urclock -b 115200 -P /dev/ttyUSB0 -U flash:w:firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex:i` (mirrors v1.5 BENCH-01's working `urclock`-bootloader command verbatim).
  2. Post-flash, run `firestarter -p /dev/ttyUSB0 fw` (handshake check). Observe the reported `<board>` slot in the handshake reply.
  3. **Case A — handshake reports `uno328pb`**: the board has true ATmega328PB silicon. Run the full Phase 29 verification (consistency-check N=5 + 1KB shell-loop + BENCH-02 cycle) on this board. Record a real row in the Phase 29 EVIDENCE table with the local commit SHA (`4f205e58`) as the firmware reference.
  4. **Case B — handshake reports `uno` (or avrdude fails with `signature mismatch` — the 328PB signature `0x1E 0x95 0x16` won't match a 328P chip's `0x1E 0x95 0x0F` even with `-F` override producing wrong-CPU-config bits)**: v1.5 misidentification is confirmed at the silicon level. Mark the EVIDENCE row `DEFERRED — board confirmed Plain Uno per [[project_uno328pb_correction]]; VERIFY-01 closes via code-equivalence with Uno row (Phase 28 hex size Δ=0 between uno and uno328pb builds — see EVIDENCE.md Phase 28 size table)`. Optionally sideload `firestarter/.pio/build/uno/firestarter_uno.hex` to restore the board to a working Plain Uno + Phase 28 fix, then run an OPTIONAL "second Uno row" verification.
  5. Either way, the milestone-level VERIFY-01 verdict is recorded with rationale; Phase 30 MILESTONE.md entry cites the chosen outcome explicitly.
  Rationale:
  - **VERIFY-01 maps to `uno328pb` by name in REQUIREMENTS.md line 30.** Silently skipping leaves a coverage gap; explicit DEFERRAL with code-equivalence rationale closes the requirement on the strength of Phase 28's `.hex` size analysis (uno328pb hex Δ=0 — the build is byte-equivalent to the Uno build modulo board-name string + PIO env metadata).
  - **Local sideload is the right tool** because Phase 29 is BEFORE merge — using `firestarter fw -i --pre --force` would require a public pre-release tag that doesn't exist yet, and creating one before bench-confirming the fix is the exact pollution pattern this phase restructure is preventing.
  - **avrdude `urclock` path is operator-proven** from v1.5 BENCH-01 (`firestarter fw -i --pre` post-flash handshake reported `v3.0.0b4 / uno328pb` on `/dev/ttyUSB0`). Same bootloader, same baud, same programmer-id — the local-hex sideload bypasses the host installer but uses identical wire semantics.
  - **Memory `[[uno328pb_correction]]` explicitly says skip for v1.6 read-bug repro; the 2026-05-21 ~57.8% baseline is FW-mismatch, not true 328PB silicon.** This decision honors the memory by not chasing the ~57.8% baseline; the reflash test resolves the ambiguity in one shot.
  - **No new code or DB changes required** — the v1.5 Phase 21 firmware env + Phase 22 release pipeline already emit `firestarter_uno328pb.hex` from `[env:uno328pb]`. Phase 28 builds this artifact identically from `v1.6-read-bug`.
  **Output the planner needs:** PLAN.md Wave B step explicitly enumerates Case A vs Case B branches with the verifier writing the chosen branch's verdict back to EVIDENCE.md + the Phase 29 SUMMARY narrative.

### Local-sideload procedure (firmware + host CLI installable on bench WITHOUT public release)

- **D-02: Local PIO build + `pio -t upload` (or `avrdude -c urclock`) sideload from `firestarter/v1.6-read-bug` LOCAL branch. NO beta merge in Phase 29.**
  Operator builds and installs from the local checkout — bench evidence is captured BEFORE any public release commitment. Phase 30 owns the eventual merge once Phase 29's verdict is green.
  Wave A desk-side build (run from meta-repo root, executable by `gsd-executor`):
  ```bash
  cd firestarter && git checkout v1.6-read-bug && git log -1 --oneline   # confirm tip = 4f205e58
  pio run -e uno          # produces .pio/build/uno/firestarter_uno.hex
  pio run -e leonardo     # produces .pio/build/leonardo/firestarter_leonardo.hex
  pio run -e uno328pb     # produces .pio/build/uno328pb/firestarter_uno328pb.hex
  shasum -a 256 .pio/build/uno/firestarter_uno.hex .pio/build/leonardo/firestarter_leonardo.hex .pio/build/uno328pb/firestarter_uno328pb.hex
  # SHA-256s recorded in EVIDENCE.md per-board build hash row
  cd ../firestarter_app && git checkout v1.6-read-bug && pip install -e .
  firestarter dev consistency-check --help   # confirm Phase 26 subcommand surface
  ```
  Wave B bench sideload (operator-driven, per board):
  ```bash
  # Plain Uno on /dev/ttyACM0
  cd firestarter && pio run -e uno -t upload --upload-port /dev/ttyACM0
  firestarter -p /dev/ttyACM0 fw   # verify post-flash handshake
  # Leonardo on /dev/ttyACM1 (32U4 needs 1200-baud touch then reset — pio handles this)
  pio run -e leonardo -t upload --upload-port /dev/ttyACM1
  firestarter -p /dev/ttyACM1 fw
  # uno328pb on /dev/ttyUSB0 — use avrdude fallback for urclock bootloader
  avrdude -p atmega328pb -c urclock -b 115200 -P /dev/ttyUSB0 \
    -U flash:w:.pio/build/uno328pb/firestarter_uno328pb.hex:i
  firestarter -p /dev/ttyUSB0 fw   # branches per D-01 Case A / Case B
  ```
  Verification:
  - Post-flash, `firestarter fw` (no args) prints `version <local-build-version>, controller <board> on /dev/ttyXXX`. The exact version string depends on whether `update_version.py` ran (probably stale at `3.0.0b4` since nothing in Phase 28 bumped it; the EVIDENCE.md per-board build hash record uses the commit SHA `4f205e58` for unambiguous identification, not the version string).
  - Operator records the per-board SHA-256 of the locally-built `.hex` file + the commit SHA in the Phase 29 EVIDENCE.md SCAFFOLD section's build hash record.
  Rationale:
  - **Bench-test BEFORE merge.** A failed bench verdict against the locally-built artifact stays private — no GitHub Pre-release tag, no PyPI pre-release, nothing to retract. The milestone re-opens cleanly via D-07 without channel pollution. A failed verdict against a publicly-tagged `3.0.0b5` would force a `3.0.0b6` cleanup tag + retract-or-yank dance.
  - **ROADMAP Phase 30 SC#5 already owns the merge.** "Sub-repo branch promotion done: `v1.6-read-bug` → `beta` → `main` in both `firestarter/` and `firestarter_app/`" — this is Phase 30's literal scope. Phase 29's earlier draft incorrectly migrated it into Wave A; corrected here.
  - **`pio -t upload` is the operator's existing build path** — `firestarter/CLAUDE.md` documents `pio run -t upload -e uno` as the canonical flash command. No new tooling.
  - **`avrdude -c urclock` for the uno328pb path** is operator-proven from v1.5 BENCH-01 (the exact `programmer_id="urclock"` finding lives in memory `[[project_bench_findings_v15]]`).
  - **Locked-step coordination is preserved** — no version bump in Phase 29; Phase 30 runs `update_version.py --beta` at merge time to produce the matching app+firmware `3.0.0bN` tags.
  - **Wave A's local-build artifacts (`.pio/build/*/firestarter_*.hex`) MUST be re-built in Phase 30 from the merge commit** (not copied from Phase 29's artifacts) to guarantee `firestarter/beta` HEAD = the artifact source-of-truth. Phase 29's artifacts are operator-bench-only; never published.
  **Output the planner needs:** Wave A's tasks list the 3 `pio run -e <env>` commands + the host CLI install + the SHA-256 build hash capture. Wave B's per-board tasks list the upload command + post-flash handshake + the three verification axes. No merge, no push, no tag.

### N count strategy (consecutive-read sample size)

- **D-03: Uniform N=5 on every participating board.**
  Phase 29 runs `firestarter dev consistency-check W27C512 --runs 5` on every board that takes part in the verification (Uno + Leonardo always; uno328pb iff Case A in D-01). Same N keeps the post-fix evidence table symmetric vs the Phase 26 pre-fix N=3 table.
  Rationale:
  - **REQUIREMENTS.md VERIFY-01 + VERIFY-02 floor is N≥5.** Phase 26's N=3 was the reproduction-grade floor (REPRO-03 minimum); Phase 29's N≥5 is the verification-grade floor.
  - **Symmetric table reads cleanly at milestone close.** Phase 30's MILESTONES.md v1.6 entry will reference both the Phase 26 pre-fix table (N=3, FAIL on Leonardo) and the Phase 29 post-fix table (N=5, PASS on Leonardo) — uniform N inside each table is a clear A/B.
  - **Cost is trivial.** A single 64KB read on Leonardo takes ~3 seconds (per the Phase 26 bench-logs serial-transfer timing); 5 runs = 15 s per board. Total bench-time delta vs N=3 is ~6 s per board — well below operator-noticeable.
  - **VERIFY-03 1KB shell-loop also runs at N=5** for consistency (5 × `dev read -s 1024` per board) — same N across all axes.
  **Output the planner needs:** Wave B's per-board task list specifies `--runs 5` literally + `for i in $(seq 5)` in the shell-loop snippets. EVIDENCE.md row schema's "N" column is `5` for every Phase 29 row.

### Plan structure / wave shape

- **D-04: Two-plan structure — 29-01 (desk-side local build, `autonomous: true`) + 29-02 (operator-on-bench, `autonomous: false`). NO merge/promotion in either plan; Phase 30 owns that.**
  - **Plan 29-01 — Desk-side local build + scaffold (`autonomous: true`, ~5 min):** Run the 3 `pio run -e <env>` commands from `firestarter/v1.6-read-bug` (tip `4f205e58`) to produce the 3 local `.hex` artifacts. Capture per-board hex SHA-256 to record in EVIDENCE.md. Install host CLI from `firestarter_app/v1.6-read-bug` via `pip install -e .`. Append the Phase 29 SCAFFOLD section to `.planning/v1.6-EVIDENCE.md` at the line-186 anchor (sub-tables for VERIFY-01+02, VERIFY-03, VERIFY-04 + hardware metadata snapshot + per-board build hash record block). Append the Phase 29 SCAFFOLD row to `.planning/v1.5-BENCH-RESULTS.md` for BENCH-02 addendum. Write the operator pre-flight checklist as a top-of-section block (explicit sideload commands per board — `pio run -e uno -t upload --upload-port /dev/ttyACM0`, `pio run -e leonardo -t upload --upload-port /dev/ttyACM1`, `avrdude -c urclock` for the uno328pb path). NO remote pushes, NO merges, NO tags. Closes the desk-side half (no VERIFY-NN closes here; this is pure scaffolding).
  - **Plan 29-02 — Bench wave (`autonomous: false`, operator-on-bench session, ~60-90 min total):** Operator sideloads the locally-built firmware on each board via the Wave A pre-flight commands, captures the hardware metadata snapshot (incl. shield rev per D-10), runs the 3-axis verification per board (full-chip consistency-check N=5 + 1KB shell-loop N=5 + BENCH-02 write→read→verify on SST27SF512), fills in the EVIDENCE.md SCAFFOLD section's rows, fills in the `.planning/v1.5-BENCH-RESULTS.md` post-hoc addendum row, and resolves the uno328pb row per D-01's sideload Case A/B test. Closes VERIFY-01 + VERIFY-02 + VERIFY-03 + VERIFY-04. **Final verifier task: hand off to Phase 30** if all four VERIFY-NN cells are PASS; otherwise milestone re-opens per D-07. NO `beta → main` promotion in this plan — that's Phase 30.
  Plan dependency: 29-01 → 29-02 (Wave B cannot run until the local `.hex` artifacts exist and the host CLI is installed).
  Rationale:
  - **Mirrors Phase 26's pattern exactly.** Plan 26-01 (desk-side tool ship) + Plan 26-02 (operator-on-bench session). Two-plan structure is the proven shape for "desk-side prep + operator session" phases.
  - **Atomic operator-session boundary.** Wave B is one continuous session; splitting per-board across multiple plans adds overhead without diagnostic granularity. Same logic as Phase 26 D-09 ("one plan per session, with all boards inside") — generalizes here.
  - **Build artifacts ready BEFORE the bench session.** Wave A's PIO compile runs desk-side; operator never waits on `pio run` mid-bench-session.
  - **Promotion-to-main is Phase 30's job per ROADMAP** — corrected from this CONTEXT.md's earlier draft which incorrectly placed it in Wave B's verifier task list. Phase 30 already owns `v1.6-read-bug → beta → main` in its SC#5 explicitly.
  **Output the planner needs:** PLAN.md 29-01 + 29-02 with explicit task lists; 29-02 task list enumerates the per-board verification axes + the EVIDENCE.md fill + the Case A/B branch for uno328pb + the green-verdict hand-off to Phase 30 (no branch operations).

### VERIFY-03 (low-rate 1KB jitter) verification mechanism

- **D-05: Operator shell-loop with `sha256sum` — reuses existing `dev read -s 1024` path; no new code.**
  Per-board procedure (locked):
  ```
  for i in $(seq 5); do
    firestarter -p /dev/ttyXXX dev read W27C512 -s 1024 -a 0 /tmp/r1k_<board>_$i.bin
  done
  sha256sum /tmp/r1k_<board>_*.bin
  ```
  Expected post-fix output: 5 identical SHA-256s (1 distinct hash across 5 files).
  Recorded in EVIDENCE.md as a sub-table inside the Phase 29 section:
  ```
  ### VERIFY-03 — 1KB low-rate jitter (post-fix)
  | Board | Port | Chip | N | SHAs distinct | Verdict | Note |
  |-------|------|------|---|---------------|---------|------|
  | uno | /dev/ttyACM0 | W27C512 | 5 | 1 | PASS | 1KB shell-loop byte-identical |
  | leonardo | /dev/ttyACM1 | W27C512 | 5 | 1 | PASS | 1KB jitter resolved post-fix |
  | uno328pb | /dev/ttyUSB0 | W27C512 | 5 | 1 \| DEFERRED | per D-01 |
  ```
  Rationale:
  - **Phase 26 D-06 explicitly locks `dev consistency-check` to full-chip-only.** Adding a `--size N` flag is out of scope (Phase 26 deferred this). The shell-loop satisfies VERIFY-03 without expanding the diagnostic's API surface.
  - **Same wire path, same chunked-read state machine.** `dev read -s 1024` exercises `_run_state_machine` + `_main_phase_read_data` (the same code path Phase 28's fix touches via `rurp_read_data_buffer` / `rurp_set_data_input`). VERIFY-03 is genuinely testing the fix in the small-window regime that the 2026-05-21 triage originally documented at ~0.1% jitter.
  - **Operator muscle memory.** The 2026-05-21 triage script in `large-read-data-jitter-uno328pb.md` already used this exact `sha256sum /tmp/read_$i.bin` shape. No new commands to learn.
  - **VERIFY-03's "if this fails while 1+2 pass, root cause is masked" clause is encoded** — per F-01 below, any FAIL in this sub-table triggers milestone-reopens, not just a row-level FAIL.
  **Output the planner needs:** Wave B task list includes the per-board shell-loop snippet + the sub-table fill. No code changes needed.

### VERIFY-04 (BENCH-02 closure) chip + procedure

- **D-06: SST27SF512 on Leonardo (the previously-failing board) for the BENCH-02 cycle. Single chip, single board, single row.**
  Operator procedure (locked):
  1. Seat SST27SF512 (the v1.5 BENCH-02 chip; electrically-erasable so re-writable). If the chip carries non-blank content from v1.5, run UV-erase OR use a fresh image that does not depend on starting blank (e.g., all-0xAA test pattern).
  2. `firestarter -p /dev/ttyACM1 write -e SST27SF512 <test-image>.bin` — the `-e` flag attempts erase first; will fail with `ERROR: Not supported` per the `w27c512-eeprom-misclassification.md` carry-over. If so, fall back to: small-window write `firestarter -p /dev/ttyACM1 write SST27SF512 <test-image>.bin -a 0 -b` (covers as much address space as the operator has patience for, mirroring the v1.5 BENCH-02 row's small-window workaround).
  3. `firestarter -p /dev/ttyACM1 dev read SST27SF512 -s <size> /tmp/readback.bin` (full-chip OR same address range as step 2 if small-window was used).
  4. `cmp <test-image>.bin /tmp/readback.bin` — exit 0 = byte-identical, exit 1 = mismatch.
  5. Record the result as a post-hoc row addendum in `.planning/v1.5-BENCH-RESULTS.md`:
  ```
  ## Phase 24 BENCH-02 post-hoc closure (2026-MM-DD via v1.6 Phase 29)
  | Bench item | Result | Evidence |
  |-----------|--------|----------|
  | SST27SF512 write→read→verify (Leonardo, post-fix `firestarter/v1.6-read-bug`) | ✓ PASS (byte-identical via cmp) OR ⚠ as before with v1.6 fix evidence | Phase 28 fix commits 437339b6 + 4f205e58; bench session YYYY-MM-DD |
  ```
  Rationale:
  - **Leonardo is the board where the read bug actually existed.** BENCH-02 on Leonardo is the maximally-informative closure — it confirms BOTH the write path is unaffected (Phase 28 GATE-1.6 axis 1) AND the read-back is now byte-identical (the v1.6 fix). Running BENCH-02 on Uno is redundant because Phase 26 already PASS'd Uno on the consistency-check axis.
  - **SST27SF512 over W27C512** because SST is electrically-erasable (in theory; in practice the chip-DB misclassification workaround applies per `w27c512-eeprom-misclassification.md`). Re-writability lets the operator avoid a UV-erase step.
  - **Single chip, single board, single row.** Avoids inflating Phase 29's bench-session scope; VERIFY-04's REQUIREMENTS phrasing is "as a side effect" — one chip-cycle satisfies it.
  - **Memory `[[user_shield_revisions]]` applies** — operator confirms which Leonardo shield is in use at session start (the Phase 26 baseline used modified Rev 0 + voltage-divider mod). For consistency, use the same shield rev as Phase 26 baseline so the A/B is direct. Operator decision; recorded in the hardware metadata snapshot table.
  - **GATE-1.6 bench rigor coincides with VERIFY-04.** Wave B does not need a separate write→read→verify cycle for GATE-1.6 (Phase 28 already proved the diff is read-path-only via desk-side inspection). The VERIFY-04 BENCH-02 row IS the GATE-1.6 bench-rigor evidence.
  **Output the planner needs:** Wave B task list includes the 5 steps above + the row format for `.planning/v1.5-BENCH-RESULTS.md`. Operator handles the small-window-write fallback if the `-e` flag fails.

### Fail-handling protocol (if bench result is FAIL)

- **D-07: Any FAIL row in the Phase 29 EVIDENCE table triggers milestone-reopens — Wave B verifier MUST NOT auto-close VERIFY-NN cells.**
  Per ROADMAP SC#3 verbatim: "If this criterion fails while criteria 1+2 pass, the root cause is masked rather than fixed and the milestone re-opens." Wave B's verifier behavior on any FAIL (any board, any of the 3 axes — full-chip consistency-check, 1KB shell-loop, BENCH-02 write→read→verify):
  1. Capture the failing run binaries + sha256s + offset distributions to EVIDENCE.md (do NOT delete the failure evidence).
  2. Mark the affected VERIFY-NN cell `FAIL` with the row's run output linked.
  3. Append a Wave B FAIL post-mortem prose block to the Phase 29 EVIDENCE section: which board, which axis, which symptom (single-bit-flip distribution, chunk-boundary clustering, etc.), differential vs Phase 26 baseline.
  4. Halt the bench session. Do NOT promote `beta → main`. Do NOT mark VERIFY-NN as closed. Update STATE.md to "v1.6 milestone re-opened — Phase 28 fix masked vs fixed root cause; further RCA needed".
  5. Operator continues debugging out-of-phase (probably a re-open of Phase 27); Phase 29 stays open until a future bench session re-runs with a revised fix.
  Rationale:
  - **ROADMAP SC#3 is literal: "milestone re-opens".** Auto-closing VERIFY-NN on a FAIL would silently violate the success criterion. The plan's verifier MUST encode this branch explicitly.
  - **Phase 26 baseline preserved.** The 2.1% Leonardo jitter at offset `0x0003` is the canonical pre-fix signature; if Phase 29 reproduces a similar distribution (single-bit-flip dominant, partial-erased-chip-correlated, scattered), the fix is masked rather than fixed — Phase 28's `_NOP()` count or the PORTx-clear mask may need adjustment (cf. Phase 28 D-01 "Bench-confirmable in Phase 29" + Phase 28 Claude's-Discretion #1).
  - **Wave B is `autonomous: false`** — the verifier runs WITH the operator on bench. A FAIL is observable in real-time; no risk of an autonomous executor silently inverting the verdict.
  **Output the planner needs:** Wave B verifier task explicitly enumerates the FAIL branch + the STATE.md update + the milestone-reopens annotation in EVIDENCE.md. No auto-retry / auto-debug; halt and surface.

### EVIDENCE.md Phase 29 section schema

- **D-08: Mirror the Phase 26 9-column row schema; append three sub-sections inside `## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD)`.**
  Section structure (locked):
  ```
  ## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD)

  **Bench session:** YYYY-MM-DD (operator-on-bench, single session)
  **Firmware sideloaded to chip:** locally-built `firestarter_<board>.hex` from `firestarter/v1.6-read-bug` (LOCAL branch, commit `4f205e58`) via `pio run -e <env> -t upload` (or `avrdude -c urclock` for uno328pb path)
  **Host CLI:** locally-installed from `firestarter_app/v1.6-read-bug` (tip `c057fe2`) via `pip install -e .`
  **Branch flow (Phase 29):** sub-repo branches stay LOCAL; no merges, no pushes, no public tags. Phase 30 owns the `v1.6-read-bug → beta → main` promotion + pre-release cut (ROADMAP Phase 30 SC#5).

  ### Pre-flight checklist (operator)
  (Wave A populates: per-board port mapping, shield rev expected, sideload commands, expected verdicts.)

  ### Per-board build hash record (Wave A capture)
  | Board | Local hex path | SHA-256 of hex | Source commit | Build timestamp |
  |-------|----------------|----------------|---------------|-----------------|
  | uno | firestarter/.pio/build/uno/firestarter_uno.hex | <sha256> | `4f205e58` | YYYY-MM-DD HH:MM |
  | leonardo | firestarter/.pio/build/leonardo/firestarter_leonardo.hex | <sha256> | `4f205e58` | YYYY-MM-DD HH:MM |
  | uno328pb | firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex | <sha256> | `4f205e58` | YYYY-MM-DD HH:MM |
  (These hash records let Phase 30 verify that the post-merge build produces byte-identical artifacts to the Phase 29 bench-tested artifacts — a strong "what bench OK'd is what got promoted" guarantee.)

  ### Hardware metadata snapshot
  | Board | Effective hw rev | Physical shield | Native auto-detect | FW build (local commit + version string) | Chip ID seen |
  |-------|------------------|-----------------|--------------------|------------------------------------------|--------------|
  (Wave B fills in; mirror of Phase 26 baseline table at lines 208-212. FW build column carries `4f205e58` + the version string the local build emitted — likely `3.0.0b4+local` or the existing `3.0.0b4` if no bump ran.)

  ### VERIFY-01 + VERIFY-02 — Full-chip consistency-check (post-fix; 9-column schema)
  | Board | Port | Chip | N | SHAs distinct | Divergent bytes (run1 vs run2) | First-diverge offset | Verdict | Log |
  |-------|------|------|---|---------------|------------------------------|----------------------|---------|-----|
  | uno | /dev/ttyACM0 | W27C512 | 5 | 1 | 0 / 65536 (0.0%) | — | PASS (regression check) | .planning/v1.6/post-fix-runs/W27C512-uno-YYYY-MM-DD-HHMMSS/ |
  | leonardo | /dev/ttyACM1 | W27C512 | 5 | 1 | 0 / 65536 (0.0%) | — | PASS (FIX CONFIRMED — inverted from Phase 26 FAIL) | .planning/v1.6/post-fix-runs/W27C512-leonardo-YYYY-MM-DD-HHMMSS/ |
  | uno328pb | /dev/ttyUSB0 | <per D-01 Case A or B> | 5 \| — | 1 \| — | 0 / 65536 (0.0%) \| — | PASS \| DEFERRED — code-equivalence with Uno row | .planning/v1.6/post-fix-runs/... \| — |

  ### VERIFY-03 — 1KB low-rate jitter (post-fix)
  | Board | Port | Chip | N | SHAs distinct | Verdict | Note |
  |-------|------|------|---|---------------|---------|------|
  (Wave B fills in per D-05.)

  ### VERIFY-04 — BENCH-02 post-hoc closure
  (Wave B fills in per D-06; cross-references `.planning/v1.5-BENCH-RESULTS.md` post-hoc row addendum.)

  ### Verdict
  - **VERIFY-01:** [CLOSED ✓ | DEFERRED with code-equivalence rationale]
  - **VERIFY-02:** [CLOSED ✓]
  - **VERIFY-03:** [CLOSED ✓ — root cause is NOT masked: 1KB jitter resolved alongside 64KB jitter]
  - **VERIFY-04:** [CLOSED ✓ — Phase 24 BENCH-02 post-hoc row added to v1.5-BENCH-RESULTS.md]

  ### Hand-off to Phase 30
  All VERIFY-NN PASS → Phase 30 may proceed with: `firestarter/v1.6-read-bug` → `firestarter/beta` merge + pre-release cut + `firestarter_app/v1.6-read-bug` → `firestarter_app/beta` merge + PyPI pre-release publish + optional install-pipeline regression check via `firestarter fw -i --pre --force` (asserting post-merge artifacts byte-match the Phase 29 build hash record above) + `beta → main` promotion + operator-authorized stable tag bump.

  Any FAIL → milestone re-opens per D-07; Phase 30 does NOT execute the merge until a future bench session re-validates.
  ```
  Rationale:
  - **9-column schema locked by Phase 26 D-08** ("Important — schema is shared. Phase 27/28/29 must read this CONTEXT.md (or the live `v1.6-EVIDENCE.md`) and follow the same row schema so the file is internally consistent across phases").
  - **Inverts Phase 26 baseline cell-for-cell**: every Verdict cell flips `FAIL → PASS`, every `SHAs distinct` cell goes `N → 1`. The structural symmetry is the milestone's empirical gate.
  - **Sub-section breakdown maps 1:1 to VERIFY-01..04**: easy for the Phase 30 MILESTONES.md scribe to cite per-requirement closure.
  - **Forward-annotation comment for Phase 29 already exists at EVIDENCE.md line 186** (the original line-111 anchor was pushed down by Phase 28's insertion); Phase 29 lands exactly at that anchor.
  **Output the planner needs:** Wave A's EVIDENCE.md scaffold task writes the section header + the 3 sub-table headers + the pre-flight checklist block + the empty Verdict block. Wave B fills in.

### Test chip selection across all 3 verification axes

- **D-09: W27C512 for VERIFY-01/02/03 (consistency-check + 1KB); SST27SF512 for VERIFY-04 (BENCH-02 write→read→verify). Single physical W27C512 chip rotated through all 3 boards.**
  - W27C512 is the Phase 26 baseline chip (Leonardo row uses W27C512 id `0xda01`; Uno row uses W27C512 id `0xda08`). Same chip means direct pre-fix vs post-fix A/B against the committed binaries in `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/`.
  - W27C512 is UV-erasable only (not electrically erasable); does NOT need re-writing between verification runs because the verification is read-only (Phase 26 D-02). Operator rotates the same chip through all 3 boards without modification.
  - SST27SF512 (electrically erasable in theory; current DB classifies as UV-only — `w27c512-eeprom-misclassification.md` workaround applies) is used ONLY for VERIFY-04 (BENCH-02 write→read→verify). Separate physical chip; seated only when the BENCH-02 cycle runs.
  - The Leonardo chip ID variant `0xda01` (vs Uno's `0xda08`) is a known cosmetic mismatch (Phase 26 EVIDENCE.md §"Scope changes" item 2) — not a Phase 29 concern; operator confirms the chip's actual identity by reading it once and noting the variant in the hardware metadata snapshot.
  Rationale:
  - **Symmetric A/B with Phase 26 baseline.** Same chip, same chip rotation, same boards (for the two real boards) → cleanest possible comparison.
  - **VERIFY-04 needs a writable chip** — only SST27SF512 fits, and only because the operator already has the v1.5 BENCH-02 workaround established (small-window write OR UV erase + full write).
  - **Memory `[[v1.5_bench_findings]]`** confirms SST27SF512 is in operator's kit and worked end-to-end for v1.5 BENCH-01.
  **Output the planner needs:** Wave B task list specifies "W27C512 in socket for tasks 1-2 (full-chip consistency-check + 1KB shell-loop); swap to SST27SF512 for task 3 (BENCH-02 write→read→verify)" per-board.

### Shield revision recording (per memory `[[user_shield_revisions]]`)

- **D-10: Operator confirms shield rev at session start; rev recorded in EVIDENCE.md hardware metadata snapshot table. Plan does NOT lock a specific shield rev.**
  Per memory `[[user_shield_revisions]]`: operator owns Rev 2.2, Rev 2.0, modified Rev 0; EEPROM `hw_revision` byte cannot distinguish them; always ASK which rev when "swap the shield" comes up. Phase 26 baseline used:
  - Plain Uno (`/dev/ttyACM0`) + Rev 2.0 shield (override cleared; auto-detect Rev2)
  - Leonardo (`/dev/ttyACM1`) + modified Rev 0 + voltage-divider mod (`--rev 2` override; native auto-detect Rev1)
  For Phase 29's direct A/B vs Phase 26: same shield rev per board is strongly preferred but not required (the bug is firmware-side per the 3-shield A/B/C triage; shield rev is signal-integrity context, not a discriminator).
  Operator records in the Phase 29 EVIDENCE hardware metadata snapshot table (D-08) the shield rev in use at session time. If different from Phase 26 baseline, note in the Verdict block: "Shield rev changed between Phase 26 and Phase 29 — A/B comparison cross-shield; fix verdict still applies because bug is shield-invariant per 3-shield triage".
  Rationale:
  - **Memory says ASK; auto mode means we can't ask**, so the next-best move is to encode the recording requirement explicitly in the EVIDENCE.md schema. The hardware metadata snapshot table makes the rev choice explicit and auditable.
  - **3-shield A/B/C triage already proved bug is shield-invariant** (Phase 26 EVIDENCE.md §"Entry conditions" + `[[user_shield_revisions]]`) → the fix's verdict isn't contingent on shield rev.
  - **Phase 30 MILESTONES.md can cite the shield rev exactly** because Phase 29 records it.
  **Output the planner needs:** Wave B's first task ("session start — hardware metadata snapshot") explicitly enumerates "operator declares which shield rev is on each board" + the row format.

### Phase 24 BENCH-02 post-hoc addendum format

- **D-11: Single post-hoc row addendum in `.planning/v1.5-BENCH-RESULTS.md`; cross-reference the Phase 29 EVIDENCE.md section.**
  Format (locked, append AFTER the existing v1.5 Verdict block at the bottom of the file):
  ```
  ## Phase 24 BENCH-02 post-hoc closure (YYYY-MM-DD via v1.6 Phase 29)

  **Closes:** v1.5 Phase 24 BENCH-02 acceptance criterion ("write→read→verify on a representative EPROM") — previously CLOSED with caveat (Row 11: full-chip read returned ~57% different bytes across consecutive calls; closed on the strength of small-window write verification).

  **Resolution:** v1.6 Phase 28 read-bug fix (firmware commits `437339b6` PORTx-clear + `4f205e58` `_NOP()` settling) eliminates the pre-existing read-streaming jitter. Phase 29 bench session re-runs the write→read→verify cycle and confirms byte-identity.

  | Bench item | Result | Evidence |
  |-----------|--------|----------|
  | SST27SF512 write→read→verify (Leonardo, post-fix `firestarter/v1.6-read-bug` LOCAL build `4f205e58`) | ✓ PASS — byte-identical via `cmp` | Phase 28 fix commits `437339b6` + `4f205e58` (LOCAL on `firestarter/v1.6-read-bug` at Phase 29 time; Phase 30 promotes); Phase 29 EVIDENCE.md §"VERIFY-04 — BENCH-02 post-hoc closure"; bench session YYYY-MM-DD |

  **Verdict:** BENCH-02 fully closed (no caveat). `.planning/todos/pending/large-read-data-jitter-uno328pb.md` ready for Phase 30 DOC-01 move-to-resolved.

  **Note on commit SHAs:** the cited fix commits are LOCAL on `firestarter/v1.6-read-bug` when this row lands. If Phase 30 uses a non-fast-forward merge (default for `beta` workflow), the post-merge `firestarter/beta` HEAD SHAs differ from `437339b6` / `4f205e58`; the original commits stay reachable as merge ancestors. If Phase 30 uses a squash-merge, only the squashed commit SHA appears on `beta`. Either way, the LOCAL SHAs cited here are unambiguous + grep-able in `git log --all`. Phase 30 may amend this row with the public SHAs post-merge for cross-reference.
  ```
  Rationale:
  - **REQUIREMENTS.md VERIFY-04 specifies "post-hoc row addendum in `.planning/v1.5-BENCH-RESULTS.md`"** — this format honors it literally.
  - **Cross-reference enables Phase 30 MILESTONES.md scribe** to cite the v1.5 BENCH-02 closure across two files without re-deriving.
  - **Caveat removal is the empirical signal** that the v1.5 milestone's only deferred item closes cleanly.
  **Output the planner needs:** Wave A scaffolds an empty row template (operator fills in YYYY-MM-DD and the chip-specific result during Wave B).

### Claude's Discretion

- **Whether to run the BENCH-02 write→read→verify on Uno in addition to Leonardo.** Default: NO (Phase 26 already proved Uno's read path is clean; BENCH-02 on Leonardo is the maximally-informative single closure). If operator volunteers a second Uno cycle for confidence, capture as a bonus row but don't make it gating.
- **Whether `pio run -e leonardo -t upload` works for the 32U4's USB-CDC reset dance** vs needing operator-side intervention. Default: trust PIO's bundled `arduino` upload protocol (which handles the 1200-baud touch automatically). If it fails on bench, fall back to manual reset-then-upload pattern; record in EVIDENCE.md.
- **How to handle a partial PASS** (e.g., 4 / 5 SHAs identical) — current encoding treats any non-1 `SHAs distinct` as FAIL per D-07. If operator wants a "marginal" verdict tier, that's a Phase 29 D-07 amendment + EVIDENCE.md schema extension; default is strict binary PASS/FAIL.
- **Whether to capture pre-flash binary baselines for the uno328pb sideload test** (so if Case B fires, the operator has a saved binary to compare the misidentified board's behavior against). Default: NOT captured — the sideload test outcome is binary (handshake reports `uno328pb` or it doesn't); pre-flash baseline adds noise without diagnostic value.
- **Whether `update_version.py` should run in Wave A** to stamp a `+local`/`+phase29` suffix into the version string for clearer EVIDENCE.md traceability. Default: NO — adds unnecessary diff churn; the build-hash record in EVIDENCE.md plus the commit SHA `4f205e58` are already unambiguous identifiers. Operator records the as-built version string verbatim from the handshake reply.

### Folded Todos

None folded. All three pending todos scored 0.6 against Phase 29 keywords but none fit Phase 29's bench-verification scope. See `<deferred>` for review notes.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 29 primary inputs (the evidence + tool chain Phase 29 consumes)

- `.planning/v1.6-EVIDENCE.md` — Phase 26 baseline section (lines 12-19), Phase 27 RCA section (lines 22-108), Phase 28 fix commit reference section (lines 112-185). Phase 29 appends `## Phase 29 — Post-fix Consistency-Check Verification` at the line-186 anchor (the original Phase 29 anchor at line-111 was pushed down by Phase 28's section).
- `.planning/v1.5-BENCH-RESULTS.md` — v1.5 BENCH-01 + BENCH-02 closure rows. Phase 29 VERIFY-04 appends a post-hoc closure section at the bottom per D-11.
- `firestarter_app/tests/test_consistency_check.py` — host-side pytest contract for `dev consistency-check`. Phase 29 does NOT edit this; it relies on the v1.6 stdout regex contract (Phase 26 PLAN.md narrative + Phase 26 Plan 26-01 commit `999c3cc`) staying stable so the operator's per-row verdict parsing is unambiguous.
- `firestarter_app/firestarter/main.py` §`dev` subparser + `firestarter_app/firestarter/eprom_operations.py:consistency_check_eprom` — the diagnostic Phase 29 invokes (read-only, no changes).

### Phase 28 inheritance (the firmware fix Phase 29 verifies)

- `.planning/phases/28-fix-implementation-unit-test-coverage/28-CONTEXT.md` — Phase 28 D-01 fix shape (PORTx-clear + `_NOP()` × 2); D-03 branch flow (`firestarter/v1.6-read-bug` cut from `beta@bc0f5ac`, branch LOCAL only post-Phase-28 — Phase 29 pushes); D-07 per-board hex size table (uno Δ=0, leonardo Δ=+41 B, uno328pb Δ=0 — the size analysis that underwrites D-01 Case B code-equivalence DEFERRAL); D-08 EVIDENCE.md append pattern (Phase 29 mirrors).
- `.planning/phases/28-fix-implementation-unit-test-coverage/28-VERIFICATION.md` — confirms all 5 Phase 28 SC verified; bench half (N≥5 byte-identity on real hardware) explicitly gated to Phase 29 per ROADMAP SC#3.
- `firestarter/src/boards/leonardo_rurp_shield.cpp` (current tip on `firestarter/v1.6-read-bug` = `4f205e58`) — the post-fix code Phase 29's bench session validates. Phase 29 does NOT edit.
- Phase 28 fix commits (LOCAL on `firestarter/v1.6-read-bug` until Phase 29 Wave A merge):
  - `fdb1ed5` — Wave A RED Unity scaffold (test commit; precedes fix)
  - `437339b6` — Commit 1: PORTx-clear in `rurp_set_data_input`
  - `4f205e58` — Commit 2: `_NOP()` settling in `rurp_read_data_buffer`

### Phase 27 carry-through (RCA context Phase 29 cites in EVIDENCE narrative)

- `.planning/phases/27-root-cause-analysis/27-CONTEXT.md` — Phase 27 D-04 EVIDENCE.md single-file accretion pattern; D-05 buffer-size A/B refutation; D-11 documentation drift correction targets deferred to Phase 30.
- `.planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Findings (2026-05-21)"` — the RCA narrative the Phase 29 verifier cites when narrating Verdict block ("inverted from Phase 26 FAIL — PRIMARY mechanism PORTx-clear validated on bench"). Also carries the `[[user_shield_revisions]]` 3-shield A/B/C triage finding.

### Phase 26 carry-through (tool + baseline)

- `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-CONTEXT.md` — Phase 26 D-01 (CLI subcommand naming + signature), D-02 (passive read-only mode), D-04 (stdout verdict format), D-05 (exit code semantics — Phase 29's CI/operator interprets `0`=PASS, `1`=FAIL, `2`=hw error), D-06 (full-chip-only scope; Phase 29 D-05 honors this), D-07 (per-port operator invocation, no orchestrator), D-08 (EVIDENCE.md 9-column schema — Phase 29 D-08 mirrors), D-09 (one plan per session, all boards inside).
- `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-02-SUMMARY.md` — Phase 26 Wave B bench session log; the canonical pre-flight + post-flight narrative Phase 29's pre-flight checklist mirrors.

### Roadmap + requirements (locked phase scope)

- `.planning/ROADMAP.md §"Phase 29: Multi-Board Bench Verification"` (lines 87-99) — Goal + 5 success criteria + dependencies. SC#3 (1KB low-rate jitter; "if this criterion fails while criteria 1+2 pass, the root cause is masked rather than fixed and the milestone re-opens") is encoded in D-07. SC#5 (GATE-1.6 bench-rigor write→read→verify) coincides with VERIFY-04 per D-06.
- `.planning/REQUIREMENTS.md` lines 28-33 — VERIFY-01, VERIFY-02, VERIFY-03, VERIFY-04 verbatim text. N≥5 floor is the requirement-level lock (D-03).

### Build / install toolchain (Phase 29 LOCAL sideload path)

- `firestarter/platformio.ini` — `[env:uno]`, `[env:leonardo]`, `[env:uno328pb]` definitions; Phase 29 Wave A invokes `pio run -e <env>` against each to produce the local `.hex` artifacts. Same env config Phase 22 v1.5 release pipeline uses to produce public artifacts — byte-equivalence between local and post-merge builds is the Wave A → Phase 30 verification guarantee.
- `firestarter/CLAUDE.md` §"Development Commands" — documents `pio run -e <env>` + `pio run -t upload -e <env>` as the canonical local build + flash path. Phase 29 D-02 follows verbatim.
- `firestarter_app/firestarter/main.py` + `eprom_operations.py` — host CLI surface; Phase 29 operator installs via `pip install -e .` from `firestarter_app/v1.6-read-bug` checkout. No PyPI dependency for Phase 29.

### v1.4 release pipeline (Phase 30 uses these; Phase 29 does NOT trigger)

- `firestarter/.github/workflows/beta-build.yml` — v1.4 Phase 17 firmware beta workflow. **Phase 30** triggers this via `firestarter/v1.6-read-bug` → `firestarter/beta` merge once Phase 29 verdict is green.
- `firestarter_app/.github/workflows/beta-build.yml` — v1.4 Phase 16 app beta workflow. **Phase 30** triggers via `firestarter_app/v1.6-read-bug` → `firestarter_app/beta` merge.
- `firestarter_app/firestarter/firmware.py` — v1.4 Phase 18 INST-02 `--pre` flag logic. **Phase 30** install-pipeline regression check (`firestarter fw -i --pre --force`) flows through this; Phase 29 does NOT exercise this path.
- `.planning/milestones/v1.4-RELEASE-PROCEDURES.md` — v1.4 Phase 19 documented procedure for cutting a coordinated beta pre-release. **Phase 30** follows this verbatim.

### Cross-cutting branching + memory

- Memory `[[feedback_branching]]` — all v1.6 work on `v1.6-read-bug` branches in all 3 repos; sub-repos branch off `beta`; promote `beta` → `main` only after operator-green. Phase 29 Wave B's final task implements the promotion.
- Memory `[[user_firestarter_repo_layout]]` — meta-repo at `/workspaces`, firmware sub-repo at `/workspaces/firestarter`, host sub-repo at `/workspaces/firestarter_app`.
- Memory `[[project_bench_findings_v15]]` — programmer_id="urclock" (not "arduino") for the misidentified board's bootloader; port mapping `/dev/ttyUSB0` for that board.
- Memory `[[project_uno328pb_correction]]` — the third board labeled `uno328pb` in v1.5 was actually a Plain Uno + wrong firmware. Phase 29 D-01 encodes the reflash test that resolves the misidentification.
- Memory `[[user_shield_revisions]]` — operator owns Rev 2.2, Rev 2.0, modified Rev 0; EEPROM `hw_revision` byte cannot distinguish them; always ASK which rev. Phase 29 D-10 encodes the recording requirement (since auto mode means we can't ask).
- `.planning/PROJECT.md §"Current Milestone: v1.6 Fix the Read Bug"` — milestone-level decisions (GATE-1.6, branch model, definition of done).

### Phase 24 carry-through (BENCH-02 closure scope)

- `.planning/v1.5-BENCH-RESULTS.md` Row 11 (full-chip 64KB byte-identical verify; previously BLOCKED) + Row 8/9 (small-window write verification; PASS). Phase 29 D-11 appends the post-hoc closure section that converts Row 11's BLOCKED to PASS via the v1.6 fix.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`firestarter dev consistency-check` host CLI command** (`firestarter_app/firestarter/main.py:create_dev_args` + `eprom_operations.py:consistency_check_eprom`) — shipped in Phase 26 Plan 26-01 sub-repo commit `999c3cc`. Phase 29 invokes unchanged with `--runs 5` per board. Stdout verdict regex contract is the row-format anchor.
- **`firestarter dev read -s 1024`** — existing 1KB read path (`firestarter_app/firestarter/main.py` `dev read` subparser per Phase 26 baseline at line 373-388). Phase 29 D-05 wraps in operator shell-loop for VERIFY-03; no new code.
- **`firestarter fw -i --pre --force`** — v1.4 Phase 18 INST-02 + GATE-01 beta-install path; v1.5 BENCH-01 proved end-to-end on `/dev/ttyUSB0` via `urclock` bootloader. Phase 29 reuses verbatim for each board's install step.
- **`firestarter write -e <chip>` + `firestarter dev read <chip> -s <size>` + `cmp`** — the BENCH-02 write→read→verify trio. Phase 29 D-06 reuses with the v1.5 small-window-write workaround (in case `-e` fails per `w27c512-eeprom-misclassification.md`).
- **GitHub Pre-release workflow + PyPI pre-release publish** — v1.4 plumbing (`firestarter/.github/workflows/beta-build.yml` + `firestarter_app/.github/workflows/beta-build.yml`); Phase 29 D-02 triggers via `v1.6-read-bug → beta` merge.
- **`update_version.py --beta`** — v1.4 Phase 15 lockstep coordination tool; auto-bumps `3.0.0bN → 3.0.0b(N+1)` when `BETA_VERSION` not explicitly set. Phase 29 operator confirms the actual cut tag at execution time.

### Established Patterns

- **Two-plan structure (desk-side prep + operator-on-bench session).** Phase 26 (26-01 desk-side + 26-02 bench) + Phase 24 (BENCH-01 desk-side scaffold + bench session). Phase 29 follows the same shape per D-04.
- **EVIDENCE.md cross-phase append-only with forward-annotation anchors.** Phase 26 → 27 → 28 → 29 each append exactly one section via `<!-- Phase N ... -->` anchors. Phase 29 honors the line-186 anchor (was line-111 pre-Phase-28) per D-08.
- **9-column row schema for bench evidence** (Phase 26 D-08). Phase 29's three sub-tables (consistency-check + 1KB + BENCH-02 hardware metadata snapshot) all conform.
- **Locked-step app + firmware pre-release cut** (v1.4 Phase 15 / 16 / 17 coordination). Phase 29 D-02 triggers both sub-repo workflows from a single `BETA_VERSION` input.
- **Operator-on-bench plan = `autonomous: false`; desk-side plan = `autonomous: true`** (Phase 26 D-09 + Phase 12 D-11). Phase 29 D-04 mirrors.
- **Hardware metadata snapshot table** (Phase 26 EVIDENCE.md:208-212). Phase 29 D-10 reuses; recording requirement explicit because memory says ASK and auto mode can't.
- **Per-port operator invocation; no orchestrator** (Phase 26 D-07). Phase 29 keeps three separate manual invocations of `dev consistency-check` per board.

### Integration Points

- **`.planning/v1.6-EVIDENCE.md` line-186 anchor** — Phase 29's append point for `## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD)`. Phase 28's section pushed the original line-111 anchor down; verify the comment position at Wave A execution and adjust line number if Phase 28 SUMMARY further amended.
- **`.planning/v1.5-BENCH-RESULTS.md` (end of file)** — Phase 29's VERIFY-04 post-hoc closure append point.
- **`firestarter/beta` HEAD** — current `bc0f5ac` (1 docs commit ahead of tag `3.0.0b4`); Phase 29 Wave A merges `firestarter/v1.6-read-bug` (`4f205e58`) here.
- **`firestarter_app/beta` HEAD** — Phase 29 Wave A merges `firestarter_app/v1.6-read-bug` (`c057fe2` = Phase 26 tip).
- **Bench hardware:** operator's 3 boards (Plain Uno + Leonardo + misidentified board labeled `uno328pb`) + RURP shield set (Rev 2.2, Rev 2.0, modified Rev 0 — operator picks per session) + test chips (W27C512 for consistency-check; SST27SF512 for BENCH-02).
- **Port mapping (from `[[project_bench_findings_v15]]` + Phase 26 baseline):** `/dev/ttyACM0` = Plain Uno; `/dev/ttyACM1` = Leonardo; `/dev/ttyUSB0` = misidentified board (uno328pb-or-Plain-Uno per D-01 reflash test).

</code_context>

<specifics>
## Specific Ideas

- **The Leonardo verdict is THE acceptance gate.** Uno + uno328pb verdicts are regression checks (Uno already PASS in Phase 26; uno328pb is byte-equivalent to Uno per Phase 28 hex size analysis). The milestone's empirical question — "does the Phase 28 fix actually fix the bug on the only board where the bug reproduced?" — has a binary answer: Leonardo Verdict = PASS (FIX CONFIRMED, milestone ships) OR FAIL (milestone re-opens per D-07).
- **Phase 26 baseline's run binaries stay on disk** (`.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_0[1-3].bin`). Phase 29 does NOT delete them; the post-fix runs land in `.planning/v1.6/post-fix-runs/W27C512-leonardo-<new-timestamp>/run_0[1-5].bin` (note: `post-fix-runs/` subdir per the Phase 26 D-04 `--output-dir` flexibility). Phase 30 archives both directories under `.planning/milestones/v1.6-phases/` as part of milestone close.
- **The 5-line Python cross-check from Phase 27** (EVIDENCE.md lines 99-108) is re-runnable against the post-fix binaries to confirm the divergence count drops from 1349 to 0. Phase 29 Wave B's verifier can optionally run this as a sanity check (expected output: `Total divergences: 0; single-bit-flip fraction: 0.0%`).
- **Two empirically-confirmed `_NOP()` count = 2 settling delay** (Phase 28 commit `4f205e58`). If Phase 29 still shows residual single-bit flips on Leonardo, operator can attempt N=3 or N=4 `_NOP()`s as a Phase 27 re-open experiment per Phase 28 Claude's Discretion #1. Phase 29 itself does NOT modify the count.
- **The `urclock` bootloader is the right `programmer_id`** for the misidentified board (per `[[project_bench_findings_v15]]`). Phase 29 D-01 reflash uses the standard `firestarter fw -i --pre --force` path which already picks `urclock` for the uno328pb-reporting handshake (v1.5 Phase 23 host CLI work). If the reflash fails with a programmer-id mismatch, the board is likely a Plain Uno (Case B) and `firestarter fw -i --pre --force --board uno` will succeed.
- **Operator's stable-installed app vs locally-installed app:** Phase 29 Wave B requires the LOCALLY-installed app from `firestarter_app/v1.6-read-bug` checkout via `pip install -e .` (because the `dev consistency-check` diagnostic is only on that branch + no PyPI pre-release exists yet — Phase 30 creates that). The locally-installed app coexists with whatever stable-or-prior install the operator has; `pip install -e .` overrides for the active venv. Phase 30's eventual PyPI pre-release publish + `firestarter fw -i --pre --force` re-install is what restores users to a publishable v1.6 state.

</specifics>

<deferred>
## Deferred Ideas

- **Cutting a one-off `3.0.0-rcaN` tag** for Phase 29 (mirror of Phase 27 RCA tag option) — explicitly NOT taken per D-02; LOCAL sideload is sufficient for Phase 29's bench evidence and avoids public-channel pollution. If Phase 29 Wave B FAILs and Phase 27 re-opens with an instrumented build, the RCA tag becomes available again at that point. Phase 30's `beta` merge creates the only public artifact for v1.6.
- **Cutting the public pre-release in Phase 29** (the original D-02 design before this correction) — explicitly NOT taken. Phase 30 owns the merge per ROADMAP Phase 30 SC#5. The local-sideload path keeps Phase 29 evidence-only.
- **Adding `--size N` flag to `dev consistency-check`** to fold VERIFY-03 into the same diagnostic — Phase 26 D-06 explicitly deferred. Could land post-v1.6 if the 1KB-only verification is repeatedly needed.
- **Auto-orchestrating cross-board verification** (`--all-boards` flag enumerating `/dev/tty*` and rotating chip) — Phase 26 D-07 / D-09 deferred; operator muscle memory wins.
- **Bench-validating the Uno's `df5fb44` 2026-05-13 fix** by adding a parallel Unity test mirroring Phase 28's test_data_input — Phase 28 `<deferred>` carries this; post-v1.6 quality-debt.
- **Reverting Leonardo `DATA_BUFFER_SIZE` from 512 → 1024** in `firestarter/platformio.ini:64-65` (the A/B annotation) — Phase 28 D-05 + Phase 27 H6 refuted buffer size as discriminator. Phase 29 keeps 512 (since both Phase 26 baseline and Phase 28 fix landed at 512). If Phase 29 PASS at 512, the 1024 revert is a Phase 30 polish OR post-v1.6 question; not a verification axis.
- **Documentation drift correction** (5 "Leonardo 1024-B" locations from Phase 27 drift table) — Phase 30 paperwork.
- **`firestarter info <chip>` crash** (TypeError at `ic_layout.py:167`) — Phase 26 EVIDENCE.md §"Scope changes" item 3; out of v1.6 scope.
- **`0xda01` W27C512 chip-ID alias gap** — Phase 26 §"Scope changes" item 2; out of v1.6 scope. Phase 29 operator notes the variant in the hardware metadata snapshot but does NOT fix the DB.
- **Cosmetic `Board: unknown-board` in `dev consistency-check` stdout** (Phase 26 REVIEW WR-02) — Phase 30 paperwork or post-v1.6.
- **`--keep-files=False` cleanup for the Phase 29 post-fix run binaries** — default keep (Phase 26 D-04); archives go with the rest of `.planning/v1.6/` under `.planning/milestones/v1.6-phases/` at Phase 30 close.
- **`dev consistency-check` FAIL-without-divergence edge case** (Phase 26 REVIEW WR-01) — Phase 30 paperwork or post-v1.6.

### Reviewed Todos (not folded)

- **`large-read-data-jitter-uno328pb.md`** — the v1.6 milestone bug itself. Phase 29 PRODUCES the post-fix evidence that demonstrates it's resolved; Phase 30 DOC-01 owns the `pending/ → resolved/` move + the root-cause summary cross-reference (per Phase 28 deferred list). Not folded into Phase 29 because the todo's state transition is paperwork, not verification.
- **`w27c512-eeprom-misclassification.md`** — operationally implicated in Phase 29 VERIFY-04 (the `firestarter write -e SST27SF512` path may fail with the v1.5-documented "ERROR: Not supported" workaround). Phase 29 D-06 uses the small-window-write workaround per v1.5 BENCH-02 precedent. The underlying DB classification fix belongs in its own milestone (operator-tagged "asap" but separate bug class — DB routing, not transport). Not folded.
- **`avrdude-mcu-detection-fallback.md`** — unrelated v1.5 carryover (low priority); host CLI enhancement, not bench verification. Not folded.

</deferred>

---

*Phase: 29-multi-board-bench-verification*
*Context gathered: 2026-05-22*

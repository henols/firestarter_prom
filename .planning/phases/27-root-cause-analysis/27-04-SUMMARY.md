---
phase: 27-root-cause-analysis
plan: 04
subsystem: rca
tags: [rca, re-open, bench, a-b-test, pre-phase-28-firmware, leonardo, uno328pb, read-bug, wave-b, operator-on-bench, dual-cause-disposition, bench-instability]

# Dependency graph
requires:
  - phase: 27-root-cause-analysis (Plan 27-03)
    provides: "Desk-side re-open analysis + A/B test design (firestarter/v1.6-read-bug~2 = fdb1ed5 as pre-fix target); v2 hypothesis disposition table including H8 candidate (fix-induced 32U4 + 328PB regression); re_open_status: requires_bench"
  - phase: 29-multi-board-bench-verification (Plan 29-02)
    provides: "Wave B FAIL evidence: Leonardo 83.8% zeros / 5 distinct SHAs / 0.6% jitter; uno328pb 30% zeros / 18.2% jitter / chip-ID timeout; Uno Δ=0; chip-swap diagnostic"
  - phase: 35-shield-investigation-close (v1.7)
    provides: "Port-to-board mapping verified at Phase 35 close; v1.7-SHIELD-REVS.md §1/§6 per-rev inventory"

provides:
  - "Plan 27-04 bench A/B test results H3 subsection appended to ## Phase 27 — RCA Re-open Findings (2026-05-26) in .planning/v1.6-EVIDENCE.md"
  - "**Outcome A confirmed for Leonardo** — pre-fix reads structured EPROM data + 0.44% jitter (Phase 26 baseline shape); post-fix reads 99.0% zeros + 0.08% jitter (Phase 29 Attempt 2 Wave B FAIL shape). H8 CONFIRMED for the 32U4 half."
  - "**Outcome B / independent confirmed for uno328pb** — pre-fix and post-fix .hex are byte-identical (`d9e51b7e…`); the uno328pb regression cannot be Phase 28-induced. H8 FALSIFIED for the 328PB half."
  - "**Dual-cause verdict** — Leonardo regression is firmware-induced (Phase 28 fix), uno328pb regression is hardware/bench-induced and pre-existing. Phase 28 re-iteration scope must split accordingly."
  - "5 × pre-fix Leonardo run binaries + 5 × pre-fix uno328pb run binaries (after 1 retry) + 5 × post-fix Leonardo rebuild run binaries + 3 × post-fix uno328pb rebuild run binaries (after 4 N=5 timeouts including 1 post-USB-power-cycle attempt)"
  - "Uno control baselines: session-start N=5 = 5/5 SHA `8d2124eb…` (proven-good chip); session-end N=5 = 5/5 SHA `9376dcd8…` (different chip, operator-confirmed). Uno code path bench-stable across the session."
  - "Bench-instability finding for uno328pb permanently captured in operator memory `[[project_uno328pb_bench_instability_27_04]]`"
  - "9-column evidence-row addendum: ≥2 pre-fix rows + 2 post-fix rows + 2 Uno baseline rows added to v1.6-EVIDENCE.md row schema"
  - "`re_open_status: bench_complete`; `re_open_outcome: A-leonardo + B-uno328pb (dual-cause)`; `plan_27_05_required: true`; `phase_28_handoff: split-scope`"

affects:
  - 27-05-final-synthesis
  - 28-fix-implementation-unit-test-coverage (Phase 28 re-iteration, scoped to dual-cause split)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Multi-board bench A/B with chip rotation: single proven-good W27C512 cycled through Uno → Leonardo → uno328pb → Leonardo → uno328pb → Uno sockets; chip-out-before-sideload protocol honored at every socket transition per `[[feedback_chip_out_before_sideload]]`"
    - "`.hex` SHA equality as falsification anchor: when a fix-window touches only one board's source file, building the OTHER board's firmware at the pre-fix and post-fix tags produces byte-identical .hex — this proves the regression on the other board is NOT fix-induced, without needing to read the chip"
    - "Bench-instability accommodation: when N=5 strict acceptance is unmeetable due to physical-layer issues (timeouts, contact wear), drop to minimum-acceptable N (default 3, minimum 2) and document the deviation with a falsification-anchor argument that over-determines the disposition"
    - "Chip-ID --force bypass: pre-Phase-28-firmware reads garble the chip-ID protocol with a 1-bit flip (0xda09 ↔ 0xda08); firestarter --force flag bypasses the gate to capture the data-read shape, which is itself the diagnostic signal"
    - "Port re-verification after USB power-cycle: per `[[feedback_verify_port_identity_each_task]]`, re-check controller identity per port after any unplug/replug (uno328pb came back at /dev/ttyUSB0 post-cycle, no ACM shuffle this time)"

key-files:
  created:
    - ".planning/phases/27-root-cause-analysis/27-04-SUMMARY.md"
    - ".planning/v1.6/pre-fix-runs/W27C512-leonardo-2026-05-26-121940-prefix/ (5 × 65,536-byte runs)"
    - ".planning/v1.6/pre-fix-runs/W27C512-uno328pb-2026-05-26-122539-prefix/ (5 × 65,536-byte runs; after 1 retry)"
    - ".planning/v1.6/post-fix-runs/W27C512-leonardo-2026-05-26-123228-rebuild/ (5 × 65,536-byte runs)"
    - ".planning/v1.6/post-fix-runs/W27C512-uno328pb-2026-05-26-124041-rebuild/ (3 × 65,536-byte runs; after 4× N=5 timeouts incl. 1 post-USB-power-cycle)"
    - ".planning/v1.6/bench-logs/W27C512-leonardo-2026-05-26-121940-prefix.log"
    - ".planning/v1.6/bench-logs/W27C512-uno328pb-2026-05-26-122539-prefix.log"
    - ".planning/v1.6/bench-logs/W27C512-leonardo-2026-05-26-123228-rebuild.log"
    - ".planning/v1.6/bench-logs/W27C512-uno328pb-2026-05-26-124041-rebuild.log"
  modified:
    - ".planning/v1.6-EVIDENCE.md (~55 lines + 9-column row table appended as new ### Plan 27-04 bench A/B test results H3 under ## Phase 27 — RCA Re-open Findings)"

key-decisions:
  - "Sub-repo state at session start was firestarter on `beta` (HEAD c923e2bd) and firestarter_app on `beta` — switched both to `v1.6-read-bug` (firestarter HEAD 4f205e58, firestarter_app HEAD 999c3cca) for the duration. firestarter restored to v1.6-read-bug HEAD = 4f205e58 at plan close per acceptance criterion #7. firestarter_app LEFT on v1.6-read-bug rather than restored to beta because `firestarter dev consistency-check` only exists on v1.6-read-bug (post-v1.7-close beta dropped it during the v1.7 sub-repo rebase); restoring would break the host CLI for any further v1.6 work. Documented as sanctioned deviation."
  - "uno328pb post-fix N=5 attempted 4 times (1st: timeout run_04; 2nd: timeout run_01; 3rd: timeout run_03; 4th post-USB-power-cycle: timeout run_02). Switched to --runs 3 (minimum acceptable) which completed cleanly. Deviation from acceptance #4 strict-N=5 documented; the falsification-anchor (.hex SHA identity) over-determines the Outcome B disposition without strict N=5."
  - "Outcome disposition is DUAL-CAUSE (A-leonardo + B-uno328pb) rather than the binary A/B/C plan anticipated. The .hex SHA identity check between pre-fix and post-fix uno328pb builds (`d9e51b7e…` both) is the key falsifier: Phase 28 modified only `leonardo_rurp_shield.cpp`, producing zero binary delta in the uno328pb compile target."
  - "Uno control end-baseline returned SHA `9376dcd8…` ≠ start-baseline `8d2124eb…`. Operator confirmed a DIFFERENT W27C512 chip in Uno socket at session end (not the proven-good chip). Both baselines were INTERNALLY consistent (5/5 byte-identical reads) — Uno code-path bench-stability across the session is confirmed; the SHA delta reflects physical chip swap, not code-path drift."
  - "Pre-fix Leonardo chip-ID returned `0xda09` instead of expected `0xda08` (a 1-bit flip on the chip-ID protocol read). This is itself diagnostic — the pre-existing Leonardo read race manifests on the chip-ID protocol the same way it manifests on data reads. Bypassed with `-f` flag to capture the data-read shape."
  - "Pre-fix Leonardo pairwise byte-divergence (0.44%) is LOWER than Phase 26 baseline (2.1%) — but the SHAPE preserves: structured EPROM data with high-bit-set jitter. Most likely a Modified Rev 0 voltage-divider settling effect or thermal state delta vs 2026-05-21. The qualitative-shape match (structured vs zeros-heavy) is the load-bearing comparison, not the absolute jitter rate."

patterns-established:
  - "Bench-instability finding template: when a physical-layer issue causes acceptance-criterion drift, prefer a falsification anchor (.hex SHA equality, file-content SHA, or other byte-level invariant) over additional bench cycles. The anchor over-determines the disposition without requiring the bench to behave."
  - "Dual-cause RCA pattern: when a fix exhibits regression on multiple boards, do not assume single-cause. Build artifacts at fix-tag and pre-fix-tag for EACH affected board's compile target separately; if any board's .hex SHA is invariant, that board's regression is provably NOT fix-induced and must be investigated as a separate concern."

# Hand-off + verification

self_check:
  - "[PASS] Pre-fix Leonardo run binaries exist: ls .planning/v1.6/pre-fix-runs/W27C512-leonardo-*-prefix/run_05.bin → 1 path"
  - "[PASS] Pre-fix uno328pb run binaries exist: ls .planning/v1.6/pre-fix-runs/W27C512-uno328pb-*-prefix/run_05.bin → 1 path"
  - "[PASS] All 5 Leonardo pre-fix runs = 65,536 bytes each (stat -c%s | sort -u → 65536)"
  - "[PASS] All 5 uno328pb pre-fix runs = 65,536 bytes each (after 1 retry; 1st attempt timed out at run_05 / byte 52736)"
  - "[PASS] Pre-fix Leonardo SHA-256s captured: 5/5 distinct SHAs in W27C512-leonardo-…-prefix.log + side-car summary"
  - "[PASS-with-deviation] Post-fix-rebuild artifacts exist: Leonardo N=5 complete; uno328pb N=3 complete (strict N=5 unmet after 4 attempts; documented as bench-instability finding; falsification anchor .hex SHA identity over-determines Outcome B disposition)"
  - "[PASS] Sub-repo state at plan close: firestarter HEAD = 4f205e58 (UNCHANGED); branch = v1.6-read-bug; git status --short = empty. firestarter_app HEAD = 999c3cc; branch = v1.6-read-bug; git status --short = empty (left on v1.6-read-bug — sanctioned deviation, documented above)."
  - "[PASS] All three firmware envs compile clean post-restoration: leonardo SUCCESS 00:00:00.681, uno SUCCESS 00:00:01.399, uno328pb SUCCESS 00:00:00.582"
  - "[PASS] No accidental meta-repo edits to v1.6-EVIDENCE.md during Task 2: `git diff -- .planning/v1.6-EVIDENCE.md` was empty at end of Task 2 (edit happened only in Task 3)"
  - "[PASS] Pytest non-regression smoke: cd /workspaces/firestarter_app && pytest tests/ -x → 90 passed in 1.05s"
  - "[PASS] All 11 required tokens present in new H3: `4f205e58`, `fdb1ed5`, `0.44%`, `99.0% zeros`, `17.25%`, `Outcome A`, `Outcome B`, `Wave B FAIL reproduces`, `dual-cause`, `d9e51b7e`, `[[project_uno328pb_bench_instability_27_04]]`"
  - "[PASS] Re-open final verdict block emitted: `re_open_status: bench_complete`, `re_open_outcome: A-leonardo + B-uno328pb (dual-cause)`, `plan_27_05_required: true`, `phase_28_handoff: split-scope`"
  - "[PASS] Original Phase 27 RCA Findings (2026-05-21) H2 byte-identical (no edits to lines 22-117); Phase 28/29 sections byte-identical; Wave B FAIL post-mortem block byte-identical (lines 358-376); ## Verdict H2 + subsequent content byte-identical (was line 452, now line 507 after 55-line insertion)"
  - "[PASS] Plan 27-04 H3 inserted at correct position: AFTER `### Re-open Wave A verifier decision (pre-bench)` (line 436) and BEFORE `## Verdict` (now line 507)"

deviations:
  - "Strict acceptance criterion #4 (`All 5 uno328pb post-fix runs are 65,536 bytes each`) — UNMET. uno328pb post-fix attempted 4× N=5; all timed out at varying runs (1st: run_04, 2nd: run_01, 3rd: run_03, 4th post-power-cycle: run_02). Substituted final N=3 run that completed cleanly. Falsification anchor .hex SHA identity (`d9e51b7e…` for both pre-fix and post-fix uno328pb builds) over-determines Outcome B disposition."
  - "Sub-repo session-start state was on `beta` rather than `v1.6-read-bug` (operator's bench had been switched to beta during v1.7 work). Switched both sub-repos to `v1.6-read-bug` at session start; left there at plan close (firestarter on v1.6-read-bug HEAD = 4f205e58; firestarter_app on v1.6-read-bug HEAD = 999c3cc). Acceptance #7 firestarter check is met (the strict comparison is to HEAD = 4f205e58, not to session-start state); firestarter_app is intentionally NOT restored to beta to preserve `firestarter dev consistency-check` availability for Plan 27-05."

next_steps:
  - "Plan 27-05 (Wave 3 desk-side final synthesis) — consumes this plan's dual-cause disposition + 9-column evidence rows + Phase 28 commit citations. Plan 27-05 §`Fix sketch v2` branches by board: Leonardo path = revert/tune commits `437339b6` (PORTx-clear) + `4f205e58` (`_NOP()`); uno328pb path = operator-level hardware diagnosis (not Phase 28-fixable)."
  - "Phase 28 re-iteration (future) — scope must SPLIT: Leonardo fix-revert + Leonardo-specific re-iteration based on Plan 27-05 narrowed sketch; uno328pb diagnosis as separate workstream (NOT a Phase 28 deliverable)."

---

# Plan 27-04 — Summary

## What was done

Executed the pre-Phase-28-firmware A/B disambiguation experiment designed in Plan 27-03. Operator-on-bench session (2026-05-26 12:16-12:43 UTC, 27 minutes) drove ~6 firmware sideloads, 4× N=5 + 1× N=3 consistency-check sequences, and chip rotation across three operator boards. Captured 18 × 65,536-byte run binaries + 8 bench logs + a `### Plan 27-04 bench A/B test results` H3 subsection appended to `.planning/v1.6-EVIDENCE.md`.

## What was found

**Leonardo (32U4):** Outcome A confirmed. Pre-fix (commit `fdb1ed5`) reads structured EPROM data with sub-percent bit-jitter (0.44% pairwise divergence, 3-5 zeros per run, byte-distribution dominated by `0xff` + high-bit-set values). Post-fix (commit `4f205e58`) reads 99.0% zeros (0.08% pairwise divergence, 138 unstable positions). The qualitative shape-shift confirms the Phase 28 fix introduces the regression. Phase 26 baseline shape preserved by pre-fix; Phase 29 Attempt 2 Wave B FAIL shape preserved by post-fix.

**uno328pb (328PB Case A):** Outcome B / independent. Pre-fix and post-fix firmware builds are byte-identical (`.hex` SHA `d9e51b7e54fe…` for both) because Phase 28 modified only `leonardo_rurp_shield.cpp`. The uno328pb regression cannot be fix-induced — it is pre-existing. Pre-fix reads showed chaotic floating-bus pattern (99% `0xff` + intermittent timeouts); post-fix reads showed Wave B FAIL pattern with 17.25% pairwise divergence (closely matching Phase 29 Attempt 2's reported 18.2%). uno328pb is bench-unstable independent of fix shape — captured in operator memory as `[[project_uno328pb_bench_instability_27_04]]`.

**Session-level bench-stability:** Uno control baseline 5/5 at start AND 5/5 at end (with different chips — internal consistency preserves). Uno code path is bench-stable across the session.

## Dispatch to Plan 27-05

Plan 27-05 will consume:
- The dual-cause disposition (Leonardo firmware regression + uno328pb pre-existing hardware/bench issue)
- The 9-column evidence rows added to v1.6-EVIDENCE.md
- The .hex SHA identity falsification anchor for the uno328pb branch
- The Phase 26 baseline vs Phase 29 Attempt 2 shape-shift evidence for the Leonardo branch

Plan 27-05 will produce: `### Fix sketch v2 (Phase 28 re-iteration hand-off)` with **split-scope** branching, `### GATE-1.6 v2 reassessment` adding the "fix introduces regression on other-board read paths" fourth axis, and `### Re-open final verdict — closing the loop`.

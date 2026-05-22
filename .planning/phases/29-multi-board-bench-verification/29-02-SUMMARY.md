---
phase: 29-multi-board-bench-verification
plan: 02
subsystem: testing
tags: [bench-verification, operator-on-bench, acceptance-gate, fail, d-07, milestone-reopens, phase-28-regression, chip-swap-diagnostic, w27c512]

requires:
  - phase: 28-fix-implementation-unit-test-coverage
    provides: locally-built firestarter_{uno,leonardo,uno328pb}.hex with Phase 28 read-bug fix candidates (commits 437339b6 PORTx-clear + 4f205e58 `_NOP()` settling)
  - phase: 29-multi-board-bench-verification (Wave A, plan 29-01)
    provides: built + SHA-256-recorded .hex artifacts; host CLI installed at 3.0.0b4; EVIDENCE.md + v1.5-BENCH-RESULTS.md SCAFFOLD sections; pre-flight checklist
  - phase: 29-multi-board-bench-verification (Wave B Attempt 1, archived in 29-02-SUMMARY-attempt1-2026-05-22-INCONCLUSIVE.md)
    provides: bench-instability diagnostic learnings (port-shuffle, chip-out-before-sideload safety, shield-specific VPP calibration, host-CLI methodology defects); Uno regression PASS established for the first time
provides:
  - **D-07 FAIL milestone-reopens verdict** for v1.6 based on chip-swap-diagnostic-strengthened evidence: Phase 28 firmware fails on Leonardo + uno328pb read paths; Uno code path unaffected
  - Chip-swap diagnostic result: proven-good chip from Uno reads garbage on Leonardo (83.8% zeros + 5 distinct SHAs across N=5) → eliminates chip-state as the variable, isolates the regression to Leonardo board / shield / firmware path
  - Strong candidate cause for Phase 27 RCA re-open: Phase 28 fix commits `437339b6` + `4f205e58` introduced a Leonardo-specific read-path regression
  - First-priority RCA experiment recommended: pre-Phase-28-firmware A/B test (build `firestarter/v1.6-read-bug~2`, sideload to Leonardo, re-probe)
  - STATE.md `status: blocked` + Open Blockers entry naming Leonardo + uno328pb FAIL
  - 12+ committed run-binary archives across Attempts 1 + 2 (preserved for Phase 27 RCA forensics)
  - Three feedback memories from the Attempt 1 + Attempt 2 sessions ([[feedback_chip_out_before_sideload]], [[feedback_verify_port_identity_each_task]]) + memory update [[project_uno328pb_correction]]
affects: 27-root-cause-analysis (re-open candidate), 28-fix-implementation-unit-test-coverage (fix-iteration target), 30-documentation-milestone-close (BLOCKED until re-validated)

tech-stack:
  added: []
  patterns:
    - "Chip-swap diagnostic: when a board's read path is suspect, swap chips with a known-good board and probe both — disambiguates chip-state from board/shield/firmware path in 5 minutes"
    - "Zero-byte-count metric (`od -An -tx1 -v <file> | tr -s ' \\n' '\\n' | grep -c '^00$'`) for hexdump-formatted reads — surfaces silent partial-read failures that pairwise-SHA diffs alone miss"
    - "Surviving-byte-offset analysis as a hardware/timing fault classifier: bytes that survive at consistent offsets across multiple runs while neighbors zero-out suggest intermittent timing race, not stuck-bit fault"

key-files:
  created:
    - .planning/v1.6/post-fix-runs/W27C512-uno-2026-05-22-100312/run_{01..05}.bin (Attempt 2 Uno baseline, 5 × 65536 B, SHA `8d2124eb…`)
    - .planning/v1.6/post-fix-runs/W27C512-uno-2026-05-22-101119-swap/run_{01..05}.bin (Attempt 2 Uno with ex-Leonardo chip, SHA `19710f6e…`)
    - .planning/v1.6/post-fix-runs/W27C512-leonardo-2026-05-22-101119-swap/run_{01..05}.bin (Attempt 2 Leonardo with proven-good chip — 5 distinct SHAs, 83.8% zeros)
    - .planning/v1.6/post-fix-runs/W27C512-uno328pb-2026-05-22-101552/run_{01..05}.bin (Attempt 2 uno328pb original chip — 5 distinct SHAs, 18.2% jitter)
    - .planning/v1.6/bench-logs/W27C512-uno-2026-05-22-100312.log
    - .planning/v1.6/bench-logs/W27C512-uno-2026-05-22-101119-swap.log
    - .planning/v1.6/bench-logs/W27C512-leonardo-2026-05-22-101119-swap.log
    - .planning/v1.6/bench-logs/W27C512-uno328pb-2026-05-22-101552.log
    - .planning/phases/29-multi-board-bench-verification/29-02-SUMMARY-attempt1-2026-05-22-INCONCLUSIVE.md (archive of Attempt 1 INCONCLUSIVE narrative, renamed in commit 29f6abd)
  modified:
    - .planning/v1.6-EVIDENCE.md (added Phase 29 Attempt 2 main section + Hardware metadata + VERIFY tables + Verdict block (4× FAIL) + Hand-off block (Phase 30 BLOCKED) + Wave B FAIL post-mortem)
    - .planning/STATE.md (`status: executing` → `status: blocked`; Current Position updated; Open Blockers entry added naming Leonardo + uno328pb FAIL with full diagnostic)

key-decisions:
  - "D-07 FAIL milestone-reopens triggered (not INCONCLUSIVE). Attempt 2 strengthened the evidence vs Attempt 1: chip-swap diagnostic eliminated chip-state as the variable (proven-good chip from Uno reads garbage on Leonardo), bench-restoration to Modified Rev 0 + voltage-divider mod ruled out the shield-swap as the cause, and the failure mode is qualitatively different from Phase 26 baseline on the same shield + chip-class combo (~83.8% zeros vs Phase 26's 2.1% bit-jitter on structured data). Together these strongly suggest Phase 28 firmware introduced a Leonardo + uno328pb read-path regression."
  - "Skip Task 5 (BENCH-02 cycle on Leonardo + SST27SF512): write→read→cmp on a broken read path adds no diagnostic value beyond what VERIFY-02 already shows. v1.5-BENCH-RESULTS.md post-hoc closure row remains scaffolded; deferred to future post-fix Phase 29 re-run."
  - "STATE.md `status: blocked` (not `executing`): per D-07 explicit language 'milestone re-opens'; Phase 30 BLOCKED. The 'blocked' status signals to /gsd-progress and downstream tooling that v1.6 is in fix-iteration territory, not in a 'partial progress can ship anyway' state."
  - "Phase 30 has zero sub-repo state mutations: no merges, no pushes, no tags. Verified `cd /workspaces/firestarter && git log -3 --oneline` + `cd /workspaces/firestarter_app && git log -3 --oneline` unchanged from session start. Plan boundaries honored."
  - "Recommend Phase 27 RCA re-open. First experiment: pre-Phase-28-firmware A/B test. The Leonardo qualitative-shape change between Phase 26 (structured data + 2.1% jitter) and Phase 29 Attempt 2 (83.8% zeros + 0.6% jitter on the ~16% surviving bytes) makes Phase 28 fix the strong candidate cause; the A/B test would confirm or falsify."

patterns-established:
  - "Pattern (memory) — chip-out before sideload, chip-in before reads: [[feedback_chip_out_before_sideload]]"
  - "Pattern (memory) — re-query `firestarter -p <port> fw` per task to detect ACM port shuffle: [[feedback_verify_port_identity_each_task]]"
  - "Pattern (bench-session) — chip-swap diagnostic is the fastest way to disambiguate 'chip damaged' from 'board path broken': swap chips between a known-good seat and a suspect seat; probe both; compare SHAs. Faster than re-seating multiple times."
  - "Pattern (data-shape) — for hexdump-formatted read output, hash only `^[0-9a-f]{8}:` data lines; the elapsed-time footer `Read complete (Xs)` varies between reads and corrupts raw-file SHA-256 equality."
  - "Pattern (data-shape) — zero-byte ratio is a fast partial-read-failure detector that pure SHA-diff misses. Healthy random-data EPROM reads at ~0.4% zeros; broken-bus reads cluster at 30-99% zeros depending on failure mode."

requirements-completed: []  # VERIFY-01/02/03/04 all FAIL or NOT ATTEMPTED. Milestone re-opens; no requirements close.

duration: 75min  # Attempt 2 session only (excluding Attempt 1's 90min)
completed: 2026-05-22
---

# Phase 29 Plan 02: Multi-Board Bench Verification (Attempt 2) — FAIL (D-07 milestone-reopens)

**The Phase 28 fix verdict on THE acceptance gate is FAIL: Leonardo reads 83.8% zeros across N=5 (5 distinct SHAs) with a proven-good chip swapped in from the always-PASS Uno seat; uno328pb (real ATmega328PB Case A) reads 5 distinct SHAs with 18.2% byte-jitter and chip-ID timeout. Uno code path holds (Δ=0 regression check triple-replicated). Chip-swap diagnostic eliminates chip-state as the variable, isolating the regression to the Leonardo + uno328pb firmware-read path. v1.6 milestone re-opens; Phase 30 BLOCKED; recommend Phase 27 RCA re-open with pre-Phase-28-firmware A/B test as first experiment.**

## Performance

- **Duration:** ~75 min (Attempt 2 operator-on-bench session; total session including Attempt 1 ~165 min)
- **Started:** 2026-05-22T10:00:00Z (operator confirmed bench restoration: Modified Rev 0 back on Leonardo, chips re-verified on Uno first)
- **Completed:** 2026-05-22T11:15:00Z (D-07 FAIL close)
- **Tasks attempted:** Tasks 1-4 + 6-8 (Task 5 BENCH-02 cycle skipped — Leonardo read path broken makes write→read→cmp diagnostically uninformative)
- **Files modified:** 2 (.planning/v1.6-EVIDENCE.md, .planning/STATE.md) + 1 new (this SUMMARY) + 1 renamed (attempt-1 SUMMARY) + 20 new evidence files in `.planning/v1.6/{post-fix-runs,bench-logs}/`

## Accomplishments

- **Strong evidence-base for D-07 FAIL milestone-reopens.** Attempt 1 captured Leonardo as bench-confounded INCONCLUSIVE; Attempt 2's chip-swap diagnostic (proven-good Uno chip reads garbage on Leonardo) eliminates chip-state as the cause variable. Combined with bench-restoration to the exact same setup that produced Phase 26 baseline (Modified Rev 0 + voltage-divider mod + W27C512 chip class), the failure-mode delta between Phase 26 (structured data + 2.1% jitter) and Phase 29 (83.8% zeros + 0.6% jitter) is strongly suggestive of Phase 28 firmware introducing the regression.
- **Triple-replicated Uno regression PASS:** SHA `8d2124eb…` × 5 in Attempt 1, SHA `8d2124eb…` × 5 in Attempt 2 baseline, SHA `19710f6e…` × 5 in Attempt 2 post-chip-swap. Phase 28 fix held cleanly on the Uno code path (Δ=0 hex confirmed empirically).
- **uno328pb Case A multi-board failure data:** 5 distinct SHAs / N=5 / 18.2% pairwise jitter on the real ATmega328PB silicon (Case A handshake confirmed across both attempts). Failure mode shape differs from Leonardo (~30% zeros vs ~84% zeros; 18.2% jitter vs 0.6% jitter). Same Phase 28 firmware, different silicon, both broken — narrows Phase 27 RCA target to a code path shared by 32U4 + 328PB but not used by Plain Uno.
- **Phase 27 RCA candidates surfaced with empirical priority:**
  1. Pre-Phase-28-firmware A/B test (first experiment — confirms or falsifies the regression hypothesis)
  2. Phase 28 Discretion #1 (`_NOP()` count adjustment in `rurp_read_data_buffer`)
  3. Investigate why uno328pb chip-ID protocol times out (separate code path from data reads)
- **Chip-swap diagnostic pattern documented** for future bench sessions (faster + more conclusive than re-seating).

## Task Commits

Each task committed atomically on `main` in the meta-repo (no sub-repo mutations per plan boundaries):

1. **Attempt-1 archive** — `29f6abd` (docs: rename old SUMMARY to attempt1 archive)
2. **Task 1 + Task 2 + Task 3 + Task 4 (Attempt 2 evidence + EVIDENCE.md updates)** — committed in the session-close commit below
3. **Task 6 + Task 8 (Verdict block + D-07 STATE.md update + FAIL post-mortem)** — committed in the session-close commit below
4. **Task 7 (this SUMMARY)** — committed in the session-close commit below

Sub-repo verification:
- `cd /workspaces/firestarter && git log -3 --oneline` — unchanged from session start
- `cd /workspaces/firestarter_app && git log -3 --oneline` — unchanged from session start
- `cd /workspaces/firestarter && git tag --list '3.0.0b5'` — empty
- `cd /workspaces/firestarter_app && git tag --list '3.0.0b5'` — empty

## Files Created/Modified

- `.planning/v1.6-EVIDENCE.md` — added "## Phase 29 Attempt 2" main section under the existing "Attempt 1 (INCONCLUSIVE — archived)" section; populated Attempt 2 Hardware metadata snapshot, VERIFY-01/02/03 tables with FAIL data, VERIFY-04 NOT ATTEMPTED, Verdict block 4× FAIL, Hand-off block "Phase 30 BLOCKED", and full Wave B FAIL post-mortem (D-07).
- `.planning/STATE.md` — frontmatter `status: executing → blocked`; Current Position updated with FAIL+D-07 narrative; Open Blockers entry added naming Leonardo + uno328pb FAIL with chip-swap-diagnostic-strengthened evidence + Phase 27 RCA recommendation.
- `.planning/phases/29-multi-board-bench-verification/29-02-SUMMARY.md` (this file) — FAIL-outcome SUMMARY.
- `.planning/phases/29-multi-board-bench-verification/29-02-SUMMARY-attempt1-2026-05-22-INCONCLUSIVE.md` — archived from yesterday's INCONCLUSIVE close (commit 29f6abd).
- Run binaries + tee'd consistency-check logs for Attempt 2 in `.planning/v1.6/post-fix-runs/` and `.planning/v1.6/bench-logs/` (4 new directories + 4 new logs).

## Decisions Made

1. **D-07 FAIL milestone-reopens (NOT INCONCLUSIVE).** Attempt 2's chip-swap diagnostic is decisive: when the proven-good chip (which just read SHA `8d2124eb…` cleanly × 5 on Uno) is placed in Leonardo's socket, Leonardo reads 83.8% zeros across 5 distinct SHAs. Chip-state is eliminated as the variable. Combined with bench-restoration to the exact Phase 26 baseline setup (Modified Rev 0 + voltage-divider mod), the failure-mode delta from Phase 26 (structured data + 2.1% jitter on this same hardware) to Phase 29 (83.8% zeros + 0.6% jitter on the surviving ~16%) is strongly suggestive of Phase 28 firmware introducing the regression. The remaining ambiguity (firmware regression vs. hardware degradation between bench sessions) is resolvable by a future Phase 27 RCA pre-Phase-28-firmware A/B test; not within Phase 29's plan scope but recorded as the first-priority next experiment.

2. **STATE.md `status: blocked` (NOT `executing`).** D-07's explicit language is "milestone re-opens"; the `blocked` status signals to /gsd-progress and the rest of the GSD toolchain that v1.6 is in fix-iteration territory and cannot ship from this state. Phase 30 will refuse to start with `status: blocked` upstream.

3. **Skipped Task 5 (BENCH-02 cycle on Leonardo + SST27SF512).** Write→read→cmp on a broken read path: either the cmp fails at the read step (~84% zeros on the read-back → cmp will mismatch) or, worse, the write step succeeds while the read step fails and we get a misleading "write OK, read bad" diagnostic that doesn't reflect actual write-path health. The plan's GATE-1.6 non-regression intent ("Phase 28 fix must not perturb write timing or VPP regulator engagement") is better tested AFTER the read path is fixed.

4. **uno328pb chip not swapped in the diagnostic.** Operator confirmed chip-swap between Uno ↔ Leonardo only; uno328pb kept its original chip. Doesn't change the Phase 29 verdict (uno328pb is FAIL either way), but leaves open the question "is the uno328pb FAIL also chip-independent?" for the next bench session.

5. **Plan deviations honored as in Attempt 1.** No sub-repo source-code edits, no submodule HEAD changes, no merges, no pushes, no tags, no `update_version.py` invocation. All bench evidence + EVIDENCE.md + STATE.md + SUMMARY.md commits land only in the meta-repo on `main`.

## Deviations from Plan

### Plan execution-order deviations (operator-confirmed)

**1. [Plan order] Attempt 2 added a chip-swap diagnostic between Task 3 and Task 4.**
- **Found during:** Task 3 (Leonardo first probe) — chip-ID returned `0x00` even with restored Modified Rev 0 shield, matching Attempt 1's failure mode despite the bench restoration. Suggested either chip-or-board fault that re-seating alone could not disambiguate.
- **Fix:** Operator agreed to chip-swap diagnostic: pull chip from Uno (just read SHA `8d2124eb…` × 5 cleanly), pull chip from Leonardo (reads `0x00`), swap them in their sockets, re-probe both. Result: Uno still reads SHA `19710f6e…` × 5 (new chip is healthy), Leonardo still reads 5 distinct SHAs with 83.8% zeros (proven-good chip reads garbage). Definitive: chip is not the variable; Leonardo board / shield / firmware path is.
- **Impact:** ~10 minutes added to session; produced the strongest evidence in either attempt; converted Attempt 1's INCONCLUSIVE into Attempt 2's D-07 FAIL.

**2. [Plan task #5 skipped] Task 5 (BENCH-02 cycle on Leonardo + SST27SF512) not executed.**
- **Found during:** Task 3 + Task 4 close
- **Issue:** With Leonardo read path reading 83.8% zeros and uno328pb at 30% zeros, a write→read→cmp cycle on Leonardo + SST27SF512 cannot produce useful diagnostic data — either the cmp will fail at the read step (testing nothing about the write step) or it will produce a misleading verdict.
- **Disposition:** SKIP. v1.5-BENCH-RESULTS.md post-hoc closure row remains scaffolded (TBD — Wave B fills); will be filled in the future Phase 29 re-run after the Leonardo read path is fixed.
- **Impact:** No GATE-1.6 non-regression evidence captured this session; will need to be tested in the future re-run.

### Plan boundary-honoring (no deviations)

- No sub-repo commits, branch changes, merges, pushes, or tags (verified via `git log` + `git tag --list`).
- No source code edits (no `.cpp`, `.h`, `.ino`, `.py` modifications in either submodule).
- No `update_version.py` invocation.
- No `firestarter fw -i --pre --force` (Phase 30 scope).

## Issues Encountered

**1. Phase 28 fix regression on Leonardo + uno328pb (the primary outcome of this plan).**
   - **Symptom:** Leonardo + uno328pb under Phase 28 firmware (`4f205e58`) read garbage (5 distinct SHAs / N=5 / 83.8% zeros on Leo, 18.2% jitter on 328pb), while Uno reads cleanly (Δ=0 hex, regression check held).
   - **Strengthening:** Attempt 2 chip-swap diagnostic eliminates chip-state as the cause variable (proven-good chip reads garbage on Leonardo); Attempt 2 bench-restoration to Phase 26-baseline shield (Modified Rev 0 + voltage-divider mod) eliminates shield-mismatch as the cause variable.
   - **Remaining hypothesis-space:** (a) Phase 28 fix commits introduced a 32U4 + 328PB read-path regression; (b) Leonardo + uno328pb hardware degraded between Phase 26 (2026-05-21) and Phase 29 Attempt 2 (2026-05-22 PM). Hypothesis (a) is the stronger candidate given the qualitative-shape change in the failure mode and the timing of the regression onset (between the two bench sessions, the firmware was updated with Phase 28 commits).
   - **Closure:** Phase 27 RCA re-open with pre-Phase-28-firmware A/B test as first experiment. See EVIDENCE.md "Wave B FAIL post-mortem (D-07)" section.

**2. uno328pb chip-ID protocol stable timeout (separate from read-data failure).**
   - **Symptom:** `firestarter id W27C512` on /dev/ttyUSB0 times out consistently across Attempt 1 + Attempt 2, even though `firestarter fw` handshake succeeds and `firestarter hw` returns Rev2 cleanly. The chip-ID protocol uses a separate code path (VPP=12V identification mode) from the data-byte read.
   - **Possible causes:** (a) Phase 28 fix affected the chip-ID protocol's timing on 328PB (different from data-byte read timing), (b) urclock bootloader interaction with the post-Phase-28 firmware boots differently than pre-fix, (c) 328PB hardware issue with VPP regulator engagement that pre-existed but wasn't visible before Phase 28.
   - **Closure:** Filed as Phase 27 RCA candidate #3 (separate from the data-byte read regression). Should be re-tested in the post-Phase-28-firmware A/B experiment.

## User Setup Required

None — no external service configuration added by this plan.

## Next Phase Readiness

**Phase 30 BLOCKED.** Cannot proceed with `v1.6-read-bug → beta → main` promotion, pre-release cut, or stable tag bump until a corrected firmware passes Phase 29.

**Phase 27 RCA recommended re-entry path:**

1. **Build pre-Phase-28-firmware:** `cd /workspaces/firestarter && git stash` (preserve config drift if any) → `git checkout v1.6-read-bug~2` → `pio run -e leonardo` → capture SHA-256 of `firestarter_leonardo.hex` for traceability. **DO NOT COMMIT** the submodule HEAD change; this is a disposable build for A/B testing. Restore with `git checkout v1.6-read-bug` after.

2. **Sideload pre-fix to Leonardo:** Chip OUT of Leonardo socket first (per [[feedback_chip_out_before_sideload]]). `pio run -e leonardo -t upload --upload-port /dev/ttyACM1` with the pre-fix build. Chip back in. Verify handshake: `firestarter -p /dev/ttyACM1 fw` should still say `controller: leonardo` (board name in firmware doesn't depend on the read-path fix commits).

3. **Re-probe Leonardo N=5 consistency-check:**
   - If pre-fix reads **structured EPROM data with ~2.1% bit-jitter** (matching Phase 26 baseline) → **confirms Phase 28 introduced a regression**. Re-open Phase 27 RCA with Phase 28 Discretion #1 (`_NOP()` count adjustment) as first experiment, OR git-bisect the two Phase 28 commits (`437339b6` vs `4f205e58`) to isolate which is the introducer.
   - If pre-fix reads **garbage similar to Attempt 2** → falsifies the firmware-regression hypothesis. Indicates hardware degradation. Operator-level diagnosis required (Leonardo board health, shield contact wear, voltage references).

4. **Re-validate uno328pb separately:** uno328pb chip wasn't swapped in this session, so the chip-vs-board question remains open there. Either (a) chip-swap uno328pb chip with Uno's known-good chip + re-probe (analogous to the Leonardo diagnostic done here), or (b) sideload pre-Phase-28-firmware to uno328pb directly + re-probe. Either path closes the ambiguity.

5. **After a corrected fix lands:** rebuild all 3 .hex artifacts, re-sideload (chip-out / chip-in protocol throughout), re-run Phase 29 Wave B from scratch (Tasks 1-7).

**Until then:** STATE.md `status: blocked`; Open Blockers entry tracks the Phase 29 FAIL; meta-repo `main` retains the FAIL evidence + post-mortem; sub-repo `v1.6-read-bug` branches stay LOCAL with the Phase 28 fix commits intact (not deleted — preserved for the bisection / A/B test).

---
*Phase: 29-multi-board-bench-verification*
*Plan: 02 (Attempt 2 — supersedes Attempt 1 INCONCLUSIVE archive)*
*Outcome: FAIL (D-07 milestone-reopens) — Phase 28 fix verdict on the acceptance gate is FAIL; chip-swap diagnostic eliminates chip-state; recommend Phase 27 RCA re-open with pre-firmware A/B test as first experiment*
*Completed: 2026-05-22*

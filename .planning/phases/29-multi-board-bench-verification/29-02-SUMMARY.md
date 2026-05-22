---
phase: 29-multi-board-bench-verification
plan: 02
subsystem: testing
tags: [bench-verification, operator-on-bench, acceptance-gate, inconclusive, hardware-instability, port-shuffle, vpp-regulator, w27c512]

requires:
  - phase: 28-fix-implementation-unit-test-coverage
    provides: locally-built firestarter_{uno,leonardo,uno328pb}.hex with Phase 28 read-bug fix candidates (commits 437339b6 + 4f205e58)
  - phase: 29-multi-board-bench-verification (Wave A, plan 29-01)
    provides: built + SHA-256-recorded .hex artifacts; host CLI installed at 3.0.0b4; EVIDENCE.md + v1.5-BENCH-RESULTS.md SCAFFOLD sections; pre-flight checklist
provides:
  - Phase 29 Wave B partial evidence: Uno regression check PASS (Phase 26 baseline held; Phase 28 fix Δ=0 confirmed on Uno code path); Leonardo + uno328pb verdicts INCONCLUSIVE (bench-instability, not Phase 28 fix evidence)
  - Five Phase-29-scope diagnostic findings recorded in .planning/v1.6-EVIDENCE.md Scope-changes #3-#8 (host-CLI dev-read stdout shape, info pin-map crash, port-identity shuffle, uno328pb v1.6 silicon confirmation, Phase 28 vs bench-degradation ambiguity, hw rev override read-back inconsistency)
  - Two new feedback memories for future bench sessions ([[feedback_chip_out_before_sideload]], [[feedback_verify_port_identity_each_task]])
  - Updated [[project_uno328pb_correction]] memory disambiguating v1.5 mislabeled Plain Uno from v1.6 real ATmega328PB
affects: 30-documentation-milestone-close, future Phase 29 re-run, possible Phase 27 RCA re-open

tech-stack:
  added: []
  patterns:
    - "Port-identity verification per task (always `firestarter -p <port> fw` to confirm `controller:` substring before issuing bench commands)"
    - "Data-only SHA-256 hashing of `dev read` hexdump output (`grep -E '^[0-9a-f]{8}:' file | sha256sum`) to skip the variable elapsed-time footer"
    - "Chip-out-before-sideload protocol for RURP-shield boards"

key-files:
  created:
    - .planning/v1.6/post-fix-runs/W27C512-uno-2026-05-22-090501/run_{01..05}.bin (5 × 65536 B, SHA `8d2124eb7c994f717ace1b2b79c52fa95153aa82c6a4891a323ad924ef409759`)
    - .planning/v1.6/post-fix-runs/W27C512-leonardo-2026-05-22-091624/run_{01..05}.bin (5 distinct SHAs, 99.4% zeros — INCONCLUSIVE, preserved for next-session post-mortem)
    - .planning/v1.6/bench-logs/W27C512-uno-2026-05-22-090501.log
    - .planning/v1.6/bench-logs/W27C512-leonardo-2026-05-22-091624.log
    - /home/vscode/.claude/projects/-workspaces/memory/feedback_chip_out_before_sideload.md
    - /home/vscode/.claude/projects/-workspaces/memory/feedback_verify_port_identity_each_task.md
  modified:
    - .planning/v1.6-EVIDENCE.md (Phase 29 section fully populated for Uno; Leonardo + uno328pb rows + Verdict block + Hand-off block populated as INCONCLUSIVE; Scope-changes #3-#8 appended)
    - /home/vscode/.claude/projects/-workspaces/memory/project_uno328pb_correction.md (disambiguated v1.5 mislabel vs v1.6 real 328PB)

key-decisions:
  - "Halted Wave B as INCONCLUSIVE rather than D-07 FAIL: the captured Leonardo data (5 SHAs / 0.05% pairwise jitter) is qualitatively different from Phase 26 baseline structured-data + 2.1% jitter and is hardware-confounded; D-07 milestone-reopens would force Phase 27 to chase a possibly-phantom timing issue when chip/shield-state may be the real cause."
  - "STATE.md stays `status: executing` (NOT `blocked`): Phase 29 produced partial evidence (Uno regression PASS) and a clear bench-recovery plan for the next session, not a fix-incomplete signal that justifies milestone re-open."
  - "Phase 30 NOT yet eligible: branch-promotion + pre-release-cut + tag-bump scope cannot fire on partial evidence. Phase 29 stays open."
  - "uno328pb identity for v1.6: handshake confirms Case A (`controller: uno328pb` → true ATmega328PB silicon), updating [[project_uno328pb_correction]] memory to disambiguate v1.5 mislabel from v1.6 real 328PB hardware."
  - "Plan methodology defects captured (not silenced): `dev read … <outfile>` positional doesn't exist (CLI prints hexdump to stdout); `firestarter info` crashes in `ic_layout.py:167`; `firestarter config --rev N` read-back display may be inconsistent. All filed as out-of-Phase-29-scope follow-ups."

patterns-established:
  - "Pattern (memory feedback): Always `chip out → sideload → chip in` for RURP-shield boards — never sideload with EPROM/SRAM seated, voltage swings on data/address/control lines can damage the chip."
  - "Pattern (memory feedback): Re-query `firestarter -p <port> fw` for `controller:` substring at the start of every multi-board task — Linux ACM port assignment shuffles after USB unplug/replug events."
  - "Pattern (Scope-change #3, EVIDENCE.md): Hash `dev read` output via `grep -E '^[0-9a-f]{8}:' file | sha256sum` to filter the variable `Read complete (Xs)` timing footer; raw `sha256sum file` produces false-positive divergence."

requirements-completed: []  # VERIFY-01/02/03/04 are NOT completed today. Uno regression PASS is one partial input to VERIFY-02; full closure requires next-session Leonardo + uno328pb data.

duration: 90min
completed: 2026-05-22
---

# Phase 29 Plan 02: Multi-Board Bench Verification — INCONCLUSIVE

**Uno regression check PASS (SHA `8d2124eb…` byte-identical to Phase 26 baseline); Leonardo + uno328pb verdicts INCONCLUSIVE due to bench-instability (chip-read degraded across Modified Rev 0 + Rev 2.0 shields; VPP regulator-over-limit on Leonardo+Rev 2.0; chip-ID timeout on uno328pb) — Phase 28 fix verdict on THE acceptance gate NOT determined today.**

## Performance

- **Duration:** ~90 min (operator-on-bench session)
- **Started:** 2026-05-22T08:55:00Z (operator confirmed bench presence + shield-rev declarations)
- **Completed:** 2026-05-22T10:25:00Z (INCONCLUSIVE close)
- **Tasks attempted:** 8 (Tasks 1-2 PASS; Tasks 3-4 INCONCLUSIVE; Task 5 DEFERRED-NEXT-SESSION; Task 6 Verdict-block-resolved-as-INCONCLUSIVE; Task 7 this SUMMARY; Task 8 NOT TRIGGERED — D-07 doesn't apply to INCONCLUSIVE data)
- **Files modified:** 2 (.planning/v1.6-EVIDENCE.md, this SUMMARY) + 12 new evidence files in `.planning/v1.6/post-fix-runs/` and `.planning/v1.6/bench-logs/` + 3 memory files

## Accomplishments

- **Uno regression check PASS** captured: N=5 byte-identical SHA-256s (`8d2124eb…`) on `/dev/ttyACM0` matching Phase 26 baseline EVIDENCE.md line 295 exactly. Phase 28 fix Δ=0 on Uno code path confirmed.
- **Uno 1KB shell-loop PASS** captured: 5 reads × 1024 B, data-only SHA `de5194e8…` identical across all reads.
- **uno328pb Case A handshake confirmed** for v1.6 hardware: `controller: uno328pb` returns from `/dev/ttyUSB0` — operator is using a different physical board than the v1.5-mislabeled Plain Uno. Memory updated.
- **Five Phase-29-scope diagnostic findings** recorded in EVIDENCE.md Scope-changes #3-#8, including a candidate Phase 28 fix regression hypothesis on Leonardo (worth a pre-fix-firmware A/B test in the next bench session).
- **Two new feedback memories** captured for future bench sessions: chip-out-before-sideload safety, port-identity verification per task.

## Task Commits

Each task committed atomically on `main` (meta-repo only; sub-repo branch state untouched per plan boundaries):

1. **Task 1: Session start / Hardware metadata snapshot** — `5b66a74` (test: shield revs recorded)
2. **Task 2: Uno bench verification** — committed alongside; bench evidence + EVIDENCE.md updates + Scope-changes #3/#4
3. **Tasks 3-8: INCONCLUSIVE close** — to be committed in this session-close commit (EVIDENCE.md INCONCLUSIVE rows + Verdict block + Hand-off block + Scope-changes #5/#6/#7/#8 + this SUMMARY + memory updates)

No sub-repo commits, no sub-repo branch promotions, no tags cut (per plan boundaries — verified `cd /workspaces/firestarter && git log -3 --oneline` and `cd /workspaces/firestarter_app && git log -3 --oneline` unchanged from session start).

## Files Created/Modified

- `.planning/v1.6-EVIDENCE.md` — Phase 29 section now reflects Uno PASS + Leonardo/uno328pb INCONCLUSIVE; Verdict block populated; Hand-off block flags Phase 30 NOT yet eligible; Scope-changes #3-#8 appended.
- `.planning/v1.6/post-fix-runs/W27C512-uno-2026-05-22-090501/run_{01..05}.bin` — 5 × 65536 B Uno run binaries (committed).
- `.planning/v1.6/post-fix-runs/W27C512-leonardo-2026-05-22-091624/run_{01..05}.bin` — 5 × 65536 B Leonardo INCONCLUSIVE run binaries (preserved for post-mortem; will be committed in this session-close commit).
- `.planning/v1.6/bench-logs/W27C512-uno-2026-05-22-090501.log` + `W27C512-leonardo-2026-05-22-091624.log` — full tee'd `dev consistency-check` stdout (committed).
- `~/.claude/projects/-workspaces/memory/feedback_chip_out_before_sideload.md` — new feedback memory.
- `~/.claude/projects/-workspaces/memory/feedback_verify_port_identity_each_task.md` — new feedback memory.
- `~/.claude/projects/-workspaces/memory/project_uno328pb_correction.md` — updated (v1.5 vs v1.6 board disambiguation).
- `~/.claude/projects/-workspaces/memory/MEMORY.md` — updated (2 new memory pointers).

## Decisions Made

1. **INCONCLUSIVE, not D-07 FAIL.** The Leonardo "5 distinct SHAs at N=5 / 0.05% pairwise jitter" data is hardware-confounded: per-run binaries are 99.4% zero-bytes (not the structured-data + 2.1%-jitter shape Phase 26 baseline produced with the same shield/chip class), and chip-ID returned `0x00` stable across 3 retries. D-07 milestone-reopens would force Phase 27 RCA to chase a possibly-phantom timing issue when the real cause may be chip/shield damage. INCONCLUSIVE preserves both hypotheses for the next-session disambiguation test.

2. **STATE.md stays `status: executing`.** Phase 29 didn't fail and didn't pass; partial evidence (Uno regression PASS) + a clear next-session recovery plan is recorded. Milestone neither ships nor re-opens on the basis of today's data.

3. **Memory `[[project_uno328pb_correction]]` updated, not deleted.** The v1.5 mislabel is still true (and still relevant for reading the v1.5 baseline `.planning/todos/pending/large-read-data-jitter-uno328pb.md` data correctly). For v1.6 Phase 29 the operator has a different real 328PB board — both contexts now coexist in the memory.

4. **No sub-repo state mutations.** Plan boundaries (NO merge, NO push, NO tag, NO `update_version.py`, NO source-code edits) honored throughout the session.

## Deviations from Plan

### Wave-B execution shape deviations (no auto-fixes — operator-confirmed branches)

**1. [Plan order] Sideloads for Tasks 3 + 4 parallelized at operator's request.**
- **Found during:** Task 2 close
- **Issue:** Plan implies sequential per-board sideload (Task 2 → Task 3 → Task 4); operator's bench layout has all 3 boards plugged in and asked to "program both pb and leonardo at the same time" while they re-seated chips.
- **Fix:** After Task 2 PASS, sideloaded `firestarter_leonardo.hex` to `/dev/ttyACM1` AND `firestarter_uno328pb.hex` to `/dev/ttyUSB0` back-to-back (not strictly parallel; sequential but without intermediate verification-read prompts). Operator confirmed chip-out-then-chip-in protocol per [[feedback_chip_out_before_sideload]] for both.
- **Impact:** Saved ~10 minutes; verification reads (Tasks 3 + 4) still ran sequentially per board.

**2. [Plan command shape] `dev read … <outfile>` positional rejected by host CLI.**
- **Found during:** Task 2 Step 4 (1KB shell-loop on Uno)
- **Issue:** Plan's `firestarter -p /dev/ttyACM0 dev read W27C512 -s 1024 -a 0 /tmp/r1k_uno_$i.bin` produces `firestarter: error: unrecognized arguments: /tmp/r1k_uno_1.bin` — `dev read` prints to stdout, doesn't take an outfile positional.
- **Fix:** Redirected stdout (`… > /tmp/r1k_<board>_$i.bin`); since the stdout is hexdump-formatted text with a variable `Read complete (Xs)` timing footer, hashed only the `^[0-9a-f]{8}:` data lines (`grep -E '^[0-9a-f]{8}:' file | sha256sum`) to compute the byte-equivalence verdict.
- **Impact:** Methodology correct; Uno Axis 2 verdict PASS holds. Plan template needs updating for next-session re-run. Filed as Scope-change #3 in EVIDENCE.md.

**3. [Plan acceptance grep] Task 1 `awk '/^## Phase 29/,/^## /'` range collapses to a single line.**
- **Found during:** Task 1 acceptance verification
- **Issue:** The `awk` range pattern with identical from/to regex matches only the from-line itself, so `awk … | grep -c '^| (Plain Uno|Leonardo|uno328pb)'` returned `0` instead of `≥3`.
- **Fix:** Verified using a corrected range `awk '/^## Phase 29 —/,/^## Verdict$/'` which returned the expected count.
- **Impact:** No semantic impact; Task 1 acceptance held. Plan acceptance-grep should be tightened in a future plan revision.

### Bench-execution deviations (operator-confirmed; full diagnostic in EVIDENCE.md)

**4. [Bench instability] Leonardo + uno328pb chip reads degraded throughout session.**
- **Five different probe configurations** tried on Leonardo and uno328pb across two re-seats + one shield-swap (Modified Rev 0 → Rev 2.0) + one override-clear + one explicit `--rev 2`; all produced different but uniformly broken chip-read patterns (chip-ID `0x00`/timeout, reads either `00 00 …`, `7f 7f …`, `5a 08 5a 08 …`, or `03 03 03 …`). Uno was the only seat that produced a clean read.
- **Final disposition:** INCONCLUSIVE close per operator's choice; no D-07 FAIL trigger because data is hardware-confounded.
- **Recovery plan recorded in EVIDENCE.md Hand-off block:** restore Modified Rev 0 + voltage-divider mod to Leonardo, verify chip-rotation chip health on Uno first, then re-run Task 3 with per-task port-identity verification.

**5. [Diagnostic detour] Port-identity shuffle cost ~20 minutes.**
- After the Modified Rev 0 → Rev 2.0 shield swap on Leonardo, Linux re-enumerated the USB devices and `/dev/ttyACM0` ↔ `/dev/ttyACM1` swapped. Orchestrator was probing the bare Plain Uno on `/dev/ttyACM1` while assuming it was Leonardo, producing the misleading "Leonardo all-`0x03`" pattern.
- **Fix:** Operator suggested checking firmware on all ports; `firestarter -p <port> fw` re-established correct identity in 30 seconds.
- **New memory captured:** [[feedback_verify_port_identity_each_task]].

## Issues Encountered

1. **Phase 28 fix vs. bench-degradation ambiguity (the primary issue).** Same shield (Modified Rev 0 + voltage-divider mod), same chip class (W27C512), same firmware-build process between Phase 26 (2026-05-21) and Phase 29 (2026-05-22). Phase 26 produced structured EPROM data + 2.1% bit-jitter on Leonardo; Phase 29 produces 99.4% zeros + 0.05% jitter on the non-zero bytes. Two candidate causes both fit:
   - **(a) Phase 28 fix broke the Leonardo read path** — the `_NOP()` settling in commit `4f205e58` may have changed `rurp_read_data_buffer` timing such that OE/CE pulse widths no longer overlap with chip data drive on 32U4.
   - **(b) Hardware degradation** — chip rotation chips may have worn pins or oxidation; Modified Rev 0 shield contact may have aged.
   
   **Disambiguation in next session:** sideload `firestarter/v1.6-read-bug~2` (one commit before Phase 28 fixes) to Leonardo with restored Modified Rev 0 + verified-healthy chip. If pre-fix reads structured data → Phase 28 is the cause → Phase 27 RCA re-opens with Phase 28 Discretion #1 (`_NOP()` count adjustment) as first experiment. If pre-fix also reads ~zeros → hardware issue → operator-level debugging.

2. **Leonardo VPP regulator over-limit on Rev 2.0 shield.** `Programmer error during init: VPP is high: 13.1V > 12.0V` returned from chip-ID protocol when the Modified Rev 0 was swapped for Rev 2.0 (which doesn't have the voltage-divider mod). The Modified Rev 0 + voltage-divider mod is calibrated specifically for Leonardo's 5V/3.3V signaling; Rev 2.0 isn't. Recorded for next-session shield-config discipline.

3. **`firestarter config --rev N` read-back display inconsistency.** After running `firestarter -p /dev/ttyACM1 config --rev 2`, the subsequent `firestarter hw` returned `Hardware revision: Rev2, Override HW: Rev0` — the "Override HW:" column reported `Rev0` despite the explicit `--rev 2` write. May be host-CLI display bug, firmware EEPROM commit timing issue, or misinterpretation of the display fields. Filed as Scope-change #8 — out-of-Phase-29-scope follow-up.

## User Setup Required

None — no external service configuration was added by this plan. (The plan-described uno328pb bootloader / urclock setup pre-existed from v1.5 BENCH-01.)

## Next Phase Readiness

**Phase 30 NOT yet eligible.** Re-run Phase 29 Wave B in a future bench session after:

1. **Bench prep:**
   - Restore Modified Rev 0 + voltage-divider mod on Leonardo.
   - Verify each chip-rotation chip is healthy by seating in Uno first and running `firestarter id W27C512` — chip-ID must match DB.
   - Confirm operator has clear ~30-60 min window for the operator-on-bench session.

2. **Session discipline:**
   - At the start of every task: re-query `firestarter -p <port> fw` and verify `controller:` substring matches the expected board (per [[feedback_verify_port_identity_each_task]]). Don't trust session-start port mapping across USB unplug events.
   - Chip out before sideload; chip back in before reads (per [[feedback_chip_out_before_sideload]]).

3. **Disambiguation test (run first, before Task 3 retry):**
   - Sideload `firestarter/v1.6-read-bug~2` (one commit before Phase 28 fixes) to Leonardo.
   - Probe chip-ID + 1KB read.
   - Compare to today's Phase 28 post-fix Leonardo data.
   - If pre-fix reads structured data → re-open Phase 27 RCA (Phase 28 fix introduced regression).
   - If pre-fix also reads ~zeros → operator-level hardware diagnosis (chip/shield).

4. **Once Leonardo bench is healthy:** retry the full Task 3 + Task 4 + Task 5 sequence.

**Until then:** STATE.md remains `executing` (Phase 29 open); no Phase 30 work; `firestarter` + `firestarter_app` v1.6-read-bug branches stay LOCAL (no merges, no pushes, no tags).

---
*Phase: 29-multi-board-bench-verification*
*Plan: 02*
*Outcome: INCONCLUSIVE (Uno regression PASS; Leonardo + uno328pb bench-confounded; Phase 30 not yet eligible)*
*Completed: 2026-05-22*

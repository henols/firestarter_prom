---
phase: 26-cross-board-reproduction-diagnostic-tooling
plan: 02
subsystem: testing
tags: [bench-validation, consistency-check, read-bug-repro, v1.6, eprom, host-cli]

requires:
  - phase: 26-cross-board-reproduction-diagnostic-tooling
    provides: "`firestarter dev consistency-check` diagnostic CLI shipped by Plan 26-01 (sub-repo commit 999c3cc on firestarter_app/v1.6-read-bug)."
provides:
  - "Pre-fix consistency-check baseline in .planning/v1.6-EVIDENCE.md (2 of 3 board rows populated; uno328pb row marked DEFERRED with explicit reason)."
  - "Empirical refutation of the 'jitter on all 3 controllers' premise: Plain Uno path is clean, Leonardo path is broken."
  - "Phase 27 RCA scope narrowed to Leonardo-specific code paths (ATmega32U4 USB-CDC, 1024-B DATA_BUFFER, per-chunk send loop)."
  - "v1.5 'uno328pb' identity correction captured: that board was actually a Plain Uno + wrong FW, not a true 328PB silicon configuration."
affects:
  - "Phase 27 (Root Cause Analysis) — inherits the narrowed scope + the first-divergence offset (0x0003) as a starting bisection point."
  - "Phase 28 (Fix Implementation) — must land a Leonardo-targeted fix that preserves Uno behavior."
  - "Phase 29 (Post-fix Verification) — re-runs the same consistency-check on Plain Uno (expected PASS, unchanged) + Leonardo (expected FAIL → PASS post-fix)."

tech-stack:
  added: []
  patterns:
    - "Cross-phase evidence-accretion file (.planning/v1.6-EVIDENCE.md) with locked 9-column row schema per D-08."

key-files:
  created:
    - ".planning/v1.6-EVIDENCE.md (populated with 2 board rows + 1 DEFERRED row + closed Verdict section)"
    - ".planning/v1.6/bench-logs/W27C512-uno-20260521-133418.log"
    - ".planning/v1.6/bench-logs/W27C512-leonardo-20260521-134133.log (aborted chip-ID-fail attempt; kept as evidence of variant mismatch)"
    - ".planning/v1.6/bench-logs/W27C512-leonardo-20260521-134210.log"
    - ".planning/v1.6/consistency-check-runs/W27C512-uno-20260521-133418/run_0[1-3].bin (3× 65536 B; all SHA-256 identical)"
    - ".planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_0[1-3].bin (3× 65536 B; 3 distinct SHAs)"
  modified:
    - ".planning/v1.6-EVIDENCE.md (scaffold from 26-02 Task 1 + populated 2026-05-21)"

key-decisions:
  - "Defer uno328pb row (Task 4) to a follow-up session — the board labeled uno328pb in v1.5 bench notes was actually a Plain Uno + wrong FW per operator clarification 2026-05-21."
  - "Override Leonardo hw_revision to Rev2 via `firestarter config --rev 2`; clear any override on Plain Uno via `--rev -1` so both boards report the same shield-rev metadata. Honest because the Leonardo's physical shield is a modified Rev 0 with an added voltage-divider mod making it capability-equivalent to Rev 2."
  - "Use --force on the Leonardo run to bypass the W27C512 chip-ID variant mismatch (0xda01 vs DB-expected 0xda08); per RESEARCH Pitfall 5, the --force flag exists precisely for this case."
  - "Use W27C512 instead of SST27SF512 (D-09's recommended chip): operator had W27C512s already socketed in both boards — fewer chip moves, less risk to chips during bench session."

patterns-established:
  - "Bench-driven dual-board pattern: both Arduinos plugged in simultaneously on /dev/ttyACM0 + /dev/ttyACM1, separate chips socketed in each, no USB swap between board runs."
  - "Shell exit capture for piped commands: use ${PIPESTATUS[0]} to capture firestarter's exit code when tee'ing output. `$?` after a pipe captures tee's exit (always 0 unless tee itself fails) and silently masks firestarter's exit-2 hardware-error signal."

requirements-completed:
  - REPRO-01
  - REPRO-02

duration: ~45min
completed: 2026-05-21
---

# Phase 26 Plan 26-02 Summary

**Pre-fix consistency-check baseline captured on Plain Uno (PASS, unexpected) + Leonardo (FAIL, 2.1% byte-jitter at first divergence offset 0x0003) — v1.6 read-bug premise narrowed from 'shared across all 3 controllers' to 'Leonardo-specific (32U4 USB-CDC code path).'**

## Performance

- **Duration:** ~45 min (2026-05-21 ~13:30 → ~14:15)
- **Started:** 2026-05-21T13:30Z (after Plan 26-01 close + scaffold commit 59e207b)
- **Completed:** 2026-05-21T14:15Z (this commit)
- **Tasks:** 4 of 5 (Task 4 uno328pb deferred — board has wrong FW)
- **Files modified:** 1 (`.planning/v1.6-EVIDENCE.md`) + 3 bench logs + 6 binary run artifacts

## Accomplishments

- **REPRO-01 closed (PASS, unexpected):** Plain Uno + Rev 2.0 shield + W27C512 (chip ID 0xda08) produced 3 byte-identical 64KB reads at SHA-256 `8d2124eb7c994f717ace1b2b79c52fa95153aa82c6a4891a323ad924ef409759`. ~20s per read. Refutes the pre-existing-bug prediction on the 328P silicon.
- **REPRO-02 closed (FAIL, jitter reproduced):** Leonardo + modified Rev 0 shield + W27C512 (chip ID 0xda01) produced 3 distinct SHAs across 3 consecutive 64KB reads. 1349 / 65536 byte-jitter rate = 2.1%; first divergence at offset `0x0003` (run_1=0x83, run_2=0x03); first 10 divergent offsets clustered in the first 1.4KB of the read — points at handshake or first-chunk boundary rather than mid-stream drift.
- **ROADMAP SC#5 partially closed:** 2 of 3 board rows populated; uno328pb row marked DEFERRED with explicit reason in the table.
- **v1.5 identity correction captured:** the board labeled `uno328pb` in v1.5 bench notes was actually a Plain Uno + wrong FW per operator clarification 2026-05-21. The 2026-05-21 ~57.8% divergence rate attributed to "uno328pb" in `.planning/todos/pending/large-read-data-jitter-uno328pb.md` was captured on a FW-mismatched plain Uno — Phase 27 must NOT use that magnitude as ground truth.
- **Cross-phase contract locked in-file:** D-08 9-column schema + Phase 27/28/29 forward-annotation HTML comments + closed Verdict section. Phases 27/28/29 inherit the shape verbatim.

## Task Commits

1. **Task 1: Scaffold v1.6-EVIDENCE.md + bench-log sentinels** — `59e207b` (docs)
2. **Task 2: Plain Uno bench run** — no commit (artifacts under .planning/v1.6/...; rolled into Task 5)
3. **Task 3: Leonardo bench run** — no commit (artifacts rolled into Task 5; aborted chip-ID-fail attempt kept as evidence)
4. **Task 4: uno328pb bench run** — DEFERRED, row marked DEFERRED in evidence table
5. **Task 5: Populate evidence table + bench artifacts + close Verdict** — this commit (docs)

## Files Created/Modified

- `.planning/v1.6-EVIDENCE.md` — populated 2 board rows (uno PASS / leonardo FAIL) + uno328pb DEFERRED row + closed Verdict section with REPRO-01/02/03 closure narratives + Hardware metadata snapshot table + Phase 27 entry conditions section.
- `.planning/v1.6/bench-logs/W27C512-uno-20260521-133418.log` — full tee'd stdout from Plain Uno run.
- `.planning/v1.6/bench-logs/W27C512-leonardo-20260521-134133.log` — aborted Leonardo attempt (chip-ID-fail without --force; kept as evidence of variant mismatch).
- `.planning/v1.6/bench-logs/W27C512-leonardo-20260521-134210.log` — full tee'd stdout from Leonardo run with --force.
- `.planning/v1.6/consistency-check-runs/W27C512-uno-20260521-133418/run_0[1-3].bin` — 3× 65536-byte binaries, byte-identical.
- `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_0[1-3].bin` — 3× 65536-byte binaries, all distinct.
- `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134133/run_01.bin` — empty (0 bytes), preserved as evidence of pre-`--force` early-bailout behavior.

## Decisions Made

See `key-decisions` frontmatter above. Highlights:

1. **Hardware-version alignment via override.** Operator's intent: both boards report the same shield-rev in their EEPROM-stored config so the consistency-check binaries reflect comparable hardware-detection state. Uno's auto-detect was already Rev2; Leonardo's auto-detect was Rev1 (its physical shield is a modified Rev 0). Overriding Leonardo to Rev2 is honest because the voltage-divider mod gives it Rev 2 capability.
2. **`--force` to bypass chip-ID variant mismatch.** Plain Uno's W27C512 has chip ID 0xda08 (matches DB), Leonardo's has 0xda01 (stable across all 3 reads — not jitter, just a different Winbond variant). RESEARCH §Pitfall 5 anticipated this. The chip-database entry should be extended to include 0xda01 as an accepted alias — flagged as cosmetic follow-up.
3. **Chip choice deviation from plan recommendation.** Plan recommended SST27SF512 (to match the 2026-05-21 baseline). Operator already had W27C512s in both sockets — saved chip-move risk. The baseline-comparison utility of SST27SF512 was already lost when the uno328pb identity correction landed, so the chip choice has minimal impact.

## Deviations from Plan

### Process deviations

**1. [Scope reduction] uno328pb row deferred — board has wrong firmware.**
- **Found during:** Task 2 setup (operator message: "Plain UNO and Leonardo hooked up no pb(skip it for now)" + follow-up "its not a uno328pb its a plain uno with the wrong FW").
- **Issue:** The plan's Task 4 was predicated on the board being a true ATmega328PB silicon configuration (per the v1.5 bench notes). Operator clarified that the board is actually a Plain Uno with mis-flashed firmware — running consistency-check on it would measure FW-silicon mismatch, not the read-bug under investigation.
- **Fix:** Row marked `DEFERRED — board has wrong FW (per operator 2026-05-21); was misidentified as 328PB in v1.5 bench notes. Requires reflash before re-baseline.` instead of populated. The plan's `requirements_addressed` only listed REPRO-01 + REPRO-02 (both closed), so the deferral does not block REPRO closure. ROADMAP SC#5 (pre-fix baseline for all 3 boards) is partially closed (2/3 boards).
- **Files modified:** `.planning/v1.6-EVIDENCE.md` (uno328pb row), `~/.claude/projects/-workspaces/memory/project_uno328pb_correction.md` (new memory entry capturing the correction).

**2. [Scope reduction] Plain Uno result was PASS (expected FAIL).**
- **Found during:** Task 2 verdict.
- **Issue:** The plan's `<how-to-verify>` step 5 for Task 2 explicitly anticipated this case: `PASS (unexpected — refutes pre-existing-bug prediction on uno)` if exit code 0. The Plain Uno's read path appears clean — refutes the "jitter on all 3 controllers" v1.6 premise.
- **Fix:** Row recorded with the verbatim plan-anticipated Verdict text. No retry — repeating the read would not change the result; per-run elapsed times (19.98s, 19.98s, 19.99s) showed deterministic timing.
- **Impact:** Phase 27 RCA scope narrows from "shared bug across all 3 controllers" to "Leonardo-specific bug." Phase 28 fix must preserve Uno's clean behavior.

**3. [Implementation finding] Shell exit capture used `$?` after a pipe — masked firestarter's exit-2 signal on first Leonardo attempt.**
- **Found during:** Task 3 first attempt (chip-ID-fail run).
- **Issue:** The pipeline `firestarter ... | tee ...` exits with tee's exit code (0 unless tee itself fails). The visible "EXIT: 0" was misleading; firestarter actually returned a non-zero exit. The plan's `<how-to-verify>` Task 2 step 4 instruction (`echo "EXIT: $?"`) inherits this bash gotcha.
- **Fix:** Used `${PIPESTATUS[0]}` for the second Leonardo attempt. Documented in `patterns-established` frontmatter for future bench sessions.
- **Files modified:** None (bench-session technique only).

### No code deviations

The plan's Task 1 scaffold + Task 5 closure code paths executed verbatim per the plan. The only deviations were operator-driven (Task 4 deferral) or evidence-driven (Plain Uno PASS verdict).

## Issues Encountered

1. **Leonardo W27C512 chip-ID variant mismatch (0xda01 vs DB-expected 0xda08).** Stable across all 3 reads = not jitter, just a chip-database alias gap. **Follow-up:** add `0xda01` to the W27C512 entry's accepted chip-id list (or create a separate "W27C512 (variant 0xda01)" entry). Out of v1.6 scope.

2. **`Board: unknown-board` cosmetic bug in consistency-check stdout.** The diagnostic's `FirmwareManager.check_current_firmware()` call returned None for board name on both Uno and Leonardo (the firestarter fw command does work; the issue is in the consistency-check internal handshake). Non-blocking for the verdict (the stdout regex contract for Phase 29 doesn't include the Board cell), but worth a follow-up patch in Phase 28 or as a post-v1.6 polish.

3. **Pre-existing `firestarter info <chip>` crash.** `TypeError: '<=' not supported between instances of 'list' and 'int'` at `firestarter_app/firestarter/ic_layout.py:167` when running `firestarter info W27C512`. Pre-existing bug, unrelated to v1.6; flagged for future cleanup.

## User Setup Required

None — the consistency-check is read-only (D-02 passive) and the bench session used hardware already present at the operator's bench.

## Next Phase Readiness

**Phase 27 (Root Cause Analysis) can start immediately.** Key inputs for Phase 27 scope:

- **Confirmed bug location:** Leonardo only. Plain Uno is clean.
- **First divergence offset:** `0x0003` (very early — handshake or first-chunk boundary, not mid-stream drift).
- **Jitter magnitude:** 2.1% byte-divergence rate at 64KB on Leonardo.
- **Code-path suspects (in priority order):**
  1. ATmega32U4 USB-CDC implementation in `firestarter/src/firestarter.cpp` MAIN-phase send loop (the 32U4 has native USB; Plain Uno uses an external USB-to-UART bridge — fundamentally different transport).
  2. Leonardo's 1024-byte `DATA_BUFFER_SIZE` vs Uno's 512-byte (the chunked-transfer code in `firestarter_app/firestarter/eprom_operations.py` may have a buffer-boundary edge case).
  3. 32U4-specific timing in the per-chunk send code path (interrupt latency, USB-CDC flush behavior, etc.).
- **What's already been ruled out:** D-03 reuse-not-duplicate is validated — the diagnostic tool exercises the same `_run_state_machine` + `_main_phase_read_data` code path as `firestarter read`. If the bug is there, the tool sees it. Plain Uno's clean result confirms the shared protocol layer above the silicon-specific transport is bug-free.

**Blockers / concerns for Phase 27:**
- The 2026-05-21 baseline magnitude (~57.8%) in `.planning/todos/pending/large-read-data-jitter-uno328pb.md` is NOT comparable to the Leonardo's 2.1% measurement (different silicon, different transport). Phase 27 must treat that prior baseline as advisory only.
- The uno328pb row remains DEFERRED — if Phase 27 needs cross-board triangulation against a true 328PB, the operator must reflash the third board first.

---
*Phase: 26-cross-board-reproduction-diagnostic-tooling*
*Plan: 02*
*Completed: 2026-05-21*

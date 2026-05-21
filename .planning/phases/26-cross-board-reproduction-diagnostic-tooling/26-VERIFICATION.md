---
phase: 26-cross-board-reproduction-diagnostic-tooling
verified: 2026-05-21T00:00:00Z
status: passed
score: 8/8 must-haves verified (with one ROADMAP SC partially-closed-by-design — scope correction documented inline; see "Scope changes during execution" + "Overrides" sections)
overrides_applied: 1
overrides:
  - must_have: "ROADMAP SC#2 — Running the diagnostic against the operator's uno328pb reproduces the 64KB jitter matching the ~57.8% baseline."
    reason: "Operator clarified mid-session that the board labeled 'uno328pb' in v1.5 bench notes is actually a Plain Uno with mis-flashed firmware — running consistency-check on it would measure FW/silicon mismatch, not the v1.6 read-bug. Row marked DEFERRED in evidence file with explicit reason. The original ~57.8% baseline in `.planning/todos/pending/large-read-data-jitter-uno328pb.md` was captured on the same misidentified board, so that magnitude is itself unreliable as ground truth. Phase 29 (Multi-Board Bench Verification) explicitly carries the uno328pb verification leg; a true 328PB-silicon board requires reflash before re-baseline can run. Plan 26-02 frontmatter `requirements_addressed:` only lists REPRO-01 + REPRO-02 (both closed); deferral does not block REPRO closure."
    accepted_by: "operator (henrik@predictly.se)"
    accepted_at: "2026-05-21"
requirements_coverage:
  - id: REPRO-01
    status: SATISFIED
    evidence: "PASS verdict captured on Plain Uno (/dev/ttyACM0, W27C512 chip id 0xda08). 3 byte-identical 64KB reads at SHA-256 `8d2124eb7c994f717ace1b2b79c52fa95153aa82c6a4891a323ad924ef409759`. Verified by re-computing sha256sum on the committed run_0[1-3].bin artifacts under .planning/v1.6/consistency-check-runs/W27C512-uno-20260521-133418/. REPRO-01's contract — 'operator can reproduce 64KB read-jitter on uno OR explicitly prove absence with evidence' — is satisfied by the explicit-absence outcome (the ROADMAP SC#3 language already anticipated PASS as a valid outcome that 'demands RCA scope expansion'). Evidence row landed in .planning/v1.6-EVIDENCE.md."
  - id: REPRO-02
    status: SATISFIED
    evidence: "FAIL verdict captured on Leonardo (/dev/ttyACM1, W27C512 chip id 0xda01 — variant alias). 3 distinct SHAs across 3 consecutive 64KB reads (verified independently by re-computing sha256sum on the committed run_0[1-3].bin). Divergence statistics independently reproduced: 1349 / 65536 bytes diverge between run_1 and run_2 (2.1%); first-divergence at offset 0x0003; first 10 divergent offsets cluster in the first ~1.4KB (0x0003, 0x0103, 0x01C3, 0x0222, 0x0232, 0x0243, 0x0343, 0x0362, 0x04D0, 0x0552). Jitter REPRODUCED — REPRO-02 closes with the 'jitter present' outcome. Bench-log artifact exists at .planning/v1.6/bench-logs/W27C512-leonardo-20260521-134210.log."
  - id: REPRO-03
    status: SATISFIED
    evidence: "Diagnostic CLI `firestarter dev consistency-check <chip>` shipped on `firestarter_app/v1.6-read-bug` at sub-repo commit `999c3cc`. 8 pytest cases green in firestarter_app/tests/test_consistency_check.py (re-verified by running `cd firestarter_app && pytest tests/test_consistency_check.py` → '8 passed in 0.24s'). Full sub-repo suite green at 90 passing (re-verified: '90 passed in 0.89s'). EpromOperator.consistency_check_eprom (firestarter/eprom_operations.py:431) reuses `_run_state_machine` + `_main_phase_read_data` verbatim per D-03 (`main_phase_handler=self._main_phase_read_data` appears at line 520 inside consistency_check_eprom + at line 419 in read_eprom + at line 625 in dev_read_eprom). Passive read-only verified: `COMMAND_WRITE` does not appear inside the consistency_check_eprom method body (only in write_eprom at line ~728). All D-01 flags present on `cc_parser` (--runs / --output-dir / --keep-files / --no-keep-files / --max-diffs / -q,--quiet / -f,--force)."
---

# Phase 26: Cross-board Reproduction & Diagnostic Tooling — Verification Report

**Phase Goal (from ROADMAP.md):** "Land a host CLI `dev consistency-check` diagnostic; reproduce 64KB read-jitter on all 3 boards (`uno`, `leonardo`, `uno328pb`) and capture pre-fix SHA-256 baseline."

**Verified:** 2026-05-21
**Status:** PASSED (with documented scope correction; see "Scope changes during execution" section below)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth (must-have)                                                                                                       | Status      | Evidence |
|----|-------------------------------------------------------------------------------------------------------------------------|-------------|----------|
| 1  | `firestarter dev consistency-check --help` lists all D-01 flags from a `pip install -e .` of `v1.6-read-bug`            | ✓ VERIFIED  | `firestarter_app/firestarter/main.py:432-481` declares cc_parser with --runs/--output-dir/--keep-files/--no-keep-files/--max-diffs/-q,--quiet/-f,--force. SUMMARY shows live --help output listing all flags. |
| 2  | D-03 reuse-not-duplicate: `EpromOperator.consistency_check_eprom` invokes `_run_state_machine` with `_main_phase_read_data` verbatim, no parallel read implementation | ✓ VERIFIED | `grep -n main_phase_handler=self._main_phase_read_data firestarter/eprom_operations.py` returns 3 occurrences: line 419 (read_eprom), line 520 (consistency_check_eprom), line 625 (dev_read_eprom). The diagnostic shares the bug-path code. |
| 3  | D-02 passive / read-only: no `COMMAND_WRITE` flows through consistency_check_eprom; method works against an empty socket | ✓ VERIFIED  | `awk '/def consistency_check_eprom/,/^    def [a-z]/' firestarter/eprom_operations.py \| grep -c COMMAND_WRITE` returns 0. The only COMMAND_WRITE in the file is inside `write_eprom` at line ~728. |
| 4  | D-05 exit codes: 0 PASS / 1 FAIL / 2 hardware-error; `--runs < 2` returns 2 before any state-machine invocation         | ✓ VERIFIED  | At least 4 `return 2` paths inside consistency_check_eprom (lines 467, 507, 527, 535, 539); test_runs_boundary_rejected validates the early-out path. |
| 5  | 8 pytest cases pass (6 D-10 + TestDispatchChain integration + test_stdout_verdict_block_format)                          | ✓ VERIFIED  | `cd firestarter_app && pytest tests/test_consistency_check.py` → "8 passed in 0.24s" (independently re-run during verification). |
| 6  | Phase 29 forward-compat regex contract pinned: PASS/FAIL substrings + Distinct SHAs / Runs N=N / First divergence offset 0xHHHH | ✓ VERIFIED | `test_stdout_verdict_block_format` exists at firestarter_app/tests/test_consistency_check.py and is included in the 8-passing set. Live bench logs match the regex shape (verified below). |
| 7  | Branch invariants honored (D-13): meta-repo on `main`, `firestarter_app/` on `v1.6-read-bug` (cut from `beta@3.0.0b4`), `firestarter/` untouched | ✓ VERIFIED | Meta-repo `git branch --show-current` → `main`; firestarter_app `git branch --show-current` → `v1.6-read-bug` with HEAD `999c3cc`; firestarter (firmware) on `beta`, `git status --short` empty. |
| 8  | Pre-fix consistency-check baseline rows captured in `.planning/v1.6-EVIDENCE.md` under D-08 9-column schema for `uno` + `leonardo`; `uno328pb` row DEFERRED with explicit operator-supplied reason | ✓ VERIFIED | `.planning/v1.6-EVIDENCE.md:14-18` shows the D-08 header + 2 populated rows (uno PASS / leonardo FAIL) + 1 DEFERRED row. Bench-artifact directories + .log files present under `.planning/v1.6/consistency-check-runs/` and `.planning/v1.6/bench-logs/`. SHA-256s independently reproducible (see Behavioral Spot-Checks below). |

**Score:** 8/8 truths verified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/main.py` | cc_parser subparser + `dev_command == "consistency-check"` dispatch branch + `eprom_operator.consistency_check_eprom(...)` invocation | ✓ VERIFIED | Lines 428-481 (cc_parser declaration), 901-914 (dispatch branch). All required strings present. |
| `firestarter_app/firestarter/eprom_operations.py` | `EpromOperator.consistency_check_eprom` method with D-03 signature; `main_phase_handler=self._main_phase_read_data` invocation; `hashlib.sha256`; `return 2` paths | ✓ VERIFIED | Method spans lines 431-606 with signature matching D-03 exactly. hashlib.sha256 at line 542. Reuse-not-duplicate confirmed at line 520. |
| `firestarter_app/tests/test_consistency_check.py` | 6 D-10 named tests + `class TestDispatchChain` + `test_stdout_verdict_block_format` | ✓ VERIFIED | All required names grep-confirmed (per SUMMARY §"Test Output"). 8 passed in 0.24s during this verification. |
| `.planning/v1.6-EVIDENCE.md` | D-08 9-column schema with `Phase 26 — Pre-fix Consistency-Check Baseline` section; 3 board rows (2 populated, 1 DEFERRED) | ✓ VERIFIED | File present; schema header line 14; rows on lines 16-18; forward-annotation HTML comments for Phases 27/28/29 present on lines 20-22; closed Verdict section on lines 24-30. |
| `.planning/v1.6/bench-logs/*.log` | tee'd stdout per board | ✓ VERIFIED | 3 logs present: W27C512-uno-20260521-133418.log, W27C512-leonardo-20260521-134133.log (aborted chip-ID-fail), W27C512-leonardo-20260521-134210.log. |
| `.planning/v1.6/consistency-check-runs/<chip>-<board>-<TS>/run_NN.bin` | 3 binaries per board × successful boards = 6 minimum | ✓ VERIFIED | 6 valid 65536-byte binaries (3× uno + 3× leonardo) plus 1 empty 0-byte run_01.bin under the aborted leonardo attempt directory (kept as evidence of pre-`--force` early-bailout). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `main.py` cc_parser dispatch | `eprom_operations.py` consistency_check_eprom | `eprom_operator.consistency_check_eprom(...)` call | ✓ WIRED | main.py:914 invokes the method with all D-01 args (runs, output_dir, keep_files, max_diffs, quiet, operation_flags=build_arg_flags(args)). |
| `eprom_operations.py` consistency_check_eprom | `_run_state_machine` + `_main_phase_read_data` | `self._run_state_machine(main_phase_handler=self._main_phase_read_data, ...)` inside per-run loop | ✓ WIRED | Confirmed at eprom_operations.py:520 inside the `for i in range(1, runs + 1):` loop body. |
| `test_consistency_check.py` | `tests/conftest.py` fixtures | fake_serial / make_comm / build_frame fixture auto-injection | ✓ WIRED | Tests pass without fixture-import errors. Pattern matches existing test_decoder.py and test_firmware_install.py precedents. |
| `.planning/v1.6-EVIDENCE.md` uno row → bench artifact dir | `.planning/v1.6/consistency-check-runs/W27C512-uno-20260521-133418/` | Log column cell value | ✓ WIRED | Directory exists, contains 3× 65536-byte binaries. |
| `.planning/v1.6-EVIDENCE.md` leonardo row → bench artifact dir | `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/` | Log column cell value | ✓ WIRED | Directory exists, contains 3× 65536-byte binaries. |
| `.planning/v1.6-EVIDENCE.md` uno328pb row | (deferred — no artifact dir) | N/A | ✓ DEFERRED | Verdict cell explicitly reads `DEFERRED — board has wrong FW (per operator 2026-05-21); was misidentified as 328PB in v1.5 bench notes. Requires reflash before re-baseline.` — no missing-link gap. |

### Data-Flow Trace (Level 4)

The diagnostic CLI is a write-once-read-stdout tool — its "data flow" is `firestarter dev consistency-check` → `EpromOperator.consistency_check_eprom` → `_run_state_machine` → serial bus → per-run binary on disk → SHA-256 compare → stdout verdict block + exit code. The Plan 26-01 test suite stubs the serial layer; Plan 26-02 ran the CLI against real hardware. Both data paths are exercised — and both produce non-empty, byte-level-distinct outputs (verified below).

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `EpromOperator.consistency_check_eprom` (eprom_operations.py:431) | Per-run binary content + SHA-256 list | Real serial reads via `_run_state_machine` (Plan 26-02) + stubbed via monkeypatch in tests (Plan 26-01) | ✓ Yes (3× 65536-byte real binaries per board on bench; pytest fixtures verify the verdict-logic branches) | ✓ FLOWING |
| `.planning/v1.6-EVIDENCE.md` rows | uno/leonardo verdict cells (SHAs, divergence, offset) | `_run_state_machine` outputs to disk → operator transcribes into row cells | ✓ Yes (verified by independently re-running sha256sum on the committed run_*.bin files — output matches the row data exactly) | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Consistency-check test suite runs and passes 8 tests | `cd firestarter_app && pytest tests/test_consistency_check.py` | `8 passed in 0.24s` | ✓ PASS |
| Full firestarter_app suite has no regressions | `cd firestarter_app && pytest` | `90 passed in 0.89s` | ✓ PASS |
| Uno bench artifacts reproduce the SUMMARY's PASS claim (3 identical SHAs) | `sha256sum .planning/v1.6/consistency-check-runs/W27C512-uno-20260521-133418/run_*.bin` | All 3 outputs = `8d2124eb7c994f717ace1b2b79c52fa95153aa82c6a4891a323ad924ef409759` — matches the EVIDENCE.md uno-row SHA exactly | ✓ PASS |
| Leonardo bench artifacts reproduce the SUMMARY's FAIL claim (3 distinct SHAs) | `sha256sum .planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_*.bin` | 3 distinct SHAs (`fc4e52ab...`, `c0b842c9...`, `f7892c16...`) | ✓ PASS |
| Leonardo divergence statistics independently reproduce 1349/65536 (2.1%) at offset 0x0003 | Python diff: `[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]` over run_01.bin vs run_02.bin | `1349 / 65536 (2.1%)`, first offset `0x0003`, first 10 offsets `0x0003, 0x0103, 0x01C3, 0x0222, 0x0232, 0x0243, 0x0343, 0x0362, 0x04D0, 0x0552` — matches EVIDENCE.md leonardo-row exactly | ✓ PASS |
| Bench logs match Phase 29 forward-compat regex contract | `grep -E "Consistency check:|Distinct SHAs:|First divergence:|Total divergent" .planning/v1.6/bench-logs/*.log` | All 4 contract substrings present in the leonardo FAIL log; uno PASS log has the PASS substring + `Distinct SHAs: 1` | ✓ PASS |
| Branch invariants honored (D-13) | `git branch --show-current` in meta + each sub-repo | meta=`main`, firestarter_app=`v1.6-read-bug`, firestarter=`beta` (untouched) | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` probes are declared for Phase 26; the PLAN/SUMMARY use pytest as the runnable check. Pytest results captured under "Behavioral Spot-Checks" (8 passing + 90 passing).

| Probe | Command | Result | Status |
|-------|---------|--------|--------|
| (none declared) | — | — | N/A — Phase 26 uses pytest as its runnable check |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REPRO-01 | 26-02 | Operator can reproduce 64KB read-jitter on `uno` (or explicitly prove absence with evidence) | ✓ SATISFIED | PASS verdict captured on Plain Uno (3 identical SHAs at `8d2124eb...`); bench artifacts re-verified during this verification. The ROADMAP's SC#3 language already named PASS as a valid outcome ("explicitly absent with evidence"). |
| REPRO-02 | 26-02 | Operator can reproduce 64KB read-jitter on `leonardo` (or explicitly prove absence) | ✓ SATISFIED | FAIL verdict captured; 1349/65536 (2.1%) divergence reproduced from binaries; first-divergence offset `0x0003` reproduced. |
| REPRO-03 | 26-01 | Reusable consistency-check diagnostic lives in host CLI | ✓ SATISFIED | `firestarter dev consistency-check` shipped at firestarter_app commit `999c3cc`; 8 tests green; full suite 90 green; D-02 passive + D-03 reuse-not-duplicate verified by grep. |

No orphaned requirement IDs found for Phase 26 (REQUIREMENTS.md maps exactly REPRO-01/02/03 to this phase; all three are claimed by 26-01-PLAN.md or 26-02-PLAN.md `requirements_addressed:` frontmatter, and all three close).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter_app/firestarter/eprom_operations.py` | 560 (per 26-REVIEW.md WR-02) | Hardcoded literal `unknown-board` string in verdict stdout | ⚠️ Warning (cosmetic) | The verdict block prints `Board: unknown-board` regardless of which board is plugged in. Not a stub — the verdict and exit code are correct; only the human-readable board label is wrong. Out-of-scope follow-up flagged in REVIEW WR-02 + Plan 26-02 SUMMARY Issue #2; the stdout regex contract for Phase 29 does NOT include the Board cell, so this does not break the cross-phase contract. |
| `firestarter_app/firestarter/eprom_operations.py` | 566-593 (per 26-REVIEW.md WR-01) | Divergence-detail block hardcodes `run_01.bin` vs `run_02.bin` comparison | ⚠️ Warning | A FAIL-with-distinct-SHAs case where run_01 and run_02 happen to be byte-identical but run_03 differs would silently print no divergence detail. Documented in 26-REVIEW.md WR-01 with a fix sketch. Out of v1.6 scope; the actual bench outputs (Plain Uno + Leonardo) do not hit this edge case. |
| All Phase-26-modified files | — | TBD / FIXME / XXX scan | ✓ NONE | `grep -n -E "TBD\|FIXME\|XXX" firestarter_app/firestarter/main.py firestarter_app/firestarter/eprom_operations.py firestarter_app/tests/test_consistency_check.py` returns no unreferenced debt markers. The `.planning/v1.6-EVIDENCE.md` file does contain `DEFERRED` for the uno328pb row, but with an explicit operator-supplied reason and a clear closure condition — not an unreferenced TBD. |

No 🛑 BLOCKER anti-patterns found.

### Scope changes during execution

Two scope-changing findings during Plan 26-02's bench session materially shift the v1.6 milestone landscape. Both are captured in `.planning/v1.6-EVIDENCE.md` §"Scope changes captured during the bench session" and in 26-02-SUMMARY.md §"Deviations from Plan". The verifier confirms they are real (operator-driven, supported by independently-reproducible evidence), not a goal-completion failure:

1. **The board labeled `uno328pb` in v1.5 bench notes is actually a Plain Uno + wrong firmware.** This was an operator clarification mid-session (2026-05-21). Consequence: the original ROADMAP-row goal text "reproduce 64KB read-jitter on all 3 boards (`uno`, `leonardo`, `uno328pb`)" cannot be literally met from this milestone's bench session — there is no true ATmega328PB-silicon board currently flashed with correct firmware on the operator's bench. The uno328pb row in `.planning/v1.6-EVIDENCE.md` is marked DEFERRED with the explicit closure condition ("requires reflash before re-baseline"). Phase 29 (Multi-Board Bench Verification) is the natural follow-on phase that carries this leg forward — its SC#1 + SC#2 specifically require N≥5 consecutive-read byte-identity on `uno`, `leonardo`, AND `uno328pb` post-fix. The deferred row will close at the Phase 29 boundary (or be re-classified if Phase 27 RCA invalidates the need for cross-328PB triage).

2. **Plain Uno result was PASS (expected FAIL per the v1.6 source-bug premise).** 3 byte-identical 64KB reads at SHA-256 `8d2124eb7c994f717ace1b2b79c52fa95153aa82c6a4891a323ad924ef409759`. The plan's Task 2 `<how-to-verify>` explicitly anticipated this case ("PASS (unexpected — refutes pre-existing-bug prediction on uno)"), and the ROADMAP-row SC#3 language already named this outcome as evidence-bearing closure ("If jitter is somehow absent on `uno`, that fact is captured with evidence (would refute the 3-shield-invariance finding and demand RCA scope expansion)"). Combined with finding #1, the v1.6 read-bug premise narrows from "shared transport-side bug across all 3 controllers" to "Leonardo-specific bug" (ATmega32U4 USB-CDC code path; 1024-B DATA_BUFFER vs Uno's 512-B; per-chunk send code on 32U4 silicon). This is **good** evidence — it sharpens Phase 27 RCA scope and reduces fix risk.

**Downstream impact for Phase 27 (RCA):**
- RCA scope narrows to Leonardo-specific code paths. The first-divergence offset `0x0003` is a strong starting bisection point — points at handshake or first-chunk boundary, not mid-stream drift.
- The 2026-05-21 baseline magnitude (~57.8%) attributed to "uno328pb" in `.planning/todos/pending/large-read-data-jitter-uno328pb.md` is NOT comparable to Leonardo's 2.1% — Phase 27 must treat that prior baseline as advisory only, since it was captured on the misidentified board.
- D-03 reuse-not-duplicate is validated empirically: the new tool reproduces a divergence pattern using the exact `_run_state_machine` + `_main_phase_read_data` code path; if Phase 27's fix targets that code path, Phase 29's same-tool verification gates correctly.

### Human Verification Required

_None._ The operator already performed all Plan 26-02 bench tasks (Tasks 2-4) at the bench on 2026-05-21; the resulting evidence is committed and independently reproducible from the binary artifacts. The verifier was able to re-derive every claimed metric (SHA-256s, divergence counts, first-divergence offset, first-10 offsets) from the committed `run_*.bin` files without re-running the diagnostic. No outstanding human action.

The two REVIEW WARNINGs (WR-01 FAIL-without-divergence edge case, WR-02 hardcoded `unknown-board`) are advisory-only follow-ups, not human-verification blockers — they are documented in 26-REVIEW.md and 26-02-SUMMARY.md "Issues Encountered" for future phases.

### Gaps Summary

No gaps blocking phase goal achievement. The single deviation from the literal ROADMAP-row goal ("reproduce on all 3 boards") is documented via the verification override above:

- The "uno328pb" leg is captured as DEFERRED with operator-clarified reason (the board was misidentified in v1.5 bench notes).
- REPRO-01 + REPRO-02 + REPRO-03 — the three requirement IDs Phase 26 was responsible for — all close with reproducible evidence.
- ROADMAP SC#1 (CLI exists with verdict + first-divergence offset) ✓ closed.
- ROADMAP SC#2 (uno328pb jitter matches ~57.8% baseline) — overridden; see frontmatter `overrides:` entry. The original baseline data was itself captured on the same misidentified board.
- ROADMAP SC#3 (uno outcome captured with evidence — "explicitly absent" is a valid outcome) ✓ closed.
- ROADMAP SC#4 (leonardo outcome captured) ✓ closed.
- ROADMAP SC#5 (pre-fix baseline rows for 3 boards) — 2/3 closed; uno328pb row DEFERRED with explicit reason. The forward-annotation HTML comments for Phases 27/28/29 are committed in-file, so the cross-phase contract is preserved.

The v1.6 milestone fix-path is **better-defined** post-Phase-26 than the original ROADMAP premise assumed: Phase 27 RCA can focus on Leonardo + 32U4 code paths rather than searching for a shared-transport bug that no longer matches the empirical picture.

---

*Verified: 2026-05-21*
*Verifier: Claude (gsd-verifier, goal-backward methodology)*

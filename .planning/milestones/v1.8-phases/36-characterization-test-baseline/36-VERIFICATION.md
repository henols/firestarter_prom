---
phase: 36-characterization-test-baseline
verified: 2026-05-27T12:00:00Z
re_verified: 2026-05-27T12:30:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
resolution_note: "Initial verification was human_needed for two advisory code-review items (WR-02, WR-03). Both were fixed in-loop in firestarter_app commit 04cc028 — WR-03 structurally (tests now use EpromDatabase(skip_local_override=True), so they no longer read ~/.firestarter and the bench/CI divergence is eliminated, not merely untestable here); WR-02 by broadening normalize_output's path-root set + Windows drive paths. Full suite re-confirmed green (162 passed, 2 xfailed, 29 snapshots). No human/other-environment testing remains."
---

# Phase 36: Characterization Test Baseline — Verification Report

**Phase Goal:** A comprehensive safety net of characterization tests is committed — pinning the current CLI command surface, serial frame-parse path, and EPROM database layer — so that any behavioral regression introduced by subsequent structural phases is caught immediately. The EpromDatabase singleton is removed to make the DB independently testable. The firmware-contract parity test is extended to cover all COMMAND_*, FLAG_*, and CTRL_* values.

**Verified:** 2026-05-27T12:00:00Z (re-verified 2026-05-27T12:30:00Z)
**Status:** passed
**Re-verification:** Yes — WR-02 and WR-03 fixed in-loop (firestarter_app `04cc028`); see Resolution below

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | EpromDatabase singleton removed; two EpromDatabase() calls return distinct objects | VERIFIED | `database.py`: no `def __new__`, no `_initialized`; `test_two_instances_are_independent` passes; `test_eprom_database.py` confirms `db1 is not db2` |
| 2 | `EpromDatabase(skip_local_override=True)` loads only packaged chip_database.json (production behavior unchanged with default False) | VERIFIED | `database.py:180,192` guard both override merges under `if not skip_local_override:`; 25 occurrences of `skip_local_override=True` in `test_eprom_database.py` |
| 3 | CLI command surface (--help for top-level + all 13 subcommands, DB-backed list/info/search, all usage/parse errors, hardware-absent path) is pinned as committed syrupy snapshots | VERIFIED | 29 snapshots in `tests/__snapshots__/test_characterization.ambr` (1121 lines); `test_characterization.py` passes 35/35 tests; snapshot file not gitignored; `normalize_output()` helper scrubs version strings, /dev/tty*, and absolute paths |
| 4 | Serial frame-parse path (_read_and_parse_lines preamble→body→terminator sequence + sliding-window timeout-reset invariant) is pinned without modifying serial_comm.py | VERIFIED | `test_serial_characterization.py`: 4 tests pass; `test_sliding_window_resets_on_yield` feeds second response after first yield, asserts both yielded; `git diff 6b2687d HEAD -- firestarter/serial_comm.py` is empty |
| 5 | Firmware-contract parity extended to COMMAND_*/FLAG_*/CTRL_* with skipif guard + COMMAND_FW_VERSION==0x0D asserted | VERIFIED | `test_revision_constants_parity.py`: 4 parity tests pass (FW header present in this checkout); `COMMAND_FW_VERSION == 0x0D` at line 112; skipif at lines 73/117/142; FLAG_FORCE, CTRL_* blocks present |

**Score: 5/5 truths verified**

### TEST-05 Deviation Note (documented and acceptable)

REQUIREMENTS.md TEST-05 names two bugs: (a) `build_arg_flags` force attribute-vs-truthiness, and (b) "possibly-missing COMMAND_FW_VERSION in constants.py". During Plan 36-02 execution, COMMAND_FW_VERSION was confirmed PRESENT at `constants.py:39` (= 13 = 0x0D) and folded into the TEST-04 parity assertion (per D-09 in 36-CONTEXT.md).

Plan 36-04 substituted bug (b) with a different genuine latent bug: `EpromOperationError` conflated with `SerialError` in `eprom_operations.py:265` (operator-reported: "app always reports that the communication is broken when the hw returns an error"). This substitution is documented in CONTEXT.md D-08/D-09 and is the correct interpretation of TEST-05's intent — characterizing real latent bugs as bugs (not pinning broken behavior) and binding their fixes to the safety net.

**Assessment:** TEST-05's intent (known latent bugs asserted at corrected behavior, set to trip when fixed) is satisfied. The second bug characterized is more impactful than the original "possibly-missing" framing (the constant was never missing). The deviation is intentional and correctly documented.

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/pyproject.toml` | `[project.optional-dependencies].test` with `pytest>=8.0` and `syrupy>=5.0` | VERIFIED | Lines 62-63: `pytest>=8.0` and `syrupy>=5.0` present; `dev` group unchanged |
| `firestarter_app/firestarter/database.py` | De-singletonized EpromDatabase with skip_local_override seam | VERIFIED | `__init__(self, skip_local_override: bool = False)`; `_initialize_database_core(self, skip_local_override: bool = False)`; no `__new__`, no `_initialized` |
| `firestarter_app/tests/test_revision_constants_parity.py` | Extended firmware-contract parity (COMMAND_*/FLAG_*/CTRL_*) | VERIFIED | 4 tests: original revision test + 3 skipif-guarded blocks for COMMAND/FLAG/CTRL; COMMAND_FW_VERSION == 0x0D asserted |
| `firestarter_app/tests/test_serial_characterization.py` | TEST-02 serial frame-parse + sliding-window timeout pins | VERIFIED | `test_preamble_body_terminator_sequence`, `test_ok_ready_frame_via_get_response`, `test_timeout_raises_on_empty`, `test_sliding_window_resets_on_yield` |
| `firestarter_app/tests/test_characterization.py` | TEST-01 CLI surface goldens (subprocess) + in-process E2E happy paths | VERIFIED | 35 test functions; `normalize_output` helper present; `subprocess.run` used (not CliRunner); `comports` monkeypatched for hardware-absent tests; `make_comm`/`fake_serial` for happy paths |
| `firestarter_app/tests/__snapshots__/test_characterization.ambr` | Committed syrupy snapshots for the CLI surface | VERIFIED | 1121 lines, 29 snapshots; `git check-ignore` returns exit 1 (not gitignored); passes clean without `--snapshot-update` |
| `firestarter_app/tests/test_eprom_database.py` | TEST-03 DB unit tests against real chip_database.json | VERIFIED | 22 tests; `skip_local_override=True` in all 22 data-asserting tests; `get_eprom`, `convert_to_programmer`, DIP->RURP translation covered; no `find_and_connect`, no serial I/O |
| `firestarter_app/tests/test_bug_characterization.py` | TEST-05 two xfail(strict=True) bug pins | VERIFIED | 2 tests; both `xfail(strict=True`); both register as XFAIL (bugs present); `# BUG:` markers citing Phase 41 / Phase 42 present |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `database.py __init__` | `_initialize_database_core` | `skip_local_override` threaded through | WIRED | Line 169: `self._initialize_database_core(skip_local_override=skip_local_override)` |
| `test_eprom_database.py` | `EpromDatabase(skip_local_override=True)` | deterministic construction seam | WIRED | 25 occurrences; all data-asserting tests use the seam |
| `test_revision_constants_parity.py` | firmware hex literals | hard-coded assertions + skipif guard | WIRED | COMMAND_FW_VERSION==0x0D at line 112; skipif on FIRMWARE_HEADER.exists() |
| `test_serial_characterization.py` | `_read_and_parse_lines` (ring-fenced) | external observation via get_response/generator only | WIRED | No import of serial_comm internals; uses `comm._read_and_parse_lines()` and `comm.get_response()` only |
| `test_characterization.py subprocess harness` | installed `firestarter` entry point | `shutil.which` + `subprocess.run`, normalized before snapshot | WIRED | Lines 56-57, 89-106: FIRESTARTER resolved via shutil.which; normalize_output applied |
| `test_bug_characterization.py` | Phase 41 (CLI-03) + Phase 42 (ERR-01) fixes | `xfail(strict=True)` auto-flips to XPASS when fix lands | WIRED | 2 xfail markers present; both tests XFAIL today; strict=True ensures XPASS breaks suite |

---

### GATE-1.8 Standing Gate Assessment

| Gate | Clause | Status | Evidence |
|------|--------|--------|---------|
| GATE-1.8a | Wire protocol byte-identical | VERIFIED | `serial_comm.py` byte-identical to base 6b2687d (empty diff) |
| GATE-1.8b | CLI surface preserved | VERIFIED | 29 committed snapshots pin current surface; test suite passes clean |
| GATE-1.8c | Firmware/app constant contract preserved | VERIFIED | Parity test extended to full COMMAND_*/FLAG_*/CTRL_* surface |
| GATE-1.8d | Read path ring-fenced | VERIFIED | serial_comm.py unmodified; test_serial_characterization.py observes externally only |
| GATE-1.8e | Full test suite green | VERIFIED | 162 passed, 2 xfailed (correct), exit 0 |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full test suite green with 2 xfailed | `python -m pytest tests/ --tb=no` | `162 passed, 2 xfailed in 14.33s` | PASS |
| serial_comm.py byte-identical to base | `git -C /workspaces/firestarter_app diff 6b2687d HEAD -- firestarter/serial_comm.py` | empty (no diff) | PASS |
| Singleton removed (no __new__, no _initialized) | `grep -n 'def __new__\|_initialized' database.py` | no matches | PASS |
| COMMAND_FW_VERSION == 0x0D asserted | `grep 'COMMAND_FW_VERSION.*==.*0x0D' test_revision_constants_parity.py` | line 112 matches | PASS |
| 2 xfail(strict=True) present in bug tests | `grep -c 'xfail(strict=True' test_bug_characterization.py` | 3 (decorator + 2 in docstrings — 2 distinct functions) | PASS |
| Snapshots committed, not gitignored | `git check-ignore tests/__snapshots__/test_characterization.ambr` | exit 1 (not ignored) | PASS |
| 29 snapshots pass without --snapshot-update | `python -m pytest tests/test_characterization.py -q` | `35 passed, 29 snapshots passed` | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| TEST-01 | 36-01, 36-03 | CLI characterization golden tests — surface + happy paths | SATISFIED | 35 tests in test_characterization.py; 29 syrupy snapshots; subprocess harness (D-01 replaces CliRunner since CLI is still argparse) |
| TEST-02 | 36-02 | Serial frame-parse characterization — sequence + sliding-window | SATISFIED | test_serial_characterization.py: 4 tests; preamble→body→terminator + sliding-window invariant pinned |
| TEST-03 | 36-01, 36-04 | EpromDatabase injectable, independently testable | SATISFIED | Singleton removed from database.py; 22 unit tests in test_eprom_database.py; skip_local_override seam functional. Note: "DI via Click context" from REQUIREMENTS.md is deferred to Phase 41 per D-06 (minimal seam only in Phase 36) |
| TEST-04 | 36-02 | Firmware-contract parity extended to COMMAND_*/FLAG_*/CTRL_* | SATISFIED | test_revision_constants_parity.py: 3 new skipif-guarded functions; COMMAND_FW_VERSION==0x0D confirmed present and asserted |
| TEST-05 | 36-04 | Two latent bugs characterized as bugs with xfail(strict=True) | SATISFIED (with documented substitution) | test_bug_characterization.py: 2 xfail(strict=True) tests; bug (a) = build_arg_flags force (as planned); bug (b) substituted from "possibly-missing COMMAND_FW_VERSION" (not actually missing) to comm-error conflation bug per D-08/D-09 |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `tests/test_characterization.py` | 353, 373 | Bare `EpromDatabase()` in `test_no_programmer_found_read/erase` — violated this phase's own MANDATORY `skip_local_override=True` rule | ~~WARNING~~ **RESOLVED** | Fixed in `04cc028`: both tests now construct `EpromDatabase(skip_local_override=True)`, so they no longer read `~/.firestarter` — the CI/bench divergence is structurally eliminated. (WR-03) |
| `tests/test_characterization.py` | 84 | `normalize_output()` path scrubber covered only `/home\|/workspaces\|/tmp\|/Users` — missed `/opt`, `/root`, `/usr`, `/var`, Windows paths | ~~WARNING~~ **RESOLVED** | Fixed in `04cc028`: scrubber broadened to `/home /workspaces /tmp /Users /opt /usr /root /var /private /Library /srv /mnt` + a Windows drive-path rule. Snapshots unchanged (29 still pass — no `/opt`-class paths in devcontainer output). (WR-02) |

No TBD/FIXME/XXX debt markers found in any modified file.

---

### Human Verification — RESOLVED IN-LOOP (no human action required)

Both items the initial verification escalated were code-fixable robustness issues on this
desk-side phase, and were fixed in `firestarter_app` commit `04cc028` (re-verified green):

1. **normalize_output path scrubber (WR-02)** — RESOLVED. The scrubber now covers
   `/home /workspaces /tmp /Users /opt /usr /root /var /private /Library /srv /mnt` plus a
   Windows drive-path rule, so a `pipx`/`/opt`/`/root` or Windows install no longer leaks an
   environment-specific path into the `test_info_known_chip_stderr` snapshot. The committed
   snapshots are unchanged (no `/opt`-class paths exist in devcontainer output), so the fix is
   purely additive coverage — 29 snapshots still pass.

2. **Bench determinism in hardware-absent tests (WR-03)** — RESOLVED structurally.
   `test_no_programmer_found_read/erase` now construct `EpromDatabase(skip_local_override=True)`,
   so they never merge `~/.firestarter/database.json`. The CI/bench divergence is eliminated by
   construction (not merely untestable here), honoring the phase's own MANDATORY rule.

---

### Gaps Summary

No gaps. All 5 must-have truths are VERIFIED; all required artifacts exist and are substantive;
all key links are wired; the full test suite is green (162 passed, 2 xfailed correctly, 29
snapshots, exit 0).

The two advisory code-review warnings (WR-02, WR-03) that initially gated this verification to
`human_needed` were fixed in-loop (`04cc028`) and the suite re-confirmed green — status is now
`passed` with no outstanding human/other-environment verification.

The TEST-05 substitution (COMMAND_FW_VERSION confirmed present → folded into TEST-04; comm-error conflation bug substituted as bug #2) is intentional and correctly documented in CONTEXT.md D-08/D-09. It is not a deviation from the phase goal; it is the correct execution of the goal given the research findings.

---

_Verified: 2026-05-27T12:00:00Z_
_Verifier: Claude (gsd-verifier)_

---
phase: 23-host-cli-installer-integration
plan: 01
subsystem: host-cli
tags: [host-cli, pytest, mocked-github-api, avrdude-mock, uno328pb, tdd-red]
tdd_shape: red
wave: 1
type: execute
requirements: [INST-01, INST-02, INST-03, GATE-01]
requirements_addressed: [INST-01, INST-02, INST-03, GATE-01]
dependency_graph:
  requires: [Phase 18 INST-04 board-string-generic substrate, Phase 21 uno328pb handshake, Phase 22 release-pipeline substrate]
  provides:
    - "5 named pytest contracts pinning uno328pb behavior (TestUno328pbResolution)"
    - "_FakeAvrdude module-local helper (first Avrdude(...) constructor mock in the suite)"
    - "_STABLE_RELEASE_UNO328PB 3-asset stable release fixture"
  affects: [firestarter_app/v1.5-uno328pb, Plan 23-02 GREEN wave]
tech-stack:
  added: []
  patterns:
    - "monkeypatch.setattr(firmware, 'Avrdude', _capture_init) — new mock pattern; first time Avrdude(...) is mocked in the suite"
    - "fail-fast positive + negative argparse assertion (uno328pb accepted + ungabunga rejected) to pin the choices= widening, not removal"
key-files:
  created: []
  modified:
    - firestarter_app/tests/test_firmware_install.py (+257 lines; pure additions, 0 deletions)
decisions:
  - "Honored D-01..D-06 verbatim; D-07 GATE-01 invariant preserved (existing 30 tests + 2 helpers + 2 fixtures byte-identical)"
  - "Honored revised D-10 (widen argparse choices) by writing test 5 against the same `create_firmware_args(sp)` entry point Phase 18's TestArgparseMutex established"
  - "Honored D-19/D-20: commit landed on `firestarter_app/v1.5-uno328pb`; no remote push"
  - "Per RESEARCH Open Q2 + Open Q3 + Pitfall 5: _FakeAvrdude lives in-file (not conftest.py); monkeypatch.setattr(firmware, 'Avrdude', ...) shape works as predicted (verified by execution)"
metrics:
  duration: ~4 min
  duration_seconds: 217
  tasks: 2
  files_modified: 1
  insertions: 257
  deletions: 0
  completed: 2026-05-21T06:22:17Z
  pre_plan_baseline: 77 passed
  post_plan_full_suite: 2 failed, 80 passed (2 RED + 3 GREEN-acceptable + 77 baseline)
  gate_01_subset: 77 passed (-k "not uno328pb")
---

# Phase 23 Plan 01: Host CLI Installer Integration — TDD RED Wave Summary

Five failing pytest contracts pinning the `uno328pb`-board behavior Wave 2 must satisfy, plus the `_FakeAvrdude` helper class and `_STABLE_RELEASE_UNO328PB` 3-asset fixture, landed in a single test-only commit on `firestarter_app/v1.5-uno328pb` with the existing 30-test suite byte-identical (D-07 GATE-01 invariant preserved).

## Decisions Honored

| Decision | Implementation Note |
|----------|---------------------|
| **D-01** (uno328pb elif branch in `_install_with_avrdude`) | Test 4 pins `partno="atmega328pb"`, `programmer_id="arduino"`, `baud_rate=115200` as the contract Wave 2 must satisfy. |
| **D-02** (`programmer_id="arduino"`) | Test 4 asserts `captured["programmer_id"] == "arduino"`. Phase 24 bench may swap to `"urclock"`. |
| **D-03** (`partno="atmega328pb"`) | Test 4 explicitly distinguishes 328PB from 328P with an AssertionError that cites the signature mismatch (`0x1E 0x95 0x16` vs `0x1E 0x95 0x0F`). |
| **D-04** (`baud_rate=115200`) | Test 4 asserts the exact integer. |
| **D-05** (3 release-resolution tests) | Tests 1, 2, 3 cover stable / pre / list paths for `board="uno328pb"`. |
| **D-06** (avrdude profile mock test) | Test 4 = the load-bearing GATE-01 anti-regression anchor; uses `monkeypatch.setattr(firmware, "Avrdude", _capture_init)` per RESEARCH Open Q3 resolution. |
| **D-07** (GATE-01 invariant — existing tests untouched) | `git diff --stat` shows `1 file changed, 257 insertions(+)` — pure additions, 0 deletions or modifications. Existing 30 test methods + 2 helpers + 2 fixtures byte-identical (`grep -E "^-[^-]"` against the diff returns empty). |
| **D-10 (revised)** (widen `--board` argparse `choices=`) | Test 5 exercises the SAME `create_firmware_args(sp)` entry point Phase 18 established in `TestArgparseMutex` (line 1110-1114 of pre-edit file). Positive `args.board == "uno328pb"` + negative `ungabunga → SystemExit` together pin the contract that choices= must be WIDENED (not removed). |
| **D-17 (revised)** (3-file edit surface in firestarter_app) | Wave 1 touches exactly 1 of those 3 files (`tests/test_firmware_install.py`). Firmware.py + main.py edits are Wave 2's scope. |
| **D-19** (commits on `v1.5-uno328pb`) | Sub-repo commit `67c8357` on `firestarter_app/v1.5-uno328pb`. Meta-repo commit on `v1.5-uno328pb` lands with this SUMMARY. |
| **D-20** (no remote push) | Branch stays local until milestone close (post-Phase-25 merge-up). |

## Pre-Wave-2 RED Status (Per-Test)

| # | Test name | Status | Evidence | Wave 2 action required |
|---|-----------|--------|----------|------------------------|
| 1 | `test_uno328pb_stable_path_resolves_correct_asset` | **PASSED** (RED-acceptable) | The v1.4 INST-04 substrate resolves `firestarter_uno328pb.hex` from a 3-asset release purely on the board-string parameter. Pins the contract holds for `board="uno328pb"`. | None — already green. Wave 2 elif branch does not affect resolver. |
| 2 | `test_uno328pb_pre_path_resolves_highest_prerelease` | **PASSED** (RED-acceptable) | Same reason — `fetch_release_info(channel='pre', board='uno328pb')` selects `3.0.1rc1` over `3.0.1b10` / `3.0.1b9` by PEP 440 sort. | None — already green. |
| 3 | `test_uno328pb_list_releases_enumerates_correctly` | **PASSED** (RED-acceptable) | Same reason — `list_releases(channel_filter='all', board='uno328pb')` returns 2 entries in `[3.0.1, 3.0.1b2]` order with all 5 required keys. | None — already green. |
| 4 | `test_uno328pb_avrdude_profile_resolution` | **FAILED (RED)** | `AssertionError: Expected partno='atmega328pb' (328PB signature 0x1E 0x95 0x16); got 'atmega328p'.` Default branch at firmware.py:417-421 hard-codes 328P. | **Wave 2 MUST add the `elif board.lower() == "uno328pb":` branch setting `(atmega328pb, arduino, 115200)` per D-01..D-04.** |
| 5 | `test_argparse_accepts_uno328pb_board_choice` | **FAILED (RED)** | `SystemExit: 2 — __main__.py fw: error: argument -b/--board: invalid choice: 'uno328pb' (choose from uno, leonardo)`. main.py:288-291 `choices=["uno", "leonardo"]` rejects. | **Wave 2 MUST widen choices to `["uno", "uno328pb", "leonardo"]`** (Phase 21 D-08 section-order: uno, uno328pb, leonardo). |

**3 GREEN-acceptable + 2 strictly-RED matches the plan's pre-execution prediction verbatim** (23-01-PLAN.md `<behavior>` for Task 2 expected status section).

## RED-Wave Verification Transcript

```
$ cd /workspaces/firestarter_app && python -m pytest tests/test_firmware_install.py -v -k uno328pb
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.0.3, pluggy-1.6.0
rootdir: /workspaces/firestarter_app
configfile: pyproject.toml
plugins: anyio-4.13.0
collected 35 items / 30 deselected / 5 selected

tests/test_firmware_install.py ...FF                                     [100%]

=== Test 4 failure excerpt (the load-bearing RED) ===
AssertionError: Expected partno='atmega328pb' (328PB signature 0x1E 0x95 0x16); got 'atmega328p'.
The 328P partno would abort avrdude with a signature mismatch on real silicon.
assert 'atmega328p' == 'atmega328pb'

=== Test 5 failure excerpt (argparse choices) ===
__main__.py fw: error: argument -b/--board: invalid choice: 'uno328pb' (choose from uno, leonardo)
SystemExit: 2

=========================== short test summary info ============================
FAILED tests/test_firmware_install.py::TestUno328pbResolution::test_uno328pb_avrdude_profile_resolution
FAILED tests/test_firmware_install.py::TestUno328pbResolution::test_argparse_accepts_uno328pb_board_choice
================== 2 failed, 3 passed, 30 deselected in 0.36s ==================
```

Both failures are real assertion / SystemExit errors — NOT import / collection / fixture errors. The tests genuinely exercise production code paths.

## GATE-01 Non-Regression

```
$ cd /workspaces/firestarter_app && python -m pytest tests/ -k "not uno328pb" -q
........................................................................ [ 93%]
.....                                                                    [100%]
77 passed, 5 deselected in 0.84s
```

Pre-plan baseline: **77 passed**. Post-plan with `-k "not uno328pb"`: **77 passed**. Every pre-Phase-23 test still green. GATE-01 invariant holds bit-for-bit.

## Commits

| Hash | Branch | Files | Description |
|------|--------|-------|-------------|
| `67c8357` | `firestarter_app/v1.5-uno328pb` | `tests/test_firmware_install.py` (+257 / -0) | test(23-01): add 5 RED tests for uno328pb host CLI integration |

`git show --stat 67c8357`:
```
 tests/test_firmware_install.py | 257 +++++++++++++++++++++++++++++++++++++++++
 1 file changed, 257 insertions(+)
```

Single file, pure additions, no deletions. D-07 invariant preserved.

## Hand-Off to Plan 23-02 (GREEN Wave)

Plan 23-02 must turn the 2 RED tests GREEN by:

1. **`firestarter_app/firestarter/firmware.py:422-423`** — insert an `elif board.lower() == "uno328pb":` branch between the existing `leonardo` arm and the implicit `uno` default. Triple = `("atmega328pb", "arduino", 115200)` per D-01..D-04. This turns `test_uno328pb_avrdude_profile_resolution` GREEN.

2. **`firestarter_app/firestarter/main.py:288-291`** — widen `choices=` from `["uno", "leonardo"]` to `["uno", "uno328pb", "leonardo"]` (Phase 21 D-08 section-order discipline). This turns `test_argparse_accepts_uno328pb_board_choice` GREEN.

Plan 23-02 success command: `cd firestarter_app && python -m pytest tests/ -v` shows **82 passed** (= 77 baseline + 5 uno328pb). No flakies, no skips.

| Test (RED today) | Wave 2 edit that turns it GREEN | Requirement |
|------------------|----------------------------------|-------------|
| `test_uno328pb_avrdude_profile_resolution` | `firmware.py:422-423` elif branch | INST-01 + GATE-01 anchor |
| `test_argparse_accepts_uno328pb_board_choice` | `main.py:288-291` choices widening | INST-03 + D-10 (revised) |

## Surprises / Deviations

**None.** The plan executed exactly as written. Specifically:

- **`create_firmware_args(sp)` entry point name matched the plan's prediction.** No fallback search needed.
- **`monkeypatch.setattr(firmware, "Avrdude", _capture_init)` pattern worked first-try.** RESEARCH Open Q3 / Assumption A2 verified at execution time — no need for `unittest.mock.patch("firestarter.firmware.Avrdude")` fallback. The module-level import at `firmware.py:30` (`from .avr_tool import Avrdude`) binds `Avrdude` as a module attribute; the production call site at `firmware.py:472` resolves it against the `firmware` module's namespace; the monkeypatch replaces that bound name cleanly.
- **`_FakeAvrdude` minimum-viable surface (4 instance attrs + `command="/fake/avrdude"` + `config=None` + `flash_firmware() -> ("", 0)`)** is exactly enough to drive `_install_with_avrdude` to the success branch (lines 482-497), reach the `config_manager.set_value("avrdude-path", avrdude.command)` save (line 492), and skip the `if avrdude.config:` branch (line 493). No AttributeError surfaced in execution. RESEARCH Pitfall 5 cleared.
- **Tests 1-3 PASSING green pre-Wave-2 is acceptable per the plan** (`<behavior>` for Task 2 line 250-253). They pin the contract that v1.4's board-string-generic substrate already extends to `uno328pb` without code change. Wave 2's elif branch does NOT touch the resolver — it only touches `_install_with_avrdude`. Tests 1-3 will continue passing green; they remain regression-protection.
- **All acceptance criteria for Tasks 1 and 2 passed verbatim**, including the strict counts: 5 collected with `-k uno328pb`, 2+ FAILED, 77 passed with `-k "not uno328pb"`, 8 total Test* classes (7 existing + 1 new — no rename), 1 file touched in commit.

## Authentication Gates

None — Wave 1 is a pure code edit + mocked test run. No network, no avrdude binary invocation, no real silicon.

## Self-Check: PASSED

- File `firestarter_app/tests/test_firmware_install.py` exists and contains `class TestUno328pbResolution` at line 1124. **FOUND**
- File contains `class _FakeAvrdude:` at line 69. **FOUND**
- File contains `_STABLE_RELEASE_UNO328PB = {` at line 126. **FOUND**
- `git log` on `firestarter_app/v1.5-uno328pb` contains commit `67c8357` titled `test(23-01): add 5 RED tests for uno328pb host CLI integration`. **FOUND** (`git log --oneline -1 67c8357` confirms).
- `pytest -v -k uno328pb` shows 5 selected, 2 failed (test 4 + test 5), 3 passed (tests 1+2+3). **FOUND**.
- `pytest -k "not uno328pb"` shows 77 passed. **FOUND**.
- D-07 byte-identity: `git diff HEAD~1 HEAD -- tests/test_firmware_install.py | grep -E "^-[^-]"` returns empty. **VERIFIED**.

## TDD Gate Compliance

Plan-level `tdd_shape: red` honored: a `test(23-01): ...` commit exists (RED gate). The GREEN gate (`feat(23-02): ...`) lands in Plan 23-02. No REFACTOR commit needed for this wave.

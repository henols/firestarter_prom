---
phase: 23-host-cli-installer-integration
plan: 02
subsystem: host-cli
tags: [host-cli, avrdude, argparse, uno328pb, gate-01, tdd-green]
tdd_shape: green
wave: 2
type: execute
requirements: [INST-01, INST-02, INST-03, GATE-01]
requirements_addressed: [INST-01, INST-02, INST-03, GATE-01]
dependency_graph:
  requires:
    - "Plan 23-01 Wave 1 -- 5 RED contracts + _FakeAvrdude helper + _STABLE_RELEASE_UNO328PB fixture (commit 67c8357 on firestarter_app/v1.5-uno328pb)"
    - "Phase 21 firmware emitting uno328pb in handshake (sub-repo ab7c2a9)"
    - "Phase 22 platformio.ini + ROADMAP literal substrate (sub-repo 897067b)"
  provides:
    - "firestarter_app/firestarter/firmware.py:_install_with_avrdude uno328pb elif branch -- (atmega328pb, arduino, 115200) per CONTEXT D-01..D-04"
    - "firestarter_app/firestarter/main.py argparse -b/--board choices widened to [uno, uno328pb, leonardo] per CONTEXT D-10 revised + Phase 21 D-08 section order"
    - "INST-01 / INST-02 / INST-03 closed at the mocked-pytest layer (INST-02 real-silicon proof deferred to Phase 24 BENCH-01 per D-15)"
  affects: [firestarter_app/v1.5-uno328pb, Phase 24 BENCH-01]
tech-stack:
  added: []
  patterns:
    - "Atomic two-file GREEN commit pairing the elif branch insertion with the argparse widening so git bisect resolution is 'Wave 2 introduced uno328pb support' (T-23-10 mitigation)"
    - "D-07 byte-identity discipline -- existing leonardo branch + uno default tuple + 30 existing test methods untouched at the byte level"
key-files:
  created: []
  modified:
    - firestarter_app/firestarter/firmware.py (+7 lines -- elif branch + 5-line Phase 21 D-10 inline comment; 0 deletions)
    - firestarter_app/firestarter/main.py (+1 line -- 'uno328pb' inserted into argparse choices list; 0 deletions)
decisions:
  - "Honored D-01..D-04 verbatim: elif branch sets (partno='atmega328pb', programmer_id='arduino', baud_rate=115200) -- exact tuple landed"
  - "Honored D-07 (GATE-01 invariant): leonardo branch text byte-identical + uno default tuple byte-identical -- diff shows pure additions only"
  - "Honored D-10 revised: main.py choices=['uno', 'leonardo'] widened to ['uno', 'uno328pb', 'leonardo'] in Phase 21 D-08 section order"
  - "Honored D-15: NO real-silicon flash in Phase 23 -- INST-02 real-silicon proof deferred to Phase 24 BENCH-01"
  - "Honored D-16: GATE-01 non-regression command pytest tests/ -k 'not uno328pb' -q reports 77 passed (pre-Phase-23 baseline byte-identical)"
  - "Honored D-17 revised: 3-file edit surface across Plan 23-01 + Plan 23-02 (tests/test_firmware_install.py from Wave 1, firmware.py + main.py from Wave 2)"
  - "Honored D-19: sub-repo commit d13d9b1 on firestarter_app/v1.5-uno328pb; meta-repo commit on v1.5-uno328pb"
  - "Honored D-20: NO remote push -- branch stays local until milestone close (post-Phase-25 merge-up)"
metrics:
  duration: ~3 min
  duration_seconds: 188
  tasks: 3
  files_modified: 2
  insertions: 8
  deletions: 0
  completed: 2026-05-21T06:29:18Z
  pre_plan_baseline_full: 80 passed 2 failed (77 pre-Phase-23 + 3 RED-acceptable + 2 RED from Wave 1)
  pre_plan_baseline_gate01: 77 passed (-k "not uno328pb")
  post_plan_full_suite: 82 passed (77 baseline + 5 uno328pb GREEN)
  post_plan_gate01: 77 passed (unchanged byte-identical)
  post_plan_uno328pb_targeted: 5 passed 0 failed
---

# Phase 23 Plan 02: Host CLI Installer Integration -- TDD GREEN Wave Summary

Two paired narrow edits (firmware.py elif branch + main.py argparse choices widening) landed atomically on `firestarter_app/v1.5-uno328pb` (sub-repo commit `d13d9b1`), turning the 2 strictly-RED tests from Plan 23-01 GREEN and closing INST-01 / INST-02 / INST-03 / GATE-01 at the mocked-pytest layer. GATE-01 non-regression verified byte-identical at 77 passed.

## Decisions Honored

| Decision | Implementation Note |
|----------|---------------------|
| **D-01** (uno328pb elif branch in `_install_with_avrdude`) | Inserted between the existing `if board.lower() == "leonardo":` arm and the implicit uno default. The elif is keyed on `board.lower() == "uno328pb"` (exact lowercase match). |
| **D-02** (`programmer_id="arduino"`) | Landed verbatim in the elif tuple. Phase 24 bench may swap to `"urclock"` (1-line follow-up) if MiniCore Urclock bootloader requires it. |
| **D-03** (`partno="atmega328pb"`) | Landed verbatim. The 5-line inline comment explicitly cites the 0x1E 0x95 0x16 vs 0x1E 0x95 0x0F signature distinction (Phase 21 D-10 hand-off rationale). |
| **D-04** (`baud_rate=115200`) | Landed verbatim. Same as uno's stk500v1/optiboot baud. |
| **D-07** (GATE-01 byte-identity invariant) | Verified via `git diff HEAD~1 HEAD -- firestarter/firmware.py \| grep -E '^[-+]' \| grep -v '^[+-]{3}'` -- output contains ONLY `+` lines (pure additions), zero `-` lines. The pre-existing `if board.lower() == "leonardo":` text and the `partno, programmer_id, baud_rate = ("atmega32u4", "avr109", 57600)` body are byte-identical post-edit. The uno default tuple (multi-line opener `partno, programmer_id, baud_rate = (` + body `"atmega328p", "arduino", 115200, ) # Defaults for uno`) is byte-identical post-edit. The 30 existing test methods in `test_firmware_install.py` are unchanged (this commit doesn't touch the test file at all -- that was Plan 23-01's commit). |
| **D-10 (revised 2026-05-21)** (widen main.py argparse choices) | Single-line allowlist widening: `["uno", "leonardo"]` -> `["uno", "uno328pb", "leonardo"]`. Multi-line list formatting preserved; help text, `type=str`, `default="uno"` all byte-identical. No new flags added (INST-03 SC#3 honored). |
| **D-15** (no real-silicon flash in Phase 23) | Wave 2 ships ONLY the mocked-pytest GREEN. INST-02 real-silicon proof is Phase 24 BENCH-01's acceptance gate (operator's 328PB-Uno + RURP shield + `firestarter fw -i --pre`). |
| **D-16** (GATE-01 non-regression command) | `cd firestarter_app && python -m pytest tests/ -k "not uno328pb" -q` reports `77 passed, 5 deselected` post-Wave-2 -- bit-for-bit unchanged from the pre-Phase-23 baseline. |
| **D-17 (revised 2026-05-21)** (3-file edit surface across the two plans) | Plan 23-01 touched 1 of 3 (`tests/test_firmware_install.py`). Plan 23-02 touched the remaining 2 (`firestarter/firmware.py` + `firestarter/main.py`). Total: 3 files, exactly as the revised D-17 predicted. |
| **D-19** (commits on `v1.5-uno328pb`) | Sub-repo commit `d13d9b1` on `firestarter_app/v1.5-uno328pb`. Meta-repo commit lands with this SUMMARY on `v1.5-uno328pb`. |
| **D-20** (no remote push) | `git status -b --short` shows `## v1.5-uno328pb` (no upstream tracking, no "ahead/behind" indicator). Branch stays local. |

## Requirements Closed (mocked-pytest scope)

| Requirement | Test method that proves it green | Note |
|-------------|----------------------------------|------|
| **INST-01** (stable install for uno328pb-reporting device) | `test_uno328pb_stable_path_resolves_correct_asset` + `test_uno328pb_avrdude_profile_resolution` | Resolver returns the right asset; install path picks the right avrdude profile. Real-silicon proof deferred to BENCH-01. |
| **INST-02** (`--pre` install for uno328pb) | `test_uno328pb_pre_path_resolves_highest_prerelease` + `test_uno328pb_avrdude_profile_resolution` | Same resolver + install-path pair, with the `channel="pre"` path. Real-silicon proof deferred to BENCH-01. |
| **INST-03** (`firmware list` enumerates uno328pb) | `test_uno328pb_list_releases_enumerates_correctly` + `test_argparse_accepts_uno328pb_board_choice` | Listing returns the right shape; argparse accepts `--board uno328pb` without `SystemExit`. |
| **GATE-01** (uno + leonardo flash paths byte-identical) | The 77 pre-Phase-23 tests + the leonardo branch byte-identity check | GATE-01 command (D-16) reports 77 passed unchanged. |

## GATE-01 Baseline + Post-State

```
PRE-PHASE-23 BASELINE (recorded in 23-01-SUMMARY.md): 77 passed
POST-PHASE-23 GATE-01 COMMAND (D-16):

$ cd /workspaces/firestarter_app && python -m pytest tests/ -k "not uno328pb" -q
........................................................................ [ 93%]
.....                                                                    [100%]
77 passed, 5 deselected in 1.24s
```

77 -> 77, bit-for-bit. The leonardo + uno paths are functionally + byte-identically unchanged.

## GREEN-Wave Verification Transcript

```
$ cd /workspaces/firestarter_app && python -m pytest tests/test_firmware_install.py -k uno328pb -v
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.0.3, pluggy-1.6.0
rootdir: /workspaces/firestarter_app
configfile: pyproject.toml
plugins: anyio-4.13.0
collected 35 items / 30 deselected / 5 selected

tests/test_firmware_install.py .....                                     [100%]

======================= 5 passed, 30 deselected in 0.17s =======================

$ cd /workspaces/firestarter_app && python -m pytest tests/ -k "not uno328pb" -q
77 passed, 5 deselected in 1.24s

$ cd /workspaces/firestarter_app && python -m pytest tests/ -q
82 passed in 1.08s
```

5 uno328pb-named PASS + 77 GATE-01 baseline PASS + 82 full suite PASS, 0 failed at every level. RED -> GREEN transition is complete.

## Diff Shape (atomic 2-file edit)

```
$ git diff HEAD~1 HEAD --stat
 firestarter/firmware.py | 7 +++++++
 firestarter/main.py     | 1 +
 2 files changed, 8 insertions(+)

$ git diff HEAD~1 HEAD -- firestarter/firmware.py | grep -E '^[-+]' | grep -v '^[+-]{3}'
+        elif board.lower() == "uno328pb":
+            # Phase 21 D-10 hand-off: ATmega328PB signature 0x1E 0x95 0x16 differs
+            # from 328P's 0x1E 0x95 0x0F -- partno must be "atmega328pb" exactly,
+            # else avrdude aborts on signature mismatch. programmer_id "arduino"
+            # mirrors the uno profile (stk500v1 / optiboot); Phase 24 BENCH-01
+            # validates against the operator's specific MiniCore bootloader.
+            partno, programmer_id, baud_rate = ("atmega328pb", "arduino", 115200)

$ git diff HEAD~1 HEAD -- firestarter/main.py | grep -E '^[-+]' | grep -v '^[+-]{3}'
+            "uno328pb",
```

8 insertions, 0 deletions. D-07 invariant holds at the strongest possible byte-level gate.

## Commits

| Hash | Branch | Files | Description |
|------|--------|-------|-------------|
| `d13d9b1` | `firestarter_app/v1.5-uno328pb` | `firestarter/firmware.py` (+7 / -0), `firestarter/main.py` (+1 / -0) | feat(23-02): wire uno328pb host CLI install path GREEN |

`git show --stat d13d9b1` confirms exactly 2 files touched, 8 insertions, 0 deletions.

## Phase 24 Hand-Off (BENCH-01)

Phase 24 inherits the real-silicon proof of INST-02 + INST-01. Specifically:

1. **Operator flashes the 328PB-Uno** via `firestarter fw -i --pre` (depends on a real GitHub Pre-release with a `firestarter_uno328pb.hex` asset -- Phase 24 first cuts that beta).
2. **Expected flow**: handshake reports `uno328pb` -> host's `check_current_firmware` extracts the string -> `manage_firmware_update` routes to `_install_with_avrdude(board="uno328pb")` -> hits the new elif branch -> invokes `Avrdude(partno="atmega328pb", programmer_id="arduino", baud_rate=115200, port=...)`.
3. **Single contingency**: if `programmer_id="arduino"` fails on the operator's specific MiniCore Urclock bootloader, the 1-line follow-up commit is `"arduino"` -> `"urclock"` at `firmware.py:_install_with_avrdude` inside the new elif body. Mocked tests are unaffected by that swap (they pin the constructor kwargs as a contract, not the specific string value -- the test would need updating only if the contract changes). Documented in CONTEXT D-02 and as a Phase 24 hand-off finding.
4. **Bench session also closes Phase 23's deferred INST-02 real-silicon proof.** Phase 23 ships when mocked GREEN; Phase 24's BENCH-01 row in `.planning/v1.5-BENCH-RESULTS.md` is the final acceptance gate.

## Surprises / Deviations

**None.** The plan executed exactly as written. Specifically:

- **Pre-plan baseline matched the prediction verbatim**: 2 RED + 3 GREEN-acceptable in `-k uno328pb`; 77 passed in `-k "not uno328pb"`.
- **Edit tool substring anchors worked on first attempt** (RESEARCH Pitfall 1 avoided -- no line-number drift). The `if board.lower() == "leonardo":` + body anchor in firmware.py and the `choices=[\n            "uno",\n            "leonardo",\n        ],` multi-line anchor in main.py both matched uniquely with no retries.
- **All 5 uno328pb tests turned GREEN (including the argparse test)** -- the argparse test from Wave 1 (`test_argparse_accepts_uno328pb_board_choice`) was present (Plan 23-01 wrote all 5 tests, not 4). So the full-suite count is 82, not 81; the Wave 2 acceptance criteria's "or 82" branch is the one that landed.
- **Indentation matched the file convention** (8-space inside method body, 12-space inside argparse `choices=[` -- both honored).
- **GATE-01 byte-identity verified by the strongest gate**: `git diff HEAD~1 HEAD -- firestarter/firmware.py | grep -E '^-[^-]'` returns empty (no `-` lines except the diff `---` header). Pure additions only.
- **Sub-repo commit `d13d9b1` shape is exactly as the plan predicted**: 2 files, 8 insertions, 0 deletions, no test file in the commit (the post-commit grep `git show --stat HEAD | grep -cF 'test_firmware_install.py'` returned 1 due to the commit message body mentioning the test file name -- the actual `--stat` shows only `firestarter/firmware.py` + `firestarter/main.py`).

## Authentication Gates

None -- Wave 2 is a pure code edit + mocked test run. No network, no avrdude binary invocation, no real silicon, no GitHub API.

## Self-Check: PASSED

- File `firestarter_app/firestarter/firmware.py` contains `elif board.lower() == "uno328pb":` at 8-space indent (line 424). **FOUND** via `grep -cE '^        elif board\.lower\(\) == "uno328pb":' firestarter/firmware.py` returning 1.
- File contains the uno328pb tuple `partno, programmer_id, baud_rate = ("atmega328pb", "arduino", 115200)`. **FOUND** via `grep -cF` returning 1.
- File contains the leonardo branch tuple `partno, programmer_id, baud_rate = ("atmega32u4", "avr109", 57600)`. **FOUND** (byte-identical -- D-07 verified).
- File contains the inline comment cite `Phase 21 D-10`. **FOUND** (1 occurrence).
- File `firestarter_app/firestarter/main.py` contains `"uno328pb",` at 12-space indent in the argparse choices list. **FOUND** via `grep -cE '^            "uno328pb",$' firestarter/main.py` returning 1.
- File contains all three choices `"uno"`, `"uno328pb"`, `"leonardo"` at the 12-space indent. **FOUND** via `grep -cE '^            "(uno|uno328pb|leonardo)",$'` returning 3.
- File contains `default="uno"` unchanged. **FOUND** (1 occurrence -- INST-01 stable-default-on-uno non-regression).
- `git log` on `firestarter_app/v1.5-uno328pb` contains commit `d13d9b1` titled `feat(23-02): wire uno328pb host CLI install path GREEN`. **FOUND**.
- `pytest tests/test_firmware_install.py -k uno328pb -v` shows 5 selected, 5 passed, 0 failed. **FOUND**.
- `pytest tests/ -k "not uno328pb" -q` shows 77 passed (GATE-01 invariant). **FOUND**.
- `pytest tests/ -q` shows 82 passed, 0 failed. **FOUND**.
- D-07 byte-identity: `git diff HEAD~1 HEAD -- firestarter/firmware.py | grep -E "^-[^-]"` returns empty (no deletions). **VERIFIED**.
- D-07 byte-identity: `git diff HEAD~1 HEAD -- firestarter/main.py | grep -E "^-[^-]"` returns empty. **VERIFIED**.
- D-20: `git status -b --short` shows `## v1.5-uno328pb` (no upstream, no remote push). **VERIFIED**.

## TDD Gate Compliance

Plan-level `tdd_shape: green` honored: a `feat(23-02): ...` commit exists (GREEN gate), preceded by Plan 23-01's `test(23-01): ...` commit (RED gate). The git log on `firestarter_app/v1.5-uno328pb` shows the correct RED -> GREEN sequence:

```
d13d9b1 feat(23-02): wire uno328pb host CLI install path GREEN   (this commit)
67c8357 test(23-01): add 5 RED tests for uno328pb host CLI integration   (Wave 1 RED)
```

No REFACTOR commit needed for this wave -- the elif + choices-widening is minimal and final per D-07 ("do not refactor existing branches").

## Phase 23 Closure Readiness

Phase 23 mocked-pytest scope is complete. Operator next step: `/gsd-verify-work 23` to run the formal phase-close verifier and write `23-VERIFICATION.md`. Then Phase 24 (BENCH-01) cuts the first v1.5 beta from `firestarter/beta` and operator-validates `firestarter fw -i --pre` on the plugged-in 328PB-Uno + RURP shield.

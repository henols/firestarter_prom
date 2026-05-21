---
phase: 23-host-cli-installer-integration
verified: 2026-05-21T07:00:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
roadmap_sc_score: 5/5
requirements_score: 4/4
---

# Phase 23: Host CLI Installer Integration — Verification Report

**Phase Goal:** `firestarter fw -i`, `firestarter fw -i --pre`, and `firestarter firmware list` flow through the existing v1.4 board-driven asset-resolution path cleanly when the connected device's firmware handshake reports `uno328pb`. Any allowlist entry needed (e.g. in `avr_tool.py` upload profile or `constants.py` enum) is added; a regression test exercises the `uno328pb`-reporting code path.

**Verified:** 2026-05-21
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria + PLAN must_haves merged)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC#1 | With a `uno328pb`-reporting firmware (or mocked), `firestarter fw -i` resolves the latest stable `firestarter_uno328pb.hex` asset URL via `fetch_release_info(board="uno328pb")` and `_install_with_avrdude` flashes it with a 328PB-compatible upload profile | VERIFIED | `test_uno328pb_stable_path_resolves_correct_asset` PASS (returns `("3.0.1", url)` with `uno328pb_stable.hex in url`); `test_uno328pb_avrdude_profile_resolution` PASS (constructor receives `partno="atmega328pb"`, `programmer_id="arduino"`, `baud_rate=115200`); runtime spot-check below confirms `_install_with_avrdude(board="uno328pb")` routes to the new elif branch and yields `ok=True` |
| SC#2 | `firestarter fw -i --pre` resolves the highest PEP 440 pre-release's `firestarter_uno328pb.hex` asset URL and flashes it | VERIFIED (mocked-pytest scope; real-silicon proof deferred to Phase 24 BENCH-01 per CONTEXT D-15) | `test_uno328pb_pre_path_resolves_highest_prerelease` PASS (`rc1 > b10 > b9` selection proves PEP 440 sort, not lex); same `_install_with_avrdude` elif branch handles the flash leg, identical to SC#1 |
| SC#3 | `firestarter firmware list [--all|--pre|--stable]` enumerates `uno328pb` releases with the same plain-text/JSON table shape as for `uno`/`leonardo` | VERIFIED | `test_uno328pb_list_releases_enumerates_correctly` PASS (`list_releases(channel_filter="all", board="uno328pb")` returns 2 entries `[3.0.1 stable, 3.0.1b2 pre]` in PEP 440 desc order, all 5 required keys `{version, tag, channel, published, asset_url}`, every `asset_url` contains `"uno328pb"`); `test_argparse_accepts_uno328pb_board_choice` PASS (argparse accepts `--board uno328pb`, still rejects `ungabunga`); runtime spot-check confirms `args.board == "uno328pb"` |
| SC#4 | A new pytest case (or extension) covers the `uno328pb`-reporting code path end-to-end with mocked GitHub responses; existing `uno`/`leonardo` test cases remain green | VERIFIED | 5 new tests in `class TestUno328pbResolution` (lines 1124-1325 of `tests/test_firmware_install.py`); `pytest -k uno328pb` = 5 passed / 0 failed; `pytest -k "not uno328pb"` = 77 passed / 0 failed (every pre-Phase-23 test still green) |
| SC#5 | GATE-01 non-regression: with `uno`/`leonardo`-reporting firmware, `firestarter fw -i` and `firestarter fw -i --pre` flash the matching `.hex` with byte-identical behavior to pre-v1.5 | VERIFIED | Cross-board runtime spot-check below shows `uno → (atmega328p, arduino, 115200)`, `leonardo → (atmega32u4, avr109, 57600)`, `uno328pb → (atmega328pb, arduino, 115200)`. Leonardo branch line + uno default tuple are byte-identical post-edit (`git diff 5bb1766 d13d9b1 -- firestarter/firmware.py | grep -E "^-[^-]"` returns empty — pure additions only); `pytest -k "not uno328pb"` shows 77 passed unchanged from pre-Phase-23 baseline (D-16 GATE-01 invariant) |

**Score:** 5/5 ROADMAP Success Criteria verified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/firmware.py` | `_install_with_avrdude` gains `elif board.lower() == "uno328pb":` branch with `("atmega328pb", "arduino", 115200)` tuple (D-01..D-04) | VERIFIED | Line 424: `elif board.lower() == "uno328pb":` followed by 5-line Phase 21 D-10 hand-off comment (lines 425-429) and assignment at line 430. Leonardo branch (line 423) byte-identical; uno default tuple (lines 417-421) byte-identical |
| `firestarter_app/firestarter/main.py` | argparse `-b/--board` `choices=` widened from `["uno", "leonardo"]` to `["uno", "uno328pb", "leonardo"]` (Phase 21 D-08 section order) | VERIFIED | Lines 288-292 show the 3-entry multi-line choices list in correct section order; `default="uno"` unchanged at line 287 |
| `firestarter_app/tests/test_firmware_install.py` | New `class TestUno328pbResolution` with 5 test methods, `_FakeAvrdude` helper, `_STABLE_RELEASE_UNO328PB` fixture | VERIFIED | `_FakeAvrdude` at line 69; `_STABLE_RELEASE_UNO328PB` at line 126; `class TestUno328pbResolution` at line 1124; 5 methods with `uno328pb` in name; 30 existing test methods byte-identical (no deletions in diff) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `_install_with_avrdude(board="uno328pb")` | `firmware.Avrdude(partno="atmega328pb", programmer_id="arduino", baud_rate=115200, ...)` | tuple unpack into constructor kwargs | WIRED | Runtime spot-check (below) confirms the elif branch is reached and the captured kwargs are exactly the expected tuple |
| `main.py fw_parser -b/--board choices` | `args.board` passed to `list_releases(board=args.board)` / `fetch_release_info(board=args.board)` | argparse validation gate | WIRED | `python -c "...create_firmware_args... p.parse_args(['fw', '--list', '--board', 'uno328pb'])"` yields `args.board='uno328pb'` |
| Phase 21 firmware handshake `<board>="uno328pb"` | `serial_comm.py` extract → `firmware.py:check_current_firmware` → `_install_with_avrdude(board="uno328pb")` | board-string-generic substrate (v1.4 INST-04) | WIRED | Substrate verified by Phase 18 + Phase 21 hand-off; Phase 23 only adds the missing AVR-side branch (D-08, D-09, D-11 confirm constants.py / avr_tool.py / serial_comm.py untouched) |

### Behavioral Spot-Checks (run by verifier)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full pytest suite green | `python -m pytest tests/ -v` | 82 passed in 0.87s, 0 failed | PASS |
| uno328pb-targeted tests green | `python -m pytest tests/ -v -k uno328pb` | 5 passed, 0 failed (77 deselected) | PASS |
| GATE-01 non-regression baseline | `python -m pytest tests/ -v -k "not uno328pb"` | 77 passed, 0 failed (5 deselected) — matches pre-Phase-23 baseline byte-for-byte | PASS |
| Argparse accepts uno328pb | `p.parse_args(["fw", "--list", "--board", "uno328pb"])` | `args.board == 'uno328pb'`; uno and leonardo also still accepted | PASS |
| Avrdude profile resolution: uno → atmega328p | `_install_with_avrdude(board="uno")` runtime probe | `partno='atmega328p', programmer_id='arduino', baud_rate=115200` (byte-identical to v1.4) | PASS |
| Avrdude profile resolution: leonardo → atmega32u4 | `_install_with_avrdude(board="leonardo")` runtime probe | `partno='atmega32u4', programmer_id='avr109', baud_rate=57600` (byte-identical to v1.4) | PASS |
| Avrdude profile resolution: uno328pb → atmega328pb | `_install_with_avrdude(board="uno328pb")` runtime probe | `partno='atmega328pb', programmer_id='arduino', baud_rate=115200` + `ok=True` returned | PASS |

### Forbidden-Edit Surface Audit (CONTEXT D-08..D-13, D-18)

| Forbidden file | Expected | Actual | Status |
|----------------|----------|--------|--------|
| `firestarter_app/firestarter/constants.py` | Unchanged | Not in `git diff 5bb1766..d13d9b1` | VERIFIED |
| `firestarter_app/firestarter/avr_tool.py` | Unchanged | Not in `git diff 5bb1766..d13d9b1` | VERIFIED |
| `firestarter_app/firestarter/serial_comm.py` | Unchanged | Not in `git diff 5bb1766..d13d9b1` | VERIFIED |
| `firestarter_app/firestarter/__init__.py` | Unchanged | Not in `git diff 5bb1766..d13d9b1` | VERIFIED |
| `firestarter_app/setup.py`, `pyproject.toml` | Unchanged | Not in `git diff 5bb1766..d13d9b1` | VERIFIED |
| `firestarter_app/README.md` | Unchanged | Not in `git diff 5bb1766..d13d9b1` | VERIFIED |
| Firmware sub-repo `firestarter/**` | HEAD == Phase 22 final `897067b` | `git -C /workspaces/firestarter rev-parse HEAD` = `897067b9edf0ca280fd8fb1a492aabf7cb3a69dd` | VERIFIED |
| Any test file other than `test_firmware_install.py` | Unchanged | `git diff 5bb1766..d13d9b1 -- 'tests/*.py' --name-only` = `tests/test_firmware_install.py` only | VERIFIED |

### Branch / Push Discipline (CONTEXT D-19, D-20)

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Sub-repo branch | `v1.5-uno328pb` | `git branch --show-current` = `v1.5-uno328pb` | VERIFIED |
| Meta-repo branch | `v1.5-uno328pb` | meta-repo on `v1.5-uno328pb` | VERIFIED |
| Sub-repo upstream tracking | none (no remote push per D-20) | `git status -b --short` shows `## v1.5-uno328pb` with no `[origin/...]` marker; `git log origin/v1.5-uno328pb` returns `fatal: ambiguous argument 'origin/v1.5-uno328pb': unknown revision` | VERIFIED |
| Wave 1 commit hash | `67c8357` | `git log --oneline -5` confirms `67c8357 test(23-01): add 5 RED tests for uno328pb host CLI integration` | VERIFIED |
| Wave 2 commit hash | `d13d9b1` | `git log --oneline -5` confirms `d13d9b1 feat(23-02): wire uno328pb host CLI install path GREEN` | VERIFIED |
| Edit surface exactly 3 files | `firestarter/firmware.py`, `firestarter/main.py`, `tests/test_firmware_install.py` | `git diff 5bb1766 d13d9b1 --name-only` = exactly those 3 | VERIFIED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| INST-01 | 23-01-PLAN, 23-02-PLAN | Stable install for uno328pb-reporting device: resolves `firestarter_uno328pb.hex` asset, flashes via 328PB-appropriate profile | SATISFIED (mocked-pytest scope; real-silicon proof deferred to BENCH-01 per D-15) | `test_uno328pb_stable_path_resolves_correct_asset` + `test_uno328pb_avrdude_profile_resolution` both PASS; runtime spot-check confirms tuple `("atmega328pb", "arduino", 115200)` |
| INST-02 | 23-01-PLAN, 23-02-PLAN | `--pre` install for uno328pb: resolves highest PEP 440 pre-release | SATISFIED (mocked-pytest scope; real-silicon proof deferred to BENCH-01 per D-15) | `test_uno328pb_pre_path_resolves_highest_prerelease` PASS; same install path as INST-01 |
| INST-03 | 23-01-PLAN, 23-02-PLAN | `firestarter firmware list` enumerates uno328pb releases, no new flags | SATISFIED | `test_uno328pb_list_releases_enumerates_correctly` + `test_argparse_accepts_uno328pb_board_choice` both PASS; `--board` choices widened (not new flag); `default="uno"` byte-identical (INST-01 stable-default-on-uno-reporting-device non-regression) |
| GATE-01 | 23-01-PLAN, 23-02-PLAN | uno + leonardo flash paths byte-identical | SATISFIED | `pytest -k "not uno328pb"` = 77 passed unchanged; leonardo branch + uno default tuple byte-identical (git diff shows pure additions only); cross-board runtime spot-checks return identical tuples to v1.4 |

**Coverage:** 4/4 requirements satisfied at mocked-pytest scope. No orphaned requirement IDs — all four IDs declared in both PLAN frontmatters are present in REQUIREMENTS.md Traceability table mapped to Phase 23, and every ID has a verifying test method.

### Anti-Patterns Found

None. Anti-pattern scan of `firmware.py`, `main.py`, and `test_firmware_install.py` for `TODO|FIXME|XXX|TBD|HACK|PLACEHOLDER` returned no new debt markers in the lines added by this phase.

### Human Verification Required

None at this phase. Real-silicon flash verification (the only human-required check for INST-01 / INST-02 end-to-end) is **explicitly deferred to Phase 24 BENCH-01** per CONTEXT D-15. Phase 23's scope is mocked-pytest only and is closable without operator intervention.

The verifier confirms:
- The deferred real-silicon scope is documented in CONTEXT D-15 and in REQUIREMENTS.md BENCH-01 (line 48).
- BENCH-01 is mapped to Phase 24 in REQUIREMENTS.md Traceability (line 93).
- Phase 24 ROADMAP entry explicitly takes INST-02 end-to-end-proof responsibility (ROADMAP.md Phase 24 SC#2).

This deferral was a planning-time decision (not a verification-time gap), is fully traced, and is the correct partition of work between desk-side and bench-side phases.

### Gaps Summary

None. All 5 ROADMAP Success Criteria are observably true in the codebase, all 4 requirement IDs are satisfied (INST-01/02/03 at mocked-pytest scope; GATE-01 fully closed), all 3 must-have artifacts exist and contain the expected content, all 3 key links are wired and behave correctly at runtime, the forbidden-edit surface is empty, the branch/push discipline holds, and the pytest suite is 82/82 green with the GATE-01 non-regression subset at 77/77 unchanged.

The phase achieved its goal exactly as planned: two TDD waves (RED tests in `67c8357`, GREEN code in `d13d9b1`) landed atomically on `firestarter_app/v1.5-uno328pb` with no remote push, no firmware-sub-repo perturbation, and no forbidden edits.

---

_Verified: 2026-05-21_
_Verifier: Claude (gsd-verifier)_

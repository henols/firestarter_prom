---
phase: 38-low-risk-extractions
plan: 03
subsystem: refactoring
tags: [python, codec, message-formatting, module-extraction, host-cli, tdd, pure-function]

# Dependency graph
requires:
  - phase: 36-characterization-test-baseline
    provides: "162-test + 29-snapshot safety net (test_decoder.py exercises the MSG_DEBUG render path end-to-end)"
  - phase: 37-tooling-baseline-ci-gate
    provides: "ruff + ruff-format + mypy watermark (44) CI gate"
  - phase: 38-low-risk-extractions
    plan: 01
    provides: "exceptions.py leaf (predecessor; commit 9f85635)"
  - phase: 38-low-risk-extractions
    plan: 02
    provides: "frame_parser.py pure leaf with _decode_param (D-08 import source; commit 38493e4)"
provides:
  - "firestarter/codec.py — public module-level pure function format_message(msg_id, params, entry) + _REVISION_SILKSCREEN table; callable without a SerialCommunicator instance"
  - "tests/test_codec.py — 10 catalog-fixture unit tests for format_message (STRUCT-02 / SC#3 / D-08)"
  - "serial_comm._decode_id_frame repointed to codec.format_message; _format_message method removed from serial_comm.py"
affects: [40-serial-restructure, 41-cli-handlers]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Public module-level pure render function (no self) extracted from a private instance method"
    - "TDD RED→GREEN: failing test_codec.py committed first, then codec.py makes it green"
    - "D-08 import correction: codec imports frame_parser._decode_param + struct (not constants+messages only)"

key-files:
  created:
    - firestarter_app/firestarter/codec.py
    - firestarter_app/tests/test_codec.py
  modified:
    - firestarter_app/firestarter/serial_comm.py

key-decisions:
  - "format_message is PUBLIC (no leading _) and self-free (D-08 / SC#3 rename) — verified zero self. references in the moved body"
  - "codec.py imports from FOUR sources (D-08 RESEARCH correction over D-08's literal 'constants + messages only'): struct, constants (explicit REVISION_* + COMMAND_NAMES), frame_parser._decode_param, messages — all cycle-safe leaves"
  - "_REVISION_SILKSCREEN moved with explicit REVISION_* named imports; the # noqa: F405 annotations DROPPED (no longer star-imported here)"
  - "Phase-35 WR-01/WR-02 rationale comments migrated VERBATIM (D-16 — live intent, not dead code)"
  - "_decode_id_frame stays in serial_comm.py (D-06); only its _format_message call site repointed to codec.format_message; _read_and_parse_lines untouched (D-09 / GATE-1.8d)"

patterns-established:
  - "Sentinel-aware message-render module as a public pure function with unit tests over catalog fixtures (no serial I/O)"

requirements-completed: [STRUCT-02]

# Metrics
duration: ~15min (executor partial; orchestrator close-out after interruption)
completed: 2026-05-27
---

# Phase 38 Plan 03: Codec Extraction Summary

**`_format_message` extracted from serial_comm.py into a new flat module `firestarter/codec.py` as the public pure function `format_message` (with `_REVISION_SILKSCREEN`), `_decode_id_frame`'s call site repointed, and 10 new `tests/test_codec.py` catalog-fixture cases added TDD-style. The D-08 `frame_parser._decode_param` import correction is in place; suite green at 172 passed / 2 xfailed / 29 snapshots, ruff + mypy@44 clean, test_decoder.py unchanged.**

## Performance

- **Duration:** ~15 min (executor completed Task 1 RED + most of Task 2, then was interrupted; orchestrator verified the working tree, applied the final `ruff format` pass on serial_comm.py, committed GREEN, and wrote this SUMMARY — see Issues Encountered)
- **Started:** 2026-05-27
- **Completed:** 2026-05-27
- **Tasks:** 2 (TDD: RED test + GREEN implementation)
- **Files:** 2 created, 1 modified

## Accomplishments
- **Task 1 (RED):** Created `tests/test_codec.py` with 10 cases across `TestFormatMessageRevision`, `TestFormatMessageDebugChunk`, `TestFormatMessageNoneSentinel` — covering MSG_OK_REV (with/without override), MSG_OK_CFG (with/without override), MSG_INFO_HW, MSG_INFO_PHYSICAL_HW, MSG_INFO_CMD, MSG_DEBUG+DBG_CMD, MSG_DATA_CHUNK, and the None-for-unknown-id sentinel. Committed RED (codec.py absent) so the test genuinely drives the extraction.
- **Task 2 (GREEN):** Created `firestarter/codec.py` — 7-line MIT header + module docstring; public `def format_message(msg_id: int, params: list, entry) -> Optional[str]` (drops `self`); `_REVISION_SILKSCREEN` moved with explicit `REVISION_*` named imports and the `# noqa: F405` annotations dropped. The D-08 import correction is present: `import struct`, `from firestarter.frame_parser import _decode_param`, plus `constants` (COMMAND_NAMES + 7 REVISION_*) and `messages` (DBG_CMD, DEBUG_CATALOG, MSG_* …). Phase-35 WR-01/WR-02 rationale comments migrated verbatim (D-16).
- In `serial_comm.py`: added `import firestarter.codec as codec`, removed the `_format_message` method and the `_REVISION_SILKSCREEN` dict, and repointed `_decode_id_frame` to `text = codec.format_message(msg_id, values, entry)`. The Plan-02 frame_parser re-export block is intact; `_read_and_parse_lines` is untouched (ring-fenced, GATE-1.8d).
- Verified behavior preservation: `test_codec.py` 10/10 green; `test_decoder.py` passes UNCHANGED (git diff empty — it exercises the MSG_DEBUG path, validating the `_decode_param` import correction per Pitfall 2); full suite **172 passed / 2 xfailed / 29 snapshots** (162 baseline + 10 new; both xfail stay xfailed); snapshot diff empty; ruff check + ruff format clean; mypy at watermark 44.

## Task Commits

Both commits inside the `firestarter_app` submodule on branch `v1.8-app-cleanup`:

1. **Task 1 (RED): test_codec.py covering format_message** — `296c511` (test) — committed while codec.py was absent (ImportError = RED confirmed)
2. **Task 2 (GREEN): extract codec.format_message + _REVISION_SILKSCREEN; repoint _decode_id_frame** — `5ec7048` (refactor)

_SUMMARY.md and meta-repo files (STATE.md / ROADMAP.md / REQUIREMENTS.md) are owned by the orchestrator and not committed inside the submodule. The `.coverage` test artifact was left untracked._

## Files Created/Modified
- `firestarter_app/firestarter/codec.py` (created) — Pure-render module. Imports: `struct`, `typing.Optional` (`# noqa: UP035`), `constants` (COMMAND_NAMES + REVISION_0/1/2_0/2_1/2_2/2_3/UNKNOWN as explicit named imports, no F405), `frame_parser._decode_param` (D-08), `messages` (the MSG_*/CATALOG/DBG_CMD/DEBUG_CATALOG names referenced). Contains public `format_message` + `_REVISION_SILKSCREEN`.
- `firestarter_app/tests/test_codec.py` (created) — 10 unit tests over `CATALOG[MSG_*]` fixtures; no serial fixtures, no SerialCommunicator instance.
- `firestarter_app/firestarter/serial_comm.py` — `import firestarter.codec as codec` added; `_format_message` method + `_REVISION_SILKSCREEN` dict removed (≈117-line block); `_decode_id_frame` call site repointed to `codec.format_message`. Ring-fenced `_read_and_parse_lines` untouched; frame_parser re-export block intact; remaining star-import `# noqa: F403/F405` annotations parked (Phase 39).

## Decisions Made
- **D-08 import correction honored.** D-08's text said codec needs "constants + messages only," but `format_message` calls `_decode_param` (MSG_DEBUG sub-dispatch) and uses `struct.error`, so codec.py imports `struct` and `frame_parser._decode_param`. Without the `_decode_param` import, MSG_DEBUG frames would `NameError` (Pitfall 2); `test_decoder.py`'s MSG_DEBUG path is the guard.
- **Silkscreen F405 dropped.** `_REVISION_SILKSCREEN` now references explicitly-imported `REVISION_*` constants, so the `# noqa: F405` (star-import suppression) annotations were removed per PATTERNS.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Applied the final `ruff format` pass on serial_comm.py (completed by orchestrator)**
- **Found during:** orchestrator close-out verification after executor interruption
- **Issue:** The executor was interrupted before running the final `ruff format` pass; `ruff format --check` reported `Would reformat: firestarter/serial_comm.py` (a formatting nit in the edited import/removal region).
- **Fix:** Ran `ruff format firestarter/serial_comm.py`. Confirmed the resulting diff hunks are confined to the edited regions (import block, frame_parser re-export, `_REVISION_SILKSCREEN` removal, `_format_message` removal, `_decode_id_frame` call-site repoint) — `_read_and_parse_lines` is absent from every hunk (ring-fence GATE-1.8d intact). No logic change.
- **Verification:** `ruff format --check` clean; `ruff check` clean; full suite 172/2/29; snapshot + test_decoder.py diffs empty.
- **Committed in:** `5ec7048` (the GREEN commit, after the format pass)

---

**Total deviations:** 1 auto-fixed (formatting-only, applied during orchestrator close-out).
**Impact on plan:** None on behavior — formatting only, confined to serial_comm.py's edited regions. All acceptance criteria met.

## Issues Encountered
- **Executor interrupted mid-Task-2; orchestrator closed out (safe-resume).** The plan's executor committed the RED test (`296c511`) and produced the complete Task 2 working tree (codec.py created, serial_comm.py edited) but was interrupted before the final `ruff format`, the GREEN commit, and the SUMMARY. The orchestrator (1) restored the test toolchain — pytest/ruff/syrupy/mypy/pytest-cov had been wiped from the `/usr/local` Python during an environment reset in the interruption window, masked by Phase-37's hardened mypy-watermark fallback — by reinstalling `pip install -e '.[test]'`; (2) ran the full verification; (3) applied the missing `ruff format` pass; (4) committed GREEN (`5ec7048`); (5) wrote this SUMMARY. No work was duplicated (Task 1's RED commit was preserved, not re-run).
- No behavioral regressions: the Phase 36 safety net + the 10 new test_codec cases + the unchanged test_decoder MSG_DEBUG path all pass.

## User Setup Required
None — but note the devcontainer's `/usr/local` Python lost its test toolchain during this plan's execution; it was restored via `python -m pip install -e '.[test]'` from `firestarter_app/`. If the suite reports "No module named pytest" again, re-run that install. (The project `.venv/` is a foreign leftover from the operator's host machine — unusable in this container; use the `/usr/local` Python.)

## Next Phase Readiness
- `firestarter/codec.py` exists with the public `format_message` — Phase 40's serial restructure can rely on render logic being out of serial_comm.py.
- serial_comm.py now delegates both frame decode (frame_parser) and message render (codec); only `_decode_id_frame` orchestration + transport remain (Phase 40 territory).
- No blockers for Plan 04 (address_parser — independent of codec) or Plan 05 (dead-code sweep — touches serial_comm.py + eprom_operations.py). `_read_and_parse_lines` remains ring-fenced.

## Threat Flags
None — this plan moved a pure render function + lookup table between local modules, renamed a private method to a public function, and added unit tests. No new external input, network, serial, file I/O, or auth surface. The D-08 `_decode_param` import is cycle-safe (frame_parser is a stdlib-only leaf). Matches plan threat_model: T-38-03 / T-38-SC accepted; wire protocol byte-identical (GATE-1.8a).

## Self-Check: PASSED
- `firestarter_app/firestarter/codec.py` exists (FOUND) with public `def format_message` (FOUND) + `_REVISION_SILKSCREEN` (FOUND); `from firestarter.frame_parser import _decode_param` present (D-08); no `# noqa: F405` on the silkscreen dict.
- `firestarter_app/tests/test_codec.py` exists with 10 cases; all GREEN.
- Commits `296c511` (RED) + `5ec7048` (GREEN) exist in the `firestarter_app` submodule.
- `_format_message` removed from serial_comm.py (grep 0); `_decode_id_frame` calls `codec.format_message` (line 296); `import firestarter.codec as codec` present (line 24).
- Full suite: 172 passed, 2 xfailed, 29 snapshots; both xfail stay xfailed.
- `git diff tests/test_decoder.py` empty; `git diff tests/__snapshots__/` empty; `_read_and_parse_lines` byte-identical (absent from diff).
- ruff check + ruff format --check clean; mypy at watermark 44.

---
*Phase: 38-low-risk-extractions*
*Completed: 2026-05-27*

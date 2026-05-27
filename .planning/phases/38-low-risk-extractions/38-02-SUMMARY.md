---
phase: 38-low-risk-extractions
plan: 02
subsystem: refactoring
tags: [python, frame-parser, module-extraction, host-cli, leaf-module, re-export]

# Dependency graph
requires:
  - phase: 36-characterization-test-baseline
    provides: "162-test + 29-snapshot safety net (test_decoder.py proves frame primitive behavior preservation)"
  - phase: 37-tooling-baseline-ci-gate
    provides: "ruff + ruff-format + mypy watermark (44) CI gate"
  - phase: 38-low-risk-extractions
    plan: 01
    provides: "exceptions.py leaf + repointed serial_comm import block (predecessor; commit 9f85635)"
provides:
  - "firestarter/frame_parser.py — pure stdlib-only leaf with the 7 wire-frame primitives (CRC8-CCITT + param decode + Response/LogMessage namedtuples + MAGIC_PREAMBLE)"
  - "_decode_param + _crc8_ccitt importable from frame_parser for Phase 39/40 codec.py and downstream consumers"
  - "Backward-compat re-export surface in serial_comm.py so test_decoder.py + downstream callers keep importing MAGIC_PREAMBLE/LogMessage/Response/_crc8_ccitt unchanged"
affects: [39-chip-resolver, 40-serial-restructure, 41-cli-handlers]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pure-leaf frame-primitive module (zero package-internal imports; stdlib struct + typing only)"
    - "Backward-compat re-export block with one # noqa: F401 on the parenthesized opening line (covers all names)"
    - "Verbatim symbol move + same-commit re-export to keep importing callers passing UNCHANGED (D-07 landmine resolution)"

key-files:
  created:
    - firestarter_app/firestarter/frame_parser.py
  modified:
    - firestarter_app/firestarter/serial_comm.py

key-decisions:
  - "frame_parser.py gets ONLY the 7 truly-pure primitives (D-05): Response, LogMessage, MAGIC_PREAMBLE, _build_crc8_table, _CRC8_CCITT_TABLE, _crc8_ccitt, _decode_param — moved VERBATIM with docstrings/noqa intact"
  - "_decode_id_frame STAYS in serial_comm.py (D-06 — package-coupled to CATALOG + codec; deferred to Phase 40)"
  - "Re-export block includes _decode_param (5 symbols total), not just the 4 test_decoder.py needs — serial_comm.py's surviving _format_message + _decode_id_frame call _decode_param at lines 410/501, so the name must resolve in serial_comm's namespace"
  - "frame_parser.py is a pure leaf: zero 'from firestarter' / 'import firestarter' lines (stdlib struct + collections.namedtuple + typing only)"
  - "_read_and_parse_lines generator body byte-identical (D-09 / GATE-1.8d ring-fence) — not in the diff at all"

patterns-established:
  - "Pure-leaf wire-frame module: CRC8 + param-decode + structured response types in one stdlib-only file"
  - "Same-commit verbatim-move + re-export so importing callers (tests + downstream) pass UNCHANGED"

requirements-completed: [STRUCT-01]

# Metrics
duration: ~12min
completed: 2026-05-27
---

# Phase 38 Plan 02: Frame Parser Extraction Summary

**The 7 pure wire-frame primitives (CRC8-CCITT, parameter decode, Response/LogMessage namedtuples, MAGIC_PREAMBLE) extracted VERBATIM from serial_comm.py into a new stdlib-only leaf `firestarter/frame_parser.py`, with a same-commit backward-compat re-export block so test_decoder.py passes UNCHANGED (162 passed / 2 xfailed / 29 snapshots, ruff + mypy@44 green).**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-05-27
- **Completed:** 2026-05-27
- **Tasks:** 2
- **Files:** 1 created, 1 modified

## Accomplishments
- Created `firestarter/frame_parser.py` as a pure stdlib-only leaf (no package-internal imports; only `struct`, `collections.namedtuple`, `typing`) holding the 7 primitives moved verbatim (D-05): `Response`, `LogMessage`, `MAGIC_PREAMBLE`, `_build_crc8_table`, `_CRC8_CCITT_TABLE`, `_crc8_ccitt`, `_decode_param`. Docstrings (including the WR-04 bounds-check rationale on `_decode_param`), `_` private prefixes, and `# noqa: UP006`/`UP035` house-style annotations all migrated intact.
- Removed those originals from `serial_comm.py` and added the backward-compat re-export block in the SAME atomic commit (D-07 landmine resolution): `from firestarter.frame_parser import (MAGIC_PREAMBLE, LogMessage, Response, _crc8_ccitt, _decode_param)` with one `# noqa: F401` on the opening line, placed at its isort-correct position (between the `exceptions` and `messages` import groups).
- Kept `_decode_id_frame` in `serial_comm.py` (D-06 — package-coupled, Phase 40) and left `_format_message` in place (Plan 03); both now resolve `_decode_param` / `_crc8_ccitt` / `LogMessage` / `MAGIC_PREAMBLE` / `Response` via the new import.
- Dropped the now-unused `from collections import namedtuple` and `typing.Any` imports from serial_comm.py (both became dead once the primitives moved out).
- Verified behavior preservation: `test_decoder.py` passes unchanged (git diff empty), full suite 162 passed / 2 xfailed / 29 snapshots (both xfail stay xfailed, not xpassed), snapshot diff empty, `_read_and_parse_lines` byte-identical (absent from the diff), ruff check + format clean, mypy at watermark 44.

## Task Commits

Per the plan's D-07 landmine guidance (re-export MUST be added in the same commit that removes the originals, or test_decoder.py's import breaks the entire suite), both tasks were committed together in one atomic commit inside the `firestarter_app` submodule:

1. **Task 1 + Task 2: Extract frame primitives to frame_parser.py + serial_comm re-export** - `38493e4` (refactor)

_Commit made inside the `firestarter_app` submodule on branch `v1.8-app-cleanup`. SUMMARY.md and meta-repo files (STATE.md / ROADMAP.md / REQUIREMENTS.md) intentionally NOT committed by this executor — the orchestrator owns meta-repo writes. The `.coverage` test artifact was left untracked (not staged)._

## Files Created/Modified
- `firestarter_app/firestarter/frame_parser.py` (created) — Pure stdlib-only leaf; 7-line MIT header (copyright 2024) + module docstring; imports only `struct`, `collections.namedtuple`, `typing.Any/Tuple` (`# noqa: UP035`); the 7 frame primitives moved verbatim. `grep -c '^from firestarter\|^import firestarter'` returns 0.
- `firestarter_app/firestarter/serial_comm.py` — Removed the 96-line primitive block (lines 51–146 region: `Response`/`LogMessage`/`MAGIC_PREAMBLE` defs, `_build_crc8_table`, `_CRC8_CCITT_TABLE`, `_crc8_ccitt`, `_decode_param`); added the 13-line re-export block in the `firestarter.*` import group; removed unused `from collections import namedtuple` and `typing.Any`. `_read_and_parse_lines` untouched (ring-fenced); `_decode_id_frame` / `_format_message` logic untouched (only resolve moved names via the new import). Star-import `# noqa: F403/F405` annotations left parked (Phase 39).

## Decisions Made
- **Re-export 5 symbols, not 4.** The RESEARCH/PATTERNS re-export snippet lists the 4 symbols `test_decoder.py` imports. But `serial_comm.py` itself still calls `_decode_param` at lines 410 (`_format_message`) and 501, so the re-export block also imports `_decode_param` (per the plan's key_reminders: "Add `_decode_param` to the import too if `_decode_id_frame` references it so the name resolves"). All 5 names (`MAGIC_PREAMBLE`, `LogMessage`, `Response`, `_crc8_ccitt`, `_decode_param`) are now bound in serial_comm's namespace; the 4 that test_decoder.py imports are a subset.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Removed now-unused `from collections import namedtuple` AND `typing.Any` from serial_comm.py**
- **Found during:** Task 2 (ruff gate)
- **Issue:** After moving `Response`/`LogMessage` (the only `namedtuple` callers) and `_decode_param` (the only `Any` annotation user) out of serial_comm.py, `ruff check` reported `F401 typing.Any imported but unused`. The plan's Task 2 action explicitly anticipates dropping `namedtuple` ("Remove the now-unused `from collections import namedtuple` import"), but `Any` becoming dead was an unstated consequence of the same move.
- **Fix:** Dropped `namedtuple` from the import block (verified 0 remaining `namedtuple` references) and removed `Any` from the `from typing import ...` line (verified 0 remaining `Any` references outside the import). `struct` and `Tuple` kept (still used at lines 336/419/533 and 604 respectively).
- **Files modified:** firestarter_app/firestarter/serial_comm.py
- **Verification:** `ruff check firestarter/serial_comm.py` → All checks passed; full suite still 162/2/29.
- **Committed in:** 38493e4 (part of the single atomic commit)

**2. [Rule 3 - Blocking] Placed the re-export block at its isort-correct position (between `exceptions` and `messages`)**
- **Found during:** Task 2 (ruff gate)
- **Issue:** The plan's Task 2 action says to add the re-export "after the existing `from firestarter.messages import ...` block". Doing so triggered ruff `I001 Import block is un-sorted` — within the `firestarter.*` group, isort orders alphabetically by module (`config`, `constants`, `exceptions`, `frame_parser`, `messages`), so `frame_parser` must sit BEFORE `messages`, not after it.
- **Fix:** Moved the re-export block (with its preceding comment) to between the `exceptions` and `messages` import blocks. Semantically identical (module-level import, still executes before any class/function defs); only ordering changed to satisfy ruff isort.
- **Files modified:** firestarter_app/firestarter/serial_comm.py
- **Verification:** `ruff check firestarter/serial_comm.py` → All checks passed.
- **Committed in:** 38493e4 (part of the single atomic commit)

---

**Total deviations:** 2 auto-fixed (both blocking, both ruff-gate-driven, both inside the import block only).
**Impact on plan:** Both auto-fixes were necessary to satisfy the plan's own ruff acceptance gate and are confined to the serial_comm.py import block. No logic change, no scope creep — the primitive bodies, `_read_and_parse_lines`, `_decode_id_frame`, and `_format_message` are all untouched.

## Issues Encountered
- None. The full Phase 36 safety net (162/2/29) caught no regressions; `test_decoder.py` (which drives hand-crafted binary frames through `_read_and_parse_lines` and asserts on `_crc8_ccitt` + `MAGIC_PREAMBLE` + `Response`/`LogMessage`) passed unchanged, giving end-to-end behavior-preservation proof for the moved primitives.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- `firestarter/frame_parser.py` exists and is importable as a pure leaf — Phase 39 / Plan 03 (`codec.py`) can now `from firestarter.frame_parser import _decode_param`.
- The serial_comm.py re-export surface is stable for the remaining Phase 38 plans (Plan 03 codec extraction, Plan 04 address_parser, Plan 05 dead-code sweep) and for Phase 40's serial restructure.
- No blockers. `_read_and_parse_lines` remains ring-fenced (GATE-1.8d); star-import `# noqa: F403/F405` annotations remain parked for Phase 39; the `# DO NOT MODIFY` marker (Phase 40 / D-10) was NOT added.

## Threat Flags
None — this plan only moved pure-compute frame primitives between local Python modules and added a re-export. The CRC8 computation is a wire-framing integrity check for local serial hardware, not a security primitive. No new external input, network, file I/O, or auth surface (matches plan threat_model: T-38-02 / T-38-SC accepted; wire protocol byte-identical).

## Self-Check: PASSED
- `firestarter_app/firestarter/frame_parser.py` exists (FOUND) and contains literal `def _decode_param` (FOUND).
- Commit `38493e4` exists in the `firestarter_app` submodule (FOUND).
- `grep -c '^from firestarter\|^import firestarter' firestarter/frame_parser.py` → 0 (pure leaf).
- serial_comm.py: originals removed (grep count 0), `from firestarter.frame_parser import` present, `_read_and_parse_lines` byte-identical (absent from diff).
- Full suite: 162 passed, 2 xfailed, 29 snapshots (unchanged baseline); both xfail stay xfailed.
- `git diff tests/test_decoder.py` empty; `git diff tests/__snapshots__/` empty.
- ruff check + ruff format --check clean; mypy at watermark 44.

---
*Phase: 38-low-risk-extractions*
*Completed: 2026-05-27*

---
phase: 38-low-risk-extractions
plan: 05
subsystem: refactoring
tags: [python, dead-code-removal, host-cli, command-names, globals-elimination, behavior-preserving]

# Dependency graph
requires:
  - phase: 36-characterization-test-baseline
    provides: "182-test + 29-snapshot safety net (operation-name log output pinned via CLI snapshots)"
  - phase: 37-tooling-baseline-ci-gate
    provides: "ruff + ruff-format + mypy watermark (44) CI gate"
  - phase: 38-low-risk-extractions
    plan: 03
    provides: "codec.py extraction + frame_parser re-export block + `import firestarter.codec as codec` in serial_comm.py (preserved untouched here)"
  - phase: 38-low-risk-extractions
    plan: 04
    provides: "address_parser.py + rewired _setup_operation (the globals() sites this plan replaced live in the same method)"
provides:
  - "firestarter/serial_comm.py — dead read_data_block method removed (zero callers; W-04 MSG_DATA_CHUNK migration made it dead); orphaned functools/operator imports dropped"
  - "firestarter/eprom_operations.py — both globals() reverse-lookups replaced with COMMAND_NAMES[cmd] (byte-identical operation-name log strings; latent int-collision fragility removed)"
affects: [39-star-import-resolution, 40-serial-restructure, 41-cli-handlers]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Dead-method removal with cascade cleanup of imports used only by the removed method (functools/operator)"
    - "globals() reverse-lookup → canonical dict lookup (COMMAND_NAMES[cmd]) — removes int-collision fragility, byte-identical for all valid commands"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/eprom_operations.py

key-decisions:
  - "read_data_block deleted whole (D-14): grep confirmed exactly one hit (its own def) — zero callers; dead since the W-04 MSG_DATA_CHUNK migration moved binary chunk delivery onto the framed message path (_read_and_parse_lines / frame_parser)"
  - "functools + operator imports removed: both used ONLY inside read_data_block (functools.reduce(operator.xor, ...) checksum); deleting the method orphaned them — Rule 3 cascade cleanup to keep ruff F401 green"
  - "Both globals() sites → COMMAND_NAMES[cmd] (D-15): RESEARCH verified 13/13 values equal old post-.replace('COMMAND_','') strings; `# noqa: F405` added (COMMAND_NAMES is star-imported, matching the existing same-file F405 idiom on COMMAND_READ)"
  - "IndexError→KeyError equivalence documented (Pitfall 5): unknown-cmd error type changes but both are unhandled and equally fatal; no caller catches IndexError around _setup_operation/_operation_context"
  - "D-16 no-op: no confirmed-dead commented-out blocks introduced by this sweep; the pre-existing serial_comm.py:151 alt-form comment and the __main__ usage examples are outside scope / live-intent — NOT invented removals"
  - "Star-import preserved (Phase 39); ring-fenced read_eprom (eprom_operations.py) + _read_and_parse_lines (serial_comm.py) untouched (GATE-1.8d); codec import + frame_parser re-export block intact"

patterns-established:
  - "Dead-code sweep as a single atomic commit: delete unreferenced method + cascade-remove its now-orphaned imports + replace fragile introspection with canonical lookup, all behavior-preserving against the snapshot safety net"

requirements-completed: [STRUCT-05]

# Metrics
duration: ~12min
completed: 2026-05-27
---

# Phase 38 Plan 05: Dead-Code Sweep Summary

**Mechanical behavior-preserving dead-code sweep: deleted the unreferenced `read_data_block` method (and the now-orphaned `functools`/`operator` imports it alone used) from `serial_comm.py`, and replaced both fragile `globals()` reverse-lookups in `eprom_operations.py` with the canonical `COMMAND_NAMES[cmd]` dict lookup — operation-name log output byte-identical, suite green at 182 passed / 2 xfailed / 29 snapshots, snapshot diff empty, ruff + ruff-format + mypy watermark (41 ≤ 44) all clean. This closes Phase 38.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-05-27
- **Completed:** 2026-05-27
- **Tasks:** 1 (auto; three mechanical edits in one task)
- **Files modified:** 2

## Accomplishments
- **D-14 — deleted `read_data_block`:** Confirmed zero callers FIRST (`grep -rn read_data_block firestarter/ tests/` returned exactly one hit — its own def at `serial_comm.py:757`). Deleted the entire 36-line method (def through its last `from e` body line). The method was dead because the W-04 `MSG_DATA_CHUNK` migration moved binary chunk delivery onto the framed `MSG_DATA_CHUNK` message path (decoded via `_read_and_parse_lines` / `frame_parser`), superseding the old length-prefixed `DATA:` reader. Did NOT touch `read_eprom` (lives in `eprom_operations.py:429`) or `_read_and_parse_lines` (`serial_comm.py:326`, ring-fenced GATE-1.8d). Frame_parser re-export block + `import firestarter.codec as codec` left intact.
- **Cascade import cleanup:** `functools` (line 10) and `operator` (line 13) were used ONLY inside `read_data_block` (`functools.reduce(operator.xor, data, 0)` checksum). Deleting the method orphaned both imports; removed them to keep `ruff check` green (F401). Confirmed via grep that no other reference exists in the file.
- **D-15 — replaced both `globals()` sites:** `_setup_operation` (was ~line 166) and `_operation_context` (was ~line 228) both used `[k for k, v in globals().items() if v == cmd][0].replace("COMMAND_", "")`. Replaced each with `COMMAND_NAMES[cmd]`. RESEARCH verified all 13 `COMMAND_NAMES` values equal the old post-`.replace` strings exactly (READ, WRITE, ERASE, BLANK_CHECK, …), so the `logger.debug` operation-name strings and the yielded `operation_name` are byte-identical. Added `# noqa: F405` to both replaced lines (COMMAND_NAMES resolves via the existing `from firestarter.constants import *` star-import — matching the file's existing F405 idiom on `COMMAND_READ`).
- **D-16 — no-op (no invented removals):** Scanned both edited files for orphaned commented-out code. The only candidates (`serial_comm.py:151` alt-form `# json_data = json.dumps(...)`, `serial_comm.py:254` rationale comment, `serial_comm.py:770` `__main__` usage example) are either pre-existing and outside this sweep's scope or live-intent documentation. Per D-16's "do NOT invent removals," removed none.
- Verified behavior preservation: full suite **182 passed / 2 xfailed / 29 snapshots** (unchanged from Plan 04's count); both xfail stay xfailed (not xpassed); `git diff tests/__snapshots__/` empty (operation-name log byte-identical); `ruff check` + `ruff format --check` clean (firestarter/ AND tests/); mypy at **41 errors** (3 below watermark 44 — the dead-method removal eliminated some typed errors; watermark gate exits 0, not exceeded).

## Task Commits

Single atomic commit inside the `firestarter_app` submodule on branch `v1.8-app-cleanup`:

1. **Task 1:** `refactor(38-05): delete dead read_data_block + replace globals() reverse-lookup with COMMAND_NAMES[cmd]` — `efb0fad`

The commit message cites the W-04 `MSG_DATA_CHUNK` migration that made `read_data_block` dead (D-14 / SC#5) and documents the IndexError→KeyError equivalence for the `globals()` → `COMMAND_NAMES[cmd]` change (D-15 / Pitfall 5).

_SUMMARY.md and meta-repo files (STATE.md / ROADMAP.md / REQUIREMENTS.md) intentionally NOT committed — the orchestrator owns meta-repo writes. The meta-repo `M firestarter` / `M firestarter_app` gitlinks were left alone. The `.coverage` test artifact was left untracked (per prior-wave convention)._

## Files Created/Modified
- `firestarter_app/firestarter/serial_comm.py` (modified) — Removed the entire `read_data_block` method (def through last body line, ~36 lines + surrounding blank) and the now-orphaned `import functools` / `import operator` lines. `grep -c read_data_block` returns 0. Ring-fenced `_read_and_parse_lines` absent from the diff (untouched); frame_parser re-export block + codec import intact; star-import + remaining `# noqa: F403/F405` annotations parked (Phase 39).
- `firestarter_app/firestarter/eprom_operations.py` (modified) — Both `globals()` reverse-lookups replaced with `COMMAND_NAMES[cmd]  # noqa: F405`. `grep -c "globals()"` returns 0; `grep -c "COMMAND_NAMES\[cmd\]"` returns 2. Star-import `# noqa: F403` and the `# noqa: F405` on the `COMMAND_READ` gate untouched (Phase 39). The Plan-04 address_parser wiring and the eprom_operations.py:265 comm-error bug (Phase 42 xfail) untouched.

## Decisions Made
- **`functools`/`operator` cascade removal (Rule 3 — see Deviations).** Not spelled out in the plan, but a direct and necessary consequence of deleting `read_data_block`: those two imports had no other referent and would have failed the plan's own `ruff check` acceptance gate.
- **`# noqa: F405` on the two `COMMAND_NAMES[cmd]` lines.** The PATTERNS doc's "After" example (`operation = COMMAND_NAMES[cmd]  # COMMAND_NAMES already imported via star-import`) omitted the noqa, but `COMMAND_NAMES` is a star-imported name, so ruff F405 fires without it. Adding `# noqa: F405` matches the file's existing idiom (the `COMMAND_READ` gate two lines down already carries it). Behavior-identical; keeps `ruff check` green and the star-import parked for Phase 39.
- **D-16 no-op confirmed, not invented.** Followed the plan's explicit "If no confirmed-dead commented block is found … do NOT invent removals."

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Removed the now-orphaned `functools` and `operator` imports from serial_comm.py**
- **Found during:** Task 1 (after deleting `read_data_block`)
- **Issue:** `import functools` (line 10) and `import operator` (line 13) were used in exactly one place — `functools.reduce(operator.xor, data, 0)` inside the deleted `read_data_block` checksum loop. After the method deletion they became unused imports, which `ruff check firestarter/` flags as F401 — failing the plan's own acceptance gate (`ruff check … exit 0`).
- **Fix:** Removed both import lines. Confirmed by grep that no other reference to `functools` or `operator` exists in `serial_comm.py`. Zero runtime/behavior impact (the imports' only consumer was the deleted method).
- **Files modified:** firestarter_app/firestarter/serial_comm.py (2 import lines)
- **Verification:** `ruff check firestarter/ tests/` → All checks passed; full suite still 182/2/29; snapshot diff empty.
- **Committed in:** `efb0fad` (the single atomic commit)

---

**Total deviations:** 1 auto-fixed (1 blocking — import cleanup directly caused by the planned `read_data_block` deletion).
**Impact on plan:** None on behavior or scope — the cascade import removal is the necessary completion of D-14's deletion (a method cannot be "fully removed" while leaving its sole-purpose imports dangling and the ruff gate red). Two import lines, no logic change, behavior byte-identical. All acceptance criteria met.

## Issues Encountered
- None. Toolchain was intact on entry (`pytest 9.0.3`, `ruff 0.15.14`, `mypy 2.1.0` all present in the `/usr/local` Python) — no reinstall needed. The `python tools/check_mypy_watermark.py` gate confirmed mypy is genuinely running (41 real errors reported), so the watermark pass is trustworthy (not the silent-OK fallback warned about in the env note).
- Line numbers had shifted from the plan's pre-wave references (read_data_block 991→757; globals() 170/232→166/228) due to waves 02/03 removing primitives + `_format_message` from serial_comm.py and waves 01/04 editing eprom_operations.py. Located all sites by grep, as instructed.

## User Setup Required
None.

## Next Phase Readiness
- Phase 38 (Low-Risk Extractions) is COMPLETE: all five plans (38-01 STRUCT-04 exceptions, 38-02 STRUCT-01 frame_parser, 38-03 STRUCT-02 codec, 38-04 STRUCT-03 address_parser, 38-05 STRUCT-05 dead-code sweep) shipped.
- Phase 39 (star-import resolution / DATA-03) can now remove `from firestarter.constants import *` from `serial_comm.py` and `eprom_operations.py`; the two new `COMMAND_NAMES[cmd]  # noqa: F405` sites will need `COMMAND_NAMES` added to an explicit import when the star-import is dropped (and the F405 noqa removed at that time).
- The ring-fenced read path (`_read_and_parse_lines`, `read_eprom`) remains untouched and reserved for v1.9 RCA (GATE-1.8d). No blockers introduced.

## Threat Flags
None — this plan deleted an unreferenced method, removed two now-orphaned stdlib imports, and replaced a `globals()` reverse-lookup with a canonical dict lookup. No new external input, network, serial, file I/O, or auth surface. The `globals()` → `COMMAND_NAMES[cmd]` change marginally HARDENS an existing path (the old int-comparison scan could mis-match a FLAG_* constant sharing the same integer value as a command; the dict keys on the exact cmd int). Wire protocol byte-identical (GATE-1.8a); ring-fenced read path untouched (GATE-1.8d). Matches plan threat_model: T-38-05 / T-38-SC accepted.

## Self-Check: PASSED
- `firestarter_app/firestarter/serial_comm.py` modified — `grep -c read_data_block` = 0 (FOUND removed); `functools`/`operator` imports gone; `_read_and_parse_lines` present (3 hits, untouched); frame_parser re-export + `import firestarter.codec as codec` present.
- `firestarter_app/firestarter/eprom_operations.py` modified — `grep -c "globals()"` = 0; `grep -c "COMMAND_NAMES\[cmd\]"` = 2; `from firestarter.constants import *` present (preserved).
- Commit `efb0fad` exists in the `firestarter_app` submodule on `v1.8-app-cleanup` (FOUND via `git log --oneline -1`); diff-tree shows exactly the two modified files, no whole-file deletions.
- Full suite: 182 passed, 2 xfailed, 29 snapshots; both xfail stay xfailed.
- `git diff tests/__snapshots__/` empty (operation-name log byte-identical).
- `ruff check` + `ruff format --check` clean (firestarter/ AND tests/); `python tools/check_mypy_watermark.py` → 41 errors ≤ watermark 44, exit 0.
- No meta-repo files modified or committed (meta HEAD still at Wave-4 close-out `666aed4`).

---
*Phase: 38-low-risk-extractions*
*Completed: 2026-05-27*

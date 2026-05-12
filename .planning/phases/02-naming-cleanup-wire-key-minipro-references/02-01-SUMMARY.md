---
phase: 02-naming-cleanup-wire-key-minipro-references
plan: 01
subsystem: wire-protocol
tags: [json-parser, serial-protocol, vpp, wire-key, atomic-rename, firmware-host-sync]

# Dependency graph
requires:
  - phase: 01-safety-closure-intel-flash-vpp-28c-chip-id
    provides: SAF-04 zero-init vpp_mv VPP-HIGH guard (covers partial-upgrade safe-fail)
provides:
  - WIRE-01 source-state assertion (Python emits "vpp_mv"; firmware parses "vpp_mv"; both CLAUDE.md examples consistent)
  - Atomic three-site flip pattern proven for future PROGMEM key-parser table renames in `firestarter/src/json_parser.c`
affects:
  - Plan 02-02 (CLEAN-01 file rename + D-04 internal vpp_volts rename — consumes the renamed wire as post-state contract)
  - Plan 02-03 (WIRE-02 check_dispatch.py regression scanner — asserts the new wire key end-to-end)
  - Phase 4 / HW-01..HW-05 (hardware-validation scripts target the new wire format)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Atomic cross-sub-repo wire-key rename (firmware + Python emitter + both CLAUDE.md docs land in two paired sub-repo commits + one parent-repo pointer bump)"
    - "Firmware three-site flip pattern (PROGMEM literal + dispatch table row + macro-arg in getter body) — all three sites must land in one sub-repo commit to avoid silent parse drop"

key-files:
  created:
    - .planning/phases/02-naming-cleanup-wire-key-minipro-references/02-01-SUMMARY.md
  modified:
    - firestarter/src/json_parser.c (3 sites: :62 PROGMEM literal, :74 dispatch row, :309 extract_int macro arg)
    - firestarter/CLAUDE.md (:74 JSON Wire Protocol field-list — collapse `vpp / vpp_mv` to `vpp_mv` only)
    - firestarter_app/firestarter/database.py (:518 dict-write key string `"vpp"` -> `"vpp_mv"`)
    - firestarter_app/CLAUDE.md (:55 wire-example phantom dual-key `"vpp": 12000,` line removed)

key-decisions:
  - "Firmware first, Python second (per RESEARCH.md commit-order recommendation): firmware sub-repo commit 39b29a9 lands the atomic three-site flip before the Python sub-repo commit 20cfe86 flips the emitter. SAF-04 covers either order — partial-upgrade safe-fail is structurally intact (RESEARCH.md Pitfall #3)."
  - "Documented PIO build evidence inline in the firmware commit message (uno + leonardo both green; 25/25 native tests pass)."
  - "Honored RESEARCH.md Factual Correction over CONTEXT.md D-02's 'delete vpp line' framing — :518 is a RENAME not a delete (the live emitter never emitted a second vpp_mv line)."
  - "Firmware-side field-list collapse to single `vpp_mv` bullet adopted per Plan 02-01 plan body (Claude's-discretion item from Phase 2 CONTEXT.md, implied by D-01 — firmware no longer reads `vpp`, documenting it as a field misleads readers)."

patterns-established:
  - "Atomic three-site flip in firestarter/src/json_parser.c: PROGMEM literal (:62) + dispatch table row (:74) + extract_int macro arg in getter body (:309) all flip in ONE commit. Skipping any single site causes silent parse drop -> handle->vpp_mv stays 0 -> SAF-04 trips on every Intel-flash write."
  - "Cross-sub-repo wire contract: rename lands as TWO paired sub-repo commits (firestarter + firestarter_app) + ONE parent-repo pointer-bump commit. SAF-04 zero-init guard covers partial-upgrade in either commit order."

requirements-completed: [WIRE-01]

# Metrics
duration: 4min
completed: 2026-05-12
---

# Phase 02 Plan 01: Atomic Wire-Key Flip vpp -> vpp_mv Summary

**Firmware JSON parser, Python wire emitter, and both CLAUDE.md examples flipped atomically from `"vpp"` (carrying integer millivolts — semantic overload) to `"vpp_mv"` end-to-end. MILESTONES.md WARNING-3 closed at the source-state assertion level.**

## Performance

- **Duration:** ~4 min (198 s plan-execution wallclock)
- **Started:** 2026-05-12T08:31:43Z
- **Completed:** 2026-05-12T08:35:01Z
- **Tasks:** 2 / 2 complete
- **Files modified:** 4 (2 firmware sub-repo, 2 Python sub-repo) plus 2 parent-repo submodule pointer bumps + 1 parent SUMMARY/STATE/ROADMAP commit
- **Sub-repo commits:** 2 (`firestarter`@`39b29a9`, `firestarter_app`@`20cfe86`)
- **Firmware build evidence:** `pio run -e uno` SUCCESS (25954/32256 B flash, 1587/2048 B RAM), `pio run -e leonardo` SUCCESS (28320/28672 B flash, 2063/2560 B RAM)
- **Firmware native tests:** `pio test -e native` -> 25/25 PASSED (dispatch + flash_intel_vpp + eeprom28c_chip_id suites)
- **Python wire smoke (W27C512):** `db.convert_to_programmer(db.get_eprom('W27C512'))` -> emits `vpp_mv: 12000`; no legacy `vpp` key.

## Accomplishments

- Atomic three-site firmware flip in `firestarter/src/json_parser.c` (`:62` PROGMEM literal, `:74` dispatch table row, `:309` `extract_int` macro arg) landed in a single sub-repo commit (`39b29a9`) — no half-flipped state ever existed, satisfying RESEARCH.md Pitfall #1.
- Python wire emitter `convert_to_programmer` at `firestarter_app/firestarter/database.py:518` now emits `"vpp_mv": vpp_mv` (was `"vpp": vpp_mv`); local-variable name and fallback at `:510` left untouched per scope rules.
- Both sub-repo CLAUDE.md files brought in sync with the new wire: firmware doc field-list collapsed to `vpp_mv` only; Python doc wire-example dropped the phantom dual-key `"vpp": 12000,` line (RESEARCH.md "Factual Correction" — the example documented a dual-key wire that never existed live).
- All eight cross-sub-repo grep gates from the plan's `<verification>` block pass.
- Both Arduino targets (`uno` + `leonardo`) compile cleanly post-flip; 25/25 host-side dispatch/SAF unit tests still pass.

## Task Commits

Each task committed atomically inside its own sub-repo (sub-repos have independent git histories):

1. **Task 02-01-01:** Firmware atomic three-site flip in `json_parser.c` + `firestarter/CLAUDE.md` field-list collapse — `firestarter@39b29a9` (`feat(02-01): rename JSON wire key vpp -> vpp_mv (atomic three-site flip)`)
2. **Task 02-01-02:** Python emitter `database.py:518` rename + `firestarter_app/CLAUDE.md:55` wire-example phantom-line removal — `firestarter_app@20cfe86` (`feat(02-01): emit "vpp_mv" wire key (rename from "vpp")`)

**Parent-repo metadata commit:** (recorded by the metadata commit after this SUMMARY lands — pointer bumps for both submodules + this SUMMARY.md + STATE.md + ROADMAP.md updates.)

## Files Created/Modified

### firestarter/ (firmware sub-repo)

- `src/json_parser.c` — atomic three-site flip:
  - `:62` — `const char key_vpp[] PROGMEM = "vpp";` -> `const char key_vpp_mv[] PROGMEM = "vpp_mv";` (variable name AND string content flip; follows sibling `key_mem_size` / `key_pin_count` snake-case convention).
  - `:74` — dispatch table row `{key_vpp, get_vpp_mv}` -> `{key_vpp_mv, get_vpp_mv}` (function pointer `get_vpp_mv` unchanged — it was already correctly named).
  - `:309` — `extract_int("vpp", handle->vpp_mv);` -> `extract_int("vpp_mv", handle->vpp_mv);` (the first macro arg is the parse key re-checked via `strncmp_P` inside `extract_num`; the C-struct field `handle->vpp_mv` at `include/firestarter.h:85` is unchanged per D-03).
- `CLAUDE.md` — `:74` field-list bullet collapsed from `vpp / vpp_mv` to single `vpp_mv` entry with millivolt clarifier (SAF-04 cross-reference).

### firestarter_app/ (Python sub-repo)

- `firestarter/database.py:518` — dict-write key string flip inside `convert_to_programmer`: `"vpp": vpp_mv,` -> `"vpp_mv": vpp_mv,`. Local variable `vpp_mv` and the fallback assignment at `:510` are unchanged.
- `CLAUDE.md:55` — wire-example phantom-line deletion: removed the `"vpp": 12000,` line; `"vpp_mv": 12000,` line preserved verbatim.

## Decisions Made

- **Commit order: firmware first, then Python.** Recommended by RESEARCH.md "Cross-Sub-Repo Coordination Pattern"; SAF-04 (Phase 1) makes either order safe via zero-init VPP-HIGH guard (RESEARCH.md Pitfall #3), so the choice was procedural rather than correctness-critical.
- **Followed RESEARCH.md Factual Correction over CONTEXT.md D-02 framing.** CONTEXT.md D-02 said "delete `\"vpp\": vpp_mv,`" implying the wire had two VPP keys today; RESEARCH.md proved the live emitter has exactly one `"vpp"` key already, so the correct edit is a one-character-class rename of the existing line at `:518`, not a deletion. Plan 02-01 plan body explicitly called this out and the executor honored it.
- **Did NOT touch line `:510`** (`vpp_mv = full_eprom_data.get("vpp_mv") or int(full_eprom_data.get("vpp", 0) * 1000)`) — that fallback reads the internal `_map_data` output dict (still keyed `"vpp"` until Plan 02-02 D-04). Plan 02-02 owns the rename to `"vpp_volts"`.
- **Did NOT touch `firestarter/CLAUDE.md:30` or `:69`** — minipro filename + protocol_id mentions; Plans 02-02 (CLEAN-01) and 02-03 (CLEAN-02) own those edits respectively. Confirmed via plan `<critical_constraints>`.

## Deviations from Plan

None — plan executed exactly as written. All eight verification gates passed on first run; no auto-fixes required.

## Issues Encountered

- One pre-existing dirty sub-repo (`firestarter_app/` had unrelated modifications: `firestarter/__init__.py`, `firestarter/ic_layout.py`, and seven deleted `.planning/codebase/*.md` files from prior session activity). Mitigation: staged only the two scoped files (`firestarter/database.py` and `CLAUDE.md`) via explicit `git add <file1> <file2>` (NOT `git add .` / `git add -A`), per the executor protocol's "stage task-related files individually" rule. The unrelated changes remain unstaged in the sub-repo working tree and are out of scope for this plan.
- No PIO availability skip needed — PlatformIO Core 6.1.19 was available; both `uno` and `leonardo` builds executed and succeeded.

## Cross-Sub-Repo Verification Gate Results

All eight gates from plan `<verification>` block:

| # | Gate | Expected | Actual | Status |
|---|------|----------|--------|--------|
| 1 | `grep -nE '"vpp_mv":\s*vpp_mv' firestarter_app/firestarter/database.py` | hits `:518` | hits `:418` + `:518` (both internal `_map_data` and external `convert_to_programmer`) | PASS |
| 2 | `grep -c '"vpp_mv"' firestarter/src/json_parser.c` (non-comment) | 2 | 2 | PASS |
| 3 | `grep -c '"vpp"' firestarter/src/json_parser.c` (non-comment) | 0 | 0 | PASS |
| 4 | `! grep -F '"vpp": 12000' firestarter_app/CLAUDE.md` | absent | absent | PASS |
| 5 | `! grep -F 'vpp / vpp_mv' firestarter/CLAUDE.md` | absent | absent | PASS |
| 6 | `grep -c 'key_vpp_mv' firestarter/src/json_parser.c` (non-comment) | >=2 | 2 | PASS |
| 7 | `grep -c '\bkey_vpp\b' firestarter/src/json_parser.c` (non-comment) | 0 | 0 | PASS |
| 8 | `:510` of `firestarter_app/firestarter/database.py` unchanged (still reads `get("vpp", 0) * 1000` upstream fallback) | unchanged | unchanged | PASS |

## Next Phase Readiness

- WIRE-01 source-state contract is locked in: Python emits only `"vpp_mv"`; firmware parses only `"vpp_mv"`; both CLAUDE.md doc examples are aligned.
- Plan 02-02 can now proceed with its work (CLEAN-01 file rename `minipro_complete_db.json` -> `chip_database.json` via `git mv`, plus D-04 internal `_map_data` rename `"vpp"` -> `"vpp_volts"` including the `:510` fallback consumer) without any state-of-the-wire ambiguity.
- Plan 02-03 can augment `tools/check_dispatch.py` (WIRE-02) with the in-loop wire-key regression asserts (`"vpp_mv" in wire` AND `"vpp" not in wire`) and run the full 743-chip scan against the renamed DB for SC#4 evidence.
- Phase 4 / HW-* hardware-validation scripts will see the final wire format (`vpp_mv` only) by the time they execute.
- Partial-upgrade safe-fail remains intact: SAF-04 (shipped Phase 1) catches both `firmware-new + app-old` and `firmware-old + app-new` mismatches via zero-init of `handle->vpp_mv` -> VPP-HIGH guard fires before any pulse.

## Self-Check: PASSED

Verified post-Write, pre-metadata-commit:

- FOUND: `.planning/phases/02-naming-cleanup-wire-key-minipro-references/02-01-SUMMARY.md`
- FOUND: `firestarter/src/json_parser.c` (modified, three sites flipped)
- FOUND: `firestarter/CLAUDE.md` (modified, field-list collapsed)
- FOUND: `firestarter_app/firestarter/database.py` (modified, `:518` renamed)
- FOUND: `firestarter_app/CLAUDE.md` (modified, phantom `:55` line removed)
- FOUND: firmware sub-repo commit `39b29a9` (`feat(02-01): rename JSON wire key vpp -> vpp_mv (atomic three-site flip)`)
- FOUND: app sub-repo commit `20cfe86` (`feat(02-01): emit "vpp_mv" wire key (rename from "vpp")`)
- All eight cross-sub-repo verification gates passed (see table above).

---
*Phase: 02-naming-cleanup-wire-key-minipro-references*
*Plan: 01*
*Completed: 2026-05-12*

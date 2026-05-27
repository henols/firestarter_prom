---
phase: 39-database-cleanup-chip-resolver
plan: 03
subsystem: documentation
tags: [python, documentation, comments, firmware-sync, pin-mapping, host-cli, zero-behavior-change]

# Dependency graph
requires:
  - phase: 39-database-cleanup-chip-resolver
    plan: 02
    provides: "database.py + constants.py in post-named-import state (no overlap with the comment blocks edited here)"
provides:
  - "pin_conversions documented as the RURP board-wiring layer (DIP socket pin → bus line), explicitly distinct from pinouts.json (chip function → socket pin) — closes the apparent 'two sources of truth' confusion without merging (DATA-02)"
  - "COMMAND_* and FLAG_* blocks in constants.py carry '# Firmware sync: firestarter.h' markers, matching the CTRL_*/REVISION_* block-header style (DATA-04)"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Firmware-sync block-header comment style: every wire-protocol constant block names its firmware-header source file"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/database.py
    - firestarter_app/firestarter/constants.py

key-decisions:
  - "DATA-02 is documentation-only (D-05): pin_conversions and pinouts.json encode DIFFERENT layers that compose in get_bus_config; NOT merged — superseding the REQUIREMENTS 'consolidate to one source' wording"
  - "DATA-04 is mark + verify only (D-09/D-10): COMMAND_FW_VERSION already present (= 13 / 0x0D) and already parity-tested; 'add if absent' is a no-op"
  - "messages.py message-ID catalog NOT relocated into constants.py (D-10): it is codegenerated from tools/catalog/messages.toml; moving it breaks the CI codegen drift gate"
  - "CTRL_*/REVISION_* block headers left unchanged — they already name rurp_pinout.h / rurp_shield.h respectively"

patterns-established:
  - "Layered-mapping clarification comment: name each layer, its direction, and the composition point, asserting one-source-of-truth-per-layer"

requirements-completed: [DATA-02, DATA-04]

# Metrics
duration: ~8min
completed: 2026-05-27
---

# Phase 39 Plan 03: pin_conversions doc + firmware-sync markers Summary

**Two documentation-only deliverables: a board-wiring clarification comment block on `pin_conversions` in `database.py` (distinguishing it from `pinouts.json` and naming `get_bus_config` as the composition point — DATA-02), and `# Firmware sync: firestarter.h` marker headers on the `COMMAND_*` and `FLAG_*` blocks in `constants.py` with `COMMAND_FW_VERSION` verified present + unchanged (DATA-04). Zero behavior change — parity suite 4/4 green, full suite 186 passed / 2 xfailed / 29 snapshots.**

## Performance
- **Duration:** ~8 min
- **Started:** 2026-05-27
- **Completed:** 2026-05-27
- **Tasks:** 2 (Task 1: database.py DATA-02; Task 2: constants.py DATA-04 + parity verify)
- **Files modified:** 2

## Accomplishments
- **DATA-02:** Replaced the single-line `# eprom pins to rurp conversion` comment above `pin_conversions` with a 7-line block stating `pin_conversions` is the RURP board-wiring layer (DIP socket pin → RURP bus line, hardware-specific), DISTINCT from `pinouts.json` (loaded as `self.pin_maps`; chip pin function → DIP socket pin, chip-specific), composing in `get_bus_config()`, with ONE source of truth per layer (not duplication). The inner `# Maps EPROM pin number to RURP hardware line number` comment and the dict contents are untouched. Verbatim from PATTERNS.md § database.py DATA-02.
- **DATA-04:** Added `# Wire-protocol command codes — Firmware sync: firestarter.h` + `# cmd field values sent in JSON commands to the Arduino firmware.` as the head of the `COMMAND_*` block, and extended the `# Control Flags` header to `# Control Flags — Firmware sync: firestarter.h` + `# flags bitmask values sent in JSON commands.` on the `FLAG_*` block — matching the existing `CTRL_*`/`REVISION_*` block-header marker style (which already name rurp_pinout.h / rurp_shield.h and were left unchanged). Verified `COMMAND_FW_VERSION = 13` (= 0x0D) present and unchanged; did NOT relocate the `messages.py` catalog (D-10).
- Verified zero behavior change: parity suite `test_revision_constants_parity.py` **4 passed** (incl. the `COMMAND_FW_VERSION == 0x0D` assertion at :116 — GATE-1.8c); full suite **186 passed, 2 xfailed, 29 snapshots** (both Phase 36 xfails remain xfail); `ruff check` clean on both files; mypy watermark **41 ≤ 44** (unchanged).

## Task Commits
All commits made inside the `firestarter_app` submodule on branch `v1.8-app-cleanup`:
1. **Task 1 (DATA-02):** `docs(39-03): document pin_conversions as RURP board-wiring layer, distinct from pinouts.json (DATA-02)` — `b176e70`
2. **Task 2 (DATA-04):** `docs(39-03): add 'Firmware sync: firestarter.h' markers to COMMAND_*/FLAG_* blocks; verify COMMAND_FW_VERSION (DATA-04)` — `6e32b37`

_SUMMARY.md and meta-repo files intentionally NOT committed inside the submodule — the orchestrator owns meta-repo writes._

## Deviations from Plan

### Noted (no fix needed)

**1. `COMMAND_FW_VERSION` shifted from line 37 to line 39 (value unchanged)**
- The acceptance criterion expected `grep -n "COMMAND_FW_VERSION = 13"` "at line 37". Adding the 2-line `COMMAND_*` marker header above `COMMAND_READ` shifted the whole block down by 2 lines, so `COMMAND_FW_VERSION = 13` now sits at line 39. This is a benign, expected consequence of the DATA-04 marker itself — the assignment, value (`= 13` / `0x0D`), and parity assertion are all unchanged and green. No action needed; the structural intent ("present + unchanged value") is fully satisfied.

---
**Total deviations:** 1 noted (0 fixes). **Impact:** none — line-number shift only, value/contract identical.

## Issues Encountered
None.

## User Setup Required
None.

## Next Phase Readiness
- Phase 39 (database cleanup + chip_resolver) deliverables DATA-01..04 are all complete. The pin-mapping "two sources of truth" confusion is documented away; every wire-protocol constant block now names its firmware-header source.
- No blockers. GATE-1.8 (wire protocol + CLI surface + read path frozen) held across all 3 plans.

## Threat Flags
None — documentation/comments only. No values, logic, runtime, network, serial, auth, or input surface touched (matches plan threat_model T-39-03 / T-39-SC accepted). Constant contract preserved + parity-tested (GATE-1.8c). No package installs.

## Self-Check: PASSED
- DATA-02: `grep -i "board-wiring" firestarter/database.py` → present; `grep -i "pinouts.json"` → present inside the new block (references the distinct layer + get_bus_config composition).
- DATA-04: `grep -c "Firmware sync" firestarter/constants.py` → 2 (COMMAND_* + FLAG_*).
- `COMMAND_FW_VERSION = 13` present + unchanged (now :39); `messages.py` not relocated (`grep -c "messages.toml\|from firestarter.messages"` → 0).
- Parity suite `test_revision_constants_parity.py` → 4 passed (GATE-1.8c).
- Full suite: 186 passed, 2 xfailed, 29 snapshots; ruff clean; mypy watermark 41 ≤ 44.
- Commits `b176e70` (DATA-02) and `6e32b37` (DATA-04) exist in the `firestarter_app` submodule.

---
*Phase: 39-database-cleanup-chip-resolver*
*Completed: 2026-05-27*

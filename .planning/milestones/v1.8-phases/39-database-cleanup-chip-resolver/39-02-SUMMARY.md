---
phase: 39-database-cleanup-chip-resolver
plan: 02
subsystem: refactoring
tags: [python, imports, star-import-removal, noqa-cleanup, lint, mypy, host-cli]

# Dependency graph
requires:
  - phase: 37-tooling-baseline-ci-gate
    provides: "ruff + mypy watermark (44) CI gate — the ground-truth lint authority used to verify the named-import lists"
  - phase: 39-database-cleanup-chip-resolver
    plan: 01
    provides: "main.py in post-chip_resolver state (op sites repointed) — 39-02 owns the main.py:23 star-import 39-01 deliberately left"
provides:
  - "All 6 modules use explicit named imports from firestarter.constants (zero star-imports repo-wide)"
  - "55 dead F403/F405 noqa markers removed; mypy can now resolve every constant name (prereq for Phase 42 mypy-gate tightening)"
affects: [42-error-handling-normalization]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Explicit named-import blocks (parenthesized, alphabetical for 3+ names) replacing wildcard imports — usage sites unchanged (D-07: no namespace-prefix rewrite)"
    - "ruff as ground truth for import lists: F401 (over-import) and F821 (missed name) verify exact membership rather than trusting a pre-written list"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/main.py
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/database.py
    - firestarter_app/firestarter/firmware.py
    - firestarter_app/firestarter/hardware.py

key-decisions:
  - "All 6 star-importing modules converted (D-06): main, serial_comm, eprom_operations, database, firmware, hardware — the repo-wide `grep` acceptance (SC#3) requires all 6, not the 4 ROADMAP named"
  - "Import lists determined by ruff, not by the RESEARCH Pattern-4 list: the plan explicitly says treat ruff as ground truth; two list corrections resulted (see Deviations)"
  - "Only F403/F405 stripped; the 3 F401 markers (serial_comm:37 frame_parser re-exports, firmware:30 FirmwareOperationError orphan, eprom_operations:391 MSG_DATA_CHUNK local) PRESERVED — they suppress genuinely-intentional unused imports"
  - "F405 markers stripped end-anchored, preserving any preceding inline comment (e.g. database `# FLAG_CAN_ERASE is 0x02`, eprom_operations `# This is 512 in constants.py`)"

patterns-established:
  - "Wildcard-to-named import sweep with ruff-verified membership and surgical dead-noqa removal — behavior byte-identical (GATE-1.8a/c/e)"

requirements-completed: [DATA-03]

# Metrics
duration: ~15min
completed: 2026-05-27
---

# Phase 39 Plan 02: star-import sweep + dead-noqa strip Summary

**Replaced every `from firestarter.constants import *` wildcard across all 6 star-importing modules with explicit named-import blocks and stripped all 55 dead `# noqa: F403`/`# noqa: F405` markers (preserving the 3 intentional F401 markers) — repo-wide star-import grep now empty, ruff clean, mypy 41 ≤ 44, full suite 186 passed / 2 xfailed / 29 snapshots unchanged.**

## Performance
- **Duration:** ~15 min
- **Started:** 2026-05-27
- **Completed:** 2026-05-27
- **Tasks:** 2 (Task 1: main/serial_comm/eprom_operations; Task 2: database/firmware/hardware + full-suite gate)
- **Files modified:** 6

## Accomplishments
- Replaced the star-import in all 6 modules with explicit named-import blocks (parenthesized + alphabetical for 3+ names; single-line for the 1–2-name cases), matching the existing exceptions-import house style. ruff-verified final membership:
  - `main.py` → 2 names: `FLAG_CHIP_ENABLE`, `FLAG_OUTPUT_ENABLE` (see Deviation 1)
  - `serial_comm.py` → 9 names (BAUD_RATE, COMMAND_FW_VERSION, FLAG_CAN_ERASE, FLAG_CHIP_ENABLE, FLAG_FORCE, FLAG_OUTPUT_ENABLE, FLAG_SKIP_BLANK_CHECK, FLAG_SKIP_ERASE, FLAG_VPE_AS_VPP)
  - `eprom_operations.py` → 15 names (BUFFER_SIZE + 9 COMMAND_* + 5 FLAG_*)
  - `database.py` → 1 name (`FLAG_CAN_ERASE`)
  - `firmware.py` → 5 names (COMMAND_FW_VERSION, 3× FIRESTARTER_RELEASE* URL, FLAG_FORCE)
  - `hardware.py` → 4 names: COMMAND_CONFIG, COMMAND_HW_VERSION, COMMAND_READ_VPE, COMMAND_READ_VPP (see Deviation 2)
- Stripped all 55 `# noqa: F403`/`# noqa: F405` markers (main 3, serial_comm 13, eprom_operations 26, database 2, firmware 6, hardware 5) via an end-anchored strip that preserved preceding inline comments. The 3 `# noqa: F401` markers were left untouched (each still suppresses a real, intentional unused import).
- Verified with ruff as ground truth: full `ruff check firestarter/` clean (F821 would have flagged any missed name; F401 flagged the over-imports that drove the two list corrections); all 6 modules import without error; mypy watermark **41 ≤ 44** (unchanged — DATA-03 did not raise it); full suite **186 passed, 2 xfailed, 29 snapshots** (both Phase 36 xfails remain xfail). Repo-wide star-import grep empty (SC#3 / DATA-03 acceptance).

## Task Commits
All commits made inside the `firestarter_app` submodule on branch `v1.8-app-cleanup`:
1. **Task 1:** `refactor(39-02): named imports + strip F403/F405 noqa — main, serial_comm, eprom_operations (DATA-03)` — `13d07c6`
2. **Task 2:** `refactor(39-02): named imports + strip F403/F405 noqa — database, firmware, hardware; repo-wide star-import grep now empty (DATA-03)` — `5126ae7`

_SUMMARY.md and meta-repo files intentionally NOT committed inside the submodule — the orchestrator owns meta-repo writes._

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — would-block] `main.py` named-import list corrected from 11 names to 2 (ruff ground truth)**
- **Found during:** Task 1 ruff gate.
- **Issue:** RESEARCH Pattern 4 listed 11 names for `main.py`, including 9 `CTRL_*` names. ruff F401 flagged all 9 `CTRL_*` as unused. Investigation: those 9 names appear in `main.py` **only inside a help-text string literal** (the `dev reg` epilog at ~lines 430–438, e.g. `0x100 - CTRL_VPP_VPE_DROP_ENABLE`), not as code references — and there is no `globals()`/`getattr`/`eval` dynamic resolution. The star-import had silently imported them but nothing referenced them; named-importing them produces 9 F401 errors and fails the `ruff check exits 0` acceptance gate.
- **Fix:** Imported only the 2 actually-referenced constants — `FLAG_CHIP_ENABLE`, `FLAG_OUTPUT_ENABLE` (used in `build_arg_flags`). The plan's own directive — "If ruff/AST surfaces a name actually used that is not in the list, add it … treat ruff as ground truth" — governs the inverse case too: drop names that are not used.
- **Verification:** `ruff check firestarter/main.py` clean; `main.py` imports cleanly; full suite green.
- **Committed in:** `13d07c6`

**2. [Rule 3 — would-block] `hardware.py` named-import list corrected from 5 names to 4 (ruff ground truth)**
- **Found during:** pre-edit usage verification + Task 2 ruff gate.
- **Issue:** RESEARCH Pattern 4 listed 5 names for `hardware.py`, including `COMMAND_READ`. `COMMAND_READ` is **not** referenced anywhere in `hardware.py` (only `COMMAND_CONFIG`, `COMMAND_HW_VERSION`, `COMMAND_READ_VPP`, `COMMAND_READ_VPE` are used — the voltage-loop reads use the `_VPP`/`_VPE` variants). Importing `COMMAND_READ` would produce an F401.
- **Fix:** Imported only the 4 actually-referenced names.
- **Verification:** `ruff check firestarter/hardware.py` clean; module imports cleanly.
- **Committed in:** `5126ae7`

---
**Total deviations:** 2 auto-fixed (both would-block — they would have failed the plan's `ruff check exits 0` gate). **Impact:** none on behavior — both are import-list corrections that make the named imports match the modules' true constant usage. The wire protocol, constant values, and all usage sites are byte-identical (GATE-1.8a/c/e). The plan's RESEARCH Pattern-4 lists were a verified-but-stale superset for `main.py` and `hardware.py`; ruff (the plan's designated ground truth) was authoritative. The other 4 modules' lists matched ruff exactly.

## Issues Encountered
- ruff's isort accepted the firmware.py `FIRESTARTER_RELEASE_URL` / `FIRESTARTER_RELEASES_URL` ordering as-written (`ruff check --select I --fix` reported no changes), so no manual reordering was needed.

## User Setup Required
None.

## Next Phase Readiness
- Every `firestarter.constants` name is now explicitly imported, so mypy resolves them by name — the prerequisite Phase 42 needs to tighten the mypy gate.
- No blockers. Plan 39-03 (docs-only markers) follows; it touches `database.py` (pin_conversions comment) and `constants.py` (sync markers) — neither overlaps the named-import blocks edited here.

## Threat Flags
None — import-header-only change. Same names resolve to the same int-literal constants; no runtime, network, serial, auth, or input-surface change (matches plan threat_model T-39-02 / T-39-SC accepted). No package installs. Wire protocol frozen (GATE-1.8a); constant values untouched (GATE-1.8c).

## Self-Check: PASSED
- Repo-wide `grep -r "from firestarter.constants import \*" firestarter/` → empty (DATA-03 / SC#3).
- `grep -rn "noqa: F403\|noqa: F405" firestarter/` → empty (all 55 stripped).
- 3 F401 markers preserved (serial_comm.py:37, firmware.py:30/36, eprom_operations.py:391/407 — each present, count 1 per file).
- `ruff check firestarter/` clean; all 6 modules import without error (no F821 undefined names).
- Full suite: 186 passed, 2 xfailed, 29 snapshots (both Phase 36 xfails remain xfail).
- mypy watermark 41 ≤ 44 (unchanged).
- Commits `13d07c6` (Task 1) and `5126ae7` (Task 2) exist in the `firestarter_app` submodule.

---
*Phase: 39-database-cleanup-chip-resolver*
*Completed: 2026-05-27*

---
phase: 66-db-inclusion-vpp-correction-dispatch-gate
plan: "05"
subsystem: database
tags: [chip-resolver, exceptions, dispatch-gate, support-status, vpp-safety, runtime-guard]

# Dependency graph
requires:
  - phase: 66-db-inclusion-vpp-correction-dispatch-gate
    plan: "04"
    provides: "NON_DISPATCHABLE_ALGO=0x00 for non-supported chips; non_supported_dispatchable gate bucket; SC#3 sim-level invariant test (IN-03)"
provides:
  - "ChipNotImplementedError(EpromOperationError) exception class — authoritative host-side refusal for non-supported chips"
  - "resolve_chip support_status guard: raises ChipNotImplementedError before convert_to_programmer for all support_status != 'supported' chips (protocol-not-implemented/adapter-required/vpp-exceeds-max)"
  - "cli_handlers.map_typed_errors arm: ChipNotImplementedError -> 'Chip not usable:' ClickException"
  - "check_dispatch.py: mirrors _map_data real mem_type derivation (etype fallback when proto==0); D-12 host-guard exemption; WR-02 live count assert; WR-03 cross-check assert"
  - "test_build_db_inclusion.py: 8th CI test realigned to _map_data model + D-12 host-guard exemption"
  - "test_chip_resolver.py: runtime-boundary tests proving M2716 and AT28C04 raise ChipNotImplementedError with no convert_to_programmer call"
affects:
  - Phase 68 (DB-04) — host-refusal guard now shipped in Phase 66; Phase 68 retains per-operation UX/messaging only
  - future chip_resolver callers — all write/read/erase/verify/blank-check flow through resolve_chip; info/list/id unaffected

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "support_status-driven host guard at resolve_chip — fires before convert_to_programmer, prevents any wire dict/serial byte for non-supported chips"
    - "ChipNotImplementedError as EpromOperationError subclass — distinct from ProtocolNotImplementedError (firmware-0xBB)"
    - "check_dispatch.py mirrors _map_data mem_type derivation exactly for simulation truthfulness (D-12)"
    - "get_eprom_config as the raw-config seam for support_status inspection (not carried through _map_data)"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/exceptions.py
    - firestarter_app/firestarter/chip_resolver.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tools/check_dispatch.py
    - firestarter_app/tests/test_build_db_inclusion.py
    - firestarter_app/tests/test_chip_resolver.py
    - firestarter_app/tests/test_consistency_check.py

key-decisions:
  - "D-12 honored: host guard (resolve_chip + ChipNotImplementedError) ships in Phase 66 (pulled forward from Phase 68 DB-04); Phase 68 retains per-operation messaging/UX"
  - "guard reads raw config via db.get_eprom_config (not db.get_eprom/_map_data) because support_status is NOT carried through _map_data into the mapped dict"
  - "check_dispatch.py non_supported_dispatchable list kept as future-regression detector (always empty under D-12 host-guard model); assert not non_supported_dispatchable + WR-02/WR-03 asserts added"
  - "test_consistency_check.py get_eprom_config stub added (Rule 1): resolve_chip now calls get_eprom_config before get_eprom; TEST_CHIP dispatch-chain test required the additional stub"

patterns-established:
  - "resolve_chip is the single safe chokepoint for program-capable ops; info/list/id handlers (cli_handlers lines 327-354) call db.get_eprom/convert_to_programmer directly and are unaffected by the guard"
  - "TDD RED/GREEN commit sequence: test(66-05) -> feat(66-05) per plan tdd=true spec"

requirements-completed: [DB-05]

# Metrics
duration: 40min
completed: 2026-06-12
---

# Phase 66 Plan 05: SC#3/DB-05 Gap-Closure (D-12 host guard) Summary

**ChipNotImplementedError host guard in resolve_chip closes the 12V-VPP hardware-damage path for non-supported chips; check_dispatch.py realigned to _map_data's real mem_type derivation with D-12 host-guard exemption**

## Performance

- **Duration:** ~40 min
- **Started:** 2026-06-12T12:00:00Z
- **Completed:** 2026-06-12T12:39:12Z
- **Tasks:** 2 (TDD task 1 = 3 commits: RED + GREEN + fix)
- **Files modified:** 7

## Accomplishments

- Closed SC#3 BLOCKER on the REAL host path: M2716 (vpp-exceeds-max), M2732 family, AT28C04 (adapter-required), and all 14 non-supported chips now raise ChipNotImplementedError before any wire dict is built or serial byte emitted — driven by support_status, not the incidental etype string
- Proved the guard via TDD runtime-boundary tests: M2716 and AT28C04 both raise ChipNotImplementedError with db.convert_to_programmer mock asserting it was never called (no wire dict, no serial bytes)
- Realigned check_dispatch.py to truthfully model _map_data's real mem_type derivation: 4 vpp-exceeds-max UV-EPROM chips now correctly derive mt=1 -> configure_eprom (the REAL firmware path), yet gate exits 0 because the host guard refuses them (D-12 — gate GREEN because host refuses, not because sim pretends mem_type=None)
- Fixed WR-02 (live non_supported_dispatchable count + assert) and WR-03 (counter cross-check assert non_dispatchable_count == non_supported_count)
- Full suite: 499 tests GREEN, coverage 71.93% (floor 70%); ruff clean on all 7 modified files; mypy strict clean on chip_resolver.py + exceptions.py; diff_db.py exit 0 (no DB churn)

## Task Commits

1. **test(66-05): RED — runtime-boundary tests for ChipNotImplementedError guard** - `1f6cf3b`
   - M2716 vpp-exceeds-max raises ChipNotImplementedError (RED: import fails)
   - AT28C04 adapter-required raises ChipNotImplementedError (RED)
   - W27C512 supported still resolves (regression guard)
   - convert_to_programmer never called when guard fires (no serial bytes)

2. **feat(66-05): GREEN — authoritative host support_status guard in resolve_chip (D-12 / T-66-01)** - `73be10c`
   - ChipNotImplementedError(EpromOperationError) added to exceptions.py
   - resolve_chip reads raw config via get_eprom_config; raises before convert_to_programmer
   - cli_handlers.map_typed_errors: except ChipNotImplementedError arm added (before EpromOperationError)

3. **feat(66-05): Task 2 — realign check_dispatch.py + 8th CI test + Rule 1 fix** - `4057df3`
   - check_dispatch.py: etype fallback when proto==0 (mirrors _map_data); D-12 exemption; WR-02/WR-03
   - test_build_db_inclusion.py 8th test: realigned to _map_data model + D-12; docstring references D-12
   - test_consistency_check.py: get_eprom_config stub added (Rule 1 fix)

## Files Created/Modified

- `/workspaces/firestarter_app/firestarter/exceptions.py` — Added ChipNotImplementedError(EpromOperationError); docstring distinguishes from ProtocolNotImplementedError (firmware-0xBB)
- `/workspaces/firestarter_app/firestarter/chip_resolver.py` — support_status guard: get_eprom_config before convert_to_programmer; not-found precedence preserved
- `/workspaces/firestarter_app/firestarter/cli_handlers.py` — ChipNotImplementedError imported; except arm in map_typed_errors (before EpromOperationError)
- `/workspaces/firestarter_app/tools/check_dispatch.py` — _map_data-mirroring mt derivation; D-12 host-guard exemption with comment block; WR-02 assert + live count; WR-03 assert
- `/workspaces/firestarter_app/tests/test_build_db_inclusion.py` — 8th test realigned; docstring updated to reference D-12 / host guard
- `/workspaces/firestarter_app/tests/test_chip_resolver.py` — 5 new runtime-boundary tests added
- `/workspaces/firestarter_app/tests/test_consistency_check.py` — get_eprom_config stub added (Rule 1 fix); ruff-formatted

## Decisions Made

- Used `db.get_eprom_config(name)` as the raw-config seam for support_status inspection because `_map_data` does NOT carry support_status into the mapped dict — this was the exact mechanism that made the Phase 66-04 simulation incorrect
- ChipNotImplementedError is a new class (not reusing ProtocolNotImplementedError) because ProtocolNotImplementedError is specifically the firmware-0xBB "protocol recognized but not implemented" case; ChipNotImplementedError is a host-side refusal covering all 3 non-supported statuses
- info/list/id display handlers bypass resolve_chip entirely (they call db.get_eprom/convert_to_programmer directly) — guard intentionally does NOT block display of non-supported chips (Phase 68 DB-04 honest reporting intent preserved)
- check_dispatch.py non_supported_dispatchable list is preserved as a future-regression detector (any chip that derives a real handler AND somehow has support_status == "supported" would populate it and FAIL the gate), but is always empty under the D-12 model

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] test_consistency_check.py dispatch-chain test broke after get_eprom_config call added to resolve_chip**
- **Found during:** Task 2 (full test suite run)
- **Issue:** `test_main_dispatch_invokes_consistency_check` monkeypatched `get_eprom` and `convert_to_programmer` but not `get_eprom_config`. The new resolve_chip calls `get_eprom_config` FIRST — returned (None, None) for "TEST_CHIP" and raised ChipNotFoundError, making the test exit with rc=1
- **Fix:** Added `get_eprom_config` stub returning `({"part_number": name, "support_status": "supported"}, "TEST")` alongside the existing `get_eprom` stub
- **Files modified:** `firestarter_app/tests/test_consistency_check.py`
- **Verification:** Test now passes; all 499 suite tests green
- **Committed in:** `4057df3` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug in test broken by production code change)
**Impact on plan:** Necessary correctness fix. No scope creep. The production code change was correct; the test needed an additional stub.

## Known Stubs

None — all data sources are wired. The support_status guard reads live DB data via get_eprom_config.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes introduced. The guard closes T-66-01 as documented in the threat register.

## Issues Encountered

- mypy strict initially rejected `dict` without type args for resolve_chip return type (`[type-arg]`); fixed by using `dict[str, Any]` (ruff UP006 requires lowercase dict; mypy strict requires type args — both satisfied by `dict[str, Any]` with `from typing import Any`)
- ruff UP006 initially triggered on `Dict[str, Any]` import — fixed to use lowercase `dict[str, Any]` (python 3.9+ builtin generics)

## Next Phase Readiness

- SC#3 / DB-05 fully closed at the runtime boundary: non-supported chips are refused by the host before any hardware is driven
- Phase 68 (DB-04) retains its scope: status-specific per-operation UX messages and honest reporting infrastructure
- Phase 67 (DB-02) pinout classification for unclassifiable DIP chips is unaffected
- DB-05 requirement satisfied; D-12 honored

## Self-Check

Files exist check:
- /workspaces/firestarter_app/firestarter/exceptions.py: FOUND
- /workspaces/firestarter_app/firestarter/chip_resolver.py: FOUND
- /workspaces/firestarter_app/firestarter/cli_handlers.py: FOUND
- /workspaces/firestarter_app/tools/check_dispatch.py: FOUND
- /workspaces/firestarter_app/tests/test_chip_resolver.py: FOUND
- /workspaces/firestarter_app/tests/test_build_db_inclusion.py: FOUND

Commits exist check:
- 1f6cf3b (RED tests): FOUND
- 73be10c (feat guard): FOUND
- 4057df3 (Task 2): FOUND

---
*Phase: 66-db-inclusion-vpp-correction-dispatch-gate*
*Completed: 2026-06-12*

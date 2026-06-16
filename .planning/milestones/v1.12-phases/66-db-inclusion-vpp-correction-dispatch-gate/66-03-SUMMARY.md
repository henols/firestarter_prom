---
phase: 66-db-inclusion-vpp-correction-dispatch-gate
plan: "03"
subsystem: database
tags: [build_db, chip_database, support_status, vpp-correction, inclusion-gate, dispatch-gate, tdd-green]

# Dependency graph
requires:
  - phase: 66-01
    provides: diff_db.py@v1.12, chip_database.baseline.json@734chips, test_build_db_inclusion.py@RED
  - phase: 66-02
    provides: check_dispatch.py D-10 rework + three consistency assertions

provides:
  - "build_db.py: NMOS_TRUE_VPP_MV dict + RURP_VPP_CEILING_MV=22000 + 0x34 in KNOWN_PROTOCOLS"
  - "build_db.py: _support_status initialization + Sites A/B/C inclusion + support_status in chip_entry"
  - "chip_database.json: 744-chip capability-honest DB with support_status on every chip"
  - "dispatch_baseline.json: regenerated 744-chip baseline (D-11 authorized deviation)"

affects:
  - 67-pinout-classification (consumes support_status for unclassifiable DIP chips)
  - 68-host-capability-reporting (reads support_status for write/read/verify refusal)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "highest-VPP-wins NMOS alias resolution for combined multi-alias entries"
    - "support_status taxonomy: supported | protocol-not-implemented | adapter-required | vpp-exceeds-max"
    - "adapter-required inclusion: fall-through with status, no handler wired (D-03 HARD)"
    - "snapshot update pattern: --snapshot-update for syrupy, regenerate for golden file on chip-count change"

key-files:
  created: []
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_app/tools/baseline/dispatch_baseline.json
    - firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md
    - firestarter_app/tests/__snapshots__/test_characterization.ambr

key-decisions:
  - "0x34 added to KNOWN_PROTOCOLS so X88C64P passes the gate; _support_status=protocol-not-implemented classifies it downstream"
  - "24-pin hazard EEPROMs: fall-through with adapter-required (not bare skip); D-03 HARD: proto_id unchanged, no handler wired"
  - "NMOS highest-VPP-wins: iterating all part aliases and taking the max vpp ensures the combined INTEL/2732,2732A,M2732,M2732A entry correctly resolves to 25V/vpp-exceeds-max"
  - "RURP_VPP_CEILING_MV=22000 derived from build_db.py L55 comment (RURP shield max ~22V) + v1.7-SHIELD-REVS §6 hardware evidence"
  - "Python 3.12 used for DB regen and gate runs (py3.11 not available — was built from source in Phase 63 but binary is gone; chip_database.json output is version-neutral; gate tools work correctly under 3.12)"
  - "Snapshot/golden updates: test_list syrupy snapshot and v1.3-COVERAGE-MATRIX.md golden file updated as legitimate regression-gate artifacts following chip-count change 734→744"
  - "dispatch_baseline.json regenerated as D-11 authorized deviation — diff is 10 new chips only, all reviewed in this commit"

patterns-established:
  - "support_status as top-level chip_entry key (D-08): always present, sibling of electrical/programming/pinout"
  - "unsupported_reason only on non-supported chips (D-07): conditional append after chip_entry construction"
  - "NMOS VPP override block placed strictly after fm1608/WARNING-5 overrides, before chip_entry (ordering invariant)"

requirements-completed: [DB-01, DB-03, DB-05]

# Metrics
duration: ~40min
completed: "2026-06-12"
tasks_completed: 2
files_modified: 5
---

# Phase 66 Plan 03: DB Inclusion + VPP Correction + Dispatch Gate — Regenerate + Green Summary

**build_db.py reworked with NMOS VPP correction dict (M2716/M2732=25V, M2732A=21V), X88C64P inclusion as protocol-not-implemented, 9 adapter-required 24-pin EEPROMs, and universal support_status field; chip_database.json regenerated to 744 chips; all three gates GREEN (check_dispatch, diff_db, 7/7 inclusion tests).**

## Performance

- **Duration:** ~40 min
- **Started:** 2026-06-12T~11:00Z
- **Completed:** 2026-06-12T~11:40Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Four edits to `build_db.py`: NMOS dict + RURP ceiling constants; 0x34 in KNOWN_PROTOCOLS; `_support_status` initialization before skip gates; Sites A/B/C override blocks; `support_status` as top-level `chip_entry` key with `unsupported_reason` conditionally appended
- DB regenerated to 744 chips (from 734): +1 X88C64P as protocol-not-implemented, +9 24-pin EEPROMs as adapter-required; all 744 chips carry `support_status`; 14 non-supported total
- NMOS VPP corrected: `2732,2732A,M2732,M2732A` → vpp_mv=25000/vpp-exceeds-max (highest-VPP-wins); `M2732A` standalone → vpp_mv=21000/supported; `M2716` entries → vpp_mv=25000/vpp-exceeds-max
- `check_dispatch.py` exits 0: 730 supported, 14 non-supported, 0 regressions, 0 consistency violations
- `diff_db.py` exits 0: all 734 changed chips attributed to RULE_PHASE66; 10 new chips confirmed; 0 unexplained
- All 7 Plan-01 inclusion tests GREEN (were RED); 493-test full suite passes at --cov-fail-under=70
- `dispatch_baseline.json` regenerated to 744 chips (D-11 authorized deviation)

## Task Commits

Each task was committed atomically inside the firestarter_app submodule:

1. **Task 1: build_db.py inclusion gates + NMOS VPP correction + support_status** — `8328d75` (feat)
2. **Task 2: Regenerate chip_database.json + dispatch baseline + golden/snapshot updates** — `bc6d84f` (feat)

## Files Created/Modified

- `/workspaces/firestarter_app/tools/build_db.py` — Sites A/B/C + NMOS dict + RURP ceiling + support_status in chip_entry
- `/workspaces/firestarter_app/firestarter/data/chip_database.json` — 744-chip regenerated DB (do NOT hand-edit)
- `/workspaces/firestarter_app/tools/baseline/dispatch_baseline.json` — 744-chip dispatch baseline (D-11)
- `/workspaces/firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` — golden file updated for chip count 734→744
- `/workspaces/firestarter_app/tests/__snapshots__/test_characterization.ambr` — test_list snapshot updated for new chips

## New Chip Delta (10 chips)

| Part Number | Status | support_status | Notes |
|-------------|--------|----------------|-------|
| X88C64P,X88C64S (XICOR) | NEW | protocol-not-implemented | proto=0x34; DIP24 form only; SOIC24 not included |
| AT28C04,AT28HC04 (ATMEL) | NEW | adapter-required | proto=0x0B; 24-pin damage-hazard |
| AT28C04E,AT28C04F (ATMEL) | NEW | adapter-required | proto=0x0B; 24-pin damage-hazard |
| AT28C16,AT28HC16,AT28HC16L (ATMEL) | NEW | adapter-required | proto=0x0B; 24-pin damage-hazard |
| AT28C16E,AT28C16F (ATMEL) | NEW | adapter-required | proto=0x0B; 24-pin damage-hazard |
| 28C04A (MICROCHIP memory) | NEW | adapter-required | proto=0x0B; 24-pin damage-hazard |
| 28C04AF (MICROCHIP memory) | NEW | adapter-required | proto=0x0B; 24-pin damage-hazard |
| 28C16A (MICROCHIP memory) | NEW | adapter-required | proto=0x0B; 24-pin damage-hazard |
| 28C16AF (MICROCHIP memory) | NEW | adapter-required | proto=0x0B; 24-pin damage-hazard |
| UPD28C04 (NEC) | NEW | adapter-required | proto=0x0B; 24-pin damage-hazard |

## NMOS Entries Corrected

| Part Number | vpp_mv (before) | vpp_mv (after) | support_status |
|-------------|----------------|----------------|----------------|
| 2732,2732A,M2732,M2732A | 18000 | 25000 | vpp-exceeds-max |
| M2716,M2716M | 18000 | 25000 | vpp-exceeds-max |
| ETC2716,M2716 (2 entries) | 18000 | 25000 | vpp-exceeds-max |
| M2732A (2 standalone entries) | 18000 | 21000 | supported |

## Decisions Made

- `0x34` added to `KNOWN_PROTOCOLS` (Site A): X88C64P passes the gate cleanly; `_support_status = "protocol-not-implemented"` classifies it immediately after the gate. The existing WARN-skip fires for all other unknown-protocol chips (DataFlash/FWH/PLCC remain absent).
- Highest-VPP-wins for NMOS aliases: the combined `2732,2732A,M2732,M2732A` entry has both M2732 (25V) and M2732A (21V) in its alias set; iterating and taking `max` yields 25V → `vpp-exceeds-max`. This is the conservative-safe direction.
- Ordering invariant preserved: Site C (NMOS VPP block) is after fm1608 override and `_etype` re-derivation, before `chip_entry` construction (L46-56 documented ordering).
- Python 3.12 used: py3.11 binary absent (was built from source in Phase 63 but the devcontainer was reset). The gates (`check_dispatch.py`, `diff_db.py`, gate tool imports) all function correctly under 3.12. chip_database.json output is version-neutral JSON. Documented here per the py3.12-masks-py3.11 drift trap memory note; no ruff/f-string backslash issues in edited code.

## Deviations from Plan

**1. [Rule 1 - Bug] F541 f-strings without placeholders in _unsupported_reason**
- **Found during:** Task 1 (`ruff check tools/build_db.py`)
- **Issue:** Initial draft used `f"Protocol 0x34..."` and `f"is not implemented..."` but neither string contained a format variable, triggering ruff F541.
- **Fix:** Removed the `f` prefix from both string literals.
- **Files modified:** `firestarter_app/tools/build_db.py`
- **Verification:** `ruff check tools/build_db.py` — only pre-existing I001/E722 errors (not introduced by this plan)
- **Committed in:** `8328d75` (Task 1 commit)

**2. [Rule 2 - Missing Critical] Updated snapshot/golden files for chip-count change**
- **Found during:** Task 2 (full pytest suite run)
- **Issue:** `test_list` (syrupy snapshot) and `test_golden_file_matches` (v1.3-COVERAGE-MATRIX.md golden file) both failed because 10 new chips appear in the DB output. The plan's acceptance criterion assumed these tests would pass automatically ("+1-field support_status change is additive"), but the new chips themselves change the list/matrix output.
- **Fix:** Updated syrupy snapshot via `--snapshot-update`; regenerated golden file via `generate_matrix()`. Both changes correctly reflect the new legitimate DB state.
- **Files modified:** `tests/__snapshots__/test_characterization.ambr`, `tests/golden/v1.3-COVERAGE-MATRIX.md`
- **Verification:** 493 tests pass; `--cov-fail-under=70` met; both tests GREEN
- **Committed in:** `bc6d84f` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 Rule 1 ruff bug, 1 Rule 2 missing snapshot/golden update)
**Impact on plan:** Both auto-fixes necessary for correctness and test-suite integrity. No scope creep.

## Issues Encountered

- Python 3.11 not available (Phase 63 built it from source but the devcontainer was reset between sessions). Used Python 3.12 as it produces functionally identical results for this use case. Documented as a decision.
- `dispatch()` signature: the function takes `(protocol, mem_type)` not `(chip)` — corrected in the dispatch baseline capture inline script.

## Next Phase Readiness

- All three gate tools exit 0 on the 744-chip DB.
- `support_status` is now a stable machine-readable field in every chip record; Phase 67 (pinout classification) and Phase 68 (host capability reporting) can consume it.
- No blockers.

---
*Phase: 66-db-inclusion-vpp-correction-dispatch-gate*
*Completed: 2026-06-12*

## Known Stubs

None — all `support_status` values, `unsupported_reason` strings, and NMOS VPP corrections are grounded in real data (datasheets, hardware evidence). No placeholder text or hardcoded empty values flow to any display layer.

## Threat Flags

None. The chip surface is additive (new entries have `support_status` != `supported` and no working handler — D-03 HARD). T-66-06/T-66-07/T-66-08/T-66-09 mitigations verified:
- T-66-06: highest-VPP-wins is conservative (refuses ambiguous high-VPP parts)
- T-66-07: adapter-required 9 EEPROMs keep original proto and are NOT routed to configure_eeprom28c; check_dispatch assertion 1 confirms
- T-66-08: diff_db.py PASS with every change attributed to RULE_PHASE66; D-11 delta enumerated above
- T-66-09: py3.12 used (py3.11 absent); gate tools functionally equivalent; noted as decision

## Self-Check: PASSED

Files exist:
- `/workspaces/firestarter_app/tools/build_db.py` — FOUND (contains RURP_VPP_CEILING_MV=22000, NMOS_TRUE_VPP_MV, 0x34 in KNOWN_PROTOCOLS, support_status in chip_entry)
- `/workspaces/firestarter_app/firestarter/data/chip_database.json` — FOUND (744 chips, all with support_status)
- `/workspaces/firestarter_app/tools/baseline/dispatch_baseline.json` — FOUND (744 chips)
- `/workspaces/.planning/phases/66-db-inclusion-vpp-correction-dispatch-gate/66-03-SUMMARY.md` — FOUND (this file)

Commits exist in firestarter_app submodule:
- `8328d75` — feat(66-03): build_db.py inclusion gates + NMOS VPP correction + support_status
- `bc6d84f` — feat(66-03): regenerate chip_database.json (744 chips) + dispatch baseline (D-11)

Gate results:
- `check_dispatch.py`: PASS (730 supported; 14 non-supported; 0 regressions; 0 violations)
- `diff_db.py`: PASS (734 RULE_PHASE66; 10 new; 0 missing)
- `test_build_db_inclusion.py`: 7/7 PASSED
- Full suite: 493 passed, --cov-fail-under=70 met

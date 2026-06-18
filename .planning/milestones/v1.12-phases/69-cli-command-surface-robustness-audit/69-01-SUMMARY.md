---
phase: 69-cli-command-surface-robustness-audit
plan: "01"
subsystem: firestarter_app
tags: [ic_layout, display, pin-map, list-vs-int, bug-fix, unit-test]
dependency_graph:
  requires: []
  provides: [SC#1-root-fix, SC#3-unit-regression]
  affects: [firestarter_app/firestarter/ic_layout.py, firestarter_app/tests/test_ic_layout.py]
tech_stack:
  added: []
  patterns: [inline-scalar-extraction, module-scoped-fixture, parametrized-test]
key_files:
  created:
    - firestarter_app/tests/test_ic_layout.py
  modified:
    - firestarter_app/firestarter/ic_layout.py
    - firestarter_app/tests/test_cli_handlers.py
    - firestarter_app/tests/test_characterization.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
decisions:
  - "Inline scalar-extraction (val[0] if isinstance(val, list) else val) at each pin-field site — no named helper, matching database.get_bus_config pattern exactly"
  - "Rule 1 auto-fix: updated test_info_chip_resolution_happy_path and test_info_known_chip exit_code 1→0 + regenerated characterization snapshot"
metrics:
  duration: "~20min"
  completed: "2026-06-15T08:03:14Z"
  tasks_completed: 2
  files_modified: 5
---

# Phase 69 Plan 01: ic_layout list-vs-int root fix + unit regression Summary

**One-liner:** Scalar-extraction fix at all 5 rw/vpp/oe-pin sites in `_generate_pin_names_for_display`; new parametrized unit test file pins the crash class.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Scalar-extract list-valued pin fields at every site | a1b8a31 | firestarter/ic_layout.py |
| 2 | Create tests/test_ic_layout.py + update broken assertions | b5d1ced | tests/test_ic_layout.py, test_cli_handlers.py, test_characterization.py, test_characterization.ambr |

## What Was Built

**Task 1 — Root fix in `_generate_pin_names_for_display`:**

The function compared `pin_map_details["vpp-pin"]`, `["oe-pin"]`, and `["rw-pin"]` directly against `pin_count` (int), but `pinouts.json` stores these fields as single-element lists (e.g. `[22]`). This caused a live `TypeError: '<=' not supported between instances of 'list' and 'int'` for every chip that has a pin-map entry, crashing `firestarter info` universally.

The fix mirrors the existing `database.get_bus_config` inline pattern (lines 286-289):
```python
rw = pin_map_details["rw-pin"]
rw = rw[0] if isinstance(rw, list) else rw
if rw <= pin_count:
    pin_names[rw - 1] = "R/W(WE)"
```
Applied at all 5 affected sites: rw-pin (2 sites), vpp-pin (2 sites), oe-pin inside vpp block + standalone oe block (3 sites). The `isinstance` guard makes it tolerant of both list and bare-int forms.

`pinouts.json` is untouched — list-valued storage is correct and intentional.

**Task 2 — New `tests/test_ic_layout.py`:**

Parametrized test over 4 representative chips:
- `W27C512` — DIP28, shared vpp/oe-pin=[22] (list-valued shared pin)
- `AT28C256` — DIP28, rw-pin=[27], oe-pin=[22] (rw + oe both lists)
- `2732` — DIP24, vpp-exceeds-max, shared vpp/oe-pin=[20]
- `M2716` — DIP24, vpp-exceeds-max, distinct vpp and oe pins

Plus `build_specifications` happy-path test for W27C512, and bare-int tolerance test.

**Rule 1 auto-fixes (deviations):**
- `test_cli_handlers.py::test_info_chip_resolution_happy_path` — previously asserted `exit_code == 1` (the broken crash behavior). Updated to `0` with corrected docstring.
- `test_characterization.py::test_info_known_chip` — previously asserted `rc == 1`. Updated to `0`, regenerated syrupy snapshot (now shows chip layout output on stdout, empty stderr).

## Verification Results

- `python -c "... db.get_eprom('2732') ... print('OK')"` → prints `OK` (no traceback)
- `python -m pytest tests/test_ic_layout.py -q` → 6/6 tests pass
- `python -m pytest --tb=short` → 505/505 tests pass (0 failures)
- `ruff check` + `ruff format --check` → clean on all 5 modified files
- `git diff --stat firestarter/data/pinouts.json` → empty (SC#4 precondition)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated exit-code assertions for the fixed crash behavior**

- **Found during:** Task 2 (full test run after fix)
- **Issue:** Two existing tests (`test_info_chip_resolution_happy_path`, `test_info_known_chip`) asserted `exit_code == 1` / `rc == 1` — the correct assertion BEFORE the fix, now wrong. The PATTERNS.md documented these as "must change to 0 after fix".
- **Fix:** Updated docstrings + changed assertions to `0`; regenerated the characterization snapshot for `test_info_known_chip` via `pytest --snapshot-update`. Both files already mentioned in the PATTERNS.md change list.
- **Files modified:** `tests/test_cli_handlers.py`, `tests/test_characterization.py`, `tests/__snapshots__/test_characterization.ambr`
- **Commit:** b5d1ced

## Success Criteria Assessment

- **SC#1 (root fix):** SATISFIED at the unit level. All 5 comparison/index sites in `_generate_pin_names_for_display` now scalar-extract list-valued pin fields. Full SC#1 confirmation (every DB chip `info`) deferred to Plan 02's CLI smoke audit.
- **SC#3 (regression tests):** Unit-level half SATISFIED. `test_ic_layout.py` pins the list-valued-pin display behavior; CLI-level regression to be added in Plan 02.

## Known Stubs

None. The fix wires real pin-field extraction; no placeholder or TODO values introduced.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. This is a pure display-layer fix in read-only host code. T-69-01 (denial-of-display) is mitigated as planned.

## Self-Check: PASSED

- `firestarter_app/firestarter/ic_layout.py` — modified, fix verified
- `firestarter_app/tests/test_ic_layout.py` — created (78 lines, min_lines=40 satisfied)
- Commits `a1b8a31` and `b5d1ced` exist in `v1.12-protocol-dispatch-hardening`
- 505 tests green, ruff-clean, pinouts.json unchanged

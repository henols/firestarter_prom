---
phase: 69-cli-command-surface-robustness-audit
plan: "02"
subsystem: firestarter_app
tags: [cli-smoke-audit, info-display, support-status, presenter, regression-tests]
dependency_graph:
  requires:
    - phase: 69-01
      provides: [SC#1-root-fix, ic_layout list-vs-int fix, test_ic_layout.py]
  provides: [SC#2-command-surface-smoke-audit, SC#3-cli-regression-all-three-statuses, presenter-happy-path]
  affects: [firestarter_app/tests/test_cli_handlers.py, firestarter_app/tests/test_eprom_info.py]
tech_stack:
  added: []
  patterns: [real-presenter-injection, support-status-refusal-pin, sc3-per-status-coverage]
key_files:
  created: []
  modified:
    - firestarter_app/tests/test_cli_handlers.py
    - firestarter_app/tests/test_eprom_info.py
key_decisions:
  - "Inject REAL EpromConsolePresenter(db) via make_app_context(db=db, eprom_presenter=...) — Pitfall 1 avoidance: the default Mock returns None and masks the ic_layout fix"
  - "All three Phase 66 non-supported statuses pinned at CLI surface: vpp-exceeds-max (M2716), adapter-required (AT28C16), protocol-not-implemented (X88C64P) — matches SC#3 contract exactly"
  - "info bypasses resolve_chip — all non-supported chips must DISPLAY at exit 0; only chip-ops (read/write/etc.) hit the ChipNotImplementedError guard"
  - "No new DB churn: firestarter/data/ unchanged; X88C64P is already the sole protocol-not-implemented chip in chip_database.json (line 14849)"

requirements-completed: [SC#2, SC#3]

duration: ~20min
completed: 2026-06-15
---

# Phase 69 Plan 02: CLI Command-Surface Smoke Audit + SC#3 per-status Coverage Summary

**CliRunner smoke tests pin all 14 CLI surfaces crash-free; all three Phase 66 non-supported statuses (vpp-exceeds-max/M2716, adapter-required/AT28C16, protocol-not-implemented/X88C64P) covered at CLI level; `prepare_detailed_eprom_data` happy path unblocked.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-06-15T08:10:00Z
- **Completed:** 2026-06-15T08:30:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Updated `test_info_chip_resolution_happy_path` to inject a REAL `EpromConsolePresenter(db)` — Pitfall 1: the default Mock masks the ic_layout fix
- Added 4 new info regression tests covering SC#1 (2732 list-valued pin), vpp-exceeds-max (M2716), adapter-required (AT28C16), and supported (W27C512) chips
- Closed SC#3 protocol-not-implemented gap: `test_read_protocol_not_implemented_typed_refusal` (X88C64P read → exit 1, typed refusal) + `test_info_protocol_not_implemented_no_crash` (X88C64P info → exit 0)
- Added `test_read_non_supported_typed_refusal` (M2716 read → exit 1, no traceback) pinning the ChipNotImplementedError → clean-exit-1 path at CLI surface
- Added `test_prepare_detailed_eprom_data_happy_path` in test_eprom_info.py — previously un-testable due to ic_layout crash now fixed in 69-01
- All CLI command surfaces already had smoke tests from prior phases (list/info/search/read/write/verify/blank/erase/id/vpp/vpe/hw/config/fw/dev subcommands); 513/513 tests green

## Task Commits

1. **Task 1: Flip info happy-path assertions and add info regression tests with a REAL presenter** — `4565342` (test)
2. **Task 2: Command-surface smoke audit + protocol-not-implemented coverage + prepare_detailed_eprom_data happy path** — `c3631bd` (test)

## Files Created/Modified

- `/workspaces/firestarter_app/tests/test_cli_handlers.py` — Updated `test_info_chip_resolution_happy_path` to inject REAL presenter; added 5 new info tests + 2 non-supported chip-op refusal tests (57 → 61 tests total in this file)
- `/workspaces/firestarter_app/tests/test_eprom_info.py` — Added `test_prepare_detailed_eprom_data_happy_path` for W27C512 (7 → 8 tests)

## Decisions Made

1. **REAL presenter injection pattern**: For all `info` tests, pass `make_app_context(db=db, eprom_presenter=EpromConsolePresenter(db))`. The factory's default `Mock(spec=EpromConsolePresenter)` returns `None` from `prepare_detailed_eprom_data`, which causes the handler to `sys.exit(1)` — masking the fix. Existing tests that skip `obj=app` work because the CLI group callback builds a real `EpromConsolePresenter` when no obj is pre-supplied.

2. **X88C64P lookup works via part_number alias**: `db.get_eprom("X88C64P")` resolves the chip despite `part_number="X88C64P,X88C64S"` (comma-separated alias). `resolve_chip("X88C64P", db=db)` raises `ChipNotImplementedError` as expected; `info X88C64P` exits 0 via the display path that bypasses `resolve_chip`.

3. **No new DB changes needed**: X88C64P was already the sole `protocol-not-implemented` chip in the packaged DB from Phase 66-03. SC#3 is satisfied without touching chip_database.json.

## Deviations from Plan

None — plan executed exactly as written. The dependency note reconciled correctly: 69-01's Rule-1 auto-fix had already flipped `test_info_chip_resolution_happy_path` from exit 1 to exit 0, and the plan's Task 1 correctly upgraded it to inject a REAL presenter (additive, not a re-flip).

## Known Stubs

None. All new tests wire real chip data through the fixed display path.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. Pure test additions. T-69-03 (denial-of-display) fully mitigated; T-69-04 (non-supported → typed refusal) confirmed at CLI surface.

## Self-Check: PASSED

- `firestarter_app/tests/test_cli_handlers.py` — modified, REAL presenter pattern applied
- `firestarter_app/tests/test_eprom_info.py` — modified, happy-path test added
- Commits `4565342` and `c3631bd` exist in `v1.12-protocol-dispatch-hardening`
- 513 tests green, ruff-clean, firestarter/data/ unchanged
- All three SC#3 non-supported statuses pinned: M2716 (vpp-exceeds-max), AT28C16 (adapter-required), X88C64P (protocol-not-implemented)

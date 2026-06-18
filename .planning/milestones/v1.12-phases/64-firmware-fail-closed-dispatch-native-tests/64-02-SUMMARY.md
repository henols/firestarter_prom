---
phase: 64-firmware-fail-closed-dispatch-native-tests
plan: "02"
subsystem: firmware
tags: [dispatch, fail-closed, not-implemented, native-tests, flash-gate, safety]
dependency_graph:
  requires:
    - phase: 64-01
      provides: configure_not_implemented handler + named dispatch arms + test_not_implemented suite
  provides:
    - fail-closed-dispatch-invariants-verified-by-native-tests
    - flash-budget-gate-passed (Leonardo 88.9% <= 90%)
  affects: [firestarter/src/proms/memory.cpp, firestarter/test/native/avr/test_not_implemented]
tech_stack:
  added: []
  patterns: [verification-only-plan, deviation-reconciliation-via-coverage-audit]
key_files:
  created: []
  modified: []
key_decisions:
  - "TEST-01 satisfied by existing 64-01 suite at test_not_implemented/ — all 6 required invariants present; creating a duplicate test_dispatch/test_not_implemented.cpp would cause a linker collision (two setUp/main) and is not done"
  - "TEST-02 satisfied: Leonardo 88.9% (25,482/28,672 B) remains under 90% ceiling; Uno 72.4% (23,344/32,256 B) — baseline carried forward from 64-01 (not 64-02 additions)"
patterns-established:
  - "Coverage-first deviation reconciliation: when a Wave-N+1 plan assumes a file path that collides with Wave-N's structural deviation, audit the existing suite for full invariant coverage before creating duplicates"
requirements-completed: [TEST-01, TEST-02]
duration: ~12min
completed: "2026-06-11"
---

# Phase 64 Plan 02: Native Test Gate + Flash Budget Verification Summary

**All fail-closed dispatch invariants locked by 6-test native Unity suite (64-01); Leonardo 88.9% flash (25,482 B / 28,672 B) within the 90% ceiling; Uno 72.4% clean — TEST-01 and TEST-02 satisfied.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-06-11
- **Completed:** 2026-06-11
- **Tasks:** 2
- **Files modified:** 0 (verification + reconciliation plan — no new source files required)

## Accomplishments

- Audited the 64-01 `test_not_implemented/` suite and confirmed complete coverage of all 6 required invariants (0x99 generic, 0x11/0x2A/0x2B/0x2C named arms, protocol==0+mem_type=1 fallback)
- Confirmed the link-collision rationale from 64-01 is genuine: both `test_configure_memory.cpp` and `test_not_implemented.cpp` define `setUp()`, `tearDown()`, `main()`, and `test_protocol_zero_with_mem_type_eprom_dispatches_eprom()` — merging them into a single binary is impossible
- Ran `pio test -e native` and confirmed all 49/49 test cases pass across all 8 native suites
- Ran `pio run -e leonardo` and confirmed flash utilization at 88.9% (25,482/28,672 B), under the 90% ceiling
- Ran `pio run -e uno` clean at 72.4% (23,344/32,256 B)

## Task Commits

This plan is a verification + reconciliation plan. No new source files were needed. No submodule commits were required for this plan.

1. **Task 1: Native test coverage audit** — satisfied by existing 64-01 suite; no new commit
2. **Task 2: Flash-budget gate** — build verification only; no new commit

**Plan metadata:** committed to meta-repo (this SUMMARY.md)

## Native Test Results — Per-Suite Breakdown

| Suite | Tests | Status |
|-------|-------|--------|
| native/avr/test_not_implemented | 6 | PASSED |
| native/avr/test_dispatch | 15 | PASSED |
| native/avr/test_read_timing | (included) | PASSED |
| native/avr/test_cobs_cmd_frame | (included) | PASSED |
| native/avr/test_cobs_data_frame | (included) | PASSED |
| native/avr/test_frame_vectors | (included) | PASSED |
| native/avr/test_data_input | (included) | PASSED |
| native/avr/test_messages | (included) | PASSED |
| **Total** | **49/49** | **ALL PASSED** |

## Coverage Audit — Required Invariants (TEST-01)

All 6 required invariants from the plan's must_haves are proven by the existing `test_not_implemented/test_not_implemented.cpp` suite:

| Invariant | Test Function | Status |
|-----------|---------------|--------|
| 0x99 unknown non-zero → ERROR + NULL pointers (SC#1, SC#3) | `test_unknown_nonzero_protocol_0x99_not_implemented` | GREEN |
| 0x11 (FWH) named arm → not-implemented (SC#4) | `test_protocol_0x11_fwh_not_implemented` | GREEN |
| 0x2A (GAL) named arm → not-implemented (SC#4) | `test_protocol_0x2A_gal_not_implemented` | GREEN |
| 0x2B (GAL) named arm → not-implemented (SC#4) | `test_protocol_0x2B_gal_not_implemented` | GREEN |
| 0x2C (PLD) named arm → not-implemented (SC#4) | `test_protocol_0x2C_pld_not_implemented` | GREEN |
| protocol==0 + mem_type=1 → not-ERROR (DISP-02, SC#2) | `test_protocol_zero_with_mem_type_eprom_dispatches_eprom` | GREEN |

All pre-existing `test_dispatch` cases (15 tests including `test_unknown_protocol_with_unknown_mem_type_errors` and `test_protocol_zero_with_mem_type_eprom_dispatches_eprom`) remain green.

## Flash Budget Results (TEST-02)

| Board | Flash Used | Flash Total | Utilization | v1.12 Start Baseline | Delta | Gate |
|-------|-----------|-------------|-------------|----------------------|-------|------|
| Leonardo | 25,482 B | 28,672 B | **88.9%** | 88.4% / 25,354 B | +128 B / +0.5% | PASS (<= 90%) |
| Uno | 23,344 B | 32,256 B | **72.4%** | 72.0% / 23,216 B | +128 B / +0.4% | PASS |

The +128 B increase on both boards reflects the Phase 64-01 additions (configure_not_implemented TU + named dispatch arms). Leonardo remains well under the 90% ceiling with 3,190 B headroom.

## Decisions Made

- **D-01 (coverage-first reconciliation):** TEST-01 is satisfied by the 64-01 suite in `test_not_implemented/`. The plan assumed a new `test_dispatch/test_not_implemented.cpp` sibling, but this would cause a linker collision. Since the existing suite covers all required invariants with 6 tests (verified exhaustively), no duplicate suite was created. This is a reconciliation of the Wave-2 plan assumption with Wave-1's structural deviation — not a reduction in test coverage.

## Deviations from Plan

### Plan assumption diverged from Wave-1 reality

**Wave-2 plan assumed:** A new sibling file `test/native/avr/test_dispatch/test_not_implemented.cpp` would be created in this plan.

**Wave-1 reality (64-01 deviation):** Wave-1 discovered a link collision — PlatformIO merges all `.cpp` files in a directory into one test binary. Both `test_configure_memory.cpp` and the proposed new file define `setUp()`, `tearDown()`, `main()`, and a function named `test_protocol_zero_with_mem_type_eprom_dispatches_eprom`. This would produce `multiple definition of setUp` linker errors.

**Wave-1 resolution:** Created `test/native/avr/test_not_implemented/` as a separate binary (separate directory) with its own `host_stubs.cpp` and `avr/pgmspace.h` shim. Updated `platformio.ini` to add the new directory to `test_filter` and `-I` paths.

**Wave-2 reconciliation:** The existing `test_not_implemented/` suite fully covers all required invariants from this plan (6/6 tests, all GREEN). Creating a duplicate `test_dispatch/test_not_implemented.cpp` is:
- Unnecessary (coverage is complete)
- Harmful (would break the build via link collision)
- Structurally wrong (wrong binary)

**Resolution:** Treat TEST-01 as satisfied by the 64-01 suite. Document the reconciliation here. No new files created in this plan.

**Rationale:** The plan's must_haves specify INVARIANTS to be proven by native tests, not a specific file path. The invariants are proven. The plan's `artifacts:` path specification was aspirational (based on a structural assumption that turned out to be incorrect due to the link-collision reality). The wave-2 executor context explicitly authorized this reconciliation.

## Files Created/Modified

None. This plan is verification-only.

## Issues Encountered

None. All builds and tests passed cleanly on the first run.

## Known Stubs

None.

## Threat Flags

No new network endpoints, auth paths, file access patterns, or schema changes. This plan verified the Wave-1 mitigations for T-64-04 and T-64-05.

## Next Phase Readiness

- Phase 64 complete: fail-closed dispatch fully implemented (64-01) and regression-locked by native tests (64-01/64-02)
- Leonardo flash at 88.9% — 3,190 B headroom for remaining v1.12 phases
- Ready for Phase 65: Host Graceful Handling (`ProtocolNotImplementedError` + CLI message)

## Self-Check: PASSED

Files verified:
- `/workspaces/firestarter/test/native/avr/test_not_implemented/test_not_implemented.cpp` — FOUND (6 tests, all invariants covered)
- `/workspaces/firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — FOUND (15 tests, all green)

Build results verified:
- `pio test -e native`: 49/49 PASS
- `pio run -e uno`: 72.4% flash (23,344/32,256 B) — PASS
- `pio run -e leonardo`: 88.9% flash (25,482/28,672 B) — PASS (<= 90%)

---
*Phase: 64-firmware-fail-closed-dispatch-native-tests*
*Completed: 2026-06-11*

---
phase: 64-firmware-fail-closed-dispatch-native-tests
plan: "01"
subsystem: firmware
tags: [dispatch, fail-closed, not-implemented, safety, native-tests]
dependency_graph:
  requires: [63-01]
  provides: [configure_not_implemented, fail-closed-dispatch-arms, native-test-suite]
  affects: [firestarter/src/proms/memory.cpp, firestarter/include/not_implemented.h, firestarter/src/proms/not_implemented.cpp]
tech_stack:
  added: [not_implemented.h, not_implemented.cpp, test_not_implemented.cpp]
  patterns: [tdd-red-green, configure_*-handler-pattern, protocol-prefix-dispatch]
key_files:
  created:
    - firestarter/include/not_implemented.h
    - firestarter/src/proms/not_implemented.cpp
    - firestarter/test/native/avr/test_not_implemented/test_not_implemented.cpp
    - firestarter/test/native/avr/test_not_implemented/host_stubs.cpp
    - firestarter/test/native/avr/test_not_implemented/avr/pgmspace.h
  modified:
    - firestarter/src/proms/memory.cpp
    - firestarter/CLAUDE.md
    - firestarter/platformio.ini
decisions:
  - "D-01 honored: configure_not_implemented is a self-contained handler (not inline emit); emits MSG_ERR_PROTOCOL_NOT_IMPLEMENTED (0xBB) with (uint8_t) cast, sets RESPONSE_CODE_ERROR, NULLs all 3 op pointers — independently testable unit"
  - "D-02 honored: named arms (0x11/0x2A/0x2B/0x2C) + generic protocol!=0 catch-all; both placed after SRAM arm, before mem_type fallback"
  - "Test suite placed in separate test/native/avr/test_not_implemented/ directory (deviation from PATTERNS.md suggestion) — required to avoid setUp/main link collision with test_dispatch binary when PIO merges all files in a directory into one binary"
metrics:
  duration: "~8 minutes"
  completed: "2026-06-11"
  tasks_completed: 2
  files_changed: 8
---

# Phase 64 Plan 01: Fail-Closed Dispatch Handler + Native Tests Summary

**One-liner:** Self-contained `configure_not_implemented()` handler + named (0x11/0x2A/0x2B/0x2C) and generic (protocol!=0) dispatch arms that route all non-zero unimplemented protocols to MSG_ERR_PROTOCOL_NOT_IMPLEMENTED (0xBB) with zero hardware side effects, eliminating the 12V VPP hazard (T-64-01).

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 (RED) | Failing tests for configure_not_implemented | 0f2a498 | test_not_implemented.cpp, host_stubs.cpp, avr/pgmspace.h, platformio.ini |
| 1 (GREEN) | configure_not_implemented handler + dispatch wiring | 30bbe4a | not_implemented.h, not_implemented.cpp, memory.cpp |
| 2 | CLAUDE.md Protocol Dispatch table update | b71c6fd | CLAUDE.md |

## What Was Built

### New Translation Unit: `configure_not_implemented()`

A self-contained handler at `firestarter/src/proms/not_implemented.cpp` that:
- Explicitly NULLs all three operation pointers (`firestarter_operation_init`, `_main`, `_end`) — belt-and-suspenders for independent testability (D-01)
- Emits `LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, (uint8_t)handle->protocol)` — sends 0xBB wire message with the offending protocol value as a u8 (cast required: `handle->protocol` is `uint32_t`)
- Sets `handle->response_code = RESPONSE_CODE_ERROR`
- No `rurp_*` calls, no hardware register writes — zero hardware side effects

### Dispatch Arms in `configure_memory()`

Two new arms inserted after the SRAM arm (`0x0E/0x27/0x28/0x29`) and before the `mem_type` fallback:

1. **Named infeasibility arms (DISP-04):** `if (protocol == 0x11 || protocol == 0x2A || protocol == 0x2B || protocol == 0x2C)` — FWH and GAL/PLD protocols; explicitly named for documented infeasibility intent + per-protocol tests
2. **Generic fail-closed guard (DISP-01):** `if (protocol != 0)` — catches any other non-zero unrecognized protocol; eliminates the silent mem_type fallback hazard

The `mem_type` fallback chain (steps 7–11) is now reachable **only** when `protocol == 0` (DISP-02).

### Native Test Suite: `test_not_implemented.cpp`

6 Unity tests in a new separate directory `test/native/avr/test_not_implemented/`:
- 4 named arm tests: `0x11`, `0x2A`, `0x2B`, `0x2C` → RESPONSE_CODE_ERROR + all-3-NULL pointers
- 1 generic catch-all test: `0x99` → RESPONSE_CODE_ERROR + all-3-NULL pointers
- 1 legacy fallback re-assertion: `protocol==0, mem_type=1` still routes to configure_eprom (NOT error)

All 6 tests GREEN. All 15 pre-existing `test_dispatch` tests still Green. Full native suite: **49/49 PASS**.

### CLAUDE.md Update

`firestarter/CLAUDE.md` § "Protocol Dispatch" dispatch table updated:
- Added step 6a (named infeasibility arms)
- Added step 6b (generic fail-closed guard)
- Step 7 reworded: "reachable ONLY when protocol == 0 (DISP-02)"
- Added fail-closed invariant paragraph below the table

### Build Results

- `pio run -e uno`: SUCCESS — 72.4% flash (23,344/32,256 B), 75.4% RAM (1,544/2,048 B)
- Flash gate (Leonardo ≤ 90%): not checked in this plan — Leonardo build verified in Plan 64-02

## Deviations from Plan

### Auto-fix: Separate test directory required (structural, not documented in PATTERNS.md)

**Found during:** Task 1 RED phase  
**Issue:** PATTERNS.md stated "No platformio.ini change needed" and suggested dropping `test_not_implemented.cpp` under `test/native/avr/test_dispatch/`. However, PlatformIO compiles all `.cpp` files in a directory into a single test binary — both `test_configure_memory.cpp` and `test_not_implemented.cpp` define `setUp()`, `tearDown()`, `main()`, and `test_protocol_zero_with_mem_type_eprom_dispatches_eprom()`. Linker error: multiple definition of `setUp`.  
**Fix:** Created separate `test/native/avr/test_not_implemented/` directory with its own `host_stubs.cpp` and `avr/pgmspace.h` shim (mirroring the test_dispatch pattern). Added the new directory to `platformio.ini` `test_filter` and `-I` include path.  
**Impact:** 2 extra support files created; platformio.ini modified; `test_filter` now has 8 entries (was 7). No behavior change to tests.  
**Files modified:** `platformio.ini`, created `test_not_implemented/host_stubs.cpp`, `test_not_implemented/avr/pgmspace.h`  
**Commits:** 0f2a498

### TDD cycle spans Task 1 + Task 2 production code

**Found during:** Task 1 GREEN phase  
**Issue:** Task 1 tests (`test_not_implemented.cpp`) assert on the full dispatch path via `configure_memory()` — the handler alone (without dispatch wiring) does not make the tests GREEN. The dispatch wiring was planned for Task 2.  
**Fix:** Implemented the dispatch wiring (memory.cpp edits + #include) as part of Task 1's GREEN phase commit. Task 2's commit carries only the CLAUDE.md documentation update.  
**Impact:** Minor reordering of work within the plan; all acceptance criteria for both tasks are fully met.

## TDD Gate Compliance

| Gate | Status |
|------|--------|
| RED commit (`test(64-01)`) | `0f2a498` — 5 tests fail, 1 passes |
| GREEN commit (`feat(64-01)`) | `30bbe4a` — 6/6 tests pass, 15/15 sibling tests pass |
| REFACTOR | Not needed — code is minimal and clean |

## Known Stubs

None. The `configure_not_implemented()` handler is fully wired and functional. The NULL operation pointers are intentional (not stubs) — a not-implemented handler should not dispatch to any operation.

## Threat Flags

No new network endpoints, auth paths, file access patterns, or schema changes introduced. The dispatch arms close an existing threat (T-64-01: 12V VPP hazard via mem_type fallback) with zero new attack surface.

## Self-Check: PASSED

Files created:
- /workspaces/firestarter/include/not_implemented.h — FOUND
- /workspaces/firestarter/src/proms/not_implemented.cpp — FOUND
- /workspaces/firestarter/test/native/avr/test_not_implemented/test_not_implemented.cpp — FOUND

Commits:
- 0f2a498 — test(64-01): add failing tests for configure_not_implemented dispatch
- 30bbe4a — feat(64-01): add configure_not_implemented handler and fail-closed dispatch arms
- b71c6fd — docs(64-01): update CLAUDE.md Protocol Dispatch table for fail-closed arms

Build gate: `pio run -e uno` — SUCCESS (72.4% flash)
Native tests: 49/49 PASS

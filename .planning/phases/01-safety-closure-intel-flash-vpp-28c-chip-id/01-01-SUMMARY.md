---
phase: 01-safety-closure-intel-flash-vpp-28c-chip-id
plan: 01-01
subsystem: firmware
tags: [arduino, unity-test, platformio, safety, intel-flash, native-test]

# Dependency graph
requires:
  - phase: v1.0-milestone (flash_intel.cpp, eprom.cpp, test_dispatch/ infrastructure)
    provides: flash_intel_write_init, eprom_check_vpp analog, test_dispatch Unity harness

provides:
  - static flash_intel_check_vpp() helper in flash_intel.cpp (SAF-04 VPP pre-pulse check)
  - Call-site in flash_intel_write_init after delay(500), before chip_id branch
  - test_flash_intel_vpp/ Unity suite (5 tests) on [env:native] with mockable VPP/hw-rev stubs

affects:
  - 01-02 (AT28C chip-id plan — same phase, same test infrastructure pattern)
  - Phase 4 HW-05 (hardware validation deferred — requires this firmware path to exist)
  - SAF-06 (VPP half closed by this plan; chip-id half in 01-02)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Suite-local link-time strong override for rurp_* mocks (Option M1 from RESEARCH.md): per-test-directory host_stubs.cpp with TU-private static + setter pattern"
    - "ArduinoFake delay() setup in setUp() required when operation_init calls delay() — When(Method(ArduinoFake(), delay)).AlwaysReturn()"
    - "Inline-copy VPP check (not shared helper extraction) preserves v1.0 eprom_check_vpp byte-identical"

key-files:
  created:
    - firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp
    - firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp
    - firestarter/test/native/avr/test_flash_intel_vpp/avr/pgmspace.h
  modified:
    - firestarter/src/proms/flash_intel.cpp
    - firestarter/.gitignore

key-decisions:
  - "D-04 (inline-copy): flash_intel_check_vpp is a static TU-private helper in flash_intel.cpp — eprom_check_vpp left byte-identical (no shared extraction)"
  - "D-01 (failure semantics): low VPP -> WARNING + proceed; high VPP -> ERROR + early-return; FLAG_FORCE downgrades ERROR to WARNING"
  - "D-02 (regulator ownership): helper runs while caller's REGULATOR|P1_VPP_ENABLE is already asserted — NO regulator toggle inside helper"
  - "D-03 (REV0 guard): #ifdef HARDWARE_REVISION + rurp_get_hardware_revision()==REVISION_0 warns and returns without ADC read"
  - "D-09 (new test directory): test_flash_intel_vpp/ is a standalone suite — test_dispatch/host_stubs.cpp untouched (D-10)"
  - "ArduinoFake delay() must be stubbed in setUp() when tests drive operation_init — discovered during RED phase SIGABRT"

patterns-established:
  - "Per-suite host_stubs.cpp with TU-private mock state + extern-C setter functions for link-time override of rurp_* hardware symbols"
  - "configure_memory(&h); h.firestarter_operation_init(&h) dispatch path used in tests (not direct function call)"
  - "FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE baked into make_intel_handle() to isolate VPP check under test"

requirements-completed: [SAF-04, SAF-06]

# Metrics
duration: 45min
completed: 2026-05-12
---

# Phase 1 Plan 01-01: Intel Flash VPP Pre-Pulse Safety Check Summary

**Static `flash_intel_check_vpp` helper added to `flash_intel_write_init` — mirrors v1.0 `eprom_check_vpp` tolerance bands (warn low / error high / FORCE override / REV0 skip) with 5 Unity tests on `[env:native]` covering all branches**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-05-12
- **Completed:** 2026-05-12
- **Tasks:** 2 (Task 1: scaffold, Task 2: implement + test bodies)
- **Files modified:** 4 (flash_intel.cpp, test_flash_intel_vpp.cpp, host_stubs.cpp [new], pgmspace.h [new])

## Accomplishments

- Added `static void flash_intel_check_vpp(firestarter_handle_t* handle)` to `flash_intel.cpp` (lines 25–57 post-edit), inserted between existing forward declarations and `configure_flash_intel()`
- Wired the call-site in `flash_intel_write_init` after `delay(500)` and before the `chip_id > 0` branch, with the canonical `if (handle->response_code == RESPONSE_CODE_ERROR) { return; }` early-return guard — matching `eprom_generic_init:252` ordering
- Created `test_flash_intel_vpp/` Unity suite (3 files) with suite-local `host_stubs.cpp` providing mockable `rurp_read_voltage_mv` (via `set_mock_vpp_mv`) and `rurp_get_hardware_revision` (via `set_mock_hw_rev`)
- All 5 SAF-04 tests pass; all 15 pre-existing dispatch tests pass byte-identical; full native suite: 20/20 PASSED

## Static Helper Signature and Insertion Range

```c
// firestarter/src/proms/flash_intel.cpp (after forward declarations, before configure_flash_intel)
static void flash_intel_check_vpp(firestarter_handle_t* handle) {
    debug("Check VPP (Intel)");
#ifdef HARDWARE_REVISION
    if (rurp_get_hardware_revision() == REVISION_0) {
        firestarter_warning_response("Rev0 dont support reading VPP/VPE");
        return;
    }
#endif
    // Caller already asserted REGULATOR | P1_VPP_ENABLE and delayed 500ms
    uint16_t vpp_mv = rurp_read_voltage_mv();
    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {
        int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        firestarter_response_format(response_code, "VPP is high: %u.%uV > %u.%uV", ...);
    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {
        firestarter_warning_response_format("VPP is low: %u.%uV < %u.%uV", ...);
    }
    // NO regulator clear — caller continues to use REGULATOR | P1_VPP_ENABLE
}
```

## Test Directory Layout and Suite-Local Interfaces

```
firestarter/test/native/avr/test_flash_intel_vpp/
├── avr/pgmspace.h          — verbatim copy of test_dispatch's PROGMEM shim
├── host_stubs.cpp          — suite-local copy of dispatch's host_stubs with two additions:
│                             set_mock_vpp_mv(uint16_t) / rurp_read_voltage_mv() mockable
│                             set_mock_hw_rev(uint8_t) / rurp_get_hardware_revision() mockable
└── test_flash_intel_vpp.cpp — Unity suite, 5 test cases
```

**Suite-local setter interfaces** (extern "C", defined in `host_stubs.cpp`, declared in test TU):
- `void set_mock_vpp_mv(uint16_t mv)` — sets `s_mock_vpp_mv`; called in `setUp()` and per-test
- `void set_mock_hw_rev(uint8_t r)` — sets `s_mock_hw_rev`; default=1 (non-REV0), set to 0 for REV0 test

## Five Test Cases and Tolerance-Band Inputs

| Test Name | `vpp_mv` setpoint | Measured `s_mock_vpp_mv` | `ctrl_flags` | `s_mock_hw_rev` | Expected `response_code` |
|-----------|------------------:|-------------------------:|:------------:|:---------------:|:------------------------:|
| `test_flash_intel_vpp_nominal_proceeds` | 12000 | 12000 | 0 | 1 | NOT ERROR (OK) |
| `test_flash_intel_low_vpp_warns` | 12000 | 11000 (<11400=95%) | 0 | 1 | WARNING |
| `test_flash_intel_high_vpp_errors` | 12000 | 12700 (>12500=+500) | 0 | 1 | ERROR |
| `test_flash_intel_high_vpp_with_force_warns` | 12000 | 12700 | FLAG_FORCE | 1 | WARNING |
| `test_flash_intel_rev0_skips_vpp_check` | 12000 | 65535 (extreme) | 0 | **0** | NOT ERROR (WARNING from REV0 guard) |

## Task Commits (inside `firestarter/` submodule)

1. **Task 1: Scaffold test directory** — `f4bed9c` (test)
   - Created `test_flash_intel_vpp/avr/pgmspace.h`, `host_stubs.cpp`, `test_flash_intel_vpp.cpp` (5 empty-body tests)
   - 5/5 PASSED (empty bodies), 15/15 dispatch PASSED

2. **Task 2: Implement helper + fill tests** — `13468b8` (feat)
   - Added `flash_intel_check_vpp` to `flash_intel.cpp`
   - Wired call-site in `flash_intel_write_init`
   - Filled 5 test bodies; added `delay()` ArduinoFake mock in `setUp()`
   - Added `core.*` to `.gitignore`
   - 5/5 PASSED, 15/15 dispatch PASSED

## Regression Evidence

| Suite | Before | After |
|-------|--------|-------|
| `pio test -e native -f "*test_dispatch*"` | 15/15 PASSED | 15/15 PASSED |
| `pio test -e native -f "*test_flash_intel_vpp*"` | (did not exist) | 5/5 PASSED |
| `pio test -e native` (total) | 15 tests | 20 tests, 20/20 PASSED |

## Files Created/Modified

- `firestarter/src/proms/flash_intel.cpp` — added `flash_intel_check_vpp` static helper (~33 lines) and 4-line call-site insertion in `flash_intel_write_init`
- `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` — new Unity suite file (5 tests, ~155 lines)
- `firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp` — new suite-local stubs with mockable VPP/hw-rev (~160 lines)
- `firestarter/test/native/avr/test_flash_intel_vpp/avr/pgmspace.h` — new PROGMEM shim (verbatim copy, 63 lines)
- `firestarter/.gitignore` — added `core.*` pattern

**Unchanged (byte-identical):**
- `firestarter/src/proms/eprom.cpp` — `eprom_check_vpp` untouched (D-04)
- `firestarter/test/native/avr/test_dispatch/` — all three files byte-identical (D-10, D-11)
- `firestarter/include/flash_intel.h` — no declaration added (static helper, D-04)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] ArduinoFake `delay()` mock required explicit setup in `setUp()`**
- **Found during:** Task 2 (RED phase — test bodies filled, SIGABRT on first run)
- **Issue:** `flash_intel_write_init` calls `delay(500)` via ArduinoFake. ArduinoFake's fakeit mock aborts when a virtual method is called without a `When(Method(...))` setup. The dispatch tests avoid this because they never call `operation_init`. Tests calling `operation_init` need explicit `delay()` setup.
- **Fix:** Added `When(Method(ArduinoFake(), delay)).AlwaysReturn();` to `setUp()`. Also changed the REV0 test value from `99999` (overflows `uint16_t`) to `65535` (UINT16_MAX). Added `core.*` to `.gitignore` to suppress crash dump files.
- **Files modified:** `test_flash_intel_vpp/test_flash_intel_vpp.cpp`, `firestarter/.gitignore`
- **Verification:** All 5 tests pass after fix
- **Committed in:** `13468b8` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 3 - Blocking)
**Impact on plan:** Required fix — the test framework cannot invoke `operation_init` without ArduinoFake mock setup. No scope creep. `delay()` setup is a necessary pattern for any future test that drives `operation_init` directly.

## Issues Encountered

- SIGABRT during RED phase from ArduinoFake's fakeit abort on unmocked `delay()` virtual. Resolved by adding `When(Method(ArduinoFake(), delay)).AlwaysReturn()` to `setUp()`. This is a known gotcha documented for future test authors: any suite that calls `operation_init` must set up `delay()` in `setUp()`.

## Cross-Reference

- **SAF-05 (AT28C chip-id half):** Lands separately in `01-02-SUMMARY.md` (next plan in this phase)
- **SAF-06 (VPP half):** Closed by this plan (5 Unity tests)
- **Phase 4 HW-05:** Hardware validation of the Intel-flash VPP path on a real RURP shield — deferred per CONTEXT.md; this firmware path must exist (done) before HW-05 can run

## Next Phase Readiness

- SAF-04 closed; flash_intel_write_init now checks VPP before any chip-id or erase/blank-check step for all 39 algorithm=0x10 Intel-flash chips
- Ready for 01-02 (AT28C chip-id check — SAF-05)
- The `When(Method(ArduinoFake(), delay)).AlwaysReturn()` pattern should be included in `01-02`'s `setUp()` if that suite also calls `operation_init`

---
*Phase: 01-safety-closure-intel-flash-vpp-28c-chip-id*
*Plan: 01-01*
*Completed: 2026-05-12*

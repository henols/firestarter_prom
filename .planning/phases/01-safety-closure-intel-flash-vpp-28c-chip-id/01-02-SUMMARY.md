---
phase: 01-safety-closure-intel-flash-vpp-28c-chip-id
plan: 01-02
subsystem: firmware
tags: [arduino, unity-test, platformio, safety, at28c-eeprom, chip-id, native-test]

# Dependency graph
requires:
  - phase: v1.0-milestone (eeprom_28c.cpp, eprom.cpp A9-12V analog, test_dispatch/ harness)
    provides: eeprom28c_write_init, eprom_get_chip_id analog, test_dispatch Unity harness
  - plan: 01-01 (test scaffold pattern: configure_memory() overwrites function pointers; re-assign after)

provides:
  - static eeprom28c_check_chip_id() helper in eeprom_28c.cpp (SAF-05 A9-12V chip-id check)
  - Call-site in eeprom28c_write_init BEFORE flash_execute_command(EEPROM_SDP_DISABLE), gated on chip_id > 0
  - test_eeprom28c_chip_id/ Unity suite (4 tests) on [env:native]

affects:
  - Phase 4 HW-05 (hardware validation deferred — AT28C A9-12V path must exist here first)
  - SAF-06 (chip-id half closed by this plan; VPP half in 01-01)
  - VERIF-05/VERIF-06 (Phase 3 retroactive verification — D-05 override is a milestone-level decision)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "configure_memory() overwrites handle function pointers before calling configure_eeprom28c(). Tests must re-assign mock function pointers AFTER configure_memory() and BEFORE operation_init()."
    - "delayMicroseconds() must be mocked in setUp() alongside delay() when operation_init calls eeprom28c_wait_for_write — same ArduinoFake abort-on-unmocked-virtual pattern as Plan 01-01"
    - "A9-12V chip-id address derivation: mfr_addr = handle->mem_size - 64 covers the full AT28C family in one expression (AT28C256=0x7FC0, AT28C64=0x1FC0)"

key-files:
  created:
    - firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp
    - firestarter/test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp
    - firestarter/test/native/avr/test_eeprom28c_chip_id/avr/pgmspace.h
  modified:
    - firestarter/src/proms/eeprom_28c.cpp

key-decisions:
  - "D-05 OVERRIDE (load-bearing): CONTEXT.md D-05 prescribed the AMD/SST software JEDEC sequence (AA→0x5555, 55→0x2AAA, 90→0x5555). RESEARCH.md datasheet evidence proved this is wrong for AT28C: the Atmel AT28C256 Rev. 0006H and Microchip AT28C64B DS20006432B datasheets define identification via A9 raised to 12V reading the upper 64 bytes. This plan implements RESEARCH.md Option A (A9-12V, mirroring eprom_get_chip_id). The AMD/SST JEDEC sequence would silently corrupt address 0x5555 on SDP-disabled parts."
  - "D-04 (inline-copy): eeprom28c_check_chip_id mirrors eprom_get_chip_id byte-for-byte for the A9-12V mechanism — eprom_get_chip_id left byte-identical (no shared extraction)"
  - "D-08 (ordering): chip-id check runs BEFORE flash_execute_command(EEPROM_SDP_DISABLE) — fail-fast on identity leaves the chip write-protected on mismatch"
  - "D-06 (gate): if (handle->chip_id > 0) — zero means skip entirely; no A9-12V toggling"
  - "D-07 (message literal): verbatim Chip ID %#04x dont match expected ID %#04x from flash_intel_check_chip_id"
  - "Test deviation: configure_memory() overwrites firestarter_get_data; tests re-assign mock pointer after configure_memory(). Zero-test assertion changed from s_mock_byte_idx==0 to ==1 (1 wait read, 0 chip-id reads proves gate)"

requirements-completed: [SAF-05, SAF-06]

# Metrics
duration: 14min
completed: 2026-05-12
---

# Phase 1 Plan 01-02: AT28C EEPROM A9-12V Chip-ID Safety Check Summary

**Static `eeprom28c_check_chip_id` helper added to `eeprom28c_write_init` BEFORE SDP-disable — A9-12V mechanism (mirroring `eprom_get_chip_id`) with address derived from `mem_size - 64` for family-wide coverage — 4 Unity tests on `[env:native]` covering matching / mismatching / zero-skip / FORCE**

## Performance

- **Duration:** ~14 min
- **Started:** 2026-05-12
- **Completed:** 2026-05-12
- **Tasks:** 2 (Task 1: scaffold, Task 2: implement + test bodies)
- **Files modified:** 4 (eeprom_28c.cpp, test_eeprom28c_chip_id.cpp, host_stubs.cpp [new], pgmspace.h [new])

## Accomplishments

- Added `static void eeprom28c_check_chip_id(firestarter_handle_t* handle)` to `eeprom_28c.cpp` (lines 55–69 post-edit), inserted after `configure_eeprom28c()` and before `eeprom28c_write_init()`
- Wired the call-site in `eeprom28c_write_init` at the very top of the function body, BEFORE `flash_execute_command(EEPROM_SDP_DISABLE)`, under `if (handle->chip_id > 0)` gate with canonical `if (handle->response_code == RESPONSE_CODE_ERROR) { return; }` early-return guard
- Created `test_eeprom28c_chip_id/` Unity suite (3 files) with suite-local `host_stubs.cpp` (byte-identical to dispatch suite's — no link-time VPP mock overrides needed for chip-id suite)
- All 4 SAF-05 tests pass; all 15 pre-existing dispatch tests pass byte-identical; full native suite: 24/24 PASSED

## D-05 Decision Override (load-bearing milestone record)

**Context:** CONTEXT.md D-05 prescribed the AMD/SST software JEDEC autoselect sequence:
```
Write 0xAA → 0x5555 (unlock 1)
Write 0x55 → 0x2AAA (unlock 2)
Write 0x90 → 0x5555 (enter chip-id mode)
Read manufacturer at 0x0000, device at 0x0001
Write 0xF0 → 0x5555 (exit chip-id mode)
```

**Override authority:** RESEARCH.md §"AT28C JEDEC sequence verification" citing:
- Atmel AT28C256 Rev. 0006H datasheet
- Microchip AT28C64B DS20006432B datasheet

Both datasheets define identification via **A9 raised to 12V**, reading the upper 64 bytes of the address space (0x7FC0..0x7FFF on AT28C256; 0x1FC0..0x1FFF on AT28C64). The AA/55/90 sequence is the AMD/SST convention and is NOT supported by AT28C hardware.

**Safety implication:** Implementing the JEDEC sequence on an AT28C would silently WRITE to address 0x5555 on an SDP-disabled part, corrupting chip data. This override prevents a silent data corruption bug.

**Implementation:** This plan implements Option A (A9-12V identification) from RESEARCH.md, mirroring `eprom_get_chip_id` (`eprom.cpp:186-197`) with address derivation from `mem_size`.

**For retroactive verification:** Phase 3 VERIF-05/VERIF-06 should audit this decision against the datasheets. The override is locked in `must_haves.truths` of `01-02-PLAN.md`.

## Static Helper Signature and Insertion Range

```c
// firestarter/src/proms/eeprom_28c.cpp (after configure_eeprom28c, before eeprom28c_write_init)
static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {
    debug("Check chip ID (28C)");
    handle->firestarter_set_control_register(handle, REGULATOR, 1);
    delay(50);
    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE, 1);
    delay(100);
    uint32_t mfr_addr = handle->mem_size - 64;  // 0x7FC0 (AT28C256) / 0x1FC0 (AT28C64)
    uint16_t chip_id = handle->firestarter_get_data(handle, mfr_addr) << 8;
    chip_id |= handle->firestarter_get_data(handle, mfr_addr + 1);
    handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE, 0);
    if (chip_id != handle->chip_id) {
        int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        firestarter_response_format(response_code, "Chip ID %#04x dont match expected ID %#04x", chip_id, handle->chip_id);
    }
}
```

**Address derivation:** `mfr_addr = handle->mem_size - 64`
- AT28C256 (32768 bytes): mfr_addr = 0x7FC0, device = 0x7FC1
- AT28C64 (8192 bytes): mfr_addr = 0x1FC0, device = 0x1FC1
- Covers entire AT28C family without per-chip conditionals

## Call-site in `eeprom28c_write_init`

```c
void eeprom28c_write_init(firestarter_handle_t* handle) {
    // Check chip identity via A9-12V (SAF-05) BEFORE SDP-disable (D-08)
    if (handle->chip_id > 0) {
        eeprom28c_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    flash_execute_command(EEPROM_SDP_DISABLE);  // <-- SDP-disable follows
    // ...
}
```

## Test Directory Layout and Suite-Local Interfaces

```
firestarter/test/native/avr/test_eeprom28c_chip_id/
├── avr/pgmspace.h          — verbatim copy of test_dispatch's PROGMEM shim (63 lines)
├── host_stubs.cpp          — byte-identical copy of test_dispatch/host_stubs.cpp
│                             (no rurp_* mock overrides needed — chip-id mocking via handle
│                             function pointer; no link-time tricks)
└── test_eeprom28c_chip_id.cpp — Unity suite, 4 test cases
```

**Mocking strategy (Option M2):** All chip-id read mocking via `handle->firestarter_get_data` function pointer. Suite-local `host_stubs.cpp` is byte-identical to dispatch suite's — no `set_mock_*` setters in stubs.

**TU-private mock infrastructure:**
```c
static uint8_t s_mock_bytes[16];  // scripted byte sequence
static int s_mock_byte_idx;       // advances on each read
static uint8_t mock_get_data_scripted(struct firestarter_handle*, uint32_t) {
    if (s_mock_byte_idx < 16) return s_mock_bytes[s_mock_byte_idx++];
    return 0xFF;
}
```

**Important:** `configure_memory()` overwrites `handle->firestarter_get_data` with `memory_get_data` before calling `configure_eeprom28c()`. Tests re-assign to `mock_get_data_scripted` after `configure_memory()` and before `operation_init()`.

## Four Test Cases and Scripted Byte Inputs

| Test Name | `s_mock_bytes` | `chip_id` | `ctrl_flags` | Expected |
|-----------|----------------|-----------|:------------:|:--------:|
| `test_eeprom28c_matching_chip_id_proceeds` | {0x1F, 0x08, 0x20} | 0x1F08 | 0 | NOT ERROR |
| `test_eeprom28c_mismatching_chip_id_errors` | {0xDE, 0xAD} | 0x1F08 | 0 | ERROR |
| `test_eeprom28c_zero_chip_id_skips_check` | {0x20} (wait byte) | 0 | 0 | s_mock_byte_idx==1 |
| `test_eeprom28c_mismatching_chip_id_with_force_warns` | {0xDE, 0xAD, 0x20} | 0x1F08 | FLAG_FORCE | WARNING |

Notes:
- `s_mock_bytes[2] = 0x20` in matching and FORCE tests satisfies `eeprom28c_wait_for_write(0x5555, 0x20)` on first poll
- `s_mock_bytes[0] = 0x20` in zero test satisfies the wait; `s_mock_byte_idx == 1` proves only the wait read 1 byte (chip-id helper consumed 0)

## Task Commits (inside `firestarter/` submodule)

1. **Task 1: Scaffold test directory** — `5c9d864` (test)
   - Created `test_eeprom28c_chip_id/avr/pgmspace.h` (verbatim copy)
   - Created `test_eeprom28c_chip_id/host_stubs.cpp` (byte-identical to dispatch suite's)
   - Created `test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp` (4 empty-body tests)
   - 4/4 PASSED (empty bodies), 15/15 dispatch PASSED

2. **Task 2 RED: Add failing test bodies** — `cc14787` (test)
   - Filled 4 test bodies with real assertions (before production code existed)
   - ERRORED (SIGABRT) — confirming RED gate

3. **Task 2 GREEN: Implement helper + fix test infrastructure** — `52dc2a2` (feat)
   - Added `eeprom28c_check_chip_id` to `eeprom_28c.cpp`
   - Wired call-site in `eeprom28c_write_init` BEFORE `flash_execute_command(EEPROM_SDP_DISABLE)`
   - Fixed test bodies: re-assign `mock_get_data_scripted` after `configure_memory()`, add wait-byte, mock `delayMicroseconds`
   - 4/4 PASSED, 15/15 dispatch PASSED, 24/24 total PASSED

## Regression Evidence

| Suite | Before | After |
|-------|--------|-------|
| `pio test -e native -f "*test_dispatch*"` | 15/15 PASSED | 15/15 PASSED |
| `pio test -e native -f "*test_eeprom28c_chip_id*"` | (did not exist) | 4/4 PASSED |
| `pio test -e native` (total) | 20 tests (from 01-01) | 24 tests, 24/24 PASSED |

## Files Created/Modified

- `firestarter/src/proms/eeprom_28c.cpp` — added `eeprom28c_check_chip_id` static helper (21 lines) and 8-line call-site insertion in `eeprom28c_write_init`
- `firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp` — new Unity suite file (4 tests, ~175 lines)
- `firestarter/test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp` — new suite-local stubs, byte-identical to dispatch suite's (~160 lines)
- `firestarter/test/native/avr/test_eeprom28c_chip_id/avr/pgmspace.h` — new PROGMEM shim (verbatim copy, 63 lines)

**Unchanged (byte-identical):**
- `firestarter/src/proms/eprom.cpp` — `eprom_get_chip_id` untouched (D-04)
- `firestarter/include/eeprom_28c.h` — no declaration added (static helper, D-04)
- `firestarter/test/native/avr/test_dispatch/` — all three files byte-identical (D-10, D-11)
- `firestarter/platformio.ini` — no changes (new test dir auto-discovered by PIO)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `configure_memory()` overwrites `handle->firestarter_get_data` before calling configure_eeprom28c()**
- **Found during:** Task 2 GREEN phase (tests failing with RESPONSE_CODE_ERROR even for matching chip-id)
- **Issue:** `configure_memory()` at line 62 sets `handle->firestarter_get_data = memory_get_data` unconditionally before calling `configure_eeprom28c()`. The plan's `make_28c_handle()` sets the mock pointer before `configure_memory()`, so it gets overwritten. After overwrite, chip-id reads call `memory_get_data` (stub returns 0), always producing chip_id=0x0000 regardless of mock bytes.
- **Fix:** Re-assign `h.firestarter_get_data = mock_get_data_scripted` after `configure_memory()` in each test body that needs it (matching, mismatching, zero, FORCE).
- **Files modified:** `test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp`
- **Verification:** 4/4 tests PASS after fix
- **Committed in:** `52dc2a2` (Task 2 feat commit)

**2. [Rule 3 - Blocking] `delayMicroseconds()` mock required in `setUp()`**
- **Found during:** Task 2 GREEN phase (SIGABRT on first run)
- **Issue:** `eeprom28c_wait_for_write` calls `delayMicroseconds(10)`. ArduinoFake aborts on unmocked virtuals. Same pattern as `delay()` discovered in Plan 01-01.
- **Fix:** Added `When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();` to `setUp()`.
- **Files modified:** `test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp`
- **Committed in:** `52dc2a2`

**3. [Rule 1 - Bug] Plan's `s_mock_byte_idx == 0` assertion for zero-test incompatible with `eeprom28c_wait_for_write`**
- **Found during:** Task 2 analysis phase
- **Issue:** Plan asserts `s_mock_byte_idx == 0` to prove the chip-id helper wasn't called. But `eeprom28c_wait_for_write` also calls `firestarter_get_data` (consuming mock bytes). With the plan's `== 0` assertion, any wait call makes the test fail.
- **Fix:** For the zero test, pre-load `s_mock_bytes[0] = 0x20` for the wait, then assert `s_mock_byte_idx == 1` (only the wait consumed 1 byte; chip-id helper would have consumed 2 first, making index 3 after wait). `== 1` proves the gate was effective: chip-id reads = 0.
- **Semantic equivalence:** The deviation from `== 0` to `== 1` preserves the test's intent (prove the gate fires) while being compatible with the actual call chain.
- **Files modified:** `test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp`
- **Committed in:** `52dc2a2`

---

**Total deviations:** 3 auto-fixed (Rules 1/3)
**Impact on plan:** All deviations necessary — none change scope or semantics. The test infrastructure discoveries (function-pointer overwrite by configure_memory, delayMicroseconds mock requirement) are now documented for future test authors.

## Known Stubs

None. `eeprom28c_check_chip_id` is fully implemented and tested. The check is forward-compat: today no algorithm=0x0D entry sets `chip_id_value` in the DB, but the firmware path is ready the moment one does.

## Cross-Reference

- **SAF-04 (Intel-flash VPP half):** Landed separately in `01-01-SUMMARY.md`
- **SAF-06:** Both halves now closed — VPP (5 tests from 01-01) + chip-id (4 tests from 01-02)
- **Phase 3 VERIF-05/06:** Must audit the D-05 override against datasheets as a milestone-level decision
- **Phase 4 HW-05:** Hardware validation of the AT28C A9-12V path on a real RURP shield — deferred; firmware path now exists

## Self-Check: PASSED

- `eeprom_28c.cpp` exists and contains `static void eeprom28c_check_chip_id`: FOUND
- `test_eeprom28c_chip_id.cpp` exists and contains `RUN_TEST(test_eeprom28c_matching_chip_id_proceeds)`: FOUND
- `host_stubs.cpp` byte-identical to dispatch suite: VERIFIED (diff returns 0)
- `avr/pgmspace.h` byte-identical to dispatch suite: VERIFIED (diff returns 0)
- Submodule commits: `5c9d864` (scaffold), `cc14787` (RED), `52dc2a2` (feat GREEN): FOUND in git log
- `pio test -e native` 24/24 PASSED: VERIFIED

---
*Phase: 01-safety-closure-intel-flash-vpp-28c-chip-id*
*Plan: 01-02*
*Completed: 2026-05-12*

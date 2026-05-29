---
phase: 44-bug-a-rca-modified-rev-0-upper-address-jitter
plan: "02"
subsystem: firmware
tags: [firmware, tdd, read-timing, rca, json-parser, unity-tests]
dependency_graph:
  requires: [44-01]
  provides: [read_settling_us-field, read_strobe_us-field, json-parser-read-timing-keys, memory-get-data-instrumented, test_read_timing-suite]
  affects: [firestarter/include/firestarter.h, firestarter/src/json_parser.c, firestarter/src/proms/memory.cpp, firestarter/platformio.ini]
tech_stack:
  added: []
  patterns: [pulse_delay-json-param-pattern, extract_long-macro, TDD-RED-GREEN-native-unity]
key_files:
  created:
    - firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp
    - firestarter/test/native/avr/test_read_timing/host_stubs.cpp
    - firestarter/test/native/avr/test_read_timing/avr/pgmspace.h
  modified:
    - firestarter/include/firestarter.h
    - firestarter/src/json_parser.c
    - firestarter/src/proms/memory.cpp
    - firestarter/platformio.ini
    - firestarter/test/native/avr/test_dispatch/avr/pgmspace.h
    - firestarter/test/native/avr/test_data_input/avr/pgmspace.h
    - firestarter/test/native/avr/test_messages/avr/pgmspace.h
decisions:
  - Cap applied at parse time (get_read_settling/get_read_strobe) so T4 test can assert handle value is bounded after json_parse
  - Secondary cap guard in memory_get_data() as defence-in-depth (1000us ceiling)
  - Added +<json_parser.c> to native build_src_filter to make json_parse available to test_read_timing
  - Added strncmp_P shim to all four pgmspace.h stubs (required by json_parser.c when compiled in native env)
  - Used jsmn_parse directly in test helper instead of json_init (json_init uses sizeof(tokens)/sizeof(tokens[0]) which is wrong for pointer params on 64-bit host)
  - Zero-ambiguity asymmetry: read_settling_us 0 = no delay (explicit test point); read_strobe_us 0 = firmware default 3us
metrics:
  duration: "~8 minutes"
  completed: "2026-05-29"
  tasks_completed: 2
  files_created: 3
  files_modified: 9
---

# Phase 44 Plan 02: Add Read-Timing Knobs to Firmware Read Path Summary

Two host-tunable read-timing knobs (`read_settling_us` address-settling delay before /CE assert, and `read_strobe_us` /CE read-strobe pulse width) added to the firmware via the established `pulse_delay` JSON param pattern. Native Unity test suite GREEN; Leonardo firmware builds at 86% flash.

## What Was Built

- `firestarter_handle_t` struct extended with `read_settling_us` and `read_strobe_us` (`uint32_t`, adjacent to `pulse_delay`)
- `json_parser.c`: PROGMEM keys `"read-settling-delay"` / `"read-strobe-us"`, registered in `key_parsers[]`, parsed by `get_read_settling()` / `get_read_strobe()`
- T-44-01 cap at `READ_TIMING_MAX_US = 1000UL` applied at parse time so the handle value is always bounded
- `memory_get_data()` instrumented: settling delay inserted BETWEEN `firestarter_set_address()` and `rurp_chip_enable()` (new pre-/CE window); strobe replaces hardcoded `delayMicroseconds(3)` after chip_enable with parameterised knob (0 = default 3us)
- `test_read_timing` native Unity suite: 4 tests — settling-parse, strobe-parse, default-zero, cap (T4) — all GREEN

## Cap Design

`READ_TIMING_MAX_US = 1000UL` (1ms). Applied twice:
1. **At parse time** (in `get_read_settling` / `get_read_strobe`): the `handle->read_settling_us` value in the struct is always ≤ 1000µs after parsing. This is what the T4 test checks.
2. **At consumption time** (in `memory_get_data()`): secondary guard before `delayMicroseconds()` call, defence-in-depth for any code path that bypasses the parser.

## Instrument Points in memory_get_data()

```
handle->firestarter_set_address(handle, address);
rurp_set_data_input();

// SETTLING: if (handle->read_settling_us) delayMicroseconds(capped settling)
// ← NEW window: 0 = no delay (explicit test point; D-04)

rurp_chip_enable();

// STROBE: delayMicroseconds(strobe ? strobe : 3)
// ← replaces hardcoded delayMicroseconds(3); 0 = firmware default 3us

uint8_t data = rurp_read_data_buffer();
rurp_chip_disable();
```

## Zero-Ambiguity Convention

| Field | Value 0 means |
|-------|--------------|
| `read_settling_us` | No settling delay (explicit zero — valid D-04 sweep point) |
| `read_strobe_us` | Use firmware default 3µs (preserves current behaviour when host omits the param) |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] json_init() unusable in native test (sizeof pointer issue)**
- **Found during:** Task 2 (GREEN phase)
- **Issue:** `json_init()` uses `sizeof(tokens)/sizeof(tokens[0])` internally where `tokens` is a pointer param — on 64-bit host this yields ~2 tokens instead of 64, causing `jsmn_parse` to return -1 (JSMN_ERROR_NOMEM)
- **Fix:** Test helper `parse_json()` calls `jsmn_parse()` directly with `NUMBER_JSNM_TOKENS` (64); also added `#include "jsmn.h"` to test file
- **Files modified:** `test/native/avr/test_read_timing/test_read_timing_params.cpp`
- **Commit:** 5a91f1b

**2. [Rule 3 - Blocking] strncmp_P missing from all pgmspace.h host stubs**
- **Found during:** Task 2 (after adding json_parser.c to native build_src_filter)
- **Issue:** `json_parser.c` uses `strncmp_P` in `jsoneq_()` (line 268). When json_parser.c was compiled for native, all four existing suites failed with "implicit declaration of function strncmp_P". The function was absent from all pgmspace.h stubs (test_dispatch, test_data_input, test_messages, test_read_timing).
- **Fix:** Added `#define strncmp_P(s1, s2, n) strncmp((s1), (s2), (n))` to all four pgmspace.h shims
- **Files modified:** All four `test/native/avr/*/avr/pgmspace.h` stubs
- **Commit:** 5a91f1b

**3. [Rule 2 - Missing critical] json_parser.c not in native build_src_filter**
- **Found during:** Task 1 / Task 2 (linker error when test called json_parse)
- **Issue:** `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp>` excluded `json_parser.c`. The test_read_timing suite calls `json_parse()` directly (not via proms/*.cpp), so the linker had undefined references to `json_init` and `json_parse`.
- **Fix:** Added `+<json_parser.c>` to native `build_src_filter` in platformio.ini
- **Files modified:** `firestarter/platformio.ini`
- **Commit:** 5a91f1b

## TDD Gate Compliance

RED gate: commit `b0a1261` — compile error on missing `read_settling_us`/`read_strobe_us` members (four tests, all FAILED due to compile error).

GREEN gate: commit `5a91f1b` — all 4 tests passed; full native suite 25/25 passed.

No REFACTOR commit needed (implementation was clean on first pass).

## Threat Coverage

T-44-01 (Tampering — unbounded delayMicroseconds): MITIGATED. Cap `READ_TIMING_MAX_US = 1000UL` applied at parse time and as secondary guard at consumption. Test 4 (test_read_settling_us_capped_at_max) validates the parse-time cap. An absurd JSON value (`read-settling-delay: 9999`) is clamped to 1000µs before storing in the handle.

T-44-02 (Tampering — malformed JSON non-numeric): ACCEPTED as per threat register. `extract_long`/`simple_strtoul` yields 0 on non-numeric input — existing behaviour, acceptable for dev-only tool.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries. The two new JSON fields extend the existing locally-trusted serial-protocol surface (operator bench hardware only).

## Known Stubs

None — both new fields are fully wired from JSON parse through to hardware `delayMicroseconds()` call in `memory_get_data()`. No placeholder values.

## Self-Check: PASSED

- `/workspaces/firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp` — FOUND
- `/workspaces/firestarter/test/native/avr/test_read_timing/host_stubs.cpp` — FOUND
- `/workspaces/firestarter/test/native/avr/test_read_timing/avr/pgmspace.h` — FOUND
- commit b0a1261 — FOUND (test(44-02): add failing read-timing knob native tests)
- commit 5a91f1b — FOUND (feat(44-02): add read-settling/read-strobe knobs to read path)

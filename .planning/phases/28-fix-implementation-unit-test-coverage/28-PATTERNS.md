# Phase 28: Fix Implementation + Unit Test Coverage — Pattern Map

**Mapped:** 2026-05-21
**Files analyzed:** 6 (3 new, 3 modified)
**Analogs found:** 6 / 6 (100%)

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` (NEW) | unit-test | request-response (Unity RUN_TEST) | `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` (primary), `test_messages/test_rurp_log_id.cpp` (secondary — uses ArduinoFake) | exact role + flow |
| `firestarter/test/native/avr/test_data_input/host_stubs.cpp` (NEW) | test-link-stub | linkage only | `firestarter/test/native/avr/test_messages/host_stubs.cpp` | exact (with documented opt-out per Q6/D.1) |
| `firestarter/test/native/avr/test_data_input/avr/pgmspace.h` (NEW) | host-shim header | macro/include translation | `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` | byte-for-byte twin |
| `firestarter/src/boards/leonardo_rurp_shield.cpp` (MOD — `rurp_set_data_input`) | board-driver fn | hardware-register write | `firestarter/src/boards/uno_rurp_shield.cpp:rurp_set_data_input` POST-`df5fb44` | exact (cross-board mirror) |
| `firestarter/src/boards/leonardo_rurp_shield.cpp` (MOD — `rurp_read_data_buffer`) | board-driver fn | hardware-register read | (no exact analog — original Uno reads only one port). Pattern source: ATmega32U4 datasheet §10.2.4 + research Q1 | partial — synthesized from datasheet + research |
| `firestarter/platformio.ini` (MOD — `test_filter` line) | build-config | declarative list | existing `test_filter` entries at lines 78-80 | exact |
| `.planning/v1.6-EVIDENCE.md` (MOD — append at line-110 anchor) | doc | append-only narrative | Phase 27 append pattern at the same file (sections above line 110) | exact |

---

## Pattern Assignments

### `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` (NEW)

**Primary analog:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`
**Secondary analog (for ArduinoFake-mocked Serial pattern):** `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp`

#### Excerpt 1 — Header banner + canonical includes (mirror lines 1-40 of `test_configure_memory.cpp`)

`test_configure_memory.cpp` lines 1-40 (verbatim shape to copy; substitute Phase-28 narrative for Phase-12 narrative):

```cpp
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 12 Wave 0 — dispatch unit tests for configure_memory().
 *
 * One test per protocol in KNOWN_PROTOCOLS (build_db.py:89). Each test
 * constructs a minimal firestarter_handle_t (protocol, mem_type, cmd,
 * response_code) and asserts `configure_memory()` does not raise
 * RESPONSE_CODE_ERROR ...
 * ...
 */

#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"

using namespace fakeit;
```

**Substitutions for Phase 28:**
- Phase-12 narrative → Phase-28 narrative (Wave A — RED unity scaffold for `rurp_set_data_input` pullup clearing per FIX-02).
- `#include "memory.h"` → replaced by **include-as-source pattern** per RESEARCH.md Q2 / Option D (see Excerpt 2 below).
- Keep `#include <Arduino.h>`, `#include <ArduinoFake.h>`, `#include <unity.h>` verbatim.
- `using namespace fakeit;` is NOT needed for the data-input test (no `When(...)` mocks of Serial in the assertions themselves), but it is harmless and keeps the include-pattern uniform with other suites. Optional.

#### Excerpt 2 — Top-of-file board-source include pattern (RESEARCH.md Q2 Option D, lines 122-134)

Insert this block AFTER the standard includes (Excerpt 1) and BEFORE any test functions:

```cpp
// --- Host-side AVR register shim. MUST be BEFORE leonardo_rurp_shield.cpp
// is included so the source sees these as plain uint8_t globals.
#include <stdint.h>
static uint8_t PORTD = 0, PORTC = 0, PORTE = 0;
static uint8_t DDRD  = 0, DDRC  = 0, DDRE  = 0;
static uint8_t PIND  = 0, PINC  = 0, PINE  = 0;
// PORTB/DDRB are referenced by rurp_board_setup + rurp_set_control_pin (never
// called by these tests, but the linker still resolves them).
static uint8_t PORTB = 0, DDRB = 0;

// --- Enable the Leonardo board guard, then pull the source into THIS TU
// so rurp_set_data_input / rurp_read_data_buffer are exposed to the tests.
#define ARDUINO_AVR_LEONARDO
#include "../../../src/boards/leonardo_rurp_shield.cpp"
```

**LANDMINE — path depth:** the test cpp lives at `test/native/avr/test_data_input/`, so the source is reached with **FOUR** `../` segments (`../../../../src/...`)? Re-count from RESEARCH.md Risk #6:

- `test/native/avr/test_data_input/test_rurp_set_data_input.cpp` → `../` = `test/native/avr/` → `../../` = `test/native/` → `../../../` = `test/` → `../../../../` = repo root → `../../../../src/boards/leonardo_rurp_shield.cpp`.

The relative path is `../../../../src/boards/leonardo_rurp_shield.cpp` (FOUR dot-dot segments). The RESEARCH.md Q2 sample showing THREE is a typo; Risk #6 corrects it. **Use four.**

#### Excerpt 3 — setUp/tearDown pattern (mirror `test_configure_memory.cpp` lines 42-55)

```cpp
void setUp(void) {
    ArduinoFakeReset();
    /* Reset all host-shim register globals to a known state before each test.
     * The "residual pullups" pre-state is set inside each test body. */
    PORTD = 0; PORTC = 0; PORTE = 0;
    DDRD  = 0; DDRC  = 0; DDRE  = 0;
    PIND  = 0; PINC  = 0; PINE  = 0;
}

void tearDown(void) {
}
```

**Substitutions for Phase 28:** drop the `When(OverloadedMethod(ArduinoFake(Serial), write, ...))` Serial mocks — the data-input test never invokes serial output. Replace with the register-reset block.

#### Excerpt 4 — Test body pattern for `test_rurp_set_data_input_clears_data_pullups_leonardo`

Source for assertions: CONTEXT.md D-02 §"Post-condition assertions" + RESEARCH.md Q4. Test body to paste:

```cpp
void test_rurp_set_data_input_clears_data_pullups_leonardo(void) {
    // Pre-state: simulate residual register state from prior
    // rurp_set_control_pins / rurp_write_data_buffer strobes — all data
    // bits set HIGH (the worst-case "every internal pullup engaged" case).
    PORTD = 0xFF; PORTC = 0xFF; PORTE = 0xFF;
    DDRD  = PORTD_DATA_MASK; DDRC = PORTC_DATA_MASK; DDRE = PORTE_DATA_MASK;

    rurp_set_data_input();

    // Post-conditions: data-bit pullups cleared on all three ports.
    TEST_ASSERT_EQUAL_HEX8(0x00, PORTD & PORTD_DATA_MASK);
    TEST_ASSERT_EQUAL_HEX8(0x00, PORTC & PORTC_DATA_MASK);
    TEST_ASSERT_EQUAL_HEX8(0x00, PORTE & PORTE_DATA_MASK);

    // DDRx data bits cleared (input). Regression guard against accidentally
    // breaking the existing DDRx-clear logic while adding the PORTx-clear.
    TEST_ASSERT_EQUAL_HEX8(0x00, DDRD & PORTD_DATA_MASK);
    TEST_ASSERT_EQUAL_HEX8(0x00, DDRC & PORTC_DATA_MASK);
    TEST_ASSERT_EQUAL_HEX8(0x00, DDRE & PORTE_DATA_MASK);

    // Control bits MUST NOT be touched (PORTD bit 6 = D12, PORTC bit 7 = D13).
    // Pre-state set them HIGH via 0xFF; the masked PORTx-clear must preserve.
    TEST_ASSERT_EQUAL_HEX8(PORTD_CONTROL_MASK, PORTD & PORTD_CONTROL_MASK);
    TEST_ASSERT_EQUAL_HEX8(PORTC_CONTROL_MASK, PORTC & PORTC_CONTROL_MASK);
}
```

**Why the control-bit assertions matter:** RESEARCH.md Risk #1 — the EVIDENCE.md sketch's `PORTD = 0x00` literal would zero the D12 control line. The test's post-condition assertions catch this regression at unit-test time. The executor MUST use the masked form (`PORTD &= ~PORTD_DATA_MASK`) and these assertions encode the contract.

#### Excerpt 5 — Test body pattern for `test_rurp_read_data_buffer_reassembles_data_bus` (RESEARCH.md Q3, lines 164-188 verbatim)

```cpp
void test_rurp_read_data_buffer_reassembles_data_bus(void) {
    // All-high data bus: PIND data bits + PINC bit 6 + PINE bit 6 all set
    // Should reassemble to 0xFF.
    PIND = PORTD_DATA_MASK;  // 0x9F: bits 0,1,2,3,4,7 set
    PINC = PORTC_DATA_MASK;  // 0x40: bit 6
    PINE = PORTE_DATA_MASK;  // 0x40: bit 6
    TEST_ASSERT_EQUAL_HEX8(0xFF, rurp_read_data_buffer());

    // All-low: returns 0x00
    PIND = 0; PINC = 0; PINE = 0;
    TEST_ASSERT_EQUAL_HEX8(0x00, rurp_read_data_buffer());

    // Single-bit walks: D0 only set → PD2 = 0x04 (bit 2 of PIND)
    PIND = _BV(2); PINC = 0; PINE = 0;
    TEST_ASSERT_EQUAL_HEX8(0x01, rurp_read_data_buffer());

    // D5 only → PC6 = 0x40 (bit 6 of PINC)
    PIND = 0; PINC = _BV(6); PINE = 0;
    TEST_ASSERT_EQUAL_HEX8(0x20, rurp_read_data_buffer());

    // D7 only → PE6 = 0x40 (bit 6 of PINE)
    PIND = 0; PINC = 0; PINE = _BV(6);
    TEST_ASSERT_EQUAL_HEX8(0x80, rurp_read_data_buffer());
}
```

#### Excerpt 6 — `main()` runner (mirror `test_configure_memory.cpp` lines 165-190)

```cpp
int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();

    RUN_TEST(test_rurp_set_data_input_clears_data_pullups_leonardo);
    RUN_TEST(test_rurp_read_data_buffer_reassembles_data_bus);

    return UNITY_END();
}
```

**What stays the same vs `test_configure_memory.cpp`:**
- File-banner shape (copyright + Phase narrative + behavioural contract paragraph).
- `setUp` / `tearDown` function signatures.
- `int main(int argc, char** argv) { (void)argc; (void)argv; UNITY_BEGIN(); ...; return UNITY_END(); }` scaffolding.
- One `RUN_TEST(...)` line per test.
- `TEST_ASSERT_EQUAL_HEX8` macro for register-state assertions (matches the "register state is hex-readable" convention noted in CONTEXT.md §Specific Ideas).
- `extern "C" { #include "..." }` brace pattern around any C headers pulled in.

**What changes:**
- `#include "memory.h"` → host-shim register globals + `#define ARDUINO_AVR_LEONARDO` + `#include "../../../../src/boards/leonardo_rurp_shield.cpp"` (the include-as-source pattern per RESEARCH.md Q2 Option D).
- Drop the `using namespace fakeit;` + ArduinoFake `When(...)` Serial mocks (not needed — these tests never trigger serial output).
- Drop the `make_handle()` helper (not needed — these tests operate on register globals, not `firestarter_handle_t`).
- Two `RUN_TEST` calls (vs `test_configure_memory.cpp`'s 15).

---

### `firestarter/test/native/avr/test_data_input/host_stubs.cpp` (NEW)

**Analog:** `firestarter/test/native/avr/test_messages/host_stubs.cpp` (closer match than `test_dispatch/host_stubs.cpp` because both this and `test_messages` need ArduinoFake's `Serial_::operator bool()` linkage via `<Arduino.h>` + `<ArduinoFake.h>` pull-in).

**CRITICAL DEVIATION from the analog:** per RESEARCH.md Q2 + Q6 + D.1, this suite does **NOT** include `../_shared/host_stubs_common.inc`. The shared inc defines `extern "C"` no-op versions of `rurp_set_data_input` / `rurp_read_data_buffer` / `rurp_set_data_output` / `rurp_write_data_buffer` / `rurp_set_control_pin` (lines 58-72 of the shared inc) — all of which would multiple-define against the REAL implementations pulled in by the test cpp's `#include "../../../../src/boards/leonardo_rurp_shield.cpp"`.

#### Excerpt 1 — `test_messages/host_stubs.cpp` lines 24-37 (reference shape)

```cpp
#include <stdint.h>
#include <stddef.h>
#include <string.h>

#include <Arduino.h>
#include <ArduinoFake.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

#include "../_shared/host_stubs_common.inc"
```

#### Excerpt 2 — Phase-28-specific `host_stubs.cpp` content (RESEARCH.md Q6 lines 314-341)

The DELTA from the analog is: replace the `#include "../_shared/host_stubs_common.inc"` line with a minimal `Serial_::operator bool()` definition only. Paste verbatim:

```cpp
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 28 — host stub TU for the test_data_input suite.
 *
 * This suite uses the include-as-source pattern (the test cpp #includes
 * leonardo_rurp_shield.cpp directly per RESEARCH.md Q2 Option D) and defines
 * PORTx/DDRx/PINx as test-local globals. The shared host_stubs_common.inc
 * is INTENTIONALLY NOT INCLUDED because:
 *   1. test_data_input does not link src/proms/*.cpp (it doesn't need the
 *      dispatch surface).
 *   2. The included leonardo_rurp_shield.cpp provides real implementations
 *      of rurp_set_data_input, rurp_read_data_buffer, rurp_set_data_output,
 *      rurp_write_data_buffer, rurp_set_control_pin, rurp_board_setup, and
 *      rurp_user_button_pressed — which would multiple-define against the
 *      shared stubs.
 *
 * The only host_stubs.cpp content needed is Serial_::operator bool() (a
 * link-only stub referenced indirectly through ArduinoFake's USB-CDC
 * surface — used inside leonardo_rurp_shield.cpp's rurp_board_setup, which
 * the tests never call but the linker still resolves).
 */
#include <Arduino.h>
#include <ArduinoFake.h>

Serial_::operator bool() {
    return true;
}
```

**What stays the same vs `test_messages/host_stubs.cpp`:**
- Copyright + Phase-narrative file banner.
- `#include <Arduino.h>` + `#include <ArduinoFake.h>`.
- `Serial_::operator bool() { return true; }` link-only definition (also present at line 141-143 of `_shared/host_stubs_common.inc`).

**What changes:**
- Drop the `extern "C" { #include "rurp_shield.h" ... }` block (not needed — `rurp_shield.h` is pulled in transitively via the test cpp's source-include).
- Drop `#include "../_shared/host_stubs_common.inc"` (would cause multiple-definition errors per the explanation in the file's docstring).
- Drop `#include <stdint.h>` / `<stddef.h>` / `<string.h>` (not needed without the shared inc).

---

### `firestarter/test/native/avr/test_data_input/avr/pgmspace.h` (NEW)

**Analog:** `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` — **copy verbatim** (the file is a stable host-shim and `test_messages/avr/pgmspace.h` is functionally identical; choose `test_dispatch/` as the reference per RESEARCH.md §"Files Phase 28 will create").

#### Excerpt — full file contents (paste byte-for-byte)

```cpp
/*
 * Phase 12 Wave 0 — host-side stub for <avr/pgmspace.h>
 *
 * The dispatch test runs on platform = native (no AVR libc available).
 * `rurp_shield.h` unconditionally `#include <avr/pgmspace.h>` to get the
 * `PROGMEM` storage attribute and `pgm_read_*` accessors. On host we just
 * neutralize these to no-ops / direct memory access so the test binary
 * can link.
 *
 * Scope: ONLY for the dispatch unit test. Not for production builds.
 * Production builds use the real AVR libc header via the Arduino framework.
 */
#ifndef _AVR_PGMSPACE_H_STUB_
#define _AVR_PGMSPACE_H_STUB_

#include <stdint.h>
#include <string.h>

#ifndef PROGMEM
#define PROGMEM
#endif

#ifndef PSTR
#define PSTR(s) (s)
#endif

#ifndef PGM_P
#define PGM_P const char *
#endif

#ifndef pgm_read_byte
#define pgm_read_byte(addr) (*(const uint8_t*)(addr))
#endif

#ifndef pgm_read_word
#define pgm_read_word(addr) (*(const uint16_t*)(addr))
#endif

#ifndef pgm_read_dword
#define pgm_read_dword(addr) (*(const uint32_t*)(addr))
#endif

#ifndef pgm_read_ptr
#define pgm_read_ptr(addr) (*(void**)(addr))
#endif

#ifndef strcpy_P
#define strcpy_P(dst, src) strcpy((dst), (src))
#endif

#ifndef strlen_P
#define strlen_P(s) strlen((s))
#endif

#ifndef memcpy_P
#define memcpy_P(dst, src) memcpy((dst), (src), (n))
#endif

#endif /* _AVR_PGMSPACE_H_STUB_ */
```

**What stays the same:** EVERY line of `test_dispatch/avr/pgmspace.h`. Pure copy.

**What changes:** OPTIONALLY change the comment "the dispatch test" → "the data_input test" in the header docstring. Functionally inert. Both `test_dispatch/` and `test_messages/` have nearly-identical files with slightly different docstrings; either is acceptable.

**Why the include-path search resolves this file:** PlatformIO automatically adds the active test directory to the include path (per `[env:native].build_flags` lines 84-86: `-I test/native/avr/test_dispatch` and `-I test/native/avr/test_messages`). **Phase 28 must add `-I test/native/avr/test_data_input` to that list** so that `#include <avr/pgmspace.h>` (pulled transitively by `rurp_shield.h` → included in `leonardo_rurp_shield.cpp`) resolves to the local shim, not the system AVR header (which won't exist on the native host).

---

### `firestarter/src/boards/leonardo_rurp_shield.cpp` — Commit 1: `rurp_set_data_input`

**Analog:** `firestarter/src/boards/uno_rurp_shield.cpp:rurp_set_data_input` POST-`df5fb44` (the canonical reference fix).

#### Excerpt 1 — Uno PRE-fix shape (from `git show df5fb44 -- src/boards/uno_rurp_shield.cpp`, the "-" side)

```cpp
void rurp_set_data_input() {
    DDRD = 0x00;
}
```

#### Excerpt 2 — Uno POST-fix shape (current state, `uno_rurp_shield.cpp:128-137`)

```cpp
void rurp_set_data_input() {
    // Clear PORTD before switching to input so internal pullups are disabled
    // on every data line. Without this, residual PORTD bits from the last
    // register-strobe or rurp_set_communication_mode (PORTD bit 0 = 1) leave
    // 1..2 data pins weakly biased HIGH against the chip's drive. Defensive
    // — does not on its own fix the FM1608 byte-0 read failure on Uno (see
    // .planning/debug/fm1608-fresh-chip-baseline.md).
    PORTD = 0x00;
    DDRD = 0x00;
}
```

#### Excerpt 3 — Leonardo PRE-fix shape (current state, `leonardo_rurp_shield.cpp:137-141`)

```cpp
void rurp_set_data_input() {
    DDRD &= ~PORTD_DATA_MASK; // Set pins D0-D3 and D4-D7 as output
    DDRC &= ~PORTC_DATA_MASK; // Set pin D5 as output
    DDRE &= ~PORTE_DATA_MASK; // Set pin D6 as output
}
```

#### Excerpt 4 — Leonardo POST-fix target shape (RESEARCH.md Q4, lines 212-227)

```cpp
void rurp_set_data_input() {
    // Clear data-bit pullups on PORTD/PORTC/PORTE before switching DDR
    // to input. Without this, residual PORTx bits from prior
    // rurp_set_control_pins / rurp_write_data_buffer strobes leave 1-2
    // data pins weakly biased HIGH against the chip's drive. On a partially
    // erased EPROM (weak drive) this produces single-bit data corruption
    // (78% single-bit XOR flips per Phase 27 RCA on Leonardo W27C512).
    // Mirror of uno_rurp_shield.cpp:rurp_set_data_input (commit df5fb44).
    PORTD &= ~PORTD_DATA_MASK;
    PORTC &= ~PORTC_DATA_MASK;
    PORTE &= ~PORTE_DATA_MASK;
    DDRD &= ~PORTD_DATA_MASK; // Set pins D0-D3 and D4-D7 as output
    DDRC &= ~PORTC_DATA_MASK; // Set pin D5 as output
    DDRE &= ~PORTE_DATA_MASK; // Set pin D6 as output
}
```

**What stays the same as the Uno-side `df5fb44`:**
- Add PORTx-clear lines BEFORE the existing DDRx-clear lines.
- 7-line comment-block-then-1-line-per-PORT shape.
- Function body otherwise unchanged (no signature change, no return type change).

**What changes (Leonardo-specific):**
- **THREE PORTs to clear, not one** (Leonardo's data bus scatters across PORTD/PORTC/PORTE; Uno's is all on PORTD).
- **Masked-clear form `PORTx &= ~PORTx_DATA_MASK`, NOT total-clear `PORTx = 0x00`.** This is the load-bearing deviation flagged by RESEARCH.md Risk #1 — Uno can use `PORTD = 0x00` because PD0..PD7 are all data bits on the Uno; Leonardo MUST mask because PORTD bit 6 carries the D12 control line (`PORTD_CONTROL_MASK = 0x40`) and PORTC bit 7 carries D13 (`PORTC_CONTROL_MASK = 0x80`). A naive `PORTD = 0x00` would zero those active control bits and break the write path.
- Comment text references "partially erased EPROM" + "78% single-bit XOR flips" (Phase 27 RCA) rather than "FM1608 byte-0 read failure" (separate Uno-side debug).
- Commit-message body (per RESEARCH.md Q4 lines 234-263) documents the masked-vs-total-clear deviation explicitly.

---

### `firestarter/src/boards/leonardo_rurp_shield.cpp` — Commit 2: `rurp_read_data_buffer`

**Analog:** no exact source-code analog (the Uno's `rurp_read_data_buffer` is a one-liner `return PIND;`; it doesn't have the three-port race condition). Pattern source = ATmega32U4 datasheet §10.2.4 (per RESEARCH.md Q1) + the existing inline `_BV()` convention used at `leonardo_rurp_shield.cpp:99-104`.

#### Excerpt 1 — Leonardo PRE-fix (current state, `leonardo_rurp_shield.cpp:112-129`)

```cpp
uint8_t rurp_read_data_buffer() {
    // Read from ports and map back to data bus bits (D0-D7)
    uint8_t pind_val = PIND;
    uint8_t pinc_val = PINC;
    uint8_t pine_val = PINE;

    uint8_t data = 0;
    data |= ((pind_val & _BV(2)) >> 2); // PD2 -> D0
    data |= ((pind_val & _BV(3)) >> 2); // PD3 -> D1
    data |= ((pind_val & _BV(1)) << 1); // PD1 -> D2
    data |= ((pind_val & _BV(0)) << 3); // PD0 -> D3
    data |= (pind_val & _BV(4));        // PD4 -> D4
    data |= ((pinc_val & _BV(6)) >> 1); // PC6 -> D5
    data |= ((pind_val & _BV(7)) >> 1); // PD7 -> D6
    data |= ((pine_val & _BV(6)) << 1); // PE6 -> D7

    return data;
}
```

#### Excerpt 2 — Leonardo POST-fix target shape (RESEARCH.md Q1, lines 39-54)

```cpp
uint8_t rurp_read_data_buffer() {
    // Read from ports and map back to data bus bits (D0-D7).
    // Insert a single _NOP() between each PINx read to let the AVR's input
    // synchronizer latch settle before the next port read. The 32U4 PINx
    // register has a 0.5-1.5 clock-cycle latch latency (datasheet 7766J
    // §10.2.4); with a partially-erased EPROM (weak chip drive) plus the
    // address-bus driven through nearby PCB traces, three back-to-back PINx
    // reads can sample mid-transition values. One _NOP() @ 16 MHz = 62.5 ns;
    // worst-case W27C512 tACC at 5V is 90 ns. Two stalls put total settling
    // at ~125 ns - comfortably > tACC, < 1 µs / 64KB read overhead.
    uint8_t pind_val = PIND;
    _NOP();
    uint8_t pinc_val = PINC;
    _NOP();
    uint8_t pine_val = PINE;

    uint8_t data = 0;
    data |= ((pind_val & _BV(2)) >> 2); // PD2 -> D0
    data |= ((pind_val & _BV(3)) >> 2); // PD3 -> D1
    data |= ((pind_val & _BV(1)) << 1); // PD1 -> D2
    data |= ((pind_val & _BV(0)) << 3); // PD0 -> D3
    data |= (pind_val & _BV(4));        // PD4 -> D4
    data |= ((pinc_val & _BV(6)) >> 1); // PC6 -> D5
    data |= ((pind_val & _BV(7)) >> 1); // PD7 -> D6
    data |= ((pine_val & _BV(6)) << 1); // PE6 -> D7

    return data;
}
```

**What stays the same:**
- Function signature: `uint8_t rurp_read_data_buffer()`.
- All eight `data |= ...` bit-extract lines (lines 119-126 — the shift-and-mask reassembly is bit-identical pre and post fix; only the three PINx reads are touched).
- All three `uint8_t pinX_val = PINX;` reads (in original order — PIND, then PINC, then PINE).
- `return data;` line.

**What changes:**
- The brief existing 1-line comment "Read from ports and map back to data bus bits (D0-D7)" expands into the multi-line datasheet-citing comment paragraph.
- Insert `_NOP();` between the PIND read and PINC read.
- Insert a second `_NOP();` between the PINC read and PINE read.
- Net additions: 2 lines of code (the `_NOP();` calls) + 8 lines of comment expansion. Total +10 lines.
- Flash impact: +4 B (per RESEARCH.md Q1 cost analysis); runtime impact: ~125 ns per byte read = ~8 ms per 64KB read (invisible).

---

### `firestarter/platformio.ini` — `test_filter` line addition

**Analog:** the existing two-line allowlist at `platformio.ini:78-80`.

#### Excerpt — `platformio.ini` lines 76-86 (current state)

```ini
; Using positive test_filter allowlist (test_ignore was being honored
; inconsistently — likely PIO version quirk).
test_filter =
    native/avr/test_dispatch
    native/avr/test_messages
build_flags =
    ${env.build_flags}
    -std=gnu++17
    -I include
    -I test/native/avr/test_dispatch
    -I test/native/avr/test_messages
    -D RURP_BOARD_NAME=\"native\"
```

#### Excerpt — Phase 28 target shape

```ini
; Using positive test_filter allowlist (test_ignore was being honored
; inconsistently — likely PIO version quirk).
test_filter =
    native/avr/test_dispatch
    native/avr/test_messages
    native/avr/test_data_input
build_flags =
    ${env.build_flags}
    -std=gnu++17
    -I include
    -I test/native/avr/test_dispatch
    -I test/native/avr/test_messages
    -I test/native/avr/test_data_input
    -D RURP_BOARD_NAME=\"native\"
```

**What stays the same:**
- Every other line in `[env:native]`.
- `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp>` (line 101) — **do NOT extend** with `+<boards/leonardo_rurp_shield.cpp>` per RESEARCH.md Risk #3. The Leonardo source is pulled into the test_data_input TU via `#include`, not via `build_src_filter`.

**What changes:**
- Add the line `    native/avr/test_data_input` to the `test_filter` block (4-space indent matching existing entries — verify by reading the surrounding lines; tabs vs spaces must match).
- Add the line `    -I test/native/avr/test_data_input` to the `build_flags` block so the test cpp's `#include <avr/pgmspace.h>` (pulled transitively by `rurp_shield.h`) resolves to the local `test_data_input/avr/pgmspace.h` shim. **RESEARCH.md Q2 line 119 says "No other platformio.ini changes" — that statement is incomplete; the `-I` line is also required so the new suite's `avr/pgmspace.h` is found. Existing suites have the analogous `-I` line for the same reason.**

---

### `.planning/v1.6-EVIDENCE.md` — append `## Phase 28 — Fix Commit References`

**Analog:** the Phase 27 RCA append pattern already present in the same file (sections at lines 1-110). The append goes at the line-110 anchor:

```
<!-- Phase 28 appends commit refs here: ## Phase 28 — Fix Commit References. -->
```

#### Excerpt — surrounding anchor context (`.planning/v1.6-EVIDENCE.md:108-112`)

```
```

<!-- Phase 28 appends commit refs here: ## Phase 28 — Fix Commit References. -->
<!-- Phase 29 inverts here: ## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD). Same 9-column row schema; Verdict cells flip from FAIL to PASS, SHAs distinct cells go from N to 1. -->

## Verdict
```

#### Append-section skeleton (per D-08 + RESEARCH.md Q1/Q4)

The append goes **between** the line-110 `Phase 28` HTML comment and the line-111 `Phase 29` HTML comment. Do NOT modify either comment marker.

```markdown
## Phase 28 — Fix Commit References

**Landed:** 2026-05-21
**Branch:** `firestarter/v1.6-read-bug` (cut from `beta@bc0f5ac` at start of Wave A)

### Wave A — RED unity scaffold

- **Commit:** `<WAVE_A_SHA>` — `test(leonardo): RED unity scaffold for rurp_set_data_input pullup clearing (FIX-02)`
- **Test files:**
  - `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp`
  - `firestarter/test/native/avr/test_data_input/host_stubs.cpp`
  - `firestarter/test/native/avr/test_data_input/avr/pgmspace.h`
- **Test names:**
  - `test_rurp_set_data_input_clears_data_pullups_leonardo` — FAIL on parent (PORTx residual bits assert)
  - `test_rurp_read_data_buffer_reassembles_data_bus` — PASS on parent (regression guard, unchanged logic)
- **Verifier output:** `pio test -e native -f "*test_data_input*"` exit non-zero; assertion-failure marker `:FAIL:` on the pullup test.

### Wave B — Fix commits

#### Commit 1 — PORTx-clear

- **SHA:** `<COMMIT_1_SHA>` — `fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input`
- **RCA reference:** `.planning/v1.6-EVIDENCE.md` §"Phase 27 — RCA Findings" (2026-05-21)
- **Introducing commit:** `5b1f1cd` "Leonardo is working, fast as a shark" (2025-02-11) — shape introduction
- **Tag presence:** bug present at every firmware tag from `2.0.2` through `3.0.0b4`
- **Mirror reference:** `df5fb44` (2026-05-13) — Uno-side equivalent fix (PORTD pullup clear)
- **Deviation from EVIDENCE.md fix sketch:** uses masked form `PORTD &= ~PORTD_DATA_MASK` (not the sketch's `PORTD = 0x00`) to preserve PORTD bit 6 = D12 control line. See commit body for rationale.

#### Commit 2 — `_NOP()` settling delay

- **SHA:** `<COMMIT_2_SHA>` — `fix(leonardo): add _NOP settling delay between PIND/PINC/PINE reads in rurp_read_data_buffer`
- **RCA reference:** same `Phase 27 — RCA Findings` section
- **Datasheet citations:** ATmega16U4/32U4 (Atmel-7766J) §10.2.4 PINx synchronizer 0.5-1.5 clk latency; Winbond W27C512 tACC=90 ns at 5V
- **Defensive-in-depth note:** Commit 1 alone may be sufficient; Commit 2 adds belt-and-suspenders against the multi-instruction port-read race. Phase 29 bench A/B can confirm.

### Per-board `.hex` sizes (D-07)

Pre-fix baseline (beta@bc0f5ac, captured 2026-05-21):
- `firestarter_uno.hex`: 62,617 B
- `firestarter_leonardo.hex`: 68,876 B
- `firestarter_uno328pb.hex`: 62,854 B

Post-fix (after Commit 1 + Commit 2):

| Board     | Pre-fix `.hex` | Post-fix `.hex` | Δ      | Notes                              |
|-----------|----------------|-----------------|--------|------------------------------------|
| uno       | 62,617         | `<N>`           | `<0>`  | Untouched — no edits to uno_rurp_shield.cpp |
| leonardo  | 68,876         | `<N>`           | `<+~40>` | PORTx-clear + 2 × _NOP(); ±200 B threshold |
| uno328pb  | 62,854         | `<N>`           | `<0>`  | Untouched — shares uno_rurp_shield.cpp |

Threshold: ±200 B (ROADMAP SC#4). Leonardo Δ within budget.

### Read-path-only inspection (GATE-1.6 desk-side confirmation)

`git diff bc0f5ac..HEAD -- src/boards/leonardo_rurp_shield.cpp` shows changes ONLY to `rurp_set_data_input` (lines 137-145 area) and `rurp_read_data_buffer` (lines 112-129 area). No edits to `rurp_set_data_output`, `rurp_write_data_buffer`, `rurp_set_control_pin`, `rurp_board_setup`, or any VPP/regulator/pulse-interval code path. Three-axis-green carried over from Phase 27 GATE-1.6 risk assessment.

### Bench verification — Phase 29 (placeholder)

Bench-side N≥5 byte-identity verification of the fix (FIX-03) is gated to Phase 29 per ROADMAP SC#3. Phase 29's `dev consistency-check` invocation against W27C512 + Leonardo will replace this placeholder with verdict + SHAs.
```

**What stays the same vs the existing Phase 27 / Phase 26 sections in the same file:**
- Markdown heading hierarchy (`## Phase N — ...` at H2; sub-sections at H3/H4).
- Date stamp at top of section.
- Code-fenced commit message subjects.
- `:` prefix for "SHA:", "RCA reference:", etc. (the Phase 27 RCA Findings section uses the same bullet shape).

**What changes:**
- New section title.
- Section body is fix-specific (commits + sizes + GATE confirmation) rather than RCA-specific.

---

## Shared Patterns

### Native-test Unity scaffolding

**Source:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` lines 31-65, 165-190
**Apply to:** every new native test cpp

The canonical Unity test cpp shape in this codebase is:

```cpp
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

// extern "C" { #include "<production-header>.h" } for any C headers under test

void setUp(void) { /* per-test reset; ArduinoFakeReset(); + suite-local globals */ }
void tearDown(void) {}

// One test function per assertion case, named test_<what_it_asserts>.

int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();
    RUN_TEST(test_<name>);
    // ... more RUN_TEST lines ...
    return UNITY_END();
}
```

Phase 28's test cpp follows this template (Excerpts 1, 3, 6 above).

### Host-side AVR-register mocking

**Source:** RESEARCH.md Q6 (verified — ArduinoFake does NOT provide PORTx/DDRx/PINx)
**Apply to:** test_data_input ONLY (no other native suite touches register globals).

Pattern: declare `static uint8_t PORTD = 0, ...;` at file scope in the test cpp **before** any `#include` that references them. The included board source then sees them as plain lvalue uint8_t globals. AVR's `_BV(n) = (1 << n)` and `_NOP() = __asm__ volatile("nop")` are both provided by ArduinoFake's `<Arduino.h>` and work transparently on x86 host.

### Commit-message footer (D-06)

**Source:** CONTEXT.md D-06 lines 124-129
**Apply to:** both Wave B fix commits

Verbatim footer block to append to BOTH Commit 1 and Commit 2:

```
RCA: .planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Findings" (2026-05-21)
Introducing-commit: 5b1f1cd "Leonardo is working, fast as a shark" (2025-02-11) — shape introduction
Tag presence: bug present at every firmware tag from 2.0.2 through 3.0.0b4 (verified via tag-walk)
Test: firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

### Branch hygiene (D-03 + RESEARCH.md Q8)

**Source:** RESEARCH.md Q8 lines 465-491
**Apply to:** Wave A first task (sub-repo branch cut)

Sequence:
```bash
cd /workspaces/firestarter
git status --short                # must be empty
git fetch origin
git rev-parse beta origin/beta   # both must = bc0f5ac
git checkout beta && git pull --ff-only origin beta
git checkout -b v1.6-read-bug
git rev-parse HEAD               # must = bc0f5ac
```

Branch is LOCAL-only; push deferred to Phase 29 boundary per D-03.

---

## No Analog Found

No new file in Phase 28 lacks an analog. The closest "synthesized-not-copied" case is the `_NOP()` insertion pattern in `rurp_read_data_buffer` (Commit 2) — there's no exact code-level analog in the codebase, but the pattern is grounded in the ATmega32U4 datasheet (cited verbatim in RESEARCH.md Q1) and matches the existing inline `_BV()` / direct-register-access conventions at `leonardo_rurp_shield.cpp:99-104`.

---

## Metadata

**Analog search scope:**
- `/workspaces/firestarter/test/native/avr/` (full tree — 4 existing test directories + `_shared/`)
- `/workspaces/firestarter/src/boards/` (full tree — uno_rurp_shield.cpp, leonardo_rurp_shield.cpp, rurp_serial_utils.cpp)
- `/workspaces/firestarter/platformio.ini` (full file)
- `/workspaces/.planning/v1.6-EVIDENCE.md` (Phase 27 sections + line-110 anchor)
- `/workspaces/firestarter/CLAUDE.md` §"Native (Host) Test Environment"

**Files scanned:** 13 (full reads) + git history of `df5fb44`

**Pattern extraction date:** 2026-05-21

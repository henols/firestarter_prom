# Phase 64: Firmware Fail-Closed Dispatch + Native Tests - Pattern Map

**Mapped:** 2026-06-11
**Files analyzed:** 4 (2 new, 1 modified, 1 new test)
**Analogs found:** 4 / 4

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/src/proms/not_implemented.cpp` | handler/service | request-response | `firestarter/src/proms/sram.cpp` (handler structure) + `firestarter/src/proms/memory.cpp:117-118` (emit shape) | role-match (composite) |
| `firestarter/include/not_implemented.h` | header/config | — | `firestarter/include/eprom.h` | exact |
| `firestarter/src/proms/memory.cpp` (edit) | dispatch | request-response | `firestarter/src/proms/memory.cpp:73-118` (existing dispatch arms) | in-place extension |
| `firestarter/test/native/avr/test_dispatch/test_not_implemented.cpp` | test | request-response | `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` | exact |

---

## Pattern Assignments

### `firestarter/src/proms/not_implemented.cpp` (handler, request-response)

**Primary analog (handler body):** `firestarter/src/proms/sram.cpp:1-17`
**Emit shape analog:** `firestarter/src/proms/memory.cpp:117-118`

**Includes pattern** (from sram.cpp:1-17 — minimal configure_ handler):
```cpp
#include "not_implemented.h"
#include "firestarter.h"
#include "logging_id.h"
#include "messages.h"
```

**Handler signature + body pattern** (mirrors sram.cpp:15-17 for structure; memory.cpp:117-118 for emit):
```cpp
// From sram.cpp:15-17 — minimal configure_ handler shape:
void configure_sram(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_SRAM);
}

// From memory.cpp:117-118 — LOG_ERROR_ID_U8 + response_code = ERROR emit shape:
LOG_ERROR_ID_U8(MSG_ERR_MEM_TYPE_UNSUPPORTED, handle->mem_type);
handle->response_code = RESPONSE_CODE_ERROR;
```

**D-01 composite pattern** (the new handler merges both — self-contained, explicit NULL pointers):
```cpp
void configure_not_implemented(firestarter_handle_t* handle) {
    handle->firestarter_operation_init = NULL;
    handle->firestarter_operation_main = NULL;
    handle->firestarter_operation_end = NULL;
    LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, (uint8_t)handle->protocol);
    handle->response_code = RESPONSE_CODE_ERROR;
}
```
- `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` is at `firestarter/include/messages.h:96` (generated, Phase 63 — do NOT hand-edit).
- `LOG_ERROR_ID_U8` macro is at `firestarter/include/logging_id.h:106`.
- Cast `(uint8_t)handle->protocol` because `handle->protocol` is `uint32_t` (`firestarter.h:89`) but the wire param is `u8`/`hex_byte` (CONTEXT.md D-01 note).
- The explicit NULL re-assignment is belt-and-suspenders per D-01: `configure_memory()` already NULLs them at lines 47-49, but `configure_not_implemented()` must be independently testable.

---

### `firestarter/include/not_implemented.h` (header, config)

**Analog:** `firestarter/include/eprom.h:1-21` — exact template match

**Full pattern** (copy verbatim, substituting names):
```cpp
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __NOT_IMPLEMENTED_H__
#define __NOT_IMPLEMENTED_H__

#include "firestarter.h"
#ifdef __cplusplus
extern "C" {
#endif

    void configure_not_implemented(firestarter_handle_t* handle);

#ifdef __cplusplus
}
#endif
#endif // __NOT_IMPLEMENTED_H__
```

Key conventions from `eprom.h`:
- Include guard: `__<UPPER_FILENAME>_H__`
- Include `"firestarter.h"` (not angle brackets)
- `extern "C"` block wrapping the single `void configure_*(firestarter_handle_t*)` declaration
- Closing `#endif` comment uses `// __<UPPER_FILENAME>_H__`

---

### `firestarter/src/proms/memory.cpp` (edit — dispatch site)

**Analog:** `firestarter/src/proms/memory.cpp:73-118` — extend the existing protocol-if chain

**Current dispatch tail** (lines 93-118 — the insertion point is after line 102, before line 104):
```cpp
// memory.cpp:93-102 — last two existing protocol arms (steps 5 and 6):
    if (handle->protocol == 0x07 || handle->protocol == 0x08 || handle->protocol == 0x0B) {
        configure_eprom(handle);
        return;
    }

    if (handle->protocol == 0x0E || handle->protocol == 0x27 ||
        handle->protocol == 0x28 || handle->protocol == 0x29) {
        configure_sram(handle);
        return;
    }

// memory.cpp:104-118 — mem_type fallback (steps 7-11, becomes protocol==0 guarded):
    if (handle->mem_type == TYPE_EPROM) {
        configure_eprom(handle);
        return;
    } else if (handle->mem_type == TYPE_SRAM) {
        ...
    }
    LOG_ERROR_ID_U8(MSG_ERR_MEM_TYPE_UNSUPPORTED, handle->mem_type);
    handle->response_code = RESPONSE_CODE_ERROR;
```

**New arms pattern** (D-02 — named arms + generic guard + protocol==0 fence, slotted after line 102):
```cpp
    // Named infeasibility arms (D-02): FWH and GAL/PLD — infeasible on RURP.
    // Explicitly recognized per SC#4 / roadmap Phase 64 requirement.
    if (handle->protocol == 0x11 || handle->protocol == 0x2A ||
        handle->protocol == 0x2B || handle->protocol == 0x2C) {
        configure_not_implemented(handle);
        return;
    }

    // Generic fail-closed guard: any non-zero unrecognized protocol → not-implemented.
    // Must sit AFTER all implemented protocol cases and BEFORE the protocol==0 mem_type fallback.
    if (handle->protocol != 0) {
        configure_not_implemented(handle);
        return;
    }

    // Legacy mem_type fallback: reachable ONLY when protocol == 0.
    if (handle->mem_type == TYPE_EPROM) {
        ...
    }
```

**Add include** at top of `memory.cpp` include block (lines 8-24):
```cpp
#include "not_implemented.h"
```

**CLAUDE.md update required:** `firestarter/CLAUDE.md` § "Protocol Dispatch" dispatch order table must add step 6.5 (named arms) and step 6.6 (generic guard) and reword step 7 to note it is only reachable when `protocol == 0`.

---

### `firestarter/test/native/avr/test_dispatch/test_not_implemented.cpp` (test)

**Analog:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:1-190` — exact structural match

**File header + setUp pattern** (from test_configure_memory.cpp:1-55):
```cpp
/*
 * Phase 64 — dispatch unit tests for configure_not_implemented() and
 * fail-closed dispatch arms.
 *
 * Tests assert RESPONSE_CODE_ERROR and all-three-NULL op pointers (unlike
 * the sibling test_configure_memory.cpp which avoids pointer checks because
 * configure_sram() is a stub with NULL firestarter_operation_init).
 * The not-implemented handler is self-contained and always leaves all
 * three pointers NULL — pointer assertions are safe here.
 */
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"

using namespace fakeit;

void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t)))
        .AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
}

void tearDown(void) {}
```

**make_handle helper pattern** (from test_configure_memory.cpp:58-65 — copy verbatim):
```cpp
static firestarter_handle_t make_handle(uint32_t protocol, uint8_t mem_type, uint8_t cmd) {
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.mem_type = mem_type;
    h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}
```

**Negative / not-implemented test pattern** (assert BOTH response_code AND NULL pointers — this is the NEW assertion style, not used in the sibling file):
```cpp
// Pattern for all not-implemented tests (one per named arm + one generic):
void test_unknown_nonzero_protocol_0x99_not_implemented(void) {
    firestarter_handle_t h = make_handle(0x99, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
    TEST_ASSERT_NULL(h.firestarter_operation_init);
    TEST_ASSERT_NULL(h.firestarter_operation_main);
    TEST_ASSERT_NULL(h.firestarter_operation_end);
}
```

**Legacy fallback re-assertion test** (mirrors test_configure_memory.cpp:159-163 exactly — must be present per CONTEXT.md):
```cpp
void test_protocol_zero_with_mem_type_eprom_dispatches_eprom(void) {
    firestarter_handle_t h = make_handle(0, 1, CMD_READ); /* TYPE_EPROM = 1 */
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}
```

**main() / RUN_TEST pattern** (from test_configure_memory.cpp:165-190):
```cpp
int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();

    RUN_TEST(test_protocol_0x11_fwh_not_implemented);
    RUN_TEST(test_protocol_0x2A_gal_not_implemented);
    RUN_TEST(test_protocol_0x2B_gal_not_implemented);
    RUN_TEST(test_protocol_0x2C_pld_not_implemented);
    RUN_TEST(test_unknown_nonzero_protocol_0x99_not_implemented);
    /* Re-assertion: legacy fallback intact */
    RUN_TEST(test_protocol_zero_with_mem_type_eprom_dispatches_eprom);

    return UNITY_END();
}
```

**No platformio.ini change needed** — per CLAUDE.md § "Reuse pattern for future native tests": dropping `test_not_implemented.cpp` under `test/native/avr/test_dispatch/` is sufficient.

**host_stubs.cpp — no extension needed** — `configure_not_implemented()` calls `LOG_ERROR_ID_U8` and `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`, both already present in the stubs via `../shared/host_stubs_common.inc`. Confirm by checking that `host_stubs.cpp` (lines 26-36) passes through to `_shared/host_stubs_common.inc` with no suite-specific extensions.

---

## Shared Patterns

### LOG_ERROR_ID_U8 emit shape
**Source:** `firestarter/src/proms/memory.cpp:117-118`
**Apply to:** `not_implemented.cpp` handler body
```cpp
LOG_ERROR_ID_U8(MSG_ERR_MEM_TYPE_UNSUPPORTED, handle->mem_type);
handle->response_code = RESPONSE_CODE_ERROR;
```
New handler substitutes `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` and `(uint8_t)handle->protocol`.

### extern "C" header guard template
**Source:** `firestarter/include/eprom.h:1-21`
**Apply to:** `not_implemented.h`
Pattern: MIT license header → `#ifndef __X_H__` guard → `#include "firestarter.h"` → `extern "C"` block → single `void configure_*(firestarter_handle_t*)` → close guard.

### Protocol-arm dispatch style
**Source:** `firestarter/src/proms/memory.cpp:73-102`
**Apply to:** new arms in `memory.cpp`
```cpp
if (handle->protocol == 0xXX || handle->protocol == 0xYY) {
    configure_handler(handle);
    return;
}
```
Each arm: unconditional call then `return`. No `else`. Same indentation as existing arms.

### Unity test setUp Serial stub
**Source:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:42-55`
**Apply to:** `test_not_implemented.cpp`
Required because any `LOG_ERROR_ID_U8` call in the handler path attempts Serial output. The ArduinoFake stubs prevent linker-resolution failure and test abort.

---

## No Analog Found

None — all four files have strong analogs in the codebase.

---

## Metadata

**Analog search scope:** `firestarter/src/proms/`, `firestarter/include/`, `firestarter/test/native/avr/test_dispatch/`
**Files scanned:** 6 (memory.cpp, sram.cpp, eprom.h, memory.h, test_configure_memory.cpp, host_stubs.cpp)
**Pattern extraction date:** 2026-06-11

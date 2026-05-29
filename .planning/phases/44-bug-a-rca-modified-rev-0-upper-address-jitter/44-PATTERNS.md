# Phase 44: Bug A RCA — Modified Rev 0 Upper-Address Jitter - Pattern Map

**Mapped:** 2026-05-29
**Files analyzed:** 9 new/modified files
**Analogs found:** 9 / 9

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/include/firestarter.h` | model/config | — | self (existing `pulse_delay` field) | exact |
| `firestarter/src/json_parser.c` | parser | request-response | self (existing `get_delay` / `key_pulse_delay`) | exact |
| `firestarter/src/proms/memory.cpp` | service | request-response | self (existing `memory_set_data` / `delayMicroseconds(handle->pulse_delay)`) | exact |
| `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp` | test | request-response | `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` | exact (same framework + pattern) |
| `firestarter/test/native/avr/test_read_timing/host_stubs.cpp` | test-support | — | `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` | exact |
| `firestarter_app/firestarter/constants.py` | config | — | self (existing `FLAG_*`, `COMMAND_*` blocks) | exact |
| `firestarter_app/firestarter/eprom_operations.py` | service | request-response | self (existing `consistency_check_eprom` + `_setup_operation`) | exact |
| `firestarter_app/firestarter/cli_handlers.py` | controller | request-response | self (existing `dev_consistency_check` Click command) | exact |
| `.planning/phases/44-bug-a-rca-modified-rev-0-upper-address-jitter/sweep_bug_a.py` | utility | batch | `.planning/v1.6-EVIDENCE.md` byte-compare pattern | role-match |

---

## Pattern Assignments

### `firestarter/include/firestarter.h` (model/config — add two fields)

**Analog:** self — the existing `pulse_delay` field in `firestarter_handle_t`

**Existing field pattern** (`firestarter.h` lines 74–104):
```c
typedef struct firestarter_handle {
    uint8_t cmd;
    uint8_t operation_state;
    uint8_t response_code;
    uint8_t mem_type;
    uint32_t protocol;
    uint8_t pins;
    uint32_t mem_size;
    uint32_t address;
    uint16_t vpp_mv;
    uint32_t pulse_delay;    // ← template: numeric dev param, uint32_t
    uint32_t ctrl_flags;
    uint16_t chip_id;
    char data_buffer[DATA_BUFFER_SIZE];
    uint32_t data_size;
    bus_config_t bus_config;
    ...
} firestarter_handle_t;
```

**New fields to add** (immediately after `pulse_delay` line 84):
```c
uint32_t read_settling_us;   // address-settling delay before /CE assert (µs; 0 = use default 3µs)
uint32_t read_strobe_us;     // /CE read-strobe pulse width (µs; 0 = use default from current hardcoded path)
```

**Copy discipline:** Both fields are `uint32_t`, same as `pulse_delay`. Place them adjacent to `pulse_delay` (line 84) so the struct layout groups all timing fields together. No other struct members change.

---

### `firestarter/src/json_parser.c` (parser — add two PROGMEM keys + parsers)

**Analog:** self — the `key_pulse_delay` / `get_delay` precedent (lines 60, 72–73, 303–305)

**PROGMEM key declaration pattern** (lines 55–63):
```c
const char key_mem_size[] PROGMEM = "memory-size";
const char key_address[] PROGMEM = "address";
const char key_flags[] PROGMEM = "flags";
const char key_chip_id[] PROGMEM = "chip-id";
const char key_pin_count[] PROGMEM = "pin-count";
const char key_pulse_delay[] PROGMEM = "pulse-delay";   // ← template
const char key_vpp_mv[] PROGMEM = "vpp_mv";
const char key_type[] PROGMEM = "type";
const char key_algorithm[] PROGMEM = "algorithm";
```

**key_parsers[] registration pattern** (lines 70–74):
```c
static const key_parser_t key_parsers[] PROGMEM = {
    {key_mem_size, get_memory_size}, {key_address, get_address},       {key_flags, get_flags},
    {key_chip_id, get_chip_id},      {key_pin_count, get_pin_count},   {key_pulse_delay, get_delay},
    {key_vpp_mv, get_vpp_mv},        {key_type, get_type},             {key_algorithm, get_algorithm},
};
```

**Parser function pattern** (`extract_long` macro, lines 267–280; `get_delay` at lines 303–305):
```c
#define extract_long(element, register) \
    extract_num(element, register, simple_strtoul)

bool get_delay(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_long("pulse-delay", handle->pulse_delay);
}
```

**New declarations and parsers to add** (mirror the exact `get_delay` shape):
```c
// After existing PROGMEM key declarations:
const char key_read_settling[] PROGMEM = "read-settling-delay";
const char key_read_strobe[]   PROGMEM = "read-strobe-us";

// In key_parsers[] (append two entries matching existing style):
{key_read_settling, get_read_settling},
{key_read_strobe,   get_read_strobe},

// Parser functions (after get_delay):
bool get_read_settling(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_long("read-settling-delay", handle->read_settling_us);
}
bool get_read_strobe(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_long("read-strobe-us", handle->read_strobe_us);
}
```

**Forward-declaration pattern** (lines 13–25): Each parser function has a forward declaration at the top of the file — add `bool get_read_settling(...)` and `bool get_read_strobe(...)` to that block.

**Unknown-field behavior** (lines 127–129): Unknown JSON fields are silently skipped. The new keys become known only after registration in `key_parsers[]`. If the host sends `"read-settling-delay"` before the firmware upgrade, firmware silently ignores it — safe forward compatibility.

---

### `firestarter/src/proms/memory.cpp` (service — instrument read path)

**Analog:** self — `memory_set_data` (lines 202–212) uses `delayMicroseconds(handle->pulse_delay)` as the write-strobe knob; `memory_get_data` (lines 182–194) has the instrument point.

**Current `memory_get_data` read path** (lines 182–194 — the instrument point):
```c
uint8_t memory_get_data(firestarter_handle_t* handle, uint32_t address) {
    rurp_chip_output();
    address = mem_util_remap_address_bus(handle, address, READ_FLAG);

    handle->firestarter_set_address(handle, address);
    rurp_set_data_input();
    rurp_chip_enable();
    delayMicroseconds(3);          // currently: /CE strobe width (after enable, before read)
    uint8_t data = rurp_read_data_buffer();
    rurp_chip_disable();

    return data;
}
```

**CRITICAL pre-implementation detail:** The current `delayMicroseconds(3)` is AFTER `rurp_chip_enable()` — it is the read-strobe pulse width, NOT a pre-/CE address-settling delay. To instrument both knobs separately:

1. **Settling delay** = new delay inserted BETWEEN `firestarter_set_address()` and `rurp_chip_enable()` (currently zero — this is the gap to add).
2. **Strobe width** = replaces the existing hardcoded `delayMicroseconds(3)` with a parameterized call.

**Analog pattern from `memory_set_data`** (lines 202–212) showing how `pulse_delay` field is used:
```c
void memory_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    rurp_chip_input();
    address = mem_util_remap_address_bus(handle, address, WRITE_FLAG);

    handle->firestarter_set_address(handle, address);
    rurp_write_data_buffer(data);
    delayMicroseconds(3);                        // pre-enable settling (hardcoded)
    rurp_chip_enable();
    delayMicroseconds(handle->pulse_delay);      // ← parameterized strobe — exact template
    rurp_chip_disable();
}
```

**New `memory_get_data` implementation pattern** (copy from `memory_set_data`'s pulse_delay usage):
```c
uint8_t memory_get_data(firestarter_handle_t* handle, uint32_t address) {
    rurp_chip_output();
    address = mem_util_remap_address_bus(handle, address, READ_FLAG);

    handle->firestarter_set_address(handle, address);
    rurp_set_data_input();

    // Settling delay: time from address-set to /CE assertion.
    // 0 = use default (current firmware behavior: no delay here).
    // Knob: "read-settling-delay" JSON field -> handle->read_settling_us.
    if (handle->read_settling_us) {
        delayMicroseconds(handle->read_settling_us);
    }

    rurp_chip_enable();

    // Read-strobe pulse width: time /CE is asserted before data latch.
    // 0 = use default (3µs — current hardcoded behavior).
    // Knob: "read-strobe-us" JSON field -> handle->read_strobe_us.
    uint32_t strobe = handle->read_strobe_us ? handle->read_strobe_us : 3;
    delayMicroseconds(strobe);

    uint8_t data = rurp_read_data_buffer();
    rurp_chip_disable();

    return data;
}
```

**Zero-ambiguity convention** (Pitfall 3 from RESEARCH.md): For `read_settling_us`, 0 = "no settling delay" (a valid test point distinct from the default). For `read_strobe_us`, 0 = "use default 3µs" (preserving current firmware behavior when the host does not set the param). Document this asymmetry in a comment.

---

### `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp` (test — new Unity suite)

**Analog:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`

**Test file imports and setUp pattern** (lines 31–65):
```cpp
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

extern "C" {
#include "memory.h"          // or json_parser.h for parser-level tests
}
#include "firestarter.h"

using namespace fakeit;

void setUp(void) {
    ArduinoFakeReset();
    /* Stub Serial.write and Serial.flush so LOG_ERROR_ID_* calls don't abort. */
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t)))
        .AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
}

void tearDown(void) {}
```

**Handle factory pattern** (lines 57–65):
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

**Test assertion pattern** (lines 71–75):
```cpp
void test_protocol_0x06_dispatches_flash3(void) {
    firestarter_handle_t h = make_handle(0x06, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}
```

**New test cases to implement** (copy the above pattern, adapted for JSON parser testing):
```cpp
// Include json_parser.h + jsmn.h, call json_parse() with a JSON string containing
// "read-settling-delay" and "read-strobe-us", assert handle fields are set:

void test_read_settling_us_parsed_from_json(void) {
    // Build JSON: {"cmd":1,"read-settling-delay":50}
    // Call json_init() + json_parse()
    // Assert handle.read_settling_us == 50
    TEST_ASSERT_EQUAL_UINT32(50, handle.read_settling_us);
}

void test_read_strobe_us_parsed_from_json(void) {
    // Build JSON: {"cmd":1,"read-strobe-us":25}
    // Assert handle.read_strobe_us == 25
    TEST_ASSERT_EQUAL_UINT32(25, handle.read_strobe_us);
}

void test_read_timing_fields_default_zero_when_absent(void) {
    // Build JSON: {"cmd":1} (no timing fields)
    // Assert handle.read_settling_us == 0 AND handle.read_strobe_us == 0
    TEST_ASSERT_EQUAL_UINT32(0, handle.read_settling_us);
    TEST_ASSERT_EQUAL_UINT32(0, handle.read_strobe_us);
}

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();
    RUN_TEST(test_read_settling_us_parsed_from_json);
    RUN_TEST(test_read_strobe_us_parsed_from_json);
    RUN_TEST(test_read_timing_fields_default_zero_when_absent);
    return UNITY_END();
}
```

**platformio.ini update required:** Add `native/avr/test_read_timing` to `test_filter` (line 78–81) and add `-I test/native/avr/test_read_timing` to `build_flags` (line 86–89). The `build_src_filter = +<proms/>` is already correct — `json_parser.c` is under `src/` and linked via `test_build_src = yes`. However, `json_parser.c` is under `src/` not `src/proms/`, so the executor must verify `json_parser.c` compiles into the native test binary (check the existing test to confirm `json_parse()` is available in `test_dispatch`).

---

### `firestarter/test/native/avr/test_read_timing/host_stubs.cpp` (test-support)

**Analog:** `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` (lines 1–35)

**Exact copy pattern** (the dispatch suite's host_stubs.cpp is a pure pass-through):
```cpp
#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

#include "../_shared/host_stubs_common.inc"
```

The new `test_read_timing` suite tests JSON parsing at the `json_parse()` level — it links `src/proms/*.cpp` (same as `test_dispatch`) and needs the same `rurp_*` no-op stubs. The shared `host_stubs_common.inc` provides all of them. No suite-specific stub extensions are needed unless the test calls `memory_get_data()` directly (which would require stubbing `rurp_chip_enable`, `rurp_read_data_buffer`, etc. — all already present in the shared inc).

**pgmspace.h shim:** Copy from any existing suite. The file at `test/native/avr/test_dispatch/avr/pgmspace.h` defines PROGMEM/PSTR/PGM_P/pgm_read_* as host-memory equivalents. The new suite needs the same shim at `test/native/avr/test_read_timing/avr/pgmspace.h`.

---

### `firestarter_app/firestarter/constants.py` (config — add two JSON key constants)

**Analog:** self — existing sync-rule comment blocks (lines 25–57, 59–70)

**Existing sync-rule pattern** (lines 25–57):
```python
# Wire-protocol command codes — Firmware sync: firestarter.h
# cmd field values sent in JSON commands to the Arduino firmware.
COMMAND_READ = 1
COMMAND_WRITE = 2
...
```

**New constants to add** (mirror the sync-rule comment convention):
```python
# Dev sweep knobs — Firmware sync: json_parser.c (key_read_settling, key_read_strobe)
# JSON key name strings for host-tunable read-timing parameters.
# MUST stay in sync with the PROGMEM key strings in firmware json_parser.c.
JSON_KEY_READ_SETTLING_DELAY = "read-settling-delay"
JSON_KEY_READ_STROBE_US = "read-strobe-us"
```

**Placement:** After the `FLAG_*` block (lines 59–70) and before the `CTRL_*` block (lines 72–84), to group dev-tool protocol extensions together.

**Import update in `eprom_operations.py`:** The constants import block (lines 27–43) will need `JSON_KEY_READ_SETTLING_DELAY` and `JSON_KEY_READ_STROBE_US` added to the `from firestarter.constants import (...)` tuple.

---

### `firestarter_app/firestarter/eprom_operations.py` (service — extend `consistency_check_eprom`)

**Analog:** self — `consistency_check_eprom` (lines 497–507) and `_setup_operation` (lines 169–222)

**Current `consistency_check_eprom` signature** (lines 497–507):
```python
def consistency_check_eprom(
    self,
    eprom_name: str,
    eprom_data_dict: dict,
    runs: int = 3,
    output_dir: Optional[str] = None,
    keep_files: bool = True,
    max_diffs: int = 10,
    quiet: bool = False,
    operation_flags: int = 0,
) -> int:
```

**New signature** (add two optional params with defaults of 0):
```python
def consistency_check_eprom(
    self,
    eprom_name: str,
    eprom_data_dict: dict,
    runs: int = 3,
    output_dir: Optional[str] = None,
    keep_files: bool = True,
    max_diffs: int = 10,
    quiet: bool = False,
    operation_flags: int = 0,
    read_settling_us: int = 0,    # address-settling delay (µs; 0=firmware default)
    read_strobe_us: int = 0,      # /CE read-strobe pulse width (µs; 0=firmware default)
) -> int:
```

**JSON field emission pattern** from `_setup_operation` (lines 188–191):
```python
command_dict = eprom_data_dict.copy()   # Work with a copy
command_dict["cmd"] = cmd
command_dict["flags"] = eprom_data_dict.get("flags", 0) | operation_flags
```

**New field injection** (add after the `flags` line in `_setup_operation` or pass through a modified `eprom_data_dict`):
```python
# Emit timing knobs only when non-zero (firmware defaults apply when absent)
if read_settling_us:
    command_dict[JSON_KEY_READ_SETTLING_DELAY] = read_settling_us
if read_strobe_us:
    command_dict[JSON_KEY_READ_STROBE_US] = read_strobe_us
```

**Threading the params through `_operation_context`** (lines 225–236): `_operation_context` calls `_setup_operation`; the knob params need to flow from `consistency_check_eprom` → `_operation_context` → `_setup_operation`. The cleanest approach (matching the existing `operation_flags` thread-through) is to add `read_settling_us` and `read_strobe_us` params to both `_operation_context` and `_setup_operation`, consistent with how `operation_flags` is already threaded through.

**Alternative (simpler, less invasive):** Merge the knob values into the `eprom_data_dict` copy before passing it to `_operation_context`, since `_setup_operation` does `command_dict = eprom_data_dict.copy()`. This avoids touching `_operation_context`'s signature and is consistent with how `eprom_data_dict` already carries `pulse-delay` from the chip database.

---

### `firestarter_app/firestarter/cli_handlers.py` (controller — extend `dev consistency-check` Click command)

**Analog:** self — `dev_consistency_check` at lines 1030–1099

**Existing Click option pattern** (lines 1031–1067):
```python
@dev.command(name="consistency-check")
@click.argument("eprom", shell_complete=_complete_eprom)
@click.option("--runs", type=int, default=3, help="Number of consecutive reads (default 3; minimum 2).")
@click.option("--output-dir", "output_dir", type=str, default=None, help="Output dir for per-run binaries...")
@click.option("--keep-files/--no-keep-files", "keep_files", default=True, help="Keep per-run binary files...")
@click.option("--max-diffs", "max_diffs", type=int, default=10, help="Max divergent offsets...")
@click.option("-q", "--quiet", is_flag=True, help="Suppress per-run tqdm progress bars (D-11).")
@click.option("-f", "--force", is_flag=True, help="Force read, even if the chip id doesn't match...")
@click.pass_obj
@map_typed_errors
def dev_consistency_check(
    app: AppContext,
    eprom: str,
    runs: int,
    output_dir: Optional[str],
    keep_files: bool,
    max_diffs: int,
    quiet: bool,
    force: bool,
) -> None:
```

**New Click options to add** (copy the `--max-diffs` integer option pattern):
```python
@click.option(
    "--read-settling",
    "read_settling_us",
    type=int,
    default=0,
    help="Address-settling delay before /CE assert (µs; 0=firmware default 0µs).",
)
@click.option(
    "--read-strobe",
    "read_strobe_us",
    type=int,
    default=0,
    help="/CE read-strobe pulse width (µs; 0=firmware default 3µs).",
)
```

**Call-site update** (lines 1088–1098):
```python
verdict_int = app.eprom_operator.consistency_check_eprom(
    eprom,
    eprom_data,
    runs=runs,
    output_dir=output_dir,
    keep_files=keep_files,
    max_diffs=max_diffs,
    quiet=quiet,
    operation_flags=_build_op_flags(force=force),
    read_settling_us=read_settling_us,    # new
    read_strobe_us=read_strobe_us,        # new
)
```

---

### `.planning/phases/44-bug-a-rca-modified-rev-0-upper-address-jitter/sweep_bug_a.py` (utility — 2D sweep harness)

**Analog:** `.planning/v1.6-EVIDENCE.md` byte-compare 5-liner pattern (established in-project scripting style)

**Byte-compare pattern from EVIDENCE.md** (cited in RESEARCH.md Pattern 3):
```python
import glob, hashlib
ref_dir = ".planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-155021-v2/"
new_dir = "<new-baseline-dir>/"
for i in range(1, 6):
    ref = open(f"{ref_dir}run_{i:02d}.bin", "rb").read()
    new = open(f"{new_dir}run_{i:02d}.bin", "rb").read()
    diffs = sum(a != b for a, b in zip(ref, new))
    print(f"run_{i:02d}: {diffs}/65536 byte differences vs Phase 29 v2 ref")
```

**Sweep harness structure** (from RESEARCH.md Pattern 2, adapted):
```python
# sweep_bug_a.py — Phase 44 sweep harness
# Run from /workspaces (or firestarter_app/ with `firestarter` on PATH)
import subprocess, csv, sys

SETTLING_VALUES = [0, 3, 10, 25, 50, 100]   # µs
STROBE_VALUES   = [0, 3, 10, 25, 50]         # µs
RUNS = 5
CHIP = "W27C512"
PORT = "/dev/ttyACM1"  # operator confirms at session start

with open("sweep-grid.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["settling_us", "strobe_us", "exit_code", "stdout_tail"])
    for s in SETTLING_VALUES:
        for t in STROBE_VALUES:
            result = subprocess.run(
                ["firestarter", "-p", PORT, "dev", "consistency-check",
                 CHIP, "--runs", str(RUNS), "-q",
                 "--read-settling", str(s), "--read-strobe", str(t)],
                capture_output=True, text=True, timeout=120
            )
            tail = result.stdout.strip()[-200:]
            w.writerow([s, t, result.returncode, tail])
            print(f"settling={s}µs strobe={t}µs -> exit={result.returncode}")
```

**D-05 constraint:** The chip must remain seated for the full sweep. No `firestarter fw` or `pio run -t upload` calls occur in this script.

---

## Shared Patterns

### PROGMEM Key Registration (Firmware)

**Source:** `firestarter/src/json_parser.c` lines 55–74
**Apply to:** Any new JSON field added to the firmware protocol.

```c
// Step 1: Declare PROGMEM key string
const char key_foo[] PROGMEM = "foo-key-name";

// Step 2: Register in key_parsers[]
static const key_parser_t key_parsers[] PROGMEM = {
    ...
    {key_foo, get_foo},
};

// Step 3: Add parser function using extract_long macro
bool get_foo(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_long("foo-key-name", handle->foo_field);
}
```

The string literal in `extract_long()` MUST match the PROGMEM string exactly. The macro expands to `PSTR(element)` comparison via `jsoneq`. If they diverge, the parser silently skips the field.

### Constants Sync Rule (Cross-repo)

**Source:** `firestarter_app/firestarter/constants.py` lines 25–57; `firestarter/include/firestarter.h` lines 48–58
**Apply to:** Every new flag bit, command code, or JSON key name that crosses the serial protocol boundary.

Sync rule (from both CLAUDE.md files):
- Any new PROGMEM key in `json_parser.c` MUST have a matching `JSON_KEY_*` constant in `constants.py`.
- Any new flag bit in `firestarter.h` MUST have a matching `FLAG_*` constant in `constants.py`.
- Change both in the same commit.

### Unity Test Handle Factory (Firmware Native Tests)

**Source:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` lines 57–65
**Apply to:** All new native Unity test files.

```cpp
static firestarter_handle_t make_handle(uint32_t protocol, uint8_t mem_type, uint8_t cmd) {
    firestarter_handle_t h = {};   // zero-initialize ALL fields
    h.protocol = protocol;
    h.mem_type = mem_type;
    h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}
```

Zero-initialization (`= {}`) is critical — it ensures new fields like `read_settling_us` and `read_strobe_us` default to 0 without explicit initialization in every test.

### ArduinoFake Serial Stub (Firmware Native Tests setUp)

**Source:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` lines 42–52
**Apply to:** Any native Unity suite that exercises code paths that call `LOG_ERROR_ID_*` or other serial-output macros.

```cpp
void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t)))
        .AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
}
```

### Host Stubs Pass-Through (Firmware Native Tests)

**Source:** `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` lines 24–35
**Apply to:** Any new native test suite that does NOT use the include-as-source pattern (i.e., links against `src/proms/*.cpp` rather than including a board source directly).

```cpp
#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

#include "../_shared/host_stubs_common.inc"
```

### Click Integer Option Pattern (Host CLI)

**Source:** `firestarter_app/firestarter/cli_handlers.py` lines 1051–1056
**Apply to:** Any new dev command option that accepts a numeric parameter.

```python
@click.option(
    "--max-diffs",
    "max_diffs",
    type=int,
    default=10,
    help="Max divergent offsets to print on FAIL (default 10).",
)
```

---

## No Analog Found

All files in scope have direct analogs. No file requires a pattern invented from scratch.

---

## Metadata

**Analog search scope:** `firestarter/src/`, `firestarter/include/`, `firestarter/test/native/avr/`, `firestarter_app/firestarter/`, `firestarter_app/tests/`
**Files scanned:** 14 source files read directly; 4 test files read directly
**Pattern extraction date:** 2026-05-29

**Key anti-patterns to avoid** (per RESEARCH.md):
- Do NOT use `pulse_delay` as the settling knob — it controls write-strobe width, not read settling.
- Do NOT instrument only `rurp_read_data_buffer()` for the settling knob — the address-settle window is in `memory_get_data()` BEFORE `rurp_chip_enable()`.
- Do NOT treat `read_settling_us == 0` and `read_strobe_us == 0` with the same convention. The former is treated as "0µs = no settling" (explicit test point); the latter as "0 = use firmware default 3µs" (preserves existing behavior).
- Do NOT re-flash between sweep points — D-05 prohibits this; the knob is a runtime JSON parameter, not a build define.

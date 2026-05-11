---
phase: 12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0
type: patterns
date: 2026-05-11
---

# Phase 12 — Close BLOCKER-1: Algorithm-Based Dispatch — Pattern Map

**Mapped:** 2026-05-11
**Files analyzed:** 8 (5 modified, 3 created)
**Analogs found:** 8 / 8

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/src/proms/memory.cpp` (modify dispatch + remove const) | firmware dispatch / service | request-response | self — existing `0x10` / `0x0D` blocks in same function | exact (same function, same idiom) |
| `firestarter_app/firestarter/database.py` (`_map_data`) | data transform / service | transform | self — `PROTOCOL_MAP` module-top dict at lines 34-43 | exact (same file, same shape) |
| `firestarter_app/tools/build_db.py` (line 214 SRAM emit) | utility / data pipeline | batch / transform | self — existing ternary at `build_db.py:214` | exact (same line, conditional shape change) |
| `firestarter/CLAUDE.md` (dispatch table doc) | doc | — | self — existing "Dispatch order in `memory.cpp`" list and "Algorithm Handlers" table | exact (same doc, edit-in-place) |
| `firestarter_app/tools/check_dispatch.py` (NEW) | utility / regression script | batch | `firestarter_app/tools/build_db.py` (same dir, standalone script, reads DB) | role-match (sibling tool) |
| `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` (NEW) | test | request-response (per-call dispatch assertion) | `.pio/libdeps/native/ArduinoFake/examples/mock-injection/test/test_my_service.cpp` (no in-tree precedent — first test in this repo) | example-from-libdep |
| `firestarter/platformio.ini` (`[env:native]` section) | config | — | self — existing `[env:uno]` and `[env:leonardo]` sections in same file + `ArduinoFake/examples/mock-injection/platformio.ini` for the native shape | exact (same file) |
| `firestarter/src/proms/memory.cpp:25` (remove `TYPE_FLASH_TYPE_2 = 2`) | constant | — | self — neighboring lines 24/26/27/28 stay; just delete line 25 | exact (one-line deletion) |

---

## Pattern Assignments

### 1. `firestarter/src/proms/memory.cpp` — `configure_memory` dispatch extension (modify)

**Analog:** `firestarter/src/proms/memory.cpp` (same file, lines 73-81 — the existing 0x10 / 0x0D protocol-prefix blocks).

**Where to insert the new cases:** between line 81 (closing `}` of the 0x0D block) and line 83 (first `if (handle->mem_type == TYPE_EPROM)` of the mem_type fallback chain).

**The exact 2–3 line block shape to mirror** (`firestarter/src/proms/memory.cpp:73-81`):

```c
    if (handle->protocol == 0x10) {
        configure_flash_intel(handle);
        return;
    }

    if (handle->protocol == 0x0D) {
        configure_eeprom28c(handle);
        return;
    }
```

**Imports already present** (`firestarter/src/proms/memory.cpp:13-22` — every required handler header is already included; **no new `#include` lines needed**):

```c
#include "eprom.h"
#include "flash_type_3.h"
#include "flash_type_4.h"
#include "flash_intel.h"
#include "eeprom_28c.h"
#include "logging.h"
#include "memory_utils.h"
#include "operation_utils.h"
#include "rurp_shield.h"
#include "sram.h"
```

**Existing mem_type fallback chain to preserve** (`firestarter/src/proms/memory.cpp:83-96` — keep verbatim per D2 steps 7-10):

```c
    if (handle->mem_type == TYPE_EPROM) {
        configure_eprom(handle);
        return;
    } else if (handle->mem_type == TYPE_SRAM) {
        configure_sram(handle);
        return;
    } else if (handle->mem_type == TYPE_FLASH_TYPE_3) {
        configure_flash3(handle);
        return;
    } else if (handle->mem_type == TYPE_FLASH_TYPE_4) {
        configure_flash4(handle);
        return;
    }
    firestarter_error_response_format("Memory type 0x%02x not supported", handle->mem_type);
```

**Concrete planner diff (insert after `memory.cpp:81`, before `:83`):**

```c
    if (handle->protocol == 0x06) {
        configure_flash3(handle);
        return;
    }

    if (handle->protocol == 0x05 || handle->protocol == 0x35 || handle->protocol == 0x39) {
        configure_flash4(handle);
        return;
    }

    if (handle->protocol == 0x07 || handle->protocol == 0x08 || handle->protocol == 0x0B) {
        configure_eprom(handle);
        return;
    }

    if (handle->protocol == 0x0E || handle->protocol == 0x27 ||
        handle->protocol == 0x28 || handle->protocol == 0x29) {
        configure_sram(handle);
        return;
    }
```

---

### 2. `firestarter/src/proms/memory.cpp:25` — remove `TYPE_FLASH_TYPE_2` constant

**Analog:** N/A (one-line deletion). Confirm exact current line content before deleting.

**Existing constant block** (`firestarter/src/proms/memory.cpp:24-28`):

```c
#define TYPE_EPROM 1
#define TYPE_FLASH_TYPE_2 2
#define TYPE_FLASH_TYPE_3 3
#define TYPE_SRAM 4
#define TYPE_FLASH_TYPE_4 5
```

**Diff:** delete line 25 only (`#define TYPE_FLASH_TYPE_2 2`). Per acceptance criterion §6 and pitfall 3 in RESEARCH.md.

---

### 3. `firestarter_app/firestarter/database.py` — algorithm→mem_type table (modify `_map_data`)

**Analog 1 (module-top constants pattern):** `firestarter_app/firestarter/database.py:34-43` — the existing `PROTOCOL_MAP` dict is the exact shape to mirror for the new `_ALGO_MEM_TYPE` table.

```python
PROTOCOL_MAP = {
    0x05: "FLASH_AMD_STD",
    0x06: "FLASH_AMD_ALT",
    0x07: "EPROM_STD",
    0x08: "EPROM_QUICK",
    0x0B: "EPROM_LEGACY",
    0x0D: "EEPROM_POLL",
    0x10: "FLASH_INTEL",
    0x28: "SRAM_STD",
}
```

Place the new `_ALGO_MEM_TYPE` dict immediately below this (still above the class definition).

**Analog 2 (small constants block):** `firestarter_app/firestarter/database.py:45-48` — module-level `types` and `ROM_CE` / `ROM_OE` constants confirm the project's "constants at top, before class" convention.

```python
# Module-level constants
types = {"memory": 0x01, "flash": 0x03, "sram": 0x04}
ROM_CE = 0x100
ROM_OE = 0x101
```

**Analog 3 (the block being replaced):** `firestarter_app/firestarter/database.py:371-380` — the existing substring branch + the `protocol_id` read that must be moved up.

```python
        # Simplified type determination
        type_str = electrical.get("type", "")
        determined_type = 1  # Default to EPROM
        if "Flash" in type_str:
            determined_type = 2  # Generic Flash
        elif "SRAM" in type_str:
            determined_type = 4

        # Read algorithm integer directly — set by build_db.py as minipro protocol_id
        protocol_id = programming.get("algorithm", 0)
```

**`info_flags` block to leave untouched** (`firestarter_app/firestarter/database.py:382-387`) — per D3 explicit guidance:

```python
        # The new DB doesn't have the raw flags, so we infer what we can
        info_flags = 0
        if programming.get("chip_id_check"):
            info_flags |= 0x00000020  # Has Readable Chip ID
        if electrical.get("type") == "Flash/EEPROM":
            info_flags |= 0x00000010  # Can be electrically erased
```

**Concrete planner diff:**

1. Insert at module top (immediately after `PROTOCOL_MAP` at line 43, before `types =` at line 46):

   ```python
   # Algorithm (minipro protocol_id) → firmware mem_type integer.
   # Firmware dispatches on protocol first; mem_type is kept consistent for fallback paths.
   _ALGO_MEM_TYPE = {
       0x05: 5,   # FLASH_AMD_STD     → TYPE_FLASH_TYPE_4
       0x06: 3,   # FLASH_AMD_ALT     → TYPE_FLASH_TYPE_3
       0x07: 1,   # EPROM_STD         → TYPE_EPROM
       0x08: 1,   # EPROM_QUICK       → TYPE_EPROM
       0x0B: 1,   # EPROM_LEGACY      → TYPE_EPROM
       0x0D: 1,   # EEPROM_POLL       → TYPE_EPROM (firmware dispatches on protocol prefix)
       0x0E: 4,   # SRAM_32PIN        → TYPE_SRAM
       0x10: 1,   # FLASH_INTEL       → TYPE_EPROM (firmware dispatches on protocol prefix)
       0x27: 4,   # SRAM_24PIN        → TYPE_SRAM
       0x28: 4,   # SRAM_STD          → TYPE_SRAM
       0x29: 4,   # SRAM_512K_1M      → TYPE_SRAM
       0x35: 5,   # FLASH_EEPROM_LIKE → TYPE_FLASH_TYPE_4
       0x39: 5,   # FLASH_INTEL_ALT   → TYPE_FLASH_TYPE_4 (no DB chips; future-proofed)
   }
   ```

2. Replace `database.py:371-380` with (note: `protocol_id` read moves up):

   ```python
           # Read algorithm integer directly — set by build_db.py as minipro protocol_id
           protocol_id = programming.get("algorithm", 0)

           # Derive mem_type from algorithm (D3). Fall back to electrical.type substring
           # only when algorithm is absent / 0 (legacy user-override DB entries).
           if protocol_id and protocol_id in _ALGO_MEM_TYPE:
               determined_type = _ALGO_MEM_TYPE[protocol_id]
           else:
               type_str = electrical.get("type", "")
               determined_type = 1  # Default to EPROM
               if "Flash" in type_str:
                   determined_type = 2  # Generic Flash (legacy fallback only)
               elif "SRAM" in type_str:
                   determined_type = 4
   ```

---

### 4. `firestarter_app/tools/build_db.py` — SRAM electrical.type emission (modify line 214)

**Analog:** `firestarter_app/tools/build_db.py:211-231` — the existing chip_entry construction with the inline ternary on line 214 that the new conditional replaces.

```python
                chip_entry = {
                    "part_number": name.split("@")[0],
                    "electrical": {
                        "type": "Flash/EEPROM" if (flags & 0x10) else "UV-EPROM",
                        "size_bytes": mem_size,
                        "pin_count": pin_count,
                        "vpp": VPP_VOLTAGES.get(voltages & 0xFF, "Unknown"),
                        "vpp_mv": VPP_MV.get(voltages & 0xFF, 0),
                        "vdd": VCC_VOLTAGES.get((voltages >> 8) & 0x0F, "5V"),
                        "vcc": VCC_VOLTAGES.get((voltages >> 12) & 0x0F, "5V"),
                    },
```

**`proto_id` is already decoded earlier in the same loop** (`firestarter_app/tools/build_db.py:198`):

```python
                proto_id = int(ic.get("protocol_id"), 16)
```

So no new decode is required — just hoist the `electrical.type` computation out of the inline ternary into a local variable computed before `chip_entry`.

**Concrete planner diff:** insert before line 211 (`chip_entry = {`):

```python
                # SRAM protocols emit electrical.type = "SRAM" so the downstream
                # database._map_data() info_flags branch (`if electrical.type == "Flash/EEPROM"`)
                # does not set the "electrically-erasable" bit for SRAM, and so the
                # display layer no longer mislabels SRAM chips as "UV-EPROM".
                if proto_id in {0x0E, 0x27, 0x28, 0x29}:
                    _etype = "SRAM"
                elif flags & 0x10:
                    _etype = "Flash/EEPROM"
                else:
                    _etype = "UV-EPROM"
```

And change line 214 from:

```python
                        "type": "Flash/EEPROM" if (flags & 0x10) else "UV-EPROM",
```

to:

```python
                        "type": _etype,
```

---

### 5. `firestarter/CLAUDE.md` — dispatch table update (doc edit)

**Analog:** `firestarter/CLAUDE.md` itself — the existing "Dispatch order in `memory.cpp`" numbered list and the "Algorithm Handlers" table. The current table already documents the Phase 12 target shape for the existing protocols (0x10, 0x0D, 0x07/0x08/0x0B, 0x06, 0x05/0x35); the update is to bring it fully in line with what the code actually does after this phase.

**Current "Dispatch order in `memory.cpp`" list in `firestarter/CLAUDE.md`:**

```
1. `protocol == 0x10` → `configure_flash_intel()` — Intel 28F command-register flash
2. `protocol == 0x0D` → `configure_eeprom28c()` — AT28C-series 5V EEPROM with page write
3. `mem_type == TYPE_EPROM (1)` → `configure_eprom()` — UV-EPROM (0x07/0x08/0x0B)
4. `mem_type == TYPE_SRAM (4)` → `configure_sram()`
5. `mem_type == TYPE_FLASH_TYPE_3 (3)` → `configure_flash3()` — AMD unlock flash (0x06)
6. `mem_type == TYPE_FLASH_TYPE_4 (5)` → `configure_flash4()` — EEPROM-like flash (0x05, 0x35)
```

**Planner action:** replace steps 3–6 with the full Phase 12 dispatch order (D2 steps 3-11), interleaving protocol-prefix steps before the mem_type fallback. Also add a row for 0x0E/0x27/0x28/0x29 → `configure_sram` in the "Algorithm Handlers" table, and add 0x39 alongside 0x35.

---

### 6. `firestarter_app/tools/check_dispatch.py` — Python regression scan (CREATE)

**Analog:** `firestarter_app/tools/build_db.py` — same directory, same "standalone script" idiom, same DB-loading pattern.

**`if __name__ == "__main__":` entry-point shape** (`firestarter_app/tools/build_db.py:245-246`):

```python
if __name__ == "__main__":
    main()
```

**Top-of-file constants pattern** (`firestarter_app/tools/build_db.py:7-13`):

```python
# ==========================================
# 1. CONFIGURATION
# ==========================================
MINIPRO_XML_URL = "https://gitlab.com/DavidGriffith/minipro/-/raw/master/infoic.xml"
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "firestarter", "data")
OUTPUT_FILE = os.path.join(_DATA_DIR, "minipro_complete_db.json")
PINOUT_FILE = os.path.join(_DATA_DIR, "pinouts.json")
```

The new `check_dispatch.py` should reuse the same `_DATA_DIR` / DB file path idiom so it works from any cwd.

**`KNOWN_PROTOCOLS` set to import or duplicate** (`firestarter_app/tools/build_db.py:89`):

```python
KNOWN_PROTOCOLS = {0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39}
```

**Failure-exits-non-zero pattern** (`firestarter_app/tools/build_db.py:158-163`):

```python
    print(f"Fetching database from: {MINIPRO_XML_URL}")
    try:
        r = requests.get(MINIPRO_XML_URL)
        root = ET.fromstring(r.content)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
```

**Concrete planner outline for `check_dispatch.py`:**

```python
"""
Regression scan: assert every chip in minipro_complete_db.json reaches a real
firmware dispatch path after Phase 12.

Exits 0 on success, 1 on any chip that would hit "Memory type 0x%02x not supported".
"""
import json
import os
import sys

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "firestarter", "data")
DB_FILE = os.path.join(_DATA_DIR, "minipro_complete_db.json")

# Must mirror firestarter_app/firestarter/database.py::_ALGO_MEM_TYPE
_ALGO_MEM_TYPE = {
    0x05: 5, 0x06: 3, 0x07: 1, 0x08: 1, 0x0B: 1,
    0x0D: 1, 0x0E: 4, 0x10: 1, 0x27: 4, 0x28: 4,
    0x29: 4, 0x35: 5, 0x39: 5,
}

def dispatch(protocol, mem_type):
    # Mirrors firmware D2 order in firestarter/src/proms/memory.cpp::configure_memory
    if protocol == 0x10:                                  return "configure_flash_intel"
    if protocol == 0x0D:                                  return "configure_eeprom28c"
    if protocol == 0x06:                                  return "configure_flash3"
    if protocol in (0x05, 0x35, 0x39):                    return "configure_flash4"
    if protocol in (0x07, 0x08, 0x0B):                    return "configure_eprom"
    if protocol in (0x0E, 0x27, 0x28, 0x29):              return "configure_sram"
    return {1: "configure_eprom", 4: "configure_sram",
            3: "configure_flash3", 5: "configure_flash4"}.get(mem_type, "ERROR")

def main():
    with open(DB_FILE) as f:
        db = json.load(f)
    errors = []
    total = 0
    for mfg, chips in db.items():
        for chip in chips:
            total += 1
            proto = chip.get("programming", {}).get("algorithm", 0)
            mt = _ALGO_MEM_TYPE.get(proto)
            if dispatch(proto, mt) == "ERROR":
                errors.append(f"{mfg}/{chip.get('part_number')} proto=0x{proto:02X} mem_type={mt}")
    if errors:
        print(f"FAIL: {len(errors)} of {total} chips have no valid dispatch path:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    print(f"PASS: all {total} chips have a valid dispatch path")

if __name__ == "__main__":
    main()
```

---

### 7. `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — Unity dispatch unit test (CREATE)

**Analog (no in-tree precedent — first Unity/ArduinoFake test in this repo):** `.pio/libdeps/native/ArduinoFake/examples/mock-injection/test/test_my_service.cpp` — closest reachable template for an ArduinoFake+Unity test with `setUp`, `RUN_TEST`, and an `int main(argc, argv)` Unity runner.

**Test sketch shape to mirror** (`.pio/libdeps/native/ArduinoFake/examples/mock-injection/test/test_my_service.cpp:1-46`):

```cpp
#include <Arduino.h>
#include <unity.h>

using namespace fakeit;

#include "MyService.h"

void setUp(void)
{
    ArduinoFakeReset();
}

void test_connect(void)
{
    When(Method(ArduinoFake(Client), stop)).AlwaysReturn();
    // ... mock setup ...
    Client* clientMock = ArduinoFakeMock(Client);
    MyService service(clientMock);
    String response = service.request("myserver.com");
    TEST_ASSERT_EQUAL(3, response.length());
    TEST_ASSERT_TRUE(response.equals("200"));
    Verify(Method(ArduinoFake(Client), stop)).Once();
}

int main(int argc, char **argv)
{
    UNITY_BEGIN();
    RUN_TEST(test_connect);
    return UNITY_END();
}
```

**What the planner should write for Phase 12** (per RESEARCH.md "Firmware Unit Test Sketch"):

- One `test_protocol_NN_dispatches_<handler>(void)` per protocol case in D2 (one each for 0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39).
- Each test constructs a minimal `firestarter_handle_t` (protocol, mem_type, cmd, response_code), calls `configure_memory(&h)`, and asserts `TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code)`. Operation-pointer assertions are unreliable because some handlers (e.g. `configure_sram`) are stubs; the response_code check is the robust dispatch-success signal.
- `setUp()` resets ArduinoFake and zero-initializes the per-test handle.
- `main()` calls `UNITY_BEGIN()`, `RUN_TEST(...)` for each case, returns `UNITY_END()`.

**File path:** PlatformIO discovers files matching `test_*.cpp` under `test/native/avr/test_dispatch/` once `[env:native]` is added.

---

### 8. `firestarter/platformio.ini` — `[env:native]` test environment (modify)

**Analog 1 (same file, existing sections):** `firestarter/platformio.ini:24-40` — the existing `[env:uno]` and `[env:leonardo]` sections demonstrate the `${env.build_flags}` extension idiom that the new `[env:native]` should also use.

```ini
[env:uno]
platform = atmelavr
board = uno
framework = arduino
build_flags = 
	${env.build_flags}
	-D RURP_BOARD_NAME=\"${this.board}\"
	-D SERIAL_ON_IO

[env:leonardo]
platform = atmelavr
board = leonardo
framework = arduino
build_flags = 
	${env.build_flags}
	-D RURP_BOARD_NAME=\"${this.board}\"
	-D DATA_BUFFER_SIZE=1024
```

**Analog 2 (native env shape from ArduinoFake example):** `.pio/libdeps/native/ArduinoFake/examples/mock-injection/platformio.ini`:

```ini
[env:native]
platform = native
test_build_src = yes
build_flags = -std=gnu++17

lib_deps = file://../../
```

**Concrete planner diff:** append the following section to `firestarter/platformio.ini` after line 40:

```ini
[env:native]
platform = native
test_framework = unity
build_flags = 
	${env.build_flags}
	-std=gnu++17
lib_deps = 
	fabiobatsilva/ArduinoFake@^0.4.0
test_build_src = no
```

(The `test_build_src = no` keeps the firmware source unbuilt for the host so AVR-only files such as `rurp_shield.cpp` aren't pulled into the native compile; the dispatch test will `#include` only the headers/sources it needs directly. The planner can flip it to `yes` if the dispatch test ends up needing whole-program compilation.)

---

## Shared Patterns

### Pattern A — Module-top constant tables (Python)

**Source:** `firestarter_app/firestarter/database.py:34-43` (`PROTOCOL_MAP`) and `firestarter_app/tools/build_db.py:25-44` (the same dict in build_db).

**Apply to:** new `_ALGO_MEM_TYPE` dict in `database.py`; new constants block in `check_dispatch.py`.

```python
PROTOCOL_MAP = {
    0x05: "FLASH_AMD_STD",
    0x06: "FLASH_AMD_ALT",
    0x07: "EPROM_STD",
    0x08: "EPROM_QUICK",
    0x0B: "EPROM_LEGACY",
    0x0D: "EEPROM_POLL",
    0x10: "FLASH_INTEL",
    0x28: "SRAM_STD",
}
```

Use the same key=`0xNN`, value=domain-meaning shape, with one entry per line and an inline comment when the meaning isn't obvious.

### Pattern B — Protocol-prefix if-chain (C++)

**Source:** `firestarter/src/proms/memory.cpp:73-81`.

**Apply to:** every new protocol branch added to `configure_memory`. Do **not** convert the chain to a `switch` — match the existing `if (...) { call; return; }` idiom (per RESEARCH.md anti-pattern note).

```c
    if (handle->protocol == 0xNN) {
        configure_<handler>(handle);
        return;
    }
```

For multi-value cases, use `||` inside the `if` (one block per handler, not one block per protocol):

```c
    if (handle->protocol == 0x07 || handle->protocol == 0x08 || handle->protocol == 0x0B) {
        configure_eprom(handle);
        return;
    }
```

### Pattern C — Standalone tool scripts under `firestarter_app/tools/`

**Source:** `firestarter_app/tools/build_db.py:156-246` (whole `main()` + `if __name__ == "__main__":` block).

**Apply to:** `firestarter_app/tools/check_dispatch.py`.

```python
def main():
    # ... do work ...
    # on failure: sys.exit(1)
    # on success: print summary

if __name__ == "__main__":
    main()
```

Path constants at module top, computed relative to `__file__` so the script works from any cwd (mirrors `_DATA_DIR` and `OUTPUT_FILE` at `build_db.py:11-13`).

### Pattern D — PlatformIO env section inheriting `${env.build_flags}`

**Source:** `firestarter/platformio.ini:24-32` (`[env:uno]`).

**Apply to:** the new `[env:native]` section. Always extend rather than replace the shared `build_flags`.

```ini
[env:<name>]
platform = <platform>
build_flags = 
	${env.build_flags}
	<additional flags>
```

---

## No Analog Found

None — every file in Phase 12 has either an in-tree analog (same file/sibling file) or a libdep example (Unity/ArduinoFake). The `test_configure_memory.cpp` file has no in-tree precedent (the `test/native/avr/` directory is empty per RESEARCH.md), so the libdep example is the canonical template; the planner should call this out in the PLAN as "first Unity test in this repo" and follow the `test_my_service.cpp` shape closely.

---

## Metadata

**Analog search scope:**
- `/workspaces/firestarter_prom/firestarter/src/proms/` — firmware dispatch + handler files
- `/workspaces/firestarter_prom/firestarter/platformio.ini` — build environments
- `/workspaces/firestarter_prom/firestarter/test/` — confirmed empty (no in-tree Unity tests)
- `/workspaces/firestarter_prom/firestarter/.pio/libdeps/native/{Unity,ArduinoFake}/examples/` — libdep test templates
- `/workspaces/firestarter_prom/firestarter_app/firestarter/database.py` — `_map_data` + module constants
- `/workspaces/firestarter_prom/firestarter_app/firestarter/constants.py` — confirmed no `mem_type` table exists yet
- `/workspaces/firestarter_prom/firestarter_app/tools/` — only `build_db.py` exists as a standalone script

**Files scanned:** 8 (in-tree) + 2 (libdep examples) = 10

**Pattern extraction date:** 2026-05-11

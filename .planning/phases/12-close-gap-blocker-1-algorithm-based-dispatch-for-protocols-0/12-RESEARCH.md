# Phase 12: Close BLOCKER-1 — Algorithm-Based Dispatch for Missing Protocols — Research

**Researched:** 2026-05-11
**Domain:** Embedded C++ firmware dispatch table extension + Python database layer alignment
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**D1 — Fix at BOTH layers (C++ primary, Python secondary)**
The fix ships in both layers: firmware `memory.cpp:configure_memory` extends protocol-prefix dispatch to all `KNOWN_PROTOCOLS`; Python `_map_data` replaces substring logic with an algorithm-driven lookup table. C++ is architecturally primary; Python is defense-in-depth.

**D2 — C++ dispatch order (memory.cpp:configure_memory)**
```
1. protocol == 0x10           → configure_flash_intel(handle)      [existing]
2. protocol == 0x0D           → configure_eeprom28c(handle)         [existing]
3. protocol == 0x06           → configure_flash3(handle)            [new]
4. protocol ∈ {0x05, 0x35}    → configure_flash4(handle)            [new]
5. protocol ∈ {0x07,0x08,0x0B}→ configure_eprom(handle)             [new]
6. protocol ∈ {0x0E,0x27,0x28,0x29} → configure_sram(handle)        [new]
7. mem_type == TYPE_EPROM (1) → configure_eprom(handle)             [fallback, kept]
8. mem_type == TYPE_SRAM (4)  → configure_sram(handle)              [fallback, kept]
9. mem_type == TYPE_FLASH_TYPE_3 (3) → configure_flash3(handle)     [fallback, kept]
10. mem_type == TYPE_FLASH_TYPE_4 (5)→ configure_flash4(handle)     [fallback, kept]
11. error: "Memory type 0x%02x not supported"
```

**D3 — Python algorithm→mem_type mapping (database.py:_map_data)**
Replace substring branch (lines 371-377) with lookup table:

| algorithm | mem_type | firmware constant     |
|-----------|----------|------------------------|
| 0x05      | 5        | TYPE_FLASH_TYPE_4      |
| 0x06      | 3        | TYPE_FLASH_TYPE_3      |
| 0x07      | 1        | TYPE_EPROM             |
| 0x08      | 1        | TYPE_EPROM             |
| 0x0B      | 1        | TYPE_EPROM             |
| 0x0D      | 1        | TYPE_EPROM             |
| 0x0E      | 4        | TYPE_SRAM              |
| 0x10      | 1        | TYPE_EPROM             |
| 0x27      | 4        | TYPE_SRAM              |
| 0x28      | 4        | TYPE_SRAM              |
| 0x29      | 4        | TYPE_SRAM              |
| 0x35      | 5        | TYPE_FLASH_TYPE_4      |
| 0x39      | TBD — see research below |                |

Fallback when `algorithm == 0` or absent: retain legacy substring behavior.
The `info_flags` derivation at lines 384-387 is correct and independent — leave it alone.

**D4 — BLOCKER-2 (SRAM) is IN SCOPE**
`build_db.py` line 214 must emit `"SRAM"` for SRAM-protocol chips (proto_id ∈ {0x0E, 0x27, 0x28, 0x29}).

**D5 — WARNING-5 (AT28C256 algo=0x07) is OUT OF SCOPE**
Defer to a future per-chip override table phase.

**D6 — Protocol 0x35 (FLASH_EEPROM_LIKE) is IN SCOPE**
Include `0x35 → configure_flash4` in C++ dispatch and `0x35 → mem_type=5` in Python table even though zero 0x35 chips exist in the DB today.

**D7 — Verification approach (no hardware)**
JSON spot-checks, firmware build (pio run -e uno / -e leonardo), firmware unit test (pio test), regression scan over all 743 chips.

### Claude's Discretion
None specified.

### Deferred Ideas (OUT OF SCOPE)
- WARNING-5 / AT28C256 algorithm override (per-chip override table in build_db.py)
- WARNING-1 / Intel flash VPP ADC check
- WARNING-2 / EEPROM_POLL chip-ID validation
- WARNING-3 / Rename wire JSON key "vpp" → "vpp_mv"
- WARNING-4 / firestarter_test.sh test harness fix
- Dropping mem_type from wire protocol
- Sector-erase CLI exposure for 0x05 flash_type_4
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-FW-01 | Firmware dispatches on algorithm for UV-EPROM protocols (0x07, 0x08, 0x0B) | D2 steps 5 confirms protocol-prefix dispatch; configure_eprom already handles all three protocols internally via `handle->protocol` switch on pulse_delay |
| REQ-FW-04 | FLASH_AMD_ALT (0x06) sector erase reachable | D2 step 3 routes 0x06 → configure_flash3; flash3_sector_erase is already implemented and wired |
| REQ-SER-01 | algorithm field is the primary dispatch key | Phase 12 completes the migration for all 10 remaining protocols |
| REQ-SAF-01 | VPP check before write for every chip | SRAM chips (BLOCKER-2) will no longer route to configure_eprom, preventing spurious VPP regulator activation |
</phase_requirements>

---

## Summary

Phase 12 closes two production blockers by extending `configure_memory` in firmware to dispatch on `handle->protocol` for all 10 remaining protocols (currently only 0x10 and 0x0D have protocol-prefix dispatch), and aligning the Python `_map_data` to derive `mem_type` from `algorithm` instead of from an `electrical.type` substring. Together these changes make 277 currently-unreachable chips work (BLOCKER-1) and prevent 52 SRAM/NVRAM chips from receiving the UV-EPROM initialization sequence that activates the 12V VPP boost regulator (BLOCKER-2).

All six firmware handlers (`configure_eprom`, `configure_sram`, `configure_flash3`, `configure_flash4`, `configure_flash_intel`, `configure_eeprom28c`) are fully implemented and exported. The C++ change is entirely within `configure_memory` — no handler internals change. The Python change is a module-level constant table replacing 7 lines. The `build_db.py` change is one conditional on line 214.

Protocol 0x35 has zero chips in the current DB; 0x39 also has zero chips. Both are in `KNOWN_PROTOCOLS`, so both dispatch cases must be wired to prevent future regressions. 0x39 dispatch recommendation is documented in the code examples section below.

**Primary recommendation:** Implement D2 dispatch order in `configure_memory` using sequential `if` blocks (matching the Phase 05 pattern), then implement D3 table in `_map_data`, then update `build_db.py` for SRAM detection. These are three tightly coupled changes that should ship as a single commit set.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Protocol-to-handler routing | Firmware (memory.cpp) | — | Firmware is the execution layer; once bytes arrive on serial, only the firmware dispatches the programming sequence |
| Wire-level `type` field accuracy | Python host (database.py) | — | Python builds the JSON command; mem_type must match the firmware's fallback expectations |
| SRAM electrical.type labeling | Database pipeline (build_db.py) | — | Source of truth for electrical classification; downstream layers read this field |
| Regression validation | Python host (test suite) | Firmware (pio test) | Python iterates the full 743-chip DB; firmware unit test validates the dispatch wiring at the C level |

---

## Standard Stack

### Core

| Component | Version | Purpose | Notes |
|-----------|---------|---------|-------|
| `firestarter/src/proms/memory.cpp` | current | `configure_memory` dispatch | Primary change target |
| `firestarter_app/firestarter/database.py` | current | `_map_data` algorithm→mem_type | Secondary change target |
| `firestarter_app/tools/build_db.py` | current | SRAM electrical.type emission | Tertiary change |
| PlatformIO Core | 6.1.19 [VERIFIED: `pio --version`] | Firmware build + test runner | Already installed |
| Unity (test framework) | present in `.pio/libdeps/native/Unity/` [VERIFIED: filesystem] | C unit testing | Used for firmware dispatch test |
| ArduinoFake | present in `.pio/libdeps/native/ArduinoFake/` [VERIFIED: filesystem] | Mock Arduino.h for native test build | Required to compile firmware source on host |

### Python Test Infrastructure

pytest is NOT installed in the project venv and NOT on the system. [VERIFIED: `pytest --version` and venv pip list returned nothing]. The regression scan (D7 §4) must either:
1. Use a plain Python script that exits non-zero on failure (`python3 tools/check_dispatch.py`)
2. Or install pytest as a dev dependency (`pip install pytest`)

The plain-script approach requires no new dependencies and matches the project's existing test pattern (`firestarter_test.sh` is a shell script). Recommended path: add a `tools/check_dispatch.py` script.

---

## Architecture Patterns

### System Architecture Diagram

```
build_db.py                   database.py                 memory.cpp
 ┌──────────────────┐         ┌───────────────────┐       ┌──────────────────────────────┐
 │ electrical.type: │         │ _map_data():       │       │ configure_memory():          │
 │  "Flash/EEPROM"  │────────▶│  type_str lookup   │       │                              │
 │  "UV-EPROM"      │  line   │  → mem_type=2 ❌   │       │  protocol==0x10 → flash_intel│
 │  "SRAM" (new)    │  214    │                    │       │  protocol==0x0D → eeprom28c  │
 └──────────────────┘         │  D3 table lookup   │       │  [NEW] 0x06 → flash3        │
                               │  → correct mem_type│       │  [NEW] 0x05/0x35 → flash4  │
          JSON wire:           │  per algorithm ✓   │       │  [NEW] 0x07/08/0B → eprom  │
          {                    └────────┬───────────┘       │  [NEW] 0x0E/27/28/29→sram  │
           "type": mem_type,            │                   │  fallback: mem_type check  │
           "algorithm": proto_id        │                   │  → ERROR (unreachable now) │
          }                             │                   └──────────────────────────────┘
                                        │
                               convert_to_programmer()
                                        │
                               serial_comm.py → json_parser.c
                                        │
                               get_type() → handle->mem_type
                               get_algorithm() → handle->protocol
```

**Entry point:** `firestarter write -e <chip>` → `EpromDatabase.get_eprom()` → `_map_data()` → `convert_to_programmer()` → serial JSON → firmware → `configure_memory()` → handler.

### Recommended Project Structure

No new files required for the C++ change. Python:

```
firestarter_app/
├── firestarter/
│   └── database.py          # _map_data D3 table (module-level constant)
├── tools/
│   ├── build_db.py          # SRAM detection fix (line 214)
│   └── check_dispatch.py    # NEW: regression scan script
firestarter/
├── src/proms/
│   └── memory.cpp           # configure_memory new protocol-prefix cases
├── test/
│   └── native/
│       └── avr/
│           └── test_dispatch/
│               └── test_configure_memory.cpp  # NEW: Unity dispatch test
└── platformio.ini           # Add [env:native] test environment
```

### Pattern 1: Protocol-Prefix Dispatch (existing pattern to replicate)

The Phase 05 pattern for 0x10 is the exact model: [VERIFIED: `firestarter/src/proms/memory.cpp` lines 73-81]

```c
// Source: firestarter/src/proms/memory.cpp:73-81 (existing)
if (handle->protocol == 0x10) {
    configure_flash_intel(handle);
    return;
}

if (handle->protocol == 0x0D) {
    configure_eeprom28c(handle);
    return;
}
```

The new cases follow the same `if ... return` idiom — NOT a `switch` on protocol, because some cases cover multiple protocol values and the `if` chain is already established.

**Target shape for new cases (D2):**

```c
// Source: D2 locked decision in 12-CONTEXT.md
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

Note: 0x39 is included with the flash4 group — see "Protocol 0x39" section below.

### Pattern 2: Algorithm-Driven mem_type Table (Python)

**Current code (lines 371-377 of database.py — the full substring block to replace):**

```python
# Simplified type determination
type_str = electrical.get("type", "")
determined_type = 1  # Default to EPROM
if "Flash" in type_str:
    determined_type = 2  # Generic Flash
elif "SRAM" in type_str:
    determined_type = 4
```

**Replacement pattern (D3):**

```python
# Source: D3 locked decision in 12-CONTEXT.md
# Module-level constant (place near top of database.py, before class definition):
_ALGO_MEM_TYPE = {
    0x05: 5,   # FLASH_AMD_STD  → TYPE_FLASH_TYPE_4
    0x06: 3,   # FLASH_AMD_ALT  → TYPE_FLASH_TYPE_3
    0x07: 1,   # EPROM_STD      → TYPE_EPROM
    0x08: 1,   # EPROM_QUICK    → TYPE_EPROM
    0x0B: 1,   # EPROM_LEGACY   → TYPE_EPROM
    0x0D: 1,   # EEPROM_POLL    → TYPE_EPROM (firmware dispatches on protocol)
    0x0E: 4,   # SRAM_RW        → TYPE_SRAM
    0x10: 1,   # FLASH_INTEL    → TYPE_EPROM (firmware dispatches on protocol)
    0x27: 4,   # SRAM_STD       → TYPE_SRAM
    0x28: 4,   # SRAM_STD2      → TYPE_SRAM
    0x29: 4,   # SRAM_NVRAM     → TYPE_SRAM
    0x35: 5,   # FLASH_EEPROM   → TYPE_FLASH_TYPE_4
    0x39: 5,   # FLASH_EEPROM2  → TYPE_FLASH_TYPE_4 (no chips in DB; future-proofed)
}

# In _map_data, replace the substring block with:
protocol_id = programming.get("algorithm", 0)
if protocol_id and protocol_id in _ALGO_MEM_TYPE:
    determined_type = _ALGO_MEM_TYPE[protocol_id]
else:
    # Legacy fallback: substring on electrical.type (for user-override DB entries
    # that lack an algorithm field, or for protocol_id == 0)
    type_str = electrical.get("type", "")
    determined_type = 1  # Default to EPROM
    if "Flash" in type_str:
        determined_type = 2  # Generic Flash (legacy; no DB chips should hit this now)
    elif "SRAM" in type_str:
        determined_type = 4
```

**Important:** `protocol_id` is read at line 380 currently (AFTER the substring block). The replacement block must either move the `protocol_id` read to before the new table block, or inline it. The simplest approach is to read `protocol_id` first, then use it for table lookup before the substring fallback.

### Pattern 3: SRAM Detection in build_db.py

**Current code (line 214):**

```python
"type": "Flash/EEPROM" if (flags & 0x10) else "UV-EPROM",
```

**Replacement (D4 detection rule):**

```python
# Source: D4 locked decision in 12-CONTEXT.md
if proto_id in {0x0E, 0x27, 0x28, 0x29}:
    electrical_type = "SRAM"
elif flags & 0x10:
    electrical_type = "Flash/EEPROM"
else:
    electrical_type = "UV-EPROM"

# Then in chip_entry["electrical"]:
"type": electrical_type,
```

Note: `proto_id` is available at this point (decoded at line 198). This detection runs before the `chip_entry` dict is constructed.

### Anti-Patterns to Avoid

- **Switch on protocol in configure_memory:** The existing pattern uses `if ... return` chains, not a `switch`. Adding a `switch` on `handle->protocol` would be inconsistent and requires more boilerplate for multi-value cases. Match the existing style.
- **Removing the mem_type fallback:** Steps 7-10 in D2 must remain. They are unreachable for DB chips but preserve backward compatibility for hand-crafted JSON commands and older Python host versions.
- **Moving protocol_id read in _map_data:** The `protocol_id` read must occur BEFORE the new table lookup. The current code reads it at line 380 (after the replaced block). The replacement must read `protocol_id` first.
- **Touching info_flags logic:** Lines 382-387 (`info_flags |= 0x00000010` when `electrical.type == "Flash/EEPROM"`) are correct and independent. The SRAM tagging fix in `build_db.py` will change `electrical.type` for SRAM chips from `"UV-EPROM"` to `"SRAM"`, meaning the `info_flags` branch will correctly NOT set `0x00000010` for SRAM chips. No change needed in `_map_data`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Protocol→mem_type mapping | Substring logic, regex, or multi-layer inference | Explicit module-level dict `_ALGO_MEM_TYPE` | The exact mapping is locked in D3; a table is self-documenting and O(1) |
| Dispatch for each protocol | Per-chip special cases inside handlers | Protocol-prefix `if` blocks in `configure_memory` | All handler logic already exists; dispatch is pure routing |
| DB-level regression test | Ad-hoc manual spot-checking | `tools/check_dispatch.py` script that iterates all 743 chips | Mechanical, repeatable, caught by CI |

---

## Key Research Findings

### Protocol 0x39 — Target Handler

[VERIFIED: `python3` DB query] Zero chips in the current `minipro_complete_db.json` have `algorithm=0x39`. The protocol is present in `KNOWN_PROTOCOLS` at `build_db.py:89` and in the `firestarter_app/CLAUDE.md` known protocols list but the DB has no matching chips.

The minipro project uses 0x39 for flash chips with EEPROM-like page-write behavior (similar to 0x35, which is `FLASH_EEPROM_LIKE`). Both 0x35 and 0x39 map to `flash_type_4.cpp` in the CLAUDE.md table. **Recommendation: dispatch `0x39 → configure_flash4`**, co-located with the `0x05 || 0x35` case. Python table: `0x39 → mem_type=5 (TYPE_FLASH_TYPE_4)`. This is the conservative default (page-write flash behavior) and can be corrected in a future phase if chips with 0x39 are added to the DB.

Confidence: MEDIUM — inferred from KNOWN_PROTOCOLS membership + CLAUDE.md table + 0x35 analogy. [ASSUMED: 0x39 is flash_type_4 family; no chip entries exist to verify against]

### Chip Count Verification

[VERIFIED: DB query against `minipro_complete_db.json`]

| Protocol | Count in DB | electrical.type | Currently reaches handler? |
|----------|-------------|-----------------|--------------------------|
| 0x05 | 27 | Flash/EEPROM (all 27) | NO — mem_type=2, no dispatch |
| 0x06 | 190 | Flash/EEPROM (all 190) | NO — mem_type=2, no dispatch |
| 0x07 | 237 | Flash/EEPROM (30), UV-EPROM (207) | PARTIAL — 207 reach configure_eprom, 30 get mem_type=2 |
| 0x08 | 127 | Flash/EEPROM (21), UV-EPROM (106) | PARTIAL — 106 reach, 21 get mem_type=2 |
| 0x0B | 53 | Flash/EEPROM (9), UV-EPROM (44) | PARTIAL — 44 reach, 9 get mem_type=2 |
| 0x0D | 18 | Flash/EEPROM (15), UV-EPROM (3) | YES — protocol prefix dispatch |
| 0x0E | 20 | UV-EPROM (all 20) | WRONG — routed to configure_eprom |
| 0x10 | 39 | Flash/EEPROM (all 39) | YES — protocol prefix dispatch |
| 0x27 | 2 | UV-EPROM (all 2) | WRONG — routed to configure_eprom |
| 0x28 | 10 | UV-EPROM (all 10) | WRONG — routed to configure_eprom |
| 0x29 | 20 | UV-EPROM (all 20) | WRONG — routed to configure_eprom |
| 0x35 | 0 | — | N/A — no chips, dispatch still needed |
| 0x39 | 0 | — | N/A — no chips, dispatch still needed |

Total broken (get "Memory type 0x02 not supported"): **277 chips** (confirmed by query, vs. 247 cited in CONTEXT.md — the 247 figure counted only the chips contributing to BLOCKER-1 per the reach table but the integration check correctly states 277).

Total SRAM incorrectly routed to `configure_eprom` (BLOCKER-2): **52 chips** (0x0E: 20, 0x27: 2, 0x28: 10, 0x29: 20).

After Phase 12 fix: **0 chips error or route incorrectly** — verified by simulation against all 743 chips.

### All Handler Functions Are Fully Implemented

[VERIFIED: filesystem + source read]

| Handler | File | Status | Notes |
|---------|------|--------|-------|
| `configure_eprom` | `eprom.cpp` | Full — read/write/erase/chip-id | Dispatches on `handle->protocol` internally for pulse_delay |
| `configure_sram` | `sram.cpp` | Stub — just a `debug()` call | Only needs to NOT call configure_eprom; generic memory read/write remain wired from `configure_memory`. This is sufficient for BLOCKER-2. |
| `configure_flash3` | `flash_type_3.cpp` | Full — write/erase/sector-erase/chip-id | Target for 0x06 |
| `configure_flash4` | `flash_type_4.cpp` | Full — write/erase | Target for 0x05, 0x35, 0x39 |
| `configure_flash_intel` | `flash_intel.cpp` | Full — write/erase/chip-id | Already dispatched on 0x10 |
| `configure_eeprom28c` | `eeprom_28c.cpp` | Full — write/erase | Already dispatched on 0x0D |

All headers export the `configure_*` functions with `extern "C"` guards. `memory.cpp` already includes `sram.h`. No new includes are needed.

### Exact Dispatch Code Structure in memory.cpp

[VERIFIED: `firestarter/src/proms/memory.cpp` lines 45-97]

The current `configure_memory` function:
1. Lines 45-71: Sets function pointers for read/write/verify/data ops (generic, all memory types)
2. Line 71: `mem_util_set_address(handle, 0)` — initial address
3. Lines 73-76: `if (handle->protocol == 0x10)` → configure_flash_intel + return
4. Lines 78-81: `if (handle->protocol == 0x0D)` → configure_eeprom28c + return
5. Lines 83-95: mem_type if-else chain (TYPE_EPROM/SRAM/FLASH3/FLASH4)
6. Line 96: error fallback

The new protocol-prefix cases (D2 steps 3-6) must be inserted **between line 81 and line 83**, maintaining the protocol-first, mem_type-fallback pattern.

`TYPE_FLASH_TYPE_2 = 2` is defined at line 25 but never used in a dispatch case. After Phase 12, it remains dead — CONTEXT.md D6 calls for its removal in the same commit.

### The `_map_data` Substring Block — Exact Lines

[VERIFIED: `database.py` lines 371-380]

```python
371:         # Simplified type determination
372:         type_str = electrical.get("type", "")
373:         determined_type = 1  # Default to EPROM
374:         if "Flash" in type_str:
375:             determined_type = 2  # Generic Flash
376:         elif "SRAM" in type_str:
377:             determined_type = 4
378:
379:         # Read algorithm integer directly — set by build_db.py as minipro protocol_id
380:         protocol_id = programming.get("algorithm", 0)
```

Lines 371-377 are replaced. Line 380 (`protocol_id` read) must be moved to execute BEFORE the new table lookup. The planner's diff will be:

- Remove lines 371-377
- Move the `protocol_id = programming.get("algorithm", 0)` line to before the type determination block
- Add the `_ALGO_MEM_TYPE` constant at module top (above the class)
- Replace the removed block with the table lookup + substring fallback

### `build_db.py` SRAM Detection — Exact Line

[VERIFIED: `build_db.py` line 214]

```python
214:                         "type": "Flash/EEPROM" if (flags & 0x10) else "UV-EPROM",
```

`proto_id` is decoded at line 198. The SRAM detection must use `proto_id` (not flags), because SRAM chips in minipro XML may or may not have `flags & 0x10` set. The exact replacement is a ternary-to-if conversion:

```python
if proto_id in {0x0E, 0x27, 0x28, 0x29}:
    _etype = "SRAM"
elif flags & 0x10:
    _etype = "Flash/EEPROM"
else:
    _etype = "UV-EPROM"
# then: "type": _etype,
```

### Verified Chip Spot-Checks

[VERIFIED: DB query]

| Chip | Manufacturer | Algorithm | Current electrical.type | Current mem_type | Post-fix mem_type | Expected handler |
|------|-------------|-----------|------------------------|------------------|-------------------|-----------------|
| W27C512 | WINBOND | 0x07 | Flash/EEPROM | 2 (broken) | 1 | configure_eprom |
| AM27C040 | AMD | 0x08 | UV-EPROM | 1 (OK) | 1 | configure_eprom |
| AM2764A | AMD | 0x07 | UV-EPROM | 1 (OK) | 1 | configure_eprom |
| AM2716 | AMD | 0x0B | UV-EPROM | 1 (OK) | 1 | configure_eprom (legacy) |
| AM29F040 | AMD | 0x06 | Flash/EEPROM | 2 (broken) | 3 | configure_flash3 |
| SST39SF040 | SST | 0x06 | Flash/EEPROM | 2 (broken) | 3 | configure_flash3 |
| AE29F1008 | ASD | 0x05 | Flash/EEPROM | 2 (broken) | 5 | configure_flash4 |
| AM28F010 | AMD | 0x10 | Flash/EEPROM | 2 → dispatch on protocol | 1 | configure_flash_intel |
| AT28C256 | ATMEL | 0x07 | Flash/EEPROM | 2 (broken) | 1 | configure_eprom (WARNING-5; D5 deferred) |
| 6116 | Standard SRAM | 0x27 | UV-EPROM | 1 (HAZARD) | 4 | configure_sram |
| DS1245AB (RW) | DALLAS | 0x0E | UV-EPROM | 1 (HAZARD) | 4 | configure_sram |
| DS1230AB (TEST) | DALLAS | 0x28 | UV-EPROM | 1 (HAZARD) | 4 | configure_sram |

Note: DS1230AB exists as two separate entries: `DS1230AB(RW)` with algorithm=0x07 (UV-EPROM timing, reaches configure_eprom correctly) and `DS1230AB(TEST)` with algorithm=0x28 (SRAM protocol, currently hazardous, fixed by Phase 12).

### AVR Flash Budget

[VERIFIED: Intel HEX analysis of `.pio/build/uno/firestarter_uno.hex`]

- Current Uno flash usage: **24,402 bytes / 32,768 bytes (74.5%)**
- Remaining: **8,366 bytes**
- Estimated delta for ~10 new protocol-dispatch `if` blocks:
  - Each `if (protocol == NN) { call; return; }` on AVR: ~12-16 bytes
  - Multi-protocol cases (`||` conditions): ~20-24 bytes
  - Total for 4 new `if` blocks (D2 steps 3-6): ~60-100 bytes
- Flash remaining after: **~8,266-8,306 bytes (still ~25% free)**
- Leonardo has a larger 32KB flash plus no `SERIAL_ON_IO` overhead; no concern.

**There is no AVR flash budget risk.** No conditional compilation is required.

### Firmware Test Infrastructure

[VERIFIED: filesystem + `pio --version` 6.1.19]

- `test/native/avr/` directory exists but is **empty** — no existing test files
- Unity framework: present at `.pio/libdeps/native/Unity/`
- ArduinoFake: present at `.pio/libdeps/native/ArduinoFake/`
- `platformio.ini` has **no `[env:native]` test environment defined** — one must be added

To add a native test environment to `platformio.ini`:

```ini
[env:native]
platform = native
build_flags = ${env.build_flags}
lib_deps =
    Unity
    ArduinoFake
test_build_src = no
```

Test files must be placed in `test/native/avr/test_dispatch/`. PlatformIO discovers test files by looking for files matching `test_*.cpp` in test directories.

The test for `configure_memory` dispatch cannot directly call `configure_memory` without mocking `rurp_shield.h` hardware calls. The simplest viable test: set up a `firestarter_handle_t` with `protocol` and `cmd` fields only, call `configure_memory`, and assert that `firestarter_operation_init` is the expected handler pointer (or at least non-NULL for write/erase). If hardware-register calls block compilation, the test can assert on `firestarter_operation_main` pointer assignment which does not touch hardware.

---

## Common Pitfalls

### Pitfall 1: Reading `protocol_id` after the replaced block

**What goes wrong:** If the `protocol_id = programming.get("algorithm", 0)` line stays at line 380 (after the substring block) and the new table lookup references `protocol_id` at lines 371-377, the code will reference an undeclared variable.

**Why it happens:** The current code reads `type_str` before `protocol_id`. The replacement inverts this dependency.

**How to avoid:** Move or duplicate the `protocol_id` read to before the table lookup. The new block structure is:

```python
protocol_id = programming.get("algorithm", 0)  # moved up
if protocol_id and protocol_id in _ALGO_MEM_TYPE:
    determined_type = _ALGO_MEM_TYPE[protocol_id]
else:
    # legacy substring fallback
```

### Pitfall 2: Placing new if-blocks after the mem_type chain

**What goes wrong:** New `if (handle->protocol == ...)` blocks placed after line 83 (the mem_type chain) will never be reached for chips whose `mem_type == TYPE_EPROM (1)` — they'll be caught by the existing `if (handle->mem_type == TYPE_EPROM)` at line 83 first.

**Why it happens:** The dispatch table has two levels. Protocol-prefix blocks MUST precede the mem_type block.

**How to avoid:** Insert all new protocol-prefix `if` blocks between line 81 (`}` closing the 0x0D block) and line 83 (`if (handle->mem_type == TYPE_EPROM)`).

### Pitfall 3: Not removing TYPE_FLASH_TYPE_2

**What goes wrong:** The constant `TYPE_FLASH_TYPE_2 = 2` at line 25 becomes a dead code artifact. If left in, future maintainers may add a dispatch case for it (which would be incorrect — there is no type-2 handler).

**How to avoid:** Delete the `#define TYPE_FLASH_TYPE_2 2` line in the same commit as the dispatch extension. CONTEXT.md acceptance criterion §6 explicitly requires this.

### Pitfall 4: build_db.py SRAM detection using flags instead of proto_id

**What goes wrong:** If SRAM detection uses `flags & 0x10` (or any flags bit) instead of `proto_id`, some SRAM chips may still be tagged "Flash/EEPROM" or "UV-EPROM" depending on their minipro flags field.

**Why it happens:** The current `flags & 0x10` test checks an "electrically erasable" minipro flag. SRAM chips may or may not have this bit set in the XML.

**How to avoid:** Use `proto_id in {0x0E, 0x27, 0x28, 0x29}` as the authoritative SRAM check. This matches D4's explicit recommendation.

### Pitfall 5: DS1230AB(RW) — dual-entry SRAM that is NOT a SRAM protocol

**What goes wrong:** DS1230AB exists as two DB entries: `(RW)` variant with `algo=0x07` (UV-EPROM, correctly routed to `configure_eprom`) and `(TEST)` variant with `algo=0x28` (SRAM, fixed by Phase 12). The `(RW)` variant is NOT affected by Phase 12 and must NOT be changed.

**Why it happens:** The minipro XML tags the same physical chip differently for read-write mode vs test mode.

**How to avoid:** The D3 table lookup is purely by `algorithm` value. algo=0x07 → mem_type=1 (TYPE_EPROM). This is correct for the (RW) variant. Phase 12 does not need to special-case these entries.

### Pitfall 6: `_ALGO_MEM_TYPE` placed inside the class

**What goes wrong:** If the dict is placed inside `EpromDatabase` class, it's accessible but slightly less clear as a "constants" declaration.

**How to avoid:** Place it at module level, above the class definition, with other module constants. Consistent with how `KNOWN_PROTOCOLS` is at the module level in `build_db.py`.

---

## Code Examples

### Complete configure_memory After Phase 12 (target state)

```c
// Source: D2 dispatch order in 12-CONTEXT.md
void configure_memory(firestarter_handle_t* handle) {
    debug("Configuring memory");
    handle->firestarter_operation_init = NULL;
    handle->firestarter_operation_main = NULL;
    handle->firestarter_operation_end = NULL;

    switch (handle->cmd) {
        case CMD_READ:
            handle->firestarter_operation_main = memory_read_execute;
            break;
        case CMD_WRITE:
            handle->firestarter_operation_main = memory_write_execute;
            break;
        case CMD_VERIFY:
            handle->firestarter_operation_main = memory_verify_execute;
            break;
    }

    handle->firestarter_get_data = memory_get_data;
    handle->firestarter_set_data = memory_set_data;
    handle->firestarter_set_address = mem_util_set_address;
    handle->firestarter_set_control_register = memory_set_control_register;
    handle->firestarter_get_control_register = memory_get_control_register;

    mem_util_set_address(handle, 0);

    // Protocol-prefix dispatch (algorithm-first, per firmware CLAUDE.md contract)
    if (handle->protocol == 0x10) {
        configure_flash_intel(handle);
        return;
    }

    if (handle->protocol == 0x0D) {
        configure_eeprom28c(handle);
        return;
    }

    // NEW: Phase 12 extensions
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

    // mem_type fallback: backward compatibility for hand-crafted JSON / legacy host
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
}
```

### Firmware Unit Test Sketch (Unity + ArduinoFake)

```c
// Source: D7 §3 verification approach in 12-CONTEXT.md
// File: test/native/avr/test_dispatch/test_configure_memory.cpp
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
#include "memory.h"
#include "firestarter.h"

// Minimal handle setup helper
static firestarter_handle_t make_handle(uint32_t protocol, uint8_t mem_type, uint8_t cmd) {
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.mem_type = mem_type;
    h.cmd = cmd;
    return h;
}

void test_protocol_0x06_dispatches_flash3(void) {
    firestarter_handle_t h = make_handle(0x06, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_NULL(h.firestarter_operation_main);
}

void test_protocol_0x27_dispatches_sram(void) {
    firestarter_handle_t h = make_handle(0x27, 0, CMD_READ);
    configure_memory(&h);
    // configure_sram is a stub — operation_main stays NULL for CMD_READ
    // but the test confirms no error path was taken by checking response_code
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

// ... one test per protocol case ...

int main(int argc, char** argv) {
    UNITY_BEGIN();
    RUN_TEST(test_protocol_0x06_dispatches_flash3);
    RUN_TEST(test_protocol_0x27_dispatches_sram);
    // ... etc ...
    return UNITY_END();
}
```

### Python Regression Scan Script

```python
# Source: D7 §4 verification approach in 12-CONTEXT.md
# File: firestarter_app/tools/check_dispatch.py
"""
Regression scan: verify every chip in minipro_complete_db.json has a valid
firmware dispatch path after Phase 12.
"""
import json, sys

_ALGO_MEM_TYPE = {
    0x05: 5, 0x06: 3, 0x07: 1, 0x08: 1, 0x0B: 1,
    0x0D: 1, 0x0E: 4, 0x10: 1, 0x27: 4, 0x28: 4,
    0x29: 4, 0x35: 5, 0x39: 5,
}

# Simulated firmware dispatch (D2 order)
def dispatch(protocol, mem_type):
    if protocol in (0x10,): return "configure_flash_intel"
    if protocol in (0x0D,): return "configure_eeprom28c"
    if protocol in (0x06,): return "configure_flash3"
    if protocol in (0x05, 0x35, 0x39): return "configure_flash4"
    if protocol in (0x07, 0x08, 0x0B): return "configure_eprom"
    if protocol in (0x0E, 0x27, 0x28, 0x29): return "configure_sram"
    # mem_type fallback
    fallback = {1: "configure_eprom", 4: "configure_sram", 3: "configure_flash3", 5: "configure_flash4"}
    return fallback.get(mem_type, "ERROR")

with open("firestarter/data/minipro_complete_db.json") as f:
    db = json.load(f)

errors = []
for mfg, chips in db.items():
    for chip in chips:
        proto = chip.get("programming", {}).get("algorithm", 0)
        mt = _ALGO_MEM_TYPE.get(proto, None)
        handler = dispatch(proto, mt)
        if handler == "ERROR":
            errors.append(f"{mfg}/{chip.get('part_number')} proto=0x{proto:02X} mem_type={mt}")

if errors:
    print("FAIL: chips with no valid dispatch path:")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print(f"PASS: all {sum(len(v) for v in db.values())} chips have a valid dispatch path")
```

---

## State of the Art

| Old Approach | Current Approach | Relevant To Phase | Impact |
|--------------|------------------|------------------|--------|
| `type` integer as sole dispatch key (mem_type) | Protocol-first, mem_type as fallback | Phase 12 completes migration | N/A (Phase 12 is the change) |
| Substring match on `electrical.type` | Algorithm dict lookup | Python _map_data D3 | Eliminates brittle text dependency |
| `flags & 0x10` for all non-EPROM type tagging | `proto_id in SRAM_set` for SRAM, `flags & 0x10` for Flash | build_db.py D4 | Eliminates SRAM-as-EPROM mislabeling |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Protocol 0x39 maps to `configure_flash4` (FLASH_EEPROM_LIKE family) | Protocol 0x39 / D3 table | If 0x39 is a different family, chips added to the DB in future would route to wrong handler — low risk since no chips exist today |

**All other claims in this research are verified against source code or DB queries.**

---

## Open Questions

1. **configure_sram stub completeness**
   - What we know: `sram.cpp` implements `configure_sram` as a single `debug()` call. It sets no operation function pointers. `configure_memory` sets `firestarter_operation_main` to `memory_read_execute` (read) or `memory_write_execute` (write) generically before calling any `configure_*`. SRAM reads and writes with generic memory ops should work correctly since SRAM has no special timing or VPP requirements.
   - What's unclear: Whether the existing SRAM handler was intentionally minimal (SRAM needs no special init) or was never finished. The minipro XML marks 0x27/0x28/0x29 chips as "read-only from RURP's perspective" in some sources.
   - Recommendation: The planner should note this as a limitation — Phase 12 fixes the safety hazard (no VPP regulator), but SRAM write operations may or may not be functionally correct (no hardware to test). The phase acceptance criterion does not require hardware verification.

2. **D3 table 0x39 value**
   - What we know: Zero 0x39 chips in DB. KNOWN_PROTOCOLS includes 0x39. CLAUDE.md doesn't enumerate it separately.
   - What's unclear: Whether 0x39 is truly a flash_type_4 family or a distinct protocol.
   - Recommendation: Dispatch to `configure_flash4` with a code comment "// TODO: verify when 0x39 chips are added to DB". Risk is negligible since no such chips exist.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | Regression scan, DB build | ✓ | 3.12.13 [VERIFIED] | — |
| PlatformIO | Firmware build + test | ✓ | 6.1.19 [VERIFIED] | — |
| Unity (C test) | Firmware unit test | ✓ (in libdeps/native) [VERIFIED] | present | — |
| ArduinoFake | Firmware unit test | ✓ (in libdeps/native) [VERIFIED] | present | — |
| pytest | Python regression test | ✗ — not installed [VERIFIED] | — | Use plain Python script (tools/check_dispatch.py) |
| avr-size | Flash size reporting | ✗ [VERIFIED: `command -v avr-size`] | — | Use Intel HEX byte-counting script |
| Hardware programmer | Hardware verification | ✗ | — | Out of scope per D7 |

**Missing dependencies with fallback:**
- pytest: use `python3 tools/check_dispatch.py` — plain script, exits non-zero on failure
- avr-size: compute from HEX file with Python; `pio run` outputs flash usage in build log

**Missing dependencies with no fallback:**
- None blocking execution.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework (firmware) | Unity 2.x — present in `.pio/libdeps/native/Unity/` |
| Framework (Python) | Plain Python script (no pytest installed) |
| Firmware config file | `platformio.ini` — needs `[env:native]` section added |
| Quick run (Python regression) | `python3 tools/check_dispatch.py` |
| Firmware build check | `pio run -e uno && pio run -e leonardo` |
| Firmware test run | `pio test -e native` (after adding env:native to platformio.ini) |
| Full suite command | `pio run -e uno && pio run -e leonardo && python3 tools/check_dispatch.py` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-FW-01 | configure_eprom reached for 0x07/0x08/0x0B chips | unit (firmware) | `pio test -e native` | Wave 0 |
| REQ-FW-04 | configure_flash3 reached for 0x06 chips | unit (firmware) | `pio test -e native` | Wave 0 |
| REQ-SER-01 | mem_type correct for all DB chips | regression script | `python3 tools/check_dispatch.py` | Wave 0 |
| BLOCKER-2 | SRAM chips dispatch to configure_sram not configure_eprom | JSON spot-check + regression | `python3 tools/check_dispatch.py` | Wave 0 |
| AC-6 | TYPE_FLASH_TYPE_2 constant removed | code review | — | manual |
| AC-7 | Both firmware targets build clean | smoke | `pio run -e uno && pio run -e leonardo` | existing targets |
| AC-8 | CLAUDE.md dispatch table matches new code | doc review | — | manual |

### Sampling Rate

- **Per task commit:** `python3 tools/check_dispatch.py` (runs in < 1 second)
- **Per wave merge:** `pio run -e uno && pio run -e leonardo && python3 tools/check_dispatch.py`
- **Phase gate:** Above full suite + `pio test -e native` green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `firestarter_app/tools/check_dispatch.py` — Python regression scan (REQ-SER-01, BLOCKER-1, BLOCKER-2)
- [ ] `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — Unity dispatch unit tests
- [ ] `[env:native]` section in `firestarter/platformio.ini` — required for `pio test -e native`

---

## Security Domain

This phase is pure firmware dispatch routing and Python database field derivation. No authentication, session management, access control, cryptography, or user input handling is involved.

ASVS categories are not applicable. No threat patterns are introduced by adding `if (protocol == 0xNN)` dispatch cases to an embedded C function.

The SRAM fix (BLOCKER-2) is a hardware safety improvement that reduces risk of applying 12V VPP to a 5V part — this is an electrical safety concern, not an information security concern.

---

## Sources

### Primary (HIGH confidence)

- `firestarter/src/proms/memory.cpp` — current configure_memory dispatch, exact line numbers verified
- `firestarter/src/proms/eprom.cpp` — configure_eprom + eprom_check_vpp, VPP regulator enabling confirmed
- `firestarter/src/proms/sram.cpp` — configure_sram stub verified
- `firestarter/src/proms/flash_type_3.cpp`, `flash_type_4.cpp` — handler implementations confirmed
- `firestarter/include/firestarter.h` — firestarter_handle_t struct, protocol field (uint32_t at line 81)
- `firestarter/src/json_parser.c` — get_type (line 301), get_algorithm (lines 312-314)
- `firestarter_app/firestarter/database.py` — _map_data lines 371-380, convert_to_programmer confirmed
- `firestarter_app/tools/build_db.py` — KNOWN_PROTOCOLS line 89, chip emission line 214
- `firestarter_app/firestarter/data/minipro_complete_db.json` — all chip count queries verified by Python script
- `.planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-CONTEXT.md` — locked decisions D1-D7
- `.planning/INTEGRATION-CHECK.md` — BLOCKER-1/BLOCKER-2 traces confirmed
- `.planning/v1.0-MILESTONE-AUDIT.md` — chip counts and reach table
- `firestarter/.pio/build/uno/firestarter_uno.hex` — flash usage computed: 24,402 bytes / 32,768 bytes
- `firestarter/.pio/libdeps/native/Unity/`, `ArduinoFake/` — test infrastructure verified present
- `firestarter/platformio.ini` — no existing test env confirmed

### Secondary (MEDIUM confidence)

- CLAUDE.md files for both sub-repos — dispatch table and KNOWN_PROTOCOLS list

### Tertiary (LOW confidence, marked ASSUMED)

- A1: Protocol 0x39 is flash_type_4 family (no DB chips to verify against)

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — all files verified by direct read
- Architecture (dispatch structure): HIGH — verified against source
- Chip counts: HIGH — verified by Python DB query (277 broken + 52 SRAM hazard)
- Pitfalls: HIGH — derived from exact code structure
- Protocol 0x39 dispatch target: MEDIUM — inferred, not verified

**Research date:** 2026-05-11
**Valid until:** 2026-06-11 (stable domain; no external dependencies subject to change)

# Architecture: v1.11 Extension Points

**Domain:** Firestarter dual-repo — decode pipeline + firmware algorithm handlers
**Researched:** 2026-06-08
**Confidence:** HIGH (derived from direct codebase reading of all named files)

---

## Scope

This document answers four architecture questions for v1.11:

1. How should a source-grounded decode pipeline replace the current heuristic overrides?
2. How does a new firmware algorithm handler plug into `configure_memory` dispatch?
3. What pinouts.json structure changes do new DIP-24/28/32 families require?
4. What is the correct build order given the cross-repo dependencies?

This is an **extension** document: the core end-to-end data path is already built and proven. Nothing here redesigns it.

---

## Existing Architecture (Baseline — Do Not Redesign)

```
infoic.xml
    ↓  build_db.py:main()
        filter: package_details (pin_count, is_smd, is_serial, type_int)
        decode: protocol_id → proto_id
                voltages  → vpp_mv
                pin_map low byte → pm_idx
                variant → variant_lo
        resolve: resolve_pinout_key(pin_count, variant, flags, pm_idx, proto_id)
                 [4-tier lookup: PIN_MAP_PROTO_TO_PINOUT → PIN_MAP_TO_PINOUT → DIP28_VARIANT_MAP → per-pin-count default]
        override: WARNING-5 (DIP28_2764 + 0x07 + Flash/EEPROM → proto_id=0x0D)
                  fm1608 (type_int==4 + EPROM-family → proto_id=0x28 + pinout override)
        emit:  chip_entry = {part_number, electrical{type,size_bytes,pin_count,vpp,vpp_mv,vdd,vcc},
                             programming{algorithm,pulse_duration,chip_id_check,chip_id_value},
                             pinout}
    ↓  chip_database.json  (do not hand-edit)
    ↓  EpromDatabase.get_eprom(name)
    ↓  _map_data(ic, manufacturer)
        reads: electrical.pin_count, programming.algorithm, ic.pinout
        derives: determined_type via _ALGO_MEM_TYPE[protocol_id]
        calls: get_bus_config(pin_count, pinout_key)
            → get_pin_map(pins, variant) → pinouts.json[variant]["pins"]
            → compose with pin_conversions[pins] (socket → RURP bus line)
            → returns {bus:[], rw-pin:N, vpp-pin:N, static-high:[]}
    ↓  convert_to_programmer(full_eprom_data)
        produces: {memory-size, type, algorithm, pin-count, vpp_mv, pulse-delay,
                   chip-id?, bus-config{bus, rw-pin?, vpp-pin?, static-high?}, flags}
    ↓  eprom_operations.py builds JSON command dict with cmd integer
    ↓  serial_comm.py COBS+CRC8 frames it → Arduino at 250000 baud
    ↓  json_parser.c → firestarter_handle_t
        handle->protocol = algorithm field
        handle->mem_type = type field (fallback)
        handle->pins     = pin-count field
        handle->bus_config = bus-config struct
    ↓  memory.cpp:configure_memory(handle)
        protocol-prefix if-return chain → handler function
    ↓  handler sets handle->firestarter_operation_{init,main,end}
```

---

## Question 1: Source-Grounded Decode Pipeline

### Current Problem

`build_db.py` resolves pinout keys through four tiers of tables: `PIN_MAP_PROTO_TO_PINOUT`, `PIN_MAP_TO_PINOUT`, `DIP28_VARIANT_MAP`, and per-pin-count defaults. These tables were built from a chip-by-chip survey of `infoic.xml` plus single-device spot-checks ("one-rom verified"). The tables codify the right answer for chips already surveyed but cannot reason about new or unchecked chips; errors are silent (wrong pinout, no warning).

The two safety overrides (WARNING-5, fm1608) are also heuristic: they detect mis-tagged chips by combining pinout key + protocol + electrical type. They will miss new families with the same combination in different forms.

### Source-Grounded Replacement

The principled signal from the minipro source is **`gnd`/`vcc`/`pin_map` bitmasks in `database.c`**. Each chip entry in minipro carries explicit `gnd` and `vcc` bitmasks that state which physical DIP pin numbers are GND/VCC, plus a `pin_map` cluster value used as a family discriminator. These are the authoritative physical-pin assignments, not heuristics.

**What to build:**

1. **Field dictionary** (host-only, pure data)

   A structured reference — as Python data tables or a companion JSON file — that maps each `infoic.xml` attribute to its decoded meaning. Minimum required fields for Firestarter:

   | infoic.xml attribute | Decoded meaning | How to use |
   |---|---|---|
   | `package_details` | bits [30:24] = pin count, bit 31 = SMD, bits [15:8] = serial-interface | Filter: keep DIP 24/28/32, no SMD, no serial |
   | `type` | 1=Memory/ROM/EPROM, 4=SRAM/NVRAM | Safety guard: type==4 with EPROM proto → fm1608 path |
   | `protocol_id` | Algorithm family; maps 1:1 to KNOWN_PROTOCOLS | Primary dispatch key unchanged |
   | `voltages` | bits [7:0] = VPP step (VPP_MV table), bits [11:8] = VDD, bits [15:12] = VCC | VPP/VCC decode unchanged |
   | `flags` | bit 4 (0x10) = electrically erasable, bit 5 (0x20) = chip-ID readable | WARNING-5 discriminator; chip-id flag |
   | `pin_map` | low byte = family cluster (pm_idx); NOT a DIP pin assignment | Clustering signal, not direct pin data |
   | `variant` | family sub-discriminator within a pm_idx cluster | DIP28_VARIANT_MAP uses low byte |
   | `pulse_delay` | programming pulse width; unit depends on protocol_id | interpret_timing() already handles this |
   | `chip_id` | 16-bit manufacturer/device code | Passed as-is to firmware |
   | `code_memory_size` | chip capacity in bytes | mem_size |

   This dictionary lives in `build_db.py` as annotated constants (current `VPP_MV`, `VCC_VOLTAGES`, etc. are already this pattern) or in a companion `tools/field_dictionary.py` for clarity.

2. **Principled `pm_idx` pinout resolution** (host-only, `build_db.py`)

   Replace the four-tier guess tables with a two-tier scheme grounded in minipro source:

   **Tier 1 (primary):** `(pin_count, proto_id)` → pinout key. Protocol ID already encodes the memory technology; technology determines physical interface:
   - EPROM family (0x07, 0x08, 0x0B): VPP on chip-specific pin, PGM strobe, address bus fills all remaining pins
   - 5V Flash AMD (0x05, 0x06): no VPP, WE at a defined pin, address bus
   - 5V EEPROM (0x0D): no VPP, WE, same JEDEC address bus within size class
   - SRAM (0x0E, 0x27, 0x28, 0x29): no VPP, WE, JEDEC SRAM layout
   - Intel Flash (0x10): VPP at pin 1 (32-pin) or pin 31 (28-pin), no PGM

   Within a pin count + protocol family the physical layout is determined by `code_memory_size` (how many address lines) and `pm_idx` (legacy variant sub-family). Most new entries reduce to "which JEDEC standard layout for this size class."

   **Tier 2 (refinement):** `pm_idx` as a consistency check, not a primary key. After Tier 1 assigns a layout, `pm_idx` within the same (pin_count, proto_id) group should be consistent. Conflicts are logged as a cross-check signal, not silently accepted.

3. **Replacing the two inline overrides** (host-only)

   WARNING-5 and fm1608 are correct guards against genuinely mis-tagged upstream data. For v1.11 they should become:
   - Named predicate functions: `_is_mistagaged_5v_eeprom(proto_id, pinout_key, etype)` and `_is_mistagaged_sram_fram(type_int, proto_id)` with docstrings citing the upstream mis-tagging pattern.
   - The override logic stays in `build_db.py`, but the discrimination rules are derived from the field dictionary (what the fields MEAN) rather than discovered by chip survey.

4. **Wire contract impact: NONE**

   The wire JSON is unchanged: `algorithm` (int), `vpp_mv` (int mV), `bus-config` (struct), `pin-count` (int). A source-grounded pipeline that emits the same fields has zero protocol impact. The firmware does not know or care how the host derived the algorithm integer.

### Where the Field Dictionary Lives

In `tools/build_db.py` as annotated module-level constants, matching the existing `VPP_MV`, `VCC_VOLTAGES`, `PROTOCOL_MAP` pattern. This keeps the decode logic co-located with the only consumer. A separate `tools/field_dictionary.py` is appropriate if the dictionary grows large enough to obscure the pipeline logic; that is a v1.11 judgement call, not a hard constraint.

---

## Question 2: New Firmware Handler Integration Contract

### How `configure_memory` Dispatch Works

`memory.cpp:configure_memory` (lines 45-118) is a sequence of `if (handle->protocol == X) { configure_Y(handle); return; }` branches. The sequence matters (higher priority = earlier):

1. `0x10` → `configure_flash_intel`
2. `0x0D` → `configure_eeprom28c`
3. `0x06` → `configure_flash3`
4. `0x05 || 0x35 || 0x39` → `configure_flash4`
5. `0x07 || 0x08 || 0x0B` → `configure_eprom`
6. `0x0E || 0x27 || 0x28 || 0x29` → `configure_sram`
7. `mem_type == TYPE_EPROM` → `configure_eprom` (fallback)
8. `mem_type == TYPE_SRAM` → `configure_sram` (fallback)
9. `mem_type == TYPE_FLASH_TYPE_3` → `configure_flash3` (fallback)
10. `mem_type == TYPE_FLASH_TYPE_4` → `configure_flash4` (fallback)
11. error

A new protocol `0xNEW` is added by inserting one block before the `mem_type` fallback chain (steps 7-10). Order within the protocol chain matters only if a new protocol numeric value could be confused with a range expression; in practice each `if` is an exact equality test.

### Handler Signature Contract

```cpp
// Declaration in firestarter/include/<handler_name>.h
void configure_<family>(firestarter_handle_t* handle);

// Implementation in firestarter/src/proms/<handler_name>.cpp
void configure_<family>(firestarter_handle_t* handle) {
    // 1. Log entry (matches existing pattern)
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_<FAMILY>);

    // 2. Set firestarter_operation_end if cleanup is needed (e.g., flash_intel does this)
    //    Most handlers leave it NULL (set to NULL by configure_memory before dispatch).

    // 3. Switch on handle->cmd and assign function pointers:
    switch (handle->cmd) {
        case CMD_READ:     /* usually no override — memory_read_execute handles generic read */
            break;
        case CMD_WRITE:
            handle->firestarter_operation_init = <family>_write_init;
            handle->firestarter_operation_main = <family>_write_execute;
            break;
        case CMD_ERASE:
            handle->firestarter_operation_main = <family>_erase_execute;
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;  /* reuse */
            break;
        case CMD_CHECK_CHIP_ID:
            handle->firestarter_operation_init = NULL;
            handle->firestarter_operation_main = <family>_check_chip_id;
            break;
    }

    // 4. Set default pulse_delay if protocol-specific default needed
    //    (eprom.cpp pattern: switch on handle->protocol for 0x08/0x0B/default)

    // 5. Override handle->firestarter_set_control_register if VPP routing
    //    needs per-family control (eprom.cpp installs eprom_internal_set_control_register
    //    to swap CTRL_VPE_ENABLE → CTRL_VPP_P1_ENABLE for 32-pin chips)
}
```

### VPP/Pin Assertion Rules

The control register bits are defined in `rurp_pinout.h`. The rules for safe VPP engagement, derived from existing handlers:

| Family | VPP path | Assert in | Deassert in |
|---|---|---|---|
| EPROM (0x07/0x08) | `CTRL_VPP_REGULATOR_ENABLE` + `CTRL_VPP_VPE_DROP_ENABLE` | `eprom_write_execute` (lazy, first chunk only) | `eprom_write_execute` after final retry fail; NOT in END phase |
| EPROM legacy (0x0B) | `CTRL_VPP_REGULATOR_ENABLE` only (no drop) | same | same |
| Intel Flash (0x10) | `CTRL_VPP_REGULATOR_ENABLE` + `CTRL_VPP_P1_ENABLE` | `flash_intel_write_init` (eager, before VPP check) | `flash_intel_cleanup` (END phase — MUST run) |
| 5V flash / EEPROM / SRAM | none | n/a | n/a |

**Safety rule for any new VPP handler:** Before asserting the regulator in WRITE_INIT, call `rurp_read_voltage_mv()` and compare against `handle->vpp_mv` (±500 mV high / 5% low) with `FLAG_FORCE` gate — exactly as `eprom_check_vpp` and `flash_intel_check_vpp` do. This is the REQ-SAF-01 pre-pulse VPP ADC compare requirement.

**Safety rule for A9 (chip-ID via 12V on A9):** All four existing chip-ID implementations assert `CTRL_VPP_REGULATOR_ENABLE` + `CTRL_VPP_A9_ENABLE`, wait 100ms, read, then deassert. Any new family supporting chip-ID must follow this exact sequence. Do NOT leave `CTRL_VPP_REGULATOR_ENABLE` asserted across a read — that was the Bug A confounder path.

### VPP Routing and `handle->pins`

`mem_util_set_address` in `memory.cpp` reads `handle->pins` to decide control-register layout:

- `handle->pins < 32`: sets `CTRL_VPP_VPE_DROP_ENABLE` in the mask (shared with `CTRL_ADDRESS_LINE_16` on legacy hardware)
- `handle->pins == 28`: forces `CTRL_ADDRESS_LINE_17` high (28-pin chips don't need A17 for addressing but the hardware needs this bit set)
- `handle->pins == 32`: uses `CTRL_VPP_P1_ENABLE` for VPP routing (pin 1 is the VPP pin on 32-pin EPROM/Intel-Flash layouts)

A new handler for a 32-pin VPP family must set `CTRL_VPP_P1_ENABLE` (not `CTRL_VPP_VPE_DROP_ENABLE`) because pin 1 on 32-pin DIP is socket position 21 in the RURP bus layout.

### dispatch line and `handle->mem_type`

The firmware dispatch chain reads `handle->protocol` (from `algorithm` JSON field) **before** `handle->mem_type`. A new handler needs:

1. **Firmware dispatch block** (one if-return in `configure_memory`, `firestarter/src/proms/memory.cpp`)
2. **`_ALGO_MEM_TYPE` entry** (`firestarter_app/firestarter/database.py`, line ~48) — maps new `proto_id` to the appropriate `TYPE_*` integer for the `mem_type` fallback field
3. **`KNOWN_PROTOCOLS` addition** in both `build_db.py` (line 83) and `database.py` is NOT needed unless the protocol appears in `infoic.xml`; if it does, add to `KNOWN_PROTOCOLS` in both files (they must stay in sync)
4. **`PROTOCOL_MAP` entry** in both `build_db.py` (line 25) and `database.py` (line 35) — human-readable name string

Items 2-4 are host-only changes. Items 2-4 must land in the same commit as the firmware dispatch block when the protocol ID is new to the system (dual-repo lockstep). If the protocol ID is already in `KNOWN_PROTOCOLS` but has no firmware handler (e.g. `0x2A`, `0x2C`, `0x2E` for NVRAM families), only the firmware dispatch block + `_ALGO_MEM_TYPE` entry are new; `KNOWN_PROTOCOLS` update is not needed.

### `constants.py` ↔ `firestarter.h` Sync

The parity test at `tests/test_revision_constants_parity.py` pattern covers `REVISION_*` constants. The firmware-contract guard should extend to any new `FLAG_*` or `CMD_*` values if a new handler introduces them. In practice v1.11 handlers are unlikely to need new flag bits (existing `FLAG_CAN_ERASE`, `FLAG_SKIP_ERASE`, `FLAG_SKIP_BLANK_CHECK`, `FLAG_VPE_AS_VPP`, `FLAG_FORCE` cover all cases). If a new flag IS needed, it must be added to both files simultaneously in a single dual-repo commit.

**Touch-point summary for a new handler:**

| File | Change | Scope |
|---|---|---|
| `firestarter/src/proms/<name>.cpp` | New handler implementation | firmware |
| `firestarter/include/<name>.h` | Handler declaration | firmware |
| `firestarter/src/proms/memory.cpp` | Add if-return dispatch block | firmware |
| `firestarter_app/firestarter/database.py` | Add `_ALGO_MEM_TYPE[proto_id]` entry | host |
| `firestarter_app/tools/build_db.py` | Add `PROTOCOL_MAP[proto_id]` entry; add to `KNOWN_PROTOCOLS` if new | host |
| `firestarter_app/firestarter/constants.py` | Add new `FLAG_*` or `CMD_*` only if genuinely new | host (lockstep if new) |
| `firestarter/include/firestarter.h` | Same as above | firmware (lockstep if new) |
| `firestarter_app/firestarter/data/pinouts.json` | Add pinout entry if new physical layout | host |
| `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` | Add Unity test case for new protocol | firmware |

---

## Question 3: pinouts.json Schema and New Entries

### Current Schema (Canonical)

A `pinouts.json` entry is an object keyed by a string identifier (e.g. `"DIP32_SST39SF040"`):

```json
"DIP32_SST39SF040": {
    "name": "human-readable description",
    "comment": "optional evidence / derivation note",
    "pins": {
        "vcc-pin":          [32],
        "gnd-pin":          [16],
        "address-bus-pins": [12, 11, 10, 9, 8, 7, 6, 5, 27, 26, 23, 25, 4, 28, 29, 3, 2, 30, 1],
        "data-bus-pins":    [13, 14, 15, 17, 18, 19, 20, 21],
        "ce-pin":           [22],
        "oe-pin":           [24],
        "rw-pin":           [31],
        "vpp-pin":          [1],
        "pgm-pin":          [27],
        "nc-pin":           [1, 26],
        "static-high-pins": [24]
    }
}
```

**Field semantics:**

| Key | Meaning | Required? | Notes |
|---|---|---|---|
| `vcc-pin` | VCC supply pin(s) | yes | Used by `get_adapter_table` and `static-high-pins` derivation |
| `gnd-pin` | GND pin(s) | yes | |
| `address-bus-pins` | A0, A1, ... in order | yes | Order = address-bit index; `get_bus_config` maps to RURP bus lines |
| `data-bus-pins` | D0–D7 in order | yes | |
| `ce-pin` | Chip-enable pin(s) | yes | |
| `oe-pin` | Output-enable pin(s) | yes | |
| `rw-pin` | WE (write-enable) for EEPROM/SRAM/Flash | conditional | Required for any writable family without PGM strobe |
| `vpp-pin` | VPP programming voltage pin | conditional | Set to the OE pin for 27512-family (shared OE/VPP); omit for 5V families |
| `pgm-pin` | PGM strobe for UV-EPROM | conditional | 2764/27256 family; not present on 27512 or 5V |
| `nc-pin` | Explicitly no-connect pins | optional | Prevents address-bus assertion on truly unused pins |
| `static-high-pins` | Pins driven HIGH unconditionally | optional | Consumed by `convert_to_programmer` → `bus_config.static_high_mask` |

**How `static-high-pins` becomes `static_high_mask`:**

`database.py:get_bus_config` converts `static-high-pins` → list of RURP bus line numbers via `pin_conversions[pins]`. `convert_to_programmer` assembles these into `static-high` array in `bus-config`. `memory.cpp:mem_util_remap_address_bus` ORs `config.static_high_mask` into every address write. This is the correct end-to-end path for VCC-tied-high pins on DIP24 chips (e.g. pin 24 of 2716 which sits at bus line 13 on the RURP).

### New Entries Required for v1.11 Type Expansion

**DIP24 families (newly skipped):**

The safety skip in `build_db.py` lines 359-370 blocks 24-pin EEPROM chips (proto 0x07/0x08/0x0B + `flags & 0x10`). Lifting this skip for a proper `configure_eeprom28c`-based path requires a `DIP24_28C16` (or similar) pinout entry if those chips have a distinct physical layout from `DIP24_2716`. On most AT28C16/AT28C04-class chips, VCC is at pin 24, GND at pin 12, and WE is at pin 21 — the same socket position that the `DIP24_2716` entry assigns to VPP. A new `DIP24_28C_EEPROM` entry with `rw-pin: [21]` and no `vpp-pin` is needed.

**DIP28 NVRAM/Timekeeper (0x2A/0x2C/0x2E, feasibility-gated):**

If the NVRAM protocols are deemed feasible, the physical layout follows JEDEC SRAM-class DIP28. `DIP28_JEDEC_SRAM_8K` (already present) covers 8K. A `DIP28_JEDEC_SRAM_32K` entry would cover the 32K-class Dallas DS1225/DS1230 family (A0-A14, WE at pin 27, same CE/OE positions).

**DIP32 NVRAM (0x2E NVRAM_512K, feasibility-gated):**

`DIP32_SST39SF040` (JEDEC 5V flash SRAM-class, WE at pin 31) already covers the physical layout of JEDEC 32-pin SRAM/NVRAM (confirmed by the existing `(32, 0, 0x0E): "DIP32_SST39SF040"` and `(32, 0, 0x29): "DIP32_SST39SF040"` entries). No new 32-pin SRAM pinout entry is required unless a specific NVRAM family diverges from the JEDEC layout.

**FWH (0x11, feasibility assessment needed):**

FWH (Firmware Hub) is a serial LPC-bus interface, not a parallel DIP bus. No DIP-socket pinout entry is architecturally possible. This family should be filtered out at the `is_serial` check in `build_db.py`; confirm whether the `package_details` serial-interface bits (bits [15:8]) correctly flag FWH chips. If they do, no pinout entry is needed and FWH is a non-issue. If not, an explicit proto_id filter (`0x11` to skip list) is the right fix.

### Schema Extension Rules

Three rules that must hold for any new pinout entry:

1. **Pin coverage is complete:** Every DIP pin 1..N must be covered by exactly one functional key (VCC, GND, address-bus, data-bus, CE, OE, rw-pin, vpp-pin, pgm-pin, nc-pin, static-high-pins). Use `nc-pin` for genuinely unused pins. `get_adapter_table` renders "NC" for pins not mentioned — gaps are a documentation gap, not a functional bug, but they mask wiring errors.

2. **Address-bus-pins order is A0-first:** The first element is A0 (LSB), last element is AN (MSB). This order is consumed directly by `get_bus_config` to produce the `bus[]` array passed to `mem_util_remap_address_bus`. Getting this wrong silently reverses the address bus.

3. **`static-high-pins` must correspond to pins that the RURP hardware must actively drive HIGH** (i.e. they map to a real RURP bus line via `pin_conversions`). Pins that float or are driven by the chip itself should NOT appear here.

---

## Question 4: Build Order

### Dependency Graph

```
[A] Field dictionary & infoic.xml decode analysis (host-only research artifact)
    ↓
[B] Re-derived resolve_pinout_key + override predicates (build_db.py rewrite, host-only)
    ↓
[C] New pinouts.json entries (host-only data layer)
    ↓ (parallel with D after B, C settled)
[D] DB regeneration: python tools/build_db.py → new chip_database.json (host-only)
    ↓
[E] New firmware handler(s) in firestarter/src/proms/ + dispatch block in memory.cpp (firmware)
    ↓ (E and D must land together for dual-repo lockstep)
[F] _ALGO_MEM_TYPE + PROTOCOL_MAP + KNOWN_PROTOCOLS updates in database.py (host, lockstep with E)
    ↓
[G] Unity dispatch tests for new protocols (firmware, can accompany E)
    ↓
[H] Correctness gate: cross-check regression proving each decoded field (host tooling)
    ↓
[I] Authoritative decode docs (package-details.md / protocol-flags.md / protocol-id.md)
```

### Host-Only vs Firmware vs Dual-Repo Lockstep

| Phase group | Repos touched | Notes |
|---|---|---|
| A: Field dictionary analysis | host (tools/, docs) | Research artifact; no wire change |
| B: resolve_pinout_key rewrite | host (tools/build_db.py) | Affects chip_database.json only; no wire change until DB regen |
| C: New pinouts.json entries | host (firestarter_app/firestarter/data/pinouts.json) | Independent of firmware |
| D: DB regen | host (chip_database.json) | Only committed after B+C are stable; the JSON file is generated |
| E: New handler + dispatch block | firmware (firestarter/src/proms/, memory.cpp, include/) | Firmware-only until lockstep commit |
| F: database.py + build_db.py constants update | host (database.py, build_db.py) | **Lockstep with E**: must be committed to the same dual-repo milestone cut as E |
| G: Unity tests | firmware (test/native/) | Accompanies E; CI must stay green |
| H: Correctness gate tooling | host (tools/) | No runtime behavior; validates pipeline |
| I: Decode docs | host (firestarter_app/firestarter/data/docs/ or .planning/) | Documentation artifact |

**What makes E+F a lockstep change:**

When a previously-skipped `proto_id` (e.g. `0x2A`) is added to `KNOWN_PROTOCOLS` in `build_db.py`, the database pipeline will start emitting chips with `algorithm=0x2A`. When those entries reach the firmware, `configure_memory` must have a dispatch block for `0x2A` or it falls through to the `mem_type` fallback chain. An app-only update without the firmware dispatch block would silently route those chips to the wrong handler. Therefore: new-protocol host changes and new-protocol firmware dispatch blocks are a dual-repo lockstep milestone unit, not independent patches.

**Exception:** If `proto_id` is already dispatched in firmware (e.g. `0x28 → configure_sram`) and the only change is a new pinout entry for a family already handled, this is host-only. The firmware does not know about pinout keys.

### Phase Decomposition for Roadmap

| Phase | Work | Scope | Dependency |
|---|---|---|---|
| 56 | Field dictionary: annotate every infoic.xml attribute meaning; produce the authoritative `package-details.md`, `protocol-flags.md`, `protocol-id.md` docs | host-only (research + docs) | none |
| 57 | Re-derive resolve_pinout_key: replace PIN_MAP_* guess tables with (pin_count, proto_id, mem_size) logic grounded in the field dictionary; replace WARNING-5 and fm1608 with named predicates | host-only (build_db.py) | Phase 56 |
| 58 | New pinouts.json entries for families not yet covered (DIP24 EEPROM; any new size class; confirm NVRAM families); DB regen | host-only | Phase 57 |
| 59 | Feasibility: NVRAM (0x2A/0x2C/0x2E) and FWH (0x11) — hardware capability vs RURP shield, safety review, protocol datasheet analysis; go/no-go gate for adding handlers | firmware research (no code) | Phase 56 |
| 60 | New firmware handlers for approved type families + dispatch blocks; Unity dispatch tests | firmware + lockstep host (E+F above) | Phase 58, Phase 59 |
| 61 | Correctness gate: automated cross-check tool verifying pipeline output against field dictionary + spot-check datasheets; regression suite | host-only | Phase 57-60 |

Phases 57, 58, and 59 can proceed in parallel after Phase 56 delivers the field dictionary. Phase 60 (firmware) depends on Phase 58 (pinouts must be stable before writing a handler that references them in the DB), but the handler C++ code can be prototyped earlier.

---

## Integration Points at File+Function Granularity

### Host-Side Touch Points for New Protocol Support

| File | Function / Symbol | Change |
|---|---|---|
| `firestarter_app/tools/build_db.py` | `PROTOCOL_MAP` (line 25) | Add `{0xNEW: "NAME"}` |
| `firestarter_app/tools/build_db.py` | `KNOWN_PROTOCOLS` (line 83) | Add `0xNEW` |
| `firestarter_app/tools/build_db.py` | `resolve_pinout_key` (line 210) | Add (pin_count, proto_id) case if layout is new |
| `firestarter_app/tools/build_db.py` | `main()` filter block (line 338) | Add safety skip if a new family is not yet safe to emit |
| `firestarter_app/firestarter/data/pinouts.json` | top-level key | Add new pinout entry |
| `firestarter_app/firestarter/database.py` | `PROTOCOL_MAP` (line 35) | Add `{0xNEW: "NAME"}` (mirrors build_db.py) |
| `firestarter_app/firestarter/database.py` | `_ALGO_MEM_TYPE` (line 48) | Add `{0xNEW: TYPE_INT}` |
| `firestarter_app/firestarter/constants.py` | `FLAG_*` / `CMD_*` | Only if a new flag or command is needed (rare) |

### Firmware-Side Touch Points for New Handler

| File | Function / Symbol | Change |
|---|---|---|
| `firestarter/src/proms/memory.cpp` | `configure_memory` (line 45) | Add `if (handle->protocol == 0xNEW) { configure_new(handle); return; }` |
| `firestarter/src/proms/<new_name>.cpp` | `configure_new()` | New file: handler implementation |
| `firestarter/include/<new_name>.h` | `configure_new()` declaration | New file: header |
| `firestarter/src/proms/memory.cpp` | `#include "<new_name>.h"` | Add include at top |
| `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` | Unity test | Add `RUN_TEST(test_protocol_0xNEW_dispatches_to_configure_new)` |
| `firestarter/include/firestarter.h` | `FLAG_*` or `CMD_*` | Only if new (lockstep with constants.py) |

### `pin_conversions` is Firmware-Board-Wiring, Not a Protocol Concern

`pin_conversions` in `database.py` (line 75) maps DIP socket pin number → RURP bus line number. This is the physical RURP board wiring — a hardware constant, not a protocol or chip family property. It does not change for new chip families unless a new package size (e.g. DIP40) were ever added (which is out of scope). For DIP 24/28/32 within the existing RURP hardware, `pin_conversions` is complete and frozen.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Adding More Guess Tables

**What:** Extending `PIN_MAP_PROTO_TO_PINOUT` or `PIN_MAP_TO_PINOUT` with new (pin_count, pm_idx, proto_id) entries without minipro source or datasheet backing.

**Why bad:** The existing tables are the technical debt v1.11 is reducing. Each entry added without evidence is another unknown to carry forward and a potential damage path if wrong.

**Instead:** For any new pinout entry, cite the source (minipro `database.c` gnd/vcc masks, JEDEC standard, or a specific chip datasheet) in the `pinouts.json` comment field. If you cannot cite a source, the entry is not ready.

### Anti-Pattern 2: Skipping the Pre-Pulse VPP ADC Compare

**What:** Writing a new VPP-using handler without calling `rurp_read_voltage_mv()` and comparing to `handle->vpp_mv` before the first programming pulse.

**Why bad:** REQ-SAF-01 was introduced specifically because an overvoltage condition (wrong regulator calibration, wrong chip) can damage the chip. The Intel flash handler shows the correct pattern (`flash_intel_check_vpp`).

**Instead:** Copy `eprom_check_vpp` or `flash_intel_check_vpp` as the VPP init step for any handler that asserts `CTRL_VPP_REGULATOR_ENABLE`.

### Anti-Pattern 3: Separate DB Regen Commit from Handler Commit

**What:** Committing a new handler to firmware, then in a separate PR committing the `KNOWN_PROTOCOLS` / `_ALGO_MEM_TYPE` updates that expose new chips to that handler.

**Why bad:** Between the two commits, the database will emit `algorithm=0xNEW` for chips that the installed firmware cannot dispatch. The firmware will fall through to a `mem_type` fallback or emit `MSG_ERR_MEM_TYPE_UNSUPPORTED`.

**Instead:** Dual-repo lockstep. New protocol support lands as a coordinated firmware+host commit pair in a single milestone cut with the same `BETA_VERSION` tag.

### Anti-Pattern 4: Adding NC Pins to `address-bus-pins`

**What:** Including a truly-NC DIP pin in the `address-bus-pins` list because it "fills the right bit position."

**Why bad:** `get_bus_config` maps every address-bus entry through `pin_conversions`, produces a RURP bus line number, and passes it to `mem_util_remap_address_bus`. An NC DIP pin that maps to a real RURP bus line will be driven with address data, which may conflict with another chip's signal.

**Instead:** Use `nc-pin` for no-connect pins. If a chip has 13 address lines but the pin positions leave a gap, the `address-bus-pins` list should have exactly 13 entries for A0-A12, with the NC pin listed separately.

### Anti-Pattern 5: A New pm_idx Table Without Retiring the Old One

**What:** Adding entries to `PIN_MAP_PROTO_TO_PINOUT` for new families as part of v1.11 while leaving the old heuristic tables in place as fallbacks.

**Why bad:** The "new principled rule + old heuristic fallback" combination makes the resolution logic harder to reason about and means errors in the old tables still silently produce wrong results for uncovered chips.

**Instead:** The re-derived pipeline should replace the lookup tables, not extend them. If a chip was previously covered by a guess table and the principled rule produces the same answer, the table entry is redundant and should be removed.

---

## Sources

- Direct code reading: `firestarter_app/tools/build_db.py` (all 538 lines)
- Direct code reading: `firestarter_app/firestarter/data/pinouts.json` (all 124 lines)
- Direct code reading: `firestarter_app/firestarter/database.py` (all 683 lines)
- Direct code reading: `firestarter/src/proms/memory.cpp` (all 371 lines)
- Direct code reading: `firestarter/src/proms/eprom.cpp`
- Direct code reading: `firestarter/src/proms/eeprom_28c.cpp`
- Direct code reading: `firestarter/src/proms/flash_intel.cpp`
- Direct code reading: `firestarter/src/proms/flash_type_3.cpp`
- Direct code reading: `firestarter/src/proms/sram.cpp`
- Direct code reading: `firestarter/include/firestarter.h`
- Direct code reading: `firestarter/include/rurp_pinout.h`
- `firestarter/CLAUDE.md` — dispatch order table (verified matches memory.cpp)
- `firestarter_app/CLAUDE.md` — constants sync requirements, WARNING-5 description
- `.planning/PROJECT.md` — v1.11 scope lock, dual-repo branching rules

---
*Architecture research for: Firestarter v1.11 — Complete infoic.xml Decode & Full Memory-Type Coverage*
*Researched: 2026-06-08*

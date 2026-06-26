# Architecture Research — Shared-Primitive Decomposition & Flash Breakdown (v1.16)

**Domain:** Internal architecture rebuild of an Arduino C++ EPROM/Flash/SRAM programmer firmware (PlatformIO, AVR, Leonardo target). Decompose duplicated per-protocol handlers into shared primitives to shrink the Leonardo flash footprint.
**Researched:** 2026-06-25
**Confidence:** HIGH (primitives derived from the actual handler source under `firestarter/src/proms/`; flash breakdown **measured** from the linked `firestarter_leonardo.elf` via `avr-nm --print-size`, not estimated)

> Method note for the flash numbers: the per-handler `.o` files are **LTO/GIMPLE** (`__gnu_lto_slim`), so `avr-size` on the objects reports 0 — real machine code only exists in the final link. All sizes below come from `avr-nm --print-size --size-sort -C .pio/build/leonardo/firestarter_leonardo.elf`, aggregated per family. Whole-image `text+data = 25,430 + 236 = 25,666 B` against Leonardo's 28,672 B usable flash (32 KB − 4 KB Caterina bootloader) = **89.5%**, matching the documented ceiling. Code symbols attributable to the named families total ~9,186 B; the remaining ~16,100 B is USB-CDC/Serial/JSON/CRC/COBS/AVR runtime that this milestone does **not** touch.

---

## Standard (current) Architecture

### System Overview — the handler layer as it exists today

```
┌──────────────────────────────────────────────────────────────────────┐
│  Host (firestarter_app)  build_db.py → chip_database.json → JSON cmd   │
│  algorithm (protocol_id) + vpp_mv + pins + bus-config + flags + cmd    │
└───────────────────────────────┬──────────────────────────────────────┘
                                 │ serial 250000 baud, COBS+CRC8
┌───────────────────────────────▼──────────────────────────────────────┐
│  memory.cpp :: configure_memory()   ── DISPATCH (protocol-first)       │
│   wires handle->firestarter_get/set_data, set_address, *_control_reg   │
│   then branches protocol → configure_<family>()                        │
└───┬───────┬───────┬───────┬───────┬───────┬───────────┬───────────────┘
    │0x07/08│0x0D   │0x06   │0x05/  │0x10   │0x0E/27/   │ !=0 / named     
    │/0B    │       │       │35/39  │       │28/29      │ infeasible      
    ▼       ▼       ▼       ▼       ▼       ▼           ▼                 
 eprom   eeprom_  flash_  flash_  flash_  sram      not_implemented      
 .cpp    28c.cpp  type_3  type_4  intel   .cpp      .cpp                 
 2364 B  842 B    776 B   882 B   1308 B  ~0 B      (shared w/ runtime)  
    │       │       │       │       │                                    
    └───────┴───┬───┴───────┴───────┘                                    
         (each handler sets handle->firestarter_operation_{init,main,end})
┌──────────────────────────────▼───────────────────────────────────────┐
│  SHARED today (already-extracted primitives):                          │
│   flash_utils.cpp  422 B  flash_util_byte_flipping / _get_chip_id /    │
│                            _check_chip_id_execute / fu_flash_data_poll  │
│   memory.cpp       mem_util_blank_check 510 B · mem_util_remap_address  │
│                    _bus 392 B · mem_util_set_address 98 B · memory_     │
│                    get/set_data 304 B · set/get_control_register 54 B   │
│   operation_utils.cpp  INIT→MAIN→END state-machine engine (~1509 B)    │
└────────────────────────────────────────────────────────────────────────┘
```

The dispatch + I/O substrate (`memory.cpp`) and the state-machine engine (`operation_utils.cpp`) are **already** well-factored shared layers. The duplication this milestone targets is concentrated **inside the seven `configure_*` handlers** — specifically the write/verify loops, the VPP-gate check, and the chip-ID compare/report.

### Component Responsibilities (current, as built)

| Component | Responsibility | Already-shared? |
|-----------|----------------|-----------------|
| `memory.cpp::configure_memory` | Protocol-first dispatch; install `get/set_data`, `set_address`, `*_control_register` function pointers (656 B) | Yes — the dispatch spine |
| `mem_util_set_address` / `_calculate_*_register` | Compose LSB/MSB/top-address register bytes from a linear address | Yes — used by every handler via `firestarter_set_address` |
| `mem_util_remap_address_bus` | Apply `bus_config` line-remap + R/W + VPP-line + static-high (392 B) | Yes — called by `memory_get_data`/`memory_set_data` |
| `memory_get_data` / `memory_set_data` | Drive the physical bus for one byte (address→/CE strobe→latch / write pulse) | Yes — the byte-level read/write primitive |
| `mem_util_blank_check` | Stateful 2 KB-chunked 0xFF scan with progress (510 B) | Yes — called by every write-init + erase-end |
| `operation_utils.cpp` | INIT→MAIN→END state machine, ACK/DONE/DATA framing, timeout | Yes — the engine all handlers plug into |
| `flash_utils.cpp` | AMD/JEDEC command byte-flipping, DQ7 data-poll, AMD chip-ID read+compare (422 B) | Yes — shared by flash3 + flash4 + eeprom28c (SDP) |
| `eprom.cpp` (0x07/08/0B) | UV-EPROM: VPP gate, A9-12V chip-ID, mismatch-retry write, erase pulse (2364 B) | **No — biggest duplication source** |
| `flash_intel.cpp` (0x10) | Intel command-register write, status-register poll, VPP gate (1308 B) | **Partially — own VPP + chip-ID copies** |
| `eeprom_28c.cpp` (0x0D) | AT28C SDP-disable, A9-12V chip-ID, 64 B page write + DQ7-style poll (842 B) | **Partially — own chip-ID + wait-loop copies** |
| `flash_type_3.cpp` (0x06) | AMD unlock, sector/chip erase, per-byte write + DQ7 verify (776 B) | Mostly — leans on flash_utils |
| `flash_type_4.cpp` (0x05) | Data-driven page-size write + page-poll, SDP unlock, custom erase (882 B) | Partially — own page-poll copy |
| `sram.cpp` (0x0E/27/28/29) | No-op `configure_sram` (~0 B); rides the generic `memory_*_execute` path | N/A — already maximally shared |
| `not_implemented.cpp` | Fail-closed `0xBB` response, zero side effects | N/A |

---

## Shared-Primitive Inventory (PRIMARY DELIVERABLE)

Each row: the primitive, which handlers duplicate it today (with file:function citations), the **measured** flash it occupies, whether it is genuinely shareable, and a proposed C-style API consistent with the existing `firestarter_handle_t*`-threading convention.

### P1 — Address setup  ✅ ALREADY SHARED (leave as-is)

- **Where:** `memory.cpp:173 mem_util_set_address` + `_calculate_lsb/msb/top_address_register` (149-189), `mem_util_remap_address_bus` (282-305). Every handler reaches the bus only through `handle->firestarter_set_address` / `firestarter_get_data` / `firestarter_set_data`, which already funnel here.
- **Duplicates:** Only `flash_utils.cpp:61 fu_flash_fast_address` re-implements a *faster* 2-register-only address write (skips the top-address/control byte) for AMD command flips. That is a deliberate optimization, not accidental duplication — **keep it**, but document the *why* in the naming pass.
- **Shareable:** Already is. **No action** beyond documentation.
- **Flash:** ~490 B, single copy.

### P2 — Byte-level data strobe (read latch / write pulse)  ✅ ALREADY SHARED

- **Where:** `memory.cpp:201 memory_get_data` (read: address→settling→/CE→strobe→latch) and `memory.cpp:247 memory_set_data` (write: address→data→/CE→`pulse_delay`→/CE off). Installed as `handle->firestarter_get_data/set_data` for all non-flash handlers.
- **Duplicates:** `flash_utils.cpp` has its own `fu_flash_flip_data` (52) + `fu_flash_data_poll` (68) because AMD command-flip timing differs (no `pulse_delay`, explicit data-output toggling). Genuinely protocol-specific — **keep**.
- **Shareable:** Already is for the standard path. **No action.**
- **Flash:** read 190 B + write 114 B, single copy each.

### P3 — VPP gate (read voltage, compare to target window, ERROR/WARN/FORCE)  ⚠️ DUPLICATED — TOP PRIORITY

- **Where + duplicates:**
  - `eprom.cpp:209 eprom_check_vpp` — **532 B**. Contains the voltage-window check **twice** (HIGH branch 229-251, LOW branch 252-270), each with an identical ~16-line `_v0/_v1/_v2/_v3` → `_b[8]` byte-packing block.
  - `flash_intel.cpp:26 flash_intel_check_vpp` — same HIGH/LOW window logic + identical `_b[8]` packing duplicated again (39-80). The byte-packing is byte-for-byte the eprom copy.
  - `eeprom_28c.cpp` — no VPP gate (5V part), but `eeprom28c_check_chip_id` re-packs the same `_b[4]` mismatch bytes (covered under P4).
- **Difference that is real (must parameterize, not delete):** the *regulator-enable bit pattern* differs — eprom uses `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE` (or direct `CTRL_VPP_REGULATOR_ENABLE` for 0x0B/`FLAG_VPE_AS_VPP`), intel uses `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_P1_ENABLE` and asserts it in the *caller* (`flash_intel_write_init`) before calling check. Also the REV0-unsupported guard + the D-11 read/blank-check skip live in `eprom_generic_init`.
- **Shareable:** YES — the measure + window-compare + report + FORCE-downgrade is identical. The regulator routing is the only variable.
- **Proposed API** (new `vpp_gate.{h,cpp}` or fold into `operation_utils`):
  ```c
  /* Reads VPP via rurp_read_voltage_mv() and compares against handle->vpp_mv.
   * Caller has ALREADY asserted the correct regulator/routing bits and delayed.
   * Sets response_code (ERROR over-voltage unless FLAG_FORCE → WARNING;
   * WARNING under-voltage). Emits the shared MSG_*_VPP_{HIGH,LOW} byte frame. */
  void vpp_check_window(firestarter_handle_t* handle, uint16_t measured_mv);

  /* Optional convenience: assert routing, delay, measure, check — used by eprom. */
  void vpp_gate(firestarter_handle_t* handle, rurp_register_t regulator_bits);
  ```
- **Estimated savings:** the byte-packing blocks (~4 copies of ~110 B of packing logic across eprom HIGH/LOW + intel HIGH/LOW) collapse to one. **~350–450 B** recoverable — the single largest concentrated duplication in the codebase.

### P4 — Chip-ID read + compare + report  ⚠️ DUPLICATED ×4 — HIGH PRIORITY

- **Where + duplicates (the compare+report `_b[4]` block appears verbatim 4 times):**
  - `eprom.cpp:306 eprom_internal_check_chip_id` — **260 B** (A9-12V read via `eprom_get_chip_id` 196 + compare/report).
  - `flash_intel.cpp:187 flash_intel_check_chip_id` — **220 B** (0x90 autoselect read + compare/report).
  - `flash_utils.cpp:89 flash_util_check_chip_id_execute` — **192 B** (AMD `FLASH_ENABLE_ID` read + compare/report) — *already shared by flash3+flash4*, proving the pattern factors cleanly.
  - `eeprom_28c.cpp:56 eeprom28c_check_chip_id` — (A9-12V read at `mem_size-64` + compare/report; inside the 414 B `eeprom28c_write_init`).
- **Difference that is real:** only the *read mechanism* differs (A9-12V vs autoselect 0x90 vs AMD unlock vs A9-12V-at-top). The **compare + report** (`if (chip_id != handle->chip_id) { pack _b[4]; FORCE? WARN : ERR; }`) is byte-identical in all four.
- **Shareable:** YES — split into a read function (protocol-specific) + a shared compare/report. `flash_utils` already did exactly this for flash3/flash4; generalize it.
- **Proposed API:**
  ```c
  /* Shared compare + MSG_*_CHIP_ID_MISMATCH report + FORCE downgrade.
   * Callers supply the already-read id. Returns true on match. */
  bool chip_id_report(firestarter_handle_t* handle, uint16_t read_id);

  /* A9-12V read primitive shared by eprom + eeprom28c (read 2 bytes at `base`).
   * Handles regulator + A9 enable/disable. */
  uint16_t chip_id_read_a9_12v(firestarter_handle_t* handle, uint32_t base_addr);
  ```
- **Estimated savings:** collapsing 4 report copies → 1 shared `chip_id_report`, plus merging the two A9-12V readers (`eprom_get_chip_id` + `eeprom28c_check_chip_id`'s read half). **~250–350 B**.

### P5 — Write-with-verify / poll loop  ⚠️ DUPLICATED ×5 — MEDIUM (higher risk)

- **Where + duplicates:**
  - `eprom.cpp:143 eprom_write_execute` — **982 B (largest single function in the firmware)**. Mismatch-bitmask retry loop (`program_mismatched_bytes` + `verify_and_update_mask`, up to `NUMBER_OF_RETRIES=20` with escalating `pulse_delay`).
  - `flash_type_3.cpp:96 flash3_write_execute` — 358 B (per-byte: enable-write cmd → set_data → `flash_util_verify_operation` DQ7).
  - `flash_type_4.cpp:80 flash4_write_execute` — 468 B (page-buffered: SDP-unlock per page → fill → `flash4_wait_for_page_write` poll-until-readback).
  - `eeprom_28c.cpp:119 eeprom28c_write_execute` — 240 B (64 B page → `eeprom28c_wait_for_write` readback poll, 188 B).
  - `flash_intel.cpp:133 flash_intel_write_execute` — 204 B (0x40 setup → data → `flash_intel_poll_sr` status-register, 166 B).
- **Difference that is real:** these are genuinely different *algorithms* (mismatch-retry vs DQ7-toggle vs page-readback-poll vs Intel SR-poll). The **completion-poll-with-timeout-and-error-frame** shape recurs but the success predicate differs per protocol.
- **Shareable:** PARTIALLY. Extract a parameterized **poll primitive** (readback-until-equal-or-timeout with a shared `MSG_ERR_*_TIMEOUT` frame), used by `eeprom28c_wait_for_write` (188 B), `flash4_wait_for_page_write`, and the verify half of `eprom_write_execute`. The *outer* algorithm loops stay protocol-specific.
  ```c
  /* Poll address until get_data()==expected or `attempts` × `step_us` elapses.
   * On timeout, emit a shared timeout frame with addr+expected+observed and set
   * response_code=ERROR. Returns true on match. Folds eeprom28c_wait_for_write
   * + flash4_wait_for_page_write + the readback half of eprom verify. */
  bool poll_readback(firestarter_handle_t* handle, uint32_t address,
                     uint8_t expected, uint16_t attempts, uint16_t step_us);
  ```
- **Estimated savings:** **~200–300 B** (the two `wait_for_write`/`wait_for_page_write` copies + part of eprom verify). Do NOT attempt to merge the outer retry algorithms — that risks behavior change on bench-proven write paths (W27C512, W29C020). Conservative.

### P6 — Page buffer write  ◆ PROTOCOL-SPECIFIC (keep separate, share only the poll)

- **Where:** `eeprom_28c.cpp:119` (fixed 64 B `PAGE_SIZE`) vs `flash_type_4.cpp:80` (data-driven 64/128/256 B via `flash4_page_size`). The page-boundary detection (`(address+1) % PAGE_SIZE == 0`) is structurally identical; the page-*size derivation* and the SDP-unlock-per-page differ.
- **Shareable:** Only the boundary-detect + the poll (P5). The page-fill bodies differ enough that merging them is net-negative on flash and risky. **Keep separate**; share `poll_readback` (P5).

### P7 — SDP unlock sequence  ✅ ALREADY SHARED (consolidate the tables)

- **Where:** `flash_utils.h:24-60` defines `FLASH_ENABLE_ID/DISABLE_ID/ERASE/ENABLE_WRITE` byte-flip tables; `eeprom_28c.cpp:26 EEPROM_SDP_DISABLE` defines its own 6-write `{0x5555,0xAA}...` table; `flash_type_3.cpp:118 flash3_sector_erase` builds a 6-entry table inline. All run through the shared `flash_util_byte_flipping` (`flash_utils.cpp:20`, 180 B).
- **Note:** `FLASH_ENABLE_WRITE` and `FLASH_ENABLE_WRITE_PROTECTION` in `flash_utils.h` are **byte-identical** (both `AA/55/A0`) — dead duplication in the header constant pool. `EEPROM_SDP_DISABLE` == `FLASH_DISABLE_WRITE_PROTECTION` (both `AA/55/80/AA/55/20`) — another duplicate table.
- **Shareable:** The *executor* already is. The **tables** can be deduplicated (remove `FLASH_ENABLE_WRITE_PROTECTION`; point eeprom28c at `FLASH_DISABLE_WRITE_PROTECTION`). These const tables sit in flash; each 6-entry table is ~30 B.
- **Estimated savings:** **~40–80 B** of constant pool, near-zero risk. Good "warm-up" task.

### P8 — Erase  ◆ MOSTLY PROTOCOL-SPECIFIC

- **Where:** `eprom.cpp:274 eprom_internal_erase` (150 B, A9+VPE pulse), `flash_intel.cpp:145 flash_intel_erase_execute` (102 B, 0x20/0xD0 + SR-poll), `flash3_erase_execute` (192 B, chip vs sector AMD unlock), `flash4_erase_execute` (244 B, bespoke CE/OE/WE toggle sequence).
- **Shareable:** Very little — these are 4 distinct silicon erase algorithms. Only the `is_flag_set(FLAG_CAN_ERASE) && !FLAG_SKIP_ERASE` *guard wrapper* in the four `*_write_init` functions repeats (~20 B each). **Low priority**; optionally fold the guard into a shared `write_init_preamble`.

### Primitive inventory summary

| Primitive | Status today | Action | Est. flash saved | Risk |
|-----------|-------------|--------|------------------|------|
| P1 Address setup | ✅ shared | document only | 0 | — |
| P2 Data strobe | ✅ shared | document only | 0 | — |
| **P3 VPP gate** | ⚠️ dup ×2 (×4 packing) | **extract `vpp_check_window`** | **~350–450 B** | Low–Med |
| **P4 Chip-ID compare/report** | ⚠️ dup ×4 | **extract `chip_id_report` + merge A9 readers** | **~250–350 B** | Low |
| P5 Write/poll loop | ⚠️ dup ×5 | extract `poll_readback` only | ~200–300 B | Med |
| P6 Page buffer | ◆ specific | share P5 poll only | (in P5) | Med |
| P7 SDP tables/executor | ✅ executor shared | dedup const tables | ~40–80 B | Very low |
| P8 Erase | ◆ specific | optional guard fold | ~40 B | Low |

**Total realistically recoverable: ~850–1,300 B** (~3–4.5 percentage points of the 28,672 B Leonardo flash). That moves the build from 89.5% to roughly **85–86.5%** — meaningfully off the ~90% ceiling, restoring headroom for future per-protocol fixes without a single new feature.

---

## Per-Handler / Family Flash Breakdown (MEASURED)

From `avr-nm --print-size` on `firestarter_leonardo.elf` (LTO-final machine code — the authoritative numbers):

| Family / module | Bytes | % of 28,672 | Top functions (bytes) |
|-----------------|------:|------------:|------------------------|
| **eprom (0x07/08/0B)** | **2,364** | 8.2% | `eprom_write_execute` **982**, `eprom_check_vpp` **532**, `eprom_internal_check_chip_id` 260, `configure_eprom` 224, `eprom_internal_erase` 150 |
| memory.cpp dispatch + bus + blank-check | 2,592 | 9.0% | `configure_memory` 656, `mem_util_blank_check` 510, `mem_util_remap_address_bus` 392, `memory_verify_execute` 238 |
| operation_utils (state-machine engine) | ~1,509 | 5.3% | `op_get_message` 394, `op_execute_stateful_operation` 196, house-keeping funcs |
| **flash_intel (0x10)** | **1,308** | 4.6% | `flash_intel_write_init` **562** (incl. inlined VPP check), `flash_intel_check_chip_id` 220, `_write_execute` 204, `_poll_sr` 166 |
| **flash_type_4 (0x05/35/39)** | **882** | 3.1% | `flash4_write_execute` 468, `flash4_erase_execute` 244 |
| **eeprom_28c (0x0D)** | **842** | 2.9% | `eeprom28c_write_init` 414, `_write_execute` 240, `_wait_for_write` 188 |
| **flash_type_3 (0x06)** | **776** | 2.7% | `flash3_write_execute` 358, `flash3_erase_execute` 192, `configure_flash3` 104 |
| flash_utils (SHARED) | 422 | 1.5% | `flash_util_check_chip_id_execute` 192, `flash_util_byte_flipping` 180 |
| sram (0x0E/27/28/29) | ~0 | 0% | `configure_sram` no-op (rides generic path) |
| not_implemented | small | — | folds into runtime |
| **Other** (USB-CDC, Serial, JSON, CRC8/COBS, malloc, AVR libgcc, `main`) | ~16,100 | 56% | `main` 4,944, USB vectors, `_process_*_data` — **out of scope** |
| **TOTAL** | **25,666** (text+data) | **89.5%** | |

**Where reuse buys the most headroom (ranked):**
1. **eprom.cpp (2,364 B)** — biggest handler; `eprom_check_vpp` (532) and `eprom_internal_check_chip_id` (260) are pure P3/P4 duplication = ~790 B, of which ~400 B is recoverable.
2. **flash_intel.cpp (1,308 B)** — `flash_intel_write_init` (562) carries an inlined second copy of the VPP-window/byte-pack; `flash_intel_check_chip_id` (220) is a 4th chip-ID copy.
3. **eeprom_28c.cpp (842 B)** — `eeprom28c_check_chip_id` (within the 414 B init) + `_wait_for_write` (188) are P4 + P5 duplicates.

The three handlers carrying VPP and/or chip-ID logic (eprom, flash_intel, eeprom_28c) hold **all** the recoverable duplication. flash3/flash4 already lean on `flash_utils`, so they yield little (P5 poll only).

---

## Recompose Order + Integration Points

Incremental, **one primitive/family at a time**, each landing as its own guarded step. Order chosen for **biggest-saving × lowest-risk × dependency-first**:

### Step 0 — Pin the golden register sequences (no code change)
- Use the existing native recording bus (`test/native/avr/_shared/host_stubs_common.inc` — `clear_bus_recording()`, `recorded_reg(i)`, `recorded_data(i)`) and the per-family `test_val_*` suites (`test_val_eprom`, `test_val_flash_intel`, `test_val_eeprom28c`, `test_val_flash3`, `test_val_flash4`) to capture the **exact control-register + data write sequence** each handler emits today. These golden traces are the recompose oracle: a recomposed handler must reproduce them byte-for-byte.
- **Guard:** `pio test -e native` green before touching anything.

### Step 1 — P7 SDP/const-table dedup (warm-up, ~40–80 B, very-low risk)
- Remove the duplicate `FLASH_ENABLE_WRITE_PROTECTION` table; repoint `eeprom_28c.cpp:EEPROM_SDP_DISABLE` at `FLASH_DISABLE_WRITE_PROTECTION` (`flash_utils.h`). No logic change.
- **Guard:** native `test_val_eeprom28c` + `test_val_flash3` golden traces unchanged; `pio run -e leonardo` size delta recorded.

### Step 2 — P4 chip-ID compare/report (~250–350 B, low risk)
- Add `chip_id_report(handle, read_id)` (generalize `flash_util_check_chip_id_execute`'s compare/report half into a callable). Repoint `eprom_internal_check_chip_id`, `flash_intel_check_chip_id`, `eeprom28c_check_chip_id`, and `flash_util_check_chip_id_execute` to call it. Add `chip_id_read_a9_12v` shared by eprom + eeprom28c.
- **Why early:** lowest behavioral risk (report is pure formatting), and `flash_utils` already proves the split works.
- **Guard:** native traces for all four families; the `MSG_*_CHIP_ID_MISMATCH` frame bytes are pinned by `test_messages` + `test_frame_vectors`.

### Step 3 — P3 VPP gate (~350–450 B, biggest saving, low–med risk)
- Add `vpp_check_window(handle, measured_mv)` carrying the single HIGH/LOW window-compare + the one `_b[8]` packing + FORCE downgrade. Repoint `eprom_check_vpp` and `flash_intel_check_vpp`; each keeps its own regulator-routing assertion + delay, then calls the shared window check.
- **Why here:** highest single saving; depends on Step-2 framing patterns being settled.
- **Guard:** `test_flash_intel_vpp` (already exists) + `test_val_eprom` recording traces; bench re-prove on Leonardo + RURP Rev 2.0 (W27C512 write — exercises the eprom VPP gate live).

### Step 4 — P5 poll primitive (~200–300 B, med risk)
- Add `poll_readback(handle, addr, expected, attempts, step_us)`. Repoint `eeprom28c_wait_for_write`, `flash4_wait_for_page_write`, and the verify-readback half of `eprom_write_execute`. **Leave the outer retry/page algorithms untouched.**
- **Why last of the extractions:** touches bench-proven write paths (W29C020 auto-erase, W27C512); highest behavioral sensitivity.
- **Guard:** native `test_val_flash4` + `test_val_eeprom28c` + `test_val_eprom`; **mandatory bench re-prove** of W29C020 (0x05/flash4), an AT28C-class write (0x0D), and W27C512 (0x07) on Leonardo + Rev 2.0, composing into the v1.16 per-protocol ledger.

### Integration points

| Boundary | What it touches | How guarded |
|----------|-----------------|-------------|
| **Dispatch (`memory.cpp::configure_memory`)** | **Unchanged** through the whole milestone — primitives are leaf helpers below the handlers; dispatch still installs the same `firestarter_operation_*` pointers. | `test_dispatch` (`test_configure_memory.cpp`, one case per `KNOWN_PROTOCOLS` entry) + host `check_dispatch.py` (744-chip resolve, 0 violations, GATE-03 VPP-safety) |
| **Host (`firestarter_app`)** | **Untouched** — primitives are firmware-internal; no wire field changes, no `constants.py`↔`firestarter.h` delta, no `algorithm`/`vpp_mv`/`flags` semantics change. Avoids dual-repo lockstep entirely for the refactor steps. | `diff_db.py` per-chip diff vs pinned baseline must be **empty** (DB regen not invoked); host pytest suite unchanged |
| **Frame/message catalog** | New shared functions must emit the *same* `MSG_*` IDs with the *same* byte layout. | `test_frame_vectors` + `test_messages` golden vectors; `logging_id.h` / `messages.h` IDs unchanged |
| **Native register oracle** | Recomposed handler register/data sequence | `test/native/avr/_shared` recording bus + per-family `test_val_*`; capture-before / assert-after each step |
| **Flash budget** | The whole point | `pio run -e leonardo` size logged per step; STATE notes the running % (target: 89.5% → ≤86.5%) |

**Lockstep note:** because the refactor is leaf-helper extraction with zero wire/constant change, it is **host-untouched** and can ship firmware-only — *unless* a primitive extraction is paired with a behavior fix (then dual-repo lockstep + the py3.12-masks-CI-3.11 ruff/codegen discipline applies, per the seed constraints).

---

## Architectural Patterns (to follow during recompose)

### Pattern 1: Handle-threaded leaf primitive
**What:** Every primitive takes `firestarter_handle_t* handle` first and reaches hardware only via the installed `handle->firestarter_*` function pointers (never raw `rurp_*` unless it is itself the strobe primitive). Matches `flash_util_*` and `mem_util_*` exactly.
**When:** all new P3/P4/P5 functions.
**Trade-off:** the indirect call costs a few bytes per site but is what makes the native recording-bus test possible (stubs swap the pointers) — keep it.

### Pattern 2: Split read-mechanism from compare/report
**What:** protocol-specific *read* (A9-12V vs autoselect vs AMD unlock) stays in the handler; the *compare + MSG frame + FORCE downgrade* is shared. Already demonstrated by `flash_util_check_chip_id_execute` serving flash3+flash4.
**When:** P4, and by analogy P3 (regulator routing in caller, window-compare shared).
**Trade-off:** one extra small function vs ~4 duplicated report blocks — strongly net-positive.

### Pattern 3: Capture-then-recompose (golden register trace)
**What:** before extracting a primitive, record the handler's exact bus sequence in a native `test_val_*` suite; after extraction, assert the sequence is byte-identical.
**When:** every extraction step.
**Trade-off:** upfront test authoring; eliminates the "silent timing/sequence regression" class (the v1.13 flash4 256 B page bug, the v1.15 AM27C020 0-bits-programmed class) from the refactor.

---

## Anti-Patterns (avoid during this rebuild)

### Anti-Pattern 1: "Unify the write loops"
**What people do:** merge `eprom_write_execute` / `flash4_write_execute` / `eeprom28c_write_execute` into one parameterized super-loop.
**Why it's wrong:** they are genuinely different silicon algorithms (mismatch-retry vs page-buffer vs DQ7-toggle); a unified loop grows branchy, often *costs* flash after the branches, and risks the bench-proven write paths. The v1.15 ledger (W29C020, W27C512) is the thing not to break.
**Do instead:** share only the **poll primitive** (P5) and the **report** (P4); keep the outer algorithm per-protocol.

### Anti-Pattern 2: Touching dispatch during the primitive pass
**What people do:** "while I'm here, also reorganize `configure_memory`."
**Why it's wrong:** the seed locks "dispatch structure unchanged through the naming pass; primitives land incrementally after." Dispatch changes are the highest-blast-radius (12V-VPP-hazard class) and would invalidate every `test_dispatch` + `check_dispatch.py` assumption at once.
**Do instead:** dispatch stays line-for-line stable; only leaf helpers move.

### Anti-Pattern 3: Regenerating the DB to "tidy" alongside the refactor
**What people do:** re-run `build_db.py` in the same commit as a primitive extraction.
**Why it's wrong:** mixes a host-data change into a firmware-only refactor, defeats `diff_db.py`'s empty-diff guard, and breaks the "minipro DB stays ground truth, datasheets only verify" locked decision.
**Do instead:** keep DB byte-identical; `diff_db.py` must show zero per-chip change across the whole milestone (except deliberate, separately-gated graduations).

---

## Integration Points (tooling summary)

| Tool / suite | Repo | Role in the recompose |
|--------------|------|------------------------|
| `pio test -e native` + `test_val_*` + `_shared` recording bus | firestarter | Per-family register-level golden oracle (capture before / assert after each step) |
| `pio test -e native -f "*test_dispatch*"` | firestarter | Dispatch-unchanged invariant (one case per KNOWN_PROTOCOLS) |
| `pio run -e leonardo` + `avr-size`/`avr-nm` | firestarter | Per-step flash-delta measurement against the 89.5%→≤86.5% target |
| `tools/check_dispatch.py` | firestarter_app | 744-chip resolve + GATE-03 VPP-safety (host guard authoritative) — must stay 0 violations |
| `tools/diff_db.py` | firestarter_app | Per-chip DB diff vs pinned baseline — must stay empty (DB untouched) |
| `dev validate-family` / `write_test.sh` | firestarter_app | Tier-3 bench re-prove on Leonardo + RURP Rev 2.0, feeding the v1.16 per-protocol ledger (composes with v1.13 matrix + v1.15 EVIDENCE.{md,json}) |

---

## Sources

- `firestarter/src/proms/{eprom,eeprom_28c,flash_intel,flash_type_3,flash_type_4,flash_utils,memory,sram,not_implemented}.cpp` (handler source — read in full) — **HIGH**
- `firestarter/src/operation_utils.cpp`, `src/hardware_operations.cpp`; `include/{firestarter,rurp_pinout,flash_utils,memory_utils,operation_utils}.h` — **HIGH**
- Measured: `avr-nm --print-size --size-sort -C .pio/build/leonardo/firestarter_leonardo.elf` (function-level sizes) + `avr-size` whole-image (25,666 B text+data = 89.5%) — **HIGH (direct measurement of the committed build)**
- `firestarter/test/native/avr/{_shared,test_val_*,test_dispatch}` (existing native register-recording harness) — **HIGH**
- `firestarter_app/tools/{check_dispatch.py,diff_db.py}` (guard gates) — **HIGH**
- `.planning/seeds/protocol-first-architecture-rebuild.md`, `.planning/notes/protocol-rebuild-rationale.md`, `.planning/PROJECT.md` v1.16 section — **HIGH**

---
*Architecture research for: Firestarter v1.16 shared-primitive decomposition*
*Researched: 2026-06-25*

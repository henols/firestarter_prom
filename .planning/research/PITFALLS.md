# Pitfalls in EPROM Programmer Database and Protocol Design

Research findings for the Firestarter protocol-aware programming architecture.
Generated: 2026-05-08

---

## 1. Database and Chip Mapping Mistakes

### 1.1 Wrong VPP Voltage Destroys Chips

VPP voltages in the 27xx family range from 9V to 25V depending on era and manufacturer.
Applying the wrong voltage will permanently damage the die.

Key voltage ranges found in the minipro XML (voltages field, low byte = VPP):

| Code  | Voltage | Typical Chips                        |
|-------|---------|--------------------------------------|
| 0x00  | 12V     | Most modern 27Cxxx EPROMs            |
| 0x70  | 13V     | AMD 27512, some 27256 parts          |
| 0x80  | 13.5V   | Some Atmel 28Cxx EEPROM parts        |
| 0x30  | 10V     | Some 28Cxx EEPROMs                   |
| 0xF0  | 18V     | Old 2716 parts, some 2732            |

The 25V VCC_PROG for the original 2716 (as seen in `pinouts.json`) is extreme and comes
from a dedicated Vpp supply pin, not the regulator chain. If a programmer assumes all
24-pin chips use 12V VPP (the modern default), it will fail to program a 2716 silently
or destroy it if the physical pin is wrongly driven.

**In this codebase:** `parse_db_2.py` decodes VPP from `(voltages & 0xFF)`. The database
does store correct VPP strings (e.g., "13V" for AM27512). The risk is in `database.py`'s
`_map_data()` which silently defaults to `vpp = 0` on parse failure and sends that to the
firmware as `vpp * 1000` millivolts. A 0mV VPP target will cause `eprom_check_vpp()` to
compare against 0 and emit warnings that are easy to miss if `FLAG_FORCE` is set.

### 1.2 Wrong Algorithm for "Similar" Chips (27C256 vs 27256)

The 27256 and 27C256 occupy the same 28-pin package and look identical to a dumb
programmer. However:

- **27256** (no C): NMOS, VPP=12.5V, VCC=6V during programming, slow pulse timing
- **27C256** (CMOS): VPP=12.5V, VCC=5V, different pulse timing, A14 on pin 1 (VPP also on pin 1)
- **27512** (same 28 pins!): VPP migrated from pin 1 to pin 22 (shared with /OE)

In the minipro XML, these are distinguished by the `variant` field:
- `variant == 0x11` (17): 27256-family (VPP on pin 1)
- `variant == 0x10` (16): 27512-family (VPP on pin 22 = /OE pin)
- `variant == 0x13` (19): 2764/27128-family (VPP on pin 1, A13 on pin 26)

**BUG FOUND:** In `parse_db_2.py`, `resolve_pinout_key()` correctly maps:
```python
if variant == 16: return "DIP28_27512"
if variant == 17: return "DIP28_27256"
return "DIP28_2764"  # default covers 2764/27128
```

However, the committed `minipro_complete_db.json` assigns `DIP28_2764` to ALL 28-pin
chips including all 27512 variants (67 chips). The `DIP28_27512` and `DIP28_27256`
pinout keys appear zero times in the current database. This means the database was
regenerated at a point when `resolve_pinout_key()` was not yet correct (or not yet
present), and was never re-regenerated.

**Consequence:** Every 27512-family chip (AM27512, AT27C512, W27C512, 27C512, etc.)
currently gets programmed with the VPP line pointed at pin 1 (A14) instead of pin 22
(/OE). VPP is applied to an address line during programming — this may partially work
(the high-voltage pulse may still reach the chip via its internal protection diodes) but
is architecturally wrong and will fail for any chip that strictly requires VPP on /OE.

### 1.3 Pin Count Heuristics Fail for Edge Cases

The 27512 is the canonical example of why pin-count-alone cannot determine pinout:

- **27256**: 28 pins, VPP on pin 1, A14 on pin 1 (dual-function)
- **27512**: 28 pins, VPP on pin 22 (/OE), pin 1 is A15 (address only), /OE shares VPP
- **2764**: 28 pins, VPP on pin 1, A12 only goes to pin 2 (NC on this), pin 26 is NC or A13

All three are 28-pin DIP, all three have identical physical outline, all three use
EPROM_STD protocol (0x07). The only distinguishing factor in minipro's database is the
`variant` field.

**27512 special case — VPP on /OE (pin 22):**

The JEDEC 27512 standard moved VPP from pin 1 to the /OE pin (pin 22) to make room for
address line A15 on pin 1. Programming sequence:
1. CE low, OE/VPP raised to VPP voltage (12V or 13V)
2. Apply address and data
3. Pulse CE low for programming pulse width (typically 1ms)

If OE/VPP is left at 0V (treated as active /OE), the chip reads instead of programs.
If VPP is applied to pin 1 (A15) instead, A15 floats at 12V — the chip may be damaged
(most EPROM address inputs have ESD protection only, not 12V tolerance) and will certainly
not program correctly.

**In `pinouts.json`:** The `DIP28_27512` entry correctly specifies:
```json
"vpp-pin": [22], "oe-pin": [22]
```
And the `DIP28_2764` entry correctly specifies:
```json
"vpp-pin": [1]
```
The pinout data is correct; the bug is that `minipro_complete_db.json` never assigns
`DIP28_27512` to any chip.

### 1.4 The "Algorithm Leakage" Bug — Unmapped Protocol IDs in the Database

The `parse_db_2.py` script calls `PROTOCOL_MAP.get(proto_id, proto_id)` — if a
protocol ID is not in the map, the **raw integer** is stored as the algorithm value.
The current database contains entries with `"algorithm": 4` (raw integer, not a string),
corresponding to protocol 0x04 which is not in `PROTOCOL_MAP`. AT45Dxxx dataflash chips
from ADESTO/Atmel have protocol 0x04 and all land in the database with a numeric algorithm
value.

In `database.py`, `_map_data()` iterates `PROTOCOL_MAP` items to reverse-lookup
`protocol_id` from the string, but when the algorithm field is already an integer (not
a string), `v == programming.get("algorithm")` always fails, so `protocol_id` stays 0.
The firmware receives `type=1` (default EPROM) and will attempt to UV-EPROM-program a
dataflash chip.

---

## 2. Protocol Ambiguities in minipro's Database

### 2.1 The `variant` Field Meaning

In minipro's `infoic.xml`, `variant` is a multi-purpose field encoding:
- **Physical pinout** (which DIP variant): bits that distinguish 27256 from 27512
- **Programming sub-variant** within a chip family
- **PLCC/SMD indicator** in combination with `package_details`

For 28-pin EPROM chips, the semantically significant values are:
- `0x10` = 27512 pinout (VPP on /OE, pin 22)
- `0x11` = 27256 pinout (VPP on pin 1, A14 shared)
- `0x13` = 2764/27128 pinout (VPP on pin 1, A13 on pin 26)
- `0x26` = 28Cxx EEPROM pinout (byte-write capable, different WE handling)

For the PLCC32 package variants, the same chip (e.g., AT27C512@PLCC32) uses
`variant=0x03` — different from the DIP28 version's `variant=0x10`. The variant field
changes meaning based on the package. Since Firestarter filters out PLCC/SMD chips
during database generation, this does not cause runtime errors, but it means you cannot
compare variant values across package types.

### 2.2 Known Quirks in `infoic.xml` Data

**Duplicate chip entries:** The same chip appears multiple times under different
manufacturers (minipro tracks per-manufacturer). The `parse_db_2.py` deduplication
only prevents identical `(name, chip_id)` pairs within a single manufacturer.
Across manufacturers, duplicates are expected and acceptable.

**`chip_id_value` of `0x00000000`:** Many chips that do not support chip ID reading have
`chip_id_value` of `0x00000000`. The `parse_db_2.py` code stores this verbatim, but
`database.py`'s `_map_data()` only adds `chip-id` to the output if the value is truthy.
`0x00000000` converts to integer 0, which is falsy — so it is correctly omitted.
However, `chip_id_check: false` with a non-zero chip_id_value would be ambiguous; in
practice this combination does not appear in the filtered dataset.

**Protocol 0x04 (FLASH_FWH) and others not in `PROTOCOL_MAP`:** `parse_db_2.py` has
`PROTOCOL_MAP` entries for 18 protocols, but minipro uses more. The fallback
`PROTOCOL_MAP.get(proto_id, proto_id)` stores raw integers for unmapped protocols.
Affected protocols found in the 24-32 pin DIP filtered set include `0x04` (several
AT45Dxxx dataflash parts) and potentially `0x34` / `0x3C` for large flash variants.

**The two `infoic.xml` files:** The `tools/` directory contains both `infoic.xml` and
`infoic2.xml`. `parse_db_2.py` fetches from the network (GitLab). The local XML files
may be stale. The two files have different chip counts, suggesting different minipro
versions. If the DB was generated from `infoic2.xml` (older) rather than the current
GitLab version, entries may have different protocol_ids.

### 2.3 Protocol ID Stability Across minipro Versions

The minipro project on GitLab updates `infoic.xml` when new chips are added or bugs
are fixed. Protocol IDs are generally stable (they encode the hardware algorithm number
in the TL866 programmer's firmware), but chip-specific parameters like `voltages`,
`pulse_delay`, and `flags` do change as contributors correct errors. The `variant` field
for a given chip has been observed to change between minipro versions when the programmer
team corrects pinout misassignments.

**Implication:** The committed `minipro_complete_db.json` is a snapshot. Re-generating
it from a newer `infoic.xml` may change VPP voltages, pinout assignments, or chip IDs
for a subset of chips. The database pipeline must be treated as a build artifact with a
known source revision, not as a static file.

---

## 3. Arduino/Embedded Firmware Pitfalls

### 3.1 Serial Buffer Overflow During Data Transfer

The ATmega328P (Uno) hardware UART receive buffer is 64 bytes. At 250000 baud, a
64-byte buffer fills in ~2.05ms. The Arduino HardwareSerial library uses a 64-byte
ring buffer by default (configurable via `SERIAL_RX_BUFFER_SIZE` in `HardwareSerial.h`).

The current firmware uses a "pull" protocol: the Arduino signals readiness before the
host sends each chunk. This avoids overflow because the Arduino explicitly requests data
(`OK` signal) only when the previous chunk is processed. The host must not send data
until it receives `OK`. If the host sends data without waiting for the `OK` response
(e.g., race condition on the Python side), the UART buffer will overflow and bytes will
be silently dropped.

The firmware reads a full JSON command in one shot via `rurp_communication_read_bytes()`.
The JSON command must fit within `DATA_BUFFER_SIZE` (512 bytes for Uno, 1024 for
Leonardo). If a future `algorithm` field is added to the JSON command, ensure the total
JSON size stays within this limit. A JSON command including bus-config (array of 20
integers) is approximately 200-250 bytes.

### 3.2 Timing Issues with VPP Ramp-Up

The firmware uses `delay()` calls (blocking millisecond delays) to wait for VPP to
stabilize. Key delays found in the code:

- `delay(500)` after enabling REGULATOR for write (in `eprom_write_execute`)
- `delay(100)` after enabling REGULATOR for VPP check
- `delay(50)` after enabling REGULATOR for chip ID read
- `delay(10)` before programming pulses

The 500ms wait in `eprom_write_execute` is triggered each time the regulator is first
enabled within a write session. If VPP does not actually reach the target voltage within
500ms (due to capacitor sizing, resistor network calibration, or cold conditions), the
first programming pulse will occur at sub-nominal VPP, which may cause the byte to
program incorrectly but pass the immediate readback verify (since the verify also happens
at low VPP). The chip may fail to read back correctly later at normal VCC.

The `eprom_check_vpp()` function validates VPP before writing, which is the correct
mitigation, but only if the chip has a `chip_id > 0` (which gates the vpp check in
`eprom_generic_init()`). For chips without chip ID support, VPP is never validated
before the first write.

**VPE vs VPP path:** The firmware distinguishes two hardware paths:
- `REGULATOR | VPE_TO_VPP`: enables regulator and routes it through the R1/R2 resistor
  divider down to VPP (normal path for most EPROMs)
- `REGULATOR` alone (FLAG_VPE_AS_VPP): routes regulator output directly as VPP
  (higher voltage, for chips needing VPE-level programming)

Wrong selection of this flag causes either under-voltage (programming fails, chip
survives) or over-voltage (chip damaged). Currently this flag is set manually by the
caller; with the new `algorithm` field, it should be derived deterministically from the
protocol.

### 3.3 Checksum/Verification Approaches That Give False Positives

The current wire protocol uses XOR checksum for data blocks:
```python
checksum = functools.reduce(operator.xor, data_chunk, 0)
```

XOR checksum has well-known weaknesses:
- Any even number of identical bit-flip errors in the same bit position cancel out
- Byte-swap errors between adjacent bytes of the same value are undetected
- All-zero payloads produce checksum 0; an all-zero block with a dropped header byte
  would still match checksum 0

For EPROM programming, a more serious false-positive scenario: during verify, the
firmware reads back each byte individually at `READ_FLAG` voltage. If the bus is
floating (chip not seated, or wrong pin mapping), the data lines may read back all-0xFF
(pulled high) or all-0x00 (pulled low). A file of all-0xFF bytes would pass verify
against a floating bus. The current code does not detect this condition.

The `mem_util_blank_check()` function catches the all-0xFF case for blank chips, but
for a written chip, a floating read would produce incorrect data that only matches the
input file if the input file itself is all-0xFF or all-0x00 by coincidence.

**Practical mitigation**: The chip ID check (when available) provides early detection
of "chip not responding correctly" before programming begins.

### 3.4 Memory Constraints on ATmega328P Affecting Algorithm Complexity

The ATmega328P has:
- 32KB flash (program memory)
- 2KB SRAM
- 1KB EEPROM (used for calibration config)

The firmware uses 512 bytes for `data_buffer` (inside `firestarter_handle_t`),
96 bytes for `response_msg`, and overhead for stack and other structs. At 250000 baud,
the stack depth during JSON parsing with jsmn tokens adds approximately 20 × 8 bytes
= 160 bytes for the token array (`NUMBER_JSNM_TOKENS` tokens × sizeof(jsmntok_t)).

Adding a new `algorithm` dispatch table that covers all EPROM/Flash/EEPROM variants
(8+ algorithm implementations) will add to flash. Each `configure_*()` function
currently fits in flash, but if Intel-style sector erase loops, AMD sector sequences,
and EEPROM poll loops are all added, the combined flash usage may approach the 32KB
limit, especially if debug strings (in PROGMEM) are numerous.

Key constraint: the `mismatch_bitmask` in `eprom_write_execute` is allocated on the
stack:
```c
uint8_t mismatch_bitmask[DATA_BUFFER_SIZE / 8];  // 64 bytes on stack
```
Adding similar per-algorithm retry tracking arrays for flash algorithms would further
consume stack. SRAM fragmentation from `malloc()` calls (used in blank check progress)
is also a concern — the ATmega does not have an MMU and heap fragmentation can cause
silent `malloc()` failures that return NULL.

---

## 4. Wire Protocol Design Pitfalls

### 4.1 JSON Parsing Overhead on 8-Bit Microcontroller

The firmware uses `jsmn` (a minimal JSON tokenizer) with a static token array. The
current `json_parse()` function allocates `tokens[NUMBER_JSNM_TOKENS]` as a static
local (in `firestarter.cpp`'s `parse_json()`), which means it occupies SRAM for the
lifetime of the program.

The parse loop in `json_parse()` is O(N × K) where N is the number of JSON fields and
K is the number of registered key parsers. Currently K=8 (key_parsers array). Adding
`algorithm` as a new field raises K to 9, which is negligible.

However, the key comparison uses `strncmp_P` against PROGMEM strings for each field in
the dispatch table. If an unknown field is received (not in the table and not
`bus-config`, `cmd`, or `state`), the firmware emits an error and returns -1, aborting
the command. This is a **backward compatibility break**: if the Python host sends a new
field (e.g., `"algorithm": 7`) to an older firmware that doesn't recognize it, the
firmware will refuse the command entirely with "Unknown field: algorithm".

**Mitigation design**: Either:
(a) Make the firmware silently skip unknown fields (change `return -1` to `token_idx += 2; continue`)
(b) Version-gate: check firmware version before sending new fields
(c) Send `algorithm` as part of `flags` or encode it into an existing field

Option (b) is already partially implemented — `serial_comm.py` checks for firmware
version >= 2.0.0. But if `algorithm` requires a minor version bump (e.g., 2.1.0), the
version check logic must be updated in `_is_version_sufficient()`.

### 4.2 Field Naming Conflicts When Extending the Protocol

The current JSON command fields:
- `cmd` / `state` (both accepted for command code)
- `memory-size`, `address`, `flags`, `chip-id`, `pin-count`, `pulse-delay`, `vpp`, `type`
- `bus-config` (nested object with `bus`, `rw-pin`, `vpp-pin`)

Risks when adding `algorithm`:
- `"type"` already carries the memory type (1=EPROM, 2=Flash2, 3=Flash3, 4=SRAM,
  5=Flash4). If `algorithm` replaces `type`, any firmware not updated will interpret the
  absence of `type` as mem_type=0 (uninitialized). The `configure_memory()` switch
  falls through to `firestarter_error_response_format("Memory type 0x%02x not supported")`
  for type=0, which is a safe failure mode.
- The field name `algorithm` is 9 characters. The `jsoneq_` function uses `strlen_P`
  on the PROGMEM key string. This is fine but adds 9 bytes to PROGMEM per key string.
- Both `cmd` and `state` are accepted for backward compatibility. If a similar dual-name
  pattern is used for `algorithm` (e.g., also accepting `proto`), the key_parsers array
  grows and the parse loop gets proportionally slower.

**The `flags` field collision risk:** Bits 0-7 of `ctrl_flags` (uint32_t) are already
defined: FORCE=0x01, CAN_ERASE=0x02, SKIP_ERASE=0x04, SKIP_BLANK_CHECK=0x08,
VPE_AS_VPP=0x10, OUTPUT_ENABLE=0x20, CHIP_ENABLE=0x40, VERBOSE=0x80. If future
algorithm variants need per-algorithm sub-flags, they must not collide with these. Bits
8-31 of `ctrl_flags` are currently unused in the firmware and could carry algorithm-
specific parameters, but this encoding is opaque and fragile.

### 4.3 Backward Compatibility Concerns When Adding New Fields

The Python host builds the command dict from `eprom_data["type"]` and sends it to the
firmware. Adding `algorithm` as a new top-level field creates two compatibility axes:

**Old Python + New Firmware**: The new firmware does not receive `algorithm`; it falls
back to `type`-based dispatch. This is safe if `type` is still sent.

**New Python + Old Firmware**: The old firmware receives `algorithm` as an unknown field
and rejects the command with "Unknown field: algorithm". The user sees a confusing error
that looks like a hardware problem.

The safest transition path:
1. Send both `type` (for old firmware) and `algorithm` (for new firmware) in the
   same command
2. New firmware parser: prefer `algorithm` if present, fall back to `type` if not
3. Old firmware parser: silently skip unknown fields (requires firmware change first)
4. After old firmware is obsolete (>=1 major version), remove `type`

**Serial framing vulnerability**: The firmware scans for `{` as the start of a JSON
frame. If a new field value contains `{` (e.g., a string value like `"algorithm":
"FLASH_AMD_STD"`), the framing code will not be confused because it only triggers on
the initial idle state scan (`rurp_communication_peak() == '{'`). String values inside
a valid command cannot trigger re-entry. However, if communication is interrupted
mid-command (timeout), the firmware discards the command and returns to IDLE. The next
`{` it sees after partial data could be the opening of a nested object within the
partially-received command, causing a malformed parse. The 10ms timeout guard in
`rurp_communication_read_bytes()` mitigates this by abandoning reads that stall.

---

## 5. Summary of Critical Bugs Found in This Codebase

| # | Location | Bug | Impact |
|---|----------|-----|--------|
| 1 | `minipro_complete_db.json` | All 27512-family chips assigned `DIP28_2764` instead of `DIP28_27512` | VPP applied to A15 (pin 1) instead of /OE (pin 22) — wrong pin for every 27512 chip |
| 2 | `minipro_complete_db.json` | All 27256-family chips assigned `DIP28_2764` instead of `DIP28_27256` | Same VPP mismapping; 27256 VPP is also on pin 1 so effect is less severe but address bus is wrong |
| 3 | `minipro_complete_db.json` | `algorithm` field contains raw integers (e.g., `4`, `10`, `52`) for unmapped protocol IDs | `database.py` reverse-lookup fails; `protocol-id` stays 0; chips get wrong programming type |
| 4 | `database.py` `_map_data()` | `determined_type` only maps Flash and SRAM; EEPROM chips get type=1 (UV-EPROM) | 28Cxx/28C64 EEPROM chips would be programmed with UV-EPROM pulse algorithm, not byte-write |
| 5 | `json_parser.c` `json_parse()` | Unknown JSON fields cause hard error + command rejection | Adding `algorithm` field to Python will silently break all older firmware installs |
| 6 | `database.py` `convert_to_programmer()` | `algorithm` / `protocol-id` is never included in the programmer command dict | The entire purpose of the protocol pipeline is not yet wired to the output |


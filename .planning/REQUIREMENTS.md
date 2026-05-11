# Requirements

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Scope:** v1

---

## v1 Requirements

### Database Pipeline (XML → JSON)

**REQ-DB-01:** `parse_db_2.py` preserves minipro `protocol_id` as an explicit `algorithm` integer field in every chip entry in `minipro_complete_db.json`. No guessing or re-derivation.

**REQ-DB-02:** `resolve_pinout_key()` maps `variant` correctly to `DIP28_27512` (variant=0x10), `DIP28_27256` (variant=0x11), and `DIP28_2764` (variant=0x13) — not all 28-pin chips to `DIP28_2764`.

**REQ-DB-03:** VPP voltage is decoded from the `voltages` field low byte using the lookup table and stored in the database entry. Silent `vpp=0` default is eliminated.

**REQ-DB-04:** `parse_db_2.py` warns and skips any chip entry whose `protocol_id` is not in the known mapping table, rather than storing a raw integer that breaks firmware dispatch.

**REQ-DB-05:** The database build pipeline is a single canonical tool named `build_db.py`. The upstream `infoic.xml` is fetched from `https://gitlab.com/DavidGriffith/minipro/` at run time and is never stored or committed in this repository. The legacy `parse_db.py` and its inputs/outputs (`infoic.xml`, `infoic2.xml`, `verified.txt`, `database_generated.json`, `pin-maps.json`) are removed.

---

### Serial Protocol / Wire Format

**REQ-SER-01:** The JSON command sent over serial includes an explicit `algorithm` integer field carrying the minipro `protocol_id` value. This replaces the lossy `type` enum as the primary dispatch key.

**REQ-SER-02:** Firmware JSON parser silently skips unknown field names instead of returning an error, enabling forward-compatible deployment of new fields.

---

### Firmware Algorithm Implementations

**REQ-FW-01:** Firmware dispatches on the `algorithm` field and executes the correct programming pulse width and VPP routing for each UV-EPROM protocol:
- `EPROM_STD` (0x07): 1ms intelligent programming pulse, VPE_TO_VPP, 12.5–13V
- `EPROM_QUICK` (0x08): 100µs pulse, VPE_TO_VPP, 32-pin address bus
- `EPROM_LEGACY` (0x0B): 500µs pulse, direct VPE_ENABLE path, 9–25V VPP range, 24-pin

**REQ-FW-02:** New `configure_flash_intel()` firmware handler for `FLASH_INTEL` (0x10): command-register architecture (0x40 program, 0x20+0xD0 erase, 0x70 status poll, 0xFF reset), mandatory 12V VPP on pin 1.

**REQ-FW-03:** `EEPROM_POLL` (0x0D) uses a DQ7 data-polling loop to detect internal write completion for AT28C010/040 page writes. SDP (Software Data Protection) disable sequence applied before first write for AT28C256.

**REQ-FW-04:** `FLASH_AMD_ALT` (0x06) supports sector erase via the standard unlock sequence with command byte `0x30` written to the sector address, in addition to chip erase.

---

### Verification & Safety

**REQ-SAF-01:** VPP voltage is checked via ADC feedback before the first write pulse for every chip — not gated on `chip_id > 0`.

**REQ-SAF-02:** Chip ID is read and validated before write for any algorithm that supports electronic ID (`flags & MP_ID_MASK`). Mismatch aborts the operation.

**REQ-SAF-03:** A blank check is performed before any Flash or EEPROM write operation. Non-blank detection returns an error prompting the user to erase first.

---

---

### User Experience & Hardware Guidance

**REQ-UX-01:** `firestarter search` and `firestarter info` must clearly distinguish chips without a valid bus-config (unknown or missing pinout key) with a visible warning, rather than silently returning incomplete data that causes confusing hardware failures.

**REQ-UX-02:** `firestarter info --adapter` displays the full physical DIP pin → RURP signal mapping table for the chip's pinout variant, derived from `pinouts.json`. This enables users to determine whether a chip can be inserted directly or requires a wiring adapter, and to derive the exact remap wiring if an adapter is needed.

---

### Address Bus Correctness

**REQ-FW-05:** Address bus lines that must be driven to a fixed HIGH state (second chip-enable pins, JEDEC-required tied-high NC pins, hardware quirk lines) are specified in `pinouts.json` as `static-high-pins` and transmitted in bus-config JSON as `static-high`. Firmware applies them via `static_high_mask` in `bus_config_t` unconditionally on every address write. No hardcoded pin-count conditions.

**REQ-FW-06:** The dead compile-time comparison `READ_WRITE == WRITE_FLAG` in `mem_util_calculate_top_address_register` is removed. The VPE_TO_VPP/A16 sharing constraint is expressed as `if (handle->pins < 32)` with a comment naming the hardware reason.

---

## v2 (Deferred)

- Backward-compat dual `type` + `algorithm` fields in wire protocol during firmware transition
- Version-gate `algorithm` field via firmware semver check in `serial_comm.py`
- Warn on chip ID read returning `0x0000` or `0xFFFF` (floating bus indicator)
- Pin `infoic.xml` source revision as metadata field in generated database
- Cross-manufacturer deduplication to reduce database size

---

## Out of Scope

- Serial interface protocols (I2C, SPI, Microwire) — different hardware interface, not supported by RURP parallel bus
- MCU/MPU types — microcontroller programming is outside scope
- SMD, PLCC, SOIC packages — no RURP socket support
- Binary wire format replacing JSON — overhead is trivial for one-per-operation command
- Full-image CRC32 checksums — per-chunk XOR is sufficient for local USB/serial
- 6.5V VCC NMOS programming — RURP fixed 5V VCC; CMOS variants cover all in-scope chips

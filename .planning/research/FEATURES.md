# Feature Categories for Requirements

## Database Pipeline (XML → JSON)

### Table Stakes (must have)
- Preserve `protocol_id` through `parse_db_2.py` into `minipro_complete_db.json` as an explicit `algorithm` string field — the core fix; `type`-based guessing is the root cause of every dispatch bug
- Resolve `variant` field to correct `pinout_key` (`DIP28_27512` / `DIP28_27256` / `DIP28_2764`) — currently ALL 28-pin chips land on `DIP28_2764`, misrouting VPP to A15 on every 27512
- Decode VPP voltage from `voltages` field low byte and store in millivolts — silent `vpp=0` default in `_map_data()` bypasses the pre-write VPP check for chips without chip IDs
- Reject / warn on unmapped protocol IDs instead of storing raw integers — raw integers in `algorithm` break the `database.py` reverse-lookup and cause wrong `mem_type` (currently affects AT45D dataflash entries leaking into the set)
- Filter to DIP 24/28/32 packages only — non-DIP packages (PLCC, SOIC, TSOP) are not supported by the RURP socket and must not appear in the output

### Differentiators (adds value)
- Pin `infoic.xml` source revision in the generated database as a metadata field — the database is a build artifact; version drift causes silent parameter changes (VPP, pulse_delay, flags)
- Deduplicate cross-manufacturer identical chips to reduce database size — the current per-manufacturer duplication inflates the JSON without adding programming value

### Out of Scope
- Support for serial protocols (I2C `0x01`, SPI `0x03`, Microwire `0x02`) — these require a fundamentally different hardware interface than the RURP parallel bus
- Support for MCU types (`0x12`) — microcontroller programming requires target-specific protocols well outside this scope

---

## Serial Protocol / Wire Format

### Table Stakes (must have)
- Add `algorithm` as an explicit integer field in the JSON command, carrying the `protocol_id` value — replaces the lossy `type` enum that collapses seven distinct algorithms into four buckets
- Send both `type` (for backward compat) and `algorithm` (for new firmware) in the same command during transition — new Python + old firmware currently results in "Unknown field" hard rejection
- Make firmware JSON parser silently skip unknown fields instead of aborting — required before any new field can safely be deployed to mixed firmware environments (change `return -1` to `continue` for unrecognized keys)
- Keep bus-config address array in the wire command — per-command pinout delivery allows the single firmware image to support any physical DIP layout without a firmware-side table
- Preserve pull-model data flow (firmware requests chunks via `OK`) — eliminates UART buffer overflow risk on the ATmega's 64-byte hardware FIFO at 250000 baud

### Differentiators (adds value)
- Version-gate new fields via firmware semver check already present in `serial_comm.py` — prevents sending `algorithm` to firmware that predates the field
- Encode `FLAG_VPE_AS_VPP` deterministically from `protocol_id` on the host rather than requiring manual flag setting — removes a fragile caller responsibility that causes over/under voltage if misconfigured

### Out of Scope
- Binary wire format replacing JSON — JSON overhead is ~200–250 bytes paid once per operation, not per byte; the complexity cost of re-parsing a binary format is not justified
- Hardware flow control (RTS/CTS) — the pull protocol already provides software flow control adequate for the target baud rate

---

## Firmware Algorithm Implementations

### Table Stakes (must have)
- `configure_eprom()` dispatching on `algorithm` for EPROM_STD (`0x07`), EPROM_QUICK (`0x08`), and EPROM_LEGACY (`0x0B`) — all three currently collapse to `type=1`; 50 ms / 100 µs / 50 ms pulse widths are not interchangeable
- Correct VPP routing per algorithm: `VPE_TO_VPP` for 27xx EPROMs, `VPE_ENABLE` direct for EPROM_LEGACY chips requiring up to 18V — wrong path selection causes under-voltage (silent fail) or over-voltage (chip damage)
- `configure_flash3()` for FLASH_AMD_ALT (`0x06`) — already implemented; must remain the reference for the 3-byte unlock + DQ7 poll algorithm (AM29F, SST39SF families)
- New `configure_flash_intel()` handler for FLASH_INTEL (`0x10`) — command-register architecture (0x40 program / 0x20+0xD0 erase / 0x70 status / 0xFF reset) is incompatible with the current eprom pulse path; 12V VPP mandatory on pin 1
- DQ7/toggle-bit polling loop for EEPROM_POLL (`0x0D`) — AT28C010/040 internal write timer is self-timed; the current `pulse_delay`-based timeout is insufficiently precise for 128-byte page writes
- A9_VPP_ENABLE chip-ID read path for 27Cxxx EPROM families — required to validate chip presence before first write pulse for chips without SDP

### Differentiators (adds value)
- SDP (Software Data Protection) disable sequence for EEPROM_POLL chips before page write — AT28C256 ships with SDP enabled from factory; omitting this causes silent write failures
- Sector erase support for FLASH_AMD_ALT — chip erase works but sector erase is faster for partial updates; same unlock sequence with `0x30` to sector address
- Pre-program-all-zeros before Intel chip erase — AM28F010/020 require all bytes written to 0x00 before bulk erase; skipping this leaves bits in an indeterminate state

### Out of Scope
- FLASH_AMD_STD page-write handler (`0x05`, AT29C/SST29EE) — these chips are currently filtered from the database; addressing the filter is a prerequisite; deferred to a follow-on
- FLASH_INTEL_ALT (`0x39`, AT49F) — filtered from database; AMD-compatible unlock sequence means `configure_flash3()` could cover it with a VPP variation, but no chips are currently in scope
- SRAM write path changes — `configure_sram()` is correct for its use case; SRAM has no programming algorithm complexity
- 6.5V VCC programming voltage for NMOS 27xx — RURP operates at fixed 5V VCC; CMOS variants of all target chips tolerate 5V, and the oldest NMOS-only parts are out of scope

---

## Pinout / Physical Mapping Layer

### Table Stakes (must have)
- Regenerate `minipro_complete_db.json` after fixing `resolve_pinout_key()` so `DIP28_27512` and `DIP28_27256` are actually assigned — the fix exists in `parse_db_2.py` but the committed JSON was never rebuilt with it
- `DIP28_27512` pinout: `vpp-pin: [22]`, `oe-pin: [22]` — VPP on /OE pin is mandatory for the 27512; applying VPP to pin 1 (A15) risks address-input damage
- `DIP28_27256` pinout: `vpp-pin: [1]` — correct and distinct from 27512; must be explicitly assigned via `variant=0x11` lookup
- `DIP24_2716` and `DIP24_2732` remain as separate pinout entries — the 2732 shares VPP and OE on pin 20 (mux), while the 2716 has a dedicated pin 21; this difference must survive in the pinout layer
- A13 tie to VCC in 24-pin mode via MSB register bit 5 — hardware behavior; firmware must not attempt to drive A13 as an address line for 24-pin chips

### Differentiators (adds value)
- Validate that `vpp-pin` and `oe-pin` do not conflict in the bus-config before sending — would catch the class of 27512/27256 VPP mis-routing bug at Python time rather than silently at the chip

### Out of Scope
- PLCC32 adapter pinout support — no PLCC physical socket on the RURP; all PLCC-package chips are filtered during database generation
- Auto-detect of DIP size from socket sensing — RURP Rev 2 routes VCC/address automatically by `pin-count`; no additional firmware work needed

---

## Verification & Safety

### Table Stakes (must have)
- VPP pre-write check via ADC feedback for all chips, not only those with chip IDs — current `eprom_check_vpp()` is gated on `chip_id > 0`; chips without readable IDs currently skip voltage validation before the first pulse
- Chip ID read before write (when supported by the algorithm) — provides early "chip not responding" detection that prevents programming a wrong or absent chip; particularly important given the VPP pin-routing bugs
- Blank check before write for Flash/EEPROM — Flash and EEPROM cannot overwrite `0→1` at the bit level without erase; attempting to do so silently leaves incorrectly-set bits
- Post-write read-back verify against source data — XOR checksum is insufficient (even-error cancellation); byte-by-byte comparison catches floating bus and marginal-cell failures

### Differentiators (adds value)
- Warn (not fail) when chip ID read returns 0x0000 / 0xFFFF — these values indicate a floating bus or absent chip and should surface before a 10-minute write session begins
- Report status-register error bits for FLASH_INTEL after each program/erase operation — bit 4 (VPP out of range) and bit 5 (program error) give actionable diagnostics that DQ7 polling cannot provide
- Surface `pulse_delay=0` warning for EPROM_LEGACY chips — the current database parser sets `pulse-delay: 0` for the new DB format; a 0µs pulse will not program any 2716/2732

### Out of Scope
- CRC32 or SHA checksum of the full image over the wire — the pull-model chunk protocol with per-chunk XOR already provides sufficient corruption detection for a local USB/serial link; full-image hashing adds latency for no practical gain in this context
- Write-protect hardware enforcement (WP pin hold) — the RURP does not have a dedicated WP-hold driver; software SDP disable is the correct approach for 28Cxx chips

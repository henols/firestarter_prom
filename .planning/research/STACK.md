# STACK — Authoritative infoic.xml Field Dictionary + minipro Source Map

**Project:** Firestarter v1.11 — Complete infoic.xml Decode & Full Memory-Type Coverage
**Researched:** 2026-06-08
**Scope:** Field-level decode reference for re-deriving `build_db.py` from minipro source. NOT a library list — the "stack" here is the infoic.xml schema + the minipro C source that consumes it.
**Confidence:** HIGH (every field cross-checked against minipro source)

Primary source: `/tmp/minipro` (cloned from `https://gitlab.com/DavidGriffith/minipro.git`), chiefly `src/database.c` `load_mem_device()` (~lines 574–806), constants `database.c` 40–75, `database.h`, `minipro.h`. All findings CONFIRMED from source unless marked INFERRED / UNKNOWN.

---

## `<ic>` Attribute Dictionary

### `name` (string)
CONFIRMED. Comma-separated alias list; each alias may carry an `@PACKAGE` suffix (display-only, not decoded). Canonical name = first entry before first comma. build_db.py splits on comma, strips `@`-suffix per piece, dedupes, rejoins — correct.

### `type` (uint32 hex) — `device->chip_type`
CONFIRMED. `database.c:583`. Constants in `minipro.h`.

| Value | Constant | Meaning |
|-------|----------|---------|
| 0x01 | MP_MEMORY | ROM/EPROM/Flash/EEPROM (parallel memory) |
| 0x02 | MP_MCU | Microcontroller |
| 0x03 | MP_PLD | Programmable logic device |
| 0x04 | MP_SRAM | SRAM / NVRAM / FRAM |
| 0x05 | MP_LOGIC | Logic IC (uses logicic.xml) |

build_db.py filters `type in [1,4]` — correct for scope.

### `package_details` (uint32 hex) — `package_details_t`
CONFIRMED. `database.c:618–703`.
```
Bit  31     SMD_FLAG          (0x80000000) surface-mount
Bits 29-24  PIN_COUNT_MASK    (0x3f000000)>>24 raw pin count (pre-PLCC remap)
Bits 15-8   ICSP_MASK         (0x0000ff00)>>8  in-circuit serial index
Bits 7-0    ADAPTER_MASK      (0x000000ff)     adapter type; 0x00 = DIP native
```
PLCC remap (`get_pin_count()` ~406–420): ADAPTER 0x38→20, 0x3E→28, 0x3F→32, 0x3D→44, else raw nibble. `plcc = PIN_COUNT(pkg) > 0x30`.

build_db.py uses `(pkg & 0x7F000000)>>24` (7-bit vs source 6-bit `0x3f000000`) — harmless for DIP (bit30 always 0). `is_smd` correct. `is_serial = (pkg & 0xFF00)>>8` correctly excludes ICSP-only parts.

### `protocol_id` (uint8 hex) — `database.c:685`; `IC2_ALG_*` in `database.h`
CONFIRMED. Catalog reachable through the INFOIC2PLUS DIP-24..32 parallel filter:

| protocol_id | IC2_ALG_* | build_db label | Description |
|------|------|------|------|
| 0x05 | IC2_ALG_F29EE | FLASH_AMD_STD | AMD/Fujitsu 5V flash (Am29F) |
| 0x06 | IC2_ALG_W29F32P | FLASH_AMD_ALT | Winbond/SST 5V flash (29F alt) |
| 0x07 | IC2_ALG_ROM28P_1 | EPROM_STD | 28-pin ROM/EPROM type 1 — UV-EPROMs + some mistagged EEPROMs |
| 0x08 | IC2_ALG_ROM32P | EPROM_QUICK | 32-pin ROM/EPROM (27C010/020/040) |
| 0x0B | IC2_ALG_ROM24P_1 | EPROM_LEGACY | 24-pin ROM/EPROM type 1 (2716/2732) |
| 0x0D | IC2_ALG_EE28C32P | EEPROM_POLL | 28/32-pin EEPROM (28C-series, 5V page-write, DQ7 poll) |
| 0x0E | IC2_ALG_RAM32_1 | SRAM_32PIN | 32-pin SRAM type 1 |
| 0x10 | IC2_ALG_28F32P | FLASH_INTEL | Intel 28F parallel flash (cmd register, 12V VPP) |
| 0x27 | IC2_ALG_ROM24P_2 | SRAM_24PIN (mislabel) | 24-pin ROM/EPROM type 2 |
| 0x28 | IC2_ALG_ROM28P_2 | SRAM_STD (mislabel) | 28-pin ROM/EPROM type 2 / used for SRAM after fm1608 override |
| 0x29 | IC2_ALG_RAM32_2 | SRAM_512K_1M | 32-pin SRAM type 2 |

**NOT in DIP-24..32 scope:** 0x09 ROM40P (40-pin), 0x0A R28TO32P (PLCC adapter), 0x0C ROM44, 0x11 FWH (LPC bus), 0x35 ITE (TQFP128), **0x39 has NO IC2_ALG define** (legacy INFOIC only, DIP40 AM27C1024) — unreachable from INFOIC2PLUS.

### `flags` (uint32 hex) — `database.c:40–52, 661–682`
CONFIRMED for decoded bits:
```
Bit 1  0x000002 MP_REVERSED_PACKAGE   reversed_package
Bit 4  0x000010 MP_ERASE_MASK         can_erase   <-- build_db "electrically erasable" discriminator
Bit 5  0x000020 MP_ID_MASK            has_chip_id
Bit 12 0x001000 MP_DATA_MEMORY_ADDRESS has_data_offset
Bit 13 0x002000 MP_DATA_BUS_WIDTH     data_org (0=8-bit,1=16-bit)
Bit 14 0x004000 MP_OFF_PROTECT_BEFORE off_protect_before
Bit 15 0x008000 MP_PROTECT_AFTER      protect_after
Bit 18 0x040000 MP_LOCK_BIT_WRITE_ONLY lock_bit_write_only
Bit 19 0x080000 MP_CALIBRATION        has_calibration
Bits 20-21 0x300000 MP_SUPPORTED_PROGRAMMING>>20 prog_support
```
The full 32-bit raw value is forwarded to TL866II+ firmware. **Bits 3/6/7 are NOT decoded in database.c** — the existing docs' "VPP required / UV-erasable / electrically-erasable" meanings for 0x08/0x40/0x80 are INFERRED, not source-confirmed. `flags & 0x10` (`can_erase`) is the correct functional "electrically erasable" signal (UV-EPROM=0, EEPROM/Flash=1).

### `voltages` (uint32 hex) — `database.c:693–697, 144–158`
CONFIRMED.
```
Bits 7-0   VPP byte   device->voltages.vpp
Bits 11-8  VCC nibble device->voltages.vcc
Bits 15-12 VDD nibble device->voltages.vdd
```
VPP byte → V (same as build_db VPP_VOLTAGES): 0x00=12, 0x10=9, 0x20=9.5, 0x30=10, 0x40=11, 0x50=11.5, 0x60=12.5, 0x70=13, 0x80=13.5, 0x90=14, 0xA0=14.5, 0xB0=15.5, 0xC0=16, 0xD0=16.5, 0xE0=17, 0xF0=18.
VCC/VDD nibble → V (`tl866ii_vcc_voltages[]`): 0x00=5, 0x01=3.3, **0x02=4, 0x03=4.5**, 0x04=5.5, 0x05=6.5.

### `variant` (uint32 hex) — `database.c:585`
CONFIRMED. Low byte = sub-algorithm/variant index sent to programmer; bits 15-8 = T56/T76 name index (irrelevant on RURP). build_db uses `variant & 0xFF`.
DIP28 UV-EPROM low byte: 0x10=27C512(DIP28_27512), 0x11=27C256(DIP28_27256), 0x12=27C128(DIP28_2764), 0x13=27C64/2764A(DIP28_2764), else→2764-default.
DIP24 low byte: 0x00=2716, 0x01=2732.

### `pin_map` (uint32 hex, INFOIC2PLUS) — `database.c:608–617`
CONFIRMED. Low byte = pin-test map index (`device->pin_map`), clusters chips by physical layout family. Upper bits: 0x10000000 T56_FLAG, 0x20000000 TL866II_FLAG, 0x40000000 T48_FLAG (programmer-support flags, decoded separately). build_db `pm_idx = pin_map_raw & 0xFF` — correct. NB: TL866II_FLAG=0 does not mean unprogrammable on TL866II+.

### `pulse_delay` (uint32 hex) — `database.c:602–603`
CONFIRMED. **Microseconds for ALL protocols, no transformation.** Verified: AM27C64=0x64(100µs), W27C512=0x64(100µs), AM2716=0x1F4(500µs), AT28C256=0x2710(10000µs=10ms). build_db's `interpret_timing()` ×100 for 0x07/0x0B is WRONG (see BUG-2).

### `chip_id` (uint32 hex) — `database.c:600, 561`
CONFIRMED. Raw silicon ID; 0 = none. Significant byte count via `get_id_bytes_count()`. ID-check gated by `flags & MP_ID_MASK (0x20)`.

### `code_memory_size` (uint32 hex) — `database.c:592`
CONFIRMED. Total addressable bytes (27C512 = 0x10000 = 65536). Used as firmware `memory-size`.

### `page_size` (uint32 hex) — `database.c:598`
CONFIRMED. Page-write size (28C EEPROM typically 64/128; 0/1 if none).

### `read_buffer_size` / `write_buffer_size` (uint32→uint16) — `database.c:586–591`
CONFIRMED. Chunk sizes; NOT used by Firestarter (it derives chunking from board `MSG_OK_READY`).

### `data_memory_size` / `data_memory2_size` — `database.c:594–597`
CONFIRMED. Secondary regions (MCU EEPROM/data banks); ~0 for parallel memory.

### `chip_info` (uint32 hex) — `database.c:605`
CONFIRMED. Opaque discriminator: 0x0006 MP_VOLTAGES1 (adjustable VCC), 0x0007 MP_VOLTAGES2 (adjustable VPP), else MCU-specific. ~0x0000 for standard parallel memory.

### `config` (string) — `database.c:637–658`
CONFIRMED. Names a `<config>` profile (fuse/lock for MCU/PLD); "null"/absent for parallel memory.

### `blank_value` (uint8 hex, optional) — `database.c:627–631`
CONFIRMED. Erased-read byte (default 0xFF). Not stored by build_db today.

### `pages_per_block` (uint32 hex, INFOIC2PLUS) — `database.c:609`
CONFIRMED. NAND/paged-flash block structure; 0/absent for scope.

---

## Confirmed build_db.py Bugs (decode correctness targets)

**BUG-1 — VCC_VOLTAGES incomplete.** Missing `0x02:"4V"`, `0x03:"4.5V"`. AT28C256 (vcc nibble 0x02), AT28C64 family (0x02/0x03) silently default to "5V". Source: `tl866ii_vcc_voltages[]`.

**BUG-2 — interpret_timing ×100 for 0x07 and 0x0B.** pulse_delay is already µs. W27C512 stored "10000 us" (should be 100); AT28C256 stored "1000000 us" (should be 10000). Remove the multiplier; return `f"{val} us"`. (Verify against minipro source once more before changing — flagged gap.)

**BUG-3 — vdd/vcc field names swapped.** Extraction positions correct but labels inverted vs database.c (bits 11-8=vcc, 15-12=vdd). Low functional impact today (both 5V for most chips) but wrong for AT28C256/NVRAM where VCC≠VDD.

**BUG-4 — PROTOCOL_MAP wrong/phantom names.** 0x35 = IC2_ALG_ITE (TQFP128, never passes filter) labeled "FLASH_EEPROM_LIKE"; 0x39 has no IC2_ALG (unreachable) labeled "FLASH_INTEL_ALT"; 0x3C invented (no IC2_ALG counterpart); 0x2A/0x2C/0x2E mislabeled NVRAM (actually GAL16/GAL22/PIC32 per FEATURES.md). 0x27/0x28 labeled SRAM_* but are IC2_ALG_ROM24P_2/ROM28P_2 (repurposed for fm1608 SRAM override, not inherently SRAM).

---

## Existing Decode-Doc Errors (deliverable corrections)

**package-details.md:** mis-titled — content describes `flags`, not `package_details`. Bits 3/6/7 meanings are INFERRED not source-confirmed. Bit 4 = `can_erase` ("can be electrically erased"), not "Requires Write Enable Sequence".

**protocol-flags.md:** 0x07 mislabeled "28-pin byte EEPROM" — it is IC2_ALG_ROM28P_1 (UV-EPROM primary + mistagged EEPROMs). Same bit-4 and bits-3/6/7 errors.

**protocol-id.md:** 0x39 described as "AT49F040 advanced flash" — CRITICAL ERROR (0x39 has no IC2_ALG, INFOIC2PLUS-unreachable). All descriptions inferred, none cite IC2_ALG names.

---

## Status legend
CONFIRMED = read in minipro source. INFERRED = datasheet/behavior, not in source. UNKNOWN = forwarded raw to closed-source TL866II+ firmware, not recoverable from source (flags bits 3/6/7).

# Feature Research

**Domain:** EPROM programmer — complete memory-type coverage for the RURP shield (v1.11)
**Researched:** 2026-06-08
**Confidence:** HIGH (grounded in direct minipro source + infoic.xml inspection, firmware
source, pinouts.json, and chip datasheets; all counts and protocol names verified against
minipro/src/database.h IC2_ALG constants)

---

## Scope Context

This is a CORRECTNESS + EXPANSION milestone. "Features" here means:
1. **Correct decode** of every infoic.xml field relevant to Firestarter (the field-dictionary goal)
2. **Full coverage** of every DIP24/28/32 parallel memory type the RURP can physically drive
3. **No new types** that are physically impossible on the RURP hardware envelope

The research question is: which currently-skipped protocol_id values have DIP parallel chips
inside the RURP envelope (5V VCC, ≤22V VPP, ≤512KB, 8-bit data, DIP24-28-32)?

---

## Complete Protocol_id Catalog

### Definitive Mapping (from minipro/src/database.h IC2_ALG constants)

| protocol_id | IC2_ALG Name | Firestarter Name (build_db.py PROTOCOL_MAP) | In KNOWN_PROTOCOLS | DIP24-32 chips (type=1/4) | Notes |
|-------------|--------------|---------------------------------------------|--------------------|---------------------------|-------|
| 0x05 | IC2_ALG_F29EE | FLASH_AMD_STD | YES | 27 | 5V page-write flash; configure_flash4 |
| 0x06 | IC2_ALG_W29F32P | FLASH_AMD_ALT | YES | 190 | AMD unlock flash; configure_flash3 |
| 0x07 | IC2_ALG_ROM28P_1 | EPROM_STD | YES | 237 (212 in DB after overrides) | UV-EPROM 28-pin; configure_eprom |
| 0x08 | IC2_ALG_ROM32P | EPROM_QUICK | YES | 127 | UV-EPROM 32-pin; configure_eprom |
| 0x0B | IC2_ALG_ROM24P_1 | EPROM_LEGACY | YES | 53 (40 in DB; 9 safety-skipped, 4 NVRAM-overridden) | 24-pin legacy EPROM + some NVRAM |
| 0x0D | IC2_ALG_EE28C32P | EEPROM_POLL | YES | 18 native + 5 via WARNING-5 override = 23 in DB | AT28C 5V EEPROM; configure_eeprom28c |
| 0x0E | IC2_ALG_RAM32_1 | SRAM_32PIN | YES | 20 | 32-pin SRAM/NVRAM (DS1245/BQ4013/M48T128); configure_sram |
| 0x10 | IC2_ALG_28F32P | FLASH_INTEL | YES | 39 | Intel command-set flash; configure_flash_intel |
| 0x11 | IC2_ALG_FWH | FLASH_FWH | NO | 4 (M50FW040/M50FW080 DIP32) | **LPC/FWH bus — NOT parallel** |
| 0x27 | IC2_ALG_ROM24P_2 | SRAM_24PIN | YES | 2 | 24-pin SRAM (6116); configure_sram |
| 0x28 | IC2_ALG_ROM28P_2 | SRAM_STD | YES | 10 XML + NVRAM via type=4 override = 34 in DB | 28-pin SRAM + Dallas/M48T NVRAM; configure_sram |
| 0x29 | IC2_ALG_RAM32_2 | SRAM_512K_1M | YES | 20 | 32-pin SRAM 512K/1M; configure_sram |
| 0x2A | IC2_ALG_GAL16 | NVRAM_32PIN (**WRONG**) | NO | 0 (GAL16V8 PLDs, type=3, not in scope) | Naming error in build_db.py; GAL PLD, not NVRAM |
| 0x2C | IC2_ALG_GAL22 | NVRAM_TIMEKEEPER (**WRONG**) | NO | 10 (ATF22V10/GAL22V10 PLDs, type=3, not in scope) | Naming error in build_db.py; GAL PLD, not timekeeper |
| 0x2E | IC2_ALG_PIC32X_2 | NVRAM_512K (**WRONG**) | NO | 0 (PIC32 MCU, no DIP memory chips) | Naming error in build_db.py; MCU, not NVRAM |
| 0x35 | IC2_ALG_ITE | FLASH_EEPROM_LIKE (**WRONG**) | YES | 0 (ITE IT8xxx MCU TQFP128 only) | Phantom: in KNOWN_PROTOCOLS but zero chips in DB |
| 0x39 | (not in IC2_ALG table) | FLASH_INTEL_ALT | YES | 0 in INFOIC2PLUS; DIP40 only in legacy INFOIC | Phantom: in KNOWN_PROTOCOLS but zero chips in DB |
| 0x3C | (not in IC2_ALG table) | FLASH_4MB (**INVENTED**) | NO | 0 in INFOIC2PLUS | Not a real IC2_ALG constant; no chips |
| 0x04 | IC2_ALG_AT45D | (not in PROTOCOL_MAP) | NO | 18 (AT45D SOIC28 only) | **SPI DataFlash — serial interface, NOT parallel** |
| 0x0A | IC2_ALG_R28TO32P | (not in PROTOCOL_MAP) | NO | 1 (TMS87C257 PLCC32 — MCU, not memory) | ROM-adapt MCU, not in scope |
| 0x34 | IC2_ALG_GEN | (not in PROTOCOL_MAP) | NO | 1 (X88C64P DIP24 supervisor+EEPROM) | Obscure supervisory chip; 1 entry; low payoff |

### Critical Naming Errors in build_db.py PROTOCOL_MAP

The `PROTOCOL_MAP` dict has three incorrect names that will mislead anyone reading it:

| protocol_id | Current (Wrong) Name | Correct Name | Impact |
|-------------|---------------------|--------------|--------|
| 0x2A | NVRAM_32PIN | GAL16 (GAL16V8 PLD algorithm) | Misleads: no NVRAM chips use 0x2A |
| 0x2C | NVRAM_TIMEKEEPER | GAL22 (GAL22V10 PLD algorithm) | Misleads: these are PLDs, not timekeepers |
| 0x2E | NVRAM_512K | PIC32X_2 (PIC32 MCU) | Misleads: MCU protocol, not NVRAM |
| 0x35 | FLASH_EEPROM_LIKE | ITE (ITE IT8xxx MCU EC) | Misleads: MCU, not flash-like-EEPROM |
| 0x3C | FLASH_4MB | (invented — not in IC2_ALG constants) | Does not exist in minipro protocol space |

**The NVRAM situation:** Dallas DS1225/DS1230/M48T* timekeepers/NVRAM chips do NOT use
0x2A/0x2C/0x2E. They use:
- 28-pin NVRAMs (DS1225, DS1230, M48T08/18/35/58/59, BQ4010/4011, Ramtron FRAM): tagged
  `type=4` with `protocol_id=0x07` in infoic.xml; the `fm1608-db-mismatch` override in
  `build_db.py` converts these to `algorithm=0x28` (SRAM_STD) → `configure_sram`. They are
  **already in the DB** and handled correctly.
- 32-pin NVRAMs (DS1245/DS1249/DS1250, BQ4013/4014, M48T128/512): use `protocol_id=0x0E`
  (SRAM_32PIN) directly → `configure_sram`. **Already in DB and handled.**
- 24-pin NVRAMs (DS1220, M48T02/12): use `protocol_id=0x0B` (EPROM_LEGACY) with `type=4`;
  `fm1608-db-mismatch` override converts to `algorithm=0x28` → `configure_sram`. **Already in DB.**

---

## Feature Landscape

### Table Stakes (Correct Decode of the 13 Already-Supported Protocols)

These are correctness fixes that v1.11 must deliver to make the existing 734-chip database
trustworthy. None require new firmware handlers.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Fix PROTOCOL_MAP naming errors (0x2A/0x2C/0x2E/0x35/0x3C)** | The names are flat-out wrong per minipro database.h source. Anyone reading PROTOCOL_MAP to understand the protocol space gets incorrect information. NVRAM chips do NOT use these IDs. | LOW | Rename: 0x2A→GAL16, 0x2C→GAL22, 0x2E→PIC32X_2, 0x35→ITE, remove 0x3C entirely. These IDs have zero DIP memory chips and are not in scope; removing 0x3C from PROTOCOL_MAP is correct. |
| **Re-derive infoic.xml field-dictionary from minipro source** | The existing protocol-id.md, protocol-flags.md have inferences but lack source grounding. `package_details`, `voltages`, `pin_map`, `flags`, `variant` fields are partially documented. | MEDIUM | Read minipro/src/database.c and xml.c to extract the authoritative decode for each field. Deliver corrected canonical docs. This is the "field dictionary" goal. |
| **Correct pinout resolution for currently-misrouted chips** | The `PIN_MAP_TO_PINOUT` and `PIN_MAP_PROTO_TO_PINOUT` tables have heuristic entries. Some have LOW confidence (MEDIUM-confidence comments in build_db.py). | MEDIUM | Cross-check pinout assignments against minipro source pin_map table + datasheets for each pm_idx group. Fix any where the assignment is wrong. |
| **Document 0x35/0x39 as phantom protocols** | They are in KNOWN_PROTOCOLS but produce zero chips. That's invisible and confusing. | LOW | Add comments in build_db.py and KNOWN_PROTOCOLS explaining why these exist (0x39 = DIP40 UV-EPROM in legacy INFOIC DB, not INFOIC2PLUS; 0x35 = ITE MCU). Consider removing from KNOWN_PROTOCOLS if they will never produce chips. |
| **VCC/VPP decode for 3.3V chips** | The `VCC_VOLTAGES` mapping is `{0:5V, 1:3.3V, ...}` but the decoding `(voltages >> 12) & 0x0F` doesn't align with all observed values (e.g., DS1230W 3.3V has `voltages=0x0101` where vdd nibble=1=3.3V). Build_db.py uses both `vdd` and `vcc` fields; the decode logic should be verified against actual 3.3V chip entries. | MEDIUM | Source-check the voltages field against minipro/src/database.c `pack_voltages()` to confirm nibble positions. Verify 3.3V chips decode correctly. |

### Differentiators (New Handlers Worth Adding)

These are the expansion types — chips currently blocked that the RURP CAN physically drive.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **24-pin EEPROM support (AT28C04/AT28C16 family)** | 9 chips currently blocked by the safety skip in build_db.py. These are 5V DIP24 EEPROMs (512B AT28C04, 2KB AT28C16) with standard parallel bus. No new firmware handler needed — they use `configure_eeprom28c` (0x0D dispatch) which already handles 5V page-write + SDP-disable. | LOW | Fix is entirely in the data pipeline: (1) use `DIP24_6116` pinout instead of `DIP24_2716` (the 6116 pinout already has WE# on pin 21 — exactly where AT28C16 WE# is); (2) assign `algorithm=0x0D`; (3) remove the safety skip for these chips. **No firmware changes needed.** SDP addresses 0x5555/0x2AAA alias correctly within 11-bit address space. Chip-ID check via A9=pin22 (12V): safe for AT28C16 (A9 is pin 22); AT28C04 has no A9 so chip_id=0 skips the check. Payoff: 9 chips unblocked. |
| **Verify configure_sram write correctness for battery-backed NVRAM** | DS1225/DS1230/M48T* NVRAM are already in the DB routed to `configure_sram`, but `configure_sram()` is a no-op stub. The read/write path uses generic `memory_get_data`/`memory_set_data` from `memory.cpp`. This is functionally correct for SRAM (CE-gated write, no VPP), but write-protect behavior of Dallas chips (WP# pin) needs datasheet verification. | LOW | Audit DS1225 and M48T08 datasheets for WP# behavior on DIP28 socket. If WP# is always internally pulled inactive or routed to a non-driven pin on the RURP, write works without changes. Document the finding. No code change likely needed. |
| **Consider configure_sram write stub documentation** | The `configure_sram` function body is a single log call. This is correct (generic handlers take over) but gives no indication to future maintainers that writes work. | LOW | Add a code comment explaining that SRAM write uses the `memory_set_data` generic path set up in `configure_memory` before `configure_sram` is called. |

### Anti-Features (Types That Look In-Scope but Are Physically Impossible on RURP)

| Feature | Why Requested | Why Infeasible on RURP | Verdict |
|---------|---------------|------------------------|---------|
| **FWH (Firmware Hub) flash — protocol_id 0x11** | M50FW040/M50FW080 are physically DIP32 chips and appear in the 32-pin filter in infoic.xml. | FWH uses the Intel LPC (Low Pin Count) bus — a 4-wire multiplexed serial protocol (LAD[0:3] + LFRAME# + CLK). Address and data are both transmitted in nibbles over LAD[0:3]. The RURP has no CLK generation, no nibble-mux capability, and the chip requires 3.3V VCC (RURP is fixed 5V — direct damage path). This is a DIP32 physical package with a non-parallel interface inside. The minipro TL866 handles it via a special bitstream; the RURP Arduino cannot. | **INFEASIBLE** |
| **NVRAM protocol_ids 0x2A/0x2C/0x2E** | These were labeled NVRAM in build_db.py and appeared to be unexplored NVRAM territory. | These IDs are GAL16V8 PLD (0x2A), GAL22V10 PLD (0x2C), and PIC32 MCU (0x2E) algorithms per minipro/src/database.h. There are zero DIP memory chips using these IDs in INFOIC2PLUS. The NVRAM chips (Dallas/M48T/BQ40) already use standard SRAM protocol IDs. | **OUT OF SCOPE (wrong device class)** |
| **AT45D DataFlash — protocol_id 0x04** | 18 SOIC28 entries in infoic.xml. Appears to be a 28-pin memory. | AT45D is Atmel/Adesto DataFlash — a SPI serial flash. All 18 entries are SOIC28 packages (SMD), and the interface is SPI (CLK, SI, SO, CS#). The infoic.xml `is_serial` byte is non-zero for these. The RURP drives a parallel bus; it has no SPI master capability. | **INFEASIBLE (serial interface + SMD)** |
| **DIP40 UV-EPROM — protocol_id 0x39 (IC2_ALG_ROM32P variant)** | 0x39 appears in KNOWN_PROTOCOLS, suggesting some support exists. | Protocol 0x39 in the INFOIC legacy database is used by 27C1024/27C2048/27C4096 (16-bit data bus, DIP40). These are word-wide (×16) EPROMs. The RURP has an 8-bit data bus and a 24/28/32-pin socket only. DIP40 does not fit the RURP ZIF socket. | **OUT OF SCOPE (DIP40, 16-bit bus)** |
| **X88C64P supervisory EEPROM — protocol_id 0x34 (IC2_ALG_GEN)** | 1 DIP24 chip in INFOIC2PLUS; looks like a 24-pin parallel EEPROM. | The Xicor X88C64 is a supervisory circuit combining reset monitoring, watchdog timer, and EEPROM. Its protocol is the minipro "GEN" (generic) handler. The chip has an unusual multiplexed/supervisory interface. With only 1 chip and unclear interface requirements, the effort/payoff ratio is poor. | **DEFER (low payoff, unclear interface)** |
| **ITE IT8xxx MCU flash — protocol_id 0x35 (IC2_ALG_ITE)** | Listed in KNOWN_PROTOCOLS as FLASH_EEPROM_LIKE, implying flash-like parallel EEPROM. | The ITE IT8xxx is an Embedded Controller (EC) MCU in TQFP128 package. It is a microcontroller, not a memory chip. There are no DIP24-32 chips using protocol_id=0x35. The minipro algorithm is an MCU-specific flashing protocol, not a generic flash EEPROM algorithm. | **OUT OF SCOPE (MCU, wrong package)** |
| **6.5V/5.5V VCC chips** | Some chips in VCC_VOLTAGES are flagged as needing 5.5V or 6.5V VCC (VCC_VOLTAGES codes 0x04/0x05). | The RURP supplies fixed 5V VCC. Chips requiring >5V VCC cannot be safely powered. These entries (if any DIP24-32 chips use them) should be filtered in build_db.py. | **INFEASIBLE (voltage envelope)** |

---

## Feature Dependencies

```
PROTOCOL_MAP naming fix
    └──prerequisite──> field-dictionary docs
        (correct names are required before documenting the protocol space)

infoic.xml field-dictionary (source-grounded)
    └──enables──> principled pinout resolution
    └──enables──> correct voltages decode
    └──enables──> removing heuristic overrides

24-pin EEPROM pipeline fix (DIP24_6116 pinout + algorithm=0x0D)
    └──independent of firmware changes
    └──depends on──> pinout verification (DIP24_6116 vs DIP24_2716 correctness confirmed)

configure_sram NVRAM write audit
    └──independent of all above
    └──no code change likely; documentation outcome

FWH / 0x2A/0x2C/0x2E / AT45D
    └──no dependency chain; these are simply EXCLUDED from all phases
```

### Dependency Notes

- **PROTOCOL_MAP naming must precede docs:** The protocol-id.md canonical doc should reflect
  correct IC2_ALG names, not the current wrong NVRAM labels.
- **24-pin EEPROM fix is pipeline-only:** No firmware handler changes are needed. The
  `configure_eeprom28c` handler already works for 5V 24-pin EEPROMs if the pinout and
  algorithm are set correctly in the data pipeline.
- **NVRAM is already handled:** The fact that NVRAM chips use standard SRAM protocol IDs
  (0x07/0x0B with type=4 override, or 0x0E/0x28/0x29 directly) means no new work is needed
  for Dallas/M48T/BQ40 NVRAM support. The `fm1608-db-mismatch` override already handles them.

---

## MVP Definition (What v1.11 Ships)

### Launch With (v1.11)

The minimum to close the v1.11 goal — all DIP parallel types correctly covered.

- [ ] **PROTOCOL_MAP naming corrections** — rename 0x2A/0x2C/0x2E/0x35, remove 0x3C, document 0x35/0x39 as phantom (data pipeline, no firmware change)
- [ ] **Authoritative field-dictionary docs** — protocol-id.md, protocol-flags.md, package-details.md rewritten from minipro source (documentation)
- [ ] **24-pin EEPROM unblock** — assign `DIP24_6116` pinout + `algorithm=0x0D` to AT28C04/AT28C16/28C04A/28C16A/UPD28C04; remove safety skip (9 new chips, data pipeline only)
- [ ] **Pinout resolution audit** — verify all PIN_MAP_TO_PINOUT and PIN_MAP_PROTO_TO_PINOUT entries against minipro source + datasheets; fix any LOW-confidence entries
- [ ] **Voltage decode correctness** — verify VCC/VDD/VPP nibble positions against minipro source; fix 3.3V chip decode if wrong
- [ ] **FWH/0x2A/0x2C/0x2E/AT45D explicitly out-of-scope** — add filter comments in build_db.py explaining why they are excluded

### Deferred / Future

- [ ] **configure_sram write stub → real SRAM write handler** — the generic path works but a real handler would be cleaner (v1.12 or later, after bench validation of NVRAM write)
- [ ] **DIP40 UV-EPROM (0x39)** — requires hardware not on the RURP; defer indefinitely
- [ ] **X88C64P supervisory EEPROM** — 1 obscure chip, unclear interface; low priority

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| PROTOCOL_MAP naming fixes | MEDIUM (correctness) | LOW | P1 |
| Authoritative field-dictionary docs | HIGH (all future work depends on this) | MEDIUM | P1 |
| 24-pin EEPROM unblock (9 chips) | MEDIUM | LOW | P1 |
| Pinout resolution audit | HIGH (safety) | MEDIUM | P1 |
| Voltage decode correctness | MEDIUM | LOW | P1 |
| FWH/exotic out-of-scope documentation | MEDIUM (prevents future wasted effort) | LOW | P1 |
| configure_sram write handler (real) | LOW (current path works) | MEDIUM | P3 |
| X88C64P supervisory chip | LOW | MEDIUM | DEFER |

---

## Sources

- `minipro/src/database.h` — definitive IC2_ALG constant names (HIGH confidence; direct source inspection)
- `minipro/infoic.xml` — chip census by protocol_id, DIP24-32, type=1/4 (HIGH confidence; direct query)
- `firestarter_app/tools/build_db.py` — PROTOCOL_MAP, KNOWN_PROTOCOLS, safety skip logic, pinout resolution (HIGH confidence; direct inspection)
- `firestarter/src/proms/memory.cpp` — configure_memory dispatch chain + configure_sram no-op stub (HIGH confidence; direct inspection)
- `firestarter/src/proms/eeprom_28c.cpp` — SDP disable addresses, chip-id A9 mechanism (HIGH confidence; direct inspection)
- `firestarter_app/firestarter/data/pinouts.json` — DIP24_6116 rw-pin=21, confirming WE# compatibility (HIGH confidence; direct inspection)
- `firestarter_app/firestarter/data/chip_database.json` — algorithm histogram confirming 0x35/0x39 = 0 chips (HIGH confidence; direct query)
- AT28C16/AT28C04 JEDEC datasheets — pinout, WE#=pin21, SDP addresses (MEDIUM confidence; well-known industry-standard chips)
- M50FW040 ST datasheet + Intel FWH specification — LPC bus protocol, 3.3V VCC, LAD[0:3] interface (HIGH confidence; FWH is a well-documented Intel standard)

---
*Feature research for: Firestarter v1.11 — Complete infoic.xml Decode & Full Memory-Type Coverage*
*Researched: 2026-06-08*

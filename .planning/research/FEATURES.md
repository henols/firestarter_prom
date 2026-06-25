# Feature Landscape — v1.15 Bench Validation of Operator Inventory

**Domain:** EPROM/Flash/EEPROM/FRAM programmer — silicon validation milestone (11 chips, 5 algorithm families, 1 graduation candidate)
**Researched:** 2026-06-23
**Based on:** .planning/PROJECT.md §v1.15, .planning/MILESTONES.md, firestarter_app/firestarter/data/chip_database.json, firestarter/src/proms/eprom.cpp, flash_type_3.cpp, flash_type_4.cpp, sram.cpp, firestarter/CLAUDE.md, .planning/research/_archive-pre-v1.15/CHIP_FAMILIES.md, .planning/research/_archive-pre-v1.15/FEATURES.md

---

## Section 1: Per-Chip Expected Behavior

All 11 chips are addressed against the chip_database.json entries as of v1.14 close (650 host tests green, 744-chip dispatch gate 0 violations). Board: Leonardo + RURP Rev 2.0. Standing preconditions per every bench task: live R1 readback (`r1 ≈ 270000`), verify `controller:` port identity, chip-OUT before sideload (Uno-class only; Leonardo is EXEMPT).

---

### 1.1 Family 0x07 configure_eprom — W27C512, W27E512, SST27SF512

**Handler:** `configure_eprom` (eprom.cpp), dispatched via `protocol == 0x07`.

**Firmware pulse timing:** `pulse_delay` defaults to 1000 µs (1 ms) when the DB value is the same (algorithm 7 / EPROM_STD path). The DB records `pulse_duration: "100 us"` for all three — this is what the host passes as `pulse-delay`; firmware uses it directly.

| Chip | DB part_number | electrical.type | vpp_mv | size_bytes | pinout | chip_id_value | support_status |
|------|---------------|-----------------|--------|-----------|--------|---------------|---------------|
| W27C512 | W27C512,W27E512 | EEPROM | 12000 | 65536 | DIP28_27512 | 0x0000da08 | supported |
| W27E512 | (same entry as W27C512) | EEPROM | 12000 | 65536 | DIP28_27512 | 0x0000da08 | supported |
| SST27SF512 | SST27SF512 | EEPROM | 12000 | 65536 | DIP28_27512 | 0x0000bfa4 | supported |

**W27C512 / W27E512 — same DB entry.**
These are EEPROM, electrically erasable. The W27E512 and W27C512 are pin-compatible JEDEC 27512 footprint chips; the DB lists them as one entry. The W27C512 is bench-proven (Phase 77: write→auto-erase→program→verify clean, SHA match). The W27E512 is a distinct die but functionally identical under 0x07 — the bench run for one is a proxy for the other.

**Erase behavior:** Auto-erase BEFORE write, enabled by `FLAG_CAN_ERASE` (derived from `electrical.type == "EEPROM"` since Phase 77). The erase uses `eprom_internal_erase` (eprom.cpp:274) which asserts VPP regulator + CTRL_VPP_A9_ENABLE + CTRL_VPE_ENABLE, then a CE pulse for `pulse_delay` microseconds. VPP for erase is the raw VPE rail (~12–14V on Rev 2.0); VPP for write is VPE through the dropping resistor (CTRL_VPP_VPE_DROP_ENABLE path = ~12V at socket).

**Programming algorithm (one line):** Apply 12V VPP, set address+data, pulse CE low for 100 µs per byte, verify immediately; retry up to 20× with increasing pulse width if mismatch.

**Correct write→read→verify looks like:**
1. `firestarter write -e W27C512 image.bin` — firmware erases (CE pulse ~100 µs with VPE on A9), blank-checks (all 0xFF), programs byte-by-byte with 100 µs pulses + verify-per-byte, returns exit 0.
2. `firestarter read -e W27C512 out.bin` — reads 64 KB at 5V VCC, no VPP.
3. SHA of out.bin matches image.bin.
4. `firestarter verify -e W27C512 image.bin` exits 0 (wrong file exits 1).

**DB suspicion flags:**
- None for W27C512/W27E512 — bench-proven in Phase 77.
- SST27SF512: chip_id 0x0000bfa4 (SST mfr 0xBF, device 0xA4). The SST27SF512 datasheet specifies VPP=12V for program and erase, VCC=5V — consistent with DB. Algorithm 7 is correct (28-pin 27512 footprint EEPROM, 50 µs min pulse per SST datasheet but DB uses 50 µs; the DB entry shows 50 µs, which differs from the W27C512 100 µs — no alarm, different manufacturers have different minimum pulse widths). **FLAG: Confirm the SST27SF512 chip ID 0xBFA4 responds correctly with `firestarter check-chip-id`. SST datasheets for the SF512 list chip ID as 0xBFA4 (mfr=0xBF, device=0xA4); this is consistent.**

---

### 1.2 Family 0x07 configure_eprom — ST M27C512 (UV-EPROM)

**DB entry:** Mfr ST, part_number `M27C512,M27V512,M27W512`. Also present as SGS-THOMSON `M27C512,M27V512`.

| Field | Value |
|-------|-------|
| electrical.type | UV-EPROM |
| vpp_mv | 13000 |
| size_bytes | 65536 |
| pinout | DIP28_27512 |
| algorithm | 7 |
| chip_id_value | 0x0000203d |
| support_status | supported |
| pulse_duration | 100 us |

**Erase behavior:** NONE electrically. UV-EPROM — can only be erased with UV light (~15 min under a UVPROM eraser). The operator has NO UV eraser. `FLAG_CAN_ERASE` is NOT set (electrical.type == "UV-EPROM", not "EEPROM"), so `eprom_write_init` will NOT call `eprom_internal_erase`. The chip can only be programmed 1→0 per bit; unprogrammed cells read 0xFF.

**Programming algorithm (one line):** Apply 13V VPP via CTRL_VPP_VPE_DROP_ENABLE path, set address+data, pulse CE low for 100 µs, verify-per-byte; retry up to 20× — but ONLY 1→0 bit transitions are possible without prior UV erase.

**VPP path:** Algorithm 7, not 0x0B — uses CTRL_VPP_VPE_DROP_ENABLE (dropping resistor from VPE to VPP rail), NOT the direct VPE path. VPP target = 13V; firmware checks VPP ADC and warns/errors if it's outside ±5% / +500mV of vpp_mv=13000.

**Correct write→read→verify for no-eraser scenario (see Section 2):**
1. `firestarter read -e M27C512 out.bin` + blank check first.
2. If blank: `firestarter write -b -e M27C512 image.bin` (skip blank check, the chip is known blank).
3. If not blank: use AND-mask / all-0x00 test write (Section 2 protocol).
4. `firestarter verify -e M27C512 image.bin` exits 0.

**DB suspicion flags:**
- VPP=13V for an ST M27C512 is correct per the ST datasheet (VPP=12.5V typical, 12-13V range). No issue.
- chip_id 0x0000203d: ST encodes this as mfr=0x20 (ST/SGS), device=0x3D. Confirmed in minipro DB. The `chip_id_check: true` means firmware will assert VPP to A9 and read the ID — requires VPP rail to be stable before the check. **FLAG: If chip_id check fails on a real M27C512, try `--force` (ID mismatch as warning) — older ST parts occasionally misread on the first probe.**
- The DB entry covers M27V512 (low-power variant) and M27W512 (wide-voltage) under the same chip_id. For bench purposes, assume operator's chip is a standard M27C512 and the chip_id will match.

---

### 1.3 Family 0x08 configure_eprom — W27E040 (EEPROM)

**DB entry:** Mfr WINBOND, part_number `W27C04,W27C040,W27E040`.

| Field | Value |
|-------|-------|
| electrical.type | EEPROM |
| vpp_mv | 12000 |
| size_bytes | 524288 (512 KB) |
| pinout | DIP32_STD |
| algorithm | 8 |
| chip_id_value | 0x0000da86 |
| support_status | supported |
| pulse_duration | 100 us |

**Algorithm 8 vs Algorithm 7:** Both dispatch to `configure_eprom` in firmware. The difference is `pulse_delay`: algorithm 0x08 defaults to 100 µs (the EPROM_QUICK / JEDEC Fast path), algorithm 0x07 defaults to 1 ms. Since the DB passes `pulse_duration: "100 us"` for both, the effective pulse is 100 µs in both cases. Algorithm 8 is used for 32-pin 27Cxxx CMOS quick-pulse chips (AM27C010/020/040) AND for Winbond/SST 32-pin EEPROM variants that happen to share the same quick-pulse timing.

**Erase behavior:** Auto-erase BEFORE write. `electrical.type == "EEPROM"` → `FLAG_CAN_ERASE` set (since Phase 77). Same `eprom_internal_erase` path as W27C512.

**Programming algorithm (one line):** Apply 12V VPP via CTRL_VPP_VPE_DROP_ENABLE path, set 32-pin address+data (A0–A18), pulse CE low for 100 µs per byte, verify immediately, retry up to 20×.

**Correct write→read→verify:**
1. `firestarter write -e W27E040 image.bin` (512 KB binary) — auto-erase then program, exit 0.
2. `firestarter read -e W27E040 out.bin` — reads 512 KB.
3. SHA match.

**DB suspicion flags:**
- `DIP32_STD` pinout: correct for the W27E040 (32-pin, VPP on pin 1, A0–A18). The W27E040 datasheet specifies the same 32-pin JEDEC 27xxx layout.
- `vpp_mv: 12000` for a W27E040: the Winbond W27E040 datasheet specifies VPP=12V for program and 14V for erase (same as W27C512 class). The erase voltage via the raw VPE rail on Rev 2.0 is ~12–14V — within range. **FLAG: Confirm the erase rail sits in the 12–14V window before seating the chip. The DB records 12V for both erase and program, but the erase path uses the unregulated VPE rail — measure chip-OUT before seating.**
- chip_id 0x0000da86: Winbond mfr=0xDA, device=0x86. W27C040=0x86 per Winbond datasheets. Consistent.

---

### 1.4 Family 0x08 configure_eprom — AM27C020 (UV-EPROM)

**DB entry:** Mfr AMD, part_number `AM27C020`.

| Field | Value |
|-------|-------|
| electrical.type | UV-EPROM |
| vpp_mv | 13000 |
| size_bytes | 262144 (256 KB) |
| pinout | DIP32_STD |
| algorithm | 8 |
| chip_id_value | 0x00000197 |
| support_status | supported |
| pulse_duration | 100 us |

**Erase behavior:** NONE electrically. UV-EPROM, no eraser available. `FLAG_CAN_ERASE` NOT set.

**Programming algorithm (one line):** Apply 13V VPP via CTRL_VPP_VPE_DROP_ENABLE path to DIP32 pin 1, set A0–A17 + data, pulse CE low for 100 µs per byte, verify-per-byte; retry up to 20×.

**Correct write→read→verify for no-eraser scenario:** Same protocol as ST M27C512 (Section 2). Read + blank check first; spend vs. preserve decision at bench.

**DB suspicion flags:**
- chip_id 0x00000197: AMD mfr=0x01, device=0x97. The AMD 27C020 datasheet chip-ID reads mfr=0x01 at A0=0, device=0x97 at A0=1 — consistent.
- `DIP32_STD` pinout: correct for AM27C020 (pin 1=VPP, pin 31=PGM, pins per JEDEC 32-pin 27Cxxx standard). Consistent with all other 32-pin AM27Cxxx parts.
- VPP=13V: AMD 27C020 specifies VPP=12.5V ±0.5V (12–13V range). DB vpp_mv=13000 is within range but at the upper limit. On Rev 2.0 the dropping-resistor path targets 13V — verify ADC readback before program.

---

### 1.5 Family 0x06 configure_flash3 — SST39SF040

**Handler:** `configure_flash3` (flash_type_3.cpp), dispatched via `protocol == 0x06`.

**DB entry:** Mfr SST, part_number `SST39SF040`. Bench-proven in Phase 74 (V1.13).

| Field | Value |
|-------|-------|
| electrical.type | Flash/EEPROM |
| vpp_mv | 12000 (WP pin only, NOT required for programming) |
| size_bytes | 524288 (512 KB) |
| pinout | DIP32_SST39SF040 |
| algorithm | 6 |
| chip_id_value | 0x0000bfb7 |
| support_status | supported |

**Erase behavior:** Sector erase (4 KB) or chip erase via AMD/JEDEC 6-byte unlock sequence to addresses 0x5555/0x2AAA. `FLAG_CAN_ERASE` derived from electrical type. For flash3, `flash3_write_init` runs `flash3_erase_execute` once (guarded by `is_operation_in_progress`). Chip erase command sequence: `0xAA→0x5555, 0x55→0x2AAA, 0x80→0x5555, 0xAA→0x5555, 0x55→0x2AAA, 0x10→0x5555`. Erase settle delay: 105 ms. All programming at 5V VCC — NO elevated VPP.

**Programming algorithm (one line):** 6-byte AMD unlock at 0x5555/0x2AAA before each byte (`FLASH_ENABLE_WRITE`), write byte at target address, poll DQ7 toggle bit until stable.

**Correct write→read→verify:**
1. `firestarter write -e SST39SF040 image.bin` — chip erase + 105 ms settle + byte-by-byte AMD program, exit 0.
2. `firestarter read -e SST39SF040 out.bin` — 512 KB at 5V.
3. SHA match.

**DB suspicion flags:**
- `DIP32_SST39SF040` pinout (not `DIP32_STD`): the SST39SF040 uses A18 on pin 1 (vs. VPP on pin 1 for 27Cxxx); WE on pin 31 (vs. PGM). This is correct and expected — the pinout key reflects the different flash layout. The DB pinout is correct.
- vpp_mv=12000: This is the WP pin voltage, NOT a programming voltage. Flash3 never enables the VPP regulator for writes (all 5V). The 12V in the DB is informational only.

---

### 1.6 Family 0x05 configure_flash4 — W29C020, W29C040

**Handler:** `configure_flash4` (flash_type_4.cpp), dispatched via `protocol ∈ {0x05, 0x35, 0x39}`. W29C020 and W29C040 both use protocol 0x05.

**W29C040 bench-proven in Phase 74** (real FAIL → fix: SDP 3-byte unlock per page + data-driven 256-byte page size).

| Chip | DB part_number | size_bytes | chip_id_value | pinout |
|------|---------------|-----------|---------------|--------|
| W29C020 | W29C020,W29C020C,W29C022 | 262144 | 0x0000da45 | DIP32_SST39SF040 |
| W29C040 | W29C040,W29C042 | 524288 | 0x0000da46 | DIP32_SST39SF040 |

Both: `electrical.type: Flash/EEPROM`, `vpp_mv: 12000` (WP pin, not programming), `algorithm: 5`, `support_status: supported`.

**Erase behavior:** Flash4 internal: the W29C0x0 chips use an internal erase triggered by a hardware /OE→12V pulse sequence (`flash4_erase_execute`). The erase is NOT the AMD 6-byte unlock sequence — it's a direct CTRL_VPP_REGULATOR_ENABLE + CTRL_VPP_VPE_DROP_ENABLE + CTRL_VPE_ENABLE assert with a WE strobe. `FLAG_CAN_ERASE` controls whether `flash4_write_init` calls `flash4_erase_execute`. For Flash/EEPROM type, `FLAG_CAN_ERASE` should be set (verify Phase 77's logic applies to flash4 too — see Pitfall note below).

**Programming algorithm (one line):** SDP 3-byte AMD unlock at page-start + page-load at 5V (256 bytes/page for W29C040, 128 bytes for W29C020), then poll DQ7 of the last written byte until stable (up to 1024 × 10 µs = ~10 ms); no elevated VPP during write.

**Page size:** Data-driven: `flash4_page_size(524288) = 256` for W29C040; `flash4_page_size(262144) = 128` for W29C020.

**Correct write→read→verify:**
1. `firestarter write -e W29C040 image.bin` — internal erase (if FLAG_CAN_ERASE set) + SDP-unlocked page writes, exit 0.
2. `firestarter read -e W29C040 out.bin` — 512 KB at 5V.
3. SHA match.

**DB suspicion flags:**
- `DIP32_SST39SF040` pinout for both: W29C0x0 use the same pin layout as SST39SF040 (A18 on pin 1, WE on pin 31), not DIP32_STD. The W29C040 datasheet confirms this. Correct.
- vpp_mv=12000: WP pin, not a programming voltage. All writes at 5V VCC.
- W29C020 chip_id 0x0000da45: Winbond mfr=0xDA, device=0x45. W29C020 datasheet confirms 0x45. Correct.
- **PITFALL FLAG: FLAG_CAN_ERASE for Flash/EEPROM type.** Phase 77 wired `FLAG_CAN_ERASE` from `electrical.type == "EEPROM"`. The W29C020 and W29C040 have `electrical.type == "Flash/EEPROM"` (not exactly "EEPROM"). Confirm that `convert_to_programmer` in database.py sets FLAG_CAN_ERASE for "Flash/EEPROM" in addition to "EEPROM", or that flash4_write_init independently handles the erase irrespective of this flag. If FLAG_CAN_ERASE is NOT set for Flash/EEPROM type, the write command will skip erase and the blank-check will fail on a non-blank chip (non-0xFF cells cannot be overwritten without erase). This must be verified before bench — it is a likely gap surfaced by v1.15 bench work.

---

### 1.7 Family 0x40 configure_sram — FM1608 (FRAM)

**Handler:** `configure_sram` (sram.cpp), dispatched via `protocol == 0x40` (decimal 64).

**DB entry:** Mfr RAMTRON, part_number `FM1608`. Bench-proven in Phase 73 (V1.13: two-pattern N=2 PASS).

| Field | Value |
|-------|-------|
| electrical.type | SRAM |
| vpp_mv | 12000 (informational — NEVER applied to FM1608) |
| size_bytes | 8192 (8 KB) |
| pinout | DIP28_JEDEC_SRAM_8K |
| algorithm | 40 (0x28) |
| chip_id_check | false |
| support_status | supported |

**Erase behavior:** None — SRAM/FRAM is overwritten byte-by-byte at 5V VCC. No erase concept. `FLAG_CAN_ERASE` not set. `configure_sram` uses `generic_memory_write_execute` — no VPP regulator engagement.

**Programming algorithm (one line):** Write bytes directly via address+data bus at 5V VCC; no erase, no VPP, no polling — FRAM writes complete instantly.

**Note on VPP:** The FM1608 DB entry shows vpp_mv=12000, but this is carried over from the minipro DB and is NOT applied by the firmware. `configure_sram` never enables the VPP regulator. The `reference_vpp_vpe_no_socket_routing.md` memory note confirms: vpp/vpe monitor commands do not route voltage to the socket; no VPP/VPE risk with FM1608 seated.

**Correct write→read→verify:**
1. `firestarter write -e FM1608 image.bin` (8 KB) — direct write at 5V, exit 0.
2. `firestarter read -e FM1608 out.bin` — 8 KB.
3. SHA match.

**DB suspicion flags:**
- `DIP28_JEDEC_SRAM_8K` pinout: FM1608 is JEDEC 6116-compatible (28-pin, 8K×8 SRAM pinout). Correct.
- vpp_mv=12000: Informational; never applied. No risk.
- algorithm=40 (0x28): Maps to `configure_sram`. Correct per dispatch table (0x28 is one of the SRAM protocol IDs).

---

### 1.8 Family 0x0B configure_eprom — the 2516 (ABSENT from DB; graduation candidate)

**The 2516 is confirmed absent from minipro's infoic.xml** (PROJECT.md §v1.15: "confirmed absent from minipro upstream; the 28 '2516' hits are all 25160 SPI serial parts"). No DB entry exists. v1.15 will author one.

**Datasheet facts (TI TMS2516 / Intel-2716-class, from CHIP_FAMILIES.md and datasheet knowledge):**

| Attribute | Value |
|-----------|-------|
| Size | 2 KB (2048 bytes, 2K×8) |
| Package | DIP24 |
| Family | NMOS UV-EPROM (Intel 2716 class) |
| Pinout | DIP24_2716 (identical read pinout to Intel 2716) |
| VCC during read | 5V |
| VCC during program | 25V (TMS2516 original — see VPP note) |
| VPP (program) | 25V on pin 21 (same pin as Intel 2716 VPP) |
| Programming pulse | 50 ms per byte (NMOS era, not quick-pulse) |
| Algorithm | 0x0B (EPROM_LEGACY — the existing NMOS 2716/2732 handler) |
| Chip ID | None — no electronic ID (like all 2716-class chips; chip_id_value = 0x00000000) |
| Erase | UV light only (no electrical erase) |

**2716 compatibility and differences:**
- The 2516 (TI TMS2516) is a 2Kx8 (2048-byte) NMOS EPROM. The Intel 2716 is also 2Kx8. They share the DIP24 physical package and the same A0–A10 / D0–D7 / CE / OE pin assignments.
- **Key difference from Intel 2716:** The TI TMS2516 requires VCC=25V during programming (VCC and VPP both elevated), whereas the Intel 2716 requires VCC=5V/6.5V and VPP=25V separately. This means the TMS2516 programming is nominally more demanding — both supplies must reach 25V.
- However, for RURP/Firestarter purposes: the 0x0B handler already uses the direct VPE path (CTRL_VPP_REGULATOR_ENABLE, no dropping resistor) and the VPE rail runs at ~22.4V DMM / 23.9V firmware readout. The TMS2516 at ~22.4V VPE on both VCC-prog and VPP is an under-voltage condition (~90% of 25V), consistent with the Phase 79 best-effort NMOS graduation approach.
- **Pin 21 = VPP / /PGM:** On the 2716, pin 21 is VPP (programming supply). On the TMS2516, pin 21 is also VPP. The firmware's 0x0B handler applies VPE to the VPP pin (CTRL_VPE_ENABLE), which is already routed to pin 21 in DIP24_2716 per pinouts.json.

**What a defensible DB entry should record:**

```json
{
  "electrical": {
    "pin_count": 24,
    "size_bytes": 2048,
    "type": "UV-EPROM",
    "vcc": "5V",
    "vdd": "5V",
    "vpp": "25V",
    "vpp_mv": 25000
  },
  "part_number": "TMS2516",
  "pinout": "DIP24_2716",
  "programming": {
    "algorithm": 11,
    "chip_id_check": false,
    "chip_id_value": "0x00000000",
    "pulse_duration": "500 us"
  },
  "support_status": "supported"
}
```

**Rationale for each field:**
- `vpp_mv: 25000`: The TMS2516 nominally requires 25V. Consistent with the 4 NMOS chips graduated in Phase 79 (INTEL M2716 etc. all at vpp_mv=25000). The `RURP_VPP_CEILING_MV` is now 25000; the chip fits within the ceiling.
- `algorithm: 11` (0x0B): EPROM_LEGACY. This is the correct handler — it uses direct VPE path, 500 µs pulse (the 0x0B default in `configure_eprom`). The TMS2516 datasheet specifies 50 ms pulses (NMOS era), but the Intel 2716 and AM2716 also specify 50 ms nominal and the DB records 500 µs for all 0x0B chips. The 500 µs DB value reflects the empirically-effective quick-pulse timing used by minipro for 2716-class chips.
- `pulse_duration: "500 us"`: Matches all other DIP24_2716 / 0x0B chips in the DB (AM2716: 500 µs, INTEL M2716: 500 µs).
- `chip_id_check: false`, `chip_id_value: "0x00000000"`: NMOS 2716-class chips have no electronic ID.
- `pinout: "DIP24_2716"`: Verified — TMS2516 and Intel 2716 share the same DIP24 JEDEC pinout (VPP=pin 21, OE=pin 20, CE=pin 18, address A0–A10 on pins 8,7,6,5,4,3,2,1,23,22,19, data D0–D7 on pins 9–11,13–17).
- `support_status: "supported"`: Consistent with the Phase 79 NMOS ceiling raise; VPP=25V ≤ RURP_VPP_CEILING_MV=25000.

**Tie to FUT-03 / Phase 79 deferred proof:**
Phase 79 (NMOS-03) deferred the definitive Leonardo write+SHA bench proof of the 4 graduated NMOS chips (INTEL M2716 etc.) for lack of a chip on hand. The TMS2516 bench run in v1.15 doubles as this proof: it demonstrates the 0x0B handler programs a DIP24_2716 NMOS EPROM at ~22.4V VPE. The TMS2516 is electrically equivalent to INTEL M2716 for this purpose.

**Erase behavior:** UV light only — no electrical erase. The operator has no UV eraser. Apply the UV-EPROM no-eraser methodology (Section 2).

---

## Section 2: UV-EPROM No-Eraser Test Methodology

Applies to: ST M27C512, AM27C020, TMS2516 (the three UV-EPROMs in the inventory).

### Electrical Reasoning

A UV-EPROM cell is a floating-gate MOSFET. The erased (UV-bleached) state is a floating gate with no stored charge — the cell reads as logic 1 (0xFF when all 8 bits = 1). Programming drives electrons onto the floating gate via hot-carrier injection during the VPP pulse, which latches the cell to logic 0. The cell **cannot be returned to logic 1 electrically** — only UV photons with sufficient energy (~4 eV, 253 nm wavelength) can remove the trapped charge.

Consequence: **Once a bit is written to 0, it stays 0 permanently without UV erase.** Writing a file that sets a bit from 1 to 0 is irreversible without a UV eraser. Writing a file that requires setting a bit from 0 to 1 is electrically impossible (the write attempt produces a verify mismatch and the firmware retries up to 20× before giving up — it cannot force a 0-bit to 1).

The safe methodology must therefore avoid any operation that requires a 0→1 transition on a chip that is not blank.

### Phase A: Non-Destructive Read + Blank Check (Zero Chips Consumed)

This phase validates the read path, DB decode (pinout, size, VPP-for-read), and address/data wiring without spending any programming budget. No VPP is applied during read.

**Procedure:**
1. Seat chip in socket. Verify board identity (`controller:` check).
2. `firestarter read -e <CHIP_NAME> candidate.bin` — read the full chip contents.
3. Compute SHA: `sha256sum candidate.bin`.
4. If SHA == SHA-of-all-FF (the all-0xFF blank pattern), the chip is blank → proceed to Phase B.
5. If SHA != SHA-of-all-FF, the chip is partially or fully programmed → proceed to Phase C.

**What this validates even if the chip is programmed:**
- Read path correct (no 0xFF drift from the v1.9 read bug — Leonardo on Rev 2.0 is the trustworthy board).
- DB pinout correct (if the read size is wrong, it crashes or returns wrong count; if the pinout is wrong, data is garbage).
- VPP-for-read is 0V (UV-EPROMs read at standard 5V with VPP deasserted) — a read operation with correct data confirms the chip is not being damaged.
- Chip is seated correctly (wrong insertion reads all-FF or all-00, both distinct from a valid programmed pattern).

**No chips are consumed** — reading a UV-EPROM is non-destructive by definition.

### Phase B: Full Write if Blank

If the chip reads all-0xFF (blank), full programming is safe. All 0→1 transitions are impossible from a fully-blank start point; every programmed bit is 1→0 which is the correct direction.

**Procedure:**
1. `firestarter write -b -e <CHIP_NAME> image.bin`
   - `-b` skips the redundant blank check (already confirmed blank in Phase A, saves time).
   - No erase flag needed — `FLAG_CAN_ERASE` is NOT set for UV-EPROM (electrical.type != "EEPROM").
   - The firmware will NOT auto-erase (correct behavior for UV-EPROM).
2. `firestarter verify -e <CHIP_NAME> image.bin` exits 0.
3. Record SHA of image.bin as the expected value.

**Firmware flags for UV-EPROM write:**
- `FLAG_CAN_ERASE` NOT set — firmware will skip `eprom_internal_erase`.
- `FLAG_SKIP_BLANK_CHECK` (the `-b` flag) — skip redundant blank check that was already done externally.
- `FLAG_SKIP_ERASE` is irrelevant since `FLAG_CAN_ERASE` is not set.

**Verification expectation:** `firestarter verify -e <CHIP_NAME> image.bin` reads the chip and compares byte-by-byte to image.bin. Every written byte must match. Wrong-file verify must exit non-zero (negative oracle check).

### Phase C: AND-Mask / All-0x00 Bit-Subset Write if Already Programmed

If the chip is not blank (Phase A found programmed content), a full overwrite is impossible without UV erase. However, a carefully constructed AND-mask write can still validate the write path and verify round-trip — using only 1→0 transitions.

**The key electrical insight:** In a UV-EPROM, writing 0x00 to any address that already contains any pattern is always valid — 0x00 has all 8 bits = 0, and every bit in the existing pattern (whether 0 or 1) can be safely AND-ed to reach 0x00. Writing 0x00 to a cell that already contains 0x00 is a no-op (already programmed; the firmware's retry loop exits immediately on the first verify). Writing 0x00 to a cell that contains any non-zero value lowers bits 1→0 — legal without erase.

**Procedure:**
1. Construct an all-0x00 test image of the correct size (`python3 -c "import sys; sys.stdout.buffer.write(b'\x00' * SIZE)" > zeros.bin`).
2. `firestarter write -b -e <CHIP_NAME> zeros.bin` — write all zeros to the chip.
   - `-b` to skip blank check (chip is NOT blank — the blank check would fail and abort).
   - No erase attempted (UV-EPROM, FLAG_CAN_ERASE not set).
   - The firmware programs each byte: for bytes already 0x00, verify passes immediately (no pulse needed). For bytes that were non-zero, the firmware applies VPP pulses driving bits 1→0 until the byte reads 0x00.
3. `firestarter read -e <CHIP_NAME> after_zeros.bin`
4. SHA of after_zeros.bin must equal SHA-of-all-zeros.
5. `firestarter verify -e <CHIP_NAME> zeros.bin` exits 0.

**Why this works without an eraser:** Every existing cell state (0x00–0xFF) can be reached by 0x00 without requiring any 0→1 transition. The AND of any value with 0x00 is always 0x00. The firmware's verify-per-byte loop will find either (a) the cell already reads 0x00 (no pulse needed, instant pass), or (b) the cell reads non-zero (pulses applied until 0x00 is verified, 20 retries max).

**Interpretation of results:**
- If the write completes and verify passes: the write path (VPP delivery, address/data bus, CE pulse, verify loop) is functionally correct. The chip has consumed its remaining programming budget on these bytes.
- If the write fails (retry exhaustion on a byte): indicates either a VPP issue (check ADC readback), a pinout mismatch, or a defective cell. RCA from the error log.

**Chip is now permanently all-0x00** — it cannot be returned to a readable state for its original content without UV erase. Operator must decide at Phase A whether to spend this chip.

### Flags Summary for UV-EPROM Operations

| Operation | Flag | Reason |
|-----------|------|--------|
| Read (Phase A) | (none special) | Normal read, no VPP |
| Write blank chip (Phase B) | `-b` (FLAG_SKIP_BLANK_CHECK) | Already confirmed blank; avoid redundant check |
| Write non-blank chip (Phase C) | `-b` (FLAG_SKIP_BLANK_CHECK) | Chip IS non-blank; blank check would fail and abort |
| Never | auto-erase | UV-EPROM electrical.type != "EEPROM" → FLAG_CAN_ERASE not set |
| Never | force-erase command | No electrical erase possible; command is a no-op or error |

### Which Chips This Applies To

| Chip | UV-EPROM? | No-eraser protocol needed? |
|------|-----------|---------------------------|
| W27C512 | No (EEPROM, electrically erasable) | No |
| W27E512 | No (EEPROM, electrically erasable) | No |
| SST27SF512 | No (EEPROM, electrically erasable) | No |
| ST M27C512 | YES | YES |
| W27E040 | No (EEPROM, electrically erasable) | No |
| AM27C020 | YES | YES |
| SST39SF040 | No (Flash/EEPROM, chip-erase) | No |
| W29C020 | No (Flash/EEPROM, chip-erase) | No |
| W29C040 | No (Flash/EEPROM, chip-erase) | No |
| FM1608 | No (FRAM, overwrite-in-place) | No |
| TMS2516 | YES | YES |

---

## Table Stakes

Features users/phases expect. Missing = milestone is incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Non-destructive read + blank-check for every chip before first write | Validates read path/decode with zero chips consumed; mandatory for UV-EPROMs | Low | Run `firestarter read` + SHA check as first action per chip |
| Full write→read→verify with SHA match for all 8 electrically-rewritable chips | Proves `supported` claim on real silicon | Medium | W27C512 already proven (Phase 77); 7 others are open |
| UV-EPROM no-eraser protocol executed for M27C512, AM27C020, TMS2516 | Operator has no UV eraser; protocol prevents irreversible chip damage | Medium | See Section 2; read + blank-check FIRST before any spend decision |
| Per-chip evidence record (pass/fail/SHA) | Reusable validation artifact; required for milestone audit | Low | Record: chip name, date, board+shield, image SHA, read SHA, verdict |
| 2516 DB entry authored and validated on silicon | Only graduation candidate; FUT-03 deferred proof | High | New DB entry + bench write+SHA on ~22.4V VPE rail |
| `dev validate-family` Tier-3 / `write_test.sh` reuse | No new harness; reuse existing tools | Low | Established in v1.13; Leonardo-only-PASS oracle |
| FLAG_CAN_ERASE correctness for Flash/EEPROM type | W29C020/W29C040 need erase before write | Medium | Verify database.py Phase-77 logic covers "Flash/EEPROM" not just "EEPROM" |
| DB decode verification (pinout, VPP, size, type match) | Each bench run is a decode-correctness test | Low | Flag any chip where read size / VPP ADC / chip_id diverges from DB |

---

## Differentiators

Features that make this milestone more than a checkbox exercise.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| TMS2516 graduation = FUT-03 proof | The 2516 bench run simultaneously closes the Phase 79 deferred best-effort NMOS proof (no other NMOS chip is on hand) | High | First new NMOS silicon proof since NMOS graduation was software-only in Phase 79 |
| AND-mask write for non-blank UV-EPROMs | Recovers test coverage from chips that were already programmed; write-path validation without needing a blank chip | Medium | Electrically sound; fully verifiable without eraser |
| Cross-family erase-path consistency check | Confirms FLAG_CAN_ERASE applies uniformly to EEPROM + Flash/EEPROM types; surfaces any gap between Phase 77 logic and flash4 handler | Medium | Likely to surface the W29C020/W29C040 gap (see Table Stakes row) |
| Chip ID check as a preliminary pre-write gate | Running `firestarter check-chip-id` before write confirms the seated chip matches the DB entry; catches wrong-chip-in-socket before VPP is applied | Low | Available for all chips with chip_id_check: true |

---

## Anti-Features

Features to explicitly NOT build or attempt.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Attempting to UV-erase any chip (M27C512, AM27C020, 2516) | Operator has no UV eraser; claiming UV erase is possible wastes phase time and plans | Use the no-eraser protocol (Section 2); never plan a "UV erase" step |
| Using Uno or uno328pb for any write/program/verify in this milestone | v1.9 read bug corrupts the oracle on non-Leonardo boards; uno328pb has program-brownout issue | Lock all write/verify to Leonardo + Rev 2.0; Uno is read-only at best |
| Trusting a non-Leonardo read as an oracle | Rev 0 read-path fault, uno328pb instability | Use Leonardo for all verdict reads |
| Writing a non-blank UV-EPROM with a non-AND-mask image | Any byte requiring a 0→1 transition on a pre-programmed bit will fail with 20 retries, exhausting the cell | Use all-0x00 AND-mask (Phase C) or skip the chip |
| Graduating a chip to `supported` without a bench SHA match | `support_status: supported` is a warranty; software-only changes do not count | Bench evidence (write+read+SHA) is mandatory per standing graduation discipline |
| Re-opening the FM1608 configure_sram correctness question | FIX-01 closed with N=2 bench evidence in Phase 73 | FM1608 bench pass in v1.15 is a re-confirmation, not a re-investigation |
| Running bench tests on Rev 0 shield | Rev 0 read-path fault makes reads unreliable | Rev 2.0 only for v1.15 bench |
| Attempting erase on SST39SF040 / W29C020 / W29C040 without first reading the chip | Flash chips can hold real data; a "test write" that triggers chip erase destroys existing content | Read chip first, record SHA, then decide whether to write |

---

## Feature Dependencies

```
Phase A (read + blank check) for each chip
  → Gate for Phase B (write if blank) or Phase C (AND-mask if programmed)
  → No chip skips Phase A

FLAG_CAN_ERASE flash4 correctness check (database.py)
  → Gate for W29C020 / W29C040 write commands
  → If not set for Flash/EEPROM, write will hit blank-check failure on a non-blank chip

TMS2516 DB entry authored
  → Gate for TMS2516 Phase A read (chip must be in DB to use firestarter commands)
  → Gate for TMS2516 graduation

TMS2516 bench SHA match
  → FUT-03 closure (Phase 79 deferred NMOS write proof)
  → TMS2516 support_status remains "supported" regardless (Phase 79 already graduated it on paper)

W27C512 bench (already proven in Phase 77)
  → Proxy for W27E512 (same DB entry, same handler)
  → Establishes write→erase→program→verify baseline for all 0x07 EEPROM chips
```

---

## MVP Recommendation

The minimum v1.15 that meets the milestone goal is:

**Priority 1 (must do):**
1. TMS2516 DB entry + Phase A read + Phase B/C write — the one genuine graduation candidate; closes FUT-03.
2. Phase A reads for all 10 remaining chips — validates read path + decode for each.

**Priority 2 (should do, silicon proof of `supported` claims):**
3. Full write→read→verify for W27E512, SST27SF512 (unproven 0x07 EEPROMs).
4. Full write→read→verify for W27E040 (unproven 0x08 EEPROM).
5. Full write→read→verify for W29C020 (unproven flash4; W29C040 proven in Phase 74).
6. Full write→read→verify for AM27C020 (UV-EPROM; blank check first, then Section 2 protocol).
7. Full write→read→verify for ST M27C512 (UV-EPROM; blank check first, then Section 2 protocol).

**Priority 3 (nice to have, already proven):**
8. FM1608 re-confirmation (Phase 73 proven; run once to confirm the COBS transport + Phase 77 changes haven't regressed).
9. SST39SF040 re-confirmation (Phase 74 proven).
10. W29C040 re-confirmation (Phase 74 proven after fix).

**Defer if blocked:**
- TMS2516 bench: If the chip is not readable (wrong pinout, no response), do NOT proceed to write. Debug Phase A first.
- AM27C020 / M27C512 write: If both chips are already programmed (Phase A finds non-0xFF), use Phase C (AND-mask) or defer write spend — reading both is still valuable even without a write.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| TMS2516 DB entry | Pulse duration: DB should use 500 µs (matching other 0x0B chips); TMS2516 datasheet says 50 ms but minipro empirically uses 500 µs for 2716-class | Use 500 µs, matching AM2716/INTEL M2716 entries; escalate to longer pulse only if 500 µs fails |
| TMS2516 bench write | Under-voltage: VPE=22.4V is ~90% of 25V; firmware will warn-and-proceed (MSG_WARN_VPP_LOW); not an error | Accept warning; record VPE voltage in bench artifact; SHA match is the pass criterion |
| TMS2516 VCC during program | TMS2516 nominally requires VCC=25V during programming, not just VPP=25V; RURP applies VCC=5V throughout | Best-effort: the 0x0B handler has no mechanism to raise VCC; program at 5V VCC with 22.4V VPE; document if write fails |
| W27E040 erase rail | Erase path uses raw VPE (~12–14V on Rev 2.0) — must be in the W27E040 spec range (12V min) | Chip-OUT DMM measurement of VPE rail before seating; target 12–14V |
| W29C020 / W29C040 FLAG_CAN_ERASE | If FLAG_CAN_ERASE is not set for "Flash/EEPROM" type, write on a non-blank chip will fail at blank-check | Check database.py before bench; if gap, use `-b` + manual pre-erase command; fix the code |
| SST27SF512 chip ID | Chip ID 0x0000BFA4 must respond correctly; SST27SF512 pre-2000 chips sometimes return 0xBFxx with wrong device byte | Run `firestarter check-chip-id` first; if mismatch, confirm with `--force` |
| UV-EPROM spend decision | A blank M27C512 or AM27C020 cannot be re-blanked without UV — once written, it is permanently written | Make the blank-vs-programmed read decision BEFORE any write command; record the decision in the bench artifact |
| All chips | Port identity: /dev/ttyACM* numbers reshuffle on USB unplug/replug | Verify `controller:` identity at every task start, not just session start |
| W27C512 (proven) | Re-run may surface a regression if Phase 77 or Phase 79 changes introduced a write-path defect | Include at least one W27C512 re-run as a regression anchor; it is the most-proven chip in the inventory |

---

## Sources

All findings are grounded in required reading and the chip_database.json analysis above. No external web search required for the DB-grounded chip facts.

- `.planning/PROJECT.md §Current Milestone: v1.15` — scope, board/shield lock, UV-EPROM constraint
- `.planning/MILESTONES.md §v1.14, §v1.13` — prior bench evidence, erase path decisions, Phase 79 NMOS
- `firestarter_app/firestarter/data/chip_database.json` — all per-chip DB entries (queried directly)
- `firestarter_app/firestarter/data/pinouts.json` — DIP24_2716, DIP28_27512, DIP32_STD, DIP32_SST39SF040
- `firestarter/src/proms/eprom.cpp` — `configure_eprom`, `eprom_write_init`, `eprom_internal_erase`, `eprom_check_vpp` (FLAG_CAN_ERASE gating, VPP path, under-voltage warn-and-proceed logic)
- `firestarter/src/proms/flash_type_3.cpp` — `configure_flash3`, `flash3_write_init` (FLAG_CAN_ERASE + erase-once guard)
- `firestarter/src/proms/flash_type_4.cpp` — `configure_flash4`, `flash4_write_init`, `flash4_page_size` (SDP per-page unlock, data-driven page size)
- `firestarter/CLAUDE.md` — dispatch table, algorithm handler mapping, control register bit definitions
- `.planning/research/_archive-pre-v1.15/CHIP_FAMILIES.md` — 2716 pinout, NMOS programming algorithm detail, pulse timing
- `.planning/research/_archive-pre-v1.15/FEATURES.md` — v1.14 feature landscape (erase path, NMOS ceiling, FLAG_CAN_ERASE rationale)
- `project_phase79_gate_reexamined.md` (memory) — VPE=22.4V DMM / 23.9V fw, Phase 79 NMOS best-effort graduation, FUT-03 deferred proof
- `project_phase77_shipped.md` (memory) — FLAG_CAN_ERASE from electrical.type == "EEPROM", W27C512 bench-proven write→erase→program→verify

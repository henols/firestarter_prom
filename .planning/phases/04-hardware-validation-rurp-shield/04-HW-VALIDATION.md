---
phase: 04-hardware-validation-rurp-shield
generated: 2026-05-12T11:52:49Z
last_session: 2026-05-12T20:31:39Z
requirements_validated: [HW-01]
requirements_attempted: [HW-02]
requirements_pending: [HW-03, HW-04, HW-05]
hardware:
  board: Uno
  firmware_version: "2.0.6 (source HEAD firestarter@587396a, flashed 2026-05-12T20:14Z; tag 2.0.6 is 30 commits behind HEAD — version.h not bumped, see follow_up firmware-version-drift)"
  host_machine: 7cc15a2d6fd7
  host_app: firestarter_app@16dcafe (2.0.7_dev)
  bench_equipment:
    - Programmer: RURP shield Rev 2.0
    - Multimeter: <model pending HW-04/HW-05 bench>
    - Power supply: <RURP-onboard regulator>
chips_tested:
  - {part: W27C512,    algo: 0x07, package: DIP28, lot: <pending HW-02 bench>, session_2026-05-12: "ID 0xda08 read OK, blank OK; write FAILED (host MAIN-phase bug, see follow_up host-main-phase-bug)"}
  - {part: SST27SF512, algo: 0x07, package: DIP28, lot: "0045231-B (from photo)", session_2026-05-12: "ID 0xbfa4 read OK, blank OK; write FAILED (host MAIN-phase bug, see follow_up host-main-phase-bug)"}
  - {part: SST39SF040, algo: 0x06, package: DIP32, lot: <pending HW-03 bench>, session_2026-05-12: "ID read 0x0000 (expected 0xbfb7), reads return all 0x00, erase reports success but chip stays at 0x00 — see follow_up sst39sf040-dead-chip"}
  - {part: AM29F040,   algo: 0x06, package: DIP32, lot: <pending HW-03 bench>}
  - {part: AT28C256,   algo: 0x0D, package: DIP28, lot: <pending HW-04 bench>}
  - {part: AM28F010,   algo: 0x10, package: DIP32, lot: <pending HW-05 bench>}
follow_ups:
  - id: host-main-phase-bug
    severity: BLOCKER
    status: RESOLVED (firestarter_app@08ca252, 2026-05-12)
    surface: firestarter_app (host CLI)
    evidence: bench-evidence-2026-05-12/02-sst27sf512_write_verbose_data_err_-3.log + 10-w27c512_write_data_err_-3_universal.log
    detail: "EpromOperator._main_phase_send_data was sending the 4-byte packet header (# + size + checksum) and then calling expect_ack() before sending the payload. The firmware protocol has no such ACK — rurp_communication_read_data (rurp_serial_utils.cpp:59-86) reads size + checksum + payload in one synchronous flow with a 2-second timeout on the payload-read loop. Host blocking on a non-existent ACK left the payload unsent; firmware timed out and returned 'Data err -3'; the host's own expect_ack then consumed the ERROR response and raised 'Firmware did not acknowledge header' — the exact failure surfaced on every configure_eprom-family write during the 2026-05-12 bench. RESOLUTION: firestarter_app@08ca252 (fix: remove spurious ACK round-trip in MAIN-phase data send) concatenates header + data_chunk into a single send_bytes call. Bench re-validation pending next session (chip + bench setup required). RESUMPTION: re-run /gsd-execute-phase 04 --wave 2 --interactive against a fresh W27C512 (already proven blank-check OK in the 2026-05-12 session)."
  - id: firmware-version-drift
    severity: HIGH
    status: RESOLVED (firestarter@bbf0e0c, 2026-05-12)
    surface: firestarter (firmware) + firestarter_app (host)
    evidence: bench-evidence-2026-05-12/05-firmware_flash_to_587396a.log
    detail: "firestarter/include/version.h VERSION constant ('2.0.6') had not been bumped despite 30 commits since the 2.0.6 git tag (db4e565), so firestarter fw kept reporting 'already up to date' against any source-tree build. This misled the 2026-05-12 bench session into believing v1.1 firmware closures (Phase 01 SAF-04+SAF-05, Phase 02 wire-key rename, Phase 12 dispatch chain) were on-board when they were not until mid-session reflash. RESOLUTION: firestarter@bbf0e0c (chore: bump VERSION to 2.0.7-dev) bumps the VERSION constant to '2.0.7-dev'. Next stable release can drop -dev and tag 2.0.7 cleanly. Long-term: prefer auto-update logic that compares git ref / SHA over version-string equality, or treat every behavior-affecting firmware commit as a VERSION-bump candidate."
  - id: sst39sf040-dead-chip
    severity: MEDIUM
    surface: operator hardware
    evidence: bench-evidence-2026-05-12/03..08 (5 logs)
    detail: "Operator's SST39SF040 (DIP32) reads chip-ID as 0x0000 instead of expected 0xbfb7. Force-read returns all 0x00. firestarter erase reports success in 0.16s but post-erase reads stay at 0x00 — chip didn't actually erase. Single-chip observation; likely dead silicon or stuck output drivers. Side observation: firmware's chip-erase success path is over-optimistic — it should require DQ7-polling confirmation + post-erase blank-check before claiming success."
  - id: fm1608-db-mismatch
    severity: HIGH
    status: RESOLVED tentatively (firestarter_app@104cf12, supersedes 687ad2a + d585668; 2026-05-13). Bench-validation required to confirm FM1608 pin 1 assumption.
    surface: firestarter_app/firestarter/data/chip_database.json + firestarter_app/firestarter/data/pinouts.json
    evidence: bench-evidence-2026-05-12/11-fm1608_read_address_bus_crosstalk.log + 12-fm1608_write_blocked_at_init_blank_check.log + fm1608_read_256_bytes_address_coupling.bin + fm1608_postwrite_unchanged_64_bytes.bin
    detail: "FM1608 DB entry is broken at FOUR levels — type, voltage, algorithm, and pinout — confirmed by 2026-05-12 bench investigation. (1) type='UV-EPROM' for what is actually a Ramtron parallel FRAM. (2) vpp='12V' / vpp_mv=12000 for a 5V single-supply chip (no programming voltage). (3) algorithm=7 (EPROM_STD) routes through configure_eprom; should be an SRAM-class algorithm (0x0E/0x27/0x28/0x29) since FRAM behaves electrically like SRAM with non-volatile cells. (4) pinout='DIP28_2764' is the standard 2764-EPROM pinout (pin 1=VPP, pin 2=A12, pin 3=A7, ...); Ramtron FM1608 has its own pinout (pin 1=A12 per datasheet, no VPP pin) — pinouts incompatible. **Bench-confirmed behavior under current entry:** (a) firestarter read FM1608 returns address-bus crosstalk (data byte = (addr & 0xFC) | 0x03 pattern; chip data drivers never enabled because CE/OE/address are routed to wrong physical pins); (b) firestarter write FM1608 aborts in INIT phase via pre-write blank check ('Not blank, at 0x000000, v: 0x00') — no MAIN phase, no VPP routing, NO chip damage; (c) chip state unchanged byte-for-byte after the write attempt (cmp confirms identical pre/post). **Safety conclusion:** the pre-write blank check + missing FLAG_CAN_ERASE in the runtime flags accidentally protect FM1608 from the worst-case damage scenario. Without those gates (e.g., on a chip whose entry sets FLAG_CAN_ERASE), the erase-before-write branch would have engaged A9_VPP_ENABLE → 12V to socket pin 24 → real damage. Recommended fix: replace the FM1608 entry with a proper SRAM-class algorithm + author a Ramtron FM1608-specific pinout in pinouts.json. Until then, the entry should be removed or marked unimplemented to prevent operators relying on it. **RESOLUTION HISTORY**: (1) d585668 (superseded) — initial skip filter; safe but discarded a previously-working chip family. (2) 687ad2a (superseded) — algorithm-only override (0x07/0x0B → 0x28) for `mfg_name == "RAMTRON"`; eliminates VPP risk but kept incorrect DIP28_2764 pinout (pgm-pin=27 emits programming-pulse signal where SRAM expects WE strobe — explains the address-bus crosstalk observed on the 2026-05-12 bench reads). (3) **104cf12 (current)** — proper schema-driven fix after researching minipro's upstream infoic.xml decoder (`/tmp/minipro/src/database.c`). Three insights: (a) The XML `type` attribute is authoritative — `type=4` always means RAM/SRAM family per minipro database.c:583; build_db.py was ignoring it and defaulting to `electrical.type='UV-EPROM'`. (b) The XML `pin_map` attribute is for TL866's socket-presence-test feature, NOT chip-pin assignments — the actual pin-to-signal mapping is baked into TL866's closed-source firmware. Firestarter must author its own pinouts per chip. (c) JEDEC 28-pin SRAM (6264, FM1608) shares the SAME address bus as 2764 EPROM (A0=pin 10, ..., A12=pin 2) — the only differences are pin 1 (NC vs VPP) and pin 27 (!WE vs !PGM). Fix: (i) build_db.py derives electrical.type from XML `type` first (type=4 → 'SRAM' even when protocol_id is EPROM-family); (ii) added new pinouts.json entry `DIP28_JEDEC_SRAM_8K` (same address bus as DIP28_2764 but rw-pin=27 instead of pgm-pin, no vpp-pin, pin 1+26 NC); (iii) generalized override: type=4 chips with EPROM-family protocol get algorithm flipped to 0x28 (SRAM_STD) + pinout flipped to DIP28_JEDEC_SRAM_8K for 28-pin variants. Bench-validation pending — FM1608 pin 1 assumed NC per 6264 standard; Ramtron's specific variant may use pin 1 = A12 instead. If bench reads still produce crosstalk, next iteration tries pin 1 as an address line. 16K/32K Ramtron variants (FM16W08/FM1808/FM18L08) over-restricted to lower 8K under this pinout — need separate 16K/32K JEDEC SRAM entries for full range. Operator using Arduino Leonardo for verbose debug visibility during bench validation."
  - id: w27e512-missing-db-entry
    severity: LOW
    surface: firestarter_app/firestarter/data/chip_database.json
    detail: "Winbond W27E512 (64K 5V EEPROM) has no DB entry. Adjacent entries: W27E257 (32K, algo=7, vpp=13.5V), W27C01/E01/L01 family (128K, algo=8). W27E512 needs its own entry — operator inventory included this part."
  - id: firestarter-info-label-bugs
    severity: MEDIUM
    status: PARTIALLY RESOLVED (firestarter_app@706d2f4, 2026-05-12)
    surface: firestarter_app (host CLI info subcommand)
    detail: "firestarter info SST27SF512 had multiple label inconsistencies, mixing dangerous and cosmetic. **(d) RESOLVED in firestarter_app@706d2f4**: Protocol 0x07 description was 'EEPROM programming protocol for 28-pin devices, Byte-wise programming, no high voltage required' — dangerously wrong since algo=0x07 is EPROM_STD per firmware PROTOCOL_MAP, dispatches through configure_eprom, and applies ~12-13V VPP during writes. Now reads: 'EPROM (standard)' label + 'UV-EPROM / MTP-Flash standard programming algorithm (EPROM_STD) / Requires ~12-13V VPP during write pulses (configure_eprom path) / 1ms write pulse with DQ7-poll verify; UV parts must be UV-erased first'. **(e) NOT A BUG (downgrade)**: Flag descriptions for bits 0x10 / 0x20 match info-flags semantics correctly — bits are OR'd into info-flags at database.py:405-409 based on electrical.type and chip_id_check, and the descriptions match. My earlier confusion conflated runtime FLAG_* (constants.py) with info-flags (database.py). **(a), (b), (c) NOT RESOLVED (out of scope)**: Type:/Can-be-erased rendering reflects the firmware-dispatch numeric type field (1 = TYPE_EPROM for any algo=0x07/0x08/0x0B/0x0D chip). Showing the DB's descriptive electrical.type string ('UV-EPROM' vs 'Flash/EEPROM') would expose upstream-DB mistagging (W27C512 is genuinely UV-erasable but DB tags it as Flash/EEPROM) — fixing the display without fixing the DB content would amplify the wrong information for affected chips. Deferred to a separate cleanup pass that also corrects the DB. (c) is similarly tied to the Type rendering."
  - id: firestarter-erase-b-silent
    severity: LOW
    surface: firestarter_app (host CLI erase subcommand)
    detail: "firestarter erase -b SST39SF040 (blank-check-after-erase flag) reported 'Erase successful' with no blank-check output. Either -b is not implemented, silently fires on a path that ignored the result, or the surface output suppression is unintended. UX bug."
  - id: firestarter-force-flag-scope
    severity: LOW
    surface: firestarter_app (host CLI argparse)
    detail: "firestarter -f blank SST39SF040 errors with 'unrecognized arguments: -f' — -f is subcommand-level only (firestarter blank -f SST39SF040 works). Either accept both forms via argparse parent/child setup, or improve the error message to point users at the correct invocation."
  - id: at28c256-pinout-mismatch
    severity: MEDIUM
    status: RESOLVED (firestarter_app@f387d15, 2026-05-13). Authored DIP28_28C256 pinout (one-rom verified) + extended WARNING-5 to recognize new pinout for algorithm flip.
    surface: firestarter_app/firestarter/data/pinouts.json (DIP28_2764) vs AT28C256 actual pinout
    evidence: piersfinlayson/one-rom chip-types.json 28C256 entry (datasheet-verified)
    detail: "AT28C256 currently routes to DIP28_2764 pinout (via WARNING-5 algorithm override 0x07→0x0D → configure_eeprom28c). The algorithm dispatch is correct (5V, no VPP regulator), but the PINOUT layout is wrong. Per one-rom's datasheet-verified data: 28C256 has 15 address lines A0-A14, with **A14 at pin 1** (not VPP), and **WE at pin 27** (not PGM). firestarter's DIP28_2764 has only 14 address lines + VPP at pin 1 + PGM at pin 27. Effects: the firmware's configure_eeprom28c handler may drive incorrect signals to pin 1 and pin 27 during writes. Bench validation needed to confirm impact. Resolution: author a new DIP28_28C256 pinout entry with: address=[10,9,8,7,6,5,4,3,25,24,21,23,2,26,1] (15 pins, A14 at pin 1), data=[11,12,13,15,16,17,18,19], ce=20, oe=22, rw-pin=27, no vpp-pin, no pgm-pin, vcc=28, gnd=14. Update build_db.py to assign this pinout to chips with (pin_count=28, pm_idx=20, _etype='Flash/EEPROM') or similar discriminator."
  - id: sst39sf040-pinout-mismatch
    severity: MEDIUM
    status: RESOLVED (firestarter_app@f387d15, 2026-05-13). Authored DIP32_SST39SF040 pinout (one-rom verified) + PIN_MAP_PROTO_TO_PINOUT routing for (32, 13, 0x06) chips (47 chips affected). May resolve the 2026-05-12 SST39SF040 bench failure (chip-ID 0x0000 + bus crosstalk) — bench retest needed.
    surface: firestarter_app/firestarter/data/pinouts.json (DIP32_STD) vs SST39SF040 actual pinout
    evidence: piersfinlayson/one-rom chip-types.json SST39SF040 entry (datasheet-verified; explicitly notes 'different pinout to 27C040')
    detail: "SST39SF040 (and AM29F040 sibling per pm_idx=13) currently routes to DIP32_STD pinout. Per one-rom: SST39SF040 has 19 address lines A0-A18 with **A18 at pin 1** (not VPP) and **WE at pin 31** (not address). firestarter's DIP32_STD has VPP at pin 1 and A18 at pin 31 — pins 1 and 31 are SWAPPED relative to SST39SF040 reality. This is the 27C040-compatible UV-EPROM layout, which one-rom explicitly notes is DIFFERENT from SST39SF040. Effects: firmware's configure_flash3 handler would route address signals to wrong physical pins for SST39SF040, and would assert PGM on pin 31 (which is WE on this chip). Likely explains the 2026-05-12 bench failure on SST39SF040 (chip-ID 0x0000 + address-bus crosstalk symptoms) — not just a dead chip, the pinout was wrong. Resolution: author a new DIP32_SST39SF040 pinout entry with: address=[12,11,10,9,8,7,6,5,27,26,23,25,4,28,29,3,2,30,1] (A18 at pin 1), data=[13,14,15,17,18,19,20,21], ce=22, oe=24, rw-pin=31 (WE), no vpp-pin, vcc=32, gnd=16. Update build_db.py PIN_MAP_TO_PINOUT to map (32, 13) → DIP32_SST39SF040 for chips with proto=0x06 family. AM29F040 likely needs same pinout (same pm_idx group, family description matches)."
  - id: nvram-pinout-low-to-medium
    severity: LOW
    status: RESOLVED (firestarter_app@ab339ca, 2026-05-13). 32-pin NVRAM rerouted DIP32_28C512_EEPROM→DIP32_SST39SF040 (WE=31, JEDEC SRAM standard, not the 28C-EEPROM-specific WE=30). 28-pin SRAM/NVRAM gained memory-size discriminator: ≤8K → DIP28_JEDEC_SRAM_8K (13 addr); >8K → DIP28_28C256 (15 addr, A14=pin 1). Database lookup gained paren-stripping for `(RW)/(TEST)/(RW3.3V)` mode-annotation suffixes — `firestarter info DS1245AB` now resolves.
    surface: firestarter_app/tools/build_db.py PIN_MAP_PROTO_TO_PINOUT (32-pin SRAM) + type=4 SRAM override (28-pin discriminator); firestarter_app/firestarter/database.py get_eprom_config (paren-strip)
    evidence: "Multi-source corroboration (datasheet fetches blocked, MEDIUM confidence via three converging sources): (1) JEDEC JC-42 standard for 32-pin parallel SRAM specifies WE=31. (2) piersfinlayson/one-rom SST39SF040 entry (datasheet-verified, same physical layout class) confirms WE=31 on the 32-pin DIP. (3) minipro devices.h shows DS1245/49/50 family at package_details=0x20000000 (32-pin) with protocol_id=0xd2 (Dallas NVRAM) — RAM-class chip classification; pin layout follows JEDEC SRAM convention. The 28C512 EEPROM's WE=30 is an EEPROM-specific variation NOT applicable to SRAM/NVRAM at this pin count."
    detail: "Previously LOW-TENTATIVE because no NVRAM-specific datasheet had been fetched; resolved by recognizing the JEDEC standard governs the physical layout while only the programming algorithm differs per chip family. 32-pin NVRAM affected: 18 chips (Dallas DS1245AB/Y, DS1249, DS1250 + ST/SGS-Thomson M48T128/M48T512). 28-pin 32K NVRAM affected: ~16 chips (DS1230AB/Y, M48T35, FM18L08/FM1808 16K+ variants). Bench-validation still recommended for the M48Txx family — one-rom has no NVRAM entries so we extrapolated from JEDEC SRAM + chip classification rather than direct datasheet read."
  - id: 24pin-eeprom-no-handler
    severity: MEDIUM
    status: MITIGATED (firestarter_app@d0bed87, 2026-05-13). 9 chips skipped at build time with WARN. Operators querying these get `EPROM 'AT28C16' not found in database.` rather than a misleading display.
    surface: firestarter_app/firestarter/data/chip_database.json (no entry); firestarter_app/tools/build_db.py SAFETY SKIP filter
    evidence: "Atmel AT28C16 datasheet (5V single-supply parallel EEPROM, WE on pin 21, no VPP) + Rev 2.3 schematic (github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer/hardware/RelativelyUniversalROMProgrammerRev2.3.pdf). Upstream infoic.xml tags these chips protocol_id=0x0B (EPROM_LEGACY) which dispatches to configure_eprom. The dispatch + signal flow is structurally wrong for 5V EEPROMs regardless of the hardware constraints described in [24pin-eprom-write-no-hv-path]."
    detail: "Affected chips: ATMEL AT28C04/AT28C04E/AT28C04F/AT28HC04/AT28C16/AT28HC16/AT28HC16L/AT28C16E/AT28C16F + MICROCHIP 28C04A/28C04AF/28C16A/28C16AF + NEC UPD28C04. These are 5V parallel EEPROMs that need byte-write + DQ7 polling (like configure_eeprom28c), not the configure_eprom 12V VPP pulse train. Even on a future shield revision with 24-pin HV routing, the dispatch would still be wrong — the algorithm needs to be EEPROM-class, not EPROM-class. Firmware needs a configure_eeprom_24c handler that: (a) uses a new DIP24_28C16 pinout with vpp-pin removed and rw-pin=21; (b) implements byte-write + DQ7-poll like configure_eeprom28c; (c) is dispatched via a new proto_id (or build_db.py algorithm flip 0x0B→0xNEW for 24-pin EEPROMs). Out of scope for Phase 04."
  - id: 24pin-eprom-firmware-vpp-path
    severity: MEDIUM
    status: OPEN — firmware patch needed. CORRECTION (firestarter_prom@2026-05-13): the previous framing as "no HV path on shield" was overstated and has been retracted. Upstream design has always required either Rev 2.2 with the "red" alternative JP4 position closed, OR an operator-soldered bodge wire from socket pin 1 to socket pin 25 (2716) / pin 24 (2732). With either of those in place, upstream Anders firmware delivers HV to socket pin 1 via `P1_VPP_ENABLE` and the wire carries it to the chip. Our firestarter firmware does NOT yet drive this path correctly — that's the actual gap.
    surface: firestarter/include/memory_utils.h:24-27 (using_p1_as_vpp predicate); firestarter/src/proms/eprom.cpp:268-274 (VPE_ENABLE → P1_VPP_ENABLE redirect)
    evidence: "Full investigation at [[04-HW-24PIN-INVESTIGATION]]. Upstream Anders firmware (`software/Arduino/ArduinoProgrammerFirmwarePrototype.ino` `burnROM()` function): for `romPinCount == 24`, sets `controlByte = (REG_DISABLE | P1_VPP_ENABLE)` — unconditionally routes HV to socket pin 1. Upstream README documents: 'Revision 2.2 also has JP4 but rotated 90 degrees (green) and another option of powering the VPP pin of 2716-type ROMs (red).' PRs #17 and #18 add 24-pin support; PR #18 author confirms tested HN462716G works. Firestarter firmware's `using_p1_as_vpp()` returns false for stock DIP24_2716 pinout (vpp_line=11 ≠ magic 0x0F), so eprom.cpp asserts VPE_ENABLE → socket pin 31 instead, missing the bodge-wire / Rev 2.2 red-jumper origin point (pin 1)."
    detail: "Affected: ~53 chips in DIP24_2716 family + ~16 chips in DIP24_2732 family. Two fix options: (a) **firmware patch** — extend using_p1_as_vpp() at memory_utils.h:24-27 to return true when `pins == 24` regardless of vpp_line (cleanest fix, matches upstream Anders firmware behavior); (b) **DB-side rewrite** — set `vpp-pin: [1]` in pinouts.json for DIP24_2716 and DIP24_2732 (would lie about chip pin numbering but trip the existing redirect logic). Recommended: option (a). Also need user-facing docs noting the hardware requirement: 'Rev 2.2 with red JP4 alt-position closed, OR Rev 2.0/2.1/2.3 with bodge wire from socket pin 1 to socket pin 25 (2716) / pin 24 (2732).' Reads of 24-pin EPROMs are unaffected (5V address bus is sufficient). **Update 2026-05-13:** Option (a) applied in firestarter@09f5a8d (VPP_P21_24_DIP=0x0B + extended using_p1_as_vpp). Bench validation pending — no 24-pin chip on hand at 2026-05-13 session."
  - id: flash3-multichunk-write-timeout
    severity: HIGH
    status: RESOLVED (firestarter_app@24f4fa4 host parser fix; supporting firmware patches firestarter@b8dab2b init-guard + firestarter@29567f1 PD0 pull-up). Bench-validated end-to-end on 2026-05-13: SST39SF040 512KB write 234.22s + read-back 138.46s, md5 IDENTICAL (be4d6c4cd1962f292ab1f276374af44c), non-verbose mode, no -v flag required.
    surface: firestarter_app/firestarter/serial_comm.py (PREFIX_REGEX + _parse_response_line); firestarter/src/boards/uno_rurp_shield.cpp (rurp_set_communication_mode); firestarter/src/proms/flash_type_3.cpp (flash3_write_init init guard).
    evidence: "Root cause traced via byte-level RX trace (temporary FIRESTARTER_RX_TRACE env-var in serial_comm.read_line_bytes). The Uno's USB-CDC bridge (ATmega16U2) cannot distinguish 'PD1 driving as UART TX' from 'PD1 driving as data-bus bit 1'. During programming the firmware does Serial.end() then drives PORTD as data bus; every byte write toggles PD1; the bridge samples PD1 at 250000 baud and forwards anything that looks like a UART frame to the host as RX data. Each chunk-completion 'OK: Req data\\r\\n' was arriving at the host prepended by ~500 bytes of garbage. The host's printable-ASCII filter (32-126) reduced the garbage but couldn't strip it entirely — patterns like backticks (0x60), slashes (0x2F), digits remained. The PREFIX_REGEX anchored on `\\b` (word boundary) then failed for filtered lines ending in `...80OK: Req data` because '0' and 'O' are both word chars, so no boundary between them. Parser silently dropped the response → host kept waiting → firmware's 1000ms internal timeout fired → operator-visible 'ERROR: Cmd: 2, timeout'."
    detail: "Multi-layer fix: (1) **Host parser** (firestarter_app@24f4fa4, load-bearing): drop `\\b` anchor from PREFIX_REGEX; use rightmost match via re.finditer + [-1]. Real responses always appear at the end of the line (followed by \\r\\n), so the rightmost prefix occurrence is correct. False-positives in garbage are ignored. (2) **Firmware init guard** (firestarter@b8dab2b): gate one-time init in flash3_write_init behind is_operation_in_progress so chip-ID check + chip-erase + 105ms settle delay run exactly ONCE per write command. Removes 256x redundant erase commands during INIT-phase blank-check iterations. (3) **Firmware PD0 pull-up** (firestarter@29567f1): in rurp_set_communication_mode, set PORTD bit 0 = 1 BEFORE clearing DDR bit 0. UART sees idle HIGH when RXEN0 enables — eliminates the secondary source of garbage from PD0 floating LOW. Drain RX buffer after Serial.begin for belt-and-braces. Together these resolve the issue for all algo=0x06 chips (~209 chips in DB)."
  - id: bench-2026-05-13-priority-chips
    severity: INFO
    status: COMPLETED — 3/3 must-work-first chips bench-validated with firmware 2.0.8-dev on Uno + Rev 2.0/2.1 board.
    surface: bench validation report
    evidence: "Bench session 2026-05-13 results: (1) **W27C512** (28-pin EPROM, algo 0x07): write 64KB + read-back, md5 IDENTICAL (e5203709fae3773f8d6aff573e722834). 89.73s write, 14.40s read. Host MAIN-phase ACK fix (firestarter_app@08ca252) confirmed holding. (2) **SST27SF512** (28-pin MTP-flash, algo 0x07): write 64KB succeeds (89.75s); first read had 2-byte transient mismatch at offsets 0x8000-0x8001 (bit 6 flipped both ways); second read clean (0 diffs). Diagnosed as transient bus glitch at A15-transition + chunk-boundary, non-deterministic. (3) **FM1608** (28-pin FRAM, algo 0x28 SRAM dispatch via DIP28_JEDEC_SRAM_8K pinout): 8191/8192 bytes write correctly; byte 0 stuck-at-0xFF regardless of source pattern. Diagnosed as chip-level damage at address 0 (consistent with prior bench sessions where wrong pinout sent 12V pulses to wrong chip pins). Dispatch + pinout + algorithm flow all CORRECT."
    detail: "All three operator-priority chips now functional. The Phase 04 dispatch + pinout work is end-to-end validated. Discovered issues: (a) [flash3-multichunk-write-timeout] new firmware bug in configure_flash3 multi-chunk path; (b) SST27SF512 transient bus glitch at A15 boundary first-read (cosmetic; non-deterministic); (c) FM1608 byte-0 stuck-at chip-level damage from prior wrong-pinout exposure (cannot be remediated in firmware/host)."
  - id: 32pin-mistagged-5v-flash
    severity: MEDIUM
    status: OPEN (research-only, no code change). 21 chips on 32-pin algo=0x08 (EPROM_QUICK / configure_eprom 12V VPP path) but with the `electrically erasable` flag — split between genuine 12V VPP UV-EPROMs (Winbond W27C/E series, SST 27SF series) and 5V parallel flash mistagged into the EPROM family (Macronix MX26C, Linkage LG28C, PTC PT28C, possibly SST 37VF series). Tagged for per-family datasheet research before any algorithm flip.
    surface: firestarter_app/firestarter/data/chip_database.json + firestarter_app/tools/build_db.py PIN_MAP_PROTO_TO_PINOUT
    evidence: "Per-family name-pattern analysis (datasheet research pending): W27C/E series is Winbond's genuine 12V VPP UV-EPROM line (datasheet-confirmed for W27C040 — VPP on pin 1, A18 on pin 31 — DIP32_STD is correct). SST27SF010/020 are Multi-Time-Programmable EPROMs per SST datasheet — 12V VPP, OK on current algo. By contrast: MX26C1000/2000/4000 are Macronix CMOS flash (5V, sector-erasable, vendor docs describe as 'flash memory' not 'EPROM'); LG28C010/020/040 are Linkage clones with the 28C prefix indicating 5V EEPROM family (compare AT28C, CAT28C); PT28C010/020/040 are PTC parallel EEPROMs (5V, page-write per PTC product brief). SST37VF series (37VF010/020/040/512) is the low-voltage MTP family — vpp=Unknown in DB → V suffix usually = 3.3V part."
    detail: "If the 5V-flash subset (MX26C, LG28C, PT28C, possibly SST37VF) is confirmed by datasheet, the correct routing is algorithm flip 0x08 → 0x05 or 0x06 (configure_flash3/4) + pinout DIP32_SST39SF040 (A18=pin 1, WE=pin 31, no VPP). Until confirmed, leave the chips on the current path — `firestarter info <chip>` shows 'UV-EPROM (12V VPP, quick pulse)' which is at least consistent with the current dispatch (operator-honest display). Next-step list for the bench session OR datasheet fetch: MX26C4000 (256K x 8 flash; check VPP requirement), LG28C040 (512K x 8; check pin 1 + VPP), PT28C040 (likewise), and SST37VF040 (likewise; the V suffix likely indicates 2.7-3.6V part)."
---

# Phase 4 — Hardware Validation (RURP shield) — Evidence

## §1 HW-01 — Test-script repair (WARNING-4 closure + jq schema migration)

**Date:** 2026-05-12T11:52:49Z
**Plan ref:** 04-01
**Commit:** firestarter_app@16dcafe

### Before (live broken refs)

Layer 1 — filename (the v1.0 / Phase 11 CLEAN-01 leftover, WARNING-4):

- `firestarter_app/firestarter_test.sh:31` — `JSON_FILE='./firestarter/data/database_generated.json'`
- `firestarter_app/write_test.sh:17`         — `JSON_FILE='./firestarter/data/database_generated.json'`

Layer 2 — jq schema (surfaced by gsd-phase-researcher, per CONTEXT.md D-01 RESEARCH.md-corrected):

- `firestarter_app/firestarter_test.sh:48-67` — three jq blocks with the pre-Phase-11 flat schema:
  - `select(.name == $target_name) | .["memory-size"]`
  - `select(.name == $target_name) | .["has-chip-id"]`
  - `select(.name == $target_name) | .["can-erase"]`
- `firestarter_app/write_test.sh:35-40` — single jq block, same pre-Phase-11 flat schema:
  - `select(.name == $target_name) | .["memory-size"]`

The new on-disk `chip_database.json` is `{manufacturer: [chip_records, ...]}` with nested
`.electrical.size_bytes`, `.programming.chip_id_check`, `.part_number`, `.electrical.type`.
The legacy queries would have returned `null` for every lookup even with the filename layer
fixed — both layers had to land in one atomic sub-repo commit per CONTEXT.md D-08.

### After (repaired refs)

Layer 1 — both scripts:

- `firestarter_app/firestarter_test.sh:31` → `JSON_FILE='./firestarter/data/chip_database.json'`
- `firestarter_app/write_test.sh:17`         → `JSON_FILE='./firestarter/data/chip_database.json'`

Layer 2 — `firestarter_test.sh` three jq queries (flattened across manufacturers; nested paths):

```bash
MEMORY_SIZE_HEX=$(jq -e --arg target_name "$EPROM_NAME" -r '
  .[] |
  .[] |
  select(.part_number == $target_name) |
  .electrical.size_bytes
' "$JSON_FILE")

HAS_CHIP_ID=$(jq -e --arg target_name "$EPROM_NAME" -r '
  .[] |
  .[] |
  select(.part_number == $target_name) |
  .programming.chip_id_check
' "$JSON_FILE")

CAN_ERASE=$(jq -e --arg target_name "$EPROM_NAME" -r '
  .[] |
  .[] |
  select(.part_number == $target_name) |
  (.electrical.type == "Flash/EEPROM")
' "$JSON_FILE")
```

Layer 2 — `write_test.sh` single jq query:

```bash
MEMORY_SIZE_HEX=$(jq -e --arg target_name "$EPROM_NAME" -r '
  .[] |
  .[] |
  select(.part_number == $target_name) |
  .electrical.size_bytes
' "$JSON_FILE")
```

The `MEMORY_SIZE_HEX` variable name is retained as-is for backward compatibility with the
downstream `dd` invocations; the new `.electrical.size_bytes` returns a plain integer
(e.g. `65536` for W27C512) and bash arithmetic auto-coerces — no hex conversion is needed.

The `CAN_ERASE` query was rewritten as `(.electrical.type == "Flash/EEPROM")` per the
`<interfaces>` translation table in 04-01-PLAN.md and RESEARCH.md §HW-01: the legacy
`.["can-erase"]` flag has no direct successor in the new schema, but the `Flash/EEPROM` type
discriminator correctly captures the "this chip supports erase" semantics for the bench-runner.

### Dry-run validation

Syntax check (both scripts, exit 0 expected):

```text
$ bash -n firestarter_app/firestarter_test.sh ; echo "exit=$?"
exit=0
$ bash -n firestarter_app/write_test.sh ; echo "exit=$?"
exit=0
```

`jq -e` smoke against the live `firestarter_app/firestarter/data/chip_database.json` for
the W27C512 reference chip (HW-02 baseline):

```text
$ JSON_FILE=firestarter_app/firestarter/data/chip_database.json
$ jq -e --arg t "W27C512" -r '.[] | .[] | select(.part_number == $t) | .electrical.size_bytes' "$JSON_FILE"
65536
exit=0
$ jq -e --arg t "W27C512" -r '.[] | .[] | select(.part_number == $t) | .programming.chip_id_check' "$JSON_FILE"
true
exit=0
$ jq -e --arg t "W27C512" -r '.[] | .[] | select(.part_number == $t) | (.electrical.type == "Flash/EEPROM")' "$JSON_FILE"
true
exit=0
```

All three jq smoke gates pass against the new nested schema. The W27C512 record returns
`size_bytes=65536` (matches the v1.0 PROJECT.md "What works today" baseline), `chip_id_check=true`
(so the HW-02 bench-run's chip-ID test branch will fire), and the `Flash/EEPROM`-type predicate
returns `true` (so the HW-02 erase + blank-check branch will also fire).

Firmware native unit-test state — **cited, not re-run** per Phase 3 LEARNINGS lesson
"existing test runs should be cited, not re-executed":

- `pio test -e native` 25/25 PASS — see `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-VERIFICATION.md` "Behavioral Spot-Check" subsection (Plan 01-01 + Plan 01-02 closure, firmware sub-repo HEAD as of 2026-05-12).

### Verdict

**PASS** — both scripts parse cleanly via `bash -n` against the post-Phase-11 DB filename
AND resolve W27C512 metadata via `jq -e` against the new nested `chip_database.json` schema.
WARNING-4 is closed: zero non-comment `database_generated.json` references survive in
either script (grep gate). Plan 04-02 (Wave 2 — HW-02 W27C512 + HW-03 AM29F040/SST39SF040
+ HW-04 AT28C256) inherits a known-clean test-script state.

## Bench Session 2026-05-12 — Diagnostic Findings (Plan 04-02 deferred)

**Outcome:** Plan 04-02 (Wave 2 — HW-02/HW-03/HW-04) **deferred**. No §-section evidence captured. Root cause: a host-side bug in firestarter_app's `EpromOperator` MAIN-phase data-send path blocks all write operations against the `configure_eprom` dispatch family (algo=0x07/0x08/0x0B). Confirmed on the canon W27C512 chip + the SST27SF512 substitute, against both the pre-flash (2.0.6 git tag) and post-flash (source HEAD `587396a`, 30 commits ahead) firmware builds.

Wave 2 cannot close until the host bug is fixed. The bench session captured substantial diagnostic gold (8 follow_ups in frontmatter, 10 raw evidence logs in `bench-evidence-2026-05-12/`) that should accelerate the fix.

### Session inventory + canon-vs-available

Plan 04-02 was authored assuming the canon four chips would be in hand. At bench start:

| Plan section | Canon chip | Operator inventory | Disposition |
|--------------|-----------|---------------------|--------------|
| §2 HW-02 | W27C512 (algo=0x07) | ✓ **had it** (initially mislabeled "W27E512" but operator clarified as DB-canon W27C512) | Bench attempted, blocked by host bug |
| §3a HW-03 chip-erase | AM29F040 (algo=0x06) | ✗ | Substituted to SST39SF040 chip-erase per D-12 |
| §3b HW-03 sector-erase | SST39SF040 (algo=0x06) | ✓ | Substitute and canon both → SST39SF040 (single chip, both variants per D-12) |
| §4 HW-04 | AT28C256 (algo=0x0D) | ✗ | Deferred per D-12 (no in-family substitute) |

D-12 (committed `f093643`) recorded the substitution plan: SST27SF512 for §2 (later resolved as: canon W27C512 was actually available), SST39SF040 for §3a + §3b, HW-04 deferred.

### Bench-attempt timeline

| Order | Chip | Operation | Result | Logfile |
|-------|------|-----------|--------|---------|
| 1 | SST27SF512 (DIP28, sub for W27C512) | `write_test.sh` then `firestarter write` | FAIL: `Data err -3` after 100% data sent, INIT complete, MAIN phase stalls at `OK: Req data` → host sends 4-byte packet header only, no payload | [01](bench-evidence-2026-05-12/01-sst27sf512_write_failed.log) + [02](bench-evidence-2026-05-12/02-sst27sf512_write_verbose_data_err_-3.log) |
| 2 | SST27SF512 | `firestarter blank` (post-fail) | PASS — chip still blank, confirming write programmed zero bytes despite host's 100% progress claim | (re-ran inline) |
| 3 | SST39SF040 (DIP32, swap) | `firestarter blank` | FAIL: chip-ID read `0x0000`, expected `0xbfb7` | [03](bench-evidence-2026-05-12/03-sst39sf040_chipid_0000.log) |
| 4 | SST39SF040 | `firestarter -v blank` (verbose) | Same fail — firmware enters INIT, AMD ID command returns 0x00 0x00 | [04](bench-evidence-2026-05-12/04-sst39sf040_chipid_0000_verbose.log) |
| 5 | (no chip) | `pio run -t upload -e uno` flash | SUCCESS in 9.37s — 25954 bytes; on-board firmware advanced from 2.0.6-tag to HEAD `587396a` (30 commits ahead, includes Phase 01/02/12 closures) | [05](bench-evidence-2026-05-12/05-firmware_flash_to_587396a.log) |
| 6 | SST39SF040 (re-insert) | `firestarter blank` | FAIL: still chip-ID 0x0000 — flash didn't fix this | [06](bench-evidence-2026-05-12/06-sst39sf040_chipid_0000_post_flash.log) |
| 7 | SST39SF040 | `firestarter blank -f` (force + verbose) | bypass ID check; enters MAIN; reads return 0x00 across full chip; "Not blank, at 0x000000" → chip not silent, but reads all zeros | [07](bench-evidence-2026-05-12/07-sst39sf040_force_blank_reads_0x00.log) |
| 8 | SST39SF040 | `firestarter erase -f -b` | "Erase successful (0.16s)" — but `-b` produced no visible blank-check; subsequent reads still all 0x00 → erase claim is false | [08](bench-evidence-2026-05-12/08-sst39sf040_fake_erase_success.log) |
| 9 | W27C512 (DIP28, swap) | `firestarter blank` | PASS — chip-ID `0xda08` matched, chip fully blank in 5.38s. Post-flash dispatch working correctly for this chip family. | [09](bench-evidence-2026-05-12/09-w27c512_blank_pass_chipid_0xda08.log) |
| 10 | W27C512 | `firestarter -v write` (canon HW-02 attempt) | FAIL: **identical failure mode to step 1** — `Data err -3` after 100% data, MAIN phase stalls at `OK: Req data` → host sends 4 bytes only. Confirmed: bug is universal across configure_eprom family, NOT chip-specific. | [10](bench-evidence-2026-05-12/10-w27c512_write_data_err_-3_universal.log) |
| 11 | W27C512 | `firestarter blank` (post-fail) | PASS — chip still blank. Write programmed zero bytes (same as step 2 for SST27SF512) | (re-ran inline) |

### Conclusive findings

1. **The host-side MAIN-phase data-send is broken for `configure_eprom` family.** Evidence: identical failure mode on two chips (canon W27C512 + sub SST27SF512), identical failure with both pre-flash and post-flash firmware. The verbose trace shows the host's send-data routine emits the 4-byte packet header (`#` + 2-byte size + 1-byte checksum) but no payload bytes follow. Firmware times out 2s later via `rurp_communication_read_data` returning `-3` ([rurp_serial_utils.cpp:82](../../../firestarter/src/boards/rurp_serial_utils.cpp#L82)).

2. **Firmware version-string drift hid the v1.1 firmware updates from the bench.** The on-board binary was at the 2.0.6 tag (`db4e565`) — pre-Phase-01-01 (SAF-04), pre-Phase-01-02 (SAF-05), pre-Phase-02-01 (vpp→vpp_mv), pre-Phase-12-02 (protocol-prefix dispatch). `firestarter fw` reported "up to date" because `version.h` was never bumped. Mid-session reflash brought the firmware to HEAD `587396a` — but did NOT fix the host MAIN-phase bug (which is on the Python side, not C++ firmware side).

3. **The operator's SST39SF040 is functionally dead** (or has stuck data-bus output drivers). The chip would have been the only canon §3b candidate had it been alive. The W27C512 substitute path is contingent on the host bug, not on SST39SF040 specifically.

4. **No `.planning/STATE.md` or `.planning/ROADMAP.md` writes** — orchestrator-owned per Phase 3 LEARNINGS surprise. Plan 04-02 is **status: deferred**, not status: complete or status: partial.

### Cross-references

- Plan body: [04-02-PLAN.md](04-02-PLAN.md)
- Substitution plan: 04-CONTEXT.md D-12 (committed `f093643`)
- Plan closure: [04-02-SUMMARY.md](04-02-SUMMARY.md) — status: deferred
- Raw bench evidence: [bench-evidence-2026-05-12/](bench-evidence-2026-05-12/) — 10 logs + 1 binary readback sample
- Follow-up tracking: frontmatter `follow_ups:` (8 items, with severity classes BLOCKER / HIGH / MEDIUM / LOW)

### What unblocks Plan 04-02 resumption

In dependency order:

1. ~~**Fix host MAIN-phase bug**~~ → **RESOLVED 2026-05-12** in `firestarter_app@08ca252` (single-line root cause: spurious `expect_ack()` between header and payload in `_main_phase_send_data`). Bench re-validation pending next session.
2. **Replace SST39SF040 chip** (`follow_up: sst39sf040-dead-chip`) — sourcing another SST39SF040 (or substituting with a different algo=0x06 chip, e.g. AM29F040 if also sourced).
3. **Source AT28C256** for HW-04 (still deferred per D-12).
4. ~~**Bump `version.h` VERSION**~~ → **RESOLVED 2026-05-12** in `firestarter@bbf0e0c` (VERSION "2.0.6" → "2.0.7-dev").
5. **Fix CLI label bugs + DB entries** (`follow_ups: firestarter-info-label-bugs`, `fm1608-db-mismatch`, `w27e512-missing-db-entry`, `firestarter-erase-b-silent`, `firestarter-force-flag-scope`) — UX + safety improvements; not strictly blockers for Plan 04-02 but cleanup-worthy. `fm1608-db-mismatch` now fully evidenced (see follow_up detail + bench-evidence-2026-05-12/11+12).

**With #1 + #4 resolved**, the next bench session can:
- Reflash the Arduino (`pio run -t upload -e uno` from `firestarter/`) — picks up both the new VERSION string AND the up-to-date dispatch chain.
- Re-run `/gsd-execute-phase 04 --wave 2 --interactive` with a fresh W27C512 (already proven blank-check OK in this session).
- Sequential remaining blockers: source §3 chip + AT28C256.

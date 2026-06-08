# Project Research Summary

**Project:** Firestarter v1.11 — Complete infoic.xml Decode & Full Memory-Type Coverage
**Synthesized:** 2026-06-08
**Confidence:** HIGH (all findings from direct minipro source + Firestarter codebase reads)
**Inputs:** STACK.md (field dictionary), FEATURES.md (protocol catalog/feasibility), ARCHITECTURE.md (integration), PITFALLS.md (hazards)

---

## ⚠ Premise Overturned — Read First

The milestone was scoped to "expand to all hardware-capable types, add firmware handlers, dual-repo." Research against minipro source shows **the hardware-feasible memory set is already essentially covered**, so the expansion space is nearly empty:

- **0x2A / 0x2C / 0x2E are NOT NVRAM.** Per `minipro/src/database.h`: 0x2A = GAL16V8 (PLD), 0x2C = GAL22V10 (PLD), 0x2E = PIC32 (MCU). **Zero DIP memory chips** use them. build_db.py's `PROTOCOL_MAP` labels (NVRAM_32PIN / NVRAM_TIMEKEEPER / NVRAM_512K) are simply wrong.
- **FWH (0x11) is INFEASIBLE on RURP.** M50FW040/080 are DIP32 physically but use the Intel LPC/FWH 4-wire serial bus and 3.3V VCC — not parallel, not 5V. Cannot be driven; 3.3V on the fixed-5V supply is a damage path.
- **Real battery-backed NVRAM / timekeeper (DS1225/DS1230/DS1245/M48T/BQ40xx) is ALREADY covered** — routed to `configure_sram` via standard SRAM protocol IDs (0x07/0x0B+type=4 → fm1608 override → 0x28; 32-pin → 0x0E). They are in the DB and work.
- **0x35 and 0x39 are phantom `KNOWN_PROTOCOLS` entries** — zero DIP-24..32 memory chips reach them (0x35=ITE TQFP128; 0x39 has no IC2_ALG and only exists in legacy INFOIC for DIP40).

**The one genuine new-chip gap is small and host-only:** ~9 blocked 24-pin EEPROMs (AT28C04, AT28C16, AT28C16A, 28C04A, UPD28C04). They are currently SKIPPED by the safety filter because the code assumed they'd get the `DIP24_2716` pinout (VPP on pin 21 = WE# damage path). Fix = assign `DIP24_6116` pinout (WE# already on pin 21) + `algorithm=0x0D`. **No new firmware handler** — `configure_eeprom28c` already does 5V page-write + SDP-disable correctly.

**Net:** the real value of v1.11 is **decode correctness + authoritative documentation**, not expansion. Firmware work is expected to be **zero** (one contingency: a `configure_sram`/NVRAM WP# safety audit could surface a firmware item).

---

## What Is Genuinely New vs Already-Covered

| Work | New? | Repo |
|------|------|------|
| Correct confirmed build_db.py decode bugs (timing, VCC, vdd/vcc swap, PROTOCOL_MAP) | NEW | host |
| Authoritative field dictionary + corrected decode docs | NEW | host (docs) |
| Re-derive `resolve_pinout_key` from minipro gnd/vcc/pin masks (retire guess tables) | NEW | host |
| Unblock 9 × 24-pin EEPROMs (DIP24_6116 + 0x0D) | NEW | host |
| Correctness/regression gate (extend check_dispatch.py; per-chip diff vs pinned snapshot) | NEW | host |
| New firmware algorithm handlers | NONE needed | — |
| NVRAM/timekeeper memory support | already covered | — |
| FWH / PLD / MCU protocols | infeasible/out-of-scope (document as anti-features) | — |

---

## Confirmed Decode Bugs (from STACK.md / FEATURES.md)

| Bug | Detail | Fix |
|-----|--------|-----|
| BUG-1 VCC_VOLTAGES incomplete | missing nibble 0x02 (4V) / 0x03 (4.5V); AT28C256/AT28C64 default to 5V | add entries |
| BUG-2 interpret_timing ×100 | applied to 0x07/0x0B; pulse_delay already µs (W27C512 → 10000µs not 100µs) | remove multiplier (verify vs source first) |
| BUG-3 vdd/vcc swap | labels inverted vs database.c (11-8=vcc, 15-12=vdd) | swap field names |
| BUG-4 PROTOCOL_MAP | wrong names 0x2A/0x2C/0x2E/0x35; invented 0x3C; phantom 0x39 | rename from IC2_ALG_*; remove invented; document phantoms |

---

## Hardware-Damage Hazard Model (from PITFALLS.md)

Six hazard classes, all one root path: **wrong decode → wrong pinout → VPP regulator output on the wrong socket pin → 5V chip destroyed.** Distinguished by three CTRL bits (`CTRL_VPP_REGULATOR_ENABLE`, `CTRL_VPE_ENABLE`/`CTRL_VPP_P1_ENABLE`, `CTRL_VPP_A9_ENABLE`).

The existing WARNING-5 / fm1608 / 24-pin-EEPROM-skip overrides each prevent a real manifestation. **Re-derivation risk:** the two-pass `_etype` computation is load-bearing (override predicates depend on the flags-based `_etype` at predicate time, then it's re-derived protocol-aware) — merging the passes silently breaks the guards. `check_dispatch.py` has a blind spot: it only checks the WARNING-5 condition for chips already in `DIP28_2764` — it must be extended to all pinouts where `vpp-pin` is present AND a 5V-EEPROM-family handler is assigned.

**Per-handler safety-review checklist (SR-1..SR-6)** in PITFALLS.md is a phase-close requirement for any newly-exposed write path: cross-check vpp-pin / WE / OE / CE / PGM / address-overlap against the datasheet pin map.

---

## Integration / Architecture (from ARCHITECTURE.md)

The decode pipeline is **not redesigned** — the wire `algorithm` integer → firmware dispatch contract is already correct. Interventions are host-side: PROTOCOL_MAP + field-decode tables; `resolve_pinout_key` rewrite to a `(pin_count, proto_id, mem_size)` principled dispatch grounded in minipro gnd/vcc/pin bitmasks (replacing the survey-built guess tables); refactor WARNING-5/fm1608 into named predicate functions; one new `pinouts.json` DIP24 5V EEPROM entry (rw-pin=21, no vpp-pin); check_dispatch.py extensions. `pin_conversions` in database.py is frozen RURP wiring — unchanged. The (unused-this-milestone) new-handler contract is documented for the future: one if-return in `memory.cpp::configure_memory` + `.cpp/.h` + `_ALGO_MEM_TYPE` + KNOWN_PROTOCOLS/PROTOCOL_MAP + Unity test, landed dual-repo lockstep.

---

## Recommended Build Order → Suggested Phases (all host-only)

1. **Pinned snapshot + field-dictionary foundation** — commit a pinned `infoic.xml` snapshot (prevents upstream drift corrupting the regression baseline) + snapshot current `chip_database.json`; produce authoritative field-dictionary tables (package_details/voltages/flags/protocol_id) from minipro source; deliver corrected `protocol-id.md` / `protocol-flags.md` / `package-details.md`.
2. **Decode bug fixes + PROTOCOL_MAP corrections** — fix BUG-1..4; add exclusion-filter comments for 0x11/0x2A/0x2C/0x2E/0x35/0x39/AT45D; extend `check_dispatch.py` (full-class WARNING-5 + type=4/flash guard) **before** re-derivation can introduce evasive regressions.
3. **Pinout resolution audit + 24-pin EEPROM unblock** — audit `PIN_MAP_TO_PINOUT`/`PIN_MAP_PROTO_TO_PINOUT` against minipro masks/datasheets; add DIP24 EEPROM pinout; unblock the 9 AT28C04/AT28C16 chips; SR-1 checklist; regenerate DB + review per-chip diff.
4. **Correctness gate + regression suite** — automated cross-check of pipeline output vs field dictionary; per-chip diff clean vs the pinned baseline; `configure_sram` NVRAM WP#/blank-check audit (documents SRAM volatility limitation; only escalates to firmware if a safety issue is found); check_dispatch green across full set.

Ordering: snapshot/dictionary first (prerequisite); bug fixes before pinout audit (voltage/flags decode affects classification); the EEPROM unblock is the one expansion step; gate last.

---

## Open Questions for Planning/Execution

- **interpret_timing ×100**: confirm against minipro `interpret_timing()` it isn't an intentional per-protocol unit before removing the multiplier.
- **VCC_VOLTAGES 0x02/0x03 exact values**: confirmed missing; values (4V/4.5V) from `tl866ii_vcc_voltages[]` — re-verify in Phase 1.
- **configure_sram NVRAM + WP#**: WP# behavior for DS1225/M48T08 unconfirmed; datasheet audit in the gate phase before declaring NVRAM write safe (only firmware item that could appear).
- **AT28C04 chip_id=0 + 9-bit address SDP**: verify `eeprom28c_check_chip_id`'s `if (chip_id > 0)` guard suppresses A9=12V for AT28C04 (no A9 pin); confirm 0x5555/0x2AAA SDP magic addresses alias correctly in 9-bit space.
- **is_serial bit for FWH**: confirm `package_details[15:8]` already filters 0x11 FWH parts (may make an explicit skip unnecessary).
- **Correctness-gate scope**: one-off script vs CI artifact — decide at plan time.

---

## Confidence

| Area | Level | Basis |
|------|-------|-------|
| Field dictionary | HIGH | direct minipro database.c/.h reads, infoic.xml samples |
| Protocol catalog / feasibility | HIGH | IC2_ALG constants + infoic.xml census + firmware reads |
| Architecture / integration | HIGH | full reads of build_db.py, database.py, memory.cpp + handlers |
| Hazard taxonomy | HIGH | firmware VPP source + build_db override comments + check_dispatch logic |
| NVRAM WP# / exotic write safety | MEDIUM | JEDEC reasoning; DS1245/M48T datasheet cross-check still pending |

**Ready for requirements + roadmap.**

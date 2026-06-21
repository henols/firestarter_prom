# Requirements: Firestarter — v1.14 Feasible-Gap Implementation

**Defined:** 2026-06-18
**Core Value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Milestone goal:** Graduate chips to `supported` by implementing the four evidence-surfaced, RURP-feasible gaps that v1.13 deliberately scoped out (validation-only) — the first chips to become newly programmable since v1.0. Build order: 999.4 → 999.5 → 999.7 → 999.6 (operator-captured 2026-06-18; X88C64 firmware before the 25V host-only change; hardware-blocked adapter last).

**Cross-cutting safety contract:** Each graduation *removes* the v1.12 `chip_resolver.resolve_chip` host-guard refusal — the authoritative wrong-VPP-to-wrong-pin damage barrier. The guard drop is always the FINAL step of a phase, gated behind native register-bit tests + wire round-trip + a Leonardo bench proof (chip-OUT VPP multimeter dry-run first). Leonardo + a clean shield is the only trustworthy PASS path; uno328pb is N/A for program/write. See `.planning/research/SUMMARY.md`.

## v1 Requirements

### Erase Write-Path — 999.4 (was v1.13 ERASE-01, skipped Phase 75)

- [ ] **ERASE-01**: Writing a W27C512-class EE-EPROM (the 7–8 `electrical.type=="EEPROM"` chips on protocol 0x07) auto-erases before programming — `FLAG_CAN_ERASE` wired from `electrical.type=="EEPROM"` in `convert_to_programmer` (`firestarter_app/firestarter/database.py`), not the always-zero `info-flags & 0x10`. Firmware `eprom_write_init` guard already honors the flag.
- [ ] **ERASE-02**: The write → auto-erase → program → verify cycle is bench-confirmed on Leonardo with a real W27C512 (14V erase-rail chip-OUT VPP dry-run first, under the VPP ceiling).

### X88C64 0x34 Handler — 999.5 (firmware; dual-repo lockstep)

- [ ] **XIC-01**: The X88C64 ALE-routing question is resolved by bench investigation — a control path to drive the 8051 Address-Latch-Enable is identified (or the gap is documented as PCB-blocked and X88C64 deferred again) — *before* any handler code is written. (`X88C64-FEASIBILITY.md` Assumption A6, LOW confidence.)
- [ ] **XIC-02**: A `configure_x88c64` firmware handler implements protocol 0x34 (8051 multiplexed address/data bus via ALE/WR/RD, page write ≤32 bytes, toggle-bit I/O6 polling), registered in `memory.cpp` dispatch *before* the `protocol != 0 → configure_not_implemented` guard. STORE/RECALL explicitly out of scope (X2210/X2212 family).
- [ ] **XIC-03**: The new handler fits the Leonardo flash budget — `pio run -e leonardo` ≤ ~90% — measured and recorded as a phase gate.
- [ ] **XIC-04**: X88C64P graduates to `supported`; an N≥5 write + read-back SHA-match cycle is bench-confirmed on Leonardo with a non-vacuous negative control.

### 25V NMOS Support — 999.7 (host-only ceiling raise; hardware-gated)

- [ ] **NMOS-01**: The on-bench shield's ability to safely produce ≥25V VPP at the socket pin is confirmed by operator multimeter (chip-OUT dry-run) *before* the ceiling constant changes. (Rated-feasible per RURP Rev 2.3 5–27V spec, but shield-R1/R2-calibration-dependent.)
- [ ] **NMOS-02**: `RURP_VPP_CEILING_MV` raised 22000 → 25000 (`firestarter_app/tools/build_db.py`) and the `check_dispatch.py` `_FAMILY_VPP_INVARIANTS` ceiling updated; the 4 NMOS chips (INTEL M2716, INTEL M2732, SGS-THOMSON ETC2716, ST M2716) re-classify off `vpp-exceeds-max`. (M2732A at 21V is already `supported`.)
- [ ] **NMOS-03**: The 4 NMOS chips graduate to `supported`; a write + verify is bench-confirmed on Leonardo.

### AT28C04/16 Adapter Graduation — 999.6 (hardware-blocked; sequence last)

- [ ] **ADPT-01**: A physical DIP24 → DIP32 adapter is built per the Phase 76 pin-map spec (`firestarter/doc/AT28C04-ADAPTER.md`), validated by a DMM continuity check — especially the /WE chip-pin-21 → socket-pin-30 reroute against `DIP32_28C512_EEPROM` — before any chip is inserted.
- [ ] **ADPT-02**: The 9 AT28C04/AT28C16 chips are wired through the existing `configure_eeprom28c` (protocol 0x0D, VPP-free) handler — the `_AT28C_DIP24_NAMES` rule arm in `build_db.py` and the `adapter-required` host-guard refusal in `chip_resolver.resolve_chip` removed.
- [ ] **ADPT-03**: The 9 chips graduate to `supported`; a golden write + read-back round-trip is bench-confirmed on Leonardo with the adapter seated.

### Safety & Regression — cross-cutting

- [ ] **SAFE-01**: For each graduated chip family, the `chip_resolver.resolve_chip` host-guard refusal is removed only as the FINAL step, after native register-bit (recording-stub) + host wire round-trip + Leonardo bench validation are all on record.
- [ ] **SAFE-02**: The `check_dispatch.py` full-DB VPP-safety gate passes after each graduation — no chip dispatches a VPP above its family invariant / the new 25V ceiling.
- [ ] **SAFE-03**: Firmware ↔ host constant parity preserved — any `FLAG_*` / protocol constant touched in `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h` is changed in lockstep; parity tests stay green.

## v2 Requirements (deferred)

### Future chip support

- **FUT-01**: X88C64 graduation if v1.14 ALE investigation (XIC-01) finds it PCB-blocked — revisit with a shield modification.
- **FUT-02**: Any NMOS chip requiring >25V VPP — stays fail-closed (anti-feature).

## Out of Scope

| Feature | Reason |
|---------|--------|
| X88C64 STORE/RECALL operations | That capability belongs to the X2210/X2212 NovRAM family, not the X88C64P EEPROM |
| NMOS chips needing >25V VPP | Beyond the confirmed/raised hardware ceiling; remain `vpp-exceeds-max` fail-closed |
| Firmware runtime VPP enforcement | Out of scope this milestone; host pre-screening (`check_dispatch.py` + host guard) remains the safety layer |
| New transport / protocol-framework changes | COBS+CRC8 transport and the algorithm-first dispatch architecture are settled — graduations reuse existing handlers |
| Graduating chips on an unverified shield (uno328pb) | uno328pb is N/A for program/write per standing bench rules; Leonardo is the only trustworthy verify board |
| 6.5V NMOS VCC programming | RURP is fixed-5V VCC; out since v1.0 |

## Traceability

Which phases cover which requirements. Filled in by the roadmapper.

| Requirement | Phase | Status |
|-------------|-------|--------|
| ERASE-01 | Phase 77 | Pending |
| ERASE-02 | Phase 77 | Pending |
| XIC-01 | Phase 78 | Pending |
| XIC-02 | Phase 78 | Pending |
| XIC-03 | Phase 78 | Pending |
| XIC-04 | Phase 78 | Pending |
| NMOS-01 | Phase 79 | Pending |
| NMOS-02 | Phase 79 | Pending |
| NMOS-03 | Phase 79 | Pending |
| ADPT-01 | Phase 80 | Pending |
| ADPT-02 | Phase 80 | Pending |
| ADPT-03 | Phase 80 | Pending |
| SAFE-01 | Phase 77 | Pending |
| SAFE-02 | Phase 77 | Pending |
| SAFE-03 | Phase 77 | Pending |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 15 ✓ (Phase 77: ERASE-01/02 + SAFE-01/02/03; Phase 78: XIC-01/02/03/04; Phase 79: NMOS-01/02/03; Phase 80: ADPT-01/02/03)
- Unmapped: 0

_SAFE-01/02/03 are cross-cutting; mapped to Phase 77 (first graduation, where the guard-removal-last pattern + check_dispatch gate + lockstep parity are established) and recur as success criteria in Phases 78–80._

---
*Requirements defined: 2026-06-18*
*Last updated: 2026-06-18 — roadmap created; 15/15 requirements mapped to Phases 77–80*

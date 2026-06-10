# Requirements: Firestarter v1.11 — Complete infoic.xml Decode & Database Correctness

**Defined:** 2026-06-08
**Core Value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware handler. No guessing.
**Milestone scope:** HOST-ONLY (firestarter_app data pipeline + docs). Firmware sub-repo untouched. Re-scoped after source-grounded research overturned the original "expand + firmware handlers" framing — see `.planning/research/SUMMARY.md`. Correctness proven by minipro-source cross-check; no bench required to close.

## v1 Requirements

Requirements for this milestone. Each maps to exactly one roadmap phase.

### DEC — Field Decode & Dictionary

- [x] **DEC-01**: An authoritative, source-cited field dictionary documents every Firestarter-relevant `infoic.xml` attribute (`package_details`, `type`, `variant`, `protocol_id`, `flags`, `voltages`, `pin_map`, `pulse_delay`, `chip_id`, `code_memory_size`, `page_size`, `chip_info`, `blank_value`), each marked CONFIRMED / INFERRED / UNKNOWN against minipro source.
- [x] **DEC-02**: `build_db.py` field decode is re-derived to match minipro source semantics for `voltages`, `flags`, `protocol_id`, `type`, and `package_details`.
- [x] **DEC-03**: `pulse_delay` is decoded as microseconds for all protocols (the `interpret_timing` ×100 multiplier for 0x07/0x0B is removed), verified against minipro source.
- [x] **DEC-04**: VCC/VDD voltage decode is complete and correctly labelled — nibble `0x02`=4V and `0x03`=4.5V are added, and `vcc` (bits 11-8) / `vdd` (bits 15-12) field names are corrected.
- [x] **DEC-05**: `PROTOCOL_MAP` uses canonical `IC2_ALG_*` names; non-memory or unreachable IDs (`0x2A`/`0x2C`/`0x2E` GAL/PIC, `0x35` ITE, `0x39`, `0x3C`) are removed or documented with an explicit exclusion rationale.

### PIN — Pinout Resolution & Chip Coverage

- [x] **PIN-01**: `resolve_pinout_key` is re-derived from principled `(pin_count, proto_id, mem_size)` rules grounded in minipro pin/gnd/vcc masks, replacing the survey-built `PIN_MAP_*` / `DIP28_VARIANT_MAP` guess tables.
- [x] **PIN-02**: The load-bearing safety overrides (WARNING-5 `0x07→0x0D`, fm1608 `type=4` flip, 24-pin EEPROM skip semantics) are preserved/verified through the re-derivation — no chip gains a VPP-on-wrong-pin damage path.
- [x] **PIN-03**: The 9 currently-blocked 24-pin EEPROMs (AT28C04 / AT28C16 family) are exposed via the `DIP24_6116` pinout + `algorithm=0x0D`, safety-reviewed (SR-1 checklist); no firmware change (`configure_eeprom28c` already handles them).

### DOC — Authoritative Decode Documentation

- [ ] **DOC-01**: `firestarter_app/doc/package-details.md` is corrected — re-titled to describe `flags`, bit meanings source-grounded, inferred bits (3/6/7) explicitly marked as not source-confirmed.
- [ ] **DOC-02**: `firestarter_app/doc/protocol-flags.md` is corrected — canonical protocol names, flag-bit interpretation fixes (bit 4 = `can_erase`).
- [ ] **DOC-03**: `firestarter_app/doc/protocol-id.md` is corrected — `IC2_ALG_*` names, the `0x39` error fixed, feasibility/exclusion notes for non-memory and infeasible IDs.

### GATE — Correctness & Regression Gate

- [ ] **GATE-01**: `infoic.xml` is pinned to a specific upstream snapshot, committed in-repo as the decode baseline (guards against upstream drift corrupting regression comparisons).
- [x] **GATE-02**: A per-chip diff of the regenerated `chip_database.json` against the pre-milestone baseline is produced and reviewed; every changed chip is explained and intended.
- [x] **GATE-03**: `check_dispatch.py` is extended to a full-class VPP-safety guard (asserts no chip with a `vpp-pin` pinout AND a 5V-EEPROM-family handler routes to a VPP-asserting path — not just `DIP28_2764`); green across the full chip set.
- [x] **GATE-04**: `configure_sram` NVRAM/SRAM blank-check + WP# behavior is audited and documented (SRAM volatility / blank-check limitation noted). Host-side audit; escalates to a firmware item ONLY if a real safety issue is found.

## v2 Requirements

Deferred to a future milestone. Tracked but not in this roadmap.

### Bench Validation

- **BENCH-01**: Bench write/program validation of the newly-unblocked 24-pin EEPROMs (AT28C04/AT28C16 family) on real hardware (this milestone closes on source-correctness only).

### Future Decode/Handler

- **FUT-01**: New firmware algorithm handler — only if a genuinely DIP-parallel, RURP-drivable memory type not already covered ever appears in upstream.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| FWH `0x11` (M50FW040/080) support | Intel LPC 4-wire serial bus + 3.3V VCC — not parallel, not 5V; infeasible on RURP |
| GAL/PLD (`0x2A`/`0x2C`), PIC/MCU (`0x2E`), ITE (`0x35`) | Not parallel DIP memory; zero DIP memory chips in infoic.xml |
| Serial/SPI/I2C memories (AT45D etc.), SMD/PLCC packages, 40-pin DIP | Outside the RURP DIP-24/28/32 5V parallel envelope |
| New NVRAM/timekeeper handlers | Already covered via existing SRAM protocols (DS1225/DS1245/M48T) |
| Firmware changes | Host-only milestone (like v1.8) — firmware sub-repo untouched unless GATE-04 surfaces a safety fix |
| Bench / hardware validation | Correctness proven by minipro-source cross-check; bench deferred to v2 BENCH-01 |
| Database schema redesign | Current `chip_database.json` schema preserved; only decoded values corrected |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DEC-01 | Phase 56 | Complete |
| DEC-02 | Phase 57 | Complete |
| DEC-03 | Phase 56 (dict) + Phase 57 (code) | Complete |
| DEC-04 | Phase 56 (dict) + Phase 57 (code) | Complete |
| DEC-05 | Phase 56 (dict) + Phase 57 (code) | Complete |
| PIN-01 | Phase 58 | Complete |
| PIN-02 | Phase 58 | Complete |
| PIN-03 | Phase 58 | Complete |
| DOC-01 | Phase 56 | Pending |
| DOC-02 | Phase 56 | Pending |
| DOC-03 | Phase 56 | Pending |
| GATE-01 | Phase 56 | Pending |
| GATE-02 | Phase 59 | Complete |
| GATE-03 | Phase 57 | Complete |
| GATE-04 | Phase 59 | Complete |

**Coverage:**

- v1 requirements: 15 total
- Mapped to phases: 15/15 ✓
- Unmapped: 0

---
*Requirements defined: 2026-06-08*
*Last updated: 2026-06-08 — roadmap created (phases 56-59 assigned; 15/15 requirements mapped)*

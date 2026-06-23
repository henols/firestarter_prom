# V1.15 Bench Validation Evidence

**Phase:** 81-2516-db-entry-non-destructive-read-sweep  
**Harness version:** 81  
**Board (locked):** Leonardo  
**Shield (locked):** Rev 2.0  
**Scaffolded:** 2026-06-23  
**Status:** Pending — Plan 81-03 sweep populates SHA, read_count, blank_check_result, and Verdict.

## Schema Notes

- **Locked columns** (never change after scaffold): Chip, Family/Algorithm, Board, Shield, Op, Anomalies structure.
- **UV-EPROM blank state** (3 chips): blank_check result is a **Phase 83 gate** — if not blank, Phase 83 uses AND-mask (0x00 image) only; if blank, full write is possible.
- **Non-UV chips** (8 chips): blank_state = n/a (EEPROMs/Flash/FRAM are never factory-blank). SHA records current contents. Blank check result noted for information.
- **read_count**: minimum 3 reads required for a non-vacuous PASS (N≥3 byte-identical reads + negative control per EVID-03).
- **Verdict**: PASS / ANOMALY / FAIL / pending. ANOMALY = suspect read after 2 reseat+retry cycles; deferred to Phase 84 FIX-01.

## Evidence Table

| Chip | Family / Algorithm | Board | Shield | Blank State | Op | SHA256 (first 16) | Read Count | Verdict | Anomalies |
|------|--------------------|-------|--------|-------------|-----|-------------------|------------|---------|-----------|
| W27C512 | 0x07 EPROM_STD/EEPROM | leonardo | Rev 2.0 | n/a — non-UV | read+blank_check | pending | pending | pending | — |
| W27E512 | 0x07 EPROM_STD/EEPROM | leonardo | Rev 2.0 | n/a — non-UV | read+blank_check | pending | pending | pending | — |
| SST27SF512 | 0x07 EPROM_STD/EEPROM | leonardo | Rev 2.0 | n/a — non-UV | read+blank_check | pending | pending | pending | — |
| W27E040 | 0x08 EPROM_QUICK/EEPROM | leonardo | Rev 2.0 | n/a — non-UV | read+blank_check | pending | pending | pending | — |
| SST39SF040 | 0x06 FLASH_AMD_ALT/Flash | leonardo | Rev 2.0 | n/a — non-UV | read+blank_check | pending | pending | pending | — |
| W29C020 | 0x05 FLASH_AMD_STD/Flash | leonardo | Rev 2.0 | n/a — non-UV | read+blank_check | pending | pending | pending | — |
| W29C040 | 0x05 FLASH_AMD_STD/Flash | leonardo | Rev 2.0 | n/a — non-UV | read+blank_check | pending | pending | pending | — |
| FM1608 | 0x40 SRAM_STD/FRAM | leonardo | Rev 2.0 | n/a — non-UV | read+blank_check | pending | pending | pending | — |
| ST M27C512 | 0x07 EPROM_STD/UV-EPROM | leonardo | Rev 2.0 | **GATE (Phase 83)** | read+blank_check | pending | pending | pending | — |
| AM27C020 | 0x08 EPROM_QUICK/UV-EPROM | leonardo | Rev 2.0 | **GATE (Phase 83)** | read+blank_check | pending | pending | pending | — |
| 2516 | 0x0B EPROM_LEGACY/UV-EPROM | leonardo | Rev 2.0 | **GATE (Phase 83)** | read+blank_check | pending | pending | pending | — |

## UV-EPROM Blank State Legend

The three UV-EPROM chips (ST M27C512, AM27C020, 2516) carry `GATE (Phase 83)` in the Blank State column. The sweep result for each will be one of:

- **blank (0xFF throughout)** → Phase 83 may proceed with a full write → verify.
- **non-blank (data present)** → Phase 83 uses AND-mask strategy (all-0x00 image) only; pristine data preserved.
- **ANOMALY** → suspect read after reseat+retry; defer to Phase 84 FIX-01.

## Extends v1.13 Validation Matrix

This artifact extends the v1.13 per-family matrix
(`firestarter_app/val-results/eprom/validation-matrix.json`, harness_version=71).
The v1.13 matrix recorded per-family verdicts (eprom, flash3, flash4, sram).
This v1.15 EVIDENCE record is per-chip (one row per physical device in the operator
inventory), with additional fields: `blank_check_result`, `sha256`, `read_count`.

No new harness or dependency is introduced (EVID-02). The `firestarter dev write-cycle`
and `firestarter read` commands are the existing tools used for read evidence.

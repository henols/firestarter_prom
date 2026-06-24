# v1.15 Bench Evidence — Phase 81 Non-Destructive Read Sweep

**Harness version:** 81 · **Board:** leonardo · **Shield:** Rev 2.0 · **Generated:** 2026-06-23/24

## SAFE-01 Preconditions (verified per task)

- **Board:** leonardo (the only authoritative read board) · **Port:** /dev/ttyACM0 · **Firmware:** 3.0.0b8
- **Shield:** Rev 2.0 — operator-confirmed silkscreen (EEPROM hw byte reports "Rev 2.0-class", cannot distinguish revs)
- **Calibration:** R1=270000, R2=44000 (not the 1000 default)
- **Host suite:** green (Plan 81-01, 651 tests)
- **Negative control (EVID-03):** FIRED — wrong-file `verify` exited RC=1 on W27C512 (Task 1) and ST M27C512 (Task 2)
- **Non-destructive:** reads apply NO VPP — **zero chips consumed**

## Sweep Result — 10 PASS / 1 ANOMALY

| # | Chip | Family / Algorithm | Board+Shield | Op | Blank-state | Read N | SHA-256 | Verdict | Anomalies |
|---|------|--------------------|--------------|----|-------------|--------|---------|---------|-----------|
| 1 | W27C512 | 0x07 (EPROM_STD / EEPROM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `9376dcd81713…97ad23c8` | **PASS** | VPP-high read refusal (~18.8V) cleared by board reset before this read; negative-control verify exited RC=1 |
| 2 | W27E512 | 0x07 (EPROM_STD / EEPROM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `71189f7fb6ae…48da9063` | **PASS** | none |
| 3 | SST27SF512 | 0x07 (EPROM_STD / EEPROM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `f633b2f5c06c…f8056360` | **PASS** | none |
| 4 | W27E040 | 0x08 (EPROM_QUICK / EEPROM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `67f70ccdae30…468b4254` | **PASS** | none |
| 5 | SST39SF040 | 0x06 (FLASH_AMD_ALT / Flash) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `c19c3e07b94b…a348368d` | **PASS** | none |
| 6 | W29C020 | 0x05 (FLASH_AMD_STD / Flash/EEPROM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `93ff5287b7e6…66b53602` | **PASS** | none |
| 7 | W29C040 | 0x05 (FLASH_AMD_STD / Flash/EEPROM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `d44736a9c4fa…1e3b48b3` | **PASS** | none |
| 8 | FM1608 | 0x40 (SRAM_STD / FRAM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `2ef1444bc950…3d4c0037` | **PASS** | blank-check 'Empty input' on FRAM (0x40) — read N=3 identical, flag for Phase 84 FIX-01 review (blank-check tooling gap, not a read fault) |
| 9 | ST M27C512 | 0x07 (EPROM_STD / UV-EPROM) | leonardo Rev 2.0 | read+blank_check | BLANK | 3 | `71189f7fb6ae…48da9063` | **PASS** | benign VPP-low warning 11.9V<13.0V on read (non-blocking; reads apply no VPP); negative-control verify RC=1 |
| 10 | AM27C020 | 0x08 (EPROM_QUICK / UV-EPROM) | leonardo Rev 2.0 | read+blank_check | NOT-BLANK | 3 | `08b687a3d711…177ed496` | **PASS** | none |
| 11 | 2516 | 0x0B (EPROM_LEGACY / UV-EPROM, NMOS) | leonardo Rev 2.0 | read+blank_check | NOT-BLANK | 3 | `—` | **ANOMALY** | READ UNSTABLE: 3 distinct SHAs across N=3 on initial + 2 reseat cycles (D-07 exhausted). VPP pinned 15.3V<25.0V on shared OE/VPP pin during read (0x0B Legacy path) — same VPP-regulator instability family as chip-1 18.8V boot refusal. Signature is 0x0B-specific (all 0x07/0x08 UV chips read clean on this bench). GATES Phase 83 (no 2516 write/preserve until read path stable). Flag Phase 84 FIX-01. |

## UV-EPROM Gating Blank-States (the Phase 83 gate)

| UV Chip | Gating blank-state | Notes |
|---------|--------------------|-------|
| ST M27C512 | **BLANK** | stable all-0xFF, N=3 byte-identical |
| AM27C020 | **NOT-BLANK** | data present (0x02@0x0000), N=3 byte-identical |
| 2516 | **NOT-BLANK** (read-unstable) | blank-check deterministically not-blank; reads jitter (3 SHAs) — exact contents unreliable |

## ⚠ Phase 83 Gate / Phase 84 FIX-01

The **2516** (0x0B Legacy, shared OE/VPP pin) read is **UNSTABLE** — 3 distinct SHAs across the initial read + 2 reseat cycles (D-07 exhausted), with VPP pinned at 15.3V on the shared OE/VPP pin. Every 0x07/0x08 UV chip read clean on this same bench, so the signature is **0x0B-specific**, not seating. This is the same VPP-regulator-instability family as the chip-1 boot refusal (VPP 18.8V>12V, cleared by reset).

- **Phase 83:** MUST NOT write or preserve-dump the irreplaceable 2516 until its read path is stable (blank-state/contents cannot be trusted).
- **Phase 84 FIX-01:** investigate the 0x0B read-path VPP control + the FM1608 blank-check "Empty input" tooling gap.


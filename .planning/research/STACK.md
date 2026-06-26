# Datasheet Acquisition + Tooling Reuse

**Project:** Firestarter — v1.16 Protocol-First Architecture Rebuild
**Researched:** 2026-06-25
**Mode:** Internal refactor (no new product tech). This document adapts the "stack" framing to **(1) the datasheet acquisition list** + **(2) the `datasheets/` folder layout** + **(3) a no-new-deps tooling-reuse confirmation**, because v1.16 adds zero third-party dependencies.

---

## Executive Summary

v1.16 is a rename + datasheet-document + primitive-decompose pass over an already-shipped codebase. The only genuinely *new* artifact this milestone introduces is a top-level `datasheets/` folder. Everything else is **reuse**: the verification harness (`check_dispatch.py`, `diff_db.py`, `write_test.sh`, `dev validate-family`, `gen_test_image.py`, the PlatformIO `[env:native]` Unity + ArduinoFake suite, host pytest/ruff/mypy) already covers the rebuild's needs, and the locked decision (carried in from the seed) is **reuse-first, no new third-party deps**.

The protocol vocabulary the naming pass will author is already half-named in `build_db.py`'s `PROTOCOL_MAP` (e.g. `0x07 → EPROM_STD`, `0x05 → FLASH_AMD_STD`). The datasheets verify that those names + the firmware handler behavior match real silicon. **12 implemented/known protocol buckets** route across **6 firmware handlers** (plus a fail-closed `not_implemented`). The 11 on-hand chips cover **5 of those buckets with silicon**; the rest need a representative datasheet so every protocol has a verification source even when it stays `UNVERIFIED` on the bench.

---

## Protocol Bucket → Handler Map (ground truth, enumerated from the real DB + firmware)

Enumerated from `firestarter_app/firestarter/data/chip_database.json` (`programming.algorithm`), `firestarter_app/tools/build_db.py` (`PROTOCOL_MAP` / `KNOWN_PROTOCOLS`), and `firestarter/src/proms/memory.cpp` (`configure_memory` dispatch).

| protocol_id | `PROTOCOL_MAP` name | Firmware handler (`src/proms/`) | DB chips | On-hand silicon? | Electrical class |
|-------------|---------------------|----------------------------------|----------|------------------|------------------|
| `0x05` | `FLASH_AMD_STD` | `configure_flash4` (flash_type_4.cpp) | 27 | **YES** — W29C020, W29C040 | Flash/EEPROM |
| `0x06` | `FLASH_AMD_ALT` | `configure_flash3` (flash_type_3.cpp) | 190 | **YES** — SST39SF040 | Flash/EEPROM |
| `0x07` | `EPROM_STD` | `configure_eprom` (eprom.cpp) | 170 | **YES** — W27C512, W27E512, SST27SF512, ST M27C512 | UV-EPROM + 7 EEPROM |
| `0x08` | `EPROM_QUICK` | `configure_eprom` (eprom.cpp) | 127 | **YES** — W27E040, AM27C020 | UV-EPROM + EEPROM |
| `0x0B` | `EPROM_LEGACY` | `configure_eprom` (eprom.cpp) | 30 | **YES** — 2516 (user-override entry) | UV-EPROM (NMOS) |
| `0x0D` | `EEPROM_POLL` | `configure_eeprom28c` (eeprom_28c.cpp) | 84 (9 adapter-req) | no | Flash/EEPROM (5V 28C) |
| `0x0E` | `SRAM_32PIN` | `configure_sram` (sram.cpp) | 20 | no | SRAM / NVRAM |
| `0x10` | `FLASH_INTEL` | `configure_flash_intel` (flash_intel.cpp) | 39 | no | Flash (Intel cmd-set) |
| `0x27` | `SRAM_24PIN` | `configure_sram` (sram.cpp) | 2 | no | SRAM |
| `0x28` | `SRAM_STD` | `configure_sram` (sram.cpp) | 34 | **YES** — FM1608 (FRAM) | SRAM + 1 FRAM |
| `0x29` | `SRAM_512K_1M` | `configure_sram` (sram.cpp) | 20 | no | SRAM |
| `0x34` | *(unnamed; XICOR X88C64)* | `configure_not_implemented` (fail-closed) | 1 | no | DIP24 5V NovRAM EEPROM |

Notes:
- **`0x40` is NOT a current protocol_id.** The v1.15-era memory note referencing FM1608 as "0x40 overwrite" is stale — in the shipped DB FM1608 is **`0x28` (`SRAM_STD`)**, FRAM type. The naming pass should reconcile this stale "0x40" reference.
- `0x35`/`0x39` are dispatch-mirrored into `configure_flash4` in firmware (`memory.cpp:89`) but are **phantom protocol_ids** (no chips, removed from `KNOWN_PROTOCOLS`/`PROTOCOL_MAP` in v1.11). Document as "dispatched-but-dead" — do not acquire datasheets.
- `0x11`/`0x2A`/`0x2B`/`0x2C` route to `configure_not_implemented` and are infeasible on RURP (LPC-serial / GAL / PIC). **No datasheet needed** (out of scope per v1.11 finding).
- `0x34` is the one *known-but-not-implemented* DIP-parallel memory; acquire its datasheet so the `UNVERIFIED`/`protocol-not-implemented` row has a rationale source (also feeds the deferred FUT-01 X88C64 handler question).

---

## Part 1 — Datasheet Acquisition List (PRIMARY)

### 1a. On-hand silicon (the 11 v1.15 inventory chips — all must be acquired)

| # | Part (CLI / DB name) | Manufacturer | protocol_id (bucket) | Authoritative datasheet source |
|---|----------------------|--------------|----------------------|--------------------------------|
| 1 | W27C512 | Winbond | `0x07` EPROM_STD | Winbond / Microchip (acquired Winbond memory): search "W27C512 datasheet" on microchip.com; archive: alldatasheet.com W27C512 |
| 2 | W27E512 | Winbond | `0x07` EPROM_STD | Same Winbond W27C512/W27E512 datasheet family (one PDF covers both); Microchip / alldatasheet |
| 3 | SST27SF512 | SST (Microchip) | `0x07` EPROM_STD | **microchip.com** — SST27SF512 is a live Microchip part (DS doc); authoritative |
| 4 | W27E040 | Winbond | `0x08` EPROM_QUICK | Winbond W27C040/W27E040 datasheet; Microchip / alldatasheet archive |
| 5 | SST39SF040 | SST (Microchip) | `0x06` FLASH_AMD_ALT | **microchip.com** — SST39SF010A/020A/040 datasheet (live, authoritative) |
| 6 | W29C020 | Winbond | `0x05` FLASH_AMD_STD | Winbond W29C020(C)/W29C022 datasheet; Microchip / alldatasheet |
| 7 | W29C040 | Winbond | `0x05` FLASH_AMD_STD | Winbond W29C040/W29C040P/W29C042 datasheet; Microchip / alldatasheet |
| 8 | FM1608 | Ramtron (Cypress/Infineon) | `0x28` SRAM_STD (FRAM) | Farnell direct PDF `farnell.com/datasheets/82469.pdf`; alldatasheet 64Kb Bytewide FRAM. **Discontinued — use archive.** |
| 9 | ST M27C512 (DB "M27C512,M27V512,M27W512") | STMicroelectronics | `0x07` EPROM_STD (13V) | STMicroelectronics M27C512 datasheet (st.com legacy / alldatasheet). **CLI name `M27C512`, vpp 13V (not 12V).** |
| 10 | AM27C020 | AMD | `0x08` EPROM_QUICK (13V) | AMD AM27C020 datasheet (alldatasheet / datasheetarchive). **Discontinued AMD — archive.** |
| 11 | 2516 | (generic NMOS, TI/Intel 2516-class) | `0x0B` EPROM_LEGACY | **No minipro entry** — it is a v1.15 user-override DB row. Source the TI/AMD/Intel **2516** (16Kbit NMOS, DIP24, 25V VPP) datasheet from bitsavers / alldatasheet. **Hard to source authoritatively — see "Hard-to-source" below.** |

### 1b. One representative per no-silicon protocol bucket (so every protocol has a datasheet)

Buckets WITHOUT on-hand silicon: `0x0D`, `0x0E`, `0x10`, `0x27`, `0x29`, and the not-implemented `0x34`. Representative parts chosen for **datasheet availability + canonical status** (all confirmed present in the shipped DB).

| protocol_id (bucket) | Representative part | Manufacturer | Why this representative | Authoritative datasheet source |
|----------------------|---------------------|--------------|--------------------------|--------------------------------|
| `0x0D` EEPROM_POLL | **AT28C256** | Atmel (Microchip) | Canonical 5V 32KB parallel EEPROM, ubiquitous, live Microchip doc; exercises data-poll/toggle write algorithm | **microchip.com** AT28C256 datasheet (authoritative, live) |
| `0x0E` SRAM_32PIN | **DS1245** (DS1245Y/AB) | Dallas (Maxim/ADI) | Canonical 32-pin battery-backed NVSRAM; representative of the whole `0x0E` Dallas/ST timekeeper-NVRAM class | analog.com (Maxim/Dallas) DS1245Y datasheet; alldatasheet archive |
| `0x10` FLASH_INTEL | **AM28F010** (or Intel 28F010) | AMD / Intel | Canonical 12V Intel-command-set bulk-erase flash; AM28F010 is in-DB and the cleanest Intel-algo representative | AMD AM28F010 datasheet (alldatasheet); cross-check Intel 28F010 (bitsavers) for the Intel command set |
| `0x27` SRAM_24PIN | **6116** | Generic ("Standard SRAM" in DB) | The archetypal 2KB 24-pin async SRAM; representative of the small-SRAM `0x27` class | Any of TI TMS6116 / Hitachi HM6116 / Sony CXK5816 datasheet (alldatasheet). Pick one and note the silicon-generic nature. |
| `0x29` SRAM_512K_1M | **628128** (HM628128 / equiv) | Generic ("Standard SRAM" in DB) | Archetypal large async SRAM in the `0x29` class; DS1245-style NVRAM also lives here | Hitachi HM628128 datasheet (alldatasheet); a Dallas DS1245-TEST datasheet doubles as cross-check |
| `0x34` *(not-implemented)* | **XICOR X88C64** (X88C64P/S) | Xicor (Renesas) | The one known-but-unimplemented DIP-parallel memory; sourcing its datasheet documents the `protocol-not-implemented` rationale + the deferred FUT-01 handler | **bitsavers.org** Xicor Data Book (1990/1985); alldatasheet X88C64P. **Discontinued — archive only.** |

### Hard-to-source datasheets (flag for the acquisition phase)

- **2516 (`0x0B`)** — There is NO single canonical "2516": it is a generic 16Kbit NMOS EPROM number used by multiple vendors (TI TMS2516, Intel 2716-class equivalents, AMD). It is *deliberately absent from minipro* (v1.15 confirmed the 28 "2516" infoic hits are all `25160` SPI serial parts). Acquire a **representative vendor 2516** (TI TMS2516 or an Intel 2716-family doc) from **bitsavers.org** and annotate the `datasheets/` entry: "user-override DB row; datasheet is a representative NMOS 16Kbit 25V part, not a minipro-traceable chip."
- **AM27C020 (`0x08`)** & **FM1608 (`0x28`)** & **XICOR X88C64 (`0x34`)** — discontinued; manufacturer sites no longer host them. Use **bitsavers.org** (Xicor), **Farnell direct PDF** (FM1608), and **datasheetarchive.com / alldatasheet.com** (AM27C020). Save the PDF locally rather than linking — archive URLs rot.
- **Winbond W27/W29 family** — Winbond's memory line was acquired (by Microchip via Nuvoton legacy / via distributor mirrors). Live manufacturer hosting is inconsistent; alldatasheet/datasheetarchive are the reliable archive. Save locally.

**Sourcing discipline:** Prefer the manufacturer (Microchip for SST + Atmel + Winbond-legacy; ST; Analog/Maxim for Dallas) when live. For discontinued parts, **bitsavers.org** is the most authoritative archive (scanned original data books); **alldatasheet.com / datasheetarchive.com / Farnell** are acceptable secondary archives. Commit the **PDF itself** into `datasheets/`, not just a URL.

---

## Part 2 — `datasheets/` Folder Layout

The seed suggests `datasheets/<protocol-name-or-id>/<part>.pdf`. Recommend keying the subfolder on the **`PROTOCOL_MAP` name prefixed with the hex id**, so the folder *is* the protocol vocabulary the naming pass authors (and a bucket with no datasheet is a visible empty/placeholder dir = an honest gap).

```
datasheets/
  README.md                         # maps hex id <-> PROTOCOL_MAP name <-> handler <-> on-hand status
  0x05-FLASH_AMD_STD/
    W29C020-winbond.pdf             # on-hand
    W29C040-winbond.pdf             # on-hand
  0x06-FLASH_AMD_ALT/
    SST39SF040-microchip.pdf        # on-hand
  0x07-EPROM_STD/
    W27C512-winbond.pdf             # on-hand (covers W27E512)
    SST27SF512-microchip.pdf        # on-hand
    M27C512-st.pdf                  # on-hand (ST, 13V)
  0x08-EPROM_QUICK/
    W27E040-winbond.pdf             # on-hand
    AM27C020-amd.pdf                # on-hand
  0x0B-EPROM_LEGACY/
    2516-ti.pdf                     # on-hand (user-override; representative NMOS)
  0x0D-EEPROM_POLL/
    AT28C256-microchip.pdf          # representative (no silicon)
  0x0E-SRAM_32PIN/
    DS1245-maxim.pdf                # representative (no silicon)
  0x10-FLASH_INTEL/
    AM28F010-amd.pdf                # representative (no silicon)
  0x27-SRAM_24PIN/
    6116-generic.pdf                # representative (no silicon)
  0x28-SRAM_STD/
    FM1608-ramtron.pdf              # on-hand (FRAM)
  0x29-SRAM_512K_1M/
    628128-hitachi.pdf              # representative (no silicon)
  0x34-not-implemented-X88C64/      # known-but-unimplemented; documents the UNVERIFIED row
    X88C64-xicor.pdf                # representative (no silicon)
```

Rationale:
- **Hex-prefix + name** makes the folder self-documenting and stable: when the naming pass renames `0x05 FLASH_AMD_STD -> e.g. flash_amd_5v_software_id`, rename the folder in lockstep, and the datasheet provenance moves with the name.
- **`datasheets/README.md`** is the single index that the per-protocol verification ledger (Q5) and the naming pass (Q4) both reference — it is the bridge from `protocol_id` -> human name -> datasheet -> handler.
- One folder per bucket means **an empty bucket folder is a visible gap** (matches the "honest `UNVERIFIED`" discipline). Buckets `0x35`/`0x39` (phantom) and `0x11`/`0x2A`/`0x2C` (infeasible) get **no folder** — document their exclusion in `README.md` only.
- File naming `<PART>-<vendor>.pdf` disambiguates multi-vendor parts (e.g. `M27C512-st.pdf` vs a hypothetical `M27C512-amd.pdf`).

---

## Part 3 — Tooling / Dependency Confirmation (NO NEW DEPS)

Every harness the rebuild needs already exists and is committed. **No new third-party dependency is required.** Verified against `firestarter_app/pyproject.toml`, `firestarter/platformio.ini`, `firestarter_app/tools/`, and `firestarter_app/firestarter/cli_handlers.py`.

| Need (rebuild stage) | Existing tool (reuse) | Location | Covers? |
|----------------------|------------------------|----------|---------|
| Dispatch / VPP-safety regression gate (refactor must not re-route a chip to a wrong/hazardous handler) | `check_dispatch.py` (GATE-03 structural + WARNING-5 type-keyed guards, 744-chip gate) | `firestarter_app/tools/check_dispatch.py` | **YES** — primary refactor safety net |
| Per-chip DB diff vs pinned baseline (naming pass must not silently change control values) | `diff_db.py` + `tools/baseline/chip_database.baseline.json` | `firestarter_app/tools/` | **YES** |
| HIL write->read->verify per family on Leonardo | `dev validate-family` + `write_test.sh` / `write_test_port.sh` | `cli_handlers.py` `dev` group; `firestarter_app/*.sh` | **YES** — the bench-validation stage |
| Deterministic test-image oracle | `gen_test_image.py` | `firestarter_app/tools/gen_test_image.py` | **YES** |
| Native register-level handler tests (primitive decomposition guard) | PlatformIO `[env:native]` Unity + ArduinoFake; per-family `test_val_*` suites already exist (`test_val_eprom`, `test_val_eeprom28c`, `test_val_flash3`, `test_val_flash4`, `test_val_flash_intel`, `test_val_sram`) + `test_dispatch` / `test_not_implemented` | `firestarter/test/native/avr/`; `firestarter/platformio.ini` | **YES** — this is exactly the "native register-level tests" the seed names |
| Host lint/type/coverage gate | `ruff` + `ruff format` + `mypy` (strict on 8 modules) + `pytest --cov-fail-under=70` | `pyproject.toml` `[project.optional-dependencies].test`; `.github/workflows/ci.yml` | **YES** |
| Validation-matrix codegen (per-family matrix from v1.13) | `gen_validation_header.py` + `validation_matrix_spec.json` | `firestarter_app/tools/` | **YES** — composes with the new per-protocol ledger (Q5) |
| Coverage-matrix audit | `audit_coverage_matrix.py` | `firestarter_app/tools/` | **YES** |

**Declared dependency surface (confirmed, unchanged):**
- Host runtime: `pyserial>=3.5`, `click>=8.1`.
- Host test/dev: `pytest`, `ruff>=0.15.14`, `mypy>=2.1.0`, `pytest-cov`, `types-pyserial`.
- Firmware native test: `fabiobatsilva/ArduinoFake@^0.4.0` + Unity (PlatformIO built-in).
- **No addition is needed for v1.16.** PDFs in `datasheets/` are static documents, not a build/runtime dependency.

### Reuse-based extension gaps (small, NOT new deps)

These are *recommended documentation/glue additions*, all reuse-only — none introduces a third-party dependency:

1. **`datasheets/README.md` as the protocol-vocabulary index** — new markdown file (no dep). It is the canonical `hex id <-> name <-> handler <-> datasheet <-> on-hand` table feeding Q4 (naming map) and Q5 (ledger).
2. **Per-protocol verification ledger** (Q5) — author as a new markdown/JSON artifact that *composes with* (does not replace) the existing `validation_matrix_spec.json` (v1.13 per-family) + the v1.15 `EVIDENCE.{md,json}`. Reuse the `gen_validation_header.py` codegen pattern if a machine-readable form is wanted; no new tool.
3. **Optional: a tiny `check_dispatch.py` assertion that every `KNOWN_PROTOCOLS` id has a `datasheets/<id>-*/` folder** — a reuse-based extension to the *existing* gate (pure stdlib `os.path`), turning "every protocol has a verification source" into an enforced invariant. Not required; nice-to-have.
4. **`0x40`/`0x28` stale-reference reconciliation** — a documentation correction in the naming pass (the memory note's "FM1608 0x40" is stale; DB says `0x28`). No tooling.

**Do NOT add:** any PDF parser, any new test framework, any DB/ORM, any HTTP client for datasheet fetching (fetch manually, commit the PDF). The reuse-first constraint holds cleanly.

---

## Confidence Assessment

| Area | Confidence | Reason |
|------|------------|--------|
| Protocol bucket enumeration | HIGH | Read directly from shipped `chip_database.json` + `build_db.py` + `memory.cpp` |
| On-hand part -> protocol_id mapping | HIGH | Matched 10/11 parts in the shipped DB by part_number; 2516 confirmed as user-override per v1.15 close notes |
| Representative no-silicon parts | HIGH | All confirmed present in the shipped DB (AT28C256, DS1245, AM28F010, 6116, 628128, X88C64) |
| Datasheet source URLs | MEDIUM | Common/live parts (SST, Atmel/Microchip, ST) authoritative; discontinued parts (FM1608, AM27C020, X88C64, 2516) rely on bitsavers/Farnell/alldatasheet archives — verify the saved PDF matches the silkscreen part at acquisition |
| No-new-deps claim | HIGH | Verified against `pyproject.toml`, `platformio.ini`, and the `tools/` + `dev`-group inventory; every harness already exists |

## Gaps to Address (at acquisition time)

- **2516** has no canonical vendor datasheet — pick a representative (TI TMS2516 / Intel 2716-family from bitsavers) and annotate the provenance.
- Discontinued-part PDFs must be **committed locally** (archive URLs rot); verify each saved PDF's part/voltage matches the DB row (esp. ST M27C512 = 13V, AM27C020 = 13V).
- The stale **`0x40` FM1608** reference in project memory should be reconciled to **`0x28`** during the naming pass (documentation only).

## Sources

- Live DB/firmware: `firestarter_app/firestarter/data/chip_database.json`, `firestarter_app/tools/build_db.py`, `firestarter/src/proms/memory.cpp`, `firestarter/platformio.ini`, `firestarter_app/pyproject.toml` (HIGH).
- [XICOR X88C64 — Xicor 1990 Data Book (bitsavers)](https://www.bitsavers.org/components/xicor/1990_Xicor_Data_Book.pdf) (MEDIUM, archive)
- [XICOR X88C64P — alldatasheet](https://www.alldatasheet.com/datasheet-pdf/pdf/34232/XICOR/X88C64P.html) (MEDIUM, archive)
- [Ramtron FM1608 — Farnell direct PDF](https://www.farnell.com/datasheets/82469.pdf) (MEDIUM, distributor archive)
- [Ramtron FM1608 — alldatasheet](https://www.alldatasheet.com/datasheet-pdf/pdf/80224/RAMTRON/FM1608.html) (MEDIUM, archive)

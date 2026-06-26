# Project Research Summary

**Project:** Firestarter — v1.16 Protocol-First Architecture Rebuild
**Domain:** Internal firmware-architecture refactor of an existing Arduino EPROM/Flash/SRAM programmer (PlatformIO/AVR firmware + Python host CLI) — NOT a new product
**Researched:** 2026-06-25
**Confidence:** HIGH

## Executive Summary

v1.16 is an **internal refactor**, not a feature build. The firmware already ships and works; the goal is to turn the inherited-from-minipro hex-ID `protocol_id` buckets into a *named, datasheet-verified, primitive-decomposed* architecture and to recover Leonardo flash headroom (currently a **measured 89.5%** against a ~90% ceiling) by collapsing duplicated per-handler code into shared primitives. The minipro/infoic-derived `chip_database.json` stays the ground truth for firmware control values; datasheets only verify the *interpretation* and document each handler's *why*. Every harness the rebuild needs already exists (`check_dispatch.py`, `diff_db.py`, the PlatformIO native `test_val_*` suites, `dev validate-family`, `gen_test_image.py`, host ruff/mypy/pytest) — **zero new third-party dependencies**, the only genuinely new artifact being a top-level `datasheets/` folder.

The work decomposes into a **staged shape** that the four researchers converge on cleanly: (1) **datasheet acquisition** — the 11 on-hand chips plus one representative per no-silicon bucket, so every protocol has a verification source; (2) a **naming + documentation pass** that authors the protocol vocabulary and enumerates each handler's accreted one-off fixes as named invariants — near-zero flash delta, lands first, stabilizes the map the refactor works against; (3) **incremental per-family primitive recompose** — one family per phase, guarded by native register-level golden traces + `check_dispatch.py` + `diff_db.py`, with a ≤90% flash gate measured every step; (4) **per-protocol bench validation** authoring a new `PROTOCOL-LEDGER.{md,json}` that *composes with* (does not replace) the v1.13 per-family matrix and the v1.15 per-chip EVIDENCE. The shared-primitive analysis is grounded in *measured* flash (`avr-nm` on the linked ELF, not estimates): ~850–1,300 B is realistically recoverable via three primitives — the **VPP gate**, **chip-ID compare/report**, and a **poll loop** — moving the build from 89.5% to roughly **85–86.5%**.

The dominant risk is that this is **a refactor that can physically destroy silicon**. A wrong VPP rail or a dropped one-off fix on an irreplaceable UV-EPROM is unrecoverable, and the *only* trustworthy read/write oracle is **Leonardo + RURP Rev 2.0** (the v1.9 read bug corrupts every other board/shield). Two scoping facts steer the roadmap: (a) the refactor is **firmware-only / host-untouched**, so it ships firmware-first with **NO dual-repo lockstep** *unless* a behavior fix rides along — this reverses the seed's default lockstep assumption; (b) the central hazard is the **algorithm-axis (`protocol_id`) vs. electrical-axis (`electrical.type`) tangle** — any primitive must key on `handle->protocol`, never on the type string. Mitigation is built into the staging: document-before-recompose, native golden-trace under test before any primitive moves, and the structural `check_dispatch.py` / `diff_db.py` gates as mandatory per-phase exit criteria.

## Key Findings

### Recommended Stack

There is no new stack — v1.16 adds **zero third-party dependencies**, confirmed against `pyproject.toml`, `platformio.ini`, and the `tools/` + `dev`-group inventory. The "stack" reduces to a **datasheet acquisition list** and a **`datasheets/` folder layout**, plus a confirmation that the existing verification harness already covers every rebuild need. The chip database stays the authoritative source of control values; datasheets are a static rationale layer committed as PDFs (archive URLs rot — commit the file, not the link).

**Core technologies (all reuse):**
- `datasheets/<hex>-<NAME>/<part>-<vendor>.pdf` + `datasheets/README.md` — the only new artifact; the folder *is* the protocol vocabulary, an empty bucket folder is a visible honest gap.
- `check_dispatch.py` + `diff_db.py` (host) — the 744-chip VPP-safety gate + per-chip baseline diff; the primary refactor safety net (both must exit 0 every phase).
- PlatformIO `[env:native]` Unity + ArduinoFake `test_val_*` / `test_dispatch` suites (firmware) — the register-level golden-trace oracle that makes recompose a refactor-under-test.
- `dev validate-family` / `write_test.sh` / `dev consistency-check` / `gen_test_image.py` — the bench-validation tier (Leonardo + Rev 2.0).
- `gen_validation_header.py` + `validation_matrix_spec.json` — the v1.13 codegen pattern the new per-protocol ledger reuses (no new tool).

**Datasheet sourcing discipline:** prefer live manufacturer (Microchip for SST/Atmel/Winbond-legacy, ST, Analog/Maxim for Dallas); for discontinued parts (FM1608, AM27C020, X88C64, 2516) use bitsavers/Farnell/alldatasheet and commit the PDF locally. The **2516 has no canonical vendor datasheet** (it is a v1.15 user-override DB row, genuinely absent from minipro) — pick a representative NMOS 16Kbit part and annotate the provenance.

### Expected Features — the protocol vocabulary

The deliverable here is the **protocol vocabulary table** the naming pass produces. The live `chip_database.json` (744 chips) contains **exactly 12 distinct `protocol_id` buckets** routing across **6 firmware handlers** plus a fail-closed `not_implemented`. **There is NO `0x40` bucket** — the project memory's "FM1608 0x40" conflated decimal `40` with hex; FM1608's algorithm is decimal 40 = **`0x28` (SRAM_STD, FRAM)**. Reconciling this is an in-scope documentation correction.

**The 12 buckets and silicon coverage (the per-protocol ledger seed):**

| protocol_id | proposed name | handler | on-hand silicon | verification state |
|---|---|---|---|---|
| `0x05` FLASH_AMD_STD | Flash-AMD-PageWrite | configure_flash4 | W29C020, W29C040 | **PARTIAL** — W29C020 PASS (first auto-erase proof); W29C040 256B page-0 FAIL (CR-01) |
| `0x06` FLASH_AMD_ALT | Flash-AMD-Unlock-SectorErase | configure_flash3 | SST39SF040 | **VERIFIED** (largest bucket, 190 chips) |
| `0x07` EPROM_STD | EPROM-Program-1ms | configure_eprom | W27C512, SST27SF512, ST M27C512 | **VERIFIED** (axis hazard: 163 UV + 7 EEPROM) |
| `0x08` EPROM_QUICK | EPROM-Program-100us-Large | configure_eprom | W27E040, AM27C020 | **UNVERIFIED for write** — AM27C020 0-bits FAIL (FUT-06) |
| `0x0B` EPROM_LEGACY | EPROM-Program-500us-DirectVPE-24pin | configure_eprom | 2516 | **UNVERIFIED** — read unstable, 3 SHAs (FUT-03) |
| `0x0D` EEPROM_POLL | EEPROM-28C-PageWrite-SDP | configure_eeprom28c | none | **UNVERIFIED** — 9 members adapter-required (FUT-04) |
| `0x0E` SRAM_32PIN | SRAM-RW-32pin | configure_sram | none | **UNVERIFIED** |
| `0x10` FLASH_INTEL | Flash-Intel-CommandRegister | configure_flash_intel | none | **UNVERIFIED** — no 28F silicon at all |
| `0x27` SRAM_24PIN | SRAM-RW-24pin | configure_sram | none | **UNVERIFIED** |
| `0x28` SRAM_STD | SRAM-RW-NVRAM | configure_sram | FM1608 (FRAM) | **VERIFIED** (overwrite) |
| `0x29` SRAM_512K_1M | SRAM-RW-512K-1M | configure_sram | none | **UNVERIFIED** |
| `0x34` (unnamed; X88C64) | EEPROM-X88C64-MultiplexedBus | configure_not_implemented | none | **UNVERIFIED / not-implemented** (PCB-blocked ALE) |

**Summary:** 4 buckets have a clean on-hand PASS (0x06, 0x07, 0x28, plus 0x05 via W29C020); 2 have on-hand silicon with open defects (0x08, 0x0B); **6 stay explicit UNVERIFIED** (0x0D, 0x0E, 0x10, 0x27, 0x29, 0x34) — honest gaps, never false confidence.

**Must keep honest (anti-features / phantoms):**
- `0x35` / `0x39` — dispatched into `configure_flash4` in firmware but **zero DB chips** (excluded from host `KNOWN_PROTOCOLS`). Document as "dispatched-but-dead" phantoms; no datasheet, no folder.
- `0x11` / `0x2A` / `0x2B` / `0x2C` — infeasible on RURP (LPC-serial / GAL / PIC); fail-closed. No datasheet, no folder.

**Two in-scope decode corrections (documentation, not wire change):**
1. **FM1608 0x40 → 0x28** — reconcile the stale project-memory/DB mismatch (it is FRAM on SRAM_STD).
2. **0x34 X88C64 `electrical.type` UV-EPROM → EEPROM** — the type is mis-set on a 5V multiplexed-bus EEPROM; flag/fix in the naming pass.

### Architecture Approach

The dispatch spine (`memory.cpp::configure_memory`, protocol-first) and the state-machine engine (`operation_utils.cpp`) are **already well-factored shared layers and must stay byte-for-byte stable**. The duplication this milestone targets is concentrated **inside the seven `configure_*` handlers**. Flash is **measured** (`avr-nm --print-size` on `firestarter_leonardo.elf`): families total ~9,186 B of the 25,666 B image; the other ~16,100 B is USB-CDC/Serial/JSON/CRC/COBS/AVR runtime this milestone does **not** touch.

**Major components / shared-primitive inventory (P1–P8):**
1. **P1 Address setup / P2 Data strobe** — already shared; document only (0 B).
2. **P3 VPP gate** — duplicated ×2 (×4 byte-packing blocks) across `eprom_check_vpp` (532 B) + `flash_intel_check_vpp`; the regulator-routing bits are the only real variable. **~350–450 B recoverable — the single largest concentrated duplication.**
3. **P4 Chip-ID compare/report** — duplicated ×4 (eprom/intel/eeprom28c + the already-shared flash_utils proving it factors); split read-mechanism (protocol-specific) from compare/report (shared). **~250–350 B.**
4. **P5 Write-with-verify / poll loop** — extract only a parameterized `poll_readback`; **leave the outer retry/page algorithms per-protocol** (they are genuinely different silicon algorithms). **~200–300 B.**
5. **P7 SDP const-table dedup** — `FLASH_ENABLE_WRITE_PROTECTION` is byte-identical dead duplication; `EEPROM_SDP_DISABLE` duplicates `FLASH_DISABLE_WRITE_PROTECTION`. **~40–80 B, near-zero risk — the warm-up task.**
6. **P6 Page buffer / P8 Erase** — mostly protocol-specific; share only the poll/guard.

**Total realistically recoverable: ~850–1,300 B → 89.5% down to ~85–86.5%.** Recompose order is biggest-saving × lowest-risk × dependency-first: **Step 0** pin golden register traces (no code change) → **Step 1** P7 tables → **Step 2** P4 chip-ID report → **Step 3** P3 VPP gate → **Step 4** P5 poll. Dispatch and the host are untouched throughout; `diff_db.py` must show an empty diff the whole milestone.

### Critical Pitfalls

1. **Re-tangling the algorithm axis with the electrical axis** — a "VPP primitive" that switches on `electrical.type` instead of `handle->protocol` re-introduces the exact 12V-on-a-5V-pin hazard class the project keeps paying down. Key every primitive on `protocol`; preserve the structural `novpp_in_eprom` / `eeprom28c_in_eprom` (WARNING-5) guards.
2. **Silently dropping one of the 8 accreted one-off fixes during recompose** — `0x0B` direct-VPE rail, `0x0B` shared OE/VPP read-skip, `0x08` P1-as-VPP, flash4 256B page boundary, VPP-skip on reads, pulse-delay defaults (100/500/1000µs), FM1608 SRAM→FRAM relabel, WARNING-5 `0x07`→`0x0D` override, SST39SF040 D-40 keep-Flash/EEPROM. Their *why* lives in commits/STATE, not code → the naming pass must enumerate each as a named behavior-contract invariant, asserted under a native test, **before** any code moves.
3. **A "cleanup" that *adds* flash and wedges the ~90% gate** — abstraction is not free on AVR; a generic primitive with function-pointer indirection can compile *larger* than inlined handlers, and PROGMEM doc strings cost flash. Measure `pio run -e leonardo` every step; net increase = STOP; keep vocabulary host-side.
4. **Silicon-destruction VPP-axis tangle + non-authoritative oracle** — over-voltage stays *blocked* at the firmware check (only under-voltage is warn-and-proceed per D-07); never bypass the `chip_resolver.resolve_chip` host guard; **only Leonardo + RURP Rev 2.0 counts as a PASS** (the ledger schema makes board/shield/evidence mandatory columns so a non-authoritative PASS is structurally impossible). Never write an irreplaceable UV part on an unstable read path (the 2516 stays UNVERIFIED).
5. **`check_dispatch.py::dispatch()` mirror drift + the py3.12-masks-CI-3.11 ruff/codegen trap** — the gate is a hand-maintained copy of firmware dispatch; a refactor that reorders dispatch silently makes it validate a fiction (add a dispatch-mirror-matches-doc test). Validate ruff/format/mypy against the CI target, not the 3.12 devcontainer; never hand-normalize generated `messages.py`.

## Implications for Roadmap

Research converges strongly on the seed's four-stage shape. Suggested phases (numbering continues at **Phase 85**):

### Phase 1: Datasheet Acquisition + `datasheets/` Folder
**Rationale:** Every later stage needs a verification source per protocol; this has no code risk and unblocks the naming pass. Lands first.
**Delivers:** `datasheets/<hex>-<NAME>/` for the 11 on-hand chips + one representative per no-silicon bucket (AT28C256, DS1245, AM28F010, 6116, 628128, X88C64) + `datasheets/README.md` (hex ↔ name ↔ handler ↔ datasheet ↔ on-hand index). No folder for phantom (0x35/0x39) or infeasible (0x11/0x2A/0x2B/0x2C) buckets — document exclusion in README only.
**Addresses:** FEATURES vocabulary completeness; STACK acquisition list.
**Avoids:** none (no code) — but flags the hard-to-source PDFs (2516, FM1608, AM27C020, X88C64) and the local-commit discipline.

### Phase 2: Naming + Documentation Pass (structure-stable, near-zero flash)
**Rationale:** Authors the protocol vocabulary and the per-family behavior contract *before* any primitive moves — stabilizes the map the refactor works against. Dispatch unchanged; wire values unchanged.
**Delivers:** the 12-bucket protocol vocabulary (proposed names on the algorithm axis), each handler's documented *why*, the **8 one-off fixes enumerated as named invariants**, and the two in-scope decode corrections (FM1608 0x40→0x28; 0x34 UV-EPROM→EEPROM). Phantom/infeasible buckets explicitly named.
**Avoids:** Pitfall 1 (axis vocabulary owned), Pitfall 2 (invariants enumerated), Pitfall 3 (prove near-zero flash delta — keep vocabulary out of PROGMEM).

### Phase 3: Pin Golden Register Traces + Dispatch-Mirror Test (recompose prerequisite)
**Rationale:** A small guard-establishing phase before any extraction: capture the exact control-register + data sequence each handler emits today (the recompose oracle), and add the `check_dispatch.py::dispatch()`-matches-documented-order test.
**Delivers:** per-family native `test_val_*` golden traces (capture-before); the dispatch-mirror invariant test.
**Avoids:** Pitfall 5 (mirror drift), Pitfall 2 (refactor-under-test).

### Phase 4..N: Incremental Per-Family Primitive Recompose (one primitive/family per phase)
**Rationale:** Biggest-saving × lowest-risk × dependency-first ordering, each step independently gated and reversible.
**Delivers:** Step 1 P7 table dedup (~40–80 B, warm-up) → Step 2 P4 chip-ID report (~250–350 B) → Step 3 P3 VPP gate (~350–450 B, biggest) → Step 4 P5 poll (~200–300 B, touches bench-proven write paths). Running flash logged 89.5% → ≤86.5%.
**Uses:** STACK harness reuse; ARCHITECTURE recompose order + proposed APIs (`vpp_check_window`, `chip_id_report`, `chip_id_read_a9_12v`, `poll_readback`).
**Avoids:** Pitfall 3 (per-step `pio run -e leonardo` ≤90% gate), Pitfall 4 (firmware-only → no lockstep unless a fix rides along), Pitfall 6 (`check_dispatch.py` + `diff_db.py` exit 0, zero DB diff).

### Phase N+1: Per-Protocol Bench Validation + PROTOCOL-LEDGER
**Rationale:** Bench-prove each protocol that has silicon on Leonardo + Rev 2.0; record the rebuild-survival dimension the existing layers lack.
**Delivers:** `.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}` (NEW artifact) composing with v1.13 `validation_matrix_spec.json` (by `family_id`) + v1.15 `EVIDENCE.json` (by chip+sha) — adds name, datasheet citation, primitives, flash delta, and verification status per bucket. PASS rows structurally require `oracle: leonardo+Rev2.0` + non-empty `evidence_refs`; 6 buckets recorded explicit UNVERIFIED.
**Avoids:** Pitfall 4 (authoritative-oracle-only PASS), Pitfall 8 (host-guard chokepoint, spend-after-stable-read).

### Phase Ordering Rationale
- **Dependency-first:** datasheets → vocabulary/invariants → golden-trace guards → recompose → bench ledger. You cannot safely recompose a family before its behavior contract is written and its golden trace pinned.
- **Reuse-payback ordering inside the recompose:** extract the highest-call-site primitive early so the flash curve trends down monotonically (P7 warm-up → P4 → P3 → P5-last because it touches W29C020/W27C512 write paths).
- **Scoping fact:** the refactor is firmware-only/host-untouched → ships firmware-first with **NO dual-repo lockstep** *unless* a primitive extraction is paired with a behavior fix (then lockstep + the py3.12/CI ruff discipline applies). This is a deliberate correction of the seed's default lockstep assumption.

### Research Flags

Phases likely needing deeper research (`--research-phase`) during planning:
- **Phase 4..N (recompose), per family touching VPP/chip-ID:** the proposed primitive APIs need per-family register-trace verification against the golden capture; the regulator-bit parameterization (0x07/0x08 dropping path vs 0x0B direct-VPE vs 0x10 P1) is the hazard surface.
- **Bench-validation phase for the 6 UNVERIFIED buckets:** datasheet-documentable now, but only bench-confirmable when silicon is acquired — flag which stay UNVERIFIED vs CHIP-NEEDED.

Phases with standard patterns (skip research-phase):
- **Phase 1 (datasheet acquisition):** mechanical; the list + folder layout are specified.
- **Phase 2 (naming/documentation):** the vocabulary + invariants are fully enumerated in FEATURES + PITFALLS.
- **Phase 3 + P7 warm-up:** well-understood, near-zero risk; `flash_utils.cpp` is the proven template.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack (datasheets + no-new-deps) | HIGH | Verified against pyproject.toml/platformio.ini/tools inventory; every harness exists. Datasheet *source URLs* are MEDIUM for discontinued parts (bitsavers/Farnell/alldatasheet — verify saved PDF matches silkscreen + voltage at acquisition). |
| Features (protocol vocabulary) | HIGH | Every row enumerated from the live DB + cross-checked against `memory.cpp` dispatch + handler sources. MEDIUM only on exact `IC2_ALG_*` semantics for 0x27/0x29 (last re-verified v1.11). |
| Architecture (primitives + flash) | HIGH | Primitives derived from actual handler source; flash numbers **measured** via `avr-nm` on the linked ELF, not estimated. |
| Pitfalls | HIGH | Grounded in the real fix history in STATE.md, the live gate scripts, the lockstep parity surface, and v1.13/v1.15 verification artifacts. |

**Overall confidence:** HIGH

### Gaps to Address
- **6 buckets have no on-hand silicon** (0x0D, 0x0E, 0x10, 0x27, 0x29, 0x34) — datasheet-documentable but only bench-confirmable when chips are acquired; carry as explicit UNVERIFIED in the ledger.
- **2516 (`0x0B`) has no canonical datasheet** and an unstable read path (FUT-03) — acquire a representative NMOS part, annotate provenance, do NOT spend the chip.
- **Open defects feeding the ledger, not this milestone's fix scope:** W29C040 flash4 256B (CR-01 / Phase-74 Wave-2), AM27C020 0x08 0-bits write (FUT-06). Recompose must preserve their current (buggy-but-documented) behavior, not silently change it.
- **Lockstep boundary:** firmware-only refactor needs no lockstep; if a behavior fix is bundled into a recompose step, that step becomes a dual-repo lockstep commit pair with the constants-parity test + CI-target ruff/codegen preflight.

## Sources

### Primary (HIGH confidence)
- `.planning/research/{STACK,FEATURES,ARCHITECTURE,PITFALLS}.md` — the four researcher outputs synthesized here.
- Live repo: `firestarter_app/firestarter/data/chip_database.json`, `tools/build_db.py` (PROTOCOL_MAP), `tools/{check_dispatch.py,diff_db.py,validation_matrix_spec.json}`, `firestarter/src/proms/*.cpp`, `firestarter/include/*.h`, `firestarter/test/native/avr/`, `pyproject.toml`, `platformio.ini`.
- Measured: `avr-nm --print-size --size-sort -C .pio/build/leonardo/firestarter_leonardo.elf` (25,666 B = 89.5%).
- `.planning/STATE.md`, `.planning/v1.15/bench/EVIDENCE.{md,json}`, `firestarter/CLAUDE.md` (dispatch table + parity rule), `.planning/seeds/protocol-first-architecture-rebuild.md`, `.planning/PROJECT.md` v1.16 section.

### Secondary (MEDIUM confidence)
- XICOR X88C64 datasheet (bitsavers / RS-Online / alldatasheet) — confirms ALE multiplexed bus + toggle-bit poll for the 0x34 row.
- Ramtron FM1608 (Farnell direct PDF / alldatasheet) — discontinued, archive only.
- AM27C020 (AMD, alldatasheet/datasheetarchive) and the representative 2516 (bitsavers TI/Intel 2716-family) — discontinued/generic, provenance to annotate at acquisition.

---
*Research completed: 2026-06-25*
*Ready for roadmap: yes*

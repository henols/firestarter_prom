# v1.15 — Decode-Correctness Audit (SC#1)

**Scope:** 11 chips from the operator's physical inventory, exercised on Leonardo + RURP Rev 2.0 across Phases 81–83.

**Purpose:** Consolidated milestone-close artifact confirming real-silicon behaviour vs the chip database (DB) for every chip's decode attributes (pinout, VPP, electrical type, algorithm, size). Every mismatch is recorded with a disposition. Cross-references `EVIDENCE.{md,json}` for raw bench data.

**Source data:** `.planning/v1.15/bench/EVIDENCE.md` and `EVIDENCE.json` — the per-chip bench log authorised across Phases 81–83. This doc consolidates and disposition-annotates that raw record.

**Status:** SC#1 consolidated decode audit — Wave-1 (84-01/02/03) outcomes incorporated; bench-pending items (84-05 re-bench) marked `PENDING 84-05`.

---

## Part 1 — Per-Chip Decode-Correctness Table

Each row covers the five DB-claimed attributes: **pinout**, **VPP**, **electrical type**, **algorithm**, and **size**. Verdict is `CONFIRMED` (silicon matched the DB) or `MISMATCH` (with disposition). Cross-reference column links to the EVIDENCE row.

### Chips 1–5: 0x07 Family (EPROM_STD) + 0x08 (EPROM_QUICK)

| # | Chip | DB Algorithm (proto_id) | EVIDENCE Verdict | Pinout | VPP | Electrical Type | Algorithm (proto) | Size |
|---|------|------------------------|-----------------|--------|-----|-----------------|-------------------|------|
| 1 | W27C512 | 0x07 (EPROM_STD / EEPROM) | PASS (Phase 82 write) | CONFIRMED — DIP28_27512 | CONFIRMED — 12V | CONFIRMED — EEPROM | CONFIRMED — 0x07 | CONFIRMED — 65536 B |
| 2 | W27E512 | 0x07 (EPROM_STD / EEPROM) | FAIL (genuine) Phase 82 | CONFIRMED — DIP28_27512 | CONFIRMED — 12V | CONFIRMED — EEPROM | CONFIRMED — 0x07 | CONFIRMED — 65536 B |
| 3 | SST27SF512 | 0x07 (EPROM_STD / EEPROM) | PASS (Phase 82 write) | CONFIRMED — DIP28_27512 | CONFIRMED — 12V | CONFIRMED — EEPROM | CONFIRMED — 0x07 | CONFIRMED — 65536 B |
| 4 | W27E040 | 0x08 (EPROM_QUICK / EEPROM) | FAIL (genuine) Phase 82 | CONFIRMED — DIP32_STD | CONFIRMED — 12V | CONFIRMED — EEPROM | CONFIRMED — 0x08 | CONFIRMED — 524288 B |
| 5 | ST M27C512 | 0x07 (EPROM_STD / UV-EPROM) | PASS (Phase 83 write) | CONFIRMED — DIP28_27512 | MISMATCH — see note | CONFIRMED — UV-EPROM | CONFIRMED — 0x07 | CONFIRMED — 65536 B |

**W27E512 decode note:** The DB decode was correct — EEPROM / 0x07 / DIP28 / 12V / 65536 B. The FAIL was a genuine stuck erase bit (@0x3d, reads 0x7f want 0xFF) deterministic across N=3 reseats — silicon wear, NOT a decode mismatch. Disposition: D-32 (silicon-limited).

**W27E040 decode note:** Same class as W27E512 — DB decode correct (EEPROM / 0x08 / DIP32 / 12V / 524288 B). The FAIL was a genuine stuck erase bit (@0x7db, reads 0xEF want 0xFF) deterministic across N=2 reseats — silicon wear, NOT a decode mismatch. Disposition: D-32 (silicon-limited).

**ST M27C512 VPP mismatch note:** The Phase-83 plan stated 12V; the actual DB VPP is **13V** (confirmed by live bench). The bench firmware applied 13V correctly. This was a plan-text error, NOT a DB error. EVIDENCE.json `decode_uv04` records `13V`. Disposition: PLAN-TEXT only, DB is correct.

---

### Chips 6–8: 0x06 (FLASH_AMD_ALT) + 0x05 (FLASH_AMD_STD)

| # | Chip | DB Algorithm (proto_id) | EVIDENCE Verdict | Pinout | VPP | Electrical Type | Algorithm (proto) | Size |
|---|------|------------------------|-----------------|--------|-----|-----------------|-------------------|------|
| 6 | SST39SF040 | 0x06 (FLASH_AMD_ALT / Flash) | PASS (Phase 82 write) | CONFIRMED — DIP32_SST39SF040 | CONFIRMED — 12V | MISMATCH — see note | CONFIRMED — 0x06 | CONFIRMED — 524288 B |
| 7 | W29C040 | 0x05 (FLASH_AMD_STD / Flash/EEPROM) | FAIL (genuine) Phase 82 | CONFIRMED — DIP32 | CONFIRMED — 12V | CONFIRMED — Flash/EEPROM | CONFIRMED — 0x05 | CONFIRMED — 524288 B |
| 8 | W29C020 | 0x05 (FLASH_AMD_STD / Flash/EEPROM) | PASS (Phase 82 write) | CONFIRMED — DIP32 | CONFIRMED — 12V | CONFIRMED — Flash/EEPROM | CONFIRMED — 0x05 | CONFIRMED — 262144 B |

**SST39SF040 electrical type MISMATCH — observation, sst-keep disposition:**

The DB records `electrical.type = "Flash/EEPROM"` while the minipro upstream classification and algorithm family (0x06 / FLASH_AMD_ALT) indicate the chip is architecturally `Flash`. Silicon confirms it operates as a Flash device — block erase + byte program, no EEPROM-style page-write polling.

However, `electrical.type` is the **sole input** to `FLAG_CAN_ERASE` at `database.py:605`. SST39SF040 requires `Flash/EEPROM` membership to preserve `FLAG_CAN_ERASE = 0x02` on the wire, enabling the Phase-77/82-proven auto-erase path (REWR-03 confirmed on silicon — B over A verified clean). Relabeling to `Flash` would drop FLAG_CAN_ERASE and break erase — a regression forbidden by D-40 (sst-keep decision, Phase 84-03).

**Disposition (sst-keep):** `Flash/EEPROM` label is KEPT deliberately. It is functionally correct for RURP's purposes even if cosmetically imprecise vs upstream. A proper fix would require decoupling the display label from the erase-flag derivation (`sst-decouple` path — not authorized this phase). Recorded as an observation, not a blocking mismatch.

**W29C040 decode note:** The DB decode was correct (DIP32 / Flash/EEPROM / 12V / 524288 B / 0x05 — confirmed by `firestarter info`). The FAIL was a flash4 256B page-write timeout at the page-0 boundary (byte @0x0000FF, reads 0x00 — per-page auto-erase not confirmed). Deterministic across initial + 1 reseat. This is a write-path DEFECT, NOT a decode mismatch. Disposition: PENDING 84-05 bench (Phase 84 FIX-01 re-bench).

---

### Chips 9–10: 0x40 (SRAM_STD / FRAM) + 0x08 (Large EPROM / UV-EPROM)

| # | Chip | DB Algorithm (proto_id) | EVIDENCE Verdict | Pinout | VPP | Electrical Type | Algorithm (proto) | Size |
|---|------|------------------------|-----------------|--------|-----|-----------------|-------------------|------|
| 9 | FM1608 | 0x40 (SRAM_STD / FRAM) | PASS (Phase 82 overwrite) | CONFIRMED — DIP28_JEDEC_SRAM_8K | MISMATCH — see note | MISMATCH → CORRECTED | CONFIRMED — 0x40 | CONFIRMED — 8192 B |
| 10 | AM27C020 | 0x08 (EPROM_QUICK / UV-EPROM) | ANOMALY (Phase 83 write) | CONFIRMED — DIP32 | MISMATCH — see note | CONFIRMED — UV-EPROM | CONFIRMED — 0x08 | CONFIRMED — 262144 B |

**FM1608 electrical type MISMATCH → CORRECTED (fm-fram-full, Phase 84-03):**

The DB originally recorded `electrical.type = "SRAM"` while the physical device is a **Ferroelectric RAM (FRAM)** — non-volatile, no destructive erase, overwrite-in-place. This was a decode mismatch. Silicon confirmed FRAM behaviour in Phase 82 (overwrite proof: B over A, clean read-back SHA match, no erase step needed or possible).

**Disposition (fm-fram-full):** Phase 84-03 shipped the correction: `build_db.py` per-chip override sets `electrical.type = "FRAM"` for FM1608; `_ELECTRICAL_TYPE_LABEL` extended; VPP display gate widened to `not in {"SRAM", "FRAM"}` (FM1608 has vpp_mv=12000 from infoic.xml artifact, now hidden); `RULE_PHASE84_RELABEL` in `diff_db.py`; companion tests pin CAN_ERASE stays OFF. DB regenerated; 673/673 host tests green. This mismatch is now RESOLVED in the DB.

**FM1608 VPP note:** infoic.xml records vpp_mv=12000 as an artifact of the minipro upstream data (the SRAM_STD protocol path does not apply VPP; FM1608 is a 5V FRAM). With the FRAM relabel, the VPP display is correctly hidden (gate = not-in-{SRAM,FRAM}). No VPP is applied to FM1608 on read or write — the `configure_sram` / `configure_fram` path is VPP-free by design.

**FM1608 blank-check note:** Phase 81 blank-check returned `Empty input` (firmware error) because `configure_sram` leaves `firestarter_operation_main = NULL` for `CMD_BLANK_CHECK`. This was a tooling gap, not a read fault. **Disposition (FIX-01 host half, Phase 84-02):** Host SRAM/FRAM blank-check short-circuit implemented — `check_eprom_blank()` detects `electrical-type in {"SRAM","FRAM"}` OR `protocol-id in {0x0E, 0x27, 0x28, 0x29}` and returns `False` before any firmware command, preventing the 0xA4 `MSG_ERR_EMPTY_INPUT`. 665 host tests green (2 new SRAM short-circuit tests). SHIPPED.

**AM27C020 VPP mismatch note:** Same class as ST M27C512 — plan text stated 12V, actual DB VPP is **13V**. Confirmed by EVIDENCE.json `decode_uv04`. Plan-text error, DB is correct.

**AM27C020 write ANOMALY:** Write deterministically fails (bad bytes 15/16, retries 20, 0 bits programmed) — the 0x08 Large EPROM write/VPP path does not program on this bench, while the 0x07 28-pin W27C512 wrote clean the same session. Plus an intermittent localized read glitch (12-byte region at 0x008004–0x00800F). Chip silicon is intact (0 bits changed, reads mostly clean). Disposition: RCA-and-defer **PENDING 84-05 bench** (Phase 84 FIX-01 re-bench with refflashed firmware).

---

### Chip 11: 0x0B (EPROM_LEGACY / UV-EPROM, NMOS)

| # | Chip | DB Algorithm (proto_id) | EVIDENCE Verdict | Pinout | VPP | Electrical Type | Algorithm (proto) | Size |
|---|------|------------------------|-----------------|--------|-----|-----------------|-------------------|------|
| 11 | 2516 | 0x0B (EPROM_LEGACY / UV-EPROM, NMOS) | ANOMALY (Phase 81 read) | Pending re-read — PENDING 84-05 | MISMATCH — see note | CONFIRMED — UV-EPROM | CONFIRMED — 0x0B | Pending confirmation — PENDING 84-05 |

**2516 source note:** This chip is a user-override DB entry (Phase 81 GRAD-01/02) — it is absent from minipro's `infoic.xml` (all 28 "2516" hits there are `25160` SPI serial parts). The DB entry records: algorithm 0x0B, pinout DIP24_2716, UV-EPROM, vpp_mv 25000, size_bytes 2048. The entry has been manually safety-reviewed.

**2516 read ANOMALY:** Phase 81 read was unstable — 3 distinct SHAs across N=3 on the initial read + 2 reseat cycles (D-07 exhausted). VPP pinned at 15.3V < 25.0V on the shared OE/VPP pin during read (the 0x0B Legacy path drives VPP=OE simultaneously). This is the same VPP-regulator instability family as chip-1's 18.8V boot refusal, but 0x0B-specific. All 0x07/0x08 UV chips read clean on the same bench.

**2516 VPP MISMATCH — observation:** The DB entry records vpp_mv=25000 (25V, NMOS class per v1.14 D-07 best-effort graduation). The bench VPP during the 0x0B read registered ~15.3V (shared OE/VPP dropped rail) — below the 25V programming spec and a plausible cause of the read instability. The VPP-skip firmware gate (FIX-01 firmware half, Phase 84-01) does not apply to 0x0B reads (0x0B is `configure_eprom_legacy` which has a different init path from the 0x07/0x08 `eprom_generic_init`). Exact VPP control behaviour for the 0x0B path under the reflashed b10+FIX-01 firmware requires re-bench to confirm.

**Disposition:** RCA-and-defer **PENDING 84-05 bench** (2516 re-read + VPP characterization after FIX-01 firmware reflash). GRAD-03 / SC#4 / FUT-03 all contingent on this re-bench producing a stable read oracle.

---

## Part 2 — Dispositions Summary

### (i) VPP-Skip Firmware Gate — SHIPPED (Phase 84-01, FIX-01 firmware half)

**Item:** Read and blank-check operations on 0x07/0x08 EPROM chips were calling `eprom_check_vpp()` in `eprom_generic_init()`, which drives the VPP regulator and checks for under/over-voltage. This caused:
- Chip-1 (W27C512) read refused at boot (VPP 18.8V > 12.0V threshold — transient regulator state); cleared by board reset
- Benign VPP-low warnings on ST M27C512 (11.9V < 13.0V) during reads (reads apply no VPP — these warnings are spurious)

**Fix:** Early-return guard in `eprom_generic_init()` for `CMD_READ` and `CMD_BLANK_CHECK` — skips `eprom_check_vpp()` entirely. Write, erase, and chip-ID still gate VPP (T-84-01 over-voltage block preserved). 5-assertion native dispatch test suite (2 positive + 3 negative). Commit `cb947c7` on `v1.15-bench-validation-of-operator-inventory` branch.

**Status:** SHIPPED — FIX-01 firmware half CLOSED.

---

### (ii) FM1608 Blank-Check Host Short-Circuit — SHIPPED (Phase 84-02, FIX-01 host half)

**Item:** `firestarter blank FM1608` (and any SRAM/FRAM chip) routed to the firmware `CMD_BLANK_CHECK` via `check_eprom_blank()`, but `configure_sram()` leaves `firestarter_operation_main = NULL` for that command, causing firmware to return `0xA4 MSG_ERR_EMPTY_INPUT`.

**Fix:** Host-side short-circuit in `check_eprom_blank()` (class constant `_SRAM_PROTO_IDS = frozenset({0x0E, 0x27, 0x28, 0x29})`). Detects SRAM/FRAM by electrical-type OR protocol-id before entering `_operation_context` — returns `False` without sending any firmware command. 2 new tests (`TestSramBlankCheckShortCircuit`); 665 host tests green. Commits `e5bfa3a` (RED) + `4c74b8d` (GREEN) in `firestarter_app` submodule.

**Status:** SHIPPED — FIX-01 host half CLOSED.

---

### (iii) SST39SF040 / FM1608 Relabel Outcome (Phase 84-03 — D-40 STOPped Part)

**FM1608 = fm-fram-full (SHIPPED):**

FM1608 `electrical.type` corrected from `SRAM` → `FRAM` via `build_db.py` per-chip override. Display-layer companion changes: `_ELECTRICAL_TYPE_LABEL["FRAM"] = "FRAM"` in `ic_layout.py`; VPP gate widened to `not in {"SRAM", "FRAM"}` in `ic_layout.py` + `eprom_info.py`. `RULE_PHASE84_RELABEL` added to `diff_db.py`. CAN_ERASE unaffected (FRAM not in `{"EEPROM", "Flash/EEPROM"}`). DB regenerated; 673/673 host tests green. FM1608 `list` snapshot updated (`SRAM` → `FRAM`). Commits `d8ca7a2` + `47c86c9` + `4d5b3de`.

**SST39SF040 = sst-keep (D-40 STOPPED — explicit observation):**

The D-40 STOP was triggered because relabeling SST39SF040 from `Flash/EEPROM` to `Flash` would drop `FLAG_CAN_ERASE` (the Phase-77/82-proven auto-erase path). Operator decision: KEEP.

> **SST39SF040 cosmetic-label observation (D-40):** The upstream minipro classification and algorithm family (0x06 / FLASH_AMD_ALT) suggest the chip is architecturally `Flash`. However, `electrical.type` is the SOLE input to `FLAG_CAN_ERASE` at `database.py:605`. SST39SF040 (proto 0x06, flash3) requires `Flash/EEPROM` to preserve `FLAG_CAN_ERASE = 0x02` on the wire, enabling the Phase-77/82-proven auto-erase path (REWR-03 silicon-confirmed). Relabeling to `Flash` would break erase — a regression D-40 forbids. The display label `Flash/EEPROM` is functionally correct for RURP's purposes even if cosmetically imprecise. To display `Flash` without breaking erase, a decoupled display/erase mechanism would be needed (`sst-decouple` path — not authorized this phase).

No code change shipped for SST39SF040. Zero regression. This observation is recorded for future reference.

---

### (iv) W27E512 + W27E040 Genuine Stuck-Bit ERASE FAILs — Silicon-Limited (D-32)

**W27E512 (0x07 EEPROM):** Phase 82 FAIL — erase cannot clear bit 7 at offset 0x3d (reads 0x7F, want 0xFF). Deterministic across N=3 reseats (D-08 exhausted). Identical offset and value every time = stuck cell, not contact or VPP. Chip read cleanly in Phase 81 (read-only) — defect manifests only on erase/write. DB decode was fully correct; the write path engaged at the correct parameters.

**W27E040 (0x08 EEPROM):** Phase 82 FAIL — erase cannot clear bit 4 at offset 0x7db (reads 0xEF, want 0xFF). Same stuck-bit-on-erase signature class as W27E512 (different offset and algorithm). N=2 reseats exhausted. DB decode correct.

**Disposition (D-32):** Both are genuine silicon wear events — NOT FIX-01 material, NOT DB/algorithm errors, NOT tooling bugs. The erase path is correct; the chips have worn past their erase endurance on these specific cells. REWR-01 is partially satisfied (W27C512 + SST27SF512 PASS; W27E512 FAIL); REWR-02 has no positive 0x08 write PASS (W27E040 sole 0x08 chip — deferred FUT-05, needs a functional 0x08 chip).

---

### (v) AM27C020 0x08 Write, W29C040 flash4 256B-page, 2516 0x0B Read — RCA-and-Defer PENDING 84-05

**AM27C020 (0x08 Large EPROM) — PENDING 84-05 bench:**

Phase 83 ANOMALY: `write` deterministically fails (bad bytes 15/16, retries 20, 0 bits programmed) at 0x000000. The 0x07 28-pin W27C512 wrote clean the same session — signature is 0x08/32-pin-path specific. Plus intermittent localized read glitch at 0x008004–0x00800F on 1 of 3 reads. Chip silicon is intact.

FIX-01 firmware half (Phase 84-01, VPP-skip) was shipped AFTER the Phase 83 bench session. The re-bench (Phase 84-05) will test the AM27C020 write on the reflashed b10+VPP-skip firmware to determine whether the VPP-skip on reads alters the write-path VPP state and whether that explains the anomaly.

> **PENDING 84-05:** AM27C020 write re-bench under reflashed firmware. If write still fails, dual-repo RCA (0x08 VPP path) follows.

**W29C040 (0x05 flash4, 512KB) — PENDING 84-05 bench:**

Phase 82 FAIL: write A times out verifying byte @0x0000FF (256B page-0 boundary), byte reads 0x00 — per-page auto-erase not confirmed. Deterministic across initial + 1 reseat. This is the first real-silicon test of the Phase-74 flash4 W29C040 SDP/256B-page fix (Phase-74 Wave-2 was deferred; the fix was native-test-verified only). Inverts the CR-01 expectation: W29C020 (256KB) passed clean; W29C040 (512KB) fails.

> **PENDING 84-05:** W29C040 write re-bench under reflashed firmware (same b10). If confirmed, likely dual-repo firmware fix (reopens Phase-74 Wave-2 under Phase 84 FIX-01). Deferred to operator bench session.

**2516 (0x0B EPROM_LEGACY, NMOS) — PENDING 84-05 bench:**

Phase 81 ANOMALY: 3 distinct SHAs across N=3 reads + 2 reseats. VPP pinned at 15.3V on the shared OE/VPP pin — below the 25V programming spec. VPP-skip firmware gate (FIX-01 fw half) does not apply to the 0x0B `configure_eprom_legacy` path; re-bench under the reflashed firmware is required to characterize whether the VPP-skip affects the 0x0B read VPP state.

> **PENDING 84-05:** 2516 re-read under reflashed firmware. If read stabilizes, write proof (GRAD-03 / FUT-03) follows. If read remains unstable, 0x0B VPP control RCA needed.

---

## Part 3 — EVIDENCE Cross-Reference Index

| Chip | EVIDENCE.md Section | EVIDENCE.json Cell | Phase | Key SHA |
|------|--------------------|--------------------|-------|---------|
| W27C512 | Phase 81 sweep row #1 + Phase 82 write row #1 | cells[0] (read) + cells[11] (write) | 81+82 | `9376dcd8…97ad23c8` (read) / `e16b2a5b…dc326ab5` (write B) |
| W27E512 | Phase 81 sweep row #2 + Phase 82 write row #2 | cells[1] (read) + cells[12] (write) | 81+82 | `71189f7f…48da9063` (read) / FAIL |
| SST27SF512 | Phase 81 sweep row #3 + Phase 82 write row #3 | cells[2] (read) + cells[13] (write) | 81+82 | `f633b2f5…f8056360` (read) / `e16b2a5b…dc326ab5` (write B) |
| W27E040 | Phase 81 sweep row #4 + Phase 82 write row #4 | cells[3] (read) + cells[14] (write) | 81+82 | `67f70ccd…468b4254` (read) / FAIL |
| SST39SF040 | Phase 81 sweep row #5 + Phase 82 write row #5 | cells[4] (read) + cells[15] (write) | 81+82 | `c19c3e07…a348368d` (read) / `a38b13b4…d970b96b` (write B) |
| W29C020 | Phase 81 sweep row #6 + Phase 82 write row #8 | cells[5] (read) + cells[19] (write) | 81+82 | `93ff5287…66b53602` (read) / `47304933…c11ce58c` (write B) |
| W29C040 | Phase 81 sweep row #7 + Phase 82 write row #7 | cells[6] (read) + cells[18] (write) | 81+82 | `d44736a9…1e3b48b3` (read) / FAIL |
| FM1608 | Phase 81 sweep row #8 + Phase 82 write row #6 | cells[7] (read) + cells[17] (write) | 81+82 | `2ef1444b…3d4c0037` (read) / `3c23e7fc…34f75c90` (write B) |
| ST M27C512 | Phase 81 sweep row #9 + Phase 83 write row #1 | cells[8] (read) + cells[20] (write) | 81+83 | `71189f7f…48da9063` (read) / `008948af…ec397c3f` (write) |
| AM27C020 | Phase 81 sweep row #10 + Phase 83 write row #2 | cells[9] (read) + cells[21] (write) | 81+83 | `08b687a3…177ed496` (read) / ANOMALY |
| 2516 | Phase 81 sweep row #11 | cells[10] (read) | 81 | ANOMALY (3 distinct SHAs, no stable value) |

---

## Part 4 — Bench-Pending Items (Placeholder for 84-06 Fill-In)

The following items are **deferred to Plan 84-05 bench session** and will be filled in by **Plan 84-06** once the bench results are recorded:

| # | Item | Pending | 84-06 will record |
|---|------|---------|-------------------|
| P1 | 2516 re-read (Phase 84-05) | PENDING 84-05 | Stable SHA or continued ANOMALY + VPP characterization under FIX-01 fw |
| P2 | 2516 write proof GRAD-03 (contingent on P1 stabilizing) | PENDING 84-05 | PASS/FAIL + SHA + VPE under-voltage note; or DEFERRED if read still unstable |
| P3 | AM27C020 re-bench write (Phase 84-05) | PENDING 84-05 | PASS/FAIL + 0x08 path VPP characterization under FIX-01 fw |
| P4 | W29C040 re-bench write (Phase 84-05) | PENDING 84-05 | PASS/FAIL + flash4 page-boundary characterization; if FAIL → firmware RCA |
| P5 | FIX-01 overall disposition | PENDING 84-05 outcome | "FIXED" or "DEFERRED with rationale" for each of the 3 FIX-01 inputs |

---

*Authored: 2026-06-25 as Plan 84-04, Wave-2 consolidation artifact.*
*Sources: EVIDENCE.md + EVIDENCE.json (Plans 81-03, 82-02/03, 83-02/03) + 84-01/02/03 SUMMARY files.*
*Next update: Plan 84-06 (after 84-05 bench session fills the PENDING items above).*

# v1.15 Bench Evidence — Phase 81 Non-Destructive Read Sweep

**Harness version:** 81 · **Board:** leonardo · **Shield:** Rev 2.0 · **Generated:** 2026-06-23/24

## SAFE-01 Preconditions (verified per task)

- **Board:** leonardo (the only authoritative read board) · **Port:** /dev/ttyACM0 · **Firmware:** 3.0.0b8
- **Shield:** Rev 2.0 — operator-confirmed silkscreen (EEPROM hw byte reports "Rev 2.0-class", cannot distinguish revs)
- **Calibration:** R1=270000, R2=44000 (not the 1000 default)
- **Host suite:** green (Plan 81-01, 651 tests)
- **Negative control (EVID-03):** FIRED — wrong-file `verify` exited RC=1 on W27C512 (Task 1) and ST M27C512 (Task 2)
- **Non-destructive:** reads apply NO VPP — **zero chips consumed**

### Phase 82 SAFE-02 Gate (recorded Plan 82-01, 2026-06-24)

- **`ruff check` (files added by 82-01):** PASS — `tools/gen_test_image.py`, `tests/test_gen_test_image.py` ruff-clean (pre-existing I001 errors in unrelated tools unchanged)
- **`ruff format --check` (files added by 82-01):** PASS — both new files already formatted
- **Full host suite:** PASS — **663 tests** (651 + 12 new gen_test_image pinning tests), 29 snapshots
- **0xA4 guard `test_init_phase_data_frames_not_acked`:** PASS (1/1 — SAFE-02 ack_data=False guard green)
- **Python:** 3.12.13 (devcontainer); CI targets py3.9/3.11 — new files use no 3.9-incompatible syntax

### Phase 82 SAFE-01 Gate — Plan 82-02 write session (operator sign-off 2026-06-24)

- **`controller:`** leonardo on **/dev/ttyACM0** (firmware `firestarter fw`), firmware 3.0.0b8
- **Shield:** Rev 2.0 — **operator-confirmed silkscreen** this session ("Rev 2.0 — start now"); fw byte reports "Rev 2.0-class" (cannot distinguish revs, per policy)
- **Calibration (live readback):** R1=270000, R2=44000 (NOT the 1000 default → VPP read trustworthy)
- **SAFE-02:** green (Plan 82-01 — 663 tests + 0xA4 guard `test_init_phase_data_frames_not_acked` PASS)
- **Authorization:** destructive A→B write session cleared; chips seated one at a time on Leonardo + Rev 2.0

### Phase 83 SAFE-02 Gate (recorded Plan 83-01, 2026-06-24)

- **0xA4 guard `test_init_phase_data_frames_not_acked`:** PASS (1/1 — SAFE-02 `ack_data=False` guard green)
- **Full host suite:** PASS — **663 tests** (unchanged from Phase 82; no source/test files modified this plan), 29 snapshots
- **`ruff check firestarter/ tests/` (CI-authoritative scope):** PASS — `All checks passed!` (RC=0)
- **`ruff format --check firestarter/ tests/` (CI-authoritative scope):** PASS — 73 files already formatted (RC=0)
- **Broad `ruff check .` / `ruff format --check .`:** reports 4 pre-existing `tools/`-tree findings (`tools/audit_coverage_matrix.py`, `tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py` I001/UP031; `+ .github/scripts/update_version.py`, `tools/check_mypy_watermark.py` format) — **FLAGGED as out-of-CI-scope, NOT masked**: `ci.yml` gates ruff over `firestarter/ tests/` only (`.github/workflows/ci.yml:60,63`), which is green. These are NOT introduced by this plan (zero source changes) and match the Phase 82 "pre-existing I001 errors in unrelated tools unchanged" note. Not a py3.12-vs-CI version discrepancy — purely a path-scope difference between `ruff check .` and the CI gate.
- **Python:** 3.12.13 (devcontainer); CI targets py3.9/3.11 — no source touched, so no new version-sensitive surface introduced
- **Verdict:** SAFE-02 GREEN — bench session (Plans 02/03) may open on the CI-authoritative gate.

### Phase 82 SAFE-01 Gate — Plan 82-03 flash4 write session (operator sign-off 2026-06-24)

- **`controller:`** leonardo on **/dev/ttyACM0** (re-verified `firestarter fw` for this session — no USB replug since 82-02), firmware 3.0.0b8
- **Shield:** Rev 2.0 — **operator-re-confirmed silkscreen** this flash4 session
- **Calibration (live readback):** R1=270000, R2=44000 (not the 1000 default)
- **SAFE-02:** green (Plan 82-01 — unchanged since 82-02)
- **DB-01 decode (firestarter info):** W29C040 = 32-pin / 0x80000 (524288) / Flash/EEPROM / 12V / 0x05; W29C020 = 32-pin / 0x40000 (262144) / Flash/EEPROM / 12V / 0x05

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

---

## Phase 82 — Rewritable A→B Write Validation

**Protocol (D-05/D-06):** For each of the 8 electrically-rewritable chips, write image A (seed=1,
full-size deterministic pseudo-random), verify A; then write image B (seed=2, same size) **without
an explicit erase step**, verify B. A clean B SHA-256 match proves auto-erase fired. Images generated
by `tools/gen_test_image.py`; stored at `/tmp/firestarter_bench_p82/<chip>_img_{A,B}.bin`.

**Known risk:** W29C020 (256KB flash4) carries **cr01_risk=yes** — `flash4_page_size(262144)` guesses
128B but the real datasheet page is 256B. A mid-page-poll write failure is pre-attributed to CR-01
and handed to Phase 84 FIX-01; it is NOT a surprise failure if it occurs.

**Verdict key:** `PASS` / `FAIL (CR-01)` / `FAIL (genuine)` / `ANOMALY`

| # | Chip | Family / Algorithm | Board+Shield | Op | Blank-state | SHA-256 (image B read-back) | Verdict | seed_A | sha256_image_A | seed_B | sha256_image_B | cr01_risk | Anomalies |
|---|------|--------------------|--------------|-------|-------------|------------------------------|---------|--------|----------------|--------|----------------|-----------|-----------|
| 1 | W27C512 | 0x07 (EPROM_STD / EEPROM) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `e16b2a5b…dc326ab5` | **PASS** | 1 | `604d9570…1645d637` | 2 | `e16b2a5b…dc326ab5` | none | Auto-erase proven (clean B over A, no explicit erase); consistency-check N=3 1-distinct-SHA; neg-control verify(A) RC=1. Initial attempt hit VPP-high 13.1V>12.0V (Phase-81 VPP-regulator family) — operator corrected VPP, clean retry. DB-01: DIP28_27512/EEPROM/12V/65536 confirmed vs silicon. |
| 2 | W27E512 | 0x07 (EPROM_STD / EEPROM) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `—…—` | **FAIL (genuine)** | 1 | `604d9570…1645d637` | 2 | `e16b2a5b…dc326ab5` | none | FAIL (genuine): erase cannot clear bit 7 @0x3d (reads 0x7f, want 0xFF) — DETERMINISTIC across initial run + 2 reseats (D-08 N=2 exhausted), identical offset/value every time = stuck cell, not contact/VPP. First session: write-cycle A RC=0 then write-cycle B erase failed + read jittered 14/65536 bytes (0xEF↔0xFF); both retries failed at erase-A. Chip read clean in Phase 81 (read-only) — defect manifests only on erase/write. DB-01 DIP28_27512/EEPROM/12V/65536 confirmed (write path engaged correctly; genuine silicon wear, not DB/algo mismatch). neg-control verify(A) RC=1. REWR-01 partial. |
| 3 | SST27SF512 | 0x07 (EPROM_STD / EEPROM) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `e16b2a5b…dc326ab5` | **PASS** | 1 | `604d9570…1645d637` | 2 | `e16b2a5b…dc326ab5` | none | Auto-erase proven (clean B over A, no explicit erase); consistency-check N=3 1-distinct-SHA == image B; neg-control verify(A) RC=1. No VPP hiccup. DB-01: DIP28_27512/EEPROM/12V/65536 confirmed vs silicon. |
| 4 | W27E040 | 0x08 (EPROM_QUICK / EEPROM) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `—…—` | **FAIL (genuine)** | 1 | `77a771b2…f1662bbd` | 2 | `a38b13b4…d970b96b` | none | FAIL (genuine): erase cannot clear bit 4 @0x7db (reads 0xef, want 0xFF) — DETERMINISTIC across initial run + 1 reseat (same offset/value), genuine stuck cell. Same stuck-bit-on-erase signature class as W27E512 (different offset). Chip read clean in Phase 81 (read-only); defect manifests only on erase/write. DB-01 DIP32_STD/EEPROM/12V/524288 confirmed (write path engaged at correct params; genuine silicon wear, not DB/algo). REWR-02 partial. |
| 5 | SST39SF040 | 0x06 (FLASH_AMD_ALT / Flash) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `a38b13b4…d970b96b` | **PASS** | 1 | `77a771b2…f1662bbd` | 2 | `a38b13b4…d970b96b` | none | Auto-erase proven (clean B over A, no explicit erase); flash3 slow path ~240s/write; consistency-check N=3 1-distinct-SHA == image B; neg-control verify(A) RC=1. DB-01: pinout DIP32_SST39SF040 / 12V / 524288 confirmed vs silicon. DB-01 NOTE for Phase 84: DB electrical.type reads 'Flash/EEPROM' while milestone classes this as 0x06 flash3/Flash — observation, not a blocker; no inline DB edit. |
| 6 | FM1608 | 0x40 (SRAM_STD / FRAM) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `3c23e7fc…34f75c90` | **PASS** | 1 | `a89c4b45…8ce5415d` | 2 | `3c23e7fc…34f75c90` | none | Overwrite proof, no erase (D-06): clean B read-back SHA == image B confirms B fully replaced A. Used DIRECT write path (write -b) — 'dev write-cycle' unusable on FRAM (erase 'Not supported'; same Phase-81 erase/blank-check tooling gap, flag Phase 84 FIX-01, NOT fixed here). write A/verify A RC=0, write B/verify B RC=0, consistency-check N=3 1-distinct-SHA == image B, neg-control verify(A) RC=1. DB-01: pinout DIP28_JEDEC_SRAM_8K / 8192 confirmed vs silicon; NOTE for Phase 84 — DB electrical.type 'SRAM' vs FRAM family (observation, no inline DB edit). |
| 7 | W29C040 | 0x05 (FLASH_AMD_STD / Flash/EEPROM) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `—…—` | **FAIL (genuine)** | 1 | `77a771b2…f1662bbd` | 2 | `a38b13b4…d970b96b` | none | FAIL (genuine, flash4 page-write): write A (-b) times out verifying byte @0x0000ff (256B page-0 boundary), reads 0x00 (page not auto-erased/programmed) — DETERMINISTIC across initial + 1 reseat (same offset/byte). Per-page auto-erase NOT confirmed → REWR-04 SC#3 NOT met on silicon. FW FLASHED b8→b10 THIS SESSION (operator-authorized deviation) to get the Phase-74 W29C040 SDP/256B-page fix; standalone erase is a 0.06s no-op on both b8 and b10 (chip stays 0x00). KEY: this is the FIRST real-silicon test of the Phase-74 fix — Phase-74 Wave-2 (W29C040 re-bench) was DEFERRED, so the fix was only native-test-verified. Reopens Phase-74 Wave-2 / hands to Phase 84 FIX-01. Distinct from the W29C020 CR-01 128-vs-256 under-sizing. DB-01: DIP32/Flash-EEPROM/12V/524288 decode confirmed vs silicon (info read clean; failure is write-path, not decode). |
| 8 | W29C020 | 0x05 (FLASH_AMD_STD / Flash/EEPROM) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `47304933…c11ce58c` | **PASS** | 1 | `b2fc5cbf…0a133457` | 2 | `47304933…c11ce58c` | no (CR-01 did NOT manifest) | PASS — A→B auto-erase proven for the Flash/EEPROM type (write B over A, no explicit erase, clean B verify): THIS is the REWR-04 SC#3 silicon confirmation of the FLAG_CAN_ERASE Flash/EEPROM branch (landed on W29C020, not W29C040). Direct write -b path (write-cycle blank-checks; flash4 has no real bulk-erase — per-page auto-erase on write). write A/verify A RC=0, write B/verify B RC=0, consistency-check N=3 1-distinct-SHA == image B, neg-control verify(A) RC=1. CR-01 (flash4_page_size 128-vs-256 under-sizing) did NOT manifest on b10 — 256B page handling was correct here. FW b10 (flashed this session). DB-01: DIP32/Flash-EEPROM/12V/262144 decode confirmed vs silicon. NB: contrast W29C040 (512KB) FAIL — reopen Phase-74 Wave-2 in Phase 84. |

---

## Phase 83 — UV-EPROM Write Proof (gated on Phase 81 blank-state)

**Scope (D-01/D-02):** This phase covers **ONLY the 2 read-stable UV-EPROM chips** —
**ST M27C512** (0x07, BLANK) and **AM27C020** (0x08, NOT-BLANK). Board = **Leonardo + RURP
Rev 2.0 ONLY** (SAFE-01/D-09). Every UV write is **irreversible** (operator has no eraser) →
non-destructive-first (UV-01): the Phase 81 blank-state is re-confirmed and the operator
authorizes the spend **at the bench** before any VPP is applied (D-04). Default lean = **SPEND**
the 2 commodity parts (D-03), but the explicit per-chip spend-vs-preserve call stays a live
bench decision.

**2516 → Phase 84 deferral (D-01 — IMPORTANT, narrows the roadmap scope):** the entire **2516**
is **OUT of Phase 83** — **no write, no preserve-dump, no re-read** in this phase. Its read was
ANOMALOUS in Phase 81 (3 distinct SHAs / N=3 + 2 reseats, VPP pinned 15.3V<25V on the shared
OE/VPP pin, 0x0B-specific). Writing/dumping the **irreplaceable** 2516 on an untrusted read path
would consume it for a **vacuous** PASS (EVID-03). Therefore **GRAD-03** (2516 VPE-rail write
proof), **SC#4** (2516 bench-proven), and the **FUT-03** close all move to **Phase 84**,
contingent on **Phase 84 FIX-01** root-causing and fixing the 0x0B read-path VPP instability so
the read oracle becomes trustworthy.

**Pre-recorded Phase 84 PASS bar for the 2516 (D-08 — inherited without re-discussion):** when
the 2516 write proof runs in Phase 84 (after FIX-01 stabilizes its read), the PASS bar is a clean
**read-back SHA match** on the spent image (after a stabilized N≥3 read); the firmware
**under-voltage warning** (~22.4V VPE < 25V NMOS spec) is captured **verbatim** and the result
recorded **best-effort** (per v1.14 D-07). **Over-voltage stays blocked throughout** (SC#5).
Achieving this closes FUT-03 (best-effort).

**Write-proof method per blank-state (UV-03):**
- **ST M27C512 (BLANK) → full known image (D-05):** spend = write a full-chip 64KB deterministic
  pseudo-random image, verify read-back **SHA == image SHA**. Strongest proof (every address line
  + bit pattern exercised). Image via `tools/gen_test_image.py` (size_bytes=65536, seed=1).
- **AM27C020 (NOT-BLANK) → all-`0x00` full wipe (D-06):** spend = write all-`0x00` over the entire
  `0x40000` (262144 B) chip (proves every currently-`1` bit can be driven `1→0` — the only legal
  transition on a UV part without erase), verify read-back **SHA == SHA(all-`0x00`)**.

**Verify oracle (D-07/D-13, non-vacuous EVID-03):** read-back SHA match on the trusted Leonardo
read, N≥3 byte-identical, plus a negative control (a wrong-file `verify` exits non-zero). Both
chips read stably in Phase 81 → their write proofs CAN be SHA-verified.

**Write-failure disposition (D-14):** reseat + retry up to N=2, then record FAIL (genuine defect)
or ANOMALY and CONTINUE; genuine defects flagged for Phase 84 FIX-01, not root-caused inline. A
UV part once spent cannot be re-blanked — a "retry" re-writes the same all-`0x00`/image
(idempotent for these proofs).

**Image SHA oracles (recorded Plan 83-01, 2026-06-24; reuse-first, EVID-02 — no new module/dep):**

| Chip | Image file (`/tmp/firestarter_bench_p83/`) | Size (bytes) | Generator | SHA-256 oracle |
|------|--------------------------------------------|--------------|-----------|----------------|
| ST M27C512 | `ST_M27C512_img.bin` | 65536 (0x10000) | `tools/gen_test_image.py 65536 1` (seed=1, deterministic — reproducible) | `604d957094f7cb1f98f50d7408f64e7720e5ae5d4acab8d1047a9a081645d637` |
| AM27C020 | `AM27C020_zeros.bin` | 262144 (0x40000) | direct byte-write of 262144 × `0x00` (NOT gen_test_image; D-06) | `8a39d2abd3999ab73c34db2476849cddf303ce389b35826850f9a700589b4a90` |

> The AM27C020 oracle equals `sha256(b"\x00" * 262144)` (verified independently). The ST M27C512
> oracle is reproducible: re-running `python tools/gen_test_image.py 65536 1 <path>` prints the
> identical digest. (NB: it also matches the Phase 82 seed=1/65536 "image A" SHA `604d9570…1645d637`
> — same generator, size, and seed.)

**Write-proof results (filled at the bench in Plans 02/03 — empty until the spend session opens):**

| # | Chip | Family / Algorithm | Board+Shield | Blank-state | Spend-vs-preserve decision | Op | Image SHA | Read-back SHA | Read N | Verdict | Anomalies |
|---|------|--------------------|--------------|-------------|----------------------------|----|-----------|---------------|--------|---------|-----------|
| 1 | ST M27C512 | 0x07 (EPROM_STD / UV-EPROM) | leonardo Rev 2.0 | BLANK (Phase 81) | _(operator, live — D-03 lean: SPEND)_ | write full image → verify | `604d9570…1645d637` | _(pending)_ | _(pending)_ | _(pending)_ | _(pending)_ |
| 2 | AM27C020 | 0x08 (EPROM_QUICK / UV-EPROM) | leonardo Rev 2.0 | NOT-BLANK (Phase 81) | _(operator, live — D-03 lean: SPEND)_ | write all-`0x00` → verify | `8a39d2ab…589b4a90` | _(pending)_ | _(pending)_ | _(pending)_ | _(pending)_ |
| — | 2516 | 0x0B (EPROM_LEGACY / UV-EPROM, NMOS) | — | NOT-BLANK, READ-UNSTABLE | **DEFERRED → Phase 84** (D-01) | — no write / no preserve-dump / no re-read in Phase 83 — | — | — | — | **DEFERRED** | GRAD-03 / SC#4 / FUT-03 move to Phase 84 (after FIX-01 stabilizes the 0x0B read); D-08 PASS bar pre-recorded above |


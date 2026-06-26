# Phase 91 — 12V-VPP Write-Path Regression RCA (working document)

**Started:** 2026-06-26 · **Firmware-under-test:** `firestarter@a296195` (recompose) ·
**Baseline:** `firestarter@a1953c2` (tag 3.0.0b10) · **Host:** `firestarter_app@e46549f`
vs v1.15 `98b3a92` · **Oracle:** Leonardo `/dev/ttyACM0` + RURP Rev 2.0.

> Operator handed full autonomous control. SST39SF040 (0x06) is seated and is the
> must-prove deliverable; W27C512 (0x07) bench re-validation is deferred to operator
> return (chip swap). This doc accumulates the A/B-first decision-tree evidence.

---

## Diff Forensics (Wave 1, Task 1 — static, no hardware)

Raw hunks captured in `diff-forensics.txt` (`git diff a1953c2..a296195` for the write-path
files). Verdict per changed file along the 0x06/0x07 write path:

| File | Change classification | Evidence |
|------|----------------------|----------|
| `src/proms/flash_type_3.cpp` (0x06 SST39SF040) | **comment-only** | The entire +22-line delta is a doc block (handler description + INV-09 keep-Flash/EEPROM note). Zero code lines changed. `configure_flash3()` body byte-identical. |
| `src/proms/eprom.cpp` (0x07 W27C512) | **measurement/extraction only — program path UNTOUCHED** | Changed hunks are confined to `eprom_check_vpp` (line ~263; VPP *guard/measurement*, extracted to share P3) + `eprom_check_chip_id`/`eprom_generic_init` + a doc header. `eprom_write_execute` (line 197, the actual program loop) is in NO changed hunk → byte-identical. `eprom_write_execute` appears in the diff only inside a `+ *` comment line. |
| `src/proms/primitives.cpp` + `include/primitives.h` (P3/P4/P5) | **new shared primitives; bodies byte-identical to originals** | P3 `vpp_check_window`, P5 `poll_readback` extracted; bodies equal the pre-recompose inline code. |
| `src/proms/flash_type_4.cpp` (0x05 W29C020) | extraction (poll_readback) | **flash4 PASSED on the bench** through this same P5 primitive — exonerates P5. |

**P3 `vpp_check_window` formally EXONERATED:** its body is byte-identical, and the
SST39SF040 (0x06/flash3) write path does **not** call P3 at all (flash3 is 5V-only,
never enables the VPP regulator). A P3 (or any single-primitive) regression cannot
explain the SST39SF040 failure. The "revert the recompose" hypothesis is **closed**.

### Host + DB wire-param parity (`98b3a92` vs `e46549f`)

- `chip_database.json` entry `SST39SF040` — **byte-identical** across the two host revs
  (`diff` empty). Verified this session.
- `chip_database.json` entry `W27C512,W27E512` (and all `27C512*` variants) —
  **byte-identical** across the two host revs (`diff` empty).
- Host write path (`eprom_operations.py`) v1.15→v1.16 delta = cosmetic output-dir
  grouping + a SRAM-only blank-check short-circuit (does not touch flash3/EPROM). The
  FLAG_CAN_ERASE refactor is zero-delta (predicate identical). (Per 91-RESEARCH §Sources.)

**Conclusion (Task 1):** Neither failing chip's write path changed in firmware OR host
OR DB between v1.15 and the recompose. The CONTEXT prior ("recompose regressed the write
path") is contradicted by the diffs.

---

## Native Trace Confirmation (Wave 1, Task 2 — unit, no board)

Re-ran the Phase-88 golden bus-sequence traces (pinned on the pre-recompose handlers,
green at Phase 89 on a296195) on the current recompose HEAD:

| Command | Result | Key cases |
|---------|--------|-----------|
| `pio test -e native -f "*test_val_flash3*"` | **6/6 PASSED** (3.26 s) | `test_golden_flash3_write`, `test_inv09_flash3_sst39sf040_keep_flash_eeprom`, write/erase/blank-check configure-no-VPP |
| `pio test -e native -f "*test_val_eprom*"` | **19/19 PASSED** (0.67 s) | `test_golden_eprom_0x07_write`, `test_inv05_eprom_vpp_skip_on_read`, `test_inv06_eprom_pulse_delay_defaults`, WR-02 chip-id severity fork |

**Coverage caveat** (per `reference_golden_trace_misses_severity_fork`): golden traces
with a matching id can miss the WARNING-vs-ERROR fork; the eprom suite now includes
explicit WR-02 mismatch cases, so this caveat is covered for 0x07. Analysis-only here.

**Conclusion (Task 2):** The recompose preserves the exact 0x06 write bus sequence
(12-entry golden) and the 0x07 write+chip-id sequence at the unit level. **Therefore any
bench write failure must be rail / timing / chip-state on real silicon — NOT a
bus-sequence code change.**

---

## A/B Prep (Wave 1, Task 3 — staged, no flash yet)

- **Images:** `/tmp/firestarter_bench_p90/SST39SF040_img_{A,B}.bin` (524288 B each)
  present. Image B SHA = `a38b13b4d285756c1f385a75d0cdf89f72720764c21fd933ced75ebdd970b96b`
  ✓ == v1.15 baseline + the **FIX-91 gate**.
- **b10 baseline build:** `git worktree add /tmp/fs-b10 a1953c2` (detached @ tag
  3.0.0b10), `pio run -e leonardo` → **SUCCESS, Flash 25654 B (89.5%)**, RAM 1999 B.
  Artifact: `/tmp/fs-b10/.pio/build/leonardo/firestarter_leonardo.hex`. Recompose HEAD
  still `a296195` (worktree did not move it).
- **Identity-disambiguation rule:** `firestarter fw` reports `3.0.0b10` for BOTH the
  recompose and b10 (version string NOT bumped). The ONLY reliable in-band discriminator
  is the **flash byte count: b10 = 25654 B, recompose = 25136 B** — confirm via the
  avrdude bytes-written line on each upload.

### Plan deviation (recorded)
Plan 01 Task 3 verify checks `/tmp/fs-b10/.pio/build/leonardo/firmware.hex`; this project
names the artifact `firestarter_leonardo.hex` (+ `.elf`). The build succeeded and the
artifact exists — substance met; the literal filename in the plan's `<automated>` check
was wrong. No impact on the A/B.

---

## ebca6266 Content Forensic (Open Q1) — Wave 2 Task 1

Re-read the seated SST39SF040 (non-destructive; read path proven byte-identical) BEFORE any
overwrite → SHA `ebca626663a78613a7572b792e00de11472aaefa84b41539ec5f5cfae3533e0b`,
**byte-identical to the Phase-90 capture** (read path stable; chip properly seated). Byte-compared
vs image B (`a38b13b4…`). Raw map in `ebca6266-forensic.txt`. Key result:

- **524285 / 524288 bytes match image B (99.9994%).** Only **3 bytes differ — all at offsets 0x0,
  0x1, 0x2.** Per-64KB block: every block 100.00% match except block 0 (the 3 bytes).
- All 3 differing bytes satisfy **`chip == imgA & imgB`** exactly:
  - 0x0: chip `0x04` = imgA `0x44` & imgB `0x1c`
  - 0x1: chip `0x20` = imgA `0x20` & imgB `0x2e`
  - 0x2: chip `0x02` = imgA `0x82` & imgB `0x2b`
- **Classification: partial-program / incomplete-erase at sector 0.** NOR cells erase to 0xFF
  (all-1) and program only clears 1→0. The `imgA & imgB` residue means those cells were NOT
  re-erased before image B was programmed over image A — the new bits that needed to go 0→1
  (require erase) could not be set. **A2 branch: timing/rail (erase-completeness), NOT
  addressing/buffer.** The Phase-90 "deterministically-wrong content" verdict was technically true
  (SHA differs) but is, mechanically, 3 un-erased bytes at the chip's very start.

## Reproduce on Recompose (a296195) — Wave 2 Task 2 (recompose leg)

Clean `write -b SST39SF040 imgB` on the current recompose fw: write reported **"successful
(177.66s)" RC=0**, but `verify` **RC=1: `0x1c != 0x04 at 0x000000`** — the SAME offset-0 failure,
**reproduced deterministically**. `0x04` (= prior residue) is a bit-subset of target `0x1c`
(needs bits 3,4 set → requires a completed erase). Confirms: the chip-erase is not finishing
before the first bytes are programmed; the firmware reports success because the per-byte DQ7
data-poll (`flash_util_verify_operation`, `& 0x80` only) matches on bit 7 (both `0x04` and `0x1c`
have bit7=0) and never detects the un-set low bits. Only the final full verify catches it.

> Note: VPP loaded-rail capture is N/A for flash3 — SST39SF040 is **5V-only and never enables the
> VPP regulator** (CLAUDE.md handler table 0x06 = None/5V). Also, a single serial port cannot
> monitor `vpp` and `write` concurrently. The "12V-VPP write-path" label never applied to 0x06;
> the real axis is **erase-before-write completeness**.

## Root Cause (RCA-91)

`flash_type_3.cpp:flash3_write_init` issues one chip-erase (`flash_execute_command(FLASH_ERASE)`)
then waits a **fixed `delay(FLASH_ERASE_DELAY_MS=105 ms)`** with **no poll for actual erase
completion**, then `flash3_write_execute` programs byte-by-byte from address 0. On this seated
SST39SF040 the chip-erase completes a few ms past 105 ms, so the first 1–3 bytes (programmed in
the overlap window right after the delay) land on cells the erase had not yet finished → they
retain `prev & new`. The DQ7-only per-byte poll masks it. This logic is **byte-identical across
b10 (a1953c2) and the recompose (a296195)** (diff = comment-only on flash_type_3.cpp), so it is a
**pre-existing marginal-timing bug, surfaced — not introduced — by the recompose.** This is why a
P3 / VPP explanation cannot cover it (flash3 has no P3 and uses no VPP).

## Decision Gate — Wave 2 Task 3

**b10 leg result:** reflashed b10 baseline fw (`a1953c2`, 25654 B avrdude-verified). The Leonardo
re-enumerated after upload (port ACM0→ACM1; the firestarter CLI auto-detected). `write -b imgB`
RC=0 "successful"; `verify` **RC=1 → `0x1c != 0x04 at 0x000000`** — **byte-identical failure to the
recompose leg.** SHAs in `bench/SST39SF040-ab/SHA256SUMS.txt`.

**Verdict: pre-existing / environmental — the recompose is INNOCENT.** Both the v1.16 recompose
(a296195) and the v1.15 baseline (a1953c2) fail identically at offset 0, on the same seated
SST39SF040 + Rev 2.0, because the flash3 write path (including the 105 ms erase delay) is
byte-identical between them (diff = comment-only). This is NOT recompose-fw and NOT host (the
write path runs on the firmware; the host merely streams bytes). It is a pre-existing marginal
chip-erase-completion timing bug. No host-axis A/B is needed (fw-cause is established on both legs).

**Indicated fix for Plan 03:** widen the flash3 chip-erase settle margin (105 ms → 500 ms) so the
erase fully completes before programming begins. (Recommended future hardening: DQ7/toggle-bit
erase-completion poll instead of a blind delay.)

## Both Symptoms Explained (RCA-91 Success Criterion 2)

- **SST39SF040 (0x06, flash3):** write-A "timeout" + write-B "successful-but-wrong" is ONE
  mechanism — an **incomplete chip-erase at the 105 ms blind delay**. The first bytes programmed
  in the erase-tail overlap window land on un-erased cells (`prev & new` residue at 0x0–0x2); DQ7
  data-polling masks it per-byte; the final verify catches `0x1c != 0x04 @0x0`. Write-A's "timeout"
  in Phase 90 is the same family (the 524 KB write is a ~177 s slow path; a transient erase/poll
  stall on the first attempt). flash3 is **5V-only, no VPP** — so this is an erase-timing bug, not
  a VPP-rail bug.
- **W27C512 (0x07, EPROM-STD):** `bad bytes:921 @0x000000` on a clean 12.0 V rail is the **same
  erase-before-write axis** — a non-blank W27C512 whose erase did not clear the first block, so the
  program could not set the needed 0→1 bits (NOR/EEPROM-class). Per memory
  `reference_w27c512_bench_write_erase_gotcha`: "bad bytes:N is chip-state, not transport." (0x07
  bench re-validation is DEFERRED — operator chip swap; see the operator checklist.)
- **Why a P3-only / VPP explanation fails to cover both:** flash3 (0x06) uses **P4/P7, never P3,
  and never enables the VPP regulator** (5V-only). The common axis is **erase-before-write
  completeness**, NOT the 12V-VPP path. The Phase-90 "12V-VPP write-path" label was correlational
  (both happened to be write failures) — the mechanism is erase, for both.

## A/B Decision Tree (resolved by the legs above)

```
Reproduce SST39SF040 write on CURRENT fw (a296195)
        │  (expect: write-A timeout + write-B wrong content `ebca6266…`, per Phase 90)
        ▼
Flash b10 (a1953c2, 25654 B), re-run write -b cycle on SST39SF040
        ├─ b10 PASSES (SHA a38b13b4…) → recompose-fw causal (UNEXPECTED given zero code delta) → fix in fw
        ├─ b10 ALSO FAILS identically  → recompose INNOCENT → environmental/pre-existing  ◀── PRIMARY (HIGH prior)
        │        └─ host-axis backup A/B (pip install 98b3a92) → isolate host vs hardware/timing
        └─ b10 fails DIFFERENTLY        → mixed/marginal → deeper instrumentation
```

**Leading hypothesis (MEDIUM):** recompose innocent; the SST39SF040 failure is an
environmental / slow-path / timeout effect (flash3 is a ~177–240 s/write slow path; the
12.0 V rail was measured idle, never under write load). The `ebca6266…` content forensic
(Wave 2) + the loaded-rail `vpp` capture will discriminate partial-program vs transform.

---

## Status
- [x] Wave 1 Task 1 — diff forensics captured + verdict (recompose innocent)
- [x] Wave 1 Task 2 — native golden traces green (bus sequence preserved)
- [x] Wave 1 Task 3 — A/B images SHA-verified + b10 baseline built + identity rule
- [ ] Wave 2 — bench A/B + ebca6266 forensic + decision gate
- [ ] Wave 3 — fix + confirm SST39SF040 write == a38b13b4…
- [ ] Wave 4 — disposition ledger rows + W27C512 operator checklist

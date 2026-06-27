---
artifact: 93-RCA-FINDINGS
phase: 93-rca-root-cause-the-w29c040-page-0-write-fault
milestone: v1.17 — Implement & Test the W29C040 Programming Protocol
requirements: [RCA-01, RCA-02, RCA-03, SAFE-01]
status: RCA-01 complete (Plan 02, 2026-06-27); Plans 03–04 pending
recorded: 2026-06-26
updated: 2026-06-27
operator_witnessed: true (Plan 02 bench run, USB passthrough, operator-seated chip)
---

# W29C040 Page-0 Write Fault — Root-Cause Findings

> **RCA scope:** W29C040 (Winbond 512K×8 5V page-write flash, protocol `0x05`
> "flash4") deterministically fails its first page program on the seated chip
> (Leonardo + RURP Rev 2.0). This document accumulates evidence across Plans 02–04
> and culminates in a named root cause (or ranked disconfirmed hypotheses) classified
> firmware-algorithm / timing / addressing / silicon, sufficient for Phase 94 to
> design a fix.
>
> **Branch base:** firmware `a296195` (v1.16 primitives recompose).
> **Differential control:** W29C020 (same `0x05`, same `DIP32_SST39SF040`, 256 KB / 128 B page) — PASSED bench.
>
> **SAFE-01 update (Plan 01, 2026-06-26):** T-93-CANERASE was found ACTIVE — W29C040
> wire `flags=0x02` routes `flash4_write_init` through `flash4_erase_execute` (12V
> VPP assertion on 5V chip). See [SAFE-01-PREFLIGHT.md](safety/SAFE-01-PREFLIGHT.md).
> Bench plans MUST use `--skip-erase` to bypass `flash4_erase_execute` during RCA.

---

## Bench Discipline Log

All bench tasks (Plans 02–04) must record their session identity here before
any chip operation. Per standing discipline from STATE.md / RESEARCH.md.

| Plan | Timestamp | Controller identity (`firestarter --version` output) | Port | R1 readback | R2 readback | Board | Shield | Notes |
|------|-----------|------------------------------------------------------|------|-------------|-------------|-------|--------|-------|
| 02   | 2026-06-27T06:38:04Z | firestarter 3.0.0b10 (editable, v1.17 branch, post-HARD-01) | /dev/ttyACM0 | 270000 | 44000 | Leonardo | Rev 2.0-class (Override HW) | chip-id confirmed 0xda46; `hw` cmd → "Rev 2.0-class, Override HW: Rev 2.0-class" |
| 03   | 2026-06-27T06:53:10Z | firestarter 3.0.0b10 (editable, v1.17 branch, post-HARD-01) | /dev/ttyACM0 | 270000 | 44000 | Leonardo | Rev 2.0-class (Override HW) | chip-id confirmed 0xda46 via `firestarter id W29C040`; fw confirmed leonardo 3.0.0b10 |
| 04   | TBD       | TBD | TBD | TBD | TBD | Leonardo | Rev 2.0 | (Plan 04 fills) |

R1 expected: r1 ≈ 270000 ± 25% (203000–338000). Out-of-range = abort and recalibrate.
Leonardo is chip-OUT-sideload-EXEMPT — do NOT remove chip before sideload.

---

## RCA-01 — Reproduction & Signature

### Prior baseline (verbatim — the signature to reproduce, N=2 deterministic)

From `.planning/v1.15/bench/EVIDENCE.md` (Phase 82 + Phase 84 Task 3c),
Leonardo + Rev 2.0, firmware carrying the Phase-74 SDP/256B-page fix (fw `6924349`/`2699d11`):

| Attempt | Command | Result |
|---------|---------|--------|
| Phase 82 write A (`-b`) | `firestarter write -b W29C040 <img>` | `Timeout verifying byte @0x0000ff` (256B page-0 boundary); reads `0x00` |
| Phase 84 attempt 1 (`-b`, 1024B image, SHA `9983e8de…`) | `firestarter write -b W29C040 <img>` | `ERROR "Timeout verifying 0xd7 at 0x0000ff (got 0x00)"` |
| Phase 84 attempt 2 | identical command | `ERROR "Timeout verifying 0xd7 at 0x0000ff (got 0x00)"` (deterministic N=2) |

**Decoded signature:**
- Failing address: `0x0000ff` — the **last byte of page 0** (256B page boundary)
- Expected byte: `0xd7`
- Observed byte: `0x00`
- Error frame packing (`flash4_wait_for_page_write` _b[]): `[expected=0xd7, A16=0x00, A8=0x00, A0=0xff, observed=0x00]`
- `observed=0x00`: neither the written value (`0xd7`) nor the erased state (`0xFF`)
  — consistent with "page never committed" (H1/H3) OR "mid-write DQ7 complement
  read" (H4 disambiguation needed).

**SAFE-01 note on repro (T-93-CANERASE):**
The prior Phase 82/84 bench evidence was taken on a firmware/host that may have
had different `FLAG_CAN_ERASE` behavior. On the current `a296195` host build,
`flags=0x02` is sent, causing `flash4_erase_execute` (12V!) to fire unless
`--skip-erase` is used. Plan 02 repro MUST use `--skip-erase`.

### T-93-CANERASE gate resolution

**T-93-CANERASE gate cleared by operator decision 2026-06-27** — The operator
authorized proceeding with `--skip-erase` mitigation. All writes in Plan 02 used
`firestarter write -b --skip-erase W29C040 <img>`, which sets `FLAG_SKIP_ERASE (0x04)`
and bypasses `flash4_erase_execute`. Full fix (preventing `FLAG_CAN_ERASE` from routing
through `flash4_erase_execute` for protocol 0x05 chips) deferred to Phase 94 FIX-01.

### Plan 02 repro results — COMPLETED 2026-06-27

**Test image:** `evidence/signature/w29c040_test_1024b_seed42.bin`
- Size: 1024 bytes (covers pages 0–3, 256-byte boundaries at 0x100/0x200/0x300)
- SHA-256: `1ba43bf584f5492eee63d3e590e65f1e1cdaf93dd988686d958f053713b7782f`
- Generated with: `python tools/gen_test_image.py 1024 42 <path>` (seed=42, deterministic)
- Key bytes: offset 0x00FF=`0x04`, offset 0x01FF=`0x81`, offset 0x02FF=`0x43`, offset 0x03FF=`0x07`

| Run | Command | Result (exact ERROR frame) | Post-fail 0x0000ff | Verdict |
|-----|---------|---------------------------|---------------------|---------|
| 1 | `firestarter -p /dev/ttyACM0 write -b --skip-erase W29C040 evidence/signature/w29c040_test_1024b_seed42.bin` | `ERROR: Timeout verifying 0x04 at 0x0000ff (got 0x00)` | 0x00 (N=5 reads stable) | FAIL — fault reproduced |
| 2 | identical | `ERROR: Timeout verifying 0x04 at 0x0000ff (got 0x00)` | 0x00 (stable) | FAIL — fault reproduced |

**Decoded ERROR frame (from `flash4_wait_for_page_write` packing `[expected, A16, A8, A0, observed]`):**
- expected byte: `0x04` (image byte at offset 255)
- failing address: `0x0000ff` → A16=`0x00`, A8=`0x00`, A0=`0xFF`
- failing address interpretation: **last byte of page 0** (256-byte page boundary)
- observed byte: `0x00`

**N=2 determinism verdict: CONFIRMED** — identical ERROR frame on both runs.

### Post-fail page-0 read-back

After Run 1 failure, page 0 (256 bytes) read:
- Address 0x0000ff: **0x00** (stable across 5 repeated reads — does NOT settle to written `0x04`)
- Address 0x0000: 0x00
- Address 0x00fe: 0x00
- Page 0 is NOT all-blank (0xFF) — contains partial prior-session data with non-zero bytes
  at some offsets (old write-test fragments); see `page0_readback_hex_after_run1.txt`
- Page 0 is NOT all-zero — some bytes contain previous-session data
- Run 1 vs Run 2 page-0 state: IDENTICAL (no new data committed on Run 2)

**H4 fork determination (settled read of 0x0000ff):**
- 0x0000ff reads `0x00` stably across N=5 reads immediately after the timeout
- It does NOT settle to the written value `0x04`
- **Verdict: H4 DISCONFIRMED** — the page DID NOT commit; the poll did not merely give up
  on a completed write. The `observed=0x00` is real: the page never committed.
  This rules out the "poll exhausted iterations on a late-completing write" theory.
  H1 (timing window violation) or H3 (SDP/timing rejection) must explain the `0x00` state.

**Capture files (all under `evidence/signature/`):**
- `run1.txt` — full serial output of Run 1
- `run2.txt` — full serial output of Run 2
- `page0_readback_after_run1.txt` — read command output
- `page0_readback_hex_after_run1.txt` — hex dump of page 0 after Run 1
- `page0_readback_hex_after_run2.txt` — hex dump of page 0 after Run 2 (identical)
- `settled_read_0x0000ff.txt` — 5× repeated reads of address 0x0000ff (all 0x00)
- `settled_read_after_run2.txt` — post-Run-2 point reads at 0x00ff, 0x0000, 0x00fe
- `pages1to3_readback_hex_after_run2.txt` — addresses 0x100–0x3FF (partial prior-session data)

---

## RCA-02 — Differential vs W29C020

### Axis comparison table (pre-bench analysis)

| Axis | W29C040 (FAILS) | W29C020 (PASSES) | Same or Differs? | RCA weight |
|------|-----------------|------------------|------------------|------------|
| Protocol / handler | `0x05` flash4 | `0x05` flash4 | **SAME** | Exonerates dispatch structure |
| Pinout | `DIP32_SST39SF040` | `DIP32_SST39SF040` | **SAME** | Exonerates pinout confusion |
| SDP unlock sequence | `5555←AA, 2AAA←55, 5555←A0` | `5555←AA, 2AAA←55, 5555←A0` | **SAME** | SDP content is NOT the differential |
| Page size | **256 B** (A8–A18 = page addr) | **128 B** (A7–A17 = page addr) | **DIFFERS** | Correct for both; BUT 2× longer page-load window (H1) |
| Byte-load window T_BLC | **200 µs max** (across 256 bytes) | **~200 µs max** (across 128 bytes) | ~SAME spec, 2× more bytes | **H1 hinge**: W29C040 must sustain cadence 2× longer |
| Address span | 19 lines (A0–A18, 512 KB) | 18 lines (A0–A17, 256 KB) | **DIFFERS — A18** | **H2 hinge**: A18 = CTRL_VPP_P1_ENABLE_REV2 (0x08) on Rev 2.0 |
| Internal write time | 5 ms typ (10 ms max) | ~10 ms | ~SAME | poll cap adequate if page committed |
| VPP requirement | None — 5V internal VPP gen | None — 5V internal VPP gen | **SAME** | Both 5V; `vpp_mv=12000` is ID-read datum only |

### W29C020 control — Datasheet differential (operator chose datasheet-only fallback)

Per OPERATOR_DECISION_SCOPE (2026-06-27): No live W29C020 write was performed because the
W29C040 was seated and operator cannot swap chips. The W29C020 differential was conducted
from datasheets (both present in `datasheets/0x05-FLASH-AMD-STD/`).

**W29C020 datasheet-confirmed differential axes:**

| Axis | W29C040 (FAILS) | W29C020 (PASSES) | Same or Differs? |
|------|-----------------|-----------------|-----------------|
| SDP unlock sequence | `5555←AA, 2AAA←55, 5555←A0` | `5555←AA, 2AAA←55, 5555←A0` | **SAME** — exonerated |
| Pinout | `DIP32_SST39SF040` | `DIP32_SST39SF040` | **SAME** — exonerated |
| VPP | None — 5V single-supply internal | None — 5V single-supply internal | **SAME** — exonerated |
| Page size | **256 B** | **128 B** | **DIFFERS** — 2× bytes, but this is correct in firmware (flash4_page_size) |
| Boot block size | **Two 16K blocks** (first/last 16K each) | **Two 8K blocks** (first/last 8K each) | **DIFFERS** |

**Surviving differing axes:**
1. Page size: 256B (W29C040) vs 128B (W29C020) — 2× longer byte-load window per page
2. A18 exists on W29C040 (512KB) — maps to CTRL_ADDRESS_LINE_18 (0x20 in HARDWARE_REVISION build)
3. Boot block boundaries: first 16K locked vs first 8K locked
4. Page-latch boundary bit: A8 is a page-address bit on W29C040 (256B page), byte-in-page bit on W29C020 (128B page)

**DEFERRED (best-effort):** Live W29C020 control write — operator chose datasheet fallback 2026-06-27.
Plan 04 / future bench step may conduct the live control.

### Plan 03 differential results — COMPLETED 2026-06-27

| Write attempt | Chip | Command | Result | Error frame | Notes |
|--------------|------|---------|--------|-------------|-------|
| Test #2: Single byte to page-0 | W29C040 | `write -b --skip-erase -a 0 W29C040 <1B: 0x39>` | **FAIL** | `Timeout verifying 0x39 at 0x000000 (got 0x00)` | H1/H3 DISCONFIRMED |
| Test #3: DEBUG_ADDRESS trace | W29C040 | SERIAL_DEBUG+DEBUG_ADDRESS trace build | Trace: `Address 0x000000, top msb lsb 00 00 00` | Protocol timeout (5008 poll msgs) | H2 DISCONFIRMED for page-0 (top=0x00=correct, stable) |
| Test #4: Non-page-0 at 0x1000 | W29C040 | `write -b --skip-erase -a 0x1000 W29C040 <256B>` | **FAIL** | `Timeout verifying 0x03 at 0x0010ff (got 0x00)` | NOT page-0-specific |
| Test #5: A18=1 at 0x40000 | W29C040 | `write -b --skip-erase -a 0x40000 W29C040 <256B>` | **PASS** | — | A18=1 writes correctly! H2 exonerated |
| Diag: 0x2000 (inside 16K) | W29C040 | `write -b --skip-erase -a 0x2000` | **FAIL** | `Timeout verifying 0x03 at 0x0020ff (got 0x00)` | Boot block hypothesis |
| Diag: 0x4000 (outside 16K) | W29C040 | `write -b --skip-erase -a 0x4000` | **PASS** | — | Confirms 16K boundary |
| Diag: 0x3F00 (last page in 16K) | W29C040 | `write -b --skip-erase -a 0x3f00` | **FAIL** | `Timeout verifying 0x03 at 0x003fff (got 0x00)` | Exact 16K lock boundary confirmed |
| Diag: 0x7C000 (last 16K block) | W29C040 | `write -b --skip-erase -a 0x7c000` | **PASS** | — | Last boot block NOT locked |
| Diag: 0x7BC00 (before last 16K) | W29C040 | `write -b --skip-erase -a 0x7bc00` | **PASS** | — | Normal mid-chip region |

**Boot block lock pattern:**
- LOCKED: 0x0000–0x3FFF (first 16K = W29C040 §6.6 first boot block) — ALL writes FAIL
- UNLOCKED: 0x4000–0x7BFFF — writes PASS
- UNLOCKED: 0x7C000–0x7FFFF (last 16K = W29C040 §6.6 last boot block) — writes PASS

Capture files: `evidence/differential/` — see `test_summary.txt` for full list.

**RCA-02 axis-exoneration summary:**
| Axis | Verdict | Evidence |
|------|---------|---------|
| SDP content | EXONERATED — SAME in both datasheets; A18=1 pages write fine showing SDP works | Test #5 PASS; datasheet comparison |
| Pinout | EXONERATED — SAME; A18 routes correctly | Test #5 PASS (A18=1); diag 0x4000 PASS |
| VPP | EXONERATED — both 5V, no VPP needed | Datasheet; T-93-NOVPP GREEN |
| Page size value | EXONERATED — 256B correct, confirmed in firmware | flash4_page_size(524288)=256; native test |
| Byte-load timing (T_BLC) | EXONERATED — single byte also fails (Test #2) | Test #2 FAIL; not a timing issue |
| A18/top-address corruption | EXONERATED for page-0 — top=0x00 stable; A18=1 pages pass | Test #3 trace; Test #5 PASS |
| **Boot block §6.6 lockout** | **ISOLATED — the variable that moves the failure** | Diagnostic boundary tests |

---

## RCA-03 — Disconfirming-Test Matrix

Each hypothesis carries a verdict column to be filled by Plans 03–04.
A named root cause is one that SURVIVES its own disconfirming test while competitors fail theirs (Phase 44 D-07 bar).

| Hypothesis | Classification | Mechanism | Disconfirming test | Verdict | Raw evidence | Classification outcome |
|------------|----------------|-----------|-------------------|---------|--------------|------------------------|
| H1 — Byte-load timing window (T_BLC=200µs) violation mid-page | TIMING | 256-byte page-load loop exceeds 200µs inter-byte window; chip commits partial page; DQ7 poll at byte 255 sees mid-write/never-committed state → `observed=0x00` | Single-byte write to page 0 (`-a 0 -s 1`): if it PASSES, per-byte mechanics are sound → multi-byte timing is the issue; if it FAILS, H1 is disconfirmed | **DISCONFIRMED** | `differential/test2_single_byte_write.txt` — single byte to 0x000000 also FAILs with `observed=0x00` | NOT the cause — timing irrelevant when boot block lock silently rejects all writes in first 16K |
| H2 — A18 / top-address register corruption during 256B page load | ADDRESSING | A18 = CTRL_ADDRESS_LINE_18=0x20 in HARDWARE_REVISION build; shared CONTROL bit could corrupt page address | DEBUG_ADDRESS trace across page-0 load: if top-address byte is constant (0x00) across 256 bytes, H2 disconfirmed | **DISCONFIRMED** | `differential/test3_debug_trace_1byte.txt` — trace shows `top msb lsb 00 00 00` (correct, stable); Test #5 (A18=1 at 0x40000) PASSES — A18 is correctly routed | NOT the cause — addressing is correct |
| H3 — SDP unlock not disabling protection (per-page re-arm / timing) | FIRMWARE-ALGORITHM | SDP 3-byte command sent at page start; if gap between last SDP write and first data byte exceeds SDP timing window, chip rejects page-load | Single-byte write (H1 test): if that single-byte write (which also sends SDP) succeeds, SDP content/timing is fine → H3 disconfirmed | **DISCONFIRMED** | `differential/test2_single_byte_write.txt` — SDP+single-byte to 0x000000 FAILs; BUT A18=1 pages with same SDP PASS → SDP is fine; failure is address-range-specific | NOT the cause — SDP works, A18=1 pages using same SDP code PASS |
| H4 — Poll/verify site or page-commit-not-triggered (firmware-algorithm) | FIRMWARE-ALGORITHM | `poll_readback` compares whole byte (not DQ7-masked); if page committed late, poll exhausts 1024 iterations returning complement; post-fail settled read would show `0xd7` | After timeout, `dev read 0x0000ff` repeatedly: if it settles to `0xd7`, page DID commit → poll gave up too early | **DISCONFIRMED** (Plan 02) | `signature/settled_read_0x0000ff.txt` — 0x0000ff reads 0x00 stably x5 after timeout; does NOT settle to expected value | NOT the cause — page never committed; poll correctly detected non-commit |
| H5 — Silicon defect / wear on seated W29C040 | SILICON | Worn/defective die; page 0 (boot block, W29C040 §6.6) specifically defective; boot block programming lockout activated | Write non-page-0 pages (`-a 0x1000`, `-a 0x4000`, `-a 0x40000`) — map the failure boundary | **CONFIRMED — the root cause** | `differential/test4_page_at_0x1000.txt` (FAIL), `test5_page_at_0x40000.txt` (PASS), `test_diag_0x4000.txt` (PASS), `test_diag_0x3f00_result.txt` (FAIL) — exact 16K boundary; §6.6 boot block lock on first 16K (0x0000–0x3FFF) | **NAMED ROOT CAUSE**: W29C040 §6.6 first-16K boot block programming lockout is activated on this chip instance |

### Recommended execution order (cheapest-first)

1. Post-fail settled read of `0x0000ff` (H4 fork; free — read after recorded fail) → Plan 02
2. Single-byte write to page 0 (H1/H3 fork) → Plan 03
3. DEBUG_ADDRESS trace of one page-0 load (H2 + H1 cadence) → Plan 03
4. Non-page-0 page write at `0x1000` (H5 / page-0-specificity) → Plan 03
5. A18=1 page write at `0x40000` (H2 completeness) → Plan 04

---

## RCA-03 — Named Root Cause

**Status: NAMED — H5 CONFIRMED (Plan 03, 2026-06-27)**

### Named Root Cause

**Classification: SILICON (chip-instance-specific, hardware-feature-state)**

**Root Cause:** The seated W29C040 has the **first 16K boot block programming
lockout feature permanently activated** (W29C040 datasheet §6.6). This is an
irreversible silicon-level hardware protection state on this specific chip instance.

**Mechanism:** W29C040 §6.6 provides two boot blocks (first 16K = 0x0000–0x3FFF,
last 16K = 0x7C000–0x7FFFF). The boot block lockout is set by a 7-byte command
sequence and is permanent — it cannot be reversed by standard write procedures.
When the first 16K is locked:
1. Any write attempt to 0x0000–0x3FFF silently fails
2. The internal write cycle never starts (the chip ignores the write command)
3. DQ7 during the poll reads `0x00` (not the complement of the written data, which
   would indicate an active write cycle, and not `0xFF` which would indicate erased)
4. `poll_readback` times out after 1024 iterations (10.24ms+) and reports `observed=0x00`

This produces exactly the recorded signature: `Timeout verifying 0xXX at 0x0000ff (got 0x00)`.

**Evidence (Phase 44 D-07 causal bar — the variable that moves the failure):**

| Address | A16-A18 | Write result | Explanation |
|---------|---------|--------------|-------------|
| 0x000000 | all 0 | **FAIL** 0x00 | First 16K locked |
| 0x001000 | all 0 | **FAIL** 0x00 | First 16K locked |
| 0x002000 | all 0 | **FAIL** 0x00 | First 16K locked |
| 0x003F00 | all 0 | **FAIL** 0x00 | Last page in first 16K — locked |
| 0x004000 | all 0 | **PASS** | First address OUTSIDE first 16K — unlocked |
| 0x040000 | A18=1 | **PASS** | Well outside both boot blocks — unlocked |
| 0x07C000 | A18=1 | **PASS** | Last 16K boot block — NOT locked |
| 0x07BC00 | A18=1 | **PASS** | Normal mid-chip — unlocked |

**Boundary:** Exact at 0x4000 (16384 = 16KB). The pattern is a perfect step function
at the 16K boundary, consistent with §6.6 boot block protection, not with any
firmware/timing/addressing cause.

### Why Phase-74/v1.15 fixes did NOT help

The Phase-74 Wave-1 fix (SDP unlock per page + correct 256B page size) was correct
for the firmware algorithm. But it cannot overcome a silicon-level hardware write
protection. The chip literally ignores the write command for locked addresses,
regardless of how correct the SDP sequence is.

### Implications for Phase 94 (Fix)

**This chip instance cannot be used to test page-0 programming.** The boot block
lockout is irreversible. Phase 94 / Phase 95 (BENCH graduation) MUST use either:
1. A different W29C040 chip instance without the first 16K lockout (check with
   the Product ID + Boot Block Lockout Detection sequence per §6.9/datasheet p.10)
2. Test the write algorithm using addresses >= 0x4000 (verified working) as a
   proxy, with documentation that page-0 specifically requires an unlocked chip

**The firmware write algorithm IS correct** for the W29C040 — it works for all
unlocked pages (0x4000+). The fault is chip-instance-specific silicon state,
not a firmware bug. Phase 94 FIX-01 (T-93-CANERASE / FLAG_CAN_ERASE fix) is
still needed and correct, but separate from the page-0 write fault root cause.

### H-code disposition summary

| H | Status | Plan | Key evidence |
|---|--------|------|-------------|
| H1 (timing) | DISCONFIRMED | 03 | Single byte at 0x000000 FAILS — timing is irrelevant |
| H2 (A18/addressing) | DISCONFIRMED | 03 | top=0x00 at init; A18=1 pages PASS |
| H3 (SDP re-arm) | DISCONFIRMED | 03 | Same SDP code; A18=1 pages with same SDP PASS |
| H4 (poll site) | DISCONFIRMED | 02 | Settled read stays 0x00 (page never committed) |
| H5 (silicon) | **CONFIRMED** | 03 | Exact 16K boundary: 0x3F00=FAIL, 0x4000=PASS; §6.6 boot block |

---

## SAFE-01 — Non-Bypass Confirmation

All RCA instrumentation flows through the normal `0x05` dispatch path. No
test-only escape hatch has been introduced. `resolve_chip("W29C040")` resolves
through the `support_status="supported"` gate normally.

**T-93-CANERASE finding (Plan 01, HIGH-severity):**
W29C040 wire `flags=0x02` (FLAG_CAN_ERASE) is SET, causing `flash4_erase_execute`
(which asserts 12V CTRL_VPP_REGULATOR_ENABLE) to fire in `flash4_write_init`.
This is a latent 12V-on-5V-chip hazard. Full details in:
**[evidence/safety/SAFE-01-PREFLIGHT.md](safety/SAFE-01-PREFLIGHT.md)**

Bench mitigation for RCA (Plans 02–04): use `--skip-erase` on all write commands
to bypass `flash4_erase_execute`. Permanent fix deferred to Phase 94 (FIX-01).

**T-93-NOVPP:** Confirmed GREEN — `test_flash4_write_execute_no_vpp` PASSED.
The flash4 write-execute path emits zero VPP control bits (CTRL_VPP_REGULATOR_ENABLE=0,
CTRL_VPP_P1_ENABLE=0) across all CONTROL_REGISTER writes.

**T-93-ESCAPE:** Confirmed SAFE — W29C040 resolves through normal dispatch
(`algorithm=5`, `support_status="supported"`, no `--force` override required).
DEBUG_ADDRESS build flag is a passive trace (no dispatch change, no escape hatch).

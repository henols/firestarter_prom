---
artifact: 93-RCA-FINDINGS
phase: 93-rca-root-cause-the-w29c040-page-0-write-fault
milestone: v1.17 — Implement & Test the W29C040 Programming Protocol
requirements: [RCA-01, RCA-02, RCA-03, SAFE-01]
status: scaffold (Plans 02–04 will fill the evidence sections)
recorded: 2026-06-26
operator_witnessed: false (bench evidence pending)
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
| 02   | TBD       | TBD | TBD | TBD | TBD | Leonardo | Rev 2.0 | (Plan 02 fills) |
| 03   | TBD       | TBD | TBD | TBD | TBD | Leonardo | Rev 2.0 | (Plan 03 fills) |
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

### Plan 02 repro results (to be filled)

| Run | Command | Result (exact ERROR frame or PASS) | Post-fail page-0 read | Notes |
|-----|---------|------------------------------------|-----------------------|-------|
| 1 | `firestarter write -b --skip-erase W29C040 <img>` | TBD | TBD | (Plan 02 fills) |
| 2 | `firestarter write -b --skip-erase W29C040 <img>` | TBD | TBD | (Plan 02 fills) |

Capture dirs: `evidence/signature/` (ERROR frames, DEBUG_ADDRESS traces, post-fail reads)

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

### Plan 03 differential results (to be filled)

| Write attempt | Chip | Command | Result | Notes |
|--------------|------|---------|--------|-------|
| Control (sibling) | W29C020 | `firestarter write -b --skip-erase W29C020 <128K img>` | TBD | (Plan 03 fills) |
| Test (failing chip) | W29C040 | `firestarter write -b --skip-erase W29C040 <512K img>` | TBD | (Plan 03 fills) |
| Single byte | W29C040 | `firestarter write -b --skip-erase W29C040 -a 0 -s 1 <1B img>` | TBD | H1/H3 fork |
| Non-page-0 | W29C040 | `firestarter write -b --skip-erase W29C040 -a 0x1000 <256B img>` | TBD | H5 / page-0-specificity |
| A18=1 page | W29C040 | `firestarter write -b --skip-erase W29C040 -a 0x40000 <256B img>` | TBD | H2 completeness |

Capture dirs: `evidence/differential/` (paired write attempts, SHAs)

---

## RCA-03 — Disconfirming-Test Matrix

Each hypothesis carries a verdict column to be filled by Plans 03–04.
A named root cause is one that SURVIVES its own disconfirming test while competitors fail theirs (Phase 44 D-07 bar).

| Hypothesis | Classification | Mechanism | Disconfirming test | Verdict | Raw evidence | Classification outcome |
|------------|----------------|-----------|-------------------|---------|--------------|------------------------|
| H1 — Byte-load timing window (T_BLC=200µs) violation mid-page | TIMING | 256-byte page-load loop exceeds 200µs inter-byte window; chip commits partial page; DQ7 poll at byte 255 sees mid-write/never-committed state → `observed=0x00` | Single-byte write to page 0 (`-a 0 -s 1`): if it PASSES, per-byte mechanics are sound → multi-byte timing is the issue; if it FAILS, H1 is disconfirmed | TBD | TBD | TBD |
| H2 — A18 / top-address register corruption during 256B page load | ADDRESSING | A18 = CTRL_VPP_P1_ENABLE_REV2 (0x08) on Rev 2.0; shared CONTROL bit could corrupt page address consistency across 256-byte load | DEBUG_ADDRESS trace across one full page-0 load: if top-address byte is constant (0x00) across all 256 bytes, H2 is disconfirmed for page 0 | TBD | TBD | TBD |
| H3 — SDP unlock not disabling protection (per-page re-arm / timing) | FIRMWARE-ALGORITHM | SDP 3-byte command sent at page start; if gap between last SDP write and first data byte exceeds SDP timing window, chip rejects page-load | Single-byte write (H1 test): if that single-byte write (which also sends SDP) succeeds, SDP content/timing is fine → H3 disconfirmed | TBD | TBD | TBD |
| H4 — Poll/verify site or page-commit-not-triggered (firmware-algorithm) | FIRMWARE-ALGORITHM | `poll_readback` compares whole byte (not DQ7-masked); if page committed late, poll exhausts 1024 iterations returning complement; post-fail settled read would show `0xd7` | After timeout, `dev read 0x0000ff` repeatedly: if it settles to `0xd7`, page DID commit → poll gave up too early (H4 confirmed); if stays `0x00`/`0xFF` → H4 disconfirmed | TBD | TBD | TBD |
| H5 — Silicon defect / wear on seated W29C040 | SILICON | Worn/defective die; page 0 (boot block, W29C040 §6.6) specifically defective | Write a non-page-0 page (`-a 0x1000`): if that succeeds but page 0 fails deterministically → boot-block-specific or silicon; if all pages fail → H5 still possible | TBD | TBD | TBD |

### Recommended execution order (cheapest-first)

1. Post-fail settled read of `0x0000ff` (H4 fork; free — read after recorded fail) → Plan 02
2. Single-byte write to page 0 (H1/H3 fork) → Plan 03
3. DEBUG_ADDRESS trace of one page-0 load (H2 + H1 cadence) → Plan 03
4. Non-page-0 page write at `0x1000` (H5 / page-0-specificity) → Plan 03
5. A18=1 page write at `0x40000` (H2 completeness) → Plan 04

---

## RCA-03 — Named Root Cause (or Ranked Hypotheses)

**Status: PENDING — to be filled by Plan 04**

The named root cause will be recorded here once the disconfirming-test matrix is
complete. Per the Phase 44 D-07 causal bar: the named cause must survive its
disconfirming test while competitors fail theirs.

Expected verdict shape (from RESEARCH § "Root-Cause Classification" pre-analysis):
Leading candidate = H1 (timing — byte-load window T_BLC violation mid-page),
with H4 (whole-byte vs DQ7-masked poll) as likely contributing factor.
The bench matrix will confirm or overturn this ranking.

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

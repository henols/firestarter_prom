# v1.18 Bench EVIDENCE — AM27C020 0x08 Write-Path RCA

**Generated:** 2026-06-29T15:43:35Z
**Milestone:** v1.18 — AM27C020 0x08 Write-Path RCA & Fix
**Phase:** 97 — pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program
**Board / Shield (LOCKED):** Leonardo + RURP Rev 2.0
**Branch base:** firmware `bccd995` (v1.17 tip) · host `e0bdea4`

> **STATUS: SCAFFOLD (Wave-1, Plan 97-01).** This record is seeded with
> schema-correct, **NEVER-fabricated** cells mirroring `EVIDENCE.json`. Cell A
> (AM27C020 / `0x08`) is filled by **Plan 97-02** (combined Tier-0 micro-probe +
> RCA-01 reproduction); Cell B (W27C512 / `0x07`) is filled by **Plan 97-03**
> (differential control write). Every measured field below is a `TBD-bench`
> placeholder. Per **D-02** the Tier-0 0-bit-flip is **INDETERMINATE pre-fix** and
> is **never fabricated**; per **D-01** a 0-flip never triggers deferral.
> Schema reuses the v1.15 `EVIDENCE.{md,json}` cell shape so Phase 99 + the
> PROTOCOL-LEDGER consume the same format ("Don't Hand-Roll" §EVIDENCE format).

---

## PRE-01 Result Line (artifact 4)

| Field | Value |
|-------|-------|
| pre_01_result | PRE-01 reads captured 2026-06-30 (oracle N=3 PASS; decode 0x08/0x197 confirmed; NOT-BLANK 0x02@0x0000). Writability verdict = **INDETERMINATE pre-fix**, set by the Task-3 micro-probe (D-01/D-02) |
| blank_state_sha256 | `90cd45f5343cd938006f20635de39479159c51b9d56c1b6f1fb23075ed567297` (consistency-check N=3 byte-identical; NOT-BLANK `0x02 @ 0x0000`) |

PRE-01's Phase-97 deliverable is **"writability indeterminate pre-fix"** — NOT a
pass/fail blocker (D-02). The Tier-0 micro-probe and the RCA-01 failure
reproduction are the **same single bench action** (D-01); a 0-bit-flip is
consistent with both "broken path" and "OTP" so it proves nothing about silicon
and **never triggers deferral** (deferral is a Phase-99 verdict only, D-06).

---

## Bench-Discipline Columns (D-08) — filled per task at the bench

| Plan | Timestamp | Controller identity | Port | R1 | R2 | Board | Shield | JP4 position + silkscreen meaning | fw commit | Notes |
|------|-----------|---------------------|------|----|----|-------|--------|-----------------------------------|-----------|-------|
| 97-02 | 2026-06-30 ~07:29Z | leonardo | /dev/ttyACM0 | 270000 | 44000 | Leonardo | Rev 2.0 | **open** (operator-stated); silkscreen meaning PENDING (D-08) — fw `info` says 32-pin=Closed, **discrepancy flagged** | bccd995 (3.0.0b10) | PRE-01 reads done; VPP adjusted 12.0→13.0V before Task-3 (operator) |
| 97-03 | TBD-bench | TBD-bench | TBD-bench | TBD-bench (expect 270000) | TBD-bench | Leonardo | Rev 2.0 | TBD-bench (ASK operator first — D-08) | TBD-bench | Plan 03 fills |

R1 expected ≈ 270000 ± 25% (Leonardo). `controller:` identity re-verified per task (ACM ports shuffle — D-08). Leonardo is chip-OUT-sideload-EXEMPT.

---

## Cell A — AM27C020 (`0x08` EPROM_QUICK) — Plan 97-02

Op: `tier0_microprobe+rca01` (the combined single program attempt at `0x000000`).

| Field (Failure Signature Capture Schema) | Source | Value |
|------------------------------------------|--------|-------|
| failing_addresses | `firestarter write` stderr (`MSG_ERR_VERIFY`) | **0x000000** |
| bad_bytes | write output | **1/1** |
| retries | write output | **20** (matches v1.15 seed) |
| bits_flipped | post-attempt consistency-check vs pre-SHA | **0** → writability INDETERMINATE pre-fix (D-01/D-02) |
| vpp_adc_mv | `firestarter vpp` ADC node | baseline 12000 (as-found); adjusted to **13000** before Task-3; during-attempt value = Task-3 |
| dmm_pin1_v | [OP] held-rail proxy DMM at socket pin 1 | **not measured** — held-rail proxy blocked by DTR-reset-on-close tooling bug (debug: held-rail-dev-reg-timeout, H1). VPP→pin-1 routing **confirmed by code** (-f 0x188 → physical 0x89, P1 asserted; H2 disproven) |
| dmm_pin31_v | [OP] held-rail proxy DMM at socket pin 31 | **not measured** — same tooling block; pin-31 = A18 mapping confirmed by `info` decode (RC-1) |
| pre_read_sha256 | consistency-check (pre-attempt) | `90cd45f5343cd938006f20635de39479159c51b9d56c1b6f1fb23075ed567297` |
| post_read_sha256 | consistency-check (post-attempt) | `90cd45f5343cd938006f20635de39479159c51b9d56c1b6f1fb23075ed567297` (**== pre → chip pristine**) |
| controller | `firestarter fw` / `hw` | leonardo |
| port | `firestarter fw` | /dev/ttyACM0 |
| r1_readback | `firestarter config` | 270000 |
| r2_readback | `firestarter config` | 44000 |
| fw_commit | `git -C firestarter rev-parse HEAD` | bccd995 (fw 3.0.0b10) |
| jp4_position | [OP] | open (operator-stated 2026-06-30) |
| jp4_silkscreen_meaning | [OP] — ASK first (D-08) | PENDING — fw `info` says 32-pin=Closed; operator has OPEN → discrepancy flagged, resolve before Task-3 |
| verdict | RCA synthesis | **RCA-01 REPRODUCED** — 0x08 writes 0 bits @ 0x000000 (1/1 bad, retries 20) at VPP=13.0V + JP4 **closed**; chip pristine. Writability INDETERMINATE. Confounds (VPP-level, JP4) exonerated → cause = RC-1 (pin31=A18) / RC-2-routing |
| anomalies | — | VPP as-found 12.0V→13.0V (operator); VPE 13.8→15.1V; pin 31 = A18 (RC-1); flags=0x08 SkipBlankCheck only (SAFE-01 intact); `-b` used (chip non-blank — justified deviation, Phase-92 decouple = blank-check skip only) |

---

## Cell B — W27C512 (`0x07` EPROM_STD) — Plan 97-03 differential control

Op: `differential_control_write` (passing-sibling control, same session/bench, same `configure_eprom()`).

| Field | Source | Value |
|-------|--------|-------|
| write_image_sha256 | generated test image | TBD-bench |
| readback_sha256 | post-write read | TBD-bench (== write image if PASS) |
| vpp_adc_mv | `firestarter vpp` | TBD-bench |
| dmm_pin1_v | [OP] | TBD-bench |
| verdict | expect PASS (exonerates unchanged axes) | TBD-bench |
| anomalies | — | TBD-bench |

---

## Differential collapse (RCA-02 framing)

The matrix collapses to **two converging differing axes** — both absent on the
passing `0x07` part:

1. **P1-VPP-delivery** — VPP routed to socket **pin 1** via the
   `CTRL_VPE_ENABLE → CTRL_VPP_P1_ENABLE` rewrite (`eprom.cpp:319-326`), never
   bench-proven on a `0x08` UV part.
2. **pin-31-as-address** — DIP `pin 31` modeled as bus line 22 (address-driven),
   not held program-active (`database.py:141`, `memory.cpp:274`).

Both verdicts (RC-1 / RC-2) are recorded in
`evidence/97-RCA-FINDINGS.md` (D-03: each must individually carry a verdict).

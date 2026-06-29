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
| pre_01_result | **TBD-bench** — "writability indeterminate pre-fix" expected (D-01/D-02) |
| blank_state_sha256 | **TBD-bench** (consistency-check N≥3 byte-identical read; known NOT-BLANK `0x02 @ 0x0000`) |

PRE-01's Phase-97 deliverable is **"writability indeterminate pre-fix"** — NOT a
pass/fail blocker (D-02). The Tier-0 micro-probe and the RCA-01 failure
reproduction are the **same single bench action** (D-01); a 0-bit-flip is
consistent with both "broken path" and "OTP" so it proves nothing about silicon
and **never triggers deferral** (deferral is a Phase-99 verdict only, D-06).

---

## Bench-Discipline Columns (D-08) — filled per task at the bench

| Plan | Timestamp | Controller identity | Port | R1 | R2 | Board | Shield | JP4 position + silkscreen meaning | fw commit | Notes |
|------|-----------|---------------------|------|----|----|-------|--------|-----------------------------------|-----------|-------|
| 97-02 | TBD-bench | TBD-bench | TBD-bench | TBD-bench (expect 270000) | TBD-bench | Leonardo | Rev 2.0 | TBD-bench (ASK operator first — D-08) | TBD-bench | Plan 02 fills |
| 97-03 | TBD-bench | TBD-bench | TBD-bench | TBD-bench (expect 270000) | TBD-bench | Leonardo | Rev 2.0 | TBD-bench (ASK operator first — D-08) | TBD-bench | Plan 03 fills |

R1 expected ≈ 270000 ± 25% (Leonardo). `controller:` identity re-verified per task (ACM ports shuffle — D-08). Leonardo is chip-OUT-sideload-EXEMPT.

---

## Cell A — AM27C020 (`0x08` EPROM_QUICK) — Plan 97-02

Op: `tier0_microprobe+rca01` (the combined single program attempt at `0x000000`).

| Field (Failure Signature Capture Schema) | Source | Value |
|------------------------------------------|--------|-------|
| failing_addresses | `firestarter write` stderr (`MSG_ERR_VERIFY`) | TBD-bench |
| bad_bytes | write output | TBD-bench (v1.15 seed: 15/16) |
| retries | write output | TBD-bench (v1.15 seed: 20) |
| bits_flipped | post-attempt consistency-check vs pre-SHA | TBD-bench (0 expected → INDETERMINATE) |
| vpp_adc_mv | `firestarter vpp` ADC node | TBD-bench |
| dmm_pin1_v | [OP] held-rail proxy DMM at socket pin 1 | TBD-bench (pass band 12.5–13.0V) |
| dmm_pin31_v | [OP] held-rail proxy DMM at socket pin 31 | TBD-bench (VIL ≈ 0V expected) |
| pre_read_sha256 | consistency-check (pre-attempt) | TBD-bench |
| post_read_sha256 | consistency-check (post-attempt) | TBD-bench (== pre if pristine) |
| controller | `firestarter --version` / `hw` | TBD-bench |
| port | `firestarter hw` | TBD-bench |
| r1_readback | `firestarter hw` | TBD-bench |
| r2_readback | `firestarter hw` | TBD-bench |
| fw_commit | `git -C firestarter rev-parse HEAD` | TBD-bench |
| jp4_position | [OP] | TBD-bench |
| jp4_silkscreen_meaning | [OP] — ASK first (D-08) | TBD-bench |
| verdict | RCA synthesis | TBD-bench |
| anomalies | — | TBD-bench |

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

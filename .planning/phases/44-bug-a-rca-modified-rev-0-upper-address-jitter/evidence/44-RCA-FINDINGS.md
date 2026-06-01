---
artifact: 44-RCA-FINDINGS
phase: 44-bug-a-rca-modified-rev-0-upper-address-jitter
milestone: v1.9 — Read-Bug RCA + Fix
requirements: [RCA-01, RCA-03]
status: RCA achieved (premise corrected)
recorded: 2026-06-01
operator_witnessed: true
---

# Bug A — Root-Cause Findings (re-grounded 2026-06-01)

> **Premise correction.** Phase 44 was titled *"Modified Rev 0 upper-address
> jitter"* on the Phase 29 v2 hypothesis (A15=1 → ~1.86× skew). The 2026-06-01
> bench session **disproved the upper-address framing** and replaced it with a
> stronger, causally-proven mechanism. This document supersedes the original
> Plan 04/05 approach (Modified-Rev-0-on-Leonardo baseline + 2D LA sweep), which
> was built on the incorrect premise.

## RCA-01 — Bug A root cause: the Rev 0 (Modified Rev 0) shield

**Bug A is a read-path signal-integrity fault of the Rev 0 / Modified Rev 0
shield**, causally coupled to the read-strobe timing.

### Evidence 1 — fault isolated to the shield (2×2 crossover)

Two controllers × two shields, W27C512, N=5 consistency-check each:

| Controller \ Shield | Rev 2.0 | Rev 0 (Modified Rev 0) |
|---------------------|---------|------------------------|
| Leonardo | PASS (clean) | **FAIL — 426B / skew 1.07×** |
| Uno | **PASS — 1 SHA (perfect)** | FAIL — 689/568B / skew 0.27–0.93× |

- **Rev 0 shield FAILS on both controllers; Rev 2.0 shield PASSES on both.**
- A chip-swap crossover exonerated the **chips** (a chip jittering on the Rev 0
  assembly read perfectly on the Rev 2.0 assembly), and the Uno reading perfectly
  with the Rev 2.0 shield **exonerated the controller**.
- Jitter is **broad and ~uniform across the address space** (skew ≈ 0.3–1.1×),
  **NOT** A15/upper-address concentrated. The lone A15-skewed datum (2.41×) all
  session was a *marginal chip* on the Rev 2.0 board and is discounted.

Evidence dirs: `isolation-experiment-20260601/round{1,2,3}-*`, `FINDINGS.md`.

### Evidence 2 — read-strobe timing is a causal lever (knob sweep)

Leonardo + Rev 0 shield, same chip seated, no reflash (D-05), v1.9 firmware knobs:

| settling / strobe (µs) | 5-run divergence |
|------------------------|------------------|
| 0 / 0 (default 3µs) | **1.28%** |
| 50 / 25 | **8.37%** (~6.5×) |
| 100 / 50 | **8.13%** |

A **longer** /CE read-strobe makes the jitter **~6.5× worse** — proving the read
timing is causally coupled to the failure (RCA-01 causal proof). Evidence:
`isolation-experiment-20260601/knob-check-leo-rev0/KNOB-CHECK.md`.

### Mechanism

The inverted knob response (longer = worse) is consistent with **charge leakage /
weak or absent data-bus pull-downs on the Rev 0 shield**: the longer the data bus
is held during each read, the more it drifts toward its float state, multiplying
read errors. This matches the static-check candidate hypotheses (weak D0–D7
pull-downs / missing termination) — which were **not** quantified this session
(operator did not capture the multimeter readings; see
`rev2.0-misattributed-20260601/static-check-notes.md`).

### Fix direction (hands off to Phase 46)

**Shorter read strobe**, not longer. The firmware default is 3µs; the actionable
test is strobe ∈ {1, 2}µs to drive jitter below the 1.28% baseline. A firmware knob
can only *compensate* a hardware fault; the true fix is shield rework (data-bus
pull-downs / termination). Note: a knob fix would be **Rev-0-class-shield-scoped**,
since the Rev 2.0 shield reads clean and needs no compensation.

## RCA-03 (partial) — per-rev failure-mode map (started)

| Shield | Read behavior (this session) | Classification |
|--------|------------------------------|----------------|
| **Rev 0 / Modified Rev 0** | broad, uniform read jitter; knob-coupled (longer strobe worse) | **Bug A = read-path signal integrity (charge-leakage / weak pulldown)** |
| **Rev 2.0** | **reads clean** on both controllers (PASS) | **Bug B is NOT a read-consistency fault** — likely write/voltage path (see below) |
| **Rev 2.2** | not tested this session | placeholder (D-10) |

## Adjacent findings (not Bug A)

- **VPP hardware is healthy** — operator meter: 12.2 V on both shields (W27C512
  target 12.0 V). The Uno previously *displayed* 1.7 V due to a miscalibrated
  `R1=1000` (should be 270000); corrected to 270000 → now reads 12.1 V. The
  Leonardo reads +0.7 V high (calibration/VCC-5.5 V offset). Divider *circuit* is
  fine; it was a stored-constant error.
- **Write/program stalls on BOTH controllers** at the MAIN-phase data-request
  handshake — a **separate write-path bug**, outside v1.9 read-RCA scope. See
  `WRITE-STALL.md`. Recommend a dedicated `/gsd-debug` session.

## Open / superseded

- Plan 04 (Modified-Rev-0 baseline on the Phase-29-v2 Leonardo) and Plan 05 (2D LA
  sweep on the upper-address premise) are **superseded** by this isolation-based
  RCA. The RCA *goal* (definitive signal-integrity mechanism + begin per-rev map)
  is achieved; the literal plan steps were not run as written.
- Quantitative static readings (A15 termination, D0–D7 pull-down) remain
  uncaptured — would confirm the charge-leakage mechanism; optional follow-up.
- Chip-ID `0xda01` (vs `0xda08`) stable across session chips — confirm with a
  known-good W27C512 before write-path debugging.

---
artifact: baseline-repro-notes
phase: 44-bug-a-rca-modified-rev-0-upper-address-jitter
plan: 44-04
task: 2
type: bench-evidence
status: reproduced
operator_witnessed: true
recorded: 2026-06-01
---

# N=5 Baseline Repro — Modified Rev 0 / W27C512 (D-11)

## Bench identity (D-09)

| Field | Value |
|-------|-------|
| Shield | Modified Rev 0 (operator-confirmed silkscreen) |
| Controller | leonardo, `/dev/ttyACM0` (verified via `firestarter fw`) |
| Firmware | **3.0.0b6** — the Plan 02 v1.9 build with read-timing knobs (single sideload before baseline; bumped from 3.0.0b4) |
| Chip | W27C512 (operator-attested same chip as Phase 29 v2) |
| Knobs | **default** (no `--read-settling` / `--read-strobe`) — baseline = current behaviour |
| Sideloads this plan | exactly 1 (before baseline; chip OUT during flash, re-seated after — D-05 / chip-out rule honoured) |

## ⚠ Chip-ID anomaly (new vs Phase 29 v2)

The chip reports a **stable** device ID of `0xda01`, not the expected `0xda08`
(W27C512). Stable across 4 standalone `id` reads + all 5 baseline reads — **not
jitter**. Manufacturer byte `0xda` (Winbond) is correct; the device byte is
consistently wrong: expected `0x08` = `0b1000`, read `0x01` = `0b0001` → **D0
reads high-when-should-be-low** (consistent with weak/absent data-bus pull-down →
tristate float high) and **D3 reads low-when-should-be-high**.

Baseline run was taken with `--force` (the documented Shield-3 path) per operator
decision. This ID misread is a **new finding** — Phase 29 v2 produced 15 readable
binaries from this chip, implying the ID resolved then. Interpretation: the board
state has likely **degraded in degree** (see skew below), or socket contact has
worsened. Recorded as a Bug A corroborating data point, not dismissed.

## Result — Bug A REPRODUCED

Consistency check verdict: **FAIL** (verdict_int=1) — 5 distinct SHA-256s from 5
consecutive reads of the same chip = read non-determinism = Bug A present.

### SHA-256 (full, new baseline)

| Run | SHA-256 |
|-----|---------|
| run_01 | `86afd44b02dcf6f75b52835663cbe80920d1ac46e5c3871dfbdfb11292d363b1` |
| run_02 | `464e14aec25c672fc1b6d2ab28d4609a4d547f880c6d1ea41bb2e9e6ee53ff53` |
| run_03 | `b4a5fdd080534982c3468556bc6349fa732faa94b0fc76842350a0a31f43eb69` |
| run_04 | `af3e009f10517235f4a48a0a93bcdf0e95275f24999d5e89a6bddd4814605d77` |
| run_05 | `cb4642c1c6dfa833fa96da0a8bde0a27a22e0568206f576f1895022740a6bd0f` |

### A15 upper-address skew (the Bug A fingerprint)

| Region | Divergent offsets | Rate |
|--------|-------------------|------|
| A15=0 (0x0000–0x7FFF) | 257 / 32768 | **0.784%** |
| A15=1 (0x8000–0xFFFF) | 620 / 32768 | **1.892%** |
| **Skew (A15=1 / A15=0)** | | **2.41×** |
| Total | 877 / 65536 | 1.338% |

- WORST pairwise run divergence: runs (3,4) = 445/65536 = **0.679%**.
- Byte-value drift (run_01): A15=0 half is 3.00% `0xff`; **A15=1 half is 32.76%
  `0xff`** — float-high drift concentrated in the upper-address region.

**Comparison to Phase 29 v2 documented signature** (A15=1 ~1.70%, A15=0 ~0.92%,
skew ~1.86×): the failure mode and skew **direction** reproduce cleanly; the new
skew is **stronger** (2.41× vs 1.86×) — consistent with the degraded chip-ID read.

### D-11 byte-compare vs Phase 29 v2 reference

Reference: `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-155021-v2/`

| Run | Byte diffs vs ref | % |
|-----|-------------------|---|
| run_01 | 5453 / 65536 | 8.32% |
| run_02 | 5440 / 65536 | 8.30% |
| run_03 | 5513 / 65536 | 8.41% |
| run_04 | 5477 / 65536 | 8.36% |
| run_05 | 5457 / 65536 | 8.33% |

A clean byte-match is **impossible by construction** — both the new set and the
reference set are non-deterministic (5 distinct SHAs each). The meaningful
continuity metric is **stable-offset agreement**: where the 5 new reads are
unanimous, they agree with the Phase 29 v2 reference **92.30%** (59681/64659) of
the time — i.e. same chip contents, read through a noisier board.

## Verdict

- **Bug A reproduced** — read non-determinism with the A15=1 upper-address skew
  (2.41×) present. Acceptance met via the "Phase 29 v2 signature with A15 skew
  present" branch (WORST pairwise 0.68% is just under the 1% alt-threshold; the
  A15-skew branch is the governing criterion).
- **Bench continuity confirmed in kind** (same failure mode, same skew direction,
  92.3% stable agreement), with a flagged **degradation in degree** (stronger
  skew + new stable chip-ID misread).
- **Precondition for Plan 05 met.** Chip remains seated; firmware is the v1.9
  build (3.0.0b6); the 2D causal sweep may proceed with NO re-flash / NO reseat
  (D-05). The static-check hypothesis remains UNFORMED quantitatively
  (see static-check-notes.md) — the upper-half 0xff float-high drift recorded
  here is the strongest available supporting evidence for the data-bus-float
  mechanism, and the Plan 05 sweep should be treated as exploratory→confirmatory.

## Acceptance-criteria status

- [x] 5 SHA-256 hashes recorded.
- [x] WORST divergence + A15=1 vs A15=0 jitter rates recorded.
- [x] Per-run byte-diff counts vs Phase 29 v2 reference recorded.
- [x] Bug A pattern reproduced (A15 skew present; Phase 29 v2 signature branch).
- [x] Exactly one firmware sideload (before baseline); chip seated thereafter.
- [x] No divergence-block: baseline reproduced, phase NOT blocked.
- [!] New finding: stable chip-ID misread `0xda01` (logged, forced per operator).

## Artifacts

- Binaries preserved: `evidence/baseline-run-20260601-070256/run_0[1-5].bin`
- Live run dir (submodule cwd, not committed): `firestarter_app/consistency-check-W27C512-unknown-board-2026-06-01-070256/`

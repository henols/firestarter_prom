---
plan: 44-05
phase: 44-bug-a-rca-modified-rev-0-upper-address-jitter
status: goal achieved via isolation experiment (method changed)
completed: 2026-06-01
requirements: [RCA-01, RCA-03]
---

# 44-05 Summary — Causal proof + RCA findings + per-rev map

## What the plan asked

2D (settling × strobe) causal sweep on the Modified Rev 0 board (D-04/05), show a
knob setting drives the jitter toward zero (D-06 = RCA-01 causal proof), corroborate
with an LA capture (D-08), write RCA findings, start the per-rev map (RCA-03; D-10).

## What actually happened (2026-06-01 bench session)

1. **Causal proof (D-06) — ACHIEVED, with an inverted result.** A knob check on
   Leonardo + Rev 0 shield (chip seated, no reflash — D-05 honored) showed the
   read-strobe is a **causal lever**: longer strobe → ~6.5× *worse* jitter
   (0/0 = 1.28% → 50/25 = 8.37%). Direction is inverted vs the original hypothesis
   ⇒ mechanism = charge-leakage / weak data-bus pulldown; **fix = shorter strobe.**
   Evidence: `evidence/isolation-experiment-20260601/knob-check-leo-rev0/`.
2. **Fault localization (beyond plan scope)** — a 2×2 controller×shield crossover
   proved Bug A is the **Rev 0 shield**, not the chip or controller.
3. **RCA findings (D-09) — WRITTEN:** `evidence/44-RCA-FINDINGS.md`.
4. **Per-rev map (RCA-03 / D-10) — STARTED:** Rev 0 → Bug A read jitter; Rev 2.0 →
   clean reads (Bug B is not a read fault); Rev 2.2 placeholder. In 44-RCA-FINDINGS.
5. **Full 2D grid + LA capture (D-04 full / D-08) — NOT done.** The quick knob
   check already proved causal coupling; the full 30-point grid + logic-analyzer
   alignment were not needed to establish the mechanism and were deferred.

## Outcome

The plan's **goal** — definitive signal-integrity mechanism (RCA-01 causal proof)
+ begin the per-rev failure-mode map (RCA-03 partial) — is **ACHIEVED**, via a
better-targeted isolation method than the originally-planned upper-address 2D/LA
sweep (whose premise was disproved). Full-grid + LA corroboration remain optional
follow-ups; the fix direction is handed to Phase 46.

## Self-Check: PASSED

- RCA-01 causal proof: knob causally moves jitter (committed `41fb784`).
- Shield isolation: 2×2 crossover (committed `ebd3004`).
- RCA findings + per-rev map written (`44-RCA-FINDINGS.md`).
- Honest scope: full 2D grid + LA capture deferred (not required for the mechanism).

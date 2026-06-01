---
artifact: knob-check
rig: Leonardo + Rev 0 shield (ttyACM0), fw 3.0.0b6, chip seated, no reflash (D-05)
type: bench-evidence
status: causal coupling PROVEN — longer timing = worse (fix direction is shorter)
recorded: 2026-06-01
operator_witnessed: true
---

# Read-Timing Knob Causal Check — Leonardo + Rev 0 shield

Tests whether the v1.9 `read_settling_us` / `read_strobe_us` knobs affect the
Rev 0 shield's read jitter. Same chip seated throughout, no reflash (D-05).

| settling / strobe (µs) | 5-run divergent | A15=0 / A15=1 | WORST-pair | verdict |
|------------------------|-----------------|---------------|-----------|---------|
| 0 / 0 (strobe→3µs default) | **1.28%** (840) | 1.24% / 1.33% | 0.68% | FAIL |
| 50 / 25 | **8.37%** (5485) | 8.48% / 8.26% | 4.63% | FAIL |
| 100 / 50 | **8.13%** (5325) | 7.82% / 8.43% | 4.46% | FAIL |

## Findings

1. **Causal coupling proven (RCA-01 mechanism handle).** The read-timing knob
   materially changes the jitter rate — a ~6.5× increase from the 0/0 baseline to
   50/25, plateauing at 100/50. The knob is a real lever on the failure.

2. **Direction is inverted vs the naive hypothesis.** *Longer* settling + *longer*
   /CE strobe makes reads **worse**, not better. So the mechanism is not
   "insufficient settling time" — it is consistent with **charge leakage / weak or
   absent data-bus pull-downs**: the longer the data bus is held/sampled per byte,
   the more it drifts toward its float state, multiplying read errors.

3. **Uniform across the address space** (A15=0 ≈ A15=1 at every point) — reconfirms
   this is a broad read-path signal-integrity fault, not an upper-address effect.

## Fix-candidate direction (next test)

The data says the fix is a **shorter** read window, not longer. The firmware
default strobe is 3µs (knob=0). Test the sub-default band:
- settling 0, strobe ∈ {1, 2} µs → does jitter drop below the 1.28% baseline?
If a shorter strobe drives the jitter toward zero, that is the RCA-01 causal proof
in the actionable direction and a concrete Phase 46 fix candidate (cap/shorten the
read strobe on Rev-0-class shields).

## Caveat

The Rev 0 shield is a known-faulty board; a firmware timing knob can only
*compensate* signal integrity, not cure a hardware fault. A shorter-strobe result
would be a mitigation, with the true fix being shield rework (pull-downs /
termination — never quantified; static readings were not captured this session).

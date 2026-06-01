---
artifact: isolation-experiment-findings
phase: 44 (Bug A) — cross-cuts Phase 45 (Bug B)
type: bench-evidence
status: RESOLVED — fault isolated to the Rev 0 (Modified Rev 0) shield
recorded: 2026-06-01
operator_witnessed: true
---

# Chip-vs-Board Isolation Experiment — 2026-06-01

## ★ VERDICT (full 2×2 complete): the Rev 0 shield is the faulty component

| Controller \ Shield | **Rev 2.0** | **Rev 0 (Modified Rev 0)** |
|---------------------|-------------|----------------------------|
| **Leonardo** (ttyACM0) | PASS — clean | **FAIL — 426B, skew 1.07× (uniform)** |
| **Uno** (ttyACM1) | **PASS — perfect, 1 SHA** | FAIL — 689/568B, skew 0.27–0.93× (uniform) |

- **Rev 0 shield FAILS on BOTH controllers; Rev 2.0 shield PASSES on BOTH.**
- The jitter **follows the Rev 0 shield**, independent of controller and chip.
- **Controller exonerated:** the Uno reads *perfectly* with the Rev 2.0 shield
  (1 SHA) — its prior instability reputation did NOT manifest here.
- **Chip exonerated** (crossover, below): good chips read clean on any Rev 2.0
  assembly and jitter on any Rev 0 assembly.
- **Failure mode is BROAD/UNIFORM read jitter** across the whole address space
  (every Rev 0 measurement: skew ≈ 0.3–1.1×) — **NOT** the "upper-address (A15)
  jitter" in the Phase 44 title. The only A15-skewed datum all session was a
  marginal chip on the Rev 2.0 board (see Secondary observation) and is discounted.

**Answer to "is the shield bad?": YES — the Rev 0 / Modified Rev 0 shield induces
read-path jitter on any controller.** Mechanism is shield-level signal integrity
(consistent with the weak-data-bus-pulldown / missing-termination candidates from
the static check, which were never quantified — see `../rev2.0-misattributed-20260601/`).

---

## Detail — chip-vs-board crossover (rounds 1–2)

## Goal

Operator question: "is it the shield that's bad?" Separate the read-jitter cause
into chip vs board-assembly (and, if possible, shield vs controller).

## Rig (firmware-verified, ports re-checked each round)

| Assembly | Port | Controller | Shield | Firmware |
|----------|------|-----------|--------|----------|
| **A** | ttyACM0 | leonardo | Rev 2.0 (detect Rev 2.0-class) | 3.0.0b6 (v1.9+knobs) |
| **B** | ttyACM1 | uno | Rev 0 (EEPROM override Rev 2.3 → Modified Rev 0 config) | 3.0.0b5 |

All reads: `dev consistency-check W27C512 --runs 5 --force`, default knobs.

## Controlled crossover (the clean experiment)

Two chips, swapped between the two assemblies:

| | Assembly A (Leo + Rev 2.0) | Assembly B (Uno + Rev 0) |
|---|---|---|
| **Round 1** | Chip-B → 19/65536 (0.03%), near-blank | Chip-D → 689/65536 (1.05%) **FAIL** |
| **Round 2 (swap)** | Chip-D → **PASS, 1 distinct SHA (perfect)** | Chip-B → 568/65536 (0.87%) **FAIL** |

### Verdict: jitter follows the BOARD ASSEMBLY, not the chip

- **Chip-D**: jittered 1.05% on Assembly B, then read **perfectly** (1 SHA, PASS)
  on Assembly A. The chip is good; B corrupted it.
- **Chip-B**: clean (0.03%) on Assembly A, then jittered 0.87% on Assembly B.
- **Both chips are good on Assembly A and bad on Assembly B.** The fault is in
  **Assembly B (Uno + Rev 0)** — it corrupts every chip placed in it. Assembly A
  (Leonardo + Rev 2.0) reads good chips cleanly.

### Jitter character on Assembly B

- Uno+Rev0 + Chip-B jitter is **uniform across address space** (A15=0 0.897% vs
  A15=1 0.836%, skew 0.93×) — a **broad read instability**, NOT an upper-address
  (A15) phenomenon. Chip-B is ~90% 0xff in both halves yet still jitters ~0.87%.

## Shield-vs-controller — RESOLVED by round 3 (shield swap)

The rounds 1–2 confound (B differs in both controller and shield) was resolved by
the round-3 shield swap: **Leonardo + Rev 0 → FAIL (426B)**, **Uno + Rev 2.0 →
PASS (1 SHA)**. The Rev 0 shield jitters on the Leonardo too, and the Uno reads
perfectly with the Rev 2.0 shield → **the Rev 0 shield is the fault; controller is
exonerated.** (The prior Uno/uno328pb instability reputation did not manifest with
a good shield.) See the VERDICT table at the top.

## Secondary observation (treat cautiously)

The earliest read of this session — a third chip ("Chip-A") on Assembly A
(Leonardo + Rev 2.0) — showed 404/65536 (0.6%) divergence with a 2.41× A15 upper
skew (the run misattributed to Modified Rev 0, now relocated to
`../rev2.0-misattributed-20260601/`). Since Assembly A reads Chips B and D cleanly,
that jitter is most plausibly a **marginal Chip-A**, not the board. The "2.41× A15
upper-address skew" should therefore NOT be carried forward as an Assembly-A board
property without re-test.

## Implications for the milestone

- **Phase 44 (Bug A = "Modified Rev 0 upper-address jitter"):** the upper-address
  framing is not supported by this rig — the only A15-skewed datum came from a
  marginal chip on the *Rev 2.0* board, and the actual Rev-0-shield assembly jitters
  broadly/uniformly. The Bug A hypothesis needs re-grounding once shield-vs-controller
  is resolved. **Plan 04 remains incomplete** (still no clean Modified-Rev-0-on-the-
  Phase-29-v2-Leonardo measurement).
- **Phase 45 (Bug B = Rev 2.0):** Assembly A (Leonardo + Rev 2.0) read good chips
  cleanly here — no Bug B timing/voltage failure reproduced in this read-only test
  (Bug B is a /CE-or-/OE + VPP=13.1V phenomenon that may need a different probe).

## Binaries

- `round1-leo-rev2.0/` (Chip-B, clean), `round1-uno-rev0/` (Chip-D, FAIL)
- `round2-leo-rev2.0-chipD/` (Chip-D, PASS), `round2-uno-rev0-chipB/` (Chip-B, FAIL)
- `round3-leo-rev0/` (Rev 0 shield on Leonardo, FAIL 426B), `round3-uno-rev2.0/` (Rev 2.0 shield on Uno, PASS)

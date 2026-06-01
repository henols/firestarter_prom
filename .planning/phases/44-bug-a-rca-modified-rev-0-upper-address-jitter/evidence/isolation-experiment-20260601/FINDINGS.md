---
artifact: isolation-experiment-findings
phase: 44 (Bug A) — cross-cuts Phase 45 (Bug B)
type: bench-evidence
status: decisive-on-chip-vs-board; shield-vs-controller still confounded
recorded: 2026-06-01
operator_witnessed: true
---

# Chip-vs-Board Isolation Experiment — 2026-06-01

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

## ⚠ Remaining confound: shield (Rev 0) vs controller (Uno)

Assembly B differs from A in **both** controller (Uno vs Leonardo) **and** shield
(Rev 0 vs Rev 2.0). This experiment proves the fault is in the B *assembly* but
**cannot yet attribute it to the Rev 0 shield specifically**. The Uno controller is
a strong independent suspect: prior bench history records the operator's Uno/uno328pb
as pre-existingly unstable on W27C512 reads (timeouts + 0xff drift), distinct from any
shield (memory `project_uno328pb_bench_instability_27_04` /
`project_uno328pb_correction`).

**To disambiguate → shield swap:** mount the Rev 0 shield on the Leonardo (or the
Rev 2.0 shield on the Uno) and re-read.
- Rev 0 shield jitters on the Leonardo → **shield** is bad.
- Rev 0 shield clean on the Leonardo → **controller (Uno)** is bad.

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

- `round1-leo-rev2.0/` (Chip-B), `round1-uno-rev0/` (Chip-D)
- `round2-leo-rev2.0-chipD/` (Chip-D, PASS), `round2-uno-rev0-chipB/` (Chip-B)

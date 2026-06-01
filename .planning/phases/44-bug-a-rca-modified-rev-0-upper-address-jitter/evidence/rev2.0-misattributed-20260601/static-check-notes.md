---
artifact: static-check-notes
phase: 44-bug-a-rca-modified-rev-0-upper-address-jitter
plan: 44-04
task: 1
type: bench-evidence
status: partial
operator_witnessed: true
recorded: 2026-06-01
---

# Static Circuit Inspection — Modified Rev 0 (D-01 / D-02)

## Board identity (D-09)

- **Silkscreen revision:** Modified Rev 0 — **operator-confirmed** ("rev 0").
  Recorded as Modified Rev 0 because the EEPROM `hw_revision` byte cannot
  distinguish the operator's three shields (Rev 2.2 / Rev 2.0 / Modified Rev 0);
  silkscreen is the only authoritative discriminator.
- **Port / controller identity:** not captured this session — no serial device
  visible to the devcontainer at inspection time (`/dev/ttyACM*` / `ttyUSB*`
  empty). To be re-verified at the start of the N=5 baseline (Task 2 / D-09).

## Measurements

> **Honest record:** the operator confirmed the inspection was performed and the
> board is Modified Rev 0, but did **not** dictate quantitative meter readings for
> this session. The values below are therefore **NOT CAPTURED** — they are left
> blank rather than fabricated, to keep the RCA evidence-grade.

| # | Measurement (chip OUT unless noted) | Expected / diagnostic meaning | Reading |
|---|--------------------------------------|-------------------------------|---------|
| a | A15 series resistance, RURP driver → A15 chip pin | ~33–100 Ω = clean; ~0 Ω / open = missing termination → ringing latched by /CE | **not captured** |
| b | D0–D7 pull-down to GND (per pin) | strong (low kΩ) vs weak/high-R/absent → tristate float reads high (63% bit-raise) | **not captured** |
| c | Rework inventory — cuts & jumpers vs upstream Rev 0 schematic | document each visible modification | **not captured** (operator noted item reviewed; no description dictated) |
| d | VPP at chip pin during a read (chip seated, powered) | ~0 V during read | **not captured** (board not connected this session) |
| e | VCC rail sag during rapid A15-toggling reads | note any droop | **not captured** (board not connected this session) |

## Pre-sweep hypothesis (D-01 / D-02)

**Status: UNFORMED by direct measurement this session.**

The static inspection did not yield the quantitative DC evidence (A15 series
termination, data-bus pull-down strength) required to sharpen the prior Phase 29 v2
characterization into a single named signal-integrity mechanism. The two candidate
mechanisms remain **untested** at the static level:

1. **Missing A15 series termination → ringing latched by /CE** — would be supported
   by a ~0 Ω / open reading at (a).
2. **Weak/absent data-bus pull-downs → tristate float reads high** — would be
   supported by weak/high-R readings at (b); this is the sub-hypothesis that could
   short-circuit the sweep (44-CONTEXT `<specifics>`).

**Consequence for Plan 05:** because the static check did not down-select to one
mechanism, the 2D (settling × strobe) sweep will be **exploratory rather than
confirmatory**. If a knob setting drives the A15=1 jitter toward zero, that is still
RCA-01 causal proof; but the static layer did not pre-commit to which mechanism the
knob is compensating for. Recommend the operator capture (a) and (b) before or
during the Plan 05 bench session if an evidence-grade mechanism attribution is
desired.

## Acceptance-criteria status

- [~] static-check-notes.md exists — **yes**, but records no quantitative readings.
- [ ] A15 series-termination measurement — **not captured**.
- [ ] data-bus pull-down measurements — **not captured**.
- [ ] VPP-at-pin — **not captured** (board not connected).
- [ ] VCC-sag observation — **not captured** (board not connected).
- [ ] ONE specific named hypothesis — **UNFORMED** (two candidates remain untested).
- [x] Operator confirmed bench board is Modified Rev 0 (silkscreen).
- [ ] Port controller identity recorded — deferred to Task 2.

**Net:** D-09 board-identity gate **met**; D-01/D-02 evidence-grade
static hypothesis **NOT met** (carried as a flagged gap).

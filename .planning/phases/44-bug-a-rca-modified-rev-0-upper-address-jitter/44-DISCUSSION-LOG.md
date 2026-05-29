# Phase 44: Bug A RCA — Modified Rev 0 Upper-Address Jitter - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-29
**Phase:** 44-bug-a-rca-modified-rev-0-upper-address-jitter
**Areas discussed:** Primary evidence path, Lead hypothesis first, Rev 2.2 coverage now

---

## Primary evidence path

### Bench instrumentation available

**User's choice:** Free-text — "I have some simple scope, 8 channel logic analyser and multimeter."
**Notes:** No high-bandwidth analog scope. LA (8 ch) becomes the strongest witness tool — can capture A15/A14/A13 + read strobe + data lines simultaneously. Reframed the evidence path around this toolkit.

### Primary proof that closes RCA-01

| Option | Description | Selected |
|--------|-------------|----------|
| Firmware sweep = causal lead | Manipulate timing knob, show jitter rate moves; LA/scope corroborate | ✓ |
| LA capture = mechanism lead | Operator LA capture headline; sweep confirms | |
| Both co-lead | Sweep + LA must agree | |
| Static circuit lead | Multimeter + schematic finds root cause first | |

**User's choice:** Firmware sweep = causal lead.

### What the sweep varies + how it's set

| Option | Description | Selected |
|--------|-------------|----------|
| Host-tunable settling delay | Address-settling knob, host-set, no re-flash | |
| Host-tunable strobe width | /OE-or-/CE pulse width knob, host-set | |
| Both knobs, host-tunable | 2D sweep of settling + strobe, host-set | ✓ |
| Re-flash per setting | Hardcode + re-sideload per point (chip out each time) | |

**User's choice:** Both knobs, host-tunable.
**Notes:** Chip stays seated; sweep from host avoids reseat variance + chip-out-before-sideload churn.

### Bar for "Bug A PROVEN" (RCA-01 closure)

| Option | Description | Selected |
|--------|-------------|----------|
| Causal + localized + witnessed | Sweep moves jitter + localized to A15 + LA/scope shot | |
| Causal + localized | Sweep moves jitter + localized to upper address | |
| Causal only | A knob that drives jitter to ~zero suffices | ✓ |
| Find a single named cause | Name one mechanism, rule out the rest | |

**User's choice:** Causal only.
**Notes:** Pragmatic — a controllable cause is an actionable Phase 46 fix target. Recorded as governing over the ROADMAP criterion-1 "name the specific cause" wording (D-07) so the verifier does not over-block.

---

## Lead hypothesis first

### Which hypothesis families in scope

| Option | Description | Selected |
|--------|-------------|----------|
| Both: timing + data pull-down | Sweep timing AND probe weak-data-bus-pull-down theory | |
| Timing-first, pull-down if needed | Sweep first; chase pull-down only if timing can't zero jitter | |
| Address-timing only | Strictly address settling/strobe; defer data-bus theory | |
| Static circuit first | Multimeter + v1.7 schematic on Modified Rev 0 mods BEFORE the sweep | ✓ |

**User's choice:** Static circuit first.
**Notes:** The Modified Rev 0 board is hand-modified — the mods are the prime suspect. Static inspection forms a specific hypothesis; the sweep then confirms causally. Data-bus-pull-down sub-hypothesis folded into the static multimeter pass rather than a separate dynamic track.

### Documentation of the Modified Rev 0 mods

| Option | Description | Selected |
|--------|-------------|----------|
| Documented in v1.7 docs | Mods recorded in v1.7 shield-revisions docs | ✓ |
| I'll describe them at the bench | Operator narrates mods live | |
| Unknown — reverse-engineer | Reverse-engineer from continuity/visual | |
| Stock Rev 0 schematic only | Compare board against stock to find deltas | |

**User's choice:** Documented in v1.7 docs.
**Notes:** Discovered during scout that those docs are NOT on the current checkout (meta `v1.7-SHIELD-REVS.md` commits unmerged; firestarter submodule at `efd203a` predates `doc/SHIELD-REVISIONS.md` on `beta`@`59a5e58`). Recorded as a flagged prerequisite — v1.9 branch must fork off beta.

---

## Rev 2.2 coverage now

| Option | Description | Selected |
|--------|-------------|----------|
| Swap & run consistency-check | Real Rev 2.2 read run this phase | |
| Static check only on Rev 2.2 | Multimeter/schematic predict, no read run | |
| Defer Rev 2.2 to Phase 45 | Record "untested, predicted clean"; test in P45 | ✓ |
| Map from existing evidence | Fill entry from v1.7 data, zero bench work | |

**User's choice:** Defer Rev 2.2 to Phase 45.
**Notes:** Keeps Phase 44 focused on Modified Rev 0; Rev 2.2 tested for real in Phase 45 when that shield is on the bench for the full per-rev map.

---

## Claude's Discretion

- **Baseline-repro rigor** — defaulted to N=5 on the same Leonardo/chip/port + byte-compare vs the 15 captured binaries (D-11); operator may raise N.
- **Where RCA evidence/docs are written** (meta vs sub-repo) and **dev-command vs build-flag** for the knobs — left to planning, subject to the chip-seated/host-tunable constraint.

## Deferred Ideas

- Rev 2.2 physical bench test → Phase 45 (per-rev map completion).
- Naming the single dominant mechanism + ruling out alternatives → stretch goal beyond the causal-only bar.
- **Prerequisite (not deferral):** fork v1.9 firmware branch off `beta` so v1.7 shield docs + firmware substrate are present.

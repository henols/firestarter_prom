---
title: 27C programming-algorithm fidelity via a per-protocol parameter table
trigger_condition: a firmware-correctness/reliability milestone is prioritized, OR a 27C part programs unreliably and RCA points at pulse behavior, OR the primitives layer is being reworked anyway
planted_date: 2026-07-02
status: dormant
---

# 27C programming-algorithm fidelity via a per-protocol parameter table

Make the 27Cxxx write algorithm datasheet-conformant by driving the *shared*
program→verify loop from a small `const` parameter table keyed by `protocol_id`,
instead of hardcoded `switch` defaults + a flat retry cap. The "regular / fast /
legacy" split described in the datasheets collapses to **rows in a table**, not
separate implementations — the loop skeleton and the v1.16 primitives already
generalize.

## Why (payoff)

- **Correctness:** current pulse behavior diverges from *every* 27C datasheet
  (Intel Quick-Pulse, AMD Flashrite, ST PRESTO II/IIB, Microchip SNAP!, legacy
  NMOS). We program, but not the way silicon vendors specify.
- **High reuse, low cost:** ~80–85% of the work is already the shared routine.
  The fix is a parameter row + a loop tweak, not new algorithm code.
- **Extensible:** future parts (or per-family over-program rules) become a new
  table row, not a new code path.

## The gap (datasheet vs. firmware today)

All three 27C `protocol_id`s (0x07/0x08/0x0B) already share ONE routine
`eprom_write_execute`; they differ only by a hardcoded pulse default and a
VPP-path branch. The divergences from datasheet-correct behavior:

1. **Escalating pulse width, not fixed 100µs.** Firmware grows the pulse each
   retry (`pulse_delay = org + org*retries/20`, `eprom.cpp:177`). Quick-Pulse /
   Flashrite / PRESTO hold a **fixed 100µs** pulse and *count* pulses. Backwards.
2. **Flat retry cap of 20** for all parts (`NUMBER_OF_RETRIES`, `eprom.cpp:20`).
   Datasheets want **10** (Microchip) or **25** (Intel/AMD), failing hard at cap.
3. **No over-program / margin pulse.** Correct for PRESTO & Quick-Pulse; wrong
   for older Intel "Intelligent" 27C parts that apply **3× the pulses used**.
4. **Legacy NMOS parts** (mapped to 0x0B) get a 500µs adaptive pulse, not the
   fixed **50ms** single pulse those parts specify.
5. **VCC never raised to 6.25V.** All four vendor algorithms assume ~6.25V
   program-VCC for threshold margin. The shield has **no VCC-raise path** →
   *hardware-bound*, NOT closable in firmware (see ceiling below).

## Shape (rough)

- **Firmware:** replace the hardcoded pulse `switch` (`eprom.cpp:70-76`) + flat
  `NUMBER_OF_RETRIES` with a `const` table keyed by `protocol_id` carrying:
  `pulse_width`, `max_pulses`, `overprogram_factor` (0 | 3×), `verify_mode`,
  `vpp_path` (drop-resistor vs direct). Change the loop to hold a fixed pulse and
  count, and apply the over-program pulse when `overprogram_factor > 0`. Keep the
  `program_mismatched_bytes` / `verify_and_update_mask` loop and the handle
  function-pointer primitives verbatim.
- **Reuse split:**

  | Varies per protocol (~15–20%) | Shared (~80–85%) |
  |---|---|
  | pulse_width, max_pulses, overprogram_rule, vpp_path, vpp_mv | program→verify loop, mismatch-mask, bus I/O primitives, address/control routing |

## Hardware ceiling (state plainly)

Firmware fidelity buys *timing / pulse-count / verify* correctness but **not**
full silicon-margin fidelity, because 6.25V program-VCC is unreachable on the
current shield. This is best-effort — the same shape as prior D-07 hardware-bound
graduations. Don't let the VCC gap block the (real, achievable) timing fixes.

## Cost / risk

- Program-timing change → any golden traces / bench-verified write results that
  encode the current pulse cadence will legitimately shift; re-baseline needed.
- Behavior-preserving-*ish* but not byte-identical: this changes *how* bytes get
  programmed. Needs on-bench re-verification per family (Leonardo + on-hand 27C
  parts), not just native tests.
- Over-program (3×) path is only correct for specific Intel-Intelligent parts —
  don't apply it blanket. Gated by the research question below.

## Next steps when triggered

1. Resolve the research question (`questions.md`): confirm exact max-pulse counts
   per part and which on-hand parts (if any) actually need the 3× over-program.
2. Draft the parameter table with datasheet-verified rows for the on-hand 27C set.
3. Rework the loop to fixed-pulse-and-count; wire the table in; drop the escalate.
4. Re-baseline golden traces; on-bench re-verify each affected family on Leonardo.
5. Document the 6.25V-VCC ceiling as accepted hardware debt.

## Related

- Research: `research/questions.md` — "27C programming-algorithm fidelity"
- Prior art: v1.16 primitives (P7/P4/P3/P5) — the loop/primitive layer this rides on
- Code: `eprom_write_execute` + program loop (`firestarter/src/proms/eprom.cpp:70-76,114-193`),
  `NUMBER_OF_RETRIES` (`firestarter/src/proms/eprom.cpp:20`),
  pulse escalation (`firestarter/src/proms/eprom.cpp:177`),
  handle primitives (`firestarter/src/proms/memory.cpp:61`)
- Datasheets: ST M27C512 PRESTO IIB (farnell 1581208), AMD Am27C010 Flashrite,
  Intel 27C010 Quick-Pulse, Microchip 27C256 DS11001N

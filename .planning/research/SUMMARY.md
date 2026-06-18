# Project Research Summary — v1.14 Feasible-Gap Implementation

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Domain:** EPROM/Flash/EEPROM programmer — chip graduation milestone (4 chip groups → `supported`) on an Arduino RURP shield (Python CLI host + Arduino C++ firmware, dual-repo lockstep)
**Researched:** 2026-06-18
**Confidence:** HIGH (all four dimensions converged; grounded in live source, v1.13 artifacts, and hardware datasheets/product specs — no contradictions)

## Executive Summary

**v1.14 is the first milestone since v1.0 where chips actually graduate to `supported`** — the four gaps v1.13 surfaced as feasible-but-deferred become fully programmable. The research converged on one structural insight: **three of four gaps are HOST-ONLY with zero firmware flash cost** (999.4 erase-wiring, 999.7 25V ceiling, 999.6 adapter graduation); only **999.5 (X88C64 0x34 handler)** adds firmware code.

The **dominant cross-cutting risk is host-guard-removal timing.** The `chip_resolver.resolve_chip` `ChipNotImplementedError` refusal installed in v1.12 is the authoritative hardware-damage prevention layer — it refuses every non-`supported` chip before any serial byte. Each of the four features *removes* that barrier for a chip family, re-opening the wrong-VPP-to-wrong-pin damage path. The safety invariant: **the graduation step (flip `support_status` → `supported` + drop the host guard) must be the FINAL plan in each phase, gated behind complete validation** (native recording-stub register tests + wire round-trip + Leonardo bench with a chip-OUT VPP multimeter dry-run first).

Two hard open questions gate feasibility and must be the **first plan** of their respective phases (not handler/constant code):
1. **X88C64 ALE routing** (999.5) — is a free `CTRL_*` bit available in `rurp_pinout.h` to toggle the 8051 Address-Latch-Enable without a PCB modification? Labeled LOW-confidence (Assumption A6 in `X88C64-FEASIBILITY.md`). If no free bit exists, the handler cannot ship and X88C64 defers again.
2. **25V VPP capability** (999.7) — can the on-bench shield physically + safely produce ≥25V at the socket VPP pin? Resolved via operator multimeter, chip-OUT dry-run (`autonomous: false`), before the ceiling constant changes.

25V is **rated-feasible** (RURP Rev 2.3 spec = 5–27V VPP; AP3012 boost regulator = 4.5–36V), so the `RURP_VPP_CEILING_MV = 22000` is a conservative software constant, not a hard hardware wall — but the dry-run is still mandatory because it depends on the specific shield's R1/R2 calibration.

**Flash budget** is the constraint for 999.5 only: Leonardo sits at **89.5% / ~3 KB free** post-v1.13. The X88C64 multiplexed-bus handler is the heaviest addition (~1–3 KB) and must be measured (`pio run -e leonardo`) as an explicit gate. This drives a build-order tension (below).

## Key Findings

### Recommended Stack

No new third-party dependencies. All work lands in existing files with existing toolchains. See `STACK.md`.

| Gap | Firmware? | Primary surgery | Flash cost |
|-----|-----------|-----------------|-----------|
| **999.4** erase write-path | No | `database.py::convert_to_programmer` — wire `FLAG_CAN_ERASE` from `electrical.type=="EEPROM"` (not `info-flags & 0x10`); firmware guard `eprom_write_init` already correct | 0 |
| **999.5** X88C64 0x34 | **Yes** | New `configure_x88c64` (+ `eeprom_x88c64.cpp`/header) registered in `memory.cpp` dispatch **before** the `protocol != 0 → configure_not_implemented` guard; possible `rurp_pinout.h` + lockstep `constants.py`/`firestarter.h` ALE bit; `build_db.py` reclassification | ~1–3 KB (measure) |
| **999.7** 25V NMOS | No | `RURP_VPP_CEILING_MV` 22000→25000 (`build_db.py`) + `_FAMILY_VPP_INVARIANTS` ceiling (`check_dispatch.py`); 4 chips reclassify off `vpp-exceeds-max` | 0 |
| **999.6** AT28C04/16 adapter | No | Remove `_AT28C_DIP24_NAMES` rule arm (`build_db.py`) + host-guard refusal (`chip_resolver.py`); existing `configure_eeprom28c` (0x0D, VPP-free) handler | 0 |

### Feature Landscape

- **Table stakes per gap = "the chip writes + verifies correctly and reports `supported`."** Observable acceptance: N≥5 write→read-back SHA matches on Leonardo + a non-vacuous negative control (wrong-file verify exits non-zero).
- **999.4** graduates 7–8 EE-EPROMs (W27C512/W27E512/W27C257/W27E257/SST27SF256/SST27SF512/SST27VF256/SST27VF512) to auto-erase-before-write.
- **999.5** graduates X88C64P only. **Anti-feature: STORE/RECALL is explicitly OUT** (that's the X2210/X2212 NovRAM family — different product).
- **999.7** graduates 4 NMOS UV-EPROMs (INTEL M2716/M2732, SGS-THOMSON ETC2716, ST M2716). M2732A (21V) is already `supported`. **Anti-feature: >25V chips stay fail-closed.**
- **999.6** graduates 9 AT28C04/AT28C16 DIP24 EEPROMs. Before the physical adapter exists, the graceful behavior is the existing honest-refusal (`adapter-required`); after, full programmability.

### Architecture & Integration

- **Dispatch arm order is load-bearing:** any new 999.5 `memory.cpp` arm must insert BEFORE the generic `if (protocol != 0) → configure_not_implemented()` guard — after it, the arm is dead code.
- **Only 999.5 requires a dual-repo lockstep phase**; 999.4/999.6/999.7 are host-only phases with bench-verification steps.
- **refused → supported end-to-end** for each graduation: DB reclassification → host-guard refusal removed → wire → (firmware, 999.5 only) → Leonardo bench proof.

## Roadmap Implications

**Suggested phase structure (Phase 77 onward — numbering continues from v1.13's Phase 76):**

| Order | Backlog | Phase | Gate / first-plan |
|-------|---------|-------|-------------------|
| 1 | 999.4 | Erase write-path (host-only, most-ready) | 14V erase-rail chip-OUT VPP dry-run before seated erase |
| 2 | 999.5 | X88C64 0x34 handler (firmware) | **ALE-routing investigation = Plan 1**, before any handler code; `pio run -e leonardo` flash gate ≤~90% |
| 3 | 999.7 | 25V NMOS ceiling raise (host-only) | **Operator multimeter ≥25V chip-OUT dry-run = Plan 1 (`autonomous: false`)**, before constant change |
| 4 | 999.6 | AT28C04/16 adapter graduation (host-only) | Physical DIP24→DIP32 adapter built + DMM /WE-reroute continuity check before any chip insertion |

**Build-order tension for the roadmapper to resolve:** PROJECT.md / operator-captured order is **999.4 → 999.5 → 999.7 → 999.6**. The PITFALLS researcher recommends swapping to **999.4 → 999.7 → 999.5 → 999.6** to land the zero-flash 25V change before the flash-consuming X88C64 handler, preserving headroom. Both are defensible; the captured order has operator backing. Flag for an explicit decision.

**Per-phase shape:** the graduation gate (flip + guard-removal) is always the final plan, never mid-phase. 999.5 wants a dedicated ALE investigation sub-plan; 999.7 wants an `autonomous: false` VPP-measurement first plan; 999.6 gates on adapter-ready (defer cleanly without impacting the others if the adapter isn't built).

## Watch Out For (top pitfalls)

1. **Host-guard removal before bench evidence** — re-opens the live 12V/25V-to-wrong-pin damage path. Graduation gate last, behind Tier-1/2/3.
2. **25V assumed, not measured** — the ceiling reflects a physical rail limit; firmware does NO runtime VPP enforcement, it trusts host pre-screening entirely. Multimeter dry-run is non-negotiable.
3. **Flash overrun on 999.5** — ~3 KB headroom; measure with `pio run -e leonardo`.
4. **ALE infeasibility** — if no free `CTRL_*` bit, X88C64 cannot graduate without a PCB change.
5. **Adapter mis-wire (999.6)** — VPP-free so damage is limited to non-function; the critical /WE reroute (chip pin 21 → socket pin 30) needs a DMM continuity check.
6. **Lockstep / FLAG_* constant drift** — no automated parity gate for `FLAG_*` bits; change `constants.py` + `firestarter.h` together.
7. **Bench-integrity standing rules** — Leonardo + clean shield is the only trustworthy PASS path; uno328pb is N/A for program/write; **always ASK which shield rev is on-bench** (Rev 2.2 / Rev 2.0 / Modified Rev 0 — EEPROM byte can't distinguish); verify per-port `controller:` identity at every task start; chip-OUT before sideload on Uno-class boards.
8. **Pre-req:** confirm the v1.13 `3.0.0b10` lockstep beta cut has landed in both sub-repos before branching v1.14 off `beta`.

## Confidence Assessment

| Dimension | Confidence | Basis |
|-----------|-----------|-------|
| Stack | HIGH | Live source (2026-06-18); flash via `pio run`; RURP Rev 2.3 5–27V verified from two sources |
| Features | HIGH | All four gaps defined in v1.13 artifacts with file:line origins; acceptance grounded in existing handlers + bench precedent |
| Architecture | HIGH | Dispatch + host-guard verified against live code; lockstep needs explicit from v1.10–v1.13 history |
| Pitfalls | HIGH | Grounded in v1.13 history (flash ceiling, uno328pb, Rev 0 Bug A, standing bench preconditions) |
| X88C64 ALE routing | **MEDIUM/LOW** | Assumption A6 explicitly unresolved — needs a bench schematic trace |

**Overall: HIGH** — feasibility of three gaps is settled; the two genuine unknowns (ALE bit, 25V rail) are correctly framed as bench-gated first-plan investigations, not blockers to milestone scoping.

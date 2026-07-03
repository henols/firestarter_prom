# Research Questions

Open questions to resolve via deeper investigation. Appended by `/gsd-explore` and other workflows.

## Protocol-first architecture rebuild (v1.16) — added 2026-06-25

Source: `/gsd-explore` session 2026-06-25. See `seeds/protocol-first-architecture-rebuild.md`.

1. **Shared-primitive inventory.** What are the actual common operations across the current
   firmware handlers (`configure_eprom`, `configure_sram`, `configure_flash`, flash4, …)?
   Produce a decomposition: address setup, data strobe, poll/verify, VPP gate, page buffer,
   SDP unlock, chip-id. Which are genuinely shareable vs protocol-specific?
2. **Datasheet sourcing list.** Concrete list of datasheets to download: the 11 on-hand ICs +
   one representative common chip per minipro protocol bucket without silicon. Where are the
   authoritative copies?
3. **Current per-handler flash breakdown.** Measure today's Leonardo flash usage attributed
   per handler/family, to quantify where reuse buys the most headroom against the ~90% ceiling.
4. **protocol_id → name → datasheet map.** For every `protocol_id` in `chip_database.json`,
   the proper human name and the datasheet-verified behavior (write/erase algorithm, VPP,
   pin roles). This is the vocabulary the naming pass produces.
5. **Verification ledger format.** How to represent per-protocol bench status (PASS on
   Leonardo / `UNVERIFIED` / chip-needed) so it composes with the existing v1.13 per-family
   matrix + v1.15 EVIDENCE.{md,json} rather than replacing them.

## Community chip-validation command (dev test) — added 2026-07-02

Source: `/gsd-explore` session 2026-07-02. See `seeds/community-chip-validation-command.md`
and `notes/dev-test-design-decisions.md`.

1. **Health-proving write/verify pattern.** What data pattern does the write/verify step
   use? A fixed pattern (e.g. 0x00/0xFF/0xAA) is simple but blind to stuck/shorted address
   lines — a chip can pass while mis-addressing. An **address-derived pattern** (each byte a
   function of its address) makes verify catch address-line faults directly. This ties to the
   old Bug A "upper-address jitter" history — the exact failure class an address-derived
   pattern would surface. Decide before planning; also decide the UV small-region variant.

2. **Community PASS → support_status graduation.** Does a community-submitted PASS
   automatically graduate a chip's `support_status` (spec-only → supported), or only flag it
   for maintainer confirmation? Affects trust model: auto-graduation risks a bad bench
   config promoting a chip falsely; manual keeps the maintainer authoritative but adds
   triage load. How does the structured report reconcile/diff against the current DB entry
   inside `gsd-inbox`?

## Bus-config mask-model redesign — added 2026-07-02

Source: `/gsd-explore` session 2026-07-02. See `seeds/bus-config-clean-redesign.md`
and `notes/bus-config-mask-model.md`.

1. **Is the per-byte remap actually a measurable fraction of read/write time, or
   is it serial-bound?** The "faster" motivation for the bus-config redesign is a
   suspicion, not a measurement. At 250000 baud (~25 KB/s) a 512-byte read is
   ~20 ms of pure transport; the per-byte work in `mem_util_remap_address_bus`
   (the `rw_line`/`vpp_line`/`using_p1_as_vpp` branches + the address-permutation
   loop) may be negligible against that. Profile a real read AND write on both a
   straight-mapped chip (permutation loop skipped, `address_lines[0]==0xFF`) and a
   permuted chip. Decide whether perf can drive the redesign, or whether the
   generality goal must carry it alone. If marginal, an additive `static_low` +
   configure-time mask precompute may suffice instead of a breaking redesign.

## info jumper-display / 2516-family support — added 2026-07-02

Source: `/gsd-explore` session 2026-07-02. See `notes/info-jumper-display-design-audit.md`
and `seeds/rev22-3pin-header-2516-family-support.md`.

1. **Is TMS2532 VPP 25V or 21V?** The TI 2516/2532 datasheets specify 25V ±1V,
   but one web source (forum) claimed 21V for the TMS2532. Confirm against the
   primary TMS2532 datasheet before any voltage decision. The chip_database.json
   currently lists 2532 @ 25V (algorithm 0x0B).

2. **Can Firestarter actually PROGRAM a 2516/2532 today, or only read it?** The
   2516 is modeled on the same pinout key as an ordinary Intel 2716
   (`DIP24_2716`) and shares firmware algorithm `0x0B`. But datasheets show the TI
   25xx family takes the program strobe on **pin 20 (PD/PGM)** while Intel parts
   take it on **pin 18 (CE/PGM)**. Determine what pin firmware `0x0B` actually
   asserts the write-strobe on. If it strobes pin 18, a write to a 2516/2532 would
   fail (or corrupt) despite `support_status: supported` — meaning the 3-pin
   header on Rev 2.2/2.3 is what physically reroutes the strobe to pin 20, and
   Firestarter cannot program these parts on Rev 2.0/2.1 at all. Verify on-bench
   (operator owns Rev 2.2).

## 27C programming-algorithm fidelity — added 2026-07-02

Source: `/gsd-explore` session 2026-07-02. See
`seeds/27c-algorithm-fidelity-param-table-refactor.md`. Researcher confirmed the
firmware runs an iterative program→verify loop but diverges from every 27C
datasheet (escalating pulse instead of fixed 100µs; flat retry cap of 20 vs
per-part 10/25; no over-program margin; no 6.25V VCC). These items were
`[ASSUMED]` and must be verified before drafting the parameter table:

1. **Exact max-pulse count per part.** Intel's 25-pulse cap is confirmed for
   27C010 but assumed for 27C256/512; Microchip's count (~10) is assumed. Pull
   the per-part cap from each primary datasheet so the table's `max_pulses` rows
   are verified, not inherited.

2. **Which on-hand parts (if any) need the 3× over-program margin?** Only the
   older Intel "Intelligent" 27C algorithm applies an over-program pulse of 3×
   the pulses used; Quick-Pulse / Flashrite / PRESTO do NOT. Map each on-hand 27C
   part to its algorithm variant and decide whether the `overprogram_factor`
   column is ever non-zero for real inventory, or is purely forward-looking.

3. **Is a true fixed-100µs pulse achievable given the firmware's page-write pulse
   model?** Today the "pulse" is `CTRL_VPE_ENABLE` asserted/de-asserted around a
   whole page write (`eprom.cpp:115-125`), and width comes from `pulse_delay`.
   Confirm the timing granularity actually lets us hold 100µs per unit, or whether
   the page-oriented pulse shape needs rethinking to match the byte-level
   datasheet algorithm.

4. **Legacy NMOS 50ms path.** Confirm which parts currently mapped to 0x0B are
   the fixed-50ms-single-pulse NMOS parts vs. adaptive CMOS, so the "legacy" row
   is correct and we don't force a 50ms cadence onto a CMOS part that wants 100µs.

## White-box voltage calibration (v1.25) — added 2026-07-03

Source: `/gsd-explore` session 2026-07-03. See
`seeds/voltage-reading-whitebox-calibration.md` and
`notes/voltage-cal-design-decisions.md`. Resolve before scoping/planning:

1. **Is the bandgap really the dominant term?** Measure the true bandgap
   `V_bg = VCC_dmm × bandgap_adc / 1024` on 2–3 bench boards (Uno, Leonardo,
   uno328pb) and compare each to the hardcoded 1100 mV. Confirms Stage 1 carries
   the accuracy and quantifies the per-board spread (is it really ~±10 %?).
2. **Does the Stage-2 VPP fit show a real offset, or is it pure gain?** After
   applying the calibrated `V_bg`, measure VPP at 2+ pot levels and check whether
   the residual is a clean scale factor (one trim point suffices) or has an
   intercept (need two points). Decides how many Stage-2 points the wizard asks for.
3. **`CONFIG_VERSION` migration.** How to upgrade an existing user's stored EEPROM
   config to the new layout without silently mis-scaling readings — confirm the
   new bandgap field defaults to 1100 mV (identity) on migration and that the
   version-bump path is covered by existing config tests.
4. **Confirmation-read mechanism.** What's the cleanest way for firmware to return
   one raw `(bandgap_adc, voltage_adc)` sample on demand for the wizard — extend an
   existing `dev`/config command, or add a dedicated calibration command? Must not
   drive any rail as a side effect (safety).
5. **DMM/ground-truth tolerance.** What DMM accuracy do we assume, and should the
   wizard record the meter/measurement so a later re-cal can tell instrument error
   from real drift?

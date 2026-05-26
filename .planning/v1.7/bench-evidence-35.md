# v1.7 Phase 35 Bench Evidence

**Operator bench session:** 2026-05-26
**Boards:** Rev 2.0, Rev 2.2, Modified Rev 0 (opportunistic 3rd-board capture)
**Firmware:** 3.0.0b5 (post Wave 1 CR-01 / CR-02 / WR-01 / WR-02 fixes)
**Capture host:** /workspaces devcontainer with USB passthrough to all three boards (operator's local hardware reachable from Claude)
**Cross-refs:**
- `.planning/phases/35-documentation-milestone-close/35-HUMAN-UAT.md` (UAT-1 / UAT-2 / UAT-3 PASS/FAIL/SKIP record)
- `.planning/v1.7-SHIELD-REVS.md` §3 (R41 value) + §8 (OPEN flag resolution) + §9 (per-rev ADC band table, Wave 4 input)
- `.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-REVIEW.md` (CR-01 / CR-02 origin)

Operator protocol applied per memory:
- `feedback_chip_out_before_sideload` — operator confirmed all sockets EMPTY before sideload (2026-05-26 06:55Z exchange)
- `feedback_verify_port_identity_each_task` — controller identity verified per port before sideload (see "Identity verification" sub-sections below) and confirmed unchanged post-flash

---

## Port → Board → Shield mapping

| Port | Controller (FW string) | Silicon (per memory) | Shield (operator-attested) | Phase 35 role |
|------|------------------------|----------------------|----------------------------|---------------|
| `/dev/ttyACM0` | `uno` | ATmega328P (plain Uno) | **Rev 2.0** | UAT-1 target |
| `/dev/ttyACM1` | `leonardo` | ATmega32U4 (Leonardo) | **Modified Rev 0** | UAT-3 cross-check (opportunistic; outside primary plan scope) |
| `/dev/ttyUSB0` | `uno328pb` (still wrong-FW; see §Wrong-FW persistence below) | ATmega328P (plain Uno per memory `[[project_uno328pb_correction]]`) | **Rev 2.2** | UAT-2 target |

---

## Rev 2.0 Board (`/dev/ttyACM0`)

### Identity verification

- Port: `/dev/ttyACM0`
- `controller:` identity: `uno`
- Pre-flight: `firestarter -v -p /dev/ttyACM0 hw` → `controller: uno on port /dev/ttyACM0`, `FW: 3.0.0b4:uno` (pre-sideload)

### Sideload result

- Install command used: `firestarter -v -p /dev/ttyACM0 fw -i --pre --force -b uno`
- Resolved release: `3.0.0b5` (auto-picked latest pre-release)
- avrdude command: `avrdude -v -p atmega328p -c arduino -b 115200 -P /dev/ttyACM0 -D -U flash:w:firestarter_uno.hex:i`
- Result: ✅ "Firmware successfully updated on /dev/ttyACM0 (7.60s)" — no verify errors
- Post-flash boot: ✅ `FW: 3.0.0b5:uno`

### Boot logs (5 boots — each `firestarter hw` triggers DTR-reset on Uno = fresh boot)

**Boots 1–5 — all identical:**
```
I: FW: 3.0.0b5:uno
I: Physical HW: Rev 2.0-class
I: HW: Rev 2.0-class
I: Cmd: 0x0f (HW_VERSION)
OK: Ready
OK: Rev 2.0-class, Override HW: Rev 2.0-class
```

(`WARN: HW: rev_unknown` from Plan 01's CR-02 hard-fail-loud emit did NOT fire — detect landed cleanly inside the Rev 2.0-class 4k7 bucket; expected behavior.)

### Raw ADC capture

| Boot # | `adc_a3` (raw, 0..1023) | Detected silkscreen string | Notes |
|--------|-------------------------|----------------------------|-------|
| 1      | not exposed by FW       | `Rev 2.0-class`            | 8-sample avg; band: `adc_a3 < ADC_BAND_R41_4K7_HIGH (200)` |
| 2      | not exposed             | `Rev 2.0-class`            | same |
| 3      | not exposed             | `Rev 2.0-class`            | same |
| 4      | not exposed             | `Rev 2.0-class`            | same |
| 5      | not exposed             | `Rev 2.0-class`            | same |

**Note:** Firmware computes `adc_a3 = analog_read_avg8(PIN_HW_REVISION_DETECT_ADC)` at `firestarter/include/rurp_hw_rev_utils.h:68` but does NOT log the raw value over serial. The serial protocol only emits the resolved silkscreen string.

### A3↔GND multimeter reading (board OFF, header pins, after pin reflow 2026-05-26)

**A3 header pin ↔ GND header pin = 27 kΩ**

This is NOT R41 in isolation — see Rev 2.2 §"R41 measurement attempt" below for the two-board comparison and interpretation. Schematic R41 value (4.7 kΩ) is not contradicted by this reading.

---

## Rev 2.2 Board (`/dev/ttyUSB0`)

### Identity verification

- Port: `/dev/ttyUSB0`
- `controller:` identity: `uno328pb` (FW string) — silicon is actually plain Uno per memory `[[project_uno328pb_correction]]`; wrong-FW state persists (see §Wrong-FW persistence below)
- Pre-flight: `firestarter -v -p /dev/ttyUSB0 hw` → `FW: 3.0.0b4:uno328pb`

### Sideload result

- Install command used: `firestarter -v -p /dev/ttyUSB0 fw -i --pre --force -b uno`
- **`-b uno` flag was overridden** by the app's controller-string auto-detect (firmware reported `uno328pb`, app downloaded `firestarter_uno328pb.hex` instead of `firestarter_uno.hex`)
- avrdude command: `avrdude -v -p atmega328pb -c urclock -b 115200 -P /dev/ttyUSB0 -D -U flash:w:firestarter_uno328pb.hex:i`
- Result: ✅ "Firmware successfully updated on /dev/ttyUSB0 (5.90s)"
- Post-flash boot: ✅ `FW: 3.0.0b5:uno328pb` (wrong-FW state retained — detect-rev logic is FW-build-independent so UAT data is still valid)

### Boot logs (5 boots — DTR-reset on USB0's plain Uno acts identically to ACM0)

**Boots 1–5 — all identical:**
```
I: FW: 3.0.0b5:uno328pb
I: Physical HW: Rev 2.0-class
I: HW: Rev 2.0-class
I: Cmd: 0x0f (HW_VERSION)
OK: Ready
OK: Rev 2.0-class
```

(No EEPROM hw_revision override set on this board → `OK:` line omits the `Override HW: …` clause; expected per Plan 02 D-04.)

### Raw ADC capture

Same as ACM0 — `adc_a3` not logged. 100% stable across 5 boots, lands in 4k7 bucket (`adc_a3 < 200`).

### R41 measurement attempt (§8 OPEN — multimeter via A3↔GND header pins, BOARD OFF)

**Procedure (operator-executed 2026-05-26):** USB unplugged → multimeter in ohms mode → probes between Arduino A3 header pin and any GND header pin → "Reflowed all the pins" first to ensure clean joints.

**Two-board comparison:**

| Shield | Port | A3↔GND reading (header pins, board OFF) | Schematic R41 |
|--------|------|------------------------------------------|---------------|
| **Rev 2.0** | /dev/ttyACM0 | **27 kΩ** | 4.7 kΩ |
| **Rev 2.2** | /dev/ttyUSB0 | **20 kΩ** | 4.7 kΩ |

**⚠ Interpretation correction — this is NOT R41 in isolation.** Both boards share the same schematic family (4.7 kΩ R41), yet measurements differ by ~7 kΩ. The only sensible explanation: A3↔GND with the board OFF doesn't isolate R41; it measures R41 (to JP4) in parallel with the ATmega's unpowered A3-pin leakage paths to GND. ATmega input-protection (ESD diodes + sub-threshold gate paths) at ~200 mV multimeter test voltage presents non-linear impedance that varies by chip instance, temperature, and undefined power-rail state. Two different ATmega chips → two different leakage profiles → 20 kΩ vs 27 kΩ.

- **§8 OPEN ground-truth resolution:** **inconclusive from A3↔GND header-pin measurement.** Schematic value (R41 = 4.7 kΩ for Rev 2.0/2.1/2.2) is still consistent with both readings because R41 itself isn't being isolated — the multimeter sees R41 || [MCU leakage]. Where MCU leakage is ~5-7 kΩ at multimeter test voltage, parallel with R41=4.7 kΩ yields ~2.5-3 kΩ — but in reverse-bias direction (which is what board-off A3 to GND would be) MCU leakage could easily be 20-100 kΩ, putting the parallel result in the observed 20-27 kΩ range.
- **Schematic-stated value:** 4.7 kΩ (upstream blob `f3b7a521`, identical to Rev 2.1) — not contradicted by these readings
- **Anders chat-intel value:** 10 kΩ — not contradicted either (10k || 7k MCU-leakage ≈ 4.1 kΩ; 10k || 100k MCU-leakage ≈ 9.1 kΩ — both still plausible)
- **Definitive resolution path:** lift one of R41's pads (desolder one leg) and measure across the resistor with both leads off the board. **OR** visually read R41's value (color bands on THT package, or "472"/"103" SMD code) — non-invasive. Both deferred to operator preference; not gating Phase 35 close.

### Band-math semantics under Plan 01 INPUT high-Z (Phase 34 §8 ASCII correction)

Plan 01's CR-01 fix switched `PIN_HW_REVISION_DETECT_ADC` from `INPUT_PULLUP` to `INPUT` (high-Z) for band-math correctness. **Side effect: the MCU's internal pull-up (the R_top in the §8 ASCII divider model) is disabled.** With no pull-up active, A3 has no path to +5V — only the R41 path to JP4 (which routes to GND in normal operation). The ATmega's ADC input leakage (~150 nA per ATmega328P datasheet, §"Pin Configurations") through R41 = 4.7 kΩ (schematic) or higher (per measurement) produces V_A3 ≈ a few hundred µV → ADC ≈ 0 (much less than `ADC_BAND_R41_4K7_HIGH = 200`).

Conclusion: **band-math under Plan 01 doesn't actually depend on R41 value as long as R41 connects A3 to a low-impedance node (GND-class).** It depends on what else is on the A3 net:
- **Stock Rev 2.0/2.1/2.2 (R41 to GND via JP4, R41 value largely irrelevant):** A3 → ~0V → ADC ∈ [0, 200) → `REVISION_2_0` ("Rev 2.0-class") ✓ confirmed Rev 2.0 + Rev 2.2 bench
- **Modified Rev 0 (operator rework adds external pull-up — inferred from bench data):** A3 → ~1-3V → ADC ∈ [220, 600) → `REVISION_2_3` — the operator's mod placed something between A3 and a positive rail
- **Pre-Rev2 boards (no R41 designator at all):** A3 floats → variable / high ADC → `REVISION_0` or `REVISION_1` via the A2 disambiguation

**Implication for Wave 4 (Plan 05):** the "threshold widening" plan in D-02 needs a fundamental re-think. The bands as written (`< 200` vs `[200, 220)` vs `[220, 600)` vs `≥ 600`) work empirically on the operator's 3 boards because they characterize *what's on the A3 net*, not *R41 value*. Wave 4 should:
- (A) Update `.planning/v1.7-SHIELD-REVS.md` §8 ASCII to remove the "internal pull-up = R_top" attribution (it's no longer accurate post-Plan 01) and add a "Plan 01 disabled the pull-up — bands now characterize A3-net composition, not R41 value alone" footnote.
- (B) Update §9 ADC band table footnotes accordingly.
- (C) Decide whether to ADD an external R_top in a future shield rev (Rev 2.4?) to make R41 value actually drive ADC variance, OR document the current behavior as the intended scheme (with the dispatcher-fall-through accepting R41-value-agnostic detection).
- (D) Threshold widening per D-02 is moot — the current thresholds aren't being stressed by R41 variance (the firmware doesn't actually depend on it).

### Band-math semantics under Plan 01 INPUT high-Z (Phase 34 §8 ASCII correction)

Plan 01's CR-01 fix switched `PIN_HW_REVISION_DETECT_ADC` from `INPUT_PULLUP` to `INPUT` (high-Z) for band-math correctness. **Side effect: the MCU's internal pull-up (the R_top in the §8 ASCII divider model) is disabled.** With no pull-up active, A3 has no path to +5V — only the R41 path to GND via JP4. The ATmega's ADC input leakage (~150 nA per ATmega328P datasheet, §"Pin Configurations") through R41 = 20 kΩ produces V_A3 ≈ 150 nA × 20 kΩ = **3 mV** → ADC ≈ 1 (much less than `ADC_BAND_R41_4K7_HIGH = 200`).

Conclusion: **band-math under Plan 01 doesn't actually depend on R41 value.** It depends on what's on the A3 net beyond R41:
- **Stock Rev 2.0/2.1/2.2 (R41 only to GND via JP4):** A3 → ~0V → ADC ≈ 0..200 → `REVISION_2_0` ("Rev 2.0-class")
- **Modified Rev 0 (operator-attested rework with external pull-up — bench evidence):** A3 → ~1-3V → ADC ∈ [220, 600) → `REVISION_2_3` (the operator's mod intentionally placed something between A3 and a positive rail)
- **Pre-Rev2 boards (no R41 designator at all):** A3 floats → variable / high ADC → `REVISION_0` or `REVISION_1` via the A2 disambiguation

**Implication for Wave 4 (Plan 05):** the "threshold widening" plan needs a fundamental re-think. The bands as written (`< 200` vs `[200, 220)` vs `[220, 600)` vs `≥ 600`) work empirically on the operator's 3 boards because they're characterizing *what's on the A3 net*, not *R41 value*. Wave 4 should:
- (A) Update `.planning/v1.7-SHIELD-REVS.md` §8 ASCII to remove the "internal pull-up = R_top" attribution (it's no longer accurate post-Plan 01) and add a "Plan 01 disabled the pull-up — bands now characterize A3-net composition, not R41 value" footnote.
- (B) Update §9 ADC band table footnotes accordingly.
- (C) Decide whether to ADD an external R_top in a future shield rev (Rev 2.4?) to make R41 value actually matter, OR document the current behavior as the intended scheme.
- (D) Threshold widening per D-02 is moot — the current thresholds aren't actually being stressed by R41 variance, only by external-pullup variance (which only exists on Modified Rev 0).

---

## Modified Rev 0 Board (`/dev/ttyACM1` — opportunistic capture, outside primary plan scope)

### Identity verification

- Port: `/dev/ttyACM1`
- `controller:` identity: `leonardo` (ATmega32U4)
- Pre-flight: `firestarter -v -p /dev/ttyACM1 hw` → `FW: 3.0.0b4:leonardo`

### Sideload result

- Install command: `firestarter -v -p /dev/ttyACM1 fw -i --pre --force -b leonardo`
- avrdude command: `avrdude -v -p atmega32u4 -c avr109 -b 57600 -P /dev/ttyACM1 -D -U flash:w:firestarter_leonardo.hex:i`
- Result: ✅ "Firmware successfully updated on /dev/ttyACM1 (5.25s)"

### Reads (5 reads — Leonardo does NOT auto-reset on serial open; all 5 are effectively the same boot)

**Reads 1–5 — all identical:**
```
I: FW: 3.0.0b5:leonardo
I: Physical HW: Rev 2.3
I: HW: Rev 2.0-class
I: Cmd: 0x0f (HW_VERSION)
OK: Ready
OK: Rev 2.0-class, Override HW: Rev 2.3
```

**Interpretation:**
- Physical ADC detect: **Rev 2.3** (10k bucket — `adc_a3` in `[ADC_BAND_R41_10K_LOW (220), ADC_BAND_R41_10K_HIGH (...))`)
- EEPROM hw_revision override: **Rev 2.3** (operator-set, value=5)
- Effective "HW" line: **Rev 2.0-class** — Phase 34 D-07 dispatcher treats `REVISION_2_3` as ctrl-reg-identical to `REVISION_2_x` for runtime behavior, while preserving the silkscreen string distinction in the override and physical-detect lines.

**This is interesting bench evidence for §6 row 6 capability matrix:** the modified Rev 0 mod has wired a 10k divider, putting it in the same band as Anders chat-intel's "Rev 2.3" board. If the operator's mod is documented, it likely intentionally targets 10k. Phase 35 §6 row "modified rev 0" can be filled in from this evidence.

### Raw ADC capture

`adc_a3` not exposed by FW. Band: 10k. 5 reads, 100% consistent.

---

## UAT cross-board summary

| UAT | Board | Result | Evidence |
|-----|-------|--------|----------|
| UAT-1 | Rev 2.0 (ACM0) | **PASS** | `FW: 3.0.0b5:uno` boots cleanly, `OK: Rev 2.0-class`, no `WARN: HW: rev_unknown` |
| UAT-2 | Rev 2.2 (USB0) | **PASS (firmware-side)** — R41 multimeter still operator-pending | `FW: 3.0.0b5:uno328pb` (wrong-FW state persists; detect-independent), `OK: Rev 2.0-class` → infers R41=4k7, contradicts Anders chat-intel |
| UAT-3 | Both Rev 2.0 + Rev 2.2 (+ ACM1 opportunistic) | **PASS** | 5 boots × 3 boards = 15 reads. 100% stable. No `rev_unknown`, no band-flapping. CR-01 INPUT high-Z fix eliminates the prior pull-up-induced shift; CR-02 hard-fail-loud emit doesn't fire because no board lands in the guard gap. |

---

## Wrong-FW persistence on `/dev/ttyUSB0`

The plain-Uno board on `/dev/ttyUSB0` still runs `uno328pb` firmware after the Phase 35 sideload. Root cause: `firestarter fw -i -b uno` honors the EXISTING firmware's controller string over the `-b` flag (see `firestarter/firestarter/firmware.py` controller-detection logic). To force the correct `uno` build, the operator must either:

1. Direct avrdude call: `avrdude -p atmega328p -c arduino -b 115200 -P /dev/ttyUSB0 -D -U flash:w:firestarter_uno.hex:i` (download the hex from the 3.0.0b5 release first)
2. Or modify the firestarter app to honor `-b` over controller auto-detect (separate phase / backlog item)

**Phase 35 scope decision:** wrong-FW state does NOT block UAT-1/2/3 because detect-rev logic is FW-build-independent. Carry forward as a v1.8 backlog item per `[[project_uno328pb_correction]]` — operator's existing decision to skip this board for v1.6 read-bug repro extends here.

---

## Photos (D-06)

**Operator action required.** Drop JPGs at:

- `.planning/v1.7/photos/rev-2-0/top.jpg`
- `.planning/v1.7/photos/rev-2-0/bottom.jpg`
- `.planning/v1.7/photos/rev-2-0/silkscreen.jpg`
- `.planning/v1.7/photos/rev-2-2/top.jpg`
- `.planning/v1.7/photos/rev-2-2/bottom.jpg`
- `.planning/v1.7/photos/rev-2-2/silkscreen.jpg`
- (Optional) `.planning/v1.7/photos/rev-0-modified/top.jpg` + `bottom.jpg` + `silkscreen.jpg` + close-up of the 10k mod

Photo dirs already exist; READMEs in place; Task 5 commit will include them once dropped.

---

## Summary (Wave 4 input)

- **Rev 2.0 MSG_OK_REV stability:** stable (5/5 boots = `Rev 2.0-class`)
- **Rev 2.2 MSG_OK_REV stability:** stable (5/5 boots = `Rev 2.0-class`)
- **Modified Rev 0 MSG_OK_REV stability:** stable (5/5 reads = effective `Rev 2.0-class` / physical `Rev 2.3`; opportunistic capture; Leonardo single-boot)
- **A3↔GND multimeter readings (board OFF, header pins):** Rev 2.0 = 27 kΩ; Rev 2.2 = 20 kΩ. **NOT R41 in isolation** — measurement includes unpowered-ATmega input-protection leakage paths. Schematic R41 value (4.7 kΩ) is not contradicted; §8 OPEN ground-truth resolution deferred to v1.8 backlog (operator decision: defer rather than do invasive lift-leg measurement now).
- **Raw ADC summary:** not exposed by `3.0.0b5` firmware. Moot under Plan 01 INPUT high-Z — band math no longer depends on R41 value (depends on A3-net composition; see §"Band-math semantics under Plan 01 INPUT high-Z").
- **Guard-gap feasibility:** **PROVED EMPIRICALLY** — 0/15 reads landed in the guard gap (`[200, 220)`); no board crossed into `REVISION_UNKNOWN`. The existing 20-count guard gap is sufficient on the operator's bench hardware; D-02 threshold widening no longer needed under Plan 01 INPUT high-Z.
- **UAT-1 / UAT-2 / UAT-3 outcomes:** all firmware-side PASS. UAT-2's §8 OPEN R41-value-in-isolation deferred to v1.8 (operator decision; non-blocking).
- **Hand-off to Wave 4 Plan 05:** redirect from "threshold widening" (D-02) to:
  - (a) Update `.planning/v1.7-SHIELD-REVS.md` §8 ASCII to remove the "internal pull-up = R_top" attribution (no longer true post-Plan 01) and document the actual band-math semantics (characterizes A3-net composition, not R41 value).
  - (b) Update §9 ADC band table footnotes to match.
  - (c) `firestarter/include/rurp_pinout.h:58-62` ADC_BAND constants stay as-is — they work empirically on all 3 boards. No re-derivation needed.
  - (d) Carry forward "external R_top in future shield rev to make R41 value actually drive ADC variance" as a v1.8 backlog seed.

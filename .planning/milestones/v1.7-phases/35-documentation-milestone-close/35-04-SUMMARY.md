---
phase: 35-documentation-milestone-close
plan: 04
status: complete
deviation: D-08 substrate (lockstep 3.0.0b5 cut + meta submodule bump) intertwined with bench validation; auto-increment via push trigger (not workflow_dispatch) — equivalent result, both repos at 3.0.0b5 in lockstep
requirements-completed: [DOC-01]
key-files:
  modified:
    - .planning/phases/35-documentation-milestone-close/35-HUMAN-UAT.md
    - .planning/v1.7/bench-evidence-35.md
    - firestarter (submodule pointer bump beta @ 1b05b1b)
    - firestarter_app (submodule pointer bump beta @ 1737939)
  created:
    - .planning/phases/35-documentation-milestone-close/35-04-SUMMARY.md
commits:
  - "ad-hoc Task 2 (firestarter sub-repo beta merge):    firestarter beta @ 8041dc3 (Phase 35 Wave 1 fixes CR-01 + CR-02)"
  - "ad-hoc Task 2 (firestarter_app sub-repo beta merge): firestarter_app beta @ 70a3692 (Phase 35 Wave 1 fixes WR-01 + WR-02)"
  - "ad-hoc Task 2 (CI auto-bump push-triggered):         firestarter beta @ 1b05b1b (version.h CI bump) + firestarter_app beta @ 1737939 (__init__.py CI bump)"
  - "meta d8ec134 — feat(35-04): bump submodules to beta @ 3.0.0b5 — Phase 35 Wave 3 beta cut (D-08)"
  - "meta dce2f2b — docs(35-04): Phase 35 Wave 3 bench evidence — UAT-1/2/3 firmware-side PASS + §8 R41 deferral (D-05 + D-06)"
patterns-established:
  - "USB passthrough bench session — devcontainer reaches operator's /dev/ttyACM*+ttyUSB* directly; Claude drives firmware sideload + serial reads, operator handles physical (chip handling, multimeter, photos). See reference_usb_passthrough_bench memory."
  - "Two-board A3↔GND comparison reveals measurement complications — single-board reading interpretable as 'R41 value', but two-board comparison forces interpretation as 'measurement-path-includes-MCU-leakage'. Pattern: always cross-check apparent physical measurements against a second instance."
---

# Phase 35 Plan 04 — Operator-on-Bench Wave Summary

**Validated Wave 1 firmware fixes (CR-01 + CR-02 + WR-01 + WR-02) on real silicon across 3 RURP shield revisions; cut both sub-repos to 3.0.0b5 on `beta` via v1.4 lockstep mechanism; captured firmware-side PASS evidence for UAT-1/2/3 with §8 OPEN R41-value-in-isolation deferred to v1.8 per operator decision.**

## UAT outcomes (verbatim from 35-HUMAN-UAT.md)

| UAT | Result |
|-----|--------|
| UAT-1 (Rev 2.0 — /dev/ttyACM0, Uno) | `[pass]` — 5/5 boots stable on `3.0.0b5:uno`, `OK: Rev 2.0-class, Override HW: Rev 2.0-class`. No `WARN: HW: rev_unknown` (detect lands cleanly in 4k7 bucket). |
| UAT-2 (Rev 2.2 — /dev/ttyUSB0, plain Uno w/ wrong-FW uno328pb build) | `[pass-firmware-side; §8-OPEN-inconclusive-via-A3-GND-method]` — 5/5 boots stable on `3.0.0b5:uno328pb`, `OK: Rev 2.0-class`. A3↔GND multimeter readings on TWO boards (Rev 2.0=27 kΩ, Rev 2.2=20 kΩ, board OFF) revealed this measurement does NOT isolate R41 — includes ATmega input-protection leakage paths. Schematic R41=4.7 kΩ not contradicted. §8 OPEN R41-value-in-isolation deferred to v1.8 backlog (lift-leg or visual-inspection methods available but operator decided to defer rather than do invasive measurement). |
| UAT-3 (multi-boot CR-01 cross-check) | `[pass]` — 5 boots × 3 boards = 15 reads. 100% stable, no `rev_unknown`, no band-flapping. CR-01 INPUT high-Z fix confirmed effective; CR-02 hard-fail-loud `WARN: HW: rev_unknown` emit doesn't fire because no board lands in the `[200, 220)` guard gap. Bonus finding: Modified Rev 0 detects as `Rev 2.3` (10k bucket) — operator's mod intentionally wired a 10k pull-up path on A3. |

## R41 measurement value + bucket assignment

- **A3↔GND header-pin readings (board OFF, after pin reflow 2026-05-26):**
  - Rev 2.0: 27 kΩ
  - Rev 2.2: 20 kΩ
- **Interpretation:** these readings include parallel ATmega input-protection leakage paths to GND with the chip unpowered — NOT R41 in isolation. Two-board comparison (same schematic family, same nominal R41 value, different ATmega instances → 7 kΩ measurement spread) forces this conclusion.
- **Schematic R41 value (4.7 kΩ for Rev 2.0/2.1/2.2) NOT contradicted** — consistent with both readings once the parallel leakage path is accounted for.
- **Bucket assignment:** firmware classifies both boards as **`REVISION_2_0` (4k7 bucket, "Rev 2.0-class")** because Plan 01 INPUT high-Z mode produces V_A3 ≈ 0V regardless of R41 value (band math characterizes A3-net composition, not R41 value alone — see Phase 34 §8 ASCII correction in §"Band-math semantics under Plan 01 INPUT high-Z" of bench-evidence-35.md).
- **§8 OPEN resolution path forward:** lift-leg measurement OR visual R41 marking inspection — both deferred to v1.8 backlog per operator decision; non-blocking for v1.7 close.

## Per-board MSG_OK_REV silkscreen string

| Port | Controller (FW) | Shield | Effective `OK: Rev …` silkscreen string |
|------|-----------------|--------|----------------------------------------|
| /dev/ttyACM0 | `3.0.0b5:uno` | Rev 2.0 | `Rev 2.0-class, Override HW: Rev 2.0-class` |
| /dev/ttyACM1 | `3.0.0b5:leonardo` | Modified Rev 0 | `Rev 2.0-class, Override HW: Rev 2.3` |
| /dev/ttyUSB0 | `3.0.0b5:uno328pb` (wrong-FW persists) | Rev 2.2 | `Rev 2.0-class` |

## Raw ADC capture method + summary statistics

**Method:** firmware does NOT log `adc_a3` raw values over serial (the `analog_read_avg8(PIN_HW_REVISION_DETECT_ADC)` result at `firestarter/include/rurp_hw_rev_utils.h:68` is consumed by the band-lookup `if/else if` chain at `:70-88` and only the resolved `REVISION_*` byte is communicated). Wave 4 threshold-widening from raw ADC bench data (D-02) is therefore not possible from `3.0.0b5` firmware. Moot anyway under Plan 01 INPUT high-Z — band math no longer depends on R41 value.

**Stability summary:**
- Rev 2.0 (5 fresh boots via DTR-reset): all `Rev 2.0-class`, 100% stable
- Rev 2.2 (5 fresh boots via DTR-reset): all `Rev 2.0-class`, 100% stable
- Modified Rev 0 (5 reads, Leonardo single-boot effectively — no auto-reset on serial open): all consistent
- 0/15 reads landed in `[200, 220)` guard gap → CR-01 INPUT high-Z fix confirmed effective; CR-02 hard-fail-loud `WARN` emit does not fire on operator's hardware

## Sub-repo + meta-repo commit SHAs

**Sub-repo beta state at 3.0.0b5 cut:**
- **firestarter:** beta @ `1b05b1b` (merge `8041dc3` + CI version.h bump)
  - GitHub Pre-release: https://github.com/henols/firestarter/releases/tag/3.0.0b5 (3 .hex assets: uno + uno328pb + leonardo)
- **firestarter_app:** beta @ `1737939` (merge `70a3692` + CI `__init__.py` bump)
  - GitHub Pre-release: https://github.com/henols/firestarter_app/releases/tag/3.0.0b5

**Meta-repo commits on `v1.7-shield-investigation` branch:**
- `d8ec134` — `feat(35-04): bump submodules to beta @ 3.0.0b5 — Phase 35 Wave 3 beta cut (D-08)`
- `dce2f2b` — `docs(35-04): Phase 35 Wave 3 bench evidence — UAT-1/2/3 firmware-side PASS + §8 R41 deferral (D-05 + D-06)`

## Open items carried forward (Wave 4+ implications)

1. **Phase 34 §8 ASCII correction (Wave 4 / Plan 05/06)** — §8 attributes R_top to MCU internal pull-up, which Plan 01 disabled (INPUT high-Z mode). Bands now characterize A3-net composition, not R41 value alone. Update §8 + §9 doc accordingly.

2. **D-02 threshold widening deprecated** — moot under Plan 01 semantics. The existing `ADC_BAND_R41_4K7_HIGH=200 / ADC_BAND_R41_10K_LOW=220 / ADC_BAND_R41_10K_HIGH=600` thresholds work empirically on all 3 operator boards. No re-derivation needed.

3. **§8 OPEN R41-value-in-isolation (v1.8 backlog)** — definitive resolution via lift-leg or visual-inspection method. Schematic 4.7 kΩ is currently unrefuted by bench evidence.

4. **`/dev/ttyUSB0` wrong-FW persistence (v1.8 backlog)** — `firestarter fw -i -b uno` ignores `-b` in favor of existing FW's controller-string auto-detect. Workaround documented (direct avrdude); separate phase needed for clean fix.

5. **Future shield rev (v1.8+ seed)** — to make R41 value actually drive ADC variance, add an external R_top to a Rev 2.4 PCB. Until then, R41-value-driven detection requires the lift-leg/visual ground-truth method per operator.

## Wave 4 (Plan 05) hand-off

Wave 4 desk-side work consumes:
- `.planning/v1.7/bench-evidence-35.md` §"Band-math semantics under Plan 01 INPUT high-Z" → update `.planning/v1.7-SHIELD-REVS.md` §8 ASCII + §9 footnotes
- `.planning/v1.7/bench-evidence-35.md` §"R41 measurement attempt" → update §3 row 3 with `4.7 kΩ per schematic / 10 kΩ per Anders chat-intel / [v1.8 follow-up for in-isolation ground truth]`
- `firestarter/include/rurp_pinout.h:58-62` ADC_BAND constants: **NO CHANGES needed** (existing thresholds work empirically). Plan 05's "threshold widening" task should be redirected to "documentation alignment" task.

Plan 05 can now start.

# v1.7 Phase 35 Bench Evidence

**Operator bench session:** YYYY-MM-DD (filled at session time)
**Boards:** Rev 2.0, Rev 2.2
**Firmware:** 3.0.0b5 (post Wave 1 CR-01 / CR-02 / WR-01 / WR-02 fixes)
**Cross-refs:**
- `.planning/phases/35-documentation-milestone-close/35-HUMAN-UAT.md` (UAT-1 / UAT-2 / UAT-3 PASS/FAIL/SKIP record)
- `.planning/v1.7-SHIELD-REVS.md` §3 (R41 value) + §8 (OPEN flag resolution) + §9 (per-rev ADC band table, Wave 4 input)
- `.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-REVIEW.md` (CR-01 / CR-02 origin)

Operator protocol — non-negotiable per memory:
- `feedback_chip_out_before_sideload` — chip OUT of socket BEFORE any `firestarter fw -i` / `avrdude` / `pio run -t upload`.
- `feedback_verify_port_identity_each_task` — verify `controller:` identity per port at every task start; `/dev/ttyACM*` numbers shuffle across USB unplug/replug.

---

## Rev 2.0 Board

### Identity verification
- Port: TBD (e.g. `/dev/ttyACM0` or `/dev/ttyUSB0`)
- `controller:` identity: TBD (expected: `uno`)
- Pre-flight command: `firestarter --board uno hw -v` (or operator's preferred identity-print command)

### Sideload result
- Install command used: TBD (e.g. `firestarter fw -i --pre --force` or `firestarter fw -i --firmware-version 3.0.0b5 --force`)
- avrdude output: TBD (record any non-zero exit / verify errors)
- Post-flash boot: TBD

### Boot logs (≥ 3 boots — capture verbatim)

**Boot 1:**
```
TBD — capture MSG_OK_REV (`OK: Rev …` silkscreen string), MSG_INFO_HW (`INFO: HW: …`), MSG_INFO_PHYSICAL_HW (`INFO: Physical HW: …`), and any LOG_WARN_ID(MSG_INFO_HW, REVISION_UNKNOWN) hard-fail-loud emit from Plan 01's CR-02 fix.
```

**Boot 2:**
```
TBD
```

**Boot 3:**
```
TBD
```

(Add additional boot blocks as needed — ≥ 3 minimum; ≥ 5 preferred for stability characterization per D-02 widen-after-bench-characterization.)

### Raw ADC capture (per boot) — for Wave 4 §9 band re-derivation per D-02

| Boot # | `adc_a3` (raw, 0..1023) | Detected silkscreen string | Notes |
|--------|-------------------------|----------------------------|-------|
| 1      | TBD                     | TBD                        |       |
| 2      | TBD                     | TBD                        |       |
| 3      | TBD                     | TBD                        |       |

---

## Rev 2.2 Board

### Identity verification
- Port: TBD
- `controller:` identity: TBD (expected: `uno`)
- Pre-flight command: TBD

### Sideload result
- Install command used: TBD
- avrdude output: TBD
- Post-flash boot: TBD

### Boot logs (≥ 3 boots — capture verbatim)

**Boot 1:**
```
TBD
```

**Boot 2:**
```
TBD
```

**Boot 3:**
```
TBD
```

### Raw ADC capture (per boot)

| Boot # | `adc_a3` (raw, 0..1023) | Detected silkscreen string | Notes |
|--------|-------------------------|----------------------------|-------|
| 1      | TBD                     | TBD                        |       |
| 2      | TBD                     | TBD                        |       |
| 3      | TBD                     | TBD                        |       |

### R41 measurement (§8 OPEN resolution — Phase 35 follow-up #5)

Procedure: with board powered OFF (USB unplugged), measure R41 resistance directly on the Rev 2.2 PCB using a multimeter in resistance / Ω mode.

- **Multimeter reading:** TBD Ω
- **Schematic-stated value:** 4.7 kΩ (upstream Rev 2.2 schematic blob `f3b7a521`, identical to Rev 2.1)
- **Anders chat-intel value:** 10 kΩ (per `.planning/v1.7/notes/CHAT-INTEL.md` §1)
- **Resolution / bucket assignment:** TBD (4k7 → Rev 2.0-class, 10k → Rev 2.3)
- **Cross-ref:** `.planning/v1.7-SHIELD-REVS.md` §3 row 3 + §8 OPEN flag; updated in Wave 3 per D-Discretion (atomic §3 + §8 + §9 row commit).

---

## Summary (Wave 4 input)

(Filled at session close — Task 5 Claude finalization step.)

- **Rev 2.0 MSG_OK_REV stability:** TBD (stable / intermittent-with-rev_unknown / consistent-rev_unknown)
- **Rev 2.2 MSG_OK_REV stability:** TBD
- **R41 measured value (Rev 2.2):** TBD Ω → TBD bucket (4k7 / 10k)
- **Raw ADC summary statistics (for Wave 4 Plan 05 band widening):**
  - Rev 2.0 `adc_a3`: min=TBD, max=TBD, mean=TBD (± stddev if ≥ 5 boots)
  - Rev 2.2 `adc_a3`: min=TBD, max=TBD, mean=TBD (± stddev if ≥ 5 boots)
  - Guard-gap feasibility: ≥ 50-count separation between adjacent buckets? TBD
- **UAT-1 / UAT-2 / UAT-3 outcomes:** TBD (cross-link to `35-HUMAN-UAT.md` post-finalization)
- **Hand-off to Wave 4 Plan 05:** raw ADC values above → re-derive `ADC_BAND_R41_4K7_HIGH` / `ADC_BAND_R41_10K_LOW` / `ADC_BAND_R41_10K_HIGH` in `firestarter/include/rurp_pinout.h:58-62` with ≥ 50-count guard gap; if separation infeasible, collapse Rev 2.0-class + Rev 2.3 into a single detected band per D-02's fall-back branch.

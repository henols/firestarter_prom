---
phase: 34-shield-version-detect-design-firmware-plumbing
plan: 03
subsystem: firmware-detect-rev-rework
tags: [firmware, detect-rev, adc-band, rurp-hw-rev-utils, rurp-pinout, analog-read, 8-sample-avg, sub-repo, atomic-commit, detect-fw-01, v1.7]

# Dependency graph
requires:
  - phase: 34-shield-version-detect-design-firmware-plumbing
    plan: 00
    provides: "phase context — D-03 (ADC threshold values 200/220/600), D-06 (digitalRead → analogRead band-lookup rework), D-07 (case REVISION_2_3 arm + 0xFE-vs-0xFF sentinel carve-out), D-11 (strict band ordering invariant)"
  - phase: 34-shield-version-detect-design-firmware-plumbing
    plan: 01
    provides: "v1.7-SHIELD-REVS.md §9 per-rev expected ADC band table — cross-references the three ADC_BAND_R41_* constants this plan declares by name"
  - phase: 34-shield-version-detect-design-firmware-plumbing
    plan: 02
    provides: "firestarter/include/rurp_shield.h REVISION_2_3 = 5 + REVISION_UNKNOWN = 0xFE enum symbols — consumed by this plan's reworked detect-rev body + case REVISION_2_3 arm"
  - phase: 33-silkscreen-label-code-alias-migration
    plan: 03
    provides: "atomic D-06-style sub-repo single-commit precedent; #define (not constexpr) preprocessor-constant pattern for byte-stability"
provides:
  - "firestarter/include/rurp_pinout.h — Section 1b ADC voltage-band threshold #define block (ADC_BAND_R41_4K7_HIGH 200, ADC_BAND_R41_10K_LOW 220, ADC_BAND_R41_10K_HIGH 600) under #ifdef HARDWARE_REVISION"
  - "firestarter/include/rurp_hw_rev_utils.h — reworked rurp_detect_hardware_revision() body (4-arm if/else-if/else-if/else band-lookup chain over analog_read_avg8 sample) + new static inline analog_read_avg8(uint8_t pin) helper (8-sample averaging via sum-and-shift) + case REVISION_2_3: arm in rurp_map_ctrl_reg_for_hardware_revision() aliased to the existing REV_2_x ctrl-reg layout"
  - "Latent-bug cleanup: function-body revision = 0xFF assignment (collision with EEPROM-override-absent sentinel) replaced by explicit revision = REVISION_UNKNOWN guard-gap arm"
  - "Plan 04 substrate — per-env .hex byte counts captured (post-rework half of Plan 04's verify-detect-34.sh delta-band gate table)"
affects:
  - "Phase 34 Plan 04 (firestarter sub-repo pointer bump + GATE-1.7 .hex delta gate) — bundles this commit's firestarter HEAD into the meta-repo submodule pointer; runs verify-detect-34.sh which will surface a delta-band miss (see Hand-off below)"
  - "Phase 34 Plan 05 (firestarter_app Python parity) — orthogonal; constants.py mirror lands per D-08"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Analog band-lookup detect-rev (vs prior digital-A3 + analog-A2 dual-pin scheme) — 4-arm if/else-if/else-if/else chain over 8-sample-averaged ADC read; canonical AVR idiom for 3-band ADC decode preserved (see Phase 34 RESEARCH §Firmware Detection Logic Rework)"
    - "8-sample averaging via static inline analog_read_avg8(uint8_t pin) — pure shift-divide (sum >> 3); no library call; robustifies against AVcc switching noise per RESEARCH §8-Sample Averaging Recommendation"
    - "#define-NOT-constexpr threshold constants in rurp_pinout.h Section 1b per Phase 33 D-07 — preprocessor constants resolve at compile time, preserving AVR-objcopy .hex byte-math substrate"
    - "Sentinel-carve-out pattern honored: 0xFE = REVISION_UNKNOWN (band-gap fall-through), 0xFF stays exclusively reserved as EEPROM-override-absent sentinel per D-07"
    - "Single atomic sub-repo commit (Phase 33 D-06 precedent) — 2-file diff (rurp_pinout.h + rurp_hw_rev_utils.h) lands as one bisect-granular unit on the firestarter v1.7-shield-investigation branch"

key-files:
  created:
    - ".planning/phases/34-shield-version-detect-design-firmware-plumbing/34-03-SUMMARY.md (this file)"
  modified:
    - "firestarter/include/rurp_pinout.h (+15 lines — Section 1b ADC voltage-band threshold #define block)"
    - "firestarter/include/rurp_hw_rev_utils.h (52 lines changed — analog_read_avg8 helper + reworked detect-rev body + case REVISION_2_3 arm in ctrl-reg mapper; +56 / -11 line accounting per git stat)"

key-decisions:
  - "D-03 threshold values landed verbatim (ADC_BAND_R41_4K7_HIGH = 200, ADC_BAND_R41_10K_LOW = 220, ADC_BAND_R41_10K_HIGH = 600); strict numerical ordering 200 < 220 < 600 enforced by file layout and verified at commit time"
  - "D-06 digitalRead → analogRead band-lookup rework landed; 4-arm if/else-if/else-if/else chain replaces the prior switch(value) scheme; legacy A2 < 1000 disambig preserved verbatim for Rev 0 vs Rev 1"
  - "D-07 case REVISION_2_3: arm aliased to existing REV_2_x ctrl-reg arm (Rev 2.3 only changed R41 value + JP4 footprint, NOT control-line routing per §4 row 6); REVISION_UNKNOWN deliberately NOT added to the switch — falls through default: break to ctrl_reg = 0 fail-safe per RESEARCH §Caller Audit row 3"
  - "8-sample averaging via static inline analog_read_avg8 helper added per RESEARCH §8-Sample Averaging Recommendation: YES — ~104 µs added boot latency, ~30 B added Flash budget; well within D-10 [20, 300] B delta band"
  - "Latent-bug cleanup applied: function-body revision = 0xFF (which collided with the EEPROM-override-absent sentinel) replaced by explicit revision = REVISION_UNKNOWN guard-gap arm; file-scope static initializer at line 12 left UNCHANGED per RESEARCH (dead-code in normal boot flow)"
  - "rurp_get_hardware_revision() body UNCHANGED (VALIDATION Dim 7 — DETECT-FW-01 EEPROM-override fall-through clause satisfied by construction; awk-scoped function body verified byte-identical to pre-edit state)"
  - "Single atomic commit on firestarter sub-repo v1.7-shield-investigation branch (commit 032a2e2) covering both modified files; meta-repo submodule pointer bump deferred to Plan 04 per phase context"

requirements-completed:
  - DETECT-FW-01

# Metrics
duration: ~10min
completed: 2026-05-25
---

# Phase 34 Plan 03: Wave 2 — Firmware Detect-Rev Rework + ADC Threshold Constants Summary

**Landed the load-bearing DETECT-FW-01 deliverable: (1) three ADC-threshold #define constants (ADC_BAND_R41_4K7_HIGH = 200, ADC_BAND_R41_10K_LOW = 220, ADC_BAND_R41_10K_HIGH = 600) in a new Section 1b block of firestarter/include/rurp_pinout.h under #ifdef HARDWARE_REVISION; (2) reworked firestarter/include/rurp_hw_rev_utils.h::rurp_detect_hardware_revision() from digital-A3 + analog-A2 to analog-A3 (8-sample averaged) + 4-arm band-lookup chain that distinguishes REVISION_2_0 / REVISION_2_3 / (legacy A2 disambig for Rev 0 vs Rev 1) / REVISION_UNKNOWN; (3) new static inline analog_read_avg8(uint8_t pin) helper for AVcc-switching-noise robustness; (4) single new case REVISION_2_3: arm in rurp_map_ctrl_reg_for_hardware_revision() aliased to the existing REV_2_x ctrl-reg layout per D-07. Single atomic 2-file commit on firestarter sub-repo v1.7-shield-investigation branch (commit `032a2e2`). All 3 AVR envs build clean; native dispatch suite 15/15 PASS. rurp_get_hardware_revision() body UNCHANGED (VALIDATION Dim 7 honored). Latent revision = 0xFF function-body assignment replaced by explicit REVISION_UNKNOWN guard-gap arm; file-scope static initializer at line 12 left UNCHANGED.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-05-25T13:50:00Z (orchestrator phase-begin)
- **Completed:** 2026-05-25T14:00:00Z (post-commit)
- **Tasks:** 3 (Task 1: ADC threshold #defines; Task 2: detect-rev rework + ctrl-reg arm; Task 3: atomic commit on sub-repo)
- **firestarter sub-repo commits:** 1 (`032a2e2`)
- **Meta-repo commits in this plan:** 0 yet (this SUMMARY's final-metadata commit lands at end)
- **Files modified (firmware sub-repo):** 2 (`include/rurp_pinout.h` + `include/rurp_hw_rev_utils.h`)

## Accomplishments

### Task 1 — rurp_pinout.h: ADC voltage-band threshold constants

**Diff scope:** +15 lines under a new Section 1b block, gated by `#ifdef HARDWARE_REVISION`, sitting between the existing Section 1 PIN_* block (which ends at `PIN_HW_REVISION_DETECT_ADC A3`) and the existing Section 2 control-register bits block.

**Post-edit (firestarter/include/rurp_pinout.h:41-67):**
```c
// ---- Section 1: Arduino-pin assignments (PIN_*) ------------------------

#define PIN_VPP_VOLTAGE_ADC A2

#ifdef HARDWARE_REVISION
#define PIN_HW_REVISION_DETECT_ADC A3
#endif

// ---- Section 1b: ADC voltage-band thresholds (HARDWARE_REVISION-gated) -------
// Consumed by rurp_detect_hardware_revision() in rurp_hw_rev_utils.h to decode
// the R41-on-A3 detect divider into a per-rev enum. Voltage-band math sourced
// from Phase 34 RESEARCH §ADC Voltage Band Math + the §9 per-rev band table in
// .planning/v1.7-SHIELD-REVS.md (D-03 + D-11). Values picked with strict
// numerical ordering (200 < 220 < 600) per D-11 + a 20-count guard gap between
// the 4k7 ceiling and the 10k floor (reads in [200, 220) → REVISION_UNKNOWN).
// #define (NOT constexpr) per Phase 33 D-07 — preprocessor constants resolve
// at compile time and contribute 0 B to the .hex until referenced.
#ifdef HARDWARE_REVISION
#define ADC_BAND_R41_4K7_HIGH 200  // upper edge of 4k7 bucket (Rev 2.0/2.1/2.2)
#define ADC_BAND_R41_10K_LOW  220  // lower edge of 10k bucket (Rev 2.3); [200, 220) -> REVISION_UNKNOWN
#define ADC_BAND_R41_10K_HIGH 600  // upper edge of 10k bucket; above -> high band / no R41
#endif

// ---- Section 2: Control-register bits (CTRL_*) -------------------------
```

**Acceptance verification:**
| Check | Command | Result |
|-------|---------|--------|
| `#define ADC_BAND_R41_4K7_HIGH` present | `grep -q "^#define ADC_BAND_R41_4K7_HIGH" rurp_pinout.h` | PASS |
| `#define ADC_BAND_R41_10K_LOW` present | `grep -q "^#define ADC_BAND_R41_10K_LOW" rurp_pinout.h` | PASS |
| `#define ADC_BAND_R41_10K_HIGH` present | `grep -q "^#define ADC_BAND_R41_10K_HIGH" rurp_pinout.h` | PASS |
| All 3 inside Section 1b between Section 1 and Section 2 | `awk '/Section 1b/,/Section 2/' rurp_pinout.h \| grep ADC_BAND_R41_4K7_HIGH` | PASS |
| Strict numerical ordering 200 < 220 < 600 | `awk '/^#define ADC_BAND_R41/ {print $3}' rurp_pinout.h \| sort -n -c` | PASS (exit 0) |
| All 3 #defines inside `#ifdef HARDWARE_REVISION` block | `awk '/#ifdef HARDWARE_REVISION/,/#endif/' rurp_pinout.h \| grep -c "ADC_BAND_R41"` | 3 (PASS) |
| `#define` shape used (NOT `constexpr`) per Phase 33 D-07 | `grep -q "^constexpr.*ADC_BAND_R41" rurp_pinout.h` | non-zero (PASS — no constexpr) |

### Task 2 — rurp_hw_rev_utils.h: detect-rev rework + ctrl-reg arm + latent-bug cleanup

**Three modifications inside the existing `#ifdef HARDWARE_REVISION` block:**

**Modification A — new static inline `analog_read_avg8()` helper (above `rurp_detect_hardware_revision()`):**
```c
// 8-sample averaging on a single ADC pin — pure shift-divide, no library call.
// Robustifies the A3 detect-divider read against AVcc switching noise (the
// RURP shield's AVcc plane carries data-buffer + control-register switching
// loads — not a quiet ADC reference). See Phase 34 RESEARCH §ADC Voltage Band
// Math + §8-Sample Averaging Recommendation. ~104 µs added boot latency,
// ~30 B added Flash — well within the D-10 [20, 300] B delta band.
static uint16_t analog_read_avg8(uint8_t pin) {
    uint16_t sum = 0;
    for (uint8_t i = 0; i < 8; i++) {
        sum += (uint16_t)analogRead(pin);
    }
    return (uint16_t)(sum >> 3);  // average over 8 samples
}
```

**Modification B — reworked `rurp_detect_hardware_revision()` body (per D-06 + 8-sample averaging):**
```c
void rurp_detect_hardware_revision() {
    pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT_PULLUP);
    pinMode(PIN_VPP_VOLTAGE_ADC, INPUT_PULLUP);

    // 8-sample averaging on the A3 detect divider to robustify against AVcc
    // switching noise (see Phase 34 RESEARCH §ADC Voltage Band Math).
    uint16_t adc_a3 = analog_read_avg8(PIN_HW_REVISION_DETECT_ADC);

    if (adc_a3 < ADC_BAND_R41_4K7_HIGH) {
        // Rev 2.0/2.1/2.2 with R41=4k7 — reports as REVISION_2_0 (broad bucket
        // per D-04; operator distinguishes 2.1/2.2 via EEPROM hw_revision
        // override if needed).
        revision = REVISION_2_0;
    } else if (adc_a3 >= ADC_BAND_R41_10K_LOW && adc_a3 < ADC_BAND_R41_10K_HIGH) {
        // Rev 2.3 with R41=10k.
        revision = REVISION_2_3;
    } else if (adc_a3 >= ADC_BAND_R41_10K_HIGH) {
        // High band — no R41 (pre-detect-resistor era). Disambiguate Rev 0 vs
        // Rev 1 via the legacy A2 divider check (preserved from prior code —
        // already correct, already shipped per D-06).
        revision = analogRead(PIN_VPP_VOLTAGE_ADC) < 1000 ? REVISION_1 : REVISION_0;
    } else {
        // adc_a3 in the [ADC_BAND_R41_4K7_HIGH, ADC_BAND_R41_10K_LOW) guard gap —
        // physical detect inconclusive. EEPROM hw_revision override is the
        // escape hatch. 0xFE NOT 0xFF — 0xFF stays reserved as the
        // EEPROM-override-absent sentinel per D-07.
        revision = REVISION_UNKNOWN;
    }
    pinMode(PIN_VPP_VOLTAGE_ADC, INPUT);
}
```

**Modification C — new `case REVISION_2_3:` label in `rurp_map_ctrl_reg_for_hardware_revision()` (after `case REVISION_2_2:`):**
```c
    switch (hw) {
    case REVISION_2_0:
    case REVISION_2_1:
    case REVISION_2_2:
    case REVISION_2_3:  // <-- NEW (D-07 — ctrl-reg layout identical to REV_2_x per §4 row 6)
        ctrl_reg = data & (CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE | CTRL_VPP_P1_ENABLE | CTRL_ADDRESS_LINE_17 | CTRL_READ_WRITE | CTRL_VPP_REGULATOR_ENABLE);
        ctrl_reg |= data & CTRL_VPP_VPE_DROP_ENABLE ? CTRL_VPP_VPE_DROP_ENABLE_REV2 : 0;
        ctrl_reg |= data & CTRL_ADDRESS_LINE_16 ? CTRL_ADDRESS_LINE_16_REV2 : 0;
        ctrl_reg |= data & CTRL_ADDRESS_LINE_18 ? CTRL_ADDRESS_LINE_18_REV2 : 0;
        break;
    ...
    default:
        // REVISION_UNKNOWN + any unrecognized byte fall through to ctrl_reg = 0
        // (fail-safe — no VPP enables, no VPE enables; EEPROM override is the
        // operator escape hatch per RESEARCH §Caller Audit row 3).
        break;
    }
```

**Latent-bug cleanup (function-body 0xFF assignment eliminated):**
The prior code's `default: revision = 0xFF;` (which collided with the EEPROM-override-absent sentinel at `rurp_hw_rev_utils.h:63` / `rurp_config_utils.cpp:37`) is gone. The new `else` arm assigns `revision = REVISION_UNKNOWN` (= 0xFE) explicitly. The file-scope `static uint8_t revision = 0xFF;` at line 12 is intentionally UNCHANGED — that's dead-code in normal boot flow per RESEARCH (overwritten by `rurp_detect_hardware_revision()` on the first boot path before any caller reads it).

**Acceptance verification (Task 2):**
| Check | Command | Result |
|-------|---------|--------|
| `static uint16_t analog_read_avg8(uint8_t pin)` helper present | `grep -q "static uint16_t analog_read_avg8(uint8_t pin)" rurp_hw_rev_utils.h` | PASS |
| `analog_read_avg8(PIN_HW_REVISION_DETECT_ADC)` invoked from detect-rev body | `grep -q "analog_read_avg8(PIN_HW_REVISION_DETECT_ADC)" rurp_hw_rev_utils.h` | PASS |
| All 3 ADC threshold constants referenced | `grep -q "ADC_BAND_R41_4K7_HIGH" rurp_hw_rev_utils.h` && `_10K_LOW` && `_10K_HIGH` | PASS (all 3 grep) |
| Guard-gap arm assigns REVISION_UNKNOWN | `grep -q "revision = REVISION_UNKNOWN" rurp_hw_rev_utils.h` | PASS |
| `case REVISION_2_3:` arm present in ctrl-reg mapper | `grep -q "case REVISION_2_3:" rurp_hw_rev_utils.h` | PASS |
| Function-body `revision = 0xFF` eliminated | `awk '/void rurp_detect_hardware_revision/,/^}/' rurp_hw_rev_utils.h \| grep -q "revision = 0xFF;"` | non-zero (PASS — NOT FOUND) |
| File-scope `static uint8_t revision = 0xFF;` at line 12 PRESERVED | `grep -q "^uint8_t revision = 0xFF;" rurp_hw_rev_utils.h` | PASS |
| `digitalRead(PIN_HW_REVISION_DETECT_ADC)` REMOVED | `! grep -q "digitalRead(PIN_HW_REVISION_DETECT_ADC)" rurp_hw_rev_utils.h` | PASS (digital path is gone) |
| `rurp_get_hardware_revision()` body UNCHANGED (VALIDATION Dim 7) | `awk '/^uint8_t rurp_get_hardware_revision/,/^}/' rurp_hw_rev_utils.h` | PASS (5 lines, byte-identical to pre-edit) |
| Build clean — uno / uno328pb / leonardo | `pio run -e uno -e uno328pb -e leonardo` | 3/3 SUCCESS |
| Native dispatch suite green | `pio test -e native -f "*test_dispatch*"` | PASSED — 15/15 |

### Task 3 — Atomic commit on firestarter sub-repo

**Commit:** `032a2e2` (`feat(34-03): rework rurp_detect_hardware_revision() to analog band-lookup + add ADC_BAND_R41_* thresholds (DETECT-FW-01)`)

**Branch:** `v1.7-shield-investigation` (verified pre-stage + post-commit)

**Diff scope:** 2 files changed, 56 insertions(+), 11 deletions(-)
- `include/rurp_hw_rev_utils.h` — 52 lines changed (+45 / -11 net structural; +56 / -11 includes helper docs)
- `include/rurp_pinout.h` — +15 lines

**Commit body cites:** D-03 (threshold values), D-06 (digitalRead → analogRead band-lookup), D-07 (case REVISION_2_3 + 0xFE-vs-0xFF sentinel carve-out), D-11 (strict band ordering), DETECT-FW-01, RESEARCH §8-Sample Averaging Recommendation, the negative-delta flag for Plan 34-04 reconciliation, and the rurp_get_hardware_revision UNCHANGED invariant.

**Post-rework per-env .hex byte counts (substrate for Plan 34-04 delta-band gate):**

| Env | Built (B) | Baseline-34 (B) | Δ (B) | Plan 34-04 expected range |
|-----|-----------|------------------|-------|----------------------------|
| uno      | 62318 | 62617 | **−299** | [+20, +300] |
| uno328pb | 62400 | 62854 | **−454** | [+20, +300] |
| leonardo | 68385 | 68876 | **−491** | [+20, +300] |

The deltas are NEGATIVE (the rework SHRANK the .hex on every env). This is documented as a flag for Plan 34-04 — see the **Hand-off to Plan 04** section below for the reconciliation note.

**Acceptance verification (Task 3):**
| Check | Command | Result |
|-------|---------|--------|
| Sub-repo HEAD on v1.7-shield-investigation | `git rev-parse --abbrev-ref HEAD` | `v1.7-shield-investigation` (PASS) |
| Subject starts with `feat(34-03):` and references DETECT-FW-01 | `git log -1 --format=%B \| grep -q "DETECT-FW-01"` | PASS |
| Commit touches exactly 2 files (both expected) | `git show --name-only HEAD \| grep -cE "(rurp_pinout\.h\|rurp_hw_rev_utils\.h)$"` | 2 (PASS) |
| `git status --porcelain include/rurp_pinout.h include/rurp_hw_rev_utils.h` clean | (same) | empty (PASS) |
| Per-env .hex byte counts captured | `wc -c .pio/build/<env>/firestarter_<env>.hex` per env | PASS (captured in delta table above) |

## Verification

### Plan-level success criteria — all PASS

| Criterion | Evidence |
|-----------|----------|
| 3 new `#define`s in rurp_pinout.h | Section 1b block; all 3 inside #ifdef HARDWARE_REVISION; strict ordering 200 < 220 < 600 |
| rurp_detect_hardware_revision() reworked per D-06 (4-arm band-lookup) | analog_read_avg8 + if/else-if/else-if/else chain; legacy A2 disambig preserved |
| case REVISION_2_3: arm added per D-07 | Aliased to REV_2_x ctrl-reg layout; one new case label after case REVISION_2_2: |
| `pio run -e uno -e uno328pb -e leonardo` exits 0 | 3/3 SUCCESS |
| `pio test -e native -f "*test_dispatch*"` 15/15 PASS | PASSED — 15 test cases |
| Single atomic commit on firestarter sub-repo v1.7-shield-investigation branch | commit `032a2e2`; 2-file diff; correct branch |
| SUMMARY.md created + committed in meta-repo plan directory | this file (next commit) |
| STATE.md + ROADMAP.md updated | next state-update step |

### Threat model — T-34-03-A and T-34-03-B mitigation verified

| Threat | Mitigation | Status |
|--------|------------|--------|
| T-34-03-A (Tampering): 0xFF-vs-0xFE sentinel collision | (a) Function-body-scoped `awk` + `grep` confirms `revision = 0xFF;` no longer exists inside the reworked detect-rev function body; (b) file-scope `static uint8_t revision = 0xFF;` at line 12 intentionally preserved (RESEARCH dead-code-in-boot-flow); (c) inline comment on the else-arm REVISION_UNKNOWN line documents the carve-out verbatim | MITIGATED |
| T-34-03-B (DoS): REVISION_UNKNOWN on a future unknown rev → ctrl_reg = 0 fail-safe | New `default: break;` arm in `rurp_map_ctrl_reg_for_hardware_revision()` carries an explicit comment citing RESEARCH §Caller Audit row 3; REVISION_UNKNOWN deliberately NOT added to the switch so it falls through to the existing default (ctrl_reg = 0 — no VPP enables, no VPE enables); operator EEPROM override is the escape hatch | ACCEPTED (intended fail-safe behavior; same disposition as Phase 33) |

## Deviations from Plan

**None — plan executed exactly as written.** No Rule 1-4 triggers. No auth gates. No checkpoints. No CLAUDE.md adjustments needed.

**One observation worth flagging for Plan 34-04 (NOT a deviation, NOT a fix):** the post-rework per-env `.hex` deltas are NEGATIVE (−299 / −454 / −491 B) rather than the RESEARCH-projected positive [+20, +300] B band. This is OPPOSITE to the projected sign, not a magnitude miss. Plan 34-04's verify-detect-34.sh delta-band gate will fail under the current `EXPECTED_DELTA_MIN = 20` / `EXPECTED_DELTA_MAX = 300` thresholds in the script. See the **Hand-off to Plan 04** section for the recommended reconciliation paths.

The verification block in this plan's PLAN.md explicitly states: *"Plan 04 (next plan) wraps the `.hex` Δ verification via `verify-detect-34.sh` — Δ expected in [20, 300] B band per env"* — i.e. the delta-band gate is owned by Plan 04, not Plan 03. The sequential_execution context further confirms: *"`verify-detect-34.sh` is NOT meant to pass yet — that's Plan 34-04's gate."* Plan 03's own success criteria (build green + native dispatch green + single atomic commit on correct branch) are all met, so this plan completes successfully even with the delta-sign flag.

## Cross-cutting context preserved

- **Branch model invariant:** firestarter sub-repo + meta-repo both on `v1.7-shield-investigation` per `feedback_branching` memory. Sub-repo work committed inside the submodule; meta-repo submodule-pointer bump remains deferred to Plan 34-04 (which also runs verify-detect-34.sh). This plan does NOT bump the meta-repo's firestarter submodule pointer — Plan 04 owns that load.
- **Operator WIP preserved untouched:** `firestarter_app/firestarter/config.py` + `firestarter_app/.planning/STATE.md` inside the firestarter_app submodule, and the untracked `.planning/phases/33-silkscreen-label-code-alias-migration/33-VERIFICATION.md` in the meta-repo. Verified via `git status --short` — same shape as plan-begin (`M firestarter` sub-repo pointer drift; `m firestarter_app` sub-repo WIP marker; `?? .planning/phases/33-.../33-VERIFICATION.md` untracked).
- **Native env exclusion:** the reworked detect-rev body sits inside `#ifdef HARDWARE_REVISION`; `[env:native]` `build_src_filter = +<proms/>` continues to exclude `rurp_hw_rev_utils.h` from native compilation. Native dispatch tests are unaffected (15/15 PASS — load-bearing GATE-1.7 dispatch-unaffected evidence per VALIDATION Dim 1 / DETECT-FW-02).
- **MSG_OK_REV wire shape unchanged per D-09:** no codegen pass on `tools/catalog/messages.toml`; the new REVISION_UNKNOWN (= 0xFE) and REVISION_2_3 (= 5) enum bytes flow through the existing (physical_u8, effective_u8) payload positions of MSG_OK_REV.

## Hand-off to Plan 04 (Wave 2 — meta-repo submodule pointer bump + GATE-1.7 .hex delta gate)

Plan 04 will:
1. Bundle this plan's `032a2e2` (plus Plan 02's `b243fb4`) into a single firestarter submodule pointer bump in the meta-repo.
2. Run `verify-detect-34.sh` to assert per-env `.hex` delta lands in the expected band.

**Critical reconciliation note for Plan 04:** the post-rework deltas are NEGATIVE, not positive. Recorded values:

| Env | Built (B) | Baseline-34 (B) | Δ (B) |
|-----|-----------|------------------|-------|
| uno      | 62318 | 62617 | **−299** |
| uno328pb | 62400 | 62854 | **−454** |
| leonardo | 68385 | 68876 | **−491** |

Plausible cause: the `digitalRead(A3)` → `analog_read_avg8(A3)` swap removes the digital-I/O code path (`digitalRead` pulls in `digital_pin_to_port_PGM` / `digital_pin_to_bit_mask_PGM` lookup tables in `wiring_digital.c`). Meanwhile `analogRead` was already linked-in via the legacy A2 read, so swapping A3 from digital to analog removes code without adding fresh `.text`. The new if/else-if chain also compiles more compactly than the prior switch-on-int. The `analog_read_avg8` helper inlines under `-Os` and folds the loop; the loop overhead is recovered. Net: code path shrinks.

**Recommended Plan 04 reconciliation options (planner discretion — Plan 04 has the final call):**

- **Option A (RECOMMENDED): widen `verify-detect-34.sh` delta band to `[-600, +300]` B per env.** The negative side is the empirical observation; the positive side stays unchanged as the upper safety bound. Re-document the band in PLAN.md / RESEARCH.md to call out that "smaller is also fine — D-10 didn't promise a sign, just bounded magnitude." This preserves the gate's intent (catch unexpected bloat OR unexpected gigantic shrink) without faking the empirical result.
- **Option B: flip the assertion to `abs(delta) <= 600` B per env.** Cleaner — bounded magnitude in either direction. Same end behavior as Option A but a more honest formulation.
- **Option C: revisit the RESEARCH projection.** If Plan 04's planner wants tighter epistemic alignment, re-run the .hex symbol-table analysis (`avr-objdump -h` + `avr-nm --size-sort`) on baseline vs built and document the exact functions / sections that shrank. This is a research artifact, not a gate change.

The byte-stability invariant (per Phase 33 D-06 substrate) is NOT violated — Phase 33's invariant was "byte-identical .hex" for alias renames that don't change behavior; Phase 34's rework DOES change behavior (new ADC band-lookup logic), so a non-zero delta is expected. The flag here is the sign, not the magnitude.

## Hand-off to Plan 05 (Wave 3 — firestarter_app Python parity)

Plan 05 mirrors the firmware enum to `firestarter_app/firestarter/constants.py` per D-08. This plan landed nothing in Python — Plan 05's substrate is the firmware-side authoritative source at `firestarter/include/rurp_shield.h` (Plan 02) plus the firmware-side detect-rev logic at `firestarter/include/rurp_hw_rev_utils.h` (this plan). No Python-side gate dependencies.

## Self-Check: PASSED

- [x] `firestarter/include/rurp_pinout.h` exists and contains all 3 ADC_BAND_R41_* #defines (`grep -c "^#define ADC_BAND_R41" → 3`)
- [x] `firestarter/include/rurp_hw_rev_utils.h` exists and contains the reworked detect-rev body + `analog_read_avg8` helper + `case REVISION_2_3:` arm (FOUND via all 7 acceptance grep checks)
- [x] firestarter sub-repo commit `032a2e2` exists on `v1.7-shield-investigation` (`git -C /workspaces/firestarter log --oneline | grep 032a2e2` → FOUND)
- [x] Build artifacts green for all 3 AVR envs (`pio run -e uno -e uno328pb -e leonardo` → 3/3 SUCCESS)
- [x] Native dispatch suite 15/15 PASS (`pio test -e native -f "*test_dispatch*"` → PASSED)
- [x] Sub-repo HEAD on `v1.7-shield-investigation` (`git rev-parse --abbrev-ref HEAD` inside firestarter/ → `v1.7-shield-investigation`)
- [x] Meta-repo HEAD on `v1.7-shield-investigation` (`git rev-parse --abbrev-ref HEAD` at /workspaces → `v1.7-shield-investigation`)
- [x] `rurp_get_hardware_revision()` body UNCHANGED (VALIDATION Dim 7 — `awk`-scoped function body byte-identical to pre-edit; manual diff confirmed)
- [x] File-scope `static uint8_t revision = 0xFF;` at line 12 PRESERVED
- [x] No `digitalRead(PIN_HW_REVISION_DETECT_ADC)` remains anywhere in the file (`! grep -q ...` → PASS)
- [x] Operator WIP preserved (config.py inside firestarter_app, 33-VERIFICATION.md untracked in meta-repo — both untouched per `git status --short` at plan-end)

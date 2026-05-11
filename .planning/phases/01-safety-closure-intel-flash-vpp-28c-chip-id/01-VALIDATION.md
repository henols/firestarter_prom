---
phase: 1
slug: safety-closure-intel-flash-vpp-28c-chip-id
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-11
approved: 2026-05-11
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source of truth: [01-RESEARCH.md §Validation Architecture](01-RESEARCH.md#validation-architecture).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Unity (PlatformIO `test_framework = unity`) + ArduinoFake@^0.4.0 |
| **Config file** | `firestarter/platformio.ini` `[env:native]` block (no changes needed) |
| **Quick run command (Phase 1 only)** | `cd firestarter && pio test -e native -f "*test_flash_intel_vpp*" -f "*test_eeprom28c_chip_id*"` |
| **Regression run command (dispatch)** | `cd firestarter && pio test -e native -f "*test_dispatch*"` |
| **Full suite command** | `cd firestarter && pio test -e native` |
| **Estimated runtime** | ~10 seconds (native, no hardware) |

---

## Sampling Rate

- **After every task commit:** Run the quick suite that the task edits (`pio test -e native -f "*test_<suite>*"`).
- **After every plan wave:** Run the full native suite (`pio test -e native`) — all 15 dispatch tests + new Phase-1 tests GREEN.
- **Before `/gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** ~10 seconds.

---

## Per-Task Verification Map

> Filled by the planner. Each task in `01-XX-PLAN.md` must reference a Test Type + Automated Command from the table below. Wave 0 tasks must precede any code-change task that depends on them.

| Req ID | Behavior | Test Type | Automated Command | File Exists? | Status |
|--------|----------|-----------|-------------------|--------------|--------|
| SAF-04 | Intel-flash VPP nominal — measured ≈ setpoint, no response_code change | unit | `pio test -e native -f "*test_flash_intel_vpp*"` (`test_flash_intel_vpp_nominal_proceeds`) | ❌ Wave 0 | ⬜ pending |
| SAF-04 | Intel-flash VPP low (< 95% of setpoint) — warning response, no error | unit | same suite (`test_flash_intel_low_vpp_warns`) | ❌ Wave 0 | ⬜ pending |
| SAF-04 | Intel-flash VPP high (> setpoint + 500 mV) — error response, write aborts | unit | same suite (`test_flash_intel_high_vpp_errors`) | ❌ Wave 0 | ⬜ pending |
| SAF-04 | FORCE-flag downgrades high-VPP error to warning | unit | same suite (`test_flash_intel_high_vpp_with_force_warns`) | ❌ Wave 0 | ⬜ pending |
| SAF-04 | REV0 hardware skips ADC compare and warns | unit | same suite (`test_flash_intel_rev0_skips_vpp_check`) | ❌ Wave 0 | ⬜ pending |
| SAF-05 | Matching chip-id proceeds (response_code unchanged after init) | unit | `pio test -e native -f "*test_eeprom28c_chip_id*"` (`test_eeprom28c_matching_chip_id_proceeds`) | ❌ Wave 0 | ⬜ pending |
| SAF-05 | Mismatching chip-id errors (response_code = RESPONSE_CODE_ERROR) | unit | same suite (`test_eeprom28c_mismatching_chip_id_errors`) | ❌ Wave 0 | ⬜ pending |
| SAF-05 | `chip_id == 0` skips the check entirely (no read attempted) | unit | same suite (`test_eeprom28c_zero_chip_id_skips_check`) | ❌ Wave 0 | ⬜ pending |
| SAF-05 | FORCE-flag downgrades mismatch error to warning | unit | same suite (`test_eeprom28c_mismatching_chip_id_with_force_warns`) | ❌ Wave 0 | ⬜ pending |
| SAF-06 (regression guard) | 15 pre-existing dispatch tests still pass byte-identical | unit | `pio test -e native -f "*test_dispatch*"` (assertion: 15/15 GREEN, no test renames) | ✅ exists | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Create the two new native test directories with suite-local stubs. Suite-local mocking is mandatory — `test_dispatch/host_stubs.cpp` must remain byte-identical (D-10).

- [ ] `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` — SAF-04 Unity tests (stubs ok; bodies arrive with SAF-04 task).
- [ ] `firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp` — suite-local stubs with mockable `rurp_read_voltage_mv` + `rurp_get_hardware_revision` via TU-private `static` globals; functionally identical to the dispatch suite's stubs elsewhere.
- [ ] `firestarter/test/native/avr/test_flash_intel_vpp/avr/pgmspace.h` — copy of `test_dispatch/avr/pgmspace.h` (PIO's per-test discovery does not share it).
- [ ] `firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp` — SAF-05 Unity tests (stubs ok; bodies arrive with SAF-05 task).
- [ ] `firestarter/test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp` — suite-local stubs; no `rurp_read_voltage_mv` override needed (mocking happens via the handle's function-pointer fields).
- [ ] `firestarter/test/native/avr/test_eeprom28c_chip_id/avr/pgmspace.h` — copy of `test_dispatch/avr/pgmspace.h`.

*PIO `[env:native]` already exists and needs no edits; `test_build_src = yes` + `src_filter = +<proms/>` pull the production TUs in automatically.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real-hardware Intel-flash VPP low/high path | SAF-04 | Native tests prove the firmware logic; only a RURP shield with a calibrated 12V rail can exercise the actual ADC reading | Deferred to Phase 4 (HW-05). Not required for Phase 1 sign-off per CONTEXT.md `<deferred>`. |
| Real AT28C chip-id read with A9-12V applied | SAF-05 | No DB chip currently sets `chip_id_value` for protocol 0x0D, and the A9-12V path needs a board capable of routing 12V to A9 | Phase 1 ships the firmware path only; activation waits on a DB override + Phase 4 HW validation. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies wired
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all `❌ Wave 0` references above (per 01-01-PLAN.md / 01-02-PLAN.md Wave-0 tasks)
- [x] No watch-mode flags in any test command
- [x] Feedback latency < 15 s
- [x] `test_dispatch/` regression guard (15/15 PASS, byte-identical) included as the phase-gate assertion
- [x] `nyquist_compliant: true` set in frontmatter after planner integration

**Approval:** approved 2026-05-11 (plan-checker verification passed; see commit history)

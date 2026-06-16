---
phase: 71
slug: validation-harness-matrix
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-16
---

# Phase 71 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `71-RESEARCH.md` §Validation Architecture (HIGH confidence).
> Refined 2026-06-16 against the final 6-plan / 2-wave split.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Unity (PlatformIO `[env:native]`, firmware) + pytest 7.x (host) |
| **Config file** | `firestarter/platformio.ini` §`[env:native]`; `firestarter_app/pyproject.toml` |
| **Quick run command** | `pio test -e native -f "*test_dispatch*"` (fw) · `cd firestarter_app && pytest tests/ -x` (host) |
| **Full suite command** | `pio test -e native && cd firestarter_app && pytest tests/ --cov-fail-under=70 && python tools/check_dispatch.py` |
| **Estimated runtime** | ~60–120 seconds (native + host + dispatch gate) |

> ⚠ Devcontainer Python is 3.12 but CI targets py39/3.11 — validate `ruff check` + `ruff format --check` against the target before claiming CI green (see project memory `reference_devcontainer_py312_masks_ci_py39`). The codegen emitter must stay ruff-clean (do NOT hand-normalize generated output — `reference_codegen_ruff_clean_emitter`).

---

## Sampling Rate

- **After every task commit (firmware):** `pio test -e native -f "*test_dispatch*"` (existing regression baseline — proves recording stub flag-off is a no-op)
- **After every task commit (host):** `cd firestarter_app && pytest tests/ -x --cov-fail-under=70 && python tools/check_dispatch.py`
- **After every plan wave:** full `pio test -e native && cd firestarter_app && pytest tests/ --cov-fail-under=70`
- **Before `/gsd-verify-work`:** all Tier-1 + Tier-2 cells GREEN; Tier-3 SKIP-deferred scaffold in place; `check_dispatch.py` exits 0; `pio run -e uno && -e leonardo` flash byte-count unchanged
- **Max feedback latency:** ~120 seconds

---

## Per-Task Verification Map

> Final — task IDs map to the 6-plan / 2-wave split. One row per requirement-behavior from `71-RESEARCH.md` §Phase Requirements → Test Map.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 71-01-T1 | 01 | 1 | HARN-01 (recording stub) | T-71-02, T-71-FLASH | Define-guarded recording buffer added to shared stub; bounded at 256 | unit (build) | `grep HOST_STUBS_RECORD_BUS test/native/avr/_shared/host_stubs_common.inc` | ❌ W0 | ⬜ pending |
| 71-01-T2 | 01 | 1 | HARN-01 (Tier-1 regression) | T-71-FLASH | Existing suites compile unchanged with flag off (no-op); zero production flash | regression (Unity) | `pio test -e native -f "*test_dispatch*"` + `pio run -e uno -e leonardo` | ✅ | ⬜ pending |
| 71-02-T1 | 02 | 1 | HARN-02 | T-71-INPUT, T-71-CONFUSE | Authored matrix JSON enumerates 6 families; validate_spec raises on malformed; input distinct from emitted artifact | unit (pytest) | `pytest tests/test_matrix_schema.py -x` | ❌ W0 | ⬜ pending |
| 71-02-T2 | 02 | 1 | HARN-02 | T-71-DRIFT | Codegen emits committed C++ header; byte-identical re-generation (drift gate) | unit (pytest) | `pytest tests/test_gen_validation_header.py -x` | ❌ W0 | ⬜ pending |
| 71-03-T1 | 03 | 1 | HARN-04 | T-71-VPP, T-71-INTEL | Per-family VPP invariants active; non-VPP families never see `vpp_mv > 6000`; gate green on clean DB | integration (script) | `python tools/check_dispatch.py` | ✅ (extend) | ⬜ pending |
| 71-03-T2 | 03 | 1 | HARN-04 | T-71-ROGUE | `non_supported_dispatchable` populated; gate FAILS on a synthetic mis-dispatch / VPP-mismatch fixture (non-vacuous) | unit (pytest) | `pytest tests/test_check_dispatch_invariants.py -x` | ❌ W0 | ⬜ pending |
| 71-04-T1 | 04 | 2 | HARN-01 (Tier-1) | T-71-VACUOUS, T-71-WIRED-WRONG | 5 family suites prove VPP/non-VPP CTL side-effect; VPP families carry a negative-control read | unit (Unity) | `pio test -e native -f "*test_val_eprom*"` (+ flash_intel/eeprom28c/flash3/flash4) | ❌ W0 | ⬜ pending |
| 71-04-T2 | 04 | 2 | HARN-01 (Tier-1 SRAM) | T-71-SRAM-FALSE | SRAM suite asserts `bus_recording_count()==0` (documented no-op; VAL-06 deferred to P73) | unit (Unity) | `pio test -e native -f "*test_val_sram*"` | ❌ W0 | ⬜ pending |
| 71-04-T3 | 04 | 2 | HARN-01 (Tier-1 wiring) | T-71-FLASH | All 6 suites in positive test_filter allowlist; full native battery green; zero production flash | regression (Unity) | `pio test -e native` + `pio run -e leonardo` | ❌ W0 | ⬜ pending |
| 71-05-T1 | 05 | 2 | HARN-01 (Tier-2) | T-71-WIREDRIFT | Host wire dict for eprom/eeprom28c/flash3/flash4/flash_intel dispatches to correct handler (no serial port) | unit (pytest) | `pytest tests/test_val_wire_eprom.py … -x` | ❌ W0 | ⬜ pending |
| 71-05-T2 | 05 | 2 | HARN-01 (Tier-2 SRAM) | T-71-SRAM-EPROM | SRAM rep chip dispatches to configure_sram AND never configure_eprom (BLOCKER-2) | unit (pytest) | `pytest tests/test_val_wire_sram.py -x` | ❌ W0 | ⬜ pending |
| 71-06-T1 | 06 | 2 | HARN-01 (Tier-3) + HARN-02 | T-71-FORGE | `dev validate-family` composes cycle methods; SKIP-deferred when no board; emits distinct results artifact | integration (pytest) | `pytest tests/test_validate_family_cmd.py tests/test_matrix_artifact.py -x` | ❌ W0 | ⬜ pending |
| 71-06-T2 | 06 | 2 | HARN-03 | T-71-VACUOUS | Negative control returns FAIL (verify *can* fail) | unit (pytest) | `pytest tests/test_validate_oracle.py::test_negative_control -x` | ❌ W0 | ⬜ pending |
| 71-06-T2 | 06 | 2 | HARN-03 | T-71-UNO328 | `uno328pb` cells hard-coded N/A; no write cycle attempted | unit (pytest) | `pytest tests/test_validate_oracle.py::test_uno328pb_na -x` | ❌ W0 | ⬜ pending |
| 71-06-T2 | 06 | 2 | HARN-03 | T-71-STALECAL | r1 ≈ 270000 ±25% precondition aborts the write path before any cycle | unit (pytest) | `pytest tests/test_validate_oracle.py::test_r1_precondition_aborts -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/test/native/avr/_shared/host_stubs_common.inc` — add `#define HOST_STUBS_RECORD_BUS` guarded recording buffer (D-04, single-edit-point) — **Plan 01**
- [ ] `firestarter_app/tools/validation_matrix_spec.json` — authored matrix source (D-01) — **Plan 02**
- [ ] `firestarter_app/tools/gen_validation_header.py` — codegen entrypoint → C++ header (D-01) — **Plan 02**
- [ ] `firestarter/test/native/avr/_shared/validation_matrix.h` — GENERATED, committed header — **Plan 02**
- [ ] `firestarter_app/tools/check_dispatch.py` — per-family VPP invariants + populated `non_supported_dispatchable` (HARN-04) — **Plan 03**
- [ ] `firestarter/test/native/avr/test_val_{eprom,eeprom28c,flash3,flash4,flash_intel,sram}/` — 6 Tier-1 native suites + `platformio.ini` allowlist (HARN-01) — **Plan 04**
- [ ] `firestarter_app/tests/test_val_wire_*.py` — 6 Tier-2 host wire round-trip files (HARN-01) — **Plan 05**
- [ ] `firestarter_app/tests/test_validate_family_cmd.py` + `test_matrix_artifact.py` — Tier-3 runner scaffold + artifact (HARN-01/02) — **Plan 06**
- [ ] `firestarter_app/tests/test_validate_oracle.py` — HARN-03 (negative control + uno328pb N/A + r1 precondition) — **Plan 06**
- [ ] `firestarter_app/tests/test_matrix_schema.py`, `test_gen_validation_header.py`, `test_check_dispatch_invariants.py` — Plans 02/03

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Tier-3 HIL real cell evidence (post-write read+SHA on Leonardo, live r1≈270000 calibration) | HARN-03 (oracle, full proof) | Requires physical board + chip; deferred to Phase 73 by D-06/D-07 — Phase 71 records SKIP-deferred cells | Phase 73: run `dev validate-family` on bench with Leonardo/ACM0; software tiers in Phase 71 use deliberate-mismatch / mocked-r1 assertions, not real hardware |

*Phase 71 is software-first/flash-free by design — all Tier-1 and Tier-2 cells are automated; the only manual surface (Tier-3 real-hardware evidence) is explicitly deferred to Phase 73.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 120s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** planned (6 plans, 2 waves)

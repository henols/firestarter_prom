---
phase: 44
slug: bug-a-rca-modified-rev-0-upper-address-jitter
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-29
---

# Phase 44 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: 44-RESEARCH.md § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Unity (PlatformIO native) for firmware + pytest for host |
| **Config file** | `firestarter/platformio.ini` (`[env:native]`) + `firestarter_app/pyproject.toml` |
| **Quick run command** | `pio test -e native -f "*test_read_timing*"` (firmware) / `pytest tests/ -x -q` (host) |
| **Full suite command** | `pio test -e native` (firmware) + `pytest tests/ --cov-fail-under=70` (host) |
| **Estimated runtime** | ~30 seconds (native) / ~20 seconds (host) |

---

## Sampling Rate

- **After every task commit:** Run the quick command for the side touched — `pio test -e native` (firmware) or `pytest tests/ -x -q` (host)
- **After every plan wave:** Both suites green + `pio run -e leonardo` succeeds (flash budget check)
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD (knob parse) | TBD | 1 | RCA-01 | T-44-01 (int overflow → cap) | `read_settling_us` / `read_strobe_us` parsed from JSON, stored in handle, bounds-capped | unit (native) | `pio test -e native -f "*test_read_timing*"` | ❌ W0 | ⬜ pending |
| TBD (read-path apply) | TBD | 1 | RCA-01 | — | Settling delay applied BETWEEN `firestarter_set_address()` and `rurp_chip_enable()`; strobe width replaces hardcoded 3µs | unit (native) | `pio test -e native -f "*test_read_timing*"` | ❌ W0 | ⬜ pending |
| TBD (host sweep params) | TBD | 1 | RCA-01 | — | `consistency_check_eprom()` accepts + emits `read_settling_us` / `read_strobe_us` in JSON, no re-flash | unit (pytest) | `pytest tests/test_eprom_operations.py -x -q -k "read_timing"` | ❌ W0 | ⬜ pending |
| TBD (baseline repro) | TBD | 2 | RCA-01 / D-11 | — | Fresh N=5 run byte-compares against Phase 29 v2 binaries; jitter present (WORST ≥ 1% zeros) | manual / bench | Operator-run + cross-check script | ✅ (script pattern in EVIDENCE.md) | ⬜ pending |
| TBD (causal sweep) | TBD | 2 | RCA-01 | — | A timing knob drives upper-address jitter toward ~zero (D-06 causal bar) | manual / bench | Operator-witnessed sweep session | manual-only | ⬜ pending |
| TBD (static check) | TBD | 2 | RCA-03 (partial) | — | Modified Rev 0 mods traced + documented; per-rev map entry written | manual / bench | Operator inspection + doc write | manual-only | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Task IDs are TBD until the planner assigns plan/wave numbers; the planner MUST update this map.*

---

## Wave 0 Requirements

- [ ] `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp` — Unity tests asserting `read_settling_us` and `read_strobe_us` are parsed from JSON and stored in `firestarter_handle_t` (template: `test/native/avr/test_data_input/`)
- [ ] `firestarter/test/native/avr/test_read_timing/host_stubs.cpp` — stubs for `rurp_*` symbols (same pattern as `test_data_input/host_stubs.cpp`)
- [ ] `tests/test_eprom_operations.py` — pytest cases for new `read_settling_us` / `read_strobe_us` params in `consistency_check_eprom()` signature and JSON command emission

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| D-11 baseline byte-compare against Phase 29 v2 binaries | RCA-01 | Requires Modified Rev 0 shield + W27C512 + Leonardo on the bench (operator-only per D-09) | Run `firestarter dev consistency-check` N=5 on same board/chip/port; cross-check SHA/zeros against `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-155021-v2/` |
| Causal sweep — knob drives jitter to ~zero | RCA-01 | Bench hardware + operator-witnessed LA/scope per D-05/D-09 | Sweep 2D (settling × strobe) with chip seated, no re-flash; record jitter metric per point |
| Static circuit inspection (D-01/D-02) | RCA-03 (partial) | Physical multimeter/probe/photo work is operator-only | Trace Modified Rev 0 cuts/jumpers vs upstream Rev 0 schematic; record in v1.7 shield docs |

---

## Validation Sign-Off

- [ ] All firmware/host code tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive automatable tasks without automated verify
- [ ] Wave 0 covers all MISSING references (new native test + pytest cases)
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter after planner wires task IDs

**Approval:** pending

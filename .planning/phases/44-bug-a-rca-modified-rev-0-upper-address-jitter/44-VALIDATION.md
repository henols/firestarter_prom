---
phase: 44
slug: bug-a-rca-modified-rev-0-upper-address-jitter
status: planned
nyquist_compliant: true
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
| **Quick run command** | `pio test -e native -f "*test_read_timing*"` (firmware) / `pytest tests/ -x -q -k read_timing` (host) |
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
| 44-01-T1 (fork off beta) | 44-01 | 1 | RCA-03 | T-44-01-GP | v1.9 branches forked off beta; shield docs present | shell assert | `cd firestarter && test "$(git branch --show-current)" = v1.9-read-bug-rca` | n/a (git) | ⬜ pending |
| 44-01-T2 (recover shield doc) | 44-01 | 1 | RCA-03 | — | v1.7-SHIELD-REVS.md recovered to meta working tree | shell assert | `grep -q "Modified Rev 0" .planning/v1.7-SHIELD-REVS.md` | ❌ recover | ⬜ pending |
| 44-02-T1 (W0 native tests) | 44-02 | 2 | RCA-01 | T-44-01 | RED native suite for knob parse + cap | unit (native) | `pio test -e native -f "*test_read_timing*"` (RED) | ❌ W0 | ⬜ pending |
| 44-02-T2 (knob impl + cap) | 44-02 | 2 | RCA-01 | T-44-01 | knobs parsed, applied at correct call sites, bounds-capped | unit (native) | `pio test -e native -f "*test_read_timing*"` + `pio run -e leonardo` | ❌ W0 | ⬜ pending |
| 44-03-T1 (W0 host tests) | 44-03 | 2 | RCA-01 | T-44-03 | RED pytest for host param emission + key-string match | unit (pytest) | `pytest tests/test_eprom_operations.py -x -q -k read_timing` (RED) | ❌ W0 | ⬜ pending |
| 44-03-T2 (host knobs + CLI) | 44-03 | 2 | RCA-01 | T-44-03 | consistency_check_eprom emits knobs; CLI options exposed | unit (pytest) | `pytest tests/test_eprom_operations.py -x -q -k read_timing` | ❌ W0 | ⬜ pending |
| 44-03-T3 (sweep harness) | 44-03 | 2 | RCA-01 | — | 2D sweep harness, no sideload (D-05) | static (ast) | `python -c "import ast; ast.parse(open('.../sweep_bug_a.py').read())"` | ❌ new | ⬜ pending |
| 44-04-T1 (static check) | 44-04 | 3 | RCA-03 | T-44-04 | Modified Rev 0 mods traced + hypothesis formed (D-01/D-02) | manual / bench | Operator inspection + doc write | manual-only | ⬜ pending |
| 44-04-T2 (baseline repro) | 44-04 | 3 | RCA-01 / D-11 | T-44-05 | N=5 byte-compare vs Phase 29 v2; Bug A pattern present | manual / bench | Operator-run + `compare_to_baseline()` cross-check | ✅ (script in Plan 03) | ⬜ pending |
| 44-05-T1 (causal sweep) | 44-05 | 4 | RCA-01 | T-44-06 | knob drives upper-address jitter toward ~zero (D-06) | manual / bench | Operator-witnessed `sweep_bug_a.py` session | ✅ (harness) | ⬜ pending |
| 44-05-T2 (findings + map) | 44-05 | 4 | RCA-01 / RCA-03 | — | RCA-01 conclusion + per-rev map started (D-10) | shell assert | `grep -q "Rev 2.2" .../44-RCA-FINDINGS.md` | ❌ new | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp` — Unity tests asserting `read_settling_us` and `read_strobe_us` are parsed from JSON, stored in `firestarter_handle_t`, default to 0 when absent, and are capped (T-44-01). Template: `test/native/avr/test_dispatch/`. **Owned by 44-02 Task 1.**
- [ ] `firestarter/test/native/avr/test_read_timing/host_stubs.cpp` + `avr/pgmspace.h` — copy from `test_dispatch/`. **Owned by 44-02 Task 1.**
- [ ] `tests/test_eprom_operations.py` — pytest cases for new `read_settling_us` / `read_strobe_us` params in `consistency_check_eprom()` signature, conditional JSON emission, and constant-string match. **Owned by 44-03 Task 1.**

---

## Manual-Only Verifications

| Behavior | Requirement | Plan/Task | Why Manual | Test Instructions |
|----------|-------------|-----------|------------|-------------------|
| Static circuit inspection (D-01/D-02) | RCA-03 (partial) | 44-04 T1 | Physical multimeter/probe/photo work is operator-only (D-09) | Trace Modified Rev 0 cuts/jumpers vs upstream Rev 0 schematic; multimeter A15 termination + data-bus pull-downs + VPP + VCC sag; record hypothesis |
| D-11 baseline byte-compare vs Phase 29 v2 binaries | RCA-01 | 44-04 T2 | Requires Modified Rev 0 shield + W27C512 + Leonardo on the bench | N=5 `dev consistency-check` default knobs; `compare_to_baseline()` vs `W27C512-leonardo-20260526-155021-v2/` |
| Causal sweep — knob drives jitter to ~zero | RCA-01 | 44-05 T1 | Bench hardware + operator-witnessed LA/scope per D-05/D-09 | `sweep_bug_a.py` 2D (settling × strobe), chip seated, no re-flash; record jitter per point + LA A15-vs-/CE |

---

## Validation Sign-Off

- [x] All firmware/host code tasks have `<automated>` verify or Wave 0 dependencies (44-02, 44-03)
- [x] Sampling continuity: no 3 consecutive automatable tasks without automated verify (each code task has a native/pytest/ast command)
- [x] Wave 0 covers all MISSING references (new native test + pytest cases — 44-02 T1, 44-03 T1)
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter after planner wired task IDs

**Approval:** planned — task IDs wired to plans 44-01..44-05.

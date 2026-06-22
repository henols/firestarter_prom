---
phase: 78
slug: x88c64-0x34-firmware-handler
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-22
---

# Phase 78 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from 78-RESEARCH.md §"Validation Architecture". Two-branch phase:
> **Branch A (deferral, expected)** = documentation only, no code; **Branch B
> (handler-write, contingency)** = firmware + native tests, graduation still
> hardware-blocked (D-04).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Firmware native = Unity (PlatformIO `[env:native]`); Host = pytest |
| **Config file** | `firestarter/platformio.ini`; `firestarter_app/pyproject.toml` |
| **Quick run command** | `pio test -e native` (from `firestarter/`) / `pytest` (from `firestarter_app/`) |
| **Full suite command** | `pio test -e native && pio run -e leonardo` (firmware) + `pytest && ruff check --target-version py39` (host) |
| **Estimated runtime** | ~60–120 seconds (native suites + Leonardo build) |

---

## Sampling Rate

- **After every firmware task commit:** Run `pio test -e native` (all native suites)
- **After every host task commit:** Run `pytest` + `ruff check --target-version py39 --select I` (3.12-masks-CI trap)
- **Phase gate (Branch A — deferral):** No firmware changes; host tests green; `check_dispatch.py` green (no DB change).
- **Phase gate (Branch B — handler-write):** `pio test -e native` green + `pio run -e leonardo` ≤ ~90% flash + `pytest` green + `check_dispatch.py` green + `constants.py` ↔ `firestarter.h` parity green.
- **Before `/gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** ~120 seconds.

---

## Per-Task Verification Map

> Task IDs are illustrative until plans are finalized; the planner maps each task to one of these requirement rows.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 78-01-* | 01 | 1 | XIC-01 | T-78-03 | A6 verdict recorded with line-cited trace evidence; no speculative bit reuse | docs/trace | — (review of X88C64-FEASIBILITY.md) | ✅ | ⬜ pending |
| 78-02-* (B) | 02 | 2 | XIC-02 | T-78-01 | 0x34 dispatch routes to `configure_x88c64`, BEFORE the `protocol != 0` guard | native dispatch | `pio test -e native -f "*test_dispatch*"` | ❌ W0 | ⬜ pending |
| 78-02-* (B) | 02 | 2 | XIC-02 | T-78-01 | configure phase sets NO VPP-enable bits; ALE/WR register order correct | native recording-stub | `pio test -e native -f "*test_val_x88c64*"` | ❌ W0 | ⬜ pending |
| 78-02-* (B) | 02 | 2 | XIC-03 | — | Leonardo flash ≤ ~90% | build measurement | `pio run -e leonardo` (read Flash % line) | ✅ | ⬜ pending |
| 78-XX (B) | — | — | XIC-04 | T-78-02 | N≥5 write+read-back SHA-match + negative control | Tier-3 bench | Manual — Leonardo + X88C64P + DIP24→DIP32 adapter | ❌ | ⬜ blocked (HW) |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky · ⬜ blocked (HW) = hardware-gated, not run this phase*

---

## Wave 0 Requirements

**Branch A (deferral — expected landing):** None — no code files created; only `X88C64-FEASIBILITY.md` updated with the A6 verdict + future-unblock spec. Existing host/firmware infrastructure covers all provable behavior.

**Branch B (handler-write — contingency, only if A6 finds a free bit):**
- [ ] `firestarter/src/proms/eeprom_x88c64.cpp` — new file (configure + write functions)
- [ ] `firestarter/include/eeprom_x88c64.h` — new header
- [ ] `firestarter/test/native/avr/test_val_x88c64/test_val_x88c64.cpp` — new recording-stub test suite (model on `test_val_flash4`)
- [ ] `firestarter/test/native/avr/test_val_x88c64/host_stubs.cpp` — `#define HOST_STUBS_RECORD_BUS`
- [ ] `firestarter_app/firestarter/data/pinouts.json` — `DIP24_X88C64` entry (A7 planner decision = dedicated pinout, recommended)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| N≥5 write + read-back SHA-match + non-vacuous negative control | XIC-04 | No physical X88C64P chip and no DIP24→DIP32 adapter on hand (D-04) — graduation is hardware-blocked this phase regardless of the ALE verdict | DEFERRED to FUT-01: with Leonardo + X88C64P + adapter, run write→read-back→SHA-compare ≥5×; confirm a blank/wrong-data negative control fails; ASK which silkscreen shield rev is mounted; verify `r1 ≈ 270000` and `controller:` port identity first |

*The SC#4 graduation flip (`support_status`→`supported` + `resolve_chip` host-guard removal) is NOT performed this phase per D-04/D-05.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or are explicitly hardware-gated/deferral-branch
- [ ] Sampling continuity: no 3 consecutive code tasks without automated verify (Branch B)
- [ ] Wave 0 covers all MISSING references (Branch B)
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter (after planner maps tasks)

**Approval:** pending

---
phase: 21
slug: firmware-target-uno328pb
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-20
---

# Phase 21 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | PlatformIO + Unity (firmware native suite) |
| **Config file** | `firestarter/platformio.ini` (with new `[env:uno328pb]`) |
| **Quick run command** | `cd firestarter && pio test -e native -f test_dispatch -f test_messages` |
| **Full suite command** | `cd firestarter && pio test -e native` |
| **Estimated runtime** | ~15 seconds native tests; ~30 seconds added `pio run -e uno328pb` build |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter && pio run -e uno328pb` (build sanity) and the relevant subset of native tests
- **After every plan wave:** Run `cd firestarter && pio test -e native` (full native suite) AND `cd firestarter && pio run -e uno -e leonardo -e uno328pb` (matrix build)
- **Before `/gsd-verify-work`:** Full suite + matrix build must be green; `firestarter_uno328pb.hex` must exist and contain the literal `uno328pb` symbol
- **Max feedback latency:** ~45 seconds (build + tests)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 21-XX-XX | TBD | 1 | FW-01..FW-04 | — | N/A (firmware build target only) | build + unit | `cd firestarter && pio run -e uno328pb && pio test -e native` | ❌ W0 (uno328pb env) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Per-task rows will be filled in by the planner once PLAN.md files are emitted.*

---

## Wave 0 Requirements

- [ ] `firestarter/platformio.ini` — `[env:uno328pb]` section
- [ ] `firestarter/scripts/name_firmware.py` (or equivalent pre-build hook) — emits `firestarter_uno328pb.hex` when `board = uno328pb`
- [ ] Macro guards widened from `__AVR_ATmega328P__` to also accept `__AVR_ATmega328PB__` / `ARDUINO_AVR_ATmega328PB` in the 4 grep-verified sites (CONTEXT D-01)
- [ ] Native test envs (`[env:native]`) unchanged — Phase 21 must not regress `test_dispatch` / `test_messages`

*If a custom `boards/uno328pb.json` is needed (CONTEXT D-05 Path A), it must exist before the first `pio run -e uno328pb`. If Path B (use PIO's stock `ATmega328PB`), no file creation needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GATE-1.5 hex byte-identity (uno + leonardo baselines) | FW-01 (regression guard) | Requires comparing two `.hex` files built at different commits; not part of PIO test runner | `cd firestarter && pio run -e uno -e leonardo && shasum .pio/build/uno/firestarter*.hex .pio/build/leonardo/firestarter*.hex` against baseline captured at `5fd751e` before any version-bump |
| Handshake `<board>` slot returns literal `uno328pb` on real hardware | FW-04 | No ATmega328PB hardware on desk for Phase 21; static-analysis substitute is sufficient | Phase 22+ on actual board: `firestarter info` shows board = uno328pb. Phase 21 substitute: `avr-objdump -j .rodata -s .pio/build/uno328pb/firmware.elf \| grep -a uno328pb` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (`[env:uno328pb]` is new; no existing harness covers it)
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter (after planner fills per-task rows)

**Approval:** pending

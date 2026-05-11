---
phase: 12
slug: close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-11
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware)** | Unity 2.x (present in `.pio/libdeps/native/Unity/`) |
| **Framework (Python)** | Plain Python script — pytest not installed |
| **Config file** | `firestarter/platformio.ini` — Wave 0 adds `[env:native]` |
| **Quick run command** | `python3 firestarter_app/tools/check_dispatch.py` |
| **Full suite command** | `pio run -e uno && pio run -e leonardo && python3 firestarter_app/tools/check_dispatch.py && pio test -e native` |
| **Estimated runtime** | ~60 seconds (firmware builds dominate) |

---

## Sampling Rate

- **After every task commit:** Run `python3 firestarter_app/tools/check_dispatch.py` (<1s)
- **After every plan wave:** Run firmware builds + regression scan
- **Before `/gsd-verify-work`:** Full suite (including `pio test -e native`) must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 0 | REQ-SER-01 | — / BLOCKER-2 (electrical safety) | check_dispatch.py asserts all chips reach a real handler and SRAM never reaches configure_eprom | regression | `python3 firestarter_app/tools/check_dispatch.py` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | REQ-FW-01..04 | — | `[env:native]` added; dispatch tests run | infra | `pio test -e native` (after env exists) | ❌ W0 | ⬜ pending |
| TBD | TBD | 1+ | REQ-FW-01 | — | configure_eprom reached for 0x07/0x08/0x0B | unit | `pio test -e native -f test_dispatch` | ❌ W0 | ⬜ pending |
| TBD | TBD | 1+ | REQ-FW-04 | — | configure_flash3 reached for 0x06 | unit | `pio test -e native -f test_dispatch` | ❌ W0 | ⬜ pending |
| TBD | TBD | 1+ | REQ-FW-02/03 | — | configure_flash4 reached for 0x05/0x35 | unit | `pio test -e native -f test_dispatch` | ❌ W0 | ⬜ pending |
| TBD | TBD | 1+ | BLOCKER-2 | electrical-safety | configure_sram reached for 0x0E/0x27/0x28/0x29; configure_eprom never reached | unit | `pio test -e native -f test_dispatch` | ❌ W0 | ⬜ pending |
| TBD | TBD | 1+ | REQ-SER-01 | — | _map_data maps algorithm→mem_type per D3 table | unit/script | `python3 firestarter_app/tools/check_dispatch.py` | ❌ W0 | ⬜ pending |
| TBD | TBD | last | AC-7 | — | Both Uno + Leonardo firmware build clean | smoke | `pio run -e uno && pio run -e leonardo` | existing | ⬜ pending |

*Per-task IDs are placeholders until PLAN.md is generated. Plan-checker / executor MUST replace `TBD` rows with the actual `{phase}-{plan}-{task}` IDs from the generated plans.*

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tools/check_dispatch.py` — Python regression scan covering REQ-SER-01, BLOCKER-1, BLOCKER-2 (iterates `minipro_complete_db.json`, asserts every `(type, algorithm)` pair has a valid firmware dispatch target, asserts SRAM chips never produce a configuration that routes to configure_eprom)
- [ ] `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — Unity tests for `configure_memory` dispatch on every protocol in `KNOWN_PROTOCOLS` (positive and negative cases — `protocol=0` falls through to mem_type, unknown protocol still produces the error)
- [ ] `[env:native]` section added to `firestarter/platformio.ini` — required for `pio test -e native`. Mirror Unity + ArduinoFake from existing `.pio/libdeps/native/` deps; `platform = native`; no upload target.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `firestarter/CLAUDE.md` dispatch table matches new code | AC-8 | Doc-source drift check; no automated parser for the table | Diff the documented order against `memory.cpp:configure_memory` source order; verify line-by-line correspondence |
| `TYPE_FLASH_TYPE_2` constant removed | AC-6 | Single-line code review | `grep -n "TYPE_FLASH_TYPE_2" firestarter/src/proms/memory.cpp` must return no matches |
| AVR binary-size delta documented | AC-7 | Reading `pio run` build output | Capture flash usage from `pio run -e uno` build log pre- and post-phase; record delta in SUMMARY.md |
| Hardware verification | (gated to future phase) | No hardware available in this env per D7 | DEFERRED — future hardware-test phase |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (`check_dispatch.py`, `test_configure_memory.cpp`, `[env:native]`)
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

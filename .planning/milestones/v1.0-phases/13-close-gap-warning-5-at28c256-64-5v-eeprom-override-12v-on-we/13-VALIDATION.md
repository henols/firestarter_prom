---
phase: 13
slug: close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-11
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (Python regression)** | Plain stdlib `check_dispatch.py` (no pytest — established in Phase 12) |
| **Framework (firmware)** | Unity 2.x via PlatformIO `[env:native]` |
| **Config file** | `firestarter/platformio.ini` (existing `[env:native]` from Phase 12) |
| **Quick run command** | `python3 firestarter_app/tools/check_dispatch.py` |
| **Full suite command** | `python3 firestarter_app/tools/check_dispatch.py && cd firestarter && pio test -e native -f "*test_dispatch*" && pio run -e uno && pio run -e leonardo` |
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
| TBD | TBD | 0 | REQ-SAF-01 / REQ-FW-03 | WARNING-5 (electrical safety) | check_dispatch.py asserts no chip with `pinout=DIP28_2764 + algo=0x07 + electrical.type='Flash/EEPROM'` routes to `configure_eprom`. Initially FAILS with 23 violations. | regression | `python3 firestarter_app/tools/check_dispatch.py` | existing (extend) | ⬜ pending |
| TBD | TBD | 1 | REQ-SAF-01 / REQ-FW-03 | WARNING-5 | `build_db.py` flips matching chips to algorithm=0x0D with electrical.type='EEPROM' (or analogous safe value). Regenerated DB has 23 chips with algorithm=0x0D that previously had algorithm=0x07. | source change | manual review | n/a | ⬜ pending |
| TBD | TBD | 2 | REQ-SAF-01 / REQ-FW-03 | WARNING-5 | Regression scan PASSes after DB regenerate. | regression | `python3 firestarter_app/tools/check_dispatch.py` | existing | ⬜ pending |
| TBD | TBD | 2 | (regression) | — | Existing Unity dispatch tests 15/15 still GREEN (no firmware change, no test churn). | unit | `pio test -e native -f "*test_dispatch*"` | existing | ⬜ pending |
| TBD | TBD | 2 | (regression) | — | Both AVR firmware targets build clean (no firmware change). | smoke | `pio run -e uno && pio run -e leonardo` | existing | ⬜ pending |
| TBD | TBD | 3 | (doc) | — | `firestarter_app/CLAUDE.md` documents the WARNING-5 override. | doc | manual review | n/a | ⬜ pending |

*Per-task IDs are placeholders until PLAN.md is generated.*

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Extend `firestarter_app/tools/check_dispatch.py` with a new guard:
  - Scan every chip in `minipro_complete_db.json`.
  - Identify hazardous chips: `pinout=DIP28_2764 AND algorithm=0x07 AND electrical.type=='Flash/EEPROM'`.
  - For each hazardous chip, simulate `dispatch(protocol, mem_type)` (existing helper).
  - Assert dispatch target is `configure_eeprom28c`, NOT `configure_eprom`.
  - On violation: append to `dip28_hazard_violations` list, print summary, exit 1.
  - Mirror the existing `_SRAM_PROTOCOLS` guard pattern (Phase 12 Plan 01).
- [ ] Wave-0 exit gate: `check_dispatch.py` exits **1** with "FAIL: N DIP28_2764 Flash/EEPROM chips route to configure_eprom" before Wave 1 begins (proves the assertion catches the hazard).

*(No new test framework needed; no firmware test changes needed; the existing 15-test Unity suite continues to apply.)*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `firestarter_app/CLAUDE.md` documents the WARNING-5 override | (doc completeness) | No automated parser for prose documentation | Diff CLAUDE.md against the source change; verify a paragraph or section explains the override condition and the 23-chip impact. |
| AVR binary-size delta is zero (no firmware change expected) | n/a | Sanity check — `pio run` output | Compare `pio run -e uno` and `pio run -e leonardo` flash usage pre- and post-phase. Expect delta = 0 bytes (this phase is data-only). |
| Hardware verification | (gated to future phase) | No hardware available | DEFERRED — future hardware-test phase to verify AT28C256 actually writes successfully via the 0x0D handler on a real RURP shield. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (`check_dispatch.py` assertion extension)
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 lands

**Approval:** pending

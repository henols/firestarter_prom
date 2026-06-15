---
phase: 70
slug: v1-11-v1-12-db-pipeline-integration-for-beta-merge
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-15
---

# Phase 70 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (firestarter_app) + PlatformIO native tests (firestarter firmware) |
| **Config file** | `firestarter_app/pyproject.toml` (`.[test]` extra); `firestarter/platformio.ini` |
| **Quick run command** | `cd firestarter_app && python -m pytest tests/ -q` |
| **Full suite command** | `cd firestarter_app && python -m pytest && ruff check . && ruff format --check . && mypy firestarter` |
| **Estimated runtime** | ~60–120 seconds (host suite); firmware native tests separate |

---

## Sampling Rate

- **After every task commit:** Run quick `pytest` for the touched module
- **After every plan wave:** Run full suite + ruff + mypy + coverage floor
- **Before `/gsd-verify-work`:** Full suite + both diff stages (D-04) + GATE-03 must be green
- **Max feedback latency:** ~120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 70-XX-XX | XX | X | SC#X | T-70-XX / — | {filled during planning} | {unit/integration} | `{command}` | ✅ / ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Map filled in by the planner / Nyquist audit against SC#1..SC#6.*

---

## Wave 0 Requirements

*Existing infrastructure (pytest + ruff + mypy + PlatformIO native tests) covers all phase
verification surfaces; no new framework install expected. Wave 0 needs confirmed only if the
regenerated `chip_database.json` requires new snapshot/golden fixtures — planner to decide.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Firmware build (uno + leonardo) + native dispatch tests | SC#6 / D-06 | Requires PlatformIO toolchain; not part of host pytest | `cd firestarter && pio run -e uno && pio run -e leonardo && pio test -e native` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

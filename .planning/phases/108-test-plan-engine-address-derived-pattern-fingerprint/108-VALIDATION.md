---
phase: 108
slug: test-plan-engine-address-derived-pattern-fingerprint
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-02
---

# Phase 108 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (firestarter_app) |
| **Config file** | firestarter_app/pyproject.toml (`[tool.pytest.ini_options]`) |
| **Quick run command** | `cd firestarter_app && python -m pytest tests/test_chip_test.py -q` |
| **Full suite command** | `cd firestarter_app && python -m pytest -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter_app && python -m pytest tests/test_chip_test.py -q`
- **After every plan wave:** Run `cd firestarter_app && python -m pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| {N}-01-01 | 01 | 1 | REQ-{XX} | — | N/A | unit | `{command}` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tests/test_chip_test.py` — stubs for SWEEP-01/02/03/04, PATT-01/02, RPT-03
- [ ] `firestarter_app/tests/conftest.py` — reuse `make_app_context()` + `Mock(spec=EpromOperator)` fixture pattern from `test_validate_family_cmd.py`

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | Engine is fully bench-free this phase (mock operator + `EpromDatabase(skip_local_override=True)`) | All phase behaviors have automated verification. |

*If none: "All phase behaviors have automated verification."*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

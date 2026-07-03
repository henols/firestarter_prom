---
phase: 114
slug: disposition-no-auto-graduate-lock-graduation-ladder-inbox-re
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-03
---

# Phase 114 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (firestarter_app) |
| **Config file** | `firestarter_app/pyproject.toml` |
| **Quick run command** | `cd firestarter_app && python -m pytest tests/ -q -x` |
| **Full suite command** | `cd firestarter_app && python -m pytest tests/` |
| **Estimated runtime** | ~seconds (unit-only; no bench) |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter_app && python -m pytest tests/ -q -x`
- **After every plan wave:** Run `cd firestarter_app && python -m pytest tests/`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| {N}-01-01 | 01 | 1 | DISP-01 / GRAD-01 / INBOX-01 | — | {expected behavior} | unit | `cd firestarter_app && python -m pytest tests/` | ❌ W0 | ⬜ pending |

*Planner: populate from RESEARCH.md `## Validation Architecture` — one row per must-have (DISP-01 AST audit + anti-hollow planted fixture; GRAD-01 report-side ladder-state + N≥2 dedup_fingerprint agreement; INBOX-01 `tools/parse_devtest_issue.py` parse + DB-diff via saved-JSON fixtures).*
*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Test files/fixtures for DISP-01 / GRAD-01 / INBOX-01 (planner-defined)
- [ ] Reuse existing seam: `EpromDatabase(skip_local_override=True)` + mock operator; SAFE-03 anti-hollow planted-fixture pattern (`tests/test_check_devtest_orchestrator.py`)

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

*All Phase 114 behaviors are host-Python + tooling — fully automated (no bench required).*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

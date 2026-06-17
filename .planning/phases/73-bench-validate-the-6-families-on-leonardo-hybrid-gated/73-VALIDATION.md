---
phase: 73
slug: bench-validate-the-6-families-on-leonardo-hybrid-gated
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-17
---

# Phase 73 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (host, Tier-2) + PlatformIO/Unity native (firmware, Tier-1); bench HIL via `firestarter dev validate-family` (Tier-3) |
| **Config file** | `firestarter_app/pyproject.toml` (`[test]` extra) + `firestarter/platformio.ini` |
| **Quick run command** | `cd firestarter_app && pytest -q` |
| **Full suite command** | `cd firestarter_app && pytest && cd ../firestarter && pio test -e native` |
| **Estimated runtime** | ~120 seconds (software tiers); Tier-3 HIL is operator-paced |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter_app && pytest -q`
- **After every plan wave:** Run full suite (host pytest + native Unity)
- **Before `/gsd-verify-work`:** Full software suite must be green; Tier-3 cells recorded in `validation-matrix.{json,md}`
- **Max feedback latency:** ~120 seconds (software); Tier-3 HIL recorded per-cell

---

## Per-Task Verification Map

> Populated by the planner per task. Tier-1/Tier-2 cells are automated; Tier-3 HIL cells are bench-recorded (matrix-cell evidence, not a watch-mode test).

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| {N}-01-01 | 01 | 1 | VAL-{XX} | T-73-XX / — | {expected secure behavior or "N/A"} | unit / bench-cell | `{command}` | ✅ / ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure (Phase 71 harness: `dev validate-family` runner, matrix artifact, non-vacuous PASS oracle, SKIP-deferred mechanism) covers all phase requirements. Phase 73 adds zero production code — no Wave 0 test scaffolding required.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Tier-3 HIL on Leonardo (W27C512, AM29F040, FM1608) | VAL-01/03/06 | Requires physical chip + Rev 2.0 shield on hand; Claude drives over USB passthrough, operator inserts chip / swaps shield | Per-family `dev validate-family` run with independent post-write full read + SHA compare + passing negative control; live R1/R2 readback (`r1 ≈ 270000`) recorded |
| FM1608 two-pattern A→B write+read-back (VAL-06 hard gate) | VAL-06 | Bench-only persistence proof; per-byte verdict separates whole-write no-op (FIX-01) from parked byte-0 FRAM bug | Write pattern A → read-back; write pattern B → read-back; baseline initial read + N≥2 confirm; per-byte D-08 classification |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify, a recorded bench-cell verdict, or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (excluding operator-paced Tier-3 HIL cells)
- [ ] Wave 0 covers all MISSING references (none — Phase 71 infrastructure reused)
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s (software tiers)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

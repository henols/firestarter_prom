---
phase: 70
slug: v1-11-v1-12-db-pipeline-integration-for-beta-merge
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-15
validated: 2026-06-16
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
| **Full suite command** | `cd firestarter_app && python -m pytest --cov-fail-under=70 && ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/ && python tools/check_mypy_watermark.py` |
| **Estimated runtime** | ~60–120 seconds (host suite); firmware native tests separate |

---

## Sampling Rate

- **After every task commit:** Run quick `pytest` for the touched module
- **After every plan wave:** Run full suite + ruff + mypy watermark + coverage floor
- **Before `/gsd-verify-work`:** Full suite + both diff stages (D-04) + GATE-03 must be green
- **Max feedback latency:** ~120 seconds

---

## Per-Task Verification Map

Phase 70 traces against the ROADMAP success criteria SC#1–SC#6 (not REQUIREMENTS.md IDs —
this is a beta-merge integration phase, see 70-VERIFICATION.md Requirements Coverage).

| SC | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|----|------|------|-------------|-----------|-------------------|-------------|--------|
| SC#1 | 70-01 | — | `resolve_pinout_key` sole pinout path + v1.12 safety features (support_status taxonomy, NMOS VPP, NON_DISPATCHABLE_ALGO, 0x34) | unit | `python -m pytest tests/test_build_db_inclusion.py -q` (15 tests: taxonomy, adapter-required, vpp-exceeds-max, protocol-not-implemented, SRAM-pinout invariants) | ✅ | ✅ green |
| SC#2 | 70-01, 70-02 | — | v1.11 decode-correctness preserved (8 decode fixes: interpret_timing, 0xF0 VPP mask, vcc/vdd bits, VCC_VOLTAGES 0x02/0x03, BUG-A/B) | unit + snapshot | `python -m pytest tests/test_decoder.py tests/test_characterization.py tests/test_bug_characterization.py -q` (74 tests) | ✅ | ✅ green |
| SC#3 | 70-02 | — | GATE-03 dispatch safety — no non-`supported` chip reaches a real handler; host guard refuses (D-12) | unit | `python -m pytest tests/test_chip_resolver.py tests/test_build_db_inclusion.py::TestDispatchSafety tests/test_decoder.py -q` (`test_non_supported_chips_are_non_dispatchable` + 9 `ChipNotImplementedError` host-guard tests + GATE-02 fail-closed `dispatch()`) | ✅ | ✅ green |
| SC#4 | 70-02 | — | GATE-02 diff_db — every changed chip vs baseline accounted for; 0 unexplained (stage-(b) identity diff) | integration | `python -m pytest tests/test_diff_db_gate.py -q` (**NEW — added by this audit; drives real `tools/diff_db.py` via subprocess, asserts exit 0 + "PASS: all"**) | ✅ | ✅ green |
| SC#5 | 70-03 | — | Full CI gate green — ruff + ruff format + mypy watermark + pytest --cov-fail-under=70 | gate (CI) | `cd firestarter_app && ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/ && python tools/check_mypy_watermark.py && python -m pytest --cov-fail-under=70` (runs in `.github/workflows/ci.yml`) | ✅ | ✅ green |
| SC#6 | 70-04 | — | Firmware v1.12→beta merge; native dispatch tests; 0xBB wire parity; flash budget | manual (firmware toolchain) | `cd firestarter && pio run -e uno && pio run -e leonardo && pio test -e native` | ✅ | 📋 manual-only |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky · 📋 manual-only*

---

## Wave 0 Requirements

No new framework install was required. The existing pytest + ruff + mypy-watermark + PlatformIO
native-test infrastructure covers all phase verification surfaces. The regenerated 744-chip
`chip_database.json` reuses the existing `test_characterization.ambr` snapshot fixtures and the
committed `tools/baseline/chip_database.baseline.json` GATE anchor — both regenerated in-phase
(Plans 02/03), no new fixture framework needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Firmware build (uno + leonardo) + native dispatch tests + 0xBB wire parity | SC#6 / D-06 | Requires PlatformIO toolchain; not part of host pytest. Cross-repo (firmware ↔ host) wire-constant parity (`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED=0xBB`) and git merge-state are not host-unit-testable. | `cd firestarter && pio run -e uno && pio run -e leonardo && pio test -e native` — verified PASS in 70-04-SUMMARY (49/49 native, uno 72.4% / leonardo 88.9% flash, 0xBB parity confirmed) |
| GATE-02 stage-(a) migration diff vs v1.11-beta DB | SC#4 | The `/tmp/v1.11-beta-db.json` baseline is a one-shot migration artifact not committed to the repo; only stage-(b) identity diff is CI-repeatable (now automated — see SC#4 above) | `FIRESTARTER_BASELINE_FILE=/tmp/v1.11-beta-db.json python tools/diff_db.py` (verified PASS, 0 UNEXPLAINED, in 70-02-SUMMARY) |

---

## Validation Sign-Off

- [x] All SCs have `<automated>` verify or are documented manual-only with reason
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (none required)
- [x] No watch-mode flags
- [x] Feedback latency < 120s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-06-16 — 5/6 SCs automated-covered; SC#6 documented manual-only (firmware toolchain). SC#4 gap closed by new `tests/test_diff_db_gate.py`.

---

## Validation Audit 2026-06-16

| Metric | Count |
|--------|-------|
| Gaps found | 1 |
| Resolved | 1 |
| Escalated | 0 |

**Gap:** SC#4 (`tools/diff_db.py` GATE-02) had zero automated test coverage — run only as a manual
gate, absent from CI and pytest. **Resolution:** added `firestarter_app/tests/test_diff_db_gate.py`
(`test_diff_db_identity_pass`) — drives the real `diff_db.py` via subprocess (test_audit_coverage_matrix
exit-code-discipline pattern) for the stage-(b) identity diff of `chip_database.json` vs the committed
`tools/baseline/chip_database.baseline.json`, asserting exit 0 + "PASS: all". Now CI-runnable; defends
against future accidental DB drift. Committed on `firestarter_app` `beta` branch as `e010149`
(gitlink NOT bumped — pinned until operator beta cut, per phase convention). Stage-(a) migration diff
remains manual-only (external one-shot baseline).

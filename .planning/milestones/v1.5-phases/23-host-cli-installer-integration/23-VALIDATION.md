---
phase: 23
slug: host-cli-installer-integration
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-21
---

# Phase 23 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 (existing `firestarter_app/tests/`) |
| **Config file** | `firestarter_app/pyproject.toml` (existing) |
| **Quick run command** | `cd firestarter_app && python -m pytest tests/test_firmware_install.py -q` |
| **Full suite command** | `cd firestarter_app && python -m pytest tests/ -v` |
| **Estimated runtime** | ~1 s test_firmware_install subset; ~1 s full suite (77 tests pre-Phase-23; expect 81-82 post-Phase-23) |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_firmware_install.py -q` (subset)
- **After every plan wave:** Run `python -m pytest tests/ -v` (full suite) and confirm regression-clean
- **Before `/gsd-verify-work`:** Full suite green; `pytest -k uno328pb` shows ≥ 4 new tests passing
- **Max feedback latency:** ~3 s (all-pytest, no network — mocked GitHub API)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 23-XX-XX | TBD | 1 | INST-01..03 + GATE-01 | — | N/A (host-side install path; no auth/network in test path) | unit | `cd firestarter_app && python -m pytest tests/test_firmware_install.py -v -k uno328pb` | ✅ (existing pytest infra) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Per-task rows will be filled in by the planner once PLAN.md files are emitted.*

---

## Wave 0 Requirements

- [ ] No new test framework install — pytest 9.0.3 already declared in `firestarter_app/pyproject.toml`.
- [ ] No new fixtures — reuse existing `mock_releases_factory()` + `monkeypatch.setattr(firmware.requests, "get", ...)` pattern.
- [ ] New `_FakeAvrdude` stub class (6-7 lines) lives in-file in `test_firmware_install.py`, NOT in `conftest.py` (matches existing module-local helper convention).

*"Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real-silicon flash of `firestarter_uno328pb.hex` succeeds via `firestarter fw -i --pre` | INST-02 (end-to-end) | Requires the operator's 328PB-Uno + RURP shield + a real beta pre-release with the uno328pb asset | Phase 24 (BENCH-01) executes this. The host installs the .hex, `avr_tool.py` reports a clean flash, device reboots with `board: uno328pb` reported by the new firmware handshake. |
| Device reboots into v1.5 firmware after flash | INST-02 + BENCH-01 | Same — needs real hardware | Phase 24 (BENCH-01) records the post-flash handshake response in `.planning/v1.5-BENCH-RESULTS.md`. |
| `programmer_id="arduino"` is correct for the operator's bootloader | D-02 in CONTEXT.md | Bench-only — bootloader protocol cannot be verified from host code in isolation | Phase 24 (BENCH-01). If `arduino` fails, swap to `urclock` in 1-line follow-up commit on `v1.5-uno328pb`. |
| `firestarter fw -i` (no --pre) installs stable uno328pb asset | INST-01 (end-to-end) | Requires a stable release (not pre-release) carrying the uno328pb asset; first stable cut is post-milestone-close | Deferred to post-v1.5-merge-up. Mocked tests cover the resolution path. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify commands (mocked-pytest invocations)
- [ ] Sampling continuity: every task has automated verify (the test suite IS the substrate; no opaque code paths)
- [ ] Wave 0 covers all MISSING references (none — pytest infra + mock helpers already exist)
- [ ] No watch-mode flags (`-q` / `-v` only)
- [ ] Feedback latency < 5 s
- [ ] `nyquist_compliant: true` set in frontmatter after planner fills per-task rows

**Approval:** pending

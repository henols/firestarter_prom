---
phase: 127
slug: host-dfu-installer
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-01
---

# Phase 127 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> **Repo:** all commands run in `firestarter_app/`, which MUST sit in the sibling layout
> (`<root>/firestarter_app` next to `<root>/firestarter`). `test_sdp_bus_config_drift.py:22`
> and `test_gen_validation_header.py:21` hardcode `_REPO_ROOT / "firestarter_app"` — a
> wrongly-named working directory produces 6 spurious failures. See `127-RESEARCH.md` §Q1.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing; `.[test]` extra) |
| **Config file** | `firestarter_app/pyproject.toml` |
| **Quick run command** | `python -m pytest tests/test_py32_dfu.py -q` |
| **Full suite command** | `python -m pytest -q` |
| **Estimated runtime** | ~60 s full suite; ~3 s for the py32 subset |
| **Post-merge baseline** | 1216 collected · 1213 passed · 3 skipped · 0 failed · coverage 81.35% (MEASURED, `127-RESEARCH.md` §Q1) |
| **Second leg** | `ci-py32` — `pip install -e .[test,py32]`, runs the pyusb-API-surface tests only (D-02) |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_py32_dfu.py -q` (plus the new
  test module the task touched)
- **After every plan wave:** Run `python -m pytest -q` — full suite, 0 failures
- **Before `/gsd-verify-work`:** Full suite green **in the sibling layout**, and the collected
  count recorded verbatim (D-04 — recorded, never asserted)
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

*Filled by the planner from PLAN.md task IDs.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 127-01-01 | 01 | 1 | HOST-01 | — | N/A | integration | `git log --format=%P -1 <merge> \| grep 4ee64a1` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements — pytest, `tests/fw_presence.py`'s
`@requires_fw`, `tests/test_skip_census.py`'s subprocess harness, and `_FakeUsbDevice` are all
already present and are the sanctioned mechanisms for HOST-03/04/05/08 (see `127-RESEARCH.md`
§Q4, §Q5). No framework install and no new fixtures directory are needed.

The one genuinely new local capability is a **pyusb-present environment**, which is created by
the `ci-py32` CI leg (D-02) rather than by a Wave 0 task — `pyusb` must NOT be installed into
the devcontainer's shared environment, because the pyusb-**absent** tests characterise that
environment.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The `ci-py32` leg actually runs green on GitHub Actions | HOST-04 | D-01: evidence requires `git push` + `gh workflow run`, and **no task in any plan may execute either command**. The structural separation is the gate, not the checkpoint type. | Operator personally runs `git push` then `gh workflow run ci.yml --ref v1.23-py32f071-integration`; records the run URL and conclusion in `127-NONREGRESSION.md`. Pushing this branch fires no release workflow (verified: `beta-release.yml` is `beta`-only, `release.yml`/`ci.yml` push are `main`-only, `publish.yml` is `release: published`). |
| Real DFU install against PY32F071 silicon | HOST-03 | **No PCB exists.** The permitted ceiling is mock/descriptor-level only. | NOT PERFORMED, and must not be claimed. Phase 130 CLOSE-02 cites "the mock-only ceiling on HOST-03" — this phase must produce that non-claim in citable form. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

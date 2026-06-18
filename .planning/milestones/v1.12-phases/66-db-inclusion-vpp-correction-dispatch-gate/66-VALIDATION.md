---
phase: 66
slug: db-inclusion-vpp-correction-dispatch-gate
status: ready
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-12
---

# Phase 66 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x+ (existing CI gate) + two standalone tool gates (`check_dispatch.py`, `diff_db.py`) |
| **Config file** | `firestarter_app/pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths=["tests"]`, `--cov-fail-under=70`) |
| **Quick run command** | `cd firestarter_app && python tools/check_dispatch.py` (tool gate, exits 0/1) |
| **Full suite command** | `cd firestarter_app && python -m pytest --cov-fail-under=70 -q` |
| **Estimated runtime** | ~30–60 seconds (tool gates < 10s each; full pytest suite ~30–45s) |

> **Python version trap:** run `build_db.py`, `check_dispatch.py`, `diff_db.py`, and pytest under the CI-target **Python 3.11** (no `python3.11` on the devcontainer PATH — source it the way Phase 63 did). `chip_database.json` generation is version-neutral, but the gate tools import `firestarter.database` and the drift/ruff gates only match CI under 3.11.

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter_app && python tools/check_dispatch.py` (exits 0 = gate green).
- **After every plan wave:** Run `cd firestarter_app && python -m pytest --cov-fail-under=70 -q`.
- **Before `/gsd-verify-work`:** `check_dispatch.py` + `diff_db.py` both exit 0 AND full pytest suite green.
- **Max feedback latency:** 60 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 66-01-01 | 01 | 1 | DB-05 | T-66-01 / T-66-SC | Pinned baseline = verbatim current DB (734); cherry-pick is git-internal, no external fetch | integration (tool) | `cd firestarter_app && test -f tools/diff_db.py && python3 -c "import json;d=json.load(open('tools/baseline/chip_database.baseline.json'));assert sum(len(v) for v in d.values() if isinstance(v,list))==734"` | ✅ (created in-task) | ⬜ pending |
| 66-01-02 | 01 | 1 | DB-05 | T-66-02 | Every Phase 66 diff attributable to a cited decision (RULE_PHASE66 rationale embeds D-04/06/07) | integration (tool) | `cd firestarter_app && python3 tools/diff_db.py; test $? -eq 0` | ✅ (Task 1) | ⬜ pending |
| 66-01-03 | 01 | 1 | DB-01/DB-03 | — | Test target uses locked taxonomy strings verbatim | unit (pytest, RED) | `cd firestarter_app && python3 -m pytest tests/test_build_db_inclusion.py --co -q` | ❌ W0 (created in-task) | ⬜ pending |
| 66-02-01 | 02 | 1 | DB-05 | T-66-03 | not_implemented FAIL only for support_status==supported; supported-no-handler still FAILs loudly | integration (tool) | `cd firestarter_app && python tools/check_dispatch.py; test $? -eq 0` | ✅ (reworked) | ⬜ pending |
| 66-02-02 | 02 | 1 | DB-05 | T-66-05 | Non-supported chips asserted to carry unsupported_reason; PNI proto asserted unimplemented | integration (tool) | `cd firestarter_app && python tools/check_dispatch.py | grep -i "non-supported"` | ✅ (reworked) | ⬜ pending |
| 66-03-01 | 03 | 2 | DB-01/DB-03 | T-66-06 / T-66-07 | No chip routed to a working handler; ambiguous high-VPP flagged (highest-VPP-wins) | unit (pytest contract) | `cd firestarter_app && grep -q "RURP_VPP_CEILING_MV = 22000" tools/build_db.py && ruff check tools/build_db.py` | ✅ (Plan 01 test) | ⬜ pending |
| 66-03-02 | 03 | 2 | DB-01/DB-03/DB-05 | T-66-08 / T-66-09 | Regen + gates under py3.11; baseline deviation reviewed; diff gate cross-checks dispatch baseline | integration (tool + pytest) | `cd firestarter_app && python tools/check_dispatch.py && python tools/diff_db.py && python -m pytest tests/test_build_db_inclusion.py -q` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tools/diff_db.py` — cherry-picked from v1.11 `f3b2ed7` + `RULE_PHASE66` (Plan 01 Task 1/2)
- [ ] `firestarter_app/tools/baseline/chip_database.baseline.json` — pinned 734-chip pre-edit baseline (Plan 01 Task 1)
- [ ] `firestarter_app/tests/test_build_db_inclusion.py` — 7 RED inclusion/VPP tests for DB-01/02/03 (Plan 01 Task 3)

*Existing pytest infrastructure (`conftest.py`, `pyproject.toml` cov gate) + the two standalone tool gates cover the rest. No framework install needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

*All phase behaviors have automated verification. (Host capability **display** / refusal messages are Phase 68 — out of scope here.)*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (diff_db.py, baseline, test scaffold — all in Plan 01)
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-06-12

---
phase: 62
slug: dispatch-baseline-capture-check-dispatch-update
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-10
---

# Phase 62 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Host-only phase (`firestarter_app`). Firmware GATE-01 baseline accepted as-is (D-02).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x (host CLI); native Unity via PlatformIO (firmware, accepted as-is) |
| **Config file** | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests"]` |
| **Quick run command** | `python3 -m pytest tests/test_decoder.py -x -q` (from `firestarter_app/`) |
| **Full suite command** | `python3 -m pytest -q` (from `firestarter_app/`) |
| **Estimated runtime** | ~quick <5s · full ~30s (559+ tests) |

> Devcontainer is Python 3.12 but CI targets py39/3.11 — validate new code with
> `ruff check` + `ruff format --check` against the target before claiming CI green
> (see project memory: py3.12 masks CI).

---

## Sampling Rate

- **After every task commit:** `ruff check tools/check_dispatch.py && ruff format --check tools/check_dispatch.py && python3 -m pytest tests/test_decoder.py -x -q`
- **After every plan wave:** `python3 -m pytest -q` (full suite)
- **Before `/gsd-verify-work`:** `python3 tools/check_dispatch.py` (all checks green, `0 not-implemented chips`) AND `python3 -m pytest -q` green
- **Max feedback latency:** <5 seconds (quick), ~30 seconds (full)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 62-01-* | 01 | 0 | GATE-02 | — | N/A | unit | `python3 -m pytest tests/test_decoder.py::TestDispatchGate02 -x -q` | ❌ W0 | ⬜ pending |
| 62-02-* | 02 | 1 | GATE-02 | — | `dispatch(0x35/0x39,None)→configure_flash4`; `dispatch(!=0,None)→not_implemented`; `dispatch(0,99)→ERROR` | unit | `python3 -m pytest tests/test_decoder.py::TestDispatchGate02 -x -q` | ❌ W0 | ⬜ pending |
| 62-02-* | 02 | 1 | GATE-02 | — | gate exits 0 with `0 not-implemented chips`, all pre-existing buckets green | integration | `python3 tools/check_dispatch.py` | ✅ existing | ⬜ pending |
| 62-03-* | 03 | 1 | GATE-01 | — | snapshot file lists 743 chips, each with `{algorithm, mem_type, resolved_handler}` triple | manual/shell | `python3 -c "import json; d=json.load(open('tools/baseline/dispatch_baseline.json')); print(d['meta']['db_chip_count'])"` → 743 | ❌ W0 | ⬜ pending |
| 62 (FW) | — | — | GATE-01 | — | `(protocol=0, mem_type=1) → NOT ERROR`; `(0, 99) → ERROR` | native Unity (accepted as-is, D-02) | `pio test -e native -f "*test_dispatch*"` (in `firestarter/`) | ✅ exists | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

> Task IDs are illustrative — final IDs assigned by the planner. Plan/wave grouping
> reflects the research's Wave-0-tests-first recommendation.

---

## Wave 0 Requirements

- [ ] `tests/test_decoder.py::TestDispatchGate02` — 5 new test methods pinning GATE-02 behavior:
  - `test_dispatch_0x35_routes_configure_flash4` → `"configure_flash4"`
  - `test_dispatch_0x39_routes_configure_flash4` → `"configure_flash4"`
  - `test_dispatch_unknown_nonzero_proto_routes_not_implemented` → `dispatch(0x99, None) == "not_implemented"`
  - `test_dispatch_protocol_zero_unknown_memtype_routes_error` → `dispatch(0, 99) == "ERROR"` (D-03 bucket separation)
  - `test_dispatch_protocol_zero_memtype_eprom_routes_eprom` → `dispatch(0, 1) == "configure_eprom"` (legacy fallback intact)
- [ ] `tools/baseline/dispatch_baseline.json` — snapshot artifact (GATE-01), 743-chip dispatch triples
- [ ] Branch `v1.12-protocol-dispatch-hardening` in `firestarter_app` (fork off `beta`) before any commit

*Existing pytest + PlatformIO Unity infrastructure covers all phase requirements — no framework install needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Snapshot is human-eyeballable across milestones | GATE-01 | D-01 chose a committed reference snapshot, not a hard diff gate — its value is human review, not machine assertion | Open `tools/baseline/dispatch_baseline.json`; confirm stable ordering and that triples self-document why each chip routes where |

*All gating behaviors (dispatch routing, not-implemented count, pre-existing buckets) have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (test_decoder.py tests, snapshot file)
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

---
phase: 138
slug: preconditions-baseline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-08
---

# Phase 138 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `138-RESEARCH.md` §"Validation Architecture" (all figures measured live 2026-08-08).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware native)** | PlatformIO **Unity** (`test_framework = unity`), 3 native envs |
| **Framework (firmware gates)** | **pytest** (stdlib + pytest only; **no `conftest.py` anywhere** — house rule) |
| **Framework (host)** | **pytest** + `pytest-cov` + snapshot plugin, `addopts = "-ra -q"`, `testpaths = ["tests"]` |
| **Config file** | `firestarter/platformio.ini` · `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `cd /workspaces/firestarter && python3 -m pytest tests/ -q` → **221 passed, 8.8 s** |
| **Full suite command** | `pio test -e native` · `-e native_nodevtools` · `-e native_pinmap_provisional` (≈50 s each warm); host: `cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` |
| **Estimated runtime** | ~9 s firmware gates · ~150 s three native envs · ~179 s host suite |

**Interpreter constraint (blocking, recorded trap):** the host suite MUST run under
`.venv/ci-replica/bin/python` (**3.11.15**). The devcontainer's ambient **3.12.13** masks the app's
py39/3.11 CI. Do not substitute.

**Count-line constraint:** host `addopts` is `-ra -q`; adding another `-q` suppresses the count line.
Always pass `-o addopts=""` when the count itself is the measurement.

**Directory-name constraint:** two host tests resolve `_HERE.parent.parent / "firestarter_app"` and
FAIL if the checkout directory is named anything else
(`tests/test_gen_validation_header.py::test_validate_spec_called_before_emission`,
`tests/test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing`).

---

## Sampling Rate

- **After every task commit:** Run the narrowest thing that can go RED — the gate or single pytest
  module the task touched (`python3 scripts/check_size_baseline.py …`, or
  `python3 -m pytest tests/test_golden_trace_identity_eprom_v131.py -q`)
- **After every plan wave:** `pio test -e native && pio test -e native_nodevtools && pio test -e native_pinmap_provisional`
  plus `python3 -m pytest tests/ -q` (firmware waves); full host suite (host waves)
- **Before `/gsd-verify-work`:** every gate green **and** the three native envs at their recorded
  counts **and** the new fixture's identity module green
- **Max feedback latency:** 60 seconds for per-task sampling (single gate or single pytest module)

---

## Per-Task Verification Map

> Populated by the planner/executor as tasks are authored. Requirement → command mapping below is
> fixed by research; the Task ID / Plan / Wave columns fill in from the PLAN.md files.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | PREP-01 | — | N/A | integration (git/gh) | `gh pr view 44 --repo henols/firestarter_app --json state,mergedAt,mergeCommit` + `comm -23` of both `git ls-tree -r --name-only` lists + restricted `git diff --stat` | ❌ W0 (no committed checker) | ⬜ pending |
| TBD | TBD | TBD | PREP-02 | — | N/A | integration (git) | `git rev-parse <branch>` + `git merge-base --is-ancestor <base> <branch>` per repo | ✅ | ⬜ pending |
| TBD | TBD | TBD | PREP-03 (AVR size) | — | N/A | unit (gate) | `python3 scripts/check_size_baseline.py --avr-log uno=… --avr-log uno328pb=… --avr-log leonardo=…` | ✅ | ⬜ pending |
| TBD | TBD | TBD | PREP-03 (native counts) | — | N/A | unit (gate) | same script, `--native-log native=… --native-log native_nodevtools=…` | ✅ | ⬜ pending |
| TBD | TBD | TBD | PREP-03 (warnings) | — | N/A | unit (gate) | `python3 scripts/check_build_warnings.py --log <env>=<log>` | ✅ | ⬜ pending |
| TBD | TBD | TBD | PREP-03 (fixture immutability) | — | N/A | unit (pytest) | `python3 -m pytest tests/test_golden_trace_identity_eprom_v131.py -q` | ❌ **W0** | ⬜ pending |
| TBD | TBD | TBD | PREP-03 (trace content) | — | N/A | unit (Unity) | `pio test -e native_trace_v131` | ❌ **W0** | ⬜ pending |
| TBD | TBD | TBD | PREP-03 (flag-off byte-exactness) | — | N/A | integration | `pio test -e native && pio test -e native_nodevtools` → re-assert 141/17/all-PASSED via the gate | ✅ | ⬜ pending |
| TBD | TBD | TBD | PREP-03 (host counts) | — | N/A | integration | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` | ✅ | ⬜ pending |
| TBD | TBD | TBD | PREP-04 | — | N/A | unit (script, self-checking) | `python3 .planning/phases/138-preconditions-baseline/138-pulse-distribution.py` | ❌ **W0** | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/test/native/avr/_shared/host_stubs_common.inc` — additive `HOST_STUBS_RECORD_TIMING`
      block (storage + `timing_push` + accessors), plus (if R2) a `HOST_STUBS_CUSTOM_READ_DATA_BUFFER`
      opt-out guard around the currently-unguarded `rurp_read_data_buffer` — covers PREP-03
- [ ] `firestarter/test/native/avr/_shared/eprom_v131_expected.h` — frozen fixture + comparator over
      the merged strobe+timing stream — covers PREP-03
- [ ] `firestarter/test/native/avr/test_trace_eprom_v131/{host_stubs.cpp,test_trace_eprom_v131.cpp}` —
      the new suite, incl. `reset_register_cache` and the pulse-counting read-back model
- [ ] `firestarter/platformio.ini` — `[env:native_trace_v131]` (1-entry `test_filter`, matching `-I`,
      **not** in `default_envs`, `build_flags` from `${env:native.build_flags}`)
- [ ] `firestarter/tests/golden/eprom_v131_trace_inventory.json` +
      `firestarter/tests/test_golden_trace_identity_eprom_v131.py`
- [ ] `firestarter/scripts/baseline/size_baseline_v131.json` — new immutable freeze (BASE-01 schema)
- [ ] `.planning/phases/138-preconditions-baseline/138-BASELINE.md` — narrative artifact in
      `131-CI-BASELINE.md` shape
- [ ] `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` + its committed verbatim
      output artifact — covers PREP-04
- [ ] No framework install needed — Unity, pytest, and the CI-parity venv all exist

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| CI run dispatched per repo, run id recorded | PREP-03 (D-06) | `gh workflow run` is blocked by the auto-mode classifier — a dispatch is inherently an operator action. Read-only `gh run view` / `gh api` work fine. | Operator dispatches the workflow; agent reads the run **read-only** and records the run id, plus `outcome`-vs-`conclusion` per step, in `138-BASELINE.md`. Firmware CI is **not** dispatchable (source-level fact); app CI is. |
| Cold-build measurement discipline | PREP-03 (D-06) | A default 2-minute Bash timeout truncates the toolchain build mid-compile and silently contaminates the figure. Automatable only with an explicit extended timeout. | `rm -rf .pio/build/<env>` then a **single** `pio` invocation with an extended timeout. Never guess a figure down from prose or a warm re-run. Warm figures are contamination (998 vs 1166 reproduced this trap live). |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

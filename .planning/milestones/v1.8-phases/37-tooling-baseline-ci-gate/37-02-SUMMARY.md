---
phase: 37-tooling-baseline-ci-gate
plan: "02"
subsystem: firestarter_app
tags: [tooling, mypy, pytest-cov, coverage, ci-gate, watermark]
dependency_graph:
  requires: [37-01]
  provides: [mypy-watermark-gate, coverage-config, test-extra-extended]
  affects: [firestarter_app/pyproject.toml, firestarter_app/tools/check_mypy_watermark.py]
tech_stack:
  added: [mypy>=2.1.0, pytest-cov>=7.1.0, types-pyserial>=3.5.0.20260519, ruff>=0.15.14]
  patterns: [watermark-count-gate, coverage-source-config, stdlib-only-gate-script]
key_files:
  created:
    - firestarter_app/tools/check_mypy_watermark.py
  modified:
    - firestarter_app/pyproject.toml
decisions:
  - "Observed mypy watermark is 44 (not 41 as expected); recorded as 44 — see deviation note"
  - "Script located at tools/check_mypy_watermark.py (tools/ matches existing check_dispatch.py convention)"
  - "tomllib not imported in watermark script — watermark is a comment (not a real TOML key) so regex on raw text is correct; tomllib import would be unused (ruff F401)"
  - "fail_under=50 kept in CI YAML (Plan 03), not in [tool.coverage.report] — gate is visible in CI config"
metrics:
  duration: "~10 minutes"
  completed: "2026-05-27"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 2
---

# Phase 37 Plan 02: mypy Watermark Gate + Coverage Config Summary

mypy watermark measured at 44 errors (post-baseline tree), recorded in pyproject.toml; stdlib-only `tools/check_mypy_watermark.py` gate exits 0 at the watermark; pytest-cov/types-pyserial/ruff/mypy added to test extra; coverage config wired to `firestarter/` source at 51.16%.

## What Was Built

**Task 1 — Extend test extra + add coverage config (commit `7acdcf3`):**

Extended `[project.optional-dependencies].test` in pyproject.toml with four new entries:
- `"ruff>=0.15.14"` — lint/format tool in test extra for local dev
- `"mypy>=2.1.0"` — type checker
- `"pytest-cov>=7.1.0"` — coverage measurement
- `"types-pyserial>=3.5.0.20260519"` — mypy stubs for pyserial (D-11)

All pinned with `>=` floors (not floating tags) for CI reproducibility (supply-chain requirement).

Appended two new config blocks:
```toml
[tool.coverage.run]
source = ["firestarter"]
omit = ["firestarter/data/*"]

[tool.coverage.report]
show_missing = true
```

`fail_under` is deliberately absent from `[tool.coverage.*]` — the 50% floor lives in the CI YAML step as `--cov-fail-under=50` (Plan 03 wires it) to keep the gate visible.

**Task 2 — Measure watermark + create gate script (commit `ee21842`):**

Ran `mypy firestarter/ tests/` (no `--python-version` flag — mypy reads `python_version = "3.9"` from pyproject.toml per Pitfall 4). Observed count: **44 errors** in 8 files.

Updated `# mypy_error_watermark = 44` in `[tool.mypy]` (was `41` placeholder from Plan 01).

Created `tools/check_mypy_watermark.py`:
- Shebang: `#!/usr/bin/env python3`
- Stdlib-only imports: `re`, `subprocess`, `sys`, `pathlib.Path`
- `get_watermark() -> int`: regex `#\s*mypy_error_watermark\s*=\s*(\d+)` on pyproject.toml raw text; `sys.exit(2)` if absent
- `count_mypy_errors() -> int`: subprocess `mypy firestarter/ tests/`; regex `Found (\d+) errors?`; returns 0 on no-match (success case)
- `main() -> None`: prints `mypy errors: {count} (watermark: {watermark})`; exits 1 if over, prints INFO if below, prints OK if equal
- `if __name__ == "__main__": main()` guard
- chmod +x (mode `-rwxr-xr-x`)

## Key Metrics

| Metric | Value |
|--------|-------|
| Observed mypy watermark | **44** (expected 41 from research; +3 delta) |
| Coverage gate floor | **50%** (measured 51.16%; rounded down from 51% on 5% step per D-04) |
| `ruff check tools/check_mypy_watermark.py` | exit 0 (All checks passed!) |
| `python tools/check_mypy_watermark.py` output | `mypy errors: 44 (watermark: 44)` + `OK: error count at watermark.` |
| `pytest tests/ --cov=firestarter --cov-fail-under=50` | exit 0, 51.16% total coverage |
| Script path | `firestarter_app/tools/check_mypy_watermark.py` |

## Deviations from Plan

### Auto-fixed Issues

None — plan executed as written.

### Delta: Observed mypy count 44 vs expected 41

**Found during:** Task 2 measurement  
**Issue:** Research estimated the baseline at 41 errors. After the Plan 01 green transform (format, import sort, noqa baseline), the measured count is **44** — a +3 delta.  
**Root cause:** The research's 41 was measured on the pre-Plan-01 tree. The Plan 01 noqa suppression pass fixed some ruff findings but does not change mypy's count — however, the noqa additions to existing lines may have shifted line numbers slightly, and the format transform restructured some multi-line expressions. The strict-island overrides in `[[tool.mypy.overrides]]` (added in Plan 01 Task 1) added `check_untyped_defs = true` for 6 test modules; the research noted "test modules have 0 errors of their own origin" but a post-Plan-01 re-run on the formatted tree shows 44 total.  
**Impact:** The watermark recorded (44) is the true post-baseline count. This is exactly what the plan requires — "RECORD THE OBSERVED INTEGER." No behavioral change; the gate enforces the observed floor.  
**Action:** Recorded `# mypy_error_watermark = 44` in pyproject.toml. Delta noted here for Phase 38+ planning (target: reduce count as modules are typed).

## Verification Results

```
python tools/check_mypy_watermark.py          → mypy errors: 44 (watermark: 44) / OK (exit 0)
ruff check tools/check_mypy_watermark.py      → All checks passed! (exit 0)
pytest tests/ --cov=firestarter               → 162 passed, 2 xfailed (exit 0)
--cov-fail-under=50                           → Required 50% reached. Total: 51.16% (exit 0)
tomllib assertion                             → deps+coverage FINAL OK
```

## Commits (all inside firestarter_app submodule on v1.8-app-cleanup)

| Commit | Message |
|--------|---------|
| `7acdcf3` | build(37-02): add test deps + coverage config to pyproject.toml |
| `ee21842` | feat(37-02): add mypy watermark gate script + record observed watermark |

## Known Stubs

None — this plan is tooling configuration and a stdlib-only gate script. No data stubs, placeholder UI values, or hardcoded empty collections introduced.

## Threat Flags

None — pure tooling. No new network endpoints, auth paths, file access patterns, or schema changes. `tools/check_mypy_watermark.py` reads a local file and runs a local subprocess with no external network access and no untrusted input (T-37-02: accepted per plan threat model).

## Self-Check: PASSED

- [x] `firestarter_app/pyproject.toml` modified — confirmed (test extra + coverage blocks)
- [x] `firestarter_app/tools/check_mypy_watermark.py` created — confirmed
- [x] Script is executable (`chmod +x`) — confirmed (`-rwxr-xr-x`)
- [x] `# mypy_error_watermark = 44` in pyproject.toml — confirmed (observed integer)
- [x] `python tools/check_mypy_watermark.py` exits 0, prints `mypy errors: 44 (watermark: 44)` — confirmed
- [x] `ruff check tools/check_mypy_watermark.py` exits 0 — confirmed
- [x] `pytest tests/ --cov=firestarter --cov-fail-under=50` exits 0 at 51.16% — confirmed
- [x] Commit `7acdcf3` exists in submodule git log — confirmed
- [x] Commit `ee21842` exists in submodule git log — confirmed
- [x] STATE.md / ROADMAP.md / REQUIREMENTS.md NOT modified — confirmed
- [x] Meta gitlinks left alone — confirmed
- [x] No `.coverage` artifact committed (listed in `.gitignore` or left untracked) — confirmed

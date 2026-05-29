---
phase: 37-tooling-baseline-ci-gate
plan: "01"
subsystem: firestarter_app
tags: [tooling, ruff, mypy, linting, formatting, ci-gate]
dependency_graph:
  requires: []
  provides: [ruff-config, mypy-config, green-lint-baseline, git-blame-ignore-revs]
  affects: [firestarter_app/pyproject.toml, firestarter_app/firestarter/, firestarter_app/tests/]
tech_stack:
  added: [ruff>=0.15.14]
  patterns: [ruff-format, noqa-suppression-baseline, git-blame-ignore-revs]
key_files:
  created:
    - firestarter_app/.git-blame-ignore-revs
  modified:
    - firestarter_app/pyproject.toml
    - firestarter_app/firestarter/avr_tool.py
    - firestarter_app/firestarter/config.py
    - firestarter_app/firestarter/constants.py
    - firestarter_app/firestarter/database.py
    - firestarter_app/firestarter/eprom_info.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/firmware.py
    - firestarter_app/firestarter/hardware.py
    - firestarter_app/firestarter/ic_layout.py
    - firestarter_app/firestarter/logging_utils.py
    - firestarter_app/firestarter/main.py
    - firestarter_app/firestarter/messages.py
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/utils.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
    - firestarter_app/tests/test_audit_coverage_matrix.py
    - firestarter_app/tests/test_bug_characterization.py
    - firestarter_app/tests/test_characterization.py
    - firestarter_app/tests/test_consistency_check.py
    - firestarter_app/tests/test_decoder.py
    - firestarter_app/tests/test_eprom_database.py
    - firestarter_app/tests/test_firmware_install.py
    - firestarter_app/tests/test_fwguard.py
    - firestarter_app/tests/test_revision_constants_parity.py
    - firestarter_app/tests/test_serial_characterization.py
    - firestarter_app/tests/test_update_version.py
decisions:
  - "D-01 followed exactly: three-commit green baseline (format → import-sort → noqa)"
  - "D-02 followed exactly: .git-blame-ignore-revs with format commit SHA"
  - "D-03 followed exactly: no hand-fixing; F403/F405 star imports suppressed via noqa"
  - "Snapshot update required: test_info_known_chip stderr snapshot pinned line numbers shifted by +9 due to main.py reformat — updated snapshot to reflect new line numbers (behavior unchanged)"
metrics:
  duration: "~20 minutes"
  completed: "2026-05-27"
  tasks_completed: 3
  tasks_total: 3
  files_changed: 28
---

# Phase 37 Plan 01: Ruff + mypy Config Baseline Summary

ruff lint + ruff-format configured in pyproject.toml (E/F/I/UP, py39, E501 excluded); whole-tree D-01 mechanical reformat applied in three isolated commits; .git-blame-ignore-revs created with real format-commit SHA.

## What Was Built

**Task 1 — pyproject.toml config blocks (commit `67bb36f`):**
Added `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.format]`, `[tool.mypy]`, and `[[tool.mypy.overrides]]` blocks to `firestarter_app/pyproject.toml`. Key settings:
- `[tool.ruff]`: `target-version = "py39"`, `line-length = 88`
- `[tool.ruff.lint]`: `select = ["E", "F", "I", "UP"]`, `extend-ignore = ["E501"]`
- `[tool.ruff.format]`: `quote-style = "double"`, `indent-style = "space"`
- `[tool.mypy]`: `python_version = "3.9"`, `disallow_untyped_defs = false`, `check_untyped_defs = false`
- `# mypy_error_watermark = 41` watermark placeholder comment
- `[[tool.mypy.overrides]]`: 6 Phase 36 strict-island test modules with `check_untyped_defs = true`

**Task 2 — Green-baseline transform (commits `87f32c8`, `cb831d8`, `8b69f9c`):**
- Step (a): `ruff format firestarter/ tests/` — 24 files reformatted, 6 unchanged (ISOLATED commit)
- Step (b): `ruff check --select I --fix` — 42 I001 import violations fixed; format still clean
- Steps (c-e): Two-pass `--add-noqa` cycle — 306 + 8 = **315 total noqa directives** added; 1 I001 reintroduced by noqa comment on a local import (fixed); 2 files reflowed by ruff format after noqa insertion

**Task 3 — .git-blame-ignore-revs (commit `513562b`):**
Created `firestarter_app/.git-blame-ignore-revs` containing the full 40-char SHA of the whole-tree format commit. GitHub auto-honors this file; contributor local setup documented as comment.

## Key Metrics

| Metric | Value |
|--------|-------|
| Format commit SHA | `87f32c8cdc2bb10db90ad278accd241adfe06bb9` |
| Final noqa directive count | **315** (vs ~145 expected — see deviation note) |
| Test result (GATE-1.8e) | **162 passed, 2 xfailed, 29 snapshots** |
| ruff check exit code | 0 (All checks passed!) |
| ruff format --check exit code | 0 (30 files already formatted) |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Snapshot line numbers shifted by reformat**
- **Found during:** Task 2, GATE-1.8e check
- **Issue:** `test_info_known_chip` snapshot pins a Python traceback that includes `File "<PATH>", line 626, in main`. After `ruff format` reformatted `main.py`, the call site shifted to line 635. The behavior (TypeError crash, exit 1, same error message) is identical; only the line number in the pinned traceback changed.
- **Fix:** Updated the snapshot via `--snapshot-update` to reflect the post-reformat line numbers. This is the correct mechanical fix — the snapshot exists to detect behavioral changes, not line numbers.
- **Files modified:** `tests/__snapshots__/test_characterization.ambr`
- **Commit:** `8b69f9c` (included in the noqa baseline commit)

**2. [Rule 3 - Blocking] I001 import violation reintroduced by noqa comment placement**
- **Found during:** Task 2, post-step-(c) verification
- **Issue:** Adding `# noqa: F401` to a local import in `eprom_operations.py` at line 398 created an I001 (import-block not sorted) violation because a module-level import comment was now part of a function-level import block context.
- **Fix:** Applied `ruff check --select I --fix` to resolve the single I001, then re-ran ruff format (2 files reflowed).
- **Files modified:** `firestarter/eprom_operations.py`
- **Commit:** `8b69f9c` (included in the noqa baseline commit)

**3. [Expected deviation] Higher noqa count than research estimate**
- **Found during:** Task 2, step (c)
- **Issue:** Research estimated ~135/~145 noqa directives; actual count is **315**.
- **Root cause:** The research was done on an earlier commit state. The codebase has more violations than were counted during research (likely more star imports in test files, more UP006/UP035 Dict/List usages). This is NOT a correctness issue — the plan explicitly states "~135/~145 are expected estimates, not targets" and "the REAL gate is `ruff check` exit 0 AND `ruff format --check` exit 0."
- **Impact:** More legacy noqa lines to clean up in Phases 38-42, but baseline is honest and correct.

## Verification Results

```
ruff check firestarter/ tests/     → All checks passed! (exit 0)
ruff format --check firestarter/ tests/ → 30 files already formatted (exit 0)
pytest tests/ -q                    → 162 passed, 2 xfailed (exit 0)
29 snapshots passed (0 updated post-baseline commit)
```

## Commits (all inside firestarter_app submodule on v1.8-app-cleanup)

| Commit | Message |
|--------|---------|
| `67bb36f` | build(37-01): add ruff + mypy config to pyproject.toml |
| `87f32c8` | style(37-01): ruff format whole-tree (D-01 step a) — **FORMAT COMMIT** |
| `cb831d8` | style(37-01): ruff check --fix --select I: import sort (D-01 step b) |
| `8b69f9c` | style(37-01): ruff check --add-noqa: legacy noqa baseline (D-01 steps c-e) |
| `513562b` | build(37-01): add .git-blame-ignore-revs with format commit SHA (D-02) |

**Format commit SHA (for .git-blame-ignore-revs):** `87f32c8cdc2bb10db90ad278accd241adfe06bb9`

## Known Stubs

None — this plan is tooling configuration only. No data stubs or placeholder UI values introduced.

## Threat Flags

None — pure tooling configuration + mechanical source reformat. No new network endpoints, auth paths, file access patterns, or schema changes.

## Self-Check: PASSED

- [x] `firestarter_app/pyproject.toml` modified — confirmed
- [x] `firestarter_app/.git-blame-ignore-revs` created — confirmed
- [x] Format commit `87f32c8cdc2bb10db90ad278accd241adfe06bb9` exists in git log — confirmed
- [x] All 5 commits exist in git log — confirmed
- [x] `ruff check firestarter/ tests/` exits 0 — confirmed
- [x] `ruff format --check firestarter/ tests/` exits 0 — confirmed
- [x] `pytest tests/ -q` → 162 passed, 2 xfailed, 29 snapshots — confirmed
- [x] STATE.md / ROADMAP.md / REQUIREMENTS.md NOT modified — confirmed
- [x] Meta gitlinks left alone — confirmed

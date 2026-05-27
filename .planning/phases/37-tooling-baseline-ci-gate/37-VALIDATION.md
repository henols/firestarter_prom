---
phase: 37
slug: tooling-baseline-ci-gate
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-27
---

# Phase 37 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: 37-RESEARCH.md § Validation Architecture (measured directly against the
> `firestarter_app/` tree at Phase 36 tip).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.0+ (Phase 36 baseline: 162 tests + 2 xfail(strict) + 29 syrupy snapshots) |
| **Config file** | `firestarter_app/pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ --cov=firestarter --cov-fail-under=50` |
| **Estimated runtime** | ~15 seconds (unit + snapshot, no hardware I/O) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q` — verifies the mechanical reformat / import-sort autofix did not change behavior.
- **After every plan wave:** Run `pytest tests/ --cov=firestarter --cov-fail-under=50` + `ruff check firestarter/ tests/` + `ruff format --check firestarter/ tests/` + `mypy firestarter/ tests/`.
- **Before `/gsd-verify-work`:** Full suite green AND `ruff check` / `ruff format --check` exit 0 AND mypy error count ≤ watermark (41).
- **Max feedback latency:** ~15 seconds (quick run).

---

## Per-Task Verification Map

> Task IDs are assigned during planning. The gsd-validate-phase / nyquist auditor fills
> concrete task rows after PLAN.md files exist. Requirement→behavior anchors below are
> fixed by RESEARCH.md and carry into the per-task rows.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | — | — | TOOL-01 | — | N/A | smoke | `ruff check firestarter/ tests/` | N/A (command) | ⬜ pending |
| TBD | — | — | TOOL-01 | — | N/A | smoke | `ruff format --check firestarter/ tests/` | N/A (command) | ⬜ pending |
| TBD | — | — | TOOL-02 | — | N/A | smoke | `python scripts/check_mypy_watermark.py` | ❌ W0 | ⬜ pending |
| TBD | — | — | TOOL-03 | — | N/A | integration | CI YAML (GitHub Actions `ci.yml`) | ❌ W0 (extend existing) | ⬜ pending |
| TBD | — | — | TOOL-03 | — | N/A | manual | `pre-commit run --all-files` | ❌ W0 | ⬜ pending |
| TBD | — | — | GATE-1.8e | — | N/A | unit/integration | `pytest tests/ -q` | ✅ 162 tests | ⬜ pending |
| TBD | — | — | GATE-1.8e | — | N/A | coverage | `pytest tests/ --cov=firestarter --cov-fail-under=50` | N/A (command) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/scripts/check_mypy_watermark.py` — count-comparison gate for TOOL-02 (run mypy → parse `Found N errors` → compare to integer watermark → fail if greater; handles the 0-error case).
- [ ] `firestarter_app/.pre-commit-config.yaml` — hook order ruff-check → ruff-format → mypy (TOOL-03).
- [ ] `firestarter_app/.git-blame-ignore-revs` — records the whole-tree `ruff format` commit SHA (D-02 blame preservation).
- [ ] Updated `firestarter_app/.github/workflows/ci.yml` — folded gate steps + PR trigger change (TOOL-03).

*Existing test infrastructure (162 tests + 2 xfail + 29 snapshots from Phase 36) covers GATE-1.8e behavior preservation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `pre-commit` hooks install and run locally | TOOL-03 | pre-commit hooks fire on `git commit` in a real working tree; CI exercises the same hooks via `pre-commit run --all-files` but local install is operator-side | `pip install pre-commit && pre-commit install && pre-commit run --all-files` from `firestarter_app/` |
| GitHub auto-honors `.git-blame-ignore-revs` | D-02 / TOOL-01 | GitHub blame-UI behavior is server-side; cannot be asserted in a local test | After merge, open a reformatted file's blame on GitHub; confirm the format commit is skipped |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

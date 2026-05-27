---
phase: 39
slug: database-cleanup-chip-resolver
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-27
---

# Phase 39 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `39-RESEARCH.md` § Validation Architecture (HIGH confidence, verified against live code).
> Scope: host-only pure refactor under GATE-1.8 — behavior byte-identical, no new threat surface.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 + syrupy 5.2.0 (snapshot) |
| **Config file** | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `cd firestarter_app && python -m pytest tests/test_chip_resolver.py tests/test_revision_constants_parity.py -q` |
| **Full suite command** | `cd firestarter_app && python -m pytest -q` |
| **Lint / type gate** | `cd firestarter_app && python -m ruff check firestarter/ && python tools/check_mypy_watermark.py` |
| **Estimated runtime** | ~12 seconds (full suite, 182+N tests) |

---

## Sampling Rate

- **After every task commit:** Run the quick run command.
- **After every plan wave:** Run the full suite command.
- **After every wave merge:** Full suite + `ruff check firestarter/` + `check_mypy_watermark.py` (all exit 0).
- **Before `/gsd-verify-work`:** Full suite + lint + watermark must all be green.
- **Max feedback latency:** ~12 seconds.

---

## Per-Task Verification Map

> Task IDs are assigned during planning (Step 8). Rows below are the requirement-level
> verification contract every task touching that requirement must satisfy; the planner
> maps each to concrete `{NN-MM-KK}` task IDs in PLAN frontmatter.

| Plan (TBD) | Wave | Requirement | Expected behavior (byte-identical) | Test Type | Automated Command | File Exists | Status |
|------------|------|-------------|------------------------------------|-----------|-------------------|-------------|--------|
| DATA-01 | 1 | DATA-01 | `resolve_chip("W27C512")` returns programmer-config dict | unit | `pytest tests/test_chip_resolver.py::test_resolve_chip_hit_returns_dict -x` | ❌ W0 (Wave 1 creates) | ⬜ pending |
| DATA-01 | 1 | DATA-01 | `resolve_chip("NOTACHIP")` raises `ChipNotFoundError` | unit | `pytest tests/test_chip_resolver.py::test_resolve_chip_miss_raises -x` | ❌ W0 (Wave 1 creates) | ⬜ pending |
| DATA-01 | 1 | DATA-01 | 9 op sites contain no `get_eprom`/`convert_to_programmer` calls | structural (grep) | `grep -n "get_eprom\|convert_to_programmer" firestarter/main.py` → 0 op-site hits | ✅ | ⬜ pending |
| DATA-01 | 1 | DATA-01 | bad-chip log line + exit-1 preserved (GATE-1.8b) | snapshot | `pytest tests/ -k bad_chip -x` (Phase 36 snapshots) | ✅ | ⬜ pending |
| DATA-01 | 1 | DATA-01 | `dev consistency-check` unchanged (ring-fenced read path, GATE-1.8d) | integration | `pytest -k consistency_check -x` | ✅ | ⬜ pending |
| DATA-03 | 2 | DATA-03 | no `from firestarter.constants import *` remain | structural (grep) | `grep -r "from firestarter.constants import \*" firestarter/` → empty | ✅ | ⬜ pending |
| DATA-03 | 2 | DATA-03 | ruff exits 0 (no dead F403/F405 noqa) | lint | `python -m ruff check firestarter/` | ✅ | ⬜ pending |
| DATA-03 | 2 | DATA-03 | mypy watermark not exceeded (≤44; currently 41) | type-check | `python tools/check_mypy_watermark.py` exits 0 | ✅ | ⬜ pending |
| DATA-02 | 3 | DATA-02 | `pin_conversions` docstring states RURP board-wiring (distinct from `pinouts.json`) | structural | `grep -i "board-wiring" firestarter/database.py` | ✅ | ⬜ pending |
| DATA-04 | 3 | DATA-04 | `COMMAND_FW_VERSION == 0x0D` parity assertion passes | unit | `pytest tests/test_revision_constants_parity.py -x` | ✅ | ⬜ pending |
| DATA-04 | 3 | DATA-04 | `# Firmware sync: firestarter.h` markers on `COMMAND_*` + `FLAG_*` blocks | structural | `grep -c "Firmware sync" firestarter/constants.py` | ✅ | ⬜ pending |
| DATA-04 | 3 | DATA-04 | full parity suite green (values unchanged, GATE-1.8c) | unit | `pytest tests/test_revision_constants_parity.py -v` (4 tests) | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tests/test_chip_resolver.py` — created in Wave 1; covers DATA-01 (hit, miss → `ChipNotFoundError`, conversion correctness against real `chip_database.json` via `EpromDatabase(skip_local_override=True)`).

*All other required test infrastructure exists — `conftest.py`, syrupy, pytest, the Phase 36 characterization snapshots, and `test_revision_constants_parity.py` are confirmed present and green (182 passed + 2 xfailed + 29 snapshots baseline).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `pin_conversions` docstring is *accurate* (semantics, not just present) | DATA-02 | Doc correctness is a human judgment; the grep only proves presence | Read the docstring: it must state `pin_conversions` maps DIP socket pin → RURP bus line (board wiring) and is distinct from `pinouts.json` (chip function → socket pin); no code/behavior change |

*All other phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or a Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers the single MISSING reference (`test_chip_resolver.py`)
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

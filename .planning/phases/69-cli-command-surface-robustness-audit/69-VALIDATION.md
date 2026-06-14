---
phase: 69
slug: cli-command-surface-robustness-audit
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-14
---

# Phase 69 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (host CLI — `firestarter_app/`) |
| **Config file** | `firestarter_app/pyproject.toml` |
| **Quick run command** | `python -m pytest tests/test_ic_layout.py tests/test_cli_handlers.py -q` |
| **Full suite command** | `python -m pytest --cov=firestarter --cov-fail-under=70 -q` |
| **Estimated runtime** | ~30 seconds |

> Run all commands from inside `firestarter_app/`. Restore the toolchain if wiped via `pip install -e '.[test]'`. Validate `ruff check` + `ruff format --check` + mypy against the CI target (py39/3.11), not just the devcontainer's 3.12.

---

## Sampling Rate

- **After every task commit:** Run quick run command (`test_ic_layout.py` + `test_cli_handlers.py`)
- **After every plan wave:** Run full suite command (with coverage gate)
- **Before `/gsd-verify-work`:** Full suite must be green, cov ≥ 70, ruff + mypy clean
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 69-01-* | 01 | 1 | SC#1 | — | `info <chip>` renders list-valued pin fields without raising | unit | `python -m pytest tests/test_ic_layout.py -q` | ❌ W0 (new file) | ⬜ pending |
| 69-02-* | 02 | 2 | SC#2, SC#3 | — | every CLI command surface returns clean outcome or typed error — never a traceback | unit | `python -m pytest tests/test_cli_handlers.py -q` | ✅ | ⬜ pending |
| 69-0x-* | — | final | SC#4 | — | full suite green, cov ≥ 70, ruff + mypy clean against CI target | suite | `python -m pytest --cov=firestarter --cov-fail-under=70 -q` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_ic_layout.py` — new file; list-valued-pin display regression for `_generate_pin_names_for_display`
- [ ] Extend `tests/test_cli_handlers.py` — command-surface smoke + Phase 66 support_status refusal cases; flip `test_info_chip_resolution_happy_path` to assert exit 0
- [ ] Regenerate `tests/__snapshots__/test_characterization.ambr` via `pytest --snapshot-update tests/test_characterization.py::test_info_known_chip` after the fix

*Existing pytest infrastructure (`make_app_context` pattern) covers the command-surface harness — no framework install needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | All phase behaviors are read-only/display or typed-error paths exercisable hardware-free | N/A |

*All phase behaviors have automated verification (HOST-ONLY; no programmer connection required for the audited display/resolution paths).*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

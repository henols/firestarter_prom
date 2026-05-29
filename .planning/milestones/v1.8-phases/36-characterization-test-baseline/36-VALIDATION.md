---
phase: 36
slug: characterization-test-baseline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-27
---

# Phase 36 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `36-RESEARCH.md` § Validation Architecture (all patterns experimentally verified against live code).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 + syrupy 5.2.0 (snapshot) |
| **Config file** | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` (syrupy added to `[project.optional-dependencies].test`) |
| **Quick run command** | `pytest tests/test_characterization.py tests/test_serial_characterization.py tests/test_eprom_database.py tests/test_bug_characterization.py -x -q` |
| **Full suite command** | `pytest tests/ -q` |
| **Estimated runtime** | ~1–2 seconds (98 existing tests baseline 1.09 s + new suites) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -q` (full suite is fast enough to run every commit)
- **After every plan wave:** Run `pytest tests/ -q`
- **Before `/gsd-verify-work`:** Full suite green AND `ruff` / `mypy` run without configuration errors (violations recorded as baseline watermark, NOT fixed — that is Phase 37)
- **Max feedback latency:** ~2 seconds

---

## Per-Task Verification Map

> Task IDs (`36-NN-MM`) are assigned by the planner. Rows below are requirement-level until plans exist; the executor maps each task to the matching row.

| Req / Gate | Behavior | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|------------|----------|------------|-----------------|-----------|-------------------|-------------|--------|
| TEST-01 | CLI surface pins (`--help` ×14 subcmds + `dev`; `list`/`info`/`search`; all arg-parse/usage errors; hardware-absent error paths) | — | N/A (test-only) | snapshot (subprocess) | `pytest tests/test_characterization.py -x -q` | ❌ W0 | ⬜ pending |
| TEST-01 | read/write/verify/erase happy-paths (in-process, `make_comm`/`fake_serial`) | — | N/A | unit (in-process) | `pytest tests/test_characterization.py -k happy -x` | ❌ W0 | ⬜ pending |
| TEST-02 | `_read_and_parse_lines` preamble→body→terminator sequence | — | N/A (ring-fenced; external observation only) | unit | `pytest tests/test_serial_characterization.py -x -q` | ❌ W0 | ⬜ pending |
| TEST-02 | sliding-window timeout resets on every yield | — | N/A | unit | `pytest tests/test_serial_characterization.py -k sliding -x` | ❌ W0 | ⬜ pending |
| TEST-03 | `EpromDatabase` injectable construction (no singleton guard; `skip_local_override` seam) | — | default `skip_local_override=False` preserves prod behavior | unit | `pytest tests/test_eprom_database.py -x -q` | ❌ W0 | ⬜ pending |
| TEST-03 | `get_eprom`, `convert_to_programmer`, DIP→RURP pin translation vs real `chip_database.json` | — | N/A | unit | `pytest tests/test_eprom_database.py -x -q` | ❌ W0 | ⬜ pending |
| TEST-04 | COMMAND_*/FLAG_*/CTRL_* parity vs `firestarter.h` (extends `test_revision_constants_parity.py`); `skipif` when firmware checkout absent | — | N/A | parity | `pytest tests/test_revision_constants_parity.py -x -q` | ✅ extend | ⬜ pending |
| TEST-05 | `build_arg_flags` `"force" in args` bug pinned, asserting corrected behavior | — | N/A | xfail(strict) `# BUG: fix → Phase 41 CLI-03` | `pytest tests/test_bug_characterization.py -x -q` | ❌ W0 | ⬜ pending |
| TEST-05 | comm-error vs operational-error conflation bug pinned, asserting corrected behavior | — | N/A | xfail(strict) `# BUG: fix → Phase 42 ERR-01` | `pytest tests/test_bug_characterization.py -x -q` | ❌ W0 | ⬜ pending |
| GATE-1.8(e) | full suite green (existing + new) | — | N/A | all | `pytest tests/ -q` | ✅ ongoing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_characterization.py` — TEST-01 (CLI surface goldens + in-process happy-paths)
- [ ] `tests/test_serial_characterization.py` — TEST-02 (`_read_and_parse_lines` pin + sliding-window)
- [ ] `tests/test_eprom_database.py` — TEST-03 (DB unit tests against real `chip_database.json`)
- [ ] `tests/test_bug_characterization.py` — TEST-05 (two `xfail(strict=True)` bug pins)
- [ ] `tests/__snapshots__/` (`.ambr` files) — generated via `--snapshot-update`, committed
- [ ] `pyproject.toml` `[project.optional-dependencies].test` — add `syrupy>=5.0` (new group alongside existing `dev`)
- [ ] `database.py` de-singleton — remove `__new__`/`_initialized` guard, add `skip_local_override: bool = False` seam (TEST-03 production change)

*Existing: `tests/test_revision_constants_parity.py` — EXTEND for TEST-04; `tests/conftest.py` fixtures (`fake_serial`, `make_comm`, `build_frame`) — reuse, no changes needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live hardware read/write/verify/erase over real Arduino | TEST-01 (E2E) | Hardware-gated; out of scope for this pure-software milestone — characterized in-process via `fake_serial` instead | N/A — board I/O deferred; not a Phase 36 risk |
| `ruff` / `mypy` baseline watermark | GATE-1.8 | Config-presence check only — violations are recorded, not fixed (that is Phase 37) | `ruff check . ; mypy firestarter` exit without **configuration** errors |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 2s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

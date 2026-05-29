---
phase: 38
slug: low-risk-extractions
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-27
---

# Phase 38 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Authoritative spec lives in `38-RESEARCH.md` → `## Validation Architecture`.
> Per-task IDs in the map below are assigned by the planner; this file pre-commits
> the infrastructure, sampling rate, Wave 0 test files, and the proof model for a
> behavior-preserving extraction.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + syrupy (snapshot) |
| **Config file** | `firestarter_app/pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `cd firestarter_app && python -m pytest --tb=short -q` |
| **Full suite command** | `cd firestarter_app && python -m pytest --tb=short -q` |
| **Estimated runtime** | ~14–18 seconds (no hardware required) |

**Verified baseline (research, 2026-05-27):** `162 passed, 2 xfailed, 29 snapshots passed`.

---

## Sampling Rate

- **After every extraction commit:** Run the full suite (`python -m pytest --tb=short -q`). It is fast (~15s) and is the *only* acceptance signal for "behavior preserved" — a partial run is insufficient because the safety net is cross-module.
- **After every plan wave:** Full suite green + `git diff tests/__snapshots__/` empty.
- **Before `/gsd-verify-work`:** Full suite green, mypy watermark not exceeded, ruff gate green.
- **Max feedback latency:** ~18 seconds.

---

## Per-Task Verification Map

> Task IDs (`38-NN-NN`) are filled by the planner. Rows below are keyed by requirement
> so the planner can attach the right `<automated>` command to each extraction task.

| Requirement | Wave | Extracted unit | Test Type | Automated Command | Proof |
|-------------|------|----------------|-----------|-------------------|-------|
| STRUCT-04 | exceptions | `exceptions.py` (8 classes, D-01/D-02) | import-smoke + suite | `python -m pytest --tb=short -q` | All repointed `import/raise/except` sites resolve; suite green |
| STRUCT-01 | frame_parser | `frame_parser.py` primitives + re-export | regression | `python -m pytest tests/test_decoder.py -q` | `test_decoder.py` passes UNCHANGED (D-07) |
| STRUCT-02 | codec | `codec.format_message` | unit (new) | `python -m pytest tests/test_codec.py -q` | 10 catalog-fixture cases (D-08) pass |
| STRUCT-03 | address_parser | `parse_address` / `parse_size` | unit (new) | `python -m pytest tests/test_address_parser.py -q` | hex / decimal / None / invalid (SC#4) pass; `_setup_operation` snapshots unchanged (D-12) |
| STRUCT-05 | dead-code sweep | `read_data_block` del + `COMMAND_NAMES[cmd]` | suite + snapshot | `python -m pytest --tb=short -q` | suite green; `globals()` gone; snapshot diff empty |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_codec.py` — new; 10 `format_message` cases per RESEARCH Validation Architecture (D-08). Import `from firestarter.codec import format_message`.
- [ ] `tests/test_address_parser.py` — new; hex/decimal/None/invalid for `parse_address` + `parse_size` (SC#4).
- [ ] (optional) `exceptions` import-smoke assertion — confirms all 8 classes importable from `firestarter.exceptions`.

Existing infrastructure (pytest + syrupy, Phase 36's 162-test net) covers everything else — no framework install needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `git diff` is moves-and-repoints only (no logic edits) | All | Diff-shape is a human judgement, not a test assertion | After each commit, `git diff HEAD~1` shows only: new file w/ copied symbols, source w/ symbols removed + re-export added, import sites repointed — no added/removed branches, no value changes |

All *functional* behaviors have automated verification via the Phase 36 suite + the two new unit files.

---

## Behavior-Preservation Guardrails (from RESEARCH Validation Architecture)

1. **Suite green** after EACH extraction commit (`python -m pytest --tb=short -q` exits 0).
2. **Snapshot diff empty** — `python -m pytest --snapshot-update` produces no changes; `git diff tests/__snapshots__/` empty.
3. **xfailed stay xfailed** — `test_build_arg_flags_force_truthiness_not_existence` and `test_eprom_operation_error_not_labeled_as_communication_error` must NOT flip to xpassed (those are Phase 41/42 bugs, out of scope here).
4. **mypy watermark not exceeded** — `python tools/check_mypy_watermark.py` exits 0 (baseline 44).
5. **ruff gate green** — `ruff check` + `ruff format --check` exit 0 on touched modules; keep parked `# noqa: F403/F405` (star-import removal is Phase 39).
6. **Re-export landmine (D-07):** when frame primitives move, `serial_comm.py` MUST re-export `MAGIC_PREAMBLE`, `LogMessage`, `Response`, `_crc8_ccitt` (`# noqa: F401`) for `test_decoder.py` lines 50–55, or the suite breaks on import.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (`test_codec.py`, `test_address_parser.py`)
- [ ] No watch-mode flags
- [ ] Feedback latency < 18s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

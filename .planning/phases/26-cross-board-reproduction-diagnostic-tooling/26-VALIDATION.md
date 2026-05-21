---
phase: 26
slug: cross-board-reproduction-diagnostic-tooling
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-21
---

# Phase 26 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Phase 26's diagnostic IS the v1.6 acceptance-gate tool (Phase 29 reuses it). The validation
> contract below is also the cross-phase forward-compatibility contract — surfaces marked
> "LOAD-BEARING" must not change between v1.6 and v1.7+.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` (already pinned in `firestarter_app/pyproject.toml` dev extras) |
| **Config file** | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` (verified) |
| **Quick run command** | `cd firestarter_app && pytest tests/test_consistency_check.py -x` |
| **Full suite command** | `cd firestarter_app && pytest` |
| **Estimated runtime** | ~5s (test_consistency_check only) / ~30–60s (full suite) |

---

## Sampling Rate

- **After every task commit (Plan 26-01):** `cd firestarter_app && pytest tests/test_consistency_check.py -x` — all 6 D-10 cases use stubbed serial, no hardware required.
- **After every plan wave (Plan 26-01 → branch tip):** `cd firestarter_app && pytest` — full suite green; the 6 new tests bring total to 88+. Must remain at 82/82 or higher passing.
- **Per bench session (Plan 26-02):** Operator runs `firestarter -p /dev/ttyXXX dev consistency-check <chip> --runs 3 --output-dir .planning/v1.6/<chip>-<board>-<TS>/` once per board (3 invocations total). Verdict captured to `.planning/v1.6-EVIDENCE.md`.
- **Before `/gsd-verify-work 26`:** Full pytest suite green + `.planning/v1.6-EVIDENCE.md` has 3 rows under Phase 26 baseline section (one per board, all `FAIL (jitter reproduced)` expected per the 3-shield-invariant prediction).
- **Max feedback latency:** ~5 seconds for unit tests; bench wave is operator-paced (one session, ~15–30 min total).

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 26-01-01 | 01 | 0 | REPRO-03 | — | Failing test scaffolds present; serial layer stubbed (no hardware required for CI). | unit (RED) | `cd firestarter_app && pytest tests/test_consistency_check.py -x` (expect 6 failures) | ❌ Wave 0 | ⬜ pending |
| 26-01-02 | 01 | 1 | REPRO-03 / D-10 #1 | — | All N runs identical → exit 0; single SHA reported. | unit | `cd firestarter_app && pytest tests/test_consistency_check.py::test_all_runs_identical_pass_exit_0 -x` | ❌ Wave 0 | ⬜ pending |
| 26-01-03 | 01 | 1 | REPRO-03 / D-10 #2 | — | Byte differs at 0x123 in run 2 → exit 1; first-divergence offset reported correctly. | unit | `pytest tests/test_consistency_check.py::test_one_byte_differs_in_run_2_exit_1 -x` | ❌ Wave 0 | ⬜ pending |
| 26-01-04 | 01 | 1 | REPRO-03 / D-10 #3 | — | Full scramble across 3 runs → exit 1, Distinct SHAs: 3, divergence at offset 0x0000. | unit | `pytest tests/test_consistency_check.py::test_full_scramble_three_distinct_shas -x` | ❌ Wave 0 | ⬜ pending |
| 26-01-05 | 01 | 1 | REPRO-03 / D-10 #4 | — | Stubbed state machine raises `EpromOperationError` → exit 2; no SHA reported for failed run. | unit | `pytest tests/test_consistency_check.py::test_serial_timeout_exit_2 -x` | ❌ Wave 0 | ⬜ pending |
| 26-01-06 | 01 | 1 | REPRO-03 / D-10 #5 | — | `--keep-files False` → output dir removed after verdict. | unit | `pytest tests/test_consistency_check.py::test_no_keep_files_removes_output_dir -x` | ❌ Wave 0 | ⬜ pending |
| 26-01-07 | 01 | 1 | REPRO-03 / D-10 #6 | — | `--runs 1` and `--runs 0` rejected → exit 2 with clear message. | unit | `pytest tests/test_consistency_check.py::test_runs_boundary_rejected -x` | ❌ Wave 0 | ⬜ pending |
| 26-01-08 | 01 | 1 | REPRO-03 (forward-compat / Phase 29) | — | Stdout verdict block format pinned via regex assertions on key lines (`Consistency check: (PASS\|FAIL)`, `Distinct SHAs: \d+`, `First divergence: offset 0x[0-9A-F]+`). | unit (regression) | `pytest tests/test_consistency_check.py::test_stdout_verdict_block_format -x` | ❌ Wave 0 | ⬜ pending |
| 26-01-09 | 01 | 1 | REPRO-03 (dispatch chain) | — | `main.py args.dev_command == "consistency-check"` reaches `EpromOperator.consistency_check_eprom` with the right kwargs. | integration (stubbed end-to-end) | `pytest tests/test_consistency_check.py::TestDispatchChain::test_main_dispatch_invokes_consistency_check -x` | ❌ Wave 0 | ⬜ pending |
| 26-02-01 | 02 | 2 | REPRO-01 | — | Operator runs `firestarter -p /dev/ttyACM0 dev consistency-check <chip> --runs 3` against `uno`; FAIL (or evidence-bearing PASS) recorded in evidence file. | bench (manual UAT) | (operator-on-bench; verdict + SHAs pasted into `.planning/v1.6-EVIDENCE.md`) | bench-only | ⬜ pending |
| 26-02-02 | 02 | 2 | REPRO-02 | — | Operator runs `firestarter -p /dev/ttyACM1 dev consistency-check <chip> --runs 3` against `leonardo`; outcome captured either way (jitter or explicitly absent with evidence). | bench (manual UAT) | (operator-on-bench) | bench-only | ⬜ pending |
| 26-02-03 | 02 | 2 | ROADMAP SC#5 | — | Pre-fix baseline rows for all 3 boards committed to `.planning/v1.6-EVIDENCE.md` per D-08 schema (9 columns: Board, Port, Chip, N, SHAs distinct, Divergent bytes, First-diverge offset, Verdict, Log). | bench (manual UAT) | `grep -E '^\| (uno\|leonardo\|uno328pb) \|' .planning/v1.6-EVIDENCE.md` returns 3 rows | bench-only | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tests/test_consistency_check.py` — 6 D-10 test cases land as failing scaffolds in Wave 0; Wave 1 implements `consistency_check_eprom` to flip them green. Reuse `tests/conftest.py` fixtures (`fake_serial`, `make_comm`, `build_frame`).
- [ ] `firestarter_app/tests/test_consistency_check.py::TestDispatchChain` — integration test verifying `args.dev_command` dispatch reaches `EpromOperator.consistency_check_eprom`. **Recommended; not in D-10 explicitly.**
- [ ] `tests/test_consistency_check.py::test_stdout_verdict_block_format` — golden / regex snapshot of the verdict block format. Guards Phase 29 forward-compat contract.
- [ ] `.planning/v1.6-EVIDENCE.md` — created by Plan 26-02 first task (header + empty Phase 26 baseline table). Operator-driven appends follow during bench wave.

**Framework install:** No install needed — pytest already pinned. No environment-level gaps.

---

## Cross-tool Forward Compatibility (Phase 29 reuse contract)

Phase 26's diagnostic IS Phase 29's acceptance-gate tool. The following surfaces are **LOAD-BEARING** and must not change between v1.6 and v1.7+:

| Surface | Contract | Reason |
|---------|----------|--------|
| Exit code semantics (D-05) | `0`=PASS, `1`=FAIL, `2`=hardware-error | Phase 29 VERIFY-01/02/03 gate on `exit 0`; any drift breaks the gate. |
| Stdout verdict block lines | Exact strings `"Consistency check: PASS"` / `"Consistency check: FAIL"` | Phase 29 evidence-accretion scripts grep these. |
| `--runs N` flag semantics | N≥2 required; default 3 | Phase 29 uses `--runs 5` — must accept higher N without behavior change. |
| Per-run artifact filename pattern | `run_{N:02d}.bin` (zero-padded 2-digit) | Phase 29 may diff pre-fix vs post-fix artifacts; consistent naming required. |
| Output dir naming pattern (default) | `consistency-check-<chip>-<board>-<TS>/` | Operator mental model from Phase 26 carries to Phase 29. |
| Evidence-file row schema (D-08) | 9 columns: Board, Port, Chip, N, SHAs distinct, Divergent bytes, First-diverge offset, Verdict, Log | Phase 27/28/29 all append rows — schema drift breaks the markdown table. |

The `test_stdout_verdict_block_format` test in Wave 0 pins surfaces 1–3 above by regex. Surfaces 4–6 are pinned by Plan 26-02 first row populating the evidence file at the locked schema.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live cross-board jitter reproduction on uno | REPRO-01 | Requires operator-owned hardware (Arduino Uno + RURP shield + a static-state EPROM in socket). No CI hardware. | Operator: plug `uno` on `/dev/ttyACM0`, mount shield, socket SST27SF512 (or other static chip), then `firestarter -p /dev/ttyACM0 dev consistency-check SST27SF512 --runs 3 --output-dir .planning/v1.6/uno-SST27SF512-$(date +%Y%m%d-%H%M%S)/`. Paste verdict block + per-run SHAs into `.planning/v1.6-EVIDENCE.md` row. |
| Live cross-board jitter reproduction on leonardo | REPRO-02 | Hardware-only (Arduino Leonardo, 1024-byte buffer board). | Same as above but `-p /dev/ttyACM1` and `leonardo` board. Capture outcome even if jitter is absent (refutes hypothesis; expand RCA scope). |
| Live cross-board jitter reproduction on uno328pb | ROADMAP SC#2 / SC#5 | Hardware-only (328PB-Uno via urclock bootloader on `/dev/ttyUSB0` per `[[project_bench_findings_v15]]`). | `firestarter -p /dev/ttyUSB0 dev consistency-check SST27SF512 --runs 3`. Expected: ~57.8% byte diff matching the 2026-05-21 triage baseline. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies (the 3 bench tasks are manual UAT, captured under Manual-Only Verifications above)
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (Wave 0 tests cover the dispatch chain, all 6 D-10 cases, and the forward-compat regex pin — 9 automated assertions across Plan 26-01)
- [ ] Wave 0 covers all MISSING references (test file, fixtures already exist in conftest.py)
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s for unit tests
- [ ] `nyquist_compliant: true` set in frontmatter (after Plan 26-01 Wave 1 is green)

**Approval:** pending

---
phase: 112-dev-test-handler-wiring
verified: 2026-07-03T00:00:00Z
status: human_needed
score: 8/8 must-haves verified
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "On Leonardo + Rev 2.0 with an electrically-erasable chip (W27C512 or W29C020), run `firestarter dev test <chip> --destructive` on the physical bench."
    expected: "The rendered report's voltage row shows vpp_before_mv/vpp_after_mv and vpe_before_mv/vpe_after_mv tracking real rail behavior across the write pulse (a plausible droop under load), not flat/static/absent values."
    why_human: "Requires live serial connection to real hardware (Leonardo board, Rev 2.0 shield, a real EPROM) — cannot be exercised via CliRunner + mocked HardwareManager. This is the Phase-111 SC2 bench re-verify explicitly deferred by both 112-02-SUMMARY.md and 112-03-SUMMARY.md; the software wiring (sampler bracketing, exit codes, TTY gating, dual-artifact write) is fully unit-tested and does not depend on this check passing."
---

# Phase 112: dev test Handler Wiring Verification Report

**Phase Goal:** `firestarter dev test <chip>` exists as a runnable command a community member can actually type — every piece built in Phases 108–111 is reachable from one CLI invocation with sensible defaults and a clear exit code.
**Verified:** 2026-07-03
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `firestarter dev test <chip>` is a registered Click subcommand (sibling of `dev validate-family`), accepting chip / `--destructive` / `--output-dir` / `-y`, running the full sweep → report flow | ✓ VERIFIED | `cli_handlers.py:1784` `@dev.command(name="test")`, `:1815 def dev_test(app, chip, destructive, output_dir, assume_yes)`. Confirmed live: `cli.commands['dev'].commands['test']` exists; `CliRunner(['dev','test','--help'])` lists positional `CHIP` + `--destructive`/`--output-dir`/`-y,--yes`. |
| 2 | Without `--destructive` → non-destructive plan (id+read+blank-check), Phase-109 banner intact; with `--destructive` → full plan (write/erase/verify) | ✓ VERIFIED | `derive_plan(chip, app.db, destructive=destructive)` at `cli_handlers.py:1854` — `chip_test.py:318-420 derive_plan` structurally omits write/erase steps into `locked_destructive` when `destructive=False` (SAFE-01). `report.banner = count_applicable(plan, results)` at `:1873` wires the SWEEP-05 N-of-M banner into the report. `TestExitCodeMapping::test_non_destructive_n_less_than_m_still_exits_0` proves write/erase are never called on a non-destructive run. |
| 3 | 3-way exit code (0 clean; 1 any BAD incl. chip-ID mismatch; 2 marginal/indeterminate with no BAD; N<M non-destructive still 0) — `max` over per-verdict codes | ✓ VERIFIED | `_VERDICT_EXIT_CODES` map + `_verdict_code()` (`cli_handlers.py:1660-1673`); `sys.exit(max(_verdict_code(r.verdict) for r in results))` at end of handler. `TestExitCodeMapping` (6 tests, all pass): clean non-destructive→0, clean destructive→0, BAD write→1, marginal disagreement→2, chip-ID mismatch→1 (write never called), N<M clean→0. |
| 4 | Handler unit-testable without hardware via `EpromDatabase(skip_local_override=True)` + mock operator (CliRunner) — `tests/test_dev_test_cmd.py` (16 tests) | ✓ VERIFIED | `tests/test_dev_test_cmd.py` exists, uses `EpromDatabase(skip_local_override=True)` + `Mock(spec=EpromOperator)` + `Mock(spec=HardwareManager)`; `python -m pytest tests/test_dev_test_cmd.py -q` → 16 passed. No serial/hardware access. |
| 5 | D-04 decoupling: `chip_test.py` does NOT import `hardware.py`; `run_plan` has optional `sampler` bracketing OP_WRITE; hardware thunk built in the handler | ✓ VERIFIED | `grep -c 'import hardware\|from firestarter.hardware\|from firestarter import hardware' firestarter/chip_test.py` → 0. `run_plan`/`_run_step`/`_dispatch_step`/`_dispatch_multi_run` all carry `sampler: Any = None` (chip_test.py:507,663,707,829); `_sample(sampler, phase)` brackets `operator.write_eprom` only inside the `OP_WRITE` branch (`:868`/`:870`), swallowing exceptions. `_make_sampler` closure built in `cli_handlers.py:1760-1780`, closing over `app.hardware_manager.sample_vpp_mv/sample_vpe_mv`. |
| 6 | SAFE-01/02/03 prohibitions: host-only, no new firmware dispatch, no VPP-set, no `--force`, no raw wire-dict in the handler | ✓ VERIFIED | `grep -nE 'set_vpp\|enable_vpp\|write_vpp\|vpp_enable\|assert_vpp\|raise_vpp' cli_handlers.py` → 0 hits. `awk` scoped from `dev.command(name="test")` to EOF for `force`/`--force` → 0 hits. `--destructive` is `is_flag=True` only, never read via `config_manager.get_value`. |
| 7 | SAFE-03 AST checker repointed from nonexistent `dev_test_cli.py` stub to real `cli_handlers.py`, function-scoped to `dev_test` + helpers; exits 0 and PASS line names `cli_handlers.py`; paired negative-fixture test proves non-zero on planted violation (anti-hollow) | ✓ VERIFIED | `grep -n dev_test_cli.py tools/check_devtest_orchestrator.py` → 0 lines. Live run: `python tools/check_devtest_orchestrator.py` → exit 0, `PASS: scanned ../firestarter/chip_test.py, ../firestarter/cli_handlers.py; 0 VPP-set, 0 raw-wire-dict, 0 --force`. `_scan_target_functions` (AST FunctionDef-name filter) scopes the handler scan to `dev_test` + 6 helpers — a deliberate, documented deviation from the plan's literal "whole-file scan" instruction, correctly avoiding 10 pre-existing legitimate `--force` flags on unrelated commands (`read`/`write`/`verify`/`blank`/`erase`/`id`). `test_checker_exits_nonzero_on_planted_handler_violation` and `test_checker_exits_nonzero_on_planted_handler_force_violation` write real fixture files to disk and invoke the checker via subprocess with `FIRESTARTER_DEVTEST_HANDLER` — both assert `returncode != 0` and `"FAIL:" in stdout`. Both pass. |
| 8 | Every piece built in Phases 108–111 is reachable from one CLI invocation (SWEEP/PATT/RPT/VOLT/XPORT) | ✓ VERIFIED | Handler composes `prompt_provenance(is_uv)` → `derive_plan` → `run_plan(sampler=...)` → `count_applicable` → `build_db_diff` → `DiagnosticReport` → `report.render(console)` → optional dual-artifact write → `sys.exit`. All key-link symbols imported and invoked (not merely imported) at `cli_handlers.py:1840-1904`. |

**Score:** 8/8 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/chip_test.py` | `sampler` threaded through run_plan/_run_step/_dispatch_step/_dispatch_multi_run | ✓ VERIFIED | Confirmed via grep + docstring read; 4-level threading present. |
| `firestarter_app/tests/test_chip_test.py` | New tests proving sampler bracket + no-op | ✓ VERIFIED | `-k sampler` selects 4 tests, all pass: brackets-write, not-invoked-around-non-write-ops, none-is-noop, exception-does-not-abort. |
| `firestarter_app/firestarter/cli_handlers.py` | New `@dev.command("test")` handler + composition helpers | ✓ VERIFIED | `dev_test` + `_verdict_code`/`_sanitize_chip_token`/`_is_uv_eprom`/`_chip_id_fields`/`_is_interactive`/`_make_sampler` all present, all invoked from the handler body. |
| `firestarter_app/tools/check_devtest_orchestrator.py` | `_DEVTEST_CLI_HANDLER` repointed to real handler; env-override seam | ✓ VERIFIED | `FIRESTARTER_DEVTEST_HANDLER` env var, `_DEFAULT_DEVTEST_HANDLER` → `cli_handlers.py`; `_HANDLER_FUNCTION_NAMES` frozenset scopes the scan. |
| `firestarter_app/tests/test_check_devtest_orchestrator.py` | Handler-shaped planted-violation test + clean baseline | ✓ VERIFIED | 10 tests total (up from 6); all pass including 2 planted-violation + 1 clean-baseline-with-handler-in-scope + 1 clean-fixture-env-override-sanity. |
| `firestarter_app/tests/test_dev_test_cmd.py` | CliRunner unit tests for the handler | ✓ VERIFIED | 16 tests across `TestExitCodeMapping`(6)/`TestPromptGating`(4)/`TestSamplerBracketing`(2)/`TestDualArtifactWrite`(4); all pass, all hardware-free (Mock specs, no real serial). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `dev_test` handler | `prompt_provenance` | TTY-gated call before sweep | ✓ WIRED | `cli_handlers.py:1840`; `TestPromptGating` proves on/off-TTY branches, `-y` scope. |
| `dev_test` handler | `derive_plan` | `derive_plan(chip, app.db, destructive=destructive)` | ✓ WIRED | `:1854`; destructive flag threaded straight from CLI option, no config/env read. |
| `dev_test` handler | `run_plan` (with sampler) | `run_plan(plan, app.eprom_operator, app.db, sampler=sampler)` | ✓ WIRED | `:1871`; sampler is `_make_sampler(...)` on destructive runs, `None` otherwise. |
| `run_plan` | `sampler("before"/"after")` | `_dispatch_multi_run`'s OP_WRITE branch | ✓ WIRED | `chip_test.py:868,870`; exception-swallowing via `_sample()`. |
| `_make_sampler` thunk | `hardware_manager.sample_vpp_mv/sample_vpe_mv` | direct calls, writes into report split slots | ✓ WIRED | `cli_handlers.py:1770-1778`; `TestSamplerBracketing` proves 4 calls on a 2-run destructive sweep, correct before/after slot population. |
| `dev_test` handler | `count_applicable` | banner assembly | ✓ WIRED | `:1873 report.banner = count_applicable(plan, results)`. |
| `dev_test` handler | `build_db_diff` | read-only DB-diff | ✓ WIRED | `:1892`. |
| `dev_test` handler | `report.render(console)` | unconditional stdout print | ✓ WIRED | Called before the `if output_dir:` branch and before `sys.exit`; `TestDualArtifactWrite::test_no_output_dir_writes_no_files_but_renders_stdout` proves render fires with no `--output-dir`. |
| `dev_test` handler | dual-artifact write | `dev-test-<chip>.json` / `.md`, guarded on `output_dir` | ✓ WIRED | `TestDualArtifactWrite` (4 tests) proves exactly 2 hyphenated files under `--output-dir`, zero files otherwise. |
| SAFE-03 checker | `cli_handlers.py` (scoped) | `_scan_target_functions` AST filter | ✓ WIRED | Live run confirms `cli_handlers.py` named in PASS line; anti-hollow proven by planted-violation tests. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `dev test` registered as Click subcommand | `python -c "from firestarter.cli_handlers import cli; assert 'test' in cli.commands['dev'].commands"` | No error | ✓ PASS |
| `dev test --help` lists all 4 flags | `CliRunner(['dev','test','--help'])` | chip arg + `--destructive`/`--output-dir`/`-y,--yes` all listed, exit 0 | ✓ PASS |
| SAFE-03 checker exits 0, names cli_handlers.py | `python tools/check_devtest_orchestrator.py` | `PASS: scanned ../firestarter/chip_test.py, ../firestarter/cli_handlers.py; 0 VPP-set, 0 raw-wire-dict, 0 --force`, exit 0 | ✓ PASS |
| `chip_test.py` imports no hardware module | `grep -c 'import hardware...' firestarter/chip_test.py` | 0 | ✓ PASS |
| `tests/test_dev_test_cmd.py` full pass | `pytest tests/test_dev_test_cmd.py -q` | 16 passed | ✓ PASS |
| `tests/test_check_devtest_orchestrator.py` full pass | `pytest tests/test_check_devtest_orchestrator.py -q` | 10 passed | ✓ PASS |
| `tests/test_chip_test.py` full pass | `pytest tests/test_chip_test.py -q` | 83 passed | ✓ PASS |
| Full suite green except one known pre-existing failure | `pytest tests/ -q` | 1 failed (`test_audit_coverage_matrix.py::test_golden_file_matches`), rest pass | ✓ PASS (expected) |
| Coverage floor held | `pytest tests/ -q --cov=firestarter --cov-fail-under=70` | 80.99% total, floor met | ✓ PASS |
| ruff clean | `ruff check` on all 6 touched files | All checks passed! | ✓ PASS |
| mypy watermark gate | `python tools/check_mypy_watermark.py` | 1 error, 34 below watermark (35) — pass | ✓ PASS |

### Pre-Existing Failure Verification (Not a Phase-112 Gap)

Per the task's explicit allowance, I independently verified `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` is pre-existing and out of scope:

- `git diff --stat 84c26cf HEAD -- .` shows **zero** changes to any coverage-matrix/ledger/golden/support_status/chip_database files across all of Phase 112's 6 commits (`b83d7e4`, `0b357bd`, `ccfb7e6`, `009c296`, `bdfb920`, `8f59374`).
- This proves the golden-file drift predates Phase 112 and Phase 112 touched none of the files that could have caused it.
- Confirmed tracked in `112-01-deferred-items.md` / `112-02-deferred-items.md`.

**Conclusion: correctly excluded from this phase's gap analysis, exactly as the task instructed.**

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| SWEEP-01..05 | 112-02 | Plan derivation, per-op verdicts, id-first gate, N≥2 runs/marginal, non-destructive default + banner | ✓ SATISFIED | `derive_plan` composed in handler; `TestExitCodeMapping` proves id-gate + N<M behavior. |
| PATT-01..03 | 112-02 | Address-derived pattern, fingerprint classifier, UV small-region variant | ✓ SATISFIED | Reachable via `run_plan`/`derive_plan` (built in Phases 108-109); handler invokes unmodified. |
| SAFE-01..03 | 112-03 | `--destructive` CLI-only gate; pure orchestrator; CI gate for zero new dispatch/VPP-set | ✓ SATISFIED | Verified directly — see Truths 6 & 7 above. |
| RPT-01..05 | 112-02 | Single-source dual-render report, auto-capture, error_code seam, provenance prompt, DB-diff | ✓ SATISFIED | `DiagnosticReport` assembly + `render()` + dual-artifact write all wired and tested. |
| VOLT-01 | 112-01, 112-02 | VPP/VPE mV sampler captured into report during write step | ✓ SATISFIED | Sampler thunk wired via `run_plan(sampler=...)`; `TestSamplerBracketing` proves before/after slot population. |
| XPORT-01 | 112-02 | Transport-health counters, degrade to "not measured" if unavailable | ✓ SATISFIED | `TransportHealth()` honestly defaults to all-`None`/not-measured (Phase 110 scope; correctly carried through, not faked). |

All 17 requirement IDs mapped in plan frontmatter (`112-01`: VOLT-01; `112-02`: SWEEP-01..05,PATT-01..03,RPT-01..05,VOLT-01,XPORT-01; `112-03`: SAFE-01..03) match REQUIREMENTS.md's Phase 108-111 origin table (`✓ Complete` for all). No orphaned requirements — this is an integration phase with no new REQ-IDs, as stated in the task.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` found in any of the 6 touched files | — | None |
| `cli_handlers.py` | 149 | "not yet implemented" string | ℹ️ Info | Pre-existing `map_typed_errors` error message unrelated to `dev_test` (line 149, far outside the `dev_test` handler which starts at line 1650+); not a Phase-112 stub. |

No blockers. No debt markers requiring follow-up-issue references.

### Human Verification Required

### 1. Phase-111 SC2 Bench Re-Verify (Hardware-Gated)

**Test:** On Leonardo + Rev 2.0 with an electrically-erasable chip (W27C512 or W29C020), run `firestarter dev test <chip> --destructive` against real hardware.
**Expected:** The rendered report's voltage row shows `vpp_before_mv`/`vpp_after_mv` and `vpe_before_mv`/`vpe_after_mv` tracking real rail behavior (a plausible droop under load) across the write pulse — not flat, static, or absent values.
**Why human:** Requires a live serial connection to real hardware; cannot be exercised through `CliRunner` + `Mock(spec=HardwareManager)`. This is explicitly documented as deferred in both `112-02-SUMMARY.md` and `112-03-SUMMARY.md` ("Deferred hardware-gated UAT item (not blocking)"). The software wiring — sampler bracketing, exit-code mapping, TTY gating, dual-artifact write — is fully unit-tested and does not depend on this bench check passing.

### Gaps Summary

No gaps found. All 8 derived observable truths (covering SC1-SC3, D-01 through D-05, SAFE-01/02/03, and the D-04 engine/handler decoupling) are VERIFIED against the actual codebase — not just SUMMARY.md claims. Every artifact exists, is substantive, and is wired; every key link traces through real code, confirmed via live execution (not just static grep) where practical: the checker was run live (exit 0, PASS line names both files), the CLI subcommand was invoked live via CliRunner (`--help` output confirmed), and all three test modules (`test_chip_test.py`, `test_check_devtest_orchestrator.py`, `test_dev_test_cmd.py`) were executed directly by the verifier (109 tests total across the three, all passing). The one known pre-existing test failure was independently re-confirmed as unrelated to this phase via a `git diff --stat` against the pre-Phase-112 commit `84c26cf`, showing zero changes to any file that could affect that golden fixture.

The only outstanding item is the Phase-111 SC2 hardware bench re-verify, which is explicitly a deferred, hardware-gated UAT item per the task's own instructions — this routes the overall status to `human_needed` rather than `gaps_found`, since no software must-have failed.

---

_Verified: 2026-07-03_
_Verifier: Claude (gsd-verifier)_

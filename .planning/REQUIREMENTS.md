# Requirements: v1.30 SDP Surface Retirement & Behavioral Lock Proof

**Defined:** 2026-08-03
**Core Value:** Algorithm-first dispatch — the minipro `protocol_id` (`algorithm`) is the single
authoritative dispatch key end to end. v1.30 changes no dispatch: it replaces an unverifiable host
surface with a self-verifying one.

**Scope:** host-only (`firestarter_app/`). **No firmware change, no dual-repo lockstep, no `.hex`
re-cut.** Phase 119's `CMD_SDP_LOCK`/`CMD_SDP_UNLOCK` are what the new leg *exercises*.
**Phases continue at 131.**

---

## ⚠ Evidence Ceiling — read before planning any phase

No AT28C part has ever been in operator inventory and protocol `0x0D` stays `UNVERIFIED`.

> **Provable this milestone:** the *plan derivation* (43 ALLOW chips get four steps, 41 REFUSE get four
> NA steps carrying reasons — measurable today with zero hardware); the *read-back comparison logic*
> and every degenerate-input arm of it, in native envs; the SDP command *emission* only to the extent
> the host can observe it.
>
> **NOT provable this milestone:** the causal claim *"the lock inhibited the write."* That is reachable
> only on real silicon — i.e. only from a community `dev test` report, which **by design does not gate
> this milestone's close.**

**Two narrowings research added, which must not be smoothed over:**

1. **The Phase 116 ground-truth trace harness is UNREACHABLE from the host.** It is a PlatformIO
   `[env:native]` Unity binary in the *firmware* repo (`test/native/avr/test_sdp_harness/`,
   `test_eeprom28c_sdp/`), and its recorder hooks `rurp_write_data_buffer` / `rurp_set_control_pin`.
   The host repo has no bus stub at all. So "emission proof" here means what `tests/conftest.py`'s
   `build_frame` / `_FakeSerial` / `make_comm` can assert over a scripted wire — **not** a bus trace.

2. **A locked die is unrepresentable in either repo's stubs.** Both model the bus, never the die's
   protection state. No fixture can simulate real inhibition; fixtures can only pin the host's
   *response* to a scripted read-back.

Any artifact claiming more than this is the v1.22 C-5 overclaim class. CLOSE-01's claim gate exists to
make that mechanical rather than aspirational.

---

## v1 Requirements

### Gate Hardening & CI Parity (GATE)

Count-independent by design — hardens the *mechanism* and deliberately sets no watermark, so it can
land before the deletion's −6. Every later phase's "green suite" is unverified until the mypy gate can
actually fail.

- [x] **GATE-01**: The mypy watermark gate fails CLOSED — a mypy run that aborts, truncates, or exits
      with an unexpected returncode produces a non-zero gate exit, never a green.
      Evidence: mechanism `firestarter_app/tools/check_mypy_watermark.py` `9465c4c` (131-01);
      fail-provable proof `f76cf94` (131-02) —
      `tests/test_check_mypy_watermark.py::test_truncated_run_exits_2` and
      `::test_end_to_end_terminal_shape_is_legible`; the D-03 RED-preserving revert (131-02 Task 2,
      uncommitted, net diff empty) observed `test_truncated_run_exits_2` fail with
      `Failed: DID NOT RAISE SystemExit` before the guard order was restored byte-identically.

- [x] **GATE-02**: The gate consults `result.returncode` **before** the error-count regex, and requires
      mypy's `(checked N source files)` completion clause to be present.
      Evidence: mechanism `9465c4c` (131-01); proof `f76cf94` (131-02) —
      `tests/test_check_mypy_watermark.py::test_truncated_run_exits_2` (no `checked` clause ⇒ exit 2)
      and `::test_config_rejection_exits_2` (well-formed clause at returncode 1, still exit 2 on a
      config diagnostic — proves the ordering is independent of the clause).

- [x] **GATE-03**: The gate enforces a minimum-checked-files floor (`MIN_CHECKED_SOURCE_FILES = 120`),
      so a run that silently checks a subset fails instead of reporting a low count.
      Evidence: mechanism `9465c4c` (131-01); proof `f76cf94` (131-02) —
      `tests/test_check_mypy_watermark.py::test_below_coverage_floor_exits_2` (4 checked < 120 ⇒
      exit 2, message names both 4 and 120).

- [x] **GATE-04**: The gate invokes mypy as `sys.executable -m mypy`, not a bare `mypy` resolved from
      `PATH`.
      Evidence: mechanism `9465c4c` (131-01); proof `f76cf94` (131-02) —
      `tests/test_check_mypy_watermark.py::test_mypy_argv_is_sys_executable_dash_m`, a whole-list
      equality assertion against `[sys.executable, "-m", "mypy", "firestarter/", "tests/"]` via
      `subprocess.run` monkeypatched inside the checker's own module namespace.

- [x] **GATE-05**: `python_version` states mypy's true effective target (`3.10`), with a comment
      recording that the previous `"3.9"` value was silently discarded and never took effect.
      Evidence: `firestarter_app/pyproject.toml:139-155` (`[tool.mypy] python_version = "3.10"`,
      commit `9465c4c` on `gsd/v1.30-sdp-surface-retirement`) — `python3 -c "import tomllib,
      pathlib; print(tomllib.loads(pathlib.Path('pyproject.toml').read_text())['tool']['mypy']
      ['python_version'])"` prints `3.10`.

- [x] **GATE-06**: The gate has a paired pytest suite — its first ever — covering truncated-run ⇒
      exit 2, config-rejection ⇒ exit 2, over-watermark ⇒ exit 1, and below-coverage-floor ⇒ exit 2.
      Evidence: `firestarter_app/tests/test_check_mypy_watermark.py`, commit `f76cf94` (131-02) —
      8 tests: `test_truncated_run_exits_2`, `test_config_rejection_exits_2`,
      `test_over_watermark_exits_1`, `test_below_coverage_floor_exits_2`,
      `test_mypy_argv_is_sys_executable_dash_m`, `test_end_to_end_terminal_shape_is_legible`, plus
      two controls (`test_complete_error_run_returns_count_without_raising`,
      `test_clean_run_returns_zero_without_raising`) proving the classifier does not raise
      unconditionally. Registered in `tools/check_no_exists_proxy.py`'s `_DEFAULT_TARGETS` in the
      same commit (F-06).

- [x] **GATE-07**: One real `gh workflow run ci.yml` dispatch is recorded on the fork base, producing
      the current post-fork error count the watermark is later set from.
      Evidence: operator-dispatched CI run `30822281624` (`workflow_dispatch` on `beta` @
      `16a313a040389aa7c88a98b85f79a7d667ca2f6f`), recorded verbatim in
      `.planning/phases/131-gate-hardening-ci-parity/131-CI-BASELINE.md` (131-05) —
      `mypy errors: 69 (watermark: 35)`; re-read independently and ticked by 131-07. This count is
      an input to Phase 132's watermark, not a Phase 131 claim.

- [x] **GATE-08**: A `sdp_capability` 43 ALLOW / 41 REFUSE / 84 total count gate exists, **derived from
      the database rather than literal**, so narrowing a chip to REFUSE in order to green a failing
      field cannot pass silently. Evidence: `firestarter_app/tests/test_sdp_db_invariant.py`'s
      `test_sdp_partition_matches_committed_allow_list_element_wise` (element-wise parity against a
      committed 43-entry ALLOW snapshot) and `test_sdp_partition_counts_are_43_41_84` (the derived
      43/41/84 triple), both non-vacuous per
      `test_partition_flags_a_moved_chip_non_vacuous` (131-03).

- [x] **GATE-09**: The CI-parity recipe is documented and runnable as an acceptance leg — suite run
      once with the firmware-sibling root pointed at an empty directory and once with the sibling
      present, CI-scoped ruff, and one run with no board attached. Evidence:
      `firestarter_app/tools/ci_parity.sh` (four labelled legs, per-leg exit code, aggregate exit,
      `BOARD-ATTACHED` stamp) and `131-CI-PARITY.md`'s recorded run (`BOARD-ATTACHED: none`; legs
      1-3 exit 0, leg 4 exit 2 explained as the hardened gate working).

- [x] **GATE-10**: `check_devtest_orchestrator.py`'s handler-function list is derived, so a newly added
      `dev_test` helper cannot go silently unscanned. Evidence:
      `firestarter_app/tests/test_check_devtest_orchestrator.py`'s
      `test_every_helper_referenced_by_dev_test_is_listed` (body-only AST derivation of every
      `dev_test`-referenced helper, asserted as a subset of `_HANDLER_FUNCTION_NAMES`) and
      `test_derivation_flags_an_unlisted_helper_non_vacuous` (a synthetic unlisted helper is caught
      and named, and the decorator-list exclusion is proven positively) (131-04).

### `dev sdp` Retirement & mypy Discharge (RETIRE)

Smallest diff, largest unblocking effect: removes a row from 999.15's classification table, dissolves
the host/firmware contradiction rather than arbitrating it, and drops the honest mypy count 69 → 63 for
free. Must land before the watermark is re-baselined or the number moves within the same milestone.

- [x] **RETIRE-01**: `firestarter dev sdp` no longer exists — the command and its four gates are gone.
- [x] **RETIRE-02**: `tools/check_no_exists_proxy.py`'s fail-closed target list is updated in the **same
      commit** as the test-file move, so that gate never goes RED.

- [x] **RETIRE-03**: The four honesty assertions carried only by `test_dev_sdp_cmd.py` survive the move
      (`git mv`, retargeted onto the new leg), proven by a grep acceptance criterion showing no net loss.

- [x] **RETIRE-04**: `COMMAND_SDP_LOCK`/`COMMAND_SDP_UNLOCK` and their `COMMAND_NAMES` entries survive,
      with a test that dereferences both so a `KeyError` at operation setup cannot regress.
      Evidence: `firestarter_app` commit `831c95f` (132-08 task 1) —
      `tests/test_revision_constants_parity.py::test_command_names_dereferences_both_sdp_commands`
      dereferences `COMMAND_NAMES` with both `COMMAND_SDP_UNLOCK` and `COMMAND_SDP_LOCK`
      unconditionally (no `requires_fw` skip, so host-only CI catches a regression too), proven a
      real gate by two separate RED demonstrations — one per entry removed — each naming the
      missing constant and the operation-setup consequence.

- [x] **RETIRE-05**: A typed `AppContext` fixture exists in `tests/conftest.py` **before** any new test
      module is authored, so new modules cannot add errors of the 30-error pattern being fixed.

- [x] **RETIRE-06**: `firestarter_app`'s primary `ci` job is GREEN at the existing watermark of 35,
      achieved **without** touching the ring-fenced `eprom_operations.py` cluster.
      Evidence: CI run `30856059940` (`workflow_dispatch` on `gsd/v1.30-sdp-surface-retirement`
      @ `42a1971`), conclusion `success` — read via `gh run view`, never computed locally
      (`.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CI-GREEN.md`). The `ci`
      job's mypy gate step reports `mypy errors: 32 (watermark: 35)`, three below the unratcheted
      watermark; `git diff --stat firestarter/eprom_operations.py` stayed empty throughout. The
      sibling `ci-py32` job also passed but is outside this claim in both directions.

- [x] **RETIRE-07**: The removal-safety dependency is recorded as a tripwire, not a sentence in a note —
      a comment at the auto-unlock site plus a test named for the dependency, so that revisiting
      auto-unlock's default forces this decision to be revisited with it.

- [x] **RETIRE-08**: The stale `301`/`377` `COMMAND_NAMES` comment references are corrected to name
      `_setup_operation` (`eprom_operations.py:329`) first and `_operation_context` (`:405`) second,
      with each corrected line number alongside the function name (D-11) — a citation of the number
      alone re-stales, which is the defect this correction fixes.
      **Corrected in-phase: measured five stale references, not three, across two files.**
      `firestarter_app/firestarter/constants.py` carries one (the comment above
      `COMMAND_SDP_UNLOCK`/`COMMAND_SDP_LOCK`); `firestarter_app/tests/test_revision_constants_parity.py`
      carries four (a module-docstring citation, the `_check_command_names_coverage` docstring, one
      citation sitting inside an assertion *message* string — correcting it changed that test's
      failure text only, not its pass/fail behaviour — and the final test's docstring citation). The
      ring-fenced `eprom_operations.py` itself contains **zero** stale tokens and needed no edit,
      which is what makes the correction's two-file, five-site scope surprising against this
      requirement's original "three" text. Corrected here rather than deferred to Phase 137's
      CLOSE-01 (D-12): fixing five satisfies "three" a fortiori, but ticking this requirement while
      knowing its own text was wrong is the shape that closes as "three corrected" with two left
      behind, and deferring the wording would leave a wrong number in this file for five phases.
      Evidence: `firestarter_app` commit `42a1971` (132-08 task 2).

### The `dev test` SDP Leg — the Oracle (LEG)

The milestone's reason to exist. Research invalidated the design note's step table as written; these
requirements encode the corrected form.

- [x] **LEG-01**: For each of the 43 SDP-capable `0x0D` chips, `dev test` derives a four-step SDP leg
      from `sdp_capability()` — with **no new command-line option** (`dev test` keeps zero options).
      **Complete** (Phase 134 plan 134-03): `firestarter_app` commit `fcb3b28` (`derive_plan`'s SDP-leg
      emission block, `_SDP_LEG_STEP_ORDER`, calling `sdp_capability(name, db)` as the derivation source)
      + `f2f280c` — `tests/test_chip_test_sdp_leg.py::test_derive_plan_allow_population_emits_six_supported_ops`
      (all 43 measured ALLOW chips), `::test_derive_plan_allow_dev_test_exposes_zero_cli_options`
      (structural zero-`click.Option` check on the real `dev_test` command, not exit-code-only), and
      `::test_derive_plan_allow_flips_supported_when_sdp_capability_patched` (patches `sdp_capability` to
      return REFUSE for a really-ALLOW chip and observes the derived steps flip — proves derivation, not
      coincidence). ⚠ **D-06 CORRECTION, ticked with BOTH readings recorded, not silently satisfied**:
      this requirement's own text says a **four**-step leg; the leg actually derived and shipped is
      **SIX** steps, in order — `write-baseline-b` · `write-baseline-a` · `sdp-lock` · `write-inhibited`
      · `sdp-unlock` · `write-restored`. The inherited "four" predates LEG-04's two-transition-direction
      mandate and omits `write-restored` — the only step producing evidence the part was left writable
      again, on a family whose protection state cannot be read back. Both readings are recorded in
      `firestarter_app/firestarter/chip_test.py`'s `_SDP_LEG_STEP_ORDER` comment and in
      `134-03-SUMMARY.md`; six is what ships.

- [x] **LEG-02**: For each of the 41 capability-REFUSED chips, the leg's steps report NA/SKIPPED
      carrying the refusal reason, never a silent omission.
      **Complete** (Phase 134 plan 134-03): `firestarter_app` commit `fcb3b28` + `f2f280c` —
      `tests/test_chip_test_sdp_leg.py::test_derive_plan_refuse_population_emits_six_na_steps_with_reason`
      (**703 chips — every non-ALLOW entry in the database, a SUPERSET of the 41 protocol-`0x0D`
      REFUSE chips this row names.** Corrected 2026-08-04 by the phase verifier, which independently
      recomputed the test's actual population; the citation said 41. The behavior is proven more
      broadly than claimed, not less — but the number was wrong, and this phase polices exactly this
      class of discrepancy elsewhere. Each step's `reason` asserted EQUAL to
      `sdp_capability(name, db)[1]` — identity against the live function, never a substring match) and
      `::test_derive_plan_refuse_run_plan_reports_na_with_no_operator_call` (`run_plan` turns each
      unsupported step into `VERDICT_NA` with zero operator calls — the existing NA path, zero new
      machinery). At `write_scope="none"` (unreachable from a real `dev test` run since Phase 121's
      reversal) a REFUSE chip's SDP leg emits NOTHING at all — a plan-time refinement of D-18 recorded in
      `134-03-SUMMARY.md`, proven by commit `294cb97`'s
      `::test_refuse_write_scope_none_is_byte_identical_to_pre_phase134` and kept from breaking LEG-10's
      named `test_empty_registry_noop`.

- [x] **LEG-03**: The inhibited-write payload comes from its own named generator and is the bitwise
      complement of the baseline pattern — differing from it in **every** byte, and equal to neither
      all-`0x00` nor all-`0xFF`, so a blank read and a stuck-bus read stay distinguishable.
      **Complete** (Phase 134 plan 134-01): `generate_inhibited_pattern(start, length)` calls
      `generate_pattern` exactly once and bitwise-complements it; five tests
      (`tests/test_chip_test_sdp_leg.py::TestInhibitedPattern`, `pytest -k "pattern_b"`) prove
      equal-length, every-byte divergence, the anti-tautology check (B != a fresh `generate_pattern()`
      call), neither pattern degenerate, and D-05's non-laundering leg against the live
      `_FF_RATIO_THRESHOLD` — all against the live generators for the real `(0, 256)` region, never a
      byte literal. Non-vacuity obligation #1 observed RED once, then restored byte-identically.

- [x] **LEG-04**: The baseline step proves a write **transition** — write pattern B, verify, write
      pattern A, verify — before any lock is applied, so a chip carrying the pattern from an earlier run
      cannot yield a passing leg on a dead write path.
      **Complete** (Phase 134 plans 134-02 + 134-03): the transition *semantics* landed in 134-02
      (`_dispatch_sdp_leg`'s read-back-equality oracle; `test_dead_write_path_baseline_b_is_bad` proves
      the B direction is the leg's entire discriminating power, D-07); the *ordering* proof — that
      `write-baseline-b` and `write-baseline-a` both run, in that order, strictly BEFORE `sdp-lock` is
      ever attempted, on every ALLOW chip's derived plan — is 134-03's, commit `fcb3b28` (the emission)
      + `f2f280c` — `tests/test_chip_test_sdp_leg.py::test_derive_plan_baseline_transition_ordering`
      (both baseline directions present; `write-inhibited` strictly between lock/unlock; `write-restored`
      the LAST step in the plan).

- [x] **LEG-05**: The oracle is **read-back equality** against the baseline pattern. A write that merely
      reported failure is never accepted as evidence.
      Evidence: `firestarter_app` commit `7284c7d` (134-02 Task 1, `_dispatch_sdp_leg`'s no-default
      truth table) + commit `4ac946a` (134-02 Task 2) —
      `tests/test_chip_test_sdp_leg.py::test_oracle_readback_true_a_produces_ok`,
      `::test_oracle_readback_true_b_produces_bad` (D-03's polarity pin: `write_eprom`'s bool held
      CONSTANT at `True` across both, only the read-back varies — a bool-driven implementation cannot
      produce two different verdicts here), `::test_oracle_readback_false_a_produces_marginal`,
      `::test_oracle_readback_false_b_produces_marginal` (the precondition gate, both directions).
      Non-vacuity obligation #2 observed: swapping the `OP_WRITE_INHIBITED` OK/BAD arms produced 3 RED
      (not VALIDATION.md's stated 2 — a measured discrepancy recorded in `134-02-SUMMARY.md`: the
      required `lock_leaked` test independently duplicates one arm of the pair), then restored
      byte-identically.

- [x] **LEG-06**: A write that unexpectedly **succeeds** after the lock reports **BAD** and exits 1 —
      never SKIPPED, NA, or OK. This is the leg's whole value and the v1.22 defect class it detects.
      **Complete (both halves), Phase 134 plan 134-05.** Engine half: `firestarter_app` commit
      `4ac946a` (134-02 Task 2) — `tests/test_chip_test_sdp_leg.py::
      test_lock_leaked_write_ok_true_b_readback_is_bad` proves `(True, B) => BAD` at the engine level.
      Exit-code half: `firestarter_app` commits `d9b14ef`/`6596f4f` (D-14's `_overall_exit_code`
      explicit-precedence fix, replacing a `max` that let `marginal`'s exit code (2) numerically
      outrank BAD's (1)) and `c56fc32` — `tests/test_dev_test_cmd.py::TestExitPrecedenceLeg06::
      test_leaked_lock_exits_1` drives the real CLI end to end on the ALLOW chip AT28C256, asserting
      BOTH `exit_code == 1` AND the `write-inhibited` step's JSON-artifact verdict is `BAD` (the
      exit-code assertion alone would not discharge this — a laundering implementation could satisfy
      it via an unrelated BAD step). `test_mixed_bad_and_marginal_exits_1_not_2` pins the run
      containing BOTH a BAD step and a `marginal` step at exit 1, driven end to end (not via a direct
      call to `_overall_exit_code`), with non-vacuity obligation #5 observed RED (`assert 2 == 1`
      after reverting to the naive `max`) and restored byte-identically.

- [x] **LEG-07**: A **partial** read-back change reports BAD — this is gh#11's exact symptom.
      Evidence: `firestarter_app` commit `4ac946a` (134-02 Task 2) —
      `tests/test_chip_test_sdp_leg.py::test_partial_readback_reports_bad` (a 16-byte splice from the
      live pattern-A/B generators, never a literal).

- [x] **LEG-08**: A degenerate read-back — empty, short, all-`0x00`, or all-`0xFF` — reports BAD or
      marginal, never equality. (The mandated `_diff_offsets` primitive reads an empty read-back as
      perfect equality; the leg must not inherit that.)
      Evidence: `firestarter_app` commit `2699579` (134-02 Task 3) —
      `tests/test_chip_test_sdp_leg.py::test_degenerate_readback_empty_is_bad`,
      `::test_degenerate_readback_short_is_bad` (both BAD via the length gate, checked before any
      `classify_fingerprint` call — P-02's measured trap), `::test_degenerate_readback_all_zero_is_marginal`,
      `::test_degenerate_readback_all_ff_is_marginal_blank_contact` (both marginal, D-04's content-degeneracy
      split; `address-line` deliberately not asserted — unreachable at this leg's exact 256-byte region).

- [x] **LEG-09**: `sdp_unlock` is **exempt** from the destructive-op set, so a destructive gate closing
      after the lock can never skip the unlock and ship a locked part.
      Evidence: `firestarter_app` commit `ded8e3e` (133-03, `_DESTRUCTIVE_OPS` asymmetry) +
      commits `35d4571`/`23f895c`/`5c8fb09` (133-04, cleanup registry + criterion-3 proofs) —
      `tests/test_chip_test_sdp_leg.py::test_unlock_exempt_from_destructive`,
      `::test_gate_closed_from_start`, `::test_lock_ran_then_gate_closes` (mutation-proved: adding
      `OP_SDP_UNLOCK` to `_DESTRUCTIVE_OPS` was observed to fail the last test, then reverted).
      Qualifier (D-11): in Phase 133 this absence is forward-protection for Phase 134, since 133
      derives no plan-level SDP step for it to gate — see `133-RECORD.md` §3 Criterion 3.

- [x] **LEG-10**: `run_plan` drains a cleanup registry in a `finally`, so the unlock is attempted even
      when a mid-leg step raises.
      Evidence: `firestarter_app` commit `35d4571` (133-04, the registry + bare `try/finally` +
      per-callable drain) —
      `tests/test_chip_test_sdp_leg.py::test_finally_drains_on_exception`,
      `::test_keyboard_interrupt_drains_and_propagates`, `::test_system_exit_drains_and_propagates`,
      `::test_empty_registry_noop`, `::test_drain_continues_after_failure`,
      `::test_drain_does_not_mutate_results` (AST-level, over the installed source).
      Qualifier (D-07): on the propagating path, the unlock is attempted but the report is honestly
      forfeited — see `133-RECORD.md` §3 Criterion 1.

- [x] **LEG-11**: `_run_step` catches `SerialError` and `HardwareOperationError`, so a mid-leg transport
      timeout degrades that step rather than killing the whole report.
      Evidence: `firestarter_app` commit `9d7c0cc` (133-02, the four-clause `except` chain) —
      `tests/test_chip_test_sdp_leg.py::test_serial_timeout_degrades_one_step`,
      `::test_hardware_error_degrades_one_step`, `::test_run_fatal_escapes`,
      `::test_assertion_error_propagates`; plus the independent build-time proof, commit `feb90f6`
      (133-05) — `tests/test_check_devtest_orchestrator.py::test_checker_exits_nonzero_on_planted_broad_except`
      (and its three parametrised variants).

- [x] **LEG-12**: Every run on an ALLOW chip renders a `HELD` / `NOT-HELD` / `NOT-RUN(reason)` field in
      **both** the human report and the JSON artifact, so a non-running oracle is visible to a
      community reporter even at exit 0.
      Evidence: `firestarter_app` commits `c461cc0`/`8f3c712` (134-06, the carriage half —
      `DiagnosticReport.sdp_hold_state` field, `to_dict()` key, `render()` row, `SCHEMA_VERSION` 1.3)
      and `defb0f5`/`a20bcf9`/`361aafe` (134-07, the assigned-value half —
      `report.sdp_hold_state = sdp_hold_state(plan, results)` at the derive-in-engine/assign-in-handler
      seam) — `tests/test_dev_test_cmd.py::TestHoldStateLeg12::test_hold_state_held_reaches_both_surfaces`,
      `::test_hold_state_not_held_reaches_both_surfaces`,
      `::test_hold_state_not_run_reason_reaches_both_surfaces` (all three values, both surfaces, the
      `NOT-RUN` reason proven in both, `operator.sdp_lock.assert_not_called()`, and the banner's dropped
      `n_ran < m_applicable` ratio, all driven end to end through the real CLI).

- [x] **LEG-13**: The applicable-step count includes the SDP oracle for ALLOW chips regardless of
      outcome, so an NA/SKIPPED oracle **drops** the headline N-of-M ratio instead of leaving it perfect.
      A **pinning test only** (D-15's own measurement: `count_applicable` already counts the six SDP
      steps in M and already excludes a SKIPPED result from N for ALLOW chips — no counting logic was
      edited). Evidence: `firestarter_app` commit `2b7a702` (134-10 Task 3) —
      `tests/test_chip_test.py::test_count_applicable_sdp_gated_allow_chip_ratio_drops` (AT28C256,
      `write_scope="full"`, gated by a dead-write-path baseline: `m_applicable == 10`, `n_ran == 6` —
      the ratio drops from today's misleading "4 of 4"; a MEASURED DISCREPANCY against
      `134-CONTEXT.md`'s stated `n_ran=5` is recorded in the test's own docstring, carried forward from
      the identical finding in `134-04-SUMMARY.md`/`134-07-SUMMARY.md`), plus
      `::test_count_applicable_sdp_does_not_change_shipped_non_sdp_counting` (the two shipped
      `count_applicable` pins re-asserted unedited),
      `::test_count_applicable_refuse_chip_n_equals_m_is_out_of_leg13_scope` (the REFUSE `N == M`
      reading recorded as explicitly out of scope), and
      `::test_count_applicable_sdp_banner_row_renders_the_dropped_ratio` (the rendered banner text,
      `diagnostic_report.py`'s own row, no code edit).

- [x] **LEG-14**: The report states recovery in the word **"rewrite"** and never "erase" (`0x0D` has no
      erase operation at all), enforced by a committed grep over the SDP report strings.

- [x] **LEG-15**: An op-registration parity test proves every new op is registered in all required
      registries — converting eight fail-open registries into one fail-closed gate.
      Evidence: `firestarter_app` commit `57e8eb5` (133-06, `tests/test_op_registration_parity.py`) —
      `test_every_op_is_registered_or_exempt` (the main leg), `test_declared_registry_count_matches`,
      `test_exemption_empty_reason_fails`, `test_stale_row_fails` (the four D-12 guards),
      `test_non_registry_still_has_no_ops` (the inversion guard), and
      `test_altered_registry_copy_fails_parity_non_vacuous` (mutation-proved: a real
      `_DESTRUCTIVE_OPS` narrowing was observed to fail the gate, then reverted).
      Correction: the "eight" count above is measured-wrong — the real breakdown is 6 policed
      registries + 6 declared non-registries; see `133-RECORD.md` §3 Criterion 5.

- [x] **LEG-16**: A committed fixture whose chip starts holding the baseline pattern and whose write is
      a **no-op** makes the baseline step report BAD. Without it the dead-write-path defect is
      unobservable in a suite whose mocks always start blank.
      Evidence: `firestarter_app` commit `2699579` (134-02 Task 3) —
      `tests/test_chip_test_sdp_leg.py::_dead_write_path_operator` (the committed fixture: `write_eprom`
      claims success, `read_eprom` always yields pattern A regardless of what was written) +
      `::test_dead_write_path_baseline_b_is_bad` (D-07: the B direction is the leg's entire
      discriminating power — the shipped write/verify pair, A-only, could never detect this). Non-vacuity
      obligation #3 observed: making the fixture's write real (read-back returns the last write's actual
      source) made the baseline step go OK and the fixture's own test fail, then restored
      byte-identically.

- [x] **LEG-17**: Each of the six exit-code laundering routes has a test asserting both that
      `sdp_lock` was **not** called and that a visible `NOT-RUN` reason is rendered.
      Evidence: `firestarter_app` commits `2f75cb9` (134-10 Task 1) and `2072105` (134-10 Task 2) —
      R1/R2 (`tests/test_dev_test_cmd.py::TestLaunderingRoutesR1R2SyntheticChipId`) driven through a
      synthetic nonzero-`chip-id` `EpromDatabase` (`tests/fixtures/synthetic_nonzero_chip_id.py`,
      D-17) so the full id-step → gate → refusal causal chain is genuinely exercised, labelled
      unreachable in production today (every shipped SDP-ALLOW chip has `chip-id == 0`, re-measured
      live by `test_all_sdp_allow_chips_have_zero_chip_id_measured_live`) and never described as "the
      leg is gated by chip ID" (`grep -ci 'gated by chip[- ]id' tests/ firestarter/ -r` returns 0); R3
      (`TestLaunderingRoutesR3R4::test_r3_…`, a `resolve_chip` refusal mapping the SDP-leg steps to
      SKIPPED); R4 (`::test_r4_…`, a REFUSE chip's NA reason compared by identity against
      `sdp_capability(name, db)[1]`); R5/R6 (`tests/test_chip_test.py::test_r5_laundering_…`/
      `test_r6_laundering_…`, library-level: `write_scope="none"` locks all six ops with no `sdp_lock`
      call, and every SDP-ALLOW chip derives a non-empty `Plan.steps`). A seventh route (D-08's
      baseline gate) is named in the same test family and is not counted among these six — see
      `134-04-SUMMARY.md`.

- [x] **LEG-18**: gh#20 (AT28C256 `dev test` FAIL, open since 2026-07-30) is triaged against the
      baseline gate, with the finding recorded — it is the live instance of the "lock a part whose
      baseline write never worked" hazard.
      Evidence: `134-GH20-TRIAGE.md` (the finding: host `3.0.0b14`/`Rev 2.3`, `dedup_fingerprint`
      `00e121446ceb`, no lock ever emitted under the baseline gate, banner drops from "4 of 4" to
      "6 of 10" — a measured correction of `134-CONTEXT.md`'s stated "5 of 10", see `134-RECORD.md`
      §4) and `.planning/todos/pending/at28c256-write-path-failure-gh20.md` (the underlying defect,
      filed with `Owner: henols`, separate and still open). The finding is **recorded**, not posted —
      the public reply to gh#20 is Phase 137's (CLOSE-06), behind its blocking operator wording
      review.

### `write --sdp-relock` (RELOCK)

Must ship with the deletion — they are a pair, and deleting the lock before re-homing it strands the
only legitimate use case the deleted command served.

> **⏸ THE PAIR WAS SPLIT — 2026-08-03, operator decision.** Phase 135, which was to carry
> RELOCK-01…RELOCK-06, is **deferred out of v1.30** and filed as ROADMAP Backlog **999.28**. The
> deletion (RETIRE-\*, Phase 132) still ships in this milestone, so the paragraph above now describes an
> accepted cost rather than a satisfied constraint: **v1.30 strands exactly the use case that paragraph
> names.** Recorded, not argued away — ROADMAP §`Phase 135` and §`Phase 999.28` carry the consequences,
> and Phase 137's CLOSE-05/CLOSE-06 were amended so the release notes and the gh#12 reply describe a
> **withdrawal with no replacement**, never a migration to a command that does not exist.
>
> **RELOCK-01…RELOCK-06 are OUT of v1 scope** (see §Out of Scope). Their text below is left
> **unmodified** so promotion from 999.28 needs no re-authoring; only the checkbox changed, from `[ ]`
> to `⏸`, so nothing counts them as in-scope-pending. **RELOCK-07 is RETAINED in v1 scope**, re-homed
> from Phase 135 to **Phase 137**, with its target text and its line citations corrected below.

- ⏸ **RELOCK-01**: `firestarter write --sdp-relock` deliberately protects a part after a write,
      as the single user-facing way to do so.

- ⏸ **RELOCK-02**: An explicit verify pass runs on the `--sdp-relock` path; the default `write` path
      stays byte-identical to today. (`write` has no verify pass at all today — this is the added scope
      the decided polarity requires.)

- ⏸ **RELOCK-03**: On verify failure the relock is **skipped** and `sdp_lock` is provably not called.
- ⏸ **RELOCK-04**: A skipped relock is reported **loudly** — a mandatory final `WARNING:` line or a
      non-zero exit, asserted by test. Because protection state cannot be read back, an `INFO`-level
      skip leaves the user with **no way to ever discover the part is unprotected**.

- ⏸ **RELOCK-05**: `--sdp-relock` on a non-`0x0D` chip **refuses loudly** rather than
      warning-and-proceeding, because the lock sequence's magic-address bytes would land as data.

- ⏸ **RELOCK-06**: `--sdp-relock` on a capability-REFUSED chip refuses **before any hardware is
      energized** — this is where the deleted command's capability gate is repurposed, not discarded.

- [ ] **RELOCK-07**: The stale `--sdp-relock` "v1.23+" deferral labels are corrected to name
      **Backlog 999.28** — *not* this milestone, since the flag does not land here. Measured
      2026-08-03: `.planning/STATE.md:634` and `.planning/PROJECT.md:823`. **⚠ Verify both line numbers
      before editing; do not trust any citation in the record, including this one.** Four separate
      places cite this same pair of labels and no two agree: this requirement previously read
      `STATE.md:538` / `PROJECT.md:823`; `PROJECT.md:134-137` asserts the live lines are
      `STATE.md:532` / `PROJECT.md:705` while itself calling the design note's `STATE.md:154` /
      `PROJECT.md:671` stale; and `ROADMAP.md`'s v1.30 milestone-list entry still carries that
      `154`/`671` pair. Only `PROJECT.md:823` has ever been right. **Fix all four citation sites when
      you fix the labels** — otherwise this drifts a third time. Re-homed from Phase 135 to Phase 137
      on 2026-08-03; retained precisely *because* the labels have already gone stale once (they read
      "v1.23+", written before v1.23 became PY32F071 Integration) and deferring the fix with the
      feature would strand them again.

### Dev-Tools Channel Gating (CHAN)

999.15 / gh#8. The channel is the gate.

- [ ] **CHAN-01**: On a stable install, the `dev` group exposes only `dev read` and `dev test`.
- [ ] **CHAN-02**: Beta-only `dev` subcommands are gated by **not registering them** — a gated command
      is not invokable, not merely undocumented. (`hidden=` is a `--help` cosmetic, documented as such
      in this codebase's own source; gating by it is security-by-help-text.)

- [ ] **CHAN-03**: Invoking a gated `dev` subcommand on a stable install refuses informatively with a
      non-zero exit.

- [ ] **CHAN-04**: `dev --help` output is pinned on **both** channels via subprocess.
- [x] **CHAN-05**: The `dev` group docstring no longer warns off the stable users `dev read` and
      `dev test` are being kept for.

- [ ] **CHAN-06**: `dev reg`'s bench-tooling role — the held-erase-rail DMM proxy — survives via a
      source-checkout override designed up front, not discovered after it breaks.

- [ ] **CHAN-07**: The gate reads **no firmware source**. Four host gates were built that way in Phase
      117 and they failed OPEN.

### SDP Partition Provenance — Derive, Don't Transcribe (PROV)

> Added 2026-08-05 by operator decision, mid-milestone, as Phase 136.1. **Scope note, binding on
> every requirement below: this changes provenance, never verdicts.** The split stays 43 ALLOW / 41
> REFUSE / 84 — proven before scoping, by re-running Phase 120's derivation against a live fetch of
> the pinned minipro revision and getting a partition byte-identical to the committed
> `120-sdp-partition.json`. No requirement here may be discharged by moving a chip between buckets.

- [ ] **PROV-01**: `tools/build_db.py` decodes `infoic.xml` flags bit 14 (`0x4000`,
      `MP_OFF_PROTECT_BEFORE`) and bit 15 (`0x8000`, `MP_PROTECT_AFTER`) and emits both into
      `chip_database.json` as explicit fields, with a comment citing minipro `database.c` @ `a8efaed`.
      Baseline measured 2026-08-05: the file today has **zero** such fields (`grep -c` returns 0 for
      `flags`, `protect_off_before` and `protect_on_after`).

- [ ] **PROV-02**: The ALLOW/REFUSE partition is derived from the committed b15 field rather than the
      65-token `SDP_CAPABLE_TOKENS` transcription — or the transcription survives only alongside a
      gate proving it EQUAL to the derived answer. Phase 120's finding still binds: **no structural
      rule works and none ever will** (`DIP28_28C64` splits 15/20; `2817` differs in pinout from
      `2804`/`2816`). A committed per-chip field is not a structural rule; family/pinout/name-shape
      regeneration is, and stays forbidden.

- [ ] **PROV-03**: A fail-closed gate proves the committed partition equals the `infoic.xml`-derived
      partition at 43/41/84, and is **seen to fail** under a planted single-chip re-bucketing, with
      the observed message recorded. Phase 131's GATE-08 is re-pointed at the derived source so the
      count gate and the partition cannot drift apart.

- [ ] **PROV-04**: The derivation is reproducible from a clean checkout — script committed into
      `firestarter_app` rather than stranded in the archived v1.22 `120-*` phase directory, pinned to
      minipro revision `a8efaedc236c1d9718bd28299dfbb99536b010ff`, and documented as needing a fetch
      because `tools/infoic*.xml` is gitignored and absent. Phase 120's exact matching rules are
      preserved: key on the exact `part_number` token, strip the package suffix (`@SOIC28`), and **do
      not strip parentheticals** — stripping `(Non-Standard)` collapses `AT28C64B(Non-Standard)` onto
      the separate `AT28C64B` entry and fabricates a MIXED verdict.

- [ ] **PROV-05**: `doc/lockable-proms.md` §17's claim that "Atmel AT28C16 / 64 / 256" are SDP-capable
      is corrected — `AT28C16`, `AT28C16E,F` and plain `AT28C64` all measure b15=0 / `page_size=1` /
      byte-write. This error has now been reproduced twice from part-number familiarity, most recently
      in this milestone's own conversation, which is why it is a requirement and not a footnote.

- [ ] **PROV-06**: The "b15 ≈ page-write family marker" equivalence is refuted in-tree with its
      measurement: b15 disagrees with `page_size > 1` on **12 of 84** entries. A reader must not be
      able to substitute `page_size` for b15 and believe they have the same axis.

### Close — Honesty Ledger, Claim Gate, Outward Follow-up (CLOSE)

- [ ] **CLOSE-01**: A v1.30 claim gate is **authored and hosted by this phase**, armed and green, with a
      `PASS:` line naming this milestone's own four artifacts, and its own suite output recorded.

- [ ] **CLOSE-02**: The claim gate carries two target-resolution legs proving its default targets
      resolve inside its own phase directory, so a naive future copy fails loudly instead of scanning
      nothing at exit 0.

- [ ] **CLOSE-03**: A host-side claim scan in `firestarter_app/tools/` covers `diagnostic_report.py`'s
      string literals — the `dev test` report text that reaches strangers on every run, which **no gate
      scans today** — and it lives where CI actually runs.

- [ ] **CLOSE-04**: An honesty ledger pairs every permitted claim with its explicit non-claim, including
      the auto-unlock coupled-decision row and the evidence ceiling's two narrowings.

- [ ] **CLOSE-05**: Release notes carry a "Removed" section mapping `dev sdp disable` → `write`
      (automatic) and `dev sdp enable` → `write --sdp-relock`.

- [ ] **CLOSE-06**: The gh#12 follow-up reply is posted **behind a blocking operator wording review**,
      stating the substitution honestly — gh#12 asked for "enable/disable" and gets neither by that
      name — and without letting "now provable" drift into "now proven".

---

## Future Requirements

Deferred, tracked, not in this roadmap.

### Silicon Validation

- **FUT-SDP-01**: The causal claim *"the lock inhibited the write"* proven on real AT28C silicon, via a
  community `dev test` report. Structurally out of reach this milestone — no AT28C part exists in
  operator inventory. This is the requirement the whole leg is built to make *answerable*, and its
  absence is a stated ceiling, not a gap.

- **FUT-SDP-02**: `0x0D` graduates from `UNVERIFIED` in `PROTOCOL-LEDGER`. Gated on FUT-SDP-01.

### Type-Checking Floor

- **FUT-MYPY-01**: Restore type-level enforcement of the advertised `>=3.9` floor — either a py3.9 CI
  matrix leg or dropping 3.9 (EOL 2025-10-31). After GATE-05 nothing type-checks against the floor the
  package still advertises in `requires-python` and a classifier; ruff's `target-version = "py39"`
  carries the syntax/idiom half but cannot catch a py3.10+ *stdlib API* used on 3.9.
  Backlog twin: `.planning/ROADMAP.md` Phase 999.26.

- **FUT-MYPY-02**: The `eprom_operations.py` D-07 ring-fence resolved deliberately — 10 `[union-attr]`
  errors, one root cause (an `Optional` connection attribute never narrowed), one fix. Tied to the
  still-open read-bug RCA.

---

## Out of Scope

| Item | Reason |
|------|--------|
| Any firmware change | `CMD_SDP_LOCK`/`CMD_SDP_UNLOCK` ship as Phase 119 built them; the firmware is what the leg *exercises*. Host-only means no dual-repo lockstep, no `.hex` re-cut, no version-pair coupling. |
| Remapping a non-running oracle to exit 2 | **Operator decision, 2026-08-03.** Would change `dev test`'s published exit-code contract for community reporters already on b14/b15. The `HELD/NOT-HELD/NOT-RUN` field (LEG-12) and the N-of-M extension (LEG-13) deliver the visibility without the breakage. |
| Dissolving the `eprom_operations.py` D-07 ring-fence | **Operator decision, 2026-08-03.** `ci` reaches green at watermark 35 without it (RETIRE-06), so it is optional extra credit; dissolving it would reverse a deliberate deferral tied to the open read-bug RCA and turn a scoped phase open-ended. → FUT-MYPY-02. |
| A sixth `dev test` result status for "inconclusive" | **Anti-feature.** `marginal` already means exactly this end to end (exit 2, inconclusive disposition, no ladder tag, counts as "ran"), and an unrecognised verdict string exits 0 — a new status is itself a false-green path. |
| Any new `dev test` command-line option | `dev test` has taken zero options since Phase 121 D-05; the four flags were removed, not disabled. The leg is plan-derived or it does not ship. |
| A transitional `dev sdp` stub or deprecation shim | Clean removal, argued and decided. One day of pre-release exposure at decision time, no stable release ever carried it; CLOSE-05's "Removed" mapping and the gh#12 reply carry the migration instead. |
| A nonce or timestamp for the inhibited-write pattern | Non-reproducible community reports, and it breaks the `dedup_fingerprint` hash. LEG-03's deterministic complement gives full-byte sensitivity without either cost. |
| New runtime dependencies | The 6-package runtime closure stays untouched — this ships to PyPI. |
| Restoring the softened Phase-129 assert | **Operator decision, 2026-08-03 — deliberately not taken here.** `test_present_root_with_missing_target_raises_not_skips` was hardened by Phase 129, then softened to a skip outside any plan during the b15 hand-off, and that commit is v1.30's fork base. Left as-is, the defect-class downgrade becomes permanent by default. Recorded so it is a decision, not a discovery. **[⚠ CORRECTED 2026-08-03, Phase 131 plan 131-07 (131-CONTEXT.md D-17; full reasoning in 131-RECORD.md): this row is wrong on repo, on commit, and on substance. Wrong repo — the test is at `firestarter/tests/test_flash_path_record_sync.py:694`, the **firmware** repo, which this milestone does not touch at all; it is not in `firestarter_app`, and no downstream agent should hunt for it there. Wrong commit — the softening is firmware `1c511e8` ("scope the meta-root premise leg to skip when no meta root exists"), not app `5934a54` as this row's framing implies is v1.30's fork base; `5934a54` touched `tests/test_py32_flash_map_host.py` and `tests/test_scan_paths_resolve.py`, neither of which is that test. Wrong substance — the change is **premise-scoped**, not weakened: the gate's own subject, that a missing scan target raises `MissingScanTargetError` rather than skipping, is still hard-asserted wherever the premise holds; what was scoped is the environment premise (`META_PRESENT`), and the companion `test_absent_meta_claim_can_never_be_false` makes a false absence claim impossible by construction. This row's action is unchanged and remains correct — do not restore, do not touch the firmware repo; this is a record correction only, with no scope consequence. Note that STATE.md's own phrasing ("softened a Phase-129-authored hard assert to a skip — a defect-class change") is the source of this row's mischaracterisation and is itself imprecise; correcting STATE.md is not in Phase 131's scope, and the divergence is recorded rather than reconciled.]** |
| Filing the py3.9-drop backlog item | **Operator decision, 2026-08-03 — deliberately not filed.** Tracked here as FUT-MYPY-01 only; with no backlog stub it will present again rather than being scheduled. **[⚠ SUPERSEDED 2026-08-03, Phase 131 plan 131-01 (131-CONTEXT.md D-13): D-13, written later the same day in the same discussion session, read this row's own stated cost and elected to pay it. Backlog stubs filed as ROADMAP.md Phase 999.26 (the py3.9 type-checking floor) and Phase 999.27 (the mypy minimum-target treadmill, Python 3.10 EOLs 2026-10-31). FUT-MYPY-01 remains the requirement-side record; 999.26 cross-links it.]** |
| Raising the mypy watermark to 69 | Would ratify the accreted debt as the new floor. The measured path reaches 33 ≤ 35, so the existing watermark holds. |
| `write --sdp-relock` itself — RELOCK-01…RELOCK-06 | **⏸ Operator decision, 2026-08-03 — deferred, not cancelled.** Phase 135 was vacated out of this milestone and filed as ROADMAP Backlog **999.28**; the phase number was not reused (136/137 keep theirs). Requirement text is retained verbatim in §`write --sdp-relock` (RELOCK) with `⏸` checkboxes, so promotion needs no re-authoring. **⚠ The cost this row accepts:** §RELOCK's own opening sentence calls the deletion and the re-homing "a pair, and deleting the lock before re-homing it strands the only legitimate use case the deleted command served" — Phase 132 ships the deletion here, so v1.30 does the stranding. Between this release and 999.28's promotion there is **no supported way to deliberately protect an SDP part**, and on `0x0D` the protection bit cannot be read back, so a user cannot observe the resulting state either. Phase 137's CLOSE-05/06 were amended to state that as a **withdrawal with no replacement** rather than a migration to `write --sdp-relock` — announcing a command that does not exist in the shipped release is the same overclaim class as v1.22's C-5. **RELOCK-07 is NOT in this row** — it stayed in v1 scope, re-homed to Phase 137. |

---

## Traceability

Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| GATE-01 | Phase 131 | Complete |
| GATE-02 | Phase 131 | Complete |
| GATE-03 | Phase 131 | Complete |
| GATE-04 | Phase 131 | Complete |
| GATE-05 | Phase 131 | Complete |
| GATE-06 | Phase 131 | Complete |
| GATE-07 | Phase 131 | Complete |
| GATE-08 | Phase 131 | Complete |
| GATE-09 | Phase 131 | Complete |
| GATE-10 | Phase 131 | Complete |
| RETIRE-01 | Phase 132 | Complete |
| RETIRE-02 | Phase 132 | Complete |
| RETIRE-03 | Phase 132 | Complete |
| RETIRE-04 | Phase 132 | Complete |
| RETIRE-05 | Phase 132 | Complete |
| RETIRE-06 | Phase 132 | Complete |
| RETIRE-07 | Phase 132 | Complete |
| RETIRE-08 | Phase 132 | Complete |
| LEG-01 | Phase 134 | Complete |
| LEG-02 | Phase 134 | Complete |
| LEG-03 | Phase 134 | Complete |
| LEG-04 | Phase 134 | Complete |
| LEG-05 | Phase 134 | Complete |
| LEG-06 | Phase 134 | Complete |
| LEG-07 | Phase 134 | Complete |
| LEG-08 | Phase 134 | Complete |
| LEG-09 | Phase 133 | Complete |
| LEG-10 | Phase 133 | Complete |
| LEG-11 | Phase 133 | Complete |
| LEG-12 | Phase 134 | Complete |
| LEG-13 | Phase 134 | Complete |
| LEG-14 | Phase 134 | Complete |
| LEG-15 | Phase 133 | Complete |
| LEG-16 | Phase 134 | Complete |
| LEG-17 | Phase 134 | Complete |
| LEG-18 | Phase 134 | Complete |
| RELOCK-01 | ~~Phase 135~~ → Backlog 999.28 | ⏸ Deferred (out of v1 scope) |
| RELOCK-02 | ~~Phase 135~~ → Backlog 999.28 | ⏸ Deferred (out of v1 scope) |
| RELOCK-03 | ~~Phase 135~~ → Backlog 999.28 | ⏸ Deferred (out of v1 scope) |
| RELOCK-04 | ~~Phase 135~~ → Backlog 999.28 | ⏸ Deferred (out of v1 scope) |
| RELOCK-05 | ~~Phase 135~~ → Backlog 999.28 | ⏸ Deferred (out of v1 scope) |
| RELOCK-06 | ~~Phase 135~~ → Backlog 999.28 | ⏸ Deferred (out of v1 scope) |
| RELOCK-07 | ~~Phase 135~~ → **Phase 137** | Pending (retained, re-homed 2026-08-03) |
| CHAN-01 | Phase 136 | Pending |
| CHAN-02 | Phase 136 | Pending |
| CHAN-03 | Phase 136 | Pending |
| CHAN-04 | Phase 136 | Pending |
| CHAN-05 | Phase 136 | Complete |
| CHAN-06 | Phase 136 | Pending |
| CHAN-07 | Phase 136 | Pending |
| PROV-01 | Phase 136.1 | Pending |
| PROV-02 | Phase 136.1 | Pending |
| PROV-03 | Phase 136.1 | Pending |
| PROV-04 | Phase 136.1 | Pending |
| PROV-05 | Phase 136.1 | Pending |
| PROV-06 | Phase 136.1 | Pending |
| CLOSE-01 | Phase 137 | Pending |
| CLOSE-02 | Phase 137 | Pending |
| CLOSE-03 | Phase 137 | Pending |
| CLOSE-04 | Phase 137 | Pending |
| CLOSE-05 | Phase 137 | Pending |
| CLOSE-06 | Phase 137 | Pending |

**Coverage:**

- v1 requirements **as scoped 2026-08-03**: 56 total (GATE 10 · RETIRE 8 · LEG 18 · RELOCK 7 · CHAN 7 ·
  CLOSE 6)
- v1 requirements **in scope now**: **50** (GATE 10 · RETIRE 8 · LEG 18 · **RELOCK 1** · CHAN 7 ·
  CLOSE 6) — RELOCK-01…06 deferred out with Phase 135 on 2026-08-03 → Backlog 999.28
- Mapped to phases: 50 of 50 in-scope
- Unmapped: 0 ✓ full coverage
- Deferred: 6 (RELOCK-01…06) — mapped to Backlog 999.28, not to any v1.30 phase; retained verbatim in
  §`write --sdp-relock` (RELOCK) above and recorded in §Out of Scope

**Phase mapping:** GATE-\* → Phase 131 (Gate Hardening & CI Parity) · RETIRE-\* → Phase 132 (Retire
`dev sdp` & Discharge the mypy Debt) · LEG-09/10/11/15 → Phase 133 (SDP Leg Mechanism) · the remaining
14 LEG requirements → Phase 134 (The Plan-Derived SDP Oracle in `dev test`) · ~~RELOCK-\* → Phase 135
(`write --sdp-relock`)~~ **⏸ RELOCK-01…06 → Backlog 999.28 (deferred 2026-08-03, Phase 135 vacated and
NOT renumbered); RELOCK-07 → Phase 137** · CHAN-\* → Phase 136 (Dev-Tools Channel Gating) · CLOSE-\* →
Phase 137 (Close — Honesty Ledger, Claim Gate, gh#12 Follow-up). Phase 133/134 is a deliberate split of
the research spine's single combined "leg" phase (see ROADMAP.md §v1.30 for rationale). **Active phase
set: 131, 132, 133, 134, 136, 137 — six phases; the 135 slot is deliberately vacant.**

---

*Requirements defined: 2026-08-03 after four-stream research (`.planning/research/SUMMARY.md`,
R-1…R-9 + A-1…A-4) and four operator decisions.*

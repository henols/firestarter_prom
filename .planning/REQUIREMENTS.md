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
- [ ] **GATE-07**: One real `gh workflow run ci.yml` dispatch is recorded on the fork base, producing
      the current post-fork error count the watermark is later set from.
- [ ] **GATE-08**: A `sdp_capability` 43 ALLOW / 41 REFUSE / 84 total count gate exists, **derived from
      the database rather than literal**, so narrowing a chip to REFUSE in order to green a failing
      field cannot pass silently.
- [ ] **GATE-09**: The CI-parity recipe is documented and runnable as an acceptance leg — suite run
      once with the firmware-sibling root pointed at an empty directory and once with the sibling
      present, CI-scoped ruff, and one run with no board attached.
- [ ] **GATE-10**: `check_devtest_orchestrator.py`'s handler-function list is derived, so a newly added
      `dev_test` helper cannot go silently unscanned.

### `dev sdp` Retirement & mypy Discharge (RETIRE)

Smallest diff, largest unblocking effect: removes a row from 999.15's classification table, dissolves
the host/firmware contradiction rather than arbitrating it, and drops the honest mypy count 69 → 63 for
free. Must land before the watermark is re-baselined or the number moves within the same milestone.

- [ ] **RETIRE-01**: `firestarter dev sdp` no longer exists — the command and its four gates are gone.
- [ ] **RETIRE-02**: `tools/check_no_exists_proxy.py`'s fail-closed target list is updated in the **same
      commit** as the test-file move, so that gate never goes RED.
- [ ] **RETIRE-03**: The four honesty assertions carried only by `test_dev_sdp_cmd.py` survive the move
      (`git mv`, retargeted onto the new leg), proven by a grep acceptance criterion showing no net loss.
- [ ] **RETIRE-04**: `COMMAND_SDP_LOCK`/`COMMAND_SDP_UNLOCK` and their `COMMAND_NAMES` entries survive,
      with a test that dereferences both so a `KeyError` at operation setup cannot regress.
- [ ] **RETIRE-05**: A typed `AppContext` fixture exists in `tests/conftest.py` **before** any new test
      module is authored, so new modules cannot add errors of the 30-error pattern being fixed.
- [ ] **RETIRE-06**: `firestarter_app`'s primary `ci` job is GREEN at the existing watermark of 35,
      achieved **without** touching the ring-fenced `eprom_operations.py` cluster.
- [ ] **RETIRE-07**: The removal-safety dependency is recorded as a tripwire, not a sentence in a note —
      a comment at the auto-unlock site plus a test named for the dependency, so that revisiting
      auto-unlock's default forces this decision to be revisited with it.
- [ ] **RETIRE-08**: The three in-tree stale `301`/`377` `COMMAND_NAMES` comment references are
      corrected to `329`/`405`.

### The `dev test` SDP Leg — the Oracle (LEG)

The milestone's reason to exist. Research invalidated the design note's step table as written; these
requirements encode the corrected form.

- [ ] **LEG-01**: For each of the 43 SDP-capable `0x0D` chips, `dev test` derives a four-step SDP leg
      from `sdp_capability()` — with **no new command-line option** (`dev test` keeps zero options).
- [ ] **LEG-02**: For each of the 41 capability-REFUSED chips, the leg's steps report NA/SKIPPED
      carrying the refusal reason, never a silent omission.
- [ ] **LEG-03**: The inhibited-write payload comes from its own named generator and is the bitwise
      complement of the baseline pattern — differing from it in **every** byte, and equal to neither
      all-`0x00` nor all-`0xFF`, so a blank read and a stuck-bus read stay distinguishable.
- [ ] **LEG-04**: The baseline step proves a write **transition** — write pattern B, verify, write
      pattern A, verify — before any lock is applied, so a chip carrying the pattern from an earlier run
      cannot yield a passing leg on a dead write path.
- [ ] **LEG-05**: The oracle is **read-back equality** against the baseline pattern. A write that merely
      reported failure is never accepted as evidence.
- [ ] **LEG-06**: A write that unexpectedly **succeeds** after the lock reports **BAD** and exits 1 —
      never SKIPPED, NA, or OK. This is the leg's whole value and the v1.22 defect class it detects.
- [ ] **LEG-07**: A **partial** read-back change reports BAD — this is gh#11's exact symptom.
- [ ] **LEG-08**: A degenerate read-back — empty, short, all-`0x00`, or all-`0xFF` — reports BAD or
      marginal, never equality. (The mandated `_diff_offsets` primitive reads an empty read-back as
      perfect equality; the leg must not inherit that.)
- [ ] **LEG-09**: `sdp_unlock` is **exempt** from the destructive-op set, so a destructive gate closing
      after the lock can never skip the unlock and ship a locked part.
- [ ] **LEG-10**: `run_plan` drains a cleanup registry in a `finally`, so the unlock is attempted even
      when a mid-leg step raises.
- [ ] **LEG-11**: `_run_step` catches `SerialError` and `HardwareOperationError`, so a mid-leg transport
      timeout degrades that step rather than killing the whole report.
- [ ] **LEG-12**: Every run on an ALLOW chip renders a `HELD` / `NOT-HELD` / `NOT-RUN(reason)` field in
      **both** the human report and the JSON artifact, so a non-running oracle is visible to a
      community reporter even at exit 0.
- [ ] **LEG-13**: The applicable-step count includes the SDP oracle for ALLOW chips regardless of
      outcome, so an NA/SKIPPED oracle **drops** the headline N-of-M ratio instead of leaving it perfect.
- [ ] **LEG-14**: The report states recovery in the word **"rewrite"** and never "erase" (`0x0D` has no
      erase operation at all), enforced by a committed grep over the SDP report strings.
- [ ] **LEG-15**: An op-registration parity test proves every new op is registered in all required
      registries — converting eight fail-open registries into one fail-closed gate.
- [ ] **LEG-16**: A committed fixture whose chip starts holding the baseline pattern and whose write is
      a **no-op** makes the baseline step report BAD. Without it the dead-write-path defect is
      unobservable in a suite whose mocks always start blank.
- [ ] **LEG-17**: Each of the six exit-code laundering routes has a test asserting both that
      `sdp_lock` was **not** called and that a visible `NOT-RUN` reason is rendered.
- [ ] **LEG-18**: gh#20 (AT28C256 `dev test` FAIL, open since 2026-07-30) is triaged against the
      baseline gate, with the finding recorded — it is the live instance of the "lock a part whose
      baseline write never worked" hazard.

### `write --sdp-relock` (RELOCK)

Must ship with the deletion — they are a pair, and deleting the lock before re-homing it strands the
only legitimate use case the deleted command served.

- [ ] **RELOCK-01**: `firestarter write --sdp-relock` deliberately protects a part after a write,
      as the single user-facing way to do so.
- [ ] **RELOCK-02**: An explicit verify pass runs on the `--sdp-relock` path; the default `write` path
      stays byte-identical to today. (`write` has no verify pass at all today — this is the added scope
      the decided polarity requires.)
- [ ] **RELOCK-03**: On verify failure the relock is **skipped** and `sdp_lock` is provably not called.
- [ ] **RELOCK-04**: A skipped relock is reported **loudly** — a mandatory final `WARNING:` line or a
      non-zero exit, asserted by test. Because protection state cannot be read back, an `INFO`-level
      skip leaves the user with **no way to ever discover the part is unprotected**.
- [ ] **RELOCK-05**: `--sdp-relock` on a non-`0x0D` chip **refuses loudly** rather than
      warning-and-proceeding, because the lock sequence's magic-address bytes would land as data.
- [ ] **RELOCK-06**: `--sdp-relock` on a capability-REFUSED chip refuses **before any hardware is
      energized** — this is where the deleted command's capability gate is repurposed, not discarded.
- [ ] **RELOCK-07**: The stale `--sdp-relock` "v1.23+" deferral labels at `STATE.md:538` and
      `PROJECT.md:823` are corrected to name this milestone.

### Dev-Tools Channel Gating (CHAN)

999.15 / gh#8. The channel is the gate.

- [ ] **CHAN-01**: On a stable install, the `dev` group exposes only `dev read` and `dev test`.
- [ ] **CHAN-02**: Beta-only `dev` subcommands are gated by **not registering them** — a gated command
      is not invokable, not merely undocumented. (`hidden=` is a `--help` cosmetic, documented as such
      in this codebase's own source; gating by it is security-by-help-text.)
- [ ] **CHAN-03**: Invoking a gated `dev` subcommand on a stable install refuses informatively with a
      non-zero exit.
- [ ] **CHAN-04**: `dev --help` output is pinned on **both** channels via subprocess.
- [ ] **CHAN-05**: The `dev` group docstring no longer warns off the stable users `dev read` and
      `dev test` are being kept for.
- [ ] **CHAN-06**: `dev reg`'s bench-tooling role — the held-erase-rail DMM proxy — survives via a
      source-checkout override designed up front, not discovered after it breaks.
- [ ] **CHAN-07**: The gate reads **no firmware source**. Four host gates were built that way in Phase
      117 and they failed OPEN.

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
| Restoring the softened Phase-129 assert | **Operator decision, 2026-08-03 — deliberately not taken here.** `test_present_root_with_missing_target_raises_not_skips` was hardened by Phase 129, then softened to a skip outside any plan during the b15 hand-off, and that commit is v1.30's fork base. Left as-is, the defect-class downgrade becomes permanent by default. Recorded so it is a decision, not a discovery. |
| Filing the py3.9-drop backlog item | **Operator decision, 2026-08-03 — deliberately not filed.** Tracked here as FUT-MYPY-01 only; with no backlog stub it will present again rather than being scheduled. **[⚠ SUPERSEDED 2026-08-03, Phase 131 plan 131-01 (131-CONTEXT.md D-13): D-13, written later the same day in the same discussion session, read this row's own stated cost and elected to pay it. Backlog stubs filed as ROADMAP.md Phase 999.26 (the py3.9 type-checking floor) and Phase 999.27 (the mypy minimum-target treadmill, Python 3.10 EOLs 2026-10-31). FUT-MYPY-01 remains the requirement-side record; 999.26 cross-links it.]** |
| Raising the mypy watermark to 69 | Would ratify the accreted debt as the new floor. The measured path reaches 33 ≤ 35, so the existing watermark holds. |

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
| GATE-07 | Phase 131 | Pending |
| GATE-08 | Phase 131 | Pending |
| GATE-09 | Phase 131 | Pending |
| GATE-10 | Phase 131 | Pending |
| RETIRE-01 | Phase 132 | Pending |
| RETIRE-02 | Phase 132 | Pending |
| RETIRE-03 | Phase 132 | Pending |
| RETIRE-04 | Phase 132 | Pending |
| RETIRE-05 | Phase 132 | Pending |
| RETIRE-06 | Phase 132 | Pending |
| RETIRE-07 | Phase 132 | Pending |
| RETIRE-08 | Phase 132 | Pending |
| LEG-01 | Phase 134 | Pending |
| LEG-02 | Phase 134 | Pending |
| LEG-03 | Phase 134 | Pending |
| LEG-04 | Phase 134 | Pending |
| LEG-05 | Phase 134 | Pending |
| LEG-06 | Phase 134 | Pending |
| LEG-07 | Phase 134 | Pending |
| LEG-08 | Phase 134 | Pending |
| LEG-09 | Phase 133 | Pending |
| LEG-10 | Phase 133 | Pending |
| LEG-11 | Phase 133 | Pending |
| LEG-12 | Phase 134 | Pending |
| LEG-13 | Phase 134 | Pending |
| LEG-14 | Phase 134 | Pending |
| LEG-15 | Phase 133 | Pending |
| LEG-16 | Phase 134 | Pending |
| LEG-17 | Phase 134 | Pending |
| LEG-18 | Phase 134 | Pending |
| RELOCK-01 | Phase 135 | Pending |
| RELOCK-02 | Phase 135 | Pending |
| RELOCK-03 | Phase 135 | Pending |
| RELOCK-04 | Phase 135 | Pending |
| RELOCK-05 | Phase 135 | Pending |
| RELOCK-06 | Phase 135 | Pending |
| RELOCK-07 | Phase 135 | Pending |
| CHAN-01 | Phase 136 | Pending |
| CHAN-02 | Phase 136 | Pending |
| CHAN-03 | Phase 136 | Pending |
| CHAN-04 | Phase 136 | Pending |
| CHAN-05 | Phase 136 | Pending |
| CHAN-06 | Phase 136 | Pending |
| CHAN-07 | Phase 136 | Pending |
| CLOSE-01 | Phase 137 | Pending |
| CLOSE-02 | Phase 137 | Pending |
| CLOSE-03 | Phase 137 | Pending |
| CLOSE-04 | Phase 137 | Pending |
| CLOSE-05 | Phase 137 | Pending |
| CLOSE-06 | Phase 137 | Pending |

**Coverage:**
- v1 requirements: 56 total (GATE 10 · RETIRE 8 · LEG 18 · RELOCK 7 · CHAN 7 · CLOSE 6)
- Mapped to phases: 56
- Unmapped: 0 ✓ full coverage

**Phase mapping:** GATE-\* → Phase 131 (Gate Hardening & CI Parity) · RETIRE-\* → Phase 132 (Retire
`dev sdp` & Discharge the mypy Debt) · LEG-09/10/11/15 → Phase 133 (SDP Leg Mechanism) · the remaining
14 LEG requirements → Phase 134 (The Plan-Derived SDP Oracle in `dev test`) · RELOCK-\* → Phase 135
(`write --sdp-relock`) · CHAN-\* → Phase 136 (Dev-Tools Channel Gating) · CLOSE-\* → Phase 137 (Close
— Honesty Ledger, Claim Gate, gh#12 Follow-up). Phase 133/134 is a deliberate split of the research
spine's single combined "leg" phase (see ROADMAP.md §v1.30 for rationale).

---

*Requirements defined: 2026-08-03 after four-stream research (`.planning/research/SUMMARY.md`,
R-1…R-9 + A-1…A-4) and four operator decisions.*

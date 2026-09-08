---
phase: 179-uv-slot-writes-flag-skip-blank-check-hardware-gated
verified: 2026-09-08T09:15:00Z
status: passed
score: 4/4 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-01-PLAN.md", ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-01-SUMMARY.md", ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-02-PLAN.md", ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-02-SUMMARY.md", ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-03-PLAN.md", ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-03-SUMMARY.md", ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-04-PLAN.md", ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-04-SUMMARY.md", ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-DECISIONS.md", ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-MEASUREMENT.md", ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-REVIEW.md", ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/COVERAGE.md", "firestarter_app/firestarter/chip_test.py", "firestarter_app/tests/fake_chip.py", "firestarter_app/tests/fixtures/rekey_ledger.py", "firestarter_app/tests/fixtures/report_shapes.py", "firestarter_app/tests/fixtures/reports/m27c512-full-blank-check-bad.json", "firestarter_app/tests/fixtures/reports/uv-slot-write-pass.json", "firestarter_app/tests/fixtures/shape_ids.json", "firestarter_app/tests/test_blast_radius_invariance.py", "firestarter_app/tests/test_chip_test_cycle.py", "firestarter_app/tests/test_chip_test_uv_slot_write.py", "firestarter_app/tests/test_dev_test_cmd.py", "firestarter_app/tests/test_uv_mask.py"]
covered_digest: "v1:sha256:a82e695e7e737c07cff724c9851dbb08f2cee83f5e6506992ce873b9352a58f2"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 179: UV Slot Writes — `FLAG_SKIP_BLANK_CHECK` (hardware-gated) Verification Report

**Phase Goal:** A UV part holding data outside the target slot accepts a write to that slot and the
run reaches `overall_verdict == "PASS"` with `run_count == 2` — not merely "the write step went OK."
**Verified:** 2026-09-08T09:15:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth (ROADMAP success criterion) | Status | Evidence |
|---|---|---|---|
| 1 | A physical UV part holding data outside the target slot accepts a write to that slot without being refused | ✓ VERIFIED | `179-MEASUREMENT.md` §3–5: real ST M27C512, non-blank outside the top slot (16 bytes non-`0xFF` at `0x0000-0x000F`), `write-partial` step verdict `OK`, exit code 0. Independently confirmed by the committed host regression `test_uv_slot_write_on_a_non_blank_part_reaches_pass_with_run_count_two`, which also proves the refusal path exists and is bypassed only by the flag (`test_the_double_refuses_a_non_blank_write_without_the_flag` / `test_the_double_accepts_a_non_blank_write_with_the_flag`, both passing). |
| 2 | That same run's `overall_verdict` reads `PASS` and `run_count` reads 2 | ✓ VERIFIED | `179-MEASUREMENT.md` §5–6: `write-partial` and `verify` both `run_count == 2`; title `[dev test] m27c512 — PASS (dea6e2474d30)`. Host regression asserts the identical fold: `sub.overall_verdict(results) == "PASS"`, `write.run_count == 2`, `verify.run_count == 2`, plus an anti-vacuity leg (`test_the_blank_check_adjudication_is_what_lifts_the_run_to_pass`) that forces the blank-check verdict back to `BAD` on a deep copy and shows the fold flips to `FAIL` — proving the `PASS` is produced by the adjudication, not incidental. |
| 3 | The blank-check skip is derived from the monotonicity witness — not the `region_policy` string alone — proven by a test where the two signals disagree and the witness wins | ✓ VERIFIED | `_is_monotonic_masked_target` (`chip_test.py:3064-3088`) checks `target.masked and bool(target.current) and target.current_is_probe_read` — no reference to `region_policy`. Read the call site (`chip_test.py:3253-3255`): the flag is `FLAG_SKIP_BLANK_CHECK if _is_monotonic_masked_target(resolved_target) else 0`. Two committed disagreement legs, read and confirmed independently: `test_uv_slot_policy_without_the_witness_does_not_set_the_flag` (policy says `uv-slot`, witness absent via a hand-built unmasked target injected through `WriteContext.cycle_targets` → `write_flags_seen == [0]`) and `test_fixed_policy_with_the_witness_sets_the_flag` (policy says `fixed`, witness present → `write_flags_seen == [8]`). Both assert zero `read_eprom` calls, proving the injection bypasses the resolver rather than merely re-deriving the same answer. |
| 4 | The regression test proving criteria 1 and 2 is committed to the suite and passes against real UV hardware, closing the "no such test exists" gap | ✓ VERIFIED (split evidence, D-179-1) | See "Criterion 4 — the split judgment" below. |

**Score:** 4/4 truths verified.

### Criterion 4 — the split judgment

`179-DECISIONS.md` (D-179-1) explicitly split criterion 4 across two artifacts and recorded that
"neither alone is criterion 4 — the operator accepted that stated cost." I evaluated both halves
independently rather than trusting the SUMMARY narrative:

- **Host half** (`179-03`): `tests/test_chip_test_uv_slot_write.py` — 12 named tests, all collected
  (`pytest --collect-only` confirms 12/12, zero skip markers anywhere in the file), all pass
  (`pytest tests/test_chip_test_uv_slot_write.py -o addopts="" -q` → `12 passed`). It proves criteria
  1–3 against a firmware-faithful double (`WriteInitPreflightChip`, which genuinely refuses a
  non-blank write without the flag and genuinely accepts it with the flag — confirmed by direct
  reading of `fake_chip.py:263-296`), not a double that rubber-stamps everything.
- **Hardware half** (`179-04`): `179-MEASUREMENT.md` — a real ST M27C512 UV EPROM, a real command
  (`firestarter -p /dev/ttyACM0 dev test m27c512`), a real port-identity check, real pre-run
  non-blank evidence, and the real step table/title/exit-code, all consistent with what the host
  regression predicts.

**My judgment:** the two together substantively satisfy the *intent* of criterion 4 — the logic is
proven exhaustively and non-vacuously in an automated, CI-collected test, and the same behavior is
independently confirmed to hold against a real part via the actual product CLI. But read literally,
criterion 4 says "the regression test … passes against real UV hardware" — and that is not what
happened: the pytest module never touches the serial port; it runs only against the double. The bench
run that touched real hardware was a manual CLI invocation, not an execution of the committed test
module. This is a genuinely weaker claim than the literal roadmap text, and it is weaker specifically
because a hardware-in-the-loop pytest test is infeasible for this project (bench hardware is
manual/operator-gated, UV writes are irreversible, there is no CI rig). Given this was an explicit,
dated, rationale-carrying operator decision made during planning (not a post-hoc rationalization at
verification time) and matches a stated prior-phase precedent (176-05), I am accepting it as
satisfying criterion 4 rather than failing the phase over a literal-text gap the operator already
adjudicated. Flagging it here so it is visible rather than silently absorbed into a clean "4/4."

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter_app/firestarter/chip_test.py` | `WriteTarget.current_is_probe_read`, `Step.uv_prewrite`, `_is_monotonic_masked_target`, positional flag at write call site, SKIPPED adjudication | ✓ VERIFIED | All five present and wired; read directly at `chip_test.py:2362,2411,3064-3088,3253-3268,2670-2682`. |
| `firestarter_app/tests/fake_chip.py::WriteInitPreflightChip` | Firmware-faithful refusal double | ✓ VERIFIED | Present, models the real (non-raising) `EpromOperator` contract and AND-physics via `FakeChip` lineage. One latent (non-blocking) defect — see WR-01 below. |
| `firestarter_app/tests/test_chip_test_uv_slot_write.py` | Committed, unskipped, 12-leg regression | ✓ VERIFIED | 12/12 collected, 12/12 pass, zero skip markers, zero debt markers (`TODO`/`FIXME`/`XXX`/`HACK`/`PLACEHOLDER` all absent). |
| `firestarter_app/tests/fixtures/reports/uv-slot-write-pass.json` + registration | Frozen `uv-slot-write-pass` shape, registered at all 8 gate-enforced sites | ✓ VERIFIED | Present; `snapshot_report_shapes.py --check` reports 19/19 matching (from `179-04-phase-seal.txt`); independently re-ran the phase's own module and mypy watermark check, both green. |
| `.planning/phases/179-.../179-MEASUREMENT.md` | Bench record with `BENCH RESULT:` sentinel | ✓ VERIFIED | Present, `BENCH RESULT: PASS`, carries measured hash/firmware/port/slot/exit-code evidence throughout — not templated language. |
| `.planning/REQUIREMENTS.md` | UV-01/02/03 marked per sentinel | ✓ VERIFIED (with caveat) | Marked `[x]` / Complete, matching the `PASS` sentinel branch. UV-02's prose still contains a mechanism claim this phase's own research falsified — see finding below; does not affect the checkbox's correctness. |
| `.planning/ROADMAP.md` | Phase 179's four plan checkboxes ticked | ✓ VERIFIED | Diff confirmed exactly 8 changed lines (4 `-`/4 `+`), all four checkboxes, nothing else touched. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `chip_test.py::_is_monotonic_masked_target` | `chip_test.py::_dispatch_multi_run` write-flag computation | direct call at line 3254 | ✓ WIRED | Confirmed by reading the call site; no `region_policy` reference anywhere in the predicate. |
| `WriteContext.cycle_targets` | `test_chip_test_uv_slot_write.py` disagreement legs | zero-probe injection seam | ✓ WIRED | Both disagreement legs set `write_context.cycle_targets` directly and assert zero `read_eprom` calls, proving the seam bypasses the resolver. |
| `submit.overall_verdict(results)` | `test_chip_test_uv_slot_write.py` | direct assertion, never `to_dict()` | ✓ WIRED | Confirmed — test asserts on `sub.overall_verdict(results)`, matching the plan's explicit prohibition on asserting a non-existent `to_dict()["overall_verdict"]` key. |
| `179-MEASUREMENT.md`'s `BENCH RESULT:` sentinel | `.planning/REQUIREMENTS.md` UV-01/02/03 | sentinel-branched seal | ✓ WIRED | `PASS` sentinel present; all three requirements ticked Complete, matching the documented branch rule. |
| `test_chip_test_uv_slot_write.py` | `179-MEASUREMENT.md` | D-179-1 Option A's two halves | ✓ WIRED (see caveat above) | Both artifacts exist and are mutually consistent; the literal "same test running against hardware" reading is not met — judged acceptable per the recorded decision. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| 12-leg regression module collects cleanly, no skip markers | `pytest tests/test_chip_test_uv_slot_write.py -o addopts="" --collect-only -q` | 12 tests collected | ✓ PASS |
| 12-leg regression module passes | `pytest tests/test_chip_test_uv_slot_write.py -o addopts="" -q` | `12 passed in 0.27s` | ✓ PASS |
| mypy watermark holds at 35 (CI Python 3.11) | `.venv311/bin/python tools/check_mypy_watermark.py` | `mypy errors: 35 (watermark: 35)` `OK` | ✓ PASS |
| Firmware already honors `FLAG_SKIP_BLANK_CHECK` (no firmware change needed) | read `firestarter/src/proms/eprom.cpp:143-145` | `if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) { mem_util_blank_check(handle); }` | ✓ PASS |
| Flag bit value agrees on both sides of the wire | grep `FLAG_SKIP_BLANK_CHECK` in both repos | `0x08` in both `constants.py` and `firestarter.h` | ✓ PASS |
| No debt/skip markers in phase-touched files | `/usr/bin/grep -n -E "TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER"` across 9 touched source/test files | no matches | ✓ PASS |
| Firmware submodule gitlink unchanged during phase 179 | `git log --oneline -- firestarter` around phase-179 commit range | no `firestarter` gitlink commit inside the phase's commit range | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| UV-01 | 179-01, 179-03, 179-04 | UV part accepts slot write | ✓ SATISFIED | Host regression + real bench PASS (`write-partial` `OK`). |
| UV-02 | 179-01, 179-02, 179-03, 179-04 | `overall_verdict == "PASS"`, `run_count == 2` | ✓ SATISFIED | Host regression asserts both directly; bench confirms identically. |
| UV-03 | 179-01, 179-03, 179-04 | Skip derived from witness, not `region_policy` | ✓ SATISFIED | Both disagreement-direction legs read and confirmed against source. |

No orphaned requirements — all three IDs mapped to this phase in `REQUIREMENTS.md` appear in at
least one plan's `requirements` field.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `.planning/REQUIREMENTS.md` | 77 | UV-02's prose still states the pre-179 falsified mechanism ("trips `hardware_refused` and aborts cycle 2") | ⚠️ Warning | Non-blocking to the phase's own success criteria (the checkbox and the behavior it certifies are both correct), but a reader of the canonical requirements traceability document inherits a mechanism claim this phase's own research (`PITFALLS.md:186-188`) proved never existed. The correction was applied to `PITFALLS.md` and `research/SUMMARY.md` but not propagated to `REQUIREMENTS.md` itself. Recommend a follow-up scoped edit to UV-02's prose (not a re-open of this phase). |
| `firestarter_app/firestarter/diagnostic_report.py` | 601-610 (message text), computed at `chip_test.py:3014` | `"256 of 256 slots left on this part"` reported by `179-MEASUREMENT.md` immediately after a run that consumed one slot | ℹ️ Info (new finding, not previously filed) | `slots_remaining=slots_total - slot_index` is computed at target-resolution time, before the write that consumes `slot_index`'s own slot executes — so the count includes the very slot this run is about to spend. This reproduces exactly as the bench artifact shows (256/256 reported right after spending slot 0). This is a distinct defect from the already-filed `T-179-05` ladder-flip todo (which is about `build_db_diff`'s ladder-fold logic, not this message's arithmetic) — checked the three pending UV-related todos and none cover this. Not a blocker for UV-01/02/03 (none of the three roadmap criteria concern this telemetry line), but it is a real off-by-one worth filing separately; recommend a small follow-up todo (`slots_remaining` should read `slots_total - slot_index - 1` post-write, or the message should be reworded to state it counts the slot about to be used). |
| `firestarter_app/tests/fake_chip.py` | 263 | `WriteInitPreflightChip.__init__` freezes `check_eprom_id` at construction (WR-01, from `179-REVIEW.md`) | ⚠️ Warning (pre-existing, already documented) | Latent — not exercised by any of this phase's 12 tests, does not affect any of the phase's own claims. Already caught and documented by the phase's own code review with a concrete fix; not re-litigated here beyond confirming it is real (`chip_test.py`/`fake_chip.py:263-296` read directly) and unfixed at time of verification. |

### Gaps Summary

No blocking gaps. All four ROADMAP success criteria are verified against the actual codebase, not
just the SUMMARY narrative — I independently ran the committed test module (12/12 pass, 0 skipped),
read the production code implementing the witness/flag/adjudication end-to-end, confirmed the
firmware side already honors the flag with matching bit value, confirmed the ROADMAP/REQUIREMENTS
edits are scoped exactly to this phase's own content, and confirmed the firmware submodule was never
touched. Two non-blocking findings are surfaced above (REQUIREMENTS.md's stale UV-02 mechanism text,
and a newly-identified `slots_remaining` off-by-one) — neither was previously filed as a todo, and
neither is a must-have for this phase's own success criteria, but both are worth a human decision on
whether to file follow-up work.

---

_Verified: 2026-09-08T09:15:00Z_
_Verifier: Claude (gsd-verifier)_

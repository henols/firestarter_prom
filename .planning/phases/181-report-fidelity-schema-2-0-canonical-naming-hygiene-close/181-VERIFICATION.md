---
phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
verified: 2026-09-09T00:00:00Z
status: gaps_found
score: 18/19 must-haves verified
behavior_unverified: 0
overrides_applied: 0
covered_files:
  - .planning/MILESTONES.md
  - .planning/REQUIREMENTS.md
  - .planning/ROADMAP.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-01-PLAN.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-01-SUMMARY.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-02-PLAN.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-02-SUMMARY.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-03-PLAN.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-03-SUMMARY.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-04-PLAN.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-04-SUMMARY.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-05-PLAN.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-05-SUMMARY.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-06-PLAN.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-06-SUMMARY.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-07-PLAN.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-07-SUMMARY.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-08-PLAN.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-08-SUMMARY.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-09-PLAN.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-09-SUMMARY.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-10-PLAN.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-10-SUMMARY.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-CLOSURE.md
  - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-CONTEXT.md
covered_digest: "v1:sha256:ab4ceec4ed49e139c165e9cfecb38d0975481bcc2ad8429fea0f15788c39da92"
gaps:
  - truth: "The phase's app-repo work is committed and reachable from the meta repo's own tracked submodule pointer, consistent with every prior phase's closing practice in this milestone"
    status: failed
    reason: >
      The meta repo's committed `firestarter_app` gitlink is still `04fd982` (the phase's own BASE
      commit) at the current HEAD (`1fdbf3e1`/`9fbc0eb6`) — it has never been advanced through any of
      phase 181's 10 plans or its close plan, despite 38 real commits (all 18 requirements' worth of
      work) landing in the submodule up to `6de7273`. `git status --porcelain` in the meta repo shows
      `M firestarter_app` uncommitted right now. This breaks the pattern every earlier phase in this
      milestone followed without exception: 179-01/179-02/179-03, 180-01, 180-03, 180-04, and 180-05
      each carried an explicit "advance firestarter_app gitlink" commit, and phase 180's own close
      commit (`2b93c20a`) is the one that set the pointer to `04fd982` in the first place. Nothing in
      181's plans changes that convention.
    artifacts:
      - path: "firestarter_app (gitlink)"
        issue: "Meta-tracked submodule pointer frozen at 04fd982 (phase base) through all of phase 181; working tree dirty at 6de7273 but never committed"
    missing:
      - "A meta-repo commit that advances the firestarter_app gitlink to (at least) 6de7273, matching every prior phase's per-plan or close-time convention"
      - "A correction to 181-10-SUMMARY.md's false claim (line ~56, ~202) that CLAUDE.md contains an explicit 'leave the M firestarter_app gitlink line alone' convention deferring gitlink bumps to milestone close — no such text exists anywhere in /workspaces/CLAUDE.md (grep confirms zero matches for 'gitlink' or 'M firestarter_app'), and this exact false-claim pattern ('gitlink bumps are deferred to milestone close') was already identified and corrected out-of-band once before, in a different phase (125-06-SUMMARY.md, per STATE.md's own recorded finding, commit 4bb038e)"
---

# Phase 181: Report Fidelity — Schema 2.0, Canonical Naming & Hygiene Close Verification Report

**Phase Goal:** The report's remaining fields are made to describe exactly what the run knows —
nothing assumed, nothing dead — the schema bump is honest about the breaking change, chips are named
the way the database names them, and the milestone's dependency and re-key discipline is closed out in
one place.

**Verified:** 2026-09-09
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

Everything the phase's 18 requirements actually claim about the report, the schema, the naming, and
the dependency/re-key discipline was independently re-derived against the live codebase (not read off
any SUMMARY) and is **substantively correct** — every code-level truth below is VERIFIED. The one
failure is structural, not functional: the meta repo's own committed record of this phase's work is
incomplete (see Gap 1), and the SUMMARY that explains away that gap cites a project convention that
does not exist.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | RPT-A1: `chip_id_actual` populates on a PASSING id check, not only on mismatch; no companion provenance key; honesty ceiling (echo, not read-back) stated in the docstring | ✓ VERIFIED | `cli_handlers.py:2211-2244` (`_chip_id_fields` docstring states the echo explicitly); `eprom_operations.py:2293-2328` (`check_eprom_id` returns `cmd_data.get("chip-id")` — the host's own expected id — on a pass, and a firmware-parsed value only on failure), confirming the docstring's claim is literally true, not merely asserted |
| 2 | RPT-A2: `steps[].fingerprint` gains `fingerprint_total`/`fingerprint_bad`/`fingerprint_bad_pct`/`fingerprint_evidence` as additive flat siblings; `fingerprint` classification key unchanged | ✓ VERIFIED | `diagnostic_report.py:912-922`; `test_blast_radius_invariance.py` 106/106 pass including `_STEPS_ELEMENT_0_KEYS` |
| 3 | RPT-A3: `steps[].divergence` exported; `None` only when no comparison was possible; agreeing reads carry `bad: 0` with the same 5-key shape as diverging reads; reason keyed on disagreement | ✓ VERIFIED | `chip_test.py:2814-2843` (both branches literally show the same 5 keys, `bad: 0` on agreement, `reason = "read runs diverged" if diverged else ""`) |
| 4 | RPT-A4: `plan.is_uv` reaches `to_dict()` as top-level `is_uv`, read off `self.plan.is_uv` | ✓ VERIFIED | `diagnostic_report.py:1007` |
| 5 | RPT-A5: detected chip ID is a structured `StepResult.chip_id_detected` field, not a prose scrape | ✓ VERIFIED | `chip_test.py:1090,2778`; `cli_handlers.py:2238` reads it structurally |
| 6 | RPT-B1: `voltage.vpp_mv`/`vpe_mv` deleted from dataclass/`_voltage_dict()`/schema, proven by an attribute-scoped AST census (not textual) | ✓ VERIFIED | `diagnostic_report.py:783-800` (4-key `_voltage_dict`); `test_voltage_field_census.py` 4/4 pass — census is `ast.Attribute` assignment-target scoped, textual false-positive count separately measured and asserted larger than the census's own zero |
| 7 | RPT-B2: `banner.locked_steps` deleted; `Plan.locked_destructive` removed (adjudicated per D-7) | ✓ VERIFIED | `grep locked_steps\|locked_destructive` returns zero hits in `chip_test.py`/`diagnostic_report.py`; `_BANNER_KEYS` shrunk to 2 entries |
| 8 | RPT-D1: `duration_s` is the mean over cycles that produced a duration (not the sum); denominator is `len(durations)`, never `run_count` when they could differ; `None` when nothing ran | ✓ VERIFIED | `chip_test.py:1328-1389` (`_aggregate_cycle_results`) |
| 9 | RPT-D2: stored, once-stamped `elapsed` from CLI entry to first serialization; render-only summed row replaced | ✓ VERIFIED | `cli_handlers.py:2479-2482` (stamped immediately before `report.render(console)`); `diagnostic_report.py:996` |
| 10 | RPT-E1: `SCHEMA_VERSION` reads `2.0` | ✓ VERIFIED | `diagnostic_report.py:51` |
| 11 | RPT-E2: frozen schema-1.2/1.4 `devtest-triage` fixtures still parse forward-only; fixture files unmodified | ✓ VERIFIED | `test_frozen_pre_2_0_fixtures_still_parse_forward_only` (re-run post-deletion in 181-09); `git log` on both fixture files shows no commit since `8b18ce74` (Phase 147) |
| 12 | RPT-E3: `dedup_fingerprint` byte-identical for every pre-existing shape; exception clause discharges EMPTY (zero re-keys this phase) | ✓ VERIFIED | 19/19 `FROZEN_HASHES` literals byte-identical to app base `04fd982` (independently diffed, zero moved lines); `LADDER_PINS`' five `m27c512-*` CANDIDATE→NO_CHANGE moves are `build_db_diff` disposition pins, a separate mechanism from `dedup_fingerprint`/`FROZEN_HASHES` — confirmed by reading both structures directly, they do not overlap |
| 13 | RPT-F1: `auto_capture.canonical_part_number` mirrors `get_eprom_config`'s own matching ladder; `ac.chip` keeps the raw token | ✓ VERIFIED | `cli_handlers.py:2247-2295` (`_canonical_part_number`); `test_canonical_part_number.py` 5/5 pass |
| 14 | RPT-F2: `.claude/skills/devtest-triage/SKILL.md` updated, naming the 4 surviving rail fields, rail-not-socket statement, pre-2.0 note | ✓ VERIFIED | `SKILL.md:330-341`; meta commit `d2116df` (skill-first, before app commit `c994849`, per the evidence transcript's stated ordering rationale) |
| 15 | HYG-01: `syrupy` bounded `>=5.0,<7` | ✓ VERIFIED | `pyproject.toml:73` |
| 16 | HYG-02: runtime deps stay exactly the 6 shipped names, pinned by test | ✓ VERIFIED | `pyproject.toml:46-53`; `test_runtime_dependencies.py` 4/4 pass |
| 17 | HYG-03: decision recorded that `dedup_fingerprint` must never hash `to_dict()`/reflect over dataclass fields, enforced by an AST pin | ✓ VERIFIED | `MILESTONES.md` (naming the mechanism, the consumer, and the gate); `test_dedup_fingerprint_hashes_an_explicit_allow_list_and_never_the_serialized_mapping` + its planted-mutant leg, both present and passing |
| 18 | HYG-04: every new `dev_test` helper (`_canonical_part_number`, `_chip_id_fields`) registered in `check_devtest_orchestrator.py`'s allow-list; `_resolve_write_scope` removed from it along with the source | ✓ VERIFIED | `check_devtest_orchestrator.py:152-165` |
| 19 | The milestone's dependency/re-key discipline is "closed out in one place" — including the meta repo's own tracked record of the app-side work that discipline governs | ✗ FAILED | See Gap 1. Meta gitlink frozen at phase-base `04fd982`; SUMMARY's justification cites a non-existent CLAUDE.md rule |

**Score:** 18/19 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/diagnostic_report.py` | `is_uv`, `SCHEMA_VERSION=2.0`, fingerprint siblings, `divergence`, `chip_id_detected` export, `elapsed`, 4-key `_voltage_dict`, `canonical_part_number` export | ✓ VERIFIED | All keys present, all wired through `to_dict()` |
| `firestarter_app/firestarter/chip_test.py` | narrowed `write_scope`, mean `duration_s`, agreeing-read `divergence`, `chip_id_detected` recording, write-refusal predicate | ✓ VERIFIED | Confirmed line-by-line |
| `firestarter_app/firestarter/cli_handlers.py` | `_chip_id_fields`, `_canonical_part_number`, inlined scope rule, `elapsed` stamp | ✓ VERIFIED | Confirmed |
| `firestarter_app/firestarter/submit.py` | canonical issue title/body line, `elapsed` line | ✓ VERIFIED | `submit.py:189,294-295` |
| `firestarter_app/tests/fixtures/report_shapes.py` | 19 byte-identical `FROZEN_HASHES` literals | ✓ VERIFIED | Independently diffed against app base `04fd982`, zero moved |
| `firestarter_app/tests/test_voltage_field_census.py` | attribute-scoped AST census | ✓ VERIFIED | 4/4 tests pass, confirmed non-textual by direct read |
| `firestarter_app/tests/test_blast_radius_invariance.py` | HYG-03 AST pin, D-14 key-list pins, LADDER_PINS ladder census | ✓ VERIFIED | 106/106 tests pass |
| `.planning/MILESTONES.md` | HYG-03 decision record | ✓ VERIFIED | Present, names mechanism + gate |
| `.planning/REQUIREMENTS.md` | 18 checkboxes + 18 traceability rows flipped, nothing else | ✓ VERIFIED | Diffed against pre-181 commit `2facbc8f`: exactly 36 changed lines, all 18 IDs, no other row touched |
| `.planning/phases/.../181-CLOSURE.md` | leads with zero-re-key verdict | ✓ VERIFIED | Opens with the claim in its first paragraph |
| `firestarter_app` gitlink (meta repo) | advanced to reflect the phase's committed work | ✗ MISSING | Still `04fd982` (phase base); dirty, uncommitted at `6de7273` |

### Key Link Verification

| From | To | Via | Status |
|------|-----|-----|--------|
| `diagnostic_report.py::to_dict` | `chip_test.py::Plan.is_uv` | `self.plan.is_uv` attribute read | ✓ WIRED |
| `diagnostic_report.py::_step_dict` | `chip_test.py::Fingerprint`/`StepResult.divergence` | direct field reads, no recomputation | ✓ WIRED |
| `cli_handlers.py::_chip_id_fields` | `chip_test.py::StepResult.chip_id_detected` | structural field read | ✓ WIRED |
| `cli_handlers.py::_canonical_part_number` | `submit.py`/`diagnostic_report.py` canonical surfaces | all four surfaces read the exported `to_dict()` value, not a second selector call | ✓ WIRED |
| `test_blast_radius_invariance.py::LADDER_PINS` | `diagnostic_report.py::build_db_diff` | 19-shape disposition census | ✓ WIRED |
| meta `.planning/REQUIREMENTS.md`/`MILESTONES.md` | `firestarter_app` submodule work | gitlink pointer | ✗ NOT_WIRED — pointer frozen at pre-phase commit |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Voltage census proves deletion, not textual | `pytest tests/test_voltage_field_census.py -v` | 4 passed | ✓ PASS |
| Blast-radius / D-16 / HYG-03 / LADDER_PINS full module | `pytest tests/test_blast_radius_invariance.py` | 106 passed | ✓ PASS |
| Canonical naming, timing, deps, orchestrator gate | `pytest tests/test_canonical_part_number.py tests/test_chip_test_timing.py tests/test_runtime_dependencies.py tests/test_check_devtest_orchestrator.py` | 46 passed | ✓ PASS |
| Broad regression sample (report/plan/chip_test/submit/provenance/parse) | `pytest tests/test_diagnostic_report.py tests/test_dev_test_cmd.py tests/test_derive_plan_structural_sentinel.py tests/test_derive_plan_no_drop_sweep.py tests/test_erase_flag_invariants.py tests/test_chip_test_blank_check_order.py tests/test_chip_test_sdp_leg.py tests/test_chip_test_cycle.py tests/test_plan_shapes_drift.py tests/test_submit.py tests/test_provenance.py tests/test_parse_devtest_issue.py tests/test_chip_test.py` | 623 passed | ✓ PASS |
| `ruff check firestarter/ tests/` | independently re-run | All checks passed | ✓ PASS |
| mypy watermark | independently re-run | 35/35 (at watermark) | ✓ PASS |
| Snapshot-shapes check | independently re-run | 19/19 match | ✓ PASS |
| `dev test` orchestrator gate | independently re-run | PASS, 0 forbidden patterns | ✓ PASS |
| 19 `FROZEN_HASHES` literals vs. app base `04fd982` | `diff <(git show 04fd982:...) <(current)` | zero diff | ✓ PASS |
| Full suite (orchestrator-measured, corroborated by 623-test sample above) | 2285 passed, 0 failed | matches | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| RPT-A1 | 181-08 | ✓ SATISFIED | see Truth #1 |
| RPT-A2 | 181-07 | ✓ SATISFIED | see Truth #2 |
| RPT-A3 | 181-07 | ✓ SATISFIED | see Truth #3 |
| RPT-A4 | 181-01 | ✓ SATISFIED | see Truth #4 |
| RPT-A5 | 181-08 | ✓ SATISFIED | see Truth #5 |
| RPT-B1 | 181-09 | ✓ SATISFIED | see Truth #6 |
| RPT-B2 | 181-04 | ✓ SATISFIED | see Truth #7 |
| RPT-D1 | 181-06 | ✓ SATISFIED | see Truth #8 |
| RPT-D2 | 181-06 | ✓ SATISFIED | see Truth #9 |
| RPT-E1 | 181-01 | ✓ SATISFIED | see Truth #10 |
| RPT-E2 | 181-01/181-09 | ✓ SATISFIED | see Truth #11 |
| RPT-E3 | 181-01 | ✓ SATISFIED | see Truth #12 |
| RPT-F1 | 181-05 | ✓ SATISFIED | see Truth #13 |
| RPT-F2 | 181-09 | ✓ SATISFIED | see Truth #14 |
| HYG-01 | 181-03 | ✓ SATISFIED | see Truth #15 |
| HYG-02 | 181-03 | ✓ SATISFIED | see Truth #16 |
| HYG-03 | 181-10 | ✓ SATISFIED | see Truth #17 |
| HYG-04 | 181-04/181-05 | ✓ SATISFIED | see Truth #18 |

All 18 requirement IDs declared across the phase's 10 plans match REQUIREMENTS.md exactly; no orphans
found in either direction.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| — | — | No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` found in any product-source file touched by this phase | — | none |
| `181-10-SUMMARY.md` | ~56, ~202 | False citation: claims CLAUDE.md states an explicit "leave the `M firestarter_app` gitlink line alone" convention deferring gitlink bumps to milestone close. No such text exists in `/workspaces/CLAUDE.md` (grep confirms). This exact false-claim pattern was already caught and corrected once before, in a different phase's SUMMARY (125-06, per `STATE.md`'s own recorded finding) | 🛑 Blocker | Masks a real, unresolved gap (the gitlink was never advanced) behind a fabricated project-convention citation |

Three commits landed on the shared branch during this phase's execution window that are **not**
part of any 181-XX plan (`8b3d8f9`, `31f3455`, `b2546da`, all touching
`firestarter_app/firestarter/serial_comm.py` and a new `test_probe_spurious_setup_ack.py`). This is
correctly and consistently documented across 181-01/02/04's SUMMARYs as a concurrent, unrelated
`/gsd-debug` session sharing the working tree — not this phase's work, not a gap in it.

### Gaps Summary

Every functional, code-level claim this phase's 18 requirements make was independently re-derived
against the live `firestarter_app` submodule (not read off any SUMMARY) and holds. The report schema,
the deletions, the additive fields, the canonical naming, the dependency bounds, and the HYG-03
enforcement mechanism are all real, tested, and wired correctly — including the specific claims this
verification was asked to be skeptical of (RPT-B1's AST-not-textual census, RPT-E3's empty exception
clause distinguished from the unrelated `LADDER_PINS` ladder re-key, and RPT-A1's honesty-ceiling
statement, which is literally true of `check_eprom_id`'s implementation).

The one gap is structural rather than functional: the phase goal's closing clause — "the milestone's
dependency and re-key discipline is closed out **in one place**" — is not actually true of the meta
repo's own committed history. The `firestarter_app` gitlink has not moved past the phase's own base
commit (`04fd982`) despite 38 real commits landing in the submodule, breaking a convention every
earlier phase in this milestone (179, 180) followed without exception, including phase 180's own close
commit, which is the one that set today's stale pointer. The close plan's SUMMARY explains this away
by citing a CLAUDE.md convention that does not exist — and this specific false-claim pattern
("gitlink bumps are deferred to milestone close") was already flagged and corrected once before in a
different phase, per `STATE.md`'s own record. Fixing it is mechanical (one commit advancing the
gitlink to at least `6de7273`), but it must actually happen, and the SUMMARY's false citation should
be corrected rather than left standing as the record of why it didn't.

---

_Verified: 2026-09-09_
_Verifier: Claude (gsd-verifier)_

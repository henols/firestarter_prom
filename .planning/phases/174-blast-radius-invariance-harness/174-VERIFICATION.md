---
phase: 174-blast-radius-invariance-harness
verified: 2026-09-03T16:53:28Z
status: gaps_found
score: 4/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "A MILESTONES.md re-key ledger section exists with the fields a declared re-key must carry (change, before-hash, after-hash, date) — the mechanism every later phase's deliberate re-key is recorded into (roadmap SC5 / GATE-06)"
    status: failed
    reason: "The section and its seven-column table (ledger_id | shape_id | change | owner | before | after | declared) exist with the right fields, but the meta-side checker that binds it (tools/rekey/check_rekey_ledger.py, D-13) — the mechanism GATE-06's own coverage evidence and the checker's own docstring rely on to make this a machine check rather than a sentence — does not detect a corrupted or fabricated MILESTONES.md row. Independently reproduced both of code review's CR-02 legs by direct execution against the real ledger plus a mutated copy of the real MILESTONES.md: (a) inserting a fabricated, fully-declared row for RK-174-01-p177-readback-gating (bogus after_hash=ffffffffffff) immediately before the real, still-undeclared row for the same ledger_id — the checker exits 0, 'OK: 6 ledger row(s), 6 MILESTONES.md row(s) bound', the fabricated declared re-key is entirely invisible; (b) corrupting the surviving row's shape_id to TOTALLY-WRONG-SHAPE and before_hash to 000000000000 while leaving after as '(undeclared)' — the checker again exits 0. Root cause: parse_milestones_rows keys rows by ledger_id in a plain dict with no duplicate-row detection (last line wins, silently), and check()'s undeclared branch only ever inspects the after cell, never shape_id/before_hash. This directly falsifies the checker's own documented guarantee ('a row cannot be declared on one side and silently never appear on the other') and GATE-06's REQUIREMENTS.md text ('recorded ... as a declared, dated, ONE-TIME decision') — a duplicate or corrupted row is exactly the silent accident this phase's whole goal exists to make impossible, and the mechanism named to prevent it does not."
    artifacts:
      - path: tools/rekey/check_rekey_ledger.py
        issue: "parse_milestones_rows (~lines 94-107) has no duplicate-ledger_id detection — a second RK-174- row for an existing ledger_id silently overwrites the first in the rows dict. check()'s undeclared branch (~lines 133-139) validates only the after cell, never shape_id/before_hash, against the ledger row."
    missing:
      - "Detect duplicate ledger_id rows while parsing MILESTONES.md and fail closed (raise LedgerParseError / print an ERROR line, non-zero exit) instead of silently keeping only the last-seen row for that ledger_id."
      - "In check()'s undeclared branch, additionally assert the MILESTONES.md row's shape_id and before_hash equal the ledger row's shape_id/before_hash whenever a row exists at all (not only that the after cell reads as undeclared) — this closes WR-01 at the same time."
      - "Extend evidence/174-01-anti-vacuity-red-green.txt (or a new evidence file) with these two legs, both currently RED (exit 0 when a non-zero exit is required) and neither previously exercised by any of the phase's anti-vacuity transcripts."
---

# Phase 174: Blast-Radius Invariance Harness Verification Report

**Phase Goal:** A frozen, absolute-value oracle exists proving any later change to `dedup_fingerprint` or the promotion ladder is a declared decision, not a silent accident — built and green before any of this milestone's behaviour changes land.
**Verified:** 2026-09-03T16:53:28Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth (roadmap Success Criterion) | Status | Evidence |
|---|---|---|---|
| 1 | A frozen table pairing report shapes to expected 12-hex `dedup_fingerprint` values lives in `firestarter_app/tests/fixtures/` and covers at minimum the four measured re-key shapes (read-back gating, SDP-step pruning, canonical naming, UV `run_count` collapse), computed against HEAD before any subsequent phase's change lands | ✓ VERIFIED | `tests/fixtures/report_shapes.py` defines 16 `SHAPE_IDS`/`FROZEN_HASHES` entries including `sst27sf512-six-step` (read-back gating), `m27c512-full-all-ok` (SDP-step pruning), `m27c512-full-canonical-name` (canonical naming), `m27c512-full-blank-check-bad` (UV run_count collapse). Independently reproduced two of the sixteen literals against the real `dedup_fingerprint` (`6d3afbc52315`, `776846bf2dc8`) — matched exactly. `test_dedup_fingerprint_is_frozen` (16 parametrized cases) passes; full 110-test phase suite passes (`110 passed in 7.15s`, reproduced independently). |
| 2 | Every assertion in that table is against an absolute expected hash string; none is a relational `fp(a) == fp(b)` comparison computed at runtime | ✓ VERIFIED | Read `test_blast_radius_invariance.py` in full: every hash assertion compares a computed `dedup_fingerprint(...)` return value against a literal string in `FROZEN_HASHES`/`LADDER_PINS`, never against a second computed fingerprint. Anti-vacuity legs assert *inequality* against the same frozen literal after a planted mutation, which is the correct converse of the same absolute-comparison idiom. |
| 3 | `build_db_diff`'s disposition and ladder output for the same frozen shapes is pinned and asserted the same way, so a promotion-ladder change cannot land silently | ✓ VERIFIED | `LADDER_PINS` (16 entries) pins `(proposed_disposition, ladder_state)` per shape; `test_build_db_diff_ladder_pin_for_all_shapes` and `test_ladder_pins_cover_all_four_build_db_diff_arms` pass, confirming all four `build_db_diff` dispositions are reached (including the AT28C256 SDP blind spot and the non-SDP all-OK arm). |
| 4 | The raw-CLI-token → `part_number` delta across the shipped database is a committed, measured artifact — a table or file — not an assumed number | ✓ VERIFIED | `firestarter_app/tests/fixtures/part_number_delta.json` exists; independently loaded and confirmed its `aggregate` block (746 rows / 59 vendors / 677 distinct part numbers / 953 aliases / 942 token-differs / 11 token-matches / 514 comma-joined / 16 not-implemented / 0 not-found / 732 lowercase-proxy) matches the SUMMARY's claimed numbers exactly. `tools/measure_part_number_delta.py --check` re-run independently: `OK: ... matches a fresh regeneration`. |
| 5 | A `MILESTONES.md` re-key ledger section exists with the fields a declared re-key must carry (change, before-hash, after-hash, date) — the mechanism every later phase's deliberate re-key is recorded into | ✗ FAILED | Section and 7-column table exist with the right fields (confirmed by reading `.planning/MILESTONES.md`), but the binding mechanism (`tools/rekey/check_rekey_ledger.py`) that is supposed to make a declared/fabricated re-key impossible to hide does not do so — see Gaps below. Both of code review's CR-02 legs independently reproduced by direct execution: exit 0 on a fabricated declared row shadowed by the real row, and exit 0 on a corrupted `shape_id`/`before_hash` on the surviving undeclared row. |

**Score:** 4/5 truths verified (0 present, behavior-unverified)

### Confirmed Critical Defect Not Rising to a Gap: CR-01 (results-list aliasing)

Independently reproduced code review's CR-01 by direct execution:

```
same results list: True
before: 6d3afbc52315 True    # == FROZEN_HASHES['m27c512-full-all-ok']
after:  e9df6ca4627c False   # moved, without m27c512-full-all-ok itself ever being touched directly
```

`_build_m27c512_full_all_ok` (`functools.cache`d) and its two derivatives
`m27c512-full-canonical-name` / `m27c512-full-comma-joined-name`
(`_clone_with_chip_override`) alias the identical `results` list object. A mutation
performed through any one of the three `shape_id`s reaches all three.

**Assessed against the roadmap criteria, not just the code-review severity scale:** this
defect does **not** falsify criterion 1, 2 or 3 as written. Today, as committed, all
sixteen frozen hashes — including the three aliased shapes — recompute correctly and
independently (16/16, orchestrator-verified and spot-confirmed above), because nothing
in the current, committed test suite mutates any of the three aliased shapes'
`results` in place. `_build_sst27sf512_six_step` (the shape the module's own
mutation-based anti-vacuity legs target) is deliberately uncached for exactly this
reason and is unaffected. The failure mode this bug creates is **collateral false
RED**, not a silent false GREEN: a future test that mutates only ONE of the three
aliased shapes to prove an anti-vacuity leg would unexpectedly also redden the other
two, for a reason unrelated to the guarded behaviour. That is a real, confirmed defect
in the harness's internal correctness — and, per the review, a live hazard specifically
for Phase 181's `RK-174-03-p181-canonical-naming-avoided` row, which is exactly the kind
of "mutate one shape, prove the pin moves" leg this milestone's later phases are
expected to write — but it does not let a real behaviour change pass silently today,
so it is recorded here as a **carried-forward risk (WARNING)**, not a gap against this
phase's own stated success criteria. It must be fixed (per the review's suggested fix:
stop caching a real-path builder that is later cloned, or deep-copy `results`/`plan` in
`_clone_with_chip_override`) before Phase 181 writes that anti-vacuity leg — and ideally
before any later phase adds a second mutation-based leg touching any of the three
aliased shapes.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter_app/tests/fixtures/report_shapes.py` | 16 shape builders, `SHAPE_IDS`/`FROZEN_HASHES`/`RESERVED_SHAPE_IDS`/`LADDER_PINS` | ✓ VERIFIED | Present, imported and exercised by 4 test modules; `functools.cache`d aliasing hazard noted above (CR-01, WARNING, not a gap). |
| `firestarter_app/tests/fixtures/reports/*.json` (16 files) | Committed `to_dict()` snapshots | ✓ VERIFIED | 16 files present; `snapshot_report_shapes.py --check` independently re-run: `OK: 16 snapshot(s) ... match a fresh regeneration`. |
| `firestarter_app/tests/fixtures/shape_ids.json` | Committed sorted 16-entry `shape_id` anchor (D-10) | ✓ VERIFIED | Present; four-way closure tests pass. |
| `firestarter_app/tests/fixtures/rekey_ledger.py` | Append-only `LEDGER`, 6 rows | ✓ VERIFIED | Present; 6 rows, all `after_hash is None`, `ledger_id`s unique and ascending. |
| `firestarter_app/tests/fixtures/devtest_issue_corpus.json` | 26-row filed `[dev test]` issue corpus (GATE-05) | ✓ VERIFIED | Present; `build_devtest_issue_corpus.py --check` independently re-run: `OK: ... matches a fresh regeneration`. |
| `firestarter_app/tests/fixtures/part_number_delta.json` | Whole-database delta artifact (GATE-04) | ✓ VERIFIED | Present; aggregate numbers independently confirmed (see Truth 4). |
| `tools/rekey/check_rekey_ledger.py` | Meta-side cross-tree checker (D-13) | ⚠️ WIRED BUT DEFECTIVE | Present, wired into `.github/workflows/rekey-ledger-check.yml` and callable locally; exits correctly on the basic clean/missing-path/undeclared-row legs the phase's own evidence exercises, but fails to detect a duplicate or corrupted `MILESTONES.md` row (CR-02 — see Gaps). |
| `.planning/MILESTONES.md` (v1.36 Re-Key Ledger section) | 6 narrated rows, declared-re-key protocol, corrections table | ✓ VERIFIED (section content) | Present and narrated; the section's *binding mechanism* is the gap, not the section's own content. |
| `.github/workflows/rekey-ledger-check.yml` | Registered CI leg, `beta`/`gsd/**` triggers, gitlink-resolved checkout | ✓ VERIFIED | Present; triggers confirmed by reading the file (branches: `beta`, `gsd/**`; push+pull_request+workflow_dispatch); on-GitHub firing is explicitly declared unproven by the phase itself (see Human Verification). |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `report_shapes.py` | `firestarter/diagnostic_report.py` | `dedup_fingerprint` called on a real `DiagnosticReport` | ✓ WIRED | Confirmed by direct import and execution; no reimplementation of the hash found anywhere in the fixture module. |
| `report_shapes.py` | `firestarter/chip_test.py` | `derive_plan`/`run_plan` build the 8 real-path shapes | ✓ WIRED | Confirmed present (`_build_real_path_report`) and exercised (0.376s cold build per SUMMARY, corroborated by the 7.15s full-module run observed here). |
| `rekey_ledger.py` | `report_shapes.py` | every ledger row's `shape_id` resolves to a builder | ✓ WIRED | `test_rekey_ledger.py`'s row-shape/resolution sweep passes; all 6 rows' `shape_id`s are members of `SHAPE_IDS`. |
| `check_rekey_ledger.py` | `rekey_ledger.py` | `ast.literal_eval`, never import | ✓ WIRED | Confirmed by reading the checker: uses `ast.parse` + `ast.literal_eval` exclusively, no `import` of the fixture module. |
| `check_rekey_ledger.py` | `.planning/MILESTONES.md` | every `RK-174-` row bound both directions | ⚠️ WIRED BUT UNSOUND | Binds correctly against the real, well-formed file (`OK: 6 ledger row(s), 6 MILESTONES.md row(s) bound`, independently re-run), but the binding is not sound against a duplicated or corrupted row — see Gaps (GATE-06). |
| `.github/workflows/rekey-ledger-check.yml` | `check_rekey_ledger.py` | `run:` step invokes it with resolved paths | ✓ WIRED | Confirmed by reading the workflow file; the `python3 meta/tools/rekey/check_rekey_ledger.py --repo-root meta ...` invocation matches the script's actual CLI. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full phase test suite (110 tests) actually passes | `pytest tests/test_blast_radius_invariance.py tests/test_rekey_ledger.py tests/test_devtest_issue_corpus.py tests/test_part_number_delta_drift.py` | `110 passed in 7.15s` | ✓ PASS |
| Frozen hash reproduces from a real `DiagnosticReport` for two independently-chosen shapes | in-process `dedup_fingerprint(build_shape(...))` | `6d3afbc52315`, `776846bf2dc8` — both match `FROZEN_HASHES` | ✓ PASS |
| Snapshot, corpus and delta artifacts regenerate byte-identically | `snapshot_report_shapes.py --check`, `build_devtest_issue_corpus.py --check`, `measure_part_number_delta.py --check` | all three `OK: ... matches a fresh regeneration` | ✓ PASS |
| `check_rekey_ledger.py` binds the real pair | `python3 tools/rekey/check_rekey_ledger.py --repo-root /workspaces` | `OK: 6 ledger row(s), 6 MILESTONES.md row(s) bound`, rc=0 | ✓ PASS |
| CR-01 reproduction: mutation through one aliased shape corrupts another's frozen hash | in-process, described above | reproduced exactly as review reported | ✓ PASS (confirms defect; not a phase-blocking gap — see analysis above) |
| CR-02 reproduction, leg (a): fabricated declared row shadowed by real row | `check_rekey_ledger.py` against a mutated `MILESTONES.md` copy with a duplicate `RK-174-01-...` row inserted before the real one | `OK: 6 ledger row(s), 6 MILESTONES.md row(s) bound`, rc=0 (should be non-zero) | ✗ FAIL (confirms GATE-06 gap) |
| CR-02 reproduction, leg (b): corrupted `shape_id`/`before_hash` on the surviving undeclared row | `check_rekey_ledger.py` against a mutated `MILESTONES.md` copy | `OK: 6 ledger row(s), 6 MILESTONES.md row(s) bound`, rc=0 (should be non-zero) | ✗ FAIL (confirms GATE-06 gap) |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| GATE-01 | 174-01, 174-02, 174-03 | Frozen `(shape → 12-hex hash)` table exists, covers the four measured re-key shapes | ✓ SATISFIED | 16-shape `FROZEN_HASHES` table, 16/16 recompute byte-exactly. |
| GATE-02 | 174-01, 174-02, 174-03 | Suite fails on any frozen-shape hash change; assertion is absolute, never relational | ✓ SATISFIED | Confirmed by full read of `test_blast_radius_invariance.py`; anti-vacuity legs pass. |
| GATE-03 | 174-01, 174-02 | `build_db_diff` ladder output pinned for the same shapes | ✓ SATISFIED | `LADDER_PINS`, all 4 disposition arms measured and pinned. |
| GATE-04 | 174-04 | Raw-token → `part_number` delta measured and recorded, not assumed | ✓ SATISFIED | `part_number_delta.json`, aggregate independently confirmed. |
| GATE-05 | 174-01, 174-02, 174-03, 174-04 | Report corpus lives in `firestarter_app/tests/fixtures/` | ✓ SATISFIED | 16 shape snapshots + 26-row filed-issue corpus, both under `firestarter_app/tests/fixtures/`, both drift-tested. |
| GATE-06 | 174-01, 174-03, 174-05 | Every deliberate re-key recorded in `MILESTONES.md` as a declared, dated, one-time decision, bound to the app-side ledger | ✗ BLOCKED | Section/fields exist and the CI leg is registered, but the binding mechanism (`check_rekey_ledger.py`) does not reliably enforce "one-time" / non-duplicated / non-corrupted rows — see Gaps. |

No orphaned requirements found: `GATE-01` through `GATE-06` are the complete set REQUIREMENTS.md maps to Phase 174, and every one is claimed by at least one plan's `requirements:` frontmatter.

**Bookkeeping note (not a gap):** `.planning/REQUIREMENTS.md`'s checkboxes for GATE-01 through GATE-06 (lines 40-45) and its Traceability table (lines 148-153) both still read unchecked / "Pending" as of this verification, despite five of the six being satisfied in the codebase. This is a documentation-sync gap in REQUIREMENTS.md itself, not a phase-goal gap — flagged here so it is not lost, but not counted against the phase's score.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `firestarter_app/tests/fixtures/report_shapes.py` | 478-543 | Shared mutable `results` list across 3 `shape_id`s (CR-01) | ⚠️ Warning | Collateral false-RED risk for future mutation-based anti-vacuity legs (esp. Phase 181's `RK-174-03` row); does not currently defeat any frozen-hash assertion. |
| `tools/rekey/check_rekey_ledger.py` | 94-147 | No duplicate-row detection; undeclared branch skips `shape_id`/`before_hash` validation (CR-02) | 🛑 Blocker | Defeats GATE-06's core "cannot be declared on one side and silently never appear on the other" guarantee — see Gaps. |
| `firestarter_app/tools/snapshot_report_shapes.py` / `report_shapes.py` | 87-94 / 497-587 | `render_shape` mutates a cached real-path shape's `.db_diff` in place (WR-02) | ℹ️ Info | Does not currently threaten GATE-01/02 (`dedup_fingerprint` never reads `db_diff`); a process-order hazard for any future GATE-05-style pin on a real-path shape's `db_diff`. |
| `firestarter_app/tests/fixtures/report_shapes.py` | 340-354 | Stale docstring describing verification mechanics that don't match the actual test (IN-01) | ℹ️ Info | Cosmetic; no behavioural effect. |
| `firestarter_app/tools/measure_part_number_delta.py` | 101-132 | `differs` conflates "resolves differently" with "does not resolve at all" (IN-02) | ℹ️ Info | Currently masked (`aliases_chip_not_found: 0`); would misclassify a future unresolvable alias. |

No `TBD`/`FIXME`/`XXX` debt markers found in any of the 15 files this phase touched. All generator/checker scripts carry exactly one `#` line (the shebang); every fixture/test/JSON file carries zero.

### Human Verification Required

### 1. GitHub Actions actually schedules `rekey-ledger-check.yml`

**Test:** After this phase's commits reach a remote branch matching the workflow's triggers (`beta` or any `gsd/**` branch push, or a PR targeting `beta`), run `gh run list --workflow=rekey-ledger-check.yml --limit 5`.
**Expected:** At least one run appears, with a conclusion (success/failure) rather than no runs at all.
**Why human:** No network path exists in this sandbox to make GitHub Actions schedule a run; the phase's own evidence (`174-05-checker-fires.txt`) declares this explicitly unproven rather than claiming it observed. Local invocation and a simulated cross-tree checkout both pass, which is the strongest evidence obtainable without the operator's confirmation.

### Gaps Summary

Four of five roadmap success criteria hold up under direct, independent re-execution — the
sixteen-shape frozen-hash table, the absolute-assertion discipline, the `build_db_diff` ladder
pins, and the measured part-number delta artifact are all real, wired, and behaviorally
confirmed, not merely present. The fifth (the `MILESTONES.md` re-key ledger as "the mechanism
every later phase's deliberate re-key is recorded into") fails on the mechanism half of that
claim: `tools/rekey/check_rekey_ledger.py` — the component this phase's own plans, SUMMARYs and
the checker's own docstring all cite as the thing that makes GATE-06 "a machine check rather
than a sentence" — can be defeated by a duplicated or corrupted `MILESTONES.md` row and will
exit 0 regardless, independently reproduced twice. Given this milestone's explicit purpose is to
make later re-keys undeniable declared decisions rather than silent accidents, a binding
mechanism that itself accepts a silent, undeclared row is a direct hit on the phase's own goal,
not a peripheral nit — it is classified as a blocking gap rather than a carried-forward risk.

CR-01 (results-list aliasing across three frozen shapes) is a second, independently confirmed
Critical-severity defect from code review, but — assessed against what the roadmap actually
requires today — it does not currently falsify any of the five success criteria: it creates a
risk of unrelated collateral test failures in future anti-vacuity work, not a silent pass of a
real change today. It is recorded as a carried-forward risk (WARNING) that should be fixed
before Phase 181 exercises `RK-174-03-p181-canonical-naming-avoided`.

---

_Verified: 2026-09-03T16:53:28Z_
_Verifier: Claude (gsd-verifier)_

---
phase: 174-blast-radius-invariance-harness
reviewed: 2026-09-03T16:45:38Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - firestarter_app/tests/fixtures/report_shapes.py
  - firestarter_app/tests/fixtures/rekey_ledger.py
  - firestarter_app/tests/fixtures/planted_rekey_mutation.py
  - firestarter_app/tests/fixtures/shape_ids.json
  - firestarter_app/tests/test_blast_radius_invariance.py
  - firestarter_app/tests/test_rekey_ledger.py
  - firestarter_app/tests/test_devtest_issue_corpus.py
  - firestarter_app/tests/test_part_number_delta_drift.py
  - firestarter_app/tools/snapshot_report_shapes.py
  - firestarter_app/tools/build_devtest_issue_corpus.py
  - firestarter_app/tools/measure_part_number_delta.py
  - firestarter_app/tests/fixtures/devtest_issue_corpus.json
  - firestarter_app/tests/fixtures/part_number_delta.json
  - tools/rekey/check_rekey_ledger.py
  - .github/workflows/rekey-ledger-check.yml
findings:
  critical: 2
  warning: 2
  info: 2
  total: 6
status: issues_found
---

# Phase 174: Code Review Report

**Reviewed:** 2026-09-03T16:45:38Z
**Depth:** standard
**Files Reviewed:** 15
**Status:** issues_found

## Summary

All 110 tests in the four phase test modules pass, and both fail-closed/fail-open
paths documented in `useful_context` were independently re-verified (`snapshot_report_shapes.py
--check` clean, `check_rekey_ledger.py` exits 0 on the real pair and 1 on the shipped
planted-mismatch fixture). The frozen-hash idiom itself (comparing a computed
`dedup_fingerprint` against an absolute literal, never against a second computed value)
is applied correctly everywhere it matters, and the module's own anti-vacuity legs
(planted mutations on the tracer shape, key-list-pin mutation legs, D-10 closure legs)
are real and were confirmed to redden by direct experiment.

However, two concrete defects were found that let the harness lie in exactly the way
this review was asked to prioritize:

1. Three of the sixteen frozen shapes (`m27c512-full-all-ok`,
   `m27c512-full-canonical-name`, `m27c512-full-comma-joined-name`) share a single
   mutable `results` list by construction. A planted in-place mutation performed
   through any ONE of the three shape objects silently corrupts the frozen-hash
   assertion of the OTHER two — proven by direct reproduction below. This is exactly
   the "harness fails for a reason unrelated to the guarded behaviour" failure mode,
   and it is trivially reachable: it is the same "mutate a field, assert the hash
   moves" idiom this very module already uses on the tracer shape.
2. The meta-side checker `tools/rekey/check_rekey_ledger.py` parses `MILESTONES.md`'s
   `RK-174-` rows into a plain `dict` keyed by `ledger_id` with no duplicate
   detection. A second, bogus `RK-174-*` row reusing an existing `ledger_id` silently
   overwrites the legitimate one in that dict, and the checker exits 0 even though the
   file on disk contains a fabricated declared re-key or a corrupted `shape_id`/
   `before_hash` pairing — proven by direct reproduction below.

Both are reported as Critical per the severity calibration given ("the harness can
pass while the guarded behaviour has moved" / "the checker can exit 0 on a broken
ledger"). Two bounded-blast-radius Warnings and two Info items follow.

## Critical Issues

### CR-01: Three frozen shapes silently alias the same mutable `results` list — a mutation through one corrupts the frozen hash of the others

**File:** `firestarter_app/tests/fixtures/report_shapes.py:478-543`

**Issue:** `_build_m27c512_full_all_ok()` is `functools.cache`d (line 497-505), so
every call to `build_shape("m27c512-full-all-ok")` in a process returns the exact
same `DiagnosticReport` instance. `_build_m27c512_full_canonical_name()` and
`_build_m27c512_full_comma_joined_name()` (lines 526-543, both UNCACHED) each call
`_clone_with_chip_override(_build_m27c512_full_all_ok(), ...)`, which builds a new
`DiagnosticReport` wrapping a NEW `AutoCapture` but reuses `report.plan` and
`report.results` BY REFERENCE (line 486-494: `plan=report.plan, results=report.results`).
The result: `m27c512-full-all-ok`, `m27c512-full-canonical-name`, and
`m27c512-full-comma-joined-name` are three different `shape_id`s whose
`DiagnosticReport.results` is the identical list object.

The module's own safety argument (docstring lines 59-63) claims caching real-path
shapes is "safe here because nothing in this plan mutates a real-path shape's
`results` after construction" — but that argument does not survive contact with
`_clone_with_chip_override`'s aliasing: a mutation performed through ANY of the
three shape_ids' `.results` reaches all three, because it is the same list.

This is not hypothetical — it is precisely the "mutate an in-memory field, assert
the hash moves" anti-vacuity idiom this same module already applies to the tracer
shape (`test_planted_mutation_clearing_write_fingerprint_reddens_the_gate`,
line 561-572). `m27c512-full-canonical-name`'s row is the one Phase 181 explicitly
plans to declare NO re-key against (`RK-174-03-p181-canonical-naming-avoided`), the
kind of row a future anti-vacuity leg is likely to poke to prove the "avoided" pin
is non-vacuous — and doing so through that shape_id would silently break the
`m27c512-full-all-ok` frozen-hash assertion (GATE-01) for a reason that has nothing
to do with any real behaviour change.

**Reproduction (confirmed by direct execution):**
```
>>> base  = build_shape('m27c512-full-all-ok')
>>> clone = build_shape('m27c512-full-canonical-name')
>>> base.results is clone.results
True
>>> dedup_fingerprint(base)                     # before
'6d3afbc52315'   # == FROZEN_HASHES['m27c512-full-all-ok']
>>> clone.results[0].verdict = 'BAD'            # mutate via the OTHER shape_id
>>> dedup_fingerprint(base)                     # after
'e9df6ca4627c'   # no longer matches the frozen literal -- and nothing about
                 # m27c512-full-all-ok itself was ever touched directly
```

**Fix:** Give each real-path derivative its own independent `results` (and `plan`,
for symmetry) rather than aliasing the cached base's list, e.g.:
```python
import copy

def _clone_with_chip_override(
    report: DiagnosticReport, chip_override: str
) -> DiagnosticReport:
    auto_capture = _dataclass_replace(report.auto_capture, chip=chip_override)
    return DiagnosticReport(
        auto_capture=auto_capture,
        transport=report.transport,
        plan=report.plan,
        results=copy.deepcopy(report.results),
    )
```
or, more generally, stop caching the real-path builders that are used as a base for
a clone (drop `@functools.cache` from `_build_m27c512_full_all_ok`) so `build_shape`
never hands out the same instance twice at all — matching the tracer's own
uncached-because-it-can-be-mutated precedent.

### CR-02: `check_rekey_ledger.py` silently drops duplicate `RK-174-` rows in `MILESTONES.md`, letting a bogus declared re-key or a corrupted row exit 0

**File:** `tools/rekey/check_rekey_ledger.py:94-107` (`parse_milestones_rows`) and
`:110-147` (`check`)

**Issue:** `parse_milestones_rows` builds `rows: dict[str, tuple[str, str, str]]`
keyed by `ledger_id`, and for every matching table line does `rows[ledger_id] = (...)`
unconditionally — the last line in the file for a given `ledger_id` silently
overwrites any earlier one. `check()` then only ever sees the surviving (last) row
for that key. There is no detection of, or line-count check for, duplicate
`ledger_id` rows anywhere in the module.

Concretely, this defeats GATE-06's stated purpose ("every declared ... row must have
a matching MILESTONES.md row ... both directions, so a row cannot be declared on one
side and silently never appear on the other") whenever `MILESTONES.md` accidentally
(or maliciously) carries two rows for the same `ledger_id`:

- If a fabricated, fully-declared row for `RK-174-01-p177-readback-gating` (bogus
  `after` hash `ffffffffffff`) is inserted BEFORE the real, still-undeclared row for
  the same id, the real row shadows it in the dict and `check()` returns **zero
  errors** — even though the file on disk contains a completely fabricated declared
  re-key that the ledger (`after_hash=None`) never authorized.
- If the real row's `shape_id`/`before_hash` cells are corrupted (e.g. `shape_id`
  changed to a nonexistent name, `before_hash` changed to `000000000000`) while the
  `after` cell is left reading `(undeclared)`, `check()` again returns **zero
  errors**, because the undeclared branch (line 133-139) only ever inspects the
  `after` cell, never `shape_id`/`before_hash`, and there is nothing to detect a
  second row overwriting a first either way.

**Reproduction (both confirmed by direct execution against the real ledger + a
mutated copy of the real `MILESTONES.md`):**
```
# (a) bogus declared row shadowed by the following legitimate undeclared row
milestones_rows['RK-174-01-p177-readback-gating']
  == ('sst27sf512-six-step', '4dc282a5d596', '(undeclared)')   # the REAL row "wins"
check(ledger_rows, milestones_rows) == []                      # 0 errors -- the
  # bogus row with after=ffffffffffff, before=4dc282a5d596 that appeared EARLIER
  # in the file is invisible

# (b) corrupted shape_id/before_hash on the surviving undeclared row
milestones_rows['RK-174-01-p177-readback-gating']
  == ('totally-wrong-shape-id', '000000000000', '(undeclared)')
check(ledger_rows, milestones_rows) == []                      # 0 errors
```

**Fix:** Detect duplicate `ledger_id` rows and fail closed, and validate
`shape_id`/`before_hash` for undeclared rows too, e.g.:
```python
def parse_milestones_rows(path: Path) -> dict[str, tuple[str, str, str]]:
    if not path.is_file():
        raise LedgerParseError(f"milestones file not found: {path}")
    rows: dict[str, tuple[str, str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _ROW_RE.match(line.strip())
        if m:
            ledger_id, shape_id, _change, _owner, before, after, _declared = m.groups()
            if ledger_id in rows:
                raise LedgerParseError(
                    f"duplicate MILESTONES.md row for ledger_id {ledger_id!r}"
                )
            rows[ledger_id] = (shape_id, before, after)
    return rows
```
and, in `check()`'s undeclared branch, also compare `m_row[0]`/`m_row[1]` against
`shape_id`/`before_hash` (not only the `after` cell) whenever a row exists at all.

## Warnings

### WR-01: Undeclared-row check in `check_rekey_ledger.py` never validates `shape_id`/`before_hash`

**File:** `tools/rekey/check_rekey_ledger.py:133-139`

**Issue:** In the `after_hash is None` branch, the only check performed is
`_HASH_RE.match(m_row[2])` against the `after` cell. `m_row[0]` (`shape_id`) and
`m_row[1]` (`before_hash`) are never compared against the ledger row's own
`shape_id`/`before_hash`. This is documented as intentional in the module docstring
("if one exists for that `ledger_id` its `after` cell must still read as undeclared,
never a filled-in hash"), but it means a `MILESTONES.md` row can misname the
`shape_id` or carry a wrong `before_hash` for an undeclared ledger row and the
checker will never notice (see CR-02's reproduction (b), which is really two bugs in
one: the duplicate-shadowing defect, and this narrower validation gap that would
still exist even without any duplicate row involved — a single corrupted undeclared
row, with no duplicate at all, also produces 0 errors).

**Fix:** For a row with `after_hash is None`, additionally assert
`m_row[0] == shape_id and m_row[1] == before_hash` whenever `m_row is not None`,
emitting an `ERROR:` line naming the mismatch.

### WR-02: `functools.cache`d real-path shapes are mutated in place by `db_diff` attribute assignment, contradicting the module's own stated safety invariant

**File:** `firestarter_app/tools/snapshot_report_shapes.py:87-94`,
`firestarter_app/tests/fixtures/report_shapes.py:497-587`

**Issue:** `render_shape()` does `report = build_shape(shape_id); report.db_diff =
build_db_diff(...)`. For the eight `functools.cache`-decorated real-path builders
(`m27c512-full-all-ok`, `m27c512-full-blank-check-bad`, `m27c512-full-runs-1`,
`at28c256-full-all-ok-sdp`, `sst27sf512-full-all-ok`, `w27e257-full-all-ok`, plus the
two derivatives via CR-01), `build_shape(shape_id)` returns the same cached instance
every call within a process (confirmed: `build_shape('m27c512-full-all-ok') is
build_shape('m27c512-full-all-ok')` is `True`, and setting `.db_diff` on one call's
return value is visible on the next call's return value). `report_shapes.py`'s
module docstring claims caching is "safe here because nothing in this plan mutates a
real-path shape's `results` after construction" — true for `results`, but silent on
`db_diff` (and any other attribute), and `render_shape` already violates the spirit
of that claim today.

`dedup_fingerprint` itself does not read `db_diff`, so this does not currently
threaten GATE-01/02 the way CR-01 does. It does threaten GATE-05 (byte-identical
snapshots) and any future D-07-style key-list pin extended to a real-path shape:
whichever test or tool runs first in a given process determines whether a
subsequent `build_shape()` caller sees a bare (`db_diff=None`) or already-populated
report, which is exactly the kind of process-order dependence a frozen-snapshot
harness should not have.

**Fix:** Either drop `@functools.cache` from the real-path builders (matching the
tracer's uncached precedent) or have `render_shape`/any other composer operate on a
shallow copy (`dataclasses.replace(report, db_diff=...)`) rather than mutating the
shared instance in place.

## Info

### IN-01: Stale docstring claim about how the D-08 blind-spot shape is verified

**File:** `firestarter_app/tests/fixtures/report_shapes.py:340-354`

**Issue:** `_build_synthetic_arm4_empty_results`'s docstring states "the acceptance
check below calls `build_db_diff` with the chip name `m27c512`... while keeping
these synthetic (empty) results." The actual test that exercises this shape
(`test_build_db_diff_ladder_pin_for_all_shapes` in `test_blast_radius_invariance.py:318-357`)
calls `build_db_diff(report.auto_capture.chip, db, report.results)` with
`report.auto_capture.chip` unmodified, i.e. `"M8720"`, not `"m27c512"`. This happens
to be harmless — `build_db_diff`'s `proposed_disposition`/`ladder_state` outputs
depend only on `results`, never on the chip-name argument — but the docstring
describes verification mechanics that do not match the code as written, which could
mislead a future maintainer investigating this shape.

**Fix:** Update the docstring to describe what the test actually does (uses
`report.auto_capture.chip` = `"M8720"` directly), or remove the specific claim if it
was describing ad hoc manual verification from the research session rather than the
committed test.

### IN-02: `measure_part_number_delta.py`'s `differs` field conflates "resolves to a different part number" with "does not resolve at all"

**File:** `firestarter_app/tools/measure_part_number_delta.py:101-132`

**Issue:** `differs = token != resolved` (and the analogous `filed_issue_rows` computation
at line 146) is computed the same way whether `resolved` is a genuinely different
`part_number` string or `None` (alias resolves to no chip at all). Both cases set
`differs = True`, so `aliases_token_differs_from_part_number` silently folds in any
future `aliases_chip_not_found` aliases as "differs" rather than surfacing them
distinctly. Currently masked because the committed artifact measures
`aliases_chip_not_found: 0`, so no row is affected today, but a future database
change introducing an unresolvable alias would inflate the "differs" count rather
than being visible as a resolution failure in that specific field.

**Fix:** Exclude `resolve_status != "ok"` rows from the differs/match counters, or
add a distinct `resolves_to_nothing` bucket, so `aliases_token_differs_from_part_number`
stays a measurement of genuine spelling drift only.

---

_Reviewed: 2026-09-03T16:45:38Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

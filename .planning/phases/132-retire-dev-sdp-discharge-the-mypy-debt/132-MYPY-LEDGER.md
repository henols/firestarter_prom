# Phase 132 — mypy Ledger

This is the single file this phase appends its three mypy readings to: this plan's pre-change
reading (section 1, below), plan 132-06's post-fix reading, and plan 132-09's certifying CI
reading. Each reading is read from a run's output, never computed from the others.

## 1. Pre-change reading (this plan, 132-01)

Measured today, 2026-08-03, from `tools/ci_replica_venv.sh`'s leg 4 (this plan's Task 2), run
against `firestarter_app` @ `8caf77f458ba1bd1eeff47f9747838dc4183e2ca` on branch
`gsd/v1.30-sdp-surface-retirement`, inside the numpy-free `.venv/ci-replica` venv the script
builds. This is a fresh measurement taken in this session, not a value carried over from
`131-CI-BASELINE.md`.

**The gate's own stamp lines, verbatim:**

```
checked 121 source files
mypy errors: 69 (watermark: 35)
FAIL: 69 errors exceeds watermark 35. New errors introduced.
```

**mypy's own completion-summary line, verbatim:**

```
Found 69 errors in 17 files (checked 121 source files)
```

**Run stamps, verbatim:**

```
INTERPRETER: /home/vscode/.local/bin/python3.11 Python 3.11.15
MYPY-VERSION: mypy 2.3.0 (compiled: yes)
NUMPY-PRESENT: no
```

**App-repo HEAD and branch:** `8caf77f` (full: `8caf77f458ba1bd1eeff47f9747838dc4183e2ca`), branch
`gsd/v1.30-sdp-surface-retirement`.

**Per-file error distribution** (counted from the run's own detailed mypy output, 69 lines total):

| File | Count |
|---|---|
| `firestarter/eprom_operations.py` | 10 (ring-fenced — `FUT-MYPY-02`, not opened by this phase) |
| `tests/test_dev_test_cmd.py` | 9 |
| `tests/test_write_skip_sdp_unlock.py` | 7 |
| `tests/test_write_skip_erase_0x0d.py` | 6 |
| `tests/test_validate_family_cmd.py` | 6 |
| `tests/test_dev_sdp_cmd.py` | 6 |
| `firestarter/database.py` | 6 |
| `tests/test_serial_comm.py` | 3 |
| `tests/test_revision_constants_parity.py` | 3 |
| `firestarter/firmware.py` | 3 |
| `firestarter/config.py` | 3 |
| `firestarter/ic_layout.py` | 2 |
| `tests/test_provenance.py` | 1 |
| `tests/test_protocol_not_implemented_production_path.py` | 1 |
| `tests/test_eprom_database.py` | 1 |
| `tests/test_characterization.py` | 1 |
| `firestarter/submit.py` | 1 |
| **Sum** | **69** |

**Per-code error distribution** (counted from the same run):

| Code | Count |
|---|---|
| `[arg-type]` | 39 |
| `[union-attr]` | 10 |
| `[assignment]` | 7 |
| `[var-annotated]` | 6 |
| `[attr-defined]` | 4 |
| `[func-returns-value]` | 3 |
| **Sum** | **69** |

**`[var-annotated]` locations, verbatim from the run** (confirms `132-PATTERNS.md`'s
correction — `config.py:84/85/102` and `database.py:174/175/325`, none in `ic_layout.py`):

```
firestarter/config.py:84: error: Need type annotation for "_instances" ... [var-annotated]
firestarter/config.py:85: error: Need type annotation for "_initialized_configs" ... [var-annotated]
firestarter/config.py:102: error: Need type annotation for "_config" ... [var-annotated]
firestarter/database.py:174: error: Need type annotation for "proms" ... [var-annotated]
firestarter/database.py:175: error: Need type annotation for "pin_maps" ... [var-annotated]
firestarter/database.py:325: error: Need type annotation for "pin_signals" ... [var-annotated]
```

**The `[annotation-unchecked]` lines are mypy notes, not errors, and are excluded from the
count.** The same run's output additionally carries 28 lines of the form
`note: By default the bodies of untyped functions are not checked...` /
`[annotation-unchecked]` — these are mypy **notes**, counted separately from mypy's own `Found 69
errors` clause, and are deliberately excluded from every count in this ledger. A later reader who
independently counts every line containing the word "error" or every diagnostic-shaped line in
the raw log and arrives at a number near 97 (69 + 28) is counting notes as errors; this ledger's
69 is correct and matches mypy's own self-reported completion clause exactly.

## 2. Divergence check against Phase 131's inherited 69

This phase's measured count (69) **agrees exactly** with `131-CI-BASELINE.md`'s CI reading of 69
(read verbatim from CI run `30822281624`, `workflow_dispatch` on `beta` @ `16a313a`, mypy 2.3.0,
Python 3.11.15). There is nothing to reconcile: the fork-base count Phase 131 recorded as an
input to Phase 132's watermark is the same number this phase independently re-measures today, in
a different environment (a fresh numpy-free `.venv/ci-replica` venv on Python 3.11.15) against the
same commit family. Per Phase 131 D-12's rule, had these two numbers disagreed, the measured
number would win and both would be recorded without reconciliation — that rule is not invoked
here because no disagreement exists.

## 3. The checked-source-files floor

The measured `checked` value is **121**, against `MIN_CHECKED_SOURCE_FILES = 120`
(`tools/check_mypy_watermark.py:48`) — one file of margin. This phase's own two new files
(`firestarter/sdp_honesty.py`, added by plan 132-02, and `tests/test_sdp_honesty.py`, the `git mv`
target of plan 132-03) are additions with no corresponding net removal, so the checked count can
only rise from 121, never fall below the 120 floor as a side effect of this phase's own work.
**Conclusion: no floor edit is needed or permitted in this phase.** This discharges Phase 131
D-05's "a `git mv` holds the count at 120 — verify" as a verified fact, measured today, rather
than an inherited assumption.

## 4. Projected path to the watermark (a projection, not a claim)

The following arithmetic is a **projection**, not a claim of a measured post-fix count. It is
attributed by owning plan, each subtraction against the measured 69 above:

```
69                                            (this reading, section 1)
 - 6   (plan 132-03: the retargeted tests/test_sdp_honesty.py module needs
        no AppContext factory at all — its production SUT is the new pure
        firestarter/sdp_honesty.py helper, not an AppContext-constructing
        CLI handler)
 - 25  (plan 132-05: the four surviving typed-factory modules —
        tests/test_dev_test_cmd.py (9 in the file total, but the
        AppContext-factory-attributable subset per module boundary is
        counted per the four survivors' own factory-driven errors:
        6 + 6 + 6 + 7 = 25 — test_write_skip_erase_0x0d.py (6),
        test_validate_family_cmd.py (6), test_dev_test_cmd.py (6), and
        test_write_skip_sdp_unlock.py (7, not 6 — this module carries a
        seventh error at :72, `Argument 1 to "EpromOperator" has
        incompatible type "object"`, beyond its own make_app_context
        factory))
 - 6   (plan 132-06: the six [var-annotated] annotations at
        config.py:84,85,102 and database.py:174,175,325)
= 32
```

Watermark stays at 35 → **3 of headroom projected**, versus research's own prior projection of
33 (the measured seventh error in `test_write_skip_sdp_unlock.py` makes it 32, one lower than
research projected). **This is a projection, not a claim.** Plan 132-06 measures the real,
post-fix count in the numpy-free replica venv, and plan 132-09 reads CI's own certifying count —
neither later plan may treat this section's arithmetic as a substitute for its own measurement.

## 5. What this document does not establish

A locally-measured count, in a replica venv, is **not** a green CI job. `firestarter_app`'s
primary `ci` job is **RED at the start of this phase by design** — Phase 131 hardened the
watermark mechanism and fixed zero of the 69 errors it measures; this phase is the one that
attempts the fixes and the certifying dispatch. Nothing in this document is a claim that
anything is green, that the `dev sdp` deletion has landed, or that any mypy fix has been made —
this ledger's section 1 is a **pre-change** reading, taken before a single line of `dev sdp` or a
single mypy fix moves, exactly as this plan's objective requires.

**D-09's accepted cost, stated plainly.** The watermark stays at **35** and is **not ratcheted**
in this phase (see `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CONTEXT.md`
D-09). If the count lands at the projected 32 (section 4), there are **3 of silent headroom** in
what Phase 131 D-04 called the milestone's central honesty artifact — an accepted, stated cost.
The actual defence against new errors sneaking in under that headroom is plan 132-05's typed
`make_app_context` factory (D-10), not a tight watermark. The measured true count this phase
produces becomes a named input to a later phase's ratchet decision — the same "measure, don't
set" split Phase 131 used for its own inherited 69.

<!-- 132-06 appends here -->

<!-- 132-09 appends here -->

# Phase 177 Scope Decisions

Recorded by the operator (all four RECOMMENDED options taken) before plan `177-01` proceeds past
Task 1. Each decision names the option taken and a one-line reason. Downstream tasks in this plan
and in `177-02` / `177-03` implement the option recorded here.

## D-177-1

**Option A** — Close PRUNE-04 as measured-empty within the `dev test` engine (`chip_test.py`).
Reason: the exhaustive call-site inventory finds exactly two `operator.read_eprom` sites in
`chip_test.py` (`:2642`, `:2728`), both name-and-excluded (the fingerprint read-back by D-1, the
SDP leg because its read-back IS the verdict), so the in-engine population is measured zero;
`eprom_operations.write_cycle_eprom` is the only genuine read-to-compare site in the package but
is not the `dev test` engine and its read-back is the uno328pb read-repeatability oracle, not a
candidate for conversion — converting it would repeat the exact error D-1 corrected one layer
down.

## D-177-2

**Option A** — Add both `_synthesized_match_fingerprint` on the zero-I/O path AND a `bad == 0 ->
FP_MATCH` bucket inside `classify_fingerprint`. Reason: `ff_ratio` can never be `None` inside
`classify_fingerprint` (it is always a computed float), so the honest-`None` synthesized path
requires a separate constructor regardless; and `RK-174-05-p177-match-bucket-d4d6` names its
mechanism as "add a `match` bucket to the classifier" and its shape `at28c256-full-all-ok-sdp`
(an SDP-leg shape this phase's read-back gate does not touch) only moves if the classifier itself
gains the bucket. The bucket is placed AFTER the `ff_ratio >= _FF_RATIO_THRESHOLD` test and AFTER
the address-line test, before the `repeat_divergent is True` test — placing it above the
`ff_ratio` test would silently re-key the whole `blank/contact` population, which this phase
prohibits; `gh23-w27e257-fail` (the only frozen `blank/contact` shape) stays frozen at
`7a89fcea856a` as the pin proving the placement is correct.

## D-177-3

**Option A** — Keep both shape ids, re-point each. `sst27sf512-six-step`'s `write`/`verify`
`step_specs` move from `indeterminate` to `match` — this IS `RK-174-01`'s declared re-key.
`sst27sf512-six-step-readback-gated` re-points to the gate's OTHER branch: a step that FAILED and
therefore kept its real read-back, verdict `marginal` (never `BAD`, which would land on the
community-fail arm). Reason: this re-populates the INCONCLUSIVE arm of `LADDER_PINS` so
`test_ladder_pins_cover_all_four_build_db_diff_arms` still covers exactly four distinct
`(proposed_disposition, ladder_state)` pairs, and neither builder is deleted — the gated shape
stays as the evidence that the original R2 projection (fingerprint dropped on a pass) was
falsified by PRUNE-03.

## D-177-4

**Option A** — Publish the full old-to-new `dedup_fingerprint` mapping as a committed meta-repo
artifact and declare the MEASURED count in `MILESTONES.md`. Reason: GATE-06 requires the re-key
recorded with before/after hashes, and D-4/D-6 says the re-key is "stated publicly"; the 18-row
figure from RESEARCH.md is a projection, not a value to transcribe — plan `177-01` Task 3 measures
the actual re-key count from the committed 26-row corpus, and if it disagrees with 18 that
disagreement is itself a finding to record in `MILESTONES.md`'s corrections table (plan `177-02`
Task 3), not an error to reconcile away. Editing or closing no GitHub issue is in scope for this
milestone.

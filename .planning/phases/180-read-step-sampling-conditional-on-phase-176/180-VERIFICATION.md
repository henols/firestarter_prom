---
phase: 180-read-step-sampling-conditional-on-phase-176
verified: 2026-09-08T16:20:00Z
status: gaps_found
score: 23/24 must-haves verified
covered_files:
  - ".planning/REQUIREMENTS.md"
  - ".planning/ROADMAP.md"
  - ".planning/phases/180-read-step-sampling-conditional-on-phase-176/180-01-PLAN.md"
  - ".planning/phases/180-read-step-sampling-conditional-on-phase-176/180-01-SUMMARY.md"
  - ".planning/phases/180-read-step-sampling-conditional-on-phase-176/180-02-PLAN.md"
  - ".planning/phases/180-read-step-sampling-conditional-on-phase-176/180-02-SUMMARY.md"
  - ".planning/phases/180-read-step-sampling-conditional-on-phase-176/180-03-PLAN.md"
  - ".planning/phases/180-read-step-sampling-conditional-on-phase-176/180-03-SUMMARY.md"
  - ".planning/phases/180-read-step-sampling-conditional-on-phase-176/180-CONTEXT.md"
  - ".planning/phases/180-read-step-sampling-conditional-on-phase-176/180-PATTERNS.md"
  - ".planning/phases/180-read-step-sampling-conditional-on-phase-176/180-PRUNE-08-CLOSURE.md"
  - ".planning/phases/180-read-step-sampling-conditional-on-phase-176/180-RESEARCH.md"
  - ".planning/phases/180-read-step-sampling-conditional-on-phase-176/180-REVIEW.md"
  - ".planning/seeds/dev-test-adaptive-sequencing.md"
  - "firestarter_app/tests/test_chip_test.py"
  - "firestarter_app/tests/test_readback_inventory.py"
covered_digest: "v1:sha256:4bf392f066d4bc67fb89d330fcf92a46821482d1527fdcffc4ef928fc348267d"
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "A planner reading only `.planning/seeds/dev-test-adaptive-sequencing.md` can no longer regenerate the rejected sampling design (D-09, Ruling 2, plan 180-02 must_have)"
    status: partial
    reason: >
      R3's live-instruction sentence was correctly replaced with a "Measured and rejected" paragraph
      that cites the connect arithmetic and the closing document. But the two paragraphs immediately
      following it — "Escalate to the full second read only when the sample diverges, so exact
      divergence counts (`cmp_len`, `bad`, `pct`, `first_offset`) survive intact..." and "**Cost,
      stated:** ... the bit-structured stride is chosen to make that region small and
      address-line-aligned rather than arbitrary." — were deliberately left untouched (per the plan's
      own <action> text: "Leave R3's ... escalation paragraph and its stated-cost paragraph as they
      are"). Both are written in present tense as live design description (escalation policy, stride
      rationale), not marked as historical or superseded. Combined with the block structure the
      rejection paragraph itself still names ("one 256 B block at each device-size-scaled boundary,
      plus block 0 and the top block"), the full behavioural spec of the rejected sampler — structure,
      escalation trigger, and design rationale — remains readable end-to-end in the seed, immediately
      contradicting the "measured and rejected" verdict two paragraphs above it. This is the literal
      failure mode D-09 exists to prevent: "the destructive reading is not outvoted but absent" — here
      it is outvoted (by an inserted rejection paragraph) but not absent.
    artifacts:
      - path: ".planning/seeds/dev-test-adaptive-sequencing.md"
        issue: "R3's 'Escalate to...' and '**Cost, stated:**...' paragraphs (immediately below the 'Measured and rejected' paragraph) still describe the rejected sample's operational behaviour in present tense, with no historical framing or removal."
    missing:
      - "Rewrite or clearly re-frame the 'Escalate to...' and 'Cost, stated:' paragraphs as historical description of the rejected proposal (e.g., prefix with 'For the historical record, the rejected design would have...') or remove them, so nothing after the rejection verdict reads as a live instruction a planner could still execute against."
prohibitions_flagged:
  - prohibition: "The seed must not be left in a state from which the rejected sampling design can be regenerated"
    verification_tier: judgment (untyped in must_haves — no explicit test/judgment tag in PLAN frontmatter)
    disposition: unresolved — same root cause as the gap above; routed as a human-verification item per the judgment-tier soft-gate rule, not silently passed.
human_verification:
  - test: "Read `.planning/seeds/dev-test-adaptive-sequencing.md` R3 section top to bottom as a future planner would, and judge whether the retained 'Escalate to...' / 'Cost, stated:' paragraphs constitute a regenerable design spec or acceptable historical color below an explicit rejection banner."
    expected: "Either confirm the paragraphs are harmless historical color (and record an override), or direct that they be rewritten/removed per the gap above."
    why_human: "Whether prose 'reads as a closed door, not an annotated one' is the exact comprehension judgment plan 180-02's own SUMMARY.md flags as `human_judgment: true` for this must-have; it is not mechanically decidable by grep, and reasonable readers could disagree about severity."
  - test: "Confirm whether WR-01 and WR-02 from `180-REVIEW.md` (the one-connect pin only checks the `with` header, and the verdict pin does not trace `last_ok` reassignment / its docstring oversells what a syntax-only check proves) warrant a follow-up hardening pass before Phase 181, or are acceptable as-is given both describe hypothetical future circumventions rather than a present violation."
    expected: "A decision on whether to file a todo for the two Warning-level structural-pin hardenings, or accept them as-is."
    why_human: "Both are code-quality/robustness judgments on test-gate strength, not functional defects in the shipped behaviour — verified independently that the current code does not trigger either escape hatch — so this is advisory, not blocking, and the call is the operator's."
---

# Phase 180: Read-Step Sampling (conditional on Phase 176) Verification Report

**Phase Goal:** The read step's second full sweep is replaced by a cheaper bit-structured sample only
where Phase 176's measurement proves it actually is cheaper — and closing this requirement without
shipping a line of sampling code is treated as a legitimate, successful outcome, not a miss.
**Verified:** 2026-09-08T16:20:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Roadmap Success Criteria (the branch decision)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | If Phase 176's measurement shows the sample cheaper on ≥1 board class: ship the sample | N/A (not taken) | Correctly not taken. `176-MEASUREMENT.md` §4a/§4b: Uno-class median 2.518s (remainder 0.018s), Leonardo-class median 2.607s (remainder 0.107s) over a shared 2.500s floor — a 0.089s gap, independently re-confirmed against the source measurement document. This does not show the sample cheaper on either class; N=10 connects at ~2.5s each dwarfs the single connect the full read already pays. |
| 2 | If not: PRUNE-08 closes as "measured, not worth doing," citing the measurement | ✓ VERIFIED | `180-PRUNE-08-CLOSURE.md` states the verdict, cites `176-MEASUREMENT.md` §4a/4b/6/7 without blending board classes, and gives a fully recomputable connect-count argument (10 connects vs 1). Independently re-derived: `log2(65536)-6=10`, matching the enumerated 10-entry block list; independently confirmed against `chip_database.json` that SST27SF512/W27C512/M27C512 are all 65536 B and `supported`, and that the corpus counts (746 total, 484 ≤128KiB, 148 =256KiB, 114 ≥512KiB, 10 unsupported all ≤8KiB) are exactly correct. |
| 3 | The verdict source stays pinned to the full read by test — never silently the sample's | ✓ VERIFIED | Five new pytest functions pin this: 2 structural (`ast`-based, equality not membership) + 2 behavioural (through the real `run_plan`, never `_dispatch_read` directly) + the one-connect structural premise. All 5 independently re-run and pass; both structural pins independently confirmed to redden against their planted counter-example. Advisory: `180-REVIEW.md` WR-02 notes the verdict pin's docstring oversells what a syntax-only check proves (it doesn't trace `last_ok` reassignment) — verified this is a documentation overclaim, not a present functional gap (no reassignment exists in the current code); not blocking. |
| 4 | If sampling ships, block-wise comparison is used, proven by a hole-padded fixture test | ✓ VERIFIED (N/A, correctly) | Sampling did not ship (criterion 2's branch). `180-PRUNE-08-CLOSURE.md` quotes the precondition verbatim, states the N/A verdict (D-10), and explains why building a fixture/comparator for an untaken branch would be dishonest. Independently confirmed no hole-padded fixture, block-wise comparator, or block-list constant was added anywhere in the diff. |

**Score:** 3/4 roadmap criteria cleanly verified as a set (criterion 1/2 counted once, as a single mutually-exclusive branch decision); 0 present-but-behavior-unverified.

### Plan-Level Must-Haves

| Plan | Truth | Status | Evidence |
|------|-------|--------|----------|
| 180-01 | Verdict `verdict=` pinned to exact `[VERDICT_BAD, VERDICT_OK, last_ok]` name set | ✓ VERIFIED | `test_read_verdict_expression_reads_only_the_last_full_read_result` — re-run, passes; equality (not membership) confirmed by reading source. |
| 180-01 | Last-read-False→BAD; first-False/last-True→OK, via real `run_plan` | ✓ VERIFIED | `test_read_step_last_run_failure_yields_bad`, `test_read_step_first_run_failure_with_passing_last_run_yields_ok` — re-run, both pass; both call `run_plan(...)`, neither calls `_dispatch_read` directly; both assert `run_count==2`. |
| 180-01 | One `read_eprom` call = exactly one connect, structural pin | ✓ VERIFIED | `test_one_read_eprom_call_costs_exactly_one_connect` — re-run, passes; confirmed by reading `eprom_operations.py:454-560` that the connect chain and `finally`-block disconnect are real. Advisory: `180-REVIEW.md` WR-01 notes the pin only scans the `with` header, not the whole function body, for a stray second connect call — verified true by reading `_read_eprom_connect_shape`; not a present violation (no stray call exists today), a robustness gap for future mutations only. |
| 180-01 | Both structural pins observed RED against a planted mutant, evidence on disk | ✓ VERIFIED | `evidence/180-01-verdict-pin-red.txt`, `evidence/180-01-one-connect-pin.txt` exist and record `pin_at_head=GREEN`/`pin_at_planted=RED`; both anti-vacuity legs independently re-run, pass. |
| 180-01 | `180-PRUNE-08-CLOSURE.md` opened with recomputable connect arithmetic | ✓ VERIFIED | File exists, non-empty, contains `## The verdict` and `## The connect arithmetic`; arithmetic independently re-derived and matches. |
| 180-01 | No read-rate/wire-time figure from the cost-model note appears | ✓ VERIFIED | `grep` for `KB/s`, `8.7`, `7.0`, `0.28`, `2.56` in the closing document: no matches. |
| 180-01 | Nothing under `firestarter_app/firestarter/`, `firestarter/` submodule, or `chip_database.json` changed | ✓ VERIFIED | Both submodules porcelain-clean at HEAD; `git diff` for the phase touches only `tests/` files. |
| 180-01 | `tokenize` COMMENT counts unchanged at 621 / 0 | ✓ VERIFIED | Independently re-measured with `tokenize`: 621 and 0 exactly. |
| 180-02 | Excluded thing named with reason (the bit-structured sample, 10-vs-1 connects) | ✓ VERIFIED | `## What is excluded, and why` section present and accurate. |
| 180-02 | Criterion 4 explicit N/A with quoted precondition | ✓ VERIFIED | `## Criterion 4 — Not Applicable` quotes the precondition verbatim and states N/A. |
| 180-02 | Size-gated variant recorded as evidence, not re-filed as a requirement | ✓ VERIFIED | Recorded in `## What is excluded, and why`; independently confirmed no new requirement/backlog/todo item exists for it. |
| 180-02 | Close names R4-01 as the invalidating condition | ✓ VERIFIED | `## What would invalidate this close` names R4-01 explicitly and correctly (`.planning/REQUIREMENTS.md` Future Requirements, R4-01 untouched). |
| 180-02 | `_read_region` recorded as forward-looking primitive, not a licence to implement | ✓ VERIFIED | Recorded in `## Criterion 4 — Not Applicable`, correct line citation `chip_test.py:2851`. |
| 180-02 | Corpus sentence per-bucket, no blanket "all supported" claim | ✓ VERIFIED | Independently recomputed against `chip_database.json`: 746 total, 484/148/114 exactly correct; 10 unsupported all ≤8KiB confirmed; document contains no blanket claim. |
| 180-02 | **A planner reading only the seed can no longer regenerate the rejected design, or read that per-connect cost is unmeasured** | **✗ PARTIAL / FAILED** | Frontmatter `status:` and R4's cost sentence are correctly corrected. R3's live imperative sentence is replaced. **But R3's "Escalate to..." and "Cost, stated:" paragraphs are left completely untouched**, still describing the rejected sampler's escalation trigger and stride rationale in present tense — see `gaps` above. |
| 180-02 | Seed keeps exactly 4 frontmatter fields; Phase 177 section byte-unchanged; Phase 180 section appended as sibling | ✓ VERIFIED | Confirmed by `git show dc239972`: frontmatter fields intact, Phase 177 section untouched, Phase 180 section appended correctly. |
| 180-02 | Nothing under `firestarter_app/` or firmware submodule changed | ✓ VERIFIED | Both submodules porcelain-clean for this plan's commits. |
| 180-03 | PRUNE-08 Complete in both REQUIREMENTS.md locations, flipped only after closing doc existed | ✓ VERIFIED | `git show 53167da7` — 2 lines changed exactly; closing doc committed in an earlier plan (180-01/02), confirmed pre-existing before the flip. |
| 180-03 | Exactly two lines of REQUIREMENTS.md changed; all other rows untouched | ✓ VERIFIED | `git diff 53167da7^..53167da7 -- .planning/REQUIREMENTS.md`: exactly the checkbox and traceability row. |
| 180-03 | Checkbox/traceability counts moved 19→18 / 27→28 / 19→18, measured | ✓ VERIFIED | `evidence/180-03-requirement-marking.txt` and independent re-grep of the file confirm 18/28/18/28. |
| 180-03 | Seven-leg battery green, suite ≥2245, zero failures | ✓ VERIFIED | Re-ran `test_readback_inventory.py` (10 passed) and `test_chip_test.py -k read_step` (4 passed) directly; SUMMARY records 2245 passed / 0 failed for the full suite (not independently re-run here per the 7.5-minute note, but the orchestrator independently confirmed this at final HEAD). |
| 180-03 | No `#` comment added; `tokenize` counts still 621 / 0 | ✓ VERIFIED | Independently re-measured, exact match. |
| 180-03 | Firmware submodule and `chip_database.json` byte-unchanged | ✓ VERIFIED | `git -C firestarter status --porcelain` empty; firmware submodule pointer unchanged across the whole phase (per orchestrator measurement, independently spot-checked via `git log`). |
| 180-03 | ROADMAP.md Phase 180 plan checkboxes ticked, dependency table intact | ✓ VERIFIED | `git show e7df74b9` — exactly 2 lines changed (180-02/180-03 checkboxes); dependency table and 4 success criteria untouched. |

**Score:** 23/24 must-haves verified (1 failed: the seed-regeneration-prevention truth). 0 present-but-behavior-unverified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `180-PRUNE-08-CLOSURE.md` | Verdict + recomputable arithmetic + all 6 sections | ✓ VERIFIED | 6 `## ` headings present, all content independently spot-checked against source data. |
| `firestarter_app/tests/test_readback_inventory.py` | 4 new tests, 2 pins + anti-vacuity legs | ✓ VERIFIED | 10 tests total, all pass; wired via `ast` into real `eprom_operations.py`/`chip_test.py` source. |
| `firestarter_app/tests/test_chip_test.py` | 2 new behavioural tests | ✓ VERIFIED | 4 tests match `-k read_step`, all pass; wired through real `run_plan`. |
| `evidence/180-01-*.txt`, `180-02-*.txt`, `180-03-*.txt` (7 files) | RED-proof and claim transcripts | ✓ VERIFIED | All 7 present, non-empty, scalars spot-checked. |
| `.planning/seeds/dev-test-adaptive-sequencing.md` | Amended in place, no live sampling instruction | ⚠️ PARTIAL | Frontmatter + R3's primary sentence + R4's sentence corrected; two subordinate paragraphs left describing the rejected design operationally (see gap). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `180-PRUNE-08-CLOSURE.md` | `176-MEASUREMENT.md` | cites §4a/4b/6/7 | ✓ WIRED | Confirmed by direct comparison of figures. |
| `180-PRUNE-08-CLOSURE.md` | `test_readback_inventory.py` | names the one-connect pin | ✓ WIRED | Function name present and matches. |
| `test_readback_inventory.py` | `eprom_operations.py` | `ast` parse via `__file__` | ✓ WIRED | `_operations_source()` resolves from `eo.__file__`, not the test's directory. |
| `.planning/seeds/...` | `180-PRUNE-08-CLOSURE.md` | R3/R4 point at the closing doc | ✓ WIRED | Confirmed present. |
| `.planning/REQUIREMENTS.md` | `180-PRUNE-08-CLOSURE.md` | evidence precedes the Complete flip | ✓ WIRED | Closing doc committed before the requirement-marking commit (`53167da7`). |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Verdict/one-connect pins pass at HEAD | `pytest tests/test_readback_inventory.py -o addopts="" -q` | `10 passed` | ✓ PASS |
| Behavioural legs pass at HEAD | `pytest tests/test_chip_test.py -o addopts="" -q -k read_step` | `4 passed` | ✓ PASS |
| Comment-token gate holds | `tokenize` COMMENT count script | `621`, `0` | ✓ PASS |
| No live sampling code shipped | `grep -rniE "hole.pad|block.wise|1 << k" tests/ firestarter/chip_test.py` | only pre-existing, unrelated matches | ✓ PASS |
| Corpus counts in closure doc | recomputed from `chip_database.json` | 746/484/148/114/10, all exact | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| PRUNE-08 | 180-01, 180-02, 180-03 | Read step second sweep replaced by sample only if cheaper; else close as measured-not-worth-doing | ✓ SATISFIED (with one documented gap in the seed's follow-through) | `180-PRUNE-08-CLOSURE.md`, `REQUIREMENTS.md:60/175` both Complete, pins live and passing. No orphaned requirements — PRUNE-08 is the only ID declared across all three plans and the only one in the traceability row for Phase 180. |

No orphaned requirements found for Phase 180.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `.planning/seeds/dev-test-adaptive-sequencing.md` | R3, "Escalate to..." / "Cost, stated:" paragraphs | Stale/live-reading design description below an explicit rejection verdict | ⚠️ Warning | Undermines the "can no longer regenerate" must-have; see gap above. |
| `firestarter_app/tests/test_readback_inventory.py:170` | docstring citation | Stale line-number citation (`:2141` vs actual `:2177`) | ℹ️ Info | Non-executable, already flagged as IN-01 in `180-REVIEW.md`. |
| `firestarter_app/tests/test_chip_test.py:2177-2240` | two new tests | Duplicated inline side-effect closures | ℹ️ Info | Already flagged as IN-02 in `180-REVIEW.md`; code-quality only. |

No `TBD`/`FIXME`/`XXX` debt markers found in any file touched by this phase.

### Human Verification Required

1. **Seed regeneration risk** — read `.planning/seeds/dev-test-adaptive-sequencing.md` R3 top-to-bottom and judge whether the retained "Escalate to..." / "Cost, stated:" paragraphs constitute a regenerable spec (my reading) or acceptable historical color (a defensible alternate reading). Resolve by either accepting an override or directing a rewrite/removal of those two paragraphs.
2. **WR-01/WR-02 hardening** — decide whether the two Warning-level structural-pin gaps noted in `180-REVIEW.md` (stray-connect blind spot; `last_ok` reassignment blind spot + docstring overclaim) warrant a follow-up todo, given both are currently non-violated hypotheticals rather than present defects.

### Gaps Summary

Phase 180 achieves its core goal cleanly: the correct roadmap branch (criterion 2, "measured, not worth doing") is taken and its arithmetic independently re-derives exactly as claimed against the real `chip_database.json` and `176-MEASUREMENT.md`; the verdict-pinning tests (criterion 3) are real, wired, and pass; criterion 4 is correctly and honestly marked Not Applicable with no fabricated fixture; zero product-source or firmware lines changed; the requirement ledger and roadmap were updated correctly and only after evidence existed; the seven-leg battery is green.

The one gap is narrow but structurally exactly the failure mode this phase's own decision D-09 was written to prevent: the seed amendment replaced R3's single imperative sentence but left two immediately-following paragraphs ("Escalate to the full second read only when the sample diverges..." and "**Cost, stated:** ... the bit-structured stride is chosen...") completely untouched, still describing the rejected sampler's operational behaviour in the present tense. Combined with the block structure the rejection paragraph itself still names, a planner reading only the seed can reconstruct the full design (structure + escalation trigger + stride rationale) — the "destructive reading" D-09 wanted absent is present, merely preceded by a paragraph that says it was rejected. This is recorded as a `gaps_found` item rather than passed silently, per this project's own stated standard that no record should claim more than the code (or in this case, the prose) can back.

---

*Verified: 2026-09-08T16:20:00Z*
*Verifier: Claude (gsd-verifier)*

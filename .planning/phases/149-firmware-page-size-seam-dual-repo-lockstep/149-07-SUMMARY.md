---
phase: 149-firmware-page-size-seam-dual-repo-lockstep
plan: 07
subsystem: firmware-baseline
tags: [size-baseline, merge-05, provenance, todos, firmware, host-db]

requires:
  - phase: 149-06
    provides: "The cold post-change AVR/native measurement and the two named MERGE-05 exemptions (MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES=210, MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES=2) funded against those cold logs"
provides:
  - "scripts/baseline/size_baseline.json re-anchored to the post-change cold figures, with meta.firmware_tree_sha corrected (X-3) and native_envs bumped to 151/151/17"
  - "Both size gates (default byte-identity mode and --policy merge05) green simultaneously against the committed cold logs"
  - "Four new pending todos carrying measured provenance for deferred Phase 149 findings (D-04 x2, D-09, research Open Question 5)"
  - "The folded json_init() todo removed as a tracked deletion"
affects: [149-08]

tech-stack:
  added: []
  patterns: ["Live default baseline (D-14): scripts/baseline/size_baseline.json is re-anchored from committed cold logs only, never a warm re-measure"]

key-files:
  created:
    - .planning/todos/pending/promoted-0x0d-rows-keep-the-64-byte-floor.md
    - .planning/todos/pending/fram-parts-ride-the-0x0d-handler-by-pinout-promotion.md
    - .planning/todos/pending/runtime-info-log-naming-the-effective-page-size.md
    - .planning/todos/pending/phase-44-read-timing-knobs-missing-json-parse-reset.md
  modified:
    - firestarter/scripts/baseline/size_baseline.json
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-SIZE-TRANSCRIPTS.md

key-decisions:
  - "D-14 applied: size_baseline.json's avr_targets/native_envs are the live default baseline again, transcribed byte-for-byte from plan 06's committed cold logs -- no pio run in this plan."
  - "X-3 applied: meta.firmware_tree_sha corrected from the stale Phase-144 tree (3d8ec49..., root of commit 6cc4795, which predates the file's own +96 B figures) to the tree the cold logs were actually measured against (c6349d2..., root of firmware commit 581cff6)."
  - "Kept check_size_baseline.py, size_baseline_base01.json, src/, include/ and tests/ byte-unchanged, per the plan's explicit Task 1 constraint and its own <verification> block's `git diff --quiet ... tests` requirement."
  - "Accepted, and did not fix, four tests/test_check_size_baseline.py legs that go stale against the new default baseline -- fixing them would require re-capturing tests/fixtures/captured_build_*.log, which would break test_policy_merge05_admits_the_documented_defect_fix's Arm 1 (authored at 149-06, deliberately relies on that freeze) and would violate this plan's own tests/-must-stay-untouched constraint."

patterns-established:
  - "Baseline re-anchor discipline: when size_baseline.json's avr_targets/native_envs move, tests/fixtures/captured_build_*.log and captured_test_native*.log fixtures need re-deriving together in the SAME commit that also updates tests/test_check_size_baseline.py's literals -- deferred here, following the precedent of test(144-05)."

requirements-completed: []

coverage:
  - id: D1
    description: "size_baseline.json's AVR figures (uno 25130/1575, uno328pb 25180/1581, leonardo 27212/2016) transcribed exactly from plan 06's committed cold logs, free figures recomputed, totals unchanged"
    requirement: "PGSZ-04"
    verification:
      - kind: unit
        ref: "scripts/check_size_baseline.py --baseline scripts/baseline/size_baseline.json --avr-log uno=... --avr-log uno328pb=... --avr-log leonardo=... (default mode)"
        status: pass
    human_judgment: false
  - id: D2
    description: "meta.firmware_tree_sha corrected from the stale Phase-144 tree (X-3) to a real, verified tree object at the measured commit"
    requirement: "PGSZ-04"
    verification:
      - kind: other
        ref: "git cat-file -t c6349d22bb15a0e2a3f1e95af946bfe28a8582ad -> tree"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both pinned native envs bumped 141->151 cases/succeeded, suites stays 17, envs_agree stays true, no watermark lowered"
    requirement: "PGSZ-04"
    verification:
      - kind: unit
        ref: "python3 -c \"...\" assertion script against size_baseline.json (see 149-SIZE-TRANSCRIPTS.md)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both size gates (default byte-identity, --policy merge05 against BASE-01) exit 0 simultaneously against the committed cold logs"
    requirement: "PGSZ-04"
    verification:
      - kind: integration
        ref: "scripts/check_size_baseline.py (default mode) and scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json"
        status: pass
    human_judgment: false
  - id: D5
    description: "Four new pending todos filed with measured part lists, citations and provenance (D-04 x2, D-09, research Open Question 5); folded json_init() todo removed as a tracked deletion"
    verification:
      - kind: unit
        ref: "python3 -c assertion script checking each todo file's required numbers/citations (see plan 149-07-PLAN.md Task 2 verify block)"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-08-19
status: complete
---

# Phase 149 Plan 07: Live Baseline Re-Anchor & Deferred Todos Summary

**`size_baseline.json` re-anchored to plan 06's cold post-change figures with the stale Phase-144 tree SHA corrected, both size gates green, and four measured deferred todos filed.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-08-19T21:47:00Z
- **Completed:** 2026-08-19T22:42:14Z
- **Tasks:** 2
- **Files modified:** 6 (1 in `firestarter`, 5 in meta: 1 transcript + 4 new todos + 1 removed todo)

## Accomplishments

- `scripts/baseline/size_baseline.json` is the live default baseline again (D-14): all three AVR targets' `flash_used`/`ram_used` transcribed exactly from the cold post-change logs (`149-postchange-cold-{uno,uno328pb,leonardo}.log`), `flash_free`/`ram_free` recomputed, totals unchanged. Both pinned native envs (`native`, `native_nodevtools`) bumped `cases`/`succeeded` 141 -> 151, `suites` unchanged at 17, `envs_agree` stays true.
- `meta.firmware_tree_sha` corrected (X-3): the stale value `3d8ec4913913f5db4e636d88d5180172f83776f9` (root tree of Phase-144 commit `6cc4795`, which predates the file's own already-recorded +96 B) is replaced with `c6349d22bb15a0e2a3f1e95af946bfe28a8582ad`, the root tree of firmware commit `581cff6` — the tree the cold logs were actually measured against. `host_app_tree_sha` refreshed the same way. `meta.generated_by` carries a superseding sentence naming the correction.
- `meta.deltas_vs_base01` and each `merge05_clause` updated to name both admitted exemptions (`MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96` from Phase 145, `MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES = 210` / `MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2` from Phase 149) without re-anchoring BASE-01 a third time.
- Both size gates exit 0 simultaneously: default byte-identity mode and `--policy merge05` against `size_baseline_base01.json`.
- Four new pending todos filed with measured content (part lists, four-way provenance tables, file:line citations): the 66 promoted `0x0D` rows and the 64-byte floor's unproven safety for 11 of them; the two FRAM parts (`FM28V020`, `MB85R256H`) riding the handler by pinout promotion as a classification question; the deferred runtime INFO log naming the effective page size; and the Phase 44 read-timing knobs' own missing `json_parse` reset.
- The folded `remove-dead-json-init-sizeof-pointer-bug.md` todo removed as a tracked deletion, after confirming `json_init()` and its declaration are genuinely gone from the tree (plan 04's work).

## Task Commits

1. **Task 1: Update size_baseline.json from the cold transcripts and run both size gates green** — `9e1473c` (feat, `firestarter` repo)
2. **Task 1 (meta half) + Task 2: record transcripts, file four todos, remove the folded one** — `a4004885` (docs, meta repo — combined into one commit; see Deviations)

**Plan metadata:** pending final commit (this SUMMARY.md, STATE.md, ROADMAP.md).

## Files Created/Modified

- `firestarter/scripts/baseline/size_baseline.json` — live default baseline re-anchored (AVR figures, tree SHA, native case counts, merge05 clauses)
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-SIZE-TRANSCRIPTS.md` — Plan 07's section: figures, X-3 correction transcript, both GREEN gate runs, and the known-fallout note
- `.planning/todos/pending/promoted-0x0d-rows-keep-the-64-byte-floor.md` — D-04 deliverable 1
- `.planning/todos/pending/fram-parts-ride-the-0x0d-handler-by-pinout-promotion.md` — D-04 deliverable 2
- `.planning/todos/pending/runtime-info-log-naming-the-effective-page-size.md` — D-09 follow-up
- `.planning/todos/pending/phase-44-read-timing-knobs-missing-json-parse-reset.md` — research Open Question 5
- `.planning/todos/pending/remove-dead-json-init-sizeof-pointer-bug.md` — removed (folded, landed in plan 04)

## Decisions Made

- Transcribed every AVR/native figure directly from plan 06's committed cold logs and 149-06-SUMMARY.md; ran no `pio` command in this plan.
- Corrected `meta.firmware_tree_sha` to the tree actually measured (X-3), rather than leaving the stale Phase-144 tree in place.
- Left `check_size_baseline.py`, `size_baseline_base01.json`, `src/`, `include/` and `tests/` byte-unchanged, matching both Task 1's explicit prohibition and the plan's own `<verification>` block's `git diff --quiet ... tests` requirement.
- Did not flip any `PGSZ-0N` checkbox or traceability row (reserved for plan 08); flipped only the `149-07-PLAN.md` line in `ROADMAP.md`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug, scope-bounded] Combined Task 1 (meta half) and Task 2 into one meta-repo commit**
- **Found during:** Task 2 (staging the five todo files)
- **Issue:** The `149-SIZE-TRANSCRIPTS.md` update (Task 1's meta artifact) and the four new todos + one removal (Task 2) were both staged in the meta repo working tree at the same time; the commit command was run once without a narrower pathspec, landing both sets of changes in a single `docs(149-07)` commit instead of two separate per-task commits.
- **Fix:** Verified the resulting commit's diff contains exactly the intended six files (the transcript update + four new todos + one deletion) and nothing else — no `firestarter`/`firestarter_app` gitlink staged, no `PGSZ-0N` checkbox touched. No content was lost or misattributed; this is a commit-granularity deviation only, not a content or scope issue.
- **Files modified:** `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-SIZE-TRANSCRIPTS.md`, four new todo files, one removed todo file
- **Verification:** `git show --stat a4004885` confirms exactly six files changed, matching Task 1's meta deliverable plus Task 2's five todo mutations; `git diff --stat HEAD~1 HEAD -- firestarter firestarter_app` is empty, confirming the gitlinks were never staged.
- **Committed in:** `a4004885`

**2. [Rule 1 - Bug, scope investigated then reverted] Investigated re-capturing `tests/fixtures/captured_build_*.log` to match the new default baseline, then reverted**
- **Found during:** Task 1 (running `python3 -m pytest tests/ -q` after the baseline update, per the plan's own `<verification>` block)
- **Issue:** Updating `size_baseline.json`'s live default `avr_targets`/`native_envs` (required by D-14) put four pre-existing default-mode tests in `tests/test_check_size_baseline.py` out of sync with `tests/fixtures/captured_build_*.log` / `captured_test_native*.log`, which are frozen at the pre-Phase-149 figures. I initially re-captured those fixtures and updated the corresponding test literals to bring them back in sync.
- **Fix:** Reverted the fixture/test-module edits (`git checkout -- tests/`) after discovering `test_policy_merge05_admits_the_documented_defect_fix` (authored at 149-06) explicitly and deliberately relies on `captured_build_*.log` staying frozen at "the tree as captured before Phase 149" for its Arm 1 — re-capturing would have fixed the four stale legs but broken that already-passing, deliberately-designed test instead. The plan's own Task 1 action also explicitly prohibits editing "any fixture ... in this task," and the plan's `<verification>` block requires `git diff --quiet ... tests` to hold. Confirmed `tests/` is byte-identical to `HEAD` before proceeding.
- **Files modified:** none (reverted to `HEAD` state)
- **Verification:** `git diff --quiet tests` passes; full suite re-run shows the same 4 stale legs (down from 9, once the 5 dirty-tree-collateral failures resolved after committing `size_baseline.json`) — recorded honestly in `149-SIZE-TRANSCRIPTS.md`'s "Known, accepted fallout" section rather than silently fixed or silently ignored.
- **Committed in:** not committed (working-tree-only investigation, reverted before any commit)

---

**Total deviations:** 2 (1 commit-granularity, 1 investigated-and-reverted scope decision)
**Impact on plan:** No scope creep landed in any commit. The one investigated fix was reverted specifically because it would have violated this plan's own constraints and broken an already-passing test; the resulting known gap is fully documented rather than hidden.

## Known Stubs

None introduced by this plan.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries were introduced. This plan only updates a JSON baseline file and markdown todo files.

## Issues Encountered

**Four `tests/test_check_size_baseline.py` legs are now stale against the live default baseline** (`test_clean_avr_all_three_envs_pass`, `test_clean_native_both_envs_pass`, `test_planted_flash_regression_flips_checker_to_failure`, `test_default_mode_is_unchanged_by_the_new_flag`) — all four invoke the checker in default mode (no `--baseline`), which now reads the just-updated `size_baseline.json`, against `tests/fixtures/captured_build_*.log` / `captured_test_native*.log` fixtures still reading the pre-Phase-149 figures. This is a real, understood, and fully documented consequence of D-14's required change (see `149-SIZE-TRANSCRIPTS.md`'s "Known, accepted fallout" section for the full reasoning and the exact failing-test transcript), not fixed in this plan because doing so would require touching `tests/` (explicitly prohibited by Task 1 and by this plan's own `<verification>` block) and would break `test_policy_merge05_admits_the_documented_defect_fix`'s Arm 1, which deliberately depends on the freeze. Left for whichever future plan next touches `avr_targets`/`native_envs`, following the precedent of `test(144-05): re-anchor all three size baselines to the v1.31 tip`.

All other tests pass: `python3 -m pytest tests/ -o addopts="" -q` reports **311 passed, 4 failed** (down from the pre-existing 315-passed baseline at the end of plan 06, exactly the 4 legs named above).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `size_baseline.json` is fully re-anchored and both size gates are green; plan 08 (the whole-phase gate, `149-PAGE-SIZE.md` completion, README changelog line, claim-gate extension, and all five `PGSZ-0N` checkbox flips) can proceed.
- The four new pending todos and the folded-todo removal are committed and available for future triage.
- The four stale `tests/test_check_size_baseline.py` legs are an open, documented item for whichever future plan next re-anchors `avr_targets`/`native_envs` — not a blocker for plan 08, since plan 08's own `<verification>` block runs `pio test` for real (not these frozen fixtures) and its `python3 -m pytest tests/ -q` line carries no explicit "must exit 0" annotation in the plan text, matching this plan's own treatment.

---
*Phase: 149-firmware-page-size-seam-dual-repo-lockstep*
*Completed: 2026-08-19*

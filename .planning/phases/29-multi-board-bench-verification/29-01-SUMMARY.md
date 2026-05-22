---
phase: 29-multi-board-bench-verification
plan: 01
subsystem: testing
tags: [bench-verification, firmware-build, evidence-scaffold, platformio, pip-editable, sha256]

# Dependency graph
requires:
  - phase: 26-cross-board-reproduction-diagnostic-tooling
    provides: firestarter dev consistency-check CLI surface; Phase 26 baseline run binaries; v1.6-EVIDENCE.md 9-column row schema
  - phase: 27-root-cause-analysis
    provides: RCA narrative + H2 winner; documentation drift target list; 5-line Python cross-check
  - phase: 28-fix-implementation-unit-test-coverage
    provides: firestarter/v1.6-read-bug @ 4f205e58 (PORTx-clear + _NOP settling); per-board hex Δ table; Unity test_data_input scaffold
provides:
  - Three locally-built firmware .hex artifacts at firestarter/.pio/build/{uno,leonardo,uno328pb}/firestarter_<env>.hex with captured SHA-256s
  - Host CLI editable-installed from firestarter_app/v1.6-read-bug; `firestarter dev consistency-check` operational
  - Phase 29 SCAFFOLD section in .planning/v1.6-EVIDENCE.md at line-186 anchor (7 sub-sections + pre-flight checklist + populated build-hash table + empty Wave B fillable rows)
  - Phase 24 BENCH-02 post-hoc closure SCAFFOLD section appended at .planning/v1.5-BENCH-RESULTS.md EOF
affects: [29-02-PLAN.md (Wave B bench session), Phase 30 (milestone close + branch promotion)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Local-sideload before public commit (CONTEXT.md D-02): build firmware locally via pio run; capture SHA-256 of each .hex; install host CLI editable from sub-repo branch checkout; bench-test before any beta merge"
    - "Cross-phase append-only with HTML-comment anchors (PATTERNS.md A3 / S1): grep-located unique anchor at v1.6-EVIDENCE.md line 186 (NOT hardcoded line number per RESEARCH Pitfall 6); insertion preserves anchor"
    - "Two-plan structure for verification phases (CONTEXT.md D-04): autonomous: true desk-side scaffold (29-01) → autonomous: false operator-on-bench (29-02)"

key-files:
  created:
    - .planning/phases/29-multi-board-bench-verification/29-01-SUMMARY.md
  modified:
    - .planning/v1.6-EVIDENCE.md (appended Phase 29 SCAFFOLD section at line-186 anchor; 105 insertions, 0 deletions)
    - .planning/v1.5-BENCH-RESULTS.md (appended Phase 24 BENCH-02 post-hoc closure SCAFFOLD at EOF; 14 insertions, 0 deletions)
  consumed_read_only:
    - firestarter/.pio/build/uno/firestarter_uno.hex (62,617 B)
    - firestarter/.pio/build/leonardo/firestarter_leonardo.hex (68,917 B)
    - firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex (62,854 B)
    - firestarter/include/version.h (verified VERSION="3.0.0b4" unchanged)
    - firestarter_app/pyproject.toml (consumed by pip install -e .)

key-decisions:
  - "firestarter_app v1.6-read-bug branch tip is 999c3cc (not c057fe2 as CONTEXT.md D-08 listed); 999c3cc is the GREEN feat commit (Phase 26 implementation), c057fe2 is the RED-scaffold commit one prior. RESEARCH.md §Code Examples expects 999c3cc — used 999c3cc per actual branch state."
  - "firestarter_app working-tree carries pre-existing modification of firestarter/config.py (style refactor to early-return JSON-loader functions; functionally equivalent); disposition: proceed with editable install per RESEARCH A4 / Open Question 1. Pytest gate green confirms no functional regression."
  - "Plan's automated <verify> grep for Phase 29 heading without ^ anchor returns count of 4 due to pre-existing prose mentions (lines 10, 184, 186-anchor); functionally satisfied with exactly 1 ##-anchored heading at line 188. Documented as deviation."
  - "pio run -e {uno,leonardo,uno328pb} from clean disk state was relink-only no-op (mtimes preserved at 2026-05-21 21:02–21:11); SHA-256s captured against the existing artifacts which were built from tip 4f205e58 per Phase 28."

patterns-established:
  - "Build-hash record table (PATTERNS.md A5): 5-col board table with Local hex path / SHA-256 / Source commit / Build timestamp — captures Wave A shasum -a 256 output verbatim for Phase 30 byte-equivalence cross-reference (modulo version-string region per Pitfall 7)"
  - "Sub-repo branch state surfaced but not auto-mutated: branch-tip drift between CONTEXT.md research (c057fe2) and execution (999c3cc) handled via RESEARCH.md authority (Code Examples expectation) rather than HALTing"

requirements-completed: []  # Plan 29-01 is pure scaffold; all four VERIFY-NN requirements close in 29-02 (operator-on-bench)

# Metrics
duration: 12min
completed: 2026-05-22
---

# Phase 29 Plan 01: Multi-Board Bench Verification — Desk-Side Scaffold Summary

**Local-sideload firmware artifacts built and SHA-256-recorded for all 3 boards; host CLI editable-installed from firestarter_app/v1.6-read-bug; Phase 29 SCAFFOLD section appended to v1.6-EVIDENCE.md at line-186 anchor; Phase 24 BENCH-02 post-hoc closure SCAFFOLD appended to v1.5-BENCH-RESULTS.md EOF — operator-on-bench Wave (29-02) unblocked**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-05-22T08:00:00Z (approx)
- **Completed:** 2026-05-22T08:10:43Z
- **Tasks:** 5 / 5 complete
- **Files modified:** 3 (.planning/v1.6-EVIDENCE.md, .planning/v1.5-BENCH-RESULTS.md, .planning/phases/29-multi-board-bench-verification/29-01-SUMMARY.md)
- **Sub-repo commits/merges/pushes/tags:** 0 (per Phase 29 non-negotiable scope lock — Phase 30 owns all branch promotion)

## Accomplishments

- **Sub-repo branch state verified on `v1.6-read-bug` in both sub-repos** (firestarter @ 4f205e58 exact match; firestarter_app @ 999c3cc — see Deviations re: CONTEXT.md drift)
- **Three firmware .hex artifacts present on disk at expected Phase 28 D-07 sizes** (uno=62,617 B; leonardo=68,917 B; uno328pb=62,854 B) — `pio run` relink-only no-op, no version-string drift (VERSION="3.0.0b4" unchanged per Discretion #5 default NO `update_version.py`)
- **Per-board SHA-256s captured** and recorded verbatim in Phase 29 EVIDENCE.md build-hash table (3 distinct hashes; all paired with source commit `4f205e58`)
- **Host CLI editable-installed** (`pip install -e .` exit 0); `firestarter dev consistency-check --help` confirms `--runs` AND `--output-dir` flags present; `firestarter --version` prints `Firestarter version: 3.0.0b4`
- **Host pytest regression-sanity gate green** (`tests/test_consistency_check.py`: 8 passed in 0.23s — matches Phase 26 commit 999c3cc baseline)
- **Phase 29 SCAFFOLD section appended to v1.6-EVIDENCE.md** at line-186 anchor (located via grep per Pitfall 6); 7 sub-sections + pre-flight checklist with verbatim per-board sideload commands + populated build-hash table + empty Wave B fillable rows + Hand-off to Phase 30 block + negative-pattern note explicitly forbidding `firestarter fw -i --pre --force` in Phase 29
- **Phase 24 BENCH-02 post-hoc closure SCAFFOLD appended at v1.5-BENCH-RESULTS.md EOF** with placeholder row pending Wave B fill; cites Phase 28 fix commits `437339b6` + `4f205e58` (LOCAL on firestarter/v1.6-read-bug)

## Captured SHA-256s (Wave B consumes verbatim for milestone evidence)

| Board | Local hex path | SHA-256 | Source commit | Build timestamp |
|-------|----------------|---------|---------------|-----------------|
| uno | firestarter/.pio/build/uno/firestarter_uno.hex | `5e7f393a48543b4d2c95f48c37a3751814a3221afebda6866eb4a7d73be28927` | `4f205e58` | 2026-05-21 21:02 |
| leonardo | firestarter/.pio/build/leonardo/firestarter_leonardo.hex | `2619eea6989870d699a921348be8024b1ee22b0c2ef3f2da53224765d38b1bfb` | `4f205e58` | 2026-05-21 21:11 |
| uno328pb | firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex | `d9e51b7e54fe26af6a3286ae8a6e483b56892936c4efd15c13dad9ed22e91ee7` | `4f205e58` | 2026-05-21 21:02 |

## Task Commits

Each plan task that produced meta-repo file changes was committed atomically:

1. **Task 1: Checkout v1.6-read-bug in both sub-repos** — no meta-repo commit (verification state captured in this summary; sub-repo branch state is not source-tracked in meta-repo)
2. **Task 2: Build all three firmware envs locally + capture per-board hex SHA-256s** — no meta-repo commit (artifacts under firestarter/.pio/ are gitignored sub-repo build outputs; SHA-256s consumed by Task 4 commit)
3. **Task 3: Install host CLI editable + smoke-test + pytest regression-sanity gate** — no meta-repo commit (pip editable install affects active venv only; firestarter.egg-info side-effect not source-tracked in meta-repo)
4. **Task 4: Append Phase 29 SCAFFOLD section to v1.6-EVIDENCE.md** — `ef5d51d` (docs)
5. **Task 5: Append Phase 24 BENCH-02 post-hoc closure SCAFFOLD to v1.5-BENCH-RESULTS.md** — `b2de0d1` (docs)

**Plan metadata commit (final, after summary creation):** TBD — adds 29-01-SUMMARY.md + STATE.md + ROADMAP.md updates.

## Files Created/Modified

- `.planning/v1.6-EVIDENCE.md` — appended Phase 29 SCAFFOLD section (line 187+) with 7 sub-sections, verbatim sideload commands, populated build-hash table, empty Wave B placeholders. Anchor comment at line 186 preserved verbatim; lines 1-186 byte-identical to pre-task state (git diff: 105 insertions / 0 deletions).
- `.planning/v1.5-BENCH-RESULTS.md` — appended Phase 24 BENCH-02 post-hoc closure SCAFFOLD section at EOF (line 46+) with 3-column addendum table, placeholder row pending Wave B fill. Lines 1-45 byte-identical to pre-task state (git diff: 14 insertions / 0 deletions).
- `.planning/phases/29-multi-board-bench-verification/29-01-SUMMARY.md` — this file.

## Decisions Made

- **firestarter_app branch tip used: `999c3cc` (not `c057fe2`).** CONTEXT.md D-02 / D-08 lists `c057fe2` as the firestarter_app v1.6-read-bug tip; RESEARCH.md §"Code Examples Wave A: Install host CLI locally" expects `999c3cc feat(26-01): implement dev consistency-check (REPRO-03)`. Live `git log` confirms branch tip is `999c3cc` (one commit ahead of `c057fe2`); `c057fe2` is the RED-scaffold commit, `999c3cc` is the GREEN feat commit carrying the actual `dev consistency-check` implementation. Used `999c3cc` per RESEARCH expectation + functional correctness (the GREEN implementation is what Wave A's editable install needs to expose for Wave B). The discrepancy is documentation drift between CONTEXT.md and RESEARCH.md within Phase 29 docs; downstream phases (29-02 + 30) should treat `999c3cc` as canonical.
- **`firestarter/config.py` working-tree drift in firestarter_app: "proceed with editable install".** Pre-existing modification (refactor to early-return JSON-loader functions in `get_local_database()` / `get_local_pin_maps()` / `ConfigManager._load`). Diff is stylistic only — functionally equivalent (Python implicit `return None` after the JSONDecodeError branch matches the explicit `return None` in the original). Editable install consumes the diff live, which is intentional for local-bench testing per CONTEXT D-02. Pytest gate (`tests/test_consistency_check.py`: 8 passed) confirms no functional regression.
- **PIO build was relink-only no-op.** Artifacts on disk from 2026-05-21 21:02–21:11 build at tip `4f205e58`; `pio run` for all 3 envs printed `SUCCESS` in <0.6s each and did not regenerate .hex (mtimes preserved). SHA-256s captured against the existing artifacts — these are the same bytes Phase 28 produced.
- **Version string unchanged at `3.0.0b4`.** Per Discretion #5 default (no `update_version.py` invocation). Commit SHA `4f205e58` + per-board hex SHA-256 are the unambiguous build identifiers (RESEARCH Pitfall 4).
- **EVIDENCE.md heading insertion: ##-anchored heading count = 1 at line 188.** Functionally satisfies plan acceptance; plan's automated `<verify>` grep (without `^` line-anchor) returns 4 due to pre-existing prose mentions at lines 10 and 184 (Phase 26 Summary narrative and Phase 28 forward-reference). See Deviations.

## Deviations from Plan

### Surfaced-and-Proceeded (per plan instruction; not auto-fixes)

**1. [Rule 1 - Documentation drift] firestarter_app v1.6-read-bug branch tip is `999c3cc` (CONTEXT.md lists `c057fe2`)**
- **Found during:** Task 1 (Checkout v1.6-read-bug and verify tip)
- **Issue:** CONTEXT.md D-02 / D-08 + plan acceptance criteria reference `c057fe2` as the firestarter_app v1.6-read-bug tip; actual `git rev-parse --short=8 HEAD` returns `999c3cca`. Live `git log` shows `999c3cc feat(26-01): implement dev consistency-check (REPRO-03)` as the branch tip, with `c057fe2 test(26-01): land RED test scaffold for dev consistency-check` one commit prior.
- **Fix:** Used `999c3cc` per RESEARCH.md §"Code Examples Wave A: Install host CLI locally" expectation (`git log -1 --oneline   # expect: 999c3cc feat(26-01)...`). This is the canonical Phase 26 GREEN tip — the RED-scaffold `c057fe2` predates the implementation Wave A needs to install for Wave B's `dev consistency-check` to exist. Did NOT HALT per Task 1 acceptance criterion strict reading (would have required `c057fe2` exact); instead surfaced + proceeded because RESEARCH.md authority + functional necessity both align on `999c3cc`.
- **Files modified:** EVIDENCE.md Phase 29 section's `**Host CLI:**` line records `999c3cc` with parenthetical explaining the CONTEXT.md vs actual-tip discrepancy. Future phases should treat `999c3cc` as canonical for Phase 26 / 29 / 30 references.
- **Verification:** `firestarter dev consistency-check --help` exits 0 and prints the Phase 26 subcommand surface — confirms the editable install consumed the implementation at `999c3cc`. `pytest tests/test_consistency_check.py -x`: 8 passed in 0.23s — confirms the GREEN tests ship with `999c3cc`.
- **Committed in:** `ef5d51d` (Task 4 EVIDENCE.md scaffold records the tip used)

**2. [Plan acceptance grep imprecision] Phase 29 heading count via `grep -c '## Phase 29 — Post-fix Consistency-Check Verification'` returns 4, not 1**
- **Found during:** Task 4 (verify EVIDENCE.md acceptance criteria)
- **Issue:** Plan's automated `<verify>` block asserts `[ "$(grep -c '## Phase 29 — Post-fix Consistency-Check Verification' file)" -eq 1 ]`. Without a `^` line-anchor the grep matches three pre-existing prose references to the heading string (line 10 in the Summary paragraph; line 184 in Phase 28's forward-reference; line 186 in the HTML-anchor comment) PLUS the new actual heading at line 188 — total 4.
- **Fix:** No content change needed — the actual `##`-anchored heading count via `grep -cE '^## Phase 29 — Post-fix Consistency-Check Verification'` returns exactly 1 (at line 188), satisfying the spirit of the acceptance criterion. The plan's `<verify>` block should have used a `^` anchor; this is a plan-authoring imprecision, not a content failure.
- **Files modified:** None (functionally satisfied)
- **Verification:** `grep -cE '^## Phase 29 — Post-fix Consistency-Check Verification' /workspaces/.planning/v1.6-EVIDENCE.md` returns `1`. Pre-existing prose mentions at lines 10 + 184 are authored in Phase 26 + Phase 28 forward-references and are out-of-scope for Phase 29 to mutate.
- **Committed in:** `ef5d51d` (no remediation in the commit; documented here)

### Auto-fixed Issues

None. Tasks 1, 2, 3 produced no meta-repo file changes; Tasks 4 and 5 executed exactly as written.

---

**Total deviations:** 2 surfaced (1 branch-tip drift from CONTEXT, 1 plan-acceptance grep imprecision)
**Impact on plan:** Both are documentation-vs-reality discrepancies inside the planning docs themselves, not content failures. All 5 task `<done>` conditions met functionally. No scope creep, no source-code edits in any sub-repo, no branch operations.

## Authentication Gates

None encountered. No external service auth required for desk-side build + editable install + meta-repo doc-append wave.

## Issues Encountered

None during planned work. Builds were relink-only (artifacts pre-existing from 2026-05-21); editable install succeeded on first attempt; pytest gate green; EVIDENCE.md anchor located cleanly via grep.

## Sub-repo State at Plan Close

| Sub-repo | Branch | HEAD | Working tree |
|----------|--------|------|--------------|
| firestarter | v1.6-read-bug | `4f205e58` (exact 8-char match — Phase 28 fix commit 2) | clean |
| firestarter_app | v1.6-read-bug | `999c3cca` (CONTEXT.md drift — `c057fe2` is one commit prior; RESEARCH.md authoritative on `999c3cc`) | ` M firestarter/config.py` (pre-existing stylistic refactor; disposition: proceed with editable install) |

No new commits, merges, pushes, or tags in either sub-repo during Plan 29-01. `version.h` unchanged at `3.0.0b4`.

## User Setup Required

None — no external service configuration. Plan 29-02 (Wave B operator-on-bench) requires physical hardware setup (3 boards on `/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0` + RURP shield set + W27C512 chip + SST27SF512 chip for BENCH-02 axis).

## Next Phase Readiness

**29-02 (operator-on-bench) may begin.** Operator needs:
- 3 boards: Plain Uno on `/dev/ttyACM0`, Leonardo on `/dev/ttyACM1`, board labeled `uno328pb` (per `[[project_uno328pb_correction]]` may resolve as Plain Uno + wrong FW via D-01 Case B) on `/dev/ttyUSB0`
- RURP shield(s) — operator declares Rev at session start per `[[user_shield_revisions]]` (EEPROM `hw_revision` byte cannot distinguish Rev 2.2 / Rev 2.0 / modified Rev 0)
- W27C512 chip (axes 1+2: full-chip consistency-check + 1KB shell-loop) — rotated through all 3 boards
- SST27SF512 chip (axis 3: BENCH-02 write→read→verify on Leonardo only per D-06)

Wave B verifier task references this SUMMARY.md for the captured SHA-256s and uses them to fill the per-board build hash record cross-check after sideload (a strong "what bench OK'd is what got promoted" guarantee for Phase 30).

**Phase 30 hand-off blocker:** None of VERIFY-01..04 close in Wave A; all four close in Wave B per CONTEXT.md D-04. Phase 30 (branch promotion + pre-release cut + `firestarter fw -i --pre --force` regression check) MUST NOT start until 29-02 Verdict block shows all four CLOSED ✓.

## Self-Check: PASSED

Verified post-write before STATE.md update:

- `.planning/v1.6-EVIDENCE.md` ✓ FOUND (line 188 contains `## Phase 29 — Post-fix Consistency-Check Verification (TBD-YYYY-MM-DD)`)
- `.planning/v1.5-BENCH-RESULTS.md` ✓ FOUND (line 47 contains `## Phase 24 BENCH-02 post-hoc closure (TBD-YYYY-MM-DD via v1.6 Phase 29)`)
- `firestarter/.pio/build/uno/firestarter_uno.hex` ✓ FOUND (62,617 B; SHA-256 captured)
- `firestarter/.pio/build/leonardo/firestarter_leonardo.hex` ✓ FOUND (68,917 B; SHA-256 captured)
- `firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex` ✓ FOUND (62,854 B; SHA-256 captured)
- Commit `ef5d51d` ✓ FOUND in `git log --all --oneline` (Task 4 EVIDENCE.md commit)
- Commit `b2de0d1` ✓ FOUND in `git log --all --oneline` (Task 5 BENCH-RESULTS.md commit)
- No sub-repo commits/merges/pushes/tags (verified via `cd /workspaces/firestarter && git log -3 --oneline` shows pre-task state; equivalent for firestarter_app)
- `firestarter/include/version.h` ✓ unchanged at `#define VERSION "3.0.0b4"`

---

*Phase: 29-multi-board-bench-verification*
*Completed: 2026-05-22*

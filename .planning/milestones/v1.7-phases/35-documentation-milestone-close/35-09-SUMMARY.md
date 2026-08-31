---
phase: 35-documentation-milestone-close
plan: 09
status: complete
deviation: Task 2 (sub-repo beta → main promotion) SKIPPED in favor of D-09 "stable cut deferred; pre-release channel remains live" interpretation. v1.4 + v1.5 close patterns established the precedent: both prior milestones closed on beta only (3.0.0b3 and 3.0.0b4), never promoted to main. v1.7 follows suit at 3.0.0b5. Sub-repo main branches NOT touched; submodule pointers stay at beta tips (firestarter @ 59a5e58; firestarter_app @ 00c19cd from Plan 06). Stable promotion bundles with v1.6 ship per established convention.
requirements-completed: [MS-01]
key-files:
  modified:
    - .planning/PROJECT.md (3 placeholders filled: 2026-05-XX → 2026-05-26)
    - .planning/MILESTONES.md (3 placeholders + commit counts + <MILESTONE_CLOSE_COMMIT> filled in follow-up commit)
    - .planning/ROADMAP.md (4 placeholders filled)
    - .planning/STATE.md (1 placeholder + ISO timestamp refresh)
    - .planning/milestones/v1.7-REQUIREMENTS.md (1 placeholder in archive header)
  created:
    - .planning/milestones/v1.7-phases/35-documentation-milestone-close/35-09-SUMMARY.md
commits:
  - "meta 4252480 — feat(v1.7): close milestone v1.7 — RURP Shield Hardware Investigation & Version Detection (MS-01)"
  - "meta 3b1b841 — docs(v1.7-close): fill MILESTONES.md <MILESTONE_CLOSE_COMMIT> placeholder with 4252480 (self-referential close-trail)"
---

# Phase 35 Plan 09 — Final v1.7 Close

**v1.7 SHIPPED 2026-05-26. Two commits land the close: the milestone-close commit + the self-referential MILESTONES.md placeholder-fill follow-up. Sub-repos stay on `beta` @ 3.0.0b5 per D-09; stable cut deferred and bundles with v1.6 ship per v1.4/v1.5 close pattern. v1.6 resume unblocked.**

## Sub-repo main HEAD SHAs

**Sub-repos NOT promoted to main per D-09.** Sub-repos remain at:
- `firestarter` beta @ `59a5e58` (operator-facing canonical doc + sub-repo README + CLAUDE.md sync rule from Plan 06)
- `firestarter_app` beta @ `00c19cd` (sub-repo README + CLAUDE.md sync rule extension from Plan 06)

Both `main` branches remain at their pre-v1.7 state (`firestarter` main @ `db4e565`, `firestarter_app` main @ `e6...` per pre-v1.7 state). Future stable promotion in a later milestone (likely bundled with v1.6 ship).

## Close commit pair SHAs

| Commit | SHA | Subject |
|--------|-----|---------|
| 1 (close) | `4252480` | `feat(v1.7): close milestone v1.7 — RURP Shield Hardware Investigation & Version Detection (MS-01)` |
| 2 (placeholder fill) | `3b1b841` | `docs(v1.7-close): fill MILESTONES.md <MILESTONE_CLOSE_COMMIT> placeholder with 4252480 (self-referential close-trail)` |

## Placeholders filled

| Placeholder | Locations | Replaced with |
|-------------|-----------|---------------|
| `2026-05-XX` (ship date) | PROJECT.md (3×), MILESTONES.md (3×), ROADMAP.md (4×), STATE.md (1×), v1.7-REQUIREMENTS.md (1×) — total 12 instances | `2026-05-26` |
| Commit counts (meta/firestarter/firestarter_app) | MILESTONES.md commits line | `108 / 144 / 109` (from `git log --oneline ^main \| wc -l` per repo) |
| `<MILESTONE_CLOSE_COMMIT>` | MILESTONES.md v1.7 entry closing line | `4252480` (the close commit's own short SHA — self-referential) |

Post-fill grep verification: `grep -c '2026-05-XX' .planning/PROJECT.md .planning/MILESTONES.md .planning/ROADMAP.md .planning/STATE.md .planning/milestones/v1.7-REQUIREMENTS.md` returns `0:0:0:0:0` (all 12 placeholders resolved). `grep -c 'MILESTONE_CLOSE_COMMIT' .planning/MILESTONES.md` returns `0`.

## v1.7 ship metric summary

| Metric | Value |
|--------|-------|
| Phases | 5 (numbered 31-35) |
| Plans | 33 (5+3+5+7+9 = 29 base + ~4 supplementary as the investigation surface evolved) |
| Requirements | 17/17 satisfied (HW-INV-01..03 + SILK-01 + DIFF-01/02 + CAPS-01/02 + ALIAS-01..03 + DETECT-HW-01/02 + DETECT-FW-01/02 + DOC-01 + MS-01) |
| Ship tag | `3.0.0b5` (both sub-repos via v1.4 lockstep) |
| Meta-repo commits | 108 (`v1.7-shield-investigation` branch) |
| firestarter sub-repo commits | 144 (beta @ 59a5e58) |
| firestarter_app sub-repo commits | 109 (beta @ 00c19cd) |
| Timeline | 2026-05-22 (planning start) → 2026-05-26 (execution close) |

## v1.6 resume hand-off

STATE.md "Operator Next Steps" cites `/gsd-plan-phase 27 --gaps` as the operator's immediate next action. Four substrate artifacts available for Phase 27 RCA re-open consumption:

1. **Labeled schematic:** `.planning/v1.7-SHIELD-REVS.md` §1 + §3 + §4
2. **Per-rev capability table:** `.planning/v1.7-SHIELD-REVS.md` §6
3. **Detect-fw substrate:** `REVISION_2_3` / `REVISION_UNKNOWN` enum + post-Plan-01 INPUT high-Z ADC band lookup + Phase 35 semantic correction (bands characterize A3-net composition, not R41 value)
4. **First disambiguation experiment** (Phase 29-02 SUMMARY hand-off): pre-Phase-28-firmware A/B test on `firestarter/v1.6-read-bug~2`

**Bonus capability:** operator's three boards stay connected via USB passthrough; Claude can drive firmware sideload + serial reads directly during v1.6 Phase 27 instrumented A/B builds (per `reference_usb_passthrough_bench` memory established during Phase 35 Wave 3).

## Note on v1.7-shield-investigation branch

The meta-repo `v1.7-shield-investigation` branch carries all v1.7 work including the close commits. It diverges from `main` (`main` is many commits behind; never merged the v1.7 series). Future cleanup: at v1.6 close, the operator can decide whether to:

- **Option A:** Merge `v1.7-shield-investigation` → `main` (preserves the v1.7 close commit chain on main)
- **Option B:** Leave `v1.7-shield-investigation` as a frozen archive branch (matches the v1.4 + v1.5 pattern where milestone-close work stayed on its dedicated branch)

Not blocking. v1.7 is shipped regardless.

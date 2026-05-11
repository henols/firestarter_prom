# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — Protocol-Aware Programming Architecture

**Shipped:** 2026-05-11
**Phases:** 13 | **Plans:** 22 | **Timeline:** 2026-05-08 → 2026-05-11 (4 days, 66 commits)

### What Was Built

- Algorithm-first wire protocol — `algorithm` integer (minipro `protocol_id`)
  flows authoritatively from upstream XML through DB, wire JSON, and into
  `memory.cpp::configure_memory` protocol-prefix dispatch for all 13 known
  protocols
- Five firmware handlers — `configure_eprom` (UV-EPROM), `configure_flash3`
  (AMD), `configure_flash_intel`, `configure_eeprom28c` (5V EEPROM with SDP
  + DQ7 polling), `configure_sram` (safe 5V no-op)
- Canonical database pipeline — single `build_db.py` fetches `infoic.xml`
  from upstream minipro at runtime; 743 chips across DIP24/28/32; legacy
  `parse_db.py` + stale artifacts removed
- Pre-write safety stack — VPP ADC compare (UV-EPROM + 28C paths), chip-ID
  validation, blank check
- Three close-out phases — Phase 11 (pipeline consolidation), Phase 12
  (BLOCKER-1 + BLOCKER-2 three-layer fix), Phase 13 (WARNING-5 data-layer
  override for 23 mis-tagged 5V EEPROMs)

### What Worked

- **Three-layer fixes for safety-critical bugs.** Phase 12 closed BLOCKER-1
  and BLOCKER-2 with parallel fixes in firmware (`configure_memory` dispatch),
  Python (`_ALGO_MEM_TYPE` table in `database.py`), and DB (`build_db.py`
  SRAM tagging). Defense-in-depth — any single layer regressing still leaves
  two correct.
- **Data-layer fix beats firmware switch.** Phase 13's WARNING-5 was tempting
  to fix as a per-chip firmware switch, but an inline 3-predicate override
  in `build_db.py` preserved the "algorithm is authoritative" contract while
  routing around an upstream minipro classification error. 23 chips fixed
  with zero firmware changes (AVR flash delta = 0 bytes).
- **Permanent regression guards.** Phase 12's `check_dispatch.py` SRAM guard
  and Phase 13's `_28C_EEPROM_HAZARD_PINOUT` guard are now load-bearing —
  any future upstream DB drift that re-introduces these hazards will fail
  CI before merge. Cheap to add, high-leverage protection.
- **Algorithm-first commit message convention.** The "BLOCKER closed at
  three layers" / "WARNING closed across three planes" framing in commit
  messages and SUMMARY frontmatter made cross-layer traceability trivial.
- **GSD audit-milestone before close.** The retrospective audit caught
  WARNING-5 as an active hazard introduced by Phase 12 (BLOCKER-1 had
  previously masked it). Without the audit it would have shipped as a
  hardware-damage path. Phase 13 inserted as a dedicated close-out phase.

### What Was Inefficient

- **Phases 01-10 shipped without formal VERIFICATION.md files.** The
  pattern of "VERIFICATION.md per phase" was not enforced until Phase 11.
  Independent verification via INTEGRATION-CHECK + `check_dispatch.py`
  caught the gaps post-hoc, but a retroactive `/gsd-validate-phase` pass
  is now backlog for v1.1.
- **Wire key naming drift.** `"vpp"` was originally volts, then quietly
  became millivolts in Phase 01 without a rename. The semantic overload
  surfaced in the v1.0 audit as WARNING-3 (`firestarter_app/CLAUDE.md`
  example shows a phantom `"vpp_mv"` key that is not emitted). Renaming
  wire keys mid-flight is harder than getting them right up front.
- **REQ-SAF-01 wording vs implementation.** "For every chip" was loose
  enough that the Intel-flash path shipped without VPP ADC compare. The
  UV-EPROM path satisfies it; the Intel-flash path (39 chips) does not.
  Either the requirement should have been tighter ("on every write
  pulse path that asserts VPP > 5V") or the audit-time check stricter.
- **Phase-level scope creep into "documentation" plans.** Phase 12 Plan 05
  and Phase 13 Plan 03 are dedicated documentation plans. They're correct
  in retrospect (CLAUDE.md drifted from the dispatch list), but the
  pattern of "every closing phase needs a doc-sync plan" is worth
  surfacing as an explicit phase template input rather than discovering
  it per phase.

### Patterns Established

- **Three-layer fix for safety-critical bugs.** When a bug crosses firmware /
  Python / DB pipeline, fix it in all three rather than picking one. Cheaper
  than the bug recurring when one layer regresses.
- **Inline override block + permanent regression guard.** Hard-coding an
  override is fine if (a) the predicates are pinned in a comment block
  referencing the audit entry, and (b) a regression guard in
  `check_dispatch.py` makes silent drift impossible.
- **Audit-then-close.** Run `/gsd-audit-milestone` before
  `/gsd-complete-milestone`. The audit caught WARNING-5 as an active
  hazard introduced by closing BLOCKER-1 — a class of regression that
  is invisible at phase-close time.
- **Submodule pointer-bumps in lockstep with planning commits.** Outer-repo
  tracks `.planning/` + sub-repo pointers only. Every code change in
  `firestarter_app/` or `firestarter/` produces a sub-repo commit + an
  outer-repo pointer-bump commit. SUMMARY.md frontmatter pins both SHAs.

### Key Lessons

1. **Algorithm-first beats type-first.** Replacing the lossy `type` byte
   with an explicit `algorithm` integer (minipro `protocol_id`) eliminated
   the entire class of "guess the type from secondary fields" bugs.
   `KNOWN_PROTOCOLS` is now a small, exhaustive, audit-able list.
2. **Closing a blocker can unmask a deeper hazard.** Phase 12 closed
   BLOCKER-1's "Memory type not supported" safe-exit, which had been
   silently protecting 23 AT28C-family 5V EEPROMs from receiving 12V on
   socket pin 1 = A14 during write. Always re-run the audit after a
   blocker is closed; the safe-failure mode you removed may have been
   load-bearing.
3. **Verification gaps are easy to skip on speed runs.** The 4-day
   timeline compressed VERIFICATION.md authoring out of Phases 01-10.
   The codebase is verifiably correct (INTEGRATION-CHECK + 743/743 chip
   dispatch scan) but the artifact gap is real workflow debt. Either
   enforce VERIFICATION.md as a per-phase blocker or accept the gap
   upfront and schedule retroactive validation.
4. **Permanent regression guards are cheap.** Both `check_dispatch.py`
   guards (SRAM, AT28C-hazard) are ~10 lines each and now block silent
   upstream-DB regressions forever. High leverage for trivial cost.

### Cost Observations

- Model mix: not measured this milestone (no telemetry pipeline configured)
- Sessions: not measured
- Notable: 13 phases / 22 plans in 4 calendar days suggests the workflow
  parallelism (multiple plans per phase, audit gates, code-review skill)
  scaled well at this granularity. The bottleneck was thinking time per
  audit decision, not execution time per plan.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Days | Key Change                                                |
| --------- | ------ | ----- | ---- | --------------------------------------------------------- |
| v1.0      | 13     | 22    | 4    | Initial — established algorithm-first, three-layer-fix, regression-guard patterns |

### Cumulative Quality

| Milestone | Verified Phases | Audit Status     | Hazard-Class E2E Flows |
| --------- | --------------- | ---------------- | ---------------------- |
| v1.0      | 3/13 formal (11, 12, 13) + 10 via INTEGRATION-CHECK | gaps_found (REQ-SAF-01 Intel-flash) | 0 (Phase 13 closed AT28C256) |

### Top Lessons (Verified Across Milestones)

1. Algorithm-first beats type-first (validated in v1.0 by 743-chip dispatch scan)
2. Three-layer fixes beat single-layer fixes for cross-cutting bugs (v1.0 BLOCKER-1, BLOCKER-2)
3. Audit-then-close — re-run the audit after closing a blocker to surface unmasked hazards (v1.0 WARNING-5 escalation)

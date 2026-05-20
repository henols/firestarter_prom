# Phase 22 Discussion Log

**Mode:** `/gsd-discuss-phase 22 --auto`
**Date:** 2026-05-20
**Pass count:** 1 (single-pass per auto-mode cap)

## Auto-resolved gray areas

The auto-mode flow identified six gray areas. Each was resolved using the recommended option (no AskUserQuestion calls; recommendations grounded in prior-phase context).

### 1. `default_envs` ordering literal
- **Question:** Should `default_envs` be `uno, uno328pb, leonardo` (matching `.ini` section order from Phase 21 D-08) or `uno, leonardo, uno328pb` (matching ROADMAP Phase 22 SC#1 current literal)?
- **Options surfaced:**
  - Recommended: `uno, uno328pb, leonardo` (section order; Phase 21 D-08 locks this)
  - Alternative: `uno, leonardo, uno328pb` (ROADMAP SC#1 current literal; older artifact)
- **Selection:** `uno, uno328pb, leonardo` (D-01 in CONTEXT.md)
- **Reason:** Phase 21 CONTEXT D-08 is the more recent locked decision; Phase 21 D-12 explicitly hands off the ROADMAP literal realignment to the Phase 22 planner.

### 2. ROADMAP SC#1 literal — own it here, or defer?
- **Question:** Should Phase 22 amend ROADMAP Phase 22 SC#1's `default_envs` literal inline, or defer to a future cleanup?
- **Options surfaced:**
  - Recommended: Amend inline alongside the `platformio.ini` edit (D-02)
  - Alternative: Defer (creates an inconsistency window between docs and code)
- **Selection:** Amend inline (D-02 in CONTEXT.md)
- **Reason:** Phase 21 D-12 said "planner for Phase 22 owns it OR plan-phase-21 amends ROADMAP inline" — Phase 21 deferred, so Phase 22 is the natural owner. Coupled with D-01 means both lines move in the same change-set.

### 3. CI workflow edit surface
- **Question:** Does Phase 22 need to edit `build.yml` and/or `beta-build.yml`?
- **Options surfaced:**
  - Recommended: No workflow edits — existing `files: .pio/build/**/firestarter_*.hex` glob already picks up the third hex (D-03)
  - Alternative: Enumerate per-board `files:` entries explicitly
- **Selection:** No edits (D-03 in CONTEXT.md)
- **Reason:** Verified by `grep -n "files:" firestarter/.github/workflows/*.yml` — both `build.yml:105` and `beta-build.yml:92` use the glob form. The glob is env-agnostic; `softprops/action-gh-release` will attach all three hex files once `pio run` produces them. SC#5 explicitly prohibits new mandatory CI checks; this option also avoids any net-new YAML.

### 4. GATE-01 byte-identity baseline reference
- **Question:** Where to source the GATE-01 reference artifacts for the `cmp -s` byte-identity check — re-fetch from the v1.4 `3.0.0b3` GitHub Release, or reuse Phase 21's local `.planning/v1.5/baselines/`?
- **Options surfaced:**
  - Recommended: Reuse `.planning/v1.5/baselines/` (D-05)
  - Alternative: Re-fetch from GitHub Release via `gh release download v3.0.0b3`
- **Selection:** Reuse Phase 21 baselines (D-05 in CONTEXT.md)
- **Reason:** Phase 21 baselines were captured at `firestarter/beta` tip `5fd751e` — which is the v1.4 ship state (per `.planning/STATE.md`). Same source SHA, same `version.h`, same artifact bytes. Avoids network dependency and matches the offline-reproducibility ethos of `CAPTURE-PROCEDURE.md`.

### 5. Verification gate scope — dry-run vs actual cut
- **Question:** Does Phase 22 verify by triggering an actual GitHub Release cut, or by running a local-matrix dry-run?
- **Options surfaced:**
  - Recommended: Local dry-run only — `pio run` (no `-e`), confirm all three `.hex` files produced + GATE-01 cmp -s + grep simulation of workflow glob (D-08)
  - Alternative: Trigger a real beta cut by pushing `v1.5-uno328pb` → `beta`
- **Selection:** Local dry-run (D-08 in CONTEXT.md)
- **Reason:** Phase 24 (Bench Validation) is the phase that performs the first real beta cut from `v1.5-uno328pb` → `firestarter/beta`. Phase 22's job is the CI-config substrate; it ships when the substrate is dry-run-verified. Pushing to remote `beta` from Phase 22 would also conflict with the branching convention captured in memory.

### 6. Phase 22 push semantics
- **Question:** Does Phase 22 push the `v1.5-uno328pb` branch to remote in either sub-repo or meta?
- **Options surfaced:**
  - Recommended: No push (D-09)
  - Alternative: Push the sub-repo branch as a remote backup
- **Selection:** No push (D-09 in CONTEXT.md)
- **Reason:** Consistent with the project branching convention (milestone work stays on `v1.5-uno328pb` locally until milestone close per memory `feedback-branching-firestarter-milestones`).

## Folded todos

None — `gsd-sdk query todo.match-phase 22` would surface any phase-22-tagged pending todos. No matches found in the meta-repo's `.planning/todos/pending/` (directory does not yet exist).

## Reviewed but not folded

None.

## Deferred ideas

All captured in CONTEXT.md `<deferred>` block:
- Stable release cut from `firestarter/main` (future milestone)
- First real beta pre-release cut (Phase 24)
- `workflow_dispatch` `beta_version` flag exercise (Phase 24 if needed)
- README updates mentioning third board's release artifacts (Phase 25)
- Adding `uno328pb` to `_flash_with_avrdude` table (Phase 23)

## Claude's discretion items

Three items left to the planner's judgment:
1. Whether to split into one plan or two (single-edit surface favors one plan)
2. Wording of the ROADMAP SC#1 amendment prose (must cite Phase 21 D-08 + D-12)
3. Whether to add a hex size/symbol assertion alongside `cmp -s` (defensive belt-and-braces; planner decides based on diff size)

## Scope creep redirected

None encountered — every recommended option stayed inside the Phase 22 boundary (release pipeline config + GATE-01 verification).

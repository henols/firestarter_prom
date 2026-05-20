# Phase 22: Release Pipeline Artifacts - Context

**Gathered:** 2026-05-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Land `firestarter_uno328pb.hex` as a third per-board release artifact on BOTH GitHub release surfaces (stable from `firestarter/main` via `build.yml`; beta pre-release from `firestarter/beta` via `beta-build.yml`) **without** altering the byte content of `firestarter_uno.hex` or `firestarter_leonardo.hex` (modulo version-string drift from `update_version.py`).

**What this phase does NOT do:**
- Cut an actual GitHub Release / Pre-release (Phase 24 owns the first real beta cut from `firestarter/beta` for bench validation; this phase ships when the local-matrix dry-run is green).
- Add new mandatory CI checks (ROADMAP SC#5 — existing catalog-validity + codegen-drift + native Unity + PIO build gates run unchanged).
- Touch the host CLI installer (Phase 23 owns INST-01..03 including the avrdude profile for `uno328pb`).

**Scope deviation from ROADMAP Phase 22 SC#1 literal:** SC#1 currently reads `default_envs = uno, leonardo, uno328pb`. Per Phase 21 CONTEXT D-08 (locked decision: `.ini` section order is `[env:uno] → [env:uno328pb] → [env:leonardo] → [env:native]`) and Phase 21 CONTEXT D-12 (HAND-OFF to Phase 22 planner), the actual `default_envs` literal this phase ships is `uno, uno328pb, leonardo` — matching the section order. ROADMAP SC#1 must be realigned inline alongside the `platformio.ini` edit. The planner owns both edits as a coupled change.

</domain>

<decisions>
## Implementation Decisions

### default_envs widening (the load-bearing edit)
- **D-01: `default_envs` literal = `uno, uno328pb, leonardo`** (matching D-08 section order from Phase 21, NOT the ROADMAP SC#1 current literal). Single-line edit on `firestarter/platformio.ini:16`: `default_envs = uno, leonardo` → `default_envs = uno, uno328pb, leonardo`.
- **D-02: ROADMAP Phase 22 SC#1 literal realignment** — amend the literal in `.planning/ROADMAP.md` (Phase 22 SC#1) from `uno, leonardo, uno328pb` to `uno, uno328pb, leonardo` in the same change-set as D-01. This resolves the Phase 21 D-12 hand-off in the natural owner. Cite Phase 21 D-08 + D-12 in the commit message and in the ROADMAP edit's prose.

### CI workflow edit surface (none — already compatible)
- **D-03: No `.github/workflows/*.yml` edits required.** Both `build.yml:105` and `beta-build.yml:92` already use the glob `files: .pio/build/**/firestarter_*.hex` (verified via grep on the v1.5-uno328pb branch tip). After `default_envs` widens, `pio run` produces all three `.hex` files at `.pio/build/{uno,uno328pb,leonardo}/firestarter_*.hex` and the glob captures all three. The `softprops/action-gh-release` glob is the single source of truth — no per-env enumeration needed.
- **D-04: No new mandatory CI checks** (ROADMAP SC#5). The existing catalog-validity + codegen-drift gate + native Unity (`pio test -e native`) + PIO build run unchanged. The `pio run` step is already env-agnostic — it picks up whatever `default_envs` lists. No matrix expansion, no per-env step duplication.

### GATE-01 byte-identity verification strategy
- **D-05: Baseline reference = Phase 21's `.planning/v1.5/baselines/`** (NOT a re-fetch from GitHub Releases for the v1.4 ship tag `3.0.0b3`). Rationale: Phase 21 captured `firestarter_uno.hex` + `firestarter_leonardo.hex` at `firestarter/beta` tip `5fd751e`, which IS the v1.4 ship state (per `.planning/STATE.md` "v1.4 SHIPPED 2026-05-20" + sub-repo HEAD on `beta`). The local baselines are byte-identical to the v1.4 ship tag artifacts (same source SHA, same `version.h` content); using them avoids a network round-trip to GitHub Releases and keeps verification reproducible offline.
- **D-06: GATE-01 verification command** — `cmp -s firestarter/.pio/build/uno/firestarter_uno.hex .planning/v1.5/baselines/firestarter_uno.hex` AND the leonardo equivalent. Both MUST exit 0 (a) BEFORE the `default_envs` edit is committed (sanity — proves the post-Phase-21 working tree is still GATE-1.5-clean), and (b) AFTER the edit (proves that widening `default_envs` did NOT perturb the two existing envs' build output). This is the same `cmp -s` pattern Phase 21 used; the planner reuses Phase 21's verification scaffolding verbatim.
- **D-07: Version-string drift handling** — REL-01/REL-02 acceptance language explicitly allows "byte-identical … modulo version-string drift from `update_version.py`". For Phase 22's local verification, `update_version.py` is NOT invoked (same Pitfall 3 discipline as Phase 21) — `include/version.h` stays unmodified at `3.0.0b2`, so `cmp -s` is a CLEAN match (not a "modulo version-string drift" match). The CI workflows DO invoke `update_version.py` before `pio run`, so the actual release-artifact byte-identity check against v1.4's `3.0.0b3` is the "modulo drift" form — but that's Phase 24's first-real-cut concern, not Phase 22's dry-run concern.

### Phase 22 verification gate (what "shipping Phase 22" means)
- **D-08: Verification = local-matrix dry-run + glob simulation, NOT an actual GitHub Release cut.** The verification step runs:
  1. `cd firestarter && pio run` (no `-e` flag — uses `default_envs`) — must exit 0 and produce all three `.hex` files
  2. `ls firestarter/.pio/build/**/firestarter_*.hex` — must list exactly three files (`firestarter_uno.hex`, `firestarter_uno328pb.hex`, `firestarter_leonardo.hex`)
  3. `cmp -s` against baselines (D-06)
  4. Static-analysis sanity on `build.yml:105` + `beta-build.yml:92` glob — confirm grep `firestarter_*.hex` resolves to the three filenames
  5. `pio test -e native` stays green (regression guard; D-04 said no new gates but the existing one MUST still pass)
- **D-09: Phase 22 does NOT push to remote.** No `git push origin v1.5-uno328pb` for either sub-repo. Operator handles remote-side cuts manually when v1.5 is ready to merge to `beta` (Phase 24 trigger). This is consistent with the existing project convention (v1.5-uno328pb is local-only per [[feedback-branching-firestarter-milestones]]).

### Edit surface summary
- **D-10: Phase 22 edits exactly 2 files:**
  - `firestarter/platformio.ini` (line 16) — sub-repo commit on `v1.5-uno328pb`
  - `.planning/ROADMAP.md` (Phase 22 SC#1) — meta-repo commit on `v1.5-uno328pb`
- **D-11: No edits to:** any `.github/workflows/*.yml`, any `firestarter/src/` file, any `firestarter/scripts/` file, `name_firmware.py`, `firestarter_app/**`. If the planner produces a plan that touches any of these, that's a planning defect — flag and reject.

### Claude's Discretion
- Whether to split into one plan or two (single-edit surface argues one plan; the planner picks).
- Wording of the ROADMAP SC#1 amendment prose (cite Phase 21 D-08 + D-12, keep it terse).
- Whether to add a `firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex` size/symbol assertion alongside the cmp -s gates (defensive belt-and-braces; planner decides based on diff size).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` lines 27-28 — REL-01 (stable) + REL-02 (beta) acceptance criteria, both anchored on the third `.hex` artifact landing AND existing two artifacts staying byte-identical per GATE-01.
- `.planning/REQUIREMENTS.md` GATE-01 row (lines 35-37, the "GATE" group) — non-regression contract for `firestarter_uno.hex` + `firestarter_leonardo.hex` across the v1.4→v1.5 boundary.

### Locked decisions from Phase 21 that govern Phase 22
- `.planning/phases/21-firmware-target-uno328pb/21-CONTEXT.md` **D-08** — `.ini` section order locks: `[env:uno] → [env:uno328pb] → [env:leonardo] → [env:native]`. `default_envs` literal must match this order.
- `.planning/phases/21-firmware-target-uno328pb/21-CONTEXT.md` **D-11** — Phase 21 hand-off to Phase 22: widen `default_envs` here, not earlier.
- `.planning/phases/21-firmware-target-uno328pb/21-CONTEXT.md` **D-12** — ROADMAP SC#1 literal realignment hand-off; explicit clause "planner for Phase 22 owns it OR plan-phase-21 amends ROADMAP inline" — Phase 21 deferred, so Phase 22 owns it.
- `.planning/phases/21-firmware-target-uno328pb/21-RESEARCH.md` Pitfall 3 — do NOT invoke `update_version.py` during local dry-run verification (it perturbs `.rodata` version-string region and breaks `cmp -s` against the unbumped baselines).

### Phase 21 verification scaffolding (reused verbatim)
- `.planning/v1.5/baselines/firestarter_uno.hex` (62,617 B, SHA-256 `0dd5c01a870de38e868bdc71cebd547cb65ed1d7573dc90678c99f7dc3a854d2`) — GATE-01 reference for uno.
- `.planning/v1.5/baselines/firestarter_leonardo.hex` (68,876 B, SHA-256 `f49e2a57a2ab8dad7224733d3e5f08f36df2d6aee4c4f924217a4d0c921fdc90`) — GATE-01 reference for leonardo.
- `.planning/v1.5/baselines/CAPTURE-PROCEDURE.md` — reproducible recipe; documents the "no `update_version.py`" invariant.

### Sub-repo edit targets
- `firestarter/platformio.ini` line 16 — `default_envs` line to widen. Section order (verified by grep) is `[env:uno]@31 → [env:uno328pb]@40 → [env:leonardo]@57 → [env:native]@67` after Phase 21's `ab7c2a9` commit on `v1.5-uno328pb`. Note: `firestarter/v1.5-uno328pb` branch — not `beta`.

### CI workflows (read-only references — NOT edited per D-03)
- `firestarter/.github/workflows/build.yml` line 105 — `files: .pio/build/**/firestarter_*.hex` glob (stable workflow Release step). Already compatible.
- `firestarter/.github/workflows/beta-build.yml` line 92 — same glob (beta workflow Pre-release step). Already compatible.

### Project / state
- `.planning/PROJECT.md` — GATE-01 + GATE-1.5 byte-identity invariants.
- `.planning/STATE.md` — v1.4 SHIPPED at `5fd751e` (= v1.4 ship tag `3.0.0b3` source SHA, the baseline anchor); v1.5 STARTED on operator branch `v1.5-uno328pb` in all three repos.
- `/workspaces/CLAUDE.md` — repo layout (meta tracks `.planning/`; firmware in `firestarter/` submodule).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **GATE-1.5 cmp -s pattern** (Phase 21 Plan 21-02 verification step): `cmp -s firestarter/.pio/build/{env}/firestarter_{env}.hex .planning/v1.5/baselines/firestarter_{env}.hex && exit 0 || exit 1`. Reuse verbatim for D-06's pre/post-edit checks.
- **`pio run` invocation pattern** (existing `build.yml` line ~70 and `beta-build.yml` line ~60): bare `pio run` with no `-e` flag — env-agnostic, picks up `default_envs`. No CI change needed.
- **Phase 21's `.planning/v1.5/baselines/CAPTURE-PROCEDURE.md`** — describes the canonical capture method. Phase 22's verification uses the captured artifacts (no re-capture needed).

### Established Patterns
- **Locked-step coordination** (Phase 15 milestone): meta-repo + sub-repo commits paired via shared milestone version. Phase 22's two-file edit (one per repo) maintains this — ROADMAP edit in meta-repo, `platformio.ini` edit in sub-repo, both on the matching `v1.5-uno328pb` branch.
- **`name_firmware.py` PROGNAME derivation** (Phase 21 D-06, sub-repo commit `da607d4`): PROGNAME = `firestarter_${RURP_BOARD_NAME}`. For `[env:uno328pb]`, `RURP_BOARD_NAME = "uno328pb"`, so the built hex is `firestarter_uno328pb.hex` — exactly what the workflow glob picks up. No `name_firmware.py` change for Phase 22.

### Integration Points
- **Stable release surface (GitHub Release for `firestarter/main`)** — `build.yml` Release step. Phase 22 does NOT trigger a stable cut (no `firestarter/main` push planned in this milestone). Actual stable verification happens in a future milestone when `v1.5-uno328pb` merges to `firestarter/beta` → `firestarter/main`.
- **Beta release surface (GitHub Pre-release for `firestarter/beta`)** — `beta-build.yml` Release step. Phase 22 does NOT trigger a beta cut (sub-repo work stays on `v1.5-uno328pb`, not `beta`). First real beta cut is Phase 24 (Bench Validation), which merges `v1.5-uno328pb` to `firestarter/beta` to trigger `beta-build.yml`.

</code_context>

<specifics>
## Specific Ideas

- The verification gate is **identical in shape** to Phase 21's verification gate (build all envs, `cmp -s` against baselines, `pio test -e native`). The only delta is that Phase 22 invokes `pio run` (no `-e` flag) instead of `pio run -e uno -e leonardo -e uno328pb` — and the success condition is that all three `.hex` files are produced from a single env-flag-less invocation.
- Single canonical reference for "where the third hex must appear": `softprops/action-gh-release@v1` `with.files` glob, both workflow files, line 105 (stable) + line 92 (beta). This is the line the planner should grep on as the proof-by-existence that no workflow YAML change is needed.

</specifics>

<deferred>
## Deferred Ideas

- **Stable release cut from `firestarter/main`** — Phase 22 does not produce one. Deferred to a future milestone (post-v1.5 merge-up), or to manual operator action when v1.5 is promoted from `beta` to `main`.
- **First real beta pre-release cut** — Phase 24 (Bench Validation) triggers this by merging `v1.5-uno328pb` → `firestarter/beta`. Phase 22 ships when the dry-run is green.
- **`workflow_dispatch` `beta_version` flag exercise for v1.5** — exists in `beta-build.yml` since v1.4 (PEP 440 input), but Phase 22 does not exercise it. Phase 24 may use it if auto-increment-from-tags resolves to the wrong base.
- **A README update mentioning the third board's release artifacts** — Phase 25 (Documentation + Milestone Close) owns DOC-01/DOC-02.
- **Adding `uno328pb` to `firestarter_app`'s `_flash_with_avrdude` table** — Phase 23 (Host CLI Installer Integration) owns INST-01.

</deferred>

---

*Phase: 22-release-pipeline-artifacts*
*Context gathered: 2026-05-20 via /gsd-discuss-phase --auto (auto-mode single-pass; recommended options applied)*
*Auto-resolved gray areas: default_envs ordering (D-01, per Phase 21 D-08), ROADMAP SC#1 realignment ownership (D-02, per Phase 21 D-12), CI workflow edit surface (D-03, glob already compatible), GATE-01 baseline reference (D-05, reuse Phase 21 captures), verification scope (D-08, local dry-run not actual cut), branch convention (D-09, no remote push from Phase 22)*

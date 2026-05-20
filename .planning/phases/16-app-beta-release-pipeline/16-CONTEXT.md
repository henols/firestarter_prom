# Phase 16: App Beta Release Pipeline - Context

**Gathered:** 2026-05-20
**Status:** Ready for planning
**Discussion mode:** `--auto --chain` (autonomous recommended-option selection)

<domain>
## Phase Boundary

`firestarter_app/` ships a new GitHub Actions workflow that handles the publisher side of the beta channel for the app. A push to the `beta` branch (or a manual `workflow_dispatch` invocation) triggers: CI gates (codegen drift + catalog validity + pytest), version bump via Phase 15's extended `update_version.py` in beta mode, auto-commit back to the `beta` branch, GitHub Release with `prerelease: true` + `make_latest: false`, and PyPI publish (via the existing `publish.yml` which fires on `release: published` for any release including prereleases). The existing `release.yml` / `publish.yml` / `ci.yml` workflows stay BYTE-IDENTICAL — GATE-01 non-regression.

**In scope (Phase 16):**
- New workflow file: `firestarter_app/.github/workflows/beta-release.yml`. Self-contained (matches `release.yml` pattern): triggers on `push: branches: [beta]` AND `workflow_dispatch` with optional `beta_version` input.
- Inline CI gates inside `beta-release.yml` (codegen drift via `tools/catalog/codegen.py --check` + drift gate via `git diff --exit-code firestarter/messages.py` + pytest) BEFORE the version bump — fail-stop semantics mirror `release.yml`'s gate ordering from v1.2 Phase 6 WR-05.
- `update_version.py` invocation receives `BETA_VERSION` env var from `workflow_dispatch.inputs.beta_version` OR falls back to git-tag-scan when invoked from a bare `push: beta` (Phase 15 D-08).
- `stefanzweifel/git-auto-commit-action@v5` commits the version bump back to the `beta` branch (mirrors `release.yml` exactly — same action, same parameters).
- `softprops/action-gh-release@v2` creates the GitHub Release with `prerelease: true` + `make_latest: false` + `tag_name: ${{ steps.version.outputs.version }}`.
- GATE-01 verification: `git -C firestarter_app diff` over `release.yml` / `publish.yml` / `ci.yml` shows zero changes after Phase 16 lands.

**Out of scope (Phase 16):**
- Firmware beta pipeline (Phase 17).
- Branch protection rules on the `beta` branch (Future Requirements per REQUIREMENTS.md).
- Auto-promotion beta → stable (deferred to v1.5+).
- Modifying `publish.yml` (verified: GitHub `release: published` event fires for prereleases too; PyPI's `gh-action-pypi-publish` accepts PEP 440 pre-release versions natively).
- Modifying `ci.yml` (its `branches: [main]` trigger is correct as-is — beta PRs against main are still caught; beta-release.yml is self-sufficient).

</domain>

<decisions>
## Implementation Decisions

### A. Workflow File Shape

- **D-01:** Create a NEW workflow file `firestarter_app/.github/workflows/beta-release.yml`. Do NOT modify `release.yml`. Stable byte-identity (GATE-01) is verified by `git diff release.yml publish.yml ci.yml` returning empty after the Phase 16 PR.
- **D-02:** Naming: `beta-release.yml`. Job name `github` (mirrors `release.yml`); workflow display name `Create a new beta pre-release`. Step names follow `release.yml`'s wording where they're shared (`Checkout`, `Create new patch release` → `Create new pre-release version`, `Commit updated version`, `Release`).

### B. Triggers

- **D-03:** Triggers in `beta-release.yml`:
  ```yaml
  on:
    push:
      branches: [beta]
      paths-ignore: [same list as release.yml]
    workflow_dispatch:
      inputs:
        beta_version:
          description: 'Explicit PEP 440 pre-release version (e.g. 3.1.0b1). Leave blank for auto-increment via git-tag scan.'
          required: false
          type: string
  ```
- **D-04:** `paths-ignore` list MUST byte-match `release.yml`'s list (`**.md`, `**.sh`, `.gitignore`, `docs/**`, `images/**`, `.github/**`, `.vscode/**`, `tools/**`). Same ignore set keeps trigger semantics consistent across stable + beta.
- **D-05:** `workflow_dispatch` is the canonical lockstep-cut mechanism per Phase 15 D-01. The release engineer runs `gh workflow run beta-release.yml --ref beta -f beta_version=3.1.0b1` from BOTH repos to coordinate.
- **D-06:** `push: branches: [beta]` is the convenience trigger for local iteration / non-lockstep beta cuts; the auto-increment fallback from Phase 15 D-08 (git-tag scan) emits `b(N+1)` automatically.

### C. CI Gate Placement (mirrors release.yml's v1.2 WR-05 ordering)

- **D-07:** All CI gates run INLINE in `beta-release.yml` BEFORE the version bump (mirrors `release.yml`'s post-WR-05 ordering rationale: gates are read-only and must veto the version bump + release publish if they fail; ordering matches firmware's `build.yml` for cross-repo symmetry).
- **D-08:** Gate sequence:
  1. `actions/checkout@v4`
  2. `actions/setup-python@v5` with `python-version: '3.11'`
  3. Catalog validity check: `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check`
  4. Codegen drift gate: regenerate `firestarter/messages.py` and `git diff --exit-code firestarter/messages.py`
  5. Install package + dev deps: `pip install -e .[dev]`
  6. Run pytest: `pytest tests/ -v`
  7. (Steps 3–6 are the existing `ci.yml` job copied inline so beta-release.yml is self-sufficient; do NOT call `ci.yml` as a reusable workflow yet — adds complexity without scope-fit benefit for v1.4.)
- **D-09:** Version-bump + release steps run AFTER gates pass:
  7. `Create new pre-release version`: `.github/scripts/update_version.py` invoked with `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}` and `GITHUB_REF` auto-set by GitHub Actions to `refs/heads/beta`.
  8. `Commit updated version`: `stefanzweifel/git-auto-commit-action@v5` (no parameter overrides — defaults match release.yml's usage).
  9. `Release`: `softprops/action-gh-release@v2` with `tag_name: ${{ steps.version.outputs.version }}`, `prerelease: true`, `make_latest: false`, `token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}`.

### D. publish.yml Integration

- **D-10:** `publish.yml` is NOT modified. It triggers on `release: published` — GitHub fires this event for BOTH stable and prerelease GH Releases. The PyPI publish action (`pypa/gh-action-pypi-publish@release/v1`) accepts PEP 440 pre-release versions natively (`X.Y.ZbN` → installable via `pip install --pre firestarter==X.Y.ZbN`). Verified by Phase 15 RESEARCH.md PEP 440 section.
- **D-11:** Consequence: after `beta-release.yml` creates the GH Release, `publish.yml` automatically picks it up via the `release: published` event hook and publishes the wheel/sdist to PyPI. Zero new workflow plumbing for the PyPI side.

### E. `BETA_VERSION` Sourcing

- **D-12:** When `workflow_dispatch` is the trigger AND `inputs.beta_version` is non-empty: pass through to `update_version.py` via `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}`. Phase 15 D-07 handles the verbatim write.
- **D-13:** When trigger is `push: branches: [beta]` (or `workflow_dispatch` without `beta_version`): `BETA_VERSION` env stays unset → Phase 15 D-08 auto-increment kicks in (git-tag scan for highest `bN` matching current base version, emits `b(N+1)`).
- **D-14:** `update_version.py` requires `fetch-depth: 0` on the checkout step so the git-tag scan can see all tags. Phase 15 RESEARCH.md Pitfall #5 documented this. Add `with: fetch-depth: 0` to the `actions/checkout@v4` step.

### F. Tag Namespace

- **D-15:** Stable tags (`X.Y.Z`) and beta tags (`X.Y.ZbN`) share the same Git tag namespace. PEP 440 ordering keeps them sortable; GitHub treats them as independent refs. No tag prefix (`v`, `beta-`, etc.) — Phase 15 D-21 regex anchored on the bare version string.

### G. Auto-Commit Back to Beta

- **D-16:** `stefanzweifel/git-auto-commit-action@v5` commits the version bump back to the `beta` branch. Configuration mirrors `release.yml` exactly — no `commit_message`, no `branch`, no `file_pattern` overrides; the action defaults are correct (commits all modified files with auto-generated message back to the current branch which is `beta` since the workflow checked out `refs/heads/beta`).
- **D-17:** The auto-commit creates a small commit churn on the `beta` branch (one commit per release). This is expected and matches stable's behavior on `main`.

### H. Permissions

- **D-18:** Job permissions: `permissions: contents: write` — matches `release.yml` exactly. Required for both git-auto-commit (push to beta branch) and softprops/action-gh-release (create GH Release).
- **D-19:** Personal access token: reuse `secrets.PERSONAL_ACCESS_TOKEN` (already configured in the repo per release.yml line 43). No new secret required.

### I. ci.yml — Do NOT Modify

- **D-20:** `ci.yml` stays byte-identical. Its triggers (`branches: [main]` for push + PR) are correct: beta PRs that target main (e.g. promotion PR) still trigger ci.yml; beta-direct pushes are handled by beta-release.yml's inline gates.
- **D-21:** Trade-off acknowledged: beta-branch pushes do NOT run `ci.yml`'s pytest in addition to `beta-release.yml`'s pytest — they're the SAME pytest invocation. Duplicate runs would be wasteful. The inline approach also matches `release.yml`'s self-contained pattern (release.yml runs gates inline; ci.yml is for PR validation only).

### J. GATE-01 Verification

- **D-22:** Phase 16 verification asserts:
  1. `git -C firestarter_app diff HEAD~N -- .github/workflows/release.yml` returns empty (release.yml unchanged across the Phase 16 commit range).
  2. Same for `publish.yml` and `ci.yml`.
  3. The new `beta-release.yml` is the ONLY workflow file added (verified via `git -C firestarter_app status`).
- **D-23:** A separate non-regression assertion: pushing a fixture commit to a throwaway branch off `main` and running `gh workflow run release.yml` (or `workflow_dispatch` if added) produces the same release tag pattern + asset shape as today. NOT in Phase 16 scope to actually run this — but the assertion is documented as a Phase 20 E2E-01 spot-check (`pip install firestarter` of pre-Phase-18 stable version line still resolves to the latest stable tag).

### Claude's Discretion

- **D-24:** Exact YAML quoting style and indentation — planner picks per project convention (2-space indent, single-quoted strings throughout `release.yml`).
- **D-25:** Whether to add `concurrency` group to prevent simultaneous beta cuts — recommended NO for v1.4 (one cut at a time is the procedural expectation; adding `concurrency` is unnecessary complexity). Planner may add if a clear use case emerges.
- **D-26:** Whether to surface the resolved `BETA_VERSION` in the workflow_dispatch summary UI — recommended yes via a final step `echo` (cheap, audit-friendly). Planner picks output format.
- **D-27:** Whether to include the `paths-ignore` block at all — planner can drop it if the `beta` branch is intended to fire on every change including doc-only edits. Recommended: keep `paths-ignore` byte-matching `release.yml` (consistency).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents (gsd-phase-researcher, gsd-planner) MUST read these before planning or implementing.**

### Milestone planning artifacts
- `.planning/PROJECT.md` — Project overview; current milestone v1.4 scope.
- `.planning/REQUIREMENTS.md` §REL (REL-01) + §GATE (GATE-01) — acceptance criteria for this phase.
- `.planning/ROADMAP.md` §"Phase 16: App Beta Release Pipeline" — goal, success criteria, dependencies.
- `.planning/STATE.md` §"v1.4 Decisions" — locked decisions including the 2026-05-20 amendment.

### Phase 15 deliverables (load-bearing — Phase 16 consumes verbatim)
- `firestarter_app/.github/scripts/update_version.py` — extended with `BETA_VERSION` env + `--beta` CLI flag + git-tag-scan fallback + PEP 440 regex validation + GITHUB_OUTPUT guard. Phase 16's `beta-release.yml` invokes this script with `GITHUB_REF=refs/heads/beta` auto-set.
- `.planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md` — operator procedure. Phase 16's release engineer uses this when cutting a beta.
- `.planning/phases/15-versioning-locked-step-coordination-foundation/15-RESEARCH.md` Pitfall #5 — `fetch-depth: 0` requirement for tag-scan.

### Existing workflows (read-only; must remain byte-identical per GATE-01)
- `firestarter_app/.github/workflows/release.yml` — Stable release trigger. Phase 16 MUST NOT modify this file. It's also the structural template for `beta-release.yml`.
- `firestarter_app/.github/workflows/publish.yml` — PyPI publish on `release: published`. Phase 16 does NOT modify; D-10 confirms it handles prereleases natively.
- `firestarter_app/.github/workflows/ci.yml` — Host CI. Phase 16 does NOT modify; D-20 explains why.

### Files to create
- `firestarter_app/.github/workflows/beta-release.yml` — THE primary deliverable. Structure mirrors `release.yml` with `beta` branch trigger + `prerelease: true` + `make_latest: false` + inline CI gates from `ci.yml` + `workflow_dispatch` input for explicit `BETA_VERSION`.

### External specs
- GitHub Actions `workflow_dispatch` inputs: https://docs.github.com/en/actions/reference/events-that-trigger-workflows#workflow_dispatch — for the `beta_version` input shape.
- GitHub Actions `paths-ignore`: https://docs.github.com/en/actions/reference/events-that-trigger-workflows#using-filters — for matching `release.yml`'s ignore list.
- `softprops/action-gh-release@v2` README — for `prerelease` + `make_latest` parameters.
- `stefanzweifel/git-auto-commit-action@v5` README — for default behavior on the auto-commit step.
- `pypa/gh-action-pypi-publish@release/v1` README — confirms PEP 440 prerelease support.
- GitHub `release: published` event semantics — fires for both stable and prerelease releases.

### Phase 17 / 18 / 19 / 20 handoff contract
- Phase 17 (Firmware Beta Pipeline) mirrors Phase 16's structure but for the firmware sub-repo. Phase 16's `beta-release.yml` is the structural template for Phase 17's analogous workflow.
- Phase 18 (Beta-Aware Firmware Downloader) shipped 2026-05-20 — its `firestarter fw -i --pre` path consumes Phase 17's published prerelease firmware. Phase 16 only ships the APP side; no direct interaction with the firmware downloader.
- Phase 19 (Documentation) documents the operator workflow including the `gh workflow run beta-release.yml --ref beta -f beta_version=X.Y.ZbN` command shape.
- Phase 20 (E2E + Close) E2E-01 (a)+(b) consume Phase 16's deliverables: real beta cut produces PyPI-installable `X.Y.ZbN`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`firestarter_app/.github/workflows/release.yml`** — Structural template for `beta-release.yml`. Both workflows have the same skeleton: trigger → checkout → run update_version.py → auto-commit → softprops/action-gh-release. Differences are: trigger branch (`main` vs `beta`), `make_latest` flag (true vs false), `prerelease` flag (absent/false vs true), additional `workflow_dispatch` trigger with `beta_version` input.
- **`firestarter_app/.github/workflows/ci.yml`** — Source of the inline CI gate steps (catalog validity check, codegen drift gate, pip install, pytest). Phase 16 copies these step-for-step into `beta-release.yml` (NOT a reusable-workflow call — D-08 rationale).
- **`firestarter_app/.github/scripts/update_version.py`** — Extended by Phase 15. Phase 16's workflow invokes it without modification; the script handles beta-context detection via `GITHUB_REF` + `BETA_VERSION` env.

### Established Patterns

- **Self-contained workflow** (release.yml pattern): each workflow runs its own gates inline rather than depending on other workflows via `workflow_run` or reusable workflows. Reduces coupling; mirrors firmware's `build.yml` style.
- **`stefanzweifel/git-auto-commit-action@v5` for version-bump commits** — established by release.yml line 33; matches firmware build.yml line 87.
- **`softprops/action-gh-release@v2` for GitHub Release creation** — established by release.yml line 38; matches firmware build.yml line 97. For beta, flip `make_latest: false` and add `prerelease: true`.
- **`secrets.PERSONAL_ACCESS_TOKEN`** — established in release.yml line 43 for the GH Release step. Reused in beta-release.yml.
- **`paths-ignore` blocks** — established in release.yml (lines 4-14). Byte-match in beta-release.yml.
- **`fetch-depth: 0` for tag-aware scripts** — required by Phase 15's git-tag-scan fallback. Add to checkout step.

### Integration Points

- **`release.yml` and `beta-release.yml` are siblings** — they coexist; one fires on `main`, the other on `beta`. No mutual interference because branch triggers are disjoint.
- **`publish.yml` consumes both** — its `release: published` trigger fires regardless of whether the release came from `release.yml` or `beta-release.yml`. PyPI version uniqueness is enforced by the version string (`X.Y.Z` vs `X.Y.ZbN` never collide).
- **`actions/checkout@v4` token scope** — default `GITHUB_TOKEN` has `contents: read` by default; the workflow's `permissions: contents: write` block at job level grants write access for the auto-commit step. release.yml uses this pattern.

</code_context>

<specifics>
## Specific Ideas

- **Operator's release-engineer workflow** (locked at Phase 15 D-01): release engineer runs `gh workflow run beta-release.yml --ref beta -f beta_version=3.1.0b1` from BOTH `firestarter_app/` AND `firestarter/` (Phase 17's analogue). Both repos pick up the same `BETA_VERSION` env, produce matching `X.Y.ZbN` strings, and create lockstep beta releases. Phase 18's downloader then picks up the firmware via `firestarter fw -i --pre` or `firestarter fw -i --firmware-version 3.1.0b1`.
- **CI duplication concern** — beta-release.yml runs catalog validity + codegen drift + pytest inline. ci.yml runs the SAME gates on push/PR to main. They never both fire on the same commit (disjoint branch triggers), so no actual duplication at runtime. The DUPLICATION is in workflow source code: if the gate sequence ever changes, both files must be updated. Acceptable trade-off for v1.4; reusable workflows can be considered in v1.5+ if maintenance becomes painful.
- **`paths-ignore` matters for branch hygiene** — `release.yml` has it; without `paths-ignore`, doc-only changes pushed to `beta` would trigger a (pointless) beta release. Keep the same list.

</specifics>

<deferred>
## Deferred Ideas

- **Reusable workflow extraction** — turning the catalog/codegen/pytest gates into a `.github/workflows/_ci-gates.yml` callable workflow that both `ci.yml` and `beta-release.yml` invoke. Reduces duplication; adds workflow-dependency complexity. Defer to v1.5+ if maintenance burden materializes.
- **`concurrency` group** to prevent simultaneous beta cuts (D-25) — see Future Requirements; not load-bearing.
- **Branch protection rules** on the `beta` branch — see Future Requirements in REQUIREMENTS.md.
- **TestPyPI publishing channel** — explicitly rejected for v1.4 per STATE.md.
- **Auto-promotion beta → stable workflow** — deferred per REQUIREMENTS.md Future Requirements.
- **Beta build for forks / PRs** — beta-release.yml only fires on push to the canonical `beta` branch and on workflow_dispatch from the repo. Fork PRs don't trigger it (intentional — beta cuts are operator-initiated).

</deferred>

---

*Phase: 16-app-beta-release-pipeline*
*Context gathered: 2026-05-20*
*Discussion mode: --auto --chain (autonomous recommended-option selection)*

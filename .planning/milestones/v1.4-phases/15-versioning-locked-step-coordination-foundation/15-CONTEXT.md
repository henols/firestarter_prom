# Phase 15: Versioning & Locked-Step Coordination (Foundation) - Context

**Gathered:** 2026-05-20
**Status:** Ready for planning
**Discussion mode:** `--auto --chain` (autonomous selection of recommended options; chain to plan-phase)

<domain>
## Phase Boundary

Both sub-repos (`firestarter_app/` and `firestarter/`) ship an extended
`update_version.py` that emits PEP 440 pre-release identifiers (`X.Y.ZbN` /
`X.Y.ZrcN`) when invoked under a beta-branch context AND preserves the existing
stable-branch behavior byte-identically. A locked-step coordination procedure
is finalized: when cutting a beta, the release engineer supplies an explicit
`BETA_VERSION` input (workflow_dispatch / env var) that BOTH repos receive,
guaranteeing matching version strings without any new shared infrastructure
(no meta-repo VERSION file, no cross-repo `repository_dispatch` PAT).

**In scope:**
- Extend `firestarter_app/.github/scripts/update_version.py` to detect beta context and emit `X.Y.ZbN` / `X.Y.ZrcN`.
- Extend `firestarter/.github/scripts/update_version.py` symmetrically (same trigger contract, same output format).
- Both scripts: stable-branch path remains byte-identical to today (regression-free per GATE-01/02 derivative).
- Both scripts: extended regex so they can READ a `X.Y.ZbN`/`X.Y.ZrcN` back from the version file (current `[0-9\.]+` regex cannot).
- pytest unit tests for both scripts (stable path + beta path + dry-run); `--dry-run` flag with golden-file diff for CI smoke verification.
- Phase-local artifact documenting the lockstep coordination procedure (consumed verbatim by Phase 18's `v1.4-RELEASE-PROCEDURES.md`).

**Out of scope (for Phase 15):**
- Adding the actual `beta`-branch GitHub Actions workflows (Phases 16 + 17 own this).
- Cleanup of existing `2.0.7_dev` / `3.0.0-dev` suffix asymmetry between repos (lockstep applies to beta cuts, not retroactive stable realignment).
- TestPyPI publishing, signed artifacts, branch protection rules (deferred per REQUIREMENTS.md Future Requirements).

</domain>

<decisions>
## Implementation Decisions

### A. Lockstep Coordination Mechanism (load-bearing — VER-03)

- **D-01:** Coordination mechanism = **manually-paired beta-branch push with an explicit `BETA_VERSION` input**. Release engineer chooses the version string (e.g. `3.1.0b1`), supplies it as `workflow_dispatch` input (or env var) to BOTH repos' beta workflows, and pushes both `beta` branches. Both `update_version.py` invocations receive the same string verbatim and write it into their respective version files.
- **D-02:** Rejected alternatives + reasons:
  - **Shared `VERSION` file in meta-repo** — would require sub-repos' workflows to checkout + write to the meta-repo, adding cross-repo write-token auth and a commit dependency. Doesn't fit "additive plumbing + docs only" scope.
  - **Cross-repo `repository_dispatch` trigger** — would require a PAT with `repo` scope on both sub-repos, plus brittle event-payload contract. Tighter coupling than the milestone needs.
  - Procedural lockstep (paired push) is the lightest-weight option compatible with the existing per-repo independent-auto-bump pattern.
- **D-03:** Lockstep is enforced at WRITE TIME via explicit operator input, not via shared state. Drift recovery: if one repo's beta build fails and the other succeeds, the operator re-triggers the failed repo with the same `BETA_VERSION` (idempotent re-publish would require a separate fix — not in v1.4 scope; documented as a known gap in Phase 18 procedure docs).

### B. Beta-Branch Context Detection

- **D-04:** Primary detection = read `GITHUB_REF` env var from GitHub Actions context. When `GITHUB_REF == "refs/heads/beta"` → beta mode; anything else → stable mode (existing behavior).
- **D-05:** Secondary trigger = `--beta` CLI flag accepted by `update_version.py` for local development / test invocation outside CI. CLI flag wins when set (allows `pytest` fixtures to exercise the beta path without monkeypatching env vars).
- **D-06:** Tertiary input = `BETA_VERSION` env var (set by `workflow_dispatch` input from the lockstep coordination per D-01). When present in beta mode, used verbatim; when absent, fall back to D-08 git-tag scan.

### C. Beta Version Identifier Computation

- **D-07:** Beta mode accepts an explicit `BETA_VERSION` env var → used VERBATIM (PEP 440 format-validated, then written into the version file). This is the LOCKSTEP-cut path — what the release engineer supplies, what both repos publish.
- **D-08:** When `BETA_VERSION` is absent in beta mode (local dev / testing), the script falls back to: scan existing git tags in the current repo for the highest `X.Y.Z(b|rc)N` matching the current base version, emit `b(N+1)` (or `b1` if no prior beta tag exists on this base). NOT used for production lockstep cuts — release engineer always supplies `BETA_VERSION` explicitly.
- **D-09:** First-beta-of-a-line resets to `b1`. Subsequent betas on the same `X.Y.Z` base increment monotonically (`b2`, `b3`, …). Promotion to `rcN` is a separate operator decision — set `BETA_VERSION=X.Y.ZrcN` explicitly.

### D. Beta Version State Storage

- **D-10:** Beta versions are written into the SAME files as stable:
  - App: `firestarter_app/firestarter/__init__.py` → `__version__ = "X.Y.ZbN"`
  - Firmware: `firestarter/include/version.h` → `#define VERSION "X.Y.ZbN"`
- **D-11:** Branch isolation handles state separation: `beta`-branch checkouts carry beta version strings; `main`-branch checkouts carry stable version strings. No new state files.

### E. Test Framework / Dry-Run Affordance (per Phase 15 SC#4)

- **D-12:** Both scripts get pytest unit tests covering: (a) stable-branch path (no env vars set → asserts patch increment, byte-identical to today's output for a fixed input); (b) beta-branch path with `BETA_VERSION` set (asserts the supplied string is written verbatim); (c) beta-branch path without `BETA_VERSION` (asserts git-tag-scan fallback emits `bN+1`); (d) `--dry-run` flag (asserts no file modification + version emitted to stdout / `GITHUB_OUTPUT`).
- **D-13:** Both scripts get a `--dry-run` flag: computes the proposed next version without modifying the version file or writing to `GITHUB_OUTPUT`. Emits the proposed version to stdout. Used in CI smoke-test and in Phase 19 E2E lockstep verification.
- **D-14:** App-side test framework = pytest (already in `firestarter_app/tests/`); fixture under `firestarter_app/tests/test_update_version.py`. Firmware-side test framework = pytest as well (firmware sub-repo's `update_version.py` is Python; minimal pytest infra added under `firestarter/tests/` or `firestarter/.github/scripts/tests/`). PlatformIO native + Unity not used here (Unity targets C++; this is a Python script).
- **D-15:** Tests run in CI on PRs to either sub-repo before the v1.4 plumbing lands in mainline (per Phase 15 SC#4). For the app, the test is added to the existing pytest job in `ci.yml`. For the firmware, a new lightweight Python test job is added to `build.yml` (or a separate workflow) that runs `pytest .github/scripts/tests/` before the existing PlatformIO build.

### F. Stable Code-Path Preservation (GATE-01/02 derivative)

- **D-16:** `update_version.py` is **extended in-place** in each sub-repo (single file per repo). No script split, no new files. The new beta logic is a guarded code branch entered ONLY when `GITHUB_REF == "refs/heads/beta"` (or `--beta` flag set, or `BETA_VERSION` env var set). Default branch path is identical to today.
- **D-17:** Stable-branch invocation MUST produce byte-identical output to the pre-v1.4 script for the same input. Verified by pytest fixture (D-12 stable case) + a manual diff check during Phase 15 plan execution: run the new script with `BETA_VERSION` unset, `GITHUB_REF=refs/heads/main`, on the current `__init__.py` / `version.h`, and confirm the resulting file diff matches the old script's output exactly (modulo the `Version file updated:` log line if that wording changes — the file write must be byte-identical).

### G. Initial Lockstep Version Reconciliation

- **D-18:** App is currently at `2.0.7_dev` (in `__init__.py`); firmware is at `3.0.0-dev` (in `include/version.h`). These DO NOT currently match. Lockstep in v1.4 applies to **beta cuts specifically**, not retroactive stable realignment.
- **D-19:** First v1.4 beta cut: release engineer chooses a coordinated `BETA_VERSION` (likely something like `3.1.0b1` or `0.0.1b1` per the REQUIREMENTS.md E2E-01 "test identifier that doesn't conflict with the current version line" guidance). The exact starting value is a Phase 19 decision (not Phase 15); Phase 15 just guarantees the script can WRITE whatever the operator supplies.
- **D-20:** Stable continues to auto-bump independently per repo (existing behavior preserved). Drift between stable versions across repos is a known acceptable state — lockstep is a property of BETA RELEASES, not of stable releases.

### H. PEP 440 Segment Coverage

- **D-21:** Supported segments: `bN` (beta) and `rcN` (release candidate). Both scripts validate `BETA_VERSION` against the regex `^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$`. Invalid input fails the script with a clear error before any file modification.
- **D-22:** Out of scope: `aN` (alpha), `devN` (development), `postN` (post-release), `+local` (local version identifiers). No business case for v1.4; can be added in a future milestone if needed.

### I. Regex Extension for Suffix Readback

- **D-23:** Both scripts' version-parsing regex MUST be extended to capture PEP 440 pre-release suffixes so that a beta-branch script invocation can read back a previously-written `X.Y.ZbN` from the version file. Today's `[0-9\.]+` truncates suffixes silently (causes existing `2.0.7_dev` / `3.0.0-dev` to be misread as `2.0.7` / `3.0.0`).
- **D-24:** New parse regex captures `(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)(?P<pre>(b|rc)[0-9]+)?` — three numeric components + optional pre-release suffix. Stable-mode write strips the suffix (so a stable bump from `3.1.0b3` would write `3.1.1` — but in practice this won't happen because stable runs on `main` which carries no beta suffix; documenting for completeness).
- **D-25:** Existing `_dev` / `-dev` suffixes in the version files are silently truncated by both old and new regex. This is the current production behavior and is preserved. Cleaning up dev-suffix conventions is OUT OF SCOPE for Phase 15 — fold into a future cleanup if needed.

### Claude's Discretion

- **D-26:** Procedure-document filename in the phase folder: planner picks a name (e.g. `15-LOCKSTEP-PROCEDURE.md`) — must be consumable verbatim by Phase 18's `v1.4-RELEASE-PROCEDURES.md` as either a copy-in or an authoritative reference.
- **D-27:** Exact pytest fixture structure (parametrize vs. per-test functions, conftest.py vs inline) — planner picks per sub-repo conventions. App side already has pytest patterns under `firestarter_app/tests/`; firmware side establishes a minimal new pattern.
- **D-28:** `--dry-run` flag's exact output format (JSON vs key=value vs plain string) — planner picks; constraint is that the output is greppable for the version string by a CI smoke test.
- **D-29:** Whether to add a CLI `--set-version X.Y.ZbN` arg in addition to the `BETA_VERSION` env var (functional duplicate; convenience). Recommendation: yes, but planner decides if it's worth the extra arg-parsing surface.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents (gsd-phase-researcher, gsd-planner) MUST read these before planning or implementing.**

### Milestone planning artifacts
- `.planning/PROJECT.md` — Project overview; current milestone v1.4 scope.
- `.planning/REQUIREMENTS.md` §VER — VER-01, VER-02, VER-03 (acceptance criteria for this phase).
- `.planning/ROADMAP.md` §"Phase 15: Versioning & Locked-Step Coordination (Foundation)" — phase goal, success criteria, dependencies.
- `.planning/STATE.md` §"v1.4 Decisions" — locked-at-milestone-start decisions (branch-driven beta, PEP 440, lockstep).

### Existing sub-repo scripts (extend in place)
- `firestarter_app/.github/scripts/update_version.py` — App version-bump script. Currently 60 lines; reads `firestarter/__init__.py`, regex `[0-9\.]+` (cannot parse PEP 440 suffixes — D-23 fix), writes back, emits to `$GITHUB_OUTPUT`. Extend to detect beta context (D-04..D-06), emit `X.Y.ZbN` (D-07..D-09), preserve stable path byte-identically (D-16, D-17).
- `firestarter/.github/scripts/update_version.py` — Firmware version-bump script. Currently 63 lines; reads `include/version.h`, regex `[0-9\.]+`, writes back, emits to `$GITHUB_OUTPUT`. Same extension shape as the app's. Format MUST be identical to the app's (PEP 440 `X.Y.ZbN`) so lockstep comparison is string-equality (per REQUIREMENTS.md VER-02).

### Existing CI workflows (read-only reference — Phases 16 + 17 modify; Phase 15 doesn't)
- `firestarter_app/.github/workflows/release.yml` — Stable trigger (push to main → run `update_version.py` → git-auto-commit → GitHub Release `make_latest: true`). v1.4 stable path must remain byte-identical (GATE-01).
- `firestarter_app/.github/workflows/publish.yml` — PyPI publish on `release: published` event (already works for stable; will publish beta versions too once they fire the `release: published` event with `prerelease: true`).
- `firestarter_app/.github/workflows/ci.yml` — Host CI (codegen drift + catalog validity + pytest). The new pytest tests for `update_version.py` (D-12, D-15) land in this workflow's existing pytest run.
- `firestarter/.github/workflows/build.yml` — Firmware CI + release (catalog validity, codegen drift, native Unity tests, version bump, PlatformIO build, GitHub Release `make_latest: true`). Stable path must remain byte-identical (GATE-02).

### Version source files (writes target these)
- `firestarter_app/firestarter/__init__.py` — App version source. Today: `__version__ = "2.0.7_dev"`.
- `firestarter/include/version.h` — Firmware version source. Today: `#define VERSION "3.0.0-dev"`.

### External specs
- PEP 440 (https://peps.python.org/pep-0440/) — Python version-identifier spec. Pre-release segment format: `(a|b|rc)N`. Required for `pip install --pre firestarter==X.Y.ZbN` to resolve correctly (REL-01 acceptance).

### Phase 18 contract
- The lockstep coordination procedure documented in Phase 15's phase-local artifact (D-26) is consumed verbatim by Phase 18's `.planning/v1.4-RELEASE-PROCEDURES.md` (DOC-03). Phase 15 docs and Phase 18 docs are tied — when Phase 15 finalizes the procedure, Phase 18 imports it. Researcher and planner should treat the procedure artifact as a deliverable that downstream phases CONSUME.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`firestarter_app/.github/scripts/update_version.py`** — App version-bump. Self-contained Python script; reads / writes one file; emits to `$GITHUB_OUTPUT`. Clean extension point: add a beta-branch check after `get_version()` returns the parsed tuple, branch on `GITHUB_REF` env var, route to either `calculate_version()` (stable, today's behavior) or a new `calculate_beta_version(BETA_VERSION_input)` function.
- **`firestarter/.github/scripts/update_version.py`** — Firmware version-bump. Near-identical structure to the app's. Same extension shape applies. Format string differs slightly (`#define VERSION "X.Y.Z"` vs `__version__ = "X.Y.Z"`) but the parse + write helpers are isomorphic.
- **`firestarter_app/tests/`** — App pytest infrastructure already in place (29 tests passing per v1.2 close). Adding `test_update_version.py` here is a natural extension.
- **`firestarter_app/.github/workflows/ci.yml`** — Host CI already runs pytest on PRs and main pushes. New tests run for free in this workflow.
- **`firestarter/.github/workflows/build.yml`** — Firmware CI already runs native Unity tests via `pio test -e native`. Adding a Python pytest run for `update_version.py` requires a new step (e.g. before the existing PlatformIO build).

### Established Patterns

- **GitHub Actions env-var-driven config**: existing scripts read `GITHUB_OUTPUT` to emit values back to the workflow. Pattern extension: read `GITHUB_REF` for branch detection (D-04), read `BETA_VERSION` for explicit lockstep input (D-06, D-07).
- **`stefanzweifel/git-auto-commit-action@v5`**: used by both stable release workflows to commit the bumped version back to the source branch. Pattern carries to beta (used by Phases 16 + 17, not Phase 15).
- **`softprops/action-gh-release@v2`**: used by both stable release workflows. For beta, the `prerelease: true` + `make_latest: false` flags are flipped (Phases 16 + 17, not Phase 15).
- **`pypa/gh-action-pypi-publish@release/v1`**: used by app's `publish.yml`. PyPI accepts pre-release versions automatically; `pip install --pre` opt-in lives client-side (REL-01 acceptance).
- **Catalog-validity / codegen-drift / native-Unity gates BEFORE version bump in firmware `build.yml`** (added in v1.2 Phase 6 WR-05): Phase 17 inherits this pattern for beta — gates fail-stop BEFORE any version bump or release artifact is produced. Phase 15 doesn't touch this directly but planner should be aware.
- **Codegen drift gate via `git diff --exit-code <generated-file>`**: used in both `ci.yml` (messages.py) and `build.yml` (messages.h). The `--dry-run` flag for `update_version.py` (D-13) could optionally use a similar pattern — emit expected version, diff against actual.

### Integration Points

- **`GITHUB_REF` env var** — auto-populated by GitHub Actions on every workflow run. Reading it requires zero workflow-yaml changes. Value on `beta` branch push = `refs/heads/beta`; on main = `refs/heads/main`.
- **`GITHUB_OUTPUT` env var** — already used by both scripts. New beta path appends `version=X.Y.ZbN` to the same output channel; Phases 16 + 17 read this value via `${{ steps.version.outputs.version }}` (mirrors existing stable pattern).
- **`workflow_dispatch` inputs** (NEW for beta) — Phases 16 + 17 will declare a `BETA_VERSION` input on their beta workflow files; the workflow passes it through to `update_version.py` as an env var. Phase 15's script just needs to read the env var; the workflow plumbing is Phases 16 + 17.
- **`pyproject.toml` `dynamic = ["version"]`** — App `pyproject.toml` declares version as dynamic (via `setuptools_scm`). However, in practice the version published to PyPI comes from `__version__` in `__init__.py` (the `update_version.py` script writes this file directly). The dynamic-version + setuptools_scm setup is a vestige; current behavior is direct-file driven. Planner should verify which mechanism actually sources the version at publish time (RESEARCH item for the researcher agent).

</code_context>

<specifics>
## Specific Ideas

- **The load-bearing decision (D-01) is the lockstep mechanism.** This was explicitly flagged in ROADMAP.md Phase 15 Structural Notes and REQUIREMENTS.md VER-03 as "the load-bearing planning decision for the milestone's first phase". The auto-selected answer is "manually-paired beta-branch push with explicit `BETA_VERSION` input". If the planner discovers this option is infeasible (e.g. workflow_dispatch input cannot be set via push trigger — likely will require both `push:` and `workflow_dispatch:` triggers on the beta workflows), the planner has authority to revisit during research; flag as a deviation for operator confirmation.
- **Subtle gotcha discovered during scout (D-25)**: current `update_version.py` regex `[0-9\.]+` silently truncates existing `_dev` / `-dev` suffixes. So both repos' current dev versions (`2.0.7_dev`, `3.0.0-dev`) would be silently rewritten as `2.0.8` / `3.0.1` on the next stable bump — independent of v1.4 work. This is pre-existing behavior, NOT a v1.4 regression to fix. Planner should NOT touch this; just preserve.
- **App + firmware version asymmetry today (D-18..D-20)**: 2.0.7_dev vs 3.0.0-dev. Lockstep applies to beta releases, not retroactive stable realignment. The first beta cut sets a coordinated version; subsequent stable cuts continue independently.

</specifics>

<deferred>
## Deferred Ideas

- **Auto-promotion workflow beta → stable** — explicitly deferred per REQUIREMENTS.md Future Requirements. Mentioned in Phase 18 DOC-03 as a known gap with a manual promotion path (fast-forward merge from `beta` to `main`).
- **Branch protection rules on `beta` branch** — optional safety net, not load-bearing. Add post-v1.4 if accidental-push problems materialize.
- **Signed release artifacts** (sigstore / GPG) — out of scope for v1.4; would be a dedicated milestone covering both stable and beta artifacts together.
- **Cleanup of `_dev` / `-dev` dev-suffix convention** (D-25) — current scripts silently truncate; not in v1.4 scope. Fold into a future cleanup if a version-format unification milestone happens.
- **`aN` / `devN` / `postN` PEP 440 segment support** (D-22) — only `bN` and `rcN` are in v1.4 scope. Easy to add later if needed.
- **TestPyPI publishing channel** — see REQUIREMENTS.md Future Requirements; rejected for v1.4 (PyPI `--pre` is the cleaner UX).
- **Idempotent beta re-publish on partial failure** (D-03) — if one repo's beta publish fails after the other succeeded, recovery requires manual re-trigger. A robust idempotent re-publish would need separate design work; documented as a known gap in Phase 18 procedure docs.

</deferred>

---

*Phase: 15-versioning-locked-step-coordination-foundation*
*Context gathered: 2026-05-20*
*Discussion mode: --auto --chain (autonomous recommended-option selection)*

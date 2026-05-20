# Phase 16: App Beta Release Pipeline — Research

**Researched:** 2026-05-20
**Domain:** GitHub Actions workflow authoring (YAML), softprops/action-gh-release v2, stefanzweifel/git-auto-commit-action v5, pypa/gh-action-pypi-publish, PEP 440 prerelease semantics
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Create a NEW file `firestarter_app/.github/workflows/beta-release.yml`. Do NOT modify `release.yml`, `publish.yml`, or `ci.yml`. Stable byte-identity (GATE-01) verified by `git diff` returning empty after the Phase 16 PR.
- **D-02:** Naming: `beta-release.yml`. Job name `github` (mirrors `release.yml`). Workflow display name `Create a new beta pre-release`. Step names follow `release.yml` wording where shared.
- **D-03:** Triggers: `push: branches: [beta]` + `paths-ignore` (same list as release.yml) + `workflow_dispatch: inputs: beta_version: (required: false, type: string)`.
- **D-04:** `paths-ignore` MUST byte-match `release.yml`'s list: `**.md`, `**.sh`, `.gitignore`, `docs/**`, `images/**`, `.github/**`, `.vscode/**`, `tools/**`.
- **D-05:** `workflow_dispatch` is the canonical lockstep-cut mechanism per Phase 15 D-01. Release engineer runs `gh workflow run beta-release.yml --ref beta -f beta_version=3.1.0b1`.
- **D-06:** `push: branches: [beta]` is the convenience trigger for local iteration; git-tag-scan fallback (Phase 15 D-08) emits `b(N+1)` automatically.
- **D-07:** All CI gates run INLINE in `beta-release.yml` BEFORE the version bump.
- **D-08:** Gate sequence: checkout (fetch-depth:0) → setup-python 3.11 → catalog validity check → codegen drift gate → pip install -e .[dev] → pytest → version bump → auto-commit → release.
- **D-09:** Version-bump step: `update_version.py` with `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}`. Release step: `softprops/action-gh-release@v2` with `tag_name: ${{ steps.version.outputs.version }}`, `prerelease: true`, `make_latest: false`, `token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}`.
- **D-10:** `publish.yml` is NOT modified. It fires on `release: published` — which covers both stable and prerelease GH Releases natively.
- **D-11:** After `beta-release.yml` creates the GH Release, `publish.yml` picks it up automatically via `release: published`. Zero new workflow plumbing for PyPI.
- **D-12:** When `workflow_dispatch` with non-empty `beta_version`: pass through as `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}`.
- **D-13:** When trigger is `push: branches: [beta]` OR `workflow_dispatch` without `beta_version`: `BETA_VERSION` env stays empty string → Phase 15 git-tag-scan fallback activates.
- **D-14:** `fetch-depth: 0` REQUIRED on `actions/checkout@v4` for git-tag-scan fallback (Phase 15 Pitfall #7).
- **D-15:** Stable tags (`X.Y.Z`) and beta tags (`X.Y.ZbN`) share the same Git tag namespace. No prefix.
- **D-16:** `stefanzweifel/git-auto-commit-action@v5` with NO parameter overrides. Defaults are correct.
- **D-17:** Auto-commit creates one commit per release on `beta`. Expected; matches stable's behavior on `main`.
- **D-18:** Job permissions: `permissions: contents: write` — matches `release.yml` exactly.
- **D-19:** Reuse `secrets.PERSONAL_ACCESS_TOKEN`. No new secret required.
- **D-20:** `ci.yml` stays byte-identical. Its triggers are correct as-is.
- **D-21:** No duplicate CI runs: beta-branch pushes fire `beta-release.yml` only; `ci.yml` fires on push/PR to `main` only. Disjoint triggers.
- **D-22:** Phase 16 verification: `git -C firestarter_app diff HEAD~N -- .github/workflows/release.yml` returns empty. Same for `publish.yml` and `ci.yml`. `beta-release.yml` is the ONLY new workflow file.

### Claude's Discretion

- **D-24:** Exact YAML quoting style and indentation — 2-space indent, single-quoted strings per project convention.
- **D-25:** No `concurrency` group for v1.4 (one cut at a time is the procedural expectation).
- **D-26:** Surface resolved `BETA_VERSION` in workflow summary via a final `echo` step (cheap, audit-friendly).
- **D-27:** Keep `paths-ignore` byte-matching `release.yml` (consistency; prevents doc-only pushes to `beta` from triggering pointless releases).

### Deferred Ideas (OUT OF SCOPE)

- Reusable workflow extraction (`.github/workflows/_ci-gates.yml`).
- `concurrency` group.
- Branch protection rules on `beta`.
- TestPyPI publishing.
- Auto-promotion beta → stable.
- Beta build for forks / PRs.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-01 | Push to `firestarter_app/beta` triggers workflow: runs CI, bumps pre-release version, creates GitHub Release with `prerelease: true` + `make_latest: false`, publishes to PyPI as `X.Y.ZbN` installable via `pip install --pre firestarter` | §Standard Stack, §Implementation Approach (full YAML), §Technical Finding 1–6 |
| GATE-01 | After v1.4 lands, push to `firestarter_app/main` still produces GitHub Release with `make_latest: true`, non-pre-release PyPI publish, `__version__` auto-bumped to next patch. No new mandatory CI checks on stable path. | §Technical Finding 7 (GATE-01 verification), §Pitfall 7 |
</phase_requirements>

---

## Summary

Phase 16 delivers exactly one new file: `firestarter_app/.github/workflows/beta-release.yml`. The file's structure mirrors `release.yml` (the structural template) with these additions: a second trigger (`workflow_dispatch` with optional `beta_version` input), inline CI gates copied from `ci.yml` before the version bump, and `prerelease: true` + `make_latest: false` on the release step.

The research confirms all key technical questions that were flagged in CONTEXT.md. The most critical finding is the auto-commit loop non-issue: `release.yml` uses default `GITHUB_TOKEN` for the `git-auto-commit-action` step (the PAT is commented out in the release step, not the auto-commit step), and GitHub explicitly prevents GITHUB_TOKEN-triggered pushes from re-firing push-event workflows. `beta-release.yml` mirrors this pattern exactly — no `token:` override on the checkout step, no `GITHUB_TOKEN` env override on the auto-commit step — so the auto-commit to `beta` does NOT re-trigger the workflow.

The second critical finding: `github.event.inputs.beta_version` evaluates to empty string (not null/undefined) when the workflow is triggered by a `push:` event. Passing `BETA_VERSION: ${{ github.event.inputs.beta_version }}` on a push-triggered run passes an empty string env var, which Phase 15's `compute_beta_version()` treats as "unset" and falls through to git-tag-scan. This is the correct behavior per D-13.

**Primary recommendation:** Write `beta-release.yml` as a verbatim structural mirror of `release.yml` with four targeted additions: `workflow_dispatch` trigger + CI gate steps (from `ci.yml`) + `prerelease: true` + `make_latest: false`. No other modifications to any existing file.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| CI gates (catalog validity, codegen drift, pytest) | CI Workflow (beta-release.yml) | — | Inline copy from ci.yml; gates are read-only and must veto version bump if they fail (D-07) |
| Pre-release version computation | CI Script (update_version.py) | — | Phase 15 deliverable; workflow passes env vars, script computes and writes |
| Git auto-commit of version bump | CI Workflow (git-auto-commit-action@v5) | — | Established pattern from release.yml; uses default GITHUB_TOKEN to avoid re-trigger loop |
| GitHub Release creation (prerelease: true) | CI Workflow (softprops/action-gh-release@v2) | — | Established action; `prerelease: true` + `make_latest: false` for beta |
| PyPI publish of pre-release wheel | publish.yml (unchanged) | — | Existing workflow fires on `release: published` for ALL releases including prereleases; no modification needed |
| Operator lockstep coordination | Manual (release engineer) | workflow_dispatch input | Phase 15 D-01: explicitly-supplied BETA_VERSION to both repos |
| GATE-01 regression verification | CI (git diff assertion) | — | D-22: `git diff` over release.yml / publish.yml / ci.yml returns empty after Phase 16 PR |

---

## Standard Stack

### Core (all pre-existing in firestarter_app; no new deps)

| Action | Version | Purpose | Why Standard |
|--------|---------|---------|--------------|
| `actions/checkout` | v4 | Repository checkout with full tag history | Already used in all app workflows |
| `actions/setup-python` | v5 | Python 3.11 environment | Already used in ci.yml (line 29) |
| `stefanzweifel/git-auto-commit-action` | v5 | Auto-commit version bump back to beta branch | Already used in release.yml (line 33) |
| `softprops/action-gh-release` | v2 | Create GitHub Release with prerelease: true + make_latest: false | Already used in release.yml (line 38); v2 confirms `make_latest` support |
| `pypa/gh-action-pypi-publish` | release/v1 | PyPI publish (via publish.yml — unchanged) | Already used; accepts PEP 440 pre-release versions natively |

**No new actions and no new secrets are required.** All five actions are already pinned in existing workflows.

### Version Notes

`softprops/action-gh-release@v2` is the current major version. The `make_latest` parameter was introduced in v2. `release.yml` already pins `@v2`, confirming the feature is available in the project's pinned version. [VERIFIED: /workspaces/firestarter_app/.github/workflows/release.yml line 38]

---

## Architecture Patterns

### System Architecture Diagram

```
Operator pushes to beta branch  OR  gh workflow run beta-release.yml --ref beta -f beta_version=X.Y.ZbN
                │
                ▼
beta-release.yml fires (push: branches:[beta] OR workflow_dispatch)
                │
        ┌───────▼────────────────────────────────┐
        │  GATE SEQUENCE (fail-stop)             │
        │  1. actions/checkout@v4                │
        │     with: fetch-depth: 0              │
        │  2. actions/setup-python@v5 (3.11)    │
        │  3. catalog validity check            │
        │     (codegen.py --check)              │
        │  4. codegen drift gate                │
        │     (regen + git diff --exit-code)    │
        │  5. pip install -e .[dev]             │
        │  6. pytest tests/ -v                  │
        └───────────────────────────────────────┘
                │ ALL GATES GREEN
                ▼
        VERSION BUMP
        update_version.py
          env: GITHUB_REF = refs/heads/beta     (auto-set by runner)
          env: BETA_VERSION = ${{ github.event.inputs.beta_version }}
                                                 (empty string on push trigger → git-tag-scan)
          writes firestarter/__init__.py
          outputs: steps.version.outputs.version = X.Y.ZbN
                │
                ▼
        AUTO-COMMIT (GITHUB_TOKEN — does NOT re-trigger push workflows)
        stefanzweifel/git-auto-commit-action@v5
          pushes to beta branch
                │
                ▼
        GITHUB RELEASE
        softprops/action-gh-release@v2
          tag_name: X.Y.ZbN
          prerelease: true
          make_latest: false       ← beta never becomes "Latest"
          token: secrets.PERSONAL_ACCESS_TOKEN
                │
                ▼ release: published event fires
        publish.yml (UNCHANGED) picks up
          pypa/gh-action-pypi-publish@release/v1
          publishes wheel + sdist to PyPI as X.Y.ZbN
          ↓
        pip install --pre firestarter==X.Y.ZbN  ← consumer opt-in
```

### Recommended Project Structure

```
firestarter_app/
└── .github/
    └── workflows/
        ├── ci.yml              # UNCHANGED (push/PR to main)
        ├── release.yml         # UNCHANGED (push to main → stable release)
        ├── publish.yml         # UNCHANGED (release: published → PyPI)
        └── beta-release.yml    # NEW (push to beta OR workflow_dispatch → beta release)
```

No other files change in Phase 16.

---

## Implementation Approach: Complete YAML for beta-release.yml

The following is the full recommended YAML. This is derived directly from:
1. `release.yml` (structural template) [VERIFIED: read directly]
2. `ci.yml` (gate steps, copied inline) [VERIFIED: read directly]
3. Phase 15 contract (env var shape, fetch-depth requirement) [VERIFIED: 15-LOCKSTEP-PROCEDURE.md]
4. D-01 through D-27 (locked decisions in CONTEXT.md)

```yaml
name: Create a new beta pre-release
on:
  push:
    branches:
    - beta
    paths-ignore:
    - '**.md'
    - '**.sh'
    - '.gitignore'
    - 'docs/**'
    - 'images/**'
    - '.github/**'
    - '.vscode/**'
    - 'tools/**'
  workflow_dispatch:
    inputs:
      beta_version:
        description: 'Explicit PEP 440 pre-release version (e.g. 3.1.0b1). Leave blank for auto-increment via git-tag scan.'
        required: false
        type: string

jobs:
  github:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Catalog validity check
        run: python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check

      - name: Codegen drift gate (messages.py)
        run: |
          python3 tools/catalog/codegen.py \
            --catalog tools/catalog/messages.toml \
            --target firestarter/messages.py \
            --language python
          git diff --exit-code firestarter/messages.py

      - name: Install package + dev deps
        run: pip install -e .[dev]

      - name: Run pytest
        run: pytest tests/ -v

      - name: Create new pre-release version
        id: version
        env:
          BETA_VERSION: ${{ github.event.inputs.beta_version }}
        run: .github/scripts/update_version.py

      - name: Commit updated version
        uses: stefanzweifel/git-auto-commit-action@v5

      - name: Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ steps.version.outputs.version }}
          prerelease: true
          make_latest: false
        env:
          GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
```

**Design notes on the YAML above:**

1. `GITHUB_REF` is NOT manually set in the version-bump step's `env:`. GitHub Actions automatically provides `GITHUB_REF` as an environment variable on every run — no explicit injection is needed. Phase 15's `is_beta_mode()` reads `os.environ.get("GITHUB_REF")` and will see `refs/heads/beta` automatically. [VERIFIED: GitHub Actions env var docs; Finding 2 in Phase 15 RESEARCH.md]

2. `BETA_VERSION: ${{ github.event.inputs.beta_version }}` passes the workflow_dispatch input. On a push trigger, `github.event.inputs.beta_version` evaluates to empty string (not null). Phase 15's `compute_beta_version()` treats empty string as "unset" and falls back to git-tag-scan. This is correct behavior per D-13. [VERIFIED: GitHub community discussion #29242 — "inputs context is unavailable [on push], which evaluates to an empty string"]

3. No `token:` override on the `Checkout` step and no `GITHUB_TOKEN` env on the `Commit updated version` step. This mirrors `release.yml` exactly. The auto-commit action uses the default `GITHUB_TOKEN`, which GitHub prevents from re-triggering push-event workflows. See Pitfall 1 below.

4. The `paths-ignore` block is ONLY under the `push:` trigger, not under `workflow_dispatch:`. This is correct: `paths-ignore` applies exclusively to push and pull_request events, and GitHub ignores it silently if placed under `workflow_dispatch`. Including it under the push trigger prevents doc-only commits to `beta` from spuriously triggering a beta release.

5. `permissions: contents: write` is at the JOB level (not workflow level), matching `release.yml` exactly. This grants both the `git-auto-commit-action` step (needs push to branch) and `softprops/action-gh-release` (needs create release) their required permissions. [VERIFIED: release.yml line 19-20]

---

## Key Technical Findings

### Finding 1: `workflow_dispatch.inputs` YAML Shape

[VERIFIED: GitHub Actions workflow syntax docs; confirmed by 15-LOCKSTEP-PROCEDURE.md canonical example]

Canonical YAML for an optional string input:

```yaml
workflow_dispatch:
  inputs:
    beta_version:
      description: 'Explicit PEP 440 pre-release version (e.g. 3.1.0b1). Leave blank for auto-increment via git-tag scan.'
      required: false
      type: string
```

- `required: false` — input is optional; omitting it in the UI or CLI is allowed.
- `type: string` — freeform text input; appears as a text box in the GitHub Actions UI.
- No `default:` field needed; the absence of a value evaluates to empty string, not null, which is what Phase 15's `compute_beta_version()` expects for the git-tag-scan fallback.
- Accessed in the job via `${{ github.event.inputs.beta_version }}`. The alternate accessor `${{ inputs.beta_version }}` is also valid in newer Actions syntax.
- CLI invocation: `gh workflow run beta-release.yml --ref beta -f beta_version=3.1.0b1` (flag is `-f`, input name matches YAML key).

### Finding 2: `github.event.inputs.beta_version` on Push vs. workflow_dispatch Triggers

[VERIFIED: GitHub community discussion #29242 — "inputs context is unavailable [on push], which evaluates to an empty string"]

When the workflow fires from a `push: branches: [beta]` event (not `workflow_dispatch`):
- `github.event.inputs` context is absent / the push event has no inputs.
- `${{ github.event.inputs.beta_version }}` evaluates to **empty string `''`** (not null, not undefined, not `'null'`).
- Passing `BETA_VERSION: ${{ github.event.inputs.beta_version }}` in the version-bump step's `env:` sets `BETA_VERSION=''` in the process environment.
- Python's `os.environ.get("BETA_VERSION", "").strip()` returns `''` — falsy in the `if explicit:` check.
- Therefore `compute_beta_version()` falls through to the git-tag-scan fallback. This is the desired behavior per D-13.

**Consequence:** The single `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}` expression correctly handles both trigger paths without conditional logic. No `if:` guard or `${{ github.event_name == 'workflow_dispatch' && ... || '' }}` expression is needed.

### Finding 3: `softprops/action-gh-release@v2` — `prerelease: true` + `make_latest: false`

[VERIFIED: GitHub REST API docs — "Latest release is the most recent non-prerelease, non-draft release"]
[VERIFIED: WebSearch — "Drafts and prereleases cannot be set as latest. The API returns: 'Latest release cannot be draft or prerelease'"]

Key facts:

1. **`prerelease: true` and `make_latest: false` are fully compatible.** There is no conflict. `make_latest: false` is belt-and-suspenders: it explicitly instructs the action not to attempt marking this release as latest. Setting `prerelease: true` alone already achieves this (the GitHub API refuses to mark a prerelease as latest), but the explicit `make_latest: false` is clearer.

2. **`make_latest: false` is required (not just defensive) in v2.** In `softprops/action-gh-release@v2`, if `make_latest` is omitted the action defers to GitHub API defaults, which for prereleases means "do not set as latest." However, explicitly setting `make_latest: false` is the correct signal and matches the CONTEXT.md specification precisely.

3. **`api.github.com/repos/.../releases/latest` automatically excludes prereleases.** The `/releases/latest` endpoint returns the most recent non-prerelease, non-draft release. A beta release tagged `X.Y.ZbN` with `prerelease: true` will never appear at `/releases/latest`. This is why `firestarter --install` (no flags) in stable-installed apps continues to download stable firmware without any code change — the endpoint contract guarantees it.

4. **GitHub UI hides prerelease releases from the default "Releases" view.** The default Releases page shows only non-prerelease releases. Prereleases are visible on the full releases list (with a "Pre-release" badge) but not on the default view. This is correct, expected UX for the beta channel.

5. **`tag_name: ${{ steps.version.outputs.version }}`** — the tag value comes from `update_version.py`'s `GITHUB_OUTPUT` write (`version=X.Y.ZbN`). `softprops/action-gh-release@v2` creates the git tag at this name AND creates the GH Release pointing to it. [VERIFIED: release.yml uses identical pattern at line 40]

### Finding 4: `stefanzweifel/git-auto-commit-action@v5` — No Infinite Loop

[VERIFIED: stefanzweifel/git-auto-commit-action README — "events triggered by GITHUB_TOKEN will not create a new workflow run"]
[VERIFIED: release.yml — Checkout step has no `token:` parameter; git-auto-commit step has PAT commented out]

The critical question: does the auto-commit to `beta` re-trigger `beta-release.yml`?

**Answer: NO**, when using the default GITHUB_TOKEN, and that is exactly what `release.yml` does today (and `beta-release.yml` will mirror).

Mechanism:
- `actions/checkout@v4` with no `token:` parameter uses the default `GITHUB_TOKEN` to configure git credentials.
- `stefanzweifel/git-auto-commit-action@v5` with no parameters inherits these credentials for its push.
- GitHub's infrastructure explicitly prevents GITHUB_TOKEN-authenticated pushes from triggering new workflow runs on the same repository. This is the documented anti-recursion guard.
- The `release.yml` proof: `release.yml` fires on `push: branches: [main]`, auto-commits a version bump back to `main`, and does NOT loop. Same mechanism will apply to `beta-release.yml`.

**If a PAT were used instead** (e.g., `actions/checkout@v4 with: token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}`), the auto-commit WOULD re-trigger the workflow, causing an infinite loop. DO NOT add `token:` to the Checkout step. `release.yml` does not have it; `beta-release.yml` must not have it either.

**The commented-out PAT in `release.yml`** (lines 34-35: `# env: GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}`) is correctly commented out. The PAT on the `Release` step (line 43) is for creating GitHub Releases via the API, not for push authentication — that scope does not affect the auto-commit re-trigger behavior.

### Finding 5: `pypa/gh-action-pypi-publish@release/v1` on PEP 440 Prereleases

[VERIFIED: Phase 15 RESEARCH.md Finding 1 — "pip install --pre exposes pre-releases; pip install firestarter (without --pre) will never install a bN/rcN build"]
[VERIFIED: publish.yml — action used at line 15; no config changes in publish.yml for this phase]

Key facts:
- PyPI accepts PEP 440 pre-release versions (`X.Y.ZbN`, `X.Y.ZrcN`) natively with zero configuration changes.
- `pypa/gh-action-pypi-publish@release/v1` requires no `--pre` flag or any special parameter to upload a pre-release wheel/sdist. The version string in the wheel METADATA (set by `setuptools_scm` from the git tag per Phase 15 Finding 4) determines whether PyPI treats it as a prerelease.
- Consumer opt-in is entirely client-side: `pip install --pre firestarter` or `pip install firestarter==X.Y.ZbN`.
- `pip install firestarter` (no flags) will never resolve to a `bN`/`rcN` version. Stable installations are unaffected by beta PyPI uploads.
- `publish.yml` fires on `release: published`. The `release: published` event fires for ALL published GH Releases, both stable (created by `release.yml`) and prerelease (created by `beta-release.yml`). [VERIFIED: GitHub docs — "types: [published]" covers all release publication events]

**Consequence for Phase 16:** `publish.yml` is fully ready for beta releases today, unchanged. The only requirement is that `beta-release.yml` creates a GH Release (which triggers `publish.yml`). The PyPI publish then happens automatically.

### Finding 6: `release: published` Event Fires for Prereleases

[VERIFIED: GitHub Actions docs — release event types include "published" which fires when a release is published, including prereleases]
[VERIFIED: Phase 16 CONTEXT.md D-10 — "GitHub fires this event for BOTH stable and prerelease GH Releases"]

The `on: release: types: [published]` trigger in `publish.yml` fires when ANY GH Release is published, regardless of the `prerelease` flag. Publishing a GH Release with `prerelease: true` is still a publication event. Therefore `publish.yml` will pick up beta releases without modification.

### Finding 7: GATE-01 Verification — Stable Pipeline Non-Regression

[VERIFIED: release.yml read directly; ci.yml read directly; publish.yml read directly]

GATE-01 verification is implemented via git diff assertions per D-22. The specific commands:

```bash
# Run from meta-repo root after Phase 16 PR merges:
git -C firestarter_app diff HEAD~1 -- .github/workflows/release.yml   # must be empty
git -C firestarter_app diff HEAD~1 -- .github/workflows/publish.yml   # must be empty
git -C firestarter_app diff HEAD~1 -- .github/workflows/ci.yml        # must be empty
git -C firestarter_app status -- .github/workflows/                   # must show ONLY beta-release.yml as new
```

If any of the first three commands produce non-empty output, the implementation has violated D-01 and GATE-01. The fourth command verifies that `beta-release.yml` is the only new file.

### Finding 8: `branches: [beta]` — Branch Pre-Existence Not Required

[ASSUMED — based on standard GitHub Actions behavior; not independently verified via docs in this session]

GitHub Actions workflows become active when merged to a branch the workflow file exists on. The `push: branches: [beta]` trigger in `beta-release.yml` does not require the `beta` branch to exist before the workflow file is committed to `beta`. Once `beta-release.yml` is on the `beta` branch, subsequent pushes to `beta` will trigger it. Creating the `beta` branch as part of Phase 16 implementation is the standard pattern.

---

## Common Pitfalls

### Pitfall 1: Auto-Commit Uses PAT → Infinite Loop

**What goes wrong:** If `actions/checkout@v4` is given `token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}`, the git credentials are set to the PAT. The `git-auto-commit-action@v5` push then uses the PAT, which GitHub DOES allow to re-trigger push-event workflows. Result: every auto-commit causes a new workflow run, causing an infinite loop.

**Why it happens:** PAT-authenticated pushes bypass GitHub's recursion guard. The default `GITHUB_TOKEN` push does not.

**How to avoid:** Do NOT add `token:` to the `Checkout` step. Mirror `release.yml`'s checkout step exactly (no `token:` parameter). The commented-out PAT block in `release.yml` (lines 34-35) is a trap — it looks like the PAT is used for the auto-commit but it isn't (it's commented out).

**Warning signs:** Workflow run appears in the Actions tab immediately after the auto-commit step completes, rather than only after a manual push.

**Proof from existing behavior:** `release.yml` fires on `push: branches: [main]`, auto-commits to `main` via `git-auto-commit-action@v5` (no PAT), and does NOT loop today.

### Pitfall 2: Missing `fetch-depth: 0`

**What goes wrong:** Default `actions/checkout@v4` uses `fetch-depth: 1` (shallow clone). `git tag --list "X.Y.Zb*"` returns an empty list or an incomplete list. Phase 15's `_git_tag_scan_fallback()` always emits `b1` because it sees no prior tags. If `b1` was already published to PyPI, the publish step fails with HTTP 400 "File already exists."

**Why it happens:** Shallow clones only fetch recent commit history; tags on older commits are not fetched.

**How to avoid:** Always include `with: fetch-depth: 0` on the `actions/checkout@v4` step. [Phase 15 RESEARCH.md Pitfall #7 — documented as Phase 16/17 requirement]

**Warning signs:** Workflow auto-increments to `b1` even when a prior `b1` already exists on the same base version.

### Pitfall 3: `paths-ignore` Placed Under `workflow_dispatch`

**What goes wrong:** YAML like this is a silent no-op:
```yaml
workflow_dispatch:
  paths-ignore:      # WRONG — not valid under workflow_dispatch
    - '**.md'
```
GitHub silently ignores `paths-ignore` under `workflow_dispatch` — the property has no effect, but the YAML parses without error.

**Why it happens:** `paths-ignore` is only valid under `push:` and `pull_request:` event objects. The GitHub Actions schema allows unknown properties under `workflow_dispatch` without raising errors.

**How to avoid:** Place `paths-ignore` ONLY under the `push:` event block, not at the top level and not under `workflow_dispatch:`. The YAML structure must be:
```yaml
on:
  push:
    branches: [beta]
    paths-ignore:   # CORRECT — under push:
      - '**.md'
  workflow_dispatch:
    inputs:         # CORRECT — no paths-ignore here
      beta_version:
        ...
```

### Pitfall 4: `.yaml` Extension Instead of `.yml`

**What goes wrong:** Creating the file as `beta-release.yaml` instead of `beta-release.yml`. GitHub Actions supports both extensions, but the project convention (and all existing workflow files) use `.yml`.

**How to avoid:** Filename MUST be `beta-release.yml`. Verify: `ls firestarter_app/.github/workflows/` shows `ci.yml`, `release.yml`, `publish.yml` — all `.yml`.

### Pitfall 5: `make_latest: false` Appears to Be Redundant But Isn't

**What goes wrong:** A reviewer might argue that `prerelease: true` alone prevents the release from being "Latest" (and they'd be right — the API enforces this). Removing `make_latest: false` would be tempting as "unnecessary."

**Why it matters:** Explicit `make_latest: false` is the self-documenting correct value from `softprops/action-gh-release@v2`. It communicates intent clearly in code review, and it ensures the behavior if the `prerelease` flag logic ever changes (e.g., accidental omission). Keep it.

### Pitfall 6: `GITHUB_REF` Not Explicitly Set in Version-Bump Step

**What seems wrong:** Phase 15's `update_version.py` reads `os.environ.get("GITHUB_REF")`. One might worry that `GITHUB_REF` needs to be explicitly passed via `env:` in the step.

**Why this is not a problem:** GitHub Actions automatically injects `GITHUB_REF` (and other `GITHUB_*` variables) into every step's environment. When the workflow fires from a `push: branches: [beta]` event, `GITHUB_REF` is automatically `refs/heads/beta`. When fired from `workflow_dispatch` targeting the `beta` branch, `GITHUB_REF` is also `refs/heads/beta`. No explicit `env: GITHUB_REF: ${{ github.ref }}` injection is needed. [VERIFIED: Phase 15 RESEARCH.md Finding 2 — GITHUB_REF semantics per event type]

### Pitfall 7: GATE-01 Regression — Modifying Existing Workflow Files

**What goes wrong:** An implementer edits `ci.yml` (e.g., to add the beta branch to its triggers) or edits `release.yml` (e.g., to add a `workflow_dispatch` trigger to stable). Any such edit breaks GATE-01.

**How to avoid:** D-01 is absolute: zero modifications to `release.yml`, `publish.yml`, `ci.yml`. The GATE-01 verification command (`git diff`) is the automated gate. Code review must also check.

**Why stable doesn't need `workflow_dispatch`:** `release.yml`'s stable path is already invocable via `workflow_dispatch` through the GitHub UI (GitHub offers this option for any workflow file). The LOCKSTEP-PROCEDURE.md Step 4 references `gh workflow run release.yml` — but this is a misprint in the draft procedure; the actual stable workflow is `release.yml` and doesn't need a dispatch trigger for v1.4 purposes. Only `beta-release.yml` needs the `workflow_dispatch` input.

### Pitfall 8: `release: published` on a Pre-Release Does Not Fire If Release is Created as Draft

**What goes wrong:** If `softprops/action-gh-release@v2` were configured to create a draft release first, `publish.yml`'s `release: published` trigger would NOT fire until the draft was manually published. Drafts are never "published" events — they are "released" as drafts.

**Why this isn't a problem for Phase 16:** `beta-release.yml` does NOT create a draft. `softprops/action-gh-release@v2` with no `draft:` parameter creates a published release immediately. The `publish.yml` `release: published` event fires immediately.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| GitHub Release creation | Custom `gh release create` shell step | `softprops/action-gh-release@v2` | Already used in release.yml; handles tag creation, asset upload, prerelease flag atomically |
| Version bump git commit | `git add && git commit && git push` shell step | `stefanzweifel/git-auto-commit-action@v5` | Already used in release.yml; handles no-change case gracefully (no-op instead of error), configures author |
| Python package build | Custom wheel build | `python3 -m build` (already in publish.yml) | Already established; publish.yml handles this unchanged |
| PyPI upload | Custom twine invocation | `pypa/gh-action-pypi-publish@release/v1` (already in publish.yml) | Already established; handles retry, attestations, token scoping |
| Pre-release version computation | Custom shell arithmetic | Phase 15's `update_version.py` | Already shipped; validates input, handles git-tag-scan fallback, writes `GITHUB_OUTPUT` |

**Key insight:** Phase 16 is assembly work — wiring together five already-working components. The only new logic is the `workflow_dispatch` input wiring and the `prerelease: true` + `make_latest: false` flags. Do not invent new patterns.

---

## Validation Architecture

`nyquist_validation` not explicitly set in `.planning/config.json` → treated as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest ≥7.0 (already in `firestarter_app/[dev]` extras) |
| Config file | `firestarter_app/pyproject.toml` — `[tool.pytest.ini_options]` testpaths=["tests"] |
| Quick run command | `cd /workspaces/firestarter_app && pytest tests/ -v` |
| Full suite command | `cd /workspaces/firestarter_app && pytest tests/ -v` (same — one test directory) |

### Phase Requirements → Test Map

Phase 16 deliverable is a single YAML file — no executable Python code changes. Tests are assertions against the workflow file content and git diff state, not pytest unit tests.

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REL-01 | `beta-release.yml` exists and contains required trigger blocks | smoke (grep/cat assertions) | `grep -q 'prerelease: true' firestarter_app/.github/workflows/beta-release.yml` | ❌ Wave 0 (file does not exist yet) |
| REL-01 | `beta-release.yml` contains `make_latest: false` | smoke | `grep -q 'make_latest: false' firestarter_app/.github/workflows/beta-release.yml` | ❌ Wave 0 |
| REL-01 | `beta-release.yml` contains `fetch-depth: 0` | smoke | `grep -q 'fetch-depth: 0' firestarter_app/.github/workflows/beta-release.yml` | ❌ Wave 0 |
| REL-01 | `beta-release.yml` contains `workflow_dispatch` with `beta_version` input | smoke | `grep -q 'beta_version' firestarter_app/.github/workflows/beta-release.yml` | ❌ Wave 0 |
| GATE-01 | `release.yml` byte-identical after Phase 16 commit | git diff | `git -C firestarter_app diff HEAD~1 -- .github/workflows/release.yml` (must be empty) | n/a — git check |
| GATE-01 | `publish.yml` byte-identical after Phase 16 commit | git diff | `git -C firestarter_app diff HEAD~1 -- .github/workflows/publish.yml` (must be empty) | n/a — git check |
| GATE-01 | `ci.yml` byte-identical after Phase 16 commit | git diff | `git -C firestarter_app diff HEAD~1 -- .github/workflows/ci.yml` (must be empty) | n/a — git check |

**Note:** Phase 16 has no new Python code to unit-test. The existing `pytest tests/ -v` suite continues to serve as the CI gate for `update_version.py` (Phase 15) and all other existing test coverage. The planner should structure verification as: (1) yaml lint / grep assertions on the new file, (2) git diff assertions on the three unchanged files, (3) optional real-network dry-run (see Open Questions §1).

### Sampling Rate

- **Per task commit:** `grep` assertions on `beta-release.yml` content (instant; no network)
- **Phase gate:** Git diff assertions on `release.yml`, `publish.yml`, `ci.yml` + existing `pytest tests/ -v` green

### Wave 0 Gaps

- [ ] `firestarter_app/.github/workflows/beta-release.yml` — the only deliverable; does not exist yet

*(Existing test infrastructure covers all other phase requirements; only the new YAML file needs to be created.)*

---

## Security Domain

`security_enforcement` not explicitly set to `false` → included.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | N/A — workflow runs in GitHub Actions with pre-configured secrets |
| V3 Session Management | No | N/A |
| V4 Access Control | Yes (limited) | `permissions: contents: write` scoped at job level; `PERSONAL_ACCESS_TOKEN` already used in `release.yml` — no new secret exposure |
| V5 Input Validation | Yes | `BETA_VERSION` env var validated by Phase 15 regex `^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$` before any file write; regex allows only digits, `.`, `b`, `rc` — no shell metacharacters, no path chars |
| V6 Cryptography | No | N/A |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed `BETA_VERSION` input triggering version file corruption | Tampering | Phase 15 regex validation in `update_version.py` before file open; script exits with error on invalid input |
| Unauthorized beta release via `workflow_dispatch` | Elevation of Privilege | GitHub Actions `workflow_dispatch` is restricted to repository collaborators with write access; same as all other workflows |
| Infinite loop DoS via auto-commit re-trigger | Denial of Service | Default GITHUB_TOKEN checkout (no PAT on checkout step) prevents re-trigger — see Pitfall 1 |
| PyPI version collision / overwrite | Tampering | PyPI is immutable; duplicate version strings rejected with HTTP 400; procedural gap documented in Phase 15 LOCKSTEP-PROCEDURE.md |

---

## Runtime State Inventory

Phase 16 is a greenfield addition (new YAML file). No existing state is renamed or migrated.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | None | None |
| Live service config | None — no external service configuration changes | None |
| OS-registered state | None | None |
| Secrets/env vars | `PERSONAL_ACCESS_TOKEN` (already configured in `firestarter_app` repo for `release.yml`) — reused by `beta-release.yml` with no changes | None |
| Build artifacts | None in Phase 16 scope | None |

---

## Environment Availability

Phase 16 is a YAML file edit — no new CLIs or external services beyond what the existing workflows already use.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `gh` CLI | LOCKSTEP-PROCEDURE Step 4 (operator) | ✓ (on operator machine) | Any modern | GitHub web UI |
| GitHub Actions runners | `beta-release.yml` | ✓ | `ubuntu-latest` | — |
| `secrets.PERSONAL_ACCESS_TOKEN` | Release step | ✓ (already configured for `release.yml`) | — | — |
| `secrets.PYPI_API_TOKEN` | `publish.yml` (unchanged) | ✓ (already configured) | — | — |

**Missing dependencies with no fallback:** None.

---

## Open Questions (RESOLVED)

1. **Can `beta-release.yml` be smoke-tested without actually publishing to PyPI?**
   - What we know: A `workflow_dispatch` run with a test `BETA_VERSION` like `0.0.1b1` would publish to PyPI if the gates pass. There is no built-in "dry run" mode in `beta-release.yml` (only `update_version.py` has `--dry-run`).
   - **RESOLVED:** Real-network testing belongs in Phase 20 E2E-01 (CONTEXT.md D-23). Phase 16 verification uses YAML lint + git diff assertions only. VALIDATION.md Manual-Only Verifications row documents the Phase 20 handoff explicitly.

2. **LOCKSTEP-PROCEDURE Step 4 references `gh workflow run release.yml`**
   - What we know: `15-LOCKSTEP-PROCEDURE.md` Step 4 currently says `gh workflow run release.yml` — should be `beta-release.yml`.
   - **RESOLVED:** Phase 19 (Documentation) will update `v1.4-RELEASE-PROCEDURES.md` AND `15-LOCKSTEP-PROCEDURE.md` with the correct `gh workflow run beta-release.yml --ref beta -f beta_version=X.Y.ZbN` command shape. Tracked as a Phase 19 deliverable; not a Phase 16 blocker.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `branches: [beta]` in `push:` trigger does not require the `beta` branch to pre-exist before `beta-release.yml` is committed | Finding 8 | If wrong: the `beta` branch must be created before the workflow is merged. Mitigation: create the `beta` branch as part of Phase 16 implementation — low risk. |
| A2 | `permissions: contents: write` at job level suffices for both `git-auto-commit-action@v5` (branch push) and `softprops/action-gh-release@v2` (release create) without a workflow-level `permissions:` block | Implementation Approach — design note 5 | If wrong: add `permissions: contents: write` at workflow level as well. Impact is minimal — a one-line edit. `release.yml` uses job-level only and works today. |

**Minimal assumptions.** The primary claims are directly verified from existing workflow files in the repository or from official GitHub documentation.

---

## Sources

### Primary (HIGH confidence)
- `/workspaces/firestarter_app/.github/workflows/release.yml` — structural template; all step patterns verified by direct read
- `/workspaces/firestarter_app/.github/workflows/ci.yml` — gate step source; catalog validity + codegen drift + pytest steps copied inline
- `/workspaces/firestarter_app/.github/workflows/publish.yml` — confirmed `release: published` trigger; no modification needed
- `/workspaces/firestarter_app/.github/scripts/update_version.py` — Phase 15 deliverable; `BETA_VERSION` env var reading, `is_beta_mode()` logic verified by direct read
- `/workspaces/.planning/phases/16-app-beta-release-pipeline/16-CONTEXT.md` — all 27 locked decisions
- `/workspaces/.planning/phases/15-versioning-locked-step-coordination-foundation/15-RESEARCH.md` — PEP 440 findings, GITHUB_REF semantics, fetch-depth:0 pitfall
- `/workspaces/.planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md` — Phase 16/17 implementation requirements; workflow YAML shape contract

### Secondary (MEDIUM confidence)
- [stefanzweifel/git-auto-commit-action README](https://github.com/stefanzweifel/git-auto-commit-action) — "events triggered by GITHUB_TOKEN will not create a new workflow run"; PAT vs GITHUB_TOKEN push behavior
- [softprops/action-gh-release README (v2)](https://github.com/softprops/action-gh-release/tree/v2) — `make_latest` and `prerelease` parameter documentation
- [GitHub REST API docs — releases](https://docs.github.com/en/rest/releases/releases) — "latest release is the most recent non-prerelease, non-draft release"; `/releases/latest` behavior verified
- [GitHub community discussion #29242](https://github.com/orgs/community/discussions/29242) — `inputs` context evaluates to empty string on non-workflow_dispatch triggers
- [GitHub Actions workflow syntax docs](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions) — `workflow_dispatch.inputs` YAML structure; `paths-ignore` scope

### Tertiary (LOW confidence / ASSUMED)
- Claim A1 (branch pre-existence) — standard GitHub Actions behavior per training knowledge; not independently verified via docs lookup in this session

---

## Metadata

**Confidence breakdown:**
- Standard stack (action versions): HIGH — verified from existing workflow files in repo
- YAML structure for beta-release.yml: HIGH — derived from release.yml template + ci.yml gate steps + 15-LOCKSTEP-PROCEDURE.md contract
- Auto-commit loop behavior: HIGH — verified from stefanzweifel README + release.yml existing behavior (stable doesn't loop)
- `github.event.inputs` on push trigger: HIGH — verified from GitHub community discussion
- `make_latest: false` + `prerelease: true` semantics: HIGH — verified from GitHub REST API docs
- `release: published` fires for prereleases: HIGH — verified from GitHub docs + ci.yml inspection
- GATE-01 git diff verification: HIGH — pattern derived from D-22 decisions; commands verified from git knowledge

**Research date:** 2026-05-20
**Valid until:** 2026-06-20 (GitHub Actions API surface is stable; action major versions change slowly)

---

## RESEARCH COMPLETE

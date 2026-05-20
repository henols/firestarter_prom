---
phase: 16-app-beta-release-pipeline
reviewed: 2026-05-20T00:00:00Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - firestarter_app/.github/workflows/beta-release.yml
findings:
  critical: 0
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 16: Code Review Report

**Reviewed:** 2026-05-20
**Depth:** standard
**Files Reviewed:** 1
**Status:** issues_found

## Summary

Reviewed `firestarter_app/.github/workflows/beta-release.yml`, the single deliverable for Phase 16.

The security-critical properties are all correct: no `token:` override on the checkout step
(no infinite-loop risk from PAT-pushed commits re-triggering the push event), `BETA_VERSION`
is passed only via an `env:` block (no shell interpolation, no injection surface),
`PERSONAL_ACCESS_TOKEN` is scoped exclusively to the Release step, `prerelease: true` +
`make_latest: false` are present, and the auto-commit step uses the job's default
`GITHUB_TOKEN` (not the PAT), which GitHub suppresses from re-triggering `push:` events.

Structural correctness is also good: CI gates run before the version bump, `fetch-depth: 0`
is on the checkout, `paths-ignore` is under `push:` only (not `workflow_dispatch:`), no
`concurrency` block (correct per D-25), all action pins are major-version references
(`@v4`, `@v5`, `@v2`) with no floating `@main`, and the YAML file parses cleanly with no
tabs and valid ASCII encoding.

Two warnings were found. The more impactful one is that `tools/**` in `paths-ignore`
byte-matches `release.yml` (per D-04), but because `beta-release.yml` embeds inline CI
gates that check codegen artifacts — which `release.yml` does not — the match creates a
deferred-detection gap: a beta push that only modifies `tools/catalog/messages.toml` will
not trigger the workflow, allowing a codegen drift to go undetected until the next
non-tools push. The second warning is omission of the D-26 audit echo step, which the
CONTEXT explicitly recommended for observability of auto-increment cuts. One info item
notes the absence of a `workflow_dispatch` ref guard, which means a mistaken
`gh workflow run beta-release.yml --ref main` would silently run the stable version-bump
path instead of the beta path; this is operator-procedural and documented in Phase 15.

---

## Warnings

### WR-01: `tools/**` in `paths-ignore` silently bypasses the codegen drift gate on tool-only pushes to `beta`

**File:** `firestarter_app/.github/workflows/beta-release.yml:13`

**Issue:** `beta-release.yml` embeds inline CI gates including a codegen drift gate
(`git diff --exit-code firestarter/messages.py`) that `release.yml` does not have. The
`paths-ignore` list nonetheless byte-matches `release.yml` and includes `tools/**`. This
means a push to `beta` that modifies only `tools/catalog/messages.toml` (without
regenerating `firestarter/messages.py`) will not trigger the workflow at all. The codegen
drift goes undetected until the next push matching a non-ignored path.

For `release.yml`, excluding `tools/**` is harmless because that workflow has no CI gates.
For `beta-release.yml`, the exclusion creates a deferred-detection gap that does not
exist on `main` (where `ci.yml` omits `tools/**` from its `paths-ignore`, so a
`messages.toml` push always triggers the drift gate).

**Fix:** Remove `tools/**` from `paths-ignore` in `beta-release.yml`. This intentionally
diverges from `release.yml`'s list but matches the CI coverage obligation that `ci.yml`
provides on `main`.

```yaml
# Change paths-ignore from:
    paths-ignore:
    - '**.md'
    - '**.sh'
    - '.gitignore'
    - 'docs/**'
    - 'images/**'
    - '.github/**'
    - '.vscode/**'
    - 'tools/**'    # remove this line

# To:
    paths-ignore:
    - '**.md'
    - '**.sh'
    - '.gitignore'
    - 'docs/**'
    - 'images/**'
    - '.github/**'
    - '.vscode/**'
```

---

### WR-02: D-26 audit echo step omitted — resolved beta version is not surfaced in the workflow summary

**File:** `firestarter_app/.github/workflows/beta-release.yml` (after line 73 — step missing)

**Issue:** CONTEXT.md D-26 explicitly recommends a final echo step surfacing the resolved
`BETA_VERSION`: "recommended yes via a final step echo (cheap, audit-friendly)." The
implementation omits it with no explanation. The gap is most impactful for push-triggered
auto-increment cuts where no `beta_version` input is provided: the operator has no
quick way to confirm which `bN` was computed without inspecting the `Create new pre-release
version` step logs. For `workflow_dispatch` invocations, the `beta_version` input is
visible in the GHA trigger summary, but for push-triggered runs it is invisible without
digging into logs.

**Fix:** Add a final step after Release:

```yaml
      - name: Show resolved beta version
        run: |
          echo "Resolved beta version: ${{ steps.version.outputs.version }}"
          echo "## Beta release created" >> $GITHUB_STEP_SUMMARY
          echo "**Version:** \`${{ steps.version.outputs.version }}\`" >> $GITHUB_STEP_SUMMARY
```

---

## Info

### IN-01: No `workflow_dispatch` ref guard — mistaken invocation on `main` silently runs the stable version-bump path

**File:** `firestarter_app/.github/workflows/beta-release.yml:15-20`

**Issue:** If an operator runs `gh workflow run beta-release.yml --ref main` (omitting
`--ref beta`), GitHub dispatches the workflow against `main`. At that point
`GITHUB_REF=refs/heads/main`, `update_version.py`'s `is_beta_mode()` check returns
`False`, and the script runs the stable patch-increment path — bumping the stable version,
committing to `main`, and creating a non-prerelease GitHub Release (because `prerelease:
true` is baked into the workflow YAML, so the release is still marked prerelease, but the
version tag will be a plain `X.Y.Z`-style string). The workflow has no `if:` condition to
validate that `GITHUB_REF` is `refs/heads/beta` before proceeding.

This scenario requires a deliberate operator error and is mitigated by the Phase 15
lockstep procedure (`--ref beta` is explicit in operator docs). Classified INFO because it
is not a code defect in the shipped file but a missing defensive guard.

**Fix (optional hardening):** Add an early check step that asserts `GITHUB_REF` before
the version bump runs:

```yaml
      - name: Assert beta branch
        run: |
          if [ "${GITHUB_REF}" != "refs/heads/beta" ]; then
            echo "ERROR: This workflow must run against the beta branch (got ${GITHUB_REF})"
            exit 1
          fi
```

Place this step before `Create new pre-release version` (line 56). This converts a silent
mis-fire into a visible failure with a clear error message.

---

_Reviewed: 2026-05-20_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

# v1.4 Lockstep Coordination Procedure

## Purpose

This document describes the operator workflow for cutting a coordinated v1.4 beta release
across both Firestarter sub-repositories (`firestarter_app` and `firestarter`). Lockstep
coordination means both repositories publish the identical version string (e.g. `3.1.0b1`)
to their respective release channels at the same time. This procedure was designed for the
v1.4 milestone beta channel and is consumed verbatim by Phase 18's `v1.4-RELEASE-PROCEDURES.md`
(DOC-03). A release engineer with no prior v1.4 context should be able to cut a beta by
following this document as a checklist.

## Prerequisites

Before cutting a coordinated beta, confirm each item:

1. Both sub-repos have a `beta` branch that exists and is up to date with the desired
   feature set (typically fast-forwarded from `main` or a feature branch).

2. Both sub-repos' `.github/scripts/update_version.py` have shipped the Phase 15 extensions.
   Verify by running:
   ```bash
   # In firestarter_app/:
   python3 -c "import sys; sys.path.insert(0, '.github/scripts'); import update_version; print(update_version.BETA_VERSION_RE.pattern)"
   # Must print: ^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$

   # In firestarter/:
   python3 -c "import sys; sys.path.insert(0, '.github/scripts'); import update_version; print(update_version.BETA_VERSION_RE.pattern)"
   # Must print: ^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$
   ```

3. Both repos' beta workflows (delivered by Phases 16 + 17) use `actions/checkout@v4` with
   `fetch-depth: 0` so the git-tag-scan fallback can see full tag history.

4. You have the `gh` CLI installed and authenticated with write access to both sub-repos:
   ```bash
   gh auth status
   gh api repos/<owner>/firestarter_app --jq '.permissions.push'   # must be true
   gh api repos/<owner>/firestarter --jq '.permissions.push'        # must be true
   ```

5. The chosen `BETA_VERSION` string is PEP 440 canonical: `X.Y.ZbN` or `X.Y.ZrcN` (lowercase,
   no separators between base and pre-release segment, no separators within pre-release).

## Version string format

Validation regex (identical in both `update_version.py` scripts, per VER-03):

```
^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$
```

**Accepted:** `3.1.0b1`, `3.1.0b2`, `3.1.0rc1`, `0.0.1b1`, `1.2.3rc2`

**Rejected:**
- `3.1.0beta1` — pre-release label spelled out (use `b`, not `beta`)
- `3.1.0-b1` — separator before pre-release segment
- `3.1.0B1` — uppercase `B`
- `3.1.0a1` — alpha segment (out of scope for v1.4)
- `3.1.0` — no pre-release segment (this would be a stable version)
- `3.1.0.post1` — post-release segment (not supported)

**Monotonic increment rule:** The first beta on a base version line starts at `b1`
(e.g. `3.1.0b1`). Subsequent betas on the same base increment monotonically: `b2`, `b3`, etc.
Promotion from beta to release candidate requires an explicit operator decision — supply
`BETA_VERSION=X.Y.ZrcN` rather than relying on any automatic promotion.

**PyPI visibility:** PyPI stores pre-release versions normally. Consumers must pass
`pip install --pre firestarter==X.Y.ZbN` to opt in. Standard `pip install firestarter`
will NOT pull pre-release versions.

## Procedure

Follow these steps in order. Each step is atomic; if any step fails, see **Failure recovery**
before re-running.

### Step 1 — Choose the lockstep version string

Select the `BETA_VERSION` to publish. Guidelines:
- For a v1.4 validation cut or Phase 19 E2E smoke test: use a clearly-test-only string
  such as `0.0.1b1` that cannot conflict with the current stable version lines
  (`2.0.7` for the app, `3.0.0` for the firmware).
- For a real beta cut: choose the next version base and append `b1`
  (e.g. `3.1.0b1` if the next planned stable release is `3.1.0`).
- Never reuse a `BETA_VERSION` that has already been published to PyPI or GitHub Releases
  without incrementing the beta counter — PyPI will reject duplicate uploads.

### Step 2 — Verify locally with the dry-run fixture

Run the lockstep fixture from the meta-repo root:

```bash
cd <meta-repo-root>
BETA_VERSION=<chosen-string> bash .planning/phases/15-versioning-locked-step-coordination-foundation/lockstep-dryrun-fixture.sh
```

Expected output (exit code 0):
```
LOCKSTEP DRY-RUN FIXTURE
========================
BETA_VERSION=<chosen-string>
App emits:       DRY_RUN: <chosen-string>
Firmware emits:  DRY_RUN: <chosen-string>

LOCKSTEP OK
```

If the fixture exits non-zero, do NOT proceed. Investigate the mismatch before triggering CI.

### Step 3 — (Optional) Desk-side dry-run per sub-repo

For additional confidence, run each script individually:

```bash
# App side (from firestarter_app/):
BETA_VERSION=<chosen-string> GITHUB_REF=refs/heads/beta \
  python3 .github/scripts/update_version.py --dry-run
# Expected: DRY_RUN: <chosen-string>

# Firmware side (from firestarter/):
BETA_VERSION=<chosen-string> GITHUB_REF=refs/heads/beta \
  python3 .github/scripts/update_version.py --dry-run
# Expected: DRY_RUN: <chosen-string>
```

Both must print `DRY_RUN: <chosen-string>` and exit 0.

### Step 4 — Trigger the app-side beta workflow

```bash
gh workflow run release.yml \
  -R <owner>/firestarter_app \
  --ref beta \
  -f beta_version=<chosen-string>
```

Alternatively, use the GitHub web UI: Actions > Beta Release > Run workflow > fill in
`beta_version`.

Wait for the workflow to complete (`gh run watch` or refresh the Actions tab), then verify:
- The new GitHub Release in `firestarter_app` is marked **Pre-release** (not Latest).
- PyPI shows `<chosen-string>` on the `firestarter` project page.
- `pip install --pre firestarter==<chosen-string>` succeeds and
  `firestarter --version` reports `<chosen-string>`.

### Step 5 — Trigger the firmware-side beta workflow with the SAME `BETA_VERSION`

```bash
gh workflow run build.yml \
  -R <owner>/firestarter \
  --ref beta \
  -f beta_version=<chosen-string>
```

Wait for the workflow to complete, then verify:
- The new GitHub Release in `firestarter` is marked **Pre-release** (not Latest).
- The release assets include the `firestarter_*.hex` build artifacts for each board target.
- The release body or `include/version.h` snapshot in the release contains
  `#define VERSION "<chosen-string>"`.

### Step 6 — Post-cut verification

Confirm all of the following before declaring the beta cut complete:

| Check | Command / Location | Expected |
|-------|--------------------|----------|
| App PyPI version | `pip show firestarter` or PyPI web | `<chosen-string>` |
| App CLI version | `pip install --pre firestarter==<chosen-string> && firestarter --version` | `<chosen-string>` |
| App GitHub Release tag | GitHub Release `firestarter_app/<chosen-string>` | Tagged, Pre-release=true |
| Firmware GitHub Release tag | GitHub Release `firestarter/<chosen-string>` | Tagged, Pre-release=true |
| Firmware version.h | In release assets or `firestarter` beta-branch HEAD | `#define VERSION "<chosen-string>"` |
| Both tags are string-equal | Compare the two release tag names | Byte-identical `<chosen-string>` |

## Version state storage

Beta version strings are written into the same source files as stable versions (per D-10):

- **App:** `firestarter_app/firestarter/__init__.py` — line `__version__ = "X.Y.ZbN"`
- **Firmware:** `firestarter/include/version.h` — line `#define VERSION "X.Y.ZbN"`

Branch isolation handles state separation (D-11): a `beta`-branch checkout carries beta version
strings; a `main`-branch checkout carries stable version strings. There are no new state files
and no shared cross-branch state between the two repos.

## Initial version reconciliation

At v1.4 milestone start (D-18), the app sits at `2.0.7_dev` and the firmware at `3.0.0-dev`.
These version strings do NOT match, and they do not need to match. Per D-20, stable versions
continue to auto-bump independently in each sub-repo; drift between stable versions is a known
acceptable state.

Lockstep is a property of **beta releases only**, not stable releases. The first coordinated
beta cut (Phase 19) chooses an explicit `BETA_VERSION` — likely `0.0.1b1` (a test-only
identifier that does not conflict with either stable version line). That choice is made by the
release engineer at cut time; Phase 15 guarantees the scripts can write whatever string the
operator supplies.

## Failure recovery

Lockstep is enforced at write time via the explicit `BETA_VERSION` input. If one workflow
fails after the other succeeded, apply the recovery below based on what failed:

| Scenario | Recovery action |
|----------|-----------------|
| App workflow failed before any file write or PyPI upload (e.g., CI test step failed) | Fix the failing test or build error; re-trigger the app workflow with the **same** `BETA_VERSION`. No drift — neither PyPI nor GitHub Release for the app exists yet. |
| App workflow succeeded and published to PyPI; firmware workflow failed at build or codegen gate | Fix the firmware issue; re-trigger the firmware workflow with the **same** `BETA_VERSION`. App is already published; firmware catches up to the same string. |
| App workflow created a PyPI release; same workflow re-triggered and PyPI rejects the upload with HTTP 400 "File already exists" | PyPI does not accept re-uploads of the same version. Increment `BETA_VERSION` to the next `bN` (e.g. `b2`) and run **both** workflows again with the new string to restore lockstep. This is a **known gap** per D-03; idempotent re-publish is deferred to a future milestone. |
| Firmware GitHub Release exists; app PyPI publish failed in the same attempted cut | Manually delete the firmware GitHub Release tag (from the Releases page or via `gh release delete <tag> -R <owner>/firestarter`), then re-cut both with the same `BETA_VERSION` from Step 4. Alternatively, increment `BETA_VERSION` and re-cut both. |
| Both workflows failed before any publish | Fix both issues; re-trigger both with the original `BETA_VERSION`. No published artifacts to undo. |

## Phase 16/17 implementation requirements (handoff)

For Phase 16 (app beta release workflow) and Phase 17 (firmware beta release workflow) authors,
the procedure above implies these workflow constraints:

**Trigger shape** — both beta workflows MUST declare both trigger types:

```yaml
on:
  push:
    branches: [beta]
  workflow_dispatch:
    inputs:
      beta_version:
        description: 'Beta version string (e.g. 3.1.0b1).'
        required: false
        default: ''
        type: string
```

**Environment mapping** — the version-bump step MUST set:

```yaml
env:
  GITHUB_REF: ${{ github.ref }}
  BETA_VERSION: ${{ github.event.inputs.beta_version }}
```

The `update_version.py` script reads `GITHUB_REF` for branch detection and `BETA_VERSION`
for the explicit lockstep input. When `BETA_VERSION` is set to a non-empty string, it is
used verbatim (D-07); when empty (push-triggered run without dispatch input), the script
falls back to git-tag scan (D-08).

**Shallow-clone guard** — `actions/checkout@v4` MUST use `fetch-depth: 0`:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

Without full history, the D-08 git-tag-scan fallback cannot scan prior `bN` tags and will
always emit `b1` regardless of prior betas on the same base version. This causes silent
duplicate tags if `b1` was already published.

**Release step flags** — the `softprops/action-gh-release@v2` step MUST set:

```yaml
prerelease: true
make_latest: false
```

This ensures beta releases are never promoted to "Latest Release" on GitHub, which would
override the stable release pointer and confuse users on the default download path.

**App PyPI publish** — `pypa/gh-action-pypi-publish@release/v1` requires no special flags
for pre-release versions. PyPI accepts `bN`/`rcN` automatically; the `pip install --pre`
opt-in lives on the client side.

## Known gaps (carry-forward to a future milestone)

The following items are intentionally deferred from v1.4:

- **Idempotent beta re-publish** (D-03): if one repo published and the other failed downstream,
  re-triggering with the same `BETA_VERSION` will fail with PyPI HTTP 400. Recovery requires
  incrementing the beta counter. A robust idempotent solution would need a separate design
  (e.g. checking PyPI existence before upload). Not fixed in v1.4.

- **`_dev` / `-dev` suffix in version files** (D-25): both repos' version files currently
  carry `_dev` / `-dev` suffixes (e.g. `2.0.7_dev`, `3.0.0-dev`) that are silently truncated
  by the version-file parse regex. This is pre-existing behavior, preserved intentionally.
  Clean up in a future version-format unification milestone.

- **Cross-repo `repository_dispatch` automation** (D-02 rejected alternative): if the
  procedural lockstep proves brittle in practice, a future milestone may introduce a
  cross-repo trigger that automatically fans out to both repos. Rejected for v1.4 because it
  requires a cross-repo PAT with `repo` scope.

- **Auto-promotion beta to stable**: explicitly deferred. Manual promotion path is a
  fast-forward merge from `beta` to `main` after the beta is validated, followed by a
  normal stable release cut.

- **Signed release artifacts**: out of scope for v1.4. Would cover both stable and beta
  artifacts in a dedicated milestone (sigstore or GPG-signed releases).

- **Branch protection rules on `beta` branch**: optional safety net to prevent accidental
  force-pushes or non-lockstep direct writes to `beta`. Deferred post-v1.4.

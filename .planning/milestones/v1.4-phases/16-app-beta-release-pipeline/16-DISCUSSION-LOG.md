# Phase 16: App Beta Release Pipeline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.

**Date:** 2026-05-20
**Phase:** 16-app-beta-release-pipeline
**Discussion mode:** `--auto --chain`
**Areas discussed:** A) Workflow file shape, B) Triggers, C) CI gate placement, D) publish.yml integration, E) BETA_VERSION sourcing, F) Tag namespace, G) Auto-commit, H) Permissions, I) ci.yml extension, J) GATE-01 verification

---

## A. Workflow File Shape

| Option | Description | Selected |
|--------|-------------|----------|
| NEW `beta-release.yml` file | Self-contained, sibling to release.yml. Stable byte-identity trivial to verify. | ✓ |
| Extend release.yml with conditional branch logic | Risks GATE-01 byte-identity; complicates `on:` filters. | |
| Reusable workflow shared by both | Reduces duplication but adds dependency complexity for v1.4 scope. | |

---

## B. Triggers

| Option | Description | Selected |
|--------|-------------|----------|
| `push: branches: [beta]` + `workflow_dispatch` (with `beta_version` input) | Branch-driven (operator convenience) + explicit lockstep cut (workflow_dispatch). | ✓ |
| `push` only | Forces release engineer to push commits to coordinate lockstep — friction. | |
| `workflow_dispatch` only | Removes branch-driven convenience promised in STATE v1.4 Decisions. | |

---

## C. CI Gate Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Inline steps mirroring release.yml + ci.yml (catalog validity → codegen drift → pytest → version bump) | Self-contained; matches release.yml self-contained pattern. | ✓ |
| Call ci.yml as a reusable workflow | Less duplication but adds workflow-dependency edge case for v1.4. | |
| Skip CI on beta builds (operator validates manually) | Breaks the GATE-01 spirit ("beta artifacts must pass the same gates as stable"). | |

---

## D. publish.yml Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Unchanged — fires on release: published for both stable and prerelease | GH event semantics + PyPI action natively handle PEP 440 prereleases. | ✓ |
| Add a tag-pattern filter to publish.yml | Unnecessary; tag pattern is implicit in version string. | |
| Duplicate publish.yml as beta-publish.yml | Adds maintenance surface for zero benefit. | |

---

## E. `BETA_VERSION` Sourcing

| Option | Description | Selected |
|--------|-------------|----------|
| `workflow_dispatch.inputs.beta_version` (optional) → env; fallback to Phase 15 D-08 git-tag scan | Explicit for lockstep cuts; auto for casual beta pushes. | ✓ |
| Required workflow_dispatch input | Breaks the bare `push: beta` convenience trigger. | |
| Env var only (no input at all) | Loses the operator-facing lockstep mechanism Phase 15 designed for. | |

---

## F. Tag Namespace

| Option | Description | Selected |
|--------|-------------|----------|
| Single namespace; bare PEP 440 strings (`3.1.0`, `3.1.0b1`) | Matches Phase 15 BETA_VERSION_RE; no transformation needed. | ✓ |
| Prefix beta tags (`beta-X.Y.ZbN` or `v-beta-X.Y.ZbN`) | Inconsistent with stable; PyPI tag != git tag becomes confusing. | |

---

## G. Auto-Commit Back to Beta

| Option | Description | Selected |
|--------|-------------|----------|
| `stefanzweifel/git-auto-commit-action@v5` (mirror release.yml defaults) | Already used in release.yml; default behavior is correct. | ✓ |
| Manual git commit + push step | Reinvents the wheel; loses error-handling the action provides. | |
| Skip auto-commit (version-bump lives only in the GH Release tag) | Confusing: `pip install firestarter` would see a different `__version__` than the tag. | |

---

## H. Permissions

| Option | Description | Selected |
|--------|-------------|----------|
| `contents: write` only (matches release.yml) | Minimum required for auto-commit + release creation. | ✓ |
| Broader (`contents: write` + `pull-requests: write`) | Unnecessary for v1.4 scope. | |

---

## I. ci.yml Extension

| Option | Description | Selected |
|--------|-------------|----------|
| NO change to ci.yml | beta-release.yml self-contained; no value in dual-firing. | ✓ |
| Extend ci.yml to fire on `beta` branch PRs/pushes | Duplicates beta-release.yml's inline gates on the same commit. | |

---

## J. GATE-01 Verification

| Option | Description | Selected |
|--------|-------------|----------|
| Git-diff assertion that release.yml/publish.yml/ci.yml are byte-unchanged in the Phase 16 PR commit | Cheap, automated, definitive. | ✓ |
| Manual review of the diff | Subjective; doesn't scale. | |

---

## Claude's Discretion

- **D-24**: YAML quoting style — planner picks per project convention.
- **D-25**: `concurrency` group — recommended NO; planner may add if a use case emerges.
- **D-26**: Workflow run summary echo of resolved BETA_VERSION — recommended yes; format up to planner.
- **D-27**: Whether to keep `paths-ignore` on beta-release.yml — recommended yes (byte-match release.yml).

## Deferred Ideas

- Reusable workflow extraction (v1.5+).
- `concurrency` group.
- Branch protection on `beta` branch (Future Requirements).
- TestPyPI publishing (rejected for v1.4).
- Auto-promotion workflow (deferred).
- Fork-PR beta builds (out of scope).

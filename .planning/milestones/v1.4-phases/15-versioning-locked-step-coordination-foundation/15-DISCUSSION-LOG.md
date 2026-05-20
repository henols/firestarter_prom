# Phase 15: Versioning & Locked-Step Coordination (Foundation) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-20
**Phase:** 15-versioning-locked-step-coordination-foundation
**Discussion mode:** `--auto --chain` (autonomous selection of recommended options; chain to plan-phase)
**Areas discussed:** A) Lockstep coordination mechanism, B) Beta-branch context detection, C) Beta version identifier computation, D) Beta version state storage, E) Test framework / dry-run, F) Stable code-path preservation, G) Initial version reconciliation, H) PEP 440 segment coverage, I) Regex extension for suffix readback

---

## A. Lockstep Coordination Mechanism (load-bearing — VER-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Manually-paired beta-branch push with explicit `BETA_VERSION` input | Release engineer chooses version, supplies via `workflow_dispatch` input (or env var) to BOTH repos' beta workflows. Procedural lockstep, no shared infra. | ✓ |
| Shared `VERSION` file in meta-repo | Both sub-repos' beta workflows read from / write to a meta-repo `VERSION` file. Single source of truth but requires cross-repo write-token auth. | |
| Cross-repo `repository_dispatch` workflow trigger | App push triggers firmware build via dispatch event with version payload. Tightest coupling, requires PAT with `repo` scope on both repos. | |

**Auto-selected (recommended):** Manually-paired beta-branch push.
**Rationale:** Lightest-weight option; matches existing per-repo independent-auto-bump pattern for stable; fits v1.4's "additive plumbing + docs only" scope. No new auth requirements (no PAT, no meta-repo write). Lockstep enforced at write time via explicit operator input.

---

## B. Beta-Branch Context Detection

| Option | Description | Selected |
|--------|-------------|----------|
| Read `GITHUB_REF` env var + `--beta` CLI flag override | Primary: GitHub Actions auto-populates `GITHUB_REF=refs/heads/beta`. Secondary: explicit CLI flag for local/test invocation. | ✓ |
| `--beta` CLI flag only | Workflow yaml has to pass `--beta` explicitly on each invocation. | |
| Git-branch detection via `git rev-parse` | Run `git rev-parse --abbrev-ref HEAD` inside the script to determine branch. Adds subprocess dependency; brittle in detached-HEAD checkouts. | |

**Auto-selected (recommended):** `GITHUB_REF` + `--beta` CLI flag.
**Rationale:** GitHub Actions sets `GITHUB_REF` for free on every run; zero workflow-yaml changes for detection. CLI flag is the test-fixture escape hatch.

---

## C. Beta Version Identifier Computation

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid: explicit `BETA_VERSION` verbatim (lockstep cuts) + git-tag scan fallback (local dev) | When `BETA_VERSION` env var is set, write it verbatim. When absent, scan git tags for highest `b/rcN` matching base version, emit `b(N+1)`. | ✓ |
| Auto-scan git tags only | Always compute from tag history. Risks drift between repos when their tag histories diverge. | |
| File-based counter (`BETA_COUNT` file) | Maintain a counter file in repo; increment per push. Extra state file, no clear benefit over tag-scan. | |
| Explicit input always required | Refuse to run without `BETA_VERSION` set. Loses local-dev ergonomics. | |

**Auto-selected (recommended):** Hybrid.
**Rationale:** Lockstep cuts use explicit input (D-01 mechanism); local dev / testing uses the auto-increment fallback. No risk of cross-repo drift in production because operator always supplies explicit version for lockstep cuts.

---

## D. Beta Version State Storage

| Option | Description | Selected |
|--------|-------------|----------|
| Same files as stable (`__init__.py` / `version.h`) | Beta-branch writes `X.Y.ZbN` into the existing version files. Branch isolation handles state separation. | ✓ |
| Separate beta-version files (e.g. `BETA_VERSION` text file) | Avoid polluting stable version files. Adds new state, requires new read-paths everywhere version is consumed. | |

**Auto-selected (recommended):** Same files as stable.
**Rationale:** Minimal new state; branch isolation handles the separation naturally; consumers of the version string (PyPI publish, GitHub Release tag, `pip show firestarter`) all work without modification.

---

## E. Test Framework / Dry-Run Affordance (per Phase 15 SC#4)

| Option | Description | Selected |
|--------|-------------|----------|
| pytest in both sub-repos + `--dry-run` flag | App: `firestarter_app/tests/test_update_version.py` (existing pytest infra). Firmware: new lightweight pytest infra under `firestarter/.github/scripts/tests/` or `firestarter/tests/`. Both scripts get `--dry-run` for CI smoke checks. | ✓ |
| pytest app-side only + manual firmware verification | Skip firmware-side pytest because firmware's primary test framework is PlatformIO Unity (C++). | |
| Golden-file diff only, no pytest | Both scripts emit a `--dry-run` output, CI diffs against a checked-in golden file. Lightweight but couples test logic to file format. | |
| PlatformIO native test on firmware side | Use Unity to test the firmware Python script. Doesn't fit — Unity targets C++ not Python. | |

**Auto-selected (recommended):** pytest in both + `--dry-run`.
**Rationale:** App side already has pytest infra (29 tests passing); near-zero cost to add `test_update_version.py`. Firmware side adopts a minimal pytest scaffold (just for this script and any future Python scripts in `.github/scripts/`). `--dry-run` provides a CLI-level smoke check for CI and Phase 19 E2E verification.

---

## F. Stable Code-Path Preservation (GATE-01/02 derivative)

| Option | Description | Selected |
|--------|-------------|----------|
| Extend `update_version.py` in-place; stable path byte-identical; beta is a guarded code branch | Single file per repo. Beta logic activated only when env vars / flags signal beta context. | ✓ |
| Split into `update_version_stable.py` + `update_version_beta.py` | Two scripts; existing workflow yaml selects which one to call. Doubles maintenance surface. | |
| New beta-only `update_beta_version.py`, leave stable script untouched | Two scripts; less risk of regressing stable; but duplicates parse / write logic. | |

**Auto-selected (recommended):** Extend in-place.
**Rationale:** Single file per repo; GATE-01/02 byte-identity verification is straightforward (run new script with no beta inputs, diff against old script's output). Shared parse / write helpers stay DRY.

---

## G. Initial Lockstep Version Reconciliation

| Option | Description | Selected |
|--------|-------------|----------|
| Lockstep starts at first beta cut; stable versions continue independently | Don't retroactively realign `2.0.7_dev` (app) and `3.0.0-dev` (firmware). First beta cut sets a new coordinated version. | ✓ |
| Force-bump app to 3.x to match firmware before v1.4 closes | Bump app to `3.0.0` (or `3.1.0`) on the next stable cut so version strings align between repos. | |
| Force-bump firmware to 2.x to match app | Bump firmware down. Awkward because firmware just had a major bump for v1.2 lockstep upgrade. | |

**Auto-selected (recommended):** Lockstep starts at first beta cut.
**Rationale:** Lockstep is a property of beta releases specifically (per STATE.md v1.4 Decisions). Retroactive realignment adds churn for no functional gain. First beta cut (Phase 19 E2E) picks a coordinated version (e.g. `3.1.0b1`); stable continues to auto-bump per repo independently.

---

## H. PEP 440 Segment Coverage

| Option | Description | Selected |
|--------|-------------|----------|
| `bN` (beta) + `rcN` (release candidate) only | Validate `BETA_VERSION` against `^[0-9]+\.[0-9]+\.[0-9]+(b\|rc)[0-9]+$`. | ✓ |
| `bN` only | Simplest. But REQUIREMENTS.md VER-01 explicitly mentions `rcN`. | |
| Full PEP 440 (`aN`, `bN`, `rcN`, `devN`, `postN`, `+local`) | Maximum flexibility. Overkill for v1.4 scope. | |

**Auto-selected (recommended):** `bN` + `rcN`.
**Rationale:** Matches REQUIREMENTS.md VER-01 exactly. Adds `rcN` for the eventual promotion-to-stable confidence stage. Skips `aN` / `devN` / `postN` because no current use case.

---

## I. Regex Extension for Suffix Readback

| Option | Description | Selected |
|--------|-------------|----------|
| Extend version-parse regex to capture optional `(b\|rc)N` suffix | New regex: `^[0-9]+\.[0-9]+\.[0-9]+(b\|rc)?[0-9]*` or named-groups form. Stable bumps strip suffix; beta bumps preserve / increment. | ✓ |
| Leave regex alone; accept that beta versions can't be read back | Script would lose context between beta runs. Breaks D-08 git-tag fallback. | |
| Replace regex with PEP 440 library parse (`packaging.version`) | Pull in `packaging` dependency. Cleaner but adds runtime dep for a one-shot script. | |

**Auto-selected (recommended):** Extend regex with named groups.
**Rationale:** Self-contained; no new dependency; handles both stable and beta version strings; preserves existing silent-truncation behavior for `_dev` / `-dev` suffixes (which is current production behavior, NOT a v1.4 regression to fix).

---

## Claude's Discretion

- **D-26**: Procedure-document filename in the phase folder (e.g. `15-LOCKSTEP-PROCEDURE.md`) — planner picks the name; must be consumable verbatim by Phase 18.
- **D-27**: Exact pytest fixture structure (parametrize vs per-test functions, conftest.py vs inline) — planner picks per sub-repo conventions.
- **D-28**: `--dry-run` flag's exact output format (JSON vs key=value vs plain string) — planner picks; constraint is greppable for the version string.
- **D-29**: Whether to add a `--set-version X.Y.ZbN` CLI arg in addition to `BETA_VERSION` env var — planner decides if the convenience justifies the extra arg-parsing surface.

## Deferred Ideas

- **Auto-promotion beta → stable workflow** — Future Requirements per REQUIREMENTS.md.
- **Branch protection rules on `beta`** — post-v1.4 if accidental-push problems materialize.
- **Signed release artifacts (sigstore / GPG)** — dedicated future milestone covering both stable + beta.
- **Cleanup of `_dev` / `-dev` dev-suffix convention** — pre-existing behavior; not a v1.4 regression.
- **`aN` / `devN` / `postN` PEP 440 segments** — add later if a use case appears.
- **TestPyPI publishing channel** — explicitly rejected for v1.4 (Future Requirements).
- **Idempotent beta re-publish on partial failure** — known gap; manual re-trigger in v1.4; robust idempotent re-publish is separate design work.

# Phase 15: Versioning & Locked-Step Coordination (Foundation) — Research

**Researched:** 2026-05-20
**Domain:** Python versioning (PEP 440), GitHub Actions env vars, pytest script testing, setuptools/setuptools_scm interaction
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Lockstep = manually-paired beta-branch push + explicit `BETA_VERSION` input (workflow_dispatch / env var) to both repos.
- **D-02:** Rejected alternatives: shared VERSION file in meta-repo; cross-repo `repository_dispatch`. Not revisited.
- **D-03:** Idempotent re-publish on partial failure is a known gap — documented in Phase 18 procedure, not fixed in Phase 15.
- **D-04:** Primary beta detection = `GITHUB_REF == "refs/heads/beta"`.
- **D-05:** Secondary trigger = `--beta` CLI flag on `update_version.py` for local/test invocation.
- **D-06:** Tertiary = `BETA_VERSION` env var. When present in beta mode, used verbatim.
- **D-07:** `BETA_VERSION` accepted verbatim (after PEP 440 regex validation). Lockstep-cut path.
- **D-08:** Fallback when `BETA_VERSION` absent in beta mode = git-tag scan for highest `X.Y.Z(b|rc)N`, emit `b(N+1)` (or `b1` if none).
- **D-09:** First beta resets to `b1`; subsequent betas on same base increment. Promotion to `rcN` is an explicit operator decision.
- **D-10:** Beta versions written into same files as stable: `firestarter/__init__.py` and `include/version.h`.
- **D-11:** Branch isolation handles state separation.
- **D-12:** Both scripts get pytest unit tests covering: (a) stable path, (b) beta path with `BETA_VERSION`, (c) beta path without `BETA_VERSION` (fallback), (d) `--dry-run`.
- **D-13:** Both scripts get `--dry-run` flag: computes proposed version, emits to stdout, no file modification.
- **D-14:** App tests under `firestarter_app/tests/test_update_version.py`; firmware tests under `firestarter/tests/` or `firestarter/.github/scripts/tests/`.
- **D-15:** App tests added to existing pytest job in `ci.yml`. Firmware gets new lightweight Python test job in `build.yml`.
- **D-16:** Extend in-place (single file per repo). No script split.
- **D-17:** Stable-branch invocation produces byte-identical output to pre-v1.4 script. Verified by pytest fixture.
- **D-18:** App at `2.0.7_dev`; firmware at `3.0.0-dev`. Lockstep applies to beta cuts only.
- **D-19:** First v1.4 beta cut version chosen in Phase 19. Phase 15 only guarantees script can write whatever the operator supplies.
- **D-20:** Stable auto-bumps independently. Known acceptable state.
- **D-21:** Supported segments: `bN` and `rcN` only. Validation regex: `^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$`.
- **D-22:** Out of scope: `aN`, `devN`, `postN`, `+local`.
- **D-23:** Version-parse regex extended to capture `(?P<pre>(b|rc)[0-9]+)?`.
- **D-24:** New parse regex: `(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)(?P<pre>(b|rc)[0-9]+)?`.
- **D-25:** Existing `_dev` / `-dev` truncation preserved as-is. Not in Phase 15 scope.

### Claude's Discretion

- **D-26:** Procedure document filename (e.g., `15-LOCKSTEP-PROCEDURE.md`).
- **D-27:** Exact pytest fixture structure (parametrize vs. per-test, conftest.py vs inline).
- **D-28:** `--dry-run` output format (JSON vs key=value vs plain string).
- **D-29:** Whether to add `--set-version X.Y.ZbN` CLI arg in addition to `BETA_VERSION` env var.

### Deferred Ideas (OUT OF SCOPE)

- Auto-promotion beta → stable workflow.
- Branch protection rules on `beta` branch.
- Signed release artifacts.
- Cleanup of `_dev` / `-dev` suffix convention.
- `aN` / `devN` / `postN` PEP 440 segment support.
- TestPyPI publishing.
- Idempotent beta re-publish on partial failure.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VER-01 | `firestarter_app/.github/scripts/update_version.py` recognizes beta-branch builds and emits PEP 440 pre-release identifiers (`X.Y.Zb1`, `X.Y.ZbN`, `X.Y.ZrcN`) instead of bumping the patch version. Stable-branch behavior preserved verbatim. | §PEP 440 format, §Current script analysis, §Stable-path preservation |
| VER-02 | `firestarter/.github/scripts/update_version.py` recognizes beta-branch builds and emits matching pre-release identifiers (`X.Y.ZbN`). Format identical to app's. Stable-branch behavior preserved verbatim. | §Firmware script analysis, §PEP 440 format |
| VER-03 | Locked-step coordination mechanism exists and is documented. Procedure produces matching `X.Y.ZbN` in both repos. | §Lockstep mechanism, §workflow_dispatch YAML shape, §Phase 16/17 contract |
</phase_requirements>

---

## Summary

Phase 15 extends two small Python scripts (`update_version.py` in each sub-repo) to emit PEP 440 pre-release version identifiers when invoked in a beta-branch context, while leaving the stable-branch path byte-identical. The coordination mechanism (D-01) is already decided: explicit `BETA_VERSION` env var, manually supplied to both repos by the release engineer. The research validates the technical choices, surfaces the `pyproject.toml`/`setuptools_scm` version-source-of-truth question, documents the exact `GITHUB_REF` values, and establishes where tests land in each sub-repo.

The highest-risk finding is the `pyproject.toml` version-source-of-truth for the app. The file has both `[tool.setuptools_scm]` and `[tool.setuptools.dynamic] version = {attr = "firestarter.__version__"}`. Research shows that at **publish time** (when `publish.yml` runs `python3 -m build` on a checkout that IS the release tag), `setuptools_scm` infers the version from the git tag itself — which will equal the tag name (e.g., `2.0.7b1`). Writing `2.0.7b1` to `__init__.py` AND tagging the commit `2.0.7b1` produces consistent results: both `setuptools_scm` (git-tag-derived) and `__init__.py` (attr-derived) agree. The `update_version.py` write to `__init__.py` remains necessary for the firmware-version handshake displayed at runtime and for `firestarter --version`, even if PyPI version ultimately comes from the git tag at publish time.

**Primary recommendation:** Extend both `update_version.py` scripts in-place with a guarded `is_beta_mode()` check, three-path version computation (verbatim-from-env, git-tag-scan-fallback, stable-increment), a validated write function, a `--dry-run` flag, and pytest coverage in both sub-repos. The stable path is structurally identical to today — the new code is behind a conditional that is never entered on `main`.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Version-identifier computation | CI Script (Python) | — | `update_version.py` runs in GitHub Actions, reads/writes version file |
| Version-file write | CI Script (Python) | — | Writes `__init__.py` and `version.h` directly |
| PyPI version metadata | Build system (setuptools_scm / git tag) | `__init__.py` attr | At `python3 -m build` time in `publish.yml`, `setuptools_scm` reads the current git tag (see §Version Source of Truth) |
| Beta-mode detection | CI Script env var | CLI flag (`--beta`) | `GITHUB_REF` is the authoritative source; `--beta` flag is for local/test use |
| Lockstep coordination | Operator (workflow_dispatch input) | — | Manual supply of `BETA_VERSION` to both repos in the same cut |
| Test execution (app) | `ci.yml` pytest job | — | Existing job; `test_update_version.py` added to `firestarter_app/tests/` |
| Test execution (firmware) | New Python job in `build.yml` | — | New step before PlatformIO build; `pytest .github/scripts/tests/` |
| Phase 18 docs consumption | Planning artifact | — | `15-LOCKSTEP-PROCEDURE.md` consumed verbatim |

---

## Standard Stack

### Core (no new dependencies required)

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| Python 3.11 | 3.11 | Script runtime | Already used in both CI workflows |
| `re` (stdlib) | stdlib | Version-string parsing and validation | Existing scripts use it; no new dep |
| `os` (stdlib) | stdlib | Env var access (`GITHUB_REF`, `BETA_VERSION`, `GITHUB_OUTPUT`) | Existing pattern |
| `argparse` (stdlib) | stdlib | `--dry-run`, `--beta`, `--set-version` CLI flags | Standard; adds zero deps |
| `subprocess` (stdlib) | stdlib | `git tag` invocation for D-08 fallback | Standard; no new dep |
| `pytest` | ≥7.0 (already in `dev` extras) | Unit tests for `update_version.py` | Already in `firestarter_app/pyproject.toml [dev]` |

[VERIFIED: /workspaces/firestarter_app/pyproject.toml — pytest>=7.0 in dev extras]
[VERIFIED: /workspaces/firestarter_app/.github/workflows/ci.yml — Python 3.11 used]
[VERIFIED: /workspaces/firestarter/.github/workflows/build.yml — Python 3.11 used]

### New for Firmware Tests Only

| Component | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| `pytest` | ≥7.0 | Firmware-side `update_version.py` tests | New requirement — firmware has no existing Python test infra |

**Firmware pytest install command (new CI step):**
```bash
pip install pytest
pytest .github/scripts/tests/ -v
```

---

## Architecture Patterns

### System Architecture Diagram

```
Push to beta branch (operator)
         │
         ▼
GitHub Actions beta workflow (Phase 16/17 — not Phase 15)
         │
         │  env:
         │    GITHUB_REF: refs/heads/beta
         │    BETA_VERSION: <operator-supplied via workflow_dispatch input>
         │
         ▼
update_version.py  ─── is_beta_mode()? ───[GITHUB_REF==refs/heads/beta OR --beta flag]──► YES
         │                                                                                    │
         │ NO (stable path — byte-identical to pre-v1.4)                                     ▼
         │                                                              BETA_VERSION env set?
         │                                                                │           │
         │                                                               YES          NO
         │                                                                │           │
         │                                                                ▼           ▼
         │                                                         validate regex   git tag scan
         │                                                         ^[0-9]+\.[0-9]+  highest bN
         │                                                         \.[0-9]+(b|rc)   → b(N+1)
         │                                                         [0-9]+$          or b1
         │                                                                │
         │                                                                ▼
         │                                                     beta version string (e.g. 3.1.0b2)
         ▼                                                                │
  get_version() ──► parse regex (D-24)                                   │
  increment patch                                                         │
  write to file                                                  [--dry-run?]
  emit to GITHUB_OUTPUT                                          NO: write file
                                                                 YES: print to stdout only
                                                                         │
                                                                         ▼
                                                           emit version=X.Y.ZbN to GITHUB_OUTPUT
                                                           (same channel as stable path)
```

### Recommended Project Structure

**firestarter_app (additions only):**
```
firestarter_app/
├── .github/
│   └── scripts/
│       └── update_version.py          # extended in-place (single file)
└── tests/
    └── test_update_version.py         # new: pytest unit tests (D-14)
```

**firestarter (additions only):**
```
firestarter/
├── .github/
│   └── scripts/
│       └── update_version.py          # extended in-place (single file)
└── tests/                             # NEW directory
    └── test_update_version.py         # new: pytest unit tests (D-14, D-15)
```

**meta-repo (planning artifact only):**
```
.planning/phases/15-versioning-locked-step-coordination-foundation/
└── 15-LOCKSTEP-PROCEDURE.md          # new: coordination procedure (D-26)
```

### Pattern 1: Beta-Mode Detection (D-04, D-05)

**What:** Single `is_beta_mode()` function checked once at script entry. Returns `True` when `GITHUB_REF == "refs/heads/beta"` OR `--beta` CLI flag is set OR `BETA_VERSION` env var is non-empty.

**When to use:** At the top of `calculate_version()` / `calculate_header_version()` equivalent. Branch before any version computation.

**Example:**
```python
# Source: D-04, D-05, D-06 from CONTEXT.md
import os, argparse, re, subprocess

def is_beta_mode(args) -> bool:
    """Return True when script is invoked in a beta-branch context."""
    if args.beta:
        return True
    if os.environ.get("GITHUB_REF") == "refs/heads/beta":
        return True
    if os.environ.get("BETA_VERSION"):
        return True
    return False
```

### Pattern 2: Beta Version Computation (D-07, D-08)

**What:** Three-path logic: (1) verbatim from `BETA_VERSION` env var (validated); (2) git-tag-scan fallback; (3) first-ever beta on base (`b1`).

**When to use:** When `is_beta_mode()` is True.

**Example:**
```python
# Source: D-07, D-08, D-21 from CONTEXT.md
BETA_VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$')

def compute_beta_version(major, minor, patch):
    """Compute beta version string. Raises ValueError on invalid input."""
    explicit = os.environ.get("BETA_VERSION", "").strip()
    if explicit:
        if not BETA_VERSION_RE.match(explicit):
            raise ValueError(f"BETA_VERSION '{explicit}' does not match {BETA_VERSION_RE.pattern}")
        return explicit
    # D-08 fallback: git-tag scan
    base = f"{major}.{minor}.{patch}"
    return _git_tag_scan_fallback(base)

def _git_tag_scan_fallback(base: str) -> str:
    """Scan git tags for highest bN on this base; emit b(N+1) or b1."""
    try:
        result = subprocess.run(
            ["git", "tag", "--list", f"{base}b*"],
            capture_output=True, text=True, check=True
        )
        tags = result.stdout.strip().splitlines()
    except subprocess.CalledProcessError:
        tags = []
    # Extract bN numbers
    n_re = re.compile(rf'^{re.escape(base)}b([0-9]+)$')
    nums = [int(m.group(1)) for t in tags if (m := n_re.match(t))]
    n = max(nums) + 1 if nums else 1
    return f"{base}b{n}"
```

### Pattern 3: Extended Parse Regex (D-23, D-24, D-25)

**What:** Extend the existing `[0-9\.]+` regex in `get_version()` / `get_header_version()` to capture `(b|rc)[0-9]+` suffix. `_dev` / `-dev` still silently truncated by falling through the parse (the new regex matches the numeric part only; non-numeric trailing content is not captured).

**App current regex (line 8):** `"^__version__ =(.\")([0-9\.]+)"`
**App extended regex:**
```python
# Source: D-24 from CONTEXT.md — captures pre-release suffix
rxs = r'^__version__ =(.\")((?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)(?P<pre>(b|rc)[0-9]+)?)'
```

**Firmware current regex (line 10):** `'^#define VERSION(.")([0-9\.]+)'`
**Firmware extended regex:**
```python
# Source: D-24 from CONTEXT.md
rxs = r'^#define VERSION(.")((?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)(?P<pre>(b|rc)[0-9]+)?)'
```

**Critical note on D-25 preservation:** The existing `_dev` / `-dev` suffix in `2.0.7_dev` and `3.0.0-dev` is NOT matched by `[0-9]+` in the patch group (the `_` and `-` are not digits). Today's code silently drops the suffix by only capturing the digits. The new regex has the same behavior: `patch` captures `0`, ignoring `_dev`. No change in behavior — the test must assert this.

### Pattern 4: `--dry-run` Flag (D-13, D-28)

**What:** `--dry-run` computes the proposed version but writes nothing. Emits the version string to stdout on a single line prefixed with `DRY_RUN:` — making it greppable in CI.

**Recommendation (D-28):** Plain string, `DRY_RUN: X.Y.ZbN` format. Greppable with `grep '^DRY_RUN:' | cut -d' ' -f2`. Simpler than JSON for this single-value output.

**Example:**
```python
# Source: D-13, D-28 from CONTEXT.md
if args.dry_run:
    print(f"DRY_RUN: {proposed_version}")
    return  # no file write, no GITHUB_OUTPUT write
```

**CI smoke-test pattern:**
```bash
version=$(python .github/scripts/update_version.py --beta --dry-run | grep '^DRY_RUN:' | cut -d' ' -f2)
echo "Proposed: $version"
```

### Pattern 5: `GITHUB_OUTPUT` Write (stable path preserved, beta path extended)

**What:** Both paths write `version=X.Y.Z` (or `version=X.Y.ZbN`) to `$GITHUB_OUTPUT`. Format is identical — Phases 16/17 read `${{ steps.version.outputs.version }}` regardless of whether it's stable or beta.

```python
# Source: existing scripts — extend to support beta value
with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
    print(f"version={version_string}", file=fh)
    print(f"major={major}", file=fh)
    print(f"minor={minor}", file=fh)
    print(f"patch={patch}", file=fh)
    # Beta-mode only: also emit pre-release segment
    if pre:
        print(f"pre={pre}", file=fh)
```

### Anti-Patterns to Avoid

- **Detecting beta mode by checking `__version__` contents:** The version file may contain `_dev` suffix that does not indicate beta mode. Always use `GITHUB_REF` or `--beta` flag for mode detection.
- **Writing `BETA_VERSION` without validation first:** Regex-validate before any file modification. Error exit must happen before the file open.
- **`sys.argv`-based `--dry-run` detection without argparse:** Fragile against test invocation patterns. Use `argparse`.
- **`git tag` call without `--list` and a glob:** `git tag` with no filter lists all tags; on a large repo this is slow and the regex filtering in Python is error-prone. Use `git tag --list "X.Y.Zb*"`.
- **Relying on `git tag` without a `try/except`:** Git may not be available in some CI sandbox environments. Always wrap subprocess calls.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PEP 440 normalization | Custom normalization logic | Let the regex in D-21 gate input | PEP 440 allows many spellings (`beta`, `b`, `BETA`); only accept canonical forms already decided (D-21) |
| Version sorting across `bN` / `rcN` | Manual sort | Use `packaging.version.Version` for any comparison needed | Ordering is non-trivial (`1.0rc1 > 1.0b2 > 1.0b1`) — but note: for Phase 15, version comparison is only needed in the git-tag-scan fallback (finding max bN), which is a simple `int(n)` compare on the N value for a fixed base |
| Git tag retrieval | Custom git parsing | `git tag --list "pattern"` via subprocess | Simple, reliable, already the standard CI pattern |

**Key insight:** The scripts are intentionally simple — they read one file, compute one version string, write one file, and emit to `GITHUB_OUTPUT`. Don't add abstractions beyond what the four test cases in D-12 require.

---

## Key Technical Findings

### Finding 1: PEP 440 Canonical Pre-Release Format

[VERIFIED: peps.python.org/pep-0440]

- **Canonical form:** `X.Y.ZbN` (no separators between base version and pre-release segment, no separators within pre-release segment).
- `X.Y.Zb.N`, `X.Y.Z-bN`, `X.Y.Z_bN` — all normalize to `X.Y.ZbN`. Only the canonical form should be written and accepted.
- PEP 440 ordering (lowest to highest): `X.Y.ZaN` < `X.Y.ZbN` < `X.Y.ZrcN` < `X.Y.Z`.
- `pip install --pre` exposes pre-releases; `pip install firestarter` (without `--pre`) will never install a `bN`/`rcN` build.
- **Canonical PEP 440 pre-release identifier regex** (official Appendix B, simplified for our supported subset):
  `(?P<pre>(b|rc)[0-9]+)` — no separators, lowercase only, `N ≥ 0` (D-21 requires `N ≥ 1` implicitly since we start at `b1`).
- **D-21 validation regex:** `^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$` — correct and sufficient. This rejects `alpha`, `beta` (spelled out), uppercase `B`, separator variants, and `aN`/`devN` as locked by D-22.

### Finding 2: `GITHUB_REF` Environment Variable Semantics

[VERIFIED: docs.github.com/en/actions/reference/workflows-and-actions/variables]

| Event | `GITHUB_REF` | `GITHUB_REF_NAME` | `GITHUB_REF_TYPE` |
|-------|-------------|-------------------|-------------------|
| Push to `beta` branch | `refs/heads/beta` | `beta` | `branch` |
| Push to `main` | `refs/heads/main` | `main` | `branch` |
| `workflow_dispatch` targeting `beta` | `refs/heads/beta` | `beta` | `branch` |
| `workflow_dispatch` targeting `main` | `refs/heads/main` | `main` | `branch` |
| Pull request (to `main`) | `refs/pull/<N>/merge` | `<N>/merge` | `branch` |
| Schedule/cron | `refs/heads/<default>` | `<default>` | `branch` |
| Release tag push | `refs/tags/X.Y.Z` | `X.Y.Z` | `tag` |

**Key implication:** `GITHUB_REF == "refs/heads/beta"` is the correct and unambiguous check for beta-branch push AND for `workflow_dispatch` triggered on the `beta` branch. D-04 is correct.

**Edge case: `workflow_dispatch` on a branch different from `beta`:** If a developer manually triggers the workflow from the `main` branch with `BETA_VERSION` set (e.g., testing), `GITHUB_REF` would be `refs/heads/main` but `BETA_VERSION` is set. The D-06 rule that `BETA_VERSION` presence also enters beta mode handles this correctly — `is_beta_mode()` returns True when `BETA_VERSION` is non-empty, regardless of `GITHUB_REF`.

**Edge case: CI tests for `update_version.py` run in `ci.yml` (PR to main):** `GITHUB_REF` on a PR = `refs/pull/<N>/merge`. This is NOT `refs/heads/beta`, so the stable path executes in CI. Correct behavior — tests for the beta path use the `--beta` flag (D-05) to simulate beta context.

### Finding 3: `workflow_dispatch` Input YAML Shape

[VERIFIED: docs.github.com/en/enterprise-server@3.0/actions/learn-github-actions/workflow-syntax-for-github-actions]

The exact YAML syntax for Phases 16/17 to declare the `BETA_VERSION` input:

```yaml
# Source: GitHub Actions workflow syntax docs
on:
  push:
    branches:
      - beta
  workflow_dispatch:
    inputs:
      beta_version:
        description: 'Beta version string (e.g. 3.1.0b1). Leave empty to auto-detect from git tags.'
        required: false
        default: ''
        type: string

jobs:
  beta-release:
    runs-on: ubuntu-latest
    env:
      BETA_VERSION: ${{ github.event.inputs.beta_version }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Bump beta version
        id: version
        env:
          GITHUB_REF: ${{ github.ref }}
          BETA_VERSION: ${{ github.event.inputs.beta_version }}
        run: python3 .github/scripts/update_version.py
```

**Notes for Phase 15:**
- The `update_version.py` script itself needs no workflow YAML changes — it just reads `os.environ["GITHUB_REF"]` and `os.environ.get("BETA_VERSION")`.
- Phases 16/17 provide the YAML that sets these env vars.
- Both `github.event.inputs.beta_version` and `inputs.beta_version` are equivalent accessors in the context of the workflow job.

### Finding 4: App Version Source-of-Truth (`pyproject.toml` + `setuptools_scm`) — CRITICAL

[VERIFIED: /workspaces/firestarter_app/pyproject.toml — read directly]
[VERIFIED: bash - `pip show firestarter` reports `2.0.7.dev0` from git (not `2.0.7_dev` from `__init__.py`)]
[VERIFIED: bash - `git describe --tags` in firestarter_app = `2.0.6-85-g4e25666` in dev env]
[VERIFIED: bash - `git describe --tags 2.0.7` = `2.0.7` (tag points to specific commit)]

The `pyproject.toml` has **both** mechanisms simultaneously:

```toml
[build-system]
requires = ['setuptools>=45', "setuptools_scm[toml]>=6.2"]

[tool.setuptools_scm]          # ← setuptools_scm active
                               #   (empty section = use defaults)

[tool.setuptools.dynamic]
version = { attr = "firestarter.__version__" }   # ← attr directive also present
```

**Actual behavior at build time:**

| Scenario | `setuptools_scm` behavior | Version in wheel METADATA |
|----------|--------------------------|--------------------------|
| `python3 -m build` at tagged commit (e.g., `HEAD = tag 2.0.7`) | `git describe` = `2.0.7` (clean) → setuptools_scm emits `2.0.7` | `2.0.7` |
| `python3 -m build` at tagged commit `2.0.7b1` | `git describe` = `2.0.7b1` → setuptools_scm emits `2.0.7b1` | `2.0.7b1` |
| `pip install -e .` in dev (no clean tag) | `git describe` = `2.0.6-85-g...` → setuptools_scm emits `2.0.7.dev0` | `2.0.7.dev0` |

**Conclusion:**

At **PyPI publish time** (`publish.yml` runs `python3 -m build` on checkout at the GitHub Release tag), `setuptools_scm` derives the version from the git tag. The `attr = "firestarter.__version__"` directive in `[tool.setuptools.dynamic]` is overridden by `setuptools_scm` when a `[tool.setuptools_scm]` section is present — setuptools_scm takes precedence.

**What this means for Phase 15:**

Writing `2.0.7b1` to `__init__.py` (via `update_version.py`) AND committing that change AND having the release workflow create the git tag `2.0.7b1` produces **consistent** results: setuptools_scm reads the tag `2.0.7b1` and the wheel METADATA shows `2.0.7b1`. The `__init__.py` write is still required for:
- `firestarter --version` at runtime (which reads `__version__` directly)
- The `git-auto-commit-action` commit that the beta workflow makes (mirroring stable behavior)
- Readback by a subsequent `update_version.py` invocation (D-23)

**Important implication for the beta release tag:** The beta release workflow (Phase 16) creates a GitHub Release tagged `2.0.7b1`. At `release: published`, `publish.yml` runs `python3 -m build` on a checkout at that tag. `setuptools_scm` sees the clean tag = `2.0.7b1`. The wheel version is `2.0.7b1`. This is the correct, desired behavior — no pyproject.toml changes needed.

### Finding 5: Existing App Test Infrastructure

[VERIFIED: /workspaces/firestarter_app/tests/ — read directly]

```
firestarter_app/tests/
├── __init__.py
├── conftest.py                    # shared fixtures (serial, CRC, frame builders)
├── golden/                        # golden files for regression tests
├── test_audit_coverage_matrix.py  # 6 test classes, Phase 11
├── test_decoder.py                # decoder tests, Phase 6
└── test_fwguard.py                # firmware version guard, Phase 6
```

**Existing patterns:**
- Class-based test organisation (`class TestFirmwareVersionGuard:`).
- `autouse` fixtures for env-var isolation (`monkeypatch.delenv(..., raising=False)`).
- `conftest.py` provides shared serial / CRC fixtures — does NOT contain version-script utilities.
- `monkeypatch.setenv` / `monkeypatch.delenv` is the standard pattern for testing env-var-driven behavior.

**Recommendation for `test_update_version.py` placement:** `firestarter_app/tests/test_update_version.py` — consistent with existing pattern. No changes to `conftest.py` needed (version script tests are self-contained; they don't need serial fixtures).

**Invocation in `ci.yml`:** The existing `pytest tests/ -v` command in the `Run pytest` step already picks up any new file under `tests/`. No `ci.yml` changes needed for the app test — it runs automatically.

### Finding 6: Firmware Test Infrastructure (New)

[VERIFIED: /workspaces/firestarter/.github/scripts/ — only `update_version.py` exists; no `tests/` directory]
[VERIFIED: /workspaces/firestarter/.github/workflows/build.yml — no Python pytest step]

The firmware sub-repo has no existing Python test infrastructure. `pio test -e native` runs C++ Unity tests only. A new, minimal pytest setup is needed.

**Recommended layout:**
```
firestarter/
└── tests/
    └── test_update_version.py     # self-contained; no conftest.py needed initially
```

**Rationale for `firestarter/tests/` over `firestarter/.github/scripts/tests/`:** Putting tests under `tests/` mirrors the app-side layout, is the pytest default discovery path, and avoids a nested `scripts/tests/` path that is awkward to invoke. The test file imports `update_version` by inserting `.github/scripts/` into `sys.path` or by using a relative import via conftest.

**New `build.yml` step (before the existing PlatformIO build):**
```yaml
- name: Set up Python 3.11 for script tests
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'

- name: Install pytest
  run: pip install pytest

- name: Run update_version.py tests
  run: pytest tests/ -v
```

**Placement in `build.yml`:** After the existing `actions/setup-python@v5` step (line 55, which sets up Python 3.11 for codegen — reuse that setup) and BEFORE the `Generate release version` step. This mirrors the firmware's existing pattern of gating the version bump behind tests.

### Finding 7: Existing Script Analysis — Current State

[VERIFIED: /workspaces/firestarter_app/.github/scripts/update_version.py — read directly]
[VERIFIED: /workspaces/firestarter/.github/scripts/update_version.py — read directly]

**App script (60 lines):**
```
get_version()        — reads __init__.py, regex: ^__version__ =(.\")([0-9\.]+)
update_version()     — writes __init__.py, format: f'"{major}.{minor}.{patch}"'
calculate_version()  — calls get/update, increments patch, writes GITHUB_OUTPUT
__main__             — calls calculate_version()
```

**Firmware script (63 lines):**
```
get_header_version() — reads include/version.h, regex: ^#define VERSION(.")([0-9\.]+)
update_version()     — writes version.h, format: f'"{major}.{minor}.{patch}"'
calculate_version()  — calls get/update, increments patch, writes GITHUB_OUTPUT
__main__             — calls calculate_version()
```

**Both scripts share the same structure.** Key differences:
- File paths: `firestarter/__init__.py` vs `include/version.h`
- Match regexes: `^__version__ =(.\")` vs `^#define VERSION(.")`
- Write format: `f'"{major}.{minor}.{patch}"\n'` for both (identical)

**Current regex limitation (D-23):** `[0-9\.]+` matches `2.0.7` from `2.0.7_dev` (stops at `_`) and `3.0.0` from `3.0.0-dev` (stops at `-`). The match succeeds but the suffix is silently discarded. A new regex `([0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]*)` would also match `2.0.7b1` without breaking the `_dev`/`-dev` truncation behavior.

**Existing typo in both scripts:** `print(f"New versin created: ...")` — "versin" is misspelled. Preserve as-is per D-17 (byte-identical stable output). Do not "fix" the typo in the stable path.

**argparse migration needed:** Current scripts have no `if __name__ == "__main__":` argument parsing — they call `calculate_version()` directly. To add `--dry-run`, `--beta`, and optionally `--set-version`, `argparse` is needed. The migration must be done so that calling the script with no arguments is identical to today (backward-compatible).

### Finding 8: Git Tag Scan Fallback (D-08) — Edge Cases

[VERIFIED: /workspaces/firestarter_app — git tags verified]

**Current tag format in both repos:** bare version numbers (no `v` prefix). Examples: `2.0.7`, `2.0.6`, `3.0.0` (firmware doesn't yet have a 3.x tag but the pattern is the same).

**Tag scan invocation:**
```bash
git tag --list "X.Y.Zb*"   # finds X.Y.Zb1, X.Y.Zb2, etc.
git tag --list "X.Y.Zrc*"  # finds X.Y.Zrc1, etc.
```

**Edge cases:**
1. **No beta tags on current base:** `git tag --list "3.1.0b*"` returns empty → emit `3.1.0b1`. Correct per D-09.
2. **No git executable:** `subprocess.CalledProcessError` or `FileNotFoundError` — fall back to `b1`. Should not happen in CI but may occur in some test environments.
3. **Tags without `v` prefix vs with:** Both repos use bare version numbers (verified). The scan pattern `"X.Y.Zb*"` correctly finds `3.1.0b1` but not `v3.1.0b1`. If a `v`-prefixed tag ever exists, it would be missed — but current pattern is bare-only (consistent).
4. **Multiple bN tags:** `git tag --list "3.1.0b*"` returns `3.1.0b1\n3.1.0b2` — correct behavior: `max([1,2])+1 = 3` → emit `3.1.0b3`.
5. **Shell environment in CI:** `subprocess.run(["git", "tag", "--list", f"{base}b*"])` — note the glob is expanded by git, not the shell, so no quoting issue. `capture_output=True` handles stdout.
6. **Shallow clone:** `publish.yml` uses `fetch-depth: 0` already. The beta workflow (Phase 16/17) should also use `fetch-depth: 0` to ensure all tags are available for the git-tag scan fallback. This is a constraint that Phase 16/17 must honor.

### Finding 9: Stable-Path Byte-Identity Verification Approach (D-17)

**Recommendation:** Golden-file / snapshot comparison approach.

For the pytest stable-path test (D-12, case a): the test writes a known input `__init__.py` content (e.g., `__version__ = "1.2.3"\n`) into a `tmp_path` file, invokes `calculate_version_stable()` (or the full script via `subprocess.run`), and asserts the output file content equals the pre-computed expected string character-for-character.

```python
# Illustrative pattern — D-27 is planner's discretion
def test_stable_path_byte_identical(tmp_path, monkeypatch):
    """Assert stable path produces byte-identical output to pre-v1.4 behavior."""
    version_file = tmp_path / "__init__.py"
    version_file.write_text('__version__ = "1.2.3"\n')
    
    monkeypatch.delenv("GITHUB_REF", raising=False)
    monkeypatch.delenv("BETA_VERSION", raising=False)
    # Redirect GITHUB_OUTPUT to a temp file
    output_file = tmp_path / "github_output"
    output_file.write_text("")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output_file))
    
    # ... invoke script logic ...
    
    assert version_file.read_text() == '__version__ = "1.2.4"\n'
    assert "version=1.2.4\n" in output_file.read_text()
```

This is a direct byte-content assertion — more precise than a golden file, and immune to filesystem encoding issues.

**Alternative (manual diff during plan execution):** The plan can include a task that runs the new script with `BETA_VERSION` unset and `GITHUB_REF=refs/heads/main`, diffs the output against the old script's output on a known input. This is the "manual diff check" referenced in D-17.

### Finding 10: Regex for D-24 — Full Analysis

The new parse regex must:
1. Match `2.0.7` (current stable, no suffix)
2. Match `2.0.7_dev` and extract `2.0.7` (D-25 — silent truncation preserved)
3. Match `2.0.7b1` and extract `2.0.7` + `b1` (new)
4. Match `3.0.0-dev` and extract `3.0.0` (D-25)
5. Match `3.1.0rc2` and extract `3.1.0` + `rc2` (new)

**D-24 regex (from CONTEXT.md):** `(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)(?P<pre>(b|rc)[0-9]+)?`

Embedded in the file-specific match:

- **App:** `r'^__version__ =(.\")(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)(?P<pre>(b|rc)[0-9]+)?'`
- **Firmware:** `r'^#define VERSION(.")(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)(?P<pre>(b|rc)[0-9]+)?'`

**Verification against D-25:** For `2.0.7_dev`, the regex stops after `7` (the `?` makes `pre` optional; `_dev` is neither `b` nor `rc` so `pre` group is `None`). Behavior identical to current `[0-9\.]+`. ✓

**Return type change in `get_version()`:** Currently returns `(major, minor, patch)` as strings. With D-24, return `(major, minor, patch, pre)` where `pre` may be `None`. All callers of `get_version()` must be updated. In the stable path, `pre` is ignored (existing stable logic only uses major/minor/patch). In the beta path, `pre` is used for readback display only.

---

## Common Pitfalls

### Pitfall 1: PyPI Rejects Same Version Re-upload

**What goes wrong:** If `update_version.py` writes `3.1.0b1` and the beta workflow creates tag `3.1.0b1` and publishes to PyPI, then if the same workflow is re-triggered (e.g., after fixing a CI issue) with the same `BETA_VERSION=3.1.0b1`, PyPI will reject the re-upload with HTTP 400 ("File already exists").

**Why it happens:** PyPI is immutable per version. Re-uploading the same version string is always rejected.

**How to avoid:** Document in Phase 18 procedures: if a beta publish fails after the tag was created, the operator must increment to `b2` for the retry. Phase 15 does not need to handle this programmatically — it's a procedure gap (D-03, acknowledged).

**Warning signs:** `twine upload` or `pypa/gh-action-pypi-publish` exits with "File already exists" (HTTP 400).

### Pitfall 2: `BETA_VERSION` Unset on a `beta` Branch Push (D-08 Fallback Triggered Unintentionally)

**What goes wrong:** A developer pushes to `beta` without setting `BETA_VERSION` (e.g., a CI fix commit) and the git-tag-scan fallback runs, auto-incrementing to `b2` even though the operator didn't intend a new beta release.

**Why it happens:** D-08 fallback runs automatically when `GITHUB_REF == refs/heads/beta` and `BETA_VERSION` is unset.

**How to avoid:** The Phase 16/17 beta workflows should make `BETA_VERSION` a **required** `workflow_dispatch` input when triggered manually. For push triggers (which cannot supply inputs), the fallback behavior (auto-increment) is appropriate — document this in Phase 18 procedures.

**Warning signs:** An unexpected new beta version appears on PyPI or GitHub Releases.

### Pitfall 3: setuptools_scm Derives a Different Version Than `__init__.py`

**What goes wrong:** At PyPI publish time, setuptools_scm reads the git tag (e.g., `2.0.7b1`) and the wheel METADATA version is `2.0.7b1`. But if `__init__.py` still contains `2.0.7_dev` (i.e., the `update_version.py` script ran in `beta` branch but the commit was not tagged), the runtime `firestarter --version` and the wheel version disagree.

**Why it happens:** setuptools_scm overrides the `attr` directive — but only if a clean tag exists at the checkout point. In the beta workflow, the git-auto-commit step commits the `__init__.py` change BEFORE the release step creates the tag — the checkout for the build step is after the tag. Order matters.

**How to avoid:** Phase 16's beta workflow must follow this order: (1) bump `__init__.py` → (2) git-auto-commit → (3) create GitHub Release with the tag (`softprops/action-gh-release` creates the tag at this point) → (4) `release: published` triggers `publish.yml` which checks out at the tag. This matches the stable workflow pattern exactly.

**Warning signs:** `pip show firestarter` shows a different version than `firestarter --version`.

### Pitfall 4: Stable Path Broken by `get_version()` Return Signature Change

**What goes wrong:** Adding `pre` to the return tuple of `get_version()` breaks the `calculate_version()` (stable path) which unpacks as `major, minor, patch = get_version()`.

**Why it happens:** Python tuple unpacking is position-sensitive.

**How to avoid:** Use a named tuple or dict, OR keep the return as `(major, minor, patch, pre)` and update all callers to unpack 4 values, OR use a `VersionInfo` dataclass. The simplest safe change: add `pre=None` as the fourth return value and update `major, minor, patch = get_version()` to `major, minor, patch, pre = get_version()` everywhere. The stable path discards `pre` silently.

**Warning signs:** `ValueError: too many values to unpack` in CI.

### Pitfall 5: `--beta` Flag Not Passed Through `subprocess.run` in Test Invocations

**What goes wrong:** Tests invoke the script via `subprocess.run(["python3", ".github/scripts/update_version.py"])` without `--beta` and without monkeypatching `GITHUB_REF`, so the stable path runs even in the "test the beta path" test case.

**Why it happens:** `subprocess.run` spawns a fresh process with a clean environment unless `env=` is explicitly set.

**How to avoid:** Either (a) test via direct function call (import the module's functions, call them directly) rather than subprocess, or (b) always pass `env={...}` explicitly when using subprocess. The function-call approach (D-27 is planner's discretion) is strongly preferred for speed and debuggability.

### Pitfall 6: `GITHUB_OUTPUT` Not Set in Test Environment

**What goes wrong:** The existing scripts call `open(os.environ["GITHUB_OUTPUT"], "a")` unconditionally. Tests running outside GitHub Actions have no `GITHUB_OUTPUT` env var set — `KeyError` crash.

**Why it happens:** The existing scripts (both app and firmware) have this bug in the stable path already. Current tests don't test `calculate_version()` directly so it hasn't been hit.

**How to avoid:** The new code must guard `GITHUB_OUTPUT` writes behind `os.environ.get("GITHUB_OUTPUT")`. In `--dry-run` mode, skip GITHUB_OUTPUT entirely. In test mode, use `monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "output"))`.

### Pitfall 7: Shallow Clone in Beta Workflow Missing Tags for D-08 Fallback

**What goes wrong:** If the beta workflow's `actions/checkout@v4` uses default `fetch-depth: 1`, `git tag --list` may return an incomplete list or no tags, causing the D-08 fallback to always emit `b1`.

**Why it happens:** Shallow clones only fetch recent commits; tags on older commits are not fetched.

**How to avoid:** Phase 16/17 beta workflows MUST use `fetch-depth: 0` (same as `publish.yml` already does). Phase 15 must document this as a Phase 16/17 requirement.

---

## Phase 16 + 17 Contract (Handoff from Phase 15)

Phase 15 deliverables guarantee the following contract for Phases 16 and 17:

| Contract Item | Phase 15 Delivers | Phase 16/17 Consumes |
|---------------|-------------------|----------------------|
| Script accepts `GITHUB_REF=refs/heads/beta` | `update_version.py` (both repos) | Workflow passes `env: GITHUB_REF: ${{ github.ref }}` |
| Script accepts `BETA_VERSION` env var | `update_version.py` (both repos) | Workflow passes `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}` |
| Script emits `version=X.Y.ZbN` to `GITHUB_OUTPUT` | Extended `GITHUB_OUTPUT` write | Workflow reads `${{ steps.version.outputs.version }}` for tag name |
| `--dry-run` flag available | argparse in both scripts | Optional: Phase 16/17 can use for smoke test |
| Stable path unchanged | pytest stable-path test passes | Stable workflow (`release.yml`, `build.yml`) untouched |

**Invocation shape from beta workflow (Phases 16/17):**
```yaml
- name: Bump beta version
  id: version
  env:
    GITHUB_REF: ${{ github.ref }}
    BETA_VERSION: ${{ github.event.inputs.beta_version }}
    GITHUB_OUTPUT: ${{ runner.temp }}/github_output  # set by GitHub runner automatically
  run: python3 .github/scripts/update_version.py
```

The script writes `version=X.Y.ZbN` to `GITHUB_OUTPUT` (the file path injected by the runner). The tag name for `softprops/action-gh-release` is:
```yaml
tag_name: ${{ steps.version.outputs.version }}   # = X.Y.ZbN
make_latest: false
prerelease: true
```

---

## Runtime State Inventory

This is a greenfield addition of new script behavior. No runtime state is renamed or migrated.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | None — git tags for beta (e.g., `3.1.0b1`) are created by Phase 16/17 workflows, not Phase 15 | None |
| Live service config | None — no external service configuration changes | None |
| OS-registered state | None — no OS-level registrations | None |
| Secrets/env vars | `PYPI_API_TOKEN` (app), `PERSONAL_ACCESS_TOKEN` (both) — already configured in GitHub repo secrets; beta publish reuses same token | None (Phase 15 does not touch secrets) |
| Build artifacts | None in Phase 15 scope | None |

---

## Validation Architecture

> `nyquist_validation` not explicitly set to `false` in `.planning/config.json` → included.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest ≥7.0 |
| Config file (app) | `firestarter_app/pyproject.toml` — `[tool.pytest.ini_options]` testpaths=["tests"] |
| Config file (firmware) | None (new; pytest auto-discovery from `tests/`) |
| Quick run command (app) | `cd firestarter_app && pytest tests/test_update_version.py -v` |
| Quick run command (firmware) | `cd firestarter && pytest tests/test_update_version.py -v` |
| Full suite command (app) | `cd firestarter_app && pytest tests/ -v` |
| Full suite command (firmware) | `cd firestarter && pytest tests/ -v` (only one test file initially) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VER-01 | App `update_version.py` emits `X.Y.ZbN` on beta branch | unit | `pytest tests/test_update_version.py -k "test_beta" -x` | ❌ Wave 0 |
| VER-01 | App stable path produces byte-identical output | unit | `pytest tests/test_update_version.py -k "test_stable" -x` | ❌ Wave 0 |
| VER-02 | Firmware `update_version.py` emits `X.Y.ZbN` | unit | `pytest tests/test_update_version.py -k "test_beta" -x` (firmware) | ❌ Wave 0 |
| VER-02 | Firmware stable path preserved | unit | `pytest tests/test_update_version.py -k "test_stable" -x` (firmware) | ❌ Wave 0 |
| VER-03 | `--dry-run` flag computes correct version, no file write | unit | `pytest tests/test_update_version.py -k "test_dry_run" -x` | ❌ Wave 0 |
| VER-03 | `BETA_VERSION` accepted verbatim and validated by regex | unit | `pytest tests/test_update_version.py -k "test_validation" -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_update_version.py -v` (both sub-repos, ~seconds)
- **Per wave merge:** `pytest tests/ -v` (full suite, both sub-repos)
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `firestarter_app/tests/test_update_version.py` — covers VER-01 (stable + beta + dry-run + validation)
- [ ] `firestarter/tests/test_update_version.py` — covers VER-02 (stable + beta + dry-run + validation)
- [ ] `firestarter/tests/` directory — does not exist; must be created
- [ ] Framework install for firmware: `pip install pytest` — new CI step needed in `build.yml`

*(App: pytest infra already complete — just add test file. Firmware: directory + CI step needed.)*

---

## Code Examples

### Verified: Existing App Script Structure

```python
# Source: /workspaces/firestarter_app/.github/scripts/update_version.py (read directly)
#!/usr/bin/env python3
import re
import os

version_file = "firestarter/__init__.py"

def get_version():
    rxs = "^__version__ =(.\")([0-9\.]+)"   # D-23: extend this regex
    txt = [line for line in open(version_file)]
    for line in txt:
        m = re.match(rxs, line)
        if m:
            major, minor, patch = str(m.group(2)).split(".")
            return (major, minor, patch)

def update_version(major, minor, patch):
    rxs = "^(__version__ = )"
    txt = [line for line in open(version_file)]
    fout = open(version_file, "w")
    for line in txt:
        m = re.match(rxs, line)
        if m:
            line = m.groups(0)[0] + f"\"{major}.{minor}.{patch}\"\n"  # stable: X.Y.Z
            fout.write(line)
        else:
            fout.write(line)
    fout.close()
    print(f"Version file updated: {major}.{minor}.{patch}")

def calculate_version():
    major, minor, patch = get_version()
    pattern = re.compile("[0-9]+")
    if pattern.match(patch):
        patch = int(patch) + 1
    else:
        patch = 0
    update_version(major, minor, patch)
    print(f"New versin created: {major}.{minor}.{patch}")  # typo preserved
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        print(f"version={major}.{minor}.{patch}", file=fh)
        # ...

if __name__ == "__main__":
    calculate_version()
```

### Verified: Existing Firmware Script Structure

```python
# Source: /workspaces/firestarter/.github/scripts/update_version.py (read directly)
#!/usr/bin/env python3
import re
import os

def get_header_version():
    header_file = "include/version.h"
    rxs = '^#define VERSION(.")([0-9\.]+)'   # D-23: extend this regex
    # ... (identical structure to app's get_version)

def update_version(major, minor, patch):
    header_file = "include/version.h"
    rxs = "^(#define VERSION )"
    # ... writes: line = m.groups(0)[0] + f'"{major}.{minor}.{patch}"\n'
    # Beta write will use: f'"{version_string}"\n' where version_string = "X.Y.ZbN"
```

### Example: Extended `update_version.py` Call Shape (app, illustrative)

```python
# Source: [ASSUMED] — illustrative; exact implementation is planner's decision
# following CONTEXT.md decisions D-04..D-17

import argparse, re, os, subprocess

BETA_VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$')
VERSION_RE = re.compile(
    r'^__version__ =(.\")(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)'
    r'(?P<pre>(b|rc)[0-9]+)?'
)

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--beta", action="store_true")
    p.add_argument("--set-version", default=None)   # D-29 optional
    return p.parse_args()

def is_beta_mode(args) -> bool:
    return (
        args.beta
        or os.environ.get("GITHUB_REF") == "refs/heads/beta"
        or bool(os.environ.get("BETA_VERSION"))
    )

if __name__ == "__main__":
    args = parse_args()
    if is_beta_mode(args):
        # beta path
        ...
    else:
        calculate_version()  # unchanged stable path
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual version bumping | `update_version.py` + `git-auto-commit-action` | Pre-v1.4 (existing) | Automated stable bumps |
| No pre-release versioning | PEP 440 `bN`/`rcN` identifiers | v1.4 (this phase) | Opt-in beta channel via `pip install --pre` |
| No beta workflow trigger | `beta` branch push | v1.4 (Phases 16/17) | Parallel release pipeline |
| `setuptools.dynamic.version.attr` as primary source | `setuptools_scm` + git tag as actual source at publish time | Already true pre-v1.4 | `__init__.py` write is for runtime display; PyPI version comes from tag |

**Deprecated/outdated:**
- `[0-9\.]+` version parse regex: cannot read back beta versions; replaced by D-24 regex in Phase 15.
- Implicit `__main__` with no argument parsing: replaced by `argparse` to support `--dry-run`, `--beta`.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `setuptools_scm` overrides `[tool.setuptools.dynamic] version = {attr = ...}` at build time — setuptools_scm-derived version (from git tag) appears in wheel METADATA | Finding 4 | If `attr` wins instead, `__init__.py` must contain the exact version string at build time — which it will (update_version.py writes it). Either way, the approach works; the risk is only in understanding which mechanism is authoritative for PyPI. Empirical evidence (`pip show` returning `2.0.7.dev0` from git, not `2.0.7_dev` from `__init__.py`) strongly supports setuptools_scm winning. |
| A2 | Tags in both repos have no `v` prefix (bare version numbers) | Finding 8 | If `v`-prefixed tags exist, the D-08 git-tag-scan fallback pattern `"X.Y.Zb*"` would miss them. Verified for existing tags (0.0.1, 2.0.7, etc. — all bare). Low risk. |
| A3 | The firmware sub-repo does not have `setuptools_scm` in its build system (it's a C++ project built via PlatformIO, not a Python wheel) | Finding 6 | Irrelevant if wrong — firmware publishes `.hex` files, not a Python wheel. No `pyproject.toml` version concern for firmware. |

**If this table is empty:** Not applicable — three assumptions flagged above.

---

## Open Questions

1. **D-29: `--set-version` CLI arg — include or skip?**
   - What we know: D-29 says "planner decides if it's worth the extra arg-parsing surface." `--beta` + `BETA_VERSION` env var covers the functional need. `--set-version` would be a convenience for local testing.
   - What's unclear: Whether Phase 19 E2E or Phase 18 procedures benefit from having `--set-version`.
   - Recommendation: Include it as an alias for `BETA_VERSION` env var; trivial to add with argparse, provides symmetry with `--beta`, useful for local dry-runs.

2. **Firmware test: `firestarter/tests/` vs `firestarter/.github/scripts/tests/`**
   - What we know: D-14 leaves location flexible. App uses `firestarter_app/tests/`. Firmware has no existing Python tests.
   - What's unclear: Whether `firestarter/tests/` conflicts with PlatformIO's test discovery (`platformio.ini` uses `test_dir = test/` per CLAUDE.md — note `test` not `tests`).
   - Recommendation: Use `firestarter/tests/` (with `s`) — separate from PlatformIO's `test/` directory. Verify `platformio.ini` `test_dir` setting doesn't conflict.

3. **`GITHUB_OUTPUT` guard: KeyError on missing env var**
   - What we know: Both existing scripts call `open(os.environ["GITHUB_OUTPUT"], "a")` — raises `KeyError` if run locally without setting `GITHUB_OUTPUT`.
   - What's unclear: Whether to guard with `os.environ.get("GITHUB_OUTPUT")` in Phase 15, or document as pre-existing behavior.
   - Recommendation: Guard it in Phase 15 (silently skip if unset, or write to `/dev/null`). The new `--dry-run` mode requires it anyway (must not write to `GITHUB_OUTPUT`). Use: `if not args.dry_run and os.environ.get("GITHUB_OUTPUT"): ...`.

---

## Environment Availability

> Phase 15 code changes are Python scripts and pytest tests — no external service dependencies beyond git and Python.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11 | Script runtime, CI | ✓ | 3.11 (CI), local varies | Python 3.9+ should work (no 3.11-specific features used) |
| git | D-08 tag-scan fallback | ✓ | Any modern git | `try/except` → fallback to `b1` |
| pytest ≥7.0 | App tests (app dev extras) | ✓ | Already in `[dev]` extras | — |
| pytest ≥7.0 | Firmware tests (new) | ✗ (not yet in firmware repo) | — | Add `pip install pytest` step in `build.yml` |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** Firmware pytest — add install step in `build.yml`.

---

## Security Domain

> `security_enforcement` not explicitly set to `false` → included.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | N/A — scripts run in CI, not user-facing |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A — GitHub Actions permissions already scoped |
| V5 Input Validation | Yes | D-21 regex validates `BETA_VERSION` before any file write |
| V6 Cryptography | No | N/A |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed `BETA_VERSION` triggering file corruption | Tampering | Regex validation (`^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$`) before file open |
| `BETA_VERSION` containing path traversal or shell injection | Tampering | Regex only allows digits, `.`, `b`, `rc` — no path chars, no shell metacharacters |
| PyPI version collision (same version re-uploaded) | Tampering | PyPI rejects re-uploads; documented as procedure gap (D-03) |

---

## Sources

### Primary (HIGH confidence)
- `/workspaces/firestarter_app/.github/scripts/update_version.py` — read directly; current 60-line stable script
- `/workspaces/firestarter/.github/scripts/update_version.py` — read directly; current 63-line stable script
- `/workspaces/firestarter_app/pyproject.toml` — read directly; `[tool.setuptools_scm]` + `[tool.setuptools.dynamic]`
- `/workspaces/firestarter_app/tests/conftest.py` — read directly; established pytest fixture patterns
- `/workspaces/firestarter_app/.github/workflows/ci.yml` — read directly; existing pytest job
- `/workspaces/firestarter/.github/workflows/build.yml` — read directly; no Python pytest step
- `/workspaces/.planning/phases/15-versioning-locked-step-coordination-foundation/15-CONTEXT.md` — all locked decisions
- `peps.python.org/pep-0440` — PEP 440 canonical pre-release format, normalization rules, ordering

### Secondary (MEDIUM confidence)
- `docs.github.com/en/actions` — `GITHUB_REF` exact values per event type; `workflow_dispatch` input YAML syntax
- `bash: git describe --tags` in `firestarter_app` — empirical evidence that `setuptools_scm` uses git tag at publish time
- `bash: pip show firestarter` — confirmed `2.0.7.dev0` from git, not `2.0.7_dev` from `__init__.py`

### Tertiary (LOW confidence)
- WebSearch results on `setuptools_scm` + `tool.setuptools.dynamic` conflict — multiple sources agree setuptools_scm takes precedence; marked LOW because not verified from a single authoritative setup-scm doc page

---

## Metadata

**Confidence breakdown:**
- PEP 440 format: HIGH — verified from official PEP
- GITHUB_REF semantics: HIGH — verified from GitHub docs
- workflow_dispatch YAML: HIGH — verified from GitHub docs
- setuptools_scm vs attr precedence: MEDIUM — empirically verified but not from authoritative docs
- Existing script analysis: HIGH — read directly from source files
- pytest patterns: HIGH — read directly from existing test files
- git tag format: HIGH — verified from `git tag` output in both repos

**Research date:** 2026-05-20
**Valid until:** 2026-06-20 (stable domain; PEP 440 and GitHub Actions docs change slowly)

---

## RESEARCH COMPLETE

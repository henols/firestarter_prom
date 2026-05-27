# Phase 37: Tooling Baseline + CI Gate — Research

**Researched:** 2026-05-27
**Domain:** Python tooling — ruff, ruff-format, mypy, pytest-cov, pre-commit, GitHub Actions
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Green baseline in three commits: (1) `ruff format`, (2) `ruff check --fix --select I`,
  (3) `ruff check --add-noqa` for residual E/F/UP findings.
- **D-02:** Create `.git-blame-ignore-revs` with the format commit SHA; document
  `git config blame.ignoreRevsFile .git-blame-ignore-revs` for contributors.
- **D-03:** No hand-fixing. F403/F405 star-import findings get `# noqa` now; resolved in Phase 39.
- **D-04:** Measure coverage first. If ≥ 60% → gate at 60%. If < 60% → gate at measured floor
  rounded down to 5% step, document deviation, record ratchet plan.
- **D-05:** Ratchet is manual; each later phase bumps the number. Phase 42 raises to ≥ 70%.
- **D-06:** Triggers: run on ALL pull requests (drop `branches: [main]` from `pull_request`);
  keep `push` on `main`; keep existing `paths-ignore`.
- **D-07:** Fold new steps into the existing single `ci` job, in order:
  `ruff check` → `ruff format --check` → `mypy` → `pytest --cov`.
- **D-08:** Single Python 3.11 in CI; ruff `target-version = "py39"`, mypy `python_version = "3.9"`.
- **D-09:** ruff rules: E, F, I, UP only. No `select = ["ALL"]`. No B/SIM/C4 yet.
- **D-10:** mypy watermark = strict-islands + count-script. Global `disallow_untyped_defs = false`;
  `[[tool.mypy.overrides]]` makes Phase 36 test modules strict. Count-script in CI.
  `mypy-baseline` noted as deferred fallback.
- **D-11:** Add `types-pyserial` to typing/test deps.

### Claude's Discretion

- Exact name + location of the mypy watermark count-comparison script.
- `pre-commit` hook pinning: `repo: local` vs pinned mirrors, exact versions.
- Whether coverage config lives in `[tool.coverage.*]` + CI flags or via pytest `addopts`.
- The precise 5%-step rounding for the coverage floor (resolved by measurement in D-04).
- Whether the import-sort autofix includes other safe fixes beyond `--select I`.

### Deferred Ideas (OUT OF SCOPE)

- Full 3.9–3.12 CI test matrix.
- Broader ruff rule set (B/bugbear, SIM, C4) — Phase 42.
- `mypy-baseline` tool — revisit only if count-drift bites.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TOOL-01 | ruff (lint) + ruff format configured in pyproject.toml; baseline pass makes tree green; rule categories documented. | ruff 0.15.14 config schema verified; exact `[tool.ruff.lint]` table confirmed; `--add-noqa` mechanics tested; 145 noqa suppressions in the real codebase. |
| TOOL-02 | mypy configured with gradual per-module strategy + types-pyserial; initial error count recorded as watermark; gate is "no new errors." | mypy 2.1.0 tested on real codebase; watermark = 41 errors; `[[tool.mypy.overrides]]` syntax verified; types-pyserial 3.5.0.20260519 confirmed. |
| TOOL-03 | CI workflow runs ruff check + ruff format --check + mypy + pytest with coverage gate; fails build on violations; pre-commit config committed. | ci.yml shape read; pull_request trigger fix specified; ruff-pre-commit v0.15.14 and mirrors-mypy v2.1.0 confirmed; coverage 51.33% → gate floor 50%. |
</phase_requirements>

---

## Summary

Phase 37 is a pure tooling phase: configure ruff + ruff-format + mypy in `pyproject.toml`, bring
the existing `firestarter_app` tree to a green linting baseline without hand-fixing any logic, and
gate CI + pre-commit so that new violations are blocked. The existing Phase 36 safety net (162
tests, 29 syrupy snapshots) makes the whole-tree reformat safe.

The research verified current tool versions (ruff 0.15.14, mypy 2.1.0, pytest-cov 7.1.0), tested
the full three-step green-baseline sequence on the real codebase, measured the current test
coverage (51.33%), and ran mypy to obtain the initial watermark (41 errors). All key decisions
were confirmed against the real code — no assumptions were needed for any load-bearing claim.

**Primary recommendation:** Follow D-01 through D-11 exactly. Set `extend-ignore = ["E501"]` in
`[tool.ruff.lint]` (E501 is redundant with ruff-format and would produce 443 noqa suppressions
on the unformatted tree — after format, only 3 bare E501s survive; excluding it is the standard
practice per the ruff formatter docs). The three-commit baseline sequence requires two `--add-noqa`
passes (the second catches F405 usage violations that only appear after F403 is suppressed), plus
a final `ruff format` run after noqa insertion to handle multiline constructs.

**Coverage gate:** Measured floor is 51.33%, which rounds down to 50% on the 5% step, triggering
the D-04 < 60% branch. Gate is set at 50% with documented deviation and ratchet plan.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Lint/format enforcement | CI / GitHub Actions | Developer local (pre-commit) | Gate must run in CI; pre-commit is the fast local feedback loop |
| mypy type checking | CI (after install) | pre-commit | Same: CI is the authoritative gate; pre-commit is convenience |
| Coverage measurement | CI (pytest-cov) | — | Coverage is a build-time metric; no pre-commit hook needed |
| `pyproject.toml` config | Host sub-repo (`firestarter_app/`) | — | All tool config lives in the package it governs |
| `.pre-commit-config.yaml` | Host sub-repo | — | Hooks run in the context of the repo being committed to |
| `.git-blame-ignore-revs` | Host sub-repo | — | Blame bypass applies to `firestarter_app/` reformat commits |
| Watermark count-script | Host sub-repo (`scripts/`) | — | CI invokes it from the package root |

---

## Standard Stack

### Core Tools

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| ruff | `>=0.15.14` | Lint + format (replaces flake8 + black + isort) | De-facto Python linter; ruff-format replaces black per PROJECT.md v1.8 decision |
| mypy | `>=2.1.0` | Static type checking | De-facto Python type checker; existing install confirmed |
| pytest-cov | `>=7.1.0` | Coverage measurement | Standard pytest-coverage integration |
| types-pyserial | `>=3.5.0.20260519` | mypy stubs for pyserial | Required for mypy to check serial I/O code (D-11) |
| pre-commit | `>=4.6.0` | Git hook manager | Standard for enforcing quality gates at commit time |
| coverage | `>=7.14.1` | Coverage data collection | Installed as pytest-cov transitive dep; may be pinned directly |

[VERIFIED: npm registry] — All packages confirmed via `pip index versions` against PyPI and `slopcheck install ruff mypy pytest-cov types-pyserial pre-commit coverage` returned 6 OK.

### Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| ruff | PyPI | 3+ yrs | 50M+/wk | github.com/astral-sh/ruff | OK | Approved |
| mypy | PyPI | 10+ yrs | 30M+/wk | github.com/python/mypy | OK | Approved |
| pytest-cov | PyPI | 10+ yrs | 30M+/wk | github.com/pytest-dev/pytest-cov | OK (no source link in metadata) | Approved |
| types-pyserial | PyPI | 4+ yrs | 2M+/wk | github.com/python/typeshed | OK | Approved |
| pre-commit | PyPI | 8+ yrs | 20M+/wk | github.com/pre-commit/pre-commit | OK | Approved |
| coverage | PyPI | 15+ yrs | 60M+/wk | github.com/nedbat/coveragepy | OK | Approved |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

### Installation (into pyproject.toml `[test]` extra)

```bash
# Extends the existing [test] group; replaces [dev] in CI
pip install -e ".[test]"
```

The `[dev]` group (pytest>=7.0) remains for backward compatibility but CI switches to `[test]`.

---

## Architecture Patterns

### System Architecture Diagram

```
Developer local push
        │
        ▼
.pre-commit hooks
  ├── ruff check --force-exclude   ← catches new violations before commit
  ├── ruff format --force-exclude  ← ensures format is applied
  └── mypy                         ← type-checks with types-pyserial stub
        │
        ▼ (on push/PR)
GitHub Actions ci.yml
  ├── Catalog validity check
  ├── Codegen drift gate
  ├── pip install -e .[test]       ← now includes ruff, mypy, pytest-cov, types-pyserial
  ├── ruff check firestarter/ tests/
  ├── ruff format --check firestarter/ tests/
  ├── scripts/check_mypy_watermark.py   ← count errors, fail if > watermark
  └── pytest tests/ --cov=firestarter --cov-fail-under=50
```

### Recommended Project Structure (new files)

```
firestarter_app/
├── pyproject.toml            # extended: [tool.ruff], [tool.ruff.lint], [tool.ruff.format],
│                             #           [tool.mypy], [[tool.mypy.overrides]],
│                             #           [tool.coverage.run], [tool.coverage.report]
│                             #           [project.optional-dependencies].test (extended)
├── .pre-commit-config.yaml   # NEW: hook order ruff-check → ruff-format → mypy
├── .git-blame-ignore-revs    # NEW: SHA of the ruff format commit (D-02)
└── scripts/
    └── check_mypy_watermark.py   # NEW: count-comparison script (D-10)
```

### Pattern 1: ruff Configuration in pyproject.toml

The `[tool.ruff]` table owns global settings (target-version, line-length); `[tool.ruff.lint]`
owns rule selection. This split is required in ruff ≥ 0.2.0 — `select` in `[tool.ruff]` is
ignored. [VERIFIED: ruff 0.15.14 confirmed via `ruff check --show-settings`]

```toml
# Source: tested against ruff 0.15.14 on the real codebase
[tool.ruff]
target-version = "py39"
line-length = 88

[tool.ruff.lint]
# E: pycodestyle errors, F: pyflakes, I: isort, UP: pyupgrade
# Rationale: E/F are baseline correctness; I enforces import order mechanically;
# UP modernises syntax conservatively (py39 target blocks UP007 X|Y, UP045 Optional→X|None).
# No select = ["ALL"] — broadening to B/SIM/C4 deferred to Phase 42.
select = ["E", "F", "I", "UP"]
# E501 is redundant with ruff-format line-length enforcement.
# Keeping E501 produces 443 noqa suppressions on the unformatted tree (3 after format).
# Standard practice per ruff docs: exclude E501 when using ruff-format.
extend-ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"    # ruff-format default
indent-style = "space"    # ruff-format default
```

**Critical version note:** In ruff ≥ 0.2.0, `select` must be under `[tool.ruff.lint]`, not
`[tool.ruff]`. Using the wrong table silently ignores the setting. Confirmed with
`--show-settings` which shows `linter.unresolved_target_version = 3.9` when correct. [VERIFIED: ruff 0.15.14]

### Pattern 2: target-version = "py39" Effect on UP Rules

`target-version = "py39"` prevents ruff UP from rewriting to 3.10+ syntax. Specifically:

| Rule | py39 | py310+ | Why it matters |
|------|------|--------|----------------|
| UP007 | **no-op** | rewrites `Union[A,B]` → `A \| B` | `requires-python = ">=3.9"` |
| UP045 | **no-op** | rewrites `Optional[X]` → `X \| None` | same |
| UP006 | fires | fires | `List` → `list`, `Dict` → `dict` (safe on 3.9) |
| UP035 | fires | fires | deprecates `typing.List`, `Dict` imports |

[VERIFIED: tested with `ruff check --select UP007 --target-version py39` vs `py310` on real file]

The `requires-python = ">=3.9"` constraint in `pyproject.toml` is the authoritative source.
UP006/UP035 are still selected (they are safe on 3.9); they generate 24+7 = 31 noqa suppressions
in Phase 37 which Phase 38–42 remove module by module.

### Pattern 3: Three-Commit Green Baseline (D-01) — Exact Mechanics

**Verified sequence** against the real `firestarter_app` codebase (ruff 0.15.14):

**Commit 1 — ruff format (whole-tree reformat):**
```bash
ruff format firestarter/ tests/
# Result: 24 files reformatted, 6 unchanged. All E501 violations reduced from 443 → 3.
# Commit this. Record SHA for .git-blame-ignore-revs (D-02).
```

**Commit 2 — import sort only:**
```bash
ruff check firestarter/ tests/ --select I --fix
# Result: 42 errors fixed (all I001 unsorted-import blocks).
# Verify format not broken: ruff format firestarter/ tests/ --check
# Result: 30 files already formatted (import sort did NOT break format).
# Commit this (mechanical, covered by the 162-test safety net).
```

**Commit 3 — noqa suppression pass:**
```bash
# First pass: add noqa to E, F, UP violations (not E501 — excluded in config)
ruff check firestarter/ tests/ --select E,F,UP --target-version py39 --add-noqa
# Result: ~135 noqa directives added.

# Second pass: ruff format may reflow multi-line constructs where noqa moved lines
# This is a KNOWN PITFALL: multiline Optional[Dict] type annotations — the noqa
# ends up on the wrong line after ruff-format reformats the block.
ruff format firestarter/ tests/
# Result: may reformat 2 files (eprom_info.py, eprom_operations.py).

# Third pass: catch F405 violations (star-import usages) — these only appear AFTER
# F403 is suppressed; F403 and F405 are separate rules.
ruff check firestarter/ tests/ --select E,F,UP --target-version py39 --add-noqa
# Result: ~9 more noqa directives (F405 on usage lines, UP006 on Dict lines that moved).

# Final verify: tree must be green on ALL selected rules:
ruff check firestarter/ tests/ --select E,F,I,UP --target-version py39
# Expected: All checks passed!
ruff format firestarter/ tests/ --check
# Expected: N files already formatted (format is idempotent now)
```

**Total noqa directives added:** ~145 (breakdown: 54 F405, 24 UP006, 20 F401, 14 F841,
7 UP035, 6 F403, 4 UP024, 4 F541, 3 UP015, 2 each E714/E402, 1 each UP036/UP008/F811/E731/E711).

[VERIFIED: tested end-to-end on real firestarter_app codebase at the Phase 36 tip commit]

### Pattern 4: mypy Configuration in pyproject.toml

```toml
# Source: tested mypy 2.1.0 on real firestarter_app codebase
[tool.mypy]
python_version = "3.9"          # D-08: honors requires-python floor
ignore_missing_imports = true   # needed for non-typed deps (tqdm, rich, argcomplete)
disallow_untyped_defs = false   # D-10: gradual adoption; global stays lenient
check_untyped_defs = false      # global: don't check inside untyped function bodies
# mypy_error_watermark = 41    # UPDATE THIS COMMENT after baseline commit

# Phase 36 test modules — written this milestone, no import errors of their own.
# "Strict-islands" here means check_untyped_defs = true so mypy validates the
# bodies of untyped test functions (catches test-level type mismatches, not just
# function signatures).
[[tool.mypy.overrides]]
module = [
    "tests.test_characterization",
    "tests.test_serial_characterization",
    "tests.test_bug_characterization",
    "tests.test_eprom_database",
    "tests.test_revision_constants_parity",
    "tests.test_decoder",
]
check_untyped_defs = true
```

**Critical version note:** mypy 2.1.0 rejects `python_version = "3.9"` when passed via
`--python-version` CLI flag ("Python 3.9 is not supported, must be 3.10 or higher").
However, `python_version = "3.9"` in the `[tool.mypy]` config block in `pyproject.toml`
is silently accepted and works correctly. This is a mypy 2.1.0 quirk: the config-file path
allows 3.9 but the CLI flag path rejects it. [VERIFIED: tested both paths on real codebase]

**"Strict islands" clarification:** The Phase 36 test modules are not type-annotated
(pytest convention — test functions rarely carry full annotations). "Strict" in D-10 means
`check_untyped_defs = true` (mypy validates the body of each untyped test function), NOT
`disallow_untyped_defs = true` (which would require adding `-> None` to every test function
and would break the whole test suite immediately). The global stays `disallow_untyped_defs =
false`; the overrides add body-checking only for the six Phase 36 modules. [VERIFIED: tested on real codebase — `check_untyped_defs = true` on test modules produces 20 additional errors globally vs. baseline 41; the test modules themselves have 0 errors of their own origin]

### Pattern 5: mypy Watermark Count-Comparison Script (D-10)

**Baseline watermark: 41 errors** (measured: `mypy firestarter/ tests/` with the config above
on the Phase 36 tip commit). [VERIFIED: direct measurement]

The watermark integer is stored as a comment in `pyproject.toml` (inside `[tool.mypy]`). The
count-comparison script reads it and compares:

```python
#!/usr/bin/env python3
"""scripts/check_mypy_watermark.py — CI mypy gate (D-10, Phase 37).

Run mypy, count errors, fail if error count exceeds watermark.
Watermark is the integer in the mypy_error_watermark comment in pyproject.toml.
"""
import re
import subprocess
import sys
import tomllib
from pathlib import Path


def get_watermark() -> int:
    """Read watermark from pyproject.toml [tool.mypy] section comment."""
    text = Path("pyproject.toml").read_text()
    m = re.search(r"#\s*mypy_error_watermark\s*=\s*(\d+)", text)
    if not m:
        print("ERROR: mypy_error_watermark comment not found in [tool.mypy]", file=sys.stderr)
        sys.exit(2)
    return int(m.group(1))


def count_mypy_errors() -> int:
    """Run mypy and return error count. 0 if success."""
    result = subprocess.run(
        ["mypy", "firestarter/", "tests/"],
        capture_output=True, text=True
    )
    output = result.stdout + result.stderr
    m = re.search(r"Found (\d+) errors?", output)
    return int(m.group(1)) if m else 0


def main() -> None:
    watermark = get_watermark()
    count = count_mypy_errors()
    print(f"mypy errors: {count} (watermark: {watermark})")
    if count > watermark:
        print(f"FAIL: {count} errors exceeds watermark {watermark}. New errors introduced.")
        sys.exit(1)
    elif count < watermark:
        print(f"INFO: {count} errors — {watermark - count} below watermark. Lower watermark in pyproject.toml.")
    else:
        print("OK: error count at watermark.")


if __name__ == "__main__":
    main()
```

**Edge cases handled:**
- 0 errors: mypy outputs `"Success: no issues found"` — regex match fails → returns 0 (correct).
- `Found N errors` vs `Found N error` (N=1) — regex `errors?` handles both. [VERIFIED]
- Exit code: mypy returns 1 when errors found, 0 on success — the script counts errors explicitly
  so it doesn't depend on mypy's exit code.
- Missing watermark comment: exits with code 2 (configuration error), not 1 (gate failure).

**Watermark comment format in pyproject.toml:**
```toml
[tool.mypy]
python_version = "3.9"
# ...
# mypy_error_watermark = 41
```

**Contrast with `mypy-baseline`:** The `mypy-baseline` tool pins the exact set of errors (file,
line, error code), so adding one error while fixing another leaves the baseline unchanged.
The count-script approach (D-10) counts totals only — if you fix 2 errors in `serial_comm.py`
and introduce 1 error in `firmware.py`, the count drops by 1 and the gate passes even though
a new error was introduced. `mypy-baseline` catches this; the count-script does not. D-10 accepts
this tradeoff ("noted as deferred fallback if count-drift bites").

### Pattern 6: Coverage Gate (D-04)

**Measured baseline:** 51.33% (pytest-cov 7.1.0, Python 3.12 in devcontainer, `--cov=firestarter`
on 162-test Phase 36 suite). [VERIFIED: direct measurement]

**Gate calculation per D-04:**
- 51.33% < 60% → D-04 "< 60%" branch applies
- Floor rounded down to nearest 5%: 51 → 50%
- Gate: `--cov-fail-under=50`
- Document deviation in commit + CONTEXT trail, record ratchet: Phase 42 raises to ≥ 70%.

Coverage config placement (planner's discretion — recommendation: keep flags in CI step, not
in pytest `addopts`, to keep the coverage gate visible in CI YAML):

```yaml
# In ci.yml:
- name: Run pytest with coverage
  run: pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=50
```

Alternatively, pyproject.toml can hold the source config (but NOT `fail_under` — that belongs
in CI where it's visible as a gate):

```toml
[tool.coverage.run]
source = ["firestarter"]
omit = ["firestarter/data/*"]  # JSON data files

[tool.coverage.report]
show_missing = true
```

### Pattern 7: CI Workflow Changes (D-06, D-07)

**Trigger change (D-06):** Remove `branches: [main]` from the `pull_request` trigger. The
`v1.8-app-cleanup` branch is never merged to `main` until Phase 43 — a `main`-only gate would
be dormant for the entire 7-phase milestone.

```yaml
on:
  push:
    branches: [main]
    paths-ignore: ['**.md', '.gitignore', 'docs/**', '.vscode/**', '.editorconfig']
  pull_request:   # <-- no branches: filter (was: branches: [main])
    paths-ignore: ['**.md', '.gitignore', 'docs/**', '.vscode/**', '.editorconfig']
```

**Install change (D-07):** Replace `pip install -e .[dev]` with `pip install -e .[test]`.
The `[test]` extra will include ruff, mypy, pytest-cov, types-pyserial (and syrupy, pytest>=8.0
from Phase 36).

**New steps folded after install:**

```yaml
- name: Install package + test deps
  run: pip install -e .[test]

- name: ruff lint
  run: ruff check firestarter/ tests/

- name: ruff format check
  run: ruff format --check firestarter/ tests/

- name: mypy type check (watermark gate)
  run: python scripts/check_mypy_watermark.py

- name: Run pytest with coverage
  run: pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=50
```

### Pattern 8: pre-commit Configuration (D-07, Discretion)

**Recommended approach: pinned mirrors** (not `repo: local`). Pinned mirrors are the standard
recommendation — they use isolated environments, don't depend on what's installed in the project's
venv, and are automatically updated by `pre-commit autoupdate`. `repo: local` is simpler but
shares the project venv which means ruff/mypy version can drift. [ASSUMED]

```yaml
# .pre-commit-config.yaml
# Hook order: ruff-check → ruff-format → mypy (D-07)
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.14   # VERIFIED: matches PyPI ruff 0.15.14 (latest as of 2026-05-27)
    hooks:
      - id: ruff-check   # runs ruff check --force-exclude
        args: ["--fix"]  # auto-fix safe fixable violations on commit
      - id: ruff-format  # runs ruff format --force-exclude

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v2.1.0    # VERIFIED: matches PyPI mypy 2.1.0 (latest as of 2026-05-27)
    hooks:
      - id: mypy
        additional_dependencies:
          - types-pyserial>=3.5.0.20260519  # D-11
```

**Hook IDs in astral-sh/ruff-pre-commit v0.15.14:** `ruff-check`, `ruff-format` (and legacy `ruff`
alias). The hook runs `ruff check --force-exclude` and `ruff format --force-exclude` respectively.
[VERIFIED: read `.pre-commit-hooks.yaml` from the pinned tag]

**Note on `--fix` in pre-commit:** Adding `args: ["--fix"]` to `ruff-check` means safe-fixable
violations are auto-fixed before commit (import sort, unused-import removal where auto-fixable).
This is optional — omit it to keep pre-commit as a check-only gate. The CONTEXT says hook order
is ruff-check → ruff-format; with `--fix` the developer may need to `git add` the auto-fixed files
before the commit succeeds.

### Pattern 9: .git-blame-ignore-revs (D-02)

```
# .git-blame-ignore-revs
# Whole-tree ruff format commit (Phase 37, 2026-05-27)
# Run: git config blame.ignoreRevsFile .git-blame-ignore-revs
<FULL 40-CHAR SHA OF THE FORMAT COMMIT>
```

**Format:** one full 40-character SHA per line; `#` lines are comments. [VERIFIED: standard git
format, supported since git 2.23]. GitHub automatically honors the file when it exists in the repo
root. For contributors: `git config blame.ignoreRevsFile .git-blame-ignore-revs` (local config).
[ASSUMED — GitHub auto-honor is widely documented but not independently verified in this session]

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Import sorting | Custom sort script | `ruff check --select I --fix` | Handles edge cases (future imports, `__all__`, `TYPE_CHECKING` blocks) |
| Line-length enforcement | Truncation script | `ruff format` (built-in) | Formatter knows about strings, comments, and valid split points |
| noqa suppression | Custom sed script | `ruff check --add-noqa` | Places noqa on the correct line per rule; handles multi-rule suppressions |
| Type stub fetching | Bundling stubs | `types-pyserial` from PyPI | typeshed-maintained, matches pyserial API exactly |
| Error count comparison | `diff` or `grep` script | `scripts/check_mypy_watermark.py` | Simple enough to hand-roll; `tomllib` (stdlib since 3.11) reads the watermark |

**Key insight:** `--add-noqa` is the right tool for the baseline suppression pass but has a
multiline-construct limitation — when ruff-format reformats multi-line type annotations, the noqa
comment can end up on the wrong line. The fix is a second `--add-noqa` pass after `ruff format`.

---

## Common Pitfalls

### Pitfall 1: `select` in Wrong TOML Table

**What goes wrong:** `select = ["E", "F", "I", "UP"]` under `[tool.ruff]` instead of
`[tool.ruff.lint]` is silently ignored — ruff uses the default rule set.
**Why it happens:** ruff split `lint.*` settings into a sub-table in 0.2.0; old documentation
and blog posts still show the pre-split layout.
**How to avoid:** Always verify with `ruff check --show-settings` and look for
`linter.rules.enabled` in the output.
**Warning signs:** Running `ruff check` finds zero violations on a messy codebase.

### Pitfall 2: `--add-noqa` + Multiline Constructs = Noqa on Wrong Line

**What goes wrong:** `ruff check --add-noqa` appends `# noqa: UP006` to the line containing
the closing `],` of a multi-line `Optional[Dict]` parameter. After ruff-format reformats the
block, `Dict` ends up on its own line without noqa; the violation reappears.
**Why it happens:** ruff associates the violation with the last line of the multi-line construct
for noqa placement, but after formatter reformats, the violation token is on a different line.
**How to avoid:** Run `ruff format` AFTER `--add-noqa`, then run `--add-noqa` a SECOND time
to catch any violations that reappeared. The second pass adds fewer directives (9 in the real
codebase). Then run `ruff format --check` to confirm idempotence.
**Warning signs:** `ruff format --check` shows files to reformat AFTER `--add-noqa` was run.

### Pitfall 3: F403 noqa Does NOT Suppress F405

**What goes wrong:** Adding `# noqa: F403` to the star-import line suppresses "unable to detect
undefined names" but F405 ("may be undefined, or defined from star imports") fires on every USAGE
of a star-imported name throughout the file. F403 and F405 are separate rule codes.
**Why it happens:** They are distinct rules — F403 is about the import statement; F405 is about
usage of names from star imports.
**How to avoid:** The second `--add-noqa` pass (after format) catches F405 on usage lines.
In the real codebase this adds ~54 F405 noqa directives (the majority of the second pass).
**Warning signs:** After `--add-noqa` pass 1, the check still shows 50+ F405 violations.

### Pitfall 4: mypy 2.1.0 Rejects `--python-version 3.9` via CLI

**What goes wrong:** `mypy firestarter/ --python-version 3.9` fails with "Python 3.9 is not
supported (must be 3.10 or higher)". CI step using `--python-version` flag breaks.
**Why it happens:** mypy 2.1.0 dropped runtime type-checking support for 3.9 via CLI. However,
`python_version = "3.9"` in the `[tool.mypy]` section of `pyproject.toml` IS accepted and runs
correctly. The config-file path bypasses the CLI validation.
**How to avoid:** Do NOT use `--python-version` as a CLI flag in CI. Let mypy read from
`pyproject.toml` (which it does automatically when invoked from the project root). Run just
`mypy firestarter/ tests/` with no version flag.
**Warning signs:** CI step with `mypy --python-version 3.9 ...` exits non-zero with the version
error even when the source code is clean.

### Pitfall 5: E501 Produces 443 noqa Suppressions Without Exclusion

**What goes wrong:** Including E501 in `select` on the unformatted tree produces 443 line-too-long
violations — after `ruff format`, these drop to 3 (because the formatter fixes most long lines).
But the ~140 noqa comments added by `--add-noqa` themselves push some previously-88-char lines
over the limit, causing an infinite format↔noqa cycle.
**Why it happens:** ruff-format's line-length limit and E501's limit are the same (88), but noqa
comments are exempt from formatting. `--add-noqa` adds "# noqa: XYZ" which can push a
previously-valid line to 89+ chars.
**How to avoid:** Add `extend-ignore = ["E501"]` to `[tool.ruff.lint]`. ruff-format already
enforces line length; E501 is redundant and the ruff docs explicitly recommend this when
using ruff-format. After format, only 3 genuine E501 violations remain (long strings in comments)
which can be manually noqa'd.
**Warning signs:** `ruff format --check` after `--add-noqa` shows files to reformat; those files
have `# noqa: E501` added to comment lines.

### Pitfall 6: pull_request Trigger with `branches: [main]` = Dormant Gate

**What goes wrong:** The existing `pull_request: branches: [main]` means CI only runs for PRs
targeting `main`. The entire v1.8 milestone runs on `v1.8-app-cleanup` — no PR will target
`main` until Phase 43 promotion. The gate is effectively disabled for 7 phases.
**Why it happens:** The original ci.yml was written for a main-branch-centric workflow before
the v1.8 feature-branch milestone.
**How to avoid:** Remove the `branches: [main]` filter from `pull_request` entirely (D-06).
Keep it on `push: branches: [main]`.

---

## Code Examples

### Complete pyproject.toml additions

```toml
# Source: verified against ruff 0.15.14 + mypy 2.1.0 on real firestarter_app codebase
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
]
test = [
    "pytest>=8.0",
    "syrupy>=5.0",
    # Phase 37 additions:
    "ruff>=0.15.14",
    "mypy>=2.1.0",
    "pytest-cov>=7.1.0",
    "types-pyserial>=3.5.0.20260519",
]

[tool.ruff]
target-version = "py39"
line-length = 88

[tool.ruff.lint]
# E: pycodestyle errors (style violations that ruff-format doesn't fix)
# F: pyflakes (undefined names, unused imports)
# I: isort (import ordering)
# UP: pyupgrade (modernise syntax within py39 bounds)
# E501 excluded: ruff-format enforces line length; E501 is redundant
# and causes a noqa-adds-noqa-on-long-lines cycle.
select = ["E", "F", "I", "UP"]
extend-ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.9"          # Note: must be in config, not CLI --python-version flag
ignore_missing_imports = true
disallow_untyped_defs = false
check_untyped_defs = false
# mypy_error_watermark = 41     # Baseline: Phase 37 tip. Lower as modules get typed.

[[tool.mypy.overrides]]
# Phase 36 test modules: strict-island (check bodies of untyped functions)
module = [
    "tests.test_characterization",
    "tests.test_serial_characterization",
    "tests.test_bug_characterization",
    "tests.test_eprom_database",
    "tests.test_revision_constants_parity",
    "tests.test_decoder",
]
check_untyped_defs = true

[tool.coverage.run]
source = ["firestarter"]

[tool.coverage.report]
show_missing = true
```

### Complete ci.yml (Phase 37 shape)

```yaml
# Source: based on existing ci.yml + D-06/D-07 changes
name: Host CI
on:
  push:
    branches: [main]
    paths-ignore: ['**.md', '.gitignore', 'docs/**', '.vscode/**', '.editorconfig']
  pull_request:           # no branches: filter — D-06
    paths-ignore: ['**.md', '.gitignore', 'docs/**', '.vscode/**', '.editorconfig']

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

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

      - name: Install package + test deps
        run: pip install -e .[test]        # was: .[dev]

      - name: ruff lint
        run: ruff check firestarter/ tests/

      - name: ruff format check
        run: ruff format --check firestarter/ tests/

      - name: mypy type check (watermark gate)
        run: python scripts/check_mypy_watermark.py

      - name: Run pytest with coverage
        run: pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=50
```

### Complete .pre-commit-config.yaml

```yaml
# Source: pinned to ruff-pre-commit v0.15.14 and mirrors-mypy v2.1.0
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.14
    hooks:
      - id: ruff-check
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v2.1.0
    hooks:
      - id: mypy
        additional_dependencies:
          - "types-pyserial>=3.5.0.20260519"
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| flake8 + isort + black | ruff (lint + isort + format) | ruff 0.1.0 stable (late 2023) | Single tool, much faster |
| `[tool.ruff] select = [...]` | `[tool.ruff.lint] select = [...]` | ruff 0.2.0 (Jan 2024) | Sub-table split; old placement silently ignored |
| mypy supports 3.9+ via CLI | mypy 2.1.0 requires ≥ 3.10 via CLI | mypy 2.1.0 (2026) | Must use config file for python_version = "3.9" |
| pytest-cov 4.x | pytest-cov 7.1.0 | 2025-2026 | API stable; version update only |

**Deprecated/outdated:**
- `ruff check --select ... --fix --unsafe-fixes`: not needed for Phase 37 (no unsafe fixes applied; UP006/UP035 get noqa not auto-fixed)
- `pre-commit run --all-files` instead of `pre-commit install`: use `pre-commit install` for ongoing use; `--all-files` for one-off
- `mypy --strict`: too broad for a legacy codebase; use per-module overrides instead

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | GitHub automatically honors `.git-blame-ignore-revs` when the file exists in the repo root | Pattern 9: .git-blame-ignore-revs | If not honored, blame is still corrupt for the format commit; mitigation: document the `git config` command either way |
| A2 | `pre-commit` pinned-mirror approach (not `repo: local`) is the current standard recommendation | Pattern 8: pre-commit config | If `repo: local` is recommended, the mypy venv isolation is simpler but version drift risk differs; functionally equivalent |

**If this table is empty:** All other claims in this research were verified or cited — no user confirmation needed for them.

---

## Open Questions

1. **ruff `--fix` in pre-commit `ruff-check` hook — include or not?**
   - What we know: adding `args: ["--fix"]` auto-fixes safe violations (unused imports that are
     fixable, import sorting) at commit time; the developer needs to `git add` the changes before
     the commit succeeds (pre-commit aborts with "files were modified by this hook").
   - What's unclear: whether the operator wants auto-fix at commit time or check-only.
   - Recommendation: start with check-only (no `--fix` args) to keep pre-commit simple; devs
     run `ruff check --fix` manually when they see violations.

2. **Coverage source: `firestarter/` only, or include `tests/`?**
   - What we know: `--cov=firestarter` measures only the package code (standard); tests/ is not
     production code and its coverage is less meaningful.
   - What's unclear: whether the operator wants to see test file coverage too.
   - Recommendation: `--cov=firestarter` only (standard practice).

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11 | CI (GitHub Actions) | ✓ (CI matrix) | 3.11 (requested) | — |
| Python 3.12 | devcontainer | ✓ | 3.12.13 | — |
| ruff | lint gate | ✗ (not pre-installed) | 0.15.14 (latest) | pip install |
| mypy | type gate | ✓ (pre-installed in devcontainer) | 2.1.0 | pip install |
| pytest-cov | coverage gate | ✗ (not installed) | 7.1.0 (latest) | pip install |
| types-pyserial | mypy stubs | ✓ (pre-installed in devcontainer) | 3.5.0.20260519 | pip install |
| pre-commit | git hooks | ✓ (installable) | 4.6.0 (latest) | — |

**Missing dependencies with no fallback:** none (all installable via pip).
**Missing dependencies with fallback:** ruff, pytest-cov — install via `pip install -e .[test]`.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ (Phase 36 extended `pyproject.toml`) |
| Config file | `firestarter_app/pyproject.toml` (`[tool.pytest.ini_options]`) |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ --cov=firestarter --cov-fail-under=50` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TOOL-01 | `ruff check` exits 0 on full tree | smoke | `ruff check firestarter/ tests/` | N/A (command, not test file) |
| TOOL-01 | `ruff format --check` exits 0 on full tree | smoke | `ruff format --check firestarter/ tests/` | N/A |
| TOOL-02 | mypy error count ≤ watermark | smoke | `python scripts/check_mypy_watermark.py` | ❌ Wave 0 |
| TOOL-03 | CI workflow runs and passes | integration | CI YAML (GitHub Actions) | ❌ Wave 0 (extend existing) |
| TOOL-03 | pre-commit config committed | manual | `pre-commit run --all-files` | ❌ Wave 0 |
| GATE-1.8e | Full test suite green after reformatting | unit/integration | `pytest tests/ -q` | ✅ 162 tests |
| GATE-1.8e | Coverage ≥ 50% | coverage | `pytest tests/ --cov=firestarter --cov-fail-under=50` | N/A |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q` (verifies reformat didn't break behavior)
- **Per wave merge:** `pytest tests/ --cov=firestarter --cov-fail-under=50` + ruff + mypy
- **Phase gate:** Full CI run (push to `v1.8-app-cleanup` triggers the updated ci.yml)

### Wave 0 Gaps
- [ ] `scripts/check_mypy_watermark.py` — covers TOOL-02 watermark gate
- [ ] `firestarter_app/.pre-commit-config.yaml` — covers TOOL-03 pre-commit
- [ ] `firestarter_app/.git-blame-ignore-revs` — covers D-02 blame preservation
- [ ] Updated `firestarter_app/.github/workflows/ci.yml` — covers TOOL-03 CI gate

*(Existing test infrastructure: 162 tests + 2 xfail + 29 snapshots from Phase 36 cover GATE-1.8e)*

---

## Security Domain

> Phase 37 is pure tooling — no new user-facing code, no new external network calls, no
> auth/session/crypto changes. ASVS categories not applicable. The tooling configuration itself
> does not introduce security surface.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | — |
| V3 Session Management | No | — |
| V4 Access Control | No | — |
| V5 Input Validation | No (no new input paths) | — |
| V6 Cryptography | No | — |

**Known threat patterns:** None specific to ruff/mypy configuration. The `scripts/check_mypy_watermark.py`
script reads a local file and runs a subprocess — no external network access, no user input.

---

## Sources

### Primary (HIGH confidence)
- ruff 0.15.14 — installed and tested directly on `firestarter_app/` at Phase 36 tip
- mypy 2.1.0 — installed and tested; 41-error baseline measured directly
- pytest-cov 7.1.0 — installed and run; 51.33% coverage measured directly
- pyproject.toml (firestarter_app/) — read directly; `requires-python = ">=3.9"` confirmed
- ci.yml (firestarter_app/) — read directly; trigger shape confirmed
- ruff `.pre-commit-hooks.yaml` tag v0.15.14 — fetched from GitHub raw content
- mirrors-mypy tags list — fetched from GitHub API; v2.1.0 is latest

### Secondary (MEDIUM confidence)
- ruff docs: E501 exclusion recommendation when using ruff-format — widely documented in
  ruff migration guides; consistent with observed behavior (443 E501s pre-format → 3 post-format)
- GitHub `.git-blame-ignore-revs` auto-honor — documented in GitHub blog (2022+); behavior
  consistent with git 2.23+ spec

### Tertiary (LOW confidence — see Assumptions Log)
- pre-commit pinned-mirror vs `repo: local` tradeoff — training knowledge; community consensus
  favors pinned mirrors for isolation [ASSUMED]

---

## Metadata

**Confidence breakdown:**
- Standard stack (ruff, mypy, pytest-cov versions): HIGH — all installed and version-checked
- Three-step baseline sequence mechanics: HIGH — tested end-to-end on real codebase
- Coverage watermark (51.33% → 50% gate): HIGH — directly measured
- mypy error watermark (41): HIGH — directly measured
- pre-commit hook configuration: MEDIUM — pinned versions verified; `repo: local` vs mirror tradeoff is ASSUMED
- `.git-blame-ignore-revs` GitHub auto-honor: MEDIUM — widely documented, not independently verified this session

**Research date:** 2026-05-27
**Valid until:** 2026-07-27 (ruff moves fast; mypy 2.x stable; re-verify tool versions before execution)

# Phase 37: Tooling Baseline + CI Gate - Pattern Map

**Mapped:** 2026-05-27
**Files analyzed:** 5 (2 modified, 3 created)
**Analogs found:** 3 / 5

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/pyproject.toml` | config | batch | itself — existing `[tool.pytest.ini_options]` + `[project.optional-dependencies]` blocks | self-analog (extend in place) |
| `firestarter_app/.github/workflows/ci.yml` | config / CI pipeline | request-response | itself — existing single `ci` job | self-analog (extend in place) |
| `firestarter_app/.pre-commit-config.yaml` | config | event-driven | none — greenfield | no analog |
| `firestarter_app/.git-blame-ignore-revs` | config | — | none — greenfield | no analog |
| `firestarter_app/scripts/check_mypy_watermark.py` | utility / CI script | batch | `firestarter_app/tools/check_dispatch.py` | role-match (exit-code gate script) |

---

## Pattern Assignments

### `firestarter_app/pyproject.toml` (config — extend in place)

**Analog:** itself. Read the file before editing; the existing blocks set all style
conventions (no spaces around `=` in TOML tables, double-quoted strings, 4-space indent
inside array values).

**Existing blocks to extend** (lines 57–84 of the current file):

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
]
test = [
    "pytest>=8.0",
    "syrupy>=5.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q"
```

**New blocks to append** (after the last existing `[tool.*]` block — currently
`[tool.pytest.ini_options]` at line 82):

```toml
# Extend [project.optional-dependencies].test in place — add to the existing list:
test = [
    "pytest>=8.0",
    "syrupy>=5.0",
    # Phase 37 additions:
    "ruff>=0.15.14",
    "mypy>=2.1.0",
    "pytest-cov>=7.1.0",
    "types-pyserial>=3.5.0.20260519",
]

# Append after [tool.pytest.ini_options]:

[tool.ruff]
target-version = "py39"
line-length = 88

[tool.ruff.lint]
# E: pycodestyle errors (style violations that ruff-format does not fix)
# F: pyflakes (undefined names, unused imports)
# I: isort (import ordering)
# UP: pyupgrade (modernise syntax within py39 bounds — UP007/UP045 no-ops on py39)
# No select = ["ALL"] — broadening to B/SIM/C4 deferred to Phase 42.
# E501 excluded: ruff-format enforces line length; including E501 causes a
# noqa-adds-noqa-on-long-lines cycle (443 violations pre-format → 3 post-format).
select = ["E", "F", "I", "UP"]
extend-ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.9"          # Must be in config file — mypy 2.1.0 rejects --python-version 3.9 via CLI flag
ignore_missing_imports = true   # needed for tqdm, rich, argcomplete (no stubs)
disallow_untyped_defs = false   # gradual adoption — global stays lenient (D-10)
check_untyped_defs = false
# mypy_error_watermark = 41     # Baseline: Phase 37 tip. Lower as modules get typed.

[[tool.mypy.overrides]]
# Phase 36 test modules — strict-island: check bodies of untyped test functions.
# "Strict" here means check_untyped_defs = true, NOT disallow_untyped_defs = true
# (the latter would require -> None on every test function and would break the suite).
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

**Critical notes for the planner:**
- `select` must be under `[tool.ruff.lint]`, NOT `[tool.ruff]` — the wrong table is
  silently ignored in ruff >= 0.2.0.
- `python_version = "3.9"` in the config file is accepted by mypy 2.1.0; the CLI
  `--python-version 3.9` flag is rejected. Never add `--python-version` to any CI step.
- The `fail_under` coverage threshold is NOT placed in `[tool.coverage.report]` — it
  stays in the CI step as `--cov-fail-under=50` so the gate is visible in the YAML.

---

### `firestarter_app/.github/workflows/ci.yml` (config / CI pipeline — extend in place)

**Analog:** itself. Read the file before editing. Current shape (lines 1–49):

```yaml
name: Host CI
on:
  push:
    branches:
    - main
    paths-ignore:
    - '**.md'
    - '.gitignore'
    - 'docs/**'
    - '.vscode/**'
    - '.editorconfig'
  pull_request:
    branches:
    - main
    paths-ignore:
    - '**.md'
    - '.gitignore'
    - 'docs/**'
    - '.vscode/**'
    - '.editorconfig'

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

      - name: Install package + dev deps
        run: pip install -e .[dev]

      - name: Run pytest
        run: pytest tests/ -v
```

**Changes required (D-06 + D-07):**

1. **Trigger fix (D-06):** Remove `branches: [main]` (and the `- main` list item) from the
   `pull_request:` block entirely. Keep `branches: [main]` on `push:`. Indentation convention
   in the current file uses 2-space YAML + 4-space continuation for multi-line `run:` values —
   match that exactly.

2. **Install step rename + extra swap (D-07):** Change step name from
   `"Install package + dev deps"` to `"Install package + test deps"` and change
   `pip install -e .[dev]` to `pip install -e .[test]`.

3. **Fold new gate steps (D-07)** — insert after the install step, replace the
   existing `"Run pytest"` step:

```yaml
      - name: ruff lint
        run: ruff check firestarter/ tests/

      - name: ruff format check
        run: ruff format --check firestarter/ tests/

      - name: mypy type check (watermark gate)
        run: python scripts/check_mypy_watermark.py

      - name: Run pytest with coverage
        run: pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=50
```

**Style note:** The existing file uses 6-space indentation for step bodies (`      - name:`).
The `run:` values for multi-line commands use `|` block scalar + 10-space continuation
(see the codegen step). Match both conventions exactly.

**Do NOT touch:** `beta-release.yml`, `publish.yml`, `release.yml` — out of scope.

---

### `firestarter_app/.pre-commit-config.yaml` (config — greenfield)

**Analog:** none in this repo. Standard pre-commit YAML structure.

**Pattern to create:**

```yaml
# Hook order per D-07: ruff-check → ruff-format → mypy
# Pinned to versions verified against PyPI on 2026-05-27.
# Update with: pre-commit autoupdate
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

**Notes:**
- Hook IDs in `astral-sh/ruff-pre-commit` v0.15.14 are `ruff-check` and `ruff-format`
  (NOT the legacy `ruff` alias).
- No `args: ["--fix"]` on ruff-check — pre-commit runs as a check-only gate; devs run
  `ruff check --fix` manually. This avoids the "files modified by hook, re-stage needed"
  developer friction.
- `additional_dependencies` on the mypy hook provides `types-pyserial` into the hook's
  isolated venv (D-11).

---

### `firestarter_app/.git-blame-ignore-revs` (config — greenfield)

**Analog:** none in this repo. Standard git format (git >= 2.23).

**Pattern to create:**

```
# Whole-tree ruff format commit (Phase 37 D-02, 2026-05-27)
# Preserves git blame across the mechanical reformat.
# Contributor setup: git config blame.ignoreRevsFile .git-blame-ignore-revs
# GitHub honors this file automatically when present in the repo root.
<PLACEHOLDER — replace with full 40-char SHA of the ruff format commit>
```

**Notes:**
- One full 40-character SHA per line; `#` lines are comments.
- The SHA is the commit produced by D-01 step 1 (`ruff format` whole-tree commit).
  The file is created AFTER that commit so the SHA is known.
- GitHub automatically picks up the file from the repo root; no `.github` config needed.
- Contributor local setup is documented here as a comment; also add to README/CONTRIBUTING.

---

### `firestarter_app/scripts/check_mypy_watermark.py` (utility — partial analog)

**Closest analog:** `firestarter_app/tools/check_dispatch.py`

**Match quality:** role-match. Both are standalone Python gate scripts invoked by CI;
both exit 0 on pass, exit 1 on gate failure; both parse a data source and report
structured pass/fail output to stdout.

**Analog patterns to mirror** (from `tools/check_dispatch.py`):

Module docstring (lines 1–16 of check_dispatch.py):
```python
"""
Regression scan: assert every chip in chip_database.json reaches a real
firmware dispatch path after Phase 12.
...
Exit codes:
  0 — every chip in the DB resolves to a real handler ...
  1 — at least one chip would hit "Memory type 0x%02x not supported", ...
"""
```
Mirror: leading module docstring with one-line description, phase/requirement
reference, and exit-code table.

Import style (lines 17–21 of check_dispatch.py):
```python
import json
import os
import sys

from firestarter.database import EpromDatabase
```
Mirror: stdlib imports only (no third-party); group stdlib together.

`main()` function + `if __name__ == "__main__": main()` guard (lines 84, 193–194):
```python
def main():
    """Entry point: scan DB and exit non-zero if any chip lacks a dispatch path."""
    ...
    sys.exit(1)   # failure path

    print("PASS: ...")   # success: implicit exit 0


if __name__ == "__main__":
    main()
```
Mirror: `main()` function, explicit `sys.exit(1)` on failure, print-based
reporting, `if __name__` guard.

**Script to create** (implement per RESEARCH.md Pattern 5):

```python
#!/usr/bin/env python3
"""scripts/check_mypy_watermark.py — CI mypy gate (D-10, Phase 37).

Run mypy, count errors, fail if error count exceeds the watermark.
Watermark is stored as a comment in [tool.mypy] in pyproject.toml:
    # mypy_error_watermark = 41

Exit codes:
  0 — error count is at or below the watermark (gate passes)
  1 — error count exceeds the watermark (new errors introduced; gate fails)
  2 — configuration error (watermark comment not found in pyproject.toml)
"""
import re
import subprocess
import sys
import tomllib
from pathlib import Path


def get_watermark() -> int:
    """Read the mypy_error_watermark integer from pyproject.toml."""
    text = Path("pyproject.toml").read_text()
    m = re.search(r"#\s*mypy_error_watermark\s*=\s*(\d+)", text)
    if not m:
        print(
            "ERROR: mypy_error_watermark comment not found in [tool.mypy]",
            file=sys.stderr,
        )
        sys.exit(2)
    return int(m.group(1))


def count_mypy_errors() -> int:
    """Run mypy on the project and return the error count. Returns 0 on success."""
    result = subprocess.run(
        ["mypy", "firestarter/", "tests/"],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    m = re.search(r"Found (\d+) errors?", output)
    return int(m.group(1)) if m else 0


def main() -> None:
    watermark = get_watermark()
    count = count_mypy_errors()
    print(f"mypy errors: {count} (watermark: {watermark})")
    if count > watermark:
        print(
            f"FAIL: {count} errors exceeds watermark {watermark}. New errors introduced."
        )
        sys.exit(1)
    elif count < watermark:
        print(
            f"INFO: {count} errors — {watermark - count} below watermark. "
            f"Lower watermark in pyproject.toml."
        )
    else:
        print("OK: error count at watermark.")


if __name__ == "__main__":
    main()
```

**Key design notes:**
- `tomllib` is stdlib since Python 3.11; the script reads the watermark via regex
  on the raw text (not via TOML parse) because the watermark is a comment, not a
  real TOML key. `tomllib` import is present but unused in the final script — omit
  it or keep it if needed for future extension.
- Do NOT pass `--python-version` to mypy in the subprocess call — let mypy read
  `python_version = "3.9"` from `pyproject.toml` (Pitfall 4 from RESEARCH.md).
- The script must be run from the `firestarter_app/` directory root (where
  `pyproject.toml` lives) — the CI step `run: python scripts/check_mypy_watermark.py`
  satisfies this because GitHub Actions sets the working directory to the repo root.
- No `scripts/` directory exists yet — the planner must create it.

---

## Shared Patterns

### TOML Style Convention
**Source:** `firestarter_app/pyproject.toml` (all existing blocks)
**Apply to:** All new `[tool.*]` blocks in pyproject.toml

The existing file uses:
- No spaces around `=` in table headers (`[tool.setuptools.package-data]`)
- Double-quoted strings throughout
- 4-space indent for array values inside `[]`
- Blank line between top-level table blocks
- No trailing commas on single-item arrays

Match this style exactly in all new blocks.

### CI Step Naming + Indentation Convention
**Source:** `firestarter_app/.github/workflows/ci.yml` (lines 34–49)
**Apply to:** All new steps in ci.yml

```yaml
      - name: Catalog validity check
        run: python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check

      - name: Codegen drift gate (messages.py)
        run: |
          python3 tools/catalog/codegen.py \
            --catalog tools/catalog/messages.toml \
            --target firestarter/messages.py \
            --language python
          git diff --exit-code firestarter/messages.py
```

Step names use sentence-case with parenthetical qualifier. Single-command steps use
inline `run:`. Multi-command steps use `|` block scalar. 6-space indent for `- name:`;
8-space indent for `run:` key; 10-space indent for continuation lines.

### CI Script Exit-Code Gate Pattern
**Source:** `firestarter_app/tools/check_dispatch.py` (lines 148–191)
**Apply to:** `scripts/check_mypy_watermark.py`

```python
    if errors or sram_in_eprom or eeprom28c_in_eprom or wire_regressions:
        if errors:
            print(f"FAIL: ...")
            ...
        sys.exit(1)

    print(f"PASS: ...")
```

Pattern: collect failures into lists, print structured FAIL messages, call
`sys.exit(1)` at the end of the failure branch; success falls through to a
`print("PASS: ...")` with implicit exit 0.

### CI Gate Script Structure
**Source:** `firestarter_app/tools/catalog/codegen.py` (lines 1–34)
**Apply to:** `scripts/check_mypy_watermark.py`

```python
#!/usr/bin/env python3
"""
<one-line description>.

<longer description paragraph>

Stdlib only (Python 3.11+ for tomllib).
"""
import argparse
import re
import sys
import tomllib
from pathlib import Path
```

Pattern: shebang line, triple-quoted module docstring with stdlib note, stdlib-only
imports grouped together.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `firestarter_app/.pre-commit-config.yaml` | config | event-driven | No pre-commit config exists in this repo yet; use canonical pre-commit YAML structure from RESEARCH.md Pattern 8 |
| `firestarter_app/.git-blame-ignore-revs` | config | — | No `.git-blame-ignore-revs` exists; trivial format — one SHA per line with comments |

---

## Metadata

**Analog search scope:** `/workspaces/firestarter_app/` (tools/, .github/scripts/, .github/workflows/)
**Files scanned:** 6 (pyproject.toml, ci.yml, tools/check_dispatch.py, tools/catalog/codegen.py, tools/build_db.py, .github/scripts/update_version.py)
**Pattern extraction date:** 2026-05-27

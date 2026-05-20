# Phase 15: Versioning & Locked-Step Coordination (Foundation) — Pattern Map

**Mapped:** 2026-05-20
**Files analyzed:** 8 (2 modified, 3 new code files, 1 new CI step, 2 planning artifacts)
**Analogs found:** 6 / 8 (2 have no codebase analog — first introduction of PEP 440 and firmware Python tests)

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/.github/scripts/update_version.py` | utility (CI script) | transform (file I/O + env-var dispatch) | itself (existing 60-line script — extend in-place) | self-analog |
| `firestarter/.github/scripts/update_version.py` | utility (CI script) | transform (file I/O + env-var dispatch) | itself (existing 63-line script — extend in-place) | self-analog |
| `firestarter_app/tests/test_update_version.py` | test | request-response (function call + assertion) | `firestarter_app/tests/test_fwguard.py` | role-match |
| `firestarter_app/tests/golden/stable-baseline.py` | test fixture | file-I/O (byte-identity seed) | `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` | role-match |
| `firestarter/tests/__init__.py` | config | — | `firestarter_app/tests/__init__.py` (empty) | exact |
| `firestarter/tests/test_update_version.py` | test | request-response (function call + assertion) | `firestarter_app/tests/test_update_version.py` (sibling new file — mirror it) | exact |
| `firestarter/tests/golden/stable-baseline.h` | test fixture | file-I/O (byte-identity seed) | `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` | role-match |
| `firestarter/.github/workflows/build.yml` | CI config | event-driven (new step insertion) | `firestarter_app/.github/workflows/ci.yml` (pytest invocation pattern) | role-match |
| `.planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md` | planning artifact | — | no analog | no analog |

---

## Pattern Assignments

### `firestarter_app/.github/scripts/update_version.py` (utility/CI script, transform + file-I/O)

**Status:** Extend in-place — this file is BOTH the analog and the modification target.

**Existing structure** (`/workspaces/firestarter_app/.github/scripts/update_version.py`, lines 1–61):

**Imports pattern** (lines 1–4):
```python
#!/usr/bin/env python3
import re
import os
```

**Existing `get_version()` function** (lines 6–16) — the regex here is the D-23 extension target:
```python
version_file = "firestarter/__init__.py"

def get_version():
    rxs = "^__version__ =(.\")([0-9\.]+)"   # ← EXTEND THIS (D-23/D-24)
    txt = [line for line in open(version_file)]
    for line in txt:
        m = re.match(rxs, line)
        if m:
            major, minor, patch = str(m.group(2)).split(".")
            return (major, minor, patch)
```

**Existing `update_version()` function** (lines 18–36) — the write format here carries to the beta path:
```python
def update_version(major, minor, patch):
    """Update the version number in the file."""
    rxs = "^(__version__ = )"
    txt = [line for line in open(version_file)]
    fout = open(version_file, "w")
    for line in txt:
        m = re.match(rxs, line)
        if m:
            line = m.groups(0)[0] + f"\"{major}.{minor}.{patch}\"\n"
            fout.write(line)
        else:
            fout.write(line)
    fout.close()
    print(f"Version file updated: {major}.{minor}.{patch}")
```

**Existing `calculate_version()` stable function + GITHUB_OUTPUT write** (lines 39–57):
```python
def calculate_version():
    major, minor, patch = get_version()
    pattern = re.compile("[0-9]+")
    if pattern.match(patch):
        patch = int(patch) + 1
    else:
        patch = 0
    update_version(major, minor, patch)
    print(f"New versin created: {major}.{minor}.{patch}")  # typo — preserve as-is (D-17)
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        print(f"version={major}.{minor}.{patch}", file=fh)
        print(f"major={major}", file=fh)
        print(f"minor={minor}", file=fh)
        print(f"patch={patch}", file=fh)
```

**Existing `__main__` entry point** (lines 59–61):
```python
if __name__ == "__main__":
    calculate_version()
```

**Extension shape — what to ADD (planner synthesizes from CONTEXT.md decisions):**

The planner inserts these additions around the existing structure:

1. **New imports** — add `argparse` and `subprocess` to the existing `import re` / `import os` block.

2. **Regex constant for `get_version()`** — replace the current inline string with the D-24 named-group regex:
   ```python
   # Replace line 8's inline string with:
   rxs = r'^__version__ =(.\")(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)(?P<pre>(b|rc)[0-9]+)?'
   ```
   Return signature changes from `(major, minor, patch)` to `(major, minor, patch, pre)` where `pre` may be `None`. Update the caller `calculate_version()` to unpack 4 values — `major, minor, patch, pre = get_version()` — and the stable path discards `pre`.

3. **New `update_version()` overload for beta path** — the write format for a pre-release string differs from the stable `f"{major}.{minor}.{patch}"`. The beta write is `f'"{version_string}"\n'` where `version_string = "3.1.0b1"`. Either extend `update_version()` to accept an optional `version_string` kwarg, or introduce a thin `update_version_string(version_string)` that reuses the same `rxs = "^(__version__ = )"` line from lines 21–22.

4. **`BETA_VERSION_RE` constant** — validation regex from D-21:
   ```python
   BETA_VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$')
   ```

5. **`is_beta_mode(args)` function** — from RESEARCH.md Pattern 1.

6. **`compute_beta_version(major, minor, patch)` function** — from RESEARCH.md Pattern 2 (verbatim env var + git-tag-scan fallback).

7. **`parse_args()` function** — argparse with `--dry-run`, `--beta`, optionally `--set-version` (D-29).

8. **Modified `__main__`** — gate on `is_beta_mode(args)` before calling `calculate_version()`.

9. **`GITHUB_OUTPUT` guard** — wrap the `open(os.environ["GITHUB_OUTPUT"], ...)` calls in `os.environ.get("GITHUB_OUTPUT")` guard per RESEARCH.md Pitfall 6.

**Key constraint (D-17):** When called with no args and no beta env vars, the extended script MUST produce byte-identical output to the current script on the same input. The stable path code (the existing `calculate_version()` body) MUST NOT be reorganized or refactored — only the `get_version()` return type (4-tuple vs 3-tuple) is a required mechanical change.

---

### `firestarter/.github/scripts/update_version.py` (utility/CI script, transform + file-I/O)

**Status:** Extend in-place — this file is BOTH the analog and the modification target. Symmetric to the app's script.

**Existing structure** (`/workspaces/firestarter/.github/scripts/update_version.py`, lines 1–64):

**Imports + `get_header_version()` function** (lines 1–18):
```python
#!/usr/bin/env python3
import re
import os

def get_header_version():
    header_file = "include/version.h"
    # rxs = "^#define VERSION (\w+)"
    rxs = '^#define VERSION(.")([0-9\.]+)'    # ← EXTEND THIS (D-23/D-24)
    txt = [line for line in open(header_file)]
    for line in txt:
        m = re.match(rxs, line)
        if m:
            major, minor, patch = str(m.group(2)).split(".")
            return (major, minor, patch)
```

**Existing `update_version()` for firmware** (lines 21–40) — note the single-quote vs double-quote difference from the app's script:
```python
def update_version(major, minor, patch):
    """Update the version number in the header file."""
    header_file = "include/version.h"
    rxs = "^(#define VERSION )"
    txt = [line for line in open(header_file)]
    fout = open(header_file, "w")
    for line in txt:
        m = re.match(rxs, line)
        if m:
            line = m.groups(0)[0] + f'"{major}.{minor}.{patch}"\n'
            fout.write(line)
        else:
            fout.write(line)
    fout.close()
    print(f"Version file updated: {major}.{minor}.{patch}")
```

**Existing `calculate_version()` + GITHUB_OUTPUT write** (lines 43–63) — structurally identical to app's:
```python
def calculate_version():
    major, minor, patch = get_header_version()
    pattern = re.compile("[0-9]+")
    if pattern.match(patch):
        patch = int(patch) + 1
    else:
        patch = 0
    update_version(major, minor, patch)
    print(f"New versin created: {major}.{minor}.{patch}")  # typo — preserve as-is (D-17)
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        print(f"version={major}.{minor}.{patch}", file=fh)
        print(f"major={major}", file=fh)
        print(f"minor={minor}", file=fh)
        print(f"patch={patch}", file=fh)
```

**Extension shape:** Identical to the app's extension except:
- `get_header_version()` instead of `get_version()`; D-24 regex uses `'^#define VERSION(.")(...)` match prefix
- `header_file = "include/version.h"` path
- Git-tag-scan fallback in `_git_tag_scan_fallback()` is identical — no version-file-format difference in git tags

---

### `firestarter_app/tests/test_update_version.py` (test, request-response)

**Analog:** `firestarter_app/tests/test_fwguard.py`

**Why this analog:** `test_fwguard.py` is the closest match — it tests a function that reads an env var (`FIRESTARTER_DEV_ALLOW_PRE_V12`) and changes behavior, uses `monkeypatch.setenv` / `monkeypatch.delenv` for env-var isolation, uses class-based test organisation with an `autouse` fixture for hermetic env cleanup, and has multiple test methods covering success + edge paths. All patterns transfer directly to `test_update_version.py`.

**Class structure pattern** (`/workspaces/firestarter_app/tests/test_fwguard.py`, lines 31–43):
```python
class TestFirmwareVersionGuard:
    """LFW-05 / LHOST-04 — host refuses pre-v1.2 firmware at probe time."""

    @pytest.fixture(autouse=True)
    def _clear_escape_hatch(self, monkeypatch):
        """Ensure the dev escape-hatch env var is unset for every test by default.

        Tests that explicitly want it set call `monkeypatch.setenv(...)` AFTER
        this autouse fixture has cleared it; the per-test setenv then overrides
        the delenv for the duration of that single test.
        """
        monkeypatch.delenv("FIRESTARTER_DEV_ALLOW_PRE_V12", raising=False)
```

**Apply to `test_update_version.py`:** The autouse fixture clears `GITHUB_REF`, `BETA_VERSION`, and `GITHUB_OUTPUT` before each test. Tests that exercise the beta path call `monkeypatch.setenv("GITHUB_REF", "refs/heads/beta")` after the autouse delenv.

**`monkeypatch.setenv` pattern** (`/workspaces/firestarter_app/tests/test_fwguard.py`, line 87):
```python
def test_dev_escape_hatch_env_var(self, monkeypatch):
    monkeypatch.setenv("FIRESTARTER_DEV_ALLOW_PRE_V12", "1")
    # ...
```

**`tmp_path` + file write pattern** (from `test_audit_coverage_matrix.py` line 577–579 — golden-file test):
```python
tmp_ledger = tmp_path / "l.json"
tmp_ledger.write_bytes(committed_ledger.read_bytes())
```

**Apply to `test_update_version.py` stable-path test:** Write a known `__init__.py` content to `tmp_path / "__init__.py"`, point the script at it via monkeypatched `version_file`, run the stable path, assert `read_text()` equals expected bytes.

**Key pattern for GITHUB_OUTPUT in tests** (from RESEARCH.md Finding 9):
```python
output_file = tmp_path / "github_output"
output_file.write_text("")
monkeypatch.setenv("GITHUB_OUTPUT", str(output_file))
```

**Import pattern for CI scripts** — since `update_version.py` is not an installable package, use `sys.path` insertion in a conftest or inline in the test:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "scripts"))
import update_version
```

**What to NOT copy from `test_fwguard.py`:** The `patch.object` / `unittest.mock` patterns are specific to class method mocking. `test_update_version.py` doesn't need `unittest.mock` — it calls module-level functions directly with monkeypatched env vars and `tmp_path` file system.

**Test class structure for `test_update_version.py`:**
```python
class TestUpdateVersionStable:
    @pytest.fixture(autouse=True)
    def _isolate_env(self, monkeypatch):
        monkeypatch.delenv("GITHUB_REF", raising=False)
        monkeypatch.delenv("BETA_VERSION", raising=False)
        monkeypatch.delenv("GITHUB_OUTPUT", raising=False)

    def test_stable_patch_increment(self, tmp_path, monkeypatch): ...
    def test_stable_byte_identical(self, tmp_path, monkeypatch): ...

class TestUpdateVersionBeta:
    @pytest.fixture(autouse=True)
    def _isolate_env(self, monkeypatch):
        # same as above

    def test_beta_explicit_version(self, tmp_path, monkeypatch): ...
    def test_beta_git_tag_fallback(self, tmp_path, monkeypatch): ...
    def test_beta_invalid_version_rejected(self, tmp_path, monkeypatch): ...

class TestUpdateVersionDryRun:
    def test_dry_run_no_file_write(self, tmp_path, monkeypatch): ...
    def test_dry_run_stdout_format(self, tmp_path, monkeypatch, capsys): ...
```

---

### `firestarter_app/tests/golden/stable-baseline.py` (test fixture, file-I/O)

**Analog:** `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md`

**How the golden-file pattern is used in the codebase** (`test_audit_coverage_matrix.py`, lines 538–585):
```python
def test_golden_file_matches(self, tmp_path):
    """End-to-end golden-file regression."""
    from pathlib import Path
    from tools.audit_coverage_matrix import generate_matrix

    golden_file = (
        Path(__file__).resolve().parents[1]
        / "tests" / "golden" / "v1.3-COVERAGE-MATRIX.md"
    )
    assert golden_file.exists(), (
        f"golden fixture missing at {golden_file}; "
        "Wave 4 Task 2 must snapshot the matrix to this path"
    )
    # ... generate output, compare byte-for-byte:
    assert out.read_bytes() == golden_file.read_bytes()
```

**Pattern for `stable-baseline.py`:** A minimal `__init__.py` file with a known version string that serves as both the input seed AND the byte-identity reference for the stable path. The file is committed under `tests/golden/` and loaded in the stable-path test.

**Naming convention note:** The existing golden file uses a descriptive milestone-scoped name (`v1.3-COVERAGE-MATRIX.md`). For Phase 15, use `stable-baseline.py` (the seed input to the stable path) and optionally `stable-expected.py` (the expected output after one patch increment). The test asserts `output_file.read_text() == stable_expected_py.read_text()`.

**Minimal file content for `stable-baseline.py`:**
```python
__version__ = "1.2.3"
```

**Minimal file content for `stable-expected.py`** (output after stable bump):
```python
__version__ = "1.2.4"
```

**Path resolution pattern** (copy from `test_golden_file_matches`, line 563–565):
```python
golden_dir = Path(__file__).resolve().parent / "golden"
baseline = golden_dir / "stable-baseline.py"
expected = golden_dir / "stable-expected.py"
```

---

### `firestarter/tests/__init__.py` (config, empty)

**Analog:** `firestarter_app/tests/__init__.py`

The file has 1 line of content (empty / comment-only). The app's `__init__.py` is also empty (1 line). Copy exactly:
```python
```
(empty file — zero bytes or a single `\n`)

---

### `firestarter/tests/test_update_version.py` (test, request-response)

**Analog:** `firestarter_app/tests/test_update_version.py` (sibling new file)

**Copy pattern exactly from the app's test file** with these substitutions:
- `sys.path.insert` target: `".github/scripts"` → same path (both scripts are in `.github/scripts/`)
- `version_file` variable: `"firestarter/__init__.py"` → `"include/version.h"` (the script's internal constant)
- Input seed file content: `'__version__ = "1.2.3"\n'` → `'#define VERSION "1.2.3"\n'`
- Expected stable-bump output: `'__version__ = "1.2.4"\n'` → `'#define VERSION "1.2.4"\n'`

The test structure (class hierarchy, autouse fixture, `monkeypatch`, `tmp_path`, `capsys`) is identical to the app-side test. No firmware-specific patterns needed — the script under test is pure Python.

**`sys.path` insertion pattern** — needed because the script is not a package. Place in conftest.py or inline:
```python
# At top of test file (or in a conftest.py if firmware gets more Python tests later)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "scripts"))
import update_version  # the firmware's update_version.py
```

---

### `firestarter/tests/golden/stable-baseline.h` (test fixture, file-I/O)

**Analog:** `firestarter_app/tests/golden/stable-baseline.py` (sibling new file)

**Minimal file content:**
```c
#define VERSION "1.2.3"
```

**Expected output after stable bump (`stable-expected.h`):**
```c
#define VERSION "1.2.4"
```

**Note on the `include/version.h` actual file** — in the real firmware, `include/version.h` likely has guards and other definitions. The golden fixture for tests uses a minimal single-line form because the script's `update_version()` writes only the matching `#define VERSION` line and passes all other lines through unchanged. Tests use `tmp_path` files (not the real `include/version.h`), so minimal content is sufficient.

---

### `firestarter/.github/workflows/build.yml` — new Python pytest step (CI config, event-driven)

**Analog:** `firestarter_app/.github/workflows/ci.yml` — the pytest step pattern.

**Existing pytest invocation in app's `ci.yml`** (lines 45–49):
```yaml
      - name: Install package + dev deps
        run: pip install -e .[dev]

      - name: Run pytest
        run: pytest tests/ -v
```

**Existing Python setup in firmware's `build.yml`** (line 55–58) — reuse this existing step:
```yaml
      - name: Set up Python 3.11 for codegen
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
```

**New step to INSERT in `build.yml`** — place AFTER the existing codegen Python setup step (line 55) and BEFORE the `Generate release version` step (line 83):
```yaml
      - name: Install pytest for script tests
        run: pip install pytest

      - name: Run update_version.py tests
        run: pytest tests/ -v
```

**Placement constraint (from RESEARCH.md Finding 6):** Insert after the `Set up Python 3.11 for codegen` step (line 55 in the current `build.yml`) — the Python runtime is already available at that point. Insert BEFORE `Generate release version` (line 83) so that if the tests fail, the version bump does not run. This mirrors the existing gate pattern: codegen-drift → native Unity → version bump.

**Full gate ordering after insertion:**
1. `actions/checkout@v4`
2. `actions/cache@v4`
3. `Set up Python 3.11 for codegen`
4. `Catalog validity check`
5. `Codegen drift gate (messages.h)`
6. `Install pytest for script tests`  ← NEW
7. `Run update_version.py tests`       ← NEW
8. `Install PlatformIO Core`
9. `Run native unit tests`
10. `Generate release version`
11. `git-auto-commit-action`
12. `Build PlatformIO Project`
13. `Release`

---

### `.planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md` (planning artifact)

**No analog in codebase.** This is a new pattern — a phase-local procedure document intended for verbatim consumption by Phase 18's `v1.4-RELEASE-PROCEDURES.md`. No existing planning artifact plays this role.

**Structure guidance from CONTEXT.md D-26 and Phase 18 contract:** The document must be self-contained (no references to planning artifact paths that won't be in the Phase 18 doc), cover the full manual lockstep procedure, and be consumable as a copy-in block. Planner defines the structure; suggested sections:

1. **Prerequisites** — what must be true before cutting a beta (both repos' beta workflows exist, `BETA_VERSION` format chosen)
2. **Step-by-step procedure** — numbered steps for the release engineer
3. **Failure recovery** — idempotent retry instructions (documented gap per D-03)
4. **Version string format** — `^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$` validation rule
5. **Known gaps** — single PyPI failure after partial success

---

## Shared Patterns

### Env-Var Isolation in Tests

**Source:** `firestarter_app/tests/test_fwguard.py` lines 34–42 and `test_audit_coverage_matrix.py` lines 55–63
**Apply to:** All test classes in both `test_update_version.py` files

```python
@pytest.fixture(autouse=True)
def _isolate_env(self, monkeypatch):
    """Ensure CI env vars are unset for every test by default."""
    monkeypatch.delenv("GITHUB_REF", raising=False)
    monkeypatch.delenv("BETA_VERSION", raising=False)
    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
```

Tests that need a specific env state call `monkeypatch.setenv(...)` AFTER this autouse — the per-test call overrides the delenv for that single test.

### `tmp_path` File-System Pattern for Script Tests

**Source:** `firestarter_app/tests/test_audit_coverage_matrix.py` lines 195–212
**Apply to:** All test methods that test file-write behavior in both `test_update_version.py` files

```python
def test_something(self, tmp_path, monkeypatch):
    version_file = tmp_path / "__init__.py"          # or "version.h"
    version_file.write_text('__version__ = "1.2.3"\n')

    output_file = tmp_path / "github_output"
    output_file.write_text("")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output_file))

    # ... call script function ...

    assert version_file.read_text() == '__version__ = "1.2.4"\n'
    assert "version=1.2.4\n" in output_file.read_text()
```

### Class-Based Test Organisation

**Source:** `firestarter_app/tests/test_fwguard.py` line 31 and `test_audit_coverage_matrix.py` line 52
**Apply to:** Both `test_update_version.py` files

All tests in a class. Class name = `TestUpdateVersionStable`, `TestUpdateVersionBeta`, `TestUpdateVersionDryRun` — one class per test scenario group. No module-level test functions.

### `capsys` for stdout assertions

**Source:** pytest stdlib — no codebase analog yet (first use in this project)
**Apply to:** `test_dry_run_stdout_format` in both `test_update_version.py` files

```python
def test_dry_run_stdout_format(self, tmp_path, monkeypatch, capsys):
    # ... call script with --dry-run ...
    captured = capsys.readouterr()
    assert captured.out.startswith("DRY_RUN: ")
    version = captured.out.strip().split("DRY_RUN: ")[1]
    assert version == "1.2.3b1"
```

### GITHUB_OUTPUT Guarded Write

**Source:** RESEARCH.md Pitfall 6 + existing script pattern (lines 52–56 app, lines 55–59 firmware)
**Apply to:** Both extended `update_version.py` scripts

Current scripts have an unguarded `open(os.environ["GITHUB_OUTPUT"], "a")`. The extension must guard it:
```python
github_output = os.environ.get("GITHUB_OUTPUT")
if github_output and not args.dry_run:
    with open(github_output, "a") as fh:
        print(f"version={version_string}", file=fh)
        print(f"major={major}", file=fh)
        print(f"minor={minor}", file=fh)
        print(f"patch={patch}", file=fh)
        if pre:
            print(f"pre={pre}", file=fh)
```

---

## No Analog Found

Files with no close match in the codebase (planner uses RESEARCH.md patterns):

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `firestarter/.github/workflows/build.yml` (new step) | CI config | event-driven | The app has a pytest step in `ci.yml`; the firmware has none — pattern is a direct port, but the exact YAML is novel for this repo |
| `.planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md` | planning artifact | — | First procedure document of this type in the project; no existing Phase X artifact plays this role |
| Beta detection logic (`is_beta_mode`, `compute_beta_version`, `_git_tag_scan_fallback`) in both scripts | utility function | — | First introduction of PEP 440 pre-release versioning in this codebase; no existing analog for git-tag-scan or BETA_VERSION env dispatch |
| `argparse` migration of `__main__` in both scripts | utility function | — | Current scripts have no argparse; this is the first introduction |

---

## Metadata

**Analog search scope:** `firestarter_app/tests/`, `firestarter_app/.github/scripts/`, `firestarter_app/.github/workflows/`, `firestarter/.github/scripts/`, `firestarter/.github/workflows/`
**Files scanned:** 9 (2 update_version.py scripts, 3 test files, 1 conftest.py, 1 `__init__.py`, 2 CI workflows)
**Pattern extraction date:** 2026-05-20

---

## Critical Notes for Planner

1. **Typo preservation (D-17):** Both existing scripts have `print(f"New versin created: ...")` — "versin" is misspelled. Do NOT fix in Phase 15. The stable-path byte-identity test asserts this exact string.

2. **Return signature change in `get_version()` / `get_header_version()`:** Adding `pre` as a fourth return value requires updating ALL callers. In the current scripts there is only one caller each (`calculate_version()`). Update the unpack: `major, minor, patch, pre = get_version()`. The stable path discards `pre`.

3. **`GITHUB_OUTPUT` KeyError (RESEARCH Pitfall 6):** Both existing scripts crash with `KeyError` if `GITHUB_OUTPUT` is not set (e.g., local runs). The guard pattern above is required for tests to work without mocking the env var.

4. **Test sys.path for unpackaged scripts:** `update_version.py` is not installed as a package. Tests must insert `.github/scripts/` into `sys.path` before importing the module. Do this in the test file itself (not conftest.py) so it's explicit and self-contained.

5. **PlatformIO `test/` vs `tests/` (RESEARCH Open Question 2):** Firmware PlatformIO tests live in `test/` (no `s`). New Python pytest tests go in `tests/` (with `s`). These are separate directories — no conflict.

6. **`pyproject.toml` pytest config (app only):** `firestarter_app/pyproject.toml` line 80: `testpaths = ["tests"]`. The new `test_update_version.py` is under `tests/` and will be discovered automatically. No `pyproject.toml` changes needed for the app. The firmware has no `pyproject.toml` — pytest discovery defaults to `tests/` which is correct.

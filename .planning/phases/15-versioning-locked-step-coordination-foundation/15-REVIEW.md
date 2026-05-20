---
phase: 15-versioning-locked-step-coordination-foundation
reviewed: 2026-05-20T00:00:00Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - firestarter_app/.github/scripts/update_version.py
  - firestarter_app/tests/test_update_version.py
  - firestarter_app/tests/golden/stable-baseline.py
  - firestarter_app/tests/golden/stable-expected.py
  - firestarter/.github/scripts/update_version.py
  - firestarter/.github/workflows/build.yml
  - firestarter/tests/test_update_version.py
  - firestarter/tests/__init__.py
  - firestarter/tests/golden/stable-baseline.h
  - firestarter/tests/golden/stable-expected.h
findings:
  critical: 3
  warning: 4
  info: 2
  total: 9
status: issues_found
---

# Phase 15: Code Review Report

**Reviewed:** 2026-05-20T00:00:00Z
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Ten files reviewed across both sub-repos: two `update_version.py` scripts (app and firmware), their pytest test suites, golden fixture files, and the firmware `build.yml` workflow. The golden files and step-ordering in `build.yml` are correct. The stable-path byte-identity contract (D-17) is preserved including the intentional "New versin created:" typo. The `GITHUB_OUTPUT` guard (Pitfall 6) is correctly applied. The `subprocess.run` call uses a list form so shell injection is not possible.

Three blockers were found: data-loss from unclosed write handles on exception, a crash when `get_version()`/`get_header_version()` finds no `__version__` / `#define VERSION` line (returns `None` and causes `TypeError` at the 4-tuple unpack site), and a logical correctness gap where the git-tag-scan fallback silently ignores `rc`-series tags even though `BETA_VERSION_RE` accepts `rc` as a valid pre-release type. Four warnings cover file-handle resource leaks, version-regex over-permissiveness, and a test coverage gap.

---

## Critical Issues

### CR-01: Version file truncated and unrecoverable if write fails mid-stream (both scripts)

**File:** `firestarter_app/.github/scripts/update_version.py:32` / `firestarter/.github/scripts/update_version.py:35`

**Issue:** `update_version()` loads all lines into `txt` (line 30/33), then immediately opens the same file for writing with `fout = open(version_file, "w")` (line 32/35), which **truncates the file to zero bytes at that instant**. The write loop then iterates over `txt` in memory. If any `fout.write(line)` call raises (e.g. disk-full, permission error), execution falls through to the unguarded `fout.close()` at line 43/46 — but Python will not reach that line if an exception is thrown first. The file is left truncated (empty or partial). No exception handling or rollback exists. The result is permanent data loss of the version file with no error message.

This affects both the stable path and the beta path since both call `update_version()`.

**Fix:** Use a write-to-temp-then-rename pattern (atomic replace), or at minimum wrap the write in a try/except/finally that restores `txt` on failure:

```python
import tempfile, os

def update_version(major, minor, patch, *, version_string=None):
    rxs = "^(__version__ = )"  # or "#define VERSION " for firmware
    with open(version_file) as fin:
        txt = fin.readlines()

    written_ver = version_string if version_string else f"{major}.{minor}.{patch}"
    dirpath = os.path.dirname(os.path.abspath(version_file))
    fd, tmp_path = tempfile.mkstemp(dir=dirpath)
    try:
        with os.fdopen(fd, "w") as fout:
            for line in txt:
                m = re.match(rxs, line)
                if m:
                    line = m.groups(0)[0] + f'"{written_ver}"\n'
                fout.write(line)
        os.replace(tmp_path, version_file)
    except Exception:
        os.unlink(tmp_path)
        raise
    print(f"Version file updated: {written_ver}")
```

---

### CR-02: `get_version()` / `get_header_version()` silently returns `None` — causes `TypeError` crash at call site (both scripts)

**File:** `firestarter_app/.github/scripts/update_version.py:11-20` (and call site line 142/175); `firestarter/.github/scripts/update_version.py:15-23` (and call site line 145/178)

**Issue:** Both `get_version()` and `get_header_version()` iterate over the file looking for a matching line. If no line matches (corrupt file, wrong path, file with no `__version__` / `#define VERSION` line), the function falls off the end and implicitly returns `None`. The callers in `calculate_version()` immediately unpack the result as a 4-tuple:

```python
major, minor, patch, _pre = get_version()   # line 142 (app beta path)
major, minor, patch, _pre = get_header_version()  # line 145 (firmware beta path)
```

When `get_version()` returns `None`, Python raises `TypeError: cannot unpack non-iterable NoneType object`. The error message gives no indication of what went wrong or which file was missing/malformed. On the stable path (lines 175/178) the same crash occurs.

**Fix:** Raise a clear `FileNotFoundError` or `ValueError` with the file path in `get_version()` / `get_header_version()` if no match is found:

```python
def get_version():
    rxs = r'^__version__ =(.\")(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)(?P<pre>(b|rc)[0-9]+)?'
    with open(version_file) as f:
        for line in f:
            m = re.match(rxs, line)
            if m:
                return (m.group("major"), m.group("minor"), m.group("patch"), m.group("pre"))
    raise ValueError(
        f"No __version__ line found in {version_file!r}. "
        f"Expected format: __version__ = \"X.Y.Z\""
    )
```

---

### CR-03: `_git_tag_scan_fallback` ignores `rc`-series tags — emits `b1` when `rc` tags exist (both scripts)

**File:** `firestarter_app/.github/scripts/update_version.py:61-78`; `firestarter/.github/scripts/update_version.py:64-81`

**Issue:** `BETA_VERSION_RE` (line 8 / line 12) accepts both `b` and `rc` pre-release identifiers (`(b|rc)[0-9]+`), so a caller can legally set `BETA_VERSION=1.2.3rc1`. However, `_git_tag_scan_fallback()` only queries git for tags matching `{base}b*` (line 65/68) and its internal `n_re` only matches `{base}b([0-9]+)` (line 71/74). If git already has tags `1.2.3rc1` and `1.2.3rc2` and `BETA_VERSION` is unset (relying on the fallback), the function returns `1.2.3b1` — silently ignoring the `rc` series. This creates a versioning inconsistency: the tag list shows `rc2` as the latest pre-release, but the script emits `b1`, which sorts *before* `rc1` under PEP 440 ordering.

Since the function is advertised as "Scan git tags for highest bN" in its docstring, the `rc` gap is at least a missing feature, but in practice it is a correctness bug because `BETA_VERSION_RE` promises to accept `rc` input and the caller has no warning that the fallback silently ignores it.

**Fix:** Either (a) restrict `BETA_VERSION_RE` to `b` only (eliminating the `rc` promise) and document this as out-of-scope, or (b) extend the fallback to also scan `{base}rc*` tags and pick the appropriate highest suffix across both series. Option (a) is lower-risk for v1.4 scope:

```python
# Option A: scope to beta-only, document rc as future work
BETA_VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+b[0-9]+$')
```

---

## Warnings

### WR-01: `get_version()` / `get_header_version()` — unclosed file handle on exception path (both scripts)

**File:** `firestarter_app/.github/scripts/update_version.py:15`; `firestarter/.github/scripts/update_version.py:18`

**Issue:** Both functions use `open(version_file)` without a `with` statement. The list comprehension `[line for line in open(version_file)]` completes successfully in the normal path (CPython reference-counts the handle closed after the comprehension), but this behavior is CPython implementation detail and not guaranteed by the language spec. Under other runtimes (PyPy, Jython) or when an exception is raised inside the comprehension, the handle may not be closed promptly.

**Fix:** Use `with open(version_file) as f: txt = f.readlines()` in both `get_version()` and `update_version()`.

---

### WR-02: `update_version()` write-path file handle never closed on exception (both scripts)

**File:** `firestarter_app/.github/scripts/update_version.py:32-43`; `firestarter/.github/scripts/update_version.py:35-46`

**Issue:** `fout = open(version_file, "w")` (without a `with` statement) followed by `fout.close()` at line 43/46. If an exception is raised between `open()` and `close()`, `fout` is never closed. On Windows this additionally holds a write lock. This is distinct from CR-01 (data loss on truncation); even if CR-01 is fixed with `os.replace`, the write handle should be managed with `with`.

**Fix:** Use `with open(version_file, "w") as fout:` (or the `os.fdopen` approach shown in CR-01 fix).

---

### WR-03: Version-parsing regex in `get_version()` / `get_header_version()` is over-permissive (both scripts)

**File:** `firestarter_app/.github/scripts/update_version.py:13`; `firestarter/.github/scripts/update_version.py:16`

**Issue:** The regex `r'^__version__ =(.\")...'` uses `(.")`  — a single arbitrary character followed by a quote — where the format requires exactly a space then a quote. The intent is to capture `' "'` (space + opening quote) so the rest of the line can be matched. The dot `.` matches any character, so lines like `__version__ =X"1.2.3"` or `__version__ =-"1.2.3"` would also be matched and parsed. In the firmware script the same issue exists: `r'^#define VERSION(.")...'` matches `#define VERSIONX"1.2.3"`.

While unlikely in practice (the version files are controlled), the read regex and the write regex are inconsistent: the write regex uses `"^(__version__ = )"` (space explicit), but the read regex uses `(.")`  (space implicit via dot). If the file ever has a malformed line, silent misparse is possible.

**Fix:** Make the read regex explicit:

```python
# App
rxs = r'^__version__ = "(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)(?P<pre>(b|rc)[0-9]+)?'

# Firmware
rxs = r'^#define VERSION "(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)(?P<pre>(b|rc)[0-9]+)?'
```

Note: the capture group `(.")`  is not used by name in either `get_version()` or `get_header_version()` — only the named groups `major/minor/patch/pre` are accessed via `.group()` — so removing the unnamed capture group is safe.

---

### WR-04: Test `test_beta_explicit_version` calls `calculate_version()` without the args it constructed — test asserts on a phantom `args` object (both test files)

**File:** `firestarter_app/tests/test_update_version.py:173-177`; `firestarter/tests/test_update_version.py:170-174`

**Issue:** The test constructs `args = update_version.parse_args()` (no arguments, so `args.beta=False, args.dry_run=False`), asserts `is_beta_mode(args)` is True (which passes because `GITHUB_REF` is set in env), then calls `update_version.calculate_version()` **with no arguments**. `calculate_version()` called without arguments calls `parse_args([])` internally and creates a fresh `args` Namespace — the `args` variable constructed on line 174 is **never used** in the actual execution path. The test exercises the function correctly by accident (env vars drive the beta path), but it does not test the `--beta` flag code path or `--set-version` code path. Additionally, the unused `args` makes the test appear to be testing a specific args object when it is not.

This is a test correctness issue: the test appears to validate a contract it does not actually enforce.

**Fix:** Either pass `args` to `calculate_version(args)` to test the args-driven path:

```python
args = update_version.parse_args(["--beta"])
assert update_version.is_beta_mode(args)
update_version.calculate_version(args)
```

Or remove the `args` construction if the intent is purely to test env-var-driven beta mode (and adjust the comment accordingly).

---

## Info

### IN-01: `GITHUB_OUTPUT` `pre` key absent from stable-path output — undocumented asymmetry

**File:** `firestarter_app/.github/scripts/update_version.py:191-194`; `firestarter/.github/scripts/update_version.py:194-197`

**Issue:** The beta path writes five keys to `GITHUB_OUTPUT`: `version`, `major`, `minor`, `patch`, `pre`. The stable path writes only four, omitting `pre`. Any downstream workflow step that unconditionally references `${{ steps.version.outputs.pre }}` will receive an empty string on the stable path rather than a clear error, making the conditional logic on that value silently incorrect. The current `build.yml` does not reference `pre` in tag_name (it uses `version`), so there is no immediate impact, but the asymmetry is undocumented in either script.

**Fix:** Add a comment in both scripts next to the stable-path `GITHUB_OUTPUT` block:

```python
# NOTE: 'pre' key is intentionally absent on the stable path (no pre-release suffix).
# Downstream steps must treat a missing 'pre' output as equivalent to empty string.
```

---

### IN-02: `build.yml` — `actions/setup-python@v4` (line 44) is a duplicate/stale step shadowed by `actions/setup-python@v5` at line 56

**File:** `firestarter/.github/workflows/build.yml:44-45` and `55-58`

**Issue:** Line 44 calls `uses: actions/setup-python@v4` with no `python-version` specified (uses runner default). Then line 55-58 calls `uses: actions/setup-python@v5` with `python-version: '3.11'`. The first call is a no-op because the second call immediately sets up the Python environment anyway. The stale `@v4` step without a version pin produces unpredictable Python versions on future runner updates, and the inconsistent version tags (`@v4` vs `@v5`) are confusing.

**Fix:** Remove the bare `actions/setup-python@v4` step at line 44-45. Keep only the `actions/setup-python@v5` step with an explicit `python-version`.

---

_Reviewed: 2026-05-20T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

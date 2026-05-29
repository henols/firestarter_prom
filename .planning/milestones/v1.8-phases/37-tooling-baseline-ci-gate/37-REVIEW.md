---
phase: 37-tooling-baseline-ci-gate
reviewed: 2026-05-27T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - firestarter_app/tools/check_mypy_watermark.py
  - firestarter_app/pyproject.toml
  - firestarter_app/.github/workflows/ci.yml
  - firestarter_app/.pre-commit-config.yaml
  - firestarter_app/.git-blame-ignore-revs
findings:
  critical: 1
  warning: 4
  info: 3
  total: 8
resolved:
  critical: 1
  warning: 2
  deferred_to_phase_42: [WR-01, WR-02]
  advisory_no_action: [IN-01, IN-02, IN-03]
  fix_commit: 8468d10
status: resolved
---

# Phase 37: Code Review Report

**Reviewed:** 2026-05-27
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Reviewed the genuinely-authored Phase 37 tooling artifacts (the mechanical whole-tree
`ruff format`/import-sort/`# noqa` baseline across `firestarter/**` and `tests/**` was
correctly out of scope and not examined). The config files (`pyproject.toml`,
`.github/workflows/ci.yml`, `.pre-commit-config.yaml`, `.git-blame-ignore-revs`) are largely
correct: the watermark regex parses the live `# mypy_error_watermark = 44` comment, the
observed mypy count is exactly 44 (verified by running mypy 2.1.0 against the tree), the
blame-ignore SHA `87f32c8` resolves to the real format commit, and the four-step CI gate is
wired in the documented order.

The dominant defect is in `check_mypy_watermark.py`: `count_mypy_errors()` discards mypy's
return code and infers the error count solely by regex-matching `Found (\d+) errors`. Any mypy
invocation that runs but does not emit that line — internal crash/traceback, a config-load
error, or a future output-format change — yields a silent count of `0`, which the gate reads as
"44 below watermark" and **passes** (even printing a misleading "lower the watermark" hint).
That converts a broken type checker into a green gate, which defeats the purpose of the gate.
Remaining findings concern version-skew between the pinned pre-commit hooks and the `>=` CI
deps (the watermark is version-sensitive), the pre-commit mypy hook running per-file without
watermark enforcement, and CWD fragility.

## Critical Issues

### CR-01: mypy gate silently passes when mypy fails to produce a "Found N errors" line

**File:** `firestarter_app/tools/check_mypy_watermark.py:32-41`
**Issue:** `count_mypy_errors()` ignores `result.returncode` entirely and derives the count only
from `re.search(r"Found (\d+) errors?", output)`. When the regex does not match it returns `0`.
mypy emits no "Found N errors" line in several non-success, non-zero-error situations:

- mypy crashes with an internal traceback (e.g. a plugin/stub bug, OOM, version mismatch)
- mypy aborts on a configuration error (e.g. an unrecognized `[tool.mypy]` option after a
  future mypy upgrade — recall the config already notes mypy 2.1.0 rejects `--python-version`)
- a future mypy changes the summary wording

In all of these the script reports `mypy errors: 0`, takes the `count < watermark` branch, prints
`INFO: 0 errors — 44 below watermark. Lower watermark...`, and **exits 0**. A type checker that
did not actually run is reported as a clean, comfortably-passing gate. This is a gate bypass: the
entire purpose of D-10 is to block new type errors, and a silent `0` is the most dangerous
possible failure mode because it also produces a "this is going great, tighten the ratchet"
message. I verified this empirically — feeding a simulated mypy traceback or config-error string
to the same regex returns `0`. (Note: the *binary-missing* case does fail loudly because
`subprocess.run(["mypy", ...])` raises an uncaught `FileNotFoundError`; only the "mypy ran but
said something unexpected" case is the silent one.)

**Fix:** Treat an unparseable result as a hard error, and validate the return code. mypy's
convention is: returncode `0` = no errors, `1` = type errors found, `>=2` = a real failure
(crash/config/usage). Distinguish them:
```python
def count_mypy_errors() -> int:
    result = subprocess.run(
        ["mypy", "firestarter/", "tests/"],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    if result.returncode >= 2:
        print(f"ERROR: mypy failed to run (exit {result.returncode}):\n{output}",
              file=sys.stderr)
        sys.exit(2)
    if result.returncode == 0:
        return 0
    m = re.search(r"Found (\d+) errors?", output)
    if not m:
        print(f"ERROR: mypy exited {result.returncode} but no error count was found:\n{output}",
              file=sys.stderr)
        sys.exit(2)
    return int(m.group(1))
```

## Warnings

### WR-01: Watermark is mypy-version-sensitive, but CI deps float (`>=`) while pre-commit pins exact

**File:** `firestarter_app/pyproject.toml:61-69`, `firestarter_app/.pre-commit-config.yaml:12-16`
**Issue:** The watermark count (44) is a function of the *exact* mypy version, the resolved stub
versions, and `python_version`. CI installs via `pip install -e .[test]`, whose specs are all
lower bounds: `mypy>=2.1.0`, `ruff>=0.15.14`, `types-pyserial>=3.5.0.20260519`. The first CI run
after mypy publishes (say) 2.2 will resolve a newer mypy whose error count almost certainly
differs from 44 — if it reports *more* errors the gate fails on a green PR with no code change;
if it reports *fewer* it silently loosens the ratchet. Meanwhile `.pre-commit-config.yaml` pins
ruff `v0.15.14` and mypy `v2.1.0` exactly, so a developer's local pre-commit and the CI gate can
diverge on tool version. The watermark is only meaningful against a fixed toolchain.
**Fix:** Pin the type/lint toolchain in `[test]` to the same versions the watermark was measured
against (or add an upper bound), e.g. `mypy>=2.1.0,<2.2`, `ruff>=0.15.14,<0.16`,
`types-pyserial==3.5.0.20260519`, so CI and pre-commit resolve the identical toolchain. Bump
both the pin and the watermark together when upgrading.

### WR-02: pre-commit mypy hook runs per-file with no watermark enforcement — inconsistent with CI gate

**File:** `firestarter_app/.pre-commit-config.yaml:11-16`
**Issue:** The `mirrors-mypy` hook as configured passes the set of *changed filenames* to mypy
rather than the project targets `firestarter/ tests/`, and it has no `args`/`files` scoping. Two
consequences: (1) it does not run the watermark gate at all (it just runs raw mypy and fails on
*any* error), so a commit touching a file that already contributes to the 44 baseline errors will
be **blocked locally** even though CI considers it within-watermark — pre-commit is stricter than
the authoritative gate, the inverse of what's intended; (2) per-file mypy resolves imports
differently than the whole-tree run, so its error set is not the same 44. Local pre-commit and CI
will disagree on type results.
**Fix:** Make the local hook mirror the CI gate. Either scope and run the watermark script as a
`repo: local` hook (`entry: python tools/check_mypy_watermark.py`, `pass_filenames: false`,
`always_run: true`), or at minimum scope the mirrors-mypy hook with
`files: ^(firestarter|tests)/` and `args: ["firestarter/", "tests/"]` plus
`pass_filenames: false` so it type-checks the same target set. As-is, document that local
pre-commit mypy is advisory and CI is authoritative (the scope note already concedes this for the
ruff `tools/` case; the mypy per-file divergence is a separate, undocumented gap).

### WR-03: Script assumes CWD is the repo root for both `pyproject.toml` and the mypy targets

**File:** `firestarter_app/tools/check_mypy_watermark.py:21,35`
**Issue:** `get_watermark()` reads `Path("pyproject.toml")` (relative) and `count_mypy_errors()`
runs `mypy firestarter/ tests/` (relative). Both only work when the process CWD is the
`firestarter_app` repo root. CI happens to satisfy this, but invoking the script from any other
directory (a common developer mistake, or a future workflow that sets `working-directory`) fails:
`get_watermark()` raises an uncaught `FileNotFoundError` traceback — verified by running it from
`/tmp`. The script's own header advertises exit code 2 for "configuration error," but a missing
`pyproject.toml` instead produces an unhandled traceback (exit 1), inconsistent with the
documented contract.
**Fix:** Anchor paths to the script location / repo root rather than CWD:
```python
REPO_ROOT = Path(__file__).resolve().parent.parent
...
text = (REPO_ROOT / "pyproject.toml").read_text()
...
["mypy", str(REPO_ROOT / "firestarter"), str(REPO_ROOT / "tests")]
```
and/or wrap the read in a `try/except FileNotFoundError` that exits 2 with a clear message, to
honor the documented exit-code contract.

### WR-04: Watermark comment regex is unanchored and order-dependent

**File:** `firestarter_app/tools/check_mypy_watermark.py:22`
**Issue:** `re.search(r"#\s*mypy_error_watermark\s*=\s*(\d+)", text)` scans the entire
`pyproject.toml` and matches the first occurrence anywhere in the file, not specifically the one
inside `[tool.mypy]`. The docstring and the error message both assert the value lives "in
[tool.mypy]," but nothing enforces that. If a second mention of `mypy_error_watermark` is ever
added above the real one (e.g. a historical note, a changelog line, a different table), the gate
silently reads the wrong number. It also accepts the comment placed in any table, contradicting
its own documentation.
**Fix:** Either tighten the regex to require it be a standalone comment line
(`re.search(r"^\s*#\s*mypy_error_watermark\s*=\s*(\d+)\s*$", text, re.MULTILINE)`) and/or
constrain the search to the `[tool.mypy]` section by slicing the text at the next `[` table
header. At minimum add a guard that errors (exit 2) if more than one match is found.

## Info

### IN-01: `count < watermark` branch is advisory-only (no auto-ratchet) — confirm intent

**File:** `firestarter_app/tools/check_mypy_watermark.py:54-58`
**Issue:** When the count drops below the watermark the script only prints an INFO nudge to lower
the value manually; it does not fail CI or update `pyproject.toml`. This is a reasonable design
(manual ratchet), but it means the watermark can drift upward-stale: someone fixes errors, the
hint scrolls past in CI logs, and the watermark stays at 44 indefinitely, weakening the gate over
time. Acceptable as documented, but worth a one-line note in the script header that the ratchet is
intentionally manual so it isn't mistaken for a bug.
**Fix:** Optionally add `# NOTE: ratchet is manual by design — CI does not fail on counts below
the watermark.` to the docstring, or consider failing when `count < watermark` to force the
ratchet (stricter teams prefer this).

### IN-02: Watermark stored as a TOML comment, not a parseable key — brittle and invisible to tooling

**File:** `firestarter_app/pyproject.toml:115`
**Issue:** `# mypy_error_watermark = 44` is a comment, so it is invisible to any TOML parser and is
only reachable via the regex hand-roll in the script. (Verified the regex matches the live value.)
A real key under a custom table (e.g. `[tool.firestarter_ci] mypy_error_watermark = 44`) would be
parseable with `tomllib` (stdlib in 3.11, which is what CI runs) and far less fragile than regex.
The comment form was presumably chosen to keep it out of `[tool.mypy]` (where mypy would reject an
unknown key), which is a valid constraint — hence Info, not Warning.
**Fix:** Move the watermark to a parseable custom table and read it with `tomllib`:
```toml
[tool.firestarter_ci]
mypy_error_watermark = 44
```
Eliminates WR-04's regex ambiguity at the same time.

### IN-03: `# mypy_error_watermark = 44` count differs from research estimate (41 vs 44) — already documented

**File:** `firestarter_app/pyproject.toml:115`
**Issue:** Per the scope note this delta (+3 over the estimated 41) is known and accepted; I
verified the live count is exactly 44 against mypy 2.1.0 / python_version 3.9, so the recorded
value is accurate as of this commit. Recording for completeness only — not a new finding. The
value's accuracy is contingent on the toolchain pin discussed in WR-01.
**Fix:** None required; keep the watermark and the toolchain version in lockstep when upgrading.

---

## Resolution Log (orchestrator, 2026-05-27)

Fixes applied in `firestarter_app` commit `8468d10` — `fix(37): harden mypy watermark gate against tool failure (CR-01, WR-03, WR-04)`:

- **CR-01 (critical) — RESOLVED.** `count_mypy_errors()` now distinguishes three outcomes: a parseable `Found N errors` count, a genuinely-clean tree (`exit 0` / `Success: no issues found` → 0), and a tool/config failure (mypy ran but produced no parseable count, or non-zero with unexpected output → `sys.exit(2)`). A broken type checker can no longer be reported as a silent `0` that passes the gate. Verified empirically against simulated crash/config-error/garbage outputs (all route to exit 2) while the normal 44/clean/0 paths are preserved.
- **WR-03 (warning) — RESOLVED.** Paths are now anchored to `REPO_ROOT = Path(__file__).resolve().parent.parent`; the watermark read and the mypy subprocess (`cwd=REPO_ROOT`) are CWD-independent. Verified the gate runs identically from the repo root and from `/tmp`.
- **WR-04 (warning) — RESOLVED.** The watermark regex is now anchored to a comment line via `re.MULTILINE` (`^\s*#\s*mypy_error_watermark...`).

Deferred (intentional — milestone-wide concerns, not Phase 37 bugs):

- **WR-01 (toolchain version pinning vs `>=` floors)** → **Phase 42** (final ruff+mypy quality sweep). The watermark/version lockstep is a milestone-wide tooling-policy decision; the `>=` floors were the plan's deliberate choice. Re-evaluate pinning + watermark together in the Phase 42 sweep.
- **WR-02 (pre-commit mypy hook stricter/per-file vs CI)** → **Phase 42.** Related to the documented pre-commit-vs-CI scope divergence; CI remains the authoritative gate. Revisit when `tools/` is baselined.

Advisory, no action (design notes): **IN-01** (manual ratchet is by design), **IN-02** (TOML-key vs comment — a future refactor; would dissolve WR-04), **IN-03** (the 44-vs-41 delta is documented and verified accurate).

_Reviewed: 2026-05-27_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

---
phase: 37-tooling-baseline-ci-gate
verified: 2026-05-27T13:31:23Z
status: passed
score: 10/10 must-haves verified
overrides_applied: 0
re_verification: false
---

# Phase 37: Tooling Baseline + CI Gate — Verification Report

**Phase Goal:** ruff, ruff-format, and mypy are configured and enforced in CI. All existing code
is formatted and linted to a green baseline (using `ruff check --add-noqa` for legacy violations,
not hand-fixing everything). From this phase forward, touched modules must be clean; the CI gate
fails the build on any new violation.

**Verified:** 2026-05-27T13:31:23Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `ruff check firestarter/ tests/` exits 0 on the full tree | VERIFIED | Live run: "All checks passed!" exit 0 |
| 2 | `ruff format --check firestarter/ tests/` exits 0 on the full tree | VERIFIED | Live run: "30 files already formatted" exit 0 |
| 3 | 162-test Phase 36 suite + 2 xfail + 29 syrupy snapshots pass after mechanical reformat | VERIFIED | Live run: "162 passed, 2 xfailed in 13.73s"; "29 snapshots passed." |
| 4 | `.git-blame-ignore-revs` records the whole-tree ruff format commit SHA | VERIFIED | SHA 87f32c8cdc2bb10db90ad278accd241adfe06bb9 resolves to commit "style(37-01): ruff format whole-tree (D-01 step a)" |
| 5 | Mypy error count measured and recorded as integer watermark in pyproject.toml | VERIFIED | `# mypy_error_watermark = 44` at pyproject.toml line 115 |
| 6 | `python tools/check_mypy_watermark.py` exits 0 when count is at/below watermark | VERIFIED | Live run: "mypy errors: 44 (watermark: 44)" "OK: error count at watermark." exit 0 |
| 7 | `pytest tests/ --cov=firestarter --cov-fail-under=50` passes at ~51% coverage | VERIFIED | Live run: "Total coverage: 51.16%" "Required test coverage of 50% reached." exit 0 |
| 8 | types-pyserial and pytest-cov available via test extra | VERIFIED | pyproject.toml test extra: pytest-cov>=7.1.0, types-pyserial>=3.5.0.20260519 |
| 9 | CI runs ruff check, ruff format --check, mypy watermark gate, and pytest with coverage floor — in that order, in the existing single ci job | VERIFIED | ci.yml step order confirmed: indices [284, 315, 368, 450] in order; all-PR trigger has no branches filter |
| 10 | Pre-commit config committed with hook order ruff-check then ruff-format then mypy | VERIFIED | .pre-commit-config.yaml: ruff-pre-commit v0.15.14 [ruff-check, ruff-format], mirrors-mypy v2.1.0 [mypy + types-pyserial] |

**Score:** 10/10 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/pyproject.toml` | [tool.ruff] + [tool.ruff.lint] + [tool.ruff.format] + [tool.mypy] + [[tool.mypy.overrides]] config blocks | VERIFIED | All blocks present; select=["E","F","I","UP"], extend-ignore=["E501"], target-version="py39", mypy python_version="3.9", disallow_untyped_defs=false; 6 strict-island modules in overrides; no fail_under in coverage config |
| `firestarter_app/.git-blame-ignore-revs` | Full 40-char SHA of whole-tree ruff format commit | VERIFIED | SHA 87f32c8cdc2bb10db90ad278accd241adfe06bb9; contributor-setup comment present; git cat-file -t → "commit" |
| `firestarter_app/tools/check_mypy_watermark.py` | stdlib-only mypy watermark count-comparison gate (exit 0/1/2) | VERIFIED | Exists; def main(); shebang; __main__ guard; stdlib-only imports (re, subprocess, sys, pathlib); REPO_ROOT-anchored paths (WR-03 fix); re.MULTILINE watermark regex (WR-04 fix); returncode-aware error handling (CR-01 fix) |
| `firestarter_app/.github/workflows/ci.yml` | Extended single ci job with 4 gate steps + all-PR trigger | VERIFIED | pull_request has no branches filter; push still branches:[main]; .[test] install; 4 steps in documented order |
| `firestarter_app/.pre-commit-config.yaml` | Pinned ruff-pre-commit + mirrors-mypy hooks in order ruff-check, ruff-format, mypy | VERIFIED | ruff-pre-commit rev v0.15.14; mirrors-mypy rev v2.1.0; hook order confirmed; no --fix on ruff-check; types-pyserial in mypy additional_dependencies |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| pyproject.toml [tool.ruff.lint] | ruff check / ruff format --check | ruff reads config from project root | VERIFIED | select=["E","F","I","UP"] confirmed; live ruff check exits 0 |
| .git-blame-ignore-revs | git blame | git config blame.ignoreRevsFile | VERIFIED | SHA resolves to commit "style(37-01): ruff format whole-tree"; contributor-setup comment documents the `git config` command |
| tools/check_mypy_watermark.py | pyproject.toml mypy_error_watermark comment | regex read of the watermark integer (re.MULTILINE, anchored to comment line) | VERIFIED | Reads `# mypy_error_watermark = 44` → 44; exits 0 |
| tools/check_mypy_watermark.py | mypy firestarter/ tests/ | subprocess + parse 'Found N errors' | VERIFIED | REPO_ROOT-anchored subprocess call; handles returncode 0, 1, >=2; exits 0 at watermark 44 |
| ci.yml | tools/check_mypy_watermark.py | ci.yml step invokes the Plan 02 script | VERIFIED | Step "mypy type check (watermark gate)": `python tools/check_mypy_watermark.py` |
| ci.yml | .[test] extra (ruff, mypy, pytest-cov, types-pyserial) | pip install -e .[test] before gate steps | VERIFIED | Install step confirmed; test extra carries all 4 new deps |

---

### Data-Flow Trace (Level 4)

Not applicable. Phase 37 produces tooling infrastructure artifacts (config files, a gate script, CI
configuration) — not components that render dynamic data from a data source. The gate script's
"data" is the mypy error count, verified end-to-end by the live `python tools/check_mypy_watermark.py`
run (exit 0, correct count printed).

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| ruff lint gate passes on green tree | `ruff check firestarter/ tests/` | "All checks passed!" exit 0 | PASS |
| ruff format gate passes on green tree | `ruff format --check firestarter/ tests/` | "30 files already formatted" exit 0 | PASS |
| mypy watermark gate exits 0 at watermark | `python tools/check_mypy_watermark.py` | "mypy errors: 44 (watermark: 44)\nOK: error count at watermark." exit 0 | PASS |
| watermark gate script is lint-clean | `ruff check tools/check_mypy_watermark.py` | "All checks passed!" exit 0 | PASS |
| pytest + coverage gate passes 50% floor | `pytest tests/ --cov=firestarter --cov-fail-under=50 -q` | "Total coverage: 51.16%" exit 0 | PASS |
| 162 tests + 2 xfail + 29 snapshots intact | `pytest tests/ -q` | "162 passed, 2 xfailed" "29 snapshots passed." | PASS |
| Blame-ignore SHA resolves to format commit | `git -C firestarter_app cat-file -t 87f32c8c...` | "commit"; log shows "style(37-01): ruff format whole-tree" | PASS |
| pre-commit YAML structure | Python yaml parse assertion | "pre-commit OK" | PASS |
| ci.yml YAML structure and step order | Python yaml parse assertion | "ci.yml OK" (steps in documented order) | PASS |

---

### Probe Execution

No probes defined for this phase. Step 7b behavioral spot-checks above cover the runnable verification surface.

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| TOOL-01 | 37-01-PLAN.md | ruff + ruff-format configured in pyproject.toml; baseline pass makes tree green; selected rule categories documented | SATISFIED | [tool.ruff.lint] with documented E/F/I/UP rationale comment; ruff check and ruff format --check both exit 0; 315 noqa directives record legacy suppressions |
| TOOL-02 | 37-02-PLAN.md | mypy configured with gradual per-module strategy + types-pyserial; initial error count recorded as watermark; "no new errors" gate | SATISFIED | [tool.mypy] disallow_untyped_defs=false global; 6-module strict-island [[tool.mypy.overrides]]; watermark=44 in comment; check_mypy_watermark.py gates at/below watermark; types-pyserial in test extra |
| TOOL-03 | 37-03-PLAN.md | CI workflow runs ruff check, ruff format --check, mypy gate, pytest with coverage gate; fails on violations; pre-commit config committed | SATISFIED | ci.yml: 4-step gate in order; all-PR trigger (no branches filter); .[test] install; .pre-commit-config.yaml: pinned hooks in order ruff-check→ruff-format→mypy |

All three phase-37 requirements (TOOL-01, TOOL-02, TOOL-03) from REQUIREMENTS.md are satisfied. No
orphaned requirements found for this phase.

---

### Code Review Findings — Resolution Status

The code review (37-REVIEW.md) raised 1 critical + 4 warnings + 3 info items.

| Finding | Severity | Resolution | Evidence |
|---------|----------|------------|----------|
| CR-01: mypy gate silent-pass on tool failure | Critical | RESOLVED in commit 8468d10 | `count_mypy_errors()` now checks returncode: 0→return 0, 1+regex→return N, else→sys.exit(2); "Success: no issues found" case handled; verified present in live file |
| WR-03: CWD fragility | Warning | RESOLVED in commit 8468d10 | `REPO_ROOT = Path(__file__).resolve().parent.parent` anchors both pyproject.toml read and mypy subprocess cwd |
| WR-04: Unanchored watermark regex | Warning | RESOLVED in commit 8468d10 | `re.search(r"^\s*#\s*mypy_error_watermark...", text, flags=re.MULTILINE)` anchored to comment line |
| WR-01: Toolchain version pinning vs >= floors | Warning | DEFERRED to Phase 42 | Intentional milestone-wide policy decision |
| WR-02: pre-commit mypy hook per-file vs CI watermark | Warning | DEFERRED to Phase 42 | CI remains authoritative gate |
| IN-01, IN-02, IN-03 | Info | Advisory, no action | Design notes acknowledged |

---

### Anti-Patterns Found

Scanned all Phase 37 modified/created files.

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| No findings | — | — | — |

No TBD, FIXME, or XXX debt markers found in any Phase 37 file. No unreferenced debt markers. No
stub patterns (placeholder returns, empty handlers, hardcoded empty data) in the tooling artifacts.

The 315 `# noqa` directives across `firestarter/` and `tests/` are the intentional legacy
suppression baseline (TOOL-01 design: `--add-noqa` pass, not hand-fixing). These are NOT stubs —
they are the documented suppression record for pre-existing violations that will be addressed as
modules are touched in Phases 38–42.

---

### Human Verification Required

None. Phase 37 is pure software/tooling infrastructure. All gate behaviors are verified
programmatically by running the actual tools:

- Linter (ruff): run and exit code checked
- Formatter (ruff format --check): run and exit code checked
- Mypy watermark gate: run and output/exit code checked
- Coverage gate (pytest --cov-fail-under=50): run and exit code checked
- CI YAML structure: parsed and asserted programmatically
- Pre-commit YAML structure: parsed and asserted programmatically
- SHA provenance: git cat-file verified
- Test suite integrity: 162 passed, 2 xfailed, 29 snapshots confirmed live

No hardware, no user-facing UI, no visual appearance, no real-time behavior, no external service
integration requiring human judgment.

---

## Gaps Summary

None. All must-haves verified. Phase goal achieved.

---

_Verified: 2026-05-27T13:31:23Z_
_Verifier: Claude (gsd-verifier)_

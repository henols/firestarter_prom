---
phase: 11-coverage-matrix-db-inconsistency-audit
reviewed: 2026-05-19T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - firestarter_app/tools/audit_coverage_matrix.py
  - firestarter_app/tests/test_audit_coverage_matrix.py
findings:
  critical: 1
  warning: 4
  info: 9
  total: 14
status: issues_found
---

# Phase 11: Code Review Report

**Reviewed:** 2026-05-19
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Phase 11 lands a 1546-line desk-side audit tool plus a 600-line test scaffold.
The implementation is broadly sound: idempotence contracts are honored (LF
newlines, sorted dict iteration, no timestamps, sort_keys JSON), the
`finding_hash` truncation is justified by D-13, and the exit-code matrix at
`generate_matrix` matches D-03. Tests pass (10/10) against the live DB.

Adversarial review surfaces one BLOCKER plus several quality concerns, all
clustered in the same area: the module-top `from firestarter.database import
EpromDatabase` is unused but eagerly imported, which couples the standalone
tool to the editable install layout despite the docstring claim that the tool
"runs from any cwd." If `firestarter_app` is not pip-installed (or installed
non-editably without `tools/` accessible), the tool fails at module import
before any work begins.

Remaining findings are quality/maintainability items: dead branches in
`generate_matrix`, an unused-parameter API leak (`detect_resolved_baseline`'s
`next_n_holder`), substring-based test assertions that risk false positives
on future DB drift, and several test-side import oddities (`__import__` with
`fromlist=...` where a normal import would suffice).

No security defects detected. Pulse-bucket parsing fail-fast is intentional
(Pitfall 3) and the truncated SHA1 ID is non-cryptographic by design (D-13).

## Critical Issues

### CR-01: Dead module-import couples tool to editable-install layout

**File:** `firestarter_app/tools/audit_coverage_matrix.py:45`
**Issue:** The line `from firestarter.database import EpromDatabase  # noqa:
F401 — singleton kept available for §3/§4 lookups` imports a name that is
**never referenced** anywhere in the 1546-line file. Verified via
`grep -n "EpromDatabase"` — only the import itself and the docstring comment
match. §3 (`emit_full_enumeration`) and §4 (`detect_hazard`,
`detect_correctness`, `detect_variance`, `emit_defects`) operate directly on
the raw `chip_database.json` dict via `chip["programming"][...]` access; none
calls into `EpromDatabase`.

The import is not free — `firestarter.database` is the host-package singleton
that pulls in `pyserial` and the full pinout-translation graph. The tool's
docstring at line 11 claims `Run from any cwd`, and its CLI entrypoint
(`main()` → `generate_matrix()` → JSON file I/O only) does not need any
firestarter runtime. The `# noqa: F401` annotation tells linters to ignore
the unused import, so a future maintainer running ruff/flake8 gets no
warning that the import is dead.

Concrete failure mode: any consumer who copies `audit_coverage_matrix.py`
into a sibling repo, or runs it against a fresh checkout where
`pip install -e firestarter_app` has not been done, gets an `ImportError` at
module top before the tool produces its first byte of output. This breaks
the "desk-side audit tool, no install required" framing of the planning
artifacts.

**Fix:** Remove the import. If a future wave needs `EpromDatabase`, re-add
it then. Drop the noqa annotation so flake8 catches re-introductions.

```python
# Delete this line entirely:
from firestarter.database import EpromDatabase  # noqa: F401 — singleton kept available for §3/§4 lookups
```

If the intent is to keep the singleton warmed up for some future expansion,
that comment belongs in a phase plan, not as a load-bearing import line.

## Warnings

### WR-01: `detect_resolved_baseline` declares an unused parameter

**File:** `firestarter_app/tools/audit_coverage_matrix.py:728-748`
**Issue:** The function signature is `detect_resolved_baseline(ledger,
next_n_holder)`, but the body never reads `next_n_holder`. Two call sites
(`generate_matrix:1434` and `:1449`) both pass `[1]` as that argument,
suggesting the caller assumed the function uses it. This is a misleading
API: a future change that needs to bump the counter when seeding the
baseline will silently pass through without effect, because the
single-element-list "mutable counter" idiom only works if the callee
actually mutates it.

The function does set `ledger[h] = "DEFECT-COV-00"` directly without using
the holder. Since NN=00 is reserved (per the docstring at line 731-732),
this is fine — but the parameter is purely decorative noise.

**Fix:** Remove the unused parameter and update both call sites.

```python
def detect_resolved_baseline(ledger):
    """Seed `DEFECT-COV-00` into the ledger if absent (D-15 RESOLVED baseline)."""
    h = finding_hash(
        "HAZARD",
        "pinout_vs_algorithm",
        (["DIP28_2764", "DIP28_28C256"], 0x07, "Flash/EEPROM"),
    )
    if h not in ledger:
        ledger[h] = "DEFECT-COV-00"

# Call sites: drop the [1] holder argument.
detect_resolved_baseline(check_ledger)  # line 1434
detect_resolved_baseline(ledger)        # line 1449
```

### WR-02: Dead branch `if start_n < 1: start_n = 1` is unreachable

**File:** `firestarter_app/tools/audit_coverage_matrix.py:1456-1458`
**Issue:**

```python
start_n = max([0] + existing_ns) + 1
if start_n < 1:
    start_n = 1
```

`max([0] + existing_ns)` is always `>= 0` because the literal `0` is in the
list. Adding 1 guarantees `start_n >= 1`. The `if start_n < 1` branch is
structurally unreachable.

This is exactly the class of dead-defensive-code that masks a real bug
(e.g. if a refactor changes `max([0] + ...)` to `max(existing_ns)`, the
guard would matter — but then the guard would also need to handle
`ValueError` on empty `existing_ns`). The current shape is misleading.

**Fix:** Remove the redundant branch.

```python
start_n = max([0] + existing_ns) + 1
next_n_holder = [start_n]
```

### WR-03: Tests assert numeric substrings without anchoring — false-positive risk

**File:** `firestarter_app/tests/test_audit_coverage_matrix.py:388-391`
**Issue:** `test_summary_stats` asserts the four magic numbers via plain
substring matching:

```python
assert "734" in body
assert "339" in body
assert "212" in body
assert "127" in body
```

These are not anchored. The matrix body contains a §2 reconciliation table
with old/new/delta columns (e.g. "Old=743", "Δ=-9"). It also embeds
per-algorithm histogram counts, plus prose like "212 chips" inside section
headers (e.g. "Per-pinout class — algo 0x07 (212 chips)" at line 350 of the
tool source).

Concrete failure: if a future DB regen drops `algo-0x07` count from 212 to
211, the matrix body contains "Per-pinout class — algo 0x07 (212 chips)"
hardcoded in the section header literal at `emit_summary:350`, so
`"212" in body` STILL passes despite the actual count being 211 — a
false-negative on a real regression. The summary table row would have
`| algo-0x07 | 211 | ...` but the literal "212 chips" prose remains.

**Fix:** Anchor the assertions to the actual summary table row, e.g.

```python
# Stronger: assert the actual table row literal.
assert "| In-scope (algo 0x07 + 0x08)  | 339 |" in body or \
       "| In-scope (algo 0x07 + 0x08) | 339   |" in body
```

Or parse the summary table and compare cell values directly. The current
shape risks silent passes when the matrix and tool drift apart.

Note the section header at `audit_coverage_matrix.py:350,360` also hardcodes
"(212 chips)" and "(127 chips)" as prose literals — these become stale on
any DB regen and the test cannot detect that drift. Consider replacing
those header literals with `f"### Per-pinout class — algo 0x07 ({n} chips)"`
sourced from `summary`.

### WR-04: `pulse_coverage` silently skips HAZARD and VARIANCE cross-refs

**File:** `firestarter_app/tools/audit_coverage_matrix.py:1190-1206`
**Issue:** When a pulse-bucket cell is uncovered, the code attempts to
populate a "cross-ref" note by iterating `findings`:

```python
for f in findings:
    sig = f.get("signature")
    if sig is None or len(sig) < 5:
        continue
    f_algo, _f_pinout, _f_size, _f_mfg, f_alias = sig[:5]
```

The `len(sig) < 5` guard structurally excludes:
- HAZARD findings (signature length = 3: list-of-pinouts, algo, etype)
- VARIANCE findings (signature length = 4: algo, pinout, size, mfg)
- DEFECT-COV-00 baseline (not in `findings` anyway)

Only CORRECTNESS findings (5-tuple) are ever cross-referenced from
pulse-bucket cells. This may be intentional (CORRECTNESS is the pulse-axis
finding type), but:

1. The behavior is silently filter-by-length, not filter-by-tier. A future
   detector that emits a 5-tuple HAZARD signature would slip through.
2. D-10 (per the §5 prose at line 1262) says uncovered cells cross-ref §4
   findings "where the gap is structural" — HAZARD gaps are structural,
   but cannot be cross-referenced from pulse buckets here.

**Fix:** Replace the implicit length guard with an explicit tier check, and
document the intent:

```python
# Pulse-bucket cross-refs target CORRECTNESS (pulse-axis) findings only.
# HAZARD/VARIANCE gaps are cross-referenced from pinout/size axes instead.
for f in findings:
    if f.get("axis") != "pulse_duration_outlier":
        continue
    sig = f["signature"]
    f_algo, _f_pinout, _f_size, _f_mfg, f_alias = sig
    ...
```

This makes the intent explicit and survives future signature-shape changes.

## Info

### IN-01: `parse_pulse_us` will crash with unfriendly ValueError on Algorithm-Controlled rows

**File:** `firestarter_app/tools/audit_coverage_matrix.py:86-90`
**Issue:** The function fail-fasts on any string not ending in `" us"`, raising
`ValueError(f"Unexpected pulse_duration shape: {s!r}")`. Empirically the live
DB has no in-scope rows with non-`" us"` values (verified — 339/339 in-scope
rows end in `" us"`). However, the DB *does* contain `"pulse_duration":
"Algorithm Controlled"` for some out-of-scope rows.

If a future build_db.py regen introduces an `"Algorithm Controlled"` row
into algo-0x07 or algo-0x08 scope, the tool hard-crashes mid-traversal in
`compute_summary:286` with no row context. The user sees the raw
`ValueError: Unexpected pulse_duration shape: 'Algorithm Controlled'` and
must `grep` the DB to find which row caused it.

**Fix:** Wrap the call site to surface chip context, or extend `parse_pulse_us`
to return `None` for known non-numeric forms and have callers skip.

```python
def parse_pulse_us(s, *, chip_label=""):
    if not isinstance(s, str) or not s.endswith(" us"):
        raise ValueError(
            f"Unexpected pulse_duration shape for {chip_label}: {s!r}"
        )
    return int(s[:-3])
```

### IN-02: Inconsistent defensive vs direct dict access for the same field

**File:** `firestarter_app/tools/audit_coverage_matrix.py:288, 505`
**Issue:** `chip_id_check` is accessed two ways in the same file:

- Line 288 (`compute_summary`): `bool(chip.get("programming", {}).get("chip_id_check", False))`
- Line 505 (`_enum_row`): `bool(chip["programming"]["chip_id_check"])` — direct, no default

Same field, same code path (both iterate `rows`), inconsistent style. The
direct access at 505 will KeyError on a malformed row that compute_summary
silently handled. Either both should defensive (preferred — matches Pitfall
3 fail-fast at the boundary) or both should be direct (acceptable if schema
is trusted).

**Fix:** Pick one style and apply consistently. Recommended: defensive
`.get(..., default)` since `compute_summary` already does it, and the
schema is owned upstream (not by this tool).

### IN-03: Dead/redundant `_json` alias in tests

**File:** `firestarter_app/tests/test_audit_coverage_matrix.py:325, 552`
**Issue:** Both `test_ledger_id_reuse` and `test_golden_file_matches` do
`import json as _json` mid-function despite no `json` shadowing concern.
The shadowing would only be needed if `json` were a local name (it isn't —
no top-level `import json` in the test file). The `_json` alias adds noise
without protection.

**Fix:** Use `import json` directly.

```python
import json
seeded_parsed = json.loads(seeded_ledger_path.read_text(encoding="utf-8"))
```

### IN-04: Obfuscated `__import__` call where a normal import would suffice

**File:** `firestarter_app/tests/test_audit_coverage_matrix.py:327`
**Issue:**

```python
with open(
    __import__("tools.audit_coverage_matrix", fromlist=["DB_FILE"]).DB_FILE,
    encoding="utf-8",
) as f:
```

The `__import__(name, fromlist=[...])` idiom is for dynamic import name
construction. Here the name is a hard literal. Three lines above, the test
already has `from tools.audit_coverage_matrix import (generate_matrix,
finding_hash, detect_hazard, iter_in_scope_rows)` — simply adding `DB_FILE`
to that import list is the standard solution.

**Fix:**

```python
from tools.audit_coverage_matrix import (
    generate_matrix,
    finding_hash,
    detect_hazard,
    iter_in_scope_rows,
    DB_FILE,
)
...
with open(DB_FILE, encoding="utf-8") as f:
    db_raw = json.load(f)
```

### IN-05: Mixed `os.path` and `pathlib.Path` usage in the same module

**File:** `firestarter_app/tools/audit_coverage_matrix.py:48-64, 694-705, 1495`
**Issue:** Path-construction is `os.path.join` / `os.path.dirname` (lines
48-64) but file I/O is `Path(...).write_text(...)` / `Path(...).read_text(...)`
(lines 694-705, 1495). The comment at line 47 documents the os.path
choice as "lifted verbatim from check_dispatch.py:23-30 per D-01" — so the
inconsistency is intentional, but a reader has to know to look up D-01.

**Fix:** Either consolidate on `pathlib.Path` throughout (recommended for
modern code), or add a one-line comment above the `Path(ledger_path).read_text`
calls cross-referencing back to D-01 so the reader knows the mix is
deliberate. Currently the `import os` plus `from pathlib import Path` at the
top reads as "the author hadn't decided yet."

### IN-06: Stale prose in section header literals

**File:** `firestarter_app/tools/audit_coverage_matrix.py:350, 360`
**Issue:** The header strings hardcode chip counts that the dynamic table
just below recomputes:

```python
parts.append("### Per-pinout class — algo 0x07 (212 chips)")  # line 350
...
parts.append("### Per-pinout class — algo 0x08 (127 chips)")  # line 360
```

These become stale on any DB regen — the table below shows the live count
(e.g. 211) but the header still claims 212. This is also why WR-03's
substring test passes spuriously.

**Fix:** Source the count from `summary`:

```python
parts.append(f"### Per-pinout class — algo 0x07 ({summary['algo_counter'][0x07]} chips)")
parts.append(f"### Per-pinout class — algo 0x08 ({summary['algo_counter'][0x08]} chips)")
```

### IN-07: `md_table` does no defensive `|` escaping at the table-construction level

**File:** `firestarter_app/tools/audit_coverage_matrix.py:225-248`
**Issue:** `md_table` assumes every cell is `|`-safe. `_enum_row` carefully
calls `_md_escape` on every cell (good), but other callers of `md_table` do
not — `emit_summary`'s `top_rows`, `algo_rows`, `pin07_rows` etc. pass raw
strings/ints/bools straight in. `emit_defects`'s `resolved_table_rows` and
`table_rows` also pass `finding["title"]`, `finding["root_cause_hypothesis"]`
verbatim — these are f-strings constructed from DB content.

Empirically the DB contains no `|` characters in manufacturer names, part
numbers, or pinout keys. But the tool's robustness invariant — "rendering
must remain robust" per the `_md_escape` docstring at line 491-493 — is
only honored at one of ~10 call sites.

**Fix:** Apply `_md_escape` inside `md_table` to every cell, then callers
do not need to remember:

```python
def md_table(headers, rows):
    str_headers = [_md_escape(h) for h in headers]
    str_rows = [[_md_escape(c) for c in r] for r in rows]
    ...
```

Then `_enum_row`'s redundant `_md_escape` wrapping can also be dropped.

### IN-08: Section "Wave 1" docstring out of date

**File:** `firestarter_app/tools/audit_coverage_matrix.py:1-35`
**Issue:** The module docstring says "Wave 1 lands §1 (Summary Statistics) +
§2 (DB Count Reconciliation). §3/§4/§5 are placeholder headers populated by
Waves 2-4." The file at HEAD already has full §3/§4/§5 implementations
(`emit_full_enumeration`, `emit_defects`, `emit_bench_coverage`). The
docstring is stale historical context, not a description of current state.

**Fix:** Update the docstring to describe the shipped state (all five
sections wired up, with brief one-line summaries of what each does).

### IN-09: `generate_matrix` doc says "Wave 1: only DB parse-error case can return 1"

**File:** `firestarter_app/tools/audit_coverage_matrix.py:1383-1390, 1535-1537`
**Issue:** Two docstrings (the function and the `--check` argparse help)
reference "Wave 1" / "Wave 3+" gating language that no longer applies. The
function now mints IDs and the `--check` drift gate is live (see
test_exit_codes step 2 returncode=1 on empty ledger). The docstrings should
describe shipped behavior.

**Fix:** Replace Wave-historical phrasing with steady-state:

```python
def generate_matrix(output, ledger_path, check=False):
    """Generate the coverage matrix + ledger.

    Returns: 0 on clean generate (or `--check` with no new findings);
             1 on DB parse error, ledger parse error, or `--check` with
             at least one finding hash absent from the ledger (drift).
    """
```

---

_Reviewed: 2026-05-19_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

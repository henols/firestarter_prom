---
phase: 39-database-cleanup-chip-resolver
reviewed: 2026-05-27T00:00:00Z
depth: deep
files_reviewed: 7
files_reviewed_list:
  - firestarter_app/firestarter/chip_resolver.py
  - firestarter_app/tests/test_chip_resolver.py
  - firestarter_app/firestarter/main.py
  - firestarter_app/firestarter/serial_comm.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/database.py
  - firestarter_app/firestarter/constants.py
findings:
  critical: 0
  warning: 0
  info: 2
  total: 2
status: issues_found
---

# Phase 39: Code Review Report

**Reviewed:** 2026-05-27
**Depth:** deep (cross-file: import graph, not-found contract trace, named-import completeness, consistency-check return-type preservation)
**Files Reviewed:** 7 (2 new, 5 modified)
**Status:** issues_found (2 Info-level nits; no BLOCKERs, no WARNINGs)

## Summary

Phase 39 is a clean mechanical refactor in three waves: the chip-resolver chokepoint
(`chip_resolver.py` + `_resolve_or_exit`), the star-import → named-import sweep
across five modules, and docs-only sync markers. **No behavioral changes were
introduced.** Every focus-area claim was verified:

- **Not-found contract preserved (9 sites).** The old pattern
  `get_eprom` → `convert_to_programmer` → `if not eprom_data: logger.error(...)` is
  faithfully reproduced by `_resolve_or_exit`: same log string
  (`"EPROM '{name}' not found in database."`), same return value (`None` → caller
  returns `1`). Diffed all 9 call sites against `9537256~1` — identical semantics.
- **Consistency-check integer verdict preserved.** The `dev consistency-check` site
  at `main.py:908` returns `eprom_operator.consistency_check_eprom(...)` directly
  (3-way int 0/1/2) without the bool→int wrapper used by the other op sites. The
  refactor preserved this exactly — comment even calls it out explicitly.
- **`not data` guard in `resolve_chip` is correct.** `convert_to_programmer` returns
  `{}` only when its input is falsy; for any real chip record it returns a non-empty
  dict (verified by runtime probe). The `if full else None` guard plus `if not data`
  cover both miss paths (missing record, empty conversion) without false-positives.
- **Named-import completeness verified.** Every constant used in each of the five
  refactored modules (`serial_comm`, `eprom_operations`, `database`, `firmware`,
  `hardware`, `main`) is present in the explicit import list. No runtime `NameError`
  risk. Star-import sweep is complete — `grep -rn "import \*" firestarter/` returns
  empty.
- **No injection surface.** The chip name string flows exclusively to in-memory dict
  lookups (`get_eprom_config` iterates `self.proms`). No filesystem path construction
  from user-supplied chip names.
- **`db` injection default is safe.** Production path passes `db_instance` (the
  singleton-equivalent already constructed in `main()`) via `_resolve_or_exit`; the
  `db is None → EpromDatabase()` fallback in `resolve_chip` is only exercised in
  scenarios where no db was passed. Tests always inject `EpromDatabase(skip_local_override=True)`.
- **Acceptance gates green.** Full 186-test suite passes (29 snapshots, 2 documented
  xfails only); `ruff check firestarter/` clean; mypy reports 41 errors (under the
  44-error watermark, same relative position as post-Phase-38 baseline of 39).

The two findings below are Info-level only; neither blocks shipping.

## Info

### IN-01: `resolve_chip` import in `main.py` is only transitively exercised — slightly misleading as a top-level import

**File:** `firestarter_app/firestarter/main.py:22`
**Issue:** `resolve_chip` is imported at module scope but never called directly from
`main()`; it is called only from `_resolve_or_exit` (line 530). The import is
necessary — Python resolves names at call time from the enclosing module's namespace,
so the `except ChipNotFoundError` at line 531 requires `ChipNotFoundError` to be
imported, and `resolve_chip` must be importable to call. However, a future editor
auditing "what does main.py use directly?" may flag `resolve_chip` as apparently
unused and attempt to remove it, which would produce a `NameError` at runtime. Ruff
does not flag it today because it is referenced in code; this is a readability note
only.
**Fix (optional):** A one-line comment co-locating the import with its sole use site:
```python
from firestarter.chip_resolver import resolve_chip  # used by _resolve_or_exit
```
Or move `_resolve_or_exit` above the import section (not idiomatic) — the comment
approach is minimal.

### IN-02: No test exercises the `db=None` production default in `resolve_chip`

**File:** `firestarter_app/tests/test_chip_resolver.py`
**Issue:** All four tests inject `EpromDatabase(skip_local_override=True)`. The
`db is None → EpromDatabase()` branch in `chip_resolver.py:30-31` is therefore never
exercised by the suite. In practice this branch is trivially correct (it constructs
the same class with default args), and the production path in `main.py` never
exercises it either (all 9 op sites pass `db_instance` explicitly). The risk is
strictly theoretical — a future refactor of `EpromDatabase.__init__` that changes
the default behavior could silently break the no-arg construction without a failing
test. Low real-world risk for a one-liner guard.
**Fix (optional, defer to Phase 41+ test expansion):** A smoke test:
```python
def test_resolve_chip_default_db_constructs_without_error():
    """resolve_chip(name, db=None) constructs EpromDatabase() without raising."""
    # Uses the packaged DB; honors ~/.firestarter if present (intentional).
    result = resolve_chip("W27C512")
    assert isinstance(result, dict)
```
This pins that `EpromDatabase()` (no args) still works when `db` is not injected.

---

_Reviewed: 2026-05-27_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_

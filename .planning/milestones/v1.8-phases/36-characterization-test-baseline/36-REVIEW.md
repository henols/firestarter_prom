---
phase: 36-characterization-test-baseline
reviewed: 2026-05-27T09:27:45Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - firestarter_app/firestarter/database.py
  - firestarter_app/pyproject.toml
  - firestarter_app/tests/test_bug_characterization.py
  - firestarter_app/tests/test_characterization.py
  - firestarter_app/tests/test_eprom_database.py
  - firestarter_app/tests/test_revision_constants_parity.py
  - firestarter_app/tests/test_serial_characterization.py
findings:
  critical: 0
  warning: 3
  info: 4
  total: 7
status: issues_found
---

# Phase 36: Code Review Report

**Reviewed:** 2026-05-27T09:27:45Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Phase 36 lands one production-code change (`database.py`: removal of the
`EpromDatabase` singleton + a new `skip_local_override` constructor seam) and
six test files (five new characterization suites + the parity gate extension).

I reviewed the production de-singleton change adversarially against all its
in-repo consumers, and reviewed the test files for correctness, robustness,
and determinism — explicitly NOT flagging the deliberate "tests assert buggy
behavior" design (BUG-1/BUG-2 xfail, the `info`-command crash snapshot).

I confirmed the suites behave as designed: running them yields 30 passed + 2
XFAIL (the two pinned latent bugs) for the non-subprocess files, and 35
passed / 29 snapshots for `test_characterization.py`. The `PlainArgs`
TypeError that BUG-1 relies on was independently reproduced; the de-singleton
diff was verified against the base commit (`6b2687d`).

The production change itself is **correct** — but it silently alters a
cross-module contract (shared mutable state) that four call sites previously
relied on, and that latent behavioral shift is not characterized by any test
in this phase. That, plus two determinism gaps in the test suite, are the
substantive findings. No Critical issues.

## Warnings

### WR-01: De-singleton silently drops shared-state semantics relied on by 4 call sites; no test pins the behavioral change

**File:** `firestarter_app/firestarter/database.py:157-196`

**Issue:** The old `EpromDatabase` was a process-wide singleton with a
one-time `_initialized` guard, so `main.py:39/48/589`, `ic_layout.py:297`, and
`eprom_info.py:285` all shared one instance that read `~/.firestarter` exactly
once. After this change each `EpromDatabase()` call builds a fresh instance and
re-runs `_initialize_database_core()` — re-reading `chip_database.json`,
`pinouts.json`, and the user override files on every call.

Two real behavioral shifts result, neither characterized by this phase's tests:

1. **State no longer shared.** If any consumer mutated `db.proms` /
   `db.pin_maps` on the (formerly shared) instance and expected another consumer
   to observe it, that coupling is now broken. `test_two_instances_are_independent`
   (`test_eprom_database.py:235`) actually *asserts* the new non-shared behavior
   — confirming the contract change is intentional — but nothing verifies the
   four production call sites tolerate it.
2. **Repeated file I/O + re-merge.** Each construction re-reads disk and
   re-runs `_merge_databases`, which performs an in-place `db[key].update(...)`
   and `db[key].append(...)` (lines 212-218). On the singleton this ran once;
   now it runs per call. Out of v1 perf scope, but the *correctness* concern is
   that `_merge_databases` mutates the dict returned by `_read_config_file`
   each time — verify no consumer caches a reference across constructions.

This is a contract change the diff makes invisibly (the only signal is a
docstring edit). It is in scope because removing shared state is exactly the
class of cross-module mutation-consistency defect a reviewer must surface.

**Fix:** Confirm (and ideally add a characterization test for) each of the four
call sites — they appear to construct, query, and discard locally, which is
safe. If any path relied on cross-call shared mutation, restore an explicit
shared instance there. At minimum, add a one-line note to the phase summary
that the singleton→fresh-instance change is a deliberate semantic break, so
v1.9 reviewers do not mistake it for a regression.

### WR-02: `normalize_output()` path scrubber misses `/opt`, `/usr`, `/root`, `/var`, and Windows paths — snapshot determinism guarantee is narrower than documented

**File:** `firestarter_app/tests/test_characterization.py:84`

**Issue:** The docstring (lines 73-85) claims snapshots are "identical on CI
... and bench ... across version bumps and different development environments."
The path regex only matches four prefixes:
```python
r'(?:/home|/workspaces|/tmp|/Users)(?:/[^\s",\')]+)+'
```
I verified that `/opt/...`, `/root/...`, `/usr/...`, `/var/...`, and Windows
`C:\...` paths pass through unscrubbed. This directly affects
`test_info_known_chip` (lines 224-236), which pins a real crash traceback on
stderr containing the absolute path of the installed `firestarter` entry point.
The committed `.ambr` shows `File "<PATH>", line 8` because it was generated in
a `/home`-or-`/workspaces` tree — but a `pipx`/`/opt/venv`/`/root/.local` or
Windows install would leak an environment-specific path and break the snapshot,
falsely reading as a behavioral regression rather than an environment artifact.

**Fix:** Broaden the prefix alternation and add a Windows branch, e.g.:
```python
s = re.sub(
    r'(?:/home|/workspaces|/tmp|/Users|/opt|/usr|/root|/var|/Library)(?:/[^\s",\')]+)+',
    "<PATH>", s,
)
s = re.sub(r'[A-Za-z]:\\(?:[^\s",\')]+\\?)+', "<PATH>", s)  # Windows
```
Or, more robustly, scrub on the `File "..."` traceback pattern rather than an
allowlist of root prefixes.

### WR-03: `test_no_programmer_found_read/erase` use bare `EpromDatabase()`, violating this phase's own "MANDATORY skip_local_override" rule and reintroducing bench/CI divergence

**File:** `firestarter_app/tests/test_characterization.py:353,372`

**Issue:** `test_eprom_database.py:18-23` states as MANDATORY: "every
data-asserting test constructs `EpromDatabase(skip_local_override=True)`. Bare
`EpromDatabase()` in tests that assert specific chip data is forbidden — it
would merge `~/.firestarter/database.json` if present, causing CI/bench
divergence (RESEARCH Pitfall 4)." Yet in the same phase, both
`test_no_programmer_found_read` and `test_no_programmer_found_erase` call:
```python
db = EpromDatabase()
eprom_data = db.get_eprom("W27C512")
assert eprom_data is not None
```
This runs the merge path and then asserts that `W27C512` resolves. On the
operator's bench machines (per project memory, the operator regularly runs on
hardware), a `~/.firestarter/database.json` that renames, removes, or shadows
`W27C512` would flip `eprom_data` to `None` and fail the assertion — the exact
Pitfall-4 divergence the rule exists to prevent. It passes here only because
this container has no `~/.firestarter` directory. The whole point of the
`skip_local_override` seam introduced in this phase is to close this gap; these
two tests bypass it.

**Fix:** Use the seam consistently:
```python
db = EpromDatabase(skip_local_override=True)
eprom_data = db.get_eprom("W27C512")
```
The override has no bearing on the "no programmer found" path being exercised,
so the deterministic packaged DB is strictly preferable.

## Info

### IN-01: Dead-code idiom `None` as a no-op statement in exception handlers

**File:** `firestarter_app/firestarter/database.py:365,370`

**Issue:** Both `except (ValueError, TypeError):` blocks in `_map_data` contain
a bare `None` expression statement (followed by a commented-out
`logger.warning`). `None` on its own line is evaluated and discarded — it is
dead code that reads as a mistake (likely a leftover from deleting a `pass` or
the warning). Pre-existing (not changed by this phase) but sits in the one
production file under review.

**Fix:** Replace the bare `None` with `pass`, or restore/remove the commented
warning:
```python
except (ValueError, TypeError):
    pass
```

### IN-02: `import re` inside `get_eprom_config` (function-local import)

**File:** `firestarter_app/firestarter/database.py:463`

**Issue:** `get_eprom_config` does `import re` at function scope on every call.
Pre-existing and not in this phase's diff, but flagged since the file is under
review: `re` is a stdlib module with no circular-import risk here, so the
function-local import only obscures the dependency. Move it to the module-level
imports at the top of the file.

**Fix:** Add `import re` to the top-of-file imports (line 27-30 block) and
remove the local one.

### IN-03: Test relies on `ConfigManager()` per-path singleton cache across tests

**File:** `firestarter_app/tests/test_bug_characterization.py:104`, `firestarter_app/tests/test_characterization.py:352,371`

**Issue:** `ConfigManager` is itself a per-config-path singleton
(`config.py:65 _instances = {}`). These tests construct `ConfigManager()` with
the default path, so they share one cached instance across the whole test
session. Today they only read config, so there is no leakage — but if a future
test mutates config state through this shared instance, ordering-dependent
flakiness becomes possible. Worth a fixture-level reset or a note. Not a defect
in current behavior.

**Fix:** Consider a `conftest` fixture that clears
`ConfigManager._instances` between tests, or document that tests must treat the
shared `ConfigManager` as read-only.

### IN-04: BUG-1 xfail rests on TypeError-via-`__contains__`, but its assertion message describes only the truthiness semantics

**File:** `firestarter_app/tests/test_bug_characterization.py:49-74`

**Issue:** The test is correctly designed and passes as XFAIL (verified: bug
present → `build_arg_flags(PlainArgs())` raises `TypeError: argument of type
'PlainArgs' is not iterable`, caught by `xfail`). The subtlety: the test
*fails today by raising TypeError before reaching the assert*, yet the
docstring and the trailing `assert (flags & FLAG_FORCE) == 0` frame the
characterized defect as a force-*truthiness*-vs-*existence* issue. When the
Phase 41 fix lands (`getattr(args, "force", False)`), the function will no
longer raise and the assert becomes the live check — fine. But a reader could
misread the current XFAIL as "force truthiness is wrong" when it is actually
"the `in` operator explodes on non-Namespace objects." A one-line comment
clarifying that today's XFAIL is the TypeError (not the assertion) would
prevent a future maintainer from "fixing" the wrong line.

**Fix:** Add to the test body, before the call:
```python
# Today (bug present) this raises TypeError at the `"force" in args` line —
# xfail captures the raise. Post-Phase-41 it returns and the assert is the live check.
```

---

_Reviewed: 2026-05-27T09:27:45Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

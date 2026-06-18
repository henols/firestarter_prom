---
phase: 62-dispatch-baseline-capture-check-dispatch-update
reviewed: 2026-06-10T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - firestarter_app/tools/check_dispatch.py
  - firestarter_app/tests/test_decoder.py
  - firestarter_app/tools/baseline/dispatch_baseline.json
findings:
  critical: 0
  warning: 4
  info: 4
  total: 8
status: issues_found
---

# Phase 62: Code Review Report

**Reviewed:** 2026-06-10
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Reviewed the Phase 62 dispatch-gate work: the new `protocol != 0 -> "not_implemented"`
arm and `not_implemented` FAIL bucket in `tools/check_dispatch.py`, the new
`TestDispatchGate02` suite (5 tests) in `tests/test_decoder.py`, and the generated
`tools/baseline/dispatch_baseline.json` snapshot.

**Verification performed:**
- Cross-checked `dispatch()` against the live firmware dispatch chain in
  `/workspaces/firestarter/src/proms/memory.cpp::configure_memory` (lines 72-118).
- Ran `python tools/check_dispatch.py` against the live DB — PASS, exit 0, 734 chips,
  0 not-implemented.
- Ran `pytest tests/test_decoder.py::TestDispatchGate02` — 5 passed.
- Structurally validated `dispatch_baseline.json` — 734 rows, all required fields
  present, no ERROR/not_implemented rows, handler/algorithm counts consistent.

No BLOCKERs. The logic is correct for the current DB. The most significant finding
(WR-01) is a **deliberate forward-looking divergence** between the Python mirror and
the current firmware: the `protocol != 0` guard models a *future* Phase-64 firmware
change that does not exist in the checked-out firmware. This is defensible by intent
but the in-file documentation actively contradicts itself about which phase this
mirrors, and the divergence is a latent regression-gate hazard. The remaining
findings are test-quality and maintainability issues.

## Narrative Findings (AI reviewer)

## Warnings

### WR-01: `dispatch()` mirrors a firmware guard that does not exist in the current firmware; docstring is self-contradictory about which phase it tracks

**File:** `firestarter_app/tools/check_dispatch.py:80-83` (also docstring lines 1-8)
**Issue:**
The new arm
```python
if protocol != 0:
    return "not_implemented"
```
is annotated "Phase-64 mirror: ... (In firmware: protocol != 0 guard before the
mem_type chain)". I read the actual firmware at
`/workspaces/firestarter/src/proms/memory.cpp::configure_memory`
(branch `4e2c985`, the firmware tree checked out in this workspace) and there is
**no `protocol != 0` guard**. After the explicit protocol arms, the firmware falls
straight through to the `mem_type` chain (lines 104-115) and only errors via
`MSG_ERR_MEM_TYPE_UNSUPPORTED` when `mem_type` is also unrecognized.

This means `check_dispatch.py` no longer mirrors the *current* firmware — it mirrors
a *future* (Phase 64) firmware state. Concretely: a chip with a non-zero unrecognized
protocol but a known `mem_type` would dispatch to a real handler on today's firmware,
yet `check_dispatch.py` now classifies it as `not_implemented` and FAILs. The two
behaviours have diverged.

Compounding this, the module docstring (lines 3-8) still says the script "Mirrors the
post-Phase-12 dispatch order" while the new arm says "Phase-64 mirror". A reader cannot
tell from the file which firmware revision is authoritative.

This is tolerable *only* because every chip in the current DB carries a known protocol
(verified: `check_dispatch.py` exits 0, 0 not-implemented). But the script's stated
purpose is "every chip ... reaches a real firmware dispatch path" — and right now, for
the firmware that actually ships on this branch, a `not_implemented` verdict would be a
**false failure**, not a real one.

**Fix:** Make the temporal contract explicit and self-consistent. Either:
1. Gate the arm behind a clearly-named flag/comment that states it is ahead of
   firmware until Phase 64 lands, and update the module docstring to match; or
2. Add a one-line assertion/comment pointing at the exact firmware commit/line this
   guard will mirror once Phase 64 ships, so a future reader can verify the mirror.
```python
# Phase-64 FORWARD guard: firmware does NOT yet implement this arm
# (memory.cpp::configure_memory has no `protocol != 0` check as of fw 4e2c985).
# Lands in Phase 64; until then this is intentionally STRICTER than firmware.
if protocol != 0:
    return "not_implemented"
```
Also update the docstring header (lines 3-8) to stop claiming "post-Phase-12 dispatch
order" as the sole reference.

### WR-02: `not_implemented` FAIL message claims a `KNOWN_PROTOCOLS` set that does not exist in the file

**File:** `firestarter_app/tools/check_dispatch.py:168-172`
**Issue:**
```python
print(
    f"FAIL: {len(not_implemented)} chips route to not_implemented "
    f"(protocol != 0, not in KNOWN_PROTOCOLS):"
)
```
There is no `KNOWN_PROTOCOLS` symbol anywhere in the file. The set of recognized
protocols is implicit in the `if` chain of `dispatch()` (0x05–0x39). An operator who
hits this failure and greps the codebase for `KNOWN_PROTOCOLS` finds nothing, which
makes the failure harder to diagnose. The message references a contract artifact that
was never created.
**Fix:** Either name the message after a real artifact (e.g. "not in the explicit
`dispatch()` protocol arms") or define an actual `KNOWN_PROTOCOLS` frozenset and use it
both in `dispatch()` and the message so the two cannot drift:
```python
KNOWN_PROTOCOLS = frozenset({0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E,
                             0x10, 0x27, 0x28, 0x29, 0x35, 0x39})
```

### WR-03: GATE-02 tests duplicate `sys.path` mutation 5×; permanent global side effect, fragile import, copy-paste drift risk

**File:** `firestarter_app/tests/test_decoder.py:695-743`
**Issue:** All five `TestDispatchGate02` tests repeat the identical 4-line block:
```python
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from check_dispatch import dispatch
```
Problems:
1. **Permanent global mutation:** each test prepends `tools/` to `sys.path` and never
   removes it. After this suite runs, `tools/` stays on `sys.path` for the rest of the
   pytest session, which can shadow other modules named like files under `tools/`
   (e.g. `build_db`, `audit_coverage_matrix`) in unrelated tests — a cross-test
   pollution hazard.
2. **Five-way copy-paste:** the same boilerplate in five places will drift. Any change
   to the import path must be made in five spots.
3. **`from check_dispatch import dispatch` executes the module top-level** — that is
   safe today (the only top-level work is constant definitions; `main()` is guarded by
   `if __name__ == "__main__"`), but it couples the tests to that invariant silently.

**Fix:** Hoist the path setup to a single module-level fixture or a `conftest.py`
`sys.path` entry, and import `dispatch` once at module top. A fixture that restores
`sys.path` on teardown removes the global side effect:
```python
@pytest.fixture(scope="module")
def dispatch_fn():
    import sys, os
    tools = os.path.join(os.path.dirname(__file__), "..", "tools")
    sys.path.insert(0, tools)
    try:
        from check_dispatch import dispatch
        yield dispatch
    finally:
        sys.path.remove(tools)
```
Then each test takes `dispatch_fn` as a parameter.

### WR-04: `dispatch_baseline.json` is a captured snapshot with no automated comparison guard — it can silently rot

**File:** `firestarter_app/tools/baseline/dispatch_baseline.json` (whole file)
**Issue:** I searched the repo (`tests/`, `tools/`, `.github/workflows/`,
`pyproject.toml`, `Makefile`) — nothing reads `dispatch_baseline.json`. It is a
write-only artifact: generated, committed, and never compared against. Its stated
purpose (meta line 5) is to capture the mapping "before Phase 64 fail-closed guard
lands", i.e. it is the *evidence* a regression gate would diff against — but no gate
diffs against it. As the DB or `dispatch()` evolves, this file becomes stale with no
signal that it has diverged from reality, and a future reader may trust it as
authoritative when it is not. A baseline with no consumer provides no protection.
**Fix:** Either (a) add a test that regenerates the dispatch mapping from the live DB
and asserts it equals this baseline (the obvious "GATE" this file implies), or
(b) if the snapshot is purely a one-time historical record for Phase 64 review, label
it as such in `meta.description` and move it out of `tools/` (which implies tooling
consumes it) into a planning/evidence location.

## Info

### IN-01: Hardcoded generation date in baseline `meta.generated`

**File:** `firestarter_app/tools/baseline/dispatch_baseline.json:3`
**Issue:** `"generated": "2026-06-10"` is a hand-or-tool-stamped literal date. If this
file is ever regenerated by a script, a stale date is misleading; if it is hand-edited,
the date will not reflect the actual capture. Minor, but worth noting for an artifact
whose entire value is being an accurate point-in-time snapshot.
**Fix:** Generate this field programmatically at capture time, or drop it in favor of
git commit provenance.

### IN-02: `dispatch()` docstring under-describes the new contract

**File:** `firestarter_app/tools/check_dispatch.py:67`
**Issue:** The docstring still reads only "Mirror firmware D2 dispatch order in
memory.cpp::configure_memory." It no longer mentions the two distinct failure verdicts
the function now returns (`"not_implemented"` for non-zero unknown protocols vs
`"ERROR"` for protocol==0 unknown mem_type) — exactly the distinction `TestDispatchGate02`
exists to pin (test_decoder.py:681-692). The function's most important new behaviour is
undocumented at the function level.
**Fix:** Document the two failure verdicts and when each is returned.

### IN-03: GATE-02 test docstrings describe mem_type semantics inconsistently

**File:** `firestarter_app/tests/test_decoder.py:695-713`
**Issue:** `test_dispatch_0x35_routes_configure_flash4` passes `dispatch(0x35, None)`
and the docstring says "explicit arm, not mem_type fallback". This is correct and the
test *would* catch a regression (since `mem_type=None` makes the fallback dict return
`ERROR`), but the reasoning is implicit. A reader has to reconstruct that `None` was
chosen specifically to defeat the fallback path. The intent ("we pass mem_type=None so
that a fall-through to the dict would FAIL, proving the explicit arm fired") is not
stated.
**Fix:** Add one sentence to the docstring making the `mem_type=None` choice's purpose
explicit, so the test's discriminating power is self-evident.

### IN-04: `0x39` arm is dead against the current DB (documented, but worth flagging for the gate's "every chip" framing)

**File:** `firestarter_app/tools/check_dispatch.py:74` and `firestarter/database.py:61`
**Issue:** `database.py:61` documents `0x39 ... (no DB chips; future-proofed)` and the
baseline confirms zero `0x39` (and zero `0x35`) chips in the 734-chip DB. The `0x39`
branch in `dispatch()` and its two GATE-02 tests therefore exercise a protocol that no
real chip uses. This is acceptable future-proofing and the tests are legitimately
guarding the *intent*, but it means the live `check_dispatch.py` run never actually
covers these arms — only the unit tests do. Noting so the coverage picture is honest.
**Fix:** None required; optionally add a comment in `dispatch()` noting 0x35/0x39 have
no DB chips today so the unit tests are the sole live coverage.

---

_Reviewed: 2026-06-10_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

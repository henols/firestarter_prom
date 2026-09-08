---
phase: 180-read-step-sampling-conditional-on-phase-176
reviewed: 2026-09-08T15:55:24Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - firestarter_app/tests/test_chip_test.py
  - firestarter_app/tests/test_readback_inventory.py
findings:
  critical: 0
  warning: 2
  info: 2
  total: 4
status: issues_found
---

# Phase 180: Code Review Report

**Reviewed:** 2026-09-08T15:55:24Z
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Reviewed the Phase 180 additions to `firestarter_app/tests/test_chip_test.py` (two new
behavioural tests, `f0eb002`/`07c6dab`) and `firestarter_app/tests/test_readback_inventory.py`
(two new structural AST pins plus their anti-vacuity legs, `3ca6195`, formatting fix `93a1672`),
using the submodule's own range `ffb0060..HEAD`. Both files are test-only; no product source was
touched by this phase.

The two behavioural tests in `test_chip_test.py` are sound: `test_read_step_last_run_failure_yields_bad`
(`[True, False]`, runs=2 → BAD) and `test_read_step_first_run_failure_with_passing_last_run_yields_ok`
(`[False, True]`, runs=2 → OK) exercise the real `run_plan` → `_dispatch_read` path (confirmed by
reading `_dispatch_read` at `firestarter/chip_test.py:2767-2810`, which dispatches with
`runs=runs` directly from `run_plan`'s op-routing `if step.op == OP_READ` arm). Together the two
legs discriminate "verdict = last full read's result" from every plausible alternative fold
(first-only, AND-all, OR-any) — verified by hand-tracing all four policies against both legs.
Neither test is vacuous and I confirmed both pass (`pytest -k "read_step_last_run_failure or
read_step_first_run_failure"`).

The two new structural pins in `test_readback_inventory.py` are real AST-based gates (verified by
reading the actual `_dispatch_read` and `read_eprom`/`_operation_context`/`_setup_operation`
source they inspect, and by hand-checking anchor-string uniqueness with `grep`), and both come
with a genuine anti-vacuity leg that plants the literal named counter-example and asserts the pin
reddens — not a decorative `pytest.raises` around an unrelated statement. All 10 tests in the file
pass. However, both pins are narrower than their own framing implies (see WR-01/WR-02 below): each
inspects one specific code shape rather than the full invariant its docstring claims to close, and
for the "one connect per read" pin there is no runtime backstop anywhere in this diff, so a
plausible bypass mutation would go completely undetected.

No hardcoded secrets, dangerous functions, or empty catch blocks were found. No comments (`#`)
were added by this phase in either file — only docstrings, consistent with the project's
zero-comments-in-source rule (docstrings are explicitly permitted).

## Warnings

### WR-01: "One connect per read" structural pin only checks the `with` header, not the rest of `read_eprom`'s body

**File:** `firestarter_app/tests/test_readback_inventory.py:243-336`
**Issue:** `test_one_read_eprom_call_costs_exactly_one_connect` and its anti-vacuity leg
(`test_a_planted_second_operation_context_in_read_eprom_reddens_the_pin`) pin the "one call = one
connect" premise entirely through `_read_eprom_connect_shape`'s `context_count`, which counts only
`_operation_context(...)` items inside `read_eprom`'s `with` header (lines 256-264). It does not
scan the rest of `read_eprom`'s body for any other route to a second connect — e.g. a stray direct
`self._setup_operation(...)` or `SerialCommunicator.find_and_connect(...)` call added anywhere
else inside the function, outside a `with` statement entirely. Such a mutation would still leave
`context_count == 1` and the pin would stay green while the "one connect" premise the closure
document (`180-PRUNE-08-CLOSURE.md`) rests on is silently false. Unlike the verdict-source pin
(WR-02), there is no companion runtime/behavioural test anywhere in this diff that would catch
this — the pin's own docstring concedes "it does not prove at runtime that exactly one serial open
occurred," but that ceiling statement undersells the gap: it isn't just that runtime isn't proven,
it's that a second **static** connect call outside the `with` header is invisible to this check
too.
**Fix:** Extend `_read_eprom_connect_shape` to also count any `ast.Call` anywhere in
`read_eprom`'s body (not just within the `with` header) whose `func.attr` is `_setup_operation` or
`find_and_connect`, and assert that total equals `context_count` (i.e., every connect-shaped call
inside `read_eprom` is reached only via the one `_operation_context` item already counted):
```python
stray_connects = sum(
    1
    for n in ast.walk(read_eprom)
    if isinstance(n, ast.Call)
    and isinstance(n.func, ast.Attribute)
    and n.func.attr in ("_setup_operation", "find_and_connect")
)
assert stray_connects == 0
```

### WR-02: Verdict-source pin inspects the `verdict=` expression's syntax, not `last_ok`'s data flow

**File:** `firestarter_app/tests/test_readback_inventory.py:138-212`
**Issue:** `test_read_verdict_expression_reads_only_the_last_full_read_result` asserts the
`ast.Name` set reachable from `_dispatch_read`'s `verdict=` keyword value is exactly
`{VERDICT_BAD, VERDICT_OK, last_ok}`. This correctly catches the anti-vacuity leg's counter-example
(a divergence term inlined directly into the ternary), but it does not trace whether `last_ok`
itself was reassigned earlier in the function body before reaching the `StepResult(...)` call — for
example, inserting `last_ok = last_ok and not divergence` immediately before the `return`
statement would leave the `verdict=` line's `ast.Name` set completely unchanged (`last_ok`,
`VERDICT_OK`, `VERDICT_BAD`), and this structural pin would stay green while the verdict now
silently depends on divergence. (This particular escape happens to still be caught by the existing
behavioural test `test_read_step_disagreement_is_divergence_metric_not_marginal` in
`test_chip_test.py`, so it is not a fully unguarded gap today — but the pin's own docstring markets
itself as "the structural half that catches a future change a behavioural test alone cannot," which
overstates what a syntax-only check on one keyword expression can prove.)
**Fix:** Either narrow the docstring's claim to "the literal verdict expression's shape" (drop the
"catches what behavioural tests can't" framing), or strengthen the pin to walk the whole function
body and assert `last_ok` is the target of exactly one `ast.Assign`/`ast.NamedExpr` (the one inside
the `for` loop), so a later reassignment is caught structurally too.

## Info

### IN-01: Stale line citation in a new docstring

**File:** `firestarter_app/tests/test_readback_inventory.py:170`
**Issue:** The docstring for `test_read_verdict_expression_reads_only_the_last_full_read_result`
cites `` `tests/test_chip_test.py`'s `test_read_step_last_run_failure_yields_bad` (:2141 sibling
range) `` — but that function is defined at `test_chip_test.py:2177`, a 36-line drift from the
citation. Non-executable (doesn't affect the gate), but factually wrong at the moment it was
written, which suggests the citation wasn't checked against the actual sibling file before commit.
**Fix:** Update the citation to the correct line (`:2177`), or drop the specific line number and
cite the function name only, which can't drift.

### IN-02: Duplicated read-side-effect closures across the two new behavioural tests

**File:** `firestarter_app/tests/test_chip_test.py:2177-2240`
**Issue:** `test_read_step_last_run_failure_yields_bad` and
`test_read_step_first_run_failure_with_passing_last_run_yields_ok` each define an essentially
identical local `_read_side_effect` / `call_returns` / `call_count` closure, differing only in the
two-element list's order (`[True, False]` vs `[False, True]`). The file already has a precedent
for factoring a `read_eprom` side-effect builder out into a shared helper
(`_writes_bytes_to_output_file`, line 1428), but that helper always returns `True` and can't
express an alternating pass/fail sequence, so it wasn't reusable here as-is.
**Fix:** Factor a small `_alternating_read_side_effect(*call_returns: bool)` helper (mirroring
`_writes_bytes_to_output_file`'s shape) that both new tests call with their own ordered tuple,
removing the duplicated boilerplate.

---

_Reviewed: 2026-09-08T15:55:24Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

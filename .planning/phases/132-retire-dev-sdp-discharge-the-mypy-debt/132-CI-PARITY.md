# Phase 132 — CI-Parity Readings

Two readings live in this file: a `## 1. Before` section (this plan, 132-01, taken before any
deletion or mypy fix lands) and a `## 2. After` section (appended by a later plan, after the
deletion + discharge, per the ROADMAP's cross-cutting rule that the recipe runs before AND after).

## 1. Before (pre-deletion, pre-discharge)

**Preconditions verified, each a hard stop on failure — none tripped:**

(a) `git -C /workspaces/firestarter_app branch --show-current` printed exactly
`gsd/v1.30-sdp-surface-retirement`.
(b) `git -C /workspaces branch --show-current` printed exactly
`gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`.
(c) `git -C /workspaces/firestarter_app status --porcelain` was non-empty, but every line matches
the plan's own `<pre_existing_tree_state>` dirt list (` M .gitignore`, `?? .coverage`,
`?? .planning/config.json`, `?? SECURITY.md`, `?? write_test_port.sh`) — pre-existing, not
introduced by this plan, and not touched here. No untracked-but-unaccounted change was present.
(d) `BOARD-ATTACHED: none` — read from `tools/ci_parity.sh`'s own stamp below, not probed
separately.

**App-repo HEAD at the time of the run:**
`8caf77f458ba1bd1eeff47f9747838dc4183e2ca` (short: `8caf77f`), on branch
`gsd/v1.30-sdp-surface-retirement`. This matches the plan's `<measured_ground_truth>` HEAD exactly.

**Run: `bash tools/ci_parity.sh` from `/workspaces/firestarter_app`, captured verbatim.**

```
---------------------------------
Leg 1: FIRESTARTER_FW_ROOT=<empty dir> python3 -m pytest tests/ -q
Proves: the suite passes with the firmware sibling absent -- the standalone-CI condition.
---------------------------------
[... suite output, various SKIPPED lines for firmware-checkout-absent cases ...]
Leg 1 exit code: 0

---------------------------------
Leg 2: python3 -m pytest tests/ -q
Proves: the suite passes with the firmware sibling present (this devcontainer's own layout).
---------------------------------
[... 100% pass, 30 snapshots passed ...]
Leg 2 exit code: 0

---------------------------------
Leg 3: ruff lint + ruff format --check, at ci.yml's exact path set
Proves: ruff is CI-scoped correctly today; the failure mode this leg guards against is running ruff locally at a different scope.
---------------------------------
All checks passed!
116 files already formatted
Leg 3 exit code: 0 (ruff check: 0, ruff format --check: 0)

---------------------------------
Leg 4: python3 tools/check_mypy_watermark.py
Proves: the hardened watermark gate (GATE-01/02/03/04) reaches a legible terminal state. A local exit 2 here (ambient numpy PEP-695 stub truncating mypy) is the gate working correctly, not a script defect -- see this script's header and 131-CI-PARITY.md.
---------------------------------
ERROR: mypy exited 2, which is neither the clean-run (0) nor errors-found (1) exit code. Treating as a tool/config failure, not a clean tree.
/usr/local/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater  [syntax]
Found 1 error in 1 file (errors prevented further checking)
Leg 4 exit code: 2

=================================
CI-PARITY SUMMARY
=================================
Leg 1 (pytest, empty sibling root):  exit 0
Leg 2 (pytest, sibling present):     exit 0
Leg 3 (ruff check + format --check): exit 0
Leg 4 (mypy watermark gate):         exit 2
BOARD-ATTACHED: none
Python: Python 3.12.13
CI-PARITY: FAIL (legs:4)
```

**Which legs passed and which did not:** Legs 1, 2, and 3 passed (exit 0 each). Leg 4 exited 2.

**Leg 4's exit 2 is the expected, correct pre-change shape — not a defect.** Quoting
`tools/ci_parity.sh`'s own leg-4 banner: *"A local exit 2 here (ambient numpy PEP-695 stub
truncating mypy) is the gate working correctly, not a script defect."* The devcontainer's ambient
`numpy` install ships a `.pyi` stub using PEP-695 `type` statement syntax that this environment's
mypy target (`python_version = "3.10"`) cannot parse, so mypy aborts with returncode 2 before
producing any per-source-file count. Phase 131's hardened
`classify_mypy_result()` correctly refuses to report a count for this truncated run (guard 1:
"returncode not in (0, 1)") rather than silently reporting a plausible-looking number. This is
exactly why this plan's Task 2 builds a separate numpy-free CI-replica venv — not to "fix" this
leg, and this leg is deliberately left un-weakened: no `|| true`, no guard removal, no forced
green aggregate exit. The aggregate `CI-PARITY: FAIL (legs:4)` is therefore the correct,
expected pre-change reading, and matches the identical shape Phase 131 recorded in its own
`131-CI-PARITY.md`.

**The one gap this recipe does not cover, and that this phase must close by other means.**
`.github/workflows/ci.yml`'s `ci` job runs pytest as:

```
pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70
```

whereas `tools/ci_parity.sh` legs 1 and 2 run `pytest tests/ -q` with **no coverage flags at
all** — this is stated explicitly in the script's own header under "WHAT THIS DELIBERATELY DOES
NOT MIRROR": *"pytest's `--cov=firestarter --cov-report=term-missing --cov-fail-under=70`
coverage gate (legs 1/2 below run the same suite WITHOUT the coverage flags -- proving
suite-pass, not coverage-floor)."* The `--cov-fail-under=70` floor is a real `ci` job step that
neither leg 1 nor leg 2 would catch a drop below. This matters directly to this phase: Phase 132
deletes `dev sdp` — approximately 126 lines of well-covered production code inside
`cli_handlers.py`, plus roughly 550 lines of its test module (`tests/test_dev_sdp_cmd.py` →
`tests/test_sdp_honesty.py`, most content pruned per D-04) — and nothing in `ci_parity.sh`'s
existing two pytest legs would notice if that deletion pushed the suite below the 70% floor.
Task 2's `tools/ci_replica_venv.sh` closes this gap with its own leg 5, running pytest with CI's
exact coverage invocation.

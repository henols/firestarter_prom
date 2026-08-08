# 138-04-HOST-BASELINE: PREP-03 host-suite half — firestarter_app under CI parity

**Owner requirement:** PREP-03, host half only (the firmware half — golden trace, flash/RAM, native
suites — is Plans 03/05/06's scope, not this plan's). **Status:** measured, 0 requirement ticked by
this plan (`may_tick_requirements: []`).

**Measured:** 2026-08-08, this session, in `/workspaces/firestarter_app`, live and read-only against
the app's own git state. Nothing below is copied from `138-RESEARCH.md` — every command was re-run
fresh in this session, and any divergence from research's recorded figures is stated explicitly,
with both values kept on record, and is **not** reconciled.

---

## 1. Branch switch — provenance

| Field | Value | Command that produced it |
|---|---|---|
| Pre-switch branch | `fix/dev-test-blank-check-after-erase` | `git symbolic-ref --short HEAD` (before switch) |
| Pre-switch HEAD SHA | `7fe8dea9143a6ac4da3d656d3e4d5d538e14a175` | `git rev-parse HEAD` (before switch) |
| Pre-switch tracked-file modifications | 0 (8 untracked files present, expected and carried over) | `git status --porcelain \| grep -v '^??' \| wc -l` → `0` |
| Post-switch branch | `gsd/v1.31-27c-programming-algorithm-fidelity` | `git symbolic-ref --short HEAD` (after switch) |
| Post-switch HEAD SHA | `4d18b645ab18a2d2465f0f623062e9249eb24132` | `git rev-parse HEAD` (after switch) |
| Base SHA recorded in `138-BRANCH-BASES.md` §4 (Plan 01) | `4d18b645ab18a2d2465f0f623062e9249eb24132` | quoted from `138-BRANCH-BASES.md` §4, Section 4 table, `firestarter_app` row |
| HEAD == recorded base? | **Yes — exact match**, both the full 40-char SHA and the 7-char short form | `git rev-parse HEAD` compared byte-for-byte against the quoted value above |

The switch used `git checkout gsd/v1.31-27c-programming-algorithm-fidelity` (branch already existed,
created — but not checked out — by Plan 01). No branch was created by this plan; no branch was pushed;
no commit was made in `firestarter_app` by this task.

## 2. Interpreter and imported package — provenance

| Field | Value | Command that produced it |
|---|---|---|
| CI-parity interpreter path | `.venv/ci-replica/bin/python` (symlink → `python3.11`) | `ls -la .venv/ci-replica/bin/python` |
| CI-parity interpreter version | **`Python 3.11.15`** | `.venv/ci-replica/bin/python --version` |
| Ambient interpreter version (recorded for contrast, **NOT** used for any measurement below) | `Python 3.12.13` | `python3 --version` |
| Imported package file | `/workspaces/firestarter_app/firestarter/__init__.py` | `.venv/ci-replica/bin/python -c "import firestarter; print(firestarter.__file__); print(firestarter.__version__)"` |
| Imported package version | `3.0.0b20` | same command as above |

The devcontainer's ambient Python (`3.12.13`) is not used for any figure in this document — the string
`3.12` appears in this file only in this sentence and the table row above, both explaining why it was
**not** substituted for the CI-parity interpreter. Every measurement below runs `.venv/ci-replica/bin/python`
explicitly, from inside `/workspaces/firestarter_app` (never a sibling directory — the package is
installed editable, and two tests resolve a path ending in the literal directory name
`firestarter_app`; see §4).

## 3. Full-suite measurement — provenance

**Stated condition of this measurement:** no serial devices are attached to this machine
(`/dev/ttyACM*` and `/dev/ttyUSB*` are both absent, confirmed immediately before this run). This
matters because `test_no_programmer_found_*`-style tests go spuriously RED when a live board is
present (a real `/dev/ttyACM*` device beats the `comports=[]` monkeypatch) — that failure mode does
not apply to this run.

| Field | Value | Command that produced it |
|---|---|---|
| Command (exact, run from `/workspaces/firestarter_app`) | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` | — |
| Timeout budget used | 600000 ms (>= the plan's required 540000 ms floor) | Bash tool invocation parameter |
| Wall-clock start | `2026-08-08T23:14:06Z` | `date -u` immediately before the run |
| Wall-clock end | `2026-08-08T23:17:07Z` | `date -u` immediately after the run |
| Exit code | `0` | shell `$?` |
| Collected | **1539** (= passed + skipped + failed, since pytest's `-q` summary omits a zero-count category) | tail of the same run |
| Passed | **1539** | tail of the same run: `1539 passed, 1 warning in 180.89s (0:03:00)` |
| Skipped | **0** | same tail line — no `skipped` clause present, and `grep -ic skip` on the full captured output returns `0` |
| Failed | **0** | same tail line — no `failed` clause present |
| Warnings | 1 (`test_click_group_gate_hook.py` — `Click` `MultiCommand` deprecation, pre-existing, unrelated to this measurement) | same run |
| Snapshot tests | `30 snapshots passed.` | same run's `snapshot report summary` block |
| Duration (pytest-reported) | `180.89s (0:03:00)` | same tail line |
| Duration (wall-clock, this session) | `181s` (`$SECONDS`) | shell timer wrapping the same invocation |

`-o addopts=""` is present in the command above and no `-qq` appears anywhere — `pyproject.toml` sets
`addopts = "-ra -q"`, and a second `-q` on the command line would reach `-qq`, which suppresses the
count line that is the entire measurement (Pitfall 9). The verbatim captured tail is reproduced in
full in §5 below, unedited.

## 4. Directory-name-dependent tests — in-place proof

| Field | Value | Command that produced it |
|---|---|---|
| Node id 1 | `tests/test_gen_validation_header.py::test_validate_spec_called_before_emission` | — |
| Node id 2 | `tests/test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing` | — |
| Command | `.venv/ci-replica/bin/python -m pytest tests/test_gen_validation_header.py::test_validate_spec_called_before_emission tests/test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing -o addopts="" -q` | — |
| Result | **`2 passed in 0.09s`** | same command, run from `/workspaces/firestarter_app` |

Both tests resolve a path ending in the literal directory name `firestarter_app` (per
`138-RESEARCH.md`'s Pitfall 8 / Runtime State Inventory) and were measured here **in place**, in
`/workspaces/firestarter_app` itself — not a sibling or renamed checkout. Their passing is the positive
evidence that this whole measurement was taken in the correct location.

## 5. Post-measurement worktree state — provenance

| Field | Value | Command that produced it |
|---|---|---|
| Tracked-file changes introduced by this task | 0 | `git status --porcelain \| grep -v '^??' \| wc -l` → `0` (re-run after both pytest invocations) |
| Untracked files (unchanged set of 8, all pre-existing) | `.coverage`, `.planning/config.json`, `SECURITY.md`, `datasheets/M27C1001.pdf`, `datasheets/M27C512.pdf`, `datasheets/W27C512.pdf`, `datasheets/W27E257.pdf`, `write_test_port.sh` | `git status --porcelain` |
| HEAD after both pytest runs | `4d18b64 Apply automatic changes` — unchanged | `git log --oneline -1` |
| Branch after both pytest runs | `gsd/v1.31-27c-programming-algorithm-fidelity` — left checked out, as later phases expect | `git symbolic-ref --short HEAD` |

**No commit was made inside `firestarter_app` by this task.** The app worktree is left on the v1.31
branch, as later Wave 3 plans (Phase 143) expect it.

---

*(Task 1 raw pass. Task 2 adds the verbatim output block, the divergence check against
`138-RESEARCH.md`, the three constraints restated as measured facts, "what this number is — and is
not," and "not established by this measurement.")*

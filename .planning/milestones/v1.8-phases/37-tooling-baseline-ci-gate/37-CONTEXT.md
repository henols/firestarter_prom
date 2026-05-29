# Phase 37: Tooling Baseline + CI Gate - Context

**Gathered:** 2026-05-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Stand up an **enforced quality gate** for `firestarter_app`: configure `ruff` (lint) +
`ruff format` + `mypy` in `pyproject.toml`, bring the existing tree to a **green baseline**
*without doing the real cleanup* (that is Phases 38–42), record the initial mypy error
**watermark**, and add a CI step + a `pre-commit` config that **fail the build on new
violations**, with a coverage gate.

This phase is **pure tooling/infrastructure — zero runtime behavior change.** The only
source edits permitted are mechanical, test-covered transforms (whole-tree `ruff format`
+ import-sort autofix) and `# noqa` suppressions for legacy lint findings. No hand-fixing
of logic, no module extraction, no typing work beyond config — those are deferred to the
later phases. Phase 36's characterization safety net (162 tests + 29 syrupy snapshots) is
what makes the mechanical reformat safe.

Requirements: TOOL-01, TOOL-02, TOOL-03 (full text in `.planning/REQUIREMENTS.md`).
Standing contract: GATE-1.8 (a–e) — see REQUIREMENTS.md lines 10–18.
</domain>

<decisions>
## Implementation Decisions

All four open gray areas were resolved by operator decision (2026-05-27): "what do you
recommend?" → **Accept all four** recommendations. The rest of Phase 37 is locked upstream
by the ROADMAP/REQUIREMENTS/PROJECT (see "Locked Upstream" below — do not re-litigate).

### Baseline → Green Strategy (TOOL-01)
- **D-01:** Reach a green tree in **three separate, individually-reviewable commits**, in order:
  1. **`ruff format`** the whole tree (mandatory so `ruff format --check` exits 0) — isolated commit.
  2. **`ruff check --fix --select I`** — import-sorting only. Mechanical and fully covered by Phase 36's tests/snapshots. (Do **not** auto-fix UP or other rewrites here — those are "fixes" that belong to the per-module cleanup in 38–42.)
  3. **`ruff check --add-noqa`** for the residual E/F/UP findings — these become the legacy watermark; the `# noqa` lines are removed module-by-module as Phases 38–42 touch each file.
- **D-02:** Preserve git blame across the whole-tree reformat: create **`.git-blame-ignore-revs`** containing the format commit SHA, and document `git config blame.ignoreRevsFile .git-blame-ignore-revs` in the README/contributor docs (GitHub honors the file automatically). Rationale: flat layout was chosen *specifically* to keep blame intact (PROJECT.md scope decision) — a reformat would otherwise wreck it.
- **D-03:** No hand-fixing in Phase 37 (honors the locked "not hand-fixing everything"). Star-import findings (`F403`/`F405` from `import *`) are `# noqa`'d now and resolved in Phase 39 (DATA-03).

### Coverage Gate Floor & Ratchet (TOOL-03)
- **D-04:** **Measure current coverage first** (`pytest --cov`; add `pytest-cov` to the `test` extra). Then set the gate:
  - If measured **≥ 60%** → set the gate at **60%** per spec.
  - If measured **< 60%** → set the gate at the **measured floor rounded down to a 5% step**, document the deviation in the commit + CONTEXT trail, and record a ratchet plan to reach 60%.
- **D-05:** Ratchet is **manual** — each later phase that adds tests bumps the threshold number in `pyproject.toml`/CI. Phase 42 (ERR SC#3) already mandates raising it to ≥ 70%. Manual bumps keep the change reviewable per phase. Rationale: a hard 60% day-one would fail the build and force test-writing *beyond* Phase 36's net — scope creep into 37. Measured-floor + explicit ratchet matches TOOL-03's "start ~60%, ratcheted up per phase".

### CI Workflow Triggers & Shape (TOOL-03)
- **D-06:** **Triggers — run on all pull requests** (drop the `branches: [main]` filter on the `pull_request` trigger) plus keep `push` on `main`. Keep the existing `paths-ignore` (md/docs/gitignore/etc.). Rationale: the entire v1.8 milestone runs on branch `v1.8-app-cleanup`; a `main`-only gate would sit **dormant** for the whole milestone — the gate must guard the refactor as it happens.
- **D-07:** **Job shape — fold** the new steps into the existing single `ci` job (order: `ruff check` → `ruff format --check` → `mypy` → `pytest --cov`). The repo is small and the job already does `pip install`; a separate parallel lint job is YAML overhead for marginal speed.
- **D-08:** **Python — keep the run on single Python 3.11** (matches current CI). Set ruff `target-version = "py39"` and mypy `python_version = "3.9"` to honor the `requires-python = ">=3.9"` floor (prevents `UP` from rewriting to 3.10+ syntax). A full 3.9–3.12 test matrix is **deferred** (see Deferred Ideas).

### Linter Rule Set & mypy Watermark (TOOL-01, TOOL-02)
- **D-09:** **ruff rules stay at the locked E/F/I/UP** for Phase 37 — do **not** add B/bugbear, SIM, C4, etc. now. Fixes are deferred to 38–42, so a broader set just produces more `# noqa` litter today with no payoff yet. Broadening the rule set → a Phase 42 quality-sweep enhancement (see Deferred Ideas). Document the selected categories with rationale (no `select = ["ALL"]`).
- **D-10:** **mypy watermark = strict-islands + count-script.** Global config stays lenient (`disallow_untyped_defs = false`); `[[tool.mypy.overrides]]` makes the **Phase 36 test modules** strict (they are clean). The "no new errors vs watermark" gate is enforced by a **small count-comparison script** in CI: run mypy → count errors → compare to the integer watermark recorded as a comment in `pyproject.toml` → fail if greater. Dependency-free; each typed module later lowers the watermark and joins the strict list. (`mypy-baseline` — pins exact errors rather than a count — is the more-precise alternative if count drift ever bites; noted as a deferred fallback.)
- **D-11:** Add **`types-pyserial`** to the typing/test deps (TOOL-02).

### Locked Upstream (carried forward — do NOT re-ask or re-litigate)
- Formatter = **ruff-format**, NOT black (PROJECT.md evolution note + TOOL-01 supersede the earlier "ruff+black+mypy" wording).
- ruff rule floor = **E, F, I; UP added**; `select = ["ALL"]` forbidden (ROADMAP Phase 37 SC#1).
- mypy = `disallow_untyped_defs = false` globally / **gradual adoption**; strict overrides **start with the Phase 36 test modules** (ROADMAP SC#2).
- CI lives in the **existing `ci.yml`**; `pre-commit` config committed with hook order **ruff-check → ruff-format → mypy** (ROADMAP SC#3).
- Host-only milestone; flat module layout; GATE-1.8 (a–e) applies (the wire protocol / CLI surface / constants contract / read-path ring-fence / suite-green clauses).

### Claude's Discretion
- Exact name + location of the mypy watermark count-comparison script (`scripts/` vs `tools/`); its shell-vs-python implementation.
- `pre-commit` hook pinning: `repo: local` vs pinned `astral-sh/ruff-pre-commit` + `pre-commit/mirrors-mypy` mirrors, and the exact pinned versions (pick current).
- Whether coverage config lives in `[tool.coverage.*]` + `--cov` flags in CI, or via pytest `addopts` — planner's call.
- The precise 5%-step rounding for the coverage floor (decided after the measurement in D-04).
- Whether the import-sort autofix (D-01 step 2) is `--select I` alone or includes other *mechanically-safe, test-covered* fixes — keep it minimal and reversible.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & locked milestone decisions
- `.planning/ROADMAP.md` — Phase 37 detail (lines 75–84): goal + 3 success criteria. Also the v1.8 section + GATE-1.8 standing gate (lines 23–34).
- `.planning/REQUIREMENTS.md` — TOOL-01 / TOOL-02 / TOOL-03 (lines 34–36); GATE-1.8 (a–e) (lines 10–18); Out-of-Scope table (lines 89–104).
- `.planning/PROJECT.md` — "Current Milestone: v1.8" + "Scope decisions (locked 2026-05-27)" (lines 32–41): ruff+ruff-format+mypy, flat layout to preserve git blame, host-only, tests-first.
- `.planning/phases/36-characterization-test-baseline/36-CONTEXT.md` — prior-phase decisions; D-47 note that Phase 36 acceptance was "ruff/mypy run **without config errors**, violations recorded as a baseline watermark NOT fixed — that's Phase 37"; the Phase 36 test modules that seed the mypy strict list.

### Files this phase configures / extends (firestarter_app sub-repo)
- `firestarter_app/pyproject.toml` — add `[tool.ruff]`, `[tool.ruff.format]`, `[tool.mypy]` (+ `[[tool.mypy.overrides]]`), coverage config + the mypy watermark comment; `requires-python = ">=3.9"`; `[project.optional-dependencies].test` (add `pytest-cov`, `types-pyserial`); `[tool.pytest.ini_options]`.
- `firestarter_app/.github/workflows/ci.yml` — the existing "Host CI" workflow to extend. Currently: `main`-only triggers, single Python 3.11, one `ci` job (catalog-check → codegen-drift → `pip install -e .[dev]` → `pytest tests/ -v`).
- `firestarter_app/.pre-commit-config.yaml` — **does not exist yet**; create it (hook order ruff-check → ruff-format → mypy).
- `firestarter_app/.git-blame-ignore-revs` — **does not exist yet**; create it (D-02).
- `firestarter_app/firestarter/` — the package to lint/format/type (`main.py`, `serial_comm.py`, `database.py`, `eprom_operations.py`, `constants.py`, `firmware.py`, `hardware.py`, `avr_tool.py`, `ic_layout.py`, `config.py`, `messages.py`, `utils.py`, `eprom_info.py`, `logging_utils.py`).
- `firestarter_app/tests/` — Phase 36 strict-list seed modules: `test_characterization.py`, `test_serial_characterization.py`, `test_bug_characterization.py`, `test_eprom_database.py`, `test_revision_constants_parity.py`, `test_decoder.py`.

### Do-not-touch (other CI workflows)
- `firestarter_app/.github/workflows/{beta-release.yml,publish.yml,release.yml}` — tag/PyPI-only pipelines; out of scope for the lint/type/coverage gate (TOOL-03 targets `ci.yml`).

### App architecture (context)
- `firestarter_app/CLAUDE.md` — data flow + the `constants.py` ↔ `firestarter/include/firestarter.h` sync contract.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Phase 36 safety net** — 162 passing tests + 2 xfail(strict) + 29 syrupy snapshots covering the CLI surface, serial frame-parse path, and EPROM DB layer. This is what makes the whole-tree `ruff format` + import-sort autofix safe to apply mechanically (any behavioral regression is caught immediately).
- `pyproject.toml` already has `[project.optional-dependencies].test = [pytest>=8.0, syrupy>=5.0]` and `[tool.pytest.ini_options]` (`testpaths=["tests"]`, `addopts="-ra -q"`) — extend rather than create.
- The Phase 36 test modules are already clean Python (written this milestone) — natural seed for the mypy strict-overrides list (D-10).

### Established Patterns
- `requires-python = ">=3.9"`, classifiers list 3.9–3.12 → ruff `target-version = "py39"` / mypy `python_version = "3.9"` keep `UP` rewrites conservative (D-08).
- CI is a single `ci` job that installs the package then runs `pytest`; the catalog-validity + codegen-drift steps run *before* install. New gate steps fold in *after* `pip install -e .[dev]` (D-07).
- Existing CI uses `pip install -e .[dev]` (dev = pytest only) — the gate run needs `.[test]` (or a dedicated install of ruff/mypy/pytest-cov) so the new tools are present.

### Integration Points
- `firestarter_app/pyproject.toml` — all tool config blocks + the mypy watermark comment.
- `firestarter_app/.github/workflows/ci.yml` — trigger change (D-06) + folded gate steps (D-07).
- New: `firestarter_app/.pre-commit-config.yaml`, `firestarter_app/.git-blame-ignore-revs`, and a small mypy-watermark count-comparison script.
</code_context>

<specifics>
## Specific Ideas

- Operator's preference, stated by delegating ("what do you recommend?" → "Accept all four"): keep Phase 37 **lean and mechanical** — set up the gate at an honest current baseline, defer all real fixes to the phases designed for them (38–42). Minimize churn, preserve git blame, don't let the coverage number force premature test-writing.
</specifics>

<deferred>
## Deferred Ideas

- **Full 3.9–3.12 CI test matrix** — nice-to-have; out of Phase 37's tooling scope. Candidate for a later CI-hardening pass.
- **Broader ruff rule set (B/bugbear, SIM, C4, …)** — defer to **Phase 42** (Error Handling + Quality Sweep), once code is actually being cleaned and a `# noqa` from these rules would be fixed rather than parked.
- **`mypy-baseline` tool** — more-precise alternative to the D-10 count-script (pins exact errors, catches "fixed one / added one"). Revisit only if count-drift becomes a real maintenance problem.

### Reviewed Todos (not folded)
Three pending todos fuzzy-matched "Phase 37" on generic keyword noise (score 0.2–0.4); all are hardware/protocol items, out of this tooling phase's domain — reviewed and **not folded**:
- `avrdude-mcu-detection-fallback.md` — blank-chip / wrong-firmware recovery (hardware; v1.9-ish).
- `serial-cobs-resync-data-path.md` — COBS framing on the serial data path (protocol; not v1.8 host-cleanup scope, and wire protocol is frozen by GATE-1.8a).
- `w27c512-eeprom-misclassification.md` — chip-DB classification fix (database content; not a tooling concern).
</deferred>

---

*Phase: 37-Tooling Baseline + CI Gate*
*Context gathered: 2026-05-27*

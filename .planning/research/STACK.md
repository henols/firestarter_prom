# Technology Stack: firestarter_app v1.8 Structural Cleanup

**Project:** firestarter_app — Python host CLI refactor
**Milestone:** v1.8 (Host CLI Structural Cleanup)
**Researched:** 2026-05-27
**Scope:** Tooling/library choices for the refactor only. No new end-user features.
**Confidence:** HIGH (all versions confirmed against PyPI as of 2026-05-27)

---

## Constraints Inherited from the Existing Codebase

Before any recommendation: these are locked inputs and must not be changed by the refactor.

| Constraint | Value | Why locked |
|------------|-------|------------|
| Python floor | `>=3.9` (pyproject.toml) | Existing requirement; changing is out-of-scope |
| Wire protocol | JSON-over-serial at 250 000 baud | Byte-identical gate GATE-1.8 |
| Command surface | All existing subcommands, flags, defaults, exit codes preserved | GATE-1.8 |
| Existing runtime deps | pyserial>=3.5, requests>=2.20, tqdm>=4.60, argcomplete>=3.6.2, rich>=14.0, packaging>=21.0 | Some will be adjusted (argcomplete drops with argparse); see below |
| Flat layout | All modules remain sibling files in `firestarter/`; no subpackages | Operator decision locked 2026-05-27 |
| Firmware sub-repo | Untouched | Host-only scope |

---

## Recommended Tooling Stack

### CLI Framework — Click 8.4.1

**Replace:** `argparse` + `argcomplete`
**Version:** `8.4.1` (released 2026-05-22; current stable)
**Source:** https://pypi.org/project/click/

**Why Click over alternatives:**
- Decorator-based definition collocates command declaration with handler — the single most important change for decomposing the 418-line `main()` dispatcher.
- Native subcommand groups (`@click.group` / `@group.command`) map directly onto the existing argparse subparsers structure; migration is mechanical subcommand-by-subcommand.
- `click.testing.CliRunner` ships in-box — no extra dep for CLI unit tests. Invokes the command in-process, captures stdout/stderr, and exposes `result.exit_code` and `result.output` without spawning a subprocess.
- Click 8.4 fixed flag-option default precedence that was broken in 8.3.x, making the `--pre` / `--stable` / `--firmware-version` mutex group (currently argparse `add_mutually_exclusive_group`) behave correctly with explicit defaults.
- Actively maintained by Pallets; 38%+ of Python CLI projects use it.

**Why NOT Typer:** Typer adds Pydantic-style type coercion and FastAPI-influenced patterns — heavier than needed. It also requires Python >=3.7 but its ecosystem maturity for production tooling is lower than Click's. The firestarter_app team has zero Pydantic/FastAPI familiarity context; Click requires no new mental model for someone who has read argparse.

**Migration approach for argparse → Click:**
1. Keep `main.py` compiling against both during transition by migrating one subcommand at a time behind a feature flag (or by migrating the entire tree in a single phase — the latter is preferred here since characterization tests are written first).
2. Subcommands: `parser.add_subparsers(dest="command")` + `if args.command == "read":` becomes `@cli.command("read")` decorated functions. The 14-branch `if/elif` dispatcher disappears entirely.
3. Flags: `add_argument("--verbose", action="store_true")` → `@click.option("--verbose", is_flag=True)`. Boolean flags with `store_true` translate 1:1.
4. Positional arguments: `add_argument("input_file")` → `@click.argument("input_file")`.
5. Mutually exclusive groups (used for `--pre`/`--stable`/`--firmware-version`): Click has no native mutex group. Implement with a manual callback guard: `if (pre and stable) or (pre and firmware_version):  raise click.UsageError(...)`. This matches the existing argparse behavior and is idiomatic Click.
6. Exit codes: argparse relied on implicit `sys.exit()`. Click's default `standalone_mode=True` calls `sys.exit(0)` on success and `sys.exit(2)` on usage error — identical to argparse defaults. `ClickException.exit_code` defaults to 1; `UsageError` exits with 2. Map existing manual `sys.exit(N)` calls to `raise click.ClickException(msg)` (exit 1) or `raise SystemExit(N)` for non-standard codes. Do not disable `standalone_mode` in the entry point — it is what makes the script behave as a CLI.
7. `argcomplete` can be dropped from runtime deps once argparse is gone; Click has its own shell completion via `click.shell_completion` (opt-in, no extra install).
8. `RawTextHelpFormatter` usage (multi-line help strings): Click preserves newlines in help text natively; no equivalent needed.

**Characterization tests to write before migration:** Use `CliRunner.invoke(current_argparse_main, [...])` via the thin wrapper pattern — write golden assertions on `result.exit_code`, key phrases in `result.output`, and `result.exception is None` for every subcommand path. Lock these before touching the CLI layer.

**Runtime dep change:** Remove `argcomplete>=3.6.2`. Click shell completion is optional and off-by-default; add only if the operator needs it later.

---

### Linter + Formatter — ruff 0.15.14 + black 26.5.1

#### ruff 0.15.14

**Version:** `0.15.14` (released 2026-05-21; current stable)
**Source:** https://pypi.org/project/ruff/

**Why ruff:** Replaces flake8 + isort + pyupgrade in a single tool written in Rust — 10–100× faster than any pure-Python alternative. The rule set covers every category needed for this cleanup: style (E), logic errors (F), import sort (I), modernization (UP), common bugs (B). Single config section in `pyproject.toml`.

**Why NOT flake8 alone:** ruff subsumes it. Adding flake8 would be a redundant dep with slower CI.

**Baseline adoption strategy for a messy codebase:**

Step 1 — generate the baseline noqa file. Run:
```
ruff check firestarter/ --add-noqa
```
This inserts `# noqa: RXXX` on every currently-failing line. Commit. CI is now green. No existing behavior changes.

Step 2 — configure with a conservative initial rule set. Enforce cleanly from day 1:
```toml
[tool.ruff]
target-version = "py39"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I"]    # pycodestyle + pyflakes + isort
ignore = [
    "E501",   # line-too-long — black handles this; don't double-enforce
]

[tool.ruff.lint.per-file-ignores]
"firestarter/__init__.py" = ["F401"]   # re-exports are intentional
"tests/*" = ["ANN"]                    # no annotations required in tests
```

Step 3 — add rule categories phase by phase as modules get cleaned up:
- Phase 36 (tooling setup): `["E", "F", "I"]`
- Phase 37 (constants + serial): add `"UP"` (pyupgrade — modernize syntax; all fixes are safe)
- Phase 39 (typing pass): add `"ANN"` selectively on newly-typed modules only via `per-file-ignores` inversion
- `"B"` (bugbear): add when ready — it catches real bugs but some rules are noisy on existing code

Do NOT use `select = ["ALL"]`. It silently enables new rules on every ruff upgrade, turning routine dependency updates into CI failures.

#### black 26.5.1

**Version:** `26.5.1` (released 2026-05-18; current stable)
**Source:** https://pypi.org/project/black/

**Why black alongside ruff-format:** ruff's formatter (ruff format) is black-compatible but not bit-for-bit identical in every edge case. For a codebase already using rich terminal output and targeting long-term maintainability, running `black` as the canonical formatter avoids subtle drift. The combination is: `ruff check --fix` (linting + safe auto-fixes) then `black` (formatting). If the team prefers a single tool, `ruff format` is an acceptable substitute — but do not run both formatters as they will fight over formatting.

**Recommendation:** Use `ruff format` as the formatter (it is the ruff project's intended path and is now the more actively developed path), and drop `black` as a direct dependency. Configure `ruff format` to match black's defaults (line-length 88, magic trailing comma). This reduces the dev dependency count by one and avoids two formatters producing different output on edge cases.

**pyproject.toml format config:**
```toml
[tool.ruff.format]
quote-style = "double"
indent-style = "space"
magic-trailing-comma = true
```

---

### Static Type Checker — mypy 2.1.0

**Version:** `2.1.0` (released 2026-05-11; current stable)
**Source:** https://pypi.org/project/mypy/

**Why mypy:** The project has no type annotations today and `disallow_untyped_defs` would red-flag every function. mypy's gradual typing support — ignore unannotated functions by default, apply per-module overrides as code gets typed — is exactly the adoption path this refactor needs. pyright is a valid alternative but mypy's per-module override table is more explicit and well-understood.

**Baseline configuration for a messy legacy codebase:**

```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = false        # too noisy on unannotated code
ignore_missing_imports = true  # stops complaining about third-party stubs not installed
disallow_untyped_defs = false  # unannotated functions are ok during migration

# Tighten per-module as modules get typed:
[[tool.mypy.overrides]]
module = "firestarter.constants"
disallow_untyped_defs = true
warn_return_any = true

[[tool.mypy.overrides]]
module = "firestarter.main"
disallow_untyped_defs = true
```

**Adoption strategy:** Start with the global config above (CI green from day 1). As each module is refactored, add it to the `[[tool.mypy.overrides]]` list with `disallow_untyped_defs = true`. Never add modules back to the permissive list once they're in the strict overrides — this is a one-way ratchet.

**Inversion endgame:** Once ~80% of modules are typed, flip the global config to `disallow_untyped_defs = true` and list only the remaining legacy holdouts in overrides with `ignore_errors = true`. This is the professional-grade mypy pattern used in large codebases.

**Required stub package:** `types-pyserial 3.5.0.20260519` — provides type stubs for `pyserial==3.5.*`, tested against mypy 2.1.0 and pyright 1.1.409. Add to dev dependencies. Without it, mypy emits `import-not-found` for every `serial.*` import.

```toml
[project.optional-dependencies]
dev = [
    "pytest>=9.0",
    "pytest-mock>=3.15",
    "pytest-cov>=7.0",
    "ruff>=0.15",
    "mypy>=2.1",
    "types-pyserial>=3.5.0.20260519",
    "syrupy>=5.2",
    "pre-commit>=4.6",
]
```

---

### Testing — pytest 9.0.3 + pytest-mock 3.15.1 + pytest-cov 7.1.0 + syrupy 5.2.0

#### pytest 9.0.3

**Version:** `9.0.3` (released 2026-04-07; current stable)
**Source:** https://pypi.org/project/pytest/

The existing project already uses pytest (tests/ dir, `pytest>=7.0` in dev deps). Upgrade the floor to `>=9.0` for the new test suite — 9.x brings improved assertion rewriting and better fixture lifecycle messages.

#### pytest-mock 3.15.1 (PREFERRED over unittest.mock directly)

**Version:** `3.15.1` (released 2025-09-16; current stable)
**Source:** https://pypi.org/project/pytest-mock/

**Why pytest-mock over raw unittest.mock:**
- `mocker` fixture automatically reverts all patches after each test via pytest's fixture lifecycle. No `@patch` decorator nesting, no `with patch(...)` context managers cluttering test bodies.
- `mocker.patch("firestarter.serial_comm.serial.Serial")` — one line, auto-cleaned.
- For pyserial mocking specifically: patch `serial.Serial` at the import site in the module under test, not at `serial.Serial` itself. Pattern: `mocker.patch("firestarter.serial_comm.serial.Serial", autospec=True)`.
- `autospec=True` is mandatory for serial mocking — it validates that test doubles honour the real `serial.Serial` interface, catching mock drift when pyserial updates.

unittest.mock is still usable inside test functions (it ships with Python); pytest-mock is just the fixture wrapper. The two coexist.

#### pytest-cov 7.1.0

**Version:** `7.1.0` (released 2026-03-21; current stable)
**Source:** https://pypi.org/project/pytest-cov/

**Coverage gate configuration:**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q --cov=firestarter --cov-report=term-missing --cov-fail-under=60"
```

**Strategy:** Set the initial gate low (60%) to allow CI to go green immediately after characterization tests are written. Raise the threshold by 10 points at each phase boundary as more modules get unit tests. Do not set the gate to 100% — `serial_comm.py`'s hardware-I/O paths cannot be fully unit-tested and the coverage number would force fake coverage via `# pragma: no cover` everywhere.

Characterization tests are the primary coverage driver in early phases. They exercise the existing behavior end-to-end (via `CliRunner`) and produce high line coverage without being brittle.

#### syrupy 5.2.0 — Snapshot/Golden Tests

**Version:** `5.2.0` (released 2026-05-16; current stable)
**Source:** https://pypi.org/project/syrupy/

**Why syrupy for characterization tests:** The primary risk in this refactor is behavioral regression — commands outputting different text, different exit codes, different JSON commands sent over serial. Syrupy lets you:
1. Run the CLI via `CliRunner.invoke(cli, ["read", "-e", "W27C512", ...])` with serial mocked.
2. Assert `assert result.output == snapshot` — on first run, syrupy writes the golden file.
3. On subsequent runs, any output drift fails the test with a diff.
4. Update intentional changes with `pytest --snapshot-update`.

This is the right tool for the characterization-first strategy: lock behavior before restructuring, then restructure freely.

**Usage pattern:**
```python
from click.testing import CliRunner
from firestarter.main import cli

def test_read_command_output(snapshot, mocker):
    mocker.patch("firestarter.serial_comm.serial.Serial", autospec=True)
    runner = CliRunner()
    result = runner.invoke(cli, ["read", "-e", "W27C512", "--port", "/dev/null"])
    assert result.exit_code == snapshot
    assert result.output == snapshot
```

**Alternative:** `pytest-golden` is a lighter alternative. Skip it — syrupy has better tooling (audit, diff output, `--snapshot-update`) and is actively maintained with zero dependencies.

**Do NOT use `pytest-reserial`** for this project. It records/replays real serial traffic, which requires live hardware. The v1.8 refactor is host-only and hardware-gated tests are explicitly excluded.

---

### pre-commit 4.6.0

**Version:** `4.6.0` (released 2026-04-21; current stable)
**Source:** https://pypi.org/project/pre-commit/

**`.pre-commit-config.yaml` (canonical configuration):**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.14
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v2.1.0
    hooks:
      - id: mypy
        additional_dependencies: ["types-pyserial>=3.5.0.20260519"]
```

**Order matters:** `ruff-check --fix` runs before `ruff-format` so that auto-fixed lint changes get formatted. mypy runs last (slow; catches type errors after style is clean).

**CI gate:** Run `pre-commit run --all-files` in CI as a required check. This catches any commit that bypassed the hook locally.

---

## Dependency Changes to pyproject.toml

### Remove from runtime deps
- `argcomplete>=3.6.2` — only needed because argparse has no native completion. Click provides `click.shell_completion` as an opt-in. Drop from runtime; the feature can be re-exposed later if the operator wants shell completion.

### No changes to other runtime deps
- `pyserial>=3.5` — keep; not touched by the refactor
- `requests>=2.20` — keep; used by `firmware.py` for GitHub Releases API
- `tqdm>=4.60` — keep; used for progress bars in EPROM operations
- `rich>=14.0` — keep; used for table output in `info` / `list` commands
- `packaging>=21.0` — keep; used for PEP 440 version comparison in firmware install

### Add to dev deps
```toml
[project.optional-dependencies]
dev = [
    "pytest>=9.0",
    "pytest-mock>=3.15",
    "pytest-cov>=7.0",
    "ruff>=0.15",
    "mypy>=2.1",
    "types-pyserial>=3.5.0.20260519",
    "syrupy>=5.2",
    "pre-commit>=4.6",
]
```

---

## Alternatives Considered and Rejected

| Category | Recommended | Rejected | Why Rejected |
|----------|-------------|----------|--------------|
| CLI framework | Click 8.4.1 | Typer | Pydantic dependency, FastAPI-style mental model unfamiliar to this project; overkill for migration-in-place |
| CLI framework | Click 8.4.1 | argparse (keep) | The 418-line dispatcher is the core structural problem; argparse enforces the flat `if/elif` pattern and has no decorator model |
| Linter | ruff | flake8 + isort + pyupgrade | Three tools replaced by one; ruff is faster and the ecosystem has standardised on it |
| Formatter | ruff format | black | ruff format is the actively maintained path; running both causes formatting conflicts |
| Type checker | mypy | pyright | mypy's per-module override table is more explicit for gradual adoption; either is fine but mypy is the de facto standard for open-source Python packages |
| Snapshot testing | syrupy | pytest-golden | syrupy has better CLI tooling (`--snapshot-update`, audit, diff); actively maintained |
| Snapshot testing | syrupy | pytest-reserial | Requires live hardware; incompatible with host-only scope |
| DI framework | nothing | Any (injector, dependency-injector, etc.) | Not needed. The codebase has simple module-level singletons (`EpromDatabase`). Introducing DI adds indirection with no benefit at this scale. |
| Async rewrite | nothing | asyncio / anyio | The serial protocol is synchronous by design; the bottleneck is hardware latency, not I/O multiplexing. An async rewrite is out of scope and would break the wire protocol invariants. |
| Plugin system | nothing | click-plugins, pluggy | No extensibility requirement exists. Do not add. |
| Schema validation | nothing | pydantic, attrs | JSON command construction is straightforward dict building. Pydantic adds a heavy dep and mandates a model layer that would fight the flat-module constraint. |

---

## Explicit "Do NOT Add" List

These are real patterns that seem attractive for a cleanup refactor. Do not add them.

- **No DI framework** (injector, dependency-injector, punq, etc.) — `EpromDatabase` is a singleton; pass it as a function argument if needed. Module-level import is sufficient.
- **No async rewrite** — the serial protocol is inherently synchronous with hardware timing constraints. asyncio/anyio adds complexity without solving any real problem.
- **No plugin system** — there is no extension use-case. click-plugins and pluggy are out.
- **No Pydantic / dataclass-heavy model layer** — the chip database is already JSON; adding a validation schema would require migrating 734 chip entries. This is scope creep.
- **No new serialization layer** — the wire protocol is locked byte-identical. msgpack, protobuf, etc. are out.
- **No logging framework replacement** — the existing `logging` + `rich` combination is adequate. Do not add `structlog`, `loguru`, etc.
- **No `flake8` alongside ruff** — ruff subsumes it entirely; running both wastes CI time and can produce conflicting directives.
- **No `black` alongside `ruff format`** — pick one; running both will produce formatting conflicts on edge cases.
- **No `isort` standalone** — ruff's `I` rule set handles import sorting; `isort` is redundant.

---

## pyproject.toml Additions (consolidated view)

Add the following sections to `firestarter_app/pyproject.toml`:

```toml
[tool.ruff]
target-version = "py39"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"firestarter/__init__.py" = ["F401"]
"tests/*" = ["ANN"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
magic-trailing-comma = true

[tool.mypy]
python_version = "3.9"
warn_return_any = false
ignore_missing_imports = true
disallow_untyped_defs = false
# Add [[tool.mypy.overrides]] per module as they get typed

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q --cov=firestarter --cov-report=term-missing --cov-fail-under=60"
```

---

## Sources

- Click 8.4.1 on PyPI: https://pypi.org/project/click/ (confirmed 2026-05-27)
- Click testing docs: https://click.palletsprojects.com/en/stable/testing/
- Click exceptions docs: https://click.palletsprojects.com/en/stable/exceptions/
- Click commands docs: https://click.palletsprojects.com/en/stable/commands/
- Click changes (8.4.x): https://click.palletsprojects.com/en/stable/changes/
- ruff 0.15.14 on PyPI: https://pypi.org/project/ruff/ (confirmed 2026-05-27)
- ruff configuration docs: https://docs.astral.sh/ruff/configuration/
- ruff linter docs: https://docs.astral.sh/ruff/linter/
- ruff pre-commit hooks: https://github.com/astral-sh/ruff-pre-commit
- black 26.5.1 on PyPI: https://pypi.org/project/black/ (confirmed 2026-05-27)
- mypy 2.1.0 on PyPI: https://pypi.org/project/mypy/ (confirmed 2026-05-27)
- mypy config file docs: https://mypy.readthedocs.io/en/stable/config_file.html
- types-pyserial 3.5.0.20260519 on PyPI: https://pypi.org/project/types-pyserial/ (confirmed 2026-05-27)
- pytest 9.0.3 on PyPI: https://pypi.org/project/pytest/ (confirmed 2026-05-27)
- pytest-mock 3.15.1 on PyPI: https://pypi.org/project/pytest-mock/ (confirmed 2026-05-27)
- pytest-cov 7.1.0 on PyPI: https://pypi.org/project/pytest-cov/ (confirmed 2026-05-27)
- syrupy 5.2.0 on PyPI: https://pypi.org/project/syrupy/ (confirmed 2026-05-27)
- pre-commit 4.6.0 on PyPI: https://pypi.org/project/pre-commit/ (confirmed 2026-05-27)
- mock-serial on PyPI: https://pypi.org/project/mock-serial/
- Professional-grade mypy configuration: https://careers.wolt.com/en/blog/tech/professional-grade-mypy-configuration

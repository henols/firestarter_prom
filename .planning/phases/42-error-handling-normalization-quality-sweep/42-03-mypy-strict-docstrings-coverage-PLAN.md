---
phase: 42-error-handling-normalization-quality-sweep
plan: 03
type: execute
wave: 3
depends_on: ["02"]
files_modified:
  - firestarter_app/pyproject.toml
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/main.py
  - firestarter_app/firestarter/chip_resolver.py
  - firestarter_app/firestarter/frame_parser.py
  - firestarter_app/firestarter/codec.py
  - firestarter_app/firestarter/address_parser.py
  - firestarter_app/firestarter/exceptions.py
  - firestarter_app/firestarter/serial_comm.py
  - firestarter_app/.github/workflows/ci.yml
  - firestarter_app/tests/test_database_conversion.py
  - firestarter_app/tests/test_eprom_operations.py
  - firestarter_app/tests/test_firmware_install.py
  - firestarter_app/tests/test_config.py
  - firestarter_app/tests/test_hardware.py
autonomous: true
requirements:
  - ERR-02
  - ERR-03
must_haves:
  truths:
    - "GATE-1.8a: wire protocol byte-identical — only return-type annotations + docstrings added to source files; no behavior changes; new tests EXERCISE eprom_operations.py / hardware.py read paths but do NOT modify them per GATE-1.8d"
    - "GATE-1.8b: end-user CLI surface preserved — docstrings added to Click callbacks begin with one-liner matching existing argparse `help=` text (or are no-ops where docstring already present); the 29 syrupy snapshots stay green because Click's --help formatting derives from the FIRST line of the docstring and that line is byte-identical to the existing help= text"
    - "GATE-1.8c: constants.py + firmware header parity untouched (constants.py not in the 8-module strict-list edit set; existing parity tests stay green)"
    - "GATE-1.8d: read path ring-fence preserved — eprom_operations.py NOT added to mypy strict overrides (D-07 deferred to v1.9); the new tests in tests/test_eprom_operations.py EXERCISE the read-side state machine via make_comm/fake_serial fixtures but NEVER modify _run_state_machine or _read_and_parse_lines bodies"
    - "GATE-1.8e: full suite green + pip install -e . && firestarter --help smoke remains green; CI gate now enforces --cov-fail-under=70"
    - "D-06 honored: 8 modules in [[tool.mypy.overrides]] strict-island block — main, cli_handlers, chip_resolver, frame_parser, codec, address_parser, exceptions, serial_comm — with disallow_untyped_defs=true AND check_untyped_defs=true; mypy exits 0 on all 8"
    - "D-07 deviation honored: eprom_operations.py NOT in mypy strict overrides this phase (read-path ring-fence; deferred to v1.9 post-RCA)"
    - "D-08 honored (per BLOCKER 4 restructure): the watermark comment in pyproject.toml is read AFTER Task 2 has fixed the strict-list modules' annotations (Task 1 only adds the override block + omit entry; Task 2 actually drives mypy strict to 0 errors then reads the FULL `mypy firestarter/` count and updates the watermark to match the new floor). Single-line edit only; tools/check_mypy_watermark.py NOT modified."
    - "D-09 honored: every @cli.command() / @cli.group() / @dev.command() callback in cli_handlers.py has a 1-line docstring; module-level docstrings present on all 8 strict-list modules (scout confirmed already present); public-function docstrings added where missing"
    - "D-10 honored: naming verified snake_case (no rename work needed; documented as conformant)"
    - "D-11 honored: incremental dead-code sweep only — no proactive grep-and-delete pass; the _resolve_or_exit shim was already removed in Plan 42-02"
    - "D-13 honored: firestarter/avr_tool.py added to [tool.coverage.run] omit list (subprocess wrapper; meaningful coverage would require avrdude binary)"
    - "D-14 honored: 5 new/extended test files land — test_database_conversion.py (NEW), test_eprom_operations.py (NEW; happy-path tests only, NO BUG-2 regression test per WARNING 10 — that lives in test_bug_characterization.py), test_firmware_install.py extension (EDIT), test_config.py (NEW), test_hardware.py (NEW)"
    - "D-15 honored: --cov-fail-under flip from 50 → 70 lands in the SAME atomic commit as the test additions; CI gate at firestarter_app/.github/workflows/ci.yml:58 updated"
    - "Target coverage threshold ≥ 70% achieved empirically (CONTEXT projected 70.2%; verified by pytest --cov run before commit; if margin tight, planner adds 1-2 small test files on logging_utils.py or utils.py per D-14 fallback)"
    - "ERR-01 SC#1 grep contract closed (BLOCKER 2): `grep -rn 'except:' firestarter/` returns 0 (no bare except); `grep -rn 'except Exception' firestarter/ | grep -vE 'as e($|[^a-zA-Z_])'` returns 0 (every `except Exception` site binds `as e`)"
    - "Phase 36 syrupy snapshots (29) + Phase 41 test_cli_handlers.py exit_code assertions (~30) + Plan 42-01 BUG-2 PASSED + Plan 42-02 _resolve_or_exit removal all preserved"
    - "no-touch invariant: eprom_operations.py BODY (only ADD coverage tests; no source edits beyond Plan 42-01's BUG-2 fix), data/chip_database.json, data/pinouts.json, tests/__snapshots__/, the firmware sub-repo — none of these have source edits in this plan"
  artifacts:
    - path: "firestarter_app/pyproject.toml"
      provides: "new [[tool.mypy.overrides]] block for 8 strict-list modules + avr_tool.py omit entry under [tool.coverage.run]; watermark comment updated post-Task-2 (BLOCKER 4)"
      contains: "disallow_untyped_defs = true"
    - path: "firestarter_app/firestarter/cli_handlers.py"
      provides: "docstrings on every @cli.command() / @cli.group() / @dev.command() callback (D-09); return-type annotations on helpers where missing (mypy strict)"
      contains: '"""'
    - path: "firestarter_app/.github/workflows/ci.yml"
      provides: "pytest step with --cov-fail-under=70 (was 50)"
      contains: "--cov-fail-under=70"
    - path: "firestarter_app/tests/test_database_conversion.py"
      provides: "database.convert_to_programmer happy paths for W27C512, AT28C256, AM29F040, 6116-class"
      contains: "convert_to_programmer"
      min_lines: 40
    - path: "firestarter_app/tests/test_eprom_operations.py"
      provides: "happy-path tests for write_eprom/verify_eprom/blank_check_eprom/erase_eprom via make_comm + fake_serial; READ path EXERCISED only — NEVER modified (GATE-1.8d); NO BUG-2 regression test (lives in test_bug_characterization.py per WARNING 10)"
      contains: "from firestarter.eprom_operations import EpromOperator"
      min_lines: 80
    - path: "firestarter_app/tests/test_firmware_install.py"
      provides: "extended with _get_releases_response_json + _compare_versions PEP 440 branch coverage"
      contains: "_compare_versions"
    - path: "firestarter_app/tests/test_config.py"
      provides: "ConfigManager.get_value / set_value / persist + override file resolution"
      contains: "from firestarter.config import ConfigManager"
      min_lines: 30
    - path: "firestarter_app/tests/test_hardware.py"
      provides: "HardwareManager read-side voltage methods (read_vpp_voltage, read_vpe_voltage); voltage-engagement methods stay low-coverage (safety boundary)"
      contains: "from firestarter.hardware import HardwareManager"
      min_lines: 40
  key_links:
    - from: "firestarter_app/pyproject.toml::[[tool.mypy.overrides]]"
      to: "firestarter_app/firestarter/{main,cli_handlers,chip_resolver,frame_parser,codec,address_parser,exceptions,serial_comm}.py"
      via: "module = [...] list with disallow_untyped_defs = true"
      pattern: "disallow_untyped_defs"
    - from: "firestarter_app/.github/workflows/ci.yml"
      to: "firestarter_app/pytest"
      via: "--cov-fail-under=70"
      pattern: "cov-fail-under=70"
    - from: "firestarter_app/tests/test_eprom_operations.py + test_hardware.py"
      to: "firestarter_app/tests/conftest.py (make_comm + fake_serial fixtures)"
      via: "fixture injection per Phase 36 D-02"
      pattern: "make_comm"
---

<objective>
Wave 3 / Plan 42-03 — Raise the v1.8 quality gates as a single atomic commit per the Phase 40/41 wave-commit pattern. Three coordinated changes:

1. **Mypy strict on 8 modules (D-06; ERR-02).** Add a new `[[tool.mypy.overrides]]` block in `pyproject.toml` listing exactly the SC-literal 8 modules — `firestarter.main`, `firestarter.cli_handlers`, `firestarter.chip_resolver`, `firestarter.frame_parser`, `firestarter.codec`, `firestarter.address_parser`, `firestarter.exceptions`, `firestarter.serial_comm` — with `disallow_untyped_defs = true` + `check_untyped_defs = true`. `eprom_operations.py` is DELIBERATELY EXCLUDED per D-07 (read-path ring-fence GATE-1.8d; deferred to v1.9). Add return-type annotations where missing on public functions across those 8 modules (the strict-mode mypy run surfaces gaps). Per BLOCKER 4: the watermark comment at `pyproject.toml:115` is updated **in Task 2** (after Task 2 has driven the strict-list modules to 0 errors and the full `mypy firestarter/` count is known) — NOT in Task 1.

2. **Docstrings + naming + dead code (D-09, D-10, D-11; ERR-03 textual portion).** Add 1-line docstrings to every `@cli.command()` / `@cli.group()` / `@dev.command()` callback in `cli_handlers.py` that lacks one (scout: per-option `help=` is in place but per-handler docstrings vary). The first line of each docstring MUST begin with the same text as the existing argparse `help=` parameter so Click's `--help` formatting stays snapshot-stable (29 syrupy goldens). Add public-function docstrings to helpers in the 8 strict-list modules where missing. Naming is verified snake_case (scout: zero camelCase function defs); document conformant. Dead-code sweep is incremental — the `_resolve_or_exit` shim was already removed in Plan 42-02; no proactive grep-and-delete.

3. **Coverage raise to 70% (D-13, D-14, D-15; ERR-03 quantitative portion).** Add `firestarter/avr_tool.py` to `[tool.coverage.run] omit` per D-13 (subprocess wrapper; meaningful coverage would require the real avrdude binary). Land 5 new/extended test files per D-14: `test_database_conversion.py` (NEW), `test_eprom_operations.py` (NEW; happy-path tests only — NO BUG-2 regression test per WARNING 10, that contract lives in `test_bug_characterization.py` already), `test_firmware_install.py` extension (EDIT), `test_config.py` (NEW), `test_hardware.py` (NEW). Flip `--cov-fail-under=50` → `--cov-fail-under=70` in `.github/workflows/ci.yml:58` in the SAME atomic commit (D-15). Target projection is 70.2% per CONTEXT D-14 calculation; verify empirically before commit; if margin tight, planner adds fallback small tests on `logging_utils.py` or `utils.py` per D-14 fallback.

This wave's commit is the largest of Phase 42 (~15 files edited, including 5 test files added/extended) but still one atomic commit per the Phase 40/41 pattern (cleaner bisect; the three changes are coupled — mypy strict requires the docstrings + return types; the coverage threshold requires the tests). Per WARNING 5, intermediate `<verify>` smoke checkpoints are inserted between task groups so context-exhaustion partial recovery remains salvageable; the single atomic commit still lands at Task 7.

Purpose: Close ERR-02 + ERR-03 + the ERR-01 SC#1 literal grep contract (BLOCKER 2). v1.8 quality bar raised end-to-end; the 8 strict-list modules are mypy-clean under disallow_untyped_defs + check_untyped_defs; the coverage floor is 70%; every Click callback has a docstring; the strict-overrides block is the future-proof gate (any new typed helper added to one of the 8 modules must be type-annotated to land green).
Output: One atomic commit on the `firestarter_app/` submodule's `v1.8-app-cleanup` branch with ~10-15 files edited/added.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
@.planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md
@.planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md
@.planning/phases/40-serial-transport-restructure/40-CONTEXT.md
@.planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md
@.planning/phases/36-characterization-test-baseline/36-CONTEXT.md
@firestarter_app/CLAUDE.md
@firestarter_app/pyproject.toml
@firestarter_app/.github/workflows/ci.yml
@firestarter_app/firestarter/cli_handlers.py
@firestarter_app/firestarter/main.py
@firestarter_app/firestarter/chip_resolver.py
@firestarter_app/firestarter/frame_parser.py
@firestarter_app/firestarter/codec.py
@firestarter_app/firestarter/address_parser.py
@firestarter_app/firestarter/exceptions.py
@firestarter_app/firestarter/serial_comm.py
@firestarter_app/firestarter/database.py
@firestarter_app/firestarter/eprom_operations.py
@firestarter_app/firestarter/firmware.py
@firestarter_app/firestarter/config.py
@firestarter_app/firestarter/hardware.py
@firestarter_app/tests/conftest.py
@firestarter_app/tests/test_firmware_install.py
</context>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| pyproject.toml → mypy CI gate | New strict block enforces typing on 8 modules — defensive guard against future untyped helpers landing without review |
| CI workflow → pytest cov gate | --cov-fail-under flip 50→70 raises the bar; future PRs that drop coverage below 70% fail CI |
| test fixtures → eprom_operations.py (read path) | Tests EXERCISE the read path via make_comm/fake_serial; GATE-1.8d requires they NEVER modify _run_state_machine body (only Plan 42-01's BUG-2 except split is allowed) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-42-06 | Tampering | mypy strict block | mitigate | The 8-module strict-list explicitly EXCLUDES eprom_operations.py per D-07 — preserves GATE-1.8d read-path ring-fence; v1.9 post-RCA can add it without behavior risk |
| T-42-07 | Denial of Service | new coverage tests | mitigate | New tests use the existing make_comm/fake_serial pattern (no real serial I/O); cannot block CI; the read-path test exercises the existing state machine WITHOUT modifying it |
| T-42-08 | Information Disclosure | docstrings | accept | New docstrings document public-function behavior — no secrets surfaced; first-line text matches existing argparse help= text (already user-visible) |
| T-42-09 | Tampering | avr_tool.py omit from coverage | accept | Coverage omission applies only to the subprocess wrapper for avrdude; D-13 records the cost/value rationale; security model around avrdude invocation is governed elsewhere (subprocess.run argv construction is the integrity point; not measurable via line coverage) |

Severity: informational only. `block_on: high` not triggered.
</threat_model>

<tasks>

<task type="auto">
  <name>Task 1: Add mypy strict overrides block + avr_tool.py coverage omit (NO watermark edit — that lands in Task 2 per BLOCKER 4)</name>
  <files>firestarter_app/pyproject.toml</files>
  <read_first>
    - firestarter_app/pyproject.toml (current state — lines 110-129 cover [tool.mypy] + the existing Phase 36 test-modules [[tool.mypy.overrides]] block + the watermark comment at line 115; lines 131-137 cover [tool.coverage.run] and [tool.coverage.report])
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md (D-06 supplies the exact 8-module list verbatim; D-08 specifies the watermark comment update rule; D-13 specifies the avr_tool.py omit entry; "Claude's Discretion" note supports two separate override blocks for readability)
    - .planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md (D-08 py39 legacy typing constraints; D-10 the original watermark+script contract — the script tools/check_mypy_watermark.py is NOT modified, only the comment value)
  </read_first>
  <action>
    Two coordinated edits in `firestarter_app/pyproject.toml` (BLOCKER 4 restructure: the watermark comment edit is moved to Task 2; this task ONLY adds the override block + the omit entry):

    1. **Append a new `[[tool.mypy.overrides]]` block AFTER the existing Phase 36 test-modules block** (currently ends at line 129). Per Claude's Discretion in CONTEXT.md, use TWO separate override blocks (test-modules + new source-modules) for readability rather than merging. The new block MUST contain:
       - `module = [` followed by a list of exactly 8 fully-qualified module names in this order (matches CONTEXT D-06 + the SC#2 literal in ROADMAP.md):
         - `"firestarter.main"`
         - `"firestarter.cli_handlers"`
         - `"firestarter.chip_resolver"`
         - `"firestarter.frame_parser"`
         - `"firestarter.codec"`
         - `"firestarter.address_parser"`
         - `"firestarter.exceptions"`
         - `"firestarter.serial_comm"`
       - `disallow_untyped_defs = true` (the STRICT-mode key; not in the test block)
       - `check_untyped_defs = true` (same as test block)
       - A `# Phase 42 D-06: strict-island for the 8 modules touched in v1.8.` header comment
       - A second `# eprom_operations.py DELIBERATELY EXCLUDED per D-07 (GATE-1.8d read-path ring-fence; deferred to v1.9 post-RCA).` comment

       The block MUST NOT include `firestarter.eprom_operations`, `firestarter.database`, `firestarter.hardware`, `firestarter.firmware`, `firestarter.config`, `firestarter.eprom_info`, `firestarter.ic_layout`, `firestarter.logging_utils`, `firestarter.utils`, `firestarter.avr_tool`, or `firestarter.messages` — those are deliberate non-strict modules this phase. Adding them is an SC deviation that requires re-running CONTEXT.

    2. **Add `firestarter/avr_tool.py` to `[tool.coverage.run] omit`.** Currently line 133 reads `omit = ["firestarter/data/*"]`. Edit to:
       - `omit = ["firestarter/data/*", "firestarter/avr_tool.py"]`
       - Add a comment above or inline explaining the rationale per D-13 (subprocess wrapper for avrdude; meaningful coverage would require real avrdude binary in CI)

    **DO NOT update the mypy watermark comment in this task** — per BLOCKER 4, the watermark depends on the post-strict-overrides full-mypy count, which is only known after Task 2 has fixed type annotations across the 8 strict-list modules. The watermark update lands in Task 2.

    DO NOT:
    - Add ruff rule changes (ruff config stays at Phase 37 watermark)
    - Touch the [project.scripts] / [tool.setuptools] / [build-system] blocks
    - Change `python_version = "3.9"` (Phase 37 D-08 lock)
    - Change `disallow_untyped_defs = false` in the global [tool.mypy] (the override is per-module; global stays lenient per Phase 37 D-10)
    - Modify `tools/check_mypy_watermark.py` (D-08: only the COMMENT changes, not the script)
    - Edit the watermark comment at pyproject.toml:115 (Task 2 owns that edit per BLOCKER 4)
    - Add new dependencies or modify existing ones (test deps already cover the additions)
  </action>
  <verify>
    <automated>cd firestarter_app && grep -c "^module = \[" pyproject.toml</automated>
  </verify>
  <acceptance_criteria>
    - `cd firestarter_app && grep -cE "^module = \[" pyproject.toml` returns at least 2 (one for the existing test-modules block + one for the new source-modules block)
    - `cd firestarter_app && python -c "import tomllib; data = tomllib.loads(open('pyproject.toml').read()); overrides = data['tool']['mypy']['overrides']; src_blk = next(b for b in overrides if 'firestarter.cli_handlers' in b['module']); assert src_blk['disallow_untyped_defs'] is True; assert src_blk['check_untyped_defs'] is True; assert 'firestarter.eprom_operations' not in src_blk['module']; assert set(src_blk['module']) == {'firestarter.main', 'firestarter.cli_handlers', 'firestarter.chip_resolver', 'firestarter.frame_parser', 'firestarter.codec', 'firestarter.address_parser', 'firestarter.exceptions', 'firestarter.serial_comm'}; print('OK')"` exits 0 with OK
    - `cd firestarter_app && grep -c '"firestarter/avr_tool.py"' pyproject.toml` returns at least 1 (in the omit list)
    - `cd firestarter_app && python -c "import tomllib; data = tomllib.loads(open('pyproject.toml').read()); assert 'firestarter/avr_tool.py' in data['tool']['coverage']['run']['omit']; print('OK')"` exits 0 with OK
    - `cd firestarter_app && grep -c "Phase 42" pyproject.toml` returns at least 1 (comments anchoring the new block to the phase)
    - `cd firestarter_app && grep -c "eprom_operations.py DELIBERATELY EXCLUDED" pyproject.toml` returns 1 (the D-07 deviation rationale comment)
    - `cd firestarter_app && python -c "import tomllib; data = tomllib.loads(open('pyproject.toml').read()); print('OK')"` exits 0 (toml parses cleanly; no syntax errors)
    - `tools/check_mypy_watermark.py` is byte-identical: `cd firestarter_app && git diff tools/check_mypy_watermark.py` is empty
    - Watermark comment at `pyproject.toml:115` is BYTE-IDENTICAL to its pre-task value (BLOCKER 4: Task 1 does NOT edit it; that's Task 2's job): `cd firestarter_app && git diff pyproject.toml -- | grep -E "mypy_error_watermark" | wc -l` returns 0
  </acceptance_criteria>
  <done>
    `pyproject.toml` has a new `[[tool.mypy.overrides]]` block listing exactly the 8 SC-literal modules with `disallow_untyped_defs = true` + `check_untyped_defs = true`; `firestarter/avr_tool.py` is in the `[tool.coverage.run] omit` list; the watermark comment is UNCHANGED in this task (lands in Task 2 per BLOCKER 4).
  </done>
</task>

<task type="auto">
  <name>Task 2: Add return-type annotations where mypy strict surfaces gaps in the 8 modules; THEN update mypy watermark in pyproject.toml (BLOCKER 4)</name>
  <files>firestarter_app/firestarter/cli_handlers.py, firestarter_app/firestarter/main.py, firestarter_app/firestarter/chip_resolver.py, firestarter_app/firestarter/frame_parser.py, firestarter_app/firestarter/codec.py, firestarter_app/firestarter/address_parser.py, firestarter_app/firestarter/exceptions.py, firestarter_app/firestarter/serial_comm.py, firestarter_app/pyproject.toml</files>
  <read_first>
    - Each of the 8 modules listed above — observe the current type-annotation state. Phase 40 added `-> None` and most other return types to `serial_comm.py` public methods (D-15..D-19); Phases 38/39/40/41 type-hinted helpers as they were moved. Most surface should already be clean; mypy strict surfaces residual gaps.
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md (D-06 + the canonical_refs section identify the 8 modules; the planner's job here is reactive — run mypy strict and fix whatever it surfaces; do not preemptively add annotations to functions that mypy doesn't complain about)
    - .planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md (D-08 py39 legacy typing: Optional[X], List[X], Tuple[X,Y], Callable[..., Any] — NOT X | None or PEP 604 syntax; `# noqa: UP006,UP035` markers preserved where applicable)
  </read_first>
  <action>
    **Two-phase task per BLOCKER 4:**

    **Phase A — Drive the strict-list modules to 0 errors:**

    Run `cd firestarter_app && mypy firestarter/cli_handlers.py firestarter/main.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py 2>&1` and read the surfaced errors. Most likely categories:

    - Missing return-type annotation on public functions/methods (mypy reports `Function is missing a return type annotation`)
    - Missing parameter annotations on public functions (mypy reports `Function is missing a type annotation for one or more arguments`)
    - Untyped function bodies where check_untyped_defs surfaces previously-hidden mismatches
    - `Any` returned where a more precise type is inferable

    For each surfaced error:
    1. **Prefer fixing in source** over `# type: ignore` per Phase 37 D-10 + Phase 41 pattern.
    2. **Use py39 legacy style** per Phase 37 D-08: `Optional[X]`, `List[X]`, `Tuple[X, Y]`, `Callable[..., Any]`, `Dict[K, V]`. NOT `X | None`. NOT PEP 604 union syntax. Add `# noqa: UP006,UP035` to typing imports where ruff's UP rules would auto-fix to PEP 585/604 syntax.
    3. **Match existing style** — if the file already uses `Optional[X]` for one optional, use `Optional[X]` for the new ones. Do NOT mix `Union[X, None]` and `Optional[X]` within a file.
    4. **NEVER use `# type: ignore`** unless the error is genuinely unfixable (e.g., a third-party stub gap) — and if used, the ignore MUST carry an inline reason comment and an issue link or a phase reference. Phase 41 W3 deviation #3 is the model.
    5. **Public-function helpers** (those without a leading underscore in their name) are the priority — internal helpers (`_complete_eprom`, `_build_op_flags`, `_FirmwareVersionType.convert`, etc.) get annotations only if mypy strict flags them.
    6. **Click handler signatures** — every `@cli.command()` callback already has explicit type-annotated parameters (Phase 41 D-08 pattern); mypy strict mostly surfaces missing `-> None` returns. Add `-> None` to every callback that lacks one.
    7. **`map_typed_errors` decorator** (added in Plan 42-02) — its signature is `def map_typed_errors(f: Callable[..., Any]) -> Callable[..., Any]:`; the inner wrapper's signature should be `def wrapper(*args: Any, **kwargs: Any) -> Any:`. If Plan 42-02 didn't include the `Any` annotations explicitly, add them here.

    Iterate until `cd firestarter_app && mypy firestarter/cli_handlers.py firestarter/main.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py` exits 0.

    If `eprom_operations.py` is somehow surfaced by the strict run (it shouldn't be unless mypy picks it up via cross-module type-narrowing), DO NOT add annotations to it — that's deferred to v1.9 per D-07.

    **Phase B — Update the mypy watermark comment in pyproject.toml (BLOCKER 4):**

    After Phase A has driven the 8 strict-list modules to 0 errors, run the full mypy command:

    `cd firestarter_app && mypy firestarter/ 2>&1 | tail -3`

    Read the total error count from the final "Found N errors in M files" line (or "Success" if zero). Update the comment at `pyproject.toml` line ~115:

    - Currently the comment reads: `# mypy_error_watermark = 44     # Baseline: Phase 37 tip. Lower as modules get typed.`
    - If the new full-mypy count is **lower than 44**, update to: `# mypy_error_watermark = N   # Updated Phase 42 D-08 post-strict-overrides addition. Old floor: 44 (Phase 37 tip).` where N is the new count.
    - If the new full-mypy count is **at or above 44**, that means the strict block surfaced errors elsewhere or the strict-list modules introduced new constraints that bubble up — fix them in source (loop back to Phase A); the watermark comment stays at 44 only after Phase A is genuinely 0-clean.
    - The script `tools/check_mypy_watermark.py` itself is NOT modified — only the comment value in pyproject.toml (the script reads the comment via regex).

    Capture the pre/post counts for the SUMMARY:
    - Pre-strict-add full mypy count (watermark): typically 44 from Phase 37 tip
    - Post-strict-add strict-list isolated count: target 0 (the 8 modules are mypy strict-clean)
    - Post-strict-add full mypy count: the value the watermark comment is updated to

    DO NOT:
    - Touch eprom_operations.py source (D-07 ring-fence; Plan 42-01's BUG-2 fix is the only allowed edit in this file across all of Phase 42)
    - Touch hardware.py, database.py, firmware.py, config.py, eprom_info.py, ic_layout.py, logging_utils.py, utils.py, messages.py source — these are NOT in the strict-list block
    - Add type annotations purely for completeness — mypy strict drives every edit (reactive fix only)
    - Change runtime behavior — type annotations are purely metadata
    - Modify `tools/check_mypy_watermark.py` (only the comment value in pyproject.toml changes per D-08)
  </action>
  <verify>
    <automated>cd firestarter_app && mypy firestarter/cli_handlers.py firestarter/main.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py 2>&1 | tail -5 && python tools/check_mypy_watermark.py</automated>
  </verify>
  <acceptance_criteria>
    - **Targeted strict-list mypy exits 0 (Phase A):** `cd firestarter_app && mypy firestarter/cli_handlers.py firestarter/main.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py` exits 0 (the new override block enforces this; targeted run validates each of the 8 modules independently is strict-clean)
    - `cd firestarter_app && mypy firestarter/main.py` exits 0 (0 errors)
    - `cd firestarter_app && mypy firestarter/cli_handlers.py` exits 0 (0 errors)
    - `cd firestarter_app && mypy firestarter/chip_resolver.py` exits 0
    - `cd firestarter_app && mypy firestarter/frame_parser.py` exits 0
    - `cd firestarter_app && mypy firestarter/codec.py` exits 0
    - `cd firestarter_app && mypy firestarter/address_parser.py` exits 0
    - `cd firestarter_app && mypy firestarter/exceptions.py` exits 0
    - `cd firestarter_app && mypy firestarter/serial_comm.py` exits 0
    - **Watermark updated (Phase B per BLOCKER 4):** `cd firestarter_app && python tools/check_mypy_watermark.py` exits 0 with the new value (the script reads the updated comment and compares to current `mypy firestarter/` count)
    - **Watermark comment edit is present:** `cd firestarter_app && git diff pyproject.toml -- | grep -cE "^[+-].*mypy_error_watermark"` returns at least 2 (one - for the old value, one + for the new) — confirms the watermark line was edited in this task per BLOCKER 4
    - `cd firestarter_app && grep -c "from __future__ import annotations" firestarter/cli_handlers.py firestarter/main.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py` returns 0 (py39 legacy style preserved per D-08)
    - **Portable grep alternation (WARNING 6):** `cd firestarter_app && for f in firestarter/cli_handlers.py firestarter/main.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py; do grep -cE "^# type: ignore|  # type: ignore$" "$f"; done | awk '{ s += $1 } END { print s }'` returns 0 OR each `# type: ignore` carries a phase-anchored reason comment (planner records exceptions in the SUMMARY)
    - `cd firestarter_app && ruff check firestarter/` exits 0 (no new ruff violations introduced by the type-annotation additions)
    - `cd firestarter_app && ruff format --check firestarter/` exits 0
    - `cd firestarter_app && pytest -v` exits 0 (no behavior change from type annotations)
    - `cd firestarter_app && git diff firestarter/eprom_operations.py` shows NO new changes beyond Plan 42-01's BUG-2 fix (D-07 read-path ring-fence preserved)
    - `tools/check_mypy_watermark.py` is byte-identical: `cd firestarter_app && git diff tools/check_mypy_watermark.py` is empty (only the COMMENT value in pyproject.toml changed)
  </acceptance_criteria>
  <done>
    All 8 strict-list modules are mypy strict-clean (0 errors each); the mypy watermark comment in pyproject.toml is updated to the post-strict-additions full-mypy count (BLOCKER 4 restructure: Task 2 owns this edit, not Task 1); no `# type: ignore` regressions introduced; py39 legacy typing preserved; ruff + ruff format gate green; full test suite still passes; eprom_operations.py untouched beyond Plan 42-01's BUG-2 fix; `tools/check_mypy_watermark.py` byte-identical.
  </done>
</task>

<task type="auto">
  <name>Task 3: Add docstrings to all 20 Click callbacks + missing public-function docstrings; intermediate verification checkpoint (WARNING 5)</name>
  <files>firestarter_app/firestarter/cli_handlers.py</files>
  <read_first>
    - firestarter_app/firestarter/cli_handlers.py (current state — scout the docstring status of every @cli.command() / @cli.group() / @dev.command() callback; many already have docstrings from Phase 41 W3 — list/info/search/read/write/verify/blank/erase/chip_id all have 1-line docstrings; vpp/vpe/hw/config/fw/dev/dev_read/dev_reg/dev_addr/dev_consistency_check status varies — verify each before editing)
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md (D-09 specifies docstring scope = SC literal modules' public surface only; D-09 specifies the first-line docstring text must match the existing argparse `help=` text — which Phase 41 W4 ported into Click's `help=` parameter on each command)
    - firestarter_app/tests/__snapshots__/test_characterization.ambr (read at least one `--help`-related snapshot to confirm Click's --help formatting derives from docstring + help= — the snapshots are the GATE-1.8b witness; any drift means a regression to fix in-wave)
  </read_first>
  <action>
    For every `@cli.command()` / `@cli.group()` / `@dev.command()` callback in `firestarter_app/firestarter/cli_handlers.py`, ensure the function body's FIRST statement is a triple-quoted docstring with a 1-line summary.

    Per D-09, the FIRST LINE of each docstring MUST be byte-identical to the user-visible summary Click already shows in `--help`. Click derives this from the docstring's first line (PEP 257 style). The 29 syrupy snapshots in `test_characterization.ambr` pin Click's `--help` output for the relevant commands; if the existing first-line text on a command is already byte-identical to its `--help` summary, leave it unchanged.

    Concrete per-callback target state (planner scouts each before editing) — the count is **20 callbacks total** per BLOCKER 3 lock (1 cli group + 14 commands + 1 dev group + 4 dev sub-commands):

    - `cli` group (line ~268): existing docstring `"""EPROM programmer for Arduino and Relatively-Universal-ROM-Programmer shield."""` already present — no edit
    - `_list_cmd` / list (line ~300): existing `"""List all EPROMs in the database."""` — no edit
    - `info` (line ~314): existing `"""EPROM info."""` — no edit
    - `search` (line ~346): existing `"""Search for EPROMs in the database."""` — no edit
    - `read` (line ~371): existing `"""Reads the content from an EPROM."""` — no edit
    - `write` (line ~415): existing multi-line docstring starting `"""Writes a binary file to an EPROM."""` — no edit (first line is the summary; the rest documents the TRAP #3 polarity rationale)
    - `verify` (line ~458): existing `"""Verifies the content of an EPROM."""` — no edit
    - `blank` (line ~488): existing `"""Checks if an EPROM is blank."""` — no edit
    - `erase` (line ~524): existing multi-line docstring `"""Erase an EPROM, if supported."""` + body — no edit
    - `chip_id` / id (line ~558): existing `"""Checks an EPROM, if supported."""` — no edit
    - `vpp` (line ~599): existing `"""VPP voltage."""` — no edit
    - `vpe` (line ~610): existing `"""VPE voltage."""` — no edit
    - `hw` (line ~625): existing `"""Hardware revision."""` — no edit
    - `config` (line ~655): existing `"""Handles CONFIGURATION values."""` — no edit
    - `fw` (line ~763): existing multi-line docstring `"""Firmware version."""` — no edit
    - `dev` group (line ~870): existing `"""Debug command for development purposes."""` + body — no edit
    - `dev_read` (line ~888): existing `"""Reads the content from an EPROM and prints data to console."""` — no edit
    - `dev_reg` (line ~950): existing `"""Direct access to registers: MSB, LSB and control register."""` — no edit
    - `dev_addr` (line ~988): existing `"""Direct access to address lines and control register."""` — no edit
    - `dev_consistency_check` (line ~1046): existing multi-line docstring — no edit

    Scout confirms: per the verbatim file content read at planning time, EVERY Click callback already has a docstring (Phase 41 W3 / W4 work). D-09's docstring-additions concern is likely a no-op for cli_handlers.py at the callback level. The planner verifies this empirically; if a missing docstring surfaces, add one matching the existing `help=` text. If ALL 20 callbacks already have docstrings, this task is a verification-only no-op for callbacks.

    For non-callback public functions in cli_handlers.py — `map_typed_errors` (added in Plan 42-02), `build_arg_flags`, `_maybe_auto_route_to_pre`, `_setup_logging`, `_complete_eprom`, `_FirmwareVersionType.convert`, `_build_op_flags`, `_maybe_auto_route_to_pre_click` — verify each has a docstring; add a 1-liner where missing. Scout: most already have docstrings (Phase 41 W3/W4 lineage).

    For the other 7 strict-list modules (`main.py`, `chip_resolver.py`, `frame_parser.py`, `codec.py`, `address_parser.py`, `exceptions.py`, `serial_comm.py`):
    - Verify each has a module-level docstring (scout: all 8 already do per CONTEXT D-09)
    - Add public-function docstrings where missing (most likely a no-op given Phase 38/39/40/41 work)
    - DO NOT add docstrings to any function in `eprom_operations.py`, `hardware.py`, `firmware.py`, `database.py`, `config.py`, `eprom_info.py`, `ic_layout.py`, `logging_utils.py`, `utils.py`, `messages.py`, `avr_tool.py` — out of D-09's scope (those modules are not in the 8-module strict list)

    DO NOT:
    - Modify any existing docstring's first line — it would risk drift against the 29 syrupy snapshots that pin Click's --help output
    - Add docstrings with PEP 257 style sections (Args:, Returns:, Raises:) unless the existing file style already uses them (D-09: match what's already in the file)
    - Add docstrings to test files (test functions don't need them per Phase 36 D-02 fixture convention; the `# noqa: D` rule is not in the ruff config)
    - Add docstrings to private functions in non-strict-list modules
  </action>
  <verify>
    <automated>cd firestarter_app && python -c "import ast; src = open('firestarter/cli_handlers.py').read(); tree = ast.parse(src); funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]; missing = [f.name for f in funcs if any(isinstance(d, ast.Attribute) and d.attr in ('command', 'group') for stmt in f.decorator_list for d in (ast.walk(stmt))) and not (f.body and isinstance(f.body[0], ast.Expr) and isinstance(f.body[0].value, ast.Constant) and isinstance(f.body[0].value.value, str))]; print('missing_docstrings:', missing)"</automated>
    <human-check>
    **Intermediate verification checkpoint (advisory in-task gate per WARNING 5)** — NOT a commit boundary; single atomic commit still lands at Task 7.

    After Tasks 1-3 are complete (override block + omit entry + watermark edit + type annotations + docstrings), run:

    `cd firestarter_app && ruff check . && mypy firestarter/cli_handlers.py firestarter/main.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py && pytest -x`

    Must exit 0. If it fails, fix in-wave before continuing to Task 4 — context-exhaustion partial recovery becomes salvageable at this checkpoint because typing + docstring work is now stable on the strict-list modules.
    </human-check>
  </verify>
  <acceptance_criteria>
    - `cd firestarter_app && python -c "import ast; src = open('firestarter/cli_handlers.py').read(); tree = ast.parse(src); count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.body and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant) and isinstance(n.body[0].value.value, str))" && echo OK` exits 0 (informational — at least 20+ docstrings present across all functions in cli_handlers.py)
    - `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (29 syrupy snapshots green — Click's --help formatting unchanged because first-line docstrings are unchanged or newly-added with text matching existing `help=` text)
    - For every of the 8 strict-list modules, `python -c "import ast; src = open('firestarter/<module>.py').read(); tree = ast.parse(src); assert isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant)"` exits 0 (module-level docstring present — verified for main, cli_handlers, chip_resolver, frame_parser, codec, address_parser, exceptions, serial_comm)
    - `cd firestarter_app && ruff check firestarter/` exits 0 (no new ruff violations introduced by docstring additions)
    - `cd firestarter_app && ruff format --check firestarter/` exits 0
    - `cd firestarter_app && mypy firestarter/cli_handlers.py firestarter/main.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py` exits 0 (Task 2's strict-clean state preserved; docstring additions are mypy-transparent)
    - Naming verification (D-10): `cd firestarter_app && grep -nE "^def [a-z]+[A-Z][a-zA-Z_]*\(" firestarter/*.py | wc -l` returns 0 (zero camelCase function defs in any firestarter source module — confirms snake_case conformance; documents D-10 "no rename needed")
    - **Intermediate verification checkpoint (WARNING 5):** `cd firestarter_app && ruff check . && mypy firestarter/cli_handlers.py firestarter/main.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py && pytest -x` exits 0 (advisory smoke gate; if context exhaustion forces partial recovery, this is the safe resume point)
  </acceptance_criteria>
  <done>
    Every Click callback in cli_handlers.py has a first-line docstring matching its existing `help=` text (D-09); every public function in the 8 strict-list modules has a docstring (added where missing — most already present from Phases 38-41); naming verified snake_case (D-10 confirmed conformant); ruff + format + mypy + 29 syrupy snapshots all green; intermediate verification checkpoint (Tasks 1-3 stable per WARNING 5).
  </done>
</task>

<task type="auto">
  <name>Task 4: Add test_database_conversion.py covering database.convert_to_programmer + DIP→RURP translation</name>
  <files>firestarter_app/tests/test_database_conversion.py</files>
  <read_first>
    - firestarter_app/firestarter/database.py (observe convert_to_programmer signature + the pin_conversions dict + the data flow `get_eprom → convert_to_programmer → wire JSON`; review at least one chip's actual record for the test fixture values — W27C512 is the canonical test chip per Phase 36 D-02 and v1.6 read-bug evidence)
    - firestarter_app/firestarter/data/chip_database.json (find canonical entries for W27C512 (28-pin, algo 0x07), AT28C256 (28-pin, algo 0x0D per WARNING-5 override), AM29F040 (32-pin, flash family), 6116-class (SRAM); read enough of each to ensure test values are byte-accurate)
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md (D-14.1 specifies the scope: representative chip records covering pinout classes + algorithm dispatch; target coverage lift database.py 60% → ~80% / ~50 lines)
    - firestarter_app/tests/conftest.py (no fixtures needed for this test — database.convert_to_programmer is a pure data-transform; the test instantiates EpromDatabase directly with skip_local_override=True per Phase 36 D-06)
    - firestarter_app/tests/test_eprom_database.py (existing tests on EpromDatabase — verify what's already covered to avoid duplication; this new file adds convert_to_programmer + DIP→RURP coverage that isn't pinned by test_eprom_database.py)
    - .planning/phases/36-characterization-test-baseline/36-CONTEXT.md (D-06 EpromDatabase.skip_local_override seam — required for hermetic tests)
  </read_first>
  <action>
    Create the new file `firestarter_app/tests/test_database_conversion.py` with the following structure:

    1. Module docstring (≤2 lines) — names the file as the Phase 42 / ERR-03 coverage lift for `database.convert_to_programmer` + DIP→RURP pin translation; cites D-14.1.

    2. Imports — `pytest`, `from firestarter.database import EpromDatabase`. The test uses `EpromDatabase(skip_local_override=True)` for hermetic construction (Phase 36 D-06 seam) — no `~/.firestarter/database.json` override interference.

    3. Module-level fixture `@pytest.fixture(scope="module")` `db` → returns `EpromDatabase(skip_local_override=True)`. (Scope=module so the JSON load is cached; convert_to_programmer is read-only against the loaded data.)

    4. Test functions covering convert_to_programmer for representative chips:
       - `test_convert_w27c512_28pin_uveprom(db)` — get_eprom("W27C512"), assert algorithm field == 7 (algo 0x07 / 28-pin CMOS UV-EPROM), assert pinout-class key, assert DIP→RURP bus-config translation produces the expected `pin-count: 28` and a valid `bus-config` dict
       - `test_convert_at28c256_28pin_5v_eeprom_override(db)` — get_eprom("AT28C256"), assert algorithm field == 13 (0x0D — WARNING-5 routing override; if the planner's empirical scout shows a different algorithm, use the actual value), assert pin-count: 28 and the bus-config does NOT engage P1_VPP_ENABLE (5V EEPROM safety per CLAUDE.md)
       - `test_convert_am29f040_32pin_flash(db)` — get_eprom("AM29F040") (or the closest match in chip_database.json — the planner picks; the goal is a 32-pin Flash representative), assert pin-count: 32 + algorithm matching the flash dispatch
       - `test_convert_6116_class_sram(db)` — find a 6116-class SRAM (24-pin or 28-pin SRAM dispatch; algo 0x0E/0x27/0x28/0x29 per CLAUDE.md), assert pin-count + algorithm matches SRAM family
       - `test_convert_unknown_chip_returns_none(db)` — get_eprom("NONEXISTENT_CHIP_XYZ") returns None (no convert_to_programmer call needed; this pins the not-found path that ChipNotFoundError sits above in chip_resolver.py)

    5. (Optional, if coverage margin requires) Per-pin DIP→RURP translation test for one chip — assert the `bus-config` field contains the expected line-number mappings for a known socket pin (e.g. pin 14 GND, pin 28 VCC). The pin_conversions dict at database.py:N is the source of truth; test values must reference actual data from `data/pinouts.json` or the database itself (no hardcoded fictional values).

    Style constraints:
    - py39 legacy typing throughout; no `from __future__ import annotations`
    - Test function names follow `test_<scenario>` convention; per-test docstring is optional (D-09 docstring scope is the 8 strict-list source modules, not tests)
    - ruff check / ruff format gate green
    - Tests are FAST (≤ 100ms each on `pytest tests/test_database_conversion.py -v`)
    - No real serial I/O; no real hardware; no real avrdude

    DO NOT:
    - Modify `database.py` source (this is a coverage-lift task; the module is not in the 8 strict-list)
    - Modify `chip_database.json` (D-13.1 forbid; data sub-tree untouched)
    - Use `unittest.mock.Mock` for the EpromDatabase — the real DB is what we're testing
    - Assume chip records that don't exist — scout the actual `chip_database.json` for valid representative entries
  </action>
  <verify>
    <automated>cd firestarter_app && pytest tests/test_database_conversion.py -v</automated>
  </verify>
  <acceptance_criteria>
    - `firestarter_app/tests/test_database_conversion.py` exists
    - `cd firestarter_app && grep -cE "^def test_" tests/test_database_conversion.py` returns at least 4 (4 happy-path tests + 1 not-found path = 5 typical)
    - `cd firestarter_app && grep -c "from firestarter.database import EpromDatabase" tests/test_database_conversion.py` returns exactly 1
    - `cd firestarter_app && grep -c "skip_local_override=True" tests/test_database_conversion.py` returns at least 1 (hermetic construction per Phase 36 D-06)
    - `cd firestarter_app && grep -c "convert_to_programmer" tests/test_database_conversion.py` returns at least 3 (multiple call sites across the 4+ tests)
    - `cd firestarter_app && pytest tests/test_database_conversion.py -v` exits 0; all tests PASS
    - `cd firestarter_app && pytest tests/test_database_conversion.py --cov=firestarter.database --cov-report=term 2>&1 | grep "database.py"` shows the database.py coverage rising from ~60% toward 80% (informational; absolute number depends on which lines the tests exercise)
    - `cd firestarter_app && ruff check tests/test_database_conversion.py` exits 0
    - `cd firestarter_app && ruff format --check tests/test_database_conversion.py` exits 0
    - `cd firestarter_app && git diff firestarter/database.py` is empty (source untouched)
  </acceptance_criteria>
  <done>
    `tests/test_database_conversion.py` adds ≥4 passing tests covering convert_to_programmer + DIP→RURP translation for representative chips; database.py coverage rises measurably; the source module is unchanged.
  </done>
</task>

<task type="auto">
  <name>Task 5: Add test_eprom_operations.py covering write/verify/blank/erase happy paths ONLY (NO BUG-2 regression test per WARNING 10; READ path EXERCISED but NEVER modified per GATE-1.8d)</name>
  <files>firestarter_app/tests/test_eprom_operations.py</files>
  <read_first>
    - firestarter_app/firestarter/eprom_operations.py (observe write_eprom/verify_eprom/blank_check_eprom/erase_eprom + the _run_state_machine driver + the COMMAND_NAMES dispatch; read CAREFULLY but DO NOT MODIFY — only Plan 42-01's BUG-2 fix is allowed across all of Phase 42 per D-07)
    - firestarter_app/tests/conftest.py (make_comm + fake_serial fixtures — Phase 36 D-02 lock; the test instantiates EpromOperator with a fake comm wired to fake_serial, then feeds wire-framed bytes via fake_serial.feed(...))
    - firestarter_app/tests/test_serial_characterization.py (existing pattern for feeding wire frames to make_comm-based tests; this new test file mirrors the structure)
    - firestarter_app/tests/test_bug_characterization.py (CRITICAL per WARNING 10: the BUG-2 contract test already lives at `tests/test_bug_characterization.py::test_eprom_operation_error_not_labeled_as_communication_error` — flipped to passing by Plan 42-01. DO NOT add a parallel BUG-2 regression test in `test_eprom_operations.py` — that would create duplicate coverage. Read this file to confirm the existing contract test is sufficient as the BUG-2 regression guard.)
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md (D-14.2 specifies the scope: write/verify/blank/erase happy paths via make_comm + fake_serial; target coverage lift eprom_operations.py 58% → ~75% / ~75 lines; CRITICAL: must NOT modify the source — only exercise it)
    - firestarter_app/firestarter/messages.py (observe the MSG_* constants for ACK/OK/INIT/MAIN/END/ERROR framing — the test feeds these to fake_serial)
  </read_first>
  <action>
    Create the new file `firestarter_app/tests/test_eprom_operations.py` (NEW — if Phase 36 left a stub at this path, scout it first via `ls firestarter_app/tests/test_eprom_operations.py 2>/dev/null` and merge with the stub; per CONTEXT.md "May coexist with an existing tests/test_eprom_operations.py if Phase 36 stub created one; planner merges"). Structure:

    1. Module docstring (≤2 lines) — names the file as the Phase 42 / ERR-03 coverage lift for EpromOperator write/verify/blank/erase HAPPY PATHS ONLY; cites D-14.2 + the GATE-1.8d read-path EXERCISE-DON'T-MODIFY contract + WARNING 10 (BUG-2 contract lives in test_bug_characterization.py — no duplicate here).

    2. Imports — `pytest`, `from firestarter.config import ConfigManager`, `from firestarter.eprom_operations import EpromOperator`, `from firestarter.constants import <relevant COMMAND_* / FLAG_* / MSG_* constants>` (named imports per Phase 39 D-06; planner picks the precise list from messages.py + constants.py based on what each test feeds).

    3. Test functions covering EpromOperator operations via the existing `make_comm` + `fake_serial` fixture pattern. Each test:
       - Constructs `config = ConfigManager()` (or uses the planner's preferred fixture for a hermetic config — Phase 36 D-02 pattern)
       - Constructs `operator = EpromOperator(config)`
       - Wires `operator.comm = make_comm()` (the make_comm fixture returns a SerialCommunicator wired to fake_serial via __new__ + injected port)
       - Feeds the wire-framed bytes the firmware would send back during a successful operation via `fake_serial.feed(build_frame(MSG_OK, b""))` etc.
       - Calls the operation (write_eprom / verify_eprom / blank_check_eprom / erase_eprom) with a minimal valid eprom_data dict
       - Asserts the returned bool == True (happy path) and the operation_name field in the wire-sent JSON command matches the expected COMMAND_* dispatch

    Minimum tests (happy paths only per CONTEXT D-14.2; the BUG-2 regression guard is OUT OF SCOPE per WARNING 10):
    - `test_blank_check_eprom_happy_path(make_comm, fake_serial)` — feeds the INIT → MAIN-blank-pass → END frame sequence; asserts blank_check_eprom returns True
    - `test_erase_eprom_happy_path(make_comm, fake_serial)` — feeds the INIT → MAIN-erase-ok → END sequence; asserts erase_eprom returns True
    - `test_write_eprom_happy_path(make_comm, fake_serial, tmp_path)` — creates a tiny test bin file in tmp_path, feeds the INIT → MAIN-data-chunk-loop → END sequence; asserts write_eprom returns True
    - `test_verify_eprom_happy_path(make_comm, fake_serial, tmp_path)` — same pattern for verify_eprom

    **WARNING 10 lock:** Do NOT add a `test_blank_check_eprom_failure_via_eprom_operation_error` or any other test that asserts the "Programmer error" log label / BUG-2 behavior. That contract lives at `tests/test_bug_characterization.py::test_eprom_operation_error_not_labeled_as_communication_error` (flipped to PASSED by Plan 42-01). Adding a parallel regression test here creates duplicate coverage — explicitly prohibited per the revision instructions.

    If the planner empirically discovers the 4 happy-path tests don't lift `eprom_operations.py` coverage from 58% → ~75% per D-14.2, add MORE happy-path variants (e.g., write_eprom with a multi-chunk buffer, verify_eprom with a 5-byte mismatch tolerance) — NOT BUG-2-related error-path tests.

    Read-path EXERCISE without MODIFY contract (CRITICAL per GATE-1.8d):
    - The test file MUST NOT contain any `read_eprom(...)` call that exercises a NEW code path in eprom_operations.py
    - The test file MUST NOT contain any patch / monkey-patch / mock of `_run_state_machine` or `_read_and_parse_lines` (those are read-path territory)
    - The test file MAY incidentally invoke `read_eprom` if it's part of the verify_eprom call chain — that's transitive exercise, not modification
    - `cd firestarter_app && git diff firestarter/eprom_operations.py` MUST be empty (no source changes; only Plan 42-01's BUG-2 fix is allowed)

    Style constraints:
    - py39 legacy typing; no `from __future__ import annotations`
    - ruff check / ruff format gate green
    - Tests are FAST (≤ 1 second each)
    - No real serial I/O; no real hardware

    DO NOT:
    - Add a BUG-2 regression test (WARNING 10 — duplicate of test_bug_characterization.py contract)
    - Modify `eprom_operations.py` (D-07 ring-fence)
    - Modify `serial_comm.py` (GATE-1.8a wire protocol untouched)
    - Use `unittest.mock.Mock` to bypass the wire-frame path — use the canonical `make_comm` + `fake_serial.feed(...)` pattern per Phase 36 D-02
  </action>
  <verify>
    <automated>cd firestarter_app && pytest tests/test_eprom_operations.py -v && git diff firestarter/eprom_operations.py | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - `firestarter_app/tests/test_eprom_operations.py` exists
    - `cd firestarter_app && grep -cE "^def test_" tests/test_eprom_operations.py` returns at least 4 (write/verify/blank/erase happy paths; NO BUG-2 regression test per WARNING 10)
    - **WARNING 10 lock asserted:** `cd firestarter_app && grep -c "not_labeled_as_communication_error\|Programmer error during\|BUG-2 regression" tests/test_eprom_operations.py` returns 0 (no BUG-2 regression test surface area in this file; that contract lives in test_bug_characterization.py)
    - `cd firestarter_app && grep -c "from firestarter.eprom_operations import EpromOperator" tests/test_eprom_operations.py` returns exactly 1
    - `cd firestarter_app && grep -c "make_comm" tests/test_eprom_operations.py` returns at least 4 (fixture used in each test)
    - `cd firestarter_app && grep -c "fake_serial" tests/test_eprom_operations.py` returns at least 4
    - `cd firestarter_app && grep -c "fake_serial.feed" tests/test_eprom_operations.py` returns at least 4 (wire frames fed to drive each operation)
    - `cd firestarter_app && pytest tests/test_eprom_operations.py -v` exits 0; all tests PASS
    - `cd firestarter_app && git diff firestarter/eprom_operations.py` matches the diff produced by Plan 42-01 only — NO additional changes from Plan 42-03 (D-07 ring-fence preserved): the file's only Phase 42 edits are the BUG-2 except-clause split from Plan 42-01
    - `cd firestarter_app && pytest tests/test_eprom_operations.py --cov=firestarter.eprom_operations --cov-report=term 2>&1 | grep "eprom_operations.py"` shows coverage rising from ~58% toward 75% (informational)
    - `cd firestarter_app && ruff check tests/test_eprom_operations.py && ruff format --check tests/test_eprom_operations.py` exits 0
  </acceptance_criteria>
  <done>
    `tests/test_eprom_operations.py` adds ≥4 passing happy-path tests covering write/verify/blank/erase via make_comm + fake_serial fixture; NO BUG-2 regression test (WARNING 10 — that contract lives in test_bug_characterization.py); eprom_operations.py coverage rises measurably; the source module is unchanged beyond Plan 42-01's BUG-2 fix (GATE-1.8d preserved).
  </done>
</task>

<task type="auto">
  <name>Task 6: Extend test_firmware_install.py with _get_releases_response_json + _compare_versions coverage; add test_config.py + test_hardware.py; intermediate coverage checkpoint (WARNING 5)</name>
  <files>firestarter_app/tests/test_firmware_install.py, firestarter_app/tests/test_config.py, firestarter_app/tests/test_hardware.py</files>
  <read_first>
    - firestarter_app/tests/test_firmware_install.py (existing test file from Phase 18; scout the current structure + fixture patterns; D-14.3 extends this file rather than creating a new one)
    - firestarter_app/firestarter/firmware.py (observe `_get_releases_response_json` + `_compare_versions` + the PEP 440 branch logic — the test exercises both functions)
    - firestarter_app/firestarter/config.py (observe ConfigManager.get_value / set_value / persist + override file resolution — D-14.4 covers these happy paths)
    - firestarter_app/firestarter/hardware.py (observe HardwareManager.read_vpp_voltage + read_vpe_voltage — D-14.5 covers READ-side only; voltage-engagement methods set_vpp_voltage / set_vpe_voltage stay UNTESTED per the safety boundary)
    - firestarter_app/tests/conftest.py (make_comm + fake_serial fixtures used by test_hardware.py)
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md (D-14.3, D-14.4, D-14.5 specify each file's scope + line targets; "Per-callback ordering of test additions" in Claude's Discretion suggests test_firmware_install.py extension first, then test_config.py, then test_hardware.py)
  </read_first>
  <action>
    Three coordinated edits across three test files:

    1. **EDIT `firestarter_app/tests/test_firmware_install.py`** per D-14.3. Read the existing structure; APPEND (do not replace) new test functions covering:
       - `_get_releases_response_json` JSON parsing for the GitHub Releases API shape (mock `requests.get` with a `responses` library fixture or `unittest.mock.patch`; assert the returned dict has the expected keys for stable + pre-release responses)
       - `_compare_versions` PEP 440 branches: stable-vs-stable, stable-vs-pre, pre-vs-pre, invalid-string error path (PEP 440 raises InvalidVersion which firmware.py guards against)
       - At least 4-6 new tests, ~60 lines total per D-14.3 target

       Imports added to the file (if not already present): `from firestarter.firmware import _get_releases_response_json, _compare_versions` (the planner verifies the exact private-name exports against the current firmware.py; if the names differ — e.g. the function is `_compare_versions(v1, v2)` vs `compare_versions` — the planner uses the actual current name).

    2. **CREATE `firestarter_app/tests/test_config.py`** per D-14.4. Structure:
       - Module docstring naming the Phase 42 / ERR-03 coverage lift for ConfigManager; cites D-14.4
       - Imports: `pytest`, `from firestarter.config import ConfigManager`, `tmp_path` fixture for isolated config-file location
       - At least 4-5 tests:
         - `test_config_manager_get_default_value(tmp_path)` — instantiates ConfigManager with a tmp_path-rooted config file, calls `get_value("nonexistent_key", "default")`, asserts returns "default"
         - `test_config_manager_set_persist_true(tmp_path)` — calls `set_value("port", "/dev/ttyACM0", persist=True)`, asserts the value is in the config file on disk + reloadable via a fresh ConfigManager instance
         - `test_config_manager_set_persist_false(tmp_path)` — calls `set_value("port", "/dev/ttyACM0", persist=False)`, asserts the value is in memory only; a fresh ConfigManager does NOT see it
         - `test_config_manager_override_file_resolution(tmp_path)` — covers the `~/.firestarter/config.json` override path resolution; assert precedence rules
         - (Optional) `test_config_manager_persist_writes_valid_json(tmp_path)` — asserts the persisted file is JSON-parseable

       Style: py39 legacy typing; ruff/format clean. Target ~50 lines covered in config.py per D-14.4.

    3. **CREATE `firestarter_app/tests/test_hardware.py`** per D-14.5. Structure:
       - Module docstring naming the Phase 42 / ERR-03 coverage lift for HardwareManager READ-side voltage methods; cites D-14.5 + the safety-boundary rationale (voltage-engagement methods stay UNTESTED — set_vpp_voltage / set_vpe_voltage engage the VPP regulator)
       - Imports: `pytest`, `from firestarter.config import ConfigManager`, `from firestarter.hardware import HardwareManager`, `make_comm` + `fake_serial` fixtures
       - At least 3-4 tests, all READ-SIDE ONLY:
         - `test_read_vpp_voltage_happy_path(make_comm, fake_serial)` — feeds a wire-framed VPP-voltage response; asserts read_vpp_voltage returns True and the value matches the fed payload
         - `test_read_vpe_voltage_happy_path(make_comm, fake_serial)` — same pattern for VPE
         - `test_get_hardware_revision_happy_path(make_comm, fake_serial)` — covers the `hw` command's underlying `get_hardware_revision` call
         - (Optional) `test_set_hardware_config_happy_path(make_comm, fake_serial)` — covers `set_hardware_config` (NOT to be confused with set_vpp_voltage which engages the VPP regulator; set_hardware_config writes the rurp_configuration_t EEPROM bytes which is safe)

       CRITICAL SAFETY: NO test calls `set_vpp_voltage` or `set_vpe_voltage` (those engage the VPP regulator). The test file's docstring + an in-file comment block explain why these methods stay UNTESTED per D-14.5 — safety boundary, not a coverage hole.

       Target ~40 lines covered in hardware.py per D-14.5 (13% → ~40%).

    DO NOT:
    - Modify firmware.py, config.py, or hardware.py source (none of these are in the 8-module strict-list AND the coverage tests should NOT need source edits to land green)
    - Add tests that touch real serial / real hardware / real avrdude
    - Inflate the test count beyond what's needed to hit the coverage floor; if 3 tests per file clears the per-module target, stop there
  </action>
  <verify>
    <automated>cd firestarter_app && pytest tests/test_firmware_install.py tests/test_config.py tests/test_hardware.py -v</automated>
    <human-check>
    **Intermediate verification checkpoint (advisory in-task gate per WARNING 5)** — NOT a commit boundary; single atomic commit still lands at Task 7.

    After Tasks 4-6 are complete (all 5 test files added/extended), run:

    `cd firestarter_app && pytest --cov=firestarter --cov-report=term-missing`

    Must report ≥ 70.0% overall coverage. If coverage falls short of 70%, add fallback small tests on logging_utils.py or utils.py per CONTEXT D-14 fallback (1-2 small test files; both small surface, easy targeted lifts) BEFORE proceeding to Task 7. This is the salvageable recovery point if context exhaustion forces a partial-recovery hand-off.
    </human-check>
  </verify>
  <acceptance_criteria>
    - `firestarter_app/tests/test_config.py` exists
    - `firestarter_app/tests/test_hardware.py` exists
    - `firestarter_app/tests/test_firmware_install.py` exists (was already present; this task EXTENDS it)
    - `cd firestarter_app && grep -cE "^def test_" tests/test_config.py` returns at least 4
    - `cd firestarter_app && grep -cE "^def test_" tests/test_hardware.py` returns at least 3
    - `cd firestarter_app && grep -cE "^def test_" tests/test_firmware_install.py` returns more than its pre-task count (Phase 18 baseline + Phase 42 additions; planner records the delta in the SUMMARY)
    - `cd firestarter_app && grep -c "set_vpp_voltage\|set_vpe_voltage" tests/test_hardware.py` returns 0 (CRITICAL SAFETY — voltage-engagement methods are NOT called per D-14.5)
    - `cd firestarter_app && pytest tests/test_firmware_install.py tests/test_config.py tests/test_hardware.py -v` exits 0; all tests PASS
    - `cd firestarter_app && ruff check tests/test_firmware_install.py tests/test_config.py tests/test_hardware.py` exits 0
    - `cd firestarter_app && ruff format --check tests/test_firmware_install.py tests/test_config.py tests/test_hardware.py` exits 0
    - `cd firestarter_app && git diff firestarter/firmware.py firestarter/config.py firestarter/hardware.py` is empty (source unchanged)
    - **Intermediate coverage checkpoint (WARNING 5):** `cd firestarter_app && pytest --cov=firestarter --cov-report=term-missing 2>&1 | grep TOTAL` reports coverage ≥ 70.0% overall (target empirically verified before Task 7 commit per D-15; if below 70%, add fallback tests per D-14 fallback BEFORE proceeding)
  </acceptance_criteria>
  <done>
    test_firmware_install.py extended with PEP 440 + JSON-parser tests; test_config.py and test_hardware.py created with safe read-side coverage; total firestarter coverage at or above 70% empirically (intermediate checkpoint per WARNING 5); no source files modified.
  </done>
</task>

<task type="auto">
  <name>Task 7: Flip CI --cov-fail-under from 50 → 70; ERR-01 SC#1 grep verification (BLOCKER 2); run full gate; commit Plan 42-03 as single atomic commit</name>
  <files>firestarter_app/.github/workflows/ci.yml</files>
  <read_first>
    - firestarter_app/.github/workflows/ci.yml (line 57-58 — the pytest step with `--cov-fail-under=50`; this is the line D-15 flips)
    - .planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md (D-15 specifies the flip happens in the SAME atomic commit as the test additions; D-16 specifies the commit subject + body verbatim)
    - .planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md (D-04 measured 51.33% / floor 50%, ratcheted to ≥70% in Phase 42 — the documented ratchet point)
    - firestarter_app/pyproject.toml (any `.pre-commit-config.yaml`-equivalent threshold reference; if absent, no edit needed)
  </read_first>
  <action>
    Four coordinated final steps:

    1. **Flip the CI coverage threshold.** In `firestarter_app/.github/workflows/ci.yml`:
       - Line 58 currently reads `run: pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=50`
       - Edit the `--cov-fail-under=50` to `--cov-fail-under=70` (D-15 + Phase 37 D-04 ratchet completion)
       - Preserve all other tokens on the line byte-identically

    2. **Verify no other workflow/script/pre-commit config carries the 50% threshold.** Run `cd firestarter_app && grep -rn "cov-fail-under=50\|cov-fail-under = 50\|cov_fail_under = 50" . --include="*.yml" --include="*.yaml" --include="*.toml" --include="*.cfg" --include="Makefile" --include="*.sh"` — must return 0 lines after the edit. If any other site is found (e.g., a `.pre-commit-config.yaml` or a Makefile), update it in lockstep per D-15.

    3. **Run the full local gate** to confirm Plan 42-03 has not regressed anything, AND close BLOCKER 2 (ERR-01 SC#1 grep contract):
       - `cd firestarter_app && ruff check . && ruff format --check . && python tools/check_mypy_watermark.py` — must exit 0
       - `cd firestarter_app && mypy firestarter/main.py firestarter/cli_handlers.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py` — must exit 0 for ALL 8 strict-list modules (the new override block enforces this)
       - `cd firestarter_app && pytest -v` — must exit 0 with all tests PASSING (no xfails; BUG-2 still PASSED from Plan 42-01; the new test files all pass)
       - `cd firestarter_app && pytest --cov=firestarter --cov-fail-under=70` — must exit 0; the coverage threshold gate at 70% passes
       - `cd firestarter_app && pytest tests/test_characterization.py -v` — must exit 0 with 29 syrupy snapshots green
       - `cd firestarter_app && pip install -e . && firestarter --help` — CLI-04 SC#4 smoke test stays green
       - **BLOCKER 2 ERR-01 SC#1 grep verification:**
         - `cd firestarter_app && grep -rn "except:" firestarter/ | wc -l` — must return 0 (no bare except sites; scout-verified zero pre-fix, this confirms post-fix)
         - `cd firestarter_app && grep -rn "except Exception" firestarter/ | grep -vE "as e($|[^a-zA-Z_])" | wc -l` — must return 0 (every `except Exception` site binds `as e`; the trailing pattern `as e($|[^a-zA-Z_])` matches `as e` followed by end-of-line or any non-identifier char so `as eprom` etc. don't false-match)

    4. **Commit the single atomic Plan 42-03 commit** on the `firestarter_app/` submodule's `v1.8-app-cleanup` branch (worktrees off per `project_v18_phase_execution_mechanics`):

       Subject line: `chore(42-03): raise v1.8 quality gates — mypy strict on 8 modules, docstrings + coverage ≥70% (ERR-02, ERR-03)`

       Body (HEREDOC; includes D-XX references for traceability):
       `Closes ERR-02 + ERR-03 + ERR-01 SC#1 literal grep contract (BLOCKER 2). Single atomic commit raising the v1.8 quality bar end-to-end.

       Mypy strict (D-06): adds [[tool.mypy.overrides]] block for 8 modules (main, cli_handlers, chip_resolver, frame_parser, codec, address_parser, exceptions, serial_comm) with disallow_untyped_defs=true + check_untyped_defs=true. eprom_operations.py DELIBERATELY EXCLUDED per D-07 (GATE-1.8d read-path ring-fence; deferred to v1.9 post-RCA). Return-type annotations added where strict mode surfaced gaps. Watermark comment at pyproject.toml:115 updated to new floor in Task 2 per D-08 + BLOCKER 4 restructure (Task 1 only adds the override block; Task 2 owns the watermark edit after driving the strict modules to 0).

       Docstrings (D-09): every Click callback in cli_handlers.py has a 1-line docstring matching its existing help= text (snapshot-stable per GATE-1.8b). Public-function docstrings added where missing in the 8 strict-list modules.

       Naming (D-10): verified snake_case conformant; no rename needed.

       Coverage (D-13/D-14/D-15): adds firestarter/avr_tool.py to [tool.coverage.run] omit (subprocess wrapper rationale). Lands 5 test files: test_database_conversion.py (NEW; database.convert_to_programmer + DIP→RURP), test_eprom_operations.py (NEW; HAPPY-PATH ONLY for write/verify/blank/erase via make_comm/fake_serial — read path EXERCISED but NEVER modified per D-07; NO BUG-2 regression test per WARNING 10 — that contract lives in test_bug_characterization.py from Plan 42-01), test_firmware_install.py extension (_get_releases_response_json + _compare_versions PEP 440 branches), test_config.py (NEW; ConfigManager get/set/persist), test_hardware.py (NEW; read-side voltage methods only — set_vpp_voltage / set_vpe_voltage stay UNTESTED per safety boundary). --cov-fail-under flipped 50 → 70 in .github/workflows/ci.yml in the same commit per D-15.

       ERR-01 SC#1 grep contract (BLOCKER 2): grep -rn "except:" firestarter/ returns 0 (no bare except); grep -rn "except Exception" firestarter/ | grep -vE "as e($|[^a-zA-Z_])" returns 0 (every except Exception site binds as e).

       Verification: 8/8 strict-list modules mypy-clean; pytest --cov-fail-under=70 passes; 29 syrupy snapshots green; CLI-04 smoke green; GATE-1.8 (a-e) preserved.`

       Do NOT amend prior commits. Do NOT push.
  </action>
  <verify>
    <automated>cd firestarter_app && grep -c "cov-fail-under=70" .github/workflows/ci.yml && grep -c "cov-fail-under=50" .github/workflows/ci.yml && ruff check . && ruff format --check . && python tools/check_mypy_watermark.py && pytest --cov=firestarter --cov-fail-under=70 -v 2>&1 | tail -10 && firestarter --help 2>&1 | head -3</automated>
  </verify>
  <acceptance_criteria>
    - `cd firestarter_app && grep -c "cov-fail-under=70" .github/workflows/ci.yml` returns at least 1
    - `cd firestarter_app && grep -c "cov-fail-under=50" .github/workflows/ci.yml` returns 0 (the old 50% threshold is gone)
    - `cd firestarter_app && grep -rn "cov-fail-under=50" . --include="*.yml" --include="*.yaml" --include="*.toml" --include="*.cfg" --include="Makefile"` returns 0 lines (no other site carries the old 50% threshold)
    - `cd firestarter_app && ruff check .` exits 0
    - `cd firestarter_app && ruff format --check .` exits 0
    - `cd firestarter_app && python tools/check_mypy_watermark.py` exits 0
    - `cd firestarter_app && mypy firestarter/main.py firestarter/cli_handlers.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py` exits 0 (ALL 8 strict-list modules mypy-clean — ERR-02 closed)
    - `cd firestarter_app && pytest -v` exits 0 with 0 xfails (BUG-2 still PASSED from Plan 42-01; new test files all pass)
    - `cd firestarter_app && pytest --cov=firestarter --cov-fail-under=70` exits 0 (ERR-03 quantitative bar cleared empirically)
    - `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (29 syrupy snapshots green; docstring additions are first-line-stable)
    - `cd firestarter_app && firestarter --help` exits 0 (CLI-04 SC#4 smoke green)
    - **BLOCKER 2 ERR-01 SC#1 grep contract — bare except:** `cd firestarter_app && grep -rn "except:" firestarter/ | wc -l` returns 0 (no bare `except:` sites; closes literal grep contract from ROADMAP SC#1)
    - **BLOCKER 2 ERR-01 SC#1 grep contract — bound exception:** `cd firestarter_app && grep -rn "except Exception" firestarter/ | grep -vE "as e($|[^a-zA-Z_])" | wc -l` returns 0 (every `except Exception` site binds `as e`)
    - `cd firestarter_app && git log -1 --format=%s` contains literal strings `chore(42-03)` AND `ERR-02` AND `ERR-03`
    - `cd firestarter_app && git log -1 --format=%B` contains literal strings `D-06`, `D-07`, `D-09`, `D-13`, `D-14`, `D-15` (full traceability)
    - `cd firestarter_app && git log -1 --format=%B` contains literal string `BLOCKER 2` AND `ERR-01 SC#1` (BLOCKER 2 closure recorded in commit body)
    - `cd firestarter_app && git log -1 --name-only` lists exactly the expected file set: `pyproject.toml`, `.github/workflows/ci.yml`, `firestarter/cli_handlers.py`, plus any of `firestarter/{main,chip_resolver,frame_parser,codec,address_parser,exceptions,serial_comm}.py` modified by Task 2, plus the 5 test files (`tests/test_database_conversion.py`, `tests/test_eprom_operations.py`, `tests/test_firmware_install.py`, `tests/test_config.py`, `tests/test_hardware.py`)
    - `cd firestarter_app && git diff HEAD~1 -- firestarter/eprom_operations.py firestarter/database.py firestarter/firmware.py firestarter/config.py firestarter/hardware.py firestarter/eprom_info.py firestarter/ic_layout.py firestarter/logging_utils.py firestarter/utils.py firestarter/messages.py firestarter/avr_tool.py firestarter/constants.py firestarter/data/chip_database.json firestarter/data/pinouts.json` is empty (all non-strict-list source files unchanged; D-07/D-13 preserved; GATE-1.8c preserved)
    - `cd firestarter_app && git rev-parse --abbrev-ref HEAD` returns `v1.8-app-cleanup`
  </acceptance_criteria>
  <done>
    Single atomic commit on firestarter_app `v1.8-app-cleanup` branch raises mypy strict on the 8 SC-literal modules (ERR-02), adds the missing docstrings + verifies snake_case (ERR-03 textual portion), lifts coverage to ≥70% with avr_tool.py omitted + 5 new/extended test files + ci.yml threshold flipped (ERR-03 quantitative portion), AND closes ERR-01 SC#1 literal grep contract (BLOCKER 2: no bare except, every `except Exception` binds `as e`). All gates green; GATE-1.8 (a–e) preserved; Phase 42 is COMPLETE.
  </done>
</task>

</tasks>

<verification>
- `cd firestarter_app && ruff check . && ruff format --check . && python tools/check_mypy_watermark.py` exits 0
- `cd firestarter_app && mypy firestarter/main.py firestarter/cli_handlers.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py` exits 0 (8/8 strict-list modules clean)
- `cd firestarter_app && pytest -v` exits 0 with 0 xfails
- `cd firestarter_app && pytest --cov=firestarter --cov-fail-under=70` exits 0
- `cd firestarter_app && pytest tests/test_characterization.py -v` exits 0 (29 syrupy snapshots green)
- `cd firestarter_app && pytest tests/test_consistency_check.py -v` exits 0 (3-way verdict preserved from Plan 42-02)
- `cd firestarter_app && pytest tests/test_bug_characterization.py -v` exits 0 (BUG-2 PASSED from Plan 42-01; BUG-1 PASSED from Phase 41)
- `cd firestarter_app && firestarter --help` exits 0
- `cd firestarter_app && grep -c "cov-fail-under=70" .github/workflows/ci.yml` returns at least 1
- `cd firestarter_app && grep -c '"firestarter/avr_tool.py"' pyproject.toml` returns at least 1
- **BLOCKER 2 grep contract:** `cd firestarter_app && grep -rn "except:" firestarter/ | wc -l` returns 0
- **BLOCKER 2 grep contract:** `cd firestarter_app && grep -rn "except Exception" firestarter/ | grep -vE "as e($|[^a-zA-Z_])" | wc -l` returns 0
- `cd firestarter_app && git diff HEAD~1 -- firestarter/eprom_operations.py firestarter/data/chip_database.json firestarter/data/pinouts.json firestarter/constants.py` is empty (no-touch invariants honored)
- All 5 new/extended test files exist and pass
</verification>

<success_criteria>
ERR-02 + ERR-03 + ERR-01 SC#1 grep contract (BLOCKER 2) closed; Phase 42 complete. The 8 SC-literal modules (`main`, `cli_handlers`, `chip_resolver`, `frame_parser`, `codec`, `address_parser`, `exceptions`, `serial_comm`) are mypy strict-clean under `disallow_untyped_defs=true` + `check_untyped_defs=true`; `eprom_operations.py` deliberately deferred to v1.9 per D-07 (GATE-1.8d read-path ring-fence). Every Click callback in `cli_handlers.py` has a 1-line docstring (D-09); naming verified snake_case conformant (D-10). Coverage floor raised from 50% to 70% (D-15) via the mixed strategy of D-13 (`firestarter/avr_tool.py` omit) + D-14 (5 new/extended test files: `test_database_conversion.py`, `test_eprom_operations.py` HAPPY-PATH ONLY per WARNING 10, `test_firmware_install.py` extension, `test_config.py`, `test_hardware.py`). Mypy watermark comment updated in Task 2 (not Task 1) per BLOCKER 4 restructure. ERR-01 SC#1 literal grep contract closed (BLOCKER 2): no bare except, every `except Exception` binds `as e`. All quality gates green; 29 syrupy CLI snapshots preserved; ~30 test_cli_handlers.py exit_code assertions preserved; BUG-2 PASSED; CLI-04 smoke green. GATE-1.8 (a–e) preserved end-to-end.
</success_criteria>

<output>
Create `.planning/phases/42-error-handling-normalization-quality-sweep/42-03-SUMMARY.md` when done.
</output>
</content>
</invoke>
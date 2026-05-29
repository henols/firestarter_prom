# Pitfalls Research — v1.8 Host CLI Structural Cleanup

**Domain:** Refactoring a hardware-facing serial CLI (Python host for Arduino EPROM programmer)
**Researched:** 2026-05-27
**Confidence:** HIGH — based on direct code reading of the actual codebase plus verification against
established Python/Click/pyserial refactoring patterns.

---

## Critical Pitfalls

### Pitfall 1: Wire-Protocol Regression via "Harmless" Serial Module Split

**What goes wrong:**
The `serial_comm.py` split into frame-parser / message-codec / transport modules looks purely structural, but the split seam tends to land in the middle of the binary framing state machine. The critical invariant is: the 4-byte magic preamble detection, the u16 length read, the `frame_len`-byte body read, and the trailing terminator read must all happen in one atomic blocking sequence (`connection.read(2)` then `connection.read(frame_len)` then `connection.read(1)`). If the refactor extracts the "parse" step into a separate module that receives a buffer from a "transport" module, the temptation is to buffer multiple reads before dispatching. This can silently change when `connection.read(N)` is called — if the transport layer now reads in chunks or uses `readinto()` differently, bytes can be consumed from the OS serial buffer at a different moment, leaving the Arduino waiting for an ACK that hasn't been sent yet. The Arduino's UART receive side has a 64-byte hardware buffer; if the host stalls between reads, the firmware fills its transmit buffer and blocks, and the host eventually sees a timeout with no obvious cause.

**Why it happens:**
The current generator `_read_and_parse_lines` mixes three concerns (byte accumulation, preamble detection, frame decoding) in one function. When decomposing, the natural split is "accumulate bytes" (transport) + "decode frames" (parser). But `connection.read(frame_len)` in the middle of the preamble handler is not a "transport" call — it is a protocol-level synchronous read. Splitting it breaks the assumption that all bytes for one frame arrive in a single blocking context.

**How to avoid:**
Write a wire-layer characterization test BEFORE splitting. The test constructs a `BytesIO`-backed fake serial (the existing `conftest.py` `fake_serial` fixture already does this), drives the full message sequence — text line, then binary frame with MAGIC_PREAMBLE, then another text line — through `_read_and_parse_lines`, and asserts exact Response values and order. Pin this test to the existing implementation. During the split, keep the end-to-end path under test and only accept the refactor when the pinned test still passes. Do not change the blocking `connection.read(frame_len)` call site without running the full hardware integration test afterward.

**Warning signs:**
- Any new `connection.read()` call that is not immediately preceded by a preamble check or inside the binary-frame consumption block.
- Buffering at any boundary between the new modules (e.g., a queue, an `asyncio` task, or a thread boundary) — none of these exist today, and introducing one changes the timing contract.
- Test that passes with `BytesIO` but flickers on hardware because the fake serial delivers bytes instantaneously while real UART delivers them with inter-byte gaps.

**Phase to address:**
Phase that owns the serial-module split. Must begin by pinning the existing `test_decoder.py` suite as a non-regression gate, then extend it to cover the preamble→body→terminator sequence before any restructure. The split should land in a single commit with zero changes to `connection.read` call sites.

---

### Pitfall 2: argparse→Click Behavioral Drift on Exit Codes

**What goes wrong:**
argparse calls `sys.exit(2)` for parse errors (wrong argument, missing required arg, unrecognized argument). Click calls `sys.exit(2)` for `UsageError` but `sys.exit(1)` for `ClickException` subclasses and `sys.exit(0)` for `--help`. The current `main()` explicitly returns `0` or `1` and the entry point calls `sys.exit(main())`. In Click, commands do not return integers — they raise `SystemExit` or return `None`. If the Click migration naively adds `return 1` at the end of a command callback, Click ignores it; the process exits 0 regardless. Any shell script or CI pipeline that checks `$?` after `firestarter read W27C512` will see unexpected exit codes.

**Why it happens:**
Click's invocation model is different: `@cli.command()` callbacks return `None`; to exit non-zero you call `sys.exit(N)` or raise `click.ClickException`. The argparse pattern of `return 0 if success else 1` is invisible to Click's runner. This is the most common mistake when migrating Python CLIs to Click.

**How to avoid:**
Before migrating any command, write a characterization test that invokes `main()` via `subprocess.run(["firestarter", ...])` or Click's `CliRunner` and asserts `result.exit_code`. Pin: (a) successful operations exit 0, (b) "EPROM not found in database" exits 1, (c) missing required argument exits 2, (d) `--help` exits 0. During the migration, each command's exit code must be explicitly verified. In Click, use `sys.exit(1)` or `raise click.ClickException(message)` (which prints to stderr and exits 1) for error cases. Do not rely on `return` value for exit code.

**Warning signs:**
- Click command callbacks with `return 0` or `return 1` statements — these are no-ops.
- `result.exit_code == 0` in CliRunner tests even though the operation failed.
- Shell-level test: `firestarter read NONEXISTENT_CHIP; echo $?` printing `0` instead of `1`.

**Phase to address:**
CLI characterization test phase (tests-first). Before touching `main.py`, capture exit codes for every command in a test suite using Click's `CliRunner`. The migration phase uses these tests as the gate.

---

### Pitfall 3: argparse→Click Behavioral Drift on Argument-Parsing Edge Cases

**What goes wrong:**
argparse and Click differ in several parsing behaviors that are not obvious:

1. **Prefix matching**: argparse allows abbreviated long options by default (`--forc` matches `--force`). Click does not. Any user or script that relied on prefix matching breaks silently — the argument is treated as unrecognized.
2. **`nargs="?"` (optional positional)**: argparse `nargs="?"` with `default=None` and `const=<something>` has specific semantics when the argument is absent vs. present without a value. Click's `argument(..., required=False)` behaves differently. The `read` command's `output_file` uses `nargs="?"` — if the Click equivalent is `@click.argument("output_file", required=False, default=None)`, test the case where `output_file` is omitted and where it is explicitly provided.
3. **`store_false` with `dest`**: The `--no-blank-check` flag uses `action="store_false", dest="blank_check", default=True`. Click's equivalent is `@click.option("--no-blank-check", "blank_check", is_flag=True, flag_value=False, default=True)`. Getting the polarity wrong silently inverts the behavior — blank check runs when user says `--no-blank-check`.
4. **Mutually exclusive groups**: argparse `add_mutually_exclusive_group()` is used for `--pre/--firmware-version/--stable` and `--install/--list`. Click requires manual `callback`-based mutex or the `cloup` library. Forgetting to enforce the mutex means users can pass `--pre` and `--firmware-version` together; the resolution logic picks one silently, which is a behavioral change.
5. **Type coercion**: `_validate_firmware_version` is wired as an argparse `type=` function and raises `ArgumentTypeError` on bad input. The Click equivalent is `callback=` or a custom `ParamType`. If the validator is not wired, Click accepts any string.

**Why it happens:**
argparse and Click have different design philosophies. Developers migrating commands one-by-one often test the happy path but miss edge cases that users rely on. The current `main.py` has 14 branches of dispatch — each one can have a different subtlety.

**How to avoid:**
Characterize the current argument-parsing behavior with explicit tests before migrating. For each flag with non-trivial semantics (store_false, nargs="?", mutually-exclusive, type=validator), write a test using `CliRunner` that exercises the edge case against the argparse implementation, then re-run the same test against the Click implementation. The mutex groups are highest risk — test that `firestarter fw --pre --firmware-version 3.0.0` exits with a usage error (exit 2) both before and after migration.

**Warning signs:**
- `--no-blank-check` not appearing in Click's `--help` output for `write`.
- `firestarter fw --pre --firmware-version 3.0.0` succeeding instead of erroring.
- `firestarter read W27C512` (no output_file) writing to the wrong default name.

**Phase to address:**
CLI characterization test phase (before migration). The test suite must cover all non-trivial flag semantics. The Click migration phase must not close until every characterization test passes.

---

### Pitfall 4: Buffer-Size Constant Drift Between Board-Specific Code Paths

**What goes wrong:**
`constants.py` defines `BUFFER_SIZE = 512` and `LEONARDO_BUFFER_SIZE = 1024`. These are used in `eprom_operations.py` to size the chunk sent per `send_ack` cycle. During the serial-module split, if the buffer-size constant usage migrates to a new module without a clear import, a developer may introduce a hardcoded `512` or re-derive the buffer size from serial state. The consequence is that reads/writes against a Leonardo board send 512-byte chunks when 1024 are available (slower, but correct) or worse, send 1024-byte chunks to an Uno which silently truncates at the hardware buffer, causing checksum mismatches that look like hardware failures.

**Why it happens:**
`BUFFER_SIZE` and `LEONARDO_BUFFER_SIZE` are easy to copy-paste or re-derive "from context." The board selection logic is currently in `eprom_operations.py` and the constants import is `from firestarter.constants import *`, which makes the origin invisible. After the split, if the constants module is reorganized, an accidental `BUFFER_SIZE = 512` local variable anywhere in the call stack shadows the constant silently.

**How to avoid:**
During the constants consolidation phase, make `BUFFER_SIZE` and `LEONARDO_BUFFER_SIZE` importable by name only (no star-import in the serial/ops modules after the refactor). Add a constants-parity test that asserts the values have not drifted. Never hardcode `512` or `1024` in the ops or serial layer — always reference the named constant. After the refactor, grep for `512` and `1024` as bare integers in the module tree and fail the PR if found in a serial/ops context.

**Warning signs:**
- Any `512` or `1024` bare integer literal in `eprom_operations.py` or its successor modules.
- A Leonardo board completing a read 2× slower after the refactor (chunk size regressed to 512).
- Checksum mismatch errors that only appear on Uno, not Leonardo (chunk too large).

**Phase to address:**
Constants consolidation phase. The parity test must be written before any constants are moved.

---

### Pitfall 5: Serial Timeout Semantics Change During Generator Refactor

**What goes wrong:**
The `_read_and_parse_lines` generator resets `start_time = time.time()` every time it yields a response (line 601 and 654 in the current code). This "sliding window" timeout means: if the firmware is still sending responses, the timeout window keeps extending. A refactor that extracts the timeout logic or changes when `start_time` is reset can turn a sliding-window timeout into a fixed-deadline timeout. The consequence: multi-response commands (the FW probe sends two `expect_ack` calls in sequence) start timing out on slow ports even though firmware is responding correctly.

**Why it happens:**
The sliding-window semantics are not documented as an invariant — they look like an implementation detail that could be cleaned up. Anyone reading the code without running the hardware may not recognize that the reset is load-bearing for commands that produce multiple response frames.

**How to avoid:**
Add a comment at the `start_time = time.time()` reset site labeling it "INVARIANT: sliding-window timeout — must reset on every yield." Write a unit test using the fake serial fixture that drives a sequence of 3 responses with 0.3-second delays between them and asserts that a 0.5-second timeout does not fire before all 3 are received (which would fail with a fixed-deadline timeout but pass with a sliding-window timeout). This test must exist before the generator is refactored.

**Warning signs:**
- `SerialTimeoutError` appearing in the FW probe sequence on slow boards after the refactor.
- `consume_remaining_input` consuming fewer frames than before.
- Any change to `start_time` initialization or reset that is not accompanied by the unit test above.

**Phase to address:**
Serial characterization test phase. The invariant test must be green before the serial split.

---

### Pitfall 6: Characterization Tests Pinning Existing Bugs as Correct Behavior

**What goes wrong:**
The current `main.py` has several behaviors that are bugs, not features:
- `build_arg_flags` uses `if "force" in args` which tests for attribute existence on the Namespace, not truthiness — this always evaluates True if argparse set the attribute, meaning `force` is always detected even when `False`. The resulting flag bits may be wrong for some commands.
- The `dev consistency-check` command is the only command that returns an int directly (0/1/2 for PASS/FAIL/error) while all other commands use the `1 if not ... else 0` bool pattern. A characterization test that pins `exit_code == 1` for a consistency-check FAIL is pinning correct behavior; but a test that pins the current `build_arg_flags` evaluation would pin a bug.
- The `argcomplete` integration in `EpromCompleter` calls `allowed_eproms()` which instantiates `EpromDatabase()` twice (once in `__init__`, once in `allowed_eproms()`). This is wasteful but not incorrect.

**Why it happens:**
Characterization tests capture existing behavior by definition. Without explicitly auditing which behaviors are intentional and which are bugs, tests will pin bugs. The v1.8 scope explicitly permits "fix bugs found" — but only if they are documented. An undocumented bug fix in the characterization test phase creates invisible behavior drift.

**How to avoid:**
Before writing any characterization test, audit the target behavior with a "bug or feature?" label. Mark tests that pin known-wrong behavior with `# BUG: <description> — do NOT preserve this behavior` and a corresponding FIXME comment. The migration phase then intentionally changes those tests to the correct behavior and documents the change in the commit. The constant parity tests (`test_revision_constants_parity.py`) are a good model: they pin intentional invariants, not accidental behaviors.

**Warning signs:**
- Characterization tests that pass before AND after the migration but should have changed.
- Tests that accept both `force=True` and `force=False` as the same flag value.
- No "CHANGED BEHAVIOR" entry in the commit log for a command whose characterization test was updated.

**Phase to address:**
Tests-first phase. Every characterization test that captures potentially-buggy behavior must carry a labeled comment. The "fix bugs found" gate is enforced at the roadmap level, not by individual test authors.

---

### Pitfall 7: Over-Mocking That Tests the Mock, Not the Code

**What goes wrong:**
The untested core paths (CLI dispatch, EPROM ops, DB lookup) require mocking `serial.Serial` and `SerialCommunicator.find_and_connect`. The failure mode is tests like:
```python
mock_comm.expect_ack.return_value = (True, "OK")
result = operator.read_eprom(...)
assert mock_comm.expect_ack.called
```
This test passes regardless of whether `read_eprom` actually processes the response correctly, constructs the right JSON command, or handles errors. It tests that `expect_ack` was called, not that the operation succeeded or failed correctly.

**Why it happens:**
When hardware is absent, mocking is the only option. But the natural tendency is to mock at the highest level (mock `find_and_connect` to return a mock communicator), which removes all the real protocol logic from the test.

**How to avoid:**
Mock at the `serial.Serial` boundary, not the `SerialCommunicator` boundary. The existing `conftest.py` `fake_serial` fixture using `BytesIO` is the right pattern — it drives real `SerialCommunicator` logic with fake bytes. Extend this pattern to the EPROM ops layer: construct fake serial responses for a read sequence (INIT ack → MAIN acks with DATA chunks → END ack) and drive real `eprom_operator.read_eprom()` with them. The test then asserts on the output bytes and final return value, not on which methods were called. Reserve `MagicMock` for the serial port object itself.

**Warning signs:**
- Test files with more `mock.assert_called_once_with(...)` than `assert result == expected` lines.
- Tests that pass when the implementation function body is replaced with `pass`.
- Test coverage showing 100% line coverage but 0% branch coverage on the JSON command construction logic.

**Phase to address:**
Tests-first phase. The test design review must verify that core-path tests drive real code with fake serial bytes, not fake code.

---

### Pitfall 8: mypy Avalanche — Getting Buried in Type Errors and Abandoning the Gate

**What goes wrong:**
Running `mypy` on the current codebase for the first time against a legacy `from firestarter.constants import *` star-import, untyped `dict` return values from `db_instance.get_eprom()`, `Optional[dict]` function signatures that are actually `dict | None | False`, and `namedtuple` fields without type parameters will produce 80-200+ errors. Teams commonly react by adding `# type: ignore` to every file, setting `ignore_errors = true` in `mypy.ini`, or abandoning strict mode entirely. The gate becomes theater.

**Why it happens:**
Adding mypy to an existing codebase is harder than starting with it. The star-import alone makes mypy unable to resolve names. The `from firestarter.constants import *` pattern in `serial_comm.py`, `eprom_operations.py`, and `main.py` means mypy cannot know which names are in scope without analyzing the constants module.

**How to avoid:**
Use `mypy --ignore-missing-imports --no-strict-optional` as the initial gate, not `--strict`. Set `warn_unused_ignores = true` so `# type: ignore` comments are tracked. Enable one mypy flag at a time per phase rather than all at once. The specific first target: replace `from firestarter.constants import *` with explicit named imports everywhere (this is also required for the flat-layout refactor). This single change makes mypy's scope analysis tractable. Accept that 100% clean mypy is a multi-phase goal; the gate for v1.8 should be "no new `Any` in the refactored modules" not "zero errors across all files."

**Warning signs:**
- `mypy.ini` or `pyproject.toml` containing `ignore_errors = true` or `disallow_untyped_defs = false` after the tooling phase.
- More than 5 `# type: ignore` comments in any single refactored module.
- The CI mypy step showing 0 errors but the module having no type annotations (meaning mypy is not checking the file at all).

**Phase to address:**
Tooling setup phase. Add mypy with minimal flags first, document the initial error count, and set a target of "no regressions" rather than "zero errors" as the phase gate. The explicit-import refactor (replacing star-imports) should be the first structural change — it improves mypy tractability and documents the constants dependency explicitly.

---

### Pitfall 9: firmware-header Contract Drift During Constants Consolidation

**What goes wrong:**
`constants.py` has three separate firmware-contract blocks that must stay byte-identical to C headers in the firmware sub-repo:
1. Command codes and flag bits → `firestarter/include/firestarter.h`
2. CTRL_* control-register bits → `firestarter/include/rurp_pinout.h`
3. REVISION_* hardware revision bytes → `firestarter/include/rurp_shield.h`

The v1.8 constants consolidation phase will touch this file. Any rename, reorder, or value change — even from a linter auto-fix ("rename `FLAG_FORCE = 0x01` to `FLAG_FORCE: Final[int] = 0x01`") — is safe. But a merge conflict resolution or a copy-paste of the block into a new module with a different value is catastrophic: the firmware sends `REVISION_2_0 = 0x02` and the host maps it to a different string, causing silent misidentification of shield hardware.

**Why it happens:**
The existing parity test (`test_revision_constants_parity.py`) covers only the REVISION_* block. The command codes and flag bits have no parity test. During constants consolidation, a developer may update the REVISION parity test but miss that the same test pattern is needed for FLAG_* and COMMAND_* values. Ruff's auto-fix may reorder dict literals or rename variables, and the linter will pass because Python values are unchanged — but a human review of the diff can miss that a constant was reordered and both ruff and mypy are satisfied while the contract is broken.

**How to avoid:**
Before the constants consolidation phase, extend the parity test to cover all three blocks: COMMAND_*, FLAG_*, CTRL_*, and REVISION_*. Each constant in `constants.py` that mirrors a firmware header value must have an explicit `assert CONSTANT_NAME == <hex_literal>` in the parity test. The hex literal must be hand-typed from the firmware header, not derived from the Python constant. This makes the test fail if the constant is changed on either side. Lock ruff's auto-fix to not reorder or rename constants in the firmware-contract section (use `# ruff: noqa` on the block header if necessary).

**Warning signs:**
- A parity test that only covers REVISION_* (the current state — command codes and flags are untested).
- Any `ruff --fix` run that touches the constants file without a parity-test check afterward.
- A merge conflict resolution in `constants.py` that does not trigger a re-run of the parity test.

**Phase to address:**
Constants consolidation phase, but the parity test extension must come first as its own committed unit, before any constants are moved.

---

### Pitfall 10: Entry-Point and Packaging Breakage During Module Moves

**What goes wrong:**
`pyproject.toml` declares `firestarter = "firestarter.main:main"` as the entry point. The flat layout decision (`packages = ["firestarter"]`) means all modules stay in the `firestarter/` package directory. However, during the `main.py` decomposition, a developer may create a new module at `firestarter/cli.py` and move the `main()` function there — then forget to update `pyproject.toml`. The installed `firestarter` command silently calls the old `main.py:main` which is now a stub or import-error. The error only manifests in an installed (`pip install -e .`) environment, not when running `python -m firestarter.main` directly.

**Why it happens:**
`pyproject.toml` is not automatically updated by refactoring tools. The entry point is tested by running `firestarter --help` after `pip install -e .`, but this step is often omitted in CI because `pip install -e .` is assumed to be stable.

**How to avoid:**
If `main()` moves, update `pyproject.toml` in the same commit. Add a CI step that runs `pip install -e . && firestarter --help` as a smoke test. The Click migration makes this more critical because Click's `@cli` entry point must be the function invoked by the script entry. If Click's group is named `cli` and the entry point still says `main`, the CLI will fail to initialize.

Additionally, `pyproject.toml` currently includes `argcomplete>=3.6.2` as a runtime dependency. After the Click migration, argcomplete is no longer needed (Click has its own shell completion). Leaving it in as an unused dependency is harmless but should be cleaned up to avoid confusing future contributors.

**Warning signs:**
- `firestarter --help` output changing unexpectedly after a module rename.
- ImportError on `from firestarter.main import main` after main is moved.
- argcomplete still in `requirements` after the Click migration.

**Phase to address:**
Click migration phase. The entry-point update and smoke test must be in the same commit as the main() migration.

---

### Pitfall 11: "Fix Bugs Found" Gate Accidentally Expanding Scope

**What goes wrong:**
The v1.8 scope permits "fix bugs found" but the host read path (the actual read-bug from Bug A/Bug B) is explicitly deferred to v1.9. During the serial-module split and EPROM-ops refactor, developers will read `read_data_block()` and `read_eprom()` carefully. It is tempting to also fix the read-path timing issues — the code will be in front of the developer, the tests will be scaffolded, and the fix may look small. But any change to the read path that is NOT a structural-only refactor risks perturbing the Bug A/Bug B substrate that v1.9 depends on. The v1.9 RCA uses 15 N=5 W27C512 binaries as its baseline; a v1.8 change to the read timing could make the v1.9 baseline invalid.

**Why it happens:**
The "while I'm in here" effect. The scope boundary between "structural refactor of read path" and "behavioral fix of read path" is blurry when the code is open in an editor.

**How to avoid:**
Establish a hard rule at the start of the serial-split phase: any change to `read_data_block()` that is not whitespace/rename/import-only requires a separate commit with "INTENTIONAL BEHAVIOR CHANGE: <description>" in the commit message and a corresponding entry in the v1.8 milestone document. The CI gate should not catch this (it's not a lint violation), but the phase VERIFICATION step must explicitly confirm that the read path is structurally-only. The v1.9 RCA team reviews the v1.8 commit log for any read-path changes before starting.

**Warning signs:**
- A commit touching `read_data_block()` or `read_eprom()` without "REFACTOR ONLY" or "INTENTIONAL BEHAVIOR CHANGE" in the commit message.
- The `read_data_block()` timeout value changing from the current implicit pyserial timeout behavior.
- Any change to the `while bytes_to_read > 0:` loop's retry logic.

**Phase to address:**
Serial-module split phase. The boundary is enforced by commit-message convention and phase VERIFICATION checklist.

---

### Pitfall 12: Over-Abstraction and Unnecessary Layer Introduction

**What goes wrong:**
The refactor creates a natural temptation to introduce abstract base classes, protocol interfaces, or dependency injection containers. For example: a `SerialTransport` ABC with `read(n)` and `write(data)` methods, a `FrameParser` protocol, a `ChipResolver` service class injected into `EpromOperator`. None of these exist today. Each new layer adds indirection that:
- Breaks git blame for the lines that actually do the work
- Adds import weight that makes the module graph harder to read
- Creates future "which layer owns this?" confusion
- Makes the codebase harder for a single-developer project to maintain

The flat-layout decision is already a correct instinct against subpackage reorg. The same instinct should apply to class hierarchy.

**Why it happens:**
Developers following "clean architecture" or "SOLID" principles for refactoring naturally reach for interfaces and dependency injection. These patterns are valuable in large teams; they are overhead in a single-developer hardware tool.

**How to avoid:**
The rule is: introduce a new class only if it replaces copy-paste that already exists (the 9x chip-lookup boilerplate in `main.py` is a valid candidate for a `resolve_chip` function — but not a `ChipResolver` class). Introduce a new module only if the existing file exceeds 300 lines after the split. Do not introduce ABCs or Protocols for existing concrete classes. The test for "is this layer necessary?" is: can the same test coverage be achieved without the new layer? If yes, skip the layer.

**Warning signs:**
- Any new file named `*_interface.py`, `*_protocol.py`, `*_base.py`, or `*_factory.py`.
- Any new `ABC` or `Protocol` class that has only one concrete implementation.
- A `ChipResolver`, `SerialTransport`, or `FrameDecoder` class that wraps a function that already worked fine.

**Phase to address:**
All refactor phases. The code review gate for each phase should explicitly check: "did this phase introduce any new indirection layers that are not justified by eliminating existing copy-paste?"

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| `from firestarter.constants import *` in all modules | No explicit import list to maintain | mypy cannot resolve names; any constant can silently shadow a local; constants-drift is invisible | Never — replace with explicit named imports in v1.8 |
| `# type: ignore` on legacy return types | Suppresses mypy error instantly | Accumulates; future type-correct code still gets ignored; masks real errors | Only when annotating a third-party stub is the only alternative |
| Mocking `SerialCommunicator` at class level in tests | Fast test setup | Tests the mock contract, not the protocol logic; does not catch framing regressions | Only for tests of the CLI dispatch layer that explicitly don't care about serial |
| Hardcoding `default="uno"` in Click options | Simple to write | Board list must be updated in two places (option choices + fw manager logic) | Acceptable until a fourth board is added |
| Leaving `argcomplete` in dependencies post-migration | No pip change required | Dead dependency misleads future contributors; adds install weight | Never — remove it in the same PR as the Click migration |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `pyserial` + `BytesIO` in tests | `BytesIO` does not implement `in_waiting` property — accessing it raises `AttributeError` | Mock `in_waiting` explicitly; the existing `conftest.py` `fake_serial` fixture already wraps this correctly — follow its pattern |
| Click's `CliRunner` | `CliRunner.invoke()` catches `SystemExit` and stores the exit code in `result.exit_code` — `sys.exit(1)` inside a command becomes `result.exit_code == 1`, not an exception | Use `CliRunner(mix_stderr=False)` and check `result.exit_code` not `result.exception` for expected failure cases |
| Click shell completion vs argcomplete | Click's `shell_completion` mechanism is incompatible with argcomplete's `BASH_COMPLETIONS` env var | Remove argcomplete dependency and `argcomplete.autocomplete(parser, ...)` call; replace with `firestarter --install-completion` via `click_completion` or the built-in Click completion |
| Firmware version check in `_probe_port` | The version check uses a regex on the text-format `FW:` response — if a future firmware emits the version via an ID-frame instead, the regex match silently fails and FirmwareOutdatedError is raised for a valid firmware | The version check path is in the `serial_comm` module; if the module is split, ensure the regex pattern is co-located with the text-path parser, not the ID-frame decoder |
| `ConfigManager` singleton + `EpromDatabase` singleton | Both are singletons initialized in `main()` after argument parsing; in Click's model, the singletons must be initialized inside the `@click.pass_context` callback, not at import time | Use `@click.pass_context` or a `@click.pass_obj` group context to carry initialized singletons; do not use module-level globals |

---

## "Looks Done But Isn't" Checklist

- [ ] **Wire protocol non-regression:** `firestarter read W27C512 /tmp/test.bin` on real hardware produces a byte-identical binary before and after refactor. Structural-only changes must pass this gate before closing the serial-split phase.
- [ ] **Exit codes verified:** `CliRunner` tests confirm exit code 1 for "chip not found", exit code 2 for bad arguments, exit code 0 for successful operations — tested against Click implementation, not just argparse.
- [ ] **Firmware contract parity:** `pytest tests/test_revision_constants_parity.py` plus new tests for COMMAND_* and FLAG_* all pass. The tests assert hex literals, not Python constants.
- [ ] **Entry point smoke test:** `pip install -e . && firestarter --help` runs successfully and shows the Click-generated help text after migration.
- [ ] **Buffer size constants not hardcoded:** `grep -r '\b512\b\|\b1024\b' firestarter/` in a serial/ops context returns no results (only in `constants.py`).
- [ ] **Star imports eliminated:** `grep -r 'import \*' firestarter/` returns no results after the explicit-import phase.
- [ ] **mypy gate not bypassed:** `pyproject.toml` contains no `ignore_errors`, `disallow_untyped_defs = false`, or `exclude` entries added during v1.8 without justification.
- [ ] **No new ABCs or Protocols without copy-paste justification:** `grep -r 'ABC\|Protocol' firestarter/` reviewed and each instance justified.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wire-protocol regression discovered post-merge | HIGH | Revert the serial-split commit; re-run characterization tests against the revert to confirm baseline; re-implement split with `connection.read` call sites preserved |
| Exit code drift discovered after Click migration | MEDIUM | Add `sys.exit(1)` to affected command callbacks; re-run CliRunner tests; no re-architecture needed |
| Firmware constant value changed in consolidation | HIGH | Git diff `constants.py` vs firmware header; restore incorrect values; re-run parity tests; if firmware has already been updated with the wrong constant, the firmware sub-repo needs a patch too |
| mypy gate abandoned mid-milestone | MEDIUM | Reset to the last state where the gate was clean; re-enable one flag at a time; do not attempt to fix all errors in one commit |
| Entry point breakage in production install | LOW | Update `pyproject.toml` entry point; `pip install -e .`; smoke test; the fix is a one-line change |
| Over-mocked tests that miss a real regression | HIGH | Cannot recover retroactively; the missed regression ships. Prevention is the only strategy — the test design review must catch this before tests are merged |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Wire-protocol regression (Pitfall 1) | Serial characterization test phase (before split) | `test_decoder.py` extended to cover preamble→body→terminator sequence; passes on fake serial and on hardware |
| Exit code drift (Pitfall 2) | CLI characterization test phase (before migration) | `CliRunner` tests assert exit codes for all 14 command branches |
| Argument-parsing edge cases (Pitfall 3) | CLI characterization test phase | Tests cover store_false, nargs="?", mutually-exclusive, type=validator for each affected command |
| Buffer-size constant drift (Pitfall 4) | Constants consolidation phase | `grep -r '\b512\b\|\b1024\b' firestarter/` clean outside `constants.py` |
| Sliding-window timeout regression (Pitfall 5) | Serial characterization test phase | Unit test drives 3 delayed responses against a 0.5s timeout and asserts all 3 are received |
| Characterization tests pinning bugs (Pitfall 6) | Tests-first phase (audit step) | Every test that pins potentially-buggy behavior carries a "BUG or FEATURE?" comment |
| Over-mocking (Pitfall 7) | Tests-first phase (test design review) | Core-path tests use `BytesIO`-backed fake serial, not `MagicMock(SerialCommunicator)` |
| mypy avalanche (Pitfall 8) | Tooling setup phase | `pyproject.toml` mypy config documented; initial error count recorded; gate is "no regressions" |
| Firmware contract drift (Pitfall 9) | Constants consolidation phase | Parity test extended to cover all three firmware-contract blocks with hex literals |
| Entry-point breakage (Pitfall 10) | Click migration phase | CI smoke test `pip install -e . && firestarter --help` added |
| Scope expansion into read path (Pitfall 11) | Serial-split phase VERIFICATION | Phase VERIFICATION checklist explicitly confirms read path is structural-only; commit log reviewed |
| Over-abstraction (Pitfall 12) | All refactor phases (code review gate) | No new ABCs, Protocols, or layers without copy-paste justification |

---

## Sources

- Direct code reading: `firestarter_app/firestarter/serial_comm.py` (1037 lines, current HEAD)
- Direct code reading: `firestarter_app/firestarter/main.py` (14-branch dispatcher, 510+ lines)
- Direct code reading: `firestarter_app/firestarter/constants.py` (firmware-contract blocks)
- Direct code reading: `firestarter_app/tests/test_revision_constants_parity.py` (existing parity gate model)
- Direct code reading: `firestarter_app/tests/test_decoder.py` and `conftest.py` (BytesIO-based fake serial pattern)
- Direct code reading: `firestarter_app/pyproject.toml` (entry point, dependency list)
- Project context: `.planning/PROJECT.md` (v1.8 scope decisions, GATE-1.8, v1.9 RCA seed)
- Click documentation: exit code semantics differ from argparse (HIGH confidence — well-documented Click behavior)
- pyserial documentation: `in_waiting` not implemented by `BytesIO` (HIGH confidence — known limitation)

---
*Pitfalls research for: Python serial hardware CLI refactoring (firestarter_app v1.8)*
*Researched: 2026-05-27*

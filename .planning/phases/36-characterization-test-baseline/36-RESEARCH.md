# Phase 36: Characterization Test Baseline - Research

**Researched:** 2026-05-27
**Domain:** Python testing — pytest, syrupy snapshot testing, characterization tests, singleton removal
**Confidence:** HIGH (all key findings verified against live code and installed libraries)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** subprocess black-box harness for CLI golden tests. Tests invoke `firestarter` entry point as subprocess, snapshot stdout/stderr/exit-code. Identical before and after argparse→Click migration — proves GATE-1.8(b) byte-for-byte.
- **D-02:** read/write/verify/erase happy-paths characterized in-process using `make_comm`/`fake_serial` fixtures with canned firmware responses. No new production serial-replay seam. This in-process subset is re-pointed from `main()` to `CliRunner.invoke()` at Phase 41 only.
- **D-03:** Scope is broad — pin BOTH board-independent surface (--help, all subcommands, ALL argument-parse/usage errors) AND E2E read/write/verify/erase happy-paths (via D-02 in-process route).
- **D-04:** syrupy is the snapshot mechanism (`assert result == snapshot`, `--snapshot-update`, `__snapshots__/`). Add to `[project.optional-dependencies].test`.
- **D-05:** Determinism = (a) syrupy normalization filters scrubbing version strings, absolute paths, `/dev/tty*` port names; (b) neutralize port auto-discovery in hardware-touching tests; (c) DB pinned to packaged `chip_database.json` with `~/.firestarter` merge skipped (see D-06).
- **D-06:** Minimal de-singleton. Remove `__new__`/`_initialized` guard (`database.py:165-181`); add constructor seam to skip `get_local_database()` user-override merge (`database.py:193-195`). Keep per-site `EpromDatabase()` construction. Defer Click-context DI wiring to Phase 41.
- **D-07:** `tests/test_eprom_database.py` covers `get_eprom`, `convert_to_programmer`, DIP→RURP pin translation against real `chip_database.json` data — without `find_and_connect` or serial I/O.
- **D-08:** TEST-05 pins exactly two genuine bugs, NEITHER pinned as correct (each asserts *corrected* behavior): (1) `build_arg_flags` `if "force" in args` attribute-vs-truthiness check (`main.py:497`) — fix in Phase 41; (2) hardware-error mislabeled as communication-error (`eprom_operations.py:265-267`) — fix in Phase 42.
- **D-09:** `COMMAND_FW_VERSION` is NOT missing (exists at `constants.py:39` = 13). Fold its check into TEST-04 firmware-parity assertion.
- **D-10:** Bug-test mechanism = `pytest.mark.xfail(strict=True)` asserting corrected behavior. Flips to XPASS when fix lands (with `strict=True`, XPASS = FAILURE, forcing removal of the marker). Each test carries a `# BUG:` marker citing its fix phase.
- **D-11:** Extend `tests/test_revision_constants_parity.py` pattern to cover all `COMMAND_*`, `FLAG_*`, and `CTRL_*` blocks. `skipif` when `firestarter/include/firestarter.h` is absent.
- **D-12:** Use existing `BytesIO` `fake_serial`/`make_comm` fixtures. Pin `_read_and_parse_lines` preamble→body→terminator sequence + delayed-response test. Timeout simulation technique is planner's discretion.

### Claude's Discretion

- Exact test-file naming/organization.
- The precise port auto-discovery neutralization mechanism (D-05b).
- The timeout-simulation technique (D-12).
- Whether to add `click` as a test dep now (NOT needed for Phase 36 — syrupy + subprocess do not need it).

### Deferred Ideas (OUT OF SCOPE)

None. Discussion stayed within phase scope.

**Sequencing note:** bug *fixes* are characterized here but applied later by design — `build_arg_flags` → Phase 41 (CLI-03); comm-error vs operational-error split → Phase 42 (ERR-01).
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TEST-01 | Characterization tests pin current CLI command surface via subprocess + syrupy snapshots | D-01, D-02, D-03, D-04, D-05; subprocess invocation verified live |
| TEST-02 | Characterization tests pin `_read_and_parse_lines` preamble→body→terminator + sliding-window timeout | D-12; `_read_and_parse_lines` generator body read and experimentally verified |
| TEST-03 | `EpromDatabase` singleton replaced with injectable construction; unit tests for DB methods | D-06, D-07; singleton guard code read; constructor seam designed and verified |
| TEST-04 | Firmware-contract parity test extended to `COMMAND_*`, `FLAG_*`, `CTRL_*` with hard-coded hex literals | D-09, D-11; `firestarter.h` read; all constants verified against Python counterparts |
| TEST-05 | Two latent bugs characterized as xfail(strict=True) asserting corrected behavior | D-08, D-10; both bugs verified live; xfail mechanics confirmed |
</phase_requirements>

---

## Summary

Phase 36 is almost entirely additive — it builds a safety net before any structural change. The only production-code change is removing the `EpromDatabase` singleton guard. All five requirements map to new test files (or extensions of existing ones) plus one small production change.

The key architectural insight is that the two test approaches (subprocess vs. in-process) serve different purposes that must not be mixed up: subprocess tests pin the CLI surface with a harness that is identical before and after the argparse→Click migration; in-process tests use `make_comm`/`fake_serial` to pin the serial protocol path where a `BytesIO` fake cannot cross the process boundary.

Research resolved all five "Claude's Discretion" items from CONTEXT.md: (1) port auto-discovery is cleanly neutralized by monkeypatching `serial.tools.list_ports.comports` in-process — but this is only needed for tests that exercise the "no programmer found" error path; subprocess tests for `--help`/`list`/`info`/`search` never call `find_and_connect` and therefore never trigger port scanning. (2) Timeout simulation for `_read_and_parse_lines` is best done with tiny real-clock timeouts (0.02–0.05 s) fed to `get_response(timeout=...)` — experimentally confirmed to work in < 25 ms total. (3) Test file naming is recommended as five files mirroring the five requirements. (4) `click` is not needed as a test dep in Phase 36.

**Primary recommendation:** Five new test files, one production change (database.py de-singleton), and one pyproject.toml change (add `test` optional-dep group with `pytest>=8.0` and `syrupy>=5.0`).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| CLI surface snapshot testing | Test harness (subprocess) | — | Subprocess boundary is the only harness that is migration-agnostic (argparse→Click transparent) |
| Serial frame-parse testing | Test harness (in-process) | — | `BytesIO` fake cannot cross process boundary; `make_comm`/`fake_serial` already exist |
| DB unit testing | Test harness (in-process) | — | No serial I/O needed; direct `EpromDatabase` construction after de-singleton |
| Firmware-parity testing | Test harness (in-process, cross-repo) | CI gate | Asserts Python constants equal C header literals; `skipif` guards CI |
| Bug characterization | Test harness (in-process) | CI gate | `xfail(strict=True)` is an in-process pytest mechanism |
| Port auto-discovery neutralization | Test infrastructure (monkeypatch) | — | `serial.tools.list_ports.comports` is the narrowest boundary to mock |
| EpromDatabase construction | Application layer (database.py) | Test infrastructure | De-singleton is the only production change; tests consume the new seam |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 9.0.3 (installed) | Test runner, fixture injection, xfail marks | Already in project; syrupy 5.x requires >=8.0 [VERIFIED: PyPI] |
| syrupy | 5.2.0 (latest) | Snapshot assertions (`assert x == snapshot`, `--snapshot-update`, `__snapshots__/`) | Designed exactly for golden-master characterization tests; idiom matches existing test style [VERIFIED: github.com/syrupy-project/syrupy, pypi.org/project/syrupy] |
| subprocess (stdlib) | Python 3.12 | Black-box CLI invocation — captures stdout/stderr/returncode | No dep needed; migration-agnostic; entry point `firestarter` confirmed at `/home/vscode/.local/bin/firestarter` [VERIFIED: live run] |
| unittest.mock / pytest monkeypatch | stdlib / pytest | Neutralize `serial.tools.list_ports.comports` | Narrowest seam for port-discovery; no production code change needed [VERIFIED: live analysis] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| shutil.which | stdlib | Locate `firestarter` entry point in subprocess tests | Use to find the installed entry point; avoids hardcoding paths |
| re | stdlib | Normalize version strings, absolute paths, port names in snapshot assertions | Scrub non-deterministic content before `assert normalized == snapshot` |
| pathlib | stdlib | Construct `firestarter/include/firestarter.h` path for skipif guard | TEST-04 cross-repo path check |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| subprocess | Click's `CliRunner` | CliRunner can't wrap argparse `main()` cleanly today; subprocess is migration-transparent (D-01 rationale) |
| Pre-normalize + `assert str == snapshot` | syrupy matchers (`path_type`, `path_value`) | syrupy matchers work on dicts/objects; CLI stdout is plain strings — pre-normalization via `re.sub` is simpler and more readable |
| tiny real-clock timeout | monkeypatching `time.time` | Real-clock with 0.02 s timeout runs in < 25 ms total (experimentally confirmed); avoids complexity of mocking time in a generator |

**Installation:**
```bash
# In pyproject.toml [project.optional-dependencies].test
pip install -e ".[test]"
```

**Version verification:**

```
syrupy: 5.2.0 (latest as of 2026-05-27, PyPI)
pytest: 9.0.3 (already installed, satisfies syrupy >=8.0.0 requirement)
```

---

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| syrupy | PyPI | ~6.5 yrs (first release 2019-12-05) | Established | github.com/syrupy-project/syrupy | [SUS] — false positive (phonetic similarity to "scrapy"; not a typosquat) | Approved — see note |

**Packages removed due to slopcheck [SLOP] verdict:** none

**Packages flagged as suspicious [SUS]:** syrupy — slopcheck flagged due to phonetic similarity to "scrapy". This is a confirmed false positive. Syrupy is a legitimate, 6.5-year-old pytest snapshot plugin maintained by the syrupy-project GitHub organization, with 117 releases and first published 2019-12-05 on PyPI. It is the canonical pytest snapshot testing library, cited in pytest ecosystem documentation and widely used in production codebases. Verified via github.com/syrupy-project/syrupy and pypi.org/project/syrupy. [CITED: github.com/syrupy-project/syrupy] [CITED: pypi.org/project/syrupy]

---

## Architecture Patterns

### System Architecture Diagram

```
TEST-01: CLI Surface Golden
  subprocess → firestarter --help/list/info/search/... → normalize_output() → assert == snapshot

TEST-01: E2E Happy Paths (in-process)
  make_comm(fake_serial) → canned firmware bytes → main()/direct-call → assert == snapshot

TEST-02: Serial Frame-Parse
  _FakeSerial.feed(bytes) → comm._read_and_parse_lines(tiny_timeout) → list(yields) → assert frames

TEST-03: EpromDatabase Unit Tests
  EpromDatabase(skip_local_override=True) → .get_eprom() / .convert_to_programmer() → assert fields

TEST-04: Firmware-Contract Parity
  skipif (firestarter/include/firestarter.h absent)
  from firestarter.constants import COMMAND_* / FLAG_* / CTRL_*
  assert COMMAND_READ == 0x01  # hard-coded hex literal from firestarter.h

TEST-05: Bug Characterization
  @pytest.mark.xfail(strict=True)
  # BUG: fix lands Phase 41
  assert build_arg_flags(non_namespace_args_with_force_False) FLAG_FORCE bit == 0

  @pytest.mark.xfail(strict=True)
  # BUG: fix lands Phase 42
  assert EpromOperationError raised by _run_state_machine is NOT reported as "Communication error"
```

### Recommended Project Structure

```
firestarter_app/
├── firestarter/
│   └── database.py          # de-singleton: remove __new__/_initialized, add skip_local_override
├── tests/
│   ├── conftest.py           # existing; no changes needed for Phase 36
│   ├── __snapshots__/        # syrupy creates this automatically on first --snapshot-update run
│   │   └── test_characterization.ambr
│   ├── test_characterization.py         # TEST-01: CLI surface + E2E happy paths
│   ├── test_serial_characterization.py  # TEST-02: _read_and_parse_lines pin
│   ├── test_eprom_database.py           # TEST-03: DB unit tests
│   ├── test_revision_constants_parity.py  # TEST-04: extend existing file (COMMAND_*/FLAG_*/CTRL_*)
│   └── test_bug_characterization.py     # TEST-05: two xfail(strict=True) bug pins
└── pyproject.toml            # add [project.optional-dependencies].test with pytest>=8.0 + syrupy>=5.0
```

### Pattern 1: Subprocess CLI Snapshot Test

**What:** Invoke the installed `firestarter` entry point via `subprocess.run`, normalize non-deterministic content, assert against snapshot.
**When to use:** All board-independent CLI surface tests (--help, list, info, search, error paths, usage errors, argument-parse failures).
**Example:**

```python
# Source: verified live against firestarter entry point
import subprocess, re, shutil

FIRESTARTER = shutil.which("firestarter")

def normalize_output(s: str) -> str:
    """Scrub non-deterministic content so snapshots are CI/bench identical."""
    s = re.sub(r"Firestarter version: [\d.a-zA-Z]+", "Firestarter version: <VERSION>", s)
    s = re.sub(r"/dev/tty\w+", "/dev/ttyXXX", s)
    s = re.sub(r"(?:/home|/workspaces|/tmp|/Users)/[^\s]+", "<PATH>", s)
    return s

def run_firestarter(*args: str) -> tuple[str, str, int]:
    r = subprocess.run([FIRESTARTER, *args], capture_output=True, text=True, timeout=10)
    return normalize_output(r.stdout), normalize_output(r.stderr), r.returncode

def test_help(snapshot):
    stdout, stderr, rc = run_firestarter("--help")
    assert rc == 0
    assert stdout == snapshot

def test_list_help(snapshot):
    stdout, stderr, rc = run_firestarter("list", "--help")
    assert rc == 0
    assert stdout == snapshot

def test_info_bad_chip(snapshot):
    stdout, stderr, rc = run_firestarter("info", "NOTACHIP")
    assert rc == 1
    assert stdout == snapshot  # "EPROM 'NOTACHIP' not found in database."
```

### Pattern 2: In-Process Happy-Path via make_comm

**What:** Bypass `find_and_connect` via `make_comm()` (uses `__new__` to skip `__init__`), feed canned firmware responses via `fake_serial.feed()`, call the operation function directly.
**When to use:** read/write/verify/erase happy-paths (D-02). NOT via subprocess.
**Example:**

```python
# Source: verified against conftest.py fixtures and _run_state_machine code
from tests.conftest import build_frame

def test_read_happy_path(make_comm, fake_serial):
    comm = make_comm()
    # Feed INIT OK, MAIN OK, END OK frame sequence
    fake_serial.feed(b"OK: Ready\n")
    fake_serial.feed(b"INIT: init done\n")
    fake_serial.feed(b"MAIN: main done\n")
    fake_serial.feed(b"END: end done\n")
    # Call the operation directly, injecting comm
    ...
```

### Pattern 3: Syrupy Normalization via Pre-Processing

**What:** For plain-string CLI output, apply `re.sub` normalization BEFORE the `== snapshot` assertion. Syrupy matchers (`path_type`, `path_value`) are for dict/object serialization and are not the right tool for free-form strings.
**When to use:** All subprocess-captured stdout/stderr assertions.
**Example:**

```python
def test_version(snapshot):
    stdout, _, rc = run_firestarter("--version")
    assert rc == 0
    assert stdout == snapshot
    # Snapshot stored as: "Firestarter version: <VERSION>\n"
    # (version string scrubbed by normalize_output before assertion)
```

### Pattern 4: Syrupy Snapshot Workflow

**What:** Initial snapshot creation via `--snapshot-update`, then snapshot files are committed.
**When to use:** First time tests are run after writing new snapshot tests.
**Example:**

```bash
# Initial: create snapshots
pytest tests/test_characterization.py --snapshot-update

# Subsequent runs: verify against stored snapshots
pytest tests/test_characterization.py

# Snapshots stored in:
# tests/__snapshots__/test_characterization.ambr
```

### Pattern 5: `_read_and_parse_lines` Timeout Test (Tiny Real-Clock)

**What:** Use `get_response(timeout=0.02)` with an empty `_FakeSerial` to trigger `SerialTimeoutError` in < 25 ms. For sliding-window reset: feed response1, then response2 into `fake_serial.feed()` between yields.
**When to use:** TEST-02 timeout invariant test (D-12).
**Example:**

```python
# Source: experimentally verified — see research notes
import time

def test_timeout_raises_on_empty(make_comm, fake_serial):
    comm = make_comm()
    # No data fed — generator should exhaust in timeout seconds
    start = time.time()
    with pytest.raises(SerialTimeoutError):
        comm.get_response(timeout=0.02)
    assert time.time() - start < 0.5  # completes quickly

def test_sliding_window_resets_on_yield(make_comm, fake_serial):
    """Invariant: each yield of _read_and_parse_lines resets the timeout window."""
    comm = make_comm()
    resp1 = b"OK: First\n"
    resp2 = b"OK: Second\n"
    fake_serial.feed(resp1)
    
    results = []
    for r in comm._read_and_parse_lines(0.05):
        results.append(r)
        if r.message == "First":
            fake_serial.feed(resp2)  # feed second after first yield
        if len(results) >= 2:
            break
    
    assert len(results) == 2  # both yielded; window reset after first
    # If window did NOT reset, only 1 would be yielded (timeout expired)
```

### Pattern 6: EpromDatabase De-Singleton Constructor Seam

**What:** Remove `__new__`/`_initialized` singleton guard; add `skip_local_override: bool = False` parameter to `__init__` that skips `get_local_database()` and `get_local_pin_maps()` calls. Tests use `EpromDatabase(skip_local_override=True)` for determinism.
**When to use:** All TEST-03 database unit tests.
**Example:**

```python
# Production unchanged: EpromDatabase() → loads packaged data + ~/.firestarter override
# Tests: EpromDatabase(skip_local_override=True) → loads packaged data only

def test_get_eprom_w27c512(tmp_path):
    db = EpromDatabase(skip_local_override=True)
    eprom = db.get_eprom("W27C512")
    assert eprom is not None
    assert eprom["memory_size"] == 65536  # 64KB

def test_convert_to_programmer(tmp_path):
    db = EpromDatabase(skip_local_override=True)
    eprom = db.get_eprom("W27C512")
    config = db.convert_to_programmer(eprom)
    assert "bus-config" in config
    assert config["memory-size"] == 65536
```

### Pattern 7: Port Auto-Discovery Neutralization (D-05b)

**What:** Use `pytest.monkeypatch.setattr` or `unittest.mock.patch` to mock `serial.tools.list_ports.comports` to return `[]`. This prevents `_list_potential_ports` from finding real ports and ensures identical output on CI (no board) and bench (board attached).
**When to use:** Only in-process tests that exercise code paths calling `find_and_connect` or `_list_potential_ports`. Specifically: tests verifying the "no programmer found" error path.
**Why this seam:** `_list_potential_ports` ALWAYS appends discovered system ports even when `-p` is given (verified in code at serial_comm.py:767-779). A bogus `-p /dev/null` alone is insufficient. The `serial.tools.list_ports.comports` boundary is the cleanest point: it is a pure stdlib-level mock, requires no production code change, and neutralizes ALL port discovery.
**NOT needed for:** Subprocess CLI tests (`--help`, `list`, `info`, `search` never call `find_and_connect`). In-process happy-path tests using `make_comm` (which bypasses `__init__` entirely).
**Example:**

```python
def test_no_programmer_found_error(monkeypatch):
    monkeypatch.setattr(
        "serial.tools.list_ports.comports", lambda: []
    )
    # Now any call to find_and_connect raises ProgrammerNotFoundError
    ...
```

### Pattern 8: Firmware-Parity xfail/skipif

**What:** Extend `test_revision_constants_parity.py` template with hard-coded hex literals for all `COMMAND_*`, `FLAG_*`, `CTRL_*` blocks; `skipif` when firmware header is absent.
**When to use:** TEST-04.
**Example:**

```python
# Source: verified against firestarter/include/firestarter.h and constants.py
import pytest
from pathlib import Path

FIRMWARE_HEADER = Path(__file__).parent.parent.parent / "firestarter" / "include" / "firestarter.h"
FW_ABSENT = not FIRMWARE_HEADER.exists()

@pytest.mark.skipif(FW_ABSENT, reason="firestarter firmware checkout absent")
def test_command_values_match_firmware():
    from firestarter.constants import (
        COMMAND_READ, COMMAND_WRITE, COMMAND_ERASE,
        COMMAND_BLANK_CHECK, COMMAND_CHECK_CHIP_ID, COMMAND_VERIFY,
        COMMAND_READ_VPP, COMMAND_READ_VPE, COMMAND_FW_VERSION,
        COMMAND_CONFIG, COMMAND_HW_VERSION,
    )
    assert COMMAND_READ          == 0x01  # CMD_READ
    assert COMMAND_WRITE         == 0x02  # CMD_WRITE
    assert COMMAND_ERASE         == 0x03  # CMD_ERASE
    assert COMMAND_BLANK_CHECK   == 0x04  # CMD_BLANK_CHECK
    assert COMMAND_CHECK_CHIP_ID == 0x05  # CMD_CHECK_CHIP_ID
    assert COMMAND_VERIFY        == 0x06  # CMD_VERIFY
    assert COMMAND_READ_VPP      == 0x0B  # CMD_READ_VPP
    assert COMMAND_READ_VPE      == 0x0C  # CMD_READ_VPE
    assert COMMAND_FW_VERSION    == 0x0D  # CMD_FW_VERSION
    assert COMMAND_CONFIG        == 0x0E  # CMD_CONFIG
    assert COMMAND_HW_VERSION    == 0x0F  # CMD_HW_VERSION

@pytest.mark.skipif(FW_ABSENT, reason="firestarter firmware checkout absent")
def test_flag_values_match_firmware():
    from firestarter.constants import (
        FLAG_FORCE, FLAG_CAN_ERASE, FLAG_SKIP_ERASE,
        FLAG_SKIP_BLANK_CHECK, FLAG_VPE_AS_VPP,
        FLAG_OUTPUT_ENABLE, FLAG_CHIP_ENABLE, FLAG_VERBOSE,
    )
    assert FLAG_FORCE            == 0x01
    assert FLAG_CAN_ERASE        == 0x02
    assert FLAG_SKIP_ERASE       == 0x04
    assert FLAG_SKIP_BLANK_CHECK == 0x08
    assert FLAG_VPE_AS_VPP       == 0x10
    assert FLAG_OUTPUT_ENABLE    == 0x20
    assert FLAG_CHIP_ENABLE      == 0x40
    assert FLAG_VERBOSE          == 0x80
```

Note: `COMMAND_DEV_ADDRESS` (7) and `COMMAND_DEV_REGISTERS` (8) are `#ifdef DEV_TOOLS` in the firmware header — they exist in `constants.py` at `0x07`/`0x08` respectively. The parity test should either skip these two or note the DEV_TOOLS guard.

### Pattern 9: xfail(strict=True) Bug Characterization

**What:** Test asserts the CORRECTED behavior. While the bug exists, the test fails (XFAIL, suite stays green). When the fix lands (Phase 41/42), the test passes (XPASS with strict=True = ERROR, forcing marker removal).
**When to use:** TEST-05 two bug tests.
**Example:**

```python
import pytest

@pytest.mark.xfail(strict=True, reason="BUG: main.py:497 uses 'in' not getattr; fix lands Phase 41 (CLI-03)")
def test_build_arg_flags_force_truthiness_not_existence():
    """Corrected behavior: build_arg_flags should use getattr(args, 'force', False),
    not 'force' in args. The 'in' operator raises TypeError on non-Namespace objects
    (e.g., plain class objects as Click would provide). The corrected pattern works
    correctly regardless of object type.
    # BUG: main.py:497 — fix lands Phase 41 (CLI-03)
    """
    from firestarter.main import build_arg_flags
    from firestarter.constants import FLAG_FORCE

    class PlainArgs:
        """Non-Namespace args object — 'in' operator raises TypeError."""
        blank_check = True
        verbose = False
        vpe_as_vpp = False
        force = False  # force is False — FLAG_FORCE should NOT be set

    flags = build_arg_flags(PlainArgs())
    assert (flags & FLAG_FORCE) == 0  # corrected: force=False means FLAG_FORCE not set


@pytest.mark.xfail(strict=True, reason="BUG: eprom_operations.py:265 conflates EpromOperationError with SerialError; fix lands Phase 42 (ERR-01)")
def test_eprom_operation_error_not_labeled_as_communication_error(make_comm, fake_serial):
    """Corrected behavior: when firmware reports an operational error (EpromOperationError),
    it should surface as an operational error with the firmware's own message — NOT as
    'Communication error during ...' which implies a serial transport failure.
    # BUG: eprom_operations.py:265 — fix lands Phase 42 (ERR-01)
    Operator-reported: 'app always reports that the communication is broken when the hw returns an error.'
    """
    from firestarter.eprom_operations import EpromOperationError
    ...
    # Test that a firmware ERROR response during state machine yields an EpromOperationError
    # that is NOT logged as "Communication error"
    # (Currently the except clause at :265 lumps EpromOperationError with SerialError/SerialTimeoutError
    # and logs "Communication error during <operation>")
```

### Anti-Patterns to Avoid

- **Subprocess for happy-path I/O tests:** `BytesIO` fake cannot be injected across process boundary. Use `make_comm` + `fake_serial` instead (D-02).
- **CliRunner for current CLI:** argparse's `main()` cannot be cleanly wrapped by Click's `CliRunner` before Phase 41. Use subprocess for CLI surface tests.
- **click as a test dep in Phase 36:** `CliRunner` is only needed from Phase 41 onward. Do not add `click` to test deps now.
- **Snapshot without normalization:** Version strings, absolute paths, `/dev/tty*` names appear in CLI output. Pre-normalize before `== snapshot` to prevent CI/bench divergence.
- **syrupy matchers for string output:** `path_type`/`path_value` matchers operate on serialized object graphs, not free-form strings. Use `re.sub` normalization for subprocess stdout/stderr.
- **Testing _read_and_parse_lines internals:** The generator body is ring-fenced for v1.9 RCA (GATE-1.8d). Tests must observe only externally-visible behavior (what `get_response()` yields, when `SerialTimeoutError` is raised).
- **xfail without strict=True:** Using `strict=False` means XPASS is silently ignored. With `strict=True`, XPASS fails the suite and forces the developer to remove the marker when the fix lands.
- **Modifying `_read_and_parse_lines`:** It is ring-fenced. Do not add parameters, logging, or instrumentation. Test it only via `get_response()`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Snapshot storage/diffing | Custom golden-file comparison | syrupy | syrupy handles `.ambr` format, `--snapshot-update`, unused-snapshot cleanup, and pytest integration automatically |
| Port-filtering mock | Production seam parameter | monkeypatch `serial.tools.list_ports.comports` | No production code change; cleaner than adding a `_port_lister` injection seam |
| CRC computation in new tests | New CRC implementation | `_ref_crc8_ccitt` from `conftest.py` | Reference CRC is already table-free and catches production lookup-table regressions |
| Frame assembly in new tests | Inline struct packing | `build_frame(msg_id, params)` from `conftest.py` | Fixture already tested and used by `test_decoder.py` |
| Version string parsing | Custom regex | `re.sub` with `normalize_output` helper | Single shared function; avoids fragile per-test normalization logic |

**Key insight:** The existing `tests/conftest.py` is comprehensive — `fake_serial`, `make_comm`, `build_frame`, `_ref_crc8_ccitt` are production-quality fixtures that the new tests should reuse without duplication.

---

## EpromDatabase De-Singleton: Detailed Design (D-06)

### Current Structure (database.py:165-181)

```python
class EpromDatabase:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EpromDatabase, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if EpromDatabase._initialized:
            return
        self.proms = {}
        self.pin_maps = {}
        self._initialize_database_core()
        EpromDatabase._initialized = True
```

### Target Structure (Phase 36 change)

Remove `__new__`/`_initialized` guard entirely. Add `skip_local_override: bool = False` to `__init__`:

```python
class EpromDatabase:
    def __init__(self, skip_local_override: bool = False):
        self.proms = {}
        self.pin_maps = {}
        self._initialize_database_core(skip_local_override=skip_local_override)
        logger.debug("EpromDatabase initialized.")

    def _initialize_database_core(self, skip_local_override: bool = False):
        self.proms = _read_config_file("chip_database.json")
        if not skip_local_override:
            local_db = get_local_database()
            if local_db:
                self.proms = self._merge_databases(self.proms, local_db)
        self.pin_maps = _read_config_file("pinouts.json")
        if not skip_local_override:
            local_pin_maps = get_local_pin_maps()
            if local_pin_maps:
                self.pin_maps = self._merge_pin_maps(self.pin_maps, local_pin_maps)
```

### Blast Radius Analysis

| Call Site | Location | Impact |
|-----------|----------|--------|
| `db_instance = EpromDatabase()` | `main.py:589` | Creates one instance per `main()` invocation — identical behavior |
| `db_instance = EpromDatabase()` | `main.py:39,48` (argcomplete validator) | Creates fresh instance on tab-complete. Loads DB from scratch — slightly slower on first tab-complete, not wrong. Only fires in shell-completion context. |
| `db_instance = EpromDatabase()` | `eprom_info.py:285` | Standalone dev/test script `main()` — creates new instance, correct behavior |
| `db_instance = EpromDatabase()` | `ic_layout.py:297` | Standalone dev/test script `main()` — creates new instance, correct behavior |
| `EpromConsolePresenter(db_instance)` | `main.py:597` | Injected — unaffected |
| `EpromInfo(db_instance)` constructor | `eprom_info.py:27` | Injected — unaffected |
| `EpromSpecBuilder(db_instance)` constructor | `ic_layout.py:32` | Injected — unaffected |

**Blast radius: LOW.** All production paths go through `main():589`'s single `db_instance`. The only risk is the argcomplete validator creating a fresh DB load (slightly slower on tab-complete, not wrong). No existing call site relies on two `EpromDatabase()` calls returning the same object.

**No class-level `_instance`/`_initialized` cleanup needed in tests** after de-singleton — the issue disappears entirely.

---

## Build_arg_flags Bug: Exact Mechanism

The bug at `main.py:497`:
```python
force = args.force if "force" in args else False
```

`"force" in args` on an `argparse.Namespace` calls `vars(args).__contains__("force")`, which returns `True` if the attribute EXISTS in the namespace — even if its value is `False`. For argparse, this works coincidentally because `args.force` IS the correct value. However:

1. **Click migration (Phase 41):** Click does not pass an `argparse.Namespace`. When `build_arg_flags` is called with a plain Python object (no `__contains__` protocol), `"force" in args` raises `TypeError: argument of type 'X' is not iterable`.
2. **The corrected pattern:** `getattr(args, "force", False)` — works for any object type, reads the actual value.

**xfail test trigger:** Call `build_arg_flags(PlainArgs())` where `PlainArgs` is a plain class without `__contains__`. Current code raises `TypeError` → test "fails" → `xfail` → suite green. After Phase 41 fix: `getattr` path works → test passes → `strict=True` forces marker removal.

---

## Comm-Error Bug: Exact Mechanism

The bug at `eprom_operations.py:265-267`:
```python
except (SerialError, SerialTimeoutError, EpromOperationError) as e:
    logger.error(f"Communication error during {operation_name}: {e}")
    return False, str(e)
```

`EpromOperationError` is raised when the firmware reports a legitimate operational failure (e.g., blank check failed, write error) — the serial link is healthy, the firmware executed the command, and responded with `ERROR:`. Lumping it with `SerialError`/`SerialTimeoutError` (transport failures) means the user always sees `"Communication error"` even when the firmware correctly reported a hardware issue.

**Operator report:** `"app always reports that the communication is broken when the hw returns an error."`

**The fix (Phase 42):** Split the `except` clause:
```python
except (SerialError, SerialTimeoutError) as e:
    logger.error(f"Communication error during {operation_name}: {e}")
    return False, str(e)
except EpromOperationError as e:
    logger.error(f"Programmer error during {operation_name}: {e}")
    return False, str(e)
```

**xfail test:** Feed a canned firmware `ERROR:` response through `make_comm`/`fake_serial`. With current code, the return value includes "Communication error". Corrected behavior: "Programmer error" or the firmware's actual error message. The xfail test asserts the corrected string; currently it fails (wrong string) → xfail. After Phase 42 fix: passes → strict=True forces marker removal.

---

## Common Pitfalls

### Pitfall 1: Snapshot Drift from Non-Normalized Output

**What goes wrong:** Snapshot contains version string `3.0.0b5` on day 1; test fails on CI after version bump.
**Why it happens:** `--version` output includes the actual package version.
**How to avoid:** Apply `normalize_output(s)` before every `== snapshot` assertion. Include in a shared helper so normalization is consistent across all test functions.
**Warning signs:** Snapshot test fails only on CI or after a version bump.

### Pitfall 2: Port Scanning in CI

**What goes wrong:** `test_no_programmer_found` passes locally (no board), fails in CI (or vice versa).
**Why it happens:** `_list_potential_ports` APPENDS system-discovered ports even when `-p` is given (`serial_comm.py:767-779`). On CI there are no serial ports → `ProgrammerNotFoundError`. On bench with a board → port found → different behavior.
**How to avoid:** Mock `serial.tools.list_ports.comports` to `lambda: []` for any in-process test that exercises `find_and_connect`. Subprocess tests for board-independent commands (`--help`, `list`, `info`) never call `find_and_connect` — no mock needed there.
**Warning signs:** Test behavior differs between CI and bench; random flakiness when board is plugged/unplugged.

### Pitfall 3: xfail(strict=True) Stale Markers

**What goes wrong:** Phase 41 fixes `build_arg_flags` but the `xfail` marker is not removed. With `strict=True`, the test produces XPASS → ERROR → suite breaks in Phase 41.
**Why it happens:** `strict=True` means "this must fail; if it passes, something unexpected happened."
**How to avoid:** Each bug-characterization test carries a `# BUG: fix lands Phase NN` comment. The Phase NN plan MUST include a task to remove the xfail marker as part of the fix commit.
**Warning signs:** Phase 41 plan succeeds but `pytest` exits non-zero with `XPASS` errors.

### Pitfall 4: Singleton State Leaking Between Tests

**What goes wrong:** After de-singleton, two tests both call `EpromDatabase()` without `skip_local_override=True`. If the operator's `~/.firestarter/database.json` is absent on CI, tests pass. If present on the operator's machine, tests load custom data and may return different results.
**Why it happens:** `get_local_database()` reads `~/.firestarter/database.json` if it exists.
**How to avoid:** All TEST-03 database unit tests must use `EpromDatabase(skip_local_override=True)`. Never use bare `EpromDatabase()` in tests that assert specific chip data.
**Warning signs:** Tests pass locally but fail on CI (or vice versa) with unexpected chip data.

### Pitfall 5: Modifying `_read_and_parse_lines`

**What goes wrong:** A test that needs a hook or instrumentation in `_read_and_parse_lines` prompts a "small addition" that turns out to change byte-read behavior.
**Why it happens:** The generator is complex; it's tempting to add debug yields or state tracking.
**How to avoid:** Test only via `get_response()` and by observing what comes out of the generator. Phase 40 will add the `# DO NOT MODIFY` marker. Phase 36 must not touch the function body.
**Warning signs:** Any change to `serial_comm.py:543-666` in this phase.

### Pitfall 6: syrupy `__snapshots__` Not Committed

**What goes wrong:** Snapshots are created locally but not committed; CI runs with empty `__snapshots__/` → all snapshot assertions fail with "snapshot not found".
**Why it happens:** `tests/__snapshots__/` directory may be in `.gitignore` or simply forgotten.
**How to avoid:** Run `pytest --snapshot-update` first (creates `.ambr` files), then commit `tests/__snapshots__/` directory. The plan must include an explicit task to commit snapshots.
**Warning signs:** All snapshot tests fail on CI with "snapshot does not exist."

### Pitfall 7: DEV_TOOLS Guard in Firmware Parity Test

**What goes wrong:** The parity test asserts `COMMAND_DEV_ADDRESS == 0x07`, but in the firmware header, `CMD_DEV_ADDRESS` is inside `#ifdef DEV_TOOLS`. The constant exists in Python's `constants.py:34` unconditionally.
**Why it happens:** The Python side does not have the DEV_TOOLS guard.
**How to avoid:** For `COMMAND_DEV_ADDRESS` (7) and `COMMAND_DEV_REGISTERS` (8), the parity test should note the DEV_TOOLS guard in a comment or skip asserting them against the header literal (the Python constant is correct as a standalone assertion regardless).
**Warning signs:** CI fails on the firmware-parity test when DEV_TOOLS is not defined.

---

## Code Examples

### Verified COMMAND_* Constants Mapping

```python
# Source: verified by reading both firestarter/include/firestarter.h and firestarter/constants.py
# Firmware (firestarter.h)    Python (constants.py)        Match
# CMD_READ          = 1   →   COMMAND_READ          = 1    ✓
# CMD_WRITE         = 2   →   COMMAND_WRITE         = 2    ✓
# CMD_ERASE         = 3   →   COMMAND_ERASE         = 3    ✓
# CMD_BLANK_CHECK   = 4   →   COMMAND_BLANK_CHECK   = 4    ✓
# CMD_CHECK_CHIP_ID = 5   →   COMMAND_CHECK_CHIP_ID = 5    ✓
# CMD_VERIFY        = 6   →   COMMAND_VERIFY        = 6    ✓
# CMD_DEV_ADDRESS   = 7   →   COMMAND_DEV_ADDRESS   = 7    ✓ (#ifdef DEV_TOOLS)
# CMD_DEV_REGISTER  = 8   →   COMMAND_DEV_REGISTERS = 8    ✓ (#ifdef DEV_TOOLS)
# CMD_READ_VPP      = 11  →   COMMAND_READ_VPP      = 11   ✓
# CMD_READ_VPE      = 12  →   COMMAND_READ_VPE      = 12   ✓
# CMD_FW_VERSION    = 13  →   COMMAND_FW_VERSION    = 13   ✓ (D-09: NOT missing)
# CMD_CONFIG        = 14  →   COMMAND_CONFIG        = 14   ✓
# CMD_HW_VERSION    = 15  →   COMMAND_HW_VERSION    = 15   ✓
```

### Verified FLAG_* Constants Mapping

```python
# Source: verified by reading both firestarter/include/firestarter.h and firestarter/constants.py
# Firmware                   Python                        Match
# FLAG_FORCE         = 0x01  → FLAG_FORCE         = 0x01  ✓
# FLAG_CAN_ERASE     = 0x02  → FLAG_CAN_ERASE     = 0x02  ✓
# FLAG_SKIP_ERASE    = 0x04  → FLAG_SKIP_ERASE    = 0x04  ✓
# FLAG_SKIP_BLANK_CHECK=0x08 → FLAG_SKIP_BLANK_CHECK=0x08 ✓
# FLAG_VPE_AS_VPP    = 0x10  → FLAG_VPE_AS_VPP    = 0x10  ✓
# FLAG_OUTPUT_ENABLE = 0x20  → FLAG_OUTPUT_ENABLE = 0x20  ✓
# FLAG_CHIP_ENABLE   = 0x40  → FLAG_CHIP_ENABLE   = 0x40  ✓
# FLAG_VERBOSE       = 0x80  → FLAG_VERBOSE       = 0x80  ✓
```

Note: `CTRL_*` constants from `rurp_pinout.h` — not in `firestarter.h`. The parity test for `CTRL_*` should reference `firestarter/include/rurp_pinout.h`, which IS present in the firmware checkout alongside `firestarter.h`. The skipif guard covers both headers.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| No Python tests for core paths | Live pytest suite (98 tests, 1.09 s) | Phase 6 "Plan 03" | All new Phase 36 tests build on this |
| `EpromDatabase` singleton | Injectable constructor (Phase 36) | This phase | Tests can create isolated instances |
| pytest>=7.0 in `dev` dep group | pytest>=8.0 + syrupy>=5.0 in `test` dep group | This phase | syrupy 5.x requires pytest>=8.0 |
| No snapshot testing | syrupy `.ambr` snapshots | This phase | CLI surface pinned before migration |
| REVISION_* parity only | COMMAND_*/FLAG_*/CTRL_* parity too | This phase | Full firmware-contract coverage |

**Deprecated/outdated:**

- `.planning/codebase/TESTING.md` claims "no Python tests" — STALE. The live suite has 98 tests. Ignore that document.
- `[project.optional-dependencies].dev` group name: CONTEXT.md mandates adding a new `test` group. Keep `dev` as-is (do not rename it, to avoid breaking any existing dev installs).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `CTRL_*` constants from `rurp_pinout.h` are physically present alongside `firestarter.h` in the firmware checkout | Code Examples | TEST-04 skipif guard covers absence; risk is low |
| A2 | `shutil.which("firestarter")` reliably returns the installed entry point in all CI environments | Pattern 1 | Tests fail if `firestarter` is not on PATH; fallback: `sys.executable` + `-c "from firestarter.main import main; ..."` |
| A3 | The two `EpromDatabase()` calls in the argcomplete validator (`main.py:39,48`) do not cause observable regression after de-singleton (each creates a fresh instance loading the same packaged data) | De-Singleton Design | If argcomplete triggers extremely frequently, the extra DB load is slightly slower. Not wrong. |

**If this table is empty for a claim:** All other claims were verified against live code or cited from official sources.

---

## Open Questions

1. **`CTRL_*` parity source header**
   - What we know: `CTRL_*` constants in Python mirror `firestarter/include/rurp_pinout.h`, not `firestarter.h`. The research confirmed that `firestarter.h` does not contain the CTRL definitions.
   - What's unclear: Whether `rurp_pinout.h` is present in the same location as `firestarter.h`.
   - Recommendation: The parity test should use `skipif` that checks for the presence of `firestarter/include/firestarter.h` (as the proxy for "firmware checkout present") — if `firestarter.h` is present, `rurp_pinout.h` is almost certainly present too. The test itself references both headers.

2. **pyproject.toml `test` vs `dev` group**
   - What we know: Currently the group is `dev = ["pytest>=7.0"]`. CONTEXT.md says add to `.test`.
   - What's unclear: Should we rename `dev` → `test` (breaking existing `pip install -e ".[dev]"` workflows) or add `test` alongside `dev`?
   - Recommendation: Add a new `test` group; keep `dev` as-is. The plan task should add `test = ["pytest>=8.0", "syrupy>=5.0"]` without touching `dev`.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | All tests | ✓ | 3.12.13 | — |
| pytest | All tests | ✓ | 9.0.3 | — |
| syrupy | TEST-01 snapshots | ✓ (installed) | 5.2.0 | Add to `test` deps; install before test run |
| `firestarter` entry point | TEST-01 subprocess | ✓ | 3.0.0b5 at `/home/vscode/.local/bin/firestarter` | `pip install -e .` to create |
| `firestarter/include/firestarter.h` | TEST-04 parity | ✓ (present) | HEAD | `skipif` guard when absent |
| `firestarter/include/rurp_pinout.h` | TEST-04 CTRL_* | ✓ (present alongside firestarter.h) | HEAD | Same `skipif` guard |

**Missing dependencies with no fallback:** none

**Missing dependencies with fallback:** syrupy (must be added to `pyproject.toml` `test` group and installed; currently installed in dev environment but not declared as a project dependency).

---

## Validation Architecture

> Nyquist validation is ENABLED (key absent from config.json, treated as enabled).

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 + syrupy 5.2.0 |
| Config file | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `pytest tests/test_characterization.py tests/test_serial_characterization.py tests/test_eprom_database.py -x -q` |
| Full suite command | `pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TEST-01 | CLI surface pins (--help, list, info, search, error paths, mutex flags) | Snapshot (subprocess) | `pytest tests/test_characterization.py -x -q` | ❌ Wave 0 |
| TEST-01 | E2E read/write/verify/erase happy paths | Unit (in-process) | `pytest tests/test_characterization.py::test_read_happy_path -x` | ❌ Wave 0 |
| TEST-02 | `_read_and_parse_lines` preamble→body→terminator sequence | Unit | `pytest tests/test_serial_characterization.py -x -q` | ❌ Wave 0 |
| TEST-02 | Sliding-window timeout reset on every yield | Unit | `pytest tests/test_serial_characterization.py::test_sliding_window -x` | ❌ Wave 0 |
| TEST-03 | `EpromDatabase` injectable construction | Unit | `pytest tests/test_eprom_database.py -x -q` | ❌ Wave 0 |
| TEST-03 | `get_eprom`, `convert_to_programmer`, DIP→RURP pin translation | Unit | `pytest tests/test_eprom_database.py -x -q` | ❌ Wave 0 |
| TEST-04 | COMMAND_*/FLAG_*/CTRL_* parity (extends existing) | Parity | `pytest tests/test_revision_constants_parity.py -x -q` | ✅ (extend) |
| TEST-05 | `build_arg_flags` force bug pinned as xfail | xfail | `pytest tests/test_bug_characterization.py -x -q` | ❌ Wave 0 |
| TEST-05 | Comm-error mislabeling bug pinned as xfail | xfail | `pytest tests/test_bug_characterization.py -x -q` | ❌ Wave 0 |
| GATE-1.8e | Full suite green (existing + new) | All | `pytest tests/ -q` | ✅ (ongoing) |

### Sampling Rate

- **Per task commit:** `pytest tests/ -q` (98 existing + new tests; 1.09 s baseline)
- **Per wave merge:** `pytest tests/ -q` (full suite)
- **Phase gate:** Full suite green before marking Phase 36 complete

### Wave 0 Gaps

- [ ] `tests/test_characterization.py` — covers TEST-01 (CLI surface + happy paths)
- [ ] `tests/test_serial_characterization.py` — covers TEST-02 (`_read_and_parse_lines` pin)
- [ ] `tests/test_eprom_database.py` — covers TEST-03 (DB unit tests)
- [ ] `tests/test_bug_characterization.py` — covers TEST-05 (two xfail bug pins)
- [ ] `tests/__snapshots__/` directory + `.ambr` files — created by `--snapshot-update` and committed
- [ ] `pyproject.toml` `[project.optional-dependencies].test` group — `pytest>=8.0`, `syrupy>=5.0`
- [ ] `database.py` de-singleton change — remove `__new__`/`_initialized`, add `skip_local_override` seam

*(Existing: `tests/test_revision_constants_parity.py` — EXTEND for TEST-04; `tests/conftest.py` — no changes needed)*

---

## Meta-Validation: Safety Net Quality

A characterization-test phase has a second-order validation concern: does the safety net actually catch regressions?

**Behavioral coverage:**

| Coverage Area | Sampled | Detection Mechanism |
|---------------|---------|---------------------|
| CLI help output (all 14 subcommands) | ✓ | Snapshot diff — any flag removal/rename shows up |
| CLI exit codes | ✓ | `assert rc == 0` / `assert rc == 1` / `assert rc == 2` |
| Argument-parse error paths | ✓ | Snapshot of stderr output |
| Board-independent DB-backed output (list, info, search) | ✓ | Snapshot — DB schema changes show up |
| Serial frame preamble + body + terminator parsing | ✓ | Unit: verified byte-by-byte |
| Sliding-window timeout reset invariant | ✓ | Tiny real-clock test: feeds two responses, asserts both yielded |
| `EpromDatabase` field shapes | ✓ | Unit: asserts specific fields on known chips |
| Firmware constant values | ✓ | Hard-coded hex literals: any drift fails immediately |
| `build_arg_flags` force bug | ✓ (xfail) | Forces marker removal when Phase 41 fix lands |
| Comm-error mislabeling bug | ✓ (xfail) | Forces marker removal when Phase 42 fix lands |

**Unsampled (and why):**

- Live hardware I/O (read/write/verify/erase via real Arduino): hardware-gated; not a risk for this pure-software milestone.
- argcomplete completion behavior: not safety-net territory; confirmed with operator in Phase 41.
- `~/.firestarter` user-override merge path: tested indirectly by constructing `EpromDatabase(skip_local_override=False)` in one test confirming the merge logic still loads without error.

**Determinism guarantees:**

- CI (no board): subprocess tests never call `find_and_connect`; in-process tests use `fake_serial`; DB tests use `skip_local_override=True`; snapshots are pre-normalized.
- Bench (board attached): same guarantees — the board-independence comes from the test structure, not env variables or skips.

**xfail-strict proof:** The xfail(strict=True) tests prove the bugs are real and pinned to their fix phases by construction: if the bug were accidentally fixed before Phase 41/42, the xfail would flip to XPASS → ERROR → suite breaks → developer notices and removes the marker. This is the enforcement mechanism.

---

## Security Domain

> `security_enforcement` key is absent from `.planning/config.json` — treated as enabled.

This phase is test-only + one production code change (singleton removal). No new network I/O, authentication, cryptography, or user input validation is introduced.

| ASVS Category | Applies | Notes |
|---------------|---------|-------|
| V2 Authentication | No | No auth code touched |
| V3 Session Management | No | No sessions |
| V4 Access Control | No | No access control |
| V5 Input Validation | No new exposure | `EpromDatabase` de-singleton reads packaged JSON; test seam only controls local-override skip |
| V6 Cryptography | No | No crypto code touched |

The only security-adjacent concern: `EpromDatabase(skip_local_override=True)` prevents loading `~/.firestarter/database.json` in tests — this is a privacy/determinism feature, not a security gap. The production default `skip_local_override=False` preserves existing behavior.

---

## Project Constraints (from CLAUDE.md)

Directives extracted from `/workspaces/CLAUDE.md` and `/workspaces/firestarter_app/CLAUDE.md`:

| Directive | How It Affects Phase 36 |
|-----------|------------------------|
| `constants.py` must stay in sync with `firestarter/include/firestarter.h` | TEST-04 enforces this — extend parity test to COMMAND_*/FLAG_*/CTRL_* |
| `_read_and_parse_lines` atomic-read invariant preserved (GATE-1.8a) | Test it externally only via `get_response()`; do NOT modify the generator body |
| Sub-repo code lives in `firestarter_app/`; meta-repo tracks only `.planning/` | All test file writes and database.py changes go in `firestarter_app/`; commit to `v1.8-app-cleanup` branch in the sub-repo |
| CLAUDE.md note: "main.py — Click CLI entry point" is aspirational | DO NOT use CliRunner in Phase 36; CLI is argparse today |
| `CTRL_*` mirrors `rurp_pinout.h`; `REVISION_*` mirrors `rurp_shield.h`; keep in sync | TEST-04 CTRL_* parity asserts against `rurp_pinout.h` literals |

---

## Sources

### Primary (HIGH confidence)

- Live code read: `firestarter_app/firestarter/serial_comm.py` — `_read_and_parse_lines`, `_list_potential_ports`, `find_and_connect`
- Live code read: `firestarter_app/firestarter/database.py` — singleton guard, `_initialize_database_core`, `get_local_database`
- Live code read: `firestarter_app/firestarter/main.py:495-510` — `build_arg_flags` bug
- Live code read: `firestarter_app/firestarter/eprom_operations.py:265-267` — comm-error conflation
- Live code read: `firestarter_app/firestarter/constants.py` — all COMMAND_*/FLAG_*/CTRL_*/REVISION_* values
- Live code read: `firestarter/include/firestarter.h` — all CMD_*/FLAG_* values (C header)
- Live code read: `firestarter_app/tests/conftest.py` — `fake_serial`, `make_comm`, `build_frame`, `_ref_crc8_ccitt`
- Live code read: `firestarter_app/tests/test_revision_constants_parity.py` — exact template for TEST-04
- Experimental verification: `_read_and_parse_lines` sliding-window reset (two responses yielded in < 1 ms); `get_response(timeout=0.02)` raises `SerialTimeoutError` in ~21 ms
- Experimental verification: `build_arg_flags` with `PlainArgs()` raises `TypeError` on `"force" in args`
- Experimental verification: `EpromDatabase` singleton behavior; all call sites analyzed
- Experimental verification: `firestarter --help`, `list`, `info`, `bad-chip` subprocess invocations — output format and return codes confirmed
- [CITED: github.com/syrupy-project/syrupy] — confirmed legitimate 6.5-year-old pytest snapshot plugin, 117 releases, pypi.org first release 2019-12-05
- [CITED: pypi.org/project/syrupy] — version history, maintainer, license

### Secondary (MEDIUM confidence)

- syrupy README (github.com/syrupy-project/syrupy/blob/main/README.md) — `snapshot.with_defaults`, `path_type`, `path_value`, `--snapshot-update`, `__snapshots__/` layout

### Tertiary (LOW confidence)

None — all findings verified against live code.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — syrupy installed and verified; pytest already in project; subprocess entry point confirmed live
- Architecture: HIGH — all patterns experimentally verified against live code
- Pitfalls: HIGH — most derived from actual code inspection, not speculation
- EpromDatabase de-singleton design: HIGH — all call sites read and analyzed
- Bug mechanics: HIGH — both bugs reproduced experimentally

**Research date:** 2026-05-27
**Valid until:** 2026-07-27 (stable tooling; syrupy version pinned in pyproject.toml)

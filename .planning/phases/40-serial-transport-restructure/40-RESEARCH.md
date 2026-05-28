# Phase 40: Serial / Transport Restructure — Research

**Researched:** 2026-05-28
**Domain:** Python serial-transport refactoring — `serial_comm.py` reduction to transport + dispatch; `_validate_firmware_version` extraction; `codec.py` `decode_id_frame` extraction; dead-code sweep; ring-fence marker; type-hint completion.
**Confidence:** HIGH — all findings verified against live source files in the `v1.8-app-cleanup` branch. No web searches required; this is pure codebase investigation.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
D-01 through D-19 (all locked 2026-05-28 — "you recommend" delegation).  See 40-CONTEXT.md `<decisions>` section for the full list. The table below summarises the ones most load-bearing for planning:

| ID | Decision |
|----|----------|
| D-01 | `_validate_firmware_version(version_str: str, allow_pre_v12: bool = False) -> None` — `@staticmethod`, owns the complete version-guard policy |
| D-02 | Env-var I/O stays in `_probe_port`; staticmethod receives the boolean |
| D-03 | `_is_version_sufficient` stays as internal "≥ 2.0.0" helper |
| D-04 | `_probe_port`'s "Could not parse FW message" paths stay in `_probe_port` |
| D-05 | `tests/test_fw_version_guard.py` covers the guard directly (matrix of accept/reject) |
| D-06 | Extract `_decode_id_frame` body to `codec.decode_id_frame` free function; thin 1-line wrapper stays on `SerialCommunicator` |
| D-07 | Why extract: `_decode_id_frame` IS frame-decode orchestration; codec.py is the natural home |
| D-08 | Breadcrumb docstring in `codec.decode_id_frame` per GATE-1.8d context |
| D-09 | `_log_rurp_feedback` and `_parse_response_line` STAY on `SerialCommunicator` |
| D-10 | DELETE `STATE_MACHINE_PREFIXES` (line 93) |
| D-11 | DELETE `read_line_bytes` (lines 164–172) |
| D-12 | DELETE three orphan/dead comment fragments (lines 64, 161, 207-209) |
| D-13 | KEEP `PREFIX_REGEX` rationale block (lines 82–90) |
| D-14 | KEEP F401 re-export comment block (lines 42–47) |
| D-15 | `# DO NOT MODIFY — v1.9 RCA territory (GATE-1.8d)` comment block above `def _read_and_parse_lines` |
| D-16 | Do NOT ring-fence `_decode_id_frame`, `_parse_response_line`, `_log_rurp_feedback` |
| D-17 | Public methods get `->` return annotations, legacy `Optional[X]` / `List[X]` style |
| D-18 | mypy strict-overrides addition OUT OF SCOPE (Phase 42 ERR-02) |
| D-19 | Module/function docstrings OUT OF SCOPE (Phase 42 ERR-03) |

### Claude's Discretion
- Exact `_validate_firmware_version` error-message strings (must be byte-identical to today's raises)
- Whether `tests/test_fw_version_guard.py` is a new file (recommend: yes, per SC#2)
- Function ordering inside `codec.py` after `decode_id_frame` is added
- Thin `_decode_id_frame` wrapper's docstring

### Deferred Ideas (OUT OF SCOPE)
- `[[tool.mypy.overrides]]` strict entry for `firestarter.serial_comm` — Phase 42 ERR-02
- Public-method docstrings — Phase 42 ERR-03
- `Optional[X]` → `X | None` modernization — Python 3.10+ floor required
- `ProtocolStateMachine` extraction — explicitly deferred to v1.9 (PROTOSM-01)
- Removing the thin `_decode_id_frame` wrapper — after Phase 41+ is settled
- Click error→exit-code mapping for `FirmwareOutdatedError` — Phase 41/42
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SERIAL-01 | `SerialCommunicator` reduced to transport + command dispatch; firmware-handshake concern lifted out; type hints added; `STATE_MACHINE_PREFIXES` dead code deleted | Verified: `STATE_MACHINE_PREFIXES` at line 93, zero external imports; `read_line_bytes` at 164-172, zero callers; three orphan comments confirmed dead at lines 64, 161, 207-209; `_decode_id_frame` at 226-334 ready for extraction; 7 methods missing `-> None` annotations identified |
| SERIAL-02 | `_validate_firmware_version` extracted as testable `@staticmethod`; `tests/test_fw_version_guard.py` covers version-guard logic directly | Verified: current env-var coupling at lines 651-654; exact FirmwareOutdatedError message strings extracted; D-05 test matrix has one correction (see Findings §3); `test_fwguard.py` already exists but covers _probe_port integration only, not the new staticmethod |
| SERIAL-03 | `_read_and_parse_lines` body byte-identical; `# DO NOT MODIFY` comment above def; all public `SerialCommunicator` methods have type-annotated signatures | Verified: generator body at 336-461; all 7 unannotated public methods confirmed; existing test_decoder.py covers body identity |
</phase_requirements>

---

## Summary

Phase 40 restructures `serial_comm.py` by extracting two responsibilities (version-guard logic, frame-decode orchestration), sweeping confirmed-dead code, and marking the ring-fenced generator. All 19 decisions in CONTEXT.md are well-grounded. The research verified every cited line number, every grep claim, and the behavioral logic of the multi-branch firmware-version guard.

**Two concrete corrections to surface before planning:**

1. **CONTEXT.md D-05 test matrix has one error:** `"2.9.9"` with `allow_pre_v12=True` is listed as "still raises (2.0.0 floor)" but live code shows `_is_version_sufficient("2.9.9", "2.0.0")` = True (2.9.9 ≥ 2.0.0), so this case PASSES (no raise). The correct expected behavior for the planner is: `"2.9.9"` + `allow_pre_v12=True` → **passes** (not raises). The test matrix row must be corrected in `test_fw_version_guard.py`.

2. **CONTEXT.md claims codec.py "already imports" CATALOG, SEVERITY_LABEL, and `_crc8_ccitt`** — these are NOT yet in codec.py. The extraction is mechanically trivial (no circular imports; messages.py and frame_parser.py are leaf modules), but the planner must schedule explicit import additions in Wave 2, not assume they are pre-existing.

One secondary finding: `"3.0.0-dev"` test case — the D-05 matrix says it should pass; see §6 below for why the planner must make an explicit decision here.

**Primary recommendation:** Proceed with the four-wave decomposition exactly as CONTEXT.md describes. The corrections above are minor (one test case row, two import-block additions). No locked decision needs to be reverted.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Version-guard policy | `SerialCommunicator._validate_firmware_version` (@staticmethod) | `_probe_port` (env-var I/O only) | Policy and I/O separated per D-02 |
| Frame decode orchestration | `codec.decode_id_frame` (free function) | `SerialCommunicator._decode_id_frame` (thin wrapper) | codec.py is the frame-decode charterowner; wrapper preserves test API |
| Binary byte-stream reading | `SerialCommunicator._read_and_parse_lines` (ring-fenced) | — | Generator body is the GATE-1.8d baseline; no movement |
| Text-line parsing + logging | `SerialCommunicator._parse_response_line` / `_log_rurp_feedback` | — | Transport concern per D-09; stays in serial_comm |
| Port discovery + connection | `SerialCommunicator._probe_port` / `find_and_connect` / `_list_potential_ports` | — | Socket lifecycle belongs in serial_comm |

---

## Key Findings (Verification Results)

### 1. D-05: Multi-branch coupling confirmed CORRECT (with one test-matrix error)

**Verified behavior from live code (lines 647–671):**

```
try:
    major = int(current_version.split(".")[0])
except (ValueError, IndexError):
    major = 0

if major < 3 and os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") != "1":
    raise FirmwareOutdatedError("... is pre-v1.2 ...")    # Branch A

if not SerialCommunicator._is_version_sufficient(current_version, "2.0.0"):
    raise FirmwareOutdatedError("... is outdated ...")    # Branch B (always runs if A skipped)
```

`FIRESTARTER_DEV_ALLOW_PRE_V12=1` sits ONLY inside Branch A's condition. Branch B always executes when Branch A is skipped. **CONTEXT.md's structural claim (D-05 note) is correct: env-var bypasses ONLY the `major < 3` check, NOT the 2.0.0 floor.**

The new `_validate_firmware_version` body therefore follows D-01 exactly: the boolean parameter `allow_pre_v12` guards only Branch A; Branch B (`_is_version_sufficient`) runs unconditionally afterward.

**Test matrix correction:** D-05 lists `"2.9.9"` with `allow_pre_v12=True` as "still raises (2.0.0 floor)". This is incorrect:
- `major = int("2") = 2` → Branch A: `2 < 3 and not True` = False → **skip**
- Branch B: `_is_version_sufficient("2.9.9", "2.0.0")` = `(2,9,9) >= (2,0,0)` = True → **no raise**
- Result: **PASSES** (no FirmwareOutdatedError)

Planner must write the test row as: `"2.9.9"` + `allow_pre_v12=True` → **passes**.

### 2. Line numbers — all verified against live `serial_comm.py`

| CONTEXT.md Reference | Actual Line | Status |
|----------------------|-------------|--------|
| `STATE_MACHINE_PREFIXES :93` | Line 93 | CORRECT |
| `read_line_bytes :164-172` | Lines 164-172 | CORRECT |
| Orphan comment `:64` | Line 64: `# Compile regex for parsing prefixes once for efficiency` | CORRECT |
| Dead comment `:161` | Line 161: `# json_data = json.dumps(command_dict)` | CORRECT |
| Dead comments `:207-209` | Lines 207-209: W-01 STATE_MACHINE_PREFIXES block | CORRECT |
| `_decode_id_frame :226-334` | Def at line 226, closing paren at line 334 | CORRECT |
| `_read_and_parse_lines :336` | Line 336 | CORRECT |
| `_is_version_sufficient :573-593` | `@staticmethod` decorator at 573, body ends at 593 | CORRECT (decorator at 573, def at 574) |
| `_probe_port :638-686` | `_probe_port` **starts at line 595** (decorator at 595); version-guard **logic** is at lines 638–686 | CONTEXT.md's `:638-686` refers to the version-guard block within `_probe_port`, not the method start. Both correct in their stated context. |
| `imports :16` | Line 16: `from typing import Generator, List, Optional, Tuple  # noqa: UP035` | CORRECT |

**Note on `_probe_port` lines:** `@staticmethod` is at line 595, `def _probe_port` at 596. The CONTEXT.md `:638-686` refers specifically to the `try/if fw_msg ... except` version-guard block that `_validate_firmware_version` will absorb. The planner should reference both: "method starts at 595, guard block at 638-686".

### 3. Caller verification (zero external callers confirmed)

**`STATE_MACHINE_PREFIXES`:** [VERIFIED] One definition at `serial_comm.py:93`, zero imports in `firestarter_app/firestarter/`, zero imports in `firestarter_app/tests/`. [ASSUMED] Not imported in `firestarter/` (firmware sub-repo not searched, but CLAUDE.md confirms they're distinct repos with no cross-Python imports).

**`read_line_bytes`:** [VERIFIED] One definition at `serial_comm.py:164`, zero callers in `firestarter_app/firestarter/`, zero callers in `firestarter_app/tests/`. The `CONCERNS.md` at `.planning/codebase/CONCERNS.md:62` notes this method's design flaw (polling `in_waiting`) — reinforces that deletion is the right call.

### 4. FirmwareOutdatedError message strings (byte-identical preservation required)

The following strings are pinned by `test_fwguard.py` assertions (lines 68-70). The new `_validate_firmware_version` must raise with these exact messages:

**Branch A (pre-v1.2 / major < 3):**
```
f"Firmware version {current_version} is pre-v1.2 (text-format logging). "
f"This host expects v1.2+ firmware emitting ID-encoded log frames. "
f"Please upgrade the firmware to v3.0.0 or later using 'firestarter fw --install'. "
f"(No fallback to text-format protocol — the host and firmware must be upgraded together; "
f'see PROJECT.md "Constraints".)'
```
`test_fwguard.py` asserts: `"pre-v1.2" in str(exc)`, `"firestarter fw --install" in str(exc)`, `"v3.0.0 or later" in str(exc)`.

**Branch B (2.0.0 floor):**
```
f"Firmware version {current_version} is outdated. "
f"Version 2.0.0 or higher is required. "
f"Please upgrade the firmware using 'firestarter fw --install'."
```

**Paths that remain in `_probe_port` (D-04):**
- `"Could not parse firmware version from programmer response. Please upgrade..."` (no-regex-match path at line 673)
- `"Firmware is outdated (pre-2.0.0). Please upgrade..."` (no-"FW:" path at line 678)
- `"Could not determine firmware version. Please upgrade..."` (IndexError/AttributeError path at line 683)

### 5. `test_decoder.py` call sites — all keyword arguments confirmed

All 4 call sites at lines 85, 150, 235, 308 use `frame_len=..., body=...` as keyword arguments. The thin wrapper `def _decode_id_frame(self, frame_len, body): return codec.decode_id_frame(frame_len, body)` preserves these exactly. No changes to `test_decoder.py` are needed or allowed.

### 6. codec.py import gap: NOT "zero new import edges" (CONTEXT.md claim is partly wrong)

CONTEXT.md D-07 states: "codec.py already imports CATALOG / MSG_DATA_CHUNK / SEVERITY_LABEL from messages.py and the `_decode_param` primitive from frame_parser — natural home, no new import edges."

**Live file reveals:**
- `_decode_param` from `frame_parser` — **already imported** (line 24)
- `MSG_DATA_CHUNK` from `messages` — **already imported** (line 28)
- `CATALOG` from `messages` — **NOT imported** (only `DEBUG_CATALOG` is)
- `SEVERITY_LABEL` from `messages` — **NOT imported**
- `_crc8_ccitt` from `frame_parser` — **NOT imported**
- `LogMessage` from `frame_parser` — **NOT imported** (needed for return type annotation)

**Wave 2 must add to codec.py's import blocks:**
```python
# From frame_parser (expand existing import line):
from firestarter.frame_parser import _crc8_ccitt, _decode_param, LogMessage

# From messages (expand existing import line):
from firestarter.messages import (
    CATALOG,
    ...(existing)...,
    MSG_DATA_CHUNK,
    SEVERITY_LABEL,
)
```

**No import cycles:** `frame_parser.py` is stdlib-only; `messages.py` is `dataclasses` + `typing` only. Adding these imports to `codec.py` introduces no cycle.

**The "no new import edges" claim from CONTEXT.md is inaccurate.** These are genuine new edges. The statement should read: "no new cross-module boundaries — codec.py already imports from both frame_parser and messages, so these additions extend existing edges rather than introducing new modules." This doesn't change D-06 or D-07's rationale, but the planner must schedule the import additions explicitly.

### 7. `"3.0.0-dev"` alpha-suffix test case — planner decision required

CONTEXT.md D-05 test matrix: `"3.0.0-dev"` (alpha suffix path — `int("3")` works) → return None.

**Tracing the live code logic:**
- `major = int("3.0.0-dev".split(".")[0]) = int("3") = 3` → Branch A condition false → skip
- `_is_version_sufficient("3.0.0-dev", "2.0.0")`: splits on `.` → `["3", "0", "0-dev"]` → `int("0-dev")` → ValueError → returns False → **Branch B raises**

**In production this never fires:** the `_probe_port` regex `r"FW:\s*([\d.x]+)"` strips `-dev` before parsing (tested: `"FW: 3.0.0-dev"` → match captures `"3.0.0"`). So `_validate_firmware_version` would receive `"3.0.0"`, not `"3.0.0-dev"`. The test case is purely a unit-test edge case.

**Planner must choose one:**

Option A (Recommended — matches D-05 intent, behavior change documented):
- Strip a trailing `-.*` alpha suffix in `_validate_firmware_version` before calling `_is_version_sufficient`. Example: `version_str.split("-")[0]` or `re.sub(r"-.*$", "", version_str)`. Document as minor intentional behavior change (per GATE-1.8 "fix bugs found" allowance). Test: `"3.0.0-dev"` → passes.

Option B (Byte-identical preserve):
- Leave `_is_version_sufficient` call unchanged. Document that `"3.0.0-dev"` raises the 2.0.0-floor error. Correct D-05 test matrix row to expect raises. No behavior change from current `_probe_port` (which never receives the suffix anyway).

**Research recommends Option A** since D-05 explicitly states the intent is "return None" and the alpha-suffix case is a plausible direct-call scenario in future test harnesses or CI pipelines.

### 8. Phase 36 safety net — snapshot inventory and current test baseline

**Snapshots:** The one snapshot file is `firestarter_app/tests/__snapshots__/test_characterization.ambr`. It contains **29 snapshots** from `test_characterization.py`:
- CLI help surfaces (--help, subcommand --help) — 14 snapshots
- DB-backed commands (list, info, search) — 3 snapshots + 1 stderr snapshot
- Usage/parse error outputs — 7 snapshots
- `test_no_blank_check_polarity` — 1 snapshot

**None of these snapshots are touched by Phase 40.** All 29 snapshot tests cover subprocess CLI output — none involve `_validate_firmware_version`, `_decode_id_frame`, or `STATE_MACHINE_PREFIXES`. The version-guard behavior is pinned by `test_fwguard.py` (4 tests, behavioral assertions) — NOT by snapshots.

**Current suite baseline (as of 2026-05-28, post-Phase-39):**
- **186 passed + 2 xfailed + 29 snapshots** (Phase 36 safety net as cited in CONTEXT.md was 162 passed — Phase 39 added 24 more tests)
- 2 xfail: `test_build_arg_flags_force_truthiness_not_existence` + `test_eprom_operation_error_not_labeled_as_communication_error` (both strict=True, Phase 41/42 scope)

### 9. D-17 type-hint baseline verification

All 7 methods listed in D-17 as needing `-> None` confirmed missing in live code:

| Method | Line | Current | Needs |
|--------|------|---------|-------|
| `__init__` | 106 | no return hint | `-> None` |
| `_log_rurp_feedback` | 201 | `(self, response: Response):` | `-> None` |
| `send_ack` | 492 | `(self):` | `-> None` |
| `send_done` | 495 | `(self):` | `-> None` |
| `consume_remaining_input` | 498 | `(self, timeout: float = 0.5):` | `-> None` |
| `disconnect` | 513 | `(self):` | `-> None` |
| `_log_command_details` | 525 | `(self, command_dict: dict):` | `-> None` |

The following D-17 ✓ methods are confirmed already annotated: `is_connected`, `send_bytes`, `send_string`, `send_json_command`, `_parse_response_line`, `_decode_id_frame`, `_read_and_parse_lines`, `get_response`, `expect_ack`, `_list_potential_ports`, `_is_version_sufficient`, `_probe_port`, `find_and_connect`.

Note: `read_line_bytes` (line 164) is annotated `-> Optional[bytes]` but is deleted in Wave 3 — no annotation work needed on it.

---

## Architecture Patterns

### Wave Dependency Safety

```
Wave 1: Extract _validate_firmware_version @staticmethod
  └── Pure addition to serial_comm.py; _probe_port repointed; new test file
  └── No dependency on Wave 2 (decode_id_frame unchanged), Wave 3, or Wave 4
  └── test_decoder.py: unchanged; test_fwguard.py: must still pass

Wave 2: Extract _decode_id_frame body to codec.decode_id_frame
  └── Requires Wave 1 to be committed (cleaner diff, but technically independent)
  └── codec.py gains decode_id_frame + new imports (CATALOG, SEVERITY_LABEL,
      _crc8_ccitt, LogMessage); serial_comm._decode_id_frame becomes 1-line wrapper
  └── test_decoder.py: must pass UNCHANGED (SC#3)

Wave 3: Dead-code sweep
  └── Requires Wave 1+2 (STATE_MACHINE_PREFIXES comment at 207-209 refers to
      the constant deleted here; cleaner in its own wave)
  └── Delete STATE_MACHINE_PREFIXES (93), read_line_bytes (164-172),
      orphan comments (64, 161, 207-209)
  └── ruff must be clean after deletion

Wave 4: Ring-fence marker + return hints
  └── Requires Wave 1+2+3 committed (adds comment above _read_and_parse_lines;
      the read_line_bytes deletion in Wave 3 must precede annotation work to
      avoid annotating a method about to be deleted)
  └── _read_and_parse_lines generator body: byte-identical
  └── 7x -> None annotations + new _validate_firmware_version signature
```

D-12 note: The Wave 3 dead comment at lines 207-209 references `STATE_MACHINE_PREFIXES` — its deletion is slightly cleaner if `STATE_MACHINE_PREFIXES` is already gone (Wave 3 handles both together, which is correct).

Waves 3+4 MAY fold into one commit if the diff is reviewable (per CONTEXT.md). The planner may optionally merge them.

### Recommended Project Structure (no new files except one test)

```
firestarter_app/
├── firestarter/
│   ├── serial_comm.py   # primary edit: 4 waves of changes
│   └── codec.py         # Wave 2: +decode_id_frame free function + new imports
└── tests/
    └── test_fw_version_guard.py  # Wave 1: new file, unit tests for _validate_firmware_version
```

### Pattern: Thin Wrapper for Test Compatibility

The precedent from Phase 38 D-07 (re-export block in `serial_comm.py` for `test_decoder.py`):

```python
# Phase 38 pattern (lines 42-47):
from firestarter.frame_parser import (  # noqa: F401 — re-exports for test_decoder.py
    MAGIC_PREAMBLE,
    LogMessage,
    Response,
    _crc8_ccitt,
    _decode_param,
)
```

The Phase 40 thin wrapper follows the same rationale:

```python
# Wave 2 pattern: one-line method wrapper (no noqa needed, it's not an import)
def _decode_id_frame(self, frame_len: int, body: bytes) -> Optional[LogMessage]:
    """Compatibility wrapper — see codec.decode_id_frame."""
    return codec.decode_id_frame(frame_len, body)
```

The generator body's call site at line 436 stays byte-identical (`self._decode_id_frame(frame_len, body)`).

### Pattern: Version Guard Extraction

Current `_probe_port` (lines 638-686, condensed):

```python
try:
    major = int(current_version.split(".")[0])
except (ValueError, IndexError):
    major = 0
if major < 3 and os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") != "1":
    raise FirmwareOutdatedError("... pre-v1.2 ...")
if not SerialCommunicator._is_version_sufficient(current_version, "2.0.0"):
    raise FirmwareOutdatedError("... outdated ...")
```

New `_validate_firmware_version` body (D-01/D-02):

```python
@staticmethod
def _validate_firmware_version(
    version_str: str, allow_pre_v12: bool = False
) -> None:
    try:
        major = int(version_str.split(".")[0])
    except (ValueError, IndexError):
        major = 0
    if major < 3 and not allow_pre_v12:
        raise FirmwareOutdatedError(
            f"Firmware version {version_str} is pre-v1.2 (text-format logging). "
            ...  # exact message from live code
        )
    if not SerialCommunicator._is_version_sufficient(version_str, "2.0.0"):
        raise FirmwareOutdatedError(
            f"Firmware version {version_str} is outdated. "
            ...  # exact message from live code
        )
```

`_probe_port` replacement block (after regex match, before 2.0.0-floor check):

```python
allow_pre_v12 = os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") == "1"
SerialCommunicator._validate_firmware_version(current_version, allow_pre_v12=allow_pre_v12)
```

### Pattern: decode_id_frame in codec.py

Insert after `format_message` function. Add the breadcrumb docstring per D-08:

```python
def decode_id_frame(frame_len: int, body: bytes) -> Optional[LogMessage]:
    """Decode an ID-encoded wire frame body...
    
    [Read-path-adjacent — behavior preserved verbatim from serial_comm.py per
    GATE-1.8d. Do not refactor without re-validating Phase 26 baseline binaries.]
    """
    # [body of _decode_id_frame migrated verbatim from serial_comm.py:227-334]
```

### Anti-Patterns to Avoid

- **Modernizing `Optional[X]` to `X | None`:** Phase 37 D-08 locked py39 floor. The existing `# noqa: UP006` / `# noqa: UP035` at line 16 stay.
- **Touching `_read_and_parse_lines` generator body:** Any byte-level change breaks GATE-1.8a/d. Only the comment block above the `def` and the docstring first line are modified.
- **Ring-fencing callees** (`_decode_id_frame`, `_parse_response_line`, `_log_rurp_feedback`): D-16 explicitly forbids marker inflation.
- **Letting `test_decoder.py` fail:** The thin wrapper existence is GATED by `test_decoder.py` passing unchanged. Do not merge Wave 2 with a failing test_decoder.py.
- **Putting env-var read in `_validate_firmware_version`:** D-02 is explicit — env I/O stays in `_probe_port`; the staticmethod is pure.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Version comparison | Custom tuple comparison | `_is_version_sufficient` (already exists as @staticmethod) | Edge cases: `"x"` placeholder handling, empty strings, single-segment versions |
| FirmwareOutdatedError class | New exception | `firestarter.exceptions.FirmwareOutdatedError` (Phase 38 extracted, stable) | Already imported in serial_comm.py:36 |
| Test isolation for env-var | `os.environ` monkeypatching in every test | `pytest.fixture(autouse=True)` with `monkeypatch.delenv` | Established pattern in `test_fwguard.py` — copy it into `test_fw_version_guard.py` |

---

## Common Pitfalls

### Pitfall 1: Forgetting the 3 "stays in _probe_port" FirmwareOutdatedError paths

**What goes wrong:** The planner lists "move version-guard to `_validate_firmware_version`" and the implementer moves ALL 5 `FirmwareOutdatedError` raises out of `_probe_port`, leaving a missing-FW-response scenario unguarded.

**Why it happens:** D-01 says "owns ALL version-guard logic" but D-04 carves out the "Could not parse FW message" paths as transport concern.

**How to avoid:** Plan task explicitly states: only the `try/if major < 3/if not _is_version_sufficient` block (lines 647-671) migrates. Lines 672-686 (no-match, no-"FW:", IndexError/AttributeError) stay in `_probe_port`.

**Warning signs:** `_probe_port` has fewer than 5 `FirmwareOutdatedError` references after Wave 1.

### Pitfall 2: Breaking `test_fwguard.py` in Wave 1

**What goes wrong:** `_probe_port` is refactored to call `_validate_firmware_version`; `test_fwguard.py` patches `expect_ack` to return `"FW: 2.0.11, ..."` — if the regex extraction or version parsing changes, the patched return value must still trigger the guard.

**Why it happens:** `test_fwguard.py` mocks at the `expect_ack` level, so the regex parse, env-var read, and guard logic all still execute. Any change to those paths breaks the test.

**How to avoid:** Wave 1 acceptance test explicitly includes `pytest tests/test_fwguard.py -v` (integration path) AND `pytest tests/test_fw_version_guard.py -v` (new unit path).

### Pitfall 3: codec.py missing imports cause Wave 2 NameError

**What goes wrong:** `decode_id_frame` body references `CATALOG`, `SEVERITY_LABEL`, `_crc8_ccitt`, `LogMessage` — none currently in codec.py. If the implementer copies the body without adding imports, the module imports without error (Python doesn't validate function bodies at import time) but the function raises `NameError` at call time.

**Why it happens:** CONTEXT.md's "no new import edges" claim misled the scout; the gap is documented in §6 above.

**How to avoid:** Wave 2 plan task explicitly lists the 4 imports to add. Wave 2 acceptance test runs `test_decoder.py` which exercises `decode_id_frame` at call time (not just import time).

### Pitfall 4: `"2.9.9" + allow_pre_v12=True` test case written as "raises"

**What goes wrong:** D-05 test matrix says this raises; implementation writes the test that way; the test passes because the test expectation is wrong. Later, when a dev bench-tests v2.x firmware with the env-var set, `_validate_firmware_version("2.9.9", allow_pre_v12=True)` returns None (no raise) but the test had never caught this.

**How to avoid:** Write the test as `assert` (no exception) for `"2.9.9" + allow_pre_v12=True`. See §1 above.

### Pitfall 5: Ring-fence comment placement wrong

**What goes wrong:** Comment block placed INSIDE the function body (as a docstring continuation or top-of-body comment) instead of IMMEDIATELY ABOVE the `def`. Grep-friendliness is lost; blame history does not show the marker on diff of the body.

**How to avoid:** D-15 is explicit: "immediately above `def _read_and_parse_lines`". Example:
```
# =================================================================
# DO NOT MODIFY — v1.9 RCA territory (GATE-1.8d)
# ...
# =================================================================
def _read_and_parse_lines(self, timeout: float) -> Generator[Response, None, None]:
    """[ring-fenced — v1.9 RCA territory; see header comment] Always-on byte-stream reader..."""
```

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 + syrupy 5.2.0 |
| Config file | `firestarter_app/pyproject.toml` |
| Quick run | `pytest firestarter_app/tests/test_decoder.py firestarter_app/tests/test_fw_version_guard.py -v` |
| Full suite | `pytest firestarter_app/tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SERIAL-02 | `_validate_firmware_version("3.0.0")` → None | unit | `pytest tests/test_fw_version_guard.py -v` | ❌ Wave 1 |
| SERIAL-02 | `_validate_firmware_version("2.9.9")` → FirmwareOutdatedError | unit | `pytest tests/test_fw_version_guard.py -v` | ❌ Wave 1 |
| SERIAL-02 | `_validate_firmware_version("abc")` → FirmwareOutdatedError (major=0) | unit | `pytest tests/test_fw_version_guard.py -v` | ❌ Wave 1 |
| SERIAL-02 | `_validate_firmware_version("1.0.0", allow_pre_v12=True)` → FirmwareOutdatedError | unit | `pytest tests/test_fw_version_guard.py -v` | ❌ Wave 1 |
| SERIAL-02 | `_validate_firmware_version("2.9.9", allow_pre_v12=True)` → None (CORRECTED) | unit | `pytest tests/test_fw_version_guard.py -v` | ❌ Wave 1 |
| SERIAL-02 | `_probe_port` still raises FirmwareOutdatedError pre-v1.2 path | integration | `pytest tests/test_fwguard.py -v` | ✅ Exists |
| SERIAL-01 | `codec.decode_id_frame` importable; thin wrapper works | unit | `pytest tests/test_decoder.py -v` | ✅ Exists (unchanged) |
| SERIAL-03 | `_read_and_parse_lines` body byte-identical | behavioral | `pytest tests/test_decoder.py tests/test_serial_characterization.py -v` | ✅ Exists (unchanged) |
| SERIAL-01 | Dead code absent: `STATE_MACHINE_PREFIXES`, `read_line_bytes` | lint/grep | `grep -n "STATE_MACHINE_PREFIXES\|read_line_bytes" firestarter/serial_comm.py` | N/A |
| SERIAL-03 | Ring-fence marker present above `_read_and_parse_lines` | grep | `grep -n "DO NOT MODIFY" firestarter/serial_comm.py` | N/A |
| SERIAL-03 | All public methods have `->` return hints | mypy | `mypy firestarter/serial_comm.py` | N/A |

### Per-Wave Acceptance Criteria

**Wave 1 Acceptance:**
- `pytest firestarter_app/tests/test_fw_version_guard.py -v` exits 0 (new file, all rows pass)
- `pytest firestarter_app/tests/test_fwguard.py -v` exits 0 (existing integration tests unchanged)
- `_probe_port` still raises `FirmwareOutdatedError` on both pre-v1.2 and outdated-2.x paths
- All 29 snapshots green
- Full suite exits 0 (186 passed + 2 xfailed)

**Wave 2 Acceptance:**
- `pytest firestarter_app/tests/test_decoder.py -v` exits 0 UNCHANGED (SC#3)
- `python3 -c "from firestarter.codec import decode_id_frame; print('OK')"` exits 0
- `python3 -c "from firestarter.serial_comm import SerialCommunicator; c = SerialCommunicator.__new__(SerialCommunicator); c._decode_id_frame(2, b'\x01\x07')"` works (thin wrapper)
- Full suite exits 0

**Wave 3 Acceptance:**
- `grep -n "STATE_MACHINE_PREFIXES\|read_line_bytes" firestarter_app/firestarter/serial_comm.py` → zero hits
- `ruff check firestarter_app/firestarter/serial_comm.py` → clean
- Full suite exits 0

**Wave 4 Acceptance:**
- `grep -n "DO NOT MODIFY" firestarter_app/firestarter/serial_comm.py` → line immediately above `def _read_and_parse_lines`
- `_read_and_parse_lines` generator body byte-identical to Wave 3 HEAD (verify with `git diff HEAD~1 -- firestarter_app/firestarter/serial_comm.py | grep "^+" | grep -v "^+#\|^+++"` — only comment and docstring-first-line additions expected)
- `grep -n "def.*self.*[^:)]*)" firestarter_app/firestarter/serial_comm.py | grep -v "-> "` → zero hits for public methods
- Full suite exits 0
- `mypy firestarter_app/firestarter/serial_comm.py` error count does NOT increase vs Wave 3 baseline

### Wave 0 Gaps

- [ ] `firestarter_app/tests/test_fw_version_guard.py` — NEW file covering SERIAL-02 (Wave 1)

---

## Environment Availability

Step 2.6: All relevant tools are in-container. No external dependencies for this phase.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | Runtime | ✓ | 3.12.13 | — |
| pytest | Test suite | ✓ | 9.0.3 | — |
| ruff | Lint gate | ✓ | (installed via pyproject.toml) | — |
| mypy | Type-hint gate | ✓ | (installed via pyproject.toml) | — |

No missing dependencies.

---

## Runtime State Inventory

Step 2.5: SKIPPED — Phase 40 is a structural refactoring (rename/extract), not a rename/migration of user-visible strings. No database keys, live service config, OS registrations, secrets, or build artifacts embed `_decode_id_frame`, `_validate_firmware_version`, `STATE_MACHINE_PREFIXES`, or `read_line_bytes` as stored strings. The changes are Python source-only.

---

## Security Domain

`security_enforcement` key is absent from `.planning/config.json` (treated as enabled). However, Phase 40 makes no changes to authentication, session management, access control, cryptography, or input validation surfaces:

- The firmware version string comparison is an extraction (same logic, same bounds), not a new input path.
- No new external inputs are introduced.
- `FirmwareOutdatedError` message strings are internal — not exposed to web surfaces.

ASVS categories V2, V3, V4, V6 are not applicable. V5 (input validation) is nominally applicable to the version string parse, but:
- The regex `r"FW:\s*([\d.x]+)"` is unchanged (stays in `_probe_port`)
- The `_validate_firmware_version` staticmethod receives the already-regex-extracted string

No security findings for this phase.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `firestarter/` firmware sub-repo contains no Python files that import `STATE_MACHINE_PREFIXES` or `read_line_bytes` | §3 Caller verification | Low — repos are distinctly Python vs C++; cross-Python imports between them are architecturally impossible per CLAUDE.md |

All other claims were verified against live source files.

---

## Open Questions (RESOLVED)

1. **`"3.0.0-dev"` test case behavior (§7 above)**
   - What we know: In production the regex strips `-dev`; direct calls to `_validate_firmware_version("3.0.0-dev")` would raise the 2.0.0 floor error with current `_is_version_sufficient`.
   - What's unclear: D-05 says "return None" (pass); current logic says raise.
   - Recommendation: Option A (strip alpha suffix) — add `version_str = re.sub(r"-.*$", "", version_str)` before the major extraction. Document as intentional behavior fix in commit message. Low risk since the production path never sends the suffix.
   - RESOLVED: Option A chosen — alpha-suffix strip via `re.sub(r"-.*$","",version_str)` in 40-01 Task 40-01-01 action. Production wire behavior unchanged (the `_probe_port` regex already strips `-dev`); documented as intentional behavior fix per GATE-1.8.

2. **`"2.9.9" + allow_pre_v12=True` test row (§1 above)**
   - What we know: This PASSES (no raise). CONTEXT.md test matrix says "raises".
   - What's unclear: Nothing — the code is unambiguous.
   - Recommendation: Write the test row as `assert` (no exception expected). No operator consultation needed.
   - RESOLVED: passes (no FirmwareOutdatedError raised). 40-01 Task 40-01-03 writes the test row as no-raise. Corrected from CONTEXT.md D-05 matrix per code trace in §1.

---

## Sources

### Primary (HIGH confidence)
- Live `firestarter_app/firestarter/serial_comm.py` — all line numbers, logic traces, annotation gaps verified by direct read and Python execution [VERIFIED: codebase]
- Live `firestarter_app/firestarter/codec.py` — import inventory verified [VERIFIED: codebase]
- Live `firestarter_app/firestarter/frame_parser.py` — stdlib-only verified [VERIFIED: codebase]
- Live `firestarter_app/tests/test_decoder.py` — 4 call sites at lines 85, 150, 235, 308 verified [VERIFIED: codebase]
- Live `firestarter_app/tests/test_fwguard.py` — message string assertions at lines 68-70 verified [VERIFIED: codebase]
- `pytest firestarter_app/tests/ -v` — 186 passed + 2 xfailed + 29 snapshots baseline confirmed [VERIFIED: test run]

### Secondary (MEDIUM confidence)
- `.planning/phases/40-serial-transport-restructure/40-CONTEXT.md` — locked decisions reference [CITED: local planning artifact]
- `.planning/REQUIREMENTS.md` — SERIAL-01..03, GATE-1.8(a-e) [CITED: local planning artifact]

---

## Metadata

**Confidence breakdown:**
- Line number verification: HIGH — read directly from source
- D-05 multi-branch behavior: HIGH — traced in Python interpreter with live logic
- codec.py import gap: HIGH — grepped and cross-referenced against _decode_id_frame body dependencies
- D-17 annotation gaps: HIGH — automated script checked all method signatures
- Test matrix corrections: HIGH — executed `_is_version_sufficient` with the relevant inputs

**Research date:** 2026-05-28
**Valid until:** 2026-06-28 (stable codebase; no external dependencies)

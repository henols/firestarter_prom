# Phase 40: Serial / Transport Restructure - Pattern Map

**Mapped:** 2026-05-28
**Files analyzed:** 3 (2 modified, 1 new)
**Analogs found:** 3 / 3

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/firestarter/serial_comm.py` | transport / service | request-response + streaming | itself (prior-phase precedents: Phase 38 D-14/D-16 dead-code sweep; Phase 38 D-07 re-export block; `_is_version_sufficient` @staticmethod) | self-analog (restructure, not replace) |
| `firestarter_app/firestarter/codec.py` | utility / transform | transform (decode) | `codec.format_message` (lines 51–160 in same file) | exact-role, same file |
| `firestarter_app/tests/test_fw_version_guard.py` | test | unit (pure-function, no I/O) | `firestarter_app/tests/test_fwguard.py` (integration-style version-guard tests) | role-match with deliberate deviation |

---

## Pattern Assignments

### `firestarter_app/firestarter/serial_comm.py` (transport service — restructure)

This file is its own primary analog. Each operation in Phase 40 extends a prior-phase precedent.

---

#### Operation A — Dead-code sweep (Wave 3, D-10/D-11/D-12)

**Analog precedent:** Phase 38 D-14 (`read_data_block` deletion) and D-16 (orphan comment removal).

**Items to delete — exact locations verified:**

| Item | Line(s) | Kind |
|------|---------|------|
| `STATE_MACHINE_PREFIXES = []` | 93 | dead constant (empty since Phase 8 W-01; zero callers) |
| `read_line_bytes` method | 164–172 | dead transport helper (zero callers; annotated `-> Optional[bytes]`) |
| Orphan comment `# Compile regex...` | 64 | orphan header (no following code) |
| Dead comment `# json_data = json.dumps(...)` | 161 | commented-out alternative |
| W-01 STATE_MACHINE_PREFIXES block | 207–209 | dead-pointing comment inside `_log_rurp_feedback` |

**Keep pattern (Phase 38 D-13/D-14 precedent):**
- `PREFIX_REGEX` rationale block (lines 82–90) — documents live Uno USB-CDC garbage-prefix workaround
- F401 re-export comment block (lines 42–47) — documents live `test_decoder.py` back-compat contract

**Re-export block to preserve** (lines 42–53):
```python
# Re-exports for backward compatibility — test_decoder.py imports MAGIC_PREAMBLE,
# LogMessage, Response, _crc8_ccitt directly from firestarter.serial_comm and must
# keep passing UNCHANGED (SC#2 / D-07). The canonical definitions now live in
# frame_parser.py (D-05). _decode_param is also pulled in so _format_message /
# _decode_id_frame in this module resolve it via the new leaf.
from firestarter.frame_parser import (  # noqa: F401  — re-exports for test_decoder.py
    MAGIC_PREAMBLE,
    LogMessage,
    Response,
    _crc8_ccitt,
    _decode_param,
)
```

---

#### Operation B — `_decode_id_frame` thin wrapper (Wave 2, D-06/D-07)

**Analog precedent:** Phase 38 D-07 re-export block (lines 42–53 above) — same "test_decoder.py back-compat" rationale. The method wrapper is the method-level equivalent of the import-level re-export.

**Current method body** (lines 226–334): the entire existing `_decode_id_frame` implementation migrates verbatim to `codec.decode_id_frame`. Only the method body changes; signature and docstring header stay.

**Thin wrapper pattern** (D-06 — what the method becomes after Wave 2):
```python
def _decode_id_frame(self, frame_len: int, body: bytes) -> Optional[LogMessage]:
    """Compatibility wrapper — see codec.decode_id_frame."""
    return codec.decode_id_frame(frame_len, body)
```

**Call site that stays byte-identical** (line 436, inside `_read_and_parse_lines` generator body):
```python
self._decode_id_frame(frame_len, body)
```
The generator body's call site is NOT modified (GATE-1.8a/d).

**Deviation flag:** This reverses Phase 38 D-06's "keep as method" decision, which explicitly deferred the final disposition to Phase 40 SC#1. The extraction is the closing of that deferred thread, not a contradiction.

---

#### Operation C — Ring-fence comment above `_read_and_parse_lines` (Wave 4, D-15)

**Analog precedent:** Phase 38 D-09 scoped GATE-1.8d to the generator body. D-15 adds the marker.

**Exact placement** (immediately above `def _read_and_parse_lines`, currently at line 336):
```python
# =================================================================
# DO NOT MODIFY — v1.9 RCA territory (GATE-1.8d)
# The body of this generator is the host-side baseline for v1.9's
# read-bug RCA. Phase 26 baseline binaries (.planning/v1.6/
# consistency-check-runs/W27C512-leonardo-20260526-*-v2*/) were
# captured against this exact body. Structural-only changes here
# (e.g. type hints on the signature) are OK; any change to the
# byte-by-byte read loop, the magic-preamble dispatch, the
# frame-length read, or the timeout reset semantics MUST be
# flagged and deferred to v1.9 alongside binary re-validation.
# =================================================================
def _read_and_parse_lines(self, timeout: float) -> Generator[Response, None, None]:
    """[ring-fenced — v1.9 RCA territory; see header comment] Always-on byte-stream reader...
```

**Do NOT ring-fence** `_decode_id_frame`, `_parse_response_line`, or `_log_rurp_feedback` — D-16 explicitly forbids marker inflation.

---

#### Operation D — `_validate_firmware_version` @staticmethod (Wave 1, D-01/D-02)

**Analog precedent:** `_is_version_sufficient` @staticmethod (lines 573–593) — already a pure-policy `@staticmethod` with no I/O; reusable as internal helper inside the new method.

**Existing analog to copy shape from** (lines 573–593):
```python
@staticmethod
def _is_version_sufficient(
    current_version_str: str, required_version_str: str
) -> bool:
    """Compares two version strings. Returns True if current >= required."""
    if not current_version_str or not required_version_str:
        return False
    try:
        current = tuple(
            map(int, current_version_str.lower().replace("x", "999").split("."))
        )
        ...
    except (ValueError, AttributeError):
        ...
        return False
```

**Source block to migrate** (version-guard block extracted from `_probe_port`, lines 638–686):
```python
# Lines 647-671: the try/if major < 3/if not _is_version_sufficient block
try:
    major = int(current_version.split(".")[0])
except (ValueError, IndexError):
    major = 0
if (
    major < 3
    and os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") != "1"
):
    raise FirmwareOutdatedError(
        f"Firmware version {current_version} is pre-v1.2 (text-format logging). "
        ...
    )
if not SerialCommunicator._is_version_sufficient(current_version, "2.0.0"):
    raise FirmwareOutdatedError(
        f"Firmware version {current_version} is outdated. "
        ...
    )
```

**Replacement in `_probe_port`** (after `current_version = match.group(1).strip()` at line 642):
```python
allow_pre_v12 = os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") == "1"
SerialCommunicator._validate_firmware_version(current_version, allow_pre_v12=allow_pre_v12)
```

**Three `_probe_port` raises that STAY in `_probe_port`** (D-04, lines 673–686):
- no-regex-match path (line 673): `"Could not parse firmware version from programmer response..."`
- no-"FW:" path (line 678): `"Firmware is outdated (pre-2.0.0)..."`
- IndexError/AttributeError path (line 683): `"Could not determine firmware version..."`

**FirmwareOutdatedError message strings pinned by `test_fwguard.py` lines 68–70** (must be byte-identical in the new staticmethod):
- Branch A: must contain `"pre-v1.2"`, `"firestarter fw --install"`, `"v3.0.0 or later"`
- Branch B: must contain `"outdated"`, `"2.0.0 or higher"`, `"firestarter fw --install"`

---

#### Operation E — Missing `-> None` return hints (Wave 4, D-17)

**7 methods confirmed missing `-> None` in live code:**

| Method | Line | Current signature |
|--------|------|-------------------|
| `__init__` | 106 | `(self, port: str, baud_rate: int = ..., timeout: float = ...):` |
| `_log_rurp_feedback` | 201 | `(self, response: Response):` |
| `send_ack` | 492 | `(self):` |
| `send_done` | 495 | `(self):` |
| `consume_remaining_input` | 498 | `(self, timeout: float = 0.5):` |
| `disconnect` | 513 | `(self):` |
| `_log_command_details` | 525 | `(self, command_dict: dict):` |

**Style constraint:** Use legacy `Optional[X]` / `List[X]` / `Tuple[X,Y]` syntax (Phase 37 D-08). Do NOT use `X | None`. The existing `# noqa: UP035` at line 16 stays.

---

### `firestarter_app/firestarter/codec.py` (utility / transform — new free function)

**Analog:** `format_message` function in the same file (lines 51–160).

**Import block pattern** (lines 1–35, the shape the expanded import block must follow):
```python
from firestarter.frame_parser import _decode_param
from firestarter.messages import (
    DBG_CMD,
    DEBUG_CATALOG,
    MSG_DATA_CHUNK,
    ...
)
```

**Gap — 4 imports NOT yet in codec.py** (RESEARCH.md §6 correction — Wave 2 must add these explicitly):
```python
# Expand the frame_parser import line (currently line 24):
from firestarter.frame_parser import _crc8_ccitt, _decode_param, LogMessage

# Expand the messages import block (currently lines 25-35):
from firestarter.messages import (
    CATALOG,           # ADD — currently only DEBUG_CATALOG is imported
    ...
    SEVERITY_LABEL,    # ADD
)
```

**Free function shape — copy from `format_message` signature** (line 51):
```python
def format_message(msg_id: int, params: list, entry) -> Optional[str]:
    """Sentinel-aware message renderer..."""
```

**New function follows same shape — free function, no `self`, explicit `Optional` return type:**
```python
def decode_id_frame(frame_len: int, body: bytes) -> Optional[LogMessage]:
    """Decode an ID-encoded wire frame body...

    Read-path-adjacent — behavior preserved verbatim from serial_comm.py per
    GATE-1.8d. Do not refactor without re-validating Phase 26 baseline binaries.
    """
    # [body migrated verbatim from serial_comm._decode_id_frame lines 239-334]
```

**Placement:** Insert after `format_message` (after line 160). Follow file's existing convention of `format_message` first (per RESEARCH.md §Pattern: decode_id_frame in codec.py).

**Body source:** `serial_comm.py` lines 239–334 (the full `_decode_id_frame` implementation, from `if frame_len < 2` through `return LogMessage(...)`). Copy verbatim — no logic changes.

**Deviation flag:** CONTEXT.md D-07 states "no new import edges" — this is inaccurate. Four genuine new imports are required (CATALOG, SEVERITY_LABEL, `_crc8_ccitt`, LogMessage). These extend existing import edges (codec already imports from both frame_parser and messages) but are not pre-existing. Planner must schedule them explicitly in Wave 2.

---

### `firestarter_app/tests/test_fw_version_guard.py` (test — NEW FILE)

**Analog:** `firestarter_app/tests/test_fwguard.py` (integration-style version-guard tests).

**autouse fixture pattern** (copy from `test_fwguard.py` lines 35–43):
```python
@pytest.fixture(autouse=True)
def _clear_escape_hatch(self, monkeypatch):
    """Ensure the dev escape-hatch env var is unset for every test by default.

    Tests that explicitly want it set call `monkeypatch.setenv(...)` AFTER
    this autouse fixture has cleared it; the per-test setenv then overrides
    the delenv for the duration of that single test.
    """
    monkeypatch.delenv("FIRESTARTER_DEV_ALLOW_PRE_V12", raising=False)
```

**Message-fragment assertion pattern** (copy shape from `test_fwguard.py` lines 68–70):
```python
assert "pre-v1.2" in str(exc_info.value)
assert "firestarter fw --install" in str(exc_info.value)
assert "v3.0.0 or later" in str(exc_info.value)
```

**Class header + import pattern** (copy from `test_fwguard.py` lines 25–33):
```python
from firestarter.serial_comm import FirmwareOutdatedError, SerialCommunicator
import pytest

class TestFirmwareVersionGuard:
    """..."""
```

**Deviation flag — NO serial mock in the new file.** The analog (`test_fwguard.py`) mocks at `expect_ack` and calls `_probe_port`:
```python
# test_fwguard.py pattern (NOT used in new file):
with patch.object(SerialCommunicator, "expect_ack", return_value=(True, mock_msg)):
    SerialCommunicator._probe_port(port_name="/dev/null", ...)
```

The new `test_fw_version_guard.py` calls the staticmethod directly — no serial mock, no port, no patch:
```python
# New file pattern:
SerialCommunicator._validate_firmware_version("3.0.0")           # assert no raise
SerialCommunicator._validate_firmware_version("2.9.9")           # assert raises
SerialCommunicator._validate_firmware_version("1.0.0", allow_pre_v12=True)  # assert raises
```

This is intentional per D-02: env-var I/O stays in `_probe_port`; the staticmethod is pure and testable without any environment mock.

**Test matrix for `test_fw_version_guard.py`** (D-05 with RESEARCH.md §1 correction applied):

| `version_str` | `allow_pre_v12` | Expected | Note |
|---------------|-----------------|----------|------|
| `"3.0.0"` | False | passes | normal accept |
| `"3.5.2"` | False | passes | normal accept |
| `"3"` | False | passes | single-segment |
| `"2.9.9"` | False | raises Branch B | 2.x < 3 → Branch A; 2.9.9 ≥ 2.0.0 → no raise? No: major=2 < 3 AND not allow_pre_v12 → Branch A raises |
| `"1.0.0"` | False | raises Branch A | major=1 < 3 |
| `"abc"` | False | raises Branch A | int("abc") fails → major=0 < 3 |
| `""` | False | raises Branch A | int("") fails → major=0 < 3 |
| `"2.9.9"` | True | **passes** | major=2 < 3 but allow_pre_v12=True → Branch A skipped; `_is_version_sufficient("2.9.9","2.0.0")`=True → no raise. CORRECTION: D-05 listed this as "raises" — it does not. |
| `"1.0.0"` | True | raises Branch B | Branch A skipped; `_is_version_sufficient("1.0.0","2.0.0")`=False → Branch B raises |
| `"3.0.0"` | False | passes | confirm allow_pre_v12=False doesn't break 3.x |

**Note on `"3.0.0-dev"` (RESEARCH.md §7):** Planner must choose between Option A (strip alpha suffix in `_validate_firmware_version` so `"3.0.0-dev"` passes) and Option B (leave as-is; `"3.0.0-dev"` raises the 2.0.0 floor). Recommend Option A (`re.sub(r"-.*$", "", version_str)`) since D-05 explicitly states intent is "return None" and production `_probe_port` regex never passes the suffix anyway. Document as intentional behavior fix in commit message.

**Do NOT delete `test_fwguard.py`.** The new file complements it: `test_fwguard.py` covers the integration path through `_probe_port` (mocked at `expect_ack`); `test_fw_version_guard.py` covers the policy staticmethod directly.

---

## Shared Patterns

### @staticmethod policy helper pattern
**Source:** `serial_comm.py` lines 573–593 (`_is_version_sufficient`)
**Apply to:** The new `_validate_firmware_version` staticmethod
```python
@staticmethod
def _is_version_sufficient(
    current_version_str: str, required_version_str: str
) -> bool:
    """Compares two version strings. Returns True if current >= required."""
    ...
    except (ValueError, AttributeError):
        ...
        return False
```
Pattern: pure policy function, no I/O, no env reads, try/except returning a safe default.

### autouse env-var fixture pattern
**Source:** `test_fwguard.py` lines 35–43
**Apply to:** `test_fw_version_guard.py` class fixture
```python
@pytest.fixture(autouse=True)
def _clear_escape_hatch(self, monkeypatch):
    monkeypatch.delenv("FIRESTARTER_DEV_ALLOW_PRE_V12", raising=False)
```
Pattern: autouse=True ensures hermetic env for all tests in the class; per-test `setenv` overrides the delenv.

### Legacy typing style (no modernization)
**Source:** `serial_comm.py` line 16
```python
from typing import Generator, List, Optional, Tuple  # noqa: UP035
```
**Apply to:** All new/modified signatures in `serial_comm.py` and `codec.py`. Use `Optional[X]` not `X | None`; `List[X]` not `list[X]`.

### Free function in codec.py
**Source:** `codec.py` lines 51–160 (`format_message`)
**Apply to:** `decode_id_frame` placement and signature shape
Pattern: module-level free function, no class wrapper, `Optional[ReturnType]` annotation, docstring with behavioral note.

---

## No Analog Found

No files in this phase lack an analog. All three files have clear pattern sources.

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tests/`
**Files scanned:** `serial_comm.py`, `codec.py`, `test_fwguard.py`, `test_decoder.py`
**Pattern extraction date:** 2026-05-28

**Prior-phase context consumed:**
- Phase 38 D-07 re-export block (lines 42–53) — thin-wrapper precedent
- Phase 38 D-14/D-16 dead-code sweep — deletion scope precedent
- Phase 38 D-09 ring-fence scope — callees-not-marked precedent
- Phase 37 D-08 py39 floor — legacy typing style locked

**RESEARCH.md corrections incorporated:**
1. `"2.9.9" + allow_pre_v12=True` → passes (not raises); test matrix row corrected
2. codec.py import gap: CATALOG, SEVERITY_LABEL, `_crc8_ccitt`, LogMessage are NOT yet imported; Wave 2 must add them explicitly
3. `"3.0.0-dev"` decision flagged for planner (Option A recommended: strip alpha suffix)

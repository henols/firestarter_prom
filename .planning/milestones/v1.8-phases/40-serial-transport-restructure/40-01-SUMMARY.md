---
phase: 40-serial-transport-restructure
plan: 01
subsystem: serial / version-guard
tags: [serial, version-guard, refactor, staticmethod, tdd]
requirements: [SERIAL-02]
dependency_graph:
  requires: [SERIAL-01-context-not-yet-complete, _is_version_sufficient @staticmethod]
  provides:
    - SerialCommunicator._validate_firmware_version pure-policy @staticmethod
    - tests/test_fw_version_guard.py unit-test surface
  affects:
    - SerialCommunicator._probe_port (repointed to staticmethod call)
tech_stack:
  added: []
  patterns:
    - "@staticmethod pure-policy helper (analog: _is_version_sufficient)"
    - "autouse monkeypatch.delenv fixture (analog: test_fwguard.py:35-43)"
    - "assertion fragments — not exact-string equality (test_fwguard.py:68-70 style)"
    - "RESEARCH §7 Option A: alpha-suffix strip via re.sub(r'-.*$', '', ...)"
key_files:
  created:
    - firestarter_app/tests/test_fw_version_guard.py
  modified:
    - firestarter_app/firestarter/serial_comm.py
decisions:
  - "D-01: _validate_firmware_version is a @staticmethod with (version_str, allow_pre_v12=False) signature"
  - "D-02: env-var I/O (FIRESTARTER_DEV_ALLOW_PRE_V12) stays in _probe_port; staticmethod is pure"
  - "D-03: _is_version_sufficient stays as internal '≥ 2.0.0' helper"
  - "D-04: 3 'Could not parse FW message' raises remain in _probe_port unchanged"
  - "D-05: tests/test_fw_version_guard.py covers the matrix with the RESEARCH §1 correction"
  - "RESEARCH §7 Option A: '3.0.0-dev' alpha-suffix strip — INTENTIONAL BEHAVIOR FIX"
metrics:
  duration_seconds: 279
  completed: 2026-05-28
  tasks_completed: 3
  tasks_total: 3
  test_delta: "186 + 11 = 197 passed; 2 xfailed; 29 snapshots — all green"
  mypy_watermark: "41 errors (unchanged; watermark 44)"
---

# Phase 40 Plan 01: SERIAL-02 — _validate_firmware_version Extraction Summary

**One-liner:** Extracted `SerialCommunicator._validate_firmware_version` as a pure `@staticmethod` that owns the complete firmware version-guard policy (pre-v1.2 refuse + 2.0.0 floor + dev-bypass), repointed `_probe_port` to call it with the env-var-derived boolean, and added 11 unit tests covering the policy directly without serial mocking.

## What Shipped

### `firestarter_app/firestarter/serial_comm.py`

**Added** a new `@staticmethod` named `_validate_firmware_version`, placed immediately after `_is_version_sufficient` (line 593) and before `_probe_port` (line 595):

```python
@staticmethod
def _validate_firmware_version(
    version_str: str, allow_pre_v12: bool = False
) -> None:
    version_str = re.sub(r"-.*$", "", version_str)
    try:
        major = int(version_str.split(".")[0])
    except (ValueError, IndexError):
        major = 0
    if major < 3 and not allow_pre_v12:
        raise FirmwareOutdatedError(...)   # Branch A: pre-v1.2
    if not SerialCommunicator._is_version_sufficient(version_str, "2.0.0"):
        raise FirmwareOutdatedError(...)   # Branch B: 2.0.0 floor
```

Both `FirmwareOutdatedError` messages are byte-identical to the strings previously embedded in `_probe_port` (per RESEARCH §4) so operator-visible behavior is unchanged.

**Removed** 25 lines from `_probe_port` (the inline `try/if major < 3/if not _is_version_sufficient` block). Replacement is 6 lines:

```python
allow_pre_v12 = (
    os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") == "1"
)
SerialCommunicator._validate_firmware_version(
    current_version, allow_pre_v12=allow_pre_v12
)
```

The Phase 6 (LFW-05 + LHOST-04) live-intent comment block immediately above the call site is preserved. The three remaining `FirmwareOutdatedError` raises in `_probe_port` — the no-regex-match path (line 711), the no-"FW:" path (line 716), and the `IndexError/AttributeError` wrapper raise (line 721) — are unchanged (D-04: those are transport-parse concerns, not version-guard policy).

**Net effect:** Before this plan `_probe_port` held 5 `FirmwareOutdatedError` raises (all version-guard or parse-failure). After: 2 in the staticmethod (Branches A/B) + 3 still in `_probe_port` (D-04 paths). The env-var read + boolean threading reproduces the original `major < 3 and os.environ.get(...) != "1"` semantics byte-identically.

### `firestarter_app/tests/test_fw_version_guard.py` (NEW)

11 unit tests on `class TestValidateFirmwareVersion` exercising the staticmethod directly (no serial mock, no `_probe_port`, no patching). Autouse `monkeypatch.delenv("FIRESTARTER_DEV_ALLOW_PRE_V12", raising=False)` fixture copied from `test_fwguard.py`:

| Row | Input | Expected | Branch / Reason |
|---|---|---|---|
| `test_v3_zero_zero_passes` | `"3.0.0"` | None | normal accept |
| `test_v3_minor_segment_passes` | `"3.5.2"` | None | normal accept |
| `test_single_segment_passes` | `"3"` | None | single-segment |
| `test_alpha_suffix_passes` | `"3.0.0-dev"` | None | **RESEARCH §7 Option A** — strip alpha suffix |
| `test_v29_with_allow_passes` | `"2.9.9", allow=True` | None | **CORRECTION** from CONTEXT.md D-05 per RESEARCH §1 |
| `test_v29_raises` | `"2.9.9"` | Branch A raise | major=2 < 3 |
| `test_pre_v12_raises` | `"1.0.0"` | Branch A raise | major=1 < 3 |
| `test_unparseable_raises` | `"abc"` | Branch A raise | int() fails → major=0 |
| `test_empty_string_raises` | `""` | Branch A raise | int() fails → major=0 |
| `test_pre_v12_bypass_floor` | `"1.0.0", allow=True` | Branch B raise | allow_pre_v12 bypasses ONLY pre-v1.2, not 2.0.0 floor |
| `test_no_env_read` | env=1, `"1.0.0"` (default allow) | Branch A raise | **D-02 invariant:** staticmethod ignores `os.environ` |

All 11 tests pass. The existing `test_fwguard.py` (4 integration tests via `expect_ack` mocking) continues to pass — both files coexist intentionally.

## Tasks & Commits

| Task | Name | Commit (firestarter_app submodule on v1.8-app-cleanup) | Files |
|------|------|--------------------------------------------------------|-------|
| 40-01-01 | Add `_validate_firmware_version` @staticmethod (D-01/D-03) | `dc727b9` `feat(40-01-01): add _validate_firmware_version @staticmethod to SerialCommunicator` | `firestarter/serial_comm.py` |
| 40-01-02 | Repoint `_probe_port` to call staticmethod (D-02/D-04) | `bedd122` `refactor(40-01-02): repoint _probe_port to call _validate_firmware_version` | `firestarter/serial_comm.py` |
| 40-01-03 | Create `test_fw_version_guard.py` (D-05) | `eb1717e` `test(40-01-03): add test_fw_version_guard.py for _validate_firmware_version` | `tests/test_fw_version_guard.py` |

Task 40-01-01's commit body contains the literal line required by Plan 40-01 success_criteria #7:

> `INTENTIONAL BEHAVIOR FIX: _validate_firmware_version strips trailing alpha suffix (e.g. '3.0.0-dev' → '3.0.0') before parsing — production wire behavior unchanged because the _probe_port regex \`r"FW:\s*([\d.x]+)"\` already strips it`

Per RESEARCH §7 Option A and the GATE-1.8 "refactor + fix bugs found" allowance. Production wire behavior is unchanged because the `_probe_port` regex `r"FW:\s*([\d.x]+)"` already strips `-dev` before any version string reaches `_validate_firmware_version` on the live wire path; the strip in the staticmethod only affects direct callers (future Click handlers, test harnesses).

## Verification

| Check | Command | Result |
|---|---|---|
| New unit tests | `pytest tests/test_fw_version_guard.py -v` | 11/11 pass |
| Integration tests | `pytest tests/test_fwguard.py -v` | 4/4 pass (unchanged) |
| Full suite | `pytest tests/` | **197 passed + 2 xfailed + 29 snapshots** (baseline 186 + 11 new) |
| Lint | `ruff check firestarter/serial_comm.py tests/test_fw_version_guard.py` | clean |
| Mypy watermark | `python tools/check_mypy_watermark.py` | 41 errors / watermark 44 — **NOT raised** |
| Call-site count | `grep -n "_validate_firmware_version" firestarter/serial_comm.py` | 2 hits (def at 596, call site at 687) |
| Raise count (excl. comments) | `grep -v '^[[:space:]]*#' firestarter/serial_comm.py \| grep -c 'FirmwareOutdatedError('` | 5 (2 staticmethod + 3 _probe_port D-04 paths) |
| Autouse fixture present | `grep -c "monkeypatch.delenv" tests/test_fw_version_guard.py` | 1 |
| CORRECTION annotation | `grep -c "CORRECTION" tests/test_fw_version_guard.py` | 1 |

Cross-checked toolchain: `pytest 9.0.3`, `ruff 0.15.14`, `mypy 2.1.0 (compiled)`. The hardened-mypy-gate watermark check ran with mypy actually installed (not the silent-OK fallback).

## Deviations from Plan

**None.** The plan executed exactly as written. The two "corrections" surfaced by Plan 40-01 / RESEARCH (the `"2.9.9" + allow_pre_v12=True → passes` row in `test_v29_with_allow_passes` and the `"3.0.0-dev" → passes` Option A behavior) were planned-and-locked corrections, not new-discovered deviations during execution.

No Rule 1 / Rule 2 / Rule 3 auto-fixes were triggered. No checkpoints were hit. No authentication gates.

## Known Stubs

None. The new staticmethod is wired into `_probe_port` and exercised by both unit tests (direct call) and integration tests (via `expect_ack`-mocked `_probe_port`).

## Self-Check: PASSED

- File created: `firestarter_app/tests/test_fw_version_guard.py` — FOUND
- File modified: `firestarter_app/firestarter/serial_comm.py` — FOUND
- Commit `dc727b9` — FOUND
- Commit `bedd122` — FOUND
- Commit `eb1717e` — FOUND

All commits on `v1.8-app-cleanup` branch inside the `firestarter_app` submodule. No commits or staged changes in the meta-repo (the operator promotes the gitlink pointer at milestone close per `project_v18_phase_execution_mechanics`).

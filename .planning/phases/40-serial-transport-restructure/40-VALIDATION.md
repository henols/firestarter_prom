---
phase: 40
slug: serial-transport-restructure
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-28
---

# Phase 40 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Built from RESEARCH.md "Validation Architecture" + CONTEXT.md wave decomposition.
> Standing gate: GATE-1.8 (a–e) — wire byte-identical, CLI surface preserved,
> no constants touched, read path ring-fenced, suite green + entry point runs.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 + syrupy 5.2.0 |
| **Config file** | `firestarter_app/pyproject.toml` |
| **Quick run command** | `cd firestarter_app && pytest tests/test_fw_version_guard.py tests/test_fwguard.py tests/test_decoder.py -v` |
| **Full suite command** | `cd firestarter_app && pytest tests/ -v` |
| **Baseline** | 186 passed + 2 xfailed + 29 snapshots (post-Phase 39, 2026-05-28) |
| **Estimated runtime** | ~10 seconds full suite |

---

## Sampling Rate

- **After every task commit:** Run quick command (target file's tests).
- **After every plan wave:** Run full suite — must stay at baseline (186 + 2xf + 29 snapshots).
- **Before `/gsd-verify-work`:** Full suite must be green AND `ruff check` clean AND mypy watermark not raised.
- **Max feedback latency:** ~10s.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------------|-----------|-------------------|-------------|--------|
| 40-01-01 | 01 | 1 | SERIAL-02 / D-01 | `_validate_firmware_version("3.0.0") -> None` | unit | `pytest firestarter_app/tests/test_fw_version_guard.py::test_v3_zero_zero_passes -v` | ❌ W0 (new file) | ⬜ pending |
| 40-01-02 | 01 | 1 | SERIAL-02 / D-01 | `_validate_firmware_version("2.9.9")` raises FirmwareOutdatedError ("outdated") | unit | `pytest firestarter_app/tests/test_fw_version_guard.py::test_v29_raises -v` | ❌ W0 | ⬜ pending |
| 40-01-03 | 01 | 1 | SERIAL-02 / D-01 | `_validate_firmware_version("1.0.0")` raises FirmwareOutdatedError ("pre-v1.2") | unit | `pytest firestarter_app/tests/test_fw_version_guard.py::test_pre_v12_raises -v` | ❌ W0 | ⬜ pending |
| 40-01-04 | 01 | 1 | SERIAL-02 / D-02 + D-05 | `_validate_firmware_version("1.0.0", allow_pre_v12=True)` raises (2.0.0 floor) | unit | `pytest firestarter_app/tests/test_fw_version_guard.py::test_pre_v12_bypass_floor -v` | ❌ W0 | ⬜ pending |
| 40-01-05 | 01 | 1 | SERIAL-02 / D-05 (CORRECTED) | `_validate_firmware_version("2.9.9", allow_pre_v12=True) -> None` (PASSES — corrected from CONTEXT.md) | unit | `pytest firestarter_app/tests/test_fw_version_guard.py::test_v29_with_allow_passes -v` | ❌ W0 | ⬜ pending |
| 40-01-06 | 01 | 1 | SERIAL-02 / D-05 | `_validate_firmware_version("abc")` raises (parse-fails-to-0) | unit | `pytest firestarter_app/tests/test_fw_version_guard.py::test_unparseable_raises -v` | ❌ W0 | ⬜ pending |
| 40-01-07 | 01 | 1 | SERIAL-02 / D-04 | `_probe_port` still raises FirmwareOutdatedError on pre-v1.2 + outdated paths | integration | `pytest firestarter_app/tests/test_fwguard.py -v` | ✅ | ⬜ pending |
| 40-01-08 | 01 | 1 | SERIAL-02 / D-04 | Phase 36 characterization snapshots unchanged | snapshot | `pytest firestarter_app/tests/test_characterization.py firestarter_app/tests/test_serial_characterization.py -v` | ✅ | ⬜ pending |
| 40-02-01 | 02 | 2 | SERIAL-01 / D-06 | `from firestarter.codec import decode_id_frame` works | smoke | `python3 -c "from firestarter.codec import decode_id_frame; print('OK')"` | N/A | ⬜ pending |
| 40-02-02 | 02 | 2 | SERIAL-01 / D-06 + D-07 | `test_decoder.py` 4 call-site tests pass UNCHANGED via thin wrapper | unit | `pytest firestarter_app/tests/test_decoder.py -v` | ✅ | ⬜ pending |
| 40-02-03 | 02 | 2 | SERIAL-01 / D-08 | `codec.decode_id_frame` docstring contains "GATE-1.8d" breadcrumb | grep | `grep -A3 "def decode_id_frame" firestarter_app/firestarter/codec.py \| grep "GATE-1.8d"` | N/A | ⬜ pending |
| 40-02-04 | 02 | 2 | SERIAL-01 / D-06 | Thin wrapper `_decode_id_frame` remains on `SerialCommunicator` | grep | `grep -n "def _decode_id_frame" firestarter_app/firestarter/serial_comm.py` | N/A | ⬜ pending |
| 40-03-01 | 03 | 3 | SERIAL-01 / D-10 | `STATE_MACHINE_PREFIXES` absent | grep | `! grep -n "STATE_MACHINE_PREFIXES" firestarter_app/firestarter/serial_comm.py` | N/A | ⬜ pending |
| 40-03-02 | 03 | 3 | SERIAL-01 / D-11 | `read_line_bytes` absent | grep | `! grep -n "read_line_bytes" firestarter_app/firestarter/serial_comm.py` | N/A | ⬜ pending |
| 40-03-03 | 03 | 3 | SERIAL-01 / D-12 | Three dead comment fragments gone (lines 64, 161, 207-209 of pre-phase HEAD) | git diff | manual diff review — confirms only deletions in those line ranges | N/A | ⬜ pending |
| 40-03-04 | 03 | 3 | SERIAL-01 / D-13 + D-14 | `PREFIX_REGEX` rationale + F401 re-export blocks KEPT | grep | `grep -c "PREFIX_REGEX\|noqa: F401" firestarter_app/firestarter/serial_comm.py` ≥ 2 | N/A | ⬜ pending |
| 40-03-05 | 03 | 3 | SERIAL-01 | ruff clean | lint | `cd firestarter_app && ruff check firestarter/serial_comm.py` exits 0 | N/A | ⬜ pending |
| 40-04-01 | 04 | 4 | SERIAL-03 / D-15 | `# DO NOT MODIFY` block IMMEDIATELY above `def _read_and_parse_lines` | grep | `grep -B1 "def _read_and_parse_lines" firestarter_app/firestarter/serial_comm.py \| grep "DO NOT MODIFY"` | N/A | ⬜ pending |
| 40-04-02 | 04 | 4 | SERIAL-03 / GATE-1.8d | `_read_and_parse_lines` generator BODY byte-identical (signature/docstring excluded) | git diff | `git diff <pre-phase-sha>..HEAD -- firestarter/serial_comm.py` shows only comment/header changes inside that function | N/A | ⬜ pending |
| 40-04-03 | 04 | 4 | SERIAL-03 / D-17 | All 7 missing `-> None` return hints added (`__init__`, `_log_rurp_feedback`, `send_ack`, `send_done`, `consume_remaining_input`, `disconnect`, `_log_command_details`) | grep | each method has `-> None:` at its def | N/A | ⬜ pending |
| 40-04-04 | 04 | 4 | SERIAL-03 / D-18 | mypy watermark NOT raised | mypy | `cd firestarter_app && mypy firestarter/serial_comm.py` error count ≤ pre-phase baseline | N/A | ⬜ pending |
| 40-04-05 | 04 | 4 | GATE-1.8e | Full suite green | full | `cd firestarter_app && pytest tests/ -v` → 186 passed + 2 xfailed + 29 snapshots | N/A | ⬜ pending |
| 40-04-06 | 04 | 4 | GATE-1.8e | `firestarter --help` exits 0 | smoke | `firestarter --help` exits 0 | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tests/test_fw_version_guard.py` — NEW file with 6+ rows covering D-05 matrix (with corrected `"2.9.9" + allow_pre_v12=True → passes` row per RESEARCH.md §1)
- [ ] Reuse the `monkeypatch.delenv("FIRESTARTER_DEV_ALLOW_PRE_V12", raising=False)` fixture pattern from existing `test_fwguard.py`

Framework + existing conftest cover all other Wave 0 needs (pytest 9.0.3, syrupy 5.2.0, ruff, mypy all installed).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `_read_and_parse_lines` byte-identity is the v1.9 RCA baseline | SERIAL-03 / GATE-1.8d | The Phase 26 baseline binaries are at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` and were captured against a specific generator body. Re-running them is hardware-bench territory (v1.9 RCA). For v1.8 we accept the proxy: `test_decoder.py` green + `git diff` shows only comment/docstring header changes inside the function. | Review `git diff` for `_read_and_parse_lines` after Wave 4 — confirm only the lines above `def` and the docstring's first line are modified. No statement-level changes inside the loop. |
| Operator-visible firmware-outdated error text on real hardware | SERIAL-02 / GATE-1.8b | Snapshot tests pin the CLI surface; real hardware re-test is v1.9-bench. | Optional: post-merge bench-test against a real pre-v1.2 firmware board if available — confirm the error message and exit code are unchanged. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (`test_fw_version_guard.py`)
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s (full suite ~10s)
- [ ] `nyquist_compliant: true` set in frontmatter after planner consumes this

**Approval:** pending

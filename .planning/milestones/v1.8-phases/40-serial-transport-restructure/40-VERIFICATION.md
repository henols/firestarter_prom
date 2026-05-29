---
phase: 40-serial-transport-restructure
verified: 2026-05-28T00:00:00Z
status: passed
score: 3/3 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: null
  previous_score: null
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 40: Serial / Transport Restructure — Verification Report

**Phase Goal:** `serial_comm.py` owns only transport concerns after Phase 38's extractions. `_validate_firmware_version` is an extractable `@staticmethod` with direct unit tests. The `_read_and_parse_lines` generator body is explicitly ring-fenced with a comment. Type hints are added to all public `SerialCommunicator` methods. Wire behavior is verified byte-identical by the existing test suite.

**Verified:** 2026-05-28
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth (Success Criterion) | Status | Evidence |
|---|---------------------------|--------|----------|
| 1 | `SerialCommunicator` owns only the named transport surface; frame-decode/message-format delegated to `frame_parser`+`codec`; `STATE_MACHINE_PREFIXES` deleted | VERIFIED | `grep "STATE_MACHINE_PREFIXES" firestarter/serial_comm.py` → 0 hits (D-10); `grep "^def decode_id_frame" firestarter/codec.py` → 1 hit (line 168); `SerialCommunicator._decode_id_frame` is a 3-line thin wrapper at lines 203–205 returning `codec.decode_id_frame(frame_len, body)`; full method list matches the SC#1 named surface (`__init__`, `is_connected`, `send_*`, `get_response`, `expect_ack`, `consume_remaining_input`, `disconnect`, `find_and_connect`, `_probe_port`, `_list_potential_ports`, `_read_and_parse_lines`, plus the explicitly-permitted `_parse_response_line`/`_log_rurp_feedback`/`_decode_id_frame`/`_log_command_details`/`_is_version_sufficient`/`_validate_firmware_version`). Also: `read_line_bytes` deleted (D-11, zero callers), three dead/orphan comments deleted (D-12). |
| 2 | `SerialCommunicator._validate_firmware_version(...) -> None` is a `@staticmethod`; `tests/test_fw_version_guard.py` covers the version-guard logic directly (passes on `"3.0.0"`, raises `FirmwareOutdatedError` on `"2.9.9"`) | VERIFIED | `isinstance(SerialCommunicator.__dict__['_validate_firmware_version'], staticmethod)` → True (smoke run); def at `firestarter/serial_comm.py:478`; signature is `_validate_firmware_version(version_str: str, allow_pre_v12: bool = False) -> None` (documented D-01 deviation from ROADMAP literal — adds `allow_pre_v12` second arg to keep env-var I/O in `_probe_port` per D-02). `tests/test_fw_version_guard.py` exists with 11 unit tests (no serial mock); `pytest tests/test_fw_version_guard.py -q` → 11/11 pass. Behavior contract proven by direct call: `"3.0.0"` returns None, `"2.9.9"` raises `FirmwareOutdatedError` containing `"pre-v1.2"`. |
| 3 | `_read_and_parse_lines` carries `# DO NOT MODIFY — v1.9 RCA territory` comment at its header; body byte-identical to pre-v1.8 (`test_decoder.py` passes unchanged); all public methods have type-annotated signatures; `pytest` exits 0 | VERIFIED | 11-line ring-fence comment block at `firestarter/serial_comm.py:207–217`, immediately above `def _read_and_parse_lines` at line 218; docstring first line prefixed with `[ring-fenced — v1.9 RCA territory; see header comment]` at line 220; `grep -c "DO NOT MODIFY" firestarter/serial_comm.py` → exactly **1** (D-16 no marker inflation). Body byte-identity proven via SHA256 hash of generator body span: pre-phase (`6e32b37`) hash `a075c371…715fc4` matches post-phase HEAD hash after stripping ONLY the planned docstring marker prefix — 127 lines preserved, byte-identical. `test_decoder.py` is byte-identical (`git diff 6e32b37 HEAD -- tests/test_decoder.py` → empty). AST scan of `SerialCommunicator` confirms 100% type-hint coverage on all method signatures (return + parameter annotations). `pytest tests/` → 197 passed + 2 xfailed + 29 snapshots, exit 0. |

**Score:** 3/3 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/serial_comm.py` | refactored to transport-only; 703 lines; thin `_decode_id_frame` wrapper; ring-fenced `_read_and_parse_lines`; `_validate_firmware_version` @staticmethod; all 7 new `-> None` hints | VERIFIED | 703 lines (matches Wave-4 SUMMARY); all named structural changes confirmed by grep + line inspection; ruff clean; mypy 38 errors below 44-watermark. |
| `firestarter_app/firestarter/codec.py` | new `decode_id_frame` free function with D-08 breadcrumb; 4 new imports (`CATALOG`, `SEVERITY_LABEL`, `LogMessage`, `_crc8_ccitt`) | VERIFIED | def at `codec.py:168`; docstring opens with "Read-path-adjacent — behavior preserved verbatim from serial_comm.py per GATE-1.8d" (D-08 confirmed); imports at lines 25–37 include all 4 named symbols; logger configured as `logging.getLogger("Codec")`. |
| `firestarter_app/tests/test_fw_version_guard.py` | NEW; 11 unit tests on `TestValidateFirmwareVersion`; autouse `monkeypatch.delenv` fixture; D-05 matrix including the corrected `"2.9.9" + allow=True → passes` row | VERIFIED | File created; 125 lines; 11 test methods present (`test_v3_zero_zero_passes`, `test_v3_minor_segment_passes`, `test_single_segment_passes`, `test_alpha_suffix_passes`, `test_v29_with_allow_passes`, `test_v29_raises`, `test_pre_v12_raises`, `test_unparseable_raises`, `test_empty_string_raises`, `test_pre_v12_bypass_floor`, `test_no_env_read`); autouse `_clear_escape_hatch` fixture at lines 24–33; `CORRECTION from CONTEXT.md D-05` annotation present at line 60. |
| `firestarter_app/tests/test_decoder.py` | BYTE-IDENTICAL to pre-phase `6e32b37` (load-bearing SC#3 + D-06 invariant) | VERIFIED | `git diff 6e32b37 HEAD -- tests/test_decoder.py` returns empty; all 32 tests pass via thin wrapper resolution to `codec.decode_id_frame`. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `serial_comm.py::_probe_port` | `serial_comm.py::SerialCommunicator._validate_firmware_version` | static call `SerialCommunicator._validate_firmware_version(current_version, allow_pre_v12=allow_pre_v12)` | WIRED | call site at `serial_comm.py:569`; preceded by `allow_pre_v12 = os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") == "1"` at line 566–568 (D-02 env-var I/O preserved in _probe_port). |
| `tests/test_fw_version_guard.py` | `serial_comm.py::SerialCommunicator._validate_firmware_version` | direct unit test class calling the staticmethod | WIRED | 11 test methods exercising both accept and reject paths; pytest 11/11 pass. |
| `serial_comm.py::_decode_id_frame` (thin wrapper) | `codec.py::decode_id_frame` | `return codec.decode_id_frame(frame_len, body)` | WIRED | wrapper at line 203–205 delegates via the `codec` module alias imported at line 22 (`import firestarter.codec as codec`). |
| `serial_comm.py::_read_and_parse_lines` (line 318) | `serial_comm.py::SerialCommunicator._decode_id_frame` (thin wrapper) | `self._decode_id_frame(frame_len, body)` | WIRED | call site at line 318 is byte-identical to pre-phase (within the ring-fenced generator body). |
| `tests/test_decoder.py` (4 sites) | `serial_comm.py::SerialCommunicator._decode_id_frame` (thin wrapper) | `comm._decode_id_frame(frame_len=..., body=...)` | WIRED | test file is byte-identical pre-vs-post (load-bearing proof); 32 tests pass via wrapper. |
| Phase 40 D-15 ring-fence | `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` (v1.9 RCA baseline binaries) | comment block names the directory verbatim | WIRED | path string present at `serial_comm.py:211` inside the 11-line ring-fence block. |

### Data-Flow Trace (Level 4)

| Artifact | Data Source | Produces Real Data | Status |
|----------|-------------|--------------------|--------|
| `_validate_firmware_version` | input `version_str` from `_probe_port`'s regex `r"FW:\s*([\d.x]+)"` against serial | YES — real version strings from live wire path | FLOWING |
| `codec.decode_id_frame` | input `(frame_len, body)` from `_read_and_parse_lines` after magic-preamble detection | YES — real wire bytes; verified by `test_decoder.py` 32/32 pass and `test_codec.py` 10/10 pass | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `_validate_firmware_version` SC#2 contract: passes on `"3.0.0"` | `python -c "from firestarter.serial_comm import SerialCommunicator; SerialCommunicator._validate_firmware_version('3.0.0')"` | exit 0, no raise | PASS |
| `_validate_firmware_version` SC#2 contract: raises `FirmwareOutdatedError` containing `"pre-v1.2"` on `"2.9.9"` | direct call | raises `FirmwareOutdatedError`; `"pre-v1.2"` in message | PASS |
| `_validate_firmware_version` is a real `@staticmethod` | `isinstance(SerialCommunicator.__dict__['_validate_firmware_version'], staticmethod)` | True | PASS |
| `codec.decode_id_frame` callable without instance | `from firestarter.codec import decode_id_frame; decode_id_frame(2, b'\x01\x07')` | returns `LogMessage` | PASS |
| `firestarter --help` runs (GATE-1.8e pip entry point) | `firestarter --help` | exit 0; full argparse usage block printed | PASS |
| Full pytest suite green | `python -m pytest tests/` | 197 passed, 2 xfailed, 29 snapshots — exit 0 | PASS |
| Ruff clean on full tree | `ruff check firestarter/ tests/` | "All checks passed!" exit 0 | PASS |
| Mypy watermark not raised | `python tools/check_mypy_watermark.py` | 38 errors / 44 watermark (BELOW; D-18 satisfied) | PASS |
| `test_decoder.py` byte-identity vs pre-phase | `git diff 6e32b37 HEAD -- tests/test_decoder.py` | empty | PASS |
| Generator body byte-identity (SHA256) | Python helper extracting `_read_and_parse_lines` body span | pre-hash `a075c371…715fc4` == post-hash-after-marker-strip `a075c371…715fc4` (127 lines) | PASS |
| Marker non-inflation (D-16) | `grep -c "DO NOT MODIFY" firestarter/serial_comm.py` | exactly 1 | PASS |

### Probe Execution

| Probe | Command | Result | Status |
|-------|---------|--------|--------|
| _(no formal `scripts/*/tests/probe-*.sh` exist in this repo for v1.8 host-cleanup; the pytest suite + ruff + mypy-watermark + entry-point smoke ARE the probes)_ | n/a | n/a | SKIPPED — no probe scripts declared/present |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| SERIAL-01 | 40-02, 40-03, 40-04 | `SerialCommunicator` reduced to transport + command dispatch; firmware-handshake lifted out of `_probe_port`; type hints added | SATISFIED | Plan 40-02 extracted `_decode_id_frame` body to `codec.decode_id_frame`; Plan 40-03 deleted `STATE_MACHINE_PREFIXES` + `read_line_bytes` + 3 dead comments; Plan 40-04 added the 7 missing `-> None` hints. The firmware-handshake concern is partially lifted: `_validate_firmware_version` is a pure staticmethod (Plan 40-01), but the env-var read + regex stay in `_probe_port` (documented D-02 split). |
| SERIAL-02 | 40-01 | `_validate_firmware_version` is a testable static method with unit tests | SATISFIED | Plan 40-01 added the `@staticmethod` at `serial_comm.py:478` and created `tests/test_fw_version_guard.py` with 11 unit tests (no serial mock). |
| SERIAL-03 | 40-04 | Wire behavior stays byte-identical; `_read_and_parse_lines` generator body unchanged; verified by existing + new tests (satisfies GATE-1.8a) | SATISFIED | Plan 40-04 added the ring-fence + docstring marker; SHA256 proof shows the 127-line generator body byte-identical pre-vs-post; `test_decoder.py` byte-identical and 32/32 pass; `test_serial_characterization.py` 29 snapshots pass. |

**Orphaned requirements check:** REQUIREMENTS.md maps SERIAL-01, SERIAL-02, SERIAL-03 to Phase 40 (table lines 130–132). All three are claimed by at least one plan's `requirements` frontmatter (verified by grep). No orphaned requirements.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter/codec.py` | 252 | word `"placeholder"` inside legitimate format-error fallback comment | INFO | Not a stub — the comment describes the `<format-error: {entry.name}>` tag that the runtime DoS-resilient render-failure path emits when a catalog format string fails to substitute. Byte-identical to the migrated text from `serial_comm.py`. Not a code smell. |

No TBD / FIXME / XXX / TODO / HACK markers anywhere in the modified files. No `return null` / `return []` / `return {}` empty-implementation stubs. No `console.log`-only / `pass`-only / `e.preventDefault()`-only handlers.

### Human Verification Required

None. This is a pure host-side Python refactor:

- The wire protocol is frozen by GATE-1.8a (proven byte-identical via SHA256 on `_read_and_parse_lines`).
- The operator-visible CLI surface is locked by 29 syrupy snapshots in `test_characterization.py` + `test_serial_characterization.py`, all passing.
- The firmware-outdated error messages are pinned verbatim from RESEARCH §4 and exercised by both unit tests (`test_fw_version_guard.py`) and integration tests (`test_fwguard.py`).
- The GATE-1.8e pip entry point smoke test (`firestarter --help`) passes with exit 0.

Bench/hardware verification is NOT needed for Phase 40 — the firmware sub-repo was not touched, the wire framing was not touched (frozen by GATE-1.8a), and the read-bug RCA is explicitly ring-fenced for v1.9 (the Phase 26 baseline binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` were captured against the now-byte-identical generator body).

### Gaps Summary

None. All three ROADMAP Success Criteria are satisfied by codebase evidence:

- **SC#1** (transport-only surface; STATE_MACHINE_PREFIXES deleted; delegation to frame_parser/codec): VERIFIED by grep + method-list inspection + the `codec.decode_id_frame` extraction.
- **SC#2** (`_validate_firmware_version` is a `@staticmethod` with direct unit tests passing on "3.0.0" and raising on "2.9.9"): VERIFIED by `isinstance(..., staticmethod)`, direct invocation, and 11/11 pass in `test_fw_version_guard.py`.
- **SC#3** (ring-fence comment + generator-body byte-identity + type-annotated public methods + pytest exits 0): VERIFIED by SHA256 generator-body proof, `test_decoder.py` empty diff, AST-confirmed 100% type-hint coverage, 197 passed + 2 xfailed + 29 snapshots.

**GATE-1.8 closure (cross-cutting, applied to Phase 40):**

- **GATE-1.8a** (wire byte-identical) — VERIFIED via SHA256 hash of the 127-line generator-body span of `_read_and_parse_lines` (pre/post hashes match after stripping ONLY the planned docstring marker prefix).
- **GATE-1.8b** (CLI surface preserved) — VERIFIED via 29 syrupy snapshots passing in `test_characterization.py` + `test_serial_characterization.py`.
- **GATE-1.8c** (constants untouched) — VERIFIED: `constants.py` not in the modified-file list of any 40-plan; not touched by any of the 9 phase commits.
- **GATE-1.8d** (read path ring-fenced) — VERIFIED via the 11-line `# DO NOT MODIFY — v1.9 RCA territory (GATE-1.8d)` comment block at `serial_comm.py:207–217` + docstring marker at line 220 + the body-identity SHA256 proof.
- **GATE-1.8e** (suite green + entry point installs/runs) — VERIFIED: 197 passed + 2 xfailed + 29 snapshots; `firestarter --help` exits 0.

**D-01..D-19 coverage check (CONTEXT.md decisions):** all 19 D-ids cited in at least 2 of the 4 PLAN+SUMMARY artifact pairs.

**Documented deviations (acknowledged by the planner + executor + this verifier):**

- D-01: `_validate_firmware_version` signature is `(version_str: str, allow_pre_v12: bool = False) -> None` — ROADMAP SC#2 names only `(version_str: str) -> None`. The extra default-False second argument keeps env-var I/O policy in `_probe_port` (D-02), which is exactly what the planner intended. The ROADMAP behavior contract ("passes on 3.0.0, raises on 2.9.9") is preserved BYTE-FOR-BYTE.
- D-07: `_decode_id_frame` body extraction to `codec.decode_id_frame` reverses Phase 38 D-06's "keep as method" decision — Phase 38 explicitly deferred the disposition to Phase 40 SC#1. Documented in 40-02-PLAN.md `must_haves.truths`.
- D-11/D-12: dead-code sweep extends SC#1's literal `STATE_MACHINE_PREFIXES` list to also delete `read_line_bytes` (zero callers) + three orphan/dead comments. Documented in 40-03-PLAN.md and 40-03-SUMMARY.md; same Phase 38 D-14/D-16 precedent.
- Wave-4 Rule-1 auto-fix: single surgical `# type: ignore[union-attr]` added on `self.connection.close()` (line 397 in current file) inside `disconnect()` — adding `-> None` to `disconnect` newly induced mypy to deeply check its body, exposing one latent narrowing failure that the pre-phase un-typed function masked. Documented in 40-04-SUMMARY.md "Deviations from Plan". Held the mypy watermark at 38 errors (well below the 44 threshold).

---

## Commit Lineage (firestarter_app submodule on v1.8-app-cleanup)

| Wave | Plan-Task | Commit | Message |
|------|-----------|--------|---------|
| 1 | 40-01-01 | `dc727b9` | feat(40-01-01): add `_validate_firmware_version` @staticmethod to SerialCommunicator |
| 1 | 40-01-02 | `bedd122` | refactor(40-01-02): repoint `_probe_port` to call `_validate_firmware_version` |
| 1 | 40-01-03 | `eb1717e` | test(40-01-03): add `test_fw_version_guard.py` for `_validate_firmware_version` |
| 2 | 40-02-01 | `7d34233` | feat(40-02-01): add `decode_id_frame` free function to codec.py |
| 2 | 40-02-02 | `a5cbbcf` | refactor(40-02-02): replace `_decode_id_frame` body with codec wrapper; delete dead messages imports |
| 3 | 40-03-01 | `c22476a` | refactor(40-03-01): delete STATE_MACHINE_PREFIXES + W-01 dead comment (D-10 + D-12 part 1) |
| 3 | 40-03-02 | `9c165dc` | refactor(40-03-02): delete read_line_bytes + two orphan comments (D-11 + D-12 parts 2/3) |
| 4 | 40-04-01 | `da1d7b7` | docs(40-04-01): ring-fence `_read_and_parse_lines` (D-15 + D-16) |
| 4 | 40-04-02 | `24636e9` | feat(40-04-02): add `-> None` to 7 public SerialCommunicator methods (D-17) |

All 9 commits confirmed present via `git -C /workspaces/firestarter_app log --oneline`; HEAD is `24636e9`.

---

_Verified: 2026-05-28_
_Verifier: Claude (gsd-verifier)_

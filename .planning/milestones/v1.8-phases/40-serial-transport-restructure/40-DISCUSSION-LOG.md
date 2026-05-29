# Phase 40: Serial / Transport Restructure - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-28
**Phase:** 40-serial-transport-restructure
**Areas discussed:** _validate_firmware_version shape, _decode_id_frame disposition, dead-code sweep extent, ring-fence marker placement & scope

---

## _validate_firmware_version shape & scope (SERIAL-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Pure compare only | `_validate_firmware_version(current, required) -> bool`; orchestrator owns pre-v1.2 reject + env-var bypass + raises | |
| Two-arg @staticmethod with env-var-as-param | `_validate_firmware_version(version_str, allow_pre_v12=False) -> None`; owns pre-v1.2 + 2.0.0-floor + raises; orchestrator reads env-var and passes the bool | ✓ |
| All-in-one with env read inside | Method does its own `os.environ` read | |
| Take raw "FW: <ver>" message | Method also runs the regex extraction | |

**User's choice:** "you recomend" — delegated; recommendation locked as D-01..D-05.
**Notes:** Two-arg form keeps the guard logic pure (no env mocking needed in tests) while still owning the full policy. Env-var I/O stays in `_probe_port` because env reads are environment policy, not version-guard policy. Preserves today's subtle behavior: `allow_pre_v12=True` bypasses ONLY the `major < 3` branch, NOT the 2.0.0 floor. `_is_version_sufficient` stays as the internal helper.

---

## _decode_id_frame final disposition (SERIAL-01)

| Option | Description | Selected |
|--------|-------------|----------|
| A — Extract to codec.py + thin wrapper | Free function `codec.decode_id_frame`; thin `SerialCommunicator._decode_id_frame` method delegates to it; `test_decoder.py` calls unchanged | ✓ |
| B — Keep as method | SC#1's "delegated" already satisfied since primitives + format_message are imports; package-coupled orchestrator stays put (Phase 38 D-06's stance) | |
| C — Extract + change tests | Move to codec, update `test_decoder.py` to call `codec.decode_id_frame` directly — fewer wrappers but breaks "test_decoder.py passes unchanged" | |
| D — Move to frame_parser | Forbidden: frame_parser is stdlib-only per Phase 38 D-05 | |

**User's choice:** "you recomend" — Option A locked as D-06..D-08.
**Notes:** Phase 38 D-06 explicitly deferred this to Phase 40, and SC#1's "frame-decode delegated" language unambiguously points at `_decode_id_frame` itself, not just its primitives. Thin wrapper preserves the `comm._decode_id_frame(frame_len, body)` test API exactly (4 sites in `test_decoder.py`). codec.py already imports CATALOG + frame_parser primitives, so the move adds zero new import edges. A read-path-adjacent breadcrumb docstring on the new function warns future-Claude.

---

## Dead-code sweep extent (SERIAL-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Strict to SC#1 | Delete only `STATE_MACHINE_PREFIXES`; leave everything else for later phases | |
| Phase 38 D-14/D-16 sweep pattern | Also delete `read_line_bytes` (zero callers, scout-verified) + three orphan/dead comment fragments (lines 64, 161, 207-209); keep live-intent comments | ✓ |
| Aggressive | Also delete `send_done` if Phase-41 will drop it; touch the F401 re-export block | |

**User's choice:** "you recomend" — Phase 38 pattern locked as D-10..D-14.
**Notes:** Documented deviation from SC#1's literal list, same reviewer template Phase 38 D-14/D-16 used. `STATE_MACHINE_PREFIXES` (SC#1) + `read_line_bytes` (zero callers) + comment fragments (orphan / dead-pointing once D-10 lands) all sweep in the same wave. The PREFIX_REGEX rationale block (USB-CDC garbage workaround) and the F401 re-export comment block (test_decoder.py back-compat) STAY — they document live intent.

---

## Ring-fence marker placement & nearest-callee scope (SERIAL-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Docstring-only | Put `# DO NOT MODIFY — v1.9 RCA territory` as the docstring's first line | |
| Header comment block + docstring marker | Multi-line `#` block immediately above `def _read_and_parse_lines` + one prefixed line in the docstring; high blame/grep/IDE visibility | ✓ |
| Mark nearest callees too | Add lighter notes to `_decode_id_frame`, `_parse_response_line`, `_log_rurp_feedback` | |

**User's choice:** "you recomend" — Option B locked as D-15..D-16.
**Notes:** Header `#` block beats docstring-only because it's visible on every blame line in the body, greppable by `grep -n "DO NOT MODIFY"`, and shows above the signature in IDE hover. Cites GATE-1.8d and the `.planning/v1.6/consistency-check-runs/...` baseline binary location. Nearest callees stay UNMARKED per Phase 38 D-09's scope (marker inflation dilutes the load-bearing signal). The single exception is the codec.py breadcrumb docstring on the new `decode_id_frame` (D-08) — a softer "read-path-adjacent" hint, not a hard ring-fence.

---

## Claude's Discretion

- Exact `_validate_firmware_version` error-message strings (keep byte-identical to today's `_probe_port` raises).
- Test file location for `tests/test_fw_version_guard.py` (recommend new file per SC#2's named filename).
- Function ordering inside `codec.py` after `decode_id_frame` is added (follow Phase 38 D-08's codec.py pattern).
- The thin `_decode_id_frame` method wrapper's docstring.
- Plan/wave decomposition — natural ordering proposed in CONTEXT.md (validate-fw → decode-id-frame → dead-code → ring-fence + type hints).

## Deferred Ideas

- `SerialCommunicator` mypy strict-overrides addition — Phase 42 ERR-02.
- Public-method docstrings on `SerialCommunicator` — Phase 42 ERR-03.
- `Optional[X]` → `X | None` modernization — locked deferred by Phase 37 D-08.
- `ProtocolStateMachine` extraction — REQUIREMENTS PROTOSM-01, explicitly v1.9.
- Removing the thin `_decode_id_frame` method wrapper — once `test_decoder.py` can repoint, drop it; not worth the test edit in v1.8.
- Centralized Click error→exit-code mapping for `FirmwareOutdatedError` — Phase 41/42 territory.

### Reviewed Todos (not folded)

- `avrdude-mcu-detection-fallback.md` — hardware / v1.9-ish.
- `serial-cobs-resync-data-path.md` — wire framing CHANGE, forbidden by GATE-1.8a; closest keyword match to "serial / transport" but firmly out of scope.
- `w27c512-eeprom-misclassification.md` — DB content, not serial structure.

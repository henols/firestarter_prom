---
phase: 38-low-risk-extractions
verified: 2026-05-27T00:00:00Z
status: passed
score: 5/5 success criteria verified (+ 5 GATE-1.8 standing checks green)
overrides_applied: 0
re_verification:
  previous_status: none
  note: Initial verification — no prior VERIFICATION.md existed.
---

# Phase 38: Low-Risk Extractions Verification Report

**Phase Goal:** Pure-compute code is extracted into new flat sibling modules with zero runtime behavior change. exceptions.py consolidates all exception classes (prerequisite for Phases 39, 40, 41). frame_parser.py, codec.py, and address_parser.py are independently testable without serial I/O. Dead code is deleted. The full test suite passes unchanged after every file move.
**Verified:** 2026-05-27
**Status:** passed
**Re-verification:** No — initial verification

All evidence drawn from the `firestarter_app` submodule (branch `v1.8-app-cleanup`), 7 source commits `9f85635..efb0fad` on base `8468d10`. SUMMARY claims were NOT trusted — every truth was checked against the actual code, git history, and a live test run.

## Goal Achievement

### Observable Truths (the 5 ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | SC#1 — exceptions.py exists with all 8 application exception classes; all import sites repointed; no exception class defined outside exceptions.py (+ Avrdude*Error in avr_tool.py per D-02) | ✓ VERIFIED | `firestarter/exceptions.py` defines exactly 8 classes (SerialError, SerialTimeoutError, ProgrammerNotFoundError, FirmwareOutdatedError, EpromOperationError, HardwareOperationError, FirmwareOperationError, ChipNotFoundError). Inheritance verified at runtime (3 subclass SerialError, 5 subclass Exception). `grep '^class .*Error'` across `firestarter/*.py` shows matches ONLY in exceptions.py (8) and avr_tool.py (2 Avrdude*Error — D-02). All 4 consumers (serial_comm, eprom_operations, firmware, hardware) import `from firestarter.exceptions import …`. exceptions.py is a pure leaf (0 firestarter imports). |
| 2 | SC#2 — frame_parser.py exists (pure stdlib leaf) with the frame primitives; test_decoder.py passes unchanged; _read_and_parse_lines untouched | ✓ VERIFIED | `firestarter/frame_parser.py` contains `_build_crc8_table`, `_CRC8_CCITT_TABLE`, `_crc8_ccitt`, `_decode_param`, `Response`, `LogMessage`, `MAGIC_PREAMBLE`; 0 firestarter-package imports (stdlib + typing only). Runtime check: `_crc8_ccitt(b'123456789')==0xF4`, `MAGIC_PREAMBLE==b'\xaa\x55\xaa\x55'`. serial_comm.py re-export block present (`# noqa: F401`). `git diff 8468d10..HEAD -- tests/test_decoder.py` is EMPTY (unchanged, D-07). test_decoder.py still imports the 4 symbols from `firestarter.serial_comm`, resolved via re-export. |
| 3 | SC#3 — codec.py exists with format_message (public) + _REVISION_SILKSCREEN; cycle-safe imports (D-08: also imports frame_parser._decode_param + struct); tests/test_codec.py covers format_message | ✓ VERIFIED | `firestarter/codec.py` defines public `def format_message(msg_id, params, entry)` (no `self`) + `_REVISION_SILKSCREEN`. Imports: `struct`, `constants` (explicit REVISION_*/COMMAND_NAMES, no F405 noqa), `frame_parser._decode_param` (D-08 correction confirmed), `messages` — all cycle-safe leaves. Runtime: `format_message(MSG_OK_REV,[0,0xFF],…)=='Rev 0'`, chunk='<chunk: 512 bytes>', unknown→None — works WITHOUT a SerialCommunicator. tests/test_codec.py has 10 test methods covering all specified catalog shapes; passes GREEN. _decode_id_frame call site repointed to `codec.format_message` (2 hits); `_format_message` method removed (0 hits). |
| 4 | SC#4 — address_parser.py exists with parse_address/parse_size raising ValueError on bad input; tests/test_address_parser.py covers hex/decimal/None/invalid | ✓ VERIFIED | `firestarter/address_parser.py` defines both public functions, pure stdlib leaf (0 firestarter imports), exact `int(s,16) if "0x" in s.lower() else int(s)` semantics. Runtime: hex/uppercase-hex/decimal/None all correct; bad input + empty string raise ValueError. tests/test_address_parser.py has 10 methods (hex, uppercase prefix, decimal, None, invalid→ValueError, empty→ValueError for both); passes GREEN. eprom_operations._setup_operation wires the parser in try/except ValueError with exact log strings 'Invalid address format: {address}' / 'Invalid size format: {size}' and `(None, 0)` return; D-13 subtlety preserved (`command_dict["address"]` set ONLY inside `if address:`, line 180). |
| 5 | SC#5 — read_data_block deleted from serial_comm.py; both globals() sites in eprom_operations.py replaced with COMMAND_NAMES[cmd]; pytest exits 0 | ✓ VERIFIED | `grep read_data_block` across firestarter/ + tests/ returns 0 (fully removed, zero callers). `grep globals()` in eprom_operations.py returns 0; `grep COMMAND_NAMES[cmd]` returns 2 (both _setup_operation:166 and _operation_context:226). Base had `globals().items()` reverse-lookup at both sites — RESEARCH-verified 13/13 value match. Star-import `from firestarter.constants import *` preserved (Phase 39 deferral). Full suite exits 0. |

**Score:** 5/5 truths verified

### GATE-1.8 Standing Checks

| Gate | Check | Status | Evidence |
| ---- | ----- | ------ | -------- |
| 1.8a | Wire protocol byte-identical | ✓ VERIFIED | No firmware files touched; constants.py untouched; only message-RENDERING (host-side log formatting) moved, not command serialization. Snapshot tests (which exercise the decode path) all pass. |
| 1.8b | CLI surface preserved (snapshot diff empty) | ✓ VERIFIED | `git diff 8468d10..HEAD -- tests/__snapshots__/` is EMPTY; 29 snapshots pass. |
| 1.8c | Constant contract preserved | ✓ VERIFIED | `git diff 8468d10..HEAD -- firestarter/constants.py` is EMPTY (untouched). |
| 1.8d | Read path ring-fenced (_read_and_parse_lines byte-identical) | ✓ VERIFIED | Extracted the full function body at base `8468d10` and `HEAD`: both 126 lines, sha256 IDENTICAL (`a075c371106a3c9f`). |
| 1.8e | Test suite green + entry point installs | ✓ VERIFIED | `python -m pytest` → 182 passed, 2 xfailed, 29 snapshots. `firestarter --help` exits 0. ruff check + format clean (36 files); mypy 41 ≤ watermark 44 (mypy 2.1.0 confirmed PRESENT, not the hardened fallback). |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `firestarter/exceptions.py` | 8 exception classes, pure leaf | ✓ VERIFIED | 61 lines, 8 classes, correct inheritance, 0 package imports |
| `firestarter/frame_parser.py` | 7 frame primitives, stdlib-only | ✓ VERIFIED | 109 lines, all primitives present, 0 package imports |
| `firestarter/codec.py` | format_message + _REVISION_SILKSCREEN | ✓ VERIFIED | 160 lines, public function, D-08 imports, cycle-safe |
| `firestarter/address_parser.py` | parse_address/parse_size, ValueError contract | ✓ VERIFIED | 30 lines, both functions, pure leaf |
| `firestarter/serial_comm.py` | primitives removed, re-export + codec import | ✓ VERIFIED | −319/+… net; primitives & _format_message & read_data_block removed; ring-fence intact |
| `firestarter/eprom_operations.py` | exception repoint, address_parser, COMMAND_NAMES[cmd] | ✓ VERIFIED | exceptions repointed, parser wired, both globals() replaced |
| `tests/test_codec.py` | 10 format_message tests | ✓ VERIFIED | 10 methods, imports format_message, GREEN |
| `tests/test_address_parser.py` | hex/decimal/None/invalid tests | ✓ VERIFIED | 10 methods, GREEN |

### Key Link Verification

| From | To | Via | Status |
| ---- | -- | --- | ------ |
| eprom_operations.py / firmware.py / hardware.py / serial_comm.py | firestarter.exceptions | `from firestarter.exceptions import …` | ✓ WIRED |
| serial_comm.py | firestarter.frame_parser | re-export `(MAGIC_PREAMBLE, LogMessage, Response, _crc8_ccitt, _decode_param)` `# noqa: F401` | ✓ WIRED |
| test_decoder.py | firestarter.serial_comm | imports 4 symbols, resolved via re-export (test unchanged) | ✓ WIRED |
| codec.py | firestarter.frame_parser | `from firestarter.frame_parser import _decode_param` (D-08) | ✓ WIRED |
| serial_comm.py | firestarter.codec | `_decode_id_frame` calls `codec.format_message` (2 hits) | ✓ WIRED |
| eprom_operations.py | firestarter.address_parser | `from firestarter.address_parser import parse_address, parse_size` in try/except | ✓ WIRED |
| eprom_operations.py | constants.COMMAND_NAMES | `COMMAND_NAMES[cmd]` at both sites (via star-import) | ✓ WIRED |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| exceptions import + inheritance | `python -c "from firestarter.exceptions import …; assert issubclass(...)"` | exceptions OK | ✓ PASS |
| frame_parser CRC + preamble | `_crc8_ccitt(b'123456789')==0xF4`, `MAGIC_PREAMBLE==b'\xaa\x55\xaa\x55'` | frame_parser OK | ✓ PASS |
| codec.format_message pure (no instance) | `format_message(MSG_OK_REV,[0,0xFF],entry)=='Rev 0'`; chunk; unknown→None | codec OK | ✓ PASS |
| address_parser hex/dec/None/raise | parse_address/parse_size all-case check | address_parser OK | ✓ PASS |
| entry point installs | `firestarter --help` | exit 0, full subcommand list | ✓ PASS |
| full suite | `python -m pytest` | 182 passed, 2 xfailed, 29 snapshots | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
| ----------- | ----------- | ------ | -------- |
| STRUCT-01 | 38-02 | ✓ SATISFIED (code) | frame_parser.py extracted with CRC8/_decode_param/Response/LogMessage, testable without serial I/O, test_decoder.py unchanged. NOTE: REQUIREMENTS.md wording lists `_decode_id_frame` as a frame_parser member, but locked decision D-06 (CONTEXT.md, pre-execution) keeps it in serial_comm.py because it is package-coupled to CATALOG+codec — deferred to Phase 40. This is a documented, intentional deviation, not a gap. The requirement's core intent (frame parsing extracted, independently testable) is delivered. |
| STRUCT-02 | 38-03 | ✓ SATISFIED (code) | codec.py with format_message + revision-silkscreen rendering, separated from frame parsing and logging side effects. |
| STRUCT-03 | 38-04 | ✓ SATISFIED (code) | address_parser.py with explicit ValueError validation; _setup_operation consumes it. |
| STRUCT-04 | 38-01 | ✓ SATISFIED (code) | exceptions.py consolidates 8 classes from serial_comm/eprom_operations/hardware/firmware. |
| STRUCT-05 | 38-05 | ✓ SATISFIED (code) | read_data_block deleted; both globals() introspection sites replaced with COMMAND_NAMES[cmd]; functools/operator dead imports cleaned up as a cascade of the deletion. |

REQUIREMENTS.md currently shows STRUCT-01..05 as "Pending" — this is EXPECTED per the task brief (orchestrator flips traceability AFTER verification passes). All 5 requirement IDs are claimed by exactly one plan each; no orphaned IDs. The code delivers each requirement.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| (none) | — | — | — | No TBD/FIXME/XXX debt markers in any changed file. No TODO/HACK/PLACEHOLDER/"not yet implemented" warning markers in changed source. ChipNotFoundError is a designed forward-dependency stub (wired in Phase 39 per D-01), not dead code. No empty-return or hollow-implementation patterns. |

### Deviations Reviewed (all behavior-preserving, all auto-fixed during execution)

- **38-01:** `# noqa: F401` on `FirmwareOperationError` import in firmware.py — orphan kept reachable per D-01; documented. ✓ Benign.
- **38-04:** `or 0` narrowing on `parse_address(address)`/`parse_size(size)` to satisfy mypy `Optional[int]` → int at the `addr`/`addr + read_size` sites. Behavior-identical: `if address:`/`and size` guards already guarantee non-empty strings, so the parser returns an int; `or 0` only collapses a literal 0 to 0. Confirmed against base behavior. ✓ Zero runtime change.
- **38-05:** `functools`/`operator` import removal from serial_comm.py — direct cascade of deleting read_data_block (their only referent). Confirmed 0 remaining references. ✓ Benign.

### Human Verification Required

None. This is a pure-software, behavior-preserving host-CLI refactor with no visual/real-time/external-service surface. The full automated safety net (182 tests + 29 snapshots + ruff + mypy + entry-point install) is the complete acceptance signal, and it is green. Wire protocol and read path are byte-identical (proven by sha256 + empty diffs), so no hardware bench check is needed.

### Gaps Summary

No gaps. All 5 ROADMAP success criteria are delivered in the actual submodule code and verified against git history, runtime behavior, and a live test run — not against SUMMARY claims. All 5 GATE-1.8 standing checks pass, including the two that protect the v1.9 read path: `_read_and_parse_lines` is byte-identical (sha256 match) and the snapshot/CLI surface diff is empty. The four new modules are substantive (not stubs), pure/cycle-safe as specified, and independently testable without serial I/O. Dead code (`read_data_block`, both `globals()` reverse-lookups, orphaned imports) is removed with zero behavior change. The phase goal is achieved.

---

_Verified: 2026-05-27_
_Verifier: Claude (gsd-verifier)_

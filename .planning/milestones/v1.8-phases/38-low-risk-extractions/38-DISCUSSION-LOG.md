# Phase 38: Low-Risk Extractions - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-27
**Phase:** 38-Low-Risk Extractions
**Areas discussed:** Exceptions module membership, frame_parser purity boundary, Ring-fence preservation, address_parser error contract

---

The four gray areas were surfaced because the codebase scout found the ROADMAP Phase 38
success criteria conflict with the actual code (or with each other). The operator answered
the selection question with **"you recommend"** — delegating all four to Claude's judgment
(the same pattern as Phase 37's "what do you recommend? → accept all four"). Claude's
recommendations were locked into CONTEXT.md (D-01…D-16). The options weighed for each area:

## Exceptions module membership

| Option | Description | Selected |
|--------|-------------|----------|
| Literal SC#1 list (7 classes) | Move exactly the 7 named classes; create `ChipNotFoundError`; leave `FirmwareOperationError` in firmware.py | partial |
| 6 existing + ChipNotFoundError + FirmwareOperationError; Avrdude*Error stay | Consolidate all genuine app exceptions; exclude the FileNotFoundError-domain avrdude pair | ✓ |
| Move everything incl. Avrdude*Error | Strictest reading of "no exception class outside this module" | |

**User's choice:** "you recommend" → Claude recommendation (option 2).
**Notes:** `ChipNotFoundError` created now per Phase 39's `Depends on: Phase 38` contract.
`FirmwareOperationError` included (orphaning it half-does the job). `AvrdudeNotFoundError` /
`AvrdudeConfigNotFoundError` excluded — they subclass `FileNotFoundError`, a tooling/filesystem
domain, and live in the self-contained avr_tool.py. No `FirestarterError` base (would change
`isinstance` = behavior change; deferred to Phase 42). → D-01, D-02, D-03, D-04.

---

## frame_parser purity boundary

| Option | Description | Selected |
|--------|-------------|----------|
| (a) Pure primitives only; `_decode_id_frame` stays in serial_comm.py | Honor "stdlib + typing only"; defer the orchestrator to Phase 40 | ✓ |
| (b) frame_parser imports CATALOG + codec | Keep SC#2's literal symbol list, relax the purity rule | |
| (c) `_decode_id_frame` made pure via dependency injection | Inject catalog + render callback so it can live in frame_parser | |

**User's choice:** "you recommend" → Claude recommendation (option a).
**Notes:** `_decode_id_frame` references `CATALOG` (messages.py) + calls `_format_message`
(→codec.py), so it cannot be both "in frame_parser" AND "stdlib + typing only". Purity is the
load-bearing constraint (it's what makes frame_parser independently testable = the point of
STRUCT-01). Documented deviation from SC#2's symbol list; flagged for plan-checker. Option (c)
deferred to Phase 40. → D-05, D-06, D-07.

---

## Ring-fence preservation

| Option | Description | Selected |
|--------|-------------|----------|
| Keep `_decode_id_frame` in place → generator untouched | Falls out of frame_parser option (a); zero edits to `_read_and_parse_lines` | ✓ |
| Thin delegating shims on SerialCommunicator | Needed only if `_decode_id_frame` were extracted; keeps generator body byte-identical | |
| Direct call-site edit inside the generator | Edit `self._decode_id_frame(...)` in the ring-fenced body | |

**User's choice:** "you recommend" → Claude recommendation (option 1).
**Notes:** Because `_decode_id_frame` stays (D-06), the ring-fenced `_read_and_parse_lines`
call site at serial_comm.py:662 is byte-identical with no change — no shims required. The
`# DO NOT MODIFY` marker stamp stays Phase 40's job per roadmap sequencing. → D-09, D-10.

---

## address_parser error contract

| Option | Description | Selected |
|--------|-------------|----------|
| Parser raises ValueError; call site wraps to preserve graceful-fail | SC#4-compliant parser; `_setup_operation` keeps the exact log + `return None,0` | ✓ |
| Parser returns None on bad input (non-raising) | Mirrors today's inline behavior but contradicts SC#4 | |
| Let the raise propagate (change CLI behavior) | Simplest, but breaks GATE-1.8b / Phase 36 snapshots | |

**User's choice:** "you recommend" → Claude recommendation (option 1).
**Notes:** Current inline parse logs `"Invalid address/size format: …"` and returns `(None, 0)`.
The extracted `parse_address`/`parse_size` raise ValueError (SC#4); `_setup_operation` wraps both
in try/except to preserve byte-identical CLI behavior. Subtlety preserved: `command_dict["address"]`
is set only when an address is actually passed (no `address=0` injection). → D-11, D-12, D-13.

---

## Claude's Discretion

- Module docstrings / function ordering in each new file; `parse_size` return type; whether to
  wrap `int()`'s ValueError with a custom message.
- Public-vs-private naming where a SC is silent (SC literals followed: `format_message` public,
  frame_parser primitives keep `_`).
- Test-file organization beyond the two SC-mandated new files; optional exceptions import-smoke test.
- Plan/wave decomposition; recommended dependency-safe order: exceptions → frame_parser → codec →
  address_parser → dead-code sweep, each an atomic suite-green commit.
- STRUCT-05 mechanics (D-14/D-15/D-16): `read_data_block` delete (zero callers confirmed),
  `globals()` → `COMMAND_NAMES[cmd]`, confirmed-dead comment removal only.

## Deferred Ideas

- Unifying `FirestarterError` base class → Phase 42 (Error Handling Normalization).
- `_decode_id_frame` as a pure DI function (so it could live in frame_parser) → Phase 40.
- Three reviewed-not-folded hardware/protocol todos (avrdude-fallback, COBS-resync,
  w27c512-misclassification) — out of scope; carried forward unchanged from Phase 37's review.

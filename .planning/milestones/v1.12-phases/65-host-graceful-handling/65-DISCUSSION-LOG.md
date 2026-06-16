# Phase 65: Host Graceful Handling - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-11
**Phase:** 65-host-graceful-handling
**Areas discussed:** Detection mechanism, Protocol value rendering, CLI message framing

---

## Detection mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Match message id `0xBB` | Add an `id` field to the `Response` namedtuple, thread it from the decoded `LogMessage` (which already carries `id`), detect on `id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`. Robust to format-string changes; slightly larger change (touches `frame_parser`/`serial_comm` Response construction). | ✓ |
| Substring `not implemented` | Match the literal SC#2 way — check rendered ERROR text for "not implemented". Minimal change, but brittle to format edits and to the prefixed text ("Programmer error during init: ..."). | |
| You decide | Let the planner pick least-risk. | |

**User's choice:** Match message id `0xBB`
**Notes:** Chosen over the literal SC#2 substring phrasing because the decode path drops the id today and id-matching is a strict robustness improvement. SC#2 intent is still satisfied — the pytest mock carries both the catalog format string and `id=0xBB`; the assertion is on the typed raise.

---

## Protocol value rendering

| Option | Description | Selected |
|--------|-------------|----------|
| Surface firmware text verbatim | Pass the already-rendered firmware string through unchanged → `0x0b`. Single source of truth (firmware owns rendering), no re-parsing. | ✓ |
| Host re-renders to u32 width | Parse the value out and re-render as `0x%08X` → `0x0000000B` to match the SC#3 example exactly. Requires carrying the raw value to the host; string-parsing the text back is fragile. | |

**User's choice:** Surface firmware text verbatim
**Notes:** The SC#3 example `Protocol 0x0000000B not implemented` is treated as illustrative of intent (message includes the protocol value), not a literal width contract. The verbatim `0x0b` text meets SC#3's real bar.

---

## CLI message framing

| Option | Description | Selected |
|--------|-------------|----------|
| Prefix + firmware text | New distinct prefix (not "Programmer error:"), keeps firmware text, adds known-but-unsupported framing. E.g. `Unsupported protocol: Protocol 0x0b not implemented — this protocol is recognized but not yet implemented in firmware.` | ✓ |
| Rephrased single sentence | Host composes its own sentence from the protocol value, not reusing firmware text verbatim. | |
| You decide | Planner writes exact wording satisfying SC#3. | |

**User's choice:** Prefix + firmware text
**Notes:** Exact wording left to planner within three constraints — distinct prefix from "Programmer error:", includes the verbatim firmware text (carrying the protocol value), and communicates known-but-not-yet-supported.

---

## Claude's Discretion

- **Where the typed raise lives** within `_run_state_machine` (three ERROR raise sites: `_execute_phase`, `_main_phase_simple`, outer catch) — lean toward a centralized `_raise_for_error_response` helper.
- **Exact CLI wording** within the D-03 constraints.
- **pytest file placement / fixture style** for the mocked ERROR response — reuse existing `tests/` conventions.

## Deferred Ideas

- Host capability reporting / pre-flight `support_status` guards on `info`/`write`/`read`/`verify` — Phases 66–68 (Phase 68 reuses this phase's `map_typed_errors` error surface).
- DB inclusion of unimplemented-protocol chips + NMOS VPP correction — Phase 66.

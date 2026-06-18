# Phase 65: Host Graceful Handling - Context

**Gathered:** 2026-06-11
**Status:** Ready for planning

<domain>
## Phase Boundary

When the firmware emits `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (`0xBB`, rendered
`"Protocol 0x%02x not implemented"`, `RESPONSE_CODE_ERROR`) — the new
fail-closed dispatch outcome shipped in Phase 64 — the **host** must (a) raise a
typed `ProtocolNotImplementedError(EpromOperationError)` instead of a generic
`EpromOperationError`, and (b) print a clear, actionable CLI message that
includes the protocol value and communicates *known-but-not-yet-supported*,
distinct from a generic "Programmer error". HOST-ONLY (`firestarter_app/`);
pytest-provable with mocked responses, **no bench required**.

**In scope (this phase — host sub-repo `firestarter_app/` only):**
- New `ProtocolNotImplementedError(EpromOperationError)` in
  `firestarter/exceptions.py` (HOST-01).
- Detection in the `_run_state_machine` error path of
  `firestarter/eprom_operations.py`: an ERROR response carrying message id
  `0xBB` raises `ProtocolNotImplementedError` (HOST-01).
- Plumbing the decoded message `id` through the `Response` namedtuple so the
  id reaches the raise site (see D-01).
- A `ProtocolNotImplementedError` arm in `map_typed_errors`
  (`firestarter/cli_handlers.py`), ordered **before** the `EpromOperationError`
  arm, producing the actionable CLI message (HOST-02).
- pytest covering: the subclass relationship, the id-`0xBB` → typed-raise path
  (mocked ERROR response), the CLI message content (includes protocol value +
  known-but-unsupported framing), and the catch ordering. CI green.

**Out of scope (later phases / not this phase):**
- Firmware emitting `0xBB` — **done** in Phase 64 (`configure_not_implemented`).
- The `0xBB` catalog constant + format string — **done** in Phase 63
  (`messages.py:111` + MessageDef at `messages.py:644-651`).
- DB `support_status` taxonomy + host capability reporting / pre-flight guards
  on `info`/`write`/`read`/`verify` — Phases 66–68 (DB-01..05, HOST surface
  reuse). **No DB reads, no chip-record capability checks in this phase** — this
  phase only handles the *firmware-reported* runtime error.

</domain>

<decisions>
## Implementation Decisions

### Detection mechanism (HOST-01, SC#2)
- **D-01: Match on message id `0xBB`, not on substring text.** The decode path
  currently builds `Response = namedtuple("Response", ["type","message","payload"])`
  (`frame_parser.py:17`) and **drops** the message id that `LogMessage`
  (`frame_parser.py:23`, fields `["severity","text","id","payload"]`) carries.
  Add an `id` field to the `Response` namedtuple and thread it from the decoded
  `LogMessage` at the construction site (`serial_comm.py:394` —
  `Response(type=decoded.severity, message=decoded.text, payload=decoded.payload)`
  → also pass `id=decoded.id`). Detection then keys on
  `response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`.
  Rationale: robust — survives any future wording change to the
  `"Protocol 0x%02x not implemented"` format string, and avoids the brittleness
  of substring-matching against text that is **prefixed** at the raise sites
  (e.g. `"Programmer error during init: ..."`). (Considered and rejected:
  substring-match on `"not implemented"` — the literal SC#2 phrasing, minimal
  change, but brittle to format edits and to the prefixing.)
  - **SC#2 satisfaction note:** the roadmap wording ("when an ERROR response
    contains 'not implemented' text") is **strengthened**, not violated — the
    pytest mock constructs an ERROR `Response` carrying both the catalog format
    string **and** `id=0xBB`; the assertion is on the typed raise. The id-match
    is a strict improvement that still passes the SC#2 intent (typed exception
    raised on the catalog not-implemented response).
  - **Add to `Response` defaults:** `id` must default to `None` so every other
    `Response(...)` construction site (text-prefix path at `serial_comm.py:222`,
    the `payload`-only sites) keeps working unchanged. New field placement must
    not break positional callers — append after `payload` or give all new
    fields defaults; planner verifies no positional `Response(...)` callers
    break.

### Protocol value rendering (HOST-02, SC#3)
- **D-02: Surface the firmware-rendered text verbatim.** The firmware emits
  `0x%02x` so the host receives `"Protocol 0x0b not implemented"`. Pass that
  string through unchanged — **firmware owns the rendering** (single source of
  truth); the host does not re-parse the protocol value out of the text. The
  roadmap SC#3 example `"Protocol 0x0000000B not implemented"` (8-digit u32) is
  treated as **illustrative of intent** (message includes the protocol value),
  not a literal width contract. SC#3's real bar — "includes the protocol value"
  — is met by the verbatim firmware text. (Considered and rejected: host
  re-renders to `0x%08X` to match the example exactly — requires carrying the
  raw protocol value separately and/or string-parsing the text back, fragile and
  duplicates the firmware's rendering responsibility.)

### CLI message framing (HOST-02, SC#3)
- **D-03: New distinct prefix + firmware text + known-but-unsupported framing.**
  In `map_typed_errors`, the `ProtocolNotImplementedError` arm raises a
  `click.ClickException` with a message that (a) uses a **new prefix distinct
  from `"Programmer error:"`** (the existing `EpromOperationError` arm), (b)
  includes the verbatim firmware text (which carries the protocol value), and
  (c) communicates that the protocol is recognized/known by the toolchain but
  not yet implemented in firmware. Illustrative shape (planner finalizes exact
  wording): `Unsupported protocol: Protocol 0x0b not implemented — this protocol
  is recognized but not yet implemented in the firmware.` The arm MUST appear
  **before** the `except EpromOperationError` arm (SC#4) so the subclass is
  caught first.

### Claude's Discretion
- **Where the typed raise lives (SC#2 names `_run_state_machine`).** There are
  three `EpromOperationError` raise/return sites reachable from the state
  machine: `_execute_phase` (INIT/END, `eprom_operations.py:340`),
  `_main_phase_simple` (MAIN, `:376`), and the outer `except EpromOperationError`
  catch (`:321`). The configure error most plausibly surfaces during the **INIT**
  phase. **Lean:** introduce a small shared helper (e.g.
  `_raise_for_error_response(response)`) that the ERROR branches call — raising
  `ProtocolNotImplementedError` when `response.id == 0xBB` else
  `EpromOperationError` — so detection is centralized and not duplicated per
  site. Planner/executor may instead detect at a single site if it can prove the
  not-implemented ERROR only ever arrives there; must preserve: all pre-existing
  ERROR paths stay green, and a `0xBB` ERROR anywhere in the state machine yields
  the typed exception.
- **Exact CLI wording** (within D-03's three constraints) — planner's call.
- **pytest file placement / fixture style** for the mocked ERROR response —
  planner's call; reuse the existing test conventions in
  `firestarter_app/tests/`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Edit sites (host sub-repo `firestarter_app/firestarter/`)
- `firestarter_app/firestarter/exceptions.py` — add
  `ProtocolNotImplementedError(EpromOperationError)`. `EpromOperationError` is
  defined here (a bare `Exception` subclass); the new class sits beside it.
- `firestarter_app/firestarter/eprom_operations.py` — `_run_state_machine`
  (error path ~`:316-323`), `_execute_phase` (raise at `:338-341`),
  `_main_phase_simple` (raise at `:374-376`). These are the ERROR→exception
  sites where the typed raise is introduced (see Discretion).
- `firestarter_app/firestarter/cli_handlers.py` — `map_typed_errors`
  (`:106-124`); add the `ProtocolNotImplementedError` arm **before** the
  `EpromOperationError` arm (`:119`). Import the new exception in the
  exceptions-import block (`:31-37`).
- `firestarter_app/firestarter/frame_parser.py:17` — `Response` namedtuple
  (`["type","message","payload"]`, `payload` defaults `None`); add `id`.
  `:23` — `LogMessage` namedtuple already carries `id` (the source of the value).
- `firestarter_app/firestarter/serial_comm.py:389-396` — where the decoded
  `LogMessage` is converted to a `Response` (id currently dropped); thread
  `id=decoded.id`. Also `:222` (text-prefix path) and `:225` construct
  `Response` without id — they rely on the `id` default.

### Wire message (already defined — Phases 63/64; reference only, do not edit)
- `firestarter_app/firestarter/messages.py:111` —
  `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB`. Import this constant for the
  id-match (do NOT hardcode `0xBB`).
- `firestarter_app/firestarter/messages.py:644-651` — `MessageDef` for `0xBB`:
  `format="Protocol 0x%02x not implemented"`, `params=(("u8","hex_byte"),)`,
  `severity=SEVERITY_ERROR`. Confirms the host receives the rendered text and
  the id is decodable.

### Requirements + roadmap
- `.planning/ROADMAP.md` § "Phase 65" (lines 434-447) — goal + 4 success
  criteria.
- `.planning/REQUIREMENTS.md` — HOST-01, HOST-02.

### Prior phase context (decisions carried forward)
- `.planning/phases/64-firmware-fail-closed-dispatch-native-tests/64-CONTEXT.md`
  — D-01 (emit shape, `(uint8_t)handle->protocol` cast, format string);
  integration-points note that this phase is the host decode of the `0xBB`
  firmware emit.
- `.planning/phases/63-catalog-lockstep-wire-change/63-CONTEXT.md` — `0xBB`
  catalog shape, hex render, mirrors `0xAE`.
- `.planning/phases/62-dispatch-baseline-capture-check-dispatch-update/62-CONTEXT.md`
  — D-03 two-bucket model (`protocol==0`+unknown `mem_type` → `0xAE`;
  `protocol!=0` → `0xBB`).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `map_typed_errors` (`cli_handlers.py:106-124`) is the existing
  typed-exception → `click.ClickException` funnel with **ordered** `except`
  clauses (`ChipNotFoundError`, `FirmwareOutdatedError`, `SerialError`,
  `EpromOperationError`, `HardwareOperationError`). Adding a subclass arm above
  `EpromOperationError` is the established pattern — no new mechanism needed.
- `LogMessage` already decodes and carries the message `id`
  (`frame_parser.py:23`); the value exists end-to-end — the only gap is that
  `Response` discards it. D-01 closes that gap with a one-field addition.
- The host already receives the **fully rendered** error text
  (`Response.message == decoded.text`, `serial_comm.py:395`) — no need to format
  the protocol value host-side (D-02).

### Established Patterns
- **Typed service-layer exceptions mapped to `ClickException` with stable exit
  codes** (D-03 lineage, `map_typed_errors` docstring). The new exception is a
  service-layer type surfaced through this single funnel.
- **Subclass-before-base catch ordering** — Python matches the first `except`;
  the subclass arm MUST precede `EpromOperationError` (SC#1 guarantees existing
  `EpromOperationError` catchers keep working; SC#4 guarantees the ordering).
- **`Response` namedtuple with defaulted trailing fields** (`payload=None`
  added in W-04) — the precedent for adding `id=None` without breaking callers.

### Integration Points
- The `0xBB` value flows: meta `messages.toml` → generated `messages.py` (done)
  → firmware emit (Phase 64, done) → **host decode + typed raise + CLI message
  (this phase)**. This phase is the terminal consumer of the `0xBB` runtime
  error.
- pytest mocks the serial layer: tests construct a `Response(type="ERROR",
  message="Protocol 0x0b not implemented", id=0xBB)` (or via the decoder) and
  assert the typed raise + CLI message — no firmware, no bench.

</code_context>

<specifics>
## Specific Ideas

- Detection imports `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` from `messages.py` rather
  than hardcoding `0xBB`.
- The CLI prefix must be visibly distinct from `"Programmer error:"` so an
  operator can tell a not-implemented-protocol case from a generic programmer
  failure at a glance (D-03).
- Test set should include at minimum: (1) `ProtocolNotImplementedError` is a
  subclass of `EpromOperationError`; (2) a mocked `id=0xBB` ERROR response →
  `ProtocolNotImplementedError` raised; (3) the CLI message for that exception
  includes the protocol value and the known-but-unsupported framing; (4) the
  `map_typed_errors` ordering places the subclass arm first (a generic
  `EpromOperationError` still maps to `"Programmer error:"`).

</specifics>

<deferred>
## Deferred Ideas

- Host capability reporting (`firestarter info`/`write`/`read`/`verify`
  pre-flight guards reading `support_status` from the DB) — Phases 66–68
  (DB-01..05, DB-04). That is the *static, pre-send* capability story; this
  phase is the *runtime, firmware-reported* error story. Phase 68 explicitly
  reuses this phase's error-surface (`map_typed_errors`).
- DB inclusion of unimplemented-protocol chips + NMOS VPP correction — Phase 66.

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 65-host-graceful-handling*
*Context gathered: 2026-06-11*

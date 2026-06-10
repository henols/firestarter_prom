# Architecture Research

**Domain:** Firmware protocol dispatch hardening + skeleton handlers (v1.12)
**Researched:** 2026-06-10
**Confidence:** HIGH — all findings grounded in direct source inspection of
`memory.cpp`, `firestarter.h`, `check_dispatch.py`, `serial_comm.py`,
`exceptions.py`, `cli_handlers.py`, and the v1.2 `messages.toml` catalog.

---

## Integration Overview

Three coupled changes must land as a lockstep dual-repo set:

1. **Firmware (`firestarter/`):** fail-closed dispatch in `memory.cpp` + a new
   catalog message `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` in `messages.toml` + a
   `configure_not_implemented()` catch-all stub.

2. **Host (`firestarter_app/`):** codegen re-run so `messages.py` carries the new
   message constant + a new `ProtocolNotImplementedError` exception + wiring in
   `eprom_operations.py` to detect the new ERROR response and raise it + wiring in
   `cli_handlers.py` to map it to a clear CLI message.

3. **Regression gate (`check_dispatch.py`):** new assertion that `dispatch()` never
   returns `"not_implemented"` for any chip in the live database (because all chips
   with gap-protocol entries should have been re-routed in the database or never
   exist in the first place).

---

## System Overview

```
  JSON command (algorithm=<proto_id>)
       |  COBS+CRC8 framed (v1.10)
       v
  +----------------------------------------------------------+
  |  firmware: configure_memory()  (memory.cpp)             |
  |                                                         |
  |  Phase 1: protocol prefix chain (if-return cascade)     |
  |    known & implemented  -> configure_<handler>(handle)  |
  |    non-zero & unknown   -> configure_not_implemented()  |
  |                            MSG_ERR_PROTOCOL_NOT_IMPL    |
  |                            response_code = ERROR        |
  |                                                         |
  |  Phase 2: mem_type fallback (protocol == 0 ONLY)        |
  |    mem_type in {1,3,4,5} -> existing fallback handlers  |
  |    mem_type unknown      -> MSG_ERR_MEM_TYPE_UNSUPPORTED|
  +----------------------------------------------------------+
       |  COBS+CRC8 frame:
       |  ERROR severity + MSG_ERR_PROTOCOL_NOT_IMPLEMENTED
       |  params: [u32 protocol_id]
       v
  +----------------------------------------------------------+
  |  host: serial_comm._read_and_parse_lines()              |
  |    -> frame_parser: id_frame decoded -> LogMessage(ERROR)|
  |    -> Response(type="ERROR",                            |
  |         message="Protocol 0x... not implemented")       |
  +----------------------------------------------------------+
       |  Response.type == "ERROR" + protocol-not-impl text
       v
  +----------------------------------------------------------+
  |  eprom_operations._run_state_machine()                  |
  |    ERROR response -> raise ProtocolNotImplementedError  |
  |      if message matches the catalog text pattern        |
  |    (fallback: EpromOperationError for other ERRORs)     |
  +----------------------------------------------------------+
       |  ProtocolNotImplementedError
       v
  +----------------------------------------------------------+
  |  cli_handlers.map_typed_errors()                        |
  |    ProtocolNotImplementedError ->                       |
  |      click.ClickException("Protocol not implemented:   |
  |        chip <name> uses algorithm 0x{proto:02X} which  |
  |        is recognized but not yet programmed. Check back |
  |        in a future firmware release.")                  |
  +----------------------------------------------------------+
       |  click prints "Error: Protocol not implemented: ..."
       |  exit code 1
```

---

## Decision 1: Fail-Closed Dispatch Placement and mem_type Fallback Disposition

### Where the Unknown-Protocol Decision Belongs

The decision point is **at the end of the protocol-prefix chain in
`configure_memory()`**, before the `mem_type` fallback block begins.

Current structure (lines 73-118 of `memory.cpp`):
- Protocol-prefix if-return chain for KNOWN_PROTOCOLS (13 entries)
- `mem_type` fallback chain for `{1, 3, 4, 5}`
- `LOG_ERROR_ID_U8(MSG_ERR_MEM_TYPE_UNSUPPORTED, ...)` + `RESPONSE_CODE_ERROR`

Target structure (v1.12):
- Protocol-prefix if-return chain: KNOWN_PROTOCOLS + any named skeletons
  -> `configure_not_implemented(handle); return;`
- **New: unknown-protocol guard** -- if `handle->protocol != 0`, call
  `configure_not_implemented(handle)` and `return`
- `mem_type` fallback chain -- reached ONLY when `handle->protocol == 0`
- `LOG_ERROR_ID_U8(MSG_ERR_MEM_TYPE_UNSUPPORTED, ...)` -- unchanged, still reachable

The `handle->protocol != 0` guard is the exact backward-compat cut-point. Any
chip emitted by the regenerated `chip_database.json` has a non-zero `algorithm` field,
so it is always caught by the protocol-prefix chain. The `mem_type` fallback is only
reachable for hand-crafted JSON commands that omit `algorithm` (or send `algorithm: 0`),
which is the legitimate backward-compat use case documented in `CLAUDE.md`.

### mem_type Fallback Disposition: Keep Behind Explicit Guard

**Decision: keep the `mem_type` fallback chain but guard it explicitly on
`handle->protocol == 0`.**

Rationale:
- The fallback serves legitimate use: older host versions, manual bench JSON, or
  test harnesses that predate the `algorithm` field. Deleting it breaks these without
  any safety benefit -- the VPP-hazard path was already closed by BLOCKER-2 (SRAM
  protocols have protocol-prefix dispatch) and WARNING-5 (the AT28C family was re-
  routed to 0x0D in `build_db.py`).
- Keeping it behind `protocol == 0` makes the guard explicit and auditable -- it
  appears as a single readable `if (handle->protocol != 0)` short-circuit before
  the fallback block, not an implicit fall-through.
- Deleting entirely would require updating every test fixture that exercises the
  `make_handle(0, mem_type, cmd)` form. The existing
  `test_protocol_zero_with_mem_type_eprom_dispatches_eprom` test must remain green.
- A whitelist approach (option C) is functionally equivalent but requires maintaining
  a separate list that mirrors the if-return chain -- redundant and drift-prone. The
  `protocol == 0` sentinel is a natural and self-maintaining boundary.

### The 12V VPP Hazard Analysis

The hazard path is: chip with unimplemented protocol + `mem_type=1` (TYPE_EPROM)
-> falls through to `configure_eprom` -> enables VPP boost regulator -> 12V on a
5V chip's pin 1.

With the `protocol != 0` guard, this path is **eliminated for all database chips**.
Every DB chip has a non-zero `algorithm`. Only a hand-crafted JSON command with
`algorithm: 0` AND `type: 1` could still reach `configure_eprom` via the fallback,
which is the intended backward-compat behavior and is the user's explicit instruction.

The existing `check_dispatch.py` GATE-03 VPP-safety guard remains valid and
unchanged. No new VPP-hazard surface is introduced.

---

## Decision 2: Skeleton Handler Structure

### What Constitutes a "Skeleton Protocol" for v1.12

From the v1.11 protocol gap enumeration (`.planning/research/FEATURES.md`):

The DB currently has chips only for the 13 already-dispatched protocols
(`0x05`, `0x06`, `0x07`, `0x08`, `0x0B`, `0x0D`, `0x0E`, `0x10`, `0x27`, `0x28`,
`0x29`, `0x35`, `0x39`). None of the "gap" protocols (`0x11`, `0x2A`, `0x2C`,
`0x2E`, etc.) have any chips in the current database.

Therefore v1.12 does not need named per-protocol skeleton `configure_*` functions:
the **catch-all `configure_not_implemented()`** in `memory.cpp` handles all non-zero
unknown protocols with `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`.

The value of v1.12 is closing the hazard hole and producing a traceable error
message. If future milestones add chips for currently-gap protocols, they add the
dispatch arm AND the real handler together; there is no benefit to a dead stub
in between.

If the roadmap explicitly calls for named skeleton stubs for documentation purposes,
they follow this structure:

### Skeleton `configure_*` Structure

A skeleton recognizes the protocol (the dispatch reaches it) but returns not-
implemented with **zero hardware side effects**. Key invariants:

1. No `rurp_chip_enable()` or `rurp_chip_disable()` call.
2. No `CTRL_VPP_REGULATOR_ENABLE`, `CTRL_VPP_VPE_DROP_ENABLE`, `CTRL_VPP_P1_ENABLE`
   register writes (these enable the boost regulator or route voltage to socket pins).
3. No function pointer assignments to `firestarter_operation_init/main/end` -- the
   main loop must not run any phase after a not-implemented response.
4. Must emit `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` with the protocol ID as a `u32` param
   and set `handle->response_code = RESPONSE_CODE_ERROR`.

Pattern (C++ body of a hypothetical `configure_flash_fwh`):
```cpp
void configure_flash_fwh(firestarter_handle_t* handle) {
    /* FWH / LPC bus -- not supported on RURP parallel bus */
    LOG_ERROR_ID_U32(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, handle->protocol);
    handle->response_code = RESPONSE_CODE_ERROR;
    /* No operation pointers set; no hardware lines touched */
}
```

### File Location for Stubs

**New file `src/proms/not_implemented.cpp`** with a matching
`include/not_implemented.h`. Rationale:
- Keeps `memory.cpp` clean.
- All skeleton stubs are co-located so a future author looking for "what needs
  implementing" finds them in one file.
- `sram.cpp` is the size reference: it is 17 lines. Skeleton stubs are even smaller.
- The file houses `configure_not_implemented()` -- the catch-all:

```cpp
/* catch-all for unrecognized non-zero protocols */
void configure_not_implemented(firestarter_handle_t* handle) {
    LOG_ERROR_ID_U32(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, handle->protocol);
    handle->response_code = RESPONSE_CODE_ERROR;
}
```

The inclusion pattern in `memory.cpp` follows the existing include list:
`#include "not_implemented.h"`.

---

## Decision 3: Not-Implemented Wire Response End-to-End

### New Catalog Entry

Add to `messages.toml` (meta-repo canonical, synced to both sub-repos via
`sync_to_subrepos.sh`):

```toml
[[messages]]
id          = 0xBB
name        = "MSG_ERR_PROTOCOL_NOT_IMPLEMENTED"
severity    = "ERROR"
format      = "Protocol 0x%08lx not implemented"
params      = [{ type = "u32", render = "hex_addr" }]
wire_format = "id_frame"
```

ID `0xBB` is the next free slot in the `0xA0..0xDF` ERROR band after `0xBA`
(`MSG_ERR_MEM_SIZE_TOO_SMALL`). Confirm by inspection before assigning; the catalog
currently ends the ERROR band at `0xBA` per the generated `messages.py`.

The `u32` param carries `handle->protocol` -- future-proof because `protocol` is
declared `uint32_t` in `firestarter_handle_t` even though all current values fit in
a byte.

Codegen (`tools/catalog/codegen.py`) regenerates:
- `firestarter/include/messages.h` (firmware C header)
- `firestarter_app/firestarter/messages.py` (Python constants)

Both are committed; the CI drift gate (`codegen + git diff --exit-code`) catches skew.

### Firmware Emission

```cpp
// in configure_not_implemented():
LOG_ERROR_ID_U32(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, handle->protocol);
handle->response_code = RESPONSE_CODE_ERROR;
```

`LOG_ERROR_ID_U32` is a thin macro wrapping `rurp_log_id_u32` (defined in
`logging_id.h`). No new macro is required.

### Host Frame Reception

The COBS+CRC8 transport (v1.10) is transparent. The `_read_and_parse_lines`
generator in `serial_comm.py` is ring-fenced (GATE-1.8d). When the firmware
emits `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`, the generator yields a
`Response(type="ERROR", message="Protocol 0x<proto> not implemented")` via the
`_decode_id_frame` -> `codec.decode_id_frame` path using the catalog entry's
format string. No changes to `_read_and_parse_lines`.

### New Host Exception

Add to `firestarter/exceptions.py`:
```python
class ProtocolNotImplementedError(EpromOperationError):
    """Raised when firmware reports a recognized-but-unimplemented protocol.

    Distinct from EpromOperationError so the CLI can print an actionable
    "not yet supported" message rather than a generic programmer error.
    Inherits from EpromOperationError so callers catching the parent continue
    to work without modification (backward-compatible widening).
    """
    pass
```

### Detection in `eprom_operations.py`

In `_run_state_machine`, the ERROR branch currently does:
```python
if response.type == "ERROR":
    raise EpromOperationError(
        f"Programmer error during {phase_name.lower()}: {response.message}"
    )
```

Augment with a protocol-not-implemented check. The cleanest approach uses the
decoded message text rather than a raw ID byte, because `_run_state_machine`
operates on `Response` objects (text-level after catalog decode):

```python
from firestarter.exceptions import ProtocolNotImplementedError

if response.type == "ERROR":
    if "not implemented" in (response.message or "").lower():
        raise ProtocolNotImplementedError(
            response.message or "Protocol not implemented"
        )
    raise EpromOperationError(
        f"Programmer error during {phase_name.lower()}: {response.message}"
    )
```

The string match is on text under project control (the catalog format string).
A more robust alternative threads the numeric message ID through `Response`, but
that would require touching the ring-fenced generator; the string match is
sufficient and safe for v1.12.

### CLI Surface in `cli_handlers.py`

Add to `map_typed_errors` (BEFORE the `EpromOperationError` catch -- subclass
must be caught first):
```python
from firestarter.exceptions import ProtocolNotImplementedError

except ProtocolNotImplementedError as e:
    raise click.ClickException(
        f"Protocol not implemented: {e}\n"
        f"This chip's programming algorithm is recognized by the firmware "
        f"but not yet implemented. Future firmware versions may add support."
    ) from e
```

User-visible output:
```
Error: Protocol not implemented: Protocol 0x0000000B not implemented
This chip's programming algorithm is recognized by the firmware
but not yet implemented. Future firmware versions may add support.
```

---

## Decision 4: `check_dispatch.py` Updates

### What the Host Guard Needs

`check_dispatch.py`'s `dispatch()` function currently returns one of:
`configure_eprom`, `configure_eeprom28c`, `configure_flash3`, `configure_flash4`,
`configure_flash_intel`, `configure_sram`, or `ERROR`.

After v1.12 the firmware has one additional outcome: `"not_implemented"` (the
catch-all path). The host guard needs:

1. **`dispatch()` updated** to return `"not_implemented"` for protocols that hit the
   catch-all. Since the current DB has zero chips for gap protocols, this change
   produces no immediate violations -- defense-in-depth for future DB additions.

2. **New assertion**: any chip that resolves to `"not_implemented"` is a FAIL.
   The DB must not contain chips the firmware cannot service.

Updated `dispatch()` function:
```python
def dispatch(protocol, mem_type):
    """Mirror firmware dispatch order after v1.12 fail-closed hardening."""
    if protocol == 0x10: return "configure_flash_intel"
    if protocol == 0x0D: return "configure_eeprom28c"
    if protocol == 0x06: return "configure_flash3"
    if protocol in (0x05, 0x35, 0x39): return "configure_flash4"
    if protocol in (0x07, 0x08, 0x0B): return "configure_eprom"
    if protocol in (0x0E, 0x27, 0x28, 0x29): return "configure_sram"
    # v1.12: any non-zero unknown protocol -> not_implemented (not ERROR)
    if protocol != 0:
        return "not_implemented"
    # mem_type fallback (protocol == 0 only, backward-compat)
    return {
        1: "configure_eprom",
        4: "configure_sram",
        3: "configure_flash3",
        5: "configure_flash4",
    }.get(mem_type, "ERROR")
```

The main scan loop adds a `not_implemented` list and FAIL guard. The PASS message
is updated to include `0 not-implemented chips`.

### `_ALGO_MEM_TYPE` Extension

`_ALGO_MEM_TYPE` maps protocol -> mem_type for the fallback chain simulation.
Gap protocols (`0x11`, etc.) are not in the current DB so no entries are needed now.
If future phases add them, those phases extend `_ALGO_MEM_TYPE` at that time.

---

## Component Boundaries (New vs Modified)

### Firmware sub-repo (`firestarter/`)

| File | Status | Change |
|------|--------|--------|
| `src/proms/memory.cpp` | MODIFIED | Add `protocol != 0` guard before mem_type fallback; add `#include "not_implemented.h"`; call `configure_not_implemented(handle); return;` for non-zero unknown protocols |
| `src/proms/not_implemented.cpp` | NEW | `configure_not_implemented()` catch-all; any named per-protocol skeletons if roadmap requires them |
| `include/not_implemented.h` | NEW | Declaration of `configure_not_implemented()` and any named skeletons |
| `include/messages.h` | MODIFIED (codegen) | `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` added by codegen |
| `tools/catalog/messages.toml` | MODIFIED | Add `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` entry (sync copy from meta-repo) |
| `test/native/avr/test_dispatch/test_configure_memory.cpp` | MODIFIED | Add test asserting non-zero unknown protocol sets `RESPONSE_CODE_ERROR`; keep existing fallback test green |

### Host sub-repo (`firestarter_app/`)

| File | Status | Change |
|------|--------|--------|
| `firestarter/exceptions.py` | MODIFIED | Add `ProtocolNotImplementedError(EpromOperationError)` |
| `firestarter/messages.py` | MODIFIED (codegen) | `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` added by codegen |
| `firestarter/eprom_operations.py` | MODIFIED | Detect "not implemented" ERROR response in `_run_state_machine`; raise `ProtocolNotImplementedError` |
| `firestarter/cli_handlers.py` | MODIFIED | Add `ProtocolNotImplementedError` catch in `map_typed_errors` (before `EpromOperationError`) |
| `tools/check_dispatch.py` | MODIFIED | Update `dispatch()` with `protocol != 0 -> not_implemented` arm; add `not_implemented` list + FAIL guard + PASS message update |
| `tools/catalog/messages.toml` | MODIFIED (sync copy) | Synced from meta-repo via `sync_to_subrepos.sh` |

### Meta-repo (`.planning/`)

| File | Status | Change |
|------|--------|--------|
| `tools/catalog/messages.toml` | MODIFIED | Canonical source; add new entry; run `sync_to_subrepos.sh` |

---

## Build Order (Dependency-Respecting)

The constraint is lockstep: the wire change (new message ID) must land in
firmware and host at the same time. The catalog is the source of truth; codegen
is the distribution mechanism.

**Step 1 -- Catalog + codegen (both repos simultaneously)**
- Edit `messages.toml` in meta-repo; run `sync_to_subrepos.sh`.
- Run codegen in both sub-repos (`codegen.py`); commit generated `messages.h` and
  `messages.py`. CI drift gate green.
- This step has no observable behavior change (nothing calls the new ID yet).
- Confirms the ID value (`0xBB`) is available before any code references it.

**Step 2 -- Firmware: not_implemented stub + memory.cpp guard**
- Create `not_implemented.cpp` / `not_implemented.h` with `configure_not_implemented()`.
- Add `#include "not_implemented.h"` to `memory.cpp`.
- Add `protocol != 0` guard: call `configure_not_implemented(handle); return;`
  immediately after the last known-protocol arm.
- The `mem_type` fallback block is unchanged; its guard (`protocol == 0`) is the
  new implicit condition.
- Run `pio test -e native` -- 15 existing tests green + new unknown-protocol test green.
- All existing `test_protocol_zero_with_mem_type_*` and named-protocol tests unaffected.

**Step 3 -- Host: exception + detection + CLI wiring**
- Add `ProtocolNotImplementedError` to `exceptions.py`.
- Add detection in `eprom_operations._run_state_machine`.
- Add catch in `cli_handlers.map_typed_errors` (before `EpromOperationError`).
- Run pytest -- existing tests green; add unit tests for the new exception path
  using a mocked ERROR response with "not implemented" text.

**Step 4 -- `check_dispatch.py` update + regression gate**
- Update `dispatch()` with `protocol != 0 -> not_implemented` arm.
- Add `not_implemented` FAIL list; update PASS message.
- Run `check_dispatch.py` -- PASS with `0 not-implemented chips` (current DB has
  none in gap protocols).

**Why this order:**
- Step 1 produces no observable change so it can be reviewed cleanly in isolation.
- Step 2 is the firmware behavior change; it is testable with native tests without hardware.
- Step 3 depends on Step 1 (needs the message constant) but is independently testable
  with a mock before any firmware change ships.
- Step 4 is additive to the regression gate; it will not fail until a gap-protocol
  chip appears in the DB, so it can land any time after Step 1.

---

## Patterns to Follow

### Pattern: Zero-Hardware-Effect Stub

`configure_sram` (17 lines, `sram.cpp`) is the reference for a minimal configure
function. The skeleton pattern differs only in emitting an error response rather
than setting operation pointers:

```cpp
/* Reference: configure_sram -- minimal, no hardware side effects */
void configure_sram(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_SRAM);
    /* operation pointers set by default to memory.cpp generic functions */
}

/* Skeleton pattern: error, no hardware */
void configure_not_implemented(firestarter_handle_t* handle) {
    LOG_ERROR_ID_U32(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, handle->protocol);
    handle->response_code = RESPONSE_CODE_ERROR;
}
```

### Pattern: Protocol-Prefix Dispatch Arm Addition

Each new dispatch arm in `memory.cpp` follows the existing
`if (handle->protocol == X) { fn(handle); return; }` form. The group-match form
for multiple protocols sharing a handler is also established. Use the single-
protocol form for any named skeleton arms to keep them individually identifiable.

### Pattern: Subclass Exception for Finer-Grained Catch

`ProtocolNotImplementedError` inheriting from `EpromOperationError` follows the
existing hierarchy (`SerialTimeoutError` inherits from `SerialError`;
`ProgrammerNotFoundError` inherits from `SerialError`). Any existing caller that
catches `EpromOperationError` continues to work; only callers that need to
distinguish the "not yet supported" case add the narrower catch.

### Pattern: Catalog-Driven Lockstep Wire Change

The v1.10 COBS change established the pattern: edit `messages.toml` -> codegen
both sub-repos -> CI drift gate proves both sub-repos carry identical constants.
v1.12 follows this identically for the new ERROR message.

---

## Anti-Patterns to Avoid

### Anti-Pattern: Skeleton That Sets Operation Pointers

**What:** A skeleton that assigns `handle->firestarter_operation_init` (even to
`NULL`) but also calls `rurp_chip_enable()` or touches the control register.

**Why bad:** Even a read operation on an unimplemented protocol would attempt to
cycle the chip enable line, potentially asserting a signal to a sensitive pin.

**Instead:** Emit the error and return immediately. Never set operation pointers
in a not-implemented handler. The main loop checks `response_code` before entering
the INIT/MAIN/END state machine.

### Anti-Pattern: Silent Fallthrough to configure_eprom

**What:** The existing `mem_type == TYPE_EPROM` fallback in `memory.cpp` when
reached by a chip with a non-zero unimplemented protocol.

**Why bad:** This is the exact VPP hazard the v1.12 `protocol != 0` guard eliminates.
It is silent (no error response, no log), and it enables the 12V boost regulator on
a chip that may not have VPP routed to pin 1.

**Instead:** The `protocol != 0` guard short-circuits to `configure_not_implemented`
before the `mem_type` chain is ever reached. Confirmed by the native dispatch tests.

### Anti-Pattern: String-Matching the Error Response Inside `_read_and_parse_lines`

**What:** Inspecting `response.message` for "not implemented" inside the ring-
fenced generator body.

**Why bad:** GATE-1.8d prohibits any change to the `_read_and_parse_lines` body.
The detection logic belongs in `_run_state_machine` (already outside the ring fence)
after the `Response` object is yielded.

**Instead:** Add the `ProtocolNotImplementedError` raise to `_run_state_machine`
via the existing `response.type == "ERROR"` branch -- outside the generator.

### Anti-Pattern: Reusing `MSG_ERR_NOT_SUPPORTED` (0xA5)

**What:** Mapping the not-implemented case to the existing `MSG_ERR_NOT_SUPPORTED`
catalog entry to avoid adding a new catalog entry.

**Why bad:** `MSG_ERR_NOT_SUPPORTED` has no params and an ambiguous format string
("Not supported"). The host cannot reliably distinguish it from command-not-supported
or operation-not-supported. The `ProtocolNotImplementedError` needs concrete evidence
to be raisable; a generic "Not supported" text is fragile.

**Instead:** Add `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` with a `u32` protocol param.

---

## Scalability Considerations

| Concern | Now (743 chips, 13 protocols) | Future (new protocol chip added to DB) |
|---------|-------------------------------|----------------------------------------|
| Adding a real handler | Edit `memory.cpp` + new `src/proms/handler.cpp` | Same as existing pattern |
| Adding a named skeleton | Edit `not_implemented.cpp` + single dispatch arm in `memory.cpp` | Single file, no cascade |
| DB adds a gap-protocol chip | `check_dispatch.py` FAILS at CI -- catches it before ship | Enforces handler-first discipline |
| New message catalog entry | `messages.toml` -> codegen -> 2 generated files | Established pattern (64 entries so far) |
| Host CLI message improvement | `map_typed_errors` catch + string update | Isolated to `cli_handlers.py` |

---

## Sources

All findings are from direct source inspection at HEAD on branch
`v1.11-infoic-decode-correctness` (2026-06-10):

- `/workspaces/firestarter/src/proms/memory.cpp` -- dispatch logic, lines 73-118
- `/workspaces/firestarter/include/firestarter.h` -- `firestarter_handle_t`, response codes, flags
- `/workspaces/firestarter/include/logging_id.h` -- `LOG_ERROR_ID_U32` macro chain
- `/workspaces/firestarter/tools/catalog/messages.toml` -- catalog; ERROR band ends at `0xBA`
- `/workspaces/firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` -- dispatch test pattern
- `/workspaces/firestarter/src/proms/sram.cpp` -- minimal handler reference (17 lines)
- `/workspaces/firestarter_app/tools/check_dispatch.py` -- host-side dispatch mirror + GATE-03
- `/workspaces/firestarter_app/firestarter/serial_comm.py` -- `_run_state_machine` error branch, ring-fence note (GATE-1.8d)
- `/workspaces/firestarter_app/firestarter/exceptions.py` -- exception hierarchy
- `/workspaces/firestarter_app/firestarter/cli_handlers.py` -- `map_typed_errors` pattern
- `/workspaces/firestarter_app/firestarter/messages.py` -- generated constants; `MSG_ERR_MEM_TYPE_UNSUPPORTED = 0xAE`, `MSG_ERR_MEM_SIZE_TOO_SMALL = 0xBA` (confirm 0xBB is free)
- `/workspaces/.planning/research/FEATURES.md` (v1.11) -- protocol gap enumeration table
- `/workspaces/.planning/PROJECT.md` -- v1.12 scope and key decisions record
- `/workspaces/firestarter/CLAUDE.md` -- dispatch order documentation and native test reuse pattern

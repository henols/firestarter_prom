# Stack Research: v1.12 Firmware Protocol Dispatch Hardening + Skeletons

**Domain:** Arduino C++ firmware mechanism additions + dual-repo host lockstep — "not implemented" wire response, skeleton handler pattern, native test extension
**Researched:** 2026-06-10
**Confidence:** HIGH (all findings grounded in actual source files; no inference from documentation alone)

---

## 1. Existing Mechanism Baseline (source-verified)

### Response Codes (`firestarter/include/firestarter.h` lines 53–56)

```c
#define RESPONSE_CODE_OK      1
#define RESPONSE_CODE_DATA    3
#define RESPONSE_CODE_WARNING 2
#define RESPONSE_CODE_ERROR   0
```

These four values are the complete set. They live in `firestarter_handle_t.response_code` (uint8_t). The dispatch consumer in `operation_utils.cpp:_check_response` (lines 322–338) does a `switch` over all four cases; anything else falls through to the `default: return false` branch (same as ERROR). The host never sees `response_code` directly — it sees the wire response which is a COBS-framed ID frame carrying a message ID from the catalog.

The response-code-to-wire-type mapping is: firmware sets `response_code`; the operation loop in `operation_utils.cpp` uses `_check_response()` to decide whether to continue; when the operation ends the final response frame (tagged with severity OK, ERROR, INIT, MAIN, END, DATA, or WARN) is what the host's `serial_comm.py` parses. The severity band of the last emitted catalog frame determines what `response.type` the host sees.

**Key insight:** `response_code` is firmware-internal loop control, NOT the host-visible discriminator. The host discriminates on `response.type` which derives from `entry.severity` in the catalog (`SEVERITY_LABEL` in `messages.py`). An ERROR-severity message ID produces `response.type == "ERROR"` in `serial_comm.py`. So adding a new distinguishable "not implemented" response requires a new **message ID** in the catalog, NOT a new `RESPONSE_CODE_*` constant.

### Message ID Catalog — Codegen Path

The canonical source is at `firestarter/tools/catalog/messages.toml` (meta-repo). A copy exists at `firestarter_app/tools/catalog/messages.toml` (app sub-repo). Codegen via `tools/catalog/codegen.py --language cpp` produces `firestarter/include/messages.h`; `--language python` produces `firestarter_app/firestarter/messages.py`. Both generated files are committed and a CI drift gate (`codegen && git diff --exit-code`) enforces byte-identity.

**Adding a new message ID requires:**
1. Add `[[messages]]` entry in `firestarter/tools/catalog/messages.toml` (meta-repo)
2. Add the identical block to `firestarter_app/tools/catalog/messages.toml`
3. Re-run codegen in both sub-repos; commit generated files
4. CI drift gate fails until generated files are committed

No hand-editing of `messages.h` or `messages.py` is allowed (they are `DO NOT EDIT` generated files).

### Existing Error IDs (relevant subset, from `messages.toml` and generated `messages.h`)

| ID | Name | Params | Current Use |
|----|------|--------|-------------|
| `0xA5` | `MSG_ERR_NOT_SUPPORTED` | none | Generic; used in multiple unrelated places — cannot cleanly mean "protocol not implemented" |
| `0xAE` | `MSG_ERR_MEM_TYPE_UNSUPPORTED` | u8 (mem_type) | Current dispatch error (`memory.cpp` line 117); carries `mem_type` byte but NOT the protocol |
| `0xBA` | `MSG_ERR_MEM_SIZE_TOO_SMALL` | u32 | Last assigned ERROR-band entry |
| `0xBB`–`0xBF` | (unassigned) | — | Next available ERROR-band slots |

`MSG_ERR_NOT_SUPPORTED` (0xA5) is too generic. The host cannot distinguish it from other 0xA5 uses. A dedicated ID is the correct approach.

---

## 2. Recommended New Message ID

### `MSG_ERR_PROTOCOL_NOT_IMPL` = `0xBB`

TOML entry to add to `messages.toml` in both sub-repos:

```toml
[[messages]]
id          = 0xBB
name        = "MSG_ERR_PROTOCOL_NOT_IMPL"
severity    = "ERROR"
format      = "Protocol 0x%02x not implemented"
params      = [{ type = "u8", render = "hex_byte" }]
wire_format = "id_frame"
```

`0xBB` is the next unassigned ERROR-band slot after `0xBA`. Carries the raw `protocol` byte as a u8 param so the host can log which protocol was attempted.

**No new `RESPONSE_CODE_*` is needed.** `RESPONSE_CODE_ERROR` already correctly triggers `expect_ack()` → `return False, response.message` on the host. Adding a fifth response code would require changes to `operation_utils.cpp:_check_response`, `firestarter.h`, and `constants.py`, all for a distinction already achievable at the catalog layer.

Generated effect in `messages.h`:
```c
#define MSG_ERR_PROTOCOL_NOT_IMPL   0xBB
```

Generated effect in `messages.py`:
```python
MSG_ERR_PROTOCOL_NOT_IMPL = 0xBB
```

---

## 3. Dispatch Extension — Fail-Closed Pattern

### Current dispatch tail (`memory.cpp` lines 104–118, source-verified)

```cpp
if (handle->mem_type == TYPE_EPROM) {
    configure_eprom(handle);     // SAFETY HAZARD: 12V VPP on any chip with mem_type=1
    return;
} else if (handle->mem_type == TYPE_SRAM) { ...
} else if (handle->mem_type == TYPE_FLASH_TYPE_3) { ...
} else if (handle->mem_type == TYPE_FLASH_TYPE_4) { ...
}
LOG_ERROR_ID_U8(MSG_ERR_MEM_TYPE_UNSUPPORTED, handle->mem_type);
handle->response_code = RESPONSE_CODE_ERROR;
```

The safety hazard: a chip with an unimplemented `protocol` but `mem_type=1` (EPROM) in the database currently silently routes to `configure_eprom`, which enables the 12V VPP boost regulator. For a chip that does not expect 12V VPP this is a hardware-damage path.

### Recommended Fail-Closed Guard (insert between last protocol block and mem_type chain)

```cpp
// Fail-closed: any non-zero protocol that reached here has no handler.
// Reject before the mem_type fallback so chips with a real protocol cannot
// accidentally route to configure_eprom (12V VPP damage path).
if (handle->protocol != 0) {
    LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPL, (uint8_t)handle->protocol);
    handle->response_code = RESPONSE_CODE_ERROR;
    return;
}
// Legacy mem_type fallback — reachable ONLY when protocol==0
// (hand-crafted JSON or pre-algorithm host versions).
if (handle->mem_type == TYPE_EPROM) { ...
```

Chips in the regenerated `chip_database.json` always carry a non-zero `algorithm` field. After this guard, they can never silently reach `configure_eprom` via the `mem_type` path.

---

## 4. Skeleton Handler Pattern

### What configure_memory() pre-sets before dispatch (source-verified, lines 47–69)

```cpp
handle->firestarter_operation_init = NULL;
handle->firestarter_operation_main = NULL;
handle->firestarter_operation_end = NULL;
handle->firestarter_get_data = memory_get_data;
handle->firestarter_set_data = memory_set_data;
handle->firestarter_set_address = mem_util_set_address;
handle->firestarter_set_control_register = memory_set_control_register;
handle->firestarter_get_control_register = memory_get_control_register;
```

A skeleton handler therefore needs to touch nothing except emit the error and set the response code:

```cpp
// Shared skeleton body — called by any protocol stub that is registered in
// the dispatch but not yet implemented.
static void configure_not_implemented(firestarter_handle_t* handle) {
    // All shared fields pre-set by configure_memory() before dispatch.
    // Operation pointers remain NULL (already set by configure_memory()).
    LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPL, (uint8_t)handle->protocol);
    handle->response_code = RESPONSE_CODE_ERROR;
}
```

**Flash cost:** `configure_not_implemented` is one function. Each skeleton dispatch entry is a 2-line if-return block calling the shared function — AVR `CALL` + `RET` is 4 instruction words (8 bytes). The shared function itself is approximately 30–40 bytes (LOG_ERROR_ID_U8 resolves to already-linked `rurp_log_id_u8`; no new linker pulls). Total for 5 skeleton protocols: ~80–100 bytes. Well within budget.

**SRAM cost:** zero. No stack frames, no local buffers. `rurp_log_id_u8` passes the u8 arg in a register.

### Flash Budget (measured from actual build, 2026-06-10)

| Board | Current Flash | Max Flash | Headroom |
|-------|--------------|-----------|----------|
| Uno (ATmega328P) | 23,216 B (70.8%) | 32,768 B | ~9,552 B free |
| Leonardo (ATmega32U4) | 25,354 B (77.4%) | 32,768 B | ~7,414 B free |
| Uno SRAM | 1,544 B (75.4%) | 2,048 B | 504 B free |
| Leonardo SRAM | 1,983 B (77.5%) | 2,560 B | 577 B free |

Both boards have 7+ KB flash headroom. The v1.12 catalog entry + guard + shared skeleton function + dispatch entries will add well under 300 bytes total. No flash risk.

---

## 5. Host-Side Response Flow (source-verified)

### End-to-end path for a not-implemented protocol error

1. Firmware: `LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPL, (uint8_t)handle->protocol)` + `handle->response_code = RESPONSE_CODE_ERROR`
2. Operation loop in `operation_utils.cpp:_check_response` returns `false`; operation aborts
3. Firmware emits the ID frame with `severity=ERROR` over COBS+CRC8
4. Host `serial_comm.py:_decode_id_frame` → `codec.decode_id_frame` decodes: `LogMessage(severity="ERROR", text="Protocol 0xNN not implemented", id=0xBB, ...)`
5. `get_response()` returns `Response(type="ERROR", message="Protocol 0xNN not implemented")`
6. `expect_ack()` returns `(False, "Protocol 0xNN not implemented")`
7. `_execute_phase()` raises `EpromOperationError("Programmer error during init: Protocol 0xNN not implemented")`
8. `@map_typed_errors` in `cli_handlers.py` (line 119): `raise click.ClickException(f"Programmer error: {e}")`
9. Click prints: `Error: Programmer error: Protocol 0xNN not implemented`

This flow works without any new Python exception class or changes to `serial_comm.py`, `eprom_operations.py`, or `cli_handlers.py` beyond what the catalog entry provides.

### Host changes required for v1.12

| File | Change | Required? |
|------|--------|-----------|
| `firestarter_app/tools/catalog/messages.toml` | Add `MSG_ERR_PROTOCOL_NOT_IMPL = 0xBB` entry | YES — lockstep |
| `firestarter_app/firestarter/messages.py` | Regenerated by codegen | YES — committed |
| `firestarter_app/firestarter/exceptions.py` | No change | No |
| `firestarter_app/firestarter/serial_comm.py` | No change | No |
| `firestarter_app/firestarter/eprom_operations.py` | No change | No |
| `firestarter_app/firestarter/cli_handlers.py` | No change | No |

The message text "Protocol 0xNN not implemented" delivered via `EpromOperationError` is the user-facing result. It is specific enough for v1.12.

---

## 6. Lockstep Sync Path

### Full change sequence

1. **`firestarter/tools/catalog/messages.toml`** (firmware sub-repo): add `[[messages]]` at `id = 0xBB`
2. **`firestarter_app/tools/catalog/messages.toml`** (app sub-repo): add identical block
3. **`firestarter/include/messages.h`**: regenerate via `python tools/catalog/codegen.py --language cpp --output include/messages.h tools/catalog/messages.toml`; commit
4. **`firestarter_app/firestarter/messages.py`**: regenerate via `python tools/catalog/codegen.py --language python --output firestarter/messages.py tools/catalog/messages.toml`; commit
5. **`firestarter/src/proms/memory.cpp`**: add `configure_not_implemented()` helper, fail-closed guard, dispatch entries for any skeleton protocols
6. **`firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`**: extend with fail-closed and skeleton tests

Note: no `sync_to_subrepos.sh` exists in either catalog directory (checked 2026-06-10). Manual copy of the TOML block is the actual practice.

### What does NOT require changes

- `firestarter.h` (response codes): no new `RESPONSE_CODE_*`
- `constants.py` (flag/command mirror): no changes — `MSG_ERR_PROTOCOL_NOT_IMPL` is a catalog detail, not a command constant
- `exceptions.py`: no new exception class for v1.12 scope
- `frame_parser.py`, `codec.py`: no changes — `0xBB` with ERROR severity decodes cleanly through the existing path

---

## 7. Native Test Extension

### Pattern (grounded in existing `test_configure_memory.cpp`, lines 149–190)

The existing test suite at `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` uses `make_handle(protocol, mem_type, cmd)` → `configure_memory(&h)` → `TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, ...)` for negative tests.

Three new test cases are needed:

```cpp
// 1. Fail-closed: previously protocol=unknown + mem_type=EPROM routed to
//    configure_eprom (12V VPP hazard). After v1.12 it must error.
void test_unknown_protocol_with_eprom_mem_type_now_errors(void) {
    firestarter_handle_t h = make_handle(0xFF, 1, CMD_READ); // TYPE_EPROM=1
    configure_memory(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

// 2. Legacy path preserved: protocol=0 with known mem_type still routes via
//    the mem_type fallback. This test must remain GREEN after the guard.
//    (Already exists as test_protocol_zero_with_mem_type_eprom_dispatches_eprom)

// 3. For each skeleton protocol registered in v1.12 dispatch:
void test_protocol_0xXX_skeleton_returns_error(void) {
    firestarter_handle_t h = make_handle(0xXX, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}
```

**Existing tests that must remain GREEN** after the fail-closed guard change:
- `test_unknown_protocol_with_unknown_mem_type_errors` (protocol=0, mem_type=99): still GREEN — `protocol==0` bypasses the new guard, falls through to `mem_type=99` → `MSG_ERR_MEM_TYPE_UNSUPPORTED` → ERROR
- `test_protocol_zero_with_mem_type_eprom_dispatches_eprom` (protocol=0, mem_type=1): still GREEN — `protocol==0` bypasses the guard, `mem_type=1` → `configure_eprom` → OK
- All 13 protocol-positive tests (protocol=known, mem_type=0): still GREEN — they are handled before the new guard

**Serial stub already covers `rurp_log_id_u8`:** the `setUp()` in the test file stubs `Serial.write` and `Serial.flush`. `LOG_ERROR_ID_U8` → `rurp_log_id_u8` uses Serial.write. No new stub additions needed.

---

## 8. What NOT to Add

| Avoid | Why |
|-------|-----|
| New `RESPONSE_CODE_*` constant | No new value is needed; host discriminates on message ID (catalog severity band), not response_code. Adds risk to `_check_response` switch + constants.py parity with zero benefit. |
| `ProtocolNotImplementedError` Python exception subclass | Not required for v1.12 ("framework + skeletons" scope). `EpromOperationError` with specific message text is sufficient. Defer to a milestone needing programmatic detection. |
| Removing the `mem_type` fallback entirely | It must survive for `protocol==0` (hand-crafted JSON, dev tools, older host). Guard with `if (handle->protocol != 0)`, do not delete the fallback. |
| Separate skeleton `.cpp` files per protocol | Unnecessary flash cost and file proliferation. One shared `configure_not_implemented()` helper is the right shape. |
| Modifying `firestarter_handle_t` | No new fields needed; `response_code` + catalog MSG ID carry all required information. |
| Changing `MSG_ERR_MEM_TYPE_UNSUPPORTED` (0xAE) | It remains correct for the `protocol==0` + unknown `mem_type` path. Do not repurpose it. |

---

## Sources

| Source | File / Location | Confidence |
|--------|-----------------|------------|
| Firmware response codes | `firestarter/include/firestarter.h` lines 53–56 | HIGH (direct read) |
| Dispatch chain | `firestarter/src/proms/memory.cpp` lines 45–118 | HIGH (direct read) |
| Message catalog (canonical) | `firestarter/tools/catalog/messages.toml` | HIGH (direct read) |
| Generated C++ header | `firestarter/include/messages.h` | HIGH (direct read) |
| Generated Python module | `firestarter_app/firestarter/messages.py` | HIGH (direct read) |
| Codegen pipeline | `firestarter/tools/catalog/codegen.py` | HIGH (direct read) |
| Host error flow | `firestarter_app/firestarter/serial_comm.py`, `eprom_operations.py`, `exceptions.py`, `cli_handlers.py` | HIGH (direct read) |
| Native test pattern | `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` | HIGH (direct read) |
| Flash budget | `pio run -e uno/leonardo --target size` (live build, 2026-06-10) | HIGH (measured) |
| v1.12 scope | `.planning/PROJECT.md` lines 16–32 | HIGH (direct read) |

---

*Stack research for: v1.12 Firmware Protocol Dispatch Hardening + Skeletons*
*Researched: 2026-06-10*

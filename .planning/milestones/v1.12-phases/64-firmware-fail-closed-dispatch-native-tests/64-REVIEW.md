---
phase: 64-firmware-fail-closed-dispatch-native-tests
reviewed: 2026-06-11T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - firestarter/include/not_implemented.h
  - firestarter/src/proms/not_implemented.cpp
  - firestarter/src/proms/memory.cpp
  - firestarter/test/native/avr/test_not_implemented/test_not_implemented.cpp
  - firestarter/test/native/avr/test_not_implemented/host_stubs.cpp
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
---

# Phase 64: Code Review Report

**Reviewed:** 2026-06-11
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Phase 64 makes protocol dispatch fail closed. A new `configure_not_implemented()`
handler NULLs all three operation pointers, emits `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`
(0xBB), and sets `RESPONSE_CODE_ERROR`. Two new dispatch arms in
`configure_memory` route named-infeasible protocols (0x11, 0x2A-0x2C) and any
non-zero unrecognized protocol to this handler before the legacy `mem_type`
fallback.

**The core security objective is met and verified by tracing the call chain.**
The dispatch ordering is correct: the generic `protocol != 0` guard (memory.cpp:116)
sits after all named/implemented arms and before the `mem_type` fallback (line 122),
so no non-zero unimplemented protocol can reach `configure_eprom`/`configure_sram`
or any VPP-enabling handler. The error propagates correctly:
`configure_not_implemented` → `RESPONSE_CODE_ERROR` → `_check_response()` returns
false (operation_utils.cpp:331) → `_execute_operation` returns `ERROR` →
`op_execute_function` returns false → caller emits `MSG_ERR_SETUP` and aborts
(firestarter.cpp:86-89). All three operation pointers are NULLed, so even if
execution were somehow attempted, `op_execute_stateful_operation` short-circuits
on the NULL `firestarter_operation_main` (operation_utils.cpp:63). The host
(`firestarter_app/firestarter/messages.py:644`) decodes 0xBB, and the firmware/host
constants are in sync. **No BLOCKER found.**

The findings below concern the "zero hardware side effects" claim precision,
diagnostic ambiguity on >8-bit protocol values, and a test-coverage weakness
that lets the named-arm tests pass vacuously.

## Warnings

### WR-01: "Zero hardware side effects" claim is imprecise — register writes occur before dispatch

**File:** `firestarter/src/proms/memory.cpp:72`
**Issue:** `configure_memory` calls `mem_util_set_address(handle, 0)` at line 72,
*before* any dispatch arm — including the not-implemented path. That function
unconditionally writes the LSB, MSB, and CONTROL registers
(memory.cpp:178/181/184). So the phase claim of "zero hardware side effects" for
unimplemented protocols is not literally accurate: three register writes always
happen.

The good news, verified by reading `mem_util_calculate_top_address_register`
(lines 157-171): for address 0 the computed `top_address` only *preserves*
existing VPP bits via `rurp_read_from_register(CONTROL_REGISTER) & mask` — it
never newly asserts `CTRL_VPP_REGULATOR_ENABLE`. So the 12V VPP hazard is not
re-introduced. The risk is the inaccurate invariant in the docs/comment, which
could mislead a future maintainer who moves VPP-enabling logic earlier, or who
trusts the "zero side effects" wording when reordering dispatch.

**Fix:** Tighten the comment in `configure_memory` and the CLAUDE.md wording to
"no *VPP-enabling* side effects; the pre-dispatch `mem_util_set_address(0)` writes
only address/control registers and preserves (does not assert) VPP bits." Better
yet, consider moving the `mem_util_set_address(handle, 0)` call to *after* the
dispatch arms (or into the implemented-handler arms) so the not-implemented path
truly touches no hardware:
```c
    // dispatch arms first; only call mem_util_set_address(0) on a recognized
    // protocol/mem_type, after the fail-closed guards have returned.
```

### WR-02: Protocol > 0xFF logs an ambiguous/colliding diagnostic byte

**File:** `firestarter/src/proms/not_implemented.cpp:17`
**Issue:** `handle->protocol` is `uint32_t` (firestarter.h:89). The dispatch guard
`handle->protocol != 0` correctly uses the full 32-bit value, so behavior is
right. But the diagnostic emits only the low 8 bits:
`LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, (uint8_t)handle->protocol)`.
A protocol value such as `0x100` or `0x107` would be reported as `0x00` / `0x07`,
making the host-side error message indistinguishable from protocol 0 or a valid
0x07. This hampers field diagnosis of a malformed/unknown `algorithm` value —
exactly the case this handler exists to surface.

Note also the `(uint8_t)` cast is redundant: `LOG_ID_U8` (logging_id.h:33) already
casts its argument to `uint8_t`. The cast hides the truncation rather than
documenting it.

**Fix:** If protocol IDs are expected to fit in a byte, validate/document that at
the parse boundary. Otherwise emit the full value, e.g. via a U32 logging macro
if one exists, or log a wider field:
```c
    // emit the full protocol value so >0xFF unknowns are not aliased to a byte
    LOG_ERROR_ID_U32(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, handle->protocol);
```
At minimum drop the redundant cast and add a comment that protocol is truncated
to 8 bits for logging.

### WR-03: Named-infeasibility tests pass vacuously — they cannot distinguish the named arm from the generic guard

**File:** `firestarter/test/native/avr/test_not_implemented/test_not_implemented.cpp:50-84`
**Issue:** The named arm (memory.cpp:107-111) and the generic guard
(memory.cpp:116-119) both call the *identical* `configure_not_implemented(handle)`
and produce identical observable state (ERROR + three NULL pointers). The four
tests for 0x11/0x2A/0x2B/0x2C assert only that observable state. Therefore if the
entire named-arm block (lines 107-111) were deleted, those protocols would fall
through to the generic guard and the tests would *still pass*. The tests do not
actually protect the DISP-04 named-arm requirement they claim to cover — they are
behaviorally equivalent to the 0x99 generic-catch-all test.

This is a real coverage gap: a refactor that drops the named arm (e.g. someone
"simplifying" by relying on the generic guard) would be undetected, silently
losing the explicit FWH/GAL/PLD recognition the phase committed to.

**Fix:** Either (a) accept that the named arm is redundant with the generic guard
and document it as intentional belt-and-suspenders (then the tests are fine as
regression anchors), or (b) make the named arm observably distinct so the test
can prove it fired — e.g. have `configure_not_implemented` accept/derive a
reason sub-code, or assert on the emitted log id/argument via a recording stub:
```c
    // record the last LOG_ERROR_ID_U8 id+arg in the stub, then:
    TEST_ASSERT_EQUAL(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, last_log_id);
    TEST_ASSERT_EQUAL(0x11, last_log_arg);  // proves the 0x11 value reached the handler
```
The current `host_stubs.cpp` no-ops `rurp_log_id_u8`, so nothing observes the
emitted id — adding a recording stub would also strengthen WR-02 coverage.

## Info

### IN-01: No test for protocol==0 with an unsupported mem_type (the surviving error tail)

**File:** `firestarter/test/native/avr/test_not_implemented/test_not_implemented.cpp:97-104`
**Issue:** The suite re-asserts that protocol==0 + mem_type=1 still dispatches to
EPROM (good — guards against the fail-closed guard over-firing). But there is no
test for protocol==0 + an unsupported mem_type (e.g. mem_type=2 or 0xFF), which is
the only path that now reaches the `MSG_ERR_MEM_TYPE_UNSUPPORTED` tail at
memory.cpp:135. That tail is the one remaining error exit not covered by Phase 64
tests, and a future reorder of the guard could accidentally shadow it.
**Fix:** Add a case `make_handle(0, 0xFF, CMD_READ)` asserting `RESPONSE_CODE_ERROR`
and three NULL pointers, documenting that the `mem_type`-unsupported tail is still
reachable for protocol==0.

### IN-02: Redundant `(uint8_t)` cast in handler

**File:** `firestarter/src/proms/not_implemented.cpp:17`
**Issue:** As noted in WR-02, `LOG_ID_U8` already casts to `uint8_t`; the explicit
cast here is dead/redundant and obscures the silent truncation of the 32-bit
protocol value.
**Fix:** Remove the redundant cast (or replace with a wider log per WR-02) and add
a one-line comment if truncation is intentional.

---

_Reviewed: 2026-06-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

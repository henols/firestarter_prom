# Phase 64: Firmware Fail-Closed Dispatch + Native Tests - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-11
**Phase:** 64-firmware-fail-closed-dispatch-native-tests
**Areas discussed:** Handler cohesion & emit ownership, Named infeasibility arms, Native test placement

---

## Handler cohesion & emit ownership

| Option | Description | Selected |
|--------|-------------|----------|
| Self-contained handler | `configure_not_implemented()` emits `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` with `handle->protocol`, sets `RESPONSE_CODE_ERROR`, leaves all 3 op pointers NULL; dispatch arms just call it. Cleanest for the TEST-01 assertion. | ✓ |
| Inline emit in configure_memory | Mirror the existing 0xAE pattern (`memory.cpp:117`); thin no-op marker handler; emit + response_code in `configure_memory`. | |

**User's choice:** Self-contained handler
**Notes:** Behavior lives in one testable unit — the TEST-01 "no op pointers + ERROR response" assertion targets a single function. Deliberately does NOT mirror the inline 0xAE cohesion pattern.

---

## Named infeasibility arms (0x11 FWH, 0x2A/0x2B/0x2C GAL/PLD)

| Option | Description | Selected |
|--------|-------------|----------|
| Named arms + catch-all guard | Explicit 0x11/0x2A/0x2B/0x2C arms → `configure_not_implemented()`, PLUS a trailing generic `protocol != 0` guard for any other unknown non-zero protocol. Fail-closed AND self-documenting. | ✓ |
| Catch-all guard only | Rely solely on generic `protocol != 0` guard (as check_dispatch.py does); named protocols only appear as test cases. Loses documented intent (roadmap SC#4). | |
| Named arms, no separate catch-all | Explicit arms only; other unknown non-zero protocols fall through to mem_type step-11 error. NOT fail-closed for e.g. 0x99. | |

**User's choice:** Named arms + catch-all guard
**Notes:** Satisfies roadmap SC#4 (explicit recognition in dispatch chain) while staying fail-closed for genuinely-unknown protocols. Named arms are functionally subsumed by the generic guard but exist for documented infeasibility intent + dedicated per-protocol tests.

---

## Native test placement

| Option | Description | Selected |
|--------|-------------|----------|
| New suite file | `test_not_implemented.cpp` — keeps NULL-pointer assertion style separate from `test_configure_memory.cpp` (whose header avoids pointer checks because `configure_sram` is a stub). | (Claude's discretion — leaning here) |
| Extend existing file | Add new cases into `test_configure_memory.cpp`; mixes two assertion philosophies in one file. | |

**User's choice:** "you decide" → Claude's discretion
**Notes:** Leaning toward a new sibling suite file under `test_dispatch/` (no platformio.ini change needed). Planner/executor may override if a single-file layout proves cleaner, provided pre-existing cases stay green and the `protocol==0` + `mem_type=1 → configure_eprom` fallback is re-asserted.

## Claude's Discretion

- Native test file placement (new suite file vs extend existing) — leaning new file `test_not_implemented.cpp`.
- Named-arm expression: grouped `if` vs individual `if`s — both acceptable if all four are named and route to `configure_not_implemented()`.
- Whether the handler explicitly re-NULLs op pointers vs relying on `configure_memory`'s top-of-function NULL — explicit preferred for a self-contained handler.

## Deferred Ideas

- Host-side `ProtocolNotImplementedError` + actionable CLI message — Phase 65.
- DB inclusion of unimplemented-protocol chips + NMOS VPP correction — Phase 66.
- Reviewed-not-folded todos: avrdude MCU-detection fallback; COBS frame-level deadline (WR-01) — both unrelated to dispatch fail-closed.

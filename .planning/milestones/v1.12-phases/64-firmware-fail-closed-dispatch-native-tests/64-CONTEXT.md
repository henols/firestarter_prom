# Phase 64: Firmware Fail-Closed Dispatch + Native Tests - Context

**Gathered:** 2026-06-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the firmware dispatch **fail closed**. In `firestarter/src/proms/memory.cpp::configure_memory()`,
every **non-zero** unimplemented `protocol` must now receive an explicit
`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (0xBB) response with the protocol value and
**zero hardware side effects** — instead of falling through the `mem_type`
chain to `configure_eprom` (the 12V-VPP-on-a-5V-part hazard). The legacy
`mem_type` fallback survives **only** behind an explicit `protocol == 0` guard.
A new shared `configure_not_implemented()` handler owns the not-implemented
outcome; the protocols a user might plausibly hand-craft but that are infeasible
on RURP (`0x11` FWH, `0x2A`/`0x2B`/`0x2C` GAL/PLD) get **named arms**, and a
trailing generic `protocol != 0` guard catches everything else. Native (host,
no-hardware) Unity tests prove the new invariants; both boards stay within their
flash ceilings (Leonardo ≤ 90%, the binding constraint).

**In scope (this phase — firmware sub-repo `firestarter/` only):**
- New `src/proms/not_implemented.cpp` + `include/not_implemented.h` exposing
  `configure_not_implemented(firestarter_handle_t*)`.
- Dispatch edits in `configure_memory()`: named arms `0x11`/`0x2A`/`0x2B`/`0x2C`
  → `configure_not_implemented()`, then a generic `protocol != 0` →
  `configure_not_implemented()` guard, both placed **after** all implemented
  protocol cases and **before** the `protocol == 0` `mem_type` fallback.
- Native Unity tests (TEST-01) for: unknown non-zero protocol (e.g. `0x99`) →
  ERROR + NULL op pointers; each named arm → not-implemented; `protocol==0` +
  `mem_type=1` legacy fallback still routes to `configure_eprom` (re-assert);
  all pre-existing dispatch tests stay green.
- Flash-budget verification (TEST-02): `pio run -e leonardo` ≤ 90% (and Uno
  builds clean).

**Out of scope (later phases / not this phase):**
- The `0xBB` catalog constant — **already done** in Phase 63 (present at
  `firestarter/include/messages.h:96`). This phase only *references/emits* it.
- Host-side `ProtocolNotImplementedError` + actionable CLI message — Phase 65
  (HOST-01/02).
- `check_dispatch.py` changes — **already done** in Phase 62 (the host mirror
  already has the `protocol != 0 → not_implemented` arm).
- Any DB inclusion / VPP correction / `support_status` work — Phase 66.

</domain>

<decisions>
## Implementation Decisions

### Handler cohesion & emit ownership (DISP-03, WIRE-02)
- **D-01:** `configure_not_implemented()` is a **self-contained handler**. It
  emits `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` carrying the protocol value, sets
  `handle->response_code = RESPONSE_CODE_ERROR`, and leaves all three operation
  pointers (`firestarter_operation_init`, `firestarter_operation_main`,
  `firestarter_operation_end`) NULL. The dispatch arms in `configure_memory()`
  just call it and `return`. Rationale: keeps the not-implemented behavior in
  one testable unit so the TEST-01 "no op pointers + ERROR response" assertion
  targets a single function — cleaner than the existing inline-emit style at
  `memory.cpp:117` (which this decision deliberately does *not* mirror).
  (Considered and rejected: thin no-op marker handler with the emit done inline
  in `configure_memory`, mirroring the 0xAE `MSG_ERR_MEM_TYPE_UNSUPPORTED`
  pattern — splits behavior across two TUs and weakens the unit test target.)
  - **Note (emit param width):** `handle->protocol` is `uint32_t`
    (`firestarter.h:89`); the wire message param is `u8`/`hex_byte` (Phase 63
    D-01). The named/known protocols are all ≤ `0xFF`, so the emit casts
    `(uint8_t)handle->protocol`. `LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, (uint8_t)handle->protocol)`
    is the expected call shape (mirror of `memory.cpp:117`).

### Named infeasibility arms (DISP-04)
- **D-02:** **Named arms + trailing catch-all guard.** Add explicit recognition
  of `0x11` (FWH), `0x2A`/`0x2B`/`0x2C` (GAL/PLD) routing to
  `configure_not_implemented()`, **plus** a generic `protocol != 0` →
  `configure_not_implemented()` guard immediately after, catching any other
  unknown non-zero protocol (e.g. `0x99`). The named arms are functionally
  subsumed by the generic guard but exist for **documented infeasibility intent**
  + dedicated per-protocol tests (roadmap SC#4 requires they be "explicitly
  recognized in the dispatch chain"). This is fail-closed AND self-documenting,
  and aligns with the host mirror's generic guard at
  `check_dispatch.py:82-83`. (Considered and rejected: catch-all-only — loses
  the named intent SC#4 wants; named-arms-only without the catch-all — NOT
  fail-closed for truly-unknown protocols like `0x99`, which would fall through
  to the `mem_type` chain.)
- **Placement (locked, mirrors Phase 62 D-03 / host dispatch):** named arms +
  generic guard sit **after** all implemented protocol cases
  (`0x10`/`0x0D`/`0x06`/`0x05·0x35·0x39`/`0x07·0x08·0x0B`/`0x0E·0x27·0x28·0x29`)
  and **before** the `protocol == 0` `mem_type` fallback chain. The `mem_type`
  fallback is therefore reachable only when `protocol == 0`.

### Claude's Discretion
- **Native test placement (TEST-01):** user delegated ("you decide"). **Lean:
  a new suite file** `test/native/avr/test_dispatch/test_not_implemented.cpp`
  rather than extending `test_configure_memory.cpp`. Rationale: the new cases
  assert NULL operation pointers, a style the existing file's header
  (lines 26-29) deliberately avoids because `configure_sram()` is a stub that
  leaves `firestarter_operation_init` NULL — mixing the two assertion
  philosophies in one file invites confusion. A sibling file under the same
  `test_dispatch/` dir needs no `platformio.ini` change (per firmware CLAUDE.md
  "Reuse pattern for future native tests"). Planner/executor may override if a
  single-file layout proves cleaner, but must preserve: (a) the pre-existing
  `test_configure_memory.cpp` cases stay green, and (b) the `protocol==0` +
  `mem_type=1 → configure_eprom` fallback is re-asserted somewhere.
- Exact arm expression (one grouped `if (protocol==0x11 || protocol==0x2A || …)`
  vs individual `if`s) — planner/executor decides; both satisfy D-02 as long as
  all four are explicitly named and route to `configure_not_implemented()`.
- Whether `configure_not_implemented()` re-NULLs the op pointers explicitly
  (defensive) or relies on `configure_memory()` already NULLing them at the top
  (`memory.cpp:47-49`) — explicit re-NULL is preferred for a self-contained,
  independently-testable handler (consistent with D-01).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Dispatch source-of-truth (edit here)
- `firestarter/src/proms/memory.cpp` — `configure_memory()` (lines 45-119) is
  the dispatch site to edit; the inline `MSG_ERR_MEM_TYPE_UNSUPPORTED` emit at
  line 117 is the structural reference for the `LOG_ERROR_ID_U8` emit shape
  (but NOT the cohesion pattern — see D-01).
- `firestarter/include/memory.h` — declaration style for the `extern "C"`
  `configure_*` handlers; `not_implemented.h` mirrors it.
- `firestarter/src/proms/eprom.h` (`include/eprom.h`) — minimal handler-header
  template for the new `not_implemented.h`.
- `firestarter/CLAUDE.md` § "Protocol Dispatch" — the canonical 11-step dispatch
  order table; the new arms slot between step 6 (SRAM protocol set) and step 7
  (`mem_type == TYPE_EPROM` fallback). **Update this section** to document the
  fail-closed arms (keep the table the source-of-truth mirror).

### Wire message (already defined — Phase 63)
- `firestarter/include/messages.h:96` — `#define MSG_ERR_PROTOCOL_NOT_IMPLEMENTED 0xBB`
  (generated; do NOT hand-edit). Format `"Protocol 0x%02x not implemented"`,
  `u8`/`hex_byte` param, `RESPONSE_CODE_ERROR`.
- `firestarter/include/logging_id.h:106` — `LOG_ERROR_ID_U8(id, p1)` macro the
  emit uses.

### Native test harness
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — the
  existing dispatch suite; lines 26-29 explain why it asserts on `response_code`
  not op pointers (informs the D-01-Discretion test-placement call). Its
  `test_protocol_zero_with_mem_type_eprom_dispatches_eprom` +
  `test_unknown_protocol_with_unknown_mem_type_errors` cases MUST stay green.
- `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` — extend only if a
  new `rurp_*`/`LOG_*` symbol is referenced (the self-contained handler emits an
  existing message, so likely no new stub needed).
- `firestarter/CLAUDE.md` § "Native (Host) Test Environment" — invocation
  (`pio test -e native -f "*test_dispatch*"`) + the "Reuse pattern for future
  native tests" (drop a `test_*.cpp` under `test_dispatch/`, no `platformio.ini`
  change).
- `firestarter/platformio.ini` — `[env:native]` (line 69), `[env:leonardo]`
  (line 57); `default_envs = uno, uno328pb, leonardo`. `pio` is available at
  `/usr/local/bin/pio` — the TEST-02 flash gate is verifiable locally, not
  CI-only.

### Host dispatch mirror (already updated — Phase 62; mirror, do not change)
- `firestarter_app/tools/check_dispatch.py:66-89` — `dispatch()` already models
  the Phase-64 fail-closed firmware behavior (generic `protocol != 0 →
  not_implemented` after named protocol cases, before the `protocol == 0`
  `mem_type` fallback). The firmware must end up consistent with this mirror.

### Prior phase context (decisions carried forward)
- `.planning/phases/62-dispatch-baseline-capture-check-dispatch-update/62-CONTEXT.md`
  — D-03 (two failure buckets: `protocol==0`+unknown `mem_type` → existing
  ERROR/0xAE; `protocol != 0` → new not_implemented/0xBB).
- `.planning/phases/63-catalog-lockstep-wire-change/63-CONTEXT.md` — D-01
  (0xBB entry shape, hex render, mirrors 0xAE).

### Requirements + roadmap
- `.planning/REQUIREMENTS.md` — DISP-01, DISP-02, DISP-03, DISP-04, WIRE-02,
  TEST-01, TEST-02 (lines 13-36).
- `.planning/ROADMAP.md` § "Phase 64" (lines 410-424) — goal + 5 success
  criteria.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `configure_memory()` already NULLs all three op pointers at the top
  (`memory.cpp:47-49`) before any dispatch — the not-implemented path inherits
  NULL pointers even before the handler runs; D-01's explicit re-NULL is belt-
  and-suspenders for an independently-testable handler.
- The inline `MSG_ERR_MEM_TYPE_UNSUPPORTED` emit (`memory.cpp:117-118`) is the
  exact `LOG_ERROR_ID_U8(...) ; handle->response_code = RESPONSE_CODE_ERROR;`
  shape the new handler reuses (just a different message ID + cast param).
- The native test harness (`host_stubs.cpp`, `avr/pgmspace.h`, `[env:native]`)
  is complete; a new `test_*.cpp` under `test_dispatch/` needs no config change.

### Established Patterns
- **Protocol-prefix-before-mem_type** dispatch (CLAUDE.md § "Protocol Dispatch")
  — the core invariant; the new fail-closed arms preserve it by sitting after
  all protocol cases and before the `mem_type` fallback.
- **`configure_memory` mirrors `check_dispatch.py::dispatch()` line-for-line**
  (documented in both CLAUDE.md files) — the firmware change must keep this
  mirror true (the host side is already at the Phase-64 shape).
- **Dispatch tests assert `response_code` / op pointers only, never register
  side effects** — the no-op `host_stubs.cpp` is sufficient.

### Integration Points
- The `0xBB` constant flows: meta `tools/catalog/messages.toml` → generated
  `firestarter/include/messages.h` (done) → **firmware emit (this phase)** →
  Phase 65 host `ProtocolNotImplementedError` decode. This phase is the only one
  that makes the firmware *emit* it.
- No `json_parser.c` change expected — `algorithm` is already parsed into
  `handle->protocol`; an unknown non-zero value simply reaches the new guard.

</code_context>

<specifics>
## Specific Ideas

- Named arms cover exactly `0x11` (FWH), `0x2A`, `0x2B`, `0x2C` (GAL/PLD) — the
  hand-craftable-but-infeasible-on-RURP set. The generic `protocol != 0` guard
  is the catch-all for anything else non-zero and unrecognized.
- Test set should include at minimum: one truly-unknown protocol (`0x99`) →
  ERROR + all-3-pointers-NULL; one test per named arm (`0x11`/`0x2A`/`0x2B`/`0x2C`)
  → not-implemented outcome; a re-assertion that `protocol==0, mem_type=1` still
  reaches `configure_eprom` (legacy fallback intact, DISP-02).

</specifics>

<deferred>
## Deferred Ideas

- Host-side graceful handling (`ProtocolNotImplementedError` subclass, actionable
  CLI message including the protocol value) — Phase 65 (HOST-01/02). pytest may
  be developed in parallel but must not merge until this firmware phase commits.
- DB inclusion of unimplemented-protocol chips (`support_status:
  protocol-not-implemented`) + NMOS VPP correction — Phase 66.

### Reviewed Todos (not folded)
- **avrdude MCU-detection fallback for blank-chip / wrong-firmware recovery**
  (`.planning/todos/pending/avrdude-mcu-detection-fallback.md`) — host/recovery
  concern, unrelated to firmware dispatch. Deferred.
- **Frame-level deadline to the firmware COBS decoder byte-wait (WR-01)**
  (`.planning/todos/pending/cobs-decoder-framelevel-deadline-wr01.md`) — COBS
  transport concern (v1.10 surface), unrelated to dispatch fail-closed. Deferred.

</deferred>

---

*Phase: 64-firmware-fail-closed-dispatch-native-tests*
*Context gathered: 2026-06-11*

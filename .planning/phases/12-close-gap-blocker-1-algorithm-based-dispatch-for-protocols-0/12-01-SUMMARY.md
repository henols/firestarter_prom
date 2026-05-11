---
phase: 12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0
plan: 01
wave: 0
subsystem: test-scaffolding
tags:
  - firmware
  - dispatch
  - tests
  - regression
  - phase-12
  - wave-0
requires:
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-CONTEXT.md
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-RESEARCH.md
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-PATTERNS.md
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-VALIDATION.md
provides:
  - firestarter_app/tools/check_dispatch.py
  - firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp
  - firestarter/test/native/avr/test_dispatch/avr/pgmspace.h
  - firestarter/platformio.ini "[env:native]"
affects:
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-02-PLAN.md
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-03-PLAN.md
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-04-PLAN.md
tech_stack:
  added:
    - PlatformIO native env (host-side test target)
    - Unity 2.x test framework (already in libdeps)
    - ArduinoFake 0.4.x (already in libdeps)
  patterns:
    - Standalone Python tool script (mirrors build_db.py)
    - Module-top constant table (`_ALGO_MEM_TYPE` mirrors `PROTOCOL_MAP`)
    - PIO env section inheriting `${env.build_flags}`
    - Unity `RUN_TEST` enumeration in `int main(int, char**)`
key_files:
  created:
    - firestarter_app/tools/check_dispatch.py
    - firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp
    - firestarter/test/native/avr/test_dispatch/avr/pgmspace.h
  modified:
    - firestarter/platformio.ini
decisions:
  - "test_build_src stays = no — flipping to yes cascades into AVR-only firmware sources (rurp_shield.cpp, dev_tools.cpp, eprom_operations.cpp) that depend on rurp_log / rurp_shield-side symbols. Documented in platformio.ini comment; Plan 02 must budget host-mocking work."
  - "check_dispatch.py simulates the post-fix dispatch table. Today's PASS is the baseline — Plan 03 (Python _map_data fix) and Plan 04 (build_db SRAM tagging) will use this script as their automated regression scan."
  - "Added host stub for <avr/pgmspace.h> under test/native/avr/test_dispatch/avr/ — scoped via `-I test/native/avr/test_dispatch` build flag so production builds (env:uno/env:leonardo) are unaffected."
metrics:
  duration_minutes: 12
  completed: 2026-05-11T08:57Z
  tasks_completed: 3
  files_created: 3
  files_modified: 1
  commits: 6  # 3 inside submodules + 3 supermodule pointer bumps
---

# Phase 12 Plan 01: Test Scaffolding (Wave 0) Summary

Wave 0 installs the regression and unit-test harness that every later
Phase-12 wave verifies against. The harness goes in BEFORE the dispatch
code changes so the first run is RED and proves the harness can detect
the gap; later waves flip it GREEN.

## Artifacts Created

### 1. `firestarter_app/tools/check_dispatch.py`
- **Path:** `/workspaces/firestarter_prom/firestarter_app/tools/check_dispatch.py`
- **Lines:** 127
- **Provides:** Standalone Python 3 regression scan. Iterates every chip
  in `minipro_complete_db.json` and asserts each `(protocol, mem_type)`
  pair resolves to a real firmware handler. Mirrors the post-Phase-12
  D2 dispatch order in `memory.cpp::configure_memory`. Exits 1 on the
  first failure (general dispatch ERROR or BLOCKER-2 SRAM-to-eprom
  routing). Honors `FIRESTARTER_DB_FILE` env var so RED tests can
  point at synthetic DBs without modifying the canonical one.
- **Current run:** `PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom`
- **Commit:** `firestarter_app@735a6f7` (supermodule pointer: `92f6ec0`)

### 2. `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`
- **Path:** `/workspaces/firestarter_prom/firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`
- **Lines:** 156
- **Provides:** Unity test suite with 15 `RUN_TEST` entries:
    - **13 protocol-positive tests** — one per `KNOWN_PROTOCOLS` entry
      (0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29,
      0x35, 0x39). Each constructs a minimal `firestarter_handle_t`
      with the protocol set, calls `configure_memory(&h)`, and asserts
      `TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code)`.
    - **1 negative test** (`test_unknown_protocol_with_unknown_mem_type_errors`)
      — handle with `protocol=0, mem_type=99` must yield
      `RESPONSE_CODE_ERROR`. Asserts the fallback error branch stays
      reachable. Must remain GREEN across every wave.
    - **1 fallback test** (`test_protocol_zero_with_mem_type_eprom_dispatches_eprom`)
      — handle with `protocol=0, mem_type=1` (TYPE_EPROM) must resolve
      via the legacy mem_type chain. Must remain GREEN across every wave.
- **Setup pattern:** `setUp()` calls `ArduinoFakeReset()`; `make_handle()`
  helper zero-initializes the struct and sets the three named fields.
- **Commit:** `firestarter@a94ba3d` (supermodule pointer: `de4f972`)

### 3. `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h`
- **Path:** `/workspaces/firestarter_prom/firestarter/test/native/avr/test_dispatch/avr/pgmspace.h`
- **Lines:** 53
- **Provides:** Host-side shim for `<avr/pgmspace.h>`. `rurp_shield.h`
  unconditionally `#include <avr/pgmspace.h>`; on `platform = native` the
  AVR libc is absent and the include fails. This stub defines `PROGMEM`,
  `PSTR`, `pgm_read_byte/word/dword/ptr`, and `strcpy_P/strlen_P/memcpy_P`
  as no-ops / direct memory access. Scoped to env:native via
  `-I test/native/avr/test_dispatch` build flag; production builds
  (env:uno, env:leonardo) get the real header from the Arduino framework.
- **Commit:** bundled in `firestarter@a94ba3d`.

### 4. `firestarter/platformio.ini` — `[env:native]` (modified)
- **Path:** `/workspaces/firestarter_prom/firestarter/platformio.ini`
- **Diff:** Appends a new `[env:native]` section after `[env:leonardo]`.
  Uses `platform = native`, `test_framework = unity`, inherits
  `${env.build_flags}`, adds `-std=gnu++17`, `-I include`, and
  `-I test/native/avr/test_dispatch`. Declares
  `lib_deps = fabiobatsilva/ArduinoFake@^0.4.0`. Sets
  `test_build_src = no` with an inline explanatory comment.
- **Existing `[env:uno]` / `[env:leonardo]`:** unchanged in header and
  contents (one trivial whitespace normalization on `build_flags =` for
  the leonardo section; net behavior identical).
- **Commit:** `firestarter@d09b143` (supermodule pointer: `c2f2cef`).
  Updated again inside `firestarter@a94ba3d` to add the include paths
  for the dispatch test compile.

## Verification — Plan-Level Success Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `[env:native]` section in platformio.ini; `pio project config` lists it | PASS | `pio project config 2>&1 \| grep "env:native"` → `env:native` (verified) |
| 2 | `check_dispatch.py` exists, exits 0 with PASS line | PASS | `PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom` (exit 0) |
| 3 | `test_configure_memory.cpp` ≥13 RUN_TEST + 1 negative + 1 fallback; compiles under `[env:native]` | PARTIAL — see "Pre-Fix RED State" | 15 RUN_TEST, 15 TEST_ASSERT_NOT_EQUAL; compile passes the test file itself but the linker stage cannot resolve `configure_memory` (Plan 02 budget item) |
| 4 | No source file in `firestarter/src/` modified (Wave 0 is harness-only) | PASS | Latest commit touching `src/` is Phase-10's `14ff2b4`; Phase-12 commits touch only `platformio.ini` and `test/native/` |

## Pre-Fix RED State — `pio test -e native -f "*test_dispatch*"`

This is the RED baseline Plan 02 will close.

### What passes today (compile stage)
- `test_configure_memory.cpp` compiles cleanly against the test-local
  `avr/pgmspace.h` stub. Verified by:
  ```
  cd firestarter && pio test -e native -f "*test_dispatch*" --without-uploading
  ```
  → progresses past the `#include` layer (the previous
  `fatal error: avr/pgmspace.h: No such file or directory` is gone).
- `pio project config` recognizes the `native` env.

### What fails today (link stage — INTENDED RED)
- The linker fails with `undefined reference to 'configure_memory'` for
  every protocol test, because `test_build_src = no` keeps `src/proms/memory.cpp`
  out of the host build.
- Flipping `test_build_src = yes` was attempted; it cascades into
  AVR-only firmware sources (`src/boards/rurp_serial_utils.cpp`,
  `src/dev_tools.cpp`, `src/eprom_operations.cpp`) which depend on
  `rurp_log` / `rurp_*` symbols defined in AVR-only TUs. Reverted to
  `test_build_src = no` and documented the link gap.
- **Therefore: at this commit ALL 13 protocol-positive tests are RED**
  (link failure). The negative + fallback tests are also RED until
  Plan 02 produces a host-linkable `configure_memory`.

### Pre-fix dispatch coverage (semantic RED, once the link gap closes)
Once Plan 02 makes `configure_memory` host-linkable, the RED tests at
that intermediate commit will be exactly the 11 protocols NOT yet
covered by the existing protocol-prefix block (today's `memory.cpp:73-81`
only routes 0x10 and 0x0D):
- `test_protocol_0x06_dispatches_flash3` — RED (falls through)
- `test_protocol_0x05_dispatches_flash4` — RED
- `test_protocol_0x35_dispatches_flash4` — RED
- `test_protocol_0x39_dispatches_flash4` — RED
- `test_protocol_0x07_dispatches_eprom` — RED
- `test_protocol_0x08_dispatches_eprom` — RED
- `test_protocol_0x0B_dispatches_eprom` — RED
- `test_protocol_0x0E_dispatches_sram` — RED (also BLOCKER-2 hazard)
- `test_protocol_0x27_dispatches_sram` — RED (also BLOCKER-2 hazard)
- `test_protocol_0x28_dispatches_sram` — RED (also BLOCKER-2 hazard)
- `test_protocol_0x29_dispatches_sram` — RED (also BLOCKER-2 hazard)

Already-green:
- `test_protocol_0x10_dispatches_flash_intel` — already passes (existing dispatch)
- `test_protocol_0x0D_dispatches_eeprom28c` — already passes (existing dispatch)
- `test_unknown_protocol_with_unknown_mem_type_errors` — must stay green
- `test_protocol_zero_with_mem_type_eprom_dispatches_eprom` — must stay green

After Plan 02 lands the dispatch extension per CONTEXT.md D2 and
PATTERNS.md section 1 concrete diff, all 11 currently-RED protocol tests
should flip GREEN. The negative + fallback tests are the regression
guards against over-eager dispatch.

## `test_build_src` Flip Decision

**Decision: keep `test_build_src = no`.**

The plan's acceptance criterion explicitly permits flipping to `yes`
"if compile fails for missing-symbol reasons." A flip was attempted
during execution. Outcome:

- With `test_build_src = no`: linker error on `configure_memory` (1 symbol).
- With `test_build_src = yes`: compile errors cascade into
  `src/dev_tools.cpp`, `src/boards/rurp_serial_utils.cpp`, and
  `src/eprom_operations.cpp` — every TU that references `rurp_log`
  (defined in AVR-only `src/boards/rurp_shield.cpp`). The flip
  introduces 3+ new compile failures and does not yield a green build.

The cleanest path forward (deferred to Plan 02) is a small host-stub
TU under `test/native/avr/test_dispatch/` that provides no-op
implementations of `rurp_log`, `rurp_read_from_register`,
`rurp_write_to_register`, etc., plus a `src_filter` in `[env:native]`
that pulls in ONLY `src/proms/*.cpp`. The Wave 0 harness lands the
test file in its final shape; Plan 02 produces the host stub.

## Known Stubs

| File | Reason | Resolved by |
|------|--------|-------------|
| `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` | Host-side replacement for AVR libc header so the test can compile on `platform = native`. The macros are no-ops because AVR PROGMEM semantics collapse to plain memory on a non-Harvard host. | Intentional and permanent for the test env; the AVR build paths never see this file. |
| `test_build_src = no` in `[env:native]` | Keeps `configure_memory` unresolved at link time today; Plan 02 introduces a `src_filter` plus host stubs for `rurp_log` and `rurp_*` so the dispatch test can link. | Plan 02 (Wave 1) — host-stub TU under `test/native/avr/test_dispatch/`. |

## Deviations from Plan

### Auto-fixed (Rule 3 — blocking issue)

**1. [Rule 3 — Blocking issue] Added host stub for `<avr/pgmspace.h>`**
- **Found during:** Task 3 (first `pio test -e native -f "*test_dispatch*"` invocation).
- **Issue:** `firestarter.h` → `rurp_shield.h` → `#include <avr/pgmspace.h>` failed
  with `fatal error: avr/pgmspace.h: No such file or directory` on `platform = native`
  (host has no AVR libc).
- **Fix:** Added `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` shim
  (PROGMEM, pgm_read_*, str*_P stubs) and added
  `-I test/native/avr/test_dispatch` to `[env:native].build_flags`.
- **Scope guard:** Production builds (env:uno, env:leonardo) do NOT add
  this include path, so they continue to use the real AVR libc header.
- **Files modified:** `firestarter/platformio.ini`, new
  `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h`.
- **Commit:** bundled in `firestarter@a94ba3d`.

**2. [Rule 3 — Blocking issue] PIO test filter required to actually run the suite**
- **Found during:** Task 3 verification.
- **Issue:** PIO's test discovery extracts the test suite name from the
  path; `test/native/avr/test_dispatch/` → suite ID `native/avr/test_dispatch`.
  The leading `native/avr/` prefix is interpreted as an env hint and the
  suite is reported as SKIPPED on all three envs (`uno`, `leonardo`, `native`).
  Invoking `pio test -e native -f "*test_dispatch*"` works around this and
  forces the run on the `native` env.
- **Fix:** Documented the required invocation in this SUMMARY and in
  Plan 02's `<verify>` expectation. No code change was needed beyond the
  filter argument.
- **Note for Plan 02:** the test wrapper command should always include
  `-f "*test_dispatch*"`. Moving the file to `test/test_dispatch/` would
  also work but would deviate from the plan's pinned `<files_modified>`
  path — opted to keep the prescribed path and document the filter.

### Architectural — surfaced for Plan 02 budget (Rule 4 territory; not auto-fixed)

**3. [Rule 4 — Architectural blocker — handed off to Plan 02] `configure_memory` is not host-linkable**
- **Found during:** Task 3 link stage.
- **Issue:** Once headers compile, the linker reports `undefined reference
  to 'configure_memory'`. Flipping `test_build_src = yes` cascades into
  three more compile failures from AVR-only firmware sources that depend
  on `rurp_log`.
- **Why not auto-fixed in Wave 0:** introducing a host-stub TU + an
  `[env:native] src_filter` that pulls in ONLY `src/proms/*.cpp` while
  satisfying `rurp_log` / `rurp_*` symbols is a non-trivial
  restructuring that the plan budgeted for Plan 02 (per the explicit
  acceptance-criterion escape hatch: "If compile-success cannot be
  achieved... document the flip in the task SUMMARY"). This SUMMARY is
  the documentation.
- **Hand-off to Plan 02:** add a host stub TU under
  `test/native/avr/test_dispatch/` providing no-op `rurp_*` and
  `rurp_log` implementations, plus `src_filter = +<proms/>` to the
  `[env:native]` section. After that lands, the 11 currently-broken
  protocol tests will flip GREEN as Plan 02's dispatch extension lands.

## Authentication Gates

None — this plan only edits text files and runs local commands.

## Threat Flags

None — Wave 0 introduces no new network endpoints, auth paths, file
access patterns, or schema changes at trust boundaries. The
BLOCKER-2 electrical-safety mitigation (`T-12-01` in the plan's
threat register) is exercised by `check_dispatch.py`'s
`sram_in_eprom` guard. Test file `test_protocol_0x0E_dispatches_sram`
(and 0x27/0x28/0x29) provide the firmware-side mitigation
verification — currently RED, will flip GREEN once Plan 02 lands.

## Commits

| Stage | Repo | Hash | Message |
|-------|------|------|---------|
| Task 1 | firestarter | `d09b143` | chore(12-01): add [env:native] test environment for Unity dispatch tests |
| Task 1 | supermodule | `c2f2cef` | chore(12-01): bump firestarter pointer — [env:native] test env |
| Task 2 | firestarter_app | `735a6f7` | chore(12-01): add check_dispatch.py regression scan |
| Task 2 | supermodule | `92f6ec0` | chore(12-01): bump firestarter_app pointer — check_dispatch.py |
| Task 3 | firestarter | `a94ba3d` | test(12-01): add Unity dispatch tests for configure_memory |
| Task 3 | supermodule | `de4f972` | test(12-01): bump firestarter pointer — Unity dispatch test scaffolding |

## Self-Check: PASSED

- `firestarter_app/tools/check_dispatch.py` — exists, exit 0, 743 chips PASS.
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — exists, 15 RUN_TEST.
- `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` — exists.
- `firestarter/platformio.ini` — `[env:native]` section parses (`pio project config`).
- All 6 commits (3 in submodules + 3 supermodule pointer bumps) exist in `git log`.
- No file in `firestarter/src/` was modified by this wave.

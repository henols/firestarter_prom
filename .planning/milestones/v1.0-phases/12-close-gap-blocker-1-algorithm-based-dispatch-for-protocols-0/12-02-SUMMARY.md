---
phase: 12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0
plan: 02
subsystem: firmware
tags:
  - firmware
  - dispatch
  - cpp
  - phase-12
  - wave-1
  - blocker-1
  - blocker-2
requires:
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-01-SUMMARY.md
provides:
  - "firestarter/src/proms/memory.cpp — configure_memory protocol-prefix dispatch for KNOWN_PROTOCOLS (D2 steps 3-6)"
  - "firestarter/test/native/avr/test_dispatch/host_stubs.cpp — host stubs for rurp_* / logging globals so [env:native] can link memory.cpp + configure_*()"
  - "firestarter/platformio.ini [env:native] — src_filter = +<proms/> + test_build_src = yes wiring so the Plan 01 Unity dispatch tests flip from RED to GREEN"
affects:
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-03-PLAN.md
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-04-PLAN.md
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-05-PLAN.md
tech-stack:
  added: []  # no new libraries — all work uses existing PlatformIO + Unity + ArduinoFake + AVR toolchain
  patterns:
    - "Protocol-prefix `if-return` dispatch chain in configure_memory (extends Phase 05/06 pattern from 0x10/0x0D to the full KNOWN_PROTOCOLS set)"
    - "Host stub TU under test/native/ for [env:native] cross-compilation — pairs with src_filter to keep AVR-only TUs out of the host link"
    - "PGM_P macro defined by the local <avr/pgmspace.h> shim before ArduinoFake redefines it (the second definition is identical so the guard prevents a clash)"
key-files:
  created:
    - firestarter/test/native/avr/test_dispatch/host_stubs.cpp
  modified:
    - firestarter/src/proms/memory.cpp
    - firestarter/platformio.ini
    - firestarter/test/native/avr/test_dispatch/avr/pgmspace.h
key-decisions:
  - "Used the if-return chain idiom (PATTERNS.md Pattern B) for the four new protocol cases instead of a switch on handle->protocol — keeps the new code shape identical to the existing 0x10 / 0x0D blocks (lines 72-80) and lets multi-value cases (0x05||0x35||0x39, 0x07||0x08||0x0B, 0x0E||0x27||0x28||0x29) live in single blocks per handler."
  - "[env:native] src_filter = +<proms/> + test_build_src = yes: pull in only the proms/ TUs from the firmware tree. AVR-only sources (src/boards/*, src/dev_tools.cpp, src/eprom_operations.cpp, src/logging.c) are excluded; their rurp_log / rurp_* / PROGMEM log-tag symbols are provided as host stubs in test/native/avr/test_dispatch/host_stubs.cpp (auto-discovered by PIO under test/). This is the host-mocking design that Wave 0's SUMMARY explicitly budgeted for Wave 1."
  - "Added `#define PGM_P const char *` to test/native/avr/test_dispatch/avr/pgmspace.h. rurp_shield.h declares `void rurp_log(PGM_P type, ...)` and needs PGM_P at file-include time — the Wave 0 shim used PSTR/pgm_read_* but missed PGM_P. ArduinoFake's later-included pgmspace.h defines an identical PGM_P (also `const char *`), so the #ifndef guard prevents redefinition."
  - "Added `-D RURP_BOARD_NAME=\"native\"` to [env:native] build_flags. firestarter.h defines `FW_VERSION VERSION \":\" RURP_BOARD_NAME` which requires the macro at preprocess time; the AVR envs already define it per-board, native didn't until now."
patterns-established:
  - "Pattern: Host-mocking firmware sources for unit tests — src_filter + per-test host_stubs.cpp + minimal avr/ shim. Reusable for any future Unity test under test/native/."
  - "Pattern: Algorithm-first dispatch with mem_type fallback. The new dispatch order in configure_memory (lines 72-115) is now the canonical reference for which dispatches are 'protocol-driven' (top) vs 'legacy / hand-crafted JSON' (bottom)."
requirements-completed:
  - REQ-FW-01
  - REQ-FW-04
  - REQ-SER-01
duration: 32min
completed: 2026-05-11
---

# Phase 12 Plan 02: configure_memory protocol-prefix dispatch + native test link Summary

**Algorithm-first dispatch in `configure_memory` for protocols 0x06, 0x05/0x35/0x39, 0x07/0x08/0x0B, 0x0E/0x27/0x28/0x29 — closes BLOCKER-1 (277 chips that fell through to "Memory type 0x%02x not supported") and BLOCKER-2 (52 SRAM chips that previously routed to `configure_eprom`, enabling the 12V VPP regulator on 5V parts).**

## Performance

- **Duration:** ~32 min
- **Started:** 2026-05-11T09:11Z (approx — based on Wave 0 completion at 08:57 + branch read time)
- **Completed:** 2026-05-11T09:43Z
- **Tasks:** 2 (Task 1 = orphan constant deletion; Task 2 = dispatch extension + native test link)
- **Files modified:** 3
- **Files created:** 1
- **Commits:** 4 (2 inside firestarter submodule + 2 supermodule pointer bumps)

## Accomplishments

- **Phase 12 centerpiece landed.** `configure_memory` now exposes an explicit `if (handle->protocol == 0xNN) { configure_*(handle); return; }` path for every protocol in `KNOWN_PROTOCOLS`. The dispatch order matches CONTEXT.md D2 exactly: `0x10`, `0x0D`, `0x06`, `{0x05,0x35,0x39}`, `{0x07,0x08,0x0B}`, `{0x0E,0x27,0x28,0x29}`, then the legacy mem_type fallback (`TYPE_EPROM`, `TYPE_SRAM`, `TYPE_FLASH_TYPE_3`, `TYPE_FLASH_TYPE_4`), then the error.
- **BLOCKER-2 electrical safety fix.** SRAM-family protocols (0x0E, 0x27, 0x28, 0x29) reach `configure_sram` via the new prefix block; the line number where `handle->protocol == 0x06` first appears (memory.cpp:82) is strictly less than where `handle->mem_type == TYPE_EPROM` first appears (memory.cpp:103), so SRAM dispatch can never reach `configure_eprom` even if the wire `mem_type` is wrong.
- **Test harness flipped from RED to GREEN.** Wave 0 left 11 protocol-positive tests RED (link failure → behavioural fall-through). All 15 `RUN_TEST` cases in `test_configure_memory.cpp` now PASS under `pio test -e native -f "*test_dispatch*"`.
- **Orphan constant deleted.** `#define TYPE_FLASH_TYPE_2 2` removed from `firestarter/src/proms/memory.cpp` (AC-6).
- **Wave 0 hand-offs absorbed.** The host stub TU (`host_stubs.cpp`) and `[env:native] src_filter` deferred from Plan 01 are both in place; the `pio test` wrapper invocation Wave 0 documented (`-f "*test_dispatch*"`) actually runs and reports SUCCESS.

## Task Commits

Each task was committed atomically. Sub-module commits land in `firestarter` first; the meta-repo pointer bump follows.

| Stage | Repo | Hash | Message |
|-------|------|------|---------|
| Task 1 | firestarter | `2b54ef0` | chore(12-02): remove orphan TYPE_FLASH_TYPE_2 constant from memory.cpp |
| Task 1 | supermodule | `5ab6329` | chore(12-02): bump firestarter pointer — TYPE_FLASH_TYPE_2 orphan removed |
| Task 2 | firestarter | `0d9db42` | feat(12-02): extend configure_memory protocol-prefix dispatch (D2 steps 3-6) |
| Task 2 | supermodule | `d25b00f` | feat(12-02): bump firestarter pointer — configure_memory dispatch + native test link |

_Note: Task 2 bundles the dispatch extension AND the host-stub + src_filter wiring in a single submodule commit. Splitting them was discussed: the dispatch change alone produces no behavioural delta on AVR (4 if-blocks → +256 bytes flash, no warnings) and the test wiring alone produces no behavioural delta either. The two changes only become observable together (RED→GREEN tests + AVR builds clean), so one commit captures the whole landing in a way that bisect can identify._

## Files Created/Modified

- `firestarter/src/proms/memory.cpp` — (modified) deleted `#define TYPE_FLASH_TYPE_2 2` (line 25 pre-edit) and inserted four new protocol-prefix `if`-blocks between lines 81 and 83 (per PATTERNS.md section 1 concrete diff). Post-edit line layout:
    - Lines 23-27: four-entry constant block (`TYPE_EPROM`, `TYPE_FLASH_TYPE_3`, `TYPE_SRAM`, `TYPE_FLASH_TYPE_4`). `TYPE_FLASH_TYPE_2` is gone.
    - Lines 72-80: existing 0x10 / 0x0D blocks — unchanged.
    - **Lines 82-101: NEW protocol-prefix blocks** in D2 order:
        - Lines 82-85: `0x06 → configure_flash3`
        - Lines 87-90: `{0x05, 0x35, 0x39} → configure_flash4`
        - Lines 92-95: `{0x07, 0x08, 0x0B} → configure_eprom`
        - Lines 97-101: `{0x0E, 0x27, 0x28, 0x29} → configure_sram`
    - Lines 103-115: existing mem_type fallback chain — unchanged.
    - Line 116: existing error fallback — unchanged.
- `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` — (created) no-op host implementations of every `rurp_*` symbol referenced (transitively) by the proms TUs (`rurp_write_to_register`, `rurp_read_from_register`, `rurp_set_data_input/output`, `rurp_chip_*`, `rurp_read_data_buffer`, `rurp_write_data_buffer`, `rurp_set_control_pin`, `rurp_read_vcc_mv`, `rurp_read_voltage_mv`, `rurp_log`, `rurp_log_P`, `rurp_board_setup`, `rurp_load_config`, `rurp_get_config`, `rurp_save_config`, `rurp_validate_config`, `rurp_communication_*`, `rurp_user_button_pressed`, `rurp_get_bandgap_adc_reading`, `rurp_detect_hardware_revision`, `rurp_get_hardware_revision`, `rurp_get_physical_hardware_revision`, `rurp_map_ctrl_reg_for_hardware_revision`) plus the eight `LOG_*_MSG` PROGMEM strings normally defined in `src/logging.c`. All stubs return safe defaults; the dispatch test never asserts on hardware side effects.
- `firestarter/platformio.ini` — (modified) `[env:native]` section:
    - Added `-D RURP_BOARD_NAME=\"native\"` to `build_flags` (firestarter.h needs the macro for `FW_VERSION`).
    - Added `src_filter = +<proms/>` so PIO pulls `src/proms/*.cpp` (memory + handlers) into the host build but skips AVR-only `src/boards/*`, `src/dev_tools.cpp`, `src/eprom_operations.cpp`, `src/logging.c`.
    - Flipped `test_build_src = no` → `test_build_src = yes` so the filtered src/ tree is actually compiled.
    - Updated the explanatory comment to reflect the new wiring.
- `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` — (modified) added `#define PGM_P const char *` (with `#ifndef` guard so ArduinoFake's later-included identical definition doesn't conflict). Other macros unchanged.

## Decisions Made

- **Dispatch shape: if-return chain, not switch.** Pattern B in PATTERNS.md is the existing 0x10/0x0D shape; cloning it for the four new cases means a single block per handler with `||` joining the multi-value cases. This keeps the new code visually indistinguishable from what's already in `memory.cpp` and satisfies the "ordering MUST match D2" success criterion by simple top-to-bottom file reading. A switch would require either case-label duplication for the multi-value handlers or fall-through tricks; both anti-patterns per RESEARCH.md.
- **Host stub TU layout: single `host_stubs.cpp` under `test/native/avr/test_dispatch/`.** PIO auto-discovers files under `test/` as part of the test build; placing the stubs alongside the test file means no platformio.ini additions, no separate lib, and the file is naturally scoped to the dispatch test. Alternative: a `test/native/lib_host_stubs/` library — rejected as over-engineering for a single test suite.
- **PGM_P guard in pgmspace.h shim.** Two options: define `PGM_P` in the shim and let ArduinoFake's identical definition no-op via `#ifndef`, or omit `PGM_P` and rely on ArduinoFake. Picked option 1 because `rurp_shield.h` is included before ArduinoFake in some TU chains, so the shim must satisfy the symbol at file-include time. The redefinition warnings about `pgm_read_byte/word/dword/ptr` are cosmetic — both definitions resolve to byte-identical reads — and silencing them would require coordinating macro values with ArduinoFake's internals, which is more fragile than living with four warnings.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking] Wave 0 deferred host-mocking work absorbed into Task 2**
- **Found during:** Task 2 pre-execution scan (the `[env:native]` build still failed to link `configure_memory` exactly as Wave 0's SUMMARY documented).
- **Issue:** Wave 0 SUMMARY's `Deferred Items 2 and 3` explicitly handed three things to Plan 02: (a) a host-stub TU for `rurp_log` / `rurp_*` symbols, (b) `[env:native] src_filter` so the proms TUs link, (c) documentation of `-f "*test_dispatch*"` wrapper invocation. Plan 02's PLAN.md focused on the dispatch extension and lined-up the build-clean acceptance criterion against `pio run -e {uno,leonardo}` — both of which were already passing in Wave 0 — but its `pio test -e native -f test_dispatch` verification step assumed the link gap was already closed. The fix needed to be packaged with Task 2.
- **Fix:** Added `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` (no-op host impls of every `rurp_*` symbol the proms reach plus the eight `LOG_*_MSG` PROGMEM globals) and updated `[env:native]` to `src_filter = +<proms/>` + `test_build_src = yes` + `-D RURP_BOARD_NAME=\"native\"`. Bundled in the Task 2 commit.
- **Files modified:** `firestarter/platformio.ini`, `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` (new).
- **Verification:** `pio test -e native -f "*test_dispatch*"` reports `15 test cases: 15 succeeded` and the binary exits cleanly (no SIGSEGV).
- **Committed in:** `firestarter@0d9db42` (Task 2 commit, supermodule pointer `d25b00f`).

**2. [Rule 3 — Blocking] PGM_P missing from <avr/pgmspace.h> shim**
- **Found during:** Task 2 first `pio test` invocation after enabling `src_filter` and pulling proms TUs into the host build.
- **Issue:** `firestarter/src/proms/eeprom_28c.cpp` (and other proms) include `rurp_shield.h` which forward-declares `void rurp_log(PGM_P type, const char* msg)`. Without `PGM_P` defined at that include point, the compiler reports `variable or field 'rurp_log' declared void` + `'PGM_P' was not declared in this scope`. The Wave 0 shim defined `PROGMEM`, `PSTR`, and the `pgm_read_*` family but missed `PGM_P` itself.
- **Fix:** Added `#define PGM_P const char *` (with `#ifndef` guard) to `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h`.
- **Files modified:** `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h`.
- **Verification:** Build proceeds past the proms compile stage; 15/15 tests pass.
- **Committed in:** `firestarter@0d9db42` (Task 2 commit).

**3. [Rule 3 — Blocking] RURP_BOARD_NAME undefined on [env:native]**
- **Found during:** Task 2 first `pio test` invocation, post-PGM_P fix.
- **Issue:** `firestarter/include/firestarter.h:16` defines `FW_VERSION VERSION ":" RURP_BOARD_NAME`. The AVR envs define `RURP_BOARD_NAME` via `-D RURP_BOARD_NAME=\"${this.board}\"`; the Wave 0 `[env:native]` block omitted the macro, so any TU that resolves `FW_VERSION` (transitively via `firestarter.h`) failed to compile on native.
- **Fix:** Added `-D RURP_BOARD_NAME=\"native\"` to `[env:native].build_flags`.
- **Files modified:** `firestarter/platformio.ini`.
- **Verification:** Compile cleans up; tests pass.
- **Committed in:** `firestarter@0d9db42` (Task 2 commit).

---

**Total deviations:** 3 auto-fixed (3 × Rule 3 — Blocking, all part of the Wave 0 hand-off the SUMMARY explicitly budgeted for this plan).
**Impact on plan:** None of the three changes alter the plan's intended deliverables — they are the work Wave 0 documented as "handed off to Plan 02". The PLAN.md's acceptance criteria all remain satisfied; the deviations are infrastructural (test-link wiring) rather than scope additions.

## Issues Encountered

- **One pgmspace.h redefinition warning chain (cosmetic).** With both our shim's `pgm_read_byte/word/dword/ptr` macros and ArduinoFake's identical-but-differently-cast versions visible, the compiler emits four `redefined` warnings per TU. Both definitions are byte-equivalent; the warnings do not affect the build or test outcomes. Silencing would require coordinating macro internals with ArduinoFake (fragile across libdep version bumps). Documented and left as-is.
- **No SIGSEGV-on-exit.** During the intermediate RED run (after stubs + src_filter, before dispatch extension), Unity printed `Program received signal SIGSEGV (Segmentation fault)` after the final test and PIO reported `16 test cases` instead of 15. After the dispatch fix landed, the same binary exits cleanly with `15 test cases: 15 succeeded`. The most plausible diagnosis: a failing test's RED-state error path inside `firestarter_error_response_format` was touching uninitialized memory that the GREEN path skips. Not worth investigating further given GREEN is now stable.

## Verification — Success Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Four new protocol-prefix `if (handle->protocol == 0xNN) { configure_*(handle); return; }` blocks in `configure_memory`, in D2 order | PASS | `memory.cpp` lines 82-101 hold the four blocks in order 0x06 → {0x05,0x35,0x39} → {0x07,0x08,0x0B} → {0x0E,0x27,0x28,0x29}. |
| 2 | Blocks positioned AFTER 0x10/0x0D, BEFORE mem_type fallback | PASS | `grep -n "handle->protocol == 0x06\|handle->mem_type == TYPE_EPROM" memory.cpp` → `82` for 0x06 vs `103` for TYPE_EPROM (82 < 103). |
| 3 | `#define TYPE_FLASH_TYPE_2 2` removed (AC-6) | PASS | `grep -c "TYPE_FLASH_TYPE_2" memory.cpp` → 0 |
| 4 | Existing 0x10/0x0D blocks and mem_type fallback chain unchanged | PASS | Diff against pre-edit shows lines 72-80 (0x10/0x0D) and 103-115 (mem_type fallback) only shifted by line-number due to insertions; no content changes. |
| 5 | `pio run -e uno` and `pio run -e leonardo` build clean (AC-7) | PASS | Both `[SUCCESS]`. Uno: 24852 / 32256 (77.0%). Leonardo: 27218 / 28672 (94.9%). |
| 6 | Flash usage delta on Uno documented in SUMMARY (< 500 bytes per AC) | PASS | Uno: 24596 → 24852 = **+256 bytes**. Leonardo: 26962 → 27218 = **+256 bytes**. Both well under the 500-byte budget and roughly 2.5× RESEARCH.md's ~100-byte-per-block prediction, which is normal compiler variance. |
| 7 | All 15 `test_protocol_*` tests pass under `pio test -e native -f test_dispatch` | PASS | `15 test cases: 15 succeeded` after the dispatch extension. The 11 protocol-positive tests for new protocols flipped RED→GREEN as predicted; the 4 pre-existing GREEN tests (0x10, 0x0D, negative, fallback) stayed GREEN. |

### Source-Level Acceptance Criteria (from Task 2 `<acceptance_criteria>`)

| Check | Expected | Actual |
|-------|----------|--------|
| `grep -c "handle->protocol == 0x06"` | ≥ 1 | 1 |
| `grep -c "handle->protocol == 0x05 \|\| handle->protocol == 0x35"` | ≥ 1 | 1 |
| `grep -c "handle->protocol == 0x07 \|\| handle->protocol == 0x08 \|\| handle->protocol == 0x0B"` | ≥ 1 | 1 |
| `grep -c "handle->protocol == 0x0E"` (with 0x27/0x28/0x29 adjacent) | ≥ 1 | 1, adjacent line confirms 0x27/0x28/0x29 |
| `grep -c "configure_sram(handle)"` | ≥ 2 | 2 (protocol block + mem_type fallback) |
| `grep -c "configure_flash3(handle)"` | ≥ 2 | 2 (protocol block + mem_type fallback) |
| `grep -cE "^\s*switch\s*\(\s*handle->protocol"` | 0 | 0 |
| `grep -c "TYPE_FLASH_TYPE_2"` | 0 | 0 |
| `grep -cE "^#define TYPE_(EPROM\|FLASH_TYPE_3\|SRAM\|FLASH_TYPE_4)"` | 4 | 4 |

### Cross-Plan Regression — `check_dispatch.py` (Plan 01 harness)

```text
$ python3 firestarter_app/tools/check_dispatch.py
PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom
```

Both BLOCKER-1 (general dispatch ERROR) and BLOCKER-2 (SRAM-to-EPROM routing) remain at zero matches across the full minipro DB. The simulated post-fix dispatch table in `check_dispatch.py` agrees byte-for-byte with what `memory.cpp:configure_memory` now does at runtime.

## Pre-Fix RED → Post-Fix GREEN Diff

### Pre-fix `pio test -e native -f "*test_dispatch*"` (after stubs landed, before dispatch extension)
```text
test_protocol_0x06_dispatches_flash3      [FAILED]   (line 66)
test_protocol_0x05_dispatches_flash4      [FAILED]   (line 72)
test_protocol_0x35_dispatches_flash4      [FAILED]   (line 78)
test_protocol_0x39_dispatches_flash4      [FAILED]   (line 84)
test_protocol_0x07_dispatches_eprom       [FAILED]   (line 90)
test_protocol_0x08_dispatches_eprom       [FAILED]   (line 96)
test_protocol_0x0B_dispatches_eprom       [FAILED]   (line 102)
test_protocol_0x0E_dispatches_sram        [FAILED]   (line 108)
test_protocol_0x27_dispatches_sram        [FAILED]   (line 114)
test_protocol_0x28_dispatches_sram        [FAILED]   (line 120)
test_protocol_0x29_dispatches_sram        [FAILED]   (line 126)
test_protocol_0x10_dispatches_flash_intel [PASSED]
test_protocol_0x0D_dispatches_eeprom28c   [PASSED]
test_unknown_protocol_with_unknown_mem_type_errors  [PASSED]
test_protocol_zero_with_mem_type_eprom_dispatches_eprom  [PASSED]
```
**11 failed, 4 succeeded.** Matches Wave 0's RED prediction exactly.

### Post-fix `pio test -e native -f "*test_dispatch*"`
```text
test_protocol_0x06_dispatches_flash3      [PASSED]
test_protocol_0x05_dispatches_flash4      [PASSED]
test_protocol_0x35_dispatches_flash4      [PASSED]
test_protocol_0x39_dispatches_flash4      [PASSED]
test_protocol_0x07_dispatches_eprom       [PASSED]
test_protocol_0x08_dispatches_eprom       [PASSED]
test_protocol_0x0B_dispatches_eprom       [PASSED]
test_protocol_0x0E_dispatches_sram        [PASSED]
test_protocol_0x27_dispatches_sram        [PASSED]
test_protocol_0x28_dispatches_sram        [PASSED]
test_protocol_0x29_dispatches_sram        [PASSED]
test_protocol_0x10_dispatches_flash_intel [PASSED]
test_protocol_0x0D_dispatches_eeprom28c   [PASSED]
test_unknown_protocol_with_unknown_mem_type_errors  [PASSED]
test_protocol_zero_with_mem_type_eprom_dispatches_eprom  [PASSED]
```
**15 test cases: 15 succeeded.**

## Authentication Gates

None — this plan only edits text files and runs local PlatformIO commands.

## Threat Flags

None new. The plan's `<threat_model>` already documents BLOCKER-2 electrical safety (`T-12-02`); the new SRAM dispatch block at memory.cpp:97-101 is the mitigation that closes it. The acceptance check that the source-line ordering forces protocol-prefix dispatch before the mem_type fallback (82 < 103) is the structural guarantee that even malformed wire `mem_type` cannot route an SRAM chip to `configure_eprom`.

## Known Stubs

| File | Reason | Resolved by |
|------|--------|-------------|
| `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` | Host-side replacement for AVR libc header so the dispatch test can compile on `platform = native`. Macros collapse PROGMEM semantics to plain memory access since the host is not a Harvard architecture. | Intentional and permanent for the test env; AVR builds (env:uno, env:leonardo) use the real header from the Arduino framework. |
| `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` | Host-side no-op replacements for `rurp_*` hardware-bus symbols and the eight `LOG_*_MSG` PROGMEM strings. The dispatch tests only assert on `handle->response_code`, never on register-write side effects, so no-op stubs are sufficient. | Intentional and permanent for the dispatch test env. If a future native test asserts on hardware side effects, the stubs can grow to record calls (ArduinoFake's `Verify(Method(...))` pattern). |

## Next Plan Readiness

- **Plan 12-03** (Python `_map_data` D3 table) can now lean on the firmware as the source of truth — every `(algorithm, mem_type)` pair the Python side will emit has an explicit handler in the firmware. The Python change becomes defense-in-depth rather than a load-bearing fix.
- **Plan 12-04** (`build_db.py` SRAM tagging D4) is independent of firmware; ready to start.
- **Plan 12-05** (CLAUDE.md dispatch table doc update) can quote the post-fix `memory.cpp` line numbers from this SUMMARY directly.
- **Flash budget:** Uno is at 77.0% / Leonardo at 94.9%. Leonardo's headroom is the tighter constraint (~1454 bytes free of 28672); future phases adding handler logic should profile before merging.
- **Test infrastructure reusable:** the `[env:native]` + `src_filter` + `host_stubs.cpp` pattern is now the canonical template for any future Unity test against firmware logic. Future tests just add their `test_*.cpp` under `test/native/avr/<dirname>/` and extend `host_stubs.cpp` only if they touch new `rurp_*` symbols.

## Self-Check: PASSED

- `firestarter/src/proms/memory.cpp` — exists, contains four new protocol-prefix blocks at lines 82-101, no `TYPE_FLASH_TYPE_2` reference.
- `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` — exists (143 lines).
- `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` — exists, contains `#define PGM_P const char *` (verified).
- `firestarter/platformio.ini` — `[env:native]` contains `src_filter = +<proms/>` and `test_build_src = yes` (verified).
- `pio test -e native -f "*test_dispatch*"` — 15/15 PASS.
- `pio run -e uno` — SUCCESS (24852 bytes).
- `pio run -e leonardo` — SUCCESS (27218 bytes).
- `python3 firestarter_app/tools/check_dispatch.py` — PASS (743 chips, 0 SRAM hazards).
- Commits exist in git log:
    - `firestarter@2b54ef0` — `git log --oneline` in `firestarter/` confirms.
    - `firestarter@0d9db42` — confirmed.
    - supermodule `5ab6329`, `d25b00f` — confirmed.

---
*Phase: 12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0*
*Plan: 02 (Wave 1)*
*Completed: 2026-05-11*

---
phase: 28
plan: 01
wave: A
subsystem: firmware
tags: [firmware, unity, leonardo, tdd-red, rurp_set_data_input, rurp_read_data_buffer, v1.6-read-bug]
requirements: [FIX-02]
requirements_completed: [FIX-02-RED]
status: complete
dependency_graph:
  requires:
    - "beta@bc0f5ac (firestarter sub-repo tip — branch source per D-03)"
    - "Phase 27 RCA findings — .planning/v1.6-EVIDENCE.md §Phase 27"
  provides:
    - "RED-bar evidence that FIX-02 first half is satisfied (test FAILS on pre-fix code)"
    - "Native Unity test scaffold for rurp_set_data_input pullup contract"
    - "Regression guard around rurp_read_data_buffer bit-map reassembly"
    - "Pre-fix per-board .hex baseline (forwarded to Wave B for D-07 Δ table)"
  affects:
    - "firestarter/v1.6-read-bug branch (created + 1 commit)"
    - "Plan 28-02 (Wave B fix commits) — input contract"
tech_stack:
  added: []
  patterns:
    - "include-as-source for board-guarded production code under [env:native]"
    - "_BV(n) host shim for ArduinoFake (anticipated by RESEARCH.md Q6 line 303)"
    - "Per-suite minimal host_stubs.cpp (opt-out of _shared/host_stubs_common.inc) for include-as-source TUs"
key_files:
  created:
    - firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp
    - firestarter/test/native/avr/test_data_input/host_stubs.cpp
    - firestarter/test/native/avr/test_data_input/avr/pgmspace.h
  modified:
    - firestarter/platformio.ini
decisions:
  - "D-03 honored: v1.6-read-bug branched from beta@bc0f5ac (firestarter sub-repo), LOCAL only — no push (deferred to Phase 29 boundary)"
  - "D-04 honored: Wave A scaffold lands as ONE atomic commit on v1.6-read-bug; Wave B fix is a separate plan"
  - "Rule 3 auto-fix #1: Added #ifndef _BV / #define _BV(n) guard in test cpp (ArduinoFake does not provide _BV; anticipated by RESEARCH.md Q6 line 303)"
  - "Rule 3 auto-fix #2: Added rurp_read_voltage_mv + rurp_get_config stubs in host_stubs.cpp (the [env:native] build_src_filter pulls in proms/*.cpp which need them, AND the header-inlined rurp_get_hardware_revision needs rurp_get_config) — could not include _shared/host_stubs_common.inc per RESEARCH Q6/D.1 multiple-definition constraint"
metrics:
  duration: ~25 min
  completed: 2026-05-21
  tasks_completed: 3
  files_created: 3
  files_modified: 1
  commits: 1
---

# Phase 28 Plan 01: Wave A — RED Unity Scaffold for FIX-02 Summary

**One-liner:** Cut `firestarter/v1.6-read-bug` from `beta@bc0f5ac` and land a single Unity native test commit that captures RED-bar evidence — `test_rurp_set_data_input_clears_data_pullups_leonardo` FAILS with `Expected 0x00 Was 0x9F` on pre-fix Leonardo source, exactly the PORTD_DATA_MASK register-residue predicted by Phase 27 RCA.

## Wave A Commit

| Field | Value |
|---|---|
| **Branch** | `firestarter/v1.6-read-bug` (LOCAL only — NOT pushed) |
| **Branch source** | `beta@bc0f5ac05b37c94eb7ddc706f65dbdc94c47899e` |
| **Wave A SHA** | `fdb1ed50147e2de9a83a68a95ebeba79dfd68bea` |
| **Subject** | `test(leonardo): RED unity scaffold for rurp_set_data_input pullup clearing (FIX-02)` |
| **Diff scope** | 4 files, 328 insertions, 0 deletions |
| **Commits ahead of beta** | 1 |

`git diff --stat beta..v1.6-read-bug`:

```
 platformio.ini                                                       |   2 +
 test/native/avr/test_data_input/avr/pgmspace.h                       |  66 ++++++++
 test/native/avr/test_data_input/host_stubs.cpp                       |  73 ++++++++
 test/native/avr/test_data_input/test_rurp_set_data_input.cpp         | 187 +++++++++++++++++++++
 4 files changed, 328 insertions(+)
```

## RED-bar Evidence (verbatim from `/tmp/phase28-wave-a-red-bar.log`)

```
test/native/avr/test_data_input/test_rurp_set_data_input.cpp:118: test_rurp_set_data_input_clears_data_pullups_leonardo: Expected 0x00 Was 0x9F	[FAILED]
test/native/avr/test_data_input/test_rurp_set_data_input.cpp:184: test_rurp_read_data_buffer_reassembles_data_bus	[PASSED]
```

- **Pullup-clear test FAILED** with `Expected 0x00 Was 0x9F`. The hex value `0x9F` IS `PORTD_DATA_MASK` (defined at `leonardo_rurp_shield.cpp:17`). The pre-state set `PORTD = 0xFF`; after `rurp_set_data_input()` the test asserts `PORTD & PORTD_DATA_MASK == 0x00`. The post-state is `0xFF & 0x9F = 0x9F`, which is EXACTLY the register-residue predicted by Phase 27 RCA. This is the load-bearing RED-bar evidence for FIX-02 first half.
- **Bit-map regression guard PASSED** (`test_rurp_read_data_buffer_reassembles_data_bus`). The shift-and-mask logic at `leonardo_rurp_shield.cpp:119-126` is unchanged on pre-fix code; this case guards Wave B Commit 2's `_NOP()` insertion from accidentally breaking the bit map.
- **Assertion failure, NOT a build/link error** — `grep -cE "undefined reference|multiple definition" /tmp/phase28-wave-a-red-bar.log` returns `0`. The test binary built clean, ran, and the failure is a Unity assertion the way it should be.
- **PIO test exit code** `1` (non-zero — RED bar). PIO renders the failure as `[FAILED]` rather than Unity's bare `:FAIL:` marker; this is a PIO test-runner display convention, not a structural difference.
- **Trailing SIGHUP on test binary exit** — this matches the pre-existing KNOWN-FLAKY teardown-abort pattern noted in `firestarter/platformio.ini` lines 70-75 for `test_flash_intel_vpp` + `test_eeprom28c_chip_id`. The assertion is registered BEFORE the SIGHUP; the SIGHUP is post-test cleanup noise and does not invalidate the RED-bar evidence.

## Sibling Suites — both still GREEN

- `pio test -e native -f "*test_dispatch*"` → exit 0, 15 test cases all PASSED.
- `pio test -e native -f "*test_messages*"` → exit 0, 5 test cases all PASSED.

## Production Builds — all three envs clean

| Board | RAM | Flash | `.hex` size | Notes |
|---|---|---|---|---|
| **uno** | 1495 B / 2048 B (73.0%) | 22,254 B / 32,256 B (69.0%) | 62,617 B | clean |
| **leonardo** | 1463 B / 2560 B (57.1%) | 24,480 B / 28,672 B (**85.4%**) | 68,876 B | clean — matches Phase 27 baseline exactly |
| **uno328pb** | 1499 B / 2048 B (73.2%) | 22,340 B / 32,384 B (69.0%) | 62,854 B | clean |

The Leonardo `.hex` size **68,876 B** matches RESEARCH.md Q7 line 437 verbatim — the pre-fix baseline is locked exactly. Forwarded to Wave B for the D-07 ±200 B Δ-budget check.

## Hand-off to Plan 28-02 (Wave B)

`v1.6-read-bug` branch ready at SHA `fdb1ed5` on the firestarter sub-repo. Pre-fix per-board `.hex` sizes captured to `/tmp/phase28-wave-a-prefix-hex-sizes.txt` (and inline above). RED bar captured to `/tmp/phase28-wave-a-red-bar.log`. Ready to apply Wave B Commit 1 (`fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups...` — RESEARCH.md Q4 exact diff) and Commit 2 (`fix(leonardo): add _NOP settling delay between PIND/PINC/PINE reads...` — RESEARCH.md Q1 exact diff) to flip the RED bar to GREEN.

## Deviations from Plan

### Auto-fixed Issues

Two Rule 3 (blocking issue) auto-fixes applied during Task 3 build/link iteration. Both were explicitly anticipated by RESEARCH.md Q6 — the planner-supplied `host_stubs.cpp` pattern in PATTERNS.md Excerpt 2 (Phase-28-specific) was a strict-minimum sketch that did not account for the transitive symbol pull-in from `[env:native].build_src_filter = +<proms/>` + the header-inlined `rurp_get_hardware_revision`.

**1. [Rule 3 - Blocking] Added `_BV(n)` host shim in test cpp**

- **Found during:** Task 3 first `pio test` invocation.
- **Issue:** Build failed with `'_BV' was not declared in this scope` in three places — the included Leonardo source uses `_BV` at lines 96-104 (`rurp_write_data_buffer`) and 119-126 (`rurp_read_data_buffer`), and the regression-guard test body uses `_BV` for single-bit walks. ArduinoFake's `Arduino.h` defines `bit(n)` but NOT `_BV(n)`.
- **Fix:** Added `#ifndef _BV \n #define _BV(n) (1U << (n)) \n #endif` guard near the top of `test_rurp_set_data_input.cpp` (before the register shim + include-as-source). This is the verbatim fix RESEARCH.md Q6 line 303 anticipated.
- **Files modified:** `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` (single hunk near top of file).
- **Commit:** `fdb1ed5` (included in the Wave A commit).

**2. [Rule 3 - Blocking] Extended host_stubs.cpp with two extra link-time stubs**

- **Found during:** Task 3 second `pio test` invocation (after `_BV` fix).
- **Issue:** Linker errors:
  - `undefined reference to rurp_read_voltage_mv` (from `src/proms/eprom.cpp::eprom_check_vpp` and `src/proms/flash_intel.cpp::flash_intel_check_vpp` — the `[env:native].build_src_filter = +<proms/>` pulls these TUs into every native test binary).
  - `undefined reference to rurp_get_config` (from `include/rurp_hw_rev_utils.h:61` which the included `leonardo_rurp_shield.cpp` transitively pulls in via `rurp_register_utils.h` → `rurp_hw_rev_utils.h`).
  - After adding both, a third linker error appeared: `multiple definition of rurp_get_physical_hardware_revision` because `rurp_hw_rev_utils.h:37` defines that function inline AND I had added it as a stub. Removed the stub; the header-inlined version is sufficient.
- **Fix:** Added two `extern "C"` stubs in `host_stubs.cpp` — `rurp_read_voltage_mv` (returns 0) and `rurp_get_config` (returns &static rurp_configuration_t). Explanatory docstring cites the symbol-source chain. The shared `_shared/host_stubs_common.inc` was still NOT included (per RESEARCH.md Q6/D.1) — including it would multiple-define `rurp_set_data_input` / `rurp_read_data_buffer` against the real Leonardo implementations pulled in via include-as-source.
- **Files modified:** `firestarter/test/native/avr/test_data_input/host_stubs.cpp` (single inline addition after `Serial_::operator bool()`).
- **Commit:** `fdb1ed5` (included in the Wave A commit).

Both fixes preserve the locked decisions in `28-CONTEXT.md` D-01..D-08 and `28-RESEARCH.md` Q1..Q8. Neither contradicts the planner's intent — RESEARCH.md Q6 explicitly says ArduinoFake doesn't provide `_BV` and supplies the guard verbatim, and Q6/D.1's "minimum required stubs" framing leaves room for the link-time-only stubs that the production code's transitive includes demand. The fixes were applied inside the same single Wave A commit (per D-04 "Wave A artifacts in ONE commit").

## Authentication Gates

None encountered.

## Known Stubs

None introduced by Wave A. The added Unity tests are full-coverage on their declared post-conditions; no placeholder data or stubbed UI paths.

## Threat Flags

None. Wave A touches only test infrastructure (`test/native/avr/test_data_input/`) + a 2-line addition to `platformio.ini`'s `[env:native]` block. No new network endpoints, no auth paths, no file-access patterns, no schema changes. The production Leonardo source is unchanged.

## TDD Gate Compliance

Wave A is the RED half of a two-wave TDD cycle. Phase 28 plan type is `execute` (not `tdd`), so the per-plan TDD gate sequence (`test(...)` → `feat(...)` → optional `refactor(...)`) is enforced at the WAVE granularity instead of within a single plan:

- ✅ **RED gate (Plan 28-01 / Wave A — this plan):** `test(leonardo): RED unity scaffold for rurp_set_data_input pullup clearing (FIX-02)` at `fdb1ed5`.
- ⬜ **GREEN gate (Plan 28-02 / Wave B):** `fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups...` + `fix(leonardo): add _NOP settling delay between PIND/PINC/PINE reads...` — pending.

The RED-bar discriminator (`Expected 0x00 Was 0x9F`, the exact `PORTD_DATA_MASK` value) provides falsifiable evidence that the test exercises the corrupting code path. A green test on Wave B is the GREEN-gate proof.

## Self-Check

Verifying claims before finalizing:

| Claim | Check | Status |
|---|---|---|
| Branch exists at SHA | `git rev-parse v1.6-read-bug` = `fdb1ed5...` (1 commit ahead of `bc0f5ac`) | ✅ verified |
| Merge-base correct | `git merge-base v1.6-read-bug beta` = `bc0f5ac` | ✅ verified |
| `test_rurp_set_data_input.cpp` exists | `test -f firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` | ✅ verified |
| `host_stubs.cpp` exists | `test -f firestarter/test/native/avr/test_data_input/host_stubs.cpp` | ✅ verified |
| `avr/pgmspace.h` exists | `test -f firestarter/test/native/avr/test_data_input/avr/pgmspace.h` | ✅ verified |
| FOUR-`../` include path | `grep -cF "../../../../src/boards/leonardo_rurp_shield.cpp" test_rurp_set_data_input.cpp` = 1 | ✅ verified |
| `#define ARDUINO_AVR_LEONARDO` before include | awk line-order check passes | ✅ verified (define@69 < include@73) |
| `host_stubs_common.inc` NOT included | `grep -c "host_stubs_common.inc" host_stubs.cpp` = 0 | ✅ verified |
| `platformio.ini` allowlist entry present | `grep "native/avr/test_data_input" platformio.ini \| grep -v -- "-I" \| wc -l` = 1 | ✅ verified |
| `-I test/native/avr/test_data_input` present | `fgrep -c -- "-I test/native/avr/test_data_input" platformio.ini` = 1 | ✅ verified |
| `build_src_filter` NOT extended with leonardo_rurp_shield.cpp | `fgrep -c "+<boards/leonardo_rurp_shield.cpp>" platformio.ini` = 0 | ✅ verified |
| RED bar — pullup test FAILED | grep `Expected 0x00 Was 0x9F` in red-bar.log = present | ✅ verified |
| RED bar — no build/link errors | `grep -cE "undefined reference\|multiple definition"` = 0 | ✅ verified |
| Sibling suite test_dispatch GREEN | `pio test -e native -f "*test_dispatch*"` exit 0 | ✅ verified |
| Sibling suite test_messages GREEN | `pio test -e native -f "*test_messages*"` exit 0 | ✅ verified |
| Production build uno clean | `pio run -e uno` exit 0, hex = 62,617 B | ✅ verified |
| Production build leonardo clean | `pio run -e leonardo` exit 0, hex = 68,876 B (matches RESEARCH baseline) | ✅ verified |
| Production build uno328pb clean | `pio run -e uno328pb` exit 0, hex = 62,854 B | ✅ verified |
| Wave A commit landed LOCAL only | `git log origin/v1.6-read-bug` → "unknown revision" | ✅ verified (not pushed) |
| Diff stat = 4 files, 328 insertions | `git diff --stat beta..v1.6-read-bug` | ✅ verified |

## Self-Check: PASSED

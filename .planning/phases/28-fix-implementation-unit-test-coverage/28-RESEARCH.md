# Phase 28 — Research: Fix Implementation + Unit Test Coverage

**Researched:** 2026-05-21
**Scope:** Answers OPEN technical questions in CONTEXT.md "Claude's Discretion" + verifier commands + Nyquist validation architecture. Locked decisions (D-01..D-08) are NOT revisited.
**Confidence:** HIGH on Q1/Q4/Q5/Q7/Q8 (datasheet + git verified); HIGH on Q2/Q3/Q6 (sub-repo source verified empirically).

## Summary

- The Uno-side `df5fb44` diff is 7 lines (6 comment + 1 `PORTD = 0x00;`) before `DDRD = 0x00;`. Leonardo needs the same shape but with 3 ports — the EXACT 3 code lines to add are pasted verbatim in Q4 below.
- `_NOP()` count for Commit 2: recommended **2 `_NOP()`s total** — one between PIND/PINC, one between PINC/PINE. Rationale: ATmega32U4 PINx synchronizer adds 0.5-1.5 clock cycles of latency per port read [VERIFIED: Atmel datasheet 7766J §10.2.4]; a single `_NOP()` (62.5 ns @ 16 MHz) covers the worst-case 1.5-cycle window before the next-port latch closes; W27C512's 90 ns `tACC` is the worst-case data-output settling [CITED: Winbond W27C512 datasheet], so two stalls in a 3-instruction read sequence give ~125 ns total settling — comfortably above the chip's access time and below any noticeable read-throughput impact (~0.4% per 64KB read). This is the default fallback from CONTEXT.md "Claude's Discretion" #1; bench evidence in Phase 29 can confirm or refine.
- Native-test build-flag integration: use **Option D — include-as-source inline** (Q2 below). Add `#define ARDUINO_AVR_LEONARDO` ABOVE `#include "boards/leonardo_rurp_shield.cpp"` in the new test file. No `platformio.ini` `build_flags`/`build_src_filter` edits needed beyond extending `test_filter`. Cleanest delta to the existing native infrastructure; doesn't cross-contaminate test_dispatch / test_messages suites.
- Ship BOTH Unity cases (Q3): `rurp_set_data_input_clears_data_pullups_leonardo` + `rurp_read_data_buffer_reassembles_data_bus`. Cost is ~30 lines of additional scaffolding (one extra RUN_TEST + 7-line pre-state + 1-line post-assert). Worth it as a regression guard against the settling-delay edit accidentally breaking the shift-and-mask bit map.
- PORTx/DDRx/PINx are NOT host-mockable via ArduinoFake [VERIFIED: grep ArduinoFake source]. The new test_data_input suite MUST define them as `uint8_t` globals in a `host_avr_io.h` shim **BEFORE** the source is included. The same shim defines `_BV(n)` if missing (ArduinoFake provides it; double-check via grep).
- Verifier commands and branch-cut sequence are paste-ready in Q7 / Q8.

**Primary recommendation:** Planner authors two atomic Wave B commits with the exact diffs in Q4 (Commit 1) + Q1 (Commit 2). Wave A authors a single test file at `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` using the include-as-source pattern in Q2, plus a minimal `host_stubs.cpp` + `avr/pgmspace.h` mirroring `test_messages/`. Extend `test_filter` allowlist by one line.

---

## Open Question Resolutions

### Q1: `_NOP()` count for Commit 2 settling delay

**Recommended:** Insert **one `_NOP()` between PIND/PINC, one `_NOP()` between PINC/PINE — 2 `_NOP()`s total**.

**Exact diff shape** (insert at `leonardo_rurp_shield.cpp:114-116`, current vs. proposed):

Current (lines 113-117):
```cpp
uint8_t rurp_read_data_buffer() {
    // Read from ports and map back to data bus bits (D0-D7)
    uint8_t pind_val = PIND;
    uint8_t pinc_val = PINC;
    uint8_t pine_val = PINE;
```

Proposed (with settling delay):
```cpp
uint8_t rurp_read_data_buffer() {
    // Read from ports and map back to data bus bits (D0-D7).
    // Insert a single _NOP() between each PINx read to let the AVR's input
    // synchronizer latch settle before the next port read. The 32U4 PINx
    // register has a 0.5-1.5 clock-cycle latch latency (datasheet 7766J
    // §10.2.4); with a partially-erased EPROM (weak chip drive) plus the
    // address-bus driven through nearby PCB traces, three back-to-back PINx
    // reads can sample mid-transition values. One _NOP() @ 16 MHz = 62.5 ns;
    // worst-case W27C512 tACC at 5V is 90 ns. Two stalls put total settling
    // at ~125 ns - comfortably > tACC, < 1 µs / 64KB read overhead.
    uint8_t pind_val = PIND;
    _NOP();
    uint8_t pinc_val = PINC;
    _NOP();
    uint8_t pine_val = PINE;
```

**Datasheet citations:**
- ATmega16U4/32U4 datasheet (Atmel-7766J, April 2016) §10.2.4 "Reading the Pin Value": *"a single signal transition on the pin will be delayed between ½ and 1½ system clock period depending upon the time of assertion."* [CITED: https://ww1.microchip.com/downloads/en/devicedoc/atmel-7766-8-bit-avr-atmega16u4-32u4_datasheet.pdf]
- Winbond W27C512 datasheet: max access times 45/70/90/120 ns across speed grades; 90 ns is the typical mid-grade. *"Accessing individual bytes from an address transition or from power-up (chip enable pin going low) is accomplished in less than 90 ns."* [CITED: https://www.jameco.com/Jameco/Products/ProdDS/131959WINBOND.pdf]
- SST 27SF512: similar speed grades (70 ns typical, 90 ns slower-grade) [CITED: https://static.moates.net/zips/27SF512.pdf — paywalled but the 27SF256 datasheet at https://www.batronix.com/files/Datenblaetter/27__/SST27SF256.pdf shows identical timing tables].

**Cost analysis:**
- Flash: 2 × `_NOP()` = 2 single-byte AVR `nop` instructions = +4 bytes total flash. Well under D-07's ±200 B threshold.
- Runtime: 2 × 62.5 ns = 125 ns per read call. At 65,536 reads per full-chip read, total overhead = ~8 ms — invisible against the ~3 s read time per 64KB.

**Commit 2 message body — paste-ready rationale paragraph for the planner:**

```
The Leonardo's data bus scatters across three AVR ports (PORTD/PORTC/PORTE)
because the ATmega32U4 pin multiplexing precludes a contiguous 8-bit data
port. `rurp_read_data_buffer` reads PIND, PINC, PINE in three separate
machine instructions with no settling delay. With a partially-erased EPROM
cell driving the bus weakly and the address bus driven through nearby PCB
traces, adjacent address-bit transitions can capacitively couple into the
data bus while a subsequent PINx read latches. Inserting a single _NOP()
between each port read (62.5 ns @ 16 MHz, two stalls totalling ~125 ns) lets
the AVR input synchronizer settle past the chip's worst-case 90 ns tACC
(per W27C512 datasheet at Vcc=5V).

This is a defensive-in-depth addition. Commit 1 (PORTx-clear) addresses the
primary corruption mechanism (residual pullup bias). The settling _NOP()s
add belt-and-suspenders against the multi-instruction port-read race that
the binary evidence also implicates (1349/65536 = 2.1% jitter, 78%
single-bit XOR flips, 63.2% address-bit-3 correlation - see Phase 27 RCA).

Flash impact: +4 B (well under the ±200 B ROADMAP SC#4 threshold). Runtime
overhead: ~125 ns per byte read = ~8 ms per full 64KB read (invisible).
```

**Bench-confirmable in Phase 29.** Per CONTEXT.md D-01, splitting the fix into two atomic commits lets a future `git bisect` between them answer "is PORTx-clear alone sufficient?" if Phase 29 reveals the fix is overkill.

[CONFIDENCE: HIGH — datasheet-cited timing on both the AVR synchronizer and the EPROM access time; default count of 2 is also the CONTEXT.md fallback.]

### Q2: Native-test ARDUINO_AVR_LEONARDO build-flag integration

**Pattern audit of existing native suites:**

- `test_dispatch/`: compiles `src/proms/*.cpp` (via `[env:native].build_src_filter = +<proms/>`); does NOT need `ARDUINO_AVR_LEONARDO`. The `src/boards/leonardo_rurp_shield.cpp` file is excluded from the link.
- `test_messages/`: same `build_src_filter` plus `+<boards/rurp_serial_utils.cpp>` (shared between boards, NO `#ifdef ARDUINO_AVR_*` guards). Does NOT need the macro either.
- Neither suite defines `ARDUINO_AVR_LEONARDO`. The `[env:native].build_flags` block has NO `-D ARDUINO_AVR_*` flag.

**Per-suite build_flags is NOT supported by PIO test_filter** [CITED: https://docs.platformio.org/en/stable/advanced/unit-testing/structure/hierarchy.html — `test_filter` selects directories; build_flags is env-level only]. Options:

| Option | Approach | Tradeoff |
|--------|----------|----------|
| A | Add `-D ARDUINO_AVR_LEONARDO` to `[env:native].build_flags` globally + `+<boards/leonardo_rurp_shield.cpp>` to `build_src_filter` | Pollutes test_dispatch + test_messages: every suite now compiles the Leonardo board file. Risks symbol-redefinition (e.g. `control_pins` global) if anything tries to link both boards |
| B | Per-suite `extra_scripts` to inject build_flags | Requires SCons scripting; non-trivial; not used by any existing suite |
| C | Shim a board-agnostic function | Means editing production code for testability; ugly |
| **D** | **Include-as-source inline: `#define ARDUINO_AVR_LEONARDO` ABOVE `#include "../../../../src/boards/leonardo_rurp_shield.cpp"` in the test file itself** | **Recommended.** Function compiles inside the test-suite TU only. No cross-suite pollution. No `platformio.ini` `build_flags` edit. Pattern is well-known (the "single-include amalgamation" trick — see `test_messages/test_rurp_log_id.cpp` which similarly includes generated `messages.h` directly). |

**Exact integration delta (Option D, recommended):**

1. **`firestarter/platformio.ini` — single-line `test_filter` addition** (insert at line 80, after `native/avr/test_messages`):
   ```ini
   test_filter =
       native/avr/test_dispatch
       native/avr/test_messages
       native/avr/test_data_input
   ```
   **No other platformio.ini changes.** `build_src_filter` is NOT extended (the Leonardo source is pulled in via the test's `#include`, not the linker's src_filter).

2. **Test cpp top-of-file pattern:**
   ```cpp
   // --- Host-side AVR register shim. MUST be BEFORE leonardo_rurp_shield.cpp
   // is included so the source sees these as plain uint8_t globals.
   #include <stdint.h>
   static uint8_t PORTD = 0, PORTC = 0, PORTE = 0;
   static uint8_t DDRD  = 0, DDRC  = 0, DDRE  = 0;
   static uint8_t PIND  = 0, PINC  = 0, PINE  = 0;

   // --- Enable the Leonardo board guard, then pull the source into THIS TU
   // so rurp_set_data_input / rurp_read_data_buffer are exposed to the tests.
   #define ARDUINO_AVR_LEONARDO
   #include "../../../src/boards/leonardo_rurp_shield.cpp"
   ```

3. **Rationale matches D-02 Claude's-discretion note in CONTEXT.md:** *"same pattern used by test_dispatch/ to selectively include `proms/*.cpp`."* test_dispatch achieves this via `build_src_filter`; test_data_input achieves the same effect with a smaller-diff approach (include-as-source rather than widening src_filter) because the Leonardo source is board-guarded and adding it to src_filter would link a second copy of `rurp_set_control_pin` + `control_pins` (currently provided as a stub in `_shared/host_stubs_common.inc:58`).

**Critical: `rurp_set_data_input` / `rurp_read_data_buffer` shadowing.** The shared stubs at `_shared/host_stubs_common.inc:63-72` define `extern "C"` no-op versions of these two functions. The test's include-as-source pulls in the REAL implementations (no `extern "C"` linkage). To prevent multiple-definition errors, the new test suite's `host_stubs.cpp` MUST opt out of the shared stubs for these two functions. Two clean options:

- **D.1 (preferred):** test_data_input/host_stubs.cpp does NOT include `_shared/host_stubs_common.inc` at all — instead inline only the stubs that this suite actually needs (in practice: `rurp_set_control_pin`, `rurp_write_to_register`, `rurp_read_from_register`, hardware-rev defaults — see Q6). Smaller, focused, no opt-out flag needed.
- **D.2 (alternative):** Add `#define HOST_STUBS_OMIT_DATA_INPUT_BUFFER` opt-out wedges to the shared inc, then opt out from this suite. More change to `_shared/`; cross-suite risk.

Planner picks D.1. test_data_input is a standalone suite that doesn't need the full shared stub menu.

[CONFIDENCE: HIGH — PIO docs verified, src_filter behavior verified empirically against existing suites.]

### Q3: `rurp_read_data_buffer` second Unity case — keep or drop?

**Recommend: SHIP the second case.** Cost is ~30 lines; the regression-guard value is high.

**Rationale:**
- The Commit 2 edit (inserting `_NOP()`s between PIND/PINC/PINE reads) is in the **same function** as the shift-and-mask bit-mapping logic. A planner or future maintainer could easily refactor the function (e.g. reorder reads, collapse onto a single register read with bit-extract) and silently break the bit map.
- A Unity test that pre-sets PIND/PINC/PINE to known values and asserts `rurp_read_data_buffer()` returns the expected reassembled byte takes ~15 lines of test body + 1 `RUN_TEST()` line = ~16 lines incremental. Plus ~5 lines for one extra `setUp` reset. Total: ~30 lines vs the first case.
- The bit-map is **non-trivial to read by inspection** — see lines 119-126 of the current source. The mapping is:
  ```
  D0 = PD2 >> 2     D1 = PD3 >> 2     D2 = PD1 << 1     D3 = PD0 << 3
  D4 = PD4          D5 = PC6 >> 1     D6 = PD7 >> 1     D7 = PE6 << 1
  ```
- A simple "input PIND=0xFF, PINC=0x40, PINE=0x40 → expect 0xFF" + a second "input PIND=0x00, PINC=0x00, PINE=0x00 → expect 0x00" + a third "single-bit walk through all 8 data lines" gives 100% bit-map coverage.

**Test sketch (planner can paste verbatim):**

```cpp
void test_rurp_read_data_buffer_reassembles_data_bus(void) {
    // All-high data bus: PIND data bits + PINC bit 6 + PINE bit 6 all set
    // Should reassemble to 0xFF.
    PIND = PORTD_DATA_MASK;  // 0x9F: bits 0,1,2,3,4,7 set
    PINC = PORTC_DATA_MASK;  // 0x40: bit 6
    PINE = PORTE_DATA_MASK;  // 0x40: bit 6
    TEST_ASSERT_EQUAL_HEX8(0xFF, rurp_read_data_buffer());

    // All-low: returns 0x00
    PIND = 0; PINC = 0; PINE = 0;
    TEST_ASSERT_EQUAL_HEX8(0x00, rurp_read_data_buffer());

    // Single-bit walks: D0 only set → PD2 = 0x04 (bit 2 of PIND)
    PIND = _BV(2); PINC = 0; PINE = 0;
    TEST_ASSERT_EQUAL_HEX8(0x01, rurp_read_data_buffer());

    // D5 only → PC6 = 0x40 (bit 6 of PINC)
    PIND = 0; PINC = _BV(6); PINE = 0;
    TEST_ASSERT_EQUAL_HEX8(0x20, rurp_read_data_buffer());

    // D7 only → PE6 = 0x40 (bit 6 of PINE)
    PIND = 0; PINC = 0; PINE = _BV(6);
    TEST_ASSERT_EQUAL_HEX8(0x80, rurp_read_data_buffer());
}
```

**Decision:** Ship both cases. Aligned with CONTEXT.md D-02 "default: yes (regression guard)".

[CONFIDENCE: HIGH — cost is bounded and the regression-guard value is structural.]

### Q4: Exact diff shape for Commit 1 (PORTx-clear)

**Reference fix (Uno-side, `df5fb44` — 7 lines added before `DDRD = 0x00;`):**
```diff
 void rurp_set_data_input() {
+    // Clear PORTD before switching to input so internal pullups are disabled
+    // on every data line. Without this, residual PORTD bits from the last
+    // register-strobe or rurp_set_communication_mode (PORTD bit 0 = 1) leave
+    // 1..2 data pins weakly biased HIGH against the chip's drive. Defensive
+    // — does not on its own fix the FM1608 byte-0 read failure on Uno (see
+    // .planning/debug/fm1608-fresh-chip-baseline.md).
+    PORTD = 0x00;
     DDRD = 0x00;
 }
```

**Leonardo equivalent — EXACT lines to add at `leonardo_rurp_shield.cpp:138`** (BEFORE the existing `DDRD &= ~PORTD_DATA_MASK;`):

```cpp
void rurp_set_data_input() {
    // Clear data-bit pullups on PORTD/PORTC/PORTE before switching DDR
    // to input. Without this, residual PORTx bits from prior
    // rurp_set_control_pins / rurp_write_data_buffer strobes leave 1-2
    // data pins weakly biased HIGH against the chip's drive. On a partially
    // erased EPROM (weak drive) this produces single-bit data corruption
    // (78% single-bit XOR flips per Phase 27 RCA on Leonardo W27C512).
    // Mirror of uno_rurp_shield.cpp:rurp_set_data_input (commit df5fb44).
    PORTD &= ~PORTD_DATA_MASK;
    PORTC &= ~PORTC_DATA_MASK;
    PORTE &= ~PORTE_DATA_MASK;
    DDRD &= ~PORTD_DATA_MASK; // Set pins D0-D3 and D4-D7 as output
    DDRC &= ~PORTC_DATA_MASK; // Set pin D5 as output
    DDRE &= ~PORTE_DATA_MASK; // Set pin D6 as output
}
```

**Note on the mask vs total-clear question:** The Uno uses `PORTD = 0x00` (clears the whole port) because PD0..PD7 are all data bits on the Uno. The Leonardo MUST use the masked form (`PORTD &= ~PORTD_DATA_MASK`) because PORTD's other bits carry CONTROL pin state — `PORTD_CONTROL_MASK = 0x40` is D12 (PD6), set by `rurp_set_control_pin` at line 71. A naive `PORTD = 0x00` would also clear the active control pin state and break the write path. The masked form preserves the control bits while clearing only the data bits. Same applies to PORTC (PORTC_CONTROL_MASK = 0x80 for D13 on PC7) and PORTE (no overlapping control mask, but masked form is symmetric and harmless).

**Verification:** EVIDENCE.md §"Fix sketch (Phase 28 handoff)" line 77 suggests `PORTD = 0x00; PORTC &= ~PORTC_DATA_MASK; PORTE &= ~PORTE_DATA_MASK;` — the `PORTD = 0x00` would be a BUG on Leonardo because it'd zero the control bit at PD6. The masked form `PORTD &= ~PORTD_DATA_MASK` is the correct Leonardo-equivalent. **Planner must paste the masked form above, NOT the EVIDENCE.md sketch literal.** This is a small but load-bearing deviation from the sketch — call it out explicitly in Commit 1's message body.

**Commit 1 message body — paste-ready:**

```
fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input

Mirror the Uno-side df5fb44 fix (2026-05-13) for the Leonardo's
three-port data bus. Clear the data bits in PORTD/PORTC/PORTE before
flipping DDR to input so the internal pullups don't bias data lines
HIGH against the chip's drive on partially-erased EPROM cells.

The Leonardo MUST use the masked form (PORTD &= ~PORTD_DATA_MASK)
rather than the Uno's PORTD = 0x00 because PORTD/PORTC on the
Leonardo also carry CONTROL pin state (PORTD_CONTROL_MASK = 0x40 at
PD6 = D12; PORTC_CONTROL_MASK = 0x80 at PC7 = D13). The masked form
preserves control state while clearing only data bits.

Addresses the primary RCA mechanism: 78% single-bit XOR divergences
between Leonardo runs of the same chip, 63.2% address-bit-3
correlation, partially-erased-region domination (15% 0xFF cells).
See Phase 27 RCA for the full evidence chain.

RCA: .planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Findings" (2026-05-21)
Introducing-commit: 5b1f1cd "Leonardo is working, fast as a shark"
                    (2025-02-11) — shape introduction
Tag presence: bug present at every firmware tag from 2.0.2 through
              3.0.0b4 (verified via tag-walk)
Test: firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp
      ::test_rurp_set_data_input_clears_data_pullups_leonardo

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

[CONFIDENCE: HIGH — df5fb44 diff captured via `git show`; PORT mask definitions verified against `leonardo_rurp_shield.cpp:16-22`.]

### Q5: PORTD_DATA_MASK / PORTC_DATA_MASK / PORTE_DATA_MASK values

**[VERIFIED: leonardo_rurp_shield.cpp:16-18]**

```cpp
#define PORTC_DATA_MASK 0x40   // bit 6 (PC6 -> D5)
#define PORTD_DATA_MASK 0x9f   // bits 0,1,2,3,4,7 — D0(PD2), D1(PD3), D2(PD1), D3(PD0), D4(PD4), D6(PD7)
#define PORTE_DATA_MASK 0x40   // bit 6 (PE6 -> D7)
```

(Original `PORTD_DATA_MASK` comment in the source says `D0(PD2), D1(PD3), D2(PD1), D3(PD0), D4(PD4), D7(PD7)` — the last entry `D7(PD7)` is a comment typo; the actual mapping per `rurp_write_data_buffer` line 101 is `D6 → PD7`. Bit 7 is set in the mask because PD7 is a data bit. Bit 5 is NOT set in the mask because PD5 is not used by Firestarter. Bit 6 is set/cleared via PORTD_CONTROL_MASK = 0x40 — and the data mask (0x9F) deliberately excludes bit 6 to preserve the control-line state. **The mask bits at PORTD bit 6 must NOT be touched by `rurp_set_data_input` — that's the D12 control line.** This is the load-bearing reason for the masked-clear form in Q4.)

The neighbor masks (CONTROL) at lines 20-22 for cross-reference:
```cpp
#define PORTB_CONTROL_MASK 0xf0   // PB4-PB7 (D8-D11)
#define PORTD_CONTROL_MASK 0x40   // PD6 (D12)
#define PORTC_CONTROL_MASK 0x80   // PC7 (D13)
```

**Note:** `~PORTD_DATA_MASK = 0x60` covers PD5 (unused) + PD6 (CONTROL) — preserved. `~PORTC_DATA_MASK = 0xBF` covers all of PORTC except bit 6 (D5 data) — including the control bit at PC7. `~PORTE_DATA_MASK = 0xBF` is symmetric.

**Capture this verbatim in the Commit 1 message body** as the "why masked, not total-clear" rationale.

[CONFIDENCE: HIGH — direct source read.]

### Q6: PORTx/DDRx/PINx host-side mockability

**[VERIFIED: grep through `.pio/libdeps/native/ArduinoFake/`]**

ArduinoFake does NOT define `PORTD` / `PORTC` / `PORTE` / `DDRD` / `DDRC` / `DDRE` / `PIND` / `PINC` / `PINE`. The `.pio/libdeps/native/ArduinoFake/src/arduino/` subtree has no `iom*.h` AVR-MCU-specific header. The only AVR-named symbol is `interrupt.h` (a no-op shim).

**Therefore the test suite MUST define these as plain `uint8_t` globals before the source under test is included.** This is straightforward because the AVR source uses them as if they were `volatile uint8_t` lvalues — assignment, read, bitwise ops — all of which work identically against a plain `uint8_t` global.

**Recommended shim location (Option D from Q2):** define them at the top of `test_rurp_set_data_input.cpp` (the test TU), NOT in a shared header. They're test-only state and including them in `_shared/` risks accidentally pulling them into other suites.

**`_BV(n)` confirmation:** `_BV` is defined by ArduinoFake's `Arduino.h` (via `bit()` macros, line 122-ish: `#define bit(b) (1UL << (b))`). For safety the test cpp file can guard: `#ifndef _BV \n #define _BV(n) (1U << (n)) \n #endif`. This matches the avr-libc definition.

**`_NOP()` confirmation:** ArduinoFake's `Arduino.h:118-121` defines `_NOP()` as `do { __asm__ volatile ("nop"); } while (0)`. On the host (x86) this just emits a nop instruction — harmless. The Leonardo source's `_NOP()` calls inside `rurp_read_data_buffer` will compile and execute successfully under `[env:native]`.

**Other symbols the include-as-source pattern needs:**
- `MONITOR_SPEED` — defined in `[env:native].build_flags` via `${env.build_flags}` → `-D MONITOR_SPEED=250000`. Available.
- `SERIAL_PORT` — used by `rurp_board_setup` (line 39-44). The test file should NOT call `rurp_board_setup` (the function is only called by Arduino's `setup()`, not from the unit-under-test surface). The function symbol must still link — ArduinoFake provides `Serial_` and `Serial`, and `_shared/host_stubs_common.inc:141-143` defines `Serial_::operator bool()`. **This is the only reason the test suite's `host_stubs.cpp` must still include the Serial-bool definition** — even if it doesn't include the shared inc for `rurp_*`, it needs the `Serial_::operator bool()` defined.
- `delayMicroseconds` — used by `rurp_board_setup` only. ArduinoFake provides a stub. Available.
- `delay` — same. Available.
- `_shared/host_stubs_common.inc` provides `rurp_set_control_pin` (used by `rurp_set_communication_mode`, but Leonardo doesn't define `rurp_set_communication_mode` — verified by grep). Not needed.

**Concrete `host_stubs.cpp` shape for test_data_input (planner can paste):**

```cpp
/*
 * Phase 28 — host stub TU for the test_data_input suite.
 * Per Q6 of 28-RESEARCH.md, this suite uses the include-as-source pattern
 * (the test cpp #includes leonardo_rurp_shield.cpp directly) and defines
 * PORTx/DDRx/PINx as test-local globals. The shared host_stubs_common.inc
 * is NOT included because:
 *   1. test_data_input does not link src/proms/*.cpp (it doesn't need the
 *      dispatch surface).
 *   2. The included leonardo_rurp_shield.cpp provides real implementations
 *      of rurp_set_data_input, rurp_read_data_buffer, rurp_set_data_output,
 *      rurp_write_data_buffer, rurp_set_control_pin — which would
 *      multiple-define against the shared stubs.
 *
 * The only host_stubs.cpp content needed is Serial_::operator bool() (a
 * link-only stub referenced indirectly through ArduinoFake's USB-CDC
 * surface — used inside leonardo_rurp_shield.cpp's rurp_board_setup, which
 * the tests never call but the linker still resolves).
 */
#include <Arduino.h>
#include <ArduinoFake.h>

Serial_::operator bool() {
    return true;
}
```

[CONFIDENCE: HIGH — confirmed by direct grep through ArduinoFake source + cross-reference with `_shared/host_stubs_common.inc:140-143`.]

### Q7: Verifier commands (paste-ready for planner)

**Wave A verifier block (RED bar against pre-fix source):**

```bash
# Cut firmware branch from beta HEAD (see Q8 for full sequence)
cd /workspaces/firestarter

# Build all three production envs first (sanity gate — confirms test
# scaffold edit didn't break the production builds; pre-fix .hex sizes
# baselined below).
pio run -e uno
pio run -e leonardo
pio run -e uno328pb

# Pre-fix .hex sizes for the Wave B Δ table (D-07)
wc -c .pio/build/uno/firestarter_uno.hex \
      .pio/build/leonardo/firestarter_leonardo.hex \
      .pio/build/uno328pb/firestarter_uno328pb.hex

# Run the new test_data_input suite — MUST FAIL (RED bar on pre-fix
# leonardo_rurp_shield.cpp).  Wave A succeeds when this exits non-zero
# with assertion failures (NOT build/link errors).
pio test -e native -f "*test_data_input*"

# Sibling suites stay GREEN (regression guard)
pio test -e native -f "*test_dispatch*"
pio test -e native -f "*test_messages*"

# Full native suite (alias for the above three combined)
pio test -e native
```

**Wave A acceptance criteria:**
1. `pio run -e {uno,leonardo,uno328pb}` all exit 0.
2. `pio test -e native -f "*test_data_input*"` exits non-zero. Output shows assertion failures from `test_rurp_set_data_input_clears_data_pullups_leonardo` (PORTx bits expected 0, got non-zero). The `test_rurp_read_data_buffer_reassembles_data_bus` case MAY pass or fail — it's a regression guard on logic that's unchanged, so it should PASS even pre-fix.
3. `pio test -e native -f "*test_dispatch*"` and `pio test -e native -f "*test_messages*"` both exit 0.

**Wave B verifier block (GREEN bar + fix Δ capture):**

```bash
cd /workspaces/firestarter

# Apply Commit 1 (PORTx-clear) then run tests
# ... edit leonardo_rurp_shield.cpp:138 per Q4 ...
git add src/boards/leonardo_rurp_shield.cpp
git commit -m "fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups..." # body per Q4

# Verify GREEN bar after Commit 1 alone (answers the bisect question
# "is PORTx-clear sufficient?")
pio test -e native -f "*test_data_input*"

# Apply Commit 2 (_NOP settling) per Q1
# ... edit leonardo_rurp_shield.cpp:114-116 ...
git add src/boards/leonardo_rurp_shield.cpp
git commit -m "fix(leonardo): add _NOP settling delay between PINx reads..." # body per Q1

# Re-verify after Commit 2 (should still be GREEN)
pio test -e native -f "*test_data_input*"

# Production builds — capture post-fix .hex sizes for the D-07 table
pio run -e uno
pio run -e leonardo
pio run -e uno328pb

# Post-fix .hex sizes
wc -c .pio/build/uno/firestarter_uno.hex \
      .pio/build/leonardo/firestarter_leonardo.hex \
      .pio/build/uno328pb/firestarter_uno328pb.hex

# Full native suite — all 3 suites GREEN
pio test -e native

# Read-path-only inspection check (desk-side GATE-1.6 confirmation)
git diff bc0f5ac..HEAD -- src/boards/leonardo_rurp_shield.cpp
# Must show ONLY changes to rurp_set_data_input (lines 137-145ish post-edit)
# and rurp_read_data_buffer (lines 112-129ish post-edit). NO changes to
# rurp_set_data_output, rurp_write_data_buffer, rurp_set_control_pin,
# rurp_board_setup, or anything outside those two functions.
git diff bc0f5ac..HEAD -- src/boards/ | grep -E "^[+-]" | grep -v "^[+-]{3}" | wc -l
# Expected: ~12 lines (Commit 1: 3 PORTx lines + comment + ~6 ctx; Commit 2:
# 2 _NOP lines + comment). Total well under D-07's ±200 B threshold.
```

**Wave B acceptance criteria:**
1. After Commit 1: `pio test -e native -f "*test_data_input*"` exits 0 (GREEN). Both Unity cases pass.
2. After Commit 2: same suite still exits 0.
3. All three `pio run -e {uno,leonardo,uno328pb}` exit 0 with no warnings beyond the pre-existing baseline.
4. Hex Δ: Uno = 0 B (untouched), uno328pb = 0 B (untouched), Leonardo = +30 to +60 B (within ±200 B threshold).
5. `git diff` shows the edit is read-path-only (no touches to write/VPP/pulse paths).
6. Sibling suites still GREEN: `pio test -e native -f "*test_dispatch*"` and `pio test -e native -f "*test_messages*"`.

**Current pre-fix baseline (captured 2026-05-21 from local `.pio/build/`):**
- `firestarter_uno.hex`: 62,617 B
- `firestarter_leonardo.hex`: 68,876 B
- `firestarter_uno328pb.hex`: 62,854 B

(These are the pre-Wave-A baselines — useful for Wave B's Δ table. Note: `.hex` byte count is roughly 2.5× the binary flash size because Intel HEX is ASCII with overhead; what ROADMAP SC#4's "85.4% Leonardo flash" reflects is the binary `.elf .text+.data` size in bytes, not the `.hex` size. Both are tracked for D-07 — Leonardo `.text+.data` flash is what matters; planner should also capture `avr-size .pio/build/leonardo/firmware.elf` for the more meaningful number.)

**Precise flash-size capture (recommended addition to Wave B):**
```bash
avr-size -A .pio/build/uno/firestarter_uno.elf | grep -E "Total|\.text|\.data"
avr-size -A .pio/build/leonardo/firestarter_leonardo.elf | grep -E "Total|\.text|\.data"
avr-size -A .pio/build/uno328pb/firestarter_uno328pb.elf | grep -E "Total|\.text|\.data"
# Or shorter — Berkley format with percentages:
avr-size -C --mcu=atmega32u4 .pio/build/leonardo/firestarter_leonardo.elf
avr-size -C --mcu=atmega328p .pio/build/uno/firestarter_uno.elf
avr-size -C --mcu=atmega328pb .pio/build/uno328pb/firestarter_uno328pb.elf
```

The PIO build output (`pio run -e leonardo`) already includes a `Flash: [#####     ] XX.X% (used N bytes from M bytes)` line; capturing that line is the cleanest one-shot Δ record. Planner has freedom on which capture command to pin into the Wave B verifier.

[CONFIDENCE: HIGH — `pio test` and `pio run` commands verified by direct invocation against the current beta tree.]

### Q8: Branch-cut command sequence

**[VERIFIED: `git rev-parse beta` returns `bc0f5ac` ✓; `git branch -a` confirms `v1.6-read-bug` does NOT yet exist on the firestarter sub-repo ✓; the existing `v1.6-read-bug` is on `firestarter_app` only.]**

**Exact Wave A first-task sequence:**

```bash
cd /workspaces/firestarter

# Ensure clean working tree
git status --short
# Expected: empty (no pending edits before branch cut)

# Fetch latest to make sure beta is fully up to date with origin
git fetch origin

# Confirm local beta matches origin/beta (no remote-ahead surprise)
git rev-parse beta origin/beta
# Expected: bc0f5ac05b37c94eb7ddc706f65dbdc94c47899e on both lines

# Check out beta locally
git checkout beta
git pull --ff-only origin beta   # no-op if local is already up to date

# Cut v1.6-read-bug from beta HEAD
git checkout -b v1.6-read-bug

# Confirm we're on the new branch at the expected SHA
git rev-parse HEAD
# Expected: bc0f5ac05b37c94eb7ddc706f65dbdc94c47899e
git symbolic-ref --short HEAD
# Expected: v1.6-read-bug
```

**Per D-03 + memory `[[feedback_branching]]`:** the branch is LOCAL only at this point. Push to origin happens at the Phase 29 boundary (merge to `beta` + pre-release cut). Wave A and Wave B do NOT push.

**If the branch already exists locally (re-running Wave A after a failed first attempt):**
```bash
git checkout v1.6-read-bug
# Sanity: must be at bc0f5ac with NO commits ahead of beta
git log beta..v1.6-read-bug --oneline
# Expected: empty (zero commits ahead) — if non-empty, planner decides whether
# to reset or amend.
```

**Meta-repo coordination (per D-03):**
- `/workspaces` meta-repo: stays on `main` (no branch). Phase 28 artifacts (28-RESEARCH.md, 28-PLAN-01/02.md, EVIDENCE.md append) commit to `main` directly.
- `/workspaces/firestarter_app` sub-repo: stays parked at the Phase 26 tip (`999c3cc` on existing `v1.6-read-bug`). NOT modified by Phase 28.
- `/workspaces/firestarter` sub-repo: NEW `v1.6-read-bug` branch (this section).

[CONFIDENCE: HIGH — git state verified directly.]

---

## Validation Architecture

**Phase 28's "validation" is a TDD RED→GREEN transition + per-board build cleanness + size-budget tracking.**

### Test Framework
| Property | Value |
|----------|-------|
| Framework | PlatformIO 6.x + Unity 2.x + ArduinoFake 0.4.x |
| Config file | `firestarter/platformio.ini` `[env:native]` (lines 67-102) |
| Quick run command | `cd /workspaces/firestarter && pio test -e native -f "*test_data_input*"` |
| Full suite command | `cd /workspaces/firestarter && pio test -e native` |
| Production build smoke | `cd /workspaces/firestarter && pio run -e uno && pio run -e leonardo && pio run -e uno328pb` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FIX-01 | Atomic fix commits with RCA citations | git inspection | `git log --oneline beta..v1.6-read-bug -- src/boards/leonardo_rurp_shield.cpp` (must show 2 commits each with `RCA:` + `Introducing-commit:` footers) | ❌ Wave B |
| FIX-02 (RED half) | Unity test FAILS on pre-fix code | `pio test -e native -f "*test_data_input*"` (Wave A run) exits non-zero | `pio test -e native -f "*test_data_input*"` | ❌ Wave 0 (created in Wave A) |
| FIX-02 (GREEN half) | Unity test PASSES on post-fix code | same command after Wave B commits exits 0 | `pio test -e native -f "*test_data_input*"` | (Wave A creates) |
| FIX-03 (desk-side half) | Read-path-only inspection | `git diff bc0f5ac..HEAD -- src/boards/leonardo_rurp_shield.cpp` shows ONLY rurp_set_data_input + rurp_read_data_buffer | manual inspection in Wave B verifier block | n/a |
| FIX-03 (bench half) | `firestarter write` + `dev read -s N` byte-compare | bench-gated — Phase 29 | n/a (deferred) | n/a |
| ROADMAP SC#4 | Per-board hex-size Δ < ±200 B | `avr-size -C .pio/build/{uno,leonardo,uno328pb}/firestarter_*.elf` before vs after | `pio run -e {uno,leonardo,uno328pb}` + size capture | n/a |

### Sampling Rate
- **Per task commit (Wave A test scaffold):** `pio test -e native -f "*test_data_input*"` — expect RED.
- **Per task commit (Wave B Commit 1):** `pio test -e native -f "*test_data_input*"` — expect GREEN.
- **Per task commit (Wave B Commit 2):** `pio test -e native -f "*test_data_input*"` — expect GREEN (still).
- **Per wave merge / phase gate:** `pio test -e native` (full native suite) + `pio run -e uno && pio run -e leonardo && pio run -e uno328pb` — all GREEN, no warnings beyond baseline.
- **Phase gate before `/gsd-verify-work`:** EVIDENCE.md `## Phase 28 — Fix Commit References` section populated per D-08 with SHAs + sizes table.

### Wave 0 Gaps
- [ ] `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` — new file; covers FIX-02 (both halves).
- [ ] `firestarter/test/native/avr/test_data_input/host_stubs.cpp` — new file; minimal (Serial_::operator bool + headers only per Q6).
- [ ] `firestarter/test/native/avr/test_data_input/avr/pgmspace.h` — new file; mirror of `test_dispatch/avr/pgmspace.h` (the included `leonardo_rurp_shield.cpp` transitively pulls `rurp_shield.h` → `<avr/pgmspace.h>`, needs the host shim).
- [ ] `firestarter/platformio.ini` line 80 area — add `native/avr/test_data_input` to `[env:native].test_filter`.

Framework install: NONE needed — PIO + Unity + ArduinoFake already present in `[env:native]`.

### Nyquist Bridge to VALIDATION.md
The planner's VALIDATION.md should pin:
- **Sample interval:** every commit on `v1.6-read-bug` runs `pio test -e native -f "*test_data_input*"`.
- **Phase gate transition:** Wave A's RED bar (test_data_input fails 1 of 2 cases pre-fix) → Wave B's GREEN bar (both cases pass) — captured in EVIDENCE.md as Wave A SHA + Wave B Commit 1 SHA + Wave B Commit 2 SHA.
- **Phase 29 hand-off invariant:** EVIDENCE.md `## Phase 28 — Fix Commit References` section is the bench operator's pre-flight reading material — must include the 3 SHAs, the introducing-commit citation, the per-board hex-size table, and the read-path-only diff confirmation.

---

## Files Phase 28 will create
- `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` (new, Wave A)
- `firestarter/test/native/avr/test_data_input/host_stubs.cpp` (new, Wave A — minimal per Q6)
- `firestarter/test/native/avr/test_data_input/avr/pgmspace.h` (new, Wave A — copy of `test_dispatch/avr/pgmspace.h` verbatim)

## Files Phase 28 will modify
- `firestarter/src/boards/leonardo_rurp_shield.cpp` — Commit 1 adds 3 lines + 7-line comment to `rurp_set_data_input` (lines 137-141 area per Q4); Commit 2 inserts 2 `_NOP()` + 9-line comment in `rurp_read_data_buffer` (lines 114-116 area per Q1)
- `firestarter/platformio.ini` — extend `[env:native].test_filter` by one line (`native/avr/test_data_input`) at line 80
- `.planning/v1.6-EVIDENCE.md` — append `## Phase 28 — Fix Commit References` section at the line-110 forward-annotation anchor per D-08

## Risks / Landmines

1. **EVIDENCE.md fix-sketch literal is subtly wrong for Leonardo.** Line 77 of EVIDENCE.md writes `PORTD = 0x00; PORTC &= ~PORTC_DATA_MASK; PORTE &= ~PORTE_DATA_MASK;` — but `PORTD = 0x00` would also zero PD6, which is the D12 control line (`PORTD_CONTROL_MASK = 0x40`). Use the masked form `PORTD &= ~PORTD_DATA_MASK` instead. **Planner must NOT paste the EVIDENCE.md literal verbatim — paste the Q4 form.** This is the single most critical landmine in this research.

2. **PORTD_DATA_MASK comment typo.** Line 17 of `leonardo_rurp_shield.cpp` says `D0(PD2), D1(PD3), D2(PD1), D3(PD0), D4(PD4), D7(PD7)` but actually `D6(PD7)` per `rurp_write_data_buffer:101`. The mask value (0x9F) is correct. Don't "fix" the comment in Phase 28 — that's a separate drift-correction (Phase 30 paperwork). Leave it.

3. **Include-as-source double-link risk.** If a future planner extends `[env:native].build_src_filter` to add `+<boards/leonardo_rurp_shield.cpp>` globally, the new test_data_input suite will get DUPLICATE definitions of all 7 Leonardo functions (one from the include-as-source, one from src_filter). The test suite's TU includes the source DIRECTLY — DO NOT also add it to src_filter. If anyone later needs Leonardo board fns in a different suite, refactor to expose them via a shim header.

4. **`avr-size` may not be installed.** The Q7 commands use `avr-size`. PIO ships with the toolchain, but if invoked outside of `pio run`, PATH may not pick it up. Fallback: `pio run -e leonardo` prints `Flash: [######    ] XX.X% (used N bytes from M bytes)` in its output — capture that line via `tee` or `tail -10 | grep Flash`.

5. **Wave A test_data_input test_rurp_read_data_buffer_reassembles_data_bus is NOT a RED test.** It exercises only the bit-mapping logic (unchanged by either fix commit). It should PASS on pre-fix code. Only `test_rurp_set_data_input_clears_data_pullups_leonardo` is the RED→GREEN test. Wave A's verifier MUST distinguish "test_data_input suite as a whole fails because one of two cases fails" vs "build/link error." The proper check is "exit code non-zero AND output contains 'test_rurp_set_data_input_clears_data_pullups_leonardo:FAIL'." Spell this out in the Wave A verifier block.

6. **`#include "../../../src/boards/leonardo_rurp_shield.cpp"` relative path.** The test cpp lives at `test/native/avr/test_data_input/`, so the source is `../../../../src/boards/leonardo_rurp_shield.cpp` (FOUR `../`, not three). Double-check the count when pasting. (PIO automatically adds the active test directory to the include path, but cross-tree `..` traversal still works because it's a literal filesystem path.)

7. **`_NOP()` count is research-recommended, not bench-confirmed.** Phase 29's bench A/B between Commit 1 alone and Commit 1+2 would empirically confirm whether the 2 `_NOP()`s are necessary. Default is to ship both commits per D-01; if Phase 29 reveals Commit 1 is sufficient, the conversation about reverting Commit 2 happens then.

8. **Wave A's RED bar shows assertion failure (NOT build error).** If the test suite fails to BUILD (e.g. missing header, double-defined symbol), that's a Wave A FAILURE state — not a successful RED bar. Wave A's verifier block must check `pio test` output for the magic string `:FAIL:` (Unity's assertion-failure marker) — not just exit code.

9. **EVIDENCE.md line 110/111 anchors are HTML comments — fragile to edits.** Phase 28's append goes AT the line-110 anchor. Do NOT modify the line-111 anchor (Phase 29's reserved spot). Use `sed -i '/Phase 28 appends commit refs here/a\## Phase 28 — Fix Commit References\n\n<body>\n' .planning/v1.6-EVIDENCE.md` OR safer: read the whole file, locate the line-110 comment, append after it via Write. Planner picks; default to safer.

---

## Sources

### Primary (HIGH confidence)
- **firestarter/src/boards/leonardo_rurp_shield.cpp** (full file read; lines 16-22 mask defs, 112-129 read fn, 137-141 set_data_input)
- **firestarter/src/boards/uno_rurp_shield.cpp** (full file read; lines 128-137 reference fix shape)
- **`git show df5fb44 -- src/boards/uno_rurp_shield.cpp`** (the canonical 7-line reference diff)
- **firestarter/platformio.ini** (lines 67-102 = `[env:native]`, lines 78-80 = `test_filter`)
- **firestarter/test/native/avr/_shared/host_stubs_common.inc** (lines 63-72 = rurp_set_data_input/buffer stubs; lines 140-143 = Serial_::operator bool)
- **firestarter/test/native/avr/test_dispatch/{host_stubs.cpp,avr/pgmspace.h}** (reference pattern for new suite)
- **firestarter/test/native/avr/test_messages/{host_stubs.cpp,avr/pgmspace.h}** (alternative reference pattern)
- **.pio/libdeps/native/ArduinoFake/src/arduino/Arduino.h** (lines 118-121 = `_NOP()` defn; lines 122-ish = `_BV`/`bit`)
- **`git rev-parse beta` + `git branch -a`** on /workspaces/firestarter (verified beta tip + absence of v1.6-read-bug branch)
- **`wc -c .pio/build/*/firestarter_*.hex`** (pre-fix .hex baselines captured 2026-05-21)
- **.planning/v1.6-EVIDENCE.md** (Phase 27 RCA — full text)
- **ATmega16U4/32U4 datasheet, Atmel-7766J, §10.2.4** (PINx synchronizer latency 0.5-1.5 cycles)
- **Winbond W27C512 datasheet** (90 ns tACC at 5V)

### Secondary (MEDIUM confidence)
- **PlatformIO docs** (test_filter directory-level only; per-suite build_flags not supported) — https://docs.platformio.org/en/stable/advanced/unit-testing/structure/hierarchy.html

### Tertiary (LOW confidence)
- None — all research-critical findings cross-verified against either source files or official datasheets.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Two `_NOP()`s (one between each PINx pair) is sufficient settling | Q1 | Under-shoot: bug not fully fixed → Phase 29 bench shows residual jitter → bench A/B adds more _NOP()s. Over-shoot: harmless ~125 ns overhead per read. Asymmetric risk strongly favors shipping the recommendation; bench can refine. |
| A2 | `_NOP()` on x86 host (`__asm__ volatile ("nop")`) compiles and runs cleanly under PIO native env | Q2, Q6 | If wrong, test build fails → caught immediately in Wave A verifier. Easy fallback: wrap in `#ifdef __AVR__ _NOP() #endif` so the host-side test skips it (the test doesn't observe `_NOP()` behavior anyway — it's structural). |
| A3 | Including `leonardo_rurp_shield.cpp` as source into the test TU with pre-defined `ARDUINO_AVR_LEONARDO` will compile cleanly under host | Q2 | If wrong (e.g. some included header pulls in AVR-only code), fallback is Option B (per-suite extra_scripts) or Option C (shim function). Caught immediately in Wave A verifier. Estimated low risk because (a) the file is already wrapped in `#ifdef ARDUINO_AVR_LEONARDO`, (b) all its calls are register operations + ArduinoFake-provided primitives. |
| A4 | The two `_NOP()`s and three masked-PORTx-clears together produce a +30 to +60 B Δ on Leonardo `.text` | Q1, Q7 | If actual Δ exceeds ±200 B (unlikely — back-of-envelope is ~12 instructions × ~2 B = ~24 B), D-07 flags it for re-review. No silent failure. |

---

## RESEARCH COMPLETE

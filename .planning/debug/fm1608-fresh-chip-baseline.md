---
slug: fm1608-fresh-chip-baseline
status: parked-2026-05-18
trigger: "Lets check whats going on with the FM1608, I have a new IC"
created: 2026-05-13T12:45:49Z
updated: 2026-05-18T08:00:00Z
reopened: 2026-05-13T15:45:00Z
reopened_reason: "Prior Resolution recommended Leonardo as the fix path for FM1608, which violates the project constraint that Uno and Leonardo are both first-class operator choices. Root-cause diagnosis (PORTD/CE coupling) stands; remediation must restore Uno support."
parked_reason: "Bug localized to this specific Uno board's hardware on 2026-05-18 via chip-swap + shield-swap cross-tests. Every Uno-firmware fix attempted has failed. Next step requires bench access to a different Uno board or a scope on /CE — operator chose to park and work on something else."
---

# FM1608 fresh-chip baseline validation

## Symptoms

- **Expected behaviour**: full 8KB round-trip md5-identical with `firestarter write FM1608 <file>` then `firestarter read FM1608 <readback>`. Dispatch should route through `DIP28_JEDEC_SRAM_8K` pinout + `configure_sram` (algo 0x28 — no VPP, byte-write).
- **Actual behaviour**: 8191/8192 bytes round-trip cleanly. Byte 0 is stuck-at-`0xFF` regardless of source pattern. **Identical symptom to the prior FM1608 chip** — refutes the chip-damage hypothesis from `04-HW-VALIDATION.md` follow_up `fm1608-db-mismatch`.
- **Error messages**: none — write reports "successful", read reports "complete". Only diff is byte 0.
- **Reproduction**: trivially reproducible across all data patterns (test pattern, 0x00, 0xAA, 0x55, 0x5A, alternating 0xAA/0x55, single-byte writes with `-a 0`). Bytes 1..8191 always reflect the source data correctly.
- **Repeatability**: three consecutive reads after a single write produce byte-identical files (md5 match) — reads are deterministic and non-destructive.

## Context

- Fresh FM1608 IC (operator confirmed brand-new, never written) on Uno Rev 2.0/2.1 shield, JP4 closed, firestarter@29567f1 firmware, firestarter_app@24f4fa4 host.
- Earlier diagnosis "chip-level damage at address 0 from wrong-pinout 12V exposure" (`04-HW-VALIDATION.md` follow_up `fm1608-db-mismatch`) is **falsified** by this run: a fresh chip that has never seen the wrong pinout exhibits the identical byte-0 stuck-at-`0xFF` symptom.
- Dispatch flow is confirmed correct: `firestarter info FM1608` shows SRAM (28-pin), 8K, vcc=5V, R/W on pin 27, NC on pins 1/26, algorithm 0x28. Host JSON sent to firmware is well-formed: `{type:4, algorithm:40, pin-count:28, vpp_mv:12000, pulse-delay:0, bus-config:{bus:[0..12], rw-pin:14}, flags:0, cmd:2, address:0}`.

## Current Focus

- **Working hypothesis (H1)**: The write of byte 0 never reaches the FRAM — byte 0 retains its factory-default value (`0xFF`) across all write attempts. The cache-skip optimization in `firestarter/include/rurp_register_utils.h` (`rurp_write_to_register` early-returns when `cache == data`) **suppresses all three shift-register clock strobes (LSB, MSB, CONTROL) on the first `memory_set_data(0, byte0)` call**, because:
  - After `command_done` from any prior command, cache = HW = `LSB=0, MSB=0, CONTROL=0`.
  - `configure_memory` line 70 calls `mem_util_set_address(handle, 0)`: LSB=0 (skip), MSB=0 (skip), CONTROL=`0x10` from `ADDRESS_LINE_17` (writes — cache `0 → 0x10`).
  - First `memory_set_data(0, byte0)` then recomputes the same target values: LSB=0, MSB=0, CONTROL=`0x10` (all cache hits → **all skipped, no shift-register strobes**).
  - On paper the HW shift register outputs *should* still hold `0/0/0x10` from the previous strobes, so the write should land. But empirically it does not — byte 0 stays `0xFF`. This points to a subtle hardware/timing state that depends on a shift-register strobe immediately before CE pulses for the data.

- **Why bytes 1..N work**: For byte 1, LSB goes `0 → 1` → strobe fires. PORTD transitions through the LSB shift-register write before the data-buffer write. Every subsequent byte's address differs in LSB → LSB always strobes. The write lands.

- **Falsifying tests already done**:
  - Three different uniform writes (0x00, 0xAA, 0x5A) — byte 0 stays `0xFF`, bytes 1..8191 reflect each pattern. (Refutes "byte 0 holds 0xAA from a prior write".)
  - Triple-read after a single write — byte-identical readback across reads. (Reads are deterministic, not the source of variance.)
  - Single-byte write with `-a 0` — byte 0 stays `0xFF`. (Same path triggers even for a 1-byte chunk.)
  - Single-byte write with `-a 1` — byte 1 successfully updates. (Confirms the bug is address-0-specific, not "first-byte-of-chunk" generic when address != 0.)

- **Next action**: Confirm or refute H1 by adding a temporary shift-register strobe **inside `memory_set_data`** for the first iteration (e.g., force-write LSB/MSB unconditionally before each `rurp_write_data_buffer`), or alternatively bypass the cache-skip optimization for the address-bus registers entirely. If byte 0 then writes cleanly, H1 is confirmed and the fix is a targeted "no-skip on first write after configure" or "always re-strobe before CE pulse".

- **Reasoning checkpoint**: H1 is the most likely root cause given the trace evidence. Alternate hypothesis H2 (read of byte 0 fails) is still possible but less likely — reads work correctly for bytes 1..N even when MSB transitions (byte 0 read triggers `MSB: 0 → 0x40` strobe). If H1 is confirmed, the fix is small (~5 lines in `memory.cpp`) and the same fix should benefit any future address-0 single-byte operation across all dispatch handlers.

## Evidence

- timestamp: 2026-05-13T14:30:00Z
  observation: Cross-branch test — checked out `firestarter@main` (2.0.6) + `firestarter_app@main` and bench-tested the SAME FM1608 chip. Result: byte 0 = `0xFF`, bytes 1..8191 correct — IDENTICAL to feature/phase-10 behaviour. Refutes regression hypothesis: the bug exists on main too. Pre-dates this branch. Main's host dispatches FM1608 differently (algorithm=0x07 / protocol-id 0x07 / variant=38, NOT the new DIP28_JEDEC_SRAM_8K + algo 0x28 path), yet the firmware-level read of byte 0 still returns 0xFF. The common factor across both dispatch paths: `memory_get_data` reads byte 0 via the same code path.

- timestamp: 2026-05-13T14:50:00Z
  observation: THIRD FM1608 chip (operator-supplied, brought as a different IC to isolate chip-damage hypothesis). On main + main, the chip's pre-existing factory state at byte 0 = 0xFF, bytes 1..7012 contain ASCII text " Firestarter EPROM progammer, python application\nFirestarter is an application for the [Relatively-Universal-ROM-Programmer]..." — left over from a previous operator write attempt. Byte 0 was 0xFF from THAT prior write attempt too. After our test write (source byte 0 = 0x37), readback shows byte 0 = 0xFF unchanged. THREE chips, THREE write attempts (different patterns each), THREE byte-0 = 0xFF results. Refutes chip-defect hypothesis statistically.

- timestamp: 2026-05-13T14:55:00Z
  observation: Cache-skip warmup hypothesis refuted. Sequence: write 0xAA at -a 1 (forces LSB cache 0→1, strobes latch). Then write 0x42 at -a 0 (forces LSB cache 1→0, strobes latch). Read back: byte 0 = 0xFF, byte 1 = 0xAA. Strobes are confirmed firing (cache misses), but byte 0 still doesn't update. Refutes Agent H1 (cache-skip suppressing the LSB strobe on first write at address 0).

- timestamp: 2026-05-13T15:00:00Z
  observation: Firmware diagnostics added (firestarter 2.0.10-dev with log_info_format in memory_set_data + memory_get_data when address==0). Captured at byte 0 with FRESH chip + verbose host:
  - WRITE: `wr0 d=55 re=0x0 lsb=0 msb=0 ctl=16 rw=14` → data=0x37, reorg_address=0, LSB latch cache=0, MSB latch cache=0 (WE bit 14=0, write mode), CTL cache=0x10 (ADDRESS_LINE_17 HIGH → chip VCC HIGH for 28-pin), rw_line=14.
  - READ: `rd0 d=255 re=0x4000 lsb=0 msb=64 ctl=16 rw=14` → data read=0xFF, reorg_address=0x4000, MSB=0x40 (WE bit 14=1, read mode), VCC HIGH, rw_line correct.
  - **Conclusion: firmware sets ALL bus signals correctly for byte 0 (address bus, WE, CE, OE, VCC). The chip simply does not respond correctly at address 0.**

- timestamp: 2026-05-13T15:10:00Z
  observation: "All-LOW bus glitch" hypothesis tested via static-high-pins workaround. Added `"static-high-pins": [26]` to DIP28_JEDEC_SRAM_8K (chip pin 26 = NC for FM1608 — chip ignores; but forces shield A13 line HIGH so bus is never all-LOW even at address 0). Diagnostic confirms host emits `bus-config: {"static-high":[13]}`, firmware computes reorg=0x2000 for write / 0x6000 for read. Result: byte 0 STILL returns 0xFF on read. **Refutes "all-LOW bus" theory.** Reverted the pinout edit (didn't help).

## Verdict

After exhaustive investigation across 3 fresh FM1608 chips, 2 firmware versions
(main 2.0.6 and feature/phase-10 2.0.10-dev), 2 host versions (main DIP28_2764
algo=0x07 dispatch and feature/phase-10 DIP28_JEDEC_SRAM_8K algo=0x28 dispatch),
multiple hypotheses tested and **all refuted at the firmware/host level**:

  - Chip damage: refuted (3 chips identical)
  - Cross-branch regression: refuted (main has it too)
  - Cache-skip suppression: refuted (warmup test)
  - WE-settle timing: refuted (delay tested)
  - All-LOW bus: refuted (static-high-A13 workaround tested)
  - Read-side specifically vs write-side: ambiguous — both possible

**Firmware diagnostics confirm correct bus setup at byte 0.** Cross-board chip-state
inspection (Uno wrote, Leonardo read without rewriting) showed a structured
corruption pattern that points to PORTD↔CE capacitive coupling during MSB-strobe
read mode on the Uno's RURP combo (see Resolution → root_cause). The Leonardo
data bus is split across PORTD/PORTC/PORTE on non-contiguous bits, so PD6 is
NOT the chip's D6 line — hence Leonardo is unaffected.

**Constraint on remediation:** Uno and Leonardo are both first-class operator
boards. The end-user picks which board to plug the shield into; the project does
NOT route specific chips to specific boards. A firmware/host fix MUST restore
correct FM1608 behaviour on Uno — "use Leonardo" is not an acceptable resolution.

**Further investigation requires bench tools** (logic analyzer or oscilloscope
on socket pins 12 / 22 / 24 / 29 / 30) to capture what physically happens
during the byte-0 CE pulse vs byte-1 CE pulse, and to confirm/quantify the
PORTD bit 6 → CE coupling glitch during MSB strobes. Without this, candidate
fixes #1 / #2 below proceed blind and are evaluated by outcome only.

## Files involved

  - firestarter/src/proms/memory.cpp: memory_set_data + memory_get_data (correct)
  - firestarter_app/firestarter/data/pinouts.json: DIP28_JEDEC_SRAM_8K entry (correct)
  - firestarter_app/firestarter/database.py: pin_conversions[28] (correct)

## Status

REOPENED 2026-05-13 — root cause provisionally diagnosed as PORTD↔CE coupling on
Uno (see Resolution → root_cause), but prior remediation plan ("use Leonardo")
violates the board-parity constraint and is withdrawn. Investigation now focused
on Uno-supporting firmware/host fix paths queued in "Next experiments" below.
Bench tools (logic analyzer / scope) remain desirable but are no longer a
prerequisite — candidate fixes #1 / #2 are evaluable by behavioural test alone.

- timestamp: 2026-05-13T14:15:00Z
  observation: User's hypothesis "write works, read fails" was tested via `firestarter verify` — verify failed with `ERROR: 0x37 != 0xff at 0x000000`, confirming the firmware-level read of byte 0 returns 0xFF (verify uses memory_get_data, same as standalone read). However, this alone doesn't distinguish (a) chip's byte 0 IS 0xFF (write didn't land) from (b) read consistently returns 0xFF regardless of chip contents. Both hypotheses fit the host-visible behaviour.

- timestamp: 2026-05-13T14:20:00Z
  observation: Tried experimental firmware fix (firestarter 2.0.11-dev) adding `delayMicroseconds(3)` and then `delayMicroseconds(100)` between `firestarter_set_address` and `rurp_chip_enable` in `memory_get_data` (hypothesis: WE LOW→HIGH transition needs settle time for the first read after a write). Neither delay changed the symptom — byte 0 still reads 0xFF. WE settle timing is NOT the root cause.

- timestamp: 2026-05-13T14:25:00Z
  observation: Read tests at different offsets to localize: `firestarter read -a 0 -s 1` returns 0xFF; `firestarter read -a 1 -s 1` returns 0xd4 (correct); read byte 100 first then byte 0 still returns 0xFF (deterministic, not state-dependent). `firestarter dev read -a 0` (lower-level path) also returns 0xFF — every read path through memory_get_data fails at address 0.

- timestamp: 2026-05-15T22:00:00Z
  observation: **Bench session results across 4 new firmware variants — primary
  mechanism resolved, secondary byte-0 bug intractable on this bench.**

  Setup: Uno on /dev/ttyACM0, fresh FM1608 in socket, host
  firestarter@2.0.7_dev, source pattern `FM1608.bin` (8 KB, md5 `24d65f04…`,
  byte 0 = 0x4F). Verified write+read+verify after each firmware flash.

  **Variant A** (firmware 2.0.11-dev, default Uno build): always-on Uno-only
  pre-clear `PORTD = 0` + 4 NOPs before MSB-strobe data write. Result: **32-of-
  33 bytes fixed**. 256-byte-boundary corruption GONE. Three consecutive reads
  md5-identical (`ca040fbb…`). Only diff: byte 0 reads `0xFF` instead of
  `0x4F`.

  **Variant B** (firmware 2.0.11-dev + `-D FM1608_FIX_LE_DELAY_US=2`): Variant
  A plus 2 µs `delayMicroseconds(2)` between PORTD-write and LE rising on
  MSB strobes. Goal: separate PD6 di/dt from LE strobe edge to test the
  "LE-rising rail disturbance" theory. Result: **identical to Variant A**
  (md5 `ca040fbb…`, 1 diff at byte 0). LE-rise rail-disturbance theory
  refuted — Variant A's `~125 ns` PD6→LE separation is sufficient; the extra
  2 µs adds nothing.

  **Fix C** (firmware 2.0.12-dev): in `configure_memory`, for read-style
  commands on chips with `bus_config.rw_line != 0xFF`, pre-remap address 0
  through `mem_util_remap_address_bus(handle, 0, READ_FLAG)` so the initial
  `mem_util_set_address` strobes the MSB latch with the R/W bit HIGH at INIT
  phase. Goal: eliminate the WE LOW→HIGH transition that happens ~300 ns
  before byte 0's CE pulse. With Fix C, byte 0's read has *zero* strobes
  (all three latch caches hit). Hypothesis: any byte-0-specific timing issue
  related to MSB strobe immediately preceding CE# LOW should disappear.
  Result: **identical to Variant A** (md5 `ca040fbb…`, 1 diff at byte 0).
  Pre-latch hypothesis refuted — eliminating the byte-0 MSB strobe didn't
  fix byte 0.

  **Fix E** (firmware 2.0.13-dev): Fix C plus generic `READ_WRITE` CTL bit
  HIGH for read-style commands when `rw_line != 0xFF`. Goal: handle the
  shield-routing case where CTL Q6 and MSB Q6 might both feed the chip's
  /WE pin via OR/AND merge (the way `flash_utils.cpp` toggles CTL READ_WRITE
  for flash chips). Result: **identical to Variant A** (md5 `ca040fbb…`,
  1 diff at byte 0). CTL Q6 path either doesn't reach socket pin 27 on
  DIP28_JEDEC_SRAM_8K wiring, or is in an OR-merge where MSB Q6 HIGH was
  already sufficient.

  **Leonardo cross-read** confirmed byte 0's actual cell value is `0x4F`
  (Uno write landed correctly). The remaining bug is purely on Uno's read
  side at address 0.

  **Generic DB discriminator confirmed**: pinouts with `rw-pin` set
  (DIP28_JEDEC_SRAM_8K, DIP28_28C256, DIP24_6116, DIP32_28C512_EEPROM,
  DIP32_SST39SF040) drive R/W actively via the bus path; pinouts without
  `rw-pin` (DIP28_27512, DIP28_2764, DIP28_27256, DIP32_STD) don't. W27C512
  has no `rw-pin` — reads byte 0 correctly. The bug class is "chips with
  `rw-pin` set" — affects FM1608 and would predictably affect M48T08/M48T18/
  M48T58/M48T59 (Dallas TimeKeeper), DS1230(RW), FM1808, FM18W08, AT28C256,
  and others sharing the same pinout family. Not validated on those chips
  (none in operator's bench inventory this session).

  **12 cumulative firmware-side fix attempts on byte 0** (Variant A through
  Fix E here + 8 prior in this file). All produce md5-identical readback
  (`ca040fbb…`) with byte 0 = 0xFF. The root cause is **not** reachable
  through:
    - PORTD pre-clear / data-bus pre-state.
    - LE-rise / PD6 di/dt timing separation.
    - MSB latch pre-state / cache priming.
    - CTL READ_WRITE bit assertion.
    - Longer access delays (pre-CE, post-CE).
    - Warmup reads at handle->address or +1.
    - UART teardown (UCSR0B clearing).
    - Serial.end delay removal.
    - Cache invalidation on programmer-mode entry.
    - PORTD=0 before DDRD=0 (pull-up disable).
    - Duplicate write to wake chip out of standby.
    - Address-bus static-high mitigation.

  Next productive step requires **bench instrumentation** (logic analyzer or
  scope on PD0-7 + /CE + /OE + /WE during byte-0 chip-enable window) to
  determine whether the chip is driving its output at byte 0, what /WE
  actually looks like at the chip pin, and whether there's a CE coupling
  event we haven't predicted.

  **Variant A is shippable as a partial fix** — restores 32 of 33 byte
  fidelity. Byte 0 stuck-at-0xFF documented as a known limitation for
  rw-pin chips on Uno.

- timestamp: 2026-05-13T19:25:00Z
  observation: **Candidate fix #1 implemented as a two-variant build**
  (firmware 2.0.11-dev). In `firestarter/include/rurp_register_utils.h`
  `rurp_internal_write_to_register`:
    - **Variant A (always on for Uno)**: pre-clear `PORTD = 0` + 4 NOPs
      (~250 ns @ 16 MHz) before the MSB-strobe data write. Goal: push PD6's
      rising edge out of the LE pulse window.
    - **Variant B (opt-in via `-D FM1608_FIX_LE_DELAY_US=N`)**: also insert
      `delayMicroseconds(N)` between the `PORTD = data` write and the LE
      rising edge (MSB strobes only). Targets the alternative theory that
      the LE-rise edge itself disturbs the shield power rail and the chip's
      WE input sees the disturbance coincident with PD6's transient.
      Platformio.ini's `[env:uno]` carries a commented build-flag stub
      (`; -D FM1608_FIX_LE_DELAY_US=2`) — uncomment for the Variant B build.
  Build verified clean on `pio run -e uno` (Variant A: 26094 / 32256 flash,
  Variant B w/ N=2: 26106 / 32256 flash) and `pio run -e leonardo` (28390 /
  28672 flash — Leonardo `#ifdef`'d out, no impact).

  **Open mechanism question (not yet bench-resolved):** For the corruption
  pattern `chip[i*256] = 0x40 | i` to manifest as a *capture* at the MSB-
  strobe moment, the chip needs /CE LOW AND /WE LOW to coincide. /CE-LOW via
  PD6→CE coupling is the load-bearing hypothesis, but /WE state at that
  instant is murky: the MSB latch is opaque during PORTD's transition, so
  /WE follows the *previously* latched bit 6 — which is HIGH for every MSB
  strobe inside a continuous read sweep, predicting 1 corrupted byte per
  write→read transition, not 32. Three reconciling theories left open:
  (a) host issues a fresh memory-configure per chunk (resets WE-LOW each
  chunk boundary), (b) 74HC573 has an undocumented LE-rising glitch that
  briefly drops bit-6 output, (c) the LE-rise edge itself disturbs the
  shield power rail and the chip sees a combined CE/WE glitch. Theory (c)
  is what Variant B targets specifically; Variants A+B together address (b)
  and (c) but not (a). If both variants fail on the 256-byte-boundary
  corruption, theory (a) or none-of-the-above remains, and remediation
  moves to fix #2 (route R/W off MSB bit 6 onto CTL register), which
  bypasses the PD6/D6 sharing entirely and is hypothesis-independent.

  Expected outcomes:
  - Variant A clears boundary corruption → PD6/LE timing coincidence was
    the mechanism (theory b or c, weak form).
  - Variant A unchanged, Variant B clears → LE-rise edge itself was load-
    bearing (theory c).
  - Both unchanged → fix #2 required; refines diagnosis away from PD6-
    timing-alone toward latch-or-host-state-machine root cause.
  - Byte 0 self-read symptom may resolve independently with either variant
    if it shares the primary mechanism; otherwise survives as a separate
    open follow-up.

- timestamp: 2026-05-13T13:05:00Z
  observation: `firestarter info FM1608` shows correct pinout/algorithm (SRAM 28-pin, 8K, vcc=5V, pin 27=R/W, pin 1+26=NC, algorithm 0x28).

- timestamp: 2026-05-13T13:08:00Z
  observation: `firestarter write FM1608 /tmp/fm1608_test.bin` (8192-byte pseudo-random pattern, md5 `864948b8…`) reports "Write successful (1.75s)". `firestarter read` reports "Read complete (1.85s)" (md5 `1348c9e9…`). `cmp` shows exactly 1 byte differs: byte 0 expected `0x37` (octal 67), got `0xFF` (octal 377). Bytes 1..8191 match source.

- timestamp: 2026-05-13T13:12:00Z
  observation: Uniform-pattern probes (0x00, 0xAA, 0x55, 0x5A) all show byte 0 readback = `0xFF`, bytes 1+ correctly reflect each pattern. `od -An -tx1 -N8` outputs after each write:
  - 0x00 write → `ff 00 00 00 00 00 00 00`
  - 0xAA write → `ff aa aa aa aa aa aa aa`
  - 0x55 write → `ff 55 55 55 55 55 55 55`

- timestamp: 2026-05-13T13:14:00Z
  observation: Single-byte `firestarter write FM1608 /tmp/oneByte.bin -a 0` (0x55 to address 0) followed by full read: byte 0 = `0xFF`, bytes 1..8191 unchanged from prior write. Same command with `-a 1`: byte 1 successfully updates to 0x55. **Bug is address-0-specific.**

- timestamp: 2026-05-13T13:16:00Z
  observation: Three consecutive reads after a single AA/55-alternating write produce three byte-identical files (`b44e655e…` ×3) with byte 0 = `0xFF`, bytes 1..7 = `55 aa 55 aa 55 aa 55`. Reads are non-destructive and deterministic.

- timestamp: 2026-05-13T13:20:00Z
  observation: Full-chip 0x00 write followed by single-byte 0x55 write at addr 0: byte 0 reads back `0xFF` (not 0x00 and not 0x55) — both writes failed to update byte 0. Bytes 1..3 read 0x00 (full-chip write took for those). Confirms address 0 is the failing location across every code path that targets it.

- timestamp: 2026-05-13T13:24:00Z
  observation: Verbose write log shows `INIT: Done` and `END: Done` housekeeping (callbacks NULL for SRAM, so phases are no-ops but ACK handshakes complete). Host sends `flags: 128` (FLAG_VERBOSE) only when `-v` is set; without `-v`, flags=0 — bug reproduces in both modes.

- timestamp: 2026-05-13T (post-summary, Leonardo cross-board test)
  observation: **Bug is Uno-specific.** Same firmware source built for Leonardo (`pio run -e leonardo`, no `SERIAL_ON_IO`), same FM1608 chip moved to Leonardo's shield, same host stack (`firestarter_app` feature branch with parser fix). Write+read of the 8KB pseudo-random pattern (byte 0 = 0x37) round-trips with md5 `3be9273180b70a0a1a2b47802a832c60` matching the input — zero mismatches, byte 0 correct. Bug does NOT manifest on Leonardo. Earlier Leonardo "test" before this was invalid (IC was out — coherent-looking pattern was bus/crosstalk artifact, not real data).

- timestamp: 2026-05-13T (Uno firmware-fix attempts, all failed)
  observation: Bench-tested six firmware fixes on Uno, none resolved byte-0=0xff:
    1. `rurp_invalidate_register_cache()` in `rurp_set_programmer_mode()` — REGRESSION: corrupted `mem_util_calculate_top_address_register` because it reads cached CTL & ORs with VPP/REGULATOR mask bits. 6144/8192 mismatches.
    2. `PORTD=0` before `DDRD=0` in `rurp_set_data_input()` (Uno only) — eliminated pullup bias. Did not fix byte 0 but is kept as defensive robustness improvement.
    3. Warmup read at `handle->address` (Uno-only) — first chip-enable absorbed; byte 0 still 0xff.
    4. Warmup read at `handle->address + 1` (forces both LSB+MSB strobes before real byte-0 read) — byte 0 still 0xff.
    5. `delay(5)` removed from `rurp_serial_end()` — byte 0 still 0xff.
    6. `UCSR0B = 0` after Serial.end (force-clear all UART enable bits) — byte 0 still 0xff.
    7. Longer access delay (`delayMicroseconds(10)` post-CE, `delayMicroseconds(2)` pre-CE setup) — byte 0 still 0xff.
    8. Duplicate first-byte write in `memory_write_execute` (Uno-only) to wake chip out of standby — byte 0 still 0xff.
  All experimental changes reverted except #2 (kept as defensive).
  Key insight: EPROM byte-0 read on Uno succeeds with FEWER strobe events than FM1608 byte-0 (EPROM = 0 strobes from all cache hits; FM1608 = 1 strobe because `rw_line=14` sets MSB bit 6 for read mode). So strobe-related theories are weakened. The unique FM1608 vs EPROM difference is the R/W line transition (LOW→HIGH on first read) — but timing analysis shows >>setup-time margin.

## Eliminated

- **Chip damage** (prior diagnosis): falsified — fresh chip behaves identically.
- **Wrong pinout / dispatch routing**: falsified — `firestarter info` and JSON command both show correct SRAM dispatch on `DIP28_JEDEC_SRAM_8K`. Bytes 1..8191 round-trip perfectly, proving address bus + data bus + /WE + /OE + /CE timing all work for non-zero addresses.
- **Host-side parser/garbage**: falsified — host parser fix `firestarter_app@24f4fa4` is in place; commands and ACK exchanges shown in verbose log are clean.
- **Blank check or erase interference**: falsified — `firestarter write -b` (no blank check) shows the same symptom.
- **Read-side leakage / address-bus crosstalk** (the `(addr & 0xFC) | 0x03` pattern from prior wrong-pinout): not reproducible here — reads return correct content for bytes 1..N and consistent `0xFF` for byte 0 across repeated reads. The crosstalk symptom required the *wrong* pinout (DIP28_2764) and is fixed in current config.

## Diagnosis (provisional, remediation pending)

- root_cause: **Uno-specific hardware-level coupling between PORTD bit 6 (chip data pin D6) and chip CE.** Decisive evidence from cross-board chip-state read: after Uno wrote the 8 KB pseudo-random pattern and Leonardo read the chip WITHOUT rewriting, exactly 32 bytes were corrupted — every byte at a 256-byte boundary (`chip[i*256]` for i=0..31) held value `0x40 | i`, the exact PORTD value the Uno firmware drove during the MSB strobe for the corresponding READ. The hardware reference (`04-HARDWARE-REFERENCE.md:16`) confirms: "All three latches share Arduino PORTD as the D-input bus" — i.e., PORTD bits 0-7 are simultaneously the latch D-inputs AND the chip's data bus pins. When MSB is strobed with `0x4X` during a read (cache miss on MSB transition every 256 bytes; the 0x40 bit is the `rw_line=14` set for read mode), AVR drives PORTD bit 6 HIGH, which goes to the latch's D6 input AND to the chip's data pin D6. Driving D6 HIGH during the strobe LE pulse evidently couples (capacitively or via shared substrate) to the chip's CE line, briefly pulling CE LOW long enough for the chip to capture the data bus value (0x4X) at the address held by the LSB latch (= the byte's offset within the chunk). Writes are unaffected because MSB strobes during writes have bit 6 = 0 (rw_line bit not set for WRITE_FLAG=0), so no PD6 HIGH transition, no coupling event. Leonardo is unaffected because its data bus is split across PORTD/PORTC/PORTE on non-contiguous bits — PD6 is NOT the chip's D6 line.
- secondary_effect: The "byte 0 = 0xff" symptom Uno self-reads layers a second Uno-only bug on top: Uno's read of address 0 specifically returns `0xff` regardless of the chip's actual stored byte. The chip held `0x40` after the corruption (confirmed by Leonardo cross-read), but Uno reads `0xff`. Mechanism for this secondary read-side bug remains unknown after 8 firmware-level fix attempts (cache invalidation, PORTD=0 input transition, warmup reads, Serial.end delay removal, UCSR0B force-clear, longer access/setup delays, duplicate-write). Both bugs require Uno's PORTD-shared-with-data-bus to manifest. Hypothesis worth re-testing under fix #1/#2: byte-0 specifically is the first read where MSB transitions `0x00 → 0x40`, which is the **largest** PD6-rising edge in any session — i.e., the secondary bug may be the same coupling mechanism, amplified, and could collapse into the primary fix.
- files_changed_so_far: only defensive PORTD=0 before DDRD=0 in `rurp_set_data_input()` (Uno) kept. All other experimental fixes reverted.

## Constraint

**Uno and Leonardo are both first-class operator boards** ([[feedback-board-parity]]). The end-user chooses which board runs the shield; the project does not assign chips to boards. Any acceptable resolution must restore correct FM1608 (and 5V-SRAM/FRAM with `rw-pin=27`) behaviour on Uno. The prior recommendation to "document FM1608 as Leonardo-only" is withdrawn.

## Next experiments (Uno fix paths)

Listed cheapest → most invasive. Stop as soon as one fixes both the 256-byte-boundary corruption AND the byte-0 stuck-at-`0xFF` read, verified by Uno-only write+read+verify round-trip on a fresh FM1608.

1. **Coupling-aware MSB strobe sequence on Uno** (cheapest, firmware-only, no host/protocol change).
   - In `rurp_write_to_register` for the MSB latch on Uno: before driving the new MSB value on PORTD and pulsing LE, first set `PORTD = 0` (force PD6 LOW), small NOP/delay, then write the target value, then strobe LE, then optionally return PORTD to a neutral state.
   - Goal: shrink or invert the PD6 rising edge during the strobe window so the capacitive kick to CE no longer crosses the chip's CE-LOW threshold.
   - Expected outcome if it works: 256-byte-boundary corruption disappears; byte 0 read may also self-resolve (see secondary_effect hypothesis).
   - Test plan: full 8 KB pseudo-random round-trip on Uno + `firestarter verify`. Cross-read with Leonardo to confirm chip contents match source (i.e., write side also clean — should already be, but verify).
   - Risk: changes a hot path in the latch strobe; must not regress non-FM1608 chips on Uno or any chip on Leonardo (guard with `#ifdef ARDUINO_AVR_UNO` or equivalent).

2. **Move R/W routing off MSB bit 6** (more invasive, host + firmware + possibly shield wiring).
   - Option 2a: Route `rw-pin` via the **CTL** register instead of MSB. Requires host-side `bus-config` extension to declare `rw-pin` in CTL space, and firmware support for the new routing. Sidesteps PD6-during-MSB-strobe entirely.
   - Option 2b: Pick a different MSB bit (not bit 6) for the R/W signal on pinouts that currently use bit 14. Requires shield-wiring check to see whether any other MSB bit is free and physically routed to chip pin 27 — likely needs a hardware mod, so deprioritized vs 2a.
   - Test plan: full 8 KB round-trip on Uno AND Leonardo (regression check) on FM1608, plus a regression sweep on at least one EPROM and one EEPROM that also use the MSB latch heavily.
   - Defer until #1 is proven insufficient — #1 is much smaller and reversible.

3. **Re-evaluate the byte-0 secondary bug under whichever fix lands.**
   - If #1 or #2 resolves the 256-byte-boundary corruption but byte 0 still reads `0xFF`, re-open the secondary investigation with a clean baseline (no boundary corruption confounding the readback). New experiments would target the byte-0-specific `MSB: 0x00 → 0x40` transition, possibly with a pre-read at `address=1` after fix #1 is in place to compare strobe behaviour.

4. **Hardware mod as last resort** (only if #1, #2a, #2b all fail).
   - Small ceramic cap or series resistor on CE to absorb the coupling glitch. Document as optional shield rev. Never as a precondition for Uno support — must be paired with a firmware fix path that also works on un-modded shields, or shipped as a shield revision the project formally adopts.

## Follow-ups (documentation + cross-chip)

- Update `04-HW-VALIDATION.md` to document the PORTD-bit-6 ↔ CE coupling root cause and link this debug session. **Do NOT** include any "use Leonardo for FRAM" recommendation.
- Cross-reference with other chips that have `rw-pin=27` or otherwise route R/W via MSB bit 6 (e.g., 6116 family, 28C256 EEPROMs) — verify whether they exhibit the same Uno-only corruption pattern. They almost certainly do, and the fix from #1/#2 should resolve them as a class.
- Optional bench task: scope-probe CE during an MSB strobe to confirm/quantify the glitch before vs after fix #1. Not blocking — outcome of fix #1 is itself diagnostic.

---

## 2026-05-18 Investigation extension — bug localized to specific Uno board

Picked up from "PD6 coupling theory" status. Goal: identify the firmware-side or hardware-side root cause of the remaining "byte 0 reads `0xFF`" failure that the pre-clear (`firestarter@fdfed03`) did not resolve.

### New observations

1. **`-a <nonzero>` partial-read bug is host-side, NOT Uno-specific.** Both Uno and Leonardo return zero-padded files (`size = addr + s`) when the host CLI is invoked with `-a <nonzero>`. Unrelated to byte-0 bug. (Captured but not chased.)

2. **`read FM1608 -a 0 -s 1` (isolated single-byte read) reproduces the bug.** Not cumulative state from a prior 8 KB read sequence — the very first byte-0 access after `configure_memory` already fails.

3. **NOT a per-chunk-of-`DATA_BUFFER_SIZE` issue.** A 1 KB read (2 chunks of 512) on Uno returns 1 diff, not 2. The bug fires once per read command at chip-address 0 only. Verified explicitly 2026-05-18.

4. **Pattern-independent.** Write byte 0 = `0x4F` → reads `0xFF`. Write byte 0 = `0x00` → reads `0xFF`. Write byte 0 = `0xFF` → reads `0xFF`. The Uno's byte-0 read returns `0xFF` regardless of chip content.

### Cross-tests that localized the bug to the Uno board

| Configuration | Diffs at byte 0 |
|---|---|
| Uno board + Uno's shield + chip-X | `0xFF` (bug) |
| Uno board + Leo's shield + chip-X | `0xFF` (bug — followed Uno board) |
| Leo board + Leo's shield + chip-X | clean ✓ |
| Leo board + Uno's shield + chip-Y | clean ✓ |

After chip + shield swaps: **the bug follows the Uno board only.** Both FM1608 chips and both RURP shields produce clean reads on the Leonardo. The chip is healthy, the shield is healthy.

### Firmware fix attempts (this round)

All targeted at the remaining byte-0 failure, layered on top of the existing pre-clear:

| Attempt | Firmware ID | Result |
|---|---|---|
| Post-clear `PORTD = 0` immediately after MSB-strobe LE drops (shrink PD6-HIGH window to just the strobe pulse) | working tree at start | No effect on byte 0 |
| Robust-read fallback: hold `/CE` LOW for an additional 100 µs and re-sample, then a 2nd `/CE` cycle | `2.0.13` | No effect — all retries return `0xFF` |
| Invalidate LSB latch cache for byte-0 reads to force the strobe (cache-hit had been skipping the LSB strobe at address 0) | `2.0.14` | No effect on byte 0 |

The robust-read result is the strongest negative finding — holding `/CE` LOW for 100 µs **and** doing a second `/CE` cycle does not coax the chip into driving the bus. Either `/CE` isn't actually going LOW at the chip's pin, the chip never enters its read-output state at address 0 on this Uno, or the AVR's PIND is reading something other than the chip's drive.

### Theories falsified by this round

- **"Chip needs longer access time"** — falsified (100 µs no help)
- **"Chip needs a second `/CE` cycle to wake up"** — falsified
- **"Stale LSB latch state"** — falsified (forced strobe via cache invalidation)
- **"Bug fires once per `DATA_BUFFER_SIZE` chunk"** — falsified (1 diff in 16 chunks)

### Hypothesis carried forward

Given:
- Bug is reproducible on this specific Uno board only, across both shields and both chips
- All firmware-level fixes have failed
- The chip is not driving the bus when commanded (all paths return `0xFF`)
- Bytes 1..N read correctly on the same Uno — so `/CE`, `/OE`, R/W, address-bus, and data-bus PIND sampling all work for those accesses

The most likely remaining cause is **hardware damage on this specific Uno board** — most plausibly a marginal contact, ESD damage, or fault on PB5 (`/CE` / D13 / SCK) or on one of PORTD's lines. The fault manifests only when the data bus has just been driven all-LOW (the unique byte-0 state) and not when at least one PORTD bit is HIGH (every other address).

### Cheapest unblocking experiment (when bench access returns)

**Test on a different Uno R3 board.** Keep the same chip + same shield. If byte 0 reads correctly on a different Uno, the bug is hardware on this specific Uno (ship as-is with operator note). If it also fails on a different Uno, there's still a firmware bug we haven't found — re-open with bench scope on PB5.

### Working-tree state at park (2026-05-18)

- `firestarter/src/proms/memory.cpp` — clean (LSB cache invalidation reverted)
- `firestarter/include/rurp_register_utils.h` — pre-clear + post-clear for MSB strobe **kept** (these are real improvements regardless of byte-0 status; fixed the 32-of-33 boundary corruptions)
- `firestarter/include/version.h` — reverted to `2.0.11-dev`
- `firestarter/platformio.ini` — operator's `DATA_BUFFER_SIZE=512` Leonardo A/B-test override left in place (operator-managed)

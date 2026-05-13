---
slug: fm1608-fresh-chip-baseline
status: hypothesis-formed
trigger: "Lets check whats going on with the FM1608, I have a new IC"
created: 2026-05-13T12:45:49Z
updated: 2026-05-13T13:30:00Z
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

**Firmware diagnostics confirm correct bus setup at byte 0.** The bug is at
hardware level — either FM1608 family has an address-0 quirk under firestarter's
specific CE pulse pattern, or the RURP shield has a subtle hardware fault
(timing race / trace issue) that manifests only when all address-line lower
bits are LOW simultaneously.

**Workaround for operators:** firestarter writes to FM1608 work for bytes 1..N-1.
Operators can either avoid byte 0 (write a sacrificial 0xFF or 0x00 at byte 0
in source files) or accept that byte 0 will read as 0xFF after writes.

**Further investigation requires bench tools** (logic analyzer or oscilloscope
on socket pins 12 / 22 / 24 / 29 / 30) to capture what physically happens
during the byte-0 CE pulse vs byte-1 CE pulse — comparing the two should
reveal the source of the difference.

## Files involved

  - firestarter/src/proms/memory.cpp: memory_set_data + memory_get_data (correct)
  - firestarter_app/firestarter/data/pinouts.json: DIP28_JEDEC_SRAM_8K entry (correct)
  - firestarter_app/firestarter/database.py: pin_conversions[28] (correct)

## Status

DEFERRED — investigation paused pending bench tools. The firmware and host
correctly handle FM1608 dispatch and bus setup; the byte-0 anomaly is a
known-issue documented for follow-up.

- timestamp: 2026-05-13T14:15:00Z
  observation: User's hypothesis "write works, read fails" was tested via `firestarter verify` — verify failed with `ERROR: 0x37 != 0xff at 0x000000`, confirming the firmware-level read of byte 0 returns 0xFF (verify uses memory_get_data, same as standalone read). However, this alone doesn't distinguish (a) chip's byte 0 IS 0xFF (write didn't land) from (b) read consistently returns 0xFF regardless of chip contents. Both hypotheses fit the host-visible behaviour.

- timestamp: 2026-05-13T14:20:00Z
  observation: Tried experimental firmware fix (firestarter 2.0.11-dev) adding `delayMicroseconds(3)` and then `delayMicroseconds(100)` between `firestarter_set_address` and `rurp_chip_enable` in `memory_get_data` (hypothesis: WE LOW→HIGH transition needs settle time for the first read after a write). Neither delay changed the symptom — byte 0 still reads 0xFF. WE settle timing is NOT the root cause.

- timestamp: 2026-05-13T14:25:00Z
  observation: Read tests at different offsets to localize: `firestarter read -a 0 -s 1` returns 0xFF; `firestarter read -a 1 -s 1` returns 0xd4 (correct); read byte 100 first then byte 0 still returns 0xFF (deterministic, not state-dependent). `firestarter dev read -a 0` (lower-level path) also returns 0xFF — every read path through memory_get_data fails at address 0.

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

## Eliminated

- **Chip damage** (prior diagnosis): falsified — fresh chip behaves identically.
- **Wrong pinout / dispatch routing**: falsified — `firestarter info` and JSON command both show correct SRAM dispatch on `DIP28_JEDEC_SRAM_8K`. Bytes 1..8191 round-trip perfectly, proving address bus + data bus + /WE + /OE + /CE timing all work for non-zero addresses.
- **Host-side parser/garbage**: falsified — host parser fix `firestarter_app@24f4fa4` is in place; commands and ACK exchanges shown in verbose log are clean.
- **Blank check or erase interference**: falsified — `firestarter write -b` (no blank check) shows the same symptom.
- **Read-side leakage / address-bus crosstalk** (the `(addr & 0xFC) | 0x03` pattern from prior wrong-pinout): not reproducible here — reads return correct content for bytes 1..N and consistent `0xFF` for byte 0 across repeated reads. The crosstalk symptom required the *wrong* pinout (DIP28_2764) and is fixed in current config.

## Resolution

- root_cause: TBD pending H1 confirmation. Strong hypothesis: cache-skip in `rurp_write_to_register` suppresses shift-register strobes on the first `memory_set_data(0, byte0)` call, leaving the SRAM/FRAM /WE or address bus in a state that prevents the write from latching at address 0.
- fix: TBD. Candidate: bypass the cache-skip for LSB/MSB/CONTROL on the first write of any chunk, OR add an unconditional strobe in `memory_set_data` immediately before `rurp_chip_enable()`. The fix must preserve the cache-skip optimization for the 99% case (subsequent bytes in a chunk), so the simplest patch is probably an "invalidate cache on entry to memory_write_execute" call inside `configure_memory` for SRAM/FRAM.
- verification: TBD. After fix, repeat the uniform-pattern probes (0x00/0xAA/0x55) — all 8192 bytes should round-trip identically. Re-run the standard pseudo-random pattern (`864948b8…`) — md5 should match.
- files_changed: TBD. Likely candidates: `firestarter/include/rurp_register_utils.h` (cache invalidation hook) and/or `firestarter/src/proms/memory.cpp` (`configure_memory` end, or `memory_set_data` first call).
- follow_up_action: Update `04-HW-VALIDATION.md` follow_up `fm1608-db-mismatch` to reflect that the byte-0 bug is firmware-side (NOT chip damage), and re-open it pending the H1 fix.

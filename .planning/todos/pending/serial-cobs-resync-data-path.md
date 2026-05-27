---
id: serial-cobs-resync-data-path
title: Evaluate COBS framing/resync on the serial data path (PacketSerial assessed, not adopted)
captured: 2026-05-27
status: pending
type: enhancement
target_milestone: v1.8+
priority: low
related_phase: null
resolves_phase: null
---

# COBS framing/resync on the serial data path

## The idea

Borrow **COBS-style automatic resync into the existing length-prefixed data-block
path** — do NOT adopt the PacketSerial library wholesale. The goal is a single
robustness win: a garbled byte should corrupt only one packet and re-sync on the
next delimiter, instead of desyncing the stream until the 2 s timeout fires.

Keep the existing CRC8-CCITT integrity layer on top; PacketSerial has no checksum.

## Investigation summary (2026-05-27)

Spawned from a `/gsd-fast` investigation: "what improvements and what cost would a
lib like PacketSerial bring to the firmware." Conclusion: **not worth a drop-in.**

### What the firmware does on the wire today (4 framings, one 250000-baud line)

| Direction | Where | Framing |
|---|---|---|
| host→fw commands | `firestarter/src/firestarter.cpp:162-172` | ASCII JSON, peek for `{`, discard junk |
| host→fw data block | `firestarter/src/boards/rurp_serial_utils.cpp:44-79` | `[len_u16][xor][payload]`, 2 s timeout |
| fw→host data block | `firestarter/src/boards/rurp_serial_utils.cpp:81-93` | same `[len_u16][xor][payload]` |
| fw→host log/telemetry | `firestarter/src/boards/rurp_serial_utils.cpp:138-184` | `[0xAA55AA55][len_u16][id][params][crc8][0x0A]` |

The host decoder at `firestarter_app/firestarter/serial_comm.py:546-660` demuxes all
of these on one stream and is **byte-for-byte synced** with the firmware (magic
preamble, CRC8 table, length semantics). A native test suite (`test_messages`) pins
the frame contract. Root CLAUDE.md mandates these two files change in lockstep.

### What PacketSerial (COBS) would improve
1. One framing instead of four — `0x00` delimiter is unambiguous, no magic preamble / length prefix needed.
2. **Automatic resync** (the genuinely valuable benefit). Today the length-prefixed data path has no resync — a corrupted length byte desyncs until timeout.
3. Callback-driven receive replaces the manual peek/read/timeout loop.

### Why a drop-in is NOT worth it
- **RAM is the blocker (Uno).** Current `pio run -e uno` baseline: **RAM 73.0% = 1495/2048, only 553 bytes free**; Flash 68.6% (22122/32256, ~10 KB free). The handle already owns `char data_buffer[512]` (`firestarter/include/firestarter.h:87`). PacketSerial's `send()` builds a **fully COBS-encoded copy** (~`n + n/254 + 2` ≈ 516 bytes for a 512-byte chunk) before writing, plus its own RX buffer. A second ~512-byte buffer does not fit in 553 free bytes → stack/globals collision → crash. You'd have to write a streaming/in-place COBS encoder anyway, at which point you're not really using the library.
- **Flash is fine** (~1–2 KB for COBS+lib vs ~10 KB free) — not the constraint.
- **Coordinated dual-repo rewrite** of `rurp_serial_utils.cpp` + `serial_comm.py` + the `test_messages` contract. Milestone-sized, not fast-sized.
- **Bench re-validation** required against the Uno `SERIAL_ON_IO` bus-aliasing problem — the magic preamble exists precisely because the UART shares PORTD with the data/address bus. Must prove `0x00` delimiter collisions with bus-driven `0x00` bytes don't create false frame boundaries.

## Does NOT fix v1.8 Bug A / Bug B

Important: the v1.8 RCA seed characterizes Bug A (Modified Rev 0 upper-address
jitter, A15=1 → 1.86× skew) and Bug B (Rev 2.0 /CE-or-/OE timing + VPP=13.1V) as
**hardware** faults, not framing faults. COBS/PacketSerial would not fix either.
This is an independent protocol-quality item — do not fold it into the Bug A/B hunt
as a candidate fix. (See memory `project-v18-rca-seed-bug-a-bug-b`.)

## Recommended path (for whoever picks this up)
1. **Preferred:** add a streaming/in-place COBS encode+decode to the data-block path
   only (host→fw and fw→host in `rurp_serial_utils.cpp`), keep CRC8, no second
   512-byte buffer. Captures the resync benefit at low RAM cost.
2. **Alternative:** if the full PacketSerial library is ever wanted, scope it to
   **Leonardo only** (ATmega32u4: 2560 B RAM, native USB-CDC, no PORTD aliasing) and
   leave the Uno on current framing — but a board-split protocol adds its own
   maintenance burden and a second test contract.

## Open questions
- Is the 2 s-timeout desync actually observed in the field, or only theoretical? If it never bites, priority stays low.
- Does the host `serial_comm.py` demux already recover gracefully enough that COBS adds little? Measure before investing.
- uno328pb shares the Uno's 2048 B RAM ceiling — same constraint as Uno.

## Cross-references
- `firestarter/src/boards/rurp_serial_utils.cpp:44-93` (data block) + `:138-184` (log frames)
- `firestarter/src/firestarter.cpp:113` (`init_programmer` read) + `:162-172` (command peek loop)
- `firestarter_app/firestarter/serial_comm.py:546-660` (host stream demux) + `:967-983` (data-block checksum read)
- `firestarter/include/firestarter.h:87` (`data_buffer[512]`)
- Root `CLAUDE.md`: serial protocol must stay in sync across `serial_comm.py` ↔ `firestarter.cpp`
- Memory `project-v18-rca-seed-bug-a-bug-b`: confirms Bug A/B are hardware, not framing

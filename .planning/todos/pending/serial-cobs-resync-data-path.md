---
id: serial-cobs-resync-data-path
title: Evaluate COBS framing/resync on the serial data path (PacketSerial assessed, not adopted)
captured: 2026-05-27
status: pending
type: enhancement
target_milestone: v1.9
priority: low
related_phase: 48
resolves_phase: 48
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

## Existing implementations surveyed (2026-05-27 refinement)

Follow-up question: "what implementations already exist and which is the best match?"
The survey surfaced a constraint the first pass missed (see CRUX below), then narrowed
the field.

### CRUX — "in-place COBS" and "512 B single frame" are mutually exclusive
COBS must write its output (~`payload + payload/254 + 1` bytes) somewhere. The ONLY
way to avoid a second buffer is **in-place** encoding, and in-place COBS is
mathematically capped at **254-byte runs** (nanocobs' `cobs_encode_tinyframe`
enforces exactly `< 254`). For larger payloads, every COBS lib (nanocobs standard
mode, cobs-c, PacketSerial, COBS-CPP) encodes into a **separate `COBS_ENCODE_MAX(n)`
destination buffer** (~514 B for a 512 B frame).

Uno RAM math: 2048 − 1495 used = **553 B free**, and the 512 B `data_buffer` is
already inside that 1495. A ~514 B COBS dst buffer → ~2009 B used → ~39 B stack left
→ crash. **So on the Uno, no off-the-shelf COBS encoder fits a 512 B single frame.**
(Decode/receive side is fine — in-place decode into `data_buffer` works. It's the
fw→host *encode* path that hits the wall.) This means the prior "streaming/in-place
COBS" phrasing was conflating two incompatible things; the real options are below.

### Candidates scored against our filters (≤512 B frame, 553 B free RAM, reuse CRC8, dual-repo)
| Implementation | Lang pair | CRC built in | 512 B frame on Uno? | Verdict |
|---|---|---|---|---|
| nanocobs (charlesnicholson) | C99 only | no | in-place ≤254 B; std mode needs 2nd buffer | Best embedded C codec, zero-malloc/zero-libc — but ≤254 to stay buffer-free |
| cobs-c + cobs-python (cmcqueen) | **C + Python, same author** | no | needs 2nd buffer → ✗ on Uno | Best host codec; matched pair = byte-identical COBS |
| PacketSerial (bakercp) | C++ only | no | full encoded copy → ✗ on Uno | Rejected (RAM) |
| SerialTransfer + pySerialTransfer (PowerBroker2) | **C++ + Python, same author** | **yes, CRC8 poly 0x9B** | payload capped 1–254 B by design | Turnkey; caps at 254, swaps our CRC poly, replaces ALL framing |
| MIN protocol (min + min-python) | C + Python | yes (CRC32) | 255 B/frame; transport buffers | Overkill + RAM heavy |
| PatrickBaus/COBS-CPP | C++ only | no | separate buffer → ✗ on Uno | Honorable mention |

Two filters do the eliminating: single-byte length fields cap SerialTransfer + MIN at
~254 B, and non-in-place encoders blow the Uno RAM budget at 512 B. Both push to the
same place: **on the Uno, frames effectively must be ≤254 B regardless of library.**

## Recommended path (for whoever picks this up)

**Preferred — codec-only, reuse our CRC8:** `nanocobs` (firmware, `tinyframe` in-place,
≤254 B) + `cobs-python` `cobs.cobs` (host), keeping the existing CRC8-CCITT (poly 0x07)
and u16-length header. Re-chunk the data path from one 512 B frame into ≤254 B COBS
frames (the `eprom_operations.py` loop already chunks; this just shrinks the unit).
- nanocobs = one `cobs.c`/`cobs.h`, C99, no malloc, no libc → drops into PlatformIO.
- Use `cobs.cobs` (plain), **NOT** `cobs.cobsr` (COBS/R variant) — must match nanocobs' plain COBS byte-for-byte.
- Keep CRC8-CCITT; both repos already implement + unit-test it (`test_messages`).

**Runner-up — turnkey:** `SerialTransfer` + `pySerialTransfer` — a matched C++/Python
pair with COBS + CRC8 + callbacks already wired; its 254 B cap is moot once we chunk.
Cost: replaces ALL framing (incl. the JSON command path), swaps CRC8-CCITT for poly
0x9B, rewrites the `test_messages` contract wholesale → larger dual-repo diff.

**If 512 B single frames MUST stay** (no re-chunk): no existing library fits the Uno →
write a custom streaming COBS encoder (nanocobs' incremental `cobs_encode_inc_begin/
inc/inc_end` is the closest reusable building block), or scope COBS to **Leonardo only**
(ATmega32u4: 2560 B RAM, native USB-CDC, no PORTD aliasing) and leave Uno on current framing.

## The decisive decision (pick before implementing)
**Are we willing to re-chunk the data path to ≤254-byte frames?**
- Yes, minimal diff + reuse CRC8 → **nanocobs + cobs-python**.
- Yes, prefer batteries-included → **SerialTransfer / pySerialTransfer**.
- No, keep 512 B single frames → custom streaming encoder, or Leonardo-only COBS.

## Open questions
- Is the 2 s-timeout desync actually observed in the field, or only theoretical? If it never bites, priority stays low.
- Does the host `serial_comm.py` demux already recover gracefully enough that COBS adds little? Measure before investing.
- uno328pb shares the Uno's 2048 B RAM ceiling — same constraint as Uno.
- Per-frame overhead of ≤254 B chunking (extra CRC + delimiter per chunk) on a 512/1024 B block — quantify vs the current single-frame cost.

## Cross-references
- `firestarter/src/boards/rurp_serial_utils.cpp:44-93` (data block) + `:138-184` (log frames)
- `firestarter/src/firestarter.cpp:113` (`init_programmer` read) + `:162-172` (command peek loop)
- `firestarter_app/firestarter/serial_comm.py:546-660` (host stream demux) + `:967-983` (data-block checksum read)
- `firestarter/include/firestarter.h:87` (`data_buffer[512]`)
- Root `CLAUDE.md`: serial protocol must stay in sync across `serial_comm.py` ↔ `firestarter.cpp`
- Memory `project-v18-rca-seed-bug-a-bug-b`: confirms Bug A/B are hardware, not framing

## Surveyed implementations (links)
- nanocobs (C99, in-place, no malloc): https://github.com/charlesnicholson/nanocobs
- cobs-python (PyPI `cobs`, use `cobs.cobs` plain): https://github.com/cmcqueen/cobs-python · https://pypi.org/project/cobs/
- cobs-c (matched-author C codec): https://github.com/cmcqueen/cobs-c
- SerialTransfer (Arduino, COBS+CRC8 poly 0x9B, ≤254 B): https://github.com/PowerBroker2/SerialTransfer
- pySerialTransfer (matching Python): https://github.com/PowerBroker2/pySerialTransfer · https://pypi.org/project/pySerialTransfer/
- COBS/R variant caveat (do NOT use for cross-impl compat): https://pythonhosted.org/cobs/cobsr-intro.html

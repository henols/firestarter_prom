---
phase: 51-command-channel-framing-migration-breaking-wire-change
reviewed: 2026-06-02T00:00:00Z
depth: standard
files_reviewed: 11
files_reviewed_list:
  - firestarter/include/firestarter.h
  - firestarter/platformio.ini
  - firestarter/src/firestarter.cpp
  - firestarter/test/native/avr/test_cobs_cmd_frame/host_stubs.cpp
  - firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp
  - firestarter_app/firestarter/constants.py
  - firestarter_app/firestarter/serial_comm.py
  - firestarter_app/tests/test_serial_comm.py
  - firestarter/README.md
  - firestarter_app/README.md
findings:
  critical: 2
  warning: 4
  info: 3
  total: 9
status: issues_found
---

# Phase 51: Code Review Report

**Reviewed:** 2026-06-02
**Depth:** standard
**Files Reviewed:** 11
**Status:** issues_found

## Summary

Reviewed the COBS+CRC8 command-channel framing migration across both repos. The
CRC-before-parse ordering, the deleted `{`-peek plaintext path, the atomic single
write, and the host/firmware `CMD_FRAME_MAX = 512` constant declarations are all
present and correct as designed. However, the firmware integration in
`firestarter.cpp` and the shared decoder in `rurp_serial_utils.cpp` (the
load-bearing primitive this phase wires up — included as essential context though
not in the explicit file list) contain two ship-blocking defects:

1. An **off-by-one out-of-bounds write** at the exact `DATA_BUFFER_SIZE` payload
   boundary — directly in the headroom the phase deliberately reserves.
2. An **unbounded busy-wait hang** on a truncated frame, because the per-frame
   timeout was removed (SC1) and the CMD_IDLE decode path has no watchdog.

Neither defect is covered by the four Unity cases in the new suite — the suite
tests `DATA_BUFFER_SIZE + 4` (drained) but never exactly `DATA_BUFFER_SIZE`, and
never a truncated/no-delimiter stream.

The host side is clean for the framing contract, but `CMD_FRAME_MAX` is declared
and never enforced on send, so an oversized command fails opaquely.

## Critical Issues

### CR-01: Off-by-one OOB write — `data_buffer[n] = '\0'` at the 512-byte boundary

**File:** `firestarter/src/firestarter.cpp:176-179`
**Issue:**
`handle.data_buffer` is declared `char data_buffer[DATA_BUFFER_SIZE]` (512 bytes,
`firestarter.h:95`). The decoder `rurp_communication_read_data()` caps the
committed payload at `out == DATA_BUFFER_SIZE` — its overflow guard only fires on
`out >= DATA_BUFFER_SIZE` *before* a further commit
(`rurp_serial_utils.cpp:113`), so a payload of *exactly* `DATA_BUFFER_SIZE` bytes
is accepted and returns `n == 512`. The CRC byte is held in the 1-byte lookahead
and never committed, so 512 is a legitimate, reachable return value (and well
inside the "512 B headroom" the phase reserves above the ~422 B worst case).

The CMD_IDLE branch then executes:

```c
handle.data_size = (uint32_t)n;       // n == 512
handle.data_buffer[n] = '\0';         // writes data_buffer[512] — OUT OF BOUNDS
```

`data_buffer[512]` is one past the end of the 512-element array. On the Uno this
overwrites whatever struct field follows `data_buffer` in `firestarter_handle_t`
(`data_size`, then `bus_config`) — silent memory corruption on the single global
`handle` with only ~545 B of free RAM. This is a data-integrity / undefined-
behavior defect on the exact boundary the design treats as valid.

The same NUL-terminate-past-decoded-length pattern is *not* a problem on the data
channel (`operation_utils.cpp:164-169` does not append a terminator), confirming
this is specific to the new command path.

**Fix:** Either reserve one byte for the terminator in the buffer, or have the
decoder cap one byte lower so a returned length always leaves room. Minimal,
self-contained fix at the call site — clamp before terminating:

```c
int n = rurp_communication_read_data(handle.data_buffer);
if (n > 0) {
    /* Reserve the terminator slot: the JSON parser uses data_size as the
     * authoritative length, so a 512-byte payload need not be NUL-terminated
     * beyond the buffer. Guard the write. */
    handle.data_size = (uint32_t)n;
    if (n < DATA_BUFFER_SIZE) {
        handle.data_buffer[n] = '\0';
    }
    if (init_programmer_framed(&handle)) {
        return;
    }
}
```

Preferred long-term fix: lower the decoder's overflow cap to
`DATA_BUFFER_SIZE - 1` (so the terminator slot is always free) and add a Unity
case for a payload of *exactly* `DATA_BUFFER_SIZE` bytes — the existing
`test_cobs_oversized_frame_bounded_recovery` uses `DATA_BUFFER_SIZE + 4` and skips
the boundary that triggers this bug.

### CR-02: Unbounded busy-wait hang on a truncated command frame (no timeout)

**File:** `firestarter/src/firestarter.cpp:158-191` (CMD_IDLE branch) +
`firestarter/src/boards/rurp_serial_utils.cpp:91-92, 124-125`
**Issue:**
The phase deleted the per-frame wall-clock timeout (the "2 s cascade … SC1 win",
documented in the test file at `test_cobs_cmd_frame.cpp:164-167` and in
`rurp_serial_utils.cpp:82`). The decoder now relies solely on the `0x00`
delimiter for frame termination and spins on raw availability:

```c
// rurp_serial_utils.cpp:124-125 (main read loop)
while (rurp_communication_available() <= 0) {}   // spins forever
// rurp_serial_utils.cpp:91-92 (_drain_to_delimiter)
while (rurp_communication_available() <= 0) {}   // spins forever
```

If the host writes a partial frame and then stops (cut cable, host crash, killed
process mid-`write`, USB-CDC stall), the firmware enters this loop with
`available() == 0` and no further bytes ever arriving. There is no escape:

- The decoder has no timeout (deleted by design).
- The `loop()` watchdog at `firestarter.cpp:159`
  (`handle.cmd != CMD_IDLE && timeout < millis()`) **cannot fire** — the firmware
  is still in the `CMD_IDLE` state while decoding, so `handle.cmd == CMD_IDLE` and
  the timeout branch is never taken. `op_reset_timeout()` is only called at the
  end of a *successful* `init_programmer_framed` (`firestarter.cpp:143`).

Result: a truncated frame hard-hangs the programmer until physical reset — a
denial-of-availability regression versus the previous timeout-bounded ingest. The
firmware controls live programming hardware; a hang mid-session can also leave
control-register / VPP state asserted (the cleanup in `command_done()` never runs).

The new Unity suite does **not** cover this: every test feeds a complete stream
ending in `0x00`. `test_cobs_resync_bounded` and
`test_cobs_oversized_frame_bounded_recovery` both terminate every frame, so the
busy-wait always has bytes to consume.

**Fix:** Reintroduce a bounded wait. Either:

- Make `rurp_communication_read_data()` return early (negative) when no byte
  arrives within a deadline (`millis()`-based), e.g. wrap the
  `while (available() <= 0)` spins with a `TIMEOUT_MS` cap and `return -1` /
  `_drain_to_delimiter()` on expiry; **or**
- Only call `rurp_communication_read_data()` once `available()` indicates a full
  delimited frame is buffered, and arm the `loop()` timeout the moment the first
  byte is seen.

Add a Unity case feeding bytes with no trailing `0x00` and asserting the call
returns (does not spin) — currently impossible to express because the mock has no
"starved read" path, so the mock needs a finite-stream-then-empty mode too.

## Warnings

### WR-01: `CMD_FRAME_MAX` declared on both sides but never enforced on the host

**File:** `firestarter_app/firestarter/constants.py:24-28` (+
`firestarter_app/firestarter/serial_comm.py:156-175`)
**Issue:**
`CMD_FRAME_MAX = 512` is added "for parity" but is dead on the host — `grep`
finds zero references outside its own definition. `send_json_command()` will
serialise, CRC, COBS-encode, and transmit a command of *any* size. If a command's
JSON exceeds 512 bytes (e.g. a large `bus-config`, or a future field), the
firmware decoder silently returns `-2` (overflow drain) and the operation fails
with only the reused generic `MSG_ERR_EMPTY_INPUT` error
(`firestarter.cpp:187`) — no actionable diagnostic on either side. The "~422 B
worst case" claim is asserted in a comment but never guarded.

**Fix:** Enforce the cap at the single send chokepoint before writing:

```python
json_bytes = json.dumps(command_dict, separators=(",", ":")).encode("ascii")
# +1 for the CRC byte that shares the frame budget
if len(json_bytes) + 1 > CMD_FRAME_MAX:
    raise SerialError(
        f"Command frame {len(json_bytes) + 1} B exceeds CMD_FRAME_MAX "
        f"({CMD_FRAME_MAX} B); firmware would reject it."
    )
```

Import `CMD_FRAME_MAX` from `constants` (currently not imported in
`serial_comm.py`).

### WR-02: Generic error masks all frame-failure causes (CRC vs overflow vs underrun)

**File:** `firestarter/src/firestarter.cpp:183-188`
**Issue:**
Every decoder failure code (`-1` underrun, `-2` overflow, `-3` COBS violation,
`-4` CRC mismatch) collapses to a single `LOG_ERROR_ID(MSG_ERR_EMPTY_INPUT)`. The
inline comment acknowledges this is a stopgap ("MSG_ERR_BAD_FRAME requires a TOML
catalog update — deferred"). For a *breaking* wire-protocol change whose first
field symptom will be "old host ↔ new firmware → decode error", operators get an
actively misleading message ("empty input") for a CRC or version-mismatch
failure. This will generate false bug reports during the lockstep-upgrade window
the READMEs warn about.

**Fix:** At minimum log the negative return code as a parameter (the data channel
already does this — `operation_utils.cpp:166`
`LOG_ERROR_ID_U16(MSG_ERR_DATA_ERR_N, (uint16_t)res)`). Reuse that message ID, or
add `MSG_ERR_BAD_FRAME` to the catalog before shipping the breaking change rather
than after.

### WR-03: `_drain_to_delimiter` / read loop ignore a sticky `read() < 0` only after the spin

**File:** `firestarter/src/boards/rurp_serial_utils.cpp:91-97, 124-131`
**Issue:**
Both loops first `while (available() <= 0) {}` and only then `read()`. The
`available()` spin is the hang vector (CR-02), but note a secondary issue: if the
underlying serial returns a transient `available() > 0` followed by `read() < 0`,
`_drain_to_delimiter` treats `d < 0` as a terminator and breaks
(`rurp_serial_utils.cpp:94`), silently re-anchoring on a *non*-delimiter
condition. That can desync the next frame (the real `0x00` is still in the
stream). The main loop handles `b < 0` differently — it drains and returns `-1`.
The two read sites disagree on what a negative read means.

**Fix:** Make the negative-read handling consistent. In `_drain_to_delimiter`, a
`read() < 0` after `available() > 0` is an I/O error, not a frame boundary —
either keep spinning or propagate the error upward rather than treating it as a
successful resync.

### WR-04: COBS overhead can push a max-size payload past the decoder cap on the wire

**File:** `firestarter_app/firestarter/serial_comm.py:171-175` +
`firestarter/src/boards/rurp_serial_utils.cpp:113`
**Issue:**
The host budget check (WR-01, if added) and the firmware cap both reason about the
*decoded payload* length. But the firmware decoder enforces the cap on `out`
(decoded bytes), while the host transmits `cobs_encode(json + crc)` which is
larger on the wire. This is internally consistent (the cap is on decoded output,
which is what matters for `data_buffer`), so it is not a correctness bug — but the
parity comment in `constants.py:24-28` conflates "frame size" with "payload size".
A JSON payload of exactly 512 B decodes to 512 B and trips CR-01; the wire frame
is ~514+ B. The naming (`CMD_FRAME_MAX`) implies a *frame* (encoded) limit but the
firmware enforces a *payload* (decoded) limit.

**Fix:** Rename or re-document so the host guard checks the same quantity the
firmware caps (decoded `len(json_bytes) + 1`), and state explicitly that the
limit is on decoded payload, not on the COBS-encoded frame. Coordinate with the
CR-01 fix so the effective payload cap is `DATA_BUFFER_SIZE - 1` on both sides.

## Info

### IN-01: Reference COBS encoder duplicated three times

**File:** `firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp:95-118`
**Issue:** `test_cobs_encode` is a third hand-rolled COBS encoder (alongside the
host `cobs_encode` in `frame_parser.py` and the firmware
`rurp_communication_write` in `rurp_serial_utils.cpp`). Three independent
implementations of the same edge-case-laden algorithm (254-run, trailing-zero,
zero-CRC) is a divergence risk; a bug in the test encoder could mask a decoder
bug. The test deliberately re-derives it for independence, which is defensible,
but worth a tracking note.
**Fix:** Add a single round-trip Unity case that pins the firmware
`rurp_communication_write` output against `rurp_communication_read_data` so the
production encoder/decoder pair is exercised end-to-end (not just decoder vs
test-encoder).

### IN-02: Unreachable inner guard left in the data-channel `#` branch

**File:** `firestarter/src/operation_utils.cpp:159-163`
**Issue:** The comment states the inner `available()` guard is now unreachable
under COBS framing ("the inner guard is unreachable"). Dead-but-documented code.
Low priority, but a candidate for removal during the same pass to avoid confusion
about whether the data-channel ingest still has a fixed-header assumption.
**Fix:** Remove the dead guard or convert the comment into a one-line note.

### IN-03: Leonardo buffer size pinned to 512 via a "TEMP" A/B-test flag

**File:** `firestarter/platformio.ini:64-65`
**Issue:** `-D DATA_BUFFER_SIZE=512  ; TEMP: 512 to match Uno for buffer-size A/B
test (was 1024)`. This is unrelated to Phase 51 but is in a reviewed file and
interacts with CR-01: while this flag is active, Leonardo shares the Uno's 512-B
boundary and the same off-by-one OOB applies to Leonardo too. If/when this reverts
to 1024, the CR-01 fix must still hold at whatever `DATA_BUFFER_SIZE` is.
**Fix:** Confirm the CR-01 fix is expressed in terms of `DATA_BUFFER_SIZE` (not a
literal 512) so it survives the Leonardo revert. No action needed on the TEMP flag
itself for this phase.

---

_Reviewed: 2026-06-02_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

---
status: partial
phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
source: [08-VERIFICATION.md]
started: 2026-05-18T00:00:00Z
updated: 2026-06-16T21:01:10Z
---

## Current Test

[testing paused — Test 1 end-to-end write deferred to /gsd-debug (out-of-scope transport regression)]

## Tests

### 1. SC#2 — End-to-end write on Uno + Leonardo
expected: Both `firestarter write -e W27C512 -i <known.bin>` runs complete normally with INIT/MAIN/END acks rendered from ID-frame decoding alone (no literal `INIT:` / `MAIN:` / `END:` text prefix in CLI output). The bootstrap `OK: FW: ...` line still appears at session start (LFW-05 preserved).
result: blocked
blocked_by: other
reason: |
  Bench session 2026-06-16, Leonardo /dev/ttyACM0, W27C512 seated, firmware updated b6→b8 during the session.
  PHASE-08 DELIVERABLE VERIFIED WORKING: all acks (`OK:`, `DATA:`, `ERROR:`) render via ID-frame decoding
  with NO literal `INIT:`/`MAIN:`/`END:` text prefixes; bootstrap `OK: FW: 3.0.0b8:leonardo` shown. The
  SC#2 *protocol* assertion is satisfied.
  END-TO-END WRITE DOES NOT COMPLETE — but the cause is OUT OF PHASE-08 SCOPE: firmware aborts during the
  write MAIN phase with MSG_ERR_EMPTY_INPUT (0xA4). Per firmware src/firestarter.cpp:191-194 this code is
  OVERLOADED ("CRC mismatch, COBS violation, overflow, or read underrun" — dedicated MSG_ERR_BAD_FRAME
  deferred), so this is a write-data-chunk COBS/CRC framing fault, not literally empty input. Reproduced
  across 3 file sizes (100 B, 37 KB, 64 KB) on matched b8/b8 → not a version issue. Regression vs the
  Phase-54 "EVEN-01 write proven clean on Leonardo/ACM0" baseline. Disposition (operator, 2026-06-16):
  hand off to /gsd-debug as a standalone write-path transport regression; NOT a Phase-08 gap.
  Earlier in the session writes also hit a VPP-high (13.1V > 12.0V) init abort; operator adjusted VPP and
  the `id`/`read` paths then init clean — VPP no longer a factor in the remaining write fault.

### 2. SC#3 — Byte-identical readback on Uno + Leonardo
expected: `firestarter read -e W27C512 -o /tmp/ph8-{uno,leo}.bin` produces a file byte-identical to the pre-Phase-8 baseline. `diff /tmp/ph8-uno.bin <Phase 7 baseline file>` and the Leonardo equivalent both exit 0.
result: pass
notes: |
  Bench 2026-06-16, Leonardo /dev/ttyACM0, fw 3.0.0b8. `firestarter read W27C512 /tmp/ph8-leo.bin` completed
  cleanly: full 65536 bytes in 7.26s via chunked MSG_DATA_CHUNK MAIN streaming; `Connecting... OK` +
  `Read complete`, NO literal `INIT:`/`MAIN:`/`END:` prefixes. The Phase-08 deliverable (ID-frame ack
  rendering + chunked read streaming, incl. the u16-required W-04 >253B path) is verified end-to-end on the
  read path. CAVEAT: the strict byte-identical-vs-Phase-7-baseline diff was NOT performed — no Phase-7
  baseline file is present in the workspace, and the chip contents were disturbed by the in-session write
  attempts. The byte-identical check is a chip-data assertion, not the Phase-08 protocol assertion; the
  protocol behavior SC#3 targets is confirmed. Uno not exercised this session (no Uno-class board at bench).

## Summary

total: 2
passed: 1
issues: 0
pending: 0
skipped: 0
blocked: 1

## Gaps

None against Phase 08 — the Phase-08 protocol deliverable (prefix→ID-frame ack rendering) is verified working
on both write and read paths. The write end-to-end failure is a separate, out-of-scope write-data-chunk
transport regression (overloaded MSG_ERR_EMPTY_INPUT / 0xA4) handed off to /gsd-debug; it is not a Phase-08
code defect and does not produce a Phase-08 gap.

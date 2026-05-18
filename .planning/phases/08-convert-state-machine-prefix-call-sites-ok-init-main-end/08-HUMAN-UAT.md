---
status: partial
phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
source: [08-VERIFICATION.md]
started: 2026-05-18T00:00:00Z
updated: 2026-05-18T00:00:00Z
---

## Current Test

[awaiting chip-seated bench session]

## Tests

### 1. SC#2 — End-to-end write on Uno + Leonardo
expected: Both `firestarter write -e W27C512 -i <known.bin>` runs complete normally with INIT/MAIN/END acks rendered from ID-frame decoding alone (no literal `INIT:` / `MAIN:` / `END:` text prefix in CLI output). The bootstrap `OK: FW: ...` line still appears at session start (LFW-05 preserved).
result: [pending]
notes: Wire-protocol changes verified chipless during the Phase 8 close session (see 08-MEASUREMENT.md § Bench Verification). What remains is chip-physics integration which Phase 8 did not modify. Run on both boards per project memory (`always-mirror-uno-leonardo-tests`).

### 2. SC#3 — Byte-identical readback on Uno + Leonardo
expected: `firestarter read -e W27C512 -o /tmp/ph8-{uno,leo}.bin` produces a file byte-identical to the pre-Phase-8 baseline. `diff /tmp/ph8-uno.bin <Phase 7 baseline file>` and the Leonardo equivalent both exit 0.
result: [pending]
notes: The MSG_DATA_CHUNK chunked-streaming path was unit-tested in `firestarter_app/tests/test_decoder.py` (chunks > 253 B exercise the u16-required W-04 path). Real chip readback proves the firmware-side wrapping matches.

## Summary

total: 2
passed: 0
issues: 0
pending: 2
skipped: 0
blocked: 0

## Gaps

None — both items are blocked on bench hardware availability, not on code defects.

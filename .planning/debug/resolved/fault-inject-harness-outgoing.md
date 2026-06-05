---
status: resolved
trigger: "53-04 XACT-02 fault injection: outgoing leg reports 'corrupted transfer unexpectedly succeeded'; incoming leg detects the corrupt frame but the corrupted transfer ends in a Timeout of unverified latency."
created: 2026-06-03
updated: 2026-06-05
phase: 53
related: [transport-protocol-verify, write-verify-datapath-overflow]
root_cause: "Harness wiring bug in EpromOperator.fault_inject_cycle (firestarter_app, 53-02). The outgoing _fault_inject_outgoing hook fires inside send_json_command, but fault_inject_cycle sets it INSIDE _operation_context AFTER the read's only JSON command (the setup) has already been sent during context entry. A READ's MAIN phase sends only plaintext 'OK' acks via send_string (never send_json_command), so the hook never fires -> nothing is corrupted -> the read succeeds -> 'corrupted transfer unexpectedly succeeded' (a FALSE NEGATIVE). It is NOT evidence the firmware accepts corrupt host->fw frames; the outgoing fault was simply never injected."
fix: "RESOLVED in firestarter_app commit 630fafd (option (a)). Threaded an optional fault_inject_outgoing hook through _operation_context -> _setup_operation -> find_and_connect -> _probe_port so it arms the communicator BEFORE the setup command frame is sent (the only corruptible host->fw command frame; a READ's MAIN phase sends only plaintext acks). Default None keeps production byte-identical (T-53-03). fault_inject_cycle (outgoing) now treats the bounded connection failure from a rejected setup frame as the expected outcome, and a fresh clean transfer proves recovery; added error-latency measurement + fault-inject-<direction>-log.txt recording the sub-second-clean-error / 2s-cascade verdict. +5 unit tests; full suite 467 passed; coverage 71.85%; ruff clean; mypy neutral. REMAINING (normal 53-04 bench execution, NOT a debug item): operator hardware re-run of all 4 combos to record the measured latency + byte-exact recovery evidence under .planning/v1.10/bench-verification/fault-injection/."
---

# Debug: fault-inject-harness-outgoing

## Symptoms (53-04 bench, Uno /dev/ttyACM0, hardened fw bafbe8a, chip seated, Rev 2.0)
- `dev fault-inject --direction outgoing --fault-form corrupt-crc8`: "fault_inject_cycle: corrupted transfer unexpectedly succeeded." (exit 1)
- `dev fault-inject --direction outgoing --fault-form drop-delimiter`: same.
- `dev fault-inject --direction incoming --fault-form corrupt-crc8`: host DETECTED it — "CRC mismatch for ID 0x10: expected 0x70, got 0x71" — then "ERROR: Timeout" then reconnect (exit 0). Detection + recovery worked; error LATENCY unmeasured (bc missing).

## Findings
1. **Outgoing harness bug (FALSE NEGATIVE):** hook set after the only send_json_command for a
   read; never fires. fault_inject_cycle (eprom_operations.py ~813) + the _fault_inject_outgoing
   hook in send_json_command. The read state machine uses send_string for acks, not
   send_json_command, so the outgoing fault is never injected during a read cycle.
2. **Incoming leg works (core XACT-02 property):** FaultInjectingSerialCommunicator mutated a
   fw->host frame; the host caught the CRC mismatch (did NOT silently accept) and the clean
   follow-on transfer succeeded. Resync = detect + recover, demonstrated. BUT the corrupted
   transfer ended in a Timeout whose latency is unverified — XACT-02 requires a SUB-SECOND clean
   error (no 2 s cascade), so this is not yet a confirmed pass.

## Scope
- This is a TEST-HARNESS defect (53-02) + a missing latency assertion, NOT a proven transport
  defect. The COBS transport (command channel CRC8-before-parse, data path, resync detection) is
  otherwise verified working this session. XACT-02 cannot be CLAIMED until the outgoing injection
  is fixed and the sub-second error latency is measured on both legs.

## Next action
Operator paused the bench. When resumed: fix the outgoing injection point, add latency
measurement, re-run all 4 combos (both directions x corrupt-crc8/drop-delimiter), and only then
record XACT-02 evidence for 53-04.

## Resolution (2026-06-05)
Harness defect fixed in firestarter_app commit `630fafd` (option (a) — corrupt the SETUP
command frame at connection time). The outgoing fault now genuinely fires (no more false
negative), and `fault-inject-<direction>-log.txt` records the measured error latency so the
sub-second-clean-error (no 2 s cascade) XACT-02 acceptance can be confirmed on hardware.
Production path byte-identical when the hook is None (T-53-03). +5 unit tests; full suite
467 passed; coverage 71.85%; ruff clean; mypy neutral (pre-existing watermark drift noted).

This closes the DIAGNOSED HARNESS DEFECT. The remaining XACT-02 work is a normal bench
execution of plan 53-04 (run all 4 combos on real hardware, record latency + byte-exact
recovery into `.planning/v1.10/bench-verification/fault-injection/`) — tracked under 53-04,
not as a debug session.

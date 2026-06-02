---
phase: 51-command-channel-framing-migration-breaking-wire-change
verified: 2026-06-02T00:00:00Z
status: gaps_found
score: 2/4 must-haves verified
overrides_applied: 0
gaps:
  - truth: "Host→fw command channel emits framed commands (Phase-49/50 framing); firmware decodes a frame and verifies CRC8 BEFORE the JSON parser sees the payload — closes CRC-01 command-channel obligation"
    status: partial
    reason: "CRC8-before-parse wiring is present and correct. However, CR-01 (off-by-one OOB write at the exact 512-byte payload boundary: handle.data_buffer[512]='\\0' writes one past the 512-element array, corrupting data_size) is confirmed in the shipped firestarter.cpp:179. The decoder correctly returns n=512 for a 512-byte payload; the NUL-terminate step then writes out-of-bounds into the struct. This is an active memory-safety defect in the new decode path."
    artifacts:
      - path: "firestarter/src/firestarter.cpp"
        issue: "Line 179: handle.data_buffer[n] = '\\0'; with n==512 writes data_buffer[512] — one past char data_buffer[DATA_BUFFER_SIZE] (512 elements). On Uno this overwrites data_size (the next struct field) and potentially bus_config on the single ~545-B-RAM global handle. Undefined behavior on the exact boundary the design reserves as valid (payload cap = DATA_BUFFER_SIZE, not DATA_BUFFER_SIZE-1). The test suite covers DATA_BUFFER_SIZE+4 (overflow-drain path) but never exactly DATA_BUFFER_SIZE, so the boundary OOB write is uncovered by the new Unity suite."
    missing:
      - "Clamp the NUL-terminate write: guard `if (n < DATA_BUFFER_SIZE)` before `data_buffer[n] = '\\0'` at firestarter.cpp:179 (short-term fix at call site)"
      - "Preferred long-term fix: lower decoder overflow cap to DATA_BUFFER_SIZE-1 so the terminator slot is always free, ensuring n <= DATA_BUFFER_SIZE-1 always holds"
      - "Add a Unity test case for exactly DATA_BUFFER_SIZE-byte payload to pin the boundary"
  - truth: "A representative set of host commands round-trips through the framed channel, parsed identically to pre-migration — no command-surface regression"
    status: failed
    reason: "CR-02 (confirmed): rurp_communication_read_data() contains unbounded busy-wait spins — both in the main decode loop (rurp_serial_utils.cpp:125: `while (rurp_communication_available() <= 0) {}`) and in _drain_to_delimiter (rurp_serial_utils.cpp:92: same pattern). If the host writes a partial frame and then stops (cut cable, host crash, USB-CDC stall), the firmware enters this spin with no escape: (a) the decoder has no timeout (deleted by design in Phase 50 as 'SC1 win'); (b) the loop() timeout guard at firestarter.cpp:159 requires `cmd != CMD_IDLE` but cmd remains CMD_IDLE throughout the decode call — so the guard CANNOT fire. Result: a truncated frame hard-hangs the programmer until physical reset. This is a behavioral regression versus the pre-migration path, which was timeout-bounded. The firmware controls live programming hardware — a hang can leave VPP asserted after command_done() never runs. The new Unity suite never tests a partial/truncated stream (every test feeds a complete stream ending in 0x00), so this defect is uncovered by the test suite."
    artifacts:
      - path: "firestarter/src/boards/rurp_serial_utils.cpp"
        issue: "Lines 92 and 125: `while (rurp_communication_available() <= 0) {}` spins indefinitely on host silence. No timeout wrapper. The per-frame timeout was deleted in Phase 50 (SC1 win) and Phase 51 did not add a replacement watchdog for the CMD_IDLE decode path."
      - path: "firestarter/src/firestarter.cpp"
        issue: "Lines 158-159: loop() timeout guard fires only when `handle.cmd != CMD_IDLE`. During CMD_IDLE decode the cmd stays CMD_IDLE throughout the blocking call, making the timeout guard unreachable."
    missing:
      - "Add a bounded wait to rurp_communication_read_data() or _drain_to_delimiter(): wrap the `while (available() <= 0) {}` spins with a millis()-based deadline (e.g. TIMEOUT_MS cap) and return -1 / propagate failure on expiry"
      - "Alternative: only call rurp_communication_read_data() once available() signals a complete delimited frame (requires a peek-until-delimiter helper) and arm the loop() timeout the moment the first byte is seen"
      - "Add a Unity test case for a partial frame with no trailing 0x00 that asserts the call returns (not spins) — requires adding a finite-stream-then-empty mode to the serial read mock"
deferred: []
human_verification: []
---

# Phase 51: Command-Channel Framing Migration Verification Report

**Phase Goal:** The host→firmware JSON command channel is migrated into the same framing layer — the firmware decodes a frame, verifies its CRC8, then hands the payload to the JSON parser; the legacy "`{`-peek and discard non-`{` bytes" path is replaced. This is a breaking wire-protocol change: firmware and host upgrade lockstep with no mixed-version interop.

**Verified:** 2026-06-02T00:00:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC1 | Host→fw command channel emits framed commands; firmware decodes and verifies CRC8 BEFORE JSON parser sees payload (closes CRC-01 command-channel obligation) | PARTIAL | Framing wiring confirmed in both repos. CRC-before-parse path in rurp_communication_read_data() is correct. Off-by-one OOB write (CR-01) confirmed at firestarter.cpp:179 — `data_buffer[512]='\\0'` when decoder returns n=512. Corrupts the global handle struct on the exact design boundary. |
| SC2 | Legacy `{`-peek / discard-non-`{` command-ingest path is replaced (or demoted to explicit documented fallback) | VERIFIED | `rurp_communication_peak()`, `== '{'`, and in-path `rurp_communication_read_bytes()` are all absent from firestarter.cpp production code (comment reference at line 114 only). grep confirms clean deletion. |
| SC3 | Breaking lockstep upgrade enforced/documented for the beta cut; no silent mixed-version mis-driving | VERIFIED | Both sub-repo READMEs contain "Breaking Changes (v1.10)" sections with explicit "breaking" keyword, COBS+CRC8 framing description, lockstep upgrade requirement, no mixed-version interop statement, and beta-only / operator-gated stable promotion note. D-01/D-02 (documentation-as-guard) satisfied. |
| SC4 | A representative set of host commands round-trips through the framed channel, parsed identically to pre-migration — no command-surface regression | FAILED | Unit tests pass (33/33 firmware, 413/413 host) but CR-02 (unbounded busy-wait hang on truncated frame) is an observable behavioral regression versus the pre-migration timeout-bounded path. A truncated command frame hard-hangs the firmware until physical reset — no escape route exists because the loop() timeout guard requires `cmd != CMD_IDLE` and the firmware stays in CMD_IDLE throughout the decode spin. |

**Score:** 2/4 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/src/firestarter.cpp` | COBS frame-decode CMD_IDLE ingest + init_programmer_framed | PARTIAL (CR-01 defect) | Present and wired correctly except for OOB NUL-terminate at the 512-byte boundary |
| `firestarter/src/boards/rurp_serial_utils.cpp` | COBS decoder primitive with CRC8 verify + drain recovery | PARTIAL (CR-02 defect) | CRC verify path correct; busy-wait loops lack timeout guard for truncated-frame hang |
| `firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp` | Unity command-frame decode + CRC8-reject + bounded-recovery cases | VERIFIED | Contains all four cases including `test_cobs_crc_reject_does_not_reach_parser`. Does NOT cover exactly-DATA_BUFFER_SIZE payload or truncated-frame (no-delimiter) streams — gaps that correspond to CR-01 and CR-02 respectively. |
| `firestarter/test/native/avr/test_cobs_cmd_frame/host_stubs.cpp` | Native-platform rurp_* stubs via _shared/host_stubs_common.inc | VERIFIED | Present; includes `host_stubs_common.inc` |
| `firestarter/include/firestarter.h` | CMD_FRAME_MAX constant (firmware half of parity pair) | VERIFIED | `#define CMD_FRAME_MAX DATA_BUFFER_SIZE` at line 26 with full comment |
| `firestarter_app/firestarter/serial_comm.py` | Framed send_json_command() (COBS+CRC8, atomic write) | VERIFIED | send_json_command at line 156 correctly: CRC8 over raw json_bytes, cobs_encode(json_bytes+crc), single frame = body+b"\\x00", one send_bytes() call. No send_string bypass. |
| `firestarter_app/firestarter/constants.py` | CMD_FRAME_MAX = 512 (host half of parity pair) | VERIFIED | Present at line 28 with sync comment |
| `firestarter_app/tests/test_serial_comm.py` | Framed-frame, atomic-write, and version-probe-framing tests | VERIFIED | Three Phase-51 tests confirmed: `test_send_json_command_emits_cobs_frame`, `test_send_json_command_atomic_frame`, `test_send_json_command_version_probe_is_framed` |
| `firestarter/README.md` | Breaking wire-change note (firmware side) | VERIFIED | "Breaking Changes (v1.10)" section with "breaking" keyword, COBS/CRC8 description, lockstep requirement |
| `firestarter_app/README.md` | Breaking wire-change note (host side) | VERIFIED | Same breaking-change section present |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `firestarter.cpp CMD_IDLE branch` | `rurp_communication_read_data(handle.data_buffer)` | Frame decode replacing {-peek | WIRED | Line 176: `int n = rurp_communication_read_data(handle.data_buffer)`. Gate is strictly `n > 0`. |
| `firestarter.cpp CMD_IDLE` | `init_programmer_framed(&handle)` | Called after n>0 decode | WIRED | Line 180: data pre-filled by decode step before call |
| `firestarter/platformio.ini` | `native/avr/test_cobs_cmd_frame` | test_filter + -I build flag | WIRED | Two entries confirmed (line 84: test_filter; line 94: -I flag) |
| `send_json_command` | `cobs_encode` / `_crc8_ccitt` | COBS+CRC8 wrap before send_bytes | WIRED | Lines 53, 172-173 in serial_comm.py |
| `send_json_command` | `send_bytes(frame)` | Single atomic write | WIRED | Line 175: `return self.send_bytes(frame)` — one bytes object, one call |
| `firestarter.h CMD_FRAME_MAX` | `constants.py CMD_FRAME_MAX` | Constant parity (CLAUDE.md) | WIRED | Both = 512. NOTE: CMD_FRAME_MAX is declared in constants.py but never imported or enforced in serial_comm.py — the cap is declared but dead on the host send path (WR-01 from code review). |

---

## Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `firestarter.cpp CMD_IDLE` | `handle.data_buffer` / `handle.data_size` | `rurp_communication_read_data()` reads from serial RX buffer | Yes — live serial bytes | FLOWING |
| `serial_comm.py send_json_command` | `frame` bytes | `json.dumps(command_dict)` + `cobs_encode` + CRC8 | Yes — computed from caller's command dict | FLOWING |

---

## Behavioral Spot-Checks (Step 7b)

Step 7b SKIPPED for firmware (no runnable hardware entry point in the devcontainer for the Arduino binary). Host-side checks covered by the existing pytest suite (413/413 confirmed in SUMMARY).

---

## Probe Execution (Step 7c)

No probes declared in plan frontmatter or SUMMARY. Conventional `scripts/*/tests/probe-*.sh` not present for this phase. SKIPPED.

---

## Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FRAME-05 | 51-01, 51-02, 51-03 | Host→fw command channel migrated to COBS framing; firmware decodes frame, verifies CRC8 before JSON parser; legacy {-peek replaced; breaking lockstep change | PARTIAL | Firmware framing wired (SC2 VERIFIED, SC3 VERIFIED); CRC-before-parse path correct; two ship-blocking defects (CR-01, CR-02) leave SC1 and SC4 unmet in full |
| CRC-01 | 51-01, 51-02 | CRC8-CCITT verified before parse on every command frame; command channel previously had no checksum | PARTIAL | CRC8 verify logic correct and confirmed by `test_cobs_crc_reject_does_not_reach_parser`; CRC-01's robustness intent is undermined by CR-01 (OOB write post-CRC) and CR-02 (no-timeout hang pre-CRC on truncated frames) |

---

## Code Review Defect Assessment (CR-01 / CR-02)

The code review (`51-REVIEW.md`) identified two Critical (ship-blocking) defects in the firmware decode path. Both are independently confirmed against the source. Verdicts for this phase:

### CR-01: Off-by-one OOB write — `data_buffer[n] = '\0'` at the 512-byte boundary

**File:** `firestarter/src/firestarter.cpp:179`
**Confirmed in source:** YES.

`data_buffer` is declared `char data_buffer[DATA_BUFFER_SIZE]` (512 bytes, `firestarter.h:95`). The PUSH macro in `rurp_communication_read_data()` caps on `out >= DATA_BUFFER_SIZE` BEFORE committing — meaning a payload of exactly 512 bytes results in `out == 512` returned as `n`. The CMD_IDLE branch then executes `handle.data_buffer[512] = '\0'`, writing one past the 512-element array. The next struct field is `uint32_t data_size` (`firestarter.h:96`), which receives the NUL byte into its first byte — silent memory corruption of the same value just assigned on line 178 (`handle.data_size = (uint32_t)n`). On Uno with ~545 B free RAM, this corruption of the global `handle` is directly observable.

**The test suite does NOT cover this:** `test_cobs_oversized_frame_bounded_recovery` uses `DATA_BUFFER_SIZE + 4`, skipping the `DATA_BUFFER_SIZE` exact boundary that triggers the OOB.

**Bearing on SC1:** SC1 claims "CRC8 BEFORE the JSON parser sees the payload". This is technically true (CRC passes, then the OOB write fires, THEN parse_json is called). However, the OOB write corrupts `data_size` between the decode step and the parse step. parse_json uses `handle->data_size` as the authoritative length for jsmn_parse. After the OOB write, `data_size` may be corrupted (the NUL overwrites its MSB). For a 512-byte payload on a little-endian AVR, the corruption overwrites the LSB of data_size (which was just set to 512 = 0x00000200). On little-endian, `data_size[0]` is the LSB = 0x00, and the NUL write goes to `data_buffer[512]` which is `data_size[0]` (not `data_size[3]`/MSB — little-endian layout). So data_size gets corrupted from 0x200 to 0x200 (LSB was already 0x00). In this particular case the corruption is a no-op on AVR little-endian. Nevertheless the OOB write is undefined behavior and its effect depends on the compiler/layout — it cannot be relied upon to be safe.

**Verdict: BLOCKER.** Undefined behavior via OOB write in a security-critical decode path that the phase introduces. Even if the practical impact is zero for current JSON command sizes (~422 B worst-case << 512 B), the design explicitly permits payloads up to DATA_BUFFER_SIZE, and the code does not guard the boundary. Must be fixed before shipping.

### CR-02: Unbounded busy-wait hang on a truncated command frame

**File:** `firestarter/src/boards/rurp_serial_utils.cpp:92, 125` + `firestarter/src/firestarter.cpp:158-159`
**Confirmed in source:** YES.

Both `_drain_to_delimiter()` (line 92) and the main `rurp_communication_read_data()` loop (line 125) contain `while (rurp_communication_available() <= 0) {}` with no escape. The `loop()` timeout guard (`firestarter.cpp:159`) fires only when `handle.cmd != CMD_IDLE`. While `rurp_communication_read_data()` is executing, `handle.cmd` remains `CMD_IDLE` (it is not changed until `init_programmer_framed()` succeeds and parse_json sets `handle->cmd`). Therefore the timeout guard CANNOT interrupt the busy-wait. A truncated frame — which can arise from a killed host process, cut USB cable, or USB-CDC TX stall mid-`write()` — hangs the firmware until physical reset. No timeout, no recovery, no cleanup (`command_done()` never runs, VPP state may remain asserted if a previous command left the hardware in programmer mode when the new command was started).

**The test suite does NOT cover this:** Every test in `test_cobs_cmd_frame` feeds a complete stream with a trailing `0x00`. The serial read mock has no "exhausted stream" mode, so a truncated-frame test cannot currently be expressed.

**Bearing on SC4:** SC4 requires "no command-surface regression." The pre-migration path used `rurp_communication_read_bytes()` (Arduino `readBytes()`), which is timeout-bounded by the `Serial.setTimeout()` value. The new path has NO timeout equivalent for the CMD_IDLE decode. This is a behavioral regression: a dropped connection that previously caused a timeout and clean recovery now causes a permanent firmware hang. The phase plan explicitly said "do NOT add a new idle wall-clock timer" (D-06), but this decision removes safety that previously existed. D-06 was written to avoid the old 2-second timeout-cascade desync — a valid concern — but the consequence is that no timeout of any kind now covers the CMD_IDLE decode path.

**Verdict: BLOCKER.** The firmware controls live programming hardware. A hang mid-session (even before a command transitions out of CMD_IDLE) can leave the system in an unknown hardware state. The milestone goal includes "no silent mixed-version mis-driving" and "bounded-corruption" intent; a permanent hang-until-reset on a common failure mode (host crash, disconnection) is worse than the pre-migration behavior and directly violates the no-regression claim of SC4.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter/src/firestarter.cpp` | 179 | `data_buffer[n] = '\\0'` with n reachable at DATA_BUFFER_SIZE | BLOCKER (CR-01) | OOB write into subsequent struct field; undefined behavior on the design's valid payload boundary |
| `firestarter/src/boards/rurp_serial_utils.cpp` | 92, 125 | `while (available() <= 0) {}` — unbounded spin | BLOCKER (CR-02) | Firmware hard-hang on truncated frame; no escape route from CMD_IDLE loop() timeout guard |
| `firestarter_app/firestarter/constants.py` | 28 | `CMD_FRAME_MAX = 512` defined but not enforced | WARNING (WR-01) | Host can send oversized commands that silently fail on firmware with a misleading error code |
| `firestarter/src/firestarter.cpp` | 187 | `LOG_ERROR_ID(MSG_ERR_EMPTY_INPUT)` for all decode failures | WARNING (WR-02) | Misleading error ID for CRC mismatch / COBS violation / overflow — first symptom operators see on mixed-version pair is "empty input" not "frame decode error" |

---

## Human Verification Required

None — all gaps are programmatically confirmed from source.

---

## Gaps Summary

Two Critical defects from the code review are confirmed in the production source and are not covered by the new Unity suite.

**CR-01 (BLOCKER)** is an off-by-one OOB write: `handle.data_buffer[512] = '\0'` at `firestarter.cpp:179` when `rurp_communication_read_data()` returns `n == DATA_BUFFER_SIZE`. The decoder correctly permits 512-byte payloads (the CRC lookahead means the overflow guard does not fire); the NUL-terminate step then writes one past the array boundary into `data_size`. The test suite covers `DATA_BUFFER_SIZE + 4` but not exactly `DATA_BUFFER_SIZE`, leaving the boundary uncovered. Fix: guard the NUL-terminate with `if (n < DATA_BUFFER_SIZE)` or lower the decoder's effective cap to `DATA_BUFFER_SIZE - 1`.

**CR-02 (BLOCKER)** is an unbounded busy-wait that causes a firmware hang-until-physical-reset on a truncated command frame (dropped host connection, killed process, USB stall). Both `rurp_serial_utils.cpp:92,125` spin forever when `available() == 0`. The `loop()` timeout guard at `firestarter.cpp:159` cannot fire because `handle.cmd == CMD_IDLE` throughout the decode call, disabling the timeout branch. This is a behavioral regression versus the pre-migration path (which was timeout-bounded via `readBytes()`). Fix: add a `millis()`-based per-byte deadline in the spin loops, or restructure so only complete delimited frames enter the decoder.

Both defects are uncovered by the four new Unity cases — the suite exercises the decode primitive only with well-formed complete streams. SC1's "CRC8-before-parse" contract holds for complete frames; SC4's "no regression" claim fails due to CR-02.

The host-side (Plan 02) and documentation (Plan 03) work is complete and correct.

---

_Verified: 2026-06-02T00:00:00Z_
_Verifier: Claude (gsd-verifier)_

---
status: diagnosed
phase: 54-even-block-data-transfers-full-buffer-aligned-host-fw-chunks
source: [54-01-SUMMARY.md, 54-02-SUMMARY.md, 54-03-SUMMARY.md]
started: 2026-06-04T15:00:44Z
updated: 2026-06-04T16:30:00Z
---

## Current Test

[testing complete — 4 passed, 1 issue (firmware VPP-measurement bug, see Gaps)]

## Tests

### 1. Firmware advertises maxchunk in identity string
expected: Firmware identity is a 4-field string `<ver>:<board>:<buf>:<maxchunk>` (e.g. `3.0.0b8:uno:512:512`); 4th field equals full DATA_BUFFER_SIZE (512 Uno / 1024 Leonardo).
result: pass
note: "Verified live by Claude. Flashed Phase 54 firmware to uno328pb (Rev 2.0 shield, socket empty). `firestarter fw` reports 4-field identity `3.0.0b6:uno328pb:512:512` — 4th field (maxchunk)=512=DATA_BUFFER_SIZE. Host FW-handshake (real write/verify probe path) parses firmware_max_chunk=512 and _calculate_buffer_size() returns 512 (full buffer, no buf−2). MINOR OBSERVATION: firmware version field still reads `3.0.0b6`, not the `3.0.0b8` used illustratively in the 54-01 SUMMARY — the version macro was not bumped this phase. Not an EVEN-01 deliverable (the 4th maxchunk field is the deliverable and is present/correct), but flag for a version-bump before the v1.10 beta cut."

### 2. Full-buffer write/verify against a real EPROM
expected: Writing then verifying an EPROM (e.g. `./write_test.sh [EPROM]`) completes successfully. Host→fw data blocks are now full buffer-sized (512 Uno / 1024 Leonardo) with NO `buffer−2` reduction. Even-block transfer — 65536-byte chips divide cleanly with no remainder/short final chunk.
result: issue
reported: "This is a fw bug, it measures 12.2v"
severity: major
note: |
  EVEN-01 TRANSPORT VERIFIED (the phase deliverable is sound): the blank-check
  write streamed 72 consecutive full-buffer 512-byte chunks (0x0000→0x9000, 36KB)
  host→fw with NO buf−2 reduction before aborting on a non-blank chip byte. Host
  sizes chunks to firmware-advertised maxchunk=512 (Test 1); 65536 % 512 == 0.
  ISSUE (separate fw bug, blocks full write+verify): on W27C512/uno328pb/Rev 2.0,
  `firestarter vpp` + the write path report "VPP is low: 1.8V < 12.0V" while the
  operator's bench multimeter reads the actual socket VPP at 12.2V. The firmware
  VPP measurement is wrong. With `-b` (program path, which needs VPP) the write
  stalls at the first chunk (0x0200) and the host times out — deterministic across
  4 retries, both random and all-zero payloads. Reads (blank-check) don't need VPP
  and streamed fine, which is why the no-`-b` path got 72 chunks in. Operator
  verdict: firmware VPP-measurement bug, NOT a real VPP/contact fault and NOT an
  EVEN-01 transport defect. Likely pre-existing (EVEN-01 did not touch VPP code).

### 3. Outdated-firmware rejection (no silent fallback)
expected: When connected to firmware that does NOT advertise the maxchunk field (old/3-field identity), the host raises a clear `FirmwareOutdatedError` and refuses to proceed — it does NOT silently fall back to the old `buf−2` chunk size.
result: pass
note: "Verified live by Claude against the real board on /dev/ttyUSB0 (running pre-Phase-54 firmware 3.0.0b6:uno328pb:512 — 3-field identity, no maxchunk). Host parsed firmware_max_chunk=None and _calculate_buffer_size() raised FirmwareOutdatedError: 'Firmware does not advertise a max-chunk capacity field. Please upgrade the firmware using firestarter fw --install.' No silent buf−2 fallback. Non-destructive (FW-identity read only, no chip operation)."

### 4. Firmware builds within RAM ceiling on all three boards
expected: `pio run -e uno`, `-e uno328pb`, and `-e leonardo` all build SUCCESS. RAM stays well within the 2 KB / 2.5 KB SRAM (Uno 1552 B / 496 B free, uno328pb 1556 B / 492 B free, Leonardo 1993 B / 567 B free). Firmware links and runs. (Note: Uno/uno328pb exceed the Phase-50-vintage 1503 B literal ceiling — attributed to Phase 53 growth, not Phase 54; Phase 54 added only 4 B.)
result: pass
note: "Verified live by Claude — all 3 builds SUCCESS; RAM matched summaries exactly (Uno 1552B/496 free, uno328pb 1556B/492 free, Leonardo 1993B/567 free)."

### 5. Dual-repo test suites + frame-vectors drift gate green
expected: Firmware native suite 42/42 PASSED (all 7 allowlisted suites incl. test_frame_vectors). Host suite 456/456 PASSED, coverage ≥ 70% (71.55%). frame-vectors drift gate clean in BOTH repos (12 vectors, exit 0), TOML byte-identical across repos, and CMD_FRAME_MAX parity (firmware == host == 512).
result: pass
note: "Verified live by Claude — FW native 42/42 succeeded; host 456 passed (71.55% cov, floor 70); FW+host codegen --check exit 0 (12 vectors); TOML diff exit 0 (byte-identical); CMD_FRAME_MAX firmware=DATA_BUFFER_SIZE(512)==host 512."

## Summary

total: 5
passed: 4
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "Firmware reports an accurate VPP voltage (≈12V) so the program/write path can complete; full-buffer even-block write+verify of an EPROM succeeds end-to-end."
  status: failed
  reason: "User reported: This is a fw bug, it measures 12.2v — firmware reports 'VPP is low: 1.8V < 12.0V' while bench multimeter measures actual socket VPP at 12.2V. The misread VPP blocks the program path: write stalls at first chunk (0x0200) and times out (deterministic, 4 retries, random + all-zero payloads) on W27C512/uno328pb/Rev 2.0. EVEN-01 transport itself is sound (72×512B chunks streamed, no buf−2). Suspected pre-existing firmware VPP-measurement bug, outside EVEN-01 scope."
  severity: major
  test: 2
  root_cause: "Stale EEPROM calibration on this uno328pb board: rurp_configuration_t.r1 holds the legacy ~1000 instead of the correct 270000. rurp_read_voltage_mv math is correct — gain = (r1+r2)/r2; with r1=1000,r2=44000 gain≈1.02× so true 12.2V computes as ≈1.75V≈1.8V (exact symptom + 6.8× ratio match). Latent firmware bug: rurp_validate_config re-applies defaults ONLY when config->version != CONFIG_VERSION ('VER06'); Phase 44 changed VALUE_R1 default 1000→270000 in rurp_shield.h WITHOUT bumping CONFIG_VERSION, so already-calibrated boards keep the stale r1 forever — the code fix never reaches their EEPROM. PRE-EXISTING; Phase 54 (f8249b8/c1ae294) touched only COBS cap + FW identity + native tests, not VPP/r1/config code. EVEN-01 transport itself verified sound (72×512B chunks streamed)."
  artifacts:
    - path: "firestarter/src/boards/rurp_common.cpp:52-71"
      issue: "rurp_read_voltage_mv — math correct but trusts stale EEPROM r1/r2"
    - path: "firestarter/src/rurp_config_utils.cpp:32-39"
      issue: "rurp_validate_config — version-gated default refresh; changed default never reaches an already-calibrated board"
    - path: "firestarter/include/rurp_shield.h:46,49-50"
      issue: "CONFIG_VERSION 'VER06' not bumped when VALUE_R1 default changed 1000→270000 (Phase 44); VALUE_R2 44000"
  missing:
    - "BENCH (immediate, non-code): recalibrate this board's EEPROM R1 to 270000 (firestarter config), then re-run Test 2 full write+verify"
    - "FIRMWARE (durable, separate from EVEN-01 scope): make corrected R1/R2 defaults propagate to already-calibrated boards — bump CONFIG_VERSION on default change, OR add a sanity-range guard rejecting implausible r1, OR a targeted r1==1000 migration"
  debug_session: .planning/debug/firmware-vpp-misread.md

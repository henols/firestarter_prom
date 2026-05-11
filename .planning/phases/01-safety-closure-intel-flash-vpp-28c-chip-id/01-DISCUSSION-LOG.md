# Phase 1: Safety Closure (Intel-flash VPP + 28C chip-ID) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-11
**Phase:** 1-safety-closure-intel-flash-vpp-28c-chip-id
**Areas discussed:** VPP failure mode (SAF-04), 28C chip-ID sequence (SAF-05), Code reuse organization (SAF-04), Test layout (SAF-06), 28C init ordering (SAF-05)

---

## VPP failure mode (SAF-04)

| Option | Description | Selected |
|--------|-------------|----------|
| Match `eprom_check_vpp` exactly | Low VPP = WARNING (proceeds with reduced confidence), High VPP = ERROR. FORCE flag downgrades errors to warnings. Same tolerance bands as v1.0 EPROM path (low: 95% of setpoint, high: setpoint + 500mV). | ✓ |
| Stricter — low VPP = ERROR | Low VPP aborts hard with `RESPONSE_CODE_ERROR` (matches audit wording "aborts with the existing voltage error code"). High VPP still ERROR. FORCE flag still downgrades. Different from eprom path — justified by Intel-flash being the highest-VPP family (12V P1). | |
| Low-only abort, no high check | Only check low-VPP (under-voltage damages the chip via incomplete program). Skip the high check — Intel flash has a built-in SR.VPP-error bit that already detects over-voltage. Minimal code surface. | |

**User's choice:** Match `eprom_check_vpp` exactly
**Notes:** Consistency with the v1.0 verified pattern wins over a strict reading of the audit text. Recorded in CONTEXT.md as D-01: the SAF-06 test must assert that response_code is set (warning or error), not specifically `RESPONSE_CODE_ERROR`, to remain valid under this semantics.

---

## 28C chip-ID sequence (SAF-05)

| Option | Description | Selected |
|--------|-------------|----------|
| Proper AT28C JEDEC sequence | Implement the full Atmel JEDEC chip-id mode: write 0xAA→0x5555, 0x55→0x2AAA, 0x90→0x5555, read mfr at 0x0000 + device at 0x0001, write 0xF0 to exit. Correct for the moment a real chip needs it; ~15 lines + test. | ✓ |
| Reuse `eprom_internal_check_chip_id` | Call the existing UV-EPROM signature-read helper (A9_VPP_ENABLE 12V mode). WRONG for AT28C — applying 12V to A9 may damage 5V EEPROMs. Listed for completeness; reject unless researcher justifies. | |
| Minimal stub — call `flash_intel_check_chip_id`-style | Call `set_data(0, 0x90)` + read 0/1 + `set_data(0, 0xFF)`. Forward-compat placeholder; works on some AT28C parts but not guaranteed JEDEC. Smallest diff; explicit TODO comment for future hardening. | |

**User's choice:** Proper AT28C JEDEC sequence
**Notes:** Forward-compat done right the first time. The chip-id mode is well-documented in the Atmel datasheets; minimal-stub form would create a debug-debt landmine for the next maintainer who hits a real chip. Researcher to confirm the exact magic addresses against the AT28C256 / AT28C64 datasheets during planning.

---

## Code reuse organization (SAF-04)

| Option | Description | Selected |
|--------|-------------|----------|
| Inline-copy into `flash_intel.cpp` | Write a new `flash_intel_check_vpp()` static helper in `flash_intel.cpp` with the regulator-already-on assumption. Mild duplication; zero risk to verified v1.0 `eprom.cpp`. Audit-text-aligned ("1-2 lines in flash_intel.cpp"). | |
| Extract shared helper into `memory_utils` | Pull a `mem_util_check_vpp_low(handle, tolerance_pct)` into `memory_utils.{h,cpp}`; `eprom_check_vpp` + new flash_intel check both call it. DRY but touches verified `eprom.cpp` logic — regression risk for v1.0's 4 working chip families. | |
| Researcher decides | Both shapes are reasonable. Let `gsd-phase-researcher` inspect `eprom_check_vpp`'s actual reuse surface area (hardware-revision guard, FORCE-flag handling, message formatting) and recommend in RESEARCH.md. | ✓ |

**User's choice:** Researcher decides
**Notes:** Decision deferred to RESEARCH.md. Constraint added in CONTEXT.md D-04: whichever path is picked, the 15 existing Unity dispatch tests must remain GREEN unchanged, and the v1.0 functional paths (W27C512 / 29F040 / SST39SF040 / AT28C256) must not regress under Phase 4 hardware validation.

---

## Test layout (SAF-06)

| Option | Description | Selected |
|--------|-------------|----------|
| New test directory per safety check | `test/native/avr/test_flash_intel_vpp/` and `test/native/avr/test_eeprom28c_chip_id/` — separate test binaries with their own setUp/main. Cleaner failure isolation; lets `host_stubs.cpp` stay shared via test_build_src config. Two new dirs. | ✓ |
| Extend existing `test_dispatch` suite | Add SAF-04 and SAF-05 tests to `test_dispatch/test_configure_memory.cpp` alongside the 15 dispatch tests. Single binary; `setUp()` doubles as a mock-reset hook. Risk: the suite drifts from being a 'dispatch test' to a 'mixed test'. | |
| New single `test_safety_checks` directory | Combine both SAF-04 and SAF-05 tests into `test/native/avr/test_safety_checks/test_safety_init.cpp`. One new directory, one binary, ~8-10 test cases total. Logical grouping (both are pre-write-init safety gates). | |

**User's choice:** New test directory per safety check
**Notes:** Per-suite isolation preferred over combined logical grouping. Constraint added in CONTEXT.md D-10: shared `host_stubs.cpp` must remain unedited; per-suite mocking goes in local TUs or via handle function-pointer overrides.

---

## 28C init ordering (SAF-05)

| Option | Description | Selected |
|--------|-------------|----------|
| Before SDP-disable | Order: chip-id check (abort on mismatch) → SDP-disable → blank check. Verify identity BEFORE modifying chip state. Standard 'fail fast' — if we have the wrong chip, don't even try to unlock writes. Matches the `flash_intel` and eprom patterns. | |
| After SDP-disable | Order: SDP-disable → chip-id check → blank check. Some AT28C parts may need SDP cleared before allowing the chip-id mode entry. Trade-off: writes one byte (SDP-disable affects internal state) before the safety check fires. | |
| Researcher decides | Both orderings are defensible. Let `gsd-phase-researcher` consult the Atmel AT28C256 datasheet timing/protocol notes and recommend the safe order. | ✓ |

**User's choice:** Researcher decides
**Notes:** Decision deferred to RESEARCH.md (D-08). Researcher must confirm whether the JEDEC chip-id mode entry requires SDP cleared first or can run on a fresh-from-power-on chip.

---

## Claude's Discretion

The user did not flag these as gray areas; they were not asked. Captured in CONTEXT.md `Claude's Discretion` block:
- Exact insertion line numbers within `flash_intel_write_init` and `eeprom28c_write_init`.
- Whether to introduce a named constant / `byte_flip_t[]` array for the JEDEC unlock bytes (preference: yes, following `EEPROM_SDP_DISABLE` precedent).
- Per-test-suite `setUp` / `tearDown` wiring.
- Whether to add a `flash_intel_check_vpp` declaration to the public `.h` header (only if non-static).
- Test names — descriptive, one assertion per test.

## Deferred Ideas

- Extract `mem_util_check_vpp(...)` as a shared helper if D-04 picks inline-copy now — deferred to v1.2 cleanup if needed.
- Per-cmd VPP check coverage on `flash_intel_erase_execute` (also enables P1_VPP at 12V) — deferred to v1.2.
- Datasheet-variance audit across the full AT28C / AT28BV family — covered only as a researcher note for now.
- Tightening HARDWARE_REVISION REV0 behaviour from "warn and proceed" to hard refusal for Intel-flash — deferred to v1.2.
- Re-running Phase 12 `check_dispatch.py` against the post-SAF-04 firmware — Phase 3 retroactive-verification concern, not Phase 1.

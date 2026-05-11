# Phase 1: Safety Closure (Intel-flash VPP + 28C chip-ID) — Research

**Researched:** 2026-05-11
**Domain:** Arduino C++ firmware safety checks (Intel flash VPP gating + AT28C chip-ID validation) with Unity host-side test coverage
**Confidence:** HIGH for D-04 (read source), HIGH for D-08 (datasheet evidence), HIGH for validation architecture, **HIGH for AT28C JEDEC sequence: CONTEXT.md's proposed sequence is WRONG — datasheets disprove it**

## Summary

CONTEXT.md is unusually load-bearing; this research answers the two deferred decisions (D-04 code organization, D-08 init ordering), supplies the Validation Architecture section the orchestrator greps for, audits the proposed scaffolding for reuse-vs-duplication, and corrects one factual error that CONTEXT.md carries forward.

**The factual correction:** the original Atmel AT28C256 datasheet (Rev. 0006H, 1999) and the current Microchip AT28C64B datasheet (DS20006432B, 2023) both specify chip identification **via raising A9 to 12V** and reading addresses `0x7FC0..0x7FFF` (AT28C256) / `0x1FC0..0x1FFF` (AT28C64). There is no software JEDEC autoselect (`AA→0x5555, 55→0x2AAA, 90→0x5555`) defined for the AT28C family. The proposed CONTEXT.md table is the AMD/SST flash convention, mistakenly attributed to AT28C because those parts happen to share the SDP magic addresses. Implementing the proposed sequence will succeed at issuing the writes (the chip will silently treat them as SDP-style sequence prefix + a write to 0x5555 with data 0x90 — undefined behaviour on AT28C; the chip will likely just start an internal write cycle and never enter any ID mode). Reads at 0x0000/0x0001 will return *array data*, not manufacturer/device codes. The check will compare array bytes against `handle->chip_id` and almost always abort.

**Primary recommendations:**

1. **D-04: inline-copy a static `flash_intel_check_vpp()` into `flash_intel.cpp`.** Do NOT extract a shared helper. The reuse surface is too narrow (one other caller, with control-register branching) and the v1.0 byte-identical regression risk is non-zero. Helper extraction is deferred tech debt, not Phase-1 work.

2. **D-08: chip-id check runs BEFORE SDP-disable** — fail-fast on identity before mutating chip state. Datasheet evidence: SDP disable is an idempotent state-change command sequence the chip *already accepts*; no AT28C variant documents a chip-id mechanism gated on SDP state. Order matches `eprom_generic_init` and `flash_intel_write_init`.

3. **AT28C SAF-05 implementation: the planner must explicitly choose between three options** (none of which match CONTEXT.md's D-05 proposal verbatim):
   - **(A) Implement A9-12V identification** mirroring `eprom_get_chip_id()` (the same hardware sequence the UV-EPROM path uses) — datasheet-correct but reads user-writable tracking bytes, not a fixed JEDEC ID. **Recommended.**
   - **(B) Keep the proposed software JEDEC sequence anyway** — known-incorrect but harmless on chips where `chip_id_value` is never populated, and matches the documented forward-compat-only scope. Will misbehave if anyone actually populates `chip_id_value`. **Not recommended.**
   - **(C) Skip the read entirely and return WARNING when `chip_id > 0`** ("chip-id validation not supported for AT28C family on this firmware"). Most conservative — closes the audit gap by acknowledging it cannot be safely implemented in software-only mode on this chip family. **Acceptable fallback if the planner doesn't want to extend A9_VPP_ENABLE wiring into the 28C path.**

4. **Validation Architecture** uses per-suite mocking via the handle's function pointers (`firestarter_get_data`, `firestarter_set_control_register`) plus per-suite mutable globals for `rurp_read_voltage_mv()`. `host_stubs.cpp` is NOT edited (D-10 contract).

5. **Reuse audit:** drop the proposed `mock_globals.cpp` (overkill — TU-private statics inside each test suite are sufficient). Keep `byte_flip_t` tables only for SAF-04 (it has none; this is moot) and SAF-05 IF the planner picks option (B); if the planner picks option (A) or (C), no JEDEC table is needed. Named constants for magic addresses earn their keep here ONLY because the SDP table's existing `byte_flip_t` rows already inline-write them — adding a third inline-write table is consistent with the project's existing style.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SAF-04 | `flash_intel_write_init` calls `rurp_read_voltage_mv()` and aborts if measured VPP is below `handle->vpp_mv` minus the tolerance window, before issuing the first write command | D-04 recommendation below; mirror `eprom_check_vpp` tolerance bands verbatim (verified at `eprom.cpp:199-232`) |
| SAF-05 | `eeprom_28c.cpp::eeprom28c_write_init` honours `handle->chip_id` when non-zero — performs chip-ID validation matching the UV-EPROM and Intel/AMD-flash paths | D-08 ordering + three implementation options (recommended: A9-12V read mirroring `eprom_get_chip_id`); datasheet evidence below |
| SAF-06 | Unity test on `[env:native]` covers Intel-flash VPP check + 28C chip-ID check; matching/mismatching ID and low/nominal/high VPP exercised | Validation Architecture section below; per-suite mocking via handle function pointers + TU-private statics |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

From `./CLAUDE.md` (meta-repo):
- Repository tracks `.planning/` and `.claude/` only. Firmware sub-repo `firestarter/` is on disk but not committed in this repo. **Implication for planner:** edits to `firestarter/src/proms/*.cpp` are executed against the on-disk sub-repo; commits land there, not in this meta-repo. The planner must make this commit-target boundary explicit in plan tasks.
- Serial protocol changes must be kept in sync between `firestarter_app/firestarter/serial_comm.py` and `firestarter/src/firestarter.cpp`. **Phase 1 does NOT change the wire protocol** (per CONTEXT.md out-of-scope); this constraint is satisfied trivially.
- Constants/flag bits are duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h`. **Phase 1 introduces no new flags or constants on the wire** — the new code reads existing fields (`vpp_mv`, `chip_id`).

From `firestarter/CLAUDE.md`:
- The dispatch order is fixed and load-bearing; Phase 1 edits are *interior to handlers*, not to `configure_memory`'s dispatch — no risk of disturbing the protocol-prefix chain.
- `[env:native]` reuse pattern explicitly states: "drop `test_*.cpp` files under `test/native/avr/<dirname>/`; extend `host_stubs.cpp` only if the new test references additional `rurp_*` symbols". **Phase 1 SAF-06 follows this contract literally — no new `rurp_*` symbols are referenced beyond what `host_stubs.cpp` already provides.**

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01** Intel-flash VPP failure semantics mirror `eprom_check_vpp`: low → `RESPONSE_CODE_WARNING` (proceeds), high → `RESPONSE_CODE_ERROR` (aborts), `FLAG_FORCE` downgrades errors to warnings. Bands: low = `vpp_mv * 95 / 100`, high = `vpp_mv + 500`.
- **D-02** VPP check runs after the regulator is already up (the existing 500ms delay), before the existing chip-ID branch.
- **D-03** Mirror `HARDWARE_REVISION` REV0 guard verbatim from `eprom_check_vpp`.
- **D-05** AT28C chip-ID uses proper JEDEC mode (`AA→0x5555, 55→0x2AAA, 90→0x5555` enter; read 0x0000/0x0001; `F0→0x5555` exit) — **THIS RESEARCH DISPUTES D-05 ON DATASHEET GROUNDS** (see AT28C verification section). The planner must reconcile: keep D-05 as-locked-by-user-but-known-wrong, OR change scope to one of the three alternatives in the AT28C section. **Recommended: planner surfaces this to the user via a /gsd-discuss-phase amendment or accepts (C) skip-and-warn as the conservative path.**
- **D-06** Gate AT28C chip-id check on `handle->chip_id > 0`.
- **D-07** FORCE-flag semantics: `is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR`. Message: `"Chip ID %#04x dont match expected ID %#04x"` verbatim.
- **D-09** Two new test directories: `test_flash_intel_vpp/` and `test_eeprom28c_chip_id/`.
- **D-10** `host_stubs.cpp` is NOT edited; per-suite mocking uses TU-private state or handle function-pointer overrides.
- **D-11** 15 existing dispatch Unity tests in `test_dispatch/test_configure_memory.cpp` remain GREEN unchanged.

### Claude's Discretion

- Exact insertion line numbers within `flash_intel_write_init` and `eeprom28c_write_init`.
- Whether to introduce named constants for JEDEC unlock magic bytes or inline-write them.
- Per-test-suite `setUp` / `tearDown` wiring.
- Whether to add a `flash_intel_check_vpp` declaration to `flash_intel.h` (only needed if external linkage).
- Test names (one assertion per test).

### Deferred Ideas (OUT OF SCOPE)

- Extracting `mem_util_check_vpp(...)` as a shared helper (researcher's D-04 recommendation is "do not extract"; carry forward to v1.2 if desired).
- VPP check on `flash_intel_erase_execute` (only `_write_init` per SAF-04 scope).
- Datasheet variance for rare AT28BV / AT28C17 variants — the override-affected chip set is AT28C256 / AT28C64 / DIP28_2764-pinout chips per the Phase 13 hazard table.
- Tightening REV0 from warn-and-proceed to hard-refuse for Intel-flash 12V path.
- Phase 12 `check_dispatch.py` re-run against post-SAF-04 firmware (Phase 3 concern).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Pre-write VPP ADC compare (SAF-04) | Firmware: `flash_intel.cpp` | — | The ADC is on the RURP shield; the host has no path to read VPP. This must be firmware. |
| AT28C chip-ID validation (SAF-05) | Firmware: `eeprom_28c.cpp` | — | Same reason — chip-ID is read off the data bus by the firmware. Host never sees raw bus data. |
| Test harness for safety checks (SAF-06) | Firmware: `test/native/avr/test_*/` | — | `[env:native]` cross-compiles `src/proms/*.cpp` against host libc + ArduinoFake. Mocking happens via handle function pointers, which are firmware-level. |
| Wire-protocol field carrying expected chip-id (`chip_id`) | Wire JSON: Python emitter → firmware JSON parser | — | Already established by v1.0 (no Phase-1 change). |
| Wire-protocol field carrying expected VPP (`vpp_mv`) | Wire JSON: Python emitter → firmware JSON parser | — | Already established by v1.0 (no Phase-1 change; rename to `vpp_mv` key is Phase-2 / WIRE-01). |

All Phase-1 work is firmware-tier. No host/Python edits.

## D-04 Recommendation (Code organization for SAF-04 VPP check)

**Recommendation: option (a) — inline-copy a static `flash_intel_check_vpp()` helper into `flash_intel.cpp`. DO NOT extract a shared helper.**

### Rationale

I read both `eprom_check_vpp` (eprom.cpp:199-232) and the proposed extraction target `flash_intel_write_init` (flash_intel.cpp:47-62). Three reuse-surface differences make extraction strictly more expensive than its DRY benefit:

**1. The control-register sequencing is fundamentally different.**
- `eprom_check_vpp` itself decides whether to use `REGULATOR | VPE_TO_VPP` (for protocol 0x07/0x08 — VPE through dropping resistor) or `REGULATOR` alone (for protocol 0x0B — direct VPE path), and asserts the bit IT chose. It also clears `REGULATOR | VPE_TO_VPP` at the end of the function (eprom.cpp:231).
- `flash_intel_write_init` has *already* asserted `REGULATOR | P1_VPP_ENABLE` (different bit pattern — 12V routed to P1 socket pin, not VPE-derived) and *already* slept 500ms. It will keep the regulator on through the write pulse.

A shared helper would either:
- (i) need a sequence-selector parameter (regulator-already-on vs. regulator-needs-to-be-asserted, which dropping resistor to use, whether to clear at exit) — three call-site-specific parameters for one shared callee. The conditional-on-parameter shape is worse than two single-purpose functions.
- (ii) require the caller to set up the regulator state before calling and clean it up after — but then `eprom_check_vpp`'s callers would need to be refactored, touching verified v1.0 code.

**2. REV0 guard interaction with regulator state.**
- `eprom_check_vpp`'s REV0 guard returns *before* asserting any regulator bits — safe.
- `flash_intel_write_init`'s REV0 guard would need to return *with the regulator still asserted* (the caller asserted it; the helper can't reach in and clean up). Either the helper does nothing on REV0 (good — same behaviour as eprom path: warn + skip ADC) or it tries to manage regulator state (bad — couples helper to caller's sequence).

The clean shape is: the new `flash_intel_check_vpp()` is a peer to `eprom_check_vpp` with the same shape but different control-register details — not a refactor of `eprom_check_vpp`.

**3. Risk vs. reward.**
- v1.0 dispatch Unity tests (15 tests in `test_dispatch/`) link `eprom.cpp` and assert on dispatch routing, not on `eprom_check_vpp` internals. A refactor that preserves byte-identical behaviour would pass these tests trivially. But:
- v1.0 Phase 03 / 07 hardware verification (W27C512 program path) implicitly depends on the *exact regulator sequencing* in `eprom_check_vpp`. There is no automated test catching a regression here; only physical hardware would catch it (deferred to Phase 4 HW-02).
- The DRY win from extraction is roughly 15 lines of code reduced. The risk is a silent v1.0 regression on the UV-EPROM path that no test in this milestone catches.

**Net judgment:** inline-copy is correct; extraction is premature and risky. If a third VPP-checking handler appears later (e.g. `flash3_write_init`, `flash_intel_erase_execute`), the extraction case strengthens — at that point a phase scoped to the refactor with explicit byte-identical hardware-revalidation is justified.

### Function signature (sketch)

```c
// In firestarter/src/proms/flash_intel.cpp, after line 23, before line 25 (configure_flash_intel).
// Static — no header change needed.
static void flash_intel_check_vpp(firestarter_handle_t* handle) {
    debug("Check VPP (Intel)");
#ifdef HARDWARE_REVISION
    if (rurp_get_hardware_revision() == REVISION_0) {
        firestarter_warning_response("Rev0 dont support reading VPP/VPE");
        return;
    }
#endif
    // Regulator already asserted by flash_intel_write_init; do not toggle it.
    uint16_t vpp_mv = rurp_read_voltage_mv();
#ifdef SERIAL_DEBUG
    debug_format("Checking VPP voltage %u mV", vpp_mv);
#endif
    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {
        int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        firestarter_response_format(response_code, "VPP is high: %u.%uV > %u.%uV",
                                    (vpp_mv + 50) / 1000, (((vpp_mv + 50) / 100) % 10),
                                    (handle->vpp_mv + 50) / 1000, (((handle->vpp_mv + 50) / 100) % 10));
    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {
        firestarter_warning_response_format("VPP is low: %u.%uV < %u.%uV",
                                            (vpp_mv + 50) / 1000, (((vpp_mv + 50) / 100) % 10),
                                            (handle->vpp_mv + 50) / 1000, (((handle->vpp_mv + 50) / 100) % 10));
    }
    // No regulator clear — caller continues to use it.
}
```

### Edit-site diff (sketch)

```diff
 void flash_intel_write_init(firestarter_handle_t* handle) {
     handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 1);
     delay(500);
+    flash_intel_check_vpp(handle);
+    if (handle->response_code == RESPONSE_CODE_ERROR) {
+        return;
+    }
     if (handle->chip_id > 0) {
         flash_intel_check_chip_id(handle);
         if (handle->response_code == RESPONSE_CODE_ERROR) {
             return;
         }
     }
     if (is_flag_set(FLAG_CAN_ERASE) && !is_flag_set(FLAG_SKIP_ERASE)) {
         flash_intel_erase_execute(handle);
     }
     if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
         mem_util_blank_check(handle);
     }
 }
```

Order matches CONTEXT.md "Established Patterns": VPP check then chip-id then proceed (mirrors `eprom_generic_init`).

[VERIFIED: read of `firestarter/src/proms/eprom.cpp:199-232` and `firestarter/src/proms/flash_intel.cpp:47-62`]

## D-08 Recommendation (Chip-id init ordering for SAF-05)

**Recommendation: chip-id check runs BEFORE the SDP-disable sequence.**

### Rationale

Three reasons, in order of evidence weight:

**1. Datasheet does not couple chip-id to SDP state.**

Both the original Atmel AT28C256 datasheet (Rev. 0006H, 1999, page 3) and the current Microchip AT28C64B datasheet (DS20006432B, 2023, section 6.7) describe DEVICE IDENTIFICATION via the A9-12V mechanism without ANY mention of an SDP precondition:

> "DEVICE IDENTIFICATION: An extra 64 bytes of EEPROM memory are available to the user for device identification. By raising A9 to 12V ± 0.5V and using address locations 7FC0H to 7FFFH the additional bytes may be written to or read from in the same manner as the regular memory array." [AT28C256 datasheet, Atmel Rev. 0006H, page 3]

> "6.7 Device Identification: An extra 64 bytes of EEPROM memory are available to the user for device identification. By raising A9 to 12V ± 0.5V and using address locations 1FC0H to 1FFFH, the additional bytes may be written to or read from in the same manner as the regular memory array." [AT28C64B datasheet, Microchip DS20006432B, section 6.7]

SDP is described in separate sections of both datasheets (AT28C256 page 3 "SOFTWARE DATA PROTECTION"; AT28C64B section 6.6.2). SDP gates writes. The identification region is described as readable/writable "in the same manner as the regular memory array" — meaning under the same SDP rules as any other address. Since chip-ID is a **READ**, SDP does not gate it; SDP only inhibits inadvertent **WRITES**.

**Conclusion: ordering is functionally indifferent for the AT28C256/64.** Both orderings work.

**2. Fail-fast is the safer convention even when the chip doesn't enforce it.**

`eprom_generic_init` order: VPP check → chip-id check → (caller proceeds to erase/blank/write). `flash_intel_write_init` order: chip-id check → erase → blank check. Both check identity *before mutating state*. The SDP-disable sequence is a state mutation (the chip transitions out of write-protect). If chip-id mismatches and `FLAG_FORCE` is not set, we ERROR and abort — leaving the chip in its protected state is preferable to leaving it half-unprotected.

**3. Convention alignment with `flash_intel_write_init`.**

Both Phase-1 edits (SAF-04 and SAF-05) should produce structurally identical init bodies:

```
[REGULATOR/SDP/setup]
[VPP check if applicable]   ← SAF-04 (no analogue in 28C — 28C is 5V-only)
[chip-id check if > 0]
[erase if applicable]
[blank check]
```

For SAF-05 specifically:

```diff
 void eeprom28c_write_init(firestarter_handle_t* handle) {
+    // Chip-id check FIRST — fail fast on identity before mutating chip state.
+    if (handle->chip_id > 0) {
+        eeprom28c_check_chip_id(handle);  // see SAF-05 section below for body
+        if (handle->response_code == RESPONSE_CODE_ERROR) {
+            return;
+        }
+    }
     flash_execute_command(EEPROM_SDP_DISABLE);
     if (!eeprom28c_wait_for_write(handle, 0x5555, 0x20)) {
         return;
     }
     if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
         mem_util_blank_check(handle);
     }
 }
```

### Why NOT after SDP-disable

CONTEXT.md hypothesized "some AT28C parts may need SDP cleared before chip-id mode entry". This hypothesis is unsupported by the AT28C256 and AT28C64B datasheets, and would only become relevant for rare AT28BV/AT28C17 variants that are not in scope per CONTEXT.md "Deferred Ideas". Choosing the after-SDP order based on an unverified hypothesis would mean a chip-id mismatch leaves the chip with SDP cleared — a strictly worse safety posture.

[VERIFIED: Atmel AT28C256 datasheet Rev. 0006H, page 3, extracted via pypdf from eater.net mirror; Microchip AT28C64B datasheet DS20006432B section 6.7, extracted from microchip.com PDF]

## AT28C JEDEC sequence verification

**Result: CONTEXT.md's proposed sequence is WRONG. The AT28C family has no software JEDEC autoselect mode.**

### Evidence

| Source | Date | Quote on identification mechanism |
|--------|------|-------------------------------------|
| Atmel AT28C256, Rev. 0006H | 12/1999 | "DEVICE IDENTIFICATION: An extra 64 bytes of EEPROM memory are available to the user for device identification. By raising A9 to 12V ± 0.5V and using address locations 7FC0H to 7FFFH the additional bytes may be written to or read from in the same manner as the regular memory array." |
| Microchip AT28C64B, DS20006432B | 2020-2023 | "6.7 Device Identification: An extra 64 bytes of EEPROM memory are available to the user for device identification. By raising A9 to 12V ± 0.5V and using address locations 1FC0H to 1FFFH..." |
| AT28C256 datasheet body (full read) | 1999 | No `0x90` autoselect command anywhere in the chip command set. Only command sequences are SDP enable (`AA/55/A0`), SDP disable (`AA/55/80, AA/55/20`), and the optional 6-byte chip erase. |

### What the proposed CONTEXT.md sequence actually does

If a planner implements `AA→0x5555, 55→0x2AAA, 90→0x5555` on an AT28C256, the chip will:
1. Treat the first two writes as the prefix of an SDP enable/disable command sequence (it shares the magic addresses).
2. The third write (`0x90 → 0x5555`) does not match any documented SDP command opcode (`A0` enable, `80` disable-start, `20` disable-finish, `10` chip-erase-finish). The chip will either:
   - (a) Treat it as an ordinary byte write to address 0x5555 with data 0x90 and start a `tWC` write cycle (with SDP-disabled), OR
   - (b) Treat it as an undefined-opcode no-op (SDP-enabled, write inhibited).
3. The subsequent reads at 0x0000/0x0001 return array data (whatever's stored there) — not manufacturer/device codes.

Outcome: `chip_id != handle->chip_id` will almost certainly compare false, ERROR fires, write aborts. **Vacuously safe** (the chip didn't get programmed) but functionally useless — and now `address 0x5555` is silently corrupted with 0x90 if the chip was SDP-disabled at the time of the write.

### Three options for SAF-05

#### Option (A) — A9-12V identification, mirroring `eprom_get_chip_id()` [RECOMMENDED]

The firmware already implements A9-12V identification for UV-EPROM at `eprom.cpp:186-197`:

```c
uint16_t eprom_get_chip_id(firestarter_handle_t* handle) {
    handle->firestarter_set_control_register(handle, REGULATOR, 1);
    delay(50);
    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE, 1);
    delay(100);
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= (handle->firestarter_get_data(handle, 0x0001));
    handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE, 0);
    return chip_id;
}
```

For AT28C256, the read addresses would be `0x7FC0` and `0x7FC1` (manufacturer/device locations within the upper 64-byte identification block). For AT28C64, `0x1FC0` and `0x1FC1`.

**Caveat:** the upper 64 bytes are **user-writable tracking memory**, not factory-programmed manufacturer/device codes. So `chip_id_value` in the DB represents *what the user/manufacturer wrote there at programming time*. For factory-fresh AT28C256 parts, these bytes are likely 0xFF (erased state). This means the check is **functionally useful only for chips that have been pre-marked**, which is a niche.

But: it's the ONLY datasheet-correct hardware ID path for these parts. And it costs the AT28C-family handler nothing extra — A9_VPP_ENABLE wiring already exists in the firmware.

**Recommended planner action:** implement option (A). Document in the SAF-05 task SUMMARY.md that the check validates *user-writable identification bytes*, not a fixed JEDEC code, and that DB entries can only populate `chip_id_value` for pre-marked AT28C parts. This satisfies REQ-SAF-02 forward-compat semantically (the check exists; it runs when `chip_id > 0`; it aborts on mismatch).

#### Option (B) — Implement the proposed software JEDEC sequence anyway

Strictly worse than (A) — known-incorrect protocol that will silently corrupt address 0x5555 of a SDP-disabled chip with a stray write of 0x90. The only argument for (B) is that it matches D-05 as locked in CONTEXT.md and produces "no chip programmed on mismatch" (which is true, but for the wrong reason). **Not recommended.**

#### Option (C) — Skip the read; return WARNING when `chip_id > 0`

Most conservative. If `handle->chip_id > 0`, emit `firestarter_warning_response("AT28C chip-id validation unavailable; proceeding without ID check")` and continue. Honest about firmware capability; closes audit-text "REQ-SAF-02 holds" only loosely (the field is acknowledged, not validated). **Acceptable fallback if planner doesn't want to add a new code path. Suggest only if planner wants to ship Phase 1 fast.**

### Variants check (per CONTEXT.md request)

| Chip family | Identification | Datasheet evidence | Notes |
|-------------|----------------|---------------------|-------|
| AT28C256 | A9-12V, 7FC0H-7FFFH | Atmel Rev. 0006H | Direct read; user-writable region |
| AT28C64 / AT28C64B | A9-12V, 1FC0H-1FFFH | Microchip DS20006432B | Same mechanism, lower address range |
| AT28C16 / AT28C17 | A9-12V (presumed) | Not verified in this research | Likely same family pattern; not in Phase 13 override set |
| AT28HC256 | A9-12V (per Microchip product page) | Not deeply verified | Functionally compatible |
| X28C256 (Xicor) | JEDEC pinout compatible; identification not deeply verified | — | Different vendor; may have own ID mechanism. Not in Phase 13 override set. |
| CAT28C256 (Catalyst / ON Semi) | Likely A9-12V (family-compatible) | Not verified | Not in Phase 13 override set. |
| AT28BV variants | Unknown | Not verified | Deferred per CONTEXT.md "Deferred Ideas". |

**For the Phase 13 override set (the 23 chips in `_28C_EEPROM_HAZARD_PINOUT` table)** — all are AT28C256 / AT28C64 / AT28C-family. Option (A) (A9-12V mechanism) covers them all uniformly.

[VERIFIED: AT28C256 Atmel datasheet Rev. 0006H 12/99 from eater.net mirror; AT28C64B Microchip datasheet DS20006432B from microchip.com; firmware code `firestarter/src/proms/eprom.cpp:186-197`]

## Validation Architecture

This section is the source of truth for the Phase-1 VALIDATION.md the planner will derive. `workflow.nyquist_validation` is absent from `.planning/config.json`; per orchestrator convention (absent = enabled), this section is required.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Unity (PlatformIO `test_framework = unity`) + ArduinoFake@^0.4.0 |
| Config file | `firestarter/platformio.ini` `[env:native]` block (no changes needed) |
| Quick run command (all native) | `cd firestarter && pio test -e native` |
| Quick run command (Phase 1 only) | `cd firestarter && pio test -e native -f "*test_flash_intel_vpp*" -f "*test_eeprom28c_chip_id*"` |
| Regression run command (dispatch) | `cd firestarter && pio test -e native -f "*test_dispatch*"` |
| Full suite command | `cd firestarter && pio test -e native` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SAF-04 | Intel-flash VPP nominal — measured ≈ setpoint, no response_code change | unit | `pio test -e native -f "*test_flash_intel_vpp*"` (assertion: `test_flash_intel_vpp_nominal_proceeds`) | ❌ Wave 0 |
| SAF-04 | Intel-flash VPP low (< 95% of setpoint) — warning response, no error | unit | same suite, `test_flash_intel_low_vpp_warns` | ❌ Wave 0 |
| SAF-04 | Intel-flash VPP high (> setpoint + 500mV) — error response, write aborts | unit | same suite, `test_flash_intel_high_vpp_errors` | ❌ Wave 0 |
| SAF-04 | FORCE-flag downgrades high-VPP error to warning | unit | same suite, `test_flash_intel_high_vpp_with_force_warns` | ❌ Wave 0 |
| SAF-04 | REV0 hardware skips ADC compare and warns | unit (only if `HARDWARE_REVISION` defined for [env:native] — it is, per platformio.ini) | same suite, `test_flash_intel_rev0_skips_vpp_check` | ❌ Wave 0 |
| SAF-05 | Matching chip-id proceeds (response_code unchanged after init) | unit | `pio test -e native -f "*test_eeprom28c_chip_id*"` (assertion: `test_eeprom28c_matching_chip_id_proceeds`) | ❌ Wave 0 |
| SAF-05 | Mismatching chip-id errors (response_code = RESPONSE_CODE_ERROR) | unit | same suite, `test_eeprom28c_mismatching_chip_id_errors` | ❌ Wave 0 |
| SAF-05 | `chip_id == 0` skips the check entirely (no read attempted) | unit | same suite, `test_eeprom28c_zero_chip_id_skips_check` | ❌ Wave 0 |
| SAF-05 | FORCE-flag downgrades mismatch error to warning | unit | same suite, `test_eeprom28c_mismatching_chip_id_with_force_warns` | ❌ Wave 0 |
| SAF-06 (regression guard) | 15 pre-existing dispatch tests still pass | unit | `pio test -e native -f "*test_dispatch*"` (assertion: 15/15 GREEN, byte-identical output to pre-Phase-1) | ✅ exists |

**Coverage cases per check:**

- **SAF-04 VPP (4 active cases + REV0):** nominal / low / high / FORCE-high-warn / REV0-skip. This is the minimum to prove all four arms of the conditional (`> high`, `< low`, `else` proceed, FORCE flag, REV0 guard). Adding "exactly-at-tolerance-edge" cases is overkill — the eprom path doesn't have them either; the boundaries are integer-arithmetic comparisons with no fuzzy regions.
- **SAF-05 chip-id (3 active cases + chip_id=0):** matching / mismatching / FORCE-mismatch-warn / chip_id=0-skipped. Same minimum-coverage logic. If the planner picks option (A) (A9-12V), no extra test is needed because the mocking happens at the `firestarter_get_data` callback layer — the test doesn't care whether 0x0000/0x0001 or 0x7FC0/0x7FC1 are read, it cares about the bytes the mock returns.

**Sampling rate (Nyquist):**
- **Per task commit:** quick run of the suite the task edits (`pio test -e native -f "*test_<suite>*"`).
- **Per wave merge:** full native suite (`pio test -e native`) — all 15 dispatch tests + new Phase-1 tests GREEN.
- **Phase gate:** full native suite green before `/gsd-verify-work`.

### Mocking approach (per-suite, NOT shared)

**Constraint (D-10):** `host_stubs.cpp` is shared with the dispatch suite and must not be edited.

**Approach:** each new test directory contains:
- `test_<name>.cpp` — Unity test bodies + Unity `main()`.
- TU-private static globals for any mutable mock state (e.g. `static uint16_t s_mock_vpp_mv = 0;`).
- TU-private static C functions that match the handle's function-pointer signatures.

Each test body sets up its own state:
```c
// In test_flash_intel_vpp.cpp
static uint16_t s_mock_vpp_mv = 0;

// PlatformIO will link this TU; it provides a stronger definition of
// rurp_read_voltage_mv than host_stubs.cpp's (which returns 0).
// WAIT — actually this causes a multiple-definition link error. Use the
// handle's function pointer to inject mocks INSTEAD of overriding rurp_*.
```

**Correction — the right shape:** `rurp_read_voltage_mv()` is a free function, not a handle method, so we CANNOT override it via the function-pointer mechanism. We have two options:

**Option M1 — link-time strong override (per-suite TU).** Each new test suite directory is its own PIO test runner; PIO compiles the `test_*/` directory's files plus `src_filter = +<proms/>`. But `host_stubs.cpp` lives under `test/native/avr/test_dispatch/`, which means PIO's *per-suite* discovery does NOT pull it into a different `test_*/` directory's binary. **This is the load-bearing insight:** under PIO, each test directory under `test/` builds its own independent test binary. So `test_flash_intel_vpp/` can ship its OWN host_stubs that provides a different `rurp_read_voltage_mv()` returning `s_mock_vpp_mv`, with `setUp()` clearing the value.

This is the recommended shape:

```
test/native/avr/
├── test_dispatch/                  (existing — UNCHANGED, owns its host_stubs.cpp)
│   ├── test_configure_memory.cpp
│   ├── host_stubs.cpp
│   └── avr/pgmspace.h
├── test_flash_intel_vpp/           (new — Phase 1)
│   ├── test_flash_intel_vpp.cpp
│   ├── host_stubs.cpp              (suite-local; provides mockable rurp_read_voltage_mv)
│   └── avr/pgmspace.h              (copy of the dispatch suite's shim — or symlink)
└── test_eeprom28c_chip_id/         (new — Phase 1)
    ├── test_eeprom28c_chip_id.cpp
    ├── host_stubs.cpp              (suite-local; provides mockable firestarter_get_data hooks via the handle)
    └── avr/pgmspace.h              (same)
```

Each new `host_stubs.cpp` is suite-local and not shared. The dispatch suite's `host_stubs.cpp` remains byte-identical (D-10 satisfied).

The suite-local `host_stubs.cpp` for `test_flash_intel_vpp/` provides:

```c
// Same content as test_dispatch/host_stubs.cpp EXCEPT rurp_read_voltage_mv:
static uint16_t s_mock_vpp_mv = 0;
extern "C" void set_mock_vpp_mv(uint16_t mv) { s_mock_vpp_mv = mv; }
extern "C" uint16_t rurp_read_voltage_mv() { return s_mock_vpp_mv; }
```

Then test bodies call `set_mock_vpp_mv(12700);` before invoking the init function.

**Option M2 — handle function-pointer overrides (for SAF-05 only).** The chip-id read uses `handle->firestarter_get_data(handle, address)` — a function pointer ON the handle. This means SAF-05 mocks are *trivial*: the test sets `handle->firestarter_get_data = my_test_specific_fn;` and that function returns a scripted byte sequence. No host_stubs change required; no link-time tricks. Use Option M2 for SAF-05.

**Summary of the mocking strategy:**

| What to mock | Mechanism | Lives in |
|--------------|-----------|----------|
| `rurp_read_voltage_mv()` (SAF-04) | Strong link-time override in suite-local `host_stubs.cpp` + TU-private mutable `s_mock_vpp_mv` | `test/native/avr/test_flash_intel_vpp/host_stubs.cpp` |
| `handle->firestarter_get_data` (SAF-05) | Set the function pointer on the handle to a TU-private static function | `test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp` |
| `handle->firestarter_set_control_register` (both) | Set the function pointer on the handle to a TU-private static no-op (or recorder) | both new `test_*.cpp` files |
| `rurp_get_hardware_revision()` (SAF-04 REV0 case) | Strong link-time override in suite-local `host_stubs.cpp` + TU-private `s_mock_hw_rev` | suite-local `host_stubs.cpp` |

**No `mock_globals.cpp` is needed.** TU-private statics in each suite-local `host_stubs.cpp` or `test_*.cpp` are sufficient — see Reuse Audit below.

### Wave 0 Gaps

- [ ] `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` — SAF-04 unit tests
- [ ] `firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp` — suite-local stubs with mockable `rurp_read_voltage_mv` and `rurp_get_hardware_revision`
- [ ] `firestarter/test/native/avr/test_flash_intel_vpp/avr/pgmspace.h` — copy or symlink of `test_dispatch/avr/pgmspace.h`
- [ ] `firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp` — SAF-05 unit tests
- [ ] `firestarter/test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp` — suite-local stubs (functionally identical to dispatch suite's; no mocking needed because mocks happen via handle function pointers)
- [ ] `firestarter/test/native/avr/test_eeprom28c_chip_id/avr/pgmspace.h` — copy of `test_dispatch/avr/pgmspace.h`

**Regression guard:** the existing `test_dispatch/test_configure_memory.cpp` (15 RUN_TESTs in `main`) must remain byte-identical and stay GREEN. The planner's verification step must include `pio test -e native -f "*test_dispatch*"` showing 15/15 PASS with no test names altered, no new tests added or removed.

## Reuse vs Duplication Audit

Per the memory note `Drop proposed scaffolding if not strictly needed`, I challenge each piece of scaffolding CONTEXT.md proposes:

| Proposed scaffolding | CONTEXT.md location | Verdict | Rationale |
|---------------------|---------------------|---------|-----------|
| `mock_globals.cpp` (new TU colocated with each suite) | D-10 last paragraph | **DROP** | TU-private `static` variables inside each suite's own `host_stubs.cpp` or `test_*.cpp` are simpler and locally-scoped. A separate `mock_globals.cpp` would need to be linked into both suites' binaries; since each PIO test directory is its own binary anyway, there's no sharing benefit. The recommended shape (suite-local `host_stubs.cpp` per directory) gives each suite exactly the mocks it needs with zero cross-suite coupling. |
| Named constant for JEDEC unlock magic bytes (e.g. `EEPROM_28C_AUTOSELECT_ENTER[]`) | Discretion / D-05 | **DROP if planner picks Option A or C; KEEP if planner picks Option B** | If A or C: no JEDEC sequence is implemented — the constant has no callsite. If B: yes, follow project convention (the existing `EEPROM_SDP_DISABLE[]` shows the project's style). |
| `byte_flip_t[]` table for chip-id sequence | Specifics / D-05 | **DROP if A or C; KEEP if B** | Same reasoning. |
| Helper extraction `mem_util_check_vpp_low(...)` in `memory_utils.{h,cpp}` | D-04 option (b) | **DROP** | See D-04 recommendation — extraction is deferred tech debt, not Phase-1 work. |
| New declaration in `flash_intel.h` for `flash_intel_check_vpp` | Discretion | **DROP** | The helper is `static` in `flash_intel.cpp`; internal linkage means no header declaration is needed. |
| Helper function `eeprom28c_check_chip_id(handle)` in `eeprom_28c.cpp` | Implicit in D-05 implementation | **KEEP** | This one earns its keep — the SAF-05 logic is ≥10 lines of register sequencing + read + compare + response formatting; inlining it into `eeprom28c_write_init` would obscure the init flow. Make it `static`, no header change. |
| Header for "byte_flip_t" / extending `flash_utils.h` for chip-id constants | implicit | **DROP** | The `byte_flip_t` type and `flash_execute_command` macro already live in `flash_utils.h:19-22`; reuse them in-place if Option B is chosen. No header growth. |

**Net scaffolding actually shipped under recommended path (D-04 inline + D-05 Option A):**
- 1 new static function in `flash_intel.cpp` (`flash_intel_check_vpp`)
- 1 new static function in `eeprom_28c.cpp` (`eeprom28c_check_chip_id` reading via A9-12V mirroring `eprom_get_chip_id`)
- 2 new test directories with: `test_*.cpp`, suite-local `host_stubs.cpp`, `avr/pgmspace.h` shim each (6 new files total under `test/native/avr/`).
- 0 new header changes.
- 0 new `mock_globals.cpp` files.
- 0 named-constant tables (Option A path doesn't use them).

## Code Examples

### SAF-04 — Intel-flash VPP check function

```c
// Source: firestarter/src/proms/eprom.cpp:199-232 (mirror); adapted for flash_intel.cpp
// Placement: firestarter/src/proms/flash_intel.cpp, after the forward declarations (line 23).
static void flash_intel_check_vpp(firestarter_handle_t* handle) {
    debug("Check VPP (Intel)");
#ifdef HARDWARE_REVISION
    if (rurp_get_hardware_revision() == REVISION_0) {
        firestarter_warning_response("Rev0 dont support reading VPP/VPE");
        return;
    }
#endif
    // Caller (flash_intel_write_init) already asserted REGULATOR | P1_VPP_ENABLE
    // and delayed 500ms; do not toggle the regulator here.
    uint16_t vpp_mv = rurp_read_voltage_mv();
#ifdef SERIAL_DEBUG
    debug_format("Checking VPP voltage %u mV", vpp_mv);
#endif
    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {
        int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        firestarter_response_format(response_code, "VPP is high: %u.%uV > %u.%uV",
                                    (vpp_mv + 50) / 1000, (((vpp_mv + 50) / 100) % 10),
                                    (handle->vpp_mv + 50) / 1000, (((handle->vpp_mv + 50) / 100) % 10));
    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {
        firestarter_warning_response_format("VPP is low: %u.%uV < %u.%uV",
                                            (vpp_mv + 50) / 1000, (((vpp_mv + 50) / 100) % 10),
                                            (handle->vpp_mv + 50) / 1000, (((handle->vpp_mv + 50) / 100) % 10));
    }
}
```

### SAF-05 — AT28C chip-ID check (Option A, A9-12V mirroring eprom_get_chip_id)

```c
// Source: firestarter/src/proms/eprom.cpp:186-197 (mirror eprom_get_chip_id);
// firestarter/src/proms/flash_intel.cpp:115-124 (mirror compare + format).
// Placement: firestarter/src/proms/eeprom_28c.cpp, before eeprom28c_write_init.
//
// READ ADDRESSES: AT28C256 has identification at 0x7FC0/0x7FC1 (upper 64 bytes); AT28C64 at
// 0x1FC0/0x1FC1. Because handle->mem_size tells us which family this is, we can pick the right
// address dynamically: use (mem_size - 64) for manufacturer, (mem_size - 63) for device.
// Caveat: these bytes are user-writable tracking memory, NOT factory-programmed JEDEC codes.
// The check only matches chips that have been pre-marked with the expected chip_id_value.
static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {
    debug("Check chip ID (28C)");
    handle->firestarter_set_control_register(handle, REGULATOR, 1);
    delay(50);
    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE, 1);
    delay(100);
    uint32_t mfr_addr = handle->mem_size - 64;       // 0x7FC0 for AT28C256, 0x1FC0 for AT28C64
    uint16_t chip_id = handle->firestarter_get_data(handle, mfr_addr) << 8;
    chip_id |= handle->firestarter_get_data(handle, mfr_addr + 1);
    handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE, 0);
    if (chip_id != handle->chip_id) {
        int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        firestarter_response_format(response_code, "Chip ID %#04x dont match expected ID %#04x", chip_id, handle->chip_id);
    }
}
```

**Planner decision point:** address calculation `mem_size - 64` correctly gives 0x7FC0 for a 32 KiB part (mem_size = 32768 = 0x8000) and 0x1FC0 for an 8 KiB part (mem_size = 8192 = 0x2000). For other AT28C sizes it generalizes naturally. **If `mem_size` is set by the host's `memory-size` JSON field**, this is robust; verify by reading `firestarter/src/json_parser.c` during planning.

### SAF-06 — test layout for SAF-04 (sketch)

```c
// firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

extern "C" {
#include "flash_intel.h"
#include "memory.h"
}
#include "firestarter.h"

using namespace fakeit;

// Declared in this suite's host_stubs.cpp; used to inject mock VPP readings.
extern "C" void set_mock_vpp_mv(uint16_t mv);
extern "C" void set_mock_hw_rev(uint8_t rev);

static void mock_set_ctrl_reg(struct firestarter_handle*, rurp_register_t, bool) {}
static bool mock_get_ctrl_reg(struct firestarter_handle*, rurp_register_t) { return 0; }
static void mock_set_data(struct firestarter_handle*, uint32_t, uint8_t) {}
static uint8_t mock_get_data(struct firestarter_handle*, uint32_t) { return 0xFF; }

void setUp(void) {
    ArduinoFakeReset();
    set_mock_vpp_mv(0);
    set_mock_hw_rev(1);  // non-REV0 by default
}
void tearDown(void) {}

static firestarter_handle_t make_intel_handle(uint16_t vpp_setpoint, uint32_t ctrl_flags) {
    firestarter_handle_t h = {};
    h.protocol = 0x10;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.vpp_mv = vpp_setpoint;
    h.ctrl_flags = ctrl_flags;
    h.chip_id = 0;  // skip chip-id branch
    h.ctrl_flags |= FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE;
    h.firestarter_set_control_register = mock_set_ctrl_reg;
    h.firestarter_get_control_register = mock_get_ctrl_reg;
    h.firestarter_set_data = mock_set_data;
    h.firestarter_get_data = mock_get_data;
    return h;
}

void test_flash_intel_vpp_nominal_proceeds(void) {
    firestarter_handle_t h = make_intel_handle(12000, 0);
    set_mock_vpp_mv(12000);
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_flash_intel_low_vpp_warns(void) {
    firestarter_handle_t h = make_intel_handle(12000, 0);
    set_mock_vpp_mv(11000);  // < 12000 * 95 / 100 = 11400
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_WARNING, h.response_code);
}

void test_flash_intel_high_vpp_errors(void) {
    firestarter_handle_t h = make_intel_handle(12000, 0);
    set_mock_vpp_mv(12700);  // > 12000 + 500
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_flash_intel_high_vpp_with_force_warns(void) {
    firestarter_handle_t h = make_intel_handle(12000, FLAG_FORCE);
    set_mock_vpp_mv(12700);
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_WARNING, h.response_code);
}

void test_flash_intel_rev0_skips_vpp_check(void) {
    firestarter_handle_t h = make_intel_handle(12000, 0);
    set_mock_hw_rev(0);  // REVISION_0
    set_mock_vpp_mv(99999);  // would error if check ran
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

int main(int, char**) {
    UNITY_BEGIN();
    RUN_TEST(test_flash_intel_vpp_nominal_proceeds);
    RUN_TEST(test_flash_intel_low_vpp_warns);
    RUN_TEST(test_flash_intel_high_vpp_errors);
    RUN_TEST(test_flash_intel_high_vpp_with_force_warns);
    RUN_TEST(test_flash_intel_rev0_skips_vpp_check);
    return UNITY_END();
}
```

Suite-local `host_stubs.cpp` differs from `test_dispatch/host_stubs.cpp` only by replacing the no-op `rurp_read_voltage_mv` and `rurp_get_hardware_revision`:

```c
// firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp
// (Otherwise byte-identical to test_dispatch/host_stubs.cpp.)
static uint16_t s_mock_vpp_mv = 0;
static uint8_t s_mock_hw_rev = 1;

extern "C" void set_mock_vpp_mv(uint16_t mv) { s_mock_vpp_mv = mv; }
extern "C" uint8_t set_mock_hw_rev(uint8_t r) { s_mock_hw_rev = r; return r; }

extern "C" uint16_t rurp_read_voltage_mv() { return s_mock_vpp_mv; }
#ifdef HARDWARE_REVISION
extern "C" uint8_t rurp_get_hardware_revision() { return s_mock_hw_rev; }
#endif
// ... all other stubs copied verbatim from test_dispatch/host_stubs.cpp ...
```

### SAF-06 — test layout for SAF-05 (sketch, Option A path)

```c
// firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp
// Uses the handle's firestarter_get_data function pointer to inject mock bytes —
// no rurp_* override needed; suite-local host_stubs.cpp is functionally identical
// to test_dispatch/host_stubs.cpp (just lives in its own directory so PIO links it).
//
// Scripted byte sequence: the test sets a TU-private static array; mock_get_data
// returns array[call_index++].

static uint8_t s_mock_bytes[16];
static int s_mock_byte_idx;

static uint8_t mock_get_data_scripted(struct firestarter_handle*, uint32_t /*addr*/) {
    if (s_mock_byte_idx < 16) return s_mock_bytes[s_mock_byte_idx++];
    return 0xFF;
}

void setUp(void) {
    ArduinoFakeReset();
    s_mock_byte_idx = 0;
    memset(s_mock_bytes, 0xFF, sizeof(s_mock_bytes));
}

static firestarter_handle_t make_28c_handle(uint16_t expected_chip_id, uint32_t ctrl_flags) {
    firestarter_handle_t h = {};
    h.protocol = 0x0D;
    h.cmd = CMD_WRITE;
    h.mem_size = 32768;  // AT28C256
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = expected_chip_id;
    h.ctrl_flags = ctrl_flags | FLAG_SKIP_BLANK_CHECK;
    h.firestarter_set_control_register = mock_set_ctrl_reg;
    h.firestarter_get_control_register = mock_get_ctrl_reg;
    h.firestarter_set_data = mock_set_data;
    h.firestarter_get_data = mock_get_data_scripted;
    return h;
}

void test_eeprom28c_matching_chip_id_proceeds(void) {
    firestarter_handle_t h = make_28c_handle(0x1F08, 0);
    // First two bytes of script become the chip-id read (manufacturer then device)
    s_mock_bytes[0] = 0x1F;  // Atmel manufacturer
    s_mock_bytes[1] = 0x08;  // AT28C256 device (sentinel value; real value varies)
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_eeprom28c_mismatching_chip_id_errors(void) {
    firestarter_handle_t h = make_28c_handle(0x1F08, 0);
    s_mock_bytes[0] = 0xDE;
    s_mock_bytes[1] = 0xAD;
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

void test_eeprom28c_zero_chip_id_skips_check(void) {
    firestarter_handle_t h = make_28c_handle(0, 0);  // chip_id == 0, check should NOT run
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
    TEST_ASSERT_EQUAL(0, s_mock_byte_idx);  // no data reads happened
}

void test_eeprom28c_mismatching_chip_id_with_force_warns(void) {
    firestarter_handle_t h = make_28c_handle(0x1F08, FLAG_FORCE);
    s_mock_bytes[0] = 0xDE;
    s_mock_bytes[1] = 0xAD;
    configure_memory(&h);
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_WARNING, h.response_code);
}

int main(int, char**) {
    UNITY_BEGIN();
    RUN_TEST(test_eeprom28c_matching_chip_id_proceeds);
    RUN_TEST(test_eeprom28c_mismatching_chip_id_errors);
    RUN_TEST(test_eeprom28c_zero_chip_id_skips_check);
    RUN_TEST(test_eeprom28c_mismatching_chip_id_with_force_warns);
    return UNITY_END();
}
```

## Common Pitfalls

### Pitfall 1: Multiple-definition link errors when overriding `rurp_*` symbols
**What goes wrong:** A new TU defining `rurp_read_voltage_mv` conflicts with `test_dispatch/host_stubs.cpp`'s definition.
**Why it happens:** Confusing PIO's single-binary-per-suite model with a single-binary-for-all-suites model. PIO builds one test binary PER `test/<dirname>/` directory.
**How to avoid:** each new test directory has its own `host_stubs.cpp` (suite-local). The dispatch suite's stubs live in its own dir and stay byte-identical.
**Warning signs:** `multiple definition of 'rurp_read_voltage_mv'` at link time.

### Pitfall 2: Forgetting `configure_memory()` dispatch before calling the init function
**What goes wrong:** Tests call `flash_intel_write_init(&h)` directly without first calling `configure_memory(&h)`, so `handle->firestarter_set_control_register` is still pointing at the test's mock (good), but the test bypasses the dispatch wiring that v1.0 dispatch tests verify.
**Why it happens:** It feels natural to "just call the init function."
**How to avoid:** Always call `configure_memory(&h);` then `h.firestarter_operation_init(&h);`. This (a) verifies dispatch still routes correctly under the new code, (b) matches how the firmware actually runs in production.
**Warning signs:** Test passes but doesn't actually exercise the production code path.

### Pitfall 3: Test asserting on `RESPONSE_CODE_ERROR` specifically when WARNING is intended
**What goes wrong:** The low-VPP path emits `RESPONSE_CODE_WARNING` (warning, proceeds), not `RESPONSE_CODE_ERROR`. A test using `TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, ...)` for the low-VPP case fails.
**Why it happens:** CONTEXT.md §D-01 explicitly says "SAF-06 test phrasing 'low-VPP path returns the voltage error code' refers to the existing voltage-error reporting infrastructure (firestarter_warning_response_format is part of the same response family)". The test must assert on `RESPONSE_CODE_WARNING` for low-VPP, NOT `RESPONSE_CODE_ERROR`.
**How to avoid:** Per-case assertion: low→`WARNING`, high→`ERROR`, high+FORCE→`WARNING`, nominal→`OK` unchanged.
**Warning signs:** Test name says "low_vpp_warns" but assertion is `ERROR`.

### Pitfall 4: AT28C `mem_size` not set in the handle when `eeprom28c_check_chip_id` runs
**What goes wrong:** The recommended Option A code calculates the identification-region address from `handle->mem_size - 64`. If a test forgets to set `mem_size`, the address is `0 - 64 = 0xFFFFFFFFFFFFFFC0`, which the mock data reads at — undefined behavior in production hardware, weird test failure.
**Why it happens:** `mem_size` is set by the host's `memory-size` JSON field; if a unit-test handle is hand-built minimally, it's zero by default.
**How to avoid:** Test helper `make_28c_handle()` sets `mem_size = 32768` explicitly. Production: `firestarter/src/json_parser.c` populates `mem_size` for every chip; verify during planning.
**Warning signs:** Test reads return wrong bytes; production hardware reads cause bus errors.

### Pitfall 5: Forgetting `FLAG_SKIP_BLANK_CHECK` in tests, causing tests to enter `mem_util_blank_check()` and time out
**What goes wrong:** `flash_intel_write_init` and `eeprom28c_write_init` call `mem_util_blank_check` at the end if `FLAG_SKIP_BLANK_CHECK` is not set. The blank-check loops over the entire chip reading bytes — under the test mock, it'll read whatever `mock_get_data` returns; if that's 0xFF for the entire mem_size, blank check passes; otherwise it reports a non-blank chip and the test sees an unexpected response_code.
**Why it happens:** The blank-check is wired into the init flow; tests focused on VPP/chip-id might overlook it.
**How to avoid:** Every test handle sets `FLAG_SKIP_BLANK_CHECK`. Also set `FLAG_SKIP_ERASE` for Intel-flash (otherwise the erase path runs against the mock).
**Warning signs:** Test response_code is unexpected (e.g. error after a "should-proceed" path); test runtime is longer than expected.

### Pitfall 6: Silently breaking the 15 dispatch tests by editing `eprom.cpp` for the helper-extract path
**What goes wrong:** Following D-04 option (b) and refactoring `eprom_check_vpp` to call a shared helper introduces a subtle behavioural change (e.g. extra debug call, different regulator-clear sequence) that the 15 dispatch tests don't catch (they assert on dispatch routing, not init behaviour) — but Phase 4 HW-02 catches it weeks later.
**Why it happens:** The dispatch tests are a regression guard for dispatch, not for handler internals. The handler internals are guarded by physical hardware tests that haven't been run since v1.0.
**How to avoid:** Pick D-04 option (a) — inline-copy. Don't touch verified v1.0 paths.
**Warning signs:** Any diff that modifies `eprom.cpp`'s `eprom_check_vpp` body during Phase 1.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| AT28C256 chip-ID inferred via "we don't know" | A9-12V hardware identification (datasheet-only; firmware doesn't currently use it for 28C path) | N/A for firmware; AT28C256 datasheet has been consistent since at least 1999 | Forces Option A or C for SAF-05; rules out Option B as datasheet-correct |
| 28C SDP magic addresses (0x5555, 0x2AAA) confused with AMD JEDEC autoselect | Recognized as coincidentally shared — same address-decode hardware, different command semantics | Confusion documented in CONTEXT.md D-05; this research clarifies | Research recommends correcting the assumption before locking implementation |

**Deprecated/outdated assumption in CONTEXT.md:**
- D-05's "Atmel AT28C JEDEC chip-id mode" specification is not Atmel; it's AMD/SST. The 0x5555/0x2AAA/0x90 sequence is documented for SST39SF0x0 and AM29Fxx0 (both algorithm 0x06 in this codebase, handled by `flash_type_3.cpp` — and indeed `flash_type_3.cpp` reuses the `flash_utils.h` `FLASH_ENABLE_ID` table that has exactly this 3-write sequence). The AT28C family does NOT support it.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The current `[env:native]` build configuration in `platformio.ini` will discover new `test_*/` directories automatically without any `platformio.ini` edit | Validation Architecture | LOW — verified by reading the comment in `platformio.ini` lines 53-61 ("auto-discovered by PIO under test/") and reading `firestarter/CLAUDE.md` "Reuse pattern for future native tests"; if wrong, planner adds a `[test:test_flash_intel_vpp]` section per-suite |
| A2 | The AT28C-family device-id region (`mem_size - 64` calculation) generalizes for the entire Phase 13 override set | D-08 / Code Examples | MEDIUM — verified for AT28C256 (32K, 0x7FC0) and AT28C64 (8K, 0x1FC0); not deeply verified for AT28C16 (2K, would be 0x07C0) or AT28HC256. If a chip in the override set doesn't use `mem_size - 64`, that one chip's `chip_id_value` validation reads wrong bytes — but currently NO chip in the regenerated DB has `chip_id_value` populated for 0x0D, so this is vacuously safe today |
| A3 | The 15 existing dispatch Unity tests do not link or reference `flash_intel_check_vpp` or `eeprom28c_check_chip_id` by name | D-04 / D-11 | LOW — verified by reading `test_dispatch/test_configure_memory.cpp` (it calls `configure_memory` and checks `response_code` only; never names internal handler functions) |
| A4 | PIO `test_build_src = yes` semantics: each `test/<dir>/` builds an independent test binary linking that directory's TUs + `src_filter`-matched firmware sources | Validation Architecture / Pitfall 1 | LOW — this is the documented PIO behavior, and `firestarter/CLAUDE.md` "Native (Host) Test Environment" reuse pattern reflects it. If wrong, all suites would share a single binary and the link error would manifest in dispatch suite too |
| A5 | `HARDWARE_REVISION` is defined for `[env:native]` builds (via the `[env]` shared `build_flags` block) | SAF-04 / REV0 test case | LOW — verified by reading `platformio.ini` lines 14-21: `-D HARDWARE_REVISION` is in the shared `[env]` block, inherited by all envs including `native` |
| A6 | `eeprom_28c.cpp` currently sets `mem_size` correctly from the JSON `memory-size` field via `json_parser.c` | SAF-05 / Pitfall 4 | LOW — would need to be verified during planning by reading `firestarter/src/json_parser.c`, but the field has been on the wire since v1.0 Phase 02 and all 0x0D dispatch tests pass, so it's almost certainly correctly wired |
| A7 | The recommended approach (option A for SAF-05) requires NO new wire-protocol fields | scope/in-scope | LOW — A9-12V mechanism uses `chip_id` (already on the wire) and `mem_size` (already on the wire). No new fields |

## Open Questions (RESOLVED)

1. **Should the planner re-discuss D-05 with the user before locking SAF-05 implementation?**
   - **RESOLVED:** Plan `01-02-PLAN.md` records the override in `must_haves.truths` (first bullet) and adopts Option A (A9-12V) with RESEARCH.md cited as authority. No `/gsd-discuss-phase --amend` round-trip required — the override is load-bearing visible to Phase 3 retroactive verification.

2. **Does `mem_size` reach `eeprom28c_check_chip_id` correctly in production firmware?**
   - **RESOLVED:** Plan `01-02-PLAN.md` Wave-1 test bodies exercise the path by setting `h.mem_size = 32768` explicitly on the hand-built handle (PATTERNS.md Pitfall 4). Production wiring is implicitly trusted: `mem_size` has been on the wire since v1.0 Phase 02 and all existing 0x0D dispatch tests pass. If a future regression appears, the SAF-05 Unity tests will not detect it (they bypass `json_parser.c`) — flagged for Phase 3 retroactive verification scope.

3. **For Option A (A9-12V), is the 12V VPP rail safe to enable on a 5V-only AT28C chip's A9 pin?**
   - **RESOLVED:** Datasheet-safe per AT28C256 Rev. 0006H ("By raising A9 to 12V ± 0.5V"). Live-hardware confirmation is deferred to Phase 4 (HW-05) per ROADMAP.md. Plan `01-02-PLAN.md` mirrors `eprom_get_chip_id`'s register sequence verbatim — same A9_VPP_ENABLE + REGULATOR toggle path that already works for UV-EPROM identification on the same shield.

4. **Is `flash_intel_erase_execute`'s VPP gating actually deferred to v1.2, or should it be in Phase 1 too?**
   - **RESOLVED:** Locked deferred by user per CONTEXT.md `<deferred>`. Plan `01-01-PLAN.md` `<threat_model>` block explicitly notes that `flash_intel_erase_execute` retains the v1.0 partial-coverage state, so REQ-SAF-01 remains "partial for Intel-erase" after Phase 1 — visible to Phase 3 retroactive verification scope.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO Core | `pio test -e native` (SAF-06 test execution) | TBD — verify during planning | — | If unavailable in dev container, planner adds `pio --version` check to Wave 0 setup |
| ArduinoFake@^0.4.0 | Native tests (transitively required by existing dispatch tests) | TBD — PIO pulls it on first test invocation | 0.4.x | — |
| `cd firestarter && pio` working dir | All firmware build/test commands | TBD — firmware sub-repo present per CLAUDE.md, not committed in this repo | — | Planner must verify the sub-repo is on disk at `firestarter/` before invoking PIO |
| GCC + libc (host) | `[env:native]` cross-compile | — (system default) | — | — |
| Python pypdf (for datasheet PDF parsing) | This research only | ✓ | Installed during research | N/A (research artifact, not phase dependency) |

**Missing dependencies with no fallback:** None identified — the dispatch suite already ran successfully in v1.0 Phase 12, so the `[env:native]` toolchain is known-working. Phase 1 reuses that infrastructure.

## Sources

### Primary (HIGH confidence)
- **AT28C256 Atmel datasheet, Rev. 0006H, 12/1999** — extracted full text via pypdf from <https://eater.net/datasheets/28c256.pdf>. Page 3, "DEVICE IDENTIFICATION" section. Confirms A9-12V mechanism; no software JEDEC autoselect.
- **AT28C64B Microchip datasheet, DS20006432B, 2023** — extracted full text via pypdf from <https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/AT28C64B-64-Kbit-8Kx8-Parallel-EEPROM-with-Page-Write-and-Software-Data-Protection-DS20006432.pdf>. Section 6.7 "Device Identification". Confirms same mechanism in current Microchip-era device.
- **`firestarter/src/proms/eprom.cpp`** — direct read of `eprom_check_vpp` (lines 199-232) and `eprom_get_chip_id` (lines 186-197). Confirms tolerance bands, REV0 guard pattern, A9-12V hardware sequence.
- **`firestarter/src/proms/flash_intel.cpp`** — direct read of `flash_intel_write_init` (lines 47-62), `flash_intel_check_chip_id` (lines 115-124), `flash_intel_poll_sr` (lines 92-113). Confirms regulator state at insertion point, response-format conventions.
- **`firestarter/src/proms/eeprom_28c.cpp`** — direct read of full file. Confirms SDP-disable table, init shape, lack of any chip-id code today.
- **`firestarter/include/firestarter.h`** — direct read. Confirms handle struct layout (`vpp_mv`, `chip_id`, `mem_size`, function pointers), `FLAG_FORCE` semantics.
- **`firestarter/include/logging.h`** — direct read. Confirms `firestarter_response_format` / `firestarter_warning_response_format` / `firestarter_error_response_format` macro family.
- **`firestarter/test/native/avr/test_dispatch/{test_configure_memory.cpp, host_stubs.cpp, avr/pgmspace.h}`** — direct read. Confirms test layout, mocking pattern, PIO conventions.
- **`firestarter/platformio.ini`** — direct read. Confirms `[env:native]` config, `src_filter`, `test_build_src`, `-D HARDWARE_REVISION` flag inheritance.

### Secondary (MEDIUM confidence)
- WebSearch on "AT28C256 software product identification mode JEDEC autoselect" — multiple datasheet sources cross-verified; no source describes a JEDEC-style software autoselect for AT28C. Indirectly confirms the negative claim.

### Tertiary (LOW confidence)
- TommyPROM PromDevice28C source code reference — community/educational implementation; not deeply verified in this research but consistent with the A9-12V conclusion.

## Metadata

**Confidence breakdown:**
- D-04 recommendation: HIGH — based on direct read of both functions; reuse-surface analysis is concrete.
- D-08 recommendation: HIGH — two independent datasheets verified; functional indifference + safety-convention alignment.
- AT28C JEDEC sequence verification: HIGH for the negative claim (no JEDEC autoselect in AT28C family) — two datasheets directly quoted. The positive claim (A9-12V is the only path) is HIGH for AT28C256/AT28C64; MEDIUM for rare variants out of scope.
- Validation Architecture: HIGH — based on direct read of existing test infrastructure + `firestarter/CLAUDE.md` reuse pattern.
- Reuse audit: HIGH — every recommendation is grounded in reading the proposed sites.
- Open question 3 (RURP shield A9_VPP wiring on 5V chips): MEDIUM — not deeply traced through `firestarter/src/boards/` in this research; planner should investigate.

**Research date:** 2026-05-11
**Valid until:** 2026-12-11 (datasheets are stable; firmware moves slowly. Re-validate before Phase 4 hardware tests in case AT28C-family parts behave differently in practice than datasheets describe.)

# Technology Stack — v1.14 Feasible-Gap Implementation

**Project:** Firestarter EPROM Programmer
**Researched:** 2026-06-18
**Confidence:** HIGH — all claims grounded in verified source files or cited hardware documentation

---

## Headline Finding

**v1.14 needs no new third-party dependencies.** Every library, framework, and tool required for all four gaps already exists and is proven in the project. The work is entirely within the established dual-repo lockstep (Arduino C++ firmware + Python CLI host). The single external hardware question — whether the RURP boost regulator can physically produce 25V — is now resolved: **YES, the RURP hardware is rated 5–27V VPP**, making the 22V software ceiling a deliberate conservative limit that can be raised, not a physical constraint. All four gap implementations are software work with bench verification gates.

---

## Current Flash Budget (critical constraint)

**Leonardo flash ceiling: ~88% design target; current actual: 89.5%**

```
Flash: [========= ]  89.5% (used 25,654 bytes from 28,672 bytes)
Free:  3,018 bytes
RAM:   78.1% (used 1,999 bytes from 2,560 bytes)
```

Source: `pio run -e leonardo` on `v1.13-algo-validation` tip (2026-06-18). The prior v1.13 target was "stay under 88%" — Phase 74 FIX-02 (`CMD_CHECK_CHIP_ID` mirror in `configure_flash4`) pushed the ceiling to 89.5%. This is the hard constraint that determines phase ordering.

**Flash-budget impact by gap (estimated):**

| Gap | Files added / changed | Estimated flash impact | Notes |
|-----|----------------------|----------------------|-------|
| 999.4 Erase write-path | Host-only (`database.py` one-liner) | **0 bytes** — firmware unchanged | `eprom_write_init` already has the `FLAG_CAN_ERASE` guard; only the flag set is wrong |
| 999.6 AT28C04/16 adapter | Host-only (remove refusal in `chip_resolver.py`) | **0 bytes** — firmware unchanged | `configure_eeprom28c` already exists and handles the protocol |
| 999.7 25V NMOS ceiling | Host-only (`build_db.py` constant + `check_dispatch.py` invariant) | **0 bytes** — firmware unchanged | Ceiling check is entirely at DB-build + CI gate; no firmware VPP limit |
| 999.5 X88C64 handler | New `eeprom_x88c64.cpp` + `eeprom_x88c64.h` + dispatch arm | **~1–3 KB** — new handler TU | The one gap that adds firmware code; must be measured before commit |

**Critical implication:** Three of the four gaps (999.4, 999.6, 999.7) are host-only changes with zero firmware footprint. The only firmware-adding gap is 999.5 (X88C64). With 3,018 bytes free, a well-written 1–3 KB handler fits comfortably — but `pio run -e leonardo` must be run and verified as part of the phase gate before committing the new handler. The suggested build order (999.4 → 999.5 → 999.7 → 999.6) is correct.

---

## Recommended Stack (no changes from v1.13)

### Firmware (Arduino C++ / PlatformIO)

| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| PlatformIO | current | Build, upload, test runner | `pio run -e leonardo`, `pio test -e native` |
| Arduino AVR framework | ATmega32U4 (Leonardo) | Firmware runtime | Leonardo is the only validated-PASS write board |
| ArduinoFake | current | Host-side test stubs | Enables `pio test -e native` dispatch suite without hardware |
| Unity | current | Native unit test framework | Already used in `test/native/avr/test_dispatch/` |

### Host (Python 3)

| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| Python | 3.9+ (CI), 3.12 (devcontainer) | Runtime | 3.9 is the CI floor; 3.12 devcontainer may mask f-string backslash issues |
| Click | current | CLI framework | Established; all commands use `@cli.command()` |
| pytest + pytest-cov | current | Test runner + coverage | Coverage floor 70%; 642 tests at v1.13 close |
| ruff | current | Lint + format | Enforced in CI; all generated code must be ruff-clean |
| mypy (strict) | current | Type checking | Enforced on 8 modules; any touched module stays in scope |

### Infrastructure

| Technology | Purpose | Notes |
|------------|---------|-------|
| GitHub Actions | CI gate | `beta-release.yml` + `ci.yml`; drift gate + ruff + mypy + pytest |
| PyPI | Beta wheel distribution | `pip install --pre firestarter`; operator-gated stable |
| `tools/build_db.py` | Chip database pipeline | Single canonical regeneration path; must stay deterministic |
| `tools/check_dispatch.py` | VPP safety + dispatch correctness CI gate | Must pass after every DB change |
| `tools/diff_db.py` | Per-chip diff gate | Must pass and be reviewed after any chip reclassification |

---

## Gap-by-Gap Stack Analysis

### 999.4 — Erase Write-Path (FLAG_CAN_ERASE Wiring)

**Nature:** Host-only fix. Zero firmware changes.

**Exact change:**
- `firestarter_app/firestarter/database.py:594–599` — `convert_to_programmer` currently gates `FLAG_CAN_ERASE` on `full_eprom_data.get("info-flags", 0) & 0x00000010`. All 7 EE-EPROM chips on protocol 0x07 (`electrical.type == "EEPROM"`: W27C512, W27E512, W27C257, W27E257, SST27SF256, SST27SF512, SST27VF256, SST27VF512) have `info-flags: 0x0` in `chip_database.json` — so the flag is never set. The fix: change the condition to check `full_eprom_data.get("electrical", {}).get("type") == "EEPROM"` (already present in the DB; derived by `build_db.py` Step 7 at `build_db.py:583–590`).

**Firmware side (no change needed):** `eprom_write_init` (`eprom.cpp:100–106`) already contains:
```cpp
if (is_flag_set(FLAG_CAN_ERASE)) {
    if (!is_flag_set(FLAG_SKIP_ERASE)) {
        eprom_internal_erase(handle);
    } else {
        LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE);
    }
}
```
The guard is correct; only the flag set was broken.

**Erase electricals already confirmed:** `eprom_internal_erase` (`eprom.cpp:274–288`) drives `CTRL_VPP_REGULATOR_ENABLE`, `CTRL_VPP_A9_ENABLE`, `CTRL_VPE_ENABLE` — the W27C512 erase sequence (Phase 73 bench-confirmed standalone). The erase rail for W27C512 is 14V (OE/VPP=14V, A9=14V per datasheet); this is within the 22V ceiling and was confirmed in Phase 73. No new electrical path is added.

**What to test:** Wire the fix → run 642 host tests → `check_dispatch.py` → `diff_db.py` → bench write on Leonardo/W27C512 (chip-OUT VPP dry-run first per memory protocol, then live write+verify).

**Confidence:** HIGH. The gap is a single condition in one function, with all surrounding infrastructure correct.

---

### 999.5 — X88C64 0x34 Firmware Handler

**Nature:** Firmware-adding gap. New handler TU. The hardest gap.

**Interface architecture (from `X88C64-FEASIBILITY.md`):**
The X88C64P presents an **8051-compatible multiplexed address/data bus**, not a standard /WE /OE /CE parallel bus:
- Pins A/D0–A/D7 carry A0–A7 (during address phase) then D0–D7 (during data phase), sequenced by ALE.
- ALE falling edge latches the lower address into the chip's internal latch.
- A8–A12 are dedicated upper address pins (straightforward parallel drive).
- /WR is the write strobe (analogous to /WE but with ALE-precondition sequencing).
- WC (pin 5) is a write-control enable/abort signal — additional control pin.
- /CE, /RD are standard active-LOW enables.
- Toggle-bit polling on I/O6 (not DQ7 like `configure_eeprom28c`).
- Page write: up to 32 bytes per internal write cycle.
- 5V only — no VPP rail, no boost regulator involvement.

**Open question — ALE routing (CRITICAL, must resolve before phase commit):**

The RURP control register has 8 bits (legacy: `0x01` through `0x80`; HARDWARE_REVISION: 9-bit with `0x100`). The current bit assignments from `rurp_pinout.h`:

| Bit | Name | Purpose |
|-----|------|---------|
| `0x01` | `CTRL_VPP_VPE_DROP_ENABLE` (legacy) / `CTRL_ADDRESS_LINE_16` (rev2) | Dual-use |
| `0x02` | `CTRL_VPP_A9_ENABLE` | Route VPP to A9 |
| `0x04` | `CTRL_VPE_ENABLE` | Apply VPE to PGM pin |
| `0x08` | `CTRL_VPP_P1_ENABLE` | Route VPP to socket pin 1 |
| `0x10` | `CTRL_ADDRESS_LINE_17` | A17 for 28-pin chips |
| `0x20` | `CTRL_ADDRESS_LINE_18` / `CTRL_ADDRESS_LINE_16` (rev2) | A18/A16 |
| `0x40` | `CTRL_READ_WRITE` | Bus direction |
| `0x80` | `CTRL_VPP_REGULATOR_ENABLE` | Enable boost regulator |

The X88C64P is DIP24, so A17/A18 (`0x10`, `0x20`) are unused. ALE could potentially be routed through `CTRL_VPP_A9_ENABLE` (since VPP is irrelevant for this 5V chip) or through `CTRL_VPE_ENABLE` (similarly unused for a 5V device). However, this is NOT confirmed — it depends on how those bits physically route to socket pins vs. the regulator circuit on the shield.

**Action required for 999.5 phase planning:** Read `firestarter/src/rurp_shield.cpp` (or equivalent hardware register write implementation) to determine whether `CTRL_VPP_A9_ENABLE` or `CTRL_VPP_VPE_DROP_ENABLE` routes to a socket pin (DIP24 position) that could serve as ALE, or whether a direct Arduino GPIO pin is available for ALE toggling. This is the bench investigation prerequisite. If no available bit exists without PCB changes, the handler cannot be completed without a shield modification.

**Code structure for the new handler:**
```
firestarter/src/proms/eeprom_x88c64.cpp  — new file
firestarter/include/eeprom_x88c64.h      — declaration
```

Handler function signature: `void configure_x88c64(firestarter_handle_t* handle)`

Dispatch wiring in `memory.cpp`: add `if (handle->protocol == 0x34) { configure_x88c64(handle); return; }` before the generic fail-closed guard (after the `configure_sram` arm at line ~99, before the named infeasibility arms at line ~107).

**Code sharing with existing handlers:**
- Toggle-bit I/O6 polling: structurally similar to `eeprom28c_wait_for_write` (`eeprom_28c.cpp`) but on bit 6 instead of bit 7 (DQ7). Can copy-adapt the polling pattern; no shared function needed (flash budget argument against factoring).
- SDP disable: X88C64P has Software Block Protect per 1K block but the write sequence is address/data pairs, NOT the AT28C 6-write magic sequence. Do not reuse `EEPROM_SDP_DISABLE`.
- Page write loop: analogous to `configure_flash4`'s page-write loop but with ALE-multiplexed address phase per byte.

**Host side for 999.5:**
- `build_db.py:KNOWN_PROTOCOLS` already includes `0x34` (verified at `build_db.py:146`).
- `check_dispatch.py:KNOWN_PROTOCOLS` does NOT include `0x34` (by design — D-10 consistency assertion requires `0x34 NOT IN` the set for the `protocol-not-implemented` classification to pass).
- When the handler is committed and the chip graduates to `supported`, `0x34` must be added to `check_dispatch.py:KNOWN_PROTOCOLS` AND removed from `build_db.py`'s special-case for protocol-not-implemented. The `diff_db.py` diff gate must be reviewed.

**Bench note:** The X88C64P requires a DIP24→DIP32 adapter (same socket-size mismatch as AT28C04/16). The adapter pin-map for the X88C64P needs a separate derivation from the datasheet — do NOT reuse the AT28C04 adapter spec (different pin assignments).

**Confidence:** MEDIUM. ALE routing is the primary risk; if a free control bit exists, the handler is implementable. If not, a PCB mod or shield revision is required.

---

### 999.7 — 25V NMOS VPP Ceiling Raise

**Nature:** Host-only change + bench hardware verification gate.

**The 25V question is now resolved: the RURP hardware CAN produce 25V.**

Evidence:
- RURP Rev 2.3 product page explicitly states "5-27V VPP" (imania.dk/product_info.php?products_id=7218).
- Hackaday project page confirms the AP3012 boost regulator supports "up to 25V for TMS2532-style ROMs" and can go "4.5→36V-ish" depending on feedback resistors.
- The `RURP_VPP_CEILING_MV = 22000` in `build_db.py:117` is a **deliberate conservative software limit**, not a hardware-physical ceiling.

However, the actual ceiling achievable on any given shield revision depends on the R1/R2 feedback resistor values stored in EEPROM (`VALUE_R1 = 270000`, `VALUE_R2 = 44000` in `rurp_shield.h:49-50`). These determine the boost regulator setpoint. **The phase must begin with a chip-OUT VPP dry-run (`firestarter dev vpp`) on the operator's Rev 2.0/2.2 shield to confirm the regulator actually reaches 25V before any chip is inserted.** If the regulator does not reach 25V with the current R1/R2, an R1 recalibration (`firestarter dev calibrate-vpp`) or resistor change is required first.

**Exact software changes:**
1. `firestarter_app/tools/build_db.py:117` — raise `RURP_VPP_CEILING_MV` from `22000` to `25000`.
2. `firestarter_app/tools/check_dispatch.py:79` — update `"configure_eprom": (0, 22000)` invariant to `(0, 25000)`.
3. Regenerate `chip_database.json` via `python tools/build_db.py` — the 4 chips currently tagged `vpp-exceeds-max` (INTEL M2716, INTEL M2732, SGS-THOMSON ETC2716, ST M2716) will be reclassified.
4. Run `diff_db.py` to review the 4-chip reclassification diff.
5. Confirm the 4 chips now have `support_status: supported` and correct `vpp_mv: 25000`.

**The 4 chips:** Per `NMOS_TRUE_VPP_MV` in `build_db.py:110–114`, M2716 and M2732 are already coded at 25V. M2732A (21V) is already `supported` and is unaffected. SGS-THOMSON ETC2716 and ST M2716 share the M2716 VPP.

**Programming electricals for 25V NMOS:** The M2716/M2732 use the `configure_eprom` path (protocol 0x07/0x08). The existing `eprom_write_execute` drives `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE` for the 0x07/0x08 path. At 25V setpoint, this same path applies — no new firmware logic is needed. The regulator simply outputs a higher voltage (25V instead of 12–14V) because `vpp_mv: 25000` is passed in the JSON command and the firmware trusts the host to have pre-screened the chip.

**Confidence:** HIGH for the software change. HARDWARE-GATED: operator must confirm 25V is achievable on the bench shield with a chip-OUT meter reading before classifying as PASS.

---

### 999.6 — AT28C04/16 Adapter Graduation

**Nature:** Host-only change (remove host-guard refusal) + physical hardware gate.

**Exact software change:**
- `firestarter_app/firestarter/chip_resolver.py` — remove or conditionalize the `adapter-required` refusal for the 9 AT28C04/16 chips. Currently `resolve_chip` raises `ChipNotImplementedError` for `support_status: adapter-required`. After the physical adapter is built and verified, change `support_status` to `supported` for the 9 chips (via DB regeneration or override).

**Firmware side (no change needed):** `configure_eeprom28c` (protocol `0x0D`) already handles these chips correctly. The handler runs SDP-disable + DQ7 page polling + 5V-only operation. The `DIP32_28C512_EEPROM` pinout is already wired. The only gap was the physical /WE reroute that the adapter provides.

**Physical adapter spec:** Documented in `firestarter/doc/AT28C04-ADAPTER.md`. The critical reroute is chip pin 21 (/WE) → DIP32 socket pin 30 (/WE). Without the adapter, /WE lands on socket pin 21 which carries D7 — harmless electrically but write-disabling. The adapter is NOT a hazardous build (no VPP rail involved; worst case is a non-functioning write, not chip destruction).

**HARDWARE-BLOCKED:** This gap cannot be completed until:
1. The operator builds the physical DIP24→DIP32 adapter per `AT28C04-ADAPTER.md`.
2. A golden write+read-back round-trip is verified on a physical AT28C04 or AT28C16 chip.

Sequence last for this reason.

**Confidence:** HIGH for the code change. HARDWARE-GATED on adapter construction.

---

## Code Sharing Map

| Existing handler | Shared by | How |
|-----------------|-----------|-----|
| `configure_eprom` / `eprom_write_init` | 999.4 (no change) | The FLAG_CAN_ERASE guard is already there; only the host-side flag set changes |
| `configure_eeprom28c` | 999.6 (no change) | Handler already correct for AT28C04/16; no new code |
| `configure_eprom` | 999.7 (no change) | 25V NMOS uses the same handler; regulator just outputs higher voltage |
| Toggle-bit polling concept | 999.5 (adapt) | I/O6 toggle pattern adapted from DQ7 in `eeprom_28c.cpp`; not shared function |

The only new firmware TU is the X88C64 handler for 999.5. All other gaps reuse existing handlers unchanged.

---

## Alternatives Considered

| Decision | Chosen | Alternative | Why Not |
|----------|--------|-------------|---------|
| FLAG_CAN_ERASE source | `electrical.type == "EEPROM"` | `info-flags & 0x10` | `info-flags` is raw minipro XML and is 0x0 for all 7 affected chips; `electrical.type` is re-derived from the correct source in `build_db.py` |
| X88C64 ALE via control register | Investigate existing CTRL_* bits (0x02 or 0x04 candidates) | Direct Arduino GPIO | Control register is the established pattern; GPIO would bypass the shield's 74HC573 register architecture — only fallback if no bit is free |
| 25V ceiling host-only vs firmware check | Host-only (in `build_db.py` + `check_dispatch.py`) | Add firmware VPP ceiling check | Firmware trusts the host; adding a firmware check duplicates the gate for no safety gain and costs flash bytes |
| AT28C04 adapter via `resolve_chip` flag | Change `support_status` in DB after bench verify | Keep `adapter-required` and add `--adapter` flag | `support_status: supported` is the correct post-adapter state; `--adapter` flag adds complexity for no benefit |

---

## Absolute Constraints for v1.14

1. **Leonardo flash: do not exceed 90% without explicit operator approval.** Current: 89.5%. Free: 3,018 bytes. The X88C64 handler (999.5) is the only gap that costs flash. Measure with `pio run -e leonardo` and record the percentage in the phase CONTEXT.
2. **25V VPP: chip-OUT dry-run required before any 25V bench test.** Per memory protocol for VPP-raising operations.
3. **X88C64 ALE routing: must be resolved (bench investigation of `rurp_pinout.h` + `rurp_shield.cpp`) before the 999.5 handler is coded.** If no free control bit exists, document the constraint and defer the handler.
4. **AT28C04 adapter: must be physically built and bench-verified before `chip_resolver.py` refusal is removed.** Sequence 999.6 last.
5. **Dual-repo lockstep:** Any firmware commit to `firestarter/` must be paired with a matching host commit in `firestarter_app/` (wire protocol, constants, messages) in the same git-push or branch tip. For 999.4/999.6/999.7 (host-only), the firmware sub-repo is untouched.
6. **`check_dispatch.py` and `diff_db.py` must pass** after every DB change before a phase is verified.

---

## Sources

| Source | Confidence | How Used |
|--------|-----------|---------|
| `firestarter/src/proms/eprom.cpp:93–111` (verified 2026-06-18) | HIGH | FLAG_CAN_ERASE guard in `eprom_write_init`; erase electricals in `eprom_internal_erase` |
| `firestarter_app/firestarter/database.py:594–599` (verified 2026-06-18) | HIGH | FLAG_CAN_ERASE gating on `info-flags & 0x10` |
| `firestarter_app/tools/build_db.py:117, 110–114, 134–148` (verified 2026-06-18) | HIGH | RURP_VPP_CEILING_MV=22000; NMOS_TRUE_VPP_MV; KNOWN_PROTOCOLS |
| `firestarter_app/tools/check_dispatch.py:79–85` (verified 2026-06-18) | HIGH | _FAMILY_VPP_INVARIANTS for configure_eprom ceiling |
| `firestarter/include/rurp_pinout.h` (verified 2026-06-18) | HIGH | CTRL_* control register bit assignments; no free ALE bit confirmed |
| `firestarter/include/rurp_shield.h:49–50` (verified 2026-06-18) | HIGH | R1=270000, R2=44000 default feedback values |
| `.planning/X88C64-FEASIBILITY.md` (Phase 76, 2026-06-18) | HIGH | X88C64P bus architecture; ALE routing open question; MEDIUM verdict |
| `firestarter/doc/AT28C04-ADAPTER.md` (verified 2026-06-18) | HIGH | DIP24→DIP32 pin-map; /WE reroute (chip pin 21 → socket pin 30) |
| `.planning/v1.13-PROTOCOL-ENUMERATION.md §Gap Item Index` (2026-06-17) | HIGH | GAP-1/GAP-3 code-state pointers; ceiling constraint rationale |
| `pio run -e leonardo` (run 2026-06-18) | HIGH | Current flash: 89.5% / 25,654 bytes; free: 3,018 bytes |
| RURP Rev 2.3 product page (imania.dk, verified 2026-06-18) | HIGH | "5-27V VPP" — hardware rated above 25V |
| Hackaday RURP project page (verified 2026-06-18) | HIGH | AP3012 boost regulator; "up to 25V for TMS2532-style ROMs"; 4.5→36V range |

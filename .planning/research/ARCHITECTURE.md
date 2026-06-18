# Architecture Research

**Domain:** EPROM programmer — dual-repo firmware + host CLI, chip graduation via algorithm dispatch + DB pipeline
**Researched:** 2026-06-18
**Confidence:** HIGH (all findings grounded in live source files on current beta, verified 2026-06-18)

---

## Standard Architecture

### System Overview

```
HOST (Python CLI — firestarter_app/)
  ┌──────────────────────────────────────────────────────────────────────┐
  │  build_db.py          chip_database.json    chip_resolver.py         │
  │  (DB pipeline)   →   (generated artifact)  →  support_status guard   │
  │  support_status       algorithm, vpp_mv,       raises                 │
  │  classification       pinout, reason            ChipNotImplementedError│
  │  WARNING-5/NMOS/                               BEFORE any serial byte │
  │  adapter/proto-ni                                                     │
  │                  ↓                                                    │
  │  database.py                                                          │
  │  _map_data() → info-flags, FLAG_CAN_ERASE                            │
  │  convert_to_programmer() → wire dict                                  │
  │                  ↓                                                    │
  │  eprom_operations.py                                                  │
  │  write/read/verify command builder                                    │
  └──────────────────┬───────────────────────────────────────────────────┘
                     │  JSON over COBS+CRC8 serial (250000 baud)
  ┌──────────────────▼───────────────────────────────────────────────────┐
  │  FIRMWARE (C++ — firestarter/)                                        │
  │                                                                       │
  │  memory.cpp :: configure_memory()                                     │
  │  ┌──────────────────────────────────────────────────────────────────┐│
  │  │ if (protocol == 0x10) → configure_flash_intel()          return ││
  │  │ if (protocol == 0x0D) → configure_eeprom28c()            return ││
  │  │ if (protocol == 0x06) → configure_flash3()               return ││
  │  │ if (protocol in 0x05/35/39) → configure_flash4()         return ││
  │  │ if (protocol in 0x07/08/0B) → configure_eprom()          return ││
  │  │ if (protocol in 0x0E/27/28/29) → configure_sram()        return ││
  │  │ [named infeasible: 0x11/2A/2B/2C] → not_implemented()    return ││
  │  │ if (protocol != 0) → not_implemented()  ← FAIL-CLOSED    return ││
  │  │ [protocol==0 only: mem_type fallback for legacy JSON]            ││
  │  └──────────────────────────────────────────────────────────────────┘│
  └──────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | File |
|-----------|---------------|------|
| `build_db.py` | Sole classification authority. Produces `support_status`, `algorithm`, `vpp_mv`, `pinout`, `unsupported_reason` per chip. Safety overrides: WARNING-5, fm1608, NMOS VPP, named rule arms. | `firestarter_app/tools/build_db.py` |
| `chip_database.json` | Generated artifact — do NOT hand-edit. Carries `support_status` for every chip. | `firestarter_app/firestarter/data/chip_database.json` |
| `chip_resolver.py` | Single chokepoint between CLI and DB. Reads `support_status` BEFORE building any wire dict. Raises `ChipNotImplementedError` for non-`supported`. No serial byte ever emitted. | `firestarter_app/firestarter/chip_resolver.py` |
| `database.py` | `EpromDatabase` — loads DB, `_map_data()` computes `info-flags` (bit 0x10 = electrically erasable), `convert_to_programmer()` emits wire dict including `FLAG_CAN_ERASE`. | `firestarter_app/firestarter/database.py` |
| `memory.cpp` | Firmware dispatch hub. Protocol-prefix if-return chain. Generic fail-closed guard at end. New handler arms inserted BEFORE the generic guard. | `firestarter/src/proms/memory.cpp` |
| `rurp_pinout.h` | CTRL_* control-register bit definitions. Hardware-level authority on which bits toggle which address/VPP/OE lines. | `firestarter/include/rurp_pinout.h` |
| `check_dispatch.py` | CI correctness gate. Mirrors `memory.cpp` dispatch in Python. Asserts every DB chip reaches the correct handler, VPP invariants hold, D-10 consistency. Must stay synchronized with both repos. | `firestarter_app/tools/check_dispatch.py` |
| `constants.py` / `firestarter.h` | Lockstep constants — flag bits (FLAG_CAN_ERASE=0x02, etc.), command codes, message IDs. Change both files in the same commit. | Both sub-repos |

---

## The Refused-to-Supported Path

Every v1.14 graduation must traverse this pipeline end-to-end:

```
build_db.py                          chip_resolver.py
  ┌─────────────────────────────┐     ┌───────────────────────────────────┐
  │ support_status = "supported"│     │ support_status == "supported"?    │
  │ algorithm = correct proto   │  →  │   YES: build wire dict + proceed  │
  │ unsupported_reason removed  │     │   NO:  raise ChipNotImplementedErr│
  └─────────────────────────────┘     └───────────────────────────────────┘
           ↓ (regenerate DB)                          ↓
  chip_database.json                  database.py convert_to_programmer()
  (updated support_status)            (emit flags, vpp_mv, algorithm)
                                                      ↓
                                      memory.cpp configure_memory()
                                      (dispatch arm routes to handler)
                                                      ↓
                                      handler executes on hardware
                                                      ↓
                                      bench: write + read-back + verify
```

**Key invariant:** The host guard (`chip_resolver.py`) fires on `support_status`. It reads this field directly from the raw chip config BEFORE calling `convert_to_programmer`. No other file needs to change to enable/disable the guard — the DB field controls it.

---

## Feature Integration Points

### 999.4 — Erase Write-Path (FLAG_CAN_ERASE for 0x07 EE-EPROMs)

**Current state (verified 2026-06-18):**

The 7 W27C512-class chips (`electrical.type = "EEPROM"`, `algorithm = 0x07`) are already `support_status: supported`. In `database.py::_map_data` (line 434), `info_flags |= 0x00000010` is set when `electrical.type in ("EEPROM", "Flash/EEPROM")`. In `convert_to_programmer` (line 597), `FLAG_CAN_ERASE (0x02)` is gated on `info-flags & 0x00000010`. Running against the live DB confirms: W27C512 → `info-flags: 0x30` → `flags: 0x02` (FLAG_CAN_ERASE set). The firmware `eprom_write_init` (eprom.cpp:100) has `if (is_flag_set(FLAG_CAN_ERASE)) { eprom_internal_erase(handle); }`.

**The actual gap:** Phase 75 was never executed. No one has bench-verified that the full write→auto-erase→program cycle works on a real W27C512. The logic is present and appears correct; the gap is bench evidence.

**What to investigate first:** Confirm whether the current host code path actually sets FLAG_CAN_ERASE correctly for the `electrical-type=EEPROM` W27C512-class chips on the current beta. If `convert_to_programmer` is using `info-flags & 0x10` but that bit is not set for some chips (possible if `_map_data` uses a different path), the ROADMAP fix applies: gate FLAG_CAN_ERASE directly on `electrical-type == "EEPROM"` rather than the derived `info-flags` bit.

**Integration points touched:**

| Layer | File | Change Type | Notes |
|-------|------|-------------|-------|
| Host wire-dict emitter | `firestarter_app/firestarter/database.py` `convert_to_programmer()` lines 594–599 | VERIFY or MODIFY | Confirm FLAG_CAN_ERASE is set for `electrical-type=EEPROM` chips. Fix if not. |
| Firmware write-init | `firestarter/src/proms/eprom.cpp` `eprom_write_init()` line 100 | NONE (logic exists) | Already has `if (is_flag_set(FLAG_CAN_ERASE))` guard |
| DB classification | `firestarter_app/tools/build_db.py` | NONE | `electrical.type` already correct for the 7 chips |
| check_dispatch.py | No change | NONE | No new protocol added |
| Host guard | `chip_resolver.py` | NONE | These chips are already `supported` |

**Lockstep requirement:** None. Host-only fix (if needed) + bench verification.

**Flash budget impact:** Zero.

---

### 999.5 — X88C64 0x34 Firmware Handler

**Critical pre-condition — ALE routing investigation (must resolve before coding):**

The X88C64P (DIP24, 5V EEPROM, 8051 multiplexed bus) requires an ALE signal to latch the lower 8 address bits on the multiplexed A/D0–A/D7 pins. The RURP firmware drives addresses via 74HC573 latches (OE-controlled); `rurp_pinout.h` defines CTRL_* bits for those latch-enable lines. An existing unused CTRL_* bit must be identified that can be repurposed to toggle ALE on pin 22 of the X88C64P. If no free bit exists without a PCB change, the handler cannot be implemented in software alone.

**Action required before any code:** Read `rurp_pinout.h` and the RURP schematic. Map CTRL_VPP_A9_ENABLE (0x02), CTRL_VPE_ENABLE (0x04), CTRL_VPP_P1_ENABLE (0x08), CTRL_ADDRESS_LINE_17/18 usage to determine if any currently-unrouted bit can serve as ALE.

**Integration points touched:**

| Layer | File | Change Type | Notes |
|-------|------|-------------|-------|
| ALE control bit | `firestarter/include/rurp_pinout.h` | INVESTIGATE → POSSIBLY MODIFY | Identify a free CTRL_* bit for ALE. If a new constant is needed, add it here. |
| Lockstep constant | `firestarter_app/firestarter/constants.py` AND `firestarter/include/firestarter.h` | MODIFY IF new CTRL_* added | Must add to both files in the same commit pair |
| Firmware dispatch | `firestarter/src/proms/memory.cpp` lines 74–119 | MODIFY | Insert `if (handle->protocol == 0x34) { configure_x88c64(handle); return; }` BEFORE the `protocol != 0` fail-closed guard |
| Firmware handler | `firestarter/src/proms/eeprom_x88c64.cpp` | NEW FILE | ALE-latch sequence (address-phase), /WR-strobe write (data-phase), page-write loop (up to 32 bytes), I/O6 toggle-bit polling, WC control |
| Firmware header | `firestarter/src/proms/eeprom_x88c64.h` | NEW FILE | `void configure_x88c64(firestarter_handle_t* handle);` |
| DB PROTOCOL_MAP | `firestarter_app/tools/build_db.py` | MODIFY | Add `0x34: "XICOR_X88C64"` (or canonical name) to `PROTOCOL_MAP`. Remove the special-case `if proto_id == 0x34: _support_status = "protocol-not-implemented"` block (lines ~361–370). After removal, the chip passes Site B naturally with `support_status=supported` and `algorithm=0x34`. |
| KNOWN_PROTOCOLS in build_db | `firestarter_app/tools/build_db.py` | NOTE | `0x34` is already in `KNOWN_PROTOCOLS` in `build_db.py`. No change needed there. |
| check_dispatch KNOWN_PROTOCOLS | `firestarter_app/tools/check_dispatch.py` | MODIFY | Add `0x34` to `KNOWN_PROTOCOLS` inside check_dispatch (currently intentionally absent). |
| check_dispatch dispatch() | `firestarter_app/tools/check_dispatch.py` | MODIFY | Add `if protocol == 0x34: return "configure_x88c64"` arm, parallel to the memory.cpp arm. |
| check_dispatch invariants | `firestarter_app/tools/check_dispatch.py` | MODIFY | Add `"configure_x88c64": (0, 6000)` to `_FAMILY_VPP_INVARIANTS` (5V-only device, no VPP). |
| Pinout review | `firestarter_app/firestarter/data/pinouts.json` | POSSIBLY MODIFY | Current DB pinout is `DIP24_6116`. Confirm that the ALE/WR/RD signals are correctly routed through this pinout, OR add a dedicated `DIP24_X88C64` entry. The handler will need precise pin mappings for the ALE and WC signals. |
| Host guard removal | `chip_resolver.py` | NONE | Automatic — once `build_db.py` classifies X88C64P as `supported`, the guard passes. No code change needed. |

**Lockstep requirement:** YES — this is the only v1.14 feature with a true dual-repo lockstep requirement. The new dispatch arm in `memory.cpp` and the updated `check_dispatch.py`/`build_db.py` classification must ship together (or firmware ships first and host ships immediately after in a separate commit).

**Flash budget impact:** HIGH (~1–3 KB for the handler). Must run `pio run -e leonardo` after adding `eeprom_x88c64.cpp` and confirm flash stays under 95% (current: 89.5%). Consider combining common EEPROM polling logic with `eeprom_28c.cpp` if flash is tight.

**New vs Modified summary:**
- NEW: `eeprom_x88c64.cpp`, `eeprom_x88c64.h`
- MODIFIED: `memory.cpp`, `build_db.py`, `check_dispatch.py`, possibly `rurp_pinout.h`, possibly `constants.py` + `firestarter.h`

---

### 999.7 — 25V NMOS Ceiling Raise (M2716/M2732)

**What is wrong today:** `RURP_VPP_CEILING_MV = 22000` in `build_db.py` (line 117). `NMOS_TRUE_VPP_MV` has M2716 and M2732 at 25000 mV. In Site C of `build_db.py`, the condition `_nmos_vpp_mv > RURP_VPP_CEILING_MV` evaluates to `25000 > 22000 = True` → `_support_status = "vpp-exceeds-max"` → `proto_id = NON_DISPATCHABLE_ALGO (0x00)`. Four chips affected: INTEL M2716, INTEL M2732, SGS-THOMSON ETC2716, ST M2716.

**Hardware gate — mandatory pre-condition:** The RURP boost regulator output is controlled by the R1/R2 feedback resistors stored in EEPROM `rurp_configuration_t.r1`/`r2`. Raising the software constant does NOT make hardware produce 25V. Operator must measure actual VPP with a multimeter on the shield being used (chip-OUT dry-run, VPP monitor mode) before changing the constant. If the shield cannot reach 25V, these chips cannot be programmed regardless of software changes.

**Integration points touched:**

| Layer | File | Change Type | Notes |
|-------|------|-------------|-------|
| VPP ceiling constant | `firestarter_app/tools/build_db.py` line 117 | MODIFY | `RURP_VPP_CEILING_MV = 22000` → `25000` |
| DB re-classification | `chip_database.json` (regenerated) | ARTIFACT | 4 chips switch: `support_status: vpp-exceeds-max → supported`, `algorithm: 0x00 → 0x07` (EPROM_STD), `vpp_mv: 25000`. Site C no longer fires for these chips. |
| check_dispatch invariants | `firestarter_app/tools/check_dispatch.py` line 79 | MODIFY | `"configure_eprom": (0, 22000)` → `(0, 25000)`. Otherwise check_dispatch flags the re-classified chips as VPP-invariant violations. |
| Host guard removal | `chip_resolver.py` | NONE | Automatic. |
| Firmware | `firestarter/src/proms/eprom.cpp` | NONE (logic exists) | `eprom_check_vpp` already reads `handle->vpp_mv` and validates against the measured ADC value. No firmware constant needs to change — the firmware uses the wire-protocol `vpp_mv` field, not a compiled ceiling. |
| Wire protocol | No change | NONE | `vpp_mv=25000` will be sent in the JSON command. Firmware reads it for ADC validation. |

**Lockstep requirement:** Minimal. Host constant change and invariant update are host-only. Firmware bench confirmation is independent.

**Flash budget impact:** Zero.

**New vs Modified summary:**
- MODIFIED: `build_db.py` (constant), `check_dispatch.py` (invariant upper bound)
- NONE: firmware, `chip_resolver.py`, `memory.cpp`

---

### 999.6 — AT28C04/16 Adapter Graduation (Hardware-Gated)

**What is wrong today:** In `build_db.py`, the `_AT28C_DIP24_NAMES` named rule arm (lines ~435–459) classifies 14 chip aliases as `support_status = "adapter-required"`. These chips have `algorithm = 0x0D` (EEPROM_POLL → `configure_eeprom28c`, VPP-free). The firmware handler is correct and complete. The classification exists solely because the RURP DIP32 socket cannot physically accept a DIP24 chip — the /WE pin (chip pin 21) would land at the wrong socket position without a physical adapter.

**Hardware gate — mandatory pre-condition:** Build the physical DIP24→DIP32 adapter per `firestarter/doc/AT28C04-ADAPTER.md`. The critical reroute: chip pin 21 (/WE) → DIP32 socket pin 30 (/WE under `DIP32_28C512_EEPROM` pinout). Without the adapter, writes will not work (firmware cannot assert /WE on the chip).

**Integration points touched:**

| Layer | File | Change Type | Notes |
|-------|------|-------------|-------|
| Named rule arm removal | `firestarter_app/tools/build_db.py` lines ~435–459 | MODIFY | Delete the `_AT28C_DIP24_NAMES` set and the `if _chip_aliases & _AT28C_DIP24_NAMES:` conditional block. After removal, chips pass Site A (0x0D is a KNOWN_PROTOCOL), skip Site B (not 0x07/08/0B), resolve to `DIP24_2816` pinout via `resolve_pinout_key` (variant_lo=0x10 → `DIP24_2816`), and are classified `supported`. |
| DB re-classification | `chip_database.json` (regenerated) | ARTIFACT | 9 chips switch: `support_status: adapter-required → supported`. `algorithm` stays `0x0D`. `unsupported_reason` removed. |
| Host guard | `chip_resolver.py` | NONE | Automatic — `support_status=supported` passes. |
| check_dispatch.py | No change | NONE | `0x0D → configure_eeprom28c` already in `dispatch()`. No VPP invariant violation (5V, no VPP pin on DIP24_2816). |
| Firmware | `firestarter/src/proms/eeprom_28c.cpp` | NONE | `configure_eeprom28c` is already correct for these chips. |
| Pinout routing | `firestarter_app/firestarter/data/pinouts.json` | NONE | `DIP24_2816` already has `rw-pin: 21` (the WE pin). The host sees the logical pinout; the adapter is transparent to software — the adapter physically maps chip pin 21 to socket pin 30, which `DIP32_28C512_EEPROM` routes to the /WE bus line. The `bus-config` JSON produced by `get_bus_config` with `DIP24_2816` is correct for this chip family. |
| AT28C04-ADAPTER.md | `firestarter/doc/AT28C04-ADAPTER.md` | MODIFY (doc) | Update "Status" section: mark as `supported` with bench evidence citation. |

**Lockstep requirement:** NONE. Host-only change (build_db.py rule arm removal only). Firmware untouched.

**Flash budget impact:** Zero.

**New vs Modified summary:**
- MODIFIED: `build_db.py` (remove named rule arm), `AT28C04-ADAPTER.md` (status update)
- NONE: firmware, `chip_resolver.py`, `memory.cpp`, `check_dispatch.py`

---

## Dual-Repo Lockstep Summary

| Feature | Firmware change? | Host change? | True lockstep? | Rationale |
|---------|-----------------|-------------|----------------|-----------|
| 999.4 Erase write-path | None expected | Verify/fix `database.py` | No | Host-only; bench verifies existing logic |
| 999.5 X88C64 handler | YES (new handler + dispatch arm + possibly new CTRL_* constant) | YES (build_db, check_dispatch, possibly constants.py) | YES | New protocol arm; potential new CTRL_* constant requires constants.py update in lockstep with rurp_pinout.h |
| 999.7 25V NMOS | None (firmware reads vpp_mv from wire) | YES (build_db, check_dispatch) | No | Host constant + invariant only; firmware bench-confirm is independent |
| 999.6 AT28C04 adapter | None | YES (build_db rule arm) | No | Pure host classification change; firmware handler exists |

**Lockstep definition:** A lockstep commit pair means both sub-repos change in a coordinated single-phase that verifies both together before any release. For v1.14, only 999.5 requires this.

---

## Build Order Dependencies and Flash Budget

| Order | Feature | Flash delta | Dependency | Rationale |
|-------|---------|------------|------------|-----------|
| 1st | 999.4 Erase write-path | ~0 | None | Software-only + bench. No flash cost. Clears ERASE-01 debt. Can proceed immediately. |
| 2nd | 999.5 X88C64 handler | +1–3 KB est. | ALE investigation must close first | Only firmware addition. Build after 999.4 so flash baseline is clean. ALE routing is the gating risk. |
| 3rd | 999.7 25V NMOS | ~0 | Hardware multimeter gate | No firmware code. Software changes are trivial. Order here because hardware gate is independent of 999.5 flash work. |
| 4th | 999.6 AT28C04 adapter | ~0 | Physical adapter must exist | Software trivial (remove rule arm). Hardware-blocked — longest lead time. |

**Flash ceiling context:** Post-v1.13 Leonardo flash is 89.5% (approximately 25,661 bytes of 28,672 bytes, ~3,011 bytes headroom). A new `eeprom_x88c64.cpp` handler adding 1–3 KB brings flash to 93–100%. Run `pio run -e leonardo` after every firmware addition and do NOT merge if flash exceeds 95%. If the handler is too large, consider extracting common ALE/WR sequencing into a shared utility shared with `eeprom_28c.cpp`.

---

## Architectural Patterns

### Pattern 1: Dispatch-First, Guard-Second (Two Independent Safety Layers)

**What:** The host guard (`chip_resolver.resolve_chip`) refuses non-`supported` chips before any serial byte. The firmware generic fail-closed guard (`if (protocol != 0) → not_implemented`) catches any protocol with no registered arm. These are independent — the host prevents incorrect usage, the firmware prevents hardware damage.

**When to use:** Every new handler registration follows: (1) build_db.py classifies chip as `supported` → (2) host guard passes → (3) firmware dispatch arm routes to correct handler. Remove classification restriction only AFTER the handler is fully implemented.

**Critical invariant for new arms:** New dispatch arms in `memory.cpp` MUST be inserted BEFORE the `if (handle->protocol != 0) { configure_not_implemented(); return; }` guard (line 116). Otherwise the chip routes to 0xBB regardless of the new arm.

### Pattern 2: DB Pipeline is the Single Classification Authority

**What:** `build_db.py` is the sole origin of classification. No chip-specific conditionals exist in `chip_resolver.py`. No manual edits to `chip_database.json`.

**When to use:** To graduate a chip, change `build_db.py` (modify/remove the rule that classified it non-supported), regenerate `chip_database.json`, and commit both together. The host guard and `check_dispatch.py` respond automatically to the field change.

**Exception:** The `_AT28C_DIP24_NAMES` named rule arm is a by-name override to be removed in 999.6. After removal, classification falls entirely to the principled `resolve_pinout_key` rules.

### Pattern 3: check_dispatch.py Must Mirror Both Repos in Sync

**What:** `check_dispatch.py`'s `dispatch()` function mirrors `memory.cpp`'s dispatch chain. Its `KNOWN_PROTOCOLS` set mirrors `build_db.py`'s set (with one intentional exception: `0x34` is absent from `check_dispatch.py` KNOWN_PROTOCOLS to satisfy the D-10 consistency assertion for `protocol-not-implemented` chips — this exception dissolves when X88C64 graduates).

**When a new handler is added:** Update `dispatch()` in `check_dispatch.py` with the matching protocol arm, add the protocol to `KNOWN_PROTOCOLS` in `check_dispatch.py`, add a VPP invariant entry to `_FAMILY_VPP_INVARIANTS`. Failing to update `check_dispatch.py` causes CI failures on the next `python tools/check_dispatch.py` run.

---

## Anti-Patterns

### Anti-Pattern 1: Inserting a firmware dispatch arm after the fail-closed guard

**What people do:** Add `if (handle->protocol == 0x34) { configure_x88c64(handle); return; }` AFTER the `if (handle->protocol != 0) { configure_not_implemented(); return; }` line.

**Why it's wrong:** The fail-closed guard returns for every non-zero protocol it sees. The new arm is unreachable dead code. The chip will silently return 0xBB (protocol not implemented) even though a handler exists.

**Do this instead:** Insert new arms BEFORE line 116 (`if (handle->protocol != 0)`). Follow the existing pattern: all named arms first, then infeasible arms, then the generic guard.

### Anti-Pattern 2: Raising the VPP ceiling without hardware confirmation

**What people do:** Change `RURP_VPP_CEILING_MV = 25000` and immediately ship 999.7.

**Why it's wrong:** The boost regulator's physical output is determined by R1/R2 feedback resistors, not the constant. Writing M2716/M2732 at incorrect VPP damages NMOS cells. The constant is a safeguard, not a capability setter.

**Do this instead:** Measure actual VPP output (chip-OUT, multimeter, VPP monitor mode) on the specific shield revision before changing the constant. If the shield maxes at 22V, these chips remain `vpp-exceeds-max` regardless of software changes.

### Anti-Pattern 3: Editing chip_database.json by hand

**What people do:** Fix a chip's `support_status` directly in the JSON to test a change.

**Why it's wrong:** The file is a generated artifact. `build_db.py` overwrites all manual changes on the next run. The `diff_db.py` gate flags unexplained diffs.

**Do this instead:** Modify the classification logic in `build_db.py` and run `python tools/build_db.py` to regenerate. Commit both `build_db.py` and the regenerated `chip_database.json` together.

### Anti-Pattern 4: Updating check_dispatch.py without updating memory.cpp (or vice versa)

**What people do:** Add a new handler arm only to `check_dispatch.py`'s `dispatch()` function, or only to `memory.cpp`, but not both.

**Why it's wrong:** `check_dispatch.py` simulates firmware dispatch. A mismatch between the two means the CI gate validates a simulation that doesn't match real firmware behavior — the safety guarantee is false.

**Do this instead:** Update both files in the same commit pair when adding a new protocol arm.

---

## Integration Check Gates (CI)

After every change in v1.14, run all applicable gates:

| Gate | Command | What it catches |
|------|---------|-----------------|
| Flash ceiling | `pio run -e leonardo` | New firmware code exceeds ~95% flash budget |
| Native dispatch tests | `pio test -e native` | Firmware dispatch regressions |
| Dispatch gate | `python tools/check_dispatch.py` | DB/dispatch mismatch, VPP invariant violations, D-10 consistency |
| Diff gate | `python tools/diff_db.py` | Unexpected chip DB changes |
| Host tests | `pytest --cov-fail-under=70` | Regression in chip resolution, wire-dict emission, guard behavior |
| Ruff + mypy | `ruff check . && ruff format --check && mypy ...` | Code quality on strict modules |

---

## Sources

- `firestarter/src/proms/memory.cpp` lines 46–137 — dispatch chain, fail-closed guard (source-verified 2026-06-18)
- `firestarter/include/rurp_pinout.h` full — CTRL_* bit definitions, REV1/REV2 variants (source-verified 2026-06-18)
- `firestarter_app/firestarter/chip_resolver.py` full — support_status guard, ChipNotImplementedError (source-verified 2026-06-18)
- `firestarter_app/firestarter/database.py` lines 385–602 — `_map_data`, `info_flags` derivation, `convert_to_programmer`, FLAG_CAN_ERASE path (source-verified 2026-06-18)
- `firestarter_app/tools/build_db.py` lines 1–744 — full classification pipeline, NMOS override, Site A/B/C, named rule arm (source-verified 2026-06-18)
- `firestarter_app/tools/check_dispatch.py` lines 1–210 — KNOWN_PROTOCOLS, dispatch(), _FAMILY_VPP_INVARIANTS, D-10 assertions (source-verified 2026-06-18)
- `.planning/X88C64-FEASIBILITY.md` — X88C64P ALE routing open question, pin description, write protocol (source-verified 2026-06-18)
- `firestarter/doc/AT28C04-ADAPTER.md` — DIP24→DIP32 pin table, /WE reroute spec (source-verified 2026-06-18)
- `.planning/ROADMAP.md` §999.4–999.7 — backlog descriptions with file:line origins (source-verified 2026-06-18)
- `.planning/PROJECT.md` §v1.14 — build order rationale, flash ceiling context, operator decisions (source-verified 2026-06-18)
- `firestarter/CLAUDE.md` + `firestarter_app/CLAUDE.md` — dispatch order table, data flow diagram (source-verified 2026-06-18)
- Live DB verification: `python3 -c "from firestarter.database import EpromDatabase; ..."` — confirmed W27C512 info-flags=0x30 / flags=0x02 on current beta (2026-06-18)

---
*Architecture research for: Firestarter v1.14 Feasible-Gap Implementation*
*Researched: 2026-06-18*

# Phase 13: Close Gap WARNING-5 — AT28C256/64 5V EEPROM Override (12V on A14 during write)

**Researched:** 2026-05-11
**Domain:** Database pipeline override, firmware dispatch safety, 28C-family EEPROM programming
**Confidence:** HIGH — all findings verified against live codebase

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Affected chip set:** ~30 chips with `algorithm=0x07` AND `electrical.type="Flash/EEPROM"` in upstream minipro. Concrete examples: AT28C256, AT28C64, AT28C64B, AT28C64E, AT28BV64, AT28BV64B, AT28BV256, AT28C17, AT28C17E. Must distinguish from W27C512, SST27SF512, and other electrically-erasable UV-EPROMs that legitimately need 12V VPP on pin 1 — ALSO have `algorithm=0x07` + `electrical.type="Flash/EEPROM"`. The distinguishing signal is **manufacturer + chip name family prefix**, not the raw upstream protocol_id alone.
- **Fix shape:** Option (A) — override table in `build_db.py`. Single layer change, leverages existing 0x0D dispatch, keeps "build_db.py is canonical" invariant.
- **Override-table location:** Module-level constant in `build_db.py` (e.g. `_PROTOCOL_OVERRIDES`), keyed by some criterion → `{new_algorithm, new_electrical_type}`. Applied AFTER reading minipro XML but BEFORE writing `chip_entry`. Logged at run time.
- **Tests/regression:** New check in `check_dispatch.py` (or sibling) asserting every chip matching the AT28C-family pattern routes to `configure_eeprom28c`. Existing `pio test -e native -f "*test_dispatch*"` covers 0x0D dispatch already — no new firmware tests needed.
- **Documentation:** Update `firestarter_app/CLAUDE.md` to document the override table. Update REQUIREMENTS.md if a new sub-requirement is added.

### Claude's Discretion
- Exact set of `(manufacturer, name_prefix)` pairs to include in the override table (informed by RESEARCH.md).
- Logging format for the regenerator.
- Whether to add a new REQ-ID for this override or treat it as closure of WARNING-5 only.

### Deferred Ideas (OUT OF SCOPE)
- Full per-chip override mechanism beyond AT28C-family.
- Hardware verification on a real RURP shield.
- Renaming wire JSON key `"vpp"` → `"vpp_mv"` (WARNING-3).
- Adding the missing VPP ADC compare to `flash_intel_write_init` (WARNING-1).
- 28C handler chip_id check (WARNING-2).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-FW-03 | `EEPROM_POLL` (0x0D) uses DQ7 data-polling loop for AT28C010/040 page writes; SDP disable sequence applied before first write for AT28C256 | Research confirms the 0x0D handler (`eeprom_28c.cpp:eeprom28c_write_init`) is correct and complete for the 28C family. AT28C256 is currently unreachable on this path because upstream DB tags it algo=0x07. The override closes this gap. |
| REQ-SAF-01 | VPP voltage checked via ADC before first write pulse for every chip | The WARNING-5 hazard compounds REQ-SAF-01: AT28C256 on the 0x07 path applies 12V to A14 before any ADC check can fire. Moving to 0x0D eliminates VPP activation entirely for this chip family. |
</phase_requirements>

---

## Summary

Phase 13 closes the hardware-damage path introduced when Phase 12 removed the BLOCKER-1 safe-error exit for AT28C-family 5V EEPROMs. These chips carry `algorithm=0x07` in the upstream minipro database (a wrong classification — they are not UV-EPROMs) and now route through `configure_eprom`, which asserts `P1_VPP_ENABLE` during write. On the `DIP28_2764` pinout that all 23 hazardous chips use, socket pin 1 maps to RURP bus line 15 (`VPP_P1_28_DIP = 0x0F`), which triggers `using_p1_as_vpp(handle) = true`. The result: 12V reaches socket pin 1 during every write pulse. On AT28C256 (and all other 28C-family EEPROMs), socket pin 1 is the A14 address line — not VPP. The fix is a data-layer override in `build_db.py` that reclassifies these chips to `algorithm=0x0D` at DB generation time, routing them to `configure_eeprom28c` (the 5V page-write path) instead.

**IMPORTANT CORRECTION TO CONTEXT.MD SCOPE:** The audit and CONTEXT.md describe "AT28C-family by manufacturer+name prefix" as the distinguishing signal. Research reveals the actual hazardous set is 23 chips across 7 manufacturers (ATMEL, MICROCHIP memory, NEC, ST, XICOR, EXEL), all sharing the condition: `pinout == DIP28_2764` AND `algorithm == 0x07` AND `electrical.type == "Flash/EEPROM"`. The name-prefix criterion covers only 10 ATMEL AT28C/BV/PC chips and misses 13 other-manufacturer 28C-family EEPROMs. The planner must decide whether to use the name-prefix criterion (CONTEXT.md locked direction, narrower coverage) or the pinout-based criterion (broader, more precise, misses nothing).

**Primary recommendation:** Apply a data-condition override in `build_db.py` — no firmware changes required. The 0x0D handler already exists, is correct for AT28C256, and never activates VPP.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Chip classification (algo override) | Database Pipeline (`build_db.py`) | — | REQ-DB-05 designates `build_db.py` as the single canonical DB build tool; this is a data-layer fix |
| Protocol dispatch (0x0D routing) | Firmware (`memory.cpp`) | — | Already wired; no change needed |
| Wire-format algorithm field | Python Host (`database.py`) | — | `_ALGO_MEM_TYPE[0x0D]=1` already present; no change needed |
| Regression assertion | Python Test (`check_dispatch.py`) | — | Mirrors firmware dispatch in Python for CI |
| Documentation | `firestarter_app/CLAUDE.md` | — | Describes the override mechanism for future maintainers |

---

## Domain Knowledge

### 1. Exact Hazardous Chip Set (VERIFIED)

**Total `algo=0x07` + `type="Flash/EEPROM"` chips in the regenerated DB: 30.** [VERIFIED: live DB scan]

These 30 chips split into three pinout groups:

| Pinout | Count | VPP pin (socket) | Status |
|--------|-------|-----------------|--------|
| `DIP28_2764` | **23** | Pin 1 (= A14 on 28C EEPROMs) | **HAZARDOUS — needs override** |
| `DIP28_27256` | 4 | Pin 1 (= VPP on W27C257/SST27SF256) | Safe — genuine UV-EPROMs needing VPP |
| `DIP28_27512` | 3 | Pin 22 (= VPP/OE on W27C512) | Safe — W27C512 etc., pin 1 = A14 address |

**The 23 hazardous DIP28_2764 chips (all 5V EEPROMs, no external VPP):** [VERIFIED: live DB scan]

| Manufacturer | Part Number | vpp_mv in DB |
|---|---|---|
| ATMEL | AT28BV64 / AT28BV64B / AT28BV256 | 0 (BV = battery voltage, low-power) |
| ATMEL | AT28C17 / AT28C17E | 12000 (upstream mistag) |
| ATMEL | AT28C256 / AT28C64 / AT28C64B / AT28C64E / AT28PC64 | 12000 (upstream mistag) |
| MICROCHIP memory | 28C17A / 28C17AF / 28C64A / 28C64AF / 28C64B / 28C256 / 28LV64A | 12000 or 0 |
| NEC | UPD28C64 / UPD28C256 | 12000 |
| ST | M28256 | 12000 |
| XICOR | X28C64 / X28C64(NonStandard) | 12000 |
| EXEL | XLE2865A | 12000 |

**The 7 safe chips (stay on 0x07 path):** W27C257, W27E257 (Winbond, DIP28_27256); SST27SF256, SST27VF256 (SST, DIP28_27256); W27C512, SST27SF512, SST27VF512 (DIP28_27512). These are electrically-erasable UV-EPROMs that genuinely need 12V VPP on pin 1.

**CORRECTION TO CONTEXT.MD "~30 chips" CLAIM:** The 30-chip count is the full `algo=0x07 + Flash/EEPROM` population. The *hazardous* subset is 23 chips (DIP28_2764 only). 7 chips are correctly on the 0x07 path. [VERIFIED: live DB scan]

### 2. Pinout Sanity Check — Confirmed Hazard Path (VERIFIED)

The CONTEXT.md notes some ambiguity about whether AT28C256 pin 1 = /WE or A14. The actual datasheet pinout and the code trace confirm: **pin 1 = A14 (high address line)**. [ASSUMED from hardware domain knowledge; no datasheet fetched]

The firmware trace: [VERIFIED: code inspection]

1. `DIP28_2764` pinout has `vpp-pin: [1]` in `pinouts.json`. [VERIFIED]
2. `database.py:get_bus_config` maps DIP28 pin 1 → RURP bus line 15 via `pin_conversions[28][1] = 15`. [VERIFIED]
3. `VPP_P1_28_DIP = 0x0F = 15` (from `rurp_shield.h`). [VERIFIED]
4. `using_p1_as_vpp(handle)` returns `true` when `handle->pins < 32 && handle->bus_config.vpp_line == 0x0F`. For AT28C256 (28-pin, DIP28_2764): **true**. [VERIFIED]
5. In `eprom_write_execute` → `program_mismatched_bytes`: sets `VPE_ENABLE` bit. [VERIFIED]
6. `eprom_internal_set_control_register` intercepts `VPE_ENABLE` and flips to `P1_VPP_ENABLE` when `using_p1_as_vpp` is true. [VERIFIED: eprom.cpp line 269-271]
7. `P1_VPP_ENABLE = 0x08` routes the VPP regulator output to RURP bus line 15 = socket pin 1. [VERIFIED]
8. On AT28C256, socket pin 1 = physical chip pin 1 = A14. 12V on A14 exceeds absolute maximum for a 5V CMOS EEPROM. [ASSUMED: standard CMOS abs-max is typically VCC+0.5V = 5.5V max on logic pins]

**Secondary hazard: DIP28_27256 chips also have `using_p1_as_vpp=True`** because their `vpp-pin=[1]`. However, the DIP28_27256 chips in this set (W27C257, SST27SF256, etc.) ARE genuine UV-EPROMs whose physical pin 1 IS their VPP pin. The fix criterion must be pinout-specific: `DIP28_2764` only.

### 3. 0x0D Handler Correctness for AT28C256 (VERIFIED)

The `configure_eeprom28c` handler in `firestarter/src/proms/eeprom_28c.cpp` is correct and complete for the 28C family. [VERIFIED: full source inspection]

**SDP disable sequence:** `EEPROM_SDP_DISABLE` is a 6-write sequence: AA→5555, 55→2AAA, 80→5555, AA→5555, 55→2AAA, 20→5555. This matches the AT28C256 Software Data Protection disable procedure. [VERIFIED: code matches standard AT28C256 SDP disable]

Note: CONTEXT.md section says "AA/55/A0 byte pattern" — that is actually the SDP *enable* sequence (3 writes). The *disable* sequence is the 6-write sequence coded in `EEPROM_SDP_DISABLE`. The code is correct; the CONTEXT comment is imprecise.

**DQ7 polling:** `eeprom28c_wait_for_write` polls by full-byte comparison (`observed == expected`). This is functionally equivalent to DQ7 polarity detection: AT28C256 inverts DQ7 during an internal write cycle; when the cycle completes, DQ7 returns to its programmed state and the full byte matches. The implementation correctly uses a 2000-iteration loop with 10µs delays (20ms max timeout). [VERIFIED]

**Page write (64 bytes):** `PAGE_SIZE = 64`. `eeprom28c_write_execute` accumulates up to 64 bytes per page (`(address + 1) % PAGE_SIZE == 0`) and polls after each page completion. AT28C256 has a 64-byte page buffer, so this is correct. [VERIFIED]

**No VPP activation:** `configure_eeprom28c` and its subordinate functions (`eeprom28c_write_init`, `eeprom28c_write_execute`, `flash_util_byte_flipping`) contain zero calls to `REGULATOR`, `VPE_TO_VPP`, `VPE_ENABLE`, `P1_VPP_ENABLE`, `A9_VPP_ENABLE`, or `eprom_check_vpp`. The handler is purely 5V VCC, no VPP regulator involvement. [VERIFIED]

**chip_id handling:** `eeprom28c_write_init` does not check `handle->chip_id` (WARNING-2). However, all 23 hazardous chips have `chip_id_check=False` and `chip_id_value=0x00000000` in the DB. Moving them to 0x0D loses no chip-ID safety gate that existed before. [VERIFIED: DB scan confirms 0/23 chips have chip_id_check=True]

**pulse_delay:** `configure_eeprom28c` sets `handle->pulse_delay = 0`. This is correct — 28C EEPROMs use internal timing for write cycles; no external pulse delay is needed. [VERIFIED]

**vpp_mv field in wire JSON after override:** After the override sets `algorithm=0x0D`, `database.py:_ALGO_MEM_TYPE[0x0D] = 1` still produces `wire type=1`. The `vpp_mv` field is still transmitted (e.g., 12000 for chips that had it), but `configure_eeprom28c` never reads `handle->vpp_mv` and never calls `eprom_check_vpp`. The wire field is harmlessly ignored. [VERIFIED]

**Conclusion:** The 0x0D handler is fully correct for AT28C256 and the 28C family. No firmware changes are needed.

### 4. `_PROTOCOL_OVERRIDES` Table Shape and Placement (VERIFIED)

Current module-top constants in `build_db.py` (in order of definition): [VERIFIED: source inspection]

```python
# Line ~25
PROTOCOL_MAP = {0x05: "FLASH_AMD_STD", 0x06: "FLASH_AMD_ALT", ...}  # lines 25-44
VPP_VOLTAGES = {...}  # lines 46-80
VPP_MV = {...}        # lines 82-87
KNOWN_PROTOCOLS = {0x05, 0x06, ...}  # line 89
VCC_VOLTAGES = {...}  # line 91
DIP28_VARIANT_MAP = {...}  # lines 93-98
```

**Proposed placement:** After `KNOWN_PROTOCOLS` (line 89), before `VCC_VOLTAGES`. This keeps all data-classification constants grouped together.

**Proposed shape — two design options for the planner:**

**Option B (research recommendation — pinout-based condition):**

```python
# Safety override: 28C-family 5V EEPROMs mistagged as EPROM_STD (0x07) in upstream minipro DB.
# All these chips use DIP28_2764 pinout (vpp-pin=1 → P1_VPP_ENABLE in configure_eprom).
# Their physical pin 1 is A14 (address line), NOT VPP. Applying 12V to A14 = hardware damage.
# Override algorithm to 0x0D (EEPROM_POLL) so configure_eeprom28c (5V page-write, no VPP) fires.
# Condition: (pinout_key == "DIP28_2764") AND (proto_id == 0x07) AND (_etype == "Flash/EEPROM")
# Reference: WARNING-5 in INTEGRATION-CHECK.md and v1.0-MILESTONE-AUDIT.md.
_EEPROM28C_OVERRIDE = {
    "algorithm": 0x0D,
    "electrical_type": "Flash/EEPROM",  # type unchanged — database.py uses _ALGO_MEM_TYPE, not type string
}
```

Applied in `main()` after `chip_entry` is built, before `chips.append(chip_entry)`:

```python
# Apply WARNING-5 safety override: DIP28_2764 chips on 0x07 path are 5V EEPROMs, not UV-EPROMs.
if (pinout_key == "DIP28_2764"
        and proto_id == 0x07
        and _etype == "Flash/EEPROM"):
    print(f"INFO: override {name} algorithm 0x07→0x0D (WARNING-5 safety, DIP28_2764 5V EEPROM)", file=sys.stderr)
    chip_entry["programming"]["algorithm"] = _EEPROM28C_OVERRIDE["algorithm"]
```

**Option A (CONTEXT.md preference — name-prefix condition):**

```python
# Keyed by (manufacturer, name_prefix_lowercase) → {algorithm, electrical_type}
_PROTOCOL_OVERRIDES = {
    ("ATMEL", "at28"): {"algorithm": 0x0D},
    # Note: does NOT cover Microchip 28Cxx, NEC UPD28Cxx, ST M28256, XICOR X28C64, EXEL XLE2865A
    # See RESEARCH.md for the complete hazardous set.
}
```

**CRITICAL OPEN QUESTION (must be resolved before PLAN.md):** The CONTEXT.md says "manufacturer + chip name family prefix" but this criterion covers only 10 ATMEL AT28C/BV/PC chips, missing 13 other chips with the same hazard. The planner must choose:
- Use the pinout-based condition (broader, covers all 23, no regex)
- Use the name-prefix condition (CONTEXT.md-preferred, narrower, leaves 13 chips in the hazard path)

**Application location in `main()`:** After line 241 (`chip_entry = {...}`), before line 243 (`chips.append(chip_entry)`).

### 5. `_ALGO_MEM_TYPE` Compatibility Check (VERIFIED)

`database.py:_ALGO_MEM_TYPE[0x0D] = 1` (TYPE_EPROM). After the override sets `algorithm=0x0D`, `_map_data` will look up `_ALGO_MEM_TYPE[0x0D] = 1` and emit `wire type=1`. Firmware dispatches on `handle->protocol = 0x0D` via the protocol-prefix chain (step 2 in `configure_memory`), which fires before any `mem_type` check. The `mem_type=1` in the wire JSON is consistent and correct as a fallback if an older host version omits the `algorithm` field. **No change to `database.py` is needed.** [VERIFIED]

### 6. `check_dispatch.py` Regression Assertion Design (VERIFIED)

Current `check_dispatch.py` asserts:
1. Every chip has a valid dispatch path (not ERROR)
2. No SRAM-protocol chip routes to `configure_eprom`

**New assertion required (WARNING-5 guard):**

```python
# New: 28C EEPROM safety guard.
# Any chip with pinout=DIP28_2764 AND electrical.type="Flash/EEPROM"
# must dispatch to configure_eeprom28c, NOT configure_eprom.
# (If it dispatches to configure_eprom, 12V P1_VPP is applied to A14.)
_28C_EEPROM_HAZARD_PINOUT = "DIP28_2764"

# In the main loop:
pinout = chip.get("pinout", "")
etype = chip.get("electrical", {}).get("type", "")
if pinout == _28C_EEPROM_HAZARD_PINOUT and etype == "Flash/EEPROM":
    if handler == "configure_eprom":
        at28c_in_eprom.append(
            f"{mfg}/{part} proto=0x{proto:02X} pinout={pinout}"
        )

# In the exit block:
if at28c_in_eprom:
    print(
        f"FAIL: {len(at28c_in_eprom)} DIP28_2764 Flash/EEPROM chips route to "
        f"configure_eprom (WARNING-5: 12V on A14 hazard):"
    )
    for e in at28c_in_eprom[:20]:
        print(f"  {e}")
    sys.exit(1)

# And in the PASS message:
print(
    f"PASS: all {total} chips have a valid dispatch path; "
    f"0 SRAM chips route to configure_eprom; "
    f"0 DIP28_2764 Flash/EEPROM chips route to configure_eprom"
)
```

**Dry-run on current (pre-fix) DB:** This assertion finds 23 violations, exits with code 1. [VERIFIED: live dry-run]

**After DB regeneration with fix:** All 23 chips have `algorithm=0x0D`, dispatch to `configure_eeprom28c`, assertion finds 0 violations, exits 0.

**W27C512/W27C257/SST27SF512 regression:** These chips have `pinout=DIP28_27512` or `pinout=DIP28_27256` (NOT `DIP28_2764`), so they are outside the new assertion's scope. They continue dispatching to `configure_eprom` without triggering the guard. [VERIFIED: DB scan confirms they are DIP28_27512/27256]

---

## Architecture Patterns

### System Architecture Diagram

```
infoic.xml (upstream minipro)
     ↓
build_db.py: parse → filter → derive _etype/proto_id → build chip_entry
                                                              ↓
                              [NEW] if pinout==DIP28_2764 + proto_id==0x07 + Flash/EEPROM
                                    → override algorithm: 0x07 → 0x0D (WARNING-5 fix)
                                    → log override to stderr (auditable)
                                              ↓
minipro_complete_db.json [23 chips now have algorithm=0x0D]
     ↓
database.py:_map_data
  protocol_id = programming["algorithm"]  → 0x0D
  determined_type = _ALGO_MEM_TYPE[0x0D]  → 1 (TYPE_EPROM, unchanged)
  wire "algorithm" = 0x0D, "type" = 1
     ↓
firmware json_parser.c → handle->protocol = 0x0D
     ↓
memory.cpp:configure_memory → step 2: protocol==0x0D → configure_eeprom28c() → RETURN
  (never reaches step 5: protocol∈{0x07,0x08,0x0B} → configure_eprom)
     ↓
eeprom_28c.cpp:eeprom28c_write_init
  → flash_execute_command(EEPROM_SDP_DISABLE) [6-write SDP disable]
  → eeprom28c_wait_for_write [DQ7 polling]
  → NO REGULATOR, NO VPE_ENABLE, NO P1_VPP_ENABLE
     ↓
eeprom28c_write_execute
  → 64-byte page writes via firestarter_set_data
  → eeprom28c_wait_for_write [DQ7 poll per page]
```

### Recommended Project Structure

No new directories needed. All changes are within existing files:

```
firestarter_app/
├── tools/
│   ├── build_db.py        [MODIFY: add _EEPROM28C_OVERRIDE / _PROTOCOL_OVERRIDES + apply in main()]
│   └── check_dispatch.py  [MODIFY: add _28C_EEPROM_HAZARD_PINOUT guard]
└── firestarter/
    ├── data/
    │   └── minipro_complete_db.json  [REGENERATE: python3 tools/build_db.py]
    └── CLAUDE.md                     [MODIFY: document override mechanism]
```

### Pattern: Data-Layer Override at Emit Time

```python
# Source: existing build_db.py SRAM override pattern (Phase 12, lines 214-219)
# Analogous: _etype = "SRAM" for SRAM proto_ids overrides the flags&0x10 heuristic
# New pattern: override algorithm field for mistagged 5V EEPROMs

# AFTER chip_entry dict is built, BEFORE chips.append()
if (pinout_key == "DIP28_2764"
        and proto_id == 0x07
        and _etype == "Flash/EEPROM"):
    print(f"INFO: {name} algorithm override 0x07→0x0D (WARNING-5 mitigation)", file=sys.stderr)
    chip_entry["programming"]["algorithm"] = 0x0D
```

The logging format: `INFO: <name> algorithm override 0x07→0x0D (WARNING-5 mitigation)`. This is parseable (structured enough for grep) and non-intrusive (goes to stderr, not stdout which carries the final count).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Chip-ID detection for 28C EEPROMs | Custom chip-ID read in override logic | None needed — all 23 chips have `chip_id_check=False` | No chip_id data exists for these chips in upstream DB |
| VPP validation for 5V path | New VPP-check bypass flag | None — 0x0D handler never activates VPP | VPP circuitry is simply not engaged on the 0x0D path |
| Name regex for 28C family | Regex across name string | Pinout condition (`pinout_key == "DIP28_2764"`) | More precise, no false positives, covers all manufacturers |
| New firmware handler | Custom EEPROM handler | `configure_eeprom28c` (0x0D) already implements correct behavior | Handler already exists and works; data-layer fix is sufficient |

**Key insight:** The 0x0D handler already exists and is correct. This is entirely a data-layer classification fix — no firmware changes of any kind are needed.

---

## Common Pitfalls

### Pitfall 1: Narrow Override Criterion (Misses 13 Chips)
**Severity:** HIGH — 13 chips remain in hardware-damage path

**What goes wrong:** Using only `manufacturer == "ATMEL" and name.startswith("AT28")` covers 10 chips (ATMEL AT28C/BV/PC family) but leaves 13 other-manufacturer 28C-family EEPROMs (Microchip 28Cxx, NEC UPD28Cxx, ST M28256, XICOR X28C64, EXEL XLE2865A) still routing to `configure_eprom` with 12V on A14.

**Why it happens:** The CONTEXT.md names "AT28C-family" as the example set but the actual hazard spans 7 manufacturers. The upstream minipro DB classifies all these chips identically (algo=0x07, Flash/EEPROM, DIP28_2764).

**How to avoid:** Use the pinout-based condition: `pinout_key == "DIP28_2764" AND proto_id == 0x07 AND _etype == "Flash/EEPROM"`. This is a purely mechanical data condition, requires no name matching, and covers all 23 hazardous chips exactly.

**Warning signs:** `check_dispatch.py` with the new `_28C_EEPROM_HAZARD_PINOUT` guard will still report failures after a name-only override (13 remaining chips).

### Pitfall 2: Applying Override Before `pinout_key` Is Resolved
**Severity:** MEDIUM — override applied to wrong chips

**What goes wrong:** If the override check runs before `resolve_pinout_key()` is called, `pinout_key` is not yet set. The condition `pinout_key == "DIP28_2764"` always evaluates False, and no chips get overridden.

**How to avoid:** The override check must execute after line 209 (`pinout_key = resolve_pinout_key(...)`) and after `_etype` is derived (lines 214-219). Apply override between the `chip_entry` dict construction (line 221) and `chips.append(chip_entry)` (line 243).

**Warning signs:** Regenerated DB still shows 23 chips with `algorithm=7`; `check_dispatch.py` still fails with 23 violations.

### Pitfall 3: Changing `vpp_mv` Field During Override
**Severity:** LOW — harmless but confusing

**What goes wrong:** An override that also sets `chip_entry["electrical"]["vpp_mv"] = 0` is tempting (5V EEPROMs don't need external VPP) but unnecessary. The 0x0D handler never reads `handle->vpp_mv`; the firmware does not validate VPP for `configure_eeprom28c`. Zeroing out `vpp_mv` adds noise to the DB diff without functional benefit.

**How to avoid:** Override `algorithm` only. Leave `vpp_mv` as-is from the upstream DB.

### Pitfall 4: Forgetting the X28C64(NonStandard) variant
**Severity:** LOW — incomplete fix, leaves one chip at risk

**What goes wrong:** Name-prefix matching might miss `X28C64(NonStandard)` if the prefix check doesn't handle the parenthesized suffix. The pinout-based condition captures it automatically.

**Why it happens:** The part_number in the DB is stored as `"X28C64(NonStandard),X28C64(NonStandard)"` (includes the alternate name). A startswith check on `"X28C64"` would catch it, but only if XICOR is explicitly listed.

**How to avoid:** Use the pinout condition, which is immune to name format variations.

### Pitfall 5: check_dispatch.py Assertion Using Name Instead of Pinout
**Severity:** MEDIUM — assertion doesn't catch future regressions

**What goes wrong:** Writing the assertion as "if manufacturer is ATMEL and name starts with AT28, assert configure_eeprom28c" creates a brittle test that only validates the 10 ATMEL chips and won't catch if a new 28C-family chip is added from a different manufacturer.

**How to avoid:** Base the assertion on `chip["pinout"] == "DIP28_2764"` AND `chip["electrical"]["type"] == "Flash/EEPROM"`. This is the structural invariant, not the name pattern.

### Pitfall 6: DQ7 Polling Incompatibility with Non-SDP 28C variants
**Severity:** MEDIUM — AT28C17 and AT28BV64 may behave differently

**What goes wrong:** The 0x0D handler calls `flash_execute_command(EEPROM_SDP_DISABLE)` unconditionally before every write. If a chip variant does not implement SDP (Software Data Protection), this 6-write sequence is harmless (writes to random addresses will be accepted or ignored by the EEPROM's normal write logic). However, for the AT28C17 (2Kx8), the address `0x5555` (21845 decimal) exceeds the chip's 2KB address space. This write attempt goes to a wrapped or non-existent address and should be harmless but is technically out-of-spec.

**How to avoid:** This is an existing behavior of the 0x0D handler for all chips it currently handles (AT28C010/040). The Phase 06 implementation chose to always run the SDP disable regardless of chip size. The planner should note this as a KNOWN LIMITATION but not block the fix. It is out of scope for Phase 13 per CONTEXT.md.

**Warning signs:** None observable without hardware; the write attempt to out-of-range addresses has no effect on 5V CMOS EEPROMs.

---

## Code Examples

### Existing SRAM override pattern (Phase 12 precedent)

```python
# Source: firestarter_app/tools/build_db.py lines 214-219
# Phase 12 precedent: _etype override for SRAM protocols
if proto_id in {0x0E, 0x27, 0x28, 0x29}:
    _etype = "SRAM"
elif flags & 0x10:
    _etype = "Flash/EEPROM"
else:
    _etype = "UV-EPROM"
```

### Proposed override application (after chip_entry construction)

```python
# Source: proposed change — apply after chip_entry dict is built (after line 241)
# BEFORE chips.append(chip_entry) (line 243)
#
# WARNING-5 mitigation: DIP28_2764 chips with algo=0x07 and Flash/EEPROM type
# are 5V EEPROMs mistagged as UV-EPROMs by upstream minipro.
# configure_eprom would assert P1_VPP_ENABLE → 12V on socket pin 1 = A14 = hardware damage.
# Route to configure_eeprom28c (0x0D) instead: 5V page-write, no VPP regulator.
if (pinout_key == "DIP28_2764"
        and proto_id == 0x07
        and _etype == "Flash/EEPROM"):
    print(
        f"INFO: {name} algorithm override 0x07→0x0D "
        f"(WARNING-5: 5V EEPROM mistagged as UV-EPROM)",
        file=sys.stderr,
    )
    chip_entry["programming"]["algorithm"] = 0x0D
```

### New check_dispatch.py guard (WARNING-5 assertion)

```python
# Source: proposed change — add to check_dispatch.py main loop alongside _SRAM_PROTOCOLS guard
_28C_EEPROM_HAZARD_PINOUT = "DIP28_2764"

# In main loop, after handler is resolved:
pinout = chip.get("pinout", "")
etype = chip.get("electrical", {}).get("type", "")
if (pinout == _28C_EEPROM_HAZARD_PINOUT
        and etype == "Flash/EEPROM"
        and handler == "configure_eprom"):
    at28c_in_eprom.append(
        f"{mfg}/{part} proto=0x{proto:02X} pinout={pinout}"
    )

# In exit block:
if at28c_in_eprom:
    print(
        f"FAIL: {len(at28c_in_eprom)} DIP28_2764 Flash/EEPROM chips route to "
        f"configure_eprom (WARNING-5: 12V on A14 hazard):"
    )
    for e in at28c_in_eprom[:20]:
        print(f"  {e}")
    sys.exit(1)
```

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib (no external test framework for check_dispatch.py) + Unity for firmware |
| Config file | `firestarter/platformio.ini` (`[env:native]`) |
| Quick run command (Python regression) | `python3 firestarter_app/tools/check_dispatch.py` |
| Full suite command | `python3 firestarter_app/tools/check_dispatch.py && cd firestarter && pio test -e native -f "*test_dispatch*" && pio run -e uno && pio run -e leonardo` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-FW-03 | AT28C256 dispatches to `configure_eeprom28c`, not `configure_eprom` | integration (DB scan) | `python3 firestarter_app/tools/check_dispatch.py` | ✅ (needs new assertion added in Wave 0) |
| REQ-SAF-01 | No DIP28_2764 Flash/EEPROM chip routes to `configure_eprom` (12V on A14) | integration (DB scan) | `python3 firestarter_app/tools/check_dispatch.py` | ✅ (same file, same assertion) |

### Sampling Rate

- **Per task commit:** `python3 firestarter_app/tools/check_dispatch.py`
- **Per wave merge:** Full suite above
- **Phase gate:** `check_dispatch.py` PASS (0 DIP28_2764 hazard + 0 SRAM violations) + `pio test -e native -f "*test_dispatch*"` 15/15 PASS

### Wave 0 Gaps

- [ ] `firestarter_app/tools/check_dispatch.py` — add `_28C_EEPROM_HAZARD_PINOUT` assertion (covers REQ-FW-03, REQ-SAF-01). This assertion should be added in Wave 0 and will initially FAIL (23 violations) until the `build_db.py` fix is applied and the DB is regenerated.

*(No new test files needed; no framework install needed; no firmware test changes needed.)*

---

## Recommended Wave Breakdown

### Wave 0 — Test Infra (pre-fix assertion)
**Goal:** Add the safety assertion to `check_dispatch.py` so the hazard is formally caught before the fix is applied.

| Task | File | Change |
|------|------|--------|
| Add `_28C_EEPROM_HAZARD_PINOUT` guard to `check_dispatch.py` | `firestarter_app/tools/check_dispatch.py` | Add guard, update PASS message |
| Verify the assertion FAILS on current DB (23 violations) | — | Run `python3 check_dispatch.py` → expect exit 1 |

**Exit criterion:** `check_dispatch.py` exits 1 with `FAIL: 23 DIP28_2764 Flash/EEPROM chips route to configure_eprom`.

### Wave 1 — Fix Application
**Goal:** Add the `_PROTOCOL_OVERRIDES` / `_EEPROM28C_OVERRIDE` constant and apply it in `build_db.py`.

| Task | File | Change |
|------|------|--------|
| Add override constant at module top | `firestarter_app/tools/build_db.py` | Add `_EEPROM28C_OVERRIDE` after `KNOWN_PROTOCOLS` |
| Apply override in `main()` after chip_entry construction | `firestarter_app/tools/build_db.py` | Add conditional override block |
| Verify override is applied during regeneration (check stderr output) | — | `python3 build_db.py 2>&1 \| grep INFO` → expect 23 override messages |

**Exit criterion:** Regenerated DB is NOT yet applied; source code change is reviewed and committed.

### Wave 2 — Regenerate and Verify
**Goal:** Regenerate the DB and confirm `check_dispatch.py` PASS.

| Task | File | Change |
|------|------|--------|
| Regenerate `minipro_complete_db.json` | `firestarter_app/firestarter/data/minipro_complete_db.json` | `python3 tools/build_db.py` |
| Verify DB has 23 chips with algorithm=0x0D (was 0x07) | — | Python count check |
| Run `check_dispatch.py` and confirm PASS | — | exit 0, 0 hazard violations |
| Run `pio test -e native` confirm 15/15 still PASS | — | No firmware changes; dispatch tests must still pass |
| Run `pio run -e uno` and `pio run -e leonardo` | — | Firmware builds must still succeed |

**Exit criterion:** `check_dispatch.py` exits 0. `pio test -e native -f "*test_dispatch*"` 15/15 PASS. Both AVR targets build SUCCESS.

### Wave 3 — Documentation
**Goal:** Update `firestarter_app/CLAUDE.md` to document the override mechanism.

| Task | File | Change |
|------|------|--------|
| Document `_PROTOCOL_OVERRIDES` / `_EEPROM28C_OVERRIDE` in CLAUDE.md | `firestarter_app/CLAUDE.md` | Add section under Database Pipeline explaining the WARNING-5 override |

**Note on REQUIREMENTS.md:** No new REQ-ID is strictly required — this closes WARNING-5 which is a safety gap under existing REQ-SAF-01 and REQ-FW-03. The planner may add `REQ-DB-06: protocol override for upstream-mistagged chips` at their discretion.

---

## Open Questions

1. **Override criterion: name-prefix vs. pinout-based**
   - What we know: CONTEXT.md says "manufacturer + chip name family prefix" (covers 10 ATMEL AT28C chips). Research confirms the actual hazardous set is 23 chips across 7 manufacturers, all identifiable by `pinout=DIP28_2764 + algo=0x07 + Flash/EEPROM`.
   - What's unclear: Is the planner aware that the name-prefix criterion in CONTEXT.md is incomplete? Does the locked decision "manufacturer + chip name family prefix" need to be revised, or does it intentionally accept 13 unprotected chips for now?
   - Recommendation: Use the pinout-based condition. It is more comprehensive, mechanical, and requires no regex or manufacturer enumeration.

2. **Microchip, NEC, ST, XICOR, EXEL 28C chips: same architecture as AT28C256?**
   - What we know: All 13 chips are in the DB with `algo=0x07`, `Flash/EEPROM`, `DIP28_2764`. They are named with the "28C" designation indicating 28C-family CMOS EEPROM architecture.
   - What's unclear: Whether these specific parts (M28256, UPD28C64, X28C64, 28C17A, XLE2865A) support the standard 28C SDP-disable sequence and 64-byte page write.
   - Recommendation: The conservative approach is to include them in the override (avoids VPP damage; if the 0x0D sequence doesn't work perfectly, write fails cleanly rather than causing hardware damage). This is out-of-scope for hardware verification per CONTEXT.md.

3. **X28C64(NonStandard) — should it be included?**
   - What we know: Xicor X28C64(NonStandard) is a 5V EEPROM on DIP28_2764 with algo=0x07. It has the same hardware-damage risk if left on the 0x07 path. The "NonStandard" designation suggests its programming sequence differs from standard AT28C; however, its operating voltage is 5V, so applying no VPP and using 0x0D will at worst fail to write (not damage).
   - Recommendation: Include it in the override. Worst case is a write error with a "NonStandard" chip; failure to include it risks hardware damage.

4. **New REQ-ID or not?**
   - What we know: REQ-FW-03 and REQ-SAF-01 both point to this gap. The fix is a data-pipeline change (REQ-DB territory).
   - Recommendation: Add `REQ-DB-06: build_db.py applies protocol overrides for upstream-mistagged chips to prevent hardware-hazard dispatch paths.` This gives the override mechanism a permanent home in the requirements. Optional — the planner decides.

---

## Environment Availability

Step 2.6: SKIPPED for firmware — no external dependencies beyond existing toolchain.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | `build_db.py`, `check_dispatch.py` | ✓ | system Python | — |
| Network access (gitlab.com) | `python3 tools/build_db.py` fetches `infoic.xml` | ✓ (dev container) | — | Use cached `infoic.xml` if network unavailable |
| PlatformIO native env | `pio test -e native` | ✓ (Phase 12 verified) | Phase 12 `[env:native]` confirmed working | — |

---

## Project Constraints (from CLAUDE.md)

- `firestarter/` and `firestarter_app/` are sub-repos; changes must be made in those directories
- `minipro_complete_db.json` must not be edited by hand — only regenerated via `build_db.py`
- Constants duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h` must stay in sync — **no constants affected by Phase 13**
- Wire protocol changes (if any) must be reflected in both `serial_comm.py` and `firestarter.cpp` — **no wire protocol changes in Phase 13**
- Serial protocol runs at 250000 baud — **no change**

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | AT28C256 pin 1 = A14 (address line); 12V exceeds absolute maximum for CMOS 5V logic | Domain Knowledge §2 | If pin 1 had some voltage tolerance up to 12V, the hazard would be reduced but not eliminated. Datasheet verification would confirm. |
| A2 | Microchip 28Cxx, NEC UPD28Cxx, ST M28256, XICOR X28C64, EXEL XLE2865A are 5V EEPROMs compatible with the 28C page-write protocol | Domain Knowledge §1 | If any of these chips require a non-standard write sequence, the 0x0D handler might fail to write them correctly. Hardware damage risk is eliminated regardless. |
| A3 | X28C64(NonStandard) does not require external VPP for write operations | Open Questions §3 | If it requires VPP on a different pin, moving to 0x0D would fail-to-write rather than damage. Risk is functional failure only. |

---

## Sources

### Primary (HIGH confidence)
- `firestarter_app/tools/build_db.py` — verified module-top constants, main() flow, override placement point
- `firestarter_app/tools/check_dispatch.py` — verified current assertion structure, proposed extension
- `firestarter_app/firestarter/database.py` — verified `_ALGO_MEM_TYPE` table, `_map_data` dispatch path
- `firestarter/src/proms/eeprom_28c.cpp` — verified SDP disable sequence, DQ7 polling, page write, no-VPP
- `firestarter/src/proms/eprom.cpp` — verified `eprom_internal_set_control_register` VPE→P1_VPP flip
- `firestarter/include/memory_utils.h` — verified `using_p1_as_vpp` definition and `VPP_P1_28_DIP=0x0F`
- `firestarter/include/rurp_shield.h` — verified `VPP_P1_28_DIP=0x0F`, `P1_VPP_ENABLE=0x08`
- `firestarter_app/firestarter/data/pinouts.json` — verified `DIP28_2764 vpp-pin=[1]`, `DIP28_27512 vpp-pin=[22]`
- `firestarter_app/firestarter/data/minipro_complete_db.json` — verified chip counts, pinout distributions, chip_id fields
- Live DB scans (Python scripts run during research) — verified all counts and dispatch dry-runs

### Secondary (MEDIUM confidence)
- `.planning/INTEGRATION-CHECK.md` — WARNING-5 firmware trace (independently verified against source)
- `.planning/v1.0-MILESTONE-AUDIT.md` — WARNING-5 scope definition (independently verified against DB)
- `.planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-VERIFICATION.md` — Phase 12 dispatch order baseline

### Tertiary (LOW confidence / ASSUMED)
- AT28C256 absolute maximum voltage on logic pins — assumed standard CMOS 5.5V from domain knowledge [A1]

---

## Metadata

**Confidence breakdown:**
- Chip set enumeration: HIGH — verified live against regenerated DB
- Pinout/hazard mechanism: HIGH — verified through complete firmware trace
- 0x0D handler correctness: HIGH — full source inspection
- Fix shape: HIGH — verified against existing patterns in the codebase
- Non-AT28 chips' 28C compatibility: MEDIUM — inferred from naming convention, not datasheet-verified

**Research date:** 2026-05-11
**Valid until:** 2026-06-11 (stable domain — upstream minipro DB changes rarely; firmware is not under active development)

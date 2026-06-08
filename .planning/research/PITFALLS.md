# Pitfalls Research

**Domain:** EPROM programmer — infoic.xml decode re-derivation + new firmware write-path handlers (Firestarter v1.11)
**Researched:** 2026-06-08
**Confidence:** HIGH (grounded in build_db.py override comments, firmware source, pinouts.json, check_dispatch.py, and audit_coverage_matrix.py findings)

---

## 1. Hardware-Damage Hazard Taxonomy

Every damage class below is a consequence of the RURP shield asserting voltage to the wrong socket pin. The shield's control register has three VPP routing bits: `CTRL_VPP_A9_ENABLE` (routes regulator output to address line A9), `CTRL_VPE_ENABLE` / `CTRL_VPP_P1_ENABLE` (routes to the PGM/VPP pin — either the DIP-edge pin or socket pin 1 depending on `using_p1_as_vpp()`), and `CTRL_VPP_REGULATOR_ENABLE` (powers the boost converter). The damage path always starts with one of those bits being asserted for the wrong chip family.

### H-1: Wrong-Pin VPP — Address Line Receives 12V+

**What goes wrong:**
`configure_eprom` asserts `CTRL_VPP_REGULATOR_ENABLE` + `CTRL_VPE_ENABLE` or `CTRL_VPP_P1_ENABLE` during every write pulse. If the chip seated in the socket has its VPP pin routed to a different physical location than the pinout entry expects, 12V lands on an address line, a data line, or a control signal.

**Concrete instances in the existing codebase:**

- WARNING-5 (DIP28_2764 + 0x07 + Flash/EEPROM): socket pin 1 is the VPP line on `DIP28_2764`. On genuine UV-EPROMs (2764/27128) pin 1 IS VPP. On 28C-family 5V EEPROMs the same pinout class is reused but pin 1 is A14. The 0x07 EPROM_STD handler fires `CTRL_VPP_P1_ENABLE` → 12V on A14 → damage.
- fm1608 (type=4 FRAM, proto=0x07/0x0B): Ramtron FRAMs are tagged SRAM-class in infoic.xml (`type=4`) but carry EPROM-family `protocol_id`. The EPROM handler would fire P1_VPP_ENABLE on pin 1, which on the JEDEC SRAM pinout is address line A13 → damage.
- 24-pin 5V EEPROM SAFETY SKIP (AT28C04/16 etc.): `DIP24_2716` routes `vpp-pin = [21]`. On a genuine 2716, pin 21 is the OE/VPP shared pin. On a 24-pin 5V EEPROM (AT28C04, AT28C16) pin 21 is WE. The EPROM handler's `CTRL_VPE_ENABLE` (VPP to PGM-equivalent pin = pin 21) hits WE → 12V on write-enable input → damage.
- 27512 vs 27256 pinout swap: `DIP28_27512` places VPP on pin 22 (OE/VPP shared). `DIP28_27256` places VPP on pin 1. A chip decoded with the wrong variant → VPP on the wrong pin.
- 2732 vs 2716 pinout swap: `DIP24_2732` has `vpp-pin = [20]` (the OE/VPP pin). `DIP24_2716` has `vpp-pin = [21]`. A 1-pin shift in a 24-pin socket.

**Root cause in re-derivation:**
`variant` and `pm_idx` in infoic.xml encode the layout family, but the decode logic (`DIP28_VARIANT_MAP`, `PIN_MAP_TO_PINOUT`, `PIN_MAP_PROTO_TO_PINOUT`) was reverse-engineered heuristically. A re-derived rule that mis-reads the variant or pm_idx byte assignment routes a chip to the wrong pinout key, which changes which socket pin gets VPP.

**Datasheet cross-check:**
For every chip receiving a VPP-capable handler, confirm: (1) the pinout entry's `vpp-pin` field matches the datasheet's VPP pin number exactly; (2) that socket pin is not shared with any signal that would be damaged by 12V+ during normal operation (CE, OE, A14, WE are all damage-sensitive).

**Phase to address:** Field-dictionary decode phase (the phase that re-derives `variant`/`pm_idx` → pinout mapping). Every new pinout key must pass a pin/voltage table audit before it goes into `pinouts.json`.

---

### H-2: Wrong-Pin VPP — WE Receives 12V+ (24-pin EEPROM class)

**What goes wrong:**
This is a subclass of H-1 specific to 24-pin chips where VPP and WE are on adjacent or overlapping pins. `configure_eprom` asserts the VPP regulator. `DIP24_2716` has `vpp-pin = [21]`. If a 24-pin EEPROM (5V WE-programmed) passes the filter — either because the `flags & 0x10` electrically-erasable guard is bypassed, or because a new chip type added without a corresponding safety skip has the wrong pinout — 12V goes to WE.

**Root cause in re-derivation:**
The existing SAFETY SKIP in `build_db.py` (lines 359-369) gates on `pin_count == 24 AND proto_id in (0x07, 0x08, 0x0B) AND (flags & 0x10)`. A re-derived decode could change which bits of `flags` represent "electrically erasable." If that bit assignment is wrong, the guard misfires and 24-pin EEPROMs pass through to the EPROM handler.

**Datasheet cross-check:**
For every 24-pin chip with an EPROM-family protocol: verify what pin 21 connects to on that chip (OE/VPP for a genuine EPROM; WE for an EEPROM). Also verify that `flags & 0x10` is the correct electrically-erasable discriminator in the authoritative minipro source — it must remain consistent with `build_db.py`'s `_etype` derivation logic.

**Phase to address:** Flags field-dictionary phase. The `flags` bit meanings must be source-verified from minipro before the safety-skip predicate is rebuilt. Until a 24-pin EEPROM firmware handler exists and is safety-reviewed, the SAFETY SKIP must remain (or be tightened, not loosened).

---

### H-3: VPP Overvoltage — Schema Cap vs. Real-Chip Requirements

**What goes wrong:**
`VPP_MV` and `VPP_VOLTAGES` cap at 0xF0 = 18000 mV (18V). The RURP shield's boost converter tops out at approximately 22V. Intel NMOS 2716 (original 1977) requires 25V VPP; Intel NMOS 2732 requires 25V; Intel M2732A requires 21V. These chips are aliased in infoic.xml under generic entries that report 18V (the schema maximum) — they silently receive 18V instead of their required voltage. At 18V they will not program correctly. They are physically unprogrammable on RURP hardware (25V > 22V hardware ceiling), but the operator has no indication of this.

Additionally, in the other direction: if the VPP value decoded from a new chip family is misread (e.g., the `voltages` byte boundary between VPP and VCC nibbles is wrong), a chip could receive a higher-than-specified VPP. The existing `voltages` field decode uses `voltages & 0xFF` for VPP and `(voltages >> 8) & 0x0F` for VDD, `(voltages >> 12) & 0x0F` for VCC. A re-derived decode that gets the nibble boundaries wrong corrupts both values simultaneously.

**Datasheet cross-check:**
(a) For every new chip entry, verify VPP spec from the datasheet against the decoded `vpp_mv` value. (b) Verify that the `voltages` field nibble layout is consistent with minipro source — specifically that `vpp = voltages & 0xFF`, `vdd = (voltages >> 8) & 0x0F`, `vcc = (voltages >> 12) & 0x0F`. (c) Flag any chip requiring VPP > 18V as "schema-capped / unverifiable" rather than silently reporting 18V.

**Phase to address:** Voltage field-dictionary decode phase.

---

### H-4: VCC Mismatch — 3.3V / 6.5V Chips on 5V Rail

**What goes wrong:**
RURP provides fixed 5V VCC. The `VCC_VOLTAGES` decode currently handles 0x00=5V, 0x01=3.3V, 0x04=5.5V, 0x05=6.5V. Chips with `vcc = 3.3V` will be over-driven. Chips with `vcc = 6.5V` are legacy NMOS parts that the RURP cannot power correctly. If the existing `vcc` field decode is wrong and a 3.3V chip is tagged as 5V, it will be exposed to over-voltage on every bus line.

**Root cause in re-derivation:**
The `VCC_VOLTAGES` map was hand-derived. A re-derivation that changes which hex value means 3.3V or moves any nibble to a different byte position changes which chips pass the 5V filter and which are silently mis-tagged.

**Datasheet cross-check:**
Verify the `voltages` field byte layout and the VCC nibble decode against minipro source. Any chip with a VCC entry that decodes to not-5V should be either filtered out (RURP cannot power it) or emit an explicit error rather than proceeding with incorrect VCC.

**Phase to address:** Voltage field-dictionary decode phase; filter layer in `build_db.py`.

---

### H-5: WE/OE/CE/PGM Strobe on the Wrong Pin

**What goes wrong:**
`configure_eeprom28c` writes via the WE line (no VPP). The WE line comes from the pinout entry's implicit control-signal mapping — the RURP drives WE via the `CTRL_READ_WRITE` bit in the control register, which the pinout's `rw-pin` field maps to the physical socket pin. A new chip type (e.g., a 24-pin EEPROM handler) that uses a pinout with `rw-pin` mapped incorrectly will assert WE on the wrong socket pin.

For `configure_eprom`, the PGM pulse is delivered via `CTRL_VPE_ENABLE` → either VPE (the shared PGM/VPP rail) or `CTRL_VPP_P1_ENABLE` depending on `using_p1_as_vpp()`. The `vpp_line` field in `bus_config` is set by the host from the pinout's `vpp-pin` entry and compared against `VPP_P1_32_DIP (0x15)`, `VPP_P1_28_DIP (0x0F)`, `VPP_P21_24_DIP (0x0B)` to select the routing path. A pinout that specifies the wrong `vpp-pin` value will pick the wrong routing path, causing the PGM pulse to fire on the wrong physical pin.

**Datasheet cross-check:**
For each new pinout entry: (1) cross-reference every control signal pin (WE, OE, CE, PGM/VPP) against the datasheet pin diagram; (2) verify that `rw-pin` (WE) is correct for write operations; (3) verify that `vpp-pin` exactly matches the datasheet's VPP/PGM pin number; (4) verify there is no physical overlap between `vpp-pin` and any address line for the target chip family.

**Phase to address:** New pinout definition phase (any phase adding a `DIP24_*` or new 28/32-pin EEPROM pinout entry to `pinouts.json`).

---

### H-6: Over-Erase / Corruption on Electrically-Erasable Chips

**What goes wrong:**
`configure_eprom`'s `eprom_internal_erase` asserts `CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE` to the chip's A9 and PGM pins respectively. This is the correct erase sequence for UV-EPROMs that support electrical erase (e.g., W27C512). On a chip that does NOT support electrical erase (most classic 27-series), calling this function with `FLAG_CAN_ERASE` set will apply the erase-voltage sequence to a chip that ignores it — low risk of damage since the chip just doesn't respond. However, if `FLAG_CAN_ERASE` is incorrectly set for a 5V EEPROM routed to `configure_eprom` (due to a decode failure), the "erase" sequence asserts 12V A9 to what may be an address line, not an erase-enable input.

For 5V flash families, `configure_flash3` and `configure_flash4` perform chip-erase or sector-erase via command sequences with no VPP. Over-erase risk here is algorithmic: if the wrong erase command sequence is used (e.g., 0x06 AMD-unlock sequence applied to a 0x05 page-write part), flash may be left in an indeterminate state.

**Datasheet cross-check:**
Verify for each chip: (a) whether electrical erase is supported (and thus `FLAG_CAN_ERASE` is appropriate); (b) the erase command sequence (for flash families) matches the datasheet command-set table; (c) A9 VPP erase is valid only for UV-EPROMs that explicitly support it — not for any 5V chip.

**Phase to address:** Per-handler correctness review; firmware write-path phase for each new handler type.

---

## 2. Re-Derivation Failure Mode Classes

These are the classes of error that occur when re-deriving the decode from minipro source. Each maps to one of the existing override cases.

### R-1: Type-Tag / Protocol-ID Mismatch (fm1608 class)

**What goes wrong:**
infoic.xml's `type` field (1=Memory, 4=SRAM) and `protocol_id` can disagree. Ramtron FRAM chips are `type=4` (SRAM-class by electrical behavior) but `protocol_id=0x07` (EPROM-family algorithm in minipro's classification). A re-derivation that trusts `protocol_id` alone routes them to `configure_eprom`. The existing fix gates on `type_int == 4 AND proto_id in (0x07, 0x08, 0x0B)` to flip `proto_id` to 0x28 (SRAM_STD).

**Generalization:**
Any chip where the minipro `type` field and `protocol_id` disagree is in this class. The re-derivation must not assume that `protocol_id` is the sole authority for dispatch — the `type` field is a veto for SRAM-class chips. More broadly: any chip tagged `type=4` that carries a VPP-capable `protocol_id` is unsafe to expose to that protocol's handler.

**Detection:**
Run `check_dispatch.py` after each DB rebuild. The BLOCKER-2 guard (`_SRAM_PROTOCOLS` set) catches SRAM-protocol chips routed to `configure_eprom`. The fm1608 class (type=4 with EPROM protocol) is caught by the `type_int == 4 AND proto_id in EPROM_FAMILY` predicate in `build_db.py`. A new variant of this pattern (type=4 + flash protocol) would bypass both guards — add an explicit guard for `type_int == 4 AND proto_id in FLASH_CAPABLE_PROTOCOLS` in the re-derived decode.

**Phase to address:** Field-dictionary decode phase (type vs. protocol resolution rules); guard extension in `check_dispatch.py`.

---

### R-2: Electrically-Erasable Flag Misinference (WARNING-5 class)

**What goes wrong:**
`flags & 0x10` is the "electrically erasable" discriminator used by WARNING-5 to distinguish 5V EEPROMs from genuine UV-EPROMs when both share `protocol_id=0x07`. If the `flags` bit for electrically-erasable is wrong (e.g., a re-derivation from minipro source discovers the bit is actually 0x80 in some schema version, or that the bit has additional conditions), the WARNING-5 predicate silently stops working.

The existing `package-details.md` (the doc being replaced) calls bit 7 (0x80) "Electrically Erasable or Writable" and bit 4 (0x10) "Requires Write Enable Sequence." The `build_db.py` override uses `flags & 0x10` not `flags & 0x80`. If the authoritative source says the discriminator is a different bit, the override fires on the wrong set of chips.

**Generalization:**
Any flags-based dispatch predicate is fragile against an incorrect bit interpretation. The re-derivation must verify each bit's meaning from minipro source code (specifically the flag decode in `database.c` or equivalent) rather than inferring it from observed patterns.

**Detection:**
After each `build_db.py` run, the `check_dispatch.py` WARNING-5 guard (pinout `DIP28_2764` + type `Flash/EEPROM` + handler `configure_eprom`) must still return zero violations. If the flags-based `_etype` derivation changes, this guard may silently pass (no violations detected) while the underlying hazard has been re-introduced via a different chip's dispatch path. The guard tests a necessary condition but not sufficiency — it only checks chips that currently have pinout `DIP28_2764`.

**Phase to address:** Flags field-dictionary decode phase; extend `check_dispatch.py` to cover the full WARNING-5 class for any pinout where pin 1 = VPP.

---

### R-3: pm_idx Aliasing — Same Index, Different Physical Layout (PIN_MAP class)

**What goes wrong:**
`pm_idx` (the low byte of `pin_map`) clusters chips by family, but multiple families can share the same `pm_idx` with different physical layouts requiring protocol-level disambiguation. The existing `PIN_MAP_PROTO_TO_PINOUT` table handles this at `(pin_count, pm_idx, proto_id)` resolution. A re-derivation that adds a new pm_idx → pinout mapping without checking for protocol-level aliases will route multiple chip families to a single pinout, possibly routing a VPP-unsafe chip through a VPP-capable handler.

Specific known cases:
- `(32, 13)`: 5V flash (0x05/0x06 → `DIP32_SST39SF040`) vs. UV-EPROM (0x08 → `DIP32_STD`) vs. 5V EEPROM (0x0D → `DIP32_28C512_EEPROM`). All three share pm_idx=13 on 32-pin parts.
- `(32, 0)`: 32-pin SRAM/NVRAM (0x0E → `DIP32_SST39SF040`) vs. anything new at pm_idx=0.
- `(28, 22)`: 28-pin 27C family where `variant_lo` (0x10/0x11/0x12/0x13) sub-discriminates between `DIP28_27512` (VPP pin 22), `DIP28_27256` (VPP pin 1), and `DIP28_2764` (VPP pin 1).

**Generalization:**
Every `None` entry in `PIN_MAP_TO_PINOUT` is a known aliased cluster. For each such cluster, the re-derivation must enumerate every proto_id present in infoic.xml at that (pin_count, pm_idx) and confirm which pinout is correct for each.

**Detection:**
After re-derivation, scan for any chip assigned to a pinout that disagrees with its protocol family (e.g., a 0x05/0x06/0x0D chip assigned to `DIP32_STD` which has `vpp-pin=[1]`, exposing it to P1 VPP). Add a check to `check_dispatch.py` or a new tool: for any chip with `algorithm in {0x05, 0x06, 0x0D}` (5V, no VPP), verify `pinout` does not contain a `vpp-pin` field.

**Phase to address:** pm_idx / pin_map decode phase; extend `check_dispatch.py`.

---

### R-4: Variant Sub-Discriminator Drift (DIP28 27512 vs 27256 vs 2764)

**What goes wrong:**
Within `(28, 22)` (pm_idx=22, 28-pin), the `DIP28_VARIANT_MAP` uses `variant & 0xFF` to select between `DIP28_27512` (VPP pin 22), `DIP28_27256` (VPP pin 1), and `DIP28_2764` (VPP pin 1). The values 0x10/0x11/0x12/0x13 were reverse-engineered from observed infoic.xml data. If a re-derivation from minipro source reveals a different variant byte assignment (or the high byte encodes the algorithm number per `database.c:uint8_t algo_number = (uint8_t)(device->variant >> 8)`), the 27512 vs 27256 discrimination could flip, routing a 27512 (VPP=22) through the 27256 pinout (VPP=1) or vice versa.

**Consequence:**
27512 routed through 27256 pinout: VPP asserted on pin 1 (A14 on the chip) instead of pin 22 (OE/VPP). 12V on A14 = damage. The failure is silent unless pin 22 is confirmed as VPP in the bench test.

**Datasheet cross-check:**
For each 28-pin EPROM family, confirm from the datasheet: (a) VPP socket pin number; (b) whether it matches the assigned pinout's `vpp-pin` field; (c) cross-reference the variant byte value against the minipro `database.c` variant-decode logic to confirm the sub-discriminator logic is correct.

**Phase to address:** variant field-dictionary decode phase; add a pinout-vs-chip-family consistency test.

---

### R-5: Unknown Protocol-ID Pass-Through

**What goes wrong:**
`build_db.py` currently skips chips with `proto_id not in KNOWN_PROTOCOLS`. When v1.11 adds new protocols (0x2A, 0x2C, 0x2E, 0x11) to `KNOWN_PROTOCOLS`, chips that were previously skipped become visible. These chips may have been skipped for damage-prevention reasons that are not documented in `KNOWN_PROTOCOLS` membership alone. A new protocol added to `KNOWN_PROTOCOLS` without a corresponding firmware handler and safety review will either (a) emit a "Memory type not supported" error, or (b) fall through to the `mem_type` legacy chain and dispatch to a wrong handler.

**Detection:**
`check_dispatch.py`'s dispatch simulation must be updated in lockstep with `KNOWN_PROTOCOLS`. Any protocol added to `KNOWN_PROTOCOLS` without a corresponding entry in `_ALGO_MEM_TYPE` will produce `mt = None` and `handler = "ERROR"` — caught immediately. However, protocols that resolve to a wrong mem_type (e.g., a new NVRAM protocol that gets `mem_type=4` / SRAM) won't be caught unless the SRAM-safety guard is extended to include the new protocol.

**Phase to address:** For each new protocol: add entry to `_ALGO_MEM_TYPE` in `check_dispatch.py` simultaneously with adding it to `KNOWN_PROTOCOLS` in `build_db.py`. Never do one without the other.

---

## 3. Per-Handler Safety-Review Methodology (No Bench Validation)

This is the concrete gate that every new write-capable handler must pass before shipping. It is the only guardrail in the absence of bench validation.

### SR-1: Pinout Pin/Voltage Map Audit

For the pinout entry assigned to the new handler, verify against the target chip's datasheet:

- [ ] `vpp-pin` matches the datasheet VPP/PGM pin number (or is absent for 5V-only handlers)
- [ ] `vpp-pin` is NOT a shared address line on ANY chip in the family that will use this pinout
- [ ] `rw-pin` (WE) matches the datasheet WE pin number
- [ ] `oe-pin` (OE) matches the datasheet OE pin number
- [ ] `ce-pin` (CE) matches the datasheet CE pin number
- [ ] `vcc-pin` list is correct (supply voltage pins; RURP asserts VCC here)
- [ ] `gnd-pin` list is correct (ground pins; RURP ties these to GND)
- [ ] No address or data bus pin in the pinout overlaps with `vpp-pin`, `vcc-pin`, or `gnd-pin`
- [ ] For 24-pin handlers: confirm pin 21 is VPP/PGM (not WE) for every chip in scope
- [ ] For 28-pin UV-EPROMs: confirm whether VPP is on pin 1 or pin 22 (not ambiguous)

### SR-2: VPP Routing Path Verification

Identify which firmware routing path the new handler uses:

- [ ] Confirm `using_p1_as_vpp()` returns the expected value for this pinout (checks `vpp_line == VPP_P1_32_DIP | VPP_P1_28_DIP | VPP_P21_24_DIP` constants)
- [ ] Confirm that `CTRL_VPE_ENABLE` vs `CTRL_VPP_P1_ENABLE` are used consistently with the expected routing (the `eprom_internal_set_control_register` intercept in `eprom.cpp` performs this flip)
- [ ] For Intel-flash (0x10): VPP is routed via `CTRL_VPP_P1_ENABLE` (pin 1 on DIP32_STD). Confirm the new handler uses the same routing if it shares the Intel-flash pinout.
- [ ] For 5V handlers (0x0D, 0x05, 0x06, 0x35, 0x39): confirm `CTRL_VPP_REGULATOR_ENABLE` is NEVER asserted in the handler's write path.

### SR-3: VPP Voltage Range Check

- [ ] Verify `vpp_mv` decoded value is within RURP hardware capability (max ~22V; reject > 18000 mV at schema level, flag 18V as schema-capped)
- [ ] Verify the target chip's VPP spec from the datasheet matches the decoded `vpp_mv` within ±10%
- [ ] Confirm the chip is not a 25V-VPP NMOS part aliased to an 18V infoic.xml entry
- [ ] The `eprom_check_vpp` ADC gate (±500 mV over-voltage / 5% under-voltage) will run before any write pulse — confirm the VPP spec is achievable on the RURP before declaring the handler "safe"

### SR-4: Handler Dispatch Chain Audit

Before shipping a new protocol handler:

- [ ] Add the protocol to `_ALGO_MEM_TYPE` in `check_dispatch.py` with the correct `mem_type`
- [ ] Run `check_dispatch.py` on the regenerated DB — must pass with 0 errors, 0 SRAM-in-eprom, 0 WARNING-5 violations
- [ ] Verify the dispatch order in `memory.cpp:configure_memory` places the new protocol in the correct position (before any fallback chain)
- [ ] Add the protocol to `KNOWN_PROTOCOLS` in `build_db.py` only after the handler is implemented in firmware
- [ ] Add a Unity test in `test/native/avr/test_dispatch/` asserting the new protocol dispatches to the expected handler — verify it passes on the native PlatformIO environment (`pio test -e native`)

### SR-5: Safety-Skip Preservation Check

- [ ] Confirm the 24-pin 5V EEPROM SAFETY SKIP (`pin_count == 24 AND proto_id in (0x07, 0x08, 0x0B) AND flags & 0x10`) is still intact after the re-derived decode (not accidentally weakened)
- [ ] Confirm the fm1608 override (`type_int == 4 AND proto_id in (0x07, 0x08, 0x0B)`) is still intact
- [ ] Confirm the WARNING-5 override (`pinout_key in DIP28_2764/DIP28_28C256 AND proto_id == 0x07 AND _etype == Flash/EEPROM`) still fires for the expected chip set after the re-derived decode
- [ ] Run a `git diff` on the DB output comparing old and new for each affected chip family — unexpected changes = regression

### SR-6: Dual-Repo Constant Parity

- [ ] Any new flag bit, command code, or control register bit used by the new handler must be defined in both `firestarter_app/firestarter/constants.py` AND `firestarter/include/firestarter.h` / `rurp_pinout.h`
- [ ] Run the existing parity test suite after adding constants

---

## 4. Regression Strategy for the 734-Chip Decode

### RG-1: Byte-Diff Regression Baseline

**What goes wrong:**
Re-deriving `build_db.py` can silently change the `algorithm`, `pinout`, `vpp_mv`, or `electrical.type` fields for existing chips. A chip that was correctly classified (e.g., W27C512 → algorithm=0x07, pinout=DIP28_27512) could be re-classified to a different pinout or algorithm if the re-derived rules differ from the originals.

**How to avoid:**
Before any re-derivation work begins, snapshot the current `chip_database.json` as a baseline (git commit or named copy). After each re-derivation step, run a JSON diff against the baseline. Any unintended change to an existing chip's `algorithm`, `pinout`, or `vpp_mv` is a regression. The diff must be reviewed field-by-field for every changed chip, not accepted in bulk.

**Detection tool:**
A purpose-built comparison script that produces a per-chip diff showing exactly which field changed and why. The goal is not just a PASS/FAIL gate but a human-reviewable diff. Any change must be categorized as either "intentional (source-derived correction)" or "regression (must revert)."

**Phase to address:** Decode re-derivation phase (any phase that modifies `build_db.py`). Make the diff a required deliverable.

---

### RG-2: Per-Chip Wire Round-Trip (check_dispatch.py)

The existing `check_dispatch.py` performs a per-chip wire round-trip via `db.get_eprom(part)` + `db.convert_to_programmer(mapped)`, asserting `vpp_mv` is present and the legacy `vpp` key is absent. This must remain green after every re-derivation step.

Additionally, the dispatch simulation must be kept in sync with `memory.cpp:configure_memory` — any new protocol added must have a corresponding `dispatch()` case in `check_dispatch.py` that mirrors the firmware's `if (handle->protocol == ...)` chain exactly.

**Warning sign:**
If `check_dispatch.py` exits with non-zero after a re-derivation, stop. Do not merge. The dispatch simulation is the authoritative regression gate for the 734-chip set.

**Phase to address:** Every build_db.py modification phase. Run as a CI step.

---

### RG-3: Upstream infoic.xml Drift

**What goes wrong:**
`build_db.py` fetches `infoic.xml` from upstream at runtime. Between v1.0 (743 chips) and v1.3 (734 chips), upstream drift caused a -9 chip count change. The re-derivation work in v1.11 depends on the same live URL. If infoic.xml changes during development (or if the re-derivation uses a cached snapshot at phase start but CI fetches live), the DB output will differ between the development snapshot and the CI-generated artifact.

**How to avoid:**
Pin a specific commit of infoic.xml as the v1.11 reference snapshot. Use a local copy (already committed to the repo or via a build-time hash check) rather than a live fetch during the re-derivation work. The MINIPRO_XML_URL fetch should be replaced with a versioned local reference for the duration of v1.11 development, with a clear note of which upstream commit the snapshot corresponds to.

**Phase to address:** First re-derivation phase. Commit the pinned infoic.xml snapshot before modifying any decode logic.

---

### RG-4: `_etype` Pre/Post Override Order

**What goes wrong:**
`build_db.py` computes `_etype` twice: once flags-based (lines 388-395, used by WARNING-5 and fm1608 predicates) and once protocol-aware after all overrides (lines 481-489, stored in the final DB entry). The WARNING-5 and fm1608 overrides MUST run between these two `_etype` computations because they depend on the flags-based value to detect mistagged chips and then the post-override re-derivation "fixes" `_etype` to match the corrected protocol.

A re-derivation that merges the two `_etype` computations into one, or changes their order, breaks the WARNING-5 predicate (it needs `_etype == "Flash/EEPROM"` at predicate time, which is set by the flags-based block) while the stored DB value must reflect the post-override protocol (UV-EPROM after the 0x07 flip vs. SRAM after the fm1608 flip).

**How to avoid:**
Maintain the two-pass `_etype` pattern explicitly in any re-derived version. Document the order dependency. Add a comment block to the re-derived code that names both `_etype` derivation passes and states why they must remain in order.

**Phase to address:** build_db.py re-derivation phase.

---

## 5. Exotic Type Pitfalls (NVRAM 0x2A/0x2C/0x2E, FWH 0x11)

### E-1: NVRAM/Timekeeper (0x2A / 0x2C / 0x2E) — No Standard Pinout Class

**What goes wrong:**
Dallas DS12887/DS1643/DS1244 NVRAM/timekeepers use the JEDEC 32-pin SRAM bus layout for data access (no VPP, WE-programmed at 5V) but with additional hardware: a built-in lithium battery, an RTC oscillator, and sometimes a power-fail comparator. The programming operation is standard SRAM byte-write — configure_sram would work for data access. However:

- The chip-enable sequencing for write operations may require a specific /WE strobe width not guaranteed by the current `configure_sram` stub (which is a "safe no-op" per the architecture)
- The RTC oscillator and battery circuitry mean some pins that look like VCC or NC on the datasheet are sensitive to voltage levels during power-up/power-down
- DS1244/DS1245 series use `(32, 0, 0x0E)` in `PIN_MAP_PROTO_TO_PINOUT` → `DIP32_SST39SF040`. This was derived from JEDEC SRAM reasoning, not confirmed from a datasheet. The SST39SF040 pinout has WE=31, CE=22, OE=24 — these must be verified against the Dallas NVRAM datasheet pin assignments.

**Datasheet cross-check for 0x2A/0x2C/0x2E:**
(a) Confirm the pinout (CE, OE, WE socket pins) matches `DIP32_SST39SF040` for each NVRAM family in scope. (b) Confirm no VPP or high-voltage operation is required (these are all 5V parts). (c) Confirm `configure_sram` (byte-write at 5V with no VPP) is functionally correct for the intended write operation. (d) Check whether the `0x2A/0x2C/0x2E` protocol requires any command-register access or special write sequences beyond a simple WE-gated byte write.

**Phase to address:** NVRAM feasibility research must precede any handler implementation. Do not expose 0x2A/0x2C/0x2E in `KNOWN_PROTOCOLS` until the datasheet cross-check is complete.

---

### E-2: FWH (0x11) — Likely Out of RURP Scope

**What goes wrong:**
FWH (Firmware Hub, Intel) is a serial protocol, not parallel. While infoic.xml carries FWH entries and they may have DIP packages in the database, FWH devices use an LPC-bus-derived serial interface (4-bit multiplexed) that the RURP parallel bus cannot drive. Adding 0x11 to `KNOWN_PROTOCOLS` will cause FWH chips to appear in the database and potentially be dispatched to `configure_flash_intel` (which expects a parallel bus command-register interface, not LPC serial).

**How to avoid:**
Confirm via minipro source that 0x11 is indeed FWH (serial, not parallel). If so, keep it in PROTOCOL_MAP for documentation purposes but do NOT add it to `KNOWN_PROTOCOLS`. The existing filter (`if proto_id not in KNOWN_PROTOCOLS: skip`) is the correct gate. Document the reason for the explicit exclusion in `build_db.py`.

**Phase to address:** Exotic-type feasibility research; exclude 0x11 from KNOWN_PROTOCOLS with an explanatory comment unless a parallel-bus FWH variant is confirmed from the datasheet.

---

### E-3: NVRAM Battery State — Irreversible Side Effects

**What goes wrong:**
Battery-backed NVRAM (DS1243/DS1244/DS1245/DS1249/DS1250, M48T128) retains data indefinitely. A programming operation that runs blank check before write will PASS blank check only if the chip has never been written (factory-new) OR if it has been bulk-erased (which these chips do not support electrically — they can only be overwritten byte-by-byte). If `FLAG_SKIP_BLANK_CHECK` is not set, the write will be aborted on a non-blank NVRAM.

More critically: the RTC oscillator in Dallas timekeepers draws current continuously. If the chip is seated in the RURP socket with VCC present, the oscillator runs and the RTC increments. This is not a damage hazard but it is a state-change side effect the operator should be aware of.

**How to avoid:**
Any NVRAM handler must set `FLAG_SKIP_BLANK_CHECK` by default (NVRAMs are never blank). Document that NVRAM write is always an overwrite, not a blank-then-write operation. Document the RTC oscillator side effect.

**Phase to address:** NVRAM handler design phase.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| "One-rom verified" comment without datasheet citation | Faster initial decode | Brittle — a different chip in the same pm_idx cluster may have a different layout | Never for v1.11 re-derivation; must cite datasheet |
| Adding protocol to KNOWN_PROTOCOLS without firmware handler | Chips appear in DB | Silent "Memory type not supported" error at runtime; operators see non-actionable failures | Never; KNOWN_PROTOCOLS and handler must ship together |
| Skipping `check_dispatch.py` after a build_db.py change | Faster iteration | Undetected dispatch regression across 734 chips | Never |
| Re-using an existing pinout for a new chip family without datasheet confirmation | Fewer new pinout entries | Pin 1 VPP vs pin 22 VPP ambiguity; wrong-pin-VPP damage | Never for VPP-capable handlers |
| Trusting the existing doc (package-details.md / protocol-flags.md) as ground truth | No upstream research needed | Those docs are heuristic-derived, not source-verified; the flags bit meanings are "inferred" not authoritative | Never for v1.11; the whole point is to replace them |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| H-1: Wrong-pin VPP | Field-dictionary decode phase (variant/pm_idx/pinout derivation) | SR-1 checklist for every new pinout; check_dispatch.py WARNING-5 guard extended |
| H-2: WE gets 12V (24-pin EEPROM) | Flags field-dictionary phase + 24-pin EEPROM handler phase | SAFETY SKIP predicate confirmed in SR-5; flags bit verified from minipro source |
| H-3: VPP overvoltage / schema cap | Voltage field-dictionary decode phase | SR-3 VPP range check; 25V parts documented as unprogrammable |
| H-4: VCC mismatch | Voltage field decode + filter layer | Chips with VCC != 5V filtered or explicitly errored |
| H-5: Wrong WE/OE/CE/PGM pin | New pinout definition phase | SR-1 full pin map audit against datasheet for every new pinout |
| H-6: Over-erase on non-erasable chips | Per-handler correctness phase | FLAG_CAN_ERASE only set when datasheet confirms electrical erase |
| R-1: type=4 / EPROM protocol conflict | build_db.py re-derivation phase | fm1608 override intact (SR-5); check_dispatch.py BLOCKER-2 guard; add flash-family guard for type=4 |
| R-2: Flags bit misinference | Flags field-dictionary decode phase | WARNING-5 verified against minipro source bit assignment; check_dispatch.py guard still 0 violations |
| R-3: pm_idx aliasing | pm_idx / pin_map decode phase | PIN_MAP_PROTO_TO_PINOUT completeness check; no 5V chip on VPP-bearing pinout |
| R-4: variant sub-discriminator drift | variant field-dictionary decode phase | Per-chip DB diff; 27512 vs 27256 VPP-pin confirmed in test |
| R-5: Unknown protocol pass-through | Each new protocol addition phase | _ALGO_MEM_TYPE updated simultaneously; check_dispatch.py runs clean |
| RG-1: Byte-diff regression | Every build_db.py modification | Per-chip JSON diff against baseline; unexpected changes reviewed |
| RG-2: Wire round-trip regression | Every build_db.py modification | check_dispatch.py green; WIRE-02 round-trip passes |
| RG-3: infoic.xml upstream drift | First re-derivation phase | Pinned snapshot committed before decode logic changes |
| RG-4: _etype pre/post order | build_db.py re-derivation | Two-pass pattern preserved; WARNING-5 fires on correct chip set |
| E-1: NVRAM pinout unconfirmed | NVRAM feasibility research phase | Datasheet pin audit for DS1245/M48T128 before exposure |
| E-2: FWH serial/parallel confusion | Exotic-type feasibility research | 0x11 explicitly excluded from KNOWN_PROTOCOLS with comment |
| E-3: NVRAM blank-check / RTC side effects | NVRAM handler design phase | FLAG_SKIP_BLANK_CHECK default; RTC behavior documented |

---

## Sources

- `firestarter_app/tools/build_db.py` — all override comments are the primary hazard catalog (HIGH confidence; grounded in production code that has prevented real damage)
- `firestarter_app/tools/check_dispatch.py` — BLOCKER-2 and WARNING-5 regression guards (HIGH confidence)
- `firestarter_app/tools/audit_coverage_matrix.py` — DEFECT-COV-00/01 findings and the `detect_hazard()` function (HIGH confidence)
- `firestarter/src/proms/eprom.cpp` — VPP routing implementation; `eprom_internal_set_control_register` / `using_p1_as_vpp()` (HIGH confidence)
- `firestarter/src/proms/flash_intel.cpp` — CTRL_VPP_P1_ENABLE routing for Intel-flash (HIGH confidence)
- `firestarter/include/rurp_pinout.h` — CTRL_VPP_* bit definitions (HIGH confidence)
- `firestarter/include/memory_utils.h` — `using_p1_as_vpp()` constants (VPP_P1_32_DIP, VPP_P1_28_DIP, VPP_P21_24_DIP) (HIGH confidence)
- `firestarter/include/rurp_shield.h` — VPP magic constants and hardware revision (HIGH confidence)
- `firestarter_app/firestarter/data/pinouts.json` — per-pinout vpp-pin, we-pin, oe-pin, ce-pin assignments (HIGH confidence)
- `firestarter_app/doc/package-details.md` / `protocol-flags.md` — existing flag interpretations (MEDIUM confidence; heuristic-derived, to be replaced by v1.11)
- `.planning/PROJECT.md` section "Current Milestone: v1.11" — scope and constraint definitions (HIGH confidence)
- minipro `src/minipro.h` via WebFetch — `pin_map_t.gnd_table`, `device_t.pin_map`, `package_details_t.adapter` field layout (MEDIUM confidence; fetched via WebFetch, core struct shapes confirmed)
- minipro `src/tl866iiplus.c` via WebFetch — 21-entry `vpp_pins[]` array confirming pin 1 can receive VPP; `tl866iiplus_set_pin_drivers()` for VPP enable logic (MEDIUM confidence; VPP routing confirmed at hardware driver level)

---

*Pitfalls research for: Firestarter v1.11 infoic.xml decode re-derivation + new firmware write-path handlers*
*Researched: 2026-06-08*

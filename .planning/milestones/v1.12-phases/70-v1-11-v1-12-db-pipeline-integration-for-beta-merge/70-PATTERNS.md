# Phase 70: v1.11 + v1.12 DB-Pipeline Integration — Pattern Map

**Mapped:** 2026-06-15
**Files analyzed:** 5 target files (existing, being surgically modified)
**Branch for all edits:** `v1.12-protocol-dispatch-hardening` (D-01)
**Analogs:** This is a re-port — every "analog" is the file itself on the two source branches.

---

## File Classification

| Target File | Role | Data Flow | v1.11 beta body | v1.12 body | Merge Strategy |
|---|---|---|---|---|---|
| `tools/build_db.py` | pipeline-transform | batch (XML→JSON) | 589 lines — principled `resolve_pinout_key`, correct decode | 715 lines — guess-tables, safety features, decode regressions | Transplant beta's function body + graft v1.12 safety features + fix decode regressions |
| `tools/check_dispatch.py` | gate/validator | batch (scan DB) | 277 lines — structural no-vpp-pin guard, WARNING-5 type guard | 359 lines — support_status machinery, D-10 assertions, missing structural guard | Merge: v1.12 body + restore beta's `_build_no_vpp_pin_set` + `PINOUTS_FILE` + `novpp_in_eprom` bucket |
| `tools/diff_db.py` | gate/validator | batch (diff JSONs) | 486 lines — has BUG_A_ETYPE + BUG_B_VPP rules | 486 lines — removed BUG_A/B, added RULE_PHASE66 | Merge: keep v1.12's RULE_PHASE66, restore beta's BUG_A_ETYPE + BUG_B_VPP |
| `tools/baseline/chip_database.baseline.json` | data/artifact | — | 734 chips (GATE-01 anchor) | not updated | Refresh to 744-chip output after regen |
| `firestarter/data/chip_database.json` | data/artifact | — | 743 chips (beta committed) | 744 chips (v1.12) | REGENERATE via `python tools/build_db.py` — never hand-merge |

---

## Pattern Assignments

### `tools/build_db.py` — Surgical transplant on v1.12 branch

This is the primary collision file. The strategy is a six-part transplant, performed in order.

---

#### Part 1: Module-top constants — use beta's, add v1.12 safety constants

**KEEP from beta (lines 27-47):** Canonical PROTOCOL_MAP (excludes 0x35/0x39/0x11/0x2A/0x2C/0x2E with explicit comments):

```python
# beta tools/build_db.py L27-47
PROTOCOL_MAP = {
    0x05: "FLASH_AMD_STD",  # IC2_ALG_F29EE
    0x06: "FLASH_AMD_ALT",  # IC2_ALG_W29F32P
    0x07: "EPROM_STD",  # IC2_ALG_ROM28P_1
    0x08: "EPROM_QUICK",  # IC2_ALG_ROM32P
    0x0B: "EPROM_LEGACY",  # IC2_ALG_ROM24P_1
    0x0D: "EEPROM_POLL",  # IC2_ALG_EE28C32P
    0x0E: "SRAM_32PIN",  # IC2_ALG_RAM32_1
    0x10: "FLASH_INTEL",  # IC2_ALG_28F32P
    0x27: "SRAM_24PIN",  # IC2_ALG_ROM24P_2
    0x28: "SRAM_STD",  # IC2_ALG_ROM28P_2
    0x29: "SRAM_512K_1M",  # IC2_ALG_RAM32_2
    # Excluded IDs documented here for traceability:
    # 0x11: IC2_ALG_FWH  — LPC 4-wire serial bus + 3.3V; infeasible on RURP
    # 0x2A: IC2_ALG_GAL16  — GAL16V8 PLD (type=3); no DIP memory chips
    # ...
    # 0x35: IC2_ALG_ITE  — ITE EC MCU TQFP128 (type=2); no DIP memory chips
    # 0x39: NO IC2_ALG CONSTANT — phantom; INFOIC2PLUS-unreachable
}
```

**KEEP from beta (lines 69-132):** `VPP_VOLTAGES`, `VPP_MV`, full `VCC_VOLTAGES` (including 0x02/0x03 entries missing from v1.12):

```python
# beta tools/build_db.py L125-132
VCC_VOLTAGES = {
    0x00: "5V",
    0x01: "3.3V",
    0x02: "4V",    # BUG-1 fix: was missing from v1.12
    0x03: "4.5V",  # BUG-1 fix: was missing from v1.12
    0x04: "5.5V",
    0x05: "6.5V",
}
```

**KEEP from beta (lines 110-122):** `KNOWN_PROTOCOLS` without 0x35/0x39:

```python
# beta tools/build_db.py L110-122
KNOWN_PROTOCOLS = {
    0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29,
    # DO NOT add 0x35 or 0x39 — removed by v1.11 DEC-05
}
```

**ADD from v1.12 (v1.12 L86-122):** Three new module-top constants — graft after VPP_MV table:

```python
# v1.12 tools/build_db.py L86-122 — add these to beta's constant section
NMOS_TRUE_VPP_MV: dict[str, int] = {
    "M2716": 25000,
    "M2732": 25000,
    "M2732A": 21000,
}
RURP_VPP_CEILING_MV = 22000

NON_DISPATCHABLE_ALGO = 0x00
```

**ADD 0x34 to KNOWN_PROTOCOLS:** Graft into beta's KNOWN_PROTOCOLS set:

```python
KNOWN_PROTOCOLS = {
    0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29,
    0x34,  # XICOR X88C64P — DIP-parallel NovRAM; included as protocol-not-implemented
    # NOT 0x35 or 0x39 — removed by v1.11 DEC-05
}
```

**DELETE from v1.12:** `DIP28_VARIANT_MAP`, `PIN_MAP_TO_PINOUT`, `PIN_MAP_PROTO_TO_PINOUT` — all three tables are deleted. Add the deletion comment from beta (lines 134-136):

```python
# beta tools/build_db.py L134-136
# D-02: DIP28_VARIANT_MAP, PIN_MAP_TO_PINOUT, and PIN_MAP_PROTO_TO_PINOUT
# have been DELETED (Phase 58 Plan 02). The principled resolve_pinout_key
# function below is the sole pinout-selection path.
```

---

#### Part 2: `resolve_pinout_key` — replace v1.12 body with beta body exactly

**DISCARD:** v1.12's `resolve_pinout_key` (3-tier lookup, signature without `type_int`/`mem_size`).

**USE:** beta's exact function body (lines 147-244), including the signature change:

```python
# beta tools/build_db.py L147-148 — function signature (adds type_int, mem_size)
def resolve_pinout_key(
    pin_count, variant, flags_int, pm_idx=None, proto_id=None, type_int=1, mem_size=0
):
```

Key branches to copy verbatim from beta:

```python
# beta tools/build_db.py L209-222 — 28-pin pm_idx=0 SRAM routing (handles all 14 SRAM chips)
elif pm_idx == 0:
    if type_int == 4 or proto_id in {0x27, 0x28, 0x29}:
        if mem_size <= 8192:
            key = "DIP28_JEDEC_SRAM_8K"
        else:
            key = "DIP28_28C256"
    elif proto_id == 0x05:
        key = "DIP28_28C256"
    else:
        key = None

# beta tools/build_db.py L241-244 — None return (D-06 fail-safe)
if key is not None and key not in VALID_PINOUT_KEYS:
    print(f"WARN: resolved pinout key '{key}' not in pinouts.json", file=sys.stderr)
return key
```

**CALL SITE UPDATE:** All calls to `resolve_pinout_key` in main() must pass the two new parameters. Pattern from beta (lines 325-333):

```python
# beta tools/build_db.py L325-333
pinout_key = resolve_pinout_key(
    pin_count,
    variant,
    flags,
    pm_idx=pm_idx,
    proto_id=proto_id,
    type_int=type_int,
    mem_size=mem_size,
)
```

---

#### Part 3: `interpret_timing` — use beta's corrected version

**DISCARD:** v1.12's `interpret_timing` (lines 178-194) — still has ×100 multiplier for 0x07/0x0B.

**USE:** beta's exact function (lines 247-258):

```python
# beta tools/build_db.py L247-258 — no multiplier (BUG-2 fix, DEC-03)
def interpret_timing(raw_hex, protocol_id):
    # Raw pulse_delay is microseconds for ALL protocols — no multiplier.
    try:
        val = int(raw_hex, 16)
    except Exception:
        val = 0

    if protocol_id in (0x07, 0x08, 0x0B):
        return f"{val} us"

    return "Algorithm Controlled"
```

---

#### Part 4: `main()` chip loop — graft v1.12 safety features into beta's structure

Beta's main() loop structure (lines 261-589) is the keeper. The graft points are:

**Graft point A — top of per-chip loop:** Initialize `_support_status`, `_unsupported_reason`, `_nmos_vpp_mv` from v1.12 (L182-184):

```python
# v1.12 tools/build_db.py L182-184 — insert at top of per-chip processing block
_support_status = "supported"
_unsupported_reason = None
_nmos_vpp_mv = None
```

**Graft point B — Site A gate:** After the `if proto_id not in KNOWN_PROTOCOLS: continue` WARN-skip (beta line 315-320), add the 0x34 classification block from v1.12 (L200-208):

```python
# v1.12 tools/build_db.py L200-208 — Site A gate (after WARN-skip continue)
if proto_id == 0x34:
    _support_status = "protocol-not-implemented"
    _unsupported_reason = (
        "protocol not implemented: 0x34 (XICOR NovRAM serial-parallel hybrid)"
    )
```

**Graft point C — Site B gate:** Before the `resolve_pinout_key` call (beta Step 1), add the 24-pin 5V EEPROM adapter-required gate from v1.12 (L24-47 of v1.12 chip loop):

```python
# v1.12 tools/build_db.py (chip loop) — Site B gate; must fire BEFORE resolve_pinout_key
if (
    pin_count == 24
    and proto_id in (0x07, 0x08, 0x0B)
    and (flags & 0x10)
):
    _support_status = "adapter-required"
    _unsupported_reason = (
        "adapter required: requires a dedicated DIP24 EEPROM adapter "
        "or firmware handler — socket pin 21 = WE, which the RURP "
        "DIP24_2716 pinout maps to the 12V VPP rail (hardware-damage path)"
    )
    print(
        f"INFO: including {mfg_name}/{name} as adapter-required — "
        f"24-pin 5V EEPROM with EPROM-family algo 0x{proto_id:02X} ...",
        file=sys.stderr,
    )
    proto_id = NON_DISPATCHABLE_ALGO  # CR-01 Option A
```

**ORDERING NOTE:** Site B must fire before `resolve_pinout_key`, so that `proto_id=0x00` is in effect when the pinout is resolved. The D-06 fail-safe skip (`if pinout_key is None: continue`) must remain AFTER Site B (these chips resolve to `DIP24_2716`, not None).

**OVERRIDE BLOCKS DELETED:** v1.12's fm1608 override block and native 28-pin SRAM override block (the two blocks that appear after `resolve_pinout_key` in v1.12) are NOT carried over. Beta's `resolve_pinout_key` handles all 14 SRAM chips via the `pm_idx=0, type_int=4` branch. Beta's existing Rule 3 (Step 6, lines 434-466) handles fm1608 correctly.

**Graft point D — Site C (NMOS VPP correction):** After all algorithm overrides (Rules 1/2/3) and Pass 2 _etype re-derivation (beta Step 7), add from v1.12 (chip loop L233-253):

```python
# v1.12 tools/build_db.py (chip loop, after Pass 2) — Site C NMOS block
part_aliases = {a.split("@")[0].strip() for a in name.split(",")}
for nmos_key, nmos_vpp in NMOS_TRUE_VPP_MV.items():
    if nmos_key in part_aliases:
        if _nmos_vpp_mv is None or nmos_vpp > _nmos_vpp_mv:
            _nmos_vpp_mv = nmos_vpp
if _nmos_vpp_mv is not None:
    if _nmos_vpp_mv > RURP_VPP_CEILING_MV:
        _support_status = "vpp-exceeds-max"
        _unsupported_reason = (
            f"VPP {_nmos_vpp_mv // 1000}V exceeds programmer max "
            f"({RURP_VPP_CEILING_MV // 1000}V)"
        )
        proto_id = NON_DISPATCHABLE_ALGO  # CR-01 Option A
    # M2732A (21V) stays supported at corrected voltage
```

**Graft point E — `chip_entry` construction:** beta's chip_entry (lines 506-558) is the base. Add `support_status` key and conditional `unsupported_reason`. Also update `vpp`/`vpp_mv` to respect `_nmos_vpp_mv`:

```python
# Integrated chip_entry pattern (beta L506-558 + v1.12 safety fields)
chip_entry = {
    "part_number": ",".join(
        dict.fromkeys(
            a.split("@")[0].strip()
            for a in name.split(",")
            if a.split("@")[0].strip()
        )
    ),
    "support_status": _support_status,       # NEW (v1.12 graft)
    "electrical": {
        "type": _etype,
        "size_bytes": mem_size,
        "pin_count": pin_count,
        "vpp": (
            f"{_nmos_vpp_mv // 1000}V"                    # NMOS correction (v1.12)
            if _nmos_vpp_mv is not None
            else VPP_VOLTAGES.get(voltages & 0xF0, "Unknown")  # 0xF0 mask (beta BUG-B fix)
        ),
        "vpp_mv": (
            _nmos_vpp_mv                                  # NMOS correction (v1.12)
            if _nmos_vpp_mv is not None
            else VPP_MV.get(voltages & 0xF0, 0)           # 0xF0 mask (beta BUG-B fix)
        ),
        "vcc": VCC_VOLTAGES.get((voltages >> 8) & 0x0F, "5V"),   # bits 11-8 (beta BUG-3 fix)
        "vdd": VCC_VOLTAGES.get((voltages >> 12) & 0x0F, "5V"),  # bits 15-12 (beta BUG-3 fix)
    },
    "programming": {
        "algorithm": proto_id,
        "pulse_duration": interpret_timing(ic.get("pulse_delay"), proto_id),
        "chip_id_check": True if (flags & 0x20) else False,
        "chip_id_value": ic.get("chip_id"),
    },
    "pinout": pinout_key,
}
if _unsupported_reason:                     # NEW (v1.12 graft)
    chip_entry["unsupported_reason"] = _unsupported_reason

# beta L573-574 — SRAM vcc normalization (keep as-is)
if _etype == "SRAM":
    chip_entry["electrical"]["vcc"] = chip_entry["electrical"]["vdd"]
```

**json.dump line:** Use beta's `sort_keys=True` (line 583):

```python
# beta tools/build_db.py L583
json.dump(complete_db, f, indent=2, sort_keys=True)
```

---

### `tools/check_dispatch.py` — v1.12 body + restore beta's structural guard

**Strategy:** Start from v1.12 version (359 lines — has support_status machinery). Add back beta's structural no-vpp-pin guard which v1.12 removed.

**RESTORE from beta — `PINOUTS_FILE` constant (lines 30-33):**

```python
# beta tools/check_dispatch.py L30-33
PINOUTS_FILE = os.environ.get(
    "FIRESTARTER_PINOUTS_FILE",
    os.path.join(_DATA_DIR, "pinouts.json"),
)
```

**RESTORE from beta — `_build_no_vpp_pin_set` function (lines 98-109):**

```python
# beta tools/check_dispatch.py L98-109
def _build_no_vpp_pin_set(pinouts_file):
    """Return the set of pinout keys that have no 'vpp-pin' entry in their pins dict.

    These pinouts have no physical VPP line routed to the socket.  If
    configure_eprom ever asserts P1_VPP_ENABLE on a chip sitting on one of
    these pinouts, the 12 V boost regulator drives a socket pin that is
    actually an address, WE, or NC line on the resident chip — a structural
    VPP hazard that is independent of electrical.type string labelling.
    """
    with open(pinouts_file, encoding="utf-8") as f:
        pinouts = json.load(f)
    return {k for k, v in pinouts.items() if not v.get("pins", {}).get("vpp-pin")}
```

**RESTORE from beta — `novpp_in_eprom` bucket and GATE-03 structural guard in main() (lines 130, 165-177):**

```python
# beta tools/check_dispatch.py L117-130 — in main(), before the chip loop
no_vpp_pin_pinouts = _build_no_vpp_pin_set(PINOUTS_FILE)
# ...
novpp_in_eprom = []   # add to the existing bucket list

# beta tools/check_dispatch.py L165-177 — inside per-chip loop
if handler == "configure_eprom" and pinout in no_vpp_pin_pinouts:
    novpp_in_eprom.append(
        f"{mfg}/{part} proto=0x{proto:02X} pinout={pinout}"
    )
```

**RESTORE from beta — `_28C_EEPROM_HAZARD_ETYPES` set (line 72):** v1.12 only uses `etype == "Flash/EEPROM"` (single string). Beta uses a set covering both "Flash/EEPROM" and "EEPROM":

```python
# beta tools/check_dispatch.py L72
_28C_EEPROM_HAZARD_ETYPES = {"Flash/EEPROM", "EEPROM"}
# And in the loop:
if (
    pinout == _28C_EEPROM_HAZARD_PINOUT
    and etype in _28C_EEPROM_HAZARD_ETYPES   # <- use set membership, not == string
    and handler == "configure_eprom"
):
```

**KEEP from v1.12:** All support_status machinery: `KNOWN_PROTOCOLS` (note: this is the check_dispatch version which intentionally does NOT include 0x34 — see v1.12 L73-87 comment), `not_implemented` bucket, D-10 assertion buckets (`missing_reason`, `pni_with_known_proto`, `non_supported_dispatchable`), updated `dispatch()` with `configure_not_implemented` arm, etype-fallback `mt` derivation (v1.12 L44-53), PASS/FAIL report blocks for new buckets.

**KEEP from v1.12 dispatch() function (L90-114):** Adds `not_implemented` return for non-zero unrecognized protocols:

```python
# v1.12 tools/check_dispatch.py L106-107
if protocol != 0:
    return "not_implemented"
```

**REMOVE from v1.12 `_ALGO_MEM_TYPE` (lines 46-48):** Delete 0x35 and 0x39 entries (they were removed by DEC-05):

```python
# v1.12 check_dispatch.py L46-47 — DELETE these two entries
0x35: 5,  # FLASH_EEPROM_LIKE → TYPE_FLASH_TYPE_4
0x39: 5,  # FLASH_INTEL_ALT   → TYPE_FLASH_TYPE_4
```

---

### `tools/diff_db.py` — merge rule sets from both branches

**Strategy:** Both branches have diverged the `_RATIONALES` dict and `_RULE_FIELD_PATHS` dict. The integrated version needs all rules.

**KEEP from beta (lines 89-108):** `BUG_A_ETYPE` and `BUG_B_VPP` rationale strings:

```python
# beta tools/diff_db.py L89-108
"BUG_A_ETYPE": (
    "BUG-A electrical.type fix — flags-based EEPROM reclassification for 0x07-protocol chips.\n"
    "  Pass 2 previously mapped ALL proto=0x07 chips to 'UV-EPROM', ignoring flags bit 0x10\n"
    "  (electrically erasable). Chips with flags & 0x10 set (W27C512, SST27SF512,\n"
    "  SST27VF512, W27C257, etc.) are CMOS EEPROMs and now decode as 'EEPROM'.\n"
    "  ..."
),
"BUG_B_VPP": (
    "BUG-B VPP decode fix — voltages & 0xF0 mask instead of voltages & 0xFF.\n"
    "  ..."
),
```

**KEEP from v1.12 (diff ~L28-39):** `RULE_PHASE66` rationale string (replaces v1.12's version of those rules):

```python
# v1.12 tools/diff_db.py (via git diff +lines) — RULE_PHASE66
"RULE_PHASE66": (
    "Phase 66 DB inclusion + VPP correction changes.\n"
    "  DB-01: New chips with support_status=protocol-not-implemented included\n"
    "  DB-02: 9 damage-hazard 24-pin EEPROMs included as support_status=adapter-required\n"
    "  DB-03: NMOS high-VPP entries corrected: M2716/M2732=25V (vpp-exceeds-max),\n"
    "    M2732A=21V (supported at corrected voltage). vpp/vpp_mv fields updated.\n"
    "  DB-05: All chips gain explicit support_status=supported (majority, mechanical change).\n"
    "  ..."
),
```

**Integrated `_RULE_FIELD_PATHS` dict:** Must include both sets of field paths:

```python
# beta tools/diff_db.py L180-198 — BUG_A_ETYPE and BUG_B_VPP field paths (restore from beta)
"BUG_A_ETYPE": {
    ("electrical", "type"),
},
"BUG_B_VPP": {
    ("electrical", "vpp"),
    ("electrical", "vpp_mv"),
},
# v1.12 diff_db.py — RULE_PHASE66 field paths (keep from v1.12)
"RULE_PHASE66": {
    ("support_status",),
    ("unsupported_reason",),
    ("electrical", "vpp"),
    ("electrical", "vpp_mv"),
},
```

**Integrated `_classify_diff` function:** The detection logic must handle all rule labels. The ordering matters — RULE_PHASE66 must not shadow BUG_A_ETYPE (type_diff is not a RULE_PHASE66 field):

```python
# Integrated _classify_diff ordering (beta ordering preserved, RULE_PHASE66 appended)
# From beta L274-108 — keep existing labels first
if ...:
    label = "RULE_ALGO"
elif ...:
    label = "BUG2_AND_BUG3"
elif ...:
    label = "BUG2_TIMING"
elif ...:
    label = "BUG3_VCC_VDD"
elif pinout_diff and not algo_diff and not timing_diff:
    label = "SRAM_PINOUT"
elif type_diff and not algo_diff and not timing_diff and not voltage_diff and not pinout_diff:
    label = "BUG_A_ETYPE"    # restore from beta
elif vpp_diff and not algo_diff and not timing_diff and not pinout_diff and not type_diff:
    label = "BUG_B_VPP"      # restore from beta (but see note: RULE_PHASE66 also covers vpp_diff)
# From v1.12 — add RULE_PHASE66 last (least specific)
elif phase66_diff and not algo_diff and not timing_diff and not voltage_diff and not pinout_diff:
    label = "RULE_PHASE66"
```

**Note on BUG_B_VPP vs RULE_PHASE66:** In the integrated DB, the only remaining vpp/vpp_mv diffs in a stage-(a) diff (vs v1.11 beta 743-chip baseline) will be NMOS-corrected chips — those fall under RULE_PHASE66. BUG_B_VPP is a historical rule that classified changes already present in the committed beta DB (vs the 734-chip pre-v1.11 baseline). The two rules can coexist since BUG_B_VPP also requires `not type_diff`, which RULE_PHASE66 does not conflict with.

**Update GATE-02 header comment (line 4):** Change baseline chip count from 734 to 744 after baseline refresh.

---

### `tools/baseline/chip_database.baseline.json` — refresh after regen

This is a data artifact, not a code file. No pattern excerpts apply. The action is:

```bash
# After build_db.py regenerates chip_database.json with 744 chips and all gates pass:
cp firestarter/data/chip_database.json tools/baseline/chip_database.baseline.json
```

The 734-chip pre-v1.11 anchor becomes historical. The new 744-chip integrated output becomes the Phase 70 GATE-01 anchor.

---

### `firestarter/data/chip_database.json` — build artifact

Never hand-merge. Regenerate:

```bash
cd /workspaces/firestarter_app
python tools/build_db.py
```

Expected output: 744 chips (743 existing + X88C64P = 744).

---

## Shared Patterns

### v1.11 Decode Regressions — Apply to `build_db.py` Only

These fixes are IN beta and MISSING or REGRESSED in v1.12. Do NOT carry from v1.12:

| Regression | v1.12 (WRONG) | Beta (CORRECT) | Critical for |
|---|---|---|---|
| `interpret_timing` ×100 | `val * 100 us` for 0x07/0x0B | `val us` for all | DEC-03, SC#2 |
| VPP mask | `voltages & 0xFF` | `voltages & 0xF0` | BUG-B |
| vcc/vdd bit positions | vdd at bits 11-8, vcc at bits 15-12 | vcc at bits 11-8, vdd at bits 15-12 | BUG-3 |
| VCC_VOLTAGES table | Missing 0x02/0x03 entries | Has 0x02:"4V", 0x03:"4.5V" | BUG-1 |
| Pass 2 _etype for 0x07 | ALL 0x07 → "UV-EPROM" | flags & 0x10 → "EEPROM" | BUG-A |
| KNOWN_PROTOCOLS | Includes 0x35, 0x39 | Excludes both | DEC-05 |
| PROTOCOL_MAP | Stale 0x11/0x2A/0x2C/0x2E/0x35/0x39/0x3C entries | Canonical only, exclusions documented | DEC-05 |
| json.dump | No sort_keys | sort_keys=True | GATE-02 |

### v1.12 Safety Features — Apply to `build_db.py` and `check_dispatch.py`

| Feature | Where | Source (v1.12 lines) |
|---|---|---|
| `NMOS_TRUE_VPP_MV` + `RURP_VPP_CEILING_MV` | build_db.py module-top | L86-93 |
| `NON_DISPATCHABLE_ALGO = 0x00` | build_db.py module-top | L122 |
| `0x34` in KNOWN_PROTOCOLS | build_db.py + check_dispatch.py | L98-113 (build), L73-87 (check — different semantics, see comment) |
| `_support_status` / `_unsupported_reason` loop vars | build_db.py main() | L182-184 |
| Site A gate (proto 0x34) | build_db.py main() | L200-208 |
| Site B gate (24-pin adapter-required) | build_db.py main() | L24-47 of chip loop |
| Site C NMOS VPP correction block | build_db.py main() | L233-253 of chip loop |
| `support_status` field in chip_entry | build_db.py main() | L272 |
| `unsupported_reason` conditional add | build_db.py main() | L300-301 |
| `dispatch()` → `not_implemented` arm | check_dispatch.py | L106-107 |
| D-10 assertion buckets | check_dispatch.py | L15-24 of main() |
| support_status-aware scan logic | check_dispatch.py | L57-119 of main() |
| `RULE_PHASE66` rationale + field paths | diff_db.py | git diff +lines 28-60 |

### GATE-03 Structural Guard — Must Not Be Lost

The no-vpp-pin structural guard exists ONLY in beta's `check_dispatch.py`. v1.12 removed it. The integrated version must have ALL of:

1. `PINOUTS_FILE` constant (env-overridable)
2. `_build_no_vpp_pin_set(pinouts_file)` function
3. `no_vpp_pin_pinouts = _build_no_vpp_pin_set(PINOUTS_FILE)` at start of main()
4. `novpp_in_eprom = []` bucket
5. Per-chip: `if handler == "configure_eprom" and pinout in no_vpp_pin_pinouts:`
6. FAIL block reporting for `novpp_in_eprom`

Source: beta `tools/check_dispatch.py` lines 30-33, 98-109, 117-119, 130, 165-177, 239-248.

---

## Verification Commands (Per Success Criterion)

| SC | Command | Expected |
|---|---|---|
| SC#1 (no guess tables) | `grep -c "DIP28_VARIANT_MAP\|PIN_MAP_TO_PINOUT" tools/build_db.py` | 0 |
| SC#2 (timing decode) | `cd /workspaces/firestarter_app && python -c "from tools.build_db import interpret_timing; print(interpret_timing('64', 0x07))"` | `100 us` |
| SC#2 (VPP mask) | After regen: `python -c "import json; db=json.load(open('firestarter/data/chip_database.json')); chips=[c for m in db.values() for c in m if 'SST27VF512' in c.get('part_number','')]; print(chips[0]['electrical']['vpp_mv'])"` | `12000` |
| SC#3 (GATE-03) | `cd /workspaces/firestarter_app && python tools/check_dispatch.py` | PASS: 744 chips |
| SC#4 stage (a) | `FIRESTARTER_BASELINE_FILE=/tmp/v1.11-beta-db.json python tools/diff_db.py` | Exit 0, 0 UNEXPLAINED |
| SC#4 stage (b) | `FIRESTARTER_BASELINE_FILE=tools/baseline/chip_database.baseline.json python tools/diff_db.py` | Exit 0, 0 UNEXPLAINED |
| SC#5 (CI gate) | `ruff check . && ruff format --check . && pytest --cov-fail-under=70` | All green |

---

## No Analog Found

No files in scope lack a concrete analog — all target files exist on both branches with full source available. The "analog" for each file is its counterpart branch revision, not an external pattern.

---

## Files with No Code Changes Required (merges clean)

Per RESEARCH.md D-08, the following host runtime files merge into beta without conflict and require no re-port work:

| File | Action | Branch |
|---|---|---|
| `firestarter/chip_resolver.py` | `git merge` picks up cleanly | v1.12 |
| `firestarter/exceptions.py` | `git merge` picks up cleanly | v1.12 |
| `firestarter/cli_handlers.py` | `git merge` picks up cleanly | v1.12 |
| `firestarter/frame_parser.py` | `git merge` picks up cleanly | v1.12 |
| `firestarter/messages.py` | Already on v1.12 branch; codegen-locked | v1.12 |
| `firestarter/` firmware sub-repo | Clean 5-commit fast-forward merge | v1.12 |

---

## Metadata

**Analog search scope:** `/workspaces/firestarter_app/tools/` on beta + `git show v1.12-protocol-dispatch-hardening:tools/*`
**Files scanned:** 5 source files × 2 branches = 10 readings
**Pattern extraction date:** 2026-06-15

# Phase 70: v1.11 + v1.12 DB-Pipeline Integration for Beta Merge — Research

**Researched:** 2026-06-15
**Domain:** DB-build pipeline integration / re-port (HOST-ONLY)
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Re-port **on the `v1.12-protocol-dispatch-hardening` branch**. Rewrite
  `build_db.py` / `check_dispatch.py` / `diff_db.py` there to sit on beta's
  principled `resolve_pinout_key` architecture, regenerate `chip_database.json`, get
  all gates green — THEN merge v1.12→beta (now near-clean) as the final step.
- **D-02:** Prefer **extending the mask logic in v1.11's `resolve_pinout_key`
  natively** so the per-chip SRAM override hacks are not needed. Fix the principled
  mask logic itself rather than layering overrides.
- **D-03 (guardrail):** The **zero-decode-regression criterion wins** over purity.
  Research surfaces which chips beta's principled resolve mis-routes (if any) and
  recommends, per chip, whether mask-extension or a documented per-chip override is
  correct. No blanket stance — case-by-case, evidence-driven.
- **D-04:** Use a **two-stage diff**: (a) decode/pinout changes — near-zero to prove
  no v1.11 regression; (b) additive safety-field changes — expected bulk, each
  categorized by a documented rule.
- **D-05:** Baseline for stage (a) is the **v1.11 beta `chip_database.json`** (743
  chips, the committed DB on beta). v1.11's pinned `chip_database.baseline.json`
  (734 chips, GATE-01 anchor) must be reconciled/refreshed as part of this work.
- **D-06:** Firmware **is in scope** for Phase 70, but the phase **STOPS before any
  tag**. Perform the firmware `v1.12→beta` merge, build both envs (uno + leonardo),
  run native dispatch tests, and confirm wire-constant parity with the host.
- **D-07:** The **beta pre-release tag / beta-cut stays operator-gated** — do NOT cut
  any tag in either repo during this phase.
- **D-08:** (implied from scope) HOST runtime code (`chip_resolver.py`,
  `exceptions.py`, `cli_handlers.py`, `frame_parser.py`) merges clean — only the
  DB-build pipeline collides.

### Claude's Discretion

- Exact task breakdown and ordering within the re-port.
- Whether `diff_db.py` itself needs a `--stage` flag or two invocations (D-04).
- Specific test/snapshot updates required by the regenerated DB.

### Deferred Ideas (OUT OF SCOPE)

- Beta cut + lockstep pre-release tag — operator-gated, out of Phase 70 (D-07).
- v1.12 milestone close — blocked on this integration phase; follows the beta merge.
</user_constraints>

---

## Summary

Phase 70 is an integration re-port, not a textual merge. The fundamental collision: v1.12 was forked from the pre-v1.11 beta (`faaa571` — June 8, 2026) and has 34 commits ahead of that fork point. v1.11 landed 20 commits on beta between the fork and today, the most important being Phase 58 which deleted `DIP28_VARIANT_MAP`, `PIN_MAP_TO_PINOUT`, and `PIN_MAP_PROTO_TO_PINOUT` and replaced them with a principled `resolve_pinout_key(pin_count, variant, flags_int, pm_idx, proto_id, type_int, mem_size)` function. v1.12's `build_db.py` was built on top of those deleted tables and therefore cannot be textually merged.

The re-port strategy (D-01) is: on the v1.12 branch, rewrite the DB-build tooling (`build_db.py`, `check_dispatch.py`, `diff_db.py`) so it uses beta's principled `resolve_pinout_key` as its sole pinout path, while grafting in v1.12's safety features (`support_status` taxonomy, NMOS VPP correction, `NON_DISPATCHABLE_ALGO`, inclusion gates). Then regenerate `chip_database.json` and get all gates green before merging v1.12→beta.

Research reveals that v1.12's `build_db.py` also regresses three v1.11 decode fixes (BUG-2 timing ×100 still present, BUG-3 vcc/vdd bit positions swapped, BUG-B VPP mask is `0xFF` not `0xF0`). These must NOT be carried over; beta's corrected versions must be preserved. Conversely, v1.12 has one decode improvement beta lacks: its Pass 2 `_etype` derivation preserves flags-based EEPROM classification for 0x07-protocol chips with `flags & 0x10` (BUG-A fix), while beta's Pass 2 correctly maps these as `_etype = "EEPROM"` too. Both branches agree on this; no regression risk there.

The firmware merge is straightforward: the `firestarter` firmware sub-repo v1.12 branch has exactly 5 commits ahead of beta (Phase 62/63/64 work: `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` catalog + `configure_not_implemented` handler + fail-closed dispatch guard). Beta firmware has 0 commits ahead of v1.12's firmware fork point — the firmware merge is clean with no conflict.

**Primary recommendation:** On the v1.12 branch, perform a surgical transplant: (1) replace v1.12's `resolve_pinout_key` body + deleted tables with beta's exact function body; (2) graft v1.12's safety features (`support_status`, NMOS VPP, NON_DISPATCHABLE_ALGO, inclusion gates) into the transplanted build_db.py; (3) fix the three v1.11 decode regressions in v1.12 build_db.py (`interpret_timing`, `vcc/vdd` bit positions, `voltages & 0xF0` mask); (4) update `diff_db.py` and `check_dispatch.py` to handle `support_status`-aware two-stage diff; (5) regenerate DB; (6) run gates; (7) merge firmware; (8) merge v1.12→beta.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Pinout selection (`resolve_pinout_key`) | DB-build pipeline (`tools/build_db.py`) | — | Sole pinout path per SC#1 / D-02; no runtime override allowed |
| Support-status taxonomy | DB-build pipeline (`tools/build_db.py`) | Host runtime (`chip_resolver.py`) | DB is the canonical source; host guard enforces at runtime |
| GATE-03 VPP-safety scan | `tools/check_dispatch.py` | CI (`pytest`) | Structural gate; must run against regenerated DB |
| Per-chip diff regression gate | `tools/diff_db.py` | CI (manual) | Two-stage: decode near-zero (a) then additive safety fields (b) |
| Wire-constant parity | `firestarter/messages.py` (host) + `firestarter/include/messages.h` (FW) | CI | Dual-repo lockstep via `catalog/codegen.py` |
| Dispatch correctness | `firestarter/src/proms/memory.cpp` (FW) | `tools/check_dispatch.py` (mirror) | FW is ground truth; check_dispatch.py is a host-side mirror |

---

## Standard Stack

### Core (no new packages — HOST-ONLY tooling re-port)

| Tool | Current State | Notes |
|------|--------------|-------|
| `tools/build_db.py` | 589 lines (beta) / 715 lines (v1.12) | Must be rewritten in-place on v1.12 branch |
| `tools/check_dispatch.py` | 277 lines (beta) / 359 lines (v1.12) | v1.12 version is the target — has support_status awareness |
| `tools/diff_db.py` | 486 lines (beta, identical to v1.12 header) | v1.12 added RULE_PHASE66; beta has BUG_A_ETYPE + BUG_B_VPP |
| `chip_database.json` | 743 chips (beta) / 744 chips (v1.12) | Regenerated artifact; never hand-merged |
| `chip_database.baseline.json` | 734 chips (tools/baseline/) | GATE-01 anchor; must be refreshed for Phase 70 |

**No new pip packages.** This phase touches only existing tooling files. The CI gate (ruff + mypy + pytest --cov-fail-under=70) remains unchanged. [ASSUMED]

---

## Architecture Patterns

### System Architecture Diagram

```
infoic.xml (pinned snapshot @ a8efaedc)
    |
    v
build_db.py (v1.12 branch — REWRITTEN with beta's resolve_pinout_key + v1.12 safety features)
    |
    +-- resolve_pinout_key() [beta's principled fn — SOLE pinout path]
    +-- support_status taxonomy [v1.12 feature — grafted in]
    +-- NMOS_TRUE_VPP_MV correction [v1.12 feature]
    +-- NON_DISPATCHABLE_ALGO=0x00 [v1.12 feature]
    +-- inclusion gates (X88C64P, 24-pin EEPROMs) [v1.12 feature]
    |
    v
chip_database.json (regenerated — 744 chips with support_status on every record)
    |
    +--[stage a diff]--> diff_db.py (baseline=v1.11 beta 743-chip DB) → near-zero
    +--[stage b diff]--> diff_db.py (NEW rules: RULE_PHASE66 + v1.11 rules) → documented bulk
    |
    +--[GATE-03]-------> check_dispatch.py (support_status-aware) → 0 violations
    |
    v
Host runtime (merges clean — no changes needed):
  chip_resolver.py | exceptions.py | cli_handlers.py | frame_parser.py

Firmware (firestarter/ sub-repo — merge v1.12→beta):
  configure_not_implemented() | MSG_ERR_PROTOCOL_NOT_IMPLEMENTED | native tests
```

### Recommended Project Structure (no changes)
```
firestarter_app/
├── tools/
│   ├── build_db.py          # REWRITTEN on v1.12 branch
│   ├── check_dispatch.py    # EXISTS on v1.12 branch (support_status-aware)
│   ├── diff_db.py           # UPDATE: add RULE_PHASE70 / restore BUG_A/BUG_B rules
│   └── baseline/
│       └── chip_database.baseline.json  # REFRESH to 744-chip v1.11+v1.12 regen
├── firestarter/
│   └── data/
│       └── chip_database.json  # REGENERATE (never hand-merge)
└── tests/
    └── test_build_db_inclusion.py  # EXISTS on v1.12 (carry over)
```

---

## Research Question 1: `resolve_pinout_key` Divergence

### Beta (v1.11) — Principled Mask-Based Function [VERIFIED: source read 2026-06-15]

```python
def resolve_pinout_key(
    pin_count, variant, flags_int, pm_idx=None, proto_id=None, type_int=1, mem_size=0
):
```

**Logic (pure `if/elif` on `pm_idx` within each `pin_count` branch):**

- **24-pin:** pm_idx=23 → variant_lo=0x01→`DIP24_2732`, variant_lo=0x10→`DIP24_2816`, else→`DIP24_2716`; pm_idx=0→`DIP24_6116` (SRAM); else→None (D-06 fail-safe)
- **28-pin:** pm_idx=22 → variant_lo=0x10→`DIP28_27512`, 0x11→`DIP28_27256`, else→`DIP28_2764`; pm_idx=21→`DIP28_2764`; pm_idx=20→`DIP28_28C256`; pm_idx=19→`DIP28_28C64`; pm_idx=18→`DIP28_28C64`; pm_idx=0 with type=4 or SRAM proto → mem_size≤8192→`DIP28_JEDEC_SRAM_8K` else `DIP28_28C256`; pm_idx=0 + proto=0x05→`DIP28_28C256`; else→None
- **32-pin:** pm_idx=0→`DIP32_SST39SF040`; pm_idx in {5,7,9,10,11,12,13} → proto_id={0x05,0x06}→`DIP32_SST39SF040`, 0x0D→`DIP32_28C512_EEPROM`, {0x07,0x08,0x10}→`DIP32_STD`; else→None
- **Returns None** for all unclassifiable cases → D-06 fail-safe skip in main().

**Key signature difference:** Beta adds `type_int=1` and `mem_size=0` as parameters. The 28-pin pm_idx=0 SRAM branch uses both. v1.12 does NOT have these parameters.

### v1.12 — Guess-Table Function [VERIFIED: source read 2026-06-15]

```python
def resolve_pinout_key(pin_count, variant, flags_int, pm_idx=None, proto_id=None):
```

**Logic (3-tier lookup: PIN_MAP_PROTO_TO_PINOUT → PIN_MAP_TO_PINOUT → variant/default):**

- Tier 1: `(pin_count, pm_idx, proto_id)` from `PIN_MAP_PROTO_TO_PINOUT` (large dict, e.g. `(32,7,0x05)→DIP32_SST39SF040`)
- Tier 2: `(pin_count, pm_idx)` from `PIN_MAP_TO_PINOUT` (maps to key or None)
- Tier 3: variant-based fallback — 24-pin uses `(variant & 0xFF)==1` for 2732, else 2716; 28-pin uses `DIP28_VARIANT_MAP.get(variant & 0xFF, "DIP28_2764")`; 32-pin defaults `DIP32_STD`
- Returns guess-table or default; **does not return None for unclassifiable** (may return wrong key)

**Key difference:** v1.12's Tier 3 fallback for 28-pin chips uses `DIP28_VARIANT_MAP` which maps variant_lo to specific pinouts. The 28-pin pm_idx=0 SRAM chips fall through to Tier 3 and get `DIP28_2764` (wrong — SRAM chips need `DIP28_JEDEC_SRAM_8K` or `DIP28_28C256`). This is why v1.12 needs the per-chip SRAM override block after `resolve_pinout_key`.

**Conclusion for D-02:** Beta's principled function already handles the correct routing for the cases v1.12 fixes via overrides, PROVIDED `type_int` and `mem_size` are passed correctly. The transplant is a function-body swap: replace v1.12's function body with beta's body, add the `type_int=1, mem_size=0` parameters, pass them from main().

---

## Research Question 2: Per-Chip SRAM Override Enumeration (D-02/D-03)

[VERIFIED: source read of v1.12 build_db.py 2026-06-15]

v1.12 has TWO override blocks that fire after `resolve_pinout_key`. Both exist because v1.12's Tier 3 fallback routes SRAM chips incorrectly.

### Override Block A: fm1608 override (type=4 AND proto in {0x07, 0x08, 0x0B})

**Chips affected:** Ramtron parallel FRAM: FM1208, FM1608, FM16W08, FM1808, FM18L08 and 24-pin equivalents (DS1220RW, M48T02/12, M48Z02/12, ST/M48T02/12).

**What v1.12 does:**
- Flips proto_id → 0x28 (SRAM_STD)
- 28-pin ≤8K: pinout → `DIP28_JEDEC_SRAM_8K`
- 28-pin >8K: pinout → `DIP28_28C256`
- 24-pin: pinout → `DIP24_6116`

**Does beta's resolve_pinout_key handle this correctly?**
YES. Beta's `resolve_pinout_key` with `type_int=4` and `pm_idx=0` routes to the `if type_int == 4 or proto_id in {0x27, 0x28, 0x29}:` branch and applies the mem_size discriminator. However, the fm1608 override fires BEFORE `resolve_pinout_key` in v1.12 (which changes proto_id to 0x28 BEFORE the pinout call), while beta applies the type=4 logic INSIDE `resolve_pinout_key`. In beta's main(), `resolve_pinout_key` is called with the ORIGINAL proto_id (0x07/0x0B) and type_int=4 — the function correctly handles it because it checks `type_int == 4` first.

**Recommendation (D-02):** The fm1608 block in v1.12 can be ELIMINATED when beta's `resolve_pinout_key` (with `type_int` parameter) is used. However, the proto_id flip to 0x28 must still happen in main() AFTER the pinout is resolved (Rule 3 in beta). Beta already has this as "Step 6: Rule 3" in its main() loop. Use beta's Rule 3 pattern verbatim.

### Override Block B: Native 28-pin SRAM (proto_id==0x28, type=4, pm_idx=0, pinout=="DIP28_2764")

**Chips affected (from v1.12 SUMMARY.md comments):**
- DS1225(TEST)/8K, DS1230AB/DS1230Y/DS1230W/32K — Dallas NVRAM
- BQ4010YMA(TEST)/8K, BQ4011YMA/BQ4011LYMA/32K — TI NVRAM
- W2464/W2465/8K, W24256/W24257A/32K — Winbond SRAM
- 6164/6264/8K, 61256/62256/32K — generic JEDEC SRAM
- (14 chips total per STATE.md Phase 67.1-01 decision)

**What v1.12 does:**
- Gate: `pin_count==28 AND pm_idx==0 AND proto_id==0x28 AND type_int==4 AND pinout_key=="DIP28_2764"`
- ≤8K: pinout → `DIP28_JEDEC_SRAM_8K`
- >8K: pinout → `DIP28_28C256`

**Does beta's resolve_pinout_key handle this correctly?**
YES. In beta's `resolve_pinout_key`, the `pm_idx == 0` branch checks `if type_int == 4 or proto_id in {0x27, 0x28, 0x29}:` — this catches both fm1608 chips (type=4, proto originally 0x07, then overridden) AND native SRAM chips (type=4, proto=0x28 natively). The mem_size discriminator routes them correctly. These 14 chips get `DIP28_JEDEC_SRAM_8K` (≤8K) or `DIP28_28C256` (>8K) directly from the principled function.

**Recommendation (D-02/D-03):** Override Block B can be ELIMINATED entirely when beta's `resolve_pinout_key` is transplanted. No per-chip override needed.

### Summary: All v1.12 SRAM Overrides Fold Into Beta's Principled Function

| Override Type | v1.12 Approach | Beta Approach | Recommendation |
|--------------|----------------|---------------|----------------|
| fm1608 FRAM (type=4, proto=0x07/0x0B, 28-pin) | Post-resolve override block A | `resolve_pinout_key` pm_idx=0 + type_int=4 branch | Eliminate — beta handles natively |
| 24-pin SRAM (type=4, 24-pin, pm_idx=0) | Override inside fm1608 block | pm_idx=0 → `DIP24_6116` (beta already has this) | Eliminate — beta handles natively |
| Native 28-pin SRAM (proto=0x28, pm_idx=0) | Override Block B | `resolve_pinout_key` pm_idx=0 + proto in {0x28} branch | Eliminate — beta handles natively |

**D-03 result:** Zero per-chip overrides needed. Beta's principled mask logic already covers all 14 v1.12 SRAM chips correctly. The D-02 preference (extend mask logic natively) is satisfied without any mask extension — the function already handles these cases.

---

## Research Question 3: v1.12 Safety Features to Re-port

[VERIFIED: source read of v1.12 build_db.py 2026-06-15]

These are the constants, logic blocks, and behaviors that must be grafted onto beta's build_db.py:

### Feature 1: `support_status` Taxonomy

**Location:** v1.12 build_db.py, throughout main() loop.

**What it adds:**
```python
_support_status = "supported"   # default at loop top
_unsupported_reason = None      # set by inclusion gates / NMOS block

# Site A: X88C64P (proto 0x34)
_support_status = "protocol-not-implemented"
_unsupported_reason = "protocol not implemented: 0x34 (XICOR NovRAM serial-parallel hybrid)"

# Site B: 24-pin 5V EEPROM hazard (pin_count==24, proto in (0x07,0x08,0x0B), flags&0x10)
_support_status = "adapter-required"
_unsupported_reason = "adapter required: requires a dedicated DIP24 EEPROM adapter..."
proto_id = NON_DISPATCHABLE_ALGO  # CR-01 Option A

# Site C: NMOS VPP exceeds ceiling
_support_status = "vpp-exceeds-max"
_unsupported_reason = f"VPP {_nmos_vpp_mv // 1000}V exceeds programmer max ({RURP_VPP_CEILING_MV // 1000}V)"
proto_id = NON_DISPATCHABLE_ALGO  # CR-01 Option A

chip_entry["support_status"] = _support_status
if _unsupported_reason:
    chip_entry["unsupported_reason"] = _unsupported_reason
```

**Graft location in beta build_db.py:** Add `_support_status = "supported"; _unsupported_reason = None` at the top of the chip processing block. Add Site A gate just after the unknown-protocol WARN-skip (proto_id==0x34 branch). Add Site B gate after the filter (before resolve_pinout_key call). Add Site C after all algorithm overrides. Add `support_status` and `unsupported_reason` to `chip_entry`.

### Feature 2: `RURP_VPP_CEILING_MV` and `NMOS_TRUE_VPP_MV`

**Location:** v1.12 build_db.py ~L86-L97.

```python
NMOS_TRUE_VPP_MV: dict[str, int] = {
    "M2716": 25000,
    "M2732": 25000,
    "M2732A": 21000,
}
RURP_VPP_CEILING_MV = 22000
```

**Graft location:** Add as module-top constants in beta build_db.py (after VPP_MV dict).

### Feature 3: `NON_DISPATCHABLE_ALGO = 0x00`

**Location:** v1.12 build_db.py ~L122.

```python
NON_DISPATCHABLE_ALGO = 0x00
```

**Why it works:** `dispatch(0x00, None)` → mem_type fallback → `{1:..., 4:..., 3:..., 5:...}.get(None, "ERROR")` → "ERROR". No real handler reached.

**Graft location:** Add as module-top constant in beta build_db.py.

### Feature 4: `0x34` (X88C64P) in `KNOWN_PROTOCOLS`

**Location:** v1.12 build_db.py, KNOWN_PROTOCOLS set.

```python
KNOWN_PROTOCOLS = {
    0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29,
    0x34,  # XICOR X88C64P — DIP-parallel NovRAM; included as protocol-not-implemented
}
```

**Note:** 0x35 and 0x39 must NOT be added (DEC-05 — removed in v1.11). Beta's KNOWN_PROTOCOLS correctly excludes them.

**Graft:** Add 0x34 to beta's KNOWN_PROTOCOLS set.

### Feature 5: True-NMOS VPP Correction (~v1.12 L630-660)

**Logic:**
```python
part_aliases = {a.split("@")[0].strip() for a in name.split(",")}
for nmos_key, nmos_vpp in NMOS_TRUE_VPP_MV.items():
    if nmos_key in part_aliases:
        if _nmos_vpp_mv is None or nmos_vpp > _nmos_vpp_mv:
            _nmos_vpp_mv = nmos_vpp
if _nmos_vpp_mv is not None:
    if _nmos_vpp_mv > RURP_VPP_CEILING_MV:
        _support_status = "vpp-exceeds-max"
        _unsupported_reason = f"VPP {_nmos_vpp_mv // 1000}V exceeds programmer max ({RURP_VPP_CEILING_MV // 1000}V)"
        proto_id = NON_DISPATCHABLE_ALGO
    # M2732A (21V) stays supported at corrected voltage
```

The NMOS block also updates `chip_entry["electrical"]["vpp"]` and `chip_entry["electrical"]["vpp_mv"]` to the corrected values. However it must use the correct VPP mask from beta: `VPP_VOLTAGES.get(voltages & 0xF0, "Unknown")` — NOT v1.12's broken `voltages & 0xFF`.

**Graft location:** After all algorithm overrides (Rules 1/2/3), before `chip_entry` construction.

### Feature 6: Capability-Honest Inclusion Gate (Site B: 24-pin 5V EEPROMs)

This is already present in beta as a "skip" (chips skipped via `pinout_key is None` fail-safe). v1.12 converts the skip to an "include as adapter-required". The gate predicate:

```python
if (pin_count == 24
    and proto_id in (0x07, 0x08, 0x0B)
    and (flags & 0x10)):
    _support_status = "adapter-required"
    _unsupported_reason = "adapter required: ..."
    proto_id = NON_DISPATCHABLE_ALGO
```

**Key insight:** In beta, these chips resolve to `DIP24_2716` via `resolve_pinout_key` (pm_idx=23, variant_lo NOT 0x10 and NOT 0x01) and pass the `pinout_key is None` fail-safe. They then hit Rule 1 (DIP24_2816 check) — but they don't land on DIP24_2816. They are NOT currently in beta's chip_database.json as adapter-required. The Site B gate must be applied BEFORE the pinout call (to set `_support_status` and demote proto_id to 0x00 before resolve_pinout_key runs). However, note the pinout call still happens — these chips will get a pinout key but with algorithm=0x00 they route to ERROR via dispatch().

**Ordering invariant:** Site B gate must fire BEFORE `resolve_pinout_key` is called (so that `proto_id = NON_DISPATCHABLE_ALGO` is in effect when the pinout is resolved — affects any tier-1 lookup that keys on proto_id).

---

## Research Question 4: v1.11 Decode Fixes to PRESERVE

[VERIFIED: source read of both branches 2026-06-15]

These fixes are IN beta but ABSENT or REGRESSED in v1.12:

### Fix 1: `interpret_timing` — NO ×100 multiplier (BUG-2, DEC-03)

**Beta (correct):**
```python
def interpret_timing(raw_hex, protocol_id):
    # Raw pulse_delay is microseconds for ALL protocols — no multiplier.
    val = int(raw_hex, 16)
    if protocol_id in (0x07, 0x08, 0x0B):
        return f"{val} us"
    return "Algorithm Controlled"
```

**v1.12 (REGRESSED — still has ×100 for 0x07 and 0x0B):**
```python
    if protocol_id == 0x0B:
        return f"{val * 100} us"
    if protocol_id == 0x07:
        return f"{val * 100} us"
    if protocol_id == 0x08:
        return f"{val} us"
```

**Action:** Use beta's `interpret_timing` verbatim. Do NOT carry v1.12's version.

### Fix 2: `voltages & 0xF0` VPP-nibble mask (BUG-B)

**Beta (correct):**
```python
"vpp": VPP_VOLTAGES.get(voltages & 0xF0, "Unknown"),
"vpp_mv": VPP_MV.get(voltages & 0xF0, 0),
```

**v1.12 (REGRESSED — uses `voltages & 0xFF`):**
```python
"vpp": VPP_VOLTAGES.get(voltages & 0xFF, "Unknown"),
"vpp_mv": VPP_MV.get(voltages & 0xFF, 0),
```

**Action:** Use `voltages & 0xF0` from beta. Critical: v1.12's NMOS VPP correction block overrides `vpp`/`vpp_mv` when `_nmos_vpp_mv is not None` — that path is fine. The base case (non-NMOS chips) must use `& 0xF0`.

### Fix 3: Corrected `vcc`/`vdd` bit positions (BUG-3, DEC-04)

**Beta (correct):**
```python
"vcc": VCC_VOLTAGES.get((voltages >> 8) & 0x0F, "5V"),   # bits 11-8
"vdd": VCC_VOLTAGES.get((voltages >> 12) & 0x0F, "5V"),  # bits 15-12
```

**v1.12 (REGRESSED — swapped):**
```python
"vdd": VCC_VOLTAGES.get((voltages >> 8) & 0x0F, "5V"),   # WRONG: this is vcc
"vcc": VCC_VOLTAGES.get((voltages >> 12) & 0x0F, "5V"),  # WRONG: this is vdd
```

**Action:** Use beta's corrected field order. Note the SRAM vcc normalization in beta (`if _etype == "SRAM": chip_entry["electrical"]["vcc"] = chip_entry["electrical"]["vdd"]`) must also be preserved.

### Fix 4: `VCC_VOLTAGES` entries for 0x02/0x03 (BUG-1, DEC-04)

**Beta (correct):** Has `0x02: "4V"` and `0x03: "4.5V"`.
**v1.12 (MISSING these two entries):** Only has `{0x00, 0x01, 0x04, 0x05}`.

**Action:** Use beta's full VCC_VOLTAGES table.

### Fix 5: No `0x35`/`0x39` in KNOWN_PROTOCOLS (DEC-05)

**Beta (correct):** KNOWN_PROTOCOLS has `{0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29}`.
**v1.12 (REGRESSED):** Includes `0x34, 0x35, 0x39` — the latter two were removed by v1.11 DEC-05. Note: `0x34` must be added (v1.12 safety feature), but `0x35` and `0x39` must NOT be added.

**Action:** Use beta's KNOWN_PROTOCOLS + add only `0x34`.

### Fix 6: Canonical PROTOCOL_MAP (DEC-05)

**Beta (correct):** PROTOCOL_MAP uses only canonical `IC2_ALG_*` names; excludes 0x2A/0x2C/0x2E/0x35/0x3C with explicit exclusion comments; 0x39 documented as phantom.
**v1.12 (REGRESSED):** Has stale `PROTOCOL_MAP` with 0x11/0x2A/0x2C/0x2E/0x35/0x39/0x3C entries.

**Action:** Use beta's canonical PROTOCOL_MAP.

### Fix 7: Sort_keys=True for deterministic output (GATE-02)

**Beta:** `json.dump(complete_db, f, indent=2, sort_keys=True)`.
**v1.12:** `json.dump(complete_db, f, indent=2)` — no sort_keys.

**Action:** Use beta's sorted output.

### Fix 8: Pass 2 `_etype` — preserves flags-based EEPROM for 0x07 chips (BUG-A)

**Beta (correct — introduced in Phase 59 follow-up cca7d62):**
```python
if proto_id in {0x07, 0x08, 0x0B}:
    if flags & 0x10:
        _etype = "EEPROM"
    else:
        _etype = "UV-EPROM"
```

**v1.12 (earlier Pass 2 — maps ALL 0x07 chips to UV-EPROM):**
```python
elif proto_id in {0x07, 0x08, 0x0B}:
    _etype = "UV-EPROM"
```

**Action:** Use beta's flags-aware Pass 2 derivation. This ensures W27C512, SST27SF512, SST27VF512, W27C257 etc. correctly show `_etype="EEPROM"` rather than "UV-EPROM".

---

## Research Question 5: Two-Stage Diff (D-04/D-05)

### Stage (a): Decode/Pinout Regression Check

**Baseline:** The v1.11 beta `chip_database.json` (743 chips, currently committed on the beta branch).

**Expected outcome:** Near-zero changes. The integrated build_db.py uses beta's principled `resolve_pinout_key` and beta's corrected decode functions — so regeneration from the same infoic.xml should produce the same core decode fields for the existing 743 chips. The only decode-field change expected is `_etype` for SRAM chips that v1.12 re-routed (already in beta via SRAM_PINOUT rule).

**New chips added (stage a):** Up to 10 new chips relative to v1.11 beta 743-chip DB (v1.12 added X88C64P and 9 adapter-required 24-pin EEPROMs). These appear as "NEW" in diff_db.py output.

**Gate:** `diff_db.py` exits 0 with 0 unexplained diffs and 0 missing chips.

### Stage (b): Additive Safety-Field Changes

**What changes vs stage (a) baseline:** Every chip gains `support_status=supported` (new field); 14 non-supported chips gain `unsupported_reason`; 4 NMOS chips have corrected `vpp`/`vpp_mv`; 9 adapter-required chips have corrected `algorithm=0x00`.

**Rule categories for stage (b):** These map cleanly to `RULE_PHASE66` (already in v1.12's `diff_db.py`). Beta's `diff_db.py` lacks `RULE_PHASE66` but has `BUG_A_ETYPE` and `BUG_B_VPP`.

### Implementation Options for D-04 (Claude's Discretion)

**Option A — Two invocations of the same `diff_db.py`:**
1. `FIRESTARTER_BASELINE_FILE=<v1.11-beta-743-chip-db> python tools/diff_db.py` — stage (a)
2. `FIRESTARTER_BASELINE_FILE=tools/baseline/chip_database.baseline.json python tools/diff_db.py` — stage (b) against the pinned GATE-01 anchor

**Option B — Single invocation with combined rule set:**
Update `diff_db.py` to carry BOTH the v1.11 rules (BUG_A_ETYPE, BUG_B_VPP, RULE_ALGO, BUG2_AND_BUG3, SRAM_PINOUT) AND the v1.12 rules (RULE_PHASE66), then diff against the 734-chip pre-v1.11 baseline. All changes since v1.11-pre would appear, categorized.

**Recommendation:** Option A is cleaner for the "near-zero decode regression" proof (stage a). Use v1.11 beta's committed `chip_database.json` (743 chips) as the stage (a) baseline by copying it to a temp path and pointing `FIRESTARTER_BASELINE_FILE` at it. Option A also requires no `--stage` flag in `diff_db.py`.

### Baseline Reconciliation (D-05)

The pinned `chip_database.baseline.json` in `tools/baseline/` currently has 734 chips (the pre-v1.11 Phase 56 anchor). After Phase 70 regeneration, this baseline must be refreshed to 744 chips (the integrated Phase 70 output) so it serves as the new GATE-01 anchor going forward. The old 734-chip baseline becomes historical.

**Action:** After all gates are green and the integrated DB is regenerated, copy `chip_database.json` → `tools/baseline/chip_database.baseline.json` and update the GATE-02 header comment in `diff_db.py`.

---

## Research Question 6: Test / Snapshot / Golden Impact

[VERIFIED: source read of both branches 2026-06-15]

### Files Touched by chip_database.json Content Changes

| File | Impact | Action |
|------|--------|--------|
| `tests/__snapshots__/test_characterization.ambr` | Snapshot of chip_database.json content | Regenerate with `pytest --snapshot-update` |
| `tests/golden/v1.3-COVERAGE-MATRIX.md` | Coverage matrix referencing DB chip counts | Update chip counts (734→744) |
| `tests/chip_database.baseline.json` | OLD location (beta has it here? — NOT FOUND) | No file at this path on beta; baseline is at `tools/baseline/` |
| `tests/test_audit_coverage_matrix.py` | References chip count constants | Update count from 734 to 744 |
| `tests/test_characterization.py` | Uses DB content for characterization tests | May need DB-specific assertions updated |
| `tests/test_decoder.py` | Has decode assertions (was heavily changed between branches) | Verify assertions align with integrated decode |
| `tests/test_eprom_database.py` | DB lookup tests | Verify against regenerated DB |
| `tests/test_eprom_info.py` | Was heavily changed in v1.12 (706 lines diff) | Use v1.12 version (already has support_status display tests) |

### New Test Files to Carry from v1.12

| File | Purpose | Action |
|------|---------|--------|
| `tests/test_build_db_inclusion.py` | 600 lines — DB-01/02/03/05 inclusion behaviors, support_status assertions | CARRY OVER as-is from v1.12 |
| `tests/test_ic_layout.py` | ic_layout pin-field scalar extraction tests (Phase 69) | EXISTS on v1.12 — carry over |
| `tests/test_protocol_not_implemented.py` | ProtocolNotImplementedError pytest | EXISTS on v1.12 — carry over |
| `tests/test_protocol_not_implemented_production_path.py` | Production-path integration test | EXISTS on v1.12 — carry over |

### check_dispatch.py vs Beta's check_dispatch.py

The v1.12 `check_dispatch.py` (359 lines) is a significant expansion of beta's (277 lines):
- Adds `support_status` awareness: non-supported chips are treated as non-dispatchable
- Has D-10 consistency assertions (3 assertions: reason present, PNI genuinely unimplemented, supported→handler)
- Has `non_supported_dispatchable` inverse guard (SC#3)
- Has `PINOUTS_FILE` absent (v1.12 lacks the structural no-vpp-pin guard that beta has)

**Critical gap:** v1.12's `check_dispatch.py` does NOT have the `no_vpp_pin` structural guard (beta's GATE-03 primary guard). Beta's check_dispatch.py has `_build_no_vpp_pin_set` and the `novpp_in_eprom` bucket. The integrated `check_dispatch.py` must include BOTH the v1.12 support_status machinery AND beta's structural no-vpp-pin guard.

**Action:** The integrated check_dispatch.py = v1.12 version + restore beta's `_build_no_vpp_pin_set`, `PINOUTS_FILE` constant, and `novpp_in_eprom` bucket.

### diff_db.py Reconciliation

v1.12's `diff_db.py` removed `BUG_A_ETYPE` and `BUG_B_VPP` rules (replacing with `RULE_PHASE66`). The integrated `diff_db.py` needs:
- Keep v1.12's `RULE_PHASE66` (for support_status/VPP correction diffs)
- Restore beta's `BUG_A_ETYPE` and `BUG_B_VPP` rules (for existing 743-chip reclassification diffs that stage (a) must classify)
- Update the GATE-02 header comment (baseline count: 734→744 after refresh)

### CI Gate Shape (from CLAUDE.md)

```bash
ruff check .
ruff format --check .
mypy (strict on 8 modules: main.py, cli_handlers.py, chip_resolver.py, frame_parser.py, codec.py, address_parser.py, exceptions.py, serial_comm.py)
pytest --cov-fail-under=70
```

**Python version trap:** Devcontainer runs Python 3.12; CI targets 3.9/3.11. Codegen (`catalog/codegen.py`) must be run with Python 3.11 for drift gate compliance. `chip_database.json` regeneration from `build_db.py` is Python-version-agnostic (JSON output is deterministic with sort_keys=True).

**Mypy watermark:** Currently at 29 (bumped from 26 in Phase 69). Must not regress below 29.

**Coverage floor:** 70%. Adding test_build_db_inclusion.py (600 lines) should increase coverage, not decrease it.

---

## Research Question 7: Firmware Lockstep (D-06)

[VERIFIED: source read 2026-06-15]

### Firmware Branch Status

The `firestarter/` sub-repo (firmware) has:
- **v1.12 branch:** 5 commits ahead of beta
- **Beta firmware:** 0 commits ahead of the firmware v1.12 fork point

This means the firmware merge is **clean and conflict-free**. The 5 v1.12 firmware commits are purely additive:

| Commit | Content |
|--------|---------|
| `5b0c053` | Add MSG_ERR_PROTOCOL_NOT_IMPLEMENTED 0xBB catalog constant (WIRE-01) |
| `67a2e9a` | Fix codegen drift — ruff-clean messages.py (Phase 63) |
| `0f2a498` | Failing tests for configure_not_implemented dispatch |
| `30bbe4a` | Add configure_not_implemented handler + fail-closed dispatch arms |
| `b71c6fd` | Update CLAUDE.md Protocol Dispatch table |

### Firmware Merge Verification Steps (D-06)

After `git merge v1.12-protocol-dispatch-hardening` into firmware beta:

1. **Build both envs:** `pio run -e uno` + `pio run -e leonardo`
2. **Flash budget check:** Leonardo must stay ≤ 90% (at v1.12-start: 88.4% → Phase 64 adds ~200B for `not_implemented.cpp`). Verified at Phase 64 shipment.
3. **Native dispatch tests:** `pio test -e native` — `test_not_implemented.cpp` suite (124 lines): tests `protocol=0x99→ERROR+NULL`, `protocol=0→configure_eprom`, `0x11/0x2A/0x2B/0x2C→configure_not_implemented`, `NULL pointers after dispatch`
4. **Wire-constant parity:**

| Constant | Python `messages.py` | C++ `messages.h` | Expected |
|----------|---------------------|------------------|---------|
| `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` | `0xBB` (v1.12) | `0xBB` (v1.12) | Match |
| `MSG_ERR_NOT_SUPPORTED` | `0xA5` (beta) | `0xA5` (beta) | Match |

**Important:** The beta `firestarter_app` currently on `beta` does NOT have `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` in its `messages.py` — that constant only exists on the v1.12 branch. The host runtime merge (which brings in `exceptions.py`, `frame_parser.py`, `cli_handlers.py` with 0xBB support) must happen on the same branch as the DB pipeline re-port. Since D-01 says work on the v1.12 branch, the host runtime is already there.

### Wire-Constant Parity Check Command

```bash
# Python side (v1.12 branch)
grep "MSG_ERR_PROTOCOL_NOT_IMPLEMENTED\|0xBB" firestarter/messages.py

# C++ side (v1.12 firmware branch)
grep "MSG_ERR_PROTOCOL_NOT_IMPLEMENTED\|0xBB" include/messages.h
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Per-chip textual merge of `chip_database.json` | Custom JSON merge script | `python tools/build_db.py` (regenerate) | DB is a build artifact — regeneration is the only valid path |
| New SRAM pinout override hacks | Per-chip `if name == "DS1230":` guards | Beta's `resolve_pinout_key(pm_idx=0, type_int=4, mem_size=...)` | Principled function already handles all 14 SRAM chips |
| New `resolve_pinout_key` for integration | Hybrid guess-table/mask function | Beta's exact function body (transplant) | SC#1: single pinout path; mixing creates dual-path regression risk |
| Separate `--stage` flag in `diff_db.py` | Modify diff_db.py API | Two invocations with different `FIRESTARTER_BASELINE_FILE` env | KISS; env-override already exists for exactly this use case |

---

## Common Pitfalls

### Pitfall 1: Carrying v1.12's `interpret_timing` ×100 Regression

**What goes wrong:** If v1.12's `interpret_timing` is used, W27C512 reports `pulse_duration: "10000 us"` instead of `"100 us"` — violating DEC-03 and SC#2.
**Why it happens:** v1.12 predates the BUG-2 fix and still has the old multiplier.
**How to avoid:** Use beta's `interpret_timing` verbatim. Run `python -c "import build_db; print(build_db.interpret_timing('64', 0x07))"` — expect "100 us" not "10000 us".

### Pitfall 2: Carrying v1.12's `voltages & 0xFF` VPP Mask Regression

**What goes wrong:** SST27VF512 (voltages=0x0001) gets `vpp_mv=0` instead of 12000mV. This is BUG-B.
**Why it happens:** v1.12 uses `voltages & 0xFF` which is 0x01 — not in the lookup table.
**How to avoid:** Use `voltages & 0xF0` from beta. After regen, verify `firestarter info SST27VF512` shows vpp_mv=12000.

### Pitfall 3: Carrying v1.12's Swapped `vcc`/`vdd` Bit Positions

**What goes wrong:** chips report wrong VCC/VDD voltages in `firestarter info`.
**Why it happens:** v1.12 has bits 7-0 as `vdd` and bits 15-12 as `vcc` — the opposite of the minipro source.
**How to avoid:** Use beta's: `vcc = (voltages >> 8) & 0x0F`, `vdd = (voltages >> 12) & 0x0F`.

### Pitfall 4: Forgetting to Pass `type_int` and `mem_size` to `resolve_pinout_key`

**What goes wrong:** All 14 SRAM chips route to `DIP28_2764` or `DIP24_2716` (wrong pinout) → 12V VPP hazard on SRAM WE pin.
**Why it happens:** v1.12's call site is `resolve_pinout_key(pin_count, variant, flags, pm_idx=pm_idx, proto_id=proto_id)` — no `type_int` or `mem_size`. Beta's function requires both.
**How to avoid:** Update the call site in main() to pass `type_int=type_int, mem_size=mem_size`.

### Pitfall 5: check_dispatch.py Missing Structural no-vpp-pin Guard After Integration

**What goes wrong:** v1.12's check_dispatch.py lacks the GATE-03 primary structural guard (`novpp_in_eprom` bucket). If a future chip lands on a no-vpp-pin pinout with a VPP-asserting algorithm, the gate misses it.
**Why it happens:** v1.12 removed `_build_no_vpp_pin_set` and `PINOUTS_FILE`.
**How to avoid:** The integrated check_dispatch.py must restore these from beta.

### Pitfall 6: Site B Gate Ordering vs resolve_pinout_key

**What goes wrong:** If Site B (adapter-required 24-pin EEPROMs) sets `proto_id = NON_DISPATCHABLE_ALGO = 0x00` BEFORE `resolve_pinout_key`, then the pinout call uses proto_id=0x00 — which won't match any Tier 1 `(pin_count, pm_idx, 0x00)` lookup. For 24-pin chips with pm_idx=23, this is fine (Tier 1 has no 0x00 entry for pm_idx=23; the function falls through to variant_lo logic). Verify no Tier 1 or Tier 2 key uses proto_id=0x00.

**How to avoid:** Run `check_dispatch.py` after regen and verify 9 adapter-required chips appear as non-dispatchable.

### Pitfall 7: diff_db.py Rule Set Mismatch

**What goes wrong:** After integration, running `diff_db.py` against the 743-chip v1.11 baseline may produce "UNEXPLAINED" for chips that changed due to `support_status` being added (a new field unknown to v1.11's diff rules).
**Why it happens:** v1.11's diff_db.py only has rules up to `BUG_B_VPP` — the new `support_status` field is outside all rule field-path sets.
**How to avoid:** Use the integrated `diff_db.py` (which has `RULE_PHASE66`) for stage (a) and stage (b) diffs. Or set stage (a) baseline to the v1.11-beta DB and only check decode fields (algorithm, pinout, pulse_duration, vpp, vcc, vdd, type).

### Pitfall 8: Python 3.12 vs 3.11 Codegen Drift

**What goes wrong:** Codegen run with devcontainer Python 3.12 produces `messages.py` with different f-string formatting than Python 3.11 CI target → drift gate fails at CI.
**Why it happens:** Python 3.12 permits backslashes in f-strings; 3.11 does not.
**How to avoid:** Run codegen with `python3.11 tools/catalog/codegen.py` (not `python3`). The v1.12 branch already has a ruff-clean emitter (Phase 63 commit `67a2e9a`).

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `DIP28_VARIANT_MAP` + `PIN_MAP_TO_PINOUT` guess tables | Principled `resolve_pinout_key(pm_idx, type_int, mem_size)` | Phase 58 (v1.11) | Single pinout path; unclassifiable → None → skip |
| Silent WARN-skip for unknown-proto chips | `support_status: protocol-not-implemented` inclusion | Phase 66 (v1.12) | DB becomes complete catalog |
| No VPP ceiling enforcement | `RURP_VPP_CEILING_MV=22000` + vpp-exceeds-max status | Phase 66 (v1.12) | M2716/M2732 correctly refused |
| `configure_memory()` mem_type fallback for unknown protocols | `protocol != 0` → `configure_not_implemented()` | Phase 64 (v1.12 firmware) | Eliminates silent 12V dispatch hazard |
| `voltages & 0xFF` VPP mask | `voltages & 0xF0` | Phase 57 (v1.11) | SST27VF512 and similar show correct 12V |
| `interpret_timing` ×100 for 0x07/0x0B | Raw microseconds for all protocols | Phase 57 (v1.11) | W27C512 shows 100us not 10000us |

**Deprecated/outdated in v1.12 branch (must not carry to integration):**
- `DIP28_VARIANT_MAP`: deleted in v1.11 Phase 58; resurrects in v1.12 — must NOT be in integrated build_db.py
- `PIN_MAP_TO_PINOUT` / `PIN_MAP_PROTO_TO_PINOUT`: same
- `PROTOCOL_MAP` entries for 0x35/0x39/0x3C/0x2A/0x2C/0x2E: removed by v1.11 DEC-05
- `interpret_timing` ×100 multiplier: removed by v1.11 BUG-2 fix

---

## Validation Architecture

### Observable Signals Per Success Criterion

| SC# | Success Criterion | Observable Signal | Sampling Command |
|-----|------------------|-------------------|-----------------|
| SC#1 | `build_db.py` uses v1.11's `resolve_pinout_key` as sole pinout path | No `DIP28_VARIANT_MAP`, `PIN_MAP_TO_PINOUT`, `PIN_MAP_PROTO_TO_PINOUT` in build_db.py | `grep -c "DIP28_VARIANT_MAP\|PIN_MAP_TO_PINOUT" tools/build_db.py` → must be 0 |
| SC#2 | v1.11 decode-correctness preserved | `diff_db.py` stage (a) exits 0; `firestarter info W27C512` shows 100us + 12V VPP | `FIRESTARTER_BASELINE_FILE=/tmp/v1.11-beta-db.json python tools/diff_db.py` |
| SC#3 | GATE-03 green: 0 non-supported chips reach real handler | `check_dispatch.py` exits 0; PASS message includes non_supported_dispatchable=0 | `python tools/check_dispatch.py` |
| SC#4 | `diff_db.py` accounts for every changed chip | `diff_db.py` stage (b) exits 0; 0 UNEXPLAINED | `FIRESTARTER_BASELINE_FILE=tools/baseline/chip_database.baseline.json python tools/diff_db.py` |
| SC#5 | Full test suite + ruff + mypy + coverage green | CI gate green; 744/744 chips scanned in `check_dispatch.py` | `ruff check . && ruff format --check . && pytest --cov-fail-under=70` |
| SC#6 | v1.12 branch merges into beta clean | `git merge` exits 0; no merge conflicts | `git checkout beta && git merge v1.12-protocol-dispatch-hardening` |

### Firmware Validation Signals (D-06)

| Signal | Command | Expected |
|--------|---------|---------|
| Uno build | `pio run -e uno` | Success, < 100% flash |
| Leonardo build | `pio run -e leonardo` | Success, ≤ 90% flash |
| Native dispatch tests | `pio test -e native` | All pass, including test_not_implemented suite |
| Wire-constant parity | `grep 0xBB firestarter/messages.py include/messages.h` | Both show `= 0xBB` |

### Per-Wave Sampling

- **Per task commit:** `ruff check tools/build_db.py && python -c "from tools.build_db import resolve_pinout_key; print('OK')"` (syntax check)
- **Per wave merge:** `python tools/build_db.py` (regenerate DB) + `python tools/check_dispatch.py` + `python tools/diff_db.py`
- **Phase gate:** Full suite green before merge: `ruff check . && ruff format --check . && mypy && pytest --cov-fail-under=70 && python tools/check_dispatch.py`

---

## Package Legitimacy Audit

No new external packages are installed in this phase. All tooling is pre-existing. [VERIFIED: branch diff shows no new dependencies]

| Package | Status | Notes |
|---------|--------|-------|
| `requests` (existing) | OK | Used by build_db.py to fetch infoic.xml — unchanged |
| No new packages | — | Phase is pure code re-port |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | Test run (devcontainer) | Yes | 3.12.x | — |
| Python 3.11 | Codegen drift gate (CI target) | Check with `python3.11 --version` | Unknown | Install via pyenv or use CI |
| `pip install -e '.[test]'` | pytest, mypy, ruff | Must be run if env wiped | — | `pip install -e '.[test]'` |
| PlatformIO (`pio`) | Firmware build/test | Available in devcontainer | Check `pio --version` | — |
| `firestarter/` firmware repo | Firmware merge + build | Available at `/workspaces/firestarter/` | — | — |

**Note on Python 3.11 for codegen:** The Phase 63 fix (`67a2e9a`) already produces ruff-clean messages.py output regardless of Python version. However, if codegen is re-run, use `python3.11` to stay aligned with CI drift gate.

---

## Open Questions

1. **Baseline file for stage (a) diff**
   - What we know: The v1.11 beta `chip_database.json` (743 chips) is the stage (a) baseline per D-05. It is the currently-committed file on the beta branch.
   - What's unclear: Whether diff_db.py can consume it directly without modification (the file lacks `support_status` fields — diff_db.py will see `support_status` appearing as a NEW field in the current vs baseline comparison, which will trigger `UNEXPLAINED` unless the rule set includes it).
   - Recommendation: Copy the v1.11 beta DB to a temp path; update `_classify_diff` to tolerate new top-level fields appearing (add a `RULE_PHASE66` field path for `(support_status,)` with `[ONLY_IN_CURRENT]` semantics), OR use a separate stage (a) script that only diffs decode fields (algorithm, pinout, pulse_duration, vpp_mv, vcc, vdd, electrical.type).

2. **24-pin EEPROM adapter-required chips — pinout resolution after proto_id demoted to 0x00**
   - What we know: Site B sets `proto_id = NON_DISPATCHABLE_ALGO = 0x00` before `resolve_pinout_key` call. For 24-pin chips with `pm_idx=23, variant_lo != 0x10`, beta's function returns `DIP24_2716`.
   - What's unclear: Is `DIP24_2716` the correct pinout to store for adapter-required chips (even if the chip is never dispatched)? v1.12 stored `DIP24_2716` for these and GATE-03 passed (structural: `DIP24_2716` has a `vpp-pin` → no `novpp_in_eprom` hit; host guard in `chip_resolver.py` refuses before wire emission).
   - Recommendation: Accept `DIP24_2716` as the stored pinout for adapter-required 24-pin EEPROMs. The host guard ensures they never reach the wire.

3. **SRAM Vcc normalization in beta — interaction with support_status**
   - What we know: Beta applies `chip_entry["electrical"]["vcc"] = chip_entry["electrical"]["vdd"]` for `_etype == "SRAM"`. This post-construction vcc override should apply to all SRAM chips including any NVRAM/FRAM that might have `support_status != supported`.
   - What's unclear: None of the 14 SRAM chips have non-supported status (they are correctly routed by the principled function). But if future SRAM chips with pm_idx=0 landed as `adapter-required`, the vcc normalization would still apply. This is the correct behavior and poses no risk.
   - Recommendation: No change needed; the normalization applies correctly to all SRAM-type chips.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | No new pip packages are needed for Phase 70 | Standard Stack | Low — tooling is internal Python; no external deps identified in branch diff |
| A2 | Python 3.11 is not available in devcontainer (must be installed or CI-run) | Environment Availability | Medium — codegen drift gate may fail if codegen is re-run with 3.12; mitigation: Phase 63 fix already makes codegen ruff-clean regardless of version |
| A3 | The firmware merge exits 0 with no conflicts (inferred from 0 commits on firmware beta not in v1.12) | Firmware Lockstep | Low — verified via `git log --oneline v1.12-protocol-dispatch-hardening..beta` in firmware repo returning empty |

---

## Sources

### Primary (HIGH confidence — directly read from source)

- `firestarter_app/tools/build_db.py` (beta branch, 589 lines) — read 2026-06-15
- `git show v1.12-protocol-dispatch-hardening:tools/build_db.py` (715 lines) — read 2026-06-15
- `firestarter_app/tools/check_dispatch.py` (beta, 277 lines) — read 2026-06-15
- `git show v1.12-protocol-dispatch-hardening:tools/check_dispatch.py` (359 lines) — read 2026-06-15
- `firestarter_app/tools/diff_db.py` (beta, 486 lines) — read 2026-06-15
- `git diff beta v1.12-protocol-dispatch-hardening -- tools/diff_db.py` — read 2026-06-15
- `.planning/phases/70-v1-11-v1-12-db-pipeline-integration-for-beta-merge/70-CONTEXT.md` — read 2026-06-15
- `.planning/ROADMAP.md` §Phase 70 (lines 877-919) — read 2026-06-15
- `.planning/STATE.md` — read 2026-06-15
- `firestarter_app/CLAUDE.md` — read 2026-06-15
- `git log --oneline beta..v1.12-protocol-dispatch-hardening` (firestarter_app, 34 commits) — run 2026-06-15
- `git log --oneline beta..v1.12-protocol-dispatch-hardening` (firestarter firmware, 5 commits) — run 2026-06-15
- `git merge-base beta v1.12-protocol-dispatch-hardening` → `faaa571` — verified 2026-06-15
- `git diff --stat beta v1.12-protocol-dispatch-hardening` — run 2026-06-15

### Secondary (MEDIUM confidence)

- `.planning/milestones/v1.11-ROADMAP.md` — decode fix requirements DEC-01..05, PIN-01..03, GATE-01..04 — read 2026-06-15

---

## Metadata

**Confidence breakdown:**
- resolve_pinout_key divergence: HIGH — both function bodies read directly
- Per-chip SRAM override analysis: HIGH — all 14 chips enumerated from source; routing logic traced
- v1.12 safety features: HIGH — all 6 features read from source with line references
- v1.11 decode fixes to preserve: HIGH — specific regressions in v1.12 identified with exact code
- Two-stage diff: HIGH — both diff_db.py versions read; rule sets identified
- Test impact: HIGH — git diff --stat enumerated all affected test files
- Firmware lockstep: HIGH — branch commit log read; merge-base identified; 5 additive commits only

**Research date:** 2026-06-15
**Valid until:** 2026-07-15 (stable codebase; all referenced code is committed)

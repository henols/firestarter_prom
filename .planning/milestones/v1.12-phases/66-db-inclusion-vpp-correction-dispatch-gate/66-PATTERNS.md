# Phase 66: DB Inclusion + VPP Correction + Dispatch Gate — Pattern Map

**Mapped:** 2026-06-12
**Files analyzed:** 4 (2 modified source, 1 cherry-pick, 1 regenerated artifact)
**Analogs found:** 4 / 4

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/tools/build_db.py` | data-pipeline transform | batch / transform | existing WARNING-5 arm (L415-423) + fm1608 arm (L446-468) in the same file | exact — same file, same idiom |
| `firestarter_app/tools/check_dispatch.py` | CI gate / utility | batch / transform | existing per-bucket FAIL lists + `not_implemented` arm at L122-124 + FAIL report at L168-176 in the same file | exact — same file, same idiom |
| `firestarter_app/tools/diff_db.py` | CI gate / utility | batch / transform | `git show f3b2ed7:tools/diff_db.py` on `v1.11-infoic-decode-correctness` | cherry-pick — not from-scratch |
| `firestarter_app/tools/baseline/dispatch_baseline.json` + `chip_database.json` | generated artifact | batch | Phase 62 dispatch baseline regen (D-11 precedent) | regeneration pattern |

---

## Pattern Assignments

### `firestarter_app/tools/build_db.py` — three insertion sites

**Analog:** same file, two existing post-decode override blocks

---

#### Site A: Unknown-protocol skip gate → conditional include (DB-01)

Current gate, **`build_db.py` L339-342** (verified live):

```python
# Skip chips with unknown protocol_id
if proto_id not in KNOWN_PROTOCOLS:
    print(f"WARN: skipping {name} — unknown protocol_id 0x{proto_id:02X}", file=sys.stderr)
    continue
```

**Idiom to follow:** Replace the unconditional `continue` with a conditional:
- DIP parallel memory confirmed by per-family re-audit (X88C64P@DIP24, proto `0x34`) → do NOT `continue`; set `_support_status = "protocol-not-implemented"` and let execution fall through to `chip_entry` construction.
- All other unknown-protocol chips (DataFlash `0x04`×18, FWH `0x11`×4, PLCC `0x0A`×1) → keep the `continue` skip with the existing WARN print.

**New KNOWN_PROTOCOLS extension:** add `0x34` to `KNOWN_PROTOCOLS` at L83 so the gate passes X88C64P through; the `_support_status` logic at `chip_entry` construction handles the classification. (RESEARCH confirmed KNOWN_PROTOCOLS at L83: `{0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39}`.)

---

#### Site B: 24-pin EEPROM damage-hazard skip → include as adapter-required (DB-02)

Current gate, **`build_db.py` L359-370** (verified live):

```python
if (pin_count == 24
        and proto_id in (0x07, 0x08, 0x0B)
        and (flags & 0x10)):
    print(
        f"WARN: skipping {mfg_name}/{name} — 24-pin 5V EEPROM with "
        f"EPROM-family algo 0x{proto_id:02X} (damage hazard: 12V VPP "
        f"to socket pin 21 = WE of 28C-family chips). No 24-pin "
        f"EEPROM firmware handler yet; tracked in follow_up "
        f"24pin-eeprom-no-handler.",
        file=sys.stderr,
    )
    continue
```

**Idiom to follow:** Replace the `continue` with a status assignment and fall-through, matching the WARNING-5 pattern (print + mutate + continue-or-fall-through). Print should change from `WARN: skipping` to `INFO: including as adapter-required`. Set `_support_status = "adapter-required"` and `_unsupported_reason` (wording at planner's discretion; must reference the 12V-on-WE hazard). Let execution continue through `resolve_pinout_key` and `chip_entry` construction.

---

#### Site C: NMOS VPP override dict + support_status derivation (DB-03/DB-07)

**Closest analog:** The WARNING-5 inline override block (`build_db.py` L397-423, verified live):

```python
# WARNING-5 safety override: DIP28_2764 chips on the 0x07 path...
if (pinout_key in ("DIP28_2764", "DIP28_28C256")
        and proto_id == 0x07
        and _etype == "Flash/EEPROM"):
    print(
        f"INFO: {mfg_name}/{name} algorithm override 0x07->0x0D "
        f"(WARNING-5: 5V EEPROM with non-EPROM pinout — route through configure_eeprom28c)",
        file=sys.stderr,
    )
    proto_id = 0x0D
```

**And the fm1608 override** (`build_db.py` L446-468, verified live):

```python
if type_int == 4 and proto_id in (0x07, 0x08, 0x0B):
    proto_id = 0x28
    if pin_count == 28:
        if mem_size <= 8192:
            pinout_key = "DIP28_JEDEC_SRAM_8K"
            size_label = "8K"
        else:
            pinout_key = "DIP28_28C256"
            size_label = f"{mem_size//1024}K"
        print(
            f"INFO: {mfg_name}/{name} type=4 SRAM override "
            f"algorithm 0x{proto_id-0x21:02X}->0x28 + pinout->{pinout_key} "
            f"(SRAM/FRAM {size_label}; configure_sram dispatch)",
            file=sys.stderr,
        )
```

**Ordering invariant (HARD):** The new NMOS VPP override block and `_support_status` derivation must be inserted AFTER the fm1608 arm (currently L446-468) and BEFORE `chip_entry` construction (currently L491). The existing code comment documents this ordering contract at L46-56. New blocks must land in this sequence:

```
[existing] L446: fm1608 type_int==4 override
[existing] L481: Re-derive _etype protocol-aware (Pass 2)
[NEW]       NMOS VPP override + _support_status derivation  ← insert here
[existing] L491: chip_entry = { ... }
```

**Module-level constants to add** (above L57, alongside VPP_VOLTAGES/VPP_MV):

```python
# NMOS VPP correction: promotes the comment at L46-56 to applied code.
# Matched against part_number aliases; "highest VPP wins" for entries with
# multiple NMOS aliases (e.g., INTEL/2732,2732A,M2732,M2732A).
NMOS_TRUE_VPP_MV: dict[str, int] = {
    "M2716": 25000,   # Intel NMOS 2716: 25V VPP (datasheet)
    "M2732": 25000,   # Intel NMOS 2732: 25V VPP (datasheet)
    "M2732A": 21000,  # Intel NMOS 2732A: 21V VPP (later variant)
}
# RURP boost regulator theoretical ceiling (build_db.py L55 comment + hw evidence).
# Chips requiring VPP above this cannot be programmed on any RURP revision.
RURP_VPP_CEILING_MV = 22000
```

**Override block to insert before `chip_entry` construction:**

```python
# DB-03: NMOS VPP correction — promote NMOS comment to applied dict.
# Must run AFTER fm1608/WARNING-5 overrides (ordering invariant — see L46-56 comment).
# "highest VPP wins": iterate all aliases; the match with the highest VPP determines
# the final voltage + status (conservative; avoids M2732/M2732A match-order ambiguity).
_nmos_vpp_mv: int | None = None
part_aliases = {a.split("@")[0].strip() for a in name.split(",")}
for nmos_key, nmos_vpp in NMOS_TRUE_VPP_MV.items():
    if nmos_key in part_aliases:
        if _nmos_vpp_mv is None or nmos_vpp > _nmos_vpp_mv:
            _nmos_vpp_mv = nmos_vpp
if _nmos_vpp_mv is not None:
    # Override the upstream-truncated voltage with the true VPP.
    _vpp_override = _nmos_vpp_mv
    _vpp_str_override = f"{_nmos_vpp_mv // 1000}V"
    if _nmos_vpp_mv > RURP_VPP_CEILING_MV:
        _support_status = "vpp-exceeds-max"
        _unsupported_reason = (
            f"VPP {_nmos_vpp_mv // 1000}V exceeds RURP ceiling "
            f"({RURP_VPP_CEILING_MV // 1000}V); cannot program on this hardware"
        )
    # else: leave _support_status as "supported" — M2732A (21V) is within ceiling
```

**`chip_entry` construction extension** (at L491, add `support_status` + conditional `unsupported_reason`):

The current `chip_entry` dict at **`build_db.py` L491-522** (verified live):

```python
chip_entry = {
    "part_number": ",".join(dict.fromkeys(
        a.split("@")[0].strip() for a in name.split(",") if a.split("@")[0].strip()
    )),
    "electrical": {
        "type": _etype,
        "size_bytes": mem_size,
        "pin_count": pin_count,
        "vpp": VPP_VOLTAGES.get(voltages & 0xFF, "Unknown"),
        "vpp_mv": VPP_MV.get(voltages & 0xFF, 0),
        "vdd": VCC_VOLTAGES.get((voltages >> 8) & 0x0F, "5V"),
        "vcc": VCC_VOLTAGES.get((voltages >> 12) & 0x0F, "5V"),
    },
    "programming": {
        "algorithm": proto_id,
        "pulse_duration": interpret_timing(ic.get("pulse_delay"), proto_id),
        "chip_id_check": True if (flags & 0x20) else False,
        "chip_id_value": ic.get("chip_id"),
    },
    "pinout": pinout_key,
}
```

**Add `support_status` as a sibling of `electrical`/`programming`/`pinout` (D-08):**

```python
chip_entry = {
    "part_number": ...,           # unchanged
    "support_status": _support_status,   # D-07/D-08: always present
    "electrical": {
        ...
        # D-03: if _nmos_vpp_mv is not None, override vpp/vpp_mv with true values
        "vpp": _vpp_str_override if _nmos_vpp_mv is not None else VPP_VOLTAGES.get(voltages & 0xFF, "Unknown"),
        "vpp_mv": _nmos_vpp_mv if _nmos_vpp_mv is not None else VPP_MV.get(voltages & 0xFF, 0),
        ...
    },
    "programming": { ... },       # unchanged
    "pinout": pinout_key,
}
if _unsupported_reason:
    chip_entry["unsupported_reason"] = _unsupported_reason  # D-07: only on non-supported
```

**`_support_status` must be initialized before the inclusion gates** (early in the `ic` processing loop, before the unknown-protocol and damage-hazard checks):

```python
_support_status = "supported"   # default; overridden at inclusion gates
_unsupported_reason = None
_nmos_vpp_mv = None
_vpp_str_override = None
```

---

### `firestarter_app/tools/check_dispatch.py` — rework `not_implemented` bucket + add assertions

**Closest analog:** the existing per-bucket FAIL lists and the `not_implemented` arm in the same file.

**Current `not_implemented` arm** (`check_dispatch.py` L122-124, verified live):

```python
if handler == "not_implemented":
    not_implemented.append(f"{mfg}/{part} proto=0x{proto:02X}")
    continue  # skip VPP/wire checks — no real handler to evaluate
```

**Reworked arm (D-10):**

```python
if handler == "not_implemented":
    ss = chip.get("support_status", "supported")
    if ss == "supported":
        # Regression: a supported chip routed to not_implemented is a gate failure.
        not_implemented.append(f"{mfg}/{part} proto=0x{proto:02X} support_status={ss}")
    # else: expected — protocol-not-implemented/adapter-required/vpp-exceeds-max chips
    # correctly route to not_implemented (no handler exists; that is the point).
    continue  # skip VPP/wire checks — no real handler to evaluate
```

**Current FAIL report for `not_implemented`** (`check_dispatch.py` L168-176, verified live):

```python
if not_implemented:
    print(
        f"FAIL: {len(not_implemented)} chips route to not_implemented "
        f"(protocol != 0, not in KNOWN_PROTOCOLS):"
    )
    for e in not_implemented[:20]:
        print(f"  {e}")
    if len(not_implemented) > 20:
        print(f"  ... and {len(not_implemented) - 20} more")
```

The FAIL message text should be updated to match the reworked condition: `"(supported chip with no dispatch handler — protocol regression)"` instead of the old `"(protocol != 0, not in KNOWN_PROTOCOLS)"`.

**Three new consistency assertion lists (D-10)** — add after the main chip loop, before the existing FAIL report block. Mirror the existing FAIL-list idiom exactly (list accumulation → conditional print + truncate → `sys.exit(1)` at the end):

```python
# D-10 Assertion 1: every non-supported chip must have a non-empty unsupported_reason.
missing_reason = []
# D-10 Assertion 2: a protocol-not-implemented chip must have an actually-unimplemented
# protocol (proto not in KNOWN_PROTOCOLS — would be a DB build bug if it had one).
pni_with_known_proto = []
# D-10 Assertion 3: no supported chip resolves to not_implemented
# (already enforced above in the per-chip loop; this post-loop list is the report).
# (not_implemented list serves double duty — it IS assertion 3)

for mfg, chips_list in db_raw.items():
    if not isinstance(chips_list, list):
        continue
    for chip in chips_list:
        ss = chip.get("support_status", "supported")
        part = chip.get("part_number", "<unknown>")
        proto = chip.get("programming", {}).get("algorithm", 0) or 0
        if ss != "supported":
            reason = chip.get("unsupported_reason", "")
            if not reason:
                missing_reason.append(
                    f"{mfg}/{part} support_status={ss} — missing unsupported_reason"
                )
            if ss == "protocol-not-implemented" and proto in KNOWN_PROTOCOLS:
                pni_with_known_proto.append(
                    f"{mfg}/{part} proto=0x{proto:02X} — protocol IS in KNOWN_PROTOCOLS"
                )
```

Add `missing_reason` and `pni_with_known_proto` to the failure-check condition and print them using the same `f"FAIL: {len(...)} ..."` + truncating loop pattern as the existing buckets (L162-200).

**`KNOWN_PROTOCOLS` must be importable in `check_dispatch.py`** for assertion 2. Currently `check_dispatch.py` imports from `firestarter.database`; import `KNOWN_PROTOCOLS` from `tools/build_db.py` or duplicate the set as a local constant (the existing set at `build_db.py:83` is the source of truth).

**Updated PASS message** (currently L203-208): add counts for non-supported chips so the gate is self-documenting:

```python
print(
    f"PASS: all {total} chips scanned; "
    f"{supported_count} supported; "
    f"{len(non_supported_list)} non-supported (non-dispatchable, expected); "
    f"0 dispatch regressions; 0 consistency violations"
)
```

---

### `firestarter_app/tools/diff_db.py` — cherry-pick from v1.11

**This file does NOT exist on the current `v1.12-protocol-dispatch-hardening` branch.**

**Source:** `git show f3b2ed7:tools/diff_db.py` on `v1.11-infoic-decode-correctness`. The v1.11 commit that created it was `fc62a27` (initial) followed by `f3b2ed7` (finalized).

**Action:** Cherry-pick the file. Do NOT rewrite from scratch — the per-chip composite-key indexing, rationale-rule classifier, exit code semantics, and RULE_ALGO block are all reusable.

**After cherry-pick, add a new `RULE_PHASE66` entry to `_RATIONALES`** (mirrors the existing `RULE_ALGO` block at the top of `_RATIONALES`):

```python
"RULE_PHASE66": (
    "Phase 66 DB inclusion + VPP correction changes.\n"
    "  DB-01: New chips with support_status=protocol-not-implemented included "
    "    (previously silently skipped). New top-level key: support_status + unsupported_reason.\n"
    "  DB-02: 9 damage-hazard 24-pin EEPROMs included as support_status=adapter-required "
    "    (previously silently skipped; DIP24 form only).\n"
    "  DB-03: NMOS high-VPP entries corrected: M2716/M2732=25V (vpp-exceeds-max), "
    "    M2732A=21V (supported at corrected voltage). vpp/vpp_mv fields updated.\n"
    "  DB-05: All chips gain explicit support_status=supported (majority, mechanical change).\n"
    "  [VERIFIED: .planning/phases/66-db-inclusion-vpp-correction-dispatch-gate/66-CONTEXT.md D-04/D-06/D-07]"
),
```

**`chip_database.baseline.json` for diff gate:** Set baseline = current 734-chip `chip_database.json` (pre-Phase-66 state) and commit as `tools/baseline/chip_database.baseline.json`. This file also does not exist on v1.12 and is the companion artifact to `diff_db.py`.

---

### `firestarter_app/tools/baseline/dispatch_baseline.json` + `chip_database.json` — regenerated artifacts

**Pattern:** Never hand-edit. Regeneration commands (from `firestarter_app/` root):

```bash
# Regenerate chip_database.json (run against CI-target Python, not devcontainer 3.12):
python tools/build_db.py

# Capture updated dispatch baseline (after DB regen):
python tools/check_dispatch.py   # verify exits 0 first
# Then update tools/baseline/dispatch_baseline.json by running the capture script
# (check Phase 62 plan for the exact capture command — it runs check_dispatch.py
# in capture mode or snapshots the output).
```

**Authorized-deviation precedent (D-11):** The Phase 62 dispatch baseline was captured at 734 chips. After Phase 66, the new DB has ~744 chips (734 + 1 from `0x34` + 9 adapter-required). The new `dispatch_baseline.json` must be regenerated and committed as a reviewed deviation, with the diff documented in the commit message (listing each new chip + its handler).

**Python version note (Pitfall 6):** `chip_database.json` generation is version-neutral. `check_dispatch.py` and `diff_db.py` import `firestarter.database` — run those under Python 3.11 (CI target) to avoid the 3.12-masks-3.11 drift trap documented in `.planning/` memory.

---

## Shared Patterns

### Inline post-decode override idiom
**Source:** `build_db.py` L415-423 (WARNING-5) and L446-468 (fm1608)
**Apply to:** All three new `build_db.py` insertion sites (Sites A, B, C above)

The invariant: any override that changes `proto_id`, `pinout_key`, `_etype`, or now `vpp_mv`/`_support_status` must be:
1. A guarded conditional block (`if <discriminator>:`)
2. Accompanied by an `INFO:` or `WARN:` print to stderr naming `{mfg_name}/{name}` and the override applied
3. Placed in the documented ordering sequence (after FLAGS-BASED _etype, after WARNING-5, after fm1608, before `chip_entry` construction)

### Per-bucket FAIL list idiom
**Source:** `check_dispatch.py` L104-200 (verified live)
**Apply to:** New consistency assertion lists in `check_dispatch.py`

The invariant:
1. Initialize an empty list before the scan loop: `missing_reason = []`
2. Append `f"{mfg}/{part} ..."` format strings during the loop
3. After the loop, check `if missing_reason:` and print `f"FAIL: {len(missing_reason)} ..."` + truncating `for e in missing_reason[:20]:` loop
4. Include the list in the master `if errors or not_implemented or ...` condition that gates `sys.exit(1)`

### `f"{mfg}/{part} proto=0x{proto:02X} ..."` message format
**Source:** `check_dispatch.py` L120, L127, L138 (verified live)
**Apply to:** All new FAIL messages and `unsupported_reason` values

All gate FAIL entries and `unsupported_reason` wording in `chip_entry` should name the mfg/part clearly. For FAIL messages, the `f"{mfg}/{part} proto=0x{proto:02X} support_status={ss}"` extension is the natural addition.

---

## No Analog Found

No files in this phase lack an analog.

| File | Note |
|------|------|
| `diff_db.py` | Exists on v1.11; cherry-pick target, not a new file |
| `chip_database.baseline.json` | Companion to `diff_db.py`; initialize from current 734-chip DB |

---

## Metadata

**Analog search scope:** `firestarter_app/tools/` (build_db.py, check_dispatch.py); `git show f3b2ed7:tools/diff_db.py` (v1.11 branch)
**Files scanned:** 3 live source files + 1 historical via git show
**Line numbers verified against:** live `build_db.py` and `check_dispatch.py` on `v1.12-protocol-dispatch-hardening` HEAD, 2026-06-12
**Pattern extraction date:** 2026-06-12

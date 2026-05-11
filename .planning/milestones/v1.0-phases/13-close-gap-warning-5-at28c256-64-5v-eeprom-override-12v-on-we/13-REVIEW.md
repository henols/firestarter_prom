---
phase: 13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we
reviewed: 2026-05-11T19:49:58Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - firestarter_app/tools/check_dispatch.py
  - firestarter_app/tools/build_db.py
  - firestarter_app/firestarter/data/minipro_complete_db.json
  - firestarter_app/CLAUDE.md
findings:
  critical: 0
  warning: 2
  info: 4
  total: 6
status: issues_found
---

# Phase 13: Code Review Report

**Reviewed:** 2026-05-11T19:49:58Z
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Phase 13 adds a `build_db.py` override that flips `proto_id` from `0x07` (EPROM_STD) to `0x0D` (EEPROM_POLL) for chips matching `(pinout="DIP28_2764", proto_id=0x07, _etype="Flash/EEPROM")`, plus a matching `check_dispatch.py` regression guard and a `firestarter_app/CLAUDE.md` paragraph. Functional verification confirms the override fires for exactly 23 chips (matching the claim) across ATMEL, MICROCHIP, NEC, XICOR, ST, and EXEL manufacturers, and `check_dispatch.py` exits 0 after regeneration.

Two correctness/robustness concerns surfaced during review:

1. The regression guard and the override use **identical** triggering predicates. They do not form independent layers of defense — if upstream `minipro` ever ships an AT28C-family chip with `flags & 0x10 == 0` (so `_etype` resolves to `UV-EPROM` rather than `Flash/EEPROM`), BOTH the override and the guard will silently miss it, the chip will reach `configure_eprom`, and 12V P1_VPP_ENABLE will be applied to A14. The "regression guard" therefore only guarantees the override fired when it triggered, not that all hazardous chips were caught. (WR-01)
2. The override flips `programming.algorithm` to `0x0D` but leaves `electrical.vpp = "12V"` and `electrical.vpp_mv = 12000` on the affected chips. The Python host sends `vpp_mv` to the firmware in the JSON command (`database.py:510-518`), so a chip routed to `configure_eeprom28c` will still carry a 12V claim downstream — internally inconsistent with the override comment which states "no VPP regulator engagement." If a future firmware change makes any 0x0D codepath consult `vpp_mv`, this becomes a live hazard. (WR-02)

Plus a few INFO items around inconsistency between `check_dispatch.py` (uses a named constant) and `build_db.py` (uses inline literal), one undocumented side-effect of the override on `interpret_timing`, two pre-existing bare `except:` clauses that were touched-but-not-fixed in adjacent code, and the JSON DB regenerates cleanly with no collateral drift (sanity confirmed).

The Critical-tier hazard the phase set out to close (BLOCKER on hardware safety) is closed for the specific scope defined; the WR-01 gap is a defense-in-depth issue, not a regression.

## Warnings

### WR-01: Override and regression guard share identical predicates — no independent defense layer

**File:** `firestarter_app/tools/build_db.py:239-247`, `firestarter_app/tools/check_dispatch.py:114-121`

**Issue:** The override in `build_db.py` triggers on:
```
pinout_key == "DIP28_2764" AND proto_id == 0x07 AND _etype == "Flash/EEPROM"
```
The regression guard in `check_dispatch.py` triggers on:
```
pinout == "DIP28_2764" AND etype == "Flash/EEPROM" AND handler == "configure_eprom"
```
Both predicates depend on `_etype == "Flash/EEPROM"`. `_etype` is derived from `flags & 0x10` at `build_db.py:216`. If upstream `minipro` flips the `0x10` bit OFF for a future AT28C-family entry (firmware-marked as UV-EPROM despite being 5V-only EEPROM), the override will not fire AND the guard will not catch it — yet the chip will reach `configure_eprom` and apply 12V to A14.

The phase CONTEXT explicitly identified the discriminator as **"manufacturer + chip name family prefix"** (line 32 of 13-CONTEXT.md), but the implementation does not use chip name as a signal in either place. The guard is therefore only "did the override fire when it tripped its own three predicates" — not "is there any chip with the AT28C-family identity that ended up dispatched to configure_eprom."

**Fix:** Make the guard use an independent signal — a name/manufacturer allowlist or a positive cross-check (e.g., "every chip whose part_number matches `^(AT28[CBV]|28C|28LV|UPD28C|X28C|XLS2865|M28256)` AND pinout=DIP28_2764 routes to configure_eeprom28c"). Concretely:
```python
# In check_dispatch.py, add a name-based positive assertion alongside the
# pinout+etype guard so the two are independent.
_AT28C_FAMILY_RE = re.compile(
    r"^(AT28[CBV]|28C\d|28LV|UPD28C|X28C|XLS2865|M28256)",
    re.IGNORECASE,
)
# ...
if (_AT28C_FAMILY_RE.match(part) and pinout == "DIP28_2764"
        and handler != "configure_eeprom28c"):
    eeprom28c_in_eprom.append(f"{mfg}/{part} family-regex hit, handler={handler}")
```
This ensures that if upstream `minipro` flips `flags & 0x10` for an AT28C variant, the guard still catches it.

### WR-02: Override leaves `vpp` / `vpp_mv` at 12V on chips routed to a 5V-only handler

**File:** `firestarter_app/tools/build_db.py:239-269`

**Issue:** The override mutates `proto_id` to `0x0D` but does not touch the `electrical.vpp` / `electrical.vpp_mv` fields, which still come from `VPP_VOLTAGES.get(voltages & 0xFF)` / `VPP_MV.get(voltages & 0xFF)` derived from the original (now-stale) minipro programming envelope. Inspection of the regenerated DB confirms 18 of the 23 overridden chips end up with `vpp="12V"`, `vpp_mv=12000` (e.g. `ATMEL/AT28C256`, `MICROCHIP memory/28C256F`, `XICOR/X28C64`). The remaining 5 have `vpp="Unknown"` only because the minipro `voltages` byte did not map to any known VPP code.

`firestarter_app/firestarter/database.py:510` passes this `vpp_mv` to the firmware in the JSON command (`"vpp_mv": vpp_mv`). The override comment at `build_db.py:227-229` claims "no VPP regulator" — but the data still carries a 12V VPP claim. The override's reasoning ("Leave _etype = 'Flash/EEPROM' unchanged — database.py's info_flags derivation depends on that string for the 'electrically erasable' bit") explains why `electrical.type` is left alone, but does not explain why `vpp`/`vpp_mv` are left at 12V. Today this happens to be safe because `configure_eeprom28c` (firmware) does not consult `vpp_mv`; if a future firmware change adds a VPP-sanity-check path on the 0x0D codepath (e.g., the REQ-SAF-01 ADC pre-pulse check), this becomes a hazard because the firmware will trust the 12V claim from the host.

**Fix:** Override `vpp_mv` to `0` (and `vpp` to `"0V"` or `"N/A"`) when the algorithm-override fires, since `configure_eeprom28c` operates on 5V VCC only:
```python
if (pinout_key == "DIP28_2764"
        and proto_id == 0x07
        and _etype == "Flash/EEPROM"):
    print(
        f"INFO: {mfg_name}/{name} algorithm override 0x07->0x0D "
        f"(WARNING-5: 5V EEPROM mistagged as UV-EPROM, DIP28_2764 pin 1 = A14)",
        file=sys.stderr,
    )
    proto_id = 0x0D
    # WARNING-5: 0x0D path is 5V VCC only — clear stale 12V VPP claim
    # so downstream code/firmware cannot mis-arm the regulator.
    voltages = voltages & ~0xFF  # forces vpp lookup to "12V" 0x00... use sentinel instead
    # Or, simpler: assign post-construction:
    _override_vpp = True
```
Either pre-clear `voltages` before the dict construction, or assign zero post-construction. Update the override comment to document the field is now consistent.

## Info

### IN-01: Inconsistency — `check_dispatch.py` uses a named constant, `build_db.py` uses inline literal

**File:** `firestarter_app/tools/check_dispatch.py:62`, `firestarter_app/tools/build_db.py:239`

**Issue:** `check_dispatch.py` defines `_28C_EEPROM_HAZARD_PINOUT = "DIP28_2764"` at module top and uses the constant in the predicate. `build_db.py` inlines `"DIP28_2764"` directly in the override predicate (line 239). The override's comment justifies this with "Inline literal — no module-top constant — matches the Phase 12 Plan 04 SRAM-detection precedent above" but the two sources now drift if anyone ever renames `DIP28_2764` in `pinouts.json`. (Phase 13 CONTEXT D6 even calls out "pattern should mirror the existing `DIP28_VARIANT_MAP` / `VPP_MV` / `KNOWN_PROTOCOLS` table idioms at module top" — explicitly the opposite choice.)

**Fix:** Promote the literal to a module-top constant in `build_db.py` (e.g., `_AT28C_HAZARD_PINOUT = "DIP28_2764"`) and reference it in the override conditional. Bonus: a single grep target makes the relationship between the override and the guard visible.

### IN-02: Override has undocumented side-effect on `programming.pulse_duration`

**File:** `firestarter_app/tools/build_db.py:247, 262-264`

**Issue:** The override reassigns `proto_id = 0x0D` BEFORE `chip_entry` is built. `interpret_timing(ic.get("pulse_delay"), proto_id)` (line 262-264) then receives the OVERRIDDEN proto_id, so chips that would have returned `f"{val * 100} us"` (under the 0x07 branch at `interpret_timing:147-148`) now fall through to `"Algorithm Controlled"`. This is arguably correct behavior (0x0D IS algorithm-controlled, not pulse-duration controlled) — but the override comment block documents only the `algorithm` flip, not the `pulse_duration` side effect. A future reader hunting "why did pulse_duration change for AT28C256?" will not find the answer in the override comment.

**Fix:** Add one line to the override comment block: `# Side effect: pulse_duration becomes "Algorithm Controlled" because interpret_timing reads the now-overridden proto_id (0x0D). This is correct — 0x0D is algorithm-controlled, not pulse-duration controlled.`

### IN-03: Pre-existing bare `except:` clauses in build_db.py

**File:** `firestarter_app/tools/build_db.py:140, 185`

**Issue:** Two bare `except:` clauses swallow ALL exceptions including `KeyboardInterrupt` and `SystemExit`. Pre-existing (NOT introduced by this phase), but `build_db.py` was the primary change target and these became visible during review. The line-185 clause swallows the entire chip-parsing block — if `ic.get("package_details")` returns `None` (malformed XML), the chip is silently skipped with zero diagnostic. The line-140 clause masks `int(raw_hex, 16)` parse failures in `interpret_timing` and silently returns `val=0`.

**Fix:** Tighten to specific exception types:
```python
# Line 140
except (TypeError, ValueError):
    val = 0

# Line 185
except (TypeError, ValueError, AttributeError):
    continue
```
Add a warning log to the line-185 path so silently-dropped chips show up in build output.

### IN-04: JSON artifact sanity check — confirmed no collateral drift

**File:** `firestarter_app/firestarter/data/minipro_complete_db.json`

**Issue:** This is a generated artifact, not source. Sanity check shows:
- Total chips: 743 (no change vs claim)
- `DIP28_2764 + Flash/EEPROM` chips: 25 total → 23 at `algorithm=0x0D` (overridden, correct), 2 at `algorithm=0x05` (AT29C256, AT29LV256 — NOT overridden, dispatch to `configure_flash4` which is out-of-scope per phase boundaries)
- Algorithm distribution: 41 chips at `0x0D` total (was 18 pre-phase per inferred delta of 23) — internally consistent
- Spot-check confirmed every chip in the override-affected list (`ATMEL/AT28C256`, `MICROCHIP memory/28C256`, `NEC/UPD28C256`, `XICOR/X28C64`, `ST/M28256`, `EXEL/XLS2865A`) shows `algorithm: 13` in the regenerated DB

No defect — recording the sanity result so future reviewers can verify scope drift if regenerated.

---

_Reviewed: 2026-05-11T19:49:58Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

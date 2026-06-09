---
slug: infoic-decode-eeprom-misclass
status: resolved
trigger: |
  DATA_START
  there are sveral issues with that the data in the infoic.xml isent decoded correctly.
  For example SST27VF512 and W27C512 are detected as uv-eproms  and not eeproms.
  the SST27VF512 dont have a vpp of 12v as it must have, you must find and consult the
  datasheets for the roms so the data of the infoic.xml can be correctly decoded there
  are several fields that is important like flags, algorithm and several more that must
  be investigated to understand what they meen in reality, so the firestarter can
  understand how to configure the programming, erasing and all other operations.
  This is a verry tidius work but it must be done!
  DATA_END
created: 2026-06-09
updated: 2026-06-09
related_todo: w27c512-eeprom-misclassification (pending, operator-escalated 2026-05-21)
related_milestone: v1.11 (just executed phases 56-59 — decode-correctness; this is a NEW class of decode gap surfacing post-execution)
---

# infoic.xml decode incorrect — EEPROM/Flash chips misclassified as UV-EPROM; VPP decode inconsistent

## Symptoms (operator report + reproduced)

**Expected:** `W27C512` and `SST27VF512` (and the wider 27Cxxx CMOS-EEPROM / SST SuperFlash
family) should decode as electrically-erasable EEPROM/Flash, not UV-EPROM, so firestarter
configures program/erase/blank correctly. `SST27VF512` should carry a 12 V VPP, not 0/Unknown.

**Actual (reproduced 2026-06-09 against current chip_database.json, 743 chips):**

| part_number              | electrical.type | vpp_mv      | algorithm | pinout         |
|--------------------------|-----------------|-------------|-----------|----------------|
| `W27C512,W27E512`        | UV-EPROM        | 12000       | 7 (0x07)  | DIP28_27512    |
| `SST27VF512`             | UV-EPROM        | **0/Unknown** | 7 (0x07)  | DIP28_27512    |
| `SST27SF512`             | UV-EPROM        | 12000       | 7 (0x07)  | DIP28_27512    |
| `W27C257`                | UV-EPROM        | 12000       | 7 (0x07)  | DIP28_27256    |

Both operator claims reproduce: misclassified as UV-EPROM, and SST27VF512 VPP missing.
Prior bench evidence (todo w27c512-eeprom-misclassification, 2026-05-21): `firestarter erase
W27C512` → `ERROR: Not supported` (routed to UV-only path); `id`/`read` work fine.

**Reproduction:** `firestarter info <chip>` / inspect `firestarter_app/firestarter/data/chip_database.json`.

**Timeline:** Pre-existing; operator escalated W27C512 on 2026-05-21. v1.11 (phases 56-59,
just executed) fixed several decode bugs (timing ×100, VCC nibbles, vcc/vdd swap, PROTOCOL_MAP,
24-pin EEPROM unblock) but did NOT address EEPROM-vs-UV type classification or this VPP case.

## Evidence (raw upstream infoic.xml, fetched 2026-06-09 from MINIPRO_XML_URL master)

NOTE: there is NO vendored/pinned infoic.xml in the repo — `build_db.py` fetches it LIVE from
`https://gitlab.com/DavidGriffith/minipro/-/raw/master/infoic.xml` (the v1.11 "pinned snapshot"
was never vendored; this is also code-review finding WR-05 in 59-REVIEW.md). A working copy is
at `/tmp/infoic.xml` (17.8 MB) for this session; re-fetch if absent.

Raw `<ic>` attributes (DIP28 variants):

```
SST27VF512@DIP28:  type=1 protocol_id=0x07 variant=0x3110 chip_id=0x0000bfa8
                   voltages=0x0001  pulse_delay=0x0032  flags=0x00000078  pin_map=0x0000c916
SST27SF512@DIP28:  type=1 protocol_id=0x07 variant=0x3110 chip_id=0x0000bfa4
                   voltages=0x0000  pulse_delay=0x0032  flags=0x00000078  pin_map=0x0000c916
W27C512,W27E512:   type=1 protocol_id=0x07 variant=0x3110 chip_id=0x0000da08
                   voltages=0x0000  pulse_delay=0x0064  flags=0x00000078  pin_map=0x00000c16
W27C257@DIP28:     type=1 protocol_id=0x07 variant=0x3211 chip_id=0x0000da02
                   voltages=0x0000  pulse_delay=0x0064  flags=0x00000078  pin_map=0x00000c16
```

### Initial leads (to confirm/refute, NOT yet root cause)

1. **VPP decode looks inverted.** SST27VF512 has `voltages=0x0001` (nonzero) yet decoded to
   `vpp_mv=0/Unknown`; the three with `voltages=0x0000` decoded to `vpp_mv=12000`. The
   `build_db.py` voltages→VPP mapping appears to mishandle the field (possibly treating the VPP
   nibble as an index/lookup where 0x0000 falls back to a 12 V default and 0x0001 maps to an
   unmapped/Unknown slot). Decode the `voltages` u16 against minipro `database.c` semantics.
2. **Type/erasability driven solely off `protocol_id=0x07 → UV-EPROM`.** `flags=0x00000078`,
   `chip_id`, and the chip family are not consulted to distinguish electrically-erasable parts
   (W27C* CMOS EEPROM, SST27SF/VF SuperFlash) from genuine UV-EPROMs. Decode what `flags`,
   `type`, and `protocol_id` mean in minipro's own source — protocol_id is the PROGRAMMING
   algorithm, which is NOT the same axis as UV-vs-electrically-erasable.
3. **The 0x07 → 12 V VPP path is load-bearing and safety-relevant.** Per firestarter_app/CLAUDE.md
   the 0x07 path genuinely needs 12 V on pin 1 for SOME of these. Any reclassification MUST pass
   the GATE-03 VPP-safety guard (check_dispatch.py) and the SR-1 checklist — do not strip 12 V
   from a part that needs it, and do not route a 5 V-only part through a 12 V-asserting handler.

## Investigation tasks (operator-specified — datasheet-grounded)

- Consult authoritative sources for each named chip: the **minipro `database.c` / infoic schema**
  (what every `<ic>` attribute means: `type`, `protocol_id`, `variant`, `voltages`, `pulse_delay`,
  `flags`, `pin_map`, `package_details`) AND the **device datasheets** (W27C512/W27E512, SST27VF512,
  SST27SF512, W27C257 — real VPP, erase mechanism, program voltage/algorithm).
- Establish the correct mapping from infoic.xml fields → firestarter electrical.type / algorithm /
  vpp_mv / erase capability, so program/erase/blank/verify configure correctly.
- Determine the full set of currently-misclassified chips (not just the 4 named) and whether a
  systematic re-derivation is warranted vs. targeted overrides.

## Constraints / boundaries

- HOST-ONLY by default (v1.11 boundary): fix lands in `firestarter_app/tools/build_db.py` (decode)
  + regenerated `chip_database.json`. Firmware (`firestarter/`) stays UNTOUCHED unless a genuine
  safety/operation gap is found that requires a handler change — then escalate as a firmware
  backlog item (do not silently change firmware).
- Any reclassification must keep GATE-03 (`check_dispatch.py`) at 0 violations and respect the
  SR-1 VPP-safety checklist. Re-run the GATE-02 diff (`tools/diff_db.py`) after any DB regen.
- This is firestarter_app submodule work → commits go INSIDE `firestarter_app` (branch
  v1.11-infoic-decode-correctness); the meta-repo firestarter_app gitlink stays pinned at the
  v1.10 tip `faaa571` (reconciled once at beta cut — do NOT bump it per fix).

## Environment

- node NOT on PATH: `NODE=$(ls /vscode/vscode-server/bin/linux-x64/*/node | head -1); export PATH="$(dirname $NODE):$PATH"`. SDK: `node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" <cmd>` (subcommands direct, NO `query` prefix).
- Python: `/usr/local` python3; run tools from inside the submodule (`cd firestarter_app && python3 tools/build_db.py` / `tools/diff_db.py` / `tools/check_dispatch.py`). Ignore `firestarter_app/.venv`.
- Network IS available (curl/requests reach gitlab) for re-fetching infoic.xml and datasheets.

## Current Focus

hypothesis: CONFIRMED. Three bugs found and fixed.
test: traced build_db.py decode path for all 4 named chips against minipro database.c + infoic.xml survey.
expecting: n/a — fixes applied and verified.
next_action: committed to firestarter_app submodule.

## Evidence Log

- timestamp: 2026-06-09 — reproduced misclassification + VPP gap against current DB (table above); extracted raw infoic.xml `<ic>` attributes for the 4 named chips (block above). Confirmed no vendored infoic.xml (live fetch).
- timestamp: 2026-06-09 — root cause analysis complete. Three bugs identified in build_db.py decode logic. See Resolution section.
- timestamp: 2026-06-09 — fixes applied to build_db.py; DB regenerated (743 chips); GATE-02 PASS (501 changes explained); GATE-03 PASS (0 violations); 516/516 tests pass.

## Eliminated

- Hypothesis that protocol_id=0x07 mapping was the sole cause: INCORRECT. The algorithm mapping IS correct (0x07=configure_eprom), but the electrical.type field needed to also consult flags bit 0x10.
- Hypothesis that infoic.xml voltages=0x0001 for SST27VF512 is an upstream data error: INCORRECT. It is a valid encoding where bits 3-0 carry programmer-option flags; bits 7-4 carry the VPP index (0x00 = 12V). The current code incorrectly used the full low byte as the VPP lookup key.

## Resolution

root_cause: |
  Three decode bugs in `firestarter_app/tools/build_db.py`:

  BUG A — electrical.type incorrect for CMOS-EEPROM family (W27C512, SST27SF512, SST27VF512, W27C257, etc.):
  Pass 2 unconditionally mapped proto=0x07 → "UV-EPROM", ignoring flags bit 0x10 (electrically erasable).
  These chips have flags & 0x10 = True (confirmed by infoic.xml survey: all DIP28_27512/27256 chips with
  this flag are CMOS EEPROMs; genuine UV-EPROMs have flags & 0x10 = False). Algorithm stays 0x07 (correct —
  these chips DO need 12V VPP via configure_eprom); only the type label was wrong.

  BUG B — VPP decode uses wrong mask (voltages & 0xFF instead of voltages & 0xF0):
  The voltages low byte layout: bits 7-4 = VPP index, bits 3-0 = option flags (powerdown-enable, T48 options).
  All valid TL866II VPP codes are multiples of 0x10 (0x00=12V, 0x10=9V, etc.). When bits 3-0 are nonzero
  (SST27VF512 voltages=0x0001, many AT49BV/SST29VF/flash chips), the full-byte key is not in the table → 0mV.
  Fix: mask with 0xF0. SST27VF512 now correctly shows vpp=12V. ~126 chips affected total.

  BUG C — Rule 2 (WARNING-5) missing coverage for DIP28_28C64 pinout (pm_idx=18/19):
  The entire AT28C64/AM28C64/M28C64/28C17 family (35 chips) on DIP28_28C64 pinout has no VPP pin (pin 1 = NC).
  Rule 2 covered DIP28_28C256 and DIP28_2764 but not DIP28_28C64. These chips stayed at algo=0x07 (UV-EPROM path)
  instead of being flipped to algo=0x0D (configure_eeprom28c, 5V-only, safe). The HAZARD tracked in the
  audit_coverage_matrix §4 is now RESOLVED.

fix: |
  build_db.py:
  1. Pass 2 (Step 7): for proto_id in {0x07, 0x08, 0x0B}, check flags & 0x10 to distinguish
     EEPROM (True) from UV-EPROM (False). Previously blindly assigned "UV-EPROM" to all 0x07 chips.
  2. chip_entry.electrical.vpp: change `voltages & 0xFF` → `voltages & 0xF0` for both vpp and vpp_mv lookups.
  3. Rule 2 (Step 5): add third condition `pinout_key == "DIP28_28C64" and proto_id == 0x07`
     unconditionally flips to algo=0x0D (no flags check needed — ALL 28C64 chips are 5V EEPROMs).

  diff_db.py: added BUG_A_ETYPE and BUG_B_VPP rationale rules to cover the new field changes.
  tests/test_audit_coverage_matrix.py: updated row counts (332→297, 205→170), replaced
  test_hazard_cluster_42_rows with test_hazard_cluster_resolved (hazard is fixed), updated
  test_ledger_id_reuse to use CORRECTNESS finding (no HAZARD findings remain), updated
  test_summary_stats counts, regenerated golden file.
  .planning/v1.3-COVERAGE-MATRIX.md + tests/golden/v1.3-COVERAGE-MATRIX.md: regenerated.

  GATE-03: 0 violations (all 743 chips have valid dispatch path).
  GATE-02: 501 changes explained (9 new chips; 0 missing).
  Tests: 516/516 pass.

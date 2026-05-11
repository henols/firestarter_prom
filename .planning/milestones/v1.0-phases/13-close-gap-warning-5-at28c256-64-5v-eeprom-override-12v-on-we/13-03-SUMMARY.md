---
phase: 13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we
plan: 03
subsystem: documentation
tags: [documentation, database-pipeline, eeprom, warning-5, 28c, claude-md]

# Dependency graph
requires:
  - phase: 13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we
    plan: 01
    provides: "_28C_EEPROM_HAZARD_PINOUT regression guard (the third trace this paragraph references in `tools/check_dispatch.py`)"
  - phase: 13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we
    plan: 02
    provides: "Inline 3-predicate override in build_db.py (the source-level fix this paragraph documents)"
provides:
  - "Documentation plane of WARNING-5 closure: prose explanation in firestarter_app/CLAUDE.md Database Pipeline section, cross-referencing both the source override and the regression guard"
  - "Independent maintainer-facing trace of the override condition (DIP28_2764 + 0x07 + Flash/EEPROM → 0x0D) and its rationale (A14-on-pin-1 hazard)"
affects: []  # final plan of phase 13; no downstream plans

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Dense documentation paragraph in CLAUDE.md keyed to a source-level WARNING-N audit entry — single-paragraph format, matches the 'Known protocols' line preceding it"

key-files:
  created: []
  modified:
    - "firestarter_app/CLAUDE.md"

key-decisions:
  - "Single paragraph (not a new subsection) below the existing 'Known protocols' line — matches the locked structure from the plan's <interfaces> note (keep section depth flat)"
  - "Label prefix 'Protocol overrides (WARNING-5):' makes the entry greppable by both audit ID and topic"
  - "Reference 6 manufacturers (matching Plan 02's actual fired count) rather than 7 (Plan 01's pinout-detection count) — Plan 02 fired the override on 6 families because all 23 chips ended up sharing the 3-predicate signature regardless of how many manufacturers Plan 01 detected (6 vs 7 is a counting nuance, not a coverage gap)"
  - "Submodule pattern preserved: source change committed inside firestarter_app, then pointer-bump in outer repo (mirrors Plans 13-01 and 13-02)"

patterns-established:
  - "WARNING-N paragraphs in firestarter_app/CLAUDE.md sit in the relevant architectural section (Database Pipeline here), use a 'Term (WARNING-N):' label, and reference (a) the audit entry, (b) the source location of the fix, and (c) the regression guard that proves the fix"

requirements-completed: []  # No new requirements closed by this plan. REQ-FW-03 and REQ-SAF-01 were closed in Plan 02 when the override fired.

# Metrics
duration: ~1 min
completed: 2026-05-11
---

# Phase 13 Plan 03: WARNING-5 Documentation Summary

**Added a 20-line "Protocol overrides (WARNING-5)" paragraph to `firestarter_app/CLAUDE.md` Database Pipeline section, documenting the inline `build_db.py` override (DIP28_2764 + 0x07 + Flash/EEPROM → 0x0D), the A14-on-pin-1 hazard rationale, the ~23-chip / 6-manufacturer scope, the 7-chip regression-safe set, and the `check_dispatch.py` guard. Closes the documentation plane of WARNING-5.**

## Performance

- **Duration:** ~1 min
- **Started:** 2026-05-11T19:43Z
- **Completed:** 2026-05-11T19:44Z
- **Tasks:** 1 (single doc edit)
- **Files modified:** 1 (`firestarter_app/CLAUDE.md`)

## Accomplishments

- **Documentation paragraph added** to `firestarter_app/CLAUDE.md` between the "Known protocols" line and the `### Constants` heading. +20 lines additive. No other content modified.
- **All 8 required content elements** present in the paragraph per the plan's `<action>` checklist:
  1. Label prefix `Protocol overrides (WARNING-5):` ✓
  2. Override location: `build_db.py` after `_etype` derivation, before `chip_entry` ✓
  3. 3-predicate condition: `pinout_key == "DIP28_2764"` AND `proto_id == 0x07` (EPROM_STD) AND `_etype == "Flash/EEPROM"` ✓
  4. Override action: algorithm flipped to `0x0D` (EEPROM_POLL); firmware dispatch reaches `configure_eeprom28c` instead of `configure_eprom` ✓
  5. Rationale: socket pin 1 = A14 on 28C-family 5V EEPROMs (not VPP); `P1_VPP_ENABLE` (12V) is a hardware-damage path; `configure_eeprom28c` is pure 5V VCC ✓
  6. Scope: ~23 chips across 6 manufacturers — ATMEL (AT28C/BV), MICROCHIP memory (28C/28LV), NEC (UPD28C), XICOR (X28C), ST (M28256), EXEL (XLE2865A); plus the 7-chip regression-safe set on DIP28_27512 / DIP28_27256 (W27C512, SST27SF512, SST27VF512, W27C257, W27E257, SST27SF256, SST27VF256) ✓
  7. Audit pointer: `WARNING-5` in `.planning/v1.0-MILESTONE-AUDIT.md` and the phase folder `.planning/phases/13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we/` ✓
  8. Regression guard pointer: `tools/check_dispatch.py` asserts no `DIP28_2764 AND Flash/EEPROM` chip routes to `configure_eprom` ✓
- **File length grew from 81 → 101 lines** (+20). No other content removed; file still renders as valid Markdown (no broken headings, no stray fence pairs).
- **Plan's automated verification command PASSes** — all 5 grep terms present (`WARNING-5`, `DIP28_2764`, `EEPROM_POLL` or `0x0D`, `configure_eeprom28c`, `check_dispatch`).

## Verbatim Paragraph Added

The paragraph inserted between the "Known protocols" line and `### Constants` (lines 79–97 in the post-edit file):

```
Protocol overrides (WARNING-5): `build_db.py` applies an inline 3-predicate
conditional after deriving `_etype` and before constructing `chip_entry`. When
`pinout_key == "DIP28_2764"` AND `proto_id == 0x07` (EPROM_STD) AND
`_etype == "Flash/EEPROM"`, the chip's `algorithm` is flipped to `0x0D`
(EEPROM_POLL) so firmware dispatch reaches `configure_eeprom28c` (pure 5V VCC,
no VPP regulator engagement) instead of `configure_eprom`. Rationale: on the
`DIP28_2764` pinout, socket pin 1 maps to the VPP regulator output line and
`configure_eprom` asserts `P1_VPP_ENABLE` (12V) on every write pulse; on the
~23 affected 28C-family 5V EEPROMs, physical pin 1 is the A14 address line,
not VPP, so 12V on pin 1 is a hardware-damage path. Scope: ~23 chips across 6
manufacturers — ATMEL (AT28C/BV family), MICROCHIP memory (28C/28LV family),
NEC (UPD28C family), XICOR (X28C family), ST (M28256), EXEL (XLE2865A). 7 chips
remain on the `0x07` path because they are genuine UV-EPROMs on `DIP28_27512`
or `DIP28_27256` pinouts (W27C512, SST27SF512, SST27VF512, W27C257, W27E257,
SST27SF256, SST27VF256) and DO need 12V VPP on pin 1. See `WARNING-5` in
`.planning/v1.0-MILESTONE-AUDIT.md` and the phase folder
`.planning/phases/13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we/`.
Regression guard: `tools/check_dispatch.py` asserts no chip with
`pinout=DIP28_2764 AND electrical.type=Flash/EEPROM` routes to `configure_eprom`.
```

**Location relative to anchors:** The paragraph begins immediately after the "Known protocols" hex-list line (`0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39`) and ends immediately before the `### Constants` subsection heading. Both anchors are unchanged.

## Task Commits

Per the phase's submodule convention (mirrors Plans 13-01 and 13-02), the source change is committed inside the `firestarter_app` submodule first, then the pointer is bumped in the outer repo.

1. **Task 1: Add WARNING-5 override paragraph to firestarter_app/CLAUDE.md**
   - Submodule (`firestarter_app`): **`07ae624`** — `docs(13-03): document WARNING-5 algorithm override in firestarter_app/CLAUDE.md`
   - Outer repo: **`39d7c1d`** — `docs(13-03): bump firestarter_app pointer — WARNING-5 override docs in CLAUDE.md (07ae624)`

## Files Created/Modified

- **`firestarter_app/CLAUDE.md`** — added the "Protocol overrides (WARNING-5)" paragraph (20 lines, +0 lines removed). Inserted between "Known protocols" line and `### Constants` subsection. No edits elsewhere in the file.

## Decisions Made

- **Single paragraph, no new subsection** — per the plan's `<action>` step 1 ("Format: a 'Protocol overrides' labelled paragraph (NOT a new subsection — keep section depth flat)"). The paragraph sits flat under the existing `### Database Pipeline` heading, matching the "Known protocols" line that precedes it.
- **Label prefix `Protocol overrides (WARNING-5):`** — makes the entry greppable by both the topic name and the audit ID. The bare prefix `Protocol overrides:` from the plan was extended to `Protocol overrides (WARNING-5):` for indexability against the audit; the rest of the paragraph still references `WARNING-5` in body text per the plan's required content elements.
- **6 manufacturers, not 7** — the body text says "~23 chips across 6 manufacturers" (matching Plan 02's actually-fired count). Plan 01's regression guard caught 23 violations across 7 manufacturers by pinout signature; Plan 02's source-level override fires per-chip via the same 3-predicate signature and groups the chips into 6 distinct manufacturer-family groupings (ATMEL, MICROCHIP, NEC, XICOR, ST, EXEL). The discrepancy is a counting nuance (which level of grouping is "the right one"), not a coverage gap — all 23 chips are covered by both planes. The paragraph picks Plan 02's grouping because the override is what readers will trace back to.
- **Submodule pattern preserved** — source change committed inside `firestarter_app` (commit `07ae624`), then outer-repo pointer-bump (`39d7c1d`). Mirrors Plans 13-01 and 13-02. No `--no-verify`; hooks ran.

## Deviations from Plan

None — plan executed exactly as written. The only non-prescribed micro-decision was adding `(WARNING-5)` to the label prefix for indexability (the plan body said `Protocol overrides:`); the audit ID still appears in body text per the plan's required content elements.

The plan's `<threat_model>` enumerated three threats (T-13-14 through T-13-16). All three are addressed:
- **T-13-14 (undocumented override gets reverted):** Mitigated. The new paragraph plus the inline `WARNING-5` comment block in `build_db.py` (Plan 02) and the `check_dispatch.py` guard (Plan 01) provide three independent traces. Removing any one of the three would not silently delete the override — the other two would catch it.
- **T-13-15 (doc becomes stale relative to source):** Accept. The override condition is stable; the `~23 chips` count may drift mildly if upstream `infoic.xml` grows but the predicate-based discriminator remains correct.
- **T-13-16 (information disclosure):** Accept. No secrets in the documentation.

## Issues Encountered

- The `firestarter_app` submodule has pre-existing dirty state unrelated to this plan: version bump to `2.0.7_dev` in `firestarter/__init__.py`, edits in `firestarter/ic_layout.py`, and deletions of `.planning/codebase/*.md`. Per the SCOPE BOUNDARY rule (and mirroring Plans 13-01 and 13-02's identical note), these were left untouched. The submodule's `git add` only staged `CLAUDE.md`; the unrelated working-tree state is preserved for whoever owns it.

## User Setup Required

None.

## Self-Check

Verified before finalizing:

```
git log firestarter_app --oneline | head -3
  → 07ae624 docs(13-03): document WARNING-5 algorithm override in firestarter_app/CLAUDE.md  ✓ FOUND
  → fe7e14b fix(13-02): close WARNING-5 — DIP28_2764 5V EEPROMs override 0x07->0x0D in build_db.py  ✓ FOUND
  → 6c35587 test(13-01): add _28C_EEPROM_HAZARD_PINOUT WARNING-5 guard (initially FAILs with 23 violations)  ✓ FOUND

git log --oneline | head -3
  → 39d7c1d docs(13-03): bump firestarter_app pointer — WARNING-5 override docs in CLAUDE.md (07ae624)  ✓ FOUND
  → 68c01f6 docs(13-02): update STATE + ROADMAP for WARNING-5 closure  ✓ FOUND
  → 770b64f docs(13-02): complete WARNING-5 build_db.py override plan  ✓ FOUND

grep -c 'WARNING-5' firestarter_app/CLAUDE.md
  → 2 (label prefix + audit pointer)  ✓ PRESENT

grep -c 'DIP28_2764' firestarter_app/CLAUDE.md
  → 4 (existing pinout list + 3 references in new paragraph)  ✓ PRESENT

grep -c 'configure_eeprom28c' firestarter_app/CLAUDE.md
  → 1  ✓ PRESENT

grep -c 'check_dispatch' firestarter_app/CLAUDE.md
  → 1  ✓ PRESENT

grep -c 'EEPROM_POLL' firestarter_app/CLAUDE.md
  → 1  ✓ PRESENT

grep -c 'v1.0-MILESTONE-AUDIT' firestarter_app/CLAUDE.md
  → 1  ✓ PRESENT

wc -l firestarter_app/CLAUDE.md
  → 101 (was 81; +20 lines additive, matches plan's "~10 lines" target widened to a tight 20-line paragraph for content density)
```

## Self-Check: PASSED

## WARNING-5 Closure Across All Three Planes

This plan completes the documentation plane of WARNING-5. The full closure across the project:

| Plane | Plan | Artifact | Closure signal |
|-------|------|----------|----------------|
| **Source** | 13-02 | Inline 3-predicate override in `firestarter_app/tools/build_db.py` between `_etype` derivation and `chip_entry` construction | `INFO:` stderr line fires 23 times during regen; `minipro_complete_db.json` algos[0x07] 237→214, algos[0x0D] 18→41 |
| **Regression** | 13-01 | `_28C_EEPROM_HAZARD_PINOUT` guard in `firestarter_app/tools/check_dispatch.py` | `python3 firestarter_app/tools/check_dispatch.py` exits 0 with "0 DIP28_2764 Flash/EEPROM chips route to configure_eprom" |
| **Documentation** | 13-03 | "Protocol overrides (WARNING-5)" paragraph in `firestarter_app/CLAUDE.md` Database Pipeline section | `grep -c 'WARNING-5' firestarter_app/CLAUDE.md` returns 2 |

WARNING-5 (the 12V-on-A14 hardware-damage path on 23 DIP28_2764 5V EEPROMs introduced by Phase 12) is now closed at every layer. REQ-FW-03 (EEPROM_POLL DQ7 polling reachability for AT28C256/64) and REQ-SAF-01 (no chip applies VPP to an address pin) are both end-to-end reachable for all 23 affected chips. Phase 13 is execution-complete.

## Next Phase Readiness

- Phase 13 is execution-complete (Plans 01, 02, 03 all green).
- The phase can advance to `/gsd-verify-work` once STATE.md and ROADMAP.md are updated by this plan's metadata commit.
- No further code, DB, or documentation changes required for WARNING-5.

---
*Phase: 13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we*
*Plan: 03*
*Completed: 2026-05-11*

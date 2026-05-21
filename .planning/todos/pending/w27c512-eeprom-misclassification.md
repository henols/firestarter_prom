---
id: w27c512-eeprom-misclassification
title: W27C/E + SST27SF/VF series misclassified as UV-only EPROMs in chip database (should be electrically erasable)
captured: 2026-05-21
escalated: 2026-05-21 (operator: "the db is really wrong and must be fixed asap")
status: pending
type: bug
target_milestone: v1.5 hotfix OR v1.6 (operator decision)
priority: high
related_phase: 24
resolves_phase: null
---

# W27C512 misclassified as UV-only EPROM — should be electrically erasable

## The bug

`firestarter erase W27C512` returns `ERROR: Not supported`. The chip is being routed to the UV-only EPROM path in the firmware. But the **W27C512 is actually electrically erasable** per Winbond's datasheet — the "C" prefix denotes CMOS Flash EEPROM, not UV-only.

Per the project's existing protocol-override notes in `firestarter_app/CLAUDE.md`:

> 7 chips remain on the `0x07` path because they are genuine UV-EPROMs on `DIP28_27512` or `DIP28_27256` pinouts (W27C512, SST27SF512, SST27VF512, W27C257, W27E257, SST27SF256, SST27VF256) and DO need 12V VPP on pin 1.

W27C512 is on that "genuine UV-EPROM" list — but operator confirms 2026-05-21 that classification is wrong. W27C512 is a flash-erasable EEPROM (electrically erasable via an erase pulse), not a UV-only EPROM. The database build pipeline (`tools/build_db.py`) is misreading the chip's electrical type from `infoic.xml`.

## Empirical evidence (bench-verified 2026-05-21)

- `firestarter id W27C512` → `Chip ID check passed for W27C512` (chip alive, correctly seated)
- `firestarter read W27C512 backup.bin` → 64KB read clean in 14.45s; data is non-blank (existing program)
- `firestarter erase W27C512` → `ERROR: Not supported` ← THE BUG
- `firestarter blank W27C512` → host timeout (separate slow-path issue, possibly related to firmware blank-check loop on non-blank chips)

Expected behavior (per operator): erase should engage the chip's electrical erase mode (high-voltage erase pulse via VPP), wait for the erase cycle (~10ms typical), then verify blank. Same firmware path that handles 28C-family EEPROMs.

## Where to look in the codebase

- `firestarter_app/tools/build_db.py` — the database generation pipeline. The WARNING-5 protocol-override logic already handles a similar misclassification case (28C-family EEPROMs on DIP28_2764 pinout that needed `algorithm = 0x0D` instead of `0x07`). This is the same shape of bug — wrong `algorithm` / `electrical.type` for W27C512 (and probably the other 6 chips on the "genuine UV-EPROM" list that aren't actually UV-only).
- `firestarter_app/firestarter/data/chip_database.json` — the generated artifact; check what `algorithm` and electrical type W27C512 has after the build pipeline runs.
- `firestarter_app/tools/infoic.xml` — upstream source. Check what manufacturer/voltage flags the W27C512 entry actually carries; the build pipeline may be misreading them.
- Other suspects on the same "genuine UV-EPROM" list that may also be electrically erasable: SST27SF512, SST27VF512, W27C257, W27E257, SST27SF256, SST27VF256. Each should be datasheet-checked individually — some are genuinely UV-only ("SF" / "VF" in SST naming may indicate flash, but not always).

## Implementation sketch (CAUTION — not a 1-line override)

A naive `proto_id = 0x0D` flip is **dangerous** for these chips. The WARNING-5 case worked because 28C-family EEPROMs are pure 5V parts — `configure_eeprom28c` (the 0x0D dispatch target) never engages the VPP regulator. But the W27C/SST27SF series **DO need 12V VPP during programming** (just like a UV-EPROM), and they need an electrical erase pulse that 0x0D's `configure_eeprom28c` (5V SDP-disable + DQ7-polling) does NOT do.

Routing W27C512 to 0x0D would leave programming non-functional (no VPP engagement). Routing it to 0x07 (current state) leaves erase non-functional (UV-only path). **There's no existing firmware dispatch that handles "12V VPP write + electrical erase" — that's the real gap.**

Concrete fix shape (probably a 2-side change):

1. **Firmware side** — add a new dispatch path in `firestarter/src/memory.cpp` (or sibling) for "12V-VPP EEPROM with electrical erase". Possibly extend `configure_eprom` to support erase mode (the W27C series uses A9=12V + specific data-pin pattern + pulse to enter erase mode per Winbond datasheet), or add a new `configure_eeprom_hvpp` (high-VPP EEPROM).
2. **Host side** — assign these chips a new `protocol_id` value (e.g. `0x35 FLASH_EEPROM_LIKE` if that's the right semantics, or define a fresh `0x12 EEPROM_HVPP` — check what's available in the firmware dispatch table), and add an override in `build_db.py` similar to WARNING-5 to flip these specific chips to that path.
3. **Regression test** — `tools/check_dispatch.py` should assert that each chip in this list routes to the new path AND that no chip on the new path has a pinout-pin-1-collision (similar to WARNING-5's existing assertion).

Affected chip list (per `firestarter_app/CLAUDE.md` "genuine UV-EPROMs" comment, all flagged by operator 2026-05-21 as actually electrically erasable):
- W27C512, W27E512 (Winbond 64KB, DIP28_27512 pinout, VPP on pin 22)
- W27C257, W27E257 (Winbond 32KB, DIP28_27256 pinout, VPP on pin 1)
- SST27SF512, SST27VF512 (SST 64KB)
- SST27SF256, SST27VF256 (SST 32KB)

Each chip's electrical erase mode (entry sequence, pulse timing, verification) needs a datasheet pass before the firmware path is written.

## Workaround until properly fixed (operator-confirmed acceptable)

`firestarter erase <chip>` returns `ERROR: Not supported` — operator must UV-erase these chips externally to make them blank-writable again. Programming-only paths (`write`/`read`/`verify`/`id`) work today; erase doesn't.

For BENCH-02 with one of these chips already in the socket: the write path still exercises VPP regulator + write pulse + read-back. Just can't restore the pre-test state without UV erase.

## Why "v1.6 quite soon" rather than v1.5

- v1.5's scope is "uno328pb third board target" — chip database bugs are orthogonal.
- The misclassification doesn't BLOCK Phase 24 BENCH-02; we can substitute SST27SF512 (a different chip) for the bench cycle.
- Fixing in v1.6 lets the fix ship alongside any other DB pipeline corrections the operator finds while running v1.5 on real silicon.

## Cross-references

- `firestarter_app/CLAUDE.md` "Protocol overrides (WARNING-5)" — the pattern this fix mirrors
- `firestarter_app/tools/build_db.py` — the pipeline to modify
- `firestarter_app/tools/infoic.xml` — upstream source
- Memory `project-bench-findings-v15` — operator hardware notes (328PB-Uno + RURP shield)
- Phase 24 BENCH-02 — chose SST27SF512 as bench-test substitute because of this bug

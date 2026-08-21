---
phase: 153
slug: write-path-erase-policy
created: 2026-08-21
status: settled
---

# Phase 153 Decisions

This file is the settled-before-code-is-written record for Phase 153 (Write-Path Erase Policy).
Every later plan in this phase cites a `D-153-NN` id from here rather than re-deciding it.

## D-153-01 — Erase supply form and MERGE-05 funding

**Form (a):** the six-byte AT28C software chip-erase sequence is supplied as **six inline
`handle->firestarter_set_data(handle, address, byte)` calls**, preceded by one
`rurp_set_data_output()` call, inside `eeprom28c_erase_execute`. **No new `const byte_flip_t`
array is declared anywhere in `eeprom_28c.cpp`.**

Measured reason: a six-entry `byte_flip_t` table occupies `0x1e` = **30 bytes in section `d`
(`.data`, i.e. RAM)** — measured with `avr-nm -S --size-sort` on the committed leonardo ELF, where
the existing `EEPROM_SDP_DISABLE` table (also six entries) sits at `0x800127` and
`_ZL11FLASH_ERASE` sits at `0x800163`, both in section `d`. MERGE-05's RAM clause is **exact
equality plus one named 2 B exemption that is already fully consumed**
(`MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2`, `+2<=2=seam2`, Phase 149). The inline form
costs **0 B RAM** because no `.data` object is created at all — every byte is a literal argument
to an existing function call, living in `.text`/`.progmem`, not in an initialized RAM section.

**Rejected forms, each named, with a distinct reason (b):**

1. **Referencing the existing `FLASH_ERASE` table from `flash_utils.h`** — rejected. It is **not**
   free: `flash_utils.h` declares its tables at namespace scope in a header, which in C++ gives
   internal linkage unless an external declaration is visible, so **each translation unit that
   includes the header gets its own copy**. The committed leonardo ELF carries **two** surviving
   copies of `FLASH_ENABLE_WRITE` — `_ZL18FLASH_ENABLE_WRITE.lto_priv.92` and
   `_ZL18FLASH_ENABLE_WRITE.lto_priv.93` — proving LTO does **not** merge them. Reusing
   `FLASH_ERASE` this way would silently duplicate the table into `eeprom_28c.cpp`'s translation
   unit, at the same +30 B RAM cost, while also colliding with FIX-04's byte-frozen
   `flash_utils.h` framing and with Phase 117 D-10 / Phase 119 D-09's deliberate
   keep-the-`0x0D`-tables-local precedent (the same precedent that keeps `EEPROM_SDP_DISABLE` and
   `EEPROM_SDP_ENABLE` local rather than sharing `flash_utils.h`'s byte-identical twins).
2. **A `PROGMEM` table plus a per-entry copy** — rejected. RAM-neutral in principle, but
   `eeprom28c_emit_command_sequence` dereferences `sequence[i].address` **directly** against a
   `const byte_flip_t*` in RAM-addressable space; a PROGMEM table would need either a second
   emitter (duplicating the shared-emitter guarantee this phase otherwise relies on) or a
   per-entry stack copy loop, and has **no in-tree precedent** for this family.
3. **A new `.data` table plus a fourth named RAM exemption** — rejected because the two RAM-
   neutral forms above make it unnecessary. Spending the milestone's fourth named MERGE-05
   exemption on RAM, when a form exists that needs none, is not funded.

**The retype hazard is acknowledged and gated, not waived (c):** writing the six address/byte
pairs inline necessarily retypes bytes that already exist in the tree (the SDP-disable and
chip-erase sequences differ by exactly one nibble in the terminal byte: `0x20` vs `0x10`), and
that one-nibble divergence is a recognised hazard class in this repository —
`test_eeprom28c_sdp` Case 19 exists specifically for it. **Binding on plan 04:** the inline
literals are permitted only because a native full-stream equality case compares the erase op's
emitted stream, positionally, against a composite built from the in-tree tables
`SDP_FIXED_DIP28_28C256` and a `FLASH_ERASE`-driven reference — so the bytes are pinned against
the tree, never against this plan's prose.

**Funding posture (d, L-01):** a **fourth, separately-named, SHA-attributed FLASH** exemption will
be added to `check_size_baseline.py`, named exactly `MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES`,
sized from plan 14's **measured** cold figure and never from an estimate — following the same
single-consumer, module-docstring-enumerated pattern as
`MERGE05_DEFECT_FIX_EXEMPTION_BYTES` (96, Phase 145), `MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES`
(210, Phase 149) and `MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES` (288, Phase 151).

Four alternatives are rejected on the record, by name:

- **Widening a band literal** (e.g. `MERGE05_UNO_CLASS_FLASH_BAND` or leonardo's 0 B band) —
  rejected: would silently admit unrelated future growth and destroy the tripwire, the same
  reasoning `check_size_baseline.py`'s own docstring gives for the prior three exemptions.
- **Re-anchoring `size_baseline_base01.json`** — rejected: three prior phases already refused
  this on the record (the `merge05_clause`/`re_anchor_note` fields say so verbatim, three times);
  a green `--policy merge05` run after a re-anchor means the anchor moved, not that flash growth
  stayed inside the original band.
- **Folding the bytes into an existing exemption constant** — rejected: each of the three
  existing exemptions is scoped to one attributable commit set (defect fix / page-size seam /
  lock-status read); laundering the erase cost into one of them breaks that single-consumer,
  single-attribution property.
- **Shrinking the fix to fit** — rejected: the six-write sequence and its `t_EC` wait are the
  AN 0544B-required shape; trimming them to fit a pre-existing band is the wrong incentive and
  risks the feature, the same reasoning already on record for the page-size seam.
- **Byte-neutral offsetting is explicitly rejected** — it would require hunting savings in code
  this phase has no reason to touch, turning a one-feature phase into an unrelated refactor.
- **Compile-time gating the `CMD_ERASE` arm off on leonardo is explicitly rejected** — it would
  create a functional divergence on the board the operator actually writes with, which is worse
  than spending a named exemption.

**The two size figures, stated separately and never conflated (e):** MERGE-05 leonardo **flash**
headroom is **0 B** (currently at exactly `+594` against a `0 (band) + 96 + 210 + 288 = 594` B
allowance — the four addends being the leonardo flash band plus the three existing named
exemptions). The **Caterina** cliff headroom is a **different, separate, UNGUARDED** figure:
`28672 - 27500 = 1172` B. Quick task `260820-a7w` raised `board_upload.maximum_size` to the real
32768 B on all three AVR environments, so the linker no longer protects the USB bootloader —
past 28672 B the leonardo's Caterina bootloader is overwritten and the board is bricked, and no
gate catches it. These two numbers (0 B MERGE-05 flash headroom vs. 1172 B Caterina headroom) must
never be conflated in any later plan.

**Gate for the inline literals (binding on plan 04):** the inline literals are gated by a native
full-stream equality case comparing `eeprom28c_erase_execute`'s emitted stream, positionally,
against a composite reference built from the in-tree `SDP_FIXED_DIP28_28C256` table and a
`FLASH_ERASE`-driven reference sequence. This is named as binding on plan 04 so the erase bytes
are pinned against the tree, not against this document's prose.

**ERASE-09 closing statement (f):** the change this section funds is
**software-proven and unvalidated on silicon**.

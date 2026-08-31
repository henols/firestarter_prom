---
title: "Decode infoic.xml flags bits 14/15 (protect-before/protect-after) in build_db.py"
date: 2026-07-10
priority: low
source: /gsd-explore session (infoic.xml protection-flags investigation)
---

# Todo: decode flags bits 14/15 as protect metadata

`tools/build_db.py` currently decodes `flags & 0x10` (electrically erasable) and
`flags & 0x20` (chip-ID check). Two more bits are protection-relevant and
verified against minipro source (`src/database.c` L39–50 @ `a8efaed`):

| Bit | Mask | minipro constant | Semantics |
|---|---|---|---|
| 14 | `0x4000` | `MP_OFF_PROTECT_BEFORE` | programmer can/must unprotect before write (gates minipro `-u`) |
| 15 | `0x8000` | `MP_PROTECT_AFTER` | can re-protect after write (gates minipro `-P`) |

## Task

Emit these as chip_database.json fields (e.g. `protect_off_before: bool`,
`protect_on_after: bool`) so diagnostics / `dev test` reports can surface
"upstream expects an unprotect-before-write sequence for this chip".

## Interpretation guardrails (from research — do NOT over-promise)

- These are **write-path reversibility hints**, NOT lock-status readability.
  W29C020C (readable permanent boot-block) is flag-identical (`0x0040c078`) to
  W29EE011 (SDP-only). The AMD Autoselect readable-sector-protect group
  (AM29F/SST39SF/W49F/AT49F) is `0x00000078` — b14/b15 both 0.
- b15=1 ≈ SDP-page-write-family marker in practice; b14=1 ∧ b15=0 ≈ "AMD-style
  chip-unprotect exists" — heuristics, inconsistent within families
  (AM29F002B has b14=1 while AM29F040 has b14=0).
- The actual protect op in minipro is an opaque TL866 opcode (0x18/0x19) —
  no mechanism/region info exists to decode.

## Acceptance

- build_db.py decodes both bits with comment citing minipro `database.c` @ `a8efaed`
- Fields present in regenerated chip_database.json; no behavior change in
  write/read paths (metadata only)
- Cross-check note: chips where firestarter's flash_5v_page handler already
  does an SDP dance should have b15=1 — flag any mismatches as findings, not failures

## Related

- Seed: `.planning/seeds/lock-status-command-hand-curated-protection-table.md`
- Note: `.planning/notes/infoic-xml-protection-flags-research.md`

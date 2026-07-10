---
title: "infoic.xml protection flags — research result (negative for lock-status derivation)"
date: 2026-07-10
context: "/gsd-explore: can minipro infoic.xml flags be connected to lockable-proms.md lock mechanisms?"
---

# infoic.xml protection flags — what the XML knows and doesn't

Investigated whether minipro's `infoic.xml` (pinned commit
`a8efaedc236c1d9718bd28299dfbb99536b010ff`) encodes chip protection/lock
information mappable to the `protection_kind / status_readable / unlockability`
taxonomy proposed in `firestarter_app/doc/lockable-proms.md`.

**Verdict: PARTIAL, and too coarse to derive lock-status metadata.** Do not
re-investigate this angle.

## What exists (verified against minipro source @ a8efaed)

Two boolean flag bits, defined in `src/database.c` L39–50:

| Bit | Mask | Constant | Meaning |
|---|---|---|---|
| 14 | `0x4000` | `MP_OFF_PROTECT_BEFORE` | unprotect-before-write supported/required (gates `-u`) |
| 15 | `0x8000` | `MP_PROTECT_AFTER` | re-protect-after-write supported (gates `-P`) |
| 18 | `0x40000` | `MP_LOCK_BIT_WRITE_ONLY` | MCU lock bits only — never set on any type=1 (memory) chip |

The protect operation itself is an **opaque TL866 firmware opcode**
(`tl866iiplus.c`: `PROTECT_OFF` 0x18 / `PROTECT_ON` 0x19, parameterless). The
XML carries no mechanism, region, or readability information. MCU fuse/lock
data lives in the `config` attribute — NULL for every parallel memory chip.

## The disqualifying cross-tab

| Chip group | flags | b14/b15 | Reality (lockable-proms.md) |
|---|---|---|---|
| W29C020C / W29C040 | `0x0040c078` | 1/1 | readable, PERMANENT boot-block lockout |
| W29EE011 / AT29C010A / AT29C256 | `0x0040c078` | 1/1 | SDP-only, NOT readable — **identical flags** |
| AT28C256 / AT28C64B | `0x0000c010` | 1/1 | SDP EEPROM |
| AM29F010/040, SST39SF040, W49F002/020, AT49F040 | `0x00000078` | 0/0 | AMD Autoselect READABLE sector-protect — **invisible** |
| MX29F040 | `0x00004278` | 1/0 | protect-off only; +undocumented bit 9 |
| AM29F002B | b14=1 | 1/0 | inconsistent within AMD family |

Conclusions:
- `status_readable` is **not derivable** (W29C020C ≡ W29EE011).
- Absence of bits ≠ no protection (whole AMD readable group is all-zeros).
- b15=1 ≈ SDP page-write family marker; b14=1∧b15=0 ≈ AMD-style unprotect
  exists. Heuristics only.

## Loose ends (recorded, not investigated)

- **Bit 22 (`0x00400000`)** — undocumented, no minipro constant; set on the
  AT29C/W29C/W29EE page-write group.
- **Bit 9 (`0x200`)** — undocumented; observed only on MX29F040.

## Consequence

Any lock-status feature needs a **hand-curated** protection table (family
level; lockable-proms.md is the source) — see seed
`.planning/seeds/lock-status-command-hand-curated-protection-table.md`.
The cheap decodable win is bits 14/15 as write-path metadata — see todo
`.planning/todos/pending/decode-infoic-flags-bits-14-15-protect-metadata.md`.

Sources: minipro `src/database.c`, `src/main.c` (`write_page_file`,
`action_write`), `src/tl866iiplus.c` @ `a8efaed` (gitlab.com/DavidGriffith/minipro).

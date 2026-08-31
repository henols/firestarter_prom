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

---

## Scoped exception — 2026-07-29 (Phase 120 / HOST-04)

**What is unchanged.** This note's verdict stands: bits 14 and 15 are too coarse to derive
lock-status metadata, `status_readable` is not derivable, and the taxonomy question should not be
re-investigated. `W29C020C` with its permanent boot-block lockout and `W29EE011` with SDP only are
still flag-identical, so readability is still not derivable. **Neither of those parts is in the
`0x0D` bucket.**

**The narrower question Phase 120 asked.** Not "what kind of protection does this part have and can
its state be read" but only "does this 28C-family protocol-`0x0D` part have an SDP command decoder at
all". Bit 15 was tested against that single, narrower question.

**Three independent probes, all passing.** HOST-04's eight named pre-SDP entries plus
identical-generation second sources: bit 15 clear on all eight (**8/8**), six of them with flags
exactly zero. Both FRAM parts, a different memory technology with no EEPROM command decoder: bit 15
clear on both (**2/2**), both with flags exactly zero. The four datasheet-of-record Atmel parts
(`AT28C256`, `AT28C64B`, `AT28C010`, `AT28C040`): bit 15 set on all four (**4/4**). No probe failed
and nothing needed a special case.

**Result and where it lives.** All 84 protocol-`0x0D` entries matched; zero unmatched, zero MIXED
under exact-token keying; ALLOW 43 / REFUSE 41. See
`.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-SDP-PARTITION.md` and
`.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-sdp-partition.json`.

**The hedge this sharpens.** This note called bit 15 "roughly an SDP page-write family marker" (see
Conclusions above). Tested directly, bit 15 and a page size greater than one **disagree on twelve of
the eighty-four**, so bit 15 is not a page-write proxy — it carries information page size does not,
which is what makes it usable as its own signal. See
`.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-WATCHLIST.md` for the nine
residual-risk entries this disagreement produces.

**Both findings are correct about different questions.** The 2026-07-10 verdict above (taxonomy:
`protection_kind` / `status_readable` / `unlockability`) and this 2026-07-29 result (capability: does
an SDP command decoder exist at all) are both correct, and neither overturns the other — treat neither
as overturned by the other. Nothing reads `infoic.xml` at runtime or in CI; `infoic.xml` is not
committed to either sub-repo; the shipped artifact is a static transcribed token table
(`firestarter/sdp_capability.py`).

**The loose ends stay loose.** This note's bit 22 and bit 9 observations, and its routing of decodable
bits 14/15 work to the pending
`decode-infoic-flags-bits-14-15-protect-metadata` todo, are unaffected by this exception. Decoding
those bits into the DB proper would later make the Phase 120 table generated rather than transcribed —
narrowing the curation, not removing the need for a partition.

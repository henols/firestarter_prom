---
title: Protocol rebuild — rationale (current-state pain)
date: 2026-06-25
context: Captured during /gsd-explore 2026-06-25. Companion to the seed protocol-first-architecture-rebuild.md.
---

# Protocol rebuild — why ("it can probably be done better than today")

The protocol layer grew organically from minipro/infoic inheritance across v1.0–v1.15.
That accumulated real scar tissue. This note records the "why" behind the v1.16 seed so a
future planner isn't working from a blank slate.

## Current-state pain

- **Protocols are bare hex IDs.** A "protocol" today is a minipro `protocol_id`
  (`0x05`, `0x06`, `0x07`, `0x08`, `0x0B`, `0x40`, `0x34`, …). The names are numbers; the
  taxonomy is inherited, not designed. Hard to reason about, easy to mis-route.
- **Axis confusion.** The algorithm axis (how to write/erase) kept getting tangled with the
  UV-vs-EEPROM electrical axis — surfaced repeatedly in v1.11 (infoic decode), v1.12
  (dispatch hardening), and the v1.15 DB-decode audit. `protocol_id` is the algorithm axis,
  NOT the UV-vs-EEPROM axis — but the code/data didn't always keep that clean.
- **Handler duplication.** `configure_eprom` / `configure_sram` / `configure_flash` / flash4
  and friends each carry overlapping address-setup, strobe, polling, and VPP logic. Lots of
  near-duplicate code.
- **Flash ceiling.** The Leonardo build sits at ~89.5% flash against a ~90% gate. Every new
  handler or fix fights for headroom. Duplication is the main culprit; shared primitives are
  the lever.
- **One-off fixes accrete.** v1.11–v1.15 shipped a long string of point fixes (0x0B shared
  OE/VPP-pin reads, 0x08 large-EPROM/P1-as-VPP writes, flash4 256B-page boundaries, VPP-skip
  on reads). Each correct, but the lack of a documented per-protocol model means the *why*
  lives in commit messages and STATE.md decisions, not in the code.

## What "better" looks like

- A **named, documented protocol vocabulary** where each protocol's behavior is traceable to
  a datasheet and its firmware handler's *why* is written down.
- **Shared primitives** so adding/maintaining a protocol is composition, not copy-paste — and
  flash shrinks instead of creeping toward the ceiling.
- A **per-protocol bench ledger** that's honest about what's silicon-proven vs `UNVERIFIED`.

## What we explicitly do NOT change

- The minipro DB stays the ground truth for firmware control values (datasheets verify, they
  don't replace).
- The Leonardo-only-authoritative bench discipline.
- Algorithm-first dispatch / no-guessing.

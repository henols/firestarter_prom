---
title: Protocol-first architecture rebuild (v1.16)
trigger_condition: v1.15 milestone closed (Phase 84 executed, v1.15 tagged/merged)
planted_date: 2026-06-25
status: dormant
---

# Protocol-first architecture rebuild (v1.16)

A ground-up re-organization of how Firestarter models, names, and validates the
EPROM/Flash/SRAM programming **protocols** — turning today's inherited-from-minipro
hex-ID buckets into a properly-named, datasheet-verified, primitive-decomposed
architecture with a per-protocol bench-verification ledger.

**Why now:** captured during `/gsd-explore` 2026-06-25. See
[`protocol-rebuild-rationale.md`](../notes/protocol-rebuild-rationale.md) for the
current-state pain this fixes.

## Locked decisions (from the explore session)

1. **Ground truth stays the minipro DB.** The minipro/infoic-derived
   `chip_database.json` remains authoritative for generating the values that control
   the firmware. Datasheets do NOT replace it.
2. **Datasheets are the verification + rationale layer.** For each protocol, use the
   datasheet to confirm our interpretation of the minipro DB is correct, and to
   **document why each firmware handler does what it does** (timing, VPP, pin behavior,
   write/erase algorithm). Preserves the "algorithm-first dispatch, no guessing" core value.
3. **Naming = both, in sequence.**
   - First: give every existing protocol bucket (0x05, 0x06, 0x07, 0x08, 0x0B, 0x40, 0x34, …)
     a real human name + documented rationale, keeping the current dispatch structure stable.
   - Then: re-decompose handlers into **shared primitives**, with names following the new
     structure — protocol by protocol, as each is validated.
4. **"Working" = bench-proven on the Leonardo.** A protocol is only "done"/verified when
   it passes on real silicon (Leonardo + RURP Rev 2.0, the only trustworthy combo). Every
   protocol without a chip on hand is carried as an explicit `UNVERIFIED` row — honest gaps,
   never false confidence.
5. **Driver = flash size via reuse.** Re-architect so common code (address setup, data
   strobe, polling, VPP gate, page buffer, SDP unlock, …) is shared, shrinking the Leonardo
   flash footprint from today's ~89.5% ceiling.

## Staged shape (rough phase decomposition for v1.16 planning)

1. **Datasheet acquisition** — download + store datasheets for all on-hand ICs + one
   representative chip per minipro protocol bucket, into a new `datasheets/` folder. (See
   the `gather-protocol-datasheets` todo.)
2. **Naming + documentation pass** — author the protocol vocabulary (hex bucket → proper
   name → datasheet-verified behavior), document each handler's *why*. Dispatch structure
   unchanged; near-zero flash delta. Stabilizes the map the refactor works against.
3. **Primitive decomposition / refactor** — extract shared primitives, recompose handlers
   from them, measure flash savings. Done incrementally, one protocol family at a time,
   each guarded by native register-level tests + the existing `check_dispatch.py` / `diff_db.py` gates.
4. **Per-protocol bench validation** — bench-prove each protocol that has silicon on the
   Leonardo; record results in a per-protocol verification ledger; leave no-chip protocols
   as explicit `UNVERIFIED`.

## Constraints carried in

- Leonardo + RURP Rev 2.0 is the ONLY authoritative bench combo (v1.9 read bug elsewhere).
- Host↔firmware constant parity must stay in lockstep (`constants.py` ↔ `firestarter.h`).
- Reuse-first: no new third-party deps; reuse `write_test.sh`, `dev validate-family`,
  `dev consistency-check`, `gen_test_image.py`, `check_dispatch.py`, `diff_db.py`.
- Dual-repo lockstep for any wire-touching change; watch the py3.12-masks-CI-3.11 ruff/codegen trap.

## When triggered

Promote via `/gsd-new-milestone v1.16` after v1.15 closes. Feed the open items from
`.planning/research/questions.md` (protocol-rebuild block) into `--research-phase` planning.

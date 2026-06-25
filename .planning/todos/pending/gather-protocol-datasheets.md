---
created: 2026-06-25T00:00:00Z
title: Gather + store protocol datasheets (datasheets/ folder)
area: docs/firmware
trigger: v1.16 protocol rebuild (start after v1.15 closes) — see seeds/protocol-first-architecture-rebuild.md
files:
  - datasheets/ (new folder — one subfolder/file per IC)
---

## Task

First concrete step of the v1.16 protocol-first rebuild: download and store datasheets so
the rebuild has a verification + rationale source for every protocol.

Collect into a new top-level `datasheets/` folder:

1. **All on-hand ICs** — the v1.15 physical inventory (the 11 chips: W27C512, W27E512,
   SST27SF512, W27E040, SST39SF040, W29C020, W29C040, FM1608, ST M27C512, AM27C020, 2516).
2. **One representative common IC per minipro protocol bucket** that has NO chip on hand, so
   every protocol has at least a datasheet to verify against (even if it stays `UNVERIFIED`
   on the bench).

## Notes

- Goal is verification + documenting each firmware handler's *why* — the minipro DB stays the
  ground truth; datasheets confirm our interpretation is correct (per the explore decision).
- Suggested layout: `datasheets/<protocol-name-or-id>/<part>.pdf` so it maps onto the new
  protocol vocabulary as it's authored.
- This is chip-independent prep — can be done before v1.16 formally starts, but the rebuild
  itself waits for v1.15 close (operator decision 2026-06-25).

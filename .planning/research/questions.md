# Research Questions

Open questions to resolve via deeper investigation. Appended by `/gsd-explore` and other workflows.

## Protocol-first architecture rebuild (v1.16) — added 2026-06-25

Source: `/gsd-explore` session 2026-06-25. See `seeds/protocol-first-architecture-rebuild.md`.

1. **Shared-primitive inventory.** What are the actual common operations across the current
   firmware handlers (`configure_eprom`, `configure_sram`, `configure_flash`, flash4, …)?
   Produce a decomposition: address setup, data strobe, poll/verify, VPP gate, page buffer,
   SDP unlock, chip-id. Which are genuinely shareable vs protocol-specific?
2. **Datasheet sourcing list.** Concrete list of datasheets to download: the 11 on-hand ICs +
   one representative common chip per minipro protocol bucket without silicon. Where are the
   authoritative copies?
3. **Current per-handler flash breakdown.** Measure today's Leonardo flash usage attributed
   per handler/family, to quantify where reuse buys the most headroom against the ~90% ceiling.
4. **protocol_id → name → datasheet map.** For every `protocol_id` in `chip_database.json`,
   the proper human name and the datasheet-verified behavior (write/erase algorithm, VPP,
   pin roles). This is the vocabulary the naming pass produces.
5. **Verification ledger format.** How to represent per-protocol bench status (PASS on
   Leonardo / `UNVERIFIED` / chip-needed) so it composes with the existing v1.13 per-family
   matrix + v1.15 EVIDENCE.{md,json} rather than replacing them.

## Community chip-validation command (dev test) — added 2026-07-02

Source: `/gsd-explore` session 2026-07-02. See `seeds/community-chip-validation-command.md`
and `notes/dev-test-design-decisions.md`.

1. **Health-proving write/verify pattern.** What data pattern does the write/verify step
   use? A fixed pattern (e.g. 0x00/0xFF/0xAA) is simple but blind to stuck/shorted address
   lines — a chip can pass while mis-addressing. An **address-derived pattern** (each byte a
   function of its address) makes verify catch address-line faults directly. This ties to the
   old Bug A "upper-address jitter" history — the exact failure class an address-derived
   pattern would surface. Decide before planning; also decide the UV small-region variant.

2. **Community PASS → support_status graduation.** Does a community-submitted PASS
   automatically graduate a chip's `support_status` (spec-only → supported), or only flag it
   for maintainer confirmation? Affects trust model: auto-graduation risks a bad bench
   config promoting a chip falsely; manual keeps the maintainer authoritative but adds
   triage load. How does the structured report reconcile/diff against the current DB entry
   inside `gsd-inbox`?

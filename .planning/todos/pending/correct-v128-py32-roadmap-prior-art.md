---
id: correct-v128-py32-roadmap-prior-art
title: Correct the v1.28 PY32F071 prior-art + flash-path claims in ROADMAP.md
captured: 2026-07-28
status: pending
type: docs
priority: medium
resolves_phase: 130
source: /gsd-explore 2026-07-28 (notes/py32f071-port-branch-state.md)
---

> **Linked to v1.23 Phase 130 (CLOSE-03), 2026-07-30.** That phase owns the
> ROADMAP slot renumber and this prior-art correction in the same change. Note
> the v1.23 research independently re-verified all five corrections below AND
> found a sixth: `platform/py32f071/PORTING.md` — which this entry's item 4 and
> the ROADMAP both cite — exists **only** on the two CLOSED PRs (#46/#47, blob
> `4b1a441`), not on the live stack, and its prescribed module layout does not
> match what #48 built. See `.planning/research/SUMMARY.md` A-6/R-8.

# Correct the v1.28 PY32F071 ROADMAP entry

[`ROADMAP.md`](../../ROADMAP.md) line 33 (`v1.28 PY32F071 Port`) was written at
the 2026-07-27 backlog review against an incomplete read of `origin`. Three
claims in its **"Prior art — verified 2026-07-27"** paragraph are wrong, and the
paragraph is load-bearing: it tells a future planner where to start.

## What to change

1. **"PR #46 was CLOSED unmerged as a draft on 2026-07-21, so this work is *not*
   in flight"** → **PR #48 (`agent/py32f071-toolchain`) is OPEN as a draft**,
   stacked on `agent/portability-macros`. PRs #45 and #47 are also closed
   attempts. The work *is* in flight.

2. **"the branch `feature/py32f071-toolchain` survives at `2c2ed10` with 603
   additions across 8 files"** → that is the smallest of five branches.
   `agent/py32f071-toolchain` carries **52 commits ahead of `beta`** (5
   portability-macro + 47 py32) and is only **27 commits behind**. Fix
   **"Start scoping from that branch, not from scratch"** to point at **#48**,
   and warn off the closed `feature/py32f071-full-support` (#47), whose `usb.c`
   is weak no-op stubs that link and would leave the board silent on USB.

3. Add the retired risk: **PY32F071 CI is green** (2026-07-21) building the
   *shared* command processor, framing and PROM algorithms for Cortex-M0+ against
   a pinned OpenPuya SDK (`0ed2f4b`) with CherryUSB CDC. "Does it build" is no
   longer the unknown. What remains: provisional pin map, runtime-only (not
   flash-persistent) config, DAC VPP on the closed #45, and **zero** hardware
   validation.

4. Record the **flash-path decision** and its PCB consequences —
   [`seeds/py32f071-no-external-tool-fw-install.md`](../../seeds/py32f071-no-external-tool-fw-install.md).
   Self-flashing bootloader over the existing CDC + COBS transport; no external
   host tools; factory USB DFU (Puya UM1504) kept as a maintainer-only recovery
   route, which requires BOOT0/nBOOT1 strapping and SWD pads **in the first
   schematic**.

5. Record the hardware reality: **no PCB exists** (operator, 2026-07-28). The
   honest closeable scope without silicon is the rebase onto `beta`, the host
   flasher seam, flash-persistent config, and the install-path design. Every
   bench-gated item in `PORTING.md` defers.

## Note

Do this before v1.28 is activated, not after — `/gsd-new-milestone` reads this
entry to seed scope, so a stale prior-art paragraph propagates straight into the
milestone.

---
title: Community chip-validation command (dev test <chip>)
trigger_condition: Next milestone planning after v1.20 closes (v1.20 tagged/merged, operator gate cleared)
planted_date: 2026-07-02
status: dormant
---

# Community chip-validation command (`firestarter dev test <chip>`)

A developer/community command that takes a chip name, derives a **technology-aware
test plan** from the chip's protocol/family, runs every supported memory operation as
**independent non-fatal steps**, and emits a **diagnostic report** the maintainer can act
on — filed straight to GitHub. The goal is to turn chip coverage from "what's on Henrik's
bench" into "what's on the whole community's bench."

**Why now:** captured during `/gsd-explore` 2026-07-02. Nearly every milestone in this
project has ended with deferrals of the form *"can't verify — operator doesn't have that
chip"* or *"Leonardo-only PASS, no HW to confirm."* Distributing testing to community
members with the missing silicon is the strategic unlock for chip coverage. See
[`dev-test-design-decisions.md`](../notes/dev-test-design-decisions.md) for the full
locked-decision detail and the diagnostic-contract field list.

## The idea in one paragraph

`firestarter dev test <chip>` reads the chip's DB entry, runs `classify()` to get its
protocol/family, and builds a test plan of *only the operations that protocol supports*
(id-check, read, write, verify, erase, blank-check). It runs each as an isolated step so a
failure in one (e.g. a locked boot block, an unsupported erase) is recorded as a **finding**
rather than aborting the sweep. It produces two things from one run: a **human-readable
pass/fail summary** and a **structured machine-readable report**, and offers to file them as
a GitHub issue automatically.

## Locked decisions (from the explore session)

- **Capability sweep, not a fixed script.** Test plan is derived per-chip from
  `classify()` / protocol; run *all possible* memory commands for that chip.
- **Independent, non-fatal steps.** A broken blank-check must not stop the write test
  (the W29C040 locked-boot-block case is the canonical example — the *surprise* was the
  valuable output).
- **Sacrifice a blank/scratch chip** is the default mental model.
- **Technology-aware destructiveness:**
  - EEPROM / Flash (electrically erasable) → full repeatable round-trip:
    write pattern → verify → erase → blank-check.
  - UV EPROM (one-way without a UV lamp) → **write only a small region** so an
    eraser-less tester can retry; electrical erase step is N/A.
- **Non-destructive by default.** Bare run = id + read + blank-check. Write/erase steps
  require an explicit **`--destructive`** flag. When run non-destructively the command must
  **loudly** state "only N of M tests ran — pass `--destructive` on a scrap chip for the rest."
- **Dual output from one run:** compact human summary + structured machine report.
- **Self-contained issue body** in the normal case: one markdown document = human results
  table on top + a fenced ` ```json ` block underneath. Small enough to need no attachment.
- **Tiered submission** (`--submit`): if `gh` is present and authed → `gh issue create` with
  auto-label so it lands in `gsd-inbox` triage; otherwise → open a prefilled
  `issues/new?title=…&body=…` browser URL. The gist/attachment path is reserved for the
  rare **verbose failure log** (byte-level dumps, raw serial traces) that exceeds URL limits.
- **Two-tier diagnostic contract** (see note for full field list): auto-capture everything
  the firmware/host knows; **prompt** the tester for the few things firmware genuinely
  can't self-report (shield revision, chip provenance, pot adjustments).

## Scope signal

This is milestone-sized, not a single phase — CLI command + test-plan engine + report
schema + submission flow + the interactive provenance prompts. Likely its own milestone
when v1.20 closes.

## Open questions

Tracked in [`research/questions.md`](../research/questions.md) under this seed:
1. What write/verify **pattern** proves chip health (fixed vs address-derived)?
2. Does a community PASS **graduate** a chip in `support_status`, or only flag it for
   maintainer confirmation?

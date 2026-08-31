---
title: dev test <chip> — design decisions & diagnostic contract
date: 2026-07-02
context: Captured during /gsd-explore 2026-07-02. Companion to seed community-chip-validation-command.md.
---

# `firestarter dev test <chip>` — design decisions

Records the "why" behind the community chip-validation seed so a future planner isn't
working from a blank slate. Companion to
[`community-chip-validation-command.md`](../seeds/community-chip-validation-command.md).

## Test-plan model

- The plan is **derived per-chip** from the DB entry + `classify()` — run only the memory
  operations the chip's protocol actually supports (id, read, write, verify, erase,
  blank-check).
- Steps run **independently and non-fatally**. A failing step is a *finding*, not an abort.
  Rationale: the W29C040 locked-boot-block discovery — the surprise was the value; a
  fail-fast script would have hidden it.

## Destructiveness (technology-aware)

| Family | Erase-after possible? | Default write behavior |
|---|---|---|
| EEPROM / Flash | Yes (electrical) | Full repeatable round-trip: write → verify → erase → blank-check |
| UV EPROM | No (needs UV lamp) | Write **small region only** so an eraser-less tester can retry; skip electrical erase |

- **Default = non-destructive**: id + read + blank-check only.
- **`--destructive`** unlocks write/erase steps; documented as "sacrifice a blank/scratch chip."
- Non-destructive runs must **loudly** report: *"only N of M tests ran — pass `--destructive`
  on a scrap chip for the rest."*

## Output & submission

- **One run → two artifacts:** compact human pass/fail summary + structured machine report.
- **Self-contained issue body** (normal case): a single markdown doc — human results table
  on top, fenced ` ```json ` block beneath. Both goals served, no attachment needed. A
  single-chip sweep is only a few KB, so it fits inside a prefilled-URL body.
- **Tiered `--submit`:**
  - `gh` present + authed → `gh issue create`, auto-labeled → drops into `gsd-inbox` triage.
  - else → open prefilled `github.com/.../issues/new?title=…&body=…` in browser.
  - **gist/attachment tier** reserved for the *verbose failure log* (byte dumps, raw serial
    traces) that overflows URL limits — the rare "detailed log to fix a problem" case.

## Two-tier diagnostic contract

The whole point: a report that says "it failed" is noise. Fields below are the ones that
repeatedly cracked real RCAs in this project (Bug A / Rev 0 shield read-path; ST-vs-Winbond
512 chip-ID mixup; AM27C020 VPP droop; uno328pb timeouts).

### Auto-captured (firmware/host already know)
- **FW version + board type** (`version:board` from MSG_OK) **and host app version** —
  pins board-specific bugs and FW/host desync.
- **Chip-ID: expected vs actual** — fastest wrong-chip / wrong-entry signal.
- **Protocol path taken** — `classify()` result + protocol byte + which handler ran
  (post-v1.20 protocol-only dispatch).
- **Per-op result + exact error code** (`0xA4`, `0xBB`, `0x303`, …).
- **Byte-mismatch fingerprint** — % bad + pattern classification: all-`0xFF` → blank/contact
  fault; high-address clustering → address-line; scattered → transport.
- **Measured VPP/VPE during the write step** — auto-run the monitor mid-sweep; captures the
  tester's actual rail voltage (many bugs were voltage droop).
- **Transport health** — COBS/CRC errors, retries, timeouts (uno328pb instability signature).
- **DB entry used** — `support_status`, `protocol_id`, pin config, voltages the host assumed.

### Must-ask the tester (firmware can't self-report)
- **Shield revision** — the EEPROM `hw_revision` byte can't distinguish Rev 2.2 / 2.0 /
  modified Rev 0, yet it was decisive for Bug A. Prompt for it (offer "not sure").
- **Chip provenance** — new/blank vs pulled/used; (UV) do they own an eraser.
- **Pot adjustments** — did they touch the voltage trim.

**Design consequence:** the command should collect the human-only provenance as **prompts
before the sweep**, so no report ever lands with those fields blank — otherwise a
beautiful auto-report is still un-actionable because the shield is unknown.

# Project: Firestarter — Protocol-Aware Programming Architecture

**Created:** 2026-05-08
**v1.0 shipped:** 2026-05-11
**v1.1 status:** Parked at 80% (Phase 4 hardware-validation open — FM1608 byte-0 bug requires a different Uno board to unblock; see `.planning/debug/fm1608-fresh-chip-baseline.md`)
**Active milestone:** v1.2 — Message-ID Logging Rework (started 2026-05-18)

## Current Milestone: v1.2 Message-ID Logging Rework

**Goal:** Replace firmware text-string logs with numeric message IDs + raw parameter byte arrays. The format catalog and decoding logic move from firmware PROGMEM to the Python host. Driven by Leonardo flash pressure (currently 98.7% Flash usage) and the protocol-cleanliness benefit of removing per-call string literals.

**Target features:**
- **Canonical message catalog** — single source-of-truth file in the meta-repo (e.g. `messages.yaml`) declaring `id → format_string + parameter_shape` for every firmware log message
- **Codegen pipeline** — build step generates `firestarter/include/messages.h` (C++ enum + ID constants) and `firestarter_app/firestarter/messages.py` (host-side decoder catalog) from the canonical file. Generated files committed; CI regenerates and diffs to fail on drift
- **Firmware send-by-ID helper** — `rurp_log_id(msg_id, param_bytes, param_count)` replaces existing `rurp_log(LOG_*_MSG, char*)`. Eliminates per-call PROGMEM string overhead
- **Host decoder** — `serial_comm.py` reads ID + param bytes, looks up format + shape in generated catalog, formats for display/logging
- **Scope: all firmware logs** — every `OK:`, `INIT:`, `MAIN:`, `END:`, `INFO:`, `WARN:`, `ERROR:` message is migrated; only the `DATA:` binary read-payload stream stays untouched
- **Phased migration** — Phase A: infrastructure (no removals). Phase B: convert error/info call-sites. Phase C: convert state-machine prefixes. Phase D: delete old log macros + measure final flash savings

**Constraints (locked at milestone start):**
- **Lockstep upgrade**: firmware + host upgrade together; firmware version bump enforces; no fallback to old text format
- **1-byte IDs**: 0–255 distinct messages
- **Raw byte array params**: catalog declares each ID's parameter shape; firmware sends bytes, host decodes per shape
- **English only**: single catalog, no localization plumbing
- **CI drift gate**: generated files committed to both sub-repos; CI regenerates and asserts no diff

**Out for v1.2** (deferred):
- `DATA:` binary payload stream — already optimal raw binary; only the prefix marker would change, not worth the protocol-parser churn
- v1.1 Phase 4 (FM1608 byte-0 hardware bug) — parked; needs different Uno board to unblock; will be resolved in a follow-up patch or folded into v1.2 close
- v1.1 Phase 5 (milestone close) — happens after v1.2 ships and the FM1608 unblock lands
- Localization (multi-language catalog)
- Compressing the `DATA:` prefix or other state-machine framing tokens

## Vision

Replace the current guessing-based chip type mapping with an explicit, protocol-driven architecture where every chip in the database has a known, correct programming algorithm — and the firmware executes exactly that algorithm.

## Current State (v1.0)

The algorithm-first contract is now load-bearing. `chip_database.json`
carries 743 chips with explicit `algorithm` integer = upstream `protocol_id`;
the wire JSON transmits it; `memory.cpp::configure_memory` dispatches a
protocol-prefix `if-return` block for every entry in `KNOWN_PROTOCOLS`
(0x05/0x06/0x07/0x08/0x0B/0x0D/0x0E/0x10/0x27/0x28/0x29/0x35/0x39) to one of
five handlers (`configure_eprom`, `configure_flash3`, `configure_flash_intel`,
`configure_eeprom28c`, `configure_sram`). Legacy `type`-byte enum dispatch
is retained only as a fallback for user-override DB entries.

**What works today (verified):**
- `firestarter write -e W27C512` (UV-EPROM 0x07) — verified by Phase 12 `check_dispatch.py` PASS + Unity dispatch tests
- `firestarter write -e AM29F040` / `SST39SF040` (AMD-style flash 0x06) — sector erase + chip erase
- `firestarter write -e AT28C256` (EEPROM 0x0D, includes 5V SDP-disable + DQ7-polling) — Phase 13 override routes 23 mis-tagged AT28C-family chips to safe handler
- `firestarter write -e 6116` (SRAM 0x0E/0x27/0x28/0x29) — safe no-op stub (no VPP regulator engagement on 5V parts)
- `firestarter info <chip> --adapter` — DIP-mirrored pin-to-signal table
- `python tools/build_db.py` — single canonical pipeline; fetches `infoic.xml` from upstream minipro at runtime

**What is partially supported:**
- `firestarter write -e AM28F010` (Intel-flash 0x10) — code path works but does
  not perform the pre-pulse VPP ADC compare REQ-SAF-01 requires "for every chip".
  See Known Gaps in `.planning/MILESTONES.md`.

## The Core Problem (resolved by v1.0)

The original system had a broken data pipeline that lost minipro's
authoritative `protocol_id`. v1.0 restores the chain end-to-end:

1. `protocol_id` from `infoic.xml` → `algorithm` integer in
   `minipro_complete_db.json` (no guessing, no re-derivation)
2. `algorithm` integer in JSON over the 250000-baud serial protocol
3. `firestarter_handle_t.algorithm` in firmware → `memory.cpp::configure_memory`
   protocol-prefix dispatch
4. Correct handler executes correct pulse timing and VPP routing per chip family

## What Must Be TRUE — Validated by v1.0

1. ✓ **minipro `protocol_id` is the authoritative source** — v1.0 (verified by
   `check_dispatch.py` across 743 chips; no guessing fallback in non-user-override path)
2. ✓ **An explicit `algorithm` field is transmitted over serial** — v1.0
   (`firestarter_handle_t.algorithm` parsed and propagated; legacy `type` retained as fallback)
3. ✓ **Firmware dispatches on `algorithm`, not `type`** — v1.0 (handlers
   implemented: configure_eprom, flash3, flash_intel, eeprom28c, sram)
4. ✓ **Database pipeline is deterministic** — v1.0 (single `build_db.py`;
   byte-identical regeneration on stable upstream XML; REQ-DB-05)
5. ✓ **DIP 24/28/32 packages fully covered** — v1.0 (filter clean; 743 chips
   across 27xx UV-EPROM, 29xx/39xx Flash AMD, Intel Flash, parallel EEPROM, SRAM)

## The One Thing That Must Work — ✓ Validated

A W27C512, a 29F040, an SST39SF040, and a 28C256 are all dispatched to
their correct algorithm from the database (not guessed). Hardware verification
on a physical RURP shield is deferred to a v1.1 hardware-test pass.

## Out of Scope (audit after v1.0)

- SMD packages, ICSP/serial interfaces, PLCC adapters — still out (no RURP support)
- MCU, PLD, logic device types — still out
- Any protocol outside minipro's DIP parallel memory types — still out
- GUI or web interface — still out
- 6.5V VCC NMOS programming — still out (RURP fixed 5V VCC; CMOS variants cover in-scope chips)
- Binary wire format replacing JSON — still out (per-operation overhead trivial)
- Full-image CRC32 — still out (per-chunk XOR sufficient over local USB serial)

## Approach (as built)

- **Database layer:** `build_db.py` (formerly `parse_db_2.py`) is the canonical
  pipeline; fetches `infoic.xml` from upstream minipro at runtime; outputs
  `algorithm` integer via direct `protocol_id` mapping with one documented
  override (Phase 13 WARNING-5: DIP28_2764 + 0x07 + Flash/EEPROM → 0x0D)
- **Wire protocol:** `algorithm` integer added to JSON command alongside
  `type` (semantically primary; type retained as fallback for user-override
  entries that pre-date the algorithm field)
- **Firmware:** `memory.cpp::configure_memory` dispatches a protocol-prefix
  `if-return` block for every `KNOWN_PROTOCOLS` entry; legacy mem_type chain
  preserved only as the last fallback
- **Pinouts:** `pinouts.json` is the physical layer; `static-high-pins` →
  `static_high_mask` end-to-end for tied-high pins (no firmware hardcodes)

## Key Decisions

| Date       | Decision                                                                                                                                                                                                                                   | Outcome  |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| 2026-05-08 | Database source = minipro `infoic.xml` via `build_db.py` (not hand-curated)                                                                                                                                                                | ✓ Good   |
| 2026-05-08 | Wire protocol = new explicit `algorithm` integer; `type` retained as legacy fallback                                                                                                                                                       | ✓ Good   |
| 2026-05-08 | Firmware dispatch = protocol-prefix `if-return` block per KNOWN_PROTOCOLS, mem_type chain only for legacy entries                                                                                                                          | ✓ Good   |
| 2026-05-08 | Packages in scope = DIP 24, 28, 32 only                                                                                                                                                                                                    | ✓ Good   |
| 2026-05-08 | Hardware = RURP shield, fixed 5V VCC, 19-bit address bus (512KB max), 8-bit data                                                                                                                                                           | ✓ Good   |
| 2026-05-11 | Phase 12: BLOCKER-1 + BLOCKER-2 closed at three layers (firmware dispatch + Python `_ALGO_MEM_TYPE` table + `build_db.py` SRAM tagging) rather than a single point-fix                                                                     | ✓ Good   |
| 2026-05-11 | Phase 13: WARNING-5 fixed at data layer (inline override in `build_db.py`) instead of firmware switch — preserves "algorithm is authoritative" contract while routing around upstream minipro classification error for 23 5V EEPROMs      | ✓ Good   |
| 2026-05-11 | Wire JSON `"vpp"` key carries millivolts (was volts) — name overloaded                                                                                                                                                                     | ✓ Resolved (Phase 2 WIRE-01) |
| 2026-05-11 | Phases 01-10 ship without formal `VERIFICATION.md` files (independent verification via INTEGRATION-CHECK + Phase 12 regression scan)                                                                                                       | ⚠ Revisit (retro `/gsd-validate-phase` runs in v1.1) |
| 2026-05-11 | Intel-flash write path ships without pre-pulse VPP ADC compare (REQ-SAF-01 partial — 39 chips affected)                                                                                                                                     | ✓ Resolved (Phase 1 SAF-04) |
| 2026-05-12 | Phase 1 closes SAF-04 (Intel-flash pre-pulse VPP ADC compare) + SAF-05 (AT28C A9-12V chip-id forward-compat) + SAF-06 (Unity coverage on `[env:native]`). Code review surfaced and fixed a regulator-leak regression on the VPP error path. | ✓ Good   |
| 2026-05-12 | Phase 2 closes WIRE-01 (atomic `"vpp"`→`"vpp_mv"` wire-key flip), CLEAN-01 (`minipro_complete_db.json`→`chip_database.json` rename + D-04 internal `vpp_volts` rename), CLEAN-02 (minipro attribution scrub: 6→1 host, 2→0 firmware), WIRE-02 (`check_dispatch.py` per-chip wire round-trip: 743/743 PASS). Layered `vpp` semantics: wire=`vpp_mv`(mV int), internal=`vpp_volts`(V float), upstream-schema READ preserved per D-08-compat. Phase 11 packaging-metadata drift also fixed (`pyproject.toml`/`MANIFEST.in` aligned to actual shipping files). | ✓ Good   |
| 2026-05-18 | v1.1 paused at 80% (Phase 4 hardware-validation in progress, FM1608 byte-0 bug parked) to start v1.2 immediately — Leonardo flash at 98.7% is blocking further firmware iteration, so logging rework jumps the queue. | — Pending |
| 2026-05-18 | v1.2 wire-format design: 1-byte message IDs + raw parameter byte arrays; catalog declares per-ID parameter shape (e.g. `[u16, u24]`). Firmware/host catalogs both codegenerated from a single canonical source. Generated files committed; CI runs `<regen> && git diff --exit-code` as drift gate. Lockstep upgrade — no backward compat to text-format firmware. | — Pending |

## Context

- **Tech stack:** Python 3 CLI host (pip package `firestarter`, JSON-over-serial
  at 250000 baud) + Arduino C++ firmware (PlatformIO, targets `uno` + `leonardo`,
  RURP shield)
- **Repo structure:** Meta-repo + 2 sub-repos (`firestarter/` firmware,
  `firestarter_app/` Python). Meta-repo tracks `.planning/` and `.claude/` only;
  sub-repos are pointer-bumped commits
- **Database state:** 743 chips post-v1.0 across DIP24/28/32. Algorithm
  histogram: 0x05=27, 0x06=190, 0x07=214, 0x08=127, 0x0B=53, 0x0D=41, 0x0E=20,
  0x10=39, 0x27=2, 0x28=10, 0x29=20 (totals 743)
- **Verified families (structural):** UV-EPROM (W27C512), Flash AMD (29F040),
  Flash Intel (28F010 minus VPP-ADC gap), EEPROM (AT28C256 via Phase 13
  override), SRAM (6116-class via safe stub)
- **Known gaps for v1.1:** see `.planning/MILESTONES.md` "Known Gaps" section
  (Intel-flash VPP ADC, retroactive VERIFICATION.md for phases 01-10, WARNING-2
  forward-compat, WARNING-3 wire-key naming, WARNING-4 test-script drift)

## Constraints

- Arduino Uno: 512-byte serial data buffer (affects chunked transfer sizing in `eprom_operations.py`)
- Arduino Leonardo: 1024-byte buffer
- Hardware calibration (R1/R2, board revision) persisted in EEPROM via `rurp_configuration_t`
- Constants/flag bits duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h` — must change together

## Sub-Repos

- `firestarter_app/` — Python host CLI, database pipeline, serial protocol
- `firestarter/` — Arduino firmware, algorithm implementations

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---

*Last updated: 2026-05-18 — v1.2 Phase 6 (Logging Infrastructure) complete: canonical message catalog + deterministic codegen + firmware `rurp_log_id` helper + host byte-stream decoder + CI drift gates across three repos. Both log paths coexist (LMIG-01). Leonardo Flash unchanged at 98.7% (380 B free) — additive code is linker-dormant until Phase 7 converts call-sites.*

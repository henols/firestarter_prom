# Project: Firestarter — Protocol-Aware Programming Architecture

**Created:** 2026-05-08
**v1.0 shipped:** 2026-05-11
**v1.1 status:** Parked at 80% (Phase 4 hardware-validation open — FM1608 byte-0 bug requires a different Uno board to unblock; see `.planning/debug/fm1608-fresh-chip-baseline.md`)
**v1.2 shipped:** 2026-05-19 (Message-ID Logging Rework — Leonardo Flash 98.7% → 85.4%, firmware 3.0.0-dev)
**v1.3 status:** Paused 2026-05-20 (hardware-gated — Phase 11 coverage matrix shipped + Phase 12 Wave 0 scaffold committed; bench plans 12-01/02/03 + Phase 13 + Phase 14 await operator hardware. Resume: `/gsd-execute-phase 12 --wave 1 --interactive`)
**v1.4 shipped:** 2026-05-20 (Beta & Pre-release Deployment Pipeline — 6 phases, 16/16 requirements)
**v1.5 shipped:** 2026-05-21 (Arduino Uno ATmega328PB Board Support — 5 phases, 15/15 requirements; ship tag `3.0.0b4`; bench-validated on operator's 328PB-Uno via `urclock` bootloader). Three open backlog items carried forward to v1.6 — see MILESTONES.md.
**v1.6 status:** RESUMED 2026-05-26 (after v1.7 close + Phase 27 re-open closure via Plan 27-05). Phase 28 re-iterated 2026-05-26 — split-scope: Plan 28-03 reverted `437339b6` (PORTx-clear) atomically with D-06 footer; Plan 28-04 (conditional second revert of `4f205e58`) stays parked drafted-but-not-executed. Re-iteration verification PASSED 5/5 desk-side (revert clean, prune clean, Axis 4 `.hex` SHA identity table holds, audit-trail guards intact, ROADMAP annotated). Status: `human_needed` — FIX-03 bench-side carries to Phase 29 v2 (sideload `firestarter/v1.6-read-bug` HEAD `efd203a` to Leonardo + N=5 consistency-check). Phase 30 still BLOCKED on Phase 29 v2. Original 64KB read-bug + uno328pb pre-existing issue deferred to v1.8 per D-10v2.
**v1.7 status:** STARTED 2026-05-22 — RURP Shield Hardware Investigation & Version Detection (catalog all RURP shield revisions, codify silkscreen labels into code-side aliases, document per-rev capabilities + electrical differences, design shield-version-detect resistor + firmware ADC read so future hardware-touch work is grounded in known-good schematics instead of operator memory).

## Current Milestone: v1.7 RURP Shield Hardware Investigation & Version Detection

**Goal:** Produce a versioned, authoritative reference for every known RURP shield revision (Rev 0 → Rev 2.2 + any others recoverable from upstream git history) — silkscreen text, electrical/mechanical schematic, label-to-code-alias map, per-rev capabilities matrix, inter-rev difference table — and design the next-rev hardware (resistor divider into an ADC pin) + firmware change that lets the board report its silkscreen rev programmatically. Ground future hardware-touch work in known-good shield schematics rather than ask-the-operator memory.

**Why now:** v1.6 Wave B FAIL burned two bench attempts on chip-swap diagnostics to disambiguate chip-state from board/shield/firmware. Future RCA passes (including v1.6's Phase 27 re-open) need a labeled schematic + per-rev capability table to design instrumented A/B experiments cleanly. Memory `user_shield_revisions` explicitly notes the EEPROM `hw_revision` byte can't distinguish operator's Rev 2.2 / Rev 2.0 / modified Rev 0 — this milestone closes that ask-the-operator loop.

**Target features:**
- Catalog all known RURP shield revisions from upstream `AndersBNielsen/Relatively-Universal-ROM-Programmer/hardware` (current revs on `main`; older revs Rev 0 + Rev 1 mined from git history)
- Per-rev silkscreen version-string extraction (the human-readable rev marker)
- Per-rev silkscreen label inventory → code-side descriptive alias map (e.g. silkscreen `VPP_EN` → alias `PIN_VPP_REGULATOR_ENABLE` usable in firmware + host)
- Per-rev capabilities matrix (chip families supported, max VPP, max VCC, address-bus width, supported algorithms)
- Inter-rev electrical/mechanical difference table (pinout, voltage divider values, VPP regulator wiring, jumpers, control-line routing, known rework hacks)
- Schematic-delta design for next-rev shield (likely Rev 2.3): resistor divider into an Arduino ADC pin so firmware can read silkscreen-rev programmatically
- Firmware change: ADC read at boot + lookup-table mapping ADC voltage band → silkscreen-rev string → reported on handshake; backward-compat fall-through for pre-detect-resistor boards (Rev 0 / 2.0 / 2.2 → ADC reads floating/grounded → firmware reports `rev_unknown` + falls back to operator-confirmed `hw_revision` byte)

**Locked decisions (v1.7 start, 2026-05-22):**

- **Scope:** Documentation-first milestone with one schematic-delta + one firmware-detect-plumbing patch. Five phases; investigation + alias-mapping + version-detect design + firmware plumbing + close.
- **Out of scope:** Fixing the v1.6 read-bug (still v1.6 territory; resumes after v1.7); new chip support; new MCU board target; physical PCB manufacturing of the new rev (design-only, operator orders/fabricates separately); EEPROM `rurp_configuration_t.hw_revision` byte semantics (preserved as legacy fall-back; no breaking change).
- **Phase numbering:** continues from v1.6 last planned phase 30 → v1.7 starts at **Phase 31**. No `--reset-phase-numbers`.
- **Branch model:** Per `feedback_branching` memory — `v1.7-shield-investigation` branches in all 3 repos. Meta-repo branches off `main`. Sub-repos branch off current `beta` tips (post-v1.5 ship, since v1.6 sub-repo branches are mid-iteration and the firmware-detect patch needs a clean substrate). Promote sub-repos → `beta` only after Phase 34 firmware-detect lands; `beta` → `main` only after operator confirms firmware reports correctly on at least one bench-present rev.
- **Definition of done:** `.planning/v1.7-SHIELD-REVS.md` (or equivalent — fixed at execution time) is the canonical reference — every rev's silkscreen-version string + label inventory + capabilities matrix is captured, every silkscreen label is mapped to a code-side alias, firmware applies the alias scheme, and the next-rev schematic delta + firmware ADC-detect plumbing are committed (without requiring physical fabrication for the firmware to compile + boot cleanly on existing boards).
- **GATE-1.7 (non-regression):** No firmware behavior change on existing boards (Rev 0 / 2.0 / 2.2 with no detect resistor): handshake still reports the operator-configured `hw_revision` byte; chip programming + read paths byte-identical to v1.6 baseline. The label-alias migration is name-only — same wire format, same firmware behavior, same compiled artifact sizes (modulo trivial symbol-name drift).
- **Operator hardware on hand:** Rev 2.2, Rev 2.0, modified Rev 0 (with hardware-bug-A/B rework) — all three available to photograph, probe, and capture silkscreen text from. Per memory `feedback_chip_out_before_sideload`: chip OUT of socket before any sideload during this milestone's firmware work. Per memory `feedback_verify_port_identity_each_task`: verify `controller:` identity per port at every task start.

## v1.6 Archive: Fix the Read Bug — ⏸ Paused 2026-05-22 (Wave B FAIL — milestone re-opens pending v1.7 substrate)

**Status:** Paused at the Phase 27 RCA re-open boundary. Phases 26 + 27 + 28 shipped 2026-05-21 — REPRO closed (consistency-check CLI + cross-board pre-fix baseline), RCA narrative + introducing-commit citation committed to `.planning/v1.6-EVIDENCE.md`, initial Leonardo `PORTx-clear` mirror fix + `_NOP()` settling landed on `firestarter/v1.6-read-bug`. Phase 29 Wave A (regression check) shipped 2026-05-22 AM. Phase 29 Wave B Attempt 2 closed FAIL 2026-05-22 PM: chip-swap diagnostic isolated Leonardo + uno328pb read-path regression to the Phase 28 fix commits — proven-good chip from Uno reads 83.8% zero-bytes + 5 distinct SHAs across N=5 consistency-check on Leonardo (`/dev/ttyACM1`, Modified Rev 0 + voltage-divider mod). Uno code path unaffected. **D-07 explicitly triggers FAIL milestone-reopens.**

**Resume from:** `/gsd-plan-phase 27 --gaps` once v1.7 ships the schematic + rev-detect plumbing. First disambiguation experiment per the Phase 29-02 SUMMARY hand-off: pre-Phase-28-firmware A/B test — build `firestarter/v1.6-read-bug~2`, sideload to Leonardo, re-probe. With v1.7's labeled-schematic + per-rev capability table in hand, the Phase 27 re-open can design instrumented A/B builds knowing exactly which silkscreen rev is on the bench at each step.

**Phase directories preserved:** `.planning/phases/26-*/`, `.planning/phases/27-*/`, `.planning/phases/28-*/`, `.planning/phases/29-*/` remain in place (not archived). v1.7 phase numbering continues at 31 to avoid collision when v1.6 resumes (Phase 30 close still reserved).

## v1.6 Original Goal (preserved for resume):

**Goal:** Root-cause and fix the 64KB streaming-read byte-jitter bug surfaced by Phase 24 bench rigor — restore byte-identical full-chip read-back across `uno`, `leonardo`, and `uno328pb` so verify operations and BENCH-02 close are meaningful again.

**Target features:**
- Reproduce 64KB read-jitter on `uno` and `leonardo` (not just `uno328pb`); confirm pre-existing latent bug, not a v1.5 regression
- Isolate firmware-side vs host-side (1KB `dev read` jitters at lower rate — already points to firmware per-chunk send code)
- Identify the exact root cause with concrete evidence (instrumented firmware build, code-path bisection, or scope/logic-analyzer trace)
- Land fix that produces byte-identical 64KB reads across N consecutive invocations on all 3 boards (`uno`, `leonardo`, `uno328pb`)
- Operator bench-validates the fix on 328PB-Uno + at least one other board; Phase 24 BENCH-02 closes as side effect
- Document root cause + fix in `.planning/v1.5-BENCH-RESULTS.md` follow-up + commit-message narrative

**Locked decisions (v1.6 start, 2026-05-21):**

- **Scope:** Fix one specific bug — the 64KB streaming-read byte-jitter (~57.8% jitter rate at 64KB, ~0.1% at 1KB) affecting all three controllers. Cross-board verification + root-cause analysis + fix + bench validation, end-to-end.
- **Out of scope:** `w27c512-eeprom-misclassification` (separate HIGH-priority backlog — different bug class, chip-database routing, deferred to its own milestone or grouped later); `avrdude-mcu-detection-fallback` (low priority); any new chip support; any new board target; any v1.1 FM1608 carryover.
- **Phase numbering:** continues from v1.5 last phase 25 → v1.6 starts at Phase 26. No `--reset-phase-numbers`.
- **Branch model:** Per operator standing instruction (memory `feedback-branching-firestarter-milestones`): all v1.6 work lands on `v1.6-read-bug` branches in all 3 repos (meta + firestarter + firestarter_app). Sub-repos branch off `beta` (current v1.5 tips). Promote to `main` only after operator green on bench cycle.
- **Definition of done:** `firestarter read <chip> file.bin` invoked N consecutive times against the same physically-static chip returns byte-identical SHA-256 hashes on all 3 boards. Plus `dev read -s 1024` byte-identical across consecutive calls (the lower-rate jitter must also resolve, otherwise the root cause isn't truly fixed).
- **Pre-existing-bug regression policy:** Once root cause is known, retroactively check git history — if the regression has a clear introducing commit, document it (helps Future-Us not reintroduce); but do not pursue blame.
- **GATE-1.6 (non-regression):** Write path stays unaffected (Phase 24 already proved write commits correctly; the fix should not perturb write timing). Existing `firestarter_uno.hex`, `firestarter_leonardo.hex`, `firestarter_uno328pb.hex` artifact sizes within reasonable drift; any size delta documented in fix-commit message.

## v1.5 Archive: Arduino Uno (ATmega328PB) Board Support — Shipped 2026-05-21

**Goal:** Ship `uno328pb` as a third first-class firmware target (alongside `uno` and `leonardo`) — end-to-end from PlatformIO env through stable + beta release artifacts (`firestarter_uno328pb.hex`), through host-CLI installer integration, to a bench-validated write→read-back→verify cycle on the operator's plugged-in ATmega328PB Uno board.

**Target features:**
- PlatformIO `[env:uno328pb]` + custom `boards/uno328pb.json` board definition; firmware compiles for ATmega328PB
- Firmware reports `uno328pb` on handshake so host CLI can match the right `.hex` artifact
- Stable + beta release pipelines publish `firestarter_uno328pb.hex` artifact (additive — `uno` + `leonardo` artifacts byte-identical to pre-v1.5; GATE-1.5)
- Host CLI's `firestarter fw -i` (stable) and `firestarter fw -i --pre` (beta) flash the 328PB board when device reports `uno328pb`; non-regression on `uno` + `leonardo` installs
- Bench-validated write→read-back→verify cycle on operator's 328PB-Uno + RURP shield (at least one representative EPROM, e.g. W27C512)
- Documentation: firmware + app READMEs + meta-repo release procedures cover the third board

**Branch model:** Work branches off `beta` in both sub-repos (per operator instruction). After bench-green, merge `beta` → `main` follows the v1.4-RELEASE-PROCEDURES.md beta→stable promotion pattern. No tag-driven path.

**Locked decisions (v1.5 start, 2026-05-20):**

- **Scope:** Add `uno328pb` as a third firmware target. Use existing v1.4 beta/stable plumbing — no pipeline redesign. The release pipelines emit one additional `.hex` artifact (per-board matrix grows from 2 → 3); the host CLI's `firestarter_{board}.hex` lookup naturally matches when firmware handshake reports `uno328pb`.
- **Out of scope:** 328PB extra peripherals (USART1, TWI1, SPI1, Timer3/4, PE0–PE3 pins) — Firestarter only uses 328P-common I/O; bootloader flashing (operator provisions the board separately); host-side VID/PID auto-detect (firmware-handshake report is authoritative); RURP shield rev changes; new chip support; CMOS bench resume (still v1.3 territory).
- **Board-ID strategy:** Custom PIO `boards/uno328pb.json` so `board = uno328pb` in `[env:uno328pb]`. `name_firmware.py` already derives the artifact name from `env.GetProjectOption("board")`, so this produces `firestarter_uno328pb.hex` with no codegen change, and the host's `firestarter_{board}.hex` lookup needs zero board-name translation.
- **MCU framework:** MiniCore (`platform = MCUdude/MiniCore`) is the established Arduino-framework support for ATmega328PB. Use it as the platform; pin definitions stay Arduino-Uno-compatible for Firestarter's I/O footprint.
- **Buffer size:** Use 512 B `DATA_BUFFER_SIZE` (same as `uno`); 328PB has the same 2 KB SRAM as 328P. Only revisit if compiled binary runs cold against the buffer floor.
- **Handshake-name source of truth:** `RURP_BOARD_NAME=\"uno328pb\"` set per-env in `platformio.ini` (mirror of `uno` and `leonardo`); firmware emits this string in the `MSG_OK_FW_HANDSHAKE` payload's `<board>` slot so host's `firmware.py:check_current_firmware` parses it identically to the existing two boards.
- **Bench validation chip:** Operator confirmed a 328PB-Uno is plugged in. Bench session validates against at least one representative EPROM (default W27C512, swap if operator's chip kit differs). Same `firestarter write/read/verify` flow as the regular Uno — algorithm dispatch is firmware-internal and unchanged by the MCU port.
- **GATE-1.5 (non-regression):** `firestarter_uno.hex` and `firestarter_leonardo.hex` are byte-identical to pre-v1.5 outputs (modulo unavoidable version-string drift from `update_version.py`). Stable-installed app's `firestarter fw -i` defaults still flash the matching artifact for `uno`/`leonardo`-reporting devices.
- **Branch flow:** Both sub-repos cut working branches off `beta` (current tip 5fd751e in both sub-repos as of 2026-05-20). Cut `3.0.1bN` (or appropriate next pre-release) for the first bench-validated cut. Promote `beta` → `main` and bump to stable (`3.0.1`) only after operator green on the 328PB bench cycle. Meta-repo's `.planning/` work proceeds on `main` per existing convention.

## v1.4 — Beta & Pre-release Deployment Pipeline — Shipped 2026-05-20

Added a parallel beta / pre-release deployment channel across both Firestarter sub-repos
without touching the existing main → stable pipelines. Branch-driven trigger (`beta` branch
in each sub-repo) wired to new beta workflows that emit PEP 440 / matching pre-release version
strings, publish PyPI pre-release wheels (installable via `pip install --pre`), and create
GitHub Pre-releases with `make_latest: false` carrying per-board `firestarter_*.hex` artifacts.
App and firmware ship locked-step on a single `BETA_VERSION` operator input. Beta-installed app
grows three new CLI flags (`--pre`, `--firmware-version`, `firmware list`) plus a PEP 440-safe
version comparator; stable-installed app's `firestarter --install` defaults remain byte-identical
to pre-v1.4 (GATE-01 + GATE-02 preserved). The locked-step coordination mechanism uses
manually-paired beta-branch pushes with an explicit `BETA_VERSION` input — documented in
`.planning/v1.4-RELEASE-PROCEDURES.md` and proven via `.planning/phases/15-*/lockstep-dryrun-fixture.sh`.

See `.planning/MILESTONES.md` for the full delivery summary.
Per-phase artifacts archived under `.planning/milestones/v1.4-phases/` (via `.planning/v1.4-archive.sh`).

## v1.3 — CMOS EPROM Family Hardware Validation — ⏸ Paused 2026-05-20 (hardware-gated)

**Status:** Paused at the autonomous/hardware boundary. Phase 11 (Coverage Matrix & DB Inconsistency Audit) shipped clean 2026-05-19 — `.planning/v1.3-COVERAGE-MATRIX.md` + 78-entry defect ledger + all-algorithms wide-scan extension (`.planning/v1.3-COVERAGE-MATRIX-ALL.md` with 137 findings across all 11 DB algorithms) delivered. Phase 12 Wave 0 (desk-side scaffold) committed 2026-05-20.

**Resume from:** `/gsd-execute-phase 12 --wave 1 --interactive` once operator has Uno + Leonardo + RURP shield + DIP-28 socket + scope + the BENCH-01/02/05 chips (W27C512, SST27SF512, W27C257) available.

**v1.4 resume-relevant context:** Phase 18 (Beta-Aware Firmware Downloader, shipped as part of v1.4) added new CLI flags that are directly useful when resuming v1.3 bench validation with pre-release firmware builds:
- `firestarter fw -i --pre` — installs the latest published pre-release firmware for the configured board (avoids manually locating a `.hex` URL).
- `firestarter fw -i --firmware-version X.Y.ZbN` — pins an exact pre-release firmware tag via the GitHub Releases API.
- `firestarter fw --list --pre` (or `--all`) — enumerates available firmware releases with version, channel (Stable/Pre-release), and asset URL.

These flags allow bench operators to install pre-release firmware builds via the app CLI without needing a stable PyPI release first — useful when cutting a bench-validation firmware build on a `beta` branch before promoting it to `main`.

**Why paused:** Operator does not have bench hardware available at this time. Phase 12 plans 12-01/02/03 are operator-on-bench (`autonomous: false`) — they cannot run without hardware. Auto-mode would silently auto-approve checkpoints without real evidence, producing fabricated BENCH-RESULTS rows — that's an integrity hazard the planner explicitly designed against. Cleanest action: pause v1.3, work on software-only v1.4 in the meantime.

**Phase directories preserved:** `.planning/phases/11-*/` and `.planning/phases/12-*/` remain in place (not archived). v1.4 phase numbering continues at 15 to avoid collision when v1.3 resumes.

## v1.2 — Message-ID Logging Rework — ✓ Shipped 2026-05-19

**Delivered:** Every firmware text-prefix log emit (`OK:` / `INIT:` / `MAIN:` / `END:` / `INFO:` / `WARN:` / `ERROR:` / `DEBUG:`) replaced with a 1-byte message-ID + raw-byte-param wire protocol driven by a canonical catalog in `tools/catalog/messages.toml`. Codegen emits C++ header for firmware + Python module for host; both regenerated and byte-identity-checked in CI. Old log helpers deleted; firmware 3.0.0-dev enforces lockstep upgrade.

**Headline result (LMIG-04):** Leonardo Flash 98.7% (28,292 B) → **85.4% (24,482 B)** — 3,792 B of new headroom on the tightest board. Uno 81.1% → 69.0%. Native tests 20/20 PASS, host pytest 29/29 PASS, hardware-bench verified on Uno + Leonardo with both verbose-mode INFO emits and SERIAL_DEBUG breadcrumb chains.

See `.planning/MILESTONES.md` for the full delivery summary. Per-phase artifacts live in `.planning/phases/06-09-*` (and will move under `.planning/milestones/v1.2-phases/` on next cleanup).

## Vision

Replace the current guessing-based chip type mapping with an explicit, protocol-driven architecture where every chip in the database has a known, correct programming algorithm — and the firmware executes exactly that algorithm.

## Current State (v1.0)

The algorithm-first contract is now load-bearing. `chip_database.json`
carries 734 chips with explicit `algorithm` integer = upstream `protocol_id`;
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
   `check_dispatch.py` across 734 chips; no guessing fallback in non-user-override path)
2. ✓ **An explicit `algorithm` field is transmitted over serial** — v1.0
   (`firestarter_handle_t.algorithm` parsed and propagated; legacy `type` retained as fallback)
3. ✓ **Firmware dispatches on `algorithm`, not `type`** — v1.0 (handlers
   implemented: configure_eprom, flash3, flash_intel, eeprom28c, sram)
4. ✓ **Database pipeline is deterministic** — v1.0 (single `build_db.py`;
   byte-identical regeneration on stable upstream XML; REQ-DB-05)
5. ✓ **DIP 24/28/32 packages fully covered** — v1.0 (filter clean; 734 chips
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
| 2026-05-18 | v1.1 paused at 80% (Phase 4 hardware-validation in progress, FM1608 byte-0 bug parked) to start v1.2 immediately — Leonardo flash at 98.7% is blocking further firmware iteration, so logging rework jumps the queue. | ✓ Good (decision validated by v1.2 ship at 85.4% Leonardo Flash on 2026-05-19; 3,792 B headroom restored) |
| 2026-05-18 | v1.2 wire-format design: 1-byte message IDs + raw parameter byte arrays; catalog declares per-ID parameter shape (e.g. `[u16, u24]`). Firmware/host catalogs both codegenerated from a single canonical source. Generated files committed; CI runs `<regen> && git diff --exit-code` as drift gate. Lockstep upgrade — no backward compat to text-format firmware. | ✓ Good (shipped v1.2 with 60 catalog entries + 41 DBG sub_ids; CI drift gate caught zero violations; lockstep upgrade via 3.0.0-dev FW major bump works cleanly) |
| 2026-05-19 | Post-Phase-9 polish: dropped `MSG_OK_FW_HANDSHAKE` per-command composite (P-04) in favour of plain `MSG_OK_READY` ack + 4 single-purpose INFO emits (FW/HW/PHYSICAL_HW/CMD) for verbose mode. Migrated `EXTRA_INFO_LOGGING` build-flag block to SERIAL_DEBUG-gated `DBG_*` sub_ids so verbose diagnostics ride the existing DEBUG channel. | ✓ Good (cleaner verbose-mode story; production wire-byte savings; bench-verified end-to-end) |
| 2026-05-19 | v1.2 milestone closed with 4 hardware-pending UAT items deferred (Phase 8 SC#2/SC#3 + Phase 9 Plan 05 Task 3 chip-seated W27C512 UAT + v1.1 fm1608 debug carry-forward). LMIG-04 acceptance number already pinned via autonomous-side Phase 9 measurement; deferred items don't gate v1.2 ship. | ✓ Good (clean decision rationale; bundles for next bench session) |
| 2026-05-20 | v1.4 trigger model = branch-driven beta (push to `beta` triggers pre-release pipeline; push to `main` triggers stable pipeline). One trigger pattern across both pipelines; no tag-driven path. | ✓ Good (operator picks the branch, not a tag; mirrors current stable trigger shape exactly) |
| 2026-05-20 | v1.4 app channel = PEP 440 pre-release versions (`X.Y.ZbN`/`X.Y.ZrcN`) on the SAME PyPI index. TestPyPI explicitly deferred. Users opt in via `pip install --pre firestarter`. | ✓ Good (single source of truth; stable users unaffected; b3 published cleanly during E2E) |
| 2026-05-20 | v1.4 firmware channel = GitHub Pre-release with `prerelease: true` AND `make_latest: false`. `/releases/latest` API auto-filters pre-releases — preserves stable-installed `firestarter fw -i` (INST-01) without client-side logic. | ✓ Good (INST-01 non-regression proven by API filtering during 3.0.0b3 E2E; stable channel still pulls 2.0.7 verbatim) |
| 2026-05-20 | v1.4 lockstep mechanism = manually-paired beta-branch push with explicit `BETA_VERSION` input. Rejected alternatives: shared meta-repo VERSION file (cross-repo write coupling), cross-repo `repository_dispatch` (requires PAT with `repo` scope across both repos). | ✓ Good (no new cross-repo trust surface; operator-readable; lockstep-dryrun-fixture.sh proves byte-identity at 3.0.0b3) |
| 2026-05-20 | v1.4 scope amendment (after Phase 15 shipped): allow narrow CLI carve-out in app (Phase 18 INST-01..04) — `--pre`, `--firmware-version`, `firmware list` flags + PEP 440 comparator fix. Without these the published beta firmware would be uninstallable via the CLI. | ✓ Good (real-hardware flash from PyPI `--pre` install on Uno + Leonardo proven 2026-05-20 — half a feature without it) |
| 2026-05-20 | v1.4 close at b3 not b1: live cut surfaced 6 substrate defects (E2E-01..06) fixed in-place. Plus .pyc hygiene fix on top. Three sequential cuts (b1 → b2 → b3) instead of one — auto-increment validated as a side-effect. | ✓ Good (substrate hardened for future beta cuts; next cut should land clean) |
| 2026-05-20 | v1.4 ships unconventional default-branch fallout: meta-repo's de-facto main (`init/project-setup`) renamed to `main` at milestone close; 345 commits fast-forwarded; stale feature branches deleted. | ✓ Good (conventional repo state; no workflow references to old name; GitHub branch-rename redirects active for ~90d) |

## Context

- **Tech stack:** Python 3 CLI host (pip package `firestarter`, JSON-over-serial
  at 250000 baud) + Arduino C++ firmware (PlatformIO, targets `uno` + `leonardo`,
  RURP shield)
- **Repo structure:** Meta-repo + 2 sub-repos (`firestarter/` firmware,
  `firestarter_app/` Python). Meta-repo tracks `.planning/` and `.claude/` only;
  sub-repos are pointer-bumped commits
- **Database state:** 734 chips post-v1.0 across DIP24/28/32. Algorithm
  histogram: 0x05=27, 0x06=190, 0x07=212, 0x08=127, 0x0B=40, 0x0D=23, 0x0E=20,
  0x10=39, 0x27=2, 0x28=34, 0x29=20 (totals 734)
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

*Last updated: 2026-05-22 — v1.7 milestone started (RURP Shield Hardware Investigation & Version Detection). v1.6 PAUSED 2026-05-22 after Phase 29 Wave B FAIL (D-07 milestone-reopens) — chip-swap diagnostic isolated Phase 28 firmware as introducing a Leonardo + uno328pb read-path regression; Uno code path unaffected. v1.6 resumes after v1.7 ships its labeled-schematic + per-rev capability table + shield-version-detect firmware plumbing — those substrates let the v1.6 Phase 27 RCA re-open design instrumented A/B builds knowing exactly which silkscreen rev sits on the bench at each step. v1.7 is documentation-first: catalog Rev 0..2.2 from upstream `AndersBNielsen/Relatively-Universal-ROM-Programmer/hardware`, extract silkscreen labels, propose code-side aliases, build per-rev capability + difference matrices, design next-rev (Rev 2.3) shield-version-detect resistor divider + firmware ADC read with backward-compat fall-through for pre-detect-resistor boards. Five phases (31-35); branch model `v1.7-shield-investigation` in all 3 repos.*

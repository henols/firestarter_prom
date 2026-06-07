# Project: Firestarter — Protocol-Aware Programming Architecture

**Created:** 2026-05-08
**v1.0 shipped:** 2026-05-11
**v1.1 status:** Parked at 80% (Phase 4 hardware-validation open — FM1608 byte-0 bug requires a different Uno board to unblock; see `.planning/debug/fm1608-fresh-chip-baseline.md`)
**v1.2 shipped:** 2026-05-19 (Message-ID Logging Rework — Leonardo Flash 98.7% → 85.4%, firmware 3.0.0-dev)
**v1.3 status:** Paused 2026-05-20 (hardware-gated — Phase 11 coverage matrix shipped + Phase 12 Wave 0 scaffold committed; bench plans 12-01/02/03 + Phase 13 + Phase 14 await operator hardware. Resume: `/gsd-execute-phase 12 --wave 1 --interactive`)
**v1.4 shipped:** 2026-05-20 (Beta & Pre-release Deployment Pipeline — 6 phases, 16/16 requirements)
**v1.5 shipped:** 2026-05-21 (Arduino Uno ATmega328PB Board Support — 5 phases, 15/15 requirements; ship tag `3.0.0b4`; bench-validated on operator's 328PB-Uno via `urclock` bootloader). Three open backlog items carried forward to v1.6 — see MILESTONES.md.
**v1.6 shipped:** 2026-05-26 (Fix the Read Bug — ships as "diagnostic + revert" per D-17v2; 5 phases, 13 plans; 12/16 requirements DELIVERED; 4 DEFERRED to v1.8 with Bug A + Bug B pattern findings as RCA seed). Per Phase 29 v2 PASS_PARKED: Leonardo Modified Rev 0 returns to Phase 26 baseline shape (WORST=0.047% zeros vs 83.8% pre-revert); Phase 28 v1 PORTx-clear regression cleanly removed via revert; `_NOP()` settling preserved. Read-bug itself carries to v1.8.
**v1.8 shipped:** 2026-05-29 (Host CLI Structural Cleanup — 8 phases, 27 requirements DELIVERED + 3 VERIFIED-at-close; argparse → Click migration; flat layout preserved (no subpackage reorg); ruff + ruff-format + mypy strict on 8 modules + 70% coverage floor enforced in CI; 2 latent bugs fixed as INTENTIONAL BEHAVIOR CHANGE (BUG-1 `build_arg_flags`, BUG-2 except-clause split); ship tag `3.0.0b7` beta-only; v1.8-app-cleanup → beta + meta-repo → main; firmware sub-repo untouched at `beta@0bbe017`; read-bug carries to v1.9 with GATE-1.8d ring-fence intact).
**v1.7 shipped:** 2026-05-26 (RURP Shield Hardware Investigation & Version Detection — 5 phases; per-rev capability table + labeled schematics + shield-version-detect firmware plumbing). Substrate consumed by v1.6 Phase 29 v2 bench session + v1.8 RCA hand-off.
**v1.10 shipped:** 2026-06-07 (Serial Transport Hardening / COBS — 7 phases (49–55; 45–48 reserved for v1.9), 27 plans, 14/14 requirements; beta-only, stable `3.0.1` operator-gated/deferred to the v1.9 read-bug fix). Custom COBS `0x00` + CRC8 framing with automatic resync on **both** the data-block path and the host→fw JSON command channel; the 2 s `len_u16` timeout cascade is gone; transport proven byte-exact (operator-witnessed bench, Uno 512 B + Leonardo 1024 B, N=5 read + write read-back). uno328pb read instability **persists** on the hardened transport → recorded as transport-exoneration, NOT a hardware fix; RCA stays deferred to v1.9. Serial is now a settled variable for the resumed read-bug RCA.

## v1.10 Archive: Serial Transport Hardening (COBS) — Shipped 2026-06-07

v1.10 hardened the Arduino↔host serial transport to *provably byte-exact*, inserted **ahead** of the paused v1.9 read-bug RCA so serial corruption is ruled out as a confounder before the per-shield RCA resumes (v1.9 Phase 45+). The trigger was v1.9 Phase 48-01 flipping the COBS verdict DEFER → **ADOPT** (`.planning/v1.9-COBS-DECISION.md` §2): the old `[len_u16][xor][payload]` data-block framing desynced on a single corrupted `len_u16` byte until a 2 s timeout fired and stayed out of sync for the rest of the transfer.

**Delivered (14/14 requirements):** Custom **streaming COBS `0x00` + CRC8-CCITT** framing with automatic resync on **both** the data-block path (Phase 50) and the host→fw JSON command channel (Phase 51, breaking lockstep wire change — CRC8 verified before the JSON parser sees a byte). COBS `0x00` was chosen over SLIP `0xC0` via a conclusive SAFE-01 static proof (Phase 49). The 2 s timeout cascade is gone (recovery now ~1 ms for corrupt frames, a single bounded ~1 s inter-byte deadline for truncated frames). Decode-in-place fits the Uno ~545 B free-RAM ceiling — no second buffer (D-04); CRC8-CCITT poly 0x07 retained unchanged (D-05). Host-encode↔fw-decode byte-compatibility is pinned by a shared golden-vector catalog with round-trip suites + codegen drift gates in both repos (Phase 52). Even-block full-buffer transfers (Phase 54) + buffer-size advertisement relocated to the `MSG_OK_READY` u16 ack with a safe-512 default (Phase 55, reverses Phase 54 D-05). **Phase 53 bench (operator-witnessed):** N=5 read + write read-back byte-identical on clean Uno + Leonardo (Rev 2.0); resync proven on real hardware both directions/both fault forms; uno328pb read instability **persists** on the hardened transport → structured transport-**exoneration** verdict (NOT a per-shield fix). Bench evidence at `.planning/v1.10/bench-verification/SUMMARY.md`. Branch `v1.10-serial-transport-hardening` was stacked off the `v1.9-read-bug-rca` tip in all 3 repos (NOT off main/beta — stale at v1.8 close); merging v1.10 first also carries v1.9's unmerged commits forward.

See `.planning/MILESTONES.md` §v1.10 for the full delivery summary; ROADMAP archived at `.planning/milestones/v1.10-ROADMAP.md`; requirements at `.planning/milestones/v1.10-REQUIREMENTS.md`.

## Current Milestone: v1.9 — Read-Bug RCA + Fix (RESUMES — v1.10 shipped)

**Status:** ▶ RESUMES at Phase 45 now that v1.10 has shipped (2026-06-07). PAUSED 2026-06-01 at Phase 44 to insert v1.10 (above); STARTED 2026-05-29 (scope locked via `/gsd-new-milestone`); proposed 2026-05-26 at v1.6 close; renumbered v1.8 → **v1.9** on 2026-05-27 when the host-CLI cleanup took the v1.8 slot. **Progress at pause:** Phase 44 (Bug A RCA — Modified Rev 0) complete; Phase 48 plan 48-01 (COBS-01 evaluation) complete and the verdict flipped DEFER→ADOPT (this is what triggered v1.10). **Remaining:** Phases 45 (Bug B RCA), 46 (Fix Design & A/B), 47 (Acceptance Gate + backlog closures), plus Phase 48 plans 48-02 (TYPE-01) and 48-03 (milestone close). Phase dirs `44-*` and `48-*` preserved in `.planning/phases/`. **Resume:** `/gsd-plan-phase 45` once the hardened transport is merged. Hardware-gated; firmware sub-repo work expected from Phase 46 onward. The transport is now a settled, byte-exact variable — the methodological prerequisite v1.10 was inserted to establish.

**Why:** v1.6 closed with the original read-bug intentionally deferred per D-17v2 re-scope. Phase 29 v2 characterized the bug as two independent failure modes — Bug A (Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew, 63% BIT-RAISE) and Bug B (Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch + VPP=13.1V). v1.9 inherits the diagnostic (`firestarter dev consistency-check`), the 15-binary N=5 bench substrate at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`, the Phase 29 v2 H3 block in `.planning/v1.6-EVIDENCE.md`, the v1.7 labeled-schematic + per-rev capability table + shield-version-detect firmware plumbing, AND the v1.8 cleaned-up host read path (GATE-1.8d ring-fence intact — baseline binaries still valid) as the foundation for designing instrumented A/B fix candidates knowing exactly which silkscreen rev sits on the bench at each step.

**Target features (scope locked 2026-05-29):**
- RCA from the characterized hypotheses (Bug A signal-integrity, Bug B timing/voltage)
- Instrumented A/B fix candidates across Modified Rev 0 + Rev 2.0 + Rev 2.2 shields
- Re-iterate Phase 29 acceptance gate (N≥5 byte-identical reads across boards)
- Close VERIFY-01 (uno328pb byte-identity) + VERIFY-03 (1KB low-rate jitter) + VERIFY-04 (Phase 24 BENCH-02 closure)
- Evaluate COBS framing/resync on the serial data path (todo: PacketSerial assessed-not-adopted) as a data-path robustness angle — complementary to the hardware RCA, NOT a Bug A fix (Bug A is hardware upper-address jitter, not a framing fault)
- Lift `eprom_operations.py` mypy strict overrides (DEFERRED per Phase 42 D-07; lifted post-RCA when the read path can be touched freely)
- Phase numbering continues at Phase 44

**Operator next step:** requirements + roadmap being generated via `/gsd-new-milestone` (2026-05-29).

## v1.8 Archive: Host CLI Structural Cleanup (firestarter_app) — Shipped 2026-05-29

v1.8 is a pure-software structural cleanup of the `firestarter_app` Python host CLI. Per GATE-1.8 (a–e) "refactor + fix bugs found" non-regression contract: wire protocol byte-identical, end-user CLI surface preserved, firmware/app constant contract preserved via parity tests, host read path ring-fenced for the v1.9 RCA, full test suite green + entry point installs. 30/30 requirements closed: 27 DELIVERED (TEST-01..05 + TOOL-01..03 + STRUCT-01..05 + DATA-01..04 + SERIAL-01..03 + CLI-01..04 + ERR-01..03) + 3 VERIFIED-at-close (DOC-01 + DOC-02 + MS-01). Two latent bugs fixed as INTENTIONAL BEHAVIOR CHANGEs: BUG-1 `build_arg_flags` truthiness check (Phase 41 Plan 41-01 commit `6241dba`); BUG-2 `eprom_operations._run_state_machine` except-clause split (Phase 42 Plan 42-01 commit `04a0c13`). `main.py` trimmed 932 → 35 lines; `cli_handlers.py` houses 14 `@cli.command()` + `dev` group with 4 sub-commands. Ship tag `3.0.0b7` beta-only (stable `3.0.1` deferred to v1.9 read-bug fix per D-17v2 carry-forward). Firmware sub-repo untouched (host-only milestone; firmware stays at `beta@0bbe017` from v1.6 close).

See `.planning/MILESTONES.md` §v1.8 for the full delivery summary. Per-phase artifacts archived under `.planning/milestones/v1.8-phases/` (via `.planning/v1.8-archive.sh` in Plan 43-02). Coverage table archived at `.planning/milestones/v1.8-REQUIREMENTS.md` (30 rows with per-requirement disposition column). v1.9 hand-off: read-bug (Bug A + Bug B) carries forward with GATE-1.8d ring-fence intact; 15 N=5 W27C512 baseline binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` remain valid because `_read_and_parse_lines` body is byte-identical pre/post v1.8.

## v1.6 — Fix the Read Bug — ✓ Shipped 2026-05-26 (diagnostic + revert per D-17v2)

v1.6 ships as a course-correction milestone. Phase 29 v1 Wave B FAIL revealed that Phase 28 v1's `437339b6` PORTx-clear introduced a Leonardo + uno328pb read-path regression (83.8% zero-bytes); Plan 27-05 RCA re-open confirmed dual-cause disposition (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb hardware). The course-correction landed: `437339b6` reverted via `ea25174` (clean removal of the regression); `4f205e58` `_NOP()` settling preserved (Plan 28-04 parks); Phase 29 v2 PASS_PARKED gate emission (Leonardo Modified Rev 0 returns to Phase 26 baseline shape — WORST=0.047% zeros across N=10). The original 64KB streaming-read byte-jitter bug is NOT fixed — characterized as Bug A (Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew) + Bug B (Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch + VPP=13.1V) and carried to v1.8 as the RCA starting hypothesis substrate.

See `.planning/MILESTONES.md` §v1.6 for the full delivery summary. Per-phase artifacts archived under `.planning/milestones/v1.6-phases/` (via `.planning/v1.6-archive.sh` in Plan 30-02). v1.8 RCA substrate ready: 15 N=5 W27C512 binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`; pattern findings in `.planning/v1.6-EVIDENCE.md` Phase 29 v2 H3 block; canonical close narrative in `.planning/phases/29-multi-board-bench-verification/29-04-SUMMARY.md` (or post-archive `.planning/milestones/v1.6-phases/29-multi-board-bench-verification/29-04-SUMMARY.md`); v1.8-deferred bug todo at `.planning/todos/pending/v1.8-seed/large-read-data-jitter-uno328pb.md`. v1.7 substrate (`.planning/v1.7-SHIELD-REVS.md` per-rev capability table + labeled schematics + shield-version-detect firmware plumbing) provides v1.8 the foundation for designing instrumented A/B fix candidates knowing exactly which silkscreen rev sits on the bench at each step.

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
| 2026-06-01 | v1.9 PAUSED at Phase 44; v1.10 Serial Transport Hardening (COBS) inserted ahead of it. Rationale: make the serial transport provably byte-exact FIRST so it is ruled out as a read-bug confounder before the per-shield RCA (Phase 45+) resumes. v1.9 phase dirs (44, 48) preserved; phases 45–48 reserved; v1.10 numbers from Phase 49. | ✓ Good (v1.10 shipped 2026-06-07; transport exonerated as a variable; v1.9 resumes at Phase 45) |
| 2026-06-01 | v1.10 branch model = **stacked** off the `v1.9-read-bug-rca` tip in all 3 repos, NOT the convention's off-`main`/`beta`. `main`/`beta` are stale at the v1.8 close and lack the COBS ADOPT decision + Phase 44 read-timing knobs that v1.10 depends on; the dependency is v1.9-substrate → v1.10 → resumed-v1.9. Tradeoff accepted: merging v1.10 first also carries v1.9's unmerged commits forward. | ✓ Good (shipped on the stacked branch; merge-forward tradeoff stands for the v1.9 promotion) |
| 2026-06-01 | v1.10 keeps CRC8-CCITT (poly 0x07) intact (D-05) and is bound by the Uno-fit filter (D-04: streaming encode only, no second ~512 B buffer, ~545 B free-RAM ceiling). Framing mechanism (streaming COBS `0x00` vs SLIP `0xC0`) deferred to plan-phase research per COBS-DECISION §2.0; SLIP sidesteps the SERIAL_ON_IO `0x00` bus-aliasing concern (Open Q2/Q3). | ✓ Good (COBS `0x00` chosen Phase 49; CRC8 retained; Uno held 504 B free at v1.10 close) |
| 2026-06-01 | Phase 49: COBS `0x00` selected over SLIP `0xC0` as the framing mechanism — SAFE-01 static proof conclusive (host cannot emit a `0x00` frame-boundary byte during the mode-transition window); scored 4-criterion matrix 11/12 vs 10/12. `len_u16` length prefix + XOR checksum dropped from the data-block frame. | ✓ Good (shipped; resync proven on hardware Phase 53) |
| 2026-06-02 | Phase 51: command-channel JSON migrated into COBS+CRC8 framing as a breaking lockstep wire change — no mixed-version interop; CRC8 verified before `parse_json()`. Decoder cap lowered to `DATA_BUFFER_SIZE-1` (CR-01 OOB write) + `millis()`-bounded inter-byte deadline (CR-02 hang) hardened the receive path. | ✓ Good (documented in both sub-repo READMEs; 36/36 native green) |
| 2026-06-05 | Phase 53 byte-exact proof accepted in **self-consistency** form (D-05): no chip on the bench was the original `19710f6e` GATE-1.8d baseline, so N=5 self-identity (rather than baseline-reproduction) is the operator-accepted achieved form; recorded explicitly in the SHA files + SUMMARY. uno328pb instability persisting on the hardened transport recorded as transport-**exoneration**, NOT a hardware fix. | ✓ Good (operator-authorized override; RCA cleanly deferred to v1.9 Phase 45+) |

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

*Last updated: 2026-06-07 — after v1.10 (Serial Transport Hardening / COBS) milestone close. Shipped 7 phases (49–55), 27 plans, 14/14 requirements: streaming COBS `0x00` + CRC8 framing with automatic resync on both the data-block path and the host→fw JSON command channel; 2 s timeout cascade removed; byte-exact proven on operator-witnessed bench (Uno + Leonardo); uno328pb instability transport-exonerated (RCA deferred). Beta-only — stable `3.0.1` operator-gated. Serial is now a settled variable. **Next: v1.9 Read-Bug RCA resumes at Phase 45** (`/gsd-plan-phase 45`) once the hardened transport is merged.*

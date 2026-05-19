---
gsd_state_version: 1.0
milestone: v1.3
milestone_name: — CMOS EPROM Family Hardware Validation
status: executing
last_updated: "2026-05-19T21:54:56.559Z"
last_activity: 2026-05-19 -- Phase 11 planning complete
progress:
  total_phases: 4
  completed_phases: 0
  total_plans: 6
  completed_plans: 0
  percent: 0
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-05-19

## Current Position

Phase: Not started (roadmap drafted)
Plan: —
Status: Ready to execute
Resume from: `/gsd-plan-phase 11` to decompose Phase 11 into executable plans
Last activity: 2026-05-19 -- Phase 11 planning complete

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-19)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** v1.3 — bench-validating the CMOS EPROM families (algo 0x07 28-pin + algo 0x08 32-pin) that v1.0–v1.2 dispatch logic ships for. End-to-end write/read/verify on Uno + Leonardo for W27C512, SST27SF512, W27C020, W27E040 plus density-tier representatives; structural-coverage report across the ~341 algo-0x07 + algo-0x08 chips in the database.

- v1.2 (Message-ID Logging Rework) shipped 2026-05-19 — Leonardo Flash 98.7% → 85.4%
- v1.3 in planning — roadmap drafted (Phases 11–14), 12/12 requirements mapped
- Phase numbering continues from v1.2 close (starts at Phase 11)

## Roadmap Summary

**v1.3 phases:** 4 (numbered 11–14, continues from v1.2 close). Granularity: Comprehensive (compressed — validation milestone, not a build milestone).

| Phase | Goal | Requirements | Bench-gated? |
|-------|------|--------------|--------------|
| 11. Coverage Matrix & DB Inconsistency Audit | Single-source coverage map of all 341 algo-0x07/0x08 DB rows + flag intra-algorithm inconsistencies | COV-01, COV-02 | No (desk-side) |
| 12. 28-Pin / Algo-0x07 Bench Validation | Full write/read/verify cycle on Uno + Leonardo for W27C512, SST27SF512, 32K density-low rep; establish chip-ID + VPP observation protocols | BENCH-01, BENCH-02, BENCH-05, PROTO-01, PROTO-02 | Yes |
| 13. 32-Pin / Algo-0x08 Bench Validation | Full write/read/verify cycle on Uno + Leonardo for W27C020, W27E040, 128K density-low rep; re-apply Phase 12 observation protocols | BENCH-03, BENCH-04, BENCH-06 | Yes |
| 14. Milestone Close & Artifacts | Publish v1.3-BENCH-RESULTS.md, update MILESTONES.md, archive phase directories | DOC-01, DOC-02 | No (paperwork) |

**Coverage:** 12/12 v1.3 requirements mapped to exactly one phase. No orphans, no duplicates.

**Phase-order rationale:**

- Phase 11 first — desk-side, lands without hardware; coverage matrix informs which density-low representatives are chosen for Phases 12 + 13.
- Phase 12 before Phase 13 — establishes chip-ID + VPP scope observation protocols against the smaller-package algo-0x07 family first; Phase 13 reuses the same protocols.
- Phase 14 last — depends on bench data + coverage matrix being in hand.

Full details: `.planning/ROADMAP.md` (v1.3 section).

## Milestone History

- **v1.0** — Protocol-Aware Programming Architecture (shipped 2026-05-11) — see `.planning/MILESTONES.md` + `.planning/milestones/v1.0-*.md`
- **v1.1** — Safety Closure & Hardware Validation — **PAUSED at 80%** (2026-05-18). Phases 1–3 complete (SAF closure, wire-key rename, retroactive VERIFICATION.md artifacts). Phase 4 hardware-validation Plan 2 of 3 in progress (FM1608 byte-0 read bug parked — see `.planning/debug/fm1608-fresh-chip-baseline.md`; needs a different Uno board to unblock). Phase 5 (milestone close) deferred.
- **v1.2** — Message-ID Logging Rework (shipped 2026-05-19) — 23/23 requirements; Leonardo Flash 98.7% → 85.4% (−3,792 B); firmware 3.0.0-dev lockstep upgrade. 4 hardware-pending UAT items deferred into v1.3 bench session (see Deferred Items below). See `.planning/MILESTONES.md`.

## Accumulated Context

### Open Blockers

None at v1.2 close.

## Deferred Items

Items acknowledged and deferred at v1.2 milestone close on 2026-05-19. The three W27C512 UAT items now **naturally fold into v1.3** — the W27C512 bench session is in scope for v1.3 BENCH-* requirements, so closing v1.3 closes Phase 08 SC#2/SC#3 + Phase 09 SC#3 as a side effect. The FM1608 byte-0 read bug remains parked (different chip family, different debug session, requires different Uno R3 hardware).

| Category | Item | Status | Note |
|----------|------|--------|------|
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 | v1.1 carryover — needs different Uno R3 to unblock; out of scope for v1.3 |
| uat | Phase 08 HUMAN-UAT.md | partial — 2 pending scenarios | chip-seated W27C512 write + readback → closes via v1.3 BENCH-01 (Phase 12) |
| verification | Phase 08 VERIFICATION.md | human_needed | bench UAT closure → closes via v1.3 BENCH-01 (Phase 12) |
| verification | Phase 09 VERIFICATION.md | human_needed | Plan 09-05 Task 3 (chip-seated W27C512 on both boards) → closes via v1.3 BENCH-01 (Phase 12) |

### Carried Over From v1.1 (still open)

- **v1.1 Phase 4 — FM1608 byte-0 read bug** — Localized to a specific Uno board (chip + shield both clean on Leonardo). Eight firmware fixes failed (PORTD pre/post-clear, robust-read with 100µs + 2nd /CE cycle, LSB cache invalidation). Cheapest unblocking experiment: try a different Uno R3. See `.planning/debug/fm1608-fresh-chip-baseline.md` (status: `parked-2026-05-18`).
- **WARNING-4** — `firestarter_test.sh` / `write_test.sh` reference deleted `database_generated.json`. Was scheduled for v1.1 Phase 4 (HW-01). Carries forward; address either as part of v1.1 closure or fold into v1.2 if test scripts are touched.
- **v1.1 DOC-01 (milestone close)** — Phase 5 of v1.1 deferred; will be picked up either after v1.2 ships or folded with the FM1608 unblock.

### Resolved in v1.1 (Phases 1–3 complete)

- WARNING-1 (Intel-flash VPP ADC compare) — Plan 01-01
- WARNING-2 (`eeprom_28c.cpp` chip-id forward-compat) — Plan 01-02
- WARNING-3 (wire JSON `"vpp"` → `"vpp_mv"`) — Plan 02-01 + 02-02
- CLEAN-01 (`minipro_complete_db.json` → `chip_database.json` rename) — Plan 02-02
- CLEAN-02 (minipro attribution scrub) — Plan 02-03
- VERIF-01..VERIF-10 (retroactive VERIFICATION.md for v1.0 Phases 01–10) — Phase 03

### Resolved Blockers (v1.0)

- BLOCKER-1 (Phase 12) — algorithm-based dispatch for protocols 0x05/0x06/0x07/0x08/0x0B and SRAM 0x0E/0x27/0x28/0x29
- BLOCKER-2 (Phase 12) — SRAM chips routed to `configure_eprom` with 12V VPP regulator
- WARNING-5 (Phase 13) — AT28C256/64 5V EEPROM 12V-on-A14 hazard via DB override

## v1.3 Decisions (locked at milestone start, 2026-05-19)

- **Scope:** Algorithm-0x07 (28-pin DIP CMOS UV-EPROM, 214 chips in DB) + algorithm-0x08 (32-pin DIP CMOS UV-EPROM, 127 chips in DB). End-to-end bench validation on Uno + Leonardo for four named chips (W27C512, SST27SF512, W27C020, W27E040) + one 28-pin lower-density representative + one 32-pin lower-density representative. Structural-coverage report across all 341 in-scope DB rows.
- **Out of scope:** New algorithms, new chip families, FM1608 (parked v1.1 carryover), flash-savings work (v1.2 budget held as-is).
- **Definition of "working" (bench gate per chip):** chip-ID read returns DB-declared value where `chip_id_check: true`; blank-check passes; write programs a test image without error; read-back is byte-identical; VPP regulator engages at 12V; both Uno (512-B buffer) and Leonardo (1024-B buffer) reach green.
- **Density coverage strategy:** test at both ends — smallest 28-pin (32K W27C257 / SST27SF256) and smallest 32-pin (128K W27C010 / SST27SF010) — so address-bus correctness covers the whole 32K → 512K span.
- **Deferred-items absorption:** v1.2 Phase 08 SC#2/SC#3 + Phase 09 Plan-05 Task 3 (chip-seated W27C512 UAT) close as a byproduct of v1.3 BENCH-01 (Phase 12).
- **Hardware-bench dependency:** entire milestone is operator-on-bench gated EXCEPT Phase 11 (desk-side coverage matrix + DB audit) and Phase 14 (close-out paperwork). Plan structure isolates these so progress is possible without continuous hardware access.
- **Phase numbering:** continues from v1.2 (Phase 11+); no `--reset-phase-numbers`.
- **PROTO-01/02 mapping:** mapped to Phase 12 (where chip-ID + VPP scope observation protocols are established + first applied); protocol carries forward into Phase 13 unchanged, and final aggregation lands in Phase 14 BENCH-RESULTS.

## v1.2 Decisions (locked at milestone start, 2026-05-18)

- **Goal weighting:** flash savings + clean protocol equally weighted. Either can drive a decision when they conflict.
- **Backwards compatibility:** none — firmware + host upgrade together. Firmware version bump enforces.
- **Scope:** ALL firmware log call-sites (`OK:`, `INIT:`, `MAIN:`, `END:`, `INFO:`, `WARN:`, `ERROR:`) migrate to ID + param-bytes format. Only the `DATA:` raw binary read-payload stream is untouched (already optimal; only the prefix marker would change and it's not worth the parser churn).
- **ID width:** 1 byte (0–255 messages). Current firmware has well under 100 distinct strings; generous headroom.
- **Param encoding:** raw byte array; catalog declares each ID's parameter shape (e.g. `[u16, u24]`). No type tags on the wire.
- **Catalog source-of-truth:** single canonical file in the meta-repo. Codegen produces a C++ header for firmware + a Python module for host.
- **Generated artifact policy:** generated files **committed** to both sub-repos. CI runs `<regen> && git diff --exit-code` so drift fails the build (visible in PRs).
- **Migration strategy:** phased. Infrastructure first (no removals). Then batched call-site conversion. Old log macros + PROGMEM strings deleted last, where the final flash-savings measurement happens.
- **Localization:** English only. No multi-language plumbing in v1.2.
- **Phase numbering:** continues from v1.1 (Phase 6-10); no `--reset-phase-numbers`.

## Decisions Carried Forward (v1.0 + v1.1)

See archived `.planning/milestones/v1.0-*.md` for v1.0 decisions and `.planning/phases/01-*/`, `02-*/`, `03-*/` for v1.1 phase-level decisions.

## Operator Next Steps

- **v1.3:** `/gsd-plan-phase 11` to decompose Phase 11 (Coverage Matrix & DB Inconsistency Audit). Phase 11 is desk-side and unblocks bench prep without requiring hardware.
- v1.1 leftovers (FM1608 hw bug, WARNING-4 test scripts, v1.1 DOC-01 milestone close) carried in this STATE; resume after v1.3 ships or fold opportunistically.

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| Phase 06 P06-01 | 10m | 2 tasks | 10 files |
| Phase 06 P02 | 30 min | 2 tasks | 12 files |
| Phase 06 P03 | 5min | 3 tasks | 5 files |
| Phase 06 P06-04 | ~6 min | 2 tasks | 3 files |
| Phase 06 P06 | 8 min | 1 tasks | 1 files |
| Phase 06 P06-05 | ~7min | 3 tasks | 3 files |
| Phase 07 P07-01 | 1min | - tasks | - files |
| Phase 07 P03 | 15min | 1 tasks | 1 files |
| Phase 07 P04 | 15min | 1 tasks | 1 files |
| Phase 07 P05 | 1min | 2 tasks | 2 files |
| Phase 07 P06 | 2min | 1 tasks | 1 files |
| Phase 07-convert-error-warn-info-call-sites P07 | 15 | 1 tasks | 2 files |
| Phase 07 P08 | 5 | 1 tasks | 1 files |
| Phase 07 P09 | 10min | 1 tasks | 1 files |
| Phase 07 P10 | 15 | 1 tasks | 1 files |
| Phase 07 P11 | 3min | 1 tasks | 1 files |
| Phase 08 P08-01 | 25min | 3 tasks | 9 files |
| Phase 08 P02 | 19 | 2 tasks | 5 files |
| Phase 08 P03 | 20min | 2 tasks | 2 files |
| Phase 08 P04 | 20min | 6 tasks | 7 files |
| Phase 08 P05 | 45min | 4 tasks | 11 files |
| Phase 08 P06 | 12min | 2 tasks | 5 files |
| Phase 08 P07 | 11min | 2 tasks | 14 files |

## Decisions

- [Phase ?]: Plan 06-01: Adopted 68-entry catalog from RESEARCH §Full Catalog Seed table (the section header's 52-count is stale; the table itself has 68 rows).
- [Phase ?]: Plan 06-01: Codegen idempotence achieved via sort-by-id + LF-only line endings + no-timestamp banner; proven by re-running and diffing the output (BYTE-IDENTICAL on all 3 emitters).
- [Phase ?]: Plan 06-01: Catalog distribution = meta-repo authoritative + vendored sub-repo copies + cross-sub-repo byte-identity assertion in sync_to_subrepos.sh.
- [Phase ?]: Leonardo override: zero-diff (weak rurp_log_id default suffices — no com_mode global, no PORTD aliasing on USB-CDC; confirms T-06-08 acceptance)
- [Phase ?]: Phase 06-02: Native test binary links real rurp_serial_utils.cpp + messages.c via widened [env:native] src_filter — production CRC8 table + emitter validated end-to-end
- [Phase ?]: Host decoder ascii_str decode uses errors='replace' for visible tamper surface
- [Phase ?]: Reference CRC in test conftest is table-FREE — independent of production lookup table (catches table drift)
- [Phase ?]: _read_and_parse_lines unified text+binary dispatch through single yield surface (D-05)
- [Phase ?]: Phase 6 Plan 04: re-raise resolution + locked wording + escape hatch
- [Phase 06]: Plan 06-06: Decision Case A — Leonardo Phase 6 close at 98.7% (28,292/28,672 B, 380 B free); −7 B vs v1.1 close baseline (rounding noise; same 98.7% display). LMIG-01 coexistence proven; no -D NO_TEXT_LOGS fall-back required. Uno baseline established at 80.9% (6,156 B free).
- [Phase ?]: Phase 06-05: release.yml NOT given needs:[ci] gate — optional per plan; retrofittable later if bad-catalog→tag→PyPI race ever bites.
- [Phase ?]: Phase 06-05: Meta-repo catalog-sync-check.yml uses cmp (byte-equality, load-bearing) + diff (readable failure dump) together; submodules:recursive on meta-repo checkout per orchestrator objective.
- [Phase ?]: Phase 06-05: GitHub slugs pinned to henols/firestarter and henols/firestarter_app (confirmed via git remote get-url origin).
- [Phase ?]: Phase 07-01: LOG_ERROR_ID_* and LOG_WARN_ID_* macro families added as unconditional one-line aliases — no FLAG_VERBOSE gate, zero flash cost until call-sites are converted
- [Phase ?]: Phase 07-03: CHIP_ID_MISMATCH uses error_code parameter (not FLAG_FORCE re-check)
- [Phase ?]: Phase 07-03: WRITE_FAILED packs [u24, u8, u16] = 6 wire bytes MSB-first; braced-block isolation for _b[] arrays in eprom.cpp
- [Phase ?]: Phase 07-04: flash_intel_poll_sr response_code assignments added alongside LOG_ERROR_ID calls (Rule 2 auto-fix — state machine requires both emit and response_code set)
- [Phase 07]: Plan 07-05: flash_type_4.cpp multi-param [u8+u24+u8] packed into named local _b[5]; flash_utils.cpp zero-param LOG_ERROR_ID site; Leonardo confirmed at 98.4% flash (464 B free) after both conversions
- [Phase 07]: Plan 07-06: eeprom_28c.cpp 3 populate-sites converted; response_code added to EEPROM timeout path (was implicit, now explicit); Leonardo 97.8% flash (632 B free) after conversion
- [Phase ?]: Two-line error populate-site pattern established in memory.cpp
- [Phase ?]: Serial stub required in dispatch test setUp once error path emits via rurp_log_id (LOG_ERROR_ID_* conversion)
- [Phase ?]: flash_type_3.cpp:87 Skipping-erase site confirmed OK-path; deferred to Phase 8 (MSG_INFO_SKIPPING_ERASE_MEM 0x59)
- [Phase ?]: Dead-code block at firestarter.cpp:86 safely deleted
- [Phase ?]: command_done() resets handle immediately after timeout emit
- [Phase ?]: No format string needed — catalog owns the wire format
- [Phase 07]: Plan 07-11: Fixed-size stack buffers (16, 8, 32 bytes) for ascii_str packing in dev_tools.cpp; strlen clamped to prevent overrun; Arduino.h already provides string.h on AVR
- [Phase 08]: Plan 08-01: 'bytes' param type added to VALID_PARAM_TYPES (variable-length raw payload; Rule 9 excludes bytes from format specifier count); needed for MSG_DATA_CHUNK + MSG_DEBUG sub-payload
- [Phase 08]: Plan 08-01: MSG_OK_REV format "Rev%u (eff: %u)" [u8, u8]; MSG_OK_CFG format "R1: %lu, R2: %lu, Cfg: %u" [u32, u32, u8]; Rule 9 requires specifier count == non-bytes param count
- [Phase 08]: Plan 08-01: MSG_OK_FW_HANDSHAKE wire_format->id_frame; format "HW: %u, Cmd: 0x%02x, FW: %s" [u8 hw, u8 cmd, ascii_str fw_version]; hw=0xFF sentinel for no HARDWARE_REVISION
- [Phase 08]: Plan 08-01: 41 unique debug strings found (43 call-sites); CONTEXT.md B-01 count of 34 was stale; DBG_* sub_id 0x00..0x28 in [debug] section; audit at /tmp/ph8-debug-audit.txt
- [Phase 08]: Plan 08-01: sync_to_subrepos.sh now runs full generation cycle (copy TOML+codegen, then regen messages.h + messages.py); idempotence confirmed by second run zero-diff
- [Phase ?]: Firmware param_count stays uint8_t, guard widened to 65533 for W-04 MSG_DATA_CHUNK forward-compat
- [Phase ?]: bytes param type decodes all remaining buf as raw bytes; filtered from printf tuple
- [Phase ?]: Phase 08-03: _format_message added as instance method on SerialCommunicator; returns None to fall through to generic catalog rendering for non-sentinel IDs
- [Phase ?]: Phase 08-03: INIT/MAIN/END removed from EXPECTED_PREFIXES; STATE_MACHINE_PREFIXES emptied; dead Done-rewrite branch removed from _log_rurp_feedback
- [Phase ?]: LOG_DATA_ID_U32_U32 composite packs two u32 values as 8 big-endian bytes — covers MSG_DATA_PROGRESS; LOG_DATA_ID_U16_U16 declared for Plan 05 VPP/VPE symmetry
- [Phase ?]: Phase 08-04: 10 call-sites converted (3 state-machine acks, 2 trivial OK/DATA, 5 R-02 populate-sites) using LOG_OK_ID_*/LOG_INIT_ID_*/LOG_MAIN_ID_*/LOG_END_ID_*/LOG_DATA_ID_* families
- [Phase ?]: Phase 08 Plan 06: R-01 SRAM win exactly 96 bytes on both Uno and Leonardo (1593->1497 B Uno, 1563->1467 B Leonardo)
- [Phase 08]: Plan 08-07: LOG_DEBUG_ID_SUB_U16_U16 added for DBG_PULSE_DELAY_MISMATCH (pulse_delay is uint32_t exceeding catalog u8 decl; u16 preserves diagnostic range)
- [Phase 08]: Plan 08-07: debug_msg_buffer deleted (malloc(80) removed, extern decl removed, Uno rurp_log_id/rurp_log_P SoftwareSerial paths removed); debug_setup() retained for SoftwareSerial port init
- [Phase 08]: Plan 08-07: Production flash unchanged vs Plan 06 baseline — debug() was already a #define no-op in production; new LOG_DEBUG_ID_SUB* expands to same nothing

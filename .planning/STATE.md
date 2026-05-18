---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: — Message-ID Logging Rework
status: executing
last_updated: "2026-05-18T20:11:55.337Z"
last_activity: 2026-05-18
progress:
  total_phases: 5
  completed_phases: 2
  total_plans: 27
  completed_plans: 26
  percent: 40
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-05-18

## Current Position

Phase: 08 (Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END)) — EXECUTING
Plan: 8 of 8
Status: Ready to execute
Resume from: `.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-08-PLAN.md`
Last activity: 2026-05-18

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-18)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** Phase 08 — Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END)

- Replace firmware text-string logs with 1-byte message IDs + raw parameter byte arrays
- Single canonical catalog (meta-repo) → codegen → C++ header (firmware) + Python module (host)
- Lockstep upgrade; no backwards compatibility to text format
- Phased migration: infrastructure → batched call-site conversion → delete old log code
- Generated files committed; CI regenerates + diffs as drift gate
- Goal: free Leonardo flash space (currently 98.7%) AND a cleaner host↔firmware protocol

## Roadmap Summary

**v1.2 phases (numbered 6-10 — continues from v1.1):**

| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 6 | Logging Infrastructure (catalog + codegen + helper + decoder) | LCAT-01..05, LFW-01, LFW-02, LFW-05, LHOST-01..04, LCI-01..04, LMIG-01 (17 reqs) | Not started |
| 7 | Convert ERROR + WARN + INFO Call-Sites | LMIG-02 | Not started |
| 8 | Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END) | LMIG-03 | Not started |
| 9 | Delete Old Log Macros + Measure Flash Savings | LFW-03, LFW-04, LMIG-04 | Not started |
| 10 | Milestone Close (v1.2) | DOC-02 | Not started |

**Coverage:** 23/23 requirements mapped (100% ✓) — 22 v1.2 requirements + DOC-02 (milestone-close) added by the roadmap.

**Dependency chain:** strictly linear (6 → 7 → 8 → 9 → 10) — mirrors the locked phased migration order Phase A → B → C → D → Close.

Full roadmap: `.planning/ROADMAP.md`

## Milestone History

- **v1.0** — Protocol-Aware Programming Architecture (shipped 2026-05-11) — see `.planning/MILESTONES.md` + `.planning/milestones/v1.0-*.md`
- **v1.1** — Safety Closure & Hardware Validation — **PAUSED at 80%** (2026-05-18). Phases 1–3 complete (SAF closure, wire-key rename, retroactive VERIFICATION.md artifacts). Phase 4 hardware-validation Plan 2 of 3 in progress (FM1608 byte-0 read bug parked — see `.planning/debug/fm1608-fresh-chip-baseline.md`; needs a different Uno board to unblock). Phase 5 (milestone close) deferred.

## Accumulated Context

### Open Blockers

None at v1.2 start.

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

- Phase 6 plans are drafted + verified. Next: `/gsd-execute-phase 6` to execute the 6-plan, 4-wave Phase 6.
- v1.1 leftovers (FM1608 hw bug, WARNING-4 test scripts, v1.1 DOC-01 milestone close) carried in this STATE; resume after v1.2 ships or fold opportunistically.

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

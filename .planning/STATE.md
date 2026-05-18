---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: — Message-ID Logging Rework
status: executing
last_updated: "2026-05-18T12:05:33.085Z"
last_activity: 2026-05-18
progress:
  total_phases: 5
  completed_phases: 0
  total_plans: 6
  completed_plans: 3
  percent: 0
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-05-18

## Current Position

Phase: 06 (logging-infrastructure) — EXECUTING
Plan: 4 of 6
Status: Ready to execute
Resume from: `.planning/phases/06-logging-infrastructure/06-02-PLAN.md` (Wave 1 firmware helper)
Last activity: 2026-05-18

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-18)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** Phase 06 — logging-infrastructure

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

## Decisions

- [Phase ?]: Plan 06-01: Adopted 68-entry catalog from RESEARCH §Full Catalog Seed table (the section header's 52-count is stale; the table itself has 68 rows).
- [Phase ?]: Plan 06-01: Codegen idempotence achieved via sort-by-id + LF-only line endings + no-timestamp banner; proven by re-running and diffing the output (BYTE-IDENTICAL on all 3 emitters).
- [Phase ?]: Plan 06-01: Catalog distribution = meta-repo authoritative + vendored sub-repo copies + cross-sub-repo byte-identity assertion in sync_to_subrepos.sh.
- [Phase ?]: Leonardo override: zero-diff (weak rurp_log_id default suffices — no com_mode global, no PORTD aliasing on USB-CDC; confirms T-06-08 acceptance)
- [Phase ?]: Phase 06-02: Native test binary links real rurp_serial_utils.cpp + messages.c via widened [env:native] src_filter — production CRC8 table + emitter validated end-to-end
- [Phase ?]: Host decoder ascii_str decode uses errors='replace' for visible tamper surface
- [Phase ?]: Reference CRC in test conftest is table-FREE — independent of production lookup table (catches table drift)
- [Phase ?]: _read_and_parse_lines unified text+binary dispatch through single yield surface (D-05)

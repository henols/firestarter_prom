---
gsd_state_version: 1.0
milestone: v1.11
milestone_name: — Complete infoic.xml Decode & Database Correctness
status: verifying
stopped_at: Phase 61 SHIPPED (executed + verified 7/7 + code-review fixed); FM1608 info-view follow-up committed. v1.11 ready to close.
last_updated: "2026-06-10T00:00:00.000Z"
last_activity: 2026-06-10
progress:
  total_phases: 10
  completed_phases: 6
  total_plans: 21
  completed_plans: 19
  percent: 60
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-06-09

## Current Position

Phase: 61 (v1.11 close phase)
Plan: 61-01 complete
Status: SHIPPED — verified 7/7, code review fixed (WR-01/WR-02), FM1608 info-view follow-up landed
Last activity: 2026-06-10
Note: Phase 61 is the v1.11 close phase. All v1.11 phases (56–61) complete. Ready for /gsd-complete-milestone.
Post-61 follow-up on firestarter_app v1.11 branch (NOT in phase artifacts; commits b81131f + e910e5e): FM1608 info-view fixes — SRAM/FRAM Vcc→5V normalization in build_db.py + DB regen, zero-pulse-delay row suppression, chip-ID "-" placeholder. Resolves the carried `w27c512-eeprom-misclassification` family of display concerns. Remember to bump the meta firestarter_app gitlink at beta cut.

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-08 after v1.11 scope lock)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** Phase 61 — list-search-display-correctness-and-table-layout
(firestarter_app data pipeline + docs). Firmware sub-repo untouched. 15 requirements across
4 phases (56–59). Phase numbering continues from v1.10 close at Phase 55.

## Roadmap Summary

**v1.11 (ACTIVE 2026-06-08):** 4 phases (56–59), 0/TBD plans, 15/15 requirements mapped.
HOST-ONLY decode-correctness milestone: authoritative field dictionary + minipro-source-grounded
decode rules, fix confirmed bugs (interpret_timing ×100, VCC nibbles, vdd/vcc swap, PROTOCOL_MAP
names), unblock 9 × 24-pin EEPROMs (host-only, no firmware change), correctness/regression gate.

| Phase | Goal | Requirements |
|-------|------|--------------|
| 56 | Snapshot + Field Dictionary + Corrected Docs | DEC-01, DEC-03, DEC-04, DEC-05, DOC-01, DOC-02, DOC-03, GATE-01 |
| 57 | Decode Bug Fixes + PROTOCOL_MAP + check_dispatch Extension | DEC-02, DEC-03*, DEC-04*, DEC-05*, GATE-03 |
| 58 | Pinout Re-derivation + 24-pin EEPROM Unblock | PIN-01, PIN-02, PIN-03 |
| 59 | Correctness Gate + Per-chip Diff + SRAM Audit | GATE-02, GATE-04 |

*DEC-03/04/05 span Phases 56 (field dictionary) and 57 (build_db.py code fixes); primary
 artifact assignment: Phase 56 for the dictionary, Phase 57 for the corrected decode code.

**v1.10 SHIPPED 2026-06-07:** 7 phases (49–55), 27 plans, 14/14 requirements. Provably
byte-exact serial transport (COBS `0x00` + CRC8). Beta-only; stable `3.0.1` operator-gated.
Archive: `.planning/milestones/v1.10-ROADMAP.md`.

**v1.9 Read-Bug RCA + Fix — DEFERRED (operator 2026-06-08):** Phases 45–48 remain.
Resumes at Phase 45 when the operator picks it back up.

## Accumulated Context

### Roadmap Evolution

- Phase 61 added (2026-06-10): List/Search Display Correctness + Table Layout — extend Phase 60's `electrical.type`-sourced display to the `firestarter list`/search table (Type + VPP columns; resolves the Phase 60 review IN-01 `info`-vs-`list` divergence incl. spurious SRAM VPP), AND enforce table-layout rules: fit all columns without breaking, never render narrower than today's default width (today is the floor). Host-only (`eprom_info.py` `print_eprom_list_table`). v1.11 `/gsd-complete-milestone` now deferred until Phase 61 ships (was: until Phase 60).
- Phase 60 added (2026-06-10): Display-Layer Decode Correctness — `firestarter info` / `ic_layout.py` must derive the displayed Type and "Can be erased" from the DB's `electrical.type`/`flags`, not solely `protocol_id`. Triggered by the post-Phase-59 `/gsd-debug` finding: `cca7d62` corrected `electrical.type` to EEPROM for W27C512/SST27VF512/etc., but the operator-facing `info` display is protocol-keyed and still shows "UV-EPROM / MTP-Flash" + "Can be erased: false". Host-only; firmware electrical-erase support is a separate firmware backlog item. Phase 60 is now the v1.11 close phase (was 59).

### v1.11 Scope Lock (2026-06-08)

Research overturned the original "expand + firmware handlers" framing. The hardware-feasible
memory set is **already covered**: 0x2A/0x2C/0x2E are GAL/PIC PLD/MCU protocols (zero DIP
memory chips); FWH `0x11` is LPC-serial + 3.3V (infeasible on RURP); real NVRAM/timekeeper
already handled via existing SRAM protocols. Genuine new-chip gap = ~9 blocked 24-pin EEPROMs
(AT28C04/AT28C16 family) — unblockable HOST-ONLY via `DIP24_6116` pinout + `algorithm=0x0D`;
`configure_eeprom28c` already handles them. No new firmware handlers needed.

**Confirmed decode bugs to fix (all host-only):**

- BUG-1: `VCC_VOLTAGES` missing nibble 0x02 (4V) / 0x03 (4.5V)
- BUG-2: `interpret_timing` ×100 multiplier for 0x07/0x0B (W27C512 → 10000µs not 100µs)
- BUG-3: `vdd`/`vcc` field labels inverted vs minipro `database.c`
- BUG-4: `PROTOCOL_MAP` wrong names for 0x2A/0x2C/0x2E/0x35; invented 0x3C; phantom 0x39

**Key ordering constraints (from research):**

1. Pinned infoic.xml snapshot FIRST (prevents upstream drift corrupting regression baseline)
2. `check_dispatch.py` full-class VPP-safety guard BEFORE re-derivation changes land
3. 24-pin EEPROM unblock AFTER corrected decode + pinout audit
4. Correctness gate (per-chip diff) LAST

**Safety guard:** The load-bearing overrides (WARNING-5, fm1608, 24-pin EEPROM skip) must
survive re-derivation intact. The two-pass `_etype` pattern in `build_db.py` must be preserved.
Any new pinout must pass the SR-1 checklist before landing.

**GATE-04 conditionality:** `configure_sram` NVRAM/SRAM audit is host-side documentation.
Escalates to a firmware backlog item ONLY if a real safety issue is found — no up-front firmware
phase is created.

### ⏸ v1.9 DEFERRED (operator 2026-06-08 — "skip that bug for now"; resumes later at Phase 45)

v1.9 (Read-Bug RCA + Fix) is paused — deferred by operator decision after v1.10 shipped.
Phase 44 (Bug A RCA) complete; Phase 48 plan 48-01 (COBS verdict) complete.
Remaining: Phases 45–48. Resume: `/gsd-plan-phase 45`.

### v1.10 Substrate (carry-forward)

- Transport provably byte-exact (COBS `0x00` + CRC8-CCITT). Settled variable for v1.9 RCA.
- uno328pb read instability persists (transport-exonerated; RCA deferred to v1.9 Phase 45+).
- GATE-1.8d ring-fence: `_read_and_parse_lines` body byte-identical; 15 N=5 W27C512 baseline
  binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` valid.

### Pending Todos (carried forward)

- `w27c512-eeprom-misclassification.md` (HIGH) — DB content fix; relevant to v1.11 decode work
- `avrdude-mcu-detection-fallback.md` (low) — out of v1.11 scope, carry forward
- `large-read-data-jitter-uno328pb.md` (HIGH) — v1.9 RCA target

### Blockers / Concerns

None for v1.11 — this is a host-only, software-only milestone. No bench required to close.
No firmware sub-repo changes expected (GATE-04 is the one conditional; it escalates to firmware
only if a real safety issue is found during the SRAM audit).

## Session Continuity

Last session: 2026-06-10
Stopped at: Session resumed — Phase 61 confirmed shipped + FM1608 follow-up committed; proceeding toward v1.11 milestone close
Resume file: None

## Decisions

- Phase 57-01: Four decode bugs fixed in build_db.py (VCC nibbles, vcc/vdd swap, timing x100, PROTOCOL_MAP names) — all host-only, no DB regeneration in this plan
- Phase 57-01: ruff format applied to pre-existing VPP_MV/KNOWN_PROTOCOLS style violations to satisfy plan gate
- Phase 57-01: Excluded PROTOCOL_MAP IDs documented as comments (not deleted) for traceability; two-pass _etype structure preserved
- [Phase ?]: GATE-03 predicate uses proto in _5v_eeprom_algos (not etype) for direct algorithm-based VPP-safety check
- [Phase ?]: pinouts.json loaded dynamically in main() so GATE-03 auto-covers Phase 58 pinout additions
- Phase 57-03: test_characterization.ambr did not need refresh; the file requiring update was tests/golden/v1.3-COVERAGE-MATRIX.md (pulse_duration column)
- Phase 57-03: DEC-03 CLI surface (firestarter info W27C512 exits 0, 100uS) completed by debug fix 8088141 on same branch; tracked in .planning/debug/firestarter-info-vpp-pin-crash.md
- [Phase ?]: Phase 58-01: DIP24_2816 pinout added with no vpp-pin (pin 21 = rw-pin/WE, SR-1 invariant)
- [Phase ?]: Phase 58-01: Five Wave 0 RED-first test classes committed (TestResolvedPinoutKey/TestGuessTablesDeleted/TestWarning5Rule RED; TestDIP24_2816Pinout GREEN)
- [Phase ?]: Phase 58-02: principled resolve_pinout_key; 743 chips; 19 Rule1 + 12 Rule2; GATE-03 0 violations; 516 tests green
- Phase 58-03: GATE-03 0 violations confirmed on 743-chip regenerated DB; AT28C04/16 CLI-reachable; SR-1 two-layer docs authored (DIP24_2816 PASS + all changed pinouts reviewed)
- Phase 59-02: GATE-04 audit: configure_sram near-no-op; BLOCKER-2 guard proof (0 SRAM chips → configure_eprom); Safety Verdict no-escalation + criterion stated; two-layer lockstep committed
- [Phase ?]: Phase 61-01: Single resolve_type_label helper on EpromSpecBuilder — D-04 single source of truth for Type label in both info and list views
- [Phase ?]: Phase 61-01: VPP gate parity — vpp_mv > 0 AND electrical-type != SRAM (D-03); SRAM shows '-' despite vpp_mv=12000
- [Phase ?]: Phase 61-01: Name column dynamic width clamped to [13,20] with ellipsis truncation; VPP column fixed at 5

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| 57 | 01 | 26min | DEC-02/03/04/05 decode fixes in build_db.py; 10 new tests; ruff clean |
| 57 | 02 | 18min | GATE-03 full-class VPP guard; check_dispatch.py extended; 0 violations |
| 57 | 03 | ~45min | DB regenerated (734 chips); W27C512=100us; GATE-03 on regen set; 480 tests green |
| Phase 58 P02 | 35 | 2 tasks | 5 files |
| 59 | 02 | ~4min | GATE-04 SRAM audit; configure_sram near-no-op confirmed; 3 NVRAM truths documented; two-layer lockstep |
| Phase 61 P01 | 40min | - tasks | - files |

## Deferred Items

Items acknowledged and deferred. None are incomplete v1.10 transport work.

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| debug | firmware-vpp-misread | diagnosed | Fixed in Phase 54 UAT (uno328pb R1 recal 1000→270000); session left open — close retroactively |
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 | Pre-v1.10 FRAM byte-0 write investigation; out of v1.10 scope |
| uat | Phase 08 (08-HUMAN-UAT.md) | partial (2 pending) | v1.0-era logging-infrastructure phase; out of v1.11 scope |
| verification | Phase 08 (08-VERIFICATION.md) | human_needed | v1.0-era logging phase; out of v1.11 scope |
| verification | Phase 09 (09-VERIFICATION.md) | human_needed | v1.0-era logging phase; out of v1.11 scope |
| todo | avrdude-mcu-detection-fallback.md | low | Carry-forward; out of v1.11 scope |
| todo | cobs-decoder-framelevel-deadline-wr01.md | medium | v1.10 COBS follow-up (WR-01); explicitly deferred per REQUIREMENTS.md §Future |
| todo | w27c512-eeprom-misclassification.md | high | Relevant to v1.11 decode work; evaluate at Phase 57 |

## Operator Next Steps

- Phase 60 complete + verified (11/11). Code-review fix cycle landed (WR-01 SRAM-VPP regression fixed). IN-01 `info`/`list` divergence promoted to Phase 61.
- Phase 61 (List/Search Display Correctness + Table Layout) is the new v1.11 close phase. Next: `/gsd-plan-phase 61`. Run `/gsd-complete-milestone` only after Phase 61 ships.

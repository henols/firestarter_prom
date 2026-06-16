---
gsd_state_version: 1.0
milestone: v1.13
milestone_name: Programming Algorithm Validation + Gap Implementation
status: planning
last_updated: "2026-06-16T10:46:59.616Z"
last_activity: 2026-06-16
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-06-10

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-06-16 — Milestone v1.13 started

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-10 for v1.12)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** Phase 70 — v1-11-v1-12-db-pipeline-integration-for-beta-merge
dispatch eliminating the silent VPP-hazard `mem_type` fallback path; new
`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` wire response (lockstep dual-repo); host
`ProtocolNotImplementedError` + clear CLI message; capability-honest DB inclusion
(`support_status` taxonomy: `protocol-not-implemented` / `adapter-required` / `vpp-exceeds-max`;
true NMOS VPP correction for M2716/M2732/M2732A; principled pinout engineering for currently-unclassifiable DIP chips;
host `info`/`write`/`read`/`verify` status-specific capability guard).
First firmware-touching milestone since v1.10. Phases 62–68, no bench required.

## Roadmap Summary

**v1.12 ACTIVE — 7 phases (62–68):**

- Phase 62: Dispatch Baseline Capture + check_dispatch Update (GATE-01, GATE-02)
- Phase 63: Catalog Lockstep Wire Change (WIRE-01)
- Phase 64: Firmware Fail-Closed Dispatch + Native Tests (DISP-01..04, WIRE-02, TEST-01, TEST-02)
- Phase 65: Host Graceful Handling (HOST-01, HOST-02)
- Phase 66: DB Inclusion + VPP Correction + Dispatch Gate (DB-01, DB-03, DB-05)
- Phase 67: Pinout Classification for Unclassifiable DIP Chips (DB-02)
- Phase 68: Host Capability Reporting (DB-04)

**v1.11 SHIPPED 2026-06-10:** 6 phases (56–61), 14 plans, 15/15 requirements. HOST-ONLY
decode-correctness milestone (firmware untouched like v1.8). Authoritative field dictionary +
minipro-source-grounded decode, 4 decode bugs fixed, principled `resolve_pinout_key`, 9 × 24-pin
EEPROMs unblocked host-only, full-class VPP-safety + per-chip diff gates, display layer reflects
`electrical.type`. Audit PASSED 15/15. Beta-only; lockstep `3.0.0b9` cut + stable operator-gated.
Archive: `.planning/milestones/v1.11-ROADMAP.md`.

**v1.10 SHIPPED 2026-06-07:** 7 phases (49–55), 27 plans, 14/14 requirements. Provably
byte-exact serial transport (COBS `0x00` + CRC8). Beta-only; stable `3.0.1` operator-gated.
Archive: `.planning/milestones/v1.10-ROADMAP.md`.

**v1.9 Read-Bug RCA + Fix — DEFERRED (operator 2026-06-08):** Phases 45–48 remain.
Resumes at Phase 45 when the operator picks it back up.

## Accumulated Context

### Roadmap Evolution

- Phase 67.1 inserted after Phase 67 (2026-06-15, URGENT): Close gaps: DB-02 pinout classification + DB-04 capability reporting. Gap-closure phase covering the DB-02 (pinout classification) and DB-04 (capability reporting) gaps surfaced by the v1.12 milestone audit; sits within the Phase 66 `support_status` taxonomy framework that Phases 67/68 build on. HOST-ONLY.
- Phase 69 added (2026-06-14): CLI Command-Surface Robustness Audit — investigate and secure that all `firestarter` commands run without crashing. Triggered by a live `TypeError: '<=' not supported between 'list' and 'int'` in `firestarter info 2732` (`ic_layout._generate_pin_names_for_display` treats pin-map `vpp-pin`/`rw-pin`/`oe-pin` as ints, but `pinouts.json` stores them as lists e.g. `[21]`; the info/display path crashes broadly, not just for 2732). HOST-ONLY.
- Phase 70 added (2026-06-15): v1.11 + v1.12 DB-Pipeline Integration for Beta Merge — discovered while attempting `merge v1.12 → beta` for milestone close. v1.12 was forked off the PRE-v1.11 beta (`faaa571`), so its DB-build pipeline (`build_db.py`/`check_dispatch.py`/`diff_db.py`) collides architecturally with v1.11's Phase 58 rewrite (`resolve_pinout_key` replaced the deleted `DIP28_VARIANT_MAP`). Re-port v1.12's DB safety features onto v1.11's architecture; regenerate DB; validate via GATE-03 + diff_db + CI. Firmware merges clean separately. HOST-ONLY DB tooling. Blocks v1.12 milestone close + beta cut.

### v1.12 Scope Lock (2026-06-10)

Research finding: the SKELETON-NEEDED bucket is **empty**. Every RURP-feasible DIP-parallel-memory
`protocol_id` is already handled (all 743 DB chips covered by 13 protocols). The unimplemented
protocol_ids (`0x11` FWH, `0x2A`/`0x2B`/`0x2C` GAL/PLD, etc.) are all infeasible on RURP.

The milestone's real value is the **fail-closed safety framework + honest reporting**:

1. The silent `mem_type` fallback hazard: `protocol != 0` + `mem_type=1` silently routes to
   `configure_eprom` → 12V VPP on potentially 5V-only chips. Eliminated by the `protocol != 0`
   guard in `configure_memory()`.

2. New `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` (lockstep dual-repo codegen via `messages.toml`).
3. `configure_not_implemented()` catch-all: zero hardware side effects; emits the new message ID.
4. Named infeasibility arms for `0x11`/`0x2A`/`0x2B`/`0x2C` (documents hardware reason in-code).
5. Host `ProtocolNotImplementedError(EpromOperationError)` + clear CLI message with protocol value.

**Branch model:** `v1.12-protocol-dispatch-hardening` off `beta` in all 3 repos; merge back to
`beta`; `beta`→stable operator-gated. Deferred v1.11 host work must reconcile into
`firestarter_app/beta` before v1.12 host changes commit.

**Critical ordering constraints (from research + pitfalls):**

1. Phase 62 GATE first — baseline + `check_dispatch.py` update BEFORE any firmware change
2. Phase 63 WIRE second — catalog message ID in both repos BEFORE firmware emits it
3. Phase 64 FIRMWARE third — guard + not_implemented handler + native tests
4. Phase 65 HOST last — `ProtocolNotImplementedError` + CLI message

**Key pitfalls to remember:**

- Codegen MUST use Python 3.11 (CI target), not the devcontainer's 3.12 — py3.12/3.11 drift trap
- `messages.toml` edit in meta-repo ONLY; sync to both sub-repos via `sync_to_subrepos.sh`
- `check_dispatch.py` updated BEFORE firmware changes (currently has 0x35/0x39 gap)
- Skeleton handlers: NEVER assign operation pointers, NEVER call hardware functions
- Flash gate: Leonardo must stay ≤ 90% after Phase 64

**Flash budget at v1.12 start (from v1.11 close):**

- Leonardo: 88.4% (25,354 B / 28,672 B) — 3,318 B remaining
- Uno: 72.0% (23,216 B / 32,256 B) — 9,040 B remaining

### ⏸ v1.9 DEFERRED (operator 2026-06-08 — "skip that bug for now"; resumes later at Phase 45)

v1.9 (Read-Bug RCA + Fix) is paused — deferred by operator decision after v1.10 shipped.
Phase 44 (Bug A RCA) complete; Phase 48 plan 48-01 (COBS verdict) complete.
Remaining: Phases 45–48. Resume: `/gsd-plan-phase 45`.

### v1.10 Substrate (carry-forward)

- Transport provably byte-exact (COBS `0x00` + CRC8-CCITT). Settled variable for v1.9 RCA.
- uno328pb read instability persists (transport-exonerated; RCA deferred to v1.9 Phase 45+).
- GATE-1.8d ring-fence: `_read_and_parse_lines` body byte-identical; 15 N=5 W27C512 baseline
  binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` valid.

### Pending Todos (carried forward from v1.11)

- `avrdude-mcu-detection-fallback.md` (low) — out of scope, carry forward
- `cobs-decoder-framelevel-deadline-wr01.md` (medium) — v1.10 COBS follow-up; deferred
- `large-read-data-jitter-uno328pb.md` (HIGH, in v1.8-seed) — v1.9 RCA target

### Blockers / Concerns

None at roadmap start. This milestone is provable on the native dispatch harness + pytest;
no bench session required to close. Dual-repo lockstep (firmware + host).

## Session Continuity

Last session: 2026-06-15T20:36:58.964Z
Stopped at: Phase 70 context gathered
Resume file: .planning/phases/70-v1-11-v1-12-db-pipeline-integration-for-beta-merge/70-CONTEXT.md

## Decisions

_(v1.12 decisions will be recorded here as phases execute.)_

- [Phase 62-01]: D-BETA-STATE: beta branch already has 0x35/0x39 explicit dispatch arms; TestDispatchGate02 tests 1+2 are GREEN now (not RED as planned); only protocol!=0 not_implemented arm is missing
- [Phase 62-02]: D-CHIP-COUNT: DB on v1.12 branch has 734 chips (not 743 as plan expected) — v1.11 work not yet reconciled into beta; dispatch_baseline.json correctly captures the actual current DB state
- [Phase ?]: Phase 63-01: D-01 honored (0xBB mirrors 0xAE); D-04 honored (py3.11.13 from source, drift gates green); D-05 honored (firestarter_app gitlink not bumped)
- [Phase ?]: Phase 65-01: _raise_for_error_response(response, message): response.id for typed dispatch, message for EpromOperationError framing
- [Phase ?]: Phase 65-01: SC#2 test asserts on _execute_phase — outer _run_state_machine except swallows typed raise before caller sees it
- [Phase ?]: Phase 65-01: GATE-1.8d ringfence pin updated for planned Response.id addition (v1.12 in-scope)
- [Phase 65-02]: Option B applied — expect_ack raises ProtocolNotImplementedError when response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED; Tuple[bool, Optional[str]] arity unchanged; zero caller-unpacking edits needed
- [Phase 65-02]: WR-02 closed — all 4 state-machine ERROR sites now route through _raise_for_error_response; production-path proven by Test A integration test (REAL EpromOperator + CliRunner)
- [Phase 66-03]: support_status taxonomy (supported|protocol-not-implemented|adapter-required|vpp-exceeds-max) now on every chip in chip_database.json (744 chips); RURP_VPP_CEILING_MV=22000; highest-VPP-wins for NMOS combined entries (M2716/M2732=25V/vpp-exceeds-max, M2732A=21V/supported)
- [Phase 66-03]: D-11 authorized: dispatch_baseline.json regenerated to 744 chips; all 10 new chips enumerated in commit message and SUMMARY.md
- [Phase 66-03]: D-03 HARD honored: adapter-required 24-pin EEPROMs keep original proto_id, no working handler wired; check_dispatch assertion 1 confirms all 9 carry unsupported_reason
- [Phase 66-04]: CR-01 Option A applied — NON_DISPATCHABLE_ALGO=0x00 at Site B (adapter-required) + Site C (vpp-exceeds-max); dispatch(0x00, None)→ERROR; D-03 HARD enforced at data layer; DB-05 SATISFIED
- [Phase 66-04]: CR-02 applied — non_supported_dispatchable bucket in check_dispatch.py; PASS message truthful; gate now detects dangerous inverse (non-supported→real handler)
- [Phase 66-04]: IN-03 applied — 8th CI test pins SC#3 invariant; 494 tests green; cov≥70
- [Phase 66-04]: D-11 authorized deviation — 13 dispatch_baseline.json triples changed (0x0B/configure_eprom → 0x00/ERROR); reviewed and enumerated in SUMMARY.md
- [Phase 66-04]: errors bucket fix (Rule 1) — guard on chip_ss==supported so non-supported ERROR outcomes are not false-failed
- [Phase ?]: Phase 66-05: D-12 honored — ChipNotImplementedError host guard in resolve_chip closes 12V-VPP hazard; check_dispatch realigned to _map_data etype fallback; DB-05 satisfied at runtime boundary
- [Phase ?]: Phase 69-01: Inline scalar-extraction at each pin-field site — no named helper, matching database.get_bus_config pattern
- [Phase 69-02]: REAL EpromConsolePresenter(db) injection required for info tests — default Mock returns None from prepare_detailed_eprom_data and masks the ic_layout fix
- [Phase 69-02]: All three SC#3 non-supported statuses pinned at CLI: vpp-exceeds-max (M2716), adapter-required (AT28C16), protocol-not-implemented (X88C64P); info DISPLAYS all three; chip-ops refuse with typed exit 1
- [Phase 69-02]: X88C64P is the sole protocol-not-implemented chip in chip_database.json (part_number alias "X88C64P,X88C64S", protocol 0x34 XICOR NovRAM); no DB churn needed
- [Phase 69-03]: Watermark bumped 26→29: honest post-fix floor (ic_layout fix 2 new mypy errors + Phase 65 test 1); no config loosening; SC#4 full CI gate green
- [Phase 67.1-01]: D-02 Option B applied — native-28-pin SRAM block in main() loop after fm1608 override; avoids resolve_pinout_key signature change; parallels existing fm1608 override pattern
- [Phase 67.1-01]: D-01 Approach A applied — unsupported_reason strings reworded in build_db.py (Sites A/B/C); DB is single source of truth; Plan 02 will print f"{e}" verbatim
- [Phase 67.1-01]: DB-02 closed — 14 SRAM chips corrected (4 × DIP24_6116 Group 1; 10 × DIP28_JEDEC_SRAM_8K/DIP28_28C256 Group 2); diff_db: 14 SRAM_PINOUT; check_dispatch: 730/14 GREEN
- [Phase 67.1-01]: DB-04 SC#2 source half closed — reason strings begin with "VPP Xv exceeds programmer max" / "adapter required:" / "protocol not implemented:"; 520 tests green
- [Phase ?]: DB-04 Approach A: map_typed_errors renders ChipNotImplementedError reason verbatim; dropped Chip not usable prefix — DB string is single source of truth for both info display and chip-op refusal
- [Phase ?]: DB-04 SC#1 info injection gated on support_status != supported (Pitfall 3 compliance); caplog used to capture logger.warning in CliRunner tests where _setup_logging is bypassed

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| 57 | 01 | 26min | DEC-02/03/04/05 decode fixes in build_db.py; 10 new tests; ruff clean |
| 57 | 02 | 18min | GATE-03 full-class VPP guard; check_dispatch.py extended; 0 violations |
| 57 | 03 | ~45min | DB regenerated (734 chips); W27C512=100us; GATE-03 on regen set; 480 tests green |
| Phase 58 P02 | 35 | 2 tasks | 5 files |
| 59 | 02 | ~4min | GATE-04 SRAM audit; configure_sram near-no-op confirmed; 3 NVRAM truths documented; two-layer lockstep |
| Phase 61 P01 | 40min | - tasks | - files |
| Phase 62 P01 | 10min | 2 tasks | 1 files |
| Phase 62 P02 | 8min | 1 task | 1 file (dispatch_baseline.json) |
| Phase 62 P03 | 15 | 2 tasks | 1 files |
| Phase 63 P01 | 35min | - tasks | - files |
| Phase 65 P01 | 17min | - tasks | - files |
| Phase 65 P02 | 10min | 3 tasks | 3 files |
| Phase 66 P03 | 40min | 2 tasks | 5 files |
| Phase 66 P04 | 45min | 3 tasks | 7 files |
| Phase 66 P05 | 40min | - tasks | - files |
| Phase 69 P01 | 20min | 2 tasks | 5 files |
| Phase 69 P02 | 20min | 2 tasks | 2 files |
| Phase 69 P03 | 10min | 1 task (Task 1 pre-done by 69-01) | 1 file |
| Phase 67.1 P01 | 35min | 2 tasks | 3 files (build_db.py + chip_database.json + test_build_db_inclusion.py); 14 SRAM pinouts corrected; 7 new tests; 520 tests green |
| Phase 67.1 P02 | 25 | - tasks | - files |

## Deferred Items

7 items acknowledged and deferred at **v1.11 milestone close (2026-06-10)** and **re-affirmed at
v1.12 milestone close (2026-06-16)** — none are v1.11 or v1.12 work (all pre-existing / out-of-scope
/ v1.9 hardware-gated). The pre-close artifact audit at the v1.12 close surfaced the identical 7
items; operator chose Acknowledge-all and proceed. See `.planning/milestones/v1.11-MILESTONE-AUDIT.md`
and `.planning/milestones/v1.12-MILESTONE-AUDIT.md` (v1.12 also carries its own accepted tech debt:
hollow GATE-03 detector + Nyquist gaps on 6/8 phases — documented in the v1.12 audit, not repeated here).

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| debug | firmware-vpp-misread | diagnosed | Fixed in Phase 54 UAT (uno328pb R1 recal 1000→270000); session left open — close retroactively |
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 | Pre-v1.10 FRAM byte-0 write investigation; out of v1.11 scope |
| uat | Phase 08 (08-HUMAN-UAT.md) | partial (2 pending) | v1.0-era logging-infrastructure phase; out of v1.11 scope |
| verification | Phase 08 (08-VERIFICATION.md) | human_needed | v1.0-era logging phase; out of v1.11 scope |
| verification | Phase 09 (09-VERIFICATION.md) | human_needed | v1.0-era logging phase; out of v1.11 scope |
| todo | avrdude-mcu-detection-fallback.md | low | Carry-forward; out of v1.11 scope |
| todo | cobs-decoder-framelevel-deadline-wr01.md | medium | v1.10 COBS follow-up (WR-01); explicitly deferred per REQUIREMENTS.md §Future |
| ~~todo~~ | ~~w27c512-eeprom-misclassification.md~~ | ✅ RESOLVED | Closed by v1.11 decode work (Phase 57/59 cca7d62 + Phase 60); todo moved to `completed/` |
| ~~todo~~ | ~~info-list-type-vpp-divergence.md~~ | ✅ RESOLVED | Closed by Phase 61 (shared resolve_type_label + D-03 VPP parity); todo moved to `completed/` |

## Operator Next Steps

- **v1.12 SHIPPED + archived 2026-06-16.** Meta tagged `v1.12` (pushed to origin); milestone
  artifacts archived to `.planning/milestones/v1.12-*`; ROADMAP collapsed; PROJECT.md +
  RETROSPECTIVE.md evolved. Meta milestone branch merged to meta `beta`.

- **OPERATOR-GATED — lockstep beta cut (both sub-repos already merged to `beta`: fw `b71c6fd` /
  app `6b5480f`, no tag):** bump `firestarter_app` version (next pre-release) + bump the meta
  `firestarter_app` **and** `firestarter` gitlinks (intentionally pinned through v1.12 — bump at
  the cut, not per-phase) + PyPI pre-release publish + GitHub Pre-release for both repos. Firmware
  changed this milestone (first since v1.10), so a real firmware pre-release tag is expected this
  cut (not a skipped lockstep tag). Watch the py3.12-masks-CI-py3.11 ruff/codegen drift traps.
  Stable promotion stays operator-authorized ("nothing is stable until I say so").

- **Then — start the next milestone:** `/clear` then `/gsd-new-milestone` — or resume the deferred
  v1.9 read-bug RCA at `/gsd-plan-phase 45`.

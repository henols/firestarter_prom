---
gsd_state_version: 1.0
milestone: v1.13
milestone_name: — Programming Algorithm Validation + Gap Implementation
status: executing
stopped_at: Phase 76 context gathered
last_updated: "2026-06-18T11:44:46.223Z"
last_activity: 2026-06-18 -- Phase 76 execution started
progress:
  total_phases: 6
  completed_phases: 3
  total_plans: 19
  completed_plans: 17
  percent: 50
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-06-16

## Current Position

Phase: 76 (Spec-Only Gaps — adapter-required + X88C64) — EXECUTING
Plan: 2 of 2
Status: Ready to execute
Last activity: 2026-06-18 -- Phase 76 execution started

## Project Reference

See: `.planning/PROJECT.md` (v1.13 milestone section)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus (v1.13):** Test-first validation — prove the 6 existing write/program/verify
algorithm families (`configure_eprom` 0x07/08/0B, `configure_eeprom28c` 0x0D, `configure_flash3`
0x06, `configure_flash4` 0x05/35/39, `configure_flash_intel` 0x10, `configure_sram` 0x0E/27/28/29)
correct on real hardware, behind a software-first three-tier validation harness + per-family matrix,
then implement only the evidence-surfaced RURP-feasible gaps (erase path; SRAM no-op fix if
confirmed; flash4 chip-id; spec-only adapter-required + X88C64). First firmware-touching milestone
since v1.12; dual-repo lockstep; branches off `beta`, merge back to `beta`, beta→stable
operator-gated. Phase numbering continues from v1.12 (70) → v1.13 starts at **Phase 71**.

## Roadmap Summary

**v1.13 ACTIVE — 6 phases (71–76), 17/17 requirements mapped:**

- **Phase 71: Validation Harness + Matrix** (HARN-01..04) — software, flash-free spine: three-tier
  harness (Tier-1 native recording-bus stub + per-family suites; Tier-2 host wire round-trip; Tier-3
  `dev validate-family` runner) + declarative matrix + extended `check_dispatch.py` (populates the
  hollow `non_supported_dispatchable` detector, closing v1.12 tech debt); bakes in the
  Leonardo-only-PASS / negative-control / live-R1 / uno328pb-N/A oracle.

- **Phase 72: Re-research Protocol Landscape** (RSCH-01) — re-enumerate feasibility verdicts BEFORE
  any flash-budget firmware commit; reaffirm-or-overturn v1.12's "feasible set complete"; re-confirm
  anti-features fail-closed.

- **Phase 73: Bench-Validate the 6 Families on Leonardo** (VAL-01..06) — hybrid-gated; Tier 1/2
  always, Tier 3 on parts-on-hand (SKIP-deferred otherwise); resolves the SRAM no-op question
  (feeds FIX-01). Standing bench precondition applies.

- **Phase 74: Per-Family Correctness Fixes** (FIX-01..03) — flash-gated RED→GREEN: SRAM real
  read/write IF VAL-06 confirms the no-op (else closed-with-evidence); flash4 `CMD_CHECK_CHIP_ID`;
  0x39 stale-comment + 2-chip coverage. Fixes-before-additions; `-e leonardo` ceiling held.

- **Phase 75: Erase Path** (ERASE-01) — `firestarter erase W27C512` host `FLAG_CAN_ERASE` routing to
  existing `eprom_internal_erase` electricals + 12V→14V rail confirm under 22V ceiling + datasheet
  preconditions; chip-OUT VPP meter dry-run. Leonardo-closeable. Research-flagged for planning.

- **Phase 76: Spec-Only Gaps** (GAP-01, GAP-02) — adapter-required AT28C04/16 pin-map spec +
  `resolve_pinout_key` arm (stays `adapter-required`); X88C64 0x34 datasheet feasibility verdict
  (handler only if fully spec'd). Graduation to `supported` is OUT of scope. Research-flagged.

**Critical ordering (research + flash-ceiling driven):** harness → re-research → validate → fix →
gaps. Tiers 1–3 of Phases 71–73 are flash-free; only Phases 74–76 consume the ~88% Leonardo flash
ceiling → fixes-before-additions, adapter-required last. RSCH-01 lands before any firmware commit.

**Hybrid bench gating:** Tier 1 (native) + Tier 2 (host) ungated software; Tier 3 (HIL) Leonardo-only
valid-PASS, closeable at PARTIAL bench coverage (matrix records SKIP/deferred cells).

**Standing bench precondition (every hardware phase — 73, 75, Tier-3 halves of 74/76):** Leonardo
is the ONLY valid-PASS verify board (v1.9 read bug corrupts the oracle on Rev-0/Rev-2.0);
**uno328pb is N/A for program/write** (999.2 brownout); live R1/R2 readback (`r1 ≈ 270000`) each task
(rules out 999.1 stale-cal); chip-OUT before any Uno-class sideload (Leonardo exempt); ASK which
shield rev; verify `controller:` port identity per task.

**Flash budget at v1.13 start (carry from v1.12):** Leonardo ~88% (~25,354 B / 28,672 B,
~3,318 B remaining); Uno 72.4% — the harness adds ZERO production flash; only FIXES + handlers
consume the ceiling.

**Prior milestones:** v1.12 SHIPPED 2026-06-16 (Phases 62–70; dual-repo lockstep on `beta`, no tag —
fw `b71c6fd` / app `6b5480f`; lockstep beta cut + stable operator-gated). v1.11 SHIPPED 2026-06-10.
v1.10 SHIPPED 2026-06-07. v1.9 Read-Bug RCA DEFERRED (Phases 45–48; resume at Phase 45).

## Accumulated Context

### Roadmap Evolution

- v1.13 roadmap created 2026-06-16: 6 phases (71–76) derived from the HARN/RSCH/VAL/FIX/ERASE/GAP
  requirements along the research-derived harness→validate→fix→gaps spine, flash-ceiling-ordered.
  17/17 requirements mapped, no orphans/duplicates. FIX-01 (SRAM) is evidence-gated on VAL-06;
  GAP-01/02 are spec-only (graduation to `supported` deferred). RSCH-01 (Phase 72) lands before any
  flash-budget firmware commit. Phases 75 + 76 flagged for `--research-phase` at planning (erase
  12V→14V rail; X88C64 0x34 protocol; DIP24 adapter pin-map).

### v1.13 Scope Notes (research 2026-06-16, HIGH confidence)

- **No new third-party deps** — both substrates installed + green: firmware native = PlatformIO
  `[env:native]` + Unity + ArduinoFake `^0.4.0` (8 suites passing); host = pytest + syrupy + ruff/mypy

  + pyserial with `make_comm`/`fake_serial` no-port fixtures. REUSE `write_test.sh`,
  `eprom_operations.py` cycle methods, `check_dispatch.py`, `diff_db.py` — do NOT rewrite/fork.

- **v1.12 "feasible set complete" overstated** — 3 genuine RURP-feasible gaps survive: erase path
  (0x07, electricals exist), `configure_sram` empty no-op (validate-first), X88C64 0x34
  (parallel 5V DIP EEPROM, MEDIUM — needs datasheet protocol). Anti-features stay fail-closed.

- **Two coupled failure classes dominate:** false-PASS (untrustworthy verify read board → pin PASS
  to Leonardo + clean shield, N≥5 SHA, negative control) and chip-destruction (wrong VPP/algorithm →
  register-bit native tests via recording stub + chip-OUT VPP meter dry-run, never bypass host guard).

- **999.1 / 999.2 are confounders, not in-scope fixes** — live R1/R2 readback at every VPP-dependent
  bench task is the discriminator; uno328pb = N/A for program/write.

### ⏸ v1.9 DEFERRED (operator 2026-06-08 — resumes later at Phase 45)

v1.9 (Read-Bug RCA + Fix) is paused. Phase 44 (Bug A RCA) complete; Phase 48 plan 48-01 (COBS
verdict) complete. Remaining: Phases 45–48. The v1.13 verify oracle is pinned to Leonardo precisely
to avoid the v1.9 shield-fleet read bug; v1.13 does NOT touch it.

### v1.10 Substrate (carry-forward)

- Transport provably byte-exact (COBS `0x00` + CRC8-CCITT) — settled variable.
- GATE-1.8d ring-fence: `_read_and_parse_lines` body byte-identical; baseline binaries valid.

### Pending Todos (carried forward)

- `avrdude-mcu-detection-fallback.md` (low) — out of scope, carry forward
- `cobs-decoder-framelevel-deadline-wr01.md` (medium) — v1.10 COBS follow-up; deferred
- `large-read-data-jitter-uno328pb.md` (HIGH, v1.8-seed) — v1.9 RCA target (NOT v1.13)

### Blockers / Concerns

None at roadmap start. v1.13 closes at PARTIAL bench coverage under hybrid gating — Tier 1/2 are
fully software-provable; Tier 3 is best-effort on parts-on-hand. Dual-repo lockstep (firmware + host)
applies to any wire-touching fix; watch the py3.12-masks-CI-3.11 ruff/codegen drift trap.

## Session Continuity

Last session: 2026-06-18T11:44:39.756Z
Stopped at: Phase 76 context gathered
Resume: `/gsd-plan-phase 71`

## Decisions

_(v1.13 decisions will be recorded here as phases execute.)_

<details>
<summary>v1.12 decisions (archived — milestone shipped 2026-06-16)</summary>

- [Phase 62-01]: D-BETA-STATE: beta branch already has 0x35/0x39 explicit dispatch arms; TestDispatchGate02 tests 1+2 are GREEN now (not RED as planned); only protocol!=0 not_implemented arm is missing
- [Phase 62-02]: D-CHIP-COUNT: DB on v1.12 branch has 734 chips (not 743 as plan expected) — v1.11 work not yet reconciled into beta; dispatch_baseline.json correctly captures the actual current DB state
- [Phase 63-01]: D-01 honored (0xBB mirrors 0xAE); D-04 honored (py3.11.13 from source, drift gates green); D-05 honored (firestarter_app gitlink not bumped)
- [Phase 65-01]: _raise_for_error_response(response, message): response.id for typed dispatch, message for EpromOperationError framing
- [Phase 65-01]: SC#2 test asserts on _execute_phase — outer _run_state_machine except swallows typed raise before caller sees it
- [Phase 65-01]: GATE-1.8d ringfence pin updated for planned Response.id addition (v1.12 in-scope)
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
- [Phase 66-05]: D-12 honored — ChipNotImplementedError host guard in resolve_chip closes 12V-VPP hazard; check_dispatch realigned to _map_data etype fallback; DB-05 satisfied at runtime boundary
- [Phase 69-01]: Inline scalar-extraction at each pin-field site — no named helper, matching database.get_bus_config pattern
- [Phase 69-02]: REAL EpromConsolePresenter(db) injection required for info tests — default Mock returns None from prepare_detailed_eprom_data and masks the ic_layout fix
- [Phase 69-02]: All three SC#3 non-supported statuses pinned at CLI: vpp-exceeds-max (M2716), adapter-required (AT28C16), protocol-not-implemented (X88C64P); info DISPLAYS all three; chip-ops refuse with typed exit 1
- [Phase 69-02]: X88C64P is the sole protocol-not-implemented chip in chip_database.json (part_number alias "X88C64P,X88C64S", protocol 0x34 XICOR NovRAM); no DB churn needed
- [Phase 69-03]: Watermark bumped 26→29: honest post-fix floor (ic_layout fix 2 new mypy errors + Phase 65 test 1); no config loosening; SC#4 full CI gate green
- [Phase 67.1-01]: D-02 Option B applied — native-28-pin SRAM block in main() loop after fm1608 override; avoids resolve_pinout_key signature change; parallels existing fm1608 override pattern
- [Phase 67.1-01]: D-01 Approach A applied — unsupported_reason strings reworded in build_db.py (Sites A/B/C); DB is single source of truth; Plan 02 will print f"{e}" verbatim
- [Phase 67.1-01]: DB-02 closed — 14 SRAM chips corrected (4 × DIP24_6116 Group 1; 10 × DIP28_JEDEC_SRAM_8K/DIP28_28C256 Group 2); diff_db: 14 SRAM_PINOUT; check_dispatch: 730/14 GREEN
- [Phase 67.1-01]: DB-04 SC#2 source half closed — reason strings begin with "VPP Xv exceeds programmer max" / "adapter required:" / "protocol not implemented:"; 520 tests green
- [DB-04 Approach A]: map_typed_errors renders ChipNotImplementedError reason verbatim; dropped Chip not usable prefix — DB string is single source of truth for both info display and chip-op refusal
- [DB-04 SC#1]: info injection gated on support_status != supported (Pitfall 3 compliance); caplog used to capture logger.warning in CliRunner tests where _setup_logging is bypassed

</details>

- [Phase 71]: HARN-03 closure: TRUST write_cycle_eprom return code directly; verdict_int==0 maps to board-class PASS via pass_type field, no source==source self-compare
- [Phase 71-08]: CR-02 resolution: flash4 host matrix trimmed to protocols=[5]; 0x35/0x39 omitted (zero DB chips, host never dispatches); rationale in protocols_note; firmware truth + native coverage preserved in test_val_flash4.cpp; drift gate green at 11 rows
- [Phase ?]: A1-RESOLVED: standalone erase already reaches eprom_internal_erase; Phase 75 scope = wire FLAG_CAN_ERASE from electrical.type in convert_to_programmer
- [Phase ?]: A2-RESOLVED: 0x2B is GAL/PLD family (memory.cpp:107-110); protocol-id.md lacks 0x2B row (documentation debt)
- [Phase ?]: SRAM-VERDICT: 0x0E/0x27/0x28/0x29 classified feasible-and-implemented (behavior deferred Phase 73 VAL-06); generic memory_write_execute fires before configure_sram
- [Phase ?]: V1.12-OVERSTATED: 3 areas - SRAM no-op (sram.cpp:15-17), FLAG_CAN_ERASE routing gap (database.py:594-597), X88C64 0x34 feasible-gap
- [Phase ?]: [Phase 73-01]: firestarter config -r1 writes to Arduino EEPROM only; r1 gate armed by writing r1=270000 directly to ~/.firestarter/config.json
- [Phase ?]: 73-02: A1-CONFIRMED: W27C512 erase fires correctly in write_cycle_eprom; Tier-3 PASS authoritative on Leonardo
- [Phase 73-03]: DEV: flash3/AM29F040 SKIP-deferred (no chip, operator 2026-06-17); flash4/W29C040 FAIL (hw-error): erase doesn't produce 0xFF blank, write verification timeout → Phase-74 candidate
- [Phase 73-03]: configure_flash4 (algorithm 5) incompatible with W29C040 SDP/page-write sequence; erase "succeeds" but chip not erased to 0xFF; write init blank-check fails; standalone write -b times out at 0x3f
- [Phase ?]: VAL-06 = table-stakes-PASS: configure_sram writes via generic_memory_write_execute; FIX-01 closed not-needed with evidence
- [Phase ?]: FM1608 erase probe: exit 1 (Not supported) — configure_sram CMD_ERASE errors; write -b direct path is the only viable FRAM write approach (Pitfall 3 confirmed)
- [Phase ?]: D-03 named arm fires AFTER Site B to overwrite generic reason with named-arm wording referencing AT28C04-ADAPTER.md; proto_id demotion stays in Site B
- [Phase ?]: D-02 X88C64P reason: parallel DIP24 5V EEPROM, 8051 multiplexed-bus (ALE/WR/RD); feasible-candidate, handler not implemented; no support_status change

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| _(v1.13 metrics recorded here as plans execute)_ | | | |

<details>
<summary>v1.11 / v1.12 performance metrics (archived)</summary>

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| 57 | 01 | 26min | DEC-02/03/04/05 decode fixes in build_db.py; 10 new tests; ruff clean |
| 57 | 02 | 18min | GATE-03 full-class VPP guard; check_dispatch.py extended; 0 violations |
| 57 | 03 | ~45min | DB regenerated (734 chips); W27C512=100us; GATE-03 on regen set; 480 tests green |
| 58 | 02 | 35min | 2 tasks / 5 files |
| 59 | 02 | ~4min | GATE-04 SRAM audit; configure_sram near-no-op confirmed; 3 NVRAM truths documented |
| 61 | 01 | 40min | — |
| 62 | 01 | 10min | 2 tasks / 1 file |
| 62 | 02 | 8min | 1 task / dispatch_baseline.json |
| 62 | 03 | 15min | 2 tasks / 1 file |
| 63 | 01 | 35min | — |
| 65 | 01 | 17min | — |
| 65 | 02 | 10min | 3 tasks / 3 files |
| 66 | 03 | 40min | 2 tasks / 5 files |
| 66 | 04 | 45min | 3 tasks / 7 files |
| 66 | 05 | 40min | — |
| 69 | 01 | 20min | 2 tasks / 5 files |
| 69 | 02 | 20min | 2 tasks / 2 files |
| 69 | 03 | 10min | 1 task / 1 file |
| 67.1 | 01 | 35min | 2 tasks / 3 files; 14 SRAM pinouts corrected; 7 new tests; 520 tests green |
| 67.1 | 02 | 25min | — |

</details>
| Phase 71 P07 | 8min | 2 tasks | 3 files |
| Phase 71 P08 | 7min | 2 tasks | 4 files |
| Phase 72 P01 | 45min | - tasks | - files |
| Phase 73 P02 | 3min | - tasks | - files |
| Phase 73 P03 | 8min | 1 task | 6 files (flash3 SKIP-deferred + flash4 FAIL verdict W29C040) |
| Phase 73 P04 | 8min | - tasks | - files |
| Phase 74 P01 | 3min | 2 tasks | 4 files |
| Phase 76 P01 | 8min | 3 tasks | 3 files |

## Deferred Items

7 items acknowledged and deferred at **v1.11 milestone close (2026-06-10)** and re-affirmed at
**v1.12 milestone close (2026-06-16)** — none are v1.11/v1.12 work (all pre-existing / out-of-scope /
v1.9 hardware-gated). v1.13 *guards against* 999.1/999.2 as confounders (live-R1 precondition,
uno328pb=N/A) but does NOT fix them. See `.planning/milestones/v1.11-MILESTONE-AUDIT.md` +
`.planning/milestones/v1.12-MILESTONE-AUDIT.md`.

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| debug | firmware-vpp-misread (999.1) | diagnosed | uno328pb R1 recal applied Phase 54 UAT; CONFIG_VERSION propagation gate = ROADMAP Backlog 999.1; v1.13 guards via live-R1 precondition |
| debug | uno328pb program brownout (999.2) | parked | ROADMAP Backlog 999.2; v1.13 marks uno328pb N/A for program/write |
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 | Pre-v1.10 FRAM byte-0 write investigation; out of v1.13 scope |
| uat | Phase 08 (08-HUMAN-UAT.md) | partial (2 pending) | v1.0-era logging phase; out of scope |
| verification | Phase 08 / Phase 09 VERIFICATION.md | human_needed | v1.0-era logging phases; out of scope |
| todo | avrdude-mcu-detection-fallback.md | low | Carry-forward; out of scope |
| todo | cobs-decoder-framelevel-deadline-wr01.md | medium | v1.10 COBS follow-up (WR-01); deferred |

## Operator Next Steps

- **v1.13 roadmap created (2026-06-16).** 6 phases (71–76), 17/17 requirements mapped, no orphans.
  ROADMAP.md (active v1.13 section + phase details + Milestones list + Progress table) +
  REQUIREMENTS.md traceability + STATE.md written. Prior-milestone collapsed sections + Backlog
  999.1/999.2 preserved.

- **Next:** `/gsd-plan-phase 71` (Validation Harness + Matrix — software, flash-free, un-gated).
  Phases 75 + 76 flagged for `--research-phase` at planning time.

- **Branch model reminder:** branches off `beta` in all 3 repos; merge back to `beta`; beta cut +
  stable promotion operator-gated. First firmware-touching milestone since v1.12 — dual-repo lockstep
  (meta-repo `messages.toml` only → regen both sub-repos) for any wire change; watch the
  py3.12-masks-CI-3.11 ruff/codegen drift trap; firmware phases carry a `pio run -e leonardo` flash-%
  ceiling criterion.

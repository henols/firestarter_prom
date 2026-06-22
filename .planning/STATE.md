---
gsd_state_version: 1.0
milestone: v1.14
milestone_name: — Feasible-Gap Implementation
status: executing
stopped_at: Phase 79 Plan 01 hardware gate NOT CLEARED (VPP ~12V < 25V) — Plans 02/03 BLOCKED
last_updated: "2026-06-22T13:57:30.054Z"
last_activity: 2026-06-22 -- Phase 79 hardware gate (NMOS-01) evaluated: NOT CLEARED
progress:
  total_phases: 4
  completed_phases: 2
  total_plans: 9
  completed_plans: 7
  percent: 56
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-06-16

## Current Position

Phase: 79 (25v-nmos-ceiling-raise) — HALTED at Plan 01 (hardware gate NOT CLEARED)
Plan: 1 of 3 (79-01 done with NOT-CLEARED verdict; 79-02/79-03 BLOCKED)
Status: Hardware gate NMOS-01 failed — chip-OUT VPP dry-run measured ~12V at socket (firmware 12.3V), < 25V required. Plan 02 ceiling change NOT authorized. Phase cannot proceed until the bench VPP rail reaches ≥25V (PCB feedback-resistor change most likely) and the chip-OUT gate re-runs to CLEARED.
Bench: leonardo @ /dev/ttyACM0, fw 3.0.0b8, shield Rev 2.0 (operator silkscreen), R1=270000/R2=44000
Last activity: 2026-06-22 -- Phase 79 hardware gate (NMOS-01) evaluated: NOT CLEARED
Sub-repo branch: firestarter_app on `v1.14-feasible-gap-implementation` (off beta); source commits inside submodule; meta gitlink PINNED until beta cut. NO source/DB changes made in Phase 79 (gate blocked Plan 02).

## Project Reference

See: `.planning/PROJECT.md` (Current Milestone: v1.14 section)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus (v1.14):** Graduate chips to `supported` by implementing the four
evidence-surfaced, RURP-feasible gaps v1.13 scoped out — the first chips to become newly
programmable since v1.0. Build order 999.4 → 999.5 → 999.7 → 999.6 (operator-locked):
Phase 77 erase write-path (host-only, most-ready), Phase 78 X88C64 0x34 firmware handler (the
only firmware-adding gap; dual-repo lockstep; flash-gated; ALE-routing investigation first),
Phase 79 25V NMOS ceiling raise (host-only; operator multimeter ≥25V dry-run first), Phase 80
AT28C04/16 adapter graduation (host-only but hardware-blocked on the adapter; last). Each
graduation removes the v1.12 `chip_resolver` host-guard refusal as the FINAL step, gated behind
native register-bit tests + wire round-trip + Leonardo bench proof (SAFE-01/02/03). Branches off
`beta` in all 3 repos, merge back to `beta`; beta→stable operator-gated. Phase numbering continues
from v1.13 (76) → v1.14 starts at **Phase 77**.

## Roadmap Summary

**v1.14 ACTIVE — 4 phases (77–80), 15/15 requirements mapped:**

- **Phase 77: Erase Write-Path Graduation** (ERASE-01, ERASE-02 + cross-cutting SAFE-01/02/03) —
  host-only, most-ready. Wire `FLAG_CAN_ERASE` from `electrical.type=="EEPROM"` (not the always-zero
  `info-flags & 0x10`) in `database.py::convert_to_programmer` so the 7–8 0x07 EE-EPROMs auto-erase
  before write; firmware `eprom_write_init` guard already honors the flag. Bench-confirm
  write→erase→program→verify on Leonardo with W27C512 (14V erase-rail chip-OUT VPP dry-run first).
  This is the skipped v1.13 Phase 75; establishes the SAFE-01/02/03 graduation-gate-last pattern.

- **Phase 78: X88C64 0x34 Firmware Handler** (XIC-01..04) — the ONLY firmware-adding gap →
  dual-repo lockstep. **ALE-routing bench investigation is the FIRST plan** (Assumption A6 LOW
  confidence; if PCB-blocked, X88C64 defers as FUT-01 and the phase still closes). Then
  `configure_x88c64` (8051 multiplexed bus, page write ≤32 B, toggle-bit I/O6 polling) registered in
  `memory.cpp` **before** the `protocol != 0 → configure_not_implemented` guard. `pio run -e leonardo`
  ≤ ~90% flash is a gate (~3 KB headroom). Graduate X88C64P after N≥5 Leonardo write+read-back.

- **Phase 79: 25V NMOS Ceiling Raise** (NMOS-01..03) — host-only but hardware-gated.
  **Operator multimeter ≥25V chip-OUT dry-run is the FIRST plan (`autonomous: false`)** before the
  constant changes (the 22V ceiling reflects a rail/calibration limit; firmware does NO runtime VPP
  enforcement). Then `RURP_VPP_CEILING_MV` 22000→25000 + `check_dispatch.py` invariant; re-classify +
  graduate the 4 NMOS chips (INTEL M2716/M2732, SGS-THOMSON ETC2716, ST M2716). M2732A (21V) already
  supported; >25V chips stay fail-closed (FUT-02).

- **Phase 80: AT28C04/16 Adapter Graduation** (ADPT-01..03) — host-only software but
  HARDWARE-BLOCKED on the physical adapter → sequenced last; defers cleanly without blocking 77–79.
  **Build the DIP24→DIP32 adapter + DMM /WE-reroute continuity check FIRST** (chip pin 21 → socket
  pin 30 vs `DIP32_28C512_EEPROM`). Then wire the 9 chips through the existing `configure_eeprom28c`
  (0x0D, VPP-free) handler; remove the `_AT28C_DIP24_NAMES` arm + the `adapter-required` refusal;
  graduate after a golden Leonardo write+read-back round-trip with the adapter seated.

**Build order (operator-locked 2026-06-18):** 999.4 → 999.5 → 999.7 → 999.6 (= Phase 77 → 78 → 79 →
80). PITFALLS noted a defensible flash-headroom swap (25V before X88C64); operator-captured order
stands. Three of four gaps are HOST-ONLY / zero firmware flash; only Phase 78 consumes the ceiling.

**Cross-cutting safety (SAFE-01/02/03, mapped to Phase 77, recur in 78–80):** each graduation removes
the v1.12 `chip_resolver.resolve_chip` host-guard refusal **as the FINAL step**, gated behind native
register-bit (recording-stub) tests + host wire round-trip + a Leonardo bench proof (chip-OUT VPP
multimeter dry-run first); `check_dispatch.py` full-DB VPP-safety gate passes after each; any `FLAG_*`/
protocol constant touched in `constants.py` + `firestarter.h` changes in lockstep (parity tests green).

**Standing bench precondition (every hardware phase 77–80):** **Leonardo is the ONLY trustworthy
program/write/verify board** (v1.9 read bug corrupts the oracle on Rev-0/Rev-2.0); **uno328pb is N/A
for program/write** (999.2 brownout); live R1/R2 readback (`r1 ≈ 270000`) each task; chip-OUT before
any Uno-class sideload (Leonardo exempt); **ASK which silkscreen shield rev is mounted**; verify
`controller:` port identity per task.

**Flash budget at v1.14 start:** Leonardo ~89.5% / ~3 KB free post-v1.13. Only the Phase 78 X88C64
handler (~1–3 KB) consumes it → measured `pio run -e leonardo` ≤ ~90% gate.

**Pre-req:** v1.13's `3.0.0b10` lockstep beta cut is operator-gated; v1.14 branches off `beta` once it
has landed in both sub-repos. Branch setup is folded into Phase 77 (no thin precursor phase).

**Prior milestones:** v1.13 SHIPPED 2026-06-18 (Phases 71–76; dual-repo lockstep on `beta` — fw
`a33513f` / app `34deccb` @ `3.0.0b9`, no tag). v1.12 SHIPPED 2026-06-16. v1.11 SHIPPED 2026-06-10.
v1.10 SHIPPED 2026-06-07. v1.9 Read-Bug RCA DEFERRED (Phases 45–48; resume at Phase 45).

## Accumulated Context

### Roadmap Evolution

- v1.14 roadmap created 2026-06-18: 4 phases (77–80) derived from the 15 v1.14 requirements
  (ERASE/XIC/NMOS/ADPT/SAFE) — one phase per feasible gap along the operator-locked build order
  999.4 → 999.5 → 999.7 → 999.6. 15/15 mapped, no orphans/duplicates. SAFE-01/02/03 cross-cutting,
  mapped to Phase 77 (first graduation establishing guard-removal-last + check_dispatch + lockstep
  parity) and recurring as success criteria in 78–80. Each phase's graduation gate (flip
  `support_status`→`supported` + drop the host guard) is the FINAL step. Phase 78 (X88C64) leads
  with an ALE-routing bench investigation + a `pio run -e leonardo` ≤~90% flash gate; Phase 79 (25V)
  leads with an `autonomous: false` operator multimeter ≥25V dry-run; Phase 80 (adapter) is
  hardware-blocked and defers cleanly. The ROADMAP §v1.14 Backlog stubs 999.4–999.7 were promoted
  (marked ✅ PROMOTED → Phase 77/78/79/80) and removed from the pending backlog.

- v1.14 captured to Backlog 2026-06-18 (operator request): 4 feasible-gap **implementation** phases that
  graduate chips to `supported` (OUT of v1.13's validation-only scope) → ROADMAP §Backlog 999.4–999.7.
  999.4 erase write-path (skipped v1.13 Phase 75, most ready), 999.5 X88C64 0x34 handler, 999.6 AT28C04/16
  adapter graduation (hardware-blocked), 999.7 25V NMOS M2716/M2732 ceiling raise (was infeasible at 22V —
  operator opted to implement assuming HW can do 25V; gating risk = confirm a shield can produce 25V VPP).
  Promote via `/gsd-new-milestone v1.14` after v1.13 close (operator-gated beta cut still pending), NOT into v1.13.

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

Last session: 2026-06-22T13:57:30.054Z
Stopped at: Phase 79 Plan 01 hardware gate NOT CLEARED — VPP ~12V at socket (< 25V); Plans 02/03 BLOCKED
Resume: hardware remediation required FIRST (raise bench VPP rail to ≥25V — PCB feedback-resistor change most likely; R1 recal unlikely since firmware 12.3V and DMM ~12V agree, so the scaling is correct and the rail is genuinely at the 12V setpoint). Then re-run `/gsd-execute-phase 79` to re-evaluate the chip-OUT gate; only a CLEARED ≥25V verdict authorizes Plan 02 (ceiling 22000→25000) and Plan 03 (graduation bench proof).

## Decisions

- [Phase 79-01]: NMOS-01 HARDWARE GATE = NOT CLEARED. Chip-OUT VPP dry-run on leonardo @ /dev/ttyACM0, shield Rev 2.0 (operator silkscreen), R1=270000/R2=44000: `firestarter vpp` read steady 12.3V (default 12V EPROM setpoint, no parameter to request 25V), operator multimeter confirmed ~12V at the socket VPP pin — both ≪ 25000 mV. Firmware does NO runtime VPP-ceiling enforcement (79-RESEARCH.md Q3), so this physical measurement is the only safety boundary; it correctly blocked the Plan 02 ceiling raise. Plans 79-02/79-03 BLOCKED pending a ≥25V re-run. Mirrors the Phase 78 DEFER discipline (gate caught a blocker; phase halts cleanly, no code/DB change).

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
- [Phase ?]: D-04: two-layer adapter spec (firestarter/doc/ + .planning/), pin-map verified, /WE reroute chip pin 21 → socket pin 30, DIP32_28C512_EEPROM confirmed
- [Phase ?]: D-01: X88C64P NO STORE/RECALL pins (those are X2210/X2212 NOVRAM family); X88C64P is parallel DIP24 with 8051 multiplexed ALE/WR/RD bus; MEDIUM feasibility-candidate; handler deferred, 0x34 not committed
- [Phase ?]: [Phase 78-01]: A6 VERDICT PCB-BLOCKED (HIGH) — control register fully allocated 0x01..0x80 (rurp_pinout.h:74-97); 0x100 non-transmissible via uint8_t rurp_write_data_buffer (rurp_shield.h:118); no free 74HC573 strobe; D-02 bar prohibits busy-bit reuse. Plan 02 takes deferral branch.
- [Phase ?]: [Phase 78-01]: XIC-04 graduation deferred to FUT-01 — no physical X88C64P chip/adapter (D-04) + PCB-blocked ALE; X88C64 stays protocol-not-implemented + host-refused; SAFE-01/02/03 hold trivially (no code change).
- [Phase 78-02]: Contingent handler-write plan took DEFER branch (Branch A) — leading [BLOCKING] gate read A6 VERDICT: PCB-BLOCKED directly; D-02 prohibits busy-bit reuse so proceed-path unauthorized. Appended `Branch A — ALE PCB-blocked, no handler code; graduation deferred FUT-01.` to X88C64-FEASIBILITY.md; Tasks 2-5 skipped; firestarter src/include/test + firestarter_app pinouts/DB/chip_resolver all CLEAN; X88C64P support_status unchanged (protocol-not-implemented); host-guard intact. XIC-02/03 vacuous on this branch.

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
| Phase 76 P02 | 12min | - tasks | - files |
| Phase 78 P01 | 12min | 2 tasks | 1 files |
| Phase 78 P02 | 6min | 1 task | 1 files (DEFER branch — zero code changes) |

## Deferred Items

9 items acknowledged and deferred at **v1.13 milestone close (2026-06-18)** (carrying 7 re-affirmed
from the v1.11 2026-06-10 / v1.12 2026-06-16 closes, plus 2 v1.13-surfaced) — none are v1.13 work
(all pre-existing, out-of-scope, accepted tech debt, or hardware-gated). v1.13 *guards against*
999.1/999.2 as confounders (live-R1 precondition, uno328pb=N/A) but does NOT fix them. See
`.planning/milestones/v1.11-MILESTONE-AUDIT.md` + `.planning/milestones/v1.12-MILESTONE-AUDIT.md`.

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| debug | firmware-vpp-misread (999.1) | diagnosed | uno328pb R1 recal applied Phase 54 UAT; CONFIG_VERSION propagation gate = ROADMAP Backlog 999.1; v1.13 guards via live-R1 precondition |
| debug | uno328pb program brownout (999.2) | parked | ROADMAP Backlog 999.2; v1.13 marks uno328pb N/A for program/write |
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 | Pre-v1.10 FRAM byte-0 write investigation; out of v1.13 scope |
| uat | Phase 08 (08-HUMAN-UAT.md) | partial (2 pending) | v1.0-era logging phase; out of scope |
| verification | Phase 08 / Phase 09 VERIFICATION.md | human_needed | v1.0-era logging phases; out of scope |
| todo | avrdude-mcu-detection-fallback.md | low | Carry-forward; out of scope |
| todo | cobs-decoder-framelevel-deadline-wr01.md | medium | v1.10 COBS follow-up (WR-01); deferred |
| todo | flash4-page-size-datasheet-sourced-cr01.md | medium | v1.13 Phase 74 CR-01 — data-driven page size shipped; replace residual capacity heuristic with datasheet per-chip value (refinement) |
| verification | Phase 71 (71-VERIFICATION.md) | gaps_found (stale) | Both verifier gaps CLOSED by follow-up plans 71-07 (non-vacuous oracle) + 71-08 (flash4 spec-trim); status line never re-run |
| phase-deferral | Phase 74 Wave-2 (W29C040 HW re-bench) + Phase 75 (erase path) | deferred to v1.14 | Backlog 999.4; hardware-gated (Leonardo+Rev2.0 T-74-VPP multimeter gate; erase 12V→14V rail confirm under 22V ceiling) |
| phase-deferral | Phase 79 NMOS-02/03 (25V ceiling raise + NMOS graduation) | hardware-blocked (FUT-03) | NMOS-01 gate NOT CLEARED 2026-06-22 (bench VPP ~12V at socket < 25V); AP3012 boost setpoint physically ~12V, needs a PCB feedback-resistor change to reach ≥25V (R1/R2 only scale ADC). Resume `/gsd-execute-phase 79` after the PCB change re-achieves a CLEARED ≥25V chip-OUT dry-run. Evidence: 79-01-SUMMARY.md |

## Operator Next Steps

- **Phase 79 is hardware-blocked (FUT-03).** To unblock: change the VPP boost-converter feedback resistor(s) on the shield so `firestarter vpp` (chip-OUT) reaches ≥25V at the socket pin, then re-run `/gsd-execute-phase 79` — the NMOS-01 gate re-evaluates and only a CLEARED ≥25V verdict authorizes the ceiling raise + graduation.
- **Phase 79 cannot ship in v1.14 without that hardware change.** Decision needed: (a) do the PCB resistor change now and resume, or (b) defer Phase 79 to a future milestone (FUT-03) and proceed to Phase 80 (AT28C04/16 adapter) so v1.14 still closes with 77/78/80.
- Phases 78 + 79 both await `/gsd-verify-phase` + `/gsd-secure-phase` where applicable (78 verified PASSED; 79 halted pre-verify by the gate).
- **Phase 80 (AT28C04/16 adapter graduation) is PLANNED** (2026-06-22): 4 plans verified PASSED (research + Nyquist VALIDATION committed). Host-only, mirrors the Phase 77 graduation pattern; hardware-gated on building the DIP24→DIP32 adapter (Plan 01 DMM continuity gate) — defers cleanly (FUT-04) if the adapter/AT28C chip is absent. Execute with `/gsd-execute-phase 80`. Plan 01 will ASK whether the adapter is built + whether an AT28C04/16 chip is on hand.

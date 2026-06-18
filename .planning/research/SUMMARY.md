# Project Research Summary

**Project:** Firestarter v1.13 — Programming Algorithm Validation + Gap Implementation
**Domain:** Firmware write/program/verify algorithm validation (test-first, hybrid native + hardware-in-the-loop) + evidence-driven gap implementation on an Arduino RURP EPROM/Flash/EEPROM/SRAM programmer
**Researched:** 2026-06-16
**Confidence:** HIGH

## Executive Summary

v1.13 is a **test-first validation milestone, not a feature build**. The 6 write/program algorithm families (`configure_eprom` 0x07/08/0B, `configure_flash3` 0x06, `configure_flash4` 0x05/35/39, `configure_flash_intel` 0x10, `configure_eeprom28c` 0x0D, `configure_sram` 0x0E/27/28/29) already exist and dispatch; the milestone must *prove them correct on real silicon* behind a reusable, **software-first** validation harness + a declarative per-family validation matrix, then implement only the gaps that testing + re-research actually surface. All four researchers converged on the same spine: a **three-tier test pyramid** — Tier 1 native Unity (`pio test -e native`, ArduinoFake + recording register stub, zero production flash), Tier 2 host pytest wire round-trip (`make_comm`/`fake_serial`, no serial port), Tier 3 host-driven HIL bench (hybrid-gated, Leonardo as the only trusted verify board). Crucially, **almost nothing new is needed** — both test stacks are installed and proven; the genuine new work is a matrix data file, per-family native suites, golden wire-vectors + golden `.bin` images, a matrix-driven bench runner (a generalization of `write_test.sh`), and a `hardware` pytest marker. **Reuse existing infra — `write_test.sh`, `eprom_operations.py` `write_cycle_eprom`/`consistency_check_eprom`, `check_dispatch.py`, `diff_db.py` — do NOT rewrite or fork.**

The dominant risks are **coupled and unforgiving: false-pass and chip-destruction**. The verify oracle is a read, and the read path is the v1.9-deferred read bug on 2 of 3 shields plus uno328pb drift — so **only Leonardo + a clean shield is a valid PASS**; everything else is advisory. Worse, native dispatch tests assert operation-pointers, NOT register side-effects, so a wrong-VPP bug compiles, passes tests, and only manifests as a fried chip on the bench — the milestone must add **register-bit native tests (recording stub) + a chip-OUT VPP multimeter dry-run** before any seated write. Two calibration/board confounders (999.1 stale-R1 VPP misread; 999.2 uno328pb program brown-out) masquerade as algorithm bugs and must be ruled out by a live R1/R2 readback at every VPP-dependent bench task; **uno328pb is N/A for any program/write test**. A vacuous verify (cached buffer, no negative control) is a third false-pass vector — PASS must require an independent post-write full read + SHA compare + a negative control that proves verify *can* fail.

v1.12's "feasible set is complete" was **overstated**. Three genuine gaps exist: (1) the **erase path** (`firestarter erase` W27C512 0x07) — firmware electricals already exist (`eprom_internal_erase` drives VPE+A9), so the gap is mostly host-side wiring + a 12V→14V rail detail (under the 22V ceiling); (2) **`configure_sram` is an empty no-op** yet 20+ chips report `supported` — validate-first, likely a correctness bug (writes may silently succeed-without-writing); (3) **X88C64 (0x34)** is mis-classified as infeasible but is a genuine parallel 5V 24-pin DIP EEPROM/NOVRAM (MEDIUM — needs a datasheet protocol spec). Plus cheap wins: flash4 missing `CMD_CHECK_CHIP_ID` case, and a stale "0x39 = 0 chips" comment (DB now has 2). Anti-features stay fail-closed: 0x11 FWH, 0x2A-2C GAL/PLD, 25V NMOS. The **build-order driver** is the Leonardo flash ceiling (~88%): the harness adds zero production flash, so fixes-before-additions, and adapter-required handlers (flash-heavy, hardware-gated) are the natural deferrals. Dual-repo lockstep + the py3.12-masks-CI-3.11 trap apply to every wire-touching firmware change.

## Key Findings

### Recommended Stack

See `STACK.md`. **No new third-party dependencies.** The two substrates are already pinned and green: firmware native = PlatformIO `[env:native]` + Unity + ArduinoFake `^0.4.0` (8 suites already passing); host = pytest `>=8` + syrupy `>=5` + ruff/mypy + pyserial, with `conftest.py` `make_comm`/`fake_serial` fixtures that drive the full INIT→MAIN→END state machine *without a serial port*. The genuinely-new work is patterns + a thin harness layer + data files, not a framework.

**Core technologies (all REUSE):**
- **PlatformIO `[env:native]` + Unity + ArduinoFake `^0.4.0`** — cross-compile real handler TUs on host, mock `Serial`/`delay`/`set_control_register`; the model for algorithm-shape + register-sequence native tests (`test_dispatch`, `test_flash_intel_vpp` patterns).
- **pytest `>=8` + syrupy `>=5` + `make_comm`/`fake_serial`** — host wire-dict + state-machine tests with no hardware; golden wire-vectors pin safety-critical fields (vpp_mv/algorithm/flags).
- **`write_test.sh` / `eprom_operations.py` cycle methods / `firestarter_test.sh`** — the existing HIL write→verify→read-back→`diff` loop; v1.13 generalizes them matrix-driven, NOT rewrites.
- **`check_dispatch.py` / `diff_db.py`** — DB-correctness + cross-family dispatch firewall; reused as CI gates and extended per-family.

**New-but-tiny:** a declarative validation-matrix data file (family → algorithm IDs → rep chip → assertions → native/bench tier), per-family native Unity suites, golden wire-vectors, seed-pinned golden `.bin` images, a matrix-driven bench runner, and a `@pytest.mark.hardware` marker (`-m "not hardware"` default in CI). The one firmware config touch: add each new suite dir to the `[env:native]` `test_filter` allowlist + `-I` include.

### Expected Features

See `FEATURES.md`. Framing is **validate vs implement vs keep-refused**, measured against the RURP feasibility ruler (fixed 5V VCC, VPP ceiling `RURP_VPP_CEILING_MV=22000`, DIP parallel 24/28/32-pin).

**Must have (table stakes — VALIDATE, code exists, prove on hardware):**
- **Validation harness + matrix (software, build FIRST, no bench gate)** — the spine; everything reports through it.
- **UV-EPROM 0x07/08/0B write+verify+chip-id** — core product path (323 chips); retry loop grows pulse_delay up to 20× (confirm convergence); 0x0B uses direct VPE (no drop resistor) — distinct VPP row.
- **5V EEPROM 0x0D (SDP-disable + 64B page + DQ7 poll)** — 84 chips (AT28C256 rep).
- **Flash AMD 0x06 write + sector/chip erase** — largest family (190 chips).
- **Resolve the SRAM no-op question** — 0x0E/27/28/29 dispatch to an empty handler; validate-or-classify-as-bug.
- **Blank check + read path (all families)** — read validated on Leonardo/EVEN-01 ONLY (decoupled from the v1.9 RCA).

**Should have (competitive — IMPLEMENT, RURP-feasible gaps):**
- **`firestarter erase W27C512` host wiring + 14V rail confirm** — flagship feasible gap; firmware electricals already exist; gap = `FLAG_CAN_ERASE` routing + 12V→14V detail + datasheet preconditions. MEDIUM.
- **`configure_sram` real read/write** — if validation shows silent no-op write, this is a correctness fix (LOW–MEDIUM).
- **Flash type-4 0x05/0x35 `CMD_CHECK_CHIP_ID` case** — trivial, mirror flash3 (LOW).
- **0x39 2-chip validation + stale-comment fix** — cheap correctness win (LOW).
- **Flash Intel 0x10 validation** (12V P1; SR error branches) — trigger: a 28F-series chip on hand.

**Defer (hardware/spec-gated):**
- **AT28C04/AT28C16 24-pin EEPROMs (adapter-required, 0x0D)** — firmware handler exists; needs a physical DIP24 adapter + a `resolve_pinout_key` arm + pin-map spec. Deliver the spec now, bench-validate when the adapter exists.
- **X88C64 0x34 handler** — MEDIUM/HIGH; re-classify as feasible candidate, but do NOT promise blind — needs the 0x34 STORE/RECALL + byte/page write protocol from the datasheet first.

**Keep refused (anti-features, fail-closed invariant):** 0x11 FWH (LPC-serial/3.3V), 0x2A-2C GAL/PLD (not memory), 25V NMOS 2716/2732 (`vpp-exceeds-max`; M2732A=21V correctly `supported`), serial/SMD/MCU. Do not relax the 22V ceiling.

### Architecture Approach

See `ARCHITECTURE.md`. The validation surface is a **three-tier test pyramid stacked on the unchanged production stack** — the harness exercises and observes the routes that already ship; it adds NO new production write/program/verify code path. Tiers 1–2 are pure software (no bench gate); Tier 3 is hybrid bench-gated and produces the per-family matrix.

**Major components:**
1. **Tier 1 — native Unity suites** (`test/native/avr/test_<family>_algo/`, one per family) + a NEW `_shared/recording_bus_stub.inc` that records `rurp_*` register-write sequences — so a fix is provable by side-effect (e.g. SRAM must NEVER set `CTRL_VPP_REGULATOR_ENABLE`), not just by op-pointer. Zero production flash.
2. **Tier 2 — host pytest** (`validation_harness.py` pure-logic module + `test_validation_harness.py` MockSerial round-trip per family) + extended `check_dispatch.py` (populate the hollow `non_supported_dispatchable` inverse guard, accepted v1.12 tech debt).
3. **Tier 3 — HIL bench** (`dev validate-family` CLI thin handler composing `write_cycle_eprom`/`consistency_check_eprom` verbatim) emitting a committed `validation-matrix.{json,md}` artifact (family × board × verdict × evidence SHA; partial coverage OK under hybrid gating).

**Build order (dependency- + flash- + bench-ordered):** (1) harness scaffolding (flash-free) → (2) re-research protocol landscape → (3) validate families on Leonardo (produces the evidence) → (4) per-family fixes (flash-gated, fixes-before-additions) → (5) adapter-required arms in `resolve_pinout_key` (flash + hardware gated, last). Steps 1–3 are flash-free; steps 4–5 are the only flash consumers — the ~88% Leonardo ceiling forces the order.

### Critical Pitfalls

See `PITFALLS.md`. Two coupled failure classes dominate: **false-pass** (a corrupt image believed good) and **chip-destruction** (wrong VPP/algorithm on a physical part).

1. **False-PASS from an untrustworthy verify read board** — the verify oracle IS the v1.9-deferred read bug on Rev-0/Rev-2.0 + uno328pb drift; the firmware's own in-program verify reads through the same path. *Avoid:* pin PASS to Leonardo + clean shield; advisory-only elsewhere; N≥5 byte-identical SHA reads; cross-check against read-independent signals (Intel SR poll, DQ7).
2. **Chip destruction by wrong VPP / wrong algorithm** — bench shortcuts (`--force`, hand-built JSON, override DB) route around the v1.12 `resolve_chip` guard; a wrong `set_control_register` bit passes native dispatch tests (which check pointers, not registers). *Avoid:* never bypass the host guard; chip-OUT VPP multimeter dry-run before any seated write; add register-bit-sequence native tests; keep GATE-03 green.
3. **Calibration + board confounders (999.1 / 999.2)** — stale-R1 EEPROM makes the VPP safety check lie (~6.8× under-read, could pass a destructive voltage); uno328pb brown-outs under program current. *Avoid:* read live R1/R2 (`r1 ≈ 270000`) + meter-reconcile at every VPP-dependent task; **uno328pb = N/A for program/write**; prefer Leonardo.
4. **Vacuous verify / clean-read-masks-bad-write** — verify against the in-memory buffer, or retry-convergence on read noise, manufactures false PASS. *Avoid:* PASS = independent post-write full read + SHA + a passing negative control (wrong-file mismatch + blank/chip-out fail) per family; record retry counts.
5. **Leonardo flash overflow + lockstep/codegen drift** — ~88% Leonardo ceiling; py3.12 masks CI-3.11 ruff/codegen; wire changes must edit the meta-repo catalog only. *Avoid:* build `-e leonardo` + flash-% ceiling as a success criterion on every firmware change; validate ruff/codegen against CI Python 3.11; meta-only catalog edits → regen → both-repo drift gate; cut a real firmware tag at the beta cut.

Standing bench preconditions (Pitfall 9): chip-OUT before any Uno-class sideload (Leonardo exempt); ASK the operator which silkscreen shield rev is mounted (EEPROM can't distinguish); re-verify `controller:` port identity per task (ACM* numbers shuffle).

## Implications for Roadmap

Based on combined research, the suggested phase structure (numbering continues from v1.12 → **Phase 71+**) follows the harness-before-validate-before-fix-before-gaps spine, ordered so flash-free software work precedes flash-consuming firmware work.

### Phase 71: Validation harness + matrix (software, flash-free)
**Rationale:** The spine of the milestone and the only fully un-gated deliverable; everything else reports through it. Built first so bench time is spent only on proven-RED divergences.
**Delivers:** Tier-1 recording bus stub + one `test_<family>_algo/` native suite per family (SRAM the obvious early RED); Tier-2 `validation_harness.py` + MockSerial round-trip; Tier-3 `dev validate-family` composing existing cycle methods + matrix serializer; extended `check_dispatch.py` with per-family invariants + populated `non_supported_dispatchable`.
**Addresses:** "Validation harness + matrix" (P1 table stakes).
**Avoids:** Bakes in the PASS definition that defends Pitfalls 1, 3, 4, 5, 6 — Leonardo-as-oracle, live R1/R2 precondition, uno328pb=N/A board-eligibility, independent-read+SHA+negative-control, retry-count capture.

### Phase 72: Re-research the protocol landscape
**Rationale:** Must reaffirm or overturn v1.12's "feasible set complete" with citations BEFORE any gap-implementation phase is committed; defines which fixes/additions are in scope.
**Delivers:** Grounded re-enumeration (SRAM no-op, X88C64 0x34, flash4 chip-id, 0x39 stale comment, erase path) with feasibility verdicts citing the v1.11 field dictionary + datasheets; confirms anti-features stay refused.
**Avoids:** Pitfall 10 (over-claiming the gap set — committing a flash-budget firmware phase to an infeasible protocol).

### Phase 73: Bench-validate families on Leonardo (hybrid-gated)
**Rationale:** Produces the evidence that defines the fix phases. Software tiers run always; bench runs the families with chips + a working shield on hand, defers parts-missing families with explicit SKIP rows.
**Delivers:** Populated validation matrix (UV-EPROM 0x07/08/0B, EEPROM 0x0D, Flash AMD 0x06 first; Flash type-4/Intel as parts allow); resolved SRAM no-op question (validate→classify).
**Uses:** `write_cycle_eprom`/`consistency_check_eprom`, `firestarter`/`dev` CLI, COBS+CRC8 transport (`STACK.md`).
**Avoids:** Pitfalls 1–6, 9 (every bench precondition: Leonardo oracle, live-R1, uno328pb exclusion, negative control, chip-out, ask-rev, verify-port).

### Phase 74: Per-family correctness fixes (flash-gated)
**Rationale:** Fix only families the bench showed divergent; software-first RED→GREEN. Order lightest-flash-impact first; fixes-before-additions because Leonardo is the ceiling.
**Delivers:** Handler fixes (e.g. SRAM real read/write if no-op confirmed; flash4 `CMD_CHECK_CHIP_ID`; 0x39 comment); each turns a RED native/wire test GREEN, keeps `check_dispatch.py`/`diff_db.py`/native suites green, re-benches to a PASS cell.
**Implements:** SRAM IMPLEMENT fork, flash4 chip-id, 0x39 (P2 differentiators).
**Avoids:** Pitfalls 2 (register-bit native test + chip-out VPP dry-run for any handler touching VPP), 7 (`-e leonardo` flash-% ceiling), 8 (lockstep/codegen for any wire-touching fix).

### Phase 75: Erase path (`firestarter erase` W27C512, 0x07)
**Rationale:** The flagship feasible gap and lowest-risk Differentiator — firmware electricals (`eprom_internal_erase`) already exist; gap is mostly host-side. Sequenced after fixes because it touches the VPP hazard surface.
**Delivers:** Host `erase` wiring (`FLAG_CAN_ERASE` routing) + 12V→14V rail confirmation under the 22V ceiling + datasheet-precondition validation.
**Avoids:** Pitfalls 2, 3 (chip-out 14V VPP meter dry-run; live-R1 reconcile), 7 (flash if any firmware touch).

### Phase 76 (defer / hardware-spec gated): Adapter-required + X88C64
**Rationale:** Both depend on artifacts the operator must supply (a physical DIP24 adapter; a 0x34 datasheet protocol). The heaviest flash consumers — gated hardest, natural deferrals under hybrid gating.
**Delivers:** Adapter pin-map spec + a `resolve_pinout_key` named rule arm (NOT a resurrected table) for AT28C04/16, staying `adapter-required` until the adapter exists and a golden write+read-back round-trips; X88C64 0x34 handler only after the protocol is spec'd.
**Avoids:** Pitfalls 7 (flash ceiling — last consumer), 10 (no blind feasibility promise), Anti-Pattern 2 (no guess-table resurrection).

### Phase Ordering Rationale
- **Harness → re-research → validate → fix → gaps** is forced by dependency (the matrix is the spine; evidence must precede fixes) AND by the **Leonardo flash ceiling** (~88%): steps 71–73 are flash-free, so all flash-consuming work (74–76) lands after the test net exists, fixes-before-additions.
- **Family isolation** (one native suite per family) means a fix to one handler cannot silently regress another; `check_dispatch.py` is the cross-family firewall.
- **Hybrid gating** lets the milestone close at partial bench coverage — the matrix records exactly which families are bench-proven vs deferred-for-parts.

### Research Flags

Phases likely needing deeper research during planning (`/gsd-plan-phase --research-phase`):
- **Phase 75 (erase path):** the 12V→14V rail setpoint, the regulator behavior without the drop resistor, and the A0-low/all-DQ-high datasheet preconditions need confirmation against `eprom_internal_erase` + the W27C512 datasheet before wiring.
- **Phase 76 (X88C64 0x34):** requires the exact STORE/RECALL + byte/page write protocol from the X88C64 datasheet; feasibility is MEDIUM and unconfirmed — do not commit until spec'd.
- **Phase 76 (adapter-required):** the DIP24 socket adapter pin-map (re-route socket pin 21 from VPP rail to WE) is a physical-design + safety question.

Phases with standard/established patterns (skip research-phase):
- **Phase 71 (harness):** the native + pytest + bench reuse patterns are fully documented in `firestarter/CLAUDE.md` and proven by 8 existing suites + `write_test.sh`.
- **Phase 74 (flash4 chip-id, 0x39 comment):** trivial mirrors of existing handler cases.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Both substrates installed, pinned, and green in CI; reuse patterns repo-canonical (`firestarter/CLAUDE.md`, `platformio.ini`, `conftest.py`). Only the ArduinoFake "current version" check is MEDIUM. |
| Features | HIGH | Firmware source + 744-chip DB read directly; datasheet/protocol facts web-grounded; feasibility verdicts measured against fixed RURP constraints. X88C64 0x34 verdict is explicitly MEDIUM (datasheet-pending). |
| Architecture | HIGH | Grounded in the actual v1.12 codebase (`memory.cpp`, `eprom_operations.py`, `check_dispatch.py`, `[env:native]`, existing Unity suites); build order driven by the named Leonardo ~88% ceiling. |
| Pitfalls | HIGH | Project-internal evidence (firmware source, the vpp-misread + datapath-overflow debug records, Phase 44 RCA, operator bench-protocol memory). |

**Overall confidence:** HIGH

### Gaps to Address
- **SRAM no-op resolution is a validate→maybe-implement fork** — research can't decide it without the bench; the matrix run in Phase 73 determines whether SRAM is a table-stakes pass or a Phase-74 fix. Resolve early (20+ chips claim support).
- **Erase 12V→14V rail detail** — the exact regulator setpoint and the datasheet preconditions (A0-low/all-DQ-high) need confirmation during Phase 75 planning, not assumption.
- **X88C64 0x34 protocol unknown** — flag as feasible-candidate, NOT a commitment; gate on a datasheet spec.
- **999.1 vs 999.2 disambiguation** — the live R1/R2 readback at bench-task start is the discriminator; bake it into the matrix preconditions so a calibration artifact is never recorded as an algorithm bug.
- **Adapter physical artifact** — AT28C04/16 support is blocked on the operator building/obtaining a DIP24 adapter; deliver the pin-map spec now, bench-validate later.

## Sources

### Primary (HIGH confidence)
- `firestarter/CLAUDE.md`, `firestarter/platformio.ini [env:native]`, `firestarter/test/native/avr/test_dispatch|test_flash_intel_vpp|test_eeprom28c_chip_id` — native test reuse pattern, recording-mock + setter patterns, `[env:native]` config
- `firestarter/src/proms/{memory,eprom,eeprom_28c,flash_type_3,flash_type_4,flash_intel,sram,flash_utils,not_implemented}.cpp` — handler shapes, erase electricals, no-op SRAM, dispatch chain, VPP control-register bits
- `firestarter_app/firestarter/{eprom_operations.py,chip_resolver.py,database.py}`, `tools/{check_dispatch.py,diff_db.py,build_db.py}`, `tests/conftest.py`, `pyproject.toml` — reusable cycle methods, support_status guard, DB gates, no-port fixtures, pinned test deps
- `firestarter_app/firestarter/data/chip_database.json` (read 2026-06-16) — 744-chip support_status + algorithm distribution
- `firestarter_app/{firestarter_test.sh,write_test.sh}` — existing HIL write→verify→read-back→diff loop
- `.planning/PROJECT.md` v1.13 milestone + Key Decisions; `.planning/debug/{firmware-vpp-misread.md,write-verify-datapath-overflow.md}` (999.1; verify negative-control precedent); v1.9 Phase 44 RCA
- Project memory: `reference_devcontainer_py312_masks_ci_py39`, `feedback_chip_out_before_sideload`, `feedback_verify_port_identity_each_task`, `user_shield_revisions`, `project_uno328pb_vpp_recal_and_program_brownout`, `reference_codegen_ruff_clean_emitter`

### Secondary (MEDIUM confidence)
- PlatformIO Unit Testing docs + ArduinoFake registry — confirmed `^0.4.0` current
- [Winbond W27C512 datasheet](https://www.dosdays.co.uk/media/winbond/W27C512_Datasheet.pdf) — erase mode OE/VPP=14V, A9=14V, 5V VCC, 100 ms
- [Elnec Xicor X88C64](https://www.elnec.com/en/device/Xicor/X88C64/), [eBay X88C64PI 24-pin DIP 5V](https://www.ebay.com/p/663635561) — confirms parallel 5V 24-pin DIP package

### Tertiary (LOW confidence)
- X88C64 0x34 write/STORE-RECALL algorithm — feasibility MEDIUM, exact protocol unconfirmed; needs datasheet before commitment
- [Andy4495/ParallelEEPROM](https://github.com/Andy4495/ParallelEEPROM) — prior-art for parallel 28C/X28 programming

---
*Research completed: 2026-06-16*
*Ready for roadmap: yes*

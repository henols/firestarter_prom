# Roadmap: Firestarter — Protocol-Aware Programming Architecture

## Milestones

- ✅ **v1.0 Protocol-Aware Programming Architecture** — Phases 1-13 (shipped 2026-05-11)
- ⏸ **v1.1 Safety Closure & Hardware Validation** — Phases 1-3 done, Phase 4 hardware-validation parked (FM1608 byte-0 bug); Phase 5 milestone-close deferred. Original artifacts preserved at `.planning/milestones/v1.1-paused/`.
- ✅ **v1.2 Message-ID Logging Rework** — Phases 6-10 (shipped 2026-05-19); Phase 10 closed by `/gsd-complete-milestone` (DOC-02)
- ⏸ **v1.3 CMOS EPROM Family Hardware Validation** — Phases 11-14 (PAUSED 2026-05-20, hardware-gated). Phase 11 shipped + Phase 12 Wave 0 scaffold committed; Plans 12-01/02/03 + Phases 13/14 await operator bench hardware.
- ✅ **v1.4 Beta & Pre-release Deployment Pipeline** — Phases 15-20 (shipped 2026-05-20; ship tag `3.0.0b3` in both sub-repos; hardware-flash validated on Uno + Leonardo). Parallel beta channel for both sub-repos without disrupting the stable main → release pipeline.
- ✅ **v1.5 Arduino Uno (ATmega328PB) Board Support** — Phases 21-25 (shipped 2026-05-21; ship tag `3.0.0b4`; bench-validated on operator's 328PB-Uno via `urclock` bootloader). `uno328pb` as a third first-class firmware target alongside `uno` + `leonardo`. Full detail in `.planning/milestones/v1.5-ROADMAP.md`; bench evidence in `.planning/v1.5-BENCH-RESULTS.md`.
- ⏸ **v1.6 Fix the Read Bug** — Phases 26-30 (PAUSED 2026-05-22 at the Phase 27 RCA re-open boundary). Phases 26+27+28 shipped; Phase 29 Wave B FAIL (D-07 milestone-reopens) — chip-swap diagnostic isolated Phase 28 firmware as introducing a Leonardo + uno328pb read-path regression; Uno code path unaffected. Phase 30 BLOCKED. Resumes after v1.7 ships its labeled-schematic + per-rev capability table + shield-version-detect substrate (v1.6 Phase 27 RCA re-open then designs instrumented A/B builds with known-good schematics).
- 🚧 **v1.7 RURP Shield Hardware Investigation & Version Detection** — Phases 31-35 (STARTED 2026-05-22). Catalog every known RURP shield revision (Rev 0 → Rev 2.2 + older revs from upstream git history); per-rev silkscreen capture, electrical/mechanical difference matrix, capability table; silkscreen-label → code-side alias migration applied to firmware + host; shield-version-detect resistor divider design + firmware ADC read + handshake report with backward-compat fall-through for pre-detect-resistor boards.

## v1.7 — RURP Shield Hardware Investigation & Version Detection (STARTED 2026-05-22)

**Milestone goal:** Produce a versioned, authoritative reference for every known RURP shield revision — silkscreen text, electrical/mechanical schematic, label-to-code-alias map, per-rev capabilities matrix, inter-rev difference table — and design the next-rev shield-version-detect resistor divider + firmware ADC read + handshake report so future hardware-touch work is grounded in known-good schematics rather than ask-the-operator memory.

**Status:** Roadmap created 2026-05-22. Phase numbering continues from v1.6 last planned phase 30 (next phase = 31). Phases 31+32+33+35 are desk-side (operator's existing Rev 2.2 / Rev 2.0 / Modified Rev 0 boards used for label-photo capture + spot-check; no bench programming needed). Phase 34 has a desk-side wave (schematic delta + firmware compile + handshake report on synthetic/floating ADC) and an optional operator-on-bench wave (sanity-check ADC read on existing pre-detect-resistor boards reports `rev_unknown` cleanly).

**Granularity:** Comprehensive — five phases for a documentation + design milestone is high, but each phase delivers an independently-verifiable artifact: per-rev inventory (HW-INV-01..03 + SILK-01), inter-rev difference + capability matrix (DIFF-01/02 + CAPS-01/02), label-alias migration (ALIAS-01..03), detect-hw schematic delta + detect-fw plumbing (DETECT-HW-01/02 + DETECT-FW-01/02), close (DOC-01 + MS-01). Coverage 17/17.

**Phase numbering:** Phases 31-35 (continues from v1.6 last planned phase 30; Phase 30 slot stays reserved for v1.6 close on resume).

**Branch model:** Per memory [[feedback_branching]] — all v1.7 work lands on `v1.7-shield-investigation` branches in all 3 repos. Meta-repo `v1.7-shield-investigation` branches off `main` (most of v1.7 lives here — documentation). Sub-repos branch off current `beta` tips (post-v1.5 ship at `3.0.0b4`; v1.6 sub-repo branches are mid-iteration and the firmware-detect patch needs a clean substrate). Promote sub-repos `v1.7-shield-investigation` → `beta` only after Phase 34 firmware-detect lands; `beta` → `main` only after operator confirms firmware handshake reports correctly on at least one bench-present rev.

### Structural Notes

- **Documentation-first investigation.** v1.7 is unusual in this project — most prior milestones added behavior or shipped a fix. v1.7 ships a reference document plus one hardware design delta + one firmware plumbing patch. The reference document (`.planning/v1.7-SHIELD-REVS.md`) is itself a load-bearing artifact: future RCA passes (including v1.6 Phase 27 re-open) read it to know what's on the bench.
- **Operator hardware on hand.** Memory [[user_shield_revisions]] — operator has Rev 2.2, Rev 2.0, modified Rev 0 (with hardware-bug-A/B rework). Phase 31 photographs + spot-checks all three. Per memory [[feedback_chip_out_before_sideload]] — chip OUT of socket before any firmware sideload in Phase 34. Per memory [[feedback_verify_port_identity_each_task]] — verify `controller:` identity per port at every task start.
- **Upstream archaeology.** Phase 31 mines `AndersBNielsen/Relatively-Universal-ROM-Programmer/hardware` via `git log -p` + `git log --diff-filter=D` to recover older revs (Rev 0, Rev 1) that may not exist on `main`. Branch tip + tag history walked to bracket when each rev was introduced.
- **Alias migration is name-only.** ALIAS-03 GATE-1.7 — the silkscreen-label → code-alias migration must NOT change firmware behavior, wire format, or compiled `.hex` size beyond trivial symbol-name overhead (≤ ~50 B). Pytest + Unity stay green.
- **Backward-compat fall-through is load-bearing.** DETECT-FW-02 GATE-1.7 — existing pre-detect-resistor boards (Rev 0 / 2.0 / 2.2 with no resistor) must handshake byte-identical to v1.6 baseline. Floating/grounded ADC reading falls through to `rev_unknown` + firmware honors EEPROM `hw_revision` byte (existing behavior preserved). The detect resistor is additive; no existing board is bricked or downgraded.

### Phases

- [ ] **Phase 31: Upstream Shield Archaeology** — Clone upstream `AndersBNielsen/Relatively-Universal-ROM-Programmer`; mine git history for all shield revisions (Rev 0, Rev 1, Rev 2.0, Rev 2.2, plus any others); per-rev silkscreen-version capture; photograph operator's three on-hand boards; populate `.planning/v1.7-SHIELD-REVS.md` inventory section.
- [ ] **Phase 32: Inter-Rev Difference + Capability Matrix** — Per-rev electrical/mechanical difference table (pinout, VPP regulator wiring, voltage divider values, jumpers, control-line routing, rework hacks); per-rev capability matrix (chip families, max VPP/VCC, address-bus width, supported algorithms); cross-check capabilities against firmware code.
- [ ] **Phase 33: Silkscreen Label → Code Alias Migration** — Inventory every silkscreen label across all known revs; propose code-side alias namespace (`PIN_<SUBSYSTEM>_<FUNCTION>`); apply aliases to `firestarter/include/` + `firestarter_app/firestarter/constants.py`; migrate existing call-sites; GATE-1.7 non-regression preserved (compiled `.hex` byte-identical modulo trivial symbol-name overhead).
- [ ] **Phase 34: Shield-Version-Detect Design + Firmware Plumbing** — Schematic delta for next-rev shield (resistor divider into Arduino ADC pin not conflicting with any current RURP signal); per-rev voltage-band lookup table; firmware ADC read at boot + handshake report; backward-compat fall-through for pre-detect-resistor boards (Rev 0 / 2.0 / 2.2 → `rev_unknown` + EEPROM `hw_revision` byte fallback).
- [ ] **Phase 35: Documentation + Milestone Close** — Finalize `.planning/v1.7-SHIELD-REVS.md`; README updates in both sub-repos cross-link to it; PROJECT.md "Validated" section updates; MILESTONES.md entry; archive `.planning/milestones/v1.7-phases/`.

### Phase Details

#### Phase 31: Upstream Shield Archaeology

**Goal:** A future reader can name every RURP shield revision that has ever existed, point at its silkscreen-version string, find its schematic file in upstream, and see photographs of the three on-hand revisions including any operator-side rework annotations.
**Depends on:** Nothing (continues from v1.6 pause boundary; meta-repo only).
**Requirements:** HW-INV-01, HW-INV-02, HW-INV-03, SILK-01
**Success Criteria** (what must be TRUE):

  1. `git clone` of `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer` is staged under `.planning/v1.7/upstream-rurp/` (gitignored — not checked into meta-repo); `git log -p hardware/` is scanned for every rev introduction + every rev deletion; recovered revs list is comprehensive.
  2. `.planning/v1.7-SHIELD-REVS.md` has an inventory section with one row per identified revision: silkscreen-version string (e.g. `RURP Rev 2.2`), upstream commit/tag of introduction, schematic file path in upstream repo, date introduced. Older revs (Rev 0, Rev 1) recovered from history are flagged "no longer on `main`" with the git commit that removed them.
  3. Operator's three on-hand boards (Rev 2.2, Rev 2.0, modified Rev 0) are photographed and stored under `.planning/v1.7/photos/<rev>/` (sufficient resolution to read silkscreen). The Modified Rev 0 rework hacks (per memory [[user_shield_revisions]]) are annotated on the photo or in an accompanying `MODIFICATIONS.md`.
  4. Silkscreen-version strings are captured verbatim per board (the actual text on the silkscreen, not a normalized form). These become the canonical revision identifiers used by all downstream phases.

**UI hint:** no

#### Phase 32: Inter-Rev Difference + Capability Matrix

**Goal:** A future engineer planning a firmware change can read one table to know which revs support which algorithms, and read another table to know what changed electrically/mechanically between rev N and rev N+1 — without re-reading upstream schematics.
**Depends on:** Phase 31 (inventory of revs to compare).
**Requirements:** DIFF-01, DIFF-02, CAPS-01, CAPS-02
**Success Criteria** (what must be TRUE):

  1. `.planning/v1.7-SHIELD-REVS.md` has an inter-rev electrical difference table covering at minimum: Arduino pin mapping (Dx/Ax → RURP signal), VPP regulator wiring (input pin, output pin, enable pin, feedback divider), voltage divider values (R1/R2 from `rurp_configuration_t`), control-line routing (CE/WE/OE per algorithm), jumper/strap positions. Each row is "rev → rev" delta. Where a rev is electrically identical to its predecessor, the row says so explicitly.
  2. An inter-rev mechanical difference subsection covers board outline / mounting holes, ZIF socket presence + orientation, header positions, notable component changes. Differences with no electrical impact are noted but not gated.
  3. A per-rev capability matrix declares for each revision: chip families supported (28-pin DIP UV-EPROM, 32-pin DIP UV-EPROM, parallel EEPROM, AMD-style flash, Intel flash, SRAM), max VPP, max VCC, address-bus width, supported firmware algorithms (subset of `0x05/0x06/0x07/0x08/0x0B/0x0D/0x0E/0x10/0x27/0x28/0x29`).
  4. Capability matrix is cross-checked against firmware code (`firestarter/src/algorithm_*.cpp` + handler dispatch in `memory.cpp::configure_memory`). If a rev physically cannot support an algorithm (e.g. missing VPP regulator on a hypothetical Rev 0), that fact is documented and a follow-up todo is captured for a runtime-guard implementation in a later milestone (out of scope for v1.7).

**UI hint:** no

#### Phase 33: Silkscreen Label → Code Alias Migration

**Goal:** Reading firmware or host code that references a RURP signal makes immediate sense without consulting a schematic — `PIN_VPP_REGULATOR_ENABLE` is self-documenting where the bare pin number isn't. The migration is name-only (no behavior change, no wire-format change, no `.hex` size drift beyond trivial symbol-name overhead).
**Depends on:** Phase 31 (silkscreen-label inventory) + Phase 32 (per-rev pin-mapping table — aliases must be consistent across revs where the silkscreen label is the same).
**Requirements:** ALIAS-01, ALIAS-02, ALIAS-03
**Success Criteria** (what must be TRUE):

  1. Every silkscreen label across all known revs is inventoried in `.planning/v1.7-SHIELD-REVS.md` (canonical table). Each row maps silkscreen label → proposed code-side alias following the `PIN_<SUBSYSTEM>_<FUNCTION>` convention (e.g. `VPP_EN` → `PIN_VPP_REGULATOR_ENABLE`, `A14` → `PIN_ADDRESS_BUS_A14`, `D0` → `PIN_DATA_BUS_BYTE_0`).
  2. Aliases land as `#define` / `constexpr` declarations in `firestarter/include/rurp_pinout.h` (or equivalent header — fixed at plan time) and as constants in `firestarter_app/firestarter/constants.py` (or equivalent module). Existing call-sites that use bare pin numbers or shield-specific net names are migrated to the aliases.
  3. GATE-1.7 non-regression: after migration, compiled firmware `.hex` artifacts for all three boards (`uno`, `leonardo`, `uno328pb`) are byte-identical to pre-migration modulo trivial symbol-name overhead (≤ ~50 B per board; documented in the fix-commit message if non-zero). Pytest + Unity test suites stay green.
  4. Per-rev pin-mapping differences (from Phase 32) are honored — if Rev 2.0 maps `VPP_EN` to Arduino pin A5 but Rev 0 maps it to a different pin, the alias resolves correctly per active rev via the existing `RURP_BOARD_NAME` per-env mechanism (or a new compile-time switch — finalized at plan time).

**UI hint:** no

#### Phase 34: Shield-Version-Detect Design + Firmware Plumbing

**Goal:** Operator can build the next-rev shield (with the new detect resistor populated) and the firmware reports the correct silkscreen-version string in the handshake without operator intervention. Existing pre-detect-resistor boards continue to report `rev_unknown` and fall through to the EEPROM `hw_revision` byte — no breaking change.
**Depends on:** Phase 32 (capability matrix — to pick an ADC pin not conflicting with any current RURP signal across any known rev) + Phase 33 (aliases — the new ADC pin gets an alias).
**Requirements:** DETECT-HW-01, DETECT-HW-02, DETECT-FW-01, DETECT-FW-02
**Success Criteria** (what must be TRUE):

  1. `.planning/v1.7-SHIELD-REVS.md` documents the schematic delta for the next-rev shield: a resistor divider into an Arduino ADC pin (pin selected to not conflict with any currently-used RURP signal across any known rev, verified against Phase 32 capability matrix). Resistor values produce voltage bands per rev with ≥ ~0.3V separation against 10-bit ADC noise floor.
  2. A per-rev expected-ADC-band table is included: rev string → expected ADC value range. The next-rev (e.g. Rev 2.3) entry is the seed; existing Rev 0 / 2.0 / 2.2 boards have no detect resistor and produce floating/grounded ADC readings — captured as the "rev_unknown" fall-through band.
  3. Firmware reads the ADC pin at boot (or on first handshake), looks up the voltage band in the table, and reports the detected silkscreen-rev string in the handshake payload. Exact wire shape (extend `MSG_OK_FW_HANDSHAKE` or add a sibling INFO emit) finalized at plan time.
  4. On pre-detect-resistor boards (floating/grounded ADC), the report is `rev_unknown` and firmware continues to honor the operator-configured `hw_revision` byte in EEPROM (existing behavior preserved). GATE-1.7 non-regression: existing pre-detect-resistor boards handshake byte-identical to v1.6 baseline modulo the additive `rev_unknown` report (documented in the fix-commit message). Chip programming + read paths byte-identical. Firmware compiles cleanly for all three board targets without requiring physical fabrication of the next-rev shield.

**UI hint:** no

#### Phase 35: Documentation + Milestone Close

**Goal:** v1.7 is closed cleanly — the canonical reference document is operator-readable, the sub-repo READMEs cross-link to it, PROJECT.md reflects what shipped, MILESTONES.md captures the delivery, and the phase artifacts are archived.
**Depends on:** Phase 31 + Phase 32 + Phase 33 + Phase 34 (everything that fills `.planning/v1.7-SHIELD-REVS.md`).
**Requirements:** DOC-01, MS-01
**Success Criteria** (what must be TRUE):

  1. `.planning/v1.7-SHIELD-REVS.md` is the canonical reference and is complete (inventory + difference matrix + capability matrix + alias table + detect-hw schematic delta + per-rev ADC band table). Cross-links from `firestarter/README.md` + `firestarter_app/README.md` resolve to it.
  2. PROJECT.md "Validated" section grows entries for the alias migration + detect-fw plumbing. The v1.7 milestone block at the top is rewritten as "Shipped 2026-05-XX". v1.6 paused-block carries through unchanged (v1.6 resume is the milestone-close hand-off).
  3. MILESTONES.md entry written; phase artifacts archived under `.planning/milestones/v1.7-phases/` via the archive script pattern established in v1.4/v1.5.
  4. Hand-off to v1.6 resume: `Operator Next Steps` in STATE.md points at `/gsd-plan-phase 27 --gaps` with a note citing the v1.7 artifacts (labeled schematic + per-rev capability table) that the Phase 27 RCA re-open will consume.

**UI hint:** no

## v1.6 — Fix the Read Bug (SHIPPED 2026-05-26 — diagnostic + revert)

<details>
<summary>✅ v1.6 shipped — ships as "diagnostic + revert" per D-17v2 (5 phases, 13 plans). Read-bug carries to v1.8 with Bug A + Bug B pattern findings as RCA seed. Full detail in `.planning/MILESTONES.md` §v1.6.</summary>

- **Ship tag:** `<TBD-from-30-03>` (default `3.0.0b5` beta-only; operator may authorize `3.0.1` stable in Plan 30-03)
- **Phases:**
  - [x] Phase 26: Cross-board Reproduction & Diagnostic Tooling (2 plans; REPRO-01..03)
  - [x] Phase 27: Root Cause Analysis (3 plans incl. re-open Plan 27-05; RCA-01..03)
  - [x] Phase 28: Fix Implementation + Unit Test Coverage (4 plans incl. revert Plan 28-03 + parked Plan 28-04; FIX-01..03 as diagnostic + revert)
  - [x] Phase 29: Multi-Board Bench Verification (4 plans incl. v2 re-iteration Plans 29-03/04; VERIFY-02 PASS via structured_data shape; VERIFY-01/03/04 DEFERRED to v1.8)
  - [x] Phase 30: Documentation + Milestone Close (3 plans; DOC-01/02 + MS-01)
- **Re-scope (D-17v2):** Phase 29 v1 Wave B FAIL → Plan 27-05 re-open confirmed dual-cause (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb hardware) → Plan 28-03 reverted `437339b6` via `ea25174`; `4f205e58` `_NOP()` settling preserved (Plan 28-04 parks) → Phase 29 v2 PASS_PARKED (Leonardo Modified Rev 0 returns to Phase 26 baseline; WORST 0.047% zeros vs 83.8% pre-revert).
- **v1.8 hand-off:** 15 N=5 W27C512 binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`; Bug A (Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew) + Bug B (Rev 2.0 /CE-or-/OE timing + VPP=13.1V) characterized in `.planning/v1.6-EVIDENCE.md` Phase 29 v2 H3 block + `.planning/milestones/v1.6-phases/29-multi-board-bench-verification/29-04-SUMMARY.md`.
- See full archive: `.planning/MILESTONES.md` §v1.6, `.planning/milestones/v1.6-REQUIREMENTS.md`, `.planning/v1.6-EVIDENCE.md`.

</details>

## v1.5 — Arduino Uno (ATmega328PB) Board Support (SHIPPED 2026-05-21)

<details>
<summary>✅ v1.5 shipped — `uno328pb` as third first-class firmware target (5 phases, 6 plans). Full detail in `.planning/milestones/v1.5-ROADMAP.md`.</summary>

- **Ship tag:** `3.0.0b4` (both sub-repos, GitHub Pre-release on each).
- **Phases:**
  - [x] Phase 21: Firmware Target — `uno328pb` (2 plans; FW-01..FW-04)
  - [x] Phase 22: Release Pipeline Artifacts (1 plan; REL-01, REL-02)
  - [x] Phase 23: Host CLI Installer Integration (2 plans; INST-01..03, GATE-01)
  - [x] Phase 24: Bench Validation on 328PB-Uno (operator-on-bench; BENCH-01, BENCH-02)
  - [x] Phase 25: Documentation + Milestone Close (1 plan; DOC-01, DOC-02, MS-01)
- **Bench-validated** on operator's 328PB-Uno via `firestarter fw -i --pre` end-to-end on `/dev/ttyUSB0` with `urclock` bootloader. Post-flash handshake reports `v3.0.0b4 / uno328pb`.
- **Open v1.6 backlog** carried forward (3 todos): `large-read-data-jitter-uno328pb` (HIGH, pre-existing, affects all controllers — **now in scope for v1.6**), `w27c512-eeprom-misclassification` (HIGH, operator-tagged asap), `avrdude-mcu-detection-fallback` (low).
- See full archive: `.planning/milestones/v1.5-ROADMAP.md`, `.planning/milestones/v1.5-REQUIREMENTS.md`, `.planning/v1.5-BENCH-RESULTS.md`.

</details>

## v1.3 — CMOS EPROM Family Hardware Validation (PAUSED 2026-05-20)

**Milestone goal:** Bench-validate, on real silicon and on both Arduino Uno + Leonardo, that the algorithm-0x07 (28-pin DIP CMOS UV-EPROM, 212 chips in DB) and algorithm-0x08 (32-pin DIP CMOS UV-EPROM, 127 chips in DB) dispatch logic shipped in v1.0–v1.2 actually programs, reads back, and verifies cleanly across the full 32K → 512K density span. This is **validation, not new features** — architecture is locked.

**Status:** ⏸ Paused 2026-05-20 — hardware-gated. Phase 11 shipped clean; Phase 12 Wave 0 desk-side scaffold committed; Plans 12-01/02/03 (BENCH-01/02/05 — W27C512, SST27SF512, W27C257) + entire Phase 13 + Phase 14 await operator bench hardware (Uno + Leonardo + RURP shield + DIP-28 socket + scope + bench chips). Resume command: `/gsd-execute-phase 12 --wave 1 --interactive` once hardware is available.

**Granularity:** Comprehensive (compressed — focused validation milestone, not a build milestone).
**Phase numbering:** Phases 11-14 (continues from v1.2 close).

### Structural Notes

- **Bench-gated vs. desk-side split.** Phase 11 (coverage matrix + DB inconsistency report) is fully desk-side and can land without hardware. Phases 12 and 13 are operator-on-bench (Uno + Leonardo + chip socket + scope). Phase 14 is paperwork only.
- **PROTO-01/02 are observation protocols, not standalone phases.** Chip-ID read at the start of every BENCH cycle (PROTO-01) and scope-measured VPP at the chip socket during write (PROTO-02) are practiced in Phase 12 where the protocol is established, then carried forward into Phase 13. They map formally to Phase 12 (where the observation protocol is set up + first applied) but the success-criteria coverage runs across both bench phases.
- **Density coverage strategy.** Phase 12 covers the 28-pin / algo-0x07 family at both the marquee 64K size (W27C512, SST27SF512) and the 32K low end (BENCH-05). Phase 13 mirrors this for 32-pin / algo-0x08 at 256K + 512K (W27C020, W27E040) and the 128K low end (BENCH-06). Together this exercises the full address-bus span end-to-end.
- **Deferred v1.2 items.** BENCH-01 (W27C512 bench cycle) naturally closes the four v1.2 hardware-pending UAT items (Phase 08 SC#2/SC#3, Phase 08 HUMAN-UAT.md, Phase 09 Plan-05 Task 3 chip-seated W27C512 UAT). Phase 12 detail flags this closure.
- **Flash budget floor.** v1.2 ship state (Leonardo 24,482 B / 85.4%, Uno 22,262 B / 69.0%, firmware 3.0.0-dev) is a non-regress floor. v1.3 is read-only against firmware semantics; only defect-driven changes are in scope.

### Phases

- [x] **Phase 11: Coverage Matrix & DB Inconsistency Audit** — Desk-side enumeration of all 339 algo-0x07/0x08 DB rows + flag intra-algorithm inconsistencies. ✅ 2026-05-19
- [ ] **Phase 12: 28-Pin / Algo-0x07 Bench Validation** — End-to-end bench cycle on Uno + Leonardo for W27C512, SST27SF512, and the 32K density-low representative; establish chip-ID + VPP scope observation protocols. ⏸ Paused (Wave 0 shipped; Waves 1-3 await hardware)
- [ ] **Phase 13: 32-Pin / Algo-0x08 Bench Validation** — End-to-end bench cycle on Uno + Leonardo for W27C020, W27E040, and the 128K density-low representative; same observation protocols carried forward. ⏸ Paused
- [ ] **Phase 14: Milestone Close & Artifacts** — Publish BENCH-RESULTS, update MILESTONES, archive v1.3 phase directories. ⏸ Paused

### Phase Details

#### Phase 11: Coverage Matrix & DB Inconsistency Audit

**Goal:** Operator has a complete, single-source coverage map of every algo-0x07 + algo-0x08 chip in `chip_database.json`, with intra-algorithm DB inconsistencies surfaced as defect candidates for follow-up milestones.
**Depends on:** Nothing (desk-side; can land before any bench session).
**Requirements:** COV-01, COV-02
**Success Criteria** (what must be TRUE):

  1. A coverage matrix file exists at `.planning/v1.3-COVERAGE-MATRIX.md` (or equivalent) enumerating every algo-0x07 + algo-0x08 row in `chip_database.json` with: manufacturer, part_number(s), pin_count, size_bytes, pulse_duration, chip_id_check, chip_id_value, pinout class. Total row count matches DB histogram (212 + 127 = 339 chips).
  2. The same file (or a companion file) lists every intra-algorithm DB inconsistency — chips that share `pin_count` + `algorithm` but differ in `pulse_duration`, `chip_id_check`, or `pinout` — with each inconsistency labeled as a defect candidate for v1.4 or a sub-repo PR (no auto-fixes applied in v1.3).
  3. Operator can use the matrix to confirm that the six BENCH chips (BENCH-01..06) span the pinout classes and pulse-duration profiles actually represented in the DB, so bench results generalize to the rest of the 339 rows.

**Plans:** 6 plans

- [x] 11-01-PLAN.md — Wave 0 failing-test scaffold for tests/test_audit_coverage_matrix.py (10 tests) ✅ 2026-05-19
- [x] 11-02-PLAN.md — Wave 1 tool skeleton + CLI + §1 Summary + §2 DB Count Reconciliation ✅ 2026-05-19
- [x] 11-03-PLAN.md — Wave 2 §3 Full Enumeration (339 rows, per-algorithm sub-tables, D-06 sort) ✅ 2026-05-19
- [x] 11-04-PLAN.md — Wave 3 §4 Defect Candidates + DEFECT-COV-NN ledger + --check semantics
- [x] 11-05-PLAN.md — Wave 4 §5 BENCH Coverage Proof + golden-file fixture
- [x] 11-06-PLAN.md — Wave 5 D-07 planning-doc count reconciliation (PROJECT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md) ✅ 2026-05-19

#### Phase 12: 28-Pin / Algo-0x07 Bench Validation

**Goal:** On both Uno and Leonardo, operator can run a full write → read-back → verify cycle on every named 28-pin CMOS UV-EPROM (W27C512, SST27SF512) and on a 32K density-low representative, with chip-ID and VPP observation protocols established and captured.
**Depends on:** Phase 11 (coverage matrix informs which density-low representative is in scope and which pinout classes are exercised). Bench hardware: Uno + Leonardo + RURP shield + DIP-28 socket + scope.
**Requirements:** BENCH-01, BENCH-02, BENCH-05, PROTO-01, PROTO-02
**Plans:** 4 plans (Wave 0 shipped; Waves 1-3 paused on bench hardware)

#### Phase 13: 32-Pin / Algo-0x08 Bench Validation

**Goal:** On both Uno and Leonardo, operator can run a full write → read-back → verify cycle on every named 32-pin CMOS UV-EPROM (W27C020, W27E040) and on a 128K density-low representative, completing the algo-0x08 family coverage at the high (512K) and low (128K) ends of the address-bus span.
**Depends on:** Phase 12 (chip-ID + VPP observation protocols established; bench harness validated against algo-0x07 first).
**Requirements:** BENCH-03, BENCH-04, BENCH-06
**Plans:** TBD (paused on bench hardware)

#### Phase 14: Milestone Close & Artifacts

**Goal:** v1.3 ships with a per-chip, per-board green/red/quirks artifact covering all six BENCH chips and both PROTO observation protocols, plus a clean milestone close (MILESTONES.md updated, phase directories archived).
**Depends on:** Phases 11, 12, 13.
**Requirements:** DOC-01, DOC-02
**Plans:** TBD (paused on bench hardware)

### v1.3 Coverage

| REQ-ID | Phase |
|--------|-------|
| BENCH-01 | Phase 12 |
| BENCH-02 | Phase 12 |
| BENCH-03 | Phase 13 |
| BENCH-04 | Phase 13 |
| BENCH-05 | Phase 12 |
| BENCH-06 | Phase 13 |
| PROTO-01 | Phase 12 (observation protocol carried forward into Phase 13) |
| PROTO-02 | Phase 12 (observation protocol carried forward into Phase 13) |
| COV-01 | Phase 11 |
| COV-02 | Phase 11 |
| DOC-01 | Phase 14 |
| DOC-02 | Phase 14 |

**Mapped: 12/12 requirements ✓** — no orphans, no duplicates.

## Prior Milestones (archived)

<details>
<summary>✅ v1.4 Beta & Pre-release Deployment Pipeline (Phases 15-20) — SHIPPED 2026-05-20</summary>

- [x] **Phase 15**: Versioning & Locked-Step Coordination (foundation) — 4/4 plans
- [x] **Phase 16**: App Beta Release Pipeline — 1/1 plan
- [x] **Phase 17**: Firmware Beta Release Pipeline — 1/1 plan
- [x] **Phase 18**: Beta-Aware Firmware Downloader (`--pre`, `--firmware-version`, `firmware list`) — 2/2 plans
- [x] **Phase 19**: Documentation (READMEs + `v1.4-RELEASE-PROCEDURES.md`) — 1/1 plan
- [x] **Phase 20**: End-to-End Smoke Test + Milestone Close — 1/1 plan

Ship tag: `3.0.0b3` (auto-incremented from `b1` → `b2` → `b3` during live E2E; six substrate defects E2E-01..06 surfaced and fixed in-place during the cut).
Hardware-flash validated: Uno + Leonardo at `3.0.0b3` via `firestarter fw -i --pre`.

Full milestone archive: [`.planning/milestones/v1.4-ROADMAP.md`](milestones/v1.4-ROADMAP.md).
Requirements archive: [`.planning/milestones/v1.4-REQUIREMENTS.md`](milestones/v1.4-REQUIREMENTS.md) (16/16 complete).
Summary: [`.planning/MILESTONES.md`](MILESTONES.md) §v1.4.
Phase archive: [`.planning/milestones/v1.4-phases/`](milestones/v1.4-phases/).

</details>

<details>
<summary>✅ v1.2 Message-ID Logging Rework (Phases 6-9) — SHIPPED 2026-05-19</summary>

- [x] **Phase 6**: Logging Infrastructure (catalog + codegen + helper + decoder) — 6/6 plans
- [x] **Phase 7**: Convert ERROR + WARN + INFO Call-Sites — 13/13 plans
- [x] **Phase 8**: Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END) — 8/8 plans
- [x] **Phase 9**: Delete Old Log Macros + Measure Flash Savings — 5/5 plans
- [x] **Phase 10**: Milestone Close (v1.2) — closed by `/gsd-complete-milestone` (DOC-02)

Full milestone archive: [`.planning/milestones/v1.2-ROADMAP.md`](milestones/v1.2-ROADMAP.md) (frozen snapshot of full phase details + coverage map + dependency graph).

Requirements archive: [`.planning/milestones/v1.2-REQUIREMENTS.md`](milestones/v1.2-REQUIREMENTS.md) (23/23 complete).

Summary: [`.planning/MILESTONES.md`](MILESTONES.md) §v1.2.

</details>

<details>
<summary>⏸ v1.1 Safety Closure & Hardware Validation (Phases 1-5) — PAUSED 2026-05-18</summary>

- [x] **Phase 1**: Safety Closure (Intel-flash VPP, 28C chip-id) — complete
- [x] **Phase 2**: Wire-key rename + minipro attribution scrub — complete
- [x] **Phase 3**: Retroactive VERIFICATION.md for v1.0 phases — complete
- [ ] **Phase 4**: Hardware validation across chip families — Plan 2 of 3 in progress; **FM1608 byte-0 read bug** parked (needs different Uno R3 to unblock; see [`.planning/debug/fm1608-fresh-chip-baseline.md`](debug/fm1608-fresh-chip-baseline.md))
- [ ] **Phase 5**: Milestone close (DOC-01) — deferred until after v1.2 ships or fm1608 unblocks

Original artifacts: [`.planning/milestones/v1.1-paused/`](milestones/v1.1-paused/).

Also carrying: WARNING-4 (`firestarter_test.sh` / `write_test.sh` references to deleted `database_generated.json`).

</details>

<details>
<summary>✅ v1.0 Protocol-Aware Programming Architecture (Phases 1-13) — SHIPPED 2026-05-11</summary>

- [x] Phases 1-13 covering the algorithm-first dispatch architecture (13 phases, 22 plans, 4-day timeline)
- Key deliverables: protocol-prefix dispatch in `memory.cpp`, 743-chip database with explicit `algorithm` integer, five firmware handlers (`configure_eprom`, `configure_flash3`, `configure_flash_intel`, `configure_eeprom28c`, `configure_sram`), pre-write safety stack (VPP ADC compare, chip-ID validation, blank check), static-pin and address-bus correctness

Full archive: [`.planning/milestones/v1.0-ROADMAP.md`](milestones/v1.0-ROADMAP.md) | [`.planning/milestones/v1.0-REQUIREMENTS.md`](milestones/v1.0-REQUIREMENTS.md) | [`.planning/milestones/v1.0-MILESTONE-AUDIT.md`](milestones/v1.0-MILESTONE-AUDIT.md) | [`.planning/milestones/v1.0-INTEGRATION-CHECK.md`](milestones/v1.0-INTEGRATION-CHECK.md) | [`.planning/milestones/v1.0-phases/`](milestones/v1.0-phases/).

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1-13 (v1.0) | v1.0 | 22/22 | ✅ Shipped | 2026-05-11 |
| 1-3 (v1.1) | v1.1 | done | ✅ Complete | 2026-05-12..18 |
| 4 (v1.1) | v1.1 | partial | ⏸ Parked | — (FM1608 blocked) |
| 5 (v1.1) | v1.1 | 0/0 | ⏸ Deferred | — |
| 6-10 (v1.2) | v1.2 | 32/32 | ✅ Shipped | 2026-05-19 |
| 11 | v1.3 | 6/6 | ✅ Complete | 2026-05-19 |
| 12 | v1.3 | 1/4 | ⏸ Paused | — (hardware-gated) |
| 13 | v1.3 | 0/0 | ⏸ Paused | — (hardware-gated) |
| 14 (close) | v1.3 | 0/0 | ⏸ Paused | — (hardware-gated) |
| 15-20 (v1.4) | v1.4 | 10/10 | ✅ Shipped | 2026-05-20 |
| 21-25 (v1.5) | v1.5 | 6/6 | ✅ Shipped | 2026-05-21 |
| 26 | v1.6 | 2/2 | Complete    | 2026-05-21 |
| 27 | v1.6 | 3/2 | Complete   | 2026-05-26 |
| 28 | v1.6 | 4/4 | Complete    | 2026-05-26 |
| 29 | v1.6 | 1/2 | In Progress|  |
| 30 (close) | v1.6 | 1/3 | In Progress|  |

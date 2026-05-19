# Roadmap: Firestarter — Protocol-Aware Programming Architecture

## Milestones

- ✅ **v1.0 Protocol-Aware Programming Architecture** — Phases 1-13 (shipped 2026-05-11)
- ⏸ **v1.1 Safety Closure & Hardware Validation** — Phases 1-3 done, Phase 4 hardware-validation parked (FM1608 byte-0 bug); Phase 5 milestone-close deferred. Original artifacts preserved at `.planning/milestones/v1.1-paused/`.
- ✅ **v1.2 Message-ID Logging Rework** — Phases 6-9 (shipped 2026-05-19); Phase 10 closed by `/gsd-complete-milestone`. Leonardo Flash 98.7% → 85.4%; firmware 3.0.0-dev.
- 🚧 **v1.3 CMOS EPROM Family Hardware Validation** — Phases 11-14 (in planning, started 2026-05-19). Bench-validate algo-0x07 (28-pin) + algo-0x08 (32-pin) families across full 32K → 512K density span on Uno + Leonardo.

## v1.3 — CMOS EPROM Family Hardware Validation (Active)

**Milestone goal:** Bench-validate, on real silicon and on both Arduino Uno + Leonardo, that the algorithm-0x07 (28-pin DIP CMOS UV-EPROM, 214 chips in DB) and algorithm-0x08 (32-pin DIP CMOS UV-EPROM, 127 chips in DB) dispatch logic shipped in v1.0–v1.2 actually programs, reads back, and verifies cleanly across the full 32K → 512K density span. This is **validation, not new features** — architecture is locked.

**Granularity:** Comprehensive (compressed — focused validation milestone, not a build milestone).
**Phase numbering:** continues from v1.2 close — starts at **Phase 11**.

### Structural Notes

- **Bench-gated vs. desk-side split.** Phase 11 (coverage matrix + DB inconsistency report) is fully desk-side and can land without hardware. Phases 12 and 13 are operator-on-bench (Uno + Leonardo + chip socket + scope). Phase 14 is paperwork only.
- **PROTO-01/02 are observation protocols, not standalone phases.** Chip-ID read at the start of every BENCH cycle (PROTO-01) and scope-measured VPP at the chip socket during write (PROTO-02) are practiced in Phase 12 where the protocol is established, then carried forward into Phase 13. They map formally to Phase 12 (where the observation protocol is set up + first applied) but the success-criteria coverage runs across both bench phases.
- **Density coverage strategy.** Phase 12 covers the 28-pin / algo-0x07 family at both the marquee 64K size (W27C512, SST27SF512) and the 32K low end (BENCH-05). Phase 13 mirrors this for 32-pin / algo-0x08 at 256K + 512K (W27C020, W27E040) and the 128K low end (BENCH-06). Together this exercises the full address-bus span end-to-end.
- **Deferred v1.2 items.** BENCH-01 (W27C512 bench cycle) naturally closes the four v1.2 hardware-pending UAT items (Phase 08 SC#2/SC#3, Phase 08 HUMAN-UAT.md, Phase 09 Plan-05 Task 3 chip-seated W27C512 UAT). Phase 12 detail flags this closure.
- **Flash budget floor.** v1.2 ship state (Leonardo 24,482 B / 85.4%, Uno 22,262 B / 69.0%, firmware 3.0.0-dev) is a non-regress floor. v1.3 is read-only against firmware semantics; only defect-driven changes are in scope.

### Phases

- [ ] **Phase 11: Coverage Matrix & DB Inconsistency Audit** — Desk-side enumeration of all 341 algo-0x07/0x08 DB rows + flag intra-algorithm inconsistencies.
- [ ] **Phase 12: 28-Pin / Algo-0x07 Bench Validation** — End-to-end bench cycle on Uno + Leonardo for W27C512, SST27SF512, and the 32K density-low representative; establish chip-ID + VPP scope observation protocols.
- [ ] **Phase 13: 32-Pin / Algo-0x08 Bench Validation** — End-to-end bench cycle on Uno + Leonardo for W27C020, W27E040, and the 128K density-low representative; same observation protocols carried forward.
- [ ] **Phase 14: Milestone Close & Artifacts** — Publish BENCH-RESULTS, update MILESTONES, archive v1.3 phase directories.

### Phase Details

#### Phase 11: Coverage Matrix & DB Inconsistency Audit
**Goal:** Operator has a complete, single-source coverage map of every algo-0x07 + algo-0x08 chip in `chip_database.json`, with intra-algorithm DB inconsistencies surfaced as defect candidates for follow-up milestones.
**Depends on:** Nothing (desk-side; can land before any bench session).
**Requirements:** COV-01, COV-02
**Success Criteria** (what must be TRUE):
  1. A coverage matrix file exists at `.planning/v1.3-COVERAGE-MATRIX.md` (or equivalent) enumerating every algo-0x07 + algo-0x08 row in `chip_database.json` with: manufacturer, part_number(s), pin_count, size_bytes, pulse_duration, chip_id_check, chip_id_value, pinout class. Total row count matches DB histogram (214 + 127 = 341 chips).
  2. The same file (or a companion file) lists every intra-algorithm DB inconsistency — chips that share `pin_count` + `algorithm` but differ in `pulse_duration`, `chip_id_check`, or `pinout` — with each inconsistency labeled as a defect candidate for v1.4 or a sub-repo PR (no auto-fixes applied in v1.3).
  3. Operator can use the matrix to confirm that the six BENCH chips (BENCH-01..06) span the pinout classes and pulse-duration profiles actually represented in the DB, so bench results generalize to the rest of the 341 rows.
**Plans:** 6 plans
- [x] 11-01-PLAN.md — Wave 0 failing-test scaffold for tests/test_audit_coverage_matrix.py (10 tests) ✅ 2026-05-19
- [ ] 11-02-PLAN.md — Wave 1 tool skeleton + CLI + §1 Summary + §2 DB Count Reconciliation
- [ ] 11-03-PLAN.md — Wave 2 §3 Full Enumeration (339 rows, per-algorithm sub-tables, D-06 sort)
- [ ] 11-04-PLAN.md — Wave 3 §4 Defect Candidates + DEFECT-COV-NN ledger + --check semantics
- [ ] 11-05-PLAN.md — Wave 4 §5 BENCH Coverage Proof + golden-file fixture
- [ ] 11-06-PLAN.md — Wave 5 D-07 planning-doc count reconciliation (PROJECT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md)

#### Phase 12: 28-Pin / Algo-0x07 Bench Validation
**Goal:** On both Uno and Leonardo, operator can run a full write → read-back → verify cycle on every named 28-pin CMOS UV-EPROM (W27C512, SST27SF512) and on a 32K density-low representative, with chip-ID and VPP observation protocols established and captured.
**Depends on:** Phase 11 (coverage matrix informs which density-low representative is in scope and which pinout classes are exercised). Bench hardware: Uno + Leonardo + RURP shield + DIP-28 socket + scope.
**Requirements:** BENCH-01, BENCH-02, BENCH-05, PROTO-01, PROTO-02
**Success Criteria** (what must be TRUE):
  1. Operator can complete the full bench cycle (chip-ID read where applicable → blank-check → write of the deterministic test image → read-back → byte-identical verify → post-cycle blank-check where electrically erasable) for W27C512 on both Uno and Leonardo with green-verdict result captured for the BENCH-RESULTS artifact. Closes deferred v1.2 Phase 08 SC#2/SC#3 + Phase 09 Plan-05 Task 3 + Phase 08 HUMAN-UAT.md.
  2. Same full bench cycle completes cleanly on both boards for SST27SF512.
  3. Same full bench cycle completes cleanly on both boards for the chosen 32K density-low representative (W27C257 or W27E257 or SST27SF256), exercising the low end of the algo-0x07 address-bus span.
  4. Chip-ID observation protocol (PROTO-01): for every chip in BENCH-01/02/05 where `chip_id_check: true` in `chip_database.json`, the chip-ID read returns the DB-declared `chip_id_value` on both boards; mismatches confirmed to block write via the safety stack. Observation protocol is recorded in a way that Phase 13 can re-apply it without re-derivation.
  5. VPP observation protocol (PROTO-02): scope-measured VPP at the chip socket VPP pin reads 12V ±5% during write/erase phases and idles at VCC or off between operations, on both boards, for every chip in BENCH-01/02/05. Scope trace captured at least once per board.
**Plans:** TBD

#### Phase 13: 32-Pin / Algo-0x08 Bench Validation
**Goal:** On both Uno and Leonardo, operator can run a full write → read-back → verify cycle on every named 32-pin CMOS UV-EPROM (W27C020, W27E040) and on a 128K density-low representative, completing the algo-0x08 family coverage at the high (512K) and low (128K) ends of the address-bus span. Chip-ID + VPP observation protocols from Phase 12 are re-applied.
**Depends on:** Phase 12 (chip-ID + VPP observation protocols established; bench harness validated against algo-0x07 first). Bench hardware: Uno + Leonardo + RURP shield + DIP-32 socket + scope.
**Requirements:** BENCH-03, BENCH-04, BENCH-06
**Success Criteria** (what must be TRUE):
  1. Operator can complete the full bench cycle (chip-ID read where applicable → blank-check → write of the deterministic test image → read-back → byte-identical verify → post-cycle blank-check where electrically erasable) for W27C020 on both Uno and Leonardo with green-verdict result captured.
  2. Same full bench cycle completes cleanly on both boards for W27E040, exercising the algo-0x08 512K high-end address-bus span.
  3. Same full bench cycle completes cleanly on both boards for the chosen 128K density-low representative (W27C010 or W27E010 or W27L010 or SST27SF010), exercising the low end of the algo-0x08 address-bus span.
  4. The chip-ID and VPP observation protocols set up in Phase 12 (PROTO-01, PROTO-02) are re-applied across BENCH-03/04/06 with no protocol modifications; any deviation (e.g. a chip with `chip_id_check: false` that nonetheless returns a stable ID, or a VPP rail that drifts beyond ±5%) is captured as a Phase 14 BENCH-RESULTS quirk note.
**Plans:** TBD

#### Phase 14: Milestone Close & Artifacts
**Goal:** v1.3 ships with a per-chip, per-board green/red/quirks artifact covering all six BENCH chips and both PROTO observation protocols, plus a clean milestone close (MILESTONES.md updated, phase directories archived).
**Depends on:** Phases 11, 12, 13 (all bench cycles complete and coverage matrix in hand).
**Requirements:** DOC-01, DOC-02
**Success Criteria** (what must be TRUE):
  1. `.planning/v1.3-BENCH-RESULTS.md` exists with a per-chip, per-board table covering BENCH-01..06 + PROTO-01/02 observations: green/red verdict, scope-measured VPP trace reference, chip-ID read result vs. `chip_id_value`, quirks noted, serial-log snippets (verbose-mode INFO or SERIAL_DEBUG breadcrumbs) where captured, photo or scope evidence linked where available.
  2. `MILESTONES.md` carries a v1.3 milestone summary (delivered, stats, decisions, known gaps if any) styled consistently with the v1.0 and v1.2 entries; v1.3 phase directories archived to `.planning/milestones/v1.3-phases/`; `PROJECT.md` updated to reflect v1.3 ship state.
  3. Flash budget non-regress floor (Leonardo 24,482 B / 85.4%, Uno 22,262 B / 69.0%, firmware 3.0.0-dev) is confirmed unchanged at milestone close — v1.3 introduced no firmware code paths that grew flash usage.
**Plans:** TBD

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
| 6 | v1.2 | 6/6 | ✅ Complete | 2026-05-18 |
| 7 | v1.2 | 13/13 | ✅ Complete | 2026-05-18 |
| 8 | v1.2 | 8/8 | ✅ Complete | 2026-05-18 |
| 9 | v1.2 | 5/5 | ✅ Complete | 2026-05-19 |
| 10 (close) | v1.2 | n/a | ✅ Complete | 2026-05-19 |
| 11 | v1.3 | 1/6 | 🚧 Executing | — |
| 12 | v1.3 | 0/0 | Not started | — |
| 13 | v1.3 | 0/0 | Not started | — |
| 14 (close) | v1.3 | 0/0 | Not started | — |

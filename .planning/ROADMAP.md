# Roadmap: Firestarter — Protocol-Aware Programming Architecture

## Milestones

- ✅ **v1.0 Protocol-Aware Programming Architecture** — Phases 1-13 (shipped 2026-05-11)
- ⏸ **v1.1 Safety Closure & Hardware Validation** — Phases 1-3 done, Phase 4 hardware-validation parked (FM1608 byte-0 bug); Phase 5 milestone-close deferred. Original artifacts preserved at `.planning/milestones/v1.1-paused/`.
- ✅ **v1.2 Message-ID Logging Rework** — Phases 6-10 (shipped 2026-05-19); Phase 10 closed by `/gsd-complete-milestone` (DOC-02)
- ⏸ **v1.3 CMOS EPROM Family Hardware Validation** — Phases 11-14 (PAUSED 2026-05-20, hardware-gated). Phase 11 shipped + Phase 12 Wave 0 scaffold committed; Plans 12-01/02/03 + Phases 13/14 await operator bench hardware.
- ✅ **v1.4 Beta & Pre-release Deployment Pipeline** — Phases 15-20 (shipped 2026-05-20; ship tag `3.0.0b3` in both sub-repos; hardware-flash validated on Uno + Leonardo). Parallel beta channel for both sub-repos without disrupting the stable main → release pipeline.
- ✅ **v1.5 Arduino Uno (ATmega328PB) Board Support** — Phases 21-25 (shipped 2026-05-21; ship tag `3.0.0b4`; bench-validated on operator's 328PB-Uno via `urclock` bootloader). `uno328pb` as a third first-class firmware target alongside `uno` + `leonardo`. Full detail in `.planning/milestones/v1.5-ROADMAP.md`; bench evidence in `.planning/v1.5-BENCH-RESULTS.md`.
- ⏸ **v1.6 Fix the Read Bug** — Phases 26-30 (SHIPPED 2026-05-26 as "diagnostic + revert" per D-17v2). Read-bug carries to v1.9 as Bug A + Bug B RCA seed.
- ✅ **v1.7 RURP Shield Hardware Investigation & Version Detection** — Phases 31-35 (SHIPPED 2026-05-26). Per-rev capability table + labeled schematics + shield-version-detect firmware plumbing.
- ✅ **v1.8 Host CLI Structural Cleanup (firestarter_app)** — Phases 36-43 (SHIPPED 2026-05-29; ship tag `3.0.0b7` beta-only). 27 requirements DELIVERED + 3 VERIFIED-at-close; argparse→Click, mypy strict on 8 modules, 70% coverage floor. Full detail in `.planning/MILESTONES.md` §v1.8.
- 🚧 **v1.9 Read-Bug RCA + Fix** — Phases 44-48 (STARTED 2026-05-29). Hardware-gated; firmware sub-repo work expected. Root-cause and fix Bug A (Modified Rev 0 upper-address jitter) + Bug B (Rev 2.0 /CE-/OE timing + VPP mismatch); N≥5 byte-identical acceptance gate across shield fleet.

## v1.9 — Read-Bug RCA + Fix (STARTED 2026-05-29)

**Milestone goal:** Root-cause and fix the EPROM read-bug deferred since v1.6, restoring N≥5 byte-identical reads across the shield fleet (Modified Rev 0, Rev 2.0, Rev 2.2). Inherits the v1.6 `dev consistency-check` diagnostic, the 15-binary N=5 W27C512 bench substrate at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`, the Phase 29 v2 Bug A/Bug B characterization in `.planning/v1.6-EVIDENCE.md`, the v1.7 schematics + shield-version-detect plumbing, and the v1.8 cleaned-up host read path (GATE-1.8d ring-fence intact — baselines still valid).

**Hardware-gated:** All bench operations are operator-authorized (shield swaps, scope traces, A/B fix trials). Per `feedback_chip_out_before_sideload`: chip leaves socket before any firmware sideload. Per `feedback_verify_port_identity_each_task`: controller identity verified per port at each bench task. Per `user_shield_revisions`: operator asked which silkscreen rev is on bench (EEPROM hw_revision byte cannot distinguish revs).

**Phase numbering:** Continues from v1.8 last phase 43 → v1.9 starts at **Phase 44**.

### Phases

- [ ] **Phase 44: Bug A RCA — Modified Rev 0 Upper-Address Jitter** — Instrument the Modified Rev 0 A15=1 jitter to a definitive signal-integrity mechanism; begin per-rev failure-mode map.
- [ ] **Phase 45: Bug B RCA — Rev 2.0 Timing & Voltage** — Instrument the Rev 2.0 /CE-or-/OE timing + VPP=13.1V failure to a definitive root cause; complete the per-rev failure-mode map.
- [ ] **Phase 46: Fix Design & A/B Bench Trials** — Design firmware fix candidates for Bug A and Bug B; A/B-test on the affected boards; regression-check across the shield fleet.
- [ ] **Phase 47: Acceptance Gate + Backlog Closures** — Re-run the Phase 29 acceptance gate (N≥5 byte-identical W27C512 reads across boards with fix applied); close VERIFY-01/03/04 backlog.
- [ ] **Phase 48: COBS Evaluation + Post-RCA Cleanup + Milestone Close** — Evaluate COBS framing on the serial data path (adopt/defer/reject decision); lift `eprom_operations.py` mypy strict overrides; close milestone with documentation and branch promotion.

## Phase Details

### Phase 44: Bug A RCA — Modified Rev 0 Upper-Address Jitter

**Goal**: The Modified Rev 0 A15=1 upper-address jitter is proven to a specific signal-integrity mechanism (ringing, crosstalk, settling-time violation, or other), with scope traces and/or circuit analysis as evidence — going beyond the Phase 29 v2 symptom characterization (1.86× skew, 63% bit-raise).
**Depends on**: Phase 29 v2 evidence substrate (`.planning/v1.6-EVIDENCE.md` H3 block), v1.7 shield-version-detect plumbing, v1.8 cleaned-up host read path. Bench hardware: Modified Rev 0 shield + scope + operator authorization.
**Requirements**: RCA-01, RCA-03 (partial — Modified Rev 0 failure mode confirmed)
**Success Criteria** (what must be TRUE):

  1. Operator-witnessed scope trace (or equivalent circuit measurement) identifies the specific electrical cause of A15=1 address line jitter on Modified Rev 0, not merely the symptom — e.g. "ringing on A15 due to missing series termination" or "settling time violation at current read-pulse width". *(Per CONTEXT D-07, the causal-only bar — a knob that controls the jitter — governs over this wording; mechanism-naming is a stretch goal.)*
  2. The root-cause mechanism is documented with supporting evidence (scope screenshot or measurement values) sufficient to inform a targeted fix strategy — not just "the signal is slow".
  3. `firestarter dev consistency-check` run on Modified Rev 0 reproduces the Phase 29 v2 pattern (jitter present, WORST ≥ 1% zeros) as a controlled baseline before any fix is applied, confirming bench continuity with v1.6 substrate.
  4. Per-rev failure-mode map is started: Modified Rev 0 → Bug A confirmed; Rev 2.2 entry recorded (confirm whether Rev 2.2 shows Bug A or is clean).

**Plans**: 5 plans
Plans:
**Wave 1**

- [x] 44-01-PLAN.md — Wave 1: fork v1.9-read-bug-rca off beta in both sub-repos + recover v1.7-SHIELD-REVS.md (git/working-tree prereq)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 44-02-PLAN.md — Wave 2: firmware read-timing knobs (read_settling_us / read_strobe_us) + bounds cap + Wave 0 native Unity tests
- [ ] 44-03-PLAN.md — Wave 2: host knob params + CLI options + Wave 0 pytest + 2D sweep harness

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 44-04-PLAN.md — Wave 3 (bench): static circuit inspection (D-01/D-02) + N=5 baseline repro vs Phase 29 v2 (D-11)

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 44-05-PLAN.md — Wave 4 (bench): 2D causal sweep + LA capture (D-03/04/05/06/08) + RCA findings + per-rev map (RCA-03 partial / D-10)

### Phase 45: Bug B RCA — Rev 2.0 Timing & Voltage

**Goal**: The Rev 2.0 read-failure mechanism (/CE-or-/OE timing mismatch + voltage-divider mismatch + VPP=13.1V interaction) is proven to a definitive root cause, with bench evidence identifying which factor(s) are causal vs incidental.
**Depends on**: Phase 44 (per-rev map started; bench protocol established). Bench hardware: Rev 2.0 shield + scope + operator authorization.
**Requirements**: RCA-02, RCA-03 (completion — Rev 2.0 failure mode confirmed; full per-rev map finalized)
**Success Criteria** (what must be TRUE):

  1. Operator-witnessed bench measurement on Rev 2.0 isolates the dominant failure factor: timing margin (/CE or /OE pulse width relative to chip t_ACC), voltage-divider mismatch (VPP at chip pin vs. expected), or VPP=13.1V overstress — with evidence distinguishing causal from coincidental.
  2. The Rev 2.0 failure reproduces with `firestarter dev consistency-check` as a controlled baseline (jitter present, WORST ≥ 1% zeros, or the specific failure mode observed in Phase 29 v2).
  3. Per-rev failure-mode map is complete and documented: Modified Rev 0 → Bug A (upper-address jitter); Rev 2.0 → Bug B (timing/voltage); Rev 2.2 → confirmed clean or categorized; each entry cites the evidence from Phase 44 / Phase 45.
  4. RCA-02 root cause is documented with enough detail that a firmware-side or host-side fix candidate can be designed without further scope work (i.e., the mechanism is fully understood, not just observed).

**Plans**: TBD

### Phase 46: Fix Design & A/B Bench Trials

**Goal**: Firmware (and/or host-side) fix candidates for Bug A and Bug B are designed based on the Phase 44/45 root causes, A/B-tested on the affected boards, and verified not to regress the unaffected boards — leaving a committed fix in both sub-repos ready for acceptance gating.
**Depends on**: Phase 44 (Bug A root cause proven), Phase 45 (Bug B root cause proven). Bench hardware: all three shields (Modified Rev 0, Rev 2.0, Rev 2.2) + operator authorization. Firmware sub-repo `firestarter/` work expected.
**Requirements**: FIX-01, FIX-02, FIX-03
**Success Criteria** (what must be TRUE):

  1. A/B comparison on Modified Rev 0: `firestarter dev consistency-check` with fix applied shows WORST < 0.1% zeros (or byte-identical N=5 reads), vs. pre-fix baseline showing the Bug A pattern — operator-witnessed, result recorded.
  2. A/B comparison on Rev 2.0: `firestarter dev consistency-check` with fix applied shows WORST < 0.1% zeros (or byte-identical N=5 reads), vs. pre-fix baseline showing the Bug B pattern — operator-witnessed, result recorded.
  3. Rev 2.2 regression check: `firestarter dev consistency-check` on Rev 2.2 with the fix applied returns the same clean baseline as pre-fix (WORST stays ≤ 0.1% zeros or equivalent); no fix for one rev breaks reads on another.
  4. The fix is committed to the firmware sub-repo (and/or host sub-repo) with atomic commits citing the RCA findings from Phases 44/45; unit tests (Unity or pytest) covering the changed code path are committed alongside the fix.

**Plans**: TBD
**UI hint**: no

### Phase 47: Acceptance Gate + Backlog Closures

**Goal**: The headline Phase 29 acceptance gate is re-run with the fix applied and passes on all boards; the three v1.6 backlog closures (VERIFY-01/03/04) are completed, retiring the open items that have been carried since v1.6.
**Depends on**: Phase 46 (fix committed and A/B-tested on both bug families). Bench hardware: all three shields + uno328pb board + operator authorization.
**Requirements**: VERIFY-A, VERIFY-01, VERIFY-03, VERIFY-04
**Success Criteria** (what must be TRUE):

  1. N≥5 consecutive `firestarter read W27C512` invocations return byte-identical SHA-256 hashes on Modified Rev 0, Rev 2.0, AND Rev 2.2 shields — operator-witnessed, hashes recorded in bench artifact.
  2. uno328pb byte-identity confirmed (VERIFY-01): N≥5 `firestarter read` on the 328PB-Uno + RURP shield returns byte-identical results, closing the v1.6 carry-forward backlog item.
  3. 1KB low-rate jitter resolved (VERIFY-03): `firestarter dev read -s 1024` returns consistent results without the jitter pattern observed in v1.5/v1.6 bench sessions.
  4. Phase 24 BENCH-02 closure (VERIFY-04): the 328PB-Uno bench cycle item carried from v1.5 Phase 24 is formally closed with a recorded bench result or documented disposition.

**Plans**: TBD

### Phase 48: COBS Evaluation + Post-RCA Cleanup + Milestone Close

**Goal**: The COBS framing evaluation yields a documented adopt/defer/reject decision with rationale; the `eprom_operations.py` mypy strict overrides are lifted now that the read path is fixed and free to touch; the milestone is documented and branches promoted.
**Depends on**: Phase 46 (read path is fixed — TYPE-01 is gated on this). Phase 47 (acceptance gate passed — milestone close follows). COBS-01 is independent of the hardware RCA and can proceed in parallel or after Phase 46.
**Requirements**: COBS-01, TYPE-01
**Success Criteria** (what must be TRUE):

  1. A written COBS-01 decision document (or section in a planning artifact) records: PacketSerial re-assessed, custom COBS layer option evaluated, and a clear adopt/defer/reject verdict with rationale referencing the current serial data-path shape post-v1.8 cleanup — not just "we looked at it".
  2. `eprom_operations.py` mypy strict overrides are removed (or reduced to the minimum justifiable residual); `mypy` on `eprom_operations.py` exits without the deferred-per-D-07 suppressions; the change is covered by the existing test suite.
  3. MILESTONES.md gains a complete v1.9 entry covering the RCA findings, fix summary, acceptance gate result, and COBS decision.
  4. Sub-repo branches for v1.9 are promoted per the branching convention; a new beta pre-release tag is cut (at minimum); the stable `3.0.1` promotion checklist is either executed or explicitly deferred with rationale.

**Plans**: TBD

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
| 26 | v1.6 | 2/2 | ✅ Complete | 2026-05-21 |
| 27 | v1.6 | 3/2 | ✅ Complete | 2026-05-26 |
| 28 | v1.6 | 4/4 | ✅ Complete | 2026-05-26 |
| 29 | v1.6 | 4/4 | ✅ Complete | 2026-05-26 |
| 30 (close) | v1.6 | 3/3 | ✅ Shipped | 2026-05-26 |
| 31-35 (v1.7) | v1.7 | — | ✅ Shipped | 2026-05-26 |
| 36-43 (v1.8) | v1.8 | 26/26 | ✅ Shipped | 2026-05-29 |
| 44 | v1.9 | 2/5 | In Progress|  |
| 45 | v1.9 | 0/TBD | Not started | — |
| 46 | v1.9 | 0/TBD | Not started | — |
| 47 | v1.9 | 0/TBD | Not started | — |
| 48 (close) | v1.9 | 0/TBD | Not started | — |

## v1.8 — Host CLI Structural Cleanup (firestarter_app) (SHIPPED 2026-05-29)

<details>
<summary>✓ v1.8 shipped — Host CLI structural cleanup (firestarter_app); 8 phases, 27 requirements DELIVERED + 3 VERIFIED-AT-CLOSE; ship tag 3.0.0b7 beta-only. Full detail in `.planning/MILESTONES.md` §v1.8.</summary>

- **Ship tag:** `3.0.0b7` (beta-only; stable `3.0.1` deferred to v1.9 read-bug fix per D-17v2 carry-forward)
- **Phases:**
  - [x] Phase 36: Characterization Test Baseline (TEST-01..05)
  - [x] Phase 37: Tooling Baseline + CI Gate (TOOL-01..03)
  - [x] Phase 38: Low-risk Extractions (STRUCT-01..05)
  - [x] Phase 39: Database Cleanup + Chip Resolver (DATA-01..04)
  - [x] Phase 40: Serial Transport Restructure (SERIAL-01..03)
  - [x] Phase 41: CLI Migration argparse → Click (CLI-01..04; BUG-1 INTENTIONAL BEHAVIOR CHANGE)
  - [x] Phase 42: Error Handling Normalization + Quality Sweep (ERR-01..03; BUG-2 INTENTIONAL BEHAVIOR CHANGE; mypy strict on 8 modules; coverage 70.12%)
  - [x] Phase 43: Documentation + Milestone Close (DOC-01..02, MS-01)
- **Branch model:** sub-repo `v1.8-app-cleanup` off `beta@3.0.0b6` (firestarter_app only); meta-repo `v1.8-app-cleanup` off `main`; firmware sub-repo untouched at `beta@0bbe017` from v1.6 close.
- **v1.9 hand-off:** read-bug (Bug A + Bug B) carries forward with GATE-1.8d ring-fence intact; 15 N=5 W27C512 baseline binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` remain valid because `_read_and_parse_lines` body is byte-identical pre/post v1.8; `eprom_operations.py` mypy strict + `ProtocolStateMachine` extraction also carry to v1.9.
- See full archive: `.planning/MILESTONES.md` §v1.8, `.planning/milestones/v1.8-REQUIREMENTS.md`, `.planning/milestones/v1.8-phases/`.

</details>

## v1.7 — RURP Shield Hardware Investigation & Version Detection (SHIPPED 2026-05-26)

<details>
<summary>✅ v1.7 shipped — per-rev capability table + labeled schematics + shield-version-detect firmware plumbing (5 phases). Full detail in `.planning/MILESTONES.md` §v1.7.</summary>

- **Phases:**
  - [x] Phase 31: Upstream Shield Archaeology (HW-INV-01, HW-INV-02, HW-INV-03, SILK-01)
  - [x] Phase 32: Inter-Rev Difference + Capability Matrix (DIFF-01, DIFF-02, CAPS-01, CAPS-02)
  - [x] Phase 33: Silkscreen Label → Code Alias Migration (ALIAS-01, ALIAS-02, ALIAS-03)
  - [x] Phase 34: Shield-Version-Detect Design + Firmware Plumbing (DETECT-HW-01, DETECT-HW-02, DETECT-FW-01, DETECT-FW-02)
  - [x] Phase 35: Documentation + Milestone Close (DOC-01, MS-01)
- **Canonical reference:** `.planning/v1.7-SHIELD-REVS.md` (9 sections: inventory, difference matrix, capability matrix, alias table, detect-hw schematic delta, per-rev ADC band table, labeled schematics, operator-board annotations, v1.8 hand-off).
- See full archive: `.planning/MILESTONES.md` §v1.7.

</details>

## v1.6 — Fix the Read Bug (SHIPPED 2026-05-26 — diagnostic + revert)

<details>
<summary>✅ v1.6 shipped — ships as "diagnostic + revert" per D-17v2 (5 phases, 13 plans). Read-bug carries to v1.9 with Bug A + Bug B pattern findings as RCA seed. Full detail in `.planning/MILESTONES.md` §v1.6.</summary>

- **Ship tag:** `3.0.0b6` (beta-only; both sub-repos lockstep)
- **Phases:**
  - [x] Phase 26: Cross-board Reproduction & Diagnostic Tooling (2 plans; REPRO-01..03)
  - [x] Phase 27: Root Cause Analysis (3 plans incl. re-open Plan 27-05; RCA-01..03)
  - [x] Phase 28: Fix Implementation + Unit Test Coverage (4 plans incl. revert Plan 28-03 + parked Plan 28-04; FIX-01..03 as diagnostic + revert)
  - [x] Phase 29: Multi-Board Bench Verification (4 plans incl. v2 re-iteration Plans 29-03/04; VERIFY-02 PASS via structured_data shape; VERIFY-01/03/04 DEFERRED to v1.9)
  - [x] Phase 30: Documentation + Milestone Close (3 plans; DOC-01/02 + MS-01)
- **Re-scope (D-17v2):** Phase 29 v1 Wave B FAIL → Plan 27-05 re-open confirmed dual-cause (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb hardware) → Plan 28-03 reverted `437339b6` via `ea25174`; `4f205e58` `_NOP()` settling preserved (Plan 28-04 parks) → Phase 29 v2 PASS_PARKED (Leonardo Modified Rev 0 returns to Phase 26 baseline; WORST 0.047% zeros vs 83.8% pre-revert).
- **v1.9 hand-off:** 15 N=5 W27C512 binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`; Bug A (Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew) + Bug B (Rev 2.0 /CE-or-/OE timing + VPP=13.1V) characterized in `.planning/v1.6-EVIDENCE.md` Phase 29 v2 H3 block + `.planning/milestones/v1.6-phases/29-multi-board-bench-verification/29-04-SUMMARY.md`.
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
- **Open v1.9 backlog** carried forward (3 todos): `large-read-data-jitter-uno328pb` (HIGH, pre-existing, affects all controllers — now in scope for v1.9), `w27c512-eeprom-misclassification` (HIGH, operator-tagged asap), `avrdude-mcu-detection-fallback` (low).
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

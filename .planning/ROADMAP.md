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
- ✅ **v1.10 Serial Transport Hardening (COBS)** — Phases 49-55 (SHIPPED 2026-06-07; beta-only, stable `3.0.1` operator-gated/deferred to the v1.9 read-bug fix). Custom COBS `0x00` + CRC8 framing with automatic resync on **both** the data-block path and the host→fw JSON command channel; transport now provably byte-exact across Uno/Leonardo, ruling serial out as a read-bug confounder. 14/14 requirements; operator-witnessed bench close. Full detail in `.planning/MILESTONES.md` §v1.10 + `.planning/milestones/v1.10-ROADMAP.md`.
- ⏸ **v1.9 Read-Bug RCA + Fix** — Phases 44-48 (PAUSED 2026-06-01 at Phase 44 — v1.10 inserted ahead; resumes at Phase 45). Hardware-gated; firmware sub-repo work expected. Root-cause and fix Bug A (Modified Rev 0 upper-address jitter) + Bug B (Rev 2.0 /CE-/OE timing + VPP mismatch); N≥5 byte-identical acceptance gate across shield fleet.
- ✅ **v1.11 Complete infoic.xml Decode & Database Correctness** — Phases 56-61 (SHIPPED 2026-06-10; beta-only, stable operator-gated). HOST-ONLY decode-correctness + authoritative-docs milestone (firmware untouched like v1.8): source-grounded field dictionary + corrected decode docs, re-derived `build_db.py` (4 decode bugs fixed), principled `resolve_pinout_key`, 9 × 24-pin EEPROMs unblocked host-only, full-class VPP-safety + per-chip diff gates, display layer (`info`/`list`/`search`) reflects `electrical.type`. 15/15 requirements; audit PASSED (5/5 E2E flows, 559 tests, 743 chips). Full detail in `.planning/MILESTONES.md` §v1.11 + `.planning/milestones/v1.11-ROADMAP.md`.
- 🔄 **v1.12 Firmware Protocol Dispatch Hardening + Skeletons** — Phases 62-68 (STARTED 2026-06-10). First firmware-touching milestone since v1.10. Fail-closed dispatch + not-implemented wire response + skeleton infeasibility markers; capability-honest DB inclusion (include-but-flag unsupported DIP parallel chips with `support_status` taxonomy: `protocol-not-implemented` / `adapter-required` / `vpp-exceeds-max`; true NMOS VPP correction; pinout engineering); dual-repo lockstep, unified-beta branch model. 17/17 requirements in progress.

<details>
<summary>✅ <b>v1.10 — Serial Transport Hardening (COBS)</b> — Phases 49–55 (SHIPPED 2026-06-07) · 27/27 plans · 14/14 reqs · beta-only</summary>

**Milestone goal:** A custom delimiter-based serial framing + automatic-resync layer on the Arduino↔host data path — covering **both** the binary data-block path **and** the host→fw JSON command channel — making the transport provably byte-exact end to end, so serial corruption is ruled out as a confounding variable before the paused per-shield read-bug RCA resumes (v1.9 Phase 45+). COBS `0x00` + CRC8-CCITT poly 0x07 (D-05); Uno-fit streaming-encode-only (D-04). Inserted ahead of the paused v1.9 RCA (Phases 45–48 reserved); branch `v1.10-serial-transport-hardening` stacked off the v1.9 tip in all 3 repos.

**Phases:**

- [x] Phase 49: Framing Mechanism Decision (COBS `0x00` vs SLIP `0xC0`) — 1/1 — 2026-06-01
- [x] Phase 50: Data-Path Framing Layer + Automatic Resync — 4/4 — 2026-06-01
- [x] Phase 51: Command-Channel Framing Migration (breaking wire change) — 4/4 — 2026-06-02
- [x] Phase 52: Lockstep Contract + Round-Trip Tests — 4/4 — 2026-06-02
- [x] Phase 54: Even-Block Data Transfers (full-buffer-aligned host→fw chunks) — 3/3 — 2026-06-04
- [x] Phase 55: Relocate Buffer-Size Advertisement to the OK Ack (+ safe 512 default) — 4/4 — 2026-06-05
- [x] Phase 53: Byte-Exact Bench Verification (hardware-gated, operator-witnessed) — 7/7 — 2026-06-05

**Requirements (14/14 ✓):** SAFE-01 (P49); FRAME-01/02/03/04 + CRC-01 (P50); FRAME-05 (P51); LOCK-01/02 (P52); EVEN-01 (P54); CAP-01 (P55); XACT-01/02/03 (P53).

Full detail: [`.planning/milestones/v1.10-ROADMAP.md`](milestones/v1.10-ROADMAP.md) · [`v1.10-REQUIREMENTS.md`](milestones/v1.10-REQUIREMENTS.md) · [`MILESTONES.md`](MILESTONES.md) §v1.10.

</details>

## v1.9 — Read-Bug RCA + Fix (STARTED 2026-05-29)

**Milestone goal:** Root-cause and fix the EPROM read-bug deferred since v1.6, restoring N≥5 byte-identical reads across the shield fleet (Modified Rev 0, Rev 2.0, Rev 2.2). Inherits the v1.6 `dev consistency-check` diagnostic, the 15-binary N=5 W27C512 bench substrate at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`, the Phase 29 v2 Bug A/Bug B characterization in `.planning/v1.6-EVIDENCE.md`, the v1.7 schematics + shield-version-detect plumbing, and the v1.8 cleaned-up host read path (GATE-1.8d ring-fence intact — baselines still valid).

**Hardware-gated:** All bench operations are operator-authorized (shield swaps, scope traces, A/B fix trials). Per `feedback_chip_out_before_sideload`: chip leaves socket before any firmware sideload. Per `feedback_verify_port_identity_each_task`: controller identity verified per port at each bench task. Per `user_shield_revisions`: operator asked which silkscreen rev is on bench (EEPROM hw_revision byte cannot distinguish revs).

**Phase numbering:** Continues from v1.8 last phase 43 → v1.9 starts at **Phase 44**.

### Phases

- [x] **Phase 44: Bug A RCA — Modified Rev 0 Upper-Address Jitter** *(complete 2026-06-01; re-grounded)* — RCA achieved: Bug A is a **Rev 0-shield read-path fault** (broad read jitter, causally controlled by read-strobe timing — the governing D-07 causal bar), NOT the hypothesized A15 upper-address effect. Per-rev map started.
- [ ] **Phase 45: Bug B RCA — Rev 2.0 Timing & Voltage** — Instrument the Rev 2.0 /CE-or-/OE timing + VPP=13.1V failure to a definitive root cause; complete the per-rev failure-mode map.
- [ ] **Phase 46: Fix Design & A/B Bench Trials** — Design firmware fix candidates for Bug A and Bug B; A/B-test on the affected boards; regression-check across the shield fleet.
- [ ] **Phase 47: Acceptance Gate + Backlog Closures** — Re-run the Phase 29 acceptance gate (N≥5 byte-identical W27C512 reads across boards with fix applied); close VERIFY-01/03/04 backlog.
- [ ] **Phase 48: COBS Evaluation + Post-RCA Cleanup + Milestone Close** — Evaluate COBS framing on the serial data path (adopt/defer/reject decision); lift `eprom_operations.py` mypy strict overrides; close milestone with documentation and branch promotion.

## Phase Details

### Phase 44: Bug A RCA — Modified Rev 0 Upper-Address Jitter

> **★ RE-GROUNDED 2026-06-01 (RCA achieved).** The 2026-06-01 bench session
> **disproved the upper-address premise** and proved a stronger result: Bug A is a
> **Rev 0 (Modified Rev 0) shield read-path fault** — broad, ~uniform read jitter
> (not A15-specific), **causally controlled by the read-strobe knob** (longer
> strobe → ~6.5× worse; mechanism = charge-leakage / weak data-bus pulldown; fix
> direction = shorter strobe, handed to Phase 46). Isolated to the shield via a 2×2
> controller×shield crossover (chips + controllers exonerated). This **meets the
> governing D-07 causal-only success bar** (a knob that controls the jitter).
> Plans 04/05 as-written (Modified-Rev-0-on-Leonardo baseline + upper-address 2D/LA
> sweep) are **superseded**. Canonical RCA: `evidence/44-RCA-FINDINGS.md`.
> Adjacent findings (out of scope, logged): VPP hardware healthy (Uno R1 miscal
> fixed); **write/program stalls on both controllers** (`evidence/.../WRITE-STALL.md`
> — recommend a separate `/gsd-debug`).

**Goal**: The Modified Rev 0 A15=1 upper-address jitter is proven to a specific signal-integrity mechanism (ringing, crosstalk, settling-time violation, or other), with scope traces and/or circuit analysis as evidence — going beyond the Phase 29 v2 symptom characterization (1.86× skew, 63% bit-raise). *(Re-grounded: mechanism proven is a Rev 0-shield read-path fault, causally controlled by read-strobe timing — see re-grounding note above.)*
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
- [x] 44-03-PLAN.md — Wave 2: host knob params + CLI options + Wave 0 pytest + 2D sweep harness

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 44-04-PLAN.md — Wave 3 (bench): *superseded* — static check done (readings uncaptured); baseline misattributed to a Rev 2.0 board & relocated. Goal served by the isolation experiment (Bug A reproduced + isolated to Rev 0 shield). See 44-04-SUMMARY.md.

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 44-05-PLAN.md — Wave 4 (bench): *goal achieved, method changed* — knob check proved causal coupling (D-06; longer strobe → 6.5× worse), 2×2 crossover isolated the fault to the Rev 0 shield, RCA findings written, per-rev map started (RCA-03 partial). Full 2D grid + LA capture deferred (not needed for the mechanism). See 44-05-SUMMARY.md.

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

**Plans**: 3 plans
Plans:
**Wave 1** *(parallel — no file overlap)*

- [x] 48-01-PLAN.md — COBS-01: from-scratch lightweight-framing survey -> `.planning/v1.9-COBS-DECISION.md` (ADR, REJECT-libraries/DEFER-concept). UNGATED — decidable now.
- [ ] 48-02-PLAN.md — TYPE-01: lift `eprom_operations.py` mypy strict ring-fence (strict-island move + ~53 behavior-preserving fixes + watermark). HARD-GATED on Phase 46.

**Wave 2** *(milestone close — depends on 48-01 + 48-02; gated on Phases 46/47)*

- [ ] 48-03-PLAN.md — MILESTONES.md v1.9 entry + coordinated lockstep `3.0.0b8` beta tag (sub-repos->beta, meta->main; no stable 3.0.1). Operator-gated promotion checkpoint.

## v1.11 — Complete infoic.xml Decode & Database Correctness (SHIPPED 2026-06-10)

<details>
<summary>✅ v1.11 shipped — host-only decode correctness: source-grounded field dictionary + corrected <code>build_db.py</code> (4 bugs), principled <code>resolve_pinout_key</code>, 9× 24-pin EEPROM unblock, VPP-safety + per-chip diff gates, display layer reflects <code>electrical.type</code>. 6 phases (56–61), 14 plans, 15/15 reqs; audit PASSED. Full detail in <code>.planning/MILESTONES.md</code> §v1.11 + <code>.planning/milestones/v1.11-ROADMAP.md</code>.</summary>

**Milestone goal:** Authoritatively decode every Firestarter-relevant field in minipro's `infoic.xml` — grounded in the minipro C source — and rebuild the database decode so every DIP parallel memory the RURP shield can physically drive is correctly classified, with an authoritative field-dictionary reference and a correctness/regression gate. HOST-ONLY milestone (`firestarter_app` data pipeline + docs); firmware sub-repo untouched like v1.8.

**Phase numbering:** Continues from v1.10 last phase 55 → v1.11 starts at **Phase 56**.

### Phases

- [x] **Phase 56: Snapshot + Field Dictionary + Corrected Docs** — Pin the infoic.xml snapshot; produce authoritative source-grounded field dictionary; deliver corrected `protocol-id.md` / `protocol-flags.md` / `package-details.md`. (completed 2026-06-08)
- [x] **Phase 57: Decode Bug Fixes + PROTOCOL_MAP + check_dispatch Extension** — Fix confirmed decode bugs (BUG-1..4: `interpret_timing` ×100, VCC nibbles, vdd/vcc swap, PROTOCOL_MAP names); extend `check_dispatch.py` to full-class VPP safety guard before any re-derivation changes land. (completed 2026-06-08)
- [x] **Phase 58: Pinout Re-derivation + 24-pin EEPROM Unblock** — Re-derive `resolve_pinout_key` from principled `(pin_count, proto_id, mem_size)` rules; add `DIP24_6116` EEPROM pinout; unblock the 9 AT28C04/AT28C16 chips; SR-1 safety checklist. (completed 2026-06-09)
- [x] **Phase 59: Correctness Gate + Per-chip Diff + SRAM Audit** — Regenerate DB; produce and review per-chip diff vs pinned baseline; `configure_sram` NVRAM/WP# behavior audit + documentation. (completed 2026-06-09)
- [x] **Phase 60: Display-Layer Decode Correctness (`info` reflects electrical.type)** — Make `ic_layout.py` derive the displayed chip Type and "Can be erased" from the DB's `electrical.type`/`flags` (decode ground truth) instead of keying solely on `protocol_id`, so the EEPROMs reclassified in the Phase 59 follow-up (`cca7d62`: W27C512, SST27VF512, SST27SF512, W27C257, …) display correctly in `firestarter info` and genuine UV-EPROMs do not regress. Host-only; firmware electrical-erase support is a separate firmware backlog item. (completed 2026-06-10)
- [x] **Phase 61: List/Search Display Correctness + Table Layout** — Route the `firestarter list` / search table Type & VPP columns through `electrical.type` (parity with `info`; resolves the Phase 60 IN-01 divergence, incl. no spurious SRAM VPP), and size the table so it fits all columns without breaking and is never narrower than today's default width. Host-only (`eprom_info.py` `print_eprom_list_table`). (completed 2026-06-10)

## Phase Details

### Phase 56: Snapshot + Field Dictionary + Corrected Docs

**Goal**: The decode pipeline has an immutable source-of-truth anchor and every Firestarter-relevant `infoic.xml` attribute is documented with an authoritative, minipro-source-cited meaning.
**Depends on**: Nothing (first phase — lays the foundation everything else requires).
**Requirements**: DEC-01, DEC-03, DEC-04, DEC-05, DOC-01, DOC-02, DOC-03, GATE-01
**Success Criteria** (what must be TRUE):

  1. A specific upstream `infoic.xml` commit is pinned and committed in-repo (or an equivalent immutable local copy); all subsequent DB regenerations in this milestone reference that snapshot, not a live URL fetch.
  2. A field-dictionary reference (as annotated constants in `build_db.py` or a companion file) documents every attribute in scope — `package_details`, `type`, `variant`, `protocol_id`, `flags`, `voltages`, `pin_map`, `pulse_delay`, `chip_id`, `code_memory_size`, `page_size`, `chip_info`, `blank_value` — each entry marked CONFIRMED / INFERRED / UNKNOWN with a minipro-source citation.
  3. `firestarter_app/doc/protocol-id.md` shows canonical `IC2_ALG_*` names, the `0x39` error is fixed, and infeasible/non-memory IDs (`0x2A`/`0x2C`/`0x2E` GAL/PIC/MCU, `0x35` ITE, `0x11` FWH) carry explicit exclusion rationales.
  4. `firestarter_app/doc/protocol-flags.md` carries corrected canonical protocol names and the flag-bit interpretation fix (bit 4 = `can_erase`, not "requires write-enable sequence").
  5. `firestarter_app/doc/package-details.md` is re-titled to describe `flags`, bit meanings are source-grounded, and inferred bits (3/6/7) are explicitly marked not-source-confirmed.

**Plans**: 3 plans
**Wave 1**

  - [x] 56-01-PLAN.md — Commit pre-milestone baseline snapshot of chip_database.json (GATE-01)

**Wave 2** *(blocked on Wave 1 completion)*

  - [x] 56-02-PLAN.md — Author infoic-field-dictionary.md: 13 attributes, citation SHA, BUG-1..4 semantics (DEC-01/03/04/05)

**Wave 3** *(blocked on Wave 2 completion)*

  - [x] 56-03-PLAN.md — Rewrite protocol-id/protocol-flags/package-details docs + regression gate (DOC-01/02/03)

**UI hint**: no

### Phase 57: Decode Bug Fixes + PROTOCOL_MAP + check_dispatch Extension

**Goal**: All four confirmed decode bugs are fixed in `build_db.py` and the VPP-safety guard in `check_dispatch.py` covers the full chip set — not just the previously-audited `DIP28_2764` pinout — so no future re-derivation change can introduce an evasive VPP-routing regression.
**Depends on**: Phase 56 (field dictionary provides source-grounded authority for each fix; bug fixes must reference the dictionary, not re-invent the lookup).
**Requirements**: DEC-02, DEC-03, DEC-04, DEC-05, GATE-03
**Success Criteria** (what must be TRUE):

  1. `firestarter info W27C512` (or equivalent DB query) reports `pulse_duration` as 100 µs, not 10000 µs — confirming the `interpret_timing` ×100 multiplier for protocols 0x07/0x0B is removed.
  2. `VCC_VOLTAGES` in `build_db.py` includes entries for nibble `0x02` (4V) and `0x03` (4.5V); AT28C256/AT28C64-class chips that previously defaulted to 5V now decode their correct VCC.
  3. `vcc` (bits 11-8) and `vdd` (bits 15-12) field names match the minipro source bit-field layout (the swap is corrected).
  4. `PROTOCOL_MAP` uses only canonical `IC2_ALG_*` names; entries for `0x2A`/`0x2C`/`0x2E`/`0x35`/`0x3C` are removed or carry explicit exclusion comments; phantom `0x39` is documented.
  5. `check_dispatch.py` asserts that no chip whose `electrical.type == "Flash/EEPROM"` (a 5V part) routes to a VPP-asserting path (`configure_eprom`) — not just the `DIP28_2764` case — and exits clean (0 violations) across the full chip set. *(Corrected 2026-06-08, Phase 57 code-review CR-01: the original phrasing keyed the guard on "algorithm in `{0x05,0x06,0x0D}`", but `dispatch()` never routes those protocols to `configure_eprom`, so that predicate was dead code. The guard now keys on `electrical.type`, which is pinout/algorithm-agnostic and genuinely enforces the Goal's intent — a true superset of the WARNING-5 check. See commit `ffa74b6` and `57-REVIEW.md`.)*

**Plans**: 3 plans
Plans:
**Wave 1** *(parallel — no file overlap)*

  - [x] 57-01-PLAN.md — Fix the 4 decode bugs in build_db.py: interpret_timing ×100 (DEC-03), VCC nibbles + vcc/vdd swap (DEC-04), PROTOCOL_MAP/KNOWN_PROTOCOLS canonicalize (DEC-05); DEC-02 umbrella
  - [x] 57-02-PLAN.md — Extend check_dispatch.py to a full-class vpp-pin + {0x05,0x06,0x0D} VPP-safety guard (GATE-03) + sync 0x35/0x39 removal (DEC-05)

**Wave 2** *(blocked on Wave 1 completion)*

  - [x] 57-03-PLAN.md — Regenerate chip_database.json + baseline diff (DEC-02/03/04) + GATE-03 on regenerated set + snapshot refresh + full suite; blocking human-verify of firestarter info W27C512

**UI hint**: no

### Phase 58: Pinout Re-derivation + 24-pin EEPROM Unblock

**Goal**: `resolve_pinout_key` is rebuilt on principled, minipro-source-grounded rules; the survey-built guess tables are retired; the 9 blocked 24-pin EEPROMs are exposed safely via the correct pinout and handler with a completed SR-1 safety review.
**Depends on**: Phase 57 (corrected field values — voltages, flags, protocol — are prerequisites for principled `resolve_pinout_key` rules; GATE-03 guard must be in place before expansion changes land).
**Requirements**: PIN-01, PIN-02, PIN-03
**Success Criteria** (what must be TRUE):

  1. `PIN_MAP_TO_PINOUT`, `PIN_MAP_PROTO_TO_PINOUT`, and `DIP28_VARIANT_MAP` guess tables are replaced (or fully superseded) by a `resolve_pinout_key` function whose dispatch is grounded in `(pin_count, proto_id, mem_size)` with each case citing a minipro source reference or a datasheer-confirmed pinout — no "one-rom verified" evidence-free entries remain.
  2. The three load-bearing safety overrides are intact and verified: WARNING-5 (`DIP28_2764` + 0x07 + Flash/EEPROM → 0x0D), fm1608 (`type=4` + EPROM-family → 0x28), and 24-pin EEPROM skip semantics — `check_dispatch.py` returns 0 violations after the re-derivation.
  3. The 9 AT28C04/AT28C16-family chips appear in the regenerated `chip_database.json` with `algorithm=0x0D` and `pinout=DIP24_6116` (or equivalent); `firestarter info AT28C16` (or any family member) returns a valid entry rather than "chip not found".
  4. The SR-1 safety checklist is completed for the `DIP24_6116` pinout: `vpp-pin` absent (no VPP on any 5V EEPROM pin), `rw-pin` matches the datasheet WE pin, `oe-pin`/`ce-pin` correct; all 24 DIP pins accounted for.

**Plans**: 3 plans (1 Wave-0 + 2 execute)
**Wave 1**

- [x] 58-01-PLAN.md — Wave 0: DIP24_2816 pinout entry + five test-first Wave 0 classes (PIN-01/02/03)
- [x] 58-02-PLAN.md — Principled resolve_pinout_key rewrite, guess-table deletion, overrides-as-rules, D-06 fail-safe, DB regen (PIN-01/02/03)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 58-03-PLAN.md — GATE-03 0-violation proof + CLI reachability + two-layer SR-1 safety review (PIN-02/03)

Note: D-07 supersedes SC#3/#4's `DIP24_6116` reference with a dedicated `DIP24_2816` entry (electrically identical, named as a 5V EEPROM for SR-1 traceability).
**UI hint**: no

### Phase 59: Correctness Gate + Per-chip Diff + SRAM Audit

**Goal**: The regenerated `chip_database.json` is reviewed against the pre-milestone baseline chip by chip; every change is explained and intentional; the `configure_sram` NVRAM behavior is documented; the correctness gate is fully green.
**Depends on**: Phase 57 (decode bugs fixed), Phase 58 (pinout re-derivation + 24-pin EEPROM exposure complete).
**Requirements**: GATE-02, GATE-04
**Success Criteria** (what must be TRUE):

  1. A per-chip diff of the regenerated `chip_database.json` against the pre-milestone baseline is produced (script or manual `jq` comparison); every chip whose `algorithm`, `pinout`, `vpp_mv`, `pulse_duration`, or `electrical.type` changed is listed with an explicit, documented rationale — no unexplained diffs remain.
  2. `check_dispatch.py` exits clean (0 errors) across the full regenerated chip set, including the newly-added 24-pin EEPROMs — confirming every chip dispatches to its intended handler via the wire round-trip.
  3. `configure_sram`'s NVRAM/SRAM behavior is documented: blank-check limitation (NVRAM is never factory-blank), WP# pin behavior for representative families (DS1225/M48T08 class), and the RTC-oscillator side effect for timekeepers — published as a comment block in `sram.cpp` or a `doc/sram-nvram-behavior.md` note. If a real safety issue is found during the audit, it is escalated as a firmware backlog item (not silently dismissed).
  4. Regenerating `chip_database.json` from the pinned `infoic.xml` snapshot produces a byte-identical result across two independent runs (pipeline determinism preserved; no runtime upstream fetch).

**Plans**: 2 plans (2 waves collapse to 1 — independent workstreams)
Plans:
**Wave 1** *(parallel — no file overlap)*

  - [x] 59-01-PLAN.md — GATE-02 correctness gate: sort_keys determinism (SC#4) + GATE-03 re-confirm (SC#2) + diff_db.py grouped-by-cause full-record diff with D-03 BLOCK
  - [x] 59-02-PLAN.md — GATE-04 SRAM/NVRAM audit: two-layer docs (59-SRAM-AUDIT.md + doc/sram-nvram-behavior.md), no firmware escalation

**UI hint**: no

### v1.11 Coverage

| Requirement | Phase | Status |
|-------------|-------|--------|
| DEC-01 | Phase 56 | Complete (56-02) |
| DEC-02 | Phase 57 | Complete (57-01/02/03) |
| DEC-03 | Phase 56 + Phase 57 | Complete (56-02, 57-01/03, debug 8088141) |
| DEC-04 | Phase 56 + Phase 57 | Complete (57-01/03) |
| DEC-05 | Phase 56 + Phase 57 | Complete (57-01/02) |
| PIN-01 | Phase 58 | Complete (58-01/02) |
| PIN-02 | Phase 58 | Complete (58-02) |
| PIN-03 | Phase 58 | Complete (58-02/03) |
| DOC-01 | Phase 56 | Complete (56-03) |
| DOC-02 | Phase 56 | Complete (56-03) |
| DOC-03 | Phase 56 | Complete (56-03) |
| GATE-01 | Phase 56 | Complete (56-01) |
| GATE-02 | Phase 59 | Complete (59-01, CR-01 fix f3b2ed7) |
| GATE-03 | Phase 57 | Complete (57-02/03) |
| GATE-04 | Phase 59 | Complete (59-02) |

**Mapped: 15/15 requirements ✓** — no orphans, no duplicates.

Note: DEC-03, DEC-04, DEC-05 span Phases 56 and 57. The field dictionary work (the authoritative source-grounded decode of timing/voltage/PROTOCOL_MAP) is Phase 56; the corrected `build_db.py` code implementing those fixes is Phase 57. Each requirement maps to the phase that delivers the primary artifact.

### Phase 60: Display-Layer Decode Correctness (`info` reflects electrical.type)

**Goal**: `firestarter info` and the operator-facing presentation layer derive the displayed chip **Type** label and **"Can be erased"** status from the database's `electrical.type` (and `flags`) — the decode ground truth produced by `build_db.py` — rather than keying solely on `protocol_id`. The electrically-erasable parts reclassified in the Phase 59 follow-up `cca7d62` (W27C512, SST27VF512, SST27SF512, W27C257, and the wider CMOS-EEPROM / SST SuperFlash family) display as EEPROM with correct erasability; genuine UV-EPROMs continue to display as UV-EPROM. HOST-ONLY — firmware electrical-erase support (so `firestarter erase W27C512` actually works) is a **separate firmware backlog item**, not this phase.

**Depends on**: Phase 59 (the `electrical.type` re-derivation in `build_db.py` / `cca7d62` is the field the display must now read).

**Requirements**: Decode-display follow-up — extends the already-validated DEC-01..05 decode to the presentation layer (`firestarter info`). No new requirement ID is minted; this surfaces decode that is already correct in the DB but invisible to the operator. (The 15/15 v1.11 requirement mapping above is unchanged.)

**Success Criteria** (what must be TRUE):

  1. `firestarter info W27C512` (and `SST27VF512`, `SST27SF512`, `W27C257`) shows a Type label indicating an electrically-erasable EEPROM (not "UV-EPROM / MTP-Flash"), sourced from the DB record's `electrical.type`.
  2. The "Can be erased" line is consistent with `electrical.type`/`flags` and does NOT mislead: it distinguishes "electrically erasable (chip-erase)" from firmware-erase-command availability — i.e., it must not imply `firestarter erase` works for the 0x07 path while the firmware lacks that command (that gap is referenced as a backlog item, not silently implied).
  3. Genuine UV-EPROMs (control set, e.g. `M27C512`, `27C256`, `M2764`) still display as UV-EPROM — no regression.
  4. `ic_layout.py`'s `get_chip_type_string` and can-erase derivation read `electrical.type`/`flags` (the protocol label may remain as supplementary detail, not the sole source of truth).
  5. Existing tests green + `ruff` clean; new/updated presenter tests cover the EEPROM-display case and the UV-EPROM control case.

**Plans**: 2 plans
Plans:
**Wave 1**

- [x] 60-01-PLAN.md — Six atomic display-decode edits (D-01/02/03/05/07) in ic_layout.py + database.py; synthetic + real-DB smoke tests

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 60-02-PLAN.md — Regenerate test_info_known_chip snapshot (EEPROM canary) + phase gate

**UI hint**: no (terminal text presentation only).

</details>

## v1.12 — Firmware Protocol Dispatch Hardening + Skeletons (STARTED 2026-06-10)

**Milestone goal:** Make the **whole stack honest about what it can and cannot program** — (a) firmware fail-closed dispatch with an explicit "not implemented" response the host surfaces cleanly + skeleton infeasibility-rejection markers, and (b) a capability-honest database that *lists* the DIP parallel-memory chips RURP cannot fully support (instead of silently dropping them) with a `supported: false` flag the host reports clearly. **Framework + honest reporting only; no new per-protocol programming logic and no new chips become programmable.** Dual-repo lockstep wire change; provable on the native dispatch harness + host pytest (no bench required to close).

Research finding: the SKELETON-NEEDED bucket is empty (every RURP-feasible protocol already has a handler); the value is the **fail-closed safety framework + honest reporting**. The DB work (Phases 66–68) is HOST-ONLY like v1.11.

**Phase numbering:** Continues from v1.11 last phase 61 → v1.12 starts at **Phase 62**.
**Branch model:** `v1.12-protocol-dispatch-hardening` off `beta` in all three repos; merge back to `beta`; stable promotion operator-gated.

### Phases

- [x] **Phase 62: Dispatch Baseline Capture + check_dispatch Update** — Capture a pre-change dispatch baseline (native test + `check_dispatch.py` scan on fallback-present state) before any firmware modification; reconcile the pre-existing `0x35`/`0x39` dispatch-mirror gap; add the `not_implemented` arm + FAIL guard to `check_dispatch.py`. Gate is green before Phase 64 touches any firmware code. (completed 2026-06-10)
- [x] **Phase 63: Catalog Lockstep Wire Change** — Add `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` to the meta-repo canonical `messages.toml`; sync to both sub-repos; regenerate `messages.h` + `messages.py` with Python 3.11; codegen drift gate green in both repos. Zero behavior change — reviewable in isolation. (completed 2026-06-11)
- [x] **Phase 64: Firmware Fail-Closed Dispatch + Native Tests** — `configure_not_implemented()` in `not_implemented.cpp`; `protocol != 0` guard in `configure_memory()`; named infeasibility arms for `0x11`/`0x2A`/`0x2B`/`0x2C`; firmware emits `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` with protocol value; native Unity tests prove fail-closed + legacy fallback intact + NULL operation pointers; Leonardo flash gate ≤ 90%. (completed 2026-06-11)
- [x] **Phase 65: Host Graceful Handling** — `ProtocolNotImplementedError(EpromOperationError)` in `exceptions.py`; detection in `_run_state_machine`; clear actionable CLI message in `map_typed_errors`; pytest tests covering the new exception path; CI green. (completed 2026-06-11)
- [ ] **Phase 66: DB Inclusion + VPP Correction + Dispatch Gate** — `build_db.py` includes DIP parallel-memory chips with unknown/unimplemented `protocol_id` marked `support_status: protocol-not-implemented`; NMOS high-VPP family (M2716/M2732 = 25V, M2732A = 21V) gets true VPP recorded with `support_status` derived from RURP ceiling (~22V); `check_dispatch.py` + per-chip diff gate treat non-`supported` entries as non-dispatchable; gate green. HOST-ONLY.
- [ ] **Phase 67: Pinout Classification for Unclassifiable DIP Chips** — Extend Phase 58 `resolve_pinout_key` rules to cover DIP chips `build_db.py` currently cannot classify; genuinely unmappable chips included as `support_status: adapter-required` with adapter note; no DIP parallel chip dropped for pinout reasons. HOST-ONLY.
- [ ] **Phase 68: Host Capability Reporting** — `firestarter info` shows `support_status` + reason for non-`supported` chips; `firestarter write` / `read` / `verify` on a non-`supported` chip prints a status-specific message ("protocol not implemented" / "adapter required: <note>" / "VPP <x>V exceeds programmer max") and does NOT attempt the hardware operation; pytest tests cover all three statuses; CI green.

## Phase Details

### Phase 62: Dispatch Baseline Capture + check_dispatch Update

**Goal**: A committed, verifiable snapshot of current dispatch behavior exists before any code changes land, and `check_dispatch.py` models the new fail-closed firmware dispatch so the regression gate is accurate for all subsequent phases.
**Depends on**: Nothing (first phase — foundational prerequisite for Phase 64).
**Requirements**: GATE-01, GATE-02
**Success Criteria** (what must be TRUE):

  1. A native Unity test (or equivalent committed artifact) asserts the current `(protocol=0, mem_type=1)` behavior routes to `configure_eprom` — pinning the legacy fallback behavior as a regression baseline before any guard is added.
  2. `check_dispatch.py`'s `dispatch()` function has explicit cases for protocols `0x35` and `0x39` (not relying on the mem_type coincidental fallback), plus a `protocol != 0` → `"not_implemented"` arm replacing the stale fallback; `0x35`/`0x39` chips continue to resolve to `configure_flash4`.
  3. A `not_implemented` list + FAIL assertion is present in the `check_dispatch.py` scan loop; running `python tools/check_dispatch.py` against the current 743-chip DB exits with `0 not-implemented chips` (PASS — because no DB chip uses a gap protocol).
  4. All pre-existing `check_dispatch.py` checks remain green (GATE-03 VPP-safety guard, SRAM-in-EPROM guard, wire round-trip 743/743 PASS).

**Plans**: 3 plans
Plans:
**Wave 1**

- [x] 62-01-PLAN.md — Fork v1.12-protocol-dispatch-hardening (off beta) + Wave 0 failing TestDispatchGate02 tests (GATE-02)

**Wave 2** *(blocked on Wave 1)*

- [x] 62-02-PLAN.md — Pre-edit dispatch baseline snapshot: 743-chip dispatch triples -> tools/baseline/dispatch_baseline.json (GATE-01)

**Wave 3** *(blocked on Wave 2 — snapshot must be pre-edit)*

- [x] 62-03-PLAN.md — check_dispatch.py edits: 0x35/0x39 explicit case + protocol!=0 not_implemented arm + main() FAIL bucket; gate green (GATE-02)

**UI hint**: no

### Phase 63: Catalog Lockstep Wire Change

**Goal**: `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` exists in both sub-repos' generated constant files, the codegen drift gate is green in both repos, and neither sub-repo has any code that references the new constant yet — so the catalog commit is self-contained and reviewable in isolation.
**Depends on**: Phase 62 (baseline captured; no dependency on output, but sequenced to keep the Phase 63 commit clearly atomic and reviewable).
**Requirements**: WIRE-01
**Success Criteria** (what must be TRUE):

  1. `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` appears in the meta-repo canonical `messages.toml`, the firmware sub-repo's synced `messages.toml`, and both generated outputs (`firestarter/include/messages.h` and `firestarter_app/firestarter/messages.py`).
  2. Codegen was run with Python 3.11 (CI-matching version); both sub-repo drift gates (`codegen + git diff --exit-code`) report no drift when run with the CI Python version.
  3. Neither `memory.cpp` nor any host file yet references the new constant — this commit introduces only the catalog definition, no call sites.
  4. The new message ID `0xBB` does not collide with any existing catalog entry; the ERROR band sequence is intact.

**Plans**: 1 plan
**UI hint**: no
Plans:

- [x] 63-01-PLAN.md — add MSG_ERR_PROTOCOL_NOT_IMPLEMENTED 0xBB to canonical messages.toml, sync + regenerate both sub-repos under py3.11, lockstep commit (WIRE-01)

### Phase 64: Firmware Fail-Closed Dispatch + Native Tests

**Goal**: The firmware no longer routes any non-zero unimplemented protocol to `configure_eprom` via the `mem_type` fallback; every unimplemented non-zero protocol receives an explicit `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` response with zero hardware side effects; native tests prove the new dispatch invariants; both boards fit within their flash ceilings.
**Depends on**: Phase 62 (baseline test pinned; `check_dispatch.py` updated — gate is accurate before firmware changes), Phase 63 (catalog constant defined in `messages.h` before firmware code references it).
**Requirements**: DISP-01, DISP-02, DISP-03, DISP-04, WIRE-02, TEST-01, TEST-02
**Success Criteria** (what must be TRUE):

  1. `configure_memory()` with a non-zero unknown protocol (e.g. `protocol=0x99`) returns `RESPONSE_CODE_ERROR` and emits `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` — confirmed by a native Unity dispatch test; no VPP regulator enable occurs.
  2. `configure_memory()` with `protocol=0` and `mem_type=1` still routes to `configure_eprom` — the legacy fallback is intact behind the `protocol == 0` guard, confirmed by the pre-existing regression test from Phase 62.
  3. `configure_not_implemented()` leaves all three operation pointers (`firestarter_operation_init`, `firestarter_operation_main`, `firestarter_operation_end`) NULL — confirmed by a native Unity test asserting NULL pointers after dispatch.
  4. Protocols `0x11`, `0x2A`, `0x2B`, and `0x2C` are explicitly recognized in the dispatch chain (named infeasibility arms) and route to `configure_not_implemented()` — confirmed by individual native Unity tests for each.
  5. `pio run -e leonardo` reports ≤ 90% flash utilization after all changes; all pre-existing native Unity tests remain green.

**Plans**: 2 plans
**Wave 1**

- [x] 64-01-PLAN.md — create self-contained configure_not_implemented handler + wire named arms (0x11/0x2A/0x2B/0x2C) and generic protocol!=0 fail-closed guard into configure_memory before the protocol==0 mem_type fallback; update CLAUDE.md dispatch table (DISP-01..04, WIRE-02)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 64-02-PLAN.md — native Unity suite (test_not_implemented.cpp) proving 0x99/named-arms -> ERROR+NULL pointers and protocol==0 fallback intact, all pre-existing dispatch tests green; flash-budget gate Leonardo <= 90% / Uno clean (TEST-01, TEST-02)

**UI hint**: no

### Phase 65: Host Graceful Handling

**Goal**: When the firmware reports `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`, the host raises a typed `ProtocolNotImplementedError` (not a generic `EpromOperationError`) and the CLI prints a clear, actionable message including the protocol value — distinguishable from generic operation failures.
**Depends on**: Phase 63 (catalog constant in `messages.py`), Phase 64 (firmware emits the new message ID — functional prerequisite; pytest tests may use mocked responses and can be developed in parallel with Phase 64 but must not merge until Phase 64 is committed).
**Requirements**: HOST-01, HOST-02
**Success Criteria** (what must be TRUE):

  1. `ProtocolNotImplementedError` is a subclass of `EpromOperationError` in `exceptions.py`; existing callers catching `EpromOperationError` continue to work without modification.
  2. `_run_state_machine` in `eprom_operations.py` raises `ProtocolNotImplementedError` when an ERROR response contains "not implemented" text — verified by a pytest test using a mocked ERROR response with the catalog format string.
  3. Running `firestarter write <chip-with-unimplemented-protocol>` (or equivalent mocked invocation) prints an actionable error message that includes the protocol value (e.g. `Protocol 0x0000000B not implemented`) and communicates that this is a known but not-yet-supported protocol — not a generic "operation failed" message.
  4. The `ProtocolNotImplementedError` catch in `map_typed_errors` appears before the `EpromOperationError` catch so the subclass is handled first; all pre-existing error paths remain green.

**Plans**: 2 plans

Plans:

- [x] 65-01-PLAN.md — add ProtocolNotImplementedError(EpromOperationError) + thread decoded message id through Response, centralize id-0xBB -> typed-raise dispatch (_raise_for_error_response) in the state-machine ERROR path, add the actionable "Unsupported protocol:" arm before the EpromOperationError arm in map_typed_errors, and pytest the 4 SC cases (HOST-01, HOST-02)
- [x] 65-02-PLAN.md — GAP-CLOSURE: wire the probe/connect boundary so the 0xBB ERROR frame reaches the CLI (Option B: expect_ack raises ProtocolNotImplementedError, _probe_port + find_and_connect propagate it instead of masking it as ProgrammerNotFoundError); close WR-02 (route _main_phase_read_data/_main_phase_send_data through _raise_for_error_response); add a production-path integration test driving the REAL find_and_connect path (HOST-01, HOST-02)

**UI hint**: no

### Phase 66: DB Inclusion + VPP Correction + Dispatch Gate

**Goal**: `build_db.py` includes every DIP parallel-memory chip that passes the serial/SMD/MCU/PLD filter, regardless of whether its `protocol_id` is implemented — chips with unknown/unimplemented protocols are included marked `support_status: protocol-not-implemented`; the authoritatively-known high-VPP NMOS family (Intel M2716/M2732 = 25V, M2732A = 21V) has its true VPP recorded (not the upstream-truncated 18V), with `support_status` derived from the RURP VPP ceiling (~22V: >ceiling -> `vpp-exceeds-max`, within range -> `supported` at corrected voltage); `check_dispatch.py` and the per-chip diff gate are updated to treat any non-`supported` entry as non-dispatchable. HOST-ONLY — no firmware change.
**Depends on**: Phase 65 (host error-surface foundation in place; logically independent but sequenced after the firmware dispatch story is complete before the DB capability story begins).
**Requirements**: DB-01, DB-03, DB-05
**Success Criteria** (what must be TRUE):

  1. DIP parallel-memory chips previously silently dropped due to an unknown/unimplemented `protocol_id` appear in the regenerated `chip_database.json` with `support_status: protocol-not-implemented` — confirmed by inspecting the `build_db.py` output diff. Serial / GAL-PLD / MCU / SMD-only chips remain absent (unchanged skip logic).
  2. The authoritatively-known NMOS M2716, M2732, and M2732A entries (and their documented equivalents) carry the true VPP (25V or 21V respectively) rather than the upstream-truncated 18V; M2716 and M2732 appear as `support_status: vpp-exceeds-max` (true VPP > ~22V RURP ceiling); any NMOS variant with corrected VPP within the ceiling appears as `support_status: supported` at the corrected voltage. NMOS-vs-CMOS alias splitting is resolved at plan time.
  3. `check_dispatch.py` exits clean (0 errors) across the full regenerated DB: entries with any non-`supported` `support_status` do NOT resolve to a programming handler (they produce a `not_supported` outcome); the pre-existing GATE-03 VPP-safety guard and wire round-trip checks remain green.
  4. A per-chip diff (via `diff_db.py` or equivalent) accounts for every new or changed entry — additions carry a documented rationale (`protocol-not-implemented` or `vpp-exceeds-max` / corrected-VPP) and no unexplained diffs appear.

**Plans**: 3 plans
Plans:
**Wave 1** *(parallel — no file overlap)*

- [x] 66-01-PLAN.md — Wave 0: cherry-pick diff_db.py + pin 734-chip chip_database.baseline.json + RULE_PHASE66 rationale/field-paths/classify arm + RED tests/test_build_db_inclusion.py (DB-05)
- [x] 66-02-PLAN.md — check_dispatch.py rework: not_implemented FAIL-only-if-supported (D-10) + 3 consistency assertions; dispatch() memory.cpp mirror preserved; gate green on current DB (DB-05)

**Wave 2** *(blocked on 66-01 + 66-02)*

- [ ] 66-03-PLAN.md — build_db.py inclusion gates (0x34 include / 9 EEPROMs adapter-required) + NMOS VPP dict + RURP_VPP_CEILING_MV=22000 + support_status on every chip; regen DB to 744 under py3.11; check_dispatch + diff_db + 7 inclusion tests + full suite green; regen dispatch_baseline (D-11) (DB-01, DB-03, DB-05)

**UI hint**: no

### Phase 67: Pinout Classification for Unclassifiable DIP Chips

**Goal**: Every DIP parallel-memory chip whose pinout `build_db.py` currently cannot classify receives a principled best-effort mapping — extending the Phase 58 `resolve_pinout_key` rules with any additional `(pin_count, proto_id, mem_size)` cases needed; only chips that genuinely cannot be correctly wired to the RURP bus are included as `support_status: adapter-required` with a note on what adapter or mapping would be needed. No DIP parallel chip is dropped for pinout reasons. HOST-ONLY — no firmware change.
**Depends on**: Phase 66 (the DB inclusion pipeline and `support_status` taxonomy are in place; Phase 67 fills in the `adapter-required` cases within that framework).
**Requirements**: DB-02
**Success Criteria** (what must be TRUE):

  1. Every DIP 24/28/32-pin parallel-memory chip that previously triggered an unclassifiable-pinout warning in `build_db.py` is either (a) mapped to an existing RURP pinout via an extended `resolve_pinout_key` rule (with source citation or datasheet reference) and included as `support_status: supported` or `protocol-not-implemented`, or (b) included as `support_status: adapter-required` with a non-empty adapter note explaining what mapping would be required — no chip is silently dropped due to pinout classification failure.
  2. The extended `resolve_pinout_key` rules follow the same principled `(pin_count, proto_id, mem_size)` dispatch pattern established in Phase 58; each new rule cites a minipro source reference or a datasheet-confirmed pinout — no evidence-free guesses.
  3. `check_dispatch.py` exits clean (0 errors) after the pinout-classification changes: `adapter-required` entries do NOT resolve to a programming handler; all other updated entries dispatch correctly; the Phase 66 GATE-03 and VPP-safety guards remain green.
  4. A per-chip diff accounts for every chip whose `pinout` field changed or was newly assigned — each diff entry has a documented rationale, and no regression on chips that were already correctly classified in Phase 66.

**Plans**: TBD
**UI hint**: no

### Phase 68: Host Capability Reporting

**Goal**: The host uses the `support_status` field produced by Phases 66-67 to give the operator clear, honest feedback — `firestarter info` shows the `support_status` and reason for every non-`supported` chip; `firestarter write` / `read` / `verify` on a non-`supported` chip prints a clear, status-specific message ("protocol not implemented" / "adapter required: <note>" / "VPP <x>V exceeds programmer max") and does NOT attempt the hardware operation.
**Depends on**: Phase 67 (the full `support_status` taxonomy is populated in `chip_database.json` before the host reads and reports it); Phase 65 (`ProtocolNotImplementedError` + `map_typed_errors` error-surface established — Phase 68 extends the same display/error surface with capability-status-aware guard paths).
**Requirements**: DB-04
**Success Criteria** (what must be TRUE):

  1. `firestarter info <non-supported-chip>` (e.g. an NMOS M2716, a DIP chip with unknown protocol, or an adapter-required chip) displays the chip record with a clear support-status line sourced from the DB's `support_status` field — not a "chip not found" error and not a bare record with no capability indication. The displayed reason is status-specific: "protocol not implemented" / "adapter required: <note>" / "VPP <x>V exceeds programmer max" as appropriate.
  2. `firestarter write <non-supported-chip>` (and `read`, `verify`) prints a clear, actionable status-specific message and exits non-zero WITHOUT attempting any serial communication with the firmware — the guard fires entirely in the host before any command is sent.
  3. Supported chips are unaffected — `firestarter write W27C512` continues to work normally; no regression on the existing write/read/verify paths.
  4. pytest tests cover all three non-supported statuses (`protocol-not-implemented`, `adapter-required`, `vpp-exceeds-max`): a mock DB entry for each routes through the CLI and produces the expected status-specific message + exit code; all pre-existing tests remain green; CI passes.

**Plans**: TBD
**UI hint**: no

### v1.12 Coverage

| Requirement | Phase | Status |
|-------------|-------|--------|
| GATE-01 | Phase 62 | Pending |
| GATE-02 | Phase 62 | Pending |
| WIRE-01 | Phase 63 | Pending |
| DISP-01 | Phase 64 | Pending |
| DISP-02 | Phase 64 | Pending |
| DISP-03 | Phase 64 | Pending |
| DISP-04 | Phase 64 | Pending |
| WIRE-02 | Phase 64 | Pending |
| TEST-01 | Phase 64 | Pending |
| TEST-02 | Phase 64 | Pending |
| HOST-01 | Phase 65 | Pending |
| HOST-02 | Phase 65 | Pending |
| DB-01 | Phase 66 | Pending |
| DB-03 | Phase 66 | Pending |
| DB-05 | Phase 66 | Pending |
| DB-02 | Phase 67 | Pending |
| DB-04 | Phase 68 | Pending |

**Mapped: 17/17 requirements ✓** — no orphans, no duplicates.

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
| 49-55 (v1.10) | v1.10 | 27/27 | ✅ Shipped | 2026-06-07 |
| 44 | v1.9 | 3/5 | In Progress|  |
| 45 | v1.9 | 0/TBD | Not started | — |
| 46 | v1.9 | 0/TBD | Not started | — |
| 47 | v1.9 | 0/TBD | Not started | — |
| 48 (close) | v1.9 | 1/3 | In Progress|  |
| 56 | v1.11 | 3/3 | Complete   | 2026-06-08 |
| 57 | v1.11 | 3/3 | Complete    | 2026-06-08 |
| 58 | v1.11 | 3/3 | Complete    | 2026-06-09 |
| 59 | v1.11 | 2/2 | Complete    | 2026-06-09 |
| 60 | v1.11 | 2/2 | Complete    | 2026-06-10 |
| 61 (close) | v1.11 | 1/1 | ✅ Shipped   | 2026-06-10 |
| 62 | v1.12 | 3/3 | Complete    | 2026-06-10 |
| 63 | v1.12 | 1/1 | Complete    | 2026-06-11 |
| 64 | v1.12 | 2/2 | Complete    | 2026-06-11 |
| 65 | v1.12 | 2/2 | Complete    | 2026-06-11 |
| 66 | v1.12 | 2/3 | In Progress|  |
| 67 | v1.12 | 0/TBD | Not started | — |
| 68 (close) | v1.12 | 0/TBD | Not started | — |

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

**Plans:** 2/2 plans complete

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

## Backlog

### Phase 999.1: Firmware calibration-default propagation (CONFIG_VERSION gate) (BACKLOG)

**Goal:** [Captured for future planning] Make corrected R1/R2 calibration defaults reach already-calibrated boards. `rurp_validate_config` ([firestarter/src/rurp_config_utils.cpp:32-39](../firestarter/src/rurp_config_utils.cpp#L32-L39)) re-applies defaults only when `config->version != CONFIG_VERSION` ("VER06"); Phase 44 changed `VALUE_R1` 1000→270000 ([firestarter/include/rurp_shield.h:49](../firestarter/include/rurp_shield.h#L49)) without bumping `CONFIG_VERSION`, so VER06-calibrated boards silently keep a stale `r1` → wildly wrong VPP reading (true 12.2V reported as ~1.8V). Fix options: bump `CONFIG_VERSION` on any default change (resets all users' calibration — communicate), OR add a sanity-range guard rejecting implausible `r1`, OR a targeted `r1==1000` migration.
**Requirements:** TBD
**Plans:** 0 plans
**Origin:** Phase 54 UAT diagnosis — [`.planning/debug/firmware-vpp-misread.md`](debug/firmware-vpp-misread.md). Severity: major. Out of EVEN-01 scope.

Plans:

- [ ] TBD (promote with /gsd-review-backlog when ready)

### Phase 999.2: uno328pb + Rev 2.0 chip-PROGRAM brownout hang (bench/hardware) (BACKLOG)

**Goal:** [Captured for future planning] Investigate the deterministic chip-PROGRAM hang on the uno328pb + Rev 2.0 shield. Across 6 attempts (firmware reflash + chip reseat + random/zero payloads) the firmware stops responding the instant it drives program current at VPP 12.7V / VCC 5.3V (suspected VPP-regulator brownout under program load); host times out on the first block. The SAME firmware + W27C512 + R1=270000 calibration writes & verifies cleanly on the Leonardo (VPP 13.1V), proving the fault is uno328pb-board-specific — not firmware/EVEN-01. Needs bench investigation: VPP regulator level, VCC stability under program load, board power.
**Requirements:** TBD
**Plans:** 0 plans
**Origin:** Phase 54 UAT Test 2 (uno328pb). Severity: major. Out of EVEN-01 scope.

Plans:

- [ ] TBD (promote with /gsd-review-backlog when ready)

<!-- Phase 61 (List/Search Display Correctness + Table Layout) shipped as part of v1.11 on
     2026-06-10 — moved out of Backlog into the v1.11 milestone section above. Full detail in
     the v1.11 archive: .planning/milestones/v1.11-ROADMAP.md. -->

_Backlog items 999.1 / 999.2 are firmware bench-investigation items (Phase 54 UAT origin) — promote with `/gsd-review-backlog` when bench hardware is available._

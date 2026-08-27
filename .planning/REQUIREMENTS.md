# Requirements: Firestarter — v1.34 Pre-Merge Hardware Regression Validation

**Defined:** 2026-08-25
**Core Value:** Algorithm-first dispatch — the minipro `protocol_id` (`algorithm`) is the single
authoritative dispatch key end to end. v1.34 touches no product code unless the bench proves v1.33
broke something. **Prove on silicon that v1.33 changed nothing behavioural, before the merge.**

## Context binding every requirement below

v1.33 shipped **−2938 B flash / −13 B RAM** across `uno` / `uno328pb` / `leonardo` on a premise of
byte-level equivalence — heap allocator removed, 438 B 64-bit runtime dropped, `jsmntok_t` narrowed
8 → 6 B, `key_parsers[]` command-decode table rewritten, handle types narrowed. Backed by native
tests, golden traces and cold builds. **Run on no Arduino.** Three PRs open and unmerged:
[`prom#43`](https://github.com/henols/firestarter_prom/pull/43),
[`fw#56`](https://github.com/henols/firestarter/pull/56),
[`app#54`](https://github.com/henols/firestarter_app/pull/54).

**Control baseline** (the arm every v1.33 result is measured against) = the exact merge-bases the
v1.33 branches forked from: firmware **`8695ee5`**, host app **`6bfa645`**.

**The five cells** — Leonardo + Rev 2.0 is the intersection of both sweeps and runs once:

| Cell | Board | Shield |
|------|-------|--------|
| A1 | Uno (ATmega328P) | Rev 2.0 |
| A2 | uno328pb (ATmega328PB) | Rev 2.0 |
| A3/B2 | Leonardo (ATmega32U4) | Rev 2.0 |
| B1 | Leonardo | Modified Rev 0 |
| B3 | Leonardo | Rev 2.2 |

## v1 Requirements

### Rig & Method (RIG)

- [x] **RIG-01**: Operator can flash either named arm — control (fw `8695ee5`) or v1.33 (fw#56 head) — to any of the three AVR targets, with the flashed image confirmed by device read-back, so no cell can silently run the wrong firmware
- [x] **RIG-02**: Every cell run records, before any test step executes: board identity **by signature** (never by handshake), the port's `controller:` identity, the operator-declared shield revision, firmware build SHA, host app SHA, and chip part + package
- [x] **RIG-03**: One written per-cell procedure exists that both arms follow identically, so any A/B delta is attributable to the firmware and to nothing else
- [ ] **RIG-04**: The write→read→verify oracle is read-back SHA equality against the written image over the **full device size**, never an exit code; the v1.33 arm additionally carries a read-stability check of N=3 reads resolving to one SHA
- [ ] **RIG-05**: Any single cell can be re-run from the written record alone, without reconstructing context from the session that produced it

### Board Sweep — three boards on Rev 2.0 (BOARD)

- [ ] **BOARD-01**: Cell A1 (Uno / Rev 2.0) completes both arms × both chips — W27C512 (DIP28, `0x07`, 64 KiB) and W29C020 (DIP32, `0x05`, 256 KiB page-write) — with every result recorded
- [ ] **BOARD-02**: Cell A2 (uno328pb / Rev 2.0) completes both arms × both chips, with its expected program failure captured on **both** arms rather than assumed
- [ ] **BOARD-03**: Cell A3/B2 (Leonardo / Rev 2.0) completes both arms × both chips on the rig v1.31 used, making its results directly comparable to that milestone's record
- [ ] **BOARD-04**: Each cell records measured write duration per arm, so a timing regression is visible against v1.31's W27C512 consistency of 0.37 s

### Shield Sweep — three shields on the Leonardo (SHIELD)

- [ ] **SHIELD-01**: Cell B1 (Leonardo / Modified Rev 0) completes both arms × both chips
- [ ] **SHIELD-02**: Cell B3 (Leonardo / Rev 2.2) completes both arms × both chips
- [ ] **SHIELD-03**: Cell A3/B2 is executed exactly once and cited by both sweeps — no duplicate run and no duplicate evidence row
- [ ] **SHIELD-04**: Each shield cell records the firmware's own shield-version detection result (the v1.7 A3 ADC band read) next to the operator's declared revision, so a detection mismatch is caught — the first time that plumbing is swept across all three physical shields

### Chip Sweep — 11 parts on the reference rig (CHIP)

- [ ] **CHIP-01**: `firestarter dev test` runs under v1.33 firmware on Leonardo + Rev 2.0 against all 11 v1.15 inventory parts — W27C512, W27E512, SST27SF512, W27E040, ST M27C512, SST39SF040, W29C040, W29C020, FM1608, AM27C020, 2516 — each producing a report artifact
- [ ] **CHIP-02**: Every report is firmware-attributable with a non-null `fw_board_identity`; a null is treated as a defect to investigate, not an accepted gap
- [ ] **CHIP-03**: Each chip's result is compared against its recorded v1.15 disposition and every divergence is listed explicitly
- [ ] **CHIP-04**: A control-arm re-run is performed for every diverging chip and for no other, keeping the sweep at 11 runs plus divergences
- [ ] **CHIP-05**: Known-dead and known-limited parts are reported with their prior disposition cited inline — W27E512 stuck bit @0x3d and W27E040 stuck bit @0x7db (D-32 silicon wear), W29C040's permanently locked §6.6 boot block (CR-01), AM27C020's non-deterministic marginality — so their reds are never counted as v1.34 findings

### Regression Triage (RCA)

- [ ] **RCA-01**: Every failure in every cell is classified **v1.33-caused / pre-existing / inconclusive**, with the specific A/B evidence supporting the classification named alongside it
- [ ] **RCA-02**: Every v1.33-caused regression is root-caused to a specific v1.33 change — which phase, which commit, which mechanism — not merely to "v1.33"
- [ ] **RCA-03**: Every v1.33-caused regression is fixed **on the v1.33 PR branch** so the open PR ships fixed, and the fix is re-validated in the cell that caught it
- [ ] **RCA-04**: Inconclusive results are recorded as inconclusive and are never resolved by assumption in either direction
- [ ] **RCA-05**: Pre-existing failures are linked to their existing backlog item — 999.2 for the uno328pb brownout, CR-01 for W29C040 — and explicitly not fixed in v1.34

### Modified Rev 0 Rework Trace (REV0)

- [ ] **REV0-01**: Operator photographs the Modified Rev 0 board — top, bottom, silkscreen, and one frame per rework region — while it is on the bench for cell B1
- [ ] **REV0-02**: Each cut and jumper is traced against the upstream Rev 0 schematic (blob `d2a7f691`) and written up in `.planning/v1.7/MODIFICATIONS.md`, replacing the stub that has stood since v1.7
- [ ] **REV0-03**: The **ten** `TBD pending Phase 35` cells in `v1.7-SHIELD-REVS.md` §4/§5 — two `Rev 0 → Modified Rev 0` rows of five cells each, plus the §4 prose mention — are filled from that trace, or each cell that stays TBD is named with the specific reason it could not be resolved

### Close (CLOSE)

- [ ] **CLOSE-01**: One evidence table covers all five cells × two arms × two chips, where every position holds either a result or a named reason for its absence — no silent gaps
- [ ] **CLOSE-02**: An explicit merge recommendation — merge / merge-with-caveats / do-not-merge — stating the evidence it rests on
- [ ] **CLOSE-03**: An honesty ledger pairs each claim with its explicit non-claim; in particular it records that program-window VPP/VCC **under load** remains unmeasured (the DTR-reset-on-close tooling gap stands), so v1.34 makes no electrical claim
- [ ] **CLOSE-04**: v1.34 performs no merge, no push to `beta`, no sub-repo tag, no beta cut and no release — every outward-facing step is left to the operator
- [ ] **CLOSE-05**: Anything found and not fixed is filed as a backlog item rather than carried as prose in a closing document

## Future Requirements

Deferred — tracked, not in this roadmap.

### Seeds declined at activation (2026-08-25)

- **Voltage-reading white-box calibration** — its "accuracy/hardware-focused milestone opens" trigger fired literally, and it has a real bench dependency, but it would roughly double v1.34 and turn a regression gate into a feature milestone. Seed stays planted.
- **Rev 2.2 3-pin header + 2516-family support** — opportunistic only. Its own trigger (v1.24 scoping) has not fired, and its blocker list needs a new DB field, `build_db.py` support and firmware pin-strobe verification.
- **Per-pin-map jumper table** — host-only refactor of `ic_layout.py`, no bench dependency whatsoever.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Merging `prom#43` / `fw#56` / `app#54` | Operator-gated. Precedent since v1.21 puts every outward-facing step behind the operator |
| Beta cut or any release | A merge to `beta` auto-fires a pre-release cut — not a side effect to trigger from a bench milestone |
| Fixing the uno328pb chip-PROGRAM brownout | Pre-existing, Backlog 999.2. v1.34 measures it on both arms; it does not adopt it |
| Fixing W29C040's page-0 flash4 fault | Pre-existing CR-01, open since v1.15, and the sample's §6.6 boot block is permanently locked regardless |
| Fixing AM27C020's marginality | Non-deterministic (write#1 60/64, write#2 0/64) — it cannot arbitrate a result in either direction, so no fix can be validated |
| Replacing W27E512 / W27E040 | Silicon wear (D-32), deterministic stuck erase bits. Not a software defect |
| Measuring program-window VPP/VCC under load | The held-rail DMM proxy is defeated by DTR-reset-on-close — the standing Phase-97 tooling gap. Every VPP figure on record is an idle firmware-ADC sample and stays that way |
| PY32F071 validation | No PCB exists. Nothing has ever run on this silicon |
| Any product-code change not traced to a v1.33-caused regression | v1.34 is a gate, not a development milestone |
| Raising the ~6.25 V program-VCC rail | Unreachable on every shield revision this project owns — the v1.31 evidence ceiling, unchanged |

## Traceability

Populated during roadmap creation (2026-08-25). Every v1 requirement maps to exactly one phase;
phase numbering continues at **160** (v1.33 ran 154–159).

| Requirement | Phase | Status |
|-------------|-------|--------|
| RIG-01 | Phase 160 | Complete |
| RIG-02 | Phase 160 | Complete |
| RIG-03 | Phase 160 | Complete |
| RIG-04 | Phase 160 | Pending |
| RIG-05 | Phase 160 | Pending |
| BOARD-01 | Phase 161 | Pending |
| BOARD-02 | Phase 161 | Pending |
| BOARD-03 | Phase 161 | Pending |
| BOARD-04 | Phase 161 | Pending |
| CHIP-01 | Phase 162 | Pending |
| CHIP-02 | Phase 162 | Pending |
| CHIP-03 | Phase 162 | Pending |
| CHIP-04 | Phase 162 | Pending |
| CHIP-05 | Phase 162 | Pending |
| SHIELD-01 | Phase 163 | Pending |
| SHIELD-02 | Phase 163 | Pending |
| SHIELD-03 | Phase 163 | Pending |
| SHIELD-04 | Phase 163 | Pending |
| REV0-01 | Phase 164 | Pending |
| REV0-02 | Phase 164 | Pending |
| REV0-03 | Phase 164 | Pending |
| RCA-01 | Phase 165 | Pending |
| RCA-02 | Phase 165 | Pending |
| RCA-03 | Phase 165 | Pending |
| RCA-04 | Phase 165 | Pending |
| RCA-05 | Phase 165 | Pending |
| CLOSE-01 | Phase 166 | Pending |
| CLOSE-02 | Phase 166 | Pending |
| CLOSE-03 | Phase 166 | Pending |
| CLOSE-04 | Phase 166 | Pending |
| CLOSE-05 | Phase 166 | Pending |

**Phase index:**

| Phase | Name | Requirements |
|-------|------|--------------|
| 160 | RIG — Dual-Arm Build, Flash Provenance & the Shared Cell Procedure | RIG-01…05 (5) |
| 161 | BOARD — Board Sweep, Three Boards on Rev 2.0 | BOARD-01…04 (4) |
| 162 | CHIP — 11-Part `dev test` Sweep on the Reference Rig | CHIP-01…05 (5) |
| 163 | SHIELD — Shield Sweep, Three Shields on the Leonardo | SHIELD-01…04 (4) |
| 164 | REV0 — Modified Rev 0 Rework Trace | REV0-01…03 (3) |
| 165 | RCA — Regression Triage, Root Cause & PR-Branch Fix | RCA-01…05 (5) |
| 166 | CLOSE — Evidence Table, Merge Recommendation & Honesty Ledger | CLOSE-01…05 (5) |

**Coverage:**

- v1 requirements: 31 total
- Mapped to phases: 31 ✅
- Unmapped: 0
- Orphans: 0 · Duplicates: 0 (no requirement appears in more than one phase)

---
*Requirements defined: 2026-08-25*

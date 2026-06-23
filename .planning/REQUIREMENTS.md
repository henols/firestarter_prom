# Requirements: Firestarter v1.15 — Bench Validation of Operator Inventory

**Defined:** 2026-06-23
**Core Value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware handler. No guessing. **This milestone proves that contract holds on real silicon** for the operator's physical chip inventory.

**Scope:** Full write→read→verify on **Leonardo + RURP Rev 2.0** (the only trustworthy program/write/verify combo) for 11 physical chips across 5 algorithm families. Prove the on-paper `supported` claim on silicon, validate DB decode, RCA/fix failures, produce a per-chip evidence record, and graduate the one genuine gap (the `2516`, confirmed absent from minipro upstream). Mostly host-side; firmware untouched unless a bench-surfaced defect forces a lockstep fix.

## v1.15 Requirements

### Evidence Record & Oracle (EVID)

- [ ] **EVID-01**: A per-chip bench evidence record (`.planning/v1.15/bench/EVIDENCE.{md,json}`) captures, for every chip exercised: chip, family/algorithm, board + shield rev, blank-state, operation, SHA, verdict, and anomalies — extending (not replacing) the v1.13 per-family validation matrix.
- [ ] **EVID-02**: All bench operations reuse existing tooling (`firestarter write/read/verify`, `dev validate-family`, `write_test.sh`) and existing gates (`check_dispatch.py`, `diff_db.py`); no new harness or third-party dependency is introduced.
- [ ] **EVID-03**: Each chip's PASS verdict is non-vacuous — proven by a trustworthy Leonardo read (N≥3, byte-identical / SHA-matched) plus a negative control (a wrong-file `verify` exits non-zero).

### Non-Destructive Read Sweep (SWEEP)

- [ ] **SWEEP-01**: Every one of the 11 chips is read end-to-end and blank-checked on Leonardo + Rev 2.0 **before any write**, consuming zero chips, validating the read path + DB decode.
- [ ] **SWEEP-02**: The blank-state of each of the 3 true UV-EPROMs (ST M27C512, AM27C020, 2516) is recorded in the evidence record — this gates each UV write decision.

### Electrically-Rewritable Validation (REWR)

- [ ] **REWR-01**: W27C512, W27E512, SST27SF512 (0x07 EEPROM, 12V) each pass full write→auto-erase→read→verify with SHA match.
- [ ] **REWR-02**: W27E040 (0x08 EEPROM, 512KB) passes full write→read→verify with SHA match.
- [ ] **REWR-03**: SST39SF040 (0x06 flash3 / AMD-style) passes full write→read→verify with SHA match.
- [ ] **REWR-04**: W29C020 and W29C040 (0x05 flash4 / Winbond) each pass full write→read→verify with SHA match, with auto-erase confirmed correct for the `Flash/EEPROM` electrical type.
- [ ] **REWR-05**: FM1608 (0x40 FRAM) passes full write→read-back→verify (overwrite path, no erase).

### UV-EPROM No-Eraser Protocol (UV)

- [ ] **UV-01**: The UV-EPROM test protocol is non-destructive-first: read + blank-check precede any write, and no UV part is written until its blank-state is recorded (operator has no UV eraser — every write is irreversible).
- [ ] **UV-02**: For each UV part the operator makes an explicit spend-vs-preserve decision at the bench before any write.
- [ ] **UV-03**: A "spent" UV part is write-proven without an eraser — a full known image if blank, else an all-`0x00` / AND-mask bit-subset write (only 1→0 transitions) — and the result is verified (read-back SHA / verify exit code).
- [ ] **UV-04**: ST M27C512 (0x07) and AM27C020 (0x08) each have a recorded read + decode validation, plus a write proof if spent.

### 2516 Graduation (GRAD)

- [ ] **GRAD-01**: The `2516` is researched to datasheet level (confirm its absence from minipro `infoic.xml`; capture NMOS / DIP24 / ~25V class / 2KB / 2716 read-compatibility) and the findings recorded.
- [ ] **GRAD-02**: A `2516` entry is authored in `~/.firestarter/database.json` (algorithm `0x0B`, pinout `DIP24_2716`, `electrical.type` UV-EPROM, `vpp_mv` 25000, `size_bytes` 2048) and **manually safety-reviewed** (user-override entries bypass `check_dispatch.py`/`diff_db.py`); `firestarter info 2516` shows correct decode.
- [ ] **GRAD-03**: The `2516` is bench-proven on Leonardo + Rev 2.0 (read + blank-check, then a write proof on the ~22.4V VPE rail), recording the result — closing the deferred **FUT-03** NMOS write+SHA evidence (best-effort per v1.14 D-07).

### DB Decode Correctness (DB)

- [ ] **DB-01**: For every chip exercised, the DB-recorded decode (pinout, VPP, electrical type, algorithm, size) is confirmed against real-silicon behavior; any mismatch is flagged in the evidence record.
- [x] **DB-02**: Before any rewritable-chip write bench, a code review confirms `FLAG_CAN_ERASE` is derived correctly for **both** `EEPROM` and `Flash/EEPROM` electrical types; any gap is fixed and pinned by a test.

### Defect RCA & Fix (FIX)

- [ ] **FIX-01**: Any per-family write/program/verify defect the bench surfaces is root-caused and fixed (host-only, or dual-repo lockstep if firmware), re-verified on the bench, with the full-DB VPP-safety gate green. *(Conditional — closes as "none found" if the bench is clean.)*

### Bench Safety & Hygiene (SAFE) — cross-cutting

- [ ] **SAFE-01**: Every bench task records and verifies its preconditions: board = Leonardo, shield rev = Rev 2.0 (operator-stated), `controller:` port identity, and a live R1/R2 readback (`r1 ≈ 270000`).
- [x] **SAFE-02**: The host test suite — including the 0xA4 `ack_data=False` regression guard (`test_init_phase_data_frames_not_acked`) — is green before any bench session.
- [x] **SAFE-03**: No non-Leonardo read is treated as authoritative; no UV part is written before blank-check + an explicit spend decision; over-voltage stays blocked (under-voltage warn-and-proceed accepted as best-effort).

## v2 / Future Requirements

Deferred — tracked, not in this roadmap.

### Future (FUT)

- **FUT-A**: Strict ≥25V-verified NMOS graduation (hardware boost stage) — this milestone is best-effort on the ~22.4V VPE rail per v1.14 D-07.
- **FUT-B**: Promote the `2516` from a user-override entry into the upstream-derived DB / `build_db.py` built-in set — only if it ever appears in minipro `infoic.xml`.
- **FUT-C**: Resume the deferred v1.9 read-bug RCA (Phase 45) to restore a trustworthy verify board beyond Leonardo.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Acquiring / using a UV eraser | Operator has none; read-first + AND-mask (all-0x00) write proof covers UV validation without one |
| Program/write validation on Uno / uno328pb | Read-bug oracle untrustworthy off Leonardo; uno328pb N/A for program/write (999.2 brownout) — v1.9 territory |
| Chips outside the operator's physical inventory | This milestone validates the 11 chips on hand, not the full 744-chip DB |
| New firmware handlers / new algorithm families | Validating existing handlers (0x05/0x06/0x07/0x08/0x0B/0x40); firmware untouched unless a defect forces a lockstep fix |
| Pushing the `2516` upstream / into `build_db.py` | User-override entry is sufficient; the part is genuinely absent from minipro (→ FUT-B) |
| Strict ≥25V NMOS hardware change | Best-effort on the existing ~22.4V VPE rail per v1.14 D-07 (no hardware change ever) → FUT-A |
| Resuming the v1.9 read-bug RCA | Separate deferred milestone (Phase 45) → FUT-C |

## Traceability

Populated during roadmap creation (each requirement maps to exactly one phase).

| Requirement | Phase | Status |
|-------------|-------|--------|
| EVID-01 | Phase 81 | Pending |
| EVID-02 | Phase 81 | Pending |
| EVID-03 | Phase 81 | Pending |
| SWEEP-01 | Phase 81 | Pending |
| SWEEP-02 | Phase 81 | Pending |
| REWR-01 | Phase 82 | Pending |
| REWR-02 | Phase 82 | Pending |
| REWR-03 | Phase 82 | Pending |
| REWR-04 | Phase 82 | Pending |
| REWR-05 | Phase 82 | Pending |
| UV-01 | Phase 83 | Pending |
| UV-02 | Phase 83 | Pending |
| UV-03 | Phase 83 | Pending |
| UV-04 | Phase 83 | Pending |
| GRAD-01 | Phase 81 | Pending |
| GRAD-02 | Phase 81 | Pending |
| GRAD-03 | Phase 83 | Pending |
| DB-01 | Phase 82 | Pending |
| DB-02 | Phase 81 | Complete |
| FIX-01 | Phase 84 | Pending |
| SAFE-01 | Phase 81 | Pending |
| SAFE-02 | Phase 81 | Complete |
| SAFE-03 | Phase 81 | Complete |

**Coverage:**

- v1.15 requirements: 23 total
- Mapped to phases: 23 ✓ (Phase 81: 11 · Phase 82: 6 · Phase 83: 5 · Phase 84: 1)
- Unmapped: 0 ✓ (every requirement maps to exactly one phase)

---
*Requirements defined: 2026-06-23*
*Last updated: 2026-06-23 after roadmap creation (traceability populated, Phases 81–84)*

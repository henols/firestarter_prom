# Requirements — v1.17 Implement & Test the W29C040 Programming Protocol

**Milestone goal:** Root-cause and fix the W29C040 flash4 (`0x05`) page-write defect on real silicon, generalize flash4 page sizing to a datasheet-sourced per-chip DB field (CR-01), and bench-prove a byte-exact write→read→verify on the operator's seated W29C040 — graduating it to genuinely `supported` and closing CR-01 / Phase-74 Wave-2.

**Locked context:**

- Firmware forks off the **v1.16 tip `a296195`** (primitives recompose), NOT firmware `beta` (stale at v1.13). Dual-repo lockstep where the change crosses the wire. Meta `.planning/` on `gsd/v1.17-w29c040-programming-protocol` (off the beta-tracking tip).
- Bench LOCKED to **Leonardo + RURP Rev 2.0**; operator seats the W29C040. Standing bench discipline (live R1/R2 readback, `controller:` identity per task, Leonardo chip-OUT-sideload-exempt).
- The W29C040 page size is **already correct** (256 B) — so the page-0 fault root cause is **distinct from** the CR-01 page-size generalization. RCA + FIX address the real fault; PGSZ generalizes page sizing for the *other* (under-sized) flash4 families.
- Phase numbering continues at **Phase 93**.

---

## v1.17 Requirements

### RCA — Root-Cause the W29C040 Write Fault

- [x] **RCA-01**: The W29C040 page-0 write fault is reproduced on the seated chip (Leonardo + Rev 2.0) with a captured failure signature — which addresses/bytes fail, and the DQ7/DQ6 toggle-poll behavior at the failure — establishing a pre-fix baseline.
- [x] **RCA-02**: The W29C040 write path is differentially compared against the passing `0x05` sibling W29C020 across the candidate axes (SDP unlock sequence, page-write polling/timing, address span / A18 512 KB addressing, page size) to isolate the differing variable(s).
- [ ] **RCA-03**: A named root cause (or ranked hypotheses each with disconfirming evidence) for the page-0 fault is recorded, classifying it as firmware-algorithm, timing, addressing, or silicon — sufficient to design a targeted fix.

### FIX — Firmware Write-Path Fix

- [ ] **FIX-01**: The firmware flash4 write path (`firestarter/src/proms/flash_type_4.cpp`, on the v1.16 primitives recompose) is corrected so the W29C040 programs page 0 and all subsequent pages without the page-write fault.
- [ ] **FIX-02**: The fix preserves the v1.16 flash4 golden register traces + dispatch-mirror guard for the passing paths (W29C020 / SST29 family); where a trace legitimately changes, it is re-pinned with cited rationale.
- [ ] **FIX-03**: Native flash4 tests cover the corrected write path (page-0 + page-boundary), and the fix is delivered dual-repo lockstep wherever it crosses the wire (`constants.py` ↔ `firestarter.h`).

### PGSZ — Datasheet-Sourced Per-Chip Page Size (CR-01)

- [ ] **PGSZ-01**: Each flash4 chip in the DB carries a datasheet-sourced per-chip `page_size` field (not derived from capacity), authored in the `build_db.py` pipeline / chip DB source with cited datasheet values.
- [ ] **PGSZ-02**: The firmware consumes the per-chip `page_size` instead of `flash4_page_size(mem_size)`, removing the capacity heuristic so the under-sized 64 KB (128 B) and 256 KB (256 B) flash4 families are correctly sized.
- [ ] **PGSZ-03**: `page_size` is carried over the wire (lockstep field) with a safe default/fallback for any chip lacking the datum; `check_dispatch.py` passes and `diff_db.py` shows only the intended `page_size` additions.

### BENCH — Bench Validation & Graduation

- [ ] **BENCH-01**: A full write→auto-erase→program→verify cycle on the seated W29C040 (Leonardo + Rev 2.0) reads back byte-exact (SHA match) to the written image — the hard graduation gate (no best-effort fallback).
- [ ] **BENCH-02**: A passing-sibling regression check (W29C020 `0x05`, plus any other on-hand flash4 band) confirms the fix + `page_size` change did not break a previously-passing chip.
- [ ] **BENCH-03**: Bench evidence (commands, source/read-back SHAs, port/rev/R1-R2 readback, pass/fail) is captured per standing bench discipline in a per-chip EVIDENCE record.

### LEDGER — Evidence & Ledger Recording

- [ ] **LEDGER-01**: The PROTOCOL-LEDGER is updated — W29C040 `0x05` moves from open-defect to PASS / `supported`; CR-01 / Phase-74 Wave-2 is closed with the bench SHA as evidence.
- [ ] **LEDGER-02**: `check_ledger.py` self-consistency gate passes with the updated ledger state.

### SAFE — Safety & Non-Regression

- [x] **SAFE-01**: Over-voltage stays blocked at the firmware VPP check and the host `chip_resolver.resolve_chip` guard is never bypassed; W29C040 graduation flows through the normal `supported` path.
- [ ] **SAFE-02**: The lockstep wire contract stays in sync (constants parity test green) and host CI is green against the **py3.11** target (ruff check + ruff format --check + mypy + diff_db + check_dispatch), avoiding the py3.12-masks-CI-3.11 trap.

---

## Future Requirements (deferred)

- **FUT-06** — AM27C020 `0x08` 32-pin write/VPP path (RCA'd, not trivially fixable; needs 0x08 32-pin Large EPROM write/VPP root-cause). Out of scope this milestone unless the W29C040 RCA surfaces a shared cause.
- **FUT-03 / GRAD-03** — 2516 `0x0B` read instability + write proof (best-effort; shared OE/VPP pin). Unrelated family; deferred.
- **FUT-05** — REWR-02 `0x08` write proof (W27E040 stuck-bit; needs a functional 0x08 rewritable chip).

## Out of Scope

- **Re-refactoring flash4 / primitives** — v1.16's primitive decomposition is the baseline; this milestone fixes behavior on top of it, not the architecture.
- **Other flash4 chips' bench validation** — only the W29C040 carries the hard graduation gate; the `page_size` correctness for 64 KB/256 KB families is delivered + gate-checked but bench-proven only opportunistically (BENCH-02) if a chip is on hand.
- **Lockstep beta cut / stable promotion / gitlink bump** — operator-gated standing policy (gitlinks PINNED at b10); not part of this milestone's delivery.
- **v1.9 read-bug RCA** — separate deferred milestone; the Leonardo + Rev 2.0 lock exists precisely to avoid it.
- **X88C64 (FUT-01), AT28C04/16 adapter (FUT-04)** — hardware-blocked, unrelated.

## Traceability

_Filled by the roadmapper 2026-06-26 — all 16 REQ-IDs mapped to exactly one phase (no orphans, no duplicates). SAFE-01/SAFE-02 home in their earliest establishing phase (93/94) and recur as preconditions through close._

| REQ-ID | Phase | Status |
|--------|-------|--------|
| RCA-01 | Phase 93 | Complete |
| RCA-02 | Phase 93 | Complete |
| RCA-03 | Phase 93 | pending |
| FIX-01 | Phase 94 | pending |
| FIX-02 | Phase 94 | pending |
| FIX-03 | Phase 94 | pending |
| PGSZ-01 | Phase 94 | pending |
| PGSZ-02 | Phase 94 | pending |
| PGSZ-03 | Phase 94 | pending |
| BENCH-01 | Phase 95 | pending |
| BENCH-02 | Phase 95 | pending |
| BENCH-03 | Phase 95 | pending |
| LEDGER-01 | Phase 96 | pending |
| LEDGER-02 | Phase 96 | pending |
| SAFE-01 | Phase 93 | Complete |
| SAFE-02 | Phase 94 | pending |

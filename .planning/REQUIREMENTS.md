# Requirements — v1.18 AM27C020 0x08 Write-Path RCA & Fix

**Milestone goal:** Root-cause why the AM27C020 (`0x08` EPROM-QUICK, 32-pin, 256K×8 CMOS EPROM) programs **0 bits**, fix the firmware/host `0x08` 32-pin write/VPP path so it programs correctly without breaking the passing EPROM paths, and bench-prove byte-exact write→verify on real silicon — gated on a Tier-0 silicon-writability pre-flight (the W29C040 lesson: confirm the chip is re-programmable before committing the bench graduation).

## Constraints / Standing Context

- **Bench LOCKED to Leonardo + RURP Rev 2.0.** Standing discipline: live R1/R2 readback + `controller:` identity per task; Leonardo chip-OUT-sideload-EXEMPT; never trust N=1.
- On-hand AM27C020, writability state UNKNOWN — **PRE-01 Tier-0 pre-flight is the hard first gate.** If OTP/dead, BENCH defers (FUT) and the milestone re-scopes to software-fix-only — no fabricated graduation.
- Research brief: `.planning/research/v1.18-AM27C020-27C-EPROM.md` — leading causes RC-1 (PGM pin 31 mapped as an address line in `DIP32_STD`, authored for 27C040 not 27C020) + RC-2 (P1 VPP routing/level never proven on a UV part). AM27C020 VPP = 12.75 V ±0.25 (Flashrite 100 µs); DB ships `vpp_mv=13000`.
- Firmware forks off the v1.17/v1.16 firmware tip (continue prior base); dual-repo lockstep (`constants.py` ↔ `firestarter.h`, pinout DB) where it crosses the wire; py3.12-masks-CI-3.11 ruff/codegen trap watch.
- SAFE invariant: over-voltage stays blocked at the firmware VPP check; host `chip_resolver.resolve_chip` guard never bypassed; no test-only escape hatch; AM27C020 flows through normal `0x08` dispatch.

## v1.18 Requirements

### PRE — Tier-0 Silicon Writability Gate

- [ ] **PRE-01**: A Tier-0 silicon-writability pre-flight (via the existing read/blank-check path + a single-bit `1→0` micro-probe, no escape hatch) determines whether the seated AM27C020 is re-programmable BEFORE the full graduation. If not writable (OTP / already-programmed / dead), the bench graduation (BENCH-01/02) is deferred to a FUT carry-forward and the milestone re-scopes to software-fix-only — recorded as such, never faked.

### RCA — Root-Cause the 0x08 0-Bits-Programmed Fault

- [ ] **RCA-01**: The AM27C020 `0x08` 0-bits-programmed failure is reproduced on the seated chip (Leonardo + Rev 2.0) with a captured signature — which bytes fail to flip `1→0`, the VPP rail readings at socket pin 1 (and pin 31), and the PGM-pin state during the program window — establishing a pre-fix baseline.
- [ ] **RCA-02**: The `0x08` write path is differentially compared against the passing `0x07` W27C512 (28-pin) across the candidate axes (PGM-pin handling / DIP32 pin-31 mapping, P1 VPP routing + level, JP4 32/28-pin, 32-pin A16/A17 addressing) to isolate the differing variable(s) and exonerate the unchanged axes.
- [ ] **RCA-03**: A named root cause (or ranked hypotheses each carrying disconfirming evidence) is recorded, classified firmware-algorithm / host-pinout / VPP-routing / addressing / silicon — sufficient to design a targeted fix without further RCA.

### FIX — Correct the 0x08 32-Pin Write/VPP Path

- [x] **FIX-01**: The firmware/host `0x08` write path is corrected per the RCA so the AM27C020 program pulse actually flips bits (e.g. PGM / DIP32 pin 31 driven program-active for the 27C020 case rather than mapped as an address line, and/or the P1 VPP routing corrected) — without regressing the passing `0x07` (and other) EPROM paths.
- [x] **FIX-02**: The v1.16 flash/eprom golden register traces + dispatch-mirror guard stay green for the passing paths; where a trace legitimately changes it is re-pinned with cited rationale; native tests cover the corrected `0x08` write path (program-pulse asserted + no regression).
- [x] **FIX-03**: The fix is delivered dual-repo lockstep wherever it crosses the wire (`constants.py` ↔ `firestarter.h`; a per-chip pinout entry, e.g. `DIP32_27C020`, in the DB/pinout pipeline if the RCA shows the 32-pin map is the cause); native + host tests green.

### BENCH — Graduation (gated on PRE-01)

- [ ] **BENCH-01**: A full write→verify cycle on the seated AM27C020 (Leonardo + Rev 2.0) reads back byte-exact (SHA match) to the written image — the graduation gate. **Contingent on PRE-01 passing**; if the chip is OTP/dead, this defers to a FUT carry-forward with documented evidence (not faked).
- [ ] **BENCH-02**: A bench EVIDENCE record is captured (the `1→0` program proof / failing-vs-fixed signature, VPP rail readings, bench-discipline log row), sufficient to update the PROTOCOL-LEDGER `0x08` entry on graduation.

### SAFE — Safety & CI

- [x] **SAFE-01**: Over-voltage stays blocked at the firmware VPP check and the host `chip_resolver.resolve_chip` guard is never bypassed; AM27C020 flows through its normal `0x08` dispatch with no test-only escape hatch (established here, recurs as a precondition through close).
- [x] **SAFE-02**: Host CI is green against the **py3.11** target (ruff check + ruff format --check + mypy + diff_db + check_dispatch), avoiding the py3.12-masks-CI-3.11 trap; constants/wire parity stays in sync if the fix crosses the wire.

## Future Requirements (deferred — carried forward, out of scope for v1.18)

- **FUT-07** — W29C040 byte-exact graduation + LEDGER `supported` (§6.6 boot block permanently locked on the operator's chip; needs a different unlocked sample + third-party bench). All v1.17 software done.
- **FUT-06 (this milestone)** — IS the v1.18 target (AM27C020 `0x08` 32-pin write/VPP). Closes on BENCH-01 (or re-scopes to software-fix-only via PRE-01).
- **FUT-05** — REWR-02 `0x08` rewritable write proof (W27E040 stuck-bit; needs a functional `0x08` rewritable chip). May benefit from the v1.18 `0x08` fix.
- **FUT-04** — AT28C04/16 adapter graduation (adapter not built; 9 chips `adapter-required`).
- **FUT-03 / GRAD-03** — 2516 `0x0B` read instability + write proof (shared OE/VPP pin; the other in-hand defect — deferred, separate family).
- **FUT-01** — X88C64 `0x34` graduation (PCB-blocked, A6/ALE routing).
- **FUT-02** — any NMOS chip requiring >25 V VPP (deliberate fail-closed anti-feature).

## Out of Scope

- **Re-architecting the EPROM handler / primitives** — fix the `0x08` write/VPP path on top of the v1.16 architecture, not the architecture.
- **The other in-hand defect (2516 `0x0B`)** and all other FUT chips — single-chip focus this milestone.
- **Lockstep beta cut / stable promotion / gitlink reconciliation** — operator-gated standing policy; not part of this milestone's delivery.
- **A control-register/PCB change for a dedicated PGM strobe** — only if the RCA proves a free strobe exists; a PCB modification is out of scope (would defer like X88C64).

## Traceability

_Filled by the roadmapper. All v1.18 REQ-IDs map to exactly one phase (no orphans, no duplicates). PRE-01 + SAFE-01 home in their earliest establishing phase and recur as preconditions through close._

| REQ-ID | Phase | Status |
|--------|-------|--------|
| PRE-01 | Phase 97 | Pending |
| RCA-01 | Phase 97 | Pending |
| RCA-02 | Phase 97 | Pending |
| RCA-03 | Phase 97 | Pending |
| SAFE-01 | Phase 97 | Pending (recurs as precondition through Phases 98–99) |
| FIX-01 | Phase 98 | Complete (Plan 04 — corrected fix: reverted Plan 02's inert A18-clear, relies on the existing rw_line mechanism / CTRL_READ_WRITE for pin-31 PGM hold, revision-agnostic) |
| FIX-02 | Phase 98 | Complete (Plan 04 — golden traces byte-identical; RC-98A/B/C reconciled + WR-01 revision-parametrized native test added) |
| FIX-03 | Phase 98 | Complete (Plan 03 — DIP32_27C020 rw-pin:[31] host half) |
| SAFE-02 | Phase 98 | Complete (Plan 03 host CI + Plan 04 primitives.cpp/eprom.cpp untouched) |
| BENCH-01 | Phase 99 | Pending (contingent on PRE-01) |
| BENCH-02 | Phase 99 | Pending |

# Requirements: v1.13 — Programming Algorithm Validation + Gap Implementation

**Milestone goal:** Prove the firmware's 6 already-implemented write/program/verify algorithm families work correctly on real hardware (test-first), behind a reusable software-first validation harness + per-family validation matrix, then implement the genuine RURP-feasible gaps that testing + re-research surface. Evidence defines what "missing" means. Dual-repo lockstep; first firmware-touching milestone since v1.12.

**Research finding (reshapes scope):** v1.12's "the RURP-feasible protocol set already has handlers" was *overstated for the chip operations*: three genuine RURP-feasible gaps survive — the **erase path** (0x07 W27C512; mostly host wiring + a 12V→14V rail detail under the 22V ceiling), an **empty `configure_sram` no-op** (20+ chips report `supported` but writes may silently do nothing), and the **mis-classified X88C64 0x34** (a parallel 5V DIP EEPROM, not a serial/PLD anti-feature). Anti-features (0x11 FWH, 0x2A-2C GAL/PLD, 25V NMOS) remain correctly fail-closed. See `.planning/research/SUMMARY.md`.

**Hardware/gating posture (hybrid):** the harness + matrix + native (Tier 1) + host wire round-trip (Tier 2) tests are software — **no bench gate**. Hardware-in-the-loop (Tier 3) bench runs cover only the families with chips + a working shield on hand; others record an explicit SKIP/deferred row in the matrix. **Leonardo is the only board whose verify read is a valid PASS** (the v1.9-deferred read bug corrupts the verify oracle on Rev-0/Rev-2.0; **uno328pb is N/A for program/write** — 999.2 brownout). Per `feedback_chip_out_before_sideload`, `feedback_verify_port_identity_each_task`, `user_shield_revisions` for all bench work.

---

## v1.13 Requirements

### HARN — Validation Harness & Matrix (software-first spine)

- [x] **HARN-01**: A reusable three-tier validation harness exists — Tier 1 native Unity per-family suites with a shared recording bus stub that captures `rurp_*` register-write sequences (so a handler is provable by side-effect, not just by operation-pointer presence); Tier 2 host pytest wire round-trip via `make_comm`/`fake_serial` (no serial port); Tier 3 a host-driven `dev validate-family` runner that composes the existing `write_cycle_eprom`/`consistency_check_eprom` cycle methods (no re-implementation of read/write). Adds zero production firmware flash.
- [x] **HARN-02**: A declarative per-family validation matrix data file (family → algorithm IDs → representative chip → assertions → native/bench tier) drives both the native suites and the bench runner, and emits a committed `validation-matrix.{json,md}` artifact (family × board × verdict × evidence SHA) that records PASS / FAIL / SKIP-deferred per cell — so partial bench coverage is explicit, not silent.
- [x] **HARN-03**: The matrix bakes in a non-vacuous PASS oracle: a PASS requires an independent post-write full read + SHA compare on **Leonardo** (advisory-only on other boards), a mandatory passing negative control (a wrong-file mismatch and a blank/chip-out failure that prove verify *can* fail), retry-count capture, and a per-task live R1/R2 calibration precondition (`r1 ≈ 270000`); `uno328pb` is hard-coded N/A for program/write cells.
- [x] **HARN-04**: `check_dispatch.py` is extended with per-family dispatch invariants AND its hollow `non_supported_dispatchable` inverse detector is populated (closing the v1.12 accepted tech debt) so a non-`supported` chip routing to a real handler — or a family handler enabling VPP it must not — fails the gate in CI.

### RSCH — Protocol Landscape Re-research

- [x] **RSCH-01**: The minipro/RURP protocol landscape is re-enumerated with per-protocol feasibility verdicts (citing the v1.11 field dictionary + datasheets), reaffirming-or-overturning v1.12's "feasible set complete" finding and confirming which FIX/ERASE/GAP items are genuinely RURP-feasible BEFORE any flash-budget firmware change is committed; anti-features (0x11, 0x2A-2C, 25V NMOS) are re-confirmed fail-closed.

### VAL — Family Validation (Tier 1/2 required for all; Tier 3 hybrid-gated)

- [x] **VAL-01**: UV-EPROM family (`configure_eprom`, 0x07/0x08/0x0B) write + verify + chip-id + blank-check is validated — pulse-delay retry loop convergence confirmed; 0x0B's direct-VPE (no drop-resistor) path proven distinct from 0x07/0x08.
- [x] **VAL-02**: 5V EEPROM family (`configure_eeprom28c`, 0x0D) is validated — SDP-disable sequence, 64-byte page write, and DQ7 data-polling confirmed (AT28C256 representative).
- [x] **VAL-03**: Flash AMD family (`configure_flash3`, 0x06) write + sector/chip erase is validated (the largest chip family).
- [x] **VAL-04**: Flash type-4 family (`configure_flash4`, 0x05/0x35/0x39) write + verify is validated.
- [x] **VAL-05**: Flash Intel family (`configure_flash_intel`, 0x10) is validated — 12V P1 handling and the status-register error branches exercised.
- [x] **VAL-06**: SRAM family (`configure_sram`, 0x0E/0x27/0x28/0x29) is validated AND the empty-no-op question is resolved — the matrix records whether a write actually persists or silently no-ops, classifying SRAM as table-stakes-PASS or as a FIX-01 correctness defect.

### FIX — Per-Family Correctness Fixes (evidence-driven)

- [x] **FIX-01**: IF VAL-06 confirms `configure_sram` is a silent no-op, the handler is corrected to perform real read/write (operation pointers wired; never enables VPP), proven by a Tier-1 register-sequence native test (RED→GREEN) and a Tier-3 Leonardo write+read-back; if VAL-06 shows it already works, FIX-01 is closed as not-needed with evidence.
- [x] **FIX-02**: Flash type-4 (`configure_flash4`) handles `CMD_CHECK_CHIP_ID` (mirroring the flash3 case), proven by a native test; no other family regresses.
- [x] **FIX-03**: The stale "0x39 = 0 chips, future-proofed" comment is corrected and the 2 current 0x39 DB chips are covered by validation.

### ERASE — Erase Path Implementation

- [ ] **ERASE-01**: `firestarter erase <chip>` works for the 0x07-path electrically-erasable EEPROMs (W27C512 representative) — host `FLAG_CAN_ERASE` routing wired to the existing firmware `eprom_internal_erase` electricals, with the 12V→14V erase-rail setpoint confirmed under the 22V RURP ceiling and the datasheet preconditions (A9/OE-VPP high rail) validated; a chip-OUT VPP multimeter dry-run precedes any seated erase. Closeable on Leonardo with a W27C512 on hand.

### GAP — Spec-Only Feasibility (deferred bench/datasheet)

- [x] **GAP-01**: The AT28C04/AT28C16 24-pin EEPROM `adapter-required` path has a documented pin-map/adapter spec and a `resolve_pinout_key` named rule arm (NOT a resurrected guess table); the chips remain `support_status: adapter-required` (refused in-host) until a physical DIP24 adapter exists and a golden write+read-back round-trips — graduation to `supported` is explicitly out of v1.13 scope.
- [x] **GAP-02**: X88C64 (0x34) is re-classified with a documented feasibility verdict + the STORE/RECALL + byte/page write protocol sourced from the datasheet; a firmware handler is committed ONLY if the protocol is fully spec'd and RURP-feasible — otherwise it remains a documented feasible-candidate (no blind handler).

---

## Future Requirements (deferred)

- **Graduating `adapter-required` chips to `supported`** — once a physical DIP24 adapter exists and golden round-trips pass (GAP-01 delivers only the spec + classification this milestone).
- **X88C64 0x34 firmware handler** — if GAP-02's datasheet spec proves feasible but the handler isn't built this milestone.
- **Per-protocol implementation of any further genuinely-feasible protocol** surfaced by RSCH-01 beyond the committed set — each its own (likely hardware-gated) milestone.
- **Full shield-fleet write/verify** (Rev-0 / Rev-2.0 / uno328pb) — blocked on the deferred v1.9 read-bug RCA (Phase 45+); v1.13 validates on Leonardo only.
- **999.1 calibration-default propagation fix** (CONFIG_VERSION gate) and **999.2 uno328pb program brownout** — backlog firmware/bench items; v1.13 only *guards against* them as confounders (live-R1 precondition, uno328pb=N/A), it does not fix them.

## Out of Scope

- **Implementing any infeasible protocol** — 0x11 FWH (LPC-serial/3.3V), 0x2A/0x2B/0x2C GAL/PLD (not memory), 25V NMOS 2716/2732 (`vpp-exceeds-max`). RURP physically cannot drive these; they stay fail-closed. Do NOT relax the `RURP_VPP_CEILING_MV=22000` ceiling.
- **Fixing the v1.9 read bug** — reads are validated on Leonardo only; the shield-fleet read RCA stays its own deferred milestone (Phase 45+).
- **Bench-proving every family this milestone** — hybrid gating: families without chips/shields on hand are recorded SKIP/deferred in the matrix; the milestone closes at partial bench coverage.
- **A hardware/MCU emulator** (Renode/QEMU/simavr) or a HIL framework — native Unity + ArduinoFake + the existing integration scripts cover the need.
- **New third-party test dependencies** — the substrate (PlatformIO native + Unity + ArduinoFake; pytest + syrupy + pyserial) is already present.
- **Graduating adapter-required / X88C64 chips to `supported`** — spec/classification only this milestone (GAP-01/02).

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| HARN-01 | Phase 71 | Complete |
| HARN-02 | Phase 71 | Complete |
| HARN-03 | Phase 71 | Complete |
| HARN-04 | Phase 71 | Complete |
| RSCH-01 | Phase 72 | Complete |
| VAL-01 | Phase 73 | Complete |
| VAL-02 | Phase 73 | Complete |
| VAL-03 | Phase 73 | Complete |
| VAL-04 | Phase 73 | Complete |
| VAL-05 | Phase 73 | Complete |
| VAL-06 | Phase 73 | Complete |
| FIX-01 | Phase 74 | Complete |
| FIX-02 | Phase 74 | Complete |
| FIX-03 | Phase 74 | Complete |
| ERASE-01 | Phase 75 | Pending |
| GAP-01 | Phase 76 | Complete |
| GAP-02 | Phase 76 | Complete |

**Mapped: 17/17 requirements** — every v1.13 requirement maps to exactly one phase; no orphans, no duplicates.

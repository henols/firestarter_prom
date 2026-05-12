# Roadmap: Firestarter — Protocol-Aware Programming Architecture

## Milestones

- ✅ **v1.0 Protocol-Aware Programming Architecture** — Phases 1-13 (shipped 2026-05-11)
- 🚧 **v1.1 Safety Closure & Hardware Validation** — Phases 1-5 (started 2026-05-11)

## Current Milestone: v1.1 — Safety Closure & Hardware Validation

**Goal:** Close the v1.0 audit gaps (Intel-flash REQ-SAF-01, WARNING-2/3/4), bring the four canon chip-family flows (W27C512, 29F040, SST39SF040, AT28C256) under real-hardware validation, and back-fill formal `VERIFICATION.md` artifacts for Phases 01-10 so the v1.0 architecture is fully audited end-to-end.

**Granularity:** Comprehensive
**Total phases:** 5
**Total requirements covered:** 24 / 24 (100%)

### Phases

- [ ] **Phase 1: Safety Closure (Intel-flash VPP + 28C chip-ID)** — Close WARNING-1 and WARNING-2 with Unity test coverage.
- [ ] **Phase 2: Naming Cleanup (Wire Key + Minipro References)** — Atomic `vpp` → `vpp_mv` rename, DB file rename (`minipro_complete_db.json` → neutral name), comment/doc cleanup, single regression scan covering all renames.
- [ ] **Phase 3: Retroactive Verification (Phases 01-10)** — Produce 10 `VERIFICATION.md` audit artifacts back-filling the v1.0 verification gap.
- [ ] **Phase 4: Hardware Validation (RURP shield)** — Repair test scripts and program/verify four canon chip families on real hardware.
- [ ] **Phase 5: Milestone Close** — Write the v1.1 `MILESTONES.md` entry.

### Phase Details

#### Phase 1: Safety Closure (Intel-flash VPP + 28C chip-ID)
**Goal**: Every algorithm path that can apply write voltage performs a pre-pulse safety check (VPP ADC compare and chip-ID validation when populated), and the new checks are covered by Unity tests on `[env:native]`.
**Depends on**: Nothing (first phase — surgical firmware edits, no upstream dependency).
**Requirements**: SAF-04, SAF-05, SAF-06
**Success Criteria** (what must be TRUE):
  1. `flash_intel_write_init` calls `rurp_read_voltage_mv()` and aborts with the existing voltage error code if measured VPP is below the chip's `vpp` setpoint (minus tolerance) before the first write command — REQ-SAF-01 holds for all 39 algorithm=0x10 Intel-flash chips.
  2. `eeprom28c_write_init` honours `handle->chip_id` when non-zero (matching ID proceeds, mismatching ID aborts), so REQ-SAF-02 holds the moment any algorithm=0x0D entry gains a `chip_id_value`.
  3. A Unity test on `[env:native]` proves the new Intel-flash VPP check: low-VPP path returns the voltage error code, nominal-VPP path proceeds.
  4. A Unity test on `[env:native]` proves the new 28C chip-ID check: matching fake chip-ID proceeds, mismatching aborts.
  5. All pre-existing dispatch / handler Unity tests still pass (no regression in the 15 v1.0 tests).
**Plans**: 2 plans
- [x] 01-01-PLAN.md — SAF-04 Intel-flash VPP ADC compare (`flash_intel_write_init` + 5 Unity tests)
- [x] 01-02-PLAN.md — SAF-05 AT28C chip-id check via A9-12V (`eeprom28c_write_init` + 4 Unity tests; OVERRIDES CONTEXT.md D-05 JEDEC proposal per RESEARCH.md datasheet evidence)

#### Phase 2: Naming Cleanup (Wire Key + Minipro References)
**Goal**: The host-side codebase has clean naming — the wire JSON VPP key is unambiguously `"vpp_mv"`, the chip-database file no longer carries the upstream toolchain name, and "minipro" appears in the app only where it's load-bearing (the `MINIPRO_XML_URL` constant and one attribution line). No dispatch regression on any of the 743 chips.
**Depends on**: Nothing structurally, but ordered before Phase 4 so hardware-test scripts use the final wire format and the final DB filename.
**Requirements**: WIRE-01, WIRE-02, CLEAN-01, CLEAN-02
**Success Criteria** (what must be TRUE):
  1. `firestarter_app/firestarter/database.py::convert_to_programmer` (and any sibling emitter) emits the wire key `"vpp_mv"` (not `"vpp"`) carrying the integer millivolt value, the firmware JSON parser reads `"vpp_mv"` into `handle->vpp_mv`, and `firestarter_app/CLAUDE.md` example wire JSON shows only `"vpp_mv"` — no phantom `"vpp"` key.
  2. The chip-database file in `firestarter_app/firestarter/data/` no longer references the minipro tool name (renamed to a neutral name such as `chip_database.json`); all readers (`firestarter/database.py`, `tools/check_dispatch.py`) and the writer (`tools/build_db.py`) point at the new name; meta + sub-repo CLAUDE.md docs reflect the new name.
  3. "minipro" mentions in app code comments are reduced to a single attribution in `tools/build_db.py` (where `MINIPRO_XML_URL` lives); `firestarter/database.py`, `tools/check_dispatch.py`, `firestarter/CLAUDE.md` have zero remaining minipro mentions; `firestarter_app/CLAUDE.md` keeps at most one line naming the upstream source.
  4. `check_dispatch.py` (or equivalent host-side test) regenerates the DB and confirms all 743 chips still parse end-to-end on Uno + Leonardo simulator with no algorithm regressing on the wire, after all four renames.
  5. `firestarter` CLI smoke (`firestarter --help` + `firestarter info W27C512`) succeeds against the renamed DB with no `FileNotFoundError` or stale-path warning.
**Plans**: 3 plans
- [x] 02-01-PLAN.md — WIRE-01 atomic wire-key flip (Python emitter at database.py:518 + firmware parser three-site flip at json_parser.c:62/74/309 + wire-JSON example doc edits)
- [ ] 02-02-PLAN.md — CLEAN-01 file rename via git mv + D-04 internal vpp_volts rename + pyproject.toml/MANIFEST.in packaging alignment
- [ ] 02-03-PLAN.md — CLEAN-02 minipro attribution scrub + WIRE-02 check_dispatch.py augmentation (Shape A round-trip) + SC#5 CLI smoke

#### Phase 3: Retroactive Verification (Phases 01-10)
**Goal**: Every v1.0 phase has a formal `VERIFICATION.md` artifact scoring its requirements against the current source tree, closing the 13 PARTIAL audit findings from the v1.0 milestone audit.
**Depends on**: Phases 1 and 2 (so `05-VERIFICATION.md` can record the SAF-04 closure and the wire-key rename is reflected in all artifacts).
**Requirements**: VERIF-01, VERIF-02, VERIF-03, VERIF-04, VERIF-05, VERIF-06, VERIF-07, VERIF-08, VERIF-09, VERIF-10
**Success Criteria** (what must be TRUE):
  1. Ten `NN-VERIFICATION.md` files exist under `.planning/milestones/v1.0-phases/` (or equivalent retroactive location) — one per v1.0 phase 01..10 — each scoring its phase requirements against the current source tree.
  2. Every audit finding from `.planning/milestones/v1.0-INTEGRATION-CHECK.md` that was attributed to "missing VERIFICATION.md" is either resolved (VERIFIED) or explicitly carried as a follow-up in the corresponding artifact.
  3. `05-VERIFICATION.md` explicitly records that the SAF-04 closure from Phase 1 satisfies the Intel-flash REQ-SAF-01 gap noted in the v1.0 audit.
  4. `10-VERIFICATION.md` confirms `static_high_mask` end-to-end wiring and the `pins < 32` VPE_TO_VPP guard are intact in the current `memory.cpp`.
**Plans**: TBD

#### Phase 4: Hardware Validation (RURP shield)
**Goal**: A physical RURP shield successfully programs and verifies the four canon chip families plus an Intel-flash family chip after the SAF-04 safety closure, with results logged in formal `HW-VALIDATION.md` artifacts and the integration-test shell scripts restored to a working state.
**Depends on**: Phase 1 (SAF-04 must ship before HW-05 can exercise the new VPP ADC compare) and Phase 2 (test scripts must use the final wire key).
**Requirements**: HW-01, HW-02, HW-03, HW-04, HW-05
**Success Criteria** (what must be TRUE):
  1. `firestarter_test.sh` and `write_test.sh` run cleanly against the current `minipro_complete_db.json` — no references to the deleted `database_generated.json` remain (WARNING-4 closed).
  2. A physical RURP shield programs and verifies a W27C512 (algo=0x07, UV-EPROM) via `firestarter write` then `firestarter read --verify`, with results logged.
  3. A physical RURP shield programs and verifies an AM29F040 (chip-erase + write) and an SST39SF040 (sector-erase + write), both algo=0x06, with results logged.
  4. A physical RURP shield programs and verifies an AT28C256 (algo=0x0D via Phase 13 override) with scope/multimeter confirmation that the VPP regulator never engages during the write window.
  5. A physical RURP shield programs and verifies an Intel-family flash (AM28F010 or 28F256, algo=0x10) and confirms the new SAF-04 VPP ADC compare aborts a deliberately-underpowered VPP run.
**Plans**: TBD

#### Phase 5: Milestone Close
**Goal**: The v1.1 milestone is formally recorded in `.planning/MILESTONES.md` using the same Known Gaps / Hardware Verification / Key Decisions structure as the v1.0 entry, so v1.2 planning can start from a clean accumulated record.
**Depends on**: Phases 1-4 (entry summarises what shipped across all preceding phases).
**Requirements**: DOC-01
**Success Criteria** (what must be TRUE):
  1. `.planning/MILESTONES.md` contains a v1.1 entry above the v1.0 entry with the canonical sub-sections (Key Accomplishments, Stats, Key Decisions, Known Gaps, Hardware Verification).
  2. The Hardware Verification sub-section records the four canon chip families plus the Intel-flash family as physically verified (linking to the Phase 4 `HW-VALIDATION.md` artifacts).
  3. The Known Gaps sub-section lists the deferred v1.2 items (DB-06, DB-07, FW-07, FW-08) and any new gaps surfaced during v1.1 execution.
  4. `.planning/PROJECT.md` "Active milestone" header is updated to reflect v1.1 shipped (with date) and the next milestone slot is open.
**Plans**: TBD

### Coverage Map (v1.1)

| Phase | Requirements |
|-------|--------------|
| 1 | SAF-04, SAF-05, SAF-06 |
| 2 | WIRE-01, WIRE-02, CLEAN-01, CLEAN-02 |
| 3 | VERIF-01, VERIF-02, VERIF-03, VERIF-04, VERIF-05, VERIF-06, VERIF-07, VERIF-08, VERIF-09, VERIF-10 |
| 4 | HW-01, HW-02, HW-03, HW-04, HW-05 |
| 5 | DOC-01 |

**Total v1.1 requirements:** 24
**Mapped:** 24
**Orphaned:** 0
**Coverage:** 100% ✓

### Dependency Graph (v1.1)

```
Phase 1 (Safety Closure)  ─┐
                           ├─► Phase 3 (Retroactive Verification) ─► Phase 5 (Milestone Close)
Phase 2 (Wire Rename)     ─┤                                        ▲
                           └─► Phase 4 (Hardware Validation) ───────┘
```

Phase 1 must precede Phase 4 (HW-05 tests the SAF-04 closure on real hardware).
Phase 2 must precede Phase 4 (test scripts must use the renamed wire key).
Phase 3 should follow Phases 1 and 2 (artifacts reflect closures from those phases).
Phase 5 closes the milestone after all preceding phases ship.

## Phases (Historical)

<details>
<summary>✅ v1.0 Protocol-Aware Programming Architecture (Phases 1-13) — SHIPPED 2026-05-11</summary>

- [x] Phase 01: Database Pipeline Fix (3/3 plans) — REQ-DB-01..04
- [x] Phase 02: Firmware JSON Protocol Extension (1/1) — REQ-SER-01, REQ-SER-02
- [x] Phase 03: UV-EPROM Algorithm Correctness (1/1) — REQ-FW-01, REQ-SAF-01
- [x] Phase 04: Flash AMD Sector Erase (2/2) — REQ-FW-04, REQ-SAF-03
- [x] Phase 05: Intel Flash Handler (1/1) — REQ-FW-02
- [x] Phase 06: EEPROM Page Write with DQ7 Polling (1/1) — REQ-FW-03, REQ-SAF-03
- [x] Phase 07: Chip ID Validation & Pre-Write Safety (1/1) — REQ-SAF-01, REQ-SAF-02
- [x] Phase 08: Integration, Rebuild & Verification (1/1) — all
- [x] Phase 09: Hardware Compatibility & Adapter Support (1/1) — REQ-UX-01, REQ-UX-02
- [x] Phase 10: Static Pins, Multi-CE, Address Bus Correctness (1/1) — REQ-FW-05, REQ-FW-06
- [x] Phase 11: Database Pipeline Cleanup (1/1) — REQ-DB-05
- [x] Phase 12: Close BLOCKER-1 + BLOCKER-2 (5/5) — REQ-FW-01, REQ-FW-04, REQ-SER-01
- [x] Phase 13: Close WARNING-5 (3/3) — REQ-FW-03, REQ-SAF-01

Full milestone details: `.planning/milestones/v1.0-ROADMAP.md`
Requirements archive: `.planning/milestones/v1.0-REQUIREMENTS.md`
Audit: `.planning/milestones/v1.0-MILESTONE-AUDIT.md` (status: gaps_found — accepted as v1.1 tech debt)

</details>

## Progress

### v1.1 (Current)

| Phase | Plans | Status | Completed |
|-------|-------|--------|-----------|
| 1. Safety Closure (Intel-flash VPP + 28C chip-ID) | 0/2 | Planned | - |
| 2. Naming Cleanup (Wire Key + Minipro References) | 0/3 | Planned | - |
| 3. Retroactive Verification (Phases 01-10) | 0/? | Not started | - |
| 4. Hardware Validation (RURP shield) | 0/? | Not started | - |
| 5. Milestone Close | 0/? | Not started | - |

### v1.0 (Shipped)

| Phase | Milestone | Plans | Status   | Completed  |
| ----- | --------- | ----- | -------- | ---------- |
| 01    | v1.0      | 2/2 | Complete    | 2026-05-12 |
| 02    | v1.0      | 1/3 | In Progress|  |
| 03    | v1.0      | 1/1   | Complete | 2026-05-09 |
| 04    | v1.0      | 2/2   | Complete | 2026-05-09 |
| 05    | v1.0      | 1/1   | Complete | 2026-05-09 |
| 06    | v1.0      | 1/1   | Complete | 2026-05-09 |
| 07    | v1.0      | 1/1   | Complete | 2026-05-10 |
| 08    | v1.0      | 1/1   | Complete | 2026-05-10 |
| 09    | v1.0      | 1/1   | Complete | 2026-05-10 |
| 10    | v1.0      | 1/1   | Complete | 2026-05-10 |
| 11    | v1.0      | 1/1   | Complete | 2026-05-10 |
| 12    | v1.0      | 5/5   | Complete | 2026-05-11 |
| 13    | v1.0      | 3/3   | Complete | 2026-05-11 |

---

*Roadmap last updated: 2026-05-12 — v1.1 Phase 2 planned (3 plans: WIRE-01 atomic flip / CLEAN-01 file rename + vpp_volts + packaging / CLEAN-02 scrub + WIRE-02 augment + SC#5 smoke); 5 phases, 24 requirements, 100% coverage*

---
phase: 05-intel-flash
verified: 2026-05-12T10:08:00Z
status: passed
score: 3/3 must-haves verified
overrides_applied: 0
requirements_verified:
  - REQ-FW-02
  - REQ-SAF-01
---

# Phase 05: Intel Flash Handler — Verification Report

**Phase Goal:** "New firmware algorithm for Intel-style command-register NOR flash." Concretely: `configure_flash_intel()` exists and implements the 28F command set (0x40 program / 0x20+0xD0 erase / 0x70 status / 0xFF reset); `memory.cpp` dispatches `handle->protocol == 0x10` to this handler BEFORE the mem_type fallback; and (closed by v1.1 SAF-04) `flash_intel_write_init()` validates VPP via `rurp_read_voltage_mv()` before issuing any write/erase command, satisfying REQ-SAF-01 for the Intel-flash family.
**Verified:** 2026-05-12T10:08:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `configure_flash_intel` exists and wires the Intel 28F operation table (`write_init`, `write_execute`, `erase_execute`, `cleanup`, `check_chip_id`). | VERIFIED | `firestarter/src/proms/flash_intel.cpp:52` (`configure_flash_intel` entry). Forward declarations at `:18` (`flash_intel_write_init`) and `:22` (`flash_intel_check_chip_id`). Operation-init assignment at `:57` (`handle->firestarter_operation_init = flash_intel_write_init`) and `:69` (`handle->firestarter_operation_main = flash_intel_check_chip_id` for CMD_CHECK_CHIP_ID). |
| 2 | `memory.cpp` dispatches `handle->protocol == 0x10` to `configure_flash_intel` BEFORE mem_type fallback. | VERIFIED | `firestarter/src/proms/memory.cpp:72` — `if (handle->protocol == 0x10) { configure_flash_intel(handle); return; }` — protocol-prefix dispatch sits before any mem_type check. Cross-link `v1.0-INTEGRATION-CHECK.md` row 8. |
| 3 | `flash_intel_write_init` validates VPP via `rurp_read_voltage_mv()` BEFORE any 28F command is issued (REQ-SAF-01 Intel portion — closed by v1.1 Plan 01-01 / SAF-04). | VERIFIED | `flash_intel.cpp:74` (`flash_intel_write_init` opens); `:77` (`flash_intel_check_vpp(handle);`); helper definition at `:25-50` reads `rurp_read_voltage_mv()` and compares against `handle->vpp_mv` with ±5% / +500mV bands; CR-01 regression at `:79-85` clears `REGULATOR \| P1_VPP_ENABLE` on error. Call-site precedes the `handle->chip_id > 0` branch at `:87`. Unity coverage: 6/6 PASS in `test_flash_intel_vpp/`. Cross-link `01-VERIFICATION.md` Truth #1 + Truth #3 + Post-Review Fixes CR-01. |

**Score:** 3/3 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/src/proms/flash_intel.cpp` | `configure_flash_intel` + `flash_intel_write_init` + `flash_intel_check_vpp` (v1.1 helper) + `flash_intel_check_chip_id` | VERIFIED | `configure_flash_intel:52`; `flash_intel_check_vpp:25-50` (static helper); `flash_intel_write_init:74` calls helper at `:77`; chip-id branch at `:87`; blank-check at `:96-97` (cross-handler, see `08-VERIFICATION.md`); `flash_intel_check_chip_id` definition at `:152` (referenced by Phase 07). |
| `firestarter/src/proms/memory.cpp` | Algo-first dispatch `protocol == 0x10` → `configure_flash_intel` | VERIFIED | Block at `:72`. |
| `firestarter/test/native/avr/test_flash_intel_vpp/` | Unity suite covering SAF-04 (nominal / low / high / FORCE / REV0 / CR-01 regression) | VERIFIED | Directory exists; 6/6 PASS per `01-VERIFICATION.md` Truth #3. Includes `test_flash_intel_high_vpp_error_clears_regulator` (CR-01 regression). |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `json_parser.c::parse_json` | `handle->protocol` | `extract_long("algorithm", handle->protocol)` | WIRED | Phase 02 wire-key contract; `handle->protocol == 0x10` for the 39 Intel-flash chips in the DB. |
| `memory.cpp:72` | `configure_flash_intel` (`flash_intel.cpp:52`) | Algo-first dispatch branch | WIRED | Branch precedes mem_type fallback — locks REQ-FW-02 reachability for every algo=0x10 chip. |
| `configure_flash_intel:52` | `flash_intel_write_init` (`flash_intel.cpp:74`) | `handle->firestarter_operation_init` assignment at `:57` | WIRED | Op-init runs VPP check first (SAF-04), then chip-id branch, then blank-check. |
| `flash_intel_write_init:77` | `flash_intel_check_vpp` (`flash_intel.cpp:25-50`) | Direct C call, unconditional | WIRED | SAF-04 helper executes BEFORE chip-id branch at `:87` and BEFORE any 28F write command — REQ-SAF-01 Intel portion satisfied. |
| `flash_intel_check_vpp:25-50` | `rurp_read_voltage_mv()` | Free-function call inside helper body | WIRED | Mockable on native via `host_stubs.cpp::set_mock_vpp_mv` (verified by Unity suite 6/6 PASS). |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `database.py::_map_data` | `protocol_id` | `programming.get("algorithm", 0)` against chip_database.json (39 algo=0x10 chips) | Yes — Intel-flash entries land protocol=0x10 | FLOWING |
| `database.py::_map_data` | `vpp_mv` | `electrical.get("vpp_mv", 0)` (post-WIRE-01 wire key) | Yes — millivolt setpoint emitted via `"vpp_mv":N` in the JSON command | FLOWING |
| `json_parser.c:62/:74/:309` | `handle->vpp_mv` | `extract_int("vpp_mv", handle->vpp_mv)` (Plan 02-01 firmware-side flip) | Yes — millivolts land on the firmware handle | FLOWING |
| `memory.cpp:72` dispatch | `configure_flash_intel` selected | Branch on `handle->protocol == 0x10` | Yes — protocol-prefix dispatch precedes mem_type | FLOWING |
| `flash_intel_check_vpp:25-50` | measured VPP | `rurp_read_voltage_mv()` against `handle->vpp_mv` | Yes — ADC reading compared against DB-sourced setpoint; aborts with voltage error code on out-of-band | FLOWING |

---

### Behavioral Spot-Checks

(All commands cited from existing verification artifacts — Phase 3 does not re-run per CONTEXT.md D-09 / RESEARCH.md Pitfall #3.)

| Behavior | Command | Result | Cited From |
|----------|---------|--------|------------|
| Intel-flash VPP ADC compare (SAF-04 nominal / low / high / FORCE / REV0 / CR-01) | `pio test -e native` (test_flash_intel_vpp) | 6/6 PASS | `01-VERIFICATION.md` Truth #3 |
| Full Phase 1 native suite (no regression after SAF-04 helper added) | `pio test -e native` | 25/25 PASS | `01-VERIFICATION.md` Behavioral Spot-Check |
| Algo-first dispatch correctness (0x10 → configure_flash_intel) | `pio test -e native` (test_dispatch) | 15/15 PASS | `12-VERIFICATION.md` Truth #6 |
| 743-chip wire round-trip — 39 Intel-flash chips dispatch without regression | `firestarter_app/tools/check_dispatch.py` | exit 0 | `02-VERIFICATION.md` (v1.1) SC4 |
| AVR firmware budget (uno + leonardo) with Intel handler linked | `pio run -e uno` / `-e leonardo` | both SUCCESS | `12-VERIFICATION.md` Truth #7 |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-FW-02 | 05-01 (v1.0) | Intel 28F handler exists; `memory.cpp` dispatches `protocol == 0x10` to `configure_flash_intel` before mem_type fallback. | SATISFIED | `flash_intel.cpp:52` (handler entry); `memory.cpp:72` (algo-first dispatch). Reachability re-confirmed by Phase 12 dispatch suite (15/15 PASS) and `check_dispatch.py` exit 0 on 743 chips. |
| REQ-SAF-01 (Intel portion) | 05-01 (v1.0) → closed by v1.1 Plan 01-01 / SAF-04 | Pre-write VPP ADC compare in `flash_intel_write_init`. | SATISFIED | `flash_intel.cpp:77` calls `flash_intel_check_vpp` helper (definition `:25-50`); 6/6 Unity PASS. UV-EPROM portion owned by `03-VERIFICATION.md`. **SC#3 lock — see Cross-Milestone Closure subsection below.** |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `flash_intel.cpp` | 25-50 | `flash_intel_check_vpp` is inline-copied rather than extracted to a shared helper alongside `eprom_check_vpp` (`eprom.cpp:199`) | Info | Pre-existing. STATE.md "D-04 (SAF-04 inline-copy decision, load-bearing)" — both helpers were intentionally left byte-identical; shared extraction deferred to a cleanup phase. Not a defect. |
| `flash_intel.cpp` | 39 | Local `int response_code` shadows outer-scope idiom | Info | Pre-existing; consistent with `flash_intel_check_chip_id:152` and codebase style. Recorded in `01-VERIFICATION.md` Anti-Patterns. |

No new BLOCKER- or WARNING-level anti-patterns introduced. No carried follow-ups: SAF-04 closed REQ-SAF-01 fully for the Intel-flash family, and Phase 05 introduces no WARNING-5 / WARNING-4 hazard.

---

### Cross-Milestone Closure — REQ-SAF-01 (Intel-flash VPP ADC compare)

The v1.0 `flash_intel_write_init` shipped without a `rurp_read_voltage_mv()` pre-pulse VPP ADC compare — flagged WARNING-1 in `v1.0-MILESTONE-AUDIT.md`, escalated to REQ-SAF-01 UNSATISFIED at v1.0 milestone close (39 algo=0x10 Intel-flash chips affected; reads safe, writes could energize VPP rail without verification).

**Closed by v1.1 Plan 01-01 (SAF-04):** `flash_intel_check_vpp` static helper at `firestarter/src/proms/flash_intel.cpp:25-50`, called from `flash_intel_write_init` at line 77 — BEFORE the `chip_id` branch at line 87 and BEFORE any write command. The helper reads `rurp_read_voltage_mv()` and compares against `handle->vpp_mv` with a 95% lower band (warning) and `+500mV` upper band (error). On error, the CR-01 regression fix at `:79-85` clears `REGULATOR | P1_VPP_ENABLE` before returning, preventing the regulator from being left armed after a voltage abort. Unity coverage: 6/6 PASS in `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp`. The CR-01 regression itself is covered by `test_flash_intel_high_vpp_error_clears_regulator`.

See `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-VERIFICATION.md` Truth #1 + Truth #3 for the canonical v1.1 verification record (Unity execution log, Post-Review Fixes narrative).

**Commit refs:** firmware `firestarter@f6480f2` (CR-01 fix); meta-repo `83c37b7` (state record).

**Current source-tree state:** REQ-SAF-01 is SATISFIED for the Intel-flash family as of 2026-05-12. ROADMAP Phase 3 SC#3 is hereby locked: 05-VERIFICATION.md explicitly records the SAF-04 closure from v1.1 Phase 1 satisfies the Intel-flash REQ-SAF-01 gap.

---

### Gaps Summary

REQ-FW-02 and REQ-SAF-01 (Intel portion) are SATISFIED against the current source tree. SAF-04 closure (v1.1 Plan 01-01) discharges the Intel-flash REQ-SAF-01 PARTIAL; reachability for REQ-FW-02 is re-confirmed by Phase 12 algo-first dispatch and the 743-chip `check_dispatch.py` PASS. **SC#3 lock satisfied above.**

No open follow-ups: the Intel-flash family carries no WARNING-5 hazard (the AT28C256/64 routing issue lives in the algo=0x07 UV-EPROM family, owned by `03-VERIFICATION.md` follow_ups). WARNING-4 (test-script drift) is owned by `08-VERIFICATION.md` per CONTEXT.md D-05.

---

_Verified: 2026-05-12T10:08:00Z_
_Verifier: Claude (gsd-verifier)_

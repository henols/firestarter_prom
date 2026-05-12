---
phase: 03-eprom-algorithms
verified: 2026-05-12T10:05:00Z
status: passed
score: 2/2 must-haves verified
overrides_applied: 0
requirements_verified:
  - REQ-FW-01
  - REQ-SAF-01
follow_ups:
  - source: v1.0-MILESTONE-AUDIT.md WARNING-5 (escalated by Phase 12)
    item: "AT28C256/64 family (30 chips, algo=0x07 + electrical.type='Flash/EEPROM') route through configure_eprom and apply 12V P1_VPP to socket pin 1 (= /WE on DIP28_2764) during write. Reads safe."
    severity: warning
    in_scope: false
    note: "Deferred to v1.2 per MILESTONES.md. Upstream-DB classification issue (minipro tags AT28C256 as EPROM_STD); not a v1.0 Phase 03 defect. Tracked as a per-chip override candidate."
---

# Phase 03: UV-EPROM Algorithm Correctness — Verification Report

**Phase Goal:** "All three UV-EPROM protocols execute with correct pulse timing and VPP routing." Concretely: `configure_eprom()` sets a protocol-appropriate default `pulse_delay` when Python supplies 0; the write path routes VPP via `REGULATOR | P1_VPP_ENABLE` for protocol 0x0B and via `REGULATOR | VPE_TO_VPP` for 0x07/0x08; `eprom_check_vpp()` validates VPP before every write (REQ-SAF-01 UV-EPROM portion).
**Verified:** 2026-05-12T10:05:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `configure_eprom()` dispatches `pulse_delay` from `handle->protocol` (1000µs / 100µs / 500µs for 0x07 / 0x08 / 0x0B). VPE_AS_VPP routing branches on `protocol == 0x0B || FLAG_VPE_AS_VPP`. Reachability: Phase 12 algo-first dispatch lands every UV-EPROM protocol in this handler before any mem_type fallback fires. | VERIFIED | `firestarter/src/proms/eprom.cpp:40` (`configure_eprom` entry); `:68-74` (protocol-default pulse_delay switch — `case 0x08: 100µs`, `case 0x0B: 500µs`, `default: 1000µs`); `:144` (write-path VPE_AS_VPP branch); `:207` (mirror branch inside `eprom_check_vpp`). Reachability: `memory.cpp:92-95` (`if (handle->protocol == 0x07 \|\| handle->protocol == 0x08 \|\| handle->protocol == 0x0B)`) dispatches to `configure_eprom` ahead of mem_type fallback — cited from `v1.0-INTEGRATION-CHECK.md` row 20 and `12-VERIFICATION.md` Truth #1. |
| 2 | `eprom_generic_init` calls `eprom_check_vpp()` unconditionally (not gated on `chip_id > 0`); the helper invokes `rurp_read_voltage_mv()` against `handle->vpp_mv` (REQ-SAF-01 UV-EPROM portion). | VERIFIED | `firestarter/src/proms/eprom.cpp:250-251` — `void eprom_generic_init(...) { eprom_check_vpp(handle); ... }` — first statement, no flag/chip-id guard. Helper definition at `:199` reads `rurp_read_voltage_mv()` and `handle->vpp_mv`. A second unconditional check fires inside `configure_eprom` itself at `:79` (`eprom_check_vpp(handle);` after the protocol-default switch). |

**Score:** 2/2 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/src/proms/eprom.cpp` | `configure_eprom` + protocol-default `pulse_delay` + `eprom_check_vpp` + unconditional call in `eprom_generic_init` | VERIFIED | `configure_eprom` at `:40`; `pulse_delay` switch at `:68-74`; VPE_AS_VPP routing branches at `:144` + `:207`; `eprom_check_vpp` definition at `:199`; `eprom_generic_init` at `:250` with unconditional `eprom_check_vpp(handle);` at `:251`. |
| `firestarter/src/proms/memory.cpp` | Algo-first dispatch for 0x07/0x08/0x0B reaching `configure_eprom` before mem_type fallback | VERIFIED | Block at `:92` — `if (handle->protocol == 0x07 \|\| handle->protocol == 0x08 \|\| handle->protocol == 0x0B) { configure_eprom(handle); return; }` — locks REQ-FW-01 reachability for every UV-EPROM chip in the 743-chip DB. Cross-link `v1.0-INTEGRATION-CHECK.md` row 20 + `12-VERIFICATION.md` Truth #1. |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `json_parser.c::parse_json` | `handle->protocol` | `extract_long("algorithm", handle->protocol)` (Phase 02 wire) | WIRED | `handle->protocol` populated at deserialization time; consumed by `memory.cpp:92` dispatch. |
| `memory.cpp:92` | `configure_eprom` (`eprom.cpp:40`) | Algo-first dispatch branch on 0x07/0x08/0x0B (Phase 12 closure) | WIRED | Branch precedes any mem_type fallback — Phase 12 protocol-prefix dispatch closes the REQ-FW-01 reachability gap for all three UV-EPROM protocols. |
| `configure_eprom` (`eprom.cpp:40`) | `eprom_generic_init` (`eprom.cpp:250`) | `handle->firestarter_operation_init` assignment at `:43` | WIRED | Init runs `eprom_check_vpp` first (`:251`), then chip-id branch, then mem_util_blank_check via standard pre-write order. |
| `eprom_generic_init:251` | `eprom_check_vpp` (`eprom.cpp:199`) | Direct C call, unconditional | WIRED | No `chip_id > 0` guard; no flag gate. Helper reads `rurp_read_voltage_mv()` and compares against `handle->vpp_mv`. REQ-SAF-01 UV-EPROM portion satisfied. |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `database.py::_map_data` | `protocol_id` | `programming.get("algorithm", 0)` against chip_database.json | Yes — 13 entries in `KNOWN_PROTOCOLS`; 0x07/0x08/0x0B all map to UV-EPROM family | FLOWING |
| `json_parser.c::parse_json` | `handle->protocol` | `extract_long("algorithm", handle->protocol)` | Yes — integer wire value lands on the firmware handle | FLOWING |
| `memory.cpp:92` dispatch | `configure_eprom` selected | Branch on `handle->protocol == 0x07 \|\| 0x08 \|\| 0x0B` | Yes — all three protocols reach `configure_eprom` via algo-first path before mem_type fallback (Phase 12 closure) | FLOWING |
| `configure_eprom:68-74` | `handle->pulse_delay` | Protocol-default switch when Python supplied 0 | Yes — defaults: 1000µs (0x07/default), 100µs (0x08), 500µs (0x0B) | FLOWING |
| `eprom_check_vpp:199` | measured VPP | `rurp_read_voltage_mv()` against `handle->vpp_mv` | Yes — actual ADC reading compared against DB-sourced setpoint at runtime | FLOWING |

---

### Behavioral Spot-Checks

(All commands cited from existing verification artifacts — Phase 3 does not re-run per CONTEXT.md D-09 / RESEARCH.md Pitfall #3.)

| Behavior | Command | Result | Cited From |
|----------|---------|--------|------------|
| Algo-first dispatch correctness across all 13 KNOWN_PROTOCOLS (including 0x07/0x08/0x0B → configure_eprom) | `pio test -e native` (test_dispatch) | 15/15 PASS | `12-VERIFICATION.md` Truth #6; re-confirmed by `01-VERIFICATION.md` (v1.1) Behavioral Spot-Check (25/25 native, includes test_dispatch) |
| 743-chip wire round-trip — every UV-EPROM chip parses and dispatches without regression | `firestarter_app/tools/check_dispatch.py` | exit 0 (0 dispatch failures) | `02-VERIFICATION.md` (v1.1) SC4 |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-FW-01 | 03-01 (v1.0) | `configure_eprom` dispatches on `handle->protocol` for pulse_delay and VPP routing; all three UV-EPROM protocols (0x07/0x08/0x0B) reach the handler. | SATISFIED | Protocol-default switch at `eprom.cpp:68-74`; VPE_AS_VPP routing at `:144` and `:207`. Reachability closed by Phase 12 algo-first dispatch — see `12-VERIFICATION.md` Truth #1 (`memory.cpp:92-95`); inline cite, not a Cross-Milestone Closure subsection (Phase 12 is v1.0, not v1.1). |
| REQ-SAF-01 (UV-EPROM portion) | 03-01 (v1.0) | Pre-write VPP ADC compare unconditional in UV-EPROM init path. | SATISFIED | `eprom_generic_init` at `eprom.cpp:250` calls `eprom_check_vpp(handle)` at `:251` unconditionally; helper defined at `:199` reads `rurp_read_voltage_mv()`. Intel-flash portion of REQ-SAF-01 is owned by `05-VERIFICATION.md` (audit attribution split per RESEARCH.md Open Question #2). |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `eprom.cpp` | 199 | `eprom_check_vpp` is a standalone definition not shared with `flash_intel_check_vpp` (`flash_intel.cpp:25-50`, SAF-04) | Info | Pre-existing. STATE.md "D-04 (SAF-04 inline-copy decision, load-bearing)" deliberately left `eprom_check_vpp` byte-identical; helper extraction deferred to a cleanup phase. Not a Phase 03 defect. |
| `eprom.cpp` | 207 | VPE_AS_VPP branch duplicated at `:144` (write path) and `:207` (check path) | Info | Pre-existing parallel-condition pattern; both branches synchronized on the same `protocol == 0x0B \|\| FLAG_VPE_AS_VPP` predicate. Out of scope. |

No new BLOCKER- or WARNING-level anti-patterns introduced by Phase 03. WARNING-5 (AT28C256/64 routing through `configure_eprom` due to upstream-DB classification) is carried in `follow_ups` above — it is **not a Phase 03 handler-logic defect**; the handler is correct, the issue is that an EEPROM family is misclassified upstream as `algorithm=0x07`.

---

### Gaps Summary

REQ-FW-01 and REQ-SAF-01 (UV-EPROM portion) are SATISFIED against the current source tree. Phase 12 algo-first dispatch closes the v1.0 PARTIAL reachability gap for 0x07/0x08/0x0B without rewriting any Phase 03 code.

One open follow-up carried forward: **WARNING-5** — AT28C256/64 family (30 chips) misclassified upstream as `algorithm=0x07 + electrical.type='Flash/EEPROM'` routes through `configure_eprom` and applies 12V P1_VPP to socket pin 1 during write. Reads are safe. Deferred to v1.2 per MILESTONES.md "Known Gaps" — upstream-DB classification fix, not a handler-logic defect (per RESEARCH.md Pitfall #10).

No `Cross-Milestone Closure` subsection: REQ-FW-01 reachability was closed by Phase 12 (a v1.0 phase, not a v1.1 closure), so the standard `Cross-Milestone Closure` framing doesn't apply per CONTEXT.md "Claude's Discretion" + RESEARCH.md recommendation. Phase 12 is cited inline in the REQ-FW-01 Requirements Coverage row. REQ-SAF-01 UV-EPROM portion was always WIRED — no v1.1 work touched the UV-EPROM check path (SAF-04 closure landed in the Intel-flash family, recorded in `05-VERIFICATION.md`).

---

_Verified: 2026-05-12T10:05:00Z_
_Verifier: Claude (gsd-verifier)_

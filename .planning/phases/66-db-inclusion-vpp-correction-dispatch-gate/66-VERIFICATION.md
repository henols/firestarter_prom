---
phase: 66-db-inclusion-vpp-correction-dispatch-gate
verified: 2026-06-12T12:00:00Z
status: gaps_found
score: 3/4 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 3/4
  gaps_closed:
    - "check_dispatch.py now has the non_supported_dispatchable bucket (CR-02); exits 0 and reports truthful PASS with counted non-dispatchable total"
    - "build_db.py sets proto_id = NON_DISPATCHABLE_ALGO (0x00) at Site B (adapter-required) and Site C (vpp-exceeds-max); DB regenerated with algorithm=0 for all 14 non-supported chips"
    - "8th CI invariant test (TestNonSupportedNonDispatchable::test_non_supported_chips_are_non_dispatchable) added; 8/8 inclusion tests pass"
    - "diff_db.py exits 0; all changes attributed (RULE_ALGO x4 compound + RULE_PHASE66 x730 + 10 new WARN)"
    - "Full pytest suite: 494 passed, cov >= 70"
  gaps_remaining:
    - >
      SC#3 remains FAILED — the new check_dispatch.py simulation and the new CI test both use
      dispatch(proto=0, mt=_ALGO_MEM_TYPE.get(0)=None) = ERROR, but database.py::_map_data
      derives mem_type from electrical.type string when protocol_id==0 (falsy), sending
      {algorithm: 0, type: 1} for UV-EPROM chips. Firmware protocol==0 fallback hits
      mem_type==TYPE_EPROM → configure_eprom for the 4 vpp-exceeds-max NMOS entries
      (INTEL/M2716, INTEL/2732-M2732, SGS-THOMSON/ETC2716-M2716, ST/ETC2716-M2716).
      The adapter-required chips are incidentally safe (Flash/EEPROM etype → mem_type=2,
      no firmware handler), but their safety depends on the etype string, not support_status.
  regressions: []
gaps:
  - truth: "entries with any non-supported support_status do NOT resolve to a programming handler (they produce a not_supported / non-dispatchable outcome)"
    status: failed
    reason: >
      The check_dispatch.py gate simulation and the 8th CI test both pass because they call
      dispatch(0, _ALGO_MEM_TYPE.get(0)=None) → ERROR. However, the real production path
      (database.py::_map_data lines 394-407) ignores support_status entirely and, because
      algorithm==0 is falsy, falls through to the electrical.type string heuristic:
      "UV-EPROM" → determined_type=1 (TYPE_EPROM, default). The wire dict emitted is
      {algorithm: 0, type: 1}. Firmware configure_memory: protocol==0 falls to the
      mem_type chain; mem_type==TYPE_EPROM(1) → configure_eprom (12V VPP boost regulator).
      For the 4 vpp-exceeds-max NMOS chips, firestarter M2716 write still resolves to
      configure_eprom at runtime. No host code reads support_status (grep returns 0 matches
      in database.py, chip_resolver.py, eprom_operations.py, cli_handlers.py).
      The adapter-required 24-pin EEPROMs are incidentally safe because "Flash/EEPROM" etype
      → determined_type=2, and firmware has no mem_type=2 case (falls to ERROR) — but this
      relies on the etype string substring, not support_status.
    artifacts:
      - path: "firestarter_app/firestarter/database.py"
        issue: >
          _map_data (lines 394-407): protocol_id = programming.get("algorithm", 0);
          when protocol_id is 0 (falsy), falls to type_str = electrical.get("type", "");
          determined_type = 1 if no "Flash"/"SRAM" substring. For UV-EPROM chips
          (M2716/M2732 family), determined_type=1 (TYPE_EPROM) is sent as wire "type".
          No reference to support_status anywhere in this file or the host runtime path.
      - path: "firestarter_app/tools/check_dispatch.py"
        issue: >
          Simulation calls dispatch(proto=0, mt=_ALGO_MEM_TYPE.get(0)=None) → ERROR.
          This does NOT mirror _map_data's actual mem_type derivation (type_str fallback).
          The gate reports "0 non_supported_dispatchable" and exits 0 — a false PASS for
          the 4 UV-EPROM vpp-exceeds-max chips whose real host+firmware path is configure_eprom.
          The 8th CI test inherits the same simulation gap (imports dispatch and _ALGO_MEM_TYPE
          from check_dispatch, does not call _map_data).
      - path: "firestarter_app/tests/test_build_db_inclusion.py"
        issue: >
          test_non_supported_chips_are_non_dispatchable (lines 319-353) uses
          mt = _ALGO_MEM_TYPE.get(proto) and dispatch(proto, mt), which is the gate's
          simulation model, not the real runtime. dispatch(0, None) = ERROR passes the
          assertion. The test does not exercise database._map_data or the wire dict,
          so it cannot catch the UV-EPROM configure_eprom path.
    missing:
      - >
        Fix option A (host guard — recommended, matches Phase 68 design intent):
        In database.py::_map_data or chip_resolver.resolve_chip, add a support_status
        check before building the wire dict:
          if full_chip.get("support_status", "supported") != "supported":
              raise ChipNotImplementedError(
                  f"{name}: {full_chip.get('unsupported_reason', 'unsupported on this hardware')}"
              )
        This makes support_status load-bearing on the host side and prevents any
        non-supported chip from reaching the serial wire. No firmware change needed.
      - >
        Fix option B (simulation gap closure — required alongside A):
        In check_dispatch.py, mirror _map_data's type_str fallback when proto==0:
          mt = _ALGO_MEM_TYPE.get(proto)
          if not proto:
              etype = chip.get("electrical", {}).get("type", "")
              mt = 1
              if "Flash" in etype: mt = 2
              elif "SRAM" in etype: mt = 4
          handler = dispatch(proto, mt)
        With this fix, the gate would correctly FAIL on the 4 UV-EPROM vpp-exceeds-max
        chips (dispatch(0, 1) = configure_eprom = real handler). Apply the same fix to
        test_non_supported_chips_are_non_dispatchable.
      - >
        After implementing option A, add a pytest test that asserts firestarter write/read
        M2716 raises ChipNotImplementedError (or equivalent) without sending any serial
        command — using a mock EpromDatabase + mock serial. This pins the invariant at
        the runtime boundary, not just the simulation boundary.
---

# Phase 66: DB Inclusion + VPP Correction + Dispatch Gate — Verification Report (Re-verification)

**Phase Goal:** `build_db.py` includes every DIP parallel-memory chip regardless of whether its
`protocol_id` is implemented (unknown/unimplemented → `support_status: protocol-not-implemented`);
NMOS high-VPP family (M2716/M2732=25V, M2732A=21V) gets true VPP with `support_status` derived
from the ~22V RURP ceiling; `check_dispatch.py` and the per-chip diff gate treat any non-supported
entry as non-dispatchable; gate green. HOST-ONLY.

**Verified:** 2026-06-12T12:00:00Z
**Status:** gaps_found
**Re-verification:** Yes — after 66-04 gap-closure plan

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC#1 | DIP parallel-memory chips with unknown/unimplemented protocol_id appear with support_status: protocol-not-implemented; serial/GAL-PLD/MCU/SMD remain absent | VERIFIED | X88C64P,X88C64S present (algorithm=0x34, support_status=protocol-not-implemented). DataFlash 0x04, FWH 0x11, PLCC 0x0A absent. diff_db.py exits 0: 10 new chips attributed to RULE_PHASE66. 8/8 inclusion tests pass. |
| SC#2 | NMOS M2716/M2732/M2732A carry true VPP (25V/21V); M2716/M2732 = vpp-exceeds-max; within-ceiling NMOS = supported at corrected voltage | VERIFIED | INTEL/M2716,M2716M: vpp_mv=25000, vpp-exceeds-max. INTEL/2732,2732A,M2732,M2732A: vpp_mv=25000, vpp-exceeds-max (highest-VPP-wins). SGS-THOMSON/M2732A, ST/M2732A: vpp_mv=21000, supported. ETC2716/M2716 (SGS-THOMSON/ST): vpp_mv=25000, vpp-exceeds-max. All 7 inclusion tests pass. |
| SC#3 | check_dispatch.py exits clean (0 errors); entries with any non-supported support_status do NOT resolve to a programming handler; GATE-03 VPP-safety guard + wire round-trip remain green | FAILED — BLOCKER | check_dispatch.py exits 0 with "0 non_supported_dispatchable" — a false PASS for the production path. Empirically verified: INTEL/M2716, INTEL/2732-M2732, SGS-THOMSON/ETC2716-M2716, ST/ETC2716-M2716 all have algorithm=0x00 + etype="UV-EPROM". database.py::_map_data derives determined_type=1 (default EPROM) from the type_str fallback when protocol_id==0. Wire dict: {algorithm:0, type:1}. Firmware configure_memory: protocol==0 → mem_type chain → mem_type==1 (TYPE_EPROM) → configure_eprom (12V VPP boost regulator). 4 vpp-exceeds-max NMOS chips still reach configure_eprom at runtime. The gate and CI test use dispatch(0, None)=ERROR — a simulation that does not match _map_data's actual derivation. No host code reads support_status (grep confirms zero matches outside chip_database.json). |
| SC#4 | A per-chip diff (diff_db.py) accounts for every new/changed entry with documented rationale; no unexplained diffs | VERIFIED | diff_db.py exits 0. RULE_ALGO x4 compound + RULE_PHASE66 x730 + 10 new WARN. 0 unexplained diffs. Chip count: 744. |

**Score: 3/4 truths verified**

---

## Re-verification: What 66-04 Fixed vs What Remains

### Gaps Closed by 66-04

| Item | Prior Status | Current Status | Evidence |
|------|-------------|----------------|---------|
| build_db.py has NON_DISPATCHABLE_ALGO=0x00 constant | Missing | VERIFIED | `grep -c 'NON_DISPATCHABLE_ALGO = 0x00' tools/build_db.py` = 1 |
| Site B (adapter-required) sets proto_id=0x00 | Missing | VERIFIED | All 9 adapter-required chips: algorithm=0x00 in DB |
| Site C (vpp-exceeds-max) sets proto_id=0x00 | Missing | VERIFIED | All 4 vpp-exceeds-max chips: algorithm=0x00 in DB |
| check_dispatch.py has non_supported_dispatchable bucket | Missing | VERIFIED | `grep -c 'non_supported_dispatchable' tools/check_dispatch.py` >= 3; in sys.exit(1) condition |
| check_dispatch.py PASS message truthful (counted) | Misleading | VERIFIED | Prints "14 chips confirmed non-dispatchable (handler in not_implemented/ERROR); 0 non_supported_dispatchable" |
| 8th CI test pins SC#3 invariant | Missing | PARTIALLY VERIFIED | Test collects + passes, but tests the simulation path (dispatch+_ALGO_MEM_TYPE) not the real runtime path (_map_data) |
| Full pytest suite green (cov >= 70) | N/A | VERIFIED | 494 passed, cov >= 70 |
| diff_db.py exits 0 after proto_id->0x00 change | Unknown | VERIFIED | RULE_ALGO x4 compound for NMOS, RULE_PHASE66 x730, 10 new WARN; exit 0 |

### Remaining Gap: Real Host+Firmware Path Still Reaches configure_eprom

The 66-04 fix correctly demotes `algorithm` to `0x00` in the DB and correctly proves that `dispatch(0, None) = ERROR` in the simulation. However, the simulation does not model what `database.py::_map_data` actually does.

**Exact code trace (empirically verified against current codebase):**

```
firestarter M2716 write → EpromDatabase.get_eprom("M2716")
  → database.py::_map_data (lines 394-407)
    protocol_id = programming.get("algorithm", 0)  # == 0 (algorithm=0 from 66-04 fix)
    if protocol_id and protocol_id in _ALGO_MEM_TYPE:  # False — 0 is falsy
        ...
    else:
        type_str = electrical.get("type", "")  # == "UV-EPROM" for M2716
        determined_type = 1  # Default to EPROM  ← hits this branch
        if "Flash" in type_str: ...  # False
        elif "SRAM" in type_str: ...  # False
    # Wire dict emitted: {algorithm: 0, type: 1, ...}

→ firmware json_parser.c: handle->protocol = 0, handle->mem_type = 1
→ firmware configure_memory:
    protocol == 0x10? No. 0x0D? No. 0x06? No. {0x05,0x35,0x39}? No.
    {0x07,0x08,0x0B}? No. {0x0E,0x27,0x28,0x29}? No.
    {0x11,0x2A,0x2B,0x2C}? No.
    protocol != 0? No (protocol==0).
    → mem_type chain:
    mem_type == TYPE_EPROM (1)? YES → configure_eprom(handle)  ← DAMAGE PATH
```

**Affected chips (4 vpp-exceeds-max NMOS entries):**

| Chip | algorithm | etype | host mem_type | firmware outcome |
|------|-----------|-------|---------------|-----------------|
| INTEL/M2716,M2716M | 0x00 | UV-EPROM | 1 | configure_eprom |
| INTEL/2732,2732A,M2732,M2732A | 0x00 | UV-EPROM | 1 | configure_eprom |
| SGS-THOMSON/ETC2716,M2716 | 0x00 | UV-EPROM | 1 | configure_eprom |
| ST/ETC2716,M2716 | 0x00 | UV-EPROM | 1 | configure_eprom |

**Adapter-required 24-pin EEPROMs (incidentally safe — NOT by design):**

| Chip | algorithm | etype | host mem_type | firmware outcome |
|------|-----------|-------|---------------|-----------------|
| ATMEL/AT28C04,AT28HC04 | 0x00 | Flash/EEPROM | 2 | ERROR (no mem_type=2 case in fw) |
| (all 9 adapter-required chips) | 0x00 | Flash/EEPROM | 2 | ERROR |

The adapter-required chips are safe only because "Flash/EEPROM" contains the substring "Flash" → `determined_type=2`, and firmware has no `mem_type==2` dispatch case. This is incidental to the etype string, not derived from `support_status`. Any future chip with `etype="UV-EPROM"` + `support_status=adapter-required` would follow the M2716 path to configure_eprom.

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/tools/build_db.py` | NON_DISPATCHABLE_ALGO=0x00 + proto_id set at Site B + Site C | VERIFIED | Constant defined; grep confirms >= 2 `proto_id = NON_DISPATCHABLE_ALGO` assignments; ruff clean |
| `firestarter_app/firestarter/data/chip_database.json` | 744 chips; every chip has support_status; non-supported algorithm=0x00 | VERIFIED | 744 chips; all 744 have support_status; all 14 non-supported have algorithm=0 (except X88C64P=0x34) |
| `firestarter_app/tools/check_dispatch.py` | non_supported_dispatchable gate + truthful PASS message | PARTIALLY VERIFIED — SIMULATION ONLY | Gate exists and passes; simulation reports 0 violations correctly within its model; but simulation does not mirror _map_data mem_type derivation for proto==0. The gate cannot detect the UV-EPROM vpp-exceeds-max configure_eprom path. |
| `firestarter_app/tests/test_build_db_inclusion.py` | 8 tests; SC#3 invariant test (IN-03) | PARTIALLY VERIFIED — SIMULATION ONLY | 8/8 tests pass; 8th test (test_non_supported_chips_are_non_dispatchable) uses the simulation dispatch path not the runtime _map_data path — it passes on a real violation |
| `firestarter_app/tools/diff_db.py` | Exits 0 on post-66-04 DB; proto_id change attributed | VERIFIED | Exit 0; RULE_ALGO x4 compound + RULE_PHASE66 x730 + 10 new WARN |
| `firestarter_app/tools/baseline/chip_database.baseline.json` | 734-chip pre-Phase-66 baseline | VERIFIED | Confirmed by test output |
| `firestarter_app/tools/baseline/dispatch_baseline.json` | Regenerated 744-chip dispatch baseline reflecting algorithm=0 triples | VERIFIED | Modified from prior; 13 changed triples enumerated in SUMMARY |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| build_db.py Site B | chip_database.json adapter-required entries | proto_id = NON_DISPATCHABLE_ALGO | VERIFIED | All 9 adapter-required: algorithm=0x00 in DB |
| build_db.py Site C | chip_database.json vpp-exceeds-max entries | proto_id = NON_DISPATCHABLE_ALGO (inside ceiling-exceed branch) | VERIFIED | All 4 vpp-exceeds-max: algorithm=0x00 in DB |
| chip_database.json algorithm=0 | check_dispatch.py simulation | dispatch(0, None)=ERROR | VERIFIED (simulation) | Simulation correctly reports no violations |
| chip_database.json algorithm=0 | database.py::_map_data → wire → firmware | _map_data derives mem_type from electrical.type string | BROKEN | UV-EPROM etype → mem_type=1 → configure_eprom (real path, not simulated) |
| support_status field | host runtime | database.py / chip_resolver.py / eprom_operations.py | NOT WIRED | grep confirms 0 references to support_status in the host runtime path. Deferred to Phase 68 (DB-04) per ROADMAP, but Phase 66's SC#3 requires non-dispatchable at the gate + runtime layer |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|-------------------|--------|
| chip_database.json | support_status per chip | build_db.py _support_status | Yes — all 744 chips | FLOWING to DB |
| chip_database.json | algorithm=0x00 for non-supported | build_db.py NON_DISPATCHABLE_ALGO | Yes — 13 chips (+ X88C64P=0x34) | FLOWING to DB |
| database.py wire dict | type (mem_type) field | _map_data electrical.type fallback when algorithm==0 | Yes — UV-EPROM → mem_type=1 | FLOWING but misroutes UV-EPROM to configure_eprom |
| check_dispatch.py | non_supported_dispatchable bucket | dispatch(0, None)=ERROR simulation | Simulation only — does not match _map_data | HOLLOW (simulation gap) |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| DB chip count = 744 | python3 -c "...sum(len(v)...)" chip_database.json | 744 | PASS |
| All 744 chips have support_status | grep -c '"support_status"' chip_database.json | 744 | PASS |
| All non-supported chips have algorithm=0 | python3 inspect loop | All 14 non-supported: algorithm=0 (X88C64P=0x34) | PASS |
| check_dispatch.py exits 0 | python3 tools/check_dispatch.py | Exit 0, "0 non_supported_dispatchable" (simulation) | PASS (simulation only) |
| M2716 real host path → configure_eprom | python3 -c "EpromDatabase.convert_to_programmer(M2716)" then firmware trace | Wire: {algorithm:0, type:1} → firmware: configure_eprom | FAIL — BLOCKER |
| M2732 real host path → configure_eprom | Same trace for 2732,2732A,M2732,M2732A entry | Wire: {algorithm:0, type:1} → firmware: configure_eprom | FAIL — BLOCKER |
| SGS-THOMSON/ST ETC2716,M2716 real path | Same trace | Wire: {algorithm:0, type:1} → firmware: configure_eprom | FAIL — BLOCKER |
| Adapter-required 24-pin EEPROM path | Same trace for AT28C04 | Wire: {algorithm:0, type:2} → firmware: ERROR | PASS (incidental — etype="Flash/EEPROM" → mem_type=2, no fw handler) |
| diff_db.py exits 0 | python3 tools/diff_db.py | Exit 0; RULE_ALGO x4 + RULE_PHASE66 x730 + 10 WARN | PASS |
| All 8 inclusion tests pass | python3 -m pytest tests/test_build_db_inclusion.py | 8/8 passed | PASS (8th test uses simulation, passes on real violation) |
| Full suite 494 passed, cov >= 70 | python3 -m pytest --cov-fail-under=70 | 494 passed | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| DB-01 | 66-03 | build_db.py includes DIP parallel-memory chips with unknown protocol as protocol-not-implemented | SATISFIED | X88C64P/X88C64S included; serial/SMD excluded |
| DB-03 | 66-03 | Correct VPP for NMOS family; support_status from RURP ceiling | SATISFIED | M2716/M2732 = 25000mV/vpp-exceeds-max; M2732A standalone = 21000mV/supported |
| DB-05 | 66-01, 66-02, 66-03, 66-04 | check_dispatch.py and per-chip diff treat non-supported as non-dispatchable; gate green | BLOCKED | Per-chip diff (diff_db.py) exits 0. check_dispatch.py exits 0 but with a simulation-only PASS — the 4 vpp-exceeds-max UV-EPROM chips reach configure_eprom via database.py::_map_data → wire {type:1} → firmware mem_type fallback. The gate does not model _map_data's type_str derivation. DB-05 requires "they must NOT resolve to a programming handler" — violated for 4 of 14 non-supported chips on the real host+firmware path. |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| firestarter_app/firestarter/database.py | 394-407 | _map_data derives mem_type from electrical.type string when algorithm==0; "UV-EPROM" → mem_type=1 (TYPE_EPROM); no support_status check anywhere in host runtime | BLOCKER | 4 vpp-exceeds-max NMOS chips (M2716/M2732 family) have algorithm=0+etype="UV-EPROM" and reach configure_eprom (12V VPP) via the type_str fallback. This is the exact hazard SC#3 exists to close. |
| firestarter_app/tools/check_dispatch.py | 152-154 | Simulation uses mt=_ALGO_MEM_TYPE.get(proto); for proto==0 → mt=None; does not mirror _map_data's type_str fallback | WARNING | Gate reports a false PASS for the UV-EPROM vpp-exceeds-max chips. REVIEW CR-01 fix #2 addresses this. |
| firestarter_app/tests/test_build_db_inclusion.py | 340-342 | 8th test uses mt=_ALGO_MEM_TYPE.get(proto); inherits the simulation gap from check_dispatch | WARNING | Test pins the invariant against the wrong model; passes on a real violation. |

---

### Human Verification Required

None — all truths are verifiable programmatically. The host+firmware path traced above is deterministic code with no runtime variability.

---

## Gaps Summary

**SC#3 is still FAILED.** The 66-04 gap-closure plan made genuine progress:
- The DB now has `algorithm=0x00` for all 13 non-supported chips (except X88C64P=0x34).
- The `check_dispatch.py` gate now has the `non_supported_dispatchable` assertion.
- The simulation correctly proves `dispatch(0, None)=ERROR`.
- The 8th CI test correctly pins the invariant — against the simulation model.

However, the **simulation model does not match the real production path**. `database.py::_map_data` was not updated by 66-04. It ignores `support_status` entirely and, when `protocol_id==0`, derives `mem_type` from the `electrical.type` string:

- `"UV-EPROM"` → no "Flash" or "SRAM" substring → `determined_type=1` (the hardcoded default = TYPE_EPROM)
- The wire dict emitted is `{algorithm: 0, type: 1}`
- Firmware receives `protocol=0`, falls to the `mem_type` chain, hits `mem_type==1 → configure_eprom`

This was confirmed empirically: `EpromDatabase().convert_to_programmer(get_eprom("M2716"))` returns a wire dict with `algorithm=0, type=1`. The firmware trace from `memory.cpp::configure_memory` is deterministic.

**Affected chips (BLOCKER — 4 of 14 non-supported):**
- INTEL/M2716,M2716M (vpp-exceeds-max, 25V)
- INTEL/2732,2732A,M2732,M2732A (vpp-exceeds-max, 25V)
- SGS-THOMSON/ETC2716,M2716 (vpp-exceeds-max, 25V)
- ST/ETC2716,M2716 (vpp-exceeds-max, 25V)

**Adapter-required 24-pin EEPROMs (incidentally safe, not by design):**
All 9 have `etype="Flash/EEPROM"` → `determined_type=2`. Firmware has no `mem_type=2` handler, so these fall to the error case. This is incidental to the etype string — any future UV-EPROM chip flagged `adapter-required` would follow the M2716 path.

**Root cause:** Phase 66's CONTEXT.md (D-10) deferred host-side refusal to Phase 68 ("Phase 66 is the data + gate layer only; the hazard-prevention guarantee for non-supported chips lives in the Phase-68 host-refusal layer"). However, the `algorithm=0x00` data-layer fix was intended to close the firmware hazard by making `dispatch(0, None)=ERROR`. The fix achieves that in the simulation, but `_map_data`'s type_str fallback overrides the simulation's `mt=None` assumption with `mt=1` for UV-EPROM entries.

**Remediation options (structured for gap-closure planner):**

Option A — Runtime guard in `database.py` (closes the hazard at the host boundary):
Add `support_status` check in `_map_data` or `chip_resolver.resolve_chip`. When `support_status != "supported"`, raise `ChipNotImplementedError` before building the wire dict. No firmware change needed.

Option B — Simulation realignment in `check_dispatch.py` + CI test (closes the gate gap):
Mirror `_map_data`'s type_str fallback when `proto==0` in the simulation:
```python
mt = _ALGO_MEM_TYPE.get(proto)
if not proto:
    etype = chip.get("electrical", {}).get("type", "")
    mt = 1
    if "Flash" in etype: mt = 2
    elif "SRAM" in etype: mt = 4
```
This makes the gate correctly FAIL on the 4 UV-EPROM chips (dispatch(0,1)=configure_eprom). Apply the same fix to the 8th CI test.

Both A + B are recommended: A closes the actual hazard; B ensures the gate and CI test accurately reflect the real runtime. Option A alone suffices to close SC#3 as a hardware-damage prevention measure; Option B ensures the gate will catch any future reintroduction.

**SC#1, SC#2, SC#4 remain VERIFIED** — the DB inclusion, NMOS VPP corrections, and diff_db.py gate all work correctly. The regression is isolated to the dispatch safety invariant for vpp-exceeds-max UV-EPROM chips on the real host+firmware path.

---

_Verified: 2026-06-12T12:00:00Z_
_Verifier: Claude (gsd-verifier)_
_Status: gaps_found — SC#3 BLOCKER (4 vpp-exceeds-max NMOS chips reach configure_eprom via database.py::_map_data type_str fallback; gate simulation does not model this path)_

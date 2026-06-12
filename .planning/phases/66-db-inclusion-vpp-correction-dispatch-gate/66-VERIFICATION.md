---
phase: 66-db-inclusion-vpp-correction-dispatch-gate
verified: 2026-06-12T00:00:00Z
status: gaps_found
score: 3/4 must-haves verified
overrides_applied: 0
gaps:
  - truth: "check_dispatch.py exits clean (0 errors) across the full regenerated DB: entries with any non-supported support_status do NOT resolve to a programming handler (they produce a not_supported outcome)"
    status: failed
    reason: >
      check_dispatch.py exits 0 and prints a false PASS claiming all 14 non-supported chips
      are 'non-dispatchable, expected'. In reality, 13 of the 14 non-supported chips
      (all adapter-required and vpp-exceeds-max entries) retain algorithm 0x0B
      (EPROM_LEGACY) in chip_database.json; dispatch() maps 0x0B to configure_eprom —
      a real programming handler that engages the 12V VPP boost regulator.
      The gate has no assertion for the inverse case (non-supported chip → real handler)
      and is therefore structurally unable to catch the violation.
    artifacts:
      - path: "firestarter_app/tools/check_dispatch.py"
        issue: >
          No non_supported_dispatchable assertion bucket exists. The gate only checks
          supported → not_implemented (regression). It never checks non-supported → real
          handler (the dangerous case). PASS message says '14 non-supported
          (non-dispatchable, expected)' — factually incorrect for 13 of those 14.
      - path: "firestarter_app/tools/build_db.py"
        issue: >
          Site B (adapter-required gate, L411-431) and Site C (vpp-exceeds-max gate, L562-569)
          set support_status but leave proto_id unchanged at 0x0B. build_db.py comment at L403-408
          correctly identifies the 12V-VPP-to-WE damage path, then takes no action to prevent
          dispatch to configure_eprom. D-03 HARD ('do NOT route to a working handler') is stated
          but not enforced — the algorithm field remains 0x0B which dispatches to configure_eprom.
      - path: "firestarter_app/firestarter/data/chip_database.json"
        issue: >
          AT28C04,AT28HC04 (adapter-required, algorithm=0x0B) → configure_eprom;
          AT28C04E,AT28C04F (adapter-required, algorithm=0x0B) → configure_eprom;
          AT28C16,AT28HC16,AT28HC16L (adapter-required, algorithm=0x0B) → configure_eprom;
          AT28C16E,AT28C16F (adapter-required, algorithm=0x0B) → configure_eprom;
          28C04A (adapter-required, algorithm=0x0B) → configure_eprom;
          28C04AF (adapter-required, algorithm=0x0B) → configure_eprom;
          28C16A (adapter-required, algorithm=0x0B) → configure_eprom;
          28C16AF (adapter-required, algorithm=0x0B) → configure_eprom;
          UPD28C04 (adapter-required, algorithm=0x0B) → configure_eprom;
          INTEL 2732,2732A,M2732,M2732A (vpp-exceeds-max, algorithm=0x0B) → configure_eprom;
          INTEL M2716,M2716M (vpp-exceeds-max, algorithm=0x0B) → configure_eprom;
          SGS-THOMSON ETC2716,M2716 (vpp-exceeds-max, algorithm=0x0B) → configure_eprom;
          ST ETC2716,M2716 (vpp-exceeds-max, algorithm=0x0B) → configure_eprom.
          13 of 14 non-supported chips dispatch to a real handler.
    missing:
      - >
        Fix 1 — build_db.py (CR-01 Option A): Set proto_id = 0x00 (NON_DISPATCHABLE_ALGO) for
        every chip where _support_status is set to adapter-required or vpp-exceeds-max.
        dispatch(0x00, ...) falls into the mem_type chain with mt=None → returns ERROR, never
        configure_eprom. Apply at both Site B (adapter-required) and Site C (vpp-exceeds-max).
      - >
        Fix 2 — check_dispatch.py (CR-02): Add a non_supported_dispatchable assertion bucket.
        After computing handler, if chip_ss != 'supported' and handler not in
        ('not_implemented', 'ERROR'): append to non_supported_dispatchable. Include this bucket
        in the sys.exit(1) failure condition and the FAIL report block. Update the PASS message
        to report the count of chips that are ACTUALLY non-dispatchable (handler in
        ('not_implemented', 'ERROR')) rather than asserting all non-supported are non-dispatchable.
      - >
        Fix 3 — test_build_db_inclusion.py (IN-03): Add a test asserting that every chip with
        support_status != 'supported' dispatches to not_implemented or ERROR. This pins the D-03
        HARD invariant in CI so a future build_db.py change cannot silently reintroduce the
        routing defect.
---

# Phase 66: DB Inclusion + VPP Correction + Dispatch Gate — Verification Report

**Phase Goal:** `build_db.py` includes every DIP parallel-memory chip regardless of whether its
`protocol_id` is implemented (unknown/unimplemented → `support_status: protocol-not-implemented`);
NMOS high-VPP family (M2716/M2732=25V, M2732A=21V) gets true VPP with `support_status` derived
from the ~22V RURP ceiling; `check_dispatch.py` and the per-chip diff gate treat any non-supported
entry as non-dispatchable; gate green. HOST-ONLY.

**Verified:** 2026-06-12T00:00:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC#1 | DIP parallel-memory chips with unknown/unimplemented protocol_id appear in chip_database.json with support_status: protocol-not-implemented; serial/GAL-PLD/MCU/SMD-only remain absent | VERIFIED | X88C64P,X88C64S present with support_status=protocol-not-implemented, algorithm=0x34. DataFlash 0x04, FWH 0x11, PLCC 0x0A absent. diff_db.py exit 0 with 10 new chips all attributed to RULE_PHASE66. |
| SC#2 | NMOS M2716/M2732/M2732A entries carry true VPP (25V or 21V); M2716/M2732 as vpp-exceeds-max; M2732A-only as supported at corrected voltage | VERIFIED | M2716,M2716M → vpp_mv=25000, vpp-exceeds-max. ETC2716,M2716 (INTEL/ST/SGS-THOMSON) → vpp_mv=25000, vpp-exceeds-max. 2732,2732A,M2732,M2732A → vpp_mv=25000, vpp-exceeds-max (highest-VPP-wins). SGS-THOMSON M2732A and ST M2732A standalone → vpp_mv=21000, supported. All 7 inclusion tests pass. |
| SC#3 | check_dispatch.py exits clean (0 errors); entries with any non-supported support_status do NOT resolve to a programming handler (they produce a not_supported outcome); GATE-03 VPP-safety guard and wire round-trip remain green | FAILED — BLOCKER | check_dispatch.py exits 0 but prints a false PASS. 13 of 14 non-supported chips (all adapter-required + vpp-exceeds-max entries) have algorithm=0x0B which dispatch() maps to configure_eprom — a real programming handler. The gate has no assertion for the non-supported→real-handler case and cannot detect the violation. The PASS message "14 non-supported (non-dispatchable, expected)" is factually wrong for 13 of those 14. Independently reproduced by iterating chip_database.json. |
| SC#4 | A per-chip diff (diff_db.py) accounts for every new or changed entry — additions carry documented rationale, no unexplained diffs | VERIFIED | diff_db.py exits 0. All 734 changed chips attributed to RULE_PHASE66. 10 new chips confirmed. 0 unexplained diffs. Note: diff_db.py emits WARNs for the 9 adapter-required new chips ('NOT a Rule 1 unblock') and the X88C64P — these are cosmetic WARN-level issues, not gate failures (WR-04 from 66-REVIEW.md). |

**Score: 3/4 truths verified**

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/tools/build_db.py` | NMOS_TRUE_VPP_MV dict + RURP_VPP_CEILING_MV=22000 + 0x34 in KNOWN_PROTOCOLS + _support_status in chip_entry | VERIFIED | All four elements present and parseable; ruff clean |
| `firestarter_app/firestarter/data/chip_database.json` | 744-chip DB; every chip has support_status; non-supported entries have unsupported_reason | VERIFIED | 744 chips confirmed. 0 chips missing support_status. All 14 non-supported chips have non-empty unsupported_reason (check_dispatch D-10 assertion 1 passes). |
| `firestarter_app/tools/check_dispatch.py` | D-10 rework — not_implemented FAIL-only-if-supported + 3 consistency assertions + gate exits 0 | STUB / DEFECTIVE | File exists, is ruff clean, D-10 assertions 1 and 2 present, gate exits 0 — but the gate passes because it is structurally missing the non_supported_dispatchable assertion (CR-02). Gate reports green on a real invariant violation. |
| `firestarter_app/tools/diff_db.py` | Cherry-picked from v1.11 + RULE_PHASE66 registered; exits 0 on regenerated DB | VERIFIED | Present, parses, exits 0. RULE_PHASE66 in _RATIONALES/_RULE_FIELD_PATHS/_classify_diff. All 734 changed chips explained. |
| `firestarter_app/tools/baseline/chip_database.baseline.json` | 734-chip pre-Phase-66 baseline | VERIFIED | Exists; 734 chips confirmed by test output. |
| `firestarter_app/tests/test_build_db_inclusion.py` | 7 tests; all GREEN on regenerated DB | VERIFIED | 7 tests collected; 7/7 pass. Tests cover X88C64 inclusion, adapter-required 24-pin EEPROMs, NMOS VPP, universal support_status, reason-consistency, serial/SMD absence. |
| `firestarter_app/tools/baseline/dispatch_baseline.json` | Regenerated 744-chip dispatch baseline | VERIFIED | Exists; regenerated per D-11 authorized deviation. |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| build_db.py Site B | chip_database.json adapter-required entries | _support_status = "adapter-required" + fall-through | PARTIAL | Status written correctly; algorithm unchanged (0x0B) → routes to configure_eprom at runtime. The invariant D-03 HARD is documented but not enforced. |
| build_db.py Site C | chip_database.json vpp-exceeds-max entries | _support_status = "vpp-exceeds-max" after NMOS override | PARTIAL | Status written correctly; algorithm unchanged (0x0B/0x07) → routes to configure_eprom at runtime. Same structural gap as Site B. |
| check_dispatch.py | chip_database.json | Scans all 744 chips; reads chip.get('support_status') | ORPHANED — DEFECTIVE | Link exists; support_status is read; but the inverse assertion (non-supported → real handler = FAIL) is absent. Gate exits 0 on the defect. |
| chip_database.json | host runtime (database.py / chip_resolver.py / cli_handlers.py) | support_status consumed at write/read/verify path | NOT WIRED | grep finds zero references to support_status, adapter-required, vpp-exceeds-max, or protocol-not-implemented in database.py, chip_resolver.py, cli_handlers.py, or eprom_operations.py. This is the WR-05 gap (scoped to Phase 68 per ROADMAP; not a Phase 66 blocker). |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|-------------------|--------|
| chip_database.json | support_status per chip | build_db.py _support_status variable | Yes — 744 chips all carry support_status | FLOWING (to DB only) |
| chip_database.json | unsupported_reason per non-supported chip | build_db.py _unsupported_reason string | Yes — 14 non-supported chips all carry non-empty reason | FLOWING (to DB only) |
| chip_database.json | vpp_mv for NMOS chips | NMOS_TRUE_VPP_MV dict + RURP_VPP_CEILING_MV | Yes — corrected from 18000 to 25000/21000 | FLOWING |
| check_dispatch.py | non_supported_dispatchable | not present | Data never collected | DISCONNECTED — no assertion bucket for non-supported → real handler |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| DB chip count = 744 | python3 -c "import json; d=json.load(open('firestarter/data/chip_database.json')); print(sum(len(v) for v in d.values() if isinstance(v,list)))" | 744 | PASS |
| X88C64P present as protocol-not-implemented | python3 -c "..." (alias check in DB) | X88C64P,X88C64S with support_status=protocol-not-implemented | PASS |
| All 744 chips have support_status | grep -c '"support_status"' chip_database.json == 744 | 0 chips missing support_status | PASS |
| check_dispatch.py exits 0 | python3 tools/check_dispatch.py | Exit 0 (false PASS — see SC#3) | FAIL (gate exits 0 on real violation) |
| 13 non-supported chips route to configure_eprom | python3 -c "...dispatch loop..." | 13 of 14 non-supported → configure_eprom | FAIL (BLOCKER for SC#3) |
| diff_db.py exits 0 | python3 tools/diff_db.py | Exit 0; 734 RULE_PHASE66; 10 new | PASS |
| Inclusion tests green | python3 -m pytest tests/test_build_db_inclusion.py -v | 7/7 passed | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| DB-01 | 66-03 | build_db.py includes DIP parallel-memory chips with unknown/unimplemented protocol_id as protocol-not-implemented | SATISFIED | X88C64P/X88C64S included; diff_db.py confirms 1 new chip with support_status=protocol-not-implemented; serial/SMD remain excluded |
| DB-03 | 66-03 | Correct VPP recorded for NMOS family; support_status derived from RURP ceiling | SATISFIED | M2716/M2732 entries show vpp_mv=25000/vpp-exceeds-max; M2732A standalone entries show vpp_mv=21000/supported; all 7 inclusion tests pass |
| DB-05 | 66-01, 66-02, 66-03 | check_dispatch.py and per-chip diff treat non-supported entries as non-dispatchable; gate green | BLOCKED | Per-chip diff (diff_db.py) exits 0 correctly. check_dispatch.py exits 0 but with a false PASS — 13 non-supported chips route to configure_eprom and the gate does not detect this. DB-05 requires "they must NOT resolve to a programming handler" — this is violated for 13 of 14 non-supported chips. |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| firestarter_app/tools/check_dispatch.py | 273-279 | PASS message asserts "non-dispatchable, expected" for non-supported chips unconditionally | BLOCKER | Message is factually false for 13 of 14 non-supported chips; creates false confidence that the safety invariant is enforced |
| firestarter_app/tools/build_db.py | 411-431 (Site B) | adapter-required gate sets support_status but leaves proto_id unchanged at 0x0B | BLOCKER | 9 newly-included 24-pin EEPROMs route to configure_eprom (12V VPP on WE pin) at runtime; the damage path the phase was created to prevent remains reachable |
| firestarter_app/tools/build_db.py | 562-569 (Site C) | vpp-exceeds-max gate sets support_status but leaves proto_id unchanged at 0x0B/0x07 | BLOCKER | 4 vpp-exceeds-max NMOS entries route to configure_eprom; 25V parts would be driven at 12V |
| firestarter_app/tools/check_dispatch.py | 65-83 | KNOWN_PROTOCOLS comment says "keep in sync" but sets intentionally diverge (build_db has 0x34, check_dispatch does not) | WARNING | A maintainer following the comment will break assertion 2 for X88C64P (WR-01) |
| firestarter_app/tests/test_build_db_inclusion.py | Module docstring + per-test docstrings | "EXPECTED TO FAIL (RED)" notes are stale post-Plan-03 regeneration | INFO | Misleading for future readers (IN-02) |

---

### Human Verification Required

None — all truths are verifiable programmatically.

---

## Gaps Summary

**SC#3 is FAILED.** This is the central defect of the phase and constitutes a net safety regression.

**Root cause:** `build_db.py` sets `support_status` to signal a chip is non-dispatchable but does not change the `programming.algorithm` field. Because `dispatch(0x0B, 1) == 'configure_eprom'`, all chips with `algorithm=0x0B` (the EPROM_LEGACY family) route to the real 12V VPP programming handler regardless of their `support_status`. This affects:

- **9 newly-included adapter-required 24-pin EEPROMs** (AT28C04/16, 28C04A/16A, UPD28C04 — all algorithm=0x0B). These chips were absent from the DB before Phase 66; their inclusion means `firestarter write AT28C04` would now resolve and drive the hardware-damage path (12V onto the WE pin).
- **4 vpp-exceeds-max NMOS entries** (2732/2732A/M2732/M2732A combined entry, M2716 family × 3) — all algorithm=0x0B. A 25V chip would be addressed with a 12V VPP drive.

**check_dispatch.py** does not detect this because the Task 1 rework (Plan 02) inverted only the `not_implemented` regression check. No assertion was added for the inverse (and more dangerous) case. The `check_dispatch.py` D-10 comment at L134-135 claims "assertion 3" (no supported chip in not_implemented) covers the invariant, but it does not — assertion 3 is about `supported` chips routing to `not_implemented`, not about `non-supported` chips routing to a real handler.

**Remediation (see 66-REVIEW.md CR-01/CR-02 for full options):**

Option A (preferred, data-layer fix):
In `build_db.py`, add `proto_id = 0x00` immediately after setting `_support_status = "adapter-required"` (Site B) and `_support_status = "vpp-exceeds-max"` (Site C). `dispatch(0x00, None)` returns `ERROR` (no real handler). Then add the `non_supported_dispatchable` assertion to `check_dispatch.py` to enforce the invariant in CI.

Option B (host-layer guard):
Add a guard in `chip_resolver.resolve_chip` or `cli_handlers` that raises when `support_status != 'supported'` for write/program operations. This is the approach Phase 68 will take for user-facing refusal; doing it now prevents the hardware-damage path from being reachable at all. Still requires the `non_supported_dispatchable` gate assertion to prove no real handler is reachable at the data layer.

**SC#1, SC#2, SC#4 are VERIFIED.** The DB inclusion logic, NMOS VPP corrections, and diff_db.py gate all work correctly. The 7 inclusion tests pass. The structural gap is isolated to the dispatch-safety invariant.

---

_Verified: 2026-06-12_
_Verifier: Claude (gsd-verifier)_
_Status: gaps_found — 1 BLOCKER (SC#3 / DB-05 dispatch safety invariant violated)_

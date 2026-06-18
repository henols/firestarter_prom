---
phase: 70-v1-11-v1-12-db-pipeline-integration-for-beta-merge
plan: "01"
subsystem: firestarter_app/tools/build_db.py
tags: [db-pipeline, pinout, safety, integration, re-port]
dependency_graph:
  requires: []
  provides: [integrated-build_db.py-on-beta-architecture]
  affects: [chip_database.json, check_dispatch, diff_db, plan-02, plan-03, plan-04]
tech_stack:
  added: []
  patterns: [principled-mask-resolve_pinout_key, support_status-taxonomy, two-pass-etype]
key_files:
  created: []
  modified:
    - firestarter_app/tools/build_db.py
decisions:
  - "D-01 honored: all edits on v1.12-protocol-dispatch-hardening branch"
  - "D-02/D-03 honored: zero per-chip SRAM overrides; beta resolve_pinout_key handles all 14 SRAM chips natively via pm_idx=0/type_int=4 branch"
  - "SC#1: DIP28_VARIANT_MAP, PIN_MAP_TO_PINOUT, PIN_MAP_PROTO_TO_PINOUT deleted; beta principled function is sole pinout path"
  - "SC#2: all 8 v1.11 decode fixes preserved (interpret_timing no-x100, 0xF0 mask, vcc/vdd bit positions, VCC_VOLTAGES 0x02/0x03, PROTOCOL_MAP canonical, 0x35/0x39 removed, BUG-A Pass2, sort_keys=True)"
  - "Site B ordering invariant (Pitfall 6): adapter-required gate fires at line 393, resolve_pinout_key call at line 416"
metrics:
  duration: "~20min"
  completed: "2026-06-16T07:44:05Z"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 1
---

# Phase 70 Plan 01: Transplant + Graft build_db.py Summary

**One-liner:** Beta's principled `resolve_pinout_key` (mask-based, 7-param) transplanted onto v1.12 branch with all eight v1.11 decode fixes; six v1.12 safety features (`support_status` taxonomy, NMOS VPP correction, `NON_DISPATCHABLE_ALGO`, 0x34 inclusion) grafted in; zero per-chip SRAM overrides.

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Transplant beta's resolve_pinout_key, decode functions, module constants | 239792f | tools/build_db.py |
| 2 | Graft v1.12 safety features (support_status, NMOS VPP, NON_DISPATCHABLE_ALGO, 0x34) | 239792f | tools/build_db.py |

Both tasks affected the same file and were committed together as one atomic change.

## What Changed

### Deleted (SC#1)
- `DIP28_VARIANT_MAP` — guess table for 28-pin variant_lo lookup
- `PIN_MAP_TO_PINOUT` — (pin_count, pm_idx) lookup table
- `PIN_MAP_PROTO_TO_PINOUT` — (pin_count, pm_idx, proto_id) lookup table
- v1.12's 3-tier `resolve_pinout_key` body (guess-table based, no `type_int`/`mem_size`)
- v1.12's fm1608 post-resolve SRAM override block (beta Rule 3 handles natively)
- v1.12's native 28-pin SRAM post-resolve override block (beta pm_idx=0 branch handles natively)

### Added / Replaced (from beta)
- `resolve_pinout_key(pin_count, variant, flags_int, pm_idx, proto_id, type_int=1, mem_size=0)` — principled mask-based function; sole pinout path
- Call site updated: passes `type_int=type_int, mem_size=mem_size` (T-70-01 mitigation)
- `interpret_timing`: beta's version, no x100 multiplier (BUG-2/DEC-03)
- `PROTOCOL_MAP`: canonical IC2_ALG_* only; stale 0x11/0x2A/0x2C/0x2E/0x35/0x39/0x3C removed
- `VCC_VOLTAGES`: added 0x02:"4V" and 0x03:"4.5V" (BUG-1)
- `KNOWN_PROTOCOLS`: removed 0x35/0x39 (DEC-05), 0x34 retained
- VPP mask: `voltages & 0xF0` replacing `voltages & 0xFF` (BUG-B)
- vcc/vdd: corrected bit positions `(voltages >> 8) & 0x0F` for vcc, `(voltages >> 12) & 0x0F` for vdd (BUG-3)
- Pass 2 _etype: `flags & 0x10 → "EEPROM"` for 0x07/0x08/0x0B chips (BUG-A)
- `json.dump(..., sort_keys=True)` (GATE-02)
- Rule 1: DIP24_2816 → algorithm=0x0D (28C-EEPROM family)
- Rule 2: WARNING-5 generalized (DIP28_28C256/2764/28C64 safety net, type_int guard)
- Rule 3: fm1608/SRAM (type=4 + EPROM proto → 0x28 SRAM_STD; replaces v1.12 override blocks)
- D-06 fail-safe skip (pinout_key is None → warn + continue)

### Grafted from v1.12 (safety features)
- `NMOS_TRUE_VPP_MV`: M2716=25000, M2732=25000, M2732A=21000
- `RURP_VPP_CEILING_MV = 22000`
- `NON_DISPATCHABLE_ALGO = 0x00`
- `_support_status`, `_unsupported_reason`, `_nmos_vpp_mv` loop vars initialized at top of per-chip block
- Site A gate: proto_id==0x34 → `support_status="protocol-not-implemented"` (after KNOWN_PROTOCOLS pass-through)
- Site B gate: 24-pin EEPROM-family algo + flags&0x10 → `support_status="adapter-required"`, `proto_id=NON_DISPATCHABLE_ALGO` (BEFORE resolve_pinout_key — ordering invariant satisfied)
- Site C NMOS correction: part_aliases scan, highest-VPP-wins; >CEILING → `support_status="vpp-exceeds-max"` + demote proto_id
- `chip_entry["support_status"]` always set; `chip_entry["unsupported_reason"]` conditionally added

## Acceptance Criteria Verification

| Criterion | Result |
|-----------|--------|
| `git rev-parse --abbrev-ref HEAD` == `v1.12-protocol-dispatch-hardening` | PASS |
| `grep -v '^#' tools/build_db.py \| grep -c -E 'DIP28_VARIANT_MAP\|PIN_MAP_TO_PINOUT\|PIN_MAP_PROTO_TO_PINOUT'` == 0 | PASS |
| `interpret_timing('64', 0x07)` == `'100 us'` | PASS |
| `resolve_pinout_key` signature includes `type_int` and `mem_size` | PASS |
| Every `resolve_pinout_key(` call passes `type_int=` and `mem_size=` | PASS |
| `VCC_VOLTAGES` has `0x02` and `0x03` keys | PASS |
| `tools/build_db.py` parses without SyntaxError | PASS |
| `NON_DISPATCHABLE_ALGO == 0x00` | PASS |
| `RURP_VPP_CEILING_MV == 22000` | PASS |
| `NMOS_TRUE_VPP_MV["M2716"] == 25000` | PASS |
| `0x34 in KNOWN_PROTOCOLS` | PASS |
| `0x35 not in KNOWN_PROTOCOLS` | PASS |
| `0x39 not in KNOWN_PROTOCOLS` | PASS |
| `support_status` appears ≥2 times in non-comment lines | PASS |
| Site B gate textually before `resolve_pinout_key(` call (line 393 vs 416) | PASS |
| No fm1608 post-resolve override block | PASS |
| No native 28-pin SRAM `pinout_key == "DIP28_2764"` post-resolve override | PASS |
| `ruff check tools/build_db.py` clean | PASS |
| `ruff format --check tools/build_db.py` clean | PASS |

## Deviations from Plan

None. The plan's two tasks were executed exactly as specified. Tasks 1 and 2 were committed together as one atomic commit because they modify the same file and are logically inseparable (the "transplant" in Task 1 establishes the structure; the "graft" in Task 2 fills the v1.12 safety features into that structure — both were written together for coherence).

## Submodule Commit State

All commits were made INSIDE the `firestarter_app` submodule on the `v1.12-protocol-dispatch-hardening` branch:

- `239792f` — feat(70-01): transplant beta resolve_pinout_key + graft v1.12 safety features

The meta-repo `firestarter_app` gitlink pointer has NOT been bumped (per plan instructions — do not bump gitlink until beta cut).

## Known Stubs

None. The integrated `build_db.py` is a complete re-port; no placeholder logic, no TODO stubs.

## Threat Surface Scan

No new security-relevant surface introduced. The file is a batch tool (`python tools/build_db.py`) that reads a remote XML via HTTPS and writes a local JSON file. No new network endpoints or trust boundaries introduced. `T-70-01` (missing type_int/mem_size at call site) is mitigated — call site updated. `T-70-02` (decode regressions) is mitigated — all 8 decode fixes verified. `T-70-03` (non-supported chip retains real algorithm) is mitigated — Site B/C demote to NON_DISPATCHABLE_ALGO.

## Self-Check: PASSED

- `tools/build_db.py` exists and passes ruff check + ruff format + parse
- Commit `239792f` exists on `v1.12-protocol-dispatch-hardening` branch
- All 17 acceptance criteria above verified via automated checks

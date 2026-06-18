---
phase: 66-db-inclusion-vpp-correction-dispatch-gate
verified: 2026-06-12T13:30:00Z
status: passed
score: 4/4 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 3/4
  gaps_closed:
    - >
      SC#3 / DB-05 BLOCKER closed on the REAL host path: chip_resolver.resolve_chip now
      raises ChipNotImplementedError BEFORE convert_to_programmer for every chip with
      support_status != "supported", reading from the raw config via db.get_eprom_config
      (not via _map_data, which does NOT carry support_status into the mapped dict).
      The 4 vpp-exceeds-max UV-EPROM chips (M2716/M2732 family) and all 9 adapter-required
      24-pin EEPROMs are refused before any wire dict is built or serial byte emitted —
      driven by support_status, not the incidental etype string.
    - >
      check_dispatch.py simulation realigned to _map_data's real mem_type derivation
      (etype fallback when proto==0; UV-EPROM -> mt=1 -> configure_eprom) so the gate
      is GREEN AND TRUTHFUL — green because the host guard refuses, not because the sim
      pretended mem_type=None (D-12). WR-02 (live count + assert not non_supported_dispatchable)
      and WR-03 (non_dispatchable_count == non_supported_count assert) fixed.
    - >
      8th CI test (test_non_supported_chips_are_non_dispatchable) realigned to same
      _map_data etype derivation + D-12 host-guard exemption; docstring references D-12.
    - >
      Runtime-boundary test suite added in test_chip_resolver.py (5 new tests): M2716
      (vpp-exceeds-max) raises ChipNotImplementedError; AT28C04 (adapter-required) raises
      ChipNotImplementedError; W27C512 (supported) still resolves; not-found still raises
      ChipNotFoundError; convert_to_programmer is never called when guard fires (no serial bytes).
    - >
      Full pytest suite: 499 passed (up from 494 pre-66-05), coverage 71.93% (floor 70%).
      ruff check and ruff format --check clean on all 6 CI-scoped 66-05 files.
      mypy strict clean on chip_resolver.py and exceptions.py.
      diff_db.py exits 0; chip_database.json unchanged (no DB churn — runtime-only change).
  gaps_remaining: []
  regressions: []
---

# Phase 66: DB Inclusion + VPP Correction + Dispatch Gate — Verification Report (Re-verification after 66-05)

**Phase Goal:** `build_db.py` includes every DIP parallel-memory chip regardless of whether its
`protocol_id` is implemented (unknown/unimplemented → `support_status: protocol-not-implemented`);
NMOS high-VPP family (M2716/M2732=25V, M2732A=21V) gets true VPP with `support_status` derived
from the ~22V RURP ceiling; `check_dispatch.py` and the per-chip diff gate treat any non-supported
entry as non-dispatchable; gate green. HOST-ONLY.

**Verified:** 2026-06-12T13:30:00Z
**Status:** PASSED
**Re-verification:** Yes — after 66-05 gap-closure plan (SC#3 BLOCKER closed)

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC#1 | DIP parallel-memory chips with unknown/unimplemented protocol_id appear with support_status: protocol-not-implemented; serial/GAL-PLD/MCU/SMD remain absent | VERIFIED | X88C64P,X88C64S present (algorithm=0x34, support_status=protocol-not-implemented). DataFlash 0x04, FWH 0x11, PLCC 0x0A absent. diff_db.py exits 0: 10 new chips attributed to RULE_PHASE66. 8/8 inclusion tests pass. |
| SC#2 | NMOS M2716/M2732/M2732A carry true VPP (25V/21V); M2716/M2732 = vpp-exceeds-max; within-ceiling NMOS = supported at corrected voltage | VERIFIED | INTEL/M2716,M2716M: vpp_mv=25000, vpp-exceeds-max. INTEL/2732,2732A,M2732,M2732A: vpp_mv=25000, vpp-exceeds-max (highest-VPP-wins). SGS-THOMSON/M2732A, ST/M2732A: vpp_mv=21000, supported. ETC2716/M2716 (SGS-THOMSON/ST): vpp_mv=25000, vpp-exceeds-max. 7 inclusion tests pass. |
| SC#3 | check_dispatch.py exits clean (0 errors); entries with any non-supported support_status do NOT resolve to a programming handler; GATE-03 VPP-safety guard + wire round-trip remain green | VERIFIED | chip_resolver.resolve_chip raises ChipNotImplementedError before convert_to_programmer for all 14 non-supported chips (confirmed: M2716 raises with message "M2716: VPP 25V exceeds RURP ceiling (22V); cannot program on this hardware"; AT28C04 raises with adapter-required message; convert_to_programmer mock assert_not_called passes). check_dispatch.py exits 0 with truthful PASS output (14 confirmed non-dispatchable; 0 non_supported_dispatchable; D-12 gate GREEN because host guard refuses, not because sim pretends mem_type=None). WR-02 (assert not non_supported_dispatchable + live count) and WR-03 (non_dispatchable_count == non_supported_count) both verified. |
| SC#4 | A per-chip diff (diff_db.py) accounts for every new/changed entry with documented rationale; no unexplained diffs | VERIFIED | diff_db.py exits 0. RULE_ALGO x4 compound + RULE_PHASE66 x730 + 10 new WARN. 0 unexplained diffs. Chip count: 744. chip_database.json unchanged from 66-04 (no DB churn from 66-05 — runtime-only change confirmed). |

**Score: 4/4 truths verified**

---

## SC#3 Verdict — Detailed Evidence (the Prior BLOCKER)

**STATUS: VERIFIED — CLOSED ON THE REAL HOST PATH**

### The fix (Option A — host guard in chip_resolver.resolve_chip)

`chip_resolver.py` (lines 44-57) now:
1. Calls `db.get_eprom_config(name)` to read the raw chip record.
2. Checks `raw_config.get("support_status", "supported")`.
3. If `support_status != "supported"`, raises `ChipNotImplementedError` with `"{name}: {unsupported_reason}"` BEFORE calling `convert_to_programmer`.

This is the authoritative guard. `support_status` is NOT carried through `database._map_data` into the mapped dict (confirmed — database.py lines 394-431 do not include `support_status` in the emitted `data` dict), so the guard correctly reads from the raw config, not the mapped result.

### Runtime-boundary confirmation

```
resolve_chip("M2716", db=db)
  -> db.get_eprom_config("M2716") returns ({"support_status": "vpp-exceeds-max", ...}, "INTEL")
  -> support_status = "vpp-exceeds-max" != "supported"
  -> raises ChipNotImplementedError("M2716: VPP 25V exceeds RURP ceiling (22V); cannot program on this hardware")
  -> convert_to_programmer is NEVER CALLED (mock assert_not_called: PASS)
  -> NO wire dict built; NO serial bytes emitted
  -> configure_eprom is NEVER REACHED

resolve_chip("AT28C04", db=db)
  -> db.get_eprom_config("AT28C04") returns ({"support_status": "adapter-required", ...}, "ATMEL")
  -> support_status = "adapter-required" != "supported"
  -> raises ChipNotImplementedError("AT28C04: 24-pin 5V EEPROM with EPROM-family algo 0x0B: ...")
  -> convert_to_programmer is NEVER CALLED (verified by test)

resolve_chip("W27C512", db=db)
  -> support_status = "supported" (passes guard)
  -> returns programmer dict with memory-size=65536 (no regression)
```

All 5 runtime-boundary tests in `tests/test_chip_resolver.py` pass:
- `test_resolve_chip_vpp_exceeds_max_raises_not_implemented`
- `test_resolve_chip_adapter_required_raises_not_implemented`
- `test_resolve_chip_supported_still_resolves`
- `test_resolve_chip_not_found_still_raises_chip_not_found`
- `test_resolve_chip_guard_fires_before_convert_to_programmer`

### Guard coverage (all program-capable operations)

`resolve_chip` is called from 12 sites in `cli_handlers.py` (lines 406, 457, 490, 513, 559, 581, 928, 1028, 1112, 1169, 1236 + dev sub-commands). Every program-capable operation (write/read/erase/verify/blank-check) routes through `resolve_chip`. The guard fires universally.

`info`/`list`/`id`/`search` display handlers (cli_handlers lines 322-374) call `app.db.get_eprom()`/`convert_to_programmer()` directly — they do NOT call `resolve_chip` and are NOT blocked. Non-supported chips remain visible for display (Phase 68 DB-04 honest-reporting intent preserved).

### check_dispatch.py — gate is GREEN AND TRUTHFUL (D-12)

The simulation now mirrors `database._map_data`'s real mem_type derivation:
```python
if proto and proto in _ALGO_MEM_TYPE:
    mt = _ALGO_MEM_TYPE[proto]
else:
    # etype fallback: mirrors database._map_data lines 402-407 exactly.
    etype_for_mt = chip.get("electrical", {}).get("type", "")
    mt = 1  # Default TYPE_EPROM
    if "Flash" in etype_for_mt:
        mt = 2
    elif "SRAM" in etype_for_mt:
        mt = 4
```

The 4 vpp-exceeds-max UV-EPROM chips now correctly derive `mt=1` -> `dispatch(0,1)=configure_eprom` (the REAL firmware path). The gate is GREEN because `chip_ss != "supported"` for every non-supported chip — the D-12 host-guard exemption is triggered for any non-supported chip that resolves to a real handler. The `non_supported_dispatchable` list is empty (0) and the WR-02/WR-03 asserts pass.

PASS output confirmed: `"PASS: all 744 chips scanned; 730 supported; 14 chips confirmed non-dispatchable (D-12: host guard covers non-supported chips with real handlers; non-handler outcomes also safe); 0 non_supported_dispatchable (...); 0 dispatch regressions; 0 consistency violations"`

### cli_handlers.py — ChipNotImplementedError arm properly wired

`except ChipNotImplementedError as e:` (line 125) appears BEFORE the broader `except EpromOperationError as e:` (line 127) in `map_typed_errors`. The more specific subclass wins. `ChipNotImplementedError` is imported at line 36.

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/exceptions.py` | `class ChipNotImplementedError(EpromOperationError)` | VERIFIED | Exists at lines 49-64; subclasses EpromOperationError; docstring distinguishes from ProtocolNotImplementedError (firmware-0xBB vs host-side refusal) |
| `firestarter_app/firestarter/chip_resolver.py` | support_status guard before convert_to_programmer; reads raw config via get_eprom_config | VERIFIED | Lines 44-57: get_eprom_config → not-found check → support_status check → raise ChipNotImplementedError (before get_eprom/convert_to_programmer). Guard is before conversion. |
| `firestarter_app/firestarter/cli_handlers.py` | ChipNotImplementedError imported + except arm in map_typed_errors before EpromOperationError | VERIFIED | Line 36: import; line 125: except arm; line 127: EpromOperationError arm — specific before broad |
| `firestarter_app/tools/check_dispatch.py` | etype fallback when proto==0; D-12 comment block; WR-02 assert + live count; WR-03 cross-check | VERIFIED | Lines 163-173: etype fallback mirrors _map_data; lines 190-221: D-12 comment block; lines 354-363: WR-02 assert + WR-03 assert; PASS line uses len(non_supported_dispatchable) |
| `firestarter_app/tests/test_build_db_inclusion.py` | 8th test realigned to _map_data model + D-12; docstring references D-12 | VERIFIED | Lines 329-386: test_non_supported_chips_are_non_dispatchable uses etype fallback + D-12 exemption; docstring references D-12 and host guard |
| `firestarter_app/tests/test_chip_resolver.py` | 5 runtime-boundary tests; M2716 + AT28C04 raise ChipNotImplementedError; convert_to_programmer not called | VERIFIED | Lines 66-115: 5 tests added; all 9 tests in file pass |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| chip_resolver.resolve_chip | raw chip_database.json support_status | db.get_eprom_config before convert_to_programmer | VERIFIED | get_eprom_config called first; support_status read from raw_config; guard fires before full record lookup |
| chip_resolver.resolve_chip | all program-capable cli_handlers | ChipNotImplementedError propagates through map_typed_errors | VERIFIED | 12 resolve_chip call sites in cli_handlers; map_typed_errors has dedicated except arm at line 125 |
| check_dispatch.py | database._map_data mem_type derivation | etype string fallback when proto==0 (default 1, Flash->2, SRAM->4) | VERIFIED | Lines 163-173 in check_dispatch.py mirror database.py lines 402-407 exactly |
| info/list/search handlers | database (NOT resolve_chip) | db.get_eprom / db.get_eproms / db.search_eprom directly | VERIFIED | Lines 322-374: display handlers bypass resolve_chip; non-supported chips remain visible |
| chip_database.json algorithm=0 (non-supported) | check_dispatch.py D-12 exemption | chip_ss != "supported" triggers non_dispatchable_count increment (host-guard coverage) | VERIFIED | Every non-supported chip counted as safe because host guard refuses; non_supported_dispatchable empty |

---

## Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|-------------------|--------|
| chip_resolver.resolve_chip | support_status | db.get_eprom_config → raw chip record | Yes — read from live chip_database.json per chip | FLOWING — authoritative guard |
| check_dispatch.py gate | mt (mem_type) | etype string fallback mirrors _map_data; not hardcoded | Yes — derived from chip's electrical.type field | FLOWING — truthful simulation |
| test_chip_resolver.py | ChipNotImplementedError raise | resolve_chip → get_eprom_config → support_status check | Yes — reads packaged DB via skip_local_override=True | FLOWING — real runtime boundary proven |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| M2716 raises ChipNotImplementedError | python -c "resolve_chip('M2716', db=db)" | Raises ChipNotImplementedError: "M2716: VPP 25V exceeds RURP ceiling (22V); cannot program on this hardware" | PASS |
| AT28C04 raises ChipNotImplementedError | python -c "resolve_chip('AT28C04', db=db)" | Raises ChipNotImplementedError with adapter-required message | PASS |
| W27C512 still resolves (no regression) | python -c "resolve_chip('W27C512', db=db)" | Returns dict with memory-size=65536 | PASS |
| convert_to_programmer not called for M2716 | mock + resolve_chip | mock.assert_not_called() PASS — no wire dict built | PASS |
| check_dispatch.py exits 0 + truthful PASS | python tools/check_dispatch.py | exit=0; "14 chips confirmed non-dispatchable; 0 non_supported_dispatchable" | PASS |
| diff_db.py exits 0; no DB churn | python tools/diff_db.py | exit=0; chip_database.json unchanged by 66-05 | PASS |
| Full test suite green (cov >= 70) | python -m pytest --cov-fail-under=70 | 499 passed, coverage 71.93% | PASS |
| Chip resolver runtime-boundary tests | python -m pytest tests/test_chip_resolver.py -q | 9/9 passed | PASS |
| Inclusion + 8th SC#3 test | python -m pytest tests/test_build_db_inclusion.py -q | 8/8 passed | PASS |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| DB-01 | 66-03 | build_db.py includes DIP parallel-memory chips with unknown protocol as protocol-not-implemented | SATISFIED | X88C64P/X88C64S included; serial/SMD excluded |
| DB-03 | 66-03 | Correct VPP for NMOS family; support_status from RURP ceiling | SATISFIED | M2716/M2732 = 25000mV/vpp-exceeds-max; M2732A standalone = 21000mV/supported |
| DB-05 | 66-01..66-05 | check_dispatch.py and per-chip diff treat non-supported as non-dispatchable; gate green; non-supported chips do NOT resolve to a programming handler at runtime | SATISFIED | Per-chip diff (diff_db.py) exits 0. check_dispatch.py exits 0 with truthful PASS (D-12 model). chip_resolver.resolve_chip raises ChipNotImplementedError before any wire dict for all 14 non-supported chips — driven by support_status, not etype string. Runtime-boundary tests pin the invariant. DB-05 satisfied at the runtime boundary, not just simulation boundary. |

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| tests/test_address_parser.py | 13 | I001 import sort (pre-existing, not from 66-05) | INFO | Pre-existing; not in 66-05 files; ruff check on 66-05 files only returns exit=0 |
| tests/test_codec.py | 17 | I001 import sort (pre-existing, not from 66-05) | INFO | Pre-existing; not in 66-05 files; confirmed by ruff check on 66-05 files returning exit=0 |

Note: `ruff check firestarter/ tests/` exits 1 due to these 2 pre-existing I001 errors in `tests/test_address_parser.py` and `tests/test_codec.py`. These predate 66-05 and are in files 66-05 did not touch. `ruff check` on the 6 CI-scoped 66-05 files returns exit=0 (all clean). `ruff format --check firestarter/ tests/` exits 0 (58 files already formatted). The CI ruff gate scope (firestarter/ tests/) will surface these pre-existing errors — this is a pre-existing debt item, not introduced by 66-05.

---

## Human Verification Required

None — all truths verifiable programmatically. The host guard, runtime-boundary tests, and behavioral spot-checks constitute full programmatic verification.

---

## Gaps Summary

No gaps. SC#3 / DB-05 is closed at the runtime boundary. The 66-05 gap-closure plan delivered both remediation options (Option A: authoritative runtime host guard; Option B: simulation realignment + WR-02/WR-03).

**SC#1, SC#2, SC#4 remain VERIFIED** — unchanged from prior verification; 66-05 touched runtime code only (no DB churn).

**SC#3 is now VERIFIED** — the prior BLOCKER is closed. Evidence chain:
1. `chip_resolver.resolve_chip` reads `support_status` from the raw config (not via `_map_data`).
2. The guard fires BEFORE `convert_to_programmer` — no wire dict is ever built for a non-supported chip.
3. The 4 vpp-exceeds-max UV-EPROM chips (M2716/M2732 family, 25V) raise `ChipNotImplementedError` at the host boundary — `configure_eprom` is unreachable.
4. The 9 adapter-required 24-pin EEPROMs raise `ChipNotImplementedError` — the guard is driven by `support_status`, not the incidental `etype` string.
5. `check_dispatch.py` models `_map_data`'s real mem_type derivation and is GREEN because the host guard refuses (not because the simulation pretended `mem_type=None`).
6. All 499 tests pass; coverage 71.93%; ruff/mypy clean on modified files; no DB churn.

---

_Verified: 2026-06-12T13:30:00Z_
_Verifier: Claude (gsd-verifier)_
_Status: passed — 4/4 SC verified; SC#3 BLOCKER closed by 66-05 host guard in chip_resolver.resolve_chip_

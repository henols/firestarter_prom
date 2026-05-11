---
phase: 12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0
plan: 03
subsystem: host-database
wave: 1
tags:
  - python
  - database
  - mem_type
  - blocker-1
  - defense-in-depth
  - phase-12
requires:
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-01-SUMMARY.md
provides:
  - firestarter_app/firestarter/database.py::_ALGO_MEM_TYPE
  - firestarter_app/firestarter/database.py::_map_data (algorithm-driven mem_type)
affects:
  - firestarter_app/firestarter/database.py
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-04-PLAN.md
tech_stack:
  added: []
  patterns:
    - Module-top constant table (`_ALGO_MEM_TYPE` mirrors sibling `PROTOCOL_MAP`)
    - Algorithm-driven dispatch with legacy substring fallback for backward compat
key_files:
  created: []
  modified:
    - firestarter_app/firestarter/database.py
decisions:
  - "Implemented D3 algorithm→mem_type table verbatim from CONTEXT.md (13 entries, hex keys, inline comments mirroring PROTOCOL_MAP shape)"
  - "Moved `protocol_id = programming.get('algorithm', 0)` read 9 lines UP (was at line 380, now line 390) so the new lookup can reference it — addresses RESEARCH.md pitfall 1"
  - "Preserved the legacy substring branch verbatim inside the `else` branch so user-override DB entries without an `algorithm` field still work — addresses CONTEXT.md D3 fallback rule"
  - "`info_flags` block (now lines 404-409) left UNTOUCHED per D3 explicit guidance — independent concern from mem_type derivation"
  - "RED test was a one-shot host harness at `/tmp/test_map_data_dispatch.py` (not committed) — the project has no pytest installed; the permanent regression scan is `firestarter_app/tools/check_dispatch.py` from Plan 12-01, which exercises all 743 chips"
metrics:
  duration_minutes: 3
  completed: 2026-05-11T09:12Z
  tasks_completed: 2
  files_created: 0
  files_modified: 1
  commits: 4  # 2 inside firestarter_app submodule + 2 supermodule pointer bumps
---

# Phase 12 Plan 03: Algorithm-Driven mem_type in Python `_map_data` Summary

**One-liner:** Replaced the brittle `electrical.type` substring branch in `firestarter_app/firestarter/database.py:_map_data` with an explicit 13-entry algorithm→mem_type lookup table, completing the BLOCKER-1 defense-in-depth fix at the host layer.

## Why This Plan

Plan 12-02 fixed BLOCKER-1 at the firmware layer (`configure_memory` now dispatches on `handle->protocol` first). Plan 12-03 is the Python-host counterpart: even if firmware is later rolled back to a pre-Phase-12 build, the wire-level `type` field now matches the firmware's `mem_type` fallback expectations per algorithm. Specifically, every SRAM-protocol chip (algo ∈ {0x0E, 0x27, 0x28, 0x29}) now emits `type=4 (TYPE_SRAM)` on the wire — closing the BLOCKER-2 electrical-safety hazard at the host layer too.

## Artifacts Modified

### `firestarter_app/firestarter/database.py`

**Submodule path:** `/workspaces/firestarter_prom/firestarter_app/firestarter/database.py`

#### Edit 1 (Task 1) — `_ALGO_MEM_TYPE` module-level constant added

Inserted after `PROTOCOL_MAP` (line 43) and before `types =` (now line 64). Exactly 13 entries, matching CONTEXT.md D3 table:

```python
# Algorithm (minipro protocol_id) → firmware mem_type integer.
# Firmware dispatches on protocol first; mem_type is kept consistent for fallback paths.
_ALGO_MEM_TYPE = {
    0x05: 5,   # FLASH_AMD_STD     → TYPE_FLASH_TYPE_4
    0x06: 3,   # FLASH_AMD_ALT     → TYPE_FLASH_TYPE_3
    0x07: 1,   # EPROM_STD         → TYPE_EPROM
    0x08: 1,   # EPROM_QUICK       → TYPE_EPROM
    0x0B: 1,   # EPROM_LEGACY      → TYPE_EPROM
    0x0D: 1,   # EEPROM_POLL       → TYPE_EPROM (firmware dispatches on protocol prefix)
    0x0E: 4,   # SRAM_32PIN        → TYPE_SRAM
    0x10: 1,   # FLASH_INTEL       → TYPE_EPROM (firmware dispatches on protocol prefix)
    0x27: 4,   # SRAM_24PIN        → TYPE_SRAM
    0x28: 4,   # SRAM_STD          → TYPE_SRAM
    0x29: 4,   # SRAM_512K_1M      → TYPE_SRAM
    0x35: 5,   # FLASH_EEPROM_LIKE → TYPE_FLASH_TYPE_4
    0x39: 5,   # FLASH_INTEL_ALT   → TYPE_FLASH_TYPE_4 (no DB chips; future-proofed)
}
```

Style mirrors `PROTOCOL_MAP` directly above (hex keys, one entry per line, inline comments).

#### Edit 2 (Task 2) — `_map_data` substring branch → algorithm lookup

**Before (lines 371-380, pre-edit):**

```python
        # Simplified type determination
        type_str = electrical.get("type", "")
        determined_type = 1  # Default to EPROM
        if "Flash" in type_str:
            determined_type = 2  # Generic Flash
        elif "SRAM" in type_str:
            determined_type = 4

        # Read algorithm integer directly — set by build_db.py as minipro protocol_id
        protocol_id = programming.get("algorithm", 0)
```

**After (lines 389-402, post-edit):**

```python
        # Read algorithm integer directly — set by build_db.py as minipro protocol_id
        protocol_id = programming.get("algorithm", 0)

        # Derive mem_type from algorithm (D3). Fall back to electrical.type substring
        # only when algorithm is absent / 0 (legacy user-override DB entries).
        if protocol_id and protocol_id in _ALGO_MEM_TYPE:
            determined_type = _ALGO_MEM_TYPE[protocol_id]
        else:
            type_str = electrical.get("type", "")
            determined_type = 1  # Default to EPROM
            if "Flash" in type_str:
                determined_type = 2  # Generic Flash (legacy fallback only)
            elif "SRAM" in type_str:
                determined_type = 4
```

**Line accounting:**
- 10 lines replaced with 14 lines (+4 lines: comment + `if`/`else` structure)
- `protocol_id` read MOVED UP 9 source lines (was at line 380, now at line 390)
- `info_flags` block now at lines 404-409 (was 382-387) — content identical, only line numbers shifted by the added comment block

## Verification — Plan-Level Success Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `_ALGO_MEM_TYPE` exists at module scope with exactly 13 D3 entries | PASS | `grep -c "^_ALGO_MEM_TYPE = {" database.py` → 1; AST inspection confirms 13 keys at top-level (not inside any class) |
| 2 | `_map_data` reads `protocol_id` before deriving `determined_type` | PASS | line 390 (`read`) precedes line 394 (`lookup`); single occurrence (not duplicated) |
| 3 | When `algorithm` is in `_ALGO_MEM_TYPE`, `determined_type` comes from the table | PASS | synthetic test `algo=0x06, electrical.type='UV-EPROM'` returns `type=3` (algorithm wins) |
| 4 | When `algorithm == 0` or absent, legacy substring branch runs | PASS | synthetic `programming={}, electrical.type='Flash/EEPROM'` → type=2; SRAM → 4; else → 1 |
| 5 | `info_flags` derivation at original lines 382-387 is unchanged | PASS | `grep -c "info_flags \|= 0x00000010"` → 1; content identical (line numbers shifted by +22 due to constant + branch comments) |
| 6 | `python3 firestarter_app/tools/check_dispatch.py` exits 0 | PASS | `PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom` (exit 0) |
| 7 | Spot-checks for W27C512, AM27C040, AM29F040, AT28C256, AE29F1008, 6116, DS1245AB(RW) all pass | PASS | See spot-check table below |

## Spot-Check Results

| Chip | DB Part Number | Algorithm | Pre-fix `type` | Post-fix `type` | Expected | Status |
|------|----------------|-----------|----------------|------------------|----------|--------|
| W27C512 | `W27C512` | 0x07 | **2 (broken)** | **1** | 1 | FIXED — BLOCKER-1 |
| AM27C040 | `AM27C040` | 0x08 | 1 | 1 | 1 | unchanged (correct pre-fix) |
| AM29F040 | `AM29F040` | 0x06 | **2 (broken)** | **3** | 3 | FIXED — BLOCKER-1 |
| AE29F1008 | `AE29F1008` | 0x05 | **2 (broken)** | **5** | 5 | FIXED — BLOCKER-1 |
| 6116 | `6116` | 0x27 | **1 (HAZARD)** | **4** | 4 | FIXED — BLOCKER-2 (SRAM no longer mislabelled) |
| DS1245AB(RW) | `DS1245AB(RW),DS1245Y(RW)` | 0x0E | **1 (HAZARD)** | **4** | 4 | FIXED — BLOCKER-2 |
| AT28C256 | `AT28C256,AT28C256` | 0x07 | 2 → 1 | 1 | 1 | per D5: deferred — algo=0x07 upstream mistag is OUT OF SCOPE |

Note on AT28C256: the upstream minipro DB tags it `algo=0x07` (EPROM_STD) instead of `0x0D` (EEPROM_POLL). Phase 12 does NOT correct this — per CONTEXT.md D5 the per-chip override table is a separate future phase. Plan 12-03 only changes `type` from 2 (pre-fix substring branch) to 1 (post-fix table lookup); the underlying upstream-tag hazard (WARNING-5) is unchanged.

## Synthetic Behavior Tests

The plan's `<behavior>` block was exercised by a one-shot RED→GREEN harness at `/tmp/test_map_data_dispatch.py` (not committed — project has no pytest installed; permanent regression scan is `check_dispatch.py`):

- **Algorithm-wins (over substring):** `algo=0x06, electrical.type='UV-EPROM'` → `type=3` (substring branch did NOT run)
- **SRAM algorithm-wins:** `algo=0x27, electrical.type='UV-EPROM'` → `type=4`
- **Fallback (no algo) — Flash branch:** `programming={}, electrical.type='Flash/EEPROM'` → `type=2`
- **Fallback (no algo) — SRAM branch:** `programming={}, electrical.type='SRAM'` → `type=4`
- **Fallback (no algo) — default:** `programming={}, electrical.type='UV-EPROM'` → `type=1`
- **Fallback (no algo) — empty:** `programming={}, electrical.type=''` → `type=1`

Pre-fix run (RED): 8 failures (6 BLOCKER-1/2 spot-checks + 2 algorithm-wins). Post-fix run (GREEN): 13/13 cases PASS.

## `check_dispatch.py` Confirmation (Permanent Regression Gate)

```
$ python3 firestarter_app/tools/check_dispatch.py
PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom
```

Exit code 0. The scan still PASSes after both edits — no regressions introduced. (Note: `check_dispatch.py` itself simulates the post-fix host+firmware dispatch — it was already GREEN after Plan 12-01 because its `_ALGO_MEM_TYPE` is a hardcoded local copy. The scan's role for Plan 12-03 is to confirm the live `database.py` does not deviate from the simulated table — both produce identical outcomes for all 743 chips.)

## Deviations from Plan

None — plan executed exactly as written. The two-task structure mapped cleanly to two file edits, two submodule commits, and two supermodule pointer bumps.

The only minor adjustment was using the full part_number strings (`AT28C256,AT28C256` and `DS1245AB(RW),DS1245Y(RW)`) in the spot-check assertions, because `EpromDatabase.get_eprom_config` does exact-match lookup on the comma-joined alias string in `part_number`. The plan's `<behavior>` block referred to the chips by their canonical short names (`AT28C256`, `DS1245AB(RW)`); using the canonical DB keys in the test is a no-op consistency adjustment, not a deviation.

## Authentication Gates

None — pure local data-transform code change.

## Threat Flags

None — Plan 12-03 introduces no new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries. The plan's threat register entry T-12-03 (electrical-safety mitigation for SRAM-protocol chips via wire-protocol `type=4`) is fully satisfied: all four SRAM algorithms (0x0E, 0x27, 0x28, 0x29) now map to `mem_type=4 (TYPE_SRAM)` via the D3 table.

## Known Stubs

None — no stub patterns introduced. The legacy substring fallback (`else` branch) is reachable only when `algorithm == 0` or absent. No chip in the regenerated DB hits the fallback today (Plan 12-04 will further reduce the chance by emitting `electrical.type = "SRAM"` for SRAM-protocol chips), but the branch is intentional for user-override DB entries lacking an `algorithm` field.

## Cross-Wave Continuity

- **Wave 0 (Plan 12-01):** `firestarter_app/tools/check_dispatch.py` was the regression gate. Plan 12-03 confirmed it still PASSes after the live code change. ✓
- **Wave 1A (Plan 12-02):** Firmware-side BLOCKER-1 fix (`configure_memory` protocol-prefix dispatch + `TYPE_FLASH_TYPE_2` removal + `[env:native]` host stubs). Plan 12-03 is the Python-side counterpart per CONTEXT.md D1 ("Fix at BOTH layers"). ✓
- **Wave 2 (Plan 12-04, upcoming):** `build_db.py` SRAM detection — will emit `electrical.type = "SRAM"` for proto_id ∈ {0x0E, 0x27, 0x28, 0x29}. Plan 12-03 is upstream-tolerant of that change because `_ALGO_MEM_TYPE[0x27] = 4` runs regardless of the `electrical.type` string. ✓

## Commits

| Stage | Repo | Hash | Message |
|-------|------|------|---------|
| Task 1 | firestarter_app | `c42ea8b` | feat(12-03): add _ALGO_MEM_TYPE algorithm→mem_type lookup table |
| Task 1 | supermodule | `f45ddce` | feat(12-03): bump firestarter_app pointer — _ALGO_MEM_TYPE table (c42ea8b) |
| Task 2 | firestarter_app | `96abda7` | feat(12-03): drive _map_data mem_type from algorithm via _ALGO_MEM_TYPE table |
| Task 2 | supermodule | `5550f1b` | feat(12-03): bump firestarter_app pointer — _map_data algorithm dispatch (96abda7) |

## Self-Check: PASSED

- `firestarter_app/firestarter/database.py` — `_ALGO_MEM_TYPE` exists with 13 D3 entries (verified via import + AST).
- `firestarter_app/firestarter/database.py` — `_map_data` reads `protocol_id` (line 390) before lookup (line 394).
- `firestarter_app/firestarter/database.py` — info_flags branch present and unchanged (line 408, content identical to pre-edit line 386).
- `firestarter_app/tools/check_dispatch.py` — exit 0, PASS line.
- All 4 commits (2 in firestarter_app + 2 supermodule pointer bumps) exist in `git log`.
- No file outside `firestarter_app/firestarter/database.py` was touched by this plan.

---
phase: 12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0
plan: 04
subsystem: host-database-pipeline
wave: 2
tags:
  - python
  - database
  - sram
  - build-pipeline
  - blocker-2
  - phase-12
requires:
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-01-SUMMARY.md
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-02-SUMMARY.md
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-03-SUMMARY.md
provides:
  - "firestarter_app/tools/build_db.py — SRAM electrical.type detection by proto_id (D4)"
  - "firestarter_app/firestarter/data/minipro_complete_db.json — regenerated DB with 52 SRAM-tagged chips"
affects:
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-05-PLAN.md
tech-stack:
  added: []
  patterns:
    - "Hoisted electrical-type derivation out of the inline ternary into an `_etype` local computed before chip_entry construction"
    - "Inline literal set `{0x0E, 0x27, 0x28, 0x29}` for SRAM detection (matches PATTERNS.md section 4 diff and stays consistent with the existing proto_id-vs-KNOWN_PROTOCOLS check at line 204)"
key-files:
  created: []
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/firestarter/data/minipro_complete_db.json
key-decisions:
  - "Used inline literal set {0x0E, 0x27, 0x28, 0x29} instead of a new SRAM_PROTOCOLS module constant — matches PATTERNS.md section 4 diff exactly and avoids introducing a third proto-set constant alongside KNOWN_PROTOCOLS"
  - "Placed the SRAM block AFTER `pinout_key = resolve_pinout_key(...)` (line 209) and BEFORE `chip_entry = {` (was line 211) — keeps the local `_etype` next to its only use site, requires no other re-ordering"
  - "Did NOT modify KNOWN_PROTOCOLS or PROTOCOL_MAP — D4 detection rule is independent of the known-protocol filter"
  - "Did NOT modify the `info_flags` derivation in database.py:_map_data — by changing electrical.type from 'UV-EPROM' to 'SRAM' for SRAM chips, the existing `if electrical.type == 'Flash/EEPROM'` test now correctly evaluates False for SRAM (no spurious 0x00000010 'electrically-erasable' bit), per D3 explicit guidance to leave that branch alone"
patterns-established:
  - "Pattern: derive electrical-type by proto_id check first, then flags-bit fallback. Reusable for any future protocol class that needs explicit detection (e.g. NVRAM family, if/when added)"
requirements-completed:
  - REQ-SER-01
duration_minutes: 2
completed: 2026-05-11T09:20Z
---

# Phase 12 Plan 04: build_db.py SRAM electrical.type emission (Wave 2) Summary

**Closes BLOCKER-2 at the database-pipeline layer (D4). `firestarter_app/tools/build_db.py` now emits `"electrical.type": "SRAM"` for `proto_id ∈ {0x0E, 0x27, 0x28, 0x29}` before the existing `flags & 0x10` heuristic runs, so the 52 SRAM chips in the regenerated `minipro_complete_db.json` are correctly classified instead of mislabeled `"UV-EPROM"`. Combined with Plans 02 (firmware) and 03 (Python host), the end-to-end algorithm-based dispatch is now correct at all three layers.**

## Performance

- **Duration:** ~2 minutes (small targeted change + network DB fetch)
- **Started:** 2026-05-11T09:18:27Z
- **Completed:** 2026-05-11T09:20Z
- **Tasks:** 2 (Task 1 = build_db.py SRAM detection; Task 2 = regenerate DB + run regression scan)
- **Files modified:** 2 (one Python script, one generated JSON DB)
- **Files created:** 0
- **Commits:** 4 (2 inside firestarter_app submodule + 2 supermodule pointer bumps)

## Task Commits

| Stage | Repo | Hash | Message |
|-------|------|------|---------|
| Task 1 | firestarter_app | `4881197` | feat(12-04): emit electrical.type = "SRAM" for SRAM proto_id (D4) |
| Task 1 | supermodule | `8f6728a` | feat(12-04): bump firestarter_app pointer — build_db.py SRAM detection (4881197) |
| Task 2 | firestarter_app | `45068c0` | feat(12-04): regenerate minipro_complete_db.json with SRAM electrical.type |
| Task 2 | supermodule | `90078e7` | feat(12-04): bump firestarter_app pointer — regenerated DB with SRAM tagging (45068c0) |

## Accomplishments

- **D4 SRAM detection landed in the data-pipeline layer.** `build_db.py` now hoists the `electrical.type` derivation out of an inline ternary into a local `_etype` variable computed by an explicit if/elif/else chain: SRAM proto_ids → `"SRAM"`, else `flags & 0x10` → `"Flash/EEPROM"`, else `"UV-EPROM"`. The chip_entry's `electrical.type` is then `"type": _etype,`.
- **BLOCKER-2 end-to-end closure verified.** Plan 02 closed it in firmware (`configure_memory` protocol-prefix dispatch routes 0x0E/0x27/0x28/0x29 to `configure_sram`); Plan 03 closed it in the Python host (`_map_data._ALGO_MEM_TYPE[0x27]=4` makes the wire `type` field match); Plan 04 closes it at the source-of-truth layer (the DB itself no longer mislabels SRAM as UV-EPROM, so the CLI display, info-flags derivation, and any downstream consumer all see the correct classification).
- **Phase 12 acceptance criterion 1 satisfied.** `python3 firestarter_app/tools/check_dispatch.py` reports `PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom`. Zero chips in the regenerated DB would hit the firmware's "Memory type 0x%02x not supported" branch.
- **Phase 12 acceptance criterion 5 satisfied.** `build_db.py` emits `electrical.type = "SRAM"` for SRAM-protocol chips per D4 detection rule. Exactly 52 chips carry the new tag (matches the BLOCKER-2 audit count from CONTEXT.md and RESEARCH.md to the chip).
- **Surgical DB diff.** The regenerated `minipro_complete_db.json` differs from the prior commit by exactly 52 insertions and 52 deletions — one line per SRAM chip swapping `"UV-EPROM"` → `"SRAM"`. No mass corruption, no other field changes, no chip-count drift.

## `build_db.py` Diff Line Ranges

**Submodule path:** `firestarter_app/tools/build_db.py`

### Edit 1 (Task 1) — SRAM detection block + ternary replacement

**Diff against pre-Plan-04 commit `96abda7`:** 12 lines net change (+11 / -1).

| Region | Before | After |
|--------|--------|-------|
| Lines 209-210 | `pinout_key = resolve_pinout_key(...)` then blank line then `chip_entry = {` (no detection block) | unchanged — `pinout_key = resolve_pinout_key(...)` stays |
| Lines 211-220 (NEW) | — | comment + `if proto_id in {0x0E, 0x27, 0x28, 0x29}: _etype = "SRAM"` / `elif flags & 0x10: _etype = "Flash/EEPROM"` / `else: _etype = "UV-EPROM"` |
| Line 224 (was line 214) | `"type": "Flash/EEPROM" if (flags & 0x10) else "UV-EPROM",` | `"type": _etype,` |
| Everything else in the chip-emission loop | unchanged | unchanged |

Post-edit line layout of `build_db.py`:
- **Line 198:** `proto_id = int(ic.get("protocol_id"), 16)` (unchanged — the new block reads it)
- **Line 204:** `if proto_id not in KNOWN_PROTOCOLS: ... continue` (unchanged — pre-filter the unknown set)
- **Line 209:** `pinout_key = resolve_pinout_key(pin_count, variant, flags)` (unchanged)
- **Lines 211-220:** NEW — comment + `_etype` derivation by D4 detection rule
- **Line 222:** `chip_entry = {` (was line 211)
- **Line 224:** `"type": _etype,` (was the inline ternary on line 214)

**Source-ordering verified:** `proto_id =` at line 198 < `_etype = "SRAM"` at line 215 < `"type": _etype,` at line 224. The `_etype` lookup reads `proto_id` (which was decoded earlier) and writes the local that `chip_entry["electrical"]["type"]` reads — pitfall 4 from RESEARCH.md cleanly avoided.

### Edit 2 (Task 2) — regenerated DB

**Submodule path:** `firestarter_app/firestarter/data/minipro_complete_db.json`

```
firestarter_app/firestarter/data/minipro_complete_db.json | 104 +++++++++++++++---------------
 1 file changed, 52 insertions(+), 52 deletions(-)
```

The 52 changed lines are exclusively `"type": "UV-EPROM"` → `"type": "SRAM"` swaps inside the `electrical` sub-object of each SRAM-protocol chip. No other field changes.

## Build Command Output

```
$ cd firestarter_app && python tools/build_db.py
WARN: skipping AT45DBxxx@SOIC28 — unknown protocol_id 0x04   (x9 — AT45DB serial flash, SOIC, out of scope)
WARN: skipping AT45Dxxx@SOIC28 — unknown protocol_id 0x04    (x3 — AT45D serial flash, SOIC, out of scope)
WARN: skipping M50FW040 — unknown protocol_id 0x11           (x2 — Intel FWH, dispatched elsewhere)
WARN: skipping M50FW080 — unknown protocol_id 0x11           (x2)
WARN: skipping TMS87C257@PLCC32 — unknown protocol_id 0x0A   (PLCC, out of scope)
WARN: skipping X88C64P@DIP24,X88C64S@SOIC24 — unknown protocol_id 0x34
Fetching database from: https://gitlab.com/DavidGriffith/minipro/-/raw/master/infoic.xml
Processing and enriching data...
Done! 743 chips processed. Saved to /workspaces/firestarter_prom/firestarter_app/tools/../firestarter/data/minipro_complete_db.json
```

The 17 WARN lines are pre-existing skips of chips with protocols outside `KNOWN_PROTOCOLS` (per Phase 11 design — unknown protocols are skipped, not silently mapped). None are SRAM family.

**Chip count:** 743 total (unchanged — same as pre-Plan-04 baseline).

**By electrical.type after regeneration:**

| Type | Count |
|------|-------|
| SRAM | **52** (was 0) |
| Flash/EEPROM | 331 |
| UV-EPROM | 360 |
| **Total** | 743 |

The 52 SRAM chips that moved to the SRAM tag previously occupied the UV-EPROM bucket; Flash/EEPROM count is unchanged. (Pre-Plan-04 counts: SRAM=0, Flash/EEPROM=331, UV-EPROM=412.)

## `check_dispatch.py` Output

```
$ python3 firestarter_app/tools/check_dispatch.py
PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom
```

Exit code 0. Both BLOCKER-1 (any chip falling through to "Memory type 0x%02x not supported") and BLOCKER-2 (SRAM chips dispatched to configure_eprom and enabling the 12V VPP regulator on a 5V SRAM) remain at **zero** across all 743 chips. The regression scan is the canonical PASS gate that all three Wave 1 + Wave 2 fixes converge on.

## Chip Count by Algorithm Post-Regeneration vs RESEARCH.md Baseline

| Algorithm | Post-regen | RESEARCH.md baseline | Delta | Acceptance (±10%) |
|-----------|-----------|----------------------|-------|-------------------|
| 0x05 FLASH_AMD_STD | 27 | 27 | 0 | PASS |
| 0x06 FLASH_AMD_ALT | 190 | 190 | 0 | PASS (≥150) |
| 0x07 EPROM_STD | 237 | 237 | 0 | PASS (≥200) |
| 0x08 EPROM_QUICK | 127 | 127 | 0 | PASS |
| 0x0B EPROM_LEGACY | 53 | 53 | 0 | PASS |
| 0x0D EEPROM_POLL | 18 | 18 | 0 | PASS |
| 0x0E SRAM_32PIN | 20 | 20 | 0 | PASS (SRAM family) |
| 0x10 FLASH_INTEL | 39 | 39 | 0 | PASS (≥30) |
| 0x27 SRAM_24PIN | 2 | 2 | 0 | PASS (SRAM family) |
| 0x28 SRAM_STD | 10 | 10 | 0 | PASS (SRAM family) |
| 0x29 SRAM_512K_1M | 20 | 20 | 0 | PASS (SRAM family) |
| 0x35 FLASH_EEPROM_LIKE | 0 | 0 | 0 | unchanged (no chips in upstream DB) |
| 0x39 FLASH_INTEL_ALT | 0 | 0 | 0 | unchanged (no chips in upstream DB) |
| **Total** | **743** | **743** | **0** | PASS |

**Upstream `infoic.xml` drift since RESEARCH.md baseline:** zero. Every algorithm count matches the RESEARCH.md table exactly to the chip. The Plan's drift tolerance of ±10% and the SRAM count range of 40-80 are all satisfied with margin.

**SRAM family total: 20 + 2 + 10 + 20 = 52 chips** — matches the BLOCKER-2 audit count from CONTEXT.md and RESEARCH.md exactly.

## Spot-Check Trace — End-to-End BLOCKER-2 Verification

A 6116 SRAM chip (algorithm = 0x27) post-Plan-04 now flows through all three layers consistently:

| Layer | Field | Pre-Phase-12 value | Post-Phase-12 value |
|-------|-------|---------------------|---------------------|
| **DB pipeline** (Plan 04) | `electrical.type` | "UV-EPROM" (hazardous mislabel) | **"SRAM"** ✓ |
| **Python host** (Plan 03) | wire JSON `"type"` | 1 (TYPE_EPROM — would activate VPP) | **4 (TYPE_SRAM)** ✓ |
| **Firmware** (Plan 02) | dispatch handler | `configure_eprom` (activates 12V VPP on 5V part — HAZARD) | **`configure_sram`** ✓ |
| `info_flags` derivation | `"electrically-erasable" bit (0x10)` | spuriously set (electrical.type matched "Flash" substring via "Flash/EEPROM" branch earlier in the broken substring logic) | **not set** ✓ (electrical.type is "SRAM", not "Flash/EEPROM") |

All three layers now agree. The 12V VPP boost regulator can no longer be enabled on a 5V SRAM part by Firestarter — defense-in-depth complete.

## Verification — Success Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `build_db.py` has the SRAM detection block; `_etype` used in chip_entry; line-214 ternary removed | PASS | grep counts: `if proto_id in {0x0E, 0x27, 0x28, 0x29}` = 1, `_etype = "SRAM"` = 1, `_etype = "Flash/EEPROM"` = 1, `_etype = "UV-EPROM"` = 1, `"type": _etype,` = 1, leftover ternary = 0 |
| 2 | Regenerated `minipro_complete_db.json` is valid JSON | PASS | `python3 -c "import json; json.load(open(...))"` succeeds |
| 3 | SRAM-tagged chip count in regenerated DB is in [40, 80] | PASS | 52 (exact match to RESEARCH.md baseline) |
| 4 | Zero SRAM-protocol chips remain tagged `"UV-EPROM"` | PASS | `[chip for chip in db if algo ∈ SRAM_set and electrical.type != 'SRAM']` = empty list |
| 5 | `python3 firestarter_app/tools/check_dispatch.py` exits 0 with PASS | PASS | `PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom` (exit 0) |
| 6 | Phase regression: 0 chips fall through to "Memory type 0x%02x not supported" | PASS | check_dispatch.py reports 0 ERROR-bucketed chips across all 743 |

### Source-Level Acceptance Criteria (from Task 1 `<acceptance_criteria>`)

| Check | Expected | Actual |
|-------|----------|--------|
| `grep -c "if proto_id in {0x0E, 0x27, 0x28, 0x29}"` | 1 | 1 |
| `grep -c '_etype = "SRAM"'` | 1 | 1 |
| `grep -c '_etype = "Flash/EEPROM"'` | 1 | 1 |
| `grep -c '_etype = "UV-EPROM"'` | 1 | 1 |
| `grep -c '"type": _etype,'` | 1 | 1 |
| `grep -nE '"type": "Flash/EEPROM" if .flags & 0x10. else "UV-EPROM"'` matches | 0 | 0 |
| `_etype = "SRAM"` line > `proto_id = int(...)` line | true | 215 > 198 ✓ |
| `_etype = "SRAM"` line < `"type": _etype,` line | true | 215 < 224 ✓ |
| `python3 -c "import ast; ast.parse(...)"` exit | 0 | 0 |

### Behavioral Acceptance Criteria (from Task 2 `<acceptance_criteria>`)

| Check | Expected | Actual |
|-------|----------|--------|
| DB parses as valid JSON | OK | OK |
| SRAM-tagged count in [40, 80] | OK | 52 |
| `check_dispatch.py` exits 0 with PASS line | OK | PASS line on final line, exit 0 |
| No SRAM-protocol chip tagged `UV-EPROM` | empty bad list | empty |
| 0x06 count ≥ 150 | true | 190 |
| 0x07 count ≥ 200 | true | 237 |
| 0x10 count ≥ 30 | true | 39 |
| `grep -c '"type": "Flash/EEPROM" if'` in JSON | 0 | 0 |
| Phase regression: 0 broken chips | true | 0 |

## Cross-Wave Continuity

- **Wave 0 (Plan 12-01):** `firestarter_app/tools/check_dispatch.py` regression scan. Plan 04 confirmed it still PASSes after the DB regeneration — and now the scan exercises the *real* post-Plan-04 DB (not a synthetic). ✓
- **Wave 1A (Plan 12-02):** Firmware dispatch extension (`configure_memory` protocol-prefix). Plan 04 is downstream-tolerant: the firmware already protects against SRAM→configure_eprom routing regardless of how `electrical.type` is set, because dispatch is on `handle->protocol`. The Plan 04 DB change is the third independent layer of the defense-in-depth. ✓
- **Wave 1B (Plan 12-03):** Python host `_ALGO_MEM_TYPE` table. The `info_flags` branch (`if electrical.type == "Flash/EEPROM"`) was left untouched by Plan 03 per D3 explicit guidance — that branch now correctly evaluates False for SRAM chips because Plan 04 changed their `electrical.type` to "SRAM". The two plans compose cleanly: Plan 03 derives `mem_type` from algorithm; Plan 04 ensures the surface display field matches. ✓
- **Wave 2 (this plan):** complete. Phase 12 BLOCKER-1 + BLOCKER-2 fully closed at firmware + host + DB layers.
- **Plan 12-05 (next):** doc-only update of `firestarter/CLAUDE.md` dispatch table. Independent of Plan 04 artifacts; can reference this SUMMARY for the final electrical.type-tag rule.

## Deviations from Plan

None — plan executed exactly as written. The two-task structure mapped cleanly to two file edits, two submodule commits, and two supermodule pointer bumps. No auto-fixes (Rules 1-3) needed; no architectural decisions (Rule 4) required.

The build_db.py edit landed exactly per PATTERNS.md section 4 concrete diff. The regenerated DB matched RESEARCH.md baseline counts to the chip (no upstream `infoic.xml` drift since baseline) and produced the predicted 52 SRAM-tagged chips. `check_dispatch.py` PASSed unchanged.

## Authentication Gates

None — this plan only edits one Python file, downloads a public XML over HTTPS (trusted upstream per Phase 11 design), and runs local regression scripts.

## Threat Flags

None new. The plan's `<threat_model>` already documents BLOCKER-2 electrical safety (T-12-04 — `mitigate`); Plan 04 is the data-layer half of the three-layer mitigation (Plans 02/03 are the firmware + host halves). The mitigation is verified by Task 2's acceptance criterion: zero SRAM-protocol chips remain tagged `"UV-EPROM"` in the regenerated DB.

No infosec surface is introduced: the upstream XML fetch is over HTTPS to a public GitLab mirror, content is parsed but not executed, and there are no SQL/exec sinks downstream.

## Known Stubs

None — no stub patterns introduced. Plan 04 changes are a single explicit `if/elif/else` chain (no placeholder branches), and the regenerated DB is the canonical output of `build_db.py` (no hand-curated entries).

## Issues Encountered

None. The plan executed in two clean steps:

1. Apply the `build_db.py` edit (1 Edit tool call, immediate AST + grep verification).
2. Run `python tools/build_db.py` (single HTTPS fetch from `gitlab.com/DavidGriffith/minipro/-/raw/master/infoic.xml`, completed in <2 seconds) and run `check_dispatch.py` (sub-second).

No network retries needed. No build failures. No regression in the dispatch scan.

## Self-Check: PASSED

- `firestarter_app/tools/build_db.py` — has SRAM detection block (lines 211-220) and `"type": _etype,` (line 224); AST parses; all grep acceptance counts match.
- `firestarter_app/firestarter/data/minipro_complete_db.json` — exists; valid JSON; 743 chips; 52 SRAM-tagged; 0 leftover ternary text.
- `firestarter_app@4881197` — present in `git log` (submodule).
- `firestarter_app@45068c0` — present in `git log` (submodule).
- supermodule `8f6728a` — present in `git log` (supermodule pointer bump for `4881197`).
- supermodule `90078e7` — present in `git log` (supermodule pointer bump for `45068c0`).
- `python3 firestarter_app/tools/check_dispatch.py` — exit 0, PASS line on all 743 chips, 0 SRAM→eprom routes.
- No file outside `firestarter_app/tools/build_db.py` and `firestarter_app/firestarter/data/minipro_complete_db.json` was touched by this plan.

---
*Phase: 12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0*
*Plan: 04 (Wave 2)*
*Completed: 2026-05-11*

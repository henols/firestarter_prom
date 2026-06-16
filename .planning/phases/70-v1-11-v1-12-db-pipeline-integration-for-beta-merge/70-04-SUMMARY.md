---
phase: 70-v1-11-v1-12-db-pipeline-integration-for-beta-merge
plan: "04"
subsystem: firestarter/src, firestarter_app
tags: [merge, beta, firmware, lockstep, dispatch-hardening, wire-parity, SC6]
dependency_graph:
  requires:
    - phase: 70-03
      provides: v1.12 branch CI-green (526 tests, ruff clean, mypy watermark 29/29)
  provides:
    - Firmware v1.12 merged onto firestarter/beta (fast-forward; b71c6fd)
    - firestarter_app v1.12 merged onto beta (6b5480f; 529 tests green)
    - MSG_ERR_PROTOCOL_NOT_IMPLEMENTED=0xBB wire parity confirmed host + firmware
    - GATE-03 green on beta (744 chips, 730 supported, 0 dispatch regressions)
    - v1.12 lockstep dual-repo on beta — one operator-authorized beta cut from done
  affects: [v1.12-milestone-close, beta-cut-operator-gated]
tech_stack:
  added: []
  patterns:
    - fast-forward firmware merge (0 beta-only commits → no conflict possible)
    - resolve-to-v1.12-for-tooling (tooling/test files taken from re-ported v1.12)
    - keep-beta-for-runtime (ic_layout.py kept from beta for v1.11 display improvements)
    - snapshot-regenerate-after-runtime-change (test_characterization.ambr regenerated)
key_files:
  created: []
  modified:
    - firestarter/include/messages.h (v1.12 firmware merge — 0xBB constant added)
    - firestarter/include/not_implemented.h (v1.12: new configure_not_implemented header)
    - firestarter/src/proms/not_implemented.cpp (v1.12: configure_not_implemented handler)
    - firestarter/src/proms/memory.cpp (v1.12: fail-closed dispatch guard)
    - firestarter_app/firestarter/data/chip_database.json (744 chips on beta)
    - firestarter_app/tools/build_db.py (v1.12 re-ported version on beta)
    - firestarter_app/tools/check_dispatch.py (v1.12 re-ported version on beta)
    - firestarter_app/tools/diff_db.py (v1.12 merged rule set on beta)
    - firestarter_app/tests/__snapshots__/test_characterization.ambr (regenerated for beta ic_layout.py)
key-decisions:
  - "D-07 honored: no git tag / release / version bump in either repo"
  - "Firmware: fast-forward merge (0 beta-only commits, clean); beta now at b71c6fd"
  - "ic_layout.py kept from beta (HEAD): Phase 60/61 display improvements (v1.11 work) preserved; v1.12 had only Phase 69 pin-field fix (subset)"
  - "test_characterization.ambr regenerated: 3 snapshots updated for beta ic_layout.py rendering (W27C512 type/VPP/erase display + list column widths)"
  - "firestarter_app gitlink NOT bumped in meta-repo: pinned until operator beta cut"
  - "Ruff I001 debt on beta: 0 errors in firestarter/ tests/ (CI scope) — pre-existing debt was in tools/ only, outside CI scope; gate GREEN"
requirements-completed: [SC#6]
duration: ~35min
completed: "2026-06-16T09:00:00Z"
tasks_completed: 2
tasks_total: 2
files_changed: 32
---

# Phase 70 Plan 04: Dual-Repo Lockstep Beta Merge Summary

**Firmware v1.12 fast-forward merged to firmware/beta (b71c6fd; uno 72.4% / leonardo 88.9% flash; 49/49 native tests) + firestarter_app v1.12 merged to host/beta (6b5480f; 529/529 tests; coverage 76.27%; GATE-03 green 744 chips); MSG_ERR_PROTOCOL_NOT_IMPLEMENTED=0xBB wire parity confirmed; v1.12 lockstep on beta — no tag cut (D-07).**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-06-16T08:20:00Z
- **Completed:** 2026-06-16T09:00:00Z
- **Tasks:** 2 / 2
- **Files modified:** 32 (firestarter_app beta merge commit) + firmware fast-forward

## Tasks Completed

| Task | Description | Repo | Commit / Result | Files |
|------|-------------|------|-----------------|-------|
| 1 | Merge firmware v1.12->beta, build uno + leonardo, native dispatch tests, wire parity | firestarter | fast-forward to b71c6fd (5 existing commits) | 11 files (messages.h, not_implemented.h/cpp, memory.cpp, tests) |
| 2 | Merge firestarter_app v1.12->beta (final), full CI gate + GATE-03 on beta | firestarter_app | 6b5480f | 32 files |

## What Was Verified

### Task 1 — Firmware

| Check | Result | Detail |
|-------|--------|--------|
| `git log --oneline v1.12..beta` | PASS | Empty — 0 beta-only commits; clean fast-forward |
| `git merge v1.12-protocol-dispatch-hardening` | PASS | Fast-forward to b71c6fd (5 commits) |
| `pio run -e uno` | PASS | 72.4% flash (23,344 / 32,256 B) |
| `pio run -e leonardo` | PASS | 88.9% flash (25,482 / 28,672 B) — under 90% ceiling |
| `pio test -e native` | PASS | 49 / 49 tests; all 6 test_not_implemented cases pass |
| Wire parity: messages.h | PASS | `#define MSG_ERR_PROTOCOL_NOT_IMPLEMENTED  0xBB` |
| Wire parity: messages.py | PASS | `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` |
| Wire parity: MSG_ERR_NOT_SUPPORTED | PASS | `0xA5` on both sides |
| No git tag created | PASS | D-07 honored |

### Native test_not_implemented suite results

| Test Case | Result |
|-----------|--------|
| test_protocol_0x11_fwh_not_implemented | PASSED |
| test_protocol_0x2A_gal_not_implemented | PASSED |
| test_protocol_0x2B_gal_not_implemented | PASSED |
| test_protocol_0x2C_pld_not_implemented | PASSED |
| test_unknown_nonzero_protocol_0x99_not_implemented | PASSED |
| test_protocol_zero_with_mem_type_eprom_dispatches_eprom | PASSED |

### Task 2 — firestarter_app

| Check | Result | Detail |
|-------|--------|--------|
| `git checkout beta && git merge v1.12-protocol-dispatch-hardening` | PASS | Merge completed; conflicts resolved per plan |
| `python tools/build_db.py` | PASS | 744 chips processed; DB regenerated clean |
| `python tools/check_dispatch.py` (GATE-03) | PASS | 744 chips / 730 supported / 14 non-dispatchable / 0 dispatch regressions |
| `ruff check firestarter/ tests/` (CI scope) | PASS | All checks passed (0 errors in CI scope) |
| `ruff format --check firestarter/ tests/` | PASS | 59 files already formatted |
| `python tools/check_mypy_watermark.py` | PASS | 29 errors / 29 watermark — OK |
| `python -m pytest --cov-fail-under=70` | PASS | 529 passed / 76.27% coverage |
| Chip count on beta | PASS | 744 chips confirmed |
| No git tag created | PASS | D-07 honored |

## Submodule Commit State

| Repo | Branch | HEAD | Status |
|------|--------|------|--------|
| `firestarter` (firmware) | `beta` | `b71c6fd` | v1.12 fast-forward merged |
| `firestarter_app` (host) | `beta` | `6b5480f` | v1.12 merge commit |
| Meta repo `firestarter_app` gitlink | — | NOT bumped | Pinned per convention; bump at operator beta cut |

## Deviations from Plan

### Handled Automatically

**1. [Rule 1 - Expected] firestarter_app merge had 12 file conflicts**
- **Found during:** Task 2 (git merge v1.12-protocol-dispatch-hardening)
- **Issue:** The merge produced 12 conflicted files (chip_database.json, ic_layout.py, tests/*, tools/*), not a "near-clean" merge as the plan optimistically stated. This was anticipated as possible by the plan's conflict resolution guidance.
- **Fix:** Applied the plan's resolution strategy:
  - `tools/build_db.py`, `tools/check_dispatch.py`, `tools/diff_db.py`, `tools/baseline/*.json`: took v1.12 (re-ported gate-green versions)
  - All test files (`tests/test_*.py`, `tests/golden/*`): took v1.12 versions
  - `firestarter/ic_layout.py`: kept beta (HEAD) version — Phase 60/61 v1.11 display improvements are more complete than v1.12's Phase 69 scalar-extract-only fix
  - `chip_database.json`: took v1.12 version, then regenerated via `python tools/build_db.py` (D-01); regenerated DB matched v1.12 version exactly
- **Files resolved:** 12 conflicted files; all CI gates green post-resolution
- **Commit:** 6b5480f

**2. [Rule 1 - Expected] test_characterization.ambr snapshot regeneration needed**
- **Found during:** Task 2 (pytest run post-merge)
- **Issue:** 3 snapshot failures in `test_characterization.py` (test_list, test_info_known_chip, test_search_w27). Root cause: the v1.12 snapshot was generated with the v1.12 branch's ic_layout.py; the beta ic_layout.py has Phase 60/61 display improvements (column width, type/VPP display for W27C512/EEPROM chips) that produce slightly different output.
- **Fix:** Ran `pytest tests/test_characterization.py --snapshot-update`. 3 snapshots updated to reflect beta's correct rendering. Changes verified: W27C512 now shows correct "EEPROM" type + 12.0v VPP + erasable flag on beta; list view has correct column widths from Phase 61 fix. All changes are v1.11 improvements (correct behavior), not regressions.
- **Files modified:** `tests/__snapshots__/test_characterization.ambr`
- **Commit:** 6b5480f (staged before merge commit)

### Pre-existing Ruff Debt

`ruff check .` (full tree) shows 4 errors — all in `tools/` (outside CI scope):
- `tools/audit_coverage_matrix.py`: I001 (pre-existing, outside CI scope)
- `tools/catalog/codegen.py`: I001 (pre-existing, outside CI scope)
- `tools/catalog/codegen_vectors.py`: I001 + UP031 (pre-existing, outside CI scope)

CI scope (`ruff check firestarter/ tests/`) returns "All checks passed!" — **gate GREEN**.

The 2 pre-existing I001 errors in `tests/test_address_parser.py` and `tests/test_codec.py` that were documented in Phase 66/67.1 and present on the v1.12 branch are GONE on beta. The beta versions of these files have been ruff-clean since Phase 37/38. The merge resolved them by taking the beta context for these files (they merged cleanly, not conflicting).

### D-07 Compliance

No git tag, pre-release, version bump, or push created in either repo. Last tag is `3.0.0b8` (pre-existing from v1.10/v1.11 milestone). The v1.12 milestone is now exactly one operator-authorized beta cut from done.

## Wire-Constant Parity Summary

| Constant | Firmware (messages.h) | Host (messages.py) | Match |
|----------|----------------------|--------------------|-------|
| `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` | `0xBB` | `0xBB` | YES |
| `MSG_ERR_NOT_SUPPORTED` | `0xA5` | `0xA5` | YES |

T-70-10 (wire-constant drift spoofing threat): **MITIGATED** — parity confirmed.

## Threat Surface Scan

No new security-relevant surface introduced by this merge. This is a lockstep delivery merge, not new feature code.

- T-70-10 (wire-constant spoofing): MITIGATED — 0xBB parity confirmed both sides
- T-70-11 (merge resurrects guess tables): MITIGATED — GATE-03 green post-merge; no 0x07 EPROM dispatch regressions; DIP28_28C64/28C256 cluster stays on 0x0D
- T-70-12 (premature beta cut): MITIGATED — D-07 hard constraint honored; no tags created; operator retains control

## Known Stubs

None. All gates green; no placeholder logic.

## Next Step (Operator)

The v1.12 milestone is now ready for operator-authorized beta cut:
1. Bump `firestarter_app` version to `3.0.0b10` (lockstep with firmware)
2. Bump meta-repo `firestarter_app` gitlink from `faaa571` to point at `6b5480f` on beta
3. Cut `3.0.0b10` pre-release tag in firestarter_app (PyPI + GitHub Pre-release)
4. Confirm firmware lockstep-version policy (may need skipped firmware tag b9 for lockstep, as at v1.10 close)
5. Run `/gsd-complete-milestone` for v1.12 close

## Self-Check: PASSED

- SUMMARY.md exists at `.planning/phases/70-v1-11-v1-12-db-pipeline-integration-for-beta-merge/70-04-SUMMARY.md` — FOUND
- Firmware beta commit `b71c6fd` exists in firestarter repo — FOUND
- Host beta merge commit `6b5480f` exists in firestarter_app repo — FOUND

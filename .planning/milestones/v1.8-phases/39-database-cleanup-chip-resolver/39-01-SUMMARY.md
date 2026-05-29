---
phase: 39-database-cleanup-chip-resolver
plan: 01
subsystem: refactoring
tags: [python, chip-resolution, module-extraction, host-cli, leaf-module, tdd, dry]

# Dependency graph
requires:
  - phase: 36-characterization-test-baseline
    provides: "182-test + 29-snapshot safety net (incl. bad-chip not-found CLI snapshot) proving behavior preservation"
  - phase: 37-tooling-baseline-ci-gate
    provides: "ruff + ruff-format + mypy watermark (44) CI gate"
  - phase: 38-low-risk-extractions
    plan: 01
    provides: "consolidated exception hierarchy in exceptions.py incl. ChipNotFoundError (the exception resolve_chip raises)"
provides:
  - "firestarter/chip_resolver.py — flat leaf with resolve_chip(name, db=None) -> dict (ChipNotFoundError on miss); the single DB-lookup chokepoint CLI dispatch and Phase 41 Click handlers will call"
  - "_resolve_or_exit(name, db) op-site adapter in main.py mapping ChipNotFoundError back to the legacy (log + return 1) contract"
  - "9 op sites (read/write/verify/blank/erase/id + dev read/addr/consistency-check) repointed; get_eprom→convert_to_programmer copy-paste eliminated"
affects: [41-cli-handlers, 42-error-handling-normalization]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single-chokepoint resolver leaf (resolve_chip): one public function between CLI dispatch and DB lookup/conversion, raising on miss"
    - "Exception-to-legacy-contract adapter (_resolve_or_exit): shared helper catches ChipNotFoundError, logs exact string, returns None — single point Phase 41 will replace with Click error mapping"
    - "db dependency-injection seam: production EpromDatabase() honors ~/.firestarter; tests pass EpromDatabase(skip_local_override=True)"

key-files:
  created:
    - firestarter_app/firestarter/chip_resolver.py
    - firestarter_app/tests/test_chip_resolver.py
  modified:
    - firestarter_app/firestarter/main.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr

key-decisions:
  - "resolve_chip treats BOTH get_eprom()==None AND convert_to_programmer()=={} as the not-found condition (raises ChipNotFoundError) — matches the pre-refactor `if not eprom_data` guard exactly"
  - "Production default db=None constructs EpromDatabase() WITHOUT skip_local_override (D-01): bench/prod must honor ~/.firestarter overrides; only tests pass skip_local_override=True"
  - "Shared _resolve_or_exit helper (option A, RESEARCH Pattern 2 / D-03), NOT per-site try/except: single point Phase 41 replaces with Click error mapping; minimizes churn at 9 sites"
  - "Exact not-found log string `EPROM '{name}' not found in database.` + exit code 1 preserved at every op site (GATE-1.8b); the 9 duplicate copies collapse to 1 in the helper (info site keeps its own → 2 total)"
  - "consistency-check site (D-04 / GATE-1.8d): only the lookup preamble replaced; eprom_data still flows to consistency_check_eprom + the D-05 3-way-verdict return is untouched"
  - "info/list/search lookups deliberately NOT touched (D-02); main.py:23 star-import deliberately left for Plan 39-02"

patterns-established:
  - "Resolver chokepoint leaf: name→programmer-config in one named function with a raise-on-miss contract and a db injection seam"
  - "Adapter helper preserves byte-identical legacy CLI behavior (log + exit 1) over a raising leaf (GATE-1.8b)"

requirements-completed: [DATA-01]

# Metrics
duration: ~20min
completed: 2026-05-27
---

# Phase 39 Plan 01: chip_resolver + 9 op-site repoint Summary

**Eliminated the 9× `get_eprom → convert_to_programmer → log+exit1` copy-paste in `main.py` by introducing a flat `chip_resolver.py` leaf with `resolve_chip(name, db=None) -> dict` (raises `ChipNotFoundError` on miss) plus a shared `_resolve_or_exit` adapter, and repointed all 9 op-site dispatch blocks to it — CLI-observable behavior byte-identical (186 passed / 2 xfailed / 29 snapshots; the one snapshot delta is a pre-existing-crash traceback line number shifting 635→652).**

## Performance
- **Duration:** ~20 min
- **Started:** 2026-05-27
- **Completed:** 2026-05-27
- **Tasks:** 2 (Task 1 TDD: RED test commit, then GREEN implementation commit)
- **Files modified:** 2 (+ 2 created)

## Accomplishments
- Created `firestarter/chip_resolver.py` as a flat leaf sibling module (MIT header in `address_parser.py` style): imports `from firestarter.database import EpromDatabase` + `from firestarter.exceptions import ChipNotFoundError` (no star imports). One public function `resolve_chip(name: str, db: EpromDatabase | None = None) -> dict`: when `db is None` constructs production `EpromDatabase()` (honors ~/.firestarter — D-01), then `full = db.get_eprom(name)`, `data = db.convert_to_programmer(full) if full else None`, `if not data: raise ChipNotFoundError(name)` else `return data`. Module + function docstrings document the `db` injection seam and the raise-on-miss contract.
- Created `tests/test_chip_resolver.py` (4 cases) following `test_eprom_database.py`: a `db` fixture returning `EpromDatabase(skip_local_override=True)` (mandatory isolation seam, every data-asserting test uses it). Cases: hit returns dict (`memory-size == 65536`), required programmer keys present, miss → `ChipNotFoundError` (via `pytest.raises`), round-trip identity vs `db.convert_to_programmer(db.get_eprom(...))`.
- Repointed all 9 op sites in `main.py` to a module-level `_resolve_or_exit(name, db) -> dict | None` helper (added before `main()`) that wraps `resolve_chip` in `try/except ChipNotFoundError`, logging the exact `f"EPROM '{name}' not found in database."` and returning `None`. Each site collapsed from the 6–7-line `get_eprom`/`convert`/`log`/`return 1` block to `eprom_data = _resolve_or_exit(args.eprom, db_instance)` + `if not eprom_data: return 1`. Sites: read, write, verify, blank, erase, id (8-space), dev read, dev addr (12-space), and the consistency-check ternary site (D-04 — downstream `consistency_check_eprom(args.eprom, eprom_data, ...)` + D-05 3-way verdict preserved).
- Added two imports to the `firestarter.*` group (ruff-isort order): `from firestarter.chip_resolver import resolve_chip` and `from firestarter.exceptions import ChipNotFoundError`. The `info`/`list`/`search` lookups (D-02) and the `main.py:23` star-import (Plan 39-02) were deliberately left untouched.
- Verified behavior preservation: full suite **186 passed, 2 xfailed, 29 snapshots** (182 baseline + 4 new chip_resolver tests; the 2 Phase 36 xfails stay xfail). bad-chip characterization (GATE-1.8b) and consistency-check integration (GATE-1.8d) both green. `ruff check firestarter/main.py` clean; mypy watermark **41 ≤ 44** (unchanged).

## TDD Gate Compliance
Task 1 declares `tdd="true"`. Gate sequence verified in the submodule git log:
1. **RED** — `test(39-01): add test_chip_resolver.py (RED — chip_resolver.py absent)` — `9537256`. Committed test-only; `chip_resolver.py` did not yet exist (import would fail at collection).
2. **GREEN** — `feat(39-01): add chip_resolver.resolve_chip — single DB-lookup chokepoint, ChipNotFoundError on miss (DATA-01)` — `37d3fe5`. All 4 cases pass.
No REFACTOR commit needed (the GREEN implementation was already clean).

## Task Commits
All commits made inside the `firestarter_app` submodule on branch `v1.8-app-cleanup`:
1. **Task 1 (RED):** `test(39-01): add test_chip_resolver.py (RED — chip_resolver.py absent)` — `9537256`
2. **Task 1 (GREEN):** `feat(39-01): add chip_resolver.resolve_chip — single DB-lookup chokepoint, ChipNotFoundError on miss (DATA-01)` — `37d3fe5`
3. **Task 2:** `refactor(39-01): repoint 9 op sites to _resolve_or_exit/resolve_chip; collapse get_eprom+convert copy-paste (DATA-01)` — `b03fe4c`

_SUMMARY.md and meta-repo files (STATE.md, ROADMAP.md, REQUIREMENTS.md, gitlinks) intentionally NOT committed by this executor — the orchestrator owns meta-repo writes._

## Files Created/Modified
- `firestarter_app/firestarter/chip_resolver.py` (created) — flat leaf; `resolve_chip` signature `resolve_chip(name: str, db: EpromDatabase | None = None) -> dict`; raises `ChipNotFoundError`; no star imports.
- `firestarter_app/tests/test_chip_resolver.py` (created) — 4 unit cases via the `EpromDatabase(skip_local_override=True)` fixture.
- `firestarter_app/firestarter/main.py` (modified) — 2 imports + `_resolve_or_exit` helper + 9 op sites repointed. `convert_to_programmer` now appears ONLY at the untouched info site (:649). `_resolve_or_exit` referenced 10× (1 def + 9 calls). "not found in database" reduced to 2 (helper + info). star-import on :23 untouched (39-02).
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` (modified) — single-line update (see Deviations).

## Decisions Made
- None beyond the locked plan decisions (D-01..D-05). The resolver contract, the `db` seam, the shared-helper choice, the consistency-check special case, and the info/list/search exclusions all followed the plan + RESEARCH + PATTERNS exactly.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — non-blocking] Updated the `test_info_known_chip` stderr snapshot for a traceback line-number shift (635 → 652)**
- **Found during:** Task 2 (full-suite gate)
- **Issue:** `test_characterization.py::test_info_known_chip` is a characterization snapshot that pins a *pre-existing* `info`-command crash (`TypeError` in `ic_layout.py`, vpp-pin comparison) — including the stderr traceback, which embeds the absolute source line of the `prepare_detailed_eprom_data` call in `main.py`. Adding 2 imports + the `_resolve_or_exit` helper *above* that call shifted it from line 635 to 652. syrupy normalizes the path (`<PATH>`) but not line numbers, so the stderr snapshot mismatched on that one line.
- **Fix:** Regenerated only that snapshot (`pytest tests/test_characterization.py::test_info_known_chip --snapshot-update`). The `info` site code is byte-identical (untouched, D-02); the crash, exit code 1, and the rest of the traceback are unchanged. `git diff` of the `.ambr` is exactly one line: `-    File "<PATH>", line 635, in main` / `+    File "<PATH>", line 652, in main`.
- **Files modified:** firestarter_app/tests/__snapshots__/test_characterization.ambr (1 line)
- **Verification:** full suite 186 passed / 2 xfailed / 29 snapshots; `.ambr` diff is the single line-number line only.
- **Committed in:** `b03fe4c` (with the Task 2 main.py change)

---
**Total deviations:** 1 auto-fixed (0 blocking). **Impact:** none on behavior — the snapshot pins a pre-existing crash whose source line legitimately moved when the helper/imports were added above it. No `info`-path behavior change.

## Issues Encountered
- The 6 standard op-site blocks are byte-identical; to avoid an ambiguous edit, each site was anchored on its unique `elif args.command == "..."` / `if args.dev_command == "..."` dispatch line. The 8-space (top-level dispatch) and 12-space (dev sub-dispatch) indentations were handled distinctly.

## User Setup Required
None.

## Next Phase Readiness
- `chip_resolver.resolve_chip` is the stable chokepoint Phase 41's Click handlers will call; `_resolve_or_exit` is the single adapter Phase 41 will replace with Click error mapping.
- Plan 39-02 (this wave's successor) owns the `main.py:23` star-import removal — left intentionally green here.
- No blockers.

## Threat Flags
None — pure host-only refactor. `resolve_chip(name)` flows the operator-supplied chip name into the existing local-JSON `.lower()` lookup; no new trust boundary, network, serial, file I/O, or auth surface (matches plan threat_model T-39-01 / T-39-SC accepted). No package installs. Wire protocol frozen (GATE-1.8a); bad-chip path log + exit 1 preserved (GATE-1.8b); read-path use of chip data unchanged (GATE-1.8d).

## Self-Check: PASSED
- `firestarter_app/firestarter/chip_resolver.py` exists (FOUND); `resolve_chip(name: str, db: EpromDatabase | None = None) -> dict` present; `from firestarter.exceptions import ChipNotFoundError` present; no star import.
- `firestarter_app/tests/test_chip_resolver.py` exists (FOUND); `skip_local_override=True` seam used; 4 cases GREEN.
- Commits `9537256` (RED), `37d3fe5` (GREEN), `b03fe4c` (repoint) exist in the `firestarter_app` submodule (FOUND).
- Full suite: 186 passed, 2 xfailed, 29 snapshots (182 baseline + 4 new; both Phase 36 xfails remain xfail).
- 9 op sites repointed: `convert_to_programmer` only at info site (:649); `_resolve_or_exit` ×10 (1 def + 9 calls); "not found in database" ×2; no `db_instance.get_eprom(args.eprom)` op-site pairs remain.
- ruff check `firestarter/main.py` clean; mypy watermark 41 ≤ 44.
- `.ambr` snapshot diff is exactly the one pre-existing-crash traceback line number.

---
*Phase: 39-database-cleanup-chip-resolver*
*Completed: 2026-05-27*

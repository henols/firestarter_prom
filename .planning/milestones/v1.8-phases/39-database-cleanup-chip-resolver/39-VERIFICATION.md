---
phase: 39-database-cleanup-chip-resolver
verified: 2026-05-27T00:00:00Z
status: passed
score: 4/4 success criteria verified (+ 5 GATE-1.8 standing checks green)
overrides_applied: 0
re_verification:
  previous_status: none
  note: Initial verification — no prior VERIFICATION.md existed.
---

# Phase 39: Database Cleanup + chip_resolver Verification Report

**Phase Goal:** The 9× chip-lookup boilerplate copy-pasted across handlers is eliminated by a single `resolve_chip()` function. All `from firestarter.constants import *` star-imports are replaced with named imports. Wire-protocol constants carry clear firmware-sync markers; `COMMAND_FW_VERSION` is verified present. The DIP→RURP pin-mapping documentation is clarified to remove the apparent "two sources of truth" ambiguity.
**Verified:** 2026-05-27
**Status:** passed
**Re-verification:** No — initial verification

All evidence drawn from the `firestarter_app` submodule (branch `v1.8-app-cleanup`), 7 commits `9537256..6e32b37` on Phase 38 base `efb0fad`. SUMMARY claims were NOT trusted — every truth was checked against the actual code, git log, live ruff/mypy runs, and a live test execution.

## Goal Achievement

### Observable Truths (the 4 ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | SC#1 — `firestarter/chip_resolver.py` exists with `resolve_chip(name) -> dict` raising `ChipNotFoundError` on miss; `tests/test_chip_resolver.py` passes; the 9 copy-paste op sites are gone | ✓ VERIFIED | `chip_resolver.py` (37 lines) defines `resolve_chip(name: str, db: EpromDatabase | None = None) -> dict` with the exact `get_eprom → convert_to_programmer → if not data: raise ChipNotFoundError(name)` body and db injection seam. `test_chip_resolver.py` has 4 tests (hit, required-keys, miss→raise, round-trip identity) — all 4 pass live. `grep -c "db_instance.get_eprom(args.eprom)" main.py` == 0. _resolve_or_exit helper defined once at :521, called 9 times at lines 677, 693, 708, 723, 734, 748, 864, 891, 902 — 1 def + 9 calls confirmed. `convert_to_programmer` at the info site (:649) only (D-02). |
| 2 | SC#2 — `pin_conversions` in database.py carries a comment block stating it encodes RURP board-wiring (DIP socket pin → bus line), DISTINCT from pinouts.json (chip function → socket pin); no behavior change | ✓ VERIFIED | Lines 68–74 of database.py: `# pin_conversions: RURP board-wiring layer. / # Maps DIP socket pin number → RURP bus line number (hardware-specific). / # This is DISTINCT from pinouts.json (loaded as self.pin_maps), which maps / # chip pin function → DIP socket pin number (chip-specific). / # They COMPOSE in get_bus_config()...`. `grep -i "board-wiring" database.py` returns line 68; `grep -i "pinouts.json"` returns lines 71–72 inside the new block. Dict contents and all logic byte-identical. DB tests pass: `pytest tests/test_eprom_database.py` green. |
| 3 | SC#3 — `grep -r "from firestarter.constants import \*" firestarter/` returns no results; modules use named imports; mypy not increased vs watermark (44) | ✓ VERIFIED | Repo-wide star-import grep returns empty. Named imports confirmed in all 6 modules: main.py (`FLAG_CHIP_ENABLE, FLAG_OUTPUT_ENABLE` — 2 names, ruff ground-truth correction from RESEARCH list of 11 per D-06), serial_comm.py (9 names), eprom_operations.py (15 names), database.py (1 name), firmware.py (5 names), hardware.py (4 names — ruff correction from 5, D-06). No `noqa: F403` or `noqa: F405` markers remain anywhere in `firestarter/`. The 3 intentional F401 markers preserved: serial_comm.py (1), firmware.py (1), eprom_operations.py (1). `ruff check firestarter/` → "All checks passed!". mypy watermark: 41 errors, watermark 44 — unchanged and within gate. |
| 4 | SC#4 — `constants.py` has `COMMAND_FW_VERSION` (== 0x0D / 13) verified present; wire-protocol blocks carry firmware-sync markers; parity test passes | ✓ VERIFIED | Line 39: `COMMAND_FW_VERSION = 13` (== 0x0D, confirmed). Line 25: `# Wire-protocol command codes — Firmware sync: firestarter.h`. Line 59: `# Control Flags — Firmware sync: firestarter.h`. `grep -c "Firmware sync" constants.py` == 2. CTRL_*/REVISION_* blocks already carry their own source-naming headers (rurp_pinout.h / rurp_shield.h) — left unchanged per D-10. `pytest tests/test_revision_constants_parity.py -v` → 4 passed (including `COMMAND_FW_VERSION == 0x0D` at :116). |

**Score:** 4/4 truths verified

### GATE-1.8 Standing Checks

| Gate | Check | Status | Evidence |
| ---- | ----- | ------ | -------- |
| 1.8a | Wire protocol byte-identical | ✓ VERIFIED | No firmware files touched; constants.py values unchanged (comments-only edits in 39-03). ruff clean; snapshot suite 29/29 passed. |
| 1.8b | bad-chip not-found path preserved (log + exit 1) | ✓ VERIFIED | `_resolve_or_exit` helper logs `f"EPROM '{name}' not found in database."` via `logger.error` and returns `None`; each op site follows with `if not eprom_data: return 1`. "not found in database" appears exactly 2× in main.py (helper + info site). `pytest -k bad_chip` → 1 passed (snapshot unchanged). |
| 1.8c | Constant contract preserved | ✓ VERIFIED | `COMMAND_FW_VERSION = 13` unchanged. parity suite `test_revision_constants_parity.py` → 4 passed. No constant values modified in any Phase 39 commit. |
| 1.8d | Read path ring-fenced (eprom_data flows to consistency_check_eprom) | ✓ VERIFIED | Lines 902–910 of main.py: `eprom_data = _resolve_or_exit(args.eprom, db_instance)` → guard → `return eprom_operator.consistency_check_eprom(args.eprom, eprom_data, ...)`. `pytest -k consistency_check` → 8 passed. |
| 1.8e | Full suite green + ruff clean + mypy within watermark | ✓ VERIFIED | `pytest -p no:cacheprovider` → **186 passed, 2 xfailed, 29 snapshots**. Both Phase 36 xfails remain xfail (not xpass). `ruff check firestarter/` → "All checks passed!". mypy: 41 errors ≤ watermark 44. |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `firestarter/chip_resolver.py` | `resolve_chip(name, db=None) -> dict`, raises `ChipNotFoundError` | ✓ VERIFIED | 37 lines, MIT header, one public function with exact signature and docstring documenting db injection seam. No star imports. Imports: `EpromDatabase`, `ChipNotFoundError`. |
| `tests/test_chip_resolver.py` | 4 unit tests using `skip_local_override=True` fixture | ✓ VERIFIED | 54 lines, `db` fixture returns `EpromDatabase(skip_local_override=True)`, 4 test functions (hit, required-keys, miss→raise, round-trip). All 4 pass. |
| `firestarter/main.py` | op sites repointed; named constants import; `_resolve_or_exit` helper | ✓ VERIFIED | `from firestarter.constants import FLAG_CHIP_ENABLE, FLAG_OUTPUT_ENABLE` at :24. `from firestarter.chip_resolver import resolve_chip` at :22. `_resolve_or_exit` defined at :521, called ×9. `db_instance.get_eprom(args.eprom)` count == 0. |
| `firestarter/serial_comm.py` | Named imports (9 constants); F401 marker preserved | ✓ VERIFIED | `from firestarter.constants import (` at :24 with 9 names. F401 count == 1 (frame_parser re-export). |
| `firestarter/eprom_operations.py` | Named imports (15 constants); F401 marker preserved | ✓ VERIFIED | `from firestarter.constants import (` at :27 with 15 names. F401 count == 1 (MSG_DATA_CHUNK local). |
| `firestarter/database.py` | Named import (FLAG_CAN_ERASE); board-wiring comment | ✓ VERIFIED | `from firestarter.constants import FLAG_CAN_ERASE` at :33. Board-wiring comment block at lines 68–74. |
| `firestarter/firmware.py` | Named imports (5 constants); F401 marker preserved | ✓ VERIFIED | `from firestarter.constants import (` at :28 with 5 names. F401 count == 1 (FirmwareOperationError orphan). |
| `firestarter/hardware.py` | Named imports (4 constants, ruff-corrected from 5) | ✓ VERIFIED | `from firestarter.constants import (` at :14 with 4 names (COMMAND_READ dropped per ruff D-06). |
| `firestarter/constants.py` | `COMMAND_FW_VERSION = 13`; 2 firmware-sync markers | ✓ VERIFIED | Line 39: `COMMAND_FW_VERSION = 13`. Line 25: COMMAND_* sync marker. Line 59: FLAG_* sync marker. `grep -c "Firmware sync"` == 2. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `chip_resolver.py` | `firestarter.exceptions` | `from firestarter.exceptions import ChipNotFoundError` | ✓ WIRED | Present at line 11. Used in `raise ChipNotFoundError(name)` at line 35. |
| `chip_resolver.py` | `firestarter.database` | `from firestarter.database import EpromDatabase` | ✓ WIRED | Present at line 10. Used in `if db is None: db = EpromDatabase()`, `db.get_eprom`, `db.convert_to_programmer`. |
| `main.py` | `chip_resolver.py` | `resolve_chip(` called at 9 op sites | ✓ WIRED | `resolve_chip` imported at :22; called by `_resolve_or_exit` at :530; `_resolve_or_exit` called ×9 at op sites. |
| all 6 modules | `constants.py` | explicit named imports | ✓ WIRED | Verified: `grep "from firestarter.constants import" firestarter/*.py` returns 6 lines, one per module, all named. |
| `constants.py` | `firestarter/include/firestarter.h` | `# Firmware sync: firestarter.h` documentary markers | ✓ WIRED | 2 markers present (COMMAND_* block :25, FLAG_* block :59). Documentary only — no runtime import. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| `resolve_chip('W27C512')` returns dict with memory-size == 65536 | `pytest tests/test_chip_resolver.py::test_resolve_chip_hit_returns_dict -v` | PASSED | ✓ PASS |
| `resolve_chip('NOTACHIP_XYZ_DOESNOTEXIST')` raises ChipNotFoundError | `pytest tests/test_chip_resolver.py::test_resolve_chip_miss_raises -v` | PASSED | ✓ PASS |
| bad-chip CLI path exits 1 with correct log message | `pytest -k bad_chip -v` | 1 passed (snapshot) | ✓ PASS |
| consistency-check eprom_data flow intact | `pytest -k consistency_check -v` | 8 passed | ✓ PASS |
| Parity test: COMMAND_FW_VERSION == 0x0D | `pytest tests/test_revision_constants_parity.py -v` | 4 passed | ✓ PASS |
| ruff clean after star-import sweep | `python -m ruff check firestarter/` | "All checks passed!" | ✓ PASS |
| mypy within watermark | `python tools/check_mypy_watermark.py` | 41 errors ≤ 44 | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| DATA-01 | 39-01 | Single `resolve_chip(name) -> programmer_config` replaces 9-handler copy-paste | ✓ SATISFIED | `chip_resolver.py` exists; 9 op sites use `_resolve_or_exit`; `get_eprom(args.eprom)` count == 0 at op sites |
| DATA-02 | 39-03 | DIP→RURP pin-mapping documented as single source per layer (not duplicate) | ✓ SATISFIED | `pin_conversions` comment block at database.py:68–74 names each layer and composition point; no merge performed (D-05 intentional) |
| DATA-03 | 39-02 | Star-imports replaced with named imports across all modules | ✓ SATISFIED | Repo-wide grep empty; 6 modules use named imports; ruff clean |
| DATA-04 | 39-03 | Wire-protocol constants carry firmware-sync markers; `COMMAND_FW_VERSION` verified present | ✓ SATISFIED | 2 `# Firmware sync: firestarter.h` markers; `COMMAND_FW_VERSION = 13` at :39; parity test 4/4 |

### Anti-Patterns Found

No debt markers (TBD/FIXME/XXX) found in any Phase 39 modified file. No stubs or placeholder implementations detected. The two SC deviations noted below (D-06 import-list corrections) were auto-fixed by the executor using ruff as ground truth per the plan directive — both resulted in smaller named-import lists that exactly match actual usage.

| File | Pattern | Severity | Impact |
| ---- | ------- | -------- | ------ |
| — | None found | — | — |

### Documented SC Deviations (informational — all intentional per plan)

| Deviation | Description | Impact |
| --------- | ----------- | ------ |
| D-02 | info/list/search lookups retained — not op sites (D-02); `get_eprom` at :641 and `convert_to_programmer` at :649 are presentation paths deliberately excluded | None — SC#1's criterion is op-site count == 0, which is satisfied |
| D-05 | DATA-02 is documentation-only, not a merge — `pin_conversions` and `pinouts.json` encode distinct layers | None — SC#2 accepts a docstring/comment; "board-wiring" grep passes |
| D-06 | SC#3 names 4 modules but 6 required (repo-wide grep passes only with all 6 converted); main.py uses 2 names not 11 (CTRL_* unused in code); hardware.py uses 4 names not 5 (COMMAND_READ unused) | None — ruff is the ground-truth authority per plan; all corrections produce a cleaner result |
| D-09/D-10 | "add COMMAND_FW_VERSION if absent" is a no-op — already present at :39 (now :39 post-marker shift) | None — verify-only satisfied |
| D-11 | SC#1 says `test_chip_resolver.py` is "from Phase 36" — it was created by Plan 39-01 (Phase 36 never created it) | None — the test exists and passes; the SC's intent is fulfilled |
| D-11 | SC#4 calls the parity test `test_firmware_contract_parity.py` — the real file is `tests/test_revision_constants_parity.py` | None — the real file has 4 tests and is green |

### Human Verification Required

None. This is a pure-software host-CLI refactor with a complete automated safety net (186 tests + 29 snapshots + ruff + mypy). All SC criteria are machine-verifiable and were verified above.

---

_Verified: 2026-05-27_
_Verifier: Claude (gsd-verifier)_

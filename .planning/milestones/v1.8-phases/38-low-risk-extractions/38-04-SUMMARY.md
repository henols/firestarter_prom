---
phase: 38-low-risk-extractions
plan: 04
subsystem: refactoring
tags: [python, address-parsing, module-extraction, host-cli, leaf-module, tdd]

# Dependency graph
requires:
  - phase: 36-characterization-test-baseline
    provides: "172-test + 29-snapshot safety net (incl. bad --address / bad --size CLI snapshots) proving behavior preservation"
  - phase: 37-tooling-baseline-ci-gate
    provides: "ruff + ruff-format + mypy watermark (44) CI gate"
  - phase: 38-low-risk-extractions
    plan: 01
    provides: "stable consolidated exception import surface in eprom_operations.py (from firestarter.exceptions import ...)"
provides:
  - "firestarter/address_parser.py — pure stdlib-only leaf with parse_address/parse_size (ValueError contract, None passthrough)"
  - "_setup_operation rewired to consume address_parser via try/except ValueError preserving exact log strings + (None, 0) graceful-fail"
affects: [41-cli-handlers, 42-error-handling-normalization]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pure-leaf parsing module (zero package-internal imports; stdlib + typing only)"
    - "Raise-then-catch extraction: parser raises ValueError, single call site catches + logs, CLI behavior byte-identical"

key-files:
  created:
    - firestarter_app/firestarter/address_parser.py
    - firestarter_app/tests/test_address_parser.py
  modified:
    - firestarter_app/firestarter/eprom_operations.py

key-decisions:
  - "address_parser.py is a pure stdlib leaf (D-11): zero `from firestarter`/`import firestarter` lines; only `from typing import Optional  # noqa: UP035`"
  - "Two separate public functions parse_address/parse_size (NOT consolidated): clearer + independently testable; both `int(s,16) if 0x else int(s)`, None passthrough, bare ValueError"
  - "command_dict['address'] set ONLY inside `if address:` (D-13): never assigned when no address given; `addr = 0` local default retained for the memory-size computation"
  - "Exact log f-strings preserved verbatim (D-12): 'Invalid address format: {address}' / 'Invalid size format: {size}'; both bad-input paths still `return None, 0`"
  - "`or 0` added at the two assignment sites to narrow Optional[int]→int for mypy (Rule 3 fix): byte-identical runtime because the truthy-string guards (`if address:` / `if ... and size:`) mean the parser never returns None there"

patterns-established:
  - "Pure-leaf parsing module: hex/decimal string parsing extracted into one stdlib-only file with explicit ValueError contract"
  - "Raise-then-catch refactor: leaf raises, single CLI-facing call site wraps in try/except + logs, preserving byte-identical external behavior (GATE-1.8b)"

requirements-completed: [STRUCT-03]

# Metrics
duration: 14min
completed: 2026-05-27
---

# Phase 38 Plan 04: Address Parser Extraction Summary

**Inline hex/decimal address+size parsing extracted from `eprom_operations._setup_operation` into a new pure stdlib-only leaf `firestarter/address_parser.py` (`parse_address`/`parse_size` with an explicit `ValueError` contract), with the single call site rewired to `try/except ValueError` preserving the exact log strings and `(None, 0)` graceful-fail — CLI-observable behavior byte-identical (182 passed / 2 xfailed / 29 snapshots unchanged).**

## Performance

- **Duration:** ~14 min
- **Started:** 2026-05-27
- **Completed:** 2026-05-27
- **Tasks:** 2 (TDD: RED test commit, then GREEN implementation commit)
- **Files modified:** 1 (+ 2 created)

## Accomplishments
- Created `firestarter/address_parser.py` as a pure stdlib-only leaf (D-11): two PUBLIC functions `parse_address(s)` / `parse_size(s)`, each `if s is None: return None` else `int(s, 16) if "0x" in s.lower() else int(s)`, letting `int()` raise `ValueError` naturally on bad input. Kept as two separate functions (not consolidated). Only import is `from typing import Optional  # noqa: UP035` (house style — no `X | None`). No logger, no package imports.
- Created `tests/test_address_parser.py` with 10 unit cases across `TestParseAddress` (hex 0x, uppercase 0X, decimal, None, invalid→ValueError, empty→ValueError) and `TestParseSize` (hex, decimal, None, invalid→ValueError). Pure-unit, no fixtures, `pytest.raises(ValueError)` for error cases.
- Rewired `_setup_operation` in `eprom_operations.py`: added `from firestarter.address_parser import parse_address, parse_size` to the firestarter.* import group; replaced the two inline `int(...)` parse blocks with the parser calls inside the existing `try/except ValueError` wrappers. Preserved the `addr = 0` default, the `if address:` block (with `command_dict["address"]` set ONLY inside it — D-13), the `if cmd == COMMAND_READ and size:` gate, the exact log f-strings (D-12), and both `return None, 0` graceful-fail paths.
- Verified behavior preservation: full Phase 36 safety net green and unchanged (182 passed — 172 baseline + 10 new address_parser cases; 2 xfailed stay xfailed, not xpassed; 29 snapshots), `git diff tests/__snapshots__/` empty (bad-address / bad-size CLI behavior byte-identical), ruff check + ruff-format clean, mypy at watermark 44 (not exceeded).

## TDD Gate Compliance
The plan declares `tdd="true"` on Task 1. Gate sequence verified in the submodule git log:
1. **RED** — `test(38-04): add test_address_parser.py (RED — address_parser.py absent)` — `aa61219`. Confirmed failing at collection (`ModuleNotFoundError: No module named 'firestarter.address_parser'`) before any implementation existed.
2. **GREEN** — `refactor(38-04): extract address_parser.py with ValueError contract; wrap _setup_operation call site` — `8e073b9`. All 10 cases pass; full suite green.
No REFACTOR commit needed (the GREEN implementation was already clean; the `or 0` narrowing was part of the GREEN commit, not a separate refactor pass).

## Task Commits

Both commits made inside the `firestarter_app` submodule on branch `v1.8-app-cleanup`:

1. **Task 1 (RED):** `test(38-04): add test_address_parser.py (RED — address_parser.py absent)` — `aa61219`
2. **Task 2 (GREEN):** `refactor(38-04): extract address_parser.py with ValueError contract; wrap _setup_operation call site` — `8e073b9`

_SUMMARY.md and meta-repo files (STATE.md, ROADMAP.md, REQUIREMENTS.md) intentionally NOT committed by this executor — the orchestrator owns meta-repo writes. The meta-repo `M firestarter` / `M firestarter_app` gitlinks were left alone._

## Files Created/Modified
- `firestarter_app/firestarter/address_parser.py` (created) — Pure stdlib-only leaf; 7-line MIT header (copyright 2024) + one-line docstring; `from typing import Optional  # noqa: UP035`; two public functions `parse_address`/`parse_size` (None passthrough, hex/decimal parse, bare ValueError on bad input). `grep -c '^from firestarter\|^import firestarter'` returns 0 (pure leaf).
- `firestarter_app/tests/test_address_parser.py` (created) — 10 unit cases (TestParseAddress + TestParseSize). Imports `from firestarter.address_parser import parse_address, parse_size`. No fixtures.
- `firestarter_app/firestarter/eprom_operations.py` (modified) — Added the address_parser import to the firestarter.* group; replaced the two inline `int(...)` parse expressions with `parse_address(address) or 0` / `parse_size(size) or 0` inside the unchanged `try/except ValueError` wrappers. Star-import `# noqa: F403` and the `# noqa: F405` on the `COMMAND_READ` gate untouched (Phase 39). globals() sites at lines 165/232 untouched (Plan 05). eprom_operations.py:265/283 comm-error bug NOT fixed (Phase 42).

## Decisions Made
- None beyond the locked plan decisions (D-11, D-12, D-13). Function membership, the two-separate-functions choice, the None-passthrough/raise contract, the call-site wrapper structure, and the D-13 address-key subtlety all followed the plan + PATTERNS exactly.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added `or 0` at the two `_setup_operation` assignment sites to keep the mypy watermark at 44**
- **Found during:** Task 2 (mypy watermark gate)
- **Issue:** `parse_address`/`parse_size` are typed `(s: Optional[str]) -> Optional[int]`. The original inline expressions returned plain `int`, so `addr = parse_address(address)` (reassigning the `int`-typed `addr` local) and `command_dict["memory-size"] = addr + read_size` (adding two `int | None`) each produced a NEW mypy error — `eprom_operations.py:181 [assignment]` and `:193 [operator]` — pushing the count to **46**, over the watermark of **44**. The acceptance gate `python tools/check_mypy_watermark.py` would have failed (`FAIL: 46 errors exceeds watermark 44`).
- **Fix:** Narrowed both assignments to `int` with `parse_address(address) or 0` and `parse_size(size) or 0`. This is **byte-identical at runtime**: both expressions sit behind truthy-string guards (`if address:` and `if cmd == COMMAND_READ and size:`), so the parser is only ever called with a non-empty string and returns a real `int`, never `None`; even for a literal `"0"`/`"0x0"` input the parse yields `0` and `0 or 0 == 0`, matching the original exactly. `command_dict["address"]` therefore still stores the same value the original code stored, and the D-13 "set only inside `if address:`" subtlety is unchanged.
- **Files modified:** firestarter_app/firestarter/eprom_operations.py (2 lines)
- **Verification:** `python tools/check_mypy_watermark.py` → `mypy errors: 44 (watermark: 44) OK`; the previously-new errors at lines 181/193 are gone; full suite still 182/2/29; ruff clean; snapshot diff empty.
- **Committed in:** `8e073b9` (part of the GREEN commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The single auto-fix was necessary to satisfy the plan's own mypy watermark acceptance gate (GATE-1.8e) without exceeding watermark 44. The PATTERNS function bodies and call-site wrapper anticipated the `Optional[int]` typing but did not spell out the narrowing at the int-typed `addr`/`addr + read_size` sites; `or 0` is the minimal, zero-runtime-change, no-new-import narrowing (the codebase uses neither `cast` nor `assert ... is not None`). No scope creep — two `or 0` tokens, no logic change, behavior byte-identical.

## Issues Encountered
- **Ruff import-grouping auto-fix on the new test file (Task 1).** The PATTERNS test template showed a blank line between `import pytest` and `from firestarter.address_parser import ...`. Because `firestarter.address_parser` did not yet exist at RED time, ruff's isort grouped both lines as a single block and flagged `I001` (un-sorted import block). `ruff check --fix` removed the intervening blank line; this is the correct house-style result and was committed with the RED test. The RED gate (collection failure / ImportError) still held after the fix.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- `firestarter/address_parser.py` exists as a stable pure-leaf parsing module; Phase 41 (CLI handlers) and Phase 42 (error-handling normalization) can rely on the explicit ValueError contract.
- No blockers. The eprom_operations.py:265/283 comm-error bug remains as-is (xfail) for Phase 42; the globals() sites (lines 165/232) remain for Plan 05's dead-code sweep; star-import `# noqa: F403/F405` annotations remain parked for Phase 39.

## Threat Flags
None — this plan only moved hex/decimal string parsing from an inline expression into a named pure-function leaf and wrapped the (now-raising) calls in the SAME pre-existing `try/except ValueError`. No new trust boundary, network, serial, file I/O, or auth surface introduced. The CLI `--address`/`--size` string boundary is pre-existing and unchanged (matches plan threat_model: T-38-04 / T-38-SC accepted; `int(s,16)`/`int(s)` parsing identical to before, no `eval`/`exec`, no injection surface). Phase 36 bad-input snapshots pinned and unchanged.

## Self-Check: PASSED
- `firestarter_app/firestarter/address_parser.py` exists (FOUND).
- `firestarter_app/tests/test_address_parser.py` exists (FOUND).
- Commit `aa61219` (RED test) exists in the `firestarter_app` submodule (FOUND).
- Commit `8e073b9` (GREEN impl) exists in the `firestarter_app` submodule (FOUND).
- `test_address_parser.py`: 10 cases GREEN. Full suite: 182 passed, 2 xfailed, 29 snapshots (172 baseline + 10 new).
- `git diff tests/__snapshots__/` empty (bad-address/bad-size CLI behavior byte-identical).
- ruff check + ruff format --check clean (firestarter/ AND tests/); mypy at watermark 44 (not exceeded).
- address_parser.py pure stdlib leaf: `grep -c '^from firestarter\|^import firestarter'` returns 0.

---
*Phase: 38-low-risk-extractions*
*Completed: 2026-05-27*

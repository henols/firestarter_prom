# Phase 39: Database Cleanup + chip_resolver — Research

**Researched:** 2026-05-27
**Domain:** Python host CLI refactor — chip resolution, named imports, constants annotation
**Confidence:** HIGH (all claims verified against live codebase)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01:** `chip_resolver.resolve_chip(name: str) -> dict` returns the converted programmer config
(today's `db.convert_to_programmer(db.get_eprom(name))` result) and raises `ChipNotFoundError`
on a miss (chip absent OR conversion yields falsy). Imports `ChipNotFoundError` from
`firestarter.exceptions`. `chip_resolver.py` is a flat sibling module; stdlib + package imports
only.

**D-02:** Replaces exactly the 9 copy-paste op sites in `main.py`:
`read` (`:660`), `write` (`:680`), `verify` (`:699`), `blank` (`:718`),
`erase` (`:733`), `id` (`:751`), and the 3 `dev` sites — `dev read` (`:871`),
`dev addr` (`:902`), `dev consistency-check` (`:917`).
`info`/`list`/`search` are NOT touched.

**D-03:** Observable behavior is byte-identical (GATE-1.8b). Each of the 9 sites logs
`f"EPROM '{args.eprom}' not found in database."` and returns exit code 1 on a miss.
Catch `ChipNotFoundError` at the dispatch (shared helper or per-site `try/except` —
planner's call). The Phase 36 snapshots for the bad-chip path MUST still pass unchanged.

**D-04 (subtlety):** `dev consistency-check` (`:917-919`) currently calls
`convert_to_programmer(...)` and discards the result (presence check only). Using
`resolve_chip()` there is behavior-equivalent — do not change what chip data is used
for downstream.

**D-05:** Documentation-only — zero behavior change. Add a docstring on `pin_conversions`
explicitly stating it encodes RURP board-wiring (socket-pin→bus-line), distinct from
`pinouts.json` (function→socket-pin). Do NOT merge.

**D-06:** Replace `from firestarter.constants import *` with explicit named imports in
**all 6** star-importing modules: `main.py:23`, `serial_comm.py:24`,
`eprom_operations.py:27`, `database.py:33`, `firmware.py:28`, and `hardware.py:14`.
SC#3 names only 4, but repo-wide grep requires all 6 — documented deviation.

**D-07:** Rejected namespace import (`from firestarter import constants` + `constants.X`
prefixing) — it would rewrite every usage site = large diff, wrecks git blame.

**D-08:** Strip the now-obsolete `# noqa: F403`/`# noqa: F405` markers in the same pass.
Touched modules must stay ruff/ruff-format clean and must not raise the mypy watermark.

**D-09:** Mark + verify only — no relocation. Add `# Firmware sync: firestarter.h` marker
comment to the `COMMAND_*` and `FLAG_*` blocks in `constants.py` (`:25-67`).
`CTRL_*` (`:69-81`) and `REVISION_*` (`:83-96`) already carry v1.7 sync-comment headers —
normalize/leave them.

**D-10:** `COMMAND_FW_VERSION` is already present (`constants.py:37`, `= 13` / `0x0D`) and
already parity-tested (`tests/test_revision_constants_parity.py:116`). SC#4's "added if
absent" is a no-op — just verify it stays green. Do NOT relocate codegenerated `messages.py`.

**D-11:** Parity test file is `tests/test_revision_constants_parity.py`, NOT
`test_firmware_contract_parity.py` as SC#4 calls it. Phase 36 extended it in place.

### Claude's Discretion

- Exact named-import lists per module (enumerate what each module actually uses).
- Module/function docstrings; function order in `chip_resolver.py`.
- `chip_resolver` internals: whether `resolve_chip` takes `EpromDatabase` as parameter
  or constructs one — follow Phase 36's de-singleton seam (`skip_local_override`);
  planner picks exact signature so `tests/test_chip_resolver.py` can run without serial I/O.
- The catch-`ChipNotFoundError` mechanism (shared helper vs per-site try/except) as long as
  D-03's observable behavior is byte-identical.
- `tests/test_chip_resolver.py` coverage shape (hit, miss→`ChipNotFoundError`, conversion
  correctness against real `chip_database.json`).
- Plan/wave decomposition. Natural ordering: (1) `chip_resolver.py` + `test_chip_resolver.py`
  + repoint the 9 sites → (2) star-import → named imports + noqa sweep → (3) `pin_conversions`
  docstring → (4) constants sync markers + parity verify.

### Deferred Ideas (OUT OF SCOPE)

- Unifying `FirestarterError` base class — Phase 42.
- Centralized Click error→exit-code mapping for `ChipNotFoundError` — Phase 41/42.
- Folding `info`/`list`/`search` lookups into a richer resolver — considered and rejected.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DATA-01 | New flat `chip_resolver.py` with `resolve_chip(name) -> programmer_config`, eliminating 9× copy-paste in `main.py`; new `tests/test_chip_resolver.py` | 9 op sites confirmed at verified line numbers; `ChipNotFoundError` at `exceptions.py:55`; `skip_local_override` seam confirmed working |
| DATA-02 | Single source of truth for DIP→RURP pin mapping — docstring on `pin_conversions` clarifying `pin_conversions` vs `pinouts.json` are composing layers, not duplicates | Composition verified in `get_bus_config` (~`:262`); `pin_conversions` dict at `database.py:69`; module docstring already references it at lines 23-25 |
| DATA-03 | Replace `from firestarter.constants import *` star-imports with named imports across all 6 modules | All 6 confirmed; exact per-module import lists derived and verified; ~55 noqa markers confirmed |
| DATA-04 | Wire-protocol constants consolidated with firmware-sync markers; `COMMAND_FW_VERSION` verified present | `COMMAND_FW_VERSION = 13` at `constants.py:37`; parity test at `test_revision_constants_parity.py:116`; `COMMAND_*`/:25-55, `FLAG_*`/:57-67 confirmed unmarked |
</phase_requirements>

---

## Summary

Phase 39 is a pure refactor with four deliverables that are independent enough to execute as separate waves. All major claims in the CONTEXT.md have been verified against the live codebase (`v1.8-app-cleanup` branch, `firestarter_app/` sub-repo). The test suite currently shows 182 passed + 2 xfailed with 29 syrupy snapshots — this is the green baseline that must be preserved end-to-end.

The most complex deliverable is DATA-01: creating `chip_resolver.py` and wiring it into 9 call sites in `main.py`. The pattern is mechanical — every op site is the same 4-6 line block — but the `dev consistency-check` site has a subtle difference (it calls `convert_to_programmer` for a presence-check side-effect, not to use the result for the operation's main path). DATA-03 (star-imports → named) is the highest line-count change but lowest risk: every usage site stays unchanged, only the import header changes.

The CONTEXT.md line numbers for the 9 op sites match the live code exactly. The noqa-marker counts match the live code exactly. The COMMAND_FW_VERSION presence and parity test location are verified. The one SC inaccuracy requiring planner awareness: `test_chip_resolver.py` does NOT exist yet (SC#1 says "from Phase 36" — it was not created there; Wave 1 creates it).

**Primary recommendation:** Execute in 4 waves per CONTEXT.md prescribed ordering. Each wave is a self-contained atomic commit with full suite green before advancing.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Chip lookup resolution (`resolve_chip`) | API / Backend (Python host service layer) | — | Pure business logic: DB query + conversion, no I/O |
| Not-found error dispatch (exit-1 + log) | CLI dispatch layer (`main.py`) | — | Still argparse in Phase 39; Click mapping deferred to Phase 41 |
| DIP→RURP pin translation | Database layer (`database.py`) | — | `pin_conversions` dict + `get_bus_config` compose in `convert_to_programmer` |
| Wire-protocol constant definitions | Constants module (`constants.py`) | Firmware header (`firestarter.h`) | Python side of a dual-definition; sync annotation makes the relationship explicit |
| Named-import hygiene | All 6 modules | CI gate (ruff F403/F405) | Import cleanup unlocks mypy strict mode on these modules in Phase 42 |

---

## Standard Stack

No new dependencies are introduced in Phase 39. All work uses the existing package.

### Existing Infrastructure Consumed by This Phase

| Component | Location | Role in Phase 39 |
|-----------|----------|------------------|
| `ChipNotFoundError` | `firestarter/exceptions.py:55` | Raised by `resolve_chip()` on miss |
| `EpromDatabase` | `firestarter/database.py:158` | Used inside `chip_resolver.py` for DB lookup |
| `EpromDatabase(skip_local_override=True)` | constructor seam, `database.py:167` | Used in `test_chip_resolver.py` to avoid serial I/O |
| `pytest` + `syrupy` | `pyproject.toml [test]` deps | Existing test framework; no new packages |
| `ruff` + `ruff-format` | Phase 37 tooling | Must exit 0 after every wave |
| `mypy` watermark gate | `tools/check_mypy_watermark.py` | Must not exceed 44 errors after any wave |

### Package Legitimacy Audit

No new packages are installed in this phase. N/A.

---

## Architecture Patterns

### System Architecture Diagram

```
main.py (argparse dispatch)
    |
    | [currently: 9× copy-paste]
    |   get_eprom(name) → convert_to_programmer(full) → if not data: log+exit1
    |
    | [after Phase 39: DATA-01]
    ↓
chip_resolver.resolve_chip(name, db=None)
    ├── db = EpromDatabase(skip_local_override=False) if db is None
    ├── full = db.get_eprom(name)
    ├── data = db.convert_to_programmer(full) if full else None
    ├── if not data: raise ChipNotFoundError(name)
    └── return data  [programmer config dict]
    |
    | ChipNotFoundError caught at dispatch
    ↓
logger.error(f"EPROM '{name}' not found in database.") + return 1
```

### Recommended Project Structure (after Phase 39)

```
firestarter_app/
├── firestarter/
│   ├── chip_resolver.py     # NEW — DATA-01
│   ├── constants.py         # EDITED — DATA-03 named imports (self), DATA-04 markers
│   ├── database.py          # EDITED — DATA-02 pin_conversions docstring, DATA-03
│   ├── eprom_operations.py  # EDITED — DATA-03 named imports
│   ├── exceptions.py        # READ-ONLY — ChipNotFoundError at :55
│   ├── firmware.py          # EDITED — DATA-03 named imports
│   ├── hardware.py          # EDITED — DATA-03 named imports
│   ├── main.py              # EDITED — DATA-01 (9 sites), DATA-03 named imports
│   └── serial_comm.py       # EDITED — DATA-03 named imports
└── tests/
    └── test_chip_resolver.py  # NEW — DATA-01
```

### Pattern 1: resolve_chip() Signature with Injectable DB

The `chip_resolver.resolve_chip` signature should accept an optional `db` parameter so tests can inject `EpromDatabase(skip_local_override=True)` without serial I/O:

```python
# firestarter/chip_resolver.py
from firestarter.database import EpromDatabase
from firestarter.exceptions import ChipNotFoundError


def resolve_chip(name: str, db: EpromDatabase | None = None) -> dict:
    """Return the programmer-config dict for *name* or raise ChipNotFoundError.

    Uses EpromDatabase.get_eprom() + convert_to_programmer() internally.
    Pass *db* to inject a pre-constructed EpromDatabase (e.g., for tests that
    use skip_local_override=True to avoid loading ~/.firestarter overrides).
    """
    if db is None:
        db = EpromDatabase()
    full = db.get_eprom(name)
    data = db.convert_to_programmer(full) if full else None
    if not data:
        raise ChipNotFoundError(name)
    return data
```

[VERIFIED: live codebase — matches the `db.get_eprom` → `db.convert_to_programmer` pattern at all 9 sites; `skip_local_override` seam confirmed at `database.py:167`]

### Pattern 2: Catch ChipNotFoundError at Dispatch

The cleanest approach consistent with D-03 (byte-identical observable behavior, still argparse, Phase 41 owns Click mapping) is a small shared helper that wraps the resolver call and preserves the exact log+exit:

```python
# In main.py — option A: shared helper
from firestarter.chip_resolver import resolve_chip
from firestarter.exceptions import ChipNotFoundError

def _resolve_or_exit(name: str, db: EpromDatabase) -> dict | None:
    """Resolve chip or log + return None (caller returns 1)."""
    try:
        return resolve_chip(name, db=db)
    except ChipNotFoundError:
        logger.error(f"EPROM '{name}' not found in database.")
        return None
```

Then each of the 9 sites becomes:
```python
    elif args.command == "read":
        eprom_data = _resolve_or_exit(args.eprom, db_instance)
        if not eprom_data:
            return 1
        return 1 if not eprom_operator.read_eprom(...) else 0
```

Option B: per-site `try/except` — larger diff, no functional difference. Planner's call (Claude's Discretion).

[VERIFIED: live codebase — exact log string `f"EPROM '{args.eprom}' not found in database."` confirmed at lines 665, 685, 704, 723, 738, 756, 876, 907, 924]

### Pattern 3: dev consistency-check Subtlety (D-04)

The `dev consistency-check` site at `:917` discards the result of `convert_to_programmer`. With `resolve_chip()`, the site becomes:

```python
        elif args.dev_command == "consistency-check":
            try:
                eprom_data = resolve_chip(args.eprom, db=db_instance)
            except ChipNotFoundError:
                logger.error(f"EPROM '{args.eprom}' not found in database.")
                return 1
            return eprom_operator.consistency_check_eprom(
                args.eprom,
                eprom_data,  # NOTE: eprom_data IS used here (passed to consistency_check_eprom)
                ...
            )
```

The current code at `:917-919` actually does pass `eprom_data` to `consistency_check_eprom`. The CONTEXT.md note that "the result is discarded" refers to the fact that `convert_to_programmer` call result is only used for a presence-check — but `consistency_check_eprom` does receive the data. Using `resolve_chip()` is fully behavior-equivalent.

[VERIFIED: live codebase — `main.py:916-938` confirms `eprom_data` is passed to `consistency_check_eprom`]

### Pattern 4: Named Import Lists Per Module

The exact constants each module uses (verified by live code scan):

| Module | Constants to Import from `firestarter.constants` |
|--------|--------------------------------------------------|
| `main.py` | `FLAG_CHIP_ENABLE`, `FLAG_OUTPUT_ENABLE`, `CTRL_ADDRESS_LINE_16`, `CTRL_ADDRESS_LINE_17`, `CTRL_ADDRESS_LINE_18`, `CTRL_READ_WRITE`, `CTRL_VPE_ENABLE`, `CTRL_VPP_A9_ENABLE`, `CTRL_VPP_P1_ENABLE`, `CTRL_VPP_REGULATOR_ENABLE`, `CTRL_VPP_VPE_DROP_ENABLE` |
| `serial_comm.py` | `BAUD_RATE`, `COMMAND_FW_VERSION`, `FLAG_CAN_ERASE`, `FLAG_CHIP_ENABLE`, `FLAG_FORCE`, `FLAG_OUTPUT_ENABLE`, `FLAG_SKIP_BLANK_CHECK`, `FLAG_SKIP_ERASE`, `FLAG_VPE_AS_VPP` |
| `eprom_operations.py` | `BUFFER_SIZE`, `COMMAND_BLANK_CHECK`, `COMMAND_CHECK_CHIP_ID`, `COMMAND_DEV_ADDRESS`, `COMMAND_DEV_REGISTERS`, `COMMAND_ERASE`, `COMMAND_NAMES`, `COMMAND_READ`, `COMMAND_VERIFY`, `COMMAND_WRITE`, `FLAG_FORCE`, `FLAG_SKIP_BLANK_CHECK`, `FLAG_SKIP_ERASE`, `FLAG_VERBOSE`, `FLAG_VPE_AS_VPP` |
| `database.py` | `FLAG_CAN_ERASE` |
| `firmware.py` | `COMMAND_FW_VERSION`, `FIRESTARTER_RELEASE_BY_TAG_URL`, `FIRESTARTER_RELEASES_URL`, `FIRESTARTER_RELEASE_URL`, `FLAG_FORCE` |
| `hardware.py` | `COMMAND_CONFIG`, `COMMAND_HW_VERSION`, `COMMAND_READ`, `COMMAND_READ_VPE`, `COMMAND_READ_VPP` |

[VERIFIED: live codebase — scanned by AST-level name search across all 6 modules]

**Note on `firmware.py`:** The `FIRESTARTER_RELEASE*` URL constants live in `constants.py` (lines 8-15), not in a separate config. Named imports for `firmware.py` must include them.

### Pattern 5: constants.py Sync-Marker Pattern

The `CTRL_*` block already models the target pattern (lines 69-81):

```python
# RURP Control Register Bits — mirror of firestarter/include/rurp_pinout.h
# Documentary only — Python does not write the control register directly
```

DATA-04 adds the equivalent to `COMMAND_*` (lines 25-55) and `FLAG_*` (lines 57-67):

```python
# Wire-protocol command codes — Firmware sync: firestarter.h
COMMAND_READ = 1
...
```

[VERIFIED: live codebase — `constants.py` read in full; `CTRL_*` block at `:69-81` already has sync header; `COMMAND_*` at `:25-55` and `FLAG_*` at `:57-67` do not yet have it]

### Anti-Patterns to Avoid

- **Touching `info` site (line 622-627):** The `info` block uses `get_eprom` but NOT `convert_to_programmer` — it calls `get_eprom_config()` separately for `(config, manufacturer)`. Do not replace this with `resolve_chip()` (D-02).
- **Constructing a new `EpromDatabase()` inside `chip_resolver.py` with no injection seam:** Makes `test_chip_resolver.py` unable to use `skip_local_override=True`, coupling tests to `~/.firestarter/database.json`.
- **Leaving any F403/F405 noqa after the import is made explicit:** Once the import is named, the noqa is dead suppression and ruff will warn about it in Phase 42 sweep.
- **Raising the mypy error count above the watermark (44):** Adding named imports does not change mypy visibility (star-imports suppress name resolution; named imports make names explicit, which mypy already sees). Net impact: neutral or slight improvement.
- **Relocating `messages.py` into `constants.py`:** `messages.py` is codegenerated from `tools/catalog/messages.toml`; relocation breaks the CI codegen drift gate.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Chip DB lookup + conversion | Custom one-off per-command logic | `resolve_chip()` from `chip_resolver.py` | The whole point of DATA-01; 9 sites have already diverged subtly |
| Not-found error signaling | Ad-hoc string comparison | `ChipNotFoundError` from `exceptions.py:55` | Type-safe, already created in Phase 38 exactly for this use |
| Test DB isolation | Mocking the entire DB class | `EpromDatabase(skip_local_override=True)` | Already implemented in Phase 36/TEST-03; loads real `chip_database.json` without user overrides |

---

## Live Code Verification Findings

### DATA-01 — 9 Op Sites

**Confirmed:** The 9 copy-paste sites exist at these lines in `main.py` (live code, verified):

| Site | Op | `get_eprom` line | `convert_to_programmer` line | log+exit line |
|------|----|-----------------|------------------------------|---------------|
| `read` | `:660` | 660 | 663 | 665 |
| `write` | `:680` | 680 | 683 | 685 |
| `verify` | `:699` | 699 | 702 | 704 |
| `blank` | `:718` | 718 | 721 | 723 |
| `erase` | `:733` | 733 | 736 | 738 |
| `id` | `:751` | 751 | 754 | 756 |
| `dev read` | `:871` | 871 | 874 | 876 |
| `dev addr` | `:902` | 902 | 905 | 907 |
| `dev consistency-check` | `:917` | 917 | 918-920 | 924 |

**Confirmed:** NOT replaced — `info` at `:622-627` uses `get_eprom` but also calls `get_eprom_config()` separately; `list`/`search` use `get_eproms`/`search_eprom`.

**Confirmed:** The exact log string is `f"EPROM '{args.eprom}' not found in database."` (not `args.eprom` at the `info` site which uses `eprom_name`). The 9 op sites all use `args.eprom`.

**Confirmed:** `ChipNotFoundError` at `exceptions.py:55` is a bare `Exception` subclass with a docstring reading "Wired in Phase 39 (chip_resolver.py)."

**SC inaccuracy (D-11 note):** `tests/test_chip_resolver.py` does NOT exist yet. SC#1 says "from Phase 36 passes" — this is wrong. The file is created in Wave 1 of Phase 39.

**Confirmed:** The Phase 36 safety net has exactly ONE snapshot test for the bad-chip path: `test_error_info_bad_chip` (which tests the `info` command, NOT one of the 9 op sites). The 9 op sites are NOT individually snapshotted for the bad-chip case in the existing test suite. The GATE-1.8b constraint for the 9 sites is enforced by functional equivalence of `resolve_chip()` + `ChipNotFoundError` catch, not by existing snapshots. The planner should note this: `test_chip_resolver.py` will be the primary behavioral test for the new function.

### DATA-02 — Pin Mapping

**Confirmed:** `pin_conversions` dict is at `database.py:69`. The module-level docstring (`:1-25`) already contains this text: "pin_conversions: A hardcoded dictionary mapping standard EPROM pin numbers (for 24, 28, 32-pin DIP packages) to the RURP's internal address/control lines." — but this is the module docstring, not a docstring ON the `pin_conversions` dict itself.

**Confirmed:** `pinouts.json` is loaded into `self.pin_maps` at `database.py:191`. The composition occurs in `get_bus_config` (`:251-307`) which iterates `pin_map_data["address-bus-pins"]` (from `pinouts.json`) through `pin_conversions[pins]`.

**DATA-02 deliverable:** A docstring comment directly above or as a comment block on the `pin_conversions` variable itself (`:69`), not just in the module docstring. Something like:

```python
# pin_conversions: RURP board-wiring layer.
# Maps DIP socket pin number → RURP bus line number (hardware-specific).
# This is DISTINCT from pinouts.json (loaded as self.pin_maps), which maps
# chip pin function → DIP socket pin number (chip-specific).
# They COMPOSE in get_bus_config(): pinouts.json gives function→socket-pin,
# pin_conversions gives socket-pin→bus-line. There is ONE source of truth
# per layer, not duplication.
pin_conversions = {
```

### DATA-03 — noqa Marker Counts

**Confirmed (live code grep):**

| Module | F403/F405 noqa markers | Confirmed |
|--------|------------------------|-----------|
| `serial_comm.py` | 13 | YES (1 F403 + 12 F405) |
| `hardware.py` | 5 | YES (1 F403 + 4 F405) |
| `firmware.py` | 6 | YES (1 F403 + 5 F405) |
| `main.py` | 3 | YES (1 F403 + 2 F405) |
| `database.py` | 2 | YES (1 F403 + 1 F405) |
| `eprom_operations.py` | 26 | YES (1 F403 + 25 F405) |
| **Total** | **55** | Matches CONTEXT.md ~55 |

**Note:** Each `from firestarter.constants import *  # noqa: F403` line counts as the F403 marker. Individual usage lines carry `# noqa: F405`. All 55 should be removed after named imports land.

### DATA-04 — constants.py Block Ranges

**Confirmed (live code):**

| Block | Lines | Has sync marker? |
|-------|-------|-----------------|
| `COMMAND_*` | `:25-55` (incl. `COMMAND_NAMES` dict) | NO — DATA-04 adds it |
| `FLAG_*` | `:57-67` | NO — DATA-04 adds it |
| `CTRL_*` | `:69-81` | YES — "mirror of firestarter/include/rurp_pinout.h" |
| `REVISION_*` | `:83-96` | YES — "mirror of firestarter/include/rurp_shield.h" |

**Confirmed:** `COMMAND_FW_VERSION = 13` is at `constants.py:37`. (Note: `= 13` in decimal, `0x0D` hex.)

**Confirmed:** `test_revision_constants_parity.py:116` asserts `COMMAND_FW_VERSION == 0x0D`. Parity test runs with `pytest tests/test_revision_constants_parity.py` → 4 passed.

**Confirmed:** The parity test file is `tests/test_revision_constants_parity.py`. There is no file named `test_firmware_contract_parity.py` in the test suite.

---

## Common Pitfalls

### Pitfall 1: info site is NOT an op site
**What goes wrong:** Replacing the `info` block's `get_eprom` call at `:622` with `resolve_chip()` and breaking `info` behavior (it also calls `get_eprom_config()` for `(config, manufacturer)` which `resolve_chip()` does not return).
**Why it happens:** The `info` block looks similar to the 9 op sites but has different data needs.
**How to avoid:** The 9 sites confirmed by live grep; `info`/`list`/`search` are explicitly excluded per D-02.
**Warning signs:** If `test_info_*` snapshots fail after the DATA-01 change.

### Pitfall 2: test_chip_resolver.py missing skip_local_override
**What goes wrong:** Test constructs `EpromDatabase()` without `skip_local_override=True`, causing CI/bench divergence if operator has `~/.firestarter/database.json`.
**Why it happens:** Easy to forget the injection seam.
**How to avoid:** All tests that assert chip data must use `EpromDatabase(skip_local_override=True)`. See `test_eprom_database.py:36` as the model.
**Warning signs:** Tests pass locally but fail on a clean CI image.

### Pitfall 3: Leaving dead noqa after named import
**What goes wrong:** After converting `from firestarter.constants import *  # noqa: F403` to named imports, any `# noqa: F405` on usage lines become dead suppressions. Phase 42 ruff sweep (`B` rules) will flag these.
**Why it happens:** Easy to convert the import line but forget the usage-site noqas.
**How to avoid:** Strip all F403/F405 noqas in the same commit as the named-import conversion (D-08). Use `grep -n "noqa: F40" <file>` after conversion to confirm zero remain.
**Warning signs:** `ruff check` passes (dead noqas are not an error by default) but the count of noqas doesn't drop to zero per module.

### Pitfall 4: mypy watermark regression
**What goes wrong:** Adding named imports somehow raises the mypy error count above 44.
**Why it happens:** Named imports make previously-opaque star-import names explicit; mypy can now see them more clearly. However, since `disallow_untyped_defs = false` globally and the constants are simple int literals, the risk is low.
**How to avoid:** Run `python tools/check_mypy_watermark.py` after each wave. Current count is 41 (3 below watermark of 44) — there is headroom.
**Warning signs:** `check_mypy_watermark.py` exits non-zero.

### Pitfall 5: dev consistency-check result usage misunderstood
**What goes wrong:** Treating the `dev consistency-check` site as "discards result" and implementing `resolve_chip()` usage incorrectly (e.g., catching ChipNotFoundError but then not passing `eprom_data` to `consistency_check_eprom`).
**Why it happens:** CONTEXT.md D-04 says "discards the result" which refers to the presence-check-only nature — but `eprom_data` IS passed to `consistency_check_eprom` downstream.
**How to avoid:** See the live code at `main.py:916-938`. `eprom_data` is passed as second arg to `consistency_check_eprom`.
**Warning signs:** `test_consistency_check.py` failures after the DATA-01 wave.

---

## Code Examples

### EpromDatabase.get_eprom + convert_to_programmer pattern (source: `database.py`)

```python
# Source: firestarter_app/firestarter/database.py:490-559 (verified)
# get_eprom returns None if chip not found
def get_eprom(self, chip_name: str):
    config, manufacturer = self.get_eprom_config(chip_name)
    if config:
        return self._map_data(config, manufacturer)
    return None

# convert_to_programmer returns {} (falsy) for None/empty input
def convert_to_programmer(self, full_eprom_data: dict) -> dict:
    if not full_eprom_data:
        return {}
    # ... builds programmer config dict ...
    return programmer_data
```

The resolver must treat BOTH `get_eprom → None` AND `convert_to_programmer → {}` as the not-found condition (as the live code already does at each op site: `if not eprom_data: ...`).

### EpromDatabase(skip_local_override=True) for tests (source: `tests/test_eprom_database.py:36`)

```python
# Source: firestarter_app/tests/test_eprom_database.py:36 (verified)
db = EpromDatabase(skip_local_override=True)
eprom = db.get_eprom("W27C512")
assert eprom is not None
assert eprom["memory-size"] == 65536
```

### test_chip_resolver.py coverage shape (recommended, following Phase 36 pattern)

```python
# tests/test_chip_resolver.py — to be created in Wave 1
import pytest
from firestarter.chip_resolver import resolve_chip
from firestarter.database import EpromDatabase
from firestarter.exceptions import ChipNotFoundError


@pytest.fixture
def db():
    return EpromDatabase(skip_local_override=True)


def test_resolve_chip_hit_returns_dict(db):
    result = resolve_chip("W27C512", db=db)
    assert isinstance(result, dict)
    assert result["memory-size"] == 65536


def test_resolve_chip_hit_has_required_programmer_keys(db):
    result = resolve_chip("W27C512", db=db)
    for key in ("memory-size", "type", "algorithm", "pin-count", "vpp_mv", "flags"):
        assert key in result, f"Missing key: {key}"


def test_resolve_chip_miss_raises(db):
    with pytest.raises(ChipNotFoundError):
        resolve_chip("NOTACHIP_XYZ_DOESNOTEXIST", db=db)


def test_resolve_chip_conversion_correctness(db):
    # Verify round-trip: resolve_chip produces same result as manual get+convert
    result = resolve_chip("W27C512", db=db)
    full = db.get_eprom("W27C512")
    expected = db.convert_to_programmer(full)
    assert result == expected
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `from firestarter.constants import *` (star-import everywhere) | Explicit named imports per module | Phase 39 (DATA-03) | mypy can trace constant types; ruff F403/F405 noqas removed |
| 9× copy-paste chip-lookup block | Single `resolve_chip()` call | Phase 39 (DATA-01) | Single chokepoint for Phase 41 Click handlers to call |
| No clear "two layers" documentation on `pin_conversions` | Docstring explains board-wiring vs chip-pinout distinction | Phase 39 (DATA-02) | Eliminates apparent "two sources of truth" confusion |
| `COMMAND_*`/`FLAG_*` blocks without firmware-sync markers | Blocks carry `# Firmware sync: firestarter.h` annotation | Phase 39 (DATA-04) | Consistent with `CTRL_*`/`REVISION_*` blocks added in v1.7 |

---

## Assumptions Log

> All claims in this research were verified against the live codebase or cited from authoritative
> project artifacts (CONTEXT.md backed by DISCUSSION-LOG.md). No assumed claims.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| (none) | — | — | — |

**All claims in this research were verified or cited — no user confirmation needed.**

---

## Open Questions

1. **Per-site `try/except` vs shared helper for ChipNotFoundError catch**
   - What we know: Both approaches are behavior-equivalent for GATE-1.8b. CONTEXT.md leaves this to Claude's Discretion.
   - What's unclear: Which produces a cleaner diff for Phase 41 (Click migration that adds centralized error mapping).
   - Recommendation: Shared helper (`_resolve_or_exit`) is preferable — it is a single point the Phase 41 planner removes and replaces with Click error mapping, minimizing churn.

2. **Whether to add `chip_resolver` to the mypy strict-island overrides in `pyproject.toml`**
   - What we know: Phase 42 (ERR-02) is the mypy-strict phase. Phase 39 only must not raise the watermark.
   - What's unclear: Whether the planner wants to proactively annotate `chip_resolver.py` to strict and add it to `[[tool.mypy.overrides]]` now.
   - Recommendation: Add `return type: dict` annotation to `resolve_chip` (minimal, correct) but defer adding `chip_resolver` to the strict overrides list to Phase 42 (keeps the Phase 39 diff minimal).

---

## Environment Availability

This phase is purely host-code changes with no external services or CLI tools beyond the development stack already confirmed working.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | Executing tests | YES | 3.12.13 | — |
| pytest + syrupy | Test suite | YES | pytest 9.0.3, syrupy 5.2.0 | — |
| ruff | Lint/format gate | YES | (confirmed: `ruff check` exits 0) | — |
| mypy | Type-check gate | YES | watermark 44, current count 41 | — |
| `firestarter_app` on `v1.8-app-cleanup` branch | Phase target | YES | confirmed | — |

---

## Validation Architecture

> Nyquist validation enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 + syrupy 5.2.0 (snapshot) |
| Config file | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `cd firestarter_app && python -m pytest tests/test_chip_resolver.py tests/test_revision_constants_parity.py -q` |
| Full suite command | `cd firestarter_app && python -m pytest -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DATA-01 | `resolve_chip("W27C512")` returns programmer config dict | unit | `pytest tests/test_chip_resolver.py::test_resolve_chip_hit_returns_dict -x` | NO — Wave 1 creates it |
| DATA-01 | `resolve_chip("NOTACHIP")` raises `ChipNotFoundError` | unit | `pytest tests/test_chip_resolver.py::test_resolve_chip_miss_raises -x` | NO — Wave 1 creates it |
| DATA-01 | 9 op sites no longer contain `get_eprom`/`convert_to_programmer` calls | structural (grep) | `grep -n "db_instance.get_eprom\|convert_to_programmer" firestarter_app/firestarter/main.py` → 0 op-site results | N/A — grep check |
| DATA-01 | Phase 36 characterization snapshots still pass (bad-chip path preserved) | snapshot | `pytest tests/test_characterization.py::test_error_info_bad_chip -x` | YES |
| DATA-01 | `consistency_check` still passes (ring-fenced read-path) | integration | `pytest tests/test_consistency_check.py -x` | YES |
| DATA-02 | `pin_conversions` docstring present in database.py | structural | manual review / `grep "board-wiring" firestarter_app/firestarter/database.py` | N/A |
| DATA-03 | No star-imports remain | structural (grep) | `grep -r "from firestarter.constants import \*" firestarter_app/firestarter/` → empty | N/A — grep check |
| DATA-03 | ruff exits 0 (no F403/F405) | lint | `cd firestarter_app && python -m ruff check firestarter/` | N/A |
| DATA-03 | mypy watermark not exceeded | type-check | `cd firestarter_app && python tools/check_mypy_watermark.py` exits 0 | YES |
| DATA-04 | `COMMAND_FW_VERSION == 0x0D` parity assertion passes | unit | `pytest tests/test_revision_constants_parity.py -x` | YES |
| DATA-04 | Full parity suite green | unit | `pytest tests/test_revision_constants_parity.py -v` (4 tests) | YES |

### Sampling Rate

- **Per wave commit:** `cd firestarter_app && python -m pytest -q` (full suite, 182+N tests; ~12s; fast enough for every commit)
- **Per wave merge:** Same + `python -m ruff check firestarter/` + `python tools/check_mypy_watermark.py`
- **Phase gate:** All three green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `firestarter_app/tests/test_chip_resolver.py` — covers DATA-01 (hit, miss, conversion correctness); created in Wave 1

*(All other required test infrastructure exists; `conftest.py`, syrupy, pytest all confirmed present.)*

---

## Security Domain

> GATE-1.8 scope: host-only pure refactor. No new network calls, no new auth paths,
> no new user-facing input surfaces.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | — |
| V3 Session Management | No | — |
| V4 Access Control | No | — |
| V5 Input Validation | Minimal | `chip_name: str` input to `resolve_chip` — passes through to `get_eprom` which uses `.lower()` string comparison; no injection risk (DB is local JSON) |
| V6 Cryptography | No | — |

No new threat patterns introduced.

---

## Project Constraints (from CLAUDE.md)

Extracted from `/workspaces/CLAUDE.md` and `firestarter_app/CLAUDE.md`:

1. **Firmware sub-repo is NOT modified** — Phase 39 is host-only. `firestarter/` firmware unchanged.
2. **`constants.py` must stay in sync with `firestarter/include/firestarter.h`** — DATA-04 adds markers; values are NOT changed. GATE-1.8c preserved.
3. **`CTRL_*` names + hex values must stay in sync with `firestarter/include/rurp_pinout.h`** — not modified in Phase 39.
4. **`REVISION_*` names + byte values must stay in sync with `firestarter/include/rurp_shield.h`** — not modified in Phase 39.
5. **Flat layout** — `chip_resolver.py` is a flat sibling under `firestarter/`, no subpackage.
6. **`chip_database.json` is generated, do NOT edit by hand** — `test_chip_resolver.py` reads it via `EpromDatabase(skip_local_override=True)`.
7. **Wire protocol byte-identical** (GATE-1.8a) — Phase 39 does not touch serial layer.
8. **Read path ring-fenced** (GATE-1.8d) — `read_eprom()` / `read_data_block()` not touched. `dev consistency-check` uses `resolve_chip()` in an equivalent way.

---

## Sources

### Primary (HIGH confidence)

- Live codebase: `firestarter_app/firestarter/main.py` — verified all 9 op site line numbers, exact log string, `info` exclusion
- Live codebase: `firestarter_app/firestarter/constants.py` — verified block ranges (`:25-55`, `:57-67`, `:69-81`, `:83-96`), `COMMAND_FW_VERSION = 13` at `:37`
- Live codebase: `firestarter_app/firestarter/database.py` — verified `pin_conversions` at `:69`, `EpromDatabase.skip_local_override` at `:167`, `convert_to_programmer` at `:519`
- Live codebase: `firestarter_app/firestarter/exceptions.py` — verified `ChipNotFoundError` at `:55`
- Live codebase: `firestarter_app/tests/test_revision_constants_parity.py` — verified `COMMAND_FW_VERSION == 0x0D` assertion at `:116`, 4 tests all pass
- Live test run: `pytest -q` → 182 passed, 2 xfailed, 29 snapshots passed (confirmed baseline)
- Live grep: all 6 star-importing modules confirmed; 55 noqa markers confirmed
- Live mypy run: 41 errors current, watermark 44 (3 below)
- `.planning/phases/39-database-cleanup-chip-resolver/39-CONTEXT.md` — decisions D-01..D-11

### Secondary (MEDIUM confidence)

- `.planning/REQUIREMENTS.md` — DATA-01..DATA-04 requirement text, GATE-1.8 standing gate
- `.planning/ROADMAP.md` — Phase 39 goal + SC#1-SC#4 (with documented SC inaccuracies noted in D-11, D-06)
- `firestarter_app/CLAUDE.md` — constants sync contract, data flow architecture

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new packages; existing tools confirmed working
- 9 op site locations: HIGH — verified by live code read and grep
- Named import lists: HIGH — verified by live AST-level name scan
- noqa marker counts: HIGH — verified by live grep with count
- Architecture: HIGH — live code read of all affected modules
- Pitfalls: HIGH — derived from live code surprises (info site subtlety, consistency-check result usage)

**Research date:** 2026-05-27
**Valid until:** Stable — this is live-code verified against a specific branch tip. Revalidate if any other phase touches `main.py`, `database.py`, or `constants.py` before Phase 39 executes.

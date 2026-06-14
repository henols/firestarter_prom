# Phase 69: CLI Command-Surface Robustness Audit - Research

**Researched:** 2026-06-14
**Domain:** Python host CLI display path — `ic_layout.py` pin-field contract + full Click command surface smoke audit
**Confidence:** HIGH

---

## Summary

The `firestarter info <chip>` command crashes for **every chip in the database** with a
`TypeError: '<=' not supported between instances of 'list' and 'int'`.  The crash is in
`ic_layout._generate_pin_names_for_display` (lines 394, 396, 402 in the current codebase),
which compares `pin_map_details["vpp-pin"]`, `rw-pin`, and `oe-pin` directly against
`pin_count` using `<=`.  Every entry in `pinouts.json` stores those fields as a
**single-element list** (e.g. `"vpp-pin": [22]`), not a bare int.

The fix is a three-line scalar-extraction change in `ic_layout.py`; `pinouts.json` is
already correct and must not change.  The existing sister function `get_bus_config` in
`database.py` already handles this correctly with the pattern
`pin_to_check = val[0] if isinstance(val, list) else val` — the same pattern must be
applied in `_generate_pin_names_for_display`.

After fixing the crash the phase requires: a smoke audit of all CLI command surfaces using
CliRunner + mock managers, regression tests that pin the fixed behaviour and each Phase 66
non-supported chip class, and a raised mypy watermark to account for the `ic_layout.py`
type errors that the fix will also resolve.

The crash is pinned as the GATE-1.8b "known-broken" snapshot in
`tests/__snapshots__/test_characterization.ambr` (`test_info_known_chip_stderr`).  Once
the fix lands, that snapshot MUST be updated to the new passing shape.

**Primary recommendation:** Fix `_generate_pin_names_for_display` in `ic_layout.py` by
extracting the first list element before every scalar comparison (three sites); update the
`test_info_known_chip` snapshot to exit 0; add dedicated regression tests and smoke tests
in `tests/test_cli_handlers.py` or a new `tests/test_ic_layout.py`.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| Pin-field display logic | Host CLI (`ic_layout.py`) | — | Pure display layer; no firmware involvement |
| Chip DB lookup | Host service (`database.py`) | — | `EpromDatabase.get_pin_map` owns the data layer |
| CLI command dispatch | Host CLI (`cli_handlers.py`) | — | Click group + command definitions |
| support_status refusal guard | Host service (`chip_resolver.py`) | — | `resolve_chip` already guards write/read/erase; info bypasses it (correct — info is read-only display) |
| Error-to-exit mapping | Host CLI (`map_typed_errors` decorator) | — | Centralized in `cli_handlers.py` |

---

## Pin-Field Contract Analysis (Research Question 1)

### Contract: list-valued in pinouts.json, scalar needed for display comparisons

Every single-pin field in `pinouts.json` (`vpp-pin`, `oe-pin`, `rw-pin`, `ce-pin`,
`vcc-pin`, `gnd-pin`) is stored as a **single-element list**.  This was confirmed by
enumerating all entries — no scalar values exist for these fields. [VERIFIED: direct
inspection of `/workspaces/firestarter_app/firestarter/data/pinouts.json`]

The list-valued contract exists because several chips share a pin between two functions
(e.g. `DIP24_2732` has `"vpp-pin": [20], "oe-pin": [20]` — OE/VPP is the same physical
pin) and the `get_adapter_table` function in `database.py` already treats all these fields
as iterables using a local `_assign` helper.  The list is the correct storage format.

`get_bus_config` in `database.py` (lines 284-295) already extracts the scalar correctly:
```python
pin_val = pin_map_data[pin_func]
pin_to_check = pin_val[0] if isinstance(pin_val, list) else pin_val
```
[VERIFIED: direct inspection of `/workspaces/firestarter_app/firestarter/database.py`]

### Crash sites in _generate_pin_names_for_display

Three comparison sites crash identically with `TypeError`:

| Line | Expression | Fix |
|------|-----------|-----|
| 394 | `pin_map_details["rw-pin"] <= pin_count` | extract `rw_pin = _scalar(pin_map_details["rw-pin"])` then compare |
| 396 | `pin_map_details["vpp-pin"] <= pin_count` | same |
| 401 | `pin_map_details["oe-pin"] != pin_map_details["vpp-pin"]` | both need scalar; list != list would not crash but semantically wrong |
| 402 | `pin_map_details["oe-pin"] <= pin_count` | same |
| 406 | `pin_map_details["oe-pin"] <= pin_count` (elif branch) | same |

Additionally, index access `pin_map_details["vpp-pin"] - 1` (line 397),
`pin_map_details["oe-pin"] - 1` (lines 404, 408), and
`pin_map_details["rw-pin"] - 1` (line 395) would crash with `TypeError` immediately
after the `<=` guard if it were not already failing. [VERIFIED: source inspection of
`/workspaces/firestarter_app/firestarter/ic_layout.py`]

### Recommended fix (minimal root fix)

Add a one-line helper at the top of `_generate_pin_names_for_display` (or as a private
static) that extracts a scalar from a possibly-list-valued pin field:

```python
def _pin_scalar(val):
    return val[0] if isinstance(val, list) else val
```

Replace every `pin_map_details["X-pin"]` used in a scalar context with
`_pin_scalar(pin_map_details["X-pin"])`.  This mirrors the existing `get_bus_config`
pattern exactly.

### Other consumers of pin-map fields

| Consumer | Field usage | List-safe? |
|---|---|---|
| `database.get_bus_config` | `rw-pin`, `vpp-pin` | YES — already does `val[0] if isinstance(val, list)` |
| `database.get_adapter_table` | all single-pin fields | YES — iterates via `_assign(pins_val, signal)` which handles both list and scalar |
| `ic_layout._generate_pin_names_for_display` | `rw-pin`, `vpp-pin`, `oe-pin` | NO — BROKEN |
| `eprom_info.EpromConsolePresenter` | indirect via `spec_builder` | N/A — fix in ic_layout fixes this |

No write-path or firmware consumers read pin-map fields directly. [VERIFIED: grep of
consumers in `/workspaces/firestarter_app/firestarter/`] [ASSUMED: no hidden consumers in
`~/.firestarter/` user extension code — no user code exists in the devcontainer]

---

## CLI Command Surface Inventory (Research Question 2)

### Full command surface

Sourced from `cli_handlers.py` + the CLAUDE.md command table:
[VERIFIED: direct inspection of `/workspaces/firestarter_app/firestarter/cli_handlers.py`]

| Command | Group | Calls resolve_chip? | Hardware required? | Display path crashes? |
|---------|-------|---------------------|--------------------|-----------------------|
| `list` | top | No | No | No (does not call `build_specifications`) |
| `info` | top | No (uses `get_eprom`) | No | YES (calls `build_specifications` → `_generate_pin_names_for_display`) |
| `search` | top | No | No | No (same table as `list`) |
| `read` | top | Yes | Yes (mockable) | No (crashes at resolve if non-supported) |
| `write` | top | Yes | Yes (mockable) | No |
| `verify` | top | Yes | Yes (mockable) | No |
| `blank` | top | Yes | Yes (mockable) | No |
| `erase` | top | Yes | Yes (mockable) | No |
| `id` | top | Yes | Yes (mockable) | No |
| `vpp` | top | No | Yes (mockable) | No |
| `vpe` | top | No | Yes (mockable) | No |
| `hw` | top | No | Yes (mockable) | No |
| `config` | top | No | Yes (mockable) | No |
| `fw` | top | No | Yes (mockable) | No |
| `dev read` | dev | Yes | Yes (mockable) | No |
| `dev reg` | dev | No | Yes (mockable) | No |
| `dev addr` | dev | Yes | Yes (mockable) | No |
| `dev consistency-check` | dev | Yes | Yes (mockable) | No |
| `dev write-cycle` | dev | Yes | Yes (mockable) | No |
| `dev fault-inject` | dev | Yes | Yes (mockable) | No |

**Observation:** Only `info` crashes today. `list` and `search` call `print_eprom_list_table`
which uses `spec_builder.get_chip_type_string` but NOT `_generate_pin_names_for_display`,
so they are safe. All hardware-requiring commands are already tested via mock `AppContext`
in `test_cli_handlers.py`.

**info command detail:**
- Does NOT go through `resolve_chip` (correct — info is display-only)
- Calls `app.db.get_eprom(eprom)` → `app.eprom_presenter.prepare_detailed_eprom_data(...)` →
  `spec_builder.build_specifications(eprom_details)` → `_generate_pin_names_for_display`
- The crash happens unconditionally for any chip that has a pin-map with `vpp-pin`, `oe-pin`, or `rw-pin`

**info command with non-supported chips:**
The `info` command deliberately bypasses `resolve_chip`, so it displays info for
`vpp-exceeds-max` and `adapter-required` chips without raising `ChipNotImplementedError`.
This is correct per Phase 68 spec: `firestarter info M2716` should show the chip record
with capability status, not refuse.  After the fix, info must show those chips without
crashing. Phase 68 will later add a `support_status` display line to the output — the
fix here must not prevent that.

### Commands that go through resolve_chip (hardware ops)

All chip-op commands (`read`, `write`, `verify`, `blank`, `erase`, `id`) and `dev`
sub-commands that take `eprom` call `resolve_chip`, which raises `ChipNotImplementedError`
for non-supported chips.  These are already covered by the Phase 66 guard.  The smoke
audit just needs to verify they exit 1 with a typed error message (not a traceback) for
non-supported chips — which they already do via `map_typed_errors`.

---

## Representative Chip Selection (Research Question 3)

All from the packaged `chip_database.json` (no local override):
[VERIFIED: confirmed via `EpromDatabase(skip_local_override=True)` query]

| Chip | Pinout key | Status | Pin fields that triggered crash |
|------|-----------|--------|--------------------------------|
| `W27C512` | `DIP28_27512` | supported | `vpp-pin: [22]`, `oe-pin: [22]` |
| `2732` | `DIP24_2732` | vpp-exceeds-max | `vpp-pin: [20]`, `oe-pin: [20]` |
| `M2716` | `DIP24_2716` | vpp-exceeds-max | `vpp-pin: [21]`, `oe-pin: [20]` |
| `AT28C04` | `DIP24_?` | adapter-required | (24-pin EEPROM) |
| `AT28C256` | `DIP28_28C256` | supported | `rw-pin: [27]`, `oe-pin: [22]` |
| `AT28C64` (or `AM28C64A`) | `DIP28_28C64` | supported | `rw-pin: [27]`, `oe-pin: [22]` |
| `SST39SF040` (or equivalent) | `DIP32_SST39SF040` | supported | `rw-pin: [31]`, `oe-pin: [24]` |

**One representative per support_status:**
- Supported 28-pin with VPP: `W27C512`
- Supported 28-pin with RW (EEPROM): `AT28C256`
- Supported 32-pin: `AT28C010` (verify in DB) or any `DIP32_STD` chip
- `vpp-exceeds-max`: `2732` (or `M2716`)
- `adapter-required`: `AT28C04` or `AT28C16`
- `protocol-not-implemented`: `X88C64P` or `X88C64S` (protocol 0x34, 24-pin)

**Note on 2732 entry:** The chip named `2732` in the DB has `part_number: "2732,2732A,M2732,M2732A"` — it matches via alias lookup. The `M2716` entry has its own record.

---

## Regression Test Patterns (Research Question 4)

### Existing test infrastructure [VERIFIED: inspected test suite]

**`tests/test_cli_handlers.py`** — CliRunner-based in-process tests using `make_app_context()`:
- Constructs `AppContext` with `EpromDatabase(skip_local_override=True)` + `Mock(spec=...)` managers
- Already covers all chip-op commands (read/write/verify/blank/erase/id/dev sub-commands)
- The `info` happy path is explicitly broken: `test_info_chip_resolution_happy_path` asserts `exit_code == 1` because of the known crash
- The `eprom_presenter` field is `Mock(spec=EpromConsolePresenter)` in existing chip-op tests — but for the `info` command test, the real presenter is needed to exercise the crash

**`tests/test_characterization.py`** — subprocess-based golden snapshots:
- `test_info_known_chip` pins the crash via `syrupy` snapshot (`test_info_known_chip_stderr` contains the `TypeError` traceback)
- After fix: this snapshot must be updated to show exit 0 and correct output

**`tests/test_eprom_info.py`** — unit tests for `EpromConsolePresenter`:
- Comment explicitly notes the happy path was not tested because it triggers the ic_layout bug
- After fix: `prepare_detailed_eprom_data` happy path can be tested

**`tests/test_chip_resolver.py`** — covers resolve_chip + Phase 66 support_status guard

### Where new regression tests belong

**Option A (recommended): Extend `tests/test_cli_handlers.py`**
- Add `test_info_happy_path` using `make_app_context()` with a REAL `EpromConsolePresenter`
  (not mocked) — invoke `firestarter info W27C512`, assert `exit_code == 0`
- Add `test_info_2732_no_crash` — `firestarter info 2732`, assert exit 0 (list-valued-pin regression)
- Add `test_info_vpp_exceeds_max_no_crash` — `firestarter info M2716`, assert exit 0
- Add `test_info_adapter_required_no_crash` — `firestarter info AT28C04`, assert exit 0

**Option B: Add `tests/test_ic_layout.py`** (unit-level)
- Test `_generate_pin_names_for_display` directly with each pinout key
- Test `build_specifications` returns non-None for each representative chip
- No CliRunner needed; faster to run

Both options are complementary. The planner should include both levels.

### CliRunner pattern for real presenter

The existing `make_app_context()` factory mocks `eprom_presenter`. For `info` tests, the
real presenter is needed. Pattern:

```python
def make_app_context_with_real_presenter(**overrides) -> AppContext:
    db = EpromDatabase(skip_local_override=True)
    return AppContext(
        db=db,
        config_manager=ConfigManager(),
        eprom_operator=Mock(spec=EpromOperator),
        hardware_manager=Mock(spec=HardwareManager),
        firmware_manager=Mock(spec=FirmwareManager),
        eprom_presenter=EpromConsolePresenter(db),  # REAL, not mocked
    )
```

### Snapshot update requirement

`tests/__snapshots__/test_characterization.ambr` contains two snapshots that pin the
current broken behavior:
- `test_info_known_chip` (stdout of `firestarter info W27C512`) — exits 1, empty stdout
- `test_info_known_chip[test_info_known_chip_stderr]` — the `TypeError` traceback

After fixing the crash, run `pytest --snapshot-update tests/test_characterization.py::test_info_known_chip`
to regenerate these snapshots with the new passing output.

---

## CI Gate Specifics (Research Question 5) [VERIFIED: inspected `.github/workflows/ci.yml` and `pyproject.toml`]

### Gate commands (exact, from CI workflow)

```bash
# From .github/workflows/ci.yml:
ruff check firestarter/ tests/
ruff format --check firestarter/ tests/
python tools/check_mypy_watermark.py
pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70
```

### Current state

| Gate | Status | Notes |
|------|--------|-------|
| `ruff check` | 2 pre-existing I001 errors in `tests/test_address_parser.py` and `tests/test_codec.py` | Pre-existing; do NOT fix in Phase 69 (not in scope; touching those files risks ruff-I001 propagation) |
| `ruff format --check` | Clean on `firestarter/` and `tests/` | Tools dir has unformatted files but CI only checks `firestarter/ tests/` |
| `mypy watermark` | FAILING: 29 errors vs watermark 26 | `ic_layout.py` contributes 2 errors: `Sequence[str].append` and `get_pin_map` type mismatch. After fix, these may resolve, reducing error count. |
| `pytest --cov-fail-under=70` | PASSING: 71.93% coverage, 499 tests | `ic_layout.py` is at 30% coverage — new tests will raise it |

### mypy details

The mypy watermark gate (`tools/check_mypy_watermark.py`) currently fails at 29 errors
vs watermark 26.  Two of those errors are in `ic_layout.py`:
- Line 437: `"Sequence[str]" has no attribute "append"` — the `pin_names` variable is typed
  as `list(...)` return which mypy sees as `Sequence`; the fix should also correct this type
- Line 521: argument type mismatch with `get_pin_map`

After the fix, the watermark value in `check_mypy_watermark.py` must be updated to the
new error count (likely 27 or fewer). The mypy overrides in `pyproject.toml` do NOT include
`ic_layout.py` in the strict island — it remains in the lenient global config.

### Coverage floor

Current: 71.93% (`ic_layout.py` at 30%, `eprom_info.py` at 30%).  New tests in
`tests/test_ic_layout.py` and expanded `tests/test_cli_handlers.py` + `tests/test_eprom_info.py`
will raise both modules.  No risk of dropping below 70%.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Scalar extraction from list-or-int | Custom type coercion | `val[0] if isinstance(val, list) else val` pattern (already in `database.get_bus_config`) | The codebase already has this pattern; copy it |
| CliRunner test infrastructure | New harness | `click.testing.CliRunner` + `make_app_context()` in `tests/test_cli_handlers.py` | Already established pattern |
| Snapshot management | Manual string comparison | `syrupy` via `pytest --snapshot-update` | Already in the test suite |
| Coverage measurement | Manual tracking | `pytest --cov=firestarter --cov-report=term-missing --cov-fail-under=70` | Existing CI command |

---

## Common Pitfalls

### Pitfall 1: Mocking the presenter in info tests

**What goes wrong:** The existing `make_app_context()` uses `Mock(spec=EpromConsolePresenter)`
for `eprom_presenter`. If an `info` test also uses a mocked presenter, the mock will return
`None` from `prepare_detailed_eprom_data` and the test will exit 1 silently — masking the
actual crash fix.

**How to avoid:** For `info` command tests that exercise the display path, inject a
**real** `EpromConsolePresenter(db)` instance.

### Pitfall 2: Forgetting to update the syrupy snapshot

**What goes wrong:** After fixing the crash, `test_info_known_chip` in
`test_characterization.py` will FAIL because the snapshot contains the old `TypeError`
traceback on stderr. The test is marked to pin current broken behavior.

**How to avoid:** Run `pytest --snapshot-update tests/test_characterization.py::test_info_known_chip`
after the fix to regenerate the snapshots. The new snapshot should show exit 0 and the
formatted chip info output.

### Pitfall 3: Forgetting address-bus-pins path

**What goes wrong:** The `address-bus-pins` field is also in pin_map_details and is
accessed at line 411 as `for i, pin_num in enumerate(pin_map_details["address-bus-pins"]):`
with `if pin_num <= pin_count`. This path is fine — `address-bus-pins` is a list but it
is ITERATED (each `pin_num` is already a scalar int). The comparison `int <= int` works.

**How to avoid:** Do not apply the `_pin_scalar` fix to `address-bus-pins` iteration.
Only `rw-pin`, `vpp-pin`, and `oe-pin` need the extraction.

### Pitfall 4: mypy watermark update

**What goes wrong:** After fixing the `ic_layout.py` crash, the mypy error count in that
file may drop from 2 to 0, changing the total error count from 29 to 27. The watermark
in `tools/check_mypy_watermark.py` must be updated from 26 to the new floor (could be 27,
meaning the watermark may need to go UP not down — counterintuitive).

**How to avoid:** Run `python tools/check_mypy_watermark.py` after all changes and update
the watermark line to the new error count if errors decreased.

### Pitfall 5: Phase 68 forward-compatibility

**What goes wrong:** Phase 68 will add `support_status` display to the `info` output.
If Phase 69 hard-codes the `info` output in syrupy snapshots that include every displayed
field, Phase 68 will have to update those snapshots.

**How to avoid:** Syrupy snapshots pin the full output — this is intentional and
acceptable. Phase 68 will naturally update them. No special action needed in Phase 69.

### Pitfall 6: rw-pin off-by-one equivalence check

**What goes wrong:** Line 401 compares `pin_map_details["oe-pin"] != pin_map_details["vpp-pin"]`
as a "different pin?" guard. After extraction to scalars, this becomes `int != int` which
is correct.  But if left as list comparison (`[20] != [20]`), Python list equality returns
`False` for equal lists — coincidentally correct! However this is fragile and confusing.

**How to avoid:** Extract both to scalars before the inequality check — makes the intent
clear and prevents future breakage if pin fields ever hold multiple pins.

---

## Code Examples

### Pattern to apply in _generate_pin_names_for_display

```python
# Source: existing database.get_bus_config pattern (lines 289-290)
# This is the correct way to handle possibly-list-valued pin fields

def _pin_scalar(pin_val):
    """Extract a scalar pin number from a possibly-list-valued pin field."""
    return pin_val[0] if isinstance(pin_val, list) else pin_val

# Example application (replaces lines 394-408):
if pin_map_details:
    if "rw-pin" in pin_map_details:
        rw = _pin_scalar(pin_map_details["rw-pin"])
        if rw <= pin_count:
            pin_names[rw - 1] = "R/W(WE)"
    if "vpp-pin" in pin_map_details:
        vpp = _pin_scalar(pin_map_details["vpp-pin"])
        if vpp <= pin_count:
            pin_names[vpp - 1] = "VPP"
            if "oe-pin" in pin_map_details:
                oe = _pin_scalar(pin_map_details["oe-pin"])
                if oe != vpp and oe <= pin_count:
                    pin_names[oe - 1] = "OE"
    elif "oe-pin" in pin_map_details:
        oe = _pin_scalar(pin_map_details["oe-pin"])
        if oe <= pin_count:
            pin_names[oe - 1] = "OE"
    if "address-bus-pins" in pin_map_details:
        for i, pin_num in enumerate(pin_map_details["address-bus-pins"]):
            if pin_num <= pin_count:
                pin_names[pin_num - 1] = f"A{i}"
```

[ASSUMED: this fixes the crash; must verify by running test suite after implementation]

### CliRunner test pattern for info happy path

```python
# Source: existing test_cli_handlers.py make_app_context pattern + this phase's extension
def test_info_happy_path_no_crash(runner: CliRunner) -> None:
    """firestarter info W27C512 exits 0 after list-vs-int fix (SC-1)."""
    db = EpromDatabase(skip_local_override=True)
    app = AppContext(
        db=db,
        config_manager=ConfigManager(),
        eprom_operator=Mock(spec=EpromOperator),
        hardware_manager=Mock(spec=HardwareManager),
        firmware_manager=Mock(spec=FirmwareManager),
        eprom_presenter=EpromConsolePresenter(db),  # real, not mocked
    )
    result = runner.invoke(cli, ["info", "W27C512"], obj=app)
    assert result.exit_code == 0
    assert "W27C512" in result.output

def test_info_2732_list_valued_pin_no_crash(runner: CliRunner) -> None:
    """firestarter info 2732 exits 0 — pins list-vs-int regression fix (SC-1)."""
    db = EpromDatabase(skip_local_override=True)
    app = AppContext(
        db=db,
        config_manager=ConfigManager(),
        eprom_operator=Mock(spec=EpromOperator),
        hardware_manager=Mock(spec=HardwareManager),
        firmware_manager=Mock(spec=FirmwareManager),
        eprom_presenter=EpromConsolePresenter(db),
    )
    result = runner.invoke(cli, ["info", "2732"], obj=app)
    # 2732 is vpp-exceeds-max; info must display it without crashing
    assert result.exit_code == 0
    assert "2732" in result.output
```

---

## Standard Stack

No new packages required. This phase uses only:

| Library | Purpose | Source |
|---------|---------|--------|
| `pytest` | Test runner | Already in `.[test]` extras |
| `click.testing.CliRunner` | In-process CLI invocation | Already used in `test_cli_handlers.py` |
| `unittest.mock.Mock` | Manager mocking | Already used throughout test suite |
| `syrupy` | Snapshot testing | Already in test suite |

**No new package installations required.** [VERIFIED: existing `pyproject.toml` `[test]` extras]

## Package Legitimacy Audit

> No new packages are installed in this phase. Section is N/A.

---

## Architecture Patterns

### Recommended Project Structure (no new files required)

```
firestarter/
└── ic_layout.py         # patch _generate_pin_names_for_display (3-line fix)

tests/
├── test_ic_layout.py    # NEW: unit tests for EpromSpecBuilder._generate_pin_names_for_display
│                        # and build_specifications for each representative chip
├── test_cli_handlers.py # EXTEND: add info happy-path + non-supported chip tests
├── test_eprom_info.py   # EXTEND: add prepare_detailed_eprom_data happy-path test
└── __snapshots__/
    └── test_characterization.ambr  # UPDATE: regenerate test_info_known_chip snapshots
```

### Pattern: Scalar extraction before list-valued pin comparison

See "Code Examples" section above. Apply consistently to all 5 sites in
`_generate_pin_names_for_display`.

### Anti-Patterns to Avoid

- **Changing pinouts.json to scalar values:** The list-valued format is intentional and
  supports multiple consumers correctly. Do NOT change the JSON — only change ic_layout.py.
- **Mocking EpromConsolePresenter in info tests:** Tests that verify the crash is fixed
  must use the real presenter. Mocking hides the bug.
- **Patching the crash at one call site:** The ROADMAP specifies "fixed at its root (pin-field
  contract aligned across ic_layout.py and pinouts.json)." The scalar-extraction helper must
  be applied at all 5 comparison/indexing sites, not just the first-crashing one.

---

## Runtime State Inventory

> Omitted — greenfield fix phase, no rename/refactor.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | Test runtime | ✓ | 3.12.13 | — |
| pytest | Test suite | ✓ | 9.0.3 | — |
| syrupy | Snapshot tests | ✓ | 5.3.2 | — |
| ruff | Lint/format gate | ✓ | (installed) | — |
| mypy | Type check | ✓ | (installed) | — |
| firestarter (editable install) | CLI tests | ✓ | installed | `pip install -e '.[test]'` |

All dependencies confirmed present. [VERIFIED: `pip install -e '.[test]'` state confirmed by test suite running]

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| Quick run command | `pytest tests/test_ic_layout.py tests/test_cli_handlers.py -x -q` |
| Full suite command | `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` |

### Phase Requirements → Test Map

| SC# | Behavior | Test Type | Automated Command | File |
|-----|----------|-----------|-------------------|------|
| SC-1 | `info W27C512` exits 0 (not TypeError) | unit + CLI | `pytest tests/test_ic_layout.py tests/test_cli_handlers.py::test_info_happy_path_no_crash` | ❌ Wave 0 |
| SC-1 | `info 2732` exits 0 (list-valued-pin regression) | CLI | `pytest tests/test_cli_handlers.py::test_info_2732_list_valued_pin_no_crash` | ❌ Wave 0 |
| SC-1 | `info` on all 11 pinout keys completes | unit | `pytest tests/test_ic_layout.py::test_generate_pin_names_all_pinouts` | ❌ Wave 0 |
| SC-2 | `list` exits 0 (already passing, smoke confirm) | CLI | `pytest tests/test_cli_handlers.py::test_list_happy_path` | ✅ exists |
| SC-2 | `search W27` exits 0 | CLI | `pytest tests/test_cli_handlers.py::test_search_happy_path` | ✅ exists |
| SC-2 | `info M2716` (vpp-exceeds-max) exits 0 | CLI | `pytest tests/test_cli_handlers.py::test_info_vpp_exceeds_max_no_crash` | ❌ Wave 0 |
| SC-2 | `info AT28C04` (adapter-required) exits 0 | CLI | `pytest tests/test_cli_handlers.py::test_info_adapter_required_no_crash` | ❌ Wave 0 |
| SC-2 | `read M2716` raises ChipNotImplementedError → exits 1 | CLI | `pytest tests/test_chip_resolver.py::test_resolve_chip_vpp_exceeds_max_raises_not_implemented` | ✅ exists |
| SC-3 | `_generate_pin_names_for_display` with list-valued pin never raises | unit | `pytest tests/test_ic_layout.py` | ❌ Wave 0 |
| SC-4 | Full suite green, cov ≥ 70 | CI | `pytest tests/ --cov=firestarter --cov-fail-under=70` | ✅ infra exists |

### Sampling Rate

- Per task commit: `pytest tests/test_ic_layout.py tests/test_cli_handlers.py -x -q`
- Per wave merge: `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70`
- Phase gate: Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_ic_layout.py` — unit tests for `EpromSpecBuilder._generate_pin_names_for_display` and `build_specifications` for all representative chips (SC-1, SC-3)
- [ ] `tests/test_cli_handlers.py` — add `test_info_happy_path_no_crash`, `test_info_2732_list_valued_pin_no_crash`, `test_info_vpp_exceeds_max_no_crash`, `test_info_adapter_required_no_crash` (SC-1, SC-2)

---

## Security Domain

> `security_enforcement` not explicitly disabled. This phase is a pure display/rendering
> fix with no input from untrusted sources, no auth, no session management, no crypto.
> The only user input is a chip name string that is looked up in a local JSON file.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | — |
| V3 Session Management | No | — |
| V4 Access Control | No | — |
| V5 Input Validation | Minimal | Chip name lookup is dict key lookup in a local file; no SQL, no eval |
| V6 Cryptography | No | — |

No threat vectors introduced by this phase.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | No hidden consumers of pin-map fields exist outside the audited `firestarter/` directory | Pin-field contract | Would need to fix additional consumers |
| A2 | The proposed `_pin_scalar` helper fixes the crash at all sites | Code Examples | If pinouts.json ever has multi-element lists for a pin field, the fix handles them (takes `[0]`); semantically may need `[0]` vs first match logic |
| A3 | `mypy` error count will decrease (not increase) after the fix | CI Gate | The watermark may need to go up if the fix introduces new type errors |

---

## Open Questions

1. **Should `_pin_scalar` be a private method or a module-level function?**
   - What we know: `get_bus_config` uses an inline expression, not a helper
   - What's unclear: whether a helper is idiomatic for this codebase
   - Recommendation: inline expression `val[0] if isinstance(val, list) else val` at each
     site, mirroring `get_bus_config` — no new helper needed

2. **Does Phase 68's `support_status` display require changes to `ic_layout.py` or `eprom_info.py`?**
   - What we know: Phase 68 will add a `support_status` display line to `firestarter info`
   - What's unclear: whether that data flows through `build_specifications` or is added
     directly in `prepare_detailed_eprom_data`
   - Recommendation: Phase 69 should not add support_status display (that's Phase 68's job);
     Phase 69 only ensures info does not crash for non-supported chips

3. **Will the test snapshot for `test_info_known_chip_stderr` become empty after the fix?**
   - What we know: the snapshot currently captures the `TypeError` traceback on stderr
   - What's unclear: whether `firestarter info W27C512` produces any stderr output when working
   - Recommendation: run `pytest --snapshot-update` after fix and inspect new snapshot

---

## Sources

### Primary (HIGH confidence)
- Direct inspection of `/workspaces/firestarter_app/firestarter/ic_layout.py` — crash sites confirmed
- Direct inspection of `/workspaces/firestarter_app/firestarter/data/pinouts.json` — all pin fields confirmed list-valued
- Direct inspection of `/workspaces/firestarter_app/firestarter/database.py` — `get_bus_config` fix pattern confirmed
- Direct inspection of `/workspaces/firestarter_app/firestarter/cli_handlers.py` — full command surface enumerated
- Direct inspection of `/workspaces/firestarter_app/firestarter/chip_resolver.py` — support_status guard confirmed
- Live crash reproduction via `python -c` — TypeError confirmed in devcontainer

### Secondary (MEDIUM confidence)
- `tests/test_eprom_info.py` docstring explicitly notes the ic_layout bug was known and deferred to v1.9
- `tests/test_characterization.py` — `test_info_known_chip` snapshot pins the current broken behavior
- `.planning/ROADMAP.md` Phase 69 section — success criteria verbatim

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Pin-field contract analysis: HIGH — directly inspected JSON + source + reproduced crash
- CLI command surface inventory: HIGH — directly inspected cli_handlers.py
- Fix pattern: HIGH — mirrors existing get_bus_config pattern byte-for-byte
- Test locations / patterns: HIGH — directly inspected existing test suite
- mypy watermark post-fix: MEDIUM — depends on what else the fix changes in ic_layout.py

**Research date:** 2026-06-14
**Valid until:** 2026-07-14 (stable codebase; extends until Phase 68 ships which may change info output shape)

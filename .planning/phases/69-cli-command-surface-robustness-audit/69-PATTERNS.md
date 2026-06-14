# Phase 69: CLI Command-Surface Robustness Audit - Pattern Map

**Mapped:** 2026-06-14
**Files analyzed:** 5 (1 modify source, 1 new test, 2 extend test, 1 update snapshot)
**Analogs found:** 5 / 5

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/ic_layout.py` (modify) | utility / display | transform | `firestarter/database.py` `get_bus_config` (lines 284-299) | exact — same list-or-scalar pin-field extraction problem, already solved |
| `tests/test_ic_layout.py` (new) | test | request-response | `tests/test_eprom_info.py` | role-match — same fixture style (module-scoped `db`/`presenter`), no CliRunner |
| `tests/test_cli_handlers.py` (extend) | test | request-response | itself — existing `test_info_chip_resolution_happy_path` + `test_read_happy_path` | exact — CliRunner + `make_app_context()` pattern |
| `tests/test_eprom_info.py` (extend) | test | request-response | itself — existing `test_prepare_detailed_returns_none_for_missing_eprom` | exact — module-scoped presenter fixture, direct method call |
| `tests/__snapshots__/test_characterization.ambr` (update) | snapshot data | — | itself — `test_info_known_chip` entry (lines 313-350+) | exact — syrupy `.ambr` format |

---

## Pattern Assignments

### `firestarter/ic_layout.py` — `_generate_pin_names_for_display` (modify, utility/transform)

**Analog:** `firestarter/database.py` lines 284-299 (`get_bus_config`)

**Scalar-extraction pattern to copy** (database.py lines 286-289):
```python
pin_val = pin_map_data[pin_func]
# The value can be a list (e.g., [22]) or a single int.
# We'll take the first element if it's a list.
pin_to_check = pin_val[0] if isinstance(pin_val, list) else pin_val
```

**Current broken sites in `_generate_pin_names_for_display`** (ic_layout.py lines 394-408):
```python
# BROKEN — every pin_map_details["X-pin"] is a list, so <= fails with TypeError
if "rw-pin" in pin_map_details and pin_map_details["rw-pin"] <= pin_count:
    pin_names[pin_map_details["rw-pin"] - 1] = "R/W(WE)"
if "vpp-pin" in pin_map_details and pin_map_details["vpp-pin"] <= pin_count:
    pin_names[pin_map_details["vpp-pin"] - 1] = "VPP"
    if (
        "oe-pin" in pin_map_details
        and pin_map_details["oe-pin"] != pin_map_details["vpp-pin"]
        and pin_map_details["oe-pin"] <= pin_count
    ):
        pin_names[pin_map_details["oe-pin"] - 1] = "OE"
elif (
    "oe-pin" in pin_map_details and pin_map_details["oe-pin"] <= pin_count
):
    pin_names[pin_map_details["oe-pin"] - 1] = "OE"
```

**Fixed replacement (apply the `database.get_bus_config` inline pattern)**:
```python
if pin_map_details:
    if "rw-pin" in pin_map_details:
        rw = pin_map_details["rw-pin"]
        rw = rw[0] if isinstance(rw, list) else rw
        if rw <= pin_count:
            pin_names[rw - 1] = "R/W(WE)"
    if "vpp-pin" in pin_map_details:
        vpp = pin_map_details["vpp-pin"]
        vpp = vpp[0] if isinstance(vpp, list) else vpp
        if vpp <= pin_count:
            pin_names[vpp - 1] = "VPP"
            if "oe-pin" in pin_map_details:
                oe = pin_map_details["oe-pin"]
                oe = oe[0] if isinstance(oe, list) else oe
                if oe != vpp and oe <= pin_count:
                    pin_names[oe - 1] = "OE"
    elif "oe-pin" in pin_map_details:
        oe = pin_map_details["oe-pin"]
        oe = oe[0] if isinstance(oe, list) else oe
        if oe <= pin_count:
            pin_names[oe - 1] = "OE"
    if "address-bus-pins" in pin_map_details:
        for i, pin_num in enumerate(pin_map_details["address-bus-pins"]):
            # address-bus-pins elements are already scalar ints — no extraction needed
            if pin_num <= pin_count:
                pin_names[pin_num - 1] = f"A{i}"
```

**Imports pattern** (ic_layout.py lines 1-14 — no change needed):
```python
import logging
from typing import Dict, List, Optional  # noqa: UP035

from firestarter.database import EpromDatabase

logger = logging.getLogger("EpromSpecBuilder")
```

---

### `tests/test_ic_layout.py` (new, test/transform)

**Analog:** `tests/test_eprom_info.py` (entire file — 111 lines)

**Module docstring pattern** (test_eprom_info.py lines 1-11):
```python
"""Phase 42 / ERR-03 fallback coverage lift for ``EpromConsolePresenter`` (D-14
fallback per CONTEXT — eprom_info.py at 19% is the largest gap).

Targets the pure helper methods ... The full ``prepare_detailed_eprom_data``
happy path is NOT exercised here because it triggers the pre-existing ic_layout
``vpp-pin <= pin_count`` TypeError ...
"""
```
For the new file: swap the context to Phase 69 and ic_layout; acknowledge the crash is now fixed.

**Fixture pattern** (test_eprom_info.py lines 14-27):
```python
import pytest

from firestarter.database import EpromDatabase
from firestarter.eprom_info import EpromConsolePresenter


@pytest.fixture(scope="module")
def db() -> EpromDatabase:
    return EpromDatabase(skip_local_override=True)


@pytest.fixture(scope="module")
def presenter(db: EpromDatabase) -> EpromConsolePresenter:
    return EpromConsolePresenter(db)
```
For `test_ic_layout.py`: replace `EpromConsolePresenter` with `EpromSpecBuilder`; the `db` fixture is identical.

**Direct-method test pattern** (test_eprom_info.py lines 29-40):
```python
def test_prepare_detailed_returns_none_for_missing_eprom(
    presenter: EpromConsolePresenter,
) -> None:
    """prepare_detailed_eprom_data returns None when eprom_details is None."""
    result = presenter.prepare_detailed_eprom_data(
        "MISSING_CHIP",
        None,
        None,
        None,
        None,
    )
    assert result is None
```
Pattern for `test_ic_layout.py`: call `spec_builder.build_specifications(eprom_details)` with real chip data from `db.get_eprom("W27C512")` and assert the result is not None. Use `db.get_pin_map(pin_count, pin_map_id)` to fetch pin_map_details to pass directly into `_generate_pin_names_for_display`.

**Representative chip list** (from RESEARCH.md — use these as parametrize values or separate tests):
- `W27C512` — DIP28, vpp-pin+oe-pin shared (list `[22]`)
- `AT28C256` — DIP28, rw-pin+oe-pin (list `[27]`, `[22]`)
- `2732` — DIP24, vpp-exceeds-max, vpp-pin+oe-pin shared (list `[20]`)
- `M2716` — DIP24, vpp-exceeds-max, vpp and oe different pins
- `AT28C16` or `AT28C04` — adapter-required, 24-pin

---

### `tests/test_cli_handlers.py` (extend, test/request-response)

**Analog:** itself — the existing `make_app_context`, `test_read_happy_path`, and `test_info_chip_resolution_happy_path` patterns.

**`make_app_context` factory** (test_cli_handlers.py lines 40-73):
```python
def make_app_context(**manager_overrides) -> AppContext:
    db = manager_overrides.pop("db", None)
    if db is None:
        db = EpromDatabase(skip_local_override=True)
    config_manager = manager_overrides.pop("config_manager", None)
    if config_manager is None:
        config_manager = ConfigManager()
    return AppContext(
        db=db,
        config_manager=config_manager,
        eprom_operator=manager_overrides.pop("eprom_operator", Mock(spec=EpromOperator)),
        hardware_manager=manager_overrides.pop("hardware_manager", Mock(spec=HardwareManager)),
        firmware_manager=manager_overrides.pop("firmware_manager", Mock(spec=FirmwareManager)),
        eprom_presenter=manager_overrides.pop("eprom_presenter", Mock(spec=EpromConsolePresenter)),
    )
```

**KEY DIFFERENCE for info tests:** Pass a REAL `EpromConsolePresenter(db)` instead of the default mock. The `make_app_context` factory already accepts `eprom_presenter=` as an override:
```python
db = EpromDatabase(skip_local_override=True)
app = make_app_context(
    db=db,
    eprom_presenter=EpromConsolePresenter(db),  # real, not mocked
)
result = runner.invoke(cli, ["info", "W27C512"], obj=app)
assert result.exit_code == 0
assert "W27C512" in result.output
```

**CliRunner invocation pattern** (test_cli_handlers.py lines 147-156):
```python
def test_read_happy_path(runner: CliRunner) -> None:
    operator = Mock(spec=EpromOperator)
    operator.read_eprom.return_value = True
    app = make_app_context(eprom_operator=operator)
    result = runner.invoke(cli, ["read", "W27C512", "out.bin"], obj=app)
    assert result.exit_code == 0
    operator.read_eprom.assert_called_once()
```

**Existing broken-behavior test to UPDATE** (test_cli_handlers.py lines 108-116):
```python
def test_info_chip_resolution_happy_path(runner: CliRunner) -> None:
    """`firestarter info W27C512` resolves the chip — note this command currently
    crashes downstream in ic_layout.py (pre-existing TypeError pinned by
    test_characterization::test_info_known_chip with exit 1). This Click-side
    test asserts the chip-resolution PATH succeeds.
    """
    result = runner.invoke(cli, ["info", "W27C512"])
    assert "not found in database" not in result.output
    assert result.exit_code == 1  # <-- MUST change to 0 after fix
```
After the fix: update the docstring and change `exit_code == 1` to `exit_code == 0`; also inject a real presenter.

**New tests to add** (following the same invocation pattern):
- `test_info_happy_path_no_crash` — `info W27C512`, exit 0, "W27C512" in output
- `test_info_2732_list_valued_pin_no_crash` — `info 2732`, exit 0 (vpp-exceeds-max, no crash)
- `test_info_vpp_exceeds_max_no_crash` — `info M2716`, exit 0
- `test_info_adapter_required_no_crash` — `info AT28C16` (or `AT28C04`), exit 0

---

### `tests/test_eprom_info.py` (extend, test/request-response)

**Analog:** itself — the module-scoped `presenter` fixture and existing direct-method call tests.

**Fixture already in place** (test_eprom_info.py lines 19-27): the `db` and `presenter` fixtures are `scope="module"`, so new tests in this file automatically reuse them.

**Pattern for happy-path extension**:
```python
def test_prepare_detailed_eprom_data_happy_path(
    presenter: EpromConsolePresenter,
) -> None:
    """prepare_detailed_eprom_data no longer crashes for W27C512 after ic_layout fix."""
    db = EpromDatabase(skip_local_override=True)
    eprom = db.get_eprom("W27C512")
    assert eprom is not None
    bus_config = db.convert_to_programmer(eprom)
    pin_map = db.get_pin_map(eprom.get("pin-count", 28), eprom.get("pin-map"))
    result = presenter.prepare_detailed_eprom_data(
        "W27C512", eprom, bus_config, pin_map, None
    )
    assert result is not None
```
The exact call signature must be verified against `EpromConsolePresenter.prepare_detailed_eprom_data` — the existing not-found test at line 29 shows it accepts 5 positional args.

---

### `tests/__snapshots__/test_characterization.ambr` (update, snapshot data)

**Analog:** itself — the existing syrupy `.ambr` format. Current broken entries:

```
# name: test_info_known_chip
  ''
# ---
# name: test_info_known_chip[test_info_known_chip_stderr]
  '''
  Traceback (most recent call last):
    File "<PATH>", line N, in <module>
    ...
    TypeError: '<=' not supported between instances of 'list' and 'int'
  '''
```

**Update mechanism** — do NOT hand-edit the `.ambr` file. Use:
```bash
cd /workspaces/firestarter_app
pytest --snapshot-update tests/test_characterization.py::test_info_known_chip
```
After running, the snapshot for `test_info_known_chip` will show exit 0 and formatted chip output; the `test_info_known_chip_stderr` snapshot will become empty or absent.

**Snapshot assertion pattern** (test_characterization.py lines 246-258):
```python
def test_info_known_chip(snapshot):
    stdout, stderr, rc = run_firestarter("info", "W27C512")
    assert rc == 1        # <-- MUST become rc == 0 after fix
    assert stdout == snapshot
    assert stderr == snapshot(name="test_info_known_chip_stderr")
```
After fix: change `assert rc == 1` to `assert rc == 0` in `test_characterization.py` BEFORE regenerating the snapshot, then run `--snapshot-update`.

---

## Shared Patterns

### `EpromDatabase(skip_local_override=True)` seam
**Source:** `tests/test_cli_handlers.py` line 52 (and `test_eprom_info.py` line 21)
**Apply to:** All new and extended test functions that construct a db or app context.
```python
db = EpromDatabase(skip_local_override=True)
```
This is MANDATORY in all tests per Phase 36 D-06: prevents a local `~/.firestarter/database.json` override from flipping CI assertions.

### `runner` fixture (CliRunner)
**Source:** `tests/test_cli_handlers.py` lines 34-37
```python
@pytest.fixture
def runner() -> CliRunner:
    """Fresh CliRunner per test — mix_stderr=True so stderr+stdout flow into result.output."""
    return CliRunner()
```
All new CliRunner tests in `test_cli_handlers.py` get this fixture for free.

### `normalize_output` + subprocess harness
**Source:** `tests/test_characterization.py` lines 64-128
**Apply to:** Any new subprocess-based tests; in-process CliRunner tests do NOT need it (output is already normalized by Click's test runner).

### Inline scalar extraction (no helper function)
**Source:** `firestarter/database.py` lines 287-289
**Apply to:** `ic_layout.py` `_generate_pin_names_for_display` — three pin fields (`rw-pin`, `vpp-pin`, `oe-pin`). Use the inline expression at each site, mirroring the database pattern. Do NOT add a named helper function (not idiomatic in this codebase — `database.py` uses the inline form).

---

## No Analog Found

None. All files have close analogs in the existing codebase.

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tests/`
**Files read:** `ic_layout.py` (lines 1-14, 380-419), `database.py` (lines 280-309), `test_cli_handlers.py` (lines 1-200), `test_eprom_info.py` (full), `test_characterization.py` (full), `tests/__snapshots__/test_characterization.ambr` (lines 1-50, 312-340)
**Pattern extraction date:** 2026-06-14

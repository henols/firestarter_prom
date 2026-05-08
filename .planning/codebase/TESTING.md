# Testing

Source: `/home/henrik/dev/henrik/git/firestarter_prom/firestarter_app/`

## Summary

The project has **no Python unit tests**. There are no `test_*.py`, `*_test.py`, `conftest.py`, or `pytest.ini` files anywhere in the repository. No pytest, unittest, or other Python testing framework is configured.

Testing is done exclusively through **bash integration scripts that require physical hardware** (an Arduino-based RURP programmer connected via serial port).

## Test Scripts

### `firestarter_test.sh`

Location: `/home/henrik/dev/henrik/git/firestarter_prom/firestarter_app/firestarter_test.sh`

A comprehensive end-to-end test suite. Requires a physical EPROM programmer connected to the system.

**Usage:**
```bash
./firestarter_test.sh [EPROM_NAME]
# Defaults to W27C512 if no EPROM name supplied
```

**What it tests (in order):**
1. Firmware version (`firestarter fw`)
2. Hardware version (`firestarter hw`)
3. Hardware config (`firestarter config`)
4. VPP voltage (`firestarter vpp -t 5`)
5. VPE voltage (`firestarter vpe -t 5`)
6. Chip ID check (if EPROM supports it)
7. Write random data to EPROM
8. Verify written data
9. Read back data
10. Binary diff of written vs. read-back data using `xxd` + `colordiff`
11. Erase (if EPROM supports it)
12. Blank check (if EPROM supports it)
13. List all EPROMs
14. Search for EPROM by name
15. Info for EPROM

**Data approach:**
- Generates random binary test data using `dd if=/dev/urandom`
- Splits into two halves (low/high), concatenates into a full image
- Uses `xxd` + `colordiff` for byte-level comparison of written vs. read-back data
- Cleans up temporary files in `./test_data/` on exit via `trap`

**EPROM metadata** is read from `./firestarter/data/database_generated.json` using `jq` to determine memory size, chip ID support, and erase capability.

### `write_test.sh`

Location: `/home/henrik/dev/henrik/git/firestarter_prom/firestarter_app/write_test.sh`

A focused write/verify/read test script (also hardware-dependent).

## No Python Test Infrastructure

- No `pytest` in `requirements.txt` or `pyproject.toml` dependencies
- No `conftest.py` or fixture files
- No mocking patterns (no `unittest.mock`, `pytest-mock`, etc.)
- No coverage configuration (no `.coveragerc`, no `[tool.coverage]` in `pyproject.toml`)
- No CI test configuration found in the repository

## Gap Assessment

The lack of Python unit tests is a significant quality gap. The following modules are candidates for unit testing without requiring hardware:

| Module | Testable without hardware |
|--------|--------------------------|
| `utils.py` | Yes — pure functions (`extract_hex_to_decimal`, `format_size`, `time_formatter`) |
| `constants.py` | Yes — static values |
| `database.py` | Yes — JSON loading/parsing/searching with mock files |
| `eprom_info.py` | Yes — data formatting and display logic |
| `config.py` | Yes — file I/O with temp dirs |
| `serial_comm.py` | Partially — parsing/validation logic; hardware interaction would need mocking |
| `eprom_operations.py` | Partially — flag building, state logic; serial layer would need mocking |

## Run Commands

### Integration tests (require hardware):
```bash
cd /home/henrik/dev/henrik/git/firestarter_prom/firestarter_app
./firestarter_test.sh W27C512
./write_test.sh W27C512
```

### If Python tests were added, the standard invocation would be:
```bash
cd /home/henrik/dev/henrik/git/firestarter_prom/firestarter_app
pip install -e ".[test]"
pytest
```

No `[project.optional-dependencies]` test group exists in `pyproject.toml` currently.

# Technology Stack

**Analysis Date:** 2026-05-08

## Languages

**Primary:**
- Python 3.9+ - Host application (CLI tool, `firestarter_app/`)
- C/C++ (Arduino/AVR) - Firmware (`firestarter/src/`)

**Secondary:**
- Bash - Integration/test scripts (`firestarter_test.sh`, `write_test.sh`)
- Python (scripting) - Build helper (`name_firmware.py`), CI version scripts

## Runtime

**Environment:**
- Python 3.9+ (tested through 3.12; system Python 3.13 present in dev)
- Arduino AVR microcontroller (ATmega328P / ATmega32U4)

**Package Manager:**
- pip with virtualenv (`.venv/` present in `firestarter_app/`)
- Lockfile: not present (only `requirements.txt` and `pyproject.toml`)

## Frameworks

**Core:**
- setuptools >= 45 - Python packaging
- setuptools_scm >= 6.2 - Version management from git tags
- Arduino framework (via PlatformIO) - Firmware build target

**Testing:**
- Bash test scripts (`firestarter_test.sh`, `write_test.sh`) - Hardware integration tests (require physical hardware)
- PlatformIO `pio test` - Firmware unit tests

**Build/Dev:**
- PlatformIO - Firmware build, upload, and test system for Arduino targets
- `python3 -m build` - Python wheel/sdist packaging (used in CI)

## Key Dependencies

**Critical:**
- pyserial >= 3.5 - Serial communication with Arduino programmer hardware
- requests >= 2.20 - HTTP client for fetching firmware releases from GitHub API
- tqdm >= 4.60 - Progress bars for read/write operations
- argcomplete >= 3.6.2 - Bash/shell tab-completion for CLI
- rich >= 14.0 - Rich terminal output (confirmation prompts via `rich.prompt.Confirm`)

**Infrastructure:**
- jsmn (vendored C lib, `firestarter/lib/`) - Lightweight JSON parser used in firmware
- avrdude (external system tool) - Required at runtime for flashing firmware to Arduino
- Arduino standard library (`<Arduino.h>`) - Firmware hardware abstraction

## Configuration

**Environment:**
- User config directory: `~/.firestarter/` (JSON files)
- Configurable via `firestarter config` CLI command
- Key runtime config: serial port, baud rate (250000), hardware revision, resistor calibration values (R1/R2)
- EPROM database overrides: `~/.firestarter/database.json` and `~/.firestarter/pin-maps.json`

**Build:**
- `firestarter_app/pyproject.toml` - Python package metadata, dependencies, entry points
- `firestarter/platformio.ini` - Firmware build environments and flags
- Build flags: `MONITOR_SPEED`, `HARDWARE_REVISION`, `DEV_TOOLS`, `SERIAL_DEBUG` (opt-in), `DATA_BUFFER_SIZE`

## Platform Requirements

**Development:**
- Python 3.9+ with pip
- PlatformIO CLI (for firmware development)
- avrdude (for firmware flashing)
- Physical RURP Arduino shield hardware for integration testing

**Production:**
- Cross-platform Python application (OS Independent per PyPI classifiers)
- Arduino Uno or Leonardo with RURP shield
- USB serial port access

---

*Stack analysis: 2026-05-08*

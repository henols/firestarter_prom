# Structure

**Analysis Date:** 2026-05-08

## Repository Layout

This is a monorepo containing two independent sub-projects — the Python host application and the Arduino firmware — each with their own git history, dependencies, and build system.

```
firestarter_prom/                    # Monorepo root
├── firestarter_app/                 # Python host CLI application (pip package)
└── firestarter/                     # Arduino C++ firmware (PlatformIO project)
```

---

## Python Application: `firestarter_app/`

```
firestarter_app/
├── pyproject.toml                   # Build config: setuptools, version from SCM, entry point
├── requirements.txt                 # Dev/test dependencies
├── CLAUDE.md                        # AI development guidance
├── README.md                        # User documentation
├── MANIFEST.in                      # Package file inclusion rules
├── firestarter_test.sh              # Comprehensive hardware test suite (bash)
├── write_test.sh                    # Write/verify focused test script (bash)
│
├── firestarter/                     # Main Python package
│   ├── __init__.py                  # Version string: __version__ = "2.0.7_dev"
│   ├── main.py                      # CLI entry point; argparse + command dispatch
│   ├── eprom_operations.py          # EpromOperator: read/write/verify/erase/blank/id
│   ├── serial_comm.py               # SerialCommunicator: port discovery, protocol I/O
│   ├── database.py                  # EpromDatabase singleton: EPROM DB + pin translation
│   ├── config.py                    # ConfigManager singleton: ~/.firestarter/config.json
│   ├── firmware.py                  # FirmwareManager: version check, download, avrdude flash
│   ├── hardware.py                  # HardwareManager: VPP/VPE voltage, HW revision/config
│   ├── eprom_info.py                # EpromConsolePresenter: formats EPROM info for display
│   ├── ic_layout.py                 # EpromSpecBuilder: builds technical spec dictionaries
│   ├── logging_utils.py             # SingleLineStatusHandler: in-place console status lines
│   ├── constants.py                 # Command codes, flag bits, baud rate, buffer sizes
│   ├── utils.py                     # hex-string-to-decimal helper
│   ├── avr_tool.py                  # Avrdude wrapper: locate binary, flash .hex files
│   └── data/                        # Bundled data files (included in package)
│       ├── minipro_complete_db.json # Primary EPROM database (new format)
│       ├── database_generated.json  # Legacy generated database
│       ├── database_overrides.json  # Override entries for generated database
│       ├── pin-maps.json            # Legacy pin map configurations
│       └── pinouts.json             # Current pinout definitions keyed by variant name
│
├── doc/                             # Additional documentation
├── images/                          # Screenshot/diagram assets
├── tools/                           # Developer utilities
├── build/                           # Build artifacts (not committed)
├── firestarter.egg-info/            # Installed package metadata
│
└── .planning/                       # GSD planning documents
    └── codebase/                    # Codebase analysis (this directory)
        ├── ARCHITECTURE.md
        └── STRUCTURE.md
```

### Key Python Files by Role

| File | Class/Function | Role |
|------|---------------|------|
| `main.py` | `main()` | CLI entry, argparse, command routing |
| `eprom_operations.py` | `EpromOperator` | All EPROM hardware operations |
| `serial_comm.py` | `SerialCommunicator` | Serial port I/O and protocol |
| `database.py` | `EpromDatabase` | EPROM spec lookup and pin translation |
| `config.py` | `ConfigManager` | Persistent user config (~/.firestarter/) |
| `firmware.py` | `FirmwareManager` | Firmware version, download, flashing |
| `hardware.py` | `HardwareManager` | VPP/VPE voltage, HW revision |
| `eprom_info.py` | `EpromConsolePresenter` | Console display of EPROM details |
| `ic_layout.py` | `EpromSpecBuilder` | Technical spec dict construction |
| `constants.py` | (module-level) | All shared constants and flag bits |
| `avr_tool.py` | `Avrdude` | avrdude subprocess wrapper |

### User Config Location

```
~/.firestarter/
├── config.json        # Saved port, avrdude paths, hw config
├── database.json      # User EPROM database overrides (optional)
└── pin-maps.json      # User pin map overrides (optional)
```

---

## Arduino Firmware: `firestarter/`

```
firestarter/
├── platformio.ini               # Build environments: uno, leonardo
├── name_firmware.py             # Pre-build script: names .hex by board
├── CLAUDE.md                    # AI development guidance
├── README.md                    # Firmware documentation
│
├── src/                         # Firmware source files
│   ├── firestarter.cpp          # Main loop, command dispatch, state machine
│   ├── eprom_operations.cpp     # read/write/verify/erase/blank_check/chip_id
│   ├── hardware_operations.cpp  # VPP/VPE voltage reading, HW revision, config
│   ├── json_parser.c            # JSON command parsing (C, not C++)
│   ├── logging.c                # Serial response formatting (prefix-tagged)
│   ├── operation_utils.cpp      # Shared operation helpers
│   ├── rurp_config_utils.cpp    # EEPROM-persisted hardware config (R1/R2/rev)
│   ├── dev_tools.cpp            # Dev commands: direct register/address access
│   │
│   ├── boards/                  # Board-specific hardware abstraction
│   │   ├── rurp_common.cpp      # Common RURP shield logic
│   │   ├── uno_rurp_shield.cpp  # Arduino Uno implementation
│   │   ├── leonardo_rurp_shield.cpp  # Arduino Leonardo implementation
│   │   └── rurp_serial_utils.cpp    # Serial utility functions
│   │
│   └── proms/                   # Memory device type handlers
│       ├── eprom.cpp            # UV-erasable EPROM support
│       ├── flash_type_3.cpp     # Flash memory type 3 (AMD standard)
│       ├── flash_type_4.cpp     # Flash memory type 4 (AMD alternate)
│       ├── flash_utils.cpp      # Shared flash operation utilities
│       ├── memory.cpp           # Generic memory operations base
│       └── sram.cpp             # SRAM device support
│
├── include/                     # Header files
│   ├── firestarter.h            # firestarter_handle_t, bus_config_t definitions
│   ├── eprom.h / eprom_operations.h  # EPROM op declarations
│   ├── hardware_operations.h    # Hardware op declarations
│   ├── json_parser.h            # JSON parser interface
│   ├── logging.h                # Logging/response interface
│   ├── memory.h / memory_utils.h     # Memory abstraction
│   ├── rurp_shield.h            # RURP shield register definitions
│   ├── rurp_types.h             # Shared type definitions
│   ├── rurp_register_utils.h    # Register manipulation helpers
│   ├── rurp_hw_rev_utils.h      # Hardware revision detection
│   ├── rurp_internal_register_utils.h
│   ├── rurp_serial_utils.h
│   ├── flash_type_3.h / flash_type_4.h / flash_utils.h / sram.h
│   ├── operation_utils.h
│   ├── dev_tools.h
│   └── version.h                # Firmware version constant
│
├── lib/                         # Local libraries (PlatformIO convention)
│
├── test/                        # Unit tests (pio test)
│   └── test_data/               # Test binary data files
│
├── test_data/                   # Test binary fixtures
│
└── .pio/                        # PlatformIO build cache (not committed)
```

### Key Firmware Files by Role

| File | Role |
|------|------|
| `src/firestarter.cpp` | Main loop, JSON dispatch, three-phase state machine |
| `src/eprom_operations.cpp` | Core EPROM/Flash/EEPROM operations |
| `src/hardware_operations.cpp` | Voltage measurement, revision detection |
| `src/json_parser.c` | Parses `{...}` JSON commands from serial |
| `src/logging.c` | Emits `OK:`, `DATA:`, `ERROR:`, `MAIN:`, etc. |
| `include/firestarter.h` | Central `firestarter_handle_t` state struct |
| `include/rurp_shield.h` | Hardware register and pin definitions |

---

## Build Environments

### Python Application
- **Python:** 3.9+
- **Build:** `pip install -e .` (setuptools + setuptools_scm)
- **Entry point:** `firestarter` → `firestarter.main:main`
- **Runtime deps:** `pyserial`, `requests`, `tqdm`, `argcomplete`, `rich`

### Arduino Firmware
- **Build tool:** PlatformIO
- **Targets:** `uno` (ATmega328P, 512-byte buffer), `leonardo` (ATmega32U4, 1024-byte buffer)
- **Serial speed:** 250000 baud
- **Key flags:** `HARDWARE_REVISION` (enabled), `DEV_TOOLS` (enabled), `SERIAL_DEBUG` (commented out)

---

## Where to Find Things

| Task | Location |
|------|----------|
| Add a new CLI command | `firestarter_app/firestarter/main.py` — add `create_*_args()` and dispatch in `main()` |
| Add a new EPROM operation | `firestarter_app/firestarter/eprom_operations.py` + corresponding firmware op |
| Change serial protocol | `firestarter_app/firestarter/serial_comm.py` + `firestarter/src/firestarter.cpp` |
| Add an EPROM to the database | `firestarter_app/firestarter/data/minipro_complete_db.json` or `~/.firestarter/database.json` |
| Change pin-map / bus config | `firestarter_app/firestarter/data/pinouts.json` or `database.py::pin_conversions` |
| Modify firmware main loop | `firestarter/src/firestarter.cpp` |
| Add a new memory device type | `firestarter/src/proms/` (new .cpp + header) |
| Change board HAL | `firestarter/src/boards/` |
| Adjust user config persistence | `firestarter_app/firestarter/config.py` |
| Modify firmware flash/install | `firestarter_app/firestarter/firmware.py` + `avr_tool.py` |
| Change constants/flags | `firestarter_app/firestarter/constants.py` + `firestarter/include/firestarter.h` |

---

*Structure analysis: 2026-05-08*

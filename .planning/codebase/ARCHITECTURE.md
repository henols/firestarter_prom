# Architecture

**Analysis Date:** 2026-05-08

## Pattern Overview

**Overall:** Layered CLI application with hardware abstraction and singleton service objects, communicating with embedded firmware via a JSON-over-serial state machine protocol.

The project is a monorepo containing two co-dependent sub-projects:
1. `firestarter_app/` - Python host-side CLI application (pip package)
2. `firestarter/` - Arduino C++ firmware for the RURP shield (PlatformIO project)

**Key Characteristics:**
- Singleton pattern for shared services (EpromDatabase, ConfigManager)
- Command-pattern CLI dispatch via argparse subparsers in `main.py`
- Three-phase state machine protocol (INIT / MAIN / END) for all hardware operations
- Hardware abstraction separates EPROM operations, hardware management, and firmware management into distinct manager classes
- JSON commands sent to firmware; structured prefix-tagged text responses returned (`OK:`, `DATA:`, `ERROR:`, etc.)

## Layers

**CLI / Entry Point Layer:**
- Purpose: Argument parsing, user input validation, command routing, logging configuration
- Location: `firestarter_app/firestarter/main.py`
- Contains: `main()` function, argparse subparser builders, `EpromCompleter` for tab-completion, `build_arg_flags()` helper
- Depends on: All manager/service classes, EpromDatabase, constants
- Used by: Console entry point `firestarter` (defined in `pyproject.toml`)

**Service / Manager Layer:**
- Purpose: Domain-specific business logic, serial communication orchestration, firmware management
- Location: `firestarter_app/firestarter/`
- Contains:
  - `EpromOperator` (`eprom_operations.py`) - read/write/erase/verify/blank-check/chip-id operations
  - `HardwareManager` (`hardware.py`) - VPP/VPE voltage reading, hardware revision and config
  - `FirmwareManager` (`firmware.py`) - firmware version check, download, and avrdude-based flashing
  - `EpromConsolePresenter` (`eprom_info.py`) - structured display of EPROM info
  - `EpromSpecBuilder` (`ic_layout.py`) - builds technical spec dictionaries for display
- Depends on: SerialCommunicator, EpromDatabase, ConfigManager, constants
- Used by: CLI layer

**Data / Repository Layer:**
- Purpose: EPROM database management, configuration persistence, pin-map translation
- Location: `firestarter_app/firestarter/`
- Contains:
  - `EpromDatabase` (`database.py`) - singleton, loads/merges JSON databases, translates pinouts to RURP bus config
  - `ConfigManager` (`config.py`) - singleton, persists app config to `~/.firestarter/config.json`
- Depends on: JSON data files in `firestarter/data/`, `~/.firestarter/` user overrides
- Used by: All manager classes and CLI layer

**Communication Layer:**
- Purpose: Serial port discovery, connection, JSON command dispatch, response parsing
- Location: `firestarter_app/firestarter/serial_comm.py`
- Contains: `SerialCommunicator` class, custom exceptions (`SerialError`, `ProgrammerNotFoundError`, `FirmwareOutdatedError`), `Response` namedtuple
- Depends on: `pyserial`, ConfigManager, constants
- Used by: EpromOperator, HardwareManager, FirmwareManager

**Firmware Layer (Embedded C++):**
- Purpose: Direct hardware control of the RURP shield; processes JSON commands and drives address/data bus
- Location: `firestarter/src/`
- Contains: `firestarter.cpp` (main loop + state machine), `eprom_operations.cpp`, `hardware_operations.cpp`, `json_parser.c`, board-specific HAL in `src/boards/`, device handlers in `src/proms/`
- Depends on: Arduino framework, PlatformIO build system
- Used by: Python host via serial port

## Data Flow

**EPROM Write Operation:**

1. User runs `firestarter write W27C512 data.bin`
2. `main.py` parses args, fetches EPROM data from `EpromDatabase`, calls `EpromOperator.write_eprom()`
3. `EpromOperator._setup_operation()` builds JSON command dict (memory-size, type, vpp, bus-config, cmd=2, flags)
4. `SerialCommunicator.find_and_connect()` probes serial ports, sends command JSON, validates firmware version from `OK:` response
5. `EpromOperator._run_state_machine()` drives three phases:
   - INIT: sends ACK, waits for `INIT:` signal from firmware
   - MAIN: firmware requests data chunks via `OK:` messages; host sends `#<len><checksum>` header then binary data block (512 bytes at a time); firmware sends `MAIN:` when done
   - END: waits for `END:` signal, sends final ACK
6. File is read in 512-byte chunks (`BUFFER_SIZE`), XOR checksum computed per chunk, progress tracked via `tqdm`
7. Result (`bool`) returned up through layers to `main.py`, which sets process exit code

**EPROM Read Operation:**

1. Similar setup as write, `cmd=1`
2. During MAIN phase, firmware sends `DATA:` signals followed by a binary block (2-byte length + 1-byte checksum + data)
3. `SerialCommunicator.read_data_block()` reads length, validates checksum, returns bytes
4. Callback writes bytes to output file at correct offset
5. Host ACKs each block; firmware sends `MAIN:` when complete

**Firmware Update Flow:**

1. `FirmwareManager.check_current_firmware()` connects, sends `COMMAND_FW_VERSION` state command
2. Parses version and board name from response
3. `fetch_latest_release_info()` hits GitHub Releases API to find latest `.hex` asset URL
4. If update needed (or forced), downloads `.hex` via HTTP to `~/.firestarter/`
5. `Avrdude` wrapper (`avr_tool.py`) invokes `avrdude` process to flash the hex file

**State Management:**
- No persistent in-memory state between CLI invocations (stateless CLI)
- `ConfigManager` persists last-used serial port and avrdude paths to `~/.firestarter/config.json`
- `EpromDatabase` is a singleton initialized once per process; data is read-only after init
- Arduino firmware maintains its own EEPROM-persisted config (`rurp_configuration_t`) for hardware calibration values

## Key Abstractions

**EpromOperator (context manager + state machine):**
- Purpose: Encapsulates the full lifecycle of a hardware operation (connect, run state machine, disconnect)
- Examples: `firestarter_app/firestarter/eprom_operations.py`
- Pattern: Context manager (`_operation_context`) wraps `_run_state_machine()`; main-phase behavior injected via `main_phase_handler` callable (strategy pattern)

**EpromDatabase (Singleton + data mapper):**
- Purpose: Authoritative source for EPROM specifications; translates generic DIP pin numbers to RURP hardware bus lines
- Examples: `firestarter_app/firestarter/database.py`
- Pattern: Singleton via `__new__`; `_map_data()` converts raw JSON schema to normalized dict; `convert_to_programmer()` produces the compact dict sent over serial

**SerialCommunicator (factory + protocol parser):**
- Purpose: Port auto-discovery, JSON command dispatch, prefix-tagged response parsing, binary data block I/O
- Examples: `firestarter_app/firestarter/serial_comm.py`
- Pattern: `find_and_connect()` class method probes ports; generator `_read_and_parse_lines()` yields parsed `Response` namedtuples; firmware version gating at connection time

**Three-Phase Serial Protocol:**
- Purpose: Reliable handshake between host and firmware for all operations
- Pattern: INIT phase (setup/config ACK), MAIN phase (data transfer with per-block ACK and checksum), END phase (completion confirmation); firmware uses prefix-tagged text lines (`OK:`, `DATA:`, `MAIN:`, `END:`, `ERROR:`)

**firestarter_handle_t (Firmware central state):**
- Purpose: Central state struct holding all operation context on the firmware side
- Examples: `firestarter/include/firestarter.h`
- Pattern: Struct with function pointers for device-specific operations (polymorphic behavior without C++ vtables in C context)

## Entry Points

**Python CLI:**
- Location: `firestarter_app/firestarter/main.py` — `main()` function
- Triggers: `firestarter` console script (defined in `pyproject.toml [project.scripts]`)
- Responsibilities: Argument parsing, logging setup, service instantiation, command dispatch

**Arduino Firmware Main Loop:**
- Location: `firestarter/src/firestarter.cpp`
- Triggers: Arduino `setup()` / `loop()` framework calls
- Responsibilities: JSON command parsing, state machine dispatch, timeout management, serial I/O

## Error Handling

**Strategy:** Layered exception hierarchy in Python; error prefix responses from firmware

**Patterns:**
- Custom exceptions in serial layer: `SerialError`, `SerialTimeoutError`, `ProgrammerNotFoundError`, `FirmwareOutdatedError` — caught at manager layer boundaries, converted to `logger.error()` + `False` return
- `EpromOperationError` raised within `_run_state_machine()` when firmware sends `ERROR:` response
- Context manager `_operation_context` ensures `SerialCommunicator.disconnect()` is always called via `finally`
- CLI layer receives `bool` return values from managers; maps `False` to exit code 1
- Firmware sends `ERROR:<message>` on hardware failures; `WARN:<message>` for non-fatal issues
- `SIGINT` handler in `main.py` logs warning and calls `sys.exit(1)` for clean keyboard interrupt

## Cross-Cutting Concerns

**Logging:** Python standard `logging` module used throughout; custom `SingleLineStatusHandler` in `logging_utils.py` supports in-place status line updates (`status='start'`/`'end'` extras) for connection progress; verbose mode adds module/line info; `tqdm` progress bars used for data transfer with `logging_redirect_tqdm` integration

**Validation:** EPROM name validation at CLI (tab-completion via `EpromCompleter`, error if not found in DB); address/size string parsing accepts both decimal and hex (`0x` prefix); flag validation in dev commands; firmware version semver comparison on every connection

**Authentication:** None (local hardware access only); firmware version gating enforces minimum 2.0.0 requirement

---

*Architecture analysis: 2026-05-08*

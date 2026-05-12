# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is a meta-repo / planning repo for the Firestarter EPROM programmer project. The actual code lives in two sub-repos:

- `firestarter/` — Arduino C++ firmware (PlatformIO). See `firestarter/CLAUDE.md`.
- `firestarter_app/` — Python host CLI application (pip package). See `firestarter_app/CLAUDE.md`.

This repo tracks only `.planning/` (GSD project management artifacts) and `.claude/` (project settings). Neither sub-repo is committed here.

## System Overview

Firestarter is a two-part system for programming EPROMs, Flash, and SRAM devices using an Arduino-based RURP (Relatively-Universal-ROM-Programmer) shield:

1. **Python CLI** (`firestarter_app/`) — runs on the host PC; parses user commands, looks up EPROM specs from a JSON database, and orchestrates operations via serial.
2. **Arduino firmware** (`firestarter/`) — runs on the Arduino; receives JSON commands, drives the hardware bus, and streams binary data back using a three-phase state machine protocol (INIT → MAIN → END).

The protocol runs at 250000 baud. Commands are JSON objects; responses are prefix-tagged lines (`OK:`, `DATA:`, `MAIN:`, `END:`, `ERROR:`).

## Development Commands

### Python app (run from `firestarter_app/`)
```bash
pip install -e .                  # install in dev mode
firestarter --help                # verify install
./firestarter_test.sh [EPROM]     # full hardware integration test
./write_test.sh [EPROM]           # write/verify test
```

### Firmware (run from `firestarter/`)
```bash
pio run -e uno                    # build for Arduino Uno
pio run -e leonardo               # build for Arduino Leonardo
pio run -t upload -e uno          # flash to board
pio run -t monitor -e uno         # serial monitor at 250000 baud
pio test                          # run unit tests
```

## Key Architecture Points

- **EPROM database** is in `firestarter_app/firestarter/data/chip_database.json`; user overrides go in `~/.firestarter/database.json`. `EpromDatabase` (singleton) translates generic DIP pin numbers to RURP bus config before sending to firmware.
- **Serial protocol changes** must be kept in sync between `firestarter_app/firestarter/serial_comm.py` and `firestarter/src/firestarter.cpp`.
- **Constants/flag bits** are duplicated between `firestarter_app/firestarter/constants.py` (Python) and `firestarter/include/firestarter.h` (C++). Change both together.
- **Board differences**: Uno has a 512-byte data buffer; Leonardo has 1024 bytes. Buffer size affects chunked transfer in `eprom_operations.py`.
- Hardware calibration (R1/R2 resistor values, board revision) is persisted in Arduino EEPROM via `rurp_configuration_t`.

# Project: Firestarter — Protocol-Aware Programming Architecture

**Created:** 2026-05-08

## Vision

Replace the current guessing-based chip type mapping with an explicit, protocol-driven architecture where every chip in the database has a known, correct programming algorithm — and the firmware executes exactly that algorithm.

## The Core Problem

The current system has a broken data pipeline:

1. **minipro XML** has `protocol_id` — a precise, tested identifier for the correct programming algorithm (e.g. `0x07 = EPROM_STD`, `0x05 = FLASH_AMD_STD`, `0x10 = FLASH_INTEL`)
2. **parse_db scripts** either discard `protocol_id` (parse_db.py) or map it to a string but then lose it (parse_db_2.py)
3. **database.py** re-derives the type by guessing from secondary fields (flags, name patterns)
4. **Firmware** receives a `type` byte (1–5) and dispatches to one of 5 implementations — but TYPE_FLASH_INTEL, TYPE_EEPROM_POLL, and NVRAM types don't exist yet

Result: chips get programmed with the wrong algorithm → verify failures, silent data corruption, or unsupported errors.

## What Must Be TRUE

For this project to be complete:

1. **minipro `protocol_id` is the authoritative source** — it flows from XML directly to the database entry, never discarded or re-derived
2. **An explicit `algorithm` field is transmitted over serial** — the JSON command includes a dedicated field that maps 1:1 with minipro protocol IDs; the legacy `type` field is replaced or supplemented
3. **Firmware dispatches on `algorithm`, not `type`** — new firmware implementations cover: UV-EPROM (STD, QUICK, LEGACY), Flash AMD (STD, ALT), Flash Intel, EEPROM Poll
4. **Database pipeline is deterministic** — given the same minipro XML entry, the output algorithm value is always correct and never guessed
5. **DIP 24/28/32 packages are fully covered** — all major families work: 27xx UV-EPROM, 29xx/39xx Flash AMD, Intel Flash, parallel EEPROM/NVRAM

## Out of Scope

- SMD packages, ICSP/serial interfaces, PLCC adapters
- MCU, PLD, logic device types
- Any protocol outside minipro's DIP parallel memory types
- GUI or web interface

## The One Thing That Must Work

A W27C512 (UV-EPROM), a 29F040 (Flash AMD), an SST39SF040 (Flash Intel), and a 28C256 (EEPROM) can all be read, written, verified, and erased correctly — with the algorithm chosen from the database, not guessed.

## Approach

- **Database layer:** `parse_db_2.py` becomes the canonical pipeline; outputs `algorithm` field using direct minipro `protocol_id` mapping (no inference)
- **Wire protocol:** Add `algorithm` to the JSON command sent over serial (alongside or replacing `type`)
- **Firmware:** Refactor `memory.cpp` dispatch to use `algorithm`; implement missing handlers
- **Pinouts:** `pinouts.json` is the physical layer; mapping from protocol→pinout is explicit, not inferred from variant+pin_count heuristics

## Sub-Repos

- `firestarter_app/` — Python host CLI, database pipeline, serial protocol
- `firestarter/` — Arduino firmware, algorithm implementations

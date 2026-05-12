# Requirements: Firestarter v1.1 — Safety Closure & Hardware Validation

**Defined:** 2026-05-11
**Core Value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritatively from upstream XML → DB → wire JSON → firmware handler, and every chip-family path satisfies its REQ-SAF-01 pre-write voltage check.

## v1.1 Requirements

Each requirement maps to exactly one phase in `ROADMAP.md`. v1.0 requirements are already validated (see `.planning/milestones/v1.0-REQUIREMENTS.md`) and not re-listed here.

### Safety Closure

- [x] **SAF-04**: `flash_intel_write_init` calls `rurp_read_voltage_mv()` and aborts if the measured VPP is below the chip's `vpp` setpoint (in millivolts) minus the existing tolerance window, before issuing the first write command — closing REQ-SAF-01 for all 39 algorithm=0x10 Intel-flash chips.
- [x] **SAF-05**: `eeprom_28c.cpp::eeprom28c_write_init` honours `handle->chip_id` when non-zero — performs the same chip-ID validation the UV-EPROM and Intel/AMD-flash paths already do, so REQ-SAF-02 holds the moment any algorithm=0x0D entry gains a `chip_id_value` (forward-compat).
- [x] **SAF-06**: A Unity test on `[env:native]` covers the new Intel-flash VPP check (low-VPP path returns the existing voltage error code; nominal-VPP path proceeds) and a fake-chip-ID test covers the new 28C path (matching ID proceeds; mismatching ID aborts).

### Retroactive Verification

- [ ] **VERIF-01**: Phase 01 (database pipeline) has a `01-VERIFICATION.md` artifact in `.planning/phases/...` produced by `/gsd-validate-phase` (or equivalent retroactive audit), scoring its REQ-DB-01..04 mapping against the current `minipro_complete_db.json`.
- [ ] **VERIF-02**: Phase 02 (firmware JSON parse) has an `02-VERIFICATION.md` covering REQ-SER-01 / REQ-FW-01 against current `firestarter.cpp` + `firestarter_app/firestarter/serial_comm.py`.
- [ ] **VERIF-03**: Phase 03 (UV-EPROM algorithm) has an `03-VERIFICATION.md` covering REQ-FW-02 / REQ-SAF-01 (UV-EPROM path) against current `eprom.cpp`.
- [ ] **VERIF-04**: Phase 04 (Flash sector erase) has a `04-VERIFICATION.md` covering REQ-FW-03 against current `flash3.cpp`.
- [ ] **VERIF-05**: Phase 05 (Intel flash) has a `05-VERIFICATION.md` covering REQ-FW-04 against current `flash_intel.cpp` (and notes the SAF-04 closure delivered in this milestone).
- [ ] **VERIF-06**: Phase 06 (EEPROM page write) has a `06-VERIFICATION.md` covering REQ-FW-04+ for the 28C path against current `eeprom_28c.cpp`.
- [ ] **VERIF-07**: Phase 07 (chip-ID safety) has a `07-VERIFICATION.md` covering REQ-SAF-02 across UV-EPROM + Intel + AMD families.
- [ ] **VERIF-08**: Phase 08 (integration) has an `08-VERIFICATION.md` covering REQ-SAF-03 (blank check gating) against the current write-init chain.
- [ ] **VERIF-09**: Phase 09 (adapter support) has a `09-VERIFICATION.md` covering REQ-UX-01 / REQ-UX-02 (search-flag + info --adapter table) against the current Python CLI.
- [ ] **VERIF-10**: Phase 10 (static pins) has a `10-VERIFICATION.md` covering REQ-FW-05 / REQ-FW-06 (`static_high_mask` end-to-end + `pins < 32` VPE_TO_VPP guard) against the current firmware.

### Hardware Validation

- [ ] **HW-01**: `firestarter_test.sh` and `write_test.sh` run cleanly against the current `minipro_complete_db.json` — both scripts updated to remove the `database_generated.json` reference (WARNING-4) and any other paths that drifted post-Phase-11.
- [ ] **HW-02**: A physical RURP shield programs and verifies a W27C512 (algo=0x07, UV-EPROM) using `firestarter write` then `firestarter read --verify`; results logged in `.planning/phases/.../HW-VALIDATION.md`.
- [ ] **HW-03**: A physical RURP shield programs and verifies an AM29F040 (algo=0x06, AMD flash, full chip-erase + write) and an SST39SF040 (algo=0x06, AMD flash, sector-erase + write); both logged.
- [ ] **HW-04**: A physical RURP shield programs and verifies an AT28C256 (algo=0x0D, 5V EEPROM via Phase 13 override) — confirms zero VPP regulator engagement on the scope/multimeter during the write window; logged.
- [ ] **HW-05**: A physical RURP shield programs and verifies an Intel-family flash (AM28F010 or 28F256, algo=0x10) **after** SAF-04 ships — confirms the new VPP ADC compare gates a deliberately-underpowered VPP run; logged.

### Naming Cleanup

- [ ] **WIRE-01**: Wire JSON `"vpp"` key (which currently carries millivolts) is renamed to `"vpp_mv"` in the Python emitter (`firestarter_app/firestarter/eprom_operations.py` / `serial_comm.py` / `database.py::convert_to_programmer` family), the firmware parser (`firestarter.cpp` / `json_parser.c` ArduinoJson key), and `firestarter_app/CLAUDE.md` example — eliminating the volts/millivolts semantic overload (WARNING-3).
- [ ] **WIRE-02**: A `check_dispatch.py` (or equivalent host-side) test confirms every chip in the regenerated DB still parses end-to-end on both Uno + Leonardo simulator after the rename — no algorithm=0x?? entry regresses on the wire.
- [ ] **CLEAN-01**: The data filename `firestarter/data/minipro_complete_db.json` is renamed to a neutral name (e.g. `chip_database.json`) — the file is *our* DB derived from the upstream XML, not the minipro tool's own artifact. All references updated atomically: `tools/build_db.py:12` (OUTPUT_FILE), `firestarter/database.py:189` (default path) + `:366` (docstring), `tools/check_dispatch.py:2` (docstring) + `:27` (data-dir glob), meta `CLAUDE.md:44`, `firestarter_app/CLAUDE.md` Pipeline section, `firestarter/CLAUDE.md:30`.
- [ ] **CLEAN-02**: Unnecessary "minipro" mentions in app code comments and docs are removed. Single attribution kept in `tools/build_db.py` (which owns `MINIPRO_XML_URL` — the actual upstream URL constant) and one line in `firestarter_app/CLAUDE.md` naming the upstream source. Replace remaining `# Algorithm (minipro protocol_id) → ...` comments in `firestarter/database.py:45,389` and `tools/check_dispatch.py:30` with neutral wording (`# Algorithm (upstream protocol_id) → ...` or `# Algorithm integer → ...`). Reduce `firestarter_app/CLAUDE.md` from 6 mentions to 1; `firestarter/CLAUDE.md` from 2 mentions to 0 (firmware never sees minipro).

### Documentation

- [ ] **DOC-01**: `.planning/MILESTONES.md` gains a v1.1 entry summarising what shipped, with the same Known Gaps / Hardware Verification / Key Decisions structure used by the v1.0 entry. (Written at milestone close, not during phases — placeholder phase 7 tracks it.)

## Future Requirements

Tracked but deferred past v1.1 (carry to v1.2 or beyond):

### Build Pipeline Robustness

- **DB-06**: `build_db.py` replaces bare `except:` blocks at ~138-186 with explicit narrow exceptions; `requests.get` gets `raise_for_status()` and an explicit `timeout=`.
- **DB-07**: `minipro_complete_db.json` re-emits a `verified` field so `database.py::get_eproms(verified=True)` stops silently returning empty.

### Pinout Coverage

- **FW-07**: `pinouts.json` `static-high-pins` coverage extended to DIP28 and DIP32 quirk pins (CE2 / JEDEC-tied NC), removing the DIP24-only gap (INFO-3).
- **FW-08**: Audit whether `DIP24_2732` pinout should ever appear in the regenerated DB (currently zero 24-pin variant=0x01 chips survive the filter on current `infoic.xml`).

## Out of Scope

| Feature | Reason |
|---------|--------|
| Adding chip families outside DIP24/28/32 parallel memory | v1.0 boundary still holds |
| Restructuring the wire protocol (binary, length-prefixed, CRC32) | Per-operation overhead trivial on local USB serial |
| Replacing minipro as the upstream DB source | `infoic.xml` is authoritative; one override is sufficient |
| New CLI subcommands beyond what already exists | v1.1 is closure, not feature growth |
| Web/GUI frontend | Still out (carried from v1.0) |
| MCU / PLD / logic-device support | Still out (carried from v1.0) |
| Rewriting any of the five existing handlers (eprom / flash3 / flash_intel / eeprom28c / sram) beyond the SAF-04 / SAF-05 edits | Out — the handlers were validated by v1.0 structural tests; this milestone touches them surgically |
| Full-image CRC32 verification | Per-chunk XOR sufficient |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SAF-04 | Phase 1 | Complete |
| SAF-05 | Phase 1 | Complete |
| SAF-06 | Phase 1 | Complete |
| VERIF-01 | Phase 3 | Pending |
| VERIF-02 | Phase 3 | Pending |
| VERIF-03 | Phase 3 | Pending |
| VERIF-04 | Phase 3 | Pending |
| VERIF-05 | Phase 3 | Pending |
| VERIF-06 | Phase 3 | Pending |
| VERIF-07 | Phase 3 | Pending |
| VERIF-08 | Phase 3 | Pending |
| VERIF-09 | Phase 3 | Pending |
| VERIF-10 | Phase 3 | Pending |
| HW-01 | Phase 4 | Pending |
| HW-02 | Phase 4 | Pending |
| HW-03 | Phase 4 | Pending |
| HW-04 | Phase 4 | Pending |
| HW-05 | Phase 4 | Pending |
| WIRE-01 | Phase 2 | Pending |
| WIRE-02 | Phase 2 | Pending |
| CLEAN-01 | Phase 2 | Pending |
| CLEAN-02 | Phase 2 | Pending |
| DOC-01 | Phase 5 | Pending |

**Coverage:**
- v1.1 requirements: 24 total (3 SAF + 10 VERIF + 5 HW + 2 WIRE + 2 CLEAN + 1 DOC = 23 + 1 = 24)
- Mapped to phases: 24
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-11*
*Last updated: 2026-05-11 — CLEAN-01/02 added (minipro reference cleanup); folded into Phase 2 Naming Cleanup*

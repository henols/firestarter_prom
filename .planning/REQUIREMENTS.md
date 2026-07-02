# Requirements: Firestarter — v1.20 Protocol-Only Dispatch (Remove the Legacy `mem_type` Axis)

**Defined:** 2026-07-02
**Core Value:** Algorithm-first dispatch — the minipro `protocol_id` (`algorithm`) is the single authoritative dispatch key end to end (XML → DB → wire JSON → firmware handler). v1.20 removes the last vestige that violates that contract: the `mem_type`/`type` backward-compat fallback axis. After v1.20 the firmware, wire, and host trust **only** the real protocol.

## v1 Requirements

Requirements for this milestone. Each maps to exactly one roadmap phase.

### Firmware (FW)

- [x] **FW-01**: When `protocol == 0`, `configure_memory()` fail-closes to `configure_not_implemented()` — the `mem_type` fallback dispatch chain (`memory.cpp` steps 7–11) is deleted so no path dispatches on `mem_type`.
- [x] **FW-02**: The `mem_type` field is removed from `firestarter_handle_t` and `json_parser.c` no longer extracts the `type` field.
- [x] **FW-03**: `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)` and the now-unused `TYPE_EPROM / TYPE_SRAM / TYPE_FLASH_TYPE_3 / TYPE_FLASH_TYPE_4` constants are retired from firmware headers/messages in lockstep.

### Wire Contract (WIRE)

- [x] **WIRE-01**: The `type` (mem_type) field is removed from the host→firmware JSON command contract; the wire carries only `algorithm` as the dispatch key. Breaking change vs hand-crafted JSON / pre-v1.20 hosts (documented).

### Host (HOST)

- [x] **HOST-01**: The host emits no `type` key in any serial command payload (the command-dict builder in `eprom_operations.py` / callers).
- [x] **HOST-02**: `database.py` drops `_ALGO_MEM_TYPE`, the derived `mem_type`, and the "Generic Flash (legacy fallback only)" substring default; `algorithm` is the sole dispatch datum carried to the wire.
- [ ] **HOST-03**: The `mem_type`-keyed legacy display-label fallbacks in `ic_layout.py` (and `eprom_info.py`) are removed; `info`/`list`/`search` derive labels from `electrical.type` / protocol only.
- [ ] **HOST-04**: A chip entry (built-in or user-override) lacking a usable `algorithm` is rejected with a clear error before any serial byte — no silent fallback dispatch.

### Docs & Migration (DOC)

- [ ] **DOC-01**: Firmware `CLAUDE.md` dispatch section (steps 7–11 removed), `firestarter/doc/PROTOCOLS.md`, and the JSON wire-field docs drop `type`/`mem_type`; the breaking change + the "every entry needs `algorithm`" requirement are recorded in the sub-repo READMEs / changelog.

### Non-Regression Gates (GATE / SAFE)

- [ ] **GATE-01**: v1.16 golden register traces + the dispatch-mirror guard stay green; `check_dispatch.py` reports 0 violations; `diff_db.py` shows no `chip_database.json` value change for real chips.
- [ ] **GATE-02**: Full native (`pio test -e native`) + host (`pytest`) suites pass with dual-repo constants parity; py3.11-target CI clean (ruff / ruff-format / mypy).
- [ ] **SAFE-01**: Over-voltage stays blocked; every currently-dispatchable DB chip still routes to the identical handler via `protocol` (regression-proving the removed fallback was dead for all real chips).

## v2 Requirements

Deferred to a future milestone. Tracked, not in this roadmap.

### Legacy Naming / Flags (LEGACY)

- **LEGACY-01**: Remove/retire `FLAG_VPE_AS_VPP (0x10)` if confirmed unused (the "legacy: direct VPE path" backward-compat flag).
- **LEGACY-02**: Rename the `EPROM_LEGACY` (0x0B) label and scrub remaining "legacy fallback" prose once the mem_type axis is gone.

## Out of Scope

Explicitly excluded from v1.20. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| `FLAG_VPE_AS_VPP (0x10)` removal | Operator chose the `mem_type` axis, not the broader vestige sweep — deferred to LEGACY-01. |
| `EPROM_LEGACY` / "legacy" naming cleanup | Naming, not the dispatch axis — deferred to LEGACY-02. |
| Canonical `electrical.type` *string* | The v1.16 classification field; unrelated to the numeric `mem_type` — must stay untouched. |
| Phantom protocol arms (0x35 / 0x39) | Fail-closed forward-compat dispatch, not legacy. |
| Named-infeasibility arms (0x11 / 0x2A–0x2C) | Fail-closed infeasible-on-RURP arms, not legacy. |
| Backward-compat fallback for pre-v1.20 hosts | Intentional breaking change — "only trust the real protocol." |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FW-01 | Phase 105 | Complete |
| FW-02 | Phase 105 | Complete |
| FW-03 | Phase 105 | Complete |
| WIRE-01 | Phase 105 | Complete |
| HOST-01 | Phase 106 | Complete |
| HOST-02 | Phase 106 | Complete |
| HOST-03 | Phase 106 | Pending |
| HOST-04 | Phase 106 | Pending |
| DOC-01 | Phase 107 | Pending |
| GATE-01 | Phase 107 | Pending |
| GATE-02 | Phase 107 | Pending |
| SAFE-01 | Phase 107 | Pending |

**Coverage:**

- v1 requirements: 12 total
- Mapped to phases: 12 (roadmap complete)
- Unmapped: 0 ✓

---
*Requirements defined: 2026-07-02*
*Last updated: 2026-07-02 after roadmap creation (Phases 105–107)*

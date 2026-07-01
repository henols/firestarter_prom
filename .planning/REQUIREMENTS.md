# Requirements: Firestarter — v1.19 Protocol Naming Labels

**Defined:** 2026-07-01
**Core Value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware handler; protocol numbers stay the dispatch key end to end. v1.19 adds a legibility layer on top of that unchanged contract: a single canonical, behavior/datasheet-correct, human-readable name set applied across firmware constants, host display, and docs — names never become the dispatch key.

## v1 Requirements

Requirements for this milestone. Each maps to exactly one roadmap phase (100–103).

### Naming (Phase 100 — authoritative name set + operator approval)

- [ ] **NAME-01**: A single canonical entry — a C-identifier-safe `PROTO_<NAME>` token + a short human display name + datasheet-cited behavioral facet prose (write algorithm / erase model / VPP behavior / pin roles) — exists for every protocol number present in `chip_database.json` (0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x34) and for the phantom IDs (0x35, 0x39, flagged non-real). Names use a chip-family/behavior axis (pin-count-primary; voltage/hazard detail lives in the facet prose), carrying forward the FM1608 (0x28) and X88C64 (0x34) identity corrections.
- [ ] **NAME-02**: The operator explicitly approves the canonical name set at a blocking gate — the draft table is presented for review and the 0x0E-vs-0x29 (both 32-pin SRAM) name collision is resolved at approval — before any downstream phase (101/102/103) begins. No silent auto-approval.
- [ ] **NAME-03**: The approved name set is recorded in one identifiable authoritative source — `firestarter/doc/PROTOCOLS.md`, revised in place — that Phases 101/102/103 each cite as their single source of truth, and it includes an operator-approved handler-family name layer for the many-to-one handlers (one EPROM handler for 0x07/0x08/0x0B; one SRAM handler for 0x0E/0x27/0x28/0x29; the single-protocol handlers) so downstream renames draw from this source rather than being invented mid-refactor.

### Firmware Labels (Phase 101 — apply names in firmware)

- [ ] **FW-01**: Firmware defines the `PROTO_<NAME>` constants for every protocol number with numeric values unchanged (the label *is* the number), so the dispatch site reads by name (`handle->protocol == PROTO_...`).
- [ ] **FW-02**: The raw-hex dispatch chain (`firestarter/src/proms/memory.cpp`) is relabeled to the named constants — including honest, explicitly-non-real phantom tokens for the 0x35/0x39 dispatch arm — preserving dispatch order and behavior.
- [ ] **FW-03**: The many-to-one handler files and functions are renamed from the approved family-name layer (`configure_flash3`/`flash_type_3.cpp`, `configure_flash4`/`flash_type_4.cpp`, `configure_eeprom28c`, …).

### Host Display (Phase 102 — apply names in the host CLI)

- [ ] **HOST-01**: The divergent host protocol vocabularies (`ic_layout.proto_display` and `protocol_info_data`) are consolidated onto the canonical display names from the authoritative source, so `firestarter info` / `list` / `search` render one consistent name per protocol.

### Docs (Phase 103 — reconcile prose + divergence record)

- [ ] **DOC-01**: `firestarter/doc/PROTOCOLS.md` prose (the §1 four-facet bucket descriptions) and the INV-01..09 native-test traceability matrix are reconciled to the new names/tokens, with no dangling references to the old minipro-heritage jargon.
- [ ] **DOC-02**: The name↔`datasheets/<hex>-<NAME>/` slug divergence is explicitly recorded (the frozen slug column retained alongside the new name so old-slug vs new-name is visible at a glance); the `datasheets/` folder slugs are NOT renamed.

### Non-Regression Gates (cross-cutting — verified in every phase that touches its surface)

- [ ] **GATE-01**: Protocol numbers remain the dispatch key end to end; no name/token becomes a dispatch or lookup key, and algorithm-first dispatch behavior is unchanged (firmware golden register traces + dispatch-mirror guard stay green).
- [ ] **GATE-02**: No `chip_database.json` content change and no wire / lockstep-constant *value* change — only C-token *names* change in firmware, not their numeric values; `diff_db.py` shows identity, `check_dispatch.py` passes, and the constants-parity test holds.
- [ ] **GATE-03**: CLI grammar is unchanged — chip selection stays by part number; no protocol name/alias is accepted as CLI input.

## Future Requirements

Deferred to a future milestone. Tracked but not in this roadmap.

### Naming (deferred)

- **NAME-F1**: Rename the `datasheets/<hex>-<NAME>/` folder slugs to match the new vocabulary (deferred to avoid folder/provenance churn; only on explicit operator instruction).
- **NAME-F2**: Accept a protocol name/alias as CLI input (filter/select by protocol name). Chip selection stays by part number for v1.19 (GATE-03).

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Canonical naming of the infeasible buckets 0x11/0x2A/0x2B/0x2C | Not present in `chip_database.json`, so outside NAME-01 scope; Phase 101 may reuse the §2.2 "honest non-protocols" labels if it needs constants for that dispatch arm. |
| Splitting the many-to-one handlers (one-handler-per-protocol) | Architectural restructure; the family layer names the existing groupings, it does not split them. |
| Any `chip_database.json` value change / new chip becoming programmable | v1.19 is a naming/legibility layer only — no capability or DB-value change (GATE-02). |
| Changing protocol numbers or wire/lockstep-constant values | Numbers stay the authoritative dispatch key (GATE-01); only token *names* change. |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| NAME-01 | Phase 100 | Pending |
| NAME-02 | Phase 100 | Pending |
| NAME-03 | Phase 100 | Pending |
| FW-01 | Phase 101 | Pending |
| FW-02 | Phase 101 | Pending |
| FW-03 | Phase 101 | Pending |
| HOST-01 | Phase 102 | Pending |
| DOC-01 | Phase 103 | Pending |
| DOC-02 | Phase 103 | Pending |
| GATE-01 | Phases 101–103 | Pending |
| GATE-02 | Phases 101–103 | Pending |
| GATE-03 | Phases 101–103 | Pending |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0 ✓

---
*Requirements defined: 2026-07-01*
*Last updated: 2026-07-01 after initial definition*

# Requirements: Firestarter — v1.16 Protocol-First Architecture Rebuild

**Defined:** 2026-06-25
**Core Value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware handler, no guessing. v1.16 makes that contract **legible** (named, datasheet-documented protocols) and **leaner** (shared-primitive handlers), with the minipro DB still ground truth.

> **Scope decisions (operator, 2026-06-25):**
> - **Flash outcome = best-effort, measured.** Per-step `pio run -e leonardo` measurement + net-non-increase gate; report achieved %; no hard floor (the ~85–86.5% figure is a pre-LTO estimate).
> - **Two decode corrections in scope** (FM1608 0x40→0x28 reconciliation + 0x34 X88C64 `electrical.type` UV-EPROM→EEPROM, host-only DB fix).
> - **Pure behavior-preserving refactor.** Open defects W29C040/flash4 (CR-01) and AM27C020/0x08 (FUT-06) are preserved exactly as-is — NOT fixed this milestone. Firmware-only; NO dual-repo lockstep unless a behavior fix rides along (none planned).

## Milestone v1.16 Requirements

Requirements for this milestone. Each maps to exactly one roadmap phase. Phase numbering continues at **Phase 85**.

### Datasheet Acquisition

- [x] **DSHEET-01**: Operator/maintainer can find a committed datasheet PDF for each of the 11 on-hand ICs (W27C512, W27E512, SST27SF512, W27E040, SST39SF040, W29C020, W29C040, FM1608, ST M27C512, AM27C020, 2516) under a new top-level `datasheets/` folder.
- [x] **DSHEET-02**: Every no-silicon protocol bucket (0x0D, 0x0E, 0x10, 0x27, 0x29, 0x34) has at least one representative datasheet committed, so every protocol has a verification source.
- [ ] **DSHEET-03**: `datasheets/README.md` indexes hex id ↔ proposed name ↔ handler ↔ datasheet ↔ on-hand status, documents the phantom (0x35/0x39) and infeasible (0x11/0x2A/0x2B/0x2C) bucket exclusions, and annotates provenance for hard-to-source/generic parts (the 2516 representative, discontinued FM1608/AM27C020/X88C64).

### Naming + Documentation Vocabulary

- [ ] **NAME-01**: Every `protocol_id` present in `chip_database.json` has an authored human-readable name on the algorithm axis plus its datasheet-verified behavior (write algorithm, erase model, VPP behavior, pin roles).
- [ ] **NAME-02**: Each firmware handler's *why* (the rationale for its current behavior) is documented and traceable to a datasheet.
- [ ] **NAME-03**: The accreted per-handler one-off fixes are enumerated as named behavior-contract invariants (0x0B direct-VPE rail, 0x0B shared OE/VPP read-skip, 0x08 P1-as-VPP, flash4 256B page boundary, VPP-skip-on-read, pulse-delay defaults, FM1608 SRAM→FRAM, WARNING-5 0x07→0x0D override, SST39SF040 keep-Flash/EEPROM).
- [ ] **NAME-04**: The two in-scope decode corrections are applied — FM1608 0x40→0x28 reconciliation (memory/doc) and 0x34 X88C64 `electrical.type` UV-EPROM→EEPROM (host DB) — and phantom/infeasible buckets are explicitly named as honest non-protocols.
- [ ] **NAME-05**: The naming pass leaves the firmware dispatch structure and all wire/control values unchanged (`diff_db.py` shows only the enumerated NAME-04 corrections; near-zero Leonardo flash delta).

### Primitive Decomposition / Refactor

- [ ] **PRIM-01**: Before any extraction, per-family golden register traces (capture-before oracle) are pinned and a `check_dispatch.py::dispatch()`-matches-documented-order test exists.
- [ ] **PRIM-02**: The shared SDP/const-table duplication (P7 warm-up) is deduplicated, with handler behavior unchanged under the native suites.
- [ ] **PRIM-03**: The shared chip-ID compare/report logic (P4) is extracted into a primitive, split from the protocol-specific read mechanism.
- [ ] **PRIM-04**: The shared VPP-gate logic (P3) is extracted into a primitive keyed on `handle->protocol` (never `electrical.type`), with regulator-routing bits parameterized per protocol.
- [ ] **PRIM-05**: The shared poll/readback verify logic (P5) is extracted into a primitive, leaving the per-protocol outer retry/page/erase algorithms intact.
- [ ] **PRIM-06**: Leonardo flash is measured (`pio run -e leonardo`) at every recompose step with a net-non-increase gate, and the achieved final flash % is reported.

### Per-Protocol Bench Validation + Ledger

- [ ] **LEDGER-01**: A new `PROTOCOL-LEDGER.{md,json}` records a per-protocol row (proposed name, datasheet citation, primitives used, verification status) and composes with — does not replace — the v1.13 `validation_matrix_spec.json` (by family) and v1.15 `EVIDENCE.json` (by chip+sha).
- [ ] **LEDGER-02**: Each protocol with on-hand silicon is bench-validated on Leonardo + RURP Rev 2.0; a PASS row structurally requires `oracle: leonardo+Rev2.0` plus non-empty evidence references.
- [ ] **LEDGER-03**: The 6 no-silicon buckets (0x0D, 0x0E, 0x10, 0x27, 0x29, 0x34) are recorded as explicit `UNVERIFIED`, and the open-defect rows (W29C040 CR-01, AM27C020 FUT-06, 2516 FUT-03) are carried at their current documented status (not silently changed).

### Cross-Cutting Safety / Invariants

- [ ] **SAFE-01**: Every extracted primitive keys behavior on `handle->protocol`, never on `electrical.type`; the `novpp_in_eprom` / `eeprom28c_in_eprom` (WARNING-5) structural guards are preserved.
- [ ] **SAFE-02**: All enumerated one-off-fix invariants (NAME-03) survive each recompose step, asserted under the native register-level tests.
- [ ] **SAFE-03**: `check_dispatch.py` (0 violations) and `diff_db.py` exit clean every phase; `diff_db.py` shows only the intentional NAME-04 corrections (baseline re-pinned for those, enumerated) and is empty across all recompose phases.
- [ ] **SAFE-04**: Over-voltage stays blocked at the firmware VPP check; the `chip_resolver.resolve_chip` host guard is never bypassed; no irreplaceable UV part is written on an unstable read path (the 2516 stays `UNVERIFIED`, not spent).
- [x] **SAFE-05**: No new third-party dependency is introduced — the existing harness (`check_dispatch.py`, `diff_db.py`, native `test_val_*` suites, `dev validate-family`, `write_test.sh`, `gen_test_image.py`, host ruff/mypy/pytest) is reused; the only new artifact is `datasheets/`. *(Phase 85-01: branch + check script only; verified via explicit git add + SAFE-05-OK gate)*
- [ ] **SAFE-06**: The refactor ships firmware-first with NO dual-repo lockstep (wire/constant values unchanged, NAME-04 is host-only); ruff/format/mypy/codegen are validated against the CI target (py3.11), not the 3.12 devcontainer, and generated `messages.py` is never hand-normalized.

## Future Requirements

Acknowledged but deferred — not in this milestone's roadmap.

### Open-Defect Fixes (preserved-as-is this milestone)

- **FUT-CR01**: Fix W29C040 flash4 256B page-0 write fault (reopen Phase-74 Wave-2; likely dual-repo lockstep firmware fix).
- **FUT-06**: Fix AM27C020 0x08 32-pin Large-EPROM write/VPP path (0-bits-programmed).
- **FUT-03**: Root-cause the 2516 0x0B read instability (shared OE/VPP), then bench-prove write (closes v1.14 FUT-03 NMOS write+SHA).

### Bench Validation of No-Silicon Buckets

- **CHIP-NEEDED**: Bench-confirm the 6 currently-UNVERIFIED buckets (0x0D, 0x0E, 0x10, 0x27, 0x29, 0x34) once representative silicon is acquired (0x34/X88C64 also PCB-blocked, FUT-01).

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Replacing the minipro/infoic DB as ground truth | Locked decision — datasheets verify interpretation; they do not replace the DB. |
| Fixing the open defects CR-01 / FUT-06 / FUT-03 | Operator chose a pure behavior-preserving refactor; these are preserved as-is and tracked as Future Requirements. |
| Implementing the 0x34 X88C64 programming handler | PCB-blocked ALE routing (v1.14 FUT-01); v1.16 only corrects its `electrical.type` decode + documents it `UNVERIFIED`. |
| New protocol handlers / newly-programmable chips | v1.16 renames, documents, and decomposes existing protocols — it adds no new programming capability. |
| Datasheets/folders for phantom (0x35/0x39) or infeasible (0x11/0x2A/0x2B/0x2C) buckets | Honest non-protocols — documented as exclusions in `datasheets/README.md`, no acquisition. |
| A hard flash-% exit gate | Operator chose best-effort measured shrink; post-LTO realized savings are uncertain, so the gate is net-non-increase + report, not a fixed floor. |
| Dual-repo lockstep wire changes | The refactor preserves wire/constant values; no lockstep unless a (currently unplanned) behavior fix rides along. |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DSHEET-01 | Phase 85 | Complete |
| DSHEET-02 | Phase 85 | Complete |
| DSHEET-03 | Phase 85 | Pending |
| NAME-01 | Phase 86 | Pending |
| NAME-02 | Phase 86 | Pending |
| NAME-03 | Phase 86 | Pending |
| NAME-04 | Phase 86 | Pending |
| NAME-05 | Phase 86 | Pending |
| PRIM-01 | Phase 87 | Pending |
| PRIM-02 | Phase 88 | Pending |
| PRIM-03 | Phase 88 | Pending |
| PRIM-04 | Phase 88 | Pending |
| PRIM-05 | Phase 88 | Pending |
| PRIM-06 | Phase 88 | Pending |
| LEDGER-01 | Phase 89 | Pending |
| LEDGER-02 | Phase 89 | Pending |
| LEDGER-03 | Phase 89 | Pending |
| SAFE-01 | Phase 87 (recurring in 88) | Pending |
| SAFE-02 | Phase 87 (recurring in 88) | Pending |
| SAFE-03 | Phase 86 (recurring in 87/88/89) | Pending |
| SAFE-04 | Phase 87 (recurring in 88/89) | Pending |
| SAFE-05 | Phase 85 | Complete (85-01) |
| SAFE-06 | Phase 86 | Pending |

**Coverage:**

- Milestone v1.16 requirements: 23 total
- Mapped to phases: 23 ✓
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-25*
*Last updated: 2026-06-25 after initial v1.16 definition*

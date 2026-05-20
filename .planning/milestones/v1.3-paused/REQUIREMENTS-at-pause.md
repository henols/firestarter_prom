# Milestone v1.3 — CMOS EPROM Family Hardware Validation

**Created:** 2026-05-19
**Goal:** Bench-validate, on real silicon and on both Uno + Leonardo, that the algorithm-0x07 (28-pin DIP CMOS UV-EPROM) + algorithm-0x08 (32-pin DIP CMOS UV-EPROM) dispatch logic shipped in v1.0–v1.2 actually programs, reads back, and verifies cleanly across the full density range of the named chip families.

**Core constraint:** This is **validation, not new features**. The protocol-aware architecture, safety stack, and logging infrastructure are locked. Any code change discovered to be necessary opens a *defect requirement* (not a feature requirement) and is scoped narrowly.

## v1.3 Requirements

### BENCH — Chip-on-bench end-to-end validation

End-to-end cycle per chip on each board: chip-ID read (where applicable), blank-check, full-image write, full-image read-back, byte-for-byte verify, post-cycle blank-check (where electrically erasable). Test image: a deterministic pattern that exercises every address bit + every data bit (e.g. address-walking + data-walking + alternating 0x55/0xAA + random with fixed seed). Operator captures green/red verdict + any anomalies (timing, chip-ID mismatches, partial writes) for the BENCH-RESULTS artifact (DOC-01).

- [ ] **BENCH-01**: W27C512 (28-pin, algo 0x07, 64K) — full write/read/verify cycle on Uno + Leonardo. Closes deferred Phase 08 SC#2/SC#3 + Phase 09 Plan-05 Task 3.
- [ ] **BENCH-02**: SST27SF512 (28-pin, algo 0x07, 64K) — full write/read/verify cycle on Uno + Leonardo.
- [ ] **BENCH-03**: W27C020 (32-pin, algo 0x08, 256K) — full write/read/verify cycle on Uno + Leonardo.
- [ ] **BENCH-04**: W27E040 (32-pin, algo 0x08, 512K) — full write/read/verify cycle on Uno + Leonardo.
- [ ] **BENCH-05**: 28-pin lower-density representative — W27C257 OR W27E257 OR SST27SF256 (algo 0x07, 32K) — full cycle on Uno + Leonardo. Covers address-bus low end for algo 0x07.
- [ ] **BENCH-06**: 32-pin lower-density representative — W27C010 OR W27E010 OR W27L010 OR SST27SF010 (algo 0x08, 128K) — full cycle on Uno + Leonardo. Covers address-bus low end for algo 0x08.

### PROTO — Protocol correctness gates measurable on bench

These are not new code paths — they verify existing firmware behavior is correct when observed on real hardware with chips fitted.

- [ ] **PROTO-01**: For every chip in BENCH-01..06 where `chip_id_check: true` in `chip_database.json`, the chip-ID read returns the DB-declared `chip_id_value`. Mismatches blocked by safety stack (must not write).
- [ ] **PROTO-02**: VPP regulator engages at 12V ±5% (scope-measured at the chip socket VPP pin) during write/erase phases for both algo 0x07 and algo 0x08; idles at VCC or off between operations.

### COVERAGE — Structural coverage report (desk-side, no chip needed)

- [x] **COV-01**: Generate a coverage matrix from `chip_database.json` enumerating every algo-0x07 + algo-0x08 row with: manufacturer, part_number(s), pin_count, size_bytes, pulse_duration, chip_id_check, chip_id_value, pinout class. Output: `.planning/v1.3-COVERAGE-MATRIX.md` (or equivalent). 339 chips covered.
- [x] **COV-02**: From the matrix, identify any DB inconsistencies inside each algorithm: chips that share `pin_count` + `algorithm` but differ in `pulse_duration`, `chip_id_check`, or `pinout`. Each inconsistency is flagged as a defect candidate (not auto-fixed in v1.3 — fixes go to v1.4 or sub-repo PRs).

### DOC — Artifacts + close-out

- [ ] **DOC-01**: `.planning/v1.3-BENCH-RESULTS.md` — per-chip, per-board green/red/quirks table covering BENCH-01..06 + PROTO-01..02 observations. Include serial-log snippets where verbose-mode INFO or SERIAL_DEBUG breadcrumbs were captured. Photo/scope evidence linked where available.
- [ ] **DOC-02**: Milestone close — update `MILESTONES.md`, archive v1.3 phase directories to `.planning/milestones/v1.3-phases/`, write the v1.3 milestone summary.

## Future Requirements (deferred past v1.3)

- New algorithms / new chip families (algo 0x05, 0x0B, 0x10 hardware validation, etc.) — separate milestones.
- Automated regression harness that re-runs the v1.3 bench matrix on every firmware bump — promising but requires bench fixturing infrastructure. Capture as v1.4+ candidate.
- DB inconsistency fixes flagged by COV-02 — addressed in a follow-up milestone or as targeted sub-repo PRs.

## Out of Scope (explicit exclusions for v1.3)

- **New code architecture** — Algorithm dispatch, safety stack, logging, codegen pipeline all locked. v1.3 is read-only against firmware semantics.
- **FM1608 byte-0 read bug (v1.1 carryover)** — Different chip family (SRAM, algo 0x07/0x28), different debug session, parked on hardware (needs a different Uno R3 board). Out of v1.3 scope; remains in STATE.md "Carried Over From v1.1".
- **Flash-savings work** — v1.2 Leonardo Flash budget (85.4% / 24,482 B) is the ship-state floor; v1.3 must not regress flash usage.
- **WARNING-4** (`firestarter_test.sh` / `write_test.sh` reference deleted `database_generated.json`) — Test-script drift, not algorithm validation. Defer to v1.4 housekeeping unless touched naturally.
- **Algo 0x05 / 0x06 / 0x0B / 0x0D / 0x10 hardware validation** — Different algorithms, different families. v1.3 fences itself to algo 0x07 + 0x08 only.
- **PLCC / SOIC / SOP adapters** — RURP shield ships DIP only.

## Traceability

Each requirement maps to exactly one phase. Coverage: 12/12 ✓.

| REQ-ID | Phase | Plan(s) | Status |
|--------|-------|---------|--------|
| BENCH-01 | Phase 12 | TBD | Not started |
| BENCH-02 | Phase 12 | TBD | Not started |
| BENCH-03 | Phase 13 | TBD | Not started |
| BENCH-04 | Phase 13 | TBD | Not started |
| BENCH-05 | Phase 12 | TBD | Not started |
| BENCH-06 | Phase 13 | TBD | Not started |
| PROTO-01 | Phase 12 (observation protocol carried forward into Phase 13) | TBD | Not started |
| PROTO-02 | Phase 12 (observation protocol carried forward into Phase 13) | TBD | Not started |
| COV-01 | Phase 11 | Plans 11-01..11-06 | ✅ Complete (Wave 0 RED + Wave 1 §1+§2 + Wave 2 §3 + Wave 3 §4 + Wave 4 §5 + Wave 5 D-07 reconciliation all landed 2026-05-19; matrix + ledger committed; 339 chips covered) |
| COV-02 | Phase 11 | Plans 11-01, 11-04 | ✅ Complete (Wave 3 §4 + ledger committed 2026-05-19; HAZARD=1, CORRECTNESS=27, VARIANCE=49 findings flagged in `.planning/v1.3-COVERAGE-MATRIX.md` + `.planning/v1.3-defect-coverage-ids.json`) |
| DOC-01 | Phase 14 | TBD | Not started |
| DOC-02 | Phase 14 | TBD | Not started |

**Coverage target:** 12 requirements, 100% mapped to phases. ✓

---

*Last updated: 2026-05-19 — traceability table populated by `gsd-roadmapper` at ROADMAP.md creation. All 12 requirements mapped to phases 11–14. Bench-gated work (Phases 12 + 13) isolated from desk-side work (Phase 11) and paperwork (Phase 14) so progress is possible without continuous hardware access.*

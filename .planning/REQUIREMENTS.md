# Requirements: Firestarter — v1.16 Protocol-First Architecture Rebuild

**Defined:** 2026-06-25
**Core Value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware handler, no guessing. v1.16 makes that contract **legible** (named, datasheet-documented protocols) and **leaner** (shared-primitive handlers), with the minipro DB still ground truth.

> **Scope decisions (operator, 2026-06-25):**
> - **Flash outcome = best-effort, measured.** Per-step `pio run -e leonardo` measurement + net-non-increase gate; report achieved %; no hard floor (the ~85–86.5% figure is a pre-LTO estimate).
> - **Pure behavior-preserving refactor** applies to the *firmware recompose* phases (88–89): open defects W29C040/flash4 (CR-01) and AM27C020/0x08 (FUT-06) are preserved exactly as-is — NOT fixed this milestone.
>
> **Scope AMENDMENT (operator, 2026-06-25 — supersedes "two decode corrections + DB-frozen"):**
> - A new **Phase 86 (infoic.xml Variant-Field Decode + Correct DB Regen)** was inserted ahead of the naming pass. `infoic.xml`'s `variant` field carries untapped signal (FM1608 = `type=4/proto=0x07/variant=0x4126`; X88C64 = `type=1/proto=0x34/variant=0x3100/flags=0x00414200`, `flags&0x10==0`). Phase 86 decodes `variant` in full, regenerates a **correct** DB from principled decode, and **deletes** the hand-maintained `build_db.py` Rule 1/2/3 override edge-cases.
> - This **lifts the DB-frozen / "two decode corrections only" constraint for Phase 86**: the regenerated DB has a real (but fully-explained) `diff_db.py` diff and a re-pinned baseline. The two original NAME-04 corrections (FM1608, X88C64) now fall out of the variant decode structurally. The recompose phases (88–89) remain DB-frozen against the new baseline.
> - **Still host-only / NO dual-repo lockstep.** Phase 86 changes `firestarter_app` only (`build_db.py` + regenerated `chip_database.json`); the firmware recompose is a separate later phase. They never share a commit pair.
> - **Safety:** deleting the WARNING-5 override is gated by `check_dispatch.py` 0-violations (the structural 12V-on-no-VPP-pin guard) — the safety guarantee is *proven preserved by the structural gate*, not by the deleted special-case.

## Milestone v1.16 Requirements

Requirements for this milestone. Each maps to exactly one roadmap phase. Phase numbering continues at **Phase 85**.

### Datasheet Acquisition

- [x] **DSHEET-01**: Operator/maintainer can find a committed datasheet PDF for each of the 12 on-hand ICs (W27C512, W27E512, SST27SF512, W27E040, SST39SF040, W29C020, W29C040, FM1608, ST M27C512, AM27C020, 2516, W27C020) under a new top-level `datasheets/` folder. *(W27C020 added post-verification 2026-06-25 — operator-confirmed on-hand; exact Winbond leaf in 0x08-EPROM-QUICK.)*
- [x] **DSHEET-02**: Every no-silicon protocol bucket (0x0D, 0x0E, 0x10, 0x27, 0x29, 0x34) has at least one representative datasheet committed, so every protocol has a verification source.
- [x] **DSHEET-03**: `datasheets/README.md` indexes hex id ↔ proposed name ↔ handler ↔ datasheet ↔ on-hand status, documents the phantom (0x35/0x39) and infeasible (0x11/0x2A/0x2B/0x2C) bucket exclusions, and annotates provenance for hard-to-source/generic parts (the 2516 representative, discontinued FM1608/AM27C020/X88C64).

### infoic.xml Variant Decode + Correct DB *(Phase 86 — added by 2026-06-25 scope amendment)*

- [ ] **VAR-01**: The `infoic.xml` `variant` field is decoded in full — the low byte (`variant & 0xFF`, the pinout-family discriminator already consumed) AND the previously-undecoded high byte — with every value that affects chip classification documented and grounded in minipro source (`database.c`) and/or a committed datasheet. Datasheets are acquired as needed to resolve high-byte ambiguity; any value no source resolves is recorded as an honest documented gap, never guessed.
- [x] **VAR-02**: `build_db.py` derives `electrical.type`, `algorithm`, and `pinout` from principled variant-driven decode, and the hand-maintained Rule 1 (28C-EEPROM force-0x0D), Rule 2 (WARNING-5 5V-EEPROM-on-EPROM-pinout flip), and Rule 3 (type=4 FRAM/SRAM → 0x28) override blocks are **removed**. — ✅ 86-02 (single classify(); firestarter_app@cab9349)
- [x] **VAR-03**: The regenerated `chip_database.json` resolves FM1608 → SRAM_STD (0x28) and X88C64 → `electrical.type` EEPROM via the general decode (no special-case); every changed record vs. the pinned baseline is explained by a cited variant-decode rule (`diff_db.py` classified-diff, v1.11 GATE-02 pattern), and the `chip_database.baseline.json` + `dispatch_baseline.json` baselines are re-pinned to the new correct DB. — ✅ COMPLETE (decode 86-02 + supplement 86-04 + baseline re-pin 86-03 2026-06-25): both baselines re-pinned to the 746-chip correct DB (chip_database.baseline.json byte-identical; dispatch_baseline.json regenerated w/ Phase-86/SHA-a8efaedc/VAR-05 provenance); diff_db.py now an IDENTITY diff (0 changed, exit 0, D-07 closed). firestarter_app@dd541f6.
- [x] **VAR-04**: `check_dispatch.py` exits 0 violations on the regenerated DB (no chip routes to a 12V-VPP path on a no-VPP pinout — the structural backstop replacing the deleted WARNING-5 override), and the 11 on-hand bench-proven chips (v1.15 EVIDENCE) keep their `algorithm`/`vpp_mv`/`pinout` wire values OR any moved value is flagged for Leonardo + RURP Rev 2.0 re-bench before Phase 90. — ✅ COMPLETE (86-02 EVIDENCE-stable + 86-03 gate 2026-06-25): check_dispatch.py 0 dispatch regressions / 0 consistency violations against the re-pinned 746-chip DB; EVIDENCE-11 wire-stable (0 chips moved, no re-bench flag); full py3.11 toolchain green (686 tests / 77.69% cov / ruff / format / mypy-watermark). firestarter_app@dd541f6.
- [x] **VAR-05**: Chips physically supportable by Firestarter but **absent from upstream `infoic.xml`** — the 24-pin oddballs **2516** and **2532** (non-JEDEC pinouts; 2532 differs from 2732) — are shipped first-class in `chip_database.json` via a **curated, provenance-cited non-upstream supplement** merged by `build_db.py` *after* the `infoic.xml` decode (e.g. `tools/extra_chips.json`), NOT via per-operator `~/.firestarter/database.json` edits. Supplement records are clearly fenced as non-upstream, each field cites a datasheet, they pass `check_dispatch.py` (0 violations), and `diff_db.py` explains them as cited "non-upstream supplement" rows against the re-pinned baseline. **2516 retains its SAFE-04 UNVERIFIED status** (unstable read path — supported/resolvable but not graduated to a write-proven part; its host guards/wire values are not silently moved). *(Added by 2026-06-25 operator directive — support these oddballs even though upstream omits them.)* — ✅ COMPLETE (Phase 86-04, 2026-06-25): tools/extra_chips.json (2516+2532, source=non-upstream-supplement + datasheet cite each); build_db.py post-decode merge (744→746); DIP24_2532 non-JEDEC pinout; diff_db EXTRA_CHIPS_SUPPLEMENT rule (exit 0); check_dispatch 0 violations; 2516 UNVERIFIED (verification_status field) + wire-stable. diff_db rows currently explained vs OLD baseline; baseline re-pin is 86-03.

### Naming + Documentation Vocabulary

- [ ] **NAME-01**: Every `protocol_id` present in `chip_database.json` has an authored human-readable name on the algorithm axis plus its datasheet-verified behavior (write algorithm, erase model, VPP behavior, pin roles).
- [ ] **NAME-02**: Each firmware handler's *why* (the rationale for its current behavior) is documented and traceable to a datasheet.
- [ ] **NAME-03**: The accreted per-handler one-off fixes are enumerated as named behavior-contract invariants, each mapped to an existing native-test assertion (traceability matrix) with minimal new tests only where a cell is empty. The enumeration has **9** items (the roadmap's "8" is a stale label): 0x0B direct-VPE rail, 0x0B shared OE/VPP read-skip, 0x08 P1-as-VPP, flash4 256B page boundary, VPP-skip-on-read, pulse-delay defaults, FM1608 SRAM→FRAM, WARNING-5 0x07→0x0D override, SST39SF040 keep-Flash/EEPROM. *(Note: the WARNING-5 and FM1608→FRAM behaviors are now achieved by Phase 86's variant decode rather than a build_db override, but they remain documented invariants the firmware/decode must preserve.)*
- [ ] **NAME-04**: The corrected FM1608 (SRAM_STD / 0x28) and X88C64 (`electrical.type` EEPROM) classifications — now delivered structurally by the Phase 86 variant decode (VAR-03), not as host special-cases — are **documented** in the vocabulary with their true `infoic.xml` identity tuple (type/proto/variant); the historical "FM1608 0x40" framing is recorded as a decimal-40 ↔ hex-0x28 conflation. Phantom (0x35/0x39) and infeasible (0x11/0x2A/0x2B/0x2C) buckets are explicitly named as honest non-protocols.
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
- [ ] **SAFE-03**: `check_dispatch.py` exits 0 violations every phase. `diff_db.py`: in **Phase 86** it shows the variant-decode diff with **every row explained by a cited decode rule**, after which the baseline is re-pinned (VAR-03); in the **naming pass (87) and the recompose phases (88–89)** `diff_db.py` is **empty** against that re-pinned baseline.
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
| DSHEET-03 | Phase 85 | Complete |
| VAR-01 | Phase 86 | In Progress (86-01: decode documented in full — DECODE-NOTES.md, pinned SHA a8efaedc, honest gaps; classifier application is 86-02) |
| VAR-02 | Phase 86 | Complete (86-02) |
| VAR-03 | Phase 86 | Complete (86-02 decode + 86-04 supplement + 86-03 baseline re-pin; diff_db IDENTITY exit 0) |
| VAR-04 | Phase 86 | Complete (86-02 EVIDENCE-stable + 86-03 gate; check_dispatch 0 violations, full py3.11 gate green) |
| VAR-05 | Phase 86 | Complete (86-04) |
| NAME-01 | Phase 87 | Pending |
| NAME-02 | Phase 87 | Pending |
| NAME-03 | Phase 87 | Pending |
| NAME-04 | Phase 87 | Pending |
| NAME-05 | Phase 87 | Pending |
| PRIM-01 | Phase 88 | Pending |
| PRIM-02 | Phase 89 | Pending |
| PRIM-03 | Phase 89 | Pending |
| PRIM-04 | Phase 89 | Pending |
| PRIM-05 | Phase 89 | Pending |
| PRIM-06 | Phase 89 | Pending |
| LEDGER-01 | Phase 90 | Pending |
| LEDGER-02 | Phase 90 | Pending |
| LEDGER-03 | Phase 90 | Pending |
| SAFE-01 | Phase 88 (recurring in 89) | Pending |
| SAFE-02 | Phase 88 (recurring in 89) | Pending |
| SAFE-03 | Phase 86 (recurring in 87/88/89) | Pending |
| SAFE-04 | Phase 86 (recurring in 88/89/90) | Pending |
| SAFE-05 | Phase 85 | Complete (85-01) |
| SAFE-06 | Phase 87 | Pending |

**Coverage:**

- Milestone v1.16 requirements: 27 total (23 original + 4 VAR added by 2026-06-25 scope amendment)
- Mapped to phases: 27 ✓
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-25*
*Last updated: 2026-06-25 after initial v1.16 definition*

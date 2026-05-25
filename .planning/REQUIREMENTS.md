# Requirements — Milestone v1.7: RURP Shield Hardware Investigation & Version Detection

**Status:** Active — defined 2026-05-22 at milestone start; phase mappings locked 2026-05-22.
**Milestone goal:** Produce a versioned, authoritative reference for every known RURP shield revision (silkscreen text, electrical/mechanical schematic, label-to-code-alias map, per-rev capabilities matrix, inter-rev difference table) and design the next-rev shield-version-detect resistor + firmware ADC read so future hardware-touch work is grounded in known-good shield schematics rather than ask-the-operator memory.

**Source upstream:** `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer/tree/main/hardware` (current revs on `main`; older revs Rev 0 + Rev 1 mined from git history).

**Why now:** v1.6 Wave B FAIL on Phase 29 burned two bench attempts on chip-swap diagnostics to disambiguate chip-state from board/shield/firmware. Memory `user_shield_revisions` notes the EEPROM `hw_revision` byte can't distinguish operator's Rev 2.2 / Rev 2.0 / Modified Rev 0. v1.7 closes that ask-the-operator loop and gives v1.6 Phase 27 RCA re-open a labeled-schematic substrate to design instrumented A/B builds.

## v1.7 Requirements

### Hardware Inventory (HW-INV)

- [x] **HW-INV-01**: Every RURP shield revision ever published in upstream `AndersBNielsen/Relatively-Universal-ROM-Programmer` (current revs on `main` + older revs Rev 0 / Rev 1 recoverable via `git log -p` / `git log --diff-filter=D`) is identified with a unique revision identifier matching its silkscreen-version string
- [x] **HW-INV-02**: Each identified revision is recorded in `.planning/v1.7-SHIELD-REVS.md` with: silkscreen-version string, upstream commit/tag that introduced it, schematic file reference (path in upstream repo), date introduced (from commit history)
- [x] **HW-INV-03**: Operator's three on-hand boards (Rev 2.2, Rev 2.0, modified Rev 0) are photographed (top + bottom views, sufficient resolution to read silkscreen) and the photos archived under `.planning/v1.7/photos/<rev>/`; any operator-side rework hacks (e.g. the Modified Rev 0 hardware-bug-A/B mod) are annotated in the photo or accompanying note

### Silkscreen Capture (SILK)

- [x] **SILK-01**: For each identified shield revision, the exact silkscreen-version string is captured verbatim (e.g. `RURP Rev 2.2`, `RURP v2.0`, `RURP Rev 0` — whatever the silkscreen actually says) and stored as the canonical revision identifier in `.planning/v1.7-SHIELD-REVS.md`

### Inter-Rev Differences (DIFF)

- [x] **DIFF-01**: An inter-rev electrical difference table is captured in `.planning/v1.7-SHIELD-REVS.md` covering at minimum: Arduino pin mapping (Dx/Ax → RURP signal), VPP regulator wiring (input pin, output pin, enable pin, feedback divider), voltage divider values (R1/R2 from `rurp_configuration_t`), control-line routing (CE/WE/OE per algorithm), jumper/strap positions
- [x] **DIFF-02**: Inter-rev mechanical differences are captured: board outline / mounting holes, ZIF socket presence + orientation, header positions, any notable component changes (DIP package vs SMD, regulator family, etc.). Differences that have no electrical impact are noted but not gated.

### Per-Rev Capabilities (CAPS)

- [x] **CAPS-01**: A per-rev capability matrix in `.planning/v1.7-SHIELD-REVS.md` declares for each revision: chip families supported (28-pin DIP UV-EPROM, 32-pin DIP UV-EPROM, parallel EEPROM, AMD-style flash, Intel flash, SRAM), max VPP, max VCC, address-bus width, supported firmware algorithms (0x05/0x06/0x07/0x08/0x0B/0x0D/0x0E/0x10/0x27/0x28/0x29 — subset per rev)
- [x] **CAPS-02**: Capability matrix is cross-checked against firmware code (`firestarter/src/algorithm_*.cpp`) — if a rev physically cannot support an algorithm (e.g. missing VPP regulator on Rev 0), that fact is documented and a firmware-side runtime guard is proposed (out-of-scope to implement in v1.7; recorded as a follow-up todo)

### Label → Code Alias Migration (ALIAS)

- [x] **ALIAS-01**: Every silkscreen label across all known revs is inventoried (e.g. `VPP`, `VPP_EN`, `WE`, `OE`, `CE`, `A0`..`A18`, `D0`..`D7`, `VCC`, `GND`, etc.) and recorded in a single canonical table in `.planning/v1.7-SHIELD-REVS.md`. The table maps silkscreen label → proposed code-side alias (descriptive identifier suitable for use in C++ + Python source). Alias naming convention: `PIN_<SUBSYSTEM>_<FUNCTION>` (e.g. `PIN_VPP_REGULATOR_ENABLE`, `PIN_DATA_BUS_BYTE_0`, `PIN_ADDRESS_BUS_A14`). (4-way namespace lock at execution time: CTRL_/PIN_/RES_/JMP_; §7 populated with 17 rows; Phase 33 Plan 04 — 2026-05-25)
- [x] **ALIAS-02**: Aliases land as `#define` / `constexpr` declarations in `firestarter/include/rurp_pinout.h` (or equivalent header — fixed at plan time) and as constants in `firestarter_app/firestarter/constants.py` (or equivalent module). Existing call-sites that use bare pin numbers or shield-specific net names are migrated to the aliases. The migration is name-only — no wire-format or behavior changes.
- [x] **ALIAS-03**: GATE-1.7 non-regression — after the alias migration, compiled firmware `.hex` artifacts for all three boards (`uno`, `leonardo`, `uno328pb`) are byte-identical to pre-migration (modulo trivial symbol-name overhead, ≤ ~50 B). Pytest + Unity test suites stay green.

### Shield-Version-Detect Hardware Design (DETECT-HW)

- [ ] **DETECT-HW-01**: A schematic delta for the next-rev shield (likely Rev 2.3) is designed and documented in `.planning/v1.7-SHIELD-REVS.md`: a resistor divider into an Arduino ADC pin (pin selected to not conflict with any currently-used RURP signal across any known rev; verified against CAPS-01 capability matrix), with rev-specific resistor values that produce clearly distinguishable voltage bands per rev (≥ ~0.3V separation against 10-bit ADC noise floor)
- [ ] **DETECT-HW-02**: The schematic delta includes a per-rev expected-ADC-band table (rev string → expected ADC value range), suitable for firmware lookup at boot. Initial table seeds the next-rev (Rev 2.3) entry; existing Rev 0 / 2.0 / 2.2 boards have no detect resistor and produce floating/grounded ADC readings — captured in the table as the "rev_unknown" fall-through band.

### Shield-Version-Detect Firmware Plumbing (DETECT-FW)

- [ ] **DETECT-FW-01**: Firmware reads the ADC pin at boot (or on first handshake), looks up the voltage band in the DETECT-HW-02 table, and reports the detected silkscreen-rev string in the handshake payload (extends `MSG_OK_FW_HANDSHAKE` or adds a sibling INFO message — exact wire format finalized at plan time). On pre-detect-resistor boards (floating/grounded ADC), the report is `rev_unknown` and firmware falls through to honoring the operator-configured `hw_revision` byte in EEPROM (existing behavior preserved).
- [ ] **DETECT-FW-02**: GATE-1.7 non-regression — existing pre-detect-resistor boards continue to handshake byte-identical to v1.6 baseline (modulo the additive `rev_unknown` report, which is documented as a new INFO emit). Chip programming + read paths byte-identical. Firmware compiles cleanly for all three board targets without requiring physical fabrication of the next-rev shield.

### Documentation & Close (DOC, MS)

- [ ] **DOC-01**: `.planning/v1.7-SHIELD-REVS.md` is the canonical reference. README updates in `firestarter/` + `firestarter_app/` cross-link to it for "which shield rev do I have" + "what does this silkscreen label mean in code" lookups. PROJECT.md "Validated" section grows entries for the alias migration + detect plumbing.
- [ ] **MS-01**: Milestone v1.7 closed via `/gsd-complete-milestone`; MILESTONES.md entry written; phase artifacts archived under `.planning/milestones/v1.7-phases/`.

## Future Requirements (deferred to later milestones)

- **v1.6 resume** — Fix the Read Bug. Phase 27 RCA re-open uses v1.7's labeled-schematic + per-rev capability table + shield-version-detect firmware plumbing to design instrumented A/B builds with known-good schematics. First experiment: pre-Phase-28-firmware A/B test on Leonardo (build `firestarter/v1.6-read-bug~2`, sideload, re-probe).
- **w27c512-eeprom-misclassification fix** — separate HIGH-priority backlog; chip-database routing bug; carry to its own milestone after v1.6 closes.
- **avrdude-based MCU-detection fallback** — low priority; blank-chip recovery path.
- **v1.1 Phase 4 FM1608 byte-0 read bug** — separate hardware-gated investigation, parked since 2026-05-18.
- **Physical fabrication of next-rev (Rev 2.3) shield** — operator-side; out of scope here. v1.7 delivers design + firmware plumbing only.
- **Runtime algorithm-vs-rev capability guards** (firmware refuses an algorithm if the bench rev physically cannot support it) — captured as a CAPS-02 follow-up todo; implement in a later milestone once CAPS matrix is solid.

## Out of Scope

- Fixing the v1.6 read-bug itself (v1.6 territory; resumes after v1.7 ships)
- New chip support, new board MCU targets, new firmware features beyond DETECT-FW plumbing
- Physical PCB manufacturing of the next-rev shield (operator orders/fabricates separately; v1.7 commits the schematic delta + firmware-side detect logic only)
- EEPROM `rurp_configuration_t.hw_revision` byte semantics — preserved as legacy fall-back; no breaking change
- v1.3 CMOS EPROM Family Hardware Validation resume (separate paused milestone, hardware-gated)
- Beta release pipeline / lockstep coordination changes (v1.4 plumbing stays as-is)
- RURP shield manufacturing instructions (operator-side concern)

## Traceability

Phase mappings locked 2026-05-22 — every v1.7 requirement maps to exactly one phase. Coverage: 17/17 ✓.

| REQ-ID       | Phase |
|--------------|-------|
| HW-INV-01    | Phase 31 |
| HW-INV-02    | Phase 31 |
| HW-INV-03    | Phase 31 |
| SILK-01      | Phase 31 |
| DIFF-01      | Phase 32 |
| DIFF-02      | Phase 32 |
| CAPS-01      | Phase 32 |
| CAPS-02      | Phase 32 |
| ALIAS-01     | Phase 33 |
| ALIAS-02     | Phase 33 |
| ALIAS-03     | Phase 33 |
| DETECT-HW-01 | Phase 34 |
| DETECT-HW-02 | Phase 34 |
| DETECT-FW-01 | Phase 34 |
| DETECT-FW-02 | Phase 34 |
| DOC-01       | Phase 35 |
| MS-01        | Phase 35 |

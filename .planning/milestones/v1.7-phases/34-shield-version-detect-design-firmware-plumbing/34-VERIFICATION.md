---
phase: 34-shield-version-detect-design-firmware-plumbing
verified: 2026-05-25T17:00:00Z
status: human_needed
score: 4/4 success criteria verified (desk-side); operator-on-bench validation pending
overrides_applied: 0
human_verification:
  - test: "Sideload Phase 34 firmware to operator's Rev 2.0 board (chip OUT of socket per memory feedback_chip_out_before_sideload); confirm MSG_OK_REV reports either 'Rev 2.0-class' or 'rev_unknown'"
    expected: "Detected silkscreen-rev string surfaces in handshake/log; either string is acceptable per the backward-compat fall-through clause (pre-detect-resistor board → rev_unknown; R41-equipped board → Rev 2.0-class)"
    why_human: "Requires physical hardware sideload + serial log inspection — cannot be verified programmatically. Acknowledged in 34-06-SUMMARY.md Phase 35 hand-off as the operator-on-bench validation step."
  - test: "Sideload Phase 34 firmware to operator's Rev 2.2 board; capture the MSG_OK_REV report"
    expected: "If R41 = 4k7 (schematic) → reports 'Rev 2.0-class'. If R41 = 10k (Anders chat-intel) → reports 'Rev 2.3'. The result resolves the §8 OPEN annotation (Phase 35 follow-up #5)."
    why_human: "Resolves a documented OPEN discrepancy through physical hardware measurement — Phase 35 follow-up #5 explicitly carries this."
  - test: "Confirm CR-01 (INPUT_PULLUP active during analogRead) does not silently misclassify operator's Rev 2.0 (4k7) and Rev 2.2 boards on bench"
    expected: "Each board reports a stable per-rev string across multiple boots; if a 4k7-bucket board lands at ADC ≈ 200..220 (the narrow guard gap from CR-02), it would report 'rev_unknown' — flagged as a known Phase 34 follow-up but does NOT violate Phase 34 success criterion 4 (rev_unknown fall-through preserved + EEPROM hw_revision override path intact)."
    why_human: "Bench characterisation of real silicon — pull-up shift magnitude is silicon/AVcc-load dependent and cannot be measured statically. Already surfaced as 34-REVIEW.md CR-01 / CR-02; documented as Phase 35 / Phase 34.1 follow-up."
known_followups:
  - source: "34-REVIEW.md CR-01 (BLOCKER classification — advisory only)"
    summary: "INPUT_PULLUP residual on PIN_HW_REVISION_DETECT_ADC during analogRead — internal pull-up (20–50 kΩ) shifts band centres ~15–30% from RESEARCH-projected values."
    impact_on_phase_34_success_criteria: "None of the 4 ROADMAP §Phase 34 Success Criteria fail by this. Bands are documented (SC #2), firmware reads ADC at boot and reports detected string (SC #3), pre-detect-resistor boards continue to report rev_unknown + EEPROM hw_revision fall-through (SC #4), firmware compiles cleanly for all 3 envs (SC #4). The empirical band centres need re-derivation on bench but the substrate is in place."
    disposition: "Defer to Phase 35 operator-on-bench validation OR a Phase 34.1 gap-closure cycle (per operator directive at verification kickoff)."
  - source: "34-REVIEW.md CR-02 (BLOCKER classification — advisory only)"
    summary: "Narrow 20-count guard gap between 4k7 and 10k buckets + silent fall-through to ctrl_reg=0 on REVISION_UNKNOWN."
    impact_on_phase_34_success_criteria: "None. The guard-gap mechanism + REVISION_UNKNOWN sentinel are explicitly part of D-07 + §9 row 6; ctrl_reg=0 on unknown rev is the documented fail-safe per RESEARCH §Caller Audit. Operator EEPROM hw_revision override is the documented escape hatch (SC #4 preserved)."
    disposition: "Same as CR-01 — Phase 35 / Phase 34.1 follow-up."
  - source: "34-REVIEW.md WR-01..WR-05 (Warning-class — advisory only)"
    summary: "MSG_INFO_HW + MSG_INFO_PHYSICAL_HW still render via generic catalog format (raw byte); MSG_OK_CFG override clause not silkscreen-aware; _REVISION_SILKSCREEN dict not keyset-validated against firmware enum; revision = 0xFF initializer collides with EEPROM sentinel; rurp_hw_rev_utils.h defines bodies in a header."
    impact_on_phase_34_success_criteria: "None. WR-01 + WR-02 are extension surface (MSG_OK_REV is the formal handshake path per RESEARCH §`hardware.py` Consumer; MSG_INFO_HW is INFO-level log decoration). WR-04's initializer collision is dead-code in normal boot flow per RESEARCH (overwritten on first call to rurp_detect_hardware_revision()). WR-05 is pre-existing structural that Phase 33 + 34 inherited."
    disposition: "Captured for Phase 35 close paperwork or v1.8 backlog as appropriate."
---

# Phase 34: Shield-Version-Detect Design + Firmware Plumbing — Verification Report

**Phase Goal (from ROADMAP.md Phase 34 block):**
> Operator can build the next-rev shield (with the new detect resistor populated) and the firmware reports the correct silkscreen-version string in the handshake without operator intervention. Existing pre-detect-resistor boards continue to report `rev_unknown` and fall through to the EEPROM `hw_revision` byte — no breaking change.

**Verified:** 2026-05-25T17:00:00Z
**Status:** human_needed (4/4 desk-side success criteria verified; operator-on-bench validation pending per Phase 35 hand-off per 34-06-SUMMARY.md status banner)
**Re-verification:** No — initial verification.

---

## Goal Achievement

### Observable Truths (ROADMAP §Phase 34 Success Criteria)

| # | Success Criterion (truth) | Status | Evidence |
|---|---------------------------|--------|----------|
| 1 | `.planning/v1.7-SHIELD-REVS.md` §8 documents schematic delta with resistor divider into ADC pin; ≥ ~0.3V separation against 10-bit ADC noise floor | ✓ VERIFIED | `/workspaces/.planning/v1.7-SHIELD-REVS.md:133-183` carries §8 with lead paragraph (D-01), ASCII topology (JP4/P1_VPP_JMP → R41 → A3 → GND), per-rev R41 value table (6 rows incl. Modified Rev 0), Source Evidence cross-refs to §3 + §7 rows 15/16/17 + `mine-notes.md`, JP4 caveat narrating 1x2→2x2 footprint transition. ADC pin = A3 = `PIN_HW_REVISION_DETECT_ADC` declared at `firestarter/include/rurp_pinout.h:46` (HARDWARE_REVISION-gated, no signal-conflict per §7 capability check). Voltage band separation per RESEARCH §ADC Voltage Band Math: 4k7 band centre ≈ 88–195 ADC ≈ 0.43–0.95V; 10k band centre ≈ 170–341 ADC ≈ 0.83–1.66V — separation ≥ 0.30V at worst-case Rpu (Phase 35 bench validation needed per CR-01 follow-up). |
| 2 | Per-rev expected-ADC-band table included; next-rev (Rev 2.3) entry seeded; pre-detect-resistor boards captured as rev_unknown fall-through | ✓ VERIFIED | `/workspaces/.planning/v1.7-SHIELD-REVS.md:185-201` carries §9 with all 6 D-11 row classes: Rev 0 / Rev 1 (high band, A3 floating, A2 disambig); Rev 2.0/2.1/2.2 broad-bucket (`REVISION_2_0 = 2`, silkscreen `"Rev 2.0-class"`); Rev 2.3 first-class (`REVISION_2_3 = 5`, silkscreen `"Rev 2.3"`); Modified Rev 0 operator-attested via EEPROM; catchall (`REVISION_UNKNOWN = 0xFE`, silkscreen `"rev_unknown"`). Threshold-constant footnote cites `ADC_BAND_R41_4K7_HIGH = 200`, `ADC_BAND_R41_10K_LOW = 220`, `ADC_BAND_R41_10K_HIGH = 600` — all three present in `/workspaces/.planning/v1.7-SHIELD-REVS.md:187,199-201`. |
| 3 | Firmware reads ADC pin at boot, looks up voltage band, reports detected silkscreen-rev string in handshake payload | ✓ VERIFIED | `firestarter/include/rurp_hw_rev_utils.h:60-89` (`rurp_detect_hardware_revision()`) reads `analog_read_avg8(PIN_HW_REVISION_DETECT_ADC)` (8-sample avg via shift-divide, line 52-58), 4-arm `if/else-if/else-if/else` band-lookup chain decides REVISION_2_0 / REVISION_2_3 / (Rev 0 vs Rev 1 via A2 disambig) / REVISION_UNKNOWN; called at boot via `setup() → rurp_detect_hardware_revision()` (firmware sub-repo). Host-side surfacing: `firestarter_app/firestarter/serial_comm.py:171-179` `_REVISION_SILKSCREEN` dict maps the 7 REVISION_* byte values to silkscreen strings; `serial_comm.py:351-357` `_format_message` MSG_OK_REV branch uses defensive `.get(byte, f"Rev{byte}")` lookup for both physical and effective bytes — operator sees `"Rev 2.3"` / `"Rev 2.0-class"` / `"rev_unknown"` in CLI output instead of `"Rev5"` / `"Rev2"`. |
| 4 | Pre-detect-resistor boards report rev_unknown + honor EEPROM hw_revision; GATE-1.7 byte-identical handshake modulo additive rev_unknown report; firmware compiles cleanly for all 3 targets without physical shield fab | ✓ VERIFIED | (a) `rurp_hw_rev_utils.h:81-87` else-arm explicitly assigns `revision = REVISION_UNKNOWN`; (b) `rurp_hw_rev_utils.h:91-97` `rurp_get_hardware_revision()` body UNCHANGED — `rurp_config->hardware_revision < 0xFF` returns EEPROM override; otherwise returns physical; (c) `verify-detect-34.sh` (`/workspaces/.planning/v1.7/baseline-34/verify-detect-34.sh`) PASS on Phase 34 final state — per-env Δ uno −299 / uno328pb −454 / leonardo −491 B (all within `abs(Δ) ≤ 600` magnitude band, widened per Plan 04 + 34-03-SUMMARY.md Option B), native dispatch suite 15/15 PASS (configure_memory unaffected per VALIDATION Dim 1 / DETECT-FW-02 GATE-1.7), `REVISION_2_3` + `REVISION_UNKNOWN` both present in `rurp_shield.h`. All 3 AVR envs compile clean (uno / uno328pb / leonardo); no physical Rev 2.3 shield required. |

**Score:** 4/4 desk-side success criteria verified.

### Required Artifacts (3-level + Level 4 data-flow checks)

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/include/rurp_shield.h` (line 25-32) | REVISION_2_3 = 5; REVISION_UNKNOWN = 0xFE under #ifdef HARDWARE_REVISION | ✓ VERIFIED | Read at `:25-32`. Both defines present; existing dense 0..4 numbering preserved. Inline comment carries 0xFE/0xFF carve-out rationale verbatim. Substantive + wired (consumed by `rurp_hw_rev_utils.h` + `constants.py`). |
| `firestarter/include/rurp_pinout.h` (Section 1b, lines 49-62) | ADC_BAND_R41_4K7_HIGH = 200; ADC_BAND_R41_10K_LOW = 220; ADC_BAND_R41_10K_HIGH = 600; all inside #ifdef HARDWARE_REVISION; strict ordering 200 < 220 < 600 | ✓ VERIFIED | Read at `:49-62`. All 3 constants present with correct values and strict ordering; #define-NOT-constexpr per Phase 33 D-07. Wired into `rurp_hw_rev_utils.h:68-76` (consumed by the 4-arm band-lookup). |
| `firestarter/include/rurp_hw_rev_utils.h` (lines 52-89) | analog_read_avg8 helper; reworked rurp_detect_hardware_revision() with analogRead + band-lookup; case REVISION_2_3 arm in rurp_map_ctrl_reg_for_hardware_revision; latent revision=0xFF eliminated from function body; rurp_get_hardware_revision() UNCHANGED | ✓ VERIFIED | All 6 sub-elements confirmed: (a) `:52-58` static inline `analog_read_avg8(uint8_t pin)` with 8-iteration loop + `sum >> 3`; (b) `:60-89` reworked detect-rev body — `pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT_PULLUP)` (advisory CR-01: see follow-ups), `analog_read_avg8` invocation, 4-arm `if/else-if/else-if/else` chain assigning REVISION_2_0 / REVISION_2_3 / (REVISION_1\|REVISION_0 via A2 < 1000) / REVISION_UNKNOWN; (c) `:21` `case REVISION_2_3:` arm aliased to REV_2_x layout (lines 18-26); (d) function-body `revision = 0xFF` ELIMINATED (verified by absence in awk-scoped function body `:60-89`); (e) `:91-97` `rurp_get_hardware_revision()` body BYTE-IDENTICAL to pre-edit (`rurp_config->hardware_revision < 0xFF` → EEPROM override, else physical); (f) file-scope `uint8_t revision = 0xFF;` at line 12 PRESERVED (intentional per RESEARCH dead-code-in-boot-flow). |
| `firestarter_app/firestarter/constants.py` (lines 85-98) | `# RURP Hardware Revisions` block with 7 REVISION_* constants (REVISION_0=0x00 through REVISION_UNKNOWN=0xFE) | ✓ VERIFIED | Read at `:85-98`. All 7 constants present with exact byte values matching firmware enum (REVISION_0=0x00, REVISION_1=0x01, REVISION_2_0=0x02, REVISION_2_1=0x03, REVISION_2_2=0x04, REVISION_2_3=0x05, REVISION_UNKNOWN=0xFE). Section-header carries sync-burden prose + 0xFF/0xFE sentinel carve-out narrative. Wired: imported into `serial_comm.py` via existing `from firestarter.constants import *` wildcard (used in `_REVISION_SILKSCREEN` dict literal); also imported via named imports in `tests/test_revision_constants_parity.py:21-29`. |
| `firestarter_app/CLAUDE.md` (line 100) | Constants subsection paragraph extended with RURP_HARDWARE_REVISIONS sync-rule sentence; Phase 33 CTRL_* sentence preserved | ✓ VERIFIED | Read at `:100`. Phase 33 CTRL_* sentence preserved verbatim. New Phase 34 sentence appended in same paragraph: cites `RURP_HARDWARE_REVISIONS` block, `firestarter/include/rurp_shield.h`, `Phase 34 / v1.7`, sync directive, AND novel 0xFE/0xFF sentinel carve-out clause. Sentence-template consistency with Phase 33's CTRL_* sentence confirmed. |
| `firestarter_app/tests/test_revision_constants_parity.py` | Hard pytest parity assertion enforcing all 7 REVISION_* byte values; named imports; module-level docstring with copyright header | ✓ VERIFIED | Read in full (45 lines). Module-level docstring with Copyright header + Phase 34 citation + source-of-truth line ref; named imports of all 7 REVISION_* constants from `firestarter.constants`; single test function `test_revision_byte_values_match_firmware_enum` with 7 `assert NAME == 0xNN` lines; trailing 0xFF sentinel-reserve comment. pytest run: 83 passed (82 baseline + 1 new). Substantive + wired (auto-discovered by pytest). |
| `firestarter_app/firestarter/serial_comm.py` (lines 168-179, 351-357) | Module-scope _REVISION_SILKSCREEN dict (7 entries) + extended _format_message MSG_OK_REV branch using defensive .get() lookup | ✓ VERIFIED | Read at `:168-179` — 3-line comment header + 7-entry dict literal mapping REVISION_0→"Rev 0" through REVISION_UNKNOWN→"rev_unknown" (broad-bucket "Rev 2.0-class" per D-04 + override-annotated "Rev 2.1 (override)" / "Rev 2.2 (override)"). Read at `:351-357` — `_format_message` MSG_OK_REV branch uses `_REVISION_SILKSCREEN.get(physical, f"Rev{physical}")` AND `_REVISION_SILKSCREEN.get(effective, f"Rev{effective}")`; 0xFF-effective-sentinel branch preserved verbatim (line 354). |
| `.planning/v1.7-SHIELD-REVS.md` §8 + §9 (lines 133-201) | §8 schematic delta + per-rev R41 table + JP4 caveat; §9 6-column ADC band table + threshold-constant footnote | ✓ VERIFIED | Read full §8 + §9 spans (133-201). All 6 row classes present in §9; threshold constants cross-linked in both narrative paragraph (`:187`) and footnote (`:199-201`). `grep -c "OWNED BY PHASE 34" v1.7-SHIELD-REVS.md` = 0 — no Phase 34 TBD markers remain. |
| `verify-detect-34.sh` (gitignored under `.planning/v1.7/baseline-34/`) | 3-assertion gate (delta band + native dispatch + enum presence); PASS on Phase 34 final state | ✓ VERIFIED + EXECUTED | Probe executed in this verification at `/workspaces/.planning/v1.7/baseline-34/verify-detect-34.sh` — exit code 0; PASS banner emitted; per-env Δ uno −299 / uno328pb −454 / leonardo −491 B (all `abs(Δ) ≤ 600`); native dispatch suite green; `REVISION_2_3` + `REVISION_UNKNOWN` confirmed in `rurp_shield.h`. |

### Key Link Verification (Wiring)

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `rurp_hw_rev_utils.h` detect-rev body | `rurp_shield.h` REVISION_2_3 + REVISION_UNKNOWN | C preprocessor #include "rurp_shield.h" at `:6` | ✓ WIRED | Symbols referenced at `:72` (REVISION_2_0), `:75` (REVISION_2_3), `:80` (REVISION_1, REVISION_0), `:86` (REVISION_UNKNOWN); `:21` REVISION_2_3 case-label. |
| `rurp_hw_rev_utils.h` detect-rev body | `rurp_pinout.h` ADC_BAND_R41_* thresholds + PIN_HW_REVISION_DETECT_ADC | C preprocessor #include "rurp_pinout.h" at `:7` | ✓ WIRED | All 3 threshold constants referenced at `:68`, `:73`, `:76`; pin alias `PIN_HW_REVISION_DETECT_ADC` referenced at `:61` (pinMode) + `:66` (analog_read_avg8 call). |
| `rurp_map_ctrl_reg_for_hardware_revision()` | `rurp_get_hardware_revision()` (EEPROM-override fall-through) | direct call at `:16` | ✓ WIRED | Dispatcher consumes `rurp_get_hardware_revision()` which already returns the EEPROM-override-priority value per `:91-97` (operator-configured `hw_revision` byte wins over physical detect). |
| `firestarter_app/firestarter/serial_comm.py` `_REVISION_SILKSCREEN` | `firestarter_app/firestarter/constants.py` REVISION_* | Python wildcard `from firestarter.constants import *` near top of serial_comm.py (Phase 33 convention) | ✓ WIRED | Constants used as dict keys at `:172-178`; pytest parity gate at `tests/test_revision_constants_parity.py` confirms byte-value fidelity vs firmware enum. |
| `_format_message` MSG_OK_REV path | `_REVISION_SILKSCREEN` dict | defensive `.get(byte, fallback)` lookup at `:353,356` | ✓ WIRED | Both physical and effective bytes routed through `.get()`; unknown bytes fall back to `f"Rev{byte}"` without raising KeyError; 0xFF-effective-sentinel branch preserved at `:354`. |
| `verify-detect-34.sh` Assertion 3 | `rurp_shield.h` REVISION_2_3 + REVISION_UNKNOWN | `grep -q` at script body | ✓ WIRED | Both enum strings present in `rurp_shield.h:30-31` confirmed by probe execution (PASS banner). |
| Meta-repo submodule pointer `firestarter` | Plan-03 firestarter HEAD SHA `032a2e2` | git submodule (`git ls-tree HEAD firestarter`) | ✓ WIRED | `git ls-tree HEAD firestarter` returns `160000 commit 032a2e2b93238856a70b1d0b87c6c332d6d6cf02`; matches `cd firestarter && git rev-parse HEAD` (`032a2e2`). Bumped in meta-repo commit `a8805b0` (Plan 04). |
| Meta-repo submodule pointer `firestarter_app` | Plan-06 firestarter_app HEAD SHA `b2183ed` | git submodule (`git ls-tree HEAD firestarter_app`) | ✓ WIRED | `git ls-tree HEAD firestarter_app` returns `160000 commit b2183ed2fc9c78d4569c410e6a2593c073fc5e1a`; matches `cd firestarter_app && git rev-parse HEAD` (`b2183ed`). Bumped in meta-repo commit `bef5bec` (Plan 06). |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `rurp_detect_hardware_revision()` → `revision` (file-scope) | `revision` (uint8_t) | `analog_read_avg8(PIN_HW_REVISION_DETECT_ADC)` (8-sample averaged hardware ADC read on Arduino A3) + `analogRead(PIN_VPP_VOLTAGE_ADC)` for high-band disambig | ✓ FLOWING | Real Arduino ADC reads drive the band-lookup; no static return / no hardcoded value. CR-01 caveat (INPUT_PULLUP residual) shifts the magnitude of the reading but does not break the data-flow — the variable carries a real ADC-derived rev classification. |
| `rurp_get_hardware_revision()` return value | `rurp_config->hardware_revision` (EEPROM byte) OR `revision` (physical detect) | `rurp_get_config()` → EEPROM-backed `rurp_configuration_t.hardware_revision` (load-bearing operator override path) | ✓ FLOWING | Real EEPROM byte from `rurp_save_config` / load lifecycle; physical detect via `rurp_get_physical_hardware_revision()` returns the ADC-driven `revision` value. SC #4 EEPROM-override-fall-through preserved by construction. |
| `_format_message` MSG_OK_REV rendering → CLI output | `params[0]` (physical u8), `params[1]` (effective u8) | MSG_OK_REV wire frame emitted by firmware via `LOG_OK_ID_*` in `hardware_operations.cpp`; wire shape per `tools/catalog/messages.toml` P-02 — UNCHANGED per D-09 | ✓ FLOWING | Real wire bytes from serial transport drive the rendering; `_REVISION_SILKSCREEN.get()` translates to silkscreen string; tests at `test_decoder.py:366-394` exercise the path with mocked SerialFake (`fake_serial` fixture). |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| firestarter_app pytest suite green (83 tests; Plan 05 parity + Plan 06 silkscreen-string updates) | `cd /workspaces/firestarter_app && pytest` | `83 passed in 0.79s` | ✓ PASS |
| Module import smoke-test (REVISION_* constants importable + correct byte values) | `python -c "from firestarter.constants import REVISION_2_3, REVISION_UNKNOWN; assert REVISION_2_3 == 0x05 and REVISION_UNKNOWN == 0xFE"` (per 34-05-SUMMARY.md self-check) | exit 0 | ✓ PASS (re-asserted via pytest module test_revision_byte_values_match_firmware_enum) |
| Phase 34 verify-detect-34.sh probe (3-assertion gate) | `bash /workspaces/.planning/v1.7/baseline-34/verify-detect-34.sh` | exit 0; PASS banner | ✓ PASS (see Probe Execution below) |
| 0xFE non-collision audit in firestarter sources | `grep -rn "0xFE" firestarter/src/ firestarter/include/` filtered for non-comment / non-CRC8-LUT | Only `rurp_serial_utils.cpp:120` (CRC8 LUT byte) + `rurp_hw_rev_utils.h:84` (comment) + `rurp_shield.h:31` (the new REVISION_UNKNOWN); no other collision | ✓ PASS |

### Probe Execution

| Probe | Command | Result | Status |
|-------|---------|--------|--------|
| `.planning/v1.7/baseline-34/verify-detect-34.sh` | `bash /workspaces/.planning/v1.7/baseline-34/verify-detect-34.sh` | exit 0; output: `PASS: Phase 34 detect-rev rework verified — delta within band, native tests green, enums present.` Per-env Δ uno=−299 B / uno328pb=−454 B / leonardo=−491 B (all `abs(Δ) ≤ 600 B` per Plan 04 magnitude-band widening). Native dispatch suite reported PASS. REVISION_2_3 + REVISION_UNKNOWN confirmed present in `firestarter/include/rurp_shield.h`. | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|----------------|-------------|--------|----------|
| DETECT-HW-01 | 34-01 | Resistor divider into ADC pin + ≥ 0.3V band separation, no signal conflict | ✓ SATISFIED | §8 fill at `v1.7-SHIELD-REVS.md:133-183`; ADC pin = A3 = `PIN_HW_REVISION_DETECT_ADC` (`rurp_pinout.h:46`, HARDWARE_REVISION-gated); voltage band separation per RESEARCH §ADC Voltage Band Math (bench validation deferred to Phase 35 per CR-01 follow-up — does not block desk-side delivery). |
| DETECT-HW-02 | 34-01 | Per-rev expected-ADC-band table with rev_unknown fall-through entry | ✓ SATISFIED | §9 fill at `v1.7-SHIELD-REVS.md:185-201`; all 6 row classes present (Rev 0 / Rev 1 / Rev 2.0-class / Rev 2.3 / Modified Rev 0 / REVISION_UNKNOWN catchall); threshold-constant cross-link to `rurp_pinout.h` declarations. |
| DETECT-FW-01 | 34-00, 34-02, 34-03, 34-04, 34-05, 34-06 | Firmware ADC band-lookup + handshake silkscreen-rev string + EEPROM fall-through preserved | ✓ SATISFIED | (a) Firmware: `rurp_detect_hardware_revision()` reworked to analog band-lookup (`rurp_hw_rev_utils.h:60-89`); `case REVISION_2_3:` arm (`:21`); `rurp_get_hardware_revision()` EEPROM-override fall-through UNCHANGED (`:91-97`). (b) Python parity: 7 REVISION_* constants in `constants.py:85-98` + hard pytest parity gate. (c) Host rendering: `_REVISION_SILKSCREEN` dict + `_format_message` MSG_OK_REV branch in `serial_comm.py`. |
| DETECT-FW-02 | 34-00, 34-02, 34-03, 34-04, 34-05, 34-06 | GATE-1.7 non-regression — chip programming/read paths byte-identical; compiles cleanly for all 3 targets; rev_unknown additive only | ✓ SATISFIED | `verify-detect-34.sh` PASS (per-env Δ in `abs(Δ) ≤ 600` band; widened from signed [+20,+300] per Plan 04 reconciliation of Plan 03 empirical negative-delta — substrate stayed within an honest magnitude budget); native dispatch suite 15/15 PASS (configure_memory unaffected); pytest 83/83 PASS; all 3 AVR envs (uno / uno328pb / leonardo) build clean. MSG_OK_REV wire shape unchanged per D-09 (`tools/catalog/messages.toml` untouched; auto-generated `messages.py` untouched; `hardware.py` untouched). |

All 4 Phase-34 requirement IDs (DETECT-HW-01, DETECT-HW-02, DETECT-FW-01, DETECT-FW-02) per `.planning/REQUIREMENTS.md:88-92` are SATISFIED on the desk-side. No orphaned requirements.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter/include/rurp_hw_rev_utils.h` | 61-62 | `pinMode(..., INPUT_PULLUP)` active during subsequent `analogRead` (CR-01 from 34-REVIEW.md) | ℹ️ INFO (advisory only — see human_verification + known_followups) | Shifts ADC band centres ~15-30% from RESEARCH-projected math. Does NOT violate Phase 34 desk-side success criteria — rev_unknown fall-through + EEPROM-override path remain intact (SC #4 preserved). Bench validation deferred to Phase 35 / Phase 34.1 per operator directive at verification kickoff. |
| `firestarter/include/rurp_hw_rev_utils.h` | 73-87 | 20-count guard gap between 4k7/10k buckets + silent ctrl_reg=0 on REVISION_UNKNOWN (CR-02 from 34-REVIEW.md) | ℹ️ INFO (advisory only) | Narrow guard gap may produce false REVISION_UNKNOWN under noise; silent ctrl_reg=0 is the documented fail-safe per RESEARCH §Caller Audit (EEPROM hw_revision override = operator escape hatch). Does NOT violate any of the 4 ROADMAP success criteria. |
| `firestarter/include/rurp_hw_rev_utils.h` | 12 | File-scope `uint8_t revision = 0xFF;` initializer (WR-04) | ℹ️ INFO | Dead-code in normal boot flow per RESEARCH (overwritten on first call to `rurp_detect_hardware_revision()`); intentional preservation per Plan 02 + Plan 03 — does not violate the EEPROM-sentinel disjointness invariant at runtime. |
| `firestarter_app/firestarter/serial_comm.py` | 359-363 | MSG_OK_CFG override clause still renders `Rev{int}` (WR-02 from 34-REVIEW.md) | ℹ️ INFO | MSG_OK_CFG is a separate catalog message from MSG_OK_REV; Plan 06 scope was MSG_OK_REV per D-05 Path A. MSG_OK_CFG extension is out-of-scope for Phase 34 and recorded for Phase 35 close paperwork or v1.8 backlog. |
| `.planning/v1.7-SHIELD-REVS.md` | 56, 58, 74, 169 | `TBD pending Phase 35` and `OPEN: ... (Phase 35 follow-up #5)` markers | ℹ️ INFO | All markers carry formal follow-up references (Phase 35 follow-up #3, #4, #5; MODIFICATIONS.md stub). Phase 32-owned §4 + §5 deferrals — NOT Phase 34 §8/§9 (which are 100% filled — `grep -c "OWNED BY PHASE 34"` = 0). Auditable debt. |

**No `TBD`, `FIXME`, or `XXX` debt markers found in Phase 34 modified source files** (firestarter/include/*.h, firestarter_app/firestarter/*.py, firestarter_app/CLAUDE.md, firestarter_app/tests/test_revision_constants_parity.py). Debt-marker gate clean for the firmware + Python surface.

### Commit Verification

All claimed commits exist on the expected branches:

| Repo | Commit | Subject | Branch | Status |
|------|--------|---------|--------|--------|
| firestarter sub-repo | `b243fb4` | `feat(34-02): add REVISION_2_3 + REVISION_UNKNOWN to rurp_shield.h enum (D-07; DETECT-FW-01 substrate)` | v1.7-shield-investigation | ✓ EXISTS |
| firestarter sub-repo | `032a2e2` | `feat(34-03): rework rurp_detect_hardware_revision() to analog band-lookup + add ADC_BAND_R41_* thresholds (DETECT-FW-01)` | v1.7-shield-investigation | ✓ EXISTS; HEAD |
| firestarter_app sub-repo | `9752a85` | `feat(34-05): add RURP_HARDWARE_REVISIONS Python parity block + sync rule + pytest gate (D-08; DETECT-FW-01)` | v1.7-shield-investigation | ✓ EXISTS |
| firestarter_app sub-repo | `b2183ed` | `feat(34-06): add _REVISION_SILKSCREEN dict to serial_comm.py for MSG_OK_REV rendering (D-05; DETECT-FW-01)` | v1.7-shield-investigation | ✓ EXISTS; HEAD |
| meta-repo | `c699324` | `docs(34-01): fill v1.7-SHIELD-REVS.md §8 + §9 — Detect-HW schematic delta + per-rev ADC band table (DETECT-HW-01 + DETECT-HW-02)` | v1.7-shield-investigation | ✓ EXISTS |
| meta-repo | `a8805b0` | `feat(34-04): bump firestarter to 032a2e2 — analog ADC band-lookup detect-rev rework (DETECT-FW-01 + DETECT-FW-02)` | v1.7-shield-investigation | ✓ EXISTS |
| meta-repo | `bef5bec` | `feat(34-06): bump firestarter_app to b2183ed — Python REVISION_* parity + serial_comm silkscreen mapping (DETECT-FW-01 + DETECT-FW-02; Phase 34 close)` | v1.7-shield-investigation | ✓ EXISTS |

Submodule pointers verified by `git ls-tree HEAD firestarter firestarter_app`:
- `firestarter` pinned at `032a2e2b93238856a70b1d0b87c6c332d6d6cf02` (matches sub-repo HEAD).
- `firestarter_app` pinned at `b2183ed2fc9c78d4569c410e6a2593c073fc5e1a` (matches sub-repo HEAD).

### Human Verification Required

The Phase 34 desk-side substrate is complete; per the explicit Phase 35 hand-off documented in `34-06-SUMMARY.md` and the verification kickoff directive, the following items require human/operator action and were not promotion-blockers in any Phase 34 plan:

#### 1. Sideload + bench-validate detect-rev on Rev 2.0 board

**Test:** Sideload Phase 34 firmware (firestarter HEAD `032a2e2`) to operator's Rev 2.0 board (chip OUT of socket per memory `feedback_chip_out_before_sideload`); capture the MSG_OK_REV (`OK: ...`) line on the serial console at the documented baud.
**Expected:** Either `"Rev 2.0-class"` (R41 = 4k7 populated → SC #1+#2 path) OR `"rev_unknown"` (no R41 / floating ADC → SC #4 fall-through path). Either outcome is acceptable per the backward-compat fall-through clause.
**Why human:** Requires physical hardware sideload + serial log inspection.

#### 2. Sideload + bench-validate detect-rev on Rev 2.2 board

**Test:** Same as item 1 but against operator's Rev 2.2 board. Compare the reported silkscreen string against schematic-stated 4k7 vs Anders chat-intel 10k.
**Expected:** Result resolves §8 OPEN annotation + Phase 35 follow-up #5.
**Why human:** Resolves a documented OPEN discrepancy through physical measurement.

#### 3. Characterize CR-01 / CR-02 magnitude impact on real silicon

**Test:** Capture per-boot `adc_a3` raw values across multiple boots on each on-hand shield rev (operator owns Rev 2.2 + Rev 2.0 + Modified Rev 0); cross-check vs the §9 expected-ADC-band table.
**Expected:** Stable per-rev classification across boots, OR a 4k7 board landing inside [200, 220) guard gap → report `"rev_unknown"` (documented intentional behavior, not a failure). EEPROM `hw_revision` override is the documented escape hatch.
**Why human:** Pull-up shift magnitude is silicon/AVcc-load dependent — cannot be measured statically. Already surfaced as 34-REVIEW.md CR-01 / CR-02; documented as Phase 35 / Phase 34.1 follow-up per operator directive at verification kickoff.

### Gaps Summary

**No blocker gaps.** All 4 ROADMAP §Phase 34 Success Criteria are observably satisfied in the codebase on the desk-side, all 4 requirement IDs (DETECT-HW-01, DETECT-HW-02, DETECT-FW-01, DETECT-FW-02) trace to verified artifacts, and the `verify-detect-34.sh` 3-assertion probe exits 0 PASS. pytest 83/83 PASS. All 3 AVR envs build clean.

The two `CRITICAL` findings in `34-REVIEW.md` (CR-01 INPUT_PULLUP residual; CR-02 narrow 20-count guard gap + silent ctrl_reg=0) are **advisory follow-ups for Phase 35 operator-on-bench validation or a Phase 34.1 gap-closure cycle** per the explicit verification kickoff directive — they do not flip the Phase 34 verdict because:
- SC #1 (resistor divider + ≥ 0.3V band separation): Documented in §8; CR-01's pull-up shift affects empirical magnitude but the divider topology and the documented separation budget hold by construction.
- SC #2 (per-rev band table + rev_unknown fall-through): Documented in §9; CR-02's guard gap is part of the documented design (REVISION_UNKNOWN catchall row); narrowness of the gap is bench-validatable later.
- SC #3 (firmware reads ADC + reports silkscreen): Code is present and wired; data flows through the analog-band-lookup path; CR-01 affects which band a given board hits but the read-and-report machinery is complete.
- SC #4 (rev_unknown + EEPROM override + 3-target compile): EEPROM-override path is UNCHANGED (`rurp_get_hardware_revision():91-97`); REVISION_UNKNOWN reporting is preserved; all 3 AVR envs compile cleanly without physical Rev 2.3 shield; chip-program/read paths byte-identical per native dispatch suite.

The 5 `WARNING`-class findings (WR-01..WR-05) are extension-surface concerns out of strict Phase 34 scope (MSG_INFO_HW / MSG_INFO_PHYSICAL_HW polish; MSG_OK_CFG silkscreen-isation; _REVISION_SILKSCREEN keyset validation; revision initializer; header-defined function bodies) — captured for Phase 35 close paperwork or v1.8 backlog as appropriate.

---

_Verified: 2026-05-25T17:00:00Z_
_Verifier: Claude (gsd-verifier)_

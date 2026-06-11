# Phase 34: Shield-Version-Detect Design + Firmware Plumbing — Discussion Log

**Date:** 2026-05-25
**Mode:** auto (no AskUserQuestion prompts; decisions auto-resolved from prior-phase substrate)
**For:** Audit / retrospective reference only. NOT consumed by gsd-researcher / gsd-planner / gsd-executor.

---

## Setup

- Phase 34 directory did not exist; created `.planning/phases/34-shield-version-detect-design-firmware-plumbing/` from `expected_phase_dir`.
- No `.continue-here.md` present → no blocking anti-patterns to acknowledge.
- No SPEC.md present for Phase 34 (project uses SPEC.md selectively; v1.7 phases skip SPEC since requirements are already locked in REQUIREMENTS.md + ROADMAP.md per Phase 31/32/33 pattern).
- No prior CONTEXT.md or interrupted DISCUSS-CHECKPOINT.json for Phase 34.
- Loaded prior context:
  - `.planning/PROJECT.md` — project overview
  - `.planning/REQUIREMENTS.md` — DETECT-HW-01..02, DETECT-FW-01..02
  - `.planning/STATE.md` — Phase 33 closed; ALIAS-01/02/03 all MET; ready for Phase 34
  - `.planning/phases/31-upstream-shield-archaeology/31-CONTEXT.md` — schema, source-citation patterns
  - `.planning/phases/33-silkscreen-label-code-alias-migration/33-CONTEXT.md` — D-06 hard-rename, D-07 `#define` byte-identical math, D-08 minimal Python parity
  - `.planning/v1.7-SHIELD-REVS.md` (full) — §3 R41-on-A3 scheme + §7 alias table + §8/§9 TBD markers
  - `firestarter/CLAUDE.md` + `firestarter_app/CLAUDE.md` — both loaded inline via system reminders
- No raw spikes/sketches; no findings skills to load.
- No pending TODO matches for Phase 34 scope.

---

## Domain Boundary

Phase 34 plumbs firmware-side detection of the existing Anders R41-on-A3 voltage-divider scheme (already shipped upstream in Rev 2.0 / 2.1 / 2.2 / 2.3 — documented in v1.7-SHIELD-REVS.md §3) and fills the §8 (Detect-HW Schematic Delta) + §9 (Per-Rev Expected ADC Band Table) markers. Firmware reworks `rurp_detect_hardware_revision()` from digital-A3 to analog-A3 band lookup; existing `MSG_OK_REV` wire shape preserved. Python-side adds parity REVISION_2_3 + REVISION_UNKNOWN constants. GATE-1.7: programming + read paths byte-identical on all 3 AVR envs. Desk-side only for Phase 34 close; operator-on-bench validation deferred to Phase 35.

---

## Auto-Resolved Gray Areas

Each gray area was auto-resolved using the prior-phase substrate. Decisions are captured in `34-CONTEXT.md` as D-NN entries; this section logs the reasoning trail.

### GA-1: Schematic-delta interpretation — design new PCB vs document existing upstream Rev 2.3

**Auto-resolution → D-01: document existing Anders Rev 2.3 R41=10k scheme; no new fabrication.**

**Rationale:** Operator does not own a Rev 2.3 board (memory [[user_shield_revisions]]: Rev 2.2 / Rev 2.0 / Modified Rev 0). Designing a Rev 2.4 with a fresh detect divider would require PCB fabrication + bench cycle outside v1.7 scope. Rev 2.3 already has the divider populated; Phase 34's job is plumbing firmware to read it, not designing new hardware. REQUIREMENTS.md DETECT-HW-02 explicitly names "Rev 2.3" as the seed entry.

### GA-2: ADC scheme rework — preserve dual-pin digital/analog or switch to single-pin band lookup

**Auto-resolution → D-06: switch A3 from `digitalRead` to `analogRead`; preserve A2 ADC for Rev 0 vs Rev 1 sub-distinction.**

**Rationale:** The spec calls for a band lookup table (DETECT-HW-02 + DETECT-FW-01). The existing `digitalRead(A3)` collapses Rev 2.0/2.1/2.2 (R41=4k7) and Rev 2.3 (R41=10k) into the same `value=0` (low) branch — cannot distinguish them. Switching to `analogRead(A3)` gives band separation per D-03 math (4k7 band ≈ ADC 138; 10k band ≈ ADC 256; floating-pull-up band ≈ ADC 1023; separation > 0.4 V across pull-up tolerance). The A2 ADC magic (`< 1000` → Rev 1, else Rev 0) is preserved verbatim in the high-band branch — proven working, no need to disturb.

### GA-3: Per-rev granularity — fine-grain (Rev 2.0 / 2.1 / 2.2 distinct) or broad bucket (Rev 2.x-class)

**Auto-resolution → D-04: broad bucket. ADC reports `REVISION_2_0` for the entire 4k7 family; EEPROM `hw_revision` byte refines if operator needs Rev 2.1 / Rev 2.2 distinction.**

**Rationale:** v1.7-SHIELD-REVS.md §6 confirms Rev 2.0, 2.1, 2.2 are electrically identical (R41 = 4k7 across all three per upstream schematics). They cannot be distinguished by ADC alone — physics gates this. The EEPROM override path (`rurp_get_hardware_revision()` at `rurp_hw_rev_utils.h:61-67`) already implements precedence correctly: EEPROM byte wins when set; physical detect wins otherwise. DETECT-FW-01 explicitly endorses the fall-through pattern ("falls through to honoring the operator-configured `hw_revision` byte in EEPROM").

### GA-4: Handshake wire format — extend MSG_OK_REV / add new MSG_INFO / add new MSG_OK code

**Auto-resolution → D-09: no new message ID; reuse `MSG_OK_REV` 2-byte wire shape verbatim; new enum values flow through the existing `physical_u8` payload position.**

**Rationale:** The spec's "extends `MSG_OK_FW_HANDSHAKE` or adds a sibling INFO message" phrasing leaves room to interpret. `MSG_OK_FW_HANDSHAKE` doesn't exist in the catalog (probable typo for `MSG_OK_FW_VERSION` 0x03 or `MSG_OK_REV` 0x04). Adding a new message ID would require a codegen pass on `tools/catalog/messages.toml` + bumping both `firestarter/include/messages.h` (autogen) and `firestarter_app/firestarter/messages.py` (autogen). Reusing `MSG_OK_REV` zero-cost — wire shape stable, host catalog stable, only payload values change. Format string `"Rev%u (eff: %u)"` already prints u8 values verbatim. DETECT-FW-02's "byte-identical to v1.6 baseline" is honored — frame structure unchanged.

### GA-5: GATE-1.7 verification mechanism — compile-only vs handshake-byte-cmp vs operator-on-bench

**Auto-resolution → D-10: per-env `.hex` size delta + native dispatch tests + pytest as the planner-side gate; operator-on-bench validation deferred to Phase 35.**

**Rationale:** Phase 33 shipped Δ = 0 B across all 3 AVR envs using exactly this pattern (per STATE.md last-activity). Phase 34 adds an `analogRead` call site, new threshold constants, a switch arm, an enum value branch — expected Δ ≈ 50–200 B per env (small, planner records actual). Sub-repo `v1.7-shield-investigation` → `beta` promotion happens at Phase 34 close (desk-side); `beta` → `main` is gated on operator-on-bench at Phase 35 per the v1.7 branch model. This honors the milestone's branch-promotion sequencing.

### GA-6: ADC band tolerances — hardcoded defaults vs calibrated per-board

**Auto-resolution → D-03 + D-11: hardcoded threshold constants in `rurp_pinout.h` (or sibling header — planner picks) derived from R41 values + ATmega internal pull-up worst-case math; operator EEPROM override is the calibration path.**

**Rationale:** Internal pull-up tolerance (20–50 kΩ) is the dominant noise term. Worst-case math still gives > 0.4 V band separation. If real-world readings land at a band edge, the EEPROM override mechanism (already shipped) is the escape hatch. Per-board calibration storage would inflate Phase 34 scope without payoff for a 3-band lookup.

### GA-7: Python-side parity — full mirror module vs minimal constants vs no-op

**Auto-resolution → D-08: minimal — add `REVISION_2_3` + `REVISION_UNKNOWN` constants to `constants.py` in a new `# RURP Hardware Revisions` block; extend `firestarter_app/CLAUDE.md` sync rule prose.**

**Rationale:** Phase 33's D-08 established the pattern: minimal additive constants block in `constants.py`, sync rule documented in CLAUDE.md, no new module. Phase 34 follows verbatim. The host catalog (`messages.py`) is auto-generated and stays untouched per D-09; `serial_comm.py` MSG_OK_REV formatting can consume the new constants symbolically per D-05 (cosmetic, not wire shape).

### GA-8: Operator-on-bench wave — required gate vs optional sanity-check vs deferred

**Auto-resolution → D-10: deferred to Phase 35. Phase 34 ships desk-side close.**

**Rationale:** v1.7 roadmap §Branch model: "Promote sub-repos `v1.7-shield-investigation` → `beta` only after Phase 34 firmware-detect lands; `beta` → `main` only after operator confirms firmware handshake reports correctly on at least one bench-present rev." This sequences operator validation to Phase 35 close, not Phase 34 close. Phase 34's optional operator-on-bench wave (roadmap §Status text) is a nice-to-have, not a gate.

---

## Scope-Creep Avoidance

Three items raised during analysis that could have inflated scope; all caught and deferred:

1. **Designing a Rev 2.4 with finer per-rev bands** (4k7 → 6k8 → 10k → 15k progression) — would let firmware distinguish Rev 2.1 from 2.2 from 2.3 by ADC alone. Out of v1.7: requires new PCB + operator validation.
2. **8-sample `analogRead` averaging** for noise robustness — would inflate code change beyond minimum needed for the band-separation math. Left to Claude's Discretion; planner adds only if D-03 tolerance math requires.
3. **`firestarter dev detect-rev` host subcommand** — diagnostic for the open Phase 35 follow-up #5 (R41 4k7-vs-10k measurement). Useful but not load-bearing for Phase 34 close. Left to Claude's Discretion; opportunistic add.

---

## Deferred Ideas Captured

See `34-CONTEXT.md` `<deferred>` section. Notable items:

- Phase 35: operator-on-bench validation; §9 row update for Modified Rev 0; README cross-links
- Post-v1.7: runtime capability guards; native-test coverage for rurp_hw_rev_utils.h; codegen MSG_OK_DETECTED_REV
- Out of v1.7: Rev 2.4 fine-grain bands; external pull-up; per-board MCU pull-up calibration

---

## Canonical Refs Accumulated

See `34-CONTEXT.md` `<canonical_refs>` section. Spans:
- 7 project planning files (ROADMAP, REQUIREMENTS, STATE, PROJECT, codebase/{STRUCTURE,CONVENTIONS,CONCERNS})
- 7 §-anchored references in `.planning/v1.7-SHIELD-REVS.md` (§1, §3, §4, §6, §7, §8, §9)
- 3 prior-phase CONTEXT.md / SUMMARY artifacts (31, 32, 33)
- 9 firmware source-of-truth file:line anchors
- 5 host CLI source-of-truth file:line anchors
- 5 memory entries
- 2 sub-repo CLAUDE.md files

---

## Outcome

CONTEXT.md written with 11 D-NN decisions + 5 Claude's Discretion items + 5 deferred-idea categories. Phase 34 is ready for `/gsd-plan-phase 34`. Planner should expect a 3-wave decomposition (§8/§9 fill on meta-repo → firmware enum + detect rework on `firestarter` → Python parity on `firestarter_app`).

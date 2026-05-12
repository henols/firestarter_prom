# Phase 4: Hardware Validation (RURP shield) — Context

**Gathered:** 2026-05-12
**Status:** Ready for planning (research complete; CONTEXT.md updated 2026-05-12 with RESEARCH.md corrections — see "Research-Led Corrections" below)
**Source:** /gsd-discuss-phase 4 (recommendations mode — user accepted all 7 recommended defaults; supplied physical-parts inventory) + /gsd-plan-phase 4 (gsd-phase-researcher findings folded in)

## Research-Led Corrections

After CONTEXT.md was authored, `gsd-phase-researcher` surfaced two load-bearing corrections to original decisions. These have been folded INTO the relevant D-NN sections below — the original wording is preserved with a clearly marked "RESEARCH.md-corrected" amendment. Planner should treat the corrected wording as authoritative.

| # | Decision | Original framing | Correction | Why it matters |
|---|----------|------------------|------------|----------------|
| D-01 | HW-01 scope | 2-line filename sed (WARNING-4 only) | Also fix jq-query schema drift (kebab-case top-level → nested) at `firestarter_test.sh:48-67` + `write_test.sh:35-40` | Without the jq fix, the scripts would still fail even with corrected filenames — the bench validation gate (success criterion #1) is missed |
| D-05 | HW-05 abort mechanism | Lower regulator via `firestarter config` (which doesn't expose a VPP setpoint) | Override `vpp_mv` in `~/.firestarter/database.json` to 8000 mV — VPP HIGH ERROR branch fires (asymmetric check at `flash_intel.cpp:39-48`) | Lowering measured VPP only trips the WARN branch; the abort is on the HIGH side. Original mechanism would have produced no abort and silently passed |



<domain>
## Phase Boundary

**In scope:**
- HW-01 — Repair `firestarter_test.sh` + `write_test.sh` so they reference the post-Phase-11 DB filename (`chip_database.json`) and any other paths that drifted (closes WARNING-4).
- HW-02 — Physical RURP-shield write + verify + read of a W27C512 (algo=0x07, UV-EPROM); logged.
- HW-03 — Physical RURP-shield write + verify of an AM29F040 (algo=0x06, chip-erase) AND an SST39SF040 (algo=0x06, sector-erase); both logged.
- HW-04 — Physical RURP-shield write + verify of an AT28C256 (algo=0x0D via Phase 13 override) with multimeter confirmation that P1_VPP never engages during the write window; logged.
- HW-05 — Physical RURP-shield write + verify of an AM28F010 (algo=0x10) PLUS a deliberate underpowered-VPP run that must abort cleanly (SAF-04 closure verified on hardware); logged.

**Out of scope (deferred or owned elsewhere):**
- WARNING-5 generalisation (AT28C256/64 upstream-DB classification fix) — deferred to v1.2.
- INFO-3 (DIP28/DIP32 quirk-pin `static-high-pins` coverage) — deferred to v1.2 / FW-07.
- New firmware features. If a bench failure surfaces a firmware bug, file as a new requirement (FW-NN) and replan; do not in-line fix in this phase.
- Phase 5 (DOC-01) MILESTONES.md v1.1 entry — Phase 5 cross-references `04-HW-VALIDATION.md`.

**Sub-repo scope (D-13 commit atomicity):**
- HW-01 modifies `firestarter_app/firestarter_test.sh` + `firestarter_app/write_test.sh` only — both in the `firestarter_app/` sub-repo, single atomic commit.
- HW-02..HW-05 write **no source code**; they exercise the live firmware + Python CLI and write only `.planning/phases/04-hardware-validation-rurp-shield/04-HW-VALIDATION.md` (one consolidated file with 5 H2 sections, one per HW-NN).
</domain>

<spec_lock>
## Locked Requirements (from ROADMAP.md Phase 4)

The ROADMAP success criteria are the gate for this phase. Verbatim:

1. `firestarter_test.sh` and `write_test.sh` run cleanly against the current `chip_database.json` — no references to the deleted `database_generated.json` remain (WARNING-4 closed).
2. A physical RURP shield programs and verifies a W27C512 (algo=0x07, UV-EPROM) via `firestarter write` then `firestarter read --verify`, with results logged.
3. A physical RURP shield programs and verifies an AM29F040 (chip-erase + write) and an SST39SF040 (sector-erase + write), both algo=0x06, with results logged.
4. A physical RURP shield programs and verifies an AT28C256 (algo=0x0D via Phase 13 override) with scope/multimeter confirmation that the VPP regulator never engages during the write window.
5. A physical RURP shield programs and verifies an Intel-family flash (AM28F010 or 28F256, algo=0x10) and confirms the new SAF-04 VPP ADC compare aborts a deliberately-underpowered VPP run.

User-supplied physical-parts inventory (2026-05-12):
- W27C512 ✓ — HW-02 baseline
- AM29F040 ✓ — HW-03 chip-erase half
- SST39SF040 ✓ — HW-03 sector-erase half
- AT28C256 ✓ — HW-04 5V invariant test
- AM28F010 ✓ — HW-05 SAF-04 abort test (Intel-compat AMD per ROADMAP wording)
</spec_lock>

<decisions>
## Implementation Decisions (locked, in recommendation order)

### D-01 — HW-01 ships as its own plan in Wave 1 (software-only, no bench dep)
HW-01 is software-only test-script repair. Plan 04-01 ships HW-01 in isolation so it unblocks immediately (no bench access required) and so Plan 04-02 (bench work) inherits a known-clean test-script state. Bench is single-resource (one chip per RURP socket); software work must not block on it.

**Scope (RESEARCH.md-corrected, 2026-05-12):** HW-01 is bigger than two filename `sed` fixes. The 2 dead `database_generated.json` references at `firestarter_app/firestarter_test.sh:31` and `firestarter_app/write_test.sh:17` are real (WARNING-4), but the scripts ALSO use a jq query schema that does not match the post-Phase-11 `chip_database.json` shape. Specifically, the scripts query the OLD flat top-level keys `.["memory-size"]`, `.["has-chip-id"]`, `.["can-erase"]`, `.["name"]` at `firestarter_test.sh:48-67` and `write_test.sh:35-40`. The new DB is `{manufacturer: [chips...]}` with nested `.electrical.size_bytes`, `.programming.chip_id_check`, `.part_number`. HW-01 fixes BOTH layers:
  1. `JSON_FILE` filename flip (`database_generated.json` → `chip_database.json`).
  2. jq query rewrite to the new nested schema (flatten across manufacturers + nested path lookups).

Planner authors both as a single sub-repo commit per D-08 (one atomic `firestarter_app/` commit covering both repair layers). Pre-fix `bash -n` syntax-check is the dry-run gate; post-fix `jq` smoke against the live DB is the acceptance gate (planner picks a known chip name, looks it up, asserts non-empty result).

### D-02 — Three plans total; HW-NN grouped by execution rhythm
- **Plan 04-01 = HW-01** (Wave 1) — software-only test-script repair.
- **Plan 04-02 = HW-02 + HW-03 + HW-04** (Wave 2) — three canon chip families that share the "well-trodden bench loop" rhythm (write → verify → read → xxd-diff). HW-04 adds the multimeter step but the bench setup is the same.
- **Plan 04-03 = HW-05** (Wave 3) — distinct because the SAF-04 abort sub-test changes the bench rhythm (configure under-voltage → run → expect abort → restore voltage → run again → expect pass).

Rejected alternatives: 5 plans (one per HW-NN) would inflate orchestration overhead for what is sequentially-gated work; 1 plan (all-in-one) loses bench-resume points for the natural overnight breaks between chip families.

### D-03 — One consolidated `04-HW-VALIDATION.md` with 5 H2 sections
Output artifact path: `.planning/phases/04-hardware-validation-rurp-shield/04-HW-VALIDATION.md`. Structure:
- H1 — phase + date
- H2 §1 (HW-01) — test-script repair record (commit hashes, before/after diff, dry-run output)
- H2 §2 (HW-02) — W27C512 bench run
- H2 §3 (HW-03) — AM29F040 + SST39SF040 bench runs (sub-headings per chip)
- H2 §4 (HW-04) — AT28C256 + multimeter trace
- H2 §5 (HW-05) — AM28F010 normal run + SAF-04 abort run

Rationale: matches the `v1.0-INTEGRATION-CHECK.md` precedent (single file, per-row evidence). Phase 5 (DOC-01) cross-references one file, not five. Each H2 section is independently authorable across days/plans.

### D-04 — HW-04 multimeter is sufficient; scope optional
ROADMAP success criterion 4 reads "scope/multimeter" — disjunction. The binary question is "did P1_VPP engage at all during the AT28C256 write window?" A handheld DMM at socket pin 1 (DIP28 P1 = VPP rail) reading 0 V continuously throughout `firestarter write` satisfies the gate. Scope adds engage/disengage edge timing, which is informative but not required for the SAF-03-cross-handler-style invariant Phase 4 is testing.

Captured in `04-HW-VALIDATION.md §4`: meter model, measurement points (P1_VPP socket pin + reference GND), reading at write-start, reading mid-write, reading at write-end. Scope screenshot optional addendum.

### D-05 — HW-05 underpowered VPP via DB override of AM28F010 `vpp_mv` (RESEARCH.md-corrected mechanism)
**Mechanism correction (2026-05-12):** The original D-05 proposed `firestarter config` to lower the VPP regulator setpoint, but RESEARCH.md established two load-bearing facts:

1. **`firestarter config` does not expose a VPP setpoint.** Its only writable args are `--rev`, `-r1`, `-r2` (board revision + resistor calibration). There is no VPP-related setpoint command.

2. **`flash_intel_check_vpp` at `flash_intel.cpp:25-50` is asymmetric on purpose** — verified verbatim live:
   - `vpp_mv > handle->vpp_mv + 500` → **ERROR** (or warning under `FLAG_FORCE`) — aborts the write.
   - `vpp_mv < handle->vpp_mv * 95 / 100` → **WARNING only** (`firestarter_warning_response_format`) — the write continues.

   Lowering the regulator's measured output (reducing `vpp_mv`) would only trip the WARNING branch — the write would proceed and HW-05 would not validate the SAF-04 abort path.

**Corrected mechanism — DB override of `handle->vpp_mv`:** Keep the regulator nominal (~12 V measured) but provide an AM28F010 override in `~/.firestarter/database.json` with `vpp_mv: 8000` (8 V). Then measured 12 V > 8000+500 = 8500 mV → **VPP HIGH ERROR** branch fires → clean abort.

Sub-runs:
1. **Sub-run A — underpowered (must abort):** Drop override `~/.firestarter/database.json` containing `{"manufacturer": [{"part_number": "AM28F010", ..., "electrical": {..., "vpp_mv": 8000, ...}, ...}]}` (full chip spec with the single `vpp_mv` field reduced). Run `firestarter write AM28F010 testbin.bin`. Expect `ERROR: VPP is high: 12.0V > 8.0V` (verbatim format from `flash_intel.cpp:41-43`) + cleared regulator/P1_VPP_ENABLE.
2. **Sub-run B — nominal (must pass):** Remove the override (or restore `vpp_mv: 12000`). Run `firestarter write AM28F010 testbin.bin` + `firestarter verify AM28F010 testbin.bin` + `firestarter read AM28F010 readback.bin`. Expect `OK:` + 0-byte `xxd` diff.

Both runs captured in `04-HW-VALIDATION.md §5`. The two-run contrast (abort + pass) is the load-bearing evidence — a single abort run alone could be masked by an unrelated regulator failure.

Captured signature (planner greps for in HW-05 log evidence): `ERROR: VPP is high:` substring on Sub-run A; `OK:` + 0-byte diff on Sub-run B.

Rejected: original `firestarter config` mechanism (no such command); physical underpowering (rewiring risk, not reversible); FLAG_FORCE bypass (would convert the ERROR back to a WARNING, defeating the abort test). The DB-override mechanism is repeatable (just drop/remove a JSON file), reversible (delete the override file), and exercises the actual production code path (every byte of `flash_intel_check_vpp` runs).

### D-06 — Per-chip evidence schema
Each H2 section in `04-HW-VALIDATION.md` carries:
- **Chip header:** part number, lot/date marking (if visible), package (DIP24/28/32), algorithm (0x07/0x06/0x0D/0x10), DB entry name (verbatim from `chip_database.json`).
- **Date/time:** ISO 8601, host machine, board (Uno vs Leonardo), firmware version, app version.
- **Terminal log:** fenced ```text``` block, full stdout+stderr of the `firestarter <cmd>` invocation, exit code at end.
- **Binary diff:** `xxd` output of source bin vs `firestarter read` bin (or "0 bytes differ" line + size assertion).
- **Voltage readings (HW-04 + HW-05 only):** meter model, probe points, readings at time-stamps.
- **Photo (optional):** linked file path (committed under `.planning/phases/04-hardware-validation-rurp-shield/photos/`) — bench setup + chip in socket.
- **Verdict line:** `PASS` / `FAIL` + one-sentence interpretation.

Failure logs are still captured (not omitted) — see D-07.

### D-07 — Failure policy: investigate, may replan, does not auto-block phase close
A bench `FAIL` at HW-NN is captured in `04-HW-VALIDATION.md §N` with full diagnostic detail, then triaged:
- **Firmware bug:** file a new requirement (e.g. FW-08), add it to REQUIREMENTS.md, replan Phase 4 to include the fix, re-run the failing chip. Phase 4 does not close until the fix lands.
- **Chip-specific issue (dead chip, mis-marked part, wrong package):** document substitute (e.g. swap AM29F040 from a different vendor), retry; if no substitute available, document the chip as deferred-to-v1.2 with the specific failure mode. Phase 4 closes on the substitute or with the documented deferral.
- **Operator error (wrong socket adapter, missed power cycle, stale flash binary):** retry with corrected procedure; do not document as a failure in the final artifact.

The point is to distinguish "v1.1 firmware is broken on this chip" from "this individual chip is broken" — only the first blocks phase close.

### D-08 — Atomic commit protocol (continues D-13 from Phases 1-3)
Per the v1.1 atomic-commit pattern:
- HW-01 lands as **one** `firestarter_app/` sub-repo commit touching both `.sh` files (`fix(test-scripts): point at chip_database.json per WARNING-4 closure`) plus an immediate-follow meta-repo commit `docs(04-01): HW-01 SUMMARY + 04-HW-VALIDATION.md §1`.
- Each HW-NN bench run gets its own meta-repo commit `docs(04-NN): HW-NN bench run — <chip>` appending the relevant H2 section to `04-HW-VALIDATION.md`. Plan SUMMARYs (`04-02-SUMMARY.md`, `04-03-SUMMARY.md`) commit separately at plan close.

### D-09 — Sub-repo coordination for HW-01
The `firestarter_app/` sub-repo edit (HW-01 test-script fix) follows the cross-sub-repo coordination pattern established in v1.1 Phase 2 (Plan 02-01 firmware-first, app-second). HW-01 is app-only — no firmware change — so the cross-sub-repo concern doesn't apply. Single sub-repo commit suffices.

### D-10 — Bench-resume points (overnight-friendly)
Hardware work is single-threaded (one RURP socket, one chip at a time) and slow (each chip family ≈ 15-30 min including socket cleaning, photo, log capture). Plan 04-02 may execute across multiple sessions. Each HW-NN H2 section is independently committable; resume = re-read `04-HW-VALIDATION.md` to see which sections are filled in.

### D-11 — Re-validation policy (out-of-band)
If a Phase 1 fix or Phase 2 wire-key rename gets re-touched after Phase 4 ships, the bench runs in `04-HW-VALIDATION.md` are still **valid** unless the firmware or wire protocol changes substantively. Re-validation is triggered by changes to:
- Any function under `flash_intel.cpp` or `eeprom_28c.cpp` (HW-04 + HW-05 chip-id / VPP paths)
- `mem_util_blank_check`, `mem_util_remap_address_bus`, or `mem_util_calculate_top_address_register` in `memory.cpp` (all bench runs)
- The `bus_config_t` struct in `firestarter.h` or any wire field in `json_parser.c`

If re-validation is needed, append a `Re-validation` subsection to the relevant H2; don't overwrite the original run.

### Claude's Discretion
- Exact wording of the abort-error string the host CLI emits on the underpowered HW-05 run — research the `serial_comm.py` `ERROR:` parse path; bench evidence captures whatever the live binary actually emits.
- Whether to also re-execute `pio test` (firmware native unit tests) as part of HW-01 dry-run validation — likely yes (it's been the v1.1 pattern since Plan 01-01) but the test-script repair itself doesn't depend on it; let the planner decide.
- Whether to include a "before HW-01 fix" failing-state log in `04-HW-VALIDATION.md §1` — useful for posterity but not required by ROADMAP success criterion 1; planner's call.
- File-naming convention for photos under `photos/` — leave to planner (likely `HW-NN-<chip>-<timestamp>.jpg`).
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before researching or planning.**

### Phase 4 source-of-truth (ROADMAP + REQUIREMENTS)
- `.planning/ROADMAP.md` (Phase 4 section, lines 68-78) — Success criteria #1-#5 are the verbatim gate
- `.planning/REQUIREMENTS.md` "Hardware Validation" section — HW-01..HW-05 verbatim

### v1.1 prior-phase artifacts (what's already shipped)
- `.planning/STATE.md` (frontmatter + Decisions sections) — D-04 SAF-04, D-05 SAF-05 override, D-13 atomic-commit pattern
- `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-VERIFICATION.md` — Truth #1 + #3 (SAF-04 `flash_intel_check_vpp` evidence cited by HW-05)
- `.planning/milestones/v1.0-phases/05-intel-flash/05-VERIFICATION.md` — Cross-Milestone Closure REQ-SAF-01 subsection (the closure HW-05 will validate on hardware)
- `.planning/milestones/v1.0-phases/13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we/13-VERIFICATION.md` — AT28C256 5V invariant evidence (the override HW-04 validates)
- `.planning/phases/03-retroactive-verification-phases-01-10/03-LEARNINGS.md` — pattern library (grep-at-write-time, 5-field follow_ups schema, per-VERIFICATION.md atomic commit)

### Live source-tree files HW-01 modifies
- `firestarter_app/firestarter_test.sh` (line 31: `JSON_FILE='./firestarter/data/database_generated.json'`)
- `firestarter_app/write_test.sh` (line 17: same broken reference)
- Live target: `firestarter_app/firestarter/data/chip_database.json` (renamed by v1.0 Phase 11 / CLEAN-01; verified live)

### Live source-tree files HW-02..HW-05 exercise (do NOT modify — read only)
- `firestarter/src/proms/flash_intel.cpp` — `flash_intel_check_vpp:25-50`, `flash_intel_write_init:77` (HW-05 SAF-04 abort path)
- `firestarter/src/proms/eeprom_28c.cpp` — `eeprom28c_check_chip_id:55-77`, write path (HW-04 5V invariant)
- `firestarter/src/proms/memory.cpp` — `:72` Intel dispatch (HW-05), `:77` 28C dispatch (HW-04), `:82-85` 0x06 flash3 dispatch (HW-03), `:92-95` UV-EPROM dispatch (HW-02), `:140` `pins < 32` guard
- `firestarter_app/firestarter/data/chip_database.json` — DB entries for W27C512, AM29F040, SST39SF040, AT28C256, AM28F010

### Codebase maps (read for bench rhythm + test-script structure)
- `.planning/codebase/TESTING.md` — current state of test-script ergonomics + hardware-dependency framing
- `.planning/codebase/STACK.md` — host + board environment, serial baud
- `.planning/codebase/CONCERNS.md` — runtime concerns relevant to bench operation
</canonical_refs>

<specifics>
## Specific Ideas (verbatim sample for downstream agents)

### `04-HW-VALIDATION.md` H2 §1 (HW-01) skeleton — verbatim shape

```markdown
## §1 HW-01 — Test-script repair (WARNING-4 closure)

**Date:** <ISO8601>
**Plan ref:** 04-01
**Commit:** firestarter_app@<hash>

### Before (live broken refs)
- `firestarter_app/firestarter_test.sh:31` — `JSON_FILE='./firestarter/data/database_generated.json'`
- `firestarter_app/write_test.sh:17` — same line, same file

### After (repaired refs)
- both scripts → `JSON_FILE='./firestarter/data/chip_database.json'`
- additional drifted-path repairs (if any) listed below

### Dry-run validation
- Syntax: `bash -n firestarter_test.sh` → exit 0
- Syntax: `bash -n write_test.sh` → exit 0
- DB-lookup smoke: `jq '.' "$JSON_FILE" | head` — well-formed JSON, exit 0
- (Optional, planner's call) `pio test` 25/25 — confirms firmware side unchanged

### Verdict
**PASS** — both scripts parse cleanly against the post-Phase-11 DB filename.
```

### `04-HW-VALIDATION.md` H2 §5 (HW-05) skeleton — abort-run pair

```markdown
## §5 HW-05 — AM28F010 + SAF-04 abort (REQ-SAF-01 Intel closure on hardware)

**Date:** <ISO8601>
**Plan ref:** 04-03
**Board:** <Uno|Leonardo>  **Firmware:** <version>  **App:** <version>
**Chip:** AM28F010, package <DIPNN>, lot <marking>, DB entry `AM28F010`

### Sub-run A — Underpowered VPP (must abort)
- Config: `firestarter config` VPP setpoint = 10000 mV (below Intel ~12000 mV gate)
- Cmd: `firestarter write AM28F010 testbin.bin`
- Expected: `ERROR:` line + abort code + regulator/P1_VPP_ENABLE cleared per CR-01
- Captured terminal log:
  ```text
  ...
  ```
- Multimeter at P1_VPP during abort window: <reading> V
- **PASS** — `flash_intel_check_vpp` aborted on the underpowered run.

### Sub-run B — Nominal VPP (must pass)
- Config: `firestarter config` VPP setpoint = 12000 mV (restored)
- Cmd: `firestarter write AM28F010 testbin.bin` then `firestarter read AM28F010 readback.bin --verify`
- Expected: `OK:` + 0-byte xxd diff
- Captured terminal log:
  ```text
  ...
  ```
- Multimeter at P1_VPP during write window: <reading> V (expect ≥ 11.5)
- **PASS** — nominal-VPP write + verify exit 0; binary diff clean.

### Verdict
**PASS** — SAF-04 closure verified on hardware: under-voltage aborts, nominal-voltage passes.
```

### HW-VALIDATION.md frontmatter (top of file)

```yaml
---
phase: 04-hardware-validation-rurp-shield
generated: <ISO8601>
requirements_validated: [HW-01, HW-02, HW-03, HW-04, HW-05]
hardware:
  board: <Uno|Leonardo>
  firmware_version: <version>
  host_machine: <hostname>
  bench_equipment:
    - Multimeter: <model>
    - Power supply: <model, if not RURP-onboard>
chips_tested:
  - {part: W27C512,    algo: 0x07, package: DIP28, lot: <marking>}
  - {part: AM29F040,   algo: 0x06, package: DIP32, lot: <marking>}
  - {part: SST39SF040, algo: 0x06, package: DIP32, lot: <marking>}
  - {part: AT28C256,   algo: 0x0D, package: DIP28, lot: <marking>}
  - {part: AM28F010,   algo: 0x10, package: DIP32, lot: <marking>}
follow_ups: []
---
```
</specifics>

<deferred>
## Deferred Ideas

- **Scope-trace addendum to HW-04** — multimeter is sufficient per D-04, but scope screenshots are valuable for v1.2 documentation if the user has a scope on the bench during HW-04 execution. Capture if convenient; do not block.
- **Photo / video evidence for milestone story** — optional in D-06; Phase 5 (DOC-01) MILESTONES.md v1.1 entry will benefit from one good bench photo per chip family. Capture during HW-02..HW-05 if convenient.
- **CI-friendly bench-runner script** — re-running the bench validation across firmware revisions would benefit from a script that drives the chip families in sequence with prompts. Out of scope for v1.1; consider for v1.2 if the bench cadence justifies tooling investment.
- **Sub-repo CLAUDE.md update referencing `04-HW-VALIDATION.md`** — once Phase 4 closes, `firestarter_app/CLAUDE.md` should cite the hardware-verified chips. Phase 5 (DOC-01) owns this update, not Phase 4.
- **AT28C256 chip-ID population** — making the SAF-05 helper non-vacuous for AT28C-family chips requires populating `chip_id_value` in the DB. Deferred to v1.2 per WARNING-5 carry-forward (already documented in `03-LEARNINGS.md` §"WARNING-5 follow_up tailored per phase").
- **Multi-board cross-check (Uno vs Leonardo)** — running HW-02..HW-05 on both boards would catch board-specific data-buffer differences (Uno 512B vs Leonardo 1024B). Not in ROADMAP success criteria; planner's discretion if user has both boards available.
</deferred>

---

*Phase: 04-hardware-validation-rurp-shield*
*Context gathered: 2026-05-12 via /gsd-discuss-phase 4 (recommendations mode)*
*All 7 recommendations accepted by user; parts inventory confirmed (5/5 chips on hand).*

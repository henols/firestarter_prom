# Phase 4: Hardware Validation (RURP shield) — Discussion Log

**Date:** 2026-05-12
**Mode:** /gsd-discuss-phase 4 — recommendations mode ("and recommend")
**Outcome:** All 7 recommendations accepted; parts inventory confirmed; ready for research + planning.

## Gray Areas Identified

Phase 4 is purely-physical hardware validation work. The ROADMAP success criteria (#1-#5) lock the WHAT precisely. Gray areas are entirely about HOW and WHEN — plan structure, evidence schema, abort-test method, failure handling.

### 1. HW-01 plan split — separate or bundled with bench work?

**Options considered:**
- (A) Bundle HW-01 with HW-02..HW-05 in one large plan
- (B) HW-01 as its own Wave 1 plan, bench work in Wave 2+ (RECOMMENDED)

**Recommendation:** (B). HW-01 is software-only (`sed`-class fix on two `.sh` files), completable in minutes without bench access; bundling creates an artificial dependency chain that blocks software-only progress and delays unblocking the bench runs.

**User decision:** Accepted recommendation (B).

---

### 2. Plan count — 1 / 3 / 5?

**Options considered:**
- (A) 1 plan for the whole phase
- (B) 3 plans: 04-01=HW-01; 04-02=HW-02+HW-03+HW-04; 04-03=HW-05 (RECOMMENDED)
- (C) 5 plans, one per HW-NN
- (D) 2 plans: 04-01=HW-01; 04-02=HW-02..HW-05

**Recommendation:** (B). HW-02..HW-04 share a "well-trodden bench loop" rhythm (write→verify→read→xxd-diff) and complete on the same bench setup. HW-05 stands alone because the SAF-04 abort sub-test changes the rhythm (configure under-voltage → expect abort → restore → expect pass). Plan-count >3 inflates orchestration overhead; plan-count <3 loses the natural HW-05 boundary.

**User decision:** Accepted recommendation (B).

---

### 3. `HW-VALIDATION.md` shape — one file or many?

**Options considered:**
- (A) ONE consolidated `04-HW-VALIDATION.md` with 5 H2 sections (RECOMMENDED)
- (B) Per-chip-family files (`HW-VALIDATION-W27C512.md`, etc.)
- (C) Per-requirement files (`04-NN-HW-VALIDATION.md`, matching plan numbering)

**Recommendation:** (A). Matches `v1.0-INTEGRATION-CHECK.md` precedent (single file, per-row evidence). Phase 5 (DOC-01) MILESTONES.md cross-references one artifact, not five. Each H2 is independently authorable across days/plans.

**User decision:** Accepted recommendation (A).

---

### 4. HW-04 evidence — scope or multimeter?

**Options considered:**
- (A) Scope required (engage/disengage edges)
- (B) Multimeter sufficient (RECOMMENDED); scope optional addendum

**Recommendation:** (B). ROADMAP wording is "scope/multimeter" (disjunction). The binary question is "did P1_VPP engage at all during the AT28C256 write window?" A DMM at socket pin 1 reading 0 V continuously satisfies the gate. Scope adds time-resolution but is not required.

**User decision:** Accepted recommendation (B).

---

### 5. HW-05 underpowered VPP — software setpoint or physical underpowering?

**Options considered:**
- (A) `firestarter config` regulator setpoint lowered to ~10 V (RECOMMENDED)
- (B) Bench-supply tap or VPP-rail pulldown resistor (physical)
- (C) Known-defective Intel chip

**Recommendation:** (A). Repeatable, reversible, no rewiring. SAF-04 closure (`flash_intel_check_vpp:25-50`) compares against the configured `handle->vpp_mv`. Two-run contrast (abort + restored-pass) is the load-bearing evidence — captured in `04-HW-VALIDATION.md §5 Sub-run A + B`.

**User decision:** Accepted recommendation (A).

---

### 6. Evidence schema — what counts as "verified" per chip?

**Options considered:**
- Terminal log only
- Terminal log + xxd binary diff
- Terminal log + xxd diff + voltage readings + photo (RECOMMENDED)

**Recommendation:** Maximum-evidence per chip:
- Chip header (part, lot, package, algo, DB entry)
- Date/time, host, board, firmware/app version
- Fenced terminal log (full stdout+stderr + exit code)
- `xxd` diff result (or "0 bytes differ" + size assertion)
- Voltage readings (HW-04 + HW-05 only)
- Photo (optional, linked under `photos/`)
- Verdict line (PASS/FAIL + one-sentence interpretation)

Mirrors `firestarter_test.sh` natural output + adds bench-specific evidence types.

**User decision:** Accepted recommendation.

---

### 7. Failure policy — block or document-and-continue?

**Options considered:**
- (A) Strict block: any bench failure blocks phase close
- (B) Permissive: log all failures, ship phase regardless
- (C) Triage: investigate, may replan, does not auto-block (RECOMMENDED)

**Recommendation:** (C). Distinguishes "v1.1 firmware is broken on this chip" (must fix, file as new FW-NN, replan) from "this chip is dead / mis-marked" (substitute or document deferral). Operator errors are corrected and not logged as failures.

**User decision:** Accepted recommendation (C).

---

## User Information Gathered

### Physical-parts inventory (confirmed 2026-05-12)
- W27C512 ✓
- AM29F040 ✓
- SST39SF040 ✓
- AT28C256 ✓
- AM28F010 ✓ (per ROADMAP wording — Intel-compat AMD)

All 5 canon chips on hand. No substitution or deferral needed.

### Bench equipment
- Multimeter on hand (per D-04 acceptance).
- Scope availability not confirmed — D-04 makes it optional.

---

## Scope Creep Redirected

None — user did not propose scope creep during this discussion. The "and recommend" prompt was purely about resolving locked-in decisions efficiently.

## Deferred Ideas Captured (in CONTEXT.md `<deferred>`)

- Scope-trace addendum to HW-04 (optional, capture if bench-time permits)
- Photo/video evidence for Phase 5 MILESTONES.md story
- CI-friendly bench-runner script (out of scope for v1.1)
- Sub-repo CLAUDE.md update referencing `04-HW-VALIDATION.md` (Phase 5 / DOC-01 owns)
- AT28C256 chip-ID population for non-vacuous SAF-05 (v1.2 / WARNING-5 carry-forward)
- Multi-board cross-check (Uno vs Leonardo) — not in ROADMAP success criteria; planner's discretion

## Claude's Discretion (deferred to research + planner)

- Exact wording of host-CLI `ERROR:` line emitted on the underpowered HW-05 run — research the `serial_comm.py` `ERROR:` parse path.
- Whether to also re-execute `pio test` (firmware native unit tests) as part of HW-01 dry-run validation.
- Whether `04-HW-VALIDATION.md §1` should capture a "before HW-01 fix" failing-state log.
- File-naming convention for `photos/` files.

---

*Discussion log written 2026-05-12 — all decisions captured in `04-CONTEXT.md`.*

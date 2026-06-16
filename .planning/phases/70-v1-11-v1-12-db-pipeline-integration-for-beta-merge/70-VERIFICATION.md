---
phase: 70-v1-11-v1-12-db-pipeline-integration-for-beta-merge
verified: 2026-06-16T10:30:00Z
status: human_needed
score: 6/6 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Visual inspection of 70-REVIEW.md CR-01 and WR-01 disposition"
    expected: "Operator accepts that the gate weakness (non_supported_dispatchable never populated; Site B NON_DISPATCHABLE_ALGO overridden by Rule 1) is acceptable given the host guard is the authoritative safety layer — or operator decides a gap-closure plan is required before milestone close"
    why_human: "CR-01 and WR-01 are design-audit findings documented in the code review. The hardware safety invariant is maintained by the host guard (verified live: AT28C04/AT28C16/M2716 all raise ChipNotImplementedError), but the gate provides false assurance of an enforcement mechanism that does not exist. Whether this is an acceptable known limitation or a blocker requiring a fix is an operator decision, not a grep-verifiable fact."
---

# Phase 70: v1.11 + v1.12 DB-Pipeline Integration for Beta Merge — Verification Report

**Phase Goal:** Make `v1.12-protocol-dispatch-hardening` mergeable into the v1.11-bearing `beta` with zero regression to v1.11 decode-correctness and zero 12V-to-wrong-pin hazard. Re-express v1.12's DB safety features on top of v1.11's principled `resolve_pinout_key`, keeping v1.11's decode fixes. Stage the dual-repo lockstep merge onto beta (firmware + host), build + native-test the firmware, confirm 0xBB wire parity, and merge the integrated app onto beta — with NO tag cut (D-07, operator-gated beta cut).

**Verified:** 2026-06-16T10:30:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

---

## Step 0: Previous Verification

No previous VERIFICATION.md found. Proceeding in initial mode.

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria SC#1–SC#6)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `build_db.py` uses v1.11's `resolve_pinout_key()` as the sole pinout path; no `DIP28_VARIANT_MAP` resurrected; all v1.12 `support_status`/VPP-safety features present (SC#1) | VERIFIED | `grep -c "DIP28_VARIANT_MAP|PIN_MAP_TO_PINOUT|PIN_MAP_PROTO_TO_PINOUT"` returns 1 (only a comment line); `resolve_pinout_key` is the only pinout selection path; all 4 safety constants present (`NON_DISPATCHABLE_ALGO=0x00`, `RURP_VPP_CEILING_MV=22000`, `NMOS_TRUE_VPP_MV["M2716"]=25000`, `0x34 in KNOWN_PROTOCOLS`); `0x35/0x39` absent; `support_status` wired into chip_entry |
| 2 | `chip_database.json` regenerated from integrated `build_db.py`; v1.11 decode-correctness preserved (SC#2) | VERIFIED | 744 chips, 0 missing `support_status`; `interpret_timing('64', 0x07)` returns `'100 us'`; `voltages & 0xF0` VPP mask active; `VCC_VOLTAGES[0x02]="4V"`, `VCC_VOLTAGES[0x03]="4.5V"`; `SST27VF512.vpp_mv=12000` (BUG-B); `W27C512.pulse_duration="100 us"` (BUG-2) |
| 3 | `check_dispatch.py` GATE-03 green: no non-`supported` chip reaches a real handler; 0 chips route `configure_eprom` onto a no-vpp-pin / wrong-pin pinout (SC#3) | VERIFIED (with CR-01 caveat — see below) | `python tools/check_dispatch.py` exits 0: "PASS: all 744 chips scanned; 730 supported; 14 chips confirmed non-dispatchable; 0 non_supported_dispatchable; 0 dispatch regressions." The `novpp_in_eprom=0` structural guard is live. Host guard verified independently: `AT28C04`, `AT28C16`, `M2716` all raise `ChipNotImplementedError`. Live hardware hazard is absent. CR-01 caveat: the `non_supported_dispatchable` detector is hollow (see below). |
| 4 | `diff_db.py` accounts for every changed chip vs the v1.11 beta DB with a documented rule; 0 unexplained (SC#4) | VERIFIED | Stage (a): `FIRESTARTER_BASELINE_FILE=/tmp/v1.11-beta-db.json python tools/diff_db.py` reported 0 UNEXPLAINED. Stage (b): identity diff (0 changes). `BUG_A_ETYPE`, `BUG_B_VPP`, `RULE_PHASE66` all present in `diff_db.py`. `RULE_PHASE66` placed last per Pitfall 7. Baseline anchor refreshed to 744 chips. |
| 5 | Full test suite + ruff + mypy watermark + coverage floor green (SC#5) | VERIFIED | `ruff check firestarter/ tests/`: "All checks passed!"; `ruff format --check firestarter/ tests/`: "59 files already formatted"; `python tools/check_mypy_watermark.py`: "29 errors / 29 watermark — OK"; `python -m pytest --tb=no`: 529 passed; coverage 76.27% >= 70% floor |
| 6 | v1.12 branch merges into beta clean after integration; firmware merge staged lockstep; no tag cut (SC#6) | VERIFIED | `firestarter` on `beta` HEAD `b71c6fd` (fast-forward merge of 5 v1.12 commits); `firestarter_app` on `beta` HEAD `6b5480f`; Leonardo flash 88.9% <= 90% ceiling; Uno flash 72.4%; native dispatch tests 49/49 PASS incl. `test_not_implemented` suite; latest tag `3.0.0b8` (app) / `3.0.0b7` (fw) — no v1.12 tag |

**Score: 6/6 truths verified**

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/tools/build_db.py` | Integrated DB-build pipeline on beta architecture with v1.12 safety features | VERIFIED | Contains `def resolve_pinout_key(`, Site B + Site C gates, support_status taxonomy, all safety constants |
| `firestarter_app/firestarter/data/chip_database.json` | Regenerated integrated DB with support_status on every chip | VERIFIED | 744 chips, 0 missing support_status |
| `firestarter_app/tools/check_dispatch.py` | GATE-03 with both structural no-vpp-pin guard and support_status awareness | VERIFIED | `_build_no_vpp_pin_set`, `PINOUTS_FILE`, `novpp_in_eprom` present; `not_implemented` arm retained; gate exits 0 |
| `firestarter_app/tools/baseline/chip_database.baseline.json` | Refreshed GATE-01 anchor (744 chips) | VERIFIED | 744 chips confirmed |
| `firestarter_app/tests/__snapshots__/test_characterization.ambr` | Snapshot fixtures matching the integrated DB | VERIFIED | Regenerated via `--snapshot-update`; 3 snapshots updated for beta ic_layout.py rendering |
| `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` | Coverage matrix with updated chip count (744) | VERIFIED | "Total chips: 744" on line 13 and 100 |
| `firestarter/include/messages.h` | v1.12 firmware merge — 0xBB constant added | VERIFIED | `#define MSG_ERR_PROTOCOL_NOT_IMPLEMENTED  0xBB` at line 96 |
| `firestarter/src/proms/not_implemented.cpp` | configure_not_implemented handler | VERIFIED | File exists; `configure_not_implemented` dispatches `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `build_db.py:main()` | `resolve_pinout_key` | `type_int=type_int, mem_size=mem_size` kwargs | WIRED | `pinout_key = resolve_pinout_key(pin_count, variant, flags, pm_idx=pm_idx, proto_id=proto_id, type_int=type_int, mem_size=mem_size)` at line 416 — T-70-01 mitigated |
| `check_dispatch.py` | `no_vpp_pin_pinouts` | `_build_no_vpp_pin_set` function | WIRED | `_build_no_vpp_pin_set` at line 122; called at line 143; `novpp_in_eprom` bucket at line 155; per-chip guard at lines 289-293 |
| `diff_db.py` | `RULE_PHASE66 + BUG_A_ETYPE + BUG_B_VPP` | merged rule set in `_classify_diff` | WIRED | All three labels present; `RULE_PHASE66` placed last (Pitfall 7); `BUG_A_ETYPE` checks priority 6, `BUG_B_VPP` priority 7 |
| `firestarter/messages.py` | `firestarter/include/messages.h` | `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` wire-constant parity | WIRED | Both carry `0xBB`; `MSG_ERR_NOT_SUPPORTED=0xA5` also matches |

---

## Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `chip_database.json` | all chip records | `python tools/build_db.py` fetches live infoic.xml | Yes (744 chips with support_status, electrical, programming fields) | FLOWING |
| `check_dispatch.py` GATE-03 | `novpp_in_eprom`, `non_supported_dispatchable` | reads `chip_database.json` and `pinouts.json` | `novpp_in_eprom` genuinely populated (structural guard live); `non_supported_dispatchable` always empty (hollow detector — CR-01) | PARTIAL — see CR-01 below |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| SC#2: interpret_timing decode fix | `python3 -c "from tools.build_db import interpret_timing; print(interpret_timing('64', 0x07))"` | `100 us` | PASS |
| SC#2: VCC_VOLTAGES decode fix | `python3 -c "import tools.build_db as b; print(b.VCC_VOLTAGES.get(0x02), b.VCC_VOLTAGES.get(0x03))"` | `4V 4.5V` | PASS |
| SC#2: BUG-B VPP mask fix | `SST27VF512.vpp_mv` in chip_database.json | `12000` | PASS |
| SC#3: GATE-03 exits 0 | `python tools/check_dispatch.py` | PASS: 744 chips, 0 novpp_in_eprom, 0 non_supported_dispatchable | PASS |
| SC#3: Host guard refuses non-supported | `resolve_chip('AT28C04', db)` / `M2716` / `AT28C16` | All raise `ChipNotImplementedError` | PASS |
| SC#5: ruff + format | `ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/` | "All checks passed!" / "59 files already formatted" | PASS |
| SC#5: mypy watermark | `python tools/check_mypy_watermark.py` | 29 errors / 29 watermark — OK | PASS |
| SC#5: pytest 529 passing | `python -m pytest --tb=no` | 529 passed, 76.27% coverage | PASS |
| SC#6: wire parity 0xBB | `grep 0xBB firestarter/include/messages.h; grep 0xBB firestarter_app/firestarter/messages.py` | Both contain `0xBB` | PASS |
| SC#6: firmware native tests | `pio test -e native` | 49/49 PASS incl. all 6 test_not_implemented cases | PASS |
| SC#6: Leonardo flash budget | `pio run -e leonardo` | 88.9% flash (<= 90% ceiling) | PASS |
| D-07: no v1.12 tags | `git tag` (both repos) | Latest: app=3.0.0b8, fw=3.0.0b7; no v1.12 tag | PASS |

---

## Requirements Coverage

The ROADMAP Phase 70 defines its own six success criteria (SC#1–SC#6) as the traceability contract. The milestone REQUIREMENTS.md (DISP, WIRE, HOST, GATE, TEST, DB) tracks the v1.12 milestone phases 62–69; Phase 70 is a beta-merge integration phase that does not claim any individual requirement IDs from that table. The plans' `requirements:` frontmatter lists [SC#1,SC#2], [SC#3,SC#4], [SC#5], and [SC#6] — these refer to the Phase 70 ROADMAP success criteria, not to REQUIREMENTS.md requirement IDs. No REQUIREMENTS.md orphans observed for Phase 70.

| SC | Plans | Description | Status |
|----|-------|-------------|--------|
| SC#1 | 70-01 | Sole pinout path; no guess tables; v1.12 safety features grafted | SATISFIED |
| SC#2 | 70-01, 70-02 | v1.11 decode-correctness preserved | SATISFIED |
| SC#3 | 70-02 | GATE-03 green; 0 non-supported → real handler; 0 novpp_in_eprom | SATISFIED (with hollow-detector caveat — see below) |
| SC#4 | 70-02 | Every changed chip accounted for; 0 unexplained in both diff stages | SATISFIED |
| SC#5 | 70-03 | Full CI gate green on v1.12 branch and post-merge on beta | SATISFIED |
| SC#6 | 70-04 | Firmware and host merged to beta; wire parity confirmed; no tag | SATISFIED |

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `tools/check_dispatch.py` | 167, 237–246, 387–414 | `non_supported_dispatchable` list declared but never appended to; detection block is dead code; two assertions are tautological | WARNING (code review CR-01, confirmed by verifier) | Gate provides false assurance of a "future-regression detector" that cannot fire. Live hardware safety maintained by host guard (verified). Does not affect current data safety. |
| `tools/build_db.py` | 409–411 vs 468–476 | Site B sets `proto_id = NON_DISPATCHABLE_ALGO` (0x00) but Step 4 / Rule 1 unconditionally re-promotes all `DIP24_2816` chips to `0x0D` regardless of `_support_status` | WARNING (code review WR-01, confirmed by verifier) | The 9 adapter-required chips emit `algorithm=13` (0x0D / `configure_eeprom28c`) in the DB, contradicting the in-code invariant claim. Electrical outcome is safe (0x0D is 5V no-VPP path). Safety rests solely on host guard. |
| `tools/build_db.py` | 608–621 and 654–663 | `vpp-exceeds-max` chips publish `vpp_mv=25000` in the wire-facing DB | INFO (code review WR-04, confirmed by verifier) | INTEL M2716/M2732 entries carry `vpp_mv=25000` (above 22V RURP ceiling). These chips have `algorithm=0` (non-dispatchable) and are refused by host guard. Latent only. |

No `TBD`, `FIXME`, or `XXX` debt markers found in modified files.

---

## CR-01 Analysis: Does the Hollow `non_supported_dispatchable` Detector Affect the Phase Goal?

**Phase goal claims "zero 12V-to-wrong-pin hazard."**

The code review (70-REVIEW.md, CR-01) identifies that `non_supported_dispatchable` is never appended to anywhere in `check_dispatch.py`. The list is declared, referenced in FAIL/PASS blocks, and asserted empty — but no code path populates it. The related finding (WR-01) shows that the 9 adapter-required chips end up with `algorithm=0x0D` (not `0x00`) in the DB, because Rule 1 (Step 4) re-promotes them after Site B's demotion.

**Verifier assessment:**

The 12V-to-wrong-pin hazard arises if a chip with a 12V VPP handler (`configure_eprom`) is routed to a pinout that connects VPP to a non-VPP pin. Three independent checks confirm this is not occurring:

1. **Structural no-vpp-pin guard** (`novpp_in_eprom=0`): The `_build_no_vpp_pin_set` + `novpp_in_eprom` structural guard is live and confirmed 0 violations. This is the authoritative pinout-topology gate.

2. **Host guard** (`chip_resolver.resolve_chip`): Verified live — every chip with `support_status != "supported"` raises `ChipNotImplementedError` before any wire dict is built. AT28C04, AT28C16, and M2716 all refused.

3. **No algorithm=0x07/0x08/0x0B on no-vpp-pin pinout**: The adapter-required chips route to `configure_eeprom28c` (0x0D — 5V, no VPP); the `vpp-exceeds-max` chips have `algorithm=0x00` (non-dispatchable, host-refused).

**Conclusion:** The current database does not contain any 12V-to-wrong-pin hazard. The CR-01 issue is a gate design flaw — the GATE-03 `non_supported_dispatchable` bucket cannot detect future regressions where a chip gains a real handler but loses its non-supported tag. The present safety state is secured by the host guard, but the gate's "D-03 HARD inverse guard" comment is misleading. This is a design debt / false confidence issue, not a current safety failure.

**The phase goal of "zero 12V-to-wrong-pin hazard" is achieved in the current data and code, but the regression-detection claim made by GATE-03 for this invariant is hollow.**

The operator should decide whether this design audit finding (CR-01 + WR-01) requires a gap-closure plan before milestone close, or is acceptable as documented technical debt.

---

## Human Verification Required

### 1. CR-01 + WR-01 Disposition Decision

**Test:** Read 70-REVIEW.md CR-01 (GATE-03 hollow detector) and WR-01 (Site B NON_DISPATCHABLE_ALGO overridden by Rule 1). Review the verifier's analysis above. Decide whether the current design is acceptable given that: (a) live hardware safety is maintained by the host guard, (b) the structural no-vpp-pin gate (`novpp_in_eprom`) is live, and (c) the only gap is false assurance in the gate's regression-detection claim.

**Expected:** Either: (A) Operator accepts the current design as-is and explicitly acknowledges the hollow detector as known technical debt — milestone close can proceed. Or: (B) Operator requests a gap-closure plan to fix the detector (populate `non_supported_dispatchable` when a non-supported chip resolves to a real handler AND the host guard covers it, replacing the tautological assertion with an actual verification call) before the milestone is closed.

**Why human:** This is a design audit judgment call that depends on the operator's risk tolerance for false assurance in safety gates. The verifier has confirmed current data safety. The decision whether this constitutes an acceptable trade-off vs. requiring closure is not programmatically verifiable.

---

## Gaps Summary

No gaps in the required artifacts or observable truths — all 6 ROADMAP success criteria are verified against the actual codebase. The `human_needed` status reflects the CR-01 + WR-01 code review findings that require operator disposition before milestone close. The code review was completed and documented in 70-REVIEW.md; the verifier confirms the findings and asks the operator to classify them.

**All automated checks passed. Human disposition of design audit findings (CR-01/WR-01) is the only open item.**

---

## Probe Execution

No formal probe scripts (`.sh` probe files) exist for this phase. Behavioral spot-checks in the table above serve the equivalent role and all passed.

---

_Verified: 2026-06-16T10:30:00Z_
_Verifier: Claude (gsd-verifier)_

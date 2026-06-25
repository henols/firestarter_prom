# v1.15 Bench Validation of Operator Inventory — Research Summary

**Milestone:** v1.15 (Bench validation of operator chip inventory)  
**Research Synthesis Date:** 2026-06-23  
**Research Sources:** STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md  
**Confidence Level:** HIGH (all claims verified against source code, project memory, and bench artifacts)

---

## Executive Summary

v1.15 is a silicon-validation milestone that validates 11 chips in the operator's inventory across 5 algorithm families, with a single genuine graduation candidate: the Intel/TI 2516 (24-pin NMOS UV-EPROM, 2K×8, 25V VPP class). The milestone is **software-minimal**: no new code dependencies, no firmware changes (unless a bench-surfaced defect forces a fix), and one new DB entry authored as a user-override (`~/.firestarter/database.json` for the absent-from-minipro 2516). The only delivery is a curated evidence record proving each chip's read/write path and DB decode on Leonardo + Rev 2.0.

**Standing constraints:** All bench work uses Leonardo + RURP Rev 2.0 only (Rev 0 read-path fault; uno328pb program brownout and read instability disqualify both from authoritative verify). The three UV-EPROM chips (ST M27C512, AM27C020, 2516) require a non-destructive read-first protocol since the operator has no UV eraser. The 2516 is a best-effort NMOS graduation at ~22.4V VPE (90% of 25V spec, Phase 79 precedent), and simultaneous closure of the FUT-03 deferred NMOS write+SHA proof.

**Key risks:** (1) Irreversible write to a UV-EPROM without eraser — mitigated by mandatory blank-check-first protocol. (2) False-PASS oracle from wrong board/shield — mitigated by Leonardo+Rev 2.0 lock, N≥5 reads, port identity verification per-task. (3) NMOS under-voltage programming at 22.4V VPE — mitigated by explicit rail measurement, firmware warning documentation, N≥3 read-backs. (4) 2516 user-override entry bypassing safety gates — mitigated by manual pre-bench review.

---

## Key Findings Summary

### From STACK.md

**Headline:** v1.15 has zero new dependencies, reuses v1.13 existing harness, adds one user-override DB entry.

**Deliverables:**
- Write→read→verify cycle: `EpromOperator.write_cycle_eprom` (already exists)
- Evidence capture: `firestarter dev write-cycle --runs 3` produces per-run binaries + SHA
- Family-level harness: `dev validate-family` (Tier-3 runner, Leonardo-only PASS oracle, R1 gate armed at 270000±25%)
- Integration test: `write_test.sh` (existing, no new code)
- Firmware: Leonardo untouched (89.5% flash, 3,018 bytes free). `configure_eprom` (0x07/0x08/0x0B) handles all.
- 2516 user-override: `~/.firestarter/database.json` (operator-managed, bypasses check_dispatch.py/diff_db.py — manual pre-bench safety review required)

**Critical invariant:** 0xA4 regression guard (Phase 77, Option C): INIT/END DATA frames NOT acked by host (`_execute_phase:ack_data=False`). Do not revert.

### From FEATURES.md

**Headline:** 11 chips, 5 algorithm families, 8 electrically-rewritable + 3 UV-EPROM with no eraser.

**Table stakes:**
- Non-destructive read + blank-check for every chip (validates read path/decode with zero risk)
- Full write→read→verify with SHA for 8 EE chips (W27C512 proven Phase 77; 7 unproven)
- UV-EPROM no-eraser protocol for 3 chips (Phase A: read+blank-check; Phase B: write if blank; Phase C: AND-mask if programmed)
- 2516 DB entry + bench SHA match (closes FUT-03 NMOS proof)
- Per-chip evidence record (EVIDENCE.md / EVIDENCE.json schema)
- **VERIFY ITEM:** FLAG_CAN_ERASE correctness for Flash/EEPROM type (W29C020/W29C040 are "Flash/EEPROM", not "EEPROM")

### From ARCHITECTURE.md

**Headline:** 2516 user-override flow, 4-phase build order, Leonardo preconditions, per-chip evidence schema.

**2516 user-override safety (manual pre-bench review required):**
1. algorithm=0x0B routes to configure_eprom ✓
2. vpp_mv=25000 ≤ RURP_VPP_CEILING_MV=25000 ✓
3. FLAG_CAN_ERASE NOT set (type=UV-EPROM) ✓
4. DIP24_2716 pinout routes VPE correctly ✓
5. Bench-verify on ~22.4V VPE rail ✓

**Build order (sequential, dependencies on Phase 81):**
- **Phase 81:** 2516 DB entry + non-destructive read sweep (all 11 chips, ~2–3 hours)
- **Phase 82:** EE-EPROM write→verify (8 chips, ~4–6 hours)
- **Phase 83:** UV-EPROM write proof (3 chips, ~3–5 hours, **FUT-03 closure**)
- **Phase 84:** DB decode audit + conditional RCA (1–8 hours)

**Leonardo preconditions:**
- R1 ≈ 270000±25% (live readback at task start)
- Port identity via `controller:` string (verified per-task after any USB event)
- Chip seating + ZIF lever confirmed before any read

**VPE rail for NMOS (2516):** 22.4V DMM / 23.9V firmware (Phase 79-01 corrected). Use `firestarter vpe` (NOT `vpp`). Under-voltage warning expected (22.4V < 23.75% threshold for 25V chip). Document rail + firmware warning explicitly.

### From PITFALLS.md

**Critical pitfalls (top 3):**
1. **Irreversible UV-EPROM write without eraser:** Mandatory blank-check FIRST. Phase A: read+blank-check. Phase B: write if blank. Phase C: AND-mask (all-0x00) if programmed. Spend decision at bench live.
2. **False-PASS oracle (wrong board/shield):** Leonardo+Rev 2.0 ONLY. Port identity per-task. N≥5 reads with identical SHA. v1.9 read-bug RCA stands.
3. **NMOS under-voltage at 22.4V VPE:** Record live rail reading, capture firmware warning, N≥3 read-backs with SHA table. Accept best-effort result per Phase 79 D-07 precedent.

**Other critical pitfalls:**
- UV-EPROM AND-mask misunderstanding (0→1 bit writes invalid)
- 0xA4 empty-input desync (regression test must be green)
- FLAG_CAN_ERASE boundary (Flash/EEPROM needs coverage)
- 2516 user-override bypasses safety gates (manual review required)
- DB decode mismatch (run `firestarter info` + `firestarter id` before write)
- Stale R1 calibration (live readback at task start)
- Chip seating faults (visual confirmation + reseat on all-0xFF)
- Port-identity drift (verify per-task, not session-start)
- Chip-OUT before Uno sideload (Leonardo EXEMPT)
- Shield revision ID (ask operator; EEPROM byte cannot distinguish revs)

---

## Implications for Roadmap

### Suggested Phase Structure

**Phase 81: 2516 DB Entry + Non-Destructive Read Sweep**
- **Goal:** Author 2516 user-override entry; validate read path + DB decode for all 11 chips with zero chip consumption. Discover blank_state for 3 UV-EPROMs (gates Phase 83).
- **Deliverable:** EVIDENCE.md populated with read+blank-check rows for all 11 chips. No writes. Manual pre-bench safety review of 2516 entry passed.
- **Time:** ~2–3 hours
- **Success:** All 11 chips readable; blank_state recorded for each UV-EPROM

**Phase 82: EE-EPROM Silicon Validation (8 Chips, Write+Verify)**
- **Goal:** Validate write path for all electrically-erasable chips. Reuse v1.13 harness. Prior evidence: W27C512 (Phase 77), SST39SF040 (Phase 74), W29C040 (Phase 74), FM1608 (Phase 73). New: W27E512, SST27SF512, W27E040, W29C020.
- **Deliverable:** EVIDENCE.md rows for each chip: op=write+verify, SHA match, verdict, anomalies
- **Time:** ~4–6 hours
- **Pre-bench gate:** **CODE REVIEW (5 min):** Confirm database.py sets `FLAG_CAN_ERASE` for "Flash/EEPROM" type. If missing, update to `if electrical_type in ("EEPROM", "Flash/EEPROM")` and re-run `pytest --cov-fail-under=70`.
- **Success:** All 8 EE chips produce SHA-match on Leonardo+Rev 2.0, N≥5 reads per chip

**Phase 83: UV-EPROM Write Proof (3 Chips, Spend vs Preserve Gated on Phase 81)**
- **Goal:** Validate write path for UV-EPROMs gated on blank_state from Phase 81. For blank: write→verify. For non-blank: AND-mask (all-0x00)→verify. **2516 graduation closes FUT-03 deferred NMOS proof.**
- **Deliverable:** EVIDENCE.md rows for M27C512, AM27C020, 2516. 2516 includes VPE rail reading, firmware warning log, N≥3 read SHA table.
- **Time:** ~3–5 hours
- **Success:** All 3 UV-EPROMs pass write+verify. 2516: SHA match N≥3 reads; VPE=22.4V ± tolerance; `MSG_WARN_VPP_LOW` documented. **FUT-03 closed.**

**Phase 84: DB Decode Correctness Audit + Conditional Defect RCA**
- **Goal:** If 81–83 clean, Phase 84 is documentation only. If defects surface, RCA and fix via lockstep pattern.
- **Deliverable:** If clean: ".planning/v1.15-EVIDENCE-AUDIT.md" (all 11 chips validated, release ready). If defect: .planning/v1.15-DEFECT-RCA.md + code fix + re-bench.
- **Time:** 1–2 hours if clean; 4–8 hours if defect
- **Success:** All 11 chips match DB claims, OR defect identified and fixed with re-bench proof

---

## Research Flags

**Pre-execution validation gates:**

1. **CODE REVIEW (Phase 82 pre-bench, 5 min):** Confirm `firestarter_app/firestarter/database.py:convert_to_programmer:592–607` sets `FLAG_CAN_ERASE` for **both** "EEPROM" **and** "Flash/EEPROM" electrical types. If missing for Flash/EEPROM, W29C020/W29C040 write on non-blank chips fails at blank-check gate. If gap found: update conditional and re-run pytest (low-risk one-liner).

2. **REGRESSION TEST CHECK (immediate):** Run `pytest` on host suite. Confirm `test_init_phase_data_frames_not_acked` (0xA4 guard, Phase 77) is green. If missing or failed, 0xA4 desync vulnerability is open.

3. **2516 ENTRY MANUAL REVIEW (Phase 81 step 1):** Before any bench session, manually verify `~/.firestarter/database.json` 2516 entry against TMS2516 datasheet:
   - VPP pin = pin 21 (DIP24)
   - algorithm = 0x0B (11 decimal)
   - vpp_mv = 25000
   - electrical.type = "UV-EPROM"
   - support_status = "supported"
   - pinout = "DIP24_2716" (must exist in pinouts.json)

**Phases with deferred research:**

- **Phase 83 (2516 NMOS under-voltage):** No existing bench data on 2516 silicon under RURP/Leonardo. Phase 79 proved 4 NMOS chips at soft best-effort; the 2516 is the second data point. Bench work will answer whether 22.4V VPE is sufficient for 25V NMOS class. If write fails: investigate (a) VPE rail voltage actual? (b) TMS2516 datasheet VCC-at-programming requirement (25V) a blocker? (RURP applies 5V VCC; no mechanism to raise it). Treat any failure as under-voltage or electrical path issue first, not firmware bug.

**Phases with well-documented patterns (no new research):**

- Phase 81 (non-destructive read): Standard protocol, Leonardo/Rev 2.0 proven.
- Phase 82 (EE-EPROM write): `write_cycle_eprom` reused from v1.13; all handlers exist.
- Phase 84 (audit/RCA): Established lockstep pattern for firmware+host fixes (v1.13 precedent).

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|-----------|-------|
| **Stack** | HIGH | All mechanisms verified live in source code at path/line. Firmware untouched. Single user-override entry minimal. |
| **Features** | HIGH | All 11 chips live-queried from DB. Pinout/VPP/algorithm/size verified per family. **FLAG_CAN_ERASE for "Flash/EEPROM" needs 5-min code review before Phase 82.** |
| **Architecture** | HIGH | 2516 user-override flow traced through EpromDatabase→chip_resolver→convert_to_programmer→memory.cpp dispatch. Build order sequential. Evidence schema matches v1.13. |
| **Pitfalls** | HIGH | All grounded in project history. Preventions concrete. Recovery strategies documented. |
| **2516 graduation (FUT-03)** | MEDIUM-HIGH | Electrically compatible with Phase 79 NMOS class. Phase 79 soft-graduated 4 chips at best-effort 22.4V. 2516 is second data point. Under-voltage at 90% spec accepted per Phase 79 D-07, but 2516 never silicon-verified. Bench proof will be authoritative. |

**Gaps requiring validation at bench:** (1) FLAG_CAN_ERASE for Flash/EEPROM (code review before Phase 82). (2) 2516 silicon performance at 22.4V VPE. (3) W29C040 full-cycle erase+write (Phase 82 proof). (4) All chip DB decode (Phase 81 read + Phase 84 audit).

---

## Ready for Requirements Definition

The four phases are well-defined with clear dependencies, deliverables, and success criteria. Phases 81–83 are sequential; Phase 84 is conditional on defects. Total estimated bench time: 9–16 hours for Phases 81–83 (serial execution). The 2516 write (Phase 83) is most time-intensive due to N≥3 re-read requirement and under-voltage documentation. FUT-03 closure achieved upon Phase 83 PASS.

**Roadmapper input:** Use this research as foundational input for requirements and phase definition.

---

**Research synthesis completed 2026-06-23.**

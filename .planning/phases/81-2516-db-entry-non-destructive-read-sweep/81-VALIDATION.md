---
phase: 81
slug: 2516-db-entry-non-destructive-read-sweep
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-23
---

# Phase 81 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (firestarter_app) |
| **Config file** | firestarter_app/pyproject.toml |
| **Quick run command** | `cd firestarter_app && pytest tests/test_database_conversion.py -q` |
| **Full suite command** | `cd firestarter_app && pytest -q` |
| **Estimated runtime** | ~32 seconds (650 tests, per 2026-06-23 research run) |

---

## Sampling Rate

- **After every task commit:** Run the quick run command
- **After every plan wave:** Run the full suite command
- **Before `/gsd-verify-work`:** Full suite must be green (incl. the 0xA4 `test_init_phase_data_frames_not_acked` guard — SAFE-02)
- **Max feedback latency:** ~32 seconds

---

## Per-Task Verification Map

*To be completed by the planner — map each task to its requirement, test type, and automated command. See RESEARCH.md §"Validation Architecture" for the recommended dimension coverage.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 81-01-01 | 01 | 1 | DB-02, SAFE-03 | T-81-01 | FLAG_CAN_ERASE chain re-audited; W29C040/W29C020/W27C512 carry the flag, M27C512 does not; constant parity | unit | `cd firestarter_app && python3 -c "from firestarter.database import EpromDatabase; db=EpromDatabase(skip_local_override=True); print(all(db.convert_to_programmer(db.get_eprom(c))['flags']&0x02 for c in ('W29C040','W29C020','W27C512')) and db.convert_to_programmer(db.get_eprom('M27C512'))['flags']&0x02==0)"` | ✅ | ⬜ pending |
| 81-01-02 | 01 | 1 | DB-02, SAFE-02 | T-81-01, T-81-02 | Flash/EEPROM pinning test green; 0xA4 guard green; full suite + ruff (CI target) green | unit | `cd firestarter_app && pytest tests/test_database_conversion.py::test_convert_w29c040_flash_eeprom_flag_can_erase tests/test_eprom_operations.py::test_init_phase_data_frames_not_acked -q && ruff check tests/test_database_conversion.py && ruff format --check tests/test_database_conversion.py && pytest -q` | ✅ | ⬜ pending |
| 81-02-01 | 02 | 1 | GRAD-01, GRAD-02 | T-81-03, T-81-05 | 2516 user-override merged via name-key; decodes 0x0B/DIP24_2716/UV-EPROM/25000/2048; no FLAG_CAN_ERASE | integration | `cd firestarter_app && python3 -c "from firestarter.database import EpromDatabase; db=EpromDatabase(skip_local_override=False); e=db.get_eprom('2516'); assert e; print(db.convert_to_programmer(e)['flags']&0x02)"` | ⬜ (created by task) | ⬜ pending |
| 81-02-02 | 02 | 1 | GRAD-02, EVID-01, EVID-02 | T-81-03, T-81-04 | SR-1 doc verifies 6 D-02 values + DIP24_2716 VPP=pin21; EVIDENCE.json 11 cells, locked columns, harness_version 81 | schema | `python3 -c "import json; d=json.load(open('.planning/v1.15/bench/EVIDENCE.json')); assert d['harness_version']=='81' and len(d['cells'])==11; print('ok')" && grep -q 'Operator sign-off' .planning/phases/81-2516-db-entry-non-destructive-read-sweep/81-2516-SAFETY-REVIEW.md && echo review-ok` | ⬜ (created by task) | ⬜ pending |
| 81-02-03 | 02 | 1 | GRAD-02 | T-81-03, T-81-04 | Operator personally signs the 2516 safety review (blocking-human, never auto-approve) | human-check | manual — operator fills `**Operator sign-off:** [x] Approved` in 81-2516-SAFETY-REVIEW.md | n/a | ⬜ pending |
| 81-03-01 | 03 | 2 | SWEEP-01, EVID-03, SAFE-01 | T-81-06, T-81-07, T-81-08 | 8 non-UV chips read (N>=3 byte-identical) + blank-check + negative control on Leonardo+Rev 2.0 | human-check | manual bench — operator records per-chip verdicts + wrong-file verify exit-nonzero into EVIDENCE | n/a | ⬜ pending |
| 81-03-02 | 03 | 2 | SWEEP-01, SWEEP-02, EVID-03, SAFE-01 | T-81-06, T-81-09 | 3 UV-EPROMs read (N>=3) + gating blank-state recorded; 2516 decode confirmed; no write | human-check | manual bench — operator records 3 UV BLANK/NOT-BLANK gating blank-states + 2516 info decode | n/a | ⬜ pending |
| 81-03-03 | 03 | 2 | EVID-01 | T-81-06, T-81-09 | EVIDENCE.{md,json} finalized: 11 cells, no pending, UV gating blank-states, PASS rows non-vacuous (N>=3+SHA) | schema | `cd /workspaces && python3 -c "import json; d=json.load(open('.planning/v1.15/bench/EVIDENCE.json')); assert len(d['cells'])==11 and not [c for c in d['cells'] if c['verdict']=='pending']; print('ok')"` | ⬜ (populated by sweep) | ⬜ pending |

---

## Wave 0 Requirements

- *Existing infrastructure (pytest, ruff, mypy) covers all software phase requirements — no Wave 0 framework install needed.*
- *Hardware bench requirements (SWEEP-01/02, EVID-*) are manual-only — see below.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 11-chip non-destructive read + blank-check on Leonardo + Rev 2.0 | SWEEP-01, SWEEP-02, EVID-01/02/03 | Requires physical chips + bench hardware (operator-executed) | Read + blank-check each chip; N≥3 byte-identical reads + negative control; record EVIDENCE row |
| 2516 user-override safety review sign-off | GRAD-02 | Human gate — operator personally approves the hand-authored override before bench | Operator signs `81-2516-SAFETY-REVIEW.md` checklist (D-01) |
| `firestarter info 2516` correct decode | GRAD-02 | Requires the user-override entry installed in `~/.firestarter/database.json` | Run `firestarter info 2516`, confirm 0x0B / DIP24_2716 / UV-EPROM / 25000mV / 2048 bytes |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 32s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** planner-complete — all tasks mapped; software tasks carry `<automated>`; manual bench/sign-off tasks are operator-only (SWEEP/EVID-03/GRAD-02 sign-off) per the Manual-Only Verifications table; no 3 consecutive auto tasks lack verify; feedback latency ~32s.

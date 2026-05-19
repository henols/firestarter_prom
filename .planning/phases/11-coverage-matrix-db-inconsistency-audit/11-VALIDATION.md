---
phase: 11
slug: coverage-matrix-db-inconsistency-audit
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-19
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 [VERIFIED: `pytest --version`] |
| **Config file** | None — discovered via `firestarter_app/tests/conftest.py` with CWD = `firestarter_app/` (mirrors Phase 06 Plan 03 pattern) |
| **Quick run command** | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py -x` |
| **Full suite command** | `cd firestarter_app && pytest tests/ -x` |
| **Estimated runtime** | ~5 s quick / ~30 s full (existing 29 tests + new ~8) |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py -x` (< 5 s)
- **After every plan wave:** Run `cd firestarter_app && pytest tests/ -x` (< 30 s)
- **Before `/gsd-verify-work`:** Full suite must be green AND manual idempotence smoke (`diff $(./tool --output /tmp/a) <(cat .planning/v1.3-COVERAGE-MATRIX.md)` returns empty)
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 11-W0-01 | W0 | 0 | COV-01, COV-02 | — | N/A | unit (stubs) | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py --collect-only` | ❌ W0 | ⬜ pending |
| 11-COV-01-row-count | enumeration | 2 | COV-01 | — | N/A | unit | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_enumeration_row_count -x` | ❌ W0 | ⬜ pending |
| 11-COV-01-sort | enumeration | 2 | COV-01 | — | N/A | unit | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_enumeration_sort -x` | ❌ W0 | ⬜ pending |
| 11-COV-01-idempotence | idempotence | 2 | COV-01 / D-02 | — | N/A | unit (smoke) | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_idempotence -x` | ❌ W0 | ⬜ pending |
| 11-COV-02-hazard-cluster | defects | 3 | COV-02 / D-12 / D-15 | — | N/A | unit | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_hazard_cluster_42_rows -x` | ❌ W0 | ⬜ pending |
| 11-COV-02-ledger-idempotent | ledger | 3 | COV-02 / D-13 | — | N/A | unit | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_ledger_idempotent -x` | ❌ W0 | ⬜ pending |
| 11-COV-02-ledger-reuse | ledger | 3 | COV-02 / D-13 | — | N/A | unit | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_ledger_id_reuse -x` | ❌ W0 | ⬜ pending |
| 11-COV-01-summary-stats | summary | 1 | COV-01 / D-07 | — | N/A | regression | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_summary_stats -x` | ❌ W0 | ⬜ pending |
| 11-D-03-exit-codes | CLI | 1 | D-03 | — | N/A | integration (subprocess) | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_exit_codes -x` | ❌ W0 | ⬜ pending |
| 11-bench-coverage | bench-proof | 4 | COV-01 / SC-03 / D-09, D-10, D-11 | — | N/A | unit | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_bench_coverage_proof -x` | ❌ W0 | ⬜ pending |
| 11-golden-file | golden | 4 | COV-01 / COV-02 | — | N/A | regression | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_golden_file_matches -x` | ❌ W4 | ⬜ pending |
| 11-D-07-doc-fix | doc-reconcile | 5 | D-07 / SC-01 | — | N/A | manual grep | `grep -nE '\b(743\|341\|214)\b' .planning/PROJECT.md .planning/ROADMAP.md .planning/REQUIREMENTS.md` returns only rows kept as historical narrative | manual-only — automated optional | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tests/test_audit_coverage_matrix.py` — new test file; covers COV-01 + COV-02 + D-03 acceptance with 8 unit/integration tests + 1 golden-file regression test
- [ ] `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` — golden-file fixture; created at the end of Wave 4 from the operator-approved matrix, then committed alongside the matrix
- [ ] No framework install required (pytest 9.0.3 already present per `pytest --version`)
- [ ] No conftest changes required (existing `conftest.py` does not interfere with stand-alone tool tests that import directly from `tools.audit_coverage_matrix`)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Planning-doc count fix (D-07) | D-07 / SC-01 | Targeted markdown edits; automated grep returns a count, but operator decides whether each remaining occurrence is "historical narrative" (preserve) or "current count claim" (replace). | 1. After running `tools/audit_coverage_matrix.py`, read §2 (DB Count Reconciliation) for live numbers. 2. Run `grep -nE '\b(743\|341\|214)\b' .planning/PROJECT.md .planning/ROADMAP.md .planning/REQUIREMENTS.md`. 3. For each hit, confirm: this is `<details>` historical narrative? leave; this is a present-tense claim? replace per D-07 edit table. |
| BENCH coverage proof — operator confirmability | SC-03 | The matrix's §5 must let an operator state, in their own words, "these six BENCH chips represent N rows on axes X/Y/Z." Automated tests can verify §5 exists and is well-formed; only an operator can confirm it *reads* as the receipt. | 1. After Wave 4 commits, read `.planning/v1.3-COVERAGE-MATRIX.md` §5 top-to-bottom. 2. Confirm each of the three per-axis tables identifies the covering BENCH chip for every covered cell + flags every uncovered cell with a cross-reference into §4. 3. Confirm the §5 prose closes by naming the milestone claim ("…these six chips represent N=339 rows…"). |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies declared
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (new test file + golden fixture)
- [ ] No watch-mode flags (pytest invocations use `-x` for fail-fast, not `--watch`)
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter (after Wave 0 lands)

**Approval:** pending

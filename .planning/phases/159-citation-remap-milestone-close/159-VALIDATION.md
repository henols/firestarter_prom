---
phase: 159
slug: citation-remap-milestone-close
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-24
---

# Phase 159 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 plus command-level Git/corpus gates |
| **Config file** | None — invoke the focused test module explicitly |
| **Quick run command** | `python3 -m pytest -q .planning/v1.33/tools/test_remap_citations.py` |
| **Full suite command** | Focused pytest suite, hardened real-corpus dry run, disposable apply/no-op hash rehearsal, `check_record_corrections.py`, and marker/requirements/roadmap gates |
| **Estimated runtime** | Establish during Wave 0 and record before production apply |

---

## Sampling Rate

- **After every tool-change commit:** Run `python3 -m pytest -q .planning/v1.33/tools/test_remap_citations.py`
- **After every manifest/reconciliation commit:** Run the hardened full-corpus dry run and require zero actionable exceptions.
- **Before the production apply:** Run unit tests, disposable apply rehearsal, second-run byte no-op/hash comparison, and the archive gate.
- **Before `/gsd-verify-work`:** Require one recorded production apply, a post-apply real-corpus no-op, the real range proof, unchanged archive gate, absent staleness marker, and complete REMAP rows.
- **Max feedback latency:** Record the measured focused-suite runtime during Wave 0; no three consecutive implementation tasks may lack an automated check.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 159-01-01 | 01 | 1 | REMAP-01, REMAP-02 | T-159-01 | Wrong anchors and actionable exceptions fail closed with zero writes | unit/integration | `python3 -m pytest -q .planning/v1.33/tools/test_remap_citations.py` | ❌ W0 additions | ⬜ pending |
| 159-01-02 | 01 | 1 | REMAP-02, REMAP-05 | T-159-02 | Planning-location reconciliation and reviewed retargets are deterministic and fixed-point | unit/integration | `python3 -m pytest -q .planning/v1.33/tools/test_remap_citations.py` | ❌ W0 additions | ⬜ pending |
| 159-02-01 | 02 | 1 | REMAP-01, REMAP-05 | T-159-03 | Late records receive explicit historical anchors and stable identities | corpus dry run | Hardened full-corpus dry-run command defined by the plan | ❌ W0 manifest | ⬜ pending |
| 159-02-02 | 02 | 2 | REMAP-02 | T-159-04 | Every non-mechanical endpoint is reviewed and ledgered; no implicit deletion choice survives | corpus/ledger | Hardened full-corpus dry run reports zero unmatched, not-at-recorded, and unreviewed-retarget rows | ❌ W0 ledger | ⬜ pending |
| 159-03-01 | 03 | 3 | REMAP-01, REMAP-02, REMAP-03, REMAP-05 | T-159-05 | Disposable rehearsal is atomic, oracle-clean, range-correct, and byte-idempotent | rehearsal | Rehearsal apply plus second-run no-op/hash comparison | ❌ W0 harness | ⬜ pending |
| 159-04-01 | 04 | 4 | REMAP-01, REMAP-02, REMAP-03, REMAP-05 | T-159-06 | Exactly one production apply is recorded and all post-apply gates pass | production gate | Production ledger plus post-apply dry run and hash/oracle checks | ❌ plan-defined | ⬜ pending |
| 159-04-02 | 04 | 5 | REMAP-04 | T-159-07 | Marker removal occurs only after all prior gates pass | close gate | `test ! -e .planning/v1.33/CITATIONS-STALE.md` | ❌ closure gate | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Extend `.planning/v1.33/tools/remap_citations.py` for per-record anchors, planning-location reconciliation, reviewed-retarget application, stable IDs, and fail-closed exception totals.
- [ ] Extend `.planning/v1.33/tools/test_remap_citations.py` with wrong-anchor, moved-document, shifted-planning-line, exception, retarget fixed-point, post-154 retarget, per-record SHA cache, real-range shrink, and transaction rollback tests.
- [ ] Create `.planning/v1.33/159-late-citation-manifest.jsonl` with historical anchors for Phase 155–158 records.
- [ ] Create a machine-readable exception ledger for the original retarget set and newly deleted/replaced endpoints; settle it before apply.
- [ ] Create a disposable-corpus rehearsal/hash harness using the production parser/writer path.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Renewed target selection for the five post-154 retargets whose destination was deleted again | REMAP-02 | The correct semantic replacement requires human review of source context | Review each stable record ID against its historical source text and candidate targets; record the chosen target and rationale in the exception ledger before the dry-run gate can pass. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verification or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verification
- [ ] Wave 0 covers all missing references
- [ ] No watch-mode flags
- [ ] Measured focused-suite feedback latency is recorded and acceptable
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

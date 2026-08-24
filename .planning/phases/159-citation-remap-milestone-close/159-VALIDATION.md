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
| 159-01-01 | 01 | 1 | REMAP-01, REMAP-02, REMAP-03, REMAP-05 | T-159-01, T-159-02 | RED legs cover wrong anchors, relocation ambiguity, every actionable exception, real range shrink, rollback, and receipt replay | unit/integration RED | `python3 -m pytest -q .planning/v1.33/tools/test_remap_citations.py; test $? -ne 0` | ❌ Wave-1 additions | ⬜ pending |
| 159-01-02 | 01 | 1 | REMAP-01, REMAP-02, REMAP-03, REMAP-05 | T-159-01..04 | Hardened engine is fail-closed, multi-anchor, reportable, atomic, fixed-point, and one-shot | unit/integration GREEN | `python3 -m pytest -q .planning/v1.33/tools/test_remap_citations.py` | ❌ Wave-1 implementation | ⬜ pending |
| 159-02-01 | 02 | 2 | REMAP-01, REMAP-02 | T-159-05..07 | Historical preparer preserves all rows, emits stable IDs, and serializes non-unique anchors for review | unit/integration | `python3 -m pytest -q .planning/v1.33/tools/test_prepare_citation_remap.py .planning/v1.33/tools/test_build_citation_manifest.py .planning/v1.33/tools/test_remap_citations.py` | ❌ Wave-2 implementation | ⬜ pending |
| 159-02-02 | 02 | 2 | REMAP-01, REMAP-02 | T-159-05..08 | Full late census produces the complete dynamic review-ID set; dry run exits 1 solely for it with all other counters zero | corpus/ledger | Plan 02's full `prepare_citation_remap.py` + `remap_citations.py --report-json /tmp/gsd-159-plan02-dry.json` verifier | ❌ Wave-2 artifacts | ⬜ pending |
| 159-03-01 | 03 | 3 | REMAP-02 | T-159-09, T-159-10 | Human reviews every and only pending stable ID, using evidence fields appropriate to target, anchor, or location decisions | checkpoint + census | Plan 03's Python set-equality census over ledger and review packet | ❌ Wave-2 inputs | ⬜ pending |
| 159-04-01 | 04 | 4 | REMAP-02 | T-159-11 | Exact approved stable-ID set is transcribed and every target/anchor/location oracle closes; no open row remains | corpus/ledger | Plan 04 Task 1's ledger assertions plus production-shaped `--report-json` dry run | ❌ Wave-4 ledger update | ⬜ pending |
| 159-04-02 | 04 | 4 | REMAP-01, REMAP-02, REMAP-03, REMAP-05 | T-159-12..14 | Disposable apply is non-vacuous, range-correct, archive-safe, and byte-idempotent | rehearsal | `python3 -m pytest -q .planning/v1.33/tools/test_rehearse_citation_remap.py .planning/v1.33/tools/test_remap_citations.py && python3 .planning/v1.33/tools/rehearse_citation_remap.py ...` | ❌ Wave-4 harness | ⬜ pending |
| 159-05-01 | 05 | 5 | REMAP-01, REMAP-02, REMAP-03, REMAP-05 | T-159-15 | READY preflight pins every input, source SHA, affected document, test, dry-run counter, archive result, and marker state | production preflight | Plan 05 Task 1's focused suites plus `159-production-preflight.json` assertions | ❌ Wave-5 receipt | ⬜ pending |
| 159-05-02 | 05 | 5 | REMAP-01, REMAP-02, REMAP-03, REMAP-05 | T-159-16..18 | Sole production apply is receipt-enforced; post-apply pass is dry and byte-no-op; range/archive evidence is recorded | production apply/gate | Plan 05 Task 2's receipt assertions, full post-apply dry run, archive gate, and commit gate | ❌ Wave-5 production artifacts | ⬜ pending |
| 159-06-01 | 06 | 6 | REMAP-01, REMAP-02, REMAP-03, REMAP-04, REMAP-05 | T-159-19..22 | Close readiness re-runs every gate and freezes a scoped payload while marker remains present | close readiness | Plan 06 Task 1's `159-close-readiness.json` assertions plus marker/pending-row gates | ❌ Wave-6 readiness | ⬜ pending |
| 159-06-02 | 06 | 6 | REMAP-04 | T-159-19..22 | Scoped closure changes only REMAP/Phase-159 regions and removes marker as the final mutation | scoped closure/final gate | Plan 06 Task 2's marker-absence, requirement/roadmap count, STATE, archive, commit, and deletion gates | ❌ Wave-6 closure | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Extend `.planning/v1.33/tools/remap_citations.py` for per-record anchors, planning-location reconciliation, reviewed-retarget application, stable IDs, and fail-closed exception totals.
- [ ] Extend `.planning/v1.33/tools/test_remap_citations.py` with wrong-anchor, moved-document, shifted-planning-line, exception, retarget fixed-point, post-154 retarget, per-record SHA cache, real-range shrink, and transaction rollback tests.
- [ ] Create `.planning/v1.33/159-late-citation-manifest.jsonl` with historical anchors for Phase 155–158 records.
- [ ] Create a machine-readable exception ledger whose dynamic review set contains the five known post-154 non-survivors plus every late non-survivor and ambiguous historical anchor/location; settle it to zero open rows before apply.
- [ ] Create a disposable-corpus rehearsal/hash harness using the production parser/writer path.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Complete measured target/anchor/location selection set (known minimum: five post-154 non-survivors) | REMAP-02 | Semantic replacements and genuinely non-unique historical identities require human judgment | Review every stable ID emitted by Plan 02, using current source context for targets and Git/document evidence for anchors/locations; the selected-ID set must exactly equal the ledger pending set and Plan 04 must reduce open rows to zero. |

---

## Validation Sign-Off

- [x] All 11 tasks have an `<automated>` verification mapped above
- [ ] Sampling continuity: no 3 consecutive tasks without automated verification
- [ ] Wave 0 covers all missing references
- [ ] No watch-mode flags
- [ ] Measured focused-suite feedback latency is recorded and acceptable
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

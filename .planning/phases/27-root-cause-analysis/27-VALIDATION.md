---
phase: 27
slug: root-cause-analysis
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-21
---

# Phase 27 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Phase 27 is **narrative-append** — no production code changes. "Validation" is
> self-validating evidence in the RCA narrative (grep-checkable content tokens
> in `.planning/v1.6-EVIDENCE.md`) plus a pytest non-regression smoke.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (host-side) — already installed in `firestarter_app/` (Phase 26 added `tests/test_consistency_check.py`, `tests/conftest.py`) |
| **Config file** | `firestarter_app/pyproject.toml` (existing) |
| **Quick run command** | `cd firestarter_app && pytest tests/ -x` |
| **Full suite command** | `cd firestarter_app && pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds (smoke only — no Phase 27 code changes) |

---

## Sampling Rate

- **After every task commit:** Narrative tokens check via grep against `.planning/v1.6-EVIDENCE.md` (single-doc diffs; checks are constant-time)
- **After every plan wave:** `cd firestarter_app && pytest tests/ -v` (non-regression smoke; Phase 27 makes no code changes)
- **Before `/gsd-verify-work`:** All RCA narrative tokens green; pytest smoke green
- **Max feedback latency:** ~5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 27-01-XX | 01 | A | RCA-01 | — | N/A (narrative phase) | grep | `grep -E 'leonardo_rurp_shield\.cpp\\|rurp_read_data_buffer\\|rurp_set_data_input' .planning/v1.6-EVIDENCE.md` | ✅ | ⬜ pending |
| 27-01-XX | 01 | A | RCA-02 | — | N/A | grep+count | `awk '/^## Phase 27 — RCA Findings/,/^## /' .planning/v1.6-EVIDENCE.md \| grep -cE '^[A-Z]'` (must be 2..5) | ✅ | ⬜ pending |
| 27-01-XX | 01 | A | RCA-03 | — | N/A | grep | `grep -E 'pre-v1\.0\\|2\.0\.[0-9]\\|3\.0\.0b[0-9]\\|5b1f1cd' .planning/v1.6-EVIDENCE.md` | ✅ | ⬜ pending |
| 27-01-XX | 01 | A | SC#4 (GATE-1.6) | — | N/A | grep | `grep -cE 'write-path\\|VPP\\|pulse interval' .planning/v1.6-EVIDENCE.md` (>=3) | ✅ | ⬜ pending |
| 27-01-XX | 01 | A | D-08 hypothesis disposition | — | N/A | grep | `grep -cE 'H[1-7].*(REFUTED\\|CONFIRMED\\|out of scope)' .planning/v1.6-EVIDENCE.md` (>=7) | ✅ | ⬜ pending |
| 27-01-XX | 01 | A | D-11 buffer-size drift | — | N/A | grep | `grep -E '512\\|1024' .planning/v1.6-EVIDENCE.md \| grep -i 'drift\\|TEMP\\|correction'` | ✅ | ⬜ pending |
| 27-01-XX | 01 | A | Non-regression | — | N/A | pytest | `cd firestarter_app && pytest tests/ -x` | ✅ | ⬜ pending |
| 27-02-XX | 02 | B | RCA-01..03 (gap-fill) | — | N/A (conditional; only fires if Wave A `needs_bench: true`) | manual | Bench instrumentation log content-check (only authored if executed) | ⚠️ conditional | ⬜ drafted |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky/conditional*

*Task IDs are placeholders; the planner will assign concrete numeric task IDs during PLAN.md generation. The verification commands above are taken verbatim from RESEARCH.md §"Validation Architecture" §"Phase Requirements → Test Map" and MUST appear (or equivalent assertions) in each task's `acceptance_criteria` block.*

---

## Wave 0 Requirements

*None — existing pytest infrastructure from Phase 26 covers all phase requirements. Phase 27 authors a narrative section into an already-shipped evidence file; no new test scaffolding required.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Hypothesis-disposition narrative reads coherently to a future maintainer | RCA-02 | Subjective readability cannot be regex-checked beyond paragraph count + token presence | Operator reads the appended `## Phase 27 — RCA Findings` section end-to-end; confirms the WHY paragraph(s) explain the bug mechanism in domain terms (data-bus race / address-LSB-bleed / `PORTD = 0x00` mirror gap), not jargon-only |
| GATE-1.6 risk verdict is correct | SC#4 | Verdict is a judgment call on whether the candidate fix touches write-path / VPP / pulse-loop code; grep can confirm the three axis-words appear but not whether the verdict is sound | Operator skims the GATE-1.6 paragraph; confirms each axis has an affirmative GREEN/RED verdict with a one-line rationale |
| Bench-escalation decision (Wave A → Wave B trigger) | D-07 | Trigger evaluation is a meta-judgment over the produced RCA's confidence level | Wave A verifier sets `needs_bench: true\|false` based on whether D-01's three escalation triggers fire; RESEARCH.md HIGH-confidence conclusion implies `needs_bench: false` |

---

## Validation Sign-Off

- [ ] All tasks have `<acceptance_criteria>` with grep/pytest commands from the table above
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (grep counts as automated)
- [ ] Wave 0 covers all MISSING references (none required — see Wave 0 Requirements)
- [ ] No watch-mode flags (pytest `-x` only)
- [ ] Feedback latency < 10s (pytest smoke + grep tokens)
- [ ] `nyquist_compliant: true` set in frontmatter (toggle after planner emits tasks with the above `acceptance_criteria`)

**Approval:** pending

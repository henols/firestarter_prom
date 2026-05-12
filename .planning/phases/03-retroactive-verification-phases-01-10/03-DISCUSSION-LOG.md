# Phase 3: Retroactive Verification (Phases 01-10) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-12
**Phase:** 03-retroactive-verification-phases-01-10
**Areas discussed:** Scoring policy, Verification depth, Plan granularity, Open-hazard handling
**Mode:** User requested recommendations across all four areas — Claude locked decisions accordingly. No interactive back-and-forth per the user's directive to operate without stopping for clarifying questions.

---

## Scoring policy (PARTIAL → SATISFIED after v1.1 closure)

| Option | Description | Selected |
|--------|-------------|----------|
| Score against current source tree (today) | A REQ that was PARTIAL in v1.0 audit but closed in v1.1 becomes SATISFIED. Status `passed` with a "Cross-Milestone Closure" subsection narrating the v1.1 closure. Matches ROADMAP SC#1 wording "against the current source tree". | ✓ |
| Score against v1.0-as-shipped state | Preserves historical snapshot; REQ stays PARTIAL with a "carried follow-up" entry pointing to v1.1 closure. Cleaner audit-trail but creates dissonance with ROADMAP SC#1. | |
| Hybrid (per-REQ status reflects current; narrative notes v1.0-as-shipped) | Compromise — frontmatter `status: passed` + body narrates historical PARTIAL state. Effectively equivalent to option 1 once narrated. | |

**User's choice:** Recommendation accepted ("What do recommend") → Option 1.
**Notes:** ROADMAP SC#3 explicitly says "05-VERIFICATION.md explicitly records that the SAF-04 closure from Phase 1 satisfies the Intel-flash REQ-SAF-01 gap" — locks the policy.

---

## Verification depth per file

| Option | Description | Selected |
|--------|-------------|----------|
| Independent re-grep + re-trace per phase | Each VERIFICATION.md re-derives the full wiring map from scratch. Maximum rigour, ~300+ lines/file. | |
| Lean, audit-driven | Cite `v1.0-MILESTONE-AUDIT.md` + `v1.0-INTEGRATION-CHECK.md` as primary evidence + spot-check current tree via `grep -n`. ~100-160 lines/file matching 11/12-VERIFICATION.md scale. | ✓ |
| Full re-run of test suites per phase | Re-run `pio test`, `pio run`, `check_dispatch.py` per VERIFICATION.md. Most thorough but duplicates v1.1 Phase 1 + Phase 2 verification runs. | |

**User's choice:** Recommendation accepted → Option 2 (Lean, audit-driven).
**Notes:** v1.1 Phase 1 already re-validated WARNING-1 + WARNING-2 closure files with 25/25 native test PASS. v1.1 Plan 02-03 re-validated WIRE-02 with 743/743 round-trip PASS. Independent re-runs would be redundant. The wiring map exists; cite it.

---

## Plan granularity

| Option | Description | Selected |
|--------|-------------|----------|
| Single plan, 10 files | All deliverables in one plan, executed sequentially. ~1200-1500 lines of doc work in one atomic unit. | |
| 2 plans split by complexity | Plan 03-01 "clean batch" (5 files: 01/02/04/08/09 — verification-gap only). Plan 03-02 "closure-and-hazard batch" (5 files: 03/05/06/07/10 — cross-milestone closure + WARNING-5 follow-ups + SC#3/SC#4 explicit locks). | ✓ |
| 10 plans, 1 per phase | Maximum atomicity but template is identical across files; over-fragmentation. | |

**User's choice:** Recommendation accepted → Option 2 (2 plans, complexity split).
**Notes:** Two-plan split is a recommendation, not a hard contract; planner may merge or split further if friction surfaces.

---

## Open-hazard handling (WARNING-5 + WARNING-4)

| Option | Description | Selected |
|--------|-------------|----------|
| Score affected REQ PARTIAL with forward-pointer | WARNING-5 makes Phase 03/06/07's REQ-FW-01/-03/-SAF-02 PARTIAL because AT28C256 still routes hazardously. | |
| Score SATISFIED + `follow_ups` frontmatter entry | The v1.0 phase delivered what it promised (correct handler logic). WARNING-5 is an upstream-data classification issue + Phase 12's deferred override, not a Phase 03/06/07 defect. Mirror `11-VERIFICATION.md` 4-entry follow_ups pattern. | ✓ |
| Score SATISFIED with caveat in body only | No frontmatter entry; just narrative. Loses machine-readable carry-forward signal. | |

**User's choice:** Recommendation accepted → Option 2 (SATISFIED + follow_ups).
**Notes:** Same treatment for WARNING-4 (test-script drift) in 08-VERIFICATION.md — Phase 4 / HW-01 owns the fix. INFO-3 (static-high-pins DIP24-only coverage) gets an analogous follow_up entry in 10-VERIFICATION.md pointing to v1.2 / FW-07.

---

## Claude's Discretion

The user delegated decision-making for all four areas. Within each, Claude additionally took discretion on:
- Exact frontmatter `verified:` timestamp (write-time ISO8601).
- Whether each per-file VERIFICATION.md includes Section 5 (Data-Flow Trace) — included only where a real cross-file data path exists (01 yes; 02 no, single-file).
- Phrasing of Cross-Milestone Closure subsections — patterned after `01-VERIFICATION.md` §"Post-Review Fixes".
- Commit message format — `docs(03-NN): retroactive verification — Phase {NN} ({REQ-IDs})` recommended.

## Deferred Ideas

(Captured in CONTEXT.md `<deferred>` block — see `03-CONTEXT.md` for the full list. Highlights:)
- Update `v1.0-MILESTONE-AUDIT.md` to mark 13 PARTIAL findings closed — Phase 3 doesn't mutate the historical audit; Phase 5 / DOC-01 may surface the closure record in `MILESTONES.md`.
- Re-run `/gsd-audit-milestone` end-to-end after Phase 3 — v1.2 candidate.
- Move stray `10-CONTEXT.md` from `.planning/milestones/v1.0-phases/10-static-pins/` — out of Phase 3 scope.
- Resolve pre-existing dirt in `firestarter_app/.planning/codebase/` — tracked in STATE.md "Operator Next Steps".

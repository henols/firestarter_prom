# Phase 70: v1.11 + v1.12 DB-Pipeline Integration for Beta Merge - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-15
**Phase:** 70-v1-11-v1-12-db-pipeline-integration-for-beta-merge
**Areas discussed:** Merge mechanics, Pinout fixes, Diff policy, Firmware scope, Firmware boundary, Mask guardrail

---

## Merge mechanics

| Option | Description | Selected |
|--------|-------------|----------|
| Re-port on v1.12 branch, then merge | Rewrite build_db/check_dispatch/diff_db ON v1.12 to sit on beta's architecture, regen DB, gates green, THEN merge v1.12→beta | ✓ |
| Fresh integration branch off beta | Branch off beta, re-implement v1.12 features, cherry-pick runtime; cleanest but loses v1.12 build_db history | |
| Merge with -X ours on build_db, re-apply after | Force beta's build_db, take v1.12 runtime, re-apply safety as follow-up; fast but risks silent loss | |

**User's choice:** Re-port on v1.12 branch, then merge
**Notes:** The merge becomes the last, near-mechanical step once the branch is architecturally compatible with beta.

---

## Pinout fixes

| Option | Description | Selected |
|--------|-------------|----------|
| Verify principled resolve covers them, drop overrides | Research whether beta's mask resolve already routes the SRAM chips; if so drop overrides | |
| Keep a documented override allowlist on top | Re-port per-chip overrides as commented allowlist; safe but preserves the hack pattern | |
| Extend the mask logic to cover the cases natively | Fix resolve_pinout_key's mask logic so no per-chip override needed; most principled, largest blast radius | ✓ |

**User's choice:** Extend the mask logic to cover the cases natively
**Notes:** Paired with the per-chip guardrail below — zero-regression wins if a mask change breaks a v1.11-correct chip.

---

## Diff policy

| Option | Description | Selected |
|--------|-------------|----------|
| Baseline = v1.11 beta chip_database.json; rule-classify every delta | Diff regen DB vs beta DB; categorize new keys + demotions | |
| Baseline = pinned chip_database.baseline.json (v1.11 GATE-01 anchor) | Use v1.11's pinned anchor as the regression reference | |
| Two-stage diff: pinout/decode separately from safety-field additions | Split into (a) decode/pinout near-zero regression gate + (b) additive safety fields expected bulk | ✓ |

**User's choice:** Two-stage diff: pinout/decode separately from safety-field additions
**Notes:** Stage (a) baselined on v1.11 beta DB is the regression-critical gate for SC#2; pinned baseline.json reconciled alongside.

---

## Firmware scope

| Option | Description | Selected |
|--------|-------------|----------|
| Out of scope — host-only; firmware deferred to operator beta cut | Phase touches only firestarter_app DB tooling | |
| In scope — stage firmware merge as part of this phase | Perform/verify firmware beta merge within Phase 70; dual-repo | ✓ |
| (n/a) | | |

**User's choice:** In scope — stage firmware merge as part of this phase
**Notes:** Expands the roadmap's "host-only" framing to dual-repo; bounded by the follow-up below.

---

## Firmware boundary (follow-up)

| Option | Description | Selected |
|--------|-------------|----------|
| Merge v1.12→beta in firmware + prove build/native tests; STOP before any tag | Merge, build uno/leonardo, run native dispatch tests, confirm wire-constant parity; leave beta cut to operator | ✓ |
| Merge + build/test AND cut the lockstep beta tag in this phase | Also create beta pre-release tag; overrides operator-gated rule | |
| Don't merge firmware yet — only verify it WOULD merge clean | Dry-run/no-commit verification only | |

**User's choice:** Merge v1.12→beta in firmware + prove build/native tests; STOP before any tag
**Notes:** Lockstep proven, not published. Beta tag stays operator-gated.

---

## Mask guardrail (follow-up)

| Option | Description | Selected |
|--------|-------------|----------|
| Fall back to a documented per-chip override for ONLY that chip | Prefer mask extension; isolate regressions with commented override | |
| No fallback — mask must be correct for all; block until resolved | Refuse any override layer | |
| Decide per-chip during planning/research | Defer fallback policy; research recommends per affected chip | ✓ |

**User's choice:** Decide per-chip during planning/research
**Notes:** Evidence-driven, case-by-case; zero-decode-regression criterion is the tiebreaker.

---

## Claude's Discretion

- Task breakdown/ordering within the re-port.
- Whether diff_db.py gets a `--stage` flag vs two invocations for the two-stage diff.
- Specific test/snapshot updates required by the regenerated DB.

## Deferred Ideas

- Beta cut + lockstep pre-release tag — operator-gated, out of Phase 70.
- v1.12 milestone close — follows the beta merge.

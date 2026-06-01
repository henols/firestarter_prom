# Phase 48: COBS Evaluation + Post-RCA Cleanup + Milestone Close - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-01
**Phase:** 48-cobs-evaluation-post-rca-cleanup-milestone-close
**Areas discussed:** COBS-01 verdict & doc, TYPE-01 strictness target, Branch promotion mechanics
**Areas offered but not selected:** Stable 3.0.1 vs beta tag (resolved indirectly during Branch promotion → beta-only)

---

## COBS-01 verdict & doc

### Q1 — adopt/defer/reject verdict
| Option | Description | Selected |
|--------|-------------|----------|
| Reject library, defer resync | REJECT PacketSerial wholesale; DEFER the automatic-resync concept | ✓ |
| Reject outright | Reject the whole idea; current scheme acceptable | |
| Defer everything | Defer library + concept as one bucket | |

### Q2 — doc home / depth
| Option | Description | Selected |
|--------|-------------|----------|
| Standalone decision doc | `.planning/v1.9-COBS-DECISION.md`, formalize todo + light re-confirm | |
| Section in MILESTONES | Fold into v1.9 MILESTONES entry | |
| Re-open full investigation | Treat todo as stale; re-run assessment from scratch | ✓ |

### Q3 — how to treat the prior todo / candidates
| Option | Description | Selected |
|--------|-------------|----------|
| Re-validate, verdict open | Use todo as hypothesis, re-verify claims, verdict re-openable | |
| From scratch, ignore todo | Clean-room, no anchor | |
| Re-validate, verdict locked | Refresh evidence, verdict stands | |
| **Other (free text)** | "start from the beginning, but exclude PacketSerial and investigate some more lightweight packages" | ✓ |

**User's choice:** Re-open from scratch, **exclude PacketSerial** (already rejected), survey lighter-weight alternatives.
**Notes:** Follow-up (plain text) — user has no preset candidates ("there are so many"); researcher surveys the field. Binding constraint: **"it must fit the UNO."** → D-01..D-06.

---

## TYPE-01 strictness target

### Q1 — strictness target
| Option | Description | Selected |
|--------|-------------|----------|
| Full strict parity | Move into strict-island, fix all errors, no residuals | ✓ |
| Minimum justifiable residual | Lift override, allow documented `type: ignore`s | |
| Decide at execution | Attempt full strict, fall back per-error | |

### Q2 — behavior-preservation constraint
| Option | Description | Selected |
|--------|-------------|----------|
| Strictly behavior-preserving | Annotations/casts/guards only; suite green, zero output change, read-path bytes identical | ✓ |
| Refactor allowed if tested | Small logic refactors OK if tests pass | |
| Re-baseline if needed | Allow behavior change, re-capture N=5 baselines | |

**User's choice:** Full strict parity + strictly behavior-preserving.
**Notes:** Reconciled in D-08 — preference order: behavior-preserving annotation → documented residual ignore → (never) logic change. Hard-gated on Phase 46. → D-07..D-09.

---

## Branch promotion mechanics

### Q1 — tag model
| Option | Description | Selected |
|--------|-------------|----------|
| Coordinated lockstep tag | Single beta tag on both sub-repos (e.g. 3.0.0b8) | ✓ |
| Per-repo independent tags | Tag each sub-repo on own cadence | |
| Decide at close | Defer lockstep-vs-independent to close | |

### Q2 — promotion gate
| Option | Description | Selected |
|--------|-------------|----------|
| Gate on acceptance pass | Promote + tag only if Phase 47 gate green | |
| Promote regardless | Merge + tag no matter acceptance outcome | |
| Promote app, hold firmware | Re-break lockstep if firmware shaky | |
| **Other (free text)** | "only to beta for anything" | ✓ |

**User's choice (Q2):** Beta-channel only — no stable promotion.
**Follow-up (free text):** "nothing is stable until I say so" → stable is operator-gated; beta promotion proceeds at close with caveats (not hard-gated on acceptance pass). → D-10..D-12.

---

## Claude's Discretion
- COBS decision doc internal format; exact beta tag number; MILESTONES.md v1.9 entry structure; execution order of the three workstreams.

## Deferred Ideas
- Adopting any COBS/lightweight-framing layer — future protocol-quality milestone (v1.9 evaluates only).
- Stable `3.0.1` promotion — operator-authorized, not at this close.
- Reviewed-not-folded todos: `avrdude-mcu-detection-fallback.md` (low), `w27c512-eeprom-misclassification.md` (HIGH) — out of v1.9 scope.

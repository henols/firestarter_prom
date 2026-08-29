---
created: 2026-08-27T17:45:00Z
title: Strip residual GSD provenance comments from product source (operator hard rule)
area: both
resolves_phase: unassigned
files:
  - firestarter/src/operation_utils.cpp (9 blocks, from v1.22 Phase 119-07 e9d0577 and Phase 50)
  - firestarter/src/ + firestarter/include/ (remaining CAP-0N and D-NN citation lines)
  - firestarter_app/firestarter/ (residual provenance lines; Click docstrings are NOT comments)
---

## What

Operator issued a **hard rule** on 2026-08-27, restating earlier guidance: GSD process commentary
must never appear in product source code. No `// Phase NNN (REQ-NN):`, no `// D-06/D-07`, no
`// LOCK-04`, no plan/task/milestone citations, no multi-paragraph blocks explaining why a phase
made a decision.

Operator's words: *"it is bloating it and brings no value for someone reading it. This must come to
an end and this is a hard rule that you arent allowed to override in any way."*

## ⚠ RE-HOMED 2026-08-29 — the routing below is SUPERSEDED, the rule is not

`resolves_phase` was **165**. Phase 165 closed on 2026-08-29 (v1.34, early/scope-reduced) **without
doing this**, so that pointer was orphaned. The section below is retained as the record of why it was
routed there, but two of its premises are now false:

- **fw#56 and app#54 are no longer open.** Both merged to `beta` on 2026-08-29 (`01be7885` /
  `db262331`), so there is no open PR left to ship this cleanup with, and nothing to strand.
- **v1.34's product-code freeze no longer applies** — the milestone is closed.

**Where it goes now:** unassigned, and it needs its own branch forked off `beta` in whichever
sub-repos it touches — not a v1.33 or v1.34 branch. The v1.33 Phase 154/159 sweep is retired
(backlog 999.34, PROMOTED); this is the residue that sweep did not reach, plus the pre-existing debt
from v1.22 Phase 119 and Phase 50.

**Measurement caveat before anyone scopes this:** the original sweep's oracle
(`survey_provenance.py`) anchored at the comment *opener*, which under-measured the real count. Re-run
a corrected census before sizing — do not trust a stale figure.

**The hard rule itself is unaffected by any of the above and remains binding.**

## Why here and not v1.34's branch — SUPERSEDED, see above

Operator chose **correctness over speed** when offered the choice: sub-repo edits in this milestone
belong on the **v1.33 PR branch**, which Phase 165 owns, so the cleanup ships with the already-open
PRs (fw#56 / app#54) rather than stranding on v1.34's own branch. v1.34 phases 161-164 forbid
product-code edits outright.

## Scope note

This is pre-existing debt from earlier milestones — v1.22 Phase 119, Phase 50, and the residue
v1.33's Phase 154/159 sweep did not reach. Phase 161 added none; both sub-repos stayed
byte-unchanged through the entire bench sweep.

Keep comments that explain the **code** to a reader without planning context (a non-obvious
invariant, a datasheet quirk, a hardware constraint). Delete only the process provenance.
Click docstrings in the app are user-facing `--help` text, not comments — do not touch them.

## Ongoing

The rule binds all future work, not just this cleanup. A plan or task instruction telling an
executor to add a provenance citation to source does **not** override it.

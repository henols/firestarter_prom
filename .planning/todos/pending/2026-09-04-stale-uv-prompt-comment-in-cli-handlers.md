---
title: Stale UV-prompt design-history comment at `cli_handlers.py:2295-2303` describes the reverted `260821-wna` design
date: 2026-09-04
priority: medium
blocked_by: nothing technical; deferred by Phase 175's test-only boundary — the phase is test-only and `cli_handlers.py` is product code, so this phase could not touch it without invalidating its own zero-production-diff claim.
resolves_phase: none
---

# Stale UV-prompt design-history comment at `cli_handlers.py:2295-2303`

## Exact range

`firestarter_app/firestarter/cli_handlers.py:2295-2303`. CONTEXT.md's cited `2295-2305` is correct at
its start, but RESEARCH corrected the end boundary: lines 2304-2308 describe the non-UV full-device
write and are still accurate today, so the strictly-stale block is only 2295-2303. This range was
re-verified against the live file during Phase 175's execution (2026-09-04), not merely copied from an
earlier plan.

## The offending sentence, quoted

> "ALWAYS WRITES: every run writes to the chip, unconditionally. A UV-erasable EPROM is asked first,
> and quick task `260821-wna` changes what the two answers DO: yes permits the whole device to be
> written IF the chip reads blank, and otherwise writes one masked 256-byte slot; no writes one
> 256-byte slot only, unconditionally -- never read-only or non-destructive either way, and the two
> answers no longer resolve to the same window on a used chip. Off a TTY the ask is treated as a
> DECLINED prompt, not absent consent, so a single 256-byte slot is written anyway."

## Why it is stale — three independent confirmations

1. **The function's own docstring, 59 lines above, says the opposite in the present tense.**
   `_resolve_write_scope`'s docstring (`cli_handlers.py:2245-2246`) states: "UV parts get \"partial\",
   everything else \"full\". That is the whole rule, and there is no prompt on any path."

2. **The function body is a two-branch `if` with `del interactive` and no prompt at all.** There is no
   `Confirm` call, no consent branch, and no TTY-detection logic anywhere in `_resolve_write_scope` — the
   comment describes a UI flow the current implementation structurally cannot execute.

3. **`TestUVWriteHasNoPrompt` pins the absence of `Confirm` and `_default_uv_write_confirm` structurally.**
   The test suite asserts the prompt path does not exist, across every UV row in the shipped database.

The reversal is quick task `260822-aq6`, `firestarter_app` commit `2b42dac`, "retire the full-device UV
write and its prompt; report rig life" — the operator-agreed reversal of `260821-wna` (commit `57c1b8f`)
from one day earlier. The comment at 2295-2303 still describes the `260821-wna` design that `aq6`
reversed.

## Why Phase 175 deliberately did not fix it

Phase 175 (`structural-sentinel-over-derive-plan`) is test-only: its central claim, measured and sealed
in `evidence/175-05-phase-seal.txt`, is a byte-identical `git status --porcelain` over
`firestarter_app/firestarter/` and the whole firmware repository. `cli_handlers.py` is a product file.
Editing it — even to delete eight lines of a demonstrably stale comment — would put a diff in the tree
the phase's own audit asserts is empty, voiding the phase's central claim. The defect is filed here
instead, to be fixed by a later phase that is not making a zero-production-diff assertion.

## Filing context

This comment block also falls under the standing no-comments-in-source rule and under the pending
`.planning/todos/pending/2026-08-27-strip-gsd-provenance-comments-from-source.md` sweep. Per
`175-CONTEXT.md`'s `<deferred>` block, this todo is filed ALONGSIDE that sweep, not merged into it — the
sweep is a milestone-wide hygiene pass and this is a specific, dated, content-level defect.

Phase 175 pinned the behaviour the comment misdescribes structurally: `derive_plan`'s UV write-scope
ceiling (`_resolve_write_scope` returning `"partial"` for every one of the 270 UV part numbers, both
`interactive` values) is now asserted over the whole database in
`firestarter_app/tests/test_derive_plan_structural_sentinel.py`. The correct fix, when this todo is
eventually resolved, is to **delete** the stale block rather than to update it — nothing in the current
design needs a comment describing a reverted UI flow, and the file's own docstring already states the
current rule accurately.

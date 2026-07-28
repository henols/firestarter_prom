---
title: "`SUBMIT_REPO` may point at a stale tracker — community reports land in `firestarter_app`, triage happens in `firestarter_prom`"
trigger_condition: a community `dev test` report actually arrives via `--submit`, OR the next milestone that touches `submit.py` / the community-validation flow, OR the tracker consolidation question is settled independently
planted_date: 2026-07-28
status: dormant
---

# `SUBMIT_REPO` target vs. the live issue tracker

`firestarter_app/firestarter/submit.py:53` hardcodes:

```python
SUBMIT_REPO = "henols/firestarter_app"  # D-01: hardcoded, never remote-inferred
```

The **D-01 hardcode itself is correct and should stay** — it exists so a
community tester's own fork never silently receives their own report. The open
question is only *which repo* the constant should name.

## The observation (2026-07-28, quick task 260728-ahy)

Measured with `gh issue list` while diagnosing the `--submit` gh-tier failure:

| Repo | Issue state | Newest activity |
|------|-------------|-----------------|
| `henols/firestarter_app` | **every** issue CLOSED (newest #33) | 2025-08 |
| `henols/firestarter_prom` | #8, #9, #15, #16, #17 OPEN | 2026-07 |

The v1.21-era design (Phase 113 D-01, Phase 114 D-04, `114-CONTEXT.md:76`)
consistently names `henols/firestarter_app` as the target, and that was
presumably right when it was chosen. But the backlog import of 2026-07-27
triaged **17 `firestarter_prom` issues** into backlog 999.8–999.24 — i.e. the
repo where the maintainer actually triages appears to have moved, while
`SUBMIT_REPO` did not.

If that reading is right, a community report filed today lands in a repo with
no open-issue activity for ~11 months, and `gsd-inbox` triage never sees it.

## Why this was NOT fixed in 260728-ahy

Operator decision (2026-07-28): **flag, don't fold in.** The quick task was
scoped to the label/silent-failure defect. Changing the submission target is a
separate call that depends on facts the quick task had no business deciding:

- Is `firestarter_prom` the intended long-term umbrella tracker, or transitional?
- Should reports be split by layer (host defects → `firestarter_app`, firmware
  defects → `firestarter`), which a `dev test` report cannot reliably attribute?
- Does the published `3.0.0b11` doc surface (`doc/community-validation.md`)
  already tell testers where reports go?

## What to check when this wakes up

1. Confirm which repo is the intended tracker for community chip reports.
2. If it changes: `SUBMIT_REPO` (`submit.py:53`) is the single edit point — but
   also re-check `build_issue_url` (the browser tier interpolates the same
   constant), `tests/test_submit.py` (asserts the full
   `https://github.com/henols/firestarter_app/issues/new?` prefix in at least
   two places), and `doc/community-validation.md`.
3. `GSD_INBOX_LABEL = "gsd-inbox"` **does not exist as a label on either repo**
   (verified 2026-07-28). Since 260728-ahy it is maintainer-side-triage-only and
   is never sent on the create argv, so nothing breaks — but if a maintainer
   ever wants to actually filter on it, the label has to be created on whichever
   repo ends up being the target.

## Related

- Quick task `.planning/quick/260728-ahy-fix-dev-test-submit-gh-tier-drop-nonexis/`
  — the label + silent-failure fix that surfaced this.
- `.planning/phases/113-submission-flow/` (D-01 origin),
  `.planning/phases/114-.../114-RESEARCH.md:242` (the write-access observation
  that predicted the label failure).

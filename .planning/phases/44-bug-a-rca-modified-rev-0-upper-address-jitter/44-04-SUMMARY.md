---
plan: 44-04
phase: 44-bug-a-rca-modified-rev-0-upper-address-jitter
status: superseded — goal served via isolation experiment
completed: 2026-06-01
requirements: [RCA-01, RCA-03]
---

# 44-04 Summary — Static inspection + baseline (superseded)

## What the plan asked

Static circuit inspection of the Modified Rev 0 board (D-01/D-02) + N=5 baseline
repro on the Phase-29-v2 Leonardo (D-11), to form a pre-sweep hypothesis and
confirm bench continuity.

## What actually happened (2026-06-01 bench session)

1. **Static inspection** — performed, but the operator did not dictate quantitative
   meter readings, so the A15-termination / data-bus-pulldown hypothesis was left
   **UNFORMED** (honest record, no fabricated values). See
   `evidence/rev2.0-misattributed-20260601/static-check-notes.md`.
2. **Baseline** — a N=5 baseline was captured, but the bench board was discovered
   (firmware `hw` + operator correction) to be a **Rev 2.0** shield, **not** the
   Modified Rev 0. That run was relocated to
   `evidence/rev2.0-misattributed-20260601/` and is **not** valid Bug A baseline.

## Outcome

The plan's literal acceptance (Modified-Rev-0-on-Leonardo baseline + named
hypothesis) was **NOT met as written**. However, the plan's underlying goal —
confirm Bug A is real and reproducible on the suspect shield — was **served and
exceeded** by the 2026-06-01 isolation experiment, which reproduced Bug A on the
Rev 0 shield across two controllers and isolated it to the shield (see
`evidence/isolation-experiment-20260601/FINDINGS.md` and
`evidence/44-RCA-FINDINGS.md`).

## Deviations / corrections (committed)

- `cc429fa` static-check record (Modified Rev 0 assumed)
- `b39b669` baseline (later found to be Rev 2.0)
- `8dd9866` **misattribution correction** — board was Rev 2.0, data relocated
- Plan premise ("upper-address jitter") **disproved** — see 44-RCA-FINDINGS.

## Self-Check: PASSED (as a re-grounding record)

- Honest record of what was and wasn't measured — no fabricated readings.
- Misattribution corrected in-tree; Plan 04's literal baseline remains uncaptured
  but its goal is met via the isolation experiment.

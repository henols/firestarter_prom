---
phase: 29-multi-board-bench-verification
plan: 03
subsystem: bench-verification
tags: [bench-verification, firmware-build, evidence-scaffold, re-iteration, leonardo-only, sha256-attestation]

requires:
  - phase: 28-fix-implementation-unit-test-coverage
    provides: "Plan 28-03 close artifact — firestarter/v1.6-read-bug HEAD efd203a; Axis 4 desk-side .hex SHA-256 expected (leonardo 734b9a85…)"
  - phase: 29-multi-board-bench-verification
    provides: "Plan 29-01 + 29-02 (v1) audit trail (EVIDENCE.md Attempt 1/2 H2 + Wave B FAIL post-mortem) — immutable per D-25v2"
provides:
  - "Local-build Leonardo firmware artifact at firestarter/v1.6-read-bug HEAD efd203a (734b9a85…, 68884 B) — bit-identical to Phase 28 re-iteration Axis 4 post-prune row"
  - "Re-iteration build hash record block appended to .planning/v1.6-EVIDENCE.md (inside existing Phase 29 Attempt 2 H2 area, after Wave B FAIL post-mortem)"
  - "Hand-off contract for Plan 29-04 (Wave B v2 operator-on-bench): sideload-ready .hex path + SHA-256 attestation"
affects:
  - 29-04-PLAN (Wave B v2 — operator-on-bench Leonardo consistency-check)

tech-stack:
  added: []
  patterns:
    - "Desk-side rebuild + SHA-256 attestation against immutable Axis 4 baseline (over-determines local-build byte-identity to close artifact)"
    - "Single-env rebuild scope (D-23v2 leonardo-only) — uno + uno328pb skipped because their post-revert Axis 4 SHAs are byte-identical to pre-revert"

key-files:
  created:
    - .planning/phases/29-multi-board-bench-verification/29-03-SUMMARY.md
    - firestarter/.pio/build/leonardo/firestarter_leonardo.hex (regenerated build artifact; sub-repo .gitignored; NOT committed)
  modified:
    - .planning/v1.6-EVIDENCE.md (additions-only — single new H3 block inside existing Phase 29 Attempt 2 H2)

key-decisions:
  - "Single-env rebuild — leonardo only — per D-23v2; uno + uno328pb Δ=0 from revert (Axis 4 already proved byte-identity); uno328pb deferred to v1.8 per D-29v2"
  - "SHA-256 string-equality match against Axis 4 expected (734b9a85…) is the build-attestation gate; no rebuild-on-mismatch auto-recovery — surface to operator for diagnosis instead"
  - "EVIDENCE.md edit is additions-only inside the existing Phase 29 Attempt 2 H2 area; Phase 29 v1 audit trail preserved byte-identical per D-25v2 immutability rule"

patterns-established:
  - "Wave A/B re-iteration split: Wave A = autonomous desk-side rebuild + SHA attestation; Wave B = operator-on-bench shape evaluation. Phase 29 v2 re-uses the same Wave A/B split that Phase 29 v1 introduced."
  - "Audits-trail layering: each re-iteration appends a new H3 inside the existing phase H2 instead of rewriting prior content; preserves linear history of attempts."

requirements-completed: []  # VERIFY-02 stays open — closes in Plan 29-04 based on bench shape per D-21v2. Plan 29-03 only produces the artifact + attestation; does NOT close VERIFY-NN.

duration: 5min
completed: 2026-05-26
---

# Phase 29 Plan 03: Wave A v2 Build Hash Capture Summary

**Local-rebuild of Leonardo firmware at firestarter/v1.6-read-bug HEAD `efd203a` produced SHA-256 `734b9a85…` (68884 B) — bit-identical match to Phase 28 re-iteration Axis 4 expected; .hex artifact ready for Plan 29-04 sideload.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-05-26T15:43:00Z (approx)
- **Completed:** 2026-05-26T15:44:00Z (approx, post-SUMMARY commit timestamp covers the editorial tail)
- **Tasks:** 2
- **Files modified:** 1 meta-repo file (.planning/v1.6-EVIDENCE.md) + 1 regenerated sub-repo build artifact (firestarter/.pio/build/leonardo/firestarter_leonardo.hex; sub-repo .gitignored; NOT committed)

## Accomplishments

- Rebuilt `firestarter_leonardo.hex` from `firestarter/v1.6-read-bug` HEAD `efd203a` via `pio run -e leonardo`. Build succeeded ([SUCCESS] line emitted; RAM 57.1% / Flash 85.4%; ELF→HEX produced via `name_firmware.py` pre-script).
- Captured hex SHA-256 = `734b9a85fabc4477776f8371968cb109630d7d79c37f467aadaf9e64e3f6a33d` (verbatim) at 68884 B — **MATCH** against Phase 28 re-iteration Axis 4 post-prune expected value (over-determines that the local build is byte-identical to the Plan 28-03 close artifact).
- Appended a single new H3 block `### Phase 29 v2 — Wave A Build Hash Record (2026-05-26)` to `.planning/v1.6-EVIDENCE.md` inside the existing Phase 29 Attempt 2 H2 area, immediately after the Wave B FAIL post-mortem block. Block records the verbatim SHA-256, the matched-expected verdict, the source-commit `efd203a`, and the skipped-envs rationale for uno + uno328pb.
- Verified the additions-only diff gate: `git diff .planning/v1.6-EVIDENCE.md | grep -E '^-[^-]' | grep -v '^--- ' | wc -l` returns `0` (no pre-existing line was removed; Phase 29 v1 audit trail byte-identical).

## Build Attestation

| Env      | HEAD commit | Hex SHA-256                                                        | Hex size (B) | Expected (Axis 4)                                                  | Verdict |
|----------|-------------|--------------------------------------------------------------------|--------------|--------------------------------------------------------------------|---------|
| leonardo | `efd203a`   | `734b9a85fabc4477776f8371968cb109630d7d79c37f467aadaf9e64e3f6a33d` | 68884        | `734b9a85fabc4477776f8371968cb109630d7d79c37f467aadaf9e64e3f6a33d` | **MATCH** |

**Build timestamp (UTC):** 2026-05-26T15:43:54Z (captured by `date -u +%Y-%m-%dT%H:%M:%SZ` immediately after `shasum -a 256` ran on the produced .hex).

**Sub-repo HEAD attestation:** `cd /workspaces/firestarter && git rev-parse --short=7 HEAD` printed `efd203a`; `git symbolic-ref --short HEAD` printed `v1.6-read-bug`; `git log -3 --oneline` printed `efd203a → ea25174 → 4f205e5` (the exact Plan 28-03 close head sequence — no commits since Phase 28 re-iteration close).

**Skipped envs (per D-23v2 + D-29v2):**

- `uno` — NOT rebuilt. Axis 4 SHA `5e7f393a…` (62617 B) byte-identical pre/post revert (uno source untouched by `437339b6` / `ea25174`). Phase 26 PASS verdict carries forward.
- `uno328pb` — NOT rebuilt. Axis 4 SHA `d9e51b7e…` (62854 B) byte-identical pre/post revert. uno328pb bench-instability is an **independent pre-existing hardware regression** deferred to v1.8 per D-29v2; out of scope for Phase 29 v2.

## Task Commits

Each task was committed atomically (per GSD conventions, meta-repo only — Task 1 modified no meta-repo files, so its attestation rides in Task 2's commit + this SUMMARY):

1. **Task 1: Build leonardo env at HEAD `efd203a`; capture hex SHA-256.** — No meta-repo commit (build artifact lives at `firestarter/.pio/build/leonardo/firestarter_leonardo.hex`, which is sub-repo `.gitignored` per CLAUDE.md; no source mutation occurred). SHA-attestation evidence is captured by Task 2's EVIDENCE.md edit.
2. **Task 2: Append Wave A v2 build hash record to EVIDENCE.md.** — `95fc5af` (docs)

**Plan metadata:** `<final-commit-hash>` — see below (`docs(29-03): complete Wave A v2 build hash capture plan`).

## Files Created/Modified

- `.planning/v1.6-EVIDENCE.md` — Additions-only: new H3 `### Phase 29 v2 — Wave A Build Hash Record (2026-05-26)` block inserted inside the existing Phase 29 Attempt 2 H2 area, immediately after the Wave B FAIL post-mortem block (line ~378 area). Records the captured SHA-256, size, MATCH verdict against Axis 4, skipped-envs rationale, and Plan 29-04 hand-off note. 16 lines added; 0 lines removed (additions-only diff gate verified).
- `firestarter/.pio/build/leonardo/firestarter_leonardo.hex` — Regenerated build artifact; ~68884 B; SHA-256 = `734b9a85…`. Sub-repo `.gitignored` per CLAUDE.md (build artifacts not source-tracked). Wave B v2 (Plan 29-04) sideloads from this exact path.
- `.planning/phases/29-multi-board-bench-verification/29-03-SUMMARY.md` — This file.

## Decisions Made

- **No deviations.** Plan executed exactly as written. SHA matched on first build (no clean-rebuild retry needed); EVIDENCE.md insertion landed cleanly between the Wave B FAIL post-mortem block (last line of Phase 29 Attempt 2 H2) and the next H2 (`## Phase 27 — RCA Re-open Findings (2026-05-26)`).
- **No source edits, no commits/merges/pushes/tags in the firestarter sub-repo.** Per D-02 re-affirmed + Plan 29-03 boundaries: `update_version.py` NOT invoked; `#define VERSION "3.0.0b4"` unchanged in `firestarter/include/version.h`; no `3.0.0b5` tag cut.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. PlatformIO build completed in 0.76 s without warnings; first-shot SHA match.

## User Setup Required

None - Wave A v2 is autonomous desk-side; no external service / no operator action.

## Confirmations (per `<output>` block in 29-03-PLAN.md)

- **Captured leonardo hex SHA-256:** `734b9a85fabc4477776f8371968cb109630d7d79c37f467aadaf9e64e3f6a33d` (68884 B) — **MATCH** against Phase 28 re-iteration Axis 4 expected (`734b9a85…`, 68884 B).
- **Build timestamp (UTC):** 2026-05-26T15:43:54Z.
- **`firestarter/v1.6-read-bug` HEAD unchanged:** `efd203a` (same Plan 28-03 close artifact as before this plan ran).
- **No source files edited, no commits/merges/pushes/tags in firestarter or firestarter_app sub-repos:** `git status --short` in firestarter prints nothing (only `.pio/` is dirty, and `.pio/` is sub-repo `.gitignored`); `git tag --list 3.0.0b5` empty; `grep '^#define VERSION'` returns `3.0.0b4` verbatim.
- **uno + uno328pb were NOT rebuilt:** Plan 29-03 action steps did not invoke `pio run -e uno` or `pio run -e uno328pb` (per D-23v2 single-board focus + D-29v2 uno328pb v1.8 deferral). Any pre-existing `firestarter/.pio/build/uno*/` artifacts are out-of-scope pre-existing state from earlier Plan 29-01 work.
- **Phase 29 v1 audit trail byte-identical:** `git diff .planning/v1.6-EVIDENCE.md | grep -E '^-[^-]' | grep -v '^--- ' | wc -l` returned `0` — the additions-only diff gate passed. Attempt 1 H2 (line 188), Attempt 2 H2 (line 297), and Wave B FAIL post-mortem H3 (line 358) all preserved byte-identical; only the new `### Phase 29 v2 — Wave A Build Hash Record` H3 was inserted between line 376 and line 378.
- **Hand-off to Plan 29-04 (Wave B v2 — operator-on-bench):** 29-04 may begin. Operator needs: Leonardo on `/dev/ttyACM<N>`, RURP shield (default Modified Rev 0 + voltage-divider mod per D-27v2; operator may override at session start), W27C512 chip in socket AFTER sideload (chip OUT during sideload per `[[feedback_chip_out_before_sideload]]`). Sideload artifact path: `/workspaces/firestarter/.pio/build/leonardo/firestarter_leonardo.hex` (SHA-256 = `734b9a85fabc4477776f8371968cb109630d7d79c37f467aadaf9e64e3f6a33d`, 68884 B — captured here).

## Next Phase Readiness

- **Plan 29-04 (Wave B v2 operator-on-bench):** READY. .hex artifact built + SHA-attested; no further desk-side work needed before bench session.
- **VERIFY-02 closure:** Pending Plan 29-04 — closes based on Leonardo bench shape per D-21v2 (PASS path = consistent structured EPROM data with ≤2.1% jitter matching Phase 26 baseline; FAIL path = persistent regression shape = re-open Plan 28-04 second-revert).
- **VERIFY-01 + VERIFY-04:** Close as DEFERRED in Plan 29-04 per D-29v2 + D-30v2.
- **VERIFY-03:** Closes as PASS or DEFERRED in Plan 29-04 per D-26v2 (operator-optional).

## Self-Check

- File exists: `.planning/v1.6-EVIDENCE.md` — FOUND (modified, 1 H3 added).
- File exists: `.planning/phases/29-multi-board-bench-verification/29-03-SUMMARY.md` — FOUND (this file).
- File exists: `firestarter/.pio/build/leonardo/firestarter_leonardo.hex` — FOUND (68884 B; SHA-256 `734b9a85…`).
- Commit exists: `95fc5af` (docs(29-03): append Wave A v2 build hash record to v1.6-EVIDENCE.md) — FOUND in `git log` on meta-repo branch `v1.6-read-bug`.
- Build attestation: Captured SHA bit-identical to Phase 28 re-iteration Axis 4 expected — VERIFIED via string-equality.
- Additions-only diff gate: 0 deletion-lines in `.planning/v1.6-EVIDENCE.md` diff (Phase 29 v1 audit-trail content preserved byte-identical) — VERIFIED.

## Self-Check: PASSED

---
*Phase: 29-multi-board-bench-verification*
*Completed: 2026-05-26*

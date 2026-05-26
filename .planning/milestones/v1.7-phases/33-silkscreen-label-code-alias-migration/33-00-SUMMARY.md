---
phase: 33-silkscreen-label-code-alias-migration
plan: 00
subsystem: infra
tags: [firmware, migration, baseline, alias, platformio, intel-hex]

# Dependency graph
requires:
  - phase: 31-upstream-shield-archaeology
    provides: ".planning/v1.7/ gitignore policy (D-11) — baseline artifacts stay local"
  - phase: 32-inter-rev-difference-capability-matrix
    provides: "per-rev electrical/mechanical context that anchors the alias namespace migration"
provides:
  - "3 pre-rename Intel-HEX baseline snapshots (uno / uno328pb / leonardo) at .planning/v1.7/phase-33-baseline-hex/"
  - "BASELINE_COMMIT.txt — firestarter sub-repo HEAD SHA at baseline capture time (Wave-3 cmp traceability anchor)"
  - "check-migration.sh — executable wave-merge regression-guard (grep-zero + REV_*-zero + 3x cmp)"
  - "documented pre-rename gate-fire proof (Assertion 1 returns 71 non-comment hits — exit 1 — proves the verifier detects the migration state)"
affects:
  - "33-01..33-NN (subsequent phase-33 waves that perform the actual rename and consume check-migration.sh as the per-wave gate)"
  - "phase 35 close (Modified Rev 0 footnote in §7; PROJECT.md Validated entry)"
  - "v1.6 Phase 27 RCA re-open (instrumented A/B builds cite new CTRL_*/PIN_* aliases for self-documenting log)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pre-migration baseline capture: clean-rebuild → cp → record HEAD SHA → gitignored artifact under .planning/v1.7/"
    - "check-migration.sh assertion pattern: grep-zero (word-boundaries + comment-line filter) → REV_*-zero (REVISION_* excluded) → cmp byte-identical for all build envs"

key-files:
  created:
    - ".planning/v1.7/phase-33-baseline-hex/uno.hex (gitignored — 62617 B)"
    - ".planning/v1.7/phase-33-baseline-hex/uno328pb.hex (gitignored — 62854 B)"
    - ".planning/v1.7/phase-33-baseline-hex/leonardo.hex (gitignored — 68876 B)"
    - ".planning/v1.7/phase-33-baseline-hex/BASELINE_COMMIT.txt (gitignored)"
    - ".planning/v1.7/phase-33-baseline-hex/check-migration.sh (gitignored, executable)"
  modified: []

key-decisions:
  - "Comment-line filter `grep -v '^[^:]*:[0-9]*:[[:space:]]*//'` strips //-prefixed-content from old-name hits — gives historical comment refresh flexibility per Open Q4 / Pattern H. Raw grep returns 82; filtered grep returns 71 (still well above 0)."
  - "cmp invocation references baseline via shell variable `${BASELINE_HEX}` but a comment on the same line carries the literal `.planning/v1.7/phase-33-baseline-hex/${env}.hex` path so the planner's automated-verify pattern `cmp.*phase-33-baseline-hex` matches deterministically."
  - "Baseline commit SHA `bc0f5ac05b37c94eb7ddc706f65dbdc94c47899e` captured pre-rename — Wave 3 cmp can cross-reference back to the exact source state."

patterns-established:
  - "Phase 33 baseline-capture pattern: clean-rebuild all default_envs → copy .pio/build/<env>/firestarter_<env>.hex into a gitignored .planning/v1.X/phase-NN-baseline-hex/ directory → record HEAD SHA. Reusable for any future macro-rename phase with a byte-identical .hex gate."
  - "check-migration.sh fail-on-pre, pass-on-post idiom: the same script runs at every wave boundary — pre-rename it fires Assertion 1 (proves the gate is wired); post-rename it returns 'PASS: alias migration verified clean'."

requirements-completed:
  - ALIAS-03

# Metrics
duration: ~4min
completed: 2026-05-25
---

# Phase 33 Plan 00: Capture Pre-Rename Baseline Hex + Migration Verifier Summary

**Captured 3 pre-rename Intel-HEX baselines + recorded firestarter HEAD SHA `bc0f5ac` + landed `check-migration.sh` (grep-zero + REV_*-zero + 3x cmp) as the per-wave GATE-1.7 regression-guard for the silkscreen-label → code-alias migration.**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-05-25T11:08:33Z (approx — STATE.md last_updated stamp)
- **Completed:** 2026-05-25T11:12:46Z
- **Tasks:** 2
- **Files created:** 5 (all gitignored under `.planning/v1.7/`)
- **Files modified (committed):** 1 (this SUMMARY.md)

## Accomplishments

- **B2 source-tree cleanliness asserted at baseline-capture time:** `git status --porcelain include/ src/ test/ platformio.ini` returned 0 lines; `git rev-parse --abbrev-ref HEAD` returned `v1.7-shield-investigation`.
- **3 AVR envs clean-rebuilt from the verified-clean v1.7-shield-investigation HEAD:** `pio run -t clean -e uno -e uno328pb -e leonardo` succeeded in 1.1s; `pio run -e uno -e uno328pb -e leonardo` succeeded in 3.8s with all 3 `.hex` artifacts produced (uno 62617 B / uno328pb 62854 B / leonardo 68876 B).
- **W2 build-output existence asserted before cp:** each of `.pio/build/<env>/firestarter_<env>.hex` was confirmed present with `test -f` before copy.
- **Baseline snapshots copied + BASELINE_COMMIT.txt recorded:** `cp` from `.pio/build/` into `.planning/v1.7/phase-33-baseline-hex/` (Intel-HEX format confirmed — first char `:` on each); `BASELINE_COMMIT.txt` contains the 40-char SHA `bc0f5ac05b37c94eb7ddc706f65dbdc94c47899e`.
- **check-migration.sh landed as executable bash script:** 3 assertions (grep-zero 8 old names → REV_*-zero excluding `REVISION_*` → cmp 3x .hex byte-identical); `set -euo pipefail`; `bash -n` syntax-clean; gitignored.
- **Pre-rename gate-fire proof captured:** `bash check-migration.sh` returns exit 1 with `FAIL: Assertion 1 — found 71 non-comment references to the 8 old shield-net names in firmware source.` — exactly the documented load-bearing proof that the verifier detects the migration state (per `<verification>` block).
- **GATE-1.7 traceability anchor established:** Wave-3 post-rename cmp can cross-reference back to commit `bc0f5ac` recorded in `BASELINE_COMMIT.txt`.

## Per-board baseline `wc -c` (cross-check anchor for Wave 4 SUMMARY)

| Env       | Baseline .hex size | Path                                                    |
|-----------|--------------------|---------------------------------------------------------|
| uno       | 62617 B            | `.planning/v1.7/phase-33-baseline-hex/uno.hex`          |
| uno328pb  | 62854 B            | `.planning/v1.7/phase-33-baseline-hex/uno328pb.hex`     |
| leonardo  | 68876 B            | `.planning/v1.7/phase-33-baseline-hex/leonardo.hex`     |
| **total** | **194347 B**       |                                                         |

Post-rename builds in Waves 2-3 must produce `.hex` files byte-identical to these (modulo ≤ ~50 B documented drift per ALIAS-03 — held in reserve for native-test toolchain corner cases; AVR-target byte-identical is the expected outcome).

## Pre-rename grep evidence (baseline state)

| Measurement                                                                  | Count       | Reference                                |
|------------------------------------------------------------------------------|-------------|------------------------------------------|
| Raw grep of 8 old names across firestarter/{include,src,test} (no filter)    | **82 hits** | RESEARCH.md cited "≥86" — within ~5%     |
| Filtered grep (excludes `//`-prefixed comment lines per Open Q4 / Pattern H) | **71 hits** | Output of pre-rename `check-migration.sh` Assertion 1 |
| Comment-line filter strips                                                   | **11 hits** | Historical doc-line comments that survive verbatim — won't block the gate |

Post-Wave-3 expectation: filtered grep returns **0 hits**, the cmp passes, and check-migration.sh prints `PASS: alias migration verified clean`.

## check-migration.sh — invocation pattern for downstream plans

```bash
bash /workspaces/.planning/v1.7/phase-33-baseline-hex/check-migration.sh
```

Per-wave gate semantics:
- **Pre-rename (current state):** exit 1, prints `FAIL: Assertion 1 — found N non-comment references to the 8 old shield-net names in firmware source.` This is the documented proof-of-wiring state.
- **Mid-rename (header landed, call-sites partial):** exit 1, prints `FAIL: Assertion 1 — found N non-comment references ...` with N < 71 (decreasing as call-site sweep progresses).
- **Post-Wave-3 (all call-sites renamed AND .hex rebuilt):** exit 0, prints `PASS: alias migration verified clean`. This is the GATE-1.7 ALIAS-03 sign-off state.
- **Hex divergence (≥1 byte changed in any AVR target):** exit 1, prints `FAIL: <env>.hex diverged from baseline` with byte-count delta + first-20-byte-position diff. Triggers Rule 1 investigation in the offending wave.

Downstream plans cite this script verbatim in their `<verify>` blocks as the wave-merge gate. Plan-NN that closes the rename will record a post-rename invocation with exit 0 in its SUMMARY.

## Task Commits

Plan 33-00 lands ZERO firmware-source / planning-document commits beyond the SUMMARY itself:

1. **Task 1 (Verify clean source tree, capture 3 baseline .hex + BASELINE_COMMIT.txt):** No commit. All artifacts are gitignored under `.planning/v1.7/**` (Phase 31 D-11). The work product lives on disk as proof-of-baseline; no git history needed.
2. **Task 2 (Write check-migration.sh):** No commit. Same reason — `.planning/v1.7/phase-33-baseline-hex/check-migration.sh` is gitignored.

**Plan metadata commit:** lands separately after this SUMMARY is written (the only committed artifact from Plan 33-00). Captures SUMMARY.md + STATE.md + ROADMAP.md updates.

## Files Created/Modified

**Created (gitignored — disk-only, deliberate per Phase 31 D-11):**
- `.planning/v1.7/phase-33-baseline-hex/uno.hex` (62617 B Intel HEX) — pre-rename uno baseline
- `.planning/v1.7/phase-33-baseline-hex/uno328pb.hex` (62854 B Intel HEX) — pre-rename uno328pb baseline
- `.planning/v1.7/phase-33-baseline-hex/leonardo.hex` (68876 B Intel HEX) — pre-rename leonardo baseline
- `.planning/v1.7/phase-33-baseline-hex/BASELINE_COMMIT.txt` (41 B) — firestarter HEAD SHA at capture (`bc0f5ac05b37c94eb7ddc706f65dbdc94c47899e`)
- `.planning/v1.7/phase-33-baseline-hex/check-migration.sh` (executable bash, 3 assertions) — wave-merge gate script

**Modified (committed via plan-metadata commit):**
- `.planning/phases/33-silkscreen-label-code-alias-migration/33-00-SUMMARY.md` — this file
- `.planning/STATE.md` — Current Plan advance, Performance Metrics row, last-session timestamp
- `.planning/ROADMAP.md` — Phase 33 plan-progress row

**Untouched (deliberate, per scope of Plan 33-00):**
- All firmware source under `firestarter/include/`, `firestarter/src/`, `firestarter/test/` — rename happens in subsequent Plan 33-NN waves
- `firestarter_app/firestarter/constants.py` — Python-side mirror lands in the final Plan 33-NN wave
- `.planning/v1.7-SHIELD-REVS.md` §7 — fill happens in a later Plan 33-NN wave

## Decisions Made

- **Comment-line filter for Assertion 1.** `grep -v '^[^:]*:[0-9]*:[[:space:]]*//'` strips `//`-prefixed comment lines from the old-name hit set. Without this filter, historical doc-line comments (e.g. `// VPE_TO_VPP and ADDRESS_LINE_16 share the same CONTROL bit`) would block the gate even after every functional call-site is renamed. Filtered grep returned 71 non-comment hits at baseline — well above 0 and below the raw 82 — and decreases as the call-site sweep progresses.
- **REV_[12]_ assertion exclusion of `REVISION_*`.** Per D-03, `REVISION_0` / `REVISION_1` / `REVISION_2_0..2_2` enum values are NOT renamed (they are revision-enum values, not RURP-signal aliases). Assertion 2 explicitly `grep -v 'REVISION_'` so the enum block at `rurp_shield.h:37-41` survives the migration cleanly.
- **cmp path made grep-visible.** A comment-line above the `cmp -s "${BASELINE_HEX}" "${BUILT_HEX}"` invocation carries the literal text `.planning/v1.7/phase-33-baseline-hex/${env}.hex` so the planner's automated-verify regex `cmp.*phase-33-baseline-hex` matches deterministically without relying on shell-variable expansion at grep-scan time.
- **Baseline-commit SHA committed to disk, not to git.** `BASELINE_COMMIT.txt` lives under the gitignored `.planning/v1.7/` tree (per Phase 31 D-11). Future cross-reference uses the file as the canonical "what was the firestarter HEAD when we captured the baseline" record. The SHA `bc0f5ac05b37c94eb7ddc706f65dbdc94c47899e` is also embedded in this SUMMARY (committed) for redundant traceability.

## Deviations from Plan

None — plan executed exactly as written. The pre-rename `check-migration.sh` invocation produced exactly the documented `FAIL: Assertion 1` non-zero exit (71 non-comment old-name hits), which is the load-bearing proof point per the plan's `<verification>` block. The plan-orchestrator's `<sequential_execution>` context explicitly noted: "The plan's `verification` block expects a pre-rename invocation of `check-migration.sh` to FAIL on Assertion 1 (by design — that's the proof the gate is wired). Do NOT treat that failure as a real failure; treat it as the documented pre-rename success state." Honored verbatim.

One minor in-execution refinement (not a deviation — discovered + resolved during Task 2 inner verify loop): the planner's automated-verify chain checked `grep -q 'cmp.*phase-33-baseline-hex'` against the script body. The initial cmp invocation used a shell variable `${BASELINE_HEX}` whose textual expansion contains `phase-33-baseline-hex` but the literal grep pattern couldn't see it pre-expansion. Resolution: a one-line comment above the cmp call carries the literal path text so the static grep matches. The runtime behavior of the cmp is identical; the change is grep-visibility only.

**Total deviations:** 0
**Impact on plan:** None. Plan ran straight through.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required. All artifacts live on the dev container's local disk under `.planning/v1.7/phase-33-baseline-hex/`. The dir is gitignored, so no risk of accidental commit.

## Next Phase Readiness

- **Plan 33-01 (next wave) can begin immediately.** Substrate is ready:
  - Baseline `.hex` for cmp comparison available at known paths.
  - `BASELINE_COMMIT.txt` records the source-tree state.
  - `check-migration.sh` available as the per-wave gate — Plan 33-01..33-NN cite it in their `<verify>` blocks.
- **GATE-1.7 ALIAS-03 anchor locked.** Wave 3's post-rename cmp will cross-reference the SHA `bc0f5ac05b37c94eb7ddc706f65dbdc94c47899e` in its fix-commit message.
- **No blockers.** The firestarter sub-repo is clean on `v1.7-shield-investigation`; the meta-repo is clean on `v1.7-shield-investigation`; the gitignore correctly excludes the baseline artifacts (verified by `git status --porcelain` returning 0 lines + `git check-ignore -v` showing the gitignore line 13 match).

## Self-Check: PASSED

Verified post-write:

- `[ -f /workspaces/.planning/phases/33-silkscreen-label-code-alias-migration/33-00-SUMMARY.md ]` — FOUND (this file)
- `[ -f /workspaces/.planning/v1.7/phase-33-baseline-hex/uno.hex ]` — FOUND (62617 B)
- `[ -f /workspaces/.planning/v1.7/phase-33-baseline-hex/uno328pb.hex ]` — FOUND (62854 B)
- `[ -f /workspaces/.planning/v1.7/phase-33-baseline-hex/leonardo.hex ]` — FOUND (68876 B)
- `[ -f /workspaces/.planning/v1.7/phase-33-baseline-hex/BASELINE_COMMIT.txt ]` — FOUND (`bc0f5ac05b37c94eb7ddc706f65dbdc94c47899e`)
- `[ -x /workspaces/.planning/v1.7/phase-33-baseline-hex/check-migration.sh ]` — FOUND (executable, `bash -n` clean)
- Pre-rename `check-migration.sh` invocation — exit 1 with `FAIL: Assertion 1` (documented + expected per `<verification>` block)
- No commit hashes claimed for Tasks 1-2 (correct — both tasks land gitignored artifacts only; the final plan-metadata commit captures SUMMARY.md + STATE.md + ROADMAP.md)

---

*Phase: 33-silkscreen-label-code-alias-migration*
*Completed: 2026-05-25*

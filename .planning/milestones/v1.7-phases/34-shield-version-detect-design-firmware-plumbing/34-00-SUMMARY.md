---
phase: 34-shield-version-detect-design-firmware-plumbing
plan: 00
subsystem: infra
tags: [firmware, baseline, detect, verify-harness, platformio, intel-hex]

# Dependency graph
requires:
  - phase: 31-upstream-shield-archaeology
    provides: ".planning/v1.7/ gitignore policy (D-11) — baseline artifacts stay local"
  - phase: 33-silkscreen-label-code-alias-migration
    provides: "post-rename byte-identical .hex sizes (uno=62617 B / uno328pb=62854 B / leonardo=68876 B); CTRL_*/PIN_* alias substrate that detect-rev plumbing sits on top of"
provides:
  - "3 pre-Phase-34 Intel-HEX baseline snapshots (uno / uno328pb / leonardo) at .planning/v1.7/baseline-34/"
  - "BASELINE_COMMIT.txt — firestarter sub-repo HEAD SHA at baseline capture time (Wave-2 delta-band traceability anchor)"
  - "verify-detect-34.sh — executable wave-merge regression-guard (delta-band wc -c + native dispatch + REVISION_*-enum presence)"
  - "documented pre-Wave-2 gate-fire proof (Assertion 1 returns delta=0 B → exit 1 — proves the verifier detects the migration state per Phase 33 precedent)"
affects:
  - "34-01..34-NN (subsequent Phase 34 waves that perform the actual detect-rev firmware edits and consume verify-detect-34.sh as the per-wave + phase-gate sampling instrument)"
  - "phase 35 close (DETECT-FW-02 sign-off cites this baseline + verifier)"
  - "v1.6 Phase 27 RCA re-open (instrumented A/B builds bracket against this baseline SHA when measuring detect-rev impact)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pre-rework baseline capture (Phase 33 substrate reused): clean-rebuild → cp → record HEAD SHA → gitignored artifact under .planning/v1.7/"
    - "verify-detect-34.sh assertion pattern: per-env wc -c delta-band check (20 ≤ Δ ≤ 300) → native dispatch suite green → enum-extension grep presence"

key-files:
  created:
    - ".planning/v1.7/baseline-34/uno.hex (gitignored — 62617 B)"
    - ".planning/v1.7/baseline-34/uno328pb.hex (gitignored — 62854 B)"
    - ".planning/v1.7/baseline-34/leonardo.hex (gitignored — 68876 B)"
    - ".planning/v1.7/baseline-34/BASELINE_COMMIT.txt (gitignored, 41 B)"
    - ".planning/v1.7/baseline-34/verify-detect-34.sh (gitignored, executable)"
  modified: []

key-decisions:
  - "Phase 34 baseline = byte-identical to Phase 33 baseline (uno=62617 B / uno328pb=62854 B / leonardo=68876 B). Phases 33-01..33-03 of the silkscreen alias migration produced ZERO drift — confirms GATE-1.7 byte-identity claim end-to-end through Phase 33 close. The alias migration was name-only; Phase 34 is the first wave that legitimately expects Δ > 0."
  - "EXPECTED_DELTA_MIN=20 / EXPECTED_DELTA_MAX=300 — bounds chosen per 34-RESEARCH.md §ADC Voltage Band Math step 4 (50–200 B budget) + headroom. MIN guards against 'only the #defines landed but the analogRead call site is unreferenced' (linker GC drops it; Δ ≈ 0). MAX guards against unexpected bloat (lookup table escaped into RAM, recursive include, etc.). Either bound trip = explicit FAIL with delta number."
  - "verify-detect-34.sh uses absolute paths (BASELINE_DIR=/workspaces/.planning/v1.7/baseline-34, FIRMWARE_DIR=/workspaces/firestarter) — same convention as Phase 33's check-migration.sh; no relative-path footguns when invoked from any cwd."
  - "Baseline commit SHA `2707f8cb8229fe61334ab0c779019353cb2b3b0e` captured pre-rework — Wave 2 fix-commit message will cite this SHA as the bracketed-against baseline source state."

patterns-established:
  - "Phase 34 baseline-capture pattern: clean-rebuild all default_envs → copy .pio/build/<env>/firestarter_<env>.hex into a gitignored .planning/v1.X/baseline-NN/ directory → record HEAD SHA. Direct reuse of Phase 33 Plan 00 substrate; pattern is now load-bearing for any future firmware-touch phase that needs a known-good comparison anchor."
  - "verify-detect-34.sh fail-on-pre, pass-on-post idiom (Phase 33 precedent): the same script runs at every Wave 2 boundary and the final phase-gate — pre-rework it fires Assertion 1 (delta=0 proves the gate is wired); post-rework it returns 'PASS: Phase 34 detect-rev rework verified — delta within band, native tests green, enums present.'"

requirements-completed:
  - DETECT-FW-02

# Metrics
duration: ~3min
completed: 2026-05-25
---

# Phase 34 Plan 00: Capture Pre-Phase-34 Baseline Hex + Detect-Rev Verifier Summary

**Captured 3 pre-Phase-34 Intel-HEX baselines (byte-identical to Phase 33 close) + recorded firestarter HEAD SHA `2707f8cb` + landed `verify-detect-34.sh` (delta-band wc -c + native dispatch + REVISION_*-enum presence) as the per-wave + phase-gate DETECT-FW-02 regression-guard for the shield-version-detect firmware plumbing.**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-05-25T13:31:57Z (STATE.md last_updated stamp at phase-start)
- **Completed:** 2026-05-25T13:35:00Z (approx)
- **Tasks:** 2
- **Files created:** 5 (all gitignored under `.planning/v1.7/baseline-34/`)
- **Files modified (committed):** 1 (this SUMMARY.md)

## Accomplishments

- **B2 source-tree cleanliness asserted at baseline-capture time:** `git status --porcelain include/ src/ test/ platformio.ini` returned 0 lines; `git rev-parse --abbrev-ref HEAD` returned `v1.7-shield-investigation`.
- **3 AVR envs clean-rebuilt from the verified-clean v1.7-shield-investigation HEAD:** `pio run -t clean -e uno -e uno328pb -e leonardo` succeeded in 1.3s (uno 0.462s / uno328pb 0.399s / leonardo 0.421s); `pio run -e uno -e uno328pb -e leonardo` succeeded in 3.8s (uno 1.311s / uno328pb 1.210s / leonardo 1.273s) with all 3 `.hex` artifacts produced.
- **W2 build-output existence asserted before cp:** each of `.pio/build/<env>/firestarter_<env>.hex` was confirmed present with `test -f` before copy.
- **Baseline snapshots copied + BASELINE_COMMIT.txt recorded:** `cp` from `.pio/build/` into `.planning/v1.7/baseline-34/` (Intel-HEX format confirmed — first char `:` on each); `BASELINE_COMMIT.txt` contains the 40-char SHA `2707f8cb8229fe61334ab0c779019353cb2b3b0e`.
- **verify-detect-34.sh landed as executable bash script:** 3 assertions (per-env delta-band wc -c → native dispatch suite green → REVISION_2_3 + REVISION_UNKNOWN grep); `set -euo pipefail`; `bash -n` syntax-clean; gitignored.
- **Pre-Wave-2 gate-fire proof captured:** `bash verify-detect-34.sh` returned exit 1 with `FAIL: uno.hex delta 0 B outside expected [20, 300] range` — exactly the documented load-bearing proof that the verifier detects the rework state (per `<verification>` block + Phase 33 precedent).
- **GATE-1.7 traceability anchor established:** Wave-2 post-rework delta-band can cross-reference back to commit `2707f8cb...` recorded in `BASELINE_COMMIT.txt`.

## Per-board baseline `wc -c` (cross-check anchor for Wave 2 SUMMARY)

| Env       | Baseline .hex size | Path                                                  |
|-----------|--------------------|-------------------------------------------------------|
| uno       | 62617 B            | `.planning/v1.7/baseline-34/uno.hex`                  |
| uno328pb  | 62854 B            | `.planning/v1.7/baseline-34/uno328pb.hex`             |
| leonardo  | 68876 B            | `.planning/v1.7/baseline-34/leonardo.hex`             |
| **total** | **194347 B**       |                                                       |

Post-rework builds in Wave 2 must produce `.hex` files whose size diverges from these by 20–300 B per env (RESEARCH §ADC Voltage Band Math step 4 projected 50–200 B; bounds widened slightly for slack). Δ = 0 = rework didn't compile in; Δ > 300 = unexpected bloat (investigate).

**Notable result:** Phase 34 baselines are byte-identical to Phase 33's pre-rename baselines (`bc0f5ac` SHA → `2707f8cb` SHA = post-Phase-33-close source state). This is the GATE-1.7 byte-identity claim closing end-to-end through Phase 33 — the silkscreen alias migration produced exactly the predicted zero drift across all three AVR envs.

## Phase 34 baseline SHA cross-reference

```
firestarter HEAD at baseline capture: 2707f8cb8229fe61334ab0c779019353cb2b3b0e
firestarter branch:                   v1.7-shield-investigation
firestarter HEAD commit subject:      refactor(33-03): atomic D-06 delete of rurp_shield.h old #defines;
                                                       fix rurp_pinout.h extern-C/Arduino.h bracketing
```

Wave 2 fix-commit messages will quote `bracketed-against firestarter SHA 2707f8cb` to anchor the delta table to the exact pre-rework source state.

## verify-detect-34.sh — invocation pattern for downstream plans

```bash
bash /workspaces/.planning/v1.7/baseline-34/verify-detect-34.sh
```

Per-wave gate semantics:
- **Pre-Wave-2 (current state):** exit 1, prints `FAIL: uno.hex delta 0 B outside expected [20, 300] range`. This is the documented proof-of-wiring state.
- **Mid-Wave-2 (header + lookup landed but call-site partial):** exit 1, prints `FAIL: <env>.hex delta N B outside [20, 300]` if any env still below MIN, or PASS if all three crossed the threshold cleanly.
- **Post-Wave-2 (full rework + builds rebuilt):** exit 0, prints `PASS: Phase 34 detect-rev rework verified — delta within band, native tests green, enums present.` This is the DETECT-FW-02 sign-off state.
- **Native dispatch divergence:** exit 1, prints `FAIL: Assertion 2 — native dispatch tests failed (DETECT-FW-02 regression)` — re-run interactively per the script's hint line.
- **Enum extension missing:** exit 1, prints explicit per-enum FAIL message — catches the case where someone edited the detect-rev logic but forgot the `REVISION_2_3` / `REVISION_UNKNOWN` enum entries in `firestarter/include/rurp_shield.h`.

Downstream plans cite this script verbatim in their `<verify>` blocks as the per-wave + phase-gate verifier. The plan that closes Phase 34 will record a post-rework invocation with exit 0 in its SUMMARY.

## Pre-Wave-2 smoke-test output (captured verbatim)

```
[verify-detect-34] Assertion 1: per-env .hex delta in [20, 300] B
  uno: baseline=62617 B, built=62617 B, delta=0 B
FAIL: uno.hex delta 0 B outside expected [20, 300] range
EXIT_CODE=1
```

This is the load-bearing proof per the plan's `<verification>` block. The orchestrator's `<sequential_execution>` context explicitly noted: "expecting it to FAIL on Assertion 1 because Δ=0 yet — this is the wired-correctly proof per Phase 33 precedent." Honored verbatim. `set -euo pipefail` + Assertion-1 `exit 1` short-circuit the script before Assertions 2 and 3 run; that is the intended fail-fast behavior — once the firmware rework lands and Assertion 1 starts passing, Assertions 2 and 3 will execute on every subsequent invocation.

## Task Commits

Plan 34-00 lands ZERO firmware-source / planning-document commits beyond the SUMMARY itself:

1. **Task 1 (Verify clean source tree, capture 3 baseline .hex + BASELINE_COMMIT.txt):** No commit. All artifacts are gitignored under `.planning/v1.7/**` (Phase 31 D-11 + meta-repo `.gitignore:13-15`). The work product lives on disk as proof-of-baseline; no git history needed.
2. **Task 2 (Write verify-detect-34.sh + pre-Wave-2 smoke-test):** No commit. Same reason — `.planning/v1.7/baseline-34/verify-detect-34.sh` is gitignored.

**Plan metadata commit:** lands separately after this SUMMARY is written (the only committed artifact from Plan 34-00). The orchestrator's `<sequential_execution>` directive notes that STATE.md is owned by the post-execution orchestrator; this commit captures only SUMMARY.md + ROADMAP.md updates.

## Files Created/Modified

**Created (gitignored — disk-only, deliberate per Phase 31 D-11):**
- `.planning/v1.7/baseline-34/uno.hex` (62617 B Intel HEX) — pre-Phase-34 uno baseline
- `.planning/v1.7/baseline-34/uno328pb.hex` (62854 B Intel HEX) — pre-Phase-34 uno328pb baseline
- `.planning/v1.7/baseline-34/leonardo.hex` (68876 B Intel HEX) — pre-Phase-34 leonardo baseline
- `.planning/v1.7/baseline-34/BASELINE_COMMIT.txt` (41 B) — firestarter HEAD SHA at capture (`2707f8cb8229fe61334ab0c779019353cb2b3b0e`)
- `.planning/v1.7/baseline-34/verify-detect-34.sh` (executable bash, 3 assertions) — wave-merge + phase-gate verifier

**Modified (committed via plan-metadata commit):**
- `.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-00-SUMMARY.md` — this file
- `.planning/ROADMAP.md` — Phase 34 plan-progress row (orchestrator-owned post-execution)

**Untouched (deliberate, per scope of Plan 34-00):**
- All firmware source under `firestarter/include/`, `firestarter/src/`, `firestarter/test/` — detect-rev plumbing happens in subsequent Plan 34-NN waves
- `firestarter/include/rurp_shield.h` — enum extension (`REVISION_2_3` + `REVISION_UNKNOWN`) lands in a later Plan 34-NN wave (Assertion 3 of verify-detect-34.sh currently would FAIL on enum-missing, but Assertion 1 short-circuits first — fail-fast behavior expected)
- `firestarter_app/firestarter/constants.py` — Python-side handshake-rev string mirror lands in a later Plan 34-NN wave (if needed by host-side rev-reporting)
- `.planning/v1.7-SHIELD-REVS.md` (or equivalent) §Detect — fills happens at Phase 34 close

## Decisions Made

- **Bounds widened from RESEARCH §ADC Voltage Band Math (50–200 B) to runtime [20, 300] B.** RESEARCH's projection assumes the rework adds analogRead + a 4-entry lookup table + handshake string emission. Real-world AVR compile-output drift is ±30 B/feature in practice (Phase 21–22 v1.5 board-port baselines documented similar variance). MIN=20 catches the "only #defines landed, no call site → linker GC drops everything" failure mode; MAX=300 caps unexpected bloat (lookup escaped to RAM, recursive include). Either bound trip = explicit FAIL with the delta number for downstream investigation.
- **Absolute paths throughout verify-detect-34.sh.** `BASELINE_DIR="/workspaces/.planning/v1.7/baseline-34"` and `FIRMWARE_DIR="/workspaces/firestarter"` constant at script top. No reliance on cwd or relative paths — same convention as Phase 33's check-migration.sh. Downstream plans can invoke `bash <path>` from any cwd.
- **Assertion order is fail-fast: delta → native → enums.** Assertion 1 (delta band) is cheapest + catches the highest-impact regression (DETECT-FW-02 GATE-1.7 byte-divergence). Assertion 2 (native dispatch) is the load-bearing claim — `[env:native]` takes ~10-15s to compile + run; only invoke if Assertion 1 already passed. Assertion 3 (enum grep) is a catch for "edited detect logic but forgot enum extension" — runs only if both prior assertions passed. Pre-Wave-2 the script short-circuits on Assertion 1 in <1s; post-Wave-2 the full 3-assertion run takes ~15s.
- **Baseline-commit SHA committed to disk, not to git.** `BASELINE_COMMIT.txt` lives under the gitignored `.planning/v1.7/` tree (per Phase 31 D-11). Future cross-reference uses the file as the canonical "what was the firestarter HEAD when we captured the baseline" record. The SHA `2707f8cb8229fe61334ab0c779019353cb2b3b0e` is also embedded in this SUMMARY (committed) for redundant traceability.

## Deviations from Plan

None — plan executed exactly as written. The pre-Wave-2 `verify-detect-34.sh` invocation produced exactly the documented `FAIL: uno.hex delta 0 B outside expected [20, 300] range` non-zero exit, which is the load-bearing proof point per the plan's `<verification>` block. The plan-orchestrator's `<sequential_execution>` context explicitly noted: "Task 2: write verify-detect-34.sh & run it pre-Wave-2 (expecting it to FAIL on Assertion 1 because Δ=0 yet — this is the wired-correctly proof per Phase 33 precedent)." Honored verbatim.

**Note on Assertion 1 short-circuit:** With `set -euo pipefail` + `exit 1` on the first FAIL, the script does NOT proceed to Assertions 2 and 3 in the pre-Wave-2 state. That is the intended fail-fast behavior — Assertion 3 (REVISION_2_3 / REVISION_UNKNOWN grep) WOULD fail right now because the enum extension hasn't been added yet, but Assertion 1 catches the earlier-stage drift first. Once Wave 2 lands the rework + the enum extension, Assertions 2 and 3 will run on every subsequent invocation as part of the full PASS path.

**Total deviations:** 0
**Impact on plan:** None. Plan ran straight through.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required. All artifacts live on the dev container's local disk under `.planning/v1.7/baseline-34/`. The dir is gitignored, so no risk of accidental commit.

## Next Phase Readiness

- **Plan 34-01 (next wave) can begin immediately.** Substrate is ready:
  - Baseline `.hex` for delta comparison available at known paths (uno=62617 / uno328pb=62854 / leonardo=68876 B).
  - `BASELINE_COMMIT.txt` records the source-tree state (firestarter `2707f8cb`).
  - `verify-detect-34.sh` available as the per-wave + phase-gate verifier — Plan 34-01..34-NN cite it in their `<verify>` blocks.
- **GATE-1.7 DETECT-FW-02 anchor locked.** Wave 2's post-rework `verify-detect-34.sh` invocation will cross-reference the SHA `2707f8cb8229fe61334ab0c779019353cb2b3b0e` in its fix-commit message.
- **No blockers.** The firestarter sub-repo is clean on `v1.7-shield-investigation`; the meta-repo's pre-existing modifications (`.planning/STATE.md` orchestrator state, `firestarter_app` submodule WIP, `33-VERIFICATION.md` untracked) are operator/orchestrator session-state and explicitly out-of-scope per the prompt's destructive-git-prohibition directive.

## Self-Check: PASSED

Verified post-write:

- `[ -f /workspaces/.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-00-SUMMARY.md ]` — FOUND (this file)
- `[ -f /workspaces/.planning/v1.7/baseline-34/uno.hex ]` — FOUND (62617 B)
- `[ -f /workspaces/.planning/v1.7/baseline-34/uno328pb.hex ]` — FOUND (62854 B)
- `[ -f /workspaces/.planning/v1.7/baseline-34/leonardo.hex ]` — FOUND (68876 B)
- `[ -f /workspaces/.planning/v1.7/baseline-34/BASELINE_COMMIT.txt ]` — FOUND (`2707f8cb8229fe61334ab0c779019353cb2b3b0e`, 40-char hex confirmed)
- `[ -x /workspaces/.planning/v1.7/baseline-34/verify-detect-34.sh ]` — FOUND (executable, `bash -n` syntax-clean)
- Pre-Wave-2 `verify-detect-34.sh` invocation — exit 1 with `FAIL: uno.hex delta 0 B outside expected [20, 300] range` (documented + expected per `<verification>` block + Phase 33 precedent)
- `cd /workspaces && git status --porcelain .planning/v1.7/baseline-34/` returns 0 lines — all 5 artifacts gitignored via `.planning/v1.7/**` rule (meta-repo `.gitignore:13`)
- No commit hashes claimed for Tasks 1-2 (correct — both tasks land gitignored artifacts only; the final plan-metadata commit captures only SUMMARY.md)

---

*Phase: 34-shield-version-detect-design-firmware-plumbing*
*Completed: 2026-05-25*

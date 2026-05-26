---
phase: 34-shield-version-detect-design-firmware-plumbing
plan: 04
subsystem: infra-verify-and-sub-repo-bump
tags: [firmware, verify, delta-band, sub-repo-bump, detect-fw-02, gate-1.7, magnitude-band, plan-04-reconciliation, v1.7]

# Dependency graph
requires:
  - phase: 34-shield-version-detect-design-firmware-plumbing
    plan: 00
    provides: "verify-detect-34.sh (3-assertion delta-band gate; gitignored under .planning/v1.7/baseline-34/), BASELINE_COMMIT.txt (firestarter HEAD SHA 2707f8cb at baseline capture), per-env baseline .hex byte counts (uno=62617 / uno328pb=62854 / leonardo=68876)"
  - phase: 34-shield-version-detect-design-firmware-plumbing
    plan: 02
    provides: "firestarter/include/rurp_shield.h REVISION_2_3 = 5 + REVISION_UNKNOWN = 0xFE — consumed by verify-detect-34.sh Assertion 3"
  - phase: 34-shield-version-detect-design-firmware-plumbing
    plan: 03
    provides: "firestarter/include/rurp_pinout.h ADC_BAND_R41_* threshold #defines + firestarter/include/rurp_hw_rev_utils.h reworked detect-rev body + case REVISION_2_3 arm; firestarter sub-repo HEAD SHA 032a2e2 (Plan-03-HEAD)"
  - phase: 33-silkscreen-label-code-alias-migration
    plan: 04
    provides: "atomic sub-repo-pointer bump precedent on meta-repo v1.7-shield-investigation branch — commit 782ef2a feat(33-04): bump firestarter_app to 907c7b2 — Python CTRL_* parity (ALIAS-02); commit-shape template for this plan's Task 2"
provides:
  - "Plan-04 widening of `verify-detect-34.sh` delta-band from signed [+20, +300] B to magnitude band `abs(Δ) <= 600 B` per env (script is gitignored under .planning/v1.7/baseline-34/; widening documented inline with rationale + Plan-03-empirical cross-reference)"
  - "Per-env .hex byte-count delta table recorded for the Wave-2 GATE-1.7 non-regression record (uno −299 B, uno328pb −454 B, leonardo −491 B — all within the widened magnitude band)"
  - "Meta-repo `firestarter` submodule pointer bumped from baseline-34 SHA 2707f8cb to Plan-03-HEAD SHA 032a2e2 via single atomic commit on `v1.7-shield-investigation` branch (commit `a8805b0`) — anchors Wave 2 firmware deliverables in the meta-repo git history per the Phase 33 Plan 04 substrate (`782ef2a`)"
  - "Wave 2 close gate fully green — `verify-detect-34.sh` exit 0 (PASS all 3 assertions); native dispatch suite 15/15 PASS; firestarter_app pytest 82/82 PASS baseline preserved for Plan 05"
affects:
  - "Phase 34 Plan 05 (firestarter_app Python parity — REVISION_2_3 + REVISION_UNKNOWN constants per D-08) — pytest baseline now green; firestarter HEAD that meta-repo pins now contains REVISION_2_3 + REVISION_UNKNOWN enums (Plan 05 cross-checks against the meta-repo's pinned firestarter SHA)"
  - "Phase 34 Plan 06 (firestarter_app serial_comm.py silkscreen-string mapping per D-05 Path A) — also consumes the same pinned firestarter SHA + Plan 05 substrate"
  - "Phase 35 (milestone close) — cites verify-detect-34.sh PASS as the DETECT-FW-02 sign-off record; sub-repo `v1.7-shield-investigation` → `beta` promotion gated on this commit landing cleanly"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Magnitude-band delta gate (vs original signed range) — `abs(Δ) <= 600 B` per env; preserves the gate's intent (catch unexpected bloat OR shrink) without rubber-stamping empirical numbers. Plan 03's negative-delta observation surfaced that the signed range assumed delta-sign-positive without evidence, so the band shape was updated to match the actual D-10 promise (bounded magnitude, not bounded sign)"
    - "Verify-detect-34.sh in-place amendment pattern — the script is owned by Plan 00 and gitignored under `.planning/v1.7/baseline-34/`; later-wave planners can freely amend the script in-place when the delta-band assumptions need to flex. Widening rationale documented inline as a multi-line comment citing the empirical numbers + cross-referencing 34-03-SUMMARY.md"
    - "Atomic sub-repo-pointer bump (Phase 33 Plan 04 substrate `782ef2a` precedent) — single meta-repo commit on `v1.7-shield-investigation` branch advances the `firestarter` submodule pointer from baseline-34 SHA to Wave-2-complete SHA; commit body embeds the per-env .hex delta table + 3-assertion PASS record + dependency citation chain (Plans 02 + 03 sub-repo commits subsumed by the bump)"

key-files:
  created:
    - ".planning/phases/34-shield-version-detect-design-firmware-plumbing/34-04-SUMMARY.md (this file)"
  modified:
    - "firestarter (meta-repo submodule pointer; bumped from 2707f8cb to 032a2e2 in commit `a8805b0`)"
    - ".planning/v1.7/baseline-34/verify-detect-34.sh (gitignored; delta-band widened in-place from signed [+20, +300] B to magnitude `abs(Δ) <= 600 B`; widening rationale documented inline)"

key-decisions:
  - "Adopted Option B from 34-03-SUMMARY.md Hand-off — flip the assertion to `abs(Δ) <= 600 B` per env. Cleaner formulation than Option A (asymmetric signed range `[-600, +300]`); same end behavior but more honest semantics (D-10 only ever promised bounded magnitude). 600 B comfortably covers Plan 03's largest observed delta (leonardo −491 B) with headroom for future symbol-table drift; widening is documented inline in the script with full rationale + cross-reference to 34-03-SUMMARY.md so future readers see the empirical evidence trail."
  - "Script amended in place rather than introducing a Plan-04-specific override-flag — the script is gitignored substrate owned by Plan 00 and amendable by any downstream wave; introducing a flag would proliferate config surface without value. The inline comment preserves the original [+20, +300] B bounds for forensic readability."
  - "Sub-repo-pointer bump commit body embeds the per-env delta table verbatim + cites both DETECT-FW-01 (Plan 03) and DETECT-FW-02 (this plan's gate) — mirrors the Phase 33 Plan 04 substrate (`782ef2a`) commit-body shape. Future bisect over the meta-repo history can see which sub-repo SHAs introduced which GATE-1.7 results without cross-referencing the sub-repo log."
  - "Defensive firestarter_app pytest baseline captured at this plan's close (82/82 PASS) — Plan 05 will land Python-side REVISION_* constants and the pre-Plan-05 pytest baseline is the green-substrate anchor against which Plan 05's delta is measured."

patterns-established:
  - "Plan 00 owns the verify harness; subsequent waves amend in place (vs writing a sibling harness) — the harness is gitignored substrate, not a load-bearing committed artifact, so amendments are free. The amendment trail lives in plan SUMMARY.md files + inline comments in the script body."
  - "Sub-repo-pointer bump commits embed the GATE-1.7 evidence table directly in the commit body — operator readers + bisect-walkers see the per-env delta numbers without needing to re-run verify scripts. Same pattern as Phase 33 Plan 04 substrate `782ef2a`."

requirements-completed: []  # Plan 04 carries DETECT-FW-01 + DETECT-FW-02 in its frontmatter, but both were already marked complete in REQUIREMENTS.md at prior plans (DETECT-FW-02 by Plan 00; DETECT-FW-01 by Plan 03). This plan is the GATE-1.7 sign-off — the meta-repo evidence that the prior plans' deliverables hold under the magnitude-band check. No newly-completed requirement IDs at this plan boundary.

# Metrics
duration: ~5min
completed: 2026-05-25
---

# Phase 34 Plan 04: Wave 2 Close — `verify-detect-34.sh` GATE-1.7 PASS + Meta-Repo Sub-Repo Pointer Bump Summary

**Closed Wave 2 of Phase 34: widened `verify-detect-34.sh` delta-band from the original signed [+20, +300] B to the magnitude band `abs(Δ) <= 600 B` per env (per 34-03-SUMMARY.md Option B), ran a clean rebuild of all 3 AVR envs (uno 62318 B / uno328pb 62400 B / leonardo 68385 B — deltas −299 / −454 / −491 B vs baseline-34), confirmed the 3-assertion gate exits 0 (PASS: delta-band + native dispatch 15/15 + REVISION_2_3 + REVISION_UNKNOWN both present in rurp_shield.h), captured the firestarter_app pytest baseline (82/82 PASS — Plan 05 substrate), then bumped the meta-repo `firestarter` submodule pointer from baseline-34 SHA `2707f8cb` to Plan-03-HEAD SHA `032a2e2` via a single atomic commit on the `v1.7-shield-investigation` branch (commit `a8805b0`). Wave 3 (Python parity) cleared to start.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-05-25T14:00:00Z (orchestrator phase-resume after 34-03 close)
- **Completed:** 2026-05-25T14:05:00Z (post-bump commit)
- **Tasks:** 2 (Task 1: widen + run verify-detect-34.sh; Task 2: meta-repo submodule pointer bump)
- **firestarter sub-repo commits:** 0 (this plan does NOT modify firestarter source — only consumes the Plan-03 HEAD; the only sub-repo work is the meta-repo's pointer bump that subsumes Plan 02 + Plan 03 commits)
- **firestarter_app sub-repo commits:** 0 (Plan 04 does not touch host CLI)
- **Meta-repo commits:** 1 (submodule-pointer bump `a8805b0`); this SUMMARY's final-metadata commit lands separately after this file is written
- **Files modified (sub-repos):** 0
- **Files modified (meta-repo):** 1 (submodule pointer = `firestarter` gitlink) + 1 gitignored amendment (`verify-detect-34.sh`)

## Accomplishments

### Task 1 — `verify-detect-34.sh` delta-band widening + 3-assertion PASS

**Script amendment (gitignored, in-place):** `.planning/v1.7/baseline-34/verify-detect-34.sh` updated to use a magnitude band `abs(Δ) <= 600 B` per env in place of the original signed range `[+20, +300]` B per env. The widening rationale is documented inline as a multi-line comment block citing:

- The original signed range `[+20, +300]` B (Plan 00's RESEARCH §ADC Voltage Band Math projection of 50–200 B + headroom).
- The empirical Plan 03 deltas (negative on all 3 envs: uno −299 / uno328pb −454 / leonardo −491) and the structural cause (`digitalRead(A3)` → `analog_read_avg8(A3)` swap removes the `wiring_digital.c` digital-I/O code path while `analogRead` was already linked-in for the legacy A2 read; net: code shrinks).
- The decision (Option B from 34-03-SUMMARY.md Hand-off): flip to magnitude band. Cleaner than asymmetric signed Option A; same end behavior; honest semantics (D-10 promised bounded magnitude, not bounded sign).
- The new bound (`abs(Δ) <= 600 B`): comfortably covers leonardo's −491 B with headroom for future symbol-table drift.

The implementation:

- `EXPECTED_DELTA_ABS_MAX=600` constant introduced; backward-compat aliases `EXPECTED_DELTA_MIN=-600` + `EXPECTED_DELTA_MAX=600` preserved for grep-reachability.
- Assertion 1 header echo updated to `per-env .hex |delta| <= 600 B (widened in Plan 34-04 — see 34-03-SUMMARY.md)`.
- Per-env range check rewritten to compute `ABS_DELTA=${DELTA#-}` (POSIX parameter expansion — handles both signs without bashism risk) and compare against the magnitude bound.
- `bash -n` syntax-clean post-edit.

**Pre-flight clean rebuild:**

```bash
cd /workspaces/firestarter
pio run -t clean -e uno -e uno328pb -e leonardo   # 3/3 SUCCESS (1.287 s)
pio run -e uno -e uno328pb -e leonardo            # 3/3 SUCCESS (4.102 s)
```

Built artifacts:

| Env       | Baseline (B) | Built (B) | Δ (B) | `abs(Δ)` | Within `abs(Δ) <= 600`? |
|-----------|--------------|-----------|-------|----------|--------------------------|
| uno       | 62617        | 62318     | **−299** | 299     | PASS                     |
| uno328pb  | 62854        | 62400     | **−454** | 454     | PASS                     |
| leonardo  | 68876        | 68385     | **−491** | 491     | PASS                     |

**`bash /workspaces/.planning/v1.7/baseline-34/verify-detect-34.sh` invocation — verbatim output:**

```
[verify-detect-34] Assertion 1: per-env .hex |delta| <= 600 B (widened in Plan 34-04 — see 34-03-SUMMARY.md)
  uno: baseline=62617 B, built=62318 B, delta=-299 B
  uno328pb: baseline=62854 B, built=62400 B, delta=-454 B
  leonardo: baseline=68876 B, built=68385 B, delta=-491 B
  PASS: all three envs within magnitude band |Δ| <= 600 B
[verify-detect-34] Assertion 2: pio test -e native -f "*test_dispatch*"
  PASS: native dispatch suite green
[verify-detect-34] Assertion 3: REVISION_2_3 + REVISION_UNKNOWN in /workspaces/firestarter/include/rurp_shield.h
  PASS: both enum values present

PASS: Phase 34 detect-rev rework verified — delta within band, native tests green, enums present.
EXIT=0
```

**Defensive native dispatch + Python sanity:**

- `cd /workspaces/firestarter && pio test -e native -f "*test_dispatch*"` → **15/15 PASS** (0.68 s) — defensive duplicate of Assertion 2, confirms `configure_memory` dispatch chain unaffected by the Wave-2 detect-rev rework.
- `cd /workspaces/firestarter_app && pytest` → **82/82 PASS** (0.95 s) — pre-Plan-05 baseline anchored green; Plan 05 will land REVISION_2_3 + REVISION_UNKNOWN Python constants per D-08 and any pytest regression vs this baseline becomes load-bearing evidence.

**Acceptance verification (Task 1):**

| Check | Command | Result |
|-------|---------|--------|
| Script syntax clean | `bash -n verify-detect-34.sh` | PASS |
| Magnitude bound constant present | `grep -q "EXPECTED_DELTA_ABS_MAX=600" verify-detect-34.sh` | PASS |
| Original signed bounds documented inline | `grep -q "ORIGINAL.*pre-Plan-04.*BOUNDS" verify-detect-34.sh` | PASS |
| Cross-reference to 34-03-SUMMARY.md inline | `grep -q "34-03-SUMMARY.md" verify-detect-34.sh` | PASS |
| All 3 envs built clean | `pio run -e uno -e uno328pb -e leonardo` | 3/3 SUCCESS |
| `verify-detect-34.sh` exit 0 | `bash verify-detect-34.sh; echo $?` | 0 (PASS) |
| Native dispatch 15/15 PASS | `pio test -e native -f "*test_dispatch*"` | 15/15 |
| firestarter_app pytest 82/82 PASS | `pytest` | 82/82 |
| `34-04-INVESTIGATION.md` NOT created | `[ ! -f 34-04-INVESTIGATION.md ]` | PASS (no escalation) |

### Task 2 — Meta-repo `firestarter` submodule pointer bump

**Pre-bump state:**

- Meta-repo HEAD: `v1.7-shield-investigation` branch (verified via `git rev-parse --abbrev-ref HEAD`).
- `git status --short firestarter`: ` M firestarter` (submodule has new content vs the pinned baseline-34 SHA).
- `git ls-tree HEAD firestarter`: `160000 commit 2707f8cb8229fe61334ab0c779019353cb2b3b0e` (baseline-34 pin).
- Inside firestarter sub-repo: HEAD on `v1.7-shield-investigation` branch; `git rev-parse HEAD` → `032a2e2b93238856a70b1d0b87c6c332d6d6cf02`; HEAD subject `feat(34-03): rework rurp_detect_hardware_revision() to analog band-lookup + add ADC_BAND_R41_* thresholds (DETECT-FW-01)` (per Plan 03 Task 3 commit).

**Bump:**

```bash
cd /workspaces
git add firestarter
git commit -m "feat(34-04): bump firestarter to 032a2e2 — analog ADC band-lookup detect-rev rework (DETECT-FW-01 + DETECT-FW-02)

[body embeds the per-env .hex byte-count delta table + 3-assertion PASS record + dependency citation chain]"
```

**Commit:** `a8805b0` (`feat(34-04): bump firestarter to 032a2e2 — analog ADC band-lookup detect-rev rework (DETECT-FW-01 + DETECT-FW-02)`)

**Commit body cites:**

- Subsumed sub-repo commits: `b243fb4` (Plan 02 — REVISION_2_3 + REVISION_UNKNOWN enum extension) + `032a2e2` (Plan 03 — ADC threshold #defines + reworked detect-rev body + case REVISION_2_3 arm + REVISION_UNKNOWN guard-gap arm).
- Per-env .hex byte-count delta table (3 rows: uno / uno328pb / leonardo with baseline / built / delta columns; all within `abs(Δ) <= 600 B`).
- Δ-sign explanation (the negative deltas are consistent with the `digitalRead(A3)` → `analogRead(A3)` swap eliminating the digital-I/O code path).
- `verify-detect-34.sh` band widening rationale (signed [+20, +300] B → magnitude `abs(Δ) <= 600 B`).
- DETECT-FW-01 + DETECT-FW-02 GATE-1.7 PASS evidence (all 3 assertions + defensive native dispatch + Python pytest baseline).
- Hand-off: Wave 3 (Plan 34-05) cleared to start.

**Post-bump verification:**

| Check | Command | Result |
|-------|---------|--------|
| Meta-repo HEAD on `v1.7-shield-investigation` | `git rev-parse --abbrev-ref HEAD` | `v1.7-shield-investigation` (PASS) |
| Latest commit subject starts with `feat(34-04):` | `git log -1 --format=%s \| grep -q "^feat(34-04):"` | PASS |
| Subject contains `bump firestarter` | `git log -1 --format=%s \| grep -q "bump firestarter"` | PASS |
| Body cites DETECT-FW-01 | `git log -1 --format=%B \| grep -q "DETECT-FW-01"` | PASS |
| Body cites DETECT-FW-02 | `git log -1 --format=%B \| grep -q "DETECT-FW-02"` | PASS |
| Body embeds 3-row delta table | `git log -1 --format=%B \| grep -c "^\| uno\| uno328pb\| leonardo"` | 3 (PASS) |
| `git status --porcelain firestarter` clean | (same) | empty (PASS) |
| Pinned firestarter SHA matches sub-repo HEAD | `git ls-tree HEAD firestarter \| awk '{print $3}'` vs `cd firestarter && git rev-parse HEAD` | both `032a2e2b93238856a70b1d0b87c6c332d6d6cf02` (PASS) |
| Commit touches only the submodule pointer | `git show --stat HEAD` | 1 file changed, 1 insertion(+), 1 deletion(-) — only `firestarter` gitlink (PASS) |

## Verification

### Plan-level success criteria — all PASS

| Criterion | Evidence |
|-----------|----------|
| `verify-detect-34.sh` widened-band documented inline | Multi-line comment block citing original [+20, +300] B + empirical Plan 03 numbers + Option B rationale + new `abs(Δ) <= 600 B` bound; cross-references 34-03-SUMMARY.md |
| Per-env .hex byte counts + deltas recorded | Table in this SUMMARY + commit body of `a8805b0` (uno −299 / uno328pb −454 / leonardo −491; all within `abs(Δ) <= 600`) |
| `verify-detect-34.sh` exits 0 | Verbatim output captured above; EXIT=0; all 3 assertions PASS |
| `pio test -e native -f "*test_dispatch*"` 15/15 | Defensive duplicate of Assertion 2 confirms dispatch chain unperturbed |
| Meta-repo submodule pointer bumped to Plan-03 HEAD | `git ls-tree HEAD firestarter` returns `032a2e2b93238856a70b1d0b87c6c332d6d6cf02` |
| `git -C /workspaces ls-tree HEAD firestarter` shows new SHA | (same — confirmed `160000 commit 032a2e2b93238856a70b1d0b87c6c332d6d6cf02 firestarter`) |
| Submodule-pointer-bump commit on `v1.7-shield-investigation` branch | `a8805b0 feat(34-04): bump firestarter to 032a2e2 — analog ADC band-lookup detect-rev rework (DETECT-FW-01 + DETECT-FW-02)` |
| SUMMARY.md created + committed in meta-repo plan directory | this file (next commit) |
| STATE.md updated | next state-update step |
| ROADMAP.md updated | next state-update step |

### Threat model — T-34-04 mitigation verified

| Threat | Mitigation | Status |
|--------|------------|--------|
| T-34-04 (Tampering): Submodule pointer bumped to wrong SHA | Task 2 step 3 verified `git status --short firestarter` showed ` M firestarter` pre-stage; step 6 confirmed `git ls-tree HEAD firestarter` matches `firestarter && git rev-parse HEAD` post-bump (both `032a2e2b93238856a70b1d0b87c6c332d6d6cf02`). Task 1 PASS gated Task 2 — bump only happened after the 3-assertion gate exited 0. | MITIGATED |

## Deviations from Plan

**None — plan executed exactly as written under the explicit `<sequential_execution>` reconciliation guidance.** No Rule 1-4 triggers. No auth gates. No checkpoints.

The orchestrator's prompt explicitly directed the executor to widen the `verify-detect-34.sh` delta-band per the Plan 03 Hand-off (Option B `abs(Δ) <= 600 B`). The widening is recorded as a plan-internal substrate amendment (the script is gitignored and Plan-00-owned), NOT as a deviation. The empirical negative deltas were known and documented at the close of Plan 03 (see 34-03-SUMMARY.md "Hand-off to Plan 04"); Plan 04 inherited the reconciliation problem and Option B was selected from the three options the Plan 03 SUMMARY laid out.

**Total deviations:** 0
**Impact on plan:** None. Plan ran straight through — band widened, gate exited 0, submodule pointer bumped cleanly.

## Cross-cutting context preserved

- **Branch model invariant:** firestarter sub-repo + meta-repo both on `v1.7-shield-investigation` per `feedback_branching` memory. Sub-repo HEAD unchanged by this plan (Plan 03's `032a2e2` is the pinned SHA). Meta-repo gained one new commit (`a8805b0`). firestarter_app submodule NOT touched.
- **Operator WIP preserved untouched:** `firestarter_app/firestarter/config.py` + `firestarter_app/.planning/STATE.md` inside the firestarter_app submodule (` m firestarter_app` marker) and the untracked `.planning/phases/33-silkscreen-label-code-alias-migration/33-VERIFICATION.md` in the meta-repo — both unchanged from pre-plan state. Verified via `git status --short` at plan-end: `m firestarter_app` and `?? .planning/phases/33-silkscreen-label-code-alias-migration/33-VERIFICATION.md` still present.
- **Native env exclusion:** the reworked detect-rev body sits inside `#ifdef HARDWARE_REVISION`; `[env:native]` `build_src_filter = +<proms/>` continues to exclude `rurp_hw_rev_utils.h` from native compilation. Defensive `pio test -e native -f "*test_dispatch*"` confirms 15/15 PASS — load-bearing GATE-1.7 dispatch-unaffected evidence per VALIDATION Dim 1 / DETECT-FW-02.
- **MSG_OK_REV wire shape unchanged per D-09:** no codegen pass on `tools/catalog/messages.toml`; the new REVISION_UNKNOWN (= 0xFE) and REVISION_2_3 (= 5) enum bytes flow through the existing (physical_u8, effective_u8) payload positions of MSG_OK_REV. Plan 06 will land the host-side u8 → silkscreen-string mapping per D-05 Path A; this plan does not touch the wire path.
- **Verify-harness ownership:** Plan 00 owns `verify-detect-34.sh`. Plan 04 amended it in-place (band widening). The script remains gitignored under `.planning/v1.7/baseline-34/`. Future Phase 35 milestone-close paperwork cites the post-Plan-04 widening + cites this plan's PASS run as the canonical DETECT-FW-02 sign-off evidence.

## Hand-off to Plan 05 (Wave 3 — firestarter_app Python parity per D-08)

Plan 05 will:

1. Add `# RURP Hardware Revisions` block to `firestarter_app/firestarter/constants.py` mirroring the firmware `REVISION_*` enum (7 constants: REVISION_0, REVISION_1, REVISION_2_0, REVISION_2_1, REVISION_2_2, REVISION_2_3, REVISION_UNKNOWN).
2. Extend `firestarter_app/CLAUDE.md` sync rule to cover the new block.
3. Land a hard pytest gate: `firestarter_app/tests/test_revision_constants_parity.py` that asserts every Python REVISION_* constant matches the firmware enum value declared in `firestarter/include/rurp_shield.h` (which the meta-repo now pins via this plan's `a8805b0` commit at sub-repo SHA `032a2e2`).

Substrate ready:

- **Pinned firestarter SHA:** `032a2e2` contains `REVISION_2_3 = 5` + `REVISION_UNKNOWN = 0xFE` (Plan 02 substrate, now anchored in meta-repo via `a8805b0`).
- **pytest baseline:** 82/82 PASS as of plan-close; any Plan 05 delta is measured against this anchor.
- **firestarter_app submodule:** still on `v1.7-shield-investigation` branch; pre-existing operator WIP in `firestarter/config.py` carries forward untouched (documented in 34-03-SUMMARY.md cross-cutting context).

## Hand-off to Plan 06 (Wave 3 — firestarter_app serial_comm.py silkscreen mapping per D-05 Path A)

Plan 06 follows Plan 05. Consumes Plan 05's REVISION_* Python constants + extends `_format_message` MSG_OK_REV branch with defensive `.get()` rendering for u8 → silkscreen-string lookup. D-09 wire shape unchanged. Final meta-repo sub-repo-pointer bump for firestarter_app at Plan 06 close (mirrors this plan's `a8805b0` shape).

## Self-Check: PASSED

- [x] `.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-04-SUMMARY.md` exists (this file)
- [x] Meta-repo commit `a8805b0` present on `v1.7-shield-investigation` branch (`git log --oneline | grep a8805b0` → FOUND)
- [x] Pinned firestarter SHA = `032a2e2b93238856a70b1d0b87c6c332d6d6cf02` (`git ls-tree HEAD firestarter | awk '{print $3}'` → matches)
- [x] firestarter sub-repo HEAD = `032a2e2` (`cd /workspaces/firestarter && git rev-parse HEAD` → matches)
- [x] firestarter sub-repo HEAD subject = Plan 03 Task 3 commit (`feat(34-03): rework rurp_detect_hardware_revision() ...`)
- [x] `verify-detect-34.sh` exits 0 with `PASS: Phase 34 detect-rev rework verified — delta within band, native tests green, enums present.` (verbatim output captured above)
- [x] Per-env .hex deltas all within `abs(Δ) <= 600 B` (uno 299 / uno328pb 454 / leonardo 491 — all PASS)
- [x] Native dispatch 15/15 PASS (defensive)
- [x] firestarter_app pytest 82/82 PASS (Plan 05 baseline)
- [x] `verify-detect-34.sh` widened-band rationale documented inline with cross-reference to 34-03-SUMMARY.md
- [x] No `34-04-INVESTIGATION.md` created (would indicate a FAIL escalation)
- [x] Meta-repo `git status` clean for `firestarter` submodule post-bump (`git status --porcelain firestarter` → empty)
- [x] Operator WIP preserved untouched (config.py inside firestarter_app + untracked 33-VERIFICATION.md in meta-repo)
- [x] Branch invariant honored (both repos on `v1.7-shield-investigation`)

---

*Phase: 34-shield-version-detect-design-firmware-plumbing*
*Completed: 2026-05-25*

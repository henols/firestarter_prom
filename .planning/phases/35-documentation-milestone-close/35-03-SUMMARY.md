---
phase: 35-documentation-milestone-close
plan: 03
subsystem: meta-repo
tags: [v1.7, shield-investigation, submodule-bump, re-baseline, wave-1-close, milestones-feed]

# Dependency graph
requires:
  - phase: 35-01
    provides: "firestarter @ 7b7748b — CR-01 INPUT high-Z + CR-02 hard-fail-loud REVISION_UNKNOWN warn emit (D-01 + D-02)"
  - phase: 35-02
    provides: "firestarter_app @ 07d8daa — MSG_INFO_HW/PHYSICAL_HW + MSG_OK_CFG Override silkscreen rendering (D-03 + D-04 / WR-01 + WR-02)"
provides:
  - "Meta-repo submodule pointers pinned to Wave 1 sub-repo HEADs (one cohesive Wave 1 jump per D-08)"
  - ".planning/v1.7/baseline-35/{uno,uno328pb,leonardo}.hex — post-Wave-1 .hex artifacts (gitignored under .planning/v1.7/**)"
  - ".planning/v1.7/baseline-35/BASELINE_COMMIT.txt — firestarter HEAD SHA the baseline was captured against (7b7748b)"
  - "Per-env Δ B table vs Phase 34 baseline-34 for D-12 MILESTONES.md Key Accomplishments line"
affects:
  - "Wave 2 operator-on-bench: unblocked — sub-repo v1.7-shield-investigation → beta promotion + 3.0.0b5 cut + firestarter fw -i --pre --force install vehicle ready"
  - "Wave 3 §9 row updates: baseline-35 directory becomes the reference Wave 3 re-derives ADC band thresholds against (per the baseline-35 key_link in 35-03-PLAN.md frontmatter)"
  - "D-12 MILESTONES.md Phase 35 Key Accomplishments line: per-env Δ B feeds verbatim"
  - "v1.6 Phase 27 RCA re-open: meta-repo submodule pointer now references the labeled-schematic + per-rev capability table + post-fix detect-fw substrate"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Submodule-pointer-bump-as-single-commit pattern (mirror of Phase 34 commits a8805b0 + bef5bec); one meta-repo commit cites both sub-repo SHAs"
    - ".planning/v1.7/** gitignore covers baseline-35/ recursively — no .gitignore change needed"
    - "Baseline directory structure mirrors baseline-34: 3 .hex files + BASELINE_COMMIT.txt"

key-files:
  created:
    - ".planning/v1.7/baseline-35/uno.hex (62249 B; post-Wave-1 uno firmware)"
    - ".planning/v1.7/baseline-35/uno328pb.hex (62318 B; post-Wave-1 uno328pb firmware)"
    - ".planning/v1.7/baseline-35/leonardo.hex (68303 B; post-Wave-1 leonardo firmware)"
    - ".planning/v1.7/baseline-35/BASELINE_COMMIT.txt (single line: 7b7748b8016bf20b6a33296bac74429d5026d96c)"
  modified:
    - "firestarter (submodule pointer: 032a2e2 → 7b7748b)"
    - "firestarter_app (submodule pointer: b2183ed → 07d8daa)"

key-decisions:
  - "Submodule pointer bump landed as ONE atomic meta-repo commit (per D-08 cohesive Wave 1 jump) — both sub-repo SHAs cited in commit body; per-env Δ B table embedded; D-01..D-04 verbatim summary embedded"
  - "Baseline-35 .hex artifacts are NOT committed — covered by existing `.planning/v1.7/**` gitignore rule (same shape as baseline-34); BASELINE_COMMIT.txt is also gitignored but lives on disk as canonical record"
  - "Sub-repo v1.7-shield-investigation → beta promotion explicitly DEFERRED to Wave 2 (D-08) — not part of this plan; operator-authorization step"
  - "Meta-repo NOT pushed to main or any remote (operator-authorization step per Phase 35 D-09 + v1.7 branch model)"

requirements-completed: [DOC-01]

# Metrics
duration: ~10 min
completed: 2026-05-25
tasks_executed: 2
commits: 1
files_modified: 2 (submodule pointers)
files_created: 4 (baseline-35 directory contents; gitignored, not in git history)
---

# Phase 35 Plan 03: Wave 1 Re-Baseline + Meta-Repo Submodule Pointer Bump Summary

**Closed Wave 1 on the meta-repo side: captured the post-Plan-01-fix `.hex` baseline to `.planning/v1.7/baseline-35/` and bumped both sub-repo submodule pointers to their respective Wave 1 HEAD SHAs in a single cohesive commit on `v1.7-shield-investigation` per D-08.**

Wave 2 (operator-on-bench `beta` promotion + `3.0.0b5` cut + bench UAT sideload) is now unblocked. Wave 3 has the canonical baseline directory it will re-derive the §9 ADC band thresholds against from Wave 2 bench evidence.

## Performance

- **Duration:** ~10 min (compile + copy + table compute + 1 commit + summary)
- **Tasks:** 2 (Task 1 baseline capture; Task 2 meta-repo pointer bump)
- **Commits:** 1 (meta-repo `v1.7-shield-investigation`)
- **Files modified:** 2 (submodule pointers `firestarter` + `firestarter_app`)
- **Files created (gitignored):** 4 under `.planning/v1.7/baseline-35/`

## Accomplishments

### Task 1 — `.planning/v1.7/baseline-35/` captured (4 artifacts)

Re-ran `pio run` for all 3 AVR envs against `firestarter @ 7b7748b` (already on `v1.7-shield-investigation`); all three SUCCESS. Copied the post-Wave-1 `.hex` outputs into the new baseline directory:

| artifact | source | size |
| -------- | ------ | ---- |
| `uno.hex` | `firestarter/.pio/build/uno/firestarter_uno.hex` | 62 249 B |
| `uno328pb.hex` | `firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex` | 62 318 B |
| `leonardo.hex` | `firestarter/.pio/build/leonardo/firestarter_leonardo.hex` | 68 303 B |
| `BASELINE_COMMIT.txt` | `cd firestarter && git rev-parse HEAD` | 41 B (single line) |

`BASELINE_COMMIT.txt` content:

```
7b7748b8016bf20b6a33296bac74429d5026d96c
```

The PlatformIO artifact name is `firestarter_{board}.hex` (not the plan-text-stated `firmware.hex`); the actual filenames in `.pio/build/<env>/` are `firestarter_uno.hex`, `firestarter_uno328pb.hex`, `firestarter_leonardo.hex`. Per the plan's verify gate (`ls /workspaces/.planning/v1.7/baseline-35/`) and baseline-34 precedent, the baseline-directory filenames are the env-suffix-only canonical names (`uno.hex`, `uno328pb.hex`, `leonardo.hex`).

### Per-env Δ B vs Phase 34 baseline (for D-12 MILESTONES.md feed)

| env       | Phase 34 baseline-34 (B) | Wave 1 baseline-35 (B) | Δ B  |
| --------- | ------------------------ | ---------------------- | ---- |
| uno       | 62 617                   | 62 249                 | −368 |
| uno328pb  | 62 854                   | 62 318                 | −536 |
| leonardo  | 68 876                   | 68 303                 | −573 |

All three deltas match the 35-01-SUMMARY.md recorded values byte-identically (cross-check passed — the firestarter HEAD didn't drift between Plan 01 and Plan 03).

**Why all three deltas are negative (recap from 35-01-SUMMARY.md):**

1. Task 1 of Plan 35-01 removes one `pinMode` call (the trailing restore line);
2. `INPUT_PULLUP` codegen in the Arduino core inlines a longer pull-up enable sequence than `INPUT` (which collapses to a simpler DDR + PORT clear path);
3. LTO folding propagates the savings across the dispatcher chain — the `uno328pb` and `leonardo` envs both benefit more than `uno` because their FrameworkArduino objects re-emit pull-up sequences in multiple translation units;
4. Plan 35-01 Task 2's added `LOG_WARN_ID_U8(MSG_INFO_HW, REVISION_UNKNOWN)` conditional is flash-light (one CALL + a small predicate).

The Phase 34 verifier (`.planning/v1.7/baseline-34/verify-detect-34.sh`) is Phase-34-scoped (assertions sized for the Phase 34 hex band); the Δ B values fall outside its [−20, +100] B expected band and were never gated on per the plan's explicit "DO NOT gate on `verify-detect-34.sh` PASS" clause.

### Task 2 — Meta-repo submodule pointer bump (commit `1356928`)

Single meta-repo commit on `v1.7-shield-investigation` (`1356928`) atomically advances both submodule pointers:

| submodule       | from      | to        | sub-repo branch              |
| --------------- | --------- | --------- | ---------------------------- |
| `firestarter`   | `032a2e2` | `7b7748b` | `v1.7-shield-investigation`  |
| `firestarter_app` | `b2183ed` | `07d8daa` | `v1.7-shield-investigation`  |

`git ls-tree HEAD firestarter` returns `7b7748b8016bf20b6a33296bac74429d5026d96c` (matches `cd firestarter && git rev-parse HEAD` byte-identically). Same for `firestarter_app` (`07d8daa35ecbaf517a34ad653b0308aac983737d`).

The commit subject:

```
feat(35-03): bump submodules — firestarter @ 7b7748b + firestarter_app @ 07d8daa for Wave 1 CR/WR fixes (D-01 + D-02 + D-03 + D-04)
```

The commit body cites:

- Both sub-repo HEAD SHAs + per-sub-repo commit subjects (Plan 01: `0501c83`, `7b7748b`; Plan 02: `bd0b384`, `a8240bd`, `947f808`, `07d8daa`);
- The full per-env Δ B table (uno / uno328pb / leonardo);
- Phase 35 D-01..D-04 verbatim summary;
- Refs back to 35-01-SUMMARY.md, 35-02-SUMMARY.md, 35-03-PLAN.md, and 34-REVIEW.md.

No `--no-verify`, no skipped hooks; standard `git commit -m` with HEREDOC body for clean formatting.

## Verification

| Check                                                                                       | Result                            |
| ------------------------------------------------------------------------------------------- | --------------------------------- |
| `ls /workspaces/.planning/v1.7/baseline-35/` returns `BASELINE_COMMIT.txt leonardo.hex uno.hex uno328pb.hex` | PASS                              |
| `cat .planning/v1.7/baseline-35/BASELINE_COMMIT.txt` matches `cd firestarter && git rev-parse HEAD`         | PASS (`7b7748b8016bf20b6a33296bac74429d5026d96c`) |
| `git check-ignore -v .planning/v1.7/baseline-35/BASELINE_COMMIT.txt` resolves to `.gitignore:13:.planning/v1.7/**` | PASS (no .gitignore change needed) |
| `git log --oneline -1 -- firestarter firestarter_app \| grep -q '35-03'`                    | PASS                              |
| `git ls-tree HEAD firestarter` returns `7b7748b8016bf20b6a33296bac74429d5026d96c`           | PASS                              |
| `git ls-tree HEAD firestarter_app` returns `07d8daa35ecbaf517a34ad653b0308aac983737d`        | PASS                              |
| `cd firestarter && git branch --show-current` returns `v1.7-shield-investigation` (NOT `beta`) | PASS (Wave 2 owns the beta push) |
| `cd firestarter_app && git branch --show-current` returns `v1.7-shield-investigation` (NOT `beta`) | PASS (Wave 2 owns the beta push) |
| `pio run -e uno` / `-e uno328pb` / `-e leonardo`                                            | 3/3 SUCCESS                       |
| Pre-existing operator WIP `firestarter_app/firestarter/config.py` untouched                 | PASS (unstaged, working-tree-modified) |
| Pre-existing untracked `.planning/phases/33-silkscreen-label-code-alias-migration/33-VERIFICATION.md` untouched | PASS (still untracked) |
| `firestarter_app/.planning/STATE.md` operator scratch untouched                             | PASS                              |
| No `.planning/STATE.md` modification                                                        | PASS (orchestrator owns)          |
| No `.planning/ROADMAP.md` modification                                                      | PASS (orchestrator owns)          |

## Commits

| Hash      | Where                              | Subject                                                                                                                                        |
| --------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `1356928` | meta-repo `v1.7-shield-investigation` | `feat(35-03): bump submodules — firestarter @ 7b7748b + firestarter_app @ 07d8daa for Wave 1 CR/WR fixes (D-01 + D-02 + D-03 + D-04)`        |

This SUMMARY commit (to follow) lands as a separate `docs(35-03): ...` commit on the meta-repo with the SUMMARY.md file change only — captures the execution-results paperwork without intermingling with the sub-repo pointer bump.

## Deviations from Plan

### Auto-fixed Issues

None. The plan executed exactly as written — no Rule 1/2/3 deviations triggered.

### Minor process observations (not deviations)

**1. PlatformIO `.hex` artifact filename is `firestarter_{board}.hex`, not `firmware.hex`.**

- Plan text: `cp /workspaces/firestarter/.pio/build/uno/firmware.hex /workspaces/.planning/v1.7/baseline-35/uno.hex`
- Actual filename: `.pio/build/uno/firestarter_uno.hex` (set by the firestarter sub-repo's `name_firmware.py` PIO post-build hook — same pattern that produces the `firestarter_uno.hex` release artifact)
- Action taken: copied from the actual filenames; destination filenames in `baseline-35/` are the canonical short names (`uno.hex` / `uno328pb.hex` / `leonardo.hex`) matching the baseline-34 precedent
- Why this isn't a Rule 1/2/3 deviation: source-path detail; semantics + verification gate (`ls baseline-35/` content) unchanged

**2. `firestarter_app` submodule shows `-dirty` in unstaged `git diff` due to pre-existing operator WIP.**

- The unstaged `git diff` reports `+Subproject commit 07d8daa35ecbaf517a34ad653b0308aac983737d-dirty` because the sub-repo working tree has the operator's pre-existing `config.py` modification
- The staged diff (and the resulting commit) records the pointer as the bare SHA `07d8daa...` — the `-dirty` indicator is display-only and never enters git history
- Per prompt directive: operator WIP left untouched, never staged, never committed
- Verification: `git ls-tree HEAD firestarter_app` returns the bare SHA; no `-dirty` suffix in the recorded commit object

## Threat Surface Notes

Aligned with the plan's `<threat_model>`:

- **T-35-06 Tampering (submodule pointer drift)** — disposition: accept (per plan). Mitigation verified in Task 2 done criteria: `git ls-tree HEAD firestarter` matches `cd firestarter && git rev-parse HEAD` byte-identically; same for `firestarter_app`. No drift introduced; the content-addressed nature of submodule SHAs means any drift would be trivially visible.

No new threat surface — pure meta-repo bookkeeping + gitignored `.hex` artifact archival. No new threat flags.

## Known Stubs

None. All artifacts fully wired; baseline directory mirrors baseline-34 shape exactly.

## Deferred Issues

None within scope. Out-of-scope items (explicit per the plan):

- **Sub-repo `v1.7-shield-investigation` → `beta` promotion** — Wave 2 territory per D-08; explicit operator-authorization step. Not in Plan 35-03 scope.
- **`3.0.0b5` lockstep pre-release cut** — Wave 2 territory per D-08; uses v1.4 lockstep mechanism (manually-paired beta-branch push with explicit `BETA_VERSION=3.0.0b5` input).
- **Wave 3 §9 row updates from bench evidence** — Plan 35-05 (or follow-on Wave 3 plan) territory; consumes `.planning/v1.7/baseline-35/` as the reference baseline against which raw ADC values are derived.
- **Meta-repo `v1.7-shield-investigation` → `main` merge** — Wave 4 territory per D-09; gated on UAT-1/2/3 green.

## Files Modified

| File                            | Change                                                                  |
| ------------------------------- | ----------------------------------------------------------------------- |
| `firestarter` (submodule)       | Pointer: `032a2e2` → `7b7748b` (one cohesive Wave 1 jump per D-08)      |
| `firestarter_app` (submodule)   | Pointer: `b2183ed` → `07d8daa` (one cohesive Wave 1 jump per D-08)      |

## Files Created (gitignored)

| File                                              | Purpose                                                                  |
| ------------------------------------------------- | ------------------------------------------------------------------------ |
| `.planning/v1.7/baseline-35/uno.hex`              | post-Wave-1 uno firmware artifact (62 249 B)                             |
| `.planning/v1.7/baseline-35/uno328pb.hex`         | post-Wave-1 uno328pb firmware artifact (62 318 B)                        |
| `.planning/v1.7/baseline-35/leonardo.hex`         | post-Wave-1 leonardo firmware artifact (68 303 B)                        |
| `.planning/v1.7/baseline-35/BASELINE_COMMIT.txt`  | firestarter HEAD SHA the baseline was captured against (`7b7748b...`)    |

All four files covered by the existing `.planning/v1.7/**` rule in `/workspaces/.gitignore:13`. No `.gitignore` change needed.

## Self-Check: PASSED

- `.planning/v1.7/baseline-35/uno.hex` exists (62 249 B) — FOUND
- `.planning/v1.7/baseline-35/uno328pb.hex` exists (62 318 B) — FOUND
- `.planning/v1.7/baseline-35/leonardo.hex` exists (68 303 B) — FOUND
- `.planning/v1.7/baseline-35/BASELINE_COMMIT.txt` exists (contents = `7b7748b8016bf20b6a33296bac74429d5026d96c`) — FOUND
- `BASELINE_COMMIT.txt` matches `cd firestarter && git rev-parse HEAD` — VERIFIED
- Meta-repo commit `1356928` exists on `v1.7-shield-investigation` — FOUND (`git log --oneline -1 -- firestarter firestarter_app | grep '35-03'` → PASS)
- `git ls-tree HEAD firestarter` returns `7b7748b8016bf20b6a33296bac74429d5026d96c` — VERIFIED
- `git ls-tree HEAD firestarter_app` returns `07d8daa35ecbaf517a34ad653b0308aac983737d` — VERIFIED
- Sub-repos still on `v1.7-shield-investigation` (NOT yet on `beta`) — VERIFIED
- No `.planning/STATE.md` or `.planning/ROADMAP.md` modification (orchestrator owns those writes) — VERIFIED
- Pre-existing operator WIP `firestarter_app/firestarter/config.py` untouched — VERIFIED
- Pre-existing untracked `.planning/phases/33-silkscreen-label-code-alias-migration/33-VERIFICATION.md` untouched — VERIFIED

---

*Phase: 35-documentation-milestone-close*
*Completed: 2026-05-25*

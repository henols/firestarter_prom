# Phase 22: Release Pipeline Artifacts - Research

**Researched:** 2026-05-20
**Domain:** PlatformIO `default_envs` widening + GitHub Actions release-asset glob compatibility + GATE-01 byte-identity verification
**Confidence:** HIGH (all 11 CONTEXT decisions verified at code-read level on the v1.5-uno328pb branch; build artifacts already exist on disk; CI globs verified by live shell expansion)

## Summary

Phase 22 has the smallest implementation surface of any phase in v1.5: **two files, one substantive line of code, one prose realignment.** The 11 locked decisions in CONTEXT.md narrow the work to:

1. `firestarter/platformio.ini:16` — change `default_envs = uno, leonardo` to `default_envs = uno, uno328pb, leonardo` (sub-repo commit on `v1.5-uno328pb`).
2. `.planning/ROADMAP.md` line 58 — realign Phase 22 SC#1's literal from `uno, leonardo, uno328pb` to `uno, uno328pb, leonardo` to match Phase 21 D-08's `.ini` section order (meta-repo commit on `v1.5-uno328pb`).

The CI workflows already use the glob `files: .pio/build/**/firestarter_*.hex` at `build.yml:105` and `beta-build.yml:92` — verified by live shell expansion on the dev box, the glob picks up all three artifacts (`firestarter_uno.hex`, `firestarter_uno328pb.hex`, `firestarter_leonardo.hex`) with zero YAML changes required. The firmware artifacts already exist locally at `.pio/build/{uno,uno328pb,leonardo}/firestarter_*.hex` because Phase 21 Plan 21-02's verification gate left them in place. `pio run` (no `-e` flag — the form used by both workflows at `build.yml:100` and `beta-build.yml:77`) consumes `default_envs` directly, so the single-line edit is sufficient to extend the CI matrix from 2 → 3 envs.

The verification gate is identical in shape to Phase 21's: build clean, build all envs, `cmp -s` against the same Phase 21 baselines under `.planning/v1.5/baselines/`, plus a static glob-resolution check on both workflow files. No new mandatory CI checks are added (ROADMAP SC#5). The "first real release cut" verification path described in REL-01/REL-02 acceptance language is **deferred to Phase 24** (Bench Validation) — Phase 22 ships when the local dry-run is green, per CONTEXT D-08.

**Primary recommendation:** Honor CONTEXT D-01..D-11 verbatim with **zero deviations**. Single plan (not two) — the edit surface is small enough that a Wave 1 / Wave 2 split would add ceremony without benefit. Skip the optional symbol/size assertion (CONTEXT D-11 Claude's Discretion) — `cmp -s` against Phase 21 baselines already covers byte-identity at the strongest level possible.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**default_envs widening (the load-bearing edit)**

- **D-01:** `default_envs` literal = `uno, uno328pb, leonardo` (matching D-08 section order from Phase 21, NOT the ROADMAP SC#1 current literal). Single-line edit on `firestarter/platformio.ini:16`: `default_envs = uno, leonardo` → `default_envs = uno, uno328pb, leonardo`.
- **D-02:** ROADMAP Phase 22 SC#1 literal realignment — amend the literal in `.planning/ROADMAP.md` (Phase 22 SC#1) from `uno, leonardo, uno328pb` to `uno, uno328pb, leonardo` in the same change-set as D-01. Cite Phase 21 D-08 + D-12 in the commit message and in the ROADMAP edit's prose.

**CI workflow edit surface (none — already compatible)**

- **D-03:** No `.github/workflows/*.yml` edits required. Both `build.yml:105` and `beta-build.yml:92` already use the glob `files: .pio/build/**/firestarter_*.hex` (verified via grep on the v1.5-uno328pb branch tip). After `default_envs` widens, `pio run` produces all three `.hex` files at `.pio/build/{uno,uno328pb,leonardo}/firestarter_*.hex` and the glob captures all three. The `softprops/action-gh-release` glob is the single source of truth — no per-env enumeration needed.
- **D-04:** No new mandatory CI checks (ROADMAP SC#5). The existing catalog-validity + codegen-drift gate + native Unity (`pio test -e native`) + PIO build run unchanged. The `pio run` step is already env-agnostic — it picks up whatever `default_envs` lists.

**GATE-01 byte-identity verification strategy**

- **D-05:** Baseline reference = Phase 21's `.planning/v1.5/baselines/` (NOT a re-fetch from GitHub Releases for the v1.4 ship tag `3.0.0b3`). Same source SHA, same `version.h` content; using them avoids a network round-trip to GitHub Releases and keeps verification reproducible offline.
- **D-06:** GATE-01 verification command — `cmp -s firestarter/.pio/build/uno/firestarter_uno.hex .planning/v1.5/baselines/firestarter_uno.hex` AND the leonardo equivalent. Both MUST exit 0 (a) BEFORE the `default_envs` edit is committed (sanity), and (b) AFTER the edit (proves widening did NOT perturb the two existing envs' build output).
- **D-07:** Version-string drift handling — `update_version.py` is NOT invoked during Phase 22's local verification. `include/version.h` stays unmodified at `3.0.0b2`, so `cmp -s` is a CLEAN match (not a "modulo version-string drift" match). The CI workflows DO invoke `update_version.py` before `pio run`, so the actual release-artifact byte-identity check against v1.4's `3.0.0b3` is the "modulo drift" form — but that's Phase 24's concern, not Phase 22's.

**Phase 22 verification gate (what "shipping Phase 22" means)**

- **D-08:** Verification = local-matrix dry-run + glob simulation, NOT an actual GitHub Release cut. The verification step runs:
  1. `cd firestarter && pio run` (no `-e` flag — uses `default_envs`) — must exit 0 and produce all three `.hex` files
  2. `ls firestarter/.pio/build/**/firestarter_*.hex` — must list exactly three files
  3. `cmp -s` against baselines (D-06)
  4. Static-analysis sanity on `build.yml:105` + `beta-build.yml:92` glob — confirm grep `firestarter_*.hex` resolves to the three filenames
  5. `pio test -e native` stays green (regression guard; D-04 said no new gates but the existing one MUST still pass)
- **D-09:** Phase 22 does NOT push to remote. No `git push origin v1.5-uno328pb` for either sub-repo. Consistent with the existing project convention (v1.5-uno328pb is local-only per `feedback-branching-firestarter-milestones`).

**Edit surface summary**

- **D-10:** Phase 22 edits exactly 2 files:
  - `firestarter/platformio.ini` (line 16) — sub-repo commit on `v1.5-uno328pb`
  - `.planning/ROADMAP.md` (Phase 22 SC#1, line 58) — meta-repo commit on `v1.5-uno328pb`
- **D-11:** No edits to: any `.github/workflows/*.yml`, any `firestarter/src/` file, any `firestarter/scripts/` file, `name_firmware.py`, `firestarter_app/**`. If the planner produces a plan that touches any of these, that's a planning defect — flag and reject.

### Claude's Discretion

- Whether to split into one plan or two (single-edit surface argues one plan; the planner picks).
- Wording of the ROADMAP SC#1 amendment prose (cite Phase 21 D-08 + D-12, keep it terse).
- Whether to add a `firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex` size/symbol assertion alongside the cmp -s gates (defensive belt-and-braces; planner decides based on diff size).

### Deferred Ideas (OUT OF SCOPE)

- Stable release cut from `firestarter/main` — Phase 22 does not produce one. Deferred to a future milestone (post-v1.5 merge-up), or to manual operator action when v1.5 is promoted from `beta` to `main`.
- First real beta pre-release cut — Phase 24 (Bench Validation) triggers this by merging `v1.5-uno328pb` → `firestarter/beta`. Phase 22 ships when the dry-run is green.
- `workflow_dispatch` `beta_version` flag exercise for v1.5 — exists in `beta-build.yml` since v1.4 (PEP 440 input), but Phase 22 does not exercise it. Phase 24 may use it if auto-increment-from-tags resolves to the wrong base.
- A README update mentioning the third board's release artifacts — Phase 25 (Documentation + Milestone Close) owns DOC-01/DOC-02.
- Adding `uno328pb` to `firestarter_app`'s `_flash_with_avrdude` table — Phase 23 (Host CLI Installer Integration) owns INST-01.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-01 | Push to `firestarter/main` produces a GitHub Release (stable, `make_latest: true`) that carries `firestarter_uno328pb.hex` in addition to existing two artifacts. Existing two artifacts remain byte-identical per GATE-01. **Phase 22 substrate-only**: provides the platformio.ini widening so a future stable cut emits the third artifact. The "release's asset list shows three .hex files" acceptance language is verified at Phase 24+ time (no Phase 22 push to main planned). [VERIFIED: build.yml:105 glob expansion via live shell on dev box] |
| REL-02 | Push to `firestarter/beta` produces a GitHub Pre-release (`prerelease: true`, `make_latest: false`) carrying `firestarter_uno328pb.hex` in addition to existing two. Existing two byte-identical per GATE-01. **Phase 22 substrate-only**: same platformio.ini widening serves both workflows. The "pre-release asset list" acceptance is verified at Phase 24 (first real beta cut from merge to `firestarter/beta`). [VERIFIED: beta-build.yml:92 glob expansion via live shell on dev box] |
| GATE-01 | After v1.5 lands, stable + beta cuts produce `firestarter_uno.hex` + `firestarter_leonardo.hex` byte-identical to pre-v1.5 cuts (modulo `update_version.py` drift). Phase 22 verifies the "modulo drift" form using Phase 21's `5fd751e` version-unbumped baselines under `.planning/v1.5/baselines/`. [VERIFIED: Phase 21 Plan 21-02 left these baselines + cmp -s exit-0 reachable on current dev box; current artifact SHA-256s match baselines verbatim] |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| PlatformIO build-matrix breadth | Build system (`platformio.ini` `[platformio]` section) | — | Single `default_envs` line drives `pio run` env enumeration |
| CI release-asset attachment | GitHub Actions workflow (`softprops/action-gh-release@v2` `files:` glob) | — | Already env-agnostic (D-03); zero edits |
| GATE-01 byte-identity gate | Meta-repo baseline (`.planning/v1.5/baselines/`) + `cmp -s` invocation | Firmware build system | Phase 21 left baselines + gate intact; Phase 22 re-applies to prove non-regression after widening |
| Documentation literal alignment | Meta-repo planning artifact (`.planning/ROADMAP.md`) | — | One-line prose realignment; coupled with platformio.ini edit |
| Native test regression guard | Test harness (`pio test -e native`) | — | Existing gate from Phase 21; widening default_envs does not touch native env, so this must stay green by construction |

## Standard Stack

### Core

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| PlatformIO Core | 6.1.19 | Build orchestrator — consumes `default_envs` to enumerate per-env builds in `pio run` (no `-e` flag) | Already pinned by Phase 21 verification toolchain; no version change [VERIFIED: `pio --version` 2026-05-20] |
| `platformio/atmelavr` platform | 5.2.0 (published 2026-04-28) | Provides toolchain for all three AVR envs; supplies bundled `ATmega328PB` board file | Same platform `[env:uno]`/`[env:uno328pb]`/`[env:leonardo]` already use — Phase 21 verified [VERIFIED: `pio pkg show platformio/atmelavr` 2026-05-20] |
| `softprops/action-gh-release@v2` | (action version pinned in workflows) | Attaches release assets to GitHub Release via `files:` glob | Already used by both workflows in v1.4 [VERIFIED: build.yml:103, beta-build.yml:90 — both use `@v2`] |
| `cmp -s` (POSIX) | system | Byte-identity gate against Phase 21 baselines | Phase 21 precedent; no install |

### Supporting

| Component | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| Unity (via `[env:native]`) | already wired | `pio test -e native` regression guard (D-08 step 5) | After every change in Phase 22 — must stay green |
| `git -C firestarter` | system | Sub-repo commit operations | Phase 22 commits the platformio.ini edit on `v1.5-uno328pb` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `default_envs = uno, uno328pb, leonardo` (D-01) | Per-workflow explicit `pio run -e uno -e uno328pb -e leonardo` invocation in `build.yml` + `beta-build.yml` | Would require YAML edits to both workflow files (D-03 violation). The `default_envs` approach is one-line + zero CI surface. CONTEXT chose D-01 — research confirms it's the smaller diff. |
| `default_envs = uno, leonardo, uno328pb` (ROADMAP SC#1 current literal) | `default_envs = uno, uno328pb, leonardo` (Phase 21 D-08 section order) | Section order in platformio.ini is `[env:uno] → [env:uno328pb] → [env:leonardo] → [env:native]` per Phase 21 commit `ab7c2a9` (verified by `awk '/^\[env:/' platformio.ini`). Matching that order in `default_envs` is the natural consistency choice — CONTEXT D-01 + D-08 lock this. |
| Re-fetch v1.4 ship-tag (`3.0.0b3`) artifacts from GitHub Releases for GATE-01 | Use Phase 21 baselines at `.planning/v1.5/baselines/` (D-05) | Re-fetch adds network dependency + introduces "modulo version-string drift" handling (3.0.0b2 vs 3.0.0b3 region differs). Phase 21 baselines were captured at `5fd751e` (= v1.4 ship state per STATE.md line 38) with `version.h` unmodified, enabling a clean `cmp -s` match. CONTEXT D-05 + D-07 locked this. |
| `cmp -s` byte-identity (D-06) | `sha256sum -c` against Phase 21's recorded hashes in `CAPTURE-PROCEDURE.md` | Equivalent strength; `cmp -s` matches the Phase 21 verification verbatim and is the documented pattern. SHA-256 is a fine belt-and-braces add-on but not load-bearing. |

**Version verification (2026-05-20):**

```bash
$ pio --version
PlatformIO Core, version 6.1.19
$ pio pkg show platformio/atmelavr | head -2
platformio/atmelavr
Platform • 5.2.0 • Public • Published on Tue Apr 28 13:35:37 2026
```

[VERIFIED: command outputs 2026-05-20 on /workspaces/firestarter]

## Architecture Patterns

### System Architecture Diagram

```
                  ┌──────────────────────────────────────────────┐
                  │ firestarter/platformio.ini                   │
                  │   [platformio] default_envs = uno,           │
                  │                              uno328pb,       │  ← Phase 22 edit
                  │                              leonardo        │
                  └────────────────────┬─────────────────────────┘
                                       │ (consumed by pio run, no -e)
                                       ▼
                  ┌──────────────────────────────────────────────┐
                  │ pio run  (CI step "Build PlatformIO Project")│
                  │   build.yml:100 and beta-build.yml:77        │
                  │   enumerates default_envs → builds 3 targets │
                  └────────────────────┬─────────────────────────┘
                                       │
                                       ▼
              ┌────────────────────────────────────────────────────────┐
              │ Local filesystem (CI runner workspace)                 │
              │   .pio/build/uno/firestarter_uno.hex                   │  ← byte-identical
              │   .pio/build/uno328pb/firestarter_uno328pb.hex         │  ← NEW
              │   .pio/build/leonardo/firestarter_leonardo.hex         │  ← byte-identical
              └────────────────────┬───────────────────────────────────┘
                                   │ (consumed by softprops glob)
                                   ▼
              ┌────────────────────────────────────────────────────────┐
              │ Release step  (softprops/action-gh-release@v2)         │
              │   build.yml:102-107          beta-build.yml:89-103     │
              │   files: .pio/build/**/firestarter_*.hex               │  ← UNCHANGED
              │   make_latest: true          prerelease: true          │
              │                              make_latest: false        │
              └────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
              ┌────────────────────────────────────────────────────────┐
              │ GitHub Release / Pre-release asset list (3 .hex files) │
              │   firestarter_uno.hex                                  │
              │   firestarter_uno328pb.hex                             │  ← NEW asset
              │   firestarter_leonardo.hex                             │
              └────────────────────────────────────────────────────────┘
                                   ▲
                                   │ "real cut" verification deferred to Phase 24
                                   │ (first push to firestarter/beta after v1.5 merge)

──── Local Phase 22 verification surface (D-08) ────────────────────────
              ┌────────────────────────────────────────────────────────┐
              │ Local dry-run on /workspaces/firestarter               │
              │ Step 1: pio run -t clean                               │
              │ Step 2: pio run        (no -e — uses default_envs)     │
              │ Step 3: ls .pio/build/**/firestarter_*.hex (3 files)   │
              │ Step 4: cmp -s vs .planning/v1.5/baselines/{uno,leo}.hex
              │ Step 5: pio test -e native (20/20 cases PASS)          │
              │ Step 6: grep glob in build.yml:105 + beta-build.yml:92 │
              └────────────────────────────────────────────────────────┘
```

### Recommended Project Structure

```
firestarter/                       (sub-repo, on branch v1.5-uno328pb @ ab7c2a9)
├── platformio.ini                 # EDIT line 16: default_envs = uno, uno328pb, leonardo
├── name_firmware.py               # UNCHANGED (Phase 21 da607d4 — produces firestarter_<RURP_BOARD_NAME>.hex)
├── .github/
│   └── workflows/
│       ├── build.yml              # UNCHANGED (line 105 glob already catches 3rd artifact)
│       └── beta-build.yml         # UNCHANGED (line 92 glob already catches 3rd artifact)
├── include/
│   └── version.h                  # UNCHANGED — must stay at "3.0.0b2" for GATE-01 cmp -s to pass
└── src/                           # UNCHANGED (Phase 21 ab7c2a9 widened 4 macro guards)

.planning/                         (meta-repo, on branch v1.5-uno328pb)
├── ROADMAP.md                     # EDIT line 58: realign default_envs literal per D-02 + Phase 21 D-12
├── v1.5/baselines/                # UNCHANGED (consumed by GATE-01 cmp -s; Phase 21 captured them)
│   ├── CAPTURE-PROCEDURE.md       # UNCHANGED (operator reference; do NOT recapture)
│   ├── firestarter_uno.hex        # UNCHANGED (SHA-256 0dd5c01a… — anchor)
│   └── firestarter_leonardo.hex   # UNCHANGED (SHA-256 f49e2a57… — anchor)
└── phases/22-release-pipeline-artifacts/
    ├── 22-CONTEXT.md              # input (locked decisions)
    ├── 22-DISCUSSION-LOG.md       # input (auto-resolved gray areas)
    ├── 22-RESEARCH.md             # this file
    └── 22-XX-PLAN.md              # NEW (planner-owned)
```

### Pattern 1: `default_envs` widening (single-line `[platformio]` edit)

**What:** Add a new env name to the comma-separated list at `firestarter/platformio.ini:16` so `pio run` (no `-e` flag) builds the new env alongside the existing ones.

**When to use:** Extending CI's build matrix to cover a new env that has been verified buildable on its own (Phase 21 verified `pio run -e uno328pb` SUCCESS at commit `ab7c2a9`).

**Example:**

```ini
# Source: /workspaces/firestarter/platformio.ini:11-16 (verified read 2026-05-20)
# BEFORE (current state on v1.5-uno328pb @ ab7c2a9):
[platformio]
; Phase 20 E2E-04: `pio run` (the firmware build) MUST NOT attempt to link the
; [env:native] target — it is a test-only environment with no main(), so
; linking fails with "undefined reference to main". Constrain default_envs
; to the AVR targets; `pio test -e native` still picks up native explicitly.
default_envs = uno, leonardo

# AFTER (Phase 22 edit per D-01):
[platformio]
; Phase 20 E2E-04: `pio run` (the firmware build) MUST NOT attempt to link the
; [env:native] target — it is a test-only environment with no main(), so
; linking fails with "undefined reference to main". Constrain default_envs
; to the AVR targets; `pio test -e native` still picks up native explicitly.
default_envs = uno, uno328pb, leonardo
```

Notes:
- Section order in the same file is `[env:uno]@31 → [env:uno328pb]@40 → [env:leonardo]@57 → [env:native]@67`. The `default_envs` order MUST match per CONTEXT D-01 + Phase 21 D-08.
- `[env:native]` deliberately stays OUT of `default_envs` (per the inline E2E-04 comment) — Phase 22 preserves that exclusion. Native is invoked separately via `pio test -e native`.
- The existing comment block above line 16 stays verbatim — it's E2E-04 substrate, not version-dependent.

### Pattern 2: GitHub Actions release-asset glob

**What:** `softprops/action-gh-release@v2`'s `files:` parameter accepts a glob pattern; the action expands it server-side at upload time. Path is relative to the workflow's working directory (the firmware sub-repo root in CI).

**When to use:** Attaching N per-env build outputs to a single Release without enumerating env names in the workflow YAML.

**Example:**

```yaml
# Source: /workspaces/firestarter/.github/workflows/build.yml:102-107 (verified 2026-05-20)
- name: Release
  uses: softprops/action-gh-release@v2
  with:
    files: .pio/build/**/firestarter_*.hex
    tag_name: ${{ steps.version.outputs.version }}
    make_latest: true
```

```yaml
# Source: /workspaces/firestarter/.github/workflows/beta-build.yml:89-103 (verified 2026-05-20)
- name: Release
  uses: softprops/action-gh-release@v2
  with:
    files: .pio/build/**/firestarter_*.hex
    tag_name: ${{ steps.version.outputs.version }}
    target_commitish: ${{ steps.release_target.outputs.sha }}
    prerelease: true
    make_latest: false
```

**Verification by live shell expansion (2026-05-20):**

```bash
$ cd /workspaces/firestarter && shopt -s globstar && ls .pio/build/**/firestarter_*.hex
.pio/build/leonardo/firestarter_leonardo.hex
.pio/build/uno/firestarter_uno.hex
.pio/build/uno328pb/firestarter_uno328pb.hex
```

[VERIFIED: live shell expansion on dev box 2026-05-20; three artifacts present from Phase 21 Plan 21-02 build]

**Note on glob semantics:** `softprops/action-gh-release@v2` uses the `@actions/glob` package internally, which honors POSIX-style `**` recursion. Behavior matches the bash `globstar` test above. The glob is NOT dependent on a specific runner OS — same result on `ubuntu-latest` (which is what both workflows use per `runs-on: ubuntu-latest` at build.yml:30 + beta-build.yml:24).

### Pattern 3: GATE-01 verification via Phase 21 baseline reuse

**What:** Run `cmp -s` against the version-unbumped baselines Phase 21 captured at `5fd751e` (= v1.4 ship state). The two existing envs' build output must be byte-identical before AND after the `default_envs` edit.

**When to use:** Any change that perturbs PlatformIO's env enumeration or build cache — to prove the change is purely additive and does not regress existing artifacts.

**Example:**

```bash
# Source: .planning/v1.5/baselines/CAPTURE-PROCEDURE.md "How to verify a fresh build matches"
# Pattern: capture baseline pre-bump, verify post-change without invoking update_version.py.

# Pre-edit sanity (proves working tree is GATE-1.5-clean before Phase 22 edits):
cd /workspaces/firestarter && pio run -e uno -e leonardo
cmp -s .pio/build/uno/firestarter_uno.hex            ../.planning/v1.5/baselines/firestarter_uno.hex      ; echo "uno exit=$?"
cmp -s .pio/build/leonardo/firestarter_leonardo.hex  ../.planning/v1.5/baselines/firestarter_leonardo.hex ; echo "leo exit=$?"
# Both must print exit=0.

# Apply edit (platformio.ini default_envs widening).

# Post-edit verification (proves widening did NOT perturb existing envs):
cd /workspaces/firestarter && pio run -t clean && pio run
cmp -s .pio/build/uno/firestarter_uno.hex            ../.planning/v1.5/baselines/firestarter_uno.hex      ; echo "uno exit=$?"
cmp -s .pio/build/leonardo/firestarter_leonardo.hex  ../.planning/v1.5/baselines/firestarter_leonardo.hex ; echo "leo exit=$?"
# Both must still print exit=0.
```

**Why `pio run -t clean` is in the post-edit step but not the pre-edit step:** PlatformIO caches incremental compilation per-env in `.pio/build/<env>/`. After the env enumeration changes (adding `uno328pb` to `default_envs`), `pio run` will trigger a build for `uno328pb` but may or may not recompile `uno` and `leonardo` depending on which other inputs changed. The `pio run -t clean` ensures a from-scratch build of all three envs, removing any ambiguity about whether the post-edit `uno`/`leonardo` artifacts were rebuilt or served from cache. This is the same pattern Phase 21 Plan 21-02 used (CONTEXT D-08-style "build clean, then build").

### Anti-Patterns to Avoid

- **Editing `.github/workflows/*.yml` to enumerate per-env hex files.** Violates D-03 + D-11. The glob already catches all three artifacts; adding `files: .pio/build/uno/firestarter_uno.hex` + per-env entries would add YAML cruft, violate "no new CI checks" (SC#5 / D-04), and create a drift surface for future env additions. Reject any plan that touches these files.

- **Invoking `update_version.py` during Phase 22 local verification.** Per CONTEXT D-07 + Phase 21 RESEARCH Pitfall 3 + CAPTURE-PROCEDURE.md "Why pre-bump". Bumping `version.h` rewrites `.data`-section bytes in the AVR ELF, drifting the version-string region of the `.hex` output. `cmp -s` against the unbumped baselines would tear at every drifted byte → false-positive GATE-01 failure. Plan and verify with `version.h` stuck at `3.0.0b2`. The CI workflow's call to `update_version.py` is a release-cut concern (Phase 24+), not a Phase 22 dry-run concern.

- **Re-capturing baselines from a fresh build to "make `cmp -s` pass".** Begs the question. The Phase 21 baselines were captured at `5fd751e` (= v1.4 ship state); they are the ground truth for the GATE-01 non-regression contract. If a Phase 22 edit causes `cmp -s` to fail, the edit is wrong, not the baseline. The recovery is to fix the edit, not to recapture.

- **Pushing `v1.5-uno328pb` to remote in either sub-repo or meta-repo.** Violates D-09. Operator-driven memory `feedback-branching-firestarter-milestones` keeps milestone work local until the milestone-close merge. Phase 24 (Bench Validation) is the phase that performs the first real beta cut by merging `v1.5-uno328pb` → `firestarter/beta`.

- **Splitting the platformio.ini edit and the ROADMAP edit into separate plans.** They are coupled per CONTEXT D-01 + D-02 — the platformio.ini literal MUST match the ROADMAP literal. A two-plan split would create a window where the two repos' commits disagree on the literal. Single plan, single change-set (one commit per repo on the matching branch).

- **Adding a new CI gate to validate the third artifact exists in the Release asset list.** Violates ROADMAP SC#5 + D-04. The existing glob + softprops behavior is sufficient; adding a post-release asset-list assertion would be net-new mandatory CI surface. If post-cut validation is needed, it's a Phase 24 manual operator step (inspect the GitHub Release UI after the first real beta cut).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Per-env release-asset enumeration in workflow YAML | Hand-author `files:` block listing each env's `.hex` path | Existing glob `files: .pio/build/**/firestarter_*.hex` (D-03) | Glob is env-agnostic; zero CI surface to maintain; auto-extends as future envs are added. |
| GATE-01 byte-identity diff with version-string normalization | Custom Intel-HEX-aware Python differ that skips checksum bytes in the version region | `cmp -s` against version-unbumped baselines (D-06) | Phase 21 already captured baselines at the unbumped state; cmp -s is the simplest faithful test. The "modulo version-string drift" form from REL-01/REL-02 acceptance is a Phase 24+ concern (real release cuts). |
| Baseline source of truth | Re-fetch v1.4 ship-tag (`3.0.0b3`) artifacts from GitHub Releases via `gh release download v3.0.0b3` | `.planning/v1.5/baselines/firestarter_*.hex` from Phase 21 Plan 21-01 (D-05) | Same source SHA (`5fd751e` = v1.4 ship state per STATE.md L38); avoids network dependency; matches the offline-reproducibility ethos of CAPTURE-PROCEDURE.md. |
| Phase 22 verification gate | Custom validation script that wraps build + cmp + glob check | Plain shell sequence: `pio run -t clean && pio run && cmp -s … && pio test -e native` (D-08) | Identical to Phase 21's verification gate shape; planner reuses Phase 21 Plan 21-02 verification scaffolding verbatim. |
| Glob semantics check | Custom Python script to expand `.pio/build/**/firestarter_*.hex` | `shopt -s globstar; ls .pio/build/**/firestarter_*.hex` in bash | Bash `globstar` semantics match `@actions/glob` (which `softprops/action-gh-release@v2` uses internally). One-liner. |

**Key insight:** The entire Phase 22 implementation surface is one substantive line of code in `platformio.ini` plus one literal realignment in ROADMAP.md. Anything beyond that — new verification scripts, new CI gates, baseline recapture, workflow YAML edits — is over-investing and violates one or more CONTEXT decisions.

## Runtime State Inventory

Phase 22 is a CI/build-configuration change. It does NOT touch persisted runtime state. Inventory below is for completeness per the rename/refactor-phase protocol.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None. No database, ChromaDB, Mem0, or persistent store references the string `uno328pb` for purposes other than the Phase 21 build artifacts. The chip_database.json in `firestarter_app` does not key on board names. | None — verified by `grep -rn "default_envs\|uno328pb" /workspaces/firestarter/include /workspaces/firestarter/src` returning zero substantive results. |
| Live service config | None. No GitHub Actions secrets need updating. Both workflows already use the glob; no per-env env-vars or secrets reference any board name. PERSONAL_ACCESS_TOKEN is unused on the firmware repo per beta-build.yml:98-103. | None — verified by reading both workflow YAMLs end-to-end. |
| OS-registered state | None. No systemd / launchd / pm2 / Task Scheduler registrations are involved. PlatformIO platform installs (`atmelavr@5.2.0`) and `framework-arduino-avr-minicore` live under `~/.platformio/packages/` and are auto-managed by PIO on env-build invocation. CI workflows install PlatformIO fresh on each run via `pip install --upgrade platformio` (build.yml:72, beta-build.yml:57). | None — CI is stateless; local dev box state is auto-managed. |
| Secrets/env vars | None. CONTEXT D-11 explicitly forbids touching `firestarter_app/**` (Phase 23's INST-01 owns the avrdude profile). `BETA_VERSION` workflow_dispatch input on beta-build.yml:17 is a Phase 24 concern. | None (Phase 22). |
| Build artifacts | `.pio/build/uno/`, `.pio/build/uno328pb/`, `.pio/build/leonardo/` already exist on dev box from Phase 21 Plan 21-02's verification (verified by `ls /workspaces/firestarter/.pio/build/`). The `default_envs` widening does NOT add new sources or change macro definitions, so existing per-env builds should remain byte-identical. | Phase 22 verification re-runs `pio run -t clean && pio run` to prove from-scratch builds still produce the three artifacts byte-identical to baselines. |

**Nothing found in category:** Phase 22 does not introduce any new stored data, live service config, OS state, secret/env var, or build-artifact dependency beyond what Phase 21 already established. The platformio.ini edit is a pure declarative change to PIO's env-enumeration list.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO Core | `pio run` (D-08 step 2), `pio test -e native` (D-08 step 5) | ✓ | 6.1.19 | — |
| `platformio/atmelavr` platform | All three envs (uno / uno328pb / leonardo) | ✓ | 5.2.0 | — |
| `framework-arduino-avr-minicore` | `[env:uno328pb]` board=ATmega328PB | ✓ | bundled via atmelavr@5.2.0 | — |
| ArduinoFake | `[env:native]` lib_deps | ✓ | 0.4.0 | — |
| `cmp` (POSIX) | GATE-01 verification (D-06) | ✓ | system | — |
| `git` (sub-repo + meta-repo) | Sub-repo commit + meta-repo commit on `v1.5-uno328pb` | ✓ | system | — |
| `bash` (globstar) | Glob simulation in verification (D-08 step 4) | ✓ | system | — |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** None.

The entire toolchain is the same one Phase 21 used at commit `ab7c2a9` (1 hour earlier per STATE.md L233-234). Zero environment delta.

## Common Pitfalls

### Pitfall 1: Editing `default_envs` order to match ROADMAP SC#1's current (stale) literal instead of CONTEXT D-01

**What goes wrong:** Operator/agent reads ROADMAP.md line 58 ("`default_envs = uno, leonardo, uno328pb`") and treats it as authoritative. Sets `default_envs` to that order in platformio.ini. The build still works (PIO doesn't care about order), but Phase 21 CONTEXT D-08 / D-12 explicitly hands off the realignment to Phase 22 — the section order in platformio.ini is `[env:uno] → [env:uno328pb] → [env:leonardo]` per Phase 21 commit `ab7c2a9`, and the `default_envs` literal must match that order for internal consistency.

**Why it happens:** ROADMAP.md is an older artifact; Phase 21 CONTEXT D-08 (locked 2026-05-20) supersedes the ROADMAP literal. Phase 21 D-12 was explicit about the hand-off: "planner for Phase 22 owns it OR plan-phase-21 amends ROADMAP inline" — Phase 21 deferred, so Phase 22 owns it.

**How to avoid:** Type `default_envs = uno, uno328pb, leonardo` exactly. AND realign ROADMAP line 58 in the same change-set per D-02. Verify by `awk '/^\[env:/' firestarter/platformio.ini | head -3` → must show `[env:uno] [env:uno328pb] [env:leonardo]` in that order; then check `default_envs` matches.

**Warning signs:** Post-edit ROADMAP.md and platformio.ini disagree on the literal. Future re-readers can't tell which is the authority.

### Pitfall 2: Invoking `update_version.py` during local verification

**What goes wrong:** Operator runs `firestarter/.github/scripts/update_version.py` between Phase 21 baseline capture and Phase 22 verification — perhaps because the script appears in both workflows (build.yml:91 + beta-build.yml:72) and the operator wants to "match CI exactly". The script rewrites `firestarter/include/version.h` (e.g., to `3.0.0b3` or auto-incremented), and the `VERSION` literal lands in `.data` via `FW_VERSION VERSION ":" RURP_BOARD_NAME` at firestarter.h:16. The `.hex` file's version-string region drifts, and `cmp -s` against Phase 21's `3.0.0b2` baselines fails → false-positive GATE-01 failure.

**Why it happens:** The CI workflows DO invoke `update_version.py` before `pio run` (verified at build.yml:89-91 and beta-build.yml:68-72). It's a natural mental model to "match CI" during local verification. But Phase 22's local-dry-run is intentionally version-unbumped per CONTEXT D-07 + CAPTURE-PROCEDURE.md.

**How to avoid:** Do NOT invoke `update_version.py` during Phase 22 verification. Verify `git -C firestarter diff --name-only include/version.h` returns empty before AND after the platformio.ini edit. Use `cat firestarter/include/version.h` to confirm `VERSION "3.0.0b2"` is unchanged.

**Warning signs:** `cmp -s` exit non-zero with a hex diff localized to a few bytes matching the ASCII pattern of a version string (e.g., `33 2e 30 2e 30 62 33` for "3.0.0b3"). If this appears, `git -C firestarter checkout 5fd751e -- include/version.h` to restore.

### Pitfall 3: PIO build cache serves stale artifacts after default_envs widening

**What goes wrong:** Operator edits `default_envs` from `uno, leonardo` to `uno, uno328pb, leonardo`, then runs `pio run` without `-t clean`. PIO reuses the cached `uno` and `leonardo` `.hex` outputs from Phase 21's build (the artifacts already exist on disk from Plan 21-02 verification — verified by `ls /workspaces/firestarter/.pio/build/` showing all three dirs). `cmp -s` passes because the cached artifacts are byte-identical to baselines — but this gives false confidence: the test didn't actually exercise the post-edit code path on a from-scratch build.

**Why it happens:** PIO's incremental build is aggressive about reuse; widening `default_envs` is a metadata change PIO may not treat as a cache-bust trigger for the existing envs.

**How to avoid:** Always invoke `pio run -t clean` before the post-edit verification build, per the Plan 21-02 verification pattern. The transcript should show "Removing /…/build/uno/", "Removing /…/build/uno328pb/", "Removing /…/build/leonardo/" before `pio run` starts the rebuild.

**Warning signs:** `pio run` post-edit completes suspiciously fast (< 0.5s per env vs the expected ~1.2s per env for a from-scratch build). If you see fast completion, force `pio run -t clean` and retry.

### Pitfall 4: Native test (`pio test -e native`) inadvertently regressed by env enumeration change

**What goes wrong:** Operator widens `default_envs` and assumes `pio test -e native` is unaffected because `native` is not in `default_envs`. But the test invocation is independent — `pio test -e native -f "*test_dispatch*" -f "*test_messages*"` runs the same suites Phase 21 verified at 20/20 PASS. If anything else in `platformio.ini` is accidentally edited (e.g., trailing whitespace stripped from a build_flag line, or section ordering reflowed), the native env may break or produce a different artifact path.

**Why it happens:** Phase 22's only substantive edit is line 16, but accidental whitespace changes elsewhere can perturb PIO's parser. PIO is whitespace-tolerant on `=`-separated values but strict on section headers and multi-line `\` continuations.

**How to avoid:** Use `git diff firestarter/platformio.ini` after the edit to confirm only line 16 changed (and only the substantive content, not whitespace). Run `pio test -e native -f "*test_dispatch*" -f "*test_messages*"` post-edit and verify 20/20 PASS as the regression guard per CONTEXT D-08 step 5.

**Warning signs:** `git diff` shows changes on lines other than 16; or `pio test -e native` reports < 20 PASSED.

### Pitfall 5: `softprops/action-gh-release@v2` glob does NOT expand `**` if the runner shell is non-bash

**What goes wrong:** Theoretical pitfall — the `softprops/action-gh-release@v2` action documentation states the glob is expanded by `@actions/glob` (a Node.js library), not by the runner shell. Bash globstar semantics are not load-bearing; the action handles `**` portably across Windows / macOS / Linux runners.

**Why it happens:** It does NOT happen in practice — both workflows use `runs-on: ubuntu-latest`, and `@actions/glob` honors `**` consistently. The bash globstar test on the dev box is a sanity check, not a contract.

**How to avoid:** Treat the bash `shopt -s globstar; ls .pio/build/**/firestarter_*.hex` test (D-08 step 4) as a sanity check that the file paths exist with the expected names, NOT as a contract that the action will see them. The action's actual contract is the YAML literal `files: .pio/build/**/firestarter_*.hex` — verifying the literal is present in the YAML and unchanged is the load-bearing check (D-08 step 4 alternative: `grep -F "files: .pio/build/\*\*/firestarter_\*.hex" firestarter/.github/workflows/*.yml` returns exactly 2 hits, one per workflow).

**Warning signs:** None expected on `ubuntu-latest`. If a future runner change (e.g., switching to a custom container) breaks this, it surfaces at first-cut time (Phase 24) — not during Phase 22's local dry-run.

### Pitfall 6: Catch-22 between Phase 22's "local dry-run only" and REL-01/REL-02's "verified by inspecting release's asset list"

**What goes wrong:** A strict reading of REL-01 / REL-02 acceptance language ("Verified end-to-end by inspecting the release's asset list after a stable/beta cut") implies Phase 22 cannot ship without an actual GitHub Release. But CONTEXT D-08 + D-09 explicitly say Phase 22 ships on local dry-run and does NOT push to remote.

**Why it happens:** REL-01 / REL-02 acceptance was written before the Phase 22 / Phase 24 split was finalized. The "release's asset list" inspection is the operator-on-bench validation that proves the CI pipeline emits the third artifact correctly — but the pipeline configuration (the platformio.ini edit) is the substrate Phase 22 ships, and the operator-on-bench validation IS Phase 24.

**How to avoid:** The plan must EXPLICITLY document that Phase 22 ships the SUBSTRATE for REL-01/REL-02 (locally verified by dry-run per D-08), and the actual "asset list inspection" portion of REL-01/REL-02 is verified at Phase 24 (first real beta cut from `firestarter/beta` after merge). This is the same pattern Phase 18 (Beta-Aware Firmware Downloader) used vs Phase 20 (E2E Smoke Test): Phase 18 shipped the consumer-side CLI substrate verified by unit tests; Phase 20 verified end-to-end against a real beta cut. Phase 22 is to Phase 24 what Phase 18 was to Phase 20.

**Warning signs:** Anyone reads the plan and asks "where's the actual cut?" — answer: "deferred to Phase 24 by design; this phase ships the platformio.ini widening that makes the cut work."

## Code Examples

Verified patterns from official sources and existing code:

### Existing `[platformio]` block (current state on v1.5-uno328pb @ ab7c2a9)

```ini
# Source: /workspaces/firestarter/platformio.ini:11-16 (verified read 2026-05-20)
[platformio]
; Phase 20 E2E-04: `pio run` (the firmware build) MUST NOT attempt to link the
; [env:native] target — it is a test-only environment with no main(), so
; linking fails with "undefined reference to main". Constrain default_envs
; to the AVR targets; `pio test -e native` still picks up native explicitly.
default_envs = uno, leonardo
```

### Existing CI release step — stable workflow (NO EDIT)

```yaml
# Source: /workspaces/firestarter/.github/workflows/build.yml:99-107 (verified 2026-05-20)
      - name: Build PlatformIO Project
        run: pio run

      - name: Release
        uses: softprops/action-gh-release@v2
        with:
          files: .pio/build/**/firestarter_*.hex
          tag_name: ${{ steps.version.outputs.version }}
          make_latest: true
```

### Existing CI release step — beta workflow (NO EDIT)

```yaml
# Source: /workspaces/firestarter/.github/workflows/beta-build.yml:76-103 (verified 2026-05-20)
      - name: Build PlatformIO Project
        run: pio run

      - name: Resolve release target SHA
        id: release_target
        run: |
          SHA=$(git rev-parse HEAD)
          echo "sha=$SHA" >> "$GITHUB_OUTPUT"
          echo "Release target SHA: $SHA"

      - name: Release
        uses: softprops/action-gh-release@v2
        with:
          files: .pio/build/**/firestarter_*.hex
          tag_name: ${{ steps.version.outputs.version }}
          target_commitish: ${{ steps.release_target.outputs.sha }}
          prerelease: true
          make_latest: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Local dry-run verification gate (D-08 — exact commands)

```bash
# Source: synthesis of CONTEXT D-06 + D-08 + Phase 21 Plan 21-02 verification transcript
# Pre-edit sanity (proves working tree is GATE-1.5-clean before any Phase 22 edit):
cd /workspaces/firestarter
pio run -t clean
pio run -e uno -e leonardo                           # build only the two non-changing envs first
cmp -s .pio/build/uno/firestarter_uno.hex            ../.planning/v1.5/baselines/firestarter_uno.hex      ; echo "pre-edit uno exit=$?"
cmp -s .pio/build/leonardo/firestarter_leonardo.hex  ../.planning/v1.5/baselines/firestarter_leonardo.hex ; echo "pre-edit leo exit=$?"
# Both must print exit=0 before applying the edit.

# Apply the edit (sed or Edit tool):
#   firestarter/platformio.ini line 16:
#     default_envs = uno, leonardo  →  default_envs = uno, uno328pb, leonardo
#   .planning/ROADMAP.md line 58:
#     "default_envs = uno, leonardo, uno328pb"  →  "default_envs = uno, uno328pb, leonardo"

# Post-edit verification (D-08 steps 1-5):
cd /workspaces/firestarter
pio run -t clean
pio run                                              # no -e flag — uses default_envs (now 3 envs)

# Step 2 verification: artifact presence
ls .pio/build/uno/firestarter_uno.hex
ls .pio/build/uno328pb/firestarter_uno328pb.hex
ls .pio/build/leonardo/firestarter_leonardo.hex

# Step 3 verification: GATE-01 byte-identity (D-06)
cmp -s .pio/build/uno/firestarter_uno.hex            ../.planning/v1.5/baselines/firestarter_uno.hex      ; echo "post-edit uno exit=$?"
cmp -s .pio/build/leonardo/firestarter_leonardo.hex  ../.planning/v1.5/baselines/firestarter_leonardo.hex ; echo "post-edit leo exit=$?"
# Both must print exit=0 (proves widening did not perturb existing envs).

# Step 4 verification: workflow glob simulation
shopt -s globstar
ls .pio/build/**/firestarter_*.hex                   # must list exactly 3 files
grep -Fn "files: .pio/build/**/firestarter_*.hex" .github/workflows/*.yml
# must show 2 hits: build.yml:105 and beta-build.yml:92 (literal text unchanged)

# Step 5 verification: native test regression guard
pio test -e native -f "*test_dispatch*" -f "*test_messages*"
# must print "20 test cases: 20 succeeded"

# Repo state check (D-09 — no remote push):
git -C /workspaces/firestarter status -s            # should show platformio.ini staged or committed only
git -C /workspaces        status -s                  # should show ROADMAP.md (and possibly firestarter submodule pointer) staged or committed only
git -C /workspaces/firestarter diff --name-only include/version.h   # must be empty
```

### ROADMAP.md SC#1 amendment (suggested wording per Claude's Discretion #2)

```markdown
# Before (ROADMAP.md line 58):
  1. `platformio.ini` `default_envs = uno, leonardo, uno328pb` so a CI-side `pio run` builds all three targets. (Or the workflow explicitly invokes each env — whichever pattern matches the existing CI shape with the smaller diff.)

# After (D-02 amendment):
  1. `platformio.ini` `default_envs = uno, uno328pb, leonardo` so a CI-side `pio run` builds all three targets. (Order matches the `[env:*]` section order in `platformio.ini` per Phase 21 D-08 + D-12 hand-off; the CONTEXT D-01 form supersedes the original SC#1 literal `uno, leonardo, uno328pb`.) The workflows' existing glob `files: .pio/build/**/firestarter_*.hex` captures all three artifacts — no workflow edits needed (CONTEXT D-03).
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hand-enumerate per-env `.hex` files in `files:` block | Glob `files: .pio/build/**/firestarter_*.hex` (one line, env-agnostic) | v1.4 Phase 17 (firmware beta release pipeline) — both workflows landed with the glob form | Phase 22 inherits this; zero CI edits needed to extend the matrix from 2 → 3 envs. |
| `default_envs = uno, leonardo` (2-env matrix) | `default_envs = uno, uno328pb, leonardo` (3-env matrix per D-01) | Phase 22 (this phase) | One-line widening; PIO `pio run` enumerates the new list automatically. |
| Custom `boards/uno328pb.json` (per original FW-02) | `board = ATmega328PB` + bundled atmelavr@5.2.0's `boards/ATmega328PB.json` + `-D RURP_BOARD_NAME=\"uno328pb\"` triple | Phase 21 D-05 / Plan 21-01 (REQUIREMENTS.md FW-02 amended) | The triple invariant (build_flag = filename = handshake string) ensures the CI glob picks up exactly `firestarter_uno328pb.hex` with no name-translation cruft. |

**Deprecated/outdated:**
- ROADMAP.md Phase 22 SC#1's literal `default_envs = uno, leonardo, uno328pb` — supersede via D-02 amendment in the same change-set as the platformio.ini edit. After Phase 22 ships, the platformio.ini and ROADMAP.md will agree on `uno, uno328pb, leonardo`.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | PIO Unity 1.0 (native env) + bash shell sequences (build + cmp + glob) |
| Config file | `firestarter/platformio.ini` `[env:native]` block (lines 67-102) |
| Quick run command | `cd firestarter && pio run -t clean && pio run && cmp -s .pio/build/uno/firestarter_uno.hex ../.planning/v1.5/baselines/firestarter_uno.hex && cmp -s .pio/build/leonardo/firestarter_leonardo.hex ../.planning/v1.5/baselines/firestarter_leonardo.hex && ls .pio/build/uno328pb/firestarter_uno328pb.hex` |
| Full suite command | Above + `pio test -e native -f "*test_dispatch*" -f "*test_messages*"` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REL-01 (substrate) | `pio run` produces `firestarter_uno328pb.hex` so a future stable cut from `firestarter/main` will attach it via the existing `files:` glob | smoke | `cd firestarter && pio run && ls .pio/build/uno328pb/firestarter_uno328pb.hex` | ✅ (the file already exists from Phase 21; Phase 22 verifies the env is enumerated by `pio run` without `-e`) |
| REL-01 (glob compat — stable) | `build.yml:105` glob still expands to include `firestarter_uno328pb.hex` after the widening | static | `grep -Fn "files: .pio/build/**/firestarter_*.hex" firestarter/.github/workflows/build.yml` and `shopt -s globstar && ls firestarter/.pio/build/**/firestarter_*.hex \| wc -l` (must = 3) | ✅ (verified live 2026-05-20) |
| REL-02 (substrate) | Same as REL-01 but for `firestarter/beta` → `beta-build.yml` pre-release path | smoke | Same `pio run` invocation; same artifact set | ✅ |
| REL-02 (glob compat — beta) | `beta-build.yml:92` glob behavior identical to stable | static | `grep -Fn "files: .pio/build/**/firestarter_*.hex" firestarter/.github/workflows/beta-build.yml` | ✅ (verified live 2026-05-20) |
| GATE-01 (uno non-regression) | `firestarter_uno.hex` byte-identical to Phase 21 baseline (= v1.4 ship state at `5fd751e`) after the `default_envs` widening | unit | `cmp -s firestarter/.pio/build/uno/firestarter_uno.hex .planning/v1.5/baselines/firestarter_uno.hex` — exit 0 | ✅ (current artifact SHA-256 0dd5c01a… matches baseline per Plan 21-02 transcript) |
| GATE-01 (leonardo non-regression) | `firestarter_leonardo.hex` byte-identical to Phase 21 baseline | unit | `cmp -s firestarter/.pio/build/leonardo/firestarter_leonardo.hex .planning/v1.5/baselines/firestarter_leonardo.hex` — exit 0 | ✅ (current artifact SHA-256 f49e2a57… matches baseline per Plan 21-02 transcript) |
| GATE-01 (native test regression guard — D-04) | `pio test -e native` stays green | unit | `cd firestarter && pio test -e native -f "*test_dispatch*" -f "*test_messages*"` — "20 test cases: 20 succeeded" | ✅ (Phase 21 baseline) |

### Sampling Rate

- **Per task commit:** Quick run command above (build + 3 cmp + 1 artifact-presence check) — completes in ~5s on the dev box per Phase 21 metrics.
- **Per wave merge:** Full suite command above (adds native test run) — completes in ~15s total.
- **Phase gate:** Full suite green + `git -C firestarter diff --name-only include/version.h` empty + `git -C firestarter status -s` shows only the `platformio.ini` change before `/gsd-verify-work`.

### Wave 0 Gaps

None — existing test infrastructure covers all phase requirements. Phase 21 left:

- Phase 21 baselines under `.planning/v1.5/baselines/` (consumed by GATE-01 cmp -s)
- `pio test -e native` filter scope already includes `test_dispatch` + `test_messages` (regression guard for D-04 / D-08 step 5)
- All three build artifacts already on disk from Plan 21-02 verification (Phase 22's first `pio run -t clean` will rebuild them from scratch)

No new test files, no new fixtures, no framework install needed. Phase 22 reuses Phase 21's verification scaffolding verbatim.

## Security Domain

Phase 22 is a build-configuration + documentation realignment change. No new user-facing surface, no new wire-protocol fields, no new auth/session/data-input handling. Security review surface is minimal.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | no | Phase 22 does not introduce new user inputs; the `default_envs` literal is a static config value typed by the developer. The Phase 21 `name_firmware.py` validation (`re.match(r"^[a-zA-Z0-9_-]+$", v)` at name_firmware.py:49) already gates the artifact-filename surface — Phase 22 does not modify that script. |
| V6 Cryptography | no | — (build-config change; no crypto surface touched) |
| V14 Configuration | yes | The `default_envs` literal is build configuration. Standard control: change is reviewed via git diff (single-line change) and verified by GATE-01 byte-identity (post-edit existing artifacts unchanged → no source-code drift). CI workflows already use signed tags (`tag_name: ${{ steps.version.outputs.version }}`) and GitHub-managed runners with pinned action versions (`actions/checkout@v4`, `actions/cache@v4`, `actions/setup-python@v5`, `softprops/action-gh-release@v2`). |

### Known Threat Patterns for {build-config / CI release pipeline}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Workflow YAML supply-chain injection | Tampering | Phase 22 does NOT edit any workflow YAML (D-03 / D-11). Existing pinned action versions (`@v2`, `@v4`, `@v5`) carry forward unchanged. |
| Asset-name collision in Release upload | Tampering | Three distinct PROGNAMEs from Phase 21's RURP_BOARD_NAME triple invariant: `firestarter_uno.hex`, `firestarter_uno328pb.hex`, `firestarter_leonardo.hex`. No collision possible — each env's PROGNAME is derived from its own per-env build flag. |
| Substrate-without-release-trigger (defense in depth) | Repudiation | Phase 22 ships the substrate; Phase 24 owns the first real trigger. Each phase carries its own audit trail in the meta-repo planning artifacts. |
| Stale baseline drift | Tampering | Phase 21 baselines under `.planning/v1.5/baselines/` are git-tracked plain blobs with documented SHA-256 anchors in CAPTURE-PROCEDURE.md. Phase 22 does NOT modify or recapture them — they remain the v1.4-ship-state ground truth for GATE-01. |
| Accidental cross-env source pollution via shared `${env.build_flags}` | Tampering | `${env.build_flags}` is read-only macro substitution; widening `default_envs` does not alter the shared block. Per-env build_flags overrides remain isolated. GATE-01 cmp -s is the load-bearing verifier that this does not regress in practice. |

## Project Constraints (from CLAUDE.md)

Extracted from `/workspaces/CLAUDE.md` (meta-repo) and `/workspaces/firestarter/CLAUDE.md` (firmware sub-repo):

| Constraint | Source | Phase 22 Compliance |
|------------|--------|---------------------|
| Meta-repo tracks only `.planning/` + `.claude/`; sub-repo `firestarter/` is separate | `/workspaces/CLAUDE.md` Repository Structure | ✓ Phase 22 commits exactly to those scopes: `firestarter/platformio.ini` lands in sub-repo on `v1.5-uno328pb`; `.planning/ROADMAP.md` lands in meta-repo on `v1.5-uno328pb`. |
| Protocol runs at 250000 baud; commands JSON; responses prefix-tagged | `/workspaces/CLAUDE.md` System Overview | ✓ Not touched — Phase 22 is build-config only. |
| Serial protocol changes must be kept in sync between `firestarter_app/.../serial_comm.py` and `firestarter/src/firestarter.cpp` | `/workspaces/CLAUDE.md` Key Architecture Points | ✓ N/A — no serial protocol changes in Phase 22. |
| Constants/flag bits duplicated between `firestarter_app/.../constants.py` and `firestarter/include/firestarter.h` — change both together | `/workspaces/CLAUDE.md` Key Architecture Points | ✓ N/A — no constants changed. |
| Board differences: Uno 512-byte buffer; Leonardo 1024-byte. Buffer size affects chunked transfer | `/workspaces/CLAUDE.md` Key Architecture Points | ✓ Not touched — Phase 22 does not change DATA_BUFFER_SIZE. (Phase 21 D-07 explicitly set uno328pb to inherit default 512.) |
| Hardware calibration (R1/R2, board revision) persisted in EEPROM via `rurp_configuration_t` | `/workspaces/CLAUDE.md` Key Architecture Points | ✓ N/A — no firmware source changes. |
| Native env layout: `[env:native]` in platformio.ini; test files under `test/native/avr/*` | `/workspaces/firestarter/CLAUDE.md` Native (Host) Test Environment | ✓ Phase 22 must NOT add `native` to `default_envs` per existing inline E2E-04 comment at platformio.ini:12-15. Verified preserved in the post-edit literal `uno, uno328pb, leonardo`. |
| Protocol dispatch via `handle->protocol` in `memory.cpp::configure_memory`; `mem_type` chain as fallback | `/workspaces/firestarter/CLAUDE.md` Architecture / Protocol Dispatch | ✓ N/A — no firmware source changes. |
| Build commands: `pio run -e uno`, `pio run -e leonardo`, `pio test`, `pio test -e native` | `/workspaces/firestarter/CLAUDE.md` Build Commands | ✓ Phase 22 extends the matrix to include `pio run -e uno328pb` (Phase 21 already validated this individual env builds). Existing commands continue to work. |

No directives from either CLAUDE.md are violated by the Phase 22 edit surface. The platformio.ini edit + ROADMAP edit + `cmp -s` verification + `pio test -e native` regression guard are all compatible with the constraints.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Bash globstar (`shopt -s globstar`) semantics match `@actions/glob` (used by `softprops/action-gh-release@v2`) for `.pio/build/**/firestarter_*.hex` | Architecture Patterns — Pattern 2 + Pitfall 5 | LOW — Both follow POSIX-style `**` recursion. Worst case: a runner-OS-specific glob difference manifests at first real beta cut (Phase 24), not Phase 22 dry-run. Mitigation: the live shell expansion on the dev box already confirms 3 files match; the YAML literal is unchanged, so the action receives the same input it has handled correctly in v1.4 (uno + leonardo) for 6 months. |

**If this table seems small:** It is. Phase 22 has 11 locked decisions from CONTEXT, all of which the research session verified at code-read or live-shell level. The single residual assumption (A1) is theoretical and well-mitigated.

## Open Questions

None — Phase 22's CONTEXT.md auto-resolved all 6 gray areas in the discussion log, and this research session verified the resulting decisions hold against the actual code on the v1.5-uno328pb branch tip (`ab7c2a9`). The planner can proceed to draft PLAN.md without operator escalation.

If the planner encounters any of the following during execution, escalate:
- `cmp -s` exits non-zero against either baseline AFTER the platformio.ini edit (means the widening perturbed an existing env — should not happen, but if it does, it's a phase-blocker).
- `pio run` (no `-e`) does NOT produce all three `.hex` files (means `default_envs` syntax is wrong — should not happen with the literal `uno, uno328pb, leonardo`).
- `pio test -e native` regresses to < 20 PASSED (means the platformio.ini edit accidentally touched the native env — should not happen with a line-16-only edit).

## Sources

### Primary (HIGH confidence)

- `/workspaces/firestarter/platformio.ini` (verified read 2026-05-20) — current `default_envs` literal at line 16; `[platformio]` section structure with E2E-04 inline comment
- `/workspaces/firestarter/.github/workflows/build.yml` (verified read 2026-05-20) — `files:` glob at line 105; `pio run` invocation at line 100; `update_version.py` invocation at line 91
- `/workspaces/firestarter/.github/workflows/beta-build.yml` (verified read 2026-05-20) — `files:` glob at line 92; `pio run` invocation at line 77; `update_version.py` invocation at line 72
- `/workspaces/firestarter/name_firmware.py` (verified read 2026-05-20) — Phase 21 reworked script; produces `firestarter_<RURP_BOARD_NAME>.hex`
- `/workspaces/firestarter/include/version.h` (verified read 2026-05-20) — `VERSION "3.0.0b2"` literal (unbumped — must stay this way for GATE-01)
- `.planning/v1.5/baselines/CAPTURE-PROCEDURE.md` (verified read 2026-05-20) — GATE-01 verification recipe; SHA-256 anchors; pre-bump invariant
- `.planning/phases/21-firmware-target-uno328pb/21-CONTEXT.md` (D-08, D-11, D-12) — Phase 21 hand-offs to Phase 22 (section order, default_envs widening, ROADMAP realignment)
- `.planning/phases/21-firmware-target-uno328pb/21-02-SUMMARY.md` (verified read 2026-05-20) — Phase 21 ship state; per-env build sizes; cmp -s green evidence
- `.planning/phases/22-release-pipeline-artifacts/22-CONTEXT.md` (D-01..D-11) — Phase 22 locked decisions
- `.planning/phases/22-release-pipeline-artifacts/22-DISCUSSION-LOG.md` — 6 auto-resolved gray areas with rationales
- `.planning/REQUIREMENTS.md` REL-01 + REL-02 + GATE-01 (lines 27-28, 42) — acceptance criteria
- `.planning/ROADMAP.md` Phase 22 SC#1..SC#5 (lines 57-62) — success criteria (SC#1 literal targeted by D-02)
- `.planning/STATE.md` (v1.5 Decisions, lines 141-153) — milestone-level invariants
- `.planning/PROJECT.md` — GATE-1.5 byte-identity contract
- `/workspaces/CLAUDE.md` — meta-repo layout
- `/workspaces/firestarter/CLAUDE.md` — firmware sub-repo build/test commands + native env layout

### Secondary (MEDIUM confidence)

- Live shell expansion `ls /workspaces/firestarter/.pio/build/**/firestarter_*.hex` (2026-05-20) — confirms three artifacts present and discoverable via globstar
- `pio --version` output 2026-05-20 — `PlatformIO Core, version 6.1.19`
- `pio pkg show platformio/atmelavr` output 2026-05-20 — `Platform • 5.2.0 • Public • Published on Tue Apr 28 13:35:37 2026`
- `git -C firestarter log --oneline -5` output 2026-05-20 — confirms `v1.5-uno328pb` branch tip at `ab7c2a9` with Phase 21 Plan 21-02 commits

### Tertiary (LOW confidence)

None — every claim in this research session was verified by direct file read or live shell command.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — PlatformIO 6.1.19 + atmelavr 5.2.0 + softprops/action-gh-release@v2 all verified live on the dev box (and Phase 21 used the same exact toolchain at the same exact commit).
- Architecture: HIGH — both CI workflow globs verified by direct file read AND by live shell expansion against the on-disk artifacts. `pio run` (no `-e`) consuming `default_envs` is documented PIO behavior and exercised in Phase 17's beta-build.yml landing.
- Pitfalls: HIGH — all 6 pitfalls are concrete, sourced from Phase 21 RESEARCH (Pitfall 3 inheritance), CAPTURE-PROCEDURE.md (version-h discipline), or direct file inspection (pitfall 1's ROADMAP-stale-literal discovery).
- Validation Architecture: HIGH — the entire test surface is reused verbatim from Phase 21 Plan 21-02 (cmp -s + pio test -e native + shell glob), all of which are documented in the Plan 21-02 transcript at SHA-256 anchors that match the current dev box state.
- Security: HIGH — Phase 22 is build-config + docs only; no surface for V2/V3/V4/V5/V6 ASVS. V14 (Configuration) compliance is structural (single-line edit, git-diff-reviewed).

**Research date:** 2026-05-20
**Valid until:** Phase 24 trigger (first real beta cut from `firestarter/beta`) — at which point the "modulo version-string drift" form of GATE-01 verification supersedes the Phase 22 dry-run form. If Phase 24 trigger has not occurred within 30 days, re-verify CI workflow YAML / `softprops/action-gh-release` version pin against any upstream changes.

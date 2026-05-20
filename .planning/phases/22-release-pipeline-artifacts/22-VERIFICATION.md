---
phase: 22-release-pipeline-artifacts
verified: 2026-05-20T00:00:00Z
status: passed
score: 7/7 must-haves verified
overrides_applied: 0
deferred:
  - truth: "REL-01: Stable release's asset list shows three .hex files after a stable cut from firestarter/main"
    addressed_in: "Phase 24 (Bench Validation) — first real cut deferred to milestone close; substrate-only for Phase 22 per CONTEXT D-08 + RESEARCH Pitfall 6"
    evidence: "Phase 22 CONTEXT D-08 + RESEARCH Pitfall 6 explicitly defer asset-list inspection to first real cut; Phase 24 Bench Validation triggers the first real beta cut from firestarter/beta"
  - truth: "REL-02: Beta pre-release's asset list shows three .hex files after a beta cut from firestarter/beta"
    addressed_in: "Phase 24 (Bench Validation)"
    evidence: "Phase 24 success criteria #2: 'Host installs the matching firestarter_uno328pb.hex from the pre-release asset' — first real beta cut from firestarter/beta after v1.5-uno328pb merge"
---

# Phase 22: Release Pipeline Artifacts Verification Report

**Phase Goal:** Both the stable workflow (`build.yml`) and the beta workflow (`beta-build.yml`) emit `firestarter_uno328pb.hex` as a third per-board release artifact alongside `firestarter_uno.hex` and `firestarter_leonardo.hex`, without altering the existing two artifacts' byte content (modulo version-string drift).

**Verified:** 2026-05-20
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth                                                                                                                                                                                                                                                | Status     | Evidence                                                                                                                                                                                                              |
| -- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1  | `firestarter/platformio.ini` line 16 contains the literal `default_envs = uno, uno328pb, leonardo` (D-08 section order; D-01 + D-02 widening)                                                                                                        | ✓ VERIFIED | `grep -n '^default_envs' firestarter/platformio.ini` → `16:default_envs = uno, uno328pb, leonardo`. Section order matches Phase 21 D-08 (`[env:uno]@31 → [env:uno328pb]@40 → [env:leonardo]@57`)                       |
| 2  | `.planning/ROADMAP.md` Phase 22 SC#1 literal reads `default_envs = uno, uno328pb, leonardo` (D-02 realignment supersedes the stale `uno, leonardo, uno328pb` form)                                                                                    | ✓ VERIFIED | `grep -n 'default_envs = uno, uno328pb, leonardo' .planning/ROADMAP.md` → line 58 hit; stale `uno, leonardo, uno328pb` grep returns exit=1 (no matches)                                                              |
| 3  | `cd firestarter && pio run` (no `-e` flag) from a clean tree produces all three `.hex` artifacts: `firestarter_uno.hex`, `firestarter_uno328pb.hex`, `firestarter_leonardo.hex` (D-08 step 1+2)                                                       | ✓ VERIFIED | `pio run -t clean` then `pio run` → `3 succeeded in 00:00:03.385` (uno 1.075s, uno328pb 1.102s, leonardo 1.209s); all three hex files present at expected paths                                                       |
| 4  | GATE-01 byte-identity holds POST-edit: `cmp -s firestarter/.pio/build/uno/firestarter_uno.hex .planning/v1.5/baselines/firestarter_uno.hex` AND the leonardo equivalent both exit 0 (D-06)                                                            | ✓ VERIFIED | `cmp -s` both exit 0; SHA-256 confirm verbatim match: uno `0dd5c01a87…d2`, leonardo `f49e2a57a2…90` against same-named baselines                                                                                       |
| 5  | Workflow glob is unchanged and compatible: `grep -F 'files: .pio/build/**/firestarter_*.hex' firestarter/.github/workflows/build.yml firestarter/.github/workflows/beta-build.yml` returns 2 hits (D-03 / D-04)                                       | ✓ VERIFIED | grep returns 2 hits at expected line numbers: `build.yml:105` + `beta-build.yml:92`. `git -C firestarter diff HEAD~1 HEAD --name-only | grep '^(\.github|src|scripts)/'` returns 0 — no forbidden-path edits         |
| 6  | Native suite regression-guard green: `pio test -e native -f "*test_dispatch*" -f "*test_messages*"` reports 20/20 PASSED (D-08 step 5)                                                                                                              | ✓ VERIFIED | `20 test cases: 20 succeeded in 00:00:03.998` (test_dispatch PASSED, test_messages PASSED). Phase 20 E2E-04 comment block above platformio.ini:16 preserved verbatim                                                  |
| 7  | `include/version.h` UNMODIFIED throughout: `git -C firestarter diff --name-only include/version.h` returns empty (Pitfall 3 / D-07)                                                                                                                  | ✓ VERIFIED | `git diff --name-only include/version.h` returns empty (exit 0); `grep -F 'VERSION "3.0.0b2"' firestarter/include/version.h` returns `#define VERSION "3.0.0b2"`. GATE-01 cmp -s is a CLEAN match (no version-string drift) |

**Score:** 7/7 truths verified

### Deferred Items

Items not yet met but explicitly addressed in later milestone phases.

| # | Item                                                                                                            | Addressed In | Evidence                                                                                                                                                                  |
| - | --------------------------------------------------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | REL-01: Stable release's asset list shows three `.hex` files after a stable cut from `firestarter/main`         | Phase 24     | CONTEXT D-08 + RESEARCH Pitfall 6 explicitly defer asset-list inspection to first real cut; substrate-only for Phase 22                                                  |
| 2 | REL-02: Beta pre-release's asset list shows three `.hex` files after a beta cut from `firestarter/beta`         | Phase 24     | Phase 24 SC#2 invokes `firestarter fw -i --pre` against the operator's plugged-in 328PB-Uno; first real beta cut from `firestarter/beta` is triggered by Phase 24's merge |

### Required Artifacts

| Artifact                                                              | Expected                                                                                       | Status     | Details                                                                                                                                                |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `firestarter/platformio.ini`                                          | `default_envs` widened from `uno, leonardo` to `uno, uno328pb, leonardo`                       | ✓ VERIFIED | Line 16 contains exact literal `default_envs = uno, uno328pb, leonardo`. Comment block above (Phase 20 E2E-04 rationale) preserved verbatim          |
| `.planning/ROADMAP.md`                                                | Phase 22 SC#1 literal realigned to match D-08 section order                                    | ✓ VERIFIED | Line 58 contains `default_envs = uno, uno328pb, leonardo`; stale `uno, leonardo, uno328pb` fully retired                                              |
| `firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex`            | Third-board CI build output that workflow glob attaches to GitHub Release; min 50k bytes      | ✓ VERIFIED | 62854 bytes (above 50000 B floor); SHA-256 `17439d0f75fbffb69f05ed8ff3cfc8fee496fb96860d113712dd272626507425`                                          |
| `.planning/phases/22-release-pipeline-artifacts/22-01-SUMMARY.md`     | Plan execution summary including verification gate transcript                                  | ✓ VERIFIED | File exists; contains REL-01 + REL-02 + GATE-01 citations; 7/7 must-haves verification table present                                                  |

### Key Link Verification

| From                                                                              | To                                                                            | Via                                                                                                       | Status   | Details                                                                                                                                       |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `firestarter/platformio.ini` line 16 (`default_envs`)                             | `pio run` (no `-e` flag) build matrix                                         | PlatformIO consumes `default_envs` as the env-enumeration list                                            | ✓ WIRED  | `pio run` (no -e) emits `3 succeeded` with uno + uno328pb + leonardo enumerated; clean-then-rebuild verifies env enumeration is live          |
| `pio run` build outputs at `.pio/build/{uno,uno328pb,leonardo}/firestarter_*.hex` | `softprops/action-gh-release@v2` Release asset list (stable + beta)            | `files: .pio/build/**/firestarter_*.hex` glob at build.yml:105 + beta-build.yml:92 (unchanged)            | ✓ WIRED  | Bash globstar simulation `ls .pio/build/**/firestarter_*.hex` returns 3 files matching the YAML glob literal verbatim                          |
| Post-edit `firestarter_{uno,leonardo}.hex` builds                                  | `.planning/v1.5/baselines/firestarter_{uno,leonardo}.hex` (Phase 21 captures) | `cmp -s` GATE-01 byte-identity gate, both must exit 0                                                     | ✓ WIRED  | Both `cmp -s` exit 0; SHA-256s match baselines exactly (uno `0dd5c01a…d2`, leonardo `f49e2a57…90`)                                            |

### Data-Flow Trace (Level 4)

Phase 22 is a build-config phase; the "data" flowing through the system is the build output (hex files). The flow is: `default_envs` → PlatformIO enumeration → 3 env builds → 3 `.hex` files → workflow glob captures all 3 → softprops attaches to Release. All flow points verified by command output above.

| Artifact                                          | Data Variable          | Source                                                | Produces Real Data | Status     |
| ------------------------------------------------- | ---------------------- | ----------------------------------------------------- | ------------------ | ---------- |
| `firestarter_uno.hex` (62617 bytes)               | hex output             | `pio run` for `[env:uno]` from real source build       | ✓ Yes              | ✓ FLOWING  |
| `firestarter_uno328pb.hex` (62854 bytes)          | hex output             | `pio run` for `[env:uno328pb]` from real source build  | ✓ Yes              | ✓ FLOWING  |
| `firestarter_leonardo.hex` (68876 bytes)          | hex output             | `pio run` for `[env:leonardo]` from real source build  | ✓ Yes              | ✓ FLOWING  |
| Workflow glob → Release assets (stable + beta)    | 3 hex paths             | YAML literal `files: .pio/build/**/firestarter_*.hex` | ✓ Yes (simulated)  | ✓ FLOWING (real cut deferred to Phase 24 per CONTEXT D-08) |

### Behavioral Spot-Checks

| Behavior                                                                                                      | Command                                                                                                                          | Result                                  | Status |
| ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | ------ |
| `pio run` (no `-e` flag) enumerates 3 envs and produces 3 hex files                                            | `cd firestarter && pio run -t clean && pio run`                                                                                  | `3 succeeded in 00:00:03.385`           | ✓ PASS |
| Workflow-glob simulation returns 3 hex paths                                                                   | `cd firestarter && shopt -s globstar && ls .pio/build/**/firestarter_*.hex \| wc -l`                                             | `3`                                     | ✓ PASS |
| GATE-01 cmp -s passes for uno baseline                                                                         | `cmp -s firestarter/.pio/build/uno/firestarter_uno.hex .planning/v1.5/baselines/firestarter_uno.hex`                            | exit 0                                  | ✓ PASS |
| GATE-01 cmp -s passes for leonardo baseline                                                                    | `cmp -s firestarter/.pio/build/leonardo/firestarter_leonardo.hex .planning/v1.5/baselines/firestarter_leonardo.hex`             | exit 0                                  | ✓ PASS |
| Workflow YAML literal grep returns 2 hits (build.yml:105 + beta-build.yml:92)                                  | `grep -n 'files: .pio/build/\*\*/firestarter_\*\.hex' firestarter/.github/workflows/build.yml firestarter/.github/workflows/beta-build.yml` | 2 hits at expected line numbers         | ✓ PASS |
| Native test regression guard passes 20/20                                                                      | `cd firestarter && pio test -e native -f "*test_dispatch*" -f "*test_messages*"`                                                 | `20 test cases: 20 succeeded`           | ✓ PASS |
| `version.h` is unmodified                                                                                      | `git -C firestarter diff --name-only include/version.h`                                                                          | empty                                   | ✓ PASS |
| `VERSION` literal pinned at `3.0.0b2`                                                                          | `grep -F 'VERSION "3.0.0b2"' firestarter/include/version.h`                                                                      | `#define VERSION "3.0.0b2"`             | ✓ PASS |
| Sub-repo HEAD is the Phase 22 commit `897067b`                                                                | `git -C firestarter rev-parse HEAD`                                                                                              | `897067b9edf0ca280fd8fb1a492aabf7cb3a69dd` | ✓ PASS |
| Phase 22 sub-repo diff vs Phase 21 is exactly `platformio.ini`                                                | `git -C firestarter diff ab7c2a9 897067b --name-only`                                                                           | `platformio.ini`                        | ✓ PASS |
| D-11 negative gate: 0 forbidden-path edits                                                                     | `git -C firestarter diff HEAD~1 HEAD --name-only \| grep -E '^(\.github\|src\|scripts)/' \| wc -l`                              | `0`                                     | ✓ PASS |
| Both repos on `v1.5-uno328pb` branch                                                                          | `git -C firestarter branch --show-current; git -C /workspaces branch --show-current`                                            | both `v1.5-uno328pb`                    | ✓ PASS |
| Both repos clean working tree (no uncommitted state, no push needed beyond what's already committed)          | `git -C firestarter status -s; git -C /workspaces status -s`                                                                    | both empty                              | ✓ PASS |

### Probe Execution

No probe scripts defined for Phase 22 (config-only / substrate phase). The behavioral spot-check table above IS the verification gate per CONTEXT D-08. Conventional probe discovery returns nothing applicable:

```bash
find /workspaces/firestarter/scripts -path '*/tests/probe-*.sh' -type f 2>/dev/null
# (no results — no probe scripts in this sub-repo)
```

**Status:** N/A (no probes defined; D-08 verification gate is the contract)

### Requirements Coverage

| Requirement | Source Plan          | Description                                                                                                                   | Status                | Evidence                                                                                                                                                                                                                                                                                                                              |
| ----------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| REL-01      | 22-01-PLAN.md        | Push to `firestarter/main` produces a stable GitHub Release carrying `firestarter_uno328pb.hex` + existing two byte-identical | ✓ SUBSTRATE SATISFIED | Substrate landed: `default_envs` widened → `pio run` (build.yml:100) builds 3 envs → glob at build.yml:105 (unchanged) catches all 3. Asset-list inspection deferred to Phase 24 per CONTEXT D-08 + RESEARCH Pitfall 6. GATE-01 byte-identity preserved on uno + leonardo via cmp -s exit 0.                                            |
| REL-02      | 22-01-PLAN.md        | Push to `firestarter/beta` produces a beta Pre-release carrying `firestarter_uno328pb.hex` + existing two byte-identical      | ✓ SUBSTRATE SATISFIED | Same widening drives beta-build.yml:77 `pio run`; glob at beta-build.yml:92 (unchanged) catches all 3. `prerelease: true` + `make_latest: false` lines untouched. Asset-list inspection deferred to Phase 24 (first real beta cut from merge to `firestarter/beta`). GATE-01 byte-identity preserved on uno + leonardo via cmp -s exit 0. |

REQUIREMENTS.md REL-01/REL-02 checkboxes remain unchecked in the source because the "end-to-end inspection" portion is by-design deferred to Phase 24 (the first real beta cut). This is the explicit substrate-vs-bench split documented in CONTEXT D-08 + RESEARCH Pitfall 6. No orphaned requirements; ROADMAP.md and REQUIREMENTS.md both map REL-01 + REL-02 to Phase 22, and both IDs appear in the plan's `requirements` frontmatter list.

### Anti-Patterns Found

Scanned files modified in this phase (`firestarter/platformio.ini`, `.planning/ROADMAP.md`):

| File                                | Line | Pattern                                                | Severity | Impact                                                                                                                                                            |
| ----------------------------------- | ---- | ------------------------------------------------------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `firestarter/platformio.ini`        | 75   | `; TODO(v1.5): root-cause the SIGABRT in Unity teardown` | ℹ️ Info  | Pre-existing TODO from v1.4 phase 17 work; explicitly tracked in v1.4 MILESTONES.md "Known Gaps". NOT modified by Phase 22's edit — only line 16 changed. Not a Phase 22 debt-marker. |

No `TBD` / `FIXME` / `XXX` markers introduced by Phase 22. The pre-existing TODO at line 75 is from a previous milestone and has formal follow-up tracking in `v1.4 MILESTONES.md` "Known Gaps" → does not trigger the debt-marker gate.

No stub patterns, empty implementations, hardcoded empty data, or console.log-only implementations in Phase 22's edit surface (config-only phase).

### Human Verification Required

No human verification items required for Phase 22 — per CONTEXT D-08 the local dry-run gate is the shipping criterion. The "inspect release's asset list" portions of REL-01 + REL-02 acceptance are formally deferred to Phase 24 (Bench Validation) and recorded in the `deferred` frontmatter above.

### Gaps Summary

No gaps. Phase 22 ships clean.

**Goal achievement:** The phase goal — "Both workflows emit `firestarter_uno328pb.hex` as a third per-board release artifact alongside the existing two, without altering the existing two's byte content" — is observably achieved at the substrate level:

1. **Both workflows wired to emit 3 artifacts:** `build.yml:100` and `beta-build.yml:77` both invoke `pio run` (no `-e` flag); this now enumerates 3 envs because `default_envs = uno, uno328pb, leonardo`. Both workflows' `files: .pio/build/**/firestarter_*.hex` globs (build.yml:105 + beta-build.yml:92, unchanged per D-03) catch all three hex files.
2. **Third artifact materializes:** `firestarter_uno328pb.hex` (62854 B) builds successfully and is present at the glob-expected path.
3. **Existing two byte-identical:** `cmp -s` against Phase 21 baselines for uno + leonardo both exit 0; SHA-256s match verbatim — Phase 22's widening did NOT perturb the two existing envs' build output. Clean match (not "modulo drift") because `version.h` is pinned at `3.0.0b2` per CONTEXT D-07 + Pitfall 3.

**Substrate vs. live-cut split:** Per CONTEXT D-08 + RESEARCH Pitfall 6, the "inspect release's asset list after a stable/beta cut" portion of REL-01 + REL-02 acceptance is verified at Phase 24's first real beta cut. Phase 22 ships the local dry-run substrate; that is by design, not a gap. The deferred items above record this hand-off explicitly.

**Edit surface = 2 substantive files (exactly per CONTEXT D-10):**
- `firestarter/platformio.ini` line 16 — sub-repo commit `897067b` on `firestarter/v1.5-uno328pb`
- `.planning/ROADMAP.md` line 58 — meta-repo commit `f0aca97` on `/workspaces v1.5-uno328pb`
- (Submodule pointer advance in meta-repo is documented in the same `f0aca97` commit body as intentional per CONTEXT D-10)

**Negative gates honored (D-11):** No edits to `.github/workflows/*.yml`, `firestarter/src/**`, `firestarter/scripts/**`, `firestarter/name_firmware.py`, or `firestarter_app/**`. Verified via `git diff HEAD~1 HEAD --name-only | grep -E '^(\.github|src|scripts)/' | wc -l` returning 0.

**Pitfall 3 preserved:** `firestarter/include/version.h` untouched; `VERSION "3.0.0b2"` literal preserved → GATE-01 cmp -s is a clean match.

**No remote push (D-09):** Both repos clean post-commit, both still on `v1.5-uno328pb`; no `git push` invoked.

---

_Verified: 2026-05-20_
_Verifier: Claude (gsd-verifier)_

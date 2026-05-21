---
phase: "22"
plan: "01"
subsystem: release-pipeline
tags: [v1.5, uno328pb, default_envs, release-pipeline, gate-1.5, gate-01, REL-01, REL-02]
status: complete
autonomous: true
requirements: [REL-01, REL-02]
requirements_addressed: [REL-01, REL-02]
dependency_graph:
  requires:
    - "Phase 21 Plan 21-02 (firestarter/v1.5-uno328pb @ ab7c2a9 — [env:uno328pb] block exists; name_firmware.py reworked; 4 macro guards widened)"
    - ".planning/v1.5/baselines/firestarter_{uno,leonardo}.hex (Phase 21 Plan 21-01 GATE-01 anchors)"
  provides:
    - "REL-01 / REL-02 substrate: `pio run` (no -e flag) produces firestarter_uno328pb.hex alongside the existing two artifacts; release-asset glob captures all three with zero workflow YAML edits"
    - "Phase 22 SC#1 ROADMAP literal aligned with platformio.ini literal (both repos agree on `default_envs = uno, uno328pb, leonardo`)"
  affects:
    - "Phase 24: first real beta cut from firestarter/beta will attach 3 .hex assets (REL-01/REL-02 asset-list inspection verified at that time per CONTEXT D-08 + RESEARCH Pitfall 6)"
    - "Phase 23: unaffected (avrdude profile hand-off from Phase 21 D-10 still belongs to Phase 23 INST-01)"
tech_stack:
  added: []
  patterns:
    - "Coupled meta-repo + sub-repo edit on the matching `v1.5-uno328pb` branch (the v1.4/v1.5 locked-step coordination pattern; Phase 15 precedent)"
    - "GATE-1.5 cmp -s against Phase 21's version-unbumped baselines (Phase 21 Plan 21-02 pattern reused verbatim)"
    - "PROGNAME = `firestarter_<RURP_BOARD_NAME>` via Phase 21's reworked name_firmware.py — automatically catches `firestarter_uno328pb.hex` once `default_envs` lists `uno328pb`"
key_files:
  created:
    - ".planning/phases/22-release-pipeline-artifacts/22-01-SUMMARY.md (this file)"
  modified:
    - "firestarter/platformio.ini (line 16, sub-repo commit 897067b)"
    - ".planning/ROADMAP.md (line 58, meta-repo commit f0aca97)"
    - "firestarter submodule pointer in meta-repo (5fd751e -> 897067b via Phase 21 ab7c2a9 -> Phase 22 897067b; meta-repo commit f0aca97)"
decisions:
  - "Followed CONTEXT D-01..D-11 verbatim with zero deviations — single plan, two coupled commits (sub-repo + meta-repo), both on v1.5-uno328pb"
  - "Did NOT add a defensive size/symbol assertion on firestarter_uno328pb.hex (Claude's Discretion #3) — `cmp -s` against baselines is the strongest available byte-identity gate; an additional check would be ceremony without signal"
  - "Did NOT invoke update_version.py (Pitfall 3 / D-07) — version.h stayed at `3.0.0b2`, enabling clean cmp -s match against Phase 21 baselines (not the `modulo drift` form — that's Phase 24's concern)"
  - "Did NOT push to remote (D-09) — both repos' v1.5-uno328pb branches stay local until Phase 24's merge to firestarter/beta triggers the first real beta cut"
metrics:
  duration: "~3 min"
  completed: "2026-05-20"
  tasks: 3
  files_changed: 3
  commits: 2
  sub_repo_commit: "897067b"
  meta_repo_commit: "f0aca97"
threat_model:
  threats_mitigated:
    - "T-22-01: literal-drift between platformio.ini and ROADMAP.md — mitigated by paired grep -F/grep -E sanity checks in Task 2 + verbatim record in this SUMMARY's Must-Haves Verification table"
    - "T-22-02: workflow YAML tampering — mitigated by D-11 negative gate (`git -C firestarter diff --name-only HEAD~1 HEAD | grep -E '^.github' returns 0`) + post-edit grep returning 2 hits at expected line numbers"
    - "T-22-03: accidental version-string drift via update_version.py — mitigated by version.h diff-empty assertion before AND after every step + VERSION literal grep"
    - "T-22-04: PIO build cache serving stale artifacts — mitigated by `pio run -t clean` BEFORE post-edit `pio run` (Task 3)"
  threats_accepted:
    - "T-22-05: unintended push to remote — accepted because no Task invokes git push and operator convention keeps milestone branches local"
    - "T-22-06: Phase 22 ships without an actual GitHub Release cut — accepted by design (CONTEXT D-08); the asset-list inspection portion of REL-01/REL-02 is verified at Phase 24's first real beta cut per RESEARCH Pitfall 6"
---

# Phase 22 Plan 01: Release Pipeline Artifacts (default_envs widening) Summary

**One-liner:** Widened `firestarter/platformio.ini` `default_envs` from `uno, leonardo` to `uno, uno328pb, leonardo` and realigned the matching ROADMAP literal — substrate for REL-01 + REL-02; release-asset glob now catches three `.hex` artifacts; GATE-01 + GATE-1.5 + native suite green.

## Phase Context

Phase 22 lands the smallest implementation surface in v1.5: **two files, one substantive line of code, one prose realignment.** Phase 21 left the `[env:uno328pb]` block, the reworked `name_firmware.py`, and the four widened macro guards on `firestarter/v1.5-uno328pb @ ab7c2a9`; Phase 22's job is to make `pio run` (no `-e` flag) actually enumerate the new env so the release workflows' existing glob `files: .pio/build/**/firestarter_*.hex` (build.yml:105 + beta-build.yml:92 — unchanged per CONTEXT D-03 / D-11) catches the third artifact at next cut.

Phase 22 ships when the local dry-run is green (CONTEXT D-08). The "inspect release's asset list" portion of REL-01 / REL-02 acceptance is verified at Phase 24's first real beta cut from `firestarter/beta` per CONTEXT D-08 + RESEARCH Pitfall 6 — by design, not a gap.

## Tasks Completed

### Task 1 — Pre-edit GATE-01 sanity (D-06 step a)

Verified the working tree was GATE-1.5-clean BEFORE any edit:

```text
firestarter branch: v1.5-uno328pb
meta branch: v1.5-uno328pb
firestarter HEAD: ab7c2a958bb86018cb68ade3191c27cd814dfc39 (= ab7c2a9)
version.h diff: (empty) — VERSION "3.0.0b2" unchanged
platformio.ini line 16: default_envs = uno, leonardo  (pre-edit state confirmed)

pio run -t clean: exit 0
pio run -e uno -e leonardo: 2 succeeded (uno ~1.15s, leonardo ~1.15s)
cmp -s .pio/build/uno/firestarter_uno.hex      v1.5/baselines/firestarter_uno.hex      -> exit 0
cmp -s .pio/build/leonardo/firestarter_leonardo.hex v1.5/baselines/firestarter_leonardo.hex -> exit 0
```

No file modifications — verification only. Working tree at firestarter/v1.5-uno328pb tip ab7c2a9 produces uno + leonardo artifacts byte-identical to Phase 21 baselines. Post-edit GATE-01 failures (if any) attributable solely to Task 2's edits.

### Task 2 — Coupled default_envs edit (D-01 + D-02 + D-08 section order)

Two atomic commits landed, one per repo, both on `v1.5-uno328pb`:

**Sub-repo commit 897067b on firestarter/v1.5-uno328pb** — `feat(22-01): widen default_envs to include uno328pb`

```diff
--- a/platformio.ini (line 16)
+++ b/platformio.ini
@@ -13,7 +13,7 @@
 ; [env:native] target — it is a test-only environment with no main(), so
 ; linking fails with "undefined reference to main". Constrain default_envs
 ; to the AVR targets; `pio test -e native` still picks up native explicitly.
-default_envs = uno, leonardo
+default_envs = uno, uno328pb, leonardo
```

Body cites Phase 21 D-08 (section order: `[env:uno] -> [env:uno328pb] -> [env:leonardo]`), D-11 (in-scope hand-off), D-12 (ROADMAP realignment hand-off, executed in companion meta-repo commit), and Phase 22 CONTEXT D-01, D-02, D-03, D-08.

Files touched: `platformio.ini` only. No workflow YAML, source, or script edits.

**Meta-repo commit f0aca97 on /workspaces v1.5-uno328pb** — `docs(22-01): realign ROADMAP Phase 22 SC#1 default_envs literal (Phase 21 D-12 hand-off)`

```diff
--- a/.planning/ROADMAP.md (line 58)
+++ b/.planning/ROADMAP.md
-  1. `platformio.ini` `default_envs = uno, leonardo, uno328pb` so a CI-side `pio run` builds all three targets. (Or the workflow explicitly invokes each env — whichever pattern matches the existing CI shape with the smaller diff.)
+  1. `platformio.ini` `default_envs = uno, uno328pb, leonardo` so a CI-side `pio run` builds all three targets. (Order matches the `[env:*]` section order in `platformio.ini` per Phase 21 D-08 + D-12 hand-off; supersedes the original stale literal `uno, leonardo, uno328pb`.) The workflows' existing glob `files: .pio/build/**/firestarter_*.hex` (build.yml:105 + beta-build.yml:92) captures all three artifacts — no workflow edits needed (CONTEXT D-03).
```

Also advanced the `firestarter` submodule pointer from the stale meta-record `5fd751e` (v1.4 baseline that pre-dated Phase 21) to `897067b` (Phase 22 sub-repo widening) so the meta-repo's submodule record now reflects the v1.5-uno328pb-branch state through Phase 22's substrate.

Files touched: `.planning/ROADMAP.md` + `firestarter` submodule pointer only. No firestarter_app edits, no firestarter/src edits, no workflow YAML edits.

Both literals AGREE post-edit. T-22-01 risk surface eliminated.

### Task 3 — Post-edit full verification gate (D-08 steps 1-5) + SUMMARY

Full Phase 22 verification gate executed; transcript in next section.

## Verification Gate Transcript

### D-08 step 1 — clean + env-flag-less build

```text
$ cd firestarter && pio run -t clean
clean exit=0
$ cd firestarter && pio run
Environment    Status    Duration
-------------  --------  ------------
uno            SUCCESS   00:00:01.132
uno328pb       SUCCESS   00:00:01.188
leonardo       SUCCESS   00:00:01.221
========================= 3 succeeded in 00:00:03.541 =========================
```

Three `succeeded` from a bare `pio run` invocation — REL-01 + REL-02 substrate proof.

### D-08 step 2 — artifact presence + workflow-glob simulation

```text
$ ls firestarter/.pio/build/{uno,uno328pb,leonardo}/firestarter_*.hex
firestarter/.pio/build/uno/firestarter_uno.hex          (62617 bytes)
firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex (62854 bytes)
firestarter/.pio/build/leonardo/firestarter_leonardo.hex (68876 bytes)

$ (cd firestarter && shopt -s globstar && ls .pio/build/**/firestarter_*.hex | wc -l)
3
```

Three artifacts present; glob returns 3.

### D-08 step 3 — GATE-01 byte-identity (D-06 post-edit form)

```text
$ cmp -s firestarter/.pio/build/uno/firestarter_uno.hex .planning/v1.5/baselines/firestarter_uno.hex; echo $?
0
$ cmp -s firestarter/.pio/build/leonardo/firestarter_leonardo.hex .planning/v1.5/baselines/firestarter_leonardo.hex; echo $?
0

$ sha256sum firestarter/.pio/build/uno/firestarter_uno.hex .planning/v1.5/baselines/firestarter_uno.hex
0dd5c01a870de38e868bdc71cebd547cb65ed1d7573dc90678c99f7dc3a854d2  firestarter/.pio/build/uno/firestarter_uno.hex
0dd5c01a870de38e868bdc71cebd547cb65ed1d7573dc90678c99f7dc3a854d2  .planning/v1.5/baselines/firestarter_uno.hex

$ sha256sum firestarter/.pio/build/leonardo/firestarter_leonardo.hex .planning/v1.5/baselines/firestarter_leonardo.hex
f49e2a57a2ab8dad7224733d3e5f08f36df2d6aee4c4f924217a4d0c921fdc90  firestarter/.pio/build/leonardo/firestarter_leonardo.hex
f49e2a57a2ab8dad7224733d3e5f08f36df2d6aee4c4f924217a4d0c921fdc90  .planning/v1.5/baselines/firestarter_leonardo.hex
```

Both `cmp -s` exit 0; SHA-256s confirm byte-identity. `default_envs` widening did NOT perturb uno or leonardo output. GATE-01 / GATE-1.5 preserved.

The new third artifact:

```text
$ sha256sum firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex
17439d0f75fbffb69f05ed8ff3cfc8fee496fb96860d113712dd272626507425  firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex
```

(No baseline expected — uno328pb is a new env first shipped in Phase 21; baseline-capture for it is deferred until v1.5 ships per CAPTURE-PROCEDURE.md convention.)

### D-08 step 4 — workflow-glob YAML literal static-analysis

```text
$ grep -Fn 'files: .pio/build/**/firestarter_*.hex' firestarter/.github/workflows/build.yml firestarter/.github/workflows/beta-build.yml
firestarter/.github/workflows/build.yml:105:          files: .pio/build/**/firestarter_*.hex
firestarter/.github/workflows/beta-build.yml:92:          files: .pio/build/**/firestarter_*.hex
```

Exactly 2 hits at the expected line numbers (build.yml:105 + beta-build.yml:92) — literal unchanged from Phase 21 state. Pitfall 5 honored: the YAML literal is the action's contract; the bash globstar (step 2) is a sanity check that the file paths exist with expected names.

```text
$ git -C firestarter diff --name-only HEAD~1 HEAD
platformio.ini

$ git -C firestarter diff --name-only HEAD~1 HEAD | grep -E '^(\.github|src|scripts)/' | wc -l
0
```

D-11 negative gate confirmed: zero forbidden-path edits in Phase 22's sub-repo commit.

### D-08 step 5 — native test regression guard

```text
$ cd firestarter && pio test -e native -f "*test_dispatch*" -f "*test_messages*"
================= 20 test cases: 20 succeeded in 00:00:07.229 =================
```

20/20 PASSED (15 dispatch + 5 messages). The `default_envs` widening does not touch the `[env:native]` env by design (Phase 20 E2E-04 invariant comment block above platformio.ini:16 preserved verbatim); Pitfall 4 (accidental whitespace edits perturbing `[env:native]` parser state) ruled out.

### Pitfall 3 sanity (post-edit)

```text
$ git -C firestarter diff --name-only include/version.h
(empty)
$ grep -F 'VERSION "3.0.0b2"' firestarter/include/version.h
#define VERSION "3.0.0b2"
```

`update_version.py` NOT invoked; `version.h` unmodified throughout Phase 22. GATE-01 cmp -s is a CLEAN match (not "modulo drift").

### D-09 sanity (no remote push)

```text
$ git -C firestarter status -s
(empty)
$ git -C . status -s
(empty)
$ git -C firestarter branch --show-current
v1.5-uno328pb
$ git -C . branch --show-current
v1.5-uno328pb
```

Both repos clean post-commit; both still on `v1.5-uno328pb`. No `git push` invoked anywhere in this plan.

## Must-Haves Verification

| # | Truth (from PLAN must_haves) | Status | Evidence |
|---|------------------------------|--------|----------|
| 1 | `firestarter/platformio.ini` line 16 contains the literal `default_envs = uno, uno328pb, leonardo` (D-08 section order; D-01 + D-02 widening) | PASS | `grep -nE '^default_envs = uno, uno328pb, leonardo$' firestarter/platformio.ini` returns `16:default_envs = uno, uno328pb, leonardo`; sub-repo commit 897067b on v1.5-uno328pb |
| 2 | `.planning/ROADMAP.md` Phase 22 SC#1 literal reads `default_envs = uno, uno328pb, leonardo` (D-02 realignment supersedes the stale `uno, leonardo, uno328pb` form) | PASS | `grep -nF 'default_envs = uno, uno328pb, leonardo' .planning/ROADMAP.md` returns line 58 hit; `grep -nF 'default_envs = uno, leonardo, uno328pb' .planning/ROADMAP.md` returns 0 hits; meta-repo commit f0aca97 |
| 3 | `cd firestarter && pio run` (no -e flag) from a clean tree produces all three `.hex` artifacts: `firestarter_uno.hex`, `firestarter_uno328pb.hex`, `firestarter_leonardo.hex` (D-08 step 1+2) | PASS | `pio run -t clean && pio run` -> 3 succeeded; three files present at `.pio/build/{uno,uno328pb,leonardo}/firestarter_*.hex` (sizes 62617 / 62854 / 68876 bytes) |
| 4 | GATE-01 byte-identity holds POST-edit: `cmp -s firestarter/.pio/build/uno/firestarter_uno.hex .planning/v1.5/baselines/firestarter_uno.hex` AND the leonardo equivalent both exit 0 (D-06) | PASS | both cmp -s exit 0; SHA-256s match baselines verbatim (uno: `0dd5c01a...`, leonardo: `f49e2a57...`) |
| 5 | Workflow glob is unchanged and compatible: `grep -F 'files: .pio/build/**/firestarter_*.hex' firestarter/.github/workflows/build.yml firestarter/.github/workflows/beta-build.yml` returns 2 hits (D-03 / D-04) | PASS | grep returns build.yml:105 + beta-build.yml:92 (2 hits); `git -C firestarter diff --name-only HEAD~1 HEAD .github/` empty (no workflow edits in Phase 22 commit) |
| 6 | Native suite regression-guard green: `pio test -e native -f "*test_dispatch*" -f "*test_messages*"` reports 20/20 PASSED (D-08 step 5) | PASS | `20 test cases: 20 succeeded in 00:00:07.229` |
| 7 | `include/version.h` UNMODIFIED throughout: `git -C firestarter diff --name-only include/version.h` returns empty (Pitfall 3 / D-07) | PASS | `git -C firestarter diff --name-only include/version.h` returns empty before/after every Task; `grep -F 'VERSION "3.0.0b2"' firestarter/include/version.h` returns 1 match |

7/7 must-have truths PASS.

## REL-01 / REL-02 / GATE-01 Substrate Coverage

**REL-01 (stable channel — push to firestarter/main produces a GitHub Release with 3 .hex assets):**
- **Substrate landed by this plan:** `default_envs = uno, uno328pb, leonardo` so `pio run` (the form invoked at build.yml:100) builds all three envs. `softprops/action-gh-release@v2`'s glob `files: .pio/build/**/firestarter_*.hex` at build.yml:105 (unchanged per D-03) captures all three artifacts.
- **Asset-list inspection portion of REL-01 acceptance:** deferred to a future stable cut from firestarter/main (post-v1.5 merge-up). Phase 22 ships the substrate; Phase 22 does NOT push to remote (D-09). The "release's asset list shows three .hex files" check is performed at the first real stable cut, not Phase 22's local dry-run.

**REL-02 (beta channel — push to firestarter/beta produces a GitHub Pre-release with 3 .hex assets):**
- **Substrate landed by this plan:** Same `default_envs` widening drives beta-build.yml:77's `pio run` invocation. Same glob at beta-build.yml:92 (unchanged) captures all three artifacts. `prerelease: true` + `make_latest: false` lines untouched.
- **Asset-list inspection portion of REL-02 acceptance:** Verified at Phase 24 (Bench Validation) per CONTEXT D-08 + RESEARCH Pitfall 6 — when `v1.5-uno328pb` merges to `firestarter/beta` and triggers the beta-build.yml workflow, the operator inspects the resulting GitHub Pre-release's asset list and confirms 3 `.hex` files. Phase 22 -> Phase 24 substrate handoff is identical in shape to Phase 18 -> Phase 20 from v1.4 (Phase 18 shipped the consumer-side CLI substrate verified by unit tests; Phase 20 verified end-to-end against a real beta cut).

**GATE-01 (non-regression on uno + leonardo across v1.4 -> v1.5 boundary):**
- **Verified by this plan:** Both `cmp -s` invocations against `.planning/v1.5/baselines/firestarter_{uno,leonardo}.hex` exit 0 after the `default_envs` widening (D-06 post-edit form). Phase 22's edit is purely additive — uno and leonardo .hex outputs are byte-identical to Phase 21 baselines (which were themselves byte-identical to v1.4 ship state per CAPTURE-PROCEDURE.md, modulo the documented `version.h` pin at `3.0.0b2`).
- **GATE-01 deferred portion:** "Modulo `update_version.py` drift" form (against v1.4 ship tag `3.0.0b3` artifacts on GitHub Releases) is a Phase 24 first-real-cut concern, not Phase 22's. Phase 22 verifies the offline-reproducible CLEAN-match form against the version-unbumped baselines.

## Deviations from Plan

None — the plan executed exactly as written. CONTEXT D-01..D-11 honored verbatim with zero deviations.

No Rule 1 / Rule 2 / Rule 3 auto-fixes were needed. No checkpoints encountered. No authentication gates. The plan's threat model (T-22-01..06) accurately predicted the risk surface; all `mitigate` dispositions were honored procedurally.

## Commits

| # | Repo | Branch | SHA | Subject |
|---|------|--------|-----|---------|
| 1 | firestarter (sub-repo) | v1.5-uno328pb | `897067b` | `feat(22-01): widen default_envs to include uno328pb` |
| 2 | meta (/workspaces) | v1.5-uno328pb | `f0aca97` | `docs(22-01): realign ROADMAP Phase 22 SC#1 default_envs literal (Phase 21 D-12 hand-off)` |

Plus this SUMMARY.md commit + STATE.md / ROADMAP.md plan-progress update commit (next, in the orchestrator's flow).

Both Phase 22 commits cite Phase 21 D-08 + D-12 in the body per CONTEXT D-02. Edit surface = exactly 2 substantive files (`firestarter/platformio.ini` + `.planning/ROADMAP.md`) plus the meta-repo submodule pointer advance for `firestarter` (5fd751e -> 897067b) — matches CONTEXT D-10. No `git push` to any remote (D-09).

## Cross-Phase Hand-Offs

- **Phase 24 (Bench Validation on 328PB-Uno):** First real beta cut is triggered by merging `v1.5-uno328pb` -> `firestarter/beta`. At that time, the asset-list inspection portion of REL-01 + REL-02 acceptance is verified per CONTEXT D-08 + RESEARCH Pitfall 6. Phase 22's `default_envs` widening is the substrate that makes the third asset appear.
- **Phase 23 (Host CLI Installer Integration):** Unchanged by Phase 22. The avrdude profile hand-off from Phase 21 D-10 (`firestarter_app/firestarter/firmware.py:417-423` needs an `uno328pb` branch for partno=`atmega328pb`, programmer_id depends on bootloader, baud_rate=115200) still belongs to Phase 23 INST-01.
- **Phase 25 (Documentation + Milestone Close):** No new doc burden from Phase 22. The release-procedures three-board matrix update (DOC-02) is Phase 25's job; Phase 22 does not pre-write any docs.

## Self-Check: PASSED

**Files created:**
- `.planning/phases/22-release-pipeline-artifacts/22-01-SUMMARY.md` — FOUND (this file)

**Files modified:**
- `firestarter/platformio.ini` — FOUND, line 16 reads `default_envs = uno, uno328pb, leonardo`
- `.planning/ROADMAP.md` — FOUND, line 58 reads `default_envs = uno, uno328pb, leonardo`
- Meta-repo submodule pointer for `firestarter` — advanced from `5fd751e` to `897067b` (verified via `git ls-tree HEAD firestarter`)

**Commits:**
- `897067b` on firestarter/v1.5-uno328pb — FOUND via `git -C firestarter log --oneline | grep 897067b`
- `f0aca97` on meta v1.5-uno328pb — FOUND via `git -C . log --oneline | grep f0aca97`

**Build outputs:**
- `firestarter/.pio/build/uno/firestarter_uno.hex` — FOUND (62617 B, SHA-256 `0dd5c01a...`)
- `firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex` — FOUND (62854 B, SHA-256 `17439d0f...`)
- `firestarter/.pio/build/leonardo/firestarter_leonardo.hex` — FOUND (68876 B, SHA-256 `f49e2a57...`)

**Verification gate:** D-08 steps 1-5 all PASS (3 succeeded; 3-file glob; both cmp -s exit 0; 2 workflow grep hits; 20/20 native tests).

**Branch invariants:** Both repos still on `v1.5-uno328pb`. version.h still at `3.0.0b2`. No remote push.

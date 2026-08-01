# Phase 128 Non-Regression Sweep — closing plan (128-10)

**Written:** 2026-08-01
**Firmware branch (`firestarter`):** `v1.23-py32f071-integration` · **HEAD at this sweep:**
`0de57da3c9edfb40f86eee8b0964e0f1bcdd8559`
**Host branch (`firestarter_app`):** `v1.23-py32f071-integration` · **HEAD at this sweep:**
`cc9452f4db9a814ffb221bab767c24db67288365`
**Meta branch:** `gsd/v1.23-py32f071-integration`

> **No PY32F071 hardware exists.** Nothing in this milestone has ever run on this silicon,
> and nothing in it can. Everything below is about **publication**: that a file with a
> particular name, carrying a particular version string, becomes a downloadable release
> asset. Nothing here says the published image runs, boots, or installs. The permitted claim
> is exactly one sentence wide.

**Re-execution pledge.** Every row in §2 was executed in **this session** (Plan 128-10's
Task 1), against the trees exactly as they now stand — nothing is copied from any of this
phase's nine prior plans' (128-01 through 128-09) SUMMARY files. Where a prior SUMMARY made a
claim (an exit code, a test count, a parsed literal), this document re-checked it
independently against the live tree and says so below. Every row in §3 is `PENDING —
operator dispatch` until Task 3 replaces it with operator-supplied, independently
re-verified evidence.

---

## 1. The claim, as precise statements

1. **REL-01 (ordering + carried version).** In `beta-build.yml`'s single job, the ARM build
   step (`id: arm`) sits strictly after the `update_version.py` step (`id: version`) and the
   `stefanzweifel/git-auto-commit-action@v5` auto-commit step, and strictly before `Release` —
   verified this session by parsing the YAML step order. In addition, a mechanical assertion
   (added Plan 128-06) converts the published `.hex` back to a flat binary and greps for the
   literal `"<steps.version.outputs.version>:py32f071"` in its `strings` output — this can only
   be observed on a real ARM build, so it is a §3 row, not a §2 row.
2. **REL-02 (published as a release asset, glob-matched).** `firestarter_py32f071.hex` is
   published by `softprops/action-gh-release@v2`'s `files:` key (a real GitHub release asset,
   not an Actions artifact), matched via the glob `build/py32f071/firestarter_*.hex`. The
   requirement's own stated rationale ("warns on unmatched glob, fails on missing literal") is
   corrected by research F-1: the action makes no glob-vs-literal distinction at all: the only
   invariant that matters is that `fail_on_unmatched_files` is never set to `true`, verified
   this session (§2). Actual publication as an asset can only be observed on a real dispatch
   (§3).
3. **REL-03 (broken ARM build still publishes the three AVR assets, proven).** An unconditional
   `Assert all AVR release assets are present` step runs immediately before `Release` with no
   `if:` guard, so it always runs regardless of whether the contained ARM steps above it
   succeeded. Locally, `scripts/check_release_assets.py` is proven live this session to exit 0
   against a clean fixture and exit 1 against two distinct planted violations (missing hex,
   zero-byte hex). The actual containment cascade on a broken CMake configure — the real proof
   that this holds under a live GitHub Actions run — can only be observed on rehearsal run B
   (§3).
4. **REL-04 (emitted filename == `asset_candidates("py32f071")[0]`, SDK SHA logged).** Three
   independent things must all be true: the CMake-emitted basename equals the frozen host
   contract (proven this session, §2, and by Plan 128-03's non-vacuous guard); the workflow's
   own in-CI transcription check and the SDK-SHA-vs-`GIT_TAG` equality check exist as exit-code
   assertions in `beta-build.yml` (Plan 128-06, verified by YAML parse in prior plans, re-parsed
   this session); and both actually fire correctly on a real ARM build, which is CI-only (§3).
   The SDK SHA is resolved from the measured FetchContent source directory
   `build/py32f071/_deps/py32f071_sdk-src` (research F-5, measured from real CI run
   `30676982030`'s ninja object paths — not guessed), compared against the pinned `GIT_TAG`.
5. **The ceiling, stated as a negative.** None of the above says or implies that the published
   `firestarter_py32f071.hex` runs, boots, or installs on PY32F071 silicon. No PY32F071 PCB
   exists. The asset publishes; that is the whole claim.

---

## 2. Locally provable, executed now

All commands below were run in this session, in `/workspaces/firestarter` unless noted.

| # | Mechanism | Command | Expected | Observed |
|---|-----------|---------|----------|----------|
| 2.1 | REL-01 step-order (mechanical read) | `python3 -c` parsing `.github/workflows/beta-build.yml`'s `jobs.build.steps`, printing the indices of the `version`, `git-auto-commit-action`, `arm` and `Release` steps | strictly increasing indices | `{'version': 10, 'git-auto-commit': 11, 'arm': 13, 'Release': 20}` → **strictly increasing: True** |
| 2.2 | REL-02 `files:` block, parsed | `python3 -c` YAML-parsing the `Release` step's `with.files` | two-entry list, `.pio/build/**/...` and `build/py32f071/...` | `['.pio/build/**/firestarter_*.hex', 'build/py32f071/firestarter_*.hex']` |
| 2.3 | REL-02 `fail_on_unmatched_files` absence, non-vacuous | comment-stripped grep of `.github/workflows/beta-build.yml` for the literal key, plus a length check on the stripped source | key absent; stripped source non-empty (guard is meaningful, not vacuously passing on an empty file) | `fail_on_unmatched_files present in comment-stripped source: False`; stripped source length **6703 chars** (non-empty) |
| 2.4 | REL-03 checker, clean fixture | `python3 scripts/check_release_assets.py --build-root tests/fixtures/clean_release_assets_all_three/pio_build` | exit 0 | `PASS: leonardo(32 bytes), uno(32 bytes), uno328pb(32 bytes) (build_root=tests/fixtures/clean_release_assets_all_three/pio_build)` — **exit 0** |
| 2.5 | REL-03 checker, planted missing-hex | `python3 scripts/check_release_assets.py --build-root tests/fixtures/planted_release_assets_missing_uno328pb/pio_build` | exit 1, names the missing target | `FAIL:\n  uno328pb: missing .../pio_build/uno328pb/firestarter_uno328pb.hex` — **exit 1** |
| 2.6 | REL-03 checker, planted zero-byte-hex | `python3 scripts/check_release_assets.py --build-root tests/fixtures/planted_release_assets_zero_byte_leonardo/pio_build` | exit 1, names the zero-byte target | `FAIL:\n  leonardo: .../pio_build/leonardo/firestarter_leonardo.hex is 0 bytes` — **exit 1** |
| 2.7 | Firmware pytest full suite | `python3 -m pytest tests/ -q` | green, count unchanged by this phase's non-firmware-compiled work | **180 passed** in 9.70s |
| 2.8 | `pio test -e native` | `pio test -e native` | 141 cases / 17 suites, matching the BASE-01/Phase-123 baseline, unchanged | **141 test cases: 141 succeeded**, 17 suites listed |
| 2.9 | `pio test -e native_nodevtools` | `pio test -e native_nodevtools` | 141 cases / 17 suites, unchanged | **141 test cases: 141 succeeded**, 17 suites listed |
| 2.10 | `test_checker_convention.py` with raised floors | `python3 -m pytest tests/test_checker_convention.py -q` | 7 passed (`FLOOR=6`, `FIXTURE_FLOOR=15`) | **7 passed** in 0.04s |
| 2.11 | Recounted `planted_*` total (files + directories, per the checker's own `glob("planted_*")`, not a directory-only count) | `python3 -c` using `Path('tests/fixtures').glob('planted_*')` | == `FIXTURE_FLOOR` (15) | **15** entries (9 log/cpp files across BASE-08's other checkers + 6 directories, including this phase's 2 planted release-assets dirs) |
| 2.12 | `GIT_TAG` parse, real `CMakeLists.txt` | `sed` expression extracting the 40-hex `GIT_TAG` from `platform/py32f071/CMakeLists.txt` | 40-hex SHA | `0ed2f4b4d3391eccfd4491006a30295fd78e32c2` (40 chars) |
| 2.13 | Host cross-repo binding, PASS-not-SKIP | (`/workspaces/firestarter_app`) `python3 -m pytest tests/test_py32_asset_name_host.py -v -rs` | 10 passed, 0 skipped, no `firestarter firmware checkout absent` skip line | **10 passed** in 0.32s, `-rs` report empty of any skip reason |
| 2.14 | Host skip census | (`/workspaces/firestarter_app`) `python3 -m pytest tests/test_skip_census.py -v` | 5 passed, no new `ALLOWED_SKIP_REASONS` entry needed | **5 passed** in 79.03s |
| 2.15 | Host full suite | (`/workspaces/firestarter_app`) `python3 -m pytest tests/ -q` + `--collect-only -q` cross-check | count unchanged since Plan 128-09 (1303) | run completed with all progress lines `.` (zero `F`/`E`/`s` characters), `30 snapshots passed`; `--collect-only -q` per-file sum == **1303**, matching Plan 128-09's recorded count exactly |
| 2.16 | Firmware tree clean | `git -C /workspaces/firestarter status --porcelain` | empty | empty; `HEAD` == `0de57da3c9edfb40f86eee8b0964e0f1bcdd8559` |
| 2.17 | Host tree — only pre-existing, unrelated dirt | `git -C /workspaces/firestarter_app status --porcelain` | `.gitignore` modified + 4 untracked files (none from this phase); `HEAD` == `cc9452f...` | ` M .gitignore`, `?? .coverage`, `?? .planning/config.json`, `?? SECURITY.md`, `?? write_test_port.sh` — matches the plan's stated pre-existing dirt exactly; `HEAD` == `cc9452f4db9a814ffb221bab767c24db67288365` |
| 2.18 | Repo-wide hyphenated-basename grep | `grep -rn "firestarter-py32f071" --include={*.yml,*.txt,*.md,*.cmake} .` (excluding `.git`) | zero matches | grep exit code **1** (no matches) — zero occurrences |

**Section 2 result: every row executed in this session; no cell reads `PENDING`.**

---

## 3. CI-only, PENDING operator dispatch

Every `Observed` cell below is a placeholder until the operator performs Task 2's checkpoint
(§4) and Task 3 replaces each with the returned, independently re-verified evidence.

| # | Mechanism | Command / Source | Expected | Observed |
|---|-----------|-------------------|----------|----------|
| 3.1 | Run A URL + head commit SHA | operator-reported | a `https://github.com/henols/firestarter/actions/runs/<digits>` URL + 40-hex SHA | PENDING — operator dispatch |
| 3.2 | Run A asset list (API, names + sizes) | `gh release view <rehearsal-tag> --json assets` | four assets: `firestarter_uno.hex`, `firestarter_uno328pb.hex`, `firestarter_leonardo.hex`, `firestarter_py32f071.hex` | PENDING — operator dispatch |
| 3.3 | Run A resolved SDK SHA (step summary) | run A's `$GITHUB_STEP_SUMMARY` | `0ed2f4b4d3391eccfd4491006a30295fd78e32c2` (equal to the pinned `GIT_TAG`, §2.12) | PENDING — operator dispatch |
| 3.4 | Run A resolved `rehearsal` boolean | run A's `mode` step log / step summary | `true` | PENDING — operator dispatch |
| 3.5 | Run A REL-01 image-carries-version PASS line | run A's `Assert the py32 image carries the bumped VERSION (REL-01)` step log | PASS, naming `3.0.0b99:py32f071` | PENDING — operator dispatch |
| 3.6 | Run A: draft created no git tag | `gh api repos/henols/firestarter/git/refs/tags/rehearsal-<run_id>` (expect 404) or equivalent operator confirmation | no tag created | PENDING — operator dispatch |
| 3.7 | Run B URL + head commit SHA | operator-reported | a second, distinct run URL + 40-hex SHA | PENDING — operator dispatch |
| 3.8 | Run B asset list (API, names + sizes) | `gh release view <rehearsal-tag> --json assets` | exactly three AVR hexes, **no** `firestarter_py32f071.hex` | PENDING — operator dispatch |
| 3.9 | Run B `::warning::` annotation + step-summary line (D-07 firing) | run B's page / step summary | `::warning::` present; step summary contains *"PY32F071 image not produced — this release carries no py32f071 asset."* | PENDING — operator dispatch |

**Section 3 result: every cell reads `PENDING — operator dispatch`.**

---

## 4. The operator dispatch procedure

This procedure is written for the **operator only**. No task in this plan executes any of the
commands below; they are instructions to a human. `beta_version` must be supplied on every
dispatch — see step 2's consequence if it is omitted.

1. **Push a throwaway branch.** From `/workspaces/firestarter` on `v1.23-py32f071-integration`,
   create a new branch and push it to `origin` (any name distinct from `beta`/`main` works,
   e.g. `rehearsal-128-10`). Verified this session and in prior phases: pushing a branch that
   is neither `beta` nor `main` fires **nothing** in this repo —
   `beta-build.yml` is `push: [beta]` + `workflow_dispatch`, `py32f071.yml` is `push: [beta]` +
   `pull_request` + `workflow_dispatch`, `build.yml` is `push: [main]` + `pull_request: [main]`.
   The push itself is safe; only the two dispatches below are gated actions.

2. **Run A (healthy).** Dispatch `beta-build.yml` (`gh workflow run beta-build.yml --ref
   rehearsal-128-10 -f rehearsal=true -f beta_version=3.0.0b99`) with **`rehearsal=true`** and
   **`beta_version=3.0.0b99`**. The second input is not optional: `update_version.py`'s
   `is_beta_mode()` returns `True` only when `--beta` is passed, `GITHUB_REF ==
   refs/heads/beta`, or `BETA_VERSION` is a non-empty string (research F-2). A throwaway-branch
   dispatch with `beta_version` left blank satisfies none of the three, so it silently takes
   the **stable** path and rewrites `include/version.h` from `3.0.0b14` to `3.0.1` — and the
   evidence collected would then record a stable version string as proof of a beta fold, which
   is not what REL-01 asks for. `3.0.0b99` is unmistakable, passes the beta version regex, and
   cannot collide with a real future `b15`. **Grep anchor for the wrong path:** if the version
   step's log shows a plain `3.0.1`-shaped string (no `bNN`/`rcNN` suffix) rather than
   `3.0.0b99`, the dispatch took the stable path — stop and re-dispatch with the input supplied
   correctly rather than proceeding.

3. **Flag A4 before the first dispatch.** GitHub resolves the workflow *definition* — including
   the `rehearsal` input, which did not exist before this phase — from the **dispatched ref**,
   not from the default branch. Precedent run `30199560282` proves dispatching from a
   non-default branch works at all, but that run's workflow definition had no *new* input. If
   `gh workflow run` (or the GitHub UI) rejects the dispatch with an unexpected-input or
   unrecognized-input error, **stop and report** rather than working around it — that is
   assumption A4 failing loudly, and it needs an operator/planner decision, not an improvised
   fix.

4. **Collect run A's evidence.** Record the run URL and the head commit SHA. Then run
   `gh release view <the rehearsal-...-tag> --json assets` and record asset **names and
   sizes** — **not** download URLs, since a draft release's asset URLs are `untagged-<hash>`
   placeholders and are not stable citations (research F-3). From the run's step summary,
   confirm: the resolved `rehearsal` boolean reads `true`; the SDK SHA line is present and
   equals the pinned `GIT_TAG` (`0ed2f4b4d3391eccfd4491006a30295fd78e32c2`); and the REL-01
   PASS line names `3.0.0b99:py32f071`. Confirm no tag was created (a draft release creates no
   git tag — `finalizeRelease()`'s early return on `draft: true`, corroborated by the action's
   own `untagged-...` comment and issue #722; D-01's ⚠ VERIFY item, RESOLVED by research F-3).

5. **Run B (planted break).** On the same throwaway branch, commit a change to
   `platform/py32f071/CMakeLists.txt`'s source list that renames one referenced source path so
   **CMake configure** fails — reproducing C-1, the real historical failure this exact target
   had in Phase 124 (a stale hyphenated-name reference caught the same way). Dispatch again
   with the same two inputs (`rehearsal=true`, `beta_version=3.0.0b99`). Collect the run URL,
   the head SHA, the asset list, and a textual (not screenshot) confirmation that the
   `::warning::` annotation and the step-summary line *"PY32F071 image not produced — this
   release carries no py32f071 asset."* both appeared.

6. **Cleanup.** Delete the draft release and delete the throwaway branch. Confirm no tag named
   `rehearsal-*` exists, and that `3.0.0b99` exists neither as a tag nor as a release anywhere
   in the repo.

7. **Two failure signatures to watch for, so a wrong result is recognised rather than absorbed
   as success:**
   - A run B that is **green**, publishes **three AVR assets**, and shows **no** `::warning::`
     annotation and no step-summary line is a **passing REL-03 and a failing D-07 simultaneously**
     — report this rather than accepting it as a clean pass.
   - A `draft` value that resolves `true` on anything **other than** a rehearsal dispatch (e.g.
     a real `beta` push) would silently stop publishing real public betas — if this is ever
     observed on a non-rehearsal run, it is a severe regression, not a rehearsal artifact.

**After the operator returns evidence, paste back:** both run URLs, both head commit SHAs,
both asset lists (names + sizes), the resolved SDK SHA, the resolved rehearsal boolean, and
whether the D-07 warning appeared on run B. Task 3 replaces §3's `PENDING` cells with these
values and re-verifies each one read-only where possible (`gh run view`, `gh api` GETs,
`gh release view --json assets`) — never by dispatching or pushing anything itself.

---

## 5. What this phase does NOT claim

- **The published image has never been executed. No PY32F071 PCB exists.** The permitted claim
  ceiling is exactly one sentence wide: the asset publishes; that is the whole claim. Nothing in
  this phase, in any of its nine prior plans, or in this artifact says or implies the image
  runs, boots, or installs.
- **The cross-repo filename binding is enforced by a local run and by developer discipline, not
  by app CI.** Neither `firestarter_app` CI workflow (`ci.yml`, `beta-release.yml`) checks out
  the firmware sibling repository — both `actions/checkout@v4` steps in both files are plain
  single-repo checkouts with no `repository:`/`path:` arguments (verified by grep, Plan 128-09).
  With no `../firestarter/.git` marker present in that environment, `tests/fw_presence.py`'s
  `FW_REPO_PRESENT` is `False` at import, and all six `@requires_fw` legs of
  `test_py32_asset_name_host.py` SKIP there; only the four unmarked RED demonstrations
  (`TestPy32AssetNameFailsClosedOnBadInput`) actually run in app CI. This is a pre-existing,
  accepted property (Phase 127 D-14 landed the same shape), not something this phase fixes.
  **Claiming CI enforcement would be false.**
- **The `continue-on-error` on the ARM call site in `beta-build.yml` is deliberate and
  permanent for now**, with a recorded removal trigger (D-05): it comes off when the PY32F071
  target is validated on real silicon. No PCB exists, so this trigger is unreachable this
  milestone, and the flag stays. This is a decision, not an oversight.
- **No ARM number anywhere in this phase was measured locally.** There is no `arm-none-eabi-gcc`
  / `cmake` / `ninja` toolchain in this devcontainer, so no local ARM build or measurement is
  possible. Every ARM figure in this phase — flash/RAM figures, the resolved SDK SHA, the
  version-string proof, the asset lists — cites a CI workflow run URL plus a commit SHA. A
  local `pio` run is never evidence about ARM.

---

## 6. Precedent and prior art

On **2026-07-26**, run
[`30199560282`](https://github.com/henols/firestarter/actions/runs/30199560282) dispatched
`beta-build.yml` (`workflow_dispatch`) from the **non-default branch**
`v1.21-community-chip-validation-command`. Two minutes later (2026-07-26T11:10:01Z) it
published the **real, public** prerelease `3.0.0b11` with a **real git tag**:
`refs/tags/3.0.0b11` → `0fd7992187467f6d245bc106786253f497ea0ecc`. That commit is contained in
`origin/beta`, `origin/v1.21-community-chip-validation-command` and
`origin/v1.23-py32f071-integration`.

D-01's draft-mode containment is not theoretical caution — **the exact accident it prevents has
already happened once, from precisely this route** (dispatching this workflow from a
non-default branch). Two things follow from this precedent:

1. **The mechanism D-01 needs is proven to work.** The "a `workflow_dispatch` workflow must
   live on the default branch" folklore does not block dispatching from a throwaway branch —
   `gh` is authenticated with `repo` + `workflow` scopes, and GitHub resolves the workflow
   *definition* (including any input new on that ref) from the dispatched ref itself.
2. **D-03's permanent `rehearsal-${{ github.run_id }}` tag override is justified by this
   precedent, not by hypothetical caution.** Without draft mode and the tag override, a
   rehearsal dispatch of this exact workflow, from this exact non-default-branch route, is
   proven capable of publishing a real public prerelease with a real tag — because it already
   did, once, before draft mode existed.

This belongs in Phase 130's CLOSE-02 honesty ledger alongside the two other stray prereleases
already recorded there (the v1.22-era `3.0.0b12` pair) as the strongest available justification
for why the `rehearsal` input is permanent (D-03) rather than removable once this phase closes.

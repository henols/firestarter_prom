# Phase 17: Firmware Beta Release Pipeline — Research

**Researched:** 2026-05-20
**Domain:** PlatformIO CI/CD, GitHub Actions workflow authoring (YAML), firmware hex artifact naming, native Unity test invocation, softprops/action-gh-release v2
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Create NEW workflow file `firestarter/.github/workflows/beta-build.yml`. Do NOT modify `build.yml`. GATE-02 verified by `git diff build.yml` returning empty after the Phase 17 PR.
- **D-02:** Naming: `beta-build.yml`. Job name `build` (mirrors `build.yml`). Workflow display name `Firestarter beta pre-release build`.
- **D-03:** Triggers: `push: branches: [beta]` + `paths-ignore` (byte-match `build.yml`) + `workflow_dispatch: inputs: beta_version: (required: false, type: string)`.
- **D-04:** `paths-ignore` byte-matches `build.yml`'s list: `**.md`, `**.sh`, `.gitignore`, `docs/**`, `documents/**`, `images/**`, `.vscode/**`, `.editorconfig/**`. Firmware list differs from app's (extra `documents/**` and `.editorconfig/**`).
- **D-05:** `workflow_dispatch` is the canonical lockstep-cut mechanism per Phase 15 D-01 / Phase 16 D-05. Release engineer runs `gh workflow run beta-build.yml --ref beta -f beta_version=3.1.0b1` from `firestarter/`.
- **D-06:** No `pull_request` trigger. Beta cuts are operator-initiated; PR-to-beta validation not needed.
- **D-07:** Gates run INLINE BEFORE version bump. Sequence:
  1. `actions/checkout@v4` with `fetch-depth: 0`
  2. `actions/cache@v4` (pip + ~/.platformio caches)
  3. `actions/setup-python@v5` with `python-version: '3.11'`
  4. Catalog validity check
  5. Codegen drift gate (messages.h, C++)
  6. Install PlatformIO Core
  7. Run native unit tests: `pio test -e native`
  8. Install pytest
  9. Run update_version.py tests: `pytest tests/ -v`
- **D-08:** After gates:
  10. Generate release version (update_version.py, `id: version`, `env: BETA_VERSION`)
  11. `stefanzweifel/git-auto-commit-action@v5` with NO `with:` block (anti-loop pattern)
  12. Build PlatformIO Project: `pio run`
  13. Release: `softprops/action-gh-release@v2` with `files: .pio/build/**/firestarter_*.hex`, `prerelease: true`, `make_latest: false`, `token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}`
- **D-09:** Artifacts: `files: .pio/build/**/firestarter_*.hex`. Publisher-consumer contract with Phase 18 downloader.
- **D-10:** `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}` on version-bump step.
- **D-11:** `fetch-depth: 0` REQUIRED for tag-scan fallback.
- **D-12:** No `pull_request:` trigger in beta-build.yml.
- **D-13:** Mirror `build.yml`'s `actions/cache@v4` step verbatim.
- **D-14:** Use ONLY `actions/setup-python@v5` with `python-version: '3.11'`. Do NOT replicate `build.yml`'s vestigial `actions/setup-python@v4` step.
- **D-15:** Rationale for D-14: Phase 17 is a new file; known-dead step would propagate tech debt. GATE-02 asserts build.yml byte-identity, not beta-build.yml verbatim similarity.
- **D-16:** `actions/checkout@v4` with `fetch-depth: 0`.
- **D-17:** `softprops/action-gh-release@v2`: `prerelease: true`, `make_latest: false`, `files: .pio/build/**/firestarter_*.hex`, `tag_name: ${{ steps.version.outputs.version }}`, `token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}`.
- **D-18:** Permissions: `permissions: contents: write` at JOB level.
- **D-19:** GATE-02 verification: (1) `git -C firestarter diff HEAD~N -- .github/workflows/build.yml` empty; (2) `beta-build.yml` is ONLY workflow file added; (3) `pytest tests/ -v` still passes.

### Claude's Discretion

- **D-20:** YAML quoting style — 2-space indent, single-quoted strings; consistent with build.yml.
- **D-21:** No `concurrency` group (mirror Phase 16 D-25).
- **D-22:** Omit build.yml's commented-out `tagging_message` and `env: GITHUB_TOKEN` from the auto-commit step. Carry only clean, live configuration into a new file.
- **D-23:** Use `Set up Python 3.11 for codegen` step name (matches build.yml line 55 for consistency).

### Deferred Ideas (OUT OF SCOPE)

- Reusable workflow extraction (gates shared between build.yml + beta-build.yml) — v1.5+.
- `concurrency` group.
- Branch protection on `beta`.
- Auto-promotion beta to stable.
- Cleanup of build.yml's vestigial setup-python@v4 step (GATE-02 requires build.yml byte-identity).
- PR validation on beta branch.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-02 | Push to `firestarter/beta` triggers workflow: runs existing build pipeline (catalog validity, codegen drift, native Unity tests, PlatformIO build), bumps pre-release version, creates GitHub Release with `prerelease: true`, `make_latest: false`, and `firestarter_*.hex` artifacts per board | §Technical Findings 1–6, §Implementation Approach (full YAML) |
| GATE-02 | After v1.4 lands, push to `firestarter/main` still produces GitHub Release with `make_latest: true`, same `firestarter_*.hex` per board, version bumped in `include/version.h`, existing catalog-validity + codegen-drift + Unity-test gates run unchanged. No new mandatory CI checks added to stable path. | §Technical Finding 7, §Pitfall 4 |
</phase_requirements>

---

## Summary

Phase 17 delivers exactly one new file: `firestarter/.github/workflows/beta-build.yml`. The structure is a near-clone of `build.yml` (the structural template, lines 1-109) with five targeted changes: (1) trigger branch flipped from `main` to `beta`, (2) `workflow_dispatch` block added with `beta_version` input, (3) vestigial `actions/setup-python@v4` step omitted, (4) `fetch-depth: 0` added to checkout, and (5) `prerelease: true` + `make_latest: false` + `token:` added to the release step.

All Phase 16 findings carry across unchanged — the anti-loop analysis (no `token:` on checkout step), `github.event.inputs.beta_version` evaluating to empty string on push triggers, `paths-ignore` scope under push only, and `make_latest: false` semantics are firmware-identical to the app side. This research focuses on the four firmware-specific questions: PlatformIO board enumeration and hex naming, native Unity test invocation, `actions/cache@v4` key/path pairs, and the `softprops` `**` glob acceptance.

The `name_firmware.py` extra_script (line 22 of `platformio.ini`) sets `PROGNAME=firestarter_{board}`, so PlatformIO produces `firestarter_uno.hex` and `firestarter_leonardo.hex` in their respective `.pio/build/{board}/` subdirectories. The glob `.pio/build/**/firestarter_*.hex` in `build.yml` line 105 covers both boards and any future additional board environments without modification.

**Primary recommendation:** Write `beta-build.yml` as a clean near-clone of `build.yml` with the five targeted changes above. One file, no edits to existing files.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Catalog validity + codegen drift gate | CI Workflow (beta-build.yml) | — | Inline copy from build.yml; gates must veto version bump if they fail (D-07); read-only steps on fresh checkout |
| Native Unity tests | CI Workflow (beta-build.yml, `pio test -e native`) | — | Host-side, no AVR board needed; established in Phase 6 WR-01; runs before version bump |
| pytest (update_version.py tests) | CI Workflow (beta-build.yml) | — | Phase 15-03 added test infrastructure to build.yml; beta-build.yml mirrors pattern |
| Pre-release version computation | CI Script (update_version.py) | — | Phase 15 deliverable; workflow passes `BETA_VERSION` env + runner provides `GITHUB_REF` |
| Git auto-commit of version bump | CI Workflow (git-auto-commit-action@v5) | — | Default GITHUB_TOKEN prevents re-trigger loop; no `token:` override |
| PlatformIO firmware build | CI Workflow (beta-build.yml, `pio run`) | — | Builds ALL configured board environments; must run AFTER version bump so hex embeds correct version |
| GitHub Release creation (prerelease: true) | CI Workflow (softprops/action-gh-release@v2) | — | `prerelease: true` + `make_latest: false`; `.hex` glob covers all boards |
| GATE-02 regression verification | CI (git diff assertion) | — | D-19: `git diff build.yml` returns empty after Phase 17 commit |

---

## Standard Stack

### Core (all pre-existing in firestarter; no new deps)

| Action | Version | Purpose | Why Standard |
|--------|---------|---------|--------------|
| `actions/checkout` | v4 | Repository checkout with full tag history (`fetch-depth: 0`) | Already used in build.yml line 35 |
| `actions/cache` | v4 | pip + PlatformIO cache (`~/.cache/pip`, `~/.platformio/.cache`, key `${{ runner.os }}-pio`) | Already used in build.yml lines 37-42; speeds up PlatformIO Core install |
| `actions/setup-python` | v5 | Python 3.11 environment | Used in build.yml line 56 (the non-vestigial step) |
| `stefanzweifel/git-auto-commit-action` | v5 | Auto-commit version bump to beta branch | Already used in build.yml line 93 |
| `softprops/action-gh-release` | v2 | Create GitHub Release with hex artifacts, `prerelease: true`, `make_latest: false` | Already used in build.yml line 103; v2 required for `make_latest` parameter |

**No new actions and no new secrets are required.** All five actions are already pinned in build.yml. `secrets.PERSONAL_ACCESS_TOKEN` is already configured for this repository (visible at build.yml line 108 as commented-out fallback).

### Version Notes

`softprops/action-gh-release@v2` is the current pinned major version in `build.yml`. The `files:` glob parameter supporting `**` is verified by build.yml line 105 (`files: .pio/build/**/firestarter_*.hex`) being the pre-existing stable release artifact pattern. [VERIFIED: /workspaces/firestarter/.github/workflows/build.yml lines 103-109]

---

## Architecture Patterns

### System Architecture Diagram

```
Operator pushes to firestarter/beta  OR  gh workflow run beta-build.yml --ref beta -f beta_version=X.Y.ZbN
                │
                ▼
beta-build.yml fires (push: branches:[beta] OR workflow_dispatch)
                │
        ┌───────▼────────────────────────────────────────┐
        │  GATE SEQUENCE (fail-stop)                     │
        │  1. actions/checkout@v4                        │
        │     with: fetch-depth: 0                       │
        │  2. actions/cache@v4                           │
        │     ~/.cache/pip + ~/.platformio/.cache        │
        │  3. actions/setup-python@v5 (3.11)             │
        │  4. catalog validity check                     │
        │     (codegen.py --check)                       │
        │  5. codegen drift gate (messages.h, C++)       │
        │     (regen + git diff --exit-code)             │
        │  6. pip install --upgrade platformio           │
        │  7. pio test -e native                         │
        │  8. pip install pytest                         │
        │  9. pytest tests/ -v                           │
        └────────────────────────────────────────────────┘
                │ ALL GATES GREEN
                ▼
        VERSION BUMP
        update_version.py
          env: GITHUB_REF = refs/heads/beta     (auto-set by runner)
          env: BETA_VERSION = ${{ github.event.inputs.beta_version }}
                                                 (empty string on push → git-tag-scan)
          writes include/version.h: #define VERSION "X.Y.ZbN"
          outputs: steps.version.outputs.version = X.Y.ZbN
                │
                ▼
        AUTO-COMMIT (GITHUB_TOKEN — does NOT re-trigger push workflows)
        stefanzweifel/git-auto-commit-action@v5
          pushes to beta branch
                │
                ▼
        PlatformIO BUILD
        pio run
          builds ALL configured board environments (uno, leonardo)
          name_firmware.py: PROGNAME = firestarter_{board}
          output: .pio/build/uno/firestarter_uno.hex
                  .pio/build/leonardo/firestarter_leonardo.hex
                │
                ▼
        GITHUB RELEASE
        softprops/action-gh-release@v2
          files: .pio/build/**/firestarter_*.hex   ← captures all boards
          tag_name: X.Y.ZbN
          prerelease: true
          make_latest: false       ← beta never becomes "Latest"
          token: secrets.PERSONAL_ACCESS_TOKEN
                │
        firestarter --install --pre (Phase 18 downloader) ← consumer opt-in
```

### Recommended Project Structure

```
firestarter/
└── .github/
    └── workflows/
        ├── build.yml             # UNCHANGED (push/PR to main → stable release)
        └── beta-build.yml        # NEW (push to beta OR workflow_dispatch → beta pre-release)
```

No other files change in Phase 17.

---

## Implementation Approach: Complete YAML for beta-build.yml

This is the full recommended YAML, derived from:
1. `build.yml` (structural template) [VERIFIED: read directly, lines 1-109]
2. Phase 16 `beta-release.yml` (trigger pattern, env-passthrough pattern) [VERIFIED: read directly]
3. Phase 15 contract (BETA_VERSION env, fetch-depth requirement) [VERIFIED: 15-LOCKSTEP-PROCEDURE.md]
4. D-01 through D-23 (locked decisions in 17-CONTEXT.md)

```yaml
name: Firestarter beta pre-release build
on:
  push:
    branches:
    - beta
    paths-ignore:
    - '**.md'
    - '**.sh'
    - '.gitignore'
    - 'docs/**'
    - 'documents/**'
    - 'images/**'
    - '.vscode/**'
    - '.editorconfig/**'
  workflow_dispatch:
    inputs:
      beta_version:
        description: 'Explicit PEP 440 pre-release version (e.g. 3.1.0b1). Leave blank for auto-increment via git-tag scan.'
        required: false
        type: string

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pip
            ~/.platformio/.cache
          key: ${{ runner.os }}-pio

      - name: Set up Python 3.11 for codegen
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Catalog validity check
        run: python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check

      - name: Codegen drift gate (messages.h)
        run: |
          python3 tools/catalog/codegen.py \
            --catalog tools/catalog/messages.toml \
            --target include/messages.h \
            --language cpp
          git diff --exit-code include/messages.h

      - name: Install PlatformIO Core
        run: pip install --upgrade platformio

      - name: Run native unit tests
        run: pio test -e native

      - name: Install pytest for script tests
        run: pip install pytest

      - name: Run update_version.py tests
        run: pytest tests/ -v

      - name: Generate release version
        id: version
        env:
          BETA_VERSION: ${{ github.event.inputs.beta_version }}
        run: .github/scripts/update_version.py

      - uses: stefanzweifel/git-auto-commit-action@v5

      - name: Build PlatformIO Project
        run: pio run

      - name: Release
        uses: softprops/action-gh-release@v2
        with:
          files: .pio/build/**/firestarter_*.hex
          tag_name: ${{ steps.version.outputs.version }}
          prerelease: true
          make_latest: false
          token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
```

**Design notes:**

1. `actions/cache@v4` step is unnamed (mirrors `build.yml` lines 37-42 verbatim — no `name:` field on that step). [VERIFIED: build.yml lines 37-42]

2. `actions/checkout@v4` step is also unnamed (mirrors `build.yml` line 35 verbatim). The `with: fetch-depth: 0` is the only addition over build.yml's checkout step.

3. `GITHUB_REF` is NOT manually injected in the version-bump step's `env:`. GitHub Actions injects `GITHUB_REF=refs/heads/beta` automatically on every run targeting the beta branch. Phase 15's `is_beta_mode()` reads it via `os.environ.get("GITHUB_REF")`. [VERIFIED: Phase 15 update_version.py lines 57-58]

4. `BETA_VERSION: ${{ github.event.inputs.beta_version }}` evaluates to empty string on push-triggered runs (not null). Phase 15's `compute_beta_version()` treats empty string as "unset" and falls back to git-tag-scan. [INHERITED from Phase 16 Finding 2]

5. `stefanzweifel/git-auto-commit-action@v5` has NO `with:` block (mirrors build.yml line 93-97 — the commented-out `tagging_message` and `GITHUB_TOKEN` blocks are intentionally omitted per D-22). Using default GITHUB_TOKEN prevents re-trigger loop. [INHERITED from Phase 16 Finding 4]

6. The `Release` step uses `token:` inside `with:` (not `env: GITHUB_TOKEN:`). This matches D-17 explicitly and is the `softprops/action-gh-release@v2` canonical parameter name. Phase 16's `beta-release.yml` uses the `env: GITHUB_TOKEN:` pattern instead — both are valid for `softprops`, but D-17 specifies `token:` for Phase 17. [VERIFIED: 17-CONTEXT.md D-17; softprops v2 supports both]

7. `paths-ignore` is placed ONLY under the `push:` event block, not under `workflow_dispatch`. Correct: `paths-ignore` is silently ignored under `workflow_dispatch`. [INHERITED from Phase 16 Pitfall 3]

8. `permissions: contents: write` is at the JOB level, matching `build.yml` lines 31-32 exactly. [VERIFIED: build.yml lines 31-32]

---

## Key Technical Findings

### Finding 1: PlatformIO Board Environments — Confirmed Enumeration

[VERIFIED: /workspaces/firestarter/platformio.ini — read directly]

`platformio.ini` defines exactly **three** named environments:
- `[env:uno]` — `platform = atmelavr`, `board = uno`
- `[env:leonardo]` — `platform = atmelavr`, `board = leonardo`
- `[env:native]` — `platform = native`, `test_framework = unity` (test-only; no hex artifact)

`pio run` (with no `-e` flag) builds ALL non-test environments. The `[env:native]` environment has `platform = native` and produces an ELF binary for host testing, NOT a `.hex` file. PlatformIO skips native environments during `pio run` (it only runs the `[env:uno]` and `[env:leonardo]` environments that have `framework = arduino`).

**Result:** `pio run` produces exactly two `.hex` files: `firestarter_uno.hex` and `firestarter_leonardo.hex`.

### Finding 2: Hex File Naming — `name_firmware.py` Extra Script

[VERIFIED: /workspaces/firestarter/name_firmware.py — read directly; /workspaces/firestarter/platformio.ini line 22]

`platformio.ini` has `extra_scripts = pre:name_firmware.py` in the `[env]` global section (applies to all environments). The script:

```python
Import("env")
board = env.GetProjectOption("board")
env.Replace(PROGNAME="firestarter_%s" % board)
```

PlatformIO's default output filename is `firmware.hex`. `name_firmware.py` replaces `PROGNAME` with `firestarter_{board}`, producing:
- `.pio/build/uno/firestarter_uno.hex`
- `.pio/build/leonardo/firestarter_leonardo.hex`

The glob `.pio/build/**/firestarter_*.hex` matches both paths via the `**` wildcard (matches any path depth including a single directory segment). This is the artifact pattern used in `build.yml` line 105 and is the publisher-consumer contract with Phase 18's downloader (`INST-02` asset selection logic greps for `firestarter_{board}.hex`).

**Consequence:** Adding a new board environment (e.g., `[env:mega]`) automatically produces `firestarter_mega.hex` and is picked up by the glob without any `beta-build.yml` change.

### Finding 3: `softprops/action-gh-release@v2` — `**` Glob Accepted

[VERIFIED: /workspaces/firestarter/.github/workflows/build.yml line 105 — the stable build already uses this exact glob in production]

`build.yml` line 105 uses `files: .pio/build/**/firestarter_*.hex` for the stable release. This means softprops v2 accepts the `**` glob in production today. The glob is not a Phase 17 hypothesis; it is a verified production pattern in the stable pipeline. `beta-build.yml` mirrors it identically.

**If no files match the glob:** softprops/action-gh-release@v2 will error if the `files:` pattern resolves to zero files. This means `pio run` must execute BEFORE the Release step (which it does — D-08 step 12 precedes step 13). If `pio run` fails or produces no hex, the workflow errors at the build step before reaching the Release step.

### Finding 4: Native Unity Test Step — `pio test -e native`

[VERIFIED: /workspaces/firestarter/platformio.ini — `[env:native]` section; /workspaces/firestarter/.github/workflows/build.yml line 80; /workspaces/firestarter/CLAUDE.md — Native test documentation]

`build.yml` line 79-80 runs `pio test -e native` as an inline gate before the version bump. The `-e native` flag runs only the `[env:native]` test environment (host-side; no AVR board required). The native suite tests `configure_memory()` dispatch logic via Unity test cases.

`beta-build.yml` mirrors this step identically. The native test environment is fully self-contained: `test/native/avr/test_dispatch/host_stubs.cpp` stubs all `rurp_*` symbols; `pio test -e native` requires no hardware, no board, no serial connection.

**Important:** `pio test` is separate from `pio run`. `pio test -e native` compiles and runs the Unity test binary against the host; `pio run` compiles the firmware binary for each board target. Both steps are present in `beta-build.yml`. They are NOT interchangeable.

### Finding 5: `actions/cache@v4` — Exact Key/Path Pairs

[VERIFIED: /workspaces/firestarter/.github/workflows/build.yml lines 37-42 — read directly]

The cache step in `build.yml`:

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      ~/.platformio/.cache
    key: ${{ runner.os }}-pio
```

- `~/.cache/pip` — pip download cache (speeds up `pip install --upgrade platformio` and `pip install pytest`)
- `~/.platformio/.cache` — PlatformIO's package/platform cache (speeds up PlatformIO Core install and board SDK downloads)
- Key `${{ runner.os }}-pio` — OS-keyed; cache is shared between `build.yml` and `beta-build.yml` runs (same key, same runner OS `Linux`). This is correct and desirable — a stable-branch `build.yml` run warms the cache; a subsequent `beta-build.yml` run benefits from it.

`beta-build.yml` mirrors this step byte-identically per D-13.

### Finding 6: pytest Step Pattern — Exact Commands from build.yml

[VERIFIED: /workspaces/firestarter/.github/workflows/build.yml lines 82-86 — read directly]

`build.yml` has two pytest-related steps:
1. `Install pytest for script tests` — `run: pip install pytest`
2. `Run update_version.py tests` — `run: pytest tests/ -v`

These are separate steps (not a combined install-and-run). `beta-build.yml` mirrors both step names and commands identically. The `tests/` directory contains `test_update_version.py` (Phase 15-03 deliverable). No additional test files are added in Phase 17.

**Test path:** `pytest tests/ -v` runs all tests under `firestarter/tests/`. Currently only `test_update_version.py` exists there. `beta-build.yml` uses the same broad `tests/` target so any future test files in that directory are automatically included.

### Finding 7: GATE-02 Verification — Stable Pipeline Non-Regression

[VERIFIED: /workspaces/firestarter/.github/workflows/build.yml — read directly; D-19 in CONTEXT.md]

GATE-02 verification is implemented via git diff assertions per D-19:

```bash
# Run from meta-repo root after Phase 17 PR merges:
git -C firestarter diff HEAD~1 -- .github/workflows/build.yml    # must be empty
git -C firestarter status -- .github/workflows/                  # must show ONLY beta-build.yml as new
```

Additionally, Phase 17 must not add any new MANDATORY CI checks to build.yml. The verification above confirms this: if `build.yml` is byte-identical, no new steps were added to it.

### Finding 8: `fetch-depth: 0` and Cache Restore Interaction

[ASSUMED — based on GitHub Actions caching behavior; no edge case observed or documented suggesting conflict]

`actions/cache@v4` restore is keyed by `${{ runner.os }}-pio` and operates on filesystem paths (`~/.cache/pip`, `~/.platformio/.cache`). These paths are independent of the git checkout depth. A full-history clone (`fetch-depth: 0`) does not affect cache key computation or cache restoration. The cache restore happens before checkout modifies any git objects. No interaction issue exists.

**Confidence:** LOW on the explicit non-interaction claim (not independently doc-verified in this session), but the behavior is standard GitHub Actions cache semantics. Tagged `[ASSUMED]` accordingly.

---

## Inherited Findings from Phase 16 (no re-verification needed)

All of the following Phase 16 findings apply to Phase 17 without firmware-specific variation:

| Phase 16 Finding | Phase 17 Application |
|-----------------|---------------------|
| Finding 1: `workflow_dispatch.inputs` YAML shape | Identical input shape in beta-build.yml |
| Finding 2: `github.event.inputs.beta_version` empty string on push | Same env passthrough pattern; same git-tag-scan fallback behavior |
| Finding 3: `softprops/action-gh-release@v2` — `prerelease: true` + `make_latest: false` | Identical flags; `files:` glob differs (`.hex` not wheel) |
| Finding 4: `stefanzweifel/git-auto-commit-action@v5` — no infinite loop | Identical: no `token:` on checkout step, no PAT on auto-commit step |
| Finding 6: `release: published` event (N/A for firmware — no `publish.yml` analogue) | Firmware has no `publish.yml`; GitHub Release IS the final destination |
| Pitfall 1: Auto-commit PAT loop | Apply identically — DO NOT add `token:` to checkout |
| Pitfall 2: Missing `fetch-depth: 0` | Apply identically — git-tag-scan needs full history |
| Pitfall 3: `paths-ignore` under `workflow_dispatch` | Apply identically — place ONLY under `push:` |
| Pitfall 4: `.yaml` extension | Filename must be `beta-build.yml` (`.yml`) |
| Pitfall 5: `make_latest: false` seemingly redundant | Keep it — explicit self-documentation |
| Pitfall 6: `GITHUB_REF` explicit injection not needed | Apply identically — runner injects automatically |

**Reference:** `.planning/phases/16-app-beta-release-pipeline/16-RESEARCH.md` — Findings 1-8 and Pitfalls 1-8 document all GitHub Actions mechanics; Phase 17 inherits them verbatim.

---

## Firmware-Specific Differences from Phase 16

| Area | Phase 16 (App) | Phase 17 (Firmware) |
|------|----------------|---------------------|
| Job name | `github` | `build` (mirrors build.yml) |
| Workflow display name | `Create a new beta pre-release` | `Firestarter beta pre-release build` |
| `paths-ignore` list | `**.md`, `**.sh`, `.gitignore`, `docs/**`, `images/**`, `.github/**`, `.vscode/**`, `tools/**` | `**.md`, `**.sh`, `.gitignore`, `docs/**`, `documents/**`, `images/**`, `.vscode/**`, `.editorconfig/**` (byte-matches firmware build.yml) |
| PlatformIO cache | — | `actions/cache@v4` with `~/.platformio/.cache` added to path |
| Build tool | `python3 -m build` (wheel/sdist) | `pio run` (hex artifacts) |
| Test gate | `pip install -e .[dev]` + `pytest tests/ -v` | `pip install --upgrade platformio` + `pio test -e native` + `pip install pytest` + `pytest tests/ -v` |
| Codegen target | `firestarter/messages.py` `--language python` | `include/messages.h` `--language cpp` |
| Artifacts | — (PyPI publish via `publish.yml` delegation) | `.pio/build/**/firestarter_*.hex` |
| Release token | `env: GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}` | `token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}` (under `with:`) |
| PyPI publish | Delegated to `publish.yml` via `release: published` event | None — GitHub Release IS the artifact destination |

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| GitHub Release creation with hex artifacts | Custom `gh release create` shell step | `softprops/action-gh-release@v2` | Already used in build.yml; handles tag creation, asset upload, prerelease flag, make_latest atomically |
| Version bump git commit | `git add && git commit && git push` shell step | `stefanzweifel/git-auto-commit-action@v5` | Already used in build.yml; handles no-change case gracefully; uses GITHUB_TOKEN by default (no loop) |
| Board-specific hex naming | Custom shell rename loop | PlatformIO `extra_scripts = pre:name_firmware.py` | Already established in platformio.ini; PROGNAME replacement happens at build time |
| Pre-release version computation | Custom shell arithmetic or sed | Phase 15's `update_version.py` | Already shipped; validates input, handles git-tag-scan fallback, writes `GITHUB_OUTPUT` |

**Key insight:** Phase 17 is pure assembly work — wiring together already-working components (build.yml gates, Phase 15 script, Phase 16 trigger pattern). No new logic is introduced.

---

## Common Pitfalls

### Pitfall 1: Omitting `pio run` Step (Release with No Artifacts)

**What goes wrong:** If the `Build PlatformIO Project` step is omitted or placed AFTER the Release step, `softprops/action-gh-release@v2` finds no files matching `.pio/build/**/firestarter_*.hex` and errors out OR creates a release with zero artifacts.

**Why it happens:** A reviewer might assume the hex files already exist from a prior build. They do not — GitHub Actions runners start from a clean workspace.

**How to avoid:** The `Build PlatformIO Project: pio run` step MUST precede the `Release` step. Sequence per D-08: gates → version bump → auto-commit → `pio run` → Release.

**Warning signs:** Release step errors with "No files found matching pattern" or GitHub Release is created with no assets attached.

### Pitfall 2: Replicating `build.yml`'s Vestigial `setup-python@v4` Step

**What goes wrong:** Copying `build.yml` lines 44-45 (`- uses: actions/setup-python@v4`) into `beta-build.yml`. This creates a no-op step that installs an unspecified Python version and is immediately shadowed by the explicit `@v5 python-version: 3.11` step that follows.

**Why it happens:** Mechanical copy-paste of `build.yml`. The vestigial step at build.yml line 44 is flagged as `IN-02` in Phase 18 code review — it is dead code.

**How to avoid:** Per D-14 and D-15, `beta-build.yml` uses ONLY `actions/setup-python@v5` with `python-version: '3.11'`. There is no `@v4` step. GATE-02 asserts `build.yml` is byte-identical; it does NOT require `beta-build.yml` to be a verbatim copy of `build.yml`.

### Pitfall 3: Missing `actions/cache@v4` Step

**What goes wrong:** Omitting the pip + PlatformIO cache step means every beta run re-downloads PlatformIO Core (~50MB) and all board SDKs from scratch. Not a functional error, but adds 3-5 minutes per run.

**Why it happens:** The cache step in `build.yml` is unnamed (`- uses: actions/cache@v4` with no `name:` field), making it visually easy to skip in a manual transcription.

**How to avoid:** Per D-13, mirror `build.yml` lines 37-42 verbatim. The step must appear between `checkout` and `setup-python`.

### Pitfall 4: GATE-02 Regression — Modifying `build.yml`

**What goes wrong:** An implementer edits `build.yml` (e.g., adding a `workflow_dispatch` trigger to the stable workflow, or adding `fetch-depth: 0` to the stable checkout). Any such edit breaks GATE-02.

**How to avoid:** D-01 is absolute: zero modifications to `build.yml`. The GATE-02 verification command (`git diff build.yml`) is the automated gate.

### Pitfall 5: `pio test -e native` vs `pio test` — Wrong Scope

**What goes wrong:** Using `pio test` without `-e native` tries to run tests on ALL environments including AVR board environments (`uno`, `leonardo`). Board environments require a physical device connected via USB; the GitHub Actions runner has no such device. The test step hangs or fails with "no device found."

**How to avoid:** Always use `pio test -e native` in CI. The `-e native` flag restricts test execution to the host-side Unity suite.

### Pitfall 6: `paths-ignore` Drift Between `build.yml` and `beta-build.yml`

**What goes wrong:** Someone edits `build.yml`'s `paths-ignore` list (e.g., adds a new ignore pattern) but forgets to update `beta-build.yml`. The two workflows then have different trigger conditions: some file changes trigger `build.yml` but not `beta-build.yml` (or vice versa).

**Why it matters:** D-04 requires byte-matching. A drift means a doc-only push to `beta` could spuriously trigger a beta release if `beta-build.yml`'s list is more permissive than `build.yml`'s.

**How to avoid:** Phase 17 documents that `beta-build.yml`'s `paths-ignore` is a byte-match of `build.yml`'s list. Any future edits to `build.yml`'s `paths-ignore` should be reflected in `beta-build.yml`.

---

## Runtime State Inventory

Phase 17 is a greenfield addition (new YAML file only). No existing state is renamed or migrated.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | None | None |
| Live service config | None | None |
| OS-registered state | None | None |
| Secrets/env vars | `PERSONAL_ACCESS_TOKEN` already configured in `firestarter` repo for the commented-out block in `build.yml` (line 108) — reused by `beta-build.yml` with no changes | None |
| Build artifacts | None in Phase 17 scope | None |

---

## Environment Availability

Phase 17 is a YAML file creation — no new CLIs or external services beyond what the existing `build.yml` already uses.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `gh` CLI | LOCKSTEP-PROCEDURE Step 5 (operator) | ✓ (on operator machine) | Any modern | GitHub web UI |
| GitHub Actions runners | `beta-build.yml` | ✓ | `ubuntu-latest` | — |
| `secrets.PERSONAL_ACCESS_TOKEN` | Release step (D-17) | ✓ (already configured for `build.yml` line 108 commented reference) | — | — |
| PlatformIO Core | `pio run`, `pio test -e native` | Installed by `pip install --upgrade platformio` step | Latest stable | — |

**Missing dependencies with no fallback:** None.

---

## Validation Architecture

`workflow.nyquist_validation` not present in `.planning/config.json` → treated as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (installed via `pip install pytest` in beta-build.yml; no version pin needed) |
| Config file | None — `pytest tests/ -v` uses implicit discovery |
| Quick run command | `cd /workspaces/firestarter && pytest tests/ -v` |
| Full suite command | `cd /workspaces/firestarter && pytest tests/ -v` (same — one test directory) |

### Phase Requirements → Test Map

Phase 17 deliverable is a single YAML file — no new Python code. Tests are assertions against the workflow file content and git diff state.

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REL-02 | `beta-build.yml` exists with correct trigger blocks | smoke (grep) | `grep -q 'prerelease: true' firestarter/.github/workflows/beta-build.yml` | ❌ Wave 0 |
| REL-02 | `beta-build.yml` contains `make_latest: false` | smoke | `grep -q 'make_latest: false' firestarter/.github/workflows/beta-build.yml` | ❌ Wave 0 |
| REL-02 | `beta-build.yml` contains `fetch-depth: 0` | smoke | `grep -q 'fetch-depth: 0' firestarter/.github/workflows/beta-build.yml` | ❌ Wave 0 |
| REL-02 | `beta-build.yml` contains `workflow_dispatch` with `beta_version` input | smoke | `grep -q 'beta_version' firestarter/.github/workflows/beta-build.yml` | ❌ Wave 0 |
| REL-02 | `beta-build.yml` contains `pio test -e native` step | smoke | `grep -q 'pio test -e native' firestarter/.github/workflows/beta-build.yml` | ❌ Wave 0 |
| REL-02 | `beta-build.yml` contains `pio run` step | smoke | `grep -q 'pio run' firestarter/.github/workflows/beta-build.yml` | ❌ Wave 0 |
| REL-02 | `beta-build.yml` contains hex artifact glob | smoke | `grep -q 'firestarter_\*.hex' firestarter/.github/workflows/beta-build.yml` | ❌ Wave 0 |
| GATE-02 | `build.yml` byte-identical after Phase 17 commit | git diff | `git -C firestarter diff HEAD~1 -- .github/workflows/build.yml` (must be empty) | n/a — git check |

### Sampling Rate

- **Per task commit:** grep assertions on `beta-build.yml` content (instant; no network)
- **Phase gate:** Git diff assertion on `build.yml` + existing `pytest tests/ -v` green + grep assertions on all required fields

### Wave 0 Gaps

- [ ] `firestarter/.github/workflows/beta-build.yml` — the only deliverable; does not exist yet

*(Existing `firestarter/tests/test_update_version.py` from Phase 15 covers the script; no new test files needed. `pio test -e native` runs existing Unity tests unchanged.)*

---

## Security Domain

`security_enforcement` not explicitly set to `false` in config.json → included.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | N/A — workflow runs in GitHub Actions with pre-configured secrets |
| V3 Session Management | No | N/A |
| V4 Access Control | Yes (limited) | `permissions: contents: write` scoped at job level; `PERSONAL_ACCESS_TOKEN` already used in `build.yml` (commented) — no new secret exposure |
| V5 Input Validation | Yes | `BETA_VERSION` env var validated by Phase 15 regex before any file write; invalid input raises `ValueError` and halts script |
| V6 Cryptography | No | N/A |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed `BETA_VERSION` input corrupting `include/version.h` | Tampering | Phase 15 `BETA_VERSION_RE.match()` validation before `update_version()` is called; script exits on invalid input |
| Unauthorized beta release via `workflow_dispatch` | Elevation of Privilege | GitHub Actions `workflow_dispatch` restricted to repository collaborators with write access |
| Infinite loop DoS via auto-commit re-trigger | Denial of Service | Default GITHUB_TOKEN checkout (no PAT) prevents re-trigger — identical to Phase 16 Finding 4 |
| GitHub Release with hex artifacts from wrong commit | Tampering | `pio run` step builds from the post-version-bump commit (auto-commit pushes the version file change before `pio run`; runner workspace reflects the new HEAD after auto-commit re-pulls) |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `fetch-depth: 0` does not interfere with `actions/cache@v4` restore | Finding 8 | If wrong: cache restore simply fails silently (cache miss); workflow continues without cache. No functional failure — only slower runs. |
| A2 | `pio run` automatically skips `[env:native]` (platform=native) and builds only `[env:uno]` and `[env:leonardo]` | Finding 1 | If wrong: `pio run` might attempt to build a native binary for the native env; this would succeed but produce no `.hex` file. The glob `.pio/build/**/firestarter_*.hex` would still match only the real board hexes since native produces an ELF, not a hex. Minimal risk. |
| A3 | `secrets.PERSONAL_ACCESS_TOKEN` is already configured in the `firestarter` repository (not just `firestarter_app`) | Environment Availability | If wrong: the Release step fails with "secret not found" error. Mitigation: Phase 17 implementer must confirm the secret exists in the firmware sub-repo's settings before executing. |

---

## Open Questions (RESOLVED)

1. **Does `softprops/action-gh-release@v2` accept the `**` glob in `files:`?**
   - RESOLVED: Yes — confirmed by build.yml line 105 using `.pio/build/**/firestarter_*.hex` in the production stable release pipeline today. The glob is not a Phase 17 hypothesis; it is a verified production pattern. [VERIFIED: build.yml read directly]

2. **Does `pio run` build ALL board environments (uno + leonardo) without `-e` flag?**
   - RESOLVED: Yes — PlatformIO's default behavior with `pio run` (no `-e` flag) is to build all non-test environments defined in `platformio.ini`. The `[env:native]` environment has `platform = native` and does not have `framework = arduino`; PlatformIO builds it as a host binary (not a firmware hex). Both `[env:uno]` and `[env:leonardo]` produce `.hex` files via `name_firmware.py`. [VERIFIED: platformio.ini read directly; CLAUDE.md for firmware sub-repo]

3. **Does `beta-build.yml` need a `publish.yml` analogue?**
   - RESOLVED: No — the firmware has no PyPI analogue. The GitHub Release (`prerelease: true`) IS the artifact delivery mechanism. Phase 18's downloader consumes the `.hex` assets directly from the GH Release via the GitHub API. No secondary workflow is triggered.

4. **Is `PERSONAL_ACCESS_TOKEN` already configured in the firmware sub-repo?**
   - PARTIALLY RESOLVED: `build.yml` line 108 has it commented out (`# token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}`), which implies it was set up at some point but is not currently active in the stable build. The secret must be confirmed to exist in the `firestarter` repository's secrets settings before Phase 17 executes. Flagged as assumption A3.

---

## Sources

### Primary (HIGH confidence)
- `/workspaces/firestarter/.github/workflows/build.yml` — structural template; all step patterns, cache config, job/permission settings verified by direct read
- `/workspaces/firestarter/platformio.ini` — board environments enumerated; native env confirmed; `extra_scripts = pre:name_firmware.py` verified
- `/workspaces/firestarter/name_firmware.py` — hex naming logic verified: `PROGNAME=firestarter_{board}` → `firestarter_uno.hex`, `firestarter_leonardo.hex`
- `/workspaces/firestarter/.github/scripts/update_version.py` — Phase 15 deliverable; `BETA_VERSION` + `GITHUB_REF` detection verified
- `/workspaces/firestarter/tests/test_update_version.py` — Phase 15 test suite; `pytest tests/ -v` target confirmed
- `/workspaces/firestarter_app/.github/workflows/beta-release.yml` — Phase 16 deliverable; trigger pattern, env passthrough, auto-commit pattern verified
- `/workspaces/.planning/phases/17-firmware-beta-release-pipeline/17-CONTEXT.md` — all 23 locked decisions
- `/workspaces/.planning/phases/16-app-beta-release-pipeline/16-RESEARCH.md` — inherited findings (GitHub API semantics, workflow_dispatch shape, anti-loop, prerelease event, pitfalls 1-8)
- `/workspaces/.planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md` — Phase 16/17 implementation requirements; workflow YAML constraints

### Secondary (MEDIUM confidence)
- [softprops/action-gh-release v2 README](https://github.com/softprops/action-gh-release/tree/v2) — `token:` vs `env: GITHUB_TOKEN:` parameter equivalence; `files:` glob behavior (glob acceptance confirmed by build.yml production use)

---

## Metadata

**Confidence breakdown:**
- Standard stack (action versions): HIGH — verified from build.yml directly
- PlatformIO board enumeration and hex naming: HIGH — verified from platformio.ini + name_firmware.py
- `pio test -e native` invocation: HIGH — verified from build.yml + platformio.ini
- `actions/cache@v4` key/path: HIGH — verified from build.yml lines 37-42
- `softprops` `**` glob: HIGH — verified from build.yml production use (line 105)
- Architecture patterns: HIGH — derived from build.yml template + Phase 16 inheritance
- Pitfalls: HIGH — derived from Phase 16 verified findings + build.yml direct inspection

**Research date:** 2026-05-20
**Valid until:** 2026-06-20 (GitHub Actions action major versions and PlatformIO build behavior are stable; action versions pinned in build.yml)

---

## RESEARCH COMPLETE

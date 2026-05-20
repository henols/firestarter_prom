# Phase 17: Firmware Beta Release Pipeline - Context

**Gathered:** 2026-05-20
**Status:** Ready for planning
**Discussion mode:** `--auto --chain`

<domain>
## Phase Boundary

`firestarter/` ships a new GitHub Actions workflow that handles the publisher side of the beta channel for the firmware sub-repo. Near-mirror of Phase 16's `beta-release.yml` for the app, with firmware-specific gates (PlatformIO build + native Unity tests) and artifacts (`firestarter_*.hex` files instead of wheel/sdist; no PyPI publish — just GitHub Pre-release).

A push to the `beta` branch (or `workflow_dispatch` with optional `beta_version` input) triggers: catalog validity check, codegen drift gate, PlatformIO Core install, native Unity tests, pytest for the `update_version.py` script, Phase 15 version bump with beta context, auto-commit back to `beta`, PlatformIO build of all configured boards, GitHub Release with `prerelease: true` + `make_latest: false` carrying `.pio/build/**/firestarter_*.hex` artifacts.

**In scope (Phase 17):**
- New workflow file: `firestarter/.github/workflows/beta-build.yml`. Self-contained (matches build.yml's self-contained pattern — firmware sub-repo has only ONE workflow file today; Phase 17 adds the second).
- Inline gates: catalog validity, codegen drift on `include/messages.h`, PlatformIO Core install, `pio test -e native`, `pip install pytest`, `pytest tests/`, then version bump → auto-commit → `pio run` → Release. Sequence mirrors `build.yml` lines 60-107.
- `update_version.py` invocation inherits Phase 15's beta-context behavior via `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}` + auto `GITHUB_REF=refs/heads/beta`.
- `softprops/action-gh-release@v2` with `prerelease: true`, `make_latest: false`, `files: .pio/build/**/firestarter_*.hex`, `tag_name: ${{ steps.version.outputs.version }}`.
- GATE-02 verification: `git -C firestarter diff` over `build.yml` shows zero changes after Phase 17 lands.

**Out of scope (Phase 17):**
- App beta pipeline (Phase 16 — shipped).
- Branch protection rules on `beta` (Future Requirements).
- Auto-promotion beta → stable (deferred to v1.5+).
- Modifying `build.yml` (GATE-02 non-regress).
- New unit tests (the firmware sub-repo's `tests/test_update_version.py` from Phase 15 covers the script; Phase 17 just wires the build.yml-equivalent for beta cuts).

</domain>

<decisions>
## Implementation Decisions

### A. Workflow File Shape

- **D-01:** Create NEW workflow file `firestarter/.github/workflows/beta-build.yml`. Do NOT modify `build.yml`. GATE-02 verified by `git diff build.yml` returning empty after the Phase 17 PR.
- **D-02:** Naming: `beta-build.yml` (mirrors `beta-release.yml` naming pattern from the app side; pairs with existing `build.yml`). Job name `build` (mirrors `build.yml`); workflow display name `Firestarter beta pre-release build`.

### B. Triggers

- **D-03:** Triggers:
  ```yaml
  on:
    push:
      branches: [beta]
      paths-ignore: [byte-match build.yml's paths-ignore]
    workflow_dispatch:
      inputs:
        beta_version:
          description: 'Explicit PEP 440 pre-release version (e.g. 3.1.0b1). Leave blank for auto-increment via git-tag scan.'
          required: false
          type: string
  ```
- **D-04:** `paths-ignore` byte-matches `build.yml`'s list (`**.md`, `**.sh`, `.gitignore`, `docs/**`, `documents/**`, `images/**`, `.vscode/**`, `.editorconfig/**`). Note: firmware's list differs from app's (extra `documents/**` and `.editorconfig/**`).
- **D-05:** `workflow_dispatch` is the canonical lockstep cut mechanism per Phase 15 D-01 / Phase 16 D-05. Release engineer runs `gh workflow run beta-build.yml --ref beta -f beta_version=3.1.0b1` from `firestarter/` matching the app-side invocation.
- **D-06:** No `pull_request` trigger (unlike `build.yml` which fires on PR to main). Rationale: beta cuts are operator-initiated; PR-to-beta validation isn't needed because cuts happen via push or dispatch, not via merged PRs.

### C. CI Gate Placement

- **D-07:** Gates run INLINE BEFORE version bump (mirror `build.yml`'s post-WR-05 ordering). Sequence:
  1. `actions/checkout@v4` with `fetch-depth: 0`
  2. `actions/cache@v4` (pip + ~/.platformio caches; mirror build.yml lines 37-42)
  3. `actions/setup-python@v5` with `python-version: '3.11'` (do NOT replicate build.yml's vestigial @v4 step — see D-22)
  4. Catalog validity check: `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check`
  5. Codegen drift gate (messages.h): regenerate + `git diff --exit-code include/messages.h`
  6. Install PlatformIO Core: `pip install --upgrade platformio`
  7. Run native unit tests: `pio test -e native`
  8. Install pytest: `pip install pytest`
  9. Run update_version.py tests: `pytest tests/ -v`
- **D-08:** After gates pass:
  10. Generate release version: `.github/scripts/update_version.py` with `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}`, `id: version`
  11. `stefanzweifel/git-auto-commit-action@v5` with NO `with:` block (mirror build.yml line 93; no token override → no re-trigger loop per Phase 16 D-16 + Phase 16 RESEARCH finding #1)
  12. `Build PlatformIO Project`: `pio run`
  13. `Release`: `softprops/action-gh-release@v2` with `files: .pio/build/**/firestarter_*.hex`, `tag_name: ${{ steps.version.outputs.version }}`, `prerelease: true`, `make_latest: false`, `token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}`

### D. Artifact Selection

- **D-09:** Artifacts: `files: .pio/build/**/firestarter_*.hex` — byte-matches `build.yml` line 105. Same set of boards (Uno, Leonardo, plus any other configured). Per Phase 18 INST-02 acceptance, the asset name pattern `firestarter_{board}.hex` is the publisher-consumer contract; Phase 17 honors it.

### E. `BETA_VERSION` Sourcing (mirror Phase 16 D-12..D-14)

- **D-10:** `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}` on the version-bump step. Empty string on push trigger → Phase 15 D-08 auto-increment fallback (git-tag scan).
- **D-11:** `fetch-depth: 0` REQUIRED on checkout for the tag-scan to see all tags (mirror Phase 16 D-14).

### F. PR Trigger

- **D-12:** NO `pull_request:` trigger in beta-build.yml. Differs from build.yml (which fires on PR to main). Justification: beta-cut operations are intentional one-shots; PR validation against beta would force every operator commit to be PR'd (vs. push-driven workflow). Existing build.yml's `pull_request: branches: [main]` continues to validate main-bound PRs.

### G. Caching

- **D-13:** Mirror `build.yml`'s `actions/cache@v4` step verbatim (pip + ~/.platformio caches, key `${{ runner.os }}-pio`). Speeds up beta runs (PlatformIO core install is the heaviest step).

### H. Vestigial setup-python step (cleaner not-byte-identical)

- **D-14:** `beta-build.yml` uses ONLY the `actions/setup-python@v5` step with `python-version: '3.11'`. Do NOT replicate `build.yml`'s vestigial `actions/setup-python@v4` step (line 44 — no version pin; immediately shadowed by the explicit @v5 step at line 56; flagged as IN-02 in Phase 18 code review).
- **D-15:** Rationale: Phase 17 is a new file; including a known-dead step would propagate technical debt. The choice to deviate here from "byte-similarity" is intentional and documented. GATE-02 verification still passes because GATE-02 asserts BUILD.YML byte-identity, not "beta-build.yml resembles build.yml verbatim."

### I. fetch-depth: 0

- **D-16:** `actions/checkout@v4` step uses `with: fetch-depth: 0` — required by Phase 15's git-tag-scan fallback (D-08 + Phase 15 RESEARCH Pitfall #5).

### J. Release Flags

- **D-17:** `softprops/action-gh-release@v2` step: `prerelease: true`, `make_latest: false`, `files: .pio/build/**/firestarter_*.hex`, `tag_name: ${{ steps.version.outputs.version }}`, `token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}`. Matches Phase 16 D-09 with firmware-specific `files:` glob.
- **D-18:** Permissions: `permissions: contents: write` at JOB level (mirror build.yml line 31-32 + Phase 16 D-18).

### K. GATE-02 Verification

- **D-19:** Phase 17 verification asserts:
  1. `git -C firestarter diff HEAD~N -- .github/workflows/build.yml` returns empty (build.yml byte-unchanged across the Phase 17 commit range).
  2. New `beta-build.yml` is the ONLY workflow file added (`git -C firestarter status` clean post-commit).
  3. Phase 18's `tests/test_update_version.py` still passes (regression guard — Phase 15-03 added pytest infrastructure; Phase 17 doesn't touch it).

### Claude's Discretion

- **D-20:** YAML quoting style — planner picks per project convention (2-space indent, single-quoted strings; consistent with build.yml).
- **D-21:** `concurrency` group — recommended NO (mirror Phase 16 D-25).
- **D-22:** Whether to omit build.yml's commented-out `tagging_message` and `env: GITHUB_TOKEN` from the auto-commit step (build.yml lines 94-97). Recommended: omit (no need to carry commented-out config into a new file).
- **D-23:** Whether to add a `Set up Python 3.11 for codegen` name string (matches build.yml line 55) or simplify. Recommended: use the same step name for consistency.

</decisions>

<canonical_refs>
## Canonical References

### Milestone planning artifacts
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md` §REL (REL-02) + §GATE (GATE-02)
- `.planning/ROADMAP.md` §"Phase 17: Firmware Beta Release Pipeline"
- `.planning/STATE.md` §"v1.4 Decisions"

### Phase 15 + 16 deliverables (load-bearing)
- `firestarter/.github/scripts/update_version.py` — extended by Phase 15 (Plan 15-03). Phase 17's workflow invokes unchanged with `GITHUB_REF=refs/heads/beta` + optional `BETA_VERSION` env.
- `firestarter/tests/test_update_version.py` — pytest suite added by Plan 15-03. Phase 17's workflow runs these.
- `firestarter_app/.github/workflows/beta-release.yml` — Phase 16 deliverable. Phase 17 is the firmware analogue; same structural skeleton, firmware-specific gates and artifacts.
- `.planning/phases/16-app-beta-release-pipeline/16-CONTEXT.md` — D-01..D-27 decisions all carry across to Phase 17 with firmware-specific variations noted above.

### Existing firmware workflow (read-only; must remain byte-identical per GATE-02)
- `firestarter/.github/workflows/build.yml` — structural template AND the file that must NOT change. Phase 17 MUST NOT modify it.

### Files to create
- `firestarter/.github/workflows/beta-build.yml` — THE single deliverable.

### External specs
- Same set as Phase 16 (workflow_dispatch inputs, softprops/action-gh-release v2, stefanzweifel/git-auto-commit-action v5, GitHub `release: published` event).
- **Note:** firmware sub-repo has NO equivalent of `publish.yml` (no PyPI step). The GitHub Pre-release IS the final artifact destination — operators download `.hex` files directly via GitHub Releases (or via Phase 18's downloader).

### Phase 18 / 19 / 20 handoff
- Phase 18 (Beta-Aware Firmware Downloader) already shipped — its `firestarter fw -i --pre` consumes the prereleases Phase 17 produces. Asset name pattern: `firestarter_{board}.hex`.
- Phase 19 will document `gh workflow run beta-build.yml --ref beta -f beta_version=X.Y.ZbN` in the release-procedures doc.
- Phase 20 E2E-01 (c)+(d) verify: prerelease GH Release marked Pre-release, expected `.hex` artifacts per board, lockstep `X.Y.ZbN` match with app side.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`firestarter/.github/workflows/build.yml`** — Structural template. The new `beta-build.yml` is a near-clone with: trigger branch flip (`main` → `beta`), addition of `workflow_dispatch` block with `beta_version` input, `prerelease: true` + `make_latest: false` on the Release step, omission of the vestigial setup-python@v4 step (D-14).
- **`firestarter_app/.github/workflows/beta-release.yml`** — Phase 16 deliverable; Phase 17 inherits its trigger pattern, env-passthrough pattern, and auto-commit pattern verbatim. Differences from beta-release.yml: PlatformIO build step + native Unity tests + `.hex` artifact glob + no PyPI delegation.
- **`firestarter/.github/scripts/update_version.py`** — Phase 15 extended; Phase 17 invokes unchanged. `BETA_VERSION` env + `GITHUB_REF` auto-detect.
- **`firestarter/tests/test_update_version.py`** — Phase 15 wave 0 + Plan 15-03 implementation; runs in beta-build.yml as a gate.

### Established Patterns

- **Self-contained workflow** — build.yml runs gates + release inline; beta-build.yml mirrors.
- **Codegen drift gate** — `python3 tools/catalog/codegen.py ... --target include/messages.h --language cpp` then `git diff --exit-code include/messages.h`. Phase 6 WR-05 established this; Phase 17 mirrors.
- **Native Unity test gate** — `pio test -e native` (host-side, no AVR board needed). Phase 6 WR-01.
- **`pio run` for the actual firmware build** — produces `.pio/build/{board}/firestarter_{board}.hex`.
- **`softprops/action-gh-release@v2`** for the Release step.
- **`stefanzweifel/git-auto-commit-action@v5`** with NO token override (anti-loop pattern from Phase 16 RESEARCH).
- **`secrets.PERSONAL_ACCESS_TOKEN`** for the gh-release token.

### Integration Points

- **`beta-build.yml` and `build.yml` are siblings** — disjoint branch triggers (main vs beta); no interference.
- **No `publish.yml` equivalent** on the firmware side. Operators (and Phase 18's downloader) consume `.hex` files directly from the GitHub Release page.
- **`fetch-depth: 0`** on checkout enables Phase 15's tag-scan fallback.

</code_context>

<specifics>
## Specific Ideas

- **build.yml's vestigial setup-python@v4 step:** flagged in Phase 18 code review IN-02. The new beta-build.yml uses ONLY the @v5 step with python-version pin. Phase 17 deliberately deviates here from pure byte-similarity for cleanliness; the deviation is documented in D-14.
- **paths-ignore differs between firmware and app:** firmware has `documents/**` and `.editorconfig/**`; app has `images/**`, `.github/**`, `tools/**`. Each beta-* workflow byte-matches its OWN main-branch sibling.
- **Asset name pattern `firestarter_{board}.hex`** is the publisher-consumer contract. Phase 18's downloader greps for this; Phase 17 MUST preserve it (build.yml line 105 already establishes; Phase 17 mirrors).

</specifics>

<deferred>
## Deferred Ideas

- Reusable workflow extraction (gates shared between build.yml + beta-build.yml) — v1.5+.
- `concurrency` group — same as Phase 16 D-25.
- Branch protection on `beta` — Future Requirements.
- Auto-promotion beta → stable — deferred.
- Cleanup of build.yml's vestigial setup-python@v4 step — separate cleanup task; not in v1.4 scope (GATE-02 requires byte-identity).
- PR validation on beta branch — see D-06.

</deferred>

---

*Phase: 17-firmware-beta-release-pipeline*
*Context gathered: 2026-05-20*
*Discussion mode: --auto --chain*

# Roadmap: Firestarter — Protocol-Aware Programming Architecture

## Milestones

- ✅ **v1.0 Protocol-Aware Programming Architecture** — Phases 1-13 (shipped 2026-05-11)
- ⏸ **v1.1 Safety Closure & Hardware Validation** — Phases 1-3 done, Phase 4 hardware-validation parked (FM1608 byte-0 bug); Phase 5 milestone-close deferred. Original artifacts preserved at `.planning/milestones/v1.1-paused/`.
- ✅ **v1.2 Message-ID Logging Rework** — Phases 6-9 (shipped 2026-05-19); Phase 10 closed by `/gsd-complete-milestone` (DOC-02)
- ⏸ **v1.3 CMOS EPROM Family Hardware Validation** — Phases 11-14 (PAUSED 2026-05-20, hardware-gated). Phase 11 shipped + Phase 12 Wave 0 scaffold committed; Plans 12-01/02/03 + Phases 13/14 await operator bench hardware.
- 🚧 **v1.4 Beta & Pre-release Deployment Pipeline** — Phases 15-20 (active, started 2026-05-20; Phase 18 inserted 2026-05-20 — Beta-Aware Firmware Downloader). Add parallel beta channel for both sub-repos without disrupting the stable main → release pipeline. App ships PyPI pre-release versions (`pip install --pre`); firmware ships GitHub Pre-release artifacts (`prerelease: true`, `make_latest: false`). App and firmware lockstep on matching version numbers. Beta-installed app can list and install any firmware (stable or pre-release); stable-installed app's `firestarter --install` defaults are byte-identical to today.

## v1.4 — Beta & Pre-release Deployment Pipeline (Active)

**Milestone goal:** Add a parallel beta / pre-release deployment channel for both sub-repos (`firestarter_app/` and `firestarter/`) without disrupting the existing main → stable pipelines. Branch-driven trigger: push to `beta` produces opt-in pre-release artifacts. App publishes PEP 440 pre-release versions to PyPI (installable via `pip install --pre firestarter`); firmware publishes GitHub Pre-releases (`prerelease: true`, `make_latest: false`) with the same `.hex` artifacts as stable. App and firmware ship locked-step (matching version numbers as a coordinated pair). Consumer-side: stable-installed app continues to download stable firmware (no regression); beta-installed app can install latest beta firmware via `--pre`, pin an exact version via `--firmware-version X.Y.ZbN`, or list available firmwares via `firestarter firmware list`.

**Granularity:** Standard (6 phases — natural decomposition of CI/CD plumbing + consumer-side enablement + docs + acceptance gate). Foundation phase resolves the load-bearing versioning question, app and firmware beta pipelines land sequentially, then consumer-side downloader, then docs, then a real beta cut as the milestone acceptance gate.
**Phase numbering:** continues from v1.3 last phase (14) — starts at **Phase 15**. (v1.3 paused, not completed; v1.3 phase directories at `.planning/phases/11-*/` and `.planning/phases/12-*/` preserved.) Phase 18 was inserted 2026-05-20 after Phase 15 shipped; old Phase 18 (Documentation) renumbered to 19, old Phase 19 (E2E + Close) renumbered to 20.

### Structural Notes

- **CI/CD plumbing + docs + minimum consumer-side enablement.** Most workflow / script / version-file edits land inside the two submodules (`firestarter/` and `firestarter_app/`); Phase 18 (Beta-Aware Firmware Downloader) adds CLI flags + a refactored downloader module to `firestarter_app/firestarter/firmware.py` + `main.py`. Zero firmware behavior changes, zero hardware bench testing. Meta-repo tracks only `.planning/` and `.claude/`.
- **Scope amendment 2026-05-20.** The original "Zero new user-facing CLI features in the app" rule is relaxed for one narrow case (Phase 18 INST-01..04): `--pre`, `--firmware-version`, `firmware list` flags + a defensive PEP 440 fix in the existing version comparator. Without them the beta channel publishes firmware nobody can install via the CLI — half a feature. No other CLI changes follow.
- **Three decisions are LOCKED at milestone start** (see `.planning/STATE.md` v1.4 Decisions): (1) branch-driven beta — push to `beta` triggers the pre-release pipeline in each sub-repo; (2) app uses PEP 440 pre-release identifiers (`X.Y.ZbN`, `X.Y.ZrcN`) on the SAME PyPI index — TestPyPI deferred; (3) firmware + app ship lockstep on matching version strings. Phase 15 finalized the locked-step coordination MECHANISM (manually-paired beta-branch push with explicit `BETA_VERSION` input — see `15-LOCKSTEP-PROCEDURE.md`).
- **Stable pipeline is sacred.** GATE-01 and GATE-02 are explicit non-regress requirements. After v1.4 lands, pushing to `firestarter_app/main` must produce a byte-identical (modulo version-number bump) GitHub Release + PyPI publish as today; pushing to `firestarter/main` must produce the same `.hex` artifacts and catalog/codegen/Unity gates as today. `firestarter --install` (no new flags) on a stable-installed app must continue hitting `/releases/latest` and download stable firmware exactly as today (INST-01). Beta plumbing + consumer-side flags are purely additive — new workflow files, new branch triggers, new CLI flags — never modifications to stable trigger behavior or stable-default download path.
- **Phase 15 is load-bearing.** Shipped 2026-05-20. REL-01 (app beta release) and REL-02 (firmware beta release) cannot meaningfully run without a defined pre-release version emission scheme + locked-step coordination procedure. Phase 15 resolved the open mechanism question (manually-paired BETA_VERSION input) and shipped VER-01/VER-02 version-bump script extensions; Phases 16 and 17 assemble the workflow plumbing on top.
- **Phase 16 before Phase 17 (sequential, not parallel).** App-side beta lands first because: (a) the PyPI pre-release version path is more constrained (PEP 440 strict, install via `--pre`, single-index gating) and shakes out the version-emission scheme; (b) firmware beta is a near-mirror with GitHub Release `prerelease: true` instead of PyPI `--pre`, so app lessons-learned feed firmware design cleanly; (c) tight feedback loop in a CI/CD setup is more valuable than parallel-track throughput when both phases ultimately depend on Phase 15 output.
- **Phase 18 depends on Phase 17.** The Beta-Aware Firmware Downloader is the consumer side of Phase 17's publisher. It can be designed earlier, but it can only be E2E-tested once real beta firmware exists in GitHub Releases. Phase 18 ships the `--pre` / `--firmware-version` / `firmware list` flags + the PEP 440 comparator fix; Phase 19 documents them; Phase 20's E2E-01 proves the publish→install loop end-to-end.
- **Phase 20 is the acceptance gate.** E2E-01 + MS-01 together. No v1.4 close without a green E2E-01 — a real beta cut in both repos using the documented Phase 19 procedure, with PyPI `pip install --pre firestarter==X.Y.ZbN`, firmware GitHub Pre-release pages showing the expected artifacts, matching version strings per VER-03, AND `firestarter --install --pre` successfully fetching the matching `X.Y.ZbN` firmware via the Phase 18 downloader. Also: a stable-installed app's `firestarter --install` (no flags) must still download stable firmware on a SEPARATE fresh install — INST-01 non-regression.
- **v1.3 carry.** v1.3 is paused, not closed. v1.4 does NOT block on v1.3 closure. v1.3 BENCH-01..06 / PROTO-01/02 / DOC-01/02 requirements stay archived at `.planning/milestones/v1.3-paused/REQUIREMENTS-at-pause.md`; resume command on the v1.3 paused list when bench hardware is available.

### Phases

- [x] **Phase 15: Versioning & Locked-Step Coordination (Foundation)** — Resolve the lockstep coordination mechanism (manually-paired beta-branch push with `BETA_VERSION` input); extend both `update_version.py` scripts to emit PEP 440 / matching pre-release identifiers on `beta`-branch builds; document the coordination procedure as input to Phase 19. (completed 2026-05-20)
- [x] **Phase 16: App Beta Release Pipeline** — Add the `firestarter_app/` beta workflow (push to `beta` → run CI → bump pre-release version per Phase 15 → GitHub Release with `prerelease: true`, `make_latest: false` → publish wheel/sdist to PyPI). Validate stable pipeline (GATE-01) still produces unchanged outputs from a `main` push. (completed 2026-05-20)
- [x] **Phase 17: Firmware Beta Release Pipeline** — Add the `firestarter/` beta workflow (push to `beta` → run catalog validity + codegen drift gate + native Unity tests + PlatformIO build → bump pre-release version per Phase 15 → GitHub Release with `prerelease: true`, `make_latest: false`, same `firestarter_*.hex` artifacts per board). Validate stable pipeline (GATE-02) still produces unchanged outputs from a `main` push. (completed 2026-05-20)
- [x] **Phase 18: Beta-Aware Firmware Downloader** — Extend `firestarter_app/` so `firestarter --install` (no flags) preserves byte-identical stable-only behavior, `--pre` fetches latest pre-release firmware (mirrors `pip install --pre`), `--firmware-version X.Y.Z[bN]` pins an exact tag via `/releases/tags/{tag}`, and a new `firestarter firmware list [--all|--pre|--stable]` enumerates available releases. Refactor `_compare_versions` to use `packaging.version.Version` so PEP 440 pre-release strings no longer crash. Adds pytest coverage for each path. (completed 2026-05-20)
- [ ] **Phase 19: Documentation** — Update `firestarter_app/README.md` (install via `pip install --pre`; install firmware via `firestarter --install --pre`, `--firmware-version X.Y.ZbN`, and `firmware list`; beta stability guarantee; how to report beta issues); update `firestarter/README.md` (find pre-release `.hex` on GitHub Releases; opt-in install via the new app flags; issue reporting); publish `.planning/v1.4-RELEASE-PROCEDURES.md` (release-engineer workflow for cutting a beta in both repos via the Phase 15 lockstep mechanism, deferred promotion path).
- [ ] **Phase 20: End-to-End Smoke Test + Milestone Close** — Cut a real beta in both sub-repos following the Phase 19 documented procedure; verify all acceptance criteria (PyPI shows pre-release version, `pip install --pre` works cleanly, firmware GitHub Release marked pre-release, both version strings match per VER-03, `firestarter --install --pre` installs the matching firmware via the Phase 18 downloader, stable-installed app still downloads stable firmware via `--install` on a separate fresh install); update MILESTONES.md, archive v1.4 phase directories, refresh PROJECT.md active-milestone footer.

### Phase Details

#### Phase 15: Versioning & Locked-Step Coordination (Foundation)
**Goal:** Both sub-repos have a defined, scripted mechanism for emitting PEP 440 / matching pre-release version identifiers on `beta`-branch builds, AND a documented locked-step coordination procedure that guarantees a beta cut in one sub-repo can be paired with the same version string in the other. Without this foundation, REL-01 and REL-02 have no version-emission scheme to plug into.
**Depends on:** Nothing (foundation phase; resolves the open milestone planning question).
**Requirements:** VER-01, VER-02, VER-03
**Success Criteria** (what must be TRUE):
  1. `firestarter_app/.github/scripts/update_version.py` (or its replacement) recognises beta-branch context (env var, CLI flag, git-branch detection — the mechanism chosen during `/gsd-discuss-phase`) and emits PEP 440 pre-release identifiers (`X.Y.Zb1`, `X.Y.ZbN`, `X.Y.ZrcN`) instead of bumping the patch component. Stable-branch behaviour (patch auto-bump) is preserved verbatim — a `main`-context invocation produces byte-identical output to the pre-v1.4 script.
  2. `firestarter/.github/scripts/update_version.py` (or its replacement) recognises beta-branch context in the same way and emits matching pre-release identifiers (`X.Y.ZbN`) into `include/version.h`. Format is identical to the app's so lockstep comparison is a string-equality check. Stable-branch behaviour preserved verbatim — a `main`-context invocation produces byte-identical output to the pre-v1.4 script.
  3. The locked-step coordination mechanism is finalised (one of: shared `VERSION` file in the meta-repo committed by both sub-repos' release workflows; cross-repo workflow trigger via `repository_dispatch`; or manually-paired beta-branch push with a written checklist) and documented in a phase-local artifact that Phase 18 (`v1.4-RELEASE-PROCEDURES.md`) consumes verbatim. The procedure, when followed, produces matching `X.Y.ZbN` version strings in both repos' beta releases — verified by a dry-run or fixture-driven test.
  4. Both version-bump scripts have a unit-level test (pytest fixture, or PlatformIO native, or a `--dry-run` flag with golden-file diff) that exercises both the stable-branch path (asserts patch increment) and the beta-branch path (asserts `b1` / `bN` / `rcN` suffix on a chosen base version). Test runs in CI on PRs to either sub-repo before the v1.4 plumbing lands in mainline.
**Plans:** 4/4 plans complete
- [x] 15-01-PLAN.md — Wave 0 RED-gate scaffold: failing pytest tests + golden baselines in both sub-repos (creates firestarter/tests/ dir)
- [x] 15-02-PLAN.md — Wave 1 app-side: extend firestarter_app/.github/scripts/update_version.py (beta detection, dry-run, validation, GITHUB_OUTPUT guard) — VER-01 GREEN
- [x] 15-03-PLAN.md — Wave 1 firmware-side: extend firestarter/.github/scripts/update_version.py + add pytest CI step to build.yml — VER-02 GREEN, lockstep regex parity
- [x] 15-04-PLAN.md — Wave 2 lockstep deliverables: 15-LOCKSTEP-PROCEDURE.md + lockstep-dryrun-fixture.sh (cross-script byte-identity proof) — VER-03 GREEN

#### Phase 16: App Beta Release Pipeline
**Goal:** A push to `firestarter_app/beta` triggers a new (or extended) GitHub Actions workflow that runs the existing CI test suite, calls the Phase 15 version-bump script in beta mode, creates a GitHub Release with `prerelease: true` and `make_latest: false`, and publishes the resulting wheel/sdist to PyPI as a `X.Y.ZbN` pre-release installable via `pip install --pre firestarter`. The existing `main` → stable pipeline behaviour is preserved verbatim (GATE-01).
**Depends on:** Phase 15 (version-bump script's beta-branch mode is the workflow's version-emission step).
**Requirements:** REL-01, GATE-01
**Success Criteria** (what must be TRUE):
  1. A push to a `beta` branch in `firestarter_app/` triggers a GitHub Actions workflow that runs the existing CI suite (pytest), calls `update_version.py` in beta mode (per Phase 15), creates a GitHub Release tagged `X.Y.ZbN` with `prerelease: true` and `make_latest: false`, builds wheel + sdist via `python3 -m build`, and publishes to PyPI as a pre-release version. End-to-end run is observable in the GitHub Actions tab as a single workflow execution producing all listed artifacts.
  2. After the beta workflow lands, `pip install --pre firestarter` on a clean Python environment installs the most-recent `X.Y.ZbN` build successfully and imports cleanly. `pip install firestarter` (without `--pre`) still installs the stable version, NOT the beta — beta is opt-in via the `--pre` flag.
  3. **GATE-01 preserved.** After v1.4 lands, a push to `firestarter_app/main` still produces: (a) a GitHub Release with `make_latest: true` (no `b`/`rc` suffix in the tag), (b) a non-pre-release wheel + sdist published to PyPI, (c) `__version__` in `firestarter/__init__.py` auto-bumped to the next patch. The stable path runs no new mandatory CI checks beyond what the pre-v1.4 release.yml + publish.yml currently run.
  4. The beta workflow shares CI gates with the stable workflow where it makes sense (existing pytest suite, lint, etc.) but does NOT introduce new mandatory gates on either path. If the existing pytest suite fails on a `beta` push, the workflow halts before publishing — same fail-stop semantics as the stable path.
**Plans:** 1/1 plans complete
- [x] 16-01-PLAN.md — Create firestarter_app/.github/workflows/beta-release.yml (single-file deliverable: push: beta + workflow_dispatch triggers, inline CI gates, Phase 15 version bump, GH Pre-release, PyPI via existing publish.yml). REL-01 + GATE-01.

#### Phase 17: Firmware Beta Release Pipeline
**Goal:** A push to `firestarter/beta` triggers a new (or extended) GitHub Actions workflow that runs the existing build pipeline (catalog validity, codegen drift gate, native Unity tests, PlatformIO build), calls the Phase 15 version-bump script in beta mode (producing matching `X.Y.ZbN` `#define VERSION` in `include/version.h`), and creates a GitHub Release with `prerelease: true`, `make_latest: false`, and the same `firestarter_*.hex` artifacts per board (Uno + Leonardo, plus any other configured board) as the stable build. The existing `main` → stable pipeline behaviour is preserved verbatim (GATE-02).
**Depends on:** Phase 15 (version-bump script's beta-branch mode), Phase 16 (lessons-learned from app-side beta pipeline feed firmware design — branch trigger shape, version emission flow, release-action wiring).
**Requirements:** REL-02, GATE-02
**Success Criteria** (what must be TRUE):
  1. A push to a `beta` branch in `firestarter/` triggers a GitHub Actions workflow that runs the existing build pipeline (catalog validity check via `tools/catalog/codegen.py --check`, codegen drift gate via the git-diff check on `include/messages.h`, native Unity tests via `pio test -e native`, PlatformIO build via `pio run`), calls `update_version.py` in beta mode (per Phase 15), and creates a GitHub Release tagged `X.Y.ZbN` with `prerelease: true`, `make_latest: false`, and the full set of `.pio/build/**/firestarter_*.hex` artifacts attached (same set per board as the stable build).
  2. **GATE-02 preserved.** After v1.4 lands, a push to `firestarter/main` still produces: (a) a GitHub Release with `make_latest: true` (no `b`/`rc` suffix in the tag), (b) the same set of `firestarter_*.hex` artifacts per board as today, (c) `VERSION` in `include/version.h` auto-bumped to the next patch. The existing catalog-validity, codegen-drift, and Unity-test gates run unchanged on the stable path. No new mandatory CI checks added beyond what the pre-v1.4 build.yml currently runs.
  3. The beta build produces the same per-board `.hex` artifact set as the stable build (no missing boards, no extra boards) — verified by file-name listing on the GitHub Release page and an artifact-count assertion in the workflow.
  4. The firmware beta version string (`X.Y.ZbN` in `include/version.h`) matches the app beta version string from Phase 16 when both repos are cut as a coordinated pair via the Phase 15 lockstep procedure. Verified by a string-equality check in Phase 19's E2E smoke test.
**Plans:** 1/1 plans complete
- [x] 17-01-PLAN.md — Create firestarter/.github/workflows/beta-build.yml (single-file deliverable: push: beta + workflow_dispatch triggers, inline catalog/codegen/native-Unity/pytest gates, Phase 15 version bump, auto-commit, pio run, GH Pre-release with firestarter_*.hex artifacts). REL-02 + GATE-02; 23 D-XX decisions; build.yml byte-identity preserved; vestigial setup-python@v4 step omitted per D-14.

#### Phase 18: Beta-Aware Firmware Downloader
**Goal:** The `firestarter_app/` CLI grows the minimum consumer-side surface needed to actually use the beta firmware channel. `firestarter --install` (no flags) continues to hit `/releases/latest` and download stable firmware byte-identically to today (INST-01 non-regression). New `firestarter --install --pre` fetches the newest pre-release firmware for the configured board (mirrors `pip install --pre`). New `firestarter --install --firmware-version X.Y.Z[bN|rcN]` pins an exact tag via `/releases/tags/{tag}`. New `firestarter firmware list [--all|--pre|--stable]` enumerates available releases for the configured board. The internal `_compare_versions` helper is refactored to use `packaging.version.Version` so PEP 440 pre-release strings (`3.1.0b1`, `3.1.0rc2`) no longer crash with `ValueError` — today's stable-only path is protected only by GitHub's `/releases/latest` filter; the new code paths bypass that protection and need a real comparator.
**Depends on:** Phase 17 (real beta firmware must exist on GitHub Releases for `--pre` to resolve anything meaningful; the unit tests can mock the GitHub API, but the Phase 20 E2E test consumes Phase 17's output via this phase's downloader).
**Requirements:** INST-01, INST-02, INST-03, INST-04
**Success Criteria** (what must be TRUE):
  1. **INST-01 (stable non-regression):** `firestarter --install` invoked with no new flags on a stable-installed app hits `api.github.com/repos/henols/firestarter/releases/latest`, parses `tag_name` + the matching board's `browser_download_url`, downloads the `.hex`, and proceeds to flash. Behavior is byte-identical to the pre-v1.4 download URL + asset selection — verified by a pytest fixture that compares HTTP-request shape and post-download file path against a captured baseline. The `_compare_versions` refactor is invisible at the URL level (only the internal comparison shape changes; PEP 440 `X.Y.Z` parses identically to today's int-tuple).
  2. **INST-02 (`--pre`):** `firestarter --install --pre` hits `/repos/henols/firestarter/releases` (paginated), filters to `prerelease: true`, sorts by PEP 440 version order, picks the highest, resolves the board-matching asset, downloads + flashes. If no pre-release exists, falls back to stable (mirrors `pip install --pre`). Verified by a pytest fixture that mocks the GitHub API with a fixture release list containing mixed stable + pre-release tags and asserts the correct tag is picked.
  3. **INST-03 (`--firmware-version`):** `firestarter --install --firmware-version 3.1.0b2` validates the input against the PEP 440 regex from Phase 15 (`^[0-9]+\.[0-9]+\.[0-9]+(b|rc)?[0-9]*$` — accepts stable + beta + rc forms), then fetches `/repos/henols/firestarter/releases/tags/3.1.0b2`. Invalid input (e.g. `--firmware-version 3.1.0beta1`) fails fast with a clear error and no network call. Mutually exclusive with `--pre` — passing both fails fast.
  4. **INST-04 (`firmware list`):** `firestarter firmware list` (default `--all`) outputs a plain-text table: `version | channel | published | asset_url` with one row per release for the configured board. `--pre` filters to pre-releases only; `--stable` filters to stable only; `--json` outputs the same data as JSON. Greppable, non-interactive.
  5. **PEP 440 comparator fix:** `firmware.py:_compare_versions` no longer raises `ValueError` on inputs like `"3.1.0b1"`. Uses `packaging.version.Version` (added as an explicit dep in `pyproject.toml`). Verified by parameterized pytest asserting correct ordering across stable + beta + rc combinations.
  6. Test coverage for all four flags lives in `firestarter_app/tests/test_firmware_install.py` (or similar). Existing `firmware.py` callers in `main.py` continue to work; the refactor preserves the public function signatures of `fetch_latest_release_info` (or it's deprecated in favor of a new router function with a back-compat shim — planner picks).
**Plans:** 2/2 plans complete

#### Phase 19: Documentation
**Goal:** End users know how to opt into the beta channel — both for the APP (PyPI `--pre`) AND for the FIRMWARE (the Phase 18 CLI flags) — and the release engineer knows how to cut a beta. Three documentation artifacts land: app README beta section (with worked examples for `--pre`, `--firmware-version`, `firmware list`), firmware README beta section, and a meta-repo release-procedures doc that captures the locked-step cutting workflow.
**Depends on:** Phases 15, 16, 17, 18 (you document what you built, not what you plan — the Phase 15 lockstep mechanism + Phase 16/17 workflow trigger shapes + Phase 18 CLI surface are the substrate for the documentation).
**Requirements:** DOC-01, DOC-02, DOC-03
**Success Criteria** (what must be TRUE):
  1. `firestarter_app/README.md` has a "Beta / pre-release channel" section documenting: (a) how to install the app — `pip install --pre firestarter` — with a worked example showing the install command + sanity check (`firestarter --version` reports the `X.Y.ZbN` string); (b) how to install matching beta firmware — `firestarter --install --pre` (worked example); (c) how to pin an exact firmware version — `firestarter --install --firmware-version X.Y.ZbN` (worked example with both a stable and a beta tag); (d) how to list available firmwares — `firestarter firmware list --all` (worked example output); (e) what stability guarantee a beta carries (explicit "no guarantees, may break, intended for testing of unreleased features" wording); (f) how to report issues against a beta build — which version identifiers to cite (`pip show firestarter` for app, `firestarter firmware list` or handshake string for firmware).
  2. `firestarter/README.md` has a "Beta / pre-release channel" section documenting: (a) where to find pre-release `.hex` artifacts — GitHub Releases page, filtering by "Pre-release" tag (with a screenshot or link example) AND via `firestarter --install --pre` for app-driven install; (b) what stability guarantee a beta carries (same wording family as the app README); (c) how to report issues against a beta build — which firmware version (the `X.Y.ZbN` string from `include/version.h` or printed at the firmware handshake) + commit SHA + board (Uno / Leonardo / other) + chip to cite.
  3. `.planning/v1.4-RELEASE-PROCEDURES.md` (or equivalent path under `.planning/`) documents the release-engineer workflow for cutting a beta: (a) which branch to push to in each repo (`beta` in both `firestarter_app/` and `firestarter/`); (b) how the locked-step `X.Y.ZbN` identifier is chosen and applied — verbatim from `15-LOCKSTEP-PROCEDURE.md`; (c) the eventual promotion path from beta to stable (auto-promotion deferred; manual promotion via fast-forward merge from `beta` to `main`). The document is detailed enough that a release engineer with no prior v1.4 context can cut a beta following it as a checklist.
**Plans:** 1/1 plan
- [ ] 19-01-PLAN.md — Wave 1: land all three DOC artifacts (DOC-01 firestarter_app/README beta section, DOC-02 firestarter/README beta section, DOC-03 .planning/v1.4-RELEASE-PROCEDURES.md) + fix 15-LOCKSTEP-PROCEDURE.md Step 4/5 stale workflow filenames (D-07). Two submodule commits (firestarter_app/, firestarter/) + one meta-repo bundled commit.

#### Phase 20: End-to-End Smoke Test + Milestone Close
**Goal:** A real beta build is cut in both sub-repos following the Phase 19 documented procedure; the Phase 18 downloader is exercised against the resulting beta firmware; all acceptance criteria verified end-to-end; milestone-close artifacts land. This is the milestone's acceptance gate — no v1.4 close without a green E2E-01.
**Depends on:** Phases 15, 16, 17, 18, 19 (every prior phase — the smoke test exercises the lockstep mechanism, both beta pipelines, the consumer-side downloader, and the documented release-engineer procedure as a single end-to-end flow).
**Requirements:** E2E-01, MS-01
**Success Criteria** (what must be TRUE):
  1. A real beta build is cut in both sub-repos following the `v1.4-RELEASE-PROCEDURES.md` procedure (no shortcuts, no out-of-band fixes). Resulting version identifier is something like `0.0.1b1` or whatever test identifier doesn't conflict with the current production version line. After the cut: (a) PyPI shows the `X.Y.ZbN` pre-release version on the `firestarter` project page; (b) `pip install --pre firestarter==X.Y.ZbN` installs cleanly from a fresh Python environment on at least one operator-accessible OS (macOS or Linux); (c) firmware GitHub Releases page shows the build marked `Pre-release` (not `Latest`) with the expected `firestarter_*.hex` artifacts per board attached; (d) both repos' beta release tags carry the same `X.Y.ZbN` string per VER-03; (e) on the beta-installed app, `firestarter --install --pre` downloads the matching `X.Y.ZbN` firmware `.hex` for the configured board (proves INST-02 end-to-end); (f) on a SEPARATE fresh stable install (`pip install firestarter` of the previous stable version line, NOT `--pre`), `firestarter --install` downloads stable firmware — NOT the new beta (proves INST-01 non-regression).
  2. `.planning/MILESTONES.md` carries a v1.4 milestone summary styled consistently with the v1.0 / v1.2 entries: delivered (beta pipeline both sides, lockstep mechanism, beta-aware downloader, docs, E2E smoke test), stats (phase / plan counts, commit counts in both submodules), key decisions (the chosen lockstep mechanism, the trigger model, PEP 440 vs alternatives, the scope amendment to include INST-01..04), known gaps if any (auto-promotion workflow deferred, branch protection deferred, signed artifacts deferred — explicit pointers to "Future Requirements" in REQUIREMENTS.md).
  3. v1.4 phase directories archived to `.planning/milestones/v1.4-phases/` and `PROJECT.md` Active Milestone footer updated to reflect v1.4 ship state. If v1.3 is still paused at v1.4 close, the v1.3 paused-status note in MILESTONES.md and PROJECT.md is refreshed to point at any new resume-relevant context (no functional change to v1.3 archive — just a coherence pass).
**Plans:** TBD

### v1.4 Coverage

| REQ-ID | Phase |
|--------|-------|
| VER-01 | Phase 15 |
| VER-02 | Phase 15 |
| VER-03 | Phase 15 |
| REL-01 | Phase 16 |
| GATE-01 | Phase 16 |
| REL-02 | Phase 17 |
| GATE-02 | Phase 17 |
| INST-01 | Phase 18 |
| INST-02 | Phase 18 |
| INST-03 | Phase 18 |
| INST-04 | Phase 18 |
| DOC-01 | Phase 19 |
| DOC-02 | Phase 19 |
| DOC-03 | Phase 19 |
| E2E-01 | Phase 20 |
| MS-01 | Phase 20 |

**Mapped: 16/16 requirements ✓** — no orphans, no duplicates. (Was 12/12 before the 2026-05-20 amendment that added INST-01..04 + Phase 18.)

## v1.3 — CMOS EPROM Family Hardware Validation (PAUSED 2026-05-20)

**Milestone goal:** Bench-validate, on real silicon and on both Arduino Uno + Leonardo, that the algorithm-0x07 (28-pin DIP CMOS UV-EPROM, 212 chips in DB) and algorithm-0x08 (32-pin DIP CMOS UV-EPROM, 127 chips in DB) dispatch logic shipped in v1.0–v1.2 actually programs, reads back, and verifies cleanly across the full 32K → 512K density span. This is **validation, not new features** — architecture is locked.

**Status:** ⏸ Paused 2026-05-20 — hardware-gated. Phase 11 shipped clean; Phase 12 Wave 0 desk-side scaffold committed; Plans 12-01/02/03 (BENCH-01/02/05 — W27C512, SST27SF512, W27C257) + entire Phase 13 + Phase 14 await operator bench hardware (Uno + Leonardo + RURP shield + DIP-28 socket + scope + bench chips). Resume command: `/gsd-execute-phase 12 --wave 1 --interactive` once hardware is available.

**Granularity:** Comprehensive (compressed — focused validation milestone, not a build milestone).
**Phase numbering:** Phases 11-14 (continues from v1.2 close).

### Structural Notes

- **Bench-gated vs. desk-side split.** Phase 11 (coverage matrix + DB inconsistency report) is fully desk-side and can land without hardware. Phases 12 and 13 are operator-on-bench (Uno + Leonardo + chip socket + scope). Phase 14 is paperwork only.
- **PROTO-01/02 are observation protocols, not standalone phases.** Chip-ID read at the start of every BENCH cycle (PROTO-01) and scope-measured VPP at the chip socket during write (PROTO-02) are practiced in Phase 12 where the protocol is established, then carried forward into Phase 13. They map formally to Phase 12 (where the observation protocol is set up + first applied) but the success-criteria coverage runs across both bench phases.
- **Density coverage strategy.** Phase 12 covers the 28-pin / algo-0x07 family at both the marquee 64K size (W27C512, SST27SF512) and the 32K low end (BENCH-05). Phase 13 mirrors this for 32-pin / algo-0x08 at 256K + 512K (W27C020, W27E040) and the 128K low end (BENCH-06). Together this exercises the full address-bus span end-to-end.
- **Deferred v1.2 items.** BENCH-01 (W27C512 bench cycle) naturally closes the four v1.2 hardware-pending UAT items (Phase 08 SC#2/SC#3, Phase 08 HUMAN-UAT.md, Phase 09 Plan-05 Task 3 chip-seated W27C512 UAT). Phase 12 detail flags this closure.
- **Flash budget floor.** v1.2 ship state (Leonardo 24,482 B / 85.4%, Uno 22,262 B / 69.0%, firmware 3.0.0-dev) is a non-regress floor. v1.3 is read-only against firmware semantics; only defect-driven changes are in scope.

### Phases

- [x] **Phase 11: Coverage Matrix & DB Inconsistency Audit** — Desk-side enumeration of all 339 algo-0x07/0x08 DB rows + flag intra-algorithm inconsistencies. ✅ 2026-05-19
- [ ] **Phase 12: 28-Pin / Algo-0x07 Bench Validation** — End-to-end bench cycle on Uno + Leonardo for W27C512, SST27SF512, and the 32K density-low representative; establish chip-ID + VPP scope observation protocols. ⏸ Paused (Wave 0 shipped; Waves 1-3 await hardware)
- [ ] **Phase 13: 32-Pin / Algo-0x08 Bench Validation** — End-to-end bench cycle on Uno + Leonardo for W27C020, W27E040, and the 128K density-low representative; same observation protocols carried forward. ⏸ Paused
- [ ] **Phase 14: Milestone Close & Artifacts** — Publish BENCH-RESULTS, update MILESTONES, archive v1.3 phase directories. ⏸ Paused

### Phase Details

#### Phase 11: Coverage Matrix & DB Inconsistency Audit
**Goal:** Operator has a complete, single-source coverage map of every algo-0x07 + algo-0x08 chip in `chip_database.json`, with intra-algorithm DB inconsistencies surfaced as defect candidates for follow-up milestones.
**Depends on:** Nothing (desk-side; can land before any bench session).
**Requirements:** COV-01, COV-02
**Success Criteria** (what must be TRUE):
  1. A coverage matrix file exists at `.planning/v1.3-COVERAGE-MATRIX.md` (or equivalent) enumerating every algo-0x07 + algo-0x08 row in `chip_database.json` with: manufacturer, part_number(s), pin_count, size_bytes, pulse_duration, chip_id_check, chip_id_value, pinout class. Total row count matches DB histogram (212 + 127 = 339 chips).
  2. The same file (or a companion file) lists every intra-algorithm DB inconsistency — chips that share `pin_count` + `algorithm` but differ in `pulse_duration`, `chip_id_check`, or `pinout` — with each inconsistency labeled as a defect candidate for v1.4 or a sub-repo PR (no auto-fixes applied in v1.3).
  3. Operator can use the matrix to confirm that the six BENCH chips (BENCH-01..06) span the pinout classes and pulse-duration profiles actually represented in the DB, so bench results generalize to the rest of the 339 rows.
**Plans:** 6 plans
- [x] 11-01-PLAN.md — Wave 0 failing-test scaffold for tests/test_audit_coverage_matrix.py (10 tests) ✅ 2026-05-19
- [x] 11-02-PLAN.md — Wave 1 tool skeleton + CLI + §1 Summary + §2 DB Count Reconciliation ✅ 2026-05-19
- [x] 11-03-PLAN.md — Wave 2 §3 Full Enumeration (339 rows, per-algorithm sub-tables, D-06 sort) ✅ 2026-05-19
- [x] 11-04-PLAN.md — Wave 3 §4 Defect Candidates + DEFECT-COV-NN ledger + --check semantics
- [x] 11-05-PLAN.md — Wave 4 §5 BENCH Coverage Proof + golden-file fixture
- [x] 11-06-PLAN.md — Wave 5 D-07 planning-doc count reconciliation (PROJECT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md) ✅ 2026-05-19

#### Phase 12: 28-Pin / Algo-0x07 Bench Validation
**Goal:** On both Uno and Leonardo, operator can run a full write → read-back → verify cycle on every named 28-pin CMOS UV-EPROM (W27C512, SST27SF512) and on a 32K density-low representative, with chip-ID and VPP observation protocols established and captured.
**Depends on:** Phase 11 (coverage matrix informs which density-low representative is in scope and which pinout classes are exercised). Bench hardware: Uno + Leonardo + RURP shield + DIP-28 socket + scope.
**Requirements:** BENCH-01, BENCH-02, BENCH-05, PROTO-01, PROTO-02
**Success Criteria** (what must be TRUE):
  1. Operator can complete the full bench cycle (chip-ID read where applicable → blank-check → write of the deterministic test image → read-back → byte-identical verify → post-cycle blank-check where electrically erasable) for W27C512 on both Uno and Leonardo with green-verdict result captured for the BENCH-RESULTS artifact. Closes deferred v1.2 Phase 08 SC#2/SC#3 + Phase 09 Plan-05 Task 3 + Phase 08 HUMAN-UAT.md.
  2. Same full bench cycle completes cleanly on both boards for SST27SF512.
  3. Same full bench cycle completes cleanly on both boards for the chosen 32K density-low representative (W27C257 or W27E257 or SST27SF256), exercising the low end of the algo-0x07 address-bus span.
  4. Chip-ID observation protocol (PROTO-01): for every chip in BENCH-01/02/05 where `chip_id_check: true` in `chip_database.json`, the chip-ID read returns the DB-declared `chip_id_value` on both boards; mismatches confirmed to block write via the safety stack. Observation protocol is recorded in a way that Phase 13 can re-apply it without re-derivation.
  5. VPP observation protocol (PROTO-02): scope-measured VPP at the chip socket VPP pin reads 12V ±5% during write/erase phases and idles at VCC or off between operations, on both boards, for every chip in BENCH-01/02/05. Scope trace captured at least once per board.
**Plans:** 4 plans
- [x] 12-04-PLAN.md — Wave 0 desk-side scaffold: BENCH-RESULTS.md skeleton + .planning/v1.3/{bench-logs,scope}/ directories
- [ ] 12-01-PLAN.md — Wave 1 BENCH-01 W27C512 bench cycle on Uno + Leonardo + PROTO-02 scope photos at pin 22 (closes deferred Phase 08/09 UAT items)
- [ ] 12-02-PLAN.md — Wave 2 BENCH-02 SST27SF512 bench cycle + PROTO-01 blocked-write evidence capture (MSG_ERR_CHIP_ID_MISMATCH)
- [ ] 12-03-PLAN.md — Wave 3 BENCH-05 W27C257 bench cycle (probe-point swap to pin 1 — DIP28_27256 VPP) + PROTO-02 BENCH-05 leg scope photos

#### Phase 13: 32-Pin / Algo-0x08 Bench Validation
**Goal:** On both Uno and Leonardo, operator can run a full write → read-back → verify cycle on every named 32-pin CMOS UV-EPROM (W27C020, W27E040) and on a 128K density-low representative, completing the algo-0x08 family coverage at the high (512K) and low (128K) ends of the address-bus span. Chip-ID + VPP observation protocols from Phase 12 are re-applied.
**Depends on:** Phase 12 (chip-ID + VPP observation protocols established; bench harness validated against algo-0x07 first). Bench hardware: Uno + Leonardo + RURP shield + DIP-32 socket + scope.
**Requirements:** BENCH-03, BENCH-04, BENCH-06
**Success Criteria** (what must be TRUE):
  1. Operator can complete the full bench cycle (chip-ID read where applicable → blank-check → write of the deterministic test image → read-back → byte-identical verify → post-cycle blank-check where electrically erasable) for W27C020 on both Uno and Leonardo with green-verdict result captured.
  2. Same full bench cycle completes cleanly on both boards for W27E040, exercising the algo-0x08 512K high-end address-bus span.
  3. Same full bench cycle completes cleanly on both boards for the chosen 128K density-low representative (W27C010 or W27E010 or W27L010 or SST27SF010), exercising the low end of the algo-0x08 address-bus span.
  4. The chip-ID and VPP observation protocols set up in Phase 12 (PROTO-01, PROTO-02) are re-applied across BENCH-03/04/06 with no protocol modifications; any deviation (e.g. a chip with `chip_id_check: false` that nonetheless returns a stable ID, or a VPP rail that drifts beyond ±5%) is captured as a Phase 14 BENCH-RESULTS quirk note.
**Plans:** TBD

#### Phase 14: Milestone Close & Artifacts
**Goal:** v1.3 ships with a per-chip, per-board green/red/quirks artifact covering all six BENCH chips and both PROTO observation protocols, plus a clean milestone close (MILESTONES.md updated, phase directories archived).
**Depends on:** Phases 11, 12, 13 (all bench cycles complete and coverage matrix in hand).
**Requirements:** DOC-01, DOC-02
**Success Criteria** (what must be TRUE):
  1. `.planning/v1.3-BENCH-RESULTS.md` exists with a per-chip, per-board table covering BENCH-01..06 + PROTO-01/02 observations: green/red verdict, scope-measured VPP trace reference, chip-ID read result vs. `chip_id_value`, quirks noted, serial-log snippets (verbose-mode INFO or SERIAL_DEBUG breadcrumbs) where captured, photo or scope evidence linked where available.
  2. `MILESTONES.md` carries a v1.3 milestone summary (delivered, stats, decisions, known gaps if any) styled consistently with the v1.0 and v1.2 entries; v1.3 phase directories archived to `.planning/milestones/v1.3-phases/`; `PROJECT.md` updated to reflect v1.3 ship state.
  3. Flash budget non-regress floor (Leonardo 24,482 B / 85.4%, Uno 22,262 B / 69.0%, firmware 3.0.0-dev) is confirmed unchanged at milestone close — v1.3 introduced no firmware code paths that grew flash usage.
**Plans:** TBD

### v1.3 Coverage

| REQ-ID | Phase |
|--------|-------|
| BENCH-01 | Phase 12 |
| BENCH-02 | Phase 12 |
| BENCH-03 | Phase 13 |
| BENCH-04 | Phase 13 |
| BENCH-05 | Phase 12 |
| BENCH-06 | Phase 13 |
| PROTO-01 | Phase 12 (observation protocol carried forward into Phase 13) |
| PROTO-02 | Phase 12 (observation protocol carried forward into Phase 13) |
| COV-01 | Phase 11 |
| COV-02 | Phase 11 |
| DOC-01 | Phase 14 |
| DOC-02 | Phase 14 |

**Mapped: 12/12 requirements ✓** — no orphans, no duplicates.

## Prior Milestones (archived)

<details>
<summary>✅ v1.2 Message-ID Logging Rework (Phases 6-9) — SHIPPED 2026-05-19</summary>

- [x] **Phase 6**: Logging Infrastructure (catalog + codegen + helper + decoder) — 6/6 plans
- [x] **Phase 7**: Convert ERROR + WARN + INFO Call-Sites — 13/13 plans
- [x] **Phase 8**: Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END) — 8/8 plans
- [x] **Phase 9**: Delete Old Log Macros + Measure Flash Savings — 5/5 plans
- [x] **Phase 10**: Milestone Close (v1.2) — closed by `/gsd-complete-milestone` (DOC-02)

Full milestone archive: [`.planning/milestones/v1.2-ROADMAP.md`](milestones/v1.2-ROADMAP.md) (frozen snapshot of full phase details + coverage map + dependency graph).

Requirements archive: [`.planning/milestones/v1.2-REQUIREMENTS.md`](milestones/v1.2-REQUIREMENTS.md) (23/23 complete).

Summary: [`.planning/MILESTONES.md`](MILESTONES.md) §v1.2.

</details>

<details>
<summary>⏸ v1.1 Safety Closure & Hardware Validation (Phases 1-5) — PAUSED 2026-05-18</summary>

- [x] **Phase 1**: Safety Closure (Intel-flash VPP, 28C chip-id) — complete
- [x] **Phase 2**: Wire-key rename + minipro attribution scrub — complete
- [x] **Phase 3**: Retroactive VERIFICATION.md for v1.0 phases — complete
- [ ] **Phase 4**: Hardware validation across chip families — Plan 2 of 3 in progress; **FM1608 byte-0 read bug** parked (needs different Uno R3 to unblock; see [`.planning/debug/fm1608-fresh-chip-baseline.md`](debug/fm1608-fresh-chip-baseline.md))
- [ ] **Phase 5**: Milestone close (DOC-01) — deferred until after v1.2 ships or fm1608 unblocks

Original artifacts: [`.planning/milestones/v1.1-paused/`](milestones/v1.1-paused/).

Also carrying: WARNING-4 (`firestarter_test.sh` / `write_test.sh` references to deleted `database_generated.json`).

</details>

<details>
<summary>✅ v1.0 Protocol-Aware Programming Architecture (Phases 1-13) — SHIPPED 2026-05-11</summary>

- [x] Phases 1-13 covering the algorithm-first dispatch architecture (13 phases, 22 plans, 4-day timeline)
- Key deliverables: protocol-prefix dispatch in `memory.cpp`, 743-chip database with explicit `algorithm` integer, five firmware handlers (`configure_eprom`, `configure_flash3`, `configure_flash_intel`, `configure_eeprom28c`, `configure_sram`), pre-write safety stack (VPP ADC compare, chip-ID validation, blank check), static-pin and address-bus correctness

Full archive: [`.planning/milestones/v1.0-ROADMAP.md`](milestones/v1.0-ROADMAP.md) | [`.planning/milestones/v1.0-REQUIREMENTS.md`](milestones/v1.0-REQUIREMENTS.md) | [`.planning/milestones/v1.0-MILESTONE-AUDIT.md`](milestones/v1.0-MILESTONE-AUDIT.md) | [`.planning/milestones/v1.0-INTEGRATION-CHECK.md`](milestones/v1.0-INTEGRATION-CHECK.md) | [`.planning/milestones/v1.0-phases/`](milestones/v1.0-phases/).

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1-13 (v1.0) | v1.0 | 22/22 | ✅ Shipped | 2026-05-11 |
| 1-3 (v1.1) | v1.1 | done | ✅ Complete | 2026-05-12..18 |
| 4 (v1.1) | v1.1 | partial | ⏸ Parked | — (FM1608 blocked) |
| 5 (v1.1) | v1.1 | 0/0 | ⏸ Deferred | — |
| 6 | v1.2 | 6/6 | ✅ Complete | 2026-05-18 |
| 7 | v1.2 | 13/13 | ✅ Complete | 2026-05-18 |
| 8 | v1.2 | 8/8 | ✅ Complete | 2026-05-18 |
| 9 | v1.2 | 5/5 | ✅ Complete | 2026-05-19 |
| 10 (close) | v1.2 | n/a | ✅ Complete | 2026-05-19 |
| 11 | v1.3 | 6/6 | ✅ Complete | 2026-05-19 |
| 12 | v1.3 | 1/4 | ⏸ Paused | — (hardware-gated) |
| 13 | v1.3 | 0/0 | ⏸ Paused | — (hardware-gated) |
| 14 (close) | v1.3 | 0/0 | ⏸ Paused | — (hardware-gated) |
| 15 | v1.4 | 4/4 | ✅ Complete  | 2026-05-20 |
| 16 | v1.4 | 1/1 | Complete    | 2026-05-20 |
| 17 | v1.4 | 1/1 | Complete    | 2026-05-20 |
| 18 | v1.4 | 2/2 | Complete    | 2026-05-20 |
| 19 | v1.4 | 0/1 | Planned     | — (Documentation; 19-01-PLAN.md planned 2026-05-20) |
| 20 (close) | v1.4 | 0/0 | Not started | — (E2E + Milestone Close; was Phase 19 before 2026-05-20 amendment) |

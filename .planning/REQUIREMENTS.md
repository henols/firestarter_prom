# Milestone v1.4 — Beta & Pre-release Deployment Pipeline

**Created:** 2026-05-20
**Goal:** Add a parallel beta / pre-release deployment channel for both sub-repos. The existing main → stable pipelines stay untouched; beta is additive plumbing. App publishes PyPI pre-release versions installable via `pip install --pre firestarter`; firmware publishes GitHub Pre-release artifacts (`prerelease: true`, `make_latest: false`). App and firmware ship locked-step with matching version numbers as a coordinated pair.

**Core constraint:** This milestone is **CI/CD plumbing + docs only** — zero new user-facing CLI features in the app, zero firmware behavior changes, zero hardware testing. All implementation commits land inside the two submodules (`.github/workflows/`, `.github/scripts/update_version.py`, version files); meta-repo tracks only planning artifacts.

> v1.3 (CMOS EPROM Family Hardware Validation) is **PAUSED** as of 2026-05-20 (hardware-gated). v1.3 requirements (BENCH-01..06, PROTO-01..02, COV-01..02 already complete, DOC-01..02) are archived at `.planning/milestones/v1.3-paused/REQUIREMENTS-at-pause.md` and will resume from there when bench hardware is available. v1.4 does NOT depend on v1.3 closure.

## v1.4 Requirements

### REL — Beta release pipeline (artifact production)

The two sub-repos each grow a parallel beta channel that mirrors the trigger shape of the existing stable channel but produces opt-in pre-release artifacts.

- [ ] **REL-01**: Push to a `beta` branch in `firestarter_app/` triggers a new (or extended) GitHub Actions workflow that runs the existing CI test suite, bumps the pre-release version identifier (per VER-01), creates a GitHub Release with `prerelease: true` and `make_latest: false`, and publishes the resulting wheel/sdist to **PyPI** (the same index as stable, not TestPyPI).
- [ ] **REL-02**: Push to a `beta` branch in `firestarter/` triggers a new (or extended) GitHub Actions workflow that runs the existing build pipeline (catalog validity check, codegen drift gate, native Unity tests, PlatformIO build), bumps the pre-release version identifier (per VER-02), and creates a GitHub Release with `prerelease: true`, `make_latest: false`, and the same `firestarter_*.hex` artifacts per board (Uno, Leonardo, any other configured board) as the stable build.

### VER — Versioning & locked-step coordination

Beta builds use PEP 440 pre-release identifiers in the app, mapped to matching firmware version strings, and coordinated so a beta cut in one repo is paired with the same version in the other.

- [ ] **VER-01**: `firestarter_app/.github/scripts/update_version.py` (or its replacement) recognizes beta-branch builds and emits PEP 440 pre-release identifiers (`X.Y.Zb1`, `X.Y.Zb2`, `X.Y.ZrcN`, etc.) instead of bumping the patch version. Stable-branch behavior (patch auto-bump) preserved verbatim.
- [ ] **VER-02**: `firestarter/.github/scripts/update_version.py` (or its replacement) recognizes beta-branch builds and emits matching pre-release identifiers (`X.Y.Zb1` etc.). The format is identical to the app's so locked-step comparison is a string equality check.
- [ ] **VER-03**: Locked-step coordination mechanism exists and is documented. When a beta is cut in one sub-repo, the matching beta version is producible in the other sub-repo by following a defined procedure (the exact mechanism — shared `VERSION` file, cross-repo workflow trigger, or manually-paired beta-branch push — is the load-bearing planning decision for the milestone's first phase and is finalized during /gsd-discuss-phase). Verification: after the procedure runs, both repos' beta releases carry the same `X.Y.ZbN` string.

### GATE — Stable-pipeline preservation (regression gates)

The existing main → stable pipelines must continue to behave identically. Beta plumbing is purely additive.

- [ ] **GATE-01**: After v1.4 lands, a push to `firestarter_app/main` still produces a GitHub Release with `make_latest: true`, the `firestarter_*.whl` and `*.tar.gz` published to PyPI as a non-pre-release version (no `b`/`rc` suffix), and `__version__` in `firestarter/__init__.py` auto-bumped to the next patch. No new mandatory CI checks added to the stable path beyond what currently runs.
- [ ] **GATE-02**: After v1.4 lands, a push to `firestarter/main` still produces a GitHub Release with `make_latest: true`, the `firestarter_*.hex` artifacts per board (same set as today), version bumped in `include/version.h`, and the existing catalog-validity + codegen-drift + Unity-test gates run unchanged. No new mandatory CI checks added to the stable path beyond what currently runs.

### DOC — Documentation & operator guidance

The beta channel is only useful if (a) end users know how to opt in, and (b) the release engineer knows how to cut a beta.

- [ ] **DOC-01**: `firestarter_app/README.md` documents the beta channel: how to install (`pip install --pre firestarter`), what stability guarantee a beta carries, and how to report issues against a beta build (which version identifier to cite).
- [ ] **DOC-02**: `firestarter/README.md` documents the beta channel: where to find pre-release `.hex` artifacts (GitHub Releases page, filtering by "pre-release"), what stability guarantee a beta carries, and how to report issues against a beta build (which firmware version + commit SHA to cite).
- [ ] **DOC-03**: Meta-repo planning docs (`.planning/v1.4-RELEASE-PROCEDURES.md` or equivalent) document the release-engineer workflow for cutting a beta: which branch to push to in each repo, how the locked-step version identifier is chosen and applied, and the eventual promotion path from beta to stable (deferred to a follow-on milestone if the auto-promotion workflow isn't built here).

### E2E — End-to-end smoke test

After plumbing lands, prove the whole stack works by cutting a real beta.

- [ ] **E2E-01**: Cut a real beta build (e.g. version `0.0.1b1` or whatever test identifier doesn't conflict with the current version line) in both sub-repos following the documented procedure. Verify: (a) app PyPI shows the pre-release version and `pip install --pre firestarter==X.Y.ZbN` installs cleanly; (b) firmware GitHub Releases page shows the build marked `Pre-release`, not `Latest`, with the expected `.hex` artifacts attached; (c) both versions strings match per VER-03. This is the milestone's acceptance gate — no v1.4 close without a green E2E-01.

### MS — Milestone close artifacts

- [ ] **MS-01**: Update `.planning/MILESTONES.md` with the v1.4 summary (what shipped, what didn't, links to commits in the two submodules). Archive v1.4 phase directories under `.planning/milestones/v1.4-phases/`. Update `PROJECT.md` Active Milestone footer. If v1.3 is still paused at v1.4 close, refresh the v1.3 paused-status note in MILESTONES.md history block to point at any new resume-relevant context.

## Future Requirements (deferred past v1.4)

- **TestPyPI publishing channel** — Initially considered; rejected for v1.4 because PyPI pre-release versions provide opt-in via `--pre` without operator friction of a separate index. Could revisit if beta operators report needing isolated install testing.
- **Auto-promotion beta → stable workflow** — Workflow file (or script) that promotes a green beta version to a stable release without re-running the full pipeline. Deferred until beta channel sees real use and the promotion pattern stabilizes.
- **Branch-protection rules for the `beta` branch** — Optional safety net (require PR review, require status checks). Useful but not load-bearing for the channel itself; add post-v1.4 if the channel gets accidental-push problems.
- **Signed release artifacts** (sigstore / GPG) — Out of scope for v1.4. Beta and stable both ship unsigned today; if signing is added, do both at once in a dedicated milestone.
- **Beta installation metrics / telemetry** — How many users are on beta? Not in scope; could fold into a future release-ops milestone.

## Out of Scope (explicit exclusions for v1.4)

- **TestPyPI publishing** — see Future Requirements (rejected for operator friction; PyPI `--pre` is the cleaner UX).
- **Changes to the existing main → stable pipeline behavior** — preserved exactly as-is per GATE-01 + GATE-02. v1.4 is additive plumbing, not a refactor of stable.
- **Hardware testing of beta builds** — v1.3's job once hardware is back. v1.4 is software-only.
- **New CLI features in the app or new firmware behavior** — purely deployment plumbing.
- **New CI checks (catalog drift, codegen gates, additional tests) on either the stable or beta path** — existing gates are reused, not extended. If new gates are needed, that's its own milestone.
- **Branch-protection rules / merge policies / release governance** — workflow plumbing only; people-process policy is separate.
- **v1.3 bench validation work** — paused; resumes when hardware is available. v1.4 does NOT block on v1.3 closure.

## Traceability

Each requirement maps to exactly one phase. Coverage: 12 requirements, 100% mapped (populated by roadmapper).

| REQ-ID | Phase | Plan(s) | Status |
|--------|-------|---------|--------|
| REL-01 | TBD | TBD | Not started |
| REL-02 | TBD | TBD | Not started |
| VER-01 | TBD | TBD | Not started |
| VER-02 | TBD | TBD | Not started |
| VER-03 | TBD | TBD | Not started |
| GATE-01 | TBD | TBD | Not started |
| GATE-02 | TBD | TBD | Not started |
| DOC-01 | TBD | TBD | Not started |
| DOC-02 | TBD | TBD | Not started |
| DOC-03 | TBD | TBD | Not started |
| E2E-01 | TBD | TBD | Not started |
| MS-01 | TBD | TBD | Not started |

**Coverage target:** 12 requirements, 100% mapped to phases.

---

*Last updated: 2026-05-20 — initial v1.4 requirements draft. Traceability table populated by `gsd-roadmapper` at ROADMAP.md creation. v1.3 paused; v1.3 REQUIREMENTS.md archived at `.planning/milestones/v1.3-paused/REQUIREMENTS-at-pause.md`.*

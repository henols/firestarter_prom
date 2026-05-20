---
phase: 15
slug: versioning-locked-step-coordination-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-20
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Derived from RESEARCH.md §Validation Architecture (lines 728-768).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest ≥7.0 (both sub-repos) |
| **Config file (app)** | `firestarter_app/pyproject.toml` — `[tool.pytest.ini_options]` testpaths=["tests"] |
| **Config file (firmware)** | None (Wave 0 creates `firestarter/tests/` directory; pytest auto-discovery — no new config required) |
| **Quick run command (app)** | `cd firestarter_app && pytest tests/test_update_version.py -v` |
| **Quick run command (firmware)** | `cd firestarter && pytest tests/test_update_version.py -v` |
| **Full suite command (app)** | `cd firestarter_app && pytest tests/ -v` |
| **Full suite command (firmware)** | `cd firestarter && pytest tests/ -v` (only one test file initially) |
| **Estimated runtime** | ~3 seconds per sub-repo (pure-Python script, no I/O beyond tmp files) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_update_version.py -v` in the affected sub-repo (~3s)
- **After every plan wave:** Run `pytest tests/ -v` in both sub-repos (~5s app, ~3s firmware)
- **Before `/gsd-verify-work`:** Full suite must be green in BOTH sub-repos
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

> Wave / Task IDs populated by planner. Below is the requirement→test-type mapping pre-derived from RESEARCH.md so the planner can attach each task to a row.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD-app-stable | app | 0 | VER-01 | — | App stable path produces byte-identical output to pre-v1.4 script (GATE-01 derivative) | unit | `cd firestarter_app && pytest tests/test_update_version.py -k "test_stable" -x` | ❌ W0 | ⬜ pending |
| TBD-app-beta | app | 1 | VER-01 | — | App `update_version.py` emits `X.Y.ZbN` when `GITHUB_REF=refs/heads/beta` AND `BETA_VERSION=X.Y.ZbN` | unit | `cd firestarter_app && pytest tests/test_update_version.py -k "test_beta" -x` | ❌ W0 | ⬜ pending |
| TBD-app-validation | app | 1 | VER-01 | — | `BETA_VERSION` rejected when not matching PEP 440 `bN`/`rcN` regex (no file modification on invalid input) | unit | `cd firestarter_app && pytest tests/test_update_version.py -k "test_validation" -x` | ❌ W0 | ⬜ pending |
| TBD-app-dryrun | app | 1 | VER-01 | — | `--dry-run` computes correct version + writes nothing to `__init__.py` and skips `$GITHUB_OUTPUT` | unit | `cd firestarter_app && pytest tests/test_update_version.py -k "test_dry_run" -x` | ❌ W0 | ⬜ pending |
| TBD-app-tag-fallback | app | 1 | VER-01 | — | When `BETA_VERSION` unset on beta branch, script scans git tags for highest `bN` matching base version and emits `b(N+1)` | unit | `cd firestarter_app && pytest tests/test_update_version.py -k "test_tag_fallback" -x` | ❌ W0 | ⬜ pending |
| TBD-fw-stable | firmware | 0 | VER-02 | — | Firmware stable path produces byte-identical `#define VERSION "X.Y.Z"` output (GATE-02 derivative) | unit | `cd firestarter && pytest tests/test_update_version.py -k "test_stable" -x` | ❌ W0 | ⬜ pending |
| TBD-fw-beta | firmware | 1 | VER-02 | — | Firmware emits `#define VERSION "X.Y.ZbN"` on beta context with explicit `BETA_VERSION` input | unit | `cd firestarter && pytest tests/test_update_version.py -k "test_beta" -x` | ❌ W0 | ⬜ pending |
| TBD-fw-validation | firmware | 1 | VER-02 | — | Firmware script validates `BETA_VERSION` against same PEP 440 regex as app (lockstep format-identity) | unit | `cd firestarter && pytest tests/test_update_version.py -k "test_validation" -x` | ❌ W0 | ⬜ pending |
| TBD-fw-dryrun | firmware | 1 | VER-02 | — | Firmware `--dry-run` flag emits proposed version without modifying `include/version.h` | unit | `cd firestarter && pytest tests/test_update_version.py -k "test_dry_run" -x` | ❌ W0 | ⬜ pending |
| TBD-fw-tag-fallback | firmware | 1 | VER-02 | — | Firmware tag-scan fallback matches app's behavior on identical git-tag fixture | unit | `cd firestarter && pytest tests/test_update_version.py -k "test_tag_fallback" -x` | ❌ W0 | ⬜ pending |
| TBD-procedure-doc | meta | 2 | VER-03 | — | Lockstep coordination procedure document exists in phase folder and is consumable by Phase 18 (acceptance: file exists, has `## Procedure` section, includes literal `BETA_VERSION` and `gh workflow run` references) | doc | `test -f .planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md && grep -q '^## Procedure' "$_"` | ❌ W2 | ⬜ pending |
| TBD-lockstep-e2e | meta | 2 | VER-03 | — | Fixture-driven dry-run on both sub-repos with same `BETA_VERSION` input produces matching version strings (string-equality assertion) | integration | `bash .planning/phases/15-versioning-locked-step-coordination-foundation/lockstep-dryrun-fixture.sh` (or pytest equivalent) | ❌ W2 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Task IDs above are placeholders (`TBD-*`). Planner assigns concrete IDs during plan creation and updates this table.*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tests/test_update_version.py` — covers VER-01 cases (stable + beta + dry-run + validation + tag-fallback)
- [ ] `firestarter/tests/` directory — does not exist yet; Wave 0 creates it
- [ ] `firestarter/tests/test_update_version.py` — covers VER-02 cases (same coverage as app)
- [ ] `firestarter/.github/workflows/build.yml` — new pytest step added (before existing PlatformIO build); `pip install pytest` step required (no `pyproject.toml` in firmware sub-repo today, so no `[dev]` extras to install)
- [ ] `firestarter_app/.github/workflows/ci.yml` — existing pytest run already covers the new test file once it lands; no workflow change needed

*All Wave 0 items are file-creation tasks. No new infrastructure beyond `pip install pytest` on the firmware CI runner.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Stable path byte-identity vs pre-v1.4 script | VER-01, VER-02 | Requires checked-out pre-v1.4 script output as a baseline; comparing output across script versions is best done with a one-shot golden-file fixture, but the baseline establishment is a one-time human-curated step | (1) Check out the pre-v1.4 commit of each `update_version.py`; (2) run with `GITHUB_REF=refs/heads/main` + `GITHUB_OUTPUT=/tmp/old.out` against current `__init__.py` / `version.h`; (3) capture resulting file write; (4) commit as golden fixture under `tests/golden/stable-baseline.{py,h}`; (5) the automated `test_stable` test (above) diffs new-script output against the golden fixture |

*Once the golden baseline is committed in Wave 0, the byte-identity check becomes fully automated. The manual step is the one-time baseline curation.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (test files + firmware tests/ dir + pytest install step)
- [ ] No watch-mode flags (single-shot pytest runs only)
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

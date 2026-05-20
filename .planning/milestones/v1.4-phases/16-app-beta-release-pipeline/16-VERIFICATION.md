---
phase: 16-app-beta-release-pipeline
verified: 2026-05-20T13:10:31Z
status: passed
score: 7/7 must-haves verified
overrides_applied: 0
re_verification: false
---

# Phase 16: App Beta Release Pipeline Verification Report

**Phase Goal:** A push to `firestarter_app/beta` triggers a new GitHub Actions workflow that runs the existing CI test suite, calls Phase 15's `update_version.py` in beta mode, creates a GitHub Release with `prerelease: true` + `make_latest: false`, and publishes wheel/sdist to PyPI as `X.Y.ZbN` pre-release. GATE-01 preserves stable behavior verbatim.
**Verified:** 2026-05-20T13:10:31Z
**Status:** passed
**Re-verification:** No — initial verification

## What Was Delivered

A single 72-line YAML file, `firestarter_app/.github/workflows/beta-release.yml`, committed at submodule SHA `001d8a2`. The file mirrors the structure of `release.yml` (stable pipeline template) with four targeted additions: `workflow_dispatch` trigger with optional `beta_version` input; inline CI gates (catalog validity, codegen drift, pip install, pytest) copied from `ci.yml` and placed before the version bump; `prerelease: true` on the release step; `make_latest: false` on the release step. Zero modifications to `release.yml`, `publish.yml`, `ci.yml`, or `update_version.py`.

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A push to `firestarter_app/beta` triggers `beta-release.yml` with inline CI gates before any version bump | VERIFIED | `push.branches: ['beta']` parsed; steps 3-6 (catalog validity → codegen drift → pip install → pytest) confirmed at lines 39-54; version bump step at line 56 (after pytest at line 53) |
| 2 | On gate-green the workflow calls `update_version.py` with `BETA_VERSION` env piped from `workflow_dispatch.inputs.beta_version` (empty on push trigger → git-tag-scan fallback) | VERIFIED | Step 7: `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}`, `run: .github/scripts/update_version.py` confirmed at lines 57-60; empty string on push trigger passes through as falsy to Phase 15 script |
| 3 | Workflow creates a GitHub Release with `prerelease: true` AND `make_latest: false` at tag `X.Y.ZbN` | VERIFIED | Step 9 with block: `tag_name: ${{ steps.version.outputs.version }}`, `prerelease: True`, `make_latest: False` — confirmed by YAML parse |
| 4 | Existing `publish.yml` fires unmodified on the resulting `release: published` event and uploads wheel/sdist to PyPI | VERIFIED | `publish.yml` `on: release: types: [published]` unchanged; `pypa/gh-action-pypi-publish@release/v1` present; GATE-01 confirms `publish.yml` byte-identical to pre-Phase-16 state |
| 5 | GATE-01: `release.yml`, `publish.yml`, and `ci.yml` are byte-identical before and after Phase 16 | VERIFIED | `git diff HEAD~1 -- .github/workflows/release.yml publish.yml ci.yml .github/scripts/update_version.py` returns 0 lines; `git diff --name-status HEAD~1 -- .github/workflows/` shows only `beta-release.yml` added |
| 6 | Workflow can be invoked via `gh workflow run beta-release.yml --ref beta -f beta_version=3.1.0b1` (canonical Phase 15 lockstep mechanism) | VERIFIED | `workflow_dispatch.inputs.beta_version` confirmed: `description: 'Explicit PEP 440 pre-release version (e.g. 3.1.0b1). Leave blank for auto-increment via git-tag scan.'`, `required: False`, `type: string`; accessible via `-f beta_version=...` |
| 7 | Auto-commit of the bumped version back to the beta branch does NOT re-trigger `beta-release.yml` (default GITHUB_TOKEN, no PAT on checkout) | VERIFIED | Checkout step `with` block contains only `fetch-depth: 0`, no `token:` parameter — confirmed by YAML parse; `git-auto-commit-action@v5` at step 8 has no `env:` or `with:` overrides |

**Score:** 7/7 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/.github/workflows/beta-release.yml` | Full beta release pipeline: triggers, inline CI gates, version bump, auto-commit, GH Release (prerelease) | VERIFIED | File exists, 72 lines, parses cleanly as YAML, all structural tokens present, submodule commit `001d8a2` |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `beta-release.yml` (Create new pre-release version step) | `firestarter_app/.github/scripts/update_version.py` | `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}` | WIRED | Lines 56-60: id=version, env block with BETA_VERSION, run: .github/scripts/update_version.py |
| `beta-release.yml` (Release step) | `firestarter_app/.github/workflows/publish.yml` (via `release: published` event) | `softprops/action-gh-release@v2` publishes GH Release; `publish.yml`'s `on.release.types: [published]` picks it up | WIRED | Release step confirmed at lines 65-72; publish.yml trigger confirmed unchanged |
| `beta-release.yml` (Checkout step) | Phase 15 git-tag-scan fallback in `update_version.py` | `actions/checkout@v4` with `fetch-depth: 0` — full tag history available for scan | WIRED | Step 1 `with.fetch-depth: 0` confirmed |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| YAML parses cleanly | `python3 -c "import yaml; yaml.safe_load(open('firestarter_app/.github/workflows/beta-release.yml'))"` | exit 0 | PASS |
| No `token:` on Checkout (anti-loop) | YAML parse — checkout step `with` keys | `{'fetch-depth': 0}` — no token key | PASS |
| `paths-ignore` under `push:` only, not `workflow_dispatch:` | YAML parse — `on.workflow_dispatch` key set | `paths-ignore` absent from workflow_dispatch | PASS |
| CI gate ordering: pytest before version-bump | line-number check: pytest=53, bump=56 | bump_line (56) > pytest_line (53) | PASS |
| `fetch-depth: 0` present | `grep -c 'fetch-depth: 0'` | 1 | PASS |
| All required structural tokens present | grep loop over 25 tokens | NONE missing | PASS |
| `prerelease: true` present | grep | line 69 | PASS |
| `make_latest: false` present | grep | line 70 | PASS |
| Existing pytest suite still green | `cd firestarter_app && pytest tests/` | 77 passed in 0.79s | PASS |
| `paths-ignore` byte-matches `release.yml` | YAML parse comparison | `['**.md','**.sh','.gitignore','docs/**','images/**','.github/**','.vscode/**','tools/**']` — identical | PASS |
| GATE-01: `release.yml` unchanged | `git diff HEAD~1 -- .github/workflows/release.yml \| wc -l` | 0 | PASS |
| GATE-01: `publish.yml` unchanged | `git diff HEAD~1 -- .github/workflows/publish.yml \| wc -l` | 0 | PASS |
| GATE-01: `ci.yml` unchanged | `git diff HEAD~1 -- .github/workflows/ci.yml \| wc -l` | 0 | PASS |
| GATE-01: `update_version.py` unchanged | `git diff HEAD~1 -- .github/scripts/update_version.py \| wc -l` | 0 | PASS |
| Single file added (beta-release.yml only) | `git diff --name-only HEAD~1 -- .github/workflows/` | `.github/workflows/beta-release.yml` only | PASS |
| GATE-01 extended: HEAD~5 diff (covers Phase 18 commits) | `git diff HEAD~5 -- release.yml publish.yml ci.yml \| wc -l` | 0 | PASS |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| REL-01 | 16-01-PLAN.md | Push to `firestarter_app/beta` triggers workflow: CI, pre-release version bump, GH Release (`prerelease: true`, `make_latest: false`), PyPI publish as `X.Y.ZbN` | SATISFIED | `beta-release.yml` fully implements all elements; `publish.yml` handles PyPI via `release: published` event without modification |
| GATE-01 | 16-01-PLAN.md | Push to `firestarter_app/main` still produces stable non-pre-release release with `make_latest: true`; no new CI checks on stable path | SATISFIED | `git diff HEAD~1` and `git diff HEAD~5` both return 0 lines for `release.yml`, `publish.yml`, `ci.yml`; only `beta-release.yml` added |

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter_app/.github/workflows/beta-release.yml` | 13 | `tools/**` in `paths-ignore` creates a deferred-detection gap for codegen drift on tool-only pushes to `beta` (noted in REVIEW.md WR-01) | Warning | Tool-only pushes to `beta` will not trigger the workflow; codegen drift from a `messages.toml`-only commit goes undetected until the next non-ignored push. Does not break the workflow correctness when triggered; does not affect GATE-01 or REL-01 structural requirements. Identified by code review (16-REVIEW.md); accepted as D-04 compliance (byte-match with `release.yml`). |
| `firestarter_app/.github/workflows/beta-release.yml` | — | D-26 audit echo step omitted (noted in REVIEW.md WR-02) | Info | Optional observability improvement; non-load-bearing per plan spec. SUMMARY.md documents the omission with rationale ("keeps diff against release.yml shape clean"). |

No `TBD`, `FIXME`, or `XXX` debt markers found. No stubs, no return null, no empty handlers.

---

## Human Verification Required

No human verification items. The following behaviors are intentionally deferred to Phase 20 (E2E-01) per PLAN.md and VALIDATION.md:

- Real GitHub Actions trigger on push to `beta` branch
- Real PyPI publish of `X.Y.ZbN` wheel/sdist
- `pip install --pre firestarter==X.Y.ZbN` against live PyPI index
- `gh workflow run beta-release.yml --ref beta -f beta_version=X.Y.ZbN` live invocation

These are documented as Phase 20 E2E-01 scope in VALIDATION.md §Manual-Only Verifications.

---

## Gaps Summary

No gaps. All 7 must-have truths verified. All structural tokens present. GATE-01 holds across both `HEAD~1` (Phase 16 commit boundary) and `HEAD~5` (spanning Phase 18 commits). Pytest suite green at 77/77.

The two review findings (WR-01: `tools/**` in paths-ignore; WR-02: D-26 summary step omitted) are pre-identified code review notes, not blocking gaps:
- WR-01 is a known behavioral trade-off accepted by D-04 (byte-match with release.yml). It does not break the workflow when triggered and does not affect either REL-01 or GATE-01 requirements.
- WR-02 is an explicitly optional step (D-26: "recommended", not mandatory); its omission is documented with rationale in SUMMARY.md.

---

_Verified: 2026-05-20T13:10:31Z_
_Verifier: Claude (gsd-verifier)_

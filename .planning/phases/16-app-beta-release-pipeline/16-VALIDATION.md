---
phase: 16
slug: app-beta-release-pipeline
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-20
---

# Phase 16 — Validation Strategy

> Per-phase validation contract. Derived from RESEARCH.md §Validation Architecture (lines 491-529). Phase 16 deliverable is a single YAML workflow file — verification is shell-level grep + git-diff assertions, not pytest unit tests.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | shell assertions (`grep`, `git diff`, `yamllint` if available) + existing pytest suite (regression only) |
| **Config file** | n/a — assertions invoked directly from PLAN.md verify commands |
| **Quick run command** | `bash tests/verify-beta-release.sh` (planner may inline assertions in `<automated>` blocks) |
| **Full suite command** | `cd firestarter_app && pytest tests/ -q` (regression baseline) |
| **Estimated runtime** | <2 seconds (pure grep + git diff; no network) |

---

## Sampling Rate

- **After file creation commit:** Run all grep assertions on `beta-release.yml`
- **After commit lands:** Run `git diff` against `release.yml` / `publish.yml` / `ci.yml` — all must be empty
- **Phase gate:** Existing 77-test pytest suite still green (no regression)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD-yml | 16-01 | 1 | REL-01 | — | beta-release.yml contains prerelease+make_latest+workflow_dispatch+fetch-depth | smoke | `for k in 'prerelease: true' 'make_latest: false' 'fetch-depth: 0' 'beta_version' 'BETA_VERSION:' 'branches:' 'beta'; do grep -q "$k" firestarter_app/.github/workflows/beta-release.yml || exit 1; done` | ❌ W0 | ⬜ pending |
| TBD-gate-release | 16-01 | 1 | GATE-01 | — | release.yml byte-identical | git-diff | `cd firestarter_app && git diff HEAD~1 -- .github/workflows/release.yml \| wc -l` returns 0 | n/a | ⬜ pending |
| TBD-gate-publish | 16-01 | 1 | GATE-01 | — | publish.yml byte-identical | git-diff | `cd firestarter_app && git diff HEAD~1 -- .github/workflows/publish.yml \| wc -l` returns 0 | n/a | ⬜ pending |
| TBD-gate-ci | 16-01 | 1 | GATE-01 | — | ci.yml byte-identical | git-diff | `cd firestarter_app && git diff HEAD~1 -- .github/workflows/ci.yml \| wc -l` returns 0 | n/a | ⬜ pending |
| TBD-yamllint | 16-01 | 1 | REL-01 | — | beta-release.yml is valid YAML (parses cleanly) | smoke | `python3 -c "import yaml; yaml.safe_load(open('firestarter_app/.github/workflows/beta-release.yml'))"` | ❌ W0 | ⬜ pending |
| TBD-regression | 16-01 | 1 | REL-01 / GATE-01 | — | Existing 77-test pytest suite still passes | unit (regression) | `cd firestarter_app && pytest tests/ -q` exit 0 | ✓ exists | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/.github/workflows/beta-release.yml` — the single deliverable file
- No new Python code; no new test files; no new pytest infrastructure

*Single-file YAML phase. Verification entirely via shell assertions on the new file + git diff on the three preserved files.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real GitHub Actions trigger on push to `beta` branch | REL-01 | Requires actually pushing to GitHub; CI-environment only | Phase 20 E2E-01 (a)+(b) exercises this end-to-end |
| Real PyPI publish of a `X.Y.ZbN` package | REL-01 | Requires PyPI credentials + a clean test version line | Phase 20 E2E-01 (a) |
| `pip install --pre firestarter==X.Y.ZbN` against real PyPI | REL-01 | Live network + clean Python env | Phase 20 E2E-01 (a) |
| `gh workflow run beta-release.yml --ref beta -f beta_version=X.Y.ZbN` UI behavior | REL-01 | Requires GitHub UI / CLI auth | Phase 20 E2E-01 + Phase 19 release-procedures doc |

*Phase 16 deliverable is a workflow file; the actual workflow execution against real GitHub + PyPI is intentionally deferred to Phase 20 E2E-01. Phase 16 verification is structural (file content + non-regression of preserved files).*

---

## Validation Sign-Off

- [x] All verification commands are `<automated>` shell assertions (verified at planning time)
- [x] Sampling continuity: single task; automated verify present (verified)
- [x] Wave 0 covers the MISSING reference (the new YAML file) — verified
- [x] No watch-mode flags (single-shot grep + git diff)
- [x] Feedback latency < 2s (no network)
- [x] `nyquist_compliant: true` (set in frontmatter)

**Approval:** signed-off (pre-execution boxes verified at planning time). `wave_0_complete: false` flips after execution.

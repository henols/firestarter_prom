---
phase: 17
slug: firmware-beta-release-pipeline
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-20
---

# Phase 17 — Validation Strategy

> Single-file YAML deliverable. Verification = shell-level grep + git-diff assertions on the new file + regression of existing tests.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | shell assertions (`grep`, `git diff`, `python3 -c "import yaml"`) + existing `pio test -e native` + pytest regression |
| **Quick run command** | inline `<automated>` block in PLAN.md verify section |
| **Full suite command** | `cd firestarter && pytest tests/ -q` (pytest regression) + `cd firestarter && pio test -e native` (Unity regression) |
| **Estimated runtime** | <5 seconds (grep + git diff; pytest is ~1s; native Unity is ~3s) |

---

## Sampling Rate

- **After file creation commit:** Run all grep + YAML-parse assertions on `beta-build.yml`
- **GATE-02 check:** `git -C firestarter diff` over `build.yml` returns empty
- **Phase gate:** `pytest tests/ -q` + `pio test -e native` both pass

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD-yml | 17-01 | 1 | REL-02 | — | beta-build.yml contains prerelease+make_latest+workflow_dispatch+fetch-depth+pio test+pio run | smoke | `for k in 'prerelease: true' 'make_latest: false' 'fetch-depth: 0' 'beta_version' 'BETA_VERSION:' 'pio test -e native' 'pio run' 'firestarter_*.hex' 'branches:' 'beta'; do grep -q "$k" firestarter/.github/workflows/beta-build.yml \|\| exit 1; done` | ❌ W0 | ⬜ pending |
| TBD-gate-build | 17-01 | 1 | GATE-02 | — | build.yml byte-identical | git-diff | `cd firestarter && git diff HEAD~1 -- .github/workflows/build.yml \| wc -l` returns 0 | n/a | ⬜ pending |
| TBD-yamllint | 17-01 | 1 | REL-02 | — | beta-build.yml is valid YAML | smoke | `python3 -c "import yaml; yaml.safe_load(open('firestarter/.github/workflows/beta-build.yml'))"` | ❌ W0 | ⬜ pending |
| TBD-no-vestige | 17-01 | 1 | REL-02 | — | NEW file does NOT replicate build.yml's vestigial @v4 setup-python step | smoke (negative) | `grep -c 'actions/setup-python@v4' firestarter/.github/workflows/beta-build.yml` returns 0 | ❌ W0 | ⬜ pending |
| TBD-no-token | 17-01 | 1 | REL-02 | — | Checkout step has NO `token:` override (anti-loop) | smoke (negative) | extract checkout step from YAML; assert no `token:` key | ❌ W0 | ⬜ pending |
| TBD-regression-pytest | 17-01 | 1 | GATE-02 | — | Existing pytest suite still passes | unit (regression) | `cd firestarter && pytest tests/ -q` exit 0 | ✓ exists | ⬜ pending |
| TBD-regression-unity | 17-01 | 1 | GATE-02 | — | Existing native Unity tests still pass | unit (regression) | `cd firestarter && pio test -e native` exit 0 | ✓ exists | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/.github/workflows/beta-build.yml` — the single deliverable
- No new test infrastructure; no new Python/C++ code

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real GitHub Actions trigger on push to `beta` | REL-02 | Live CI environment required | Phase 20 E2E-01 (c) |
| Real GitHub Pre-release creation with `.hex` artifacts | REL-02 | Live GitHub API | Phase 20 E2E-01 (c) |
| Lockstep version match with app's `X.Y.ZbN` | REL-02 + VER-03 derivative | Cross-repo coordination | Phase 20 E2E-01 (d) |
| Phase 18 `firestarter fw -i --pre` consuming real beta `.hex` | INST-02 E2E | Real network + real firmware | Phase 20 E2E-01 (e) |

---

## Validation Sign-Off

- [x] All verification commands are `<automated>` shell assertions
- [x] Sampling continuity: single task; automated verify present
- [x] Wave 0 covers MISSING reference (the new YAML file)
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** signed-off at planning time. `wave_0_complete` flips after execution.

---
phase: 22
slug: release-pipeline-artifacts
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-20
---

# Phase 22 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | PlatformIO matrix build + Unity native tests (existing infra; no new harness) |
| **Config file** | `firestarter/platformio.ini` (the line being edited) |
| **Quick run command** | `cd firestarter && pio run` (bare — picks up `default_envs`) |
| **Full suite command** | `cd firestarter && pio run && pio test -e native -f "*test_dispatch*" -f "*test_messages*"` |
| **Estimated runtime** | ~30 s matrix build (3 envs incremental) + ~4 s native tests |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter && pio run` and confirm all 3 hex artifacts exist at `.pio/build/{uno,uno328pb,leonardo}/firestarter_{uno,uno328pb,leonardo}.hex`
- **After every plan wave:** Full suite — matrix build + native tests + `cmp -s` against Phase 21 baselines
- **Before `/gsd-verify-work`:** Full suite green; ROADMAP SC#1 literal == `default_envs` literal (text-equal sanity)
- **Max feedback latency:** ~40 s

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 22-XX-XX | TBD | 1 | REL-01 / REL-02 | — | N/A (build config only) | build + glob | `cd firestarter && pio run && shopt -s globstar && ls .pio/build/**/firestarter_*.hex \| wc -l` (must = 3) | ✅ (existing infra) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Per-task rows will be filled in by the planner once PLAN.md files are emitted.*

---

## Wave 0 Requirements

- [ ] No new test files needed — Phase 21's baselines at `.planning/v1.5/baselines/` are the GATE-01 anchors and already exist.
- [ ] No new framework install — PlatformIO + Unity already in use.
- [ ] The post-edit verification gate uses Phase 21's `cmp -s` pattern verbatim.

*"Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Stable GitHub Release asset list shows three `.hex` files | REL-01 | Requires an actual push to `firestarter/main` + a stable cut to verify end-to-end | Defer to a future milestone (post-v1.5 merge-up to `main`). Phase 22 substrate is dry-run-verified; not gated on this manual step. |
| Beta GitHub Pre-release asset list shows three `.hex` files | REL-02 | Requires the first real beta cut from `firestarter/beta` to verify end-to-end | Phase 24 (Bench Validation) triggers this naturally by merging `v1.5-uno328pb` → `firestarter/beta`. Phase 22 ships before this; verification of the asset list is recorded in `.planning/v1.5-BENCH-RESULTS.md` per BENCH-01. |
| `prerelease: true` + `make_latest: false` preserved on the new beta pre-release | REL-02 (preservation clause) | Visible only on the live GitHub Pre-release page | Operator inspects the GitHub Pre-release UI after Phase 24's cut. Phase 22 does NOT touch the `prerelease:` / `make_latest:` lines in `beta-build.yml` (D-03 — no workflow edits), so preservation is structurally guaranteed. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify commands (build + glob + cmp -s + native test)
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (each task is verifiable in isolation)
- [ ] Wave 0 covers all MISSING references (none — Phase 21 baselines are the Wave 0 substrate)
- [ ] No watch-mode flags
- [ ] Feedback latency < 45 s
- [ ] `nyquist_compliant: true` set in frontmatter after planner fills per-task rows

**Approval:** pending

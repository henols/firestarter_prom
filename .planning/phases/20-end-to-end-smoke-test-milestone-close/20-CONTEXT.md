# Phase 20: End-to-End Smoke Test + Milestone Close - Context

**Gathered:** 2026-05-20
**Status:** Ready for planning
**Discussion mode:** `--auto --chain`

<domain>
## Phase Boundary

The milestone acceptance gate. Two requirements:

1. **E2E-01:** Cut a real beta build in both sub-repos following `.planning/v1.4-RELEASE-PROCEDURES.md` (Phase 19 deliverable). Verify end-to-end: PyPI shows `X.Y.ZbN`, `pip install --pre firestarter==X.Y.ZbN` works, firmware GitHub Pre-release page shows expected `.hex` artifacts, version strings match per VER-03, `firestarter fw -i --pre` (or `--firmware-version X.Y.ZbN`) installs the matching firmware via Phase 18's downloader, AND stable-installed `firestarter fw -i` on a SEPARATE fresh stable install still downloads stable firmware (INST-01 non-regression).

2. **MS-01:** Update `.planning/MILESTONES.md` with v1.4 summary, archive phase directories under `.planning/milestones/v1.4-phases/`, refresh `PROJECT.md` Active Milestone footer.

**Critical constraint:** E2E-01 inherently requires LIVE network operations (real `gh workflow run`, real PyPI publish, real `pip install --pre` from a fresh Python environment, real GitHub Pre-release creation). These cannot be executed in the planning environment. Phase 20's planning-side deliverable is:
- An OPERATOR CHECKLIST (`20-HUMAN-UAT.md`) the operator follows step-by-step
- An AUTOMATED VERIFIER (`.planning/v1.4-e2e-verify.sh`) the operator runs AFTER the cut to mechanically confirm all sub-criteria
- The MILESTONE CLOSE artifacts (MILESTONES.md entry, archive script, PROJECT.md text) prepared as drafts that finalize once the operator confirms E2E-01 green

**In scope (Phase 20):**
- `.planning/phases/20-*/20-HUMAN-UAT.md` — operator checklist with the 6 E2E-01 sub-criteria from REQUIREMENTS.md verbatim.
- `.planning/v1.4-e2e-verify.sh` — bash script that mechanically verifies each E2E-01 sub-criterion against the live state (PyPI API, GitHub Releases API, local install in tmp venv, firmware install). Operator runs this once after the cut.
- `.planning/MILESTONES.md` — append v1.4 milestone summary (in v1.0/v1.2 style).
- `.planning/v1.4-archive.sh` — bash script that moves `.planning/phases/{15..20}-*` to `.planning/milestones/v1.4-phases/` (mirrors v1.2 archive pattern from MILESTONES.md history).
- `PROJECT.md` — update Active Milestone footer to reflect v1.4 ship state; do NOT preemptively name a next milestone.

**Out of scope:**
- Actually executing the live beta cut (operator work; happens outside the planning environment).
- Auto-promotion workflow beta → stable (deferred per REQUIREMENTS.md Future Requirements; manual fast-forward merge is documented in v1.4-RELEASE-PROCEDURES.md).
- v1.5 milestone planning (`PROJECT.md` does NOT preemptively name a next milestone).
- Cleanup of pre-existing technical debt (e.g., `.editorconfig/**` glob — deferred per Phase 17 code review WR-01).

</domain>

<decisions>
## Implementation Decisions

### A. Plan Structure

- **D-01:** Single plan, two tasks:
  - **Task 1 — E2E-01 substrate:** write `20-HUMAN-UAT.md` (operator checklist) + `v1.4-e2e-verify.sh` (automated verifier). Both reference the 6 E2E-01 sub-criteria (a-f) from REQUIREMENTS.md verbatim.
  - **Task 2 — MS-01 close artifacts (draft):** write the v1.4 entry for `MILESTONES.md`, write `v1.4-archive.sh`, update `PROJECT.md` Active Milestone footer. These are DRAFTS that finalize after operator confirms E2E-01 green via `gsd-audit-uat` against `20-HUMAN-UAT.md`.

### B. HUMAN-UAT.md Location and Structure

- **D-02:** `20-HUMAN-UAT.md` lives at `.planning/phases/20-end-to-end-smoke-test-milestone-close/20-HUMAN-UAT.md`. Standard GSD UAT template:
  ```yaml
  ---
  status: partial
  phase: 20-end-to-end-smoke-test-milestone-close
  source: [20-VERIFICATION.md]
  started: 2026-05-20
  updated: 2026-05-20
  ---
  ```
- **D-03:** Test list (6 tests = E2E-01 sub-criteria a-f from REQUIREMENTS.md):
  1. PyPI shows `X.Y.ZbN` pre-release version on the firestarter project page
  2. `pip install --pre firestarter==X.Y.ZbN` installs cleanly from a fresh Python env on macOS or Linux
  3. Firmware GitHub Releases page shows the build marked `Pre-release` (not `Latest`) with expected `firestarter_*.hex` artifacts per board
  4. Both repos' beta release tags carry the same `X.Y.ZbN` string per VER-03
  5. Beta-installed app's `firestarter fw -i --pre` downloads the matching `X.Y.ZbN` firmware `.hex` for the configured board (proves INST-02 E2E)
  6. SEPARATE fresh stable install (`pip install firestarter==X.Y.Z` of previous stable) — `firestarter fw -i` downloads stable firmware, NOT the new beta (proves INST-01 non-regression)

### C. e2e-verify.sh Location and Behavior

- **D-04:** `.planning/v1.4-e2e-verify.sh` (meta-repo). Reasoning: operator-runnable from any meta-repo clone; outlives Phase 20's directory.
- **D-05:** Behavior: takes `BETA_VERSION` as positional arg (e.g. `bash .planning/v1.4-e2e-verify.sh 0.0.1b1`). Runs:
  1. `curl https://pypi.org/pypi/firestarter/json` → grep for `X.Y.ZbN` in releases
  2. `gh release view X.Y.ZbN -R henols/firestarter --json isPrerelease,isLatest,assets` → assert prerelease=true, isLatest=false, asset list contains both `firestarter_uno.hex` and `firestarter_leonardo.hex`
  3. Lockstep check: `gh release view X.Y.ZbN -R henols/firestarter_app --json tagName` AND `gh release view X.Y.ZbN -R henols/firestarter --json tagName` — assert string-equal (per VER-03 + Phase 15 D-01)
  4. Optional dry-run check: invoke `firestarter fw --list --pre` against the installed beta app and assert the new `X.Y.ZbN` row appears
  5. Exit 0 on all-green; non-zero with explicit failure summary otherwise
- **D-06:** Steps 5 and 6 of D-03 (pip install + firestarter fw -i) are HUMAN-UAT items (require real install + flash hardware), not script-automatable. e2e-verify.sh covers the API-level checks only.

### D. MILESTONES.md v1.4 Entry Content

- **D-07:** Match the structural shape of v1.0 and v1.2 entries in `.planning/MILESTONES.md`. Sections: Delivered (what shipped), Stats (phase/plan counts + commit counts across both submodules + meta-repo), Key Decisions (lockstep mechanism, trigger model, magic default, PEP 440 vs alternatives, scope amendment that added Phase 18), Known Gaps (auto-promotion, branch protection, signed artifacts — pointers to Future Requirements), Hardware impact (none — software-only milestone).

### E. Archive Script

- **D-08:** `.planning/v1.4-archive.sh` (meta-repo). Action: `mkdir -p .planning/milestones/v1.4-phases/ && mv .planning/phases/15-* .planning/phases/16-* .planning/phases/17-* .planning/phases/18-* .planning/phases/19-* .planning/phases/20-* .planning/milestones/v1.4-phases/`. Mirrors the v1.2 cleanup pattern (referenced in PROJECT.md line 47).
- **D-09:** Run sequence: archive script → commit move (`refactor: archive v1.4 phase directories`) → operator can run from any clone.

### F. PROJECT.md Update

- **D-10:** Update PROJECT.md `Active milestone` footer to reflect v1.4 ship state. Pattern: replace `Active milestone: v1.4 — Beta & Pre-release Deployment Pipeline (started 2026-05-20)` with `**v1.4 shipped: <DATE>** (Beta & Pre-release Deployment Pipeline — 6 phases, 16/16 requirements)`. Add the v1.4 milestone entry to the "Current State" section if needed.
- **D-11:** Do NOT preemptively name a next milestone. The next milestone is whatever the operator decides AFTER v1.4 ships (could be v1.3 resume, could be v1.5 auto-promotion, could be neither).

### G. E2E Test Version Identifier

- **D-12:** Operator picks the `BETA_VERSION` at execution time (not pre-baked into the checklist). HUMAN-UAT.md instructs:
  - Check current stable version line: `pip show firestarter` (current latest stable) + `cat firestarter/include/version.h`
  - Pick a `BETA_VERSION` of form `X.Y.ZbN` that does NOT conflict with any existing stable or beta tag in EITHER repo
  - Suggested defaults: `0.0.1b1` (clean version line — guaranteed no conflict) OR next-minor `(major).(minor+1).0b1` (semantic intent: pre-release of next minor)
  - Recommended for FIRST E2E run: `0.0.1b1` (zero risk of disrupting current users on stable line)

### H. Operator Acceptance Criteria

- **D-13:** Phase 20 is considered green ONLY when ALL of:
  1. All 6 HUMAN-UAT.md tests result `pass`
  2. `bash .planning/v1.4-e2e-verify.sh <BETA_VERSION>` exits 0
  3. MILESTONES.md v1.4 entry committed
  4. v1.4-archive.sh executed and phase dirs moved
  5. PROJECT.md updated to ship state
- **D-14:** `gsd-audit-uat 20` surfaces HUMAN-UAT.md pending items in `/gsd-progress` until the operator confirms each test as `pass` / `issue`. When all pass + verifier-script green + archive done → Phase 20 close.

### I. Deferred Items in MILESTONES.md

- **D-15:** v1.4 MILESTONES.md entry explicitly enumerates deferred items as POINTERS to REQUIREMENTS.md Future Requirements:
  - Auto-promotion beta → stable workflow (Future Requirements)
  - Branch protection rules on `beta` branch (Future Requirements)
  - Signed release artifacts (Future Requirements)
  - TestPyPI publishing (Future Requirements)
  - Cleanup of pre-existing build.yml technical debt (Phase 17 WR-01 — vestigial setup-python@v4 + `.editorconfig/**` glob)
  - Cleanup of pre-existing update_version.py technical debt (Phase 18 CR-01..CR-03 — atomic file write, none-return crash, rc-series tag fallback)
  - Cleanup of `_dev` / `-dev` suffix conventions (Phase 15 D-25)

### J. First-Run Verdict

- **D-16:** Phase 20 verifier on initial planning run returns `status: human_needed` (NOT `passed`). E2E-01 verification cannot complete in the planning environment — it requires live network + operator action. HUMAN-UAT.md persists with `status: partial` until operator runs the cut + the verifier script + confirms each test.
- **D-17:** This is consistent with the project's existing `human_needed` pattern from v1.2 Phase 08/09 + v1.3 Phase 12 — the GSD workflow already handles this gracefully via `/gsd-audit-uat`.

### Claude's Discretion

- **D-18:** Whether e2e-verify.sh should bundle a "quick smoke" mode that runs all API checks without the operator-driven install steps — recommended yes; default is full check, `--quick` flag skips the install-prompt branches.
- **D-19:** Whether v1.4-archive.sh should accept a `--dry-run` flag for operator review before actually moving directories — recommended yes (low cost; matches project's caution culture).
- **D-20:** Whether MILESTONES.md should include a "v1.4 timeline" mini-chart (start: 2026-05-20; phases shipped: 2026-05-20) — recommended NO (the timeline is degenerate since everything shipped same-day; not informative).

</decisions>

<canonical_refs>
## Canonical References

### Milestone planning artifacts
- `.planning/PROJECT.md` — Active milestone footer to update.
- `.planning/REQUIREMENTS.md` §E2E (E2E-01) §MS (MS-01) — the 6 sub-criteria of E2E-01 + the milestone-close requirements.
- `.planning/ROADMAP.md` §"Phase 20: End-to-End Smoke Test + Milestone Close" — full success criteria.
- `.planning/STATE.md` §"v1.4 Decisions"
- `.planning/MILESTONES.md` — file to append v1.4 entry to. v1.0, v1.2 entries are style templates.

### Phase 15-19 deliverables (load-bearing — what Phase 20 verifies)
- `firestarter_app/.github/workflows/beta-release.yml` (Phase 16)
- `firestarter/.github/workflows/beta-build.yml` (Phase 17)
- `firestarter_app/firestarter/firmware.py` + `main.py` (Phase 18 CLI surface)
- `.planning/v1.4-RELEASE-PROCEDURES.md` (Phase 19 — the procedure the operator follows during E2E)
- `.planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md` (Phase 19 D-07 fix applied)

### Files to create
- `.planning/phases/20-end-to-end-smoke-test-milestone-close/20-HUMAN-UAT.md` (operator checklist)
- `.planning/v1.4-e2e-verify.sh` (automated verifier)
- `.planning/v1.4-archive.sh` (archive script)

### Files to modify
- `.planning/MILESTONES.md` (append v1.4 entry)
- `.planning/PROJECT.md` (Active milestone → ship state)

### External tooling required by operator (not by planner)
- `gh` CLI authenticated with write access to henols/firestarter_app + henols/firestarter
- Operator-accessible PyPI account (only needed for the cut, not for verification — PyPI API is public)
- Clean Python venv for E2E-01 sub-criterion (b)
- (Optionally) RURP hardware for E2E-01 sub-criterion (e) firmware install — but the install command can be exercised without actually flashing if the operator chooses

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`.planning/MILESTONES.md` v1.0 / v1.2 entries** — structural template for the v1.4 entry. Same section headers.
- **`.planning/phases/15-*/lockstep-dryrun-fixture.sh`** — Phase 15 fixture pattern. Phase 20's `v1.4-e2e-verify.sh` follows the same self-contained bash + curl + gh structure.
- **`gsd-audit-uat`** — existing GSD command that surfaces HUMAN-UAT.md items in `/gsd-progress`. Phase 20 follows the v1.2 Phase 08/09 + v1.3 Phase 12 precedent.

### Established Patterns

- **HUMAN-UAT.md YAML frontmatter** — `status: partial` → `status: passed`/`status: human_needed` lifecycle. Test entries with `result: pending` → `pass` / `issue` after operator confirms.
- **`gh` CLI for GitHub API** — used in Phase 15-LOCKSTEP-PROCEDURE.md; reused here.
- **bash + `curl` for PyPI JSON API** — straightforward; PyPI's JSON endpoint at `https://pypi.org/pypi/{pkg}/json` is unauthenticated.

### Integration Points

- **Phase 18's `firestarter fw -i --pre`** — invoked in E2E sub-criterion (e). The phase 18 downloader's GitHub API mocking is replaced with real network in Phase 20.
- **Phase 18's `firestarter fw -i` (no flags) on stable install** — invoked in E2E sub-criterion (f) for INST-01 non-regression.
- **`v1.4-RELEASE-PROCEDURES.md` (Phase 19)** — operator follows this verbatim. The HUMAN-UAT.md checklist references it line-by-line.

</code_context>

<specifics>
## Specific Ideas

- **`human_needed` is the correct first-run verdict.** The GSD workflow gracefully handles this via HUMAN-UAT.md persistence + `gsd-audit-uat` resurfacing. No surprise; matches the v1.2 Phase 08/09 + v1.3 Phase 12 pattern.
- **Don't pre-bake a specific BETA_VERSION into the checklist.** The operator chooses at execution time based on the current state of both repos' tag namespaces. Pre-baking risks tag-conflict if Phase 20 takes weeks to actually execute.
- **`v1.4-archive.sh` is a script, not a one-shot Bash command in the plan.** Reason: the move is conditional on E2E-01 green; the operator runs the script AFTER the verification, not during plan execution.
- **`PROJECT.md` Active Milestone update is the SHIP-STATE update**, not a milestone-archive update. The v1.4 entry stays in the `## Current Milestone: v1.4` section but the header flips to past-tense ("**v1.4 shipped:**" + date).

</specifics>

<deferred>
## Deferred Ideas

- Auto-promotion beta → stable (Future Requirements).
- Branch protection rules on `beta` (Future Requirements).
- Signed release artifacts (Future Requirements).
- TestPyPI publishing channel (Future Requirements).
- Pre-existing build.yml technical debt cleanup (Phase 17 WR-01).
- Pre-existing update_version.py code-review findings cleanup (Phase 18 CR-01..CR-03).
- `_dev` / `-dev` suffix convention cleanup (Phase 15 D-25).
- v1.5 milestone planning — operator-driven after Phase 20 ships; not preemptively scoped.
- Per-board fallback when `--pre` finds release with assets for one board but not another (Phase 18 deferred).
- Cached firmware download / offline install (Phase 18 deferred).
- Cross-repo metrics dashboard (Future Requirements).

</deferred>

---

*Phase: 20-end-to-end-smoke-test-milestone-close*
*Context gathered: 2026-05-20*
*Discussion mode: --auto --chain*

# Phase 19: Documentation - Context

**Gathered:** 2026-05-20
**Status:** Ready for planning
**Discussion mode:** `--auto --chain`

<domain>
## Phase Boundary

Document the v1.4 beta channel for end users (operators of the app + firmware) AND for the release engineer (who cuts the beta builds). Three artifacts:

1. **`firestarter_app/README.md`** — new "Beta / Pre-release Channel" section covering app install (`pip install --pre firestarter`), firmware install via Phase 18's flags (`firestarter fw -i --pre`, `firestarter fw -i --firmware-version X.Y.ZbN`, `firestarter fw --list`), stability guarantee, issue reporting.
2. **`firestarter/README.md`** — short "Beta channel" section covering the GitHub Pre-release page (filter view), the app-side install path (with link to app README's beta section), stability guarantee, issue reporting.
3. **`.planning/v1.4-RELEASE-PROCEDURES.md`** (meta-repo) — release-engineer workflow for cutting a beta in both sub-repos. Consumes `15-LOCKSTEP-PROCEDURE.md` verbatim + documents the Phase 16 `gh workflow run beta-release.yml --ref beta -f beta_version=X.Y.ZbN` + Phase 17 `gh workflow run beta-build.yml --ref beta -f beta_version=X.Y.ZbN` invocations + the manual promotion path (fast-forward merge beta → main; auto-promotion deferred per REQUIREMENTS.md).

Plus a small fix to `15-LOCKSTEP-PROCEDURE.md` Step 4 (replace `release.yml` reference with `beta-release.yml` — Phase 16 RESEARCH Open Q2 resolution).

**In scope (Phase 19):**
- Three documentation files (one in each sub-repo + one in meta-repo).
- One small edit to `15-LOCKSTEP-PROCEDURE.md` (Step 4 reference fix).
- All other artifacts (workflows, scripts, code) stay untouched.

**Out of scope:**
- Code changes (no app/firmware behavior modifications).
- Phase 20 E2E + milestone close.
- Auto-promotion workflow (deferred per REQUIREMENTS.md).
- Branch protection / signed artifacts / TestPyPI (deferred).
- Edits to other v1.0/v1.2/v1.3 docs.

</domain>

<decisions>
## Implementation Decisions

### A. App README — Section Placement (DOC-01)

- **D-01:** Add new "Beta / Pre-release Channel" section in `firestarter_app/README.md` AFTER the "Installing the Firestarter Python Program" subsection and BEFORE "Installing the Firmware on the Arduino" (so it sits naturally alongside the existing install instructions). Add a Table-of-Contents entry under "Installation".
- **D-02:** Section structure:
  ```markdown
  ## Beta / Pre-release Channel
  
  ### Installing the beta app
  pip install --pre firestarter  (worked example with `firestarter --version` sanity check)
  
  ### Installing beta firmware
  `firestarter fw -i --pre` (worked example output)
  `firestarter fw -i --firmware-version X.Y.ZbN` (exact-tag pin example)
  `firestarter fw --list` (table example output) / `firestarter fw --list --json`
  Note on the magic default: on a beta-installed app, bare `firestarter fw -i` auto-routes to --pre.
  
  ### Stability guarantee
  Explicit no-guarantees wording (D-09).
  
  ### Reporting issues against a beta build
  - which version identifiers to cite (app: `pip show firestarter`; firmware: `firestarter fw --list` or handshake string)
  - GitHub Issues link with template
  ```

### B. Firmware README — Section Placement (DOC-02)

- **D-03:** firmware README is currently very short (license + pointer). Add a new "Beta / Pre-release Channel" section AFTER the existing pointer text and BEFORE the License section. Short section — primary install path is via the app's `--pre` flag (cross-reference); secondary path is direct download from GitHub Releases page filtered to "Pre-release."
- **D-04:** Section structure:
  ```markdown
  ## Beta / Pre-release Channel
  
  Pre-release firmware `.hex` builds are published as GitHub Pre-releases (tagged X.Y.ZbN, marked "Pre-release", NOT marked "Latest"). Two install paths:
  
  1. **Via the app (recommended):** `firestarter fw -i --pre` — see [firestarter_app README beta section](link).
  2. **Direct download:** GitHub Releases page → filter by "Pre-release" → download `firestarter_{board}.hex`.
  
  Stability: no guarantees; for testing pre-release features only.
  
  Reporting issues: cite firmware version (X.Y.ZbN from `include/version.h` or `firestarter fw --list` output), commit SHA, board, chip.
  ```

### C. Release Procedures Doc Location (DOC-03)

- **D-05:** File: `.planning/v1.4-RELEASE-PROCEDURES.md` in the META-REPO (not a sub-repo). Justification: cross-repo coordination doc; consumes both app and firmware workflows; sits naturally alongside `15-LOCKSTEP-PROCEDURE.md`.

### D. Release Procedures Content

- **D-06:** `v1.4-RELEASE-PROCEDURES.md` structure:
  ```markdown
  # v1.4 Release Procedures
  
  ## Overview
  Three release types: stable (main → auto via release.yml/build.yml), beta (beta → workflow_dispatch via beta-release.yml/beta-build.yml), and promotion (beta → stable via fast-forward merge).
  
  ## Prerequisites
  - gh CLI authenticated with write access to henols/firestarter_app + henols/firestarter
  - Local clone of both sub-repos
  - Operator decided on the X.Y.ZbN version per PEP 440 (b1, b2, ..., rc1, rc2)
  
  ## Cutting a beta (lockstep)
  Verbatim copy of 15-LOCKSTEP-PROCEDURE.md §Procedure with these corrections + augmentations:
  - Step 4 of 15-LOCKSTEP-PROCEDURE.md says "release.yml" — should be "beta-release.yml"; fix inline.
  - App invocation: gh workflow run beta-release.yml --ref beta -f beta_version=X.Y.ZbN -R henols/firestarter_app
  - Firmware invocation: gh workflow run beta-build.yml --ref beta -f beta_version=X.Y.ZbN -R henols/firestarter
  - Post-cut verification table (PyPI, GitHub Pre-release, app install, firmware install)
  
  ## Verifying a beta
  - `pip install --pre firestarter==X.Y.ZbN` (clean Python env)
  - `firestarter --version` matches X.Y.ZbN
  - `firestarter fw -i --pre` (or `--firmware-version X.Y.ZbN`) installs firmware
  - Stable-installed app's `firestarter fw -i` still installs stable (non-regression check)
  
  ## Promoting beta → stable (manual)
  - Currently manual: cherry-pick / fast-forward merge from beta to main; let main's existing release.yml/build.yml produce the stable cut
  - Auto-promotion workflow deferred to v1.5+ (per REQUIREMENTS.md Future Requirements)
  
  ## Failure recovery
  - Inherit 15-LOCKSTEP-PROCEDURE.md §Failure recovery verbatim
  - If one repo's workflow_dispatch run fails after the other succeeded, re-trigger the failed repo with the SAME BETA_VERSION (idempotent re-publish is a known gap — Phase 15 D-03)
  
  ## Known gaps
  - Auto-promotion deferred (v1.5+)
  - Branch protection on `beta` deferred (Future Requirements)
  - Signed artifacts deferred (Future Requirements)
  - Idempotent re-publish on partial failure: manual re-trigger only (Phase 15 D-03)
  ```

### E. Fix to 15-LOCKSTEP-PROCEDURE.md

- **D-07:** Update `15-LOCKSTEP-PROCEDURE.md` Step 4 — replace any occurrence of `release.yml` with `beta-release.yml` (the actual Phase 16 deliverable). Phase 16 RESEARCH Open Q2 resolution. Also confirm the firmware-side reference uses `beta-build.yml` (the Phase 17 deliverable).

### F. Stability Guarantee Wording

- **D-08:** Both READMEs use the SAME wording for the stability guarantee:
  > **⚠ No stability guarantees.** Beta builds are intended for testing pre-release features. They may contain bugs, may change without notice, or may be withdrawn. For production / hardware-bench use, install the stable release.

### G. Issue Reporting Template

- **D-09:** Both READMEs reference GitHub Issues with required fields:
  - Beta version identifier (`X.Y.ZbN` from `pip show firestarter` for app, from `firestarter fw --list` or handshake string for firmware)
  - Board (Uno / Leonardo / other)
  - OS (macOS / Linux / Windows)
  - For hardware-related issues: chip part number + manufacturer
  - Full stderr / traceback for crashes
  - Repro steps
  - Use existing GitHub Issue URLs (no new issue templates added in this phase).

### Claude's Discretion

- **D-10:** Exact placement of the Table-of-Contents entry — planner picks the natural alphabetical/structural slot.
- **D-11:** Whether to add a small "Channel Selection Matrix" table summarizing stable vs beta install commands — recommended yes (operator-friendly).
- **D-12:** Whether to link FROM the firmware README to specific commits / docs — recommended keep it light (existing README is intentionally minimal).
- **D-13:** Whether `v1.4-RELEASE-PROCEDURES.md` includes a Mermaid diagram of the release flow — recommended NO (text is sufficient; Mermaid renders inconsistently in GitHub).

</decisions>

<canonical_refs>
## Canonical References

### Milestone planning artifacts
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md` §DOC (DOC-01, DOC-02, DOC-03)
- `.planning/ROADMAP.md` §"Phase 19: Documentation"
- `.planning/STATE.md` §"v1.4 Decisions"

### Phase 15..18 deliverables (load-bearing — what we document)
- `.planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md` — Phase 15 deliverable. Phase 19's `v1.4-RELEASE-PROCEDURES.md` consumes this verbatim + corrects Step 4's release.yml reference per Phase 16 RESEARCH Open Q2.
- `firestarter_app/.github/workflows/beta-release.yml` — Phase 16 deliverable. Doc references the `gh workflow run` invocation.
- `firestarter/.github/workflows/beta-build.yml` — Phase 17 deliverable. Doc references the `gh workflow run` invocation.
- `firestarter_app/firestarter/main.py` + `firmware.py` — Phase 18 deliverables. Doc references `--pre`, `--firmware-version`, `--list`, `--json`, `--stable` flags + magic default behavior.

### Files to modify
- `firestarter_app/README.md` — add Beta channel section (DOC-01).
- `firestarter/README.md` — add Beta channel section (DOC-02).
- `.planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md` — fix Step 4 reference (D-07).

### Files to create
- `.planning/v1.4-RELEASE-PROCEDURES.md` (DOC-03).

### Existing READMEs (read-only template reference)
- `firestarter_app/README.md` — existing structure (Installation → Usage → Commands → Examples). Phase 19 inserts the new section between Installation subsections.
- `firestarter/README.md` — existing minimal structure (logo + pointer + License). Phase 19 inserts a Beta channel section before License.

### Phase 20 contract
- Phase 20 E2E-01 follows the procedure documented here. Phase 19's `v1.4-RELEASE-PROCEDURES.md` must be detailed enough that Phase 20's operator can execute end-to-end without reading any other doc.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`firestarter_app/README.md` existing Table of Contents** (lines 27-58) — structural anchor for the new beta section's TOC entry.
- **`firestarter_app/README.md` Installation section** (after TOC) — natural insertion point for the new "Beta / Pre-release Channel" subsection.
- **`firestarter/README.md`** — currently 15 lines of pointer-content. Light additive section.
- **`.planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md`** — 297 lines of operator procedure. Phase 19 consumes / extends in `v1.4-RELEASE-PROCEDURES.md`.

### Established Patterns

- **Markdown style** — both READMEs use H2/H3 hierarchy, fenced code blocks with language tags, badge images at top.
- **Cross-repo links** — firmware README links to app README and the RURP hardware project. Phase 19 follows this pattern.

</code_context>

<specifics>
## Specific Ideas

- **Magic default surprise prevention:** the app README's beta section MUST explicitly explain the magic default (D-21 in Phase 18 CONTEXT). Otherwise operators on a beta-installed app would be confused by automatic --pre routing. The INFO log explains it at runtime; the README explains it at install time.
- **Cross-link strategy:** firmware README's beta section is intentionally SHORT and links to the app README's beta section for the install commands. Single source of truth for the install procedure.
- **`v1.4-RELEASE-PROCEDURES.md` is the Phase 20 substrate:** Phase 20's E2E test executes this procedure verbatim. Anything missing here surfaces as a Phase 20 gap.

</specifics>

<deferred>
## Deferred Ideas

- New GitHub Issue templates (`.github/ISSUE_TEMPLATE/beta-bug.yml`) — not in v1.4 scope (Future Requirements).
- Mermaid diagrams in `v1.4-RELEASE-PROCEDURES.md` (D-13) — GitHub-Mermaid rendering inconsistency makes this risky.
- Auto-promotion beta → stable workflow doc section — deferred (workflow itself doesn't exist).
- Branch protection documentation — deferred until protection rules exist.
- Signing key documentation — deferred per REQUIREMENTS.md.
- Cross-repo metrics dashboard (PyPI download counts of `X.Y.ZbN` vs stable) — Future Requirements.

</deferred>

---

*Phase: 19-documentation*
*Context gathered: 2026-05-20*
*Discussion mode: --auto --chain*

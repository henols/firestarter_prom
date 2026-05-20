---
status: passed
phase: 20-end-to-end-smoke-test-milestone-close
source: [20-VERIFICATION.md]
started: 2026-05-20
updated: 2026-05-20
closed: 2026-05-20
ship_tag: 3.0.0b2
---

# Phase 20 — End-to-End Smoke Test (E2E-01) — Operator Checklist

## Purpose

This checklist drives the live beta cut and the consumer-side verification of all 6 E2E-01
sub-criteria. The operator follows `.planning/v1.4-RELEASE-PROCEDURES.md` in the Cut Sequence
below to cut a real beta in both sub-repos, then verifies each test in the list below.

`gsd-audit-uat 20` resurfaces pending items in `/gsd-progress` until all 6 tests are marked
`pass` — this matches the established `human_needed` pattern from v1.2 Phase 08/09 and
v1.3 Phase 12. Until the operator executes the live cut, runs the verifier, and confirms
each test, this phase remains open.

## Prerequisites

Before starting the cut sequence, confirm the following are in place:

- [ ] `gh` CLI is installed and authenticated: `gh auth status` returns green for both
      `henols/firestarter_app` and `henols/firestarter` (write access required for release creation).
- [ ] PyPI account credentials are configured for the `firestarter` project
      (only needed for the actual cut — the PyPI JSON API used by `v1.4-e2e-verify.sh` is public
      and unauthenticated).
- [ ] A clean Python virtual environment is available for Test 2 (clean-install from PyPI) and
      Test 5 (beta-installed app firmware install). Suggested: `python3 -m venv /tmp/e2e-beta`.
- [ ] A SEPARATE clean Python virtual environment is available for Test 6 (stable-installed
      non-regression). Suggested: `python3 -m venv /tmp/e2e-stable`.
- [ ] `jq` and `curl` are installed (required by `v1.4-e2e-verify.sh`).
- [ ] `beta` branch exists in both sub-repos (see §One-time setup below — only needed before
      the very first cut).

### One-time setup: create `beta` branch in each sub-repo

Before the first-ever beta cut, the `beta` branch must exist in both repos. Run once:

```bash
# In firestarter_app/:
git checkout main && git pull
git checkout -b beta && git push -u origin beta

# In firestarter/:
git checkout main && git pull
git checkout -b beta && git push -u origin beta
```

After this, `beta` exists at the same commit as `main`. No workflow fires yet — there's
nothing to merge into `beta`. Subsequent PRs will diff against this baseline.

### Choosing the resulting BETA_VERSION (Option 1 auto-increment vs Option 2 explicit)

Under **Option 1 (canonical — PR → merge to `beta`)**, you do NOT pre-pick `BETA_VERSION`.
Each repo's `update_version.py` scans git tags for the highest `X.Y.Zb*` matching the current
base version and auto-emits `b(N+1)`. First-ever cut emits `b1`. The resulting tag string is
whatever the script chooses based on the base version line.

**Base-version mismatch warning:** the two sub-repos currently carry DIFFERENT bases:
- `firestarter_app/firestarter/__init__.py`: `__version__ = "2.0.7_dev"` → auto-increment to `2.0.7b1`
- `firestarter/include/version.h`: `#define VERSION "3.0.0_dev"` → auto-increment to `3.0.0b1`

This breaks Test 4 (lockstep tag string-equality) on the first cut. **You have three options:**

1. **Reconcile bases first (recommended):** in your `firestarter_app` PR to `beta`, change
   `__version__ = "2.0.7_dev"` to `__version__ = "3.0.0_dev"` so both repos share the
   `3.0.0` base. Both then auto-increment to `3.0.0b1`. One-time reset.
2. **Use Option 2 once (lockstep escape hatch):** instead of letting auto-increment run on the
   first cut, use `gh workflow run ... -f beta_version=3.1.0b1` (or your chosen string) in BOTH
   repos. After the first cut anchors a common base, switch back to Option 1 for subsequent betas.
3. **Accept asymmetry (NOT RECOMMENDED):** publish `2.0.7b1` (app) + `3.0.0b1` (firmware).
   Test 4 will fail; `v1.4-e2e-verify.sh` Step 3 will report a lockstep mismatch. You'd need
   to manually skip that check and reinterpret VER-03. This pushes the problem to v1.5+.

The Cut Sequence below assumes **Option 1 with base reconciliation** (path #1). If you pick
path #2, jump to the §Option 2 alternative below.

## Cut Sequence (Option 1 — canonical PR → merge to `beta`)

Follow these steps in order before filling in the HUMAN-UAT tests below.

**Step 1 — Reconcile bases (FIRST cut only; skip on subsequent cuts):**

In `firestarter_app/`, open a PR targeting `beta` that changes:
```diff
- __version__ = "2.0.7_dev"
+ __version__ = "3.0.0_dev"
```
in `firestarter/__init__.py`. Merge this PR before the feature PR. The merge will trigger
`beta-release.yml` and emit `3.0.0b1` (first-ever beta on the `3.0.0` base).

If you don't need a feature for the first cut, this reconcile PR IS the first cut — it
publishes `3.0.0b1` to PyPI.

**Step 2 — Open feature PRs in both sub-repos targeting `beta`:**

In `firestarter_app/`:
```bash
git checkout beta && git pull
git checkout -b feature/<short-name>
# ... make changes (touch source files, NOT just docs / **.md / **.sh / docs/** / images/** / .vscode/**) ...
git push -u origin feature/<short-name>
gh pr create --base beta --title "<title>" --body "<body>"
```

In `firestarter/`:
```bash
git checkout beta && git pull
git checkout -b feature/<short-name>
# ... make changes (touch source files, NOT just docs / **.md / **.sh / docs/** / documents/** / images/** / .vscode/** / .editorconfig/**) ...
git push -u origin feature/<short-name>
gh pr create --base beta --title "<title>" --body "<body>"
```

⚠ **`paths-ignore` warning:** if your PR only touches `paths-ignore` patterns (markdown,
shell scripts, docs, images, .vscode/, .editorconfig/), the merge will NOT trigger the
workflow. Touch source code, a `.toml`, a workflow YAML, or `include/` / `firestarter/`
content to ensure the workflow fires.

**Step 3 — Merge both PRs close in time:**

```bash
gh pr merge <app-pr-num>     -R henols/firestarter_app --squash --delete-branch
gh pr merge <firmware-pr-num> -R henols/firestarter     --squash --delete-branch
```

Each merge pushes to `beta`. The workflow runs:
1. CI gates (catalog validity, codegen drift, pytest, native Unity for firmware)
2. `update_version.py` scans tags → emits `b(N+1)` (first cut after reconciliation: `3.0.0b1`)
3. Version bump auto-committed back to `beta`
4. GitHub Pre-release created
5. PyPI publish (app side only)

Watch both runs:
```bash
gh run watch -R henols/firestarter_app
gh run watch -R henols/firestarter
```

**Step 4 — Identify the emitted BETA_VERSION:**

```bash
BETA_VERSION_APP=$(gh release view -R henols/firestarter_app --json tagName -q .tagName)
BETA_VERSION_FW=$(gh release view -R henols/firestarter      --json tagName -q .tagName)
echo "app:      $BETA_VERSION_APP"
echo "firmware: $BETA_VERSION_FW"
```

If the bases were reconciled per Step 1, both will be the same (e.g. `3.0.0b1`).
Use that string as `<BETA_VERSION>` for the remaining tests.

If they differ, you skipped reconciliation — either roll back and reconcile, switch to
Option 2 (next section), or accept asymmetry knowing Test 4 will fail.

**Step 5 — Run automated verifier:**

```bash
bash .planning/v1.4-e2e-verify.sh "$BETA_VERSION_APP"
```

Expected: exit 0 with `ALL CHECKS PASSED`. If Step 3 (lockstep equality) fails, you have
drift — see §Option 2 alternative or §Recovering from drift in `v1.4-RELEASE-PROCEDURES.md`.

**Step 6 — Walk through the 6 HUMAN-UAT tests below** and mark each `pass` or `issue`,
substituting `<BETA_VERSION>` with the value from Step 4.

### Option 2 alternative (lockstep escape hatch)

Use this if you want to pin a specific `BETA_VERSION` (e.g. `0.0.1b1` for a guaranteed-clean
first test cut without reconciling bases):

```bash
# Land your changes on beta first via PR → merge (steps 2-3 above), but the auto-increment
# emitted strings can be ignored if you're going to override them.
# OR: skip the feature PRs entirely if the current beta-branch state is what you want to ship.

BETA_VERSION=0.0.1b1   # your chosen string; must satisfy ^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$

gh workflow run beta-release.yml -R henols/firestarter_app --ref beta -f beta_version=$BETA_VERSION
gh workflow run beta-build.yml   -R henols/firestarter     --ref beta -f beta_version=$BETA_VERSION
```

Both workflows write `$BETA_VERSION` verbatim — guaranteed string-equal across both repos.
Then run verifier:
```bash
bash .planning/v1.4-e2e-verify.sh "$BETA_VERSION"
```
and walk the 6 HUMAN-UAT tests.

## HUMAN-UAT Tests

---

### Test 1: PyPI pre-release visibility

**Maps to:** E2E-01 sub-criterion (a)
**Result:** pass
**Verified by:** operator

**Steps:**
1. Open `https://pypi.org/project/firestarter/#history` in a browser.
2. Locate the `<BETA_VERSION>` row in the version history list.
3. Confirm the row is tagged with the "pre-release" badge (PyPI displays this for
   PEP 440 `bN`/`rcN` versions).

> Note: This criterion is ALSO covered automatically by `v1.4-e2e-verify.sh` Step 1
> (PyPI JSON API check). Browser inspection provides the human-observable confirmation.

**Expected:** `<BETA_VERSION>` row is visible on the PyPI history page, tagged as pre-release.

**Notes:**

---

### Test 2: Clean-install from PyPI

**Maps to:** E2E-01 sub-criterion (b)
**Result:** pass
**Verified by:** operator

**Steps:**
1. Create and activate a fresh Python virtual environment:
   ```bash
   python3 -m venv /tmp/e2e-beta && source /tmp/e2e-beta/bin/activate
   ```
2. Install the beta version:
   ```bash
   pip install --pre firestarter==<BETA_VERSION>
   ```
3. Verify the installed version:
   ```bash
   firestarter --version
   ```
4. Confirm the install completed with exit 0 and no resolver errors or missing-dependency
   warnings.

**Expected:** `pip install` completes with exit 0 (no resolver errors, no missing dependencies);
`firestarter --version` prints exactly `<BETA_VERSION>` (with the `bN` suffix).

**Notes:**

---

### Test 3: Firmware GitHub Pre-release with .hex artifacts

**Maps to:** E2E-01 sub-criterion (c)
**Result:** pass
**Verified by:** operator

**Steps:**
1. Open `https://github.com/henols/firestarter/releases/tag/<BETA_VERSION>` in a browser.
2. Confirm the **"Pre-release"** badge is visible on the release page.
3. Confirm the **"Latest release"** badge is NOT present (must be absent, not just not Latest).
4. Open the Assets section and confirm BOTH of the following files are listed:
   - `firestarter_uno.hex`
   - `firestarter_leonardo.hex`

> Note: This criterion is ALSO covered automatically by `v1.4-e2e-verify.sh` Step 2
> (GitHub Releases JSON API assertions for `isPrerelease`, `!isLatest`, and asset names).

**Expected:** Release page shows the Pre-release badge, no Latest badge, and both per-board
`.hex` assets are present in the Assets section.

**Notes:**

---

### Test 4: Lockstep version string equality

**Maps to:** E2E-01 sub-criterion (d)
**Result:** pass
**Verified by:** operator

**Steps:**
1. Open `https://github.com/henols/firestarter_app/releases/tag/<BETA_VERSION>` in a browser.
   Confirm the tag name at the top of the page is exactly `<BETA_VERSION>`.
2. Open `https://github.com/henols/firestarter/releases/tag/<BETA_VERSION>` in a browser.
   Confirm the tag name at the top of the page is exactly `<BETA_VERSION>`.
3. Verify both tag strings are byte-identical to `<BETA_VERSION>` (no suffix differences,
   no prefix differences, same capitalization).

> Note: This criterion is ALSO covered automatically by `v1.4-e2e-verify.sh` Step 3
> (string-equality assertion on `tagName` from both repos' JSON API responses, per VER-03).

**Expected:** Both repos carry the same `<BETA_VERSION>` tag string per VER-03; byte-identical.

**Notes:**

---

### Test 5: Beta-installed app fetches matching beta firmware (INST-02 E2E)

**Maps to:** E2E-01 sub-criterion (e)
**Result:** pass
**Verified by:** operator

**Steps:**
1. In the virtual environment from Test 2 (beta-installed app — `source /tmp/e2e-beta/bin/activate`):
   ```bash
   firestarter fw -i --pre
   ```
2. If RURP hardware is available, allow the flash to proceed and confirm it completes
   successfully.
3. If RURP hardware is NOT available, observe the CLI output before any flash attempt.
   The CLI should print the resolved download URL or asset name. Cancel before flashing
   if no hardware is connected — the download URL resolution is what proves INST-02 end-to-end.
4. Confirm the resolved asset URL or download path references `<BETA_VERSION>`
   (e.g., `firestarter_uno.hex` from the `<BETA_VERSION>` GitHub Release).

Alternative: if you prefer to pin the exact version rather than "latest pre-release":
```bash
firestarter fw -i --firmware-version <BETA_VERSION>
```

**Expected:** The CLI resolves the `<BETA_VERSION>` GitHub Pre-release, selects the configured
board's `.hex` asset (Uno or Leonardo), and either flashes successfully or reports the resolved
asset URL/path referencing `<BETA_VERSION>`. Proves INST-02 end-to-end.

**Notes:**

---

### Test 6: Stable-installed app non-regression (INST-01)

**Maps to:** E2E-01 sub-criterion (f)
**Result:** pass
**Verified by:** operator

**Steps:**
1. Create and activate a SEPARATE fresh virtual environment (do NOT use the Test 2 venv):
   ```bash
   python3 -m venv /tmp/e2e-stable && source /tmp/e2e-stable/bin/activate
   ```
2. Install the stable version (NO `--pre` flag):
   ```bash
   pip install firestarter
   ```
3. Verify the installed version is stable (no `b`/`rc` suffix):
   ```bash
   firestarter --version
   ```
4. Run the stable firmware install with NO flags:
   ```bash
   firestarter fw -i
   ```
5. Observe the download URL or asset resolved by the CLI.
6. Confirm the URL does NOT reference `<BETA_VERSION>` — it must point at the latest
   STABLE firmware release.

**Expected:** Stable app installs with no pre-release suffix; `firestarter fw -i` (no flags)
resolves the latest STABLE firmware release (not `<BETA_VERSION>`). Proves INST-01 non-regression:
the `/releases/latest` API endpoint filters out pre-releases automatically, so stable-installed
users are unaffected by the new beta channel.

**Notes:**

---

## Completion Criteria

Phase 20 is considered green when ALL of the following are true:

- [x] All 6 tests above are marked `pass`
- [x] `bash .planning/v1.4-e2e-verify.sh <BETA_VERSION>` exited 0
- [x] `.planning/MILESTONES.md` v1.4 entry committed (Task 2 deliverable — already done
      as of the plan-20-01 commit; placeholder tokens replaced 2026-05-20)
- [x] `bash .planning/v1.4-archive.sh` executed and phase directories moved to
      `.planning/milestones/v1.4-phases/`
- [x] `.planning/PROJECT.md` updated to ship state with the real ship date (2026-05-20)

Once all criteria are met, update this file's frontmatter to `status: passed` and
commit the change as part of the milestone close.

## First-Run Note

On the very first encounter with this checklist, the operator will not have cut any beta
yet. `gsd-audit-uat 20` will return `status: human_needed` — this is CORRECT behavior,
not a defect.

This matches the established GSD workflow pattern from:
- v1.2 Phase 08/09 — chip-seated W27C512 hardware UAT (`status: human_needed` until bench session)
- v1.3 Phase 12 — CMOS EPROM bench validation (`status: human_needed` until bench hardware available)

`20-HUMAN-UAT.md` persists with `status: partial` until each test transitions from `pending`
to `pass` via the operator's live E2E run. The GSD workflow surfaces pending items in
`/gsd-progress` until closure.

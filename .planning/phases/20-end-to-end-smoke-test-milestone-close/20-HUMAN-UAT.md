---
status: partial
phase: 20-end-to-end-smoke-test-milestone-close
source: [20-VERIFICATION.md]
started: 2026-05-20
updated: 2026-05-20
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
- [ ] `BETA_VERSION` is chosen per the guidance below.
- [ ] `jq` and `curl` are installed (required by `v1.4-e2e-verify.sh`).

### Choosing BETA_VERSION

Pick a `BETA_VERSION` of the form `X.Y.ZbN` that does NOT conflict with any existing stable
or beta tag in EITHER repo. Must match the PEP 440 regex `^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$`.

Recommended options:
- **First E2E run:** `0.0.1b1` — clean version line, zero risk of disrupting current stable
  users on the `2.0.7` app / `3.0.0` firmware stable lines.
- **Next-minor real beta:** `(major).(minor+1).0b1` — semantic intent: pre-release of the
  next minor version. Verify no existing tag in either repo before using.

Verify no conflict:
```bash
gh release list -R henols/firestarter_app | grep "$BETA_VERSION"   # should return nothing
gh release list -R henols/firestarter     | grep "$BETA_VERSION"   # should return nothing
```

## Cut Sequence

Follow these steps in order before filling in the HUMAN-UAT tests below.

**Step 1 — Lockstep dry-run:**
```bash
BETA_VERSION=<chosen> bash .planning/phases/15-versioning-locked-step-coordination-foundation/lockstep-dryrun-fixture.sh
```
Expected output: `LOCKSTEP OK`. If it prints `LOCKSTEP FAILED`, stop and check your
`BETA_VERSION` choice and both sub-repos' `update_version.py` scripts.

**Step 2 — Cut app beta release:**
```bash
gh workflow run beta-release.yml -R henols/firestarter_app --ref beta -f beta_version=<chosen>
```
Wait for the workflow to complete green in the Actions tab
(`https://github.com/henols/firestarter_app/actions`).

**Step 3 — Cut firmware beta release:**
```bash
gh workflow run beta-build.yml -R henols/firestarter --ref beta -f beta_version=<chosen>
```
Wait for the workflow to complete green in the Actions tab
(`https://github.com/henols/firestarter/actions`).

**Step 4 — Run automated verifier:**
```bash
bash .planning/v1.4-e2e-verify.sh <chosen>
```
Expected: exit 0 with `ALL CHECKS PASSED`. If any check fails, review the per-step
failure summary printed by the script and fix before proceeding to the HUMAN-UAT tests.

**Step 5 — Walk through the 6 HUMAN-UAT tests below** and mark each `pass` or `issue`.

## HUMAN-UAT Tests

---

### Test 1: PyPI pre-release visibility

**Maps to:** E2E-01 sub-criterion (a)
**Result:** pending
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
**Result:** pending
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
**Result:** pending
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
**Result:** pending
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
**Result:** pending
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
**Result:** pending
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

- [ ] All 6 tests above are marked `pass`
- [ ] `bash .planning/v1.4-e2e-verify.sh <BETA_VERSION>` exited 0
- [ ] `.planning/MILESTONES.md` v1.4 entry committed (Task 2 deliverable — already done
      as of the plan-20-01 commit; operator updates `<SHIP_DATE_PLACEHOLDER>` tokens)
- [ ] `bash .planning/v1.4-archive.sh` executed and phase directories moved to
      `.planning/milestones/v1.4-phases/`
- [ ] `.planning/PROJECT.md` updated to ship state with the real ship date
      (operator replaces `<SHIP_DATE_PLACEHOLDER>` token)

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

---
phase: 25-documentation-milestone-close
status: complete
shipped: 2026-05-21
type: documentation + milestone-close
requirements: [DOC-01, DOC-02, MS-01]
requirements_addressed: [DOC-01, DOC-02, MS-01]
---

# Phase 25: Documentation + Milestone Close — SUMMARY

## What was delivered

**DOC-01** — Both READMEs updated:
- `firestarter/README.md` (firmware sub-repo, beta branch commit `bc0f5ac`): Added "Supported boards" section with a three-row matrix (uno / uno328pb / leonardo) listing PlatformIO env, MCU, bootloader, and notes. Updated the issue-report template's "Board" field to include uno328pb. Pushed to origin/beta — `*.md` path-ignore in workflow means no extra CI cut triggered.
- `firestarter_app/README.md` (app sub-repo, beta branch commit `26e22a0`): Extended the `--board` option help text to list uno328pb alongside uno and leonardo. Added an "install on a 328PB-Uno" example command with a note about the auto-selected `programmer_id=urclock`. Updated the issue-report template's "Board" field. Pushed to origin/beta — same path-ignore behavior.

**DOC-02** — `v1.4-RELEASE-PROCEDURES.md` updated with a "v1.5 update" header note clarifying the procedure mechanics carry forward unchanged from v1.4. Only delta: the asset-list verification step now expects 3 `.hex` files instead of 2 (no release-engineer action needed; the `softprops/action-gh-release@v2` glob picks up the third asset automatically).

**MS-01** — Three artifacts produced:
- `MILESTONES.md` gained a v1.5 entry (delivery summary, 5 key accomplishments, branch strategy, 3 open-backlog bugs carried to v1.6, key locked decisions)
- `PROJECT.md` updated: status header flipped from "v1.5 status: Started" to "v1.5 shipped 2026-05-21"; "Current Milestone: v1.5 ..." section header re-tagged as "v1.5 Archive"
- Phase directories archived under `.planning/milestones/v1.5-phases/` via `gsd:complete-milestone` (next step in the closure flow)

## Mode

Direct execution (no formal `/gsd-discuss-phase 25` → `/gsd-plan-phase 25` ceremony) — the scope was mechanical documentation work derived 1:1 from the Phase 21–24 shipped state. Operator-authorized via the "close the milestone" instruction 2026-05-21.

## Verification

- `git -C /workspaces/firestarter log --oneline beta -1` → `bc0f5ac docs(25): document uno328pb as third firmware build target (v1.5)`
- `git -C /workspaces/firestarter_app log --oneline beta -1` → `26e22a0 docs(25): document uno328pb board choice + urclock auto-select (v1.5)`
- `grep -c "uno328pb" /workspaces/firestarter/README.md /workspaces/firestarter_app/README.md` → both > 0
- `grep -c "v1.5" /workspaces/.planning/MILESTONES.md` → multiple hits in the new v1.5 section
- `grep "v1.5 shipped" /workspaces/.planning/PROJECT.md` → hit

## Outcome

v1.5 milestone is fully documented and ready for archival. The `gsd:complete-milestone` skill executes immediately after this SUMMARY commit lands.

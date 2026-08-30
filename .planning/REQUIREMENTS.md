# Requirements: Firestarter — v1.35 Documentation Consolidation & Wiki Migration

**Defined:** 2026-08-30
**Milestone value:** One front door, one documentation home, and no page that claims more than the code can back.

**Scope note.** This milestone changes documentation, repository configuration, and one sync/check
script. It does not touch firmware or host behaviour. Every requirement below is verifiable by
reading a file, running a script, or querying the GitHub API — none of it needs hardware.

---

## v1 Requirements

### Wiki — the single documentation home

- [ ] **WIKI-01**: The `firestarter_prom` wiki exists and is reachable, with a Home page that indexes every documentation page by name.
- [ ] **WIKI-02**: Wiki pages are authored as markdown files inside the `firestarter_prom` repository, and that in-repo copy is the single source of truth — the wiki is a publishing target, never the place edits originate.
- [ ] **WIKI-03**: A maintainer can publish the in-repo wiki source to the GitHub wiki with one command; re-running it with no source change produces no wiki commit.
- [ ] **WIKI-04**: A drift check reports failure when the published wiki differs from the in-repo source, and is demonstrated failing before it is trusted.
- [ ] **WIKI-05**: A reader can navigate between wiki pages without going back to the repository — every page is reachable from the Home page or a sidebar.
- [ ] **WIKI-06**: The two sub-repo wikis are disabled, so `firestarter_prom` is the only wiki that can accumulate content.

### Front door — `firestarter_prom`

- [ ] **FRONT-01**: `firestarter_prom` has a README that says what Firestarter is, and for whom, within the first screenful.
- [ ] **FRONT-02**: A newcomer can go from that README to a first successful chip read — obtain the RURP shield, install the CLI, flash the firmware, read a chip — without opening any other document.
- [ ] **FRONT-03**: The README links into the wiki for everything past getting started, and does not restate content the wiki owns.
- [ ] **FRONT-04**: All three GitHub repository descriptions are set and distinguish the three repos from one another (all three are empty today).

### Sub-repo READMEs — repo-scoped only

- [ ] **REPO-01**: `firestarter/README.md` carries only firmware-specific information and links to `firestarter_prom` for everything else.
- [ ] **REPO-02**: `firestarter_app/README.md` carries only app-specific information and links to `firestarter_prom` for everything else.
- [ ] **REPO-03**: Each sub-repo README is short enough to read in one sitting — assessed by judgement at review, deliberately not against a line-count ceiling. (They are 151 and 779 lines today, for reference only; the number is not the criterion.)
- [ ] **REPO-04**: The PyPI listing built from `firestarter_app/README.md` still names the project, gives the install command, links to the documentation, and states the license — the accepted thinning does not become an unusable package page.

### Migration — emptying `doc/`

- [ ] **MIGRATE-01**: The content of all 13 `doc/` files is reachable on the wiki.
- [ ] **MIGRATE-02**: `firestarter/doc/` and `firestarter_app/doc/` no longer exist in either repository.
- [ ] **MIGRATE-03**: `firestarter_app` still builds, installs, and passes its test suite after `doc/` removal — three of those files (`package-details.md`, `protocol-flags.md`, `protocol-id.md`) are currently carried in the sdist.
- [ ] **MIGRATE-04**: No file in either sub-repo links to a `doc/` path that no longer exists.

### Legacy — correcting what is already wrong

- [ ] **LEGACY-01**: No documentation page sends a reader to an issue tracker that is disabled — the six links into `henols/firestarter/issues` and `henols/firestarter_app/issues` are gone.
- [ ] **LEGACY-02**: The app README's table of contents lists exactly the sections the document contains — today it advertises `Id`, `Vpe` and `Hw`, none of which exist, and omits `List`, `Search` and `VCC`, which do.
- [ ] **LEGACY-03**: No README opens with accumulated breaking-change notices ahead of its install instructions; the v1.10 / v1.20 / v1.32 history is reachable on the wiki instead.
- [ ] **LEGACY-04**: `firestarter_app/things.md` — a six-line scratch note about finding avrtools on Windows — is either a real wiki page or deleted.
- [ ] **LEGACY-05**: `firestarter_app/SECURITY.md` is a genuine security policy or is removed; a GSD Phase 69 audit record no longer occupies the path GitHub reads as the repository's security policy.
- [ ] **LEGACY-06**: No user-facing documentation page is titled or framed as a GSD phase artifact — `pinout-safety-review.md` ("Phase 58") and `sram-nvram-behavior.md` ("Phase 59") read as reference material or do not ship.
- [ ] **LEGACY-07**: `firestarter_app/autocomplete.md` is folded into the app README or the wiki rather than sitting loose at the repository root.

### Policy — Backlog 999.13 in full

- [ ] **POLICY-01**: The documentation states plainly that `firestarter_prom` is the only issue tracker, that `firestarter` and `firestarter_app` have Issues disabled, and that pull requests go to the repository containing the changed code.
- [ ] **POLICY-02**: `firestarter_prom` offers issue templates covering at least a bug report, a feature request, and a `dev test` chip-validation report.
- [ ] **POLICY-03**: `main` in all three repositories is behind a ruleset whose enforcement is **active** — pull request required, no direct push, no force-push, no deletion. (`firestarter` has such a ruleset today with enforcement **disabled**; the other two have none.)
- [ ] **POLICY-04**: The `beta` lockstep cut still works under those rulesets, demonstrated rather than assumed — this project's milestone convention pushes `beta`, not `main`.
- [ ] **POLICY-05**: The GSD close procedure is updated for PR-only `main`, either as a PR flow or a documented admin bypass, so `/gsd-complete-milestone` does not break at the next close.

### Honesty — claims survive the move unchanged

- [ ] **HONEST-01**: Every `support_status` value (`protocol-not-implemented`, `adapter-required`, `vpp-exceeds-max`) and every `PROTOCOL-LEDGER` `UNVERIFIED` bucket reads on the wiki exactly as faithfully as it read in the source document — the migration upgrades no claim.
- [ ] **HONEST-02**: Any wiki page making per-chip or per-protocol claims either carries a check that fails when it disagrees with `chip_database.json` / `PROTOCOL-LEDGER.json`, or carries an explicit "generated from DB vN, verified <date>" stamp.

---

## Future Requirements

Deferred by decision, not dropped. Tracked against Backlog **999.12** (gh#5), which stays open.

### Wiki content (carried into 999.12 from the retired 999.14 / gh#7)

- **FUT-W-01**: A searchable compatibility matrix of supported operations per device.
- **FUT-W-02**: Per-family pages — 27Cxxx, 28Cxxx, 29Cxxx, 39SFxxx, AM29Fxxx, and per-vendor groupings.
- **FUT-W-03**: Programming-algorithm and command-set pages, sourced from `firestarter/doc/PROTOCOLS.md`'s 12-bucket vocabulary and `PROTOCOL-LEDGER.{md,json}` rather than re-authored.
- **FUT-W-04**: Task-oriented tutorials.
- **FUT-W-05**: README and repository metadata keywords for discoverability.

### Repository identity

- **FUT-R-01**: Backlog **999.9** (gh#2) — rename all three repositories without breaking installation. Sequenced after this milestone by operator decision; see the hazard below.

---

## Out of Scope

| Item | Reason |
|------|--------|
| Compatibility matrix, family pages, algorithm pages, tutorials | Operator decision at activation: **relocate and correct only**. Tracked as FUT-W-01…05 against Backlog 999.12. |
| Repository rename (Backlog 999.9 / gh#2) | Operator chose to proceed and sweep references later. See the sequencing hazard below — this is an accepted cost, not an oversight. |
| A generated documentation site (MkDocs / Docusaurus) | Retired at the 2026-07-27 backlog review when the operator chose the Wiki. The SEO and discoverability goal gh#7 was filed for is given up. |
| Edits to `.planning/` historical records | `.planning/`→`.planning/` citations are historical-by-intent. Repairing them destroys the evidence they exist to preserve. |
| Firmware or host application behaviour | This is a documentation and configuration milestone. Any product-code change found necessary is filed, not fixed here. |
| Restructuring Discord or the community forum | Out of the documentation surface this milestone owns. |

---

## Constraints and Hazards

**Operator-gated blocker — the wiki must be created by hand.** GitHub creates `<repo>.wiki.git` only
when the first page is saved through the web UI. There is no REST endpoint for wiki pages, and
push-to-create was tested at activation and fails (`remote: Repository not found`). WIKI-01 cannot be
satisfied until the operator saves one page at `https://github.com/henols/firestarter_prom/wiki`.
Every other requirement is unblocked and can proceed in parallel — no phase may be planned whose
first action is a wiki push.

**Branch protection changes the close procedure.** POLICY-03 puts `main` behind enforcing rulesets.
`/gsd-complete-milestone` pushes `main` directly today. POLICY-05 exists because POLICY-03 would
otherwise break the next milestone close, and POLICY-04 exists because this project's actual
convention pushes `beta` — protection that blocks the lockstep cut would be worse than no protection.

**Sequencing hazard, accepted at activation.** Backlog 999.9 renames all three repositories
(`firestarter_prom` → `firestarter`, `firestarter` → `firestarter_fw`). Every wiki link, README
pointer and issue URL written by this milestone would be invalidated by that rename. The operator was
shown this before approving scope and chose to proceed, sweeping references afterwards.

**The honesty constraint is load-bearing, not decorative.** Hand-maintained pages drift where a
generator would not. A wiki page implying blanket support for an unverified chip is precisely the
false-PASS failure mode v1.21 was built to prevent. HONEST-02 is the mitigation and is in scope.

---

## Traceability

Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| _(pending roadmap)_ | | |

**Coverage:**
- v1 requirements: 32 total
- Mapped to phases: 0
- Unmapped: 32 ⚠️

---
*Requirements defined: 2026-08-30*
*Last updated: 2026-08-30 after milestone v1.35 activation*

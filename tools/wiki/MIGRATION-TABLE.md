# Wiki Migration Table

This table is the auditable record of where every wiki page came from. Documentation now
lives only in the GitHub wiki (`firestarter_prom.wiki.git`); there is no in-repo source tree
and no publish subcommand — pages reach the wiki by a cloned-and-pushed commit (D-19). This
table exists for two consumers: a reviewer checking that a moved file kept its content and
its claims, and the Backlog 999.9 repository-rename sweep that greps it for a source path
before renaming anything.

| Source repo | Source path | Wiki page | Rendered title | Pre-deletion SHA | Moved in |
|---|---|---|---|---|---|
| firestarter_prom | — | Home | Home | — | 167 |
| firestarter_prom | — | How-To-Edit-This-Wiki | How To Edit This Wiki | — | 167 (renamed 168) |
| firestarter | firestarter/doc/PROTOCOLS.md | Programming-Protocols | Programming Protocols | a218b4f5273d14f0abd796b21ac104792de01603 | 168 |
| firestarter | firestarter/doc/SHIELD-REVISIONS.md | Shield-Revisions | Shield Revisions | a218b4f5273d14f0abd796b21ac104792de01603 | 168 |
| firestarter | firestarter/doc/AT28C04-ADAPTER.md | AT28C04-Adapter | AT28C04 Adapter | a218b4f5273d14f0abd796b21ac104792de01603 | 168 |
| firestarter_app | firestarter_app/doc/beta-testing-install.md | Beta-Testing-Install | Beta Testing Install | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |
| firestarter_app | firestarter_app/doc/community-validation.md | Community-Validation | Community Validation | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |
| firestarter_app | firestarter_app/doc/infoic-field-dictionary.md | Infoic-Field-Dictionary | Infoic Field Dictionary | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |
| firestarter_app | firestarter_app/doc/lockable-proms.md | Lockable-PROMs | Lockable PROMs | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |
| firestarter_app | firestarter_app/doc/package-details.md | Package-Details | Package Details | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |
| firestarter_app | firestarter_app/doc/pinout-safety-review.md | Pinout-Safety-Review | Pinout Safety Review | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |
| firestarter_app | firestarter_app/doc/protocol-flags.md | Protocol-Flags | Protocol Flags | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |
| firestarter_app | firestarter_app/doc/protocol-id.md | Protocol-ID | Protocol ID | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |
| firestarter_app | firestarter_app/doc/sram-nvram-behavior.md | SRAM-and-NVRAM-Behavior | SRAM and NVRAM Behavior | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 |

The Pre-deletion SHA is the sub-repo commit that created the
`gsd/v1.35-documentation-consolidation-wiki-migration` branch (Task 1 of Plan 168-01) —
`doc/` content is never edited in-repo by this phase, only deleted, so that commit's tree is
exact for every row. This is the *only* future oracle for the pre-migration text once `doc/`
is deleted (D-02): the checker reads the source side with
`git -C <subrepo> show <sha>:doc/<file>`. Task 3 of this plan proves all 13 rows resolve to
non-empty content before this plan is allowed to close.

The `How-To-Edit-This-Wiki` rename (from `How-This-Wiki-Is-Published`, per D-21) has no
source SHA because it is wiki-authored prose, not a migrated `doc/` file. The old title
asserted a publishing model that stopped existing at the reversal; keeping it would ship a
false title on a public page for the sake of a URL with exactly one known inbound link
(`Home.md:5`), which this phase rewrites in the same wiki commit that renames the page.

## Deferred, not migrating

`firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` is **not** part of the migration. The
PY32F071 work it describes exists only at the planning stage and its code is a
proof-of-concept, so publishing an install guide for it would promise a capability the
project cannot currently back. It is deferred to future wiki work alongside FUT-W-01…05
and is deliberately absent from the table above so no migration pass picks it up by
accident.

It is still **deleted** — MIGRATE-02 removes the whole `firestarter_app/doc/` directory, and
this file is inside it — so "deferred" would silently become "lost" without a recorded
oracle. Its pre-deletion SHA is `d56424e1979edf7245cffb9ec3111c0469f5b23f` (the same
branch-creation commit as the migrating app files), readable as
`git -C firestarter_app show d56424e1979edf7245cffb9ec3111c0469f5b23f:firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md`.

## The hyphen hazard

GitHub renders a hyphen in a wiki page's filename as a space in its rendered title, so a
title that needs a literal hyphen cannot be expressed as a wiki page name and must be
reworded instead. Do not work around this by substituting a look-alike, non-ASCII hyphen
character (such as U+2010) into the filename to smuggle a literal hyphen through — an
invisible non-ASCII character inside a URL that gets hand-written into other repositories'
READMEs is a worse defect than a reworded title, and it would not be visible on review.

Two of the twelve filenames above are the specific cases worth checking deliberately
when this table is filled in: `AT28C04-ADAPTER.md`, whose natural title is a part number
that already contains a hyphen, and `sram-nvram-behavior.md`, whose natural title reads
most naturally with a slash (SRAM/NVRAM) rather than a hyphen. Both need a reworded title
that a rendered wiki page can actually carry, decided deliberately rather than defaulted
into by whatever the mechanical hyphen-to-space substitution happens to produce.

**Resolved.** `AT28C04-ADAPTER.md` needs no literal hyphen in its intended title at all —
the page stem `AT28C04-Adapter` renders as "AT28C04 Adapter", which reads correctly without
the hyphen `render_title` would otherwise strip. `sram-nvram-behavior.md`'s natural
"SRAM/NVRAM" is illegal under `wiki.py`'s `check_page_names` (which rejects `/` outright),
so it is reworded to "SRAM and NVRAM Behavior", page stem `SRAM-and-NVRAM-Behavior`. Both
stems use only the alphabet `[A-Za-z0-9-]` that `_LEGAL_TARGET_RE` admits
(`tools/wiki/wiki.py:52`), so both are reachable by the only legal internal link form.
Neither uses the U+2010 look-alike workaround this section forbids.

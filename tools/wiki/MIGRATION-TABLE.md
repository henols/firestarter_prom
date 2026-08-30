# Wiki Migration Table

This table is the auditable record of where every wiki page came from. The publish path
derives a page's name mechanically from its filename and consults no manifest, so nothing
in this repository reads this table to decide what to publish.

`wiki.py publish` does not read this table, and never will, because a consulted manifest is exactly the kind of second source of truth this project's drift check exists to eliminate. This table exists for humans: reviewers checking that a moved file kept its content and its claims intact, and the repository-rename sweep that greps it for a source path before renaming anything.

| Source repo | Source path | Wiki page | Rendered title | Moved in |
|---|---|---|---|---|
| firestarter_prom | — | Home | Home | 167 |
| firestarter_prom | — | How-This-Wiki-Is-Published | How This Wiki Is Published | 167 |
| firestarter | firestarter/doc/PROTOCOLS.md | TBD | TBD | TBD |
| firestarter | firestarter/doc/SHIELD-REVISIONS.md | TBD | TBD | TBD |
| firestarter | firestarter/doc/AT28C04-ADAPTER.md | TBD | TBD | TBD |
| firestarter_app | firestarter_app/doc/beta-testing-install.md | TBD | TBD | TBD |
| firestarter_app | firestarter_app/doc/community-validation.md | TBD | TBD | TBD |
| firestarter_app | firestarter_app/doc/infoic-field-dictionary.md | TBD | TBD | TBD |
| firestarter_app | firestarter_app/doc/lockable-proms.md | TBD | TBD | TBD |
| firestarter_app | firestarter_app/doc/package-details.md | TBD | TBD | TBD |
| firestarter_app | firestarter_app/doc/pinout-safety-review.md | TBD | TBD | TBD |
| firestarter_app | firestarter_app/doc/protocol-flags.md | TBD | TBD | TBD |
| firestarter_app | firestarter_app/doc/protocol-id.md | TBD | TBD | TBD |
| firestarter_app | firestarter_app/doc/sram-nvram-behavior.md | TBD | TBD | TBD |

The two filled rows above are the pages authored directly in this phase, with no prior
source path — they demonstrate the columns against real data rather than an empty
template. The twelve `TBD` rows are the shell for the next migration pass to fill in:
their source repository and source path are already recorded, so that pass is auditable
against this table rather than trusted to remember all twelve files correctly.

## Deferred, not migrating

`firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` is **not** part of the migration. The
PY32F071 work it describes exists only at the planning stage and its code is a
proof-of-concept, so publishing an install guide for it would promise a capability the
project cannot currently back. It is deferred to future wiki work alongside FUT-W-01…05
and is deliberately absent from the table above so no migration pass picks it up by
accident.

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

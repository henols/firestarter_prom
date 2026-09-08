---
created: 2026-09-08T00:00:00Z
title: Relocate MIGRATION-TABLE.md out of tools/ — it is a closed-milestone record, not tooling
area: meta
files:
  - tools/wiki/MIGRATION-TABLE.md (the file to move; the only survivor of 5426d7ef)
  - .planning/v1.35/ (proposed destination — the milestone whose output it is)
  - .planning/ROADMAP.md, .planning/STATE.md (live records that cite it)
  - .planning/milestones/v1.35-REQUIREMENTS.md, .planning/milestones/v1.35-ROADMAP.md
  - .planning/v1.35/CLOSE-RECORD.md, .planning/notes/v135-wiki-only-reversal.md
  - .planning/phases/167-*, 168-*, 171-*, 172-*, 173-*, 174-* (archived citers)
---

## Problem

Commit `5426d7ef` (2026-09-02) retired the wiki checkers, deleting `wiki.py`,
`honest01_claims.py`, `honest02_truth.py`, `provenance_footers.py`, `dispatch_mirror.py`,
`selftest.sh`, `claim-allowlist.json` and `claim-vocabulary.json`. `MIGRATION-TABLE.md` was left
behind as the sole occupant of `tools/wiki/`.

It is not tooling. It is the provenance record of the v1.35 wiki migration, and that milestone is
closed. Operator's call: *"it is done and does not belong in tools"*.

It must **not** be deleted — it is cited from live records (`ROADMAP.md`, `STATE.md`,
`v1.35/CLOSE-RECORD.md`, `MILESTONES.md`, `RETROSPECTIVE.md`, `PROJECT.md`) as well as archives.

## Measured citation surface

- **286** occurrences of the path form `tools/wiki/MIGRATION-TABLE.md` across **85** `.md` files
  under `.planning/`.
- **221** further bare `MIGRATION-TABLE` mentions with no path prefix — these need **no** change.
- Several citations are **line-anchored**: `MIGRATION-TABLE.md:15`, `:18-19`, `:20`, `:45-58`,
  `:52-53`, `:68-80`, `:104-105` (seen in `171-PATTERNS.md`, `171-03-PLAN.md`,
  `171-03-SUMMARY.md`). A pure `git mv` leaves file content byte-identical, so **every line
  anchor stays valid** — only the directory prefix changes.

## Approach

1. `git mv tools/wiki/MIGRATION-TABLE.md .planning/v1.35/MIGRATION-TABLE.md` — content untouched,
   so line anchors survive. `tools/wiki/` then disappears entirely.
2. **Scripted** path remap of the 286 path-form citations, `tools/wiki/MIGRATION-TABLE.md` ->
   `.planning/v1.35/MIGRATION-TABLE.md`. Do this with a script, not by hand — the citation-repair
   discipline requires a round-trip oracle, and 85 files is past the hand-edit threshold.
3. Round-trip oracle: after the remap, assert that **zero** files contain the old path and that
   the new path resolves to an existing file from every citing file's perspective.

## Precedent nuance to record in the SUMMARY

Before the move the 286 citations are `.planning/` -> **source**, which the repair rule covers:
never accept staleness, archives included. After the move they become `.planning/` ->
`.planning/`, which is historical-by-intent and explicitly **not** subject to future repair. So
this remap is a one-time transition across that boundary. State that explicitly, otherwise a
later reader may see 286 `.planning/`->`.planning/` citations and conclude the repair rule was
misapplied.

## Acceptance

- [ ] `tools/wiki/` no longer exists; `tools/` contains only `catalog/` and `rekey/`.
- [ ] `.planning/v1.35/MIGRATION-TABLE.md` exists and is byte-identical to the old file
      (`git log --follow` shows the rename; `git show HEAD~1:tools/wiki/MIGRATION-TABLE.md | diff - .planning/v1.35/MIGRATION-TABLE.md` is empty).
- [ ] `/usr/bin/grep -rn "tools/wiki/MIGRATION-TABLE" .planning | wc -l` is **0**.
- [ ] `/usr/bin/grep -rn "tools/wiki" .planning --include='*.md' | wc -l` — the remaining hits are
      only historical references to the *deleted checkers*, not to the table. Enumerate them in
      the SUMMARY rather than repairing them: they cite files `5426d7ef` removed, and rewriting
      those would destroy the retirement evidence.
- [ ] The count of line-anchored `MIGRATION-TABLE.md:<N>` citations is unchanged, and each anchor
      still lands on the line it names.
- [ ] No CI gate references `tools/wiki` — confirmed: `.github/workflows/` holds only
      `catalog-sync-check.yml` and `rekey-ledger-check.yml`.
- [ ] Record gates re-run clean (allow 300s — STATE.md carries a very long line).

## Note

Use `/gsd-quick` for this. It is a tracked-file change with a real oracle, not an inline edit.

---
phase: 11-build-db-cleanup
type: context
---

# Phase 11 — Database Pipeline Cleanup

## Problem

The `firestarter_app/tools/` directory contains two parsers and two committed XML snapshots:

```
tools/
  parse_db.py       (legacy, unused — reads local infoic.xml, writes database_generated.json)
  parse_db_2.py     (active — fetches XML from gitlab, writes minipro_complete_db.json)
  infoic.xml        (6.7 MB, January 2025 snapshot)
  infoic2.xml       (17.8 MB, December 2024 snapshot)
  verified.txt      (referenced only by parse_db.py)
```

This is wrong on three counts:

1. **Two parsers.** The runtime (`database.py`, `CLAUDE.md`) already calls out `parse_db_2.py` as canonical. `parse_db.py` is dead code that confuses readers and produces a stale `database_generated.json` that is never read.

2. **Bad name.** `parse_db_2.py` is a name from the transition. With the legacy gone, the active tool should be called `build_db.py` — it builds the database, it doesn't merely parse XML.

3. **XML snapshots in the repo.** `infoic.xml` is upstream data from the minipro project. It changes upstream, and snapshots in this repo go stale immediately. The active `parse_db_2.py` already fetches it over HTTPS at run time (line 10, line 159). The committed snapshots only exist because the legacy `parse_db.py` reads from disk. After this phase the script has a single source of truth — upstream — and the snapshots must never be re-committed.

## Goal

After this phase:

- One file in `tools/` named `build_db.py` does the entire job: fetch upstream XML, parse, write `minipro_complete_db.json`.
- No `infoic*.xml` files exist in the working tree, and `.gitignore` prevents them being committed in the future.
- Doc and comment references point to `build_db.py`.

## Scope

### In scope

- `firestarter_app/tools/parse_db.py` — delete
- `firestarter_app/tools/parse_db_2.py` — rename to `build_db.py`
- `firestarter_app/tools/infoic.xml`, `tools/infoic2.xml` — delete
- `firestarter_app/tools/verified.txt` — delete (only consumer was `parse_db.py`)
- `firestarter_app/firestarter/data/database_generated.json` — delete (only producer was `parse_db.py`)
- `firestarter_app/firestarter/data/pin-maps.json` — delete (legacy, no producer or consumer in current code)
- `firestarter_app/.gitignore` — add `tools/infoic*.xml`
- `firestarter_app/CLAUDE.md` — replace `parse_db_2.py` → `build_db.py` (4 occurrences)
- `firestarter_app/firestarter/database.py` — replace `parse_db_2.py` → `build_db.py` in comments (2 occurrences: line 379, line 487)

### Out of scope

- No behavior changes inside the script. The only diff inside `build_db.py` vs `parse_db_2.py` is the rename — same imports, same URL, same parsing, same output.
- `firestarter_app/firestarter/data/pinouts.json` — referenced by `build_db.py` at module load; leave untouched.
- `firestarter_app/firestarter/data/database_overrides.json` — user-editable override file; leave untouched.
- The `verified` field gap (legacy `parse_db.py` set `verified=True/False` per chip from `verified.txt`; `parse_db_2.py` doesn't, so `get_eproms(verified=True)` silently returns nothing). This is a pre-existing bug, not introduced by this phase, and out of scope. Flag in plan as a known issue for a future phase.

## Constraints

- **Rename must preserve git history.** Use `git mv`, not delete + add.
- **No script logic changes.** Diff between old `parse_db_2.py` and new `build_db.py` must be exactly the filename (and no internal self-references to fix — verified by grep on `parse_db_2` in the file's body: there are none).
- **Output byte-identity.** Running `python tools/build_db.py` after the rename, against the same upstream XML, must produce a `minipro_complete_db.json` byte-identical to what `parse_db_2.py` would have produced. The script does not depend on its own filename.
- **No new dependencies.** `requests` is already imported by `parse_db_2.py`.

## Locked decisions

- New filename is `build_db.py` (user choice, not negotiable).
- XML is **never** persisted to disk — fetched and parsed in memory only.
- `.gitignore` pattern is `tools/infoic*.xml` (covers `infoic.xml`, `infoic2.xml`, future `infoic3.xml` etc.).
- `verified.txt`, `database_generated.json`, `pin-maps.json` are deleted (not retained as historical artifacts).
- The fetch URL stays `https://gitlab.com/DavidGriffith/minipro/-/raw/master/infoic.xml` — already correct.

## Claude's discretion

- Order of operations within the single PLAN (delete → rename → gitignore → docs, vs grouped any other way).
- Whether to verify byte-identity manually via a one-shot diff, or rely on the trivial-rename argument.
- Commit granularity: one commit covering all of it is acceptable (single atomic refactor), or split into a "delete legacy" / "rename active" / "update docs" trio. Recommend single commit — the changes are coupled.

## Acceptance

A reviewer with a fresh `firestarter_app/` checkout runs:

```bash
git ls-files tools/ | grep -E 'parse_db|infoic|verified'
# expected: tools/build_db.py
python tools/build_db.py
# expected: prints "Done! N chips processed. Saved to .../minipro_complete_db.json"
git status
# expected: clean (no infoic.xml appears)
grep -rn 'parse_db_2\|parse_db\.py' firestarter_app/
# expected: no matches outside .planning/
```

All four checks pass.

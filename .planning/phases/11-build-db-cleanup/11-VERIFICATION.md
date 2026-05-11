---
phase: 11-build-db-cleanup
verified: 2026-05-11T07:25:00Z
status: passed
score: 4/4 must-haves verified
overrides_applied: 0
requirements_verified:
  - REQ-DB-05
follow_ups:
  - source: 11-REVIEW.md WR-01
    item: "firestarter_test.sh:31 and write_test.sh:17 still reference deleted ./firestarter/data/database_generated.json"
    severity: warning
    in_scope: false
    note: "Explicitly out of scope per CONTEXT.md / orchestrator note; track as separate follow-up phase"
  - source: 11-REVIEW.md WR-02
    item: "build_db.py uses bare except: at lines 138-141, 158-163, 179-186 (silent chip drops, KeyboardInterrupt swallow)"
    severity: warning
    in_scope: false
    note: "Pre-existing in parse_db_2.py; not introduced by phase. CONTEXT.md locks 'no behavior changes inside the script'"
  - source: 11-REVIEW.md WR-03
    item: "build_db.py lacks requests.raise_for_status() and timeout; non-200 response can silently overwrite minipro_complete_db.json"
    severity: warning
    in_scope: false
    note: "Pre-existing in parse_db_2.py; not introduced by phase. CONTEXT.md locks 'no behavior changes inside the script'"
  - source: 11-01-PLAN.md known issues
    item: "verified field in minipro_complete_db.json no longer populated; get_eproms(verified=True) silently returns nothing"
    severity: info
    in_scope: false
    note: "Pre-existing bug; track as separate phase"
---

# Phase 11: Database Pipeline Cleanup — Verification Report

**Phase Goal:** "Consolidate the database build pipeline to a single canonical tool. Remove the legacy `parse_db.py` and its stale outputs, rename `parse_db_2.py` to `build_db.py`, and ensure the source `infoic.xml` is fetched from upstream at run time and never stored or committed in this project."

**Verified:** 2026-05-11T07:25:00Z
**Status:** passed
**Re-verification:** No — initial verification
**Phase commit (submodule):** `firestarter_app@29e310d`
**Phase commit (parent pointer bump):** `parent@5d2f337`

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Only one database build tool exists: `tools/build_db.py` | VERIFIED | `git ls-files tools/` in submodule returns exactly `tools/build_db.py` and `tools/pin-layouts.odt`. No `parse_db.py`, no `parse_db_2.py`. `ls firestarter_app/tools/` confirms working-tree state matches. |
| 2 | No `infoic*.xml` files in working tree; `.gitignore` prevents recommit | VERIFIED | `find firestarter_app -name 'infoic*.xml' -not -path './.git/*' ...` returns nothing. `firestarter_app/.gitignore` contains `tools/infoic*.xml`. After running `python tools/build_db.py` (which performs the upstream fetch), no `infoic.xml` appeared on disk — confirms in-memory fetch. |
| 3 | All doc/comment references point to `build_db.py` | VERIFIED | `grep -rn 'parse_db_2\|parse_db\.py' firestarter_app/ --exclude-dir=.git --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=test_env` returns **zero matches**. `CLAUDE.md` has 4 `build_db.py` references at lines 11, 19, 42, 69. `database.py` has 2 `build_db.py` comment references at lines 379, 487. |
| 4 | Running `build_db.py` from a fresh checkout produces a byte-identical `minipro_complete_db.json` | VERIFIED | `python firestarter_app/tools/build_db.py` ran successfully against upstream (network available); printed `Done! 743 chips processed.` After the run, `git status` in submodule shows `tools/` and `firestarter/data/` clean — i.e. the regenerated DB is byte-identical to the committed `minipro_complete_db.json`. SUMMARY.md also documents a pre-rename baseline diff with no changes. |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/tools/build_db.py` | Sole database build pipeline | VERIFIED | Exists (7474 bytes). Substantive: contains `MINIPRO_XML_URL`, `PROTOCOL_MAP`, `interpret_timing`, `main()` write of `minipro_complete_db.json`. Wired: doc references in `CLAUDE.md` and code comments in `database.py` point to it; `git log --follow tools/build_db.py` shows history through `parse_db_2.py` commit `8241257`. Data flows: executed successfully end-to-end producing 743 chips. |
| `firestarter_app/.gitignore` | Contains `tools/infoic*.xml` | VERIFIED | File contents include exactly the line `tools/infoic*.xml` adjacent to `tools/__pycache__/`. Glob matches `infoic.xml`, `infoic2.xml`, and any future `infoicN.xml` variant. |

All artifacts: VERIFIED.

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `firestarter_app/CLAUDE.md` | `tools/build_db.py` | doc references (4 occurrences updated) | WIRED | Lines 11, 19, 42, 69 each contain `build_db.py`. No `parse_db_2.py` or `parse_db.py` references remain. Confirmed via `grep -n 'build_db\|parse_db' CLAUDE.md`. |
| `firestarter_app/firestarter/database.py` | `tools/build_db.py` | comment references at lines 379, 487 | WIRED | Line 379: `# Read algorithm integer directly — set by build_db.py as minipro protocol_id`. Line 487: `# Use vpp_mv directly when available (integer millivolts from build_db.py)`. Confirmed via direct `grep -n` and via `git show 29e310d -- firestarter/database.py` diff (only 2 lines changed, both as expected). |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|---------------------|--------|
| `tools/build_db.py` | XML root → `processed_chips` dict | `requests.get(MINIPRO_XML_URL)` then `ET.fromstring(r.content)` | Yes (743 chips from upstream gitlab.com) | FLOWING |
| `firestarter/data/minipro_complete_db.json` | (output) | `build_db.py` `main()` writes via `json.dump` | Yes — file is 335,879 bytes, byte-identical to pre-rename baseline per SUMMARY | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `build_db.py` runs end-to-end against upstream and writes DB | `python firestarter_app/tools/build_db.py` | exit 0; "Done! 743 chips processed. Saved to .../minipro_complete_db.json" | PASS |
| Running the script leaves no `infoic*.xml` on disk (in-memory fetch only) | `find firestarter_app -name 'infoic*.xml' ...` post-run | no matches | PASS |
| Regenerated DB is byte-identical to committed copy | `git status` in submodule after run | tools/ and firestarter/data/ clean | PASS |
| `git log --follow` preserves rename history | `git log --follow tools/build_db.py` | shows `29e310d` then `8241257` (parse_db_2.py commit) | PASS |
| No stale references remain | `grep -rn 'parse_db_2\|parse_db\.py' firestarter_app/ --exclude-dir=.git ...` | zero matches | PASS |

### Probe Execution

No phase-declared probes (`scripts/*/tests/probe-*.sh`) for this refactor-only phase; the plan's Step 6 verification checks are functionally equivalent and were re-run live above. Not applicable.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-DB-05 | 11-01-PLAN | Single canonical `build_db.py`; upstream `infoic.xml` fetched at run time and never stored/committed; legacy `parse_db.py`, `infoic.xml`, `infoic2.xml`, `verified.txt`, `database_generated.json`, `pin-maps.json` removed | SATISFIED | All sub-clauses verified: (a) `tools/build_db.py` is the sole tool; (b) `MINIPRO_XML_URL` constant + `requests.get(...)` at runtime; (c) `.gitignore` blocks `tools/infoic*.xml`; (d) `git show 29e310d --stat` confirms deletion of `parse_db.py`, `infoic.xml`, `verified.txt`, `database_generated.json`, `pin-maps.json` (and SUMMARY documents `infoic2.xml` was untracked → bare `rm`). |

No orphaned requirements: REQUIREMENTS.md maps only REQ-DB-05 to Phase 11; all other DB-pipeline requirements are owned by Phase 01.

### Anti-Patterns Found

Scan target: files modified in commit `29e310d` (per SUMMARY key-files): `tools/build_db.py`, `.gitignore`, `CLAUDE.md`, `firestarter/database.py`.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter_app/tools/build_db.py` | 138-141, 158-163, 179-186 | bare `except:` | Info | Pre-existing in `parse_db_2.py`; not introduced by phase. Carried in `follow_ups`. Phase-locked "no behavior changes inside the script" makes this out-of-scope. |
| `firestarter_app/tools/build_db.py` | 158-163 | `requests.get(...)` missing `raise_for_status()` and `timeout` | Info | Pre-existing; same rationale as above. |
| `firestarter_app/firestarter/database.py` | 173 | `// `-style comment in Python (`# //_read_config_file(...)`) | Info | Pre-existing (review IN-03). Not in this phase's diff. |
| `firestarter_app/firestarter/database.py` | 359-368 | bare `None` no-op except body | Info | Pre-existing (review IN-01). Not in this phase's diff. |

No BLOCKER or WARNING level anti-patterns introduced by this phase. No `TBD`/`FIXME`/`XXX` debt markers added in phase commit.

### Collateral Drift (advisory)

| File | Issue | Severity | In Scope |
|------|-------|----------|----------|
| `firestarter_app/firestarter_test.sh:31` | `JSON_FILE='./firestarter/data/database_generated.json'` references deleted DB | Warning | No — out of scope per CONTEXT.md / orchestrator note |
| `firestarter_app/write_test.sh:17` | Same broken reference | Warning | No — same |

These are tracked in `follow_ups` frontmatter for a subsequent phase. They do not block REQ-DB-05 since REQ-DB-05 governs the build pipeline itself, not the test harness; and the plan's Known-Issues section + the orchestrator's note explicitly carve these out.

### Human Verification Required

None. All four observable truths verified programmatically. The rename is mechanical, byte-identity of the generated DB was reproduced live (network was available at verification time), and all reference updates are statically confirmed via `grep`.

### Gaps Summary

No gaps. Phase 11 cleanly delivered REQ-DB-05:

1. Single canonical `tools/build_db.py` — confirmed via `git ls-files tools/` and direct directory listing.
2. Legacy parser and stale inputs/outputs removed — confirmed via `git show 29e310d --stat` and `find` for absence.
3. Upstream-only XML fetch — confirmed by inspecting `build_db.py` source (`MINIPRO_XML_URL` + `requests.get`) and by running the script: no `infoic*.xml` materialized on disk post-run.
4. `.gitignore` glob `tools/infoic*.xml` in place.
5. Doc/comment references in `CLAUDE.md` (4) and `database.py` (2) all point to `build_db.py`; zero `parse_db_2` / `parse_db.py` references remain in the submodule (excluding `.git`, `__pycache__`, `.venv`, `test_env`).
6. Rename preserves history via `git mv` (verified with `git log --follow`).
7. Submodule commit `29e310d` and parent pointer bump `5d2f337` both landed and are correctly described.

Three WARNING-level findings from `11-REVIEW.md` (broken `database_generated.json` references in test shell scripts; bare `except:` blocks; missing `raise_for_status`/`timeout`) are recorded as `follow_ups` but explicitly out of scope per CONTEXT.md "no behavior changes inside the script" lock and per the orchestrator's note on advisory-only collateral. They do not affect REQ-DB-05 closure.

---

_Verified: 2026-05-11T07:25:00Z_
_Verifier: Claude (gsd-verifier)_

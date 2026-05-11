---
phase: 11-build-db-cleanup
reviewed: 2026-05-11T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - firestarter_app/tools/build_db.py
  - firestarter_app/.gitignore
  - firestarter_app/CLAUDE.md
  - firestarter_app/firestarter/database.py
findings:
  critical: 0
  blocker: 0
  warning: 3
  info: 6
  total: 9
status: issues_found
---

# Phase 11: Code Review Report

**Reviewed:** 2026-05-11
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Phase 11 is a refactor-only cleanup. The submodule commit `29e310d` is well-scoped: `git mv tools/parse_db_2.py -> tools/build_db.py` is a 100% similarity rename, the legacy `parse_db.py` and its generated/input artefacts are deleted, `.gitignore` is updated, and exactly the 4 doc-string references in `CLAUDE.md` and 2 comment lines in `database.py` (lines 379 and 487) are rewritten. Confirmed via `git diff 29e310d^ 29e310d`: no logic changes inside `build_db.py` or `database.py`. `git log --follow` confirms history of `build_db.py` correctly points back through `parse_db_2.py`.

The phase delivered what it claimed. However, the wider repository still contains stale references to artefacts that were just deleted, and `build_db.py` (now the canonical pipeline) contains several pre-existing defects that take on greater weight now that it is the only path. Those are the bulk of the findings below.

No BLOCKER / Critical issues were found in the four reviewed files.

## Warnings

### WR-01: Sibling shell scripts now point at a non-existent JSON database

**File:** `firestarter_app/firestarter_test.sh:31`, `firestarter_app/write_test.sh:17`
**Issue:** Both scripts still contain `JSON_FILE='./firestarter/data/database_generated.json'` and immediately `jq -e` against it. That file was deleted as part of phase-11 cleanup (see commit `29e310d` "Remove ... firestarter/data/database_generated.json"). The very first `jq -e` call will fail with "Could not open file" and the scripts will then enter the `if [ -z "$MEMORY_SIZE_HEX" ]` branch and `exit 1`. The hardware integration tests advertised in `firestarter_app/CLAUDE.md:10` (`./firestarter_test.sh [EPROM]`) are now broken by this phase. These files were not in the review scope for phase-11 but the deletion of their input was, so this is collateral drift that the phase should have caught.
**Fix:** Re-point both scripts at the new canonical file and reflect that fields are now nested under `electrical.*`. Minimal jq edit:
```bash
JSON_FILE='./firestarter/data/minipro_complete_db.json'
# ...
MEMORY_SIZE_HEX=$(jq -e --arg target_name "$EPROM_NAME" -r '
  .[] | .[] |
  select(.part_number == $target_name) |
  .electrical.size_bytes
' "$JSON_FILE")
HAS_CHIP_ID=$(jq -e --arg target_name "$EPROM_NAME" -r '
  .[] | .[] |
  select(.part_number == $target_name) |
  .programming.chip_id_check
' "$JSON_FILE")
# size_bytes is already decimal in the new DB, so drop the `MEMORY_SIZE_DECIMAL=$((MEMORY_SIZE_HEX))` step
```
Either land this fix in this phase, or open a follow-up phase before claiming the hardware test scripts work.

### WR-02: `build_db.py` swallows arbitrary exceptions during package decoding and silently drops chips

**File:** `firestarter_app/tools/build_db.py:179-186`, `:138-141`, `:158-163`
**Issue:** Three bare `except:` clauses:
- L179-186: `try ... except: continue` around `int(ic.get("package_details"), 16)` etc. — any chip whose XML attributes are missing or malformed is dropped without a single warning. Future minipro XML schema drift will cause silent coverage loss in the canonical DB.
- L138-141: `interpret_timing` swallows the bare `int(raw_hex, 16)` failure and falls back to `val = 0`, again without diagnostic.
- L158-163: the network fetch / parse path catches `Exception` and prints the message but exits without a stack trace.

Bare `except:` also catches `KeyboardInterrupt` / `SystemExit`, which is the documented Python anti-pattern. With this script now being the **sole** DB pipeline (per the phase summary), silent drops are the most likely source of the next "why is chip X missing?" bug.
**Fix:**
```python
try:
    pkg_val = int(ic.get("package_details"), 16)
    pin_count = (pkg_val & 0x7F000000) >> 24
    is_smd = pkg_val & 0x80000000
    is_serial = (pkg_val & 0x0000FF00) >> 8
    type_int = int(ic.get("type"), 16)
except (TypeError, ValueError) as e:
    print(f"WARN: skipping {ic.get('name')} — malformed attrs: {e}", file=sys.stderr)
    continue
```
And in `interpret_timing`:
```python
try:
    val = int(raw_hex, 16)
except (TypeError, ValueError):
    val = 0
```

### WR-03: `build_db.py` does not check HTTP status before parsing the response

**File:** `firestarter_app/tools/build_db.py:158-163`
**Issue:** `r = requests.get(MINIPRO_XML_URL)` followed immediately by `ET.fromstring(r.content)`. There is no `r.raise_for_status()` and no timeout. A 5xx error page or a captive-portal HTML response will reach the parser, which then either explodes inside the bare `except:` (with a generic "Error: ..." print) or — worse — parses an HTML body as XML and writes a near-empty DB to `minipro_complete_db.json`, **silently overwriting the good DB on disk**. Now that this is the sole canonical pipeline, that is a real data-loss vector for the next user who runs `python tools/build_db.py` while their network is misbehaving.
**Fix:**
```python
try:
    r = requests.get(MINIPRO_XML_URL, timeout=30)
    r.raise_for_status()
    root = ET.fromstring(r.content)
except (requests.RequestException, ET.ParseError) as e:
    print(f"Error fetching/parsing minipro XML: {e}", file=sys.stderr)
    sys.exit(1)
```
Optionally write to a tempfile and `os.replace` only after a non-empty parse to make the overwrite atomic.

## Info

### IN-01: `database.py:362, 367` use a bare expression `None` as a no-op except body

**File:** `firestarter_app/firestarter/database.py:359-368`
**Issue:** The `except (ValueError, TypeError):` bodies are literally the expression `None` followed by a commented-out logger call. `None` as a statement is dead and confusing — it looks like an attempted `return None` or `raise`. Pre-existing, but exposed now that the file is being touched.
**Fix:** Replace each `None` with `pass`, or just uncomment the `logger.warning(...)` debug line that the author clearly intended to ship.

### IN-02: `database.py` still ships a large commented-out block

**File:** `firestarter_app/firestarter/database.py:459-475`
**Issue:** The bottom of `get_eprom` contains ~16 lines of commented-out logic referring to a "concise" output mode that no longer exists in the new code path. Dead documentation rotting in place. Pre-existing.
**Fix:** Delete the comment block; git history preserves it if anyone wants to recover the logic.

### IN-03: `database.py:173` keeps a `//`-style comment in Python

**File:** `firestarter_app/firestarter/database.py:173`
**Issue:** `override_proms = None  # //_read_config_file("database_overrides.json")` — the `//` prefix is C/JS syntax. Combined with the fact that `firestarter/data/database_overrides.json` actually exists on disk, this looks like a half-finished feature that should either be wired in or removed.
**Fix:** Decide whether to load `database_overrides.json` or drop the dead reference; in either case strip the stray `//`.

### IN-04: `PROTOCOL_MAP` is now duplicated and divergent between `build_db.py` and `database.py`

**File:** `firestarter_app/firestarter/database.py:34-43`, `firestarter_app/tools/build_db.py:25-44`
**Issue:** `database.py` defines a `PROTOCOL_MAP` with 8 entries; `build_db.py` defines a `PROTOCOL_MAP` with 18 entries (and is the only one actually used — the one in `database.py` is currently dead code, no `PROTOCOL_MAP` references exist anywhere else in `firestarter/`). Now that `build_db.py` is the canonical pipeline, the stale copy in `database.py` will silently rot whenever upstream adds a protocol id. Pre-existing but elevated by phase-11's "single source of truth" framing.
**Fix:** Either delete `PROTOCOL_MAP` from `database.py` (it is unused — `grep -n PROTOCOL_MAP firestarter/` returns only the definition), or factor it into a shared module imported by both.

### IN-05: `VPP_VOLTAGES` mixes hex and decimal keys for the same values

**File:** `firestarter_app/tools/build_db.py:46-80`
**Issue:** The dict maps the *same* values under both `0x00`/`0` and `0x10`/`16`, etc., commented "Legacy Integer Keys". Because `0x00 == 0` in Python, these collide — the later entry wins. As written, the "12V" / "9V" / etc. strings happen to match, so this is functionally a no-op, but it is a latent footgun: if anyone edits one of the hex entries and forgets the decimal twin (or vice versa), the legacy lookup will silently disagree.
**Fix:** Drop the "Legacy Integer Keys" half — the call site at `build_db.py:217` already uses `voltages & 0xFF`, which is identical for both representations.

### IN-06: `interpret_timing` produces strings that `database.py` then ignores

**File:** `firestarter_app/tools/build_db.py:137-153`, `firestarter_app/firestarter/database.py:398`
**Issue:** `build_db.py` carefully formats `pulse_duration` as `"{val * 100} us"` / `"Algorithm Controlled"`, writes it to `programming.pulse_duration` in the JSON, and `database.py:398` then unconditionally writes `"pulse-delay": 0` with the trailing comment `# Not directly available in new format, may need parsing from string`. So the entire `interpret_timing` codepath produces output that no consumer reads. Pre-existing dead-data pipeline that the phase-11 reframing brings into focus.
**Fix:** Either parse the `us` value back out in `_map_data` (e.g., regex `^(\d+)\s*us$`) and assign it to `pulse-delay`, or stop emitting `pulse_duration` from `build_db.py`. Don't ship both halves of a no-op.

---

_Reviewed: 2026-05-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

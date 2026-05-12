---
phase: 02-naming-cleanup-wire-key-minipro-references
reviewed: 2026-05-12T00:00:00Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - CLAUDE.md
  - firestarter/CLAUDE.md
  - firestarter/src/json_parser.c
  - firestarter_app/CLAUDE.md
  - firestarter_app/MANIFEST.in
  - firestarter_app/firestarter/database.py
  - firestarter_app/pyproject.toml
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/check_dispatch.py
findings:
  critical: 0
  warning: 3
  info: 4
  total: 7
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-05-12
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

Phase 02 is a naming-cleanup phase consisting of mechanical renames and one
new diagnostic block (the D-15 wire round-trip in `check_dispatch.py`). The
mechanical renames look complete and consistent: `vpp` → `vpp_mv` is applied
atomically at the three load-bearing sites in `firestarter/src/json_parser.c`
(declaration `:25`, PROGMEM key `:62`, dispatch table `:74`, getter
`:308-310`); the wire emitter at `firestarter_app/firestarter/database.py:518`
emits `vpp_mv`; and the file rename `minipro_complete_db.json` →
`chip_database.json` lands consistently across `pyproject.toml:66`,
`MANIFEST.in:1`, `database.py:189`, `database.py:366` docstring, `build_db.py:12`
(OUTPUT_FILE), and `check_dispatch.py:2`/`:29`. The two deliberate preservations
(`MINIPRO_XML_URL` at `build_db.py:10`, `electrical.get("vpp", ...)` DB-schema
READ at `database.py:375`) match the phase-context decisions D-08 and D-09.

The new D-15 wire round-trip block at `check_dispatch.py:132-146` is sound in
the happy path but has three quality defects: it silently skips chips whose
`part_number` isn't in `EpromDatabase.proms`, it can double-emit the same
wire-key regression message for duplicated `part_number`s across manufacturers,
and it bypasses the `FIRESTARTER_DB_FILE` env override for the wire-emit portion
(the env var affects the iteration source but `EpromDatabase()` always loads
the canonical `chip_database.json` path, so test substitution is incomplete).

The most concrete defects are a stale `_PROTOCOL_OVERRIDES` reference in a
comment that points at a constant `build_db.py` doesn't actually define, an
unconditional `MANIFEST.in` `include` for a file (`avrdude.conf`) that does
not exist in the package, and packaging of `database_overrides.json` which the
code never loads (load site is commented out at `database.py:191`). The phase
context explicitly says MANIFEST.in + pyproject.toml were "aligned to real
shipping files" — these two items contradict that goal.

## Warnings

### WR-01: `MANIFEST.in` ships a file that does not exist (`avrdude.conf`)

**File:** `firestarter_app/MANIFEST.in:4`
**Issue:** Line 4 (`include firestarter/data/avrdude.conf`) references a file
that does not exist anywhere in the package tree (`find firestarter_app -name
"avrdude.conf"` returns empty). Phase context states the MANIFEST.in /
`pyproject.toml` `[tool.setuptools.package-data]` lists were aligned to "real
shipping files" — this line contradicts that. Behavior at `sdist` time:
setuptools emits a warning ("no previously-included files matching ... found")
but does not fail the build; behavior at `bdist_wheel` time: silently skipped.
The defect is that the manifest LIES about what's in the source distribution,
and a user reading the manifest will look for a file that the project deleted.
**Fix:** Remove the line.
```diff
 include firestarter/data/chip_database.json
 include firestarter/data/pinouts.json
 include firestarter/data/database_overrides.json
-include firestarter/data/avrdude.conf
 include firestarter/database.py
```

### WR-02: `database_overrides.json` packaged but never loaded; `pyproject.toml` and `MANIFEST.in` advertise it as shipping data

**File:** `firestarter_app/pyproject.toml:67`, `firestarter_app/MANIFEST.in:3`,
`firestarter_app/firestarter/database.py:191`
**Issue:** `pyproject.toml:67` and `MANIFEST.in:3` declare
`firestarter/data/database_overrides.json` as part of the shipping package
data, and the file exists on disk (3358 bytes). But `database.py:191` has the
load site commented out:
```python
override_proms = None  # //_read_config_file("database_overrides.json")
```
So the JSON ships in every wheel/sdist but the installed code never reads it.
Phase context: package-data was supposed to be aligned to "real shipping
files," meaning files the runtime actually uses. Either the file should be
loaded (un-comment `:191`) or it should be removed from packaging. Note the
oddly-formatted `# //` comment marker — `//` is not Python comment syntax,
just a dangling marker that suggests this was hastily disabled.
**Fix:** Decide one direction. If overrides are intentionally inert until a
future feature, drop the file from both `pyproject.toml:67` and
`MANIFEST.in:3`:
```diff
 [tool.setuptools.package-data]
 "firestarter" = [
     "data/chip_database.json",
-    "data/database_overrides.json",
     "data/pinouts.json",
 ]
```
```diff
 include firestarter/data/chip_database.json
 include firestarter/data/pinouts.json
-include firestarter/data/database_overrides.json
```
Otherwise restore the load site and replace the `# //` marker with a real Python
comment.

### WR-03: Stale `_PROTOCOL_OVERRIDES` reference in `check_dispatch.py` comment points at a constant `build_db.py` does not define

**File:** `firestarter_app/tools/check_dispatch.py:62`
**Issue:** The comment block at `:56-63` says:
```
# The safe handler is `configure_eeprom28c` (algorithm=0x0D); chips reach it after
# Plan 02 regenerates the DB with `_PROTOCOL_OVERRIDES` in build_db.py.
```
But `build_db.py` does NOT define `_PROTOCOL_OVERRIDES` anywhere; the
WARNING-5 algorithm flip is implemented as an inline 3-predicate conditional
at `build_db.py:239-247`. A reader following the comment to `build_db.py`
will grep for `_PROTOCOL_OVERRIDES`, find nothing, and lose confidence in the
correctness chain. This is a documentation-vs-code drift introduced during the
Plan 02-03 augmentation.
**Fix:** Replace the comment with an accurate description of the inline
conditional, citing line numbers in `build_db.py`:
```diff
-# The safe handler is `configure_eeprom28c` (algorithm=0x0D); chips reach it after
-# Plan 02 regenerates the DB with `_PROTOCOL_OVERRIDES` in build_db.py.
+# The safe handler is `configure_eeprom28c` (algorithm=0x0D); chips reach it
+# after the inline 3-predicate WARNING-5 override at build_db.py:239-247
+# flips proto_id from 0x07 to 0x0D for (DIP28_2764 + Flash/EEPROM + 0x07).
```

## Info

### IN-01: `check_dispatch.py` D-15 round-trip silently skips chips not registered in `EpromDatabase`

**File:** `firestarter_app/tools/check_dispatch.py:136-146`
**Issue:** The new wire-emit assertion guards on `if mapped:` (line 137). If
`db.get_eprom(part)` returns `None` — which happens when `part_number` is not
indexed by `EpromDatabase` (rare but possible if `db_raw` was iterated as a
disjoint test DB), the wire-key regression check is silently skipped. The
comment at `:133-135` acknowledges this ("Chips not registered in
EpromDatabase's index (rare) skip the wire assert") but the script never
reports HOW MANY chips were skipped, so a partial regression could pass
silently.
**Fix:** Count skipped chips and emit a summary line so partial coverage is
visible:
```python
wire_skipped = 0
...
if mapped:
    ...
else:
    wire_skipped += 1
...
print(f"PASS: all {total} chips ...; wire-emit checked on {total - wire_skipped} of {total} chips")
```

### IN-02: `check_dispatch.py` `FIRESTARTER_DB_FILE` env override applies only to iteration source, not to `EpromDatabase` lookup

**File:** `firestarter_app/tools/check_dispatch.py:27-30, :93, :136`
**Issue:** `DB_FILE` at `:27-30` honors `FIRESTARTER_DB_FILE` and is loaded
into `db_raw` at `:86-87`. But the `EpromDatabase()` singleton at `:93`
always loads the canonical `firestarter/data/chip_database.json` via
`database._read_config_file` (no env-var support). For a test invocation like
`FIRESTARTER_DB_FILE=/tmp/test_db.json python tools/check_dispatch.py`, the
dispatch scan reads `/tmp/test_db.json` but the wire round-trip reads the
canonical DB. Mismatched parts silently fall through `if mapped:` (IN-01) and
the test still reports PASS. This violates the principle of least surprise for
anyone using the env override.
**Fix:** Either (a) document that the env override only affects the dispatch
scan, or (b) construct `EpromDatabase` from the same DB. Option (b) requires
adding an alternate constructor / patching `_read_config_file`; option (a) is
a one-line docstring note.

### IN-03: `convert_to_programmer` `or` fallback conflates missing vs zero for `vpp_mv`

**File:** `firestarter_app/firestarter/database.py:510`
**Issue:**
```python
vpp_mv = full_eprom_data.get("vpp_mv") or int(full_eprom_data.get("vpp_volts", 0) * 1000)
```
The `or` short-circuits when `vpp_mv` is falsy. For a legitimate `vpp_mv == 0`
(SRAM, 5V EEPROM via `configure_eeprom28c` — no VPP regulator), the second
clause fires. If `vpp_volts` is also 0 the output is 0 (correct). But if
`vpp_volts` was populated by `_map_data` from a legacy `electrical.vpp` string
that happened to parse to a non-zero float (e.g., for a 28C chip that has
upstream `vpp="12V"` even though the override path doesn't need it), the wire
emits `vpp_mv: 12000` for a chip that the firmware must NOT pulse with 12V.
The phase touches this line via the `vpp_volts` internal-key rename, so the
defect is in scope. Prefer explicit None-check:
**Fix:**
```python
vpp_mv = full_eprom_data.get("vpp_mv")
if vpp_mv is None:
    vpp_mv = int(full_eprom_data.get("vpp_volts", 0) * 1000)
```
Note: I have not traced every chip in the current DB to confirm whether this
mismatch can actually be triggered post-Phase-13 (WARNING-5 override sets
algorithm to 0x0D but does not zero out `vpp_mv`). Worth confirming.

### IN-04: Bare `None` statements as exception suppressors in `database.py`

**File:** `firestarter_app/firestarter/database.py:380, :385`
**Issue:** Two `except` blocks contain a bare `None` expression as a no-op
placeholder where the original `logger.warning` was commented out:
```python
except (ValueError, TypeError):
    None
    # logger.warning(f"Invalid VPP value for {ic.get('part_number')}: {vpp_str}")
```
`None` is a valid expression statement (evaluates and discards), so this works,
but it's idiomatically `pass`. Pre-existing; the `vpp_str` line `:375` is in
the phase blast radius (it is the deliberate D-08 preservation of the legacy
DB-schema READ), and the immediately-following exception handler is in the
same code block. Worth tidying while the file is open.
**Fix:** Replace both `None` statements with `pass`, and either uncomment the
`logger.warning` lines or delete them (commented-out code is itself a code
smell):
```diff
         try:
             vpp = float(vpp_str)
         except (ValueError, TypeError):
-            None
-            # logger.warning(f"Invalid VPP value for {ic.get('part_number')}: {vpp_str}")
+            logger.warning(f"Invalid VPP value for {ic.get('part_number')}: {vpp_str}")
         try:
             vcc = float(vcc_str)
         except (ValueError, TypeError):
-            None
-            # logger.warning(f"Invalid VCC value for {ic.get('part_number')}: {vcc_str}")
+            logger.warning(f"Invalid VCC value for {ic.get('part_number')}: {vcc_str}")
```

---

## Out-of-Scope Observations (NOT findings — context for reviewers)

The following items were inspected during review and confirmed to be deliberate
phase-context decisions, not defects:

1. **`build_db.py:255` `"vpp": VPP_VOLTAGES.get(...)`** — the on-disk
   DB-schema KEY `electrical.vpp` (string "12V"), distinct from the wire key
   `vpp_mv`. Preserved per phase context (Plan 02-01 D-08).
2. **`build_db.py:10` `MINIPRO_XML_URL`** — the single load-bearing
   attribution to the upstream `infoic.xml` source. Preserved per D-09.
3. **`database.py:375` `electrical.get("vpp", "0")`** — same DB-schema READ
   as item 1, on the consumer side. Preserved per D-08-compat.
4. **`firestarter_app/firestarter/config.py:19` `database.json`** — user
   override file in `~/.firestarter/`. Distinct from `chip_database.json`.
   Out of scope; not in file list.
5. **`firestarter_test.sh` / `write_test.sh` `database_generated.json`** —
   WARNING-4 carry-over, not in this phase's file list.

---

_Reviewed: 2026-05-12_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

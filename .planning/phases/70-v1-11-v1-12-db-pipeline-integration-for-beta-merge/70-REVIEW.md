---
phase: 70-v1-11-v1-12-db-pipeline-integration-for-beta-merge
reviewed: 2026-06-16T08:34:54Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/check_dispatch.py
  - firestarter_app/tools/diff_db.py
  - firestarter_app/tools/check_mypy_watermark.py
  - firestarter_app/tests/test_audit_coverage_matrix.py
  - firestarter_app/tests/test_characterization.py
findings:
  critical: 1
  warning: 5
  info: 3
  total: 9
status: issues_found
---

# Phase 70: Code Review Report

**Reviewed:** 2026-06-16T08:34:54Z
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found

## Summary

Reviewed the v1.11/v1.12 DB-build pipeline integration: `build_db.py` (the
infoic.xml→chip_database.json decode that drives 12V VPP routing), the GATE-03
structural dispatch guard (`check_dispatch.py`), the GATE-02 diff gate
(`diff_db.py`), the mypy watermark gate, and two test suites.

All three gates currently exit 0 against the live 744-chip DB, and the
electrical-safety invariants that *are* implemented (DIP24_2816→0x0D,
no-vpp-pin structural guard, SRAM-never-configure_eprom) hold in the data. The
decode logic is heavily commented and mostly correct.

However, the central GATE-03 claim — the "D-03 HARD inverse guard" that a
non-supported chip must never reach a real firmware handler — is **not actually
enforced**. The detector list it depends on is never populated, and a
contradiction between two `build_db.py` override stages means the 9
adapter-required chips DO resolve to a real handler (`configure_eeprom28c`),
caught only by the runtime host guard rather than the gate. This undermines the
phase's primary safety claim and is the BLOCKER below. Several supporting
assertions are tautological dead code, and the decode path has an unguarded
crash surface on malformed upstream input.

## Critical Issues

### CR-01: GATE-03 "inverse guard" is dead code — non-supported→real-handler regression cannot be detected

**File:** `firestarter_app/tools/check_dispatch.py:167`, `:201-246`, `:387-398`, `:405-414`
**Issue:**
The list `non_supported_dispatchable` (declared line 167) is **never appended to
anywhere in the file** (confirmed: the only references are the declaration and
read-only uses at lines 318, 387, 411, 422). The code comments at lines 234-245
describe a FAIL condition — "a non-supported chip derives a real handler AND the
host guard would NOT refuse it" — but no code path implements that detection.

Consequently:
- The gate-failure branch `if non_supported_dispatchable:` (line 387) is
  unreachable.
- The assertion `assert not non_supported_dispatchable` (line 411) is
  tautological — the list is always `[]`.
- The assertion `assert non_dispatchable_count == non_supported_count`
  (line 405) is also tautological: both counters are incremented
  unconditionally inside the same `if chip_ss != "supported":` block (lines 202
  and 246) with no intervening `continue`, so they can never diverge.

This matters because the DB *does* contain a case this guard is supposed to
catch: the 9 `adapter-required` chips carry `algorithm == 0x0D`, which
`dispatch()` routes to the **real** handler `configure_eeprom28c` (verified
live). They are non-dispatchable in name only — the gate passes them solely
because the list is hard-wired empty. The stated safety net ("future-regression
detector") provides false confidence: if a chip ever lost its non-supported tag
while keeping a real handler, GATE-03 would still exit 0.

**Fix:** Actually populate the list when a non-supported chip resolves to a real
handler, so the host guard becomes a *verified* invariant rather than an assumed
one:
```python
REAL_HANDLERS = {
    "configure_eprom", "configure_sram", "configure_eeprom28c",
    "configure_flash_intel", "configure_flash3", "configure_flash4",
}
...
if chip_ss != "supported":
    non_supported_count += 1
    ...
    if handler in REAL_HANDLERS:
        # Cross-check the authoritative host guard for THIS chip rather than
        # asserting it covers all such chips by construction.
        try:
            resolve_chip(part, db)            # must raise ChipNotImplementedError
            non_supported_dispatchable.append(
                f"{mfg}/{part} proto=0x{proto:02X} handler={handler} "
                f"NOT refused by host guard"
            )
        except ChipNotImplementedError:
            pass                              # correctly refused — safe
    non_dispatchable_count += 1
```
At minimum, remove the two tautological assertions (lines 405-414) and the
unreachable `if non_supported_dispatchable:` branch, and stop advertising a
detector that does not exist — the current code reads as enforcement but is not.

## Warnings

### WR-01: `build_db.py` Step 4 overrides the NON_DISPATCHABLE_ALGO sentinel set in Site B — D-03 invariant comment is false

**File:** `firestarter_app/tools/build_db.py:409-411` (Site B) vs `:468-476` (Step 4)
**Issue:**
Site B demotes the 24-pin 5V-EEPROM family to the non-dispatchable sentinel:
`proto_id = NON_DISPATCHABLE_ALGO` (0x00), with a comment asserting "dispatch()
returns ERROR instead of configure_eprom (D-03 HARD invariant)." But these
chips resolve to `pinout_key == "DIP24_2816"` (variant_lo == 0x10), so the very
next override stage — Step 4, lines 468-476 — runs `if pinout_key ==
"DIP24_2816": proto_id = 0x0D` and **silently re-promotes** them to 0x0D
(`configure_eeprom28c`, a real handler). Verified live: all 9 `adapter-required`
chips ship with `algorithm: 13` (0x0D), not 0x00.

The net electrical outcome is *safe* (0x0D is the 5V no-VPP handler), so this is
not a hardware-damage path. But the in-code invariant the author relied on
("flagged chip → ERROR, never a working handler") is violated, and the only
thing actually preventing operation is the runtime host guard — exactly the
fragile single-point-of-failure CR-01 fails to verify. The `adapter-required`
reason string ("requires a dedicated DIP24 EEPROM adapter or firmware handler")
also becomes self-contradictory: the DB now *names* a working handler for the
chip.

**Fix:** Either (a) reassert the sentinel after Step 4 for non-supported chips
(`if _support_status != "supported": proto_id = NON_DISPATCHABLE_ALGO` placed
after all Rule 1/2/3 overrides and before `chip_entry` construction), or
(b) drop the Site B `NON_DISPATCHABLE_ALGO` demotion and its misleading comment
entirely and document that adapter-required safety rests solely on the host
guard. Do not leave the code claiming an invariant it does not hold.

### WR-02: Unguarded `int(None, 16)` crash on malformed/updated upstream XML

**File:** `firestarter_app/tools/build_db.py:329-333`
**Issue:**
The DECODE RAW DATA block calls `int(ic.get("variant"), 16)`,
`int(ic.get("protocol_id"), 16)`, `int(ic.get("flags"), 16)`,
`int(ic.get("voltages"), 16)`, and `int(ic.get("code_memory_size"), 16)` with
**no default and no try/except**. If any of these attributes is missing on an
`<ic>` element, `ic.get(...)` returns `None`, `int(None, 16)` raises
`TypeError`, and the entire database build aborts mid-stream. The preceding
filter block (lines 311-318) is wrapped in `try/except: continue`, and
`pin_map` (line 337) correctly supplies a `"0"` default — so the hardening is
inconsistent: this block is the one place left unprotected. Since the source is
a remotely-fetched, externally-maintained `infoic.xml` (URL at line 11), a
future upstream schema change can crash `build_db.py` with an opaque traceback.

**Fix:** Wrap the decode block in the same `try/except: continue` pattern used
at lines 311-318 (with a `WARN: skipping {name} — malformed fields` message), or
supply explicit defaults and skip the chip when a required field is absent.

### WR-03: GATE-02 does not fail on unexpected NEW chips — contract overstated

**File:** `firestarter_app/tools/diff_db.py:480-496`, `:508`
**Issue:**
The gate's failure set is `failures = list(unexplained) + missing_chips`
(line 508). New chips are **excluded** from this set: a new chip that is not a
Rule-1 unblock only prints a `WARN:` line (line 491) and does not affect the
exit code. The module docstring (lines 11-13) states exit 0 means "all changed
chips explained by a cited root-cause rule; N new chips confirmed (Rule 1
unblock)", but in practice a regression that *adds* an unexpected chip (e.g. a
future `resolve_pinout_key` change that classifies a previously-skipped chip)
passes the gate silently. Given the baseline is the pinned integrated output
(0 diffs today), this is latent, but the gate's stated job — proving every
delta is attributable — is not actually enforced for additions.

**Fix:** Include non-Rule-1 new chips in the failure set, or downgrade the
docstring/PASS-line wording to make clear that additions are reported but never
block. Preferred:
```python
unexpected_new = [k for k in new_chips
                  if not (cu_idx[k][1].get("pinout") == "DIP24_2816"
                          and cu_idx[k][1].get("programming", {}).get("algorithm") == 0x0D)]
failures = list(unexplained) + missing_chips + unexpected_new
```

### WR-04: `vpp-exceeds-max` chips still publish `vpp_mv: 25000` in the wire-facing DB

**File:** `firestarter_app/tools/build_db.py:608-621`, `:654-663`
**Issue:**
For the 4 `vpp-exceeds-max` NMOS chips, `proto_id` is demoted to
`NON_DISPATCHABLE_ALGO` but the emitted `electrical.vpp` ("25V") and
`electrical.vpp_mv` (25000) retain the over-ceiling value (verified live). The
RURP boost ceiling is 22000 mV. The host guard is supposed to refuse these
chips before any wire dict is built, but per CR-01 that invariant is not
verified by the gate, and the DB itself carries a value that — if ever
serialized to the firmware — requests 25V on hardware that maxes at ~22V. Defense
in depth would clamp or null the wire voltage for non-supported chips so the DB
never contains a physically-unsafe programming voltage even as a latent field.

**Fix:** For chips with `support_status == "vpp-exceeds-max"`, either omit
`vpp_mv`/set it to 0, or keep the human-readable `vpp` string for `info` display
but zero the wire-facing `vpp_mv`. Pair this with CR-01 so the gate proves no
non-supported chip's voltage can reach the wire.

### WR-05: INTEL `2732,2732A,M2732,M2732A` blocks the programmable 21V M2732A variant

**File:** `firestarter_app/tools/build_db.py:603-621`
**Issue:**
The "highest VPP wins" NMOS loop (lines 604-607) iterates aliases and keeps the
max VPP. The INTEL entry `2732,2732A,M2732,M2732A` contains both `M2732` (25V,
over ceiling) and `M2732A` (21V, programmable). Highest-wins resolves the whole
combined entry to 25V / `vpp-exceeds-max`, so the legitimately-programmable
2732A/M2732A variants are blocked because they share one DB record with M2732.
The code comments (lines 108-114, 600-602) acknowledge the "combined entry"
ambiguity and call highest-wins "conservative", so this is a known trade-off —
but it silently denies a supported chip. SGS-THOMSON/ST list `M2732A` separately
(correctly resolved to 21V supported), demonstrating the entry-granularity
problem is upstream-data-shaped, not fundamental.

**Fix:** Document this denial explicitly in the operator-facing
`unsupported_reason` for combined entries (e.g. "M2732A (21V) is programmable
but shares an upstream record with 25V M2732; override via
~/.firestarter/database.json"), so an operator with a 2732A understands why it
is refused rather than assuming the part is unsupported.

## Info

### IN-01: Unused imports flagged with `# noqa: F401` in test_characterization.py

**File:** `firestarter_app/tests/test_characterization.py:30-36`, `:45`
**Issue:** `os`, `sys`, `tempfile`, `Path`, and `MSG_OK_READY` are imported and
immediately suppressed with `# noqa: F401`. They are genuinely unused (each test
re-imports `subprocess`/`sys`/`Path` locally where needed). Carrying dead
top-level imports plus suppression comments is noise.
**Fix:** Delete the unused imports rather than suppressing the linter; re-add if a
future test needs them.

### IN-02: `interpret_timing` swallows all exceptions into a silent `0`

**File:** `firestarter_app/tools/build_db.py:276-279`
**Issue:** `except Exception: val = 0` masks any malformed `pulse_delay`
(including `None`) as 0 µs with no diagnostic. A chip with a corrupt timing
field would silently ship "0 us", which a downstream consumer cannot distinguish
from a legitimate zero.
**Fix:** Narrow to `(ValueError, TypeError)` and emit a `WARN:` to stderr naming
the chip when the parse fails, mirroring the WARN discipline used elsewhere in
the file.

### IN-03: `_map_data` uses bare `None` expression statements as no-op except bodies

**File:** `firestarter_app/firestarter/database.py:404`, `:409` (called by check_dispatch's WIRE-02 path)
**Issue:** The `except (ValueError, TypeError):` blocks contain a lone `None`
expression statement (line 404, 409) followed by a commented-out
`logger.warning`. `None` as a statement is a no-op that reads like a mistake;
combined with commented-out logging, an invalid VPP/VCC string is silently
defaulted to 0 with no trace. (Pre-existing, but exercised by the WIRE-02
round-trip in `check_dispatch.main`.)
**Fix:** Replace the `None` no-op with either `pass` or, preferably, restore the
`logger.warning` so a malformed voltage string surfaces.

---

_Reviewed: 2026-06-16T08:34:54Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

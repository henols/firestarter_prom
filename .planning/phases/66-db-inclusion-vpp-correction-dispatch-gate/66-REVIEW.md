---
phase: 66-db-inclusion-vpp-correction-dispatch-gate
reviewed: 2026-06-12T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/check_dispatch.py
  - firestarter_app/tools/diff_db.py
  - firestarter_app/tests/test_build_db_inclusion.py
findings:
  critical: 2
  warning: 5
  info: 3
  total: 10
status: issues_found
---

# Phase 66: Code Review Report

**Reviewed:** 2026-06-12
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Phase 66 introduces a `support_status` taxonomy (`supported` / `protocol-not-implemented` /
`adapter-required` / `vpp-exceeds-max`), DB-01/02 inclusion gates, DB-03 NMOS true-VPP
correction with "highest-VPP-wins", and a reworked dispatch gate. The stated HARD invariant
is: *"a non-`supported` chip must NEVER be wired to a working dispatch handler (no
protocol/mem_type change that makes it programmable)."*

That invariant is **violated by 13 of the 14 non-supported chips**. The `adapter-required`
and `vpp-exceeds-max` chips keep `algorithm` 0x0B (EPROM_LEGACY), which dispatches to the real
`configure_eprom` handler — the exact 12V-VPP hardware-damage path the classification was
created to prevent. The reworked `check_dispatch.py` gate does **not** detect this because it
only flags *supported → not_implemented*, never *non-supported → real handler*; it then prints
a PASS message falsely asserting all 14 are "non-dispatchable." This is the central defect of
the phase and is reproducible against the regenerated DB.

Secondary concerns: the two `KNOWN_PROTOCOLS` constants are documented as must-keep-in-sync
mirrors but are intentionally (and load-bearingly) divergent, so following the sync instruction
breaks the gate; and the highest-VPP-wins logic marks the combined `2732,2732A,M2732,M2732A`
entry `vpp-exceeds-max`, silently blocking the programmable 21V M2732A part.

## Critical Issues

### CR-01: Non-supported chips are wired to a working dispatch handler (HARD invariant violated)

**File:** `firestarter_app/tools/build_db.py:411-431, 551-571`
**Issue:**
The DB-02 `adapter-required` gate (L411-431) and the DB-03 `vpp-exceeds-max` gate (L562-569)
set `support_status` but leave `proto_id` unchanged at `0x0B`/`0x07`/`0x08`. Empirically, on
the regenerated `chip_database.json`, 13 of 14 non-supported chips dispatch to a real handler:

```
('ATMEL','AT28C04,AT28HC04','adapter-required','0xb','configure_eprom')
('ATMEL','AT28C16,AT28HC16,AT28HC16L','adapter-required','0xb','configure_eprom')
('MICROCHIP memory','28C04A','adapter-required','0xb','configure_eprom')
('NEC','UPD28C04','adapter-required','0xb','configure_eprom')
('INTEL','2732,2732A,M2732,M2732A','vpp-exceeds-max','0xb','configure_eprom')
('INTEL','M2716,M2716M','vpp-exceeds-max','0xb','configure_eprom')
('ST','ETC2716,M2716','vpp-exceeds-max','0xb','configure_eprom')
... (13 total)
```

`configure_eprom` engages the 12V VPP boost regulator and asserts `P1_VPP_ENABLE` — which the
phase's own comment (L405-408, L417-423) identifies as the hardware-damage path for the
24-pin EEPROMs (12V onto socket pin 21 = WE). Because the host runtime (`database.py`
`get_eprom` / `convert_to_programmer`) never inspects `support_status`, a user running
`firestarter write AT28C04` (or any of these 13 parts) gets a fully-formed wire command and the
firmware drives the damage path. `support_status` is documentation-only; nothing enforces it.

**Fix:** The invariant requires non-supported chips be made non-dispatchable. Two acceptable
approaches — pick one and apply at both gates:

```python
# Option A (preferred per "no protocol change that makes it programmable"):
# Set algorithm to a sentinel the firmware/host treat as non-dispatchable.
NON_DISPATCHABLE_ALGO = 0x00  # dispatch() returns ERROR/not_implemented for proto 0
...
if (pin_count == 24 and proto_id in (0x07,0x08,0x0B) and (flags & 0x10)):
    _support_status = "adapter-required"
    _unsupported_reason = (...)
    proto_id = NON_DISPATCHABLE_ALGO   # <-- prevents configure_eprom routing
...
if _nmos_vpp_mv is not None and _nmos_vpp_mv > RURP_VPP_CEILING_MV:
    _support_status = "vpp-exceeds-max"
    _unsupported_reason = (...)
    proto_id = NON_DISPATCHABLE_ALGO   # <-- prevents configure_eprom routing
```
If `proto_id` cannot change (to preserve display info), instead gate at the host: have
`get_eprom_config` / `convert_to_programmer` raise on `support_status != "supported"` for
write/program operations. Whichever path is chosen, CR-02's gate must be updated to actually
prove the invariant.

### CR-02: Dispatch gate does not enforce the HARD invariant and prints a false PASS

**File:** `firestarter_app/tools/check_dispatch.py:162-174, 273-279`
**Issue:**
The reworked `not_implemented` bucket only fails when a chip routes to the `not_implemented`
*handler* AND is `supported` (L165-171). There is **no check** for the inverse and far more
dangerous case: a *non-supported* chip routing to a *real* handler (`configure_eprom`,
`configure_eeprom28c`, etc.). As a result, the 13 chips from CR-01 pass the gate, and the
summary line (L273-279) prints:

```
PASS: all 744 chips scanned; 730 supported; 14 non-supported (non-dispatchable, expected); ...
```

The phrase "14 non-supported (non-dispatchable, expected)" is factually wrong — 13 of those 14
ARE dispatchable to `configure_eprom`. The gate that exists specifically to catch this class of
hazard reports green. The docstring (L1-16) and "D-10 Assertion 3" comment (L134-135) both
claim the invariant is enforced; it is not.

**Fix:** Add an explicit assertion that any non-supported chip resolves to a non-dispatchable
handler, and correct the summary wording:

```python
non_supported_dispatchable = []  # add near other bucket lists
...
# inside the per-chip loop, after computing handler:
if chip_ss != "supported" and handler not in ("not_implemented", "ERROR"):
    non_supported_dispatchable.append(
        f"{mfg}/{part} support_status={chip_ss} proto=0x{proto:02X} -> {handler} "
        f"(HARD invariant: non-supported chip wired to a working handler)"
    )
...
# include non_supported_dispatchable in the failure gate and print block.
```
Only after CR-01 is fixed will this assertion pass; until then it correctly fails. Also change
the summary to count actually-non-dispatchable chips rather than asserting it unconditionally.

## Warnings

### WR-01: KNOWN_PROTOCOLS "mirror" is load-bearingly divergent — sync instruction breaks the gate

**File:** `firestarter_app/tools/check_dispatch.py:65-83` vs `firestarter_app/tools/build_db.py:98-113`
**Issue:**
`check_dispatch.py` L67-68 says "Local mirror of build_db.py:83 — source of truth. Keep in sync
if KNOWN_PROTOCOLS changes." But the two sets are intentionally different: `build_db.py` includes
`0x34` (so X88C64P passes the inclusion gate); `check_dispatch.py` omits `0x34` (so Assertion 2,
L158-161 — "a protocol-not-implemented chip must have proto NOT in KNOWN_PROTOCOLS" — passes for
X88C64P). The two constants therefore have *different semantics* (inclusion-gate set vs
implemented-handler set) and must NOT be equal. A maintainer who follows the literal "keep in
sync" comment and adds `0x34` to the check_dispatch mirror will cause Assertion 2 to falsely fail
on X88C64P. This is a maintenance trap encoded directly in the comments.

**Fix:** Rename the check_dispatch set to reflect its real meaning and document why it diverges:

```python
# Protocols that have a REAL firmware handler. Deliberately a SUBSET of
# build_db.py's KNOWN_PROTOCOLS — 0x34 is in build_db's inclusion gate but is
# NOT implemented, so it is intentionally absent here. Do NOT "sync" 0x34 in:
# Assertion 2 relies on 0x34 being absent so X88C64P (protocol-not-implemented)
# validates correctly.
IMPLEMENTED_PROTOCOLS = { 0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39 }
```

### WR-02: Highest-VPP-wins silently blocks the programmable M2732A on combined entries

**File:** `firestarter_app/tools/build_db.py:557-571`
**Issue:**
For the upstream combined entry `INTEL/2732,2732A,M2732,M2732A`, the alias set contains both
`M2732` (25000 mV) and `M2732A` (21000 mV). "Highest VPP wins" selects 25000 mV → `vpp_mv`
exceeds the 22000 mV ceiling → the whole record is marked `vpp-exceeds-max`. But the same record
*is* the programmable 21V M2732A. So a chip the operator could legitimately program (21V ≤ 22V)
is classified unprogrammable. The test `test_nmos_m2732a_supported` (test file L190-215)
deliberately excludes combined entries (`"M2732A" in al and "M2732" not in al`), so this loss of
function is invisible to the test suite. The L570-571 comment claims "M2732A (21V) is within the
RURP ceiling" — true in isolation, but the combined-entry path contradicts it.

**Fix:** Confirm the intended behavior. If a combined entry should remain programmable at the
lower safe voltage, the override must not promote a record to `vpp-exceeds-max` when at least one
alias is within the ceiling; or the build should split the combined record. At minimum, document
that combined NMOS entries are intentionally conservatively blocked, and add a test asserting the
`2732,2732A,M2732,M2732A` record's resulting `support_status` so the behavior is pinned.

### WR-03: NMOS status override can clobber an earlier adapter-required/protocol classification

**File:** `firestarter_app/tools/build_db.py:562-569`
**Issue:**
The NMOS block unconditionally assigns `_support_status = "vpp-exceeds-max"` (and overwrites
`_unsupported_reason`) when `_nmos_vpp_mv > ceiling`, regardless of whether an earlier gate
already set `adapter-required` (L416) or `protocol-not-implemented` (L391). If a chip ever
matched both an earlier gate and an NMOS alias above the ceiling, the earlier (possibly more
hazardous) classification and its reason string are silently lost. No current chip hits this, but
the ordering is fragile and undocumented as a precedence rule.

**Fix:** Make precedence explicit — only downgrade to `vpp-exceeds-max` when the status is still
`supported`, mirroring the existing comment style:

```python
if _nmos_vpp_mv is not None and _nmos_vpp_mv > RURP_VPP_CEILING_MV:
    if _support_status == "supported":
        _support_status = "vpp-exceeds-max"
        _unsupported_reason = (...)
    # else: a stronger gate already classified this chip; keep it.
```

### WR-04: diff_db NEW-chips check hardcodes Rule-1; Phase 66 new chips spuriously WARN

**File:** `firestarter_app/tools/diff_db.py:421-439`
**Issue:**
The NEW-chips reporting block is hardcoded to expect every new chip to be a "Rule 1 unblock
(DIP24_2816 + algo=0x0D)" and prints `WARN: new chip ... is NOT a Rule 1 unblock` otherwise.
Phase 66 adds new chips that are NOT Rule-1: X88C64P (`protocol-not-implemented`, algo 0x34) and
the 9 `adapter-required` 24-pin EEPROMs (algo 0x07/0x08/0x0B, pinout DIP24_2716). All of these
will print the spurious WARN even though they are the intended Phase-66 inclusions. It does not
fail the gate (WARN only), but the report is misleading for the very phase under review.

**Fix:** Generalize the new-chip verification to recognize the Phase-66 inclusion shapes
(non-`supported` chips with a non-empty `unsupported_reason`) in addition to Rule-1 unblocks,
and only WARN on a new chip that matches none of the expected shapes.

### WR-05: support_status is never consumed at runtime — no enforcement layer exists

**File:** `firestarter_app/firestarter/database.py:466-555` (consumers absent)
**Issue:**
`grep` across `database.py`, `eprom_operations.py`, `cli_handlers.py`, and `chip_resolver.py`
finds zero references to `support_status` / `adapter-required` / `vpp-exceeds-max` /
`protocol-not-implemented`. The field is written by `build_db.py` and read only by the offline
`check_dispatch.py` gate. There is no path that prevents `firestarter write <non-supported>` from
proceeding. Combined with CR-01 (algorithm left dispatchable), the taxonomy provides no actual
operator protection. Even if CR-01 is fixed by leaving algorithm intact and gating at the host,
that host gate does not yet exist.

**Fix:** Add a runtime guard in the write/program path (e.g., in `chip_resolver.resolve_chip` or
`cli_handlers`) that refuses to build a programmer command when
`support_status != "supported"`, surfacing `unsupported_reason` to the operator. This is the
enforcement half of the feature and should land before the catalog inclusions ship.

## Info

### IN-01: Bare `except:` clauses swallow all exceptions including SystemExit/KeyboardInterrupt

**File:** `firestarter_app/tools/build_db.py:301, 346`
**Issue:** `interpret_timing` (L299-302) and the per-chip decode (L340-347) use bare `except:`,
which catches `KeyboardInterrupt`/`SystemExit` and hides real decode bugs as silent `continue`/0.
**Fix:** Narrow to the expected exception types, e.g. `except (ValueError, TypeError):`.

### IN-02: Test docstrings claim "EXPECTED TO FAIL (RED)" but tests pass post-regeneration

**File:** `firestarter_app/tests/test_build_db_inclusion.py:12-15` and per-test RED notes
**Issue:** The module docstring and several test docstrings (e.g., L70-73, L120-123, L167-169)
assert the tests must fail until Plan 03 lands. Plan 03 has landed (the DB now has 744
`support_status` entries and the suite passes 7/7). The RED notes are now stale and misleading to
a future reader debugging the suite.
**Fix:** Update the docstrings to GREEN/post-implementation wording, or remove the RED notes.

### IN-03: Test suite does not assert the HARD non-dispatchability invariant

**File:** `firestarter_app/tests/test_build_db_inclusion.py` (whole file)
**Issue:** The scaffold verifies presence of `support_status`, reasons, and VPP values, but no
test asserts that non-supported chips are non-dispatchable — the single most important safety
property of the phase. CR-01 would have been caught by such a test.
**Fix:** Add a test that, for every chip with `support_status != "supported"`, asserts its
`programming.algorithm` does not resolve to a real handler (reuse the `check_dispatch.dispatch`
table), so the invariant is pinned in CI rather than only in the offline gate.

---

_Reviewed: 2026-06-12_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

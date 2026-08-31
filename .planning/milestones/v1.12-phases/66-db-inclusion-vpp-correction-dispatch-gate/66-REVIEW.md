---
phase: 66-db-inclusion-vpp-correction-dispatch-gate
reviewed: 2026-06-12T00:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/check_dispatch.py
  - firestarter_app/tests/test_build_db_inclusion.py
findings:
  critical: 1
  warning: 4
  info: 2
  total: 7
status: issues_found
---

# Phase 66: Code Review Report (66-04 gap-closure re-review)

**Reviewed:** 2026-06-12
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Phase 66 plan 66-04 is a SAFETY gap-closure whose stated invariant is: a chip with
`support_status != "supported"` must NEVER resolve to a real programming handler
(`configure_eprom`, etc.) that would drive 12V VPP onto a pin. The implementation
sets `proto_id = NON_DISPATCHABLE_ALGO (0x00)` at Site B (adapter-required) and
Site C (vpp-exceeds-max) in `build_db.py`, adds a `non_supported_dispatchable`
gate bucket plus PASS-line rework in `check_dispatch.py`, and adds a CI invariant
test in `test_build_db_inclusion.py`.

The build-time demotion to `0x00` is correctly ordered and holds for all 14
non-supported chips in the regenerated DB; `check_dispatch.py` exits 0 and reports
"14 chips confirmed non-dispatchable." However, **the safety invariant is verified
ONLY against a simulated dispatch model that does not match the real host+firmware
runtime path.** Tracing the actual production path (`database._map_data` → wire →
firmware `configure_memory`) shows the vpp-exceeds-max NMOS EPROMs (M2716/M2732)
STILL reach `configure_eprom` (12V VPP) at runtime. The gate, the mirrored test,
and the PASS message all report this case as safe — they are not truthful for that
bucket. This is the exact hardware-damage path the phase exists to close, so it is
a BLOCKER.

(Note: this artifact previously held a broader 66-wide review covering diff_db.py;
it is replaced here with the focused 66-04 re-review of the 3 changed files in the
diff range 4454d07^..HEAD.)

## Critical Issues

### CR-01: vpp-exceeds-max NMOS EPROMs still dispatch to `configure_eprom` (12V VPP) at runtime — the gate's safety claim is false

**File:** `firestarter_app/tools/build_db.py:584`, `firestarter_app/firestarter/database.py:395-407`, `firestarter_app/tools/check_dispatch.py:152-154`

**Issue:**
The fix demotes `proto_id` to `0x00` for non-supported chips and proves safety via
`check_dispatch.dispatch(0x00, _ALGO_MEM_TYPE.get(0x00))`. `_ALGO_MEM_TYPE.get(0x00)`
is `None`, so the simulated `mem_type` fallback returns `"ERROR"` — apparently safe.

But the **real host runtime** does NOT derive `mem_type` that way. In
`database.py::_map_data` (lines 395-407), when `protocol_id` is `0` (falsy) the
code falls through to an `electrical.type`-string heuristic:

```python
protocol_id = programming.get("algorithm", 0)   # == 0 for non-supported chips
if protocol_id and protocol_id in _ALGO_MEM_TYPE:
    determined_type = _ALGO_MEM_TYPE[protocol_id]
else:
    type_str = electrical.get("type", "")
    determined_type = 1                          # default EPROM
    if "Flash" in type_str: determined_type = 2
    elif "SRAM" in type_str: determined_type = 4
```

For the vpp-exceeds-max NMOS parts (M2716/M2732), `build_db.py` leaves
`electrical.type == "UV-EPROM"` (the proto==0 re-derivation block at
build_db.py:553-561 hits no branch, so `_etype` keeps its flags-based value, and
these UV-EPROMs lack the 0x10 erasable flag). The host therefore computes
`determined_type = 1 (TYPE_EPROM)` and sends `{"protocol-id": 0, "type": 1, ...}`
on the wire.

The firmware (`firestarter/src/proms/memory.cpp`) protocol==0 fallback then runs:
```cpp
if (handle->protocol != 0) { configure_not_implemented(handle); return; }
if (handle->mem_type == TYPE_EPROM) { configure_eprom(handle); return; }  // <-- HIT (TYPE_EPROM==1)
```
`configure_eprom` engages the 12V VPP boost regulator — exactly the
hardware-damage path 66-04 was supposed to eliminate for these chips.

Verified empirically against the regenerated DB (4 vpp-exceeds-max entries):
```
INTEL/M2716:       etype='UV-EPROM' proto=0 -> HOST mem_type=1; check_dispatch sim handler=ERROR
SGS-THOMSON/M2716: etype='UV-EPROM' proto=0 -> HOST mem_type=1; check_dispatch sim handler=ERROR
ST/M2716:          etype='UV-EPROM' proto=0 -> HOST mem_type=1; check_dispatch sim handler=ERROR
INTEL/2732:        etype='UV-EPROM' proto=0 -> HOST mem_type=1; check_dispatch sim handler=ERROR
```
The simulated handler is `ERROR` (the gate's "safe" verdict) but the host-derived
`mem_type` is `1`, which firmware routes to `configure_eprom`.

Additionally, `chip_resolver.resolve_chip` and `eprom_operations` perform NO
`support_status` check (grep of `firestarter/*.py` for `support_status` returns
zero matches), so `firestarter M2716 write file.bin` is not blocked anywhere on the
host before the command is transmitted.

The adapter-required 24-pin EEPROMs happen to escape this because their
`electrical.type == "Flash/EEPROM"` yields `determined_type = 2`, which is NOT in
the firmware's mem_type fallback (only TYPE_EPROM=1/SRAM=4/FLASH_3=3/FLASH_4=5),
so firmware fails closed. That is incidental — it depends on a string-substring
match, not on `support_status` — and does not protect the UV-EPROM bucket.

**Fix (defense-in-depth; prefer the runtime guard, and also close the gate gap):**

1. Authoritative runtime guard — make `support_status` load-bearing instead of
   relying on `algorithm==0` round-tripping safely through the `electrical.type`
   fallback. In `database.py::_map_data` (or `chip_resolver.resolve_chip`), refuse
   to emit a program-capable command for non-supported chips:
```python
if full.get("support_status", "supported") != "supported":
    raise ChipNotImplementedError(
        f"{name}: {full.get('unsupported_reason', 'unsupported on this hardware')}"
    )
```
2. Close the simulation gap so the gate models the real host derivation. In
   `check_dispatch.py`, derive `mem_type` the same way `_map_data` does (fall back
   to the `electrical.type` string when `proto == 0`) before calling `dispatch`:
```python
proto = chip.get("programming", {}).get("algorithm", 0) or 0
mt = _ALGO_MEM_TYPE.get(proto)
if not proto:                              # mirror database._map_data fallback
    etype = chip.get("electrical", {}).get("type", "")
    mt = 1
    if "Flash" in etype: mt = 2
    elif "SRAM" in etype: mt = 4
handler = dispatch(proto, mt)
```
   With this change the gate (and the mirrored test) would correctly FAIL on the
   current DB, surfacing the M2716/M2732 hazard. The same change must be applied to
   `test_build_db_inclusion.py::test_non_supported_chips_are_non_dispatchable`,
   which imports the same `dispatch`/`_ALGO_MEM_TYPE` and inherits the identical
   blind spot.

## Warnings

### WR-01: CI gate and invariant test share one dispatch model — neither validates the real runtime path

**File:** `firestarter_app/tools/check_dispatch.py:152-154`, `firestarter_app/tests/test_build_db_inclusion.py:329-343`

**Issue:** The test deliberately imports `check_dispatch._ALGO_MEM_TYPE` and
`check_dispatch.dispatch` (lines 332, 341-342) and re-runs the exact computation
the gate performs. This is not independent verification — the test cannot catch any
defect the gate misses, including CR-01. Both the module docstring and the test
docstring assert the invariant is "pinned in CI," but the pin is anchored to a
simulation that diverges from `database._map_data` (which IS the production path).

**Fix:** Drive the invariant test through the real production path
(`EpromDatabase().convert_to_programmer(get_eprom(part))` and assert the emitted
`type`/`protocol-id` cannot reach a 12V handler), OR at minimum align both gate and
test mem_type derivation with `_map_data` per CR-01 fix #2 and add a direct
assertion on the wire dict's `type` field for non-supported chips.

### WR-02: PASS summary hardcodes "0 non_supported_dispatchable" instead of the derived count

**File:** `firestarter_app/tools/check_dispatch.py:315`

**Issue:** The PASS line prints the string literal `"0 non_supported_dispatchable"`.
It is "true" only because the gate `sys.exit(1)`s whenever the list is non-empty, so
the literal is structurally correct today. But it is decoupled from the data: a
future refactor that drops the early-exit, or that populates the list without adding
it to the abort condition (line 238), would print a falsely reassuring "0" while a
violation exists. The phase brief explicitly asks whether the PASS message is
truthful — a hardcoded safety count is a latent truthfulness hazard.

**Fix:** Print the live count and add a belt-and-suspenders assert:
```python
assert not non_supported_dispatchable
print(f"... {len(non_supported_dispatchable)} non_supported_dispatchable; ...")
```

### WR-03: `non_dispatchable_count` and `non_supported_count` encode the same invariant but are never cross-checked

**File:** `firestarter_app/tools/check_dispatch.py:158-183`, `309-317`

**Issue:** `non_dispatchable_count` is incremented (line 183) only inside the
`else` arm of the `handler not in (...)` check, itself nested under
`if chip_ss != "supported":`. The PASS line advertises it as
"`{n} chips confirmed non-dispatchable`". The relationship
`non_dispatchable_count == non_supported_count` (14 == 14 today) holds ONLY because
every non-supported chip currently dispatches safely in the simulation. If a future
DB contained an unsafe entry, these two counters would disagree
(e.g. `non_supported_count=14`, `non_dispatchable_count=13`), yet the mismatch is
never asserted — the gate relies entirely on the `non_supported_dispatchable` list
membership. The redundant counter adds confusion without adding a check.

**Fix:** After the loop, assert the relationship to make the counters load-bearing:
```python
assert non_dispatchable_count == non_supported_count, (
    f"{non_supported_count - non_dispatchable_count} non-supported chip(s) "
    f"resolved to a real handler"
)
```

### WR-04: `KNOWN_PROTOCOLS` triplicated with an intentional membership divergence (0x34) enforced only by a comment

**File:** `firestarter_app/tools/check_dispatch.py:73-87` vs `firestarter_app/tools/build_db.py:98-113`

**Issue:** `check_dispatch.KNOWN_PROTOCOLS` is a deliberate SUBSET of
`build_db.KNOWN_PROTOCOLS` — it omits `0x34` so D-10 assertion 2 passes for
X88C64P. The divergence is correct but fragile: it is enforced solely by prose
("Do NOT add 0x34 here"). Anyone "syncing" the two sets — a natural reaction to the
`0x34` mismatch — silently breaks assertion 2, and nothing fails. A third copy in
`firestarter_app/CLAUDE.md` drifts independently.

**Fix:** Derive the mirror in code so the divergence is explicit and self-checking:
```python
from build_db import KNOWN_PROTOCOLS as _BUILD_KNOWN
KNOWN_PROTOCOLS = _BUILD_KNOWN - {0x34}  # 0x34 included at build but "not implemented"
```
or add a test asserting `check_dispatch.KNOWN_PROTOCOLS == build_db.KNOWN_PROTOCOLS - {0x34}`.

## Info

### IN-01: Bare `except:` clauses swallow all exceptions including KeyboardInterrupt

**File:** `firestarter_app/tools/build_db.py:308-311`, `349-356`

**Issue:** `interpret_timing` uses a bare `except:` (line 310) that catches
`BaseException` (including `KeyboardInterrupt`/`SystemExit`) and silently defaults
`val = 0`. The package-decode site (line 355) uses the same bare `except:` and
silently `continue`s on any malformed `ic`. These predate 66-04 but live in the
reviewed file and mask malformed-XML data-quality issues.

**Fix:** Narrow to `except (ValueError, TypeError):` so unexpected failures and
interrupts propagate.

### IN-02: fm1608 provenance log prints a stale back-computed "from" algorithm

**File:** `firestarter_app/tools/build_db.py:532-537`

**Issue:** Inside the fm1608 block `proto_id` is set to `0x28` (line 519), then the
log at line 534 prints `0x{proto_id-0x21:02X}` (= `0x07`) to reconstruct the source
algorithm. This back-computation only yields the intended `0x07`; for chips that
arrived via `0x08`/`0x0B` the displayed "from" value is wrong (an `0x0B`-origin FRAM
is mislabeled `0x07`). Cosmetic (stderr provenance only).

**Fix:** Capture the original algorithm into a local before the override and log
that value verbatim instead of arithmetic on the post-override value.

---

_Reviewed: 2026-06-12_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

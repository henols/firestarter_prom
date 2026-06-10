# Phase 62: Dispatch Baseline Capture + check_dispatch Update — Research

**Researched:** 2026-06-10
**Domain:** Python host tooling — dispatch simulation gate + snapshot artifact
**Confidence:** HIGH (all findings verified by direct codebase inspection)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Baseline is a one-time committed human-readable reference snapshot (NOT
  a regenerate-and-diff golden gate). The live regression pin is the existing firmware
  Unity test + the new `not_implemented` FAIL assertion in `check_dispatch.py`
  (0 not-implemented chips).
- **D-02:** Phase 62 is HOST-ONLY — touches only `firestarter_app`. The existing
  firmware Unity test in `test_configure_memory.cpp` is accepted as-is as the
  GATE-01 firmware baseline. Do NOT fork the firmware v1.12 branch. The app
  sub-repo must be on `v1.12-protocol-dispatch-hardening` (forked off `beta`)
  before committing Phase 62 work.
- **D-03:** Two distinct failure buckets:
  - `protocol == 0` + unrecognized `mem_type` → existing `"ERROR"` bucket
  - `protocol != 0` + unrecognized protocol → new `"not_implemented"` bucket
- **D-04:** Snapshot records the dispatch triple per chip:
  `part → { algorithm, mem_type, resolved_handler }`. Exclude `vpp_mv`/wire fields.

### Claude's Discretion

- Exact snapshot file format/location and filename (within `firestarter_app`), and the
  precise dispatch-order arrangement of the explicit `0x35`/`0x39` cases vs. the
  `protocol != 0` arm in `check_dispatch.py::dispatch()` — constrained by:
  mirror `memory.cpp::configure_memory` order line-for-line, and the
  `protocol != 0 → not_implemented` arm must sit **after** all explicit protocol cases
  and **before** the `protocol == 0` `mem_type` fallback.

### Deferred Ideas (OUT OF SCOPE)

- Strengthen firmware Unity dispatch test with pointer-level `configure_eprom`
  assertion — Phase 64 (TEST-01).
- Golden-snapshot regenerate-and-diff dispatch gate (Phase-59 style) — not adopted.
- `vpp_mv` / wire-field regression baseline — Phase 66.
- `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` catalog constant — Phase 63.
- Firmware `configure_not_implemented()` + fail-closed `configure_memory` — Phase 64.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GATE-01 | Pre-removal dispatch baseline captured (every DB chip's resolved handler + representative cases) and committed BEFORE fallback is guarded | §Baseline Artifact Design — snapshot iteration pattern; §Firmware Baseline (existing Unity test) |
| GATE-02 | `check_dispatch.py` gains `not_implemented` arm mirroring `protocol != 0` guard, plus FAIL assertion that 0 DB chips resolve to not-implemented; pre-existing `0x35`/`0x39` dispatch-mirror gap reconciled; exits clean across all 743 chips | §Dispatch Gap Analysis; §check_dispatch.py Modification Plan |
</phase_requirements>

---

## Summary

Phase 62 has two deliverables. First, a committed human-readable snapshot artifact
that records the dispatch triple (`algorithm`, `mem_type`, `resolved_handler`) for
every chip in the 743-chip database — frozen before any v1.12 code changes land.
Second, a surgical update to `check_dispatch.py::dispatch()` that closes a
pre-existing mirror gap (`0x35`/`0x39` had no explicit cases and fell through to
`"ERROR"`) and adds a new `protocol != 0 → "not_implemented"` arm that models the
Phase-64 firmware fail-closed guard.

The gap analysis (direct codebase inspection) confirms: 0 chips in the current
743-chip DB use `0x35` or `0x39` — both are excluded from `KNOWN_PROTOCOLS` in
`build_db.py`. Therefore the new `not_implemented` FAIL assertion in the scan loop
must exit with `0 not-implemented chips (PASS)` by construction. The `dispatch()`
edit is surgical (3 changes: add `0x35`/`0x39` to the `0x05` arm; insert
`protocol != 0 → "not_implemented"` arm; update `_ALGO_MEM_TYPE` map).

**Primary recommendation:** The snapshot should be a single JSON file at
`firestarter_app/tools/baseline/dispatch_baseline.json`, sorted by manufacturer
then part number for stable diffs, containing the dispatch triple per chip plus
a `meta` block recording the DB chip count and date. This mirrors the precedent set
by `chip_database.baseline.json` in the same `tools/baseline/` directory.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Dispatch simulation gate | Host tooling (`tools/`) | — | Pure Python simulation of firmware dispatch; no serial/HW needed |
| Baseline snapshot artifact | Host sub-repo (`firestarter_app`) | Meta planning docs | D-02: host-only, committed in app sub-repo |
| Firmware baseline (GATE-01 pin) | Firmware sub-repo (Unity test) | — | Existing; accepted as-is (D-02); no Phase 62 firmware touch |
| `dispatch()` mirror discipline | `check_dispatch.py` | `memory.cpp` | Python mirror must follow C++ source-of-truth order line-for-line |

---

## Firmware Dispatch Source-of-Truth

### `configure_memory()` Full Dispatch Order

[VERIFIED: direct read of `/workspaces/firestarter/src/proms/memory.cpp` lines 45–119]

```cpp
// memory.cpp::configure_memory() — canonical dispatch, lines 73–118
if (handle->protocol == 0x10) {          // step 1
    configure_flash_intel(handle); return;
}
if (handle->protocol == 0x0D) {          // step 2
    configure_eeprom28c(handle); return;
}
if (handle->protocol == 0x06) {          // step 3
    configure_flash3(handle); return;
}
if (handle->protocol == 0x05 ||          // step 4 — THE RELEVANT GROUPING
    handle->protocol == 0x35 ||
    handle->protocol == 0x39) {
    configure_flash4(handle); return;
}
if (handle->protocol == 0x07 ||          // step 5
    handle->protocol == 0x08 ||
    handle->protocol == 0x0B) {
    configure_eprom(handle); return;
}
if (handle->protocol == 0x0E ||          // step 6
    handle->protocol == 0x27 ||
    handle->protocol == 0x28 ||
    handle->protocol == 0x29) {
    configure_sram(handle); return;
}
// steps 7–10: mem_type fallback chain (protocol == 0 / legacy)
if (handle->mem_type == TYPE_EPROM)      { configure_eprom(handle);  return; }
else if (handle->mem_type == TYPE_SRAM)  { configure_sram(handle);   return; }
else if (handle->mem_type == TYPE_FLASH_TYPE_3) { configure_flash3(handle); return; }
else if (handle->mem_type == TYPE_FLASH_TYPE_4) { configure_flash4(handle); return; }
// step 11: error
LOG_ERROR_ID_U8(MSG_ERR_MEM_TYPE_UNSUPPORTED, handle->mem_type);
handle->response_code = RESPONSE_CODE_ERROR;
```

The 11-step canonical order from `firestarter/CLAUDE.md` § "Protocol Dispatch":
[VERIFIED: direct read of `/workspaces/firestarter/CLAUDE.md` lines 36–46]

1. `protocol == 0x10` → `configure_flash_intel()`
2. `protocol == 0x0D` → `configure_eeprom28c()`
3. `protocol == 0x06` → `configure_flash3()`
4. `protocol ∈ {0x05, 0x35, 0x39}` → `configure_flash4()`
5. `protocol ∈ {0x07, 0x08, 0x0B}` → `configure_eprom()`
6. `protocol ∈ {0x0E, 0x27, 0x28, 0x29}` → `configure_sram()`
7. `mem_type == 1 (TYPE_EPROM)` → `configure_eprom()`
8. `mem_type == 4 (TYPE_SRAM)` → `configure_sram()`
9. `mem_type == 3 (TYPE_FLASH_TYPE_3)` → `configure_flash3()`
10. `mem_type == 5 (TYPE_FLASH_TYPE_4)` → `configure_flash4()`
11. error: `MSG_ERR_MEM_TYPE_UNSUPPORTED`

**Critical insight:** Steps 1–6 are the protocol-prefix chain. Steps 7–10 are
the `mem_type` fallback chain, reached ONLY when `protocol` is 0 (or not matched
by any step 1–6 case). Step 11 is the error path for `protocol == 0` with unknown
`mem_type`. The Phase-64 fail-closed firmware change will insert a new
`protocol != 0 → not_implemented` arm between step 6 and step 7.

---

## Dispatch Gap Analysis

### Current `check_dispatch.py::dispatch()` State

[VERIFIED: direct read of `/workspaces/firestarter_app/tools/check_dispatch.py` lines 75–95]

```python
def dispatch(protocol, mem_type):
    if protocol == 0x10:
        return "configure_flash_intel"
    if protocol == 0x0D:
        return "configure_eeprom28c"
    if protocol == 0x06:
        return "configure_flash3"
    if protocol == 0x05:          # <-- MISSING 0x35 and 0x39
        return "configure_flash4"
    if protocol in (0x07, 0x08, 0x0B):
        return "configure_eprom"
    if protocol in (0x0E, 0x27, 0x28, 0x29):
        return "configure_sram"
    # mem_type fallback — matches memory.cpp:83-95
    return {
        1: "configure_eprom",
        4: "configure_sram",
        3: "configure_flash3",
        5: "configure_flash4",
    }.get(mem_type, "ERROR")
```

**Gaps (confirmed by `dispatch(0x35, None) -> "ERROR"` and `dispatch(0x39, None) -> "ERROR"`):**
[VERIFIED: runtime test in devcontainer]

1. `protocol == 0x05` arm is missing `0x35` and `0x39` — both fall through to the
   `mem_type` dict which returns `"ERROR"` because `_ALGO_MEM_TYPE.get(0x35)` is
   `None`.
2. No `protocol != 0` arm exists — the fallback dict is reached for ANY non-zero
   unrecognized protocol, silently routing it through `mem_type` (the VPP hazard).

**Why PASS today:** 0 chips in the 743-chip DB use `0x35` or `0x39`.
[VERIFIED: runtime count → 0 chips; `KNOWN_PROTOCOLS` excludes both from `build_db.py` lines 108–122]

### `_ALGO_MEM_TYPE` Gap

The `_ALGO_MEM_TYPE` dict at lines 38–50 maps protocol → firmware mem_type for the
fallback path. It currently has no entries for `0x35` or `0x39` because they are
not in `KNOWN_PROTOCOLS`. After the edit, `dispatch()` will have explicit cases for
`0x35`/`0x39` (never reaching `_ALGO_MEM_TYPE`), but the dict should also be
updated for consistency (add `0x35: 5, 0x39: 5` — same `TYPE_FLASH_TYPE_4` as
`0x05`) so it documents the full protocol→mem_type picture.

---

## `check_dispatch.py` Modification Plan

### What to Change in `dispatch()`

[VERIFIED: source inspection of check_dispatch.py + memory.cpp]

**Change 1:** Extend the `protocol == 0x05` arm to include `0x35` and `0x39`,
matching the `memory.cpp` step 4 grouping:

```python
# BEFORE (line 83):
if protocol == 0x05:
    return "configure_flash4"

# AFTER:
if protocol in (0x05, 0x35, 0x39):
    return "configure_flash4"
```

**Change 2:** Insert a `protocol != 0 → "not_implemented"` arm AFTER all explicit
protocol cases (after the `0x0E/0x27/0x28/0x29` arm at line 87) and BEFORE the
`mem_type` fallback dict. This models the Phase-64 firmware guard:

```python
    if protocol in (0x0E, 0x27, 0x28, 0x29):
        return "configure_sram"
    # Phase-64 mirror: non-zero unrecognized protocol → not_implemented
    # (In firmware: protocol != 0 guard before the mem_type chain)
    if protocol != 0:
        return "not_implemented"
    # mem_type fallback chain — protocol == 0 only (backward-compat)
    return {
        1: "configure_eprom",
        4: "configure_sram",
        3: "configure_flash3",
        5: "configure_flash4",
    }.get(mem_type, "ERROR")
```

The `protocol != 0` check fires only for protocols that passed through all 6
explicit arms above without matching — i.e. truly unrecognized non-zero protocols.
For `0x05`, `0x35`, `0x39`, etc., the explicit arms above match first and return
before reaching this line.

### What to Change in `_ALGO_MEM_TYPE`

Add two entries for documentation completeness (they will never be reached by
the new explicit dispatch arms, but the dict should be complete):

```python
_ALGO_MEM_TYPE = {
    0x05: 5,   # FLASH_AMD_STD  → TYPE_FLASH_TYPE_4
    0x35: 5,   # FLASH_EEPROM   → TYPE_FLASH_TYPE_4  (NEW)
    0x39: 5,   # FLASH_EEPROM2  → TYPE_FLASH_TYPE_4  (NEW)
    ...        # rest unchanged
}
```

### What to Change in `main()` Scan Loop

Add a `not_implemented` accumulator list + FAIL print following the established
bucket pattern. Insert it between the `errors` check and the `sram_in_eprom` check
(or at the top of the bucket group):

```python
not_implemented = []
# ... in the chip loop, after handler = dispatch(proto, mt):
if handler == "ERROR":
    errors.append(f"{mfg}/{part} proto=0x{proto:02X} mem_type={mt}")
    continue
if handler == "not_implemented":
    not_implemented.append(
        f"{mfg}/{part} proto=0x{proto:02X}"
    )
    continue  # not_implemented chips have no handler — skip remaining checks
```

In the exit block, add the `not_implemented` check:

```python
if (
    errors
    or not_implemented
    or sram_in_eprom
    ...
):
    if not_implemented:
        print(
            f"FAIL: {len(not_implemented)} chips route to not_implemented "
            f"(protocol != 0, not in KNOWN_PROTOCOLS):"
        )
        for e in not_implemented[:20]:
            print(f"  {e}")
        if len(not_implemented) > 20:
            print(f"  ... and {len(not_implemented) - 20} more")
```

Update the PASS summary line to include the new bucket:

```python
print(
    f"PASS: all {total} chips have a valid dispatch path; "
    f"0 not-implemented chips; "
    f"0 SRAM chips route to configure_eprom; "
    ...
)
```

**Note on `continue` placement:** The `not_implemented` arm must use `continue`
to skip the safety checks below it (BLOCKER-2, GATE-03, WARNING-5, WIRE-02).
Those checks are predicated on a chip reaching a real handler; a `not_implemented`
chip should not be evaluated for VPP hazard (it has no handler to route to).

---

## Baseline Artifact Design

### What to Capture (D-04)

The snapshot records the dispatch triple per chip. Each entry has:
- `part` (part_number from DB)
- `algorithm` (protocol name string from `PROTOCOL_MAP`, e.g. `"EPROM_STD"`)
- `algorithm_id` (hex protocol value, e.g. `"0x07"`) — included for human readability
- `mem_type` (integer from `_ALGO_MEM_TYPE`)
- `resolved_handler` (string, e.g. `"configure_eprom"`)

Excludes `vpp_mv`, `pinout`, `electrical.type`, and wire fields (D-04).

### Recommended Format: JSON with `meta` block

[ASSUMED: format/location within Claude's Discretion; constrained to `firestarter_app`]

```json
{
  "meta": {
    "generated": "2026-06-10",
    "db_chip_count": 743,
    "description": "Dispatch baseline: protocol → handler mapping for every DB chip, captured before Phase 64 fail-closed guard lands."
  },
  "chips": [
    {
      "manufacturer": "AMD",
      "part": "AM27C010",
      "algorithm": "EPROM_STD",
      "algorithm_id": "0x07",
      "mem_type": 1,
      "resolved_handler": "configure_eprom"
    },
    ...
  ]
}
```

### Recommended Location

`firestarter_app/tools/baseline/dispatch_baseline.json`

Rationale: [VERIFIED: `tools/baseline/` already exists and contains `chip_database.baseline.json`]
- Consistent with Phase 56's precedent — all baseline snapshots in `tools/baseline/`.
- Not in `firestarter/data/` (that directory holds runtime data, not planning artifacts).
- The `tools/` subtree is the right location for pipeline/gate tooling artifacts.

### Stable Sort Order for Diff-Friendliness

Sort by `manufacturer` then `part` (both ascending alphabetically). This matches
the sort order of `chip_database.json` (dict keys are manufacturers) and makes
the snapshot stable across regenerations.

### How to Generate the Snapshot

The snapshot generator can be a standalone Python script or a short inline script
invoked during the plan's execution. It reuses the same iteration pattern as
`check_dispatch.py::main()`:

```python
import json
from tools.check_dispatch import dispatch, _ALGO_MEM_TYPE
from tools.build_db import PROTOCOL_MAP

with open("firestarter/data/chip_database.json") as f:
    db = json.load(f)

chips = []
for mfg, chip_list in sorted(db.items()):
    if not isinstance(chip_list, list):
        continue
    for chip in chip_list:
        proto = chip.get("programming", {}).get("algorithm", 0) or 0
        mt = _ALGO_MEM_TYPE.get(proto)
        handler = dispatch(proto, mt)
        algo_name = PROTOCOL_MAP.get(proto, f"UNKNOWN_0x{proto:02X}")
        chips.append({
            "manufacturer": mfg,
            "part": chip.get("part_number", "<unknown>"),
            "algorithm": algo_name,
            "algorithm_id": f"0x{proto:02X}",
            "mem_type": mt,
            "resolved_handler": handler,
        })

snapshot = {
    "meta": {
        "generated": "2026-06-10",
        "db_chip_count": len(chips),
        "description": "...",
    },
    "chips": sorted(chips, key=lambda c: (c["manufacturer"], c["part"])),
}
with open("tools/baseline/dispatch_baseline.json", "w") as f:
    json.dump(snapshot, f, indent=2)
```

**Important:** The snapshot is generated BEFORE the `dispatch()` edit (to capture
the current fallback-present state). If the snapshot is generated after the
`dispatch()` edit, the 0x35/0x39 entries would show `configure_flash4` instead of
`ERROR` — which is acceptable for a "current behavior" snapshot, but D-01 says
"before any v1.12 code changes land." The safest approach: generate snapshot first,
then edit `dispatch()`.

**Observed dispatch triple counts (current DB, pre-edit):**
[VERIFIED: runtime enumeration in devcontainer]

| Algorithm | mem_type | Handler | Chip count |
|-----------|----------|---------|-----------|
| EEPROM_POLL | 1 | configure_eeprom28c | 84 |
| EPROM_LEGACY | 1 | configure_eprom | 30 |
| EPROM_QUICK | 1 | configure_eprom | 127 |
| EPROM_STD | 1 | configure_eprom | 170 |
| FLASH_AMD_ALT | 3 | configure_flash3 | 190 |
| FLASH_AMD_STD | 5 | configure_flash4 | 27 |
| FLASH_INTEL | 1 | configure_flash_intel | 39 |
| SRAM_24PIN | 4 | configure_sram | 2 |
| SRAM_32PIN | 4 | configure_sram | 20 |
| SRAM_512K_1M | 4 | configure_sram | 20 |
| SRAM_STD | 4 | configure_sram | 34 |
| **Total** | | | **743** |

11 unique (algorithm, mem_type, handler) triples. 0 chips use 0x35 or 0x39.

---

## Firmware Baseline (GATE-01, D-02)

### Existing Unity Tests: Accepted As-Is

[VERIFIED: direct read of `/workspaces/firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`]

The two GATE-01 representative-case pins already exist in `test_configure_memory.cpp`:

```cpp
// Pin 1: legacy fallback intact (protocol=0, mem_type=1 → configure_eprom)
void test_protocol_zero_with_mem_type_eprom_dispatches_eprom(void) {
    firestarter_handle_t h = make_handle(0, 1, CMD_READ);  /* TYPE_EPROM = 1 */
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}

// Pin 2: unknown (protocol=0, mem_type=99) → RESPONSE_CODE_ERROR
void test_unknown_protocol_with_unknown_mem_type_errors(void) {
    firestarter_handle_t h = make_handle(0, 99, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}
```

13 positive tests also exist (one per KNOWN_PROTOCOLS entry, including `0x35` and
`0x39` via `test_protocol_0x35_dispatches_flash4` and
`test_protocol_0x39_dispatches_flash4`). Per D-02 these are accepted as-is. Phase
62 adds NO firmware tests.

**Run command for the existing firmware baseline:**
```bash
# From firestarter/ sub-repo (firmware NOT touched in Phase 62)
pio test -e native -f "*test_dispatch*"
```

---

## Branch Action Required

[VERIFIED: `cd /workspaces/firestarter_app && git branch --show-current` → `v1.11-infoic-decode-correctness`]

The `firestarter_app` sub-repo is currently on `v1.11-infoic-decode-correctness`.
Per D-02, the planner must include a Wave 0 task to create and switch to the
`v1.12-protocol-dispatch-hardening` branch (forked off `beta`) before committing
any Phase 62 work.

```bash
cd firestarter_app
git checkout beta
git pull origin beta  # or equivalent
git checkout -b v1.12-protocol-dispatch-hardening
```

---

## Standard Stack

This phase is pure Python host tooling — no new packages. All tools already
installed.

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12 (devcontainer) / 3.9 (CI target) | Runtime |
| ruff | 0.15.16 | Lint + format gate |
| pytest | 9.0.3 | Test runner |
| json (stdlib) | — | Snapshot I/O |

[VERIFIED: devcontainer versions from `python3 --version`, `pip show ruff`, `pip show pytest`]

**No new packages needed.** The snapshot generator and dispatch edit both use
only stdlib + existing project imports.

---

## Package Legitimacy Audit

No new packages installed this phase. Section not applicable.

---

## Architecture Patterns

### Recommended Project Structure Changes

```
firestarter_app/
├── tools/
│   ├── check_dispatch.py        # MODIFIED: dispatch() + main() scan loop
│   └── baseline/
│       ├── chip_database.baseline.json  # existing (Phase 56)
│       └── dispatch_baseline.json       # NEW (Phase 62 GATE-01 snapshot)
```

### Pattern: Per-Bucket Failure List

The existing `main()` scan loop idiom (replicate exactly for `not_implemented`):

```python
# Accumulator (top of main, alongside other bucket lists)
not_implemented = []

# Inside chip loop, after handler = dispatch(proto, mt):
if handler == "not_implemented":
    not_implemented.append(f"{mfg}/{part} proto=0x{proto:02X}")
    continue  # skip VPP/wire checks for chips with no handler

# Exit block predicate (add not_implemented to the OR chain)
if (
    errors
    or not_implemented
    or sram_in_eprom
    ...
):
    if not_implemented:
        print(
            f"FAIL: {len(not_implemented)} chips route to not_implemented "
            f"(protocol != 0, not in KNOWN_PROTOCOLS):"
        )
        for e in not_implemented[:20]:
            print(f"  {e}")
        if len(not_implemented) > 20:
            print(f"  ... and {len(not_implemented) - 20} more")
```

### Anti-Patterns to Avoid

- **Generating snapshot AFTER `dispatch()` edit:** If the snapshot is generated
  after the edit, 0x35/0x39 entries change from `ERROR` to `configure_flash4`.
  Generate snapshot first; edit `dispatch()` second.
- **Using `continue` incorrectly in chip loop:** `not_implemented` chips must
  `continue` before the VPP/wire safety checks (those checks are only meaningful
  for chips with a real handler).
- **Placing `protocol != 0` arm before explicit protocol cases:** The arm must
  come AFTER all 6 explicit protocol arms. The explicit arms (0x10, 0x0D, 0x06,
  0x05/0x35/0x39, 0x07/0x08/0x0B, 0x0E/0x27/0x28/0x29) match known protocols
  first; only the residual unknown non-zero protocols reach the new arm.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Snapshot sort/JSON | Custom sort logic | `json.dump(..., sort_keys=False)` + explicit `sorted()` on the chips list by (mfg, part) |
| Chip enumeration | New DB parser | Reuse `check_dispatch.py` iteration pattern — already battle-tested across 743 chips |
| Protocol name lookup | Custom table | `from tools.build_db import PROTOCOL_MAP` |

---

## Common Pitfalls

### Pitfall 1: Snapshot Generated After Dispatch Edit

**What goes wrong:** If `dispatch()` is edited before the snapshot is written, the
snapshot will show `configure_flash4` for 0x35/0x39 chips (which would be 0 chips
anyway, but the intent is to capture pre-edit state).
**How to avoid:** Wave 1 = snapshot; Wave 2 = edit. Never reorder.

### Pitfall 2: `not_implemented` Arm Before Explicit Cases

**What goes wrong:** If `protocol != 0` is placed before the explicit `0x10`,
`0x0D`, `0x06`, etc. arms, ALL known protocols return `"not_implemented"` — the
gate fails spectacularly with 743 FAIL chips.
**How to avoid:** The arm is the last `if` before the `mem_type` dict. All explicit
arms above it have already caught their protocols. Only residual non-zero protocols
fall through.
**Warning signs:** Running `python tools/check_dispatch.py` after the edit and
seeing a massive FAIL count instead of 0 not-implemented.

### Pitfall 3: Missing `continue` After `not_implemented` Check

**What goes wrong:** Without `continue`, a `not_implemented` chip falls through
to the BLOCKER-2/GATE-03/WIRE-02 safety checks below, which are predicated on
`handler == "configure_eprom"` etc. This is harmless for the current DB (0 chips)
but creates a latent bug for Phase 66 when gap-protocol chips are added.
**How to avoid:** Add `continue` immediately after appending to `not_implemented`.

### Pitfall 4: Ruff/Format Drift (py3.12 vs py3.11)

**What goes wrong:** The devcontainer runs Python 3.12 and ruff 0.15.16. CI
targets Python 3.9. f-string backslash syntax and some UP rules behave differently
between versions.
**How to avoid:** Run `ruff check tools/check_dispatch.py` and
`ruff format --check tools/check_dispatch.py` in the devcontainer before committing.
The new code must pass both. Avoid f-string backslashes; use `0x{proto:02X}` not
`f"0x{proto:02X}"` inside other f-strings with backslashes.

### Pitfall 5: `_ALGO_MEM_TYPE` Lookup Returns `None` for 0x35/0x39

**What goes wrong:** The current `_ALGO_MEM_TYPE` has no entry for 0x35 or 0x39.
If the `dispatch()` edit correctly handles these with explicit arms, `_ALGO_MEM_TYPE`
is never consulted for them. But if the explicit arm is accidentally not added,
`mt = _ALGO_MEM_TYPE.get(proto)` returns `None`, and `dispatch(0x35, None)` falls
through to `{1: ..., 4: ..., 3: ..., 5: ...}.get(None, "ERROR")` → `"ERROR"`.
**How to avoid:** Add `0x35: 5, 0x39: 5` to `_ALGO_MEM_TYPE` as defensive entries.
Confirm with `dispatch(0x35, None)` in a quick test.

---

## Runtime State Inventory

This is a pure host-tooling phase — no rename, no refactor of runtime-registered
state. Explicitly checked:

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | None — snapshot is a new file, no existing records to migrate | None |
| Live service config | None — no external services involved | None |
| OS-registered state | None | None |
| Secrets/env vars | `FIRESTARTER_DB_FILE` / `FIRESTARTER_PINOUTS_FILE` env overrides exist in check_dispatch.py; the snapshot generator should use the same env-override pattern | None |
| Build artifacts | `tools/baseline/` dir already exists; no .gitkeep needed | None |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | Devcontainer execution | ✓ | 3.12.13 | — |
| ruff | Format/lint gate | ✓ | 0.15.16 | — |
| pytest | Test runner | ✓ | 9.0.3 | — |
| firestarter_app installed (editable) | `from firestarter.database import EpromDatabase` in check_dispatch.py | ✓ | already `pip install -e .` | `pip install -e '.[test]'` |
| `tools/baseline/` directory | Snapshot output | ✓ | exists | — |

[VERIFIED: all via devcontainer shell commands]

No missing dependencies.

---

## Validation Architecture

> `workflow.nyquist_validation` key is absent from `.planning/config.json` → treated as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests"]` |
| Quick run command | `python3 -m pytest tests/test_decoder.py -x -q` |
| Full suite command | `python3 -m pytest -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| GATE-01 | Snapshot artifact committed, contains 743 chips, all with valid triples | manual/shell | `python3 -c "import json; d=json.load(open('tools/baseline/dispatch_baseline.json')); print(d['meta']['db_chip_count'])"` → 743 | ❌ Wave 0: create file |
| GATE-01 | Firmware Unity test pins `(protocol=0, mem_type=1) → NOT ERROR` | native Unity (firmware, accepted as-is) | `pio test -e native -f "*test_dispatch*"` (in `firestarter/`) | ✅ exists |
| GATE-02 | `dispatch(0x35, None)` → `"configure_flash4"` | unit | new pytest in `tests/test_decoder.py` | ❌ Wave 0 |
| GATE-02 | `dispatch(0x39, None)` → `"configure_flash4"` | unit | new pytest in `tests/test_decoder.py` | ❌ Wave 0 |
| GATE-02 | `dispatch(0x99, None)` → `"not_implemented"` | unit | new pytest in `tests/test_decoder.py` | ❌ Wave 0 |
| GATE-02 | `dispatch(0, 99)` → `"ERROR"` (D-03 bucket separation) | unit | new pytest in `tests/test_decoder.py` | ❌ Wave 0 |
| GATE-02 | `python tools/check_dispatch.py` exits 0 with `0 not-implemented chips` | integration | `python3 tools/check_dispatch.py` | — (run against existing DB) |
| GATE-02 (pre-existing) | All 6 existing buckets stay green (GATE-03, SRAM, wire round-trip) | integration | `python3 tools/check_dispatch.py` | ✅ existing |

### Unit Tests to Add (Wave 0 Gap)

Add to `tests/test_decoder.py` in the `TestGate03StructuralVppGuard` class or a
new `TestDispatchGATE02` class:

```python
class TestDispatchGate02:
    """GATE-02: check_dispatch.dispatch() models the Phase-64 fail-closed guard."""

    def test_dispatch_0x35_routes_configure_flash4(self):
        from tools.check_dispatch import dispatch
        assert dispatch(0x35, None) == "configure_flash4"

    def test_dispatch_0x39_routes_configure_flash4(self):
        from tools.check_dispatch import dispatch
        assert dispatch(0x39, None) == "configure_flash4"

    def test_dispatch_unknown_nonzero_proto_routes_not_implemented(self):
        """protocol != 0 with unrecognized protocol → not_implemented (D-03)."""
        from tools.check_dispatch import dispatch
        assert dispatch(0x99, None) == "not_implemented"

    def test_dispatch_protocol_zero_unknown_memtype_routes_error(self):
        """protocol == 0, unknown mem_type → ERROR (D-03 — distinct bucket)."""
        from tools.check_dispatch import dispatch
        assert dispatch(0, 99) == "ERROR"

    def test_dispatch_protocol_zero_memtype_eprom_routes_eprom(self):
        """Legacy fallback intact: protocol=0, mem_type=1 → configure_eprom."""
        from tools.check_dispatch import dispatch
        assert dispatch(0, 1) == "configure_eprom"
```

### Sampling Rate

- **Per task commit:** `ruff check tools/check_dispatch.py && ruff format --check tools/check_dispatch.py && python3 -m pytest tests/test_decoder.py -x -q`
- **Per wave merge:** `python3 -m pytest -q` (full 559+ test suite)
- **Phase gate:** `python3 tools/check_dispatch.py` (all checks green, 0 not-implemented) + `python3 -m pytest -q` (green) before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_decoder.py::TestDispatchGate02` — 5 new test methods (GATE-02)
- [ ] `tools/baseline/dispatch_baseline.json` — snapshot artifact (GATE-01)
- [ ] Branch `v1.12-protocol-dispatch-hardening` in `firestarter_app` (off `beta`)

---

## Security Domain

This phase modifies only a regression-gate script and creates a static JSON
snapshot file. No authentication, session management, cryptography, or user input
processing is involved. Security enforcement is not applicable.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `0x35`/`0x39` in `KNOWN_PROTOCOLS` | Both removed; firmware handles them via the `0x05` arm grouping | Phase 57 (v1.11) | No DB chips affected; `check_dispatch.py` has a mirror gap |
| `check_dispatch.py` mem_type fallback covers all non-zero protocols | Phase-64 firmware will guard `protocol != 0` before the fallback | Phase 62 (this phase) hosts the pre-change snapshot | Eliminates silent VPP hazard |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Snapshot location `tools/baseline/dispatch_baseline.json` (within Claude's Discretion) | §Baseline Artifact Design | Planner may choose a different path; no functional risk |
| A2 | Snapshot JSON schema (meta block + chips array) | §Baseline Artifact Design | Planner may use a different format (e.g. CSV or plain text); D-04 shape is locked, schema is not |
| A3 | `_ALGO_MEM_TYPE` should get `0x35: 5, 0x39: 5` entries | §Dispatch Gap Analysis | If omitted, the dict is slightly incomplete but functionally harmless given explicit dispatch arms |

---

## Open Questions

1. **Should the snapshot generator be a standalone script or inline in the plan task?**
   - What we know: Phase 56 used a direct `cp` / Python inline copy; the snapshot is simple enough for inline generation.
   - What's unclear: Whether a reusable `gen_dispatch_baseline.py` script is wanted for future milestones.
   - Recommendation: Inline script in the plan task (one-shot; D-01 says one-time snapshot, not a regenerate-and-diff gate). No standalone script needed.

2. **Exact PASS line text in `check_dispatch.py` after adding `not_implemented` bucket**
   - What we know: The PASS line at line 266 currently reads `f"PASS: all {total} chips have a valid dispatch path; 0 SRAM chips route ..."`.
   - What's unclear: Whether to insert `"0 not-implemented chips; "` before or after the existing text.
   - Recommendation: Insert as the first clause after the chip count: `f"PASS: all {total} chips have a valid dispatch path; 0 not-implemented chips; 0 SRAM chips route ..."`.

---

## Sources

### Primary (HIGH confidence — direct codebase inspection)

- `/workspaces/firestarter/src/proms/memory.cpp` — Full `configure_memory()` dispatch source read (lines 45–119)
- `/workspaces/firestarter/CLAUDE.md` § "Protocol Dispatch" — Canonical 11-step dispatch order table
- `/workspaces/firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — Existing Unity baseline; all 15 tests confirmed
- `/workspaces/firestarter_app/tools/check_dispatch.py` — Complete source read; current `dispatch()` arms and `main()` scan loop
- `/workspaces/firestarter_app/tools/build_db.py` lines 27–122 — `PROTOCOL_MAP`, `KNOWN_PROTOCOLS` (0x35/0x39 excluded confirmed)
- Runtime tests in devcontainer — chip count (743), 0 chips use 0x35/0x39, dispatch(0x35, None) → "ERROR"

### Secondary (MEDIUM confidence — planning artifacts)

- `.planning/phases/62-dispatch-baseline-capture-check-dispatch-update/62-CONTEXT.md` — Locked decisions D-01..D-04
- `.planning/REQUIREMENTS.md` — GATE-01, GATE-02 requirement text
- `.planning/ROADMAP.md` § "Phase 62" — Success criteria

---

## Metadata

**Confidence breakdown:**
- Dispatch source-of-truth (memory.cpp): HIGH — direct source read
- check_dispatch.py current state: HIGH — direct source read + runtime verified
- `0x35`/`0x39` zero-chip count: HIGH — runtime verified against live DB
- Snapshot format/location: MEDIUM (within Discretion bounds) — follows established precedent
- Pitfalls: HIGH — all derived from direct code inspection and documented project history

**Research date:** 2026-06-10
**Valid until:** Stable until Phase 64 lands (firmware dispatch changes) — no TTL concern for Phase 62 planning

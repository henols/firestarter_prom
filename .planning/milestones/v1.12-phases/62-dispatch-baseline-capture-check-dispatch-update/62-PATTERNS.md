# Phase 62: Dispatch Baseline Capture + check_dispatch Update - Pattern Map

**Mapped:** 2026-06-10
**Files analyzed:** 4 (2 modified, 1 created, 1 inline script)
**Analogs found:** 4 / 4

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/tools/check_dispatch.py` | utility/gate | batch (full-DB scan) | itself (surgical edit) | exact |
| `firestarter_app/tests/test_decoder.py` | test | request-response | `tests/test_decoder.py::TestGate03StructuralVppGuard` (same file) | exact |
| `firestarter_app/tools/baseline/dispatch_baseline.json` | config/artifact | batch | `tools/baseline/chip_database.baseline.json` | exact |
| snapshot generator (inline script) | utility | batch/transform | `check_dispatch.py::main()` chip iteration loop | role-match |

---

## Pattern Assignments

### `firestarter_app/tools/check_dispatch.py` (utility/gate, batch — surgical edit)

**Analog:** itself — all three changes are surgical modifications to existing functions.

#### Change 1: `dispatch()` — extend the `0x05` arm to include `0x35` and `0x39`

**Existing arm** (`check_dispatch.py` lines 83–84):
```python
if protocol == 0x05:
    return "configure_flash4"
```

**Pattern to follow** — use a tuple membership test, matching the style of the
`0x07/0x08/0x0B` arm immediately below it (lines 85–86):
```python
if protocol in (0x07, 0x08, 0x0B):
    return "configure_eprom"
```

**Target state after edit:**
```python
if protocol in (0x05, 0x35, 0x39):
    return "configure_flash4"
```

#### Change 2: `dispatch()` — insert `protocol != 0 → "not_implemented"` arm

**Insert location:** After the `0x0E/0x27/0x28/0x29` arm (line 87–88) and
before the `mem_type` fallback dict (lines 90–95). This mirrors the Phase-64
firmware insertion point between step 6 and step 7 of `configure_memory()`.

**Existing boundary lines for insertion** (`check_dispatch.py` lines 87–95):
```python
    if protocol in (0x0E, 0x27, 0x28, 0x29):
        return "configure_sram"
    # mem_type fallback chain (matches memory.cpp:83-95)
    return {
        1: "configure_eprom",
        4: "configure_sram",
        3: "configure_flash3",
        5: "configure_flash4",
    }.get(mem_type, "ERROR")
```

**Target state after insertion:**
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

#### Change 3: `_ALGO_MEM_TYPE` dict — add `0x35` and `0x39` entries

**Existing dict** (`check_dispatch.py` lines 38–50):
```python
_ALGO_MEM_TYPE = {
    0x05: 5,  # FLASH_AMD_STD     → TYPE_FLASH_TYPE_4
    0x06: 3,  # FLASH_AMD_ALT     → TYPE_FLASH_TYPE_3
    0x07: 1,  # EPROM_STD         → TYPE_EPROM
    0x08: 1,  # EPROM_QUICK       → TYPE_EPROM
    0x0B: 1,  # EPROM_LEGACY      → TYPE_EPROM
    0x0D: 1,  # EEPROM_POLL       → TYPE_EPROM (firmware dispatches on protocol prefix)
    0x0E: 4,  # SRAM_32PIN        → TYPE_SRAM
    0x10: 1,  # FLASH_INTEL       → TYPE_EPROM (firmware dispatches on protocol prefix)
    0x27: 4,  # SRAM_24PIN        → TYPE_SRAM
    0x28: 4,  # SRAM_STD          → TYPE_SRAM
    0x29: 4,  # SRAM_512K_1M      → TYPE_SRAM
}
```

**Target state — add after the `0x05` entry** (same comment style as existing):
```python
_ALGO_MEM_TYPE = {
    0x05: 5,  # FLASH_AMD_STD     → TYPE_FLASH_TYPE_4
    0x35: 5,  # FLASH_EEPROM      → TYPE_FLASH_TYPE_4  (explicit arm; dict entry for completeness)
    0x39: 5,  # FLASH_EEPROM2     → TYPE_FLASH_TYPE_4  (explicit arm; dict entry for completeness)
    0x06: 3,  # FLASH_AMD_ALT     → TYPE_FLASH_TYPE_3
    ...       # rest unchanged
}
```

#### Change 4: `main()` — add `not_implemented` bucket (accumulator + loop check + exit block)

**Analog pattern to copy:** the `errors` bucket (lines 127–145 and 207–220).
The `not_implemented` bucket uses the exact same shape. Copy the three-part
pattern:

**Part A — accumulator declaration** (copy from line 127, alongside `errors = []`):
```python
errors = []
sram_in_eprom = []
# ... (add alongside these)
not_implemented = []
```

**Part B — chip loop detection** (copy from lines 143–145, the `errors` arm):
```python
            if handler == "ERROR":
                errors.append(f"{mfg}/{part} proto=0x{proto:02X} mem_type={mt}")
                continue
```
New bucket uses same structure but inserts immediately after the `errors` arm:
```python
            if handler == "not_implemented":
                not_implemented.append(
                    f"{mfg}/{part} proto=0x{proto:02X}"
                )
                continue  # skip VPP/wire checks — no real handler to evaluate
```

**Part C — exit block FAIL print** (copy shape from lines 215–220, `errors` branch):
```python
        if errors:
            print(f"FAIL: {len(errors)} of {total} chips have no valid dispatch path:")
            for e in errors[:20]:
                print(f"  {e}")
            if len(errors) > 20:
                print(f"  ... and {len(errors) - 20} more")
```
New bucket entry (insert in the `if (errors or sram_in_eprom or ...)` OR-chain
at line 207–214, and a corresponding print block before the existing `if errors:`):
```python
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

**Part D — PASS summary line update** (line 266–273):
```python
    print(
        f"PASS: all {total} chips have a valid dispatch path; "
        f"0 SRAM chips route to configure_eprom; "
        ...
    )
```
Insert `"0 not-implemented chips; "` as the first clause after the chip count:
```python
    print(
        f"PASS: all {total} chips have a valid dispatch path; "
        f"0 not-implemented chips; "
        f"0 SRAM chips route to configure_eprom; "
        ...
    )
```

---

### `firestarter_app/tests/test_decoder.py` (test — new `TestDispatchGate02` class)

**Analog:** `tests/test_decoder.py::TestGate03StructuralVppGuard` (lines 1426–1554+)

**Import pattern** (from `TestGate03StructuralVppGuard`, lines 1460–1464):
```python
    def test_novpp_pin_pinout_with_configure_eprom_is_flagged(self, tmp_path):
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
        from check_dispatch import _build_no_vpp_pin_set, dispatch
```

Each test method does a local `sys.path.insert` + `from check_dispatch import dispatch`
inline. The new `TestDispatchGate02` methods are simpler (no `tmp_path`, no
`_build_no_vpp_pin_set`) but should follow the same per-method local import style.

**Class docstring pattern** (lines 1426–1441):
```python
class TestGate03StructuralVppGuard:
    """Regression tests for the GATE-03 structural no-vpp-pin guard in check_dispatch.py.

    GATE-03 (Phase 59): The real structural hazard is configure_eprom routed to a
    pinout that has no vpp-pin. ...

    Test cases:
      1. ...
      2. ...
      3. ...
    """
```

**Core test method pattern** (lines 1488–1522) — simpler method, no fixtures:
```python
    def test_w27c512_on_dip28_27512_is_not_flagged(self):
        """W27C512 (EEPROM type, algo 0x07) on DIP28_27512 (has vpp-pin) must NOT be flagged.
        ...
        """
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
        from check_dispatch import _build_no_vpp_pin_set, dispatch

        ...
        handler = dispatch(proto, None)
        assert handler == "configure_eprom", (
            f"Expected algo 0x07 → configure_eprom, got {handler!r}"
        )
```

**Target new class (append after `TestGate03StructuralVppGuard`):**
```python
class TestDispatchGate02:
    """GATE-02: check_dispatch.dispatch() models the Phase-64 fail-closed guard.

    Phase 62 — D-03: two distinct failure buckets:
      - protocol != 0 + unrecognized protocol → "not_implemented"
      - protocol == 0 + unknown mem_type → "ERROR"
    Phase 62 — dispatch mirror gap: 0x35/0x39 must now route to configure_flash4
    (not fall through to "ERROR" via the mem_type dict).

    Test cases:
      1. dispatch(0x35, None) → "configure_flash4"
      2. dispatch(0x39, None) → "configure_flash4"
      3. dispatch(0x99, None) → "not_implemented"  (unknown non-zero protocol)
      4. dispatch(0, 99)     → "ERROR"            (protocol=0, unknown mem_type)
      5. dispatch(0, 1)      → "configure_eprom"  (legacy fallback intact)
    """

    def test_dispatch_0x35_routes_configure_flash4(self):
        """0x35 (FLASH_EEPROM) must route to configure_flash4 — explicit arm, not mem_type fallback."""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
        from check_dispatch import dispatch

        assert dispatch(0x35, None) == "configure_flash4"

    def test_dispatch_0x39_routes_configure_flash4(self):
        """0x39 (FLASH_EEPROM2) must route to configure_flash4 — explicit arm, not mem_type fallback."""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
        from check_dispatch import dispatch

        assert dispatch(0x39, None) == "configure_flash4"

    def test_dispatch_unknown_nonzero_proto_routes_not_implemented(self):
        """protocol != 0 with unrecognized protocol → not_implemented (D-03)."""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
        from check_dispatch import dispatch

        assert dispatch(0x99, None) == "not_implemented"

    def test_dispatch_protocol_zero_unknown_memtype_routes_error(self):
        """protocol == 0, unknown mem_type → ERROR (D-03 — distinct bucket from not_implemented)."""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
        from check_dispatch import dispatch

        assert dispatch(0, 99) == "ERROR"

    def test_dispatch_protocol_zero_memtype_eprom_routes_eprom(self):
        """Legacy fallback intact: protocol=0, mem_type=1 → configure_eprom."""
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
        from check_dispatch import dispatch

        assert dispatch(0, 1) == "configure_eprom"
```

---

### `firestarter_app/tools/baseline/dispatch_baseline.json` (artifact, batch)

**Analog:** `tools/baseline/chip_database.baseline.json`

**File shape** (lines 1–22 of `chip_database.baseline.json`):
```json
{
  "ALI(Acer)": [
    {
      "part_number": "M8720",
      "electrical": {
        "type": "UV-EPROM",
        "size_bytes": 262144,
        ...
      },
      "programming": {
        "algorithm": 8,
        ...
      },
      "pinout": "DIP32_STD"
    }
  ],
  "ALLIANCE": [
    { ... }
  ]
}
```

The existing baseline is a direct copy of `chip_database.json` (full chip entries,
manufacturer-keyed dict). The dispatch baseline is different in shape — it uses a
`meta` block + flat `chips` array sorted by (manufacturer, part) — but shares the
same conventions: JSON with 2-space indent, sorted stable order, located in
`tools/baseline/`, no binary data.

**Target file shape for `dispatch_baseline.json`:**
```json
{
  "meta": {
    "generated": "2026-06-10",
    "db_chip_count": 743,
    "description": "Dispatch baseline: protocol → handler mapping for every DB chip, captured before Phase 64 fail-closed guard lands."
  },
  "chips": [
    {
      "manufacturer": "ALI(Acer)",
      "part": "M8720",
      "algorithm": "EPROM_QUICK",
      "algorithm_id": "0x08",
      "mem_type": 1,
      "resolved_handler": "configure_eprom"
    },
    ...
  ]
}
```

**Location:** `firestarter_app/tools/baseline/dispatch_baseline.json`
(same directory as `chip_database.baseline.json`; Phase 56 precedent confirmed).

---

### Snapshot generator (inline script, batch/transform)

**Analog:** `check_dispatch.py::main()` chip iteration loop (lines 134–205).

**Chip loop pattern to reuse** (lines 134–144):
```python
    for mfg, chips in db_raw.items():
        if not isinstance(chips, list):
            continue
        for chip in chips:
            total += 1
            proto = chip.get("programming", {}).get("algorithm", 0) or 0
            mt = _ALGO_MEM_TYPE.get(proto)
            handler = dispatch(proto, mt)
            part = chip.get("part_number", "<unknown>")
```

**Imports pattern to reuse** (lines 18–22):
```python
import json
import os
import sys

from firestarter.database import EpromDatabase
```

**Target inline generator** (run as `python3 -c "..."` or standalone script in the plan task):
```python
import json, sys, os
sys.path.insert(0, ".")
from tools.check_dispatch import dispatch, _ALGO_MEM_TYPE
from tools.build_db import PROTOCOL_MAP

DB_FILE = os.environ.get(
    "FIRESTARTER_DB_FILE",
    os.path.join("firestarter", "data", "chip_database.json"),
)
with open(DB_FILE, encoding="utf-8") as f:
    db_raw = json.load(f)

chips = []
for mfg, chip_list in sorted(db_raw.items()):
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
        "description": (
            "Dispatch baseline: protocol → handler mapping for every DB chip, "
            "captured before Phase 64 fail-closed guard lands."
        ),
    },
    "chips": sorted(chips, key=lambda c: (c["manufacturer"], c["part"])),
}
out = os.path.join("tools", "baseline", "dispatch_baseline.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(snapshot, f, indent=2)
    f.write("\n")
print(f"Written {len(chips)} chips → {out}")
```

**Critical ordering:** Run the snapshot generator BEFORE editing `dispatch()`.
After the edit, `dispatch(0x35/0x39, None)` returns `"configure_flash4"` instead
of `"ERROR"` — generating pre-edit captures the true current fallback behavior
(D-01: "before any v1.12 code changes land").

---

## Shared Patterns

### Bucket FAIL print idiom
**Source:** `check_dispatch.py` lines 215–220 (`errors` bucket) and lines 221–229
(`sram_in_eprom` bucket)
**Apply to:** the new `not_implemented` bucket in `main()`

The canonical shape (copy verbatim, substituting bucket name and message):
```python
        if <bucket_list>:
            print(
                f"FAIL: {len(<bucket_list>)} <description>:"
            )
            for e in <bucket_list>[:20]:
                print(f"  {e}")
            if len(<bucket_list>) > 20:
                print(f"  ... and {len(<bucket_list>) - 20} more")
```

### OR-chain predicate in exit block
**Source:** `check_dispatch.py` lines 207–214
**Apply to:** add `or not_implemented` to the existing OR chain

```python
    if (
        errors
        or not_implemented        # <-- insert here (before sram_in_eprom)
        or sram_in_eprom
        or eeprom28c_in_eprom
        or novpp_in_eprom
        or vpp_eeprom_in_eprom
        or wire_regressions
    ):
```

### Per-test local import style
**Source:** `tests/test_decoder.py` lines 1460–1464 and 1497–1500
**Apply to:** every method in the new `TestDispatchGate02` class

```python
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
        from check_dispatch import dispatch
```

The `sys.path.insert` is per-method (not class-level) — copy exactly.

### Ruff format compliance
**Apply to:** all edits to `check_dispatch.py` and `test_decoder.py`
- No f-string backslashes (use intermediate variables if needed)
- String formatting: `f"0x{proto:02X}"` not `"0x%02X" % proto`
- Run `ruff check tools/check_dispatch.py && ruff format --check tools/check_dispatch.py` before committing
- Run `ruff check tests/test_decoder.py && ruff format --check tests/test_decoder.py` before committing

---

## No Analog Found

All files have close analogs. No entries.

---

## Metadata

**Analog search scope:** `firestarter_app/tools/`, `firestarter_app/tests/`, `firestarter_app/tools/baseline/`
**Files scanned:** 4 (check_dispatch.py in full; test_decoder.py lines 1-30 + 1426-1554; chip_database.baseline.json lines 1-40)
**Pattern extraction date:** 2026-06-10

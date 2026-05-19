# Phase 11: Coverage Matrix & DB Inconsistency Audit - Pattern Map

**Mapped:** 2026-05-19
**Files analyzed:** 5 new + 4 modified
**Analogs found:** 9 / 9

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/tools/audit_coverage_matrix.py` | utility (codegen tool) | batch / file-I/O | `firestarter_app/tools/check_dispatch.py` | exact (same loader + iterator + exit-code shape) |
| `firestarter_app/tests/test_audit_coverage_matrix.py` | test | batch / file-I/O | `firestarter_app/tests/test_fwguard.py` | role-match (pytest class-based with monkeypatch + tmp_path) |
| `.planning/v1.3-COVERAGE-MATRIX.md` | output artifact (markdown) | file-I/O | `.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md` §"SC#4 Build Status" | exact (column-aligned pipe-table convention) |
| `.planning/v1.3-defect-coverage-ids.json` | data ledger (JSON) | file-I/O | `firestarter_app/firestarter/data/chip_database.json` (write style) + `build_db.py:530-531` `json.dump(...)` recipe | role-match (committed sorted-keys JSON) |
| `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` | test fixture | file-I/O (read-only) | no in-repo golden-file precedent — RESEARCH.md §"Golden-file pattern (recommended)" defines the shape | none (greenfield) |
| `.planning/PROJECT.md` (mod) | doc | targeted Edit | RESEARCH.md §"D-07 Planning-Doc Reconciliation — Exact Edit Plan" enumerates the 12 in-file targets | n/a — Edit-tool replacement task |
| `.planning/ROADMAP.md` (mod) | doc | targeted Edit | same | n/a |
| `.planning/REQUIREMENTS.md` (mod) | doc | targeted Edit | same | n/a |
| `.planning/STATE.md` (mod) | doc | targeted Edit | same | n/a |

## Pattern Assignments

### `firestarter_app/tools/audit_coverage_matrix.py` (utility, batch / file-I/O)

**Analog:** `firestarter_app/tools/check_dispatch.py` (full file — 195 lines)

**Module-top constants + env-var escape hatch** (`check_dispatch.py:17-30`, VERIFIED):
```python
import json
import os
import sys

from firestarter.database import EpromDatabase

# Module-top path constants (mirrors firestarter_app/tools/build_db.py:11-13)
_DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "firestarter", "data"
)
DB_FILE = os.environ.get(
    "FIRESTARTER_DB_FILE",
    os.path.join(_DATA_DIR, "chip_database.json"),
)
```
*Lift verbatim into the new tool — same path computation, same env-var name `FIRESTARTER_DB_FILE`, same fallback chain. Per CONTEXT.md D-01 + RESEARCH.md Pattern 1.*

**DB iteration scaffold** (`check_dispatch.py:86-105`, VERIFIED):
```python
def main():
    """Entry point: scan DB and exit non-zero if any chip lacks a dispatch path."""
    with open(DB_FILE, encoding="utf-8") as f:
        db_raw = json.load(f)

    db = EpromDatabase()

    errors = []
    total = 0
    for mfg, chips in db_raw.items():
        if not isinstance(chips, list):
            continue
        for chip in chips:
            total += 1
            proto = chip.get("programming", {).get("algorithm", 0) or 0
```
*Re-shape into `iter_in_scope_rows()` generator filtered to `proto in (0x07, 0x08)`. RESEARCH.md §"Code Examples" line 551-561 already shows the target shape.*

**Per-chip field extraction pattern** (`check_dispatch.py:104-122`, VERIFIED):
```python
            proto = chip.get("programming", {}).get("algorithm", 0) or 0
            mt = _ALGO_MEM_TYPE.get(proto)
            handler = dispatch(proto, mt)
            part = chip.get("part_number", "<unknown>")
            ...
            pinout = chip.get("pinout", "")
            etype = chip.get("electrical", {}).get("type", "")
```
*The new tool reads the same fields plus `size_bytes`, `pulse_duration`, `chip_id_check`, `chip_id_value` from the same nested-dict shape.*

**Exit-code discipline** (`check_dispatch.py:148-190`, VERIFIED):
```python
    if errors or sram_in_eprom or eeprom28c_in_eprom or wire_regressions:
        if errors:
            print(
                f"FAIL: {len(errors)} of {total} chips have no valid dispatch path:"
            )
            for e in errors[:20]:
                print(f"  {e}")
            if len(errors) > 20:
                print(f"  ... and {len(errors) - 20} more")
        ...
        sys.exit(1)

    print(
        f"PASS: all {total} chips have a valid dispatch path; "
        ...
    )

if __name__ == "__main__":
    main()
```
*Mirror exit code 0/1 discipline — exit 1 when NEW defect-candidates would be minted (D-03) or DB parse fails; exit 0 when ledger is stable. The `--check` flag is RESEARCH.md Pattern 3 (build_db CLI surface).*

---

**Secondary analog:** `firestarter_app/tools/build_db.py` (override block + CLI argparse surface)

**WARNING-5 override predicate block — quote VERBATIM for §4 `DEFECT-COV-00 — RESOLVED` baseline** (`build_db.py:397-423`, VERIFIED):
```python
                # WARNING-5 safety override: DIP28_2764 chips on the 0x07
                # (EPROM_STD) path apply 12V P1_VPP_ENABLE to socket pin 1
                # during the write pulse. On the DIP28_2764 pinout, socket
                # pin 1 = A14 (high address line) on 28C-family 5V CMOS
                # EEPROMs — applying 12V there is a hardware-damage path.
                # Flip proto_id to 0x0D so these chips route to
                # configure_eeprom28c (5V page-write, SDP-disable + DQ7
                # polling, no VPP regulator) which the firmware already
                # implements correctly. Leave _etype = "Flash/EEPROM"
                # unchanged — database.py's info_flags derivation depends
                # on that string for the "electrically erasable" bit, which
                # IS correct for these chips.
                # Discriminator (3 predicates): pinout_key == "DIP28_2764"
                # AND proto_id == 0x07 AND _etype == "Flash/EEPROM".
                # Inline literal — no module-top constant — matches the
                # Phase 12 Plan 04 SRAM-detection precedent above.
                # References: WARNING-5 in .planning/v1.0-MILESTONE-AUDIT.md
                # and .planning/INTEGRATION-CHECK.md.
                if (pinout_key in ("DIP28_2764", "DIP28_28C256")
                        and proto_id == 0x07
                        and _etype == "Flash/EEPROM"):
                    print(
                        f"INFO: {mfg_name}/{name} algorithm override 0x07->0x0D "
                        f"(WARNING-5: 5V EEPROM with non-EPROM pinout — route through configure_eeprom28c)",
                        file=sys.stderr,
                    )
                    proto_id = 0x0D
```
*The matrix's §4 `DEFECT-COV-00 — RESOLVED` finding paraphrases this predicate verbatim (severity=HAZARD, axis=`pinout_vs_algorithm`, signature=`(("DIP28_2764", "DIP28_28C256"), 0x07, "Flash/EEPROM")`). The new HAZARD finding raised by the matrix differs only in the `_etype` clause — it catches the rows where `_etype != "Flash/EEPROM"` (post-re-derivation, all 0x07 chips become UV-EPROM at `build_db.py:483-484`).*

**`_etype` re-derivation pattern that explains the override bypass** (`build_db.py:470-489`, VERIFIED):
```python
                # Re-derive electrical.type protocol-aware after all algorithm
                # overrides have run. The firmware dispatch is the ground truth:
                #   - 0x07/0x08/0x0B → configure_eprom (12V VPP) → UV-EPROM
                #   - 0x0D / 0x05 / 0x06 / 0x10 / 0x35 / 0x39 → Flash/EEPROM family
                #   - 0x0E/0x27/0x28/0x29 → SRAM
                if proto_id in {0x0E, 0x27, 0x28, 0x29}:
                    _etype = "SRAM"
                elif proto_id in {0x07, 0x08, 0x0B}:
                    _etype = "UV-EPROM"
                elif proto_id in {0x05, 0x06, 0x0D, 0x10, 0x35, 0x39}:
                    _etype = "Flash/EEPROM"
```
*The matrix's §4 description for the new HAZARD finding cites these lines explicitly per RESEARCH.md Pitfall 1 ("the WARNING-5 predicate is structurally unreachable for these 42 rows").*

**fm1608 override block (cited in §2 reconciliation)** (`build_db.py:425-468`, VERIFIED):
```python
                # fm1608-db-mismatch override: SRAM-tagged chips with EPROM-family
                # protocol. Upstream infoic.xml tags Ramtron parallel FRAM (FM1208/
                # 1608/16W08/1808/18L08) with `type="4"` (SRAM/RAM-family) but
                # protocol_id 0x07/0x0B (EPROM family).
                ...
                if type_int == 4 and proto_id in (0x07, 0x08, 0x0B):
                    proto_id = 0x28
```
*The matrix's §2 reconciliation cites this override as the explanation for the 0x0B → 0x28 count shift (RESEARCH.md §"Live DB Audit" lines 327-332).*

**JSON output write pattern** (`build_db.py:530-531`):
```python
    with open(OUTPUT_FILE, "w") as f:
        json.dump(complete_db, f, indent=2)
```
*The new tool's ledger writer **enhances** this with `sort_keys=True` + explicit `newline="\n"` + trailing newline per RESEARCH.md Pattern 2 (codegen idempotence). The matrix-body writer uses `pathlib.Path.write_text(content, encoding="utf-8", newline="\n")` instead — explicit LF for cross-platform stability.*

---

**Tertiary analog:** `firestarter_app/firestarter/database.py` (loader singleton + `_ALGO_MEM_TYPE`)

**Loader import** (`database.py:27-32`):
```python
import os
import json
import logging
from pathlib import Path
from firestarter.config import get_local_database, get_local_pin_maps
from firestarter.constants import *
```
*The new tool imports `from firestarter.database import EpromDatabase` exactly like `check_dispatch.py:21` does. No new loader code needed — the singleton already handles the user-override merge if present.*

**Algorithm → mem_type translation table** (`database.py:47-61`, mirrored in `check_dispatch.py:35-49`):
```python
_ALGO_MEM_TYPE = {
    0x05: 5,   # FLASH_AMD_STD     → TYPE_FLASH_TYPE_4
    0x06: 3,   # FLASH_AMD_ALT     → TYPE_FLASH_TYPE_3
    0x07: 1,   # EPROM_STD         → TYPE_EPROM
    0x08: 1,   # EPROM_QUICK       → TYPE_EPROM
    0x0B: 1,   # EPROM_LEGACY      → TYPE_EPROM
    ...
}
```
*The new tool **does not need** `_ALGO_MEM_TYPE` directly (the matrix filters by `algorithm` integer, not mem_type) but should import the same `PROTOCOL_MAP` from `database.py:34-43` for the §3 column rendering and §1 summary stats. Identical import pattern to `check_dispatch.py:21`.*

---

### `firestarter_app/tests/test_audit_coverage_matrix.py` (test, batch / file-I/O)

**Analog:** `firestarter_app/tests/test_fwguard.py` (class-based pytest with autouse + monkeypatch + tmp_path)

**Class-based pytest organisation with autouse fixture** (`test_fwguard.py:31-42`, VERIFIED):
```python
class TestFirmwareVersionGuard:
    """LFW-05 / LHOST-04 — host refuses pre-v1.2 firmware at probe time."""

    @pytest.fixture(autouse=True)
    def _clear_escape_hatch(self, monkeypatch):
        """Ensure the dev escape-hatch env var is unset for every test by default.
        ...
        """
        monkeypatch.delenv("FIRESTARTER_DEV_ALLOW_PRE_V12", raising=False)
```
*Adapt to:* `class TestAuditCoverageMatrix:` with autouse `_isolate_env` fixture that `monkeypatch.delenv("FIRESTARTER_DB_FILE", raising=False)` so tests hermetically use the live DB unless they override it explicitly.

**Per-test env-var override** (`test_fwguard.py:85-87`, VERIFIED):
```python
    def test_dev_escape_hatch_env_var(self, monkeypatch):
        """LFW-05 / LHOST-04 path: escape-hatch. FIRESTARTER_DEV_ALLOW_PRE_V12=1 bypasses."""
        monkeypatch.setenv("FIRESTARTER_DEV_ALLOW_PRE_V12", "1")
```
*The new test file mirrors this to point `FIRESTARTER_DB_FILE` at a tmp-path fixture DB for the "first-run mints IDs", "second-run reuses IDs", and "cold-start absent ledger" scenarios (RESEARCH.md Pitfall 4).*

---

**Secondary analog:** `firestarter_app/tests/test_decoder.py` (parametrize + direct function call pattern)

**Direct-function-call test pattern** (`test_decoder.py:70-84`, VERIFIED):
```python
    def test_zero_param_frame_decodes_as_ready(self, fake_serial, make_comm):
        """LHOST-01: zero-param MSG_OK_READY frame → Response(type='OK', message='Ready')."""
        comm = make_comm()
        frame = build_frame(MSG_OK_READY, b"")
        fake_serial.feed(frame)

        response = _drive_one_response(comm)
        assert response is not None
        assert response.type == "OK"
        assert response.message == "Ready"
```
*Per RESEARCH.md §"Validation Architecture", the new tests import `from tools.audit_coverage_matrix import generate_matrix` and call it directly (no subprocess) for unit tests. One integration test (`test_exit_codes`) uses `subprocess.run([...])` to verify the CLI exit-code surface per D-03.*

**RESEARCH.md §"Validation Architecture" maps 8 test IDs to discrete `def test_*` functions:**

| Req | Test fn |
|-----|---------|
| COV-01 row count | `test_enumeration_row_count` |
| COV-01 sort order | `test_enumeration_sort` |
| COV-01 idempotence | `test_idempotence` (the load-bearing one — see RESEARCH.md Code Example line 242-255) |
| COV-02 HAZARD cluster | `test_hazard_cluster_42_rows` |
| COV-02 ledger idempotent | `test_ledger_idempotent` |
| COV-02 ledger ID reuse | `test_ledger_id_reuse` |
| COV-01/02 summary stats | `test_summary_stats` |
| D-03 exit codes | `test_exit_codes` (subprocess) |

**Idempotence test recipe** (RESEARCH.md §"Code Examples" lines 242-255, VERIFIED):
```python
def test_idempotence(tmp_path):
    from tools.audit_coverage_matrix import generate_matrix
    out_a = tmp_path / "a.md"
    out_b = tmp_path / "b.md"
    ledger = tmp_path / "ids.json"
    # First run mints IDs into ledger
    generate_matrix(output=out_a, ledger_path=ledger)
    snap_ledger_1 = ledger.read_text()
    # Second run — must be byte-identical AND must not mint new IDs
    generate_matrix(output=out_b, ledger_path=ledger)
    assert out_a.read_bytes() == out_b.read_bytes(), "matrix not idempotent"
    assert ledger.read_text() == snap_ledger_1, "ledger mutated on second run"
```

---

### `.planning/v1.3-COVERAGE-MATRIX.md` (output artifact, file-I/O)

**Analog:** `.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md` §"SC#4 Build Status" + §"Anchor table"

**Markdown table convention — column-aligned, pipe-style** (`08-MEASUREMENT.md:233-236`, VERIFIED):
```markdown
| Board | Build | Flash Used | Flash Max | % Used | Free | Delta vs Ph7 |
|-------|-------|------------|-----------|--------|------|--------------|
| Leonardo | SUCCESS | 24,538 B | 28,672 B | 85.6% | 4,134 B | −2,488 B (−8.7 pp) |
| Uno | SUCCESS | 22,330 B | 32,256 B | 69.2% | 9,926 B | −2,508 B (−7.8 pp) |
```
*The matrix's §3 + §5 tables use **identical** style: pipe-fenced, hyphen-separator row, no fancy unicode borders. The emitter (`md_table` helper in RESEARCH.md §"Code Examples" lines 638-647) reproduces this exactly with per-column `ljust` to the max cell width.*

**Multi-table-stacked layout** (`08-MEASUREMENT.md:233-298`, VERIFIED):
```markdown
## SC#4 Build Status

| Board | Build | Flash Used | ... |
| ... |

## Native test suite:
```
[code block]
```

| Board | Pre-R-01 | Post-R-01 | Delta |
| ... |
```
*The matrix's §1 (Summary stats) emits **multiple narrow tables stacked** (per-algorithm histograms, per-pinout histograms, per-tier counts) following this same pattern. Per CONTEXT.md "Claude's Discretion" line 75, §3 splits per-algorithm into two tables (algo-0x07 first, algo-0x08 second) rather than one wide table.*

**Section header conventions** (08-MEASUREMENT.md uses `## SC#N` h2 + horizontal-rule separators):
```markdown
---

## SC#4 Build Status

[content]

---

## Next section
```
*The matrix uses identical `## §N: <Section Name>` h2 headers + `---` separators per D-05's five-section order.*

---

### `.planning/v1.3-defect-coverage-ids.json` (data ledger, file-I/O)

**Analog:** `firestarter_app/firestarter/data/chip_database.json` (write style at `build_db.py:530-531`)

**Sorted JSON write recipe** (RESEARCH.md Pattern 2 + §"Code Examples" lines 630-633):
```python
def emit_ledger(ledger, ledger_path):
    """sort_keys=True so hash-key ordering is deterministic."""
    blob = json.dumps(ledger, indent=2, sort_keys=True) + "\n"
    Path(ledger_path).write_text(blob, encoding="utf-8", newline="\n")
```
*Mandatory: `sort_keys=True` (without this, dict insertion order leaks into the diff). `indent=2` matches `build_db.py:531`. Explicit `+ "\n"` so the file ends with a trailing newline (POSIX text-file convention).*

**Cold-start guard** (RESEARCH.md Pitfall 4, lines 510-514):
```python
try:
    ledger = json.loads(ledger_path.read_text())
except FileNotFoundError:
    ledger = {}
```
*The first-ever invocation must not crash on missing ledger file. Test this explicitly in `test_first_run_creates_ledger`.*

---

### `.planning/PROJECT.md` (modified — targeted Edit operations)

**Edit targets — verbatim line excerpts from RESEARCH.md §"D-07 Planning-Doc Reconciliation — Exact Edit Plan" + live grep verification:**

`PROJECT.md:16` (target — "Target features" bullet):
```
- Structural-coverage report across all ~341 algorithm-0x07 + algorithm-0x08 chips in the database (which chips share which DB row, pulse-duration profile, chip-id check status, pinout class).
```
*Edit: `~341` → `339`*

`PROJECT.md:43` (target — "Current State (v1.0)" para):
```
carries 743 chips with explicit `algorithm` integer = upstream `protocol_id`;
```
*Edit: `743 chips` → `734 chips`*

`PROJECT.md:79` (target — "Validated by v1.0" bullet):
```
   `check_dispatch.py` across 743 chips; no guessing fallback in non-user-override path)
```
*Edit: `743 chips` → `734 chips`*

`PROJECT.md:86` (target — Validated list bullet):
```
5. ✓ **DIP 24/28/32 packages fully covered** — v1.0 (filter clean; 743 chips
```
*Edit: `743 chips` → `734 chips`*

`PROJECT.md:135` (HISTORICAL — RESEARCH.md A6 says **leave alone**):
```
| 2026-05-12 | Phase 2 closes WIRE-01 (atomic `"vpp"`→`"vpp_mv"` wire-key flip), CLEAN-01 (`minipro_complete_db.json`→`chip_database.json` rename + D-04 internal `vpp_volts` rename), CLEAN-02 (minipro attribution scrub: 6→1 host, 2→0 firmware), WIRE-02 (`check_dispatch.py` per-chip wire round-trip: 743/743 PASS).
```
*No edit — this is a decision-log row describing a v1.0/v1.1 historical state. Per RESEARCH.md A6 + "Claude's Discretion".*

`PROJECT.md:149` (target — "Database state" Context line):
```
- **Database state:** 743 chips post-v1.0 across DIP24/28/32. Algorithm
```
*Edit: `743 chips post-v1.0` → `734 chips post-v1.0` (or add footnote per RESEARCH.md option). Recommended: simple replacement; the matrix's §2 carries the full delta narrative.*

`PROJECT.md:150-151` (target — algorithm histogram):
```
  histogram: 0x05=27, 0x06=190, 0x07=214, 0x08=127, 0x0B=53, 0x0D=41, 0x0E=20,
  0x10=39, 0x27=2, 0x28=10, 0x29=20 (totals 743)
```
*Edits (5 substring replacements on these 2 lines):*
- `0x07=214` → `0x07=212`
- `0x0B=53` → `0x0B=40`
- `0x0D=41` → `0x0D=23`
- `0x28=10` → `0x28=34`
- `(totals 743)` → `(totals 734)`

`PROJECT.md:190` (target — last-updated footer):
```
*Last updated: 2026-05-19 — v1.3 milestone started (CMOS EPROM Family Hardware Validation). Goal: bench-validate algorithm-0x07 (28-pin, 214 chips) + algorithm-0x08 (32-pin, 127 chips) families on Uno + Leonardo via four named chips (W27C512, SST27SF512, W27C020, W27E040) + density-extreme representatives.
```
*Edit: `(28-pin, 214 chips)` → `(28-pin, 212 chips)`*

---

### `.planning/ROADMAP.md` (modified — targeted Edit operations)

`ROADMAP.md:12` (v1.3 milestone-goal paragraph):
```
**Milestone goal:** Bench-validate, on real silicon and on both Arduino Uno + Leonardo, that the algorithm-0x07 (28-pin DIP CMOS UV-EPROM, 214 chips in DB) and algorithm-0x08 (32-pin DIP CMOS UV-EPROM, 127 chips in DB) dispatch logic shipped in v1.0–v1.2 actually programs, reads back, and verifies cleanly across the full 32K → 512K density span.
```
*Edit: `(28-pin DIP CMOS UV-EPROM, 214 chips in DB)` → `(28-pin DIP CMOS UV-EPROM, 212 chips in DB)`*

`ROADMAP.md:27` (Phase 11 bullet):
```
- [ ] **Phase 11: Coverage Matrix & DB Inconsistency Audit** — Desk-side enumeration of all 341 algo-0x07/0x08 DB rows + flag intra-algorithm inconsistencies.
```
*Edit: `all 341 algo-0x07/0x08 DB rows` → `all 339 algo-0x07/0x08 DB rows`*

`ROADMAP.md:39` (SC-01 of Phase 11):
```
  1. A coverage matrix file exists at `.planning/v1.3-COVERAGE-MATRIX.md` (or equivalent) enumerating every algo-0x07 + algo-0x08 row in `chip_database.json` with: manufacturer, part_number(s), pin_count, size_bytes, pulse_duration, chip_id_check, chip_id_value, pinout class. Total row count matches DB histogram (214 + 127 = 341 chips).
```
*Edit: `(214 + 127 = 341 chips)` → `(212 + 127 = 339 chips)`*

`ROADMAP.md:41` (SC-03 of Phase 11):
```
  3. Operator can use the matrix to confirm that the six BENCH chips (BENCH-01..06) span the pinout classes and pulse-duration profiles actually represented in the DB, so bench results generalize to the rest of the 341 rows.
```
*Edit: `the rest of the 341 rows` → `the rest of the 339 rows`*

`ROADMAP.md:134` (v1.0 archived bullet — RESEARCH.md A6 says leave alone unless adding annotation):
```
- Key deliverables: protocol-prefix dispatch in `memory.cpp`, 743-chip database with explicit `algorithm` integer, five firmware handlers ...
```
*Recommended: **no edit** (historical v1.0 close state). Per RESEARCH.md "Claude's Discretion" + A6.*

---

### `.planning/REQUIREMENTS.md` (modified — targeted Edit operations)

`REQUIREMENTS.md:30` (COV-01 acceptance):
```
- [ ] **COV-01**: Generate a coverage matrix from `chip_database.json` enumerating every algo-0x07 + algo-0x08 row with: manufacturer, part_number(s), pin_count, size_bytes, pulse_duration, chip_id_check, chip_id_value, pinout class. Output: `.planning/v1.3-COVERAGE-MATRIX.md` (or equivalent). 341 chips covered.
```
*Edit: `341 chips covered.` → `339 chips covered.`*

---

### `.planning/STATE.md` (modified — targeted Edit operations)

`STATE.md:36` (Current focus):
```
**Current focus:** v1.3 — bench-validating the CMOS EPROM families (algo 0x07 28-pin + algo 0x08 32-pin) that v1.0–v1.2 dispatch logic ships for. End-to-end write/read/verify on Uno + Leonardo for W27C512, SST27SF512, W27C020, W27E040 plus density-tier representatives; structural-coverage report across the ~341 algo-0x07 + algo-0x08 chips in the database.
```
*Edit: `~341 algo-0x07 + algo-0x08` → `~339 algo-0x07 + algo-0x08`*

`STATE.md:48` (v1.3 phases table):
```
| 11. Coverage Matrix & DB Inconsistency Audit | Single-source coverage map of all 341 algo-0x07/0x08 DB rows + flag intra-algorithm inconsistencies | COV-01, COV-02 | No (desk-side) |
```
*Edit: `all 341 algo-0x07/0x08 DB rows` → `all 339 algo-0x07/0x08 DB rows`*

`STATE.md:109` (v1.3 Decisions — Scope):
```
- **Scope:** Algorithm-0x07 (28-pin DIP CMOS UV-EPROM, 214 chips in DB) + algorithm-0x08 (32-pin DIP CMOS UV-EPROM, 127 chips in DB). End-to-end bench validation on Uno + Leonardo for four named chips (W27C512, SST27SF512, W27C020, W27E040) + one 28-pin lower-density representative + one 32-pin lower-density representative. Structural-coverage report across all 341 in-scope DB rows.
```
*Edits (2 substring replacements on this 1 line):*
- `(28-pin DIP CMOS UV-EPROM, 214 chips in DB)` → `(28-pin DIP CMOS UV-EPROM, 212 chips in DB)`
- `all 341 in-scope DB rows` → `all 339 in-scope DB rows`

---

## Shared Patterns

### Pattern A: `tools/` sibling structure (applies to all new `firestarter_app/tools/` work)

**Source:** `firestarter_app/tools/check_dispatch.py` + `firestarter_app/tools/build_db.py`
**Apply to:** `firestarter_app/tools/audit_coverage_matrix.py`

Conventions all three tools share (VERIFIED):
- No entry point in `pyproject.toml` — run as `python tools/<name>.py`
- Module docstring at top describing purpose + exit-code semantics
- `_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "firestarter", "data")` for DB path resolution
- `FIRESTARTER_DB_FILE` env-var override on the DB path (mirrors `check_dispatch.py:27-30`)
- Import `from firestarter.database import EpromDatabase` for any semantic lookup; raw iteration uses `json.load`
- Exit code 0 on success, 1 on failure (`sys.exit(1)`)
- `if __name__ == "__main__": main()` footer

### Pattern B: Codegen idempotence (applies to matrix + ledger writes)

**Source:** RESEARCH.md Pattern 2 + Phase 06 Plan 06-01 LCAT-05 recipe
**Apply to:** Every `pathlib.Path.write_text(...)` call in `audit_coverage_matrix.py`

```python
from pathlib import Path

def emit(content_lines, output_path):
    """LF-only, UTF-8, trailing newline — Phase 06 LCAT-05 recipe."""
    content = "\n".join(content_lines) + "\n"
    Path(output_path).write_text(content, encoding="utf-8", newline="\n")
```

Mandatory invariants:
1. Sort all dict iteration by stable key (per RESEARCH.md §"Code Examples" `sort_key` lines 565-575)
2. No timestamps in output (no `datetime.now()`, no `date.today()`)
3. LF line endings (`newline="\n"` explicit on every `write_text` call)
4. JSON: `json.dumps(..., sort_keys=True, indent=2) + "\n"`
5. Smoke verification: `tool --output /tmp/a; tool --output /tmp/b; diff /tmp/a /tmp/b` returns empty

### Pattern C: Stable defect-ID hash composition (applies to ledger minting in matrix tool)

**Source:** RESEARCH.md Pattern 4 + CONTEXT.md D-13
**Apply to:** Every defect-candidate finding emitted into the JSON ledger

```python
import hashlib, json

def finding_hash(severity, axis, signature):
    payload = {
        "severity": severity,
        "axis": axis,
        "signature": list(signature),
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha1(blob).hexdigest()[:16]
```

Signature-tuple composition (per CONTEXT.md D-14 + RESEARCH.md table at line 224):

| Severity | Axis | Signature tuple |
|----------|------|-----------------|
| HAZARD | `"pinout_vs_algorithm"` | `(pinout, algorithm_int, etype)` |
| CORRECTNESS | `"pulse_duration_outlier"` | `(algorithm_int, pinout, size_bytes, manufacturer, part_number_first_alias)` |
| VARIANCE | `"chip_id_check_toggle"` | `(algorithm_int, pinout, size_bytes, manufacturer)` |
| VARIANCE | `"chip_id_value_drift"` | `(algorithm_int, pinout, size_bytes, manufacturer)` |

### Pattern D: Markdown table emission (applies to §1, §2, §3, §4, §5 of matrix)

**Source:** `.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md:233-236` + RESEARCH.md §"Code Examples" lines 638-647
**Apply to:** Every table-emit site in `audit_coverage_matrix.py`

```python
def md_table(headers, rows, alignments=None):
    """Pipe-style markdown table. alignments: list of '<' '>' or ':' chars per col."""
    widths = [max(len(str(headers[i])),
                  max((len(str(r[i])) for r in rows), default=0))
              for i in range(len(headers))]
    def line(cells):
        return "| " + " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(cells)) + " |"
    header_line = line(headers)
    sep_line = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    return "\n".join([header_line, sep_line] + [line(r) for r in rows])
```

Conventions (VERIFIED against `08-MEASUREMENT.md`):
- Pipe-fenced rows (`| cell | cell |`)
- Hyphen-only separator row (`|-----|-----|`)
- Per-column left-justified padding to max cell width
- No fancy unicode borders, no centered alignment

### Pattern E: Pulse-duration string parse + bucket (applies to §1, §3, §5 of matrix)

**Source:** RESEARCH.md §"Code Examples" lines 580-593 (synthesized from `build_db.py:515` `interpret_timing` output shape)
**Apply to:** Every site that reads `chip["programming"]["pulse_duration"]`

```python
def parse_pulse_us(s):
    """'10000 us' -> 10000. Raise on shape mismatch — caller must surface."""
    if not s.endswith(" us"):
        raise ValueError(f"Unexpected pulse_duration shape: {s!r}")
    return int(s[:-3])

def pulse_bucket(us):
    """D-09 bucketing (microseconds-integer input)."""
    if us < 100:           return "< 100 us"
    if us < 1000:          return "100-999 us"
    if us < 10_000:        return "1-9 ms"
    if us < 100_000:       return "10-99 ms"
    return "100 ms-1 s"
```

*Per RESEARCH.md Pitfall 3: **fail-fast** on shape mismatch — never silently coerce. Any chip with a non-`" us"` pulse_duration is a regression and must surface as a hard error.*

### Pattern F: Sort key for deterministic enumeration (applies to §3 + §5)

**Source:** RESEARCH.md §"Code Examples" lines 564-575 (derived from CONTEXT.md D-06)
**Apply to:** Every iteration that becomes table-row output

```python
def sort_key(mfg, chip):
    return (
        chip["programming"]["algorithm"],
        chip["pinout"],
        chip["electrical"]["size_bytes"],
        mfg,
        chip["part_number"].split(",")[0],  # first alias
    )

rows = sorted(iter_in_scope_rows(), key=lambda mc: sort_key(*mc))
```

*This key tuple is the load-bearing contract for byte-identical re-runs (Pattern B).*

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` | test fixture | file-I/O (read-only) | No existing golden-file fixture in `firestarter_app/tests/`. Pattern is greenfield. The Wave 4 task creates this by copying the operator-approved matrix output verbatim, then `test_golden_file_matches` reads it via `tmp_path` + `Path.read_text()`. See RESEARCH.md §"Golden-file pattern (recommended)" lines 792-799 for the exact template. |

## Metadata

**Analog search scope:**
- `/workspaces/firestarter_app/tools/` (all 3 committed tools)
- `/workspaces/firestarter_app/firestarter/database.py` (loader singleton)
- `/workspaces/firestarter_app/tests/` (3 existing test files + conftest.py)
- `/workspaces/.planning/phases/08-*/08-MEASUREMENT.md` (markdown-table precedent)
- `/workspaces/.planning/PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md` (Edit targets)

**Files scanned:** 11

**Pattern extraction date:** 2026-05-19

**Key project-memory rules applied:**
- `[[project_db-overrides-firmware-is-ground-truth]]` — defect-candidate `suggested_fix_venue` defaults to `v1.4 build_db.py override` for HAZARD findings; firmware patches only for safety-driven defects (CONTEXT.md `<canonical_refs>` line 111).
- `[[feedback_always-mirror-uno-leonardo-tests]]` — N/A to Phase 11 (desk-side; no firmware); convention preserved for downstream Phases 12-13.

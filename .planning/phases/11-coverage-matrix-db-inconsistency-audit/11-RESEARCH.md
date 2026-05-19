# Phase 11: Coverage Matrix & DB Inconsistency Audit — Research

**Researched:** 2026-05-19
**Domain:** Desk-side Python codegen + DB audit (no firmware, no serial, no chip)
**Confidence:** HIGH (all stack/pattern claims VERIFIED against committed sources in this repo)

## Summary

Phase 11 produces **one** committed Python tool (`firestarter_app/tools/audit_coverage_matrix.py`) plus **two** generated artifacts (`.planning/v1.3-COVERAGE-MATRIX.md` and `.planning/v1.3-defect-coverage-ids.json`), plus targeted count fixes in three planning docs. There is no new runtime code, no new test framework, no library installs. The tool is a third sibling of `tools/check_dispatch.py` and `tools/build_db.py` and mirrors their conventions verbatim — same `_DATA_DIR` constant, same `FIRESTARTER_DB_FILE` env-var escape hatch, same `EpromDatabase` import for the loader, same `for mfg, chips in db.items(): for c in chips:` iteration shape, same exit-code discipline, same `--output PATH` CLI flag. Codegen idempotence is the load-bearing correctness property — proven by the same Phase 06 Plan 06-01 recipe (sort by stable key + LF-only + no timestamps) and verified by a "run twice, diff zero" smoke test before the matrix is committed.

The empirical DB audit (executed below against the live `firestarter/data/chip_database.json`) confirms the CONTEXT.md drift exactly: **734 total chips, 212 algo-0x07, 127 algo-0x08, 339 in-scope-for-v1.3** — not 743 / 214 / 127 / 341 as currently quoted in PROJECT.md, ROADMAP.md, REQUIREMENTS.md. The audit also confirms the headline HAZARD cluster: **42 chips on the `(pinout ∈ {DIP28_28C64, DIP28_28C256}) AND algorithm == 0x07` signature dispatch through `configure_eprom` today** — the existing WARNING-5 build_db override does not catch them because the `_etype == "Flash/EEPROM"` predicate is no longer true after the post-override `_etype` re-derivation at `build_db.py:481-486` rewrites every `0x07`-tagged chip to `_etype = "UV-EPROM"`. This is the new HAZARD class the matrix raises.

**Primary recommendation:** lift `tools/check_dispatch.py` verbatim as the skeleton; add a single `--output PATH` flag mirroring `build_db.py`; emit five sections in the fixed order from D-05 using one pass over the DB to accumulate three structures (summary-stats, full-enumeration rows, defect-candidates); render markdown with `"\n".join(...)` and `pathlib.Path.write_text(..., encoding="utf-8", newline="\n")`; encode the ledger as `json.dumps(d, indent=2, sort_keys=True) + "\n"` to keep it diff-clean.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Read live DB | Desk-side host tool (`tools/`) | — | Mirrors `check_dispatch.py` / `build_db.py`. No runtime, no serial. |
| Emit `.planning/v1.3-COVERAGE-MATRIX.md` | Desk-side host tool | — | Markdown is the artifact; no host-runtime consumer. |
| Persist stable DEFECT-COV-NN IDs | Desk-side host tool + JSON ledger | — | `.planning/v1.3-defect-coverage-ids.json` is committed alongside matrix. |
| Reconcile drifted planning-doc numbers | Manual `Edit` task (1 wave) | — | Three files, ≤ 12 targeted string-edits. Not codegen. |
| Validate idempotence | pytest unit test under `firestarter_app/tests/` | Smoke test: `diff $(./tool --output /tmp/a) $(./tool --output /tmp/b)` | Same recipe as Phase 06 LCAT-05. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | ≥ 3.9 (per `firestarter_app/pyproject.toml`) | Runtime | `firestarter_app` minimum [VERIFIED: pyproject.toml requires-python] |
| `json` (stdlib) | — | DB read + ledger write | Mirrors `check_dispatch.py:17` and `build_db.py:2` |
| `os` / `pathlib` (stdlib) | — | Path handling, env-var override | Mirrors `check_dispatch.py:18` and `database.py:30` |
| `argparse` (stdlib) | — | `--output PATH` CLI flag | Mirrors `build_db.py` CLI pattern (CONTEXT.md D-04) |
| `collections.Counter` / `defaultdict` (stdlib) | — | Per-axis histograms | Already proven in `check_dispatch.py`-style iteration |
| `hashlib.sha1` (stdlib) | — | Stable DEFECT-COV-NN finding-hash (D-13) | sha1 is correct here — collision resistance against a 339-row signature space is overkill; first 12 hex chars (48 bits) suffices [VERIFIED: birthday-collision probability < 1e-9 for ≤ 1k findings] |
| `firestarter.database.EpromDatabase` | (in-repo) | DB loader singleton | Same import as `check_dispatch.py:21` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 9.0.3 (already installed) | Idempotence unit test | Land alongside the tool in Wave 0 / Wave 1 |
| stdlib `subprocess` | — | "run twice, diff zero" smoke pattern (optional — pytest can call the codegen function directly without spawning a process) | Only if the test asserts CLI surface, not the inner function |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hand-rolled hash composition for ledger | `hashlib.blake2b(..., digest_size=8)` | sha1 chosen for stdlib obviousness + matches no-installed-deps rule; 8-byte blake2b would also work but no win |
| `csv` instead of markdown for §3 | — | Markdown wins (operator scrolls once per D-05; csv requires viewer; matrix lives next to other `.planning/*.md`) |
| Separate ledger lookup module | Inline `_load_ledger() / _save_ledger() / _mint_id()` in `audit_coverage_matrix.py` | Inline is fine — ledger is dead-simple `dict[hash] → id`; one file = one tool |

**Installation:** None. All imports are stdlib + already-installed `firestarter` package.

**Version verification:** Skipped — no new external dependencies introduced.

## Architecture Patterns

### System Architecture Diagram

```
                              ┌─────────────────────────────────┐
                              │ FIRESTARTER_DB_FILE env-var?    │
                              │  fallback: chip_database.json   │
                              └───────────────┬─────────────────┘
                                              │
                                              ▼
              ┌───────────────────────────────────────────────────────────┐
              │  json.load(...)  +  EpromDatabase()  (singleton; for      │
              │  semantic lookups like get_eprom by alias if needed)      │
              └───────────────┬───────────────────────────────────────────┘
                              │
              ┌───────────────▼───────────────┐
              │  Single pass over             │
              │  (mfg, chips, c) tuples:      │
              │  filter algorithm ∈ {7, 8}    │
              │  → 339 rows                   │
              └───────┬───────────────────────┘
                      │
                      ├─ accumulate per-algo histograms (pinout, pulse, size)
                      ├─ accumulate per-cluster pulse_duration sets
                      ├─ collect HAZARD candidate rows (DIP28_28C64/256 + 0x07)
                      ├─ collect CORRECTNESS candidate rows (pulse outliers per cluster)
                      ├─ collect VARIANCE candidate rows (chip_id_check / chip_id_value flips)
                      │
                      ▼
              ┌───────────────────────────────┐
              │  Load committed ledger        │
              │  v1.3-defect-coverage-ids.json│
              └───────┬───────────────────────┘
                      │
                      ▼
              ┌───────────────────────────────┐
              │  For each finding-hash:       │
              │  reuse existing DEFECT-COV-NN │
              │  OR mint next NN              │
              └───────┬───────────────────────┘
                      │
                      ├─ emit §1 Summary stats
                      ├─ emit §2 DB Count Reconciliation
                      ├─ emit §3 Full Enumeration (per-algo, sorted)
                      ├─ emit §4 Defect Candidates (HAZARD→CORRECTNESS→VARIANCE)
                      ├─ emit §5 BENCH Coverage Proof (3 per-axis tables)
                      │
                      ▼
              ┌───────────────────────────────┐
              │  pathlib.Path.write_text(     │
              │    content,                   │
              │    encoding='utf-8',          │
              │    newline='\n')              │
              └───────┬───────────────────────┘
                      │
              ┌───────▼──────────────────────────────────┐
              │  exit 0: no new findings since ledger     │
              │  exit 1: new findings minted OR DB parse  │
              │         error  (mirrors check_dispatch)   │
              └───────────────────────────────────────────┘
```

### Recommended Project Structure
```
firestarter_app/
├── tools/
│   ├── audit_coverage_matrix.py    # NEW — the generator
│   ├── check_dispatch.py            # existing — skeleton donor
│   └── build_db.py                  # existing — CLI / override-list donor
└── tests/
    ├── conftest.py                  # existing — pytest infra
    └── test_audit_coverage_matrix.py  # NEW — idempotence + ledger-stability tests
.planning/
├── v1.3-COVERAGE-MATRIX.md          # NEW — generated, committed
└── v1.3-defect-coverage-ids.json    # NEW — generated, committed (ledger)
```

### Pattern 1: Mirror `check_dispatch.py` loader scaffold
**What:** Module-top path constants with `FIRESTARTER_DB_FILE` env-var override; import `EpromDatabase` for the singleton if any lookup-by-name surface is needed; iterate `db_raw.items()` for the raw row scan.
**When to use:** Always — this is the only loader pattern in the host repo and is already battle-tested.
**Example:**
```python
# Source: firestarter_app/tools/check_dispatch.py:23-30 (VERIFIED)
import json, os, sys
from firestarter.database import EpromDatabase

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "firestarter", "data")
DB_FILE = os.environ.get(
    "FIRESTARTER_DB_FILE",
    os.path.join(_DATA_DIR, "chip_database.json"),
)

def main():
    with open(DB_FILE, encoding="utf-8") as f:
        db_raw = json.load(f)
    for mfg, chips in db_raw.items():
        if not isinstance(chips, list):
            continue
        for chip in chips:
            proto = chip.get("programming", {}).get("algorithm", 0) or 0
            ...
```

### Pattern 2: Codegen idempotence (Phase 06 Plan 06-01 / LCAT-05)
**What:** Sort every iteration by stable key, format integers consistently, no timestamps in output, LF-only line endings.
**When to use:** Always for the matrix body AND the JSON ledger.
**Example:**
```python
# Source: .planning/phases/06-logging-infrastructure/06-RESEARCH.md:603-625 (VERIFIED)
# 1. Sort by ID ascending — input order is irrelevant
# 2. No timestamps — banner is a fixed string, NOT datetime.now()
# 3. LF line endings — pathlib.Path.write_text(content, encoding='utf-8', newline='\n')
# 4. Explicit ordering — for entry in sorted(items, key=lambda x: x['key'])
# 5. Stable string formatting — integer values as '0x%02X' consistently
# 6. UTF-8 throughout

# Verification (LCAT-05 quick test):
#   tool --output /tmp/a
#   tool --output /tmp/b
#   diff /tmp/a /tmp/b && echo "BYTE-IDENTICAL ✓"
```

### Pattern 3: Mirror `build_db.py` CLI surface
**What:** `argparse` with `--output PATH` (default `.planning/v1.3-COVERAGE-MATRIX.md`), optional `--check` flag (exit 1 if NEW findings minted vs current ledger; for future CI wiring per D-03).
**When to use:** For the tool's CLI surface only.
**Example:**
```python
# Source: derived from firestarter_app/tools/build_db.py CLI style + CONTEXT.md D-04
import argparse
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default=".planning/v1.3-COVERAGE-MATRIX.md")
    p.add_argument("--check", action="store_true",
                   help="exit 1 if new defect candidates would be minted")
    args = p.parse_args()
    ...
```

### Pattern 4: D-13 stable hash composition for DEFECT-COV-NN
**What:** A finding's identity = (severity, axis, normalized-signature-tuple). The signature is a tuple of grouping fields specific to the finding's axis. The hash is sha1 of the canonical JSON serialization (sort_keys=True, no whitespace).
**When to use:** Every defect-candidate row entered into the ledger.
**Example:**
```python
# Source: synthesized from CONTEXT.md D-13 + .planning/phases/06-logging-infrastructure/06-RESEARCH.md "stable key" rule
import hashlib, json

def finding_hash(severity, axis, signature):
    """
    severity : "HAZARD" | "CORRECTNESS" | "VARIANCE"
    axis     : str — the diverging field name (e.g. "pulse_duration", "chip_id_check",
                     "pinout_vs_algorithm", "chip_id_value")
    signature: tuple of grouping-key fields, ordered. Each field MUST be:
                 - a scalar (str, int, bool) OR
                 - a tuple of scalars (for set-valued fields, pre-sorted)
               so that JSON serialization is fully deterministic.
    """
    payload = {
        "severity": severity,
        "axis": axis,
        "signature": list(signature),  # JSON has no tuple
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha1(blob).hexdigest()[:16]  # 64 bits — collision-safe for ≤ 1k findings
```

**Signature composition per severity tier (recommended):**

| Severity | Axis examples | Signature tuple |
|----------|--------------|-----------------|
| HAZARD | `"pinout_vs_algorithm"` | `(pinout, algorithm_int, etype)` — one finding per (pinout, algo, etype) cluster |
| CORRECTNESS | `"pulse_duration_outlier"` | `(algorithm_int, pinout, size_bytes, manufacturer, part_number_first_alias)` — fine-grained so one outlier mints one finding |
| VARIANCE | `"chip_id_check_toggle"` | `(algorithm_int, pinout, size_bytes, manufacturer)` — cluster-level, all toggled parts share one finding |
| VARIANCE | `"chip_id_value_drift"` | `(algorithm_int, pinout, size_bytes, manufacturer)` — same cluster signature |

**Why this is collision-resistant for the live DB:**
- Live DB has 339 in-scope rows. Even if every row generated a unique finding (it won't), we have 339 hashes ≪ 2⁶⁴.
- The signature tuples are deterministically derived from existing DB fields; no manual labels.
- Adding NEW chips to the DB at v1.4 with the same pinout/algo/size as existing findings does NOT shift IDs — the signature is stable across row additions because it does not include row count.
- Risk surface: only changes to `severity` or `axis` strings (or to the signature schema) would re-hash. Document the schema in the tool's docstring; treat schema bumps as a ledger reset.

### Pattern 5: Phase 06 idempotence test pattern
**What:** Land a pytest unit test that runs the codegen function twice, asserts byte-identical output, asserts ledger is idempotent (no new IDs minted on second run).
**When to use:** Wave 0 / Wave 1, alongside the tool.
**Example:**
```python
# Source: synthesized from .planning/phases/06-logging-infrastructure/06-RESEARCH.md:603-625
# Pattern follows existing firestarter_app/tests/conftest.py + test_decoder.py style.
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

### Anti-Patterns to Avoid
- **Touching `chip_database.json` or `build_db.py`:** OUT OF SCOPE per CONTEXT.md `<domain>` and REQUIREMENTS.md COV-02. The matrix documents, never patches. (CONTEXT.md "NOT in scope" line 27.)
- **Touching firmware (`firestarter/src/proms/memory.cpp`, handlers):** OUT OF SCOPE — defects route to v1.4 sub-repo PRs.
- **Adding the new tool to the installed pip package:** `pyproject.toml` already excludes `tools/`; do not add an entry-point. The tool is a sibling of `check_dispatch.py` / `build_db.py`, runs as `python tools/audit_coverage_matrix.py`.
- **Wiring `audit_coverage_matrix.py` to CI as a drift gate:** D-03 keeps the exit-code discipline for future CI; Phase 11 does NOT wire CI per CONTEXT.md Deferred Ideas.
- **Proposing BENCH-05 / BENCH-06 chip swaps in §5:** D-11 explicitly forbids it. Phase 12 CONTEXT.md owns selection.
- **Splitting the matrix into multiple files:** D-05 mandates single combined file. The ledger is the only sibling artifact, and it is JSON, not markdown.
- **Including `datetime.now()` anywhere in the output:** breaks idempotence — the matrix would diff every run.
- **Using `dict.items()` without sorting:** Python 3.7+ preserves insertion order, but the sort is the load-bearing contract per Pattern 2.
- **Hand-rolling a CSV / TSV intermediate:** the matrix is markdown; intermediate formats add complexity without benefit.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| DB row iteration | Custom `os.walk` / glob over the data dir | `for mfg, chips in db_raw.items(): for chip in chips:` | One JSON file = one `json.load`; every existing tool uses this shape. |
| Pinout → pin lookup | Recompute `pin_conversions` table | `EpromDatabase().get_pin_map()` / direct read of `pinouts.json` | Already shipped + tested + Phase-12-verified. Only needed for §4 HAZARD descriptions if quoting "pin 1 = A14 on DIP28_28C256". |
| Variant-string parsing | Custom comma-split | Either store `part_number` verbatim (D-06) OR reuse `database.py:471-491`'s `_strip_paren` / alias-split helpers if needed | Variant count vs row count is documented in CONTEXT.md `<code_context>` — the matrix exposes BOTH. |
| Markdown table emission | A library like `tabulate` | Plain string formatting with column widths derived from max-width-per-column | Zero deps wins; matches `.planning/MILESTONES.md` + `08-MEASUREMENT.md` precedent. |
| Stable hash for ledger | Hand-coded XOR / hashlib.md5 (deprecated by some) | `hashlib.sha1(canonical-json-bytes).hexdigest()[:16]` | sha1 is stdlib + cryptographically irrelevant here (collision resistance is the only relevant property and 64-bit truncation is fine). |
| Bucketing pulse_duration | Floats + thresholds | Integer microseconds extracted from `"NNN us"` string + tuple boundaries | Pulse strings are already integer-microsecond labels (see DB audit below); a single `int(s.replace(" us",""))` suffices. |
| JSON ledger write | `pickle` or YAML | `json.dumps(d, indent=2, sort_keys=True) + "\n"` | Stays diff-clean; sorts keys (LedgerKey strings → hashes are alpha-sortable); LF-terminated. |

**Key insight:** The host repo already contains every primitive this tool needs. The wave plan should explicitly NOT add any package, NOT touch installed code, NOT introduce new test dependencies. The only new files are `tools/audit_coverage_matrix.py`, `tests/test_audit_coverage_matrix.py`, `.planning/v1.3-COVERAGE-MATRIX.md`, `.planning/v1.3-defect-coverage-ids.json`.

## Runtime State Inventory

> Phase 11 is a desk-side codegen + documentation phase. No service is being renamed; no DB schema changes; no stored data is being migrated. The five categories below are answered explicitly for completeness.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — the matrix and ledger are NEW files; `chip_database.json` is read-only input | none |
| Live service config | None — no n8n / Datadog / Tailscale touch points | none |
| OS-registered state | None — no Task Scheduler / pm2 / systemd interactions | none |
| Secrets/env vars | One env var READ: `FIRESTARTER_DB_FILE` (existing, inherited from `check_dispatch.py:27-30`). No secrets, no new vars | none |
| Build artifacts | None — `pyproject.toml` / `MANIFEST.in` already exclude `tools/`; no wheel re-packaging needed | none |

## Live DB Audit (empirical input to §1, §2, §3, §4, §5)

The following counts and clusters come from running a one-pass scan over `firestarter_app/firestarter/data/chip_database.json` at HEAD on branch `refactor/v1.3-foundations` (2026-05-19). Every number below is `[VERIFIED: live DB scan, 2026-05-19]` and must be reproduced exactly by the new tool on its first run — they are the regression anchor.

### Phase 11 Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| COV-01 | Generate coverage matrix from `chip_database.json` enumerating every algo-0x07 + algo-0x08 row with: manufacturer, part_number(s), pin_count, size_bytes, pulse_duration, chip_id_check, chip_id_value, pinout class. Output: `.planning/v1.3-COVERAGE-MATRIX.md`. **CORRECTION: 339 chips (not 341)** | Full enumeration logic = single-pass over `db_raw.items()` filtered by `algorithm ∈ {7, 8}`; sort order from D-06; column set documented in §3. CONTEXT.md D-07 already locked the count correction. |
| COV-02 | Identify DB inconsistencies (chips sharing `pin_count + algorithm` but differing in `pulse_duration`, `chip_id_check`, or `pinout`) flagged as defect candidates (no auto-fixes in v1.3) | Three-tier taxonomy from CONTEXT.md D-12; HAZARD candidates from §4 cluster audit below; CORRECTNESS pulse-outlier scan + VARIANCE chip-id-toggle scan executed against live DB. |

### Top-level counts (CONFIRMED, all VERIFIED against live DB scan)

| Field | Live DB value | CONTEXT.md / docs claim | Drift |
|-------|---------------|-------------------------|-------|
| Total chips | **734** | 743 (PROJECT.md L43, L79, L86, L135, L149, L151; ROADMAP.md L134) | −9 |
| algo-0x07 count | **212** | 214 (ROADMAP.md L12, STATE.md L109, PROJECT.md L150) | −2 |
| algo-0x08 count | **127** | 127 (all sources) | 0 ✓ |
| In-scope (0x07 + 0x08) | **339** | 341 (ROADMAP.md L27, L39, L41; REQUIREMENTS.md L30; PROJECT.md L16) | −2 |

**Full live per-algorithm histogram (2026-05-19):**
```
0x05: 27    0x0B: 40    0x10: 39    0x29: 20
0x06: 190   0x0D: 23    0x27:  2
0x07: 212   0x0E: 20    0x28: 34
0x08: 127
                                      TOTAL: 734
```

**Diff vs PROJECT.md L150 ("Algorithm histogram: 0x05=27, 0x06=190, 0x07=214, 0x08=127, 0x0B=53, 0x0D=41, 0x0E=20, 0x10=39, 0x27=2, 0x28=10, 0x29=20 (totals 743)"):**

| Algo | Claimed | Live | Δ |
|------|---------|------|---|
| 0x07 | 214 | 212 | −2 |
| 0x0B | 53 | 40 | −13 |
| 0x0D | 41 | 23 | −18 |
| 0x28 | 10 | 34 | +24 |

The fm1608-db-mismatch override (`build_db.py:446-468`, executed AFTER the WARNING-5 override and BEFORE the protocol-aware `_etype` re-derivation) flips chips with `type=4 ∧ proto_id ∈ {0x07, 0x08, 0x0B}` to `proto_id = 0x28`, which explains the 0x0B → 0x28 shift. The 0x0D delta is the WARNING-5 override draining FROM 0x07 INTO 0x0D for the 23 chips that DID satisfy `etype == Flash/EEPROM` at override time — but the live `0x0D` count is 23 not 41, so the upstream xml + override set has changed since the v1.0 historical doc was written. **The matrix's §2 reconciliation should treat this as "delta absorbed by v1.0-v1.2 overrides + upstream xml drift" per CONTEXT.md "Claude's Discretion" — no archaeology required.**

### algo-0x07 distributions (212 chips)

**Pinout class histogram:**
| Pinout | Row count |
|--------|-----------|
| DIP28_27256 | 67 |
| DIP28_2764 | 58 |
| DIP28_27512 | 45 |
| DIP28_28C64 | 35 |
| DIP28_28C256 | 7 |

**Pulse-duration histogram (ascending):**
| pulse_duration | rows |
|----------------|------|
| 100 us | 1 |
| 5000 us | 4 |
| 10000 us | 113 |
| 20000 us | 31 |
| 50000 us | 4 |
| 100000 us | 28 |
| 300000 us | 1 |
| 500000 us | 2 |
| 1000000 us | 28 |

**Size-bytes histogram (ascending):**
| size_bytes | rows | label |
|-----------|------|-------|
| 2048 | 7 | 2K |
| 8192 | 57 | 8K |
| 16384 | 26 | 16K |
| 32768 | 74 | 32K |
| 65536 | 45 | 64K |
| 131072 | 3 | 128K |

**`chip_id_check`:** True=129, False=83
**`electrical.type`:** UV-EPROM=212 (post-override re-derivation tags ALL 0x07 chips as UV-EPROM)

### algo-0x08 distributions (127 chips)

**Pinout class:** DIP32_STD=127 (uniform — only one pinout class for algo-0x08)

**Pulse-duration histogram:**
| pulse_duration | rows |
|----------------|------|
| 10 us | 7 |
| 20 us | 1 |
| 50 us | 11 |
| 100 us | 104 |
| 200 us | 2 |
| 1000 us | 2 |

**Size-bytes histogram:**
| size_bytes | rows | label |
|-----------|------|-------|
| 65536 | 1 | 64K |
| 131072 | 51 | 128K |
| 262144 | 36 | 256K |
| 524288 | 31 | 512K |
| 1048576 | 8 | 1 MB |

**`chip_id_check`:** True=95, False=32
**`electrical.type`:** UV-EPROM=127

### Bucket boundary recommendation (D-09 Claude's discretion)

The CONTEXT.md proposes `<100 µs / 100-999 µs / 1-9 ms / 10-99 ms / 100 ms-1 s`. **Verdict: keep these boundaries** — they map cleanly to the empirical clusters above:

| Bucket | algo-0x07 rows | algo-0x08 rows | Coverage notes |
|--------|---------------|----------------|----------------|
| < 100 µs | 0 | 8 (10/20/50 µs) | algo-0x08 only — covered by BENCH-04 (W27E040 = 50 µs typical) if BENCH-04's actual pulse is in-bucket |
| 100–999 µs | 1 (the 100 µs outlier in 28C256) | 117 (100 + 200 µs) | algo-0x08: dominant mass; W27C020 / W27E040 BENCH chips live here |
| 1–9 ms | 4 (5 ms cluster) | 2 (1 ms) | algo-0x07: thin cluster; W27C512 BENCH chips here at < 10 ms typical |
| 10–99 ms | 144 (10 ms = 113, 20 ms = 31) | 0 | algo-0x07: dominant mass; W27C512 + SST27SF512 BENCH chips at 10 ms |
| 100 ms–1 s | 63 (100 / 300 / 500 / 1000 ms) | 0 | algo-0x07: 28C-family suspects cluster here at 1 s — flagged as HAZARD candidates |

The boundaries surface the algo-0x08 vs algo-0x07 magnitude shift cleanly; no benefit from re-bucketing.

### HAZARD candidate cluster (CONFIRMED — the headline new finding) [VERIFIED: dispatch simulation against live DB, 2026-05-19]

| Cluster | algorithm | pinout | row count | configure_eprom dispatches? | Pin 1 on pinout | Risk |
|---------|-----------|--------|-----------|-----------------------------|-----------------|------|
| DIP28_28C64 + 0x07 | 0x07 | DIP28_28C64 | **35** | **YES** | NC (5V part, WE on pin 27) | 12V VPP_ENABLE on socket pin 1 every write pulse |
| DIP28_28C256 + 0x07 | 0x07 | DIP28_28C256 | **7** | **YES** | A14 (5V part, WE on pin 27) | 12V on A14 = hardware damage path |
| **Total HAZARD rows** | | | **42** | | | |

**Why the existing WARNING-5 override does NOT catch these:** `build_db.py:415-423` predicate is `pinout in ("DIP28_2764", "DIP28_28C256") AND proto_id == 0x07 AND _etype == "Flash/EEPROM"`. The `_etype` is set by the upstream `flags & 0x10` test at `build_db.py:392-393`. For these 42 chips, upstream `flags & 0x10` evaluates False (upstream minipro tags them differently — likely as plain 0x07 EPROM_STD without the EEPROM flag bit), so `_etype = "UV-EPROM"` and the WARNING-5 predicate is not satisfied. The override is bypassed. After the post-override `_etype` re-derivation at `build_db.py:481-486`, all of these chips get re-tagged `_etype = "UV-EPROM"` because they remain on 0x07. The matrix MUST flag this exact override-bypass class as the new HAZARD finding. The `pinouts.json` comments on `DIP28_28C64` and `DIP28_28C256` (read above) explicitly say "Routes through configure_eeprom28c via WARNING-5 algo flip" — that's the design intent, but for these 42 chips the flip never happened.

**Manufacturer distribution (HAZARD):**

| Manufacturer | DIP28_28C64 rows | DIP28_28C256 rows | Total |
|--------------|-------------------|-------------------|-------|
| AMD | 2 | — | 2 |
| ATMEL | 8 | — | 8 |
| CATALYST(CSI) | 4 | 2 | 6 |
| CYPRESS | — | 1 | 1 |
| EXEL | 3 | 1 | 4 |
| FUJITSU | — | 1 | 1 |
| HITACHI | — | 1 | 1 |
| MICROCHIP memory | 7 | — | 7 |
| NEC | 1 | — | 1 |
| SAMSUNG | 2 | — | 2 |
| SGS-THOMSON | 2 | — | 2 |
| ST | 3 | — | 3 |
| XICOR | 3 | 1 | 4 |

**Representative HAZARD examples for the matrix's `examples` field per CONTEXT.md D-14:**

- DIP28_28C64 cluster: `AMD/AM28C64A,AM28C64AE,AM28C64B,AM28C64BE`, `ATMEL/AT28C17`, `MICROCHIP memory/28C64AF`
- DIP28_28C256 cluster: `CATALYST(CSI)/CAT28C256,CAT28C257`, `XICOR/X28C256`, `FUJITSU/MB85R256H`

### CORRECTNESS candidate clusters (pulse_duration variance within (algo, pinout, size))

| algorithm | pinout | size_bytes | row count | distinct pulses | Notes |
|-----------|--------|------------|-----------|-----------------|-------|
| 0x07 | DIP28_27256 | 32768 | 67 | 5 ({5/10/20/50/100} ms) | Dominant mass at 10 ms; 6 chips at 100 ms = candidate outliers |
| 0x07 | DIP28_27512 | 65536 | 45 | 4 ({5/10/20/100} ms) | Dominant mass at 10 ms; 2 chips at 100 ms |
| 0x07 | DIP28_2764 | 8192 | 29 | 4 ({10/20/50/100} ms) | Bimodal: 12 at 10 ms vs 12 at 100 ms |
| 0x07 | DIP28_2764 | 16384 | 26 | 4 ({10/20/50/100} ms) | Bimodal |
| 0x07 | DIP28_28C256 | 32768 | 7 | 2 ({100 us, 1 s}) | **CORRECTNESS outlier: Fujitsu MB85R256H at 100 µs while 6 others at 1 s** — strong "wrong-class" signal (MB85R256H is a FRAM) |
| 0x07 | DIP28_28C64 | 2048 | 7 | 4 ({20/100/500/1000} ms) | High variance |
| 0x07 | DIP28_28C64 | 8192 | 28 | 5 ({20/100/300/500/1000} ms) | High variance; 20 at 1 s + 4 at 100 ms (likely a few wrongly-pulled chips) |
| 0x08 | DIP32_STD | 131072 | 51 | 5 ({10/50/100/200/1000} us) | Dominant 100 µs (44 chips); a few 1000-µs outliers |
| 0x08 | DIP32_STD | 262144 | 36 | 4 ({10/20/50/100} us) | Dominant 100 µs |
| 0x08 | DIP32_STD | 524288 | 31 | 4 ({10/50/100/1000} us) | Dominant 100 µs; **one chip at 1000 µs** — outlier |
| 0x08 | DIP32_STD | 1048576 | 8 | 2 ({50/100} us) | Bimodal |
| **Total CORRECTNESS clusters** | | | | **11** | each cluster mints ≥ 1 finding; outliers within each get their own row |

**Per-cluster outlier scan (≥ 10x the cluster median):**

- `algo=0x07 DIP28_28C64 size=8192`: `ATMEL/AT28C64E,AT28C64F` pulse=20 ms (median 1 s) — 50x faster than peers
- `algo=0x07 DIP28_28C64 size=8192`: `MICROCHIP memory/28C64AF` pulse=20 ms (median 1 s)
- `algo=0x07 DIP28_28C256 size=32768`: `FUJITSU/MB85R256H` pulse=100 µs (median 1 s) — 10000x faster ⇒ this is a FRAM mistakenly classified as 28C256

These three are the "near-identical part at 100x off" pattern CONTEXT.md D-12 describes.

### VARIANCE candidate clusters

**`chip_id_check` toggled within (algo, pinout, size, manufacturer):** 13 clusters detected. Examples:

| Cluster | Toggled members |
|---------|-----------------|
| 0x07 DIP28_27256 32768 CATALYST(CSI) | `CAT27256,CAT27HC256I` (False) vs `CAT27HC256` (True) |
| 0x07 DIP28_27256 32768 CYPRESS | `CY27C256` (False) vs `CY27H256` (True) |
| 0x07 DIP28_27512 65536 CYPRESS | `CY27C512` (False) vs `CY27H512` (True) |
| 0x07 DIP28_2764 8192 HITACHI | `HN27C64G` (False) vs `HN27C64FP` (True) |
| 0x07 DIP28_2764 8192 TI | `TMS2764` (False) vs `TMS27C64,TMS27PC64` (True) |
| 0x07 DIP28_2764 16384 WSI | `WS27C128F` (True) vs `WS57C128FB` (False) |
| 0x08 DIP32_STD 131072 HITACHI | `HN27C101AG,...` (True), `HN27C301AG,...` (True), `HN27C301G` (False) |
| 0x08 DIP32_STD 131072 SGS-THOMSON | `M23C1001` (False), `M27C1000` (True), `M27C1001,M27V101` (True) |

**`chip_id_value` drift within (algo, pinout, size, manufacturer)** where `chip_id_check=True` on multiple members with different `chip_id_value`: **36 clusters**. Most are legitimate (different die revisions = different IDs). The matrix records these as VARIANCE / informational by default — not actionable, but visible.

## Common Pitfalls

### Pitfall 1: `_etype` re-derivation race
**What goes wrong:** A reader of the live DB sees `electrical.type == "UV-EPROM"` on a `DIP28_28C64` row and assumes the WARNING-5 override already neutralised the hazard.
**Why it happens:** `build_db.py:481-486` rewrites `_etype` AFTER the WARNING-5 override runs at `build_db.py:415-423`. If the upstream `flags & 0x10` was False at predicate time, the override is bypassed but the row still ends up with `_etype = "UV-EPROM"` after re-derivation.
**How to avoid:** The matrix's §4 description for the HAZARD finding MUST explicitly note "after `_etype` is re-derived to UV-EPROM at `build_db.py:481-486`, the WARNING-5 predicate (`_etype == 'Flash/EEPROM'`) is structurally unreachable for these 42 rows — the override cannot catch them. Fix venue: extend WARNING-5 predicate to gate on `pinout` alone (drop the `_etype` clause) at `build_db.py:415`, OR add a new override class keyed on `pinout ∈ {DIP28_28C64, DIP28_28C256} ∧ proto_id == 0x07`."
**Warning signs:** Reading the WARNING-5 override and concluding "it covers DIP28_28C256" without tracing the predicate.

### Pitfall 2: Variant string ≠ row
**What goes wrong:** Summary stats say "339 rows" but operator searches by alias and counts "490 chips" — confusion.
**Why it happens:** `part_number` is a comma-joined alias string. `W27C512,W27E512` is one row covering two chip names.
**How to avoid:** §1 Summary stats expose both `row_count` and `variant_count`. The variant count is `sum(len(part_number.split(",")) for row in rows)`. CONTEXT.md `<code_context>` notes this explicitly.

### Pitfall 3: Pulse string parsing
**What goes wrong:** Tool parses `pulse_duration` as a float, gets `10000.0` for "10000 us", then fails to bucket cleanly because of float comparison surprises.
**Why it happens:** `build_db.py:515` calls `interpret_timing(...)` which returns a string like `"10000 us"`. The trailing " us" is always present per the live DB scan.
**How to avoid:** Parse as `int(pulse_str.split(" ")[0])` or `int(pulse_str.replace(" us", ""))`. The integer microsecond value is the canonical key.
**Warning signs:** If any chip has a `pulse_duration` not ending in " us", the parser MUST raise — DO NOT silently coerce, that's how hidden divergences slip in.

### Pitfall 4: Ledger lookup with empty file
**What goes wrong:** First-ever run finds no `.planning/v1.3-defect-coverage-ids.json`, crashes on `json.load`.
**Why it happens:** The ledger doesn't exist until the first run mints it.
**How to avoid:** Treat absent ledger as `{}`:
```python
try:
    ledger = json.loads(ledger_path.read_text())
except FileNotFoundError:
    ledger = {}
```
**Warning signs:** Test the cold-start path explicitly in the pytest suite (`test_first_run_creates_ledger`).

### Pitfall 5: Ledger key shadowing
**What goes wrong:** Two findings hash to the same 16-hex value (the truncated sha1). Second overwrites first.
**Why it happens:** 64-bit truncation has ~1e-9 collision probability per pair across ~1k findings (birthday paradox); realistically not a problem for ≤ 1k findings but worth defending.
**How to avoid:** When `mint_id` is called and the hash already exists in the ledger, verify the signature payload matches; if it doesn't, raise a hard error. This catches both genuine collisions AND signature-schema accidents.

### Pitfall 6: Operator runs `python tools/audit_coverage_matrix.py` from the wrong cwd
**What goes wrong:** Tool writes the matrix to `<cwd>/.planning/v1.3-COVERAGE-MATRIX.md` instead of `<repo-root>/.planning/v1.3-COVERAGE-MATRIX.md`. Two matrices in the tree.
**Why it happens:** `argparse` default is a relative path.
**How to avoid:** Either (a) make the default absolute by computing `_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))` (sibling of `firestarter_app/`) and joining, OR (b) document the run-from-meta-repo-root convention in the tool's `--help` text. Recommended: (a) for robustness, since the operator's typical cwd varies.

### Pitfall 7: Mixing CRLF and LF on Windows
**What goes wrong:** Tool runs on Windows, emits CRLF, diff against committed LF version reports every line as changed.
**Why it happens:** Python's default `open(..., "w")` uses platform newlines.
**How to avoid:** `pathlib.Path.write_text(content, encoding="utf-8", newline="\n")` — explicit. Mirror the LCAT-05 recipe.

## Code Examples

### Loader + per-chip iteration scaffold (verbatim mirror)
```python
# Source: firestarter_app/tools/check_dispatch.py:17-30 + 86-104 (VERIFIED)
import json
import os
import sys

from firestarter.database import EpromDatabase

_DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "firestarter", "data"
)
DB_FILE = os.environ.get(
    "FIRESTARTER_DB_FILE",
    os.path.join(_DATA_DIR, "chip_database.json"),
)

def iter_in_scope_rows():
    with open(DB_FILE, encoding="utf-8") as f:
        db_raw = json.load(f)
    for mfg, chips in db_raw.items():
        if not isinstance(chips, list):
            continue
        for chip in chips:
            proto = chip.get("programming", {}).get("algorithm", 0) or 0
            if proto in (0x07, 0x08):
                yield mfg, chip
```

### Sort key for full enumeration (D-06)
```python
# Source: synthesized from CONTEXT.md D-06 + Phase 06 idempotence rule
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

### Pulse-duration parser
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

### Stable defect-ID minter
```python
# Source: synthesized from CONTEXT.md D-13 + Pattern 4 above
import hashlib, json

def finding_hash(severity, axis, signature):
    payload = {
        "severity": severity,
        "axis": axis,
        "signature": list(signature),
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha1(blob).hexdigest()[:16]

def mint_or_reuse(ledger, severity, axis, signature, next_n_holder):
    """Return existing DEFECT-COV-NN or mint a new one. Mutates ledger in-place."""
    h = finding_hash(severity, axis, signature)
    if h in ledger:
        return ledger[h]
    n = next_n_holder[0]
    next_n_holder[0] += 1
    new_id = f"DEFECT-COV-{n:02d}"
    ledger[h] = new_id
    return new_id
```

### Idempotent file write
```python
from pathlib import Path

def emit(content_lines, output_path):
    """LF-only, UTF-8, trailing newline — Phase 06 LCAT-05 recipe."""
    content = "\n".join(content_lines) + "\n"
    Path(output_path).write_text(content, encoding="utf-8", newline="\n")

def emit_ledger(ledger, ledger_path):
    """sort_keys=True so hash-key ordering is deterministic."""
    blob = json.dumps(ledger, indent=2, sort_keys=True) + "\n"
    Path(ledger_path).write_text(blob, encoding="utf-8", newline="\n")
```

### Markdown table emitter (D-06 / D-09 style — mirrors 08-MEASUREMENT.md)
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

## D-07 Planning-Doc Reconciliation — Exact Edit Plan

The reconciliation task should land as the **last** wave (after the matrix's final numbers are locked) per CONTEXT.md Claude's Discretion.

**Target edits (15 total locations):**

| File | Line | Current substring | Replacement | Note |
|------|------|-------------------|-------------|------|
| `.planning/PROJECT.md` | 16 | `~341 algorithm-0x07 + algorithm-0x08` | `339 algorithm-0x07 + algorithm-0x08` | Target features bullet |
| `.planning/PROJECT.md` | 43 | `743 chips with` | `734 chips with` | "Current State (v1.0)" para |
| `.planning/PROJECT.md` | 79 | `check_dispatch.py` across 743 chips | `check_dispatch.py` across 734 chips | "Validated by v1.0" line |
| `.planning/PROJECT.md` | 86 | `743 chips` | `734 chips` | Last bullet of validated list |
| `.planning/PROJECT.md` | 135 | n/a — `743` not in the cell text | (no edit — context line about v1.1 P2 only mentions 743 in old narrative) | **Verify**: re-scan; if the line says "across 743 chips" in the decisions-table cell, update; if it's historical narrative referring to the v1.0 state, leave it. Pre-edit grep showed L135 = decisions-table row mentioning Phase 11 packaging — no `743` substring at first glance; the L135 hit was a false-positive on a long line. Treat as **conditional**. |
| `.planning/PROJECT.md` | 149 | `743 chips post-v1.0` | `734 chips post-v1.0` (or add a footnote: "v1.0 closed at 743; v1.1-v1.2 overrides + upstream xml drift reduced to 734 by v1.3 start") | "Context: Database state" |
| `.planning/PROJECT.md` | 150 | `0x07=214` | `0x07=212` | algorithm histogram |
| `.planning/PROJECT.md` | 150 | `0x0B=53` | `0x0B=40` | algorithm histogram |
| `.planning/PROJECT.md` | 150 | `0x0D=41` | `0x0D=23` | algorithm histogram |
| `.planning/PROJECT.md` | 150 | `0x28=10` | `0x28=34` | algorithm histogram |
| `.planning/PROJECT.md` | 151 | `(totals 743)` | `(totals 734)` | histogram totals |
| `.planning/PROJECT.md` | 190 | `(28-pin, 214 chips)` | `(28-pin, 212 chips)` | last-updated footer |
| `.planning/ROADMAP.md` | 12 | `(28-pin DIP CMOS UV-EPROM, 214 chips in DB)` | `(28-pin DIP CMOS UV-EPROM, 212 chips in DB)` | v1.3 goal paragraph |
| `.planning/ROADMAP.md` | 27 | `Desk-side enumeration of all 341 algo-0x07/0x08 DB rows` | `Desk-side enumeration of all 339 algo-0x07/0x08 DB rows` | Phase 11 bullet |
| `.planning/ROADMAP.md` | 39 | `(214 + 127 = 341 chips)` | `(212 + 127 = 339 chips)` | SC-01 of Phase 11 |
| `.planning/ROADMAP.md` | 41 | `the rest of the 341 rows` | `the rest of the 339 rows` | SC-03 of Phase 11 |
| `.planning/ROADMAP.md` | 134 | `743-chip database` | `734-chip database` (or annotate: "743-chip database at v1.0 close; 734 after v1.1-v1.2 overrides") | v1.0 archived bullet — historical, optional |
| `.planning/REQUIREMENTS.md` | 30 | `341 chips covered.` | `339 chips covered.` | COV-01 acceptance |
| `.planning/STATE.md` | 36 | `~341 algo-0x07 + algo-0x08` | `~339 algo-0x07 + algo-0x08` | Current focus paragraph |
| `.planning/STATE.md` | 48 | `341 algo-0x07/0x08 DB rows` | `339 algo-0x07/0x08 DB rows` | v1.3 phases table |
| `.planning/STATE.md` | 109 | `214 chips in DB) + algorithm-0x08 (32-pin DIP CMOS UV-EPROM, 127 chips in DB)` | `212 chips in DB) + algorithm-0x08 (32-pin DIP CMOS UV-EPROM, 127 chips in DB)` | v1.3 Decisions |
| `.planning/STATE.md` | 109 | `all 341 in-scope DB rows` | `all 339 in-scope DB rows` | same line, second occurrence |

**Note on archive integrity:** `743` references inside `<details>` archived sections of ROADMAP.md (v1.0 archive bullet L134) and historical decision-log rows in PROJECT.md (L135 — narrative about Phase 2 of v1.1) describe HISTORICAL DB state at v1.0 close. Per CONTEXT.md "Claude's Discretion" ("short note, no archaeology"), the recommended treatment is:

- Update LIVE v1.3 acceptance / coverage statements (rows above) to current live counts.
- Leave HISTORICAL narrative (v1.0-archived context) alone, with one explanatory footnote in PROJECT.md L149's "Context" block that records the drift: "DB count was 743 at v1.0 close; subsequent v1.1-v1.2 overrides + upstream `infoic.xml` drift reduced to 734 by v1.3 start. See `.planning/v1.3-COVERAGE-MATRIX.md` §2 for full reconciliation."

The plan should treat each row in the table above as a single Edit task; one task per file, one commit per file, or one combined commit per CONTEXT.md "single commit, separate from the matrix-tool commits" (D-07).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Inline `cat <<EOF >> matrix.md` shell scripts | Committed Python tool with idempotent codegen | Phase 06 (LCAT-05 idempotence rule) | Re-runnable; diffs are tractable; CI-wirable later |
| Hand-maintained inconsistency lists in `MILESTONES.md` | Generator-emitted markdown table with stable IDs | This phase | DB regen does not invalidate operator references; v1.4 PRs cite stable IDs |
| String-formatted dict iteration (insertion order) | Sorted iteration with explicit key tuples | Phase 06 | Byte-identity of regenerated artifact across machines + Python minor versions |
| `743` chip count quoted everywhere | Live DB scan + matrix §2 reconciliation | This phase | Single source of truth |

**Deprecated/outdated:**
- The "743 chips" + "341 in-scope" + "214 algo-0x07" figures in `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md` — replaced by 734 / 339 / 212.
- ROADMAP.md L39's SC-01 phrasing "214 + 127 = 341" — replaced by "212 + 127 = 339" per D-07.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | sha1-truncated-to-16-hex is collision-resistant for ≤ 1k findings | Pattern 4 / Standard Stack | If wrong: two findings collide and stomp each other in the ledger. Defense: the mint function should verify the cached payload matches the new signature; raise on mismatch. |
| A2 | The `pulse_duration` string format is always `"<int> us"` for in-scope rows | Code Examples / Pitfall 3 | If wrong: parser raises; fail-fast. Verified for all 339 rows in this audit, but a future build_db.py change could regress. |
| A3 | Operator runs the tool from meta-repo root (where `.planning/` is a subdirectory) OR the tool resolves to repo-root via `__file__` walk | Pitfall 6 | If wrong: matrix lands in wrong cwd; operator notices on `git status`. Defense: compute absolute default from `__file__`. |
| A4 | The 23-chip drift on algo-0x0D (claimed 41 vs live 23) and the 24-chip surge on algo-0x28 (claimed 10 vs live 34) are explained by the fm1608-db-mismatch override at `build_db.py:446-468` + upstream `infoic.xml` updates between v1.0 close and v1.3 start | Live DB Audit / D-07 | If wrong: the reconciliation §2 may need to dig deeper (git log on `chip_database.json`). CONTEXT.md "Claude's Discretion" already authorises "short note, no archaeology" — so this is low-risk operationally. |
| A5 | The matrix's §4 HAZARD finding does NOT need bench validation to be entered into the ledger — the dispatch simulation + pinout analysis is sufficient evidence | Live DB Audit / Pitfall 1 | If wrong: the finding's `suggested_fix_venue` should read `awaiting bench data` rather than `v1.4 build_db.py override`. The matrix should err on the side of `v1.4 build_db.py override` because the WARNING-5 precedent + pinouts.json comments + check_dispatch.py guard already establish the design intent. |
| A6 | Phase 11 does NOT need to update the v1.0 archived `<details>` blocks in ROADMAP.md (L134) or the v1.0 decisions-log rows in PROJECT.md (L135) that reference `743` as a historical state | D-07 Exact Edit Plan | If wrong: planner adds an extra Edit task for historical context. Cheap to revisit. |

## Open Questions

1. **Should the matrix include a `programmable-on-bench?` advisory column in §3?**
   - What we know: D-06 specifies 9 columns (manufacturer, part_number(s), pin_count, size_bytes, pulse_duration, chip_id_check, chip_id_value, pinout, electrical.type). No advisory column.
   - What's unclear: Phase 12 / 13 operators might want a glance-by-glance "is this chip even routable" indicator.
   - Recommendation: Skip — adds a derived column and complicates idempotence. The §5 BENCH coverage proof tables ARE the advisory surface.

2. **Should DEFECT-COV-NN be zero-padded to 2 or 3 digits?**
   - What we know: CONTEXT.md D-13 example is `DEFECT-COV-NN` with no width spec.
   - What's unclear: 339 chips could theoretically produce ~50 findings (HAZARD = 1 cluster, CORRECTNESS ≤ 11 clusters, VARIANCE ≤ 49 clusters). Two digits suffice for the v1.3 horizon, three is future-proof.
   - Recommendation: 2-digit (`DEFECT-COV-00..99`). If v1.4 expands the matrix to all 13 algorithms, bump to 3-digit at that point. The ledger stores the raw integer separately from the formatted ID; reformatting is a one-line change.

3. **Single ledger file or split per-tier?**
   - What we know: D-13 specifies one ledger file.
   - What's unclear: nothing — D-13 is explicit.
   - Recommendation: single file. Done.

4. **What happens if `chip_database.json` is regenerated mid-phase and a HAZARD finding's hash changes (e.g., a new pinout joins the cluster)?**
   - What we know: D-08 says "tool flags the new delta vs the matrix's last-committed counts".
   - What's unclear: if the signature evolves (e.g., the cluster now includes a third pinout), does the finding get a new ID? The hash composition (pinout, algo, etype) means a NEW pinout-flavoured row mints a NEW finding — old one stays in the ledger with no rows pointing at it.
   - Recommendation: the tool MUST emit a "ledger-orphan" warning if a finding-hash in the ledger has zero matching rows in the live DB. Operator decides whether to retire the ID or investigate.

5. **Should the §5 coverage tables call out BENCH-05/06 candidate chips by name?**
   - What we know: D-11 says "Phase 11 stays observational on BENCH-05 / BENCH-06 selection." But CONTEXT.md also says "It flags uncovered pinout classes (DIP28_28C64 = 35 algo-0x07 rows; DIP28_28C256 = 7 rows) and uncovered pulse buckets neutrally."
   - Recommendation: §5 names the BENCH-01..06 chips from REQUIREMENTS.md as the column headers ("BENCH chip that exercises this pinout") because that's how operators read the tables. It does NOT propose alternatives or selection changes.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Everything | ✓ | ≥ 3.9 (per `pyproject.toml`) | — |
| pytest | Idempotence test | ✓ | 9.0.3 | — (already installed) |
| `firestarter` package | EpromDatabase import | ✓ | dev-install via `pip install -e .` (assumed already done) | If absent: `python tools/audit_coverage_matrix.py` can fall back to pure `json.load` without the EpromDatabase singleton — singleton is only needed if §4 quotes pin layouts |
| `firestarter_app/firestarter/data/chip_database.json` | DB read | ✓ | live HEAD (734 chips, 2026-05-19) | — |
| `firestarter_app/firestarter/data/pinouts.json` | §4 HAZARD descriptions (pin 1 = A14 quotes) | ✓ | live HEAD | — |
| git working tree | Commit + ledger persistence | ✓ | branch `refactor/v1.3-foundations` | — |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none.

The phase introduces no new dependencies. Verified by `which pytest` + `cat pyproject.toml` + filesystem `ls`.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 [VERIFIED: `pytest --version`] |
| Config file | None — discovered via `firestarter_app/tests/conftest.py` and CWD = `firestarter_app/` (mirrors Phase 06 Plan 03 pattern) |
| Quick run command | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py -x` |
| Full suite command | `cd firestarter_app && pytest tests/ -x` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| COV-01 | Matrix file exists, enumerates 339 algo-0x07/0x08 rows with the 9 required columns | unit + golden | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_enumeration_row_count -x` | ❌ Wave 0 |
| COV-01 | Sort order: (algo, pinout, size, mfg, first-alias) | unit | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_enumeration_sort -x` | ❌ Wave 0 |
| COV-01 | Codegen idempotence: byte-identical on second run | unit (smoke) | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_idempotence -x` | ❌ Wave 0 |
| COV-02 | Every detected inconsistency cluster appears in §4 with a stable DEFECT-COV-NN id | unit | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_hazard_cluster_42_rows -x` | ❌ Wave 0 |
| COV-02 | Ledger is idempotent (no new IDs minted on identical DB) | unit | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_ledger_idempotent -x` | ❌ Wave 0 |
| COV-02 | Ledger ID persistence (mint-then-rerun reuses same ID) | unit | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_ledger_id_reuse -x` | ❌ Wave 0 |
| COV-01 / COV-02 | DB count drift: matrix's §2 numbers match live DB | regression | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_summary_stats -x` | ❌ Wave 0 |
| D-03 | Exit code 0 on clean run; exit code 1 on `--check` after a new finding emerges | integration (subprocess) | `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py::test_exit_codes -x` | ❌ Wave 0 |
| D-07 | Planning-doc counts match live | manual grep verification | `grep -E '\b(743\|341\|214)\b' .planning/PROJECT.md .planning/ROADMAP.md .planning/REQUIREMENTS.md` returns only the rows explicitly kept as historical | manual-only — automated optional |

### Sampling Rate
- **Per task commit:** `cd firestarter_app && pytest tests/test_audit_coverage_matrix.py -x` (single test file; < 5 s)
- **Per wave merge:** `cd firestarter_app && pytest tests/ -x` (existing 29 tests + new ~8 = ~37 tests; < 30 s)
- **Phase gate:** Full suite green + manual `diff $(./tool --output /tmp/a) <(cat .planning/v1.3-COVERAGE-MATRIX.md)` returns empty before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `firestarter_app/tests/test_audit_coverage_matrix.py` — new file; covers COV-01 + COV-02 + D-03 acceptance
- [ ] No framework install needed (pytest 9.0.3 already present)
- [ ] No conftest changes needed (existing `conftest.py` does not interfere; the new tests are stand-alone and import directly from `tools.audit_coverage_matrix`)

**Golden-file pattern (recommended):**

Once the matrix is regenerated to the operator's satisfaction at the end of Wave 4, copy it to `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` and add:

```python
def test_golden_file_matches(tmp_path):
    from tools.audit_coverage_matrix import generate_matrix
    out = tmp_path / "matrix.md"
    ledger = tmp_path / "ids.json"
    # Seed the ledger from the committed ledger so IDs match
    ledger.write_text(Path(".planning/v1.3-defect-coverage-ids.json").read_text())
    generate_matrix(output=out, ledger_path=ledger)
    golden = Path("tests/golden/v1.3-COVERAGE-MATRIX.md").read_text()
    assert out.read_text() == golden, "regenerated matrix drifted from golden"
```

This is the regression gate that catches DB-regeneration drift cleanly. If a future DB update legitimately shifts a number, the operator regenerates the golden file alongside the matrix — both in one commit.

## Sources

### Primary (HIGH confidence)
- [`firestarter_app/tools/check_dispatch.py`] (lines 17–195) — loader scaffold, env-var pattern, dispatch simulation
- [`firestarter_app/tools/build_db.py`] (lines 1–100 + 380–489) — CLI pattern, override logic, `_etype` re-derivation
- [`firestarter_app/firestarter/database.py`] (lines 34–61 + 157–202) — `EpromDatabase` singleton, `_ALGO_MEM_TYPE` table
- [`firestarter_app/firestarter/data/chip_database.json`] — live DB (scanned 2026-05-19; 734 rows confirmed)
- [`firestarter_app/firestarter/data/pinouts.json`] — `DIP28_28C64`, `DIP28_28C256`, `DIP28_2764` definitions (pin 1 = A14 on 28C256 confirmed)
- [`firestarter_app/CLAUDE.md`] §"Database Pipeline" — WARNING-5 override semantics + the 23-chip-scope reference
- [`.planning/phases/06-logging-infrastructure/06-RESEARCH.md`] (lines 603–625) — codegen idempotence recipe (sort + LF + no timestamps)
- [`.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md`] (lines 232–316) — markdown table style precedent
- [`.planning/milestones/v1.0-MILESTONE-AUDIT.md`] (lines 17–35 + 121–125 + 216–230) — WARNING-5 escalation language for `DEFECT-COV-00` baseline
- [`.planning/phases/11-coverage-matrix-db-inconsistency-audit/11-CONTEXT.md`] — locked decisions D-01 through D-15

### Secondary (MEDIUM confidence)
- pytest 9.0.3 documentation conventions (parametrize, tmp_path) — used in `firestarter_app/tests/test_decoder.py`

### Tertiary (LOW confidence)
- None — every claim in this research is anchored to an in-repo source verified during this session.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every component is stdlib or already-in-repo; no version uncertainty.
- Architecture: HIGH — the architecture is a sibling of two existing tools (`check_dispatch.py`, `build_db.py`) and the patterns are battle-tested.
- Pitfalls: HIGH for #1, #2, #3, #4, #5, #7 (all verified against in-repo sources); MEDIUM for #6 (depends on operator habit).
- Live DB audit: HIGH — every count is the output of a one-pass scan over committed JSON.
- D-13 hash composition: HIGH — sha1 + 16-hex truncation is a well-understood collision-resistance pattern; the signature schema is deterministic.
- D-07 edit plan: HIGH for the 12 LIVE-numeric edits; MEDIUM for the historical-narrative-preservation guidance (operator discretion).

**Research date:** 2026-05-19
**Valid until:** 2026-06-18 (30 days; the DB count is stable until the next `python tools/build_db.py` regeneration or a new minipro upstream xml drop). If `chip_database.json` is regenerated before phase plans land, re-run the live DB audit section (~30 s of scripting) and update the affected counts in §2 and the D-07 edit plan.

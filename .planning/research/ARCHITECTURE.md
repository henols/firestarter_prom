# Architecture Research

**Domain:** EPROM programmer — bench validation milestone (silicon proof + single chip graduation)
**Researched:** 2026-06-23
**Confidence:** HIGH — all claims grounded in live source files verified at path and line level on the current gsd/v1.14 branch

---

## Standard Architecture

### System Overview

```
HOST (Python CLI — firestarter_app/)
  ┌─────────────────────────────────────────────────────────────────────┐
  │  ~/.firestarter/database.json    chip_database.json                 │
  │  (user-override, 2516 entry)  ← merged by EpromDatabase.__init__() │
  │         ↓ _merge_databases()                                        │
  │  database.py EpromDatabase                                          │
  │  get_eprom_config(name) → raw config (support_status read here)    │
  │                  ↓                                                  │
  │  chip_resolver.py resolve_chip()                                    │
  │  support_status == "supported"?                                     │
  │    YES → convert_to_programmer() → wire dict (flags, vpp_mv, algo) │
  │    NO  → raise ChipNotImplementedError (BEFORE any serial byte)    │
  │                  ↓                                                  │
  │  eprom_operations.py write_cycle_eprom / consistency_check_eprom   │
  │  (compose write→read→verify; called by dev validate-family)        │
  │                  ↓                                                  │
  │  serial_comm.py COBS+CRC8 JSON frame                                │
  └──────────────────────────┬──────────────────────────────────────────┘
                             │ JSON over COBS+CRC8 at 250000 baud
  ┌──────────────────────────▼──────────────────────────────────────────┐
  │  FIRMWARE (C++ — firestarter/) — Leonardo + RURP Rev 2.0           │
  │  memory.cpp configure_memory()                                      │
  │  protocol → configure_eprom (0x07/0x08/0x0B including 2516→0x0B)  │
  │          → configure_flash3 (0x06 SST39SF040)                      │
  │          → configure_flash4 (0x05 W29C020/W29C040)                 │
  │          → configure_sram   (0x0E/0x27/0x28/0x29 FM1608)           │
  │  [generic fail-closed: protocol != 0 → configure_not_implemented]  │
  └──────────────────────────────────────────────────────────────────────┘

  GATES (run after every code change)
  ┌──────────────────────────────────────────────────────────────────────┐
  │  tools/check_dispatch.py — mirrors memory.cpp dispatch in Python;   │
  │    asserts all 744 chips reach correct handler; VPP invariants hold  │
  │  tools/diff_db.py — every DB change cited against a root-cause rule  │
  │  pytest --cov-fail-under=70 — host test suite + coverage floor      │
  │  pio test -e native — firmware Unity test suites                    │
  └──────────────────────────────────────────────────────────────────────┘

  BENCH EVIDENCE RECORD (v1.15 NEW artifact — per chip, per session)
  ┌──────────────────────────────────────────────────────────────────────┐
  │  .planning/v1.15/bench/EVIDENCE.md + EVIDENCE.json                  │
  │  columns: chip | family | board/shield | blank_state | op | SHA     │
  │           verdict | anomalies                                        │
  │                                                                      │
  │  Populated by: write_test.sh or dev validate-family --output-dir    │
  │  The v1.13 validation-matrix.{json,md} artifact is EXTENDED with    │
  │  per-chip rows (one row per chip, not per family) and lives          │
  │  separately from the family-level matrix in tools/.                  │
  └──────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | File |
|-----------|---------------|------|
| `EpromDatabase` | Loads and merges `chip_database.json` + `~/.firestarter/database.json`; provides `get_eprom_config`, `_map_data`, `convert_to_programmer` | `firestarter_app/firestarter/database.py` |
| `chip_resolver.resolve_chip` | Single chokepoint; reads `support_status` from raw config BEFORE building any wire dict; raises `ChipNotImplementedError` for non-`supported` chips | `firestarter_app/firestarter/chip_resolver.py` |
| `eprom_operations.write_cycle_eprom` | Composes write→read→verify cycle; called by `dev validate-family` and `write_test.sh`; returns 0=PASS, 1=FAIL, 2=hw-error | `firestarter_app/firestarter/eprom_operations.py` |
| `dev validate-family` | Tier-3 HIL runner; r1 precondition gate; emits `validation-matrix.{json,md}`; authoritative PASS only on Leonardo | `firestarter_app/firestarter/cli_handlers.py` lines 1259–1593 |
| `validation_matrix_spec.json` | Authored spec: 6 families, rep_chip per family, boards/skip_boards per tier | `firestarter_app/tools/validation_matrix_spec.json` |
| `memory.cpp configure_memory` | Firmware dispatch hub; protocol-prefix if-return chain; fail-closed `protocol != 0` guard | `firestarter/src/proms/memory.cpp` |
| `check_dispatch.py` | CI correctness gate: mirrors `memory.cpp` dispatch; asserts every DB chip → correct handler; VPP invariants; D-10 consistency | `firestarter_app/tools/check_dispatch.py` |
| `diff_db.py` | Per-chip diff gate: flags any DB change not cited by a root-cause rule against the pinned baseline | `firestarter_app/tools/diff_db.py` |
| `build_db.py` | Sole DB classification authority; produces `support_status`, `algorithm`, `vpp_mv`, `pinout`, `unsupported_reason` | `firestarter_app/tools/build_db.py` |
| `~/.firestarter/database.json` | User-override DB; merged on top of the generated DB by `EpromDatabase._merge_databases()`; NOT processed by `build_db.py` or guarded by `check_dispatch.py`/`diff_db.py` | operator-managed file |

---

## Question 1: Matrix Integration and Per-Chip Evidence Record

### Where the v1.13 Matrix Lives and Its Schema

The v1.13 validation matrix is a two-file artifact:

- **Spec (authored, static):** `firestarter_app/tools/validation_matrix_spec.json` — defines 6 families, each with a `rep_chip`, tier1/tier2/tier3 descriptions, `boards`, and `skip_boards`. Schema version 1. This spec is NOT modified per chip; it defines the family-level structure.

- **Results (generated, per-run):** `validation-matrix.json` and `validation-matrix.md` written to `--output-dir` by `dev validate-family`. Cell schema:

```json
{
  "family": "eprom",
  "board": "leonardo",
  "tier": 3,
  "verdict": "PASS",
  "pass_type": "authoritative",
  "evidence_sha": "<sha256 of source image>",
  "retry_count": 1
}
```

The `pass_type` field distinguishes authoritative (Leonardo) from advisory (other boards). The `evidence_sha` is the SHA256 of the **source image written** — not the readback, which is compared internally by `write_cycle_eprom`.

### How Per-Chip Results Get Recorded

`dev validate-family` records one cell per family per board. For v1.15, this is per-family (not per-chip within a family). The 11-chip inventory spans 6 families but multiple chips per family — e.g., W27C512 / W27E512 / SST27SF512 / ST M27C512 all map to `eprom` family (0x07/0x08).

**The gap:** The existing matrix records one row per family, using the `rep_chip`. It does not record individual results for W27E512 vs SST27SF512 vs ST M27C512 separately — only the family's representative chip (W27C512) gets a row.

**The v1.15 extension:** The per-chip evidence record is a **separate artifact** that augments the family-level matrix. It is not a replacement. Concretely:

- The **family-level** `validation-matrix.{json,md}` is produced by `dev validate-family` as before (one row per family, rep_chip only). Already exists from v1.13 for the `eprom` family.
- The **per-chip** evidence record is a new `.planning/v1.15/bench/EVIDENCE.md` (and companion `EVIDENCE.json`) written manually or semi-automatically by the bench executor during each session.

### Proposed Per-Chip Evidence Record Format

**EVIDENCE.json schema (one record per chip per bench session):**

```json
{
  "schema_version": 1,
  "milestone": "v1.15",
  "generated": "2026-06-XX T...",
  "records": [
    {
      "chip": "W27C512",
      "family": "eprom",
      "board": "leonardo",
      "shield": "Rev 2.0",
      "blank_state": "pre-erased",
      "op": "write+verify",
      "sha": "<sha256 of written image>",
      "verdict": "PASS",
      "anomalies": ""
    },
    {
      "chip": "2516",
      "family": "eprom_legacy",
      "board": "leonardo",
      "shield": "Rev 2.0",
      "blank_state": "blank (confirmed)",
      "op": "read+blank_check",
      "sha": "N/A (read only)",
      "verdict": "PASS",
      "anomalies": "VPE rail 22.4V (under-voltage warning from FW; proceeded best-effort)"
    }
  ]
}
```

**EVIDENCE.md — rendered Markdown table (same data):**

| Chip | Family | Board/Shield | Blank State | Op | SHA (first 16) | Verdict | Anomalies |
|------|--------|-------------|------------|-----|----------------|---------|-----------|
| W27C512 | eprom (0x07) | leonardo/Rev 2.0 | pre-erased | write+verify | `abcd1234...` | PASS | — |
| W27E512 | eprom (0x07) | leonardo/Rev 2.0 | auto-erased | write+verify | `efgh5678...` | PASS | — |
| 2516 | eprom_legacy (0x0B) | leonardo/Rev 2.0 | blank | read+blank_check | N/A | PASS | under-voltage warn |

**Column definitions:**

- **chip** — canonical part_number (matches DB lookup key)
- **family** — algorithm family id matching `validation_matrix_spec.json` + protocol hex in parens
- **board/shield** — `leonardo/Rev 2.0` (fixed for this milestone)
- **blank_state** — `blank (confirmed)`, `pre-erased (auto)`, `pre-erased (UV)`, `unknown (AND-mask write)`, `non-blank (skipped destructive)`
- **op** — `read+blank_check`, `write+verify`, `and_mask_write+verify`, `read_only`
- **sha** — SHA256 of the written image (from `write_test.sh` output or `evidence_sha` from `dev validate-family`); `N/A` for read-only ops
- **verdict** — `PASS`, `FAIL`, `SKIP-deferred`, `PARTIAL` (if AND-mask proof only)
- **anomalies** — firmware warnings, retry count, DB decode mismatches observed, anything deviating from expected behavior

**Relationship to the family-level matrix:** The per-chip EVIDENCE record is complementary. The family-level matrix proves the algorithm family is correctly implemented. The per-chip EVIDENCE record proves individual silicon samples match the DB (pinout, VPP, size, electrical type). Reference the family-level matrix row from EVIDENCE.md via a note column or header comment.

---

## Question 2: 2516 User-Override Flow

### Where the 2516 Entry Lives

The 2516 (Intel/vintage 24-pin NMOS EPROM, 2K×8, 25V VPP) is **absent from minipro's `infoic.xml`** — confirmed: the 28 `2516` hits in the XML are all `25160` SPI serial parts, not parallel DIP EPROMs. Therefore:

- `chip_database.json` (generated by `build_db.py` from `infoic.xml`) contains NO `2516` entry.
- The entry must live in `~/.firestarter/database.json` as a user-override.

### How User-Override Entries Flow Through the Stack

**Step 1 — Load and merge** (`database.py` lines 200–251):

```python
# EpromDatabase._initialize_database_core()
self.proms = _read_config_file("chip_database.json")   # base DB

if not skip_local_override:
    local_db = get_local_database()                     # ~/.firestarter/database.json
    if local_db:
        self.proms = self._merge_databases(self.proms, local_db)
```

`_merge_databases` iterates `local_db` keys (manufacturers). For a new manufacturer key not in the base DB, the entire list is appended. For an existing key, it matches on `part_number` and updates fields, or appends the new entry if the name is absent. **Result:** the 2516 entry is indistinguishable from a built-in entry after merge.

**Step 2 — Lookup** (`database.py` lines 492–531, `get_eprom_config`):

Searches `self.proms` — the merged dict — by `part_number` exact match and comma-separated alias match. The 2516 entry is found identically to any DB chip.

**Step 3 — Support status guard** (`chip_resolver.py` lines 43–57):

```python
raw_config, _ = db.get_eprom_config(name)         # finds 2516 in merged proms
support_status = raw_config.get("support_status", "supported")
if support_status != "supported":
    raise ChipNotImplementedError(...)
```

The user-override entry must include `"support_status": "supported"`. If absent, the field defaults to `"supported"` (line 54: `raw_config.get("support_status", "supported")`). So a minimal override entry without `support_status` passes the guard as `supported` by default.

**Step 4 — Wire dict construction** (`database.py` `_map_data` + `convert_to_programmer`):

`_map_data` reads `electrical.pin_count`, `programming.algorithm`, `electrical.vpp_mv`, and the `pinout` key. It derives `determined_type` from `_ALGO_MEM_TYPE[protocol_id]` — for `0x0B` this gives `mem_type=1` (TYPE_EPROM). `convert_to_programmer` builds the wire dict including `algorithm: 0x0B` and `vpp_mv: 25000`.

**Step 5 — Dispatch** (`memory.cpp`):

Protocol `0x0B` hits the arm `if (protocol in 0x07, 0x08, 0x0B) → configure_eprom()`. This is the 2716-family (EPROM_LEGACY) handler. The 2516 is electrically compatible with the 2716 protocol — same DIP24 pinout, same VPP class, same pulse structure.

### Minimum Valid 2516 User-Override Entry

```json
{
  "INTEL": [
    {
      "part_number": "2516",
      "support_status": "supported",
      "pinout": "DIP24_2716",
      "electrical": {
        "type": "UV-EPROM",
        "pin_count": 24,
        "size_bytes": 2048,
        "vcc": "5V",
        "vpp": "25V",
        "vpp_mv": 25000
      },
      "programming": {
        "algorithm": 11,
        "pulse_duration": "50000 us",
        "chip_id_check": false
      }
    }
  ]
}
```

Notes on the entry:
- `"algorithm": 11` is `0x0B` decimal — EPROM_LEGACY, the 2716-family path.
- `"pinout": "DIP24_2716"` — this key must exist in `pinouts.json`. Verify it does: `pinouts.json` has a `DIP24_2716` entry (per v1.11 `resolve_pinout_key` rebuild). If it uses `DIP24_2816` instead, check which key is correct for 24-pin 25V NMOS.
- `"electrical.type": "UV-EPROM"` — NOT `"EEPROM"` and NOT `"Flash/EEPROM"`. This prevents `convert_to_programmer` from setting `FLAG_CAN_ERASE` (line 605: `if ... in ("EEPROM", "Flash/EEPROM")`), which is correct — UV EPROMs are NOT electrically erasable.
- `"pulse_duration": "50000 us"` — 50 ms, the long-pulse EPROM_LEGACY spec. The `_parse_pulse_duration` helper parses this format.
- `"chip_id_check": false` — the 2516 has no software-readable chip ID.
- `"vpp_mv": 25000` — uses the raised ceiling (22000→25000 from Phase 79 NMOS-02).

### Safety Constraint: check_dispatch.py and diff_db.py Do NOT Cover User-Overrides

This is a critical safety caveat: `check_dispatch.py` loads `chip_database.json` directly (lines 24–33 set `DB_FILE`). It does NOT load or merge `~/.firestarter/database.json`. Similarly, `diff_db.py` compares against the pinned `chip_database.baseline.json`. The 2516 entry bypasses both gates entirely.

**Manual safety review required:**

1. Confirm `algorithm: 0x0B` routes to `configure_eprom` — it does (check_dispatch.py line 143: `if protocol in (0x07, 0x08, 0x0B): return "configure_eprom"`).
2. Confirm `vpp_mv: 25000` is within the `configure_eprom` invariant: `(0, 25000)` (inclusive upper bound per Phase 79 raise). 25000 ≤ 25000 — passes.
3. Confirm `FLAG_CAN_ERASE` is NOT set (electrical.type = UV-EPROM → not in `("EEPROM", "Flash/EEPROM")`).
4. Confirm `DIP24_2716` pinout routes VPP correctly for 24-pin chips on the RURP socket (verify pin_conversions[24] mapping in database.py lines 80–97).
5. Bench-verify on the ~22.4V VPE rail (0x0B hardwired to VPE-only path, same as M2716 graduated in Phase 79).

---

## Question 3: Build Order for Phases

### Recommended Phase Order

```
Phase 81: 2516 DB Entry + Initial Read Sweep (non-destructive, all 11 chips)
Phase 82: EE-EPROM Silicon Validation (8 chips, write+verify, destructive OK)
Phase 83: UV-EPROM Write Proof (3 chips, spend-vs-preserve decided per chip)
Phase 84: DB Decode Correctness Audit + Defect RCA (conditional)
```

**Rationale:**

**Phase 81 (2516 DB entry + non-destructive sweep) — do first:**

The 2516 is the milestone's only graduation candidate and the one genuine software deliverable. Author the `~/.firestarter/database.json` entry first so `firestarter info 2516` works and the read path is exercisable. Then run a non-destructive read sweep across all 11 chips: `firestarter read <chip> -o /dev/null` (or `blank_check`) — this validates the read path, DB decode (pinout, size, VPP), and controller identity for every chip with zero destructive risk. UV-EPROMs survive this session regardless of whether they are blank or programmed.

This session answers two questions cheaply: (a) does the DB entry produce a valid wire dict and connect to the chip? (b) is each UV-EPROM blank or programmed? The blank-state discovery gates the Phase 83 decision tree.

**Phase 82 (EE-EPROM silicon validation) — second:**

The 8 electrically-erasable chips (W27C512, W27E512, SST27SF512, W27E040, SST39SF040, W29C020, W29C040, FM1608) can be written and re-written without constraint. Validate each one via `write_test.sh` or `dev validate-family`. Prior bench evidence exists for W27C512 (Phase 77), SST39SF040 + W29C040 (Phase 74), FM1608 (Phase 73) — those can re-run as confirmation or be cited directly from prior evidence. New chips are W27E512, SST27SF512, W27E040, W29C020.

**Phase 83 (UV-EPROM write proof) — third, gated on Phase 81 blank-state:**

The 3 UV-EPROMs (ST M27C512, AM27C020, 2516) require an eraser to recycle. Since the operator has none, the Phase 81 blank-state discovery determines the op:
- **Chip confirmed blank:** run full write→verify (spends the chip, non-recoverable without UV eraser).
- **Chip programmed:** run AND-mask write — write a 0x00 pattern (or any byte that only clears 1→0 bits relative to the existing content) and verify it. This proves the write path works without requiring a blank start.

The spend-vs-preserve decision is made live at the bench, per chip, after the Phase 81 blank-state result is known. This is why Phase 83 cannot run concurrently with Phase 81.

The 2516 graduation (FUT-03 NMOS write+SHA) is the primary target of Phase 83.

**Phase 84 (DB decode correctness + conditional defect RCA) — fourth:**

Any mismatch between observed silicon behavior and DB declarations (wrong size, wrong VPP, wrong algorithm response) is root-caused and fixed here. If Phases 82–83 produce clean PASSes with no anomalies, Phase 84 is a documentation pass only. If a family fails, Phase 84 is a firmware/host fix in the established lockstep pattern.

### New vs Modified Components Per Phase

| Phase | New Components | Modified Components | Notes |
|-------|---------------|---------------------|-------|
| 81 | `~/.firestarter/database.json` (2516 entry) | None | Host-only; no code change; user-override; bypasses check_dispatch/diff_db |
| 82 | `.planning/v1.15/bench/EVIDENCE.{md,json}` | None (software exists) | Reuse `write_test.sh` / `dev validate-family`; update evidence record per chip |
| 83 | EVIDENCE.{md,json} rows for UV chips | None unless write fails | If write fails: fix in `eprom_operations.py` or firmware (lockstep if wire-level) |
| 84 | None | `build_db.py` (if DB decode wrong), firmware (if algorithm bug) | Conditional — only if bench surfaces a defect |

---

## Question 4: Bench-Session Integration Points

### R1/R2 Live Readback Precondition

**Gate:** `r1 ≈ 270000 ± 25%` (range 202500–337500).

**Source:** `dev validate-family` checks this in `_check_r1_precondition` (cli_handlers.py lines 1413–1416). If `r1_raw` is outside the band, it calls `sys.exit(2)` before any write cycle.

**How to arm:** `firestarter config -r1` writes to Arduino EEPROM. The CLI reads back the live value via hardware config. The `r1=270000` value is persisted in `~/.firestarter/config.json` after the Phase 73 calibration session (per STATE.md: `firestarter config -r1 writes to Arduino EEPROM only; r1 gate armed by writing r1=270000 directly to ~/.firestarter/config.json`).

**At each task start:** Run `firestarter info <chip>` or `firestarter dev reg 0 0 0 -r` as a quick live-readback before any VPP-dependent operation. This confirms R1 hasn't been reset (EEPROM is non-volatile but can be factory-reset).

### Controller Port Identity Check

**Gate:** Verify `controller:` in the firmware handshake output matches `leonardo` on the expected port before each task.

**Why:** `/dev/ttyACM*` numbers shuffle after any USB unplug/replug. Trusting a session-start port mapping across a shield swap or board cycle risks driving the wrong board (per `feedback_verify_port_identity_each_task` memory).

**How:** `firestarter info <any chip>` prints the controller identity from the handshake. Or `firestarter dev read <chip> -o /dev/null` — the handshake fires on connect. Confirm `"controller": "leonardo"` in the output before proceeding with any write cycle.

**In phases:** Every bench plan that opens a serial connection must include a port-identity verification as step 1.

### Leonardo Chip-OUT Sideload Exemption

**Rule:** Leonardo does NOT require chip removal before sideloading firmware. Only Uno-class boards (Uno, uno328pb) need chip-out before sideload because their USB-serial bridge drives the shield bus during the upload sequence.

**Source:** `feedback_chip_out_before_sideload` memory: "chip OUT before sideload — Uno-class ONLY (Uno + uno328pb); Leonardo EXEMPT". Also per `reference_vpp_vpe_no_socket_routing`: `hw_read_voltage` enables the regulator + measures only; no A9/VPE/P1 routing bits.

**Practical implication for v1.15:** During bench sessions, re-flashing or updating firmware on Leonardo does not require removing the chip. This saves considerable time when iterating on a firmware fix for a family failure.

### VPE Rail for NMOS (2516 and graduated NMOS chips)

**Rail value:** VPE = 22.4V DMM / 23.9V firmware `firestarter vpe` (per Phase 79-01 corrected reading). This is ~90% of the 25V nominal spec.

**Which rail:** The `0x0B` EPROM_LEGACY handler uses `CTRL_VPP_REGULATOR_ENABLE` (0x80) only — this is the direct VPE path (no VPE→VPP dropping resistor engaged). The firmware's `eprom_check_vpp` validates the ADC reading against `handle->vpp_mv` (25000) and emits an under-voltage warning (22.4V < 23.75V = 95% threshold) but proceeds. Over-voltage is still blocked.

**For the 2516 bench session:** The chip programs (or attempts to program) on the ~22.4V VPE rail. The firmware warning is expected and informational. A clean SHA-match after write+verify is the definitive proof regardless of the warning.

**VPP monitor gotcha:** `firestarter vpp` reads the DROPPED rail (0x07/0x08 path via VPE→VPP drop) — this reports ~15–19V, NOT the VPE rail. For NMOS/0x0B chips, always use `firestarter vpe` to read the programming rail (per Phase 79-01 rail correction, operator-confirmed 2026-06-23).

**Hold-rail for DMM:** `firestarter dev reg 0 0 0x86 -f` holds the erase/VPE rail on for DMM measurement (per `reference_v114_bench_erase_rail_and_test_artifact`).

---

## Data Flow

### 2516 Entry → Wire Dict → Dispatch

```
~/.firestarter/database.json
  └── {"INTEL": [{"part_number": "2516", "algorithm": 11, ...}]}
      ↓ EpromDatabase._merge_databases()
      merged self.proms["INTEL"] (appended)
      ↓ get_eprom_config("2516")
      raw_config (support_status defaults to "supported")
      ↓ chip_resolver.resolve_chip("2516")
      support_status == "supported" → proceed
      ↓ get_eprom("2516") → _map_data()
      determined_type = _ALGO_MEM_TYPE[0x0B] = 1 (TYPE_EPROM)
      info_flags: electrical.type="UV-EPROM" → NOT in ("EEPROM","Flash/EEPROM") → 0x10 NOT set
      ↓ convert_to_programmer()
      FLAGS: electrical-type="UV-EPROM" → FLAG_CAN_ERASE NOT set → flags=0
      wire dict: {algorithm: 11, vpp_mv: 25000, type: 1, flags: 0, pin-count: 24,
                  memory-size: 2048, bus-config: <DIP24_2716 mapping>}
      ↓ serial_comm.py COBS+CRC8 JSON frame → Leonardo
      ↓ memory.cpp: protocol=0x0B → configure_eprom() → EPROM_LEGACY path
      VPE rail (~22.4V) used; firmware warns under-voltage; proceeds
```

### Non-Destructive Read Sweep (Phase 81)

```
For each of 11 chips:
  firestarter read <chip> -o /tmp/<chip>.bin
    → chip_resolver validates support_status (2516 via user-override)
    → wire dict with cmd=READ (no VPP engagement on read for most families)
    → firmware reads memory, streams binary via COBS
    → host saves binary
  firestarter blank-check <chip>
    → reads and checks for 0xFF fill
    → records blank_state in EVIDENCE.md
```

### Write+Verify Cycle (Phase 82 / 83)

```
write_test.sh <chip>   (or dev validate-family --chip <chip> --board leonardo ...)
  → write_cycle_eprom(chip, eprom_data, source_image_path=<test_bin>, runs=1)
      → firestarter write <chip> <image>
          → erase first (FLAG_CAN_ERASE set for EE-EPROMs) → program → done
      → firestarter read <chip> -o <readback>
      → sha256(<image>) == sha256(<readback>)?
          YES → verdict=PASS (authoritative on Leonardo)
          NO  → verdict=FAIL → escalate to Phase 84
  → record row in EVIDENCE.{md,json}
```

---

## Architectural Patterns

### Pattern 1: Non-Destructive-First Safety Ordering

**What:** Run reads and blank-checks before any write. For UV-EPROMs, make the spend-vs-preserve decision based on observed blank state, never based on assumption.

**When to use:** Any bench session touching UV-EPROMs (M27C512, AM27C020, 2516). The operator has no eraser — a write to a non-blank UV-EPROM produces a chip in an unknown state that cannot be recovered.

**Trade-offs:** Adds one bench session (Phase 81) before any writes. Prevents irreversible chip loss.

**Rule:** Blank-check every UV-EPROM in Phase 81. Record result in `blank_state` column of EVIDENCE.md. Only proceed to write in Phase 83 after the blank_state field is populated.

### Pattern 2: User-Override Entry for Chips Absent from minipro

**What:** Author a `~/.firestarter/database.json` entry that mirrors the chip_database.json schema fields needed by `_map_data` and `convert_to_programmer`. The merged DB is indistinguishable from a built-in entry to all downstream code.

**When to use:** Any chip absent from minipro `infoic.xml` (confirmed absent, not merely missing from the RURP subset). Only the 2516 in v1.15 scope.

**Critical fields:** `part_number`, `pinout` (must match an existing key in `pinouts.json`), `electrical.pin_count`, `electrical.size_bytes`, `electrical.vpp_mv`, `programming.algorithm` (integer, not hex string), `programming.pulse_duration` (format: `"50000 us"`), `support_status` (defaults to `"supported"` if absent).

**Safety caveat:** User-override entries bypass `check_dispatch.py` and `diff_db.py`. All safety properties must be manually verified as listed in Question 2 above.

### Pattern 3: Evidence Record Extends, Not Replaces, the Family Matrix

**What:** The `validation-matrix.{json,md}` produced by `dev validate-family` records per-family results using the rep_chip. The `EVIDENCE.{md,json}` in `.planning/v1.15/bench/` records per-chip results for every chip in the inventory.

**When to use:** Always in v1.15. The family matrix is the harness output (generated). The EVIDENCE record is the milestone artifact (curated, one row per physical chip exercised).

**How they relate:** EVIDENCE.md references the family-level matrix result. Where `dev validate-family` was run for a family, cite the generated `validation-matrix.md` as the authoritative source. The EVIDENCE row for the rep_chip is the same result (PASS/FAIL/SHA); non-rep chips in the same family get their own EVIDENCE rows but do NOT get family-matrix rows.

### Pattern 4: Guard-Removal-Last Discipline (from SAFE-01/02/03, v1.14 Phase 77)

**What:** When graduating a chip to `supported`, the `support_status` change in `build_db.py` (or user-override entry set to `"supported"`) is the FINAL step, after: native recording-stub tests pass, host wire round-trip passes, and bench write+verify SHA-match proves the chip programs correctly.

**When to use:** The 2516 graduation only (other 10 chips are already `support_status: supported` in the DB). Do not set `"support_status": "supported"` in the user-override entry until the read sweep (Phase 81) confirms the chip is reachable and the pinout/VPP decode is correct.

**Practical sequence:** Author the entry with `"support_status": "needs-validation"` initially (which will raise `ChipNotImplementedError` via the guard) — OR start with `"supported"` since the entry is in `~/.firestarter/database.json` (local only, no CI gate). The choice is pragmatic: for a user-override, setting `"supported"` from the start and verifying during Phase 81 read sweep is cleaner.

---

## Anti-Patterns

### Anti-Pattern 1: Trusting Port Identity Without Verifying

**What people do:** Assume `/dev/ttyACM0` is Leonardo throughout a multi-chip bench session because it was Leonardo at session start.

**Why it's wrong:** USB ACM numbers shuffle on any unplug/replug. A shield swap, cable bump, or devcontainer reconnect can silently reassign ports. Writing to the wrong board or driving the wrong shield is a hardware-damage path.

**Do this instead:** Run `firestarter info <any_chip>` at the start of each bench task and confirm `"controller": "leonardo"` before any write cycle.

### Anti-Pattern 2: Running AND-Mask Write Without Confirming Current Content

**What people do:** Attempt an AND-mask write (0x00-fill) to a UV-EPROM without first reading the current content to determine which bits are already 0.

**Why it's wrong:** An AND-mask write (`flags & 0x00 = 0x00`) always writes 0xFF→0x00 transitions, but a chip that's already partially written may have mixed content. The write proves the write path works on 1→0 transitions regardless — but the verify is against the written image, not the original. This is still valid as a bench proof; the issue is documentation: record `blank_state` and `op` accurately in EVIDENCE.md.

**Do this instead:** Read the chip first (Phase 81). If non-blank, decide on AND-mask write with a known test pattern (e.g., all-0x00). Record `blank_state: "non-blank (see read SHA)"` and `op: "and_mask_write (0x00 fill)"` in EVIDENCE.md.

### Anti-Pattern 3: Editing chip_database.json by Hand for the 2516

**What people do:** Add the 2516 directly to `firestarter_app/firestarter/data/chip_database.json`.

**Why it's wrong:** `chip_database.json` is a generated artifact overwritten by `python tools/build_db.py`. The 2516 is absent from `infoic.xml` so `build_db.py` will never emit it. Any hand edit is silently lost on the next `build_db.py` run. Additionally, adding it to the generated file triggers `diff_db.py` failures (unexplained chip).

**Do this instead:** The entry belongs exclusively in `~/.firestarter/database.json`. This is the correct operator-override path for chips absent from the upstream source. Document the entry schema clearly so it can be reproduced after a clean install.

### Anti-Pattern 4: Using `firestarter vpp` to Read the NMOS Programming Rail

**What people do:** Run `firestarter vpp` to measure the VPP rail during a 2516/NMOS (0x0B) bench session and interpret the result as the programming voltage.

**Why it's wrong:** `firestarter vpp` forces the DROPPED path (hardware_operations.cpp:28 — `0x07`/`0x08` style with VPE→VPP resistor drop). For `0x0B` chips, the programming rail is VPE (direct regulator output, no drop). `firestarter vpp` will report ~15–19V (the VPE→VPP dropped value), which is NOT the voltage reaching the chip's VPP pin on the 0x0B path.

**Do this instead:** Use `firestarter vpe` to read the NMOS programming rail. This was corrected in Phase 79-01 (rail correction, operator-confirmed 2026-06-23). Expected reading: ~22.4V DMM / 23.9V firmware.

---

## Integration Check Gates

Every code or DB change in v1.15 must pass:

| Gate | Command | What It Catches |
|------|---------|-----------------|
| Host tests + coverage | `pytest --cov-fail-under=70` | Regression in chip resolution, wire-dict emission |
| Dispatch gate | `python tools/check_dispatch.py` | DB/dispatch mismatch, VPP invariant violations |
| Diff gate | `python tools/diff_db.py` | Unexplained DB changes vs baseline |
| Ruff + mypy | `ruff check . && ruff format --check && mypy ...` | Code quality on 8 strict modules |
| Firmware tests | `pio test -e native` | Firmware dispatch regressions (only if firmware is touched) |
| Flash ceiling | `pio run -e leonardo` ≤ ~90% | New firmware code exceeds budget (only if firmware is touched) |

**User-override safety (manual, no CI gate):** For the `~/.firestarter/database.json` 2516 entry specifically, run the manual checks listed in Question 2 before any bench write attempt.

---

## Sources

- `firestarter_app/firestarter/chip_resolver.py` lines 16–63 — `resolve_chip`, support_status guard, skip_local_override seam (source-verified 2026-06-23)
- `firestarter_app/firestarter/database.py` lines 194–251 — `EpromDatabase.__init__`, `_initialize_database_core`, `_merge_databases` (source-verified 2026-06-23)
- `firestarter_app/firestarter/database.py` lines 385–609 — `_map_data`, `info_flags` derivation, `convert_to_programmer`, `FLAG_CAN_ERASE` path (source-verified 2026-06-23)
- `firestarter_app/firestarter/config.py` lines 15–37 — `HOME_PATH`, `DATABASE_FILE` = `~/.firestarter/database.json`, `get_local_database()` (source-verified 2026-06-23)
- `firestarter_app/firestarter/cli_handlers.py` lines 1259–1593 — `dev validate-family`, r1 precondition, validation-matrix artifact schema (source-verified 2026-06-23)
- `firestarter_app/tools/validation_matrix_spec.json` full — 6 families, rep_chip per family, tier3 boards/skip_boards (source-verified 2026-06-23)
- `firestarter_app/tools/check_dispatch.py` lines 1–158 — KNOWN_PROTOCOLS, `dispatch()`, `_FAMILY_VPP_INVARIANTS` including `configure_eprom: (0, 25000)` post-Phase 79 (source-verified 2026-06-23)
- `.planning/PROJECT.md` §v1.15 — milestone goals, UV-EPROM protocol, 2516 graduation target, bench constraints (source-verified 2026-06-23)
- `.planning/STATE.md` — r1 gate arming, standing bench preconditions, FUT-03 NMOS bench SHA (source-verified 2026-06-23)
- `.planning/MILESTONES.md` §v1.13 — three-tier harness description, per-family matrix, non-vacuous PASS oracle (source-verified 2026-06-23)
- `.planning/MILESTONES.md` §v1.14 — Phase 79 NMOS VPE rail readings, rail correction (22.4V DMM / 23.9V fw), FLAG_CAN_ERASE graduation (source-verified 2026-06-23)
- `.planning/research/_archive-pre-v1.15/ARCHITECTURE.md` — dispatch diagram, component table, refused-to-supported path, check_dispatch mirror requirement (source-verified 2026-06-23, reused where accurate)
- Project memory: `reference_vpp_vpe_no_socket_routing`, `feedback_chip_out_before_sideload`, `feedback_verify_port_identity_each_task`, `project_phase79_gate_reexamined`, `reference_v114_bench_erase_rail_and_test_artifact`

---
*Architecture research for: Firestarter v1.15 Bench Validation of Operator Inventory*
*Researched: 2026-06-23*

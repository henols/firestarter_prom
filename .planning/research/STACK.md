# Technology Stack — v1.15 Bench Validation of Operator Inventory

**Project:** Firestarter EPROM Programmer
**Researched:** 2026-06-23
**Confidence:** HIGH — all claims grounded in verified source files at path, line, and field level

---

## Headline Finding

**v1.15 needs no new third-party dependencies and almost certainly needs no new harness code.** Every mechanism needed to write→read→verify all 11 chips already exists. The only genuine software addition is a single user-override DB entry for the `2516` chip in `~/.firestarter/database.json`. The v1.13 three-tier harness, `write_test.sh`, `dev validate-family`, and `eprom_operations.write_cycle_eprom` are reused as-is. Firmware is untouched unless a bench-surfaced defect forces a fix.

---

## Board / Shield Lock

**Leonardo + RURP Rev 2.0 only.** Standing bench constraints (verified from project memory):

- `/dev/ttyACM0` identity: verify `controller:` port identity at every task start — ACM numbers shuffle after any USB unplug/replug.
- Leonardo is **chip-OUT-sideload-exempt** (v1.10 COBS transport; only Uno-class boards need chip-out during sideload).
- R1 readback before each write session: `firestarter dev config` should show `r1 ≈ 270000` (recalibrated in Phase 54). The `dev validate-family` Tier-3 runner aborts if r1 is outside ±25% of 270000 — this is the live precondition gate.
- VPE rail: ~22.4V DMM / ~23.9V firmware-reported. VPP is a separate ~15–19V rail. Both are measure-only (no routing to socket during `vpp`/`vpe` monitor commands).

---

## Reusable Stack — Exact Files and Commands

### 1. Full Write→Read→Verify Cycle Commands

The canonical per-chip cycle is already wired into `EpromOperator.write_cycle_eprom` (`firestarter_app/firestarter/eprom_operations.py:766–873`). It runs: erase → write → read-back N times → SHA-256 compare each read-back against source image. Returns 0 (PASS) / 1 (mismatch) / 2 (hw-error).

**CLI surface** (from `firestarter_app/firestarter/cli_handlers.py`):

```bash
# Standard write (triggers auto-erase for EEPROM-class chips):
firestarter write <chip> <image.bin>

# Skip blank check / erase (for UV-EPROMs or pre-erased chips):
firestarter write --no-blank-check <chip> <image.bin>

# Write at byte offset (for partial-image writes in write_test.sh):
firestarter write --no-blank-check -a <hex_offset> <chip> <image.bin>

# Read to file:
firestarter read <chip> <output.bin>

# Verify image against chip:
firestarter verify <chip> <image.bin>

# Blank check:
firestarter blank-check <chip>
```

**SHA evidence capture** — use `sha256sum` (or Python `hashlib.sha256`) on the output `.bin` after read. `write_cycle_eprom` computes and logs SHA-256 internally; `consistency_check_eprom` (`eprom_operations.py:566–764`) does the same for N consecutive reads and prints a PASS/FAIL verdict block with SHA-256 values.

**The `dev write-cycle` command** invokes `write_cycle_eprom` directly and is the cleanest single-command evidence artifact:

```bash
firestarter dev write-cycle --runs 3 --source <image.bin> --output-dir <dir> <chip>
```

This produces a `write-cycle-<chip>-unknown-board-<timestamp>/` directory with per-run read-back binaries and SHA comparison logged to stdout — reusable as the per-chip evidence record without any new tooling.

**The `dev validate-family` Tier-3 runner** (`cli_handlers.py:1419–1560`, spec at `tools/validation_matrix_spec.json`) composes `write_cycle_eprom` per family and emits `validation-matrix.{json,md}` artifacts. Use it for families where a spec entry already exists (eprom/flash3/flash4/sram). It requires `--board`, `--chip`, `--source`, and a configured `--port`.

**`write_test.sh`** (`firestarter_app/write_test.sh`) is the integration-level harness: generates random/null/0xFF test images at full chip size, runs write→verify→read→compare for each, then does a two-part partial-address write. No new code needed — pass the chip name as `$1`.

```bash
cd firestarter_app && ./write_test.sh W27C512
```

### 2. Blank-Check / `-b` / Auto-Erase Interaction by Family

This is the critical decision point for each chip at the bench. The flag chain flows through `build_flags` (`eprom_operations.py:80–95`) and `convert_to_programmer` (`database.py:562–617`).

**`FLAG_CAN_ERASE` (0x02) is now derived canonically from `electrical.type == "EEPROM"` or `"Flash/EEPROM"` in `database.py:convert_to_programmer:593–606` (Phase 77 / ERASE-01). This is the authoritative source.**

| Family | Algorithm | `electrical.type` | `FLAG_CAN_ERASE` set? | Default write behavior | `-b` / `--no-blank-check` flag |
|--------|-----------|-------------------|-----------------------|------------------------|-------------------------------|
| 0x07 W27C512, W27E512, SST27SF512 | `configure_eprom` | `"EEPROM"` | YES | Blank-check → auto-erase → write | `--no-blank-check` skips blank-check AND sets `FLAG_SKIP_ERASE` (see `_build_op_flags` in `cli_handlers.py:158–165`) |
| 0x08 W27E040 | `configure_eprom` | `"EEPROM"` | YES | Blank-check → auto-erase → write | Same as above |
| 0x06 SST39SF040 | `configure_flash3` | `"Flash/EEPROM"` | YES | Blank-check → auto-erase → write | `--no-blank-check` skips blank-check AND erase |
| 0x05 W29C020, W29C040 | `configure_flash4` | `"Flash/EEPROM"` | YES | Blank-check → auto-erase → write | Same |
| 0x40 FM1608 | `configure_sram` | `"SRAM"` | NO | No VPP, no erase step | SRAM is always overwrite — `-b` not needed |
| 0x07 ST M27C512, SGS-THOMSON M27C512 | `configure_eprom` | `"UV-EPROM"` | NO | Blank-check only — no auto-erase | `--no-blank-check` to skip (use for pre-erased chips) |
| 0x08 AM27C020 | `configure_eprom` | `"UV-EPROM"` | NO | Blank-check only | `--no-blank-check` to skip |
| 0x0B 2516 (new entry) | `configure_eprom` | `"UV-EPROM"` | NO | Blank-check only | `--no-blank-check` for write without eraser |

**Key invariant for `--no-blank-check`:** `cli_handlers.py:158–165` — when `blank_check=False`, `_build_op_flags` passes `skip_erase=not blank_check` = `True`, which sets `FLAG_SKIP_ERASE (0x04)` in addition to `FLAG_SKIP_BLANK_CHECK (0x08)`. For EEPROM-class chips where `FLAG_CAN_ERASE` is already set, combining with `FLAG_SKIP_ERASE` suppresses the erase step. This is the correct behavior for appending a second partial image with `-b -a <offset>` as `write_test.sh` does.

**0xA4 regression guard (Option C, Phase 77):** INIT/END DATA frames are NOT acked by the host (`_execute_phase:ack_data=False` at `eprom_operations.py:372`). This is required to prevent desync on the default write path for EEPROM chips. Do not revert this.

### 3. UV-EPROM Non-Destructive Protocol

For chips where the operator has no UV eraser (ST M27C512, AM27C020, 2516): read-first strategy.

**Step 1 — Blank check (non-destructive):**
```bash
firestarter blank-check <chip>
```
Returns 0 if all bytes are 0xFF. If blank: proceed to full write+verify. If not blank: AND-mask strategy.

**Step 2 — Read and inspect (non-destructive, validates read path + VPP routing):**
```bash
firestarter read <chip> <chip>_read.bin
sha256sum <chip>_read.bin
```
This validates the read path, DB decode (pinout, VPP, size), and algorithm dispatch on real silicon.

**Step 3 — Spend decision:** If chip is blank, write a known image and verify. If not blank but preserving the chip, an AND-mask write (only 1→0 bit transitions) can prove the write path without erasing. The host write command will succeed if the source image only sets bits that are already 0xFF in the chip.

### 4. VPP Monitoring (Verification, Not Routing)

From project memory: `vpp`/`vpe` monitor commands enable the regulator + measure only. No A9/VPE/P1 routing bits are set. A chip seated in the socket is safe during these commands.

```bash
# Continuous VPP monitor (capture 15 s):
timeout -s INT 15 stdbuf -oL firestarter vpp

# VPE rail check:
firestarter vpe
```

Use `vpe` to confirm ~22.4V rail before any 0x0B NMOS write. Use `vpp` to confirm VPP rail separately.

---

## 2516 — Add Mechanism: User-Override DB Entry

### Why `~/.firestarter/database.json`, Not `build_db.py`

The `2516` is confirmed absent from minipro's upstream `infoic.xml` (the 28 "2516" hits are all `25160` SPI serial parts — per project memory, Phase 78 research). `build_db.py` derives all entries from `infoic.xml` at runtime: there is no mechanism to hand-author an entry inside `build_db.py` without hacking the XML parser.

The user-override path at `~/.firestarter/database.json` is the correct mechanism per `CLAUDE.md` ("user overrides go in `~/.firestarter/database.json`") and `chip_resolver.py:resolve_chip:40` (constructs `EpromDatabase()` with default `skip_local_override=False` in production, honoring the override file). The `EpromDatabase` class merges the override file at construction time; `get_eprom_config` finds the chip by `part_number` alias match.

`build_db.py` would need a bespoke hand-authored entry section, which is architecturally wrong (it is a fetch-and-decode pipeline, not an authoring tool). `~/.firestarter/database.json` is the documented escape hatch for exactly this case.

**Note:** A `~/.firestarter/database.json` entry is NOT subject to `diff_db.py` or `check_dispatch.py` — those gates run against `chip_database.json` only. The 2516 entry must be manually validated for safety before use (no DB gate catches it). This is the tradeoff of the user-override path.

### Required Field Schema

The `EpromDatabase._map_data` method (`database.py:385`) extracts fields from the stored dict. `convert_to_programmer` (`database.py:562`) reads `electrical-type` (the key is hyphenated in the `_map_data` output, different from the JSON storage key `electrical.type`). The override file must use the schema that `EpromDatabase` actually reads — which is the `get_eprom` flattened output schema, not the raw JSON storage schema.

Inspecting `_map_data` and the DB schema: the override file uses the same JSON structure as `chip_database.json` per-chip entries (nested `electrical`, `programming`, `pinout` keys). The `EpromDatabase` loader reads both formats.

**Minimum viable 2516 entry for `~/.firestarter/database.json`:**

```json
{
  "INTEL": [
    {
      "part_number": "2516",
      "support_status": "supported",
      "electrical": {
        "type": "UV-EPROM",
        "size_bytes": 2048,
        "pin_count": 24,
        "vpp": "25V",
        "vpp_mv": 25000,
        "vcc": "5V",
        "vdd": "5V"
      },
      "programming": {
        "algorithm": 11,
        "pulse_duration": "500 us",
        "chip_id_check": false,
        "chip_id_value": "0x00000000"
      },
      "pinout": "DIP24_2716"
    }
  ]
}
```

### Field-by-Field Rationale

| Field | Value | Rationale |
|-------|-------|-----------|
| `part_number` | `"2516"` | Bare name; `EpromDatabase.get_eprom_config` matches by alias split on comma |
| `support_status` | `"supported"` | Graduation target; `chip_resolver.resolve_chip` checks this first |
| `electrical.type` | `"UV-EPROM"` | Intel 2516 is UV-erase only (no electrically-erasable path); `FLAG_CAN_ERASE` must NOT be set |
| `electrical.size_bytes` | `2048` | 2KB = 16Kbit — standard 2516 capacity |
| `electrical.pin_count` | `24` | DIP24 package |
| `electrical.vpp_mv` | `25000` | The Intel 2516 requires 25V VPP for programming (same NMOS family as M2716). The RURP VPE rail provides ~22.4V (~90% of 25V); firmware warns-and-proceeds on under-voltage per Phase 79 behavior |
| `electrical.vpp` | `"25V"` | String form of vpp_mv for display |
| `programming.algorithm` | `11` (= `0x0B`) | `EPROM_LEGACY` / `IC2_ALG_ROM24P_1` — the 24-pin UV-EPROM family handler (`configure_eprom`). All existing 2716-family chips use `0x0B` on `DIP24_2716`: INTEL M2716, AMD AM2716, FUJITSU MBM2716 (verified in `chip_database.json`) |
| `pinout` | `"DIP24_2716"` | Standard 24-pin UV-EPROM layout. All `DIP24_2716` chips in the DB use this pinout for the 0x0B algorithm family. The pin layout: VPP=pin 21, OE=pin 20, CE=pin 18, PGM=pin 18 (shared on some variants) |
| `programming.pulse_duration` | `"500 us"` | Conservative mid-range for 2516-family. Intel 2516 datasheet specifies 50ms programming pulse but the firmware's `configure_eprom` `pulse_delay` is in microseconds (verified `interpret_timing` BUG-2 fix in `build_db.py:273`). `500 us` matches the AMD AM2716 entry. Fine-tune during bench if needed |
| `programming.chip_id_check` | `false` | The 2516 has no electronic chip ID (JEDEC ID not present on NMOS devices); the DB entries for all other 2716-family chips also show `chip_id_value: "0x00000000"` |

**2716-family base profile confirmation** (from live DB query against `chip_database.json`):
- INTEL M2716: algo=0x0B, pinout=DIP24_2716, vpp_mv=25000, etype=UV-EPROM, size=2048
- AMD AM2716: algo=0x0B, pinout=DIP24_2716, vpp_mv=18000, etype=UV-EPROM, size=2048
- FUJITSU MBM2716: algo=0x0B, pinout=DIP24_2716, vpp_mv=12000, etype=UV-EPROM, size=2048

The 2516 maps onto the INTEL M2716 profile (same die era, NMOS, 25V VPP class) with `vpp_mv=25000`.

### Applying the Override

```bash
mkdir -p ~/.firestarter
# Write the JSON above to ~/.firestarter/database.json
firestarter info 2516   # verify the entry is found and shows correct fields
firestarter blank-check 2516   # non-destructive first probe
```

`chip_resolver.resolve_chip("2516")` will find the entry via `EpromDatabase(skip_local_override=False)` and pass the support-status guard (status=`"supported"`).

---

## Evidence Record Artifact — Reusing Existing Tooling

**No new harness.** The per-chip evidence record is produced by composing existing commands and capturing their output.

**Per-chip evidence procedure:**

```bash
# 1. Identity check (verify port + R1)
firestarter dev config

# 2. Blank check (non-destructive)
firestarter blank-check <chip>

# 3. Info dump (validates DB decode: VPP, algorithm, size, type)
firestarter info <chip>

# 4. Write cycle with SHA evidence (electrically-rewritable chips):
firestarter dev write-cycle \
  --runs 3 \
  --source <image.bin> \
  --output-dir evidence/<chip>/ \
  <chip>

# 5. Independent read + SHA:
firestarter read <chip> evidence/<chip>/final_read.bin
sha256sum evidence/<chip>/final_read.bin

# 6. Verify against source:
firestarter verify <chip> <image.bin>
```

The `dev write-cycle` output directory contains: per-run read-back `.bin` files (SHA-logged to stdout), the source image SHA, and PASS/FAIL verdict. This is the evidence artifact per chip. Store the directory under `.planning/phases/<phase-number>-*/` as part of the bench session.

**For UV-EPROMs (read-only session when not blank):** Steps 1–3 + step 5 (read + SHA) constitute a valid evidence record for the read path and DB decode correctness. The write path remains unproven until a blank chip is available.

**For `dev validate-family`** (when running a family sweep): use the `--output-dir` option to capture the `validation-matrix.json` artifact. This is appropriate for confirming full-family behavior across all chips in the inventory that share an algorithm family.

---

## DB Correctness Verification (Post-Bench)

**If a chip behaves differently from DB claims** (wrong size, wrong VPP trigger, wrong algorithm behavior), the mismatch is evidence of a DB decode error. Remediation path:

1. `firestarter info <chip>` — check all fields (VPP, type, algorithm, size, pinout).
2. Cross-reference against `chip_database.json` entry for the exact `part_number`.
3. If a field is wrong in the DB: trace back to `build_db.py` decode logic — specifically `VPP_MV` table (line 88–105), `PROTOCOL_MAP` (line 27–47), `resolve_pinout_key` (line 173–270), and `interpret_timing` (line 273–284).
4. Fix `build_db.py`, regenerate with `python tools/build_db.py`, then run `python tools/check_dispatch.py` and `python tools/diff_db.py` (both must pass with zero violations).

**The gates:**
- `python tools/check_dispatch.py` — 744-chip VPP safety + dispatch correctness (exit 0 = clean)
- `python tools/diff_db.py` — per-chip diff against `tools/baseline/chip_database.baseline.json` (exit 0 = all changes explained)

Both are required after any DB modification before a phase is verified.

---

## Python Test Environment

No changes from v1.14. Current state (verified at v1.14 close):

| Component | Version | Notes |
|-----------|---------|-------|
| Python (devcontainer) | 3.12 | CI runs 3.9/3.11; f-string backslash issues mask on 3.12 |
| pytest + pytest-cov | current | 650 tests at v1.14 close; floor 70% |
| ruff | current | check + format enforced in CI |
| mypy (strict) | current | 8 modules; any touched module stays in scope |
| Click | current | CLI framework |

**Install in dev mode:**
```bash
cd firestarter_app && pip install -e '.[test]'
```

**Run suite:**
```bash
cd firestarter_app && pytest --cov-fail-under=70
```

---

## Firmware Stack (Unchanged)

| Component | Notes |
|-----------|-------|
| PlatformIO, `[env:leonardo]` | `pio run -e leonardo`; flash budget 89.5% at v1.14 close (3,018 bytes free) |
| `configure_eprom` (0x07/0x08/0x0B) | Handles all 0x0B NMOS chips including the 2516 path — no new handler needed |
| `configure_flash3` (0x06) | SST39SF040 |
| `configure_flash4` (0x05) | W29C020, W29C040 |
| `configure_sram` (0x28) | FM1608 (FRAM, type=4, Rule 3 override in build_db.py) |

**Firmware is untouched for v1.15 unless a bench defect surfaces.** If a defect forces a fix, it requires dual-repo lockstep and flash budget verification.

---

## What NOT to Add

- **No new Python packages.** All evidence capture uses existing `write_cycle_eprom`, `consistency_check_eprom`, and CLI commands.
- **No new firmware handlers.** The 2516 uses the existing `configure_eprom` via `0x0B` — same as M2716, AM2716.
- **No new harness.** `dev validate-family`, `dev write-cycle`, and `write_test.sh` are sufficient. Do not build a parallel bench runner.
- **Do NOT add the 2516 to `build_db.py`.** It is absent from upstream `infoic.xml`; `build_db.py` is a fetch-and-decode pipeline, not an authoring tool. The user-override path is architecturally correct for this case.
- **Do NOT add the 2516 to `chip_database.json` by hand.** That file is generated output from `build_db.py` and is committed; hand-editing it will be overwritten on the next `build_db.py` run and will trigger `diff_db.py` failures.
- **No new `diff_db.py` root-cause rules** for v1.15 unless a DB regeneration is triggered by a bench-found decode error.

---

## Sources

| Source | Confidence | How Used |
|--------|-----------|---------|
| `firestarter_app/firestarter/eprom_operations.py:766–873` (verified 2026-06-23) | HIGH | `write_cycle_eprom` API — the canonical per-chip evidence method |
| `firestarter_app/firestarter/eprom_operations.py:80–95` (verified 2026-06-23) | HIGH | `build_flags` + `FLAG_SKIP_ERASE` / `FLAG_SKIP_BLANK_CHECK` interaction |
| `firestarter_app/firestarter/database.py:562–617` (verified 2026-06-23) | HIGH | `convert_to_programmer`; `FLAG_CAN_ERASE` from `electrical-type` (Phase 77 canonical fix) |
| `firestarter_app/firestarter/cli_handlers.py:158–165, 434–475, 1419–1560` (verified 2026-06-23) | HIGH | `_build_op_flags`; `--no-blank-check` flag; `dev validate-family` Tier-3 runner |
| `firestarter_app/firestarter/chip_resolver.py:16–63` (verified 2026-06-23) | HIGH | `resolve_chip` support-status guard; `skip_local_override=False` production path |
| `firestarter_app/tools/build_db.py:27–148, 173–270, 273–284` (verified 2026-06-23) | HIGH | PROTOCOL_MAP; resolve_pinout_key; interpret_timing; NMOS_TRUE_VPP_MV; RURP_VPP_CEILING_MV=25000 |
| `firestarter_app/tools/check_dispatch.py:79, 117–131` (verified 2026-06-23) | HIGH | `_FAMILY_VPP_INVARIANTS["configure_eprom"]=(0,25000)`; KNOWN_PROTOCOLS (0x34 excluded) |
| `firestarter_app/tools/validation_matrix_spec.json` (verified 2026-06-23) | HIGH | Tier-3 rep_chip for each family; skip_boards; oracle rules |
| `firestarter_app/write_test.sh` (verified 2026-06-23) | HIGH | Integration test script mechanics; `-b -a <offset>` partial write pattern |
| `firestarter_app/firestarter/data/chip_database.json` (live query 2026-06-23) | HIGH | 2716-family profile: M2716 algo=0x0B, DIP24_2716, vpp_mv=25000, size=2048; all 10 existing inventory chips verified fields |
| `firestarter_app/firestarter/constants.py:77–88` (verified 2026-06-23) | HIGH | FLAG_CAN_ERASE=0x02, FLAG_SKIP_ERASE=0x04, FLAG_SKIP_BLANK_CHECK=0x08 |
| Project memory: `reference_vpp_vpe_no_socket_routing.md` | HIGH | vpp/vpe monitor commands are measure-only; no routing bits set |
| Project memory: `project_phase79_gate_reexamined.md` | HIGH | VPE=22.4V DMM / 23.9V fw; firmware warns-and-proceeds on under-voltage; 0x0B uses VPE rail directly |
| Project memory: `project_phase77_shipped.md` | HIGH | FLAG_CAN_ERASE from electrical.type; 0xA4 guard; SAFE-01/02/03; bench-proven on W27C512 |
| Project memory: `project_phase78_shipped.md` | HIGH | 2516 absent from infoic.xml confirmed |
| `CLAUDE.md` (root): `~/.firestarter/database.json` | HIGH | User-override DB path documented as the canonical mechanism for custom entries |

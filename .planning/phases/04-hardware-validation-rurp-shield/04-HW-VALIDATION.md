---
phase: 04-hardware-validation-rurp-shield
generated: 2026-05-12T11:52:49Z
requirements_validated: [HW-01, HW-02, HW-03, HW-04, HW-05]
hardware:
  board: <Uno|Leonardo>
  firmware_version: <pending HW-02..HW-05 bench runs>
  host_machine: <pending HW-02..HW-05 bench runs>
  bench_equipment:
    - Multimeter: <model pending HW-04/HW-05 bench>
    - Power supply: <RURP-onboard regulator>
chips_tested:
  - {part: W27C512,    algo: 0x07, package: DIP28, lot: <pending HW-02>}
  - {part: AM29F040,   algo: 0x06, package: DIP32, lot: <pending HW-03>}
  - {part: SST39SF040, algo: 0x06, package: DIP32, lot: <pending HW-03>}
  - {part: AT28C256,   algo: 0x0D, package: DIP28, lot: <pending HW-04>}
  - {part: AM28F010,   algo: 0x10, package: DIP32, lot: <pending HW-05>}
follow_ups: []
---

# Phase 4 — Hardware Validation (RURP shield) — Evidence

## §1 HW-01 — Test-script repair (WARNING-4 closure + jq schema migration)

**Date:** 2026-05-12T11:52:49Z
**Plan ref:** 04-01
**Commit:** firestarter_app@16dcafe

### Before (live broken refs)

Layer 1 — filename (the v1.0 / Phase 11 CLEAN-01 leftover, WARNING-4):

- `firestarter_app/firestarter_test.sh:31` — `JSON_FILE='./firestarter/data/database_generated.json'`
- `firestarter_app/write_test.sh:17`         — `JSON_FILE='./firestarter/data/database_generated.json'`

Layer 2 — jq schema (surfaced by gsd-phase-researcher, per CONTEXT.md D-01 RESEARCH.md-corrected):

- `firestarter_app/firestarter_test.sh:48-67` — three jq blocks with the pre-Phase-11 flat schema:
  - `select(.name == $target_name) | .["memory-size"]`
  - `select(.name == $target_name) | .["has-chip-id"]`
  - `select(.name == $target_name) | .["can-erase"]`
- `firestarter_app/write_test.sh:35-40` — single jq block, same pre-Phase-11 flat schema:
  - `select(.name == $target_name) | .["memory-size"]`

The new on-disk `chip_database.json` is `{manufacturer: [chip_records, ...]}` with nested
`.electrical.size_bytes`, `.programming.chip_id_check`, `.part_number`, `.electrical.type`.
The legacy queries would have returned `null` for every lookup even with the filename layer
fixed — both layers had to land in one atomic sub-repo commit per CONTEXT.md D-08.

### After (repaired refs)

Layer 1 — both scripts:

- `firestarter_app/firestarter_test.sh:31` → `JSON_FILE='./firestarter/data/chip_database.json'`
- `firestarter_app/write_test.sh:17`         → `JSON_FILE='./firestarter/data/chip_database.json'`

Layer 2 — `firestarter_test.sh` three jq queries (flattened across manufacturers; nested paths):

```bash
MEMORY_SIZE_HEX=$(jq -e --arg target_name "$EPROM_NAME" -r '
  .[] |
  .[] |
  select(.part_number == $target_name) |
  .electrical.size_bytes
' "$JSON_FILE")

HAS_CHIP_ID=$(jq -e --arg target_name "$EPROM_NAME" -r '
  .[] |
  .[] |
  select(.part_number == $target_name) |
  .programming.chip_id_check
' "$JSON_FILE")

CAN_ERASE=$(jq -e --arg target_name "$EPROM_NAME" -r '
  .[] |
  .[] |
  select(.part_number == $target_name) |
  (.electrical.type == "Flash/EEPROM")
' "$JSON_FILE")
```

Layer 2 — `write_test.sh` single jq query:

```bash
MEMORY_SIZE_HEX=$(jq -e --arg target_name "$EPROM_NAME" -r '
  .[] |
  .[] |
  select(.part_number == $target_name) |
  .electrical.size_bytes
' "$JSON_FILE")
```

The `MEMORY_SIZE_HEX` variable name is retained as-is for backward compatibility with the
downstream `dd` invocations; the new `.electrical.size_bytes` returns a plain integer
(e.g. `65536` for W27C512) and bash arithmetic auto-coerces — no hex conversion is needed.

The `CAN_ERASE` query was rewritten as `(.electrical.type == "Flash/EEPROM")` per the
`<interfaces>` translation table in 04-01-PLAN.md and RESEARCH.md §HW-01: the legacy
`.["can-erase"]` flag has no direct successor in the new schema, but the `Flash/EEPROM` type
discriminator correctly captures the "this chip supports erase" semantics for the bench-runner.

### Dry-run validation

Syntax check (both scripts, exit 0 expected):

```text
$ bash -n firestarter_app/firestarter_test.sh ; echo "exit=$?"
exit=0
$ bash -n firestarter_app/write_test.sh ; echo "exit=$?"
exit=0
```

`jq -e` smoke against the live `firestarter_app/firestarter/data/chip_database.json` for
the W27C512 reference chip (HW-02 baseline):

```text
$ JSON_FILE=firestarter_app/firestarter/data/chip_database.json
$ jq -e --arg t "W27C512" -r '.[] | .[] | select(.part_number == $t) | .electrical.size_bytes' "$JSON_FILE"
65536
exit=0
$ jq -e --arg t "W27C512" -r '.[] | .[] | select(.part_number == $t) | .programming.chip_id_check' "$JSON_FILE"
true
exit=0
$ jq -e --arg t "W27C512" -r '.[] | .[] | select(.part_number == $t) | (.electrical.type == "Flash/EEPROM")' "$JSON_FILE"
true
exit=0
```

All three jq smoke gates pass against the new nested schema. The W27C512 record returns
`size_bytes=65536` (matches the v1.0 PROJECT.md "What works today" baseline), `chip_id_check=true`
(so the HW-02 bench-run's chip-ID test branch will fire), and the `Flash/EEPROM`-type predicate
returns `true` (so the HW-02 erase + blank-check branch will also fire).

Firmware native unit-test state — **cited, not re-run** per Phase 3 LEARNINGS lesson
"existing test runs should be cited, not re-executed":

- `pio test -e native` 25/25 PASS — see `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-VERIFICATION.md` "Behavioral Spot-Check" subsection (Plan 01-01 + Plan 01-02 closure, firmware sub-repo HEAD as of 2026-05-12).

### Verdict

**PASS** — both scripts parse cleanly via `bash -n` against the post-Phase-11 DB filename
AND resolve W27C512 metadata via `jq -e` against the new nested `chip_database.json` schema.
WARNING-4 is closed: zero non-comment `database_generated.json` references survive in
either script (grep gate). Plan 04-02 (Wave 2 — HW-02 W27C512 + HW-03 AM29F040/SST39SF040
+ HW-04 AT28C256) inherits a known-clean test-script state.

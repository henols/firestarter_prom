---
phase: 04-hardware-validation-rurp-shield
generated: 2026-05-12T11:52:49Z
last_session: 2026-05-12T20:31:39Z
requirements_validated: [HW-01]
requirements_attempted: [HW-02]
requirements_pending: [HW-03, HW-04, HW-05]
hardware:
  board: Uno
  firmware_version: "2.0.6 (source HEAD firestarter@587396a, flashed 2026-05-12T20:14Z; tag 2.0.6 is 30 commits behind HEAD — version.h not bumped, see follow_up firmware-version-drift)"
  host_machine: 7cc15a2d6fd7
  host_app: firestarter_app@16dcafe (2.0.7_dev)
  bench_equipment:
    - Programmer: RURP shield Rev 2.0
    - Multimeter: <model pending HW-04/HW-05 bench>
    - Power supply: <RURP-onboard regulator>
chips_tested:
  - {part: W27C512,    algo: 0x07, package: DIP28, lot: <pending HW-02 bench>, session_2026-05-12: "ID 0xda08 read OK, blank OK; write FAILED (host MAIN-phase bug, see follow_up host-main-phase-bug)"}
  - {part: SST27SF512, algo: 0x07, package: DIP28, lot: "0045231-B (from photo)", session_2026-05-12: "ID 0xbfa4 read OK, blank OK; write FAILED (host MAIN-phase bug, see follow_up host-main-phase-bug)"}
  - {part: SST39SF040, algo: 0x06, package: DIP32, lot: <pending HW-03 bench>, session_2026-05-12: "ID read 0x0000 (expected 0xbfb7), reads return all 0x00, erase reports success but chip stays at 0x00 — see follow_up sst39sf040-dead-chip"}
  - {part: AM29F040,   algo: 0x06, package: DIP32, lot: <pending HW-03 bench>}
  - {part: AT28C256,   algo: 0x0D, package: DIP28, lot: <pending HW-04 bench>}
  - {part: AM28F010,   algo: 0x10, package: DIP32, lot: <pending HW-05 bench>}
follow_ups:
  - id: host-main-phase-bug
    severity: BLOCKER
    surface: firestarter_app (host CLI)
    evidence: bench-evidence-2026-05-12/02-sst27sf512_write_verbose_data_err_-3.log + 10-w27c512_write_data_err_-3_universal.log
    detail: "EpromOperator MAIN-phase data-send constructs the 4-byte data packet header (# + 2-byte size + 1-byte checksum) but never sends the payload bytes that should follow. Firmware times out after 2s waiting for payload → Data err -3 (rurp_serial_utils.cpp:82). Universal across configure_eprom dispatch family (algo=0x07/0x08/0x0B); confirmed identical failure mode on canon W27C512 AND substitute SST27SF512, both pre-flash and post-flash firmware. Blocks all Plan 04-02 §2/§3/§4 bench work."
  - id: firmware-version-drift
    severity: HIGH
    surface: firestarter (firmware) + firestarter_app (host)
    evidence: bench-evidence-2026-05-12/05-firmware_flash_to_587396a.log
    detail: "firestarter/include/version.h VERSION constant ('2.0.6') has not been bumped despite 30 commits since the 2.0.6 git tag (db4e565). firestarter fw misleadingly reports 'already up to date' against the on-board binary even when source has substantial drift (Phase 01 SAF-04+SAF-05, Phase 02 wire-key rename, Phase 12 dispatch chain, etc., all post-tag). Fix: bump VERSION string on every source-tree change to firmware OR change auto-update logic to compare git ref / SHA."
  - id: sst39sf040-dead-chip
    severity: MEDIUM
    surface: operator hardware
    evidence: bench-evidence-2026-05-12/03..08 (5 logs)
    detail: "Operator's SST39SF040 (DIP32) reads chip-ID as 0x0000 instead of expected 0xbfb7. Force-read returns all 0x00. firestarter erase reports success in 0.16s but post-erase reads stay at 0x00 — chip didn't actually erase. Single-chip observation; likely dead silicon or stuck output drivers. Side observation: firmware's chip-erase success path is over-optimistic — it should require DQ7-polling confirmation + post-erase blank-check before claiming success."
  - id: fm1608-db-mismatch
    severity: HIGH (safety)
    surface: firestarter_app/firestarter/data/chip_database.json
    detail: "FM1608 DB entry has {type: 'UV-EPROM', vpp: '12V', algorithm: 7}, but FM1608 is a Ramtron parallel FRAM — 5V single-supply, NO 12V programming voltage. firestarter write FM1608 would engage configure_eprom (algo=7) → 12V VPP regulator → likely chip damage. DB entry needs to be either removed or rewritten with a correct FRAM-class algorithm (or removed pending implementation). vdd: '3.3V' field is also wrong (real FM1608 is 5V Vdd)."
  - id: w27e512-missing-db-entry
    severity: LOW
    surface: firestarter_app/firestarter/data/chip_database.json
    detail: "Winbond W27E512 (64K 5V EEPROM) has no DB entry. Adjacent entries: W27E257 (32K, algo=7, vpp=13.5V), W27C01/E01/L01 family (128K, algo=8). W27E512 needs its own entry — operator inventory included this part."
  - id: firestarter-info-label-bugs
    severity: MEDIUM
    surface: firestarter_app (host CLI info subcommand)
    detail: "firestarter info SST27SF512 has at least 4 label inconsistencies: (a) Type: 'EPROM' but DB says 'Flash/EEPROM'; (b) 'Can be erased: false' but DB type implies erasable; (c) 'Protocol: EEPROM (ID: 0x07)' but algo=0x07 is EPROM_STD per firestarter/CLAUDE.md, not EEPROM; (d) description text 'no high voltage required' but algo=0x07 uses 13V VPE_TO_VPP (dangerously incorrect); (e) Flags: 0x30 labeled 'Can be electrically erased / Has Readable Chip ID' but per constants.py 0x30 = FLAG_VPE_AS_VPP (0x10) | FLAG_OUTPUT_ENABLE (0x20), no relation to those labels. Single-line user-facing description is misleading and partially dangerous."
  - id: firestarter-erase-b-silent
    severity: LOW
    surface: firestarter_app (host CLI erase subcommand)
    detail: "firestarter erase -b SST39SF040 (blank-check-after-erase flag) reported 'Erase successful' with no blank-check output. Either -b is not implemented, silently fires on a path that ignored the result, or the surface output suppression is unintended. UX bug."
  - id: firestarter-force-flag-scope
    severity: LOW
    surface: firestarter_app (host CLI argparse)
    detail: "firestarter -f blank SST39SF040 errors with 'unrecognized arguments: -f' — -f is subcommand-level only (firestarter blank -f SST39SF040 works). Either accept both forms via argparse parent/child setup, or improve the error message to point users at the correct invocation."
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

## Bench Session 2026-05-12 — Diagnostic Findings (Plan 04-02 deferred)

**Outcome:** Plan 04-02 (Wave 2 — HW-02/HW-03/HW-04) **deferred**. No §-section evidence captured. Root cause: a host-side bug in firestarter_app's `EpromOperator` MAIN-phase data-send path blocks all write operations against the `configure_eprom` dispatch family (algo=0x07/0x08/0x0B). Confirmed on the canon W27C512 chip + the SST27SF512 substitute, against both the pre-flash (2.0.6 git tag) and post-flash (source HEAD `587396a`, 30 commits ahead) firmware builds.

Wave 2 cannot close until the host bug is fixed. The bench session captured substantial diagnostic gold (8 follow_ups in frontmatter, 10 raw evidence logs in `bench-evidence-2026-05-12/`) that should accelerate the fix.

### Session inventory + canon-vs-available

Plan 04-02 was authored assuming the canon four chips would be in hand. At bench start:

| Plan section | Canon chip | Operator inventory | Disposition |
|--------------|-----------|---------------------|--------------|
| §2 HW-02 | W27C512 (algo=0x07) | ✓ **had it** (initially mislabeled "W27E512" but operator clarified as DB-canon W27C512) | Bench attempted, blocked by host bug |
| §3a HW-03 chip-erase | AM29F040 (algo=0x06) | ✗ | Substituted to SST39SF040 chip-erase per D-12 |
| §3b HW-03 sector-erase | SST39SF040 (algo=0x06) | ✓ | Substitute and canon both → SST39SF040 (single chip, both variants per D-12) |
| §4 HW-04 | AT28C256 (algo=0x0D) | ✗ | Deferred per D-12 (no in-family substitute) |

D-12 (committed `f093643`) recorded the substitution plan: SST27SF512 for §2 (later resolved as: canon W27C512 was actually available), SST39SF040 for §3a + §3b, HW-04 deferred.

### Bench-attempt timeline

| Order | Chip | Operation | Result | Logfile |
|-------|------|-----------|--------|---------|
| 1 | SST27SF512 (DIP28, sub for W27C512) | `write_test.sh` then `firestarter write` | FAIL: `Data err -3` after 100% data sent, INIT complete, MAIN phase stalls at `OK: Req data` → host sends 4-byte packet header only, no payload | [01](bench-evidence-2026-05-12/01-sst27sf512_write_failed.log) + [02](bench-evidence-2026-05-12/02-sst27sf512_write_verbose_data_err_-3.log) |
| 2 | SST27SF512 | `firestarter blank` (post-fail) | PASS — chip still blank, confirming write programmed zero bytes despite host's 100% progress claim | (re-ran inline) |
| 3 | SST39SF040 (DIP32, swap) | `firestarter blank` | FAIL: chip-ID read `0x0000`, expected `0xbfb7` | [03](bench-evidence-2026-05-12/03-sst39sf040_chipid_0000.log) |
| 4 | SST39SF040 | `firestarter -v blank` (verbose) | Same fail — firmware enters INIT, AMD ID command returns 0x00 0x00 | [04](bench-evidence-2026-05-12/04-sst39sf040_chipid_0000_verbose.log) |
| 5 | (no chip) | `pio run -t upload -e uno` flash | SUCCESS in 9.37s — 25954 bytes; on-board firmware advanced from 2.0.6-tag to HEAD `587396a` (30 commits ahead, includes Phase 01/02/12 closures) | [05](bench-evidence-2026-05-12/05-firmware_flash_to_587396a.log) |
| 6 | SST39SF040 (re-insert) | `firestarter blank` | FAIL: still chip-ID 0x0000 — flash didn't fix this | [06](bench-evidence-2026-05-12/06-sst39sf040_chipid_0000_post_flash.log) |
| 7 | SST39SF040 | `firestarter blank -f` (force + verbose) | bypass ID check; enters MAIN; reads return 0x00 across full chip; "Not blank, at 0x000000" → chip not silent, but reads all zeros | [07](bench-evidence-2026-05-12/07-sst39sf040_force_blank_reads_0x00.log) |
| 8 | SST39SF040 | `firestarter erase -f -b` | "Erase successful (0.16s)" — but `-b` produced no visible blank-check; subsequent reads still all 0x00 → erase claim is false | [08](bench-evidence-2026-05-12/08-sst39sf040_fake_erase_success.log) |
| 9 | W27C512 (DIP28, swap) | `firestarter blank` | PASS — chip-ID `0xda08` matched, chip fully blank in 5.38s. Post-flash dispatch working correctly for this chip family. | [09](bench-evidence-2026-05-12/09-w27c512_blank_pass_chipid_0xda08.log) |
| 10 | W27C512 | `firestarter -v write` (canon HW-02 attempt) | FAIL: **identical failure mode to step 1** — `Data err -3` after 100% data, MAIN phase stalls at `OK: Req data` → host sends 4 bytes only. Confirmed: bug is universal across configure_eprom family, NOT chip-specific. | [10](bench-evidence-2026-05-12/10-w27c512_write_data_err_-3_universal.log) |
| 11 | W27C512 | `firestarter blank` (post-fail) | PASS — chip still blank. Write programmed zero bytes (same as step 2 for SST27SF512) | (re-ran inline) |

### Conclusive findings

1. **The host-side MAIN-phase data-send is broken for `configure_eprom` family.** Evidence: identical failure mode on two chips (canon W27C512 + sub SST27SF512), identical failure with both pre-flash and post-flash firmware. The verbose trace shows the host's send-data routine emits the 4-byte packet header (`#` + 2-byte size + 1-byte checksum) but no payload bytes follow. Firmware times out 2s later via `rurp_communication_read_data` returning `-3` ([rurp_serial_utils.cpp:82](../../../firestarter/src/boards/rurp_serial_utils.cpp#L82)).

2. **Firmware version-string drift hid the v1.1 firmware updates from the bench.** The on-board binary was at the 2.0.6 tag (`db4e565`) — pre-Phase-01-01 (SAF-04), pre-Phase-01-02 (SAF-05), pre-Phase-02-01 (vpp→vpp_mv), pre-Phase-12-02 (protocol-prefix dispatch). `firestarter fw` reported "up to date" because `version.h` was never bumped. Mid-session reflash brought the firmware to HEAD `587396a` — but did NOT fix the host MAIN-phase bug (which is on the Python side, not C++ firmware side).

3. **The operator's SST39SF040 is functionally dead** (or has stuck data-bus output drivers). The chip would have been the only canon §3b candidate had it been alive. The W27C512 substitute path is contingent on the host bug, not on SST39SF040 specifically.

4. **No `.planning/STATE.md` or `.planning/ROADMAP.md` writes** — orchestrator-owned per Phase 3 LEARNINGS surprise. Plan 04-02 is **status: deferred**, not status: complete or status: partial.

### Cross-references

- Plan body: [04-02-PLAN.md](04-02-PLAN.md)
- Substitution plan: 04-CONTEXT.md D-12 (committed `f093643`)
- Plan closure: [04-02-SUMMARY.md](04-02-SUMMARY.md) — status: deferred
- Raw bench evidence: [bench-evidence-2026-05-12/](bench-evidence-2026-05-12/) — 10 logs + 1 binary readback sample
- Follow-up tracking: frontmatter `follow_ups:` (8 items, with severity classes BLOCKER / HIGH / MEDIUM / LOW)

### What unblocks Plan 04-02 resumption

In dependency order:

1. **Fix host MAIN-phase bug** (`follow_up: host-main-phase-bug`, BLOCKER) — the Python `EpromOperator` data-send must emit header AND payload, not just header. Likely a single-file fix in `firestarter_app/firestarter/eprom_operations.py` (or `serial_comm.py`). The verbose trace in log 10 pinpoints the exact failure: `Sent 4 bytes` should be `Sent <header_size + payload_size> bytes`.
2. **Replace SST39SF040 chip** (`follow_up: sst39sf040-dead-chip`) — sourcing another SST39SF040 (or substituting with a different algo=0x06 chip, e.g. AM29F040 if also sourced).
3. **Source AT28C256** for HW-04 (still deferred per D-12).
4. **Bump `version.h` VERSION** (`follow_up: firmware-version-drift`, HIGH) — prevents future drift hiding.
5. **Fix CLI label bugs + DB entries** (`follow_ups: firestarter-info-label-bugs`, `fm1608-db-mismatch`, `w27e512-missing-db-entry`, `firestarter-erase-b-silent`, `firestarter-force-flag-scope`) — UX + safety improvements; not strictly blockers for Plan 04-02 but cleanup-worthy.

Once #1 is fixed and at least one canon §3 chip is in hand, re-run `/gsd-execute-phase 04 --wave 2 --interactive` to resume.

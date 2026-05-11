# Milestones

## v1.0 — Protocol-Aware Programming Architecture (Shipped: 2026-05-11)

**Phases:** 13 | **Plans:** 22 | **Timeline:** 2026-05-08 → 2026-05-11 (4 days, 66 commits)

**Delivered:** Replaced the guessing-based chip-type pipeline with an explicit
algorithm-first architecture where minipro `protocol_id` flows authoritatively
from upstream XML through the database, wire protocol, and firmware dispatch —
and the firmware executes exactly that algorithm for every chip in the 743-entry
DB. Two safety-critical hazards closed (BLOCKER-1, BLOCKER-2, WARNING-5).

### Key Accomplishments

1. **Algorithm-first wire protocol** (REQ-SER-01, REQ-FW-01) — `firestarter_handle_t`
   carries an explicit `algorithm` integer; `memory.cpp::configure_memory`
   protocol-prefix dispatch covers all 13 KNOWN_PROTOCOLS (0x05/0x06/0x07/0x08/
   0x0B/0x0D/0x0E/0x10/0x27/0x28/0x29/0x35/0x39); legacy `type` enum retained
   as fallback only. Verified by 15/15 Unity dispatch tests on `[env:native]`
   plus `check_dispatch.py` PASS across all 743 chips.

2. **Database pipeline canonicalized** (REQ-DB-01..05, Phases 01 + 11) — Single
   `build_db.py` fetches `infoic.xml` from upstream minipro at runtime,
   parses deterministically to `minipro_complete_db.json` with explicit
   `algorithm` integer, decoded-millivolt `vpp`, correct DIP28 variant splitting
   (`DIP28_27512` / `DIP28_27256` / `DIP28_2764`), unknown-protocol chips
   skipped with WARN. Legacy `parse_db.py`, `infoic.xml`, `verified.txt`,
   `database_generated.json`, `pin-maps.json` all removed.

3. **Five new firmware handlers** — `configure_eprom` (UV-EPROM STD/QUICK/LEGACY,
   Phase 03), `configure_flash3` (AMD-style sector erase, Phase 04),
   `configure_flash_intel` (Intel command-register flash, Phase 05),
   `configure_eeprom28c` (AT28C SDP-disable + DQ7-polling page write, Phase 06),
   `configure_sram` (5V SRAM safe no-op, Phase 12).

4. **Pre-write safety stack** (REQ-SAF-01/02/03, Phases 03 + 07) — VPP ADC
   compare before first write pulse on UV-EPROM and 28C-EEPROM paths;
   chip-ID validation for Intel + AMD + UV-EPROM (`A9_VPP_ENABLE` sequence
   for 27Cxxx); blank check across Flash/EEPROM write inits gated by
   `!FLAG_SKIP_BLANK_CHECK`.

5. **Static-pin and address-bus correctness** (REQ-FW-05/06, Phase 10) —
   `static_high_mask` end-to-end (`pinouts.json` static-high-pins → wire JSON
   static-high → `bus_config_t.static_high_mask` → `mem_util_remap_address_bus`
   unconditional OR); replaces hardcoded `pins == 24` heuristic for tied-high
   CE2/NC pins. Dead `READ_WRITE == WRITE_FLAG` condition replaced with the
   physical-reality `if (handle->pins < 32)` plus VPE_TO_VPP/A16-sharing comment.

6. **CLI hardware-compatibility surface** (REQ-UX-01/02, Phase 09) —
   `firestarter search` flags chips with no valid pinout via `[!]` marker;
   `firestarter info --adapter` prints a DIP-mirrored two-column physical-pin →
   RURP-signal table derived entirely from `pinouts.json`, enabling adapter
   wiring without source-code reference.

7. **Three safety-critical close-out phases** —
   - **Phase 11** consolidated the build pipeline to `build_db.py` and removed
     all legacy artifacts (REQ-DB-05; byte-identical regeneration verified).
   - **Phase 12** closed BLOCKER-1 (277 chips fell through to "Memory type
     0x%02x not supported" before the protocol-prefix dispatch) + BLOCKER-2
     (52 SRAM chips routed to `configure_eprom` with 12V VPP regulator on 5V
     parts). Fixed at three layers: firmware dispatch + Python `_ALGO_MEM_TYPE`
     table + `build_db.py` SRAM tagging.
   - **Phase 13** closed WARNING-5 (23 DIP28_2764 5V EEPROMs mistagged in
     upstream minipro as `algorithm=0x07` would have applied 12V to socket
     pin 1 = A14 address line on write). Data-layer-only fix via inline
     3-predicate override in `build_db.py` flipping these chips to `0x0D`
     (`EEPROM_POLL` → `configure_eeprom28c`, pure 5V path with zero VPP
     regulator engagement). Permanent regression guard `_28C_EEPROM_HAZARD_PINOUT`
     in `check_dispatch.py`.

### Stats

- **Files modified:** firmware (Arduino C++) + Python CLI submodules; meta-repo
  tracks `.planning/` only
- **Verification:** Phase 11 (4/4), Phase 12 (8/8), Phase 13 (8/8) formally
  verified end-to-end. Phases 01-10 verified by independent
  `INTEGRATION-CHECK.md` + Phase 12 `check_dispatch.py` regression on the full
  743-chip DB.
- **E2E flows shipped:** `write -e W27C512`, `write -e AM29F040`,
  `write -e SST39SF040`, `erase -s 0x10000 -e SST39SF040`, `write -e 6116`
  (SRAM safe), `write -e AT28C256` (now safe via Phase 13), `write -e AM28F010`
  (Intel — see Known Gaps), `info <chip> --adapter`, `python tools/build_db.py`.

### Key Decisions

- **Database source:** minipro `infoic.xml` via `build_db.py` (not hand-curated
  JSON). Outcome: ✓ — 743 chips covered without per-chip curation overhead.
- **Wire protocol:** New explicit `algorithm` integer field (minipro
  `protocol_id`); `type` retained as legacy fallback. Outcome: ✓ — all 13
  KNOWN_PROTOCOLS dispatched correctly; no regressions.
- **Firmware dispatch:** Protocol-prefix `if-return` block per KNOWN_PROTOCOLS
  entry in `configure_memory`, mem_type chain retained only for legacy
  user-override DB entries. Outcome: ✓ — verified by Phase 12 `check_dispatch.py`.
- **Packages in scope:** DIP 24, 28, 32 only. Outcome: ✓ — SMD/PLCC/serial
  filtered cleanly by `build_db.py`.
- **WARNING-5 fix:** Data-layer override in `build_db.py` rather than
  per-chip firmware switch. Outcome: ✓ — preserves the "algorithm is
  authoritative" contract while routing around the upstream minipro
  classification error for 23 5V EEPROMs.

### Known Gaps (accepted as tech debt for v1.1)

Captured from `.planning/milestones/v1.0-MILESTONE-AUDIT.md` (status:
`gaps_found`). Audit-time score: 4/18 SATISFIED, 13 PARTIAL (verification-gap
only), 1 UNSATISFIED.

- **REQ-SAF-01 partial — Intel-flash write path** (WARNING-1): `flash_intel_write_init`
  (`firestarter/src/proms/flash_intel.cpp:47-62`) enables `REGULATOR |
  P1_VPP_ENABLE` and delays 500ms before the first write pulse, but never calls
  `rurp_read_voltage_mv()` ADC compare. The UV-EPROM and 28C-EEPROM paths
  satisfy REQ-SAF-01; the Intel-flash family (39 chips, algo=0x10, highest VPP
  in firmware) does not. **Severity: WARNING.** Fix scope: 1-2 lines in
  `flash_intel.cpp`; pattern mirrors `eprom_check_vpp`.

- **Phases 01-10 lack formal VERIFICATION.md files** (verification-gap on 13
  requirements). Wiring is independently verified by `.planning/INTEGRATION-CHECK.md`
  + Phase 12 `check_dispatch.py` (743/743 chips PASS) + Phase 13 hazard guard
  (0 violations) + 15/15 Unity dispatch tests. By the workflow rule "missing
  VERIFICATION.md = unverified phase", 10 of 13 phases remain structurally
  unverified. Optional retroactive `/gsd-validate-phase` runs would close.

- **WARNING-2 — 28C chip-ID forward-compat hazard**:
  `eeprom_28c.cpp::eeprom28c_write_init` ignores `handle->chip_id`. Vacuous
  today (zero 0x0D chips in regenerated DB carry `chip_id_value`) but breaks
  REQ-SAF-02 the moment a user-override or upstream DB change populates
  chip_id for an AT28C-family chip.

- **WARNING-3 — wire-protocol key naming**: JSON `"vpp"` key now carries
  millivolts (was volts) — semantic overload. Recommend renaming wire key to
  `"vpp_mv"`. `firestarter_app/CLAUDE.md` example currently shows a phantom
  `"vpp_mv"` key that is not emitted.

- **WARNING-4 — test-script drift**: `firestarter_test.sh:31` and
  `write_test.sh:17` reference the deleted `database_generated.json`. Breaks
  the documented hardware-integration E2E flow.

- **`build_db.py` robustness**: Bare `except:` at lines ~138-186 (silent chip
  drops + KeyboardInterrupt swallow). `requests.get` lacks `raise_for_status()`
  and `timeout` (non-200 upstream silently overwrites DB). Pre-existing,
  out-of-scope of Phase 11 lock.

- **Lost `verified` field**: `minipro_complete_db.json` no longer carries the
  `verified` field; `database.py::get_eproms(verified=True)` silently returns
  empty. Carried in `11-VERIFICATION.md` follow_ups.

- **DIP24/DIP28/DIP32 `static-high-pins` coverage**: Only DIP24 variants
  populated in `pinouts.json` today. DIP28/DIP32 quirk pins (CE2, JEDEC-tied
  NC) could be added in a future phase (INFO-3).

- **`DIP24_2732` pinout** never appears in regenerated DB (no 24-pin
  variant=0x01 chips survive the DIP/memory-type filter on current
  `infoic.xml`). May be intentional; flag for review.

### Hardware Verification

Not performed in this milestone — no RURP shield available in the dev
environment. All verification was structural (code/DB/dispatch tests). The
documented hardware integration tests (`firestarter_test.sh`, `write_test.sh`)
should be re-run against a physical board before declaring the four
chip-family canon (W27C512, 29F040, SST39SF040, AT28C256) hardware-validated.

---

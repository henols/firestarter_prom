# Roadmap: Firestarter — Protocol-Aware Programming Architecture

## Milestones

- ✅ **v1.0 Protocol-Aware Programming Architecture** — Phases 1-13 (shipped 2026-05-11)
- ⏸ **v1.1 Safety Closure & Hardware Validation** — Phases 1-5 (paused at 80% on 2026-05-18; archived at `.planning/milestones/v1.1-paused/`)
- 🚧 **v1.2 Message-ID Logging Rework** — Phases 6-10 (started 2026-05-18)

## Current Milestone: v1.2 — Message-ID Logging Rework

**Goal:** Replace firmware text-string logs with 1-byte numeric message IDs plus raw parameter byte arrays. The format catalog and decoding logic move from firmware PROGMEM to the Python host. Driven by Leonardo flash pressure (currently 98.7% Flash usage) and the protocol-cleanliness benefit of removing per-call string literals.

**Granularity:** Comprehensive
**Total phases:** 5 (numbered 6-10; phase numbering continues from v1.1)
**Total requirements covered:** 23 / 23 (100%) — 22 v1.2 requirements + DOC-02 milestone-close requirement added by this roadmap

### Phases

- [ ] **Phase 6: Logging Infrastructure (catalog + codegen + helper + decoder)** — Phase A of the locked phased migration. Land the canonical catalog, codegen pipeline, firmware `rurp_log_id` helper, host decoder, and CI drift gate — all without removing any existing log code. Both paths coexist briefly.
- [ ] **Phase 7: Convert ERROR + WARN + INFO Call-Sites** — Phase B. Migrate firmware ERROR/WARN/INFO log call-sites to `rurp_log_id`. Old helpers still present for state-machine prefix acks.
- [ ] **Phase 8: Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END)** — Phase C. Convert `OK:` / `INIT:` / `MAIN:` / `END:` call-sites; host parser switches from line-prefix matching to ID-frame decoding for state-machine acks. `DATA:` prefix marker stays literal text.
- [ ] **Phase 9: Delete Old Log Macros + Measure Flash Savings** — Phase D. Remove old `rurp_log` / `rurp_log_P` / `LOG_*_MSG` PROGMEM definitions and `log_info_const` / `log_error_format` / `log_warn` macros. Bump firmware major version. Measure final Leonardo flash usage.
- [ ] **Phase 10: Milestone Close (v1.2)** — Write the v1.2 `MILESTONES.md` entry with the formal flash-savings comparison vs the v1.1 baseline. Update PROJECT.md active-milestone header.

### Phase Details

#### Phase 6: Logging Infrastructure (catalog + codegen + helper + decoder)
**Goal**: A canonical message catalog plus codegen-produced firmware header + host Python module exist, the firmware `rurp_log_id` send-by-ID helper compiles and links alongside the old log helpers, the host `serial_comm.py` can decode an ID-encoded log frame, and CI fails on any drift between the catalog and the generated artifacts. No existing call-site is converted yet — both old and new paths coexist.
**Depends on**: Nothing (first v1.2 phase; PHASE A of the locked phased migration per PROJECT.md "Phased migration" target feature).
**Requirements**: LCAT-01, LCAT-02, LCAT-03, LCAT-04, LCAT-05, LFW-01, LFW-02, LFW-05, LHOST-01, LHOST-02, LHOST-03, LHOST-04, LCI-01, LCI-02, LCI-03, LCI-04, LMIG-01
**Success Criteria** (what must be TRUE):
  1. A single canonical catalog file in the meta-repo declares every firmware log message as `{id, symbolic_name, format_string, parameter_shape}`, and running the codegen script twice on the same catalog produces byte-identical `firestarter/include/messages.h` + `firestarter_app/firestarter/messages.py` artifacts (no timestamps, no ordering instability).
  2. An invalid catalog (duplicate ID, duplicate symbolic name, malformed param shape, empty format string) fails codegen with a clear error before any source files are written — verifiable by introducing each violation in a scratch catalog and confirming the codegen exits non-zero.
  3. `pio run -e leonardo` and `pio run -e uno` both compile cleanly with the new `rurp_log_id(uint8_t, const uint8_t*, uint8_t)` helper available in firmware **alongside** the existing `rurp_log` family — neither path is removed yet, and the binary still links.
  4. Sending a hand-crafted ID-encoded log frame from a Python test fixture into `serial_comm.py` yields a `LogMessage(severity, text)` whose severity matches the catalog category (`OK` / `INIT` / `MAIN` / `END` / `INFO` / `WARN` / `ERROR`) and whose text matches the catalog format string rendered against the supplied param bytes (e.g. a `[u24]` param renders as `0x{:06X}`).
  5. Both sub-repo CI pipelines run codegen and assert `git diff --exit-code` on the generated files; introducing a manual edit to either generated file (without re-running codegen) makes CI fail visibly in the PR.
  6. The host's firmware-version check is wired to refuse a firmware reporting an old (pre-v1.2) major version with an operator-facing "upgrade firmware" message — even though no firmware has bumped its version yet, the host-side guard is in place and unit-tested.
**Plans**: 6 plans
- [x] 06-01-PLAN.md — Catalog + codegen + sync script (meta-repo) + first generated artifacts in both sub-repos
- [x] 06-02-PLAN.md — Firmware `rurp_log_id` helper, CRC8 table, Uno strong override, native Unity test suite
- [x] 06-03-PLAN.md — Host pytest infrastructure + always-on byte-stream reader + `_decode_id_frame` + LHOST-01/02/03 acceptance suite
- [x] 06-04-PLAN.md — Host fw-version refuse guard + `FIRESTARTER_DEV_ALLOW_PRE_V12` escape hatch + 4 unit tests
- [ ] 06-05-PLAN.md — CI drift gates (firmware build.yml modified, host ci.yml new, meta-repo catalog-sync-check.yml new)
- [x] 06-06-PLAN.md — Phase 6 close flash budget measurement (Leonardo + Uno) with fall-back plan

#### Phase 7: Convert ERROR + WARN + INFO Call-Sites
**Goal**: Every firmware ERROR, WARN, and INFO log call-site is emitted via `rurp_log_id` (or the LOG_* macro form) with parameters as raw byte arrays per the catalog. The host renders these frames identically to how the text-format messages used to read in the CLI output. Old log helpers remain present in firmware **only** for the state-machine prefix acks (`OK:` / `INIT:` / `MAIN:` / `END:`), which are still text-formatted at the end of this phase.
**Depends on**: Phase 6 (catalog, codegen, `rurp_log_id` helper, and host decoder must exist before any call-site can be converted; PHASE B of the locked phased migration).
**Requirements**: LMIG-02
**Success Criteria** (what must be TRUE):
  1. A grep across `firestarter/src/`, `firestarter/include/`, and `firestarter/lib/` for the ERROR/WARN/INFO log macros (`log_error_format`, `log_warn`, `log_info_const`, or equivalents) returns zero hits — every former site now calls `rurp_log_id` (directly or via a `LOG_ERROR(MSG_*, ...)` macro).
  2. `firestarter write -e W27C512` (or another canon chip from v1.0) run end-to-end against the firmware-simulator harness produces host-side log output where every ERROR/WARN/INFO line was rendered by the new catalog decoder (verifiable by toggling the decoder off and seeing those specific lines disappear).
  3. The state-machine acks (`OK:` / `INIT:` / `MAIN:` / `END:` / `DATA:`) still flow as **text** at the end of this phase — host parser line-prefix matching for those prefixes is untouched, confirming that this phase is strictly the error/info conversion.
  4. `pio run -e leonardo` and `pio run -e uno` still compile cleanly; the firmware binary size has dropped measurably vs the Phase 6 baseline (record the delta — not yet the milestone target, but the trend must be downward).
**Plans**: TBD

#### Phase 8: Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END)
**Goal**: The firmware emits `OK:` / `INIT:` / `MAIN:` / `END:` state-machine acks as ID-encoded frames via `rurp_log_id`, and the host parser switches from line-prefix matching to ID-frame decoding for those acks. The `DATA:` binary read-payload stream prefix marker remains a literal text prefix (explicitly out of scope per the locked v1.2 constraints). After this phase the only text-formatted log surface left in firmware is the bootstrap `OK: FW: ...` version handshake response (per LFW-05).
**Depends on**: Phase 7 (ERROR/WARN/INFO conversion must already be in place so the host parser only has to migrate one log family at a time; PHASE C of the locked phased migration).
**Requirements**: LMIG-03
**Success Criteria** (what must be TRUE):
  1. A test run of the firmware-simulator harness shows that the only line-prefix-matched messages remaining in the host parser are the `DATA:` binary read-payload stream marker and the bootstrap `OK: FW: ...` version handshake — every other `OK:` / `INIT:` / `MAIN:` / `END:` ack arrives as an ID-encoded frame.
  2. `firestarter write -e W27C512` runs end-to-end and reaches normal completion with the host correctly rendering state-machine progress (INIT phase, MAIN data-transfer phase, END acknowledgement) from ID-frame decoding alone — visible in the host CLI output and indistinguishable in user experience from the pre-v1.2 text-format output.
  3. The `DATA:` binary read-payload stream still works unchanged — `firestarter read -e W27C512 -o out.bin` against the simulator produces a byte-identical binary file vs the pre-Phase-8 baseline (locked constraint: `DATA:` prefix stays text per PROJECT.md "Out for v1.2").
  4. `pio run -e leonardo` and `pio run -e uno` both compile, with the firmware binary size again measurably smaller than the Phase 7 baseline.
**Plans**: TBD

#### Phase 9: Delete Old Log Macros + Measure Flash Savings
**Goal**: All legacy firmware log infrastructure (`rurp_log`, `rurp_log_P`, `LOG_*_MSG` PROGMEM string literals, and the `log_info_const` / `log_error_format` / `log_warn` macros) is deleted from `firestarter/src/`, `firestarter/include/`, and `firestarter/lib/`. The firmware major version bumps to 3.0.0 so old hosts refuse to talk to new firmware (and vice versa). A formal flash-usage measurement is recorded for both Uno and Leonardo, with the Leonardo number compared to the v1.1 baseline of 98.7%.
**Depends on**: Phase 8 (every call-site that used a legacy log helper must already be converted before the helpers can be deleted; PHASE D of the locked phased migration).
**Requirements**: LFW-03, LFW-04, LMIG-04
**Success Criteria** (what must be TRUE):
  1. A grep across `firestarter/src/`, `firestarter/include/`, and `firestarter/lib/` for `PROGMEM` string literals returns only documented exemptions (the `DATA:` prefix marker and any genuinely non-log PROGMEM data such as font tables or constant lookup tables) — every PROGMEM string that existed solely to be passed to a log function is gone, and the list of remaining hits is enumerated in the phase verification artifact.
  2. The legacy log macros (`log_info_const`, `log_error_format`, `log_warn`) and the underlying `rurp_log` / `rurp_log_P` functions are deleted from the codebase — a grep for the symbols returns zero hits in `firestarter/src/` and `firestarter/include/`.
  3. Firmware version handshake reports major version `3.0.0` (or equivalent v1.2 major bump per LFW-05); a host built before Phase 6 trying to talk to this firmware fails with the operator-facing "upgrade firmware" message wired in Phase 6 (regression-tested against the Phase 6 host guard).
  4. `pio run -e leonardo` reports Flash usage **below 90%** with measurable headroom vs the v1.1 baseline of 98.7% — the exact percentage is recorded in the phase verification artifact (e.g. `Leonardo Flash: X% (Y bytes free), down from 98.7%`).
  5. `pio run -e uno` also reports the new Flash usage, recorded alongside the Leonardo number for the milestone-close comparison.
**Plans**: TBD

#### Phase 10: Milestone Close (v1.2)
**Goal**: The v1.2 milestone is formally recorded in `.planning/MILESTONES.md` using the same Key Accomplishments / Stats / Key Decisions / Known Gaps structure as the v1.0 + v1.1 entries, with a dedicated Flash-Savings comparison sub-section that pins the v1.1 baseline (98.7% Leonardo) against the v1.2 post-Phase-9 measurement. PROJECT.md is updated to reflect v1.2 shipped, and any carried-forward v1.1 leftover items are re-listed cleanly in STATE.md for the next milestone slot.
**Depends on**: Phase 9 (the milestone entry summarises what shipped across Phases 6-9 and quotes the Phase 9 final flash-savings number).
**Requirements**: DOC-02
**Success Criteria** (what must be TRUE):
  1. `.planning/MILESTONES.md` contains a v1.2 entry above the v1.0 + v1.1 entries with the canonical sub-sections (Key Accomplishments, Stats, Key Decisions, Known Gaps, Flash-Savings Comparison).
  2. The Flash-Savings Comparison sub-section explicitly quotes the v1.1 baseline (Leonardo 98.7% Flash) and the v1.2 post-Phase-9 number, with the bytes-saved delta and the percentage-point delta both reported.
  3. `.planning/PROJECT.md` "Active milestone" header is updated to reflect v1.2 shipped (with date) and the next milestone slot is open (or v1.1 resumption is noted, per the operator's current intent in STATE.md).
  4. STATE.md is rolled forward — `milestone: v1.2` → next active milestone (or back to v1.1 resumption), open carried-over items (FM1608 hw bug, WARNING-4 test-script drift, v1.1 DOC-01 close) are re-listed cleanly, and `progress.percent` resets for the next milestone.
**Plans**: TBD

### Coverage Map (v1.2)

| Phase | Requirements | Count |
|-------|--------------|-------|
| 6 | LCAT-01, LCAT-02, LCAT-03, LCAT-04, LCAT-05, LFW-01, LFW-02, LFW-05, LHOST-01, LHOST-02, LHOST-03, LHOST-04, LCI-01, LCI-02, LCI-03, LCI-04, LMIG-01 | 17 |
| 7 | LMIG-02 | 1 |
| 8 | LMIG-03 | 1 |
| 9 | LFW-03, LFW-04, LMIG-04 | 3 |
| 10 | DOC-02 | 1 |

**Total v1.2 requirements:** 23 (22 from REQUIREMENTS.md + DOC-02 added by this roadmap under a new "Milestone Close" category)
**Mapped:** 23
**Orphaned:** 0
**Coverage:** 100% ✓

### Dependency Graph (v1.2)

```
Phase 6 (Infrastructure / Phase A)
   │
   ▼
Phase 7 (ERROR/WARN/INFO conversion / Phase B)
   │
   ▼
Phase 8 (State-machine prefix conversion / Phase C)
   │
   ▼
Phase 9 (Delete old macros + measure / Phase D)
   │
   ▼
Phase 10 (Milestone Close)
```

Strictly linear by design: each conversion phase requires the previous phase's infrastructure to be in place, and the Phase 9 delete-and-measure step requires every call-site to have already been migrated. The locked phased migration order (per PROJECT.md "Phased migration" and REQUIREMENTS.md LMIG-01..04) maps 1:1 to Phases 6→9, with Phase 10 closing the milestone.

## Phases (Historical)

<details>
<summary>⏸ v1.1 Safety Closure & Hardware Validation (Phases 1-5) — PAUSED 2026-05-18 at 80%</summary>

- [x] Phase 1: Safety Closure (Intel-flash VPP + 28C chip-ID) — Complete
- [x] Phase 2: Naming Cleanup (Wire Key + Minipro References) — Complete
- [x] Phase 3: Retroactive Verification (Phases 01-10) — Complete (2026-05-12)
- [~] Phase 4: Hardware Validation (RURP shield) — 1/3 plans complete; FM1608 byte-0 hw bug parked
- [ ] Phase 5: Milestone Close — Deferred until v1.2 ships

Full v1.1 roadmap (frozen at pause): `.planning/milestones/v1.1-paused/ROADMAP-at-pause.md`
Carried-forward items in STATE.md: FM1608 hw bug, WARNING-4 test-script drift, DOC-01 milestone close.

</details>

<details>
<summary>✅ v1.0 Protocol-Aware Programming Architecture (Phases 1-13) — SHIPPED 2026-05-11</summary>

- [x] Phase 01: Database Pipeline Fix (3/3 plans) — REQ-DB-01..04
- [x] Phase 02: Firmware JSON Protocol Extension (1/1) — REQ-SER-01, REQ-SER-02
- [x] Phase 03: UV-EPROM Algorithm Correctness (1/1) — REQ-FW-01, REQ-SAF-01
- [x] Phase 04: Flash AMD Sector Erase (2/2) — REQ-FW-04, REQ-SAF-03
- [x] Phase 05: Intel Flash Handler (1/1) — REQ-FW-02
- [x] Phase 06: EEPROM Page Write with DQ7 Polling (1/1) — REQ-FW-03, REQ-SAF-03
- [x] Phase 07: Chip ID Validation & Pre-Write Safety (1/1) — REQ-SAF-01, REQ-SAF-02
- [x] Phase 08: Integration, Rebuild & Verification (1/1) — all
- [x] Phase 09: Hardware Compatibility & Adapter Support (1/1) — REQ-UX-01, REQ-UX-02
- [x] Phase 10: Static Pins, Multi-CE, Address Bus Correctness (1/1) — REQ-FW-05, REQ-FW-06
- [x] Phase 11: Database Pipeline Cleanup (1/1) — REQ-DB-05
- [x] Phase 12: Close BLOCKER-1 + BLOCKER-2 (5/5) — REQ-FW-01, REQ-FW-04, REQ-SER-01
- [x] Phase 13: Close WARNING-5 (3/3) — REQ-FW-03, REQ-SAF-01

Full milestone details: `.planning/milestones/v1.0-ROADMAP.md`

</details>

## Progress

### v1.2 (Current)

| Phase | Plans | Status | Completed |
|-------|-------|--------|-----------|
| 6. Logging Infrastructure (catalog + codegen + helper + decoder) | 0/6 | Not started | - |
| 7. Convert ERROR + WARN + INFO Call-Sites | 0/? | Not started | - |
| 8. Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END) | 0/? | Not started | - |
| 9. Delete Old Log Macros + Measure Flash Savings | 0/? | Not started | - |
| 10. Milestone Close (v1.2) | 0/? | Not started | - |

### v1.1 (Paused at 80%)

| Phase | Plans | Status | Completed |
|-------|-------|--------|-----------|
| 1. Safety Closure (Intel-flash VPP + 28C chip-ID) | 2/2 | Complete | 2026-05-12 |
| 2. Naming Cleanup (Wire Key + Minipro References) | 3/3 | Complete | 2026-05-12 |
| 3. Retroactive Verification (Phases 01-10) | 2/2 | Complete | 2026-05-12 |
| 4. Hardware Validation (RURP shield) | 1/3 | Paused | - |
| 5. Milestone Close | 0/? | Deferred | - |

### v1.0 (Shipped)

| Phase | Milestone | Plans | Status   | Completed  |
| ----- | --------- | ----- | -------- | ---------- |
| 01-13 | v1.0      | 22/22 | Complete | 2026-05-11 |

---

*Roadmap last updated: 2026-05-18 — v1.2 created with 5 phases (6-10), 23 requirements (22 v1.2 + DOC-02 milestone-close), 100% coverage. Phase numbering continues from v1.1's last phase.*

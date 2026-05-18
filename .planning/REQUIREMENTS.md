# Requirements: Firestarter v1.2 — Message-ID Logging Rework

**Defined:** 2026-05-18
**Core Value (carried from PROJECT.md):** Algorithm-first dispatch — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware handler. No guessing.
**Milestone-specific driver:** Free Leonardo flash (currently 98.7% used) AND clean up the firmware↔host log/status protocol by moving format strings from firmware PROGMEM to a host-side catalog keyed by 1-byte message IDs.

> **Status of prior milestones:**
> - v1.0 — Validated, see [`.planning/milestones/v1.0-*.md`]
> - v1.1 — **PAUSED at 80%** on 2026-05-18; original REQUIREMENTS + ROADMAP preserved at [`.planning/milestones/v1.1-paused/`]. Open items (FM1608 byte-0 hw bug, WARNING-4 test-script drift, DOC-01 milestone close) carry forward and will be resolved after v1.2 ships or folded opportunistically.

## v1.2 Requirements

Each requirement maps to exactly one v1.2 roadmap phase (numbering continues from v1.1's last phase: phase 6 onward). v1.0 + open v1.1 requirements are not re-listed here.

### Logging Catalog (canonical source + codegen)

- [x] **LCAT-01**: A single canonical catalog file in the meta-repo (`tools/catalog/messages.toml`) declares every firmware log message as `{id, symbolic_name, format_string, parameter_shape}`. The file is the source of truth — no message exists in firmware or host code without an entry here.
- [x] **LCAT-02**: Catalog validation enforces: unique 1-byte IDs (0–255), unique symbolic names, well-formed parameter shapes (each param has a type: `u8` / `u16` / `u24` / `u32` / `i8` / `i16` / `i32`), and a non-empty format_string. Validation runs as part of codegen and fails the build on violation.
- [x] **LCAT-03**: A codegen script (in `tools/` or equivalent) produces a C++ header (e.g. `firestarter/include/messages.h`) containing the message-ID enum + symbolic name constants + a `MSG_PARAM_COUNT(id)` helper, deterministically from the canonical catalog.
- [x] **LCAT-04**: The same codegen script produces a Python module (e.g. `firestarter_app/firestarter/messages.py`) containing the ID → format-string + parameter-shape lookup, deterministically from the canonical catalog.
- [x] **LCAT-05**: Codegen output is byte-identical when run twice on the same input (no timestamps, no ordering instability, no unstable hashes). This is the property the CI drift gate relies on.

### Logging Firmware-side

- [x] **LFW-01**: A `rurp_log_id(uint8_t msg_id, const uint8_t* params, uint8_t param_count)` helper exists in firmware and replaces the existing `rurp_log(LOG_*_MSG, char*)` family. It sends the wire frame for an ID-encoded log message over `SERIAL_PORT` per the wire-format agreed in phase planning (a binary frame distinguishable from `DATA:` binary payload).
- [x] **LFW-02**: Convenience macros / inline helpers exist so that idiomatic call-sites (e.g. `LOG_INFO(MSG_VPP_OK)` with no params, or `LOG_ERROR(MSG_BAD_VPP, vpp_mv_value)` with one u16 param) are no more verbose than the current `log_info_const` / `log_error_format` macros they replace.
- [ ] **LFW-03**: All firmware log call-sites that today use `OK:` / `INIT:` / `MAIN:` / `END:` / `INFO:` / `WARN:` / `ERROR:` PROGMEM strings are converted to `rurp_log_id` (or the LOG_* macro form). Every former format-string is represented as a single entry in the canonical catalog.
- [ ] **LFW-04**: After conversion, `firestarter/src/`, `firestarter/include/`, and `firestarter/lib/` contain zero PROGMEM string literals that exist only to be passed to a log function. (`DATA:` prefix marker and any non-log PROGMEM strings are exempt and noted explicitly.)
- [x] **LFW-05**: Firmware version handshake bumps the major version (e.g. `3.0.0`) so the host's version check rejects mismatched-format firmware cleanly. The `OK: FW: ...` response message itself stays text-formatted (this single message is required to bootstrap the version check before the ID catalog is loaded).

### Logging Host-side

- [x] **LHOST-01**: `firestarter_app/firestarter/serial_comm.py` parses incoming ID-encoded log frames using the generated `messages.py` catalog: reads 1-byte ID, reads N bytes of params per the declared shape, and yields a `LogMessage(severity, text)` for downstream display.
- [x] **LHOST-02**: The formatter renders parameters into the format_string using the declared types — e.g. `[u16]` rendered as the integer value, `[u24]` rendered as a 6-hex-digit address (`0x{:06X}`). Rendering rules are part of the catalog (per-param: integer / hex / decimal / signed / ascii-char).
- [x] **LHOST-03**: The host's existing log severity routing (`logger.warning`, `logger.error`, etc. per current `_log_rurp_feedback`) is preserved — severity is derived from the catalog entry's category (`OK` / `INIT` / `MAIN` / `END` / `INFO` / `WARN` / `ERROR` / `DATA`), and the host logger receives the formatted human-readable line.
- [x] **LHOST-04**: The host's fw-version check refuses to talk to firmware older than v1.2's major bump (per LFW-05). Error message instructs the operator to upgrade firmware. No fallback to old text-protocol parsing.

### Logging CI / Build integration

- [x] **LCI-01**: The firmware sub-repo (`firestarter/`) has a CI step that runs codegen (regenerates `messages.h` from canonical catalog) and asserts no `git diff` on the generated file. Drift fails the CI run.
- [x] **LCI-02**: The host sub-repo (`firestarter_app/`) has the equivalent CI step for `messages.py`. Drift fails CI.
- [x] **LCI-03**: Both sub-repo builds (`pio run`, `pip install -e .` test paths) run codegen before compile/test, so a developer who edits the canonical catalog locally sees the updated generated files appear in their working tree.
- [x] **LCI-04**: Catalog validity (LCAT-02) is checked as part of codegen and CI; an invalid catalog file fails both local builds and CI before any source generation happens.

### Logging Migration

- [x] **LMIG-01**: **Phase A (infrastructure-only)**: catalog + codegen + `rurp_log_id` helper + host decoder all land in a single phase, without removing any existing log code. Firmware compiles and links with both old `rurp_log(LOG_*_MSG, ...)` and new `rurp_log_id(...)` paths available. Old hosts continue working against unchanged firmware behavior.
- [x] **LMIG-02**: **Phase B (error + info conversion)**: firmware ERROR + WARN + INFO log call-sites are converted to `rurp_log_id` form. Each batch commits separately by call-site cluster (one PROM module at a time). Old log helpers still present for OK/INIT/MAIN/END prefixes.
- [ ] **LMIG-03**: **Phase C (state-machine prefix conversion)**: `OK:` / `INIT:` / `MAIN:` / `END:` call-sites are converted. Host parser switches from line-prefix matching to ID-frame decoding for state-machine acks. **`DATA:` prefix marker remains as literal text** (gates the host's binary read loop and is not changed in v1.2).
- [ ] **LMIG-04**: **Phase D (delete + measure)**: Old `rurp_log` / `rurp_log_P` / `LOG_*_MSG` PROGMEM definitions and `log_info_const` / `log_error_format` / `log_warn` macros are removed. `pio run -e leonardo` produces a final flash-savings number documented in the milestone close. Target: bring Leonardo flash below 90% with measurable headroom.

### Milestone Close

- [ ] **DOC-02**: The v1.2 milestone is formally recorded in `.planning/MILESTONES.md` with the canonical sub-sections (Key Accomplishments, Stats, Key Decisions, Known Gaps) **plus a dedicated Flash-Savings Comparison sub-section** that pins the v1.1 baseline (98.7% Leonardo Flash) against the v1.2 post-Phase-9 measurement (target: <90%). PROJECT.md "Active milestone" header updates to reflect v1.2 shipped; STATE.md rolls forward with any carried-over v1.1 items re-listed cleanly. (Mirrors the v1.1 DOC-01 milestone-close requirement.)

## v2 Requirements (deferred)

### Logging extensions

- **LMIG-05** (future): Compress the `DATA:` prefix marker too. Saves ~5 bytes per read chunk on the wire. Requires reworking the host's binary read-loop parser.
- **LCAT-06** (future): Catalog versioning — allow multiple catalog versions to coexist for backwards compatibility (would have prevented the lockstep upgrade requirement). Not needed for v1.2 since operator upgrades firmware + host together.
- **LCAT-07** (future): Localization support — allow multiple format strings per ID indexed by locale.

## Out of Scope (v1.2 explicit exclusions)

| Feature | Reason |
|---------|--------|
| Backwards compatibility with text-format firmware | Operator upgrades firmware + host together; firmware major-version bump enforces |
| `DATA:` binary payload stream changes | Already raw binary after the prefix; only the prefix marker would change and it's not worth the parser churn for ~5 bytes per chunk |
| Localization (non-English catalog) | Operators are technical; no localization roadmap |
| 2-byte IDs / variable-length IDs | Current message count is well under 100; 1-byte (256) gives 2.5x headroom |
| Typed parameters with on-wire type tags | Param shapes are catalog-declared; no need for self-describing parameters on the wire |
| Embedding the catalog in firmware PROGMEM | Defeats the flash-savings goal |
| v1.1 leftover items (FM1608 hw bug, WARNING-4, milestone close) | Carried in STATE; resumed after v1.2 ships |

## Traceability

Each requirement maps to exactly one v1.2 phase. Phase numbering continues from v1.1 (so v1.2 starts at Phase 6).

| Requirement | Phase | Status |
|-------------|-------|--------|
| LCAT-01 | Phase 6 | Complete |
| LCAT-02 | Phase 6 | Complete |
| LCAT-03 | Phase 6 | Complete |
| LCAT-04 | Phase 6 | Complete |
| LCAT-05 | Phase 6 | Complete |
| LFW-01  | Phase 6 | Complete |
| LFW-02  | Phase 6 | Complete |
| LFW-03  | Phase 9 | Pending |
| LFW-04  | Phase 9 | Pending |
| LFW-05  | Phase 6 | Complete |
| LHOST-01 | Phase 6 | Complete |
| LHOST-02 | Phase 6 | Complete |
| LHOST-03 | Phase 6 | Complete |
| LHOST-04 | Phase 6 | Complete |
| LCI-01  | Phase 6 | Complete |
| LCI-02  | Phase 6 | Complete |
| LCI-03  | Phase 6 | Complete |
| LCI-04  | Phase 6 | Complete |
| LMIG-01 | Phase 6 | Complete |
| LMIG-02 | Phase 7 | Complete |
| LMIG-03 | Phase 8 | Pending |
| LMIG-04 | Phase 9 | Pending |
| DOC-02  | Phase 10 | Pending |

**Coverage (post-roadmap):**
- v1.2 requirements: 23 total (5 LCAT + 5 LFW + 4 LHOST + 4 LCI + 4 LMIG + 1 DOC milestone-close)
- Mapped to phases: 23
- Unmapped: 0 ✓
- Coverage: **100% ✓**

**Per-phase coverage:**

| Phase | Name | Requirement count | Requirements |
|-------|------|-------------------|--------------|
| 6 | Logging Infrastructure (catalog + codegen + helper + decoder) | 17 | LCAT-01..05, LFW-01, LFW-02, LFW-05, LHOST-01..04, LCI-01..04, LMIG-01 |
| 7 | Convert ERROR + WARN + INFO Call-Sites | 1 | LMIG-02 |
| 8 | Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END) | 1 | LMIG-03 |
| 9 | Delete Old Log Macros + Measure Flash Savings | 3 | LFW-03, LFW-04, LMIG-04 |
| 10 | Milestone Close (v1.2) | 1 | DOC-02 |

---

*Requirements defined: 2026-05-18*
*Last updated: 2026-05-18 — Traceability populated (5 phases, 23 requirements, 100% coverage); DOC-02 added under new "Milestone Close" category by the roadmapper.*

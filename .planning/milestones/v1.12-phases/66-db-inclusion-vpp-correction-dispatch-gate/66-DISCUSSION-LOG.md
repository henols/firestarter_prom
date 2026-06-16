# Phase 66: DB Inclusion + VPP Correction + Dispatch Gate - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-12
**Phase:** 66-db-inclusion-vpp-correction-dispatch-gate
**Areas discussed:** Inclusion discriminator, VPP correction encoding, support_status schema, Gate & baseline reconciliation

---

## Inclusion discriminator (DB-01)

### Q1 — How to decide which dropped chips get included vs stay skipped

| Option | Description | Selected |
|--------|-------------|----------|
| Re-audit per family | Researcher re-classifies each dropped family + form factor; include only confirmed DIP-parallel memory; serial/PLCC/SMD/adapter stay skipped | ✓ |
| Trust the DIP filter as-is | Include all 24 dropped chips; wrongly lists AT45 SPI DataFlash + PLCC-only parts | |
| Tighten filter, then include all | Make filter alias-aware, then include everything that survives | |

**User's choice:** Re-audit per family
**Notes:** The coarse DIP filter leaks `@SOIC28`/`@PLCC32` aliases. `X88C64@DIP24` (proto 0x34) is a genuine DIP parallel EEPROM the research FEATURES.md table under-counted — flagged as the consistency case the re-audit must catch.

### Q2 — Scope of the 9 damage-hazard-skipped 24-pin EEPROMs

| Option | Description | Selected |
|--------|-------------|----------|
| Out of scope — Phase 67 | Leave the 9 skipped; adapter work is Phase 67/DB-02 | |
| Include as adapter-required now | Pull the 9 into Phase 66 as support_status:adapter-required | ✓ |
| Include as vpp/hazard-skip flag | New 5th status value outside locked taxonomy | |

**User's choice:** Include as adapter-required now
**Notes:** Expands Phase 66 into the adapter taxonomy. Constrained by milestone "no new chips programmable" → flag only, do NOT unblock. Reconciliation needed: v1.11's partial DIP24_6116+0x0D unblock skipped these 9; researcher must confirm each is genuinely flag-only.

---

## VPP correction encoding (DB-03)

### Q1 — How to encode the curated NMOS high-VPP exception list

| Option | Description | Selected |
|--------|-------------|----------|
| Inline dict in build_db.py | Module-level dict matched against aliases, post-decode override; matches WARNING-5/fm1608 idiom | ✓ |
| External data file | JSON/TOML exceptions file; reintroduces removed database_overrides.json | |
| Match by chip_id_value | Key on upstream chip_id; may not discriminate NMOS vs CMOS | |

**User's choice:** Inline dict in build_db.py

### Q2 — Faithfulness when an NMOS part is aliased inside a generic CMOS-sharing entry

| Option | Description | Selected |
|--------|-------------|----------|
| Key-and-correct, don't split | Record true VPP on the entry as-is; no new entries | ✓ |
| Split into separate entries | Emit distinct NMOS + CMOS entries | |
| Correct only sole-identity entries | Leave mixed entries at 18V with a note | |

**User's choice:** Key-and-correct, don't split
**Notes:** Status-derivation rule (record true VPP; > ~22V ceiling → vpp-exceeds-max; ≤ → supported) already locked by ROADMAP/REQUIREMENTS; exact ceiling + curated list membership deferred to plan time.

---

## support_status schema (DB-01/03/05)

### Q1 — Every chip vs only non-supported entries

| Option | Description | Selected |
|--------|-------------|----------|
| Every chip (explicit) | All 743 entries get support_status; uniform + always-queryable; one-time uniform diff | ✓ |
| Only non-supported (sparse) | Absence == supported; minimal churn; downstream must default | |

**User's choice:** Every chip (explicit)

### Q2 — Field placement in the entry JSON

| Option | Description | Selected |
|--------|-------------|----------|
| Top-level keys | Siblings of electrical/programming/pinout; simplest for consumers | ✓ |
| Nested capability object | capability:{status,reason}; adds a nesting level | |

**User's choice:** Top-level keys

### Q3 — Pinout value for an included non-supported chip (Phase 67 owns classification)

| Option | Description | Selected |
|--------|-------------|----------|
| Whatever resolve_pinout_key returns | Best-effort/fallback; inert because non-dispatchable; Phase 67 refines | ✓ |
| Placeholder (Unknown/null) | Explicit non-trustworthy signal; introduces a sentinel consumers must tolerate | |

**User's choice:** Whatever resolve_pinout_key returns

---

## Gate & baseline reconciliation (DB-05)

### Q1 — How check_dispatch.py treats non-supported entries

| Option | Description | Selected |
|--------|-------------|----------|
| Exclude + consistency-assert | Non-supported exempt from safety checks; add consistency assertions; not_implemented PASS-if-flagged; host-refusal layer owns hazard prevention | ✓ |
| Apply safety checks to all | Run checks on all with expected/FAIL partitioning; more complex | |

**User's choice:** Exclude + consistency-assert

### Q2 — Baseline reconciliation

| Option | Description | Selected |
|--------|-------------|----------|
| Regenerate as authorized deviation | Regenerate affected baseline(s), review diff in plan/commit (v1.11 D-01/D-02 precedent) | ✓ |
| Append-only / allowlist | Leave baseline untouched; gate tolerates new entries; can mask regressions | |

**User's choice:** Regenerate as authorized deviation
**Notes:** Phase-62 dispatch_baseline excludes vpp_mv by design → churns only from new included chips, not VPP corrections.

---

## Claude's Discretion

- Exact enum string values + `unsupported_reason` wording (taxonomy strings locked; phrasing flexible).
- Placement of new build_db.py inclusion logic relative to existing drop gates/overrides (must run after WARNING-5/fm1608 overrides).
- Shape of new check_dispatch.py consistency assertions + FAIL message format (mirror existing idiom).

## Deferred Ideas

- Pinout classification for unclassifiable chips → Phase 67 (DB-02).
- Host capability display + refusal messages → Phase 68 (DB-04).
- Making any flagged chip programmable / 24-pin EEPROM firmware handler / high-VPP hardware → future hardware-gated milestones.
- Erase-command firmware support for 0x07-path EEPROMs → separate firmware backlog.

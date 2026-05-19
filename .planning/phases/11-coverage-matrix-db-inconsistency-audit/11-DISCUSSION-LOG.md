# Phase 11: Coverage Matrix & DB Inconsistency Audit - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-19
**Phase:** 11-coverage-matrix-db-inconsistency-audit
**Areas discussed:** Generator artifact, Output structure + DB-drift handling, BENCH coverage proof depth, Inconsistency taxonomy & defect IDs

---

## Generator artifact

| Option | Description | Selected |
|--------|-------------|----------|
| Committed Python tool | New firestarter_app/tools/audit_coverage_matrix.py — reuses EpromDatabase loader, mirrors the style of tools/check_dispatch.py. Re-runnable when DB regenerates from infoic.xml. Writes both the matrix and the inconsistency report as markdown. Committed to firestarter_app/ sub-repo. | ✓ |
| One-shot ad-hoc script | Script lives in /tmp or under .planning/scratch/ during phase work; outputs are committed but the generator is not. Cheaper, but matrix decays the moment the DB regenerates. | |
| Hand-written markdown | No code — operator+Claude assemble the matrix from manual DB inspection. 341 rows is large but doable. Maximally readable, zero re-runnability. | |

**User's choice:** Committed Python tool.
**Notes:** Locks the matrix to a re-runnable artifact mirroring `check_dispatch.py`. Idempotence and exit-code discipline added by Claude (D-02 / D-03) to keep the tool CI-ready for a future drift gate.

---

## Output structure + DB-drift handling

Discussed in three sub-questions.

### File layout

| Option | Description | Selected |
|--------|-------------|----------|
| Two files, paired | `.planning/v1.3-COVERAGE-MATRIX.md` + `.planning/v1.3-DB-INCONSISTENCIES.md`. Generator emits both atomically; planning docs link them. Cleaner separation for v1.4 backlog grooming. | |
| Single combined file | Everything in `.planning/v1.3-COVERAGE-MATRIX.md` with sections: summary stats → full enumeration → inconsistencies → BENCH proof. One scroll for the operator. | ✓ |
| Three files | Matrix + inconsistencies + a separate BENCH-COVERAGE-PROOF.md. Granular but more cross-linking burden. | |

**User's choice:** Single combined file.

### Main grouping inside the matrix table

| Option | Description | Selected |
|--------|-------------|----------|
| By pinout class then size | Algorithm → pinout class → size_bytes asc → manufacturer alpha. Best for spotting pulse_duration / chip_id_check variance within a pinout class. | ✓ |
| By size then manufacturer | Algorithm → size_bytes asc → manufacturer. Best for address-bus-span auditing but spreads pinout variance across the table. | |
| Flat alphabetical | Single sorted table by manufacturer → part_number. Easiest to grep, hardest to spot clustering. | |

**User's choice:** By pinout class then size.

### DB-count drift handling (734 vs 743; 212 vs 214; 341 vs 339)

| Option | Description | Selected |
|--------|-------------|----------|
| Surface as finding, fix docs in Phase 14 | Phase 11 records actual counts + flags drift section. Phase 14 sweeps the corrections into PROJECT.md/ROADMAP.md/REQUIREMENTS.md. Keeps Phase 11 strictly read-only. | |
| Fix in Phase 11 alongside matrix | Phase 11 plan includes a small task that updates PROJECT.md/ROADMAP.md/REQUIREMENTS.md to live numbers. Single commit. Matrix + docs ship aligned. | ✓ |
| Note only; never fix | Matrix shows true counts. Planning docs keep their pre-v1.3 numbers as historical record. No reconciliation. | |

**User's choice:** Fix in Phase 11 alongside matrix.
**Notes:** Locked the matrix-tool to write a "DB Count Reconciliation" section that re-derives the deltas on every run — so future regens stay honest (D-08).

---

## BENCH coverage proof depth

Discussed in two sub-questions.

### Proof rigor

| Option | Description | Selected |
|--------|-------------|----------|
| Per-axis coverage tables | Three tables in the matrix: pinout-class coverage, pulse-duration bucket coverage, size/address-bus-span coverage. Each uncovered cell called out explicitly. | ✓ |
| One coverage summary table | Single "BENCH chip → axes exercised" table. Lightweight; gaps visible but not enumerated cell-by-cell. | |
| Narrative paragraph only | Short prose pulled from REQUIREMENTS.md. No new tables. Minimum effort. | |

**User's choice:** Per-axis coverage tables.

### Uncovered pinout classes (DIP28_28C64, DIP28_28C256)

| Option | Description | Selected |
|--------|-------------|----------|
| Flag as defect candidates, exclude from BENCH proof | These 42 rows go into the inconsistency section as a class-level defect candidate; BENCH proof explicitly notes "out of scope — see DEFECT-COV-N". | |
| Recommend BENCH-05/06 swap | Recommend Phase 12 re-select BENCH-05 to cover DIP28_28C64 instead of (or in addition to) the 32K UV-EPROM rep. Higher coverage but pulls more weight into BENCH-05 selection. | |
| Flag and let Phase 12 decide | Matrix flags the uncovered pinouts; Phase 12 CONTEXT.md owns the actual BENCH selection. Phase 11 stays strictly observational. | ✓ |

**User's choice:** Flag and let Phase 12 decide.
**Notes:** Establishes a clean boundary — Phase 11 inputs into Phase 12's selection rather than pre-empting it (D-11).

---

## Inconsistency taxonomy & defect IDs

Discussed in two sub-questions.

### Severity classification

| Option | Description | Selected |
|--------|-------------|----------|
| Three severity tiers | HAZARD / CORRECTNESS / VARIANCE — safety vs programming-correctness vs cosmetic. Each finding tagged. v1.4 prioritises HAZARD first. | ✓ |
| Two tiers | BLOCKING vs INFORMATIONAL. Simpler, less guidance for v1.4 triage. | |
| Flat list | No severity. Each inconsistency stands on its own; operator triages in v1.4. | |

**User's choice:** Three severity tiers.

### Stable IDs

| Option | Description | Selected |
|--------|-------------|----------|
| DEFECT-COV-NN with metadata | Each finding gets a sequential ID + per-finding metadata (severity, affected count, root-cause hypothesis, suggested fix venue). Stable across DB regenerations via a small ID ledger. v1.4 / sub-repo PRs reference by ID. | ✓ |
| Anonymous enumeration | Numbered list regenerated each run; no stable IDs. Metadata still per-finding but no stable handle. | |
| Hybrid: stable IDs for HAZARD only | HAZARD-tier findings get DEFECT-COV-NN IDs. CORRECTNESS / VARIANCE enumerated. Compromise. | |

**User's choice:** DEFECT-COV-NN with metadata.
**Notes:** Introduced the `.planning/v1.3-defect-coverage-ids.json` ledger (D-13) so a v1.4 sub-repo PR can still reference `DEFECT-COV-07` after the DB regenerates. Resolved-baseline finding `DEFECT-COV-00 — RESOLVED in v1.0 Phase 13 WARNING-5` carries continuity (D-15).

---

## Claude's Discretion

The operator did not lock the following — researcher / planner propose concrete choices grounded in Phase 11's scope and proceed without re-asking. Captured in CONTEXT.md `<decisions> → Claude's Discretion`:

- **Exact pulse-duration bucket boundaries** for the §5 coverage table (Claude proposes `<100 µs / 100–999 µs / 1–9 ms / 10–99 ms / 100 ms–1 s`).
- **Markdown table width / split** in §3 Full Enumeration (Claude proposes split per-algorithm).
- **Ledger file format** for stable defect IDs (Claude proposes a JSON dict keyed by finding-hash).
- **Root-cause attribution for the 743→734 drift** (Claude proposes a short note, no archaeology).
- **Commit cadence / wave structure** for the executor (Claude proposes 5 waves: tool skeleton → enumeration → defects + ledger → BENCH proof → planning-doc reconciliation).

## Deferred Ideas

- Auto-fixes against `chip_database.json` / `build_db.py` — explicit out of scope per REQUIREMENTS.md COV-02.
- BENCH-05 / BENCH-06 chip swap to cover DIP28_28C64 / DIP28_28C256 — Phase 12 CONTEXT.md decides.
- CI wiring of `audit_coverage_matrix.py` as a drift gate — exit-code discipline is in place; CI hookup is a later milestone.
- Upstream minipro PRs against `infoic.xml` classification errors — v1.4+.
- Coverage matrix for the other 9 algorithms (0x05/0x06/0x0B/0x0D/0x0E/0x10/0x27/0x28/0x29/0x35/0x39) — follow-on milestone; same tool, drop the algo filter.
- HTML / dashboard rendering of the matrix — much later milestone.

---
phase: 11-coverage-matrix-db-inconsistency-audit
plan: 04
subsystem: testing
tags: [python, pytest, audit-tool, defect-ledger, sha1-hashing, codegen, idempotence, markdown-rendering, chip-database]

# Dependency graph
requires:
  - phase: 11
    provides: "Wave 2 §3 enumeration + sort_key + Wave 1 tool skeleton (11-03 / 11-02)"
provides:
  - "§4 DB Inconsistencies / Defect Candidates emit — HAZARD-first tier order (D-12) with 1 HAZARD + 27 CORRECTNESS + 49 VARIANCE live findings + DEFECT-COV-00 RESOLVED baseline"
  - "Pattern C stable defect-ID composition: 16-hex-truncated sha1(canonical-JSON({severity, axis, signature})) → DEFECT-COV-NN mapping persisted in .planning/v1.3-defect-coverage-ids.json"
  - "DEFECT-COV-00 RESOLVED baseline citing v1.0 Phase 13 WARNING-5 override predicate verbatim from build_db.py:415-423"
  - "DEFECT-COV-01: the new HAZARD finding — 42-row cluster (35 DIP28_28C64 + 7 DIP28_28C256) on algo-0x07 where WARNING-5 predicate is structurally unreachable because build_db.py:481-486 re-derives _etype = UV-EPROM after the override fires"
  - "--check flag full semantics (D-03): dry-run drift gate; returns 1 if any detected finding hash is absent from the on-disk ledger or DEFECT-COV-00 is absent; does NOT mutate the ledger"
  - "Three Wave-3 tests green: test_hazard_cluster_42_rows, test_ledger_idempotent, test_ledger_id_reuse + extended test_exit_codes with 3 returncode sub-cases"
affects:
  - "11-05 (Wave 4 — bench coverage proof): consumes the §4 finding inventory to cross-reference uncovered cells in the §5 per-axis tables"
  - "11-06 (Wave 5 — planning-doc reconciliation): treats DEFECT-COV-NN IDs as the stable vocabulary for v1.4 follow-up PRs"
  - "v1.4 build_db.py PR queue: DEFECT-COV-01 needs an override-class extension (drop _etype == Flash/EEPROM clause OR add a new pinout-keyed override)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pattern C (PATTERNS.md): sha1(canonical-JSON of {severity, axis, list(signature)})[:16] hash composition"
    - "next_n_holder list-as-mutable-counter (RESEARCH.md Code Examples 609-619) for cross-call ID minting"
    - "Tier-first / hash-ascending output sort (D-12) for stable §4 rendering"
    - "Dry-run drift gate (D-03): --check copies the on-disk ledger into memory, runs detection, exits 1 if any finding hash is absent — never mutates the on-disk file"

key-files:
  created:
    - ".planning/phases/11-coverage-matrix-db-inconsistency-audit/11-04-SUMMARY.md"
    - ".planning/v1.3-defect-coverage-ids.json"
  modified:
    - "firestarter_app/tools/audit_coverage_matrix.py — +468 lines: finding_hash, load_ledger, save_ledger, mint_or_reuse, detect_resolved_baseline, detect_hazard, detect_correctness, detect_variance, emit_defects; wired into generate_matrix; --check now compares in-memory findings against on-disk ledger; §1 TBD severity-tier placeholders replaced with live counts"
    - "firestarter_app/tests/test_audit_coverage_matrix.py — +150 / -42 lines: three Wave-3 NotImplementedError stubs replaced with real test bodies; test_exit_codes extended with the empty-ledger drift-gate sub-case; subprocess.run calls gain explicit check=False kwarg"
    - ".planning/v1.3-COVERAGE-MATRIX.md — §4 populated (DEFECT-COV-00 RESOLVED + DEFECT-COV-01..77 live); §1 severity-tier counts populated (1 HAZARD / 27 CORRECTNESS / 49 VARIANCE)"

key-decisions:
  - "DEFECT-COV-00 signature uses the PRE-rederive _etype value (Flash/EEPROM) because that is what WARNING-5 predicate observes at predicate time (build_db.py:415-417). The new HAZARD finding (DEFECT-COV-01) uses the POST-rederive value (UV-EPROM) because that is the substrate the detector sees in the rendered DB. Two distinct hashes → two distinct IDs."
  - "CORRECTNESS clusters split by per-(manufacturer, first_alias) signature so multi-vendor pulse outliers in the same (algo, pinout, size) bucket render as separate DEFECT-COV-NN entries — D-14 schema."
  - "VARIANCE chip_id_value_drift considers only members with chip_id_check=True; values for chip_id_check=False members are not part of the cluster identity (the firmware never reads them)."
  - "DEFECT-COV-00 is reserved; live mints start at NN=01. next_n_holder seeded at max(existing_NN, 0) + 1 so pre-seeded high IDs (e.g. DEFECT-COV-99 in a manually edited ledger) survive without collision."
  - "--check seeds DEFECT-COV-00 into an in-memory ledger copy before comparing; this prevents a one-shot false drift on first --check against a populated-but-baseline-less ledger from a prior partial write."

patterns-established:
  - "Hash composition uses list(signature) coercion so tuples (the natural Python shape) round-trip cleanly through json.dumps. The signature shape for HAZARD pinout_vs_algorithm is (list-of-pinout-strings, algorithm-int, etype-string) — three positional elements."
  - "Test hashes are NEVER hard-coded literals; test_ledger_id_reuse computes the HAZARD hash live from detect_hazard() + iter_in_scope_rows() against the real DB (Pitfall 5)."

requirements-completed: [COV-02]

# Metrics
duration: 6min
completed: 2026-05-19
---

# Phase 11 Plan 04: Coverage Matrix §4 Defect Findings + DEFECT-COV Ledger Summary

**Wave-3 §4 emit lands: 1 HAZARD (the 42-row WARNING-5-unreachable cluster) + 27 CORRECTNESS + 49 VARIANCE live findings, anchored by the DEFECT-COV-00 RESOLVED baseline citing build_db.py:415-423 verbatim, with a 78-entry ledger that survives DB regenerations via 16-hex-truncated-sha1 stable hashes.**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-05-19T22:18:41Z
- **Completed:** 2026-05-19T22:25:00Z (approx)
- **Tasks:** 3
- **Files modified:** 4 (1 tool, 1 test, 1 generated matrix, 1 generated ledger)

## Accomplishments

- §4 DB Inconsistencies / Defect Candidates emit added to `audit_coverage_matrix.py` — tier-first order (HAZARD → CORRECTNESS → VARIANCE per D-12), hash-ascending within tier for stable rendering, DEFECT-COV-00 RESOLVED block emitted first.
- DEFECT-COV-00 RESOLVED baseline quotes the WARNING-5 override predicate verbatim from `build_db.py:415-423` as a fenced Python code block so the audit narrative is self-contained.
- DEFECT-COV-01 detects the new HAZARD: the 42-row cluster (35 `DIP28_28C64` + 7 `DIP28_28C256`) on algo-0x07 where WARNING-5 is structurally unreachable because `build_db.py:481-486` rewrites `_etype` to "UV-EPROM" after the override predicate evaluates.
- 27 CORRECTNESS findings detected — per-vendor pulse_duration outliers (>=10x cluster median), notable: FUJITSU/MB85R256H at 100us vs cluster median 1s (DEFECT-COV-13), confirming the FRAM-mis-classified-as-28C256 signal documented in RESEARCH.md.
- 49 VARIANCE findings — chip_id_check toggles + chip_id_value drift across (algo, pinout, size, manufacturer) clusters.
- Stable 16-hex-truncated-sha1 hash composition (Pattern C) backs every ID. Ledger at `.planning/v1.3-defect-coverage-ids.json` is sorted-keys JSON with trailing newline — byte-identical across runs.
- `--check` flag now implements D-03 dry-run drift semantics: exit 1 if any detected finding hash is absent from the on-disk ledger; exit 0 if all present; never mutates the ledger.
- §1 severity-tier counts populated with live numbers (1 HAZARD / 27 CORRECTNESS / 49 VARIANCE) — Wave 1 TBD placeholder removed.
- 8 of 10 tests now green; only Wave 4 stubs (`test_bench_coverage_proof`, `test_golden_file_matches`) remain — both will land in Plan 11-05.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add defect detection + ledger mint/reuse + §4 emit + --check semantics to tool** — `firestarter_app@0e2faf7` (feat)
2. **Task 2: Implement test_hazard_cluster_42_rows + test_ledger_idempotent + test_ledger_id_reuse; extend test_exit_codes** — `firestarter_app@37d6be9` (test)
3. **Task 3: Regenerate matrix + ledger; commit to .planning/** — `e819d11` (docs, parent repo)

## Files Created/Modified

- `firestarter_app/tools/audit_coverage_matrix.py` — added `finding_hash`, `load_ledger`, `save_ledger`, `mint_or_reuse`, `detect_resolved_baseline`, `_examples_for`, `detect_hazard`, `detect_correctness`, `detect_variance`, `emit_defects`; wired into `generate_matrix`; rewrote `--check` block to be a real drift gate; `emit_summary` accepts optional `severity_counts` kwarg and renders live tier totals when provided; `emit_placeholder_sections` now returns just §5.
- `firestarter_app/tests/test_audit_coverage_matrix.py` — three Wave-3 test bodies replace `NotImplementedError` stubs; `test_exit_codes` extended with empty-ledger drift-gate sub-case; subprocess calls now use explicit `check=False`.
- `.planning/v1.3-COVERAGE-MATRIX.md` — regenerated; §4 now contains DEFECT-COV-00 RESOLVED + DEFECT-COV-01 (HAZARD-42-row) + 26 CORRECTNESS entries + 49 VARIANCE entries; §1 severity-tier counts populated.
- `.planning/v1.3-defect-coverage-ids.json` — NEW (78 entries: DEFECT-COV-00 baseline + DEFECT-COV-01..77 live mints); sorted keys; trailing newline.

## Decisions Made

- **Two distinct hashes for the WARNING-5 HAZARD evidence:** DEFECT-COV-00 (RESOLVED) and DEFECT-COV-01 (new). The plan's `<interfaces>` block calls these out as separate findings — DEFECT-COV-00's signature uses `_etype = "Flash/EEPROM"` (the PRE-rederive value the predicate observes at gate time), and DEFECT-COV-01 uses `_etype = "UV-EPROM"` (the POST-rederive value the detector sees). Same physical cluster of chips; two distinct stable IDs, two distinct narrative angles (the v1.0 fix vs. the v1.4 gap).
- **CORRECTNESS findings split per-(manufacturer, first_alias).** D-14's signature schema for `pulse_duration_outlier` is the 5-tuple `(algorithm, pinout, size_bytes, manufacturer, first_alias)`. Multi-vendor outliers in the same (algo, pinout, size) cluster therefore render as separate `DEFECT-COV-NN` entries — more granular, more actionable than one cluster-level lump. The 27 CORRECTNESS findings would have been ~11 cluster-level findings under a looser signature.
- **VARIANCE chip_id_value_drift filters to chip_id_check=True members only.** A cluster member with `chip_id_check=False` does not actually exercise the chip_id readout path in firmware; its `chip_id_value` is documentation-only metadata and not part of the cluster's effective identity contract.
- **--check seeds DEFECT-COV-00 into an in-memory ledger copy before the drift comparison.** Otherwise a fresh ledger that has been partially seeded but not yet emitted (or that was hand-trimmed) would trip the drift gate on every run. The seed is in-memory only — the on-disk ledger is never mutated under `--check`.
- **Hash signatures coerce tuples to lists.** `json.dumps` cannot serialize tuples natively (it emits them as lists, but mixed tuple/list keys would produce different `json.dumps` output for the SAME signature). Coercing every signature element to a list at hash time guarantees that a caller passing a tuple and a caller passing the equivalent list produce the SAME 16-hex hash → same DEFECT-COV-NN.

## Deviations from Plan

None — plan executed exactly as written. All acceptance criteria met:

- 8 named functions (`finding_hash`, `mint_or_reuse`, `detect_hazard`, `detect_correctness`, `detect_variance`, `emit_defects`, `load_ledger`, `save_ledger`) present in tool — verified via `grep -cE "^def (...)"` returning 8.
- `hashlib.sha1(...).hexdigest()` present (1 occurrence).
- `[:16]` truncation present (1 occurrence).
- Tool runs clean: `python tools/audit_coverage_matrix.py --output /tmp/m5.md --ledger /tmp/l5.json` → exit 0.
- §4 header present (1 occurrence).
- DEFECT-COV-00 RESOLVED present (2 occurrences — `### DEFECT-COV-00 — RESOLVED...` header + ledger value).
- HAZARD finding present (1 `### DEFECT-COV-...HAZARD` heading — DEFECT-COV-01).
- "42" literal present in matrix body (3 occurrences — affected_chips + finding title + tier-count narrative).
- Ledger valid JSON with sorted keys, contains DEFECT-COV-00, ends with trailing newline.
- §1 has no `TBD` strings — all three severity tiers populated with live integer counts.
- Byte-identical re-run: `diff /tmp/m5.md /tmp/m6.md` empty.
- `--check` against full ledger exits 0; against empty ledger exits 1.
- 8 of 10 tests green (5 Wave 0-2 + 3 Wave 3 + extended test_exit_codes); only Wave 4 stubs remain failing as designed.
- Committed matrix + ledger byte-identical to a fresh tool run.

## Issues Encountered

None. The Wave 2 tool skeleton (Plan 11-03) had a clean §4 placeholder slot — the new `emit_defects` function returned a list of markdown lines, joined and inserted into `generate_matrix`'s body assembly in place of the old `s4` placeholder. The `emit_placeholder_sections` function shrank from returning `(s4, s5)` to just `s5`.

The submodule pointer drift in `firestarter` (parent repo's git status shows ` M firestarter`) was correctly identified as out-of-scope and left untouched per the orchestrator's instructions. Only `.planning/v1.3-COVERAGE-MATRIX.md` and `.planning/v1.3-defect-coverage-ids.json` were committed in the parent repo for Task 3; the tool + test edits live as commits inside the `firestarter_app` submodule's own repo.

## User Setup Required

None — the audit tool is desk-side (operates only on `chip_database.json`); the regenerated matrix and ledger are committed under `.planning/` for downstream wave consumption.

## Next Phase Readiness

- **Plan 11-05 (Wave 4 — bench coverage proof):** Can now consume the 78-entry ledger + §4 finding inventory to populate §5's three per-axis tables (D-09 / D-10 / D-11). Uncovered cells in those tables will cross-reference `DEFECT-COV-NN` IDs by hash lookup against `.planning/v1.3-defect-coverage-ids.json`.
- **Plan 11-06 (Wave 5 — planning-doc reconciliation):** Treats the DEFECT-COV-NN namespace as the stable vocabulary for v1.4 follow-up PRs. Phase 11 closure depends on every reconciliation patch in `.planning/PROJECT.md`, `.planning/ROADMAP.md`, etc. citing IDs from this ledger.
- **v1.4 build_db.py PR queue:** DEFECT-COV-01 is the headline gap — the WARNING-5 predicate needs an override-class extension (either drop the `_etype == Flash/EEPROM` clause or add a new pinout-keyed override for `{DIP28_28C64, DIP28_28C256} × proto_id == 0x07`). The §4 metadata table for DEFECT-COV-01 carries the `suggested_fix_venue` text verbatim.
- The 78-entry ledger is the regression anchor — any new finding minted on a future DB regen will trip `--check` with exit 1, signaling the operator to inspect the new hash before committing.

## Self-Check: PASSED

- `firestarter_app/tools/audit_coverage_matrix.py` modified with 8 new defs (`finding_hash`, `load_ledger`, `save_ledger`, `mint_or_reuse`, `detect_resolved_baseline`, `detect_hazard`, `detect_correctness`, `detect_variance`, `emit_defects`) — FOUND.
- `firestarter_app/tests/test_audit_coverage_matrix.py` modified — 3 Wave-3 tests + extended test_exit_codes all green — FOUND (8 passed, 2 Wave-4 stubs failed as expected).
- `.planning/v1.3-COVERAGE-MATRIX.md` regenerated with §4 (DEFECT-COV-00 RESOLVED + 77 live findings) — FOUND.
- `.planning/v1.3-defect-coverage-ids.json` created (78 sorted entries, trailing newline) — FOUND.
- `firestarter_app@0e2faf7` (Task 1) — FOUND (`git log --oneline | grep 0e2faf7` returns the commit).
- `firestarter_app@37d6be9` (Task 2) — FOUND.
- `e819d11` (Task 3, parent) — FOUND.

---
*Phase: 11-coverage-matrix-db-inconsistency-audit*
*Completed: 2026-05-19*

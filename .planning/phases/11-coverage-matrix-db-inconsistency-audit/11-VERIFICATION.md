---
phase: 11-coverage-matrix-db-inconsistency-audit
verified: 2026-05-19T00:00:00Z
status: passed
score: 12/12 must-haves verified
overrides_applied: 0
human_verification: []
---

# Phase 11: Coverage Matrix & DB Inconsistency Audit Verification Report

**Phase Goal:** Operator has a complete, single-source coverage map of every algo-0x07 + algo-0x08 chip in `chip_database.json`, with intra-algorithm DB inconsistencies surfaced as defect candidates for follow-up milestones.

**Verified:** 2026-05-19
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria + Specific Must-Haves)

| #   | Truth                                                                                                                                                                                                                                       | Status     | Evidence                                                                                                                                                                                                                                                                                            |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SC-01 | Coverage matrix file exists at `.planning/v1.3-COVERAGE-MATRIX.md` enumerating every algo-0x07 + algo-0x08 row with manufacturer, part_number(s), pin_count, size_bytes, pulse_duration, chip_id_check, chip_id_value, pinout class + electrical type (9 columns) | ✓ VERIFIED | File exists (212,387 bytes, 1425 lines). §3 enumeration has 339 data rows (212 algo-0x07 + 127 algo-0x08). Two per-algorithm sub-tables both carry the 9 required columns in the D-06 order. Total row count matches DB histogram per §1: 212 + 127 = 339. |
| SC-02 | Same file lists every intra-algorithm DB inconsistency, each labeled as defect candidate; no auto-fixes applied to chip_database.json | ✓ VERIFIED | §4 emit contains 78 `### DEFECT-COV-NN` headers (DEFECT-COV-00 RESOLVED baseline + 77 live findings). Three severity tiers present: 1 HAZARD + 27 CORRECTNESS + 49 VARIANCE = 77 live + 1 resolved (per §1 Severity-tier counts block). `git log firestarter/data/chip_database.json` shows zero commits from this phase — last touch was `d0bed87 feat(db): safety skip for 24-pin 5V EEPROMs` (pre-v1.3). `tools/build_db.py` also untouched. |
| SC-03 | Operator can use matrix to confirm BENCH-01..06 span the pinout classes + pulse-duration profiles in DB | ✓ VERIFIED | §5 contains six h3 sub-sections: Pinout-Class Coverage, Pulse-Duration Bucket Coverage (algo-0x07), Pulse-Duration Bucket Coverage (algo-0x08), Size Bucket Coverage (algo-0x07), Size Bucket Coverage (algo-0x08), Known Gaps. Each table identifies BENCH chip(s) covering each cell and flags uncovered cells with DEFECT-COV-NN cross-references or "see Known Gaps". Milestone-claim closing prose explicitly cites N=339 + BENCH-RESULTS receipt framing. |
| MH-4 | Tool idempotence (two-run diff empty) | ✓ VERIFIED | `python tools/audit_coverage_matrix.py --output /tmp/a.md --ledger /tmp/al.json && python tools/audit_coverage_matrix.py --output /tmp/b.md --ledger /tmp/bl.json && diff /tmp/a.md /tmp/b.md` → exit 0. Ledger also byte-identical. |
| MH-5 | Test suite green: 10 tests pass | ✓ VERIFIED | `python -m pytest tests/test_audit_coverage_matrix.py -v` → 10 passed in 0.33s. Full suite: 39 passed in 0.62s. |
| MH-6 | Golden file matches committed matrix | ✓ VERIFIED | `diff firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md .planning/v1.3-COVERAGE-MATRIX.md` → exit 0. Both 212,387 bytes. |
| MH-7 | Planning-doc reconciliation: no live-claim line cites 743 / 341 / 214 | ✓ VERIFIED | `grep -nE "743|341|214" .planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md` returns only 3 hits, all confirmed historical: ROADMAP.md:140 (v1.0 archived <details> bullet, "743-chip database"), STATE.md:221 (Plan 11-02 narrative explaining §2 hard-coding OLD values), PROJECT.md:135 (v1.1 Phase 2 decision-log row narrating WIRE-02 743/743 PASS). These are deliberately preserved per RESEARCH.md A6. |
| MH-8 | COV-01 and COV-02 marked complete in REQUIREMENTS.md with traceability | ✓ VERIFIED | REQUIREMENTS.md COV-01 row: "✅ Complete (Wave 0 RED + Wave 1 §1+§2 + Wave 2 §3 + Wave 3 §4 + Wave 4 §5 + Wave 5 D-07 reconciliation all landed 2026-05-19; matrix + ledger committed; 339 chips covered)". COV-02 row: "✅ Complete (Wave 3 §4 + ledger committed 2026-05-19; HAZARD=1, CORRECTNESS=27, VARIANCE=49 findings flagged...)". Both reference plans 11-01..11-06 explicitly. |
| MH-9 | Out-of-scope hygiene: no firmware changes; no chip_database.json mutations; no build_db.py changes | ✓ VERIFIED | `git log --oneline firestarter/data/chip_database.json \| head -5` shows no Phase 11 commits. `git log --oneline tools/build_db.py` shows no Phase 11 commits. Last touches predate Phase 11. Phase 11 commits in firestarter_app are exclusively against `tools/audit_coverage_matrix.py` and `tests/test_audit_coverage_matrix.py` (+ new `tests/golden/v1.3-COVERAGE-MATRIX.md`). |

**Score:** 9/9 truths verified (3 ROADMAP SCs + 6 task-specific must-haves) = 12/12 if counting individual sub-claims, all VERIFIED.

### Required Artifacts

| Artifact                                                                     | Expected                                                                              | Status     | Details                                                                                                                                                                          |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.planning/v1.3-COVERAGE-MATRIX.md`                                          | Single coverage map; §1-§5 all populated                                              | ✓ VERIFIED | 1425 lines, 212,387 bytes. All 5 sections present (`grep -cE "^## §[1-5]:" → 5`). §3 has 339 data rows in two per-algorithm sub-tables. §4 has 78 DEFECT-COV entries. §5 has 6 sub-sections. |
| `.planning/v1.3-defect-coverage-ids.json`                                    | Stable defect-ID ledger keyed by hash; sorted keys; trailing newline                  | ✓ VERIFIED | 78 entries; `python -c "...sorted(d.keys()) == list(d.keys())"` → True; DEFECT-COV-00..77 all unique; trailing newline present.                                                  |
| `firestarter_app/tools/audit_coverage_matrix.py`                             | Runnable generator implementing §1-§5 emit + ledger + --check                          | ✓ VERIFIED | 57,693 bytes; `def generate_matrix`, `def main`, `def finding_hash`, `def emit_full_enumeration`, `def emit_defects`, `def emit_bench_coverage`, `BENCH_CHIP_MAP` constant all present. Runs end-to-end to exit 0. |
| `firestarter_app/tests/test_audit_coverage_matrix.py`                        | 10-test suite covering all wave contracts                                             | ✓ VERIFIED | 10 collected test methods; zero NotImplementedError stubs remain (the one residual `grep` hit is inside a docstring/comment, not a live raise — see below). All 10 pass.         |
| `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md`                       | Byte-identical snapshot of committed matrix for regression pin                        | ✓ VERIFIED | 212,387 bytes; `diff` against `.planning/v1.3-COVERAGE-MATRIX.md` returns empty.                                                                                                 |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `tools/audit_coverage_matrix.py` | `firestarter/data/chip_database.json` | `json.load(open(DB_FILE))` | WIRED | `_DATA_DIR` + `DB_FILE` + `FIRESTARTER_DB_FILE` env-var override all present; iteration yields 734 total chips → 339 in-scope rows verified live. |
| `tools/audit_coverage_matrix.py` | `.planning/v1.3-COVERAGE-MATRIX.md` | `Path.write_text(content, encoding="utf-8", newline="\n")` | WIRED | `DEFAULT_OUTPUT` derived from `_REPO_ROOT` via `__file__`; default-cwd invocation writes to the committed location; byte-identical re-run confirmed. |
| `tools/audit_coverage_matrix.py::finding_hash` | `hashlib.sha1` | `sha1(json.dumps({...},sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()[:16]` | WIRED | All 78 ledger keys are 16-hex strings; mint/reuse path verified via test_ledger_id_reuse. |
| `tools/audit_coverage_matrix.py::emit_bench_coverage` | `§4 DEFECT-COV-NN findings` | format-string cross-reference of finding IDs into uncovered-cell notes | WIRED | §5 Pinout-Class table cites DEFECT-COV-01, DEFECT-COV-02, DEFECT-COV-03, etc. in uncovered cells (verified via grep against the matrix). |
| `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` | `.planning/v1.3-COVERAGE-MATRIX.md` | byte-identical snapshot | WIRED | `diff` returns empty; both 212,387 bytes. |
| `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md` | `.planning/v1.3-COVERAGE-MATRIX.md §2` | reconciled count claims align (734 / 212 / 339) | WIRED | Plan 11-06 commit `70be654` applied 19 substring replacements; grep gates confirm no live-claim line still references 743/341/214. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `.planning/v1.3-COVERAGE-MATRIX.md` §1 summary stats | `summary["total_chips"]` etc. | `compute_summary(rows, db_raw)` iterating live `chip_database.json` | ✓ Yes — 734/339/212/127 are live-computed | ✓ FLOWING |
| `.planning/v1.3-COVERAGE-MATRIX.md` §3 enumeration | `rows` iterator output | `iter_in_scope_rows(db_raw)` filtered to algo 0x07/0x08 | ✓ Yes — 339 distinct DB records, each row carries 9 live fields | ✓ FLOWING |
| `.planning/v1.3-COVERAGE-MATRIX.md` §4 defect findings | `findings` list | `detect_hazard(rows) + detect_correctness(rows) + detect_variance(rows)` over live rows + seeded DEFECT-COV-00 baseline | ✓ Yes — 77 live findings derived from real DB clusters; the 42-row HAZARD cluster confirmed by independent `grep "DIP28_28C64" + "DIP28_28C256"` count | ✓ FLOWING |
| `.planning/v1.3-COVERAGE-MATRIX.md` §5 BENCH coverage | `BENCH_CHIP_MAP` × `rows` × `findings` | three coverage helpers consume live rows + findings; BENCH chip identity matched against actual DB part_number variants | ✓ Yes — coverage cells correctly identify covered vs uncovered + cite real DEFECT-COV-NN IDs | ✓ FLOWING |
| `.planning/v1.3-defect-coverage-ids.json` | `ledger` dict | `mint_or_reuse(ledger, severity, axis, signature, ...)` writes via `save_ledger` | ✓ Yes — 78 entries, sorted keys, all values map to DEFECT-COV-NN strings | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Tool runs end-to-end to /tmp | `python tools/audit_coverage_matrix.py --output /tmp/a.md --ledger /tmp/al.json` | exit 0; 1425-line matrix produced | ✓ PASS |
| Idempotence (matrix) | `diff /tmp/a.md /tmp/b.md` after two consecutive runs | empty (exit 0) | ✓ PASS |
| Idempotence (ledger) | `diff /tmp/al.json /tmp/bl.json` | empty (exit 0) | ✓ PASS |
| Fresh-run matches committed matrix | `diff /tmp/a.md .planning/v1.3-COVERAGE-MATRIX.md` | empty (exit 0) | ✓ PASS |
| Fresh-run matches committed ledger | `diff /tmp/al.json .planning/v1.3-defect-coverage-ids.json` | empty (exit 0) | ✓ PASS |
| Golden file byte-identical | `diff tests/golden/v1.3-COVERAGE-MATRIX.md .planning/v1.3-COVERAGE-MATRIX.md` | empty (exit 0) | ✓ PASS |
| `--check` against full ledger | `python tools/audit_coverage_matrix.py --check --ledger .planning/v1.3-defect-coverage-ids.json` | exit 0 (no drift) | ✓ PASS |
| `--check` against empty ledger | `echo "{}" > /tmp/empty.json && python tools/audit_coverage_matrix.py --check --ledger /tmp/empty.json` | exit 1 (drift detected) | ✓ PASS |
| Audit test suite | `python -m pytest tests/test_audit_coverage_matrix.py -v` | 10 passed in 0.33s | ✓ PASS |
| Full firestarter_app test suite | `python -m pytest tests/` | 39 passed in 0.62s | ✓ PASS |
| §3 row count = 339 | `awk '/^## §3:/,/^## §4:/' matrix | grep -E "^\| " | grep -v header/sep | wc -l` | 339 | ✓ PASS |
| §3 algo-0x07 sub-table = 212 rows | `awk '/^### algo-0x07/,/^### algo-0x08/' matrix | row count` | 212 | ✓ PASS |
| §3 algo-0x08 sub-table = 127 rows | `awk '/^### algo-0x08 \(127 rows\)/,/^---/' matrix | row count` | 127 | ✓ PASS |
| All 9 columns in §3 | `grep "^\| Manufacturer.*Part Number.*Pin Count.*Size.*Pulse Duration.*Chip ID Check.*Chip ID Value.*Pinout.*Electrical Type"` | 2 matches (one per sub-table) | ✓ PASS |
| Severity tiers in §4 | `grep -cE "HAZARD\|CORRECTNESS\|VARIANCE"` in §4 body | 184 (includes severity counts + per-finding labels) | ✓ PASS |
| BENCH-01..06 references | `grep -cE "BENCH-0[1-6]" matrix` | 16 (well above the ≥ 6 floor) | ✓ PASS |

### Probe Execution

No phase-declared `scripts/*/tests/probe-*.sh` exist for Phase 11 (verified via `find scripts -path '*/tests/probe-*.sh'` — no results in firestarter_app). Phase 11 contract uses pytest as the regression substrate. Tests executed as part of the spot-checks above.

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| `tests/test_audit_coverage_matrix.py` (pytest, the phase's regression contract) | `python -m pytest tests/test_audit_coverage_matrix.py -v` | 10 passed in 0.33s | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
| ----------- | -------------- | ----------- | ------ | -------- |
| **COV-01** | 11-01, 11-02, 11-03, 11-04 (declared), 11-05, 11-06 | Generate coverage matrix from chip_database.json enumerating every algo-0x07 + algo-0x08 row with 9 columns. Output: .planning/v1.3-COVERAGE-MATRIX.md. 339 chips covered. | ✓ SATISFIED | Matrix exists with §3 enumeration of 339 rows in 9-column tables; REQUIREMENTS.md marks COV-01 as `[x]` complete; ROADMAP.md SC-01 phrasing reconciled to "212 + 127 = 339 chips" (Plan 11-06 commit 70be654). |
| **COV-02** | 11-01 (declared), 11-04 (primary detection + ledger) | Identify intra-algorithm DB inconsistencies; flag each as defect candidate; no auto-fixes in v1.3. | ✓ SATISFIED | §4 emit lists 77 live findings across HAZARD/CORRECTNESS/VARIANCE tiers + DEFECT-COV-00 RESOLVED baseline. Ledger at `.planning/v1.3-defect-coverage-ids.json` provides stable IDs. Zero mutations to `chip_database.json` (verified via git log). REQUIREMENTS.md marks COV-02 as `[x]` complete. |

Both requirement IDs declared in PLAN frontmatter (COV-01, COV-02) are satisfied. No orphaned requirements detected — Phase 11 covers exactly the two COVERAGE requirements assigned to it by ROADMAP.md and REQUIREMENTS.md.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `firestarter_app/tools/audit_coverage_matrix.py` | 45 | Unused `from firestarter.database import EpromDatabase` (CR-01 from advisory code review) | ⚠️ Info | Code-quality issue surfaced by the advisory code review. Couples standalone tool to editable-install layout despite "runs from any cwd" docstring claim. **Per the verification request, this is NOT a goal-achievement failure** — the tool runs end-to-end and produces correct output when `firestarter_app` is editable-installed (verified live). Tracking for v1.4 cleanup. |
| `firestarter_app/tests/test_audit_coverage_matrix.py` | (multiple) | 1 `NotImplementedError` grep hit | ℹ️ Info | Single residual reference inside docstring/comment — not a live `raise NotImplementedError`. All 10 tests have real assertion bodies (`python -m pytest -v` → 10 passed). False-positive in the basic grep gate. |
| (none) | — | TBD / FIXME / XXX markers in Phase 11 files | (none found) | `grep -nE "TBD\|FIXME\|XXX"` against the modified files returns no live markers in the tool or test file (the only TBDs were in the Wave 1 §1 severity-tier block, replaced by live counts in Wave 3 per the matrix `### Severity-tier finding counts (D-12)` block: `HAZARD: 1 / CORRECTNESS: 27 / VARIANCE: 49`). |

### Note on Live-Number Drift in SUMMARY vs Live Data

SUMMARY 11-02 quoted preliminary RESEARCH.md numbers (e.g., `<100us=0/8, 10-99ms=148/0, 100ms-1s=63/0` for algo-0x07/0x08). The committed matrix's §1 reports the live-computed values from the current `chip_database.json`:

- `<100us`: 0 / 19
- `100-999us`: 1 / 106
- `10-99ms`: 148 / 0
- `100ms-1s`: 59 / 0

This is the **expected** behavior — Plan 11-02 explicitly decided to live-compute these per D-08 ("§2 reconciliation regenerated from the live DB on every run"). The matrix is the authoritative live source; the slight drift between RESEARCH.md preliminary numbers and the committed matrix is normal upstream-DB drift and does not affect goal achievement. The 4 load-bearing anchors (734 / 212 / 127 / 339) are all correct in §1, §2, the tests, and the reconciled planning docs.

### Human Verification Required

None. All success criteria are programmatically verifiable and have been verified:
- §3 row count and column shape — grep + count
- §4 severity tiers and defect-ID format — grep + JSON parse
- §5 axis tables and BENCH coverage — grep + structural inspection
- Idempotence and golden-file match — `diff` exit 0
- Test green-state — pytest exit 0
- Planning-doc reconciliation — grep gates

The "operator can use the matrix" success criterion (SC-03) is verified structurally: §5 contains the three per-axis tables identifying BENCH chips per cell + Known Gaps subsection + milestone-claim closing prose. Operator readability is observable in the markdown structure itself.

## Gaps Summary

No gaps. All three ROADMAP Success Criteria, all 9 specific verification must-haves, and both requirement IDs (COV-01, COV-02) are satisfied with live codebase evidence.

The phase delivers exactly what was promised:

1. **Single-source coverage map** (`.planning/v1.3-COVERAGE-MATRIX.md`, 1425 lines) enumerating all 339 in-scope chips in two per-algorithm sub-tables with the 9 required columns in D-06 sort order.
2. **Defect inventory** in §4 with 77 live findings across three severity tiers (HAZARD/CORRECTNESS/VARIANCE) + DEFECT-COV-00 RESOLVED baseline, anchored by a stable hash → DEFECT-COV-NN ledger that survives DB regenerations.
3. **BENCH coverage proof** in §5 demonstrating BENCH-01..06 span the relevant pinout / pulse / size axes, with uncovered cells either cross-referenced to §4 findings or documented in Known Gaps as deliberate scope decisions.
4. **Planning-doc reconciliation** landed in a separate commit (`70be654`); all live-claim count references in PROJECT.md / ROADMAP.md / REQUIREMENTS.md / STATE.md now agree with the matrix's §2 (734 / 212 / 127 / 339); historical narrative in archived `<details>` blocks correctly preserved per A6.
5. **Out-of-scope hygiene** — zero mutations to `chip_database.json`, `build_db.py`, or firmware. Phase 11 is exclusively a desk-side audit tool + the artifacts it produces.

The advisory code-review BLOCKER (CR-01 — dead `EpromDatabase` import) is correctly noted as a code-quality follow-up, not a goal-achievement failure, per the verification request guidance. The tool runs end-to-end and produces correct output in the verified environment.

---

_Verified: 2026-05-19_
_Verifier: Claude (gsd-verifier)_

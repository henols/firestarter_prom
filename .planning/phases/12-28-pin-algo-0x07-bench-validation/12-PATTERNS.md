# Phase 12: 28-Pin / Algo-0x07 Bench Validation — Pattern Map

**Mapped:** 2026-05-20
**Files analyzed:** 4 new artifacts (1 markdown + multiple per-cycle logs + multiple scope photos + 1 modified STATE.md tracking table) + 3 orchestrator-owned tracking files (STATE.md, ROADMAP.md, REQUIREMENTS.md)
**Analogs found:** 6 / 6 (4 strong, 1 partial, 1 greenfield with template)

> **Phase shape (atypical).** Per CONTEXT.md domain block + RESEARCH.md §Summary: this phase lands ZERO new production Python code in `firestarter_app/firestarter/` and ZERO firmware changes. The only artifacts under version control are markdown + log + scope-photo files in `.planning/`. Every "execution" task is an operator running the existing `firestarter_app/firestarter_test.sh` harness verbatim (D-02) at the bench; the gsd-executor's role is scribe (read operator-provided log paths → extract values → write BENCH-RESULTS.md row) plus orchestration tracking. Pattern E below codifies the operator-driven `autonomous: false` task shape; Patterns A–D codify the artifact emit shapes.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `.planning/v1.3-BENCH-RESULTS.md` (NEW — Plan 12-04 scaffolds; Plans 12-01/02/03 append) | output artifact (markdown evidence table) | append-only file-I/O via operator transcription | `.planning/v1.3-COVERAGE-MATRIX.md` §5 BENCH coverage tables + `.planning/phases/09-*/09-MEASUREMENT.md` §"Bench Verification — Chipless Wire-Protocol Validation" §"Phase 8 SC#2/SC#3 (carried)" + `.planning/milestones/v1.0-MILESTONE-AUDIT.md` requirements/phase results tables | role-match (multiple convergent precedents; closest single match is 09-MEASUREMENT.md's bench-evidence transcription pattern) |
| `.planning/v1.3/bench-logs/{CHIP}-{board}-{date}.log` (NEW — multiple; operator-generated per cycle via `tee`) | evidence log (text) | streaming stdout/stderr capture via `tee 2>&1` | `firestarter_app/firestarter_test.sh` itself (the harness that emits the lines being captured) + the chipless-matrix tee pattern from Phase 8/9 bench transcripts (08-MEASUREMENT.md lines 362–378) | exact (same `tee` capture convention; same harness emitting; the only delta is the destination path) |
| `.planning/v1.3/scope/{board}-vpp-write-{date}.png` (NEW — multiple; operator-captured oscilloscope export) | evidence binary (PNG/JPG/BMP — see CONTEXT.md D-05) | file-I/O (operator drops in directory) | none (greenfield — no prior phase used scope photos) | none (greenfield; Pattern D below provides a template) |
| `.planning/STATE.md` §"Deferred Items" table (MODIFIED — per CONTEXT.md D-15 when Plan 12-01 closes Phase 08 SC#2/SC#3 + Phase 09 Plan-05 Task 3) | doc (tracking table) | targeted Edit by orchestrator | `.planning/STATE.md` §"Deferred Items" current table at lines 79–84 + Phase 11 orchestrator-driven tracking precedent (per CONTEXT.md D-15 cousin) | exact (same table, same row shape; only the `Status` cell flips from `human_needed` / `partial — 2 pending scenarios` to `closed via BENCH-01`) |
| `.planning/STATE.md` §"v1.3 phases" table (MODIFIED — Phase 12 row flipped to complete by orchestrator) | doc (tracking table) | targeted Edit by orchestrator | Phase 11 close pattern — STATE.md L23–27 + L46–51 + ROADMAP.md Phase entry updated in lockstep per Phase 11 D-07 / Plan 11-06 | exact (Phase 11 just did this; reuse verbatim) |
| `.planning/ROADMAP.md` (MODIFIED — Phase 12 SC#1..5 flipped to complete by orchestrator) | doc (tracking table) | targeted Edit by orchestrator | same as STATE.md row above | exact |
| `.planning/REQUIREMENTS.md` (MODIFIED — BENCH-01/02/05 + PROTO-01/02 status flipped to complete by orchestrator) | doc (tracking table) | targeted Edit by orchestrator | same | exact |

## Pattern Assignments

### `.planning/v1.3-BENCH-RESULTS.md` (output artifact — operator-on-bench evidence aggregator)

**Primary analog:** `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md` (bench-evidence transcription artifact; the most-recent precedent that captures operator-driven UAT into a markdown file via section headers, severity-band tables, and verbatim CLI-output blocks)

**Secondary analog:** `.planning/v1.3-COVERAGE-MATRIX.md` §5 BENCH Coverage Proof (the format for tables that cross-reference BENCH-NN identifiers; lines 1361–1425). This is the matrix the BENCH-RESULTS.md output completes.

**Tertiary analog:** `.planning/milestones/v1.0-MILESTONE-AUDIT.md` lines 247–294 (the WARNING-5-era requirements/phase results table style — pipe-fenced, status-cell + notes-cell convention used throughout the project for milestone-close evidence tables).

---

**Section-header convention** (from `09-MEASUREMENT.md` lines 293, 337, 322; VERIFIED via grep):
```markdown
## Phase 8 SC#2 (carried) — Chip-Seated Write

**Status:** ⏸ **Pending operator-on-bench** (Task 3 of Plan 09-05; Phase 8 carry-over per CONTEXT.md Claude's-Discretion).
```
*Adapt for Phase 12:* one h2 per requirement (`## BENCH-01 — W27C512 (28-pin, algo 0x07, 64K)`, `## BENCH-02 — SST27SF512 ...`, `## BENCH-05 — W27C257 ...`, `## PROTO-01 — Chip-ID Safety Stack`, `## PROTO-02 — VPP Regulator Scope Evidence`). Each section opens with a one-line **Status** marker (`⏸ Pending`, `✅ PASS`, `❌ FAIL`, `↪ Carried`).

---

**Per-chip-per-board row schema** (per CONTEXT.md D-08; 14 columns + 6 rows; pipe-table style matching Pattern B below):
```markdown
| Chip       | Board    | Date       | info | vpp_engaged       | chip_id_read | chip_id_db   | chip_id_match | blank_pre | write | read | verify | blank_post       | log                                                | notes |
|------------|----------|------------|------|-------------------|--------------|--------------|---------------|-----------|-------|------|--------|------------------|----------------------------------------------------|-------|
| W27C512    | uno      | 2026-05-20 | OK   | 12.0V ±5% (scope) | 0x0000da08   | 0x0000da08   | Y             | BLANK     | OK    | OK   | OK     | N/A (UV-EPROM)   | `.planning/v1.3/bench-logs/W27C512-uno-2026-05-20.log` |       |
| W27C512    | leonardo | 2026-05-20 | OK   | 12.0V ±5% (scope) | 0x0000da08   | 0x0000da08   | Y             | BLANK     | OK    | OK   | OK     | N/A (UV-EPROM)   | `.planning/v1.3/bench-logs/W27C512-leonardo-2026-05-20.log` |       |
| SST27SF512 | uno      | …          | …    | …                 | 0x0000bfa4   | 0x0000bfa4   | Y             | …         | …     | …    | …      | N/A (UV-EPROM)   | …                                                  |       |
```
*Source-of-truth cell-value provenance is CONTEXT.md D-08 (the executor-to-operator contract for which log line / scope photo each cell maps to). The format itself matches Pattern B's pipe-fenced column-aligned style.*

---

**PROTO-01 evidence row** (per CONTEXT.md D-09; 1 row total, captured during Plan 12-02 against SST27SF512):
```markdown
## PROTO-01 — Chip-ID Safety Stack Evidence

| Chip Socketed | Board    | Intended (wrong) Chip | Expected Block Reason          | Observed Log Snippet                                                     | Log Path                                                                                |
|---------------|----------|-----------------------|--------------------------------|--------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| SST27SF512    | leonardo | W27C512               | `MSG_ERR_CHIP_ID_MISMATCH` (0xB9) | `ERROR: Chip ID 0xbfa4 does not match expected ID 0xda08`                  | `.planning/v1.3/bench-logs/SST27SF512-blocked-write-leonardo-2026-05-20.log`            |
```
*Grep target the operator runs to populate the `Observed Log Snippet` cell, per RESEARCH.md §"PROTO-01 chip-ID line extraction from log":*
```bash
grep -iE "chip[_-]id|MSG_(WARN|ERR)_CHIP_ID" /workspaces/.planning/v1.3/bench-logs/SST27SF512-blocked-write-leonardo-2026-05-20.log
```

---

**PROTO-02 evidence rows** (per CONTEXT.md D-10; 2 rows = one per board; optional 2 more for idle-state photos):
```markdown
## PROTO-02 — VPP Regulator Scope Evidence

| Board    | Scope Photo Path                                              | Measured VPP (V) | Tolerance Band Check (11.4V–12.6V) | Idle-State Observed | Captured During                | Probe Point        |
|----------|---------------------------------------------------------------|------------------|------------------------------------|---------------------|--------------------------------|--------------------|
| uno      | `.planning/v1.3/scope/uno-vpp-write-2026-05-20.png`           | 12.0             | Y                                  | Y (idle-photo below) | `firestarter write W27C512`    | socket pin 22 (VPP on DIP28_27512) |
| leonardo | `.planning/v1.3/scope/leonardo-vpp-write-2026-05-20.png`      | 11.9             | Y                                  | Y                   | `firestarter write W27C512`    | socket pin 22 (VPP on DIP28_27512) |
```
*Probe-point cell is load-bearing per RESEARCH.md Pitfall 1 — Plan 12-03 (BENCH-05 = W27C257) MUST record `socket pin 1 (VPP on DIP28_27256)` in this column to evidence the probe-swap was performed. A row with `socket pin 22` for W27C257 is invalid evidence.*

---

**Top-of-file scaffold** (Plan 12-04 creates, mirroring `09-MEASUREMENT.md` header convention + `v1.3-COVERAGE-MATRIX.md` h1 banner):
```markdown
# v1.3 BENCH Validation Results

**Status:** Phase 12 in progress (Phase 14 / DOC-01 owns final aggregation; this file accretes rows across Phases 12 + 13)
**Phase 12 scope:** BENCH-01 (W27C512), BENCH-02 (SST27SF512), BENCH-05 (W27C257) — all 28-pin algo-0x07 — on Uno + Leonardo
**Phase 13 scope (later):** BENCH-03 (W27C020), BENCH-04 (W27E040), BENCH-06 (32-pin density-low candidate) — algo-0x08 — on Uno + Leonardo
**Cross-reference:** `.planning/v1.3-COVERAGE-MATRIX.md` §5 BENCH Coverage Proof (proves BENCH-01..06 represent the 339-row algo-0x07+0x08 family)

---

## Per-Chip-Per-Board Cycle Results (D-08 schema; 14 columns)

[per-chip-per-board row schema table — empty headers + separator row only; chip plans append rows]

---

## PROTO-01 — Chip-ID Safety Stack Evidence (D-09)

[PROTO-01 row schema — empty headers only; Plan 12-02 Task 4 appends one row]

---

## PROTO-02 — VPP Regulator Scope Evidence (D-10)

[PROTO-02 row schema — empty headers only; Plans 12-01/02/03 append one row per board]

---

## Notes & Anomalies

(Freeform operator notes — chip re-seats, retried cycles, scope-trigger misses, etc.)
```
*Per RESEARCH.md Open Question 1: scaffold headers + separator row ONLY (not pre-populated placeholder rows). This keeps appending idempotent on resume.*

---

### `.planning/v1.3/bench-logs/{CHIP}-{board}-{date}.log` (evidence log files)

**Analog:** `firestarter_app/firestarter_test.sh` itself (the harness producing the stdout/stderr captured into these logs)

**Source of every captured line** (`firestarter_test.sh:90-118`, VERIFIED):
```bash
exec_firestarter() {
    TEST_NAME=$1
    CMD_NAME=$2
    EPROM=${3:-}
    ...
    firestarter_cmd="firestarter $VERBOSE_FLAG $CMD_NAME $CMD_ARGS $EPROM $FILE_NAME"
    echo "---------------------------------"
    echo "Test: $TEST_NAME"
    echo "Cmd: $firestarter_cmd"
    echo "---------------------------------"
    echo
    $firestarter_cmd
    if test $? -gt 0; then
        echo "$TEST_NAME failed"
        exit 1
    fi
    echo
    sleep 0.5
}
```
*The `Test: <name>` banner lines + the `firestarter` CLI's `-v` output are the grep targets the executor uses to extract `info`/`write`/`read`/`verify` cell values for the BENCH-RESULTS row. Banner format is stable across all harness invocations.*

---

**Capture pattern A — `tee` invocation** (per CONTEXT.md D-02 + 08-MEASUREMENT.md lines 362–378 chipless-matrix transcripts; also see Pattern A "Per-cycle log capture" below):
```bash
# Source: CONTEXT.md D-02 invocation block (lines 60-65) + Pattern A below
cd /workspaces/firestarter_app
./firestarter_test.sh W27C512 2>&1 \
  | tee /workspaces/.planning/v1.3/bench-logs/W27C512-uno-2026-05-20.log
```
*The `2>&1` merges stderr into stdout (the `firestarter` CLI emits ERROR-band frames to stderr in some paths; merging keeps the log linear). The `tee` to a per-cycle file is the project-standard log pattern established v1.0+ (see RESEARCH.md §"Established Patterns").*

---

**Capture pattern B — pre-cycle blank-check insertion** (per RESEARCH.md §"Pre-cycle blank check insertion (D-07 step 4)" lines 437–457; the harness does not run pre-cycle blank for UV-EPROMs, so Plan 12-01/02/03 Task 1 prepends a manual call with `tee -a` for append):
```bash
# Step 4 of D-07 (pre-cycle blank check, manual addition):
cd /workspaces/firestarter_app
firestarter -v blank W27C512 2>&1 \
  | tee -a /workspaces/.planning/v1.3/bench-logs/W27C512-uno-2026-05-20.log

# Then the harness for the rest of the cycle (note tee -a, not tee):
./firestarter_test.sh W27C512 2>&1 \
  | tee -a /workspaces/.planning/v1.3/bench-logs/W27C512-uno-2026-05-20.log
```
*`tee -a` appends so both the blank check output and the harness output share one log file — the D-14 resume-anchor contract requires a single linear log per cycle.*

---

**Log path convention** (per RESEARCH.md §"Recommended Directory Layout" lines 213–229; date ISO format per CONTEXT.md "Claude's Discretion" line 80):
```
.planning/v1.3/bench-logs/
├── W27C512-uno-2026-05-20.log
├── W27C512-leonardo-2026-05-20.log
├── SST27SF512-uno-2026-05-20.log
├── SST27SF512-leonardo-2026-05-20.log
├── W27C257-uno-2026-05-20.log
├── W27C257-leonardo-2026-05-20.log
└── SST27SF512-blocked-write-{board}-2026-05-20.log   # PROTO-01 evidence (D-04)
```
*Filename schema: `{CHIP_UPPERCASE}-{board_lowercase}-{ISO_date}.log`. Plan 12-02 Task 4 produces the `-blocked-write-` variant for PROTO-01 evidence.*

---

### `.planning/v1.3/scope/{board}-vpp-write-{date}.png` (scope photo evidence — GREENFIELD)

**No prior analog exists in the codebase.** No phase before Phase 12 captured oscilloscope photos as committed evidence. This pattern is established here for the first time and carried forward to Phase 13 unchanged (per CONTEXT.md D-05/D-06 carry-forward clause).

**Template** (per CONTEXT.md D-05 + D-06; see Pattern D below for the full operator-instruction shape):

| Property | Requirement |
|----------|-------------|
| **File format** | PNG or JPG recommended; BMP / SVG / CSV acceptable per CONTEXT.md "Claude's Discretion" line 79 |
| **Filename** | `{board}-vpp-{phase}-{date}.{ext}` where `{phase}` ∈ {`write` (required), `idle` (optional)} and `{board}` ∈ {`uno`, `leonardo`} |
| **Minimum required** | 2 photos (one per board) for Plan 12-01 — covers PROTO-02 across both buffer sizes (Uno 512 B, Leonardo 1024 B per CLAUDE.md). Plans 12-02 / 12-03 reuse the Plan 12-01 photos by reference unless board-specific VPP anomaly observed. |
| **Optional** | `{board}-vpp-idle-{date}.{ext}` for the "between operations" idle-state evidence per ROADMAP SC#5 — capture window per RESEARCH.md Open Question 2 (after harness completion, before chip removal). |
| **Annotation content** | Per CONTEXT.md D-06: photo MUST visibly include (1) chip socket VPP pin probe point, (2) scope time-base reading, (3) voltage scale. Operator adds one-line caption in BENCH-RESULTS row stating measured Vpp + tolerance band. |
| **Probe location** | DIP28_27512 chips (W27C512, SST27SF512): **socket pin 22**. DIP28_27256 chip (W27C257): **socket pin 1**. RESEARCH.md Pitfall 1 — Plan 12-03 first task MUST instruct operator to re-probe pin 1 before seating W27C257; otherwise photo captures the wrong pin (DIP28_27256 pin 22 = `oe-pin`, not VPP). |
| **Trigger timing** | Operator watches harness stdout for the `--- Test: Writing to <CHIP> ---` banner (`firestarter_test.sh:146`); the next several seconds are when VPP is asserted at 12V. Window per chip per RESEARCH.md §"Scope photo capture timing": 64K W27C512 ≈ 10 min, 32K W27C257 ≈ 5 min. |
| **Caption template (one-line, embedded in BENCH-RESULTS row)** | `Measured VPP = 12.0V at pin 22 during write; tolerance band 11.4–12.6V → PASS` |

*Per RESEARCH.md Anti-Pattern "Committing scope photos to git as PNG blobs": default is commit PNG inline (≤500KB typical); revisit at milestone close if archive size becomes a problem (per RESEARCH.md A5).*

---

### `.planning/STATE.md` §"Deferred Items" table (modified by orchestrator per CONTEXT.md D-15 when Plan 12-01 closes Phase 08 SC#2/SC#3 + Phase 09 Plan-05 Task 3)

**Analog:** `.planning/STATE.md` current §"Deferred Items" section at lines 76–84 (VERIFIED via direct file read)

**Current table state** (`STATE.md:79-84`, the rows whose Status cells flip when Plan 12-01 closes green):
```markdown
| Category | Item | Status | Note |
|----------|------|--------|------|
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 | v1.1 carryover — needs different Uno R3 to unblock; out of scope for v1.3 |
| uat | Phase 08 HUMAN-UAT.md | partial — 2 pending scenarios | chip-seated W27C512 write + readback → closes via v1.3 BENCH-01 (Phase 12) |
| verification | Phase 08 VERIFICATION.md | human_needed | bench UAT closure → closes via v1.3 BENCH-01 (Phase 12) |
| verification | Phase 09 VERIFICATION.md | human_needed | Plan 09-05 Task 3 (chip-seated W27C512 on both boards) → closes via v1.3 BENCH-01 (Phase 12) |
```
*After Plan 12-01 closes green (`autonomous: false` operator confirmation), orchestrator runs a targeted Edit changing the three `Status` cells in rows 2–4:*

| Row | Status cell — before | Status cell — after |
|-----|----------------------|---------------------|
| `uat / Phase 08 HUMAN-UAT.md` | `partial — 2 pending scenarios` | `closed-2026-05-20 (Phase 12 BENCH-01)` |
| `verification / Phase 08 VERIFICATION.md` | `human_needed` | `closed-2026-05-20 (Phase 12 BENCH-01)` |
| `verification / Phase 09 VERIFICATION.md` | `human_needed` | `closed-2026-05-20 (Phase 12 BENCH-01)` |

The `debug / fm1608-fresh-chip-baseline` row stays unchanged (`parked-2026-05-18`) — Phase 12 explicitly out-of-scopes it per CONTEXT.md "Deferred Ideas" line 218 + STATE.md L88.

*Pattern C (deferred-items closure pattern) — see Shared Patterns below — defines this orchestrator-owned edit shape. Plans themselves do NOT directly modify STATE.md; they emit a SUMMARY.md row reporting "Phase 08 SC#2/SC#3 closed via this BENCH-01 cycle" and the orchestrator does the lockstep STATE.md / ROADMAP.md / REQUIREMENTS.md edit on plan-close per Phase 11 D-15.*

---

### `.planning/STATE.md` §"v1.3 phases" table + `.planning/ROADMAP.md` Phase 12 entry + `.planning/REQUIREMENTS.md` BENCH/PROTO rows (all three modified by orchestrator on phase close)

**Analog:** Phase 11 close pattern (D-15 cousin). See `.planning/STATE.md:46-51` (v1.3 phases table where Phase 11's row is already complete; Phase 12 row currently reads `Yes` in `Bench-gated?`) + `.planning/ROADMAP.md` §"Phase 12" entry + `.planning/REQUIREMENTS.md` BENCH/PROTO sections.

**Orchestrator edit shape on phase close** (mirrors Phase 11's Plan 11-06 D-07 reconciliation pass — VERIFIED via STATE.md L236 narrative):
1. Flip STATE.md `Current Position` from `Phase 12 in progress` → `Phase 12 COMPLETE`
2. Flip ROADMAP.md Phase 12 SC#1..5 checkboxes from `[ ]` → `[x]` (per ROADMAP convention)
3. Flip REQUIREMENTS.md BENCH-01/02/05 + PROTO-01/02 status indicators per the project's REQUIREMENTS.md convention (checkboxes or status cells — orchestrator follows the live file shape)
4. Bump STATE.md frontmatter `completed_phases` and `percent` counters

*Per Phase 11 Plan 11-06 narrative (STATE.md L236): "D-07 reconciliation landed as a single dedicated commit". Phase 12 follows the same convention — the per-plan SUMMARY commits land before the cross-doc tracking-table edit pass, and that pass is its own commit.*

---

## Shared Patterns

### Pattern A — Per-cycle log capture via `tee 2>&1 | tee` (applies to every bench plan task that invokes the harness)

**Source:** `firestarter_app/firestarter_test.sh` (the harness that emits the captured output) + 08-MEASUREMENT.md lines 362–378 (the most-recent project precedent for `tee`'d bench captures) + CONTEXT.md D-02 invocation block

**Apply to:** All cycle invocations in Plans 12-01, 12-02, 12-03. PROTO-01 blocked-write capture in Plan 12-02 Task 4 uses the same pattern with a distinct log-path suffix.

**Canonical invocation form:**
```bash
# Per-cycle (full bench harness): one tee, fresh log file per (chip, board, date) tuple
cd /workspaces/firestarter_app
./firestarter_test.sh <CHIP> 2>&1 \
  | tee /workspaces/.planning/v1.3/bench-logs/<CHIP>-<board>-<date>.log

# Pre-cycle blank check (manual addition per D-07 step 4): tee -a APPEND so both
# the blank check and the harness output share one log
firestarter -v blank <CHIP> 2>&1 \
  | tee -a /workspaces/.planning/v1.3/bench-logs/<CHIP>-<board>-<date>.log
./firestarter_test.sh <CHIP> 2>&1 \
  | tee -a /workspaces/.planning/v1.3/bench-logs/<CHIP>-<board>-<date>.log
```

**Invariants (operator MUST observe):**
1. `2>&1` first, then `tee` — stderr merges into stdout BEFORE tee splits to file (otherwise stderr is lost from the log)
2. `cd /workspaces/firestarter_app` is mandatory — the harness reads `./firestarter/data/chip_database.json` via the relative path at `firestarter_test.sh:31` (Assumption A4 in RESEARCH.md). Running from any other cwd causes the harness to exit at line 73 with `No match found`.
3. Single log file per (chip, board, date); use `tee -a` for any additional commands appended to the same cycle (pre-cycle blank, PROTO-01 blocked-write addendum if folded into the same cycle).
4. Log filename schema: `{CHIP_UPPERCASE}-{board_lowercase}-{ISO_date}.log` — sortable by date, greppable by chip, decodable by board.
5. Log file is the **resume anchor** (per CONTEXT.md D-14): if a cycle is interrupted mid-step, the operator inspects the last completed step in the log and continues from there. No separate per-task progress file is created.

**Verification by executor (per RESEARCH.md Open Question 3):**
```bash
ls -l /workspaces/.planning/v1.3/bench-logs/<CHIP>-<board>-<date>.log
test -s /workspaces/.planning/v1.3/bench-logs/<CHIP>-<board>-<date>.log  # size > 0
grep -q "All tests passed" /workspaces/.planning/v1.3/bench-logs/<CHIP>-<board>-<date>.log  # green-cycle sentinel from firestarter_test.sh:171
```
*Executor refuses to write the BENCH-RESULTS row if the log file is missing or empty (RESEARCH.md Open Question 3 recommendation).*

---

### Pattern B — Markdown table emission (applies to every table in BENCH-RESULTS.md)

**Source:** `.planning/v1.3-COVERAGE-MATRIX.md` §5 BENCH Coverage Proof tables (lines 1361–1425; VERIFIED) + Phase 11 PATTERNS.md Pattern D ("Markdown table emission") + `08-MEASUREMENT.md` Severity-band frame coverage table (lines 332–342, VERIFIED) + v1.0-MILESTONE-AUDIT.md requirements/phase results tables (lines 247–294, VERIFIED).

**Apply to:** Every table in `.planning/v1.3-BENCH-RESULTS.md` — per-chip-per-board rows (D-08), PROTO-01 evidence row (D-09), PROTO-02 evidence rows (D-10), and any operator notes / anomalies tables.

**Canonical convention** (VERIFIED stable across all three precedents):
- Pipe-fenced rows: `| cell | cell |`
- Hyphen-only separator row: `|-----|-----|`
- Per-column left-justified padding to max cell width
- No fancy unicode borders, no centered alignment, no HTML
- Single blank line before the header row; single blank line after the final row

**Verbatim sample** (`08-MEASUREMENT.md:332-342`, VERIFIED — the closest in-style precedent for a bench-evidence column-aligned table):
```markdown
| Band | Frame | Uno result | Leonardo result |
|---|---|---|---|
| OK composite (P-04) | MSG_OK_FW_HANDSHAKE u8+u8+ascii_str | `OK: FW: 2.0.11-dev:uno, HW: Rev1, Cmd: 0x0b` | `OK: FW: 2.0.11-dev:leonardo, HW: Rev1, Cmd: 0x0b` |
| OK fixed (P-02) | MSG_OK_REV u8+u8 | `Rev1` (effective=0xFF sentinel branch) | `Rev1, Override HW: Rev2` (non-sentinel branch) |
```

**Cell-content conventions** (per RESEARCH.md §"PROTO-01 chip-ID line extraction" + project-wide markdown precedent):
- Log paths in backticks: `` `.planning/v1.3/bench-logs/<chip>-<board>-<date>.log` ``
- CLI command-output snippets in backticks: `` `OK: FW: 3.0.0-dev:uno` ``
- Pass/Fail status: literal `OK` / `FAIL: <reason>` (D-08 schema)
- Skipped-by-design cells: `N/A (UV-EPROM)` (D-08 `blank_post` cell for algo-0x07; literal string)

**Emit-source guidance (operator hand-edits this file; no code-gen):**
- This file is **human-edited via the executor's continuation prompt**, not regenerated from a tool. The executor receives the operator's log/photo paths, extracts cell values, and inserts a single row at the end of the corresponding table.
- No `sort_keys=True` / no `Path.write_text(...newline="\n")` / no idempotence machinery — the file is append-only and ordered by phase-execution time (Plan 12-01 rows first, then 12-02, then 12-03).
- The orchestrator commits the file in lockstep with STATE.md / ROADMAP.md updates per CONTEXT.md D-15 (see Pattern C below).

---

### Pattern C — Deferred-items closure & orchestrator-owned tracking writes (applies to STATE.md, ROADMAP.md, REQUIREMENTS.md modifications)

**Source:** Phase 11 D-15 / Plan 11-06 narrative (STATE.md L236, VERIFIED) — "D-07 reconciliation landed as a single dedicated commit". Phase 12 D-15 explicitly inherits this pattern ("orchestrator commits STATE.md + ROADMAP.md progress in lockstep — same pattern as Phase 11").

**Apply to:** All `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` modifications across Phase 12. Plans themselves do **NOT** modify these files directly.

**Contract (orchestrator-owned, two-phase):**

**Phase α (per plan close):** Each chip plan's executor produces:
1. A `12-NN-SUMMARY.md` file with: list of artifacts created/updated (BENCH-RESULTS.md rows added, log files captured, scope photos saved); list of deferred-items closed (Phase 12-01 only — closes Phase 08 SC#2/SC#3 + Phase 09 Plan-05 Task 3); list of any operator anomalies noted.
2. An updated `.planning/v1.3-BENCH-RESULTS.md` with the rows for this plan's chip-board cycles appended.
3. Zero direct edits to STATE.md / ROADMAP.md / REQUIREMENTS.md.

**Phase β (orchestrator, after each chip plan commits):**
1. Reads the just-committed SUMMARY.md to extract the deferred-items-closed list and the SC-status deltas.
2. Edits STATE.md §"Deferred Items" table — flips Status cells per the Plan 12-01 schema documented above (the table at "`.planning/STATE.md` §"Deferred Items" table" section).
3. Edits STATE.md §"v1.3 phases" table — updates Phase 12 row's progress indicator.
4. Edits STATE.md `Current Position` + `Resume from` blocks per the v1.3 precedent.
5. Edits ROADMAP.md Phase 12 entry — flips Success Criteria checkboxes per the SUMMARY's coverage.
6. Edits REQUIREMENTS.md BENCH-01 / BENCH-02 / BENCH-05 / PROTO-01 / PROTO-02 rows — flips status indicators.
7. Commits all three edits in a single commit (Phase 11 Plan 11-06 D-07 convention — STATE.md L236 narrative "20 substring replacements across PROJECT/ROADMAP/REQUIREMENTS/STATE").

**Anti-pattern (per RESEARCH.md Anti-Pattern "Treating Phase 12 as automated executable"):** A chip-plan task that begins "Edit STATE.md to flip..." is a planning error — that's the orchestrator's job, not the plan's. Plans emit signals (SUMMARY.md rows); the orchestrator interprets and applies.

**Verbatim Phase 11 precedent** (`STATE.md:236`):
> Plan 11-06: D-07 reconciliation landed as a single dedicated commit (70be654, separate from matrix-tool commits per D-07). 20 substring replacements across PROJECT.md (6) / ROADMAP.md (4) / REQUIREMENTS.md (1) / STATE.md (2 …).

*Phase 12's close commit follows the same shape: one orchestrator commit replacing N substrings across the 3 tracking files after Plan 12-03 (the last chip plan) closes.*

---

### Pattern D — Scope-photo evidence convention (GREENFIELD — applies to all PROTO-02 captures)

**Source:** CONTEXT.md D-05 + D-06 (no prior phase analog). Phase 12 establishes this pattern; Phase 13 reuses unchanged per CONTEXT.md D-06 carry-forward clause.

**Apply to:** Every PROTO-02 capture in Plans 12-01, 12-02, 12-03 (minimum 2 photos = 1 per board; optional idle-state photos per board).

**File-name schema:**
```
.planning/v1.3/scope/{board}-vpp-{phase}-{date}.{ext}
```
where:
- `{board}` ∈ {`uno`, `leonardo`}
- `{phase}` ∈ {`write` (required, captured during `firestarter write`), `idle` (optional, captured after harness completion per RESEARCH.md Open Question 2)}
- `{date}` = ISO `YYYY-MM-DD` (recommended; operator's local convention acceptable per CONTEXT.md "Claude's Discretion" line 80)
- `{ext}` = `png` or `jpg` recommended; `bmp` / `svg` / `csv` acceptable if annotation requirements met (CONTEXT.md "Claude's Discretion" line 79)

**Required photo content (per CONTEXT.md D-06):**
The photo must visibly include:
1. **Chip socket VPP pin probe point** — the operator's scope probe physically on the correct socket pin (pin 22 for DIP28_27512 chips, pin 1 for DIP28_27256 chips per RESEARCH.md Pitfall 1)
2. **Scope time-base reading** — e.g., `10 ms/div` or `5 ms/div` baked into the export
3. **Voltage scale** — e.g., `5 V/div` or `2 V/div` baked into the export

The operator's scope's built-in annotation export (cursors + scale labels) satisfies this without additional image-processing per RESEARCH.md "Don't Hand-Roll" line 309.

**Operator instruction template** (Plan 12-01 Task 1 / Plan 12-03 Task 1 — the latter MUST include the probe-swap reminder):
```
Before starting the write phase:
1. Confirm scope probe is on socket pin <22 for W27C512/SST27SF512 | 1 for W27C257> — see RESEARCH.md Pitfall 1.
2. Set scope time-base ≈ 10 ms/div (write-pulse width is 10 ms for algo-0x07; 1 div per pulse).
3. Set voltage scale ≈ 5 V/div (12V VPP swings into ~2.5 divisions from 0V baseline).
4. Arm scope trigger on positive edge ≥ 6V (catches the VPP rise from VCC ≈ 5V → 12V).

When the harness stdout prints "--- Test: Writing to <CHIP> ---":
5. The scope auto-triggers on the first write-pulse VPP assertion.
6. Save the captured trace as PNG to .planning/v1.3/scope/<board>-vpp-write-<date>.png .
7. Confirm the saved image shows the 12V plateau, the timing scale, and the voltage scale.
```

**Caption template** (one-line, embedded in BENCH-RESULTS PROTO-02 row's `notes` cell or as a markdown caption near the row):
```
Measured VPP = <X>.X V at socket pin <22|1> during `firestarter write <CHIP>`; tolerance band 11.4-12.6V → <PASS|FAIL>; scope @ 10 ms/div, 5 V/div.
```

**Warning signs the photo is invalid** (per RESEARCH.md Pitfall 1):
- Trace shows ~5V swings instead of 12V plateau → probe is on the wrong pin (likely `oe-pin` on DIP28_27512, or pin 22 on DIP28_27256 = `oe-pin`)
- Idle level shows clean digital edges (rise/fall < 100 ns) → probe is on a logic line, not the regulator output
- No annotation visible → scope export configured without scale labels; re-export with annotations enabled

---

### Pattern E — Operator-driven `autonomous: false` task shape (applies to every task in Plans 12-01, 12-02, 12-03)

**Source:** `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-05-measurement-and-bench-uat-PLAN.md` Tasks 2 + 3 (VERIFIED — the most-recent `autonomous: false` operator-on-bench plan in the project; closest possible analog to Phase 12 chip plans, including chip-seated W27C512 UAT on both boards).

**Apply to:** Every operator-on-bench task in Plans 12-01, 12-02, 12-03. Plan 12-04 (desk-side scaffold) is the only `autonomous: true` plan in the phase and uses a different task shape (regular executor task — see RESEARCH.md §"Pattern 1" for operator-driven checkpoint task structure).

**Verbatim task shape** (from `09-05-measurement-and-bench-uat-PLAN.md:242-309`, Task 2 — the operator-on-bench wire-protocol re-run, the closest analog by intent + structure):
```xml
<task type="checkpoint:human-verify" gate="blocking">
  <name>Task N: <short imperative describing what the operator does at the bench></name>
  <read_first>
    - <plan-relative path to the upstream RESEARCH section the operator needs>
    - <path to the artifact created by an upstream task that this task fills/extends>
    - <project-memory references where the convention is documented>
  </read_first>
  <what-built>
    <one-paragraph summary of what upstream tasks produced and what this task adds.
     States the executor's role explicitly: "Task N fills the empty <section> section
     with the operator's transcribed outputs from running the bench cycle.">
  </what-built>
  <how-to-verify>
    Operator runs <bench command> on both Uno (`/dev/ttyACM0`) and Leonardo
    (`/dev/ttyACM1` — actual port may differ; resolve via `firestarter --list-ports`).
    Per project memory `[[feedback_always-mirror-uno-leonardo-tests]]` every Uno
    command is paired with a Leonardo run as the control.

    1. **<Subtask 1 — descriptive heading>:**
       ```bash
       <exact command operator runs, including the tee redirect to the bench-log path>
       ```
       Expected: <substring or grep target that proves the subtask succeeded>
       Significance: <why this subtask matters for the phase requirement it covers>

    2. **<Subtask 2 — descriptive heading>:**
       ```bash
       <next command>
       ```
       Expected: <next assertion>

    ...

    N. **Operator transcribes** the observed outputs into the empty
       `## <Section Name>` section of `<artifact path>`. Format mirrors
       <reference precedent path lines NNN-NNN>.

    N+1. **Operator commits** the updated `<artifact path>`.

    Expected outcome: <one-line statement of what the phase has proved when this task closes>.
  </how-to-verify>
  <resume-signal>
    Type "<task-name-approved>" with the observed outputs transcribed into
    <artifact path>, OR describe issues (e.g. "<error scenario 1>", "<error
    scenario 2>"). If any issue surfaces, the operator should pause and report
    it — per project memory `[[<relevant memory>]]` <one-line context>.
  </resume-signal>
  <verify>
    <automated>cd /workspaces &amp;&amp; grep -q '<load-bearing substring 1>' <artifact path> &amp;&amp; grep -q '<load-bearing substring 2>' <artifact path></automated>
  </verify>
  <acceptance_criteria>
    - `<artifact path>` contains a populated `## <Section Name>` section with
      observed outputs for <list of commands> on BOTH boards
    - The <key field> output for Uno contains the substring `<substring>`
    - The <key field> output for Leonardo contains the substring `<substring>`
    - <Anti-regression assertion — e.g., "No FirmwareOutdatedError raised">
    - <Cross-board consistency assertion — e.g., "every command produces output
      matching the Phase N baseline at <reference> lines NNN-NNN">
  </acceptance_criteria>
  <done>
    - <Single-line declaration of what is now true that wasn't before>
    - <Reference to the next task in the chain, or "phase advances to N+1">
  </done>
</task>
```

**Key invariants** (per RESEARCH.md Anti-Patterns + Pattern 1 + project-memory):
1. **Task type is `checkpoint:human-verify` with `gate="blocking"`** — NOT `auto`. The executor must NOT auto-run any `firestarter` command; every CLI invocation is an instruction TO THE OPERATOR. Anti-pattern: a `<task type="auto">` that contains `<action>firestarter write ...</action>` — this is a planning error because the sandbox has no hardware.
2. **`<read_first>` block cites the upstream RESEARCH section + artifact path + project-memory references** that the operator (NOT the executor) must internalize before starting the bench step. The executor's job is to surface these to the operator via the continuation prompt.
3. **`<how-to-verify>` body is operator-facing prose** (full sentences, imperative voice, "Operator runs…", "Expected: …"). Markdown-fenced code blocks contain the exact bash commands to copy-paste. Subtasks are numbered 1..N for unambiguous "where did I leave off?" recovery.
4. **`<resume-signal>` is a string the operator types after completing the bench step**, returning control to the executor. Format: `<task-name-approved>` for green, descriptive prose for issues. The executor's continuation prompt instructs the operator on the exact resume-signal phrase.
5. **`<verify><automated>` runs grep against the artifact** (NOT against any hardware state). The executor uses this AFTER the operator returns the resume-signal — if the grep fails, the operator's transcription is missing and the task is incomplete.
6. **`<acceptance_criteria>` cites load-bearing substrings** (`OK: FW: 3.0.0-dev:uno`, `MSG_ERR_CHIP_ID_MISMATCH`, `12.0V`, `socket pin 22`, `Files are identical`) that the executor's `<automated>` grep targets. Per RESEARCH.md T-09-05-06 (Pitfall 6 / Threat T-09-05-06 in the 09-05 plan): grep-substring assertions catch transcription errors.
7. **Project-memory citations are explicit** — `[[feedback_always-mirror-uno-leonardo-tests]]` (both-boards rule), `[[project_db-overrides-firmware-is-ground-truth]]` (PROTO-01 firmware-safety-stack source), `[[feedback_ic-removal-autonomy]]` (chip swaps between boards proceed without per-cycle operator confirmation), and (where Leonardo readback diverges from Uno on a chip-seated cycle) `[[project_leonardo-shield-socket-wonky]]` (re-seat before declaring regression).

**Phase 12 task numbering (per CONTEXT.md D-11 + RESEARCH.md §"Pattern 1: Operator-Driven Checkpoint Tasks" lines 232–248):**

| Plan | Task 0 (setup) | Task 1 (Uno cycle) | Task 2 (board swap) | Task 3 (Leonardo cycle) | Task 4 (PROTO-01, 12-02 only) | Task 5 (commit) |
|------|----------------|--------------------|---------------------|--------------------------|---------------------------------|------------------|
| 12-01 | Seat W27C512; confirm Uno USB; probe pin 22 | Run harness + tee log + capture scope-write photo | Swap to Leonardo USB | Same as Task 1 with leonardo log + photo | — | executor-driven SUMMARY.md + BENCH-RESULTS.md row append |
| 12-02 | Seat SST27SF512; confirm Uno USB; reuse pin 22 probe | Run harness + tee log + (scope photo reused from 12-01 unless anomaly) | Swap to Leonardo USB | Same as Task 1 | Run wrong-chip-name write capture per Pattern 2 (RESEARCH.md lines 250–274) | same |
| 12-03 | **PROBE-POINT SWAP — move scope to pin 1**; seat W27C257; confirm Uno USB | Run harness + tee log + capture scope-write photo (pin 1) | Swap to Leonardo USB | Same as Task 1 with leonardo log + photo | — | same |

*The Plan 12-03 Task 0 probe-swap reminder is **load-bearing** per RESEARCH.md Pitfall 1; the task's `<acceptance_criteria>` block MUST grep the BENCH-RESULTS PROTO-02 row for the literal substring `socket pin 1` to prove the swap happened.*

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `.planning/v1.3/scope/{board}-vpp-{write,idle}-{date}.{png,jpg}` | evidence binary (scope photo) | file-I/O | No prior phase used oscilloscope photos as committed evidence. Pattern is fully greenfield. Pattern D above provides the template (filename schema + content requirements + probe-point per pinout + caption template + trigger-timing instructions). Phase 13 inherits Pattern D unchanged per CONTEXT.md D-06 carry-forward clause. |

## Metadata

**Analog search scope:**
- `/workspaces/.planning/phases/08-*/08-MEASUREMENT.md` (chipless wire-protocol bench transcript precedent; lines 322–378 closest by intent)
- `/workspaces/.planning/phases/08-*/08-HUMAN-UAT.md` (manual UAT shape — 2 pending scenarios; closes via this phase)
- `/workspaces/.planning/phases/09-*/09-05-measurement-and-bench-uat-PLAN.md` (most-recent `autonomous: false` operator-on-bench plan; Pattern E source)
- `/workspaces/.planning/phases/09-*/09-MEASUREMENT.md` (most-recent bench-evidence transcription artifact; bench-section + chip-seated-section precedent; BENCH-RESULTS.md primary analog)
- `/workspaces/.planning/phases/11-*/11-PATTERNS.md` (Pattern D markdown-table convention; D-15 orchestrator-owned tracking precedent)
- `/workspaces/.planning/v1.3-COVERAGE-MATRIX.md` (BENCH-coverage cross-reference target; §5 lines 1361–1425)
- `/workspaces/.planning/milestones/v1.0-MILESTONE-AUDIT.md` (requirements/phase results table style; lines 247–294)
- `/workspaces/.planning/STATE.md` (deferred items table + v1.3 phases table — modification targets per Pattern C)
- `/workspaces/firestarter_app/firestarter_test.sh` (harness emitting the bench-log content; Pattern A source)
- `/workspaces/firestarter_app/write_test.sh` (deterministic-image alt-harness reference per CONTEXT.md D-02 note)

**Files scanned:** 10 strong analogs + Phase 12 CONTEXT.md (234 lines, all 15 decisions D-01..D-15) + Phase 12 RESEARCH.md (698 lines, full read across two ranges)

**Pattern extraction date:** 2026-05-20

**Key project-memory rules applied:**
- `[[feedback_always-mirror-uno-leonardo-tests]]` — every chip plan's Task 1 (Uno) is paired with Task 3 (Leonardo). Establishes the convention for v1.3; carried forward into Phase 13.
- `[[project_db-overrides-firmware-is-ground-truth]]` — relevant to PROTO-01 evidence: the safety-stack-blocked-write captures the FIRMWARE path (MSG_ERR_CHIP_ID_MISMATCH 0xB9), not a host preflight. Pattern E `<read_first>` blocks for Plan 12-02 Task 4 cite this memory explicitly so the operator runs WITHOUT `-f` (FLAG_FORCE) per RESEARCH.md Pitfall 6.
- `[[feedback_ic-removal-autonomy]]` — chip swaps between boards proceed autonomously per task; no per-cycle operator confirmation needed (relevant to Plan 12-01/02/03 Task 2 board-swap subtasks).
- `[[project_leonardo-shield-socket-wonky]]` — if Leonardo readback / verify diverges from Uno's green cycle on a chip-seated step, suspect chip-socket contact first; re-seat before declaring a phase regression. Cited in every chip plan's Leonardo-cycle task `<how-to-verify>` block.

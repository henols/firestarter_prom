# Phase 27: Root Cause Analysis — Pattern Map

**Mapped:** 2026-05-21
**Files analyzed:** 1 modified (narrative-append) + 0 created; 2 Wave-B-conditional candidates (informational only)
**Analogs found:** 1/1 (exact analog within same file)
**Phase type:** narrative-append (zero new source files)

## Phase-Type Note

Phase 27 is a **narrative-append phase**. The deliverable is prose appended to a
single existing Markdown file (`.planning/v1.6-EVIDENCE.md`). There is no Python
module, no Arduino source file, no test file to create. Wave A (the only autonomous
wave per CONTEXT.md D-01 / D-07) is desk-side analysis + Markdown authoring against
already-committed evidence binaries and read-only sub-repo source.

This makes PATTERNS.md intentionally short: one file modified, one analog. The
"read-only evidence base" subsection lists the files Phase 27 grep/reads for
evidence but does NOT modify (those go into the RCA narrative as citations, not as
edits).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `.planning/v1.6-EVIDENCE.md` (append `## Phase 27 — RCA Findings` section) | docs / evidence-accretion artifact | append-only narrative + optional 9-column row | The Phase 26 contributions to the *same file* at commits `59e207b` (scaffold) and `5288a48` (baseline rows + Verdict + Scope + Hardware-metadata + Phase 27 entry-conditions) | **exact** (same file, same accretion pattern, same author voice) |

## Pattern Assignments

### `.planning/v1.6-EVIDENCE.md` — append `## Phase 27 — RCA Findings`

**Analog:** Phase 26's authoring of the same file. The file as-of `5288a48` contains
the full template Phase 27 must match: `## Phase N — <title>` H2 header, `### <Subsection>`
H3 subsections under it, a 9-column row schema for evidence rows, and HTML-comment
sentinels at line 20-22 reserving the slot for the Phase 27 / Phase 28 / Phase 29
sections.

#### Pattern 1 — H2 phase-section header shape

**Source:** `.planning/v1.6-EVIDENCE.md:12`

```markdown
## Phase 26 — Pre-fix Consistency-Check Baseline (2026-05-21)
```

**Copy this exact shape for Phase 27.** The HTML-comment sentinel at line 20 already
names it verbatim: `## Phase 27 — RCA Findings`. Do not add the date in parentheses
unless the planner chooses to (the Phase 26 example does; the sentinel comment does
not). Per D-04, the Phase 27 section appends *immediately after* the line-20 HTML
sentinel (so the sentinel remains in place above it for Phase 28 / Phase 29 to find).

#### Pattern 2 — H3 subsection structure under the phase H2

**Source:** `.planning/v1.6-EVIDENCE.md:24-55` (the "Verdict", "Scope changes captured
during the bench session", "Hardware metadata snapshot", "Phase 27 entry conditions"
H3 subsections under the single Phase 26 H2)

```markdown
## Phase 26 — Pre-fix Consistency-Check Baseline (2026-05-21)

| Board | Port | Chip | ... |
|-------|------|------|-----|
| ... |

<!-- sentinels ... -->

## Verdict

**REPRO-01:** CLOSED ✓ — uno verdict PASS captured ...
**REPRO-02:** CLOSED ✓ — leonardo verdict FAIL captured ...
**REPRO-03:** CLOSED ✓ — diagnostic CLI ...

### Scope changes captured during the bench session
1. ...
2. ...

### Hardware metadata snapshot
| Board | Effective hw rev ... |
| ... |

### Phase 27 entry conditions
- Empirical signal: ...
- ...
```

**Apply to Phase 27.** The Phase 27 H2 should follow the same H3 cadence. RESEARCH.md
§"Tasks-and-Files Map" task A9 enumerates the recommended subsections:

```markdown
## Phase 27 — RCA Findings

[2-5 paragraph RCA-02 WHY narrative; lift from RESEARCH.md §"Detailed RCA-02 Narrative"]

### Hypothesis Disposition
| Rank | Hypothesis | Verdict | Confidence | Evidence cite |
| ... |

### Introducing-commit triangulation (RCA-03)
[milestone-bracket = pre-v1.0; cite tag-walk evidence from RESEARCH.md §"Code Examples — introducing-commit triangulation query"]

### GATE-1.6 Risk Assessment
[three named axes per D-09 — write-path timing / VPP regulator engagement / chip-programming pulse intervals — affirmative no-risk verdicts]

### Documentation drift correction targets (per D-11)
[six locations listed in RESEARCH.md §"Documentation Drift Correction Targets"; the call-out only — direct edits land in later phases]

### Fix sketch (Phase 28 handoff)
[candidate fix shape — Uno-side df5fb44 mirror to Leonardo + optional _NOP() settling]

### (optional, planner's call) Hex-dump appendix
[L1[0x1000..0x101F] = 10 01 02 03 ... side-by-side vs L2 / L3 — useful because H2 wins per CONTEXT.md §"Claude's Discretion"]
```

#### Pattern 3 — Voice / tone / per-paragraph density

**Source:** `.planning/v1.6-EVIDENCE.md:26-28` (Verdict block — REPRO-01/02/03)

```markdown
**REPRO-02:** CLOSED ✓ — leonardo verdict FAIL captured (3 distinct SHAs across 3 consecutive 64KB reads; 1349 / 65536 bytes diverge between run_1 and run_2 = 2.1% byte-jitter rate; first divergence at offset `0x0003`). Jitter reproduced — the read-bug exists on the Leonardo and is therefore the primary Phase 27 RCA target. Suspects: 32U4 USB-CDC implementation (vs the 328P's external USB-to-UART bridge), 1024-byte DATA_BUFFER vs Uno's 512-byte buffer, or 32U4-specific timing in the per-chunk send code path.
```

**Match this voice in the Phase 27 RCA-02 narrative:** dense, evidence-citing, no
bullet-point dilution, em-dash-separated clauses. Concrete numbers (`1349 / 65536`,
`2.1%`, `0x0003`) inline with the prose. Inline file references using
`backticked/relative/path:line` shape (e.g., `firestarter/platformio.ini:64-65`).

**Critical drift-correction note:** REPRO-02 quoted above contains the exact
"1024-byte DATA_BUFFER" documentation drift D-11 mandates correcting. The Phase 27
narrative MUST cite this very paragraph as an instance of the drift (per D-11's
location-list including `v1.6-EVIDENCE.md:27`) — i.e., Phase 27 references but does
not edit Phase 26's section (anti-pattern per RESEARCH.md §"Anti-Patterns to Avoid":
"Modifying the v1.6-EVIDENCE.md Phase 26 section in place").

#### Pattern 4 — 9-column row schema (apply ONLY if Phase 27 adds new evidence rows)

**Source:** `.planning/v1.6-EVIDENCE.md:14-18` (Phase 26 baseline rows)

```markdown
| Board | Port | Chip | N | SHAs distinct | Divergent bytes (run1 vs run2) | First-diverge offset | Verdict | Log |
|-------|------|------|---|---------------|------------------------------|----------------------|---------|-----|
| leonardo | /dev/ttyACM1 | W27C512 (id 0xda01) | 3 | 3 | 1349 / 65536 (2.1%) | 0x0003 | FAIL (jitter reproduced — 32U4 USB-CDC + 1024-B buffer path) | `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/` |
```

**Apply only if Wave B fires** and produces a new evidence row (instrumented FW build
re-run). Wave A's deliverable is free-form prose per D-04 — no new rows expected.
If Wave A is sufficient (HIGH-confidence per RESEARCH.md), this pattern is dormant.

#### Pattern 5 — HTML-comment sentinels reserving downstream-phase slots

**Source:** `.planning/v1.6-EVIDENCE.md:20-22`

```markdown
<!-- Phase 27 RCA appends a section here: ## Phase 27 — RCA Findings. Same 9-column schema is the contract — do NOT modify or expand. See CONTEXT.md §D-08. -->
<!-- Phase 28 appends commit refs here: ## Phase 28 — Fix Commit References. -->
<!-- Phase 29 inverts here: ## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD). Same 9-column row schema; Verdict cells flip from FAIL to PASS, SHAs distinct cells go from N to 1. -->
```

**Phase 27 preserves these comments** — the Phase 27 H2 section appends *between*
the line-20 comment (Phase 27 slot) and the line-21 comment (Phase 28 slot), or
immediately after the line-20 comment with the line-21/22 comments shifting
downward as the file grows. Do not delete the sentinels; Phase 28 / Phase 29 still
need them.

## Shared Patterns

### Evidence-accretion narrative artifact

**Source:** `.planning/v1.6-EVIDENCE.md` (Phase 26 sections) — established by D-04 of
Phase 27 CONTEXT.md.
**Apply to:** The single file modified by Phase 27.
**Pattern:** Append-only sections (one `## Phase N — <title>` H2 per phase); never
edit prior-phase sections; HTML-comment sentinels mark insertion slots; 9-column
row schema is locked across all v1.6 phases per Phase 26 D-08.

### Inline file-reference shape

**Source:** Throughout `.planning/v1.6-EVIDENCE.md` Phase 26 sections (e.g., line 30:
`firestarter_app sub-repo commit 999c3cc on v1.6-read-bug, cut from beta at 3.0.0b4`).
**Apply to:** Every code-citation in the Phase 27 RCA narrative.
**Pattern:** Backticked relative path + line range (`firestarter/src/boards/leonardo_rurp_shield.cpp:112-129`),
or backticked commit SHA + branch context. No hyperlinked Markdown — plain backticks.

### Hypothesis-disposition table column shape

**Source:** RESEARCH.md §"Hypothesis Disposition Summary Table" (already pre-formatted
for lift-and-paste into the Phase 27 H2 section).
**Apply to:** The `### Hypothesis Disposition` H3 inside Phase 27's H2.
**Pattern:** 5-column table (Rank | Hypothesis | Verdict | Confidence | Evidence cite).
Verdict values: `CONFIRMED` / `REFUTED` / `OUT OF SCOPE`. Confidence values:
`HIGH` / `MEDIUM` / `LOW`. Evidence cite is a backticked file/path/line citation,
optionally with a 1-sentence rationale appended after an em-dash.

## Read-Only Evidence Base (Phase 27 reads these — does NOT modify)

These files are the substrate Phase 27 grep/reads to build the RCA narrative. They
are NOT in the "files modified" list — they are evidence sources, not deliverables.
Listed per RESEARCH.md §"Sources" and §"Tasks-and-Files Map":

| File | Lines | Why Phase 27 reads it |
|------|-------|-----------------------|
| `firestarter/src/boards/leonardo_rurp_shield.cpp` | 112-141 | **THE BUG** — `rurp_read_data_buffer` (112-129) + `rurp_set_data_input` (137-141). H2 corruption site. RCA-01 cites this. |
| `firestarter/src/boards/uno_rurp_shield.cpp` | 120-137 | **THE CONTRAST** — `rurp_read_data_buffer` (120-122; direct PIND read) + `rurp_set_data_input` (128-137; the `df5fb44` PORTD=0x00 fix). RCA-02 cites this as "the fix the Leonardo lacks". |
| `firestarter/src/boards/rurp_serial_utils.cpp` | 190-227 | **H1 REFUTATION** — `_firestarter_emit_frame_wide` is shared by both boards; Uno PASSes; therefore emitter is not the bug. Cited in hypothesis disposition. |
| `firestarter/src/eprom_operations.cpp` | 110-132 | **H3 REFUTATION** — `_process_outgoing_data` per-chunk send loop; shared with Uno. |
| `firestarter/platformio.ini` | 64-65 (the `; TEMP: 512 ...` comment) | **D-05 / D-11 SOURCE-OF-TRUTH** — proves Leonardo and Uno both run at `DATA_BUFFER_SIZE=512`. Refutes the 1024-byte hypothesis (H6 / bug-report H4) and the docs-drift in 6 listed locations. |
| `firestarter/include/firestarter.h` | 18-20 | `DATA_BUFFER_SIZE` default = 512 (corroborates platformio.ini override). |
| `firestarter_app/firestarter/serial_comm.py` | 385-616 (`_decode_id_frame` 385-489, `_read_and_parse_lines` 491-616) | **H1 / H4 REFUTATION** — host parser is sound; CRC mismatch behavior is reject-and-resync (line 411-414), not accept-corrupted; rules out CRC false-positive. |
| `firestarter_app/firestarter/eprom_operations.py` | 353-391 (`_main_phase_read_data`), 431+ (`consistency_check_eprom`) | Confirms diagnostic tool exercises the bug path verbatim (D-03 reuse property). |
| `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_01.bin` | full 65,536 B | H2 EVIDENCE — first-divergence offset, single-bit-flip distribution, address-bit correlation, partially-erased chip detection. |
| `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_02.bin` | full 65,536 B | H2 EVIDENCE — 1349 divergent positions vs run_01; 78% single-bit-flip fraction. |
| `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_03.bin` | full 65,536 B | H2 EVIDENCE — flicker-prone-position rate across N=3. |
| `.planning/v1.6/consistency-check-runs/W27C512-uno-20260521-133418/run_01.bin` | full 65,536 B | REFERENCE — Uno PASS binary; "looks like genuine EPROM content" contrast (`37 d4 71 0e ab 48 ...` vs Leonardo's `00 01 02 83 04 05 ...`). |
| `.planning/v1.6/consistency-check-runs/W27C512-uno-20260521-133418/run_02.bin` | full 65,536 B | REFERENCE — same SHA as run_01 (PASS). |
| `.planning/v1.6/consistency-check-runs/W27C512-uno-20260521-133418/run_03.bin` | full 65,536 B | REFERENCE — same SHA as run_01 / run_02. |
| `.planning/v1.6/bench-logs/W27C512-leonardo-20260521-134210.log` | full | **H4 REFUTATION** — grep for `CRC mismatch` returns nothing; CRC false-positive ruled out. |
| `.planning/v1.6/bench-logs/W27C512-uno-20260521-133418.log` | full | REFERENCE — clean Uno log for cross-comparison. |
| Firmware git history: `git show 2.0.{2..6}:src/boards/leonardo_rurp_shield.cpp` | tag-walk | RCA-03 milestone-bracket — confirms structural identity of `rurp_read_data_buffer` from 2.0.2 forward. |
| Firmware git history: `git show 5b1f1cd` ("Leonardo is working, fast as a shark", 2025-02-11) | single commit | Introduction of the current shift-and-mask read function (replaced earlier loop-based variant). |
| Firmware git history: `git show df5fb44` ("fix(uno): disable PORTD pullups on data-input transition", 2026-05-13) | single commit | The Uno-side fix that was never mirrored to Leonardo. |
| Firmware git history: `git show 1abadaa` (W-04 frame-wide, Phase 8 / v1.2 / 2026-05-18) | single commit | Introduction of `_firestarter_emit_frame_wide` — NOT the bug source, but the RCA-03 anchor for why the v1.2 milestone is *not* the bug-introducing milestone (the bug predates `_firestarter_emit_frame_wide`). |

## Wave B Candidate Files (CONDITIONAL — won't run by default)

**This subsection is informational scaffolding only.** Per D-01 / D-03 / D-12 the
firmware sub-repo branch `firestarter/v1.6-read-bug` is only cut if Wave A's
verifier reports `needs_bench: true`. RESEARCH.md §"Wave B Trigger Criteria" shows
none of the three D-01 triggers fire (HIGH confidence Wave A closes). The candidate
files below are listed so the planner has the skeleton when drafting Plan 27-02 but
SHOULD NOT execute against them.

| Candidate file | Wave B edit shape | Analog (NOT for execution) |
|----------------|-------------------|----------------------------|
| `firestarter/platformio.ini` (Wave B only) | Add `-D RCA_INSTRUMENT_*` build flags inside the `[env:leonardo]` block (currently lines 57-65). Single-block addition mirroring the existing `-D DATA_BUFFER_SIZE=512` line. | The existing `[env:leonardo]` block IS its own analog — append flags to the same block; do not create a new env. |
| `firestarter/src/boards/leonardo_rurp_shield.cpp` (Wave B only) | Wrap `rurp_read_data_buffer` (lines 112-129) with `#ifdef RCA_INSTRUMENT_*` instrumentation. Candidate instrumentation point per CONTEXT.md §"Claude's Discretion". | The function itself is its own analog — instrumentation is a wrap, not a rewrite. |
| `firestarter_app/firestarter/eprom_operations.py` (Wave B only, if host-side trace flag is needed) | Add `--rca-trace` flag to `dev consistency-check` (lines 431+). Mirror existing flag-handling in the same module. | The existing `dev consistency-check` CLI surface from Phase 26's `999c3cc`. |

**Branch flow if Wave B fires (per D-03 / D-12):**
- Cut `firestarter/v1.6-read-bug` from `beta@3.0.0b4` (the same tip Phase 26 referenced; verified at research time `beta` HEAD = `d955846` = tag `3.0.0b4`).
- Land instrumentation flags as a SINGLE commit on the new branch.
- Use the existing `firestarter_app/v1.6-read-bug` branch (already exists from Phase 26) for any host-side instrumentation.
- Meta-repo (`.planning/`) stays on `main`.

## No Analog Found

(None. The single file Phase 27 modifies has an exact in-file analog from Phase 26.)

## Metadata

**Analog search scope:**
- `.planning/v1.6-EVIDENCE.md` (the file itself — primary analog source)
- `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/` (Phase 26 plans / context / summaries for cross-phase pattern continuity)
- `.planning/v1.{3,5}-{BENCH-RESULTS,EVIDENCE}.md` (cross-phase evidence-accretion precedent referenced by RESEARCH.md §"Architecture Patterns / Pattern 1")
- Firmware + host sub-repo source files listed in §"Read-Only Evidence Base" (search scope verified by RESEARCH.md §"Sources")

**Files scanned:** ~25 (1 modified target, ~17 read-only evidence sources, ~4 git-history commits, ~3 Wave-B-conditional candidate files)

**Pattern extraction date:** 2026-05-21

**Confidence:** HIGH — the analog is the same file authored by the immediately-prior
phase; voice / structure / schema are directly transferable. No interpretive gap.

**Downstream notes for the planner:**
1. Plan 27-01 (Wave A) writes the Phase 27 H2 section; lift the lift-and-paste-ready
   subsections from RESEARCH.md §"Detailed RCA-02 Narrative" + §"Hypothesis Disposition
   Summary Table" + §"GATE-1.6 Risk Assessment" + §"Documentation Drift Correction
   Targets".
2. Plan 27-02 (Wave B) is DRAFTED but flagged `autonomous: false` and `executes_only_if: needs_bench`.
   Per RESEARCH.md §"Wave B Trigger Criteria" all three triggers are NOT triggered;
   the verifier in Plan 27-01 should report `needs_bench: false`.
3. The "5-line Python disambiguation" from RESEARCH.md §"Code Examples — Binary
   cross-check" is the cheapest fallback if a future reviewer doubts the H2 verdict —
   include it in the RCA narrative as an inline reproducible check (recommended).

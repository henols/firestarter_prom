---
phase: 85-datasheet-acquisition
verified: 2026-06-25T16:00:00Z
status: human_needed
score: 4/4 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Spot-open 2-3 PDFs and confirm title-page part number matches the README row"
    expected: "Each opened PDF shows a title page or first page identifying the chip matching the README row; substitute/representative flags are honest"
    why_human: "The %PDF magic-byte check confirms real PDFs were committed, but content identity (right title-page part number vs. a plausible but wrong document) cannot be asserted programmatically — requires a human to open the file."
  - test: "Confirm representative exemplar picks for the 6 no-silicon buckets are reasonable"
    expected: "Operator reviews the 6 no-silicon picks (AT28C256, DS1245Y, Intel-28F010, 6116, DS1245Y-as-DS1250Y-sub, X88C64 data book) against the bucket algorithm and agrees they are adequate algorithm references"
    why_human: "Editorial judgment (D-06 'best-documented exemplar') — cannot be programmatically verified"
---

# Phase 85: Datasheet Acquisition Verification Report

**Phase Goal:** Every protocol has a committed datasheet PDF so the naming pass and future bench sessions have a verification source for each algorithm.
**Verified:** 2026-06-25T16:00:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A `datasheets/<hex>-<NAME>/` folder exists for each of the 11 on-hand chip families with a committed PDF | VERIFIED | 11 PDFs confirmed present under 0x05/0x06/0x07/0x08/0x0B/0x28; all pass `%PDF` magic-byte check; git commit `83313fc` shows 17 datasheets/ paths only |
| 2 | A `datasheets/<hex>-<NAME>/` folder exists for each of the 6 no-silicon protocol buckets with at least one representative datasheet PDF | VERIFIED | 6 bucket dirs confirmed: 0x0D/0x0E/0x10/0x27/0x29/0x34; each holds a real PDF (>1k, `%PDF` magic); git commit `83313fc` |
| 3 | `datasheets/README.md` indexes every folder (hex ID ↔ proposed name ↔ handler ↔ datasheet filename ↔ on-hand status), explicitly names the phantom/infeasible exclusions, and annotates provenance | VERIFIED | README.md (172 lines) contains all 12 bucket rows + all 6 excluded hex IDs (0x35/0x39/0x11/0x2A/0x2B/0x2C); D-02/D-03 policy documented; 2516 no-DB-entry note present; per-file provenance table (17 rows) with source URL + retrieval date + substitute flag; git commit `45fed04` |
| 4 | No new third-party tool or library introduced — only new artifact is `datasheets/` folder tree (SAFE-05) | VERIFIED | All three phase commits (11a7c7f, 83313fc, 45fed04) touch ONLY paths under `datasheets/`; confirmed via `git show --name-only` on each commit; no platformio.ini/pyproject.toml/src modifications |

**Score:** 4/4 truths verified

### Deferred Items

None.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/datasheets/datasheets-check.sh` | Wave-0 structural gate, ≥30 lines, executable, covers DSHEET-01/02/03+SAFE-05 | VERIFIED | 100 lines, executable (`chmod +x`), `set -euo pipefail`; all 12 expected buckets named; all 6 forbidden IDs checked; README existence + exclusion grep; %PDF magic-byte check; exits 0 on PASS |
| `firestarter/datasheets/0x07-EPROM-STD/W27C512.pdf` | On-hand 0x07 EPROM-STD datasheet | VERIFIED | Present, 172 KB, `%PDF` magic confirmed |
| `firestarter/datasheets/0x07-EPROM-STD/W27E512.pdf` | W27E512 filed under 0x07 (not 0x08) | VERIFIED | Present under 0x07-EPROM-STD; correct per DB (algorithm=7, shared silicon entry with W27C512) |
| `firestarter/datasheets/0x28-SRAM-STD/FM1608.pdf` | FM1608 filed under 0x28 | VERIFIED | Present under 0x28-SRAM-STD; correct per DB (algorithm=40 decimal = 0x28, type=FRAM) |
| `firestarter/datasheets/0x05-FLASH-AMD-STD/W29C020.pdf` | On-hand 0x05 FLASH-AMD-STD datasheet | VERIFIED | Present, 289 KB, `%PDF` magic confirmed |
| `firestarter/datasheets/0x34-EEPROM-X88C64/X88C64.pdf` | No-silicon 0x34 representative (Xicor data book) | VERIFIED | Present, 25.2 MB, `%PDF` magic confirmed; README correctly marks as `data-book` not a leaflet |
| `firestarter/datasheets/README.md` | DSHEET-03 index, ≥40 lines, contains `0x35` | VERIFIED | 172 lines; contains all 18 hex IDs (12 bucket + 6 exclusion); D-08 columns present; D-02/D-03 policy documented; 2516 no-DB-entry note |

All 17 PDFs present, each >1k and `%PDF`-magic verified. Full list:

| Bucket | Filename | Size | %PDF | Notes |
|--------|----------|------|------|-------|
| 0x05-FLASH-AMD-STD | W29C020.pdf | 289 KB | OK | exact |
| 0x05-FLASH-AMD-STD | W29C040.pdf | 257 KB | OK | exact |
| 0x06-FLASH-AMD-ALT | SST39SF040.pdf | 1.5 MB | OK | exact |
| 0x07-EPROM-STD | W27C512.pdf | 172 KB | OK | exact |
| 0x07-EPROM-STD | W27E512.pdf | 193 KB | OK | exact-family |
| 0x07-EPROM-STD | SST27SF512.pdf | 335 KB | OK | family-substitute (SST27SF256 family doc) |
| 0x07-EPROM-STD | ST-M27C512.pdf | 269 KB | OK | exact |
| 0x08-EPROM-QUICK | W27E040.pdf | 172 KB | OK | family-substitute (W27C512 bitsavers family doc) |
| 0x08-EPROM-QUICK | AM27C020.pdf | 89 KB | OK | exact |
| 0x0B-EPROM-LEGACY | 2516_EPROM.pdf | 671 KB | OK | exact (no chip_database.json entry — user-override) |
| 0x28-SRAM-STD | FM1608.pdf | 144 KB | OK | exact |
| 0x0D-EEPROM-POLL | AT28C256.pdf | 660 KB | OK | exact (no-silicon rep) |
| 0x0E-SRAM-32PIN | DS1245Y.pdf | 221 KB | OK | exact (no-silicon rep) |
| 0x10-FLASH-INTEL | Intel-28F010.pdf | 407 KB | OK | exact (no-silicon rep) |
| 0x27-SRAM-24PIN | 6116.pdf | 91 KB | OK | exact (no-silicon rep) |
| 0x29-SRAM-512K-1M | DS1245Y.pdf | 221 KB | OK | substitute (DS1250Y curl-blocked, DS1245Y sibling filed) |
| 0x34-EEPROM-X88C64 | X88C64.pdf | 25.2 MB | OK | data-book (1990 Xicor Data Book scan) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `datasheets-check.sh` | `datasheets/<bucket>/*.pdf` | `find + head -c4 %PDF magic-byte assertion` | WIRED | Script iterates `expected_buckets` list, runs `head -c4 "$f" \| grep -q '%PDF'` on each PDF found; confirmed live PASS |
| `datasheets/README.md` | `datasheets/<bucket>/*.pdf` | Every bucket row filename references a real committed file | WIRED | All 17 filenames named in README exist on disk; WARN lines from check script are from source URLs in provenance table (URL path segments containing `.pdf`), not from filename references — script exits 0 |
| Phase commits | `datasheets/` only | SAFE-05: explicit `git add datasheets/...` in each task | WIRED | `git show --name-only` for 11a7c7f, 83313fc, 45fed04 — all paths begin with `datasheets/`; no src/, include/, test/, platformio.ini paths |

### Data-Flow Trace (Level 4)

Not applicable — this phase produces static document assets (PDFs + README). No dynamic data rendering, no state variables, no fetch/store patterns. Level 4 data-flow tracing is irrelevant for a static-asset commit phase.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Phase-gate script prints `datasheets-check: PASS` and exits 0 | `cd /workspaces/firestarter && bash datasheets/datasheets-check.sh; echo "Exit: $?"` | 10 WARN lines (README source-URL path segments, expected non-defects per task instructions) + `datasheets-check: PASS` + `Exit: 0` | PASS |
| All 17 PDFs have `%PDF` magic bytes | `cd /workspaces/firestarter && for f in datasheets/*/*.pdf; do head -c4 "$f"; echo; done` | All 17 print `%PDF` | PASS |
| No forbidden bucket directories exist | `ls datasheets/0x35* datasheets/0x39* datasheets/0x11* datasheets/0x2A* datasheets/0x2B* datasheets/0x2C* 2>/dev/null` | No output (no forbidden dirs) | PASS |
| W27E512 is filed under 0x07-EPROM-STD, not 0x08 | `ls firestarter/datasheets/0x07-EPROM-STD/W27E512.pdf` | File present under 0x07 | PASS |
| FM1608 is filed under 0x28-SRAM-STD | `ls firestarter/datasheets/0x28-SRAM-STD/FM1608.pdf` | File present under 0x28 | PASS |
| All three phase commits touch only `datasheets/` paths | `git show --name-only 11a7c7f 83313fc 45fed04` | All file paths in each commit begin with `datasheets/` | PASS |

### Probe Execution

No `probe-*.sh` files were declared or referenced for this phase. The authoritative gate is `datasheets-check.sh`, which was run as a behavioral spot-check above (PASS, exit 0).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| DSHEET-01 | 85-02-PLAN.md | 11 on-hand IC datasheets committed under `datasheets/` | SATISFIED | All 11 PDFs present in DB-correct bucket folders; each >1k and `%PDF` |
| DSHEET-02 | 85-02-PLAN.md | Every no-silicon protocol bucket has ≥1 representative datasheet | SATISFIED | 6 no-silicon buckets (0x0D/0x0E/0x10/0x27/0x29/0x34) each have a real PDF committed |
| DSHEET-03 | 85-03-PLAN.md | `datasheets/README.md` indexes hex↔name↔handler↔file↔status + exclusions + provenance | SATISFIED | README.md (172 lines) has all required columns and all 18 hex IDs; check script passes |
| SAFE-05 | 85-01-PLAN.md, 85-03-PLAN.md | No new third-party dependency; only new artifact is `datasheets/` | SATISFIED | All 3 commits verified `datasheets/`-only; no platformio.ini/pyproject.toml edits; `datasheets-check.sh` enforces structural shape |

Note: REQUIREMENTS.md traceability table still shows DSHEET-03 as "Pending" (line 89). This is a stale tracking state in the planning artifact — the commit `45fed04` delivered the README and the phase gate PASSes. The tracking checkbox should be updated, but this does not reflect a code gap.

### Anti-Patterns Found

No source code was modified in this phase (static-asset only). Anti-pattern scanning for code smells is not applicable. The check script itself (`datasheets-check.sh`) was scanned:

- No `TBD`, `FIXME`, `XXX`, `TODO`, or `PLACEHOLDER` markers
- No empty implementations or stub returns
- All assertions are substantive (not bypassed)
- `set -euo pipefail` for strict error handling

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | None found | — | — |

### Human Verification Required

Two items require human review per the VALIDATION.md §"Manual-Only Verifications" contract. These were planned verification items deferred from automated checking by design:

#### 1. PDF Content Identity Spot-Check

**Test:** Open 2-3 PDFs from the committed tree and confirm the title page or first page of each PDF shows the part number matching the README row. Suggested candidates: `0x07-EPROM-STD/W27C512.pdf` (exact, primary), `0x08-EPROM-QUICK/W27E040.pdf` (family-substitute — confirm it is a Winbond EPROM family document rather than an unrelated PDF), `0x29-SRAM-512K-1M/DS1245Y.pdf` (substitute — confirm it is a Dallas DS1245Y NVRAM datasheet, filed as a stand-in for DS1250Y).

**Expected:** Each PDF's title page or first section clearly identifies the chip family documented. Substitute/representative flags in the README match what the PDF actually contains.

**Why human:** The `%PDF` magic-byte check confirms real PDFs were committed (not HTML interstitials or corrupt files), but content identity — "is this the W27E040 document or did we accidentally commit the wrong Winbond file?" — requires a human to open and read the first page.

#### 2. No-Silicon Exemplar Quality Review

**Test:** Review the 6 no-silicon bucket representatives in README against each bucket's algorithm purpose. Specifically: AT28C256 for 0x0D (SDP-unlock + page-poll), DS1245Y for 0x0E (12V VPP write-protect-bypass), Intel-28F010 for 0x10 (command-register architecture), 6116 for 0x27 (24-pin async SRAM JEDEC pinout), DS1245Y-substitute for 0x29 (Dallas battery-backed NVRAM family), X88C64 data-book for 0x34 (ALE-multiplexed address/data bus).

**Expected:** Operator confirms each no-silicon exemplar is a reasonable algorithm reference for its bucket, and that the D-06 "best-documented exemplar" rationale in the README makes sense.

**Why human:** Editorial judgment — cannot be programmatically asserted.

### Gaps Summary

No automated gaps found. All 4 success criteria are verified. All 17 PDFs are real committed documents with `%PDF` magic bytes and sizes >1k. The phase-gate script passes (exit 0). All three commits are confined to `datasheets/` paths (SAFE-05). The README contains all required content.

The only open items are the two manual verification checks documented above — these are planned human review tasks per the VALIDATION.md contract, not failures.

---

## Addendum — Post-Verification Scope Addition (2026-06-25)

After this report was written, the operator confirmed a **W27C020** chip is on hand and it was added to the phase. Reconciliation:

- **New file:** `firestarter/datasheets/0x08-EPROM-QUICK/W27C020.pdf` (164 KB, `%PDF` magic, 6 pp). Commit `bc0892a` on `v1.16-protocol-first-architecture-rebuild`; SAFE-05 verified (only `datasheets/` staged).
- **Bucket:** 0x08-EPROM-QUICK is correct — chip DB entry `W27C02,W27C020,W27E02,W27E020,W27L02`, `algorithm=8`, DIP32_STD, 12V VPP.
- **Content identity:** VERIFIED programmatically (pypdf text extraction) — "Preliminary W27C020 / 256K × 8 ELECTRICALLY ERASABLE EPROM / Revision A1 / September 1998"; part number appears 28×. This file is therefore **exempt from human-verification item #1** (its content is already confirmed).
- **Provenance:** manufacturer-primary — Winbond's own path `winbond.com/PDF/sheet/w27c020.pdf` retrieved via the Wayback Machine (live path now 404s). Flagged `exact` in README.
- **Counts updated:** DSHEET-01 on-hand 11→12; total committed PDFs 17→18. README index/provenance/tree updated. `datasheets-check.sh` still **PASS** (exit 0).
- **Tracking:** REQUIREMENTS.md DSHEET-01 list updated (+W27C020) and DSHEET-03 flipped Pending→Complete (the stale-tracking note above is now resolved).

Net effect on verdict: unchanged. Must-haves remain 4/4; status remains `human_needed` pending the two manual review items (W27C020's own content is no longer among them).

---

_Verified: 2026-06-25T16:00:00Z_
_Verifier: Claude (gsd-verifier)_

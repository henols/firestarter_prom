---
phase: 02-naming-cleanup-wire-key-minipro-references
plan: 03
subsystem: docs-attribution-and-regression-tooling
tags: [clean-02, wire-02, sc5, check-dispatch-augment, minipro-scrub, shape-a, atomic-attribution]

# Dependency graph
requires:
  - phase: 02-naming-cleanup-wire-key-minipro-references
    plan: 01
    provides: WIRE-01 source-state assertion (Python emits "vpp_mv"; firmware parses "vpp_mv")
  - phase: 02-naming-cleanup-wire-key-minipro-references
    plan: 02
    provides: CLEAN-01 file rename + D-04 vpp_volts internal rename + packaging fix (chip_database.json resolves in editable install)
provides:
  - CLEAN-02 attribution scrub (firestarter_app/CLAUDE.md == 1 minipro line; firestarter/CLAUDE.md == 0; database.py / check_dispatch.py == 0; MINIPRO_XML_URL load-bearing constant retained on build_db.py:10)
  - WIRE-02 dynamic regression evidence (check_dispatch.py exits 0 with "0 wire-key regressions" across all 743 chips via per-chip db.convert_to_programmer round-trip)
  - SC#5 CLI smoke discharge (pip install -e . + firestarter --help + firestarter info W27C512 + firestarter info --adapter W27C512 all exit 0)
  - Phase 02 closure (WIRE-01 / WIRE-02 / CLEAN-01 / CLEAN-02 all discharged)
affects:
  - Phase 3 (Retroactive Verification): can now reference the post-Phase-2 wire format (vpp_mv only) and renamed DB filename (chip_database.json) in its audit artifacts
  - Future check_dispatch.py invocations on CI / pre-commit: scanner now gates both static dead-key usage AND dynamic wire-shape regressions in a single binary

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Scanner == single CI gate: static DEAD_KEYS scan + dynamic per-chip wire round-trip fused inside one check_dispatch.py binary (Shape A per RESEARCH.md, beats Shape B parametrize-pytest because it preserves single-tool gate UX)"
    - "Load-bearing-attribution preservation: tools/build_db.py:10 MINIPRO_XML_URL constant verbatim + tools/build_db.py:29 argparse default=\"minipro\" + firestarter_app/CLAUDE.md:68 infoic.xml markdown-link parenthetical (3 surviving attribution sites — 1 in CLAUDE.md prose, 1 constant identifier, 1 CLI default arg)"
    - "Three-CLAUDE.md doc-consistency contract closed: meta CLAUDE.md (0 minipro), firmware CLAUDE.md (0 minipro), host CLAUDE.md (1 minipro at :68 next to infoic.xml)"

key-files:
  created:
    - .planning/phases/02-naming-cleanup-wire-key-minipro-references/02-03-SUMMARY.md
  modified:
    - firestarter_app/firestarter/database.py (:45 + :389 comment scrubs)
    - firestarter_app/tools/check_dispatch.py (:30 comment scrub + module-top EpromDatabase import + main() db_raw rename + db = EpromDatabase() + wire_regressions list + per-chip round-trip block + union-check extension + wire_regressions reporter + PASS-line extension)
    - firestarter_app/tools/build_db.py (:23 comment scrub; :10 MINIPRO_XML_URL preserved)
    - firestarter_app/CLAUDE.md (:42 + :46 + :71 minipro -> upstream; :68 minipro attribution preserved)
    - firestarter/CLAUDE.md (:69 minipro -> upstream)

key-decisions:
  - "Surviving minipro attribution at firestarter_app/CLAUDE.md:68 (the Database Pipeline section opening line containing infoic.xml + chip_database.json) rather than :42 (Key Files bullet) — RESEARCH.md recommended choice; :68 sits next to the actual upstream file path (infoic.xml) and ends in the renamed DB filename, giving a single self-contained provenance pointer."
  - "Plan body referenced line :69 for the host CLAUDE.md surviving attribution; actual current line is :68 (off-by-one shift after Plan 02-02 edits). Used content-based location (line containing infoic.xml + chip_database.json) rather than line numbers — plan body explicitly noted line numbers may shift, and grep -cF returns 1 as required."
  - "Three tasks (02-03-01 D-09/D-10 comment scrub + 02-03-02 D-15 Shape A augmentation + 02-03-03 host CLAUDE.md reduction) collapsed into one firestarter_app/ sub-repo commit (0489a20) per plan body suggestion (\"All four edits in one commit OR part of a larger Plan 02-03 commit\"). Firmware sub-repo CLAUDE.md edit in its own commit (587396a)."
  - "MINIPRO_XML_URL on build_db.py:10 + default=\"minipro\" on :29 preserved verbatim per D-09 (load-bearing). The case-sensitive grep gate (grep -cF minipro) targets lowercase substrings only; the uppercase MINIPRO_XML_URL constant identifier and the surviving lowercase URL substring on :10 satisfy \"single attribution constant\" framing without inflating the CLAUDE.md substring count."
  - "Pre-existing unrelated dirt in firestarter_app/ working tree (deleted .planning/codebase/*.md, version bump in __init__.py, ic_layout.py reformat) preserved un-staged for a future scoped plan, mirroring Plans 02-01 + 02-02 SUMMARY documentation of the same dirt."

patterns-established:
  - "Fused scanner pattern: a single check_dispatch.py binary now reports two distinct failure classes (static dead-key usage + dynamic wire-shape regressions) with a unified PASS/FAIL contract and a single sys.exit(1) point. Future regression classes follow the same shape — declare a new failure list parallel to existing ones, append inside the per-chip loop, extend the union check + reporter block + PASS line trailing fragment."

requirements-completed: [CLEAN-02, WIRE-02]

# Metrics
duration: ~9min
completed: 2026-05-12
---

# Phase 02 Plan 03: CLEAN-02 Attribution Scrub + WIRE-02 Wire Round-Trip + SC#5 CLI Smoke Summary

Closes Phase 02 by reducing minipro references to a single surviving attribution line in host CLAUDE.md (next to `infoic.xml` and `chip_database.json`), augmenting `check_dispatch.py` with a per-chip `db.convert_to_programmer()` round-trip that proves Plan 02-01's wire-key contract holds for all 743 chips, and discharging SC#5 (pip install + --help + info W27C512 + info --adapter W27C512 all exit 0 against the renamed DB with no FileNotFoundError or stale-path leakage).

## Performance

- **Duration:** ~9 min (539 s plan-execution wallclock)
- **Started:** 2026-05-12T08:51:32Z
- **Completed:** 2026-05-12T09:00:31Z
- **Tasks:** 3 / 3 complete (collapsed into 1 app sub-repo commit + 1 firmware sub-repo commit + 1 meta-repo commit per plan body)
- **Files modified (in scope, committed):** 6 — 4 in `firestarter_app/`, 1 in `firestarter/`, plus this SUMMARY.md in the meta-repo
- **Sub-repo commits:** 2 (`firestarter_app`@`0489a20`, `firestarter`@`587396a`)

## Accomplishments

- **Static + dynamic scanner gate landed.** `check_dispatch.py` now runs both the existing 743-chip dispatch scan AND a per-chip `db.convert_to_programmer(db.get_eprom(part))` round-trip, asserting `"vpp_mv" in wire` AND `"vpp" not in wire` for every entry in `chip_database.json`. The scanner reports both stages on success: `PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom; 0 DIP28_2764 Flash/EEPROM chips route to configure_eprom; 0 wire-key regressions`.
- **CLEAN-02 closed end-to-end across all three CLAUDE.md files.** Host CLAUDE.md retains exactly 1 surviving minipro line at `:68` (the Database Pipeline opening, containing `infoic.xml` + `chip_database.json` — single self-contained provenance pointer). Firmware CLAUDE.md and meta CLAUDE.md both contain zero minipro substrings. `firestarter_app/firestarter/database.py` and `firestarter_app/tools/check_dispatch.py` both contain zero minipro substrings.
- **Load-bearing attribution constant preserved verbatim.** `firestarter_app/tools/build_db.py:10 MINIPRO_XML_URL` is byte-identical to pre-edit state; the only edit in that file was the softened `:23` comment per D-09. `build_db.py:29 default="minipro"` argparse arg is also preserved.
- **SC#5 CLI smoke fully discharged.** All four required invocations exit 0 against the editable-installed firestarter_app/ with the renamed `chip_database.json`:
  - `pip install -e .` — Successfully installed firestarter-2.0.5.
  - `firestarter --help` — exit 0; 28 lines of CLI usage output, no error text.
  - `firestarter info W27C512` — exit 0; 45 lines of chip metadata (VCC/VPP/pin_count/manufacturer + DIP-layout output).
  - `firestarter info --adapter W27C512` — exit 0; 63 lines (chip metadata + adapter pin-mapping table); exercises both `pinouts.json` read path and `get_adapter_table()` — no `KeyError` from the renamed dict key.
- **Phase 02 contract fully discharged.** WIRE-01 (Plan 02-01), WIRE-02 (this plan), CLEAN-01 (Plan 02-02), CLEAN-02 (this plan) all closed. Phase 02 ready for `/gsd-verify-work`.

## Task Commits

Each task landed atomically; sub-repos have independent git histories:

1. **Tasks 02-03-01 + 02-03-02 + 02-03-03 host-side (collapsed per plan body):** D-10 verbatim comment scrub (4 files; 4 edits) + D-15 Shape A wire round-trip augmentation in `check_dispatch.py` + host CLAUDE.md minipro reduction to 1 surviving line. `firestarter_app@0489a20` (`CLEAN-02 + WIRE-02: minipro attribution scrub + check_dispatch.py wire round-trip + SC#5 smoke`).
2. **Task 02-03-03 firmware-side:** firestarter/CLAUDE.md:69 `minipro` → `upstream` prose flip. `firestarter@587396a` (`docs(02-03): drop final minipro reference from CLAUDE.md (D-11)`).

**Parent-repo metadata commit** (this commit): submodule pointer bumps for both sub-repos + this SUMMARY.md + STATE.md + ROADMAP.md updates.

## Files Created/Modified

### firestarter_app/ (Python application sub-repo) — commit 0489a20

- `firestarter/database.py` — 2 single-line comment edits:
  - `:45` — `# Algorithm (minipro protocol_id) → firmware mem_type integer.` → `# Algorithm integer (upstream protocol_id from infoic.xml) → firmware mem_type integer.`
  - `:389` — `# Read algorithm integer directly — set by build_db.py as minipro protocol_id` → `# Read algorithm integer directly — set by build_db.py from upstream protocol_id`
- `firestarter_app/tools/check_dispatch.py`:
  - `:30` — comment scrub identical to `database.py:45`.
  - Module-top: added `from firestarter.database import EpromDatabase` (third-party import position per PEP 8).
  - `main()`: renamed `db = json.load(f)` local to `db_raw`; instantiated `db = EpromDatabase()` parallel; added `wire_regressions = []` sibling failure list; per-chip loop now calls `db.get_eprom(part)` + `db.convert_to_programmer(mapped)` and appends to `wire_regressions` on either missing `vpp_mv` or present `vpp`.
  - Union failure check extended with `or wire_regressions`; new `if wire_regressions:` reporter block mirrors the existing `sram_in_eprom` / `eeprom28c_in_eprom` blocks (header line + `[:20]` slice + `... and N more` overflow).
  - Final PASS line trailing fragment extended with `; 0 wire-key regressions`.
- `firestarter_app/tools/build_db.py:23` — `# This map translates the numeric protocol ID from minipro's XML` → `# This map translates the numeric protocol ID from upstream's XML`. `:10 MINIPRO_XML_URL` constant + `:29 default="minipro"` argparse arg preserved verbatim per D-09.
- `firestarter_app/CLAUDE.md` — 3 single-line minipro neutralizations:
  - `:42` — `parses minipro \`infoic.xml\`` → `parses the upstream \`infoic.xml\``
  - `:46` — `carries the minipro \`protocol_id\` integer` → `carries the upstream \`protocol_id\` integer`
  - `:71` — `- algorithm — minipro \`protocol_id\` integer` → `- algorithm — upstream \`protocol_id\` integer`
  - `:68` — KEPT as the single surviving attribution line: `\`tools/build_db.py\` parses \`tools/infoic.xml\` (minipro chip database XML) and outputs \`firestarter/data/chip_database.json\`.` (post-Plan-02-02 line-number shift from the plan body's nominal `:69`; the content is the same authoritative-source pointer D-12 intends).

### firestarter/ (Arduino firmware sub-repo) — commit 587396a

- `firestarter/CLAUDE.md:69` — `The \`algorithm\` field (integer, minipro \`protocol_id\`) is parsed into \`handle->protocol\` and is the primary dispatch key.` → `The \`algorithm\` field (integer, upstream \`protocol_id\`) is parsed into \`handle->protocol\` and is the primary dispatch key.` The substantive claim (integer `algorithm` field → `handle->protocol` is the primary dispatch key) is unchanged.

### meta-repo (firestarter_prom) — this commit

- `.planning/phases/02-naming-cleanup-wire-key-minipro-references/02-03-SUMMARY.md` — this file.
- Two submodule pointer bumps (firestarter → 587396a; firestarter_app → 0489a20).
- STATE.md + ROADMAP.md updates (Phase 02 marked complete, plan counter advanced past Plan 03).

## Decisions Made

- **Surviving attribution at `firestarter_app/CLAUDE.md:68`, not `:42`.** RESEARCH.md "Missed Callsites" gave the binary choice; `:68` is co-located with `infoic.xml` (the actual upstream file) and ends with `chip_database.json` (the renamed local artifact). One self-contained provenance pointer beats two non-adjacent half-attributions.
- **Plan body `:69` line number stale.** Post-Plan-02-02 line shifts placed the Database Pipeline opening at `:68`, not `:69`. Used content-based location and the `grep -cF minipro CLAUDE.md == 1` gate to confirm correctness rather than chasing the obsolete line number. Plan body explicitly noted line numbers may shift.
- **Three tasks collapsed into one app sub-repo commit.** Plan body explicitly authorised "All four edits in one commit (or part of a larger Plan 02-03 commit that also lands Tasks 02-03-02 and the doc scrub in Task 02-03-03)". The collapsed commit gives a single blame entry that closes CLEAN-02 + WIRE-02 atomically.
- **Shape A over Shape B for the wire round-trip.** Per RESEARCH.md recommendation: fused inside the existing `check_dispatch.py` scanner rather than a parallel pytest fixture. Preserves single-binary "scanner == gate" UX; CI / pre-commit gates one tool, not two.
- **`build_db.py` argparse `default="minipro"` retained.** Although CLAUDE.md line `:23` build_db CLI example was rewritten, the actual argparse default in `build_db.py:29` (the load-bearing default directory path users rely on when running `python tools/build_db.py` without arguments) is preserved. The case-sensitive `grep -cF minipro` gate is satisfied without changing CLI behavior.
- **Pre-existing co-located dirt left un-staged.** Plans 02-01 and 02-02 both documented out-of-scope dirt in `firestarter_app/` (deleted `.planning/codebase/*.md`, version bump in `__init__.py`, `ic_layout.py` reformat). This plan honored the same scoping rule: only the four files in Plan 02-03's scope are staged.

## Deviations from Plan

### Auto-fixed Issues

None — plan executed as written. All grep gates and SC#5 invocations passed on first run after the verbatim D-10 rewrites + Shape A augmentation + 3-line host CLAUDE.md scrub.

### Plan body line-number drift (not a deviation; explicit plan note)

- Plan body referenced `firestarter_app/CLAUDE.md:69` and `firestarter/CLAUDE.md:69` as the surviving-attribution / drop targets. Actual current line numbers are `:68` (host, the Database Pipeline opening) and `:69` (firmware, correct). Used content-based identification (markdown text containing `infoic.xml` for host, `algorithm field` and `handle->protocol` for firmware) rather than line-number lookups. The plan's verification gates (`grep -cF minipro` counts) are satisfied; line numbers are not part of the acceptance contract.

### Out-of-scope discoveries

- `firestarter_app/tools/build_db.py:157` and `:159` (`print(f"Fetching database from: {MINIPRO_XML_URL}")` + `r = requests.get(MINIPRO_XML_URL)`) retain the uppercase constant identifier `MINIPRO_XML_URL`. These are call-sites of the load-bearing constant; preserving them is the explicit intent of D-09. Case-sensitive `grep -cF minipro` correctly counts only the lowercase substring on `:10` (the URL value) — the uppercase identifier usages are invisible to the gate. No edit needed.

### Authentication gates

None.

## Verification Gate Results

All gates from plan `<verify>` blocks + `<success_criteria>`:

| # | Gate | Expected | Actual | Status |
|---|------|----------|--------|--------|
| 1 | `grep -cF minipro firestarter_app/firestarter/database.py` | 0 | 0 | PASS |
| 2 | `grep -cF minipro firestarter_app/tools/check_dispatch.py` | 0 | 0 | PASS |
| 3 | `grep -nF MINIPRO_XML_URL firestarter_app/tools/build_db.py` includes `:10` | yes | yes (also `:157`, `:159`) | PASS |
| 4 | `grep -cF minipro firestarter_app/CLAUDE.md` | 1 | 1 (line :68, infoic.xml attribution) | PASS |
| 5 | `grep -ciF minipro firestarter/CLAUDE.md` | 0 | 0 | PASS |
| 6 | `grep -ciF minipro CLAUDE.md` (meta) | 0 | 0 | PASS |
| 7 | `grep -ciF minipro firestarter/src/ firestarter/include/` | all 0 | all 0 | PASS |
| 8 | `check_dispatch.py` contains `from firestarter.database import EpromDatabase` | yes | yes | PASS |
| 9 | `check_dispatch.py` contains `db = EpromDatabase()` in main() | yes | yes | PASS |
| 10 | `check_dispatch.py` contains `wire_regressions = []` | yes | yes | PASS |
| 11 | `check_dispatch.py` contains both `"vpp_mv" not in wire` and `"vpp" in wire` | yes | yes | PASS |
| 12 | `check_dispatch.py` union check matches `if errors or sram_in_eprom or eeprom28c_in_eprom or wire_regressions:` | yes | yes | PASS |
| 13 | `python tools/check_dispatch.py` exits 0 with `^PASS:` and `0 wire-key regressions` | yes | yes (full line cited below) | PASS |
| 14 | `pip install -e .` exit code | 0 | 0 | PASS |
| 15 | `firestarter --help` exit code | 0 | 0 | PASS |
| 16 | `firestarter info W27C512` exit code | 0 | 0 | PASS |
| 17 | `firestarter info --adapter W27C512` exit code | 0 | 0 | PASS |
| 18 | No `FileNotFoundError` or `stale` in `/tmp/sc5_*.out` | absent | absent | PASS |

**check_dispatch.py PASS line (verbatim from /tmp/check_dispatch.out):**

```
PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom; 0 DIP28_2764 Flash/EEPROM chips route to configure_eprom; 0 wire-key regressions
```

## Threat Flags

None. This plan only edited comments, prose, and added a defensive static + dynamic regression scanner. No new network endpoints, no auth changes, no schema changes at trust boundaries.

## Known Stubs

None.

## TDD Gate Compliance

Plan type is `cleanup` (frontmatter `type: execute` with cleanup intent); TDD gate does not apply. The new `wire_regressions` check in `check_dispatch.py` is a defensive regression scanner that runs against live production data (the full 743-chip database) and exits non-zero on any deviation — it functions as a continuous CI-gate assertion rather than as an isolated TDD test.

## Self-Check: PASSED

Verified post-Write, pre-metadata-commit:

- FOUND: `.planning/phases/02-naming-cleanup-wire-key-minipro-references/02-03-SUMMARY.md` (this file).
- FOUND: firestarter_app sub-repo commit `0489a20` (`CLEAN-02 + WIRE-02: minipro attribution scrub + check_dispatch.py wire round-trip + SC#5 smoke`) — 4 files, 45 insertions, 11 deletions.
- FOUND: firestarter sub-repo commit `587396a` (`docs(02-03): drop final minipro reference from CLAUDE.md (D-11)`) — 1 file, 1 insertion, 1 deletion.
- FOUND: All 18 verification gates above pass.

## Next Phase Readiness

- **Phase 02 fully discharged.** WIRE-01 / WIRE-02 / CLEAN-01 / CLEAN-02 all closed. Phase 02 ready for `/gsd-verify-work`.
- **Phase 3 (Retroactive Verification) entry contract met.** All Phase 3 audit artifacts (`03-VERIFICATION.md` and onward) can reference the post-Phase-2 canonical wire format (`vpp_mv` only) and renamed DB filename (`chip_database.json`) without ambiguity.
- **Continuous regression coverage in place.** `check_dispatch.py` now gates both static dead-key usage AND dynamic wire-shape regressions across all 743 chips in a single binary; future plans that touch the wire emitter or DB schema will fail the scanner immediately on regression.

---
*Phase: 02-naming-cleanup-wire-key-minipro-references*
*Plan: 03*
*Completed: 2026-05-12*

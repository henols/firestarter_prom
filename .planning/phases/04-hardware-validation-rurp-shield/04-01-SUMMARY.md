---
phase: 04-hardware-validation-rurp-shield
plan: 04-01
subsystem: hardware-validation-test-script-repair
wave: 1
tags: [hardware-validation, test-script-repair, warning-4-closure, jq-schema-migration, docs-and-shell]

# Dependency graph
requires:
  - phase: 02-naming-cleanup-wire-key-minipro-references
    plan: 01
    provides: "CLEAN-01 — chip_database.json filename established at firestarter_app/firestarter/data/chip_database.json; the surviving test-script refs to the old database_generated.json are the WARNING-4 leftovers Plan 04-01 closes."
provides:
  - "WARNING-4 closure — zero non-comment database_generated.json refs survive in firestarter_test.sh or write_test.sh"
  - "HW-01 discharge — both .sh scripts parse via bash -n AND resolve W27C512 metadata via jq -e against the new nested chip_database.json schema"
  - "04-HW-VALIDATION.md scaffolded with frontmatter + H1 + §1 (HW-01) evidence block; §2..§5 inherit a clean evidence-file for the bench-run plans"
affects:
  - "Plan 04-02 (Wave 2) — HW-02 W27C512 + HW-03 AM29F040/SST39SF040 + HW-04 AT28C256 inherit a known-clean test-script state"
  - "Plan 04-03 (Wave 3) — HW-05 AM28F010 + SAF-04 abort run will append §5 to the same 04-HW-VALIDATION.md"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Atomic sub-repo commit (firestarter_app@16dcafe) for both .sh files together per CONTEXT.md D-08 + D-13 — half-flipped state (filename fixed but jq schema not, or vice-versa) would have left WARNING-4 nominally closed but the bench-runner still broken on first chip-metadata lookup"
    - "Two-layer scope discipline: CONTEXT.md D-01 RESEARCH.md-corrected — the planner honored RESEARCH.md over the original CONTEXT.md framing (which proposed a 2-line filename sed), recognizing the surviving jq-schema drift surfaced at firestarter_test.sh:48-67 + write_test.sh:35-40"
    - "Grep-at-write-time verification (Phase 3 LEARNINGS Pitfall #7) — every cited line:offset was confirmed via direct grep against firestarter_app/ at write time; the planned-line-numbers in <interfaces> happened to match live state exactly"
    - "pio test 25/25 PASS state cited (Plan 01-01 closure) — not re-run, per Phase 3 LEARNINGS 'existing test runs should be cited, not re-executed'"

key-files:
  created:
    - .planning/phases/04-hardware-validation-rurp-shield/04-HW-VALIDATION.md
    - .planning/phases/04-hardware-validation-rurp-shield/04-01-SUMMARY.md
  modified:
    - firestarter_app/firestarter_test.sh
    - firestarter_app/write_test.sh

key-decisions:
  - "D-01 RESEARCH.md-corrected scope honored: both filename (layer 1, WARNING-4) AND jq schema (layer 2, surfaced by gsd-phase-researcher) fixed in a single atomic firestarter_app/ sub-repo commit. Live grep at write time confirmed exactly 2 database_generated refs pre-fix (firestarter_test.sh:31 + write_test.sh:17) and 4 legacy jq query blocks pre-fix (3 in firestarter_test.sh + 1 in write_test.sh) — every one resolved."
  - "MEMORY_SIZE_HEX variable name retained as-is. The new .electrical.size_bytes returns a plain integer (e.g. 65536 for W27C512); bash arithmetic auto-coerces in the downstream dd invocations. Renaming was the planner's call and was not necessary for correctness."
  - "CAN_ERASE query rewritten as (.electrical.type == \"Flash/EEPROM\") — the legacy .[\"can-erase\"] flag has no direct successor in the new schema, but the Flash/EEPROM type discriminator correctly captures the 'this chip supports erase' semantics for the bench-runner branch at firestarter_test.sh:154."
  - "No firmware (firestarter/) source modified by this plan — Plan 04-01 is firestarter_app-only test-script repair. No writes to .planning/STATE.md or .planning/ROADMAP.md (orchestrator-owned per Phase 3 LEARNINGS surprise)."

requirements-completed: [HW-01]

# Metrics
duration: ~5min
completed: 2026-05-12
status: complete
closed: 2026-05-12T11:52:49Z
---

# Phase 04 Plan 01: HW-01 Test-Script Repair (WARNING-4 closure + jq schema migration) — Summary

**Both `firestarter_app/firestarter_test.sh` and `firestarter_app/write_test.sh` repaired in a single atomic `firestarter_app/` sub-repo commit covering BOTH layers: (1) WARNING-4 filename swap from the deleted `database_generated.json` to the post-Phase-11 `chip_database.json`, AND (2) jq-query schema migration from the pre-Phase-11 flat top-level schema (`.["memory-size"]`, `.["has-chip-id"]`, `.["can-erase"]`, `.name`) to the nested `chip_database.json` schema (`.electrical.size_bytes`, `.programming.chip_id_check`, `.electrical.type`, `.part_number`). HW-01 is discharged; `04-HW-VALIDATION.md` scaffolded with frontmatter + H1 + §1 evidence block for the Plan 04-02/04-03 bench runs to append against.**

## What landed

- **`firestarter_app/firestarter_test.sh`** — filename swap on line 31 + three jq queries (lines 48-67) migrated to the nested schema. `MEMORY_SIZE_HEX` retained; `HAS_CHIP_ID` reads `.programming.chip_id_check`; `CAN_ERASE` reads `(.electrical.type == "Flash/EEPROM")`.
- **`firestarter_app/write_test.sh`** — filename swap on line 17 + the single jq query (lines 35-40) migrated to the nested schema.
- **`.planning/phases/04-hardware-validation-rurp-shield/04-HW-VALIDATION.md`** — NEW file: canonical phase frontmatter (`requirements_validated: [HW-01..HW-05]`, `chips_tested:` rows for W27C512/AM29F040/SST39SF040/AT28C256/AM28F010 with bench-run fields marked `<pending>` until Plan 04-02/04-03), H1 (`# Phase 4 — Hardware Validation (RURP shield) — Evidence`), H2 §1 (HW-01) with before/after diff, dry-run validation output, and PASS verdict.
- **`.planning/phases/04-hardware-validation-rurp-shield/04-01-SUMMARY.md`** — this file.

## Commits

| # | Layer | Commit | Files |
|---|-------|--------|-------|
| 1 | Sub-repo (`firestarter_app/`) | `firestarter_app@16dcafe` — `fix(test-scripts): WARNING-4 closure + jq schema migration to chip_database.json` | `firestarter_test.sh`, `write_test.sh` (one atomic commit per CONTEXT.md D-08 + D-13) |
| 2 | Meta-repo | `docs(04-01): HW-01 SUMMARY + 04-HW-VALIDATION.md §1` _(this commit)_ | `04-HW-VALIDATION.md`, `04-01-SUMMARY.md` (one atomic commit per D-08 "immediate-follow meta-repo commit") |

The meta-repo commit also bumps the `firestarter_app` submodule pointer from `0489a20` (Plan 02-03 close) → `16dcafe` (Plan 04-01 close).

## Decisions consumed

**CONTEXT.md D-01 (RESEARCH.md-corrected) was the load-bearing decision** — the original CONTEXT.md framing proposed a 2-line filename `sed`, but `gsd-phase-researcher` surfaced a second-layer drift: the scripts' jq queries used the pre-Phase-11 flat schema (`.["memory-size"]`, `.["has-chip-id"]`, `.["can-erase"]`, `.name`) which would return `null` for every lookup against the new `{manufacturer: [chip_records]}` nested schema even after the filename was fixed. Honoring D-01 as corrected (both layers in one commit) was the only path that actually discharged HW-01 — fixing only layer 1 would have left the bench-runner broken on first chip-metadata lookup. Live grep at write time confirmed all 6 broken lines (2 filename + 4 jq query blocks).

**CONTEXT.md D-08 (atomic-commit shape)** was applied at both layers:
- One atomic sub-repo commit (`16dcafe`) touching both .sh files together — verifiable via `cd firestarter_app && git log -1 --name-only` returning exactly `firestarter_test.sh` + `write_test.sh`.
- One atomic meta-repo commit (this commit) pairing the `04-HW-VALIDATION.md` §1 evidence block with this SUMMARY — `git log -1 --name-only --pretty=format: | grep -v '^.planning/' | wc -l` returns 0 (zero non-`.planning/` paths in this commit; the submodule pointer bump is the only exception and is itself the sub-repo→meta-repo bridge per D-08).

## Out-of-band notes

- **No `pio test` re-run.** Firmware native unit-test state cited from `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-VERIFICATION.md` "Behavioral Spot-Check" (25/25 PASS as of Plan 01-01/01-02 close), per Phase 3 LEARNINGS "existing test runs should be cited, not re-executed".
- **No source under `firestarter/` modified.** Plan 04-01 is `firestarter_app`-only test-script repair; the firmware sub-repo is untouched.
- **No writes to `.planning/STATE.md` or `.planning/ROADMAP.md`.** Orchestrator-owned per Phase 3 LEARNINGS surprise; orchestrator will update them post-wave-merge.
- **HW-01 sub-repo commit is the only `firestarter_app/` write across Phase 4.** HW-02..HW-05 (Plan 04-02 + 04-03) are verification-only bench runs that append to `04-HW-VALIDATION.md` and write zero source code.

## Hand-off

**Wave 1 is closed. Plan 04-02 (Wave 2) is unblocked the moment this commit lands** — HW-02 (W27C512), HW-03 (AM29F040 + SST39SF040), and HW-04 (AT28C256 + multimeter trace) all inherit a known-clean test-script state and can begin the bench-runner loop (write → verify → read → xxd-diff) on the operator's RURP shield. Plan 04-03 (Wave 3) follows for HW-05 (AM28F010 + SAF-04 abort run). Per CONTEXT.md D-10 bench-resume convention, the bench-runner plans re-read `04-HW-VALIDATION.md` to identify the next unfilled `§N` section.

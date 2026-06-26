---
gsd_state_version: 1.0
milestone: v1.16
milestone_name: — Protocol-First Architecture Rebuild
status: executing
stopped_at: Phase 90 context gathered
last_updated: "2026-06-26T12:28:23.133Z"
last_activity: 2026-06-26 -- Phase 90 planning complete
progress:
  total_phases: 6
  completed_phases: 5
  total_plans: 25
  completed_plans: 21
  percent: 83
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-06-25

## Current Position

Phase: 90
Plan: Not started
Status: Ready to execute
Last activity: 2026-06-26 -- Phase 90 planning complete

Progress: [████████░░] 83%

> **Scope amendment 2026-06-25:** Mid-discussion the operator pivoted v1.16 from a
> pure behavior-preserving refactor to *fix the DB at its root* — decode the
> `infoic.xml` `variant` field fully and delete the `build_db.py` Rule 1/2/3 override
> edge-cases. New Phase 86 inserted (host-only); Naming→87, Golden Traces→88,
> Recompose→89, Bench Ledger→90. See `.planning/phases/86-variant-decode-correct-db-regen/86-CONTEXT.md`.

## Quick Tasks Completed

| ID | Task | Date | Status | Commit |
|----|------|------|--------|--------|
| 260625-f1g | Group dev write-cycle/consistency-check run folders under `firestarter-runs/` (was dumping in launch dir) | 2026-06-25 | complete ✓ | firestarter_app@bc55b29 |

## Project Reference

See: `.planning/PROJECT.md` (v1.16 Current Milestone section + Key Decisions)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware handler. v1.16 makes that contract **legible** (named, datasheet-documented protocols) and **leaner** (shared-primitive handlers). Minipro DB stays ground truth; datasheets verify + document the *why*.

**Current focus:** Phase 89 — incremental-primitive-recompose

## Roadmap Summary

**v1.16 ACTIVE — 5 phases (85–89), 23/23 requirements mapped. Dependency-first ordering:**

- **Phase 85: Datasheet Acquisition** (DSHEET-01/02/03, SAFE-05) — No code; commit datasheet PDFs for 11 on-hand chips + 1 representative per 6 no-silicon buckets; author `datasheets/README.md` index. Unblocks naming pass.

- **Phase 86: Naming + Documentation Pass** (NAME-01/02/03/04/05, SAFE-03, SAFE-06) — Author 12-bucket protocol vocabulary (hex → human name → datasheet-verified behavior), enumerate 8 one-off invariants as named behavior-contract items, apply FM1608 0x40→0x28 + 0x34 UV-EPROM→EEPROM decode corrections. Dispatch structure byte-identical; near-zero flash delta.

- **Phase 87: Golden Traces + Dispatch-Mirror Guard** (PRIM-01, SAFE-01, SAFE-02, SAFE-04) — Pin per-family native register golden traces and add the dispatch-mirror invariant test before any extraction. Establishes the recompose oracle.

- **Phase 88: Incremental Primitive Recompose** (PRIM-02/03/04/05/06, SAFE-01/02/03 recurring) — P7 SDP-table dedup (warm-up ~40–80 B) → P4 chip-ID compare/report (~250–350 B) → P3 VPP gate (~350–450 B, biggest) → P5 poll (~200–300 B). Each step guarded by native suites + `check_dispatch.py` + `diff_db.py`; `pio run -e leonardo` net-non-increase gate; achieved flash % reported.

- **Phase 89: Bench Validation + PROTOCOL-LEDGER** (LEDGER-01/02/03, SAFE-04 recurring) — Bench-prove on-hand protocols (0x05/W29C020, 0x06/SST39SF040, 0x07/W27C512, 0x28/FM1608) on Leonardo + Rev 2.0; author `PROTOCOL-LEDGER.{md,json}` composing with v1.13 matrix + v1.15 EVIDENCE; 6 no-silicon buckets explicit UNVERIFIED.

**Build order (dependency-first, safety-load-bearing):** 85 → 86 → 87 → 88 → 89. Cannot safely recompose a family before its behavior contract is written (Phase 86) and its golden trace pinned (Phase 87). Flash curve trends down monotonically during Phase 88 (P7→P4→P3→P5 order).

**Cross-cutting safety (SAFE-01..06):** SAFE-01 (protocol-key, not electrical.type) homed in Phase 87, recurring in 88. SAFE-02 (one-off invariants survive recompose) homed in Phase 87, recurring in 88. SAFE-03 (check_dispatch.py 0 violations + diff_db.py empty every phase) homed in Phase 86 (naming applies NAME-04 corrections; baseline re-pinned for those), recurring in 87/88/89. SAFE-04 (over-voltage blocked, host guard never bypassed) homed in Phase 87, recurring in 88/89. SAFE-05 (no new 3rd-party deps; only new artifact is `datasheets/`) homed in Phase 85. SAFE-06 (firmware-first, no lockstep, CI target py3.11 not 3.12 devcontainer) homed in Phase 86.

## Accumulated Context

### Roadmap Evolution

- v1.16 roadmap created 2026-06-25: 5 phases (85–89) derived from the 23 v1.16 requirements
  (DSHEET/NAME/PRIM/LEDGER/SAFE) along the research-locked dependency-first spine (datasheets →
  vocabulary/invariants → golden-trace guards → recompose → bench ledger). 23/23 mapped, no
  orphans/duplicates (Phase 85: 4 reqs · Phase 86: 7 · Phase 87: 4 · Phase 88: 8 · Phase 89: 4;
  SAFE-01/02/03/04 cross-cutting, homed in earliest establishing phase and recurring as
  preconditions in later phases). PRIM-02..05 consolidated into Phase 88 as sub-plans (the
  4 extraction steps are closely coupled under the same gate discipline; fine-grained splits
  would create thin phases with implementation-task criteria rather than observable outcomes).
  At Comprehensive granularity, 5 phases matches the natural delivery boundaries (acquisition →
  vocabulary → oracle → refactor → validation). Research convergence: HIGH confidence on all
  four research dimensions (STACK/FEATURES/ARCHITECTURE/PITFALLS).

- v1.15 roadmap created 2026-06-23: 4 phases (81–84); shipped 2026-06-25.
- v1.14 roadmap created 2026-06-18: 4 phases (77–80); shipped 2026-06-23.

### v1.16 Scope Notes (research 2026-06-25, HIGH confidence)

- **Firmware-only / host-untouched.** No dual-repo lockstep for the refactor (wire/constant values
  unchanged). NAME-04 decode corrections (FM1608 0x40→0x28 reconciliation + 0x34 UV-EPROM→EEPROM)
  are host-only DB fixes applied in Phase 86; `diff_db.py` shows only those 2 intentional changes.

- **Flash outcome = best-effort measured, not a hard gate.** Per-step `pio run -e leonardo`
  net-non-increase gate + report achieved %; no hard ≤86.5% floor.

- **Pure behavior-preserving refactor.** CR-01 (W29C040 flash4), FUT-06 (AM27C020 0x08), FUT-03
  (2516 0x0B read) preserved as-is; not fixed this milestone.

- **12 live protocol buckets** in chip_database.json (744 chips): 0x05/06/07/08/0B/0D/0E/10/27/28/29/34.
  No 0x40 — FM1608 is decimal 40 = 0x28 (SRAM_STD/FRAM). Phantom 0x35/0x39 = zero DB chips
  (document as "dispatched-but-dead"). Infeasible 0x11/0x2A/0x2B/0x2C = fail-closed.

- **Realistically recoverable: ~850–1,300 B** via P3 VPP gate (~350–450 B) + P4 chip-ID
  (~250–350 B) + P5 poll (~200–300 B) + P7 tables (~40–80 B) → 89.5% → ~85–86.5%.

### ⏸ v1.9 DEFERRED (operator 2026-06-08 — resumes later at Phase 45)

v1.9 (Read-Bug RCA + Fix) is paused. Phase 44 (Bug A RCA) complete. Remaining: Phases 45–48. The
v1.16 bench oracle is pinned to Leonardo + Rev 2.0 precisely to avoid the v1.9 shield-fleet read bug.

### v1.10 Substrate (carry-forward)

Transport provably byte-exact (COBS `0x00` + CRC8-CCITT) — settled variable. GATE-1.8d ring-fence intact.

### Pending Todos (carried forward)

- `avrdude-mcu-detection-fallback.md` (low) — out of scope, carry forward
- `cobs-decoder-framelevel-deadline-wr01.md` (medium) — v1.10 COBS follow-up; deferred
- `large-read-data-jitter-uno328pb.md` (HIGH, v1.8-seed) — v1.9 RCA target
- `gather-protocol-datasheets.md` — feeds v1.16 Phase 85 directly

### Blockers / Concerns

None at roadmap start. v1.16 is a firmware-only refactor with no hardware dependencies except the
Phase 88 bench re-prove steps (W27C512 + W29C020 write paths on Leonardo + Rev 2.0) and the Phase 89
bench-validation session. Primary risk: abstraction overhead increases flash rather than shrinks it
on AVR — mitigated by the per-step net-non-increase measurement gate. Watch the py3.12-masks-CI-3.11
ruff/codegen drift trap for any host-side NAME-04 corrections in Phase 86.

## Session Continuity

Last session: 2026-06-26T11:59:50.517Z
Stopped at: Phase 90 context gathered
Resume: Phase 88 — Golden Traces + Dispatch-Mirror Guard

## Decisions

- [Phase 86-03, 2026-06-25]: VAR-03/04/SAFE-04 — re-pinned BOTH diff_db baselines LAST (D-07 / RESEARCH Pitfall 4: only after the 86-02 + 86-04 classified diff was reviewed PASS-all incl. the 2516/2532 supplement rows). chip_database.baseline.json = byte-identical cp of the 746-chip correct DB (load-bearing diff_db gate). dispatch_baseline.json regenerated (746 chips) by faithfully mirroring check_dispatch.py main()'s own per-chip mem_type derivation + dispatch() (no committed generator exists — RESEARCH A2); meta provenance cites Phase 86 + minipro SHA a8efaedc + the VAR-05 supplement (supersedes the Phase 66 Plan 04 744-chip capture); 66 dispatch deltas are the legitimate 28C-EEPROM→configure_eeprom28c (0x0D) consolidation + 2 added supplement chips (X88C64P stays not_implemented; mem_type None→1 benign). RESULT: diff_db.py now an IDENTITY diff (0 changed/0 new/0 missing, exit 0). Full phase gate green vs CI py3.11: 686 host tests, 77.69% coverage (≥70 floor), ruff check + ruff format --check clean (firestarter/ tests/), mypy watermark 35==35 exit 0 (mypy 2.1.0 confirmed present, not the MISSING-prints-OK trap). 4 ruff errors in tools/ confirmed pre-existing (present @ dd541f6~1) AND out-of-CI-scope (ci.yml lints firestarter/ tests/ only). SAFE-04 intact: no write path / host guard / 2516 wire values touched; 2516 UNVERIFIED preserved. Commit firestarter_app@dd541f6. Phase 86 COMPLETE (4/4) → ready for /gsd-verify-work.
- [Phase 86-04, 2026-06-25]: VAR-05/SAFE-04 — shipped 2516 + 2532 (upstream-absent 24-pin oddballs) first-class via curated provenance-cited non-upstream supplement tools/extra_chips.json (D-10), merged by build_db.py AFTER the infoic.xml decode loop / BEFORE json.dump (NOT routed through classify()/resolve_pinout_key — fully-specified). DB 744→746. KEY: 2516 UNVERIFIED expressed via a verification_status field, NOT support_status — support_status stays "supported" so the chip is resolvable for read/info (the host guard refuses ANY non-"supported" chip, which would block read); wire values verbatim from v1.15 user-override (0x0B/DIP24_2716/UV-EPROM/25000mV/2048B; SAFE-04). 2532 is non-JEDEC → new DIP24_2532 pinout (VPP=pin21, A11=pin18; distinct from DIP24_2732; vpp-pin satisfies GATE-03). diff_db EXTRA_CHIPS_SUPPLEMENT rule fences source=non-upstream-supplement NEW rows as cited (exit 0, PASS all 72). check_dispatch 0 violations (746 chips, 736 supported). 8 supplement tests green. Downstream goldens regen for the legitimate 744→746 (coverage matrix + test_characterization list; only the 2 new rows). Baselines NOT re-pinned (86-03 LAST). Commits firestarter_app@94ea3b5/4054bfe/5e368d1.
- [Phase 79-02, 2026-06-23]: NMOS-02 executed under CONTEXT D-07 operator override. VPE = 22.4V DMM / 23.9V fw; ceiling 22000→25000; 4 NMOS chips graduated `vpp-exceeds-max`→`supported` (0x0B, 25000mV). Best-effort, no HW change ever. FUT-02 (>25V fail-closed) preserved.
- [Phase 82, 2026-06-24]: Rewritable silicon validation: 5 PASS / 3 FAIL (W27E512/W27E040 stuck-bit silicon wear; W29C040 flash4 256B page-0 fault confirming Phase-74 fix not silicon-effective → CR-01). W29C020 auto-erase = first Flash/EEPROM auto-erase silicon proof.
- [Phase 84-05, 2026-06-25]: FIX-01 closed by disposition D-43; GRAD-03/FUT-03 deferred best-effort D-22; 2516 read still unstable after VPP-skip.
- [Phase 85-01, 2026-06-25]: v1.16-protocol-first-architecture-rebuild branch forked from beta (not v1.15 tip) in firestarter sub-repo; datasheets-check.sh Wave-0 gate authored with 12-bucket %PDF contract (correctly RED at scaffold stage, PASS after Plans 02/03 populate the tree).
- [Phase 85-02, 2026-06-25]: 17 datasheets committed; W27E512→0x07, FM1608→0x28 (DB-verified); 3 D-02 fallbacks: SST27SF512/W27E040/DS1250Y bot-blocked; SAFE-05 intact
- [Phase 85-03, 2026-06-25]: datasheets/README.md authored (DSHEET-03); 12-bucket index + 6 exclusions + D-02/D-03 policy; phase-gate PASS (exit 0); SAFE-05 intact
- [Phase 86-02, 2026-06-25]: VAR-02/03/04 — replaced build_db.py Rule 1/Rule 2(WARNING-5)/Rule 3 + two-pass _etype with one principled classify(type,proto,pm_idx,flags,pinout,mem_size) (D-06 full deletion, no residual override). Regenerated chip_database.json (744 chips): FM1608 0x28/FRAM/DIP28_JEDEC_SRAM_8K, X88C64 EEPROM/protocol-not-implemented (proto 0x34 arm), W27C512 stable. KEY: arm-2 scoped to EPROM-family proto for DIP28 clusters (DIP24_2816 any-proto) — first cut over-broadened and mis-flipped AT29C256/AT29LV256 (genuine 5V flash, proto 0x05) to 0x0D; fixed → 0 algorithm changes vs pre-regen. diff_db.py VARIANT_DECODE label (cites database.c#L1918 + minipro.h#L70) exit 0 (PASS all 72 changed chips explained, transcript tools/variant-decode-diff.txt). check_dispatch.py 0 dispatch regressions / 0 consistency violations. EVIDENCE-11 wire-stable (zero moved, no re-bench flag). MINIPRO_XML_URL pinned to a8efaedc. Baseline NOT re-pinned (86-03). Commits firestarter_app@cab9349/46efe6e/16fd2e2.
- [Phase 86-01, 2026-06-25]: VAR-01 docs + Wave-0 oracle (host-only, build_db.py untouched). DECODE-NOTES.md pins minipro master SHA a8efaedc236c1d9718bd28299dfbb99536b010ff (= existing @ a8efaedc); high byte = T56/T76 algo_number (database.c#L1918), NOT a classifier — classification keys on type/proto/pm_idx/flags. Refactor-under-test oracle: FM1608 GREEN (algo 40/FRAM/DIP28_JEDEC_SRAM_8K), X88C64 RED-as-designed (UV-EPROM today → Plan 02 adds proto 0x34→EEPROM arm), 10 upstream-decoded EVIDENCE chips wire-stable vs OLD baseline (2516 excluded → owned by Plan 86-04). Commits firestarter_app@bd462fa/a6f7e88/68865c1.
- [Phase 86 discuss, 2026-06-25]: MILESTONE RESTRUCTURED. Grounded in raw infoic.xml that FM1608=type4/proto0x07/variant0x4126 and X88C64=type1/proto0x34/variant0x3100/flags0x00414200 (flags&0x10==0 → why its type is mis-decoded). Operator pivoted: decode the variant field fully (incl. undecoded high byte) + delete build_db.py Rule1/2/3 → correct DB. Inserted new Phase 86 (host-only variant decode); renumbered 86→90; added VAR-01..04 (27 reqs). Decisions: full override deletion (check_dispatch 0-violations = structural backstop), every diff_db row explained + re-pin baseline, on-hand bench chips unchanged-or-rebenched.
- [Phase ?]: FM1608 decimal-40/hex-0x28 conflation retired in PROTOCOLS.md
- [Phase 87-03, 2026-06-26]: NAME-03/SAFE-02 — 9 INV native test assertions in matrix-assigned suite paths; INV-04 page-boundary probe switched from 257-byte (recording-buffer overflow) to 65-byte (discriminates 64B vs 256B pages via SDP-count=1 proof); INV-03 uses pins=32+vpp_line=VPP_P1_32_DIP to activate using_p1_as_vpp() and observe CTRL_VPP_P1_ENABLE in execute phase; SAFE-02 three-target grep contract complete: doc+handler+test for all 9 INVs. firestarter@b67acde
- [Phase 87-04, 2026-06-26]: NAME-05/SAFE-03/SAFE-06 — All five frozen-world gates PASS. check_dispatch.py exit 0 (746 chips, 0 violations). diff_db.py exit 0 (0 changed/0 new/0 missing, identity diff). pio run -e leonardo flash delta = 0 bytes (pre=25654 post=25654 — exact match, well within 16-byte threshold). All 9 INV ids hit >=3 files (PROTOCOLS.md + handler + test; INV-01 and INV-09 hit 4 files). Host repo git-diff exit 0 (zero source/tool/test files modified — SAFE-06 machine-verified, not py3.12-maskable toolchain run). Phase 87 COMPLETE.
- [Phase 88-04, 2026-06-26]: SAFE-02/PRIM-01 — dispatch-mirror invariant test authored as host pytest (test_dispatch_mirror.py). Three-way bind: PROTOCOLS.md §0 doc-parse ↔ check_dispatch.dispatch() + _ALGO_MEM_TYPE ↔ test_configure_memory.cpp firmware-leg enumeration. Full §0 table (12 rows incl. SRAM 0x0E/0x27/0x28/0x29, 0x34→not_implemented). Phantom 0x35/0x39 excluded from doc/firmware-leg assertion (not in §0). 2 tests pass, ruff-clean, no firmware modified. firestarter_app@e46549f.
- [Phase 88-02, 2026-06-26]: PRIM-01/SAFE-02 — eeprom28c + flash_intel golden register traces pinned. 4 fixtures committed. Key: eeprom28c has no CMD_CHECK_CHIP_ID handler — chip-id golden trace uses CMD_WRITE + chip_id=0x1F08 + operation_init only. flash_intel write golden test needed delayMicroseconds + millis() stubs added to setUp() (first time write_execute called in suite). SR poll exited via scripted get_data returning 0x80. All 10 suite tests green. firestarter@0b1ce93/fa0f908.
- [Phase 88-03, 2026-06-26]: PRIM-01/SAFE-02 — flash3 + flash4 golden register traces pinned. 3 fixtures committed. flash3 (0x06): 12-entry write trace; millis() stub required in setUp() (flash_util_verify_operation DQ7 poll timeout). flash4 (0x05): 206-entry write trace (65-byte INV-04 probe, < 256 cap) + 16-entry chip-id trace (scripted mock re-assigned after configure_memory(), Pitfall 3). flash3 has no chip-id P4 site (D-03). All 17 suite tests green. firestarter@1282c32/e6cce3e.
- [Phase 87-02, 2026-06-26]: NAME-02 — all 10 handler files carry datasheet-anchored rationale header blocks (plain C comments, zero flash). INV-01/02/03/05/06/08 in eprom.cpp; INV-04 in flash_type_4.cpp; INV-09 in flash_type_3.cpp; INV-07 in sram.cpp; plus dispatch rationale in flash_utils/memory/not_implemented/firestarter.cpp. Comment-only diff guard PASS (all 10 files). SAFE-02 greppability: INV ids now hit doc (87-01) + handler (87-02) — third target (test names) lands in Plan 03. Commits firestarter@f362263/3b8202d.
- [Phase 88-05, 2026-06-26]: SAFE-04/D-07/D-08/D-09 — all frozen-world gates PASS: check_dispatch 0 violations (746 chips), diff_db empty (0 changed/0 new/0 missing), Leonardo flash=25654 B (0-byte delta vs Phase-87 baseline), native suite 16/16 PASS. SC#4 guards present+unmodified: eprom.cpp:282 + flash_intel.cpp:65 VPP check, chip_resolver.py:55 resolve_chip guard. 2516 stays UNVERIFIED (verification_status=UNVERIFIED + support_status=supported). Phase 88 COMPLETE. meta@467a10f.
- [Phase 89-01, 2026-06-26]: PRIM-02/P7 — delete-not-merge const-table dedup: FLASH_ENABLE_WRITE_PROTECTION (zero callers, byte-identical to FLASH_ENABLE_WRITE) deleted from flash_utils.h; local EEPROM_SDP_DISABLE deleted from eeprom_28c.cpp and single caller redirected to shared FLASH_DISABLE_WRITE_PROTECTION. Both tables byte-identical verified at execution time. 102/102 native tests green, golden traces zero-diff, flash delta=0 B (25654→25654 B, 89.5%), check_dispatch 0 violations, diff_db empty, INV-01..09 all >=3 files. Pre-existing .gitignore change in firestarter_app noted (not source, not P7-caused). firestarter@0052c42.
- [Phase ?]: [Phase 89-02, 2026-06-26]: PRIM-03/P4 — new primitives module (primitives.h/cpp) + chip_id_report shared across 4 call sites (flash_utils/eprom/eeprom28c/flash_intel); eprom error_code param retained as void (Assumption A3 resolved via golden trace); flash 25654→25490 B (-164 B, D-01 PASS); 102/102 native green; check_dispatch 0 violations; diff_db empty; INV-01..09 >=3 files. firestarter@a10871d
- [Phase ?]: [Phase 89-03, 2026-06-26]: PRIM-04/P3 — vpp_check_window extracted; delay(100) handler-local; D-08 threshold byte-identical in primitives.cpp; REGULATOR=0 in primitive (D-06); flash 25490->25088 B (-402 B); 102/102 PASS; firestarter@a52fd0a
- [Phase ?]: Phase 89-04: P5 extracted — poll_readback() shares bounded single-address poll kernel; each caller retains site-specific error frame (addr-first vs expected-first byte order preserved); eprom verify_and_update_mask untouched; zero-diff traces; +2 B flash delta; firestarter@abbbb5c
- [Phase 89-05, 2026-06-26]: PRIM-06 closed — 89-FLASH-LEDGER.md authored: step table P7(0B)+P4(-164B)+P3(-402B)+P5(+2B)=-564B net; final flash 25090 B (87.5%) vs 25654 B baseline; D-01 PASS (25090 < 25654); no D-02 deferrals; all 4 primitives committed; 102/102 native PASS; check_dispatch 0 violations; diff_db identity; SAFE-04 intact (D-08 threshold in primitives.cpp:98, resolve_chip present, 2516 UNVERIFIED); INV-01..09 all >=3 files. Phase 89 COMPLETE. meta@0c31bd4

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| 85 | 01 | 4min | Wave-0 scaffold: branch fork + datasheets-check.sh |
| 85 | 02 | 8min | 17 PDFs downloaded and committed (DSHEET-01/02) |
| 85 | 03 | 5min | README.md authored + phase-gate PASS (DSHEET-03) |
| 86 | 01 | 14min | VAR-01 DECODE-NOTES.md + Wave-0 oracle (FM1608 GREEN / X88C64 RED-as-designed / EVIDENCE GREEN); build_db.py untouched |
| 86 | 04 | 34min | VAR-05/SAFE-04 — 2516 + 2532 non-upstream supplement (extra_chips.json + DIP24_2532); post-decode merge (744→746); diff_db EXTRA_CHIPS_SUPPLEMENT exit 0; check_dispatch 0 violations; 8 supplement tests; 2516 UNVERIFIED + wire-stable; 686 host tests green |
| 86 | 03 | 17min | VAR-03/04/SAFE-04 — re-pin both baselines LAST to the 746-chip correct DB (chip_database.baseline.json byte-identical; dispatch_baseline.json regenerated via check_dispatch mirror + Phase-86/SHA-a8efaedc/VAR-05 provenance); diff_db.py now IDENTITY diff exit 0 (D-07 closed); check_dispatch 0 violations; full py3.11 gate green (686 tests / 77.69% cov / ruff / format / mypy-watermark); 4 tools/ ruff errors pre-existing + out-of-CI-scope. Phase 86 COMPLETE |
| 87 | 02 | 18min | NAME-02 — rationale header blocks in all 10 handler files; INV-01..INV-09 greppable in doc+handler; comment-only diff guard PASS (zero flash delta). firestarter@f362263/3b8202d |
| 87 | 03 | 10min | NAME-03/SAFE-02 — 9 INV-id-bearing live Unity assertions across 4 test_val_* suites; recording-buffer overflow resolved for INV-04 (65-byte probe); 91/91 native tests pass. firestarter@b67acde |
| 87 | 04 | 2min | NAME-05/SAFE-03/SAFE-06 — All 5 frozen-world gates PASS: check_dispatch 0 violations (746 chips), diff_db empty (0 changed), flash delta=0 (25654/25654), all 9 INV >=3 files, host git-diff clean. Phase 87 COMPLETE. |
| 88 | 04 | 8min | SAFE-02/PRIM-01 — dispatch-mirror invariant test: three-way bind doc↔tool↔firmware over full §0 table; 2 pytest pass; ruff-clean. firestarter_app@e46549f |
| 88 | 02 | 30min | PRIM-01/SAFE-02 — eeprom28c + flash_intel golden traces: 4 fixtures (17+17+7+6 entries); 10 suite tests green; delayMicroseconds+millis() stubs added to flash_intel setUp(); eeprom28c chip-id via CMD_WRITE+init-only. firestarter@0b1ce93/fa0f908 |
| 88 | 03 | 20min | PRIM-01/SAFE-02 — flash3 + flash4 golden traces: 3 fixtures (12+206+16 entries); 17 suite tests green; millis() stub added to flash3 setUp(); flash4 chip-id scripted mock (Pitfall 3); flash3 no chip-id (D-03 coverage). firestarter@1282c32/e6cce3e |
| 88 | 05 | 10min | SAFE-04/D-07/D-08/D-09 — frozen-world gates + SC#4 posture: 16/16 native PASS, check_dispatch 0 violations, diff_db empty, flash=25654 B (0-byte delta), VPP checks + resolve_chip guard present+unmodified, 2516 UNVERIFIED. Phase 88 COMPLETE. meta@467a10f |
| 89 | 01 | 8min | PRIM-02/P7 — delete-not-merge const-table dedup: FLASH_ENABLE_WRITE_PROTECTION + EEPROM_SDP_DISABLE removed; caller redirected to FLASH_DISABLE_WRITE_PROTECTION; 102/102 native PASS, flash delta=0 B (25654→25654), check_dispatch 0 violations, diff_db empty, INV-01..09 >=3 files. firestarter@0052c42 |
| Phase 89 P89-02 | 12min | 2 tasks | 6 files |
| Phase 89 P89-03 | 18min | - tasks | - files |
| Phase 89 P04 | 15min | 2 tasks | 4 files |
| 89 | 05 | 8min | PRIM-06 — 89-FLASH-LEDGER.md: step table P7/P4/P3/P5; final 25090 B (87.5%, -564 B net); D-01 PASS; 102/102 native; check_dispatch 0 violations; diff_db empty; SAFE-04 intact; Phase 89 COMPLETE. meta@0c31bd4 |

## Deferred Items

**Re-acknowledged at v1.15 milestone close (2026-06-25):** all prior open items are pre-existing carry-forwards or intentional v1.15 deferrals. See full table in the v1.15 STATE.md snapshot or `.planning/milestones/v1.15-MILESTONE-AUDIT.md`.

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| FUT-01 (v1.14) | X88C64 0x34 graduation | deferred — PCB-blocked | A6 ALE-routing PCB-BLOCKED (HIGH); stays `protocol-not-implemented`. |
| FUT-03 (v1.15) | 2516 0x0B read instability + write proof | deferred best-effort (D-22) | 3 distinct SHAs after VPP-skip; shared OE/VPP pin; FUT-03. |
| FUT-04 (v1.14) | AT28C04/16 adapter graduation | deferred — adapter not built | 9 chips stay `adapter-required`; ADPT-01/02/03. |
| FUT-05 (v1.15) | REWR-02 0x08 write proof | deferred — no functional 0x08 chip | W27E040 stuck-bit; need sibling 0x08 rewritable chip. |
| CR-01 / Phase-74 Wave-2 | W29C040 flash4 256B page-write fault | open — reopened by Phase 84 | Phase-74 fix not silicon-effective. Reopen Phase-74 Wave-2 (likely dual-repo lockstep firmware fix). |
| FUT-06 (v1.15) | AM27C020 0x08 32-pin write/VPP path | deferred — RCA'd, not trivially fixable | 0-bits-programmed; requires 0x08 32-pin Large EPROM write/VPP root-cause. |
| release-gate | Lockstep beta cut `3.0.0b11` + gitlink bump | OPERATOR-GATED | Standing v1.11–v1.15 policy; gitlinks PINNED. |

## Operator Next Steps

- Plan the new Phase 86 (variant decode): `/gsd-plan-phase 86`
  - Recommend running with research (the variant high-byte decode needs minipro `database.c` + datasheet grounding).

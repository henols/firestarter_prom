---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Safety Closure & Hardware Validation
status: verifying
last_updated: "2026-05-12T09:02:18.546Z"
last_activity: 2026-05-12
progress:
  total_phases: 5
  completed_phases: 2
  total_plans: 5
  completed_plans: 5
  percent: 100
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-05-12

## Current Position

Phase: 02 (naming-cleanup-wire-key-minipro-references) — COMPLETE (ready for /gsd-verify-work)
Plan: 3 of 3 complete
Status: Phase 02 closed — WIRE-01, WIRE-02, CLEAN-01, CLEAN-02 all discharged
Last activity: 2026-05-12 — Plan 02-03 complete (firestarter_app@0489a20 + firestarter@587396a; check_dispatch.py 743-chip wire round-trip green; SC#5 CLI smoke all exit 0)

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-11)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** Phase 02 — naming-cleanup-wire-key-minipro-references

- Intel-flash REQ-SAF-01 closure (VPP ADC compare in `flash_intel_write_init`)
- 28C chip-ID forward-compat (`eeprom28c_write_init` honouring `handle->chip_id`)
- Wire JSON `"vpp"` → `"vpp_mv"` rename (atomic Python + firmware sync)
- Retroactive `VERIFICATION.md` artifacts for Phases 01-10
- Physical-hardware validation of the four canon chip families on a RURP shield

## Roadmap Summary

| Phase | Name | Requirements |
|-------|------|--------------|
| 1 | Safety Closure (Intel-flash VPP + 28C chip-ID) | SAF-04, SAF-05, SAF-06 |
| 2 | Wire Protocol Rename (`vpp` → `vpp_mv`) | WIRE-01, WIRE-02 |
| 3 | Retroactive Verification (Phases 01-10) | VERIF-01..VERIF-10 |
| 4 | Hardware Validation (RURP shield) | HW-01..HW-05 |
| 5 | Milestone Close | DOC-01 |

## Milestone History

- **v1.0** — Protocol-Aware Programming Architecture (shipped 2026-05-11) —
  see `.planning/MILESTONES.md` + `.planning/milestones/v1.0-*.md`

## Accumulated Context

### Open Blockers

None.

### Resolved in v1.1

- WARNING-1 — Intel-flash write path missing VPP ADC compare → **CLOSED by Plan 01-01** (`flash_intel_check_vpp` + 5 Unity tests; 20/20 native tests passing)

### Open Warnings (now tracked as v1.1 phases)

- WARNING-2 — `eeprom_28c.cpp` ignores `handle->chip_id` → **CLOSED by Plan 01-02** (`eeprom28c_check_chip_id` A9-12V + 4 Unity tests; 24/24 native tests passing)
- WARNING-3 — wire JSON `"vpp"` key carries millivolts → **CLOSED at source level by Plan 02-01** (firmware `firestarter@39b29a9` atomic three-site flip in `json_parser.c` + Python `firestarter_app@20cfe86` emitter rename at `database.py:518`; both CLAUDE.md examples synced; 8/8 cross-sub-repo grep gates pass; `pio run -e uno/leonardo` both succeed; 25/25 native tests pass). **D-04 internal twin (`_map_data` dict key `"vpp"` carrying float volts next to `"vpp_mv"` int mV) CLOSED by Plan 02-02** (firestarter_app@9e61061 — internal dict key renamed to `"vpp_volts"` at `database.py:417` + emitter fallback at `:510` + 2 downstream consumers at `eprom_info.py:271` + `ic_layout.py:516`; upstream-schema READ at `database.py:375` PRESERVED per D-08-compat). **WIRE-02 regression evidence + CLEAN-02 attribution scrub + SC#5 CLI smoke CLOSED by Plan 02-03** (firestarter_app@0489a20 — D-15 Shape A wire round-trip in check_dispatch.py asserts "vpp_mv" in wire AND "vpp" not in wire for all 743 chips, exits 0 with "0 wire-key regressions"; minipro reduced to 1 surviving attribution at firestarter_app/CLAUDE.md:68 next to infoic.xml + chip_database.json; firestarter@587396a — final minipro mention in firmware CLAUDE.md flipped to "upstream"; pip install -e . + firestarter --help + firestarter info W27C512 + firestarter info --adapter W27C512 all exit 0).
- WARNING-4 — `firestarter_test.sh` / `write_test.sh` reference deleted `database_generated.json` → **Phase 4 (HW-01)**

(Full audit trail: `.planning/milestones/v1.0-INTEGRATION-CHECK.md` and `.planning/milestones/v1.0-MILESTONE-AUDIT.md`.)

### Resolved Blockers (v1.0)

- BLOCKER-1 (Phase 12) — algorithm-based dispatch for protocols 0x05/0x06/0x07/0x08/0x0B
  and SRAM 0x0E/0x27/0x28/0x29

- BLOCKER-2 (Phase 12) — SRAM chips routed to `configure_eprom` with 12V VPP regulator
- WARNING-5 (Phase 13) — AT28C256/64 5V EEPROM 12V-on-A14 hazard via DB override

## Decisions (Phase 1)

- **D-04 (SAF-04):** `flash_intel_check_vpp` implemented as inline-copy static helper in `flash_intel.cpp` — `eprom_check_vpp` left byte-identical; shared helper extraction deferred to cleanup phase
- **D-05 override (SAF-05, load-bearing):** `eeprom28c_check_chip_id` uses A9-12V identification (RESEARCH.md datasheet evidence), NOT the AMD/SST JEDEC AA/55/90 sequence from CONTEXT.md D-05. JEDEC sequence would corrupt address 0x5555 on SDP-disabled AT28C parts.
- **ArduinoFake delay() + delayMicroseconds():** Any test suite that drives `operation_init` must mock BOTH `delay()` AND `delayMicroseconds()` in `setUp()` — fakeit aborts on unmocked virtuals
- **configure_memory() function-pointer overwrite:** `configure_memory()` overwrites `handle->firestarter_get_data` with `memory_get_data` before calling the specific handler. Tests that mock `firestarter_get_data` must RE-ASSIGN the mock pointer AFTER `configure_memory()` and before `operation_init()`.

## Decisions (Phase 2)

- **Plan 02-01 commit order — firmware first, Python second.** Recommended by Phase 2 RESEARCH.md "Cross-Sub-Repo Coordination Pattern"; SAF-04 (shipped Phase 1) makes either order safe via zero-init `handle->vpp_mv` VPP-HIGH guard (RESEARCH.md Pitfall #3). Both sub-repo commits land in the same wave: firmware `39b29a9`, then app `20cfe86`.
- **Plan 02-01 — rename, not delete, at `database.py:518`.** Honored RESEARCH.md "Factual Correction" over CONTEXT.md D-02's "delete `\"vpp\": vpp_mv,`" framing. The live wire today emits exactly one VPP key (`"vpp"` carrying integer mV); there is no second `"vpp_mv": ...,` line to delete. The correct edit is a one-character-class swap on a single line.
- **Plan 02-01 — firmware atomic three-site flip locked into ONE commit.** PROGMEM literal (`:62`) + dispatch table row (`:74`) + `extract_int` macro arg (`:309`) all flip in one firmware commit. Half-flipped state would silently drop the field (RESEARCH.md Pitfall #1).
- **Plan 02-02 — three tasks collapsed into ONE `firestarter_app/` commit (9e61061) per D-13 natural atomicity.** CLEAN-01 `git mv` rename + 7 path callsite flips + D-04 internal `vpp_volts` rename + v1.0 Phase 11 `pyproject.toml`/`MANIFEST.in` packaging-drift fix all land together so package state is coherent at every revision. Firmware sub-repo CLAUDE.md edit in its own commit (`firestarter@8bb85e1`).
- **Plan 02-02 — index-only partial staging for `ic_layout.py`.** Working tree carried a pre-existing co-located black/whitespace reformat with a load-bearing `pin_map_details["vpp-pin"][0]` indexing bugfix needed for SC#5 smoke. Recipe: `cp worktree → /tmp; git checkout HEAD -- file; re-apply scoped vpp_volts line; git add; restore from /tmp`. Result: index contains exactly the one-line scoped edit; pre-existing reformat remains unstaged for a future plan.
- **Plan 02-02 — upstream-schema READ at `database.py:375` PRESERVED** (`electrical.get("vpp", "0").replace("V", "")`). RESEARCH.md Pitfall #2 three-vpp-concepts distinction held: internal dict key renamed to `"vpp_volts"`; wire emit key already `"vpp_mv"` (Plan 02-01); upstream-schema read against on-disk DB `"12V"` string + legacy user-override DBs UNCHANGED per D-08-compat.
- **Plan 02-03 — surviving minipro attribution at `firestarter_app/CLAUDE.md:68`, not `:42`.** RESEARCH.md "Missed Callsites" gave the binary choice; `:68` sits next to `infoic.xml` (the actual upstream file) and ends with `chip_database.json` (the renamed local artifact) — single self-contained provenance pointer beats two non-adjacent half-attributions. Plan body's nominal `:69` line number was an off-by-one shift after Plan 02-02 edits; used content-based location.
- **Plan 02-03 — Shape A wire round-trip fused into existing `check_dispatch.py`.** Per RESEARCH.md recommendation: per-chip `db.convert_to_programmer(db.get_eprom(part))` round-trip added inside the existing 743-chip dispatch-scan loop (parallel failure list `wire_regressions`, sibling reporter block, extended PASS line). Single-binary "scanner == gate" UX preserved; Shape B parametrize-pytest rejected because it would have split CI signal across two tools.
- **Plan 02-03 — `MINIPRO_XML_URL` constant + argparse `default="minipro"` preserved verbatim per D-09.** `build_db.py:10` constant identifier (case-sensitive grep counts only the lowercase URL substring on `:10`, not the uppercase identifier or its `:157/:159` usages) and `:29 default="minipro"` (load-bearing CLI default directory path) both unchanged. CLAUDE.md surviving attribution + these two file-level survivors together form the canonical minipro-provenance triplet.

## Operator Next Steps

- Plan 02-03 complete. CLEAN-02 attribution closed (1 surviving line at firestarter_app/CLAUDE.md:68; 0 in firestarter/CLAUDE.md; 0 in meta CLAUDE.md). WIRE-02 dynamic evidence closed (check_dispatch.py per-chip wire round-trip exits 0 with "0 wire-key regressions" across all 743 chips). SC#5 fully discharged (pip install -e . + firestarter --help + firestarter info W27C512 + firestarter info --adapter W27C512 all exit 0).
- Phase 02 fully discharged: WIRE-01 (Plan 02-01) + WIRE-02 (Plan 02-03) + CLEAN-01 (Plan 02-02) + CLEAN-02 (Plan 02-03) all closed.
- Run `/gsd-verify-work 02` next to confirm Phase 02 verification artifacts and trigger Phase 3 (Retroactive Verification) planning.
- Pre-existing dirt logged for a future scoped plan (unchanged since Plan 02-02): `firestarter_app/firestarter/__init__.py` version bump 2.0.6 → 2.0.7_dev; `firestarter_app/.planning/codebase/*.md` deletions; `firestarter_app/firestarter/ic_layout.py` black/whitespace reformat carrying a load-bearing `pin_map_details["vpp-pin"][0]` indexing fix.

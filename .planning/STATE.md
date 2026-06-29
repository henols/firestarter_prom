---
gsd_state_version: 1.0
milestone: v1.18
milestone_name: AM27C020 0x08 Write-Path RCA & Fix
status: planning
last_updated: "2026-06-29T12:15:57.443Z"
last_activity: 2026-06-29
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-06-27

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-06-29 — Milestone v1.18 started

## Project Reference

See: `.planning/PROJECT.md` (v1.17 Current Milestone section + Key Decisions)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware handler. v1.17 proves that contract on the W29C040 flash4 (`0x05`) write path: root-cause the page-0 write fault, make flash4 page sizing datasheet-sourced per-chip (CR-01), and bench-prove byte-exact write→read→verify on real silicon.

**Current focus:** Phase 94 — fix-pgsz-firmware-write-path-fix-datasheet-sourced-per-chip-page-size

## Milestone Context (v1.17)

- **Scope (operator-confirmed 2026-06-26):** widest — W29C040 RCA + fix **and** generalize CR-01 (datasheet-sourced per-chip `page_size` DB field).
- **Branch base:** firmware forks off the **v1.16 tip `a296195`** (primitives recompose), NOT firmware `beta` (stale at v1.13 `a1953c2`). Mirrors v1.15/v1.16 precedent; gitlinks PINNED at b10; lockstep beta cut operator-gated. Meta `.planning/` proceeds per convention.
- **Done bar:** byte-exact write→auto-erase→program→verify SHA on the seated W29C040 (Leonardo + Rev 2.0). Hard graduation gate — no best-effort fallback authorized.
- **Bench LOCKED to Leonardo + RURP Rev 2.0.** Standing discipline: live R1/R2 readback each task, verify `controller:` port identity per task, Leonardo chip-OUT-sideload-exempt. Operator seats the W29C040 so the bench can be driven unattended.
- **Dual-repo lockstep** (`constants.py` ↔ `firestarter.h`) if `page_size` crosses the wire; reuse-first; py3.12-masks-CI-3.11 ruff/codegen trap watch.
- Phase numbering continues from v1.16's Phase 92 → **v1.17 starts at Phase 93**.
- Closes **CR-01 / Phase-74 Wave-2** (W29C040 flash4 256 B page-0 fault; open since v1.13, confirmed not-silicon-effective at v1.15 Phase 82/84).

## Roadmap Summary (v1.17 — Phases 93–96)

Created 2026-06-26 · granularity Comprehensive · 16/16 requirements mapped (no orphans, no duplicates). Strict sequence: **RCA → FIX+PGSZ → BENCH → LEDGER**. SAFE-01 homes in Phase 93, SAFE-02 in Phase 94; both recur as preconditions through close.

| Phase | Goal | Requirements | Bench-gated |
|-------|------|--------------|-------------|
| 93 — RCA | Reproduce + differentially isolate + name the W29C040 page-0 write-fault root cause | RCA-01, RCA-02, RCA-03, SAFE-01 | yes (Leonardo + Rev 2.0, seated W29C040) |
| 94 — FIX + PGSZ | Fix flash4 write path (traces/guard green) + datasheet-sourced per-chip `page_size` over the wire (CR-01) | FIX-01/02/03, PGSZ-01/02/03, SAFE-02 | no (native + host CI) |
| 95 — BENCH | Byte-exact write→auto-erase→program→verify (SHA) graduation gate + W29C020 sibling regression + EVIDENCE | BENCH-01, BENCH-02, BENCH-03 | yes (hard graduation gate, no fallback) |
| 96 (close) — LEDGER | PROTOCOL-LEDGER → W29C040 PASS/`supported`, close CR-01/Phase-74 Wave-2, `check_ledger.py` green, milestone close | LEDGER-01, LEDGER-02 | no |

**Dependency chain:** 93 → 94 → 95 → 96 (linear; RCA must name the cause before FIX is designable; BENCH gates on the committed fix + `page_size`; LEDGER records the bench PASS).

**Firmware/host surfaces:** `firestarter/src/proms/flash_type_4.cpp` (fix, on the `a296195` recompose) + flash4 golden traces/dispatch-mirror guard (keep green); host `build_db.py` / `chip_database.json` / `constants.py` ↔ `firestarter.h` (per-chip `page_size` lockstep field); `check_dispatch.py` / `diff_db.py` / `check_ledger.py` gates.

## Accumulated Context

### Deferred Items (carry-forward at v1.16 close — 2026-06-26)

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| FUT-01 (v1.14) | X88C64 0x34 graduation | deferred — PCB-blocked | A6 ALE-routing PCB-BLOCKED (HIGH); stays `protocol-not-implemented`. |
| FUT-03 (v1.15) | 2516 0x0B read instability + write proof | deferred best-effort (D-22) | 3 distinct SHAs after VPP-skip; shared OE/VPP pin. |
| FUT-04 (v1.14) | AT28C04/16 adapter graduation | deferred — adapter not built | 9 chips stay `adapter-required`. |
| FUT-05 (v1.15) | REWR-02 0x08 write proof | deferred — no functional 0x08 chip | W27E040 stuck-bit; need sibling 0x08 rewritable chip. |
| FUT-06 (v1.15) | AM27C020 0x08 32-pin write/VPP path | deferred — RCA'd, not trivially fixable | 0-bits-programmed; needs 0x08 32-pin Large EPROM write/VPP root-cause. |
| **CR-01 / Phase-74 Wave-2** | **W29C040 flash4 256 B page-0 write fault** | **ACTIVE — v1.17 target** | Phase-74 fix not silicon-effective; page size already correct (256 B) → deeper RCA. **This milestone.** |
| release-gate | Lockstep beta cut `3.0.0b11` + gitlink bump | OPERATOR-GATED | Standing v1.11–v1.16 policy; gitlinks PINNED at b10. |
| uat_gap | Phase 85 — 85-HUMAN-UAT.md (2 pending scenarios) | partial | v1.16 carry-forward. |

### v1.9 DEFERRED (operator 2026-06-08 — resumes later at Phase 45)

v1.9 (Read-Bug RCA + Fix) is paused. Phase 44 (Bug A RCA) complete; remaining Phases 45–48. The v1.17 bench oracle is pinned to Leonardo + Rev 2.0 precisely to avoid the v1.9 shield-fleet read bug.

### v1.10 Substrate (carry-forward)

Transport provably byte-exact (COBS `0x00` + CRC8-CCITT) — settled variable. GATE-1.8d ring-fence intact.

### v1.16 Substrate (carry-forward, directly relevant to v1.17)

- **flash4 lives on the primitives recompose** (`a296195`): `flash_type_4.cpp` uses P7/P4/P3/P5 shared primitives; `flash4_page_size(mem_size)` capacity heuristic still in place (the CR-01 target).
- **PROTOCOL-LEDGER** at `.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}` + `check_ledger.py`; W29C040 0x05 carried as an open defect (CR-01). v1.17 must update this on bench PASS.
- **Golden register traces + dispatch-mirror guard** pinned for flash4 (Phase 88-03, 206-entry write trace) — the recompose oracle the W29C040 fix must keep green.
- **datasheets/** folder exists in the firestarter sub-repo; no W29C040 datasheet committed yet (Phase 85 bot-blocked some). May need acquisition for the datasheet-sourced `page_size`.

### Pending Todos (carried forward)

- `flash4-page-size-datasheet-sourced-cr01.md` (medium) — **directly resolved by v1.17** (datasheet-sourced per-chip `page_size`).
- `avrdude-mcu-detection-fallback.md` (low) — out of scope, carry forward.
- `cobs-decoder-framelevel-deadline-wr01.md` (medium) — v1.10 COBS follow-up; deferred.
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` (firmware) — carry forward.
- `large-read-data-jitter-uno328pb.md` (HIGH, v1.8-seed) — v1.9 RCA target.
- `photograph-modified-rev-0.md` (medium) — carry forward.

### Decisions (v1.17)

- **T-93-CANERASE (Phase 93 Plan 01, 2026-06-26):** FLAG_CAN_ERASE (0x02) IS set in W29C040 wire flags — `flash4_erase_execute` asserts 12V on a 5V-only chip. Bench plans 02–04 MUST use `--skip-erase`. Phase 94 FIX-01 scope: prevent FLAG_CAN_ERASE from reaching `flash4_erase_execute` for protocol 0x05 chips.
- **Phase-74 traps ruled out (Phase 93 Plan 01, 2026-06-26):** SDP present and 256B page confirmed by native tests (11/11 PASS). RCA must search deeper than Phase-74 hypotheses.
- **H4 DISCONFIRMED (Phase 93 Plan 02, 2026-06-27):** Address 0x0000ff stays 0x00 (not 0x04) after N=5 settled reads following fault — page never committed. Poll did not merely give up on a late-completing write. H1 (T_BLC timing) and H3 (SDP rejection) remain active hypotheses.
- **T-93-CANERASE gate cleared by operator (2026-06-27):** Proceed-with-skip-erase authorized. All Plan 02 writes used `--skip-erase`. Full fix (FIX-01) deferred to Phase 94.
- **RCA-01 reproduction confirmed N=2 (Phase 93 Plan 02, 2026-06-27):** ERROR frame identical on both runs: `Timeout verifying 0x04 at 0x0000ff (got 0x00)`. Decoded: `[expected=0x04, A16=0x00, A8=0x00, A0=0xFF, observed=0x00]`. Same failing site (0x0000ff) as v1.15 Phase 82/84 baseline.
- **H5 CONFIRMED as root cause (Phase 93 Plan 03, 2026-06-27):** W29C040 §6.6 first-16K boot block programming lockout permanently activated on this chip instance. Boundary sweep: 0x3F00 FAILS, 0x4000 PASSES — exact step at 16K boundary. H1/H2/H3/H4 all DISCONFIRMED with direct bench evidence. Firmware write algorithm is correct for unlocked pages.
- **W29C020 live control DEFERRED per operator (Phase 93 Plan 03, 2026-06-27):** Datasheet-only differential done (SDP/pinout/VPP same in both; page size/A18/boot-block-boundary differ). Live write deferred as best-effort.
- **SERIAL_DEBUG+DEBUG_ADDRESS overhead trap (Phase 93 Plan 03, 2026-06-27):** Combining both flags causes 5008+ poll messages per 1-byte write, swamping host protocol and causing Command 2 timed out. Future trace builds: use DEBUG_ADDRESS without SERIAL_DEBUG, or capture init-phase only.
- **Phase 94 FIX-01 scope clarified (Phase 93 Plan 03, 2026-06-27):** Root cause is chip-instance-specific silicon, not firmware. Firmware write algorithm is correct. FIX-01 still needed for T-93-CANERASE (FLAG_CAN_ERASE=0x02 12V hazard). Unlocked W29C040 or addresses ≥0x4000 needed for BENCH graduation.
- **RCA-03 NAMED: SILICON classification confirmed (Phase 93 Plan 04, 2026-06-27):** H5 CONFIRMED as sole surviving hypothesis. Classified SILICON/chip-instance-specific-hardware-feature-state. H1(timing)/H2(addressing)/H3(SDP)/H4(poll-site) all disconfirmed with direct bench evidence. Phase 44 D-07 causal bar met (exact 16K boundary is the variable that moves the failure).
- **Lock reversibility fork (Phase 93 Plan 04, 2026-06-27):** Evidence is agnostic on whether §6.6 lock is software-reversible (a) or hardware-permanent (b). Research notes lean (b) but PDF not directly readable. Phase 94 FIRST STEP: read §6.6 for UNLOCK command. If (a): add boot-block unlock to flash4 write path; if (b): different chip or re-scope BENCH-01.
- **SAFE-01 = HELD (Phase 93 Plan 04, 2026-06-27):** Conditional — held only because --skip-erase was used throughout RCA. Underlying T-93-CANERASE hazard (FLAG_CAN_ERASE=0x02 → 12V on 5V chip) remains OPEN until Phase 94 FIX-01. Phase 94 must implement FIX-01 before any bench work without --skip-erase.
- **Milestone done-bar impact noted (Phase 93 Plan 04, 2026-06-27):** If §6.6 lock is permanent (b), Phase 95 BENCH-01 byte-exact write→verify on page-0 is not achievable on current chip. Operator decision needed: new chip OR re-scope to addresses ≥0x4000.

### Decisions (Phase 94 Plan 02, 2026-06-27)

- **PGSZ wire field end-to-end (Phase 94 Plan 02, 2026-06-27):** JSON_KEY_PAGE_SIZE = "page-size" added host-side; emit-when-present mirrors read-strobe-us pattern; uint32_t page_size in firestarter_handle_t; key_page_size PROGMEM + get_page_size parser in json_parser.c. V5 bound-check: 0/absurd → handle->page_size=0 → firmware heuristic fallback.
- **Cited values only: W29C040=256, W29C020=128 (Phase 94 Plan 02, 2026-06-27):** _PAGE_SIZE_BY_PART in build_db.py; W29C040/W29C042=256 from W29C040.pdf §6.2; W29C020/W29C020C/W29C022=128 from W29C020.pdf §6.2. No [ASSUMED] values graduated.
- **flash4_page_size heuristic retained as fallback (Phase 94 Plan 02, 2026-06-27):** Safe-fallback form: handle->page_size ? handle->page_size : flash4_page_size(handle->mem_size). Zero-initialized handle → page_size==0 → heuristic. Heuristic NOT deleted.
- **address=126/data_size=4 native test window (Phase 94 Plan 02, 2026-06-27):** address=0/data_size=129 exceeded 256-entry recording cap (8+128*3=392 entries). address=126/data_size=4 yields 31 entries; still crosses 128B boundary at addr 128. Discriminant preserved.

### Decisions (Phase 94 Plan 01, 2026-06-27)

- **FIX-01a IMPLEMENTED (Phase 94 Plan 01, 2026-06-27):** T-93-CANERASE mitigated. Defense-in-depth: host `convert_to_programmer` now gates `FLAG_CAN_ERASE` on `algorithm != 5`; firmware `flash4_write_init` skips `flash4_erase_execute` when `handle->protocol == 0x05`. W29C040 wire flags now 0x00. Phase 95 bench can proceed without `--skip-erase`.
- **D-06 guard keyed on protocol (Phase 94 Plan 01, 2026-06-27):** Firmware guard uses `handle->protocol == 0x05`, NOT `handle->vpp_mv`. W29C040 vpp_mv=12000 is a chip-ID datum, not a program rail — voltage heuristic would never fire (Pitfall 3).

### Blockers / Concerns

- **Boot-block lock on seated chip (carry-forward):** §6.6 lock is permanent (no unlock command). Phase 95 BENCH-01 requires addresses ≥0x4000 on current chip, or a new unlocked chip. Operator decision needed before Phase 95.

### Decisions (Phase 94 Plan 04, 2026-06-27)

- **SAFE-02 CLOSED (Phase 94 Plan 04, 2026-06-27):** Python 3.11.15 obtained via uv. All 9 ci.yml steps green on py3.11.15. py3.11 traps cleared (no f-string backslash SyntaxErrors; codegen drift-gate clean). Constants parity confirmed: all 8 FLAG_* bits match; JSON_KEY_PAGE_SIZE is a wire string (not a flag), parity unaffected.
- **Writable region proof N=3 COMPLETE (Phase 94 Plan 04, 2026-06-27):** W29C040 writable region 0x4000+, 16KB, 3 write→verify cycles, all SHA match. Used -b (skip blank check only); FLAG_CAN_ERASE=0 post-FIX-01a → no 12V erase. W29C040 auto-erases per page via SDP. No --skip-erase used.
- **read command output semantics confirmed (Phase 94 Plan 04, 2026-06-27):** `firestarter read -a ADDR --size SZ` returns (ADDR+SZ) bytes starting from address 0; target region data starts at offset ADDR in the output file.
- **Boot-block detect live-trigger not achieved (Phase 94 Plan 04, 2026-06-27):** Blank check fires before write attempt (non-blank locked region). Confirmed via Plan-03 native test + Phase-93 silicon boundary evidence. No --skip-erase bypass was used.

## Operator Next Steps

- Start the next milestone with /gsd-new-milestone

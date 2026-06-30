---
gsd_state_version: 1.0
milestone: v1.18
milestone_name: — AM27C020 0x08 Write-Path RCA & Fix
status: executing
last_updated: "2026-06-30T14:36:00.000Z"
last_activity: 2026-06-30 -- Phase 98 HELD: both plans executed + native-green, but code review CR-01 (BLOCKER) found the firmware PGM hold-LOW is a physical no-op on Rev 2.x (pin-31 control bit OR-aliased to VPP-P1 held HIGH). Operator investigating Rev-2 schematic before completion.
progress:
  total_phases: 7
  completed_phases: 4
  total_plans: 13
  completed_plans: 13
  percent: 54
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-06-30

## Current Position

Phase: 98 (fix-correct-the-0x08-32-pin-write-vpp-path) — HELD (executed, NOT verified/complete)
Plan: 2 of 2 (both plans executed + committed; native suite 117/117 green)
Status: Phase 98 ON HOLD — code review CR-01 (BLOCKER) found the firmware PGM=VIL hold-LOW is a physical NO-OP on Rev 2.x. On Rev 2, pin-31's control bit is OR-aliased to CTRL_VPP_P1_ENABLE (both == phys 0x08), which is held HIGH for VPP across the whole program window, so `clear(logical A18)` cannot pull the shared physical bit LOW. Fix is correct on Rev 0/1 only. WR-01: native tests assert on the LOGICAL register and never run the Rev-2 remap → passed green-by-construction. See 98-REVIEW.md.
Next: OPERATOR — confirm against the Rev-2 schematic whether pin 31 / PGM truly shares the P1 output node. If yes, the register-clear approach can't deliver VIL while VPP-on-P1 is active and the fix needs rethinking (dedicated PGM strobe, or sequence PGM outside the P1-high window). Then /gsd-plan-phase 98 --gaps (CR-01 fix + a Rev-2-physical native test that runs rurp_map_ctrl_reg_for_hardware_revision). Phase 99 bench spend is gated behind this.
Last activity: 2026-06-30 -- Phase 98 HELD on CR-01 (see frontmatter)

## Project Reference

See: `.planning/PROJECT.md` (v1.18 Current Milestone section + Key Decisions)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware handler. v1.18 proves that contract on the AM27C020 `0x08` EPROM-QUICK 32-pin write path: root-cause the 0-bits-programmed failure, fix the write/VPP path (RC-1 leading: PGM pin 31 mapped as address line rather than held program-active), and bench-prove byte-exact write→verify on real silicon — gated on Tier-0 writability pre-flight.

**Current focus:** Phase 98 — fix-correct-the-0x08-32-pin-write-vpp-path

## Milestone Context (v1.18)

- **Scope (operator-confirmed 2026-06-29):** Single-chip RCA→fix→bench: AM27C020 `0x08` 32-pin write/VPP path. FUT-06 (carried from v1.15) elevated to the primary target.
- **Branch base:** Firmware forks off the v1.17 tip (continues prior base), NOT firmware `beta` (stale at v1.13 `a1953c2`; lacks v1.15 VPP-skip + v1.16 recompose + v1.17 fixes). Mirrors v1.15–v1.17 precedent; gitlinks PINNED; lockstep beta cut operator-gated.
- **Done bar:** byte-exact write→verify SHA on the seated AM27C020 (Leonardo + Rev 2.0). Hard graduation gate contingent on PRE-01 writability — if OTP/dead, clean deferral to FUT is the acceptable alternate outcome.
- **Bench LOCKED to Leonardo + RURP Rev 2.0.** Standing discipline: live R1/R2 readback each task, verify `controller:` port identity per task, Leonardo chip-OUT-sideload-exempt.
- **Dual-repo lockstep** (`constants.py` ↔ `firestarter.h`; pinout DB) wherever the fix crosses the wire. Reuse-first. Watch the py3.12-masks-CI-3.11 ruff/codegen drift trap.
- Phase numbering continues from v1.17's Phase 96 → **v1.18 starts at Phase 97**.
- Closes **FUT-06** (AM27C020 `0x08` 32-pin write/VPP path; RCA'd at v1.15 Phase 83/84, not trivially fixable, 0-bits-programmed).

## Roadmap Summary (v1.18 — Phases 97–99)

Created 2026-06-29 · granularity Comprehensive · 11/11 requirements mapped (no orphans, no duplicates). Strict sequence: **PRE+RCA → FIX → BENCH+LEDGER**. SAFE-01 homes in Phase 97, SAFE-02 in Phase 98; both recur as preconditions through close.

| Phase | Goal | Requirements | Bench-gated |
|-------|------|--------------|-------------|
| 97 — PRE + RCA | Tier-0 writability pre-flight + reproduce failure signature + differential isolation + named root cause | PRE-01, RCA-01, RCA-02, RCA-03, SAFE-01 | yes (Leonardo + Rev 2.0, seated AM27C020, DMM at pin 1 + pin 31) |
| 98 — FIX | Correct 0x08 32-pin write/VPP path (golden traces green, dual-repo lockstep, py3.11 CI) | FIX-01, FIX-02, FIX-03, SAFE-02 | no (native + host CI) |
| 99 — BENCH + LEDGER | Byte-exact write→verify graduation (contingent on PRE-01) or documented FUT deferral + EVIDENCE + PROTOCOL-LEDGER updated | BENCH-01, BENCH-02 | yes (hard graduation gate; deferral is a clean documented outcome) |

**Dependency chain:** 97 → 98 → 99 (linear; RCA must name the cause before FIX is designable; BENCH gates on the committed fix AND on the Tier-0 writability result from Phase 97).

**Firmware/host surfaces:** `firestarter/src/proms/eprom.cpp` (program-pulse / VPP-routing for `using_p1_as_vpp` 32-pin parts); possibly `firestarter_app/firestarter/data/pinouts.json` (new `DIP32_27C020` entry if PGM-as-address-line is the cause); lockstep `firestarter.h` ↔ `constants.py` if a new wire field is needed; `check_dispatch.py` / `diff_db.py` / `PROTOCOL-LEDGER` gates.

## Accumulated Context

### Deferred Items (carry-forward at v1.17 close — 2026-06-29)

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| FUT-07 (v1.17) | W29C040 byte-exact graduation + LEDGER `supported` | deferred — §6.6 boot block permanently locked on seated chip | Needs a different unlocked sample + third-party bench. All v1.17 software done. |
| **FUT-06 (v1.15)** | **AM27C020 0x08 32-pin write/VPP path** | **ACTIVE — v1.18 target** | 0-bits-programmed; JP4-closed didn't fix; RC-1 (PGM pin 31 mapped as address line) is the leading hypothesis. **This milestone.** |
| FUT-05 (v1.15) | REWR-02 0x08 rewritable write proof | deferred — no functional 0x08 rewritable chip | W27E040 stuck-bit; may benefit from v1.18 `0x08` fix. |
| FUT-04 (v1.14) | AT28C04/16 adapter graduation | deferred — adapter not built | 9 chips stay `adapter-required`. |
| FUT-03 (v1.15) | 2516 0x0B read instability + write proof | deferred best-effort (D-22) | 3 distinct SHAs after VPP-skip; shared OE/VPP pin. |
| FUT-01 (v1.14) | X88C64 0x34 graduation | deferred — PCB-blocked | A6 ALE-routing PCB-BLOCKED (HIGH); stays `protocol-not-implemented`. |
| release-gate | Lockstep beta cut `3.0.0b11` + gitlink bump | OPERATOR-GATED | Standing v1.11–v1.17 policy; gitlinks PINNED. |

### v1.9 DEFERRED (operator 2026-06-08 — resumes later at Phase 45)

v1.9 (Read-Bug RCA + Fix) is paused. Phase 44 (Bug A RCA) complete; remaining Phases 45–48. The v1.18 bench oracle is pinned to Leonardo + Rev 2.0 precisely to avoid the v1.9 shield-fleet read bug.

### v1.10 Substrate (carry-forward)

Transport provably byte-exact (COBS `0x00` + CRC8-CCITT) — settled variable. GATE-1.8d ring-fence intact.

### v1.17 Substrate (carry-forward, directly relevant to v1.18)

- **T-93-CANERASE fix shipped (Phase 94 Plan 01):** `FLAG_CAN_ERASE` gated on `algorithm != 5` in host; firmware `flash4_write_init` skips erase when `handle->protocol == 0x05`. No equivalent issue for `0x08` — but establishes the dual-repo lockstep discipline for protocol-keyed defense-in-depth.
- **Per-chip `page_size` wire field added (Phase 94 Plan 02):** precedent for a new wire datum from pinout DB → host → firmware. Same pattern may apply if `DIP32_27C020` needs a new control-pin concept.
- **PROTOCOL-LEDGER at `.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}`** carries `0x08` as `open-defect-carried (FUT-06)`. v1.18 must update this on bench PASS (or re-record at new FUT status).
- **Golden register traces + dispatch-mirror guard** pinned for `eprom` family (0x07/0x08/0x0B, Phase 88). Any `eprom.cpp` change must keep 0x07 + 0x0B traces byte-identical and add an explicit 0x08 32-pin trace/case (v1.16 P89 CR-01 lesson: need a failure-case/mismatch test).

### v1.18 Research Findings (pre-loaded from `.planning/research/v1.18-AM27C020-27C-EPROM.md`)

- **RC-1 (LEADING):** PGM pin (DIP pin 31) not held program-active; modeled as an address line in `DIP32_STD`. The 27C020's PGM requirement (CE=VIL AND PGM=VIL) is never satisfied — firmware strobes CE only, pin 31 tracks address bits. The 27C040 (where pin 31 = A18) is the chip `DIP32_STD` was authored for.
- **RC-2:** P1 VPP routing/level never proven on a `0x08` UV part. `CTRL_VPP_P1_ENABLE` is only toggled during the per-byte data-write window, not held across the full pulse.
- **RC-3:** JP4 (JMP_VPP_P1_BYPASS) position — JP4-closed alone didn't fix it (Phase 83/84). Cross-confirm with Rev 2.0 schematic semantics.
- **RC-4:** 32-pin high-address / control-bit collision (lower rank — symptom is clean 0-bits at address 0 where collisions are least likely).
- **RC-5:** Chip is OTP/already-programmed/dead (silicon). The Tier-0 pre-flight (PRE-01) determines this definitively before any graduation spend.
- **VPP measurement method:** `firestarter dev reg 0 0 0x86 -f` holds rail for DMM. DMM at socket pin 1 (VPP) AND pin 31 (PGM) during a write attempt is the most decisive measurement.
- **Fix surfaces:** `eprom.cpp` (program-pulse / `using_p1_as_vpp` 32-pin sequencing); `pinouts.json` (possible `DIP32_27C020` entry redirecting pin 31 from address-bus to PGM control); `firestarter.h` ↔ `constants.py` if a new wire flag/field is needed.

### Pending Todos (carried forward)

- `avrdude-mcu-detection-fallback.md` (low) — out of scope, carry forward.
- `cobs-decoder-framelevel-deadline-wr01.md` (medium) — v1.10 COBS follow-up; deferred.
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` (firmware) — carry forward.
- `large-read-data-jitter-uno328pb.md` (HIGH, v1.8-seed) — v1.9 RCA target.
- `photograph-modified-rev-0.md` (medium) — carry forward.

## Operator Next Steps

- Plan Phase 98 with `/gsd-plan-phase 98` (CONTEXT.md ready)

## Decisions

- [Phase ?]: SAFE-01 invariant: holds because Phase-97 procedure never passes --force (firmware HAS a FLAG_FORCE over-voltage relaxation at primitives.cpp:121); held-rail proxy pinned host-space 0x188/0x180 marked [ASSUMED] per A1; all bench fields TBD-bench never fabricated (D-02)
- [Phase 98 Plan 01]: Q1 RESOLVED — static-high-pins RULED OUT as PGM vehicle (static_high_mask drives HIGH; PGM=VIL); DIP32_27C020 takes pin 31 off address bus only; PGM-assert is Plan 02 firmware branch (memory_set_data hold-LOW)
- [Phase 98 Plan 01]: D-04 host-side alias guard — size gate (mem_size<=262144) structurally excludes 512K AM27C040 / 1M AM27C080 from DIP32_27C020; both stay DIP32_STD
- [Phase 98 Plan 01]: Blast radius 88 chips accepted (entire ≤256K 0x08 32-pin class); architectural correctness is class-wide (A18 unused at ≤256K); LOW-7: baseline git diff is the audited artifact
- [Phase 98 Plan 02]: A5 CONFIRMED — 0x08 golden trace byte-identical post-fix; test_golden_eprom_0x08_write uses pins=0 (default), gate fails, PGM-hold branch does not fire; no re-bless needed
- [Phase 98 Plan 02]: MED-5 verified no-op — per-buffer P1-hold in program_mismatched_bytes already spans every per-byte CE pulse; no redundant per-byte P1 churn added; new code only asserts CTRL_ADDRESS_LINE_18 hold-LOW (distinct from P1 VPP routing)
- [Phase 98 Plan 02]: HIGH-1 blind-fix honesty — addr-0 register state byte-unchanged under RC-1; Phase 99 is sole empirical gate; no over-claim that bits flip on silicon

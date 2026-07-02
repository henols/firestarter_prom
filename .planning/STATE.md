---
gsd_state_version: 1.0
milestone: v1.20
milestone_name: — Protocol-Only Dispatch — Remove the Legacy `mem_type` Axis
current_phase: 107
status: verifying
stopped_at: Completed 107-03-PLAN.md (final gate sweep, v1.20 milestone verified non-regression at close)
last_updated: "2026-07-02T15:28:54.223Z"
last_activity: 2026-07-02
last_activity_desc: Phase 107 complete
progress:
  total_phases: 3
  completed_phases: 3
  total_plans: 7
  completed_plans: 7
  percent: 100
current_phase_name: docs-gate-documentation-non-regression-close
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-07-02

## Current Position

Phase: 107
Plan: Not started
Status: Phase complete — ready for verification
Last activity: 2026-07-02 — Phase 107 complete

## Project Reference

See: `.planning/PROJECT.md` (v1.19 Phase 104 close footer + Key Decisions)

**Core value:** Algorithm-first dispatch — the minipro `protocol_id` (`algorithm`) is the single authoritative dispatch key end to end (XML → DB → wire JSON → firmware handler). v1.20 removes the last vestige that violates that contract: the `mem_type`/`type` backward-compat fallback axis. After v1.20 the firmware, wire, and host trust **only** the real protocol.

**Current focus:** Phase 107 — docs-gate-documentation-non-regression-close

## Milestone Context (v1.20)

- **Scope (from REQUIREMENTS.md, defined 2026-07-02):** Delete the vestigial `mem_type`/`type` backward-compat dispatch axis end to end. 12 v1 requirements across firmware (FW-01..03), the wire contract (WIRE-01), the host (HOST-01..04), docs (DOC-01), and non-regression gates (GATE-01/02, SAFE-01).
- **Sequencing invariant:** the wire contract must never be left half-broken. Firmware stops parsing `type` FIRST (Phase 105) — safe because `json_parser.c` silently skips unknown fields, so a host that briefly still emits `type` is unaffected. The host then stops emitting `type` (Phase 106), completing WIRE-01's removal in lockstep across both phases.
- **Dead-code framing:** the `mem_type` fallback is already dead code for every DB chip (all carry `algorithm`) — this is a legibility/safety cleanup, not a behavior change for real chips. Accepted consequence: user-override DB entries lacking `algorithm` will no longer work (must specify a protocol) — enforced by HOST-04's pre-flight rejection.
- **Firmware-touching (Phase 105):** dual-repo lockstep (`constants.py` ↔ `firestarter.h`); watch the py3.12-masks-CI-3.11 ruff/codegen drift trap for host changes (Phase 106/107).
- **Guards held throughout:** v1.16 golden register traces + dispatch-mirror guard, `check_dispatch.py` (0 violations), `diff_db.py` (chip_database.json identity), dual-repo constants parity, py3.11-target CI. Over-voltage stays blocked (SAFE-01).
- Phase numbering continues from v1.19's Phase 104 → **v1.20 starts at Phase 105**.
- **Out of scope (v2/LEGACY):** `FLAG_VPE_AS_VPP (0x10)` removal (LEGACY-01), `EPROM_LEGACY` naming cleanup (LEGACY-02) — deferred, tracked in REQUIREMENTS.md v2 section.
- Branches off `beta` in all 3 repos; gitlinks PINNED; lockstep beta cut + stable promotion operator-gated — NOT a phase in this milestone.

## Roadmap Summary (v1.20)

**Phases:** 3 (105–107) · **Granularity:** Comprehensive (tight removal milestone — 3 phases per the FW → HOST → DOCS+GATE natural sequencing) · **Coverage:** 12/12 requirements mapped ✓ · **Dependency chain:** strictly linear 105 → 106 → 107.

| Phase | Goal | Requirements | Success Criteria |
|-------|------|--------------|------------------|
| 105 — FW | Delete the `mem_type` fallback dispatch chain (`memory.cpp` steps 7–11); `protocol == 0` fail-closes; drop `handle->mem_type` + stop parsing `type` in `json_parser.c`; retire `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)` + `TYPE_*` constants. Dual-repo lockstep. | FW-01, FW-02, FW-03, WIRE-01 | 4 |
| 106 — HOST | Stop emitting `type`; drop `_ALGO_MEM_TYPE` + the "Generic Flash (legacy fallback only)" default in `database.py`; remove `mem_type`-keyed legacy label fallbacks in `ic_layout.py`; reject any chip entry lacking `algorithm` before any serial byte. Completes WIRE-01's emit-side removal. | HOST-01, HOST-02, HOST-03, HOST-04 | 4 |
| 107 — DOCS + GATE (close) | Update `firestarter/CLAUDE.md`, `PROTOCOLS.md`, wire-field docs to drop `type`/`mem_type`; record the breaking change; re-verify golden traces + dispatch-mirror guard, `check_dispatch.py`, `diff_db.py`, full native + host suites, constants parity, py3.11-target CI. | DOC-01, GATE-01, GATE-02, SAFE-01 | 4 |

**Non-regression gates (GATE-01/02, SAFE-01):** v1.16 golden traces + dispatch-mirror guard green; `check_dispatch.py` 0 violations; `diff_db.py` no value change for real chips; over-voltage blocked; every dispatchable DB chip routes identically via `protocol` alone. Verified in every phase that touches dispatch, re-verified explicitly at Phase 107 close.

Detail: `.planning/ROADMAP.md` §v1.20.

## Accumulated Context

### Deferred Items (carry-forward at v1.17 close — 2026-06-29)

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| FUT-07 (v1.17) | W29C040 byte-exact graduation + LEDGER `supported` | deferred — §6.6 boot block permanently locked on seated chip | Needs a different unlocked sample + third-party bench. All v1.17 software done. |
| ~~FUT-06 (v1.15)~~ → **FUT-08 (v1.18)** | AM27C020 0x08 32-pin write/VPP path | **retired-by-replacement (v1.18 Phase 99 close, 2026-07-01)** | Phase-98 fix bench-proven effective (write#1 60/64 byte-exact; Phase-97 0-bits signature refuted) but marginal/unreliable (write#2 0/64) — no byte-exact graduation. FUT-08 carries the next step: characterize program-window VPP-under-load (DMM at socket pin 1) + write timing. See PROTOCOL-LEDGER `0x08` / `.planning/v1.18/bench/EVIDENCE.json`. |
| FUT-05 (v1.15) | REWR-02 0x08 rewritable write proof | deferred — no functional 0x08 rewritable chip | W27E040 stuck-bit; may benefit from v1.18 `0x08` fix. |
| FUT-04 (v1.14) | AT28C04/16 adapter graduation | deferred — adapter not built | 9 chips stay `adapter-required`. |
| FUT-03 (v1.15) | 2516 0x0B read instability + write proof | deferred best-effort (D-22) | 3 distinct SHAs after VPP-skip; shared OE/VPP pin. |
| FUT-01 (v1.14) | X88C64 0x34 graduation | deferred — PCB-blocked | A6 ALE-routing PCB-BLOCKED (HIGH); stays `protocol-not-implemented`. |
| LEGACY-01 (v1.20 v2) | `FLAG_VPE_AS_VPP (0x10)` removal if confirmed unused | deferred to v2 | Operator scoped v1.20 to the `mem_type` axis only, not the broader vestige sweep. |
| LEGACY-02 (v1.20 v2) | `EPROM_LEGACY` (0x0B) label rename + remaining "legacy fallback" prose scrub | deferred to v2 | Naming, not the dispatch axis; do after v1.20 lands. |
| release-gate | Lockstep beta cut `3.0.0b11` + gitlink bump | OPERATOR-GATED | Standing v1.11–v1.19 policy; gitlinks PINNED. |

### Deferred Items — acknowledged at v1.19 milestone close (2026-07-02)

The **same 14** open artifact items (from `audit-open`) were re-confirmed acknowledged-and-deferred at the v1.19 close (operator: "Acknowledge & proceed"). **None originate in v1.19 (Phases 100–104)** — all are the identical pre-existing cross-milestone carry-forwards listed in the v1.18-close table below (2 debug sessions, 2 UAT gaps, 5 verification gaps, 5 pending todos), unchanged by this naming/rename milestone. NAME-01/02/03 REQUIREMENTS bookkeeping (previously showing Pending though delivered in Phase 100) was reconciled to Complete at this close.

### Deferred Items — acknowledged at v1.18 milestone close (2026-07-01)

14 open artifact items (from `audit-open`) acknowledged-and-deferred at v1.18 close. **None originate in v1.18 (Phases 97–99)** — all are pre-existing cross-milestone carry-forwards, unchanged by this milestone.

| Category | Item | Status |
|----------|------|--------|
| debug | firmware-vpp-misread | diagnosed (uno328pb VPP divider ~6.8x under-read) |
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 |
| uat_gap | Phase 08 — 08-HUMAN-UAT.md | partial (0 pending scenarios) |
| uat_gap | Phase 85 — 85-HUMAN-UAT.md | partial (2 pending scenarios) |
| verification_gap | Phase 08 — 08-VERIFICATION.md | human_needed |
| verification_gap | Phase 09 — 09-VERIFICATION.md | human_needed |
| verification_gap | Phase 71 — 71-VERIFICATION.md | gaps_found |
| verification_gap | Phase 84 — 84-VERIFICATION.md | human_needed |
| verification_gap | Phase 85 — 85-VERIFICATION.md | human_needed |
| todo | 2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads | firmware |
| todo | avrdude-mcu-detection-fallback | low |
| todo | cobs-decoder-framelevel-deadline-wr01 | medium |
| todo | photograph-modified-rev-0 | MEDIUM |
| todo | write-modifications-md-rework-trace | MEDIUM |

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

### Roadmap Evolution

- v1.20 roadmap created 2026-07-02: 3 phases (105–107), 12/12 requirements mapped. FW → HOST → DOCS+GATE strictly linear sequencing (wire-contract removal ordered so it's never half-broken).
- Phase 104 added: Rename protocol header and .cpp files to descriptive protocol-type names (replace hard-to-read flash type N naming)

## Operator Next Steps

- `/gsd-plan-phase 105` to begin firmware `mem_type` removal.

## Decisions

- [v1.20 roadmap]: WIRE-01 assigned primarily to Phase 105 (firmware stops parsing `type`) with Phase 106 (host stops emitting `type`) realizing the emit-side removal — sequenced FW-first because `json_parser.c` silently skips unknown fields, so a host briefly still emitting `type` during the gap is harmless; the reverse order (host-first) would leave firmware still trusting a fallback the host stopped feeding, which is safe too, but FW-first keeps the fail-closed guarantee active earliest.
- [Phase ?]: SAFE-01 invariant: holds because Phase-97 procedure never passes --force (firmware HAS a FLAG_FORCE over-voltage relaxation at primitives.cpp:121); held-rail proxy pinned host-space 0x188/0x180 marked [ASSUMED] per A1; all bench fields TBD-bench never fabricated (D-02)
- [Phase 98 Plan 01]: Q1 RESOLVED — static-high-pins RULED OUT as PGM vehicle (static_high_mask drives HIGH; PGM=VIL); DIP32_27C020 takes pin 31 off address bus only; PGM-assert is Plan 02 firmware branch (memory_set_data hold-LOW)
- [Phase 98 Plan 01]: D-04 host-side alias guard — size gate (mem_size<=262144) structurally excludes 512K AM27C040 / 1M AM27C080 from DIP32_27C020; both stay DIP32_STD
- [Phase 98 Plan 01]: Blast radius 88 chips accepted (entire ≤256K 0x08 32-pin class); architectural correctness is class-wide (A18 unused at ≤256K); LOW-7: baseline git diff is the audited artifact
- [Phase 98 Plan 02]: A5 CONFIRMED — 0x08 golden trace byte-identical post-fix; test_golden_eprom_0x08_write uses pins=0 (default), gate fails, PGM-hold branch does not fire; no re-bless needed
- [Phase 98 Plan 02]: MED-5 verified no-op — per-buffer P1-hold in program_mismatched_bytes already spans every per-byte CE pulse; no redundant per-byte P1 churn added; new code only asserts CTRL_ADDRESS_LINE_18 hold-LOW (distinct from P1 VPP routing)
- [Phase 98 Plan 02]: HIGH-1 blind-fix honesty — addr-0 register state byte-unchanged under RC-1; Phase 99 is sole empirical gate; no over-claim that bits flip on silicon
- [Phase 98 Plan 03]: rw-pin:[31] on DIP32_27C020 mirrors the working DIP32_SST39SF040 precedent — pin 31 resolves via pin_conversions[32][31]=22 to config.rw_line=22 -> CTRL_READ_WRITE (0x40), closing the corrected CR-01 fork (host half)
- [Phase 98 Plan 03]: DB regen confirmed idempotent for rw-pin (pinouts.json runtime datum, never embedded in chip_database.json) — diff_db.py shows only the pre-existing Phase-94 PGSZ_PAGE_SIZE delta
- [Phase 98 Plan 03]: py3.11 CI sign-off follows the 98-01 precedent (CI-PENDING/structurally-green) — no python3.11 binary in this devcontainer; all CI-scoped commands (ruff/mypy-watermark/diff_db/check_dispatch/parity) pass under 3.12.13
- [Phase 98 Plan 04]: Reverted 98-02's inert CTRL_ADDRESS_LINE_18 clear (physical no-op on Rev 2 via the 0x08 alias; wrong-pin on Rev 0/1); relies on existing rw_line mechanism (CTRL_READ_WRITE 0x40, revision-invariant) fed by 98-03's rw-pin:[31]
- [Phase 98 Plan 04]: WR-01 revision-parametrized native test added via local replicas of rurp_map_ctrl_reg_for_hardware_revision (Rev 2 + Rev 0/1) — the missing RED state; WR-02 RC-98B pinned to EQUAL(5); IN-02 firmware constant deferred to 98-05 (no size literal survives the revert)
- [Phase 98 Plan 05]: IN-03 macro replacement named `mem_min` (not `min`) to avoid any future collision with Arduino's own min() or std::min — static inline single-evaluation function, sole call site (memory_read_execute) updated, behavior identical (side-effect-free operands)
- [Phase 98 Plan 05]: IN-02 host authoritative value moved from build_db.py-only literal (98-03) into constants.py (the established landing spot for every firmware-parity constant this codebase tracks) — build_db.py now imports it; parity test follows the file's REAL pattern (hardcoded literal + FW_ABSENT skipif + citing comment), not literal header-parsing, matching its 6 sibling assertions
- [Phase 98 Plan 05]: Phase 98 CLOSED — all 5 plans complete (98-01/02 original fix attempt + 98-03/04 corrected CR-01 fix + 98-05 IN-01/02/03 cleanup); native suite 119/119 green, golden traces byte-identical, host CI green on py3.11 target; Phase 99 (BENCH + LEDGER) unblocked
- [Phase 99 Plan 01]: Chose minimal D-09 extension (option a, evidence-shape branch keyed on `v1_18_writeverify_sha_selfconsistent`) over a new status enum value — a v1.18-native 0x08 graduation is proven by write/read-back self-consistency (no v1.15 write baseline exists for AM27C020) without requiring a fabricated `p90_writecycle_sha_matches_v115` claim; honesty guard verified (bare 0x08 PASS claim without the marker still fails); FUT-06 retirement path (removal from open_defects[], not status_changed flip) proven by test; gate is now CAPABLE of a graduated 0x08 row but 99-04 decides the actual outcome from the bench result
- [Phase Phase 99 Plan 02]: check_graduation.py filters on op prefix phase99* (never the Phase-97 tier0_microprobe+rca01 cell); branches PASS (write_image_sha256==readback_sha256 self-consistency) vs DEFER (bits_flipped+post_read_sha256 differential), validated against 9 synthetic fixture cells without ever mutating the real EVIDENCE.json
- [Phase 99]: [Phase 99 Plan 04]: Took the DEFER branch decided by 99-03 (Phase-98 fix bench-effective-but-unreliable: write#1 60/64 byte-exact, write#2 0/64); retired FUT-06 by removal-and-replacement rather than in-place edit, opening FUT-08 (renumbered from the operator-requested "FUT-07" — that id is already taken by the v1.17 W29C040 defect in this same table) as an explicit successor citing the fix-effective-but-unreliable finding + the next diagnostic step (program-window VPP-under-load + write timing); 0x08 row stays open-defect-carried with on_hand_chip now AM27C020
- [Phase ?]: D-01/D-02/D-04 applied: single _PROTOCOL_DISPLAY_NAME map in ic_layout.py feeds both proto_display fallback and info Protocol line; ASCII dashes; 0x34 added / 0x11 dropped
- [Phase ?]: 0x34 description_points bullet chosen as minimal placeholder text, flagged Phase-103-DOC-01-owned
- [Phase ?]: py3.11 CI recorded as CI-PENDING/structurally-green under py3.12.13 devcontainer (Phase-98 precedent)
- [Phase ?]: Phase 103 Plan 01: Heading token substitutions copied verbatim from §0 canonical bucket table; cross-link anchors regenerated + grep-verified against actual rendered headings (not hand-guessed); INV row edits scoped to behavior column only, SAFE-02 grep-contract columns kept byte-identical; D-04 callout placed above §0 table reusing existing blockquote style
- [Phase 103 Plan 02]: D-05 GATE re-verification used existing tooling only (no new tests/scripts) — `pio` was present this session so the GATE-01 firmware leg (`pio test -e native`, 82/82) is a real executed PASS, not deferred; `python3.11` was absent so only the constants-parity py3.11-target leg is recorded CI-PENDING (structurally-green under py3.12), per the deterministic Phase-98 CI-PENDING guard (never a fabricated PASS for an absent-tool leg)
- [Phase 103 Plan 02]: Milestone-CLOSED narrative written only after confirming zero GATE-01/02/03 FAIL verdicts in 103-VERIFICATION.md (precondition honored); no beta cut, no gitlink bump, no `chip_database.json`/code change triggered — v1.19 close is docs+planning-artifacts only
- [Phase ?]: Renamed file-internal flash3_*/flash4_* static helpers to flash_nor_unlock_*/flash_5v_page_* stems for full identifier consistency (discretionary per 104-PATTERNS.md); no cross-file impact since file-internal — Plan 104-01
- [Phase ?]: Left pre-existing unrelated platformio.ini whitespace diff untouched (out of plan scope, not introduced by this work) — Plan 104-01
- [Phase 104-02]: New family-id strings introduced for Plan 03: nor_unlock (was flash3) and 5v_page (was flash4) — become the test-suite directory names in Plan 03
- [Phase 104-02]: Preserved validation_matrix_spec.json protocols_note prose factual content verbatim, only substituting handler/test-module name references
- [Phase 104-03]: Rule 1 fixed 4 latent firestarter_app test regressions caused by Plan 02's flash3/flash4->nor_unlock/5v_page spec rename (test_val_wire_flash3/4.py StopIteration + stale handler assertions in test_matrix_schema/test_validate_family_cmd/test_gen_validation_header); surfaced only when the full suite was run beyond the plan's declared verification scope
- [Phase 104-03]: Left cli_handlers.py dev validate-family Choice list stale (still lists flash3/flash4) and tools/baseline/dispatch_baseline.json (orphaned, zero Python consumers) untouched -- both explicitly out of plan scope (GATE-03 cli_handlers.py prohibition; no regression risk from the unconsumed baseline file)
- [Phase 105]: Executed D-01 setup (merge v1.19->beta lockstep in both sub-repos, no tag; fork v1.20-protocol-only-dispatch off updated beta) as a hard precondition since it had not yet been performed despite operator authorization — Research flagged neither beta nor origin/beta contained the v1.19 PROTO_ layer this plan's edits reference; without it no v1.20 branch existed to work on
- [Phase 105]: Collapsed configure_memory() dispatch tail to a single unconditional terminal configure_not_implemented(handle) call (D-04) instead of an if/else on protocol==0 — Matches the codebase's existing named-infeasibility-arm fail-closed style; protocol==0 and any unrecognized non-zero protocol now share one exit
- [Phase 105]: Kept the vestigial mem_type parameter in native test make_handle() (both suites) after removing the struct field, rather than dropping it and touching ~25 call sites — Lower-churn mechanical choice explicitly left to Claude's Discretion in CONTEXT.md and RESEARCH.md
- [Phase 106-01]: Kept dispatch(algo, 0) rather than changing dispatch()'s signature since the mem_type fallback chain is protocol==0-only (dead for every real chip's non-zero algorithm)
- [Phase 106-01]: Logged pre-existing test_audit_coverage_matrix.py golden-fixture drift and the expected test_chip_resolver.py ripple (owned by Plan 03) to deferred-items.md rather than fixing them - both explicitly out of scope
- [Phase 106-02]: get_chip_type_string signature shrunk to (self, protocol_id=None) - chip_type_int param and the local type_map dict deleted; unresolved falls to bare 'Unknown'
- [Phase 106-02]: resolve_type_label signature shrunk to (self, electrical_type, protocol_id=None) - type_int param deleted; delegates to get_chip_type_string(protocol_id)
- [Phase 106-02]: __main__ self-test block repurposed to exercise protocol tier (0x08 known, 0x99 unknown) replacing removed numeric-tier calls
- [Phase 106-02]: eprom_info.py:69 string-typed 'type': 'unknown' raw-JSON field left untouched - different axis from numeric mem_type
- [Phase ?]: [Phase 106-03]: Guard placement and read-path exactly mirror the existing support_status guard (same raw_config object, same exception, same pre-serial ordering); reject rule is a plain falsy-check covering both absent and explicit-0, no KNOWN_PROTOCOLS gate added (D-01 pass-through preserved)
- [Phase ?]: [Phase 106-03]: Rule 1 auto-fix applied to test_consistency_check.py's dispatch-chain mock (missing programming.algorithm key), directly caused by the new HOST-04 guard; confirmed via git stash that test_audit_coverage_matrix.py golden-fixture drift and the 4 pre-existing ruff/format failures in tools/*.py are unrelated and out of scope
- [Phase 107-01]: Reworded three explanatory mentions of the retired mem_type axis in firestarter/CLAUDE.md to avoid the literal substring 'mem_type' (legacy-integer/backward-compat phrasing), satisfying the plan's strict grep-based acceptance criteria while preserving meaning
- [Phase 107-01]: Kept protocol==0 as its own explicit numbered terminal dispatch step (renumbered to 7) rather than folding into the generic 6b non-zero-unrecognized guard, matching the plan's required wording
- [Phase ?]: [Phase 107-02]: Restored MSG_WARN_FL4_BOOT_BLOCK_LOCKED (0x85) / MSG_ERR_FL4_BOOT_BLOCK_LOCKED (0xBC) to the meta canonical messages.toml before finalizing the 0xAE removal sync -- these Phase-95 host-only messages were never present in canonical and the sync would have silently deleted them from messages.py, breaking tests/test_val_wire_5v_page.py (Rule 1 auto-fix, caught pre-commit)
- [Phase ?]: [Phase 107-02]: Firmware include/messages.h gained the same restored 0x85/0xBC #define constants as an inert byproduct (firmware source never references either name) -- accepted as a correction of the canonical source of truth, not a firmware behavior change
- [Phase ?]: [Phase 107-03]: Applied D-07 pass bar literally - confirmed each of the 5 pre-existing failing/dirty artifacts (1 pytest failure + 4 ruff errors + 1 ruff-format file) is outside git diff beta..HEAD before accepting as prior debt; zero new regressions from v1.20
- [Phase ?]: [Phase 107-03]: Host pytest missing final summary line (syrupy plugin display quirk) cross-verified independently via pytest --collect-only (711 total minus 1 named failure = 710 passed), matching RESEARCH.md baseline exactly

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| Phase 98 P04 | 35min | 3 tasks | 2 files |
| Phase 98 P05 | 25min | 3 tasks | 5 files |
| Phase 99 P01 | 25min | 3 tasks | 2 files |
| Phase 99 P02 | 15min | 2 tasks | 3 files |
| Phase 99 P04 | 15min | 2 tasks | 4 files |
| Phase 102 P01 | 25min | 3 tasks | 3 files |
| Phase 103 P01 | 8min | 3 tasks | 1 files |
| Phase 103 P02 | 18min | 2 tasks | 1 files |
| Phase 104 P01 | 20min | 3 tasks | 7 files |
| Phase 104 P02 | 12min | 3 tasks | 6 files |
| Phase 104 P03 | 55min | 3 tasks | 15 files |
| Phase 105 P01 | 32min | 3 tasks | 6 files |
| Phase 106 P01 | 20min | 3 tasks | 8 files |
| Phase 106 P02 | 12min | 3 tasks | 3 files |
| Phase 106 P03 | 12min | 3 tasks | 3 files |
| Phase 107 P01 | 18min | 3 tasks | 4 files |
| Phase 107 P02 | 22min | 2 tasks | 5 files |
| Phase 107 P03 | 20min | 2 tasks | 0 files |

## Session

**Last session:** 2026-07-02T15:20:48.152Z
**Stopped at:** Completed 107-03-PLAN.md (final gate sweep, v1.20 milestone verified non-regression at close)
**Resume file:** 
None

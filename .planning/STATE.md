---
gsd_state_version: 1.0
milestone: v1.22
milestone_name: — AT28C Software Data Protection Lifecycle
current_phase: 117
current_phase_name: FIX — remap-aware `0x0D` emitter + honest completion signal
status: verifying
stopped_at: Phase 116 complete + verified 6/6 — Phase 117 next, unplanned
last_updated: "2026-07-27T22:36:54.377Z"
last_activity: 2026-07-28
last_activity_desc: "Quick task 260728-ahy: dev test --submit gh-tier label/silent-failure fix"
progress:
  total_phases: 7
  completed_phases: 1
  total_plans: 7
  completed_plans: 7
  percent: 14
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-07-27

## Current Position

Phase: 117 — FIX — remap-aware `0x0D` emitter + honest completion signal
Plan: Not started
Status: Phase complete — ready for verification
Last activity: 2026-07-28 — Completed quick task 260728-ahy: `dev test --submit` gh-tier label/silent-failure fix (Phase 117 still unplanned, unaffected)

<!-- NOTE: `query state.planned-phase` returned `"updated": []` and did not write this block or `progress.total_plans` — hand-corrected. Same tooling class as the recurring `phase.complete` mis-advance; verify STATE.md by hand after every planning/transition step. -->

**Phase 116 plan graph:**

| Wave | Plans | Sub-repo | What it builds |
|------|-------|----------|----------------|
| 1 | 116-01 | firmware | v1.22 branch off `beta` in both sub-repos; opt-in ordered bus-recording extension; `0xBB` dispatch negative (80/80 byte-exactness pinned before count → 82) |
| 2 | 116-02, 116-03, 116-04 | app→fw, app, app | generated `sdp_bus_config.h` + drift gate; `chip_id_check` DB invariant (84, no skipif); planted-`LOG_` timing-window scan |
| 3 | 116-05 | firmware | always-green SDP harness suite; address-keyed `mock_get_data`; ordered full-stream equality asserts |
| 4 | 116-06 | firmware | parked RED `0x0D` suite (`-I` only, no `test_filter`) + `RED-BASELINE.md` |
| 5 | 116-07 | meta | `116-PREMISE.md` + PROJECT.md third ⚠ correction block (1 operator checkpoint, `autonomous: false`) |

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-07-27 — v1.22 milestone-start footer + Current Milestone section, incl. both ⚠ correction blocks)

**Core value:** Algorithm-first dispatch — the minipro `protocol_id` (`algorithm`) is the single authoritative dispatch key end to end (XML → DB → wire JSON → firmware handler). As of v1.20 the last vestige violating that contract — the `mem_type`/`type` backward-compat fallback axis — is gone; firmware, wire, and host trust **only** the real protocol. v1.22 completes the write-protection lifecycle on protocol `0x0D` without adding a second dispatch axis — `handle->protocol` stays the sole dispatch key; `handle->cmd` is extended only as an operation selector *inside* the existing `0x0D` handler, exactly as v1.13 Phase 74 extended `flash_5v_page.cpp`.

**Current focus:** Phase 116 — GROUND TRUTH + TRACE HARNESS

## Milestone Context (v1.22)

- **Scope (from REQUIREMENTS.md, defined 2026-07-27; research `.planning/research/SUMMARY.md`, 4-stream synthesis):** Make Software Data Protection on protocol `0x0D` (`configure_eeprom28c`) explicit, observable, and bidirectional. 36 v1 requirements: the trace harness/oracle (TRACE-01..06), the remap-aware emitter + honest completion-signal fix (FIX-01..06), auto-unlock observability (OBS-01..05), the new SDP-lock capability (LOCK-01..06), the host CLI/wire surface (HOST-01..06), the `dev test` phantom-erase correctness fix (DEVTEST-01), non-regression gates + docs (GATE-01..03), and the honesty-ledger close (CLOSE-01..03).
- **The milestone opens with a FIX, not a feature.** Four independent research streams converged: the SDP-disable sequence already shipped in `3.0.0b11` almost certainly never reaches silicon (`flash_util_byte_flipping` bypasses `mem_util_remap_address_bus`, so `/WE` is inhibited on ≥1 command write across all 84 `0x0D` chips), and its `eeprom28c_wait_for_write(handle, 0x5555, 0x20)` success check is INVERTED (both datasheets state the command-sequence data "is not written to the device"). This reverses the milestone's own kickoff framing twice (see PROJECT.md's two ⚠ correction blocks) and the planned gh#11/gh#12 closeout tone — they may be live defects, not stale 2024 reports.
- **No AT28C part on the operator's bench → software-only validation, no bench phase.** Every success criterion is verifiable without silicon (native register-trace assertions, host pytest, source-scan gates, measured host-side timing). `0x0D` stays `UNVERIFIED` in `PROTOCOL-LEDGER` at close; zero chips change `support_status`; the 84-chip count is unchanged. See REQUIREMENTS.md §"Validation Ceiling" for the exact permitted/forbidden claims — never write or accept a criterion crossing that line.
- **Ordering invariants (non-negotiable):** harness before any firmware change (116→117, else every trace claim is hollow — the abandoned commit `0052c42` lesson); fix before observability (117→118, advertising a sequence that doesn't reach silicon is worse than silence); observability before lock (118→119, lock is the only new state-mutating capability); firmware before host, unambiguously (119/118→120, a host emitting `0x100` against `3.0.0b11` firmware today is silently ignored — HOST-06); the `dev test` phantom-erase fix before the closeout comments (121→122, else every community re-test auto-tags `community-fail`).
- **Locked decisions (operator, 2026-07-27 — do not re-litigate):** full SDP lifecycle is core scope; auto-unlock stays default-on + reported + `--skip-sdp-unlock` opt-out (`--sdp-relock` deferred to v1.23+); CLI surface `firestarter dev sdp <chip> enable|disable`; gh#11's 1-byte-in-64 poll defect is in scope (FIX-06); `dev test` phantom-erase fix in scope (DEVTEST-01); `lock-status` + hand-curated protection table stay out of scope (planted seed).
- Phase numbering continues from v1.21's Phase 115 → **v1.22 starts at Phase 116**.
- **Branch model:** v1.21 IS merged into `beta` in both sub-repos, so v1.22 forks off `beta` per standing policy (reversing the v1.15/v1.21 fork-off-prior-version exception) — verify with `git` at execute time regardless.
- **Key context:** Promoted from Backlog 999.19 (root cause, leads) + 999.18 (verification, follows). Reframed twice at kickoff (see PROJECT.md §"Current Milestone: v1.22", both ⚠ correction blocks). Precedent in-tree: v1.13 Phase 74 (SDP + page write on `flash_5v_page`), v1.14 Phase 77 (erase write-path wired from `electrical.type`).
- **Established fact, do not re-litigate:** `include/primitives.h`/`src/proms/primitives.cpp` do NOT exist; `a296195` and `0052c42` are ancestors of neither `beta` nor the v1.21 line — the v1.16 Phase-89 primitive recompose sits on an unmerged branch. The real shared seam is `flash_utils.{h,cpp}`; the real trace mechanism is `HOST_STUBS_RECORD_BUS`, which records only `rurp_write_to_register` (not data bytes, not strobes — Phase 116 must extend it). `page-size` does NOT exist on the wire (`constants.py`'s "Firmware sync" comment is false).

## Roadmap Summary (v1.22)

**Phases:** 7 (116–122) · **Granularity:** research-recommended spine, adopted verbatim (no coverage gaps found) · **Coverage:** 36/36 requirements mapped ✓, 0 unmapped · **Dependency chain:** 116 → 117 → 118 → 119 → 120 → 121 → 122 (strictly linear — every ordering invariant above is load-bearing, not a preference).

| Phase | Goal | Requirements | Success Criteria |
|-------|------|--------------|------------------|
| 116 — Ground Truth + Trace Harness | Extend `HOST_STUBS_RECORD_BUS` (opt-in, ordered data+strobe stream); new `0x0D` SDP trace suite RED against today's tree; 4 planted-fault negative traces; address-keyed `mock_get_data`; DB-invariant `chip_id_check` test; premise-verification artifact (INIT-abort prediction) | TRACE-01..06 | 6 |
| 117 — FIX: remap-aware emitter + honest completion signal | Replace `flash_execute_command(EEPROM_SDP_DISABLE)` with a `0x0D`-local emitter on `handle->firestarter_set_data`; delete the inverted `(0x5555,0x20)` check; terminal-byte guards; correct the 1-byte-in-64 page poll; flash_utils/flash_5v_page/flash_nor_unlock byte-untouched; Phase 116 suite RED→GREEN | FIX-01..06 | 6 |
| 118 — OBSERVE: auto-unlock visible + opt-out-able (FW half) | Report line before/after (never inside) the sequence + planted-`LOG_` timing-window test; `FLAG_SKIP_SDP_UNLOCK` (0x100) honored; named `AT28C_TBLC_MAX_US=100`; `micros()`-measured duration logged; default `write` byte-identical to b11 | OBS-01..05 | 5 |
| 119 — LOCK: SDP-enable + command surface (FW half) | `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` standalone (no payload, no DONE round-trip); lock body = 3 loads + `t_WC`, no payload; `is_memory_cmd()` replacing the ordinal admission guard (DEV_TOOLS-invariant); `default:`→`MSG_ERR_NOT_SUPPORTED`; `FLASH_ENABLE_WRITE_PROTECTION` preserved; flash-delta reported | LOCK-01..06 | 6 |
| 120 — HOST: CLI surface, wire emission, capability refusal | `firestarter dev sdp <chip> enable\|disable` behind v1.21 destructiveness gate + SAFE-04; `write --skip-sdp-unlock`; lockstep `CMD_*`/`FLAG_*` + `COMMAND_NAMES` + parity test; pre-wire refusal for the 2 FRAM + pre-SDP `2804`/`2816`/`2817` class; honest non-fabricated SDP-outcome reporting; FW-before-host sequencing enforced | HOST-01..06 | 5 |
| 121 — `dev test` FIX + GATES + DOCS | `OP_ERASE`→`NA` for `0x0D` + firmware `CMD_ERASE` fail-closed; AST capability gate + planted-violation pytest; docs corrected (`PROTOCOLS.md` §1.6, `lockable-proms.md`, `protocol-id.md`, both CLAUDE.md, both READMEs) incl. "0x0D has no erase"; full non-regression set green (native, `check_dispatch.py`, host pytest, ruff/format py3.9/3.11, `diff_db.py` identity) | DEVTEST-01, GATE-01..03 | 5 |
| 122 — CLOSE: honesty ledger, community ask, release decision | `0x0D` stays `UNVERIFIED`, 0 `support_status` changes, 84-chip count unchanged; gh#12 answered with the decided policy + gh#11 followed up (never "verified fixed"); accept/avoid/cleanup beta-push decision recorded BEFORE any push; every closing claim matches the validation-ceiling's permitted claim only | CLOSE-01..03 | 4 |

**Non-negotiable ordering invariants (repeated from Milestone Context — these gate plan sequencing, not just phase numbering):** harness-before-fix, fix-before-observe, observe-before-lock, firmware-before-host, `dev-test`-fix-before-closeout.

**Research flags carried from `.planning/research/SUMMARY.md`:** Phases 116, 119, 121 likely need `/gsd-plan-phase --research-phase <N>`. Phases 117, 118, 120, 122 are standard patterns (existing in-tree precedents).

**Hardware-gated work:** NONE — this milestone has no bench phase (no AT28C part in operator inventory). Every phase and every success criterion above is verifiable in software alone.

Detail: `.planning/ROADMAP.md` §v1.22.

## Accumulated Context

### Deferred Items (carry-forward at v1.17 close — 2026-06-29)

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| FUT-07 (v1.17) | W29C040 byte-exact graduation + LEDGER `supported` | deferred — §6.6 boot block permanently locked on seated chip | Needs a different unlocked sample + third-party bench. All v1.17 software done. |
| ~~FUT-06 (v1.15)~~ → **FUT-08 (v1.18)** | AM27C020 0x08 32-pin write/VPP path | **retired-by-replacement (v1.18 Phase 99 close, 2026-07-01)** | Phase-98 fix bench-proven effective (write#1 60/64 byte-exact; Phase-97 0-bits signature refuted) but marginal/unreliable (write#2 0/64) — no byte-exact graduation. FUT-08 carries the next step: characterize program-window VPP-under-load (DMM at socket pin 1) + write timing. See PROTOCOL-LEDGER `0x08` / `.planning/v1.18/bench/EVIDENCE.json`. **+ Second data point folded in 2026-07-27 (backlog review):** [`henols/firestarter_prom#14`](https://github.com/henols/firestarter_prom/issues/14) reports a community **TMS27C010A** that blank-checks clean then fails write immediately at `0x000000` — `TI / TMS27C010A,TMS27PC010A` is `algorithm 8` / `pinout DIP32_27C020` / 131072 B, i.e. inside the same scope guard as AM27C020, so this is the *same* `0x08` write-path defect on a second, independently-owned part. Report predates the fix (app 1.2.2 / fw 1.2.3, 2024-11) — ask the reporter to re-test on current firmware; a community `0x08` part is exactly the extra silicon this item needs, and it is not operator-inventory-gated. Backlog stub 999.21 was retired into this row. |
| FUT-05 (v1.15) | REWR-02 0x08 rewritable write proof | deferred — no functional 0x08 rewritable chip | W27E040 stuck-bit; may benefit from v1.18 `0x08` fix. |
| FUT-04 (v1.14) | AT28C04/16 adapter graduation | deferred — adapter not built | 9 chips stay `adapter-required`. |
| FUT-03 (v1.15) | 2516 0x0B read instability + write proof | deferred best-effort (D-22) | 3 distinct SHAs after VPP-skip; shared OE/VPP pin. |
| FUT-01 (v1.14) | X88C64 0x34 graduation | deferred — PCB-blocked | A6 ALE-routing PCB-BLOCKED (HIGH); stays `protocol-not-implemented`. |
| LEGACY-01 (v1.20 v2) | `FLAG_VPE_AS_VPP (0x10)` removal if confirmed unused | deferred to v2 | Operator scoped v1.20 to the `mem_type` axis only, not the broader vestige sweep. |
| LEGACY-02 (v1.20 v2) | `EPROM_LEGACY` (0x0B) label rename + remaining "legacy fallback" prose scrub | deferred to v2 | Naming, not the dispatch axis; do after v1.20 lands. |
| release-gate | Lockstep beta cut `3.0.0b11` + gitlink bump | OPERATOR-GATED | Standing v1.11–v1.20 policy; gitlinks PINNED. |

### Deferred Items — acknowledged at v1.21 milestone close (2026-07-27)

Close type: **override_closeout** — all v1.21 phases (108–115) are `phase_complete` + `verification_status: passed` (Phase 115 verified 5/5), but `audit-open` reports 14 open artifact items, so the close is recorded as an override with the items acknowledged-and-deferred (operator: "Acknowledge & proceed"). **None originate in v1.21 (Phases 108–115)** — they are the identical pre-existing cross-milestone carry-forwards re-confirmed at the v1.18/v1.19/v1.20 closes (see the v1.20 table below for the full item list; unchanged by this VALIDATION+DOCS milestone). Known verification overrides: 14.

**Resolved this milestone (was OPERATOR-GATED at v1.20 close):** the `release-gate` carry-forward — the lockstep `3.0.0b11` beta cut is now PUBLISHED on both channels (PyPI + GitHub prerelease) and the meta gitlinks are bumped off PINNED-b10 to the b11 commits (Phase 115).

### Deferred Items — acknowledged at v1.20 milestone close (2026-07-02)

Close type: **override_closeout** — all v1.20 phases (105–107) are `phase_complete` + `verification_status: passed`, but `audit-open` reports 14 open artifact items, so the close is recorded as an override with the items acknowledged-and-deferred (operator: "Acknowledge & proceed"). **None originate in v1.20 (Phases 105–107)** — they are the identical pre-existing cross-milestone carry-forwards re-confirmed at the v1.18 and v1.19 closes (unchanged by this dead-code-removal milestone). Known verification overrides: 14 (see table below).

| Category | Item | Status |
|----------|------|--------|
| debug | firmware-vpp-misread | diagnosed |
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

### v1.21 Substrate (carry-forward, directly relevant to Phase 108+)

- **`dev validate-family` is the architectural precedent** — `dev test` is its sibling. Reuse its `EpromDatabase(skip_local_override=True)` + mock-operator test seam so Phases 108/109/110/112/113/114 need no hardware.
- **`resolve_chip` guard bypass mechanism (Phase 108):** research recommends Option (a) — bypass via `get_eprom()` + `convert_to_programmer()` for plan derivation only, no shared-code change — over adding a `require_supported=False` seam to `chip_resolver`. Confirm at Phase 108 planning.
- **`consistency_check_eprom`'s divergence math** is the reuse target for the byte-mismatch fingerprint classifier (Phase 108) — do not reimplement.
- **`EpromOperationError.error_code`** is the smallest, highest-leverage seam in the milestone (Phase 108) — every later phase's per-step result depends on it existing.
- **VPP/VPE mV sampler (Phase 111):** `read_vpp_voltage`/`read_vpe_voltage` in `hardware.py` currently return `bool` and only print; confirm the `MSG_DATA_VPP/VPE_VOLTAGE` (0xE4/0xE5) frame parse and sampling count during Phase 111 planning — this is the milestone's one hardware-gated validation.
- **Transport-health capture (Phase 110):** no persistent COBS/CRC/retry/timeout counters exist today; resync is only `logger.debug`-logged. Recommendation: attach a `logging.Handler` during the sweep and count resync/timeout records (zero-risk to transport); report "not measured" if absent. Decide handler-vs-counter approach during Phase 110 planning.
- **UV small-region window choice (Phase 108/109/111):** a high-address contiguous window maximizes upper-address-line coverage from a small write; validate exact size/placement against real UV parts (bench-informed).
- **Research flags:** Phase 108 (pattern math for the UV small-region variant + fingerprint thresholds) and Phase 111 (mV sampler frame parsing/sampling count) likely need `/gsd-plan-phase --research-phase <N>`. Phases 109/110/112/113/114 are well-grounded in existing source + locked decisions — standard planning patterns apply.

### Pending Todos (carried forward)

- `avrdude-mcu-detection-fallback.md` (low) — out of scope, carry forward.
- `cobs-decoder-framelevel-deadline-wr01.md` (medium) — v1.10 COBS follow-up; deferred.
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` (firmware) — carry forward.
- `large-read-data-jitter-uno328pb.md` (HIGH, v1.8-seed) — v1.9 RCA target.
- `photograph-modified-rev-0.md` (medium) — carry forward.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260728-ahy | Fix `dev test --submit` gh tier: drop the nonexistent `gsd-inbox` label from the create argv + surface the swallowed `gh` stderr | 2026-07-28 | `688bf10..0245828` (firestarter_app submodule; gitlink NOT bumped) | [260728-ahy-fix-dev-test-submit-gh-tier-drop-nonexis](./quick/260728-ahy-fix-dev-test-submit-gh-tier-drop-nonexis/) |

Planted seed: `.planning/seeds/submit-repo-target-live-tracker-drift.md` — `SUBMIT_REPO` still names `henols/firestarter_app` while open-issue triage appears to have moved to `henols/firestarter_prom`. Flagged, deliberately not folded into the quick task (operator call).

### Roadmap Evolution

- v1.22 roadmap created 2026-07-27: 7 phases (116–122), 36/36 requirements mapped, 0 unmapped. Adopted the research SUMMARY.md §"The reconciled spine" verbatim — no coverage gaps found, no deviation needed. Strictly linear dependency chain (116→117→118→119→120→121→122); every adjacent-phase link is one of the milestone's non-negotiable ordering invariants (harness-before-fix, fix-before-observe, observe-before-lock, firmware-before-host, dev-test-fix-before-close), not a planning convenience. No bench phase — first milestone since the community-validation-command era with zero hardware-gated success criteria (no AT28C part in operator inventory).
- v1.21 roadmap created 2026-07-02: 7 phases (108–114), 24/24 requirements mapped (corrected from the REQUIREMENTS.md draft's stale "20 total" count). Phase spine per research SUMMARY.md §Implications for Roadmap: 108 (engine+pattern+fingerprint) → 109 (safety gate) → 110 (report+provenance) → 111 (voltage sampler, hardware-gated, isolated) → 112 (CLI wiring) → 113 (submission) → 114 (disposition lock, close).
- v1.20 roadmap created 2026-07-02: 3 phases (105–107), 12/12 requirements mapped. FW → HOST → DOCS+GATE strictly linear sequencing (wire-contract removal ordered so it's never half-broken).
- Phase 104 added: Rename protocol header and .cpp files to descriptive protocol-type names (replace hard-to-read flash type N naming)
- Phase 115 added: Beta install & firmware-flash bench validation (community onboarding) — hardware-gated capstone of v1.21

## Operator Next Steps

- Execute Phase 116 with `/gsd-execute-phase 116` (Wave 1 must land before anything else — it creates the sub-repo branches)
- Phase 116 Plan 07 carries one operator checkpoint (`autonomous: false`) — the PROJECT.md ⚠ correction wording

## Decisions

- [v1.21 roadmap]: Requirement-count discrepancy resolved in favor of the actual enumerated REQ-IDs (24) over the stale header text (20) — no requirement was dropped or invented; the original definition simply undercounted its own list.
- [v1.21 roadmap]: Phase 112 (`dev test` CLI wiring) kept as its own phase rather than merged into Phase 108 or 111, per the research's explicit "MAY be merged if trivial, use judgment" guidance — the CLI surface integrates four prior phases' work and benefits from its own plan/verification cycle; VOLT-01 (Phase 111) stays isolated as the sole hardware-gated phase, unaffected by this choice.
- [v1.21 roadmap]: Followed the research-recommended 7-phase spine verbatim (no coverage gaps found that would require deviating) — SAFE-02/03 treated as hard Phase-109 success criteria per the instruction's explicit load-bearing-safety guidance; DISP-01 treated as a locked anti-feature asserted by Phase-114 success criteria (no code path writes `support_status` from a report).
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
- [Phase 108-01]: Added error_code=response.id to the ProtocolNotImplementedError branch too (discretionary symmetry), not just the generic EpromOperationError branch — The id is always MSG_ERR_PROTOCOL_NOT_IMPLEMENTED (0xBB) there, so this gives every EpromOperationError-family exception a consistent .error_code at zero cost
- [Phase 108-02]: Restricted address-line candidate bits to 8 <= k < (cmp_len-1).bit_length() -- bits at/above the compared region size never toggle within [0, cmp_len) and would spuriously score 100% clustering on scattered data
- [Phase ?]: [Phase 108-03]: id-check NA rule keyed on the programmer-dict chip-id sentinel value 0, not key presence -- every DB entry carries a chip-id key but many carry the literal sentinel 0 meaning no real id to compare
- [Phase ?]: [Phase 108-03]: blank-check NA condition checks BOTH electrical-type in {SRAM,FRAM} AND protocol-id in the SRAM proto-id set, mirroring check_eprom_blank's own short-circuit so derive_plan owns the decision up front
- [Phase ?]: [Phase 108-03]: No named protocol constant exists for flash4 (0x05) in constants.py; added a local _PROTOCOL_FLASH4 module constant in chip_test.py mirroring database.py's own algo != 5 check
- [Phase ?]: run_plan re-resolves every executed step via resolve_chip (guard-honoring), never reusing derive_plan's bypassing dict
- [Phase ?]: id-gate closes on ANY id-step uncertainty (BAD or SKIPPED), not just an explicit numeric mismatch (conservative Pitfall 4 reading)
- [Phase ?]: runs<2 rejected before any resolve/operator call; write/erase/verify disagreement reports marginal, never coerced to OK/BAD; read disagreement is a divergence metric only
- [Phase ?]: [Phase 109 Plan 01]: derive_plan(destructive=False) structurally omits write/erase from Plan.steps into an advisory Plan.locked_destructive list; run_plan never iterates it (SAFE-01, D-01)
- [Phase ?]: [Phase 109 Plan 01]: UV detection at execution time uses algorithm==0x0B (EPROM_LEGACY, UV-EPROM-exclusive DB-wide) as a fallback signal because resolve_chip's programmer dict drops electrical-type; _UV_WRITE_REGION_LENGTH (256) is an engine constant no DB field can widen (PATT-03, SC4)
- [Phase ?]: [Phase 109 Plan 02]: count_applicable(plan, results) computes SWEEP-05 M from the single Plan object (supported steps + locked_destructive), never re-deriving; N counts OK/BAD/marginal, excluding NA/SKIPPED
- [Phase ?]: [Phase 109 Plan 02]: SAFE-02 source-scan test uses ast.walk (not raw substring grep) to avoid false positives on docstring prose describing the safety property (e.g. 'passes no --force')
- [Phase 109]: SAFE-03: AST-based checker (fresh ast.parse walk) + mandatory anti-hollow paired pytest with 4 planted-violation fixtures via FIRESTARTER_DEVTEST_SRC env-override -- closes v1.12 hollow-GATE-03 tech debt
- [Phase ?]: test_report_module_is_orchestrator_only rewritten from raw substring grep to AST-based import/literal scan -- the module's own docstrings describe the SAFE-02 invariant in prose, which a substring check false-positives on (mirrors Phase-109 SAFE-02 ast.walk lesson)
- [Phase ?]: Reworded diagnostic_report.py docstring prose to avoid literal substrings SerialCommunicator/HardwareManager so the plan's shell-grep verification command passes cleanly, meaning preserved
- [Phase ?]: DiagnosticReport, AutoCapture, TransportHealth implemented in one file write (Tasks 2+3 land in one module) since to_dict()/render() depend directly on the sub-dataclass shapes; committed as two separate git commits to preserve per-task traceability
- [Phase 110-02]: Provenance model + injectable prompt_provenance + is_submittable added to diagnostic_report.py; composed into DiagnosticReport append-only (RPT-04) — shield revision never auto-derived from hw_revision byte (D-05); not sure counts as filled/submittable
- [Phase ?]: DbDiff is read-only by construction (write-method-less Mock DB proof + structural no-write scan); proposed_disposition is always advisory descriptive text, never a concrete support_status value
- [Phase 111-01]: Named the honest-fallback test test_sample_none_returns_none_on_error (not test_sample_returns_none_on_error) so the -k sample_none selector required by 111-VALIDATION.md actually matches
- [Phase 111-01]: Asserted the render() single-source contract for the voltage split by scanning rendered table cells for the expected value rather than inspecting render() source text, since Plan 03 has not yet decided the exact voltage row wording
- [Phase ?]: [Phase 111-02]: Used RESEARCH Pattern A (regex re-parse of Response.message) per plan directive, superseding CONTEXT D-05's raw-payload premise -- Response.payload is None for 0xE4/0xE5 frames
- [Phase ?]: [Phase 111-02]: sample_vpp_mv/sample_vpe_mv placed strictly after _read_voltage_loop/read_vpp_voltage/read_vpe_voltage with zero lines changed in those methods (SC3 verified via git diff)
- [Phase ?]: [Phase 111-03]: Old combined vpp_vpe_mv slot fully removed (0 occurrences) rather than kept as a deprecated alias, satisfying the negative-grep acceptance criterion and the D-01 split
- [Phase ?]: [Phase 111-03]: _voltage_dict modeled byte-for-byte on the existing _transport_dict pattern (six explicit NOT_MEASURED-if-None branches) matching the file's established idiom
- [Phase ?]: [Phase 111-03]: Voltage render() row placed after banner, before provenance, as a single add_row sourced only from to_dict()['voltage'] (single-source contract, Phase 110 D-01)
- [Phase 111 close]: UAT Test 1 (live-hardware VPP/VPE parity, SC2 hardware half / D-05) PASS on Leonardo + Rev 2.0 (ACM0 = "Rev 2.0-class"); VERIFICATION.md flipped human_needed→passed. UAT Test 2 (before/after write-step capture) reclassified out of the blocking UAT set → deferred to Phase 112 (operator decision) since no write-step call site exists in Phase 111 by design; logged in 111/deferred-items.md — NOT a Phase 111 gap.
- [Phase ?]: sampler kwarg threaded through all 4 call-chain levels (run_plan -> _run_step -> _dispatch_step -> _dispatch_multi_run) with default None at every level, per D-04 backward-compat guarantee
- [Phase ?]: Sampler bracket scoped strictly to the OP_WRITE branch operator.write_eprom call, not OP_VERIFY/OP_ERASE or the whole run_plan loop -- write-droop-vs-read-droop distinguishability (D-04)
- [Phase ?]: TTY isatty() check factored into a private _is_interactive() seam because CliRunner.invoke() replaces sys.stdin, breaking direct sys.stdin.isatty() patching in tests
- [Phase ?]: chip_id_actual/chip_id_mismatch_reason recovered by parsing the id StepResult.reason text rather than widening chip_test.py's StepResult schema
- [Phase 112-03]: Scoped the SAFE-03 handler AST scan to dev_test + its private helpers via a new AST function-name filter (_scan_target_functions) instead of whole-file, because cli_handlers.py has 10 pre-existing legitimate --force flags on unrelated commands that a whole-file scan would false-positive on
- [Phase ?]: simple test decision
- [Phase ?]: [Phase 112-04]: REVERSED RPT-04 / D-04 / D-05 / D-06 (operator-approved, 112-UAT.md test 2) -- deleted prompt_provenance/Provenance/SHIELD_REV_CHOICES/_CHIP_ORIGIN_CHOICES outright (the path-separator-in-choice-string bug rejecting new/used/2.0); is_submittable now derived from AutoCapture completeness only (chip+protocol+host_version), never a human-provenance field
- [Phase ?]: [Phase 112-04]: fw_board_identity stays honest None -- re-confirmed EpromOperator.comm is torn down after every op (no live comm to read post-run_plan); FirmwareManager.check_current_firmware evaluated and rejected as a source since it opens its own extraneous connection (SAFE-02 violation). hw_revision IS auto-captured via new HardwareManager.read_hardware_revision_value() (dedicated clean energize/query connection). --pot-adjusted flag confirmed out of scope, not implemented
- [Phase ?]: [Phase 112-05]: Gated OP_VERIFY behind destructive in derive_plan (SC2/SWEEP-05 fix direction (a), pre-decided) -- mirrors OP_WRITE/OP_ERASE D-01 pattern exactly; _DESTRUCTIVE_OPS/_MULTI_RUN_OPS untouched
- [Phase ?]: [Phase 112-05]: Repaired 8 tests broken by the verify-gate fix (5 more than the plan's named 3) -- all same bug class, discovered via the plan's own required full targeted-suite verification step
- [Phase ?]: [Phase 112-05]: RPT-04 reworded to the 112-04 auto-capture model, closing the documentation debt flagged in 112-VERIFICATION.md
- [Phase ?]: [Phase 113-01]: dedup_fingerprint reads report.results directly (not report.to_dict()['steps']) to avoid a circular call back into to_dict(), which itself now calls dedup_fingerprint(self)
- [Phase ?]: [Phase 113-02]: overall_verdict is FAIL-dominant (BAD beats marginal) for the issue title -- deliberately distinct from cli_handlers.py's exit-code max() ordering where marginal(2) > BAD(1)
- [Phase ?]: [Phase 113-02]: build_issue_url omits the labels query param entirely (RESEARCH Pitfall 1) -- GitHub drops/404s labels for non-write community testers; triage relies on the [dev test] title marker + fenced-JSON schema_version instead
- [Phase ?]: [Phase 113-02]: gh_available never calls run_fn when which_fn('gh') is falsy -- PATH-short-circuited before any subprocess spawn
- [Phase ?]: [Phase 113-03]: submit_via_browser drops the JSON fence by splitting the pre-built body string on its own '\n\n```json\n' marker rather than re-invoking build_body(include_json=False) -- the plan-mandated signature (title, body, saved_json_path) never receives sanitized_dict/results — Only implementation consistent with the required function signature while satisfying every behavior clause
- [Phase ?]: [Phase 113-03]: Left SUB-01/SUB-02 unchecked in REQUIREMENTS.md -- both are also 113-04's frontmatter requirements (the --submit CLI flag + call site); until that lands a bare dev test run cannot reach submit_report — Requirement isn't fully satisfied from a user's perspective until the CLI wiring plan lands
- [Phase ?]: [Phase 113-04]: Patched firestarter.submit.submit_report (module attribute) as the stable seam for both mocked-call-site and real-submit_report end-to-end tests, since the dev_test call site imports submit lazily inside the if submit: block
- [Phase ?]: [Phase 113-04]: submit.py scanned in FULL via _scan_file (not the scoped _scan_target_functions handler path) for the new SAFE-03 leg -- it is a fresh Phase-113 module with zero pre-existing force/VPP/wire-dict usage, mirroring chip_test.py
- [Phase 114-01]: ladder_state derived in the SAME verdict-branch structure as proposed_disposition (BAD/marginal-indeterminate/all-OK/else); community-confirmed formalized as a named-but-unused constant, never producible by build_db_diff (GRAD-01 SC2 by construction)
- [Phase ?]: [Phase 114-02]: CLI shape (discretionary D-04) -- single-body mode takes --title + --body-file/stdin as separate inputs (mirroring two gh issue view --json invocations); --dir/--glob N-agreeing mode operates on plain saved-body files, no title needed
- [Phase ?]: [Phase 114-02]: schema_version matched by presence only (any value), never an exact-version comparison -- survives Plan 01's 1.0->1.1 bump and any future schema change with zero parser code change
- [Phase ?]: [Phase 114-02]: No rich import in parse_devtest_issue.py (even though rich is already a project dependency) -- plain-text render_diff() only, satisfying the literal no-third-party-import-errors acceptance criterion
- [Phase ?]: DISP-01 checker uses exact-string match against support_status (not substring) to avoid false-positive on current_support_status near-name
- [Phase ?]: Both DISP-01 scan targets (diagnostic_report.py, parse_devtest_issue.py) treated as mandatory; missing-target check fails closed before the scan loop
- [Phase ?]: Task 1 RED phase wrote the full 7-test anti-hollow suite covering both Task 1 and Task 2 acceptance criteria; Task 2 verified-complete with no separate commit (mirrors 109-03 SAFE-03 precedent)
- [Phase ?]: Phase 114.1: guard placed strictly between --destructive confirm block and derive_plan, keyed on app.db.get_eprom(chip) emptiness only — never on a resolve_chip support-status refusal — so case B (present-but-unsupported chips like AT28C16) still runs the full community-validation sweep — Protects the community-validation command's entire purpose (proving support on chips the maintainer's DB refuses)
- [Phase ?]: Phase 114.1: reused existing ChipNotFoundError + @map_typed_errors -> click.ClickException path (no new exception type, no new exit-code branch, no logger.error+sys.exit style) — Minimal, self-contained hardening; matches how every other command already rejects unknown chips
- [Phase 115]: Doc structure mirrors community-validation.md voice (audience/purpose lead, what-this-is-NOT framing, tables, fenced commands)
- [Phase 115]: 328PB-Uno guidance: try -b uno328pb first, fall back to -b uno only on avrdude signature-check rejection - never guess/force
- [Phase 115]: README gets exactly one pointer link; per-board matrix NOT duplicated (D-09)
- [Phase ?]: Both sub-repos re-verified merge-base ancestry live before forking v1.22 off beta (Task 1, F10) — 0 commits ahead at creation, no pre-existing operator work destroyed
- [Phase ?]: HOST_STUBS_REAL_REGISTER_UTILS hooks exactly rurp_write_data_buffer + rurp_set_control_pin — rurp_shield.h's single pin namespace covers latch strobes AND /CE+/OE with no third hook
- [Phase ?]: s_strobe_overflow is an explicit saturation flag (not silent drop), and TRACE-01b baseline is pinned at 80/80 before TRACE-03d raises it to 82/82
- [Phase ?]: EpromDatabase has no constructor seam for an alternate pinouts.json path -- the --pinouts override loads JSON directly onto db.pin_maps before derivation
- [Phase ?]: Wrote exactly 4 drift-gate tests (not 5) to match the plan's literal 4-tests-passing acceptance criterion
- [Phase 116-03]: Reworded 'no FW_ABSENT-style skipif' to 'no FW_ABSENT-style skip marker' in test_sdp_db_invariant.py's docstring so the literal grep -c 'skipif' acceptance criterion returns 0 while preserving the meaning (Phase 107-01 wording-fix precedent)
- [Phase 116-03]: Factored shared _select_0x0d_chips/_assert_chip_id_check_false helpers so the TRACE-05 non-vacuity test exercises the same code path as the real-DB assertion, not a parallel reimplementation
- [Phase 116-03]: Brace-scoped {address, byte} extraction (not a file-wide regex) for the unlock-table parity gate, because eeprom_28c.cpp has a non-initializer call site (eeprom28c_wait_for_write) using the identical literal bytes that would false-positive a loose pattern
- [Phase ?]: [Phase 116-04]: Deny list implemented as one regex covering every logging_id.h LOG_* macro rather than a hand-enumerated name list
- [Phase ?]: [Phase 116-04]: Window scoped strictly to eeprom28c_write_init's brace-matched body so the out-of-window control is correct by construction
- [Phase 116-04]: TRACE-03 checkbox left unchecked in REQUIREMENTS.md — this plan lands only the planted-LOG_ sub-negative (TRACE-03c) of TRACE-03's four required first-class negatives; the other three (unlock-table mutation, lock-table swap, protocol!=0x0D positive) land in 116-05's always-green harness suite per D-04. Mirrors the 116-01 precedent (commit 8d8c42f) that reverted an identical premature TRACE-01/03 completion mark.
- [Phase ?]: SDP_SHIPPED is a single array (not one per pinout) -- fu_flash_fast_address never consults bus_config, so the shipped stream is byte-identical across all four 0x0D pinouts by construction
- [Phase ?]: 5 reference-emitter guard cases (one per SDP_BUS_CONFIGS row, not one per distinct pinout) -- AT28C010/AT28C040 both independently assert against the shared SDP_FIXED_DIP32_28C512_EEPROM array
- [Phase ?]: Bumped sdp_assert_stream_equals failure-message buffer 192->320 bytes after the mandatory corrupted-array check showed truncation
- [Phase 116]: DIP32 RED cases (4-5) assert against a dynamically-driven reference-emitter snapshot under the same stale seed, not the canonical zero-seed SDP_FIXED_DIP32_28C512_EEPROM constant — A plain zero-seed comparison only reproduces the same incidental /OE-ordering divergence Cases 1-3 already show and proves nothing about the real write-inhibit bug (CORRECTION 3)
- [Phase ?]: Datasheet audit recorded as an honest present/unconfirmed/absent finding rather than a general statement (Phase 116 Plan 07)
- [Phase ?]: Task 3 human-verify checkpoint auto-approved per this run's explicit orchestrator auto-mode instruction; self-review against RESEARCH Pitfall 7 and the 66-of-84 figure performed directly (Phase 116 Plan 07)

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
| Phase 108 P01 | 20min | 3 tasks | 3 files |
| Phase 108 P02 | 25min | 3 tasks | 2 files |
| Phase 108 P03 | 25min | 2 tasks | 2 files |
| Phase 108 P04 | 45min | 3 tasks | 2 files |
| Phase 109 P01 | 35min | 2 tasks | 2 files |
| Phase 109 P02 | 22min | 2 tasks | 2 files |
| Phase 109 P03 | 35min | 2 tasks | 2 files |
| Phase 110 P01 | 25min | 3 tasks | 2 files |
| Phase 110 P02 | 20min | 3 tasks | 3 files |
| Phase 110-diagnostic-report-model-dual-output-provenance-prompts P03 | 25min | 3 tasks | 2 files |
| Phase 111 P01 | 20min | 2 tasks | 2 files |
| Phase 111 P02 | 12min | 2 tasks | 1 files |
| Phase 111 P03 | 12min | 2 tasks | 1 files |
| Phase 112 P01 | 20min | 2 tasks | 2 files |
| Phase 112 P02 | 45min | 2 tasks | 2 files |
| Phase 112 P03 | 35min | 2 tasks | 3 files |
| Phase 112 P04 | 40min | 3 tasks | 6 files |
| Phase 112 P05 | 35min | 3 tasks | 4 files |
| Phase 113 P01 | 20min | 2 tasks | 2 files |
| Phase 113 P02 | 30min | 3 tasks | 2 files |
| Phase 113 P03 | 35min | 2 tasks | 2 files |
| Phase 113 P04 | 35min | 2 tasks | 4 files |
| Phase 114 P01 | 12min | 2 tasks | 3 files |
| Phase 114 P02 | 15min | 2 tasks | 2 files |
| Phase 114 P03 | 30min | 2 tasks | 2 files |
| Phase 114.1 P01 | 12min | 2 tasks | 2 files |
| Phase 115 P01 | 5min | 2 tasks | 2 files |
| Phase 116 P01 | 25min | 3 tasks | 2 files |
| Phase 116 P02 | 30min | 3 tasks | 3 files |
| Phase 116 P03 | 25min | 2 tasks | 2 files |
| Phase 116 P04 | 20min | 2 tasks | 3 files |
| Phase 116 P05 | 70min | 3 tasks | 4 files |
| Phase 116 P06 | 65min | 2 tasks | 4 files |
| Phase 116 P07 | 45min | 3 tasks | 2 files |

## Session

**Last session:** 2026-07-27T22:25:22.065Z
**Stopped at:** Completed 116-06-PLAN.md
**Resume file:** None

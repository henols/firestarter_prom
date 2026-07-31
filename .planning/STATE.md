---
gsd_state_version: 1.0
milestone: v1.23
milestone_name: — PY32F071 Integration
current_phase: 124
current_phase_name: firmware-integration-merge
status: executing
stopped_at: Completed 124-04-PLAN.md (THE LANDING)
last_updated: "2026-07-31T09:01:34.715Z"
last_activity: 2026-07-31
last_activity_desc: Phase 124 execution started
progress:
  total_phases: 8
  completed_phases: 1
  total_plans: 23
  completed_plans: 15
  percent: 13
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-07-31

## Current Position

Phase: 124 (firmware-integration-merge) — EXECUTING
Plan: 5 of 12
Status: Ready to execute
Last activity: 2026-07-31 — Phase 124 execution started

**⚠ Wave 7 (124-11) is operator-gated.** MERGE-02's ARM evidence requires pushing the firmware milestone branch and dispatching the `py32f071.yml` workflow. Per D-09 the gate is **structural**, not a flag: plan 124-11 contains no task that runs `git push` or `gh workflow run` — it prints the commands and stops. `--auto`/`--chain` cannot wave it through, but an autonomous chain will still halt there awaiting the operator.

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-07-30 — v1.23 Current Milestone section + v1.23 start footer; v1.22 Archive section retained with all eight ⚠ correction blocks)

**Core value:** Algorithm-first dispatch — the minipro `protocol_id` (`algorithm`) is the single authoritative dispatch key end to end (XML → DB → wire JSON → firmware handler). As of v1.20 the last vestige violating that contract — the `mem_type`/`type` backward-compat fallback axis — is gone; firmware, wire, and host trust **only** the real protocol. v1.23 adds a fourth board target beneath that contract without disturbing it: the PROM programming algorithms stay platform-independent and the HAL boundary absorbs the new MCU, so protocol dispatch is untouched by the port.

**Current focus:** Phase 124 — firmware-integration-merge

## Milestone Context (v1.23)

- **Scope:** Land the in-flight PY32F071 firmware port and the host USB-DFU firmware installer onto `beta` as one lockstep integration, plus the cross-repo release-asset unblock, without touching the three AVR targets. Eight target features — see PROJECT.md §"Current Milestone: v1.23 PY32F071 Integration". Requirements not yet defined (this is the requirements step).
- **This is an integration milestone, not a build-it milestone.** Both halves already exist and are green: the firmware stack on `agent/py32f071-toolchain` (PR #48, OPEN draft, stacked on `agent/portability-macros`) with **PY32F071 CI green three consecutive times on 2026-07-21** compiling the *shared* command processor, framing and PROM algorithms for Cortex-M0+; the host installer on `firestarter_app` `feature/py32f071-fw-install` @ `4ee64a1` (**58 tests passing** — and they pass with `pyusb` not importable — mypy identical to pristine `origin/beta`). The "does this architecture even build" risk is retired. **The work is the rebase, the release plumbing, and the honesty.** Measured: **21 host capabilities already exist and need landing; 8 items remain to be built, and only one of those (the release-asset publication) gates any user-visible value at all.**

- **⚠ RESEARCH CORRECTIONS — read `.planning/research/SUMMARY.md` before planning any phase.** This section and PROJECT.md's were written BEFORE the four-stream research; 18 numbered corrections (R-1…R-18) and 7 adjudicated inter-researcher conflicts (A-1…A-7) apply to both. Three of four researchers built, merged and tested the branches. The five that change what gets planned: **(1)** `agent/portability-macros` **cannot land alone** — 141/141 native → **0 passing / 17 ERRORED**; its repair `780a3fb` is on the stacked branch, so the two land **atomically** (R-9/A-4). **(2)** Both repos merge with **zero conflicts** and disjoint file sets, but `platform/py32f071/CMakeLists.txt:46-47` names `flash_type_3/4.cpp` — renamed by v1.19 Phase 104 — so the ARM target **fails at CMake configure**, and `py32f071.yml` has **no `push` trigger** to catch it (A-2/A-3). **(3)** Flash growth is not the risk: **−56 B Leonardo, +22 B Uno, +28 B 328PB**, RAM unchanged; live Leonardo headroom is **2600 B on `beta` / 2656 B merged, not 2992 B** (A-1/A-5/R-10). **(4)** The cross-repo gates **fail OPEN** — a firmware rename flipped 5 legs PASS→SKIP at exit 0 with a false reason, and moving firmware files is this milestone's premise (A-7). **(5)** Flash-persistent config is **design work** — `PORTING.md` lives only on closed PRs #46/#47 and its layout does not match what #48 built (R-8/A-6).
- **Every py32 branch is 72 commits behind `beta`.** Measure against `beta`, never `main` — `main` lags `beta` by ~268 commits in firmware and ~544 in the app, which makes live branches look abandoned. The rebase is real work, not a fast-forward.
- **No PY32F071 PCB exists (operator, 2026-07-28) → software-only validation, no bench phase.** PR #48's pin map (PB0–PB7 data, PA0–PA5 control, VPP on PA4/ADC ch4) is an explicitly provisional placeholder so the target compiles before a schematic and **must not be trusted near a PROM**. Permitted claims: the target builds clean, native + host suites pass, the DFU sequence is exercised against device descriptors and mocks. Forbidden: *"the firmware runs on a PY32F071"* or *"the install works end to end."* Never write or accept a success criterion crossing that line.
- **Hard acceptance constraint:** Uno, ATmega328PB, Leonardo and the native test suite remain unaffected. Golden register traces, the dispatch-mirror guard, `check_dispatch.py`, `diff_db.py` identity, and the nine cross-repo source-scanning gates all stay green.
- **Locked decisions (operator, 2026-07-30 — do not re-litigate):** scope is port + host install + VPP **seam**; the DAC closed loop and the calibration model stay OUT (see the collision note below); slot is **v1.23**, retiring the queued v1.28/v1.29 py32 slots into it and renumbering `Binary Command Protocol` v1.23 → v1.28 while v1.24–v1.27 stay untouched.
- **⚠ The DAC-VPP / calibration collision — settled, do not reopen.** PR #45 (`feature/common-vpp-calibration`, closed, 10 commits) is ONE API spanning two concerns and the closed loop *depends* on the calibration half: `rurp_set_vpp_target_mv()` closes its loop on `rurp_read_voltage_mv()` (the **calibrated** read), and `rurp_calibrate_vpp_two_point()` **is** the White-Box Voltage Calibration milestone's Stage-2 divider trim, already cross-platform. Three of its ten commits reach into that milestone's files: `9134f2a` (`src/boards/rurp_common.cpp`, its exact Stage-1 target), `768580f` (`include/rurp_types.h`) and `b964ee6` (`src/rurp_config_utils.cpp`) — the latter two being `CONFIG_VERSION`-bump + EEPROM-migration territory, which is also where Backlog 999.1's stale-`r1` fix lives. **Resolution: seam only** — capability macros, `rurp_vpp_control_mode_t`/`rurp_vpp_result_t`, `RURP_VPP_CONTROL_MANUAL` on every board, `rurp_set_vpp_target_mv()` returning `MANUAL_ADJUSTMENT_REQUIRED`; no AVR measurement reroute, no `CONFIG_VERSION` bump. Two supporting facts: PR #45 does **not** contain the Stage-1 bandgap back-solve, so that milestone's ±10 % win is unaffected either way; and with no PCB a closed loop **cannot be validated at all**.
- **⚠ Start from PR #48. Never from PR #47.** `feature/py32f071-full-support` (closed) has a 24-file `platform/py32f071/` tree and an all-inclusive CMake list, so it reads as the most finished branch — but `src/usb.c` (141 lines) is a ring buffer over `__attribute__((weak))` **no-op** low-level hooks. It links, and a board flashed with it would be **silent on USB**. `vpp_target.c` is 13 lines; there is no SDK fetch.
- **⚠ The v1.28 ROADMAP entry's prior-art paragraph is stale** — it claims the work is "not in flight" citing PR #46 closed-unmerged and `feature/py32f071-toolchain` @ `2c2ed10` (the smallest of five branches) as the place to start scoping. All three claims were re-verified wrong against `origin` on 2026-07-30. Pending todo `correct-v128-py32-roadmap-prior-art` owns the correction and warns explicitly that `/gsd-new-milestone` reads that entry to seed scope. **Scope from PROJECT.md §"Current Milestone: v1.23", not from the ROADMAP's v1.28 entry.**
- **The self-flash bootloader is the intended primary install route; the DFU path landing here is the runner-up.** `.planning/seeds/py32f071-no-external-tool-fw-install.md` decides for a bootloader in the first few KB of the 128 KiB flash speaking the existing USB CDC + COBS framing — zero new host dependencies, structurally identical to how the Uno works. Every factory-bootloader route was rejected on host-side grounds (Puya `PY32DfuTool` is Windows-x64-only; `dfu-util` reintroduces avrdude's PATH-discovery burden; `puyaisp` needs a second USB-serial dongle on a board with native USB). The pyusb DFU client is that table's *vendored-Python-over-libusb* row, accepted at operator request so the transfer sequence gets proven; residual cost is `pyusb` + libusb, and a WinUSB driver via Zadig on Windows. **Landing it does not retire the seed** — what this milestone must capture is the PCB consequences, because the board is still paper and they are cheap now and expensive after layout.
- Phase numbering continues from v1.22's Phase 122 → **v1.23 starts at Phase 123**.
- **Branch model:** meta branch `gsd/v1.23-py32f071-integration` forked off the v1.22 tip `8be00ee` (NOT `main`, which lags by ~1267 commits). Sub-repos fork off `beta` per standing policy, then the py32 branches merge in — verify with `git` at execute time regardless. Extra worktrees `firestarter_py32_ci/` (fw @ `feature/py32f071-release-assets`) and `firestarter_app_py32/` (app @ `feature/py32f071-fw-install`) are checkouts of the same two repos, gitignored in meta, never gitlinked.
- **Release hazard, unchanged:** pushing `beta` in either sub-repo auto-fires CI and cuts a new beta — the cut is a deliberate decision, never a side effect. `firestarter_app`'s CI fix `81fa53c` lives on `beta` only and must be reintroduced whenever the milestone branch next merges toward `main`.
- **Release-asset mechanics (already designed, not yet implemented).** `py32f071.yml` deliberately does **not** cut releases: `beta-build.yml` runs `.github/scripts/update_version.py`, which rewrites `include/version.h` and auto-commits *before* building, so an image built in any other job carries a stale `VERSION` — and the host's entire update decision is that string compared against the release tag. `feature/py32f071-release-assets` @ `ad47c3b` already renames the output to `firestarter_py32f071.hex` (correct prefix and separator) but it is still an **Actions artifact**. The fold is 3 steps plus one `files:` line, spelled out in `platform/py32f071/README.md` §"Release integration" — use a **glob**, not a literal path, because `softprops/action-gh-release` warns on an unmatched glob but *fails* on a missing literal file, so a broken ARM build must never block the AVR beta.

## Roadmap Summary (v1.23)

**Created:** 2026-07-30 — adopted research SUMMARY.md's reconciled 8-phase spine (123–130) verbatim; no coverage gaps found requiring deviation.

**Phases:** 8 (123–130). **Granularity:** Comprehensive (config). **Coverage:** 47/47 v1 requirements mapped, 0 unmapped — exact 1:1 category→phase mapping (BASE→123, MERGE→124, VPP→125, CFG→126, HOST→127, REL→128, PCB→129, CLOSE→130).

| Phase | Goal | Requirements | Research |
|-------|------|--------------|----------|
| 123 Non-Regression Baselines & Gate Hardening | Record AVR flash/RAM + native counts; split the fail-open FW-absent proxy; ship every checker with a planted-violation fixture — before any firmware moves | BASE-01…08 | skip |
| 124 Firmware Integration Merge (atomic) | Land `agent/portability-macros` + the py32 stack as one commit-pair; fix C-1 (CMake rename); add ARM `push` trigger; make the pinmap refusal fire | MERGE-01…08 | skip |
| 125 VPP Control Seam | Hand-authored `rurp_vpp.h`/`.cpp`; every board → `MANUAL_ADJUSTMENT_REQUIRED`; prove `rurp_config_utils.cpp` untouched | VPP-01…03 | skip |
| 126 Flash-Persistent Config ⚠ highest-risk | Dual-slot CRC32 py32 config backend behind a common/per-platform seam; AVR EEPROM path proven a pure move | CFG-01…07 | **yes** |
| 127 Host DFU Installer *(parallel w/ 125-126)* | Merge `feature/py32f071-fw-install`; close the 8 remaining host gaps | HOST-01…08 | skip |
| 128 Release-Asset Fold | Fold ARM build into `beta-build.yml` after the version bump; publish `firestarter_py32f071.hex` as a real release asset | REL-01…04 | skip |
| 129 Flash-Path Decision & PCB Record | Record the 3-tier flash path + PCB requirements before any schematic, citing Phase 126's actually-reserved flash map | PCB-01…05 | **yes** |
| 130 Close | Apply R-1…R-18; honesty ledger; ROADMAP slot renumber; release-decision artifact before any push | CLOSE-01…04 | skip |

**Load-bearing ordering (not preference):** 123→124 (gates predate the moves they detect) · 124 atomic (A-4: portability-macros alone breaks native 141/141→0/17-ERRORED) · 125→126 (shared-file attribution: both touch `rurp_config_utils.cpp`) · 127→128 (asset-name contract direction) · 126→129 (real map, not intended) · 128 after the `beta-build.yml` version bump. **Genuinely parallel: {125, 126} ∥ {127}** — different repo, disjoint files, no shared gate; the one real parallelisation opportunity in this spine.

**Deviation from research spine:** none. The 8-phase spine in `.planning/research/SUMMARY.md` §"Implications for Roadmap" was adopted verbatim; the category→phase mapping is exact and required no coverage-gap resolution.

**Full detail:** `.planning/ROADMAP.md` §"v1.23 — PY32F071 Integration (PLANNING)".

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

### Deferred Items — acknowledged at v1.22 milestone close (2026-07-30)

Close type: **override_closeout** — all v1.22 phases (116–122) are `phase_complete` + `verification_status: passed` (Phase 122 verified 5/5) and all 41 v1 requirements are Complete, but `audit-open` reports 14 open artifact items, so the close is recorded as an override with the items acknowledged-and-deferred (operator: "Acknowledge & proceed"). **None originate in v1.22 (Phases 116–122)** — they are the identical pre-existing cross-milestone carry-forwards re-confirmed at the v1.18/v1.19/v1.20/v1.21 closes. Known verification overrides: 14.

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
| todo | correct-v128-py32-roadmap-prior-art | medium |
| todo | decode-infoic-flags-bits-14-15-protect-metadata | low |

*(+8 further todos beyond the 5 the audit enumerates — `audit-open` reports 5 with a `_remainder_count: 8`.)*

**⚠ This is the fifth consecutive close to acknowledge the same 14 items.** Recorded here as a standing carry-forward rather than a fresh finding. The two debug sessions and the five verification gaps all predate v1.17; a deliberate one-pass resolution is worth more than a sixth acknowledgement.

**New v1.22-originated carry-forwards (NOT counted in the 14 — none is an `audit-open` artifact type):**

| Item | Status | Disposition |
|------|--------|-------------|
| `0x0D` SDP silicon graduation | **deferred — no AT28C part on the bench** | Sampling rate zero, by design and by stated ceiling. Unblocks on a community re-test (gh#11 / gh#12, both left OPEN) or a future bench session. `PROTOCOL-LEDGER` `0x0D` stays `UNVERIFIED`. |
| AT28C 2K×8 class (19 chips on `DIP24_2816`) | **REFUSED by the derived allow-set** | 7 `pre-SDP generation`, 12 `unrecognised`; SDP-F7/SDP-F8 name the family deferred. `AT28C16` additionally `adapter-required` (see FUT-04). Correcting D-14's overclaim about this class is what surfaced it. |
| ⚠ App CI fix `81fa53c` on `beta` ONLY | **must be reintroduced at the next merge toward `main`** | Adds a `pytest.mark.skipif` guard to `test_check_is_memory_cmd_no_ifdef.py` + `test_check_no_log_in_sdp_window.py`'s `test_checker_exits_zero_on_clean_source` legs, which hard-fail in a standalone checkout with no sibling `firestarter` repo. Cherry-picked onto the milestone branch then **reverted** to keep branch HEAD byte-matching Plan 122-03's recorded merge SHA. `ci.yml` carries the same standalone-checkout risk. Recorded in `122-CUT.md` §8. |
| `check_ledger.py` pre-existing RED | **deliberately not fixed in v1.22** | 2 `LEDGER-01` violations from v1.19 Phase 104's `flash_type_3`/`flash_type_4` → `flash_nor_unlock`/`flash_5v_page` rename. Fixing it would edit a closed milestone's artifact; CLOSE-01 never gated on it. **Recommended as a backlog seed.** |
| Stray `3.0.0b12` prereleases | **left public (D-05, CLEANUP declined)** | Both repos. Operator decision at the `122-DECISION.md` gate; revisit only if it confuses a community installer. |
| Meta `catalog-sync-check.yml` + firmware `build.yml`'s `native_nodevtools` step | **`main`-gated — dormant, never run against v1.22 code** | Corrected against the workflow files at close: the Phase 122 hand-over said both carry `ref: main` in their checkout steps; only one does. `catalog-sync-check.yml` lives in the **meta** repo (not a sub-repo), triggers on push/PR to `main` scoped to `paths: tools/catalog/**`, and checks out **both sub-repos at `ref: main`**. Firmware `build.yml` has no `ref:` override — it simply only triggers on `push: branches: [main]`. Since `main` is never merged under this branch model, both are dormant rather than red. A known property, not a defect to chase. |
| `--sdp-relock`, three-field SDP report shape, `lock-status` + protection table | **deferred / out of scope** | `--sdp-relock` → v1.23+; the report shape retains a minimal honesty floor (HOST-05); `lock-status` stays a planted seed at `.planning/seeds/lock-status-command-hand-curated-protection-table.md`. |
| release-gate: stable promotion | **OPERATOR-GATED** | Standing v1.11–v1.22 policy. PyPI `info.version` remains `2.0.7`; `main` untouched in all three repos (firmware lags `beta` by 268 commits, app by 544, meta by 1267). |

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
- `fold-response-code-into-log-macro.md` (medium) — captured during v1.22; blocked on Phase 117 (shares `eeprom_28c.cpp`).

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260728-ahy | Fix `dev test --submit`: drop the nonexistent `gsd-inbox` label from the `gh` create argv, retarget `SUBMIT_REPO` → `henols/firestarter_prom`, and stop both tiers reporting phantom success | 2026-07-28 | `688bf10..36a9bb5` (firestarter_app submodule; gitlink NOT bumped) | [260728-ahy-fix-dev-test-submit-gh-tier-drop-nonexis](./quick/260728-ahy-fix-dev-test-submit-gh-tier-drop-nonexis/) |
| 260729-iyx | Install Bun in devcontainer to enable the Claude Code Discord channel plugin (DM-only) | 2026-07-29 | `c5385a7` | [260729-iyx-install-bun-in-devcontainer-to-enable-di](./quick/260729-iyx-install-bun-in-devcontainer-to-enable-di/) |

**Discord channel plugin — container side DONE, Discord side operator-owned (260729-iyx, 2026-07-29).** `discord@claude-plugins-official` v0.0.4 was already installed and `~/.claude/channels/discord/.env` already held a token, but `bun` was missing — the plugin's `.mcp.json` launches `"command": "bun"` as a **bare name** resolved from PATH by the MCP launcher with no shell, so Bun 1.3.14 is installed at `/usr/local/bin/bun` (verified resolvable under `env -i` + stock system PATH) and the same layer is now in `.devcontainer/Dockerfile` for rebuild durability. `~/.claude` **is** a named volume, so the token and `access.json` survive rebuilds; `~/.bun` is not, which is why the prefix is overridden. **Ordering trap:** `/discord:access policy allowlist` must be set only *after* pairing succeeds — setting it first makes pairing impossible, because the default `pairing` policy is what emits the code.

**Submission target settled (operator, 2026-07-28):** `SUBMIT_REPO` = `henols/firestarter_prom`, reversing the v1.21 Phase 113 D-01 choice of `henols/firestarter_app`. Authority is `henols/firestarter_prom#6` — *"New GitHub issues must be allowed only in `henols/firestarter_prom`"*, with issue creation to be **disabled** on `henols/firestarter` and `henols/firestarter_app`. A `dev test` report spans host + firmware + shield and cannot attribute itself to one layer, so the cross-repository tracker is the only correct destination. D-01 itself is unchanged and reinforced (hardcoded constant, never remote-inferred); the repo name now lives in exactly one place, with tests deriving every URL/argv expectation from it and one literal lock assertion so a silent retarget fails loudly.

**`firestarter_prom#6` repo settings APPLIED (2026-07-28).** `has_issues` set to `false` on `henols/firestarter` and `henols/firestarter_app` via `gh api -X PATCH`; `henols/firestarter_prom` stays `true`. Verified: `gh issue create --repo henols/firestarter_app` now refuses with *"the 'henols/firestarter_app' repository has disabled issues"*.

- The soft half was **already** in place before this and needed no change: both repos carry `.github/ISSUE_TEMPLATE/config.yml` with `blank_issues_enabled: false` + a `contact_links` redirect to `firestarter_prom/issues/new/choose`, and no other templates. That governs only the **New issue button** — a template config cannot block direct-URL or API creation, which is exactly how the misfiled `firestarter_app#43` got there. `has_issues: false` is the only hard block.
- **Side effect (accepted):** disabling issues hides the repos' existing issues — 7 on `firestarter`, 16 on `firestarter_app`, **all closed**, so only closed history is hidden. Fully reversible: `gh api -X PATCH repos/henols/firestarter_app -F has_issues=true` restores every issue; nothing is deleted.

**Remaining follow-up — release sequencing (operator-owned).** Published `3.0.0b11` still has `SUBMIT_REPO = henols/firestarter_app`, and its browser tier now hits **HTTP 404** on `firestarter_app/issues/new` (measured 2026-07-28; `firestarter_prom/issues/new` returns 302). So for b11 installs `--submit` now fails visibly instead of misfiling — arguably the better failure, but it is a dead end until a release carries the retarget. The five fix commits are cherry-picked onto **local** `beta` (`591c819..0050277`, on top of `ec74474`) and **not pushed**; pushing `beta` auto-fires the beta CI and cuts the next beta (the stray `3.0.0b12` mechanism from the v1.21 close), so that push is a deliberate release decision.

Bench cleanup done: `firestarter_app#43` (the misfiled `fm1608` report) closed with a pointer to `firestarter_prom#18`; the duplicate test issue `firestarter_prom#19` deleted. Surviving report: `firestarter_prom#18`.

### Roadmap Evolution

- v1.22 roadmap created 2026-07-27: 7 phases (116–122), 36/36 requirements mapped, 0 unmapped. Adopted the research SUMMARY.md §"The reconciled spine" verbatim — no coverage gaps found, no deviation needed. Strictly linear dependency chain (116→117→118→119→120→121→122); every adjacent-phase link is one of the milestone's non-negotiable ordering invariants (harness-before-fix, fix-before-observe, observe-before-lock, firmware-before-host, dev-test-fix-before-close), not a planning convenience. No bench phase — first milestone since the community-validation-command era with zero hardware-gated success criteria (no AT28C part in operator inventory).
- v1.21 roadmap created 2026-07-02: 7 phases (108–114), 24/24 requirements mapped (corrected from the REQUIREMENTS.md draft's stale "20 total" count). Phase spine per research SUMMARY.md §Implications for Roadmap: 108 (engine+pattern+fingerprint) → 109 (safety gate) → 110 (report+provenance) → 111 (voltage sampler, hardware-gated, isolated) → 112 (CLI wiring) → 113 (submission) → 114 (disposition lock, close).
- v1.20 roadmap created 2026-07-02: 3 phases (105–107), 12/12 requirements mapped. FW → HOST → DOCS+GATE strictly linear sequencing (wire-contract removal ordered so it's never half-broken).
- Phase 104 added: Rename protocol header and .cpp files to descriptive protocol-type names (replace hard-to-read flash type N naming)
- Phase 115 added: Beta install & firmware-flash bench validation (community onboarding) — hardware-gated capstone of v1.21

## Operator Next Steps

- **v1.23 PY32F071 Integration is ACTIVE** (started 2026-07-30, branch `gsd/v1.23-py32f071-integration`). Next: define requirements, then `/gsd-plan-phase 123`.
- **The release-asset blocker is half-resolved, and the remaining half is designed.** `feature/py32f071-release-assets` @ `ad47c3b` already fixes the *name* (`firestarter_py32f071.hex` — correct prefix and separator), but the image is still an Actions **artifact**. Publishing it as a release asset means folding the ARM build into `beta-build.yml` *after* the version bump: 3 steps plus one `files:` glob, spelled out in `platform/py32f071/README.md` §"Release integration".
- **⚠ Two ROADMAP corrections owed as part of this milestone:** the stale v1.28 prior-art paragraph (pending todo `correct-v128-py32-roadmap-prior-art`, all five corrections — it warns that `/gsd-new-milestone` reads that entry to seed scope), and the slot renumber (retire v1.28/v1.29 into v1.23; `Binary Command Protocol` v1.23 → v1.28; leave v1.24–v1.27 alone).
- **⚠ GSD footgun hit on 2026-07-30 — watch for it.** `gsd-tools query commit` silently switched the checkout off `gsd/v1.22-…` onto the divergent `gsd/v1.21-community-chip-validation-command` and committed there, because `init.new-milestone` reported `current_milestone: "v1.21"` while STATE.md frontmatter said `v1.22`, and `branching_strategy: milestone` acted on the stale value. Side effect: HEAD's gitlinks reverted to the **b11** commits, silently undoing the v1.22 b14 bump. Recovered (housekeeping re-landed as `8be00ee` on the right branch, v1.21 branch reset, gitlinks re-verified at `5c9160a`/`e7d3ee8`). **Check `git rev-parse --abbrev-ref HEAD` after every `gsd-tools query commit`.**
- **Carry into the next merge toward `main`:** reintroduce `firestarter_app`'s `81fa53c` (see the v1.22 Deferred Items table) or `ci.yml`'s standalone-checkout failure resurfaces.
- **Worth one deliberate pass:** the same 14 `audit-open` items have now been acknowledged at five consecutive closes. Also `check_ledger.py`'s 2 pre-existing `LEDGER-01` REDs — a small, self-contained backlog seed.
- **Watch for:** a community re-test on [gh#11](https://github.com/henols/firestarter_prom/issues/11) / [gh#12](https://github.com/henols/firestarter_prom/issues/12) — both left OPEN. Real AT28C silicon is the only thing that can move `0x0D` off `UNVERIFIED`.

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
- [Phase 117-01]: Followed 117-CONTEXT.md D-01/D-02/D-03 exactly: un-mocked set_data, flipped+reordered five response-code assertions, added permanent case 8, captured the edited-and-RED intermediate before any production change; ticked no requirement (oracle half only, closes jointly with 117-02)
- [Phase 117-02]: eeprom28c_write_init rebuilt on a 0x0D-local remap-aware eeprom28c_emit_command_sequence driven through handle->firestarter_set_data, closing FIX-01 and FIX-03 (A16-A18 staleness) as one routing change — flash_execute_command bypasses handle->bus_config and CONTROL_REGISTER entirely; memory_set_data applies the full remap and rewrites CONTROL on every address change
- [Phase 117-02]: Inverted (0x5555, 0x20) read-back deleted outright; replaced by eeprom28c_wait_for_sdp_completion (t_WC wait + bounded silent DQ6 toggle poll, never writes response_code) closing FIX-02 — Both AT28C datasheets state the command sequence byte is never written to the device, so the old check could only pass when the sequence was NOT recognised
- [Phase 117-02]: Reworded 3 in-code comments to avoid literal-substring collisions with non-comment-filtered acceptance-criteria greps (rurp_set_data_output exactly 1; eeprom28c_wait_for_write(handle, 0x5555 exactly 0) — Meaning fully preserved; matches the project's established pattern of wording around literal-substring gates rather than weakening them
- [Phase 117-03]: FIX-06: eeprom28c_write_execute's conflated eeprom28c_wait_for_write split into eeprom28c_wait_for_page_write (DQ7-complement completion poll) and eeprom28c_verify_page_readback (always-on per-byte data-landed read-back over the current flush window, failing-address attribution via MSG_ERR_VERIFY); conflated function deleted outright
- [Phase 117-03]: Anti-hollow proof executed: read-back temporarily removed, both planted-violation cases went RED and the isolation control stayed GREEN, recorded verbatim in 117-03-SUMMARY.md; temporary revert never staged/committed (confirmed byte-identical restore)
- [Phase 117-04]: Followed 117-CONTEXT.md D-10/D-11 exactly: FIX-05 guard lives in test_sdp_harness, reads the production EEPROM_SDP_DISABLE array via extern (plan 117-02's linkage grant), and the planted-violation counterpart reuses TEST_UNLOCK_MUTATED_TERMINAL rather than adding a second copy — Matches the plan's discretion resolutions and D-11's cross-guard requirement
- [Phase 117-04]: Reworded two in-code comment mentions of the two new test-case names to avoid a third literal occurrence, since acceptance criteria required each name to appear exactly twice (definition + RUN_TEST) — Meaning preserved (both comments still cite FIX-05/D-11); mirrors 117-02's identical literal-substring-grep adjustment pattern
- [Phase 117]: Recorded the measured Leonardo flash delta (+204 B) as-is despite the research prediction of net-negative -- measured over predicted.
- [Phase 117]: Recorded firestarter_app's pre-existing dirty working tree as an explicit named exclusion rather than claiming a clean tree -- the load-bearing host-untouched proof is the unmoved commit history (36a9bb5).
- [Phase 117]: Ticked FIX-04 only in REQUIREMENTS.md after independently verifying FIX-01/02/03/05/06 were already Complete -- six of six for Phase 117.
- [Phase 117 regression gate]: **Phase 117 broke 4 Phase-116 host-side gates.** `test_sdp_table_parity` (x3) and `test_check_no_log_in_sdp_window` (x1) scan `eeprom_28c.cpp` source text and were keyed to pre-117 identifiers/declaration syntax: 117-02 replaced `flash_execute_command(EEPROM_SDP_DISABLE)` and changed the definition to `EEPROM_SDP_DISABLE[6] =` (extern needs a complete array type, but the parity regex required `[]`), and 117-03 deleted `eeprom28c_wait_for_write` outright. Proven Phase-117-caused, NOT pre-existing, by injecting phase-base `ada4bdc` source via the `FIRESTARTER_SDP_SRC` env seam. Host CI (`ci.yml` pytest --cov, `beta-release.yml` pytest) was red. Fixed under operator authorization, append-only per the anti-hollow contract: `firestarter_app@9dd11a9`, with record corrections in `firestarter@f8d10a5` (RED-BASELINE FIX-04 gate section) and `117-05-SUMMARY.md`.
- [Phase 117 regression gate]: **Narrowed the host-untouched claim rather than deleting it.** True and load-bearing: Phase 117 introduced no wire, protocol, or behavioral host change (no `MSG_*`/`FLAG_*`/command/CLI/serialized field) -- the two changed host files are source-scanning test gates, which cannot participate in firmware/host version skew, so the firmware-before-host ordering invariant is intact and FIX-04's substantive blob-SHA content is unaffected. Meta gitlink still not bumped.
- [Phase 117 regression gate]: **Root cause is a PLAN-COVERAGE gap, not an implementation defect.** Phase 116 anticipated this exact case in its own source comments and the checker's stderr ("ADD the new anchor ... rather than deleting this gate"); none of Phase 117's five plans owned that step. **Carry into Phase 118+ planning:** any firmware rename/deletion must be checked against the host-side source-scanning gates (`tools/check_*.py`, `tests/test_sdp_*`, `tests/test_check_*`) before the phase closes -- Phase 118's OBS-01 touches this same SDP window and will trip the same class of gate.
- [Phase 117 regression gate]: `test_audit_coverage_matrix::test_golden_file_matches` confirmed the only other host failure and proven unrelated -- fails identically with the gate fixes stashed, reads the chip database, references no firmware path. Same stale golden carried since v1.21; still needs its own regeneration commit.
- [Phase 118-01]: scan()'s return contract widened to (violations, emitter_range, poll_range); anchor tuples repurposed as a write_init rename tripwire, no longer computing the window — Plan 118-04's own verification depends on knowing this contract
- [Phase 118-01]: Case 2's expected planted-line number derived from the fixture at test time instead of a second hardcoded literal — Prevents a future re-plant from silently desyncing the assertion from the fixture
- [Phase ?]: D-04 shape reused verbatim: four separate SDP catalog ids with literal format strings, not one parameterised id with an unlock/lock discriminator
- [Phase ?]: Left the after-line's format string carrying only the measured duration; the budget lives solely in the runtime WARN branch, avoiding a duplicate AT28C_TBLC_MAX_US literal (118-04, Claude's Discretion)
- [Phase 118]: 118-05: make_sdp_handle gained a default-arg extra_flags parameter (not a sibling function) so cases 9/10 share one factory/row with zero churn to the 8 existing call sites
- [Phase 118]: 118-05: AT28C_TBLC_MAX_US is private to eeprom_28c.cpp's TU (not exported) -- Case 11 mirrors the value as a cited local constant while deriving sdp_seq_len from the real exported EEPROM_SDP_DISABLE array
- [Phase 118-06]: 9-row CORRECTION-4 gate table: gen_sdp_bus_config.py + its drift test as 2 rows, check_dispatch.py + build_db.py combined as 1 row (single shared disposition, no dedicated pytest)
- [Phase 118-06]: Re-derived (not copied) both boards' phase-base flash/RAM figures via a throwaway git worktree at f8d10a5
- [Phase 118-06]: test_no_programmer_found_* divergence recorded honestly: live serial devices ARE present this run yet the pair still passed 2/2 -- not explained by board-absence
- [Phase 118]: OBS-04: measured Leonardo SDP-disable emit duration at 572us against a 600us (6x AT28C_TBLC_MAX_US) budget, full provenance in 118-MEASUREMENT.md; no operator checkpoint per D-12 — Milestone's only empirical result; D-13 requires raw output with provenance, kept out of PROTOCOL-LEDGER to avoid a validation-ceiling misread
- [Phase 118]: Chip-id mismatch warning did not appear because at28c256's DB entry carries chip-id: 0 (skip ID check) -- documented as a stronger confirmation of D-01's unconditional report lines, not a deviation — at28c256 chip-id field bypasses eeprom28c_check_chip_id's early-return entirely, regardless of socket contents
- [Phase 119-01]: 0x61's format string carries both D-12 clauses in one line: sequence emitted AND protection state not readable
- [Phase 119-01]: messages.h carries only numeric #defines (no PROGMEM string table); three new unreferenced ids cost 0 bytes flash this plan
- [Phase ?]: 119-02: is_memory_cmd() is a header-inline switch over exactly eight named CMD_* macros with zero preprocessor conditionals in its body -- never names CMD_DEV_ADDRESS/CMD_DEV_REGISTER, which is what makes it DEV_TOOLS-invariant
- [Phase ?]: 119-02: three named behaviour deltas (cmd 7, cmd 8, cmd 0/CMD_IDLE) accepted as deliberate safety tightening / firmware-internal-state exclusion, not preserved behaviour
- [Phase ?]: 119-02: firestarter.cpp's second ordinal-range guard (three debug-only lines) deliberately left unconverted -- diagnostics only, not an admission gate
- [Phase ?]: LOCK-03's textual oracle: check_is_memory_cmd_no_ifdef.py brace-matches is_memory_cmd()'s own definition pattern (static inline bool, not check_no_log_in_sdp_window.py's void-only _func_def_pattern) and asserts both zero preprocessor conditionals and an exact eight-command CMD_* set
- [Phase ?]: Planted-violation fixture wraps CMD_SDP_UNLOCK/CMD_SDP_LOCK case labels in #ifdef DEV_TOOLS/#endif inside the switch body, keeping all eight CMD_* names textually present so the fixture isolates the no-conditional assertion from the command-set assertion
- [Phase 119-04]: EEPROM_SDP_ENABLE[3] (AA-55-A0) added with load-bearing extern linkage, 0x0D-local, no default: arm in configure_eeprom28c per D-05
- [Phase 119-04]: Two standalone ops (eeprom28c_sdp_unlock_execute/eeprom28c_sdp_lock_execute) rather than one cmd-discriminated function; check_no_log_in_sdp_window.py repaired in the same plan as the D-14 helper refactor that broke it
- [Phase ?]: Kept the temporary SDP_TRACE_DUMP dump helper permanently behind #ifdef (test_sdp_harness.cpp style) rather than deleting after use
- [Phase ?]: DIP32_28C512_EEPROM's lock golden recorded under the deliberately stale upper-address CONTROL seed -- length 33 with an extra CONTROL_REGISTER-clearing write, not 30/index-27 like the other three pinouts
- [Phase 119]: LOCK-05 closed: three-way byte-identity + distinctness guard over EEPROM_SDP_ENABLE/FLASH_ENABLE_WRITE_PROTECTION/FLASH_ENABLE_WRITE (link-time firmware oracle + independent source-text host oracle); D-12 report-shape, D-14 budget-WARN fires/does-not-fire pair, D-13 standalone-unlock==auto-unlock stream equality all proven; criterion-5 header-comment deviation recorded (same class as D-05/D-15, flash_utils.h stays byte-frozen)
- [Phase 119]: Option (a) taken for RESEARCH Open Question 1: both native envs widened with +<operation_utils.cpp>, in lockstep; a satisfiable link gap (op_reset_timeout) was stubbed rather than falling back to option (b) -- LOCK-04/DEVTEST-01 proofs are now tests, not prose
- [Phase 119]: The generic NULL-main refusal lives at operation_utils.cpp's single fall-through (D-06), reusing MSG_ERR_NOT_SUPPORTED; no default: arm added to configure_eeprom28c or any other configure_* handler
- [Phase 119]: LOCK-04 marked Complete as mechanism-corrected, intent-satisfied (D-05's disproof + D-06's guard), requirement wording unchanged; LOCK-02 marked Complete via the dispatch proof (case group 3) plus the wiring proof (cases 24/25)
- [Phase ?]: Plan 119-08: verified structural precondition (nothing followed write_execute's per-byte loop) before the single-exit restructure; tracker+report line landed at +100 B all boards
- [Phase ?]: Plan 119-08: host_stubs_common.inc is NOT blob-identical to phase base (Plan 119-07 added op_reset_timeout stub) -- corrected the stale acceptance-criterion claim rather than restating it
- [Phase 119]: Plan 119-09: amended Phase 121 ROADMAP scope + REQUIREMENTS.md DEVTEST-01 mapping to record the firmware half (fail-closed CMD_ERASE via generic NULL-main refusal) landed early in Phase 119; DEVTEST-01 checkbox stays unticked, host half stays Phase 121 — D-08: an unamended Phase 121 would lead a future planner to re-implement a fix that already shipped, or mark DEVTEST-01 failed
- [Phase 119]: PROJECT.md's SIXTH CORRECTION block records: LOCK-04 mechanism-corrected/intent-satisfied (D-05/D-06); LOCK-06's 3348B superseded by live 2992B (D-15), DEV_TOOLS build confirmed binding at 1292B cost; three command-behaviour deltas incl. CMD_IDLE (F-B2); _SRAM_PROTO_IDS KEEP disposition for Phase 120 (F-F2) — Gathers this phase's four mechanism-vs-intent divergences and three deliberate behaviour deltas in one place per D-08, so they read as decisions rather than surprises
- [Phase 119]: LOCK-06 closed: full-phase Leonardo flash delta +392 B measured against the live 2992 B phase-base headroom (28672-25680), landing at 2600 B free -- fits, no threshold claim beyond that; -D DEV_TOOLS confirmed the binding, tighter build (1292 B flag cost)
- [Phase 119]: 119-NONREGRESSION.md written: nine-row CORRECTION-4 gate checklist handed to Phases 120-122; host_stubs_common.inc's true non-identity recorded with its cause; sdp_expected.h's retired whole-file blob-SHA shorthand replaced by re-verified per-array byte-identity
- [Phase 119]: Plan 119-11: Leonardo's page-boundary-crossing write (6080us) is not directly comparable to the Uno-class boards' clean within-page figures (84/88us) -- traced via source, not guessed
- [Phase 119]: Plan 119-11: All three boards measured; Leonardo write succeeded (empty socket, -b skips blank check), Uno/uno328pb both failed identically at page-1 readback verify; no board recorded not-measured
- [Phase ?]: sdp_capability predicate is name-keyed (db.get_eprom) with an injected db, not DB-loader-decoupled — resolve_chip's programmer dict has no protocol-id/name (D-03 mechanism correction, RESEARCH F-06)
- [Phase ?]: sdp_capability_for_entry raises KeyError (never a silent default) on a dict missing protocol-id, naming resolve_chip as the likely wrong dict — anti-vacuity by construction
- [Phase ?]: F-120-05 corrected in constants.py: firmware FLAG_* block ends at FLAG_SKIP_SDP_UNLOCK 0x100 -- no 0x200 flag exists; ROADMAP.md:363 and Phase 120 Depends-on line are wrong; REQUIREMENTS.md deliberately not edited
- [Phase ?]: COMMAND_NAMES has two dereference sites (eprom_operations.py:301 and :377), not one; both CMD_SDP_* are unconditional in firmware, never DEV_TOOLS-gated
- [Phase 120-03]: Confirmed both CONTEXT.md corrections live before fixing: target is _log_rurp_feedback (not _log_response), and the blast radius is six unconditional INFO-band ids (0x5E/0x5F/0x60/0x61/0x62 + 0x5B MSG_INFO_HW), not five. — 0x5B is emitted via the unconditional LOG_WARN_ID_U8 alias despite catalog severity INFO, so the fix also partially resolves Phase 35's CR-02 hard-fail-loud warning.
- [Phase 120-03]: Promotion kept to exactly one elif arm; NON_RESPONSE_PREFIXES and get_response() left untouched so INFO frames still never reach the operation layer (load-bearing for plan 120-08's D-10). — Scoping the change minimizes risk and keeps the negative-scoped-promotion test meaningful.
- [Phase 120-05]: Task 1's five HOST-04 named-refusal/structural-invariant legs reuse the module's existing minimal-literal-dict idiom; only the F-06 shape leg (Task 2) uses a real EpromDatabase(skip_local_override=True)+resolve_chip(), per the plan's explicit prohibition against faking the shape it exists to prove
- [Phase 120-05]: Local-override leg isolates the config dir via patch("firestarter.config.DATABASE_FILE", ...) (test_config.py's existing idiom), not FIRESTARTER_CONFIG_DIR — config.py's DATABASE_FILE/PIN_MAP_FILE constants are fixed at import time
- [Phase 120-06]: sdp_unlock/sdp_lock are payload-free copies of erase_eprom's shape (no main_phase_handler); True means the sequence was emitted, never a silicon-state claim
- [Phase 120-06]: build_flags gains skip_sdp_unlock as a keyword-only parameter (bare * after skip_erase) mapping FLAG_SKIP_SDP_UNLOCK, because both production callers pass the first four args positionally (D-19)
- [Phase 120-06]: Emitted command_dict flags == 2 for 0x0D chips (DB FLAG_CAN_ERASE) is pinned as firmware-inert at the wire boundary, not suppressed
- [Phase ?]: Rebuilt constants parity gate is header-guard-aware: whole-file #ifndef __FIRESTARTER_H__ include guard excluded from depth tracking, else every define sits at depth >= 1 making the conditional-compilation assertion vacuous
- [Phase ?]: Exemptions for CMD_IDLE/CMD_FRAME_MAX/CMD_DEV_ADDRESS/CMD_DEV_REGISTER are a frozen four-entry name-pair map (never a skip-set), deliberately not auto-derived
- [Phase ?]: HOST-03's same-commit-pair wording read honestly: firmware landed CMD_SDP_UNLOCK/LOCK in Phase 119, host lands the parity gate in Phase 120 deliberately per HOST-06 ordering -- proven bidirectional agreement, not single-commit landing
- [Phase ?]: dev sdp's four gates run in D-08 order (absent -> capability -> support-status -> confirm -> serial), the exact reverse of dev test's confirm-before-absent-chip ordering
- [Phase ?]: No --destructive-style mode flag for dev sdp (D-05): the enable/disable subcommand argument IS the mode
- [Phase ?]: dev sdp refuses off-TTY without -y (D-06), inverting dev test's off-TTY-proceeds behaviour, since dev sdp has no flag that could stand in for consent
- [Phase ?]: MSG_ERR_UNKNOWN_CMD keyed by message id (not text) and mapped to FirmwareOutdatedError naming 'firestarter fw --install' (D-14)
- [Phase ?]: D-10 summary line uses click.echo, not logger.info, after logger.info proved unreliable under CliRunner capture for a mocked-operator invocation
- [Phase 120]: D-04: capability-refused protocol-0x0D chips get FLAG_SKIP_SDP_UNLOCK force-set on write, with a mandatory default-visible report line (deliberate divergence from 3.0.0b11)
- [Phase 120]: D-18: --skip-sdp-unlock on a non-0x0D chip warns and proceeds; bit still emitted, write not refused or aborted
- [Phase 120]: D-15: write_eprom requires firmware's 0x86 (MSG_WARN_SDP_UNLOCK_SKIPPED) ack when --skip-sdp-unlock was set on a protocol-0x0D chip; absence fails the write loudly, naming firestarter fw --install — Closes HOST-06's flag-bit half; detects after the fact rather than preventing
- [Phase 120]: D-16: no version floor introduced for HOST-06 -- the firmware/host landing-order invariant is recorded as fact (firmware Phase 119 tip 0048b3d, host Phase 120) rather than enforced by a version comparator — Host cannot see the firmware pre-release suffix; a version floor would tie correctness to Phase 122's CLOSE-03 release decision
- [Phase 120-11]: dev test redesign folded into Phase 121 ROADMAP scope as a recorded REVERSAL of Phase 112 Plan 04 (112-UAT.md), SAFE-01 and SAFE-03 (D-20) -- amendment only, no implementation
- [Phase 120-11]: REQUIREMENTS.md DEVTEST-02..06 added Pending/Phase 121; v1.21 SUB-01/SUB-02 recorded as reversed without editing archived wording; coverage corrected to 41/41 mapped, 0 unmapped
- [Phase 120-11]: PROJECT.md SEVENTH CORRECTION records the derived 43/41 HOST-04 partition provenance and corrects SIXTH CORRECTION item 6's stated reason (_SRAM_PROTO_IDS is vacuous in production; KEEP disposition still stands)
- [Phase 120-12]: Row 7 (test_revision_constants_parity.py) recorded CHANGED BY DESIGN, not unchanged, per this phase's own rebuild
- [Phase 120-12]: 120-VALIDATION.md's Wave-0 rows corrected in place where the originally-authored test reference did not match the landed test, before flipping nyquist_compliant/wave_0_complete true
- [Phase 120-12]: The dev test submit repo-target ask discharged as verification only: SUBMIT_REPO already correct at e615b4c/2b9e8dd; released-artifact caveat recorded, not re-fixed
- [Phase 121]: find_prior_report/comment_via_gh added as injected-seam gh functions; submit_report restructured to dedup-first/always-ask/comment-on-duplicate (D-09/D-10/D-11); negative argv widened to a deny-set on both gh paths incl. short forms (DEVTEST-06, RESEARCH Pitfall 6)
- [Phase 121]: D-15's mechanism corrected per RESEARCH C-7: edit meta catalog only, run sync_to_subrepos.sh to regenerate both mirrors; three-way byte-identity + sync idempotence proven
- [Phase ?]: GATE-02 closed (Plan 121-13): all eight docs corrected across both sub-repos for the post-fix SDP/erase model and the always-writes reality; doc/lockable-proms.md first-committed with its wrong AT28C16/64 row split against sdp_capability.py's derived allow-set, no provenance header (D-16); GATE-02's named doc list widened per D-17 (community-validation.md, beta-testing-install.md), REQUIREMENTS.md wording unedited
- [Phase ?]: GATE-03 closed: full non-regression sweep re-run at the phase final commit under both devcontainer (3.12.13) and uv-provisioned CI-parity Python 3.11.15; 1134 passed/0 failed both interpreters
- [Phase ?]: DEVTEST-01/02/03/04 and GATE-01 independently re-verified against the live tree and ticked, per orchestrator-resolved ambiguity overriding the plan's stale Tick-GATE-03-only text
- [Phase ?]: py3.9 pytest impossibility reproduced live (syrupy>=5.0 needs >=3.10); py3.9 claim rests on config-pinned ruff/mypy + packaging classifier, not a test run
- [Phase 122]: 122-01: FIRESTARTER_CLAIMSCAN_TARGETS uses os.environ.get with no default so absent-vs-empty is unambiguous (None=defaults, empty string=zero targets, fail closed)
- [Phase 122]: 122-01: check_permitted_claims.py's own docstring states a green run is only the mechanizable half of ROADMAP criterion 4, never sufficient alone
- [Phase 122]: 122-02: D-05 recorded ACCEPT for the beta-push auto-fire; live pre-flight re-measurement matched 122-RESEARCH.md with zero divergence
- [Phase 122]: Whole-file --ours resolution applied to exactly submit.py and test_submit.py; empty-diff proof (0 bytes pre- and post-commit) taken as sole acceptance criterion for the app inbound merge
- [Phase 122]: Firmware inbound merge required no resolution decision — conflict-free per live re-probe, matching C-1 exactly
- [Phase 122]: Task 3's literal automated verify (test -z on submodule status --porcelain) is over-strict against the expected unstaged gitlink drift documented in 122-DECISION.md; relied on the more precise acceptance_criteria wording (no staged change) instead — no fix applied, documented as a finding
- [Phase ?]: Investigated 1134-vs-1150 app pytest delta via git log; traced to a documentation inconsistency in prior phase-122 artifacts (true pre-merge baseline is 1134, per Phase 121's own record), not a regression
- [Phase ?]: Cited REQUIREMENTS.md's forbidden claim by file:line instead of quoting it verbatim in 122-NONREGRESSION.md, since the exact wording is the claim-scanner's own trigger phrase and fails the scanner regardless of quotation context
- [Phase 122]: 122-05: nine claim-class rows written instead of D-11's 'roughly eight' -- the timing claim splits into the emitter measurement (gating) and the page-load measurement (context-only), different sources and dispositions
- [Phase 122]: 122-05: the C-5/D-14 No-Hazmats divergence is recorded in 122-LEDGER.md as an explicit flagged, traceable, overturnable item for Plan 122-11's operator wording review -- not silently corrected
- [Phase ?]: D-10 EIGHTH CORRECTION: gh#11 community reproduction of the exact predicted INIT abort on real AT28C256 raises TRACE-06 to community-corroborated while the fix stays unproven; 0x0D stays UNVERIFIED, zero support_status changes
- [Phase ?]: C-5/D-14 divergence flagged in PROJECT.md item 3 — RESOLVED at plan 122-11's D-16 wording review, operator ruled ACCEPT (see the 122-11 decision entry below)
- [Phase ?]: D-05 accepted: outbound merge pushed to beta in both sub-repos; CI cut 3.0.0b14 in both (firmware verified green first; app hit a standalone-CI test gap, fixed inline, and re-cut). Recorded in 122-CUT.md.
- [Phase 122]: Operator authorization for the PyPI publish and both-channels verification was pre-granted by the orchestrator with explicit evidence (b14 live both repos, PyPI still b13, C-3's 46% miss rate); verbatim response 'Publish to PyPI' recorded in 122-08-SUMMARY.md
- [Phase 122]: Operator approved all five 122-11 closing artifacts as written (2026-07-30); C-5/D-14 divergence ruled ACCEPT, corrected size-class No-Hazmats answer is final
- [Phase ?]: Operator final go/no-go verdict, verbatim: "Post it — all four calls."
- [Phase ?]: Both gh release edit / gh issue comment calls used --notes-file / --body-file exclusively; no inline string form was ever constructed
- [Phase ?]: Neither henols/firestarter_prom issue was closed and no label flag was ever sent (D-13) - both remain OPEN with zero labels
- [Phase 122]: CLOSE-01/02/03 ticked only after clause-by-clause re-verification against REQUIREMENTS.md's own prose (Plan 122-13) — the only plan in Phase 122 permitted to tick a requirement checkbox
- [Phase 122]: Phase 122 gitlink bump, the v1.22 annotated tag, the main-branch merges, and the stable release are all deliberately left for /gsd-complete-milestone (D-07); Plan 122-13 asserts the gitlinks still read 0048b3d/96e0622 with nothing staged
- [Phase 122]: Criterion 4 (community non-overclaim) is recorded as a three-way split: the green check_permitted_claims.py scan is the mechanizable half only, the D-16 operator wording review is the judgement half, and 'SDP works on real AT28C silicon' has a sampling rate of zero, permanently, by design
- [Phase 123-01]: Recorded firmware_tree_sha as the fork-point SHA (5c9160a), the actual HEAD at measurement time, not the later fixture-commit SHA
- [Phase 123-01]: captured_native_warnings_excerpt.log documents real pio-test framing (Processing/Building) rather than the plan's assumed 'Compiling .pio/build/...' line, which pio test never emits (verified default/-v/-vvv on a clean rebuild)
- [Phase 123]: Reused FIRESTARTER_CLAIMSCAN_TARGETS env-var name across phase dirs per RESEARCH A3 (checkers never coexist in one process)
- [Phase 123]: D-16 implemented as a 3-line window (PROXIMITY_WINDOW=1) over line-scoped matching, not sentence segmentation
- [Phase 123]: D-15 arming (UNARMED/armed-incomplete) applies only to the default-target path; argv/env-seam targets keep the ordinary fail-closed guard
- [Phase 123]: check_size_baseline.py uses manual argv parsing (no argparse) to stay strictly stdlib-only, matching the check_permitted_claims.py house convention
- [Phase 123]: check_uno_ram.sh deletion recorded as superseding an already-red gate (floor 545 B vs measured 475 B free), referenced by no workflow in either sub-repo
- [Phase ?]: 123-07: Used RESEARCH Mechanism 1 (committed tree without .git marker + tmp_path-materialised marker) for the fake firmware sibling fixture, per D-12; CONTEXT's .git-gitfile workaround was confirmed not to work
- [Phase ?]: AVR FAIL messages name the offending macro(s), added during Task 3 to satisfy the end-to-end anti-hollow test
- [Phase ?]: planted_build_warnings_native_excess.log required 361 appended synthetic lines (not a small number) since the truncated captured_test_native_summary.log base carries 0 real warnings
- [Phase ?]: PlatformIO-invisibility verified via test_filter entry counts (17 per native env), not pio test --list-tests, which enumerates all on-disk suite dirs (18) regardless of test_filter
- [Phase 123-08]: Rekeyed all 7 proxy-carrying host test modules onto tests.fw_presence.requires_fw (24 decorator legs + 1 non-decorator inline guard promoted to a decorator); every per-module reason= string and FW_ABSENT-shaped constant removed
- [Phase 123-08]: Created tests/scan_paths.py (D-11) covering both cross-repo populations; verifying RESEARCH's 11 tool files individually found 7 of them are same-repo package look-alikes, not cross-repo resolvers, despite matching the grep that found them
- [Phase 123]: PATH_RE requires a (?!\w) boundary after the recognised extension so a greedy backtrack can never misclassify CMAKE_TOOLCHAIN_FILE's .cmake as a bogus .c source entry
- [Phase 123]: Missing/unparseable manifest under an armed key, and an unrecognised source-list name, both exit 2 (config/parse error class), consistent with this phase's other two checkers
- [Phase 123]: 123-09: ALLOWED_SKIP_REASONS seeded with all four known-legitimate skip reasons found by static inspection (not only ones observed in this 0-skip local run), since two are standalone-CI-only conditions that would otherwise trip the census the first time it runs in GitHub Actions
- [Phase 123]: 123-09: census liveness signal switched from the run's trailing summary line to a --collect-only per-file count sum, after measuring pytest 9.1.1 in this environment intermittently omits that trailing line from captured stdout under -q
- [Phase ?]: Arming reading (a) chosen over (b) for BASE-05: gate is UNARMED until platform/py32f071/ exists, matching D-07 literally; rejected always-armed reading recorded in the docstring
- [Phase ?]: Comment mentions do not count as consumers for check_orphan_provisional.py -- bundled with #undef exclusion as one defect class per threat T-123-05-01, implemented via a comment-stripping pass before the consumer regex
- [Phase ?]: RURP_PY32F071_PINMAP_CONFIGURED structurally-dead #error is explicitly out of check_orphan_provisional.py's scope -- MERGE-04's problem, not BASE-05's
- [Phase ?]: Scoped BASE-08 checker-convention meta-test to firestarter/scripts/check_*.py only (non-recursive), naming the 3 pre-existing firestarter_app/tools/ violators (incl. check_mypy_watermark.py's missing test) in the docstring rather than allow-listing or fixing them
- [Phase ?]: 123-11: cited REQUIREMENTS.md's forbidden-claim list by location (not verbatim) in 123-NONREGRESSION.md to avoid tripping check_permitted_claims.py's own courtesy claim-scan, matching 122-NONREGRESSION.md's precedent
- [Phase ?]: 123-11: both native envs re-confirmed agreeing at 141 cases / 17 suites on a fresh build; MERGE-06 remains satisfiable as worded, no amendment needed for Phase 124
- [Phase 124]: 124-01: Violation counting is per violating commit, not per marker, in check_landing_range.py (matches the plan's own FAIL: 1 acceptance criterion and RESEARCH's measured true-merge figure)
- [Phase 124]: 124-01: ScanError caught only at the __main__ entry point in check_landing_range.py, never inside main() itself
- [Phase ?]: MERGE-05 band mode: leonardo effective band=0, uno-class band=MERGE05_UNO_CLASS_FLASH_BAND(64), single named constant governs the uno-class rule while leonardo's stricter must-not-grow rule reuses band=0 locally
- [Phase ?]: BASE-01 frozen byte-identically as size_baseline_base01.json (blob SHA b940c91655600a57ad7ef67cba723943af929daf) so Plan 124-10's re-baseline of size_baseline.json cannot move MERGE-05's reference point
- [Phase 124]: Phase 124 Plan 03: grep -c 'pytest.skip|mark.skipif' cannot be reduced below 2 in test_golden_trace_identity.py -- the self-check must contain the exact patterns it searches for as startswith() arguments; reduced from a naive 7 by rewording all non-functional prose, documented as a structural discrepancy analogous to 124-02's shell=True grep finding
- [Phase ?]: 124-04: squash tree proven byte-identical to true-merge tree in scratch clone; landing e2c422d has 0 Criterion-1 violations; ad47c3b confirmed non-ancestor (D-07 held)
- [Phase ?]: 124-04: all AVR flash/RAM and native 141/17 counts match RESEARCH's predicted post-landing figures exactly; MERGE-05/MERGE-06 pass by exit code; five expected-red gates (W-1..W-5) fired for their pre-declared owners

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
| Phase 117 P01 | 12min | 3 tasks | 3 files |
| Phase 117 P02 | 15min | 3 tasks | 2 files |
| Phase 117 P03 | 20min | 2 tasks | 2 files |
| Phase 117 P04 | 25min | 1 tasks | 1 files |
| Phase 117 P05 | 24min | 2 tasks | 2 files |
| Phase 118 P01 | 55min | 3 tasks | 3 files |
| Phase 118 P02 | 25min | 3 tasks | 5 files |
| Phase 118 P04 | 20min | 3 tasks | 1 files |
| Phase 118 P05 | 55min | 3 tasks | 3 files |
| Phase 118 P06 | 45min | 2 tasks | 2 files |
| Phase 118 P07 | 25min | 2 tasks | 2 files |
| Phase 119 P01 | 10min | 2 tasks | 6 files |
| Phase 119 P02 | ~35min | 3 tasks | 9 files |
| Phase 119 P03 | 25min | 2 tasks | 3 files |
| Phase 119 P04 | 55min | 3 tasks | 5 files |
| Phase 119 P05 | ~50min | 3 tasks | 2 files |
| Phase 119 P06 | 45min | 3 tasks | 3 files |
| Phase 119 P07 | ~25min | 3 tasks | 7 files |
| Phase 119 P08 | 55min | 3 tasks | 3 files |
| Phase 119 P09 | ~20min | 2 tasks | 5 files |
| Phase 119 P10 | ~50min | 3 tasks | 2 files |
| Phase 119 P11 | 50min | 2 tasks | 1 files |
| Phase 120 P01 | 15min | 3 tasks | 2 files |
| Phase 120 P02 | 10min | 2 tasks | 1 files |
| Phase 120 P03 | 12min | 2 tasks | 2 files |
| Phase 120 P05 | 20min | 2 tasks | 1 files |
| Phase 120 P06 | 20min | 3 tasks | 2 files |
| Phase 120 P07 | 45min | 3 tasks | 5 files |
| Phase 120 P08 | 55min | 3 tasks | 4 files |
| Phase 120 P09 | 35min | 3 tasks | 3 files |
| Phase 120 P10 | 45min | 3 tasks | 8 files |
| Phase 120 P12 | 55min | 3 tasks | 3 files |
| Phase 121 P11 | 30min | 3 tasks | 2 files |
| Phase 121 P12 | 35min | 2 tasks | 5 files |
| Phase 121 P13 | 50min | 2 tasks | 9 files |
| Phase 121 P14 | 110min | 3 tasks | 2 files |
| Phase 122 P01 | 15min | 3 tasks | 6 files |
| Phase 122 P02 | 20min | 2 tasks | 1 files |
| Phase 122 P03 | 7min | 3 tasks | 4 files |
| Phase 122 P04 | 25min | 3 tasks | 1 files |
| Phase 122 P05 | 35min | 3 tasks | 1 files |
| Phase 122 P06 | 35min | 2 tasks | 1 files |
| Phase 122 P07 | 47min | 3 tasks | 3 files |
| Phase 122 P08 | 20min | 3 tasks | 1 files |
| Phase 122 P09 | 12min | 3 tasks | 3 files |
| Phase 122 P10 | 25min | 3 tasks | 2 files |
| Phase 122 P11 | 20 | 3 tasks | 1 files |
| Phase 122 P12 | 25min | 3 tasks | 1 files |
| Phase 122 P13 | 35min | 3 tasks | 3 files |
| Phase 123 P01 | 9 | 3 tasks | 8 files |
| Phase 123 P10 | 20min | 3 tasks | 7 files |
| Phase 123 P02 | 20 | 3 tasks | 6 files |
| Phase 123 P07 | 45min | 3 tasks | 5 files |
| Phase 123 P03 | 30 | 3 tasks | 6 files |
| Phase 123 P08 | 70min | 3 tasks | 9 files |
| Phase 123 P04 | 35 | 3 tasks | 20 files |
| Phase 123 P09 | 55min | 2 tasks | 4 files |
| Phase 123 P05 | 22 | 2 tasks | 10 files |
| Phase 123 P06 | 12min | 2 tasks | 1 files |
| Phase 123 P11 | 55 | 3 tasks | 3 files |
| Phase 124 P01 | 12min | 2 tasks | 4 files |
| Phase 124 P02 | 10min | 3 tasks | 6 files |
| Phase 124 P03 | 22min | 2 tasks | 2 files |
| Phase 124 P04 | 20min | 3 tasks | 22 files |

## Session

**Last session:** 2026-07-31T09:01:34.700Z
**Stopped at:** Completed 124-04-PLAN.md (THE LANDING)
**Resume file:** 
None

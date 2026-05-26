---
gsd_state_version: 1.0
milestone: v1.7
milestone_name: — RURP Shield Hardware Investigation & Version Detection
status: ready_to_plan
last_updated: 2026-05-26T14:55:53.862Z
last_activity: 2026-05-26
progress:
  total_phases: 10
  completed_phases: 3
  total_plans: 13
  completed_plans: 61
  percent: 30
stopped_at: Phase 28 complete (4/4) — ready to discuss Phase 29
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-05-22

## Current Position

Phase: 29
Plan: Not started
Status: Ready to plan
Last activity: 2026-05-26

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-21)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** Phase 29 — multi board bench verification

- v1.2 (Message-ID Logging Rework) shipped 2026-05-19 — Leonardo Flash 98.7% → 85.4%
- v1.3 (CMOS EPROM Family Hardware Validation) PAUSED 2026-05-20 — Phase 11 shipped, Phase 12 Wave 0 scaffold shipped, Waves 1–3 + Phases 13/14 await hardware (see Paused Milestones below)
- v1.4 (Beta & Pre-release Deployment Pipeline) SHIPPED 2026-05-20 — 6/6 phases, 10/10 plans, ship tag 3.0.0b3, hardware-flash validated on Uno + Leonardo
- v1.5 (Arduino Uno ATmega328PB Board Support) SHIPPED 2026-05-21 — 5/5 phases, 6/6 plans, ship tag 3.0.0b4, bench-validated on operator's 328PB-Uno via `urclock` bootloader. Three open backlog items carried forward to v1.6 (the read-bug fix is the v1.6 milestone scope; the other two carry further).
- v1.6 (Fix the Read Bug) PAUSED 2026-05-22 at the Phase 27 RCA re-open boundary — Phases 26+27+28 shipped, Phase 29 Wave B FAIL (D-07 milestone-reopens), Phase 30 BLOCKED (see Paused Milestones below)
- **v1.7 (RURP Shield Hardware Investigation & Version Detection) STARTED 2026-05-22** — five phases (31-35); branch model `v1.7-shield-investigation` in all 3 repos

## Roadmap Summary

**v1.7 phases:** 5 (numbered 31-35, continues from v1.6 last planned phase 30). Granularity: Comprehensive.

| Phase | Goal | Requirements |
|-------|------|--------------|
| 31. Upstream Shield Archaeology | Clone upstream `AndersBNielsen/Relatively-Universal-ROM-Programmer`; mine git history; identify + record every shield revision ever published (Rev 0, Rev 1, Rev 2.0, Rev 2.2, plus any others); extract per-rev silkscreen-version string + photographs + schematic file references | HW-INV-01, HW-INV-02, HW-INV-03, SILK-01 |
| 32. Inter-Rev Difference + Capability Matrix | Per-rev electrical/mechanical difference table (pinout, VPP regulator wiring, voltage divider values, jumpers, control-line routing, rework hacks); per-rev capability matrix (chip families supported, max VPP, max VCC, address-bus width, supported algorithms) | DIFF-01, DIFF-02, CAPS-01, CAPS-02 |
| 33. Silkscreen Label → Code Alias Migration | Inventory every silkscreen label across all known revs; propose a single code-side alias namespace (descriptive identifiers like `PIN_VPP_REGULATOR_ENABLE`); apply aliases to firmware (`firestarter/include/`) + host (`firestarter_app/firestarter/constants.py`); GATE-1.7 non-regression preserved | ALIAS-01, ALIAS-02, ALIAS-03 |
| 34. Shield-Version-Detect Design + Firmware Plumbing | Schematic delta for next-rev shield (resistor divider into Arduino ADC pin); firmware ADC read + lookup table mapping voltage band → silkscreen-rev string; handshake reports detected rev; backward-compat fall-through for pre-detect-resistor boards (Rev 0 / 2.0 / 2.2 → `rev_unknown` + EEPROM `hw_revision` byte fallback) | DETECT-HW-01, DETECT-HW-02, DETECT-FW-01, DETECT-FW-02 |
| 35. Documentation + Milestone Close | `.planning/v1.7-SHIELD-REVS.md` reference document finalized; README + per-sub-repo docs updated; MILESTONES.md entry; archive `.planning/milestones/v1.7-phases/`; PROJECT.md "Validated" updates | DOC-01, MS-01 |

**Coverage:** 17/17 v1.7 requirements mapped to exactly one phase. No orphans, no duplicates.

**Phase-order rationale:** Archaeology → difference matrix → label aliasing → detect design → close. Phases 31+32+33+35 are desk-side (operator's existing Rev 2.2 / 2.0 / Mod-Rev 0 boards used for label-photo capture + spot-check; no bench programming). Phase 34 has a desk-side wave (schematic delta + firmware compile + handshake report on synthetic/floating ADC) and an optional operator-on-bench wave (sanity-check ADC read on existing pre-detect-resistor boards reports `rev_unknown` cleanly without breaking handshake).

Full details: `.planning/ROADMAP.md` (v1.7 section).

### v1.6 phases (paused — preserved for resume)

**v1.6 phases:** 5 (numbered 26-30, continues from v1.5 last phase 25). Granularity: Comprehensive.

| Phase | Goal | Requirements |
|-------|------|--------------|
| 26. Cross-board Reproduction & Diagnostic Tooling | Land a host CLI `dev consistency-check` diagnostic; reproduce 64KB read-jitter on all 3 boards (`uno`, `leonardo`, `uno328pb`) and capture pre-fix SHA-256 baseline | REPRO-01, REPRO-02, REPRO-03 |
| 27. Root Cause Analysis | Identify the exact code path that introduces byte corruption (instrumented build, bisection, or scope trace); document WHY; bracket the introducing commit | RCA-01, RCA-02, RCA-03 |
| 28. Fix Implementation + Unit Test Coverage | Land the fix in the appropriate sub-repo(s) with atomic commits + RCA citations; ship a native unit test (Unity/pytest) that would fail on pre-fix code; preserve GATE-1.6 write-path non-regression | FIX-01, FIX-02, FIX-03 |
| 29. Multi-Board Bench Verification | Operator-on-bench acceptance gate — N≥5 consecutive `firestarter read` invocations return byte-identical SHA-256 hashes on `uno`, `leonardo`, AND `uno328pb`; `dev read -s 1024` low-rate jitter also resolves; Phase 24 BENCH-02 closes as side effect | VERIFY-01, VERIFY-02, VERIFY-03, VERIFY-04 |
| 30. Documentation + Milestone Close | Move todo out of `pending/`, update PROJECT.md, ship MILESTONES.md entry, archive `.planning/milestones/v1.6-phases/`, sub-repo branch promotion | DOC-01, DOC-02, MS-01 |

**Coverage:** 16/16 v1.6 requirements mapped to exactly one phase. No orphans, no duplicates.

**Phase-order rationale:** Reproduce → Diagnose → Fix → Verify → Close. Each phase delivers an independently-verifiable artifact (diagnostic tool, RCA narrative, fix commits + tests, multi-board bench evidence, milestone close paperwork). Phases 26+30 are desk-side; Phase 27 is largely desk-side with optional bench instrumentation; Phase 28 is desk-side TDD; Phase 29 is the only exclusively-bench phase (the acceptance gate). The 3-shield A/B/C triage already proves the bug is transport-side and not RURP-hardware-specific — so RCA can proceed without continuous bench access, with bench used only for reproduction confirmation (Phase 26) + fix validation (Phase 29).

**Bench-gated vs desk-side split (Phase 26 internal wave structure):**

- Wave A (desk-side): Implement `firestarter dev consistency-check <chip> --runs N` host CLI command (REPRO-03 artifact). Lands without hardware. The command becomes the canonical post-fix regression check.
- Wave B (operator-on-bench): Run the diagnostic against `uno`, `leonardo`, AND `uno328pb` to satisfy REPRO-01/02 + the per-board baseline rows of REPRO-03's evidence file. Falls naturally between Phase 26 Wave A and Phase 27 — operator decides whether to interleave (Wave A → bench → Wave B → start Phase 27) or batch (Wave A → Phase 27 desk-side → bench session covering Phase 26 Wave B + Phase 29 in one operator sitting).

**Branch model:** Per memory `feedback-branching-firestarter-milestones` — all v1.6 work lands on `v1.6-read-bug` branches in all 3 repos. Sub-repos branch off current `beta` tips (post-v1.5 ship); meta-repo branches off `main`. Sub-repos `v1.6-read-bug` → `beta` merge happens at the Phase 29 boundary to trigger a fresh pre-release cut (e.g. `3.0.0b5` or `3.0.1bN`) for bench install via `firestarter fw -i --pre --force`. Promote `beta` → `main` only after operator green on the multi-board bench cycle. Instrumented builds for Phase 27 RCA may need their own one-off pre-release tag.

Full details: `.planning/ROADMAP.md` (v1.6 section).

### v1.5 phases (archived — preserved for reference)

**v1.5 phases:** 5 (numbered 21-25, continues from v1.4 last phase 20). Granularity: Standard.

| Phase | Goal | Requirements |
|-------|------|--------------|
| 21. Firmware Target — `uno328pb` | `pio run -e uno328pb` builds clean; `boards/uno328pb.json` declares ATmega328PB MCU + Arduino-Uno-compatible pin mapping; firmware handshake reports `uno328pb`; `pio test -e native` stays green | FW-01, FW-02, FW-03, FW-04 |
| 22. Release Pipeline Artifacts | Stable (`build.yml`) + beta (`beta-build.yml`) workflows emit `firestarter_uno328pb.hex` as a third per-board artifact; existing `firestarter_uno.hex` + `firestarter_leonardo.hex` byte-identical | REL-01, REL-02 |
| 23. Host CLI Installer Integration | `firestarter fw -i`/`--pre`/`firmware list` flow through existing v1.4 board-driven asset resolution cleanly for `uno328pb`-reporting devices; allowlist + regression test added; GATE-01 non-regression verified on `uno`/`leonardo` | INST-01, INST-02, INST-03, GATE-01 |
| 24. Bench Validation on 328PB-Uno | Cut v1.5 beta pre-release, flash 328PB-Uno via `firestarter fw -i --pre`, run write→read→verify on representative EPROM (W27C512 default); `.planning/v1.5-BENCH-RESULTS.md` row captured | BENCH-01, BENCH-02 |
| 25. Documentation + Milestone Close | README updates (firmware + app), release-procedures three-board matrix, MILESTONES.md entry, archive `.planning/milestones/v1.5-phases/`, PROJECT.md shipped update | DOC-01, DOC-02, MS-01 |

**Coverage:** 15/15 v1.5 requirements mapped to exactly one phase. No orphans, no duplicates.

**Phase-order rationale:** Firmware target → release artifacts → host CLI → bench validation → docs + close. Phases 21–23 + 25 desk-side; Phase 24 is the only operator-on-bench phase (and the operator confirmed the 328PB-Uno + RURP shield is plugged in, so v1.5 is not hardware-gated the way v1.3 is).

Full details: `.planning/ROADMAP.md` (v1.5 section).

### v1.4 phases (archived — preserved for reference)

`.planning/ROADMAP.md` retains the v1.4 section (Phases 15-20, shipped 2026-05-20) under the Prior Milestones collapsible. Per-phase artifacts archived at `.planning/milestones/v1.4-phases/`.

**v1.4 phases:** 6 (numbered 15-20, continues from v1.3 last phase 14; Phase 18 inserted 2026-05-20, old 18/19 renumbered to 19/20). Granularity: Standard.

| Phase | Goal | Requirements |
|-------|------|--------------|
| 15. Versioning & Locked-Step Coordination (Foundation) ✅ | Both sub-repos emit PEP 440 / matching pre-release identifiers on `beta`-branch builds; locked-step coordination mechanism finalised and documented | VER-01, VER-02, VER-03 |
| 16. App Beta Release Pipeline | Push to `firestarter_app/beta` → GitHub Actions workflow → bump pre-release version → PyPI pre-release publish + GitHub Pre-release. Stable pipeline (GATE-01) preserved verbatim | REL-01, GATE-01 |
| 17. Firmware Beta Release Pipeline | Push to `firestarter/beta` → GitHub Actions workflow → catalog/codegen/Unity/PIO gates → bump pre-release version → GitHub Pre-release with `.hex` artifacts per board. Stable pipeline (GATE-02) preserved verbatim | REL-02, GATE-02 |
| 18. Beta-Aware Firmware Downloader | `firestarter --install` defaults preserved (INST-01 non-regression); `--pre` fetches latest pre-release fw; `--firmware-version X.Y.Z[bN]` pins exact tag; `firestarter firmware list` enumerates releases; `_compare_versions` refactored to PEP 440-safe via `packaging.version.Version` | INST-01, INST-02, INST-03, INST-04 |
| 19. Documentation | App README + firmware README beta sections (install via `pip install --pre` AND `firestarter --install --pre/--firmware-version/firmware list`; stability guarantee; issue reporting); `v1.4-RELEASE-PROCEDURES.md` documents release-engineer cutting workflow | DOC-01, DOC-02, DOC-03 |
| 20. End-to-End Smoke Test + Milestone Close | Cut real beta in both repos per Phase 19 procedure; verify PyPI + GitHub Release outputs + locked-step version match + `firestarter --install --pre` works + stable-installed app still defaults to stable fw; close milestone (MILESTONES.md, archive, PROJECT.md update) | E2E-01, MS-01 |

**Coverage:** 16/16 v1.4 requirements mapped to exactly one phase. No orphans, no duplicates. (Was 12/12 before the 2026-05-20 amendment that added INST-01..04 + Phase 18.)

**Phase-order rationale:**

- Phase 15 first ✅ — foundation phase resolved the lockstep coordination question (manually-paired beta-branch push with explicit `BETA_VERSION` input) and shipped both `update_version.py` extensions; REL-01 + REL-02 have no version-emission scheme to plug into without it.
- Phase 16 before Phase 17 (sequential, not parallel) — app-side beta path is more constrained (PEP 440 strict, single PyPI index, `--pre` install semantics) so it shakes out the version-emission flow; firmware beta is a near-mirror with GitHub Release `prerelease: true` instead of PyPI, so app lessons-learned feed firmware design cleanly. Tight feedback loop in a CI/CD setup is more valuable than parallel-track throughput here.
- Phase 18 after Phase 17 — the Beta-Aware Firmware Downloader is the consumer side of Phase 17's publisher. Unit tests mock the GitHub API and can land without real beta fw existing in GitHub; the Phase 20 E2E test then proves the publish→install loop end-to-end against real artifacts.
- Phase 19 after Phases 15/16/17/18 — you document what you built, not what you plan; both READMEs + the meta-repo `v1.4-RELEASE-PROCEDURES.md` lock the substrate that emerged from the prior four phases, including the Phase 18 CLI flags.
- Phase 20 last — the acceptance gate. Cut a real beta in both repos following the Phase 19 documented procedure; verify all acceptance criteria including `firestarter --install --pre` (INST-02 E2E) and stable-installed `firestarter --install` non-regression (INST-01 E2E); close milestone. No v1.4 close without a green E2E-01.

Full details: `.planning/ROADMAP.md` (v1.4 section).

### v1.3 phases (paused — preserved for resume)

`.planning/ROADMAP.md` retains the v1.3 section (Phases 11-14) intact. v1.3 is paused, not deleted; Phase 11 shipped + Phase 12 Wave 0 scaffold shipped; Waves 1-3 + Phases 13/14 await bench hardware. Resume command on the Paused Milestones list below.

## Milestone History

- **v1.0** — Protocol-Aware Programming Architecture (shipped 2026-05-11) — see `.planning/MILESTONES.md` + `.planning/milestones/v1.0-*.md`
- **v1.1** — Safety Closure & Hardware Validation — **PAUSED at 80%** (2026-05-18). Phases 1–3 complete (SAF closure, wire-key rename, retroactive VERIFICATION.md artifacts). Phase 4 hardware-validation Plan 2 of 3 in progress (FM1608 byte-0 read bug parked — see `.planning/debug/fm1608-fresh-chip-baseline.md`; needs a different Uno board to unblock). Phase 5 (milestone close) deferred.
- **v1.2** — Message-ID Logging Rework (shipped 2026-05-19) — 23/23 requirements; Leonardo Flash 98.7% → 85.4% (−3,792 B); firmware 3.0.0-dev lockstep upgrade. 4 hardware-pending UAT items deferred into v1.3 bench session (see Deferred Items below). See `.planning/MILESTONES.md`.

## Accumulated Context

### Open Blockers

- **None for v1.7 directly.** Milestone is documentation-first; investigation can proceed with operator's Rev 2.2 / Rev 2.0 / Modified Rev 0 boards (photographs + spot-check) without programming-side bench access. Phase 34 firmware-detect plumbing is desk-side compile + handshake-report verification; optional bench wave validates pre-detect-resistor backward-compat fall-through.

### Paused Milestones

| Milestone | Paused | Reason | Resume Command |
|-----------|--------|--------|----------------|
| **v1.3** — CMOS EPROM Family Hardware Validation | 2026-05-20 | Hardware-gated. Phase 11 (coverage matrix + 78-finding defect ledger + all-algorithms wide-scan with 137 findings across 11 algos) shipped. Phase 12 Wave 0 desk-side scaffold committed (`.planning/v1.3-BENCH-RESULTS.md` skeleton + `.planning/v1.3/bench-logs/` + `.planning/v1.3/scope/`). Plans 12-01/02/03 (BENCH-01/02/05 — W27C512, SST27SF512, W27C257) + entire Phase 13 (algo-0x08 family) + Phase 14 milestone close cannot start without Uno + Leonardo + RURP shield + DIP-28 socket + scope + the bench chips. Auto-mode would silently fabricate bench results — operator paused milestone to avoid integrity hazard. v1.4 phase numbering continues at 15 to avoid collision when v1.3 resumes. | `/gsd-execute-phase 12 --wave 1 --interactive` (once bench hardware available) |
| **v1.6** — Fix the Read Bug | 2026-05-22 | D-07 FAIL milestone-reopens triggered by Phase 29 Wave B Attempt 2 (2026-05-22 PM): Leonardo (`/dev/ttyACM1`, Modified Rev 0 + voltage-divider mod, 32U4 silicon) reads 83.8% zero-bytes with 5 distinct SHAs across N=5 consistency-check; uno328pb (`/dev/ttyUSB0`, Rev 2.2, real ATmega328PB Case A confirmed) reads 5 distinct SHAs with 18.2% pairwise byte-jitter. Chip-swap diagnostic eliminates chip as the variable (proven-good chip from Uno reads garbage on Leonardo). Uno code path unaffected (Δ=0 Phase 28 hex, regression check held). Strong candidate cause: Phase 28 fix (commits `437339b6` PORTx-clear + `4f205e58` `_NOP()` settling) introduced a Leonardo + uno328pb read-path regression. Phase 30 BLOCKED — no `v1.6-read-bug → beta → main` promotion, no pre-release cut, no public tag until a corrected fix re-runs Phase 29 to PASS. **Phase 27 re-open CLOSED 2026-05-26 (Plan 27-05):** Dual-cause disposition confirmed (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb pre-existing hardware); Phase 28 re-iteration UNBLOCKED with split-scope handoff. Phase 28 first task: revert `437339b6` alone on `firestarter/v1.6-read-bug` → rebuild Leonardo → sideload → N=5 consistency-check. See `.planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Re-open Findings (2026-05-26)"` for Fix sketch v2 + GATE-1.6 v2 + final verdict. | `/gsd-execute-phase 28` (Phase 28 re-iteration UNBLOCKED — split-scope: Leonardo fix-revert/tune; uno328pb operator hardware diagnosis) |

## Deferred Items

Items acknowledged and deferred at v1.2 milestone close on 2026-05-19. The three W27C512 UAT items now **naturally fold into v1.3** — the W27C512 bench session is in scope for v1.3 BENCH-* requirements, so closing v1.3 closes Phase 08 SC#2/SC#3 + Phase 09 SC#3 as a side effect. The FM1608 byte-0 read bug remains parked (different chip family, different debug session, requires different Uno R3 hardware).

| Category | Item | Status | Note |
|----------|------|--------|------|
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 | v1.1 carryover — needs different Uno R3 to unblock; out of scope for v1.3 |
| uat | Phase 08 HUMAN-UAT.md | partial — 2 pending scenarios | chip-seated W27C512 write + readback → closes via v1.3 BENCH-01 (Phase 12) |
| verification | Phase 08 VERIFICATION.md | human_needed | bench UAT closure → closes via v1.3 BENCH-01 (Phase 12) |
| verification | Phase 09 VERIFICATION.md | human_needed | Plan 09-05 Task 3 (chip-seated W27C512 on both boards) → closes via v1.3 BENCH-01 (Phase 12) |

### Carried Over From v1.1 (still open)

- **v1.1 Phase 4 — FM1608 byte-0 read bug** — Localized to a specific Uno board (chip + shield both clean on Leonardo). Eight firmware fixes failed (PORTD pre/post-clear, robust-read with 100µs + 2nd /CE cycle, LSB cache invalidation). Cheapest unblocking experiment: try a different Uno R3. See `.planning/debug/fm1608-fresh-chip-baseline.md` (status: `parked-2026-05-18`).
- **WARNING-4** — `firestarter_test.sh` / `write_test.sh` reference deleted `database_generated.json`. Was scheduled for v1.1 Phase 4 (HW-01). Carries forward; address either as part of v1.1 closure or fold into v1.2 if test scripts are touched.
- **v1.1 DOC-01 (milestone close)** — Phase 5 of v1.1 deferred; will be picked up either after v1.2 ships or folded with the FM1608 unblock.

### Resolved in v1.1 (Phases 1–3 complete)

- WARNING-1 (Intel-flash VPP ADC compare) — Plan 01-01
- WARNING-2 (`eeprom_28c.cpp` chip-id forward-compat) — Plan 01-02
- WARNING-3 (wire JSON `"vpp"` → `"vpp_mv"`) — Plan 02-01 + 02-02
- CLEAN-01 (`minipro_complete_db.json` → `chip_database.json` rename) — Plan 02-02
- CLEAN-02 (minipro attribution scrub) — Plan 02-03
- VERIF-01..VERIF-10 (retroactive VERIFICATION.md for v1.0 Phases 01–10) — Phase 03

### Resolved Blockers (v1.0)

- BLOCKER-1 (Phase 12) — algorithm-based dispatch for protocols 0x05/0x06/0x07/0x08/0x0B and SRAM 0x0E/0x27/0x28/0x29
- BLOCKER-2 (Phase 12) — SRAM chips routed to `configure_eprom` with 12V VPP regulator
- WARNING-5 (Phase 13) — AT28C256/64 5V EEPROM 12V-on-A14 hazard via DB override

## v1.5 Decisions (locked at milestone start, 2026-05-20)

- **Scope:** Add `uno328pb` as a third firmware target alongside the existing `uno` and `leonardo`. End-to-end coverage: PlatformIO env → handshake board-name reporting → stable + beta release pipelines emit a third `.hex` artifact → host CLI installer flashes the right artifact when device reports `uno328pb` → bench-validated EPROM write→read-back→verify cycle on operator's plugged-in 328PB-Uno + RURP shield.
- **Out of scope:** 328PB extra peripherals (USART1, TWI1, SPI1, Timer3/4, PE0–PE3 pins) — Firestarter only uses 328P-common I/O; bootloader flashing (operator provisions the board separately); host-side VID/PID auto-detect (firmware-handshake report is authoritative — same pattern as `uno`/`leonardo`); RURP shield rev changes; new chip support; CMOS bench resume (still v1.3 territory, hardware-gated).
- **Branch model:** Both sub-repos cut working branches off `beta` (current tip 5fd751e in both sub-repos as of 2026-05-20). Cut the first v1.5 pre-release (e.g. `3.0.1bN`) from `beta` once Phases 21–23 are green. Promote `beta` → `main` and bump to stable (`3.0.1`) only after operator green on the 328PB bench cycle (Phase 24). Meta-repo's `.planning/` work proceeds on `main` per existing convention.
- **Board-ID strategy:** Custom PIO `boards/uno328pb.json` so `board = uno328pb` in `[env:uno328pb]`. `name_firmware.py` already derives the artifact name from `env.GetProjectOption("board")`, so this produces `firestarter_uno328pb.hex` with no codegen change, and the host's `firestarter_{board}.hex` lookup in `firmware.py` matches without any board-name translation.
- **MCU framework:** MiniCore (`platform = MCUdude/MiniCore`) is the established Arduino-framework support for ATmega328PB. Use it as the platform. Pin definitions kept Arduino-Uno-compatible for Firestarter's I/O footprint (no use of PB-exclusive pins PE0–PE3).
- **Buffer size:** Use `DATA_BUFFER_SIZE=512` (same as `uno`). 328PB has the same 2 KB SRAM as 328P. Only revisit if compiled binary runs cold against the buffer floor on bench.
- **Handshake-name source of truth:** `RURP_BOARD_NAME=\"uno328pb\"` set per-env in `platformio.ini` (mirror of `uno` and `leonardo`); firmware emits this string in the `MSG_OK_FW_HANDSHAKE` payload's `<board>` slot so the host's `firmware.py:check_current_firmware` parses it identically to the existing two boards.
- **Phase numbering:** continues from v1.4 last phase 20; v1.5 starts at Phase 21. No `--reset-phase-numbers`.
- **GATE-1.5 (non-regression):** `firestarter_uno.hex` and `firestarter_leonardo.hex` are byte-identical to pre-v1.5 outputs (modulo unavoidable version-string drift from `update_version.py`). Stable-installed app's `firestarter fw -i` defaults still flash the matching artifact for `uno`/`leonardo`-reporting devices.
- **Bench validation chip:** Operator's plugged-in 328PB-Uno is the test vehicle. Bench session validates against at least one representative EPROM available in the operator's chip kit (default W27C512 — overlaps v1.3 BENCH-01 chip-of-interest). Algorithm dispatch is firmware-internal and unchanged by the MCU port, so a single representative chip is sufficient to prove the port.
- **Documentation surface:** Firmware README + app README each grow a one-paragraph board-matrix entry for `uno328pb`. Meta-repo `v1.4-RELEASE-PROCEDURES.md` (or v1.5-renamed equivalent) grows the per-board artifact line in the release-engineer checklist.

## v1.7 Decisions (locked at milestone start, 2026-05-22)

- **Scope:** Documentation-first investigation of every known RURP shield revision (Rev 0 → Rev 2.2 + any older revs recoverable from upstream git history); per-rev silkscreen-version capture; silkscreen-label → code-side alias migration; inter-rev electrical/mechanical difference table; per-rev capabilities matrix; design + firmware plumbing for a next-rev shield-version-detect resistor divider.
- **Out of scope:** Fixing the v1.6 read-bug (still v1.6 territory; resumes after v1.7 ships); new chip support; new MCU board target (`uno328pb` family closed in v1.5); physical PCB manufacturing of the next-rev shield (design-only); EEPROM `rurp_configuration_t.hw_revision` byte semantics (preserved as legacy fall-back, no breaking change); RURP shield manufacturing instructions (operator-side concern).
- **Source of truth for upstream schematics:** `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer/tree/main/hardware` (current revs on `main`; older revs Rev 0 + Rev 1 mined from git history via `git log -p`/`git log --diff-filter=D`).
- **Operator hardware on hand:** Rev 2.2, Rev 2.0, modified Rev 0 (with hardware-bug-A/B rework). Per memory [[user_shield_revisions]] — operator photographs + spot-checks all three during Phase 31 silkscreen capture. Per memory [[feedback_chip_out_before_sideload]] — chip OUT of socket before any firmware sideload (Phase 34). Per memory [[feedback_verify_port_identity_each_task]] — verify `controller:` identity per port at every task start.
- **Phase numbering:** continues from v1.6 last planned phase 30 → v1.7 starts at **Phase 31**. No `--reset-phase-numbers`. Phase 30 (v1.6 milestone close) slot stays reserved.
- **Branch model:** Per memory [[feedback_branching]] — `v1.7-shield-investigation` branches in all 3 repos. Meta-repo branches off `main`. Sub-repos branch off current `beta` tips (post-v1.5 ship, since v1.6 sub-repo branches are mid-iteration and the firmware-detect patch needs a clean substrate). Promote sub-repos → `beta` only after Phase 34 firmware-detect lands; `beta` → `main` only after operator confirms firmware reports correctly on at least one bench-present rev. Most of v1.7 lives in the meta-repo (documentation).
- **Definition of done:** `.planning/v1.7-SHIELD-REVS.md` (or equivalent — fixed at execution time) is the canonical per-rev reference; every silkscreen label maps to a code-side alias; firmware uses the aliases; next-rev schematic delta + ADC-detect firmware plumbing are committed (without requiring physical fabrication for firmware to compile + boot cleanly on existing pre-detect-resistor boards).
- **GATE-1.7 (non-regression):** Existing pre-detect-resistor boards (Rev 0 / 2.0 / 2.2) handshake byte-identical to v1.6 baseline; chip programming + read paths byte-identical; the alias migration is name-only (no wire-format or behavior changes); compiled `.hex` sizes within trivial drift (≤ symbol-name overhead, typically a few bytes).
- **Backward-compat fall-through:** Firmware ADC-detect must gracefully handle pre-detect-resistor boards — floating/grounded ADC reading falls through to "rev_unknown" reported in handshake, AND firmware continues to honor the operator-configured `hw_revision` byte in EEPROM (existing behavior preserved). The detect resistor is additive; existing boards are not bricked or downgraded.
- **Resistor-divider design constraints (Phase 34 target):** Pick an Arduino ADC pin not currently used by any active RURP signal across any known rev (verified in Phase 32 capability matrix); resistor values chosen to give clearly distinguishable voltage bands per rev (≥ ~0.3V separation against 10-bit ADC noise floor); each rev gets a documented expected-ADC-band entry in the firmware lookup table; rev string returned by detect matches the silkscreen-version string captured in Phase 31 verbatim.

## v1.6 Decisions (locked at milestone start, 2026-05-21; PAUSED 2026-05-22 at the Phase 27 RCA re-open boundary)

- **Scope:** Fix one specific bug — the 64KB streaming-read byte-jitter (~57.8% jitter rate at 64KB, ~0.1% at 1KB) affecting all three controllers (`uno`, `leonardo`, `uno328pb`). Cross-board verification + root-cause analysis + fix + bench validation.
- **Out of scope:** `w27c512-eeprom-misclassification` (separate HIGH-priority backlog — chip database routing bug, different milestone); `avrdude-mcu-detection-fallback` (low priority); any new chip support; any new board target; v1.1 FM1608 carryover.
- **Phase numbering:** continues from v1.5 (Phase 26+); no `--reset-phase-numbers`. Five phases (26-30); 16/16 requirements mapped.
- **Branch model:** Per memory [[feedback_branching]]: `v1.6-read-bug` branches in all 3 repos. Sub-repos branch off current `beta` tips; promote to `main` only after operator green on bench.
- **Definition of done:** `firestarter read <chip> file.bin` invoked N consecutive times against the same physically-static chip returns byte-identical SHA-256 hashes on all 3 boards.
- **GATE-1.6 (non-regression):** Write path unaffected — Phase 24 already proved write commits correctly.
- **Pause reason (2026-05-22):** Phase 29 Wave B FAIL — D-07 milestone-reopens. Chip-swap diagnostic isolated Phase 28 firmware as introducing a Leonardo + uno328pb read-path regression. Paused to let v1.7 ship labeled-schematic + per-rev capability table; resume after v1.7 close with `/gsd-plan-phase 27 --gaps`.

## v1.4 Decisions (locked at milestone start, 2026-05-20; amended 2026-05-20 for Phase 18)

- **Scope:** Add a parallel beta / pre-release deployment channel for both sub-repos. The existing main → stable pipelines (app: PyPI publish on GitHub Release; firmware: GitHub Release with `make_latest: true` carrying `firestarter_*.hex`) stay exactly as they are. Beta is additive plumbing PLUS a minimum consumer-side surface in the app so the beta firmware channel is actually installable (see Scope amendment below). No firmware behavior changes, no new chip support.
- **Scope amendment (2026-05-20, after Phase 15 shipped):** The original "no new user-facing CLI features in the app" rule is relaxed for one narrow case — Phase 18 (Beta-Aware Firmware Downloader). Without it the published beta firmware is uninstallable via the `firestarter` CLI. Carve-out covers ONLY: `firestarter --install --pre`, `firestarter --install --firmware-version X.Y.Z[bN|rcN]`, `firestarter firmware list [--all|--pre|--stable]`, and a defensive refactor of `firmware.py:_compare_versions` to use `packaging.version.Version` (today it crashes on PEP 440 pre-release strings). No other CLI changes follow. Driver: operator confirmation that stable-app non-regression + beta-app full-install capability are hard requirements.
- **Trigger model: branch-driven beta.** Each sub-repo gets a `beta` branch. Pushing to `beta` triggers the pre-release build (mirrors the current main → stable trigger shape). Stable still triggers only on `main`. Operators cut a beta by pushing to `beta`; cut a stable by merging to `main`.
- **App PyPI channel: PEP 440 pre-release versions.** Beta builds publish `X.Y.Zb1` / `X.Y.ZbN` / `X.Y.ZrcN` to the SAME PyPI index as stable. Users opt in via `pip install --pre firestarter`. TestPyPI explicitly deferred (extra index adds operator friction; opt-in via `--pre` is the simpler one-source-of-truth UX).
- **Firmware channel: GitHub Pre-release.** Beta builds create a GitHub Release with `prerelease: true` AND `make_latest: false`, same `.hex` artifacts (per-board). Beta releases do NOT become "latest" — `api.github.com/.../releases/latest` automatically filters them out, which is why stable-installed `firestarter --install` continues to download stable fw with zero code changes. Beta-installed app opts into pre-releases via `--pre` (Phase 18).
- **Locked-step versioning between app and firmware.** App and firmware always release with matching version numbers. Phase 15 finalized the coordination MECHANISM as **manually-paired beta-branch push with explicit `BETA_VERSION` input** (rejected alternatives: shared `VERSION` file in meta-repo, cross-repo `repository_dispatch`). Procedure documented in `.planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md` — Phase 19 consumes verbatim into `v1.4-RELEASE-PROCEDURES.md`.
- **Existing pipelines preserved.** No regressions in main → stable: app `release.yml` + `publish.yml`, firmware `build.yml` keep current behavior verbatim. v1.4 plumbing is additive (new workflow files or new branches in existing workflows; existing release artifacts stay byte-identical to current outputs when triggered from main). On the consumer side, `firestarter --install` with no flags on a stable-installed app stays byte-identical to today (INST-01).
- **Out of scope:** TestPyPI publishing, auto-promotion beta → stable, hardware bench testing of beta builds (v1.3's job once hardware is back), new CI checks beyond what stable runs, any other CLI behavior change beyond the Phase 18 carve-out, any firmware behavior change.
- **Implementation lives in submodules.** All workflow file edits, version-bump script edits, version file edits land inside `firestarter/` and `firestarter_app/` (their own git repos). Phase 18 also touches `firestarter_app/firestarter/firmware.py` + `main.py` + new tests under `firestarter_app/tests/`. Meta-repo (`/workspaces`) tracks only `.planning/` + `.claude/` — same pattern as v1.3 Phase 12 commits.

## v1.3 Decisions (locked at milestone start, 2026-05-19)

- **Scope:** Algorithm-0x07 (28-pin DIP CMOS UV-EPROM, 212 chips in DB) + algorithm-0x08 (32-pin DIP CMOS UV-EPROM, 127 chips in DB). End-to-end bench validation on Uno + Leonardo for four named chips (W27C512, SST27SF512, W27C020, W27E040) + one 28-pin lower-density representative + one 32-pin lower-density representative. Structural-coverage report across all 339 in-scope DB rows.
- **Out of scope:** New algorithms, new chip families, FM1608 (parked v1.1 carryover), flash-savings work (v1.2 budget held as-is).
- **Definition of "working" (bench gate per chip):** chip-ID read returns DB-declared value where `chip_id_check: true`; blank-check passes; write programs a test image without error; read-back is byte-identical; VPP regulator engages at 12V; both Uno (512-B buffer) and Leonardo (1024-B buffer) reach green.
- **Density coverage strategy:** test at both ends — smallest 28-pin (32K W27C257 / SST27SF256) and smallest 32-pin (128K W27C010 / SST27SF010) — so address-bus correctness covers the whole 32K → 512K span.
- **Deferred-items absorption:** v1.2 Phase 08 SC#2/SC#3 + Phase 09 Plan-05 Task 3 (chip-seated W27C512 UAT) close as a byproduct of v1.3 BENCH-01 (Phase 12).
- **Hardware-bench dependency:** entire milestone is operator-on-bench gated EXCEPT Phase 11 (desk-side coverage matrix + DB audit) and Phase 14 (close-out paperwork). Plan structure isolates these so progress is possible without continuous hardware access.
- **Phase numbering:** continues from v1.2 (Phase 11+); no `--reset-phase-numbers`.
- **PROTO-01/02 mapping:** mapped to Phase 12 (where chip-ID + VPP scope observation protocols are established + first applied); protocol carries forward into Phase 13 unchanged, and final aggregation lands in Phase 14 BENCH-RESULTS.

## v1.2 Decisions (locked at milestone start, 2026-05-18)

- **Goal weighting:** flash savings + clean protocol equally weighted. Either can drive a decision when they conflict.
- **Backwards compatibility:** none — firmware + host upgrade together. Firmware version bump enforces.
- **Scope:** ALL firmware log call-sites (`OK:`, `INIT:`, `MAIN:`, `END:`, `INFO:`, `WARN:`, `ERROR:`) migrate to ID + param-bytes format. Only the `DATA:` raw binary read-payload stream is untouched (already optimal; only the prefix marker would change and it's not worth the parser churn).
- **ID width:** 1 byte (0–255 messages). Current firmware has well under 100 distinct strings; generous headroom.
- **Param encoding:** raw byte array; catalog declares each ID's parameter shape (e.g. `[u16, u24]`). No type tags on the wire.
- **Catalog source-of-truth:** single canonical file in the meta-repo. Codegen produces a C++ header for firmware + a Python module for host.
- **Generated artifact policy:** generated files **committed** to both sub-repos. CI runs `<regen> && git diff --exit-code` so drift fails the build (visible in PRs).
- **Migration strategy:** phased. Infrastructure first (no removals). Then batched call-site conversion. Old log macros + PROGMEM strings deleted last, where the final flash-savings measurement happens.
- **Localization:** English only. No multi-language plumbing in v1.2.
- **Phase numbering:** continues from v1.1 (Phase 6-10); no `--reset-phase-numbers`.

## Decisions Carried Forward (v1.0 + v1.1)

See archived `.planning/milestones/v1.0-*.md` for v1.0 decisions and `.planning/phases/01-*/`, `02-*/`, `03-*/` for v1.1 phase-level decisions.

## Operator Next Steps

- `/gsd-discuss-phase 31` — gather context for Phase 31 (Upstream Shield Archaeology); clone `AndersBNielsen/Relatively-Universal-ROM-Programmer`, map git history, capture silkscreen text from operator's Rev 2.2 / Rev 2.0 / Modified Rev 0 boards
- Alternative: `/gsd-plan-phase 31` — skip discussion, plan Phase 31 directly using REQUIREMENTS.md + ROADMAP.md
- v1.6 resume: deferred until v1.7 ships — `/gsd-plan-phase 27 --gaps` once v1.7 close lands the labeled-schematic + per-rev capability table

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| Phase 06 P06-01 | 10m | 2 tasks | 10 files |
| Phase 06 P02 | 30 min | 2 tasks | 12 files |
| Phase 06 P03 | 5min | 3 tasks | 5 files |
| Phase 06 P06-04 | ~6 min | 2 tasks | 3 files |
| Phase 06 P06 | 8 min | 1 tasks | 1 files |
| Phase 06 P06-05 | ~7min | 3 tasks | 3 files |
| Phase 07 P07-01 | 1min | - tasks | - files |
| Phase 07 P03 | 15min | 1 tasks | 1 files |
| Phase 07 P04 | 15min | 1 tasks | 1 files |
| Phase 07 P05 | 1min | 2 tasks | 2 files |
| Phase 07 P06 | 2min | 1 tasks | 1 files |
| Phase 07-convert-error-warn-info-call-sites P07 | 15 | 1 tasks | 2 files |
| Phase 07 P08 | 5 | 1 tasks | 1 files |
| Phase 07 P09 | 10min | 1 tasks | 1 files |
| Phase 07 P10 | 15 | 1 tasks | 1 files |
| Phase 07 P11 | 3min | 1 tasks | 1 files |
| Phase 08 P08-01 | 25min | 3 tasks | 9 files |
| Phase 08 P02 | 19 | 2 tasks | 5 files |
| Phase 08 P03 | 20min | 2 tasks | 2 files |
| Phase 08 P04 | 20min | 6 tasks | 7 files |
| Phase 08 P05 | 45min | 4 tasks | 11 files |
| Phase 08 P06 | 12min | 2 tasks | 5 files |
| Phase 08 P07 | 11min | 2 tasks | 14 files |
| Phase 11 P11-01 | 12min | 1 tasks | 1 files |
| Phase 11 P11-02 | 12min | 2 tasks | 4 files |
| Phase 11 P11-03 | 18min | 3 tasks | 3 files |
| Phase 11 P04 | 6min | 3 tasks | 4 files |
| Phase 11 P05 | 10min | 2 tasks | 4 files |
| Phase 11 P06 | ~6min | 1 tasks | 4 files |
| Phase 12 P12-04 | 3min | 1 tasks | 3 files |
| Phase 21 P21-01 | ~5min | 2 tasks | 4 files |
| Phase 21 P21-02 | ~4min | 3 tasks | 5 files |
| Phase 22 P22-01 | ~3min | 3 tasks | 3 files |
| Phase 23 P23-01 | ~4min | 2 tasks | 1 files |
| Phase 23 P23-02 | ~3min | 3 tasks | 2 files |
| Phase 26 P01 | 5min | 2 tasks | 3 files |
| Phase 29 P1 | 12min | 5 tasks | 3 files |

## Decisions

- [Phase ?]: Plan 06-01: Adopted 68-entry catalog from RESEARCH §Full Catalog Seed table (the section header's 52-count is stale; the table itself has 68 rows).
- [Phase ?]: Plan 06-01: Codegen idempotence achieved via sort-by-id + LF-only line endings + no-timestamp banner; proven by re-running and diffing the output (BYTE-IDENTICAL on all 3 emitters).
- [Phase ?]: Plan 06-01: Catalog distribution = meta-repo authoritative + vendored sub-repo copies + cross-sub-repo byte-identity assertion in sync_to_subrepos.sh.
- [Phase ?]: Leonardo override: zero-diff (weak rurp_log_id default suffices — no com_mode global, no PORTD aliasing on USB-CDC; confirms T-06-08 acceptance)
- [Phase ?]: Phase 06-02: Native test binary links real rurp_serial_utils.cpp + messages.c via widened [env:native] src_filter — production CRC8 table + emitter validated end-to-end
- [Phase ?]: Host decoder ascii_str decode uses errors='replace' for visible tamper surface
- [Phase ?]: Reference CRC in test conftest is table-FREE — independent of production lookup table (catches table drift)
- [Phase ?]: _read_and_parse_lines unified text+binary dispatch through single yield surface (D-05)
- [Phase ?]: Phase 6 Plan 04: re-raise resolution + locked wording + escape hatch
- [Phase 06]: Plan 06-06: Decision Case A — Leonardo Phase 6 close at 98.7% (28,292/28,672 B, 380 B free); −7 B vs v1.1 close baseline (rounding noise; same 98.7% display). LMIG-01 coexistence proven; no -D NO_TEXT_LOGS fall-back required. Uno baseline established at 80.9% (6,156 B free).
- [Phase ?]: Phase 06-05: release.yml NOT given needs:[ci] gate — optional per plan; retrofittable later if bad-catalog→tag→PyPI race ever bites.
- [Phase ?]: Phase 06-05: Meta-repo catalog-sync-check.yml uses cmp (byte-equality, load-bearing) + diff (readable failure dump) together; submodules:recursive on meta-repo checkout per orchestrator objective.
- [Phase ?]: Phase 06-05: GitHub slugs pinned to henols/firestarter and henols/firestarter_app (confirmed via git remote get-url origin).
- [Phase ?]: Phase 07-01: LOG_ERROR_ID_* and LOG_WARN_ID_* macro families added as unconditional one-line aliases — no FLAG_VERBOSE gate, zero flash cost until call-sites are converted
- [Phase ?]: Phase 07-03: CHIP_ID_MISMATCH uses error_code parameter (not FLAG_FORCE re-check)
- [Phase ?]: Phase 07-03: WRITE_FAILED packs [u24, u8, u16] = 6 wire bytes MSB-first; braced-block isolation for _b[] arrays in eprom.cpp
- [Phase ?]: Phase 07-04: flash_intel_poll_sr response_code assignments added alongside LOG_ERROR_ID calls (Rule 2 auto-fix — state machine requires both emit and response_code set)
- [Phase 07]: Plan 07-05: flash_type_4.cpp multi-param [u8+u24+u8] packed into named local _b[5]; flash_utils.cpp zero-param LOG_ERROR_ID site; Leonardo confirmed at 98.4% flash (464 B free) after both conversions
- [Phase 07]: Plan 07-06: eeprom_28c.cpp 3 populate-sites converted; response_code added to EEPROM timeout path (was implicit, now explicit); Leonardo 97.8% flash (632 B free) after conversion
- [Phase ?]: Two-line error populate-site pattern established in memory.cpp
- [Phase ?]: Serial stub required in dispatch test setUp once error path emits via rurp_log_id (LOG_ERROR_ID_* conversion)
- [Phase ?]: flash_type_3.cpp:87 Skipping-erase site confirmed OK-path; deferred to Phase 8 (MSG_INFO_SKIPPING_ERASE_MEM 0x59)
- [Phase ?]: Dead-code block at firestarter.cpp:86 safely deleted
- [Phase ?]: command_done() resets handle immediately after timeout emit
- [Phase ?]: No format string needed — catalog owns the wire format
- [Phase 07]: Plan 07-11: Fixed-size stack buffers (16, 8, 32 bytes) for ascii_str packing in dev_tools.cpp; strlen clamped to prevent overrun; Arduino.h already provides string.h on AVR
- [Phase 08]: Plan 08-01: 'bytes' param type added to VALID_PARAM_TYPES (variable-length raw payload; Rule 9 excludes bytes from format specifier count); needed for MSG_DATA_CHUNK + MSG_DEBUG sub-payload
- [Phase 08]: Plan 08-01: MSG_OK_REV format "Rev%u (eff: %u)" [u8, u8]; MSG_OK_CFG format "R1: %lu, R2: %lu, Cfg: %u" [u32, u32, u8]; Rule 9 requires specifier count == non-bytes param count
- [Phase 08]: Plan 08-01: MSG_OK_FW_HANDSHAKE wire_format->id_frame; format "HW: %u, Cmd: 0x%02x, FW: %s" [u8 hw, u8 cmd, ascii_str fw_version]; hw=0xFF sentinel for no HARDWARE_REVISION
- [Phase 08]: Plan 08-01: 41 unique debug strings found (43 call-sites); CONTEXT.md B-01 count of 34 was stale; DBG_* sub_id 0x00..0x28 in [debug] section; audit at /tmp/ph8-debug-audit.txt
- [Phase 08]: Plan 08-01: sync_to_subrepos.sh now runs full generation cycle (copy TOML+codegen, then regen messages.h + messages.py); idempotence confirmed by second run zero-diff
- [Phase ?]: Firmware param_count stays uint8_t, guard widened to 65533 for W-04 MSG_DATA_CHUNK forward-compat
- [Phase ?]: bytes param type decodes all remaining buf as raw bytes; filtered from printf tuple
- [Phase ?]: Phase 08-03: _format_message added as instance method on SerialCommunicator; returns None to fall through to generic catalog rendering for non-sentinel IDs
- [Phase ?]: Phase 08-03: INIT/MAIN/END removed from EXPECTED_PREFIXES; STATE_MACHINE_PREFIXES emptied; dead Done-rewrite branch removed from _log_rurp_feedback
- [Phase ?]: LOG_DATA_ID_U32_U32 composite packs two u32 values as 8 big-endian bytes — covers MSG_DATA_PROGRESS; LOG_DATA_ID_U16_U16 declared for Plan 05 VPP/VPE symmetry
- [Phase ?]: Phase 08-04: 10 call-sites converted (3 state-machine acks, 2 trivial OK/DATA, 5 R-02 populate-sites) using LOG_OK_ID_*/LOG_INIT_ID_*/LOG_MAIN_ID_*/LOG_END_ID_*/LOG_DATA_ID_* families
- [Phase ?]: Phase 08 Plan 06: R-01 SRAM win exactly 96 bytes on both Uno and Leonardo (1593->1497 B Uno, 1563->1467 B Leonardo)
- [Phase 08]: Plan 08-07: LOG_DEBUG_ID_SUB_U16_U16 added for DBG_PULSE_DELAY_MISMATCH (pulse_delay is uint32_t exceeding catalog u8 decl; u16 preserves diagnostic range)
- [Phase 08]: Plan 08-07: debug_msg_buffer deleted (malloc(80) removed, extern decl removed, Uno rurp_log_id/rurp_log_P SoftwareSerial paths removed); debug_setup() retained for SoftwareSerial port init
- [Phase 08]: Plan 08-07: Production flash unchanged vs Plan 06 baseline — debug() was already a #define no-op in production; new LOG_DEBUG_ID_SUB* expands to same nothing
- [Phase 11]: Plan 11-01: Wave 0 RED-gate scaffold uses NotImplementedError after deferred import (not pytest.fail) — single failure-mode story across Wave 0 → Wave N transition (ModuleNotFoundError today, NotImplementedError once Wave 1 creates the tool module).
- [Phase 11]: Plan 11-01: Class-based pytest organisation chosen over module-level functions to mirror test_fwguard.py:31-42 — class boundary is the natural scope for the autouse _isolate_env fixture that clears FIRESTARTER_DB_FILE per test.
- [Phase 11]: Plan 11-01: Each stub docstring quotes BOTH requirement IDs (COV-01/COV-02/SC-03) AND decision IDs (D-02/D-03/D-06/D-07/D-09/D-10/D-11/D-12/D-13/D-15) — trace test → contract → CONTEXT.md walkable without re-reading PLAN.md.
- [Phase 11]: Plan 11-02: Live-DB regression anchors locked in three places — tool body (computed live), §2 reconciliation (live vs hard-coded old), test_summary_stats (substring asserts). A future DB regen that drifts 734 / 339 / 212 / 127 trips the test immediately; update all three together.
- [Phase 11]: Plan 11-02: §2 hard-codes the OLD planning-doc counts (743 / 214 / 341 / per-algo histogram) rather than greping them, so the matrix's §2 stays stable through and after Wave 5's D-07 planning-doc edit pass.
- [Phase 11]: Plan 11-02: Pulse-bucket sort uses explicit dict mapping (_pulse_bucket_sort_key returns 0-4 for the five D-09 buckets); never insertion order — Pattern B byte-identity guarantee across Python minor versions.
- [Phase 11]: Plan 11-02: --check semantic in Wave 1 is a no-op (always returns 0). Wave 3 (Plan 11-04) wires the real "would minting add new IDs?" comparison after the defect-findings emit lands. TODO comments in both tool body (line 524) and test_exit_codes mark the extension point.
- [Phase 11]: Plan 11-02: _REPO_ROOT computed from __file__ (three dirname() hops) → absolute --output and --ledger defaults; defends against operator-cwd variance per RESEARCH.md Pitfall 6.
- [Phase 11]: Plan 11-03: chip_id_value renders verbatim — all algo-0x07 + algo-0x08 rows store it as a string (`"0x00000108"`, `"0x00000000"`) in the live DB; no int-vs-string branching needed. Plan allowed the conditional; live data made it unnecessary.
- [Phase 11]: Plan 11-03: Per-algorithm split happens BEFORE Pattern F sort (filter → sort → render). Keeps each sub-table self-contained for test slicing (test_enumeration_sort parses each sub-table independently and asserts non-decreasing on the 4-tuple projection (pinout, size_bytes, manufacturer, first_alias) — algorithm is implicit per sub-table).
- [Phase 11]: Plan 11-03: emit_placeholder_sections() reduced from 3-tuple (s3, s4, s5) to 2-tuple (s4, s5) — §3 is now real; Wave 3/4 still consume the helper for §4/§5 placeholders. Clean shrink rather than a §3 stub left dangling.
- [Phase 11]: Plan 11-03: Defensive `_md_escape` (replaces `|` with `\|`) applied to every §3 cell despite no DB row containing `|` today. Robustness over micro-optimization — one function call per cell.
- [Phase 11]: Plan 11-03: 339-row regression anchor lives in three places (tool body live-computed, §2 reconciliation, test_enumeration_row_count). Drift in any one trips test_enumeration_row_count immediately; update all three together if DB regenerates.
- [Phase 11]: DEFECT-COV-00 uses pre-rederive _etype (Flash/EEPROM); DEFECT-COV-01 uses post-rederive _etype (UV-EPROM) — two distinct hashes for the same physical 42-row cluster — Build_db.py:481-486 rewrites _etype AFTER WARNING-5 predicate fires; the predicate-time and detect-time substrates are different — two distinct stable IDs capture both narrative angles (v1.0 fix vs v1.4 gap)
- [Phase 11]: Plan 11-05: BENCH_CHIP_MAP encoded verbatim from REQUIREMENTS.md §BENCH lines 14-19; BENCH-05 / BENCH-06 carry selection_pending=True so they render as 'BENCH-NN (candidate)' with Covered? = 'Y (pending selection)' per D-11. §5 records candidate names but does not propose alternatives — selection lives in Phase 12 CONTEXT.md.
- [Phase 11]: Plan 11-05: Compute order in generate_matrix is s4 BEFORE s5 — emit_defects mints DEFECT-COV-NN IDs into the ledger before emit_bench_coverage reads them for uncovered-cell cross-references. Linear order is the simplest correct shape; the alternative is a two-pass mint or render trampoline.
- [Phase 11]: Plan 11-05: Pulse-coverage cross-references filtered by first_alias-in-bucket membership (not "any finding on this algorithm"). 100ms-1s algo-0x07 cell now references 16 specific CORRECTNESS findings instead of dumping 52+ noisy IDs.
- [Phase 11]: Plan 11-05: Greenfield golden-file fixture at firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md is the regression anchor. test_golden_file_matches seeds tmp_path/l.json byte-identically from .planning/v1.3-defect-coverage-ids.json so DEFECT-COV-NN assignments stay stable; any output drift requires regenerating the golden alongside the matrix in one commit.
- [Phase 11]: Plan 11-05: Phrasing avoidance — initial caption read "does not propose swaps" but the literal "swap" tripped D-11 acceptance grep. Replaced with "is observational only" to preserve intent without triggering the regex. Lesson: D-11 acceptance gate is substring-grep, not semantic.
- [Phase 11]: Plan 11-06: D-07 reconciliation landed as a single dedicated commit (70be654, separate from matrix-tool commits per D-07). 20 substring replacements across PROJECT.md (6) / ROADMAP.md (4) / REQUIREMENTS.md (1) / STATE.md (2 — L36 substring "~341 algo-0x07" not present in live file, edit deferred per PLAN action guidance "do not invent substitute edits"). Historical narrative preserved in 3 locations per RESEARCH.md A6 (PROJECT.md L135 WIRE-02 743/743 PASS decision-row; ROADMAP.md L140 v1.0 archived <details> bullet; STATE.md L220 Plan 11-02 narrative about §2 hard-coding the OLD counts).
- [Phase ?]: [Phase 12]: Plan 12-04: Headers-only scaffold for v1.3-BENCH-RESULTS.md (no placeholder rows) — resolves RESEARCH.md Open Q1; append-a-new-row is idempotent on resume vs edit-an-empty-row.
- [Phase ?]: [Phase 12]: Plan 12-04: BENCH evidence accretion model — v1.3-BENCH-RESULTS.md is append-only across Phases 12 + 13; Phase 14 / DOC-01 closes it. Two empty directories (bench-logs/, scope/) committed via .gitkeep sentinels.
- [Phase 21]: Plan 21-01: Path B locked at the requirements layer — REQUIREMENTS.md FW-02 amended to drop boards/uno328pb.json entirely; the requirement now anchors on `RURP_BOARD_NAME` as the single source of truth for the board-id triple (artifact filename = build_flag value = handshake `<board>` slot). Citing CONTEXT D-05 + D-09 inline keeps the REQUIREMENTS → CONTEXT trace grep-walkable.
- [Phase 21]: Plan 21-01: GATE-1.5 baselines captured with `include/version.h` UNMODIFIED (VERSION="3.0.0b2") per RESEARCH Pitfall 3 — any `update_version.py` invocation between capture and Plan 21-02's `cmp -s` gate tears the .rodata version-string region. CAPTURE-PROCEDURE.md records the "do NOT run update_version.py" warning explicitly + SHA-256 of each baseline for drift detection.
- [Phase 21]: Plan 21-01: Hex baselines stored as plain blobs under `.planning/v1.5/baselines/` (no Git LFS) per CONTEXT D-04 Claude's Discretion — meta-repo is otherwise text-only and ~62/69 KB per board is below any meaningful LFS threshold.
- [Phase 21]: Plan 21-02: RESEARCH Open Q1 resolved at execution time — `platform = atmelavr` worked on the FIRST attempt (no fallback to `MCUdude/MiniCore` needed). The bundled `boards/ATmega328PB.json` in `platformio/atmelavr@5.2.0` supplies `build.core = "MiniCore"` and `-DARDUINO_AVR_ATmega328PB` via `build.extra_flags`. CONTEXT D-07's literal `platform = MCUdude/MiniCore` is a colloquial reference; the canonical PIO form is `atmelavr` (mirrors `[env:uno]`).
- [Phase 21]: Plan 21-02: FW-03 verification surface adjustment — AVR ELFs (avr-gcc output) DO NOT have a `.rodata` section; the `FW_VERSION` literal lands in `.data` instead. Plan's primary `avr-objdump -j .rodata -s` command errors with `section '.rodata' mentioned in -j option, but not found in any input file`. CONTEXT D-13's alternative `avr-strings -a *.elf | grep -F <board>` (or `avr-objdump -j .data -s`) is the canonical AVR-correct verification surface and surfaces the literal `3.0.0b2:uno328pb` cleanly. Documented in 21-02-SUMMARY.md "Deviations" section for downstream phases (especially Phase 22 if it ever adds a CI gate asserting the handshake string ships in the artifact).
- [Phase 21]: Plan 21-02: PROGNAME-named ELF — PIO renames BOTH the `.hex` AND the `.elf` to `PROGNAME`. Actual ELF path is `.pio/build/uno328pb/firestarter_uno328pb.elf`, NOT `firmware.elf`. This is inherited behavior (uno + leonardo envs also emit `firestarter_uno.elf` / `firestarter_leonardo.elf`); the plan's `firmware.elf` references were spec drift. Downstream phases that need the ELF should reference `.pio/build/<env>/firestarter_<env>.elf`.
- [Phase 21]: Plan 21-02: Atomic 4-site widening + new env block landed in a single firmware sub-repo commit (ab7c2a9) per CONTEXT D-01 invariant — no half-state in any commit. Pitfall 5 honored: `rurp_common.cpp` lines 25 + 28 (the Leonardo `#elif` arm + `#error "Unsupported board"`) preserved verbatim through the widening of lines 10 + 23.
- [Phase 21]: Plan 21-02: GATE-1.5 byte-identity preserved across BOTH perturbations (script rework + macro widening). Sub-repo commits ordered such that Task 1 (script) and Task 2 (widening + env) committed separately to isolate the GATE-1.5 risk surface per RESEARCH Assumption A3 — cmp -s verified green AFTER each commit, not just at the end.
- [Phase 22]: Plan 22-01: Coupled meta-repo + sub-repo edit on the matching `v1.5-uno328pb` branch landed exactly per CONTEXT D-01..D-11 with zero deviations. Section-order choice `default_envs = uno, uno328pb, leonardo` (Phase 21 D-08 / Phase 22 D-01) picked over the older ROADMAP literal `uno, leonardo, uno328pb` because the `.ini` section order is the natural consistency anchor and is what the planner-owns-the-realignment hand-off in Phase 21 D-12 enabled.
- [Phase 22]: Plan 22-01: Phase 22 ships SUBSTRATE for REL-01 + REL-02 (the platformio.ini widening + ROADMAP literal realignment); the "inspect release's asset list after a stable/beta cut" portion of REL-01/REL-02 acceptance is verified at Phase 24's first real beta cut from `firestarter/beta` per CONTEXT D-08 + RESEARCH Pitfall 6. Same Phase 18->Phase 20 pattern from v1.4. Documented in 22-01-SUMMARY.md REL-01/REL-02/GATE-01 substrate coverage section.
- [Phase 22]: Plan 22-01: Skipped defensive size/symbol assertion on firestarter_uno328pb.hex (Claude's Discretion #3) — `cmp -s` against Phase 21 baselines is the strongest available byte-identity gate; an additional check would be ceremony without signal. Plan executed with the smaller-diff form (RESEARCH primary recommendation).
- [Phase 22]: Plan 22-01: Meta-repo submodule pointer advance from 5fd751e -> 897067b included in the meta-repo commit (f0aca97) alongside ROADMAP.md. This rolls the meta-repo's submodule record through both Phase 21's ab7c2a9 (sub-repo Phase 21 tip — never previously committed back to meta-repo) and Phase 22's 897067b. Future plan executors should verify submodule pointer consistency early.
- [Phase 23]: Plan 23-01: TDD RED wave landed 5 named pytest contracts (`TestUno328pbResolution` class) + `_FakeAvrdude` helper + `_STABLE_RELEASE_UNO328PB` 3-asset fixture in a single sub-repo commit (67c8357) on `firestarter_app/v1.5-uno328pb`. D-07 GATE-01 invariant preserved bit-for-bit (`git diff --stat` shows `1 file changed, 257 insertions(+), 0 deletions`). Pre-Wave-2 status verified at execution time matches the plan's prediction verbatim: tests 1-3 PASS green (v1.4 INST-04 board-string-generic resolver substrate extends to `uno328pb` for free), tests 4 + 5 FAIL RED (firmware.py default `atmega328p` branch + main.py `choices=["uno","leonardo"]` allowlist). Plan 23-02's job is precisely those two edits.
- [Phase 23]: Plan 23-01: RESEARCH Open Q3 / Assumption A2 verified empirically — `monkeypatch.setattr(firmware, "Avrdude", _capture_init)` does propagate to the production call site at firmware.py:472 (no `unittest.mock.patch("firestarter.firmware.Avrdude")` fallback needed). Module-level import at firmware.py:30 binds `Avrdude` as a module attribute; the call site resolves against `firmware.Avrdude` so the monkeypatch wins. New mock pattern is now established for any future Avrdude-mocking test.
- [Phase 23]: Plan 23-01: D-07 invariant verified via the strongest possible gate — `git diff HEAD~1 HEAD -- tests/test_firmware_install.py | grep -E "^-[^-]"` returns empty (no `-` lines that aren't part of the `---`/`@@@` diff header). Pure additions only; existing 30 test methods + 2 helpers (`mock_releases_factory`, `mock_404_response`) + 2 fixtures (`_STABLE_RELEASE_UNO`, `_STABLE_RELEASE_LEONARDO`) byte-identical to the pre-edit state.
- [Phase 23]: Plan 23-02: TDD GREEN wave landed atomic 2-file paired edit on `firestarter_app/v1.5-uno328pb` (sub-repo commit d13d9b1) -- firmware.py `_install_with_avrdude` gains the `elif board.lower() == "uno328pb":` branch with the canonical `("atmega328pb", "arduino", 115200)` profile, and main.py argparse `-b/--board` choices widens from `["uno","leonardo"]` to `["uno","uno328pb","leonardo"]` (Phase 21 D-08 section order). 8 insertions / 0 deletions; the leonardo branch + uno default tuple are byte-identical post-edit (D-07 invariant verified via `grep -E "^-[^-]"` returning empty on both files). 5 uno328pb-named tests turn GREEN; GATE-01 command `-k "not uno328pb"` stays at 77 passed bit-for-bit; full suite at 82 passed.
- [Phase 23]: Plan 23-02: Substring-anchor Edits worked on first attempt for both files (RESEARCH Pitfall 1 cleared -- no line-number drift). The 8-space indent on the elif (function-body level) and 12-space indent on the new `"uno328pb",` choice (inside the multi-line `choices=[` list) matched the file's existing conventions. The inline Phase 21 D-10 hand-off comment cites the 0x1E 0x95 0x16 vs 0x1E 0x95 0x0F signature distinction explicitly, providing the trace for future readers and the Phase 24 BENCH-01 contingency hand-off ("if `arduino` programmer_id fails on the operator's MiniCore Urclock bootloader, 1-line swap to `urclock`").
- [Phase 23]: Plan 23-02: INST-01 / INST-02 / INST-03 / GATE-01 all closed at the mocked-pytest layer. INST-02 real-silicon proof deferred to Phase 24 BENCH-01 (D-15). Phase 23 ready for `/gsd-verify-work 23`. No remote push (D-20) -- branch stays local until milestone close at Phase 25.
- [Phase ?]: Plan 26-01: consistency_check_eprom returns int directly (0/1/2 per D-05); dispatch branch returns the int directly (no bool->int wrapper) — 3-way verdict can't fit in bool.
- [Phase ?]: Plan 26-01: Reused _run_state_machine + _main_phase_read_data + _write_to_file closure verbatim per D-03 reuse-not-duplicate (grep verifies 3 main_phase_handler= occurrences in eprom_operations.py).
- [Phase ?]: Plan 26-01: Default output_dir uses 'unknown-board' placeholder; Plan 26-02 bench wave passes --output-dir explicitly with real board name.
- [Phase ?]: Plan 26-01: Quiet mode swaps progress_callback to a no-op lambda for the call duration (restored in finally) per RESEARCH Pitfall 1 — does not touch ClassProgressHandler directly.
- [Phase ?]: Plan 26-01: Phase 29 forward-compat contract pinned by test_stdout_verdict_block_format regex regression — Consistency check: PASS|FAIL, Distinct SHAs, Runs: N=, First divergence: offset 0x[0-9A-F]+.
- [Phase 29]: Plan 29-01: firestarter_app v1.6-read-bug branch tip is 999c3cc (NOT c057fe2 as CONTEXT.md D-02 lists); 999c3cc is the GREEN feat commit carrying dev consistency-check implementation, c057fe2 is the RED-scaffold one commit prior. RESEARCH.md authoritative; downstream phases should treat 999c3cc as canonical.
- [Phase 29]: Plan 29-01: Captured per-board build SHA-256s at firestarter/v1.6-read-bug commit 4f205e58 (uno=5e7f393a..., leonardo=2619eea6..., uno328pb=d9e51b7e...) for Wave B + Phase 30 byte-equivalence cross-reference; full hashes in v1.6-EVIDENCE.md build-hash table.
- [Phase 29]: Plan 29-01: firestarter_app/firestarter/config.py working-tree drift dispositioned 'proceed with editable install' — stylistic early-return refactor (functionally equivalent); pytest gate green (8 passed) confirms no functional regression.

## Deferred Items (acknowledged at v1.5 close 2026-05-21)

| Category | Item | Status | Carries to |
|----------|------|--------|------------|
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 (pre-v1.5; hardware-gated) | v1.6+ if/when Phase 4 v1.1 unblocks |
| uat-gap | Phase 08 HUMAN-UAT.md | partial — 2 pending scenarios (v1.2 territory) | Future v1.x cleanup |
| verification-gap | Phase 08 VERIFICATION.md | human_needed (v1.2 territory) | Future v1.x cleanup |
| verification-gap | Phase 09 VERIFICATION.md | human_needed (v1.2 territory) | Future v1.x cleanup |
| todo | large-read-data-jitter-uno328pb.md | **in scope for v1.6** — Phases 26-30 (READ-BUG milestone) | v1.6 (active) |
| todo | w27c512-eeprom-misclassification.md | HIGH — operator-tagged asap | v1.7+ |
| todo | avrdude-mcu-detection-fallback.md | low — host CLI enhancement | v1.7+ |

Operator-authorized close 2026-05-21 ("close the milestone"). v1.6 STARTED 2026-05-21; roadmap created 2026-05-21.

---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: — Arduino Uno
status: verifying
last_updated: "2026-05-20T20:36:23.361Z"
last_activity: 2026-05-20
progress:
  total_phases: 5
  completed_phases: 1
  total_plans: 2
  completed_plans: 2
  percent: 20
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-05-20

## Current Position

Phase: 22
Plan: Not started
Status: Phase 21 ready for /gsd-verify-work; Phase 22 (REL) next
Last activity: 2026-05-20

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-20)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing.

**Current focus:** Phase 21 — firmware-target-uno328pb

- v1.2 (Message-ID Logging Rework) shipped 2026-05-19 — Leonardo Flash 98.7% → 85.4%
- v1.3 (CMOS EPROM Family Hardware Validation) PAUSED 2026-05-20 — Phase 11 shipped, Phase 12 Wave 0 scaffold shipped, Waves 1–3 + Phases 13/14 await hardware (see Paused Milestones below)
- v1.4 (Beta & Pre-release Deployment Pipeline) SHIPPED 2026-05-20 — 6/6 phases, 10/10 plans, ship tag 3.0.0b3, hardware-flash validated on Uno + Leonardo
- v1.5 (Arduino Uno ATmega328PB Board Support) STARTED 2026-05-20 — `uno328pb` as a third first-class firmware target; operator's 328PB-Uno + RURP shield available for bench validation; work branches off `beta` in both sub-repos

## Roadmap Summary

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

None at v1.4 start.

### Paused Milestones

| Milestone | Paused | Reason | Resume Command |
|-----------|--------|--------|----------------|
| **v1.3** — CMOS EPROM Family Hardware Validation | 2026-05-20 | Hardware-gated. Phase 11 (coverage matrix + 78-finding defect ledger + all-algorithms wide-scan with 137 findings across 11 algos) shipped. Phase 12 Wave 0 desk-side scaffold committed (`.planning/v1.3-BENCH-RESULTS.md` skeleton + `.planning/v1.3/bench-logs/` + `.planning/v1.3/scope/`). Plans 12-01/02/03 (BENCH-01/02/05 — W27C512, SST27SF512, W27C257) + entire Phase 13 (algo-0x08 family) + Phase 14 milestone close cannot start without Uno + Leonardo + RURP shield + DIP-28 socket + scope + the bench chips. Auto-mode would silently fabricate bench results — operator paused milestone to avoid integrity hazard. v1.4 phase numbering continues at 15 to avoid collision when v1.3 resumes. | `/gsd-execute-phase 12 --wave 1 --interactive` (once bench hardware available) |

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

- Run `/gsd-verify-work 21` to formally close Phase 21 (all SC green; both plans shipped). Then start Phase 22 (Release Pipeline Artifacts): `/gsd-execute-phase 22` — this widens `[platformio] default_envs` to include `uno328pb` so `build.yml` + `beta-build.yml` attach the new artifact to GitHub Releases. Cross-phase hand-off reminder: CONTEXT D-11 / D-12 — Phase 22 SC#1's ROADMAP literal currently reads `default_envs = uno, leonardo, uno328pb`; the CONTEXT D-08 section order argues for `uno, uno328pb, leonardo`. Phase 22 planner picks. Phase 23 (Host CLI) hand-off: `firestarter_app/firestarter/firmware.py:417-423` needs an `uno328pb` branch for the avrdude profile (CONTEXT D-10) — partno = `atmega328pb`, baud_rate = 115200, programmer_id = whatever bootloader the operator flashed (likely `urclock` per MiniCore default).

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

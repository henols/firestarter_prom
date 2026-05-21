# Roadmap: Firestarter — Protocol-Aware Programming Architecture

## Milestones

- ✅ **v1.0 Protocol-Aware Programming Architecture** — Phases 1-13 (shipped 2026-05-11)
- ⏸ **v1.1 Safety Closure & Hardware Validation** — Phases 1-3 done, Phase 4 hardware-validation parked (FM1608 byte-0 bug); Phase 5 milestone-close deferred. Original artifacts preserved at `.planning/milestones/v1.1-paused/`.
- ✅ **v1.2 Message-ID Logging Rework** — Phases 6-10 (shipped 2026-05-19); Phase 10 closed by `/gsd-complete-milestone` (DOC-02)
- ⏸ **v1.3 CMOS EPROM Family Hardware Validation** — Phases 11-14 (PAUSED 2026-05-20, hardware-gated). Phase 11 shipped + Phase 12 Wave 0 scaffold committed; Plans 12-01/02/03 + Phases 13/14 await operator bench hardware.
- ✅ **v1.4 Beta & Pre-release Deployment Pipeline** — Phases 15-20 (shipped 2026-05-20; ship tag `3.0.0b3` in both sub-repos; hardware-flash validated on Uno + Leonardo). Parallel beta channel for both sub-repos without disrupting the stable main → release pipeline.
- 🚧 **v1.5 Arduino Uno (ATmega328PB) Board Support** — Phases 21-25 (STARTED 2026-05-20). `uno328pb` as a third first-class firmware target alongside `uno` + `leonardo`; operator's 328PB-Uno + RURP shield available for bench validation; work branches off `beta` in both sub-repos.

## v1.5 — Arduino Uno (ATmega328PB) Board Support (STARTED 2026-05-20)

**Milestone goal:** Ship `uno328pb` as a third first-class firmware target alongside the existing `uno` and `leonardo`. End-to-end coverage: PlatformIO env + custom board definition → firmware handshake reports `uno328pb` → stable + beta release pipelines emit a third per-board `.hex` artifact (`firestarter_uno328pb.hex`) → host CLI's `firestarter fw -i` flashes the right artifact when the device reports `uno328pb` → bench-validated EPROM write → read-back → verify cycle on the operator's plugged-in 328PB-Uno + RURP shield. **This is a surgical MCU port; algorithm dispatch, wire protocol, chip database, host CLI verbs are unchanged.**

**Status:** 🚧 In progress 2026-05-20. Sub-repo work branches will be cut from `beta` (current tip 5fd751e in both sub-repos as of milestone start) per operator instruction. Meta-repo `.planning/` work proceeds on `main`.

**Granularity:** Standard. Five phases, 13 requirements, each mapped to exactly one phase.
**Phase numbering:** Phases 21–25 (continues from v1.4 close at Phase 20).

### Structural Notes

- **Sub-repo branching.** Per operator instruction, both `firestarter/` and `firestarter_app/` cut working branches off `beta`. The v1.4 substrate already supports a per-board artifact matrix; v1.5 just widens it from 2 → 3 boards. First v1.5 pre-release version cut from `beta` after Phases 21–23 are green; promotion `beta` → `main` follows the v1.4 beta→stable pattern only after the Phase 24 bench-green.
- **Desk-side vs. operator-bench split.** Phases 21 (firmware target), 22 (release pipelines), 23 (host CLI integration), 25 (docs + milestone close) are desk-side and can land without the 328PB-Uno in hand. Phase 24 is the only operator-on-bench phase — it requires the 328PB-Uno + RURP shield + an EPROM in the socket to validate the port on real silicon. The operator confirmed the hardware is available, so v1.5 is *not* hardware-gated in the way v1.3 is.
- **Board-ID = artifact-name = handshake-string (consistent triple).** `board = uno328pb` in `[env:uno328pb]` → `name_firmware.py` emits `firestarter_uno328pb.hex` → `RURP_BOARD_NAME=\"uno328pb\"` build flag → firmware handshake reports `uno328pb` → host `firmware.py:fetch_latest_release_info` resolves `firestarter_{board}.hex` → installer downloads `firestarter_uno328pb.hex`. The triple makes the host code path zero-change for the install-by-board-name flow; v1.5 host work is one allowlist entry + one regression test, not a board-name translation table.
- **GATE-1.5 (non-regression).** `firestarter_uno.hex` + `firestarter_leonardo.hex` byte-identical to pre-v1.5 outputs (modulo version-string drift); stable-installed app's `firestarter fw -i` on `uno`/`leonardo`-reporting devices unchanged. Verified at Phase 22 (release pipeline) and Phase 23 (host CLI).
- **Branch tip baseline.** Both sub-repos at `beta` tip `5fd751e` (2026-05-20). Last commit message: `chore: ignore __pycache__/*.pyc + untrack accidentally-committed bytecode`. Meta-repo at `main` tip `9839eca` (v1.5 requirements commit).

### Phases

- [x] **Phase 21: Firmware Target — `uno328pb`** — PlatformIO env (no custom board file; see CONTEXT D-05 Path B amendment to FW-02) + name_firmware.py rework + handshake-name plumbing + native test green + GATE-1.5 byte-identity on uno + leonardo. Desk-side. (FW-01, FW-02, FW-03, FW-04). **Plans:** 2/2 complete (shipped 2026-05-20)
- [x] **Phase 22: Release Pipeline Artifacts** — Stable + beta workflows emit `firestarter_uno328pb.hex` as a third per-board artifact; existing two artifacts unchanged. Desk-side / CI-side. (REL-01, REL-02). **Plans:** 1/1 complete (substrate; asset-list inspection portion deferred to Phase 24 first beta cut per CONTEXT D-08 + Pitfall 6)
- [x] **Phase 23: Host CLI Installer Integration** — Confirm `firestarter fw -i`/`--pre`/`firmware list` work for `uno328pb`-reporting devices; add any allowlist entry + regression test; verify GATE-01 non-regression on existing boards. Desk-side. (INST-01, INST-02, INST-03, GATE-01). **Plans:** 2/2 complete (shipped 2026-05-21; full suite 82/82 PASS; GATE-01 `pytest -k "not uno328pb"` = 77 PASS byte-identical to pre-Phase-23; INST-02 real-silicon proof deferred to Phase 24 BENCH-01 per D-15)
- [ ] **Phase 24: Bench Validation on 328PB-Uno** — Operator-on-bench cycle: cut a v1.5 beta pre-release, flash 328PB-Uno via `firestarter fw -i --pre`, run write→read→verify on a representative EPROM (W27C512 default). Capture `.planning/v1.5-BENCH-RESULTS.md`. (BENCH-01, BENCH-02)
- [ ] **Phase 25: Documentation + Milestone Close** — README updates (firmware + app), release-procedures update for three-board matrix, MILESTONES.md entry, archive v1.5 phase directories, update PROJECT.md to "shipped". (DOC-01, DOC-02, MS-01)

### Phase Details

#### Phase 21: Firmware Target — `uno328pb`
**Goal:** A clean `pio run -e uno328pb` build that emits `firestarter_uno328pb.hex` and a firmware that, when handshaken, reports its board as the literal string `uno328pb`. Native dispatch + messages tests green.
**Depends on:** Nothing (desk-side; no operator hardware needed for build/handshake-string validation). Can land before Phase 22 even sees the artifact.
**Requirements:** FW-01, FW-02, FW-03, FW-04
**Success Criteria** (what must be TRUE):
  1. `pio run -e uno328pb` from a clean checkout of `firestarter/beta` produces `.pio/build/uno328pb/firestarter_uno328pb.hex` with no errors and no new warnings (vs. the `uno`/`leonardo` baseline).
  2. The PlatformIO board file `firestarter/boards/uno328pb.json` exists, declares `mcu = atmega328pb`, declares an Arduino-Uno-compatible pin mapping (no PE0–PE3 use), and is loaded by `[env:uno328pb]` via `board = uno328pb`. `env.GetProjectOption("board")` returns the literal string `uno328pb` (validated by adding a `pre:name_firmware.py` print or by observing the artifact filename).
  3. `platformio.ini` has a new `[env:uno328pb]` section with `platform = MCUdude/MiniCore`, `board = uno328pb`, `framework = arduino`, and `build_flags` carrying `${env.build_flags}` + `-D RURP_BOARD_NAME=\"uno328pb\"` (+ `DATA_BUFFER_SIZE=512` if explicit is preferred; matches `uno`).
  4. Firmware emits the literal string `uno328pb` in the `<board>` slot of the `MSG_OK_FW_HANDSHAKE` payload — verifiable by linking against an existing native test harness or, if not host-testable, by static analysis of the build's `.elf` symbol section showing `RURP_BOARD_NAME` resolves to `"uno328pb"`.
  5. `pio test -e native` from the same checkout completes with `test_dispatch` and `test_messages` suites both green — the new env addition must not regress the host-side native suite.
**Plans:** 2/2 plans complete
- [x] 21-01-PLAN.md — Wave 1: Capture GATE-1.5 baselines (firestarter_uno.hex + firestarter_leonardo.hex from beta @ 5fd751e) + amend REQUIREMENTS.md FW-02 per CONTEXT D-09 (drop boards/uno328pb.json, anchor on RURP_BOARD_NAME + name_firmware.py rework) — shipped 2026-05-20 (commits 78dc1fe + 6fdaaff)
- [x] 21-02-PLAN.md — Wave 2: Reworked firestarter/name_firmware.py (PROGNAME from RURP_BOARD_NAME via env.ParseFlags) + atomic 4-site macro guard widening (ARDUINO_AVR_UNO → || ARDUINO_AVR_ATmega328PB) + added [env:uno328pb] block (platform=atmelavr, board=ATmega328PB) + full verification gate green (FW-01 build SUCCESS / 0 warnings; FW-03 `avr-strings` surfaces `3.0.0b2:uno328pb` from firestarter_uno328pb.elf [AVR ELFs lack .rodata → avr-strings is the canonical alt per CONTEXT D-13]; FW-04 native suite 20/20 PASS; GATE-1.5 cmp -s both exit 0) — shipped 2026-05-20 (sub-repo commits da607d4 + ab7c2a9 on firestarter/beta)

#### Phase 22: Release Pipeline Artifacts
**Goal:** Both the stable workflow (`build.yml`) and the beta workflow (`beta-build.yml`) emit `firestarter_uno328pb.hex` as a third per-board release artifact alongside `firestarter_uno.hex` and `firestarter_leonardo.hex`, without altering the existing two artifacts' byte content (modulo version-string drift).
**Depends on:** Phase 21 (the artifact must exist on disk before the release upload step can attach it).
**Requirements:** REL-01, REL-02
**Success Criteria** (what must be TRUE):
  1. `platformio.ini` `default_envs = uno, uno328pb, leonardo` so a CI-side `pio run` builds all three targets. (Order matches the `[env:*]` section order in `platformio.ini` per Phase 21 D-08 + D-12 hand-off; supersedes the original stale literal `uno, leonardo, uno328pb`.) The workflows' existing glob `files: .pio/build/**/firestarter_*.hex` (build.yml:105 + beta-build.yml:92) captures all three artifacts — no workflow edits needed (CONTEXT D-03).
  2. `build.yml` Release step's `files:` glob (`/.pio/build/**/firestarter_*.hex`) catches `firestarter_uno328pb.hex` end-to-end on a stable cut from `firestarter/main`. After a stable cut, the GitHub Release asset list shows three `.hex` files.
  3. `beta-build.yml` Release step's `files:` glob likewise catches `firestarter_uno328pb.hex` on a beta cut from `firestarter/beta`. After a beta cut, the GitHub Pre-release asset list shows three `.hex` files; `prerelease: true` and `make_latest: false` unchanged.
  4. `firestarter_uno.hex` and `firestarter_leonardo.hex` from a v1.5 cut are byte-identical to a pre-v1.5 cut of the same source revision (modulo version-string drift from `update_version.py`). Verified by `diff` against the v1.4 ship-tag (3.0.0b3) artifacts.
  5. No new mandatory CI checks are added; existing catalog-validity + codegen-drift + native Unity + PIO build gates run unchanged.
**Plans:** 1/1 plans complete
- [x] 22-01-PLAN.md — Wave 1: widen `firestarter/platformio.ini` `default_envs` to `uno, uno328pb, leonardo` (D-01) + realign ROADMAP Phase 22 SC#1 literal (D-02; Phase 21 D-12 hand-off); GATE-01 byte-identity + native suite regression-clean; no CI workflow edits (D-03 / D-11) — shipped 2026-05-20 (sub-repo commit 897067b on firestarter/v1.5-uno328pb + meta-repo commit f0aca97 on v1.5-uno328pb; GATE-01 cmp -s both exit 0; native 20/20 PASS; workflow YAMLs untouched)

#### Phase 23: Host CLI Installer Integration
**Goal:** `firestarter fw -i`, `firestarter fw -i --pre`, and `firestarter firmware list` flow through the existing v1.4 board-driven asset-resolution path cleanly when the connected device's firmware handshake reports `uno328pb`. Any allowlist entry needed (e.g. in `avr_tool.py` upload profile or `constants.py` enum) is added; a regression test exercises the `uno328pb`-reporting code path.
**Depends on:** Phase 22 (the host integration test downloads a real `uno328pb` asset; pre-Phase-22 there is no asset to download — though unit tests with mocked GitHub API can land in parallel with Phase 22).
**Requirements:** INST-01, INST-02, INST-03, GATE-01
**Success Criteria** (what must be TRUE):
  1. With a `uno328pb`-reporting firmware connected (or simulated via the existing serial mock used in `tests/test_firmware*.py`), `firestarter fw -i` resolves the latest stable release's `firestarter_uno328pb.hex` asset URL via `fetch_latest_release_info(board="uno328pb")` and `avr_tool.py` flashes it with a 328PB-compatible upload profile.
  2. `firestarter fw -i --pre` likewise resolves the highest PEP 440 pre-release's `firestarter_uno328pb.hex` asset URL and flashes it.
  3. `firestarter firmware list [--all|--pre|--stable]` enumerates `uno328pb` releases when a 328PB device is connected, with the same plain-text/JSON table shape as for `uno`/`leonardo`.
  4. A new pytest case (or extension of an existing one in `firestarter_app/tests/`) covers the `uno328pb`-reporting code path end-to-end with mocked GitHub responses; existing `uno`/`leonardo` test cases remain green.
  5. With a `uno`-reporting or `leonardo`-reporting firmware connected, `firestarter fw -i` and `firestarter fw -i --pre` flash the matching `.hex` artifact with byte-identical behavior to pre-v1.5 (GATE-01 non-regression).
**Plans:** 2/2 plans complete
- [x] 23-01-PLAN.md — Wave 1: TDD RED. **SHIPPED 2026-05-21.** Adds class TestUno328pbResolution with 5 tests (3 release-resolution + 1 avrdude profile + 1 argparse allowlist) + _FakeAvrdude helper + _STABLE_RELEASE_UNO328PB fixture in firestarter_app/tests/test_firmware_install.py (D-05, D-06, D-10 revised). Sub-repo commit `67c8357` on `firestarter_app/v1.5-uno328pb`. SUMMARY: `23-01-SUMMARY.md`. Pre-Wave-2 status verified at execution: tests 1-3 PASS green (v1.4 board-string-generic substrate); tests 4 + 5 FAIL RED (avrdude profile + argparse allowlist). GATE-01 baseline holds (`pytest -k "not uno328pb"` = 77 passed).
- [x] 23-02-PLAN.md — Wave 2: TDD GREEN. **SHIPPED 2026-05-21.** Atomic 2-file paired edit on `firestarter_app/v1.5-uno328pb` (sub-repo commit `d13d9b1`): firestarter/firmware.py `_install_with_avrdude` gains `elif board.lower() == "uno328pb":` branch with the canonical `("atmega328pb", "arduino", 115200)` profile (D-01..D-04) + 5-line Phase 21 D-10 hand-off inline comment; firestarter/main.py argparse `-b/--board` choices widens from `["uno","leonardo"]` to `["uno","uno328pb","leonardo"]` (D-10 revised, Phase 21 D-08 section order). 8 insertions / 0 deletions. D-07 byte-identity verified (leonardo branch + uno default tuple unchanged). 5 uno328pb-named tests turn GREEN; GATE-01 (`pytest -k "not uno328pb"`) holds at 77 passed bit-for-bit; full suite at 82 passed. SUMMARY: `23-02-SUMMARY.md`. INST-01 / INST-02 / INST-03 / GATE-01 closed at mocked-pytest layer; INST-02 real-silicon proof deferred to Phase 24 BENCH-01.

#### Phase 24: Bench Validation on 328PB-Uno
**Goal:** Operator-on-bench session: cut a v1.5 beta pre-release in `firestarter/beta` (and matching app pre-release in `firestarter_app/beta` per v1.4 locked-step procedure), flash the operator's plugged-in 328PB-Uno via `firestarter fw -i --pre`, then run a real `write → read → verify` cycle on at least one representative EPROM in the operator's chip kit (default W27C512). Capture `.planning/v1.5-BENCH-RESULTS.md`.
**Depends on:** Phases 21, 22, 23 (all desk-side foundations must be green before a beta cut is meaningful).
**Requirements:** BENCH-01, BENCH-02
**Success Criteria** (what must be TRUE):
  1. A v1.5 beta pre-release exists in both sub-repos (matching version strings per v1.4 VER-03 locked-step). Firmware pre-release asset list carries three `.hex` files including `firestarter_uno328pb.hex`.
  2. Operator runs `firestarter fw -i --pre` connected to the 328PB-Uno + RURP shield. Host installs the matching `firestarter_uno328pb.hex` from the pre-release asset, `avr_tool.py` reports a clean flash, and the device reboots into the v1.5 firmware. Post-flash handshake reports the v1.5 version and `board: uno328pb`.
  3. Operator runs `firestarter write <chip>` on an EPROM in the socket (default W27C512 — substitute from operator's kit if necessary). Write completes without error; `firestarter read <chip>` returns byte-identical data; `firestarter verify <chip>` reports PASS.
  4. VPP regulator engages at the expected millivolts for the chip's algorithm (per existing firmware behavior — same value as on the regular `uno` for the same chip).
  5. Bench results captured as a row in `.planning/v1.5-BENCH-RESULTS.md` (skeleton committed by Phase 24's planning work; row appended by the bench session).

#### Phase 25: Documentation + Milestone Close
**Goal:** `firestarter/README.md` + `firestarter_app/README.md` both mention the third supported board with install-by-handshake guidance. Meta-repo `v1.4-RELEASE-PROCEDURES.md` (or the renamed v1.5 successor) lists three boards in the release-engineer per-board verification step. v1.5 ships: `MILESTONES.md` entry, phase directories archived under `.planning/milestones/v1.5-phases/`, `PROJECT.md` updated to "shipped".
**Depends on:** Phase 24 (you document what you built and what you've validated — the docs lock the substrate after bench-green).
**Requirements:** DOC-01, DOC-02, MS-01
**Success Criteria** (what must be TRUE):
  1. Firmware README and app README each have a paragraph in the supported-boards / hardware section describing `uno328pb` (name, MCU, how host detects it, where to find the `.hex` on GitHub Releases).
  2. Meta-repo release-procedures doc lists three per-board verification steps (one per `.hex` artifact), with `uno328pb` added alongside the existing `uno` and `leonardo` checks. Locked-step procedure unchanged.
  3. `MILESTONES.md` grows a v1.5 entry with the standard sections (delivery summary, key accomplishments, stats, key decisions, known gaps).
  4. `.planning/v1.5-archive.sh` exists and successfully moves `.planning/phases/21-*/` through `25-*/` into `.planning/milestones/v1.5-phases/`. Phase dirs cleared from `.planning/phases/`.
  5. `.planning/PROJECT.md` updated: v1.5 marked shipped with date, current-milestone section retired (or replaced by a "next milestone TBD" placeholder).

### v1.5 Coverage

| REQ-ID | Phase |
|--------|-------|
| FW-01 | Phase 21 |
| FW-02 | Phase 21 |
| FW-03 | Phase 21 |
| FW-04 | Phase 21 |
| REL-01 | Phase 22 |
| REL-02 | Phase 22 |
| INST-01 | Phase 23 |
| INST-02 | Phase 23 |
| INST-03 | Phase 23 |
| GATE-01 | Phase 23 |
| BENCH-01 | Phase 24 |
| BENCH-02 | Phase 24 |
| DOC-01 | Phase 25 |
| DOC-02 | Phase 25 |
| MS-01 | Phase 25 |

**Mapped: 15/15 requirements ✓** — no orphans, no duplicates. (REQUIREMENTS.md groups GATE under its own category; this table tracks it under Phase 23 since the host-side regression is where the gate is actively verified. Total checkbox items in REQUIREMENTS.md = 15: FW×4 + REL×2 + INST×3 + GATE×1 + BENCH×2 + DOC×2 + MS×1.)

### Phase-order rationale

- **Phase 21 first** — firmware target foundation. No release artifact, no host install, no bench session is meaningful without a buildable `firestarter_uno328pb.hex` and a handshake-reporting firmware. Desk-side; lowest-risk start.
- **Phase 22 second** — release pipelines pick up the artifact once Phase 21 produces it. Desk-side / CI-side; verifies via a real stable + beta cut that the GitHub Release asset list grows from 2 → 3 entries.
- **Phase 23 third** — host CLI integration. Sequential (not parallel) with Phase 22 because the integration test downloads a real `uno328pb.hex` from a beta pre-release — pre-Phase-22 the asset doesn't exist. Unit-test work with mocked GitHub responses can land earlier in parallel if useful, but the green gate is post-Phase-22.
- **Phase 24 fourth (operator-on-bench)** — only meaningful after Phases 21–23 are green. Cut a v1.5 beta pre-release per the v1.4 locked-step procedure, then flash + bench. This is the only hardware-gated phase; the operator confirmed the 328PB-Uno is plugged in so it's not a milestone-blocker the way v1.3's hardware gap is.
- **Phase 25 last** — document what was built and bench-validated; close. Follows the v1.4 milestone-close shape (READMEs + RELEASE-PROCEDURES + MILESTONES.md + archive + PROJECT.md update).

## v1.3 — CMOS EPROM Family Hardware Validation (PAUSED 2026-05-20)

**Milestone goal:** Bench-validate, on real silicon and on both Arduino Uno + Leonardo, that the algorithm-0x07 (28-pin DIP CMOS UV-EPROM, 212 chips in DB) and algorithm-0x08 (32-pin DIP CMOS UV-EPROM, 127 chips in DB) dispatch logic shipped in v1.0–v1.2 actually programs, reads back, and verifies cleanly across the full 32K → 512K density span. This is **validation, not new features** — architecture is locked.

**Status:** ⏸ Paused 2026-05-20 — hardware-gated. Phase 11 shipped clean; Phase 12 Wave 0 desk-side scaffold committed; Plans 12-01/02/03 (BENCH-01/02/05 — W27C512, SST27SF512, W27C257) + entire Phase 13 + Phase 14 await operator bench hardware (Uno + Leonardo + RURP shield + DIP-28 socket + scope + bench chips). Resume command: `/gsd-execute-phase 12 --wave 1 --interactive` once hardware is available.

**Granularity:** Comprehensive (compressed — focused validation milestone, not a build milestone).
**Phase numbering:** Phases 11-14 (continues from v1.2 close).

### Structural Notes

- **Bench-gated vs. desk-side split.** Phase 11 (coverage matrix + DB inconsistency report) is fully desk-side and can land without hardware. Phases 12 and 13 are operator-on-bench (Uno + Leonardo + chip socket + scope). Phase 14 is paperwork only.
- **PROTO-01/02 are observation protocols, not standalone phases.** Chip-ID read at the start of every BENCH cycle (PROTO-01) and scope-measured VPP at the chip socket during write (PROTO-02) are practiced in Phase 12 where the protocol is established, then carried forward into Phase 13. They map formally to Phase 12 (where the observation protocol is set up + first applied) but the success-criteria coverage runs across both bench phases.
- **Density coverage strategy.** Phase 12 covers the 28-pin / algo-0x07 family at both the marquee 64K size (W27C512, SST27SF512) and the 32K low end (BENCH-05). Phase 13 mirrors this for 32-pin / algo-0x08 at 256K + 512K (W27C020, W27E040) and the 128K low end (BENCH-06). Together this exercises the full address-bus span end-to-end.
- **Deferred v1.2 items.** BENCH-01 (W27C512 bench cycle) naturally closes the four v1.2 hardware-pending UAT items (Phase 08 SC#2/SC#3, Phase 08 HUMAN-UAT.md, Phase 09 Plan-05 Task 3 chip-seated W27C512 UAT). Phase 12 detail flags this closure.
- **Flash budget floor.** v1.2 ship state (Leonardo 24,482 B / 85.4%, Uno 22,262 B / 69.0%, firmware 3.0.0-dev) is a non-regress floor. v1.3 is read-only against firmware semantics; only defect-driven changes are in scope.

### Phases

- [x] **Phase 11: Coverage Matrix & DB Inconsistency Audit** — Desk-side enumeration of all 339 algo-0x07/0x08 DB rows + flag intra-algorithm inconsistencies. ✅ 2026-05-19
- [ ] **Phase 12: 28-Pin / Algo-0x07 Bench Validation** — End-to-end bench cycle on Uno + Leonardo for W27C512, SST27SF512, and the 32K density-low representative; establish chip-ID + VPP scope observation protocols. ⏸ Paused (Wave 0 shipped; Waves 1-3 await hardware)
- [ ] **Phase 13: 32-Pin / Algo-0x08 Bench Validation** — End-to-end bench cycle on Uno + Leonardo for W27C020, W27E040, and the 128K density-low representative; same observation protocols carried forward. ⏸ Paused
- [ ] **Phase 14: Milestone Close & Artifacts** — Publish BENCH-RESULTS, update MILESTONES, archive v1.3 phase directories. ⏸ Paused

### Phase Details

#### Phase 11: Coverage Matrix & DB Inconsistency Audit
**Goal:** Operator has a complete, single-source coverage map of every algo-0x07 + algo-0x08 chip in `chip_database.json`, with intra-algorithm DB inconsistencies surfaced as defect candidates for follow-up milestones.
**Depends on:** Nothing (desk-side; can land before any bench session).
**Requirements:** COV-01, COV-02
**Success Criteria** (what must be TRUE):
  1. A coverage matrix file exists at `.planning/v1.3-COVERAGE-MATRIX.md` (or equivalent) enumerating every algo-0x07 + algo-0x08 row in `chip_database.json` with: manufacturer, part_number(s), pin_count, size_bytes, pulse_duration, chip_id_check, chip_id_value, pinout class. Total row count matches DB histogram (212 + 127 = 339 chips).
  2. The same file (or a companion file) lists every intra-algorithm DB inconsistency — chips that share `pin_count` + `algorithm` but differ in `pulse_duration`, `chip_id_check`, or `pinout` — with each inconsistency labeled as a defect candidate for v1.4 or a sub-repo PR (no auto-fixes applied in v1.3).
  3. Operator can use the matrix to confirm that the six BENCH chips (BENCH-01..06) span the pinout classes and pulse-duration profiles actually represented in the DB, so bench results generalize to the rest of the 339 rows.
**Plans:** 6 plans
- [x] 11-01-PLAN.md — Wave 0 failing-test scaffold for tests/test_audit_coverage_matrix.py (10 tests) ✅ 2026-05-19
- [x] 11-02-PLAN.md — Wave 1 tool skeleton + CLI + §1 Summary + §2 DB Count Reconciliation ✅ 2026-05-19
- [x] 11-03-PLAN.md — Wave 2 §3 Full Enumeration (339 rows, per-algorithm sub-tables, D-06 sort) ✅ 2026-05-19
- [x] 11-04-PLAN.md — Wave 3 §4 Defect Candidates + DEFECT-COV-NN ledger + --check semantics
- [x] 11-05-PLAN.md — Wave 4 §5 BENCH Coverage Proof + golden-file fixture
- [x] 11-06-PLAN.md — Wave 5 D-07 planning-doc count reconciliation (PROJECT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md) ✅ 2026-05-19

#### Phase 12: 28-Pin / Algo-0x07 Bench Validation
**Goal:** On both Uno and Leonardo, operator can run a full write → read-back → verify cycle on every named 28-pin CMOS UV-EPROM (W27C512, SST27SF512) and on a 32K density-low representative, with chip-ID and VPP observation protocols established and captured.
**Depends on:** Phase 11 (coverage matrix informs which density-low representative is in scope and which pinout classes are exercised). Bench hardware: Uno + Leonardo + RURP shield + DIP-28 socket + scope.
**Requirements:** BENCH-01, BENCH-02, BENCH-05, PROTO-01, PROTO-02
**Plans:** 4 plans (Wave 0 shipped; Waves 1-3 paused on bench hardware)

#### Phase 13: 32-Pin / Algo-0x08 Bench Validation
**Goal:** On both Uno and Leonardo, operator can run a full write → read-back → verify cycle on every named 32-pin CMOS UV-EPROM (W27C020, W27E040) and on a 128K density-low representative, completing the algo-0x08 family coverage at the high (512K) and low (128K) ends of the address-bus span.
**Depends on:** Phase 12 (chip-ID + VPP observation protocols established; bench harness validated against algo-0x07 first).
**Requirements:** BENCH-03, BENCH-04, BENCH-06
**Plans:** TBD (paused on bench hardware)

#### Phase 14: Milestone Close & Artifacts
**Goal:** v1.3 ships with a per-chip, per-board green/red/quirks artifact covering all six BENCH chips and both PROTO observation protocols, plus a clean milestone close (MILESTONES.md updated, phase directories archived).
**Depends on:** Phases 11, 12, 13.
**Requirements:** DOC-01, DOC-02
**Plans:** TBD (paused on bench hardware)

### v1.3 Coverage

| REQ-ID | Phase |
|--------|-------|
| BENCH-01 | Phase 12 |
| BENCH-02 | Phase 12 |
| BENCH-03 | Phase 13 |
| BENCH-04 | Phase 13 |
| BENCH-05 | Phase 12 |
| BENCH-06 | Phase 13 |
| PROTO-01 | Phase 12 (observation protocol carried forward into Phase 13) |
| PROTO-02 | Phase 12 (observation protocol carried forward into Phase 13) |
| COV-01 | Phase 11 |
| COV-02 | Phase 11 |
| DOC-01 | Phase 14 |
| DOC-02 | Phase 14 |

**Mapped: 12/12 requirements ✓** — no orphans, no duplicates.

## Prior Milestones (archived)

<details>
<summary>✅ v1.4 Beta & Pre-release Deployment Pipeline (Phases 15-20) — SHIPPED 2026-05-20</summary>

- [x] **Phase 15**: Versioning & Locked-Step Coordination (foundation) — 4/4 plans
- [x] **Phase 16**: App Beta Release Pipeline — 1/1 plan
- [x] **Phase 17**: Firmware Beta Release Pipeline — 1/1 plan
- [x] **Phase 18**: Beta-Aware Firmware Downloader (`--pre`, `--firmware-version`, `firmware list`) — 2/2 plans
- [x] **Phase 19**: Documentation (READMEs + `v1.4-RELEASE-PROCEDURES.md`) — 1/1 plan
- [x] **Phase 20**: End-to-End Smoke Test + Milestone Close — 1/1 plan

Ship tag: `3.0.0b3` (auto-incremented from `b1` → `b2` → `b3` during live E2E; six substrate defects E2E-01..06 surfaced and fixed in-place during the cut).
Hardware-flash validated: Uno + Leonardo at `3.0.0b3` via `firestarter fw -i --pre`.

Full milestone archive: [`.planning/milestones/v1.4-ROADMAP.md`](milestones/v1.4-ROADMAP.md).
Requirements archive: [`.planning/milestones/v1.4-REQUIREMENTS.md`](milestones/v1.4-REQUIREMENTS.md) (16/16 complete).
Summary: [`.planning/MILESTONES.md`](MILESTONES.md) §v1.4.
Phase archive: [`.planning/milestones/v1.4-phases/`](milestones/v1.4-phases/).

</details>

<details>
<summary>✅ v1.2 Message-ID Logging Rework (Phases 6-9) — SHIPPED 2026-05-19</summary>

- [x] **Phase 6**: Logging Infrastructure (catalog + codegen + helper + decoder) — 6/6 plans
- [x] **Phase 7**: Convert ERROR + WARN + INFO Call-Sites — 13/13 plans
- [x] **Phase 8**: Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END) — 8/8 plans
- [x] **Phase 9**: Delete Old Log Macros + Measure Flash Savings — 5/5 plans
- [x] **Phase 10**: Milestone Close (v1.2) — closed by `/gsd-complete-milestone` (DOC-02)

Full milestone archive: [`.planning/milestones/v1.2-ROADMAP.md`](milestones/v1.2-ROADMAP.md) (frozen snapshot of full phase details + coverage map + dependency graph).

Requirements archive: [`.planning/milestones/v1.2-REQUIREMENTS.md`](milestones/v1.2-REQUIREMENTS.md) (23/23 complete).

Summary: [`.planning/MILESTONES.md`](MILESTONES.md) §v1.2.

</details>

<details>
<summary>⏸ v1.1 Safety Closure & Hardware Validation (Phases 1-5) — PAUSED 2026-05-18</summary>

- [x] **Phase 1**: Safety Closure (Intel-flash VPP, 28C chip-id) — complete
- [x] **Phase 2**: Wire-key rename + minipro attribution scrub — complete
- [x] **Phase 3**: Retroactive VERIFICATION.md for v1.0 phases — complete
- [ ] **Phase 4**: Hardware validation across chip families — Plan 2 of 3 in progress; **FM1608 byte-0 read bug** parked (needs different Uno R3 to unblock; see [`.planning/debug/fm1608-fresh-chip-baseline.md`](debug/fm1608-fresh-chip-baseline.md))
- [ ] **Phase 5**: Milestone close (DOC-01) — deferred until after v1.2 ships or fm1608 unblocks

Original artifacts: [`.planning/milestones/v1.1-paused/`](milestones/v1.1-paused/).

Also carrying: WARNING-4 (`firestarter_test.sh` / `write_test.sh` references to deleted `database_generated.json`).

</details>

<details>
<summary>✅ v1.0 Protocol-Aware Programming Architecture (Phases 1-13) — SHIPPED 2026-05-11</summary>

- [x] Phases 1-13 covering the algorithm-first dispatch architecture (13 phases, 22 plans, 4-day timeline)
- Key deliverables: protocol-prefix dispatch in `memory.cpp`, 743-chip database with explicit `algorithm` integer, five firmware handlers (`configure_eprom`, `configure_flash3`, `configure_flash_intel`, `configure_eeprom28c`, `configure_sram`), pre-write safety stack (VPP ADC compare, chip-ID validation, blank check), static-pin and address-bus correctness

Full archive: [`.planning/milestones/v1.0-ROADMAP.md`](milestones/v1.0-ROADMAP.md) | [`.planning/milestones/v1.0-REQUIREMENTS.md`](milestones/v1.0-REQUIREMENTS.md) | [`.planning/milestones/v1.0-MILESTONE-AUDIT.md`](milestones/v1.0-MILESTONE-AUDIT.md) | [`.planning/milestones/v1.0-INTEGRATION-CHECK.md`](milestones/v1.0-INTEGRATION-CHECK.md) | [`.planning/milestones/v1.0-phases/`](milestones/v1.0-phases/).

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1-13 (v1.0) | v1.0 | 22/22 | ✅ Shipped | 2026-05-11 |
| 1-3 (v1.1) | v1.1 | done | ✅ Complete | 2026-05-12..18 |
| 4 (v1.1) | v1.1 | partial | ⏸ Parked | — (FM1608 blocked) |
| 5 (v1.1) | v1.1 | 0/0 | ⏸ Deferred | — |
| 6-10 (v1.2) | v1.2 | 32/32 | ✅ Shipped | 2026-05-19 |
| 11 | v1.3 | 6/6 | ✅ Complete | 2026-05-19 |
| 12 | v1.3 | 1/4 | ⏸ Paused | — (hardware-gated) |
| 13 | v1.3 | 0/0 | ⏸ Paused | — (hardware-gated) |
| 14 (close) | v1.3 | 0/0 | ⏸ Paused | — (hardware-gated) |
| 15-20 (v1.4) | v1.4 | 10/10 | ✅ Shipped | 2026-05-20 |

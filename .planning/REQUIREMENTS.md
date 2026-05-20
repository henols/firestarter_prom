# Milestone v1.5 — Arduino Uno (ATmega328PB) Board Support

**Created:** 2026-05-20
**Goal:** Ship `uno328pb` as a third first-class firmware target alongside `uno` and `leonardo`. End-to-end coverage: PlatformIO env + custom board definition → firmware handshake reports `uno328pb` → stable + beta release pipelines emit a third per-board `.hex` artifact → host CLI's `firestarter fw -i` installer flashes the right artifact when the device reports `uno328pb` → bench-validated EPROM write→read-back→verify cycle on the operator's plugged-in 328PB-Uno + RURP shield.

**Core constraint:** This is a **firmware port + CI/CD + a tiny host-side allowlist + one bench session** — no protocol changes, no algorithm-dispatch changes, no new chip support, no new CLI flags. The v1.4 beta/stable plumbing stays in place; v1.5 only widens the per-board artifact matrix from 2 → 3 and proves the third target on real silicon. Phase numbering continues at Phase 21 (v1.4 closed at Phase 20).

**Branch model:** Both sub-repos cut working branches off `beta` (per operator instruction). First v1.5 pre-release version cut from `beta` after Phases 21–23 are green; promotion to `main` (stable) follows the v1.4 beta → stable pattern only after Phase 24 bench-green.

> v1.3 (CMOS EPROM Family Hardware Validation) remains **PAUSED** as of 2026-05-20 (hardware-gated). v1.3 requirements (BENCH-01..06, PROTO-01..02, COV-01..02 complete, DOC-01..02) are archived at `.planning/milestones/v1.3-paused/REQUIREMENTS-at-pause.md` and will resume from there when the v1.3 bench hardware kit is available. v1.5 does NOT depend on v1.3 closure. The operator's 328PB-Uno may overlap with v1.3 BENCH-01's chip-of-interest (W27C512), but the v1.5 bench session is scoped to *proving the 328PB port*, not to closing v1.3's coverage matrix.

## v1.5 Requirements

### FW — Firmware build target (`uno328pb`)

The 328PB is pin-compatible with the 328P on Arduino-Uno I/O; firmware compiles against MiniCore's `ATmega328PB` MCU support without touching algorithm dispatch, JSON parser, or VPP control. PlatformIO grows a third AVR env so the existing build/test pipeline picks up the new target with no codegen changes.

- [ ] **FW-01**: `pio run -e uno328pb` builds a flashable `.hex` from `main` (and from `beta`) of the firmware sub-repo. The build uses `platform = MCUdude/MiniCore` (the established Arduino-framework support for ATmega328PB) and finishes green in CI with no warnings beyond the existing `uno`/`leonardo` baseline.
- [ ] **FW-02**: A custom PlatformIO board file `boards/uno328pb.json` exists in the firmware sub-repo and declares `mcu = atmega328pb`, an appropriate F_CPU for an Arduino-Uno-clock 328PB board (16 MHz default), upload protocol/baud matching the operator's bench Uno-328PB, and Arduino-Uno-compatible pin mapping. With this file present `board = uno328pb` is a valid env option and `env.GetProjectOption("board")` returns the literal string `uno328pb` so `name_firmware.py` emits `firestarter_uno328pb.hex` with no script change.
- [ ] **FW-03**: Firmware compiled from `[env:uno328pb]` emits the literal string `uno328pb` in the `<board>` slot of the `MSG_OK_FW_HANDSHAKE` payload (the `OK: FW: <version>:<board>` legacy text wire, per `firmware.py:check_current_firmware:101..117`). Source of truth: `-D RURP_BOARD_NAME=\"uno328pb\"` set per-env in `platformio.ini` (mirror of the existing `uno` and `leonardo` envs).
- [ ] **FW-04**: `pio test -e native` (the host-side Unity dispatch + messages suite) remains green after the v1.5 firmware sub-repo changes. The 328PB env addition is `[env:*]` config + a new board JSON; native test build is independent and must not regress.

### REL — Release pipeline artifacts

The two firmware-sub-repo workflows (stable `build.yml` and beta `beta-build.yml`) emit a third per-board `.hex` artifact. Both already build "everything in `default_envs`" via `pio run` and glob `firestarter_*.hex` for the release attachment — the change is to widen `default_envs` so `pio run` picks up `uno328pb`, and to confirm the glob still catches the new artifact end-to-end on a CI run.

- [ ] **REL-01**: Push to `firestarter/main` produces a GitHub Release (stable, `make_latest: true`) that carries `firestarter_uno328pb.hex` **in addition to** the existing `firestarter_uno.hex` and `firestarter_leonardo.hex` artifacts. Existing two artifacts remain byte-identical (modulo version-string drift from `update_version.py`) per GATE-01. Verified end-to-end by inspecting the release's asset list after a stable cut.
- [ ] **REL-02**: Push to `firestarter/beta` produces a GitHub Pre-release (`prerelease: true`, `make_latest: false`) that carries `firestarter_uno328pb.hex` in addition to the existing two per-board artifacts. Existing two artifacts remain byte-identical to a pre-v1.5 beta cut per GATE-01. Verified end-to-end by inspecting the pre-release's asset list after a beta cut.

### INST — Host CLI installer integration

The host CLI's `firestarter fw -i` flow already does `firestarter_{board}.hex` lookup driven by the firmware handshake's reported board name (`firmware.py:install_firmware:535..551`, `fetch_latest_release_info:141..156`). With FW-03 in place the lookup just works. v1.5 adds (a) any board-allowlist entry needed elsewhere in the host code (`avr_tool.py` upload profile, `constants.py` enum, etc.) and (b) a regression test that exercises the `uno328pb`-reporting code path. No new CLI flags.

- [ ] **INST-01**: When a device whose firmware reports `uno328pb` is connected, `firestarter fw -i` (stable, no flags) resolves the latest stable release's `firestarter_uno328pb.hex` asset URL, downloads it, and flashes it via `avr_tool.py` using a 328PB-appropriate upload profile. End-to-end success metric: the device, after flash, again identifies as `uno328pb` and runs the firmware handshake cleanly.
- [ ] **INST-02**: When a device whose firmware reports `uno328pb` is connected, `firestarter fw -i --pre` resolves the highest PEP 440 pre-release's `firestarter_uno328pb.hex` asset URL via the existing v1.4 `--pre` channel logic (`firmware.py:fetch_latest_release_info` + `_compare_versions`), downloads it, and flashes it.
- [ ] **INST-03**: `firestarter firmware list [--all|--pre|--stable]` (the v1.4 INST-04 listing surface) correctly enumerates `uno328pb` releases when a 328PB device is connected — same plain-text/JSON table shape as for `uno` and `leonardo`, scoped to the board the firmware handshake reports. No new flags; existing listing logic resolves the asset name from the connected-device board string per `fetch_latest_release_info:141..147`.

### GATE — Non-regression on existing boards

The v1.5 changes are additive — the two existing per-board paths (Uno-328P and Leonardo) must continue to behave identically.

- [ ] **GATE-01**: After v1.5 lands, a stable cut (push to `firestarter/main`) produces `firestarter_uno.hex` and `firestarter_leonardo.hex` byte-identical to a pre-v1.5 stable cut (modulo unavoidable version-string drift introduced by `update_version.py`). A beta cut (push to `firestarter/beta`) likewise produces byte-identical existing two artifacts. Stable-installed app's `firestarter fw -i` against a `uno`-reporting or `leonardo`-reporting device flashes the matching artifact with the same byte stream as pre-v1.5.

### BENCH — Operator-bench validation on real silicon

The operator's Arduino-Uno-form-factor board with an ATmega328PB chip + RURP shield is the test vehicle. v1.5 must prove (a) the v1.5 firmware flashes onto that board cleanly via the v1.5 release path, and (b) a real EPROM write→read-back→verify cycle on that board returns byte-identical results to what the regular `uno` target would on the same chip with the same shield.

- [ ] **BENCH-01**: After a v1.5 beta pre-release exists (REL-02 green), operator runs `firestarter fw -i --pre` connected to the 328PB-Uno + RURP shield. The host installs `firestarter_uno328pb.hex` from the pre-release asset, `avr_tool.py` reports a clean flash, and the device reboots into the v1.5 firmware. After reboot, `firestarter --hw` (or equivalent handshake-trigger command) reports the new v1.5 version and `board: uno328pb`. INST-02 + INST-01 are end-to-end-proven by this step.
- [ ] **BENCH-02**: With the same operator hardware (328PB-Uno + RURP shield + an operator-chosen EPROM in the socket — default W27C512, swap if the operator's chip kit differs), operator runs a full `firestarter write <chip>` → `firestarter read <chip>` → `firestarter verify <chip>` cycle. Write completes without error, read-back is byte-identical to the test image, verify reports PASS. VPP regulator engages at the expected millivolts for the chip's algorithm (per existing firmware behavior). Captured as a row in `.planning/v1.5-BENCH-RESULTS.md`.

### DOC — Documentation & operator guidance

- [ ] **DOC-01**: `firestarter/README.md` (firmware sub-repo) and `firestarter_app/README.md` (app sub-repo) each grow a one-paragraph entry for the third supported board in their "Supported boards" / "Hardware" section: name (`uno328pb`), MCU (ATmega328PB), how the host detects it (firmware handshake reports `uno328pb`), and where to find the `.hex` artifact on GitHub Releases (the asset list).
- [ ] **DOC-02**: Meta-repo `.planning/v1.4-RELEASE-PROCEDURES.md` (or the v1.5 successor — to be decided in the milestone close phase) is updated so the release-engineer checklist's per-board verification step lists three boards instead of two. The locked-step procedure itself (paired `beta` push, `BETA_VERSION` input, `lockstep-dryrun-fixture.sh`) is unchanged.

### MS — Milestone close

- [ ] **MS-01**: `.planning/MILESTONES.md` grows a v1.5 entry (delivery summary, key accomplishments, stats, key decisions, known gaps); v1.5 phase directories are archived under `.planning/milestones/v1.5-phases/` via a `v1.5-archive.sh` script; `.planning/PROJECT.md` is updated to mark v1.5 shipped. Closure runs after BENCH-01 + BENCH-02 are green.

## Future Requirements (deferred past v1.5)

Captured here so they don't get lost; not in v1.5 scope.

- **Use 328PB extra peripherals** — leverage the extra USART/TWI/SPI/Timer hardware (e.g. a second UART for debug breadcrumbs without disturbing the 250000-baud command channel) to claw back flash budget or improve diagnostics. Deferred — no current Firestarter use case forces it.
- **PE0–PE3 pin exposure** — the 328PB's four extra GPIO pins (PE0–PE3) could become additional control register bits if the RURP shield ever needs more strobe lines. Deferred — out of scope of current shield revision.
- **VID/PID-based board auto-detect** — replace handshake-based board identification with a USB descriptor probe before the firmware speaks. Deferred — current handshake works for all three boards and adds no operator friction.
- **Resume v1.3 BENCH-01..06 on the 328PB-Uno** — if the v1.5 bench session validates W27C512 cleanly on the 328PB-Uno, that *closes a subset* of v1.3 BENCH-01 by side effect, but only on the 328PB-Uno (v1.3 explicitly requires the standard Uno + Leonardo combination). The v1.3 milestone resume command and chip-coverage matrix are unchanged.

## Out of Scope (explicit exclusions)

- **328PB extra peripherals (USART1, TWI1, SPI1, Timer3/4, PE0–PE3)** — Firestarter only uses 328P-common I/O. v1.5 ships a 328P-compatible firmware on the 328PB MCU, not a 328PB-optimized firmware. Reason: any extra-peripheral use changes the firmware behavior matrix from "same as `uno`" to "different from `uno`", which would force a parallel test suite. Out of scope until a use case forces it (see Future Requirements above).
- **Bootloader provisioning** — operator is responsible for flashing an appropriate Arduino-Uno-compatible bootloader to the 328PB chip before v1.5's `firestarter fw -i` can flash app firmware over it. Standard MiniCore bootloader covers this. Reason: bootloader provisioning is a one-time pre-Firestarter step that pre-dates Firestarter's involvement with the board.
- **Host-side VID/PID-based board auto-detect** — the firmware handshake remains the source of truth for board identification. Reason: handshake works for `uno` and `leonardo` today with zero false positives; adding a parallel detection mechanism doubles the surface for ambiguous cases.
- **New chip support, new algorithms, new wire-protocol fields, new firmware behavior** — v1.5 is a *port to a new MCU package*. Algorithm dispatch in `memory.cpp::configure_memory`, JSON wire format, VPP/VPE control, chip database, and host CLI verbs are byte-identical to v1.4 behavior on the 328PB target. Reason: scope creep would entangle a clean port with semantic changes.
- **Cross-board flash-budget rework, message-ID catalog edits, codegen changes** — the v1.2 message-ID catalog and v1.0 algorithm dispatch are stable. Reason: same as above — keep the port surgical.
- **CMOS EPROM bench-coverage matrix close-out (v1.3)** — the operator's 328PB-Uno bench validation is for *proving the v1.5 port*, not for closing v1.3 BENCH-01..06. Reason: v1.3 explicitly requires the regular Uno + Leonardo combination; running BENCH-01 on a 328PB-Uno wouldn't satisfy v1.3's coverage gate. v1.3 stays paused.
- **TestPyPI re-introduction, auto-promotion beta→stable** — these v1.4 deferrals remain deferred.

## Traceability

Filled in by the roadmap. See `.planning/ROADMAP.md` v1.5 section for the phase ↔ REQ-ID mapping.

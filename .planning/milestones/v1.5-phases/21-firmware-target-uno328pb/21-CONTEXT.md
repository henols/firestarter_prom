# Phase 21: Firmware Target — `uno328pb` - Context

**Gathered:** 2026-05-20
**Status:** Ready for planning
**Source:** `/gsd-discuss-phase 21` (interactive — 3 of 5 gray areas discussed; 2 routed to planner / cross-phase notes)

<domain>
## Phase Boundary

Phase 21 delivers a **buildable, handshake-correct `[env:uno328pb]` firmware target** in the `firestarter/` sub-repo, additive to the existing `uno` + `leonardo` envs, with the host-side native suite (`pio test -e native`) staying green. Concretely:

- `pio run -e uno328pb` from a clean checkout of `firestarter/beta` produces `.pio/build/uno328pb/firestarter_uno328pb.hex` (no errors, no new warnings vs the uno/leonardo baseline) — FW-01.
- The handshake (`OK: FW: <version>:<board>` text wire emitted by `fw_get_version()` at [firestarter/src/hardware_operations.cpp:82-92](firestarter/src/hardware_operations.cpp#L82-L92) via `FW_VERSION = VERSION ":" RURP_BOARD_NAME` at [firestarter/include/firestarter.h:16](firestarter/include/firestarter.h#L16)) emits the literal string `uno328pb` in the `<board>` slot — FW-03.
- `pio test -e native` (host-side Unity dispatch + messages suites) stays green — FW-04.
- `firestarter_uno.hex` + `firestarter_leonardo.hex` remain byte-identical to a `firestarter/beta` tip `5fd751e` pre-v1.5 cut (modulo version-string drift) — GATE-1.5 obligation.

**Scope deviation from REQUIREMENTS.md FW-02 (this phase, this CONTEXT — see D-08):** REQUIREMENTS.md FW-02 currently locks "a custom PlatformIO board file `boards/uno328pb.json` exists" as the board-id mechanism. This phase **amends FW-02** to drop the custom JSON entirely and instead rework `firestarter/name_firmware.py` to derive PROGNAME from the `-D RURP_BOARD_NAME` build flag. The board-id triple (board-id = artifact-name = handshake-string) is preserved with a single source of truth (`RURP_BOARD_NAME` only). The amendment must land in `.planning/REQUIREMENTS.md` before the phase ships (planner owns the edit).

**In scope (Phase 21):**

1. Edit `firestarter/platformio.ini` — add `[env:uno328pb]` (after `[env:uno]`, before `[env:leonardo]` so the two 328-family envs are visually grouped). No change to `[platformio] default_envs` in this phase (see D-13 cross-phase note).
2. Rework `firestarter/name_firmware.py` — replace `board = env.GetProjectOption("board")` with a function that parses the `-D RURP_BOARD_NAME=\"X\"` token out of the per-env build_flags list, extracts `X`, and sets PROGNAME = `firestarter_X`. The existing `[env:uno]` and `[env:leonardo]` already declare `-D RURP_BOARD_NAME=\"${this.board}\"`, so they continue to emit `firestarter_uno.hex` and `firestarter_leonardo.hex` byte-identically.
3. Widen 4 `ARDUINO_AVR_UNO` macro guards atomically (single commit) to include `ARDUINO_AVR_ATmega328PB` so the existing Uno board-setup code compiles into the 328PB target (D-01).
4. Capture pre-v1.5 baseline hex files at `.planning/v1.5/baselines/firestarter_uno.hex` + `.planning/v1.5/baselines/firestarter_leonardo.hex` (from `firestarter/beta` tip `5fd751e`); use them as a GATE-1.5 byte-identity gate in the phase's verification step (D-05).
5. Amend `.planning/REQUIREMENTS.md` FW-02 inline (drop the `boards/uno328pb.json` requirement; reframe FW-02 around the `name_firmware.py` rework + `RURP_BOARD_NAME` triple) — planner-owned edit; the milestone-requirements ledger stays consistent before Phase 22 ingests it.

**Out of scope (Phase 21 — explicitly):**

- `firestarter_app/firestarter/firmware.py` host avrdude profile table (lines 417-423) — adding a `uno328pb` branch to the `if board.lower() == "leonardo"` chain is **Phase 23 — INST work** per REQUIREMENTS.md INST-01..03. Captured as cross-phase hand-off (see Deferred / Phase 23).
- `[platformio] default_envs` update — Phase 21 ships `default_envs = uno, leonardo` unchanged. Phase 22 (REL) owns widening it to `uno, leonardo, uno328pb` (or `uno, uno328pb, leonardo` to match platformio.ini section order — see D-13).
- The `boards/uno328pb.json` file — Path B (D-08) explicitly drops the file. No `boards/` directory contents are created or modified by this phase.
- Any change to `firestarter/src/proms/*.cpp` (algorithm dispatch), `firestarter/include/messages.h` (catalog), or `firestarter/src/json_parser.c` (wire format). The MCU port is byte-identical behavior; only the macro-guard widening touches algorithm-adjacent code (rurp_common.cpp bandgap math + rurp_register_utils.h FM1608 workaround — both reach the new env, none change semantics on the existing two).
- 328PB peripheral exploration (USART1, TWI1, SPI1, Timer3/4, PE0–PE3) — out-of-scope per PROJECT.md / REQUIREMENTS.md v1.5 locked decisions.
- Bench flash on the operator's 328PB-Uno — Phase 24 owns this; Phase 21 succeeds at the desk-side build/handshake/native-test gate.

</domain>

<decisions>
## Implementation Decisions

### Board macro routing (board.cpp guard widening)

- **D-01: Widen all 4 `ARDUINO_AVR_UNO` macro guards atomically** to include `ARDUINO_AVR_ATmega328PB`, in a single commit:
  1. `firestarter/src/boards/uno_rurp_shield.cpp:8` — top-level `#ifdef ARDUINO_AVR_UNO` block (board setup, USER_BUTTON, com_mode global, `rurp_board_setup()`).
  2. `firestarter/src/boards/rurp_common.cpp:10` — outer `#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_LEONARDO)` gating the entire ADC / bandgap / Vcc / voltage code.
  3. `firestarter/src/boards/rurp_common.cpp:23` — inner `#if defined(ARDUINO_AVR_UNO)` controlling the ADMUX bandgap channel mask (the 328PB has the same ADMUX bandgap bits as the 328P).
  4. `firestarter/include/rurp_register_utils.h:63` — the FM1608 PORTD-bit-6 pre-clear + 4-NOP settle workaround (PORTD layout on the Arduino-Uno-shaped 328PB is identical to the 328P; the workaround applies if/when an Arduino-Uno-shaped 328PB ever exhibits the same FM1608 byte-0 read bug parked in v1.1).

  Rationale: the 328PB is a strict superset of the 328P for the registers Firestarter touches (PORTB/C/D, DDR*, PIN*, ADMUX bandgap channel, ADCSRA). All four widened blocks are byte-correct on the new MCU. Anything less than "all 4" produces a partially-set-up board (e.g. `rurp_common.cpp:28` is `#error "Unsupported board"` — the second site would still trip the error). Atomic = no half-state in any commit.

- **D-02: Guard style = repeat inline `defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)` at each of the 4 sites.** Do NOT introduce an umbrella macro (`RURP_BOARD_UNO_FAMILY` or similar) in `rurp_shield.h`. Rationale: 4 sites is below the threshold where an indirection-layer macro pays for itself; inline self-documentation + `grep -r "ARDUINO_AVR_"` discoverability is worth the 4-place update cost if a future board ever joins this family. The "umbrella macro" path is a legitimate next step IF v1.6+ adds another 328-family Arduino board; otherwise this is premature abstraction.

- **D-03: No new native tests for the widened guards.** `pio test -e native` already runs with `-D RURP_BOARD_NAME=\"native\"` (per [firestarter/CLAUDE.md](firestarter/CLAUDE.md) "Native Test Environment" section) — the new macro conditions resolve to false in the native env, so no test can exercise them without simulating AVR register writes (outside the existing `host_stubs.cpp` scope). Validation happens at the build site (`pio run -e uno328pb` link-clean) and on real silicon in Phase 24.

- **D-04: GATE-1.5 verification = `cmp -s` against checked-in baseline hex files.** Phase 21 captures `firestarter_uno.hex` + `firestarter_leonardo.hex` from `firestarter/beta` tip `5fd751e` (the pre-v1.5 baseline per PROJECT.md / STATE.md), commits them to `.planning/v1.5/baselines/` in the meta-repo (NOT the firmware sub-repo — they're planning artifacts), and the phase's verification step runs `cmp -s .pio/build/uno/firestarter_uno.hex .planning/v1.5/baselines/firestarter_uno.hex` after the macro widening (and similarly for leonardo). The version-string region drifts via `update_version.py` between cuts; the comparison normalizes that region (the v1.4 `lockstep-dryrun-fixture.sh` pattern at [firestarter/.github/scripts/update_version.py](firestarter/.github/scripts/update_version.py) is the precedent — planner verifies the exact byte offsets).

  Note: GATE-1.5 byte-identity must hold AFTER both the macro widening AND the `name_firmware.py` rework. If either change perturbs the uno or leonardo .hex outputs, that's a phase-level fail.

### `boards/uno328pb.json` — Path B (drop the JSON, rework name_firmware.py)

- **D-05 (amends REQUIREMENTS.md FW-02): Path B. No custom `boards/uno328pb.json` file is created.** Rationale: MiniCore (`platform = MCUdude/MiniCore`) ships a built-in `ATmega328PB` board JSON. Setting `[env:uno328pb] board = ATmega328PB` would compile fine, but the existing `firestarter/name_firmware.py` derives PROGNAME from `env.GetProjectOption("board")` — that would produce `firestarter_ATmega328PB.hex`, which breaks the locked **board-id = artifact-name = handshake-string** triple (PROJECT.md "Structural Notes"). Path B keeps the triple intact with a single source of truth (`RURP_BOARD_NAME`).

- **D-06: PROGNAME source = parse `-D RURP_BOARD_NAME=\"X\"` from `env['BUILD_FLAGS']`** in the reworked `name_firmware.py`. The script extracts `X` and sets `PROGNAME = "firestarter_%s" % X`. This makes the handshake-string flag the single source of truth for both the artifact name AND the firmware-emitted board string — they can no longer drift. For `[env:uno]` and `[env:leonardo]` (which already declare `-D RURP_BOARD_NAME=\"${this.board}\"`), this resolves to `firestarter_uno` and `firestarter_leonardo` respectively, preserving GATE-1.5 byte-identity on the artifact filename and content.

  Implementation guidance for the script: parse the build_flags list (PIO presents this as `env['BUILD_FLAGS']` — a list of strings); search for the token that matches `-D RURP_BOARD_NAME=\"<value>\"`; extract `<value>`; fail loudly with a clear message if not found (any env without this flag is a misconfiguration after this phase). Defensive: also handle the case where the flag is split across list entries (PIO sometimes joins them, sometimes doesn't — researcher verifies).

- **D-07: `[env:uno328pb]` block content (no `boards/` file, mirror `[env:uno]` flags):**
  ```ini
  [env:uno328pb]
  platform = MCUdude/MiniCore
  board = ATmega328PB
  framework = arduino
  build_flags =
      ${env.build_flags}
      -D RURP_BOARD_NAME=\"uno328pb\"
      -D SERIAL_ON_IO
  ```
  Notes:
  - `board = ATmega328PB` uses MiniCore's built-in board definition verbatim — Arduino-Uno-compatible pin mapping is MiniCore's default for that variant. No `board_build.variant`, `upload_protocol`, or `upload_speed` overrides in this phase (Phase 24 bench session is the place to lock those if defaults fail on the operator's bench bootloader).
  - `RURP_BOARD_NAME` is hard-coded to the literal `\"uno328pb\"` (NOT `\"${this.board}\"` — because `${this.board}` would resolve to `ATmega328PB`, breaking the triple). The flag IS the source of truth; the PIO `board` setting drives only the MiniCore compile/link, never the artifact name.
  - `DATA_BUFFER_SIZE` stays at the default 512 — inherited from [firestarter/include/firestarter.h:18-19](firestarter/include/firestarter.h#L18-L19) (`#ifndef DATA_BUFFER_SIZE / #define DATA_BUFFER_SIZE 512`). Same as `[env:uno]`, which doesn't declare it explicitly either.
  - `SERIAL_ON_IO` mirrors `[env:uno]` — 328PB-Uno wires USART0 to FTDI via PD0/PD1 just like the regular Uno, so the same gating applies.

- **D-08 (`platformio.ini` section placement): `[env:uno328pb]` is inserted between `[env:uno]` and `[env:leonardo]`** — section order becomes `[env:uno]` → `[env:uno328pb]` → `[env:leonardo]` → `[env:native]`. Rationale: groups the two 328-family AVR envs visually adjacent, signaling that they share the 328-family register layout (and thus the macro widening from D-01). Phase 22's `default_envs` widening should match this order (`uno, uno328pb, leonardo`) — ROADMAP Phase 22 SC#1 currently lists `default_envs = uno, leonardo, uno328pb`; planner-for-Phase-22 should realign that ordering before ingesting (cross-phase note D-12).

- **D-09: REQUIREMENTS.md FW-02 amendment must land before Phase 21 ships.** The planner owns the edit. New FW-02 text should reframe around: (a) `[env:uno328pb]` exists in platformio.ini with `board = ATmega328PB` (MiniCore built-in) and `-D RURP_BOARD_NAME=\"uno328pb\"`; (b) `name_firmware.py` derives PROGNAME from `RURP_BOARD_NAME`; (c) the locked source-of-truth for the board-id triple is the `RURP_BOARD_NAME` build flag. No `boards/uno328pb.json` requirement remains.

### Cross-phase hand-offs (Phase 22 / 23 / planner)

- **D-10 (HAND-OFF → Phase 23): Host CLI avrdude profile for `uno328pb`.** [firestarter_app/firestarter/firmware.py:417-423](firestarter_app/firestarter/firmware.py#L417-L423) — the `_flash_with_avrdude` defaults are `(atmega328p, arduino, 115200)` for Uno and `(atmega32u4, avr109, 57600)` for Leonardo. There is **no `uno328pb` branch**. A 328PB device reporting `uno328pb` would fall through to the Uno defaults, and `avrdude -p atmega328p` against a real 328PB signature mismatches (0x1E 0x95 **0x16** vs 0x1E 0x95 0x0F). Phase 23 INST-01 SC#1 must add the branch: `if board.lower() == "uno328pb": partno = "atmega328pb"; programmer_id = "arduino" (or "urclock" — match the MiniCore bootloader the operator flashes); baud_rate = 115200`. Verify against the operator's actual bench bootloader during Phase 24. (See REQUIREMENTS.md INST-01..03 + ROADMAP.md Phase 23 SC#1.)

- **D-11 (HAND-OFF → Phase 22): `default_envs` widening.** Phase 21 does NOT modify `[platformio] default_envs` — it stays `uno, leonardo`. Phase 22 (REL) takes over: REL-01 / REL-02 require the release workflows to emit `firestarter_uno328pb.hex` as a third artifact, which `pio run` will only do if `uno328pb` is in `default_envs`. Phase 22 should set `default_envs = uno, uno328pb, leonardo` (matching D-08's `.ini` section order) OR `default_envs = uno, leonardo, uno328pb` (matching ROADMAP Phase 22 SC#1's current literal) — Phase 22 planner picks consistency with D-08 over consistency with ROADMAP SC#1 (the ROADMAP text is the older artifact).

- **D-12 (HAND-OFF → Phase 22 planner / ROADMAP touch-up): Realign Phase 22 SC#1's `default_envs` literal with D-08's section order.** Currently ROADMAP.md Phase 22 SC#1 says `default_envs = uno, leonardo, uno328pb`. After Phase 21's `.ini` reorder (D-08), Phase 22 SC#1's literal should read `default_envs = uno, uno328pb, leonardo` to match. Minor edit; planner for Phase 22 owns it OR plan-phase-21 amends ROADMAP inline alongside the REQUIREMENTS FW-02 amendment.

- **D-13 (HAND-OFF → planner): native-test scope for Phase 21.** No new native tests are added by Phase 21 (per D-03). The verification surface for FW-03 SC#4 (handshake emits literal `uno328pb`) is **build-time .elf symbol grep**: after `pio run -e uno328pb`, run `avr-strings -a .pio/build/uno328pb/firmware.elf | grep -F uno328pb` (or `avr-nm` + objdump on `.rodata`) and confirm the literal byte sequence is present in the binary's read-only data section. This is a Phase 21 verification gate, not a checked-in test. Planner: capture this as a verification step in PLAN.md.

### Claude's Discretion

- The exact byte offsets in the `firestarter_uno.hex` / `firestarter_leonardo.hex` baseline files where `update_version.py` perturbs bytes (and thus need normalization in the `cmp` GATE-1.5 check) — research surface for the planner. Existing [firestarter/.github/scripts/update_version.py](firestarter/.github/scripts/update_version.py) is the source.
- The exact parsing form in `name_firmware.py` for `-D RURP_BOARD_NAME` (regex vs `shlex`-style split vs PIO's `env.ParseFlags`) — planner / researcher picks based on what PIO's SCons `env['BUILD_FLAGS']` actually exposes at script time. Failure mode for missing flag = `Exit(1)` with a clear error message.
- Whether to commit the two baseline hex files via Git LFS or as plain blobs (Git LFS not currently configured in the meta-repo) — likely plain blobs since AVR hex is ~70 KB max per board and the meta-repo otherwise tracks only text. Planner confirms.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone & phase contracts (locked decisions)
- `.planning/ROADMAP.md` (v1.5 section) — Phase 21 goal + success criteria (5 SC) + dependency chain (Phase 22 picks up the artifact, Phase 24 bench-validates).
- `.planning/REQUIREMENTS.md` — FW-01..FW-04 requirements; FW-02 currently locks `boards/uno328pb.json`. **D-09 amends FW-02 to drop the JSON.** This phase MUST land that amendment inline.
- `.planning/PROJECT.md` (v1.5 Locked Decisions) — MiniCore platform, 512 B buffer, board-id = artifact-name = handshake-string triple, branches off `beta` in firestarter sub-repo, GATE-1.5 byte-identity obligation.
- `.planning/STATE.md` (v1.5 Decisions, lines 141-153) — same lock set as PROJECT.md, plus phase-numbering continuation (Phase 21).

### Firmware sub-repo (edit targets)
- `firestarter/platformio.ini` — env config; Phase 21 inserts `[env:uno328pb]` between `[env:uno]` and `[env:leonardo]` (D-08).
- `firestarter/name_firmware.py` — Phase 21 rewrites this script to derive PROGNAME from `-D RURP_BOARD_NAME` (D-06). Current 3-line implementation: `Import("env"); board = env.GetProjectOption("board"); env.Replace(PROGNAME="firestarter_%s" % board)`.
- `firestarter/include/firestarter.h` (line 16) — `#define FW_VERSION VERSION ":" RURP_BOARD_NAME` — the handshake string macro; do NOT modify.
- `firestarter/src/hardware_operations.cpp` (lines 82-92) — `fw_get_version()` emits `OK: FW: <version>:<board>` via `SERIAL_PORT.println(FW_VERSION)`. Read-only reference.
- `firestarter/src/boards/uno_rurp_shield.cpp` (line 8) — guard widening site #1 (D-01).
- `firestarter/src/boards/rurp_common.cpp` (lines 10, 23) — guard widening sites #2 + #3 (D-01).
- `firestarter/include/rurp_register_utils.h` (line 63) — guard widening site #4 (D-01); FM1608 PORTD-bit-6 workaround.
- `firestarter/src/boards/leonardo_rurp_shield.cpp` (line 9) — read-only reference for guard-style symmetry.
- `firestarter/CLAUDE.md` — firmware sub-repo CLAUDE.md (native test env layout, dispatch-table source-of-truth notes).

### Host sub-repo (Phase 23 hand-off only — NOT Phase 21 edit target)
- `firestarter_app/firestarter/firmware.py` (lines 417-423) — `_flash_with_avrdude` board → (partno, programmer_id, baud_rate) table. Cross-phase note D-10: Phase 23 owns adding the `uno328pb` branch.

### Cross-phase precedents (read for pattern)
- `firestarter/.github/scripts/update_version.py` — the version-string injection script; relevant for understanding which byte regions in the .hex output drift between cuts (D-04 GATE-1.5 cmp normalization).
- `.planning/phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md` (or its v1.5 cousin once written) — v1.4 byte-identity verification pattern that D-04 mirrors.
- `.planning/v1.4-RELEASE-PROCEDURES.md` — release-engineer per-board cut workflow; Phase 22 widens to three boards, Phase 21 stays at two.

### Spike/sketch findings
None apparent for Phase 21. (No `.planning/spikes/` or `.planning/sketches/` artifacts in the v1.5 area.)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`firestarter/name_firmware.py`** — currently 3 lines; SCons extra_script wired at `[env]` level via `extra_scripts = pre:name_firmware.py`. The script runs once per env. Phase 21 rewrites the body but the wiring is reused. The `-D RURP_BOARD_NAME=\"X\"` build_flag is already declared by `[env:uno]` and `[env:leonardo]` — Phase 21 leverages that, not adds new flags.
- **`firestarter/include/firestarter.h:16` — `FW_VERSION` macro** — concatenates `VERSION` (from `firestarter/include/version.h`, written by `update_version.py`) with `:` and `RURP_BOARD_NAME` (from build_flag). Already proven for `uno` + `leonardo`; reused as-is for `uno328pb`. No edit.
- **`firestarter/src/hardware_operations.cpp` — `fw_get_version()`** — handshake emit site; emits `OK: FW: ` literal prefix + `FW_VERSION` content. Already correctly board-aware. No edit.
- **`firestarter/src/boards/rurp_common.cpp` — ADC bandgap / Vcc / voltage math** — currently gated on `ARDUINO_AVR_UNO || ARDUINO_AVR_LEONARDO`. After D-01 widening, the same code base serves uno + uno328pb + leonardo. Math is identical; the 328PB shares the 328P's ADMUX bandgap channel encoding.
- **`firestarter/src/boards/uno_rurp_shield.cpp` — `rurp_board_setup()`** — sets PORTB output mask, initializes register-select lines, configures USER_BUTTON input. Wiring is Arduino-Uno-shaped; widening the guard makes the same setup reach the 328PB binary.

### Established Patterns

- **`extra_scripts = pre:script.py` is `[env]`-scoped (inherited by all envs)** — so the `name_firmware.py` rework must be backward-compatible with the existing two envs' build_flags shape. D-06's parser-form choice (regex / shlex / ParseFlags) must handle the current `[env:uno]` and `[env:leonardo]` declarations.
- **`build_flags = ${env.build_flags} + per-env flags`** — current pattern in `[env:uno]` and `[env:leonardo]`. `[env:uno328pb]` follows the same shape (D-07).
- **Per-env `-D RURP_BOARD_NAME=\"X\"`** — established in v1.0 and consumed by `FW_VERSION` macro. Phase 21 extends consumption to also drive the PROGNAME (D-06).
- **GATE-1.5 byte-identity precedent** — v1.4 ship locked `firestarter_uno.hex` + `firestarter_leonardo.hex` byte-identical via `lockstep-dryrun-fixture.sh`. Phase 21 reuses this gate shape: capture baseline hex from `firestarter/beta` tip `5fd751e`, post-change `cmp -s` with version-region normalization (D-04).
- **Phase 9 / LFW-05 — handshake emits a lone surviving text-format line** at [firestarter/src/hardware_operations.cpp:84-89](firestarter/src/hardware_operations.cpp#L84-L89). The host parses it at [firestarter_app/firestarter/firmware.py:101-117](firestarter_app/firestarter/firmware.py#L101-L117) — `payload = msg[3:].lstrip() if msg.startswith("FW:") else msg; parts = payload.split(":", 1); board_name = parts[1].strip()`. The board string `uno328pb` flows from `RURP_BOARD_NAME` straight through this text channel; FW-03 + INST-01 (Phase 23) chain works zero-touch on the host parser.

### Integration Points

- **Phase 22 (REL) consumes the `.hex`** — Phase 21 produces `.pio/build/uno328pb/firestarter_uno328pb.hex`; Phase 22's `build.yml` + `beta-build.yml` glob `**/firestarter_*.hex` will pick it up automatically once `default_envs` widens (D-11 / D-12). No release-pipeline change needed in Phase 21.
- **Phase 23 (INST) consumes the handshake string** — once `uno328pb`-reporting firmware exists (Phase 21 output), Phase 23 wires the avrdude profile entry (D-10 hand-off) + adds a regression test exercising the `uno328pb` code path.
- **Phase 24 (BENCH) consumes the .hex via the host CLI** — after Phase 22 + 23 land, the operator runs `firestarter fw -i --pre` against the 328PB-Uno, which (per the working chain) downloads `firestarter_uno328pb.hex` from a beta pre-release and flashes it via the new avrdude profile.

</code_context>

<specifics>
## Specific Ideas

- **Path B (Drop the boards/ file) was a user-driven pivot from FW-02 as originally written.** Operator question "Isent there a predefined json for the atmega328pb that we can use" → realization that MiniCore ships a built-in `ATmega328PB` board JSON → realization that the only thing the custom JSON existed for was the artifact-name derivation → solving via `name_firmware.py` rework collapses two requirements (custom JSON + per-env board entry) into one (per-env `-D RURP_BOARD_NAME` flag) with a single source of truth. The operator's framing "does we really need to do this?" surfaced a load-bearing simplification.
- **`[env:uno328pb]` ordering between `[env:uno]` and `[env:leonardo]`** was a user-overridden recommendation (Claude suggested "after [env:leonardo]"; operator picked "before [env:leonardo] grouping 328-family"). The pattern signal: the operator reads `platformio.ini` as a board taxonomy, not a chronological history. Future env additions should follow MCU-family grouping (e.g. a hypothetical `mega2560` would go after `leonardo`).
- **Atomic 4-site guard widening** rather than minimal (`uno_rurp_shield.cpp:8` only) — Claude recommendation surfaced the half-state risk (`rurp_common.cpp:28` `#error "Unsupported board"`) and the operator confirmed atomic. Pattern: macro guards that share a board family should widen together.

</specifics>

<deferred>
## Deferred Ideas

- **Per-env `custom_prog_name` PIO option** as a PROGNAME source instead of parsing `-D RURP_BOARD_NAME` (an alternative considered in D-06). If `name_firmware.py`'s flag-parser proves brittle (e.g. PIO's SCons env exposes build_flags in a form that's hard to grep reliably), revisit Path B's PROGNAME source. Today's pick stands.
- **Umbrella macro `RURP_BOARD_UNO_FAMILY`** in `rurp_shield.h` — deferred per D-02 as premature abstraction for 4 sites + 1 new board. Reconsider in v1.6+ if another 328-family Arduino target lands.
- **Static-assert / .elf-grep CI step** for the `RURP_BOARD_NAME` literal — deferred from D-13 (FW-03 verification stays a single Phase 21 step, not an ongoing CI gate). Phase 22 can revisit if it wants a per-cut release-pipeline check.
- **`board_build.variant`, `upload_protocol`, `upload_speed` explicit overrides in `[env:uno328pb]`** — deferred from D-07. MiniCore's defaults for ATmega328PB are accepted as-is in Phase 21. Phase 24 (bench) is the place to lock these if defaults fail on the operator's bench bootloader.
- **MiniCore version pinning** — `platform = MCUdude/MiniCore` resolves to whatever PIO has cached / latest available. Pinning to a specific MiniCore version (e.g. `platform = MCUdude/MiniCore@^3.0.0`) would lock the toolchain shape and reduce GATE-1.5 byte-identity surprises across CI runners. Deferred — Phase 22 may want to set this once CI cuts confirm the version is stable.
- **328PB extra peripherals (USART1, TWI1, SPI1, Timer3/4, PE0–PE3)** — locked out-of-scope at milestone level (REQUIREMENTS.md / PROJECT.md). Future milestone if a Firestarter feature ever forces it.
- **Resume v1.3 BENCH-01..06 on the 328PB-Uno** — locked deferred at milestone level (REQUIREMENTS.md "Future Requirements"). The Phase 24 bench session is for proving the v1.5 port, not for closing v1.3 BENCH coverage gates.

</deferred>

---

*Phase: 21-firmware-target-uno328pb*
*Context gathered: 2026-05-20*

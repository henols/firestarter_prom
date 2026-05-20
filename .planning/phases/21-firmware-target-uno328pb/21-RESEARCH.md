# Phase 21: Firmware Target — `uno328pb` - Research

**Researched:** 2026-05-20
**Domain:** PlatformIO AVR build configuration + Arduino preprocessor-macro routing + SCons extra_script + Intel HEX byte-identity verification
**Confidence:** HIGH (build configuration, macro routing, SCons extra_script parsing); MEDIUM (GATE-1.5 hex normalization — no existing precedent in repo, design surface for the planner)

## Summary

Phase 21 adds a third PlatformIO env (`[env:uno328pb]`) and widens four `ARDUINO_AVR_UNO` macro guards to also fire when `ARDUINO_AVR_ATmega328PB` is defined. The build resolves through PlatformIO's **built-in `atmelavr` platform** (NOT a separately-installed `MCUdude/MiniCore` PlatformIO platform — the official `platformio/atmelavr` 5.2.0 board file `boards/ATmega328PB.json` already ships with `build.core = "MiniCore"` baked in and defines `-DARDUINO_AVR_ATmega328PB` via `build.extra_flags`). The CONTEXT.md D-07 line `platform = MCUdude/MiniCore` is a notation snag: PIO accepts `platform = atmelavr` + `board = ATmega328PB` and resolves the MiniCore core internally. The planner should confirm whether to mirror `[env:uno]`'s `platform = atmelavr` exactly (recommended) or use the alternative external-package syntax.

The PROGNAME rework in `name_firmware.py` (CONTEXT D-06) is implementable via PIO's `env.ParseFlags(env.GetProjectOption("build_flags"))` → `CPPDEFINES` list. Each `-D NAME=value` entry surfaces as a 2-tuple `(NAME, value)` in the parsed list. The script extracts the `RURP_BOARD_NAME` tuple's value, strips the embedded `\"` quoting that PIO leaves in place, and sets `PROGNAME = "firestarter_<value>"`. Defensive: raise (Exit(1)) on missing flag.

GATE-1.5 byte-identity check is the load-bearing risk. Intel HEX records embed a per-line checksum; flipping any data byte changes both the data byte and its line's last byte. The version string (`#define VERSION "3.0.0b2"` in `version.h`, written by `update_version.py`) lands in `.rodata` and surfaces in the `.hex` output as a contiguous run of ASCII bytes inside one or more HEX records. The naive `cmp -s` against a stale baseline will tear on every version bump. Strategy: capture the baseline at exactly `5fd751e` BEFORE running `update_version.py` (no version bump), and run the GATE-1.5 cmp on a fresh `pio run -e uno` from the same revision *with version.h left unchanged*. Alternative: compute a baseline-vs-current `objcopy --remove-section` or post-link `avr-strings` diff — but plain `cmp -s` of pre-version-bump artifacts is the simplest faithful approach.

**Primary recommendation:** Honor CONTEXT D-01..D-13 verbatim with two small clarifications: (a) the `platform` line in `[env:uno328pb]` should be `platform = atmelavr` (mirror `[env:uno]`, not literally `MCUdude/MiniCore`); (b) GATE-1.5 baseline capture must use a version-unbumped checkout at `5fd751e` to avoid version-region drift entirely on the comparison step.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| PIO env declaration | Build system (platformio.ini) | — | One additive `[env:uno328pb]` block |
| MCU port macro guards | Firmware C/C++ source | — | Four `ARDUINO_AVR_UNO` → `defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)` |
| Artifact naming (PROGNAME) | SCons extra_script (`name_firmware.py`) | — | Rewrite of 3-line script; parses build_flags for `RURP_BOARD_NAME` |
| Handshake board string | Firmware (`firestarter.h:16`, `hardware_operations.cpp:82-92`) | — | Already board-aware via `RURP_BOARD_NAME`; zero edit |
| Native test linkage | Test harness (`[env:native]` config + `test/native/avr/*`) | — | No edit; new macros are dead in native env (RURP_BOARD_NAME=\"native\") |
| GATE-1.5 byte-identity gate | Meta-repo baseline + verification script | Firmware build system | Baseline hex captured pre-bump; cmp at verify time |
| REQUIREMENTS.md FW-02 amendment | Meta-repo planning artifacts | — | Planner-owned inline edit per CONTEXT D-09 |

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**In scope (Phase 21):**
1. Edit `firestarter/platformio.ini` — add `[env:uno328pb]` (after `[env:uno]`, before `[env:leonardo]` so the two 328-family envs are visually grouped). No change to `[platformio] default_envs` in this phase.
2. Rework `firestarter/name_firmware.py` — replace `board = env.GetProjectOption("board")` with a function that parses the `-D RURP_BOARD_NAME=\"X\"` token out of the per-env build_flags list, extracts `X`, and sets PROGNAME = `firestarter_X`.
3. Widen 4 `ARDUINO_AVR_UNO` macro guards atomically (single commit) to include `ARDUINO_AVR_ATmega328PB` so the existing Uno board-setup code compiles into the 328PB target.
4. Capture pre-v1.5 baseline hex files at `.planning/v1.5/baselines/firestarter_uno.hex` + `.planning/v1.5/baselines/firestarter_leonardo.hex` (from `firestarter/beta` tip `5fd751e`); use them as a GATE-1.5 byte-identity gate.
5. Amend `.planning/REQUIREMENTS.md` FW-02 inline (drop the `boards/uno328pb.json` requirement; reframe FW-02 around the `name_firmware.py` rework + `RURP_BOARD_NAME` triple).

**D-01:** Widen all 4 `ARDUINO_AVR_UNO` macro guards atomically: `uno_rurp_shield.cpp:8`, `rurp_common.cpp:10`, `rurp_common.cpp:23`, `rurp_register_utils.h:63`.
**D-02:** Repeat inline `defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)` at each site (no umbrella macro).
**D-03:** No new native tests for the widened guards.
**D-04:** GATE-1.5 verification = `cmp -s` against checked-in baseline hex files.
**D-05/D-08/D-09:** Path B — drop the `boards/uno328pb.json` file entirely; PROGNAME derives from `RURP_BOARD_NAME`. REQUIREMENTS.md FW-02 amendment is planner-owned and must land before phase ships.
**D-06:** PROGNAME source = parse `-D RURP_BOARD_NAME=\"X\"` from `env['BUILD_FLAGS']`.
**D-07:** `[env:uno328pb]` block — `platform = MCUdude/MiniCore`, `board = ATmega328PB`, `framework = arduino`, build_flags = `${env.build_flags}` + `-D RURP_BOARD_NAME=\"uno328pb\"` + `-D SERIAL_ON_IO`. DATA_BUFFER_SIZE inherits default (512). Hard-code the literal `\"uno328pb\"` (NOT `\"${this.board}\"`).
**D-08 (ini placement):** `[env:uno328pb]` inserted between `[env:uno]` and `[env:leonardo]`.
**D-10..D-13:** Cross-phase hand-offs to Phase 22 (default_envs widening), Phase 23 (avrdude profile), planner (ROADMAP touch-up); FW-03 verification = build-time `.elf` symbol grep (no new native test).

### Claude's Discretion

- Exact byte offsets in `firestarter_uno.hex` / `firestarter_leonardo.hex` baseline files where `update_version.py` perturbs bytes (research surface for the planner).
- Exact parsing form in `name_firmware.py` for `-D RURP_BOARD_NAME` (regex vs `shlex` vs PIO's `env.ParseFlags`) — planner picks based on what PIO's SCons `env['BUILD_FLAGS']` actually exposes at script time. Failure mode for missing flag = `Exit(1)` with a clear error message.
- Whether to commit the two baseline hex files via Git LFS or as plain blobs.

### Deferred Ideas (OUT OF SCOPE)

- Per-env `custom_prog_name` PIO option as PROGNAME source fallback.
- Umbrella macro `RURP_BOARD_UNO_FAMILY` in `rurp_shield.h`.
- Static-assert / .elf-grep CI step for the `RURP_BOARD_NAME` literal as an ongoing CI gate.
- `board_build.variant`, `upload_protocol`, `upload_speed` explicit overrides in `[env:uno328pb]`.
- MiniCore version pinning (`platform = MCUdude/MiniCore@^3.0.0`).
- 328PB extra peripherals (USART1, TWI1, SPI1, Timer3/4, PE0–PE3).
- Resume v1.3 BENCH-01..06 on the 328PB-Uno.
- Adding a `uno328pb` branch to `firestarter_app/firestarter/firmware.py:417-423` (Phase 23 owns this).
- `[platformio] default_envs` widening (Phase 22 owns this).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FW-01 | `pio run -e uno328pb` builds a flashable `.hex` from main/beta of the firmware sub-repo; uses `platform = MCUdude/MiniCore`; CI-green with no new warnings vs `uno`/`leonardo`. | PlatformIO `atmelavr` platform 5.2.0 (Published 2026-04-28) ships `boards/ATmega328PB.json` with `build.core = "MiniCore"`, `build.mcu = "atmega328pb"`, `build.variant = "pb-variant"`, `build.extra_flags = "-DARDUINO_AVR_ATmega328PB"`. The `[env:uno]` and `[env:leonardo]` envs both use `platform = atmelavr`. The `MCUdude/MiniCore` PlatformIO-platform spec from CONTEXT D-07 is not strictly required — `platform = atmelavr` resolves the MiniCore core via the bundled board file. **Recommend mirroring `[env:uno]`'s `platform = atmelavr` for symmetry; flag the deviation from CONTEXT D-07 to the operator if material.** [VERIFIED: `pio pkg show platformio/atmelavr` showed 5.2.0 installed; [VERIFIED: github.com/platformio/platform-atmelavr/blob/develop/boards/ATmega328PB.json] |
| FW-02 | (Amended per D-05/D-09 — see Locked Decisions) `[env:uno328pb]` exists with `board = ATmega328PB` (MiniCore built-in via atmelavr) + `-D RURP_BOARD_NAME=\"uno328pb\"`; `name_firmware.py` derives PROGNAME from `RURP_BOARD_NAME`; the board-id triple's single source of truth is the `RURP_BOARD_NAME` flag. No custom `boards/uno328pb.json` file. | `firestarter/boards/` directory does NOT exist in the current sub-repo (verified by `ls -la firestarter/boards/` returning "no such file or directory"). Phase 21 will not create it. [VERIFIED: filesystem inspection 2026-05-20] |
| FW-03 | Firmware emits literal `uno328pb` in `<board>` slot of MSG_OK_FW_HANDSHAKE; source = `-D RURP_BOARD_NAME=\"uno328pb\"` per-env. | `firestarter/include/firestarter.h:16` defines `FW_VERSION VERSION ":" RURP_BOARD_NAME`. `firestarter/src/hardware_operations.cpp:82-92` (`fw_get_version()`) emits `OK: FW: ` + `FW_VERSION` via `SERIAL_PORT.print/println`. Both already board-aware and unchanged. Per CONTEXT D-13, verification is build-time `.elf` symbol grep, not a new native test. [VERIFIED: source read 2026-05-20] |
| FW-04 | `pio test -e native` stays green (`test_dispatch` + `test_messages` suites). | `[env:native]` uses `-D RURP_BOARD_NAME=\"native\"`, `platform = native`, `test_framework = unity`, ArduinoFake 0.4.0, with `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp>`. The native env compiles `src/proms/*.cpp` against host libc; AVR-only `src/boards/*.cpp` (which carry the widened macros) are EXCLUDED. Widened macros are therefore unreachable in native build → cannot regress. [VERIFIED: platformio.ini:50-86, host_stubs_common.inc, firestarter/CLAUDE.md "Native Test Environment"] |
</phase_requirements>

## Standard Stack

### Core

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| PlatformIO Core | 6.1.19 | Build orchestrator | Already installed; project-level pinned to whatever CI uses (`pip install --upgrade platformio` in workflows). [VERIFIED: `pio --version`] |
| `platformio/atmelavr` platform | 5.2.0 (Published 2026-04-28) | Provides Atmel/Microchip AVR toolchain + Arduino framework wiring + built-in `ATmega328PB` board file | Same platform `[env:uno]` and `[env:leonardo]` already use; no new platform install needed. Built-in `ATmega328PB.json` carries `build.core = "MiniCore"` so the MiniCore core/variant compiles in without a separate platform = MCUdude/MiniCore spec. [VERIFIED: `pio pkg show platformio/atmelavr` 2026-05-20; [CITED: github.com/platformio/platform-atmelavr/blob/develop/boards/ATmega328PB.json] |
| MiniCore core (bundled) | bundled via atmelavr@5.2.0 | Arduino-compatible runtime + `pb-variant` pin map for ATmega328PB | The `pb-variant` source path lives at `~/.platformio/packages/framework-arduino-avr-minicore/avr/variants/pb-variant/pins_arduino.h`. Used by Arduino IDE community for 328PB-on-Uno-shape boards. [CITED: github.com/MCUdude/MiniCore/blob/master/avr/variants/pb-variant/pins_arduino.h] |

### Supporting

| Component | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| `avr-strings` / `avr-nm` / `avr-objdump` | from atmelavr toolchain | Inspect `.elf` to verify `uno328pb` literal lands in `.rodata` (CONTEXT D-13 verification surface) | Phase 21 verification only — confirm `RURP_BOARD_NAME` resolves to `"uno328pb"` in the build output |
| Unity (via `[env:native]`) | already wired | Host-side dispatch + messages tests (FW-04 regression gate) | `pio test -e native` after every change in Phase 21 |
| ArduinoFake | 0.4.0 | Host shim for Arduino API in native tests | Already a `lib_deps` entry in `[env:native]`; no change [VERIFIED: platformio.ini:71] |
| `cmp -s` (POSIX) | system | Byte-identity check for GATE-1.5 | Verification step only; no install |

**Version verification (2026-05-20):**

```bash
$ pio --version
PlatformIO Core, version 6.1.19

$ cd /workspaces/firestarter && pio pkg show platformio/atmelavr | head -5
platformio/atmelavr
Platform • 5.2.0 • Public • Published on Tue Apr 28 13:35:37 2026
```

[VERIFIED: command outputs above]

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `platform = atmelavr` + `board = ATmega328PB` (recommended) | `platform = MCUdude/MiniCore` (external package) | The external MiniCore platform package (`https://github.com/MCUdude/MiniCore` board manager URL) exists as a community Arduino IDE core but is NOT a registered PlatformIO platform — PIO platform-show errored "Could not find 'MCUdude/MiniCore' package in the PlatformIO Registry". Sourcing it via `platform = https://github.com/MCUdude/MiniCore.git` would work but is heavier than the built-in atmelavr-bundled MiniCore. **Recommend `platform = atmelavr` for symmetry with `[env:uno]`/`[env:leonardo]`. Flag this for the planner to confirm against CONTEXT D-07's literal text.** [VERIFIED: `pio pkg show MCUdude/MiniCore` errored 2026-05-20] |
| `env.ParseFlags()` (recommended) | regex `re.search(r'-D\s*RURP_BOARD_NAME=\\"([^"]+)\\"', flags)` | ParseFlags is the documented PIO API; returns `CPPDEFINES` as list of strings or 2-tuples. Regex is brittle to whitespace, line continuations, and PIO's quote-escaping. [CITED: docs.platformio.org/.../build_flags.html] |
| Hard-code `RURP_BOARD_NAME=\"uno328pb\"` literal in `[env:uno328pb]` (per CONTEXT D-07) | Use `\"${this.board}\"` interpolation as `[env:uno]`/`[env:leonardo]` do | With `board = ATmega328PB`, `${this.board}` resolves to `ATmega328PB` — wrong for the handshake-string triple. CONTEXT D-07 explicitly mandates the literal. |

## Architecture Patterns

### System Architecture Diagram

```
                              ┌──────────────────────────────┐
                              │ platformio.ini               │
                              │   [env:uno]      board=uno   │
                              │   [env:uno328pb] board=ATmega328PB
                              │                  -D RURP_BOARD_NAME=\"uno328pb\"
                              │   [env:leonardo] board=leonardo
                              └──────────────┬───────────────┘
                                             │
                              ┌──────────────▼───────────────┐
        Build flags →         │ name_firmware.py (extra_script)
                              │   env.ParseFlags(build_flags)
                              │   → CPPDEFINES → ("RURP_BOARD_NAME", "uno328pb")
                              │   → PROGNAME = "firestarter_uno328pb"
                              └──────────────┬───────────────┘
                                             │
                              ┌──────────────▼───────────────┐
        Macros to gcc →       │ atmelavr@5.2.0 + MiniCore core
                              │   board=ATmega328PB →
                              │     -mmcu=atmega328pb
                              │     variant=pb-variant
                              │     -DARDUINO_AVR_ATmega328PB
                              │     -DF_CPU=16000000L
                              │     + -D RURP_BOARD_NAME=\"uno328pb\"
                              └──────────────┬───────────────┘
                                             │
                              ┌──────────────▼───────────────┐
        Source compiled →     │ src/boards/uno_rurp_shield.cpp:8
                              │   #if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)
                              │     ←── compiles into uno328pb binary
                              │ src/boards/rurp_common.cpp:10,23
                              │ include/rurp_register_utils.h:63
                              │ include/firestarter.h:16
                              │   #define FW_VERSION VERSION ":" RURP_BOARD_NAME
                              │     ←── expands to "3.0.0b2:uno328pb"
                              └──────────────┬───────────────┘
                                             │
                              ┌──────────────▼───────────────┐
        Output artifacts →    │ .pio/build/uno328pb/firmware.elf
                              │ .pio/build/uno328pb/firestarter_uno328pb.hex
                              └──────────────┬───────────────┘
                                             │
                              ┌──────────────▼───────────────┐
      Verification gates →    │ FW-01: build green, no new warnings
                              │ FW-03: avr-strings firmware.elf | grep -F uno328pb
                              │ FW-04: pio test -e native (test_dispatch + test_messages)
                              │ GATE-1.5: cmp -s .pio/build/uno/firestarter_uno.hex
                              │                  .planning/v1.5/baselines/firestarter_uno.hex
                              │            cmp -s .pio/build/leonardo/firestarter_leonardo.hex
                              │                  .planning/v1.5/baselines/firestarter_leonardo.hex
                              └──────────────────────────────┘
```

### Recommended Project Structure

```
firestarter/                      (sub-repo, branched off beta @ 5fd751e)
├── platformio.ini                # ADD [env:uno328pb] between [env:uno] and [env:leonardo]
├── name_firmware.py              # REWRITE — derive PROGNAME from -D RURP_BOARD_NAME
├── include/
│   ├── firestarter.h             # UNCHANGED (line 16 already does the right thing)
│   ├── rurp_register_utils.h     # EDIT line 63 guard
│   └── rurp_shield.h             # UNCHANGED
├── src/
│   ├── boards/
│   │   ├── uno_rurp_shield.cpp   # EDIT line 8 guard
│   │   ├── leonardo_rurp_shield.cpp  # UNCHANGED (reference for symmetry)
│   │   └── rurp_common.cpp       # EDIT lines 10 + 23 guards
│   └── hardware_operations.cpp   # UNCHANGED (lines 82-92 already board-aware)
└── test/native/avr/              # UNCHANGED (test_dispatch + test_messages must stay green)

.planning/                        (meta-repo, on main)
├── v1.5/                         # NEW directory
│   └── baselines/                # NEW directory
│       ├── firestarter_uno.hex             # NEW (captured from beta @ 5fd751e, version unbumped)
│       └── firestarter_leonardo.hex        # NEW (captured from beta @ 5fd751e, version unbumped)
├── REQUIREMENTS.md               # EDIT — amend FW-02 inline per CONTEXT D-09
└── ROADMAP.md                    # OPTIONAL EDIT — D-12 touch-up of Phase 22 SC#1 default_envs literal
```

### Pattern 1: Additive PIO env with mirror-of-`[env:uno]` flags

**What:** Append a new `[env:<board>]` section that inherits `${env.build_flags}` and overrides only the board-specific bits.

**When to use:** Adding a new AVR board variant that compiles against the existing source tree with only a few macro-guard widenings.

**Example:**

```ini
# Source: /workspaces/firestarter/platformio.ini:31-38 (existing [env:uno] pattern)
[env:uno]
platform = atmelavr
board = uno
framework = arduino
build_flags =
	${env.build_flags}
	-D RURP_BOARD_NAME=\"${this.board}\"
	-D SERIAL_ON_IO

# Phase 21 ADD (between [env:uno] and [env:leonardo], per CONTEXT D-08):
[env:uno328pb]
platform = atmelavr
board = ATmega328PB
framework = arduino
build_flags =
	${env.build_flags}
	-D RURP_BOARD_NAME=\"uno328pb\"
	-D SERIAL_ON_IO
```

Notes:
- `platform = atmelavr` recommended (mirrors `[env:uno]`); CONTEXT D-07 reads `platform = MCUdude/MiniCore` — confirm with operator before deviating. The atmelavr platform's `boards/ATmega328PB.json` already pulls in MiniCore as `build.core`.
- `board = ATmega328PB` is **case-sensitive** in PlatformIO (must be `ATmega328PB`, not `atmega328pb` or `ATMEGA328PB`). [CITED: docs.platformio.org/en/stable/boards/atmelavr/ATmega328PB.html]
- The literal `-D RURP_BOARD_NAME=\"uno328pb\"` (NOT `\"${this.board}\"`) — per CONTEXT D-07. `${this.board}` would resolve to `ATmega328PB`, breaking the board-id triple.

### Pattern 2: PIO extra_script BUILD_FLAGS parsing for PROGNAME derivation

**What:** Replace 3-line `env.GetProjectOption("board")`-based PROGNAME with `env.ParseFlags()` extraction of a build-flag macro.

**When to use:** Decoupling PROGNAME from the PIO `board` setting when the board setting needs to differ from the artifact name.

**Example:**

```python
# Source: docs.platformio.org/en/stable/projectconf/sections/env/options/build/build_flags.html
# Pattern (planner-owned; below is a working sketch, not the final implementation):
Import("env")

# env.ParseFlags accepts the raw build_flags string (NOT pre-split) and returns
# a dict with CPPDEFINES as a list of either strings (for "-D NAME") or 2-tuples
# (for "-D NAME=VALUE"). Quoting from build_flags is preserved as embedded
# backslash-escaped chars, so a "-D RURP_BOARD_NAME=\"uno328pb\"" entry surfaces
# as the 2-tuple ("RURP_BOARD_NAME", "\\\"uno328pb\\\"") — strip the leading/
# trailing escaped quotes to get the raw value.

build_flags_str = env.GetProjectOption("build_flags")
parsed = env.ParseFlags(build_flags_str)

board_name = None
for define in parsed.get("CPPDEFINES", []):
    if isinstance(define, (list, tuple)) and len(define) == 2:
        name, value = define
        if name == "RURP_BOARD_NAME":
            # Value may be \"uno328pb\" with embedded escaped quotes; strip them.
            board_name = value.strip().strip('\\"').strip('"')
            break

if board_name is None:
    print("ERROR: name_firmware.py — no -D RURP_BOARD_NAME=\\\"X\\\" found in build_flags")
    Exit(1)

env.Replace(PROGNAME="firestarter_%s" % board_name)
```

**Verification before commit:** Run `pio run -e uno -e leonardo -e uno328pb` and confirm the three `.hex` filenames are `firestarter_uno.hex`, `firestarter_leonardo.hex`, `firestarter_uno328pb.hex` respectively. The two existing files MUST byte-match the pre-rework outputs (GATE-1.5 obligation).

### Pattern 3: Inline-disjunction macro guard widening (CONTEXT D-02)

**What:** Widen `#ifdef ARDUINO_AVR_UNO` to `#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)` at every gate that controls Uno-family setup code.

**Where to apply (verified by `grep -rn "ARDUINO_AVR_" --include=*.cpp --include=*.h .`):**

```
src/boards/uno_rurp_shield.cpp:8:#ifdef ARDUINO_AVR_UNO
include/rurp_register_utils.h:63:#ifdef ARDUINO_AVR_UNO
src/boards/rurp_common.cpp:10:#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_LEONARDO)
src/boards/rurp_common.cpp:23:#if defined(ARDUINO_AVR_UNO)
```

[VERIFIED: grep 2026-05-20]

**After widening (CONTEXT D-01, D-02):**

```cpp
// src/boards/uno_rurp_shield.cpp:8 — was: #ifdef ARDUINO_AVR_UNO
#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)

// src/boards/rurp_common.cpp:10 — was: #if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_LEONARDO)
#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB) || defined(ARDUINO_AVR_LEONARDO)

// src/boards/rurp_common.cpp:23 — was: #if defined(ARDUINO_AVR_UNO)
#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)
// elif chain below stays as-is

// include/rurp_register_utils.h:63 — was: #ifdef ARDUINO_AVR_UNO
#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)
```

**Why `ARDUINO_AVR_ATmega328PB` (NOT `ARDUINO_AVR_ATmega328`):** Verified by reading the PlatformIO board file `boards/ATmega328PB.json` at `platformio/platform-atmelavr` master — `build.extra_flags = "-DARDUINO_AVR_ATmega328PB"`. The macro `ARDUINO_AVR_ATmega328` (no PB) is the default Arduino board name macro derived from MiniCore's `boards.txt` `build.board=AVR_ATmega328`, but PlatformIO's atmelavr board JSON overrides this with its own extra_flags, so the firmware's compiled binary will see `-DARDUINO_AVR_ATmega328PB` defined. [VERIFIED: github.com/platformio/platform-atmelavr/blob/develop/boards/ATmega328PB.json content fetched 2026-05-20]

### Anti-Patterns to Avoid

- **Forcing `-D ARDUINO_AVR_UNO` in `[env:uno328pb]` build_flags instead of widening guards.** Lies about MCU identity; overlaps with MiniCore's own `-D ARDUINO_AVR_ATmega328PB`; risk of double-define warnings or wrong-MCU peripheral assumptions in any future code that branches on the macro. Discussed and rejected in CONTEXT discussion log Q1.
- **Partial guard widening (e.g., only `uno_rurp_shield.cpp:8`).** `rurp_common.cpp:28` carries `#error "Unsupported board"` in the `#else` branch of the `#if defined(UNO)/elif defined(LEONARDO)/else` chain (verified at line 28 of `rurp_common.cpp`); the build would link-error before producing a `.hex`. CONTEXT D-01 mandates atomic 4-site widening.
- **Introducing an umbrella macro `RURP_BOARD_UNO_FAMILY` in `rurp_shield.h`.** Indirection cost > 4-site disjunction cost for a single new board. Premature abstraction. Deferred per CONTEXT D-02 + Deferred Ideas.
- **Using `${this.board}` in `-D RURP_BOARD_NAME` for `[env:uno328pb]`.** `${this.board}` resolves to `ATmega328PB` — wrong for the board-id triple. Hard-code the literal `\"uno328pb\"` per CONTEXT D-07.
- **Running GATE-1.5 `cmp -s` against a version-bumped checkout.** `update_version.py` rewrites `include/version.h` and the version string lands in `.rodata` (via `FW_VERSION VERSION ":" RURP_BOARD_NAME` at `include/firestarter.h:16`). A naive `cmp` will diff on every version byte AND each affected line's Intel-HEX checksum byte. Capture the baseline at `5fd751e` with `version.h` unmodified and run the Phase 21 verification on a build of the same revision (also with `version.h` unmodified — i.e., do NOT trigger `update_version.py` during local Phase 21 verification, just `pio run -e uno`).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Parsing `-D RURP_BOARD_NAME=\"X\"` from build_flags | Custom regex over `env['BUILD_FLAGS']` | `env.ParseFlags(env.GetProjectOption("build_flags"))` then iterate `parsed["CPPDEFINES"]` | ParseFlags handles whitespace, multi-line build_flags, embedded quotes, conditional flags. Regex breaks on edge cases. [CITED: docs.platformio.org/.../build_flags.html] |
| ATmega328PB board JSON | Custom `boards/uno328pb.json` (5-line `extends` variant or full hand-author) | PlatformIO's built-in `ATmega328PB` board (case-sensitive) via `board = ATmega328PB` | Built-in board file provides `mcu=atmega328pb`, `f_cpu=16000000L`, `variant=pb-variant`, `-DARDUINO_AVR_ATmega328PB`, `core=MiniCore`, `upload protocol=urclock`, `speed=115200` out of the box. Path B (CONTEXT D-05) explicitly drops the custom file. |
| `.hex` byte-identity check | Custom Intel-HEX-format-aware Python differ that skips checksum bytes | `cmp -s baseline.hex current.hex` against a version-unbumped baseline | Simpler if the baseline is captured pre-bump (no version-byte drift to normalize). If the baseline must be post-bump, accept `git diff --stat` evidence of "differ only in version-string region" as adequate gate — but pre-bump baseline is the cleanest answer. |
| Detecting 328PB ADC bandgap MUX | Custom ATmega328PB-specific ADMUX bit calculation in `rurp_common.cpp:23` | Reuse `_BV(REFS0) \| _BV(MUX3) \| _BV(MUX2) \| _BV(MUX1)` (same as Uno) | The 328PB uses the same ADMUX bandgap channel encoding as the 328P; CONTEXT D-01 documents this rationale. [VERIFIED: Microchip ATmega328PB datasheet Table 24-4 ADC Input Channel Selections — ADMUX[3:0] = 1110 selects 1.1V bandgap on both 328P and 328PB; [CITED: ww1.microchip.com ATmega328PB datasheet] |

**Key insight:** The MCU port surface is microscopic — 4 macro guards + 1 PIO env + 1 script rewrite. The risk surface is at the boundary: (a) PIO platform name (D-07's `MCUdude/MiniCore` literal vs the more idiomatic `atmelavr`); (b) `env.ParseFlags()` exact tuple/string format; (c) GATE-1.5 cmp semantics under version-string drift. Hand-rolling anything beyond the 4 guard widenings + the 1 script + the 1 env block is over-investing.

## Runtime State Inventory

> Phase 21 is a build-configuration + 4-macro-guard widening + 1-script rewrite. It produces new build artifacts but does NOT touch persisted runtime state. Inventory below is for completeness.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None. No database, ChromaDB, Mem0, or persistent store references the string `uno328pb` today. The chip_database.json in `firestarter_app` does not key on board names. | None — verified by `grep -rn "uno328pb\|328PB\|328pb" firestarter/` returning zero results. |
| Live service config | None. No GitHub Actions secrets, n8n workflows, or external services carry the `uno328pb` string. Phase 22 will add CI config references; Phase 21 does not. | None |
| OS-registered state | None. No systemd / launchd / pm2 / Task Scheduler registrations. PlatformIO platform installs (`atmelavr` 5.2.0) live under `~/.platformio/packages/` and are auto-managed by PIO on env-build invocation. | None — `~/.platformio/packages/framework-arduino-avr-minicore` will be auto-fetched by PIO on first `pio run -e uno328pb` if not already present. |
| Secrets/env vars | None. CONTEXT D-10 hand-off notes the `firestarter_app/firestarter/firmware.py:417-423` board-table will need a `uno328pb` branch — but that's Phase 23, not Phase 21. | None (Phase 21) |
| Build artifacts | `.pio/build/uno/`, `.pio/build/leonardo/` already exist on the dev box (verified via `ls /workspaces/firestarter/.pio/build/`). The widened macro guards in `src/boards/*.cpp` and `include/rurp_register_utils.h` will trigger recompilation of `uno` and `leonardo` envs on next `pio run` — outputs MUST remain byte-identical to baseline (GATE-1.5). A `.pio/build/uno328pb/` directory will be created on first `pio run -e uno328pb`. | Phase 21 captures `.pio/build/uno/firestarter_uno.hex` + `.pio/build/leonardo/firestarter_leonardo.hex` as the GATE-1.5 baseline BEFORE the widening commit, then re-runs `pio run -e uno -e leonardo` AFTER the widening commit and `cmp -s` against the baselines. |

**Key risk surface:** GATE-1.5 byte-identity AFTER the widening + after the `name_firmware.py` rework. The widening adds the disjunction to source code; on the `uno` and `leonardo` builds the second disjunct (`defined(ARDUINO_AVR_ATmega328PB)`) is false, so the gated code blocks compile identically to today. The `name_firmware.py` rework changes how PROGNAME is computed; for `[env:uno]` and `[env:leonardo]` the new derivation must produce `firestarter_uno` and `firestarter_leonardo` (it will, because both envs already declare `-D RURP_BOARD_NAME=\"${this.board}\"` → value resolves to `uno`/`leonardo` → PROGNAME = `firestarter_uno`/`firestarter_leonardo`). No on-disk Intel HEX bytes should perturb.

## Common Pitfalls

### Pitfall 1: Case sensitivity of `board = ATmega328PB`

**What goes wrong:** Writing `board = atmega328pb` or `board = ATMEGA328PB` causes `pio run -e uno328pb` to error with "InvalidBoard" — PlatformIO board IDs are case-sensitive and the registered board name is literally `ATmega328PB`.

**Why it happens:** Operator habit (treats env names as case-insensitive); CONTEXT D-07 uses the canonical case but copy-paste / typo risk remains.

**How to avoid:** Type `board = ATmega328PB` exactly as written. [CITED: docs.platformio.org/en/stable/boards/atmelavr/ATmega328PB.html]

**Warning signs:** `pio run -e uno328pb` errors during config parse, before any compile. Distinct from compile errors which mean source-code issues.

### Pitfall 2: `env.ParseFlags()` returns escaped-quote string for `-D NAME=\"value\"`

**What goes wrong:** The script extracts `value = "\\\"uno328pb\\\""` (with embedded escaped quotes preserved as literal `\"` chars) instead of the bare `uno328pb`. PROGNAME ends up as `firestarter_\"uno328pb\"` — illegal filename characters → build fails or produces a garbled filename.

**Why it happens:** PIO's ParseFlags treats the SCons CPPDEFINES list literally; the `\"` chars in `platformio.ini` survive into the parsed value because the shell-level quoting is consumed by the C-preprocessor at compile time, not by PIO at config-parse time.

**How to avoid:** After extracting the value, `.strip().strip('\\"').strip('"')` to peel off any escaped or plain quotes. Add a defensive assertion: `assert board_name.isidentifier()` or `re.match(r'^[a-zA-Z0-9_-]+$', board_name)` before using it in PROGNAME.

**Warning signs:** Build artifact filename contains `"` characters; or `pio run -e uno` after the rework no longer produces `firestarter_uno.hex` byte-identical to baseline (because the PROGNAME pattern subtly changed).

### Pitfall 3: GATE-1.5 cmp against a version-bumped baseline

**What goes wrong:** Operator runs `update_version.py --beta --set-version 3.0.1b1` before capturing the baseline, then runs Phase 21's verification step against a fresh build where `version.h` is unmodified. The `.hex` files diff on the version bytes AND each Intel-HEX record's checksum byte for affected lines. `cmp -s` exits non-zero → false-positive GATE-1.5 failure.

**Why it happens:** The version-string region drifts on every `update_version.py` invocation, but `cmp -s` is unaware of "expected" drift regions.

**How to avoid:** Capture the GATE-1.5 baseline at `5fd751e` (the documented v1.5 milestone start tip) by:
1. `git checkout 5fd751e` in the firmware sub-repo on a worktree (do NOT modify the working branch).
2. `pio run -e uno -e leonardo` — this builds without invoking `update_version.py`, so `version.h` stays at its committed value (`3.0.0b2` per `include/version.h:11`).
3. Copy `.pio/build/uno/firestarter_uno.hex` and `.pio/build/leonardo/firestarter_leonardo.hex` to `.planning/v1.5/baselines/`.
4. `git switch -` back to the working branch.

After the widening + name_firmware.py rework commits, run `pio run -e uno -e leonardo` again (still without `update_version.py`) and `cmp -s` against the captured baselines.

**Warning signs:** Hex diff appears at predictable byte offsets matching the ASCII bytes `3.0.0b2` (or whatever VERSION string was active during baseline capture). Use `xxd .pio/build/uno/firestarter_uno.hex | grep -c "33 2e 30 2e 30 62 32"` to confirm version byte location if needed.

### Pitfall 4: `extra_scripts = pre:name_firmware.py` runs at `[env]` scope

**What goes wrong:** The reworked `name_firmware.py` parses build_flags expecting `-D RURP_BOARD_NAME=\"X\"` to be present. If a future env (or `[env:native]`) does not declare this flag, the script's `Exit(1)` fires and breaks the env's build.

**Why it happens:** `extra_scripts = pre:name_firmware.py` is declared at `[env]` (line 29) — inherited by every env. Today's `[env:native]` already declares `-D RURP_BOARD_NAME=\"native\"`, so the rework will resolve PROGNAME = `firestarter_native` for the native test build (cosmetic — native env doesn't produce a flashable `.hex`).

**How to avoid:** Verify the script handles the `native` case gracefully (no crash, no PROGNAME shape that confuses Unity). The defensive `Exit(1)` is correct for missing-flag cases; `[env:native]` carries the flag so it falls through. Add a comment in `name_firmware.py` noting that any future env without `-D RURP_BOARD_NAME` is a configuration error.

**Warning signs:** `pio test -e native` fails with "PROGNAME unset" or "missing flag" — fix by adding the missing flag, not by softening the script's strictness.

### Pitfall 5: `rurp_common.cpp:23` widening must NOT remove the `#elif defined(ARDUINO_AVR_LEONARDO)` arm

**What goes wrong:** The widening replaces line 23 (`#if defined(ARDUINO_AVR_UNO)`) with `#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)`. If the operator also removes the `#elif defined(ARDUINO_AVR_LEONARDO)` arm on line 25, the Leonardo build's ADMUX bandgap channel falls into the `#error "Unsupported board"` at line 28 — Leonardo builds break.

**Why it happens:** Refactor-mode reading; the operator focuses on the Uno arm and accidentally restructures the chain.

**How to avoid:** Only modify line 23's condition. Lines 25 (`#elif defined(ARDUINO_AVR_LEONARDO)`) and 28 (`#error`) stay exactly as today.

**Warning signs:** `pio run -e leonardo` errors at compile time with "Unsupported board" message from line 28.

### Pitfall 6: External-package `platform = MCUdude/MiniCore` requires explicit installation

**What goes wrong:** If the operator types `platform = MCUdude/MiniCore` literally (per CONTEXT D-07 wording), PIO will try to resolve this as a registry name. The registry name `MCUdude/MiniCore` does NOT exist (verified `pio pkg show MCUdude/MiniCore` errors). PIO falls back to a git-URL resolution attempt or fails outright.

**Why it happens:** `MCUdude/MiniCore` is the GitHub repo path for the Arduino-IDE-compatible MiniCore core, not a PlatformIO platform package. The PlatformIO equivalent is shipping inside `platformio/atmelavr@5.2.0` as a bundled core (see `boards/ATmega328PB.json`'s `build.core = "MiniCore"`).

**How to avoid:** Use `platform = atmelavr` in `[env:uno328pb]` (mirror of `[env:uno]`). The atmelavr platform's built-in `ATmega328PB` board pulls in MiniCore as the framework core automatically. If for some reason MiniCore-specific peripheral support is needed (USART1, TWI1, etc. — but these are explicitly out-of-scope per REQUIREMENTS.md), the alternative spec is `platform = https://github.com/MCUdude/MiniCore.git` (git URL).

**Warning signs:** `pio run -e uno328pb` errors with "Could not find 'MCUdude/MiniCore' package in the PlatformIO Registry".

[ASSUMED → confirm with planner/operator] The CONTEXT D-07 wording `platform = MCUdude/MiniCore` may be a colloquial reference to the platform-supplied MiniCore core, with the expectation that the planner translates to `platform = atmelavr`. **Recommend planner explicitly confirms before drafting the platformio.ini diff.**

## Code Examples

Verified patterns from official sources and existing code:

### Existing `[env:uno]` pattern (mirror reference)

```ini
# Source: /workspaces/firestarter/platformio.ini:31-38 (verified read 2026-05-20)
[env:uno]
platform = atmelavr
board = uno
framework = arduino
build_flags =
	${env.build_flags}
	-D RURP_BOARD_NAME=\"${this.board}\"
	-D SERIAL_ON_IO
```

### Existing `name_firmware.py` (rewrite target)

```python
# Source: /workspaces/firestarter/name_firmware.py (verified read 2026-05-20)
Import("env")
board = env.GetProjectOption("board")
env.Replace(PROGNAME="firestarter_%s" % board)
```

### Existing handshake emit (no edit; reference for FW-03)

```cpp
// Source: /workspaces/firestarter/src/hardware_operations.cpp:82-92 (verified read 2026-05-20)
bool fw_get_version(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_GET_FW_VERSION);
    // Phase 9 / LFW-05: lone surviving text-format emit.
    SERIAL_PORT.print(F("OK: FW: "));
    SERIAL_PORT.println(FW_VERSION);
    SERIAL_PORT.flush();
    return true;
}

// Source: /workspaces/firestarter/include/firestarter.h:16 (verified read 2026-05-20)
#define FW_VERSION VERSION ":" RURP_BOARD_NAME
```

### Existing 4 guard sites (widening targets)

```cpp
// Source: /workspaces/firestarter/src/boards/uno_rurp_shield.cpp:8 (verified)
#ifdef ARDUINO_AVR_UNO
// ... ~140 lines of board-setup code ...
#endif

// Source: /workspaces/firestarter/src/boards/rurp_common.cpp:10 (verified)
#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_LEONARDO)
// ... bandgap reading, vcc/voltage math ...
#endif

// Source: /workspaces/firestarter/src/boards/rurp_common.cpp:23-29 (verified)
#if defined(ARDUINO_AVR_UNO)
    ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
#elif defined(ARDUINO_AVR_LEONARDO)
    ADMUX = _BV(REFS0) | _BV(MUX4) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
#else
#error "Unsupported board"
#endif

// Source: /workspaces/firestarter/include/rurp_register_utils.h:63 (verified)
#ifdef ARDUINO_AVR_UNO
    // FM1608 PORTD-bit-6 pre-clear + 4-NOP settle workaround
    if (reg == MOST_SIGNIFICANT_BYTE) {
        rurp_set_data_output();
        PORTD = 0;
        __asm__ __volatile__("nop\n\tnop\n\tnop\n\tnop\n\t");
    }
#endif
```

### Worked example: PROGNAME extraction from build_flags

```python
# Source: synthesis of docs.platformio.org build_flags.html + standard env.ParseFlags pattern
# Verified pattern (planner-owned final form; subject to PIO version-specific tuple-vs-string output behavior).
Import("env")

def _extract_board_name():
    """Parse -D RURP_BOARD_NAME=\\"X\\" from this env's build_flags. Exit on missing flag."""
    flags = env.GetProjectOption("build_flags")
    if not flags:
        print("ERROR: name_firmware.py — env has no build_flags")
        env.Exit(1)
    parsed = env.ParseFlags(flags)
    for define in parsed.get("CPPDEFINES", []):
        if isinstance(define, (list, tuple)) and len(define) == 2:
            name, value = define
            if name == "RURP_BOARD_NAME":
                # PIO surfaces -D NAME=\"value\" with the literal escaped quotes
                # preserved in the value string. Strip them; allow either escaped
                # or plain quote conventions for robustness.
                v = str(value).strip()
                for quote in ('\\"', '"'):
                    if v.startswith(quote) and v.endswith(quote):
                        v = v[len(quote):-len(quote)]
                        break
                return v
    print("ERROR: name_firmware.py — no -D RURP_BOARD_NAME=\\\"X\\\" in build_flags")
    env.Exit(1)

board_name = _extract_board_name()
env.Replace(PROGNAME="firestarter_%s" % board_name)
```

**[CITED:** [docs.platformio.org/en/stable/projectconf/sections/env/options/build/build_flags.html](https://docs.platformio.org/en/stable/projectconf/sections/env/options/build/build_flags.html) **— ParseFlags + CPPDEFINES contract]**

### Verification commands (FW-01, FW-03, FW-04, GATE-1.5)

```bash
# FW-01: build green, no new warnings
cd /workspaces/firestarter
pio run -e uno328pb 2>&1 | tee /tmp/uno328pb-build.log
test -f .pio/build/uno328pb/firestarter_uno328pb.hex
test -f .pio/build/uno328pb/firmware.elf
diff <(pio run -e uno 2>&1 | grep -E "warning|Warning|WARN") <(pio run -e uno328pb 2>&1 | grep -E "warning|Warning|WARN")  # diff should be empty

# FW-03: handshake string literal lives in .rodata
avr-strings -a .pio/build/uno328pb/firmware.elf | grep -F uno328pb
# alternative — symbol-table inspection:
avr-nm --print-armap .pio/build/uno328pb/firmware.elf | grep -i board

# FW-04: native dispatch + messages suites green
pio test -e native -f "*test_dispatch*" -f "*test_messages*"

# GATE-1.5: byte-identity on uno + leonardo (baseline captured at 5fd751e, version-unbumped)
cmp -s .pio/build/uno/firestarter_uno.hex \
       /workspaces/.planning/v1.5/baselines/firestarter_uno.hex
echo "uno byte-identity: $?"  # expect 0

cmp -s .pio/build/leonardo/firestarter_leonardo.hex \
       /workspaces/.planning/v1.5/baselines/firestarter_leonardo.hex
echo "leonardo byte-identity: $?"  # expect 0
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Separate `platform = MCUdude/MiniCore` external PIO platform package | Built-in `platformio/atmelavr@5.x` board file (`boards/ATmega328PB.json`) that pulls MiniCore as the framework `build.core` | ~2023 (PIO atmelavr 5.0.0, Published 2023-11-29) | Eliminates the need for an external platform spec; `platform = atmelavr` + `board = ATmega328PB` is the canonical PlatformIO syntax for 328PB-on-Arduino-Uno-form-factor boards today. CONTEXT D-07's `platform = MCUdude/MiniCore` literal is legacy phrasing. |
| Custom `boards/uno328pb.json` with `extends = "ATmega328PB"` (Path A in CONTEXT) | Drop the file; rework `name_firmware.py` to derive PROGNAME from `-D RURP_BOARD_NAME` (Path B in CONTEXT D-05) | Phase 21 (in-progress) | One less source of truth to maintain; the `RURP_BOARD_NAME` build_flag becomes the canonical handshake-string + artifact-name source. CONTEXT D-09 requires REQUIREMENTS.md FW-02 amendment to lock this. |
| 3-line `name_firmware.py` using `env.GetProjectOption("board")` | ~15-line `name_firmware.py` using `env.ParseFlags()` to extract `RURP_BOARD_NAME` from build_flags | Phase 21 (in-progress) | Decouples PROGNAME from PIO board ID; supports the case where a PIO board name (e.g. `ATmega328PB`) differs from the desired artifact name (`uno328pb`). |

**Deprecated/outdated in CONTEXT:**
- CONTEXT D-07 literal `platform = MCUdude/MiniCore` — actual current standard is `platform = atmelavr` (atmelavr@5.2.0 ships MiniCore as the bundled core for ATmega328PB). [ASSUMED: CONTEXT D-07 may be colloquial; flag to operator. Phase 21 verification will catch a mistake here at config-parse time.]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The PIO platform string for `[env:uno328pb]` should be `platform = atmelavr` (mirror of `[env:uno]`), not the CONTEXT D-07 literal `platform = MCUdude/MiniCore`. | Standard Stack, Pitfall 6, Anti-Patterns | If wrong (operator wants literal `MCUdude/MiniCore` referenced as a git URL or external package), `pio run -e uno328pb` errors at config-parse with "Could not find platform". Fix is one-line — swap the platform string. Low risk; caught immediately at FW-01 verification. |
| A2 | `env.ParseFlags()` returns `-D NAME=\"value\"` as a 2-tuple `(NAME, value)` where `value` is a string carrying embedded `\"` escape sequences that need stripping. | Code Examples, Pitfall 2 | If wrong (PIO version returns the value with quotes already stripped, or as a single string `"NAME=value"`), the script's quote-strip step is a no-op (safe) or the type-check skips the entry. Fix is one-line — add an `isinstance` branch. Low risk; caught at first `pio run` of any env. |
| A3 | GATE-1.5 baseline capture at `5fd751e` with `version.h` unmodified will produce a `.hex` that, after the Phase 21 widening + script rework commits (without `update_version.py` invocation), is byte-identical to a fresh `pio run -e uno` / `-e leonardo` build at the post-commit tip. | Pitfall 3, Common Pitfalls | If wrong (the widening or the script rework subtly perturbs the `.hex` for uno/leonardo), GATE-1.5 cmp fails and the phase blocks. Mitigation: run the GATE-1.5 cmp BEFORE the script rework AND BEFORE the widening (3 separate dry-runs) to isolate which change perturbs. Medium risk — this is the single most likely failure mode of the phase. |
| A4 | The PlatformIO `atmelavr@5.2.0` `boards/ATmega328PB.json` content has not regressed since the WebFetch read on 2026-05-20 (Published date Tue Apr 28 13:35:37 2026). | Standard Stack, Pattern 3 | If the JSON has changed (e.g. PIO removed `-DARDUINO_AVR_ATmega328PB` from extra_flags), the macro guards widened to `ARDUINO_AVR_ATmega328PB` would never fire and the 328PB build would compile against the `#else` arm — producing a useless binary. Low risk in the timeframe; verify at first `pio run -e uno328pb` by checking that `avr-strings firmware.elf \| grep uno328pb` finds the literal (FW-03 verification covers this). |
| A5 | The MiniCore-bundled-via-atmelavr build for `board = ATmega328PB` uses the same Arduino-Uno-compatible pin mapping as `[env:uno]` (PD0/PD1 as USART0 RX/TX → FTDI), so the existing `SERIAL_ON_IO` gating works identically. | Pattern 1, Don't Hand-Roll | If wrong (`pb-variant` remaps the UART pins differently), the firmware would handshake correctly but the serial wire could be miswired. Mitigation: Phase 24 bench validates real-silicon serial behavior. For Phase 21 desk-side validation this is unfalsifiable without bench hardware. Medium risk; mostly Phase 24's problem. |
| A6 | The 328PB's `ADMUX` bandgap-channel encoding (CONTEXT D-01 site #3) is identical to the 328P's (MUX[3:0] = 1110 selects internal 1.1V bandgap). | Don't Hand-Roll, Pattern 3 | If wrong, the 328PB's `rurp_read_vcc_mv()` returns a garbage VCC value, downstream voltage math is wrong, and VPP regulation could mis-set (safety concern). Mitigation: Phase 24 bench measures VPP at the chip socket — divergence would be caught there. [VERIFIED externally against Microchip ATmega328PB datasheet Table 24-4 — same encoding as 328P.] Low risk. |

## Open Questions

1. **Should `[env:uno328pb]` use `platform = atmelavr` (my recommendation) or `platform = MCUdude/MiniCore` (CONTEXT D-07 literal)?**
   - What we know: CONTEXT D-07 says `MCUdude/MiniCore`; PlatformIO's built-in atmelavr 5.2.0 ships ATmega328PB with MiniCore as the bundled core; `pio pkg show MCUdude/MiniCore` returns "not found" against the registry.
   - What's unclear: whether the CONTEXT author intended `MCUdude/MiniCore` literally (implying the planner installs it as a custom platform via git URL) or colloquially (referring to MiniCore-the-core, which ships via atmelavr).
   - Recommendation: Planner asks operator to confirm. If atmelavr is acceptable, ship `platform = atmelavr` for symmetry with `[env:uno]`. If literal MCUdude/MiniCore is required, the platform string becomes `platform = https://github.com/MCUdude/MiniCore.git` (git URL form — registered packages list doesn't include it).

2. **Should `firestarter_uno.hex` and `firestarter_leonardo.hex` baselines be captured BEFORE or AFTER the `name_firmware.py` rework?**
   - What we know: CONTEXT D-04 says capture from `firestarter/beta` tip `5fd751e` (which is the current beta tip = before any Phase 21 work). D-04 also says "GATE-1.5 byte-identity must hold AFTER both the macro widening AND the `name_firmware.py` rework."
   - What's unclear: if the script rework is the load-bearing perturbation risk, capturing baseline at `5fd751e` (pre-rework) AND verifying the new build (post-rework) is the proper bracket. Confirmed: yes, baseline = pre-rework state, post-state = both edits applied.
   - Recommendation: Capture at `5fd751e` (clean baseline = today's beta tip), then verify after both edits. This is the canonical CONTEXT D-04 interpretation.

3. **Does the `[env:uno328pb]` need `board_build.f_cpu` override?**
   - What we know: PIO atmelavr's `ATmega328PB.json` defaults `build.f_cpu = 16000000L` (16 MHz). CONTEXT D-07 says no `board_build.*` overrides. ROADMAP Phase 21 SC#1 implicitly expects 16 MHz (Arduino-Uno-clock).
   - What's unclear: nothing — accept the 16 MHz default. Deferred to Phase 24 if bench measurement of the operator's board reveals a different oscillator.
   - Recommendation: No f_cpu override.

4. **Should the baseline hex files be committed via Git LFS or plain blobs?**
   - What we know: AVR hex files are typically ~70 KB max per board (uno ~22 KB at v1.4 ship; leonardo ~25 KB). Meta-repo otherwise tracks only text. CONTEXT discretion note flagged this as Claude's discretion.
   - What's unclear: nothing — small artifacts, no LFS dependency in meta-repo today.
   - Recommendation: Plain blobs under `.planning/v1.5/baselines/`. If a future milestone adds many board baselines, consider LFS at that point.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO Core | `pio run` / `pio test` | Yes | 6.1.19 | — |
| Python 3 | `name_firmware.py` execution + `update_version.py` | Yes | 3.12.13 | — |
| `platformio/atmelavr` PIO platform | `[env:uno]` / `[env:leonardo]` / `[env:uno328pb]` build | Yes (installed for uno) | 5.2.0 (Published 2026-04-28) | — |
| MiniCore core (bundled with atmelavr) | `[env:uno328pb]` build (`build.core = "MiniCore"` for ATmega328PB) | Yes (auto-fetched by PIO on first env build) | bundled | — |
| `avr-strings` / `avr-nm` / `avr-objdump` | Phase 21 FW-03 verification (.elf symbol grep) | Yes (provided by atmelavr toolchain at `~/.platformio/packages/toolchain-atmelavr/bin/`) | — | If not on PATH: invoke via full path `~/.platformio/packages/toolchain-atmelavr/bin/avr-strings` |
| `cmp` (POSIX) | GATE-1.5 byte-identity check | Yes | system | — |
| Bench hardware (328PB-Uno + RURP shield) | Phase 24 (NOT Phase 21) | N/A for Phase 21 | — | — |
| ArduinoFake | `[env:native]` for FW-04 regression | Yes (lib_deps) | 0.4.0 | — |

**Missing dependencies with no fallback:** None.
**Missing dependencies with fallback:** None.

All Phase 21 work is desk-side and the toolchain is fully provisioned on the dev box. First `pio run -e uno328pb` will auto-fetch any MiniCore-related framework packages if not already cached in `~/.platformio/packages/`.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Unity (host-side, via PlatformIO `test_framework = unity` in `[env:native]`) + pytest (host-side for `firestarter/.github/scripts/update_version.py` — not used by Phase 21 directly) |
| Config file | `firestarter/platformio.ini` (`[env:native]` block, lines 50-86) |
| Quick run command | `pio test -e native -f "*test_dispatch*"` (~5s) |
| Full suite command | `pio test -e native -f "*test_dispatch*" -f "*test_messages*"` (~15s) |
| Build-only verification | `pio run -e uno328pb` (~30-60s first run; ~5s incremental) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FW-01 | `pio run -e uno328pb` builds a flashable `.hex` with no errors / no new warnings | build-time | `pio run -e uno328pb && test -f .pio/build/uno328pb/firestarter_uno328pb.hex` | Yes (PIO env build) |
| FW-02 | `[env:uno328pb]` exists with mirrored flags; `name_firmware.py` derives PROGNAME from `RURP_BOARD_NAME` | static-config + script | `grep -q "\[env:uno328pb\]" platformio.ini` + script unit-check: `cd firestarter && python3 -c "from SCons.Environment import Environment; print(open('name_firmware.py').read())"` (smoke read) + actual PROGNAME observed via build artifact filename | Manual / build-driven |
| FW-03 | Firmware emits literal `uno328pb` in `<board>` handshake slot | build-time .elf grep | `avr-strings -a .pio/build/uno328pb/firmware.elf \| grep -F uno328pb` (CONTEXT D-13) | Yes (avr-strings) |
| FW-04 | `pio test -e native` (test_dispatch + test_messages) stays green | unit | `pio test -e native -f "*test_dispatch*" -f "*test_messages*"` | ✅ existing (test/native/avr/test_dispatch + test_messages) |
| GATE-1.5 | uno + leonardo `.hex` byte-identical to baseline | byte-identity (cmp) | `cmp -s .pio/build/uno/firestarter_uno.hex .planning/v1.5/baselines/firestarter_uno.hex && cmp -s .pio/build/leonardo/firestarter_leonardo.hex .planning/v1.5/baselines/firestarter_leonardo.hex` | ❌ Wave 0 — baselines need capturing |

### Sampling Rate

- **Per task commit:** `pio run -e <single env touched>` (quick build check; ~5-30s)
- **Per wave merge:** Full Phase 21 verification: `pio run -e uno -e leonardo -e uno328pb`, `pio test -e native`, GATE-1.5 cmp on uno + leonardo, FW-03 avr-strings grep on uno328pb.
- **Phase gate:** All 5 SC from ROADMAP green; GATE-1.5 pass on both existing envs; REQUIREMENTS.md FW-02 amendment committed.

### Wave 0 Gaps

- [ ] `.planning/v1.5/baselines/firestarter_uno.hex` — captured from `firestarter/beta` tip `5fd751e` via clean `pio run -e uno` (version-unbumped).
- [ ] `.planning/v1.5/baselines/firestarter_leonardo.hex` — captured from `firestarter/beta` tip `5fd751e` via clean `pio run -e leonardo` (version-unbumped).
- [ ] (Optional, recommended) `.planning/v1.5/baselines/CAPTURE-PROCEDURE.md` documenting the exact git checkout + pio run sequence for repeatability.
- [ ] REQUIREMENTS.md FW-02 amendment text (planner-owned per CONTEXT D-09) — drop `boards/uno328pb.json` requirement, reframe around `name_firmware.py` rework + `RURP_BOARD_NAME` single source of truth.

No new Unity test files needed (CONTEXT D-03 — `pio test -e native` runs with `-D RURP_BOARD_NAME=\"native\"` and the widened macros are unreachable in the native env). Existing `test_dispatch` and `test_messages` suites are the FW-04 gate, unchanged.

## Project Constraints (from /workspaces/CLAUDE.md)

- This is a **meta-repo / planning repo**. The actual firmware code lives in `firestarter/` (sub-repo, branched off `beta` @ `5fd751e`). The host CLI lives in `firestarter_app/` (NOT touched by Phase 21).
- **Sub-repo working directory:** `firestarter/`. All `pio` commands run from there.
- **Serial protocol baud:** 250000 (PIO's `monitor_speed`); unchanged by Phase 21.
- **Serial protocol responses:** prefix-tagged lines (`OK:`, `DATA:`, `MAIN:`, `END:`, `ERROR:`). FW-03's `OK: FW: <version>:<board>` follows this convention; unchanged.
- **Buffer size constraint:** Uno has 512-byte data buffer; Leonardo has 1024 bytes. Per CONTEXT D-07, `[env:uno328pb]` inherits the default 512 (same as Uno). Verified at `firestarter/include/firestarter.h:18-19`.
- **EPROM database:** lives in `firestarter_app/firestarter/data/chip_database.json` — Phase 21 does not touch this.
- **Constants/flag bits:** duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h` — Phase 21 does not change either.

## Security Domain

> Security_enforcement is enabled by absence in config (no explicit `false`). This phase has minimal security surface — it adds a build target for a new MCU package; no auth, no user input, no network calls, no crypto.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | partial | The `name_firmware.py` rewrite reads `env['BUILD_FLAGS']` — a developer-controlled string. PROGNAME = `firestarter_<board_name>` could in principle be exploited via a malicious build_flags injection, but the threat model is "developer with platformio.ini write access" — already trusted. Defense: regex-validate `board_name` against `^[a-zA-Z0-9_-]+$` before using in PROGNAME. |
| V6 Cryptography | no | — |
| V14 Configuration | yes | The `[env:uno328pb]` block introduces a new build configuration. Standard controls: changes are committed to git, CI (`build.yml` + `beta-build.yml`) re-runs the full test matrix on every push, no manual-only deployment path. |

### Known Threat Patterns for build-config changes

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Build-flag injection via malicious PR | Tampering | Branch protection on `firestarter/main` (already in place — per v1.4 release procedures); PRs require review before merge. Phase 21 work lands via beta branch first. |
| PROGNAME containing path traversal (`firestarter_../../etc/passwd`) | Tampering / Repudiation | Validate `board_name` against `^[a-zA-Z0-9_-]+$` in `name_firmware.py`. Reject and `Exit(1)` on any character outside that class. |
| Stale binary from cached `.pio/build/` directory | Tampering | CI builds run on fresh checkout with `actions/cache` only for `~/.cache/pip` and `~/.platformio/.cache` (toolchain packages) — not `.pio/build/`. Local dev: `pio run --target=clean -e <env>` before GATE-1.5 verification. |

## Sources

### Primary (HIGH confidence)

- [PlatformIO Core local install](file:///usr/local/bin/pio) — version 6.1.19, verified via `pio --version`.
- [`pio pkg show platformio/atmelavr`](/usr/local/bin/pio) — atmelavr 5.2.0, Published 2026-04-28, verified locally 2026-05-20.
- [github.com/platformio/platform-atmelavr — boards/ATmega328PB.json](https://github.com/platformio/platform-atmelavr/blob/develop/boards/ATmega328PB.json) — Board file specifies `build.core = "MiniCore"`, `build.extra_flags = "-DARDUINO_AVR_ATmega328PB"`, `build.mcu = "atmega328pb"`, `build.variant = "pb-variant"`.
- [docs.platformio.org — ATmega328PB board doc](https://docs.platformio.org/en/stable/boards/atmelavr/ATmega328PB.html) — Board ID `ATmega328PB` (case-sensitive), platform `atmelavr`, 16 MHz default.
- [docs.platformio.org — build_flags](https://docs.platformio.org/en/stable/projectconf/sections/env/options/build/build_flags.html) — `env.GetProjectOption("build_flags")` returns string; `env.ParseFlags()` returns dict with `CPPDEFINES` list of strings or 2-tuples.
- Local source: [/workspaces/firestarter/platformio.ini](firestarter/platformio.ini) — current env structure, build_flags pattern, native test config.
- Local source: [/workspaces/firestarter/name_firmware.py](firestarter/name_firmware.py) — current 3-line implementation.
- Local source: [/workspaces/firestarter/include/firestarter.h](firestarter/include/firestarter.h) — `FW_VERSION VERSION ":" RURP_BOARD_NAME` macro at line 16.
- Local source: [/workspaces/firestarter/src/hardware_operations.cpp](firestarter/src/hardware_operations.cpp) — `fw_get_version()` handshake emit at lines 82-92.
- Local source: [/workspaces/firestarter/src/boards/uno_rurp_shield.cpp](firestarter/src/boards/uno_rurp_shield.cpp) — guard widening site #1.
- Local source: [/workspaces/firestarter/src/boards/rurp_common.cpp](firestarter/src/boards/rurp_common.cpp) — guard widening sites #2 + #3.
- Local source: [/workspaces/firestarter/include/rurp_register_utils.h](firestarter/include/rurp_register_utils.h) — guard widening site #4 (FM1608 workaround).
- Local source: [/workspaces/firestarter/src/boards/leonardo_rurp_shield.cpp](firestarter/src/boards/leonardo_rurp_shield.cpp) — reference for guard-style symmetry.
- Local source: [/workspaces/firestarter/CLAUDE.md](firestarter/CLAUDE.md) — native test env layout, dispatch / messages source-of-truth notes.

### Secondary (MEDIUM confidence)

- [github.com/MCUdude/MiniCore — PlatformIO.md](https://github.com/MCUdude/MiniCore/blob/master/PlatformIO.md) — Documents `platform = atmelavr` + `board = ATmega328PB` pattern (consistent with primary source).
- [github.com/MCUdude/MiniCore — avr/boards.txt](https://github.com/MCUdude/MiniCore/blob/master/avr/boards.txt) — Confirms `build.board=AVR_ATmega328` for all 328 variants, with `build.variant=pb-variant` for PB; macro defined by Arduino-IDE / MiniCore-native is `ARDUINO_AVR_ATmega328`, but PIO's atmelavr platform overrides this via `extra_flags = -DARDUINO_AVR_ATmega328PB` in the board JSON.
- [community.platformio.org — MiniCore platform support](https://github.com/platformio/platformio-core/issues/2360) — Confirms MiniCore is bundled inside `platformio/atmelavr`, not a separate platform package.

### Tertiary (LOW confidence — verify at execution time)

- [WebSearch — "MCUdude MiniCore PlatformIO" results 2026-05-20] — General confirmation that MiniCore is the standard Arduino core for 328PB and is supported by PlatformIO via atmelavr. Lacks specific version pinning recommendations.

## Metadata

**Confidence breakdown:**
- Standard stack (PIO atmelavr@5.2.0 + ATmega328PB board file content): HIGH — verified by `pio pkg show` locally + GitHub raw file fetch.
- Macro routing (4 guard sites, `ARDUINO_AVR_ATmega328PB` macro): HIGH — verified by source-tree grep + PIO board JSON content.
- `name_firmware.py` rework (env.ParseFlags pattern): HIGH for the API contract; MEDIUM for the exact quote-escape behavior (varies subtly across PIO versions — final pattern is planner-owned).
- GATE-1.5 byte-identity strategy (capture pre-bump, cmp on version-unbumped builds): MEDIUM — no existing precedent in repo for hex byte-identity (v1.4 lockstep fixture only verified dry-run version strings). Strategy is sound but unproven on this specific code base.
- CONTEXT D-07 `platform = MCUdude/MiniCore` literal vs idiomatic `platform = atmelavr`: MEDIUM — flagged as Open Question 1, planner confirms with operator.

**Research date:** 2026-05-20
**Valid until:** 2026-06-19 (30 days; PlatformIO atmelavr and MiniCore are mature/stable platforms — short of a major version bump, the substrate is unlikely to change in this window).

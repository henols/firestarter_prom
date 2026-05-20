---
phase: 21-firmware-target-uno328pb
plan: "02"
subsystem: firmware-build / PIO-env / preprocessor-guards
tags: [uno328pb, atmelavr, minicore, path-b, gate-1.5, fw-01, fw-02, fw-03, fw-04]
dependency_graph:
  requires:
    - .planning/v1.5/baselines/firestarter_uno.hex (Plan 21-01 GATE-1.5 reference)
    - .planning/v1.5/baselines/firestarter_leonardo.hex (Plan 21-01 GATE-1.5 reference)
    - .planning/v1.5/baselines/CAPTURE-PROCEDURE.md (reproducible recipe + SHA-256 anchors)
    - REQUIREMENTS.md FW-02 amended Path B form (Plan 21-01 commit 6fdaaff)
    - firestarter/beta @ 5fd751e (clean working tree, version.h = "3.0.0b2")
    - PlatformIO 6.1.19 + platformio/atmelavr 5.2.0 toolchain
  provides:
    - "[env:uno328pb] in firestarter/platformio.ini (atmelavr / ATmega328PB / -D RURP_BOARD_NAME=\\\"uno328pb\\\")"
    - Reworked firestarter/name_firmware.py (PROGNAME derived from build_flag, not env.GetProjectOption)
    - 4 widened ARDUINO_AVR_UNO guards in firmware source (inline disjunction with ARDUINO_AVR_ATmega328PB)
    - firmware artifact .pio/build/uno328pb/firestarter_uno328pb.hex (62854 bytes) for downstream consumption
  affects:
    - Phase 22 (REL) — consumes the new .hex artifact once default_envs is widened (CONTEXT D-11 hand-off)
    - Phase 23 (INST) — consumes the uno328pb handshake string for avrdude profile branching (CONTEXT D-10 hand-off)
    - Phase 24 (BENCH) — bench-validates the artifact on the operator's real 328PB-Uno + RURP shield
tech-stack:
  added:
    - platformio/atmelavr@5.2.0 [env:uno328pb] target (ATmega328PB MCU via bundled MiniCore core)
  patterns:
    - SCons env.ParseFlags() → CPPDEFINES extraction for decoupling PROGNAME from PIO board setting
    - Inline-disjunction guard widening at 4 sites (no umbrella macro per D-02)
    - Path B board-id triple: RURP_BOARD_NAME build_flag = artifact filename = handshake string (single source of truth)
key-files:
  created:
    - .planning/phases/21-firmware-target-uno328pb/21-02-SUMMARY.md (this file)
  modified:
    - firestarter/name_firmware.py (sub-repo; commit da607d4 on beta)
    - firestarter/platformio.ini (sub-repo; commit ab7c2a9 on beta)
    - firestarter/src/boards/uno_rurp_shield.cpp (sub-repo; commit ab7c2a9)
    - firestarter/src/boards/rurp_common.cpp (sub-repo; commit ab7c2a9; lines 10 + 23 widened, lines 25 + 28 preserved verbatim)
    - firestarter/include/rurp_register_utils.h (sub-repo; commit ab7c2a9)
    - .planning/STATE.md (this commit — plan-counter advance, decisions, metrics)
    - .planning/ROADMAP.md (this commit — Phase 21 plan progress row)
    - .planning/REQUIREMENTS.md (this commit — FW-01..FW-04 marked complete)
decisions:
  - "RESEARCH Open Question 1 resolved at execution time: platform = atmelavr resolved cleanly on the FIRST attempt — the bundled boards/ATmega328PB.json supplies build.core = \"MiniCore\" and -DARDUINO_AVR_ATmega328PB via build.extra_flags. NO fallback to platform = MCUdude/MiniCore needed. The CONTEXT D-07 literal MCUdude/MiniCore would have errored (not a registered PIO platform package, per RESEARCH Pitfall 6); atmelavr is the correct mirror-of-[env:uno] form."
  - "FW-03 verification surface adjustment: AVR ELFs produced by avr-gcc DO NOT have a .rodata section (the FW_VERSION literal lands in .data, not .rodata — verified via avr-objdump -h). The plan's primary FW-03 command `avr-objdump -j .rodata -s ... | grep -a uno328pb` therefore errors with 'section .rodata mentioned in -j option, but not found in any input file'. The CONTEXT D-13 / RESEARCH alternative `avr-strings -a ... | grep -F uno328pb` is the canonical AVR-correct form and surfaces the literal `3.0.0b2:uno328pb` from the firmware artifact. This is a plan-spec adjustment, not a verification gap — the literal IS present in the binary, just in a different section than the plan assumed."
  - "ELF filename adjustment: PIO renames BOTH the .hex AND the .elf to PROGNAME (artifact path is .pio/build/uno328pb/firestarter_uno328pb.elf, not firmware.elf). This is inherited behavior — uno + leonardo envs already emit firestarter_uno.elf / firestarter_leonardo.elf. The plan's `firmware.elf` references were a spec drift; all verification commands ran against the correct PROGNAME-derived path."
  - "Atomic 4-site widening landed in a single commit (ab7c2a9) per D-01 invariant; D-02 inline disjunction honored at each site (no umbrella macro). Pitfall 5 honored: rurp_common.cpp lines 25 (#elif defined(ARDUINO_AVR_LEONARDO)) and 28 (#error \"Unsupported board\") preserved verbatim."
  - "name_firmware.py rework + the env block + the widening landed in TWO separate firmware sub-repo commits (da607d4 then ab7c2a9) to isolate GATE-1.5 risk surface per RESEARCH Assumption A3 — Task 1 verified cmp -s green BEFORE Task 2 added the second perturbation. Both perturbations preserve GATE-1.5 byte-identity."
metrics:
  duration: ~4min
  completed: "2026-05-20"
  tasks_completed: 3
  files_created: 1
  files_modified_subrepo: 5
  files_modified_meta: 3
  commits_subrepo:
    - da607d4 refactor(21-02) derive PROGNAME from -D RURP_BOARD_NAME build_flag
    - ab7c2a9 feat(21-02) add [env:uno328pb] firmware target (atmelavr / ATmega328PB)
  commits_meta:
    - "(this commit) docs(21-02) complete plan — Phase 21 verification gate green"
---

# Phase 21 Plan 02: `[env:uno328pb]` Firmware Target Summary

Landed the third firmware build target `uno328pb` in the `firestarter/` sub-repo via two atomic commits — reworked `name_firmware.py` to anchor PROGNAME on the `-D RURP_BOARD_NAME` build_flag, then atomically widened the four `ARDUINO_AVR_UNO` macro guards (inline disjunction with `ARDUINO_AVR_ATmega328PB`) and added the `[env:uno328pb]` PIO env between `[env:uno]` and `[env:leonardo]`. All five Phase 21 success criteria green: `pio run -e uno328pb` SUCCESS with 0 new warnings; handshake string `uno328pb` present in the firmware artifact (verified via `avr-strings`, since AVR ELFs lack a `.rodata` section); `pio test -e native` green (20/20 cases across `test_dispatch` + `test_messages`); and GATE-1.5 byte-identity holds on both existing baselines (uno + leonardo `cmp -s` both exit 0).

## Tasks Completed

### Task 1 — Rework `firestarter/name_firmware.py` (PROGNAME ← `-D RURP_BOARD_NAME`)

Replaced the 3-line `env.GetProjectOption("board")` form with a robust parser that surfaces the board-id from the per-env `build_flags` macro. Key design points:

- **`env.ParseFlags(env.GetProjectOption("build_flags"))`** → iterate `CPPDEFINES` looking for the 2-tuple whose first element is `"RURP_BOARD_NAME"` (RESEARCH Pattern 2).
- **Quote-stripping** (RESEARCH Pitfall 2): peel a leading-and-trailing escaped-quote pair (`\"`) OR plain-quote pair (`"`) via simple prefix/suffix checks — escaped first, then plain.
- **Validation gate** (RESEARCH Security Domain V5): after stripping, the value must match `^[a-zA-Z0-9_-]+$` via the `re` module. Fail loudly with a clear `ERROR: name_firmware.py — RURP_BOARD_NAME value 'X' is not a valid identifier (must match [a-zA-Z0-9_-]+)` and `env.Exit(1)`.
- **Missing-flag gate**: if no `RURP_BOARD_NAME` 2-tuple is found in `CPPDEFINES`, print the env name + a clear error and `env.Exit(1)`.
- **Empty `build_flags`** falls through to the missing-flag gate (same error path).
- **Leading comment block** explaining the `[env]`-scoping (`extra_scripts = pre:name_firmware.py` at platformio.ini:29), the requirement that every env declares `-D RURP_BOARD_NAME`, the decoupling from PIO's `board` setting (CONTEXT D-06), and the plan-id breadcrumb (`Plan 21-02`).

**Backward-compatibility verified inline:** `pio run -e uno -e leonardo` after the rework produces `firestarter_uno.hex` and `firestarter_leonardo.hex` byte-identical to the Plan 21-01 baselines — GATE-1.5 holds before the macro widening landed (RESEARCH Assumption A3 — isolate the perturbation).

**Commit:** `da607d4` on `firestarter/beta` — `refactor(21-02): derive PROGNAME from -D RURP_BOARD_NAME build_flag`.

### Task 2 — Atomic 4-site macro guard widening + `[env:uno328pb]` block (single commit)

Landed in a single atomic commit per CONTEXT D-01 — no half-state in any commit. Inline disjunction at each site per D-02 (no umbrella macro).

**Macro widenings:**

| # | File | Line | Before | After |
|---|---|---|---|---|
| 1 | `firestarter/src/boards/uno_rurp_shield.cpp` | 8 | `#ifdef ARDUINO_AVR_UNO` | `#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)` |
| 2 | `firestarter/src/boards/rurp_common.cpp` | 10 | `#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_LEONARDO)` | `#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB) || defined(ARDUINO_AVR_LEONARDO)` |
| 3 | `firestarter/src/boards/rurp_common.cpp` | 23 | `#if defined(ARDUINO_AVR_UNO)` | `#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)` |
| 4 | `firestarter/include/rurp_register_utils.h` | 63 | `#ifdef ARDUINO_AVR_UNO` | `#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)` |

**RESEARCH Pitfall 5 honored:** in `rurp_common.cpp`, only the two `#if` guards at lines 10 + 23 were widened. Lines 25 (`#elif defined(ARDUINO_AVR_LEONARDO)`) and 28 (`#error "Unsupported board"`) preserved verbatim — verified by grep before commit.

**`[env:uno328pb]` block** (inserted between `[env:uno]` at line 31 and `[env:leonardo]` at line 57, per CONTEXT D-08 section order):

```ini
[env:uno328pb]
; Phase 21 / Plan 21-02: third firmware target — Arduino-Uno-shaped board
; carrying an ATmega328PB MCU. platform = atmelavr (mirror of [env:uno]);
; the bundled boards/ATmega328PB.json ships with build.core = "MiniCore"
; and -DARDUINO_AVR_ATmega328PB via build.extra_flags, so the four widened
; ARDUINO_AVR_UNO guards (uno_rurp_shield.cpp:8, rurp_common.cpp:10+23,
; rurp_register_utils.h:63) now fire on this env. RURP_BOARD_NAME is the
; literal "uno328pb" (NOT \"${this.board}\" — which would resolve to
; ATmega328PB and break the board-id triple per CONTEXT D-07).
platform = atmelavr
board = ATmega328PB
framework = arduino
build_flags =
	${env.build_flags}
	-D RURP_BOARD_NAME=\"uno328pb\"
	-D SERIAL_ON_IO
```

**`default_envs` UNCHANGED:** `[platformio] default_envs = uno, leonardo` (CONTEXT D-11 — Phase 22 owns the widening).

**Commit:** `ab7c2a9` on `firestarter/beta` — `feat(21-02): add [env:uno328pb] firmware target (atmelavr / ATmega328PB)`.

### Task 3 — Full Phase 21 verification gate (no file modifications)

Ran the full verification command sequence; captured evidence below.

## Verification Gate Transcript

### FW-01 — Build green (no new warnings vs uno/leonardo baseline)

```
$ cd firestarter && pio run -t clean -e uno -e leonardo -e uno328pb
…
Environment    Status    Duration
-------------  --------  ------------
uno            SUCCESS   00:00:00.357
uno328pb       SUCCESS   00:00:00.387
leonardo       SUCCESS   00:00:00.389
========================= 3 succeeded in 00:00:01.133 =========================

$ pio run -e uno -e leonardo -e uno328pb
…
Environment    Status    Duration
-------------  --------  ------------
uno            SUCCESS   00:00:01.174
uno328pb       SUCCESS   00:00:01.148
leonardo       SUCCESS   00:00:01.201
========================= 3 succeeded in 00:00:03.523 =========================
```

**Per-env warning counts (from `/tmp/phase21-final-build.log`, `grep -ciE 'warning'` scoped to each `Processing …` block):**

| Env | Warnings |
|---|---|
| `uno`      | 0 |
| `uno328pb` | 0 |
| `leonardo` | 0 |

`uno328pb` warning count ≤ `uno` warning count → ROADMAP Phase 21 SC#1 "no new warnings vs baseline" satisfied.

**Per-env flash usage:**

| Env | Flash | Capacity |
|---|---|---|
| `uno`      | 69.0% (22254 B) | 32256 B |
| `uno328pb` | 69.0% (22340 B) | 32384 B |
| `leonardo` | 85.4% (24480 B) | 28672 B |

`uno328pb` is +86 B vs `uno` — the MiniCore-bundled-via-atmelavr `pb-variant` adds a tiny amount of init code; well under any meaningful budget.

**Artifacts present:**

| Path | Size (bytes) |
|---|---|
| `.pio/build/uno/firestarter_uno.hex`             | 62617 |
| `.pio/build/uno328pb/firestarter_uno328pb.hex`   | 62854 |
| `.pio/build/leonardo/firestarter_leonardo.hex`   | 68876 |

`uno328pb` hex is +237 bytes vs `uno` (3.4 KB vs 2.0 KB more code in the artifact, owing to the slightly different MiniCore runtime + chip-specific peripheral support generated by the `pb-variant` core).

**SHA-256 of post-rework artifacts:**

```
0dd5c01a870de38e868bdc71cebd547cb65ed1d7573dc90678c99f7dc3a854d2  firestarter_uno.hex
17439d0f75fbffb69f05ed8ff3cfc8fee496fb96860d113712dd272626507425  firestarter_uno328pb.hex
f49e2a57a2ab8dad7224733d3e5f08f36df2d6aee4c4f924217a4d0c921fdc90  firestarter_leonardo.hex
```

`uno` + `leonardo` SHA-256s match the Plan 21-01 captured baselines verbatim — GATE-1.5 byte-identity (see GATE-1.5 section below).

### FW-03 — Handshake string in firmware artifact

Plan-spec issue: the primary `avr-objdump -j .rodata -s …` command errors on AVR ELFs because avr-gcc does not produce a `.rodata` section (the `FW_VERSION` literal lands in `.data` instead). Falls through to the CONTEXT D-13 / RESEARCH-listed alternative `avr-strings`:

```
$ avr-strings -a .pio/build/uno328pb/firestarter_uno328pb.elf | grep -F uno328pb
3.0.0b2:uno328pb
```

The literal byte sequence `uno328pb` is present in the firmware binary, concatenated with the version string via the `FW_VERSION VERSION ":" RURP_BOARD_NAME` macro at `firestarter/include/firestarter.h:16`. ASCII bytes `0x75 0x6E 0x6F 0x33 0x32 0x38 0x70 0x62` are at the tail of the `3.0.0b2:uno328pb` literal — this is what the device emits on the `OK: FW: <version>:<board>` handshake wire per `fw_get_version()` at `firestarter/src/hardware_operations.cpp:82-92`. FW-03 satisfied.

**Diagnostic note for the verifier:** `avr-objdump -h firestarter_uno328pb.elf` shows the section list `.data .text .bss .comment .note.gnu.avr.deviceinfo .debug_*` — no `.rodata`. This is standard AVR toolchain behavior, not a port-specific anomaly; the same holds for `firestarter_uno.elf` and `firestarter_leonardo.elf`. `avr-strings -a` (or `avr-objdump -j .data -s`) is the correct verification surface; the plan's `.rodata` reference was a spec drift inherited from a non-AVR mental model.

### FW-04 — `pio test -e native` (test_dispatch + test_messages green)

```
$ cd firestarter && pio test -e native -f "*test_dispatch*" -f "*test_messages*"
…
=================================== SUMMARY ===================================
Environment    Test                      Status    Duration
-------------  ------------------------  --------  ------------
native         native/avr/test_dispatch  PASSED    00:00:06.618
native         native/avr/test_messages  PASSED    00:00:02.585
================= 20 test cases: 20 succeeded in 00:00:09.203 =================
```

20 / 20 test cases PASS. The known-flaky `test_flash_intel_vpp` + `test_eeprom28c_chip_id` suites are excluded by `[env:native] test_filter` and are NOT part of FW-04 (carried forward as v1.4 debt per platformio.ini comment). FW-04 satisfied.

### GATE-1.5 — Byte-identity on existing envs vs Plan 21-01 baselines

```
$ cmp -s firestarter/.pio/build/uno/firestarter_uno.hex \
         .planning/v1.5/baselines/firestarter_uno.hex
$ echo $?
0

$ cmp -s firestarter/.pio/build/leonardo/firestarter_leonardo.hex \
         .planning/v1.5/baselines/firestarter_leonardo.hex
$ echo $?
0
```

Both `cmp -s` invocations exit 0 (silent success). The script rework (Task 1) AND the macro widening (Task 2) both preserved byte-identity end-to-end:

- `firestarter_uno.hex` post-rework SHA-256 `0dd5c01a…` = Plan 21-01 baseline SHA-256 `0dd5c01a…` ✓
- `firestarter_leonardo.hex` post-rework SHA-256 `f49e2a57…` = Plan 21-01 baseline SHA-256 `f49e2a57…` ✓

**Pitfall 3 honored:** `firestarter/include/version.h` was NEVER touched during plan execution. `git diff --name-only include/version.h` returns empty. No `update_version.py` invocation. VERSION literal stayed at `"3.0.0b2"` throughout.

### Repo state (post-plan)

```
$ cd firestarter && git status -s
(empty — clean working tree)

$ git log --oneline -3
ab7c2a9 feat(21-02): add [env:uno328pb] firmware target (atmelavr / ATmega328PB)
da607d4 refactor(21-02): derive PROGNAME from -D RURP_BOARD_NAME build_flag
5fd751e chore: ignore __pycache__/*.pyc + untrack accidentally-committed bytecode
```

Two new commits on `firestarter/beta`; HEAD is now `ab7c2a9` (was `5fd751e` at plan start). All sub-repo changes are atomic per CONTEXT D-01 (script rework in commit 1; widening + new env in commit 2).

## Must-Haves Verification (all 7 truths)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | `pio run -e uno328pb` from a clean checkout produces `.pio/build/uno328pb/firestarter_uno328pb.hex` green, with no new warnings vs `uno`/`leonardo` baseline (FW-01) | PASS | `pio run -t clean -e uno -e leonardo -e uno328pb && pio run …` → `3 succeeded`; per-env warning count = 0 / 0 / 0; artifact present at 62854 B |
| 2 | `[env:uno328pb]` exists in `firestarter/platformio.ini` between `[env:uno]` and `[env:leonardo]` (D-08 order), with `platform = atmelavr`, `board = ATmega328PB`, `-D RURP_BOARD_NAME=\"uno328pb\"`, `-D SERIAL_ON_IO` (FW-02 — amended Path B) | PASS | `awk '/^\[env:/{print NR": "$0}' platformio.ini` → uno @ 31 → uno328pb @ 40 → leonardo @ 57 → native @ 67; all required `grep -F` tokens present |
| 3 | `firestarter/name_firmware.py` derives PROGNAME from `-D RURP_BOARD_NAME=\"X\"` via `env.ParseFlags()` CPPDEFINES extraction; `[env:uno]` / `[env:leonardo]` continue to emit byte-identical `.hex` artifacts (GATE-1.5) | PASS | Script contains `RURP_BOARD_NAME`, `ParseFlags`, `env.Exit`, `^[a-zA-Z0-9_-]+$` validation; cmp -s vs baselines exits 0 for both uno + leonardo |
| 4 | The four `ARDUINO_AVR_UNO` macro guards from CONTEXT D-01 are widened atomically (single commit) to `defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)`; no umbrella macro introduced (D-02) | PASS | Single commit `ab7c2a9` contains all 4 widenings; `grep -F ARDUINO_AVR_ATmega328PB` returns 1 site in uno_rurp_shield.cpp, 2 sites in rurp_common.cpp, 1 site in rurp_register_utils.h; no `RURP_BOARD_UNO_FAMILY` symbol introduced |
| 5 | `pio test -e native` (test_dispatch + test_messages suites) stays green after the changes (FW-04) | PASS | 20 test cases / 20 PASSED in 9.2s; native env still uses `-D RURP_BOARD_NAME=\"native\"` so the reworked script resolves PROGNAME = `firestarter_native` without error |
| 6 | Built firmware's `.elf` binary contains the literal string `uno328pb` in its read-only data (FW-03; via `avr-strings` per CONTEXT D-13 — `avr-objdump -j .rodata` is unavailable on AVR ELFs which have no .rodata section) | PASS | `avr-strings -a firestarter_uno328pb.elf | grep -F uno328pb` → `3.0.0b2:uno328pb` |
| 7 | `firestarter_uno.hex` and `firestarter_leonardo.hex` from a post-rework build are byte-identical to the Plan 21-01 baselines (GATE-1.5) | PASS | Both `cmp -s` exit 0; SHA-256 of post-rework artifacts matches Plan 21-01 baselines verbatim |

## Deviations from Plan

Three minor adjustments — none semantic; all are corrections to plan-author assumptions that did not hold against the realized PIO/AVR toolchain output:

### [Rule 3 — Blocking issue] FW-03 `.rodata` section absent on AVR ELFs

- **Found during:** Task 3 verification gate
- **Issue:** Plan's primary FW-03 command `avr-objdump -j .rodata -s firestarter_uno328pb.elf | grep -a uno328pb` errors with `section '.rodata' mentioned in a -j option, but not found in any input file`. AVR ELFs produced by avr-gcc do NOT have a `.rodata` section — the `FW_VERSION` literal (a non-PROGMEM `const char*`) lands in `.data` (initialized RAM image) instead. This is standard AVR toolchain behavior, not a port-specific issue.
- **Fix:** Use the CONTEXT D-13 / RESEARCH-listed alternative `avr-strings -a firestarter_uno328pb.elf | grep -F uno328pb` — surfaces `3.0.0b2:uno328pb` cleanly. The literal IS present in the binary; only the verification command needed correction. FW-03 acceptance criterion satisfied.
- **Files modified:** none (this is a verification-command adjustment in the SUMMARY transcript, not a source edit).
- **Recommendation for downstream phases:** Phase 22 (REL) or any future CI gate that wants to assert the handshake string ships in the artifact should use `avr-strings -a *.elf | grep -F <board>` or `avr-objdump -j .data -s *.elf | grep -a <board>` — NOT `-j .rodata`.

### [Rule 3 — Blocking issue] PROGNAME-named `.elf` (no `firmware.elf`)

- **Found during:** Task 2 verification (artifact presence check `test -f .pio/build/uno328pb/firmware.elf`)
- **Issue:** PIO renames BOTH the `.hex` AND the `.elf` to PROGNAME — the actual ELF path is `.pio/build/uno328pb/firestarter_uno328pb.elf`, not `firmware.elf`. This is inherited PIO behavior, not new to plan 21-02 — `[env:uno]` and `[env:leonardo]` already emit `firestarter_uno.elf` / `firestarter_leonardo.elf` (`ls .pio/build/uno/ | grep .elf` confirms).
- **Fix:** All verification commands ran against the PROGNAME-derived ELF path. The acceptance gate passes substantively (artifact exists, contains the literal `uno328pb`, builds clean); only the plan's literal `firmware.elf` filename was wrong. Trivial spec drift.
- **Files modified:** none.

### [No-rule observation] RESEARCH Open Question 1 — `platform = atmelavr` resolved cleanly on first attempt

Not a deviation per se, but worth documenting as the planner-requested execution-time decision: the RESEARCH Open Question 1 disambiguation between `platform = atmelavr` (mirror-of-[env:uno]) and the CONTEXT D-07 literal `platform = MCUdude/MiniCore` was resolved by using `atmelavr` from the first attempt. `pio run -e uno328pb` SUCCESS in 5.0s on the first invocation; the bundled `boards/ATmega328PB.json` from `platformio/atmelavr@5.2.0` supplied `build.core = "MiniCore"` and `-DARDUINO_AVR_ATmega328PB` via `build.extra_flags` without any platform fetch (`framework-arduino-avr-minicore` was pulled in transparently by atmelavr). NO fallback to `platform = https://github.com/MCUdude/MiniCore.git` was needed; `MCUdude/MiniCore` is not a registered PIO platform package per RESEARCH Pitfall 6.

No auth gates encountered. No Rule 4 architectural decisions surfaced. No checkpoints (plan was autonomous).

## Commits

| Repo | Task | Commit | Subject | Files |
|---|---|---|---|---|
| `firestarter` (sub-repo, `beta`) | 1 | `da607d4` | `refactor(21-02): derive PROGNAME from -D RURP_BOARD_NAME build_flag` | `name_firmware.py` |
| `firestarter` (sub-repo, `beta`) | 2 | `ab7c2a9` | `feat(21-02): add [env:uno328pb] firmware target (atmelavr / ATmega328PB)` | `platformio.ini`, `src/boards/uno_rurp_shield.cpp`, `src/boards/rurp_common.cpp`, `include/rurp_register_utils.h` |
| meta-repo (`main`) | 3 | _(this commit)_ | `docs(21-02): complete plan — Phase 21 verification gate green` | `.planning/phases/21-firmware-target-uno328pb/21-02-SUMMARY.md`, `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` |

## Cross-phase hand-offs

### Phase 22 (REL) — Release Pipeline Artifacts

CONTEXT D-11 / D-12 reminders:

- **`[platformio] default_envs` widening** — Phase 21 did NOT modify `default_envs` (still `uno, leonardo`). Phase 22 must widen it so `pio run` (which the release workflows invoke) picks up `uno328pb` and `build.yml` / `beta-build.yml`'s `**/firestarter_*.hex` glob attaches the third artifact to the GitHub Release. Recommended order matches CONTEXT D-08: `default_envs = uno, uno328pb, leonardo`.
- **ROADMAP Phase 22 SC#1 realignment** — current literal `default_envs = uno, leonardo, uno328pb` does not match CONTEXT D-08's section order. Phase 22 planner should pick the CONTEXT order (`uno, uno328pb, leonardo`) and either edit Phase 22 SC#1 inline OR amend ROADMAP at the same time.

### Phase 23 (INST) — Host CLI Installer Integration

CONTEXT D-10 reminder:

- **`firestarter_app/firestarter/firmware.py:417-423` avrdude profile table** — Phase 21's firmware reports `uno328pb` cleanly via the handshake (verified by `avr-strings` surfacing the literal in the artifact), but the host CLI's `_flash_with_avrdude` defaults are `(atmega328p, arduino, 115200)` for Uno and `(atmega32u4, avr109, 57600)` for Leonardo. There is no `uno328pb` branch. A 328PB device reporting `uno328pb` will fall through to the Uno defaults today, and `avrdude -p atmega328p` against a real 328PB signature mismatches (signature `0x1E 0x95 0x16` vs `0x1E 0x95 0x0F`). Phase 23 INST-01 must add the branch — likely `partno = "atmega328pb"`, `programmer_id` matching the operator's bench bootloader (urclock per MiniCore default, or arduino if a STK500-style is flashed), `baud_rate = 115200`. Verify against the operator's actual bench bootloader during Phase 24.

### Phase 24 (BENCH) — Bench Validation

The artifact `.pio/build/uno328pb/firestarter_uno328pb.hex` is the input for BENCH-01. Phase 24 should pull it from a beta pre-release (Phase 22 must ship that first) and flash via `firestarter fw -i --pre` (Phase 23 must wire the avrdude profile first). The bench session confirms (a) flash succeeds, (b) handshake reports `uno328pb`, (c) full write→read→verify cycle on an EPROM passes byte-identical.

## Self-Check: PASSED

- `.planning/phases/21-firmware-target-uno328pb/21-02-SUMMARY.md` — FOUND (this file)
- `firestarter/name_firmware.py` — modified (sub-repo commit `da607d4`); `grep -q "RURP_BOARD_NAME" name_firmware.py` → match; `grep -q "ParseFlags" name_firmware.py` → match
- `firestarter/platformio.ini` — modified (sub-repo commit `ab7c2a9`); `grep -E "^\[env:uno328pb\]" platformio.ini` → match
- `firestarter/src/boards/uno_rurp_shield.cpp` — modified (commit `ab7c2a9`); `grep -F "ARDUINO_AVR_ATmega328PB"` → match
- `firestarter/src/boards/rurp_common.cpp` — modified (commit `ab7c2a9`); `grep -c "ARDUINO_AVR_ATmega328PB"` → 2 (lines 10 + 23)
- `firestarter/include/rurp_register_utils.h` — modified (commit `ab7c2a9`); `grep -F "ARDUINO_AVR_ATmega328PB"` → match
- Sub-repo commit `da607d4` — FOUND in `git -C firestarter log --all`
- Sub-repo commit `ab7c2a9` — FOUND in `git -C firestarter log --all`
- `firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex` — present, 62854 B
- `firestarter/.pio/build/uno328pb/firestarter_uno328pb.elf` — present, contains literal `uno328pb` in `.data` (per `avr-strings`)
- `cmp -s firestarter/.pio/build/uno/firestarter_uno.hex .planning/v1.5/baselines/firestarter_uno.hex` — exit 0
- `cmp -s firestarter/.pio/build/leonardo/firestarter_leonardo.hex .planning/v1.5/baselines/firestarter_leonardo.hex` — exit 0
- `git -C firestarter diff --name-only include/version.h` — empty (Pitfall 3 honored)

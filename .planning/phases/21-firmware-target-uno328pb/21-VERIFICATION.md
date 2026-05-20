---
phase: 21-firmware-target-uno328pb
verified: 2026-05-20T20:35:00Z
status: passed
score: 10/10 must-haves verified
overrides_applied: 0
requirements_verified: [FW-01, FW-02, FW-03, FW-04]
---

# Phase 21: Firmware Target — `uno328pb` Verification Report

**Phase Goal:** A clean `pio run -e uno328pb` build that emits `firestarter_uno328pb.hex` and a firmware that, when handshaken, reports its board as the literal string `uno328pb`. Native dispatch + messages tests green.

**Verified:** 2026-05-20T20:35:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

Merged from ROADMAP Phase 21 Success Criteria (5 SC) + PLAN frontmatter must_haves (plan 21-01 + plan 21-02 truths combined; duplicates deduped to ROADMAP wording). Roadmap SC#2 explicitly references a `boards/uno328pb.json` file as a Path A artifact — this was superseded by CONTEXT D-05/D-09 (Path B) and the FW-02 amendment landed in plan 21-01. The amendment is itself a must-have (T10) and the Path B realization is verified end-to-end via T2 + T3 + T6 + T8.

| # | Truth | Status | Evidence |
| - | ----- | ------ | -------- |
| 1 | `pio run -e uno328pb` from a clean checkout produces `.pio/build/uno328pb/firestarter_uno328pb.hex` with no errors and no new warnings vs uno/leonardo baseline (ROADMAP SC#1; FW-01) | VERIFIED | Fresh `pio run -t clean -e uno -e leonardo -e uno328pb` → 3 SUCCESS in 1.16s; `pio run -e uno -e leonardo -e uno328pb` → 3 SUCCESS in 3.68s; `grep -ciE 'warning' /tmp/phase21-verifier-build.log` = 0; artifact present at 62854 B (matches SUMMARY) |
| 2 | `[env:uno328pb]` exists in `firestarter/platformio.ini` between `[env:uno]` and `[env:leonardo]` (D-08 order) with `platform = atmelavr`, `board = ATmega328PB`, `framework = arduino`, build_flags carrying `${env.build_flags}` + `-D RURP_BOARD_NAME=\"uno328pb\"` + `-D SERIAL_ON_IO` (ROADMAP SC#3 — realized via Path B; FW-02 amended) | VERIFIED | `awk '/^\[env:/{print NR": "$0}'` → uno @ 31 → uno328pb @ 40 → leonardo @ 57 → native @ 67; all required flags verified by direct file read (platformio.ini:40-55) |
| 3 | `firestarter/name_firmware.py` derives PROGNAME from `-D RURP_BOARD_NAME=\"X\"` via `env.ParseFlags()` CPPDEFINES extraction with `^[a-zA-Z0-9_-]+$` validation + missing-flag `env.Exit(1)` (FW-02 amended; ROADMAP SC#2 realized via Path B) | VERIFIED | name_firmware.py:33 `env.ParseFlags(flags)`; :34 iterates `CPPDEFINES`; :37 matches `RURP_BOARD_NAME`; :49 `re.match(r"^[a-zA-Z0-9_-]+$", v)`; :52 + :57 `env.Exit(1)` on validation / missing-flag failure |
| 4 | Four `ARDUINO_AVR_UNO` macro guards (CONTEXT D-01) widened atomically to `defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)`, inline disjunction at each site (D-02 — no umbrella macro) | VERIFIED | Single commit `ab7c2a9` ships all 4 widenings; grep counts: uno_rurp_shield.cpp=1 (line 8), rurp_common.cpp=2 (lines 10+23), rurp_register_utils.h=1 (line 63); total 4 sites verified by direct read; no `RURP_BOARD_UNO_FAMILY` or other umbrella macro introduced |
| 5 | `rurp_common.cpp` Pitfall 5 invariant: lines 25 (`#elif defined(ARDUINO_AVR_LEONARDO)`) and 28 (`#error "Unsupported board"`) preserved verbatim | VERIFIED | `grep -nE "^#elif defined\(ARDUINO_AVR_LEONARDO\)" rurp_common.cpp` → match at line 25; `grep -F '#error "Unsupported board"'` → match present; direct sed read of lines 20-32 confirms verbatim preservation |
| 6 | `pio test -e native` (test_dispatch + test_messages) stays green after changes (ROADMAP SC#5; FW-04) | VERIFIED | `pio test -e native -f "*test_dispatch*" -f "*test_messages*"` → both PASSED; 20 test cases / 20 succeeded in 4.01s |
| 7 | Built firmware's `.elf` contains the literal string `uno328pb` (ROADMAP SC#4; FW-03; CONTEXT D-13 — AVR ELFs lack .rodata so `avr-strings` is canonical) | VERIFIED | `avr-strings -a firestarter_uno328pb.elf \| grep -F uno328pb` returns `3.0.0b2:uno328pb` (the concatenated `FW_VERSION VERSION ":" RURP_BOARD_NAME` payload that flows to the handshake) |
| 8 | `firestarter_uno.hex` and `firestarter_leonardo.hex` from a post-rework `pio run` are byte-identical to Plan 21-01 baselines (GATE-1.5) | VERIFIED | `cmp -s` against both baselines exits 0; SHA-256 post-rework `0dd5c01a…` (uno) matches baseline; `f49e2a57…` (leonardo) matches baseline — both unchanged from Plan 21-01 capture |
| 9 | `firestarter/include/version.h` is unmodified during plan execution (Pitfall 3 — no `update_version.py` invocation; otherwise GATE-1.5 tears on `.rodata` version-string drift) | VERIFIED | `git -C firestarter diff --name-only include/version.h` returns empty; `version.h:11` still reads `#define VERSION "3.0.0b2"` verbatim |
| 10 | `.planning/REQUIREMENTS.md` FW-02 amended per CONTEXT D-05 + D-09 (Path B): no `boards/uno328pb.json` requirement remains; anchored on `RURP_BOARD_NAME` build_flag + `name_firmware.py` rework; decision-ID traceability via inline `D-05` + `D-09` tokens | VERIFIED | FW-02 body contains literal `RURP_BOARD_NAME`, `D-05`, `D-09`, `ATmega328PB`, `atmelavr`; `boards/uno328pb.json` token only appears in the explicit "no file is created" callout; FW-02 checkbox is `[x]` (closed) |

**Score:** 10/10 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `.planning/v1.5/baselines/firestarter_uno.hex` | Pre-rework GATE-1.5 baseline | VERIFIED | Present, 62617 B, SHA-256 `0dd5c01a…` (matches Plan 21-01 capture) |
| `.planning/v1.5/baselines/firestarter_leonardo.hex` | Pre-rework GATE-1.5 baseline | VERIFIED | Present, 68876 B, SHA-256 `f49e2a57…` (matches Plan 21-01 capture) |
| `.planning/v1.5/baselines/CAPTURE-PROCEDURE.md` | Reproducible capture recipe | VERIFIED | Present, 7700 B; contains `5fd751e` (7×), `RURP_BOARD_NAME` (3×), `update_version.py` (4×), `cmp -s` (7×) — all required strings |
| `.planning/REQUIREMENTS.md` (FW-02 amended) | Path B amendment per D-09 | VERIFIED | FW-02 body cites D-05 + D-09 + ATmega328PB + atmelavr + RURP_BOARD_NAME; `boards/uno328pb.json` only in the "no file is created" callout |
| `firestarter/platformio.ini` (`[env:uno328pb]`) | Path B env block | VERIFIED | Section header at line 40 between [env:uno]@31 and [env:leonardo]@57; `platform = atmelavr`, `board = ATmega328PB`, `framework = arduino`, build_flags carrying RURP_BOARD_NAME literal `uno328pb` + SERIAL_ON_IO |
| `firestarter/name_firmware.py` | RURP_BOARD_NAME-driven PROGNAME | VERIFIED | 62 lines; imports `re`; uses `env.ParseFlags` (line 33) → CPPDEFINES iteration (line 34) → quote-stripping (lines 42-46) → identifier regex validation (line 49) → `env.Exit(1)` (lines 52 + 57); leading comment block cites CONTEXT D-05/D-06/D-09 + Plan 21-02 |
| `firestarter/src/boards/uno_rurp_shield.cpp:8` | Widened guard | VERIFIED | `#if defined(ARDUINO_AVR_UNO) \|\| defined(ARDUINO_AVR_ATmega328PB)` — present at line 8 |
| `firestarter/src/boards/rurp_common.cpp:10` | Widened outer guard | VERIFIED | `#if defined(ARDUINO_AVR_UNO) \|\| defined(ARDUINO_AVR_ATmega328PB) \|\| defined(ARDUINO_AVR_LEONARDO)` — present at line 10 |
| `firestarter/src/boards/rurp_common.cpp:23` | Widened ADMUX guard | VERIFIED | `#if defined(ARDUINO_AVR_UNO) \|\| defined(ARDUINO_AVR_ATmega328PB)` — present at line 23; lines 25 + 28 preserved verbatim |
| `firestarter/include/rurp_register_utils.h:63` | Widened FM1608 guard | VERIFIED | `#if defined(ARDUINO_AVR_UNO) \|\| defined(ARDUINO_AVR_ATmega328PB)` — present at line 63 |
| `firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex` | Build output (FW-01) | VERIFIED | Present, 62854 B, SHA-256 `17439d0f…` (matches SUMMARY claim) |
| `firestarter/.pio/build/uno328pb/firestarter_uno328pb.elf` | Build output (FW-03 surface) | VERIFIED | Present, 48000 B; sections `.data` (0xca) + `.text` (0x567a); no `.rodata` (confirms SUMMARY's section-layout finding — AVR-correct) |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `[env:uno328pb] -D RURP_BOARD_NAME=\"uno328pb\"` | `name_firmware.py` PROGNAME | `env.ParseFlags()` CPPDEFINES | WIRED | PROGNAME-driven artifact present at `.pio/build/uno328pb/firestarter_uno328pb.hex` (62854 B) — only reachable if the parser extracted `uno328pb` correctly; conversely `firestarter_uno.hex` + `firestarter_leonardo.hex` byte-identical against baselines proves the parser also resolves `${this.board}` correctly for the existing two envs |
| `[env:uno328pb] -D RURP_BOARD_NAME=\"uno328pb\"` | `FW_VERSION` macro (firmware.h:16) | C preprocessor concatenation | WIRED | `avr-strings -a firestarter_uno328pb.elf \| grep -F uno328pb` → `3.0.0b2:uno328pb` — confirms the build_flag flowed through `FW_VERSION VERSION ":" RURP_BOARD_NAME` into the linked binary |
| Widened guards in `boards/uno_rurp_shield.cpp` + `rurp_common.cpp` + `rurp_register_utils.h` | `firestarter_uno328pb.hex` binary | atmelavr@5.2.0 supplies `-DARDUINO_AVR_ATmega328PB` via `boards/ATmega328PB.json` `build.extra_flags` | WIRED | Build SUCCESS for the new env; the four widened `#if` blocks compile their bodies into the artifact (size delta +86 B vs uno per SUMMARY); link is green |
| Post-rework `.pio/build/uno/firestarter_uno.hex` | `.planning/v1.5/baselines/firestarter_uno.hex` | `cmp -s` byte-identity | WIRED (GATE-1.5) | `cmp -s` exit 0; SHA-256 verbatim match against Plan 21-01 capture |
| Post-rework `.pio/build/leonardo/firestarter_leonardo.hex` | `.planning/v1.5/baselines/firestarter_leonardo.hex` | `cmp -s` byte-identity | WIRED (GATE-1.5) | `cmp -s` exit 0; SHA-256 verbatim match against Plan 21-01 capture |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `firestarter_uno328pb.hex` | Compiled object code from widened guard sites | Source files in `firestarter/src/boards/` + `firestarter/include/`; macro routing supplied at build time by atmelavr/ATmega328PB.json extra_flags | Yes — `.text` size 0x567a bytes; flash usage 69.0% (22340 B); the 86-byte delta vs uno is the MiniCore-bundled `pb-variant` runtime addition | FLOWING |
| `FW_VERSION` literal in `.data` section | `RURP_BOARD_NAME` build_flag value `uno328pb` | platformio.ini build_flags → preprocessor → `firestarter.h:16` `FW_VERSION VERSION ":" RURP_BOARD_NAME` → linker | Yes — `avr-strings` surfaces the concatenated literal `3.0.0b2:uno328pb` in the binary | FLOWING |
| `firestarter_uno.hex` PROGNAME | `${this.board}` → `uno` via SCons interpolation → CPPDEFINES `RURP_BOARD_NAME=uno` | platformio.ini `[env:uno]` `-D RURP_BOARD_NAME=\"${this.board}\"` → name_firmware.py parser | Yes — artifact filename byte-identical to baseline; PROGNAME resolves to `firestarter_uno` | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| FW-01 build green (3 envs) | `cd firestarter && pio run -t clean -e uno -e leonardo -e uno328pb && pio run -e uno -e leonardo -e uno328pb` | 3 SUCCESS in 3.68s; 0 warnings | PASS |
| FW-03 handshake literal in artifact | `avr-strings -a .pio/build/uno328pb/firestarter_uno328pb.elf \| grep -F uno328pb` | `3.0.0b2:uno328pb` | PASS |
| FW-04 native suite | `pio test -e native -f "*test_dispatch*" -f "*test_messages*"` | 20 / 20 cases PASSED in 4.01s | PASS |
| GATE-1.5 uno byte-identity | `cmp -s .pio/build/uno/firestarter_uno.hex .planning/v1.5/baselines/firestarter_uno.hex` | exit 0 | PASS |
| GATE-1.5 leonardo byte-identity | `cmp -s .pio/build/leonardo/firestarter_leonardo.hex .planning/v1.5/baselines/firestarter_leonardo.hex` | exit 0 | PASS |
| Pitfall 3 (version.h pristine) | `git -C firestarter diff --name-only include/version.h` | (empty) | PASS |
| Sub-repo working tree clean | `git -C firestarter status -s` | (empty) | PASS |
| Sub-repo commits present | `git -C firestarter log --oneline -3` | `ab7c2a9` + `da607d4` + `5fd751e` (base) | PASS |

### Probe Execution

No probes declared in PLAN/SUMMARY for this phase. The phase verification surface is build commands + `cmp -s` + native test runner + `avr-strings`, all of which are exercised in Behavioral Spot-Checks above. No `scripts/*/tests/probe-*.sh` exist in the firestarter sub-repo for this work area. N/A — no probes to execute.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| FW-01 | 21-02-PLAN | `pio run -e uno328pb` builds a flashable `.hex` from `beta`; no warnings vs `uno`/`leonardo` baseline | SATISFIED | Build 3-env SUCCESS in 3.68s; 0 warnings in build log; artifact `firestarter_uno328pb.hex` at 62854 B present |
| FW-02 | 21-01-PLAN (amendment) + 21-02-PLAN (implementation) | `[env:uno328pb]` with `platform = atmelavr` + `board = ATmega328PB` + `-D RURP_BOARD_NAME=\"uno328pb\"`; `name_firmware.py` derives PROGNAME from build_flag; board-id triple locked (amended Path B per D-05 + D-09; no boards/ JSON) | SATISFIED | Direct read of platformio.ini:40-55 confirms env block; name_firmware.py:33-57 confirms ParseFlags-based parser with validation gate; FW-02 amendment text in REQUIREMENTS.md confirms Path B locked |
| FW-03 | 21-02-PLAN | Firmware emits literal `uno328pb` in `<board>` slot of `OK: FW: <version>:<board>` handshake | SATISFIED | `avr-strings -a firestarter_uno328pb.elf \| grep -F uno328pb` → `3.0.0b2:uno328pb` confirms the literal byte sequence ships in the binary; the handshake emit path `fw_get_version()` at `hardware_operations.cpp:82-92` was not modified (read-only reference per CONTEXT) so the wire format flows through unchanged |
| FW-04 | 21-02-PLAN | `pio test -e native` (test_dispatch + test_messages) green | SATISFIED | 20 / 20 native test cases PASSED in 4.01s |

All 4 declared requirement IDs (FW-01, FW-02, FW-03, FW-04) verified. No orphaned requirements: REQUIREMENTS.md Traceability table maps exactly FW-01..FW-04 to Phase 21; all four are accounted for in the phase plans and all four are SATISFIED.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `firestarter/platformio.ini` | 75 | `; TODO(v1.5): root-cause the SIGABRT in Unity teardown and re-enable.` | Info | Pre-existing v1.4-carried debt for test_flash_intel_vpp + test_eeprom28c_chip_id Unity teardown SIGABRT; documented as carry-forward debt in v1.4 MILESTONES.md "Known Gaps"; NOT introduced by Phase 21 and explicitly out-of-scope (the suites are excluded from FW-04 via `test_filter` which only includes `test_dispatch` + `test_messages`). Not a blocker. |

No `TBD`, `FIXME`, or `XXX` debt markers in any Phase-21-modified file. The single `TODO(v1.5)` marker is pre-existing carry-forward debt (introduced in v1.4 Phase 17 WR-01) referencing the v1.5 milestone as the target for its resolution — that is, the marker is a formal follow-up reference and the phase under verification is the v1.5 cycle itself (root-causing it is out-of-scope for Phase 21, which is the firmware target plan; this debt belongs to a future v1.5 phase or a successor milestone). Per gate.md the marker has scope reference (v1.5) — not unreferenced — so no blocker.

### Human Verification Required

None. All Phase 21 success criteria are programmatically verifiable on the developer desk:

- FW-01: build command exit code
- FW-02: file content checks (platformio.ini env block + name_firmware.py parser) + REQUIREMENTS.md amendment grep
- FW-03: `avr-strings` grep against the .elf
- FW-04: `pio test -e native` exit code
- GATE-1.5: `cmp -s` against checked-in baselines

Phase 24 will provide bench-on-real-silicon verification (different phase scope; not a Phase 21 gap).

### Deviations from Original Plan (Documented in SUMMARY, Verified Acceptable)

Three deviations were documented in 21-02-SUMMARY.md and are accepted by this verification:

1. **FW-03 verification surface `.rodata` → `.data` via `avr-strings`** — Plan-author assumption that AVR ELFs have a `.rodata` section did not hold; AVR ELFs produced by avr-gcc place `const char*` literals in `.data` instead. CONTEXT D-13 explicitly lists `avr-strings` as a canonical alternative; the literal `uno328pb` IS present in the binary (`3.0.0b2:uno328pb` extracted), only the section header differs from the plan's mental model. The objdump section table (verified: `.data 0xca` + `.text 0x567a`; no `.rodata`) confirms this is standard AVR toolchain behavior, not a port-specific issue. ACCEPTED — verification surface adjustment, not an FW-03 gap.

2. **ELF filename `firmware.elf` → PROGNAME-derived `firestarter_uno328pb.elf`** — PIO renames both .hex AND .elf to PROGNAME (inherited behavior — uno + leonardo envs already emit firestarter_uno.elf / firestarter_leonardo.elf). All verification commands ran against the PROGNAME-derived path. ACCEPTED — trivial spec drift, not a behavior gap.

3. **`platform = MCUdude/MiniCore` → `platform = atmelavr`** — RESEARCH Open Question 1 disambiguation: `MCUdude/MiniCore` is not a registered PIO platform package; `atmelavr@5.2.0` bundles MiniCore via the built-in `boards/ATmega328PB.json` (`build.core = "MiniCore"`). The mirror-of-`[env:uno]` form was selected at execution time per RESEARCH Pitfall 6 + Open Q1 resolution. ACCEPTED — documented in REQUIREMENTS.md FW-02 amendment text + ROADMAP.md FW-01 closure note + SUMMARY decisions array; both planning artifacts reflect the as-built form.

### Cross-Phase Hand-Offs (Out-of-Scope for Phase 21 — Verified Intentional)

These items in the wider milestone were intentionally NOT touched by Phase 21 and are not gaps:

- **`[platformio] default_envs` stays `uno, leonardo`** (CONTEXT D-11): Phase 22 owns widening it to include `uno328pb`. Verified: line 16 of platformio.ini still reads `default_envs = uno, leonardo`.
- **ROADMAP Phase 22 SC#1 literal `default_envs = uno, leonardo, uno328pb`** (CONTEXT D-12): scope-correct hand-off; Phase 22 planner picks the final order (D-08 suggests `uno, uno328pb, leonardo` for section symmetry).
- **`firestarter_app/firestarter/firmware.py:417-423` avrdude profile** (CONTEXT D-10): Phase 23 INST-01 owns adding the `uno328pb` branch. Verified out-of-scope for Phase 21.

### Gaps Summary

**No gaps.** All 10 must-have truths VERIFIED, all 12 required artifacts present and substantive, all 5 key links wired with real data flowing, all 4 requirements (FW-01..FW-04) satisfied, all 8 behavioral spot-checks pass, no blocker anti-patterns, version.h pristine (Pitfall 3 honored), GATE-1.5 byte-identity confirmed on both existing envs via `cmp -s` exit 0 and SHA-256 match.

Phase 21 goal — "A clean `pio run -e uno328pb` build that emits `firestarter_uno328pb.hex` and a firmware that, when handshaken, reports its board as the literal string `uno328pb`. Native dispatch + messages tests green." — is achieved end-to-end. Ready to proceed to Phase 22 (Release Pipeline Artifacts).

---

_Verified: 2026-05-20T20:35:00Z_
_Verifier: Claude (gsd-verifier)_

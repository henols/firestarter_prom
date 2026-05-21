# Phase 21: Firmware Target — `uno328pb` - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-20
**Phase:** 21-firmware-target-uno328pb
**Areas discussed:** Board macro routing, [env:uno328pb] flags, boards/uno328pb.json scope (pivoted to Path B)
**Areas routed to planner/researcher (not discussed):** default_envs timing, Native-test FW-03 verification surface

---

## Gray Area Selection

| Option | Description | Selected |
|--------|-------------|----------|
| Board macro routing | `uno_rurp_shield.cpp` is `#ifdef ARDUINO_AVR_UNO`; MiniCore sets `ARDUINO_AVR_ATmega328PB` instead. How to bridge. | ✓ |
| boards/uno328pb.json scope | Inherit MiniCore stock or hand-author. | (discussed via "Next area") |
| default_envs timing | Phase 21 vs Phase 22 ownership of `[platformio] default_envs` widening. | |
| [env:uno328pb] flags | Mirror `[env:uno]` build_flags vs differ. | (discussed via "Next area") |
| Native-test FW-03 verification | Native test addition vs build-time .elf grep. | |

**User's choice:** Board macro routing (only). Subsequent "Next area" turns added [env:uno328pb] flags + boards/uno328pb.json scope.

---

## Board macro routing

### Q1: How should `firestarter/src/boards/uno_rurp_shield.cpp` reach the 328PB target?

| Option | Description | Selected |
|--------|-------------|----------|
| Widen the guard | Edit guard to `#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)`. Single source of truth; 328PB is a strict 328P superset for PORT/ADMUX. | ✓ |
| Force -D ARDUINO_AVR_UNO | Add the macro via env build_flags. Zero diff to board.cpp. Lies about identity; overlaps with MiniCore's own ATmega328PB definition. | |
| Third board file | Add `uno328pb_rurp_shield.cpp`. Explicit per-board; code duplication or include-trick drift. | |

**User's choice:** Widen the guard.
**Notes:** Selected the recommended option without comment.

### Q2: Widening scope — how many sites does Phase 21 extend?

| Option | Description | Selected |
|--------|-------------|----------|
| All 4 sites, atomically | Widen uno_rurp_shield.cpp:8 + rurp_common.cpp:10 + rurp_common.cpp:23 + rurp_register_utils.h:63 in a single commit. | ✓ |
| Bare minimum only | Only widen uno_rurp_shield.cpp:8. NOT viable: rurp_common.cpp:10 guards the entire ADC TU, would compile to `#error "Unsupported board"` at line 28. | |
| All 4 except FM1608 workaround | Widen 3 of 4; leave the FM1608 PORTD-bit-6 workaround Uno-only. Risk: silent non-application if 328PB exhibits the same bug. | |

**User's choice:** All 4 sites, atomically.
**Notes:** Confirms phase-level "no half-state in any commit" pattern.

### Q3: Guard style — umbrella macro or repeat inline?

| Option | Description | Selected |
|--------|-------------|----------|
| Repeat inline | `defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)` at each of 4 sites. Self-documenting; greppable; no new header dep. | ✓ |
| Umbrella macro in rurp_shield.h | `#define RURP_BOARD_UNO_FAMILY` then `#ifdef` at each site. Future-extensible; adds indirection. | |
| Per-site helper macro | Each site declares its own helper. Most explicit; most verbose. | |

**User's choice:** Repeat inline.
**Notes:** Operator agrees umbrella is premature abstraction for 4 sites.

### Q4: Native-test coverage for the widened guards?

| Option | Description | Selected |
|--------|-------------|----------|
| No new native tests | [env:native] uses `-D RURP_BOARD_NAME="native"`; the new macros are false there. Validating them in-test would force ArduinoFake to simulate AVR registers. | ✓ |
| Add one native compile-only test | static_assert / SFINAE harness simulating the env defines. Brittle; conditional-compilation surface. | |
| Defer to Phase 24 bench cycle | Real-silicon test proves the widening; synthetic native check adds no signal. | |

**User's choice:** No new native tests.
**Notes:** Aligns with "stay surgical" milestone guardrail; bench validation is the canonical proof point.

### Q5: GATE-1.5 verification — byte-identity proof under macro widening?

| Option | Description | Selected |
|--------|-------------|----------|
| diff against checked-in baseline | Capture pre-v1.5 hex from `firestarter/beta` tip `5fd751e`, commit to `.planning/v1.5/baselines/`, post-change `cmp -s` with version-region normalization. | ✓ |
| Phase 22 will catch it via CI | Defer to Phase 22's REL-01/02 byte-identity success criterion. Reverses failure-mode story; Phase 21 ships a regression that surfaces a phase later. | |
| Eyeball via `pio run` build report | Visual flash% + nm symbol-diff. % match doesn't prove byte-identity. | |

**User's choice:** diff against checked-in baseline.
**Notes:** Mirrors v1.4 lockstep-dryrun-fixture pattern.

### Continuation: More questions about Board macro routing, or move to next?

**User's choice:** Move to another gray area.
**Notes:** Switched to "[env:uno328pb] flags".

---

## [env:uno328pb] flags

### Q1: Which `[env:uno]` flags carry over verbatim?

| Option | Description | Selected |
|--------|-------------|----------|
| Mirror [env:uno] verbatim | `${env.build_flags}` + `-D RURP_BOARD_NAME=\"${this.board}\"` + `-D SERIAL_ON_IO`. DATA_BUFFER_SIZE inherited as 512 default. | ✓ |
| Mirror + explicit DATA_BUFFER_SIZE=512 | Add `-D DATA_BUFFER_SIZE=512` explicitly. 0 functional difference. | |
| Mirror minus SERIAL_ON_IO | 328PB exposes USART1 — but we out-of-scoped that. Without SERIAL_ON_IO behavior diverges with no upside. | |

**User's choice:** Mirror [env:uno] verbatim.
**Notes:** Verified `DATA_BUFFER_SIZE 512` is the firestarter.h default — so "inherited" is byte-correct.

### Q2: Placement of `[env:uno328pb]` in `platformio.ini`?

| Option | Description | Selected |
|--------|-------------|----------|
| After [env:leonardo], before [env:native] | Recommended by Claude — matches a `default_envs = uno, leonardo, uno328pb` reading order. | |
| Before [env:leonardo] | Groups 328-family AVR envs visually adjacent. Implies a Phase 22 `default_envs = uno, uno328pb, leonardo` realignment. | ✓ |
| After [env:native] | Zero diff to existing lines (contiguous at EOF). Breaks AVR-then-native grouping. | |

**User's choice:** Before [env:leonardo].
**Notes:** Operator-overridden recommendation. Signals MCU-family grouping over chronological-add ordering. Captured as D-12 hand-off for Phase 22 ROADMAP touch-up.

### Q3: Does `${this.board}` interpolate when `board` is a custom file in `boards/`?

| Option | Description | Selected |
|--------|-------------|----------|
| Trust ${this.board} | Mirror [env:uno] pattern. PIO resolves the env's `board` setting regardless of custom-vs-built-in. | ✓ |
| Hard-code the literal | Defensively explicit; duplicates the literal across `board =` and `-D RURP_BOARD_NAME`. | |
| Both + CI assertion | Static-assert / build-time grep. Belongs in Phase 22 CI gate if anywhere. | |

**User's choice:** Trust ${this.board}.
**Notes:** Question premise was later invalidated by Path B (the `boards/` file gets dropped; `${this.board}` would resolve to `ATmega328PB`, not `uno328pb`). D-07 ended up hard-coding the literal — superseded by Path B pivot.

### Continuation: More questions, or move on?

**User's choice:** Next area.
**Notes:** Switched to "boards/uno328pb.json scope".

---

## boards/uno328pb.json scope

### Q1: Inherit from MiniCore's stock variant or hand-author standalone?

| Option | Description | Selected |
|--------|-------------|----------|
| Hand-author full JSON | Full custom JSON: mcu, f_cpu, core, variant, upload protocol/speed, etc. | |
| Minimal JSON + extends | `extends = "ATmega328PB"`; override only artifact-name handle and variant. | |
| Defer JSON content to plan-phase | Lock path + literal in CONTEXT; route internals to researcher/planner. | |

**User's choice (freeform):** "Isent there a predefined json for the atmega328pb that we can use"
**Notes:** Operator question. Triggered investigation of MiniCore's built-in `ATmega328PB` board JSON. Realization: a custom JSON exists only to drive `name_firmware.py`'s artifact-name derivation. The follow-up question reframed the decision.

### Q2 (reframed): Path A (custom JSON ~5 lines) or Path B (drop JSON + rework name_firmware.py)?

| Option | Description | Selected |
|--------|-------------|----------|
| Path A — keep custom JSON | 5-line `{"extends":"ATmega328PB","name":"uno328pb"}`. Zero touch to shared scripts. GATE-1.5 preserved by construction. FW-02 unchanged. | |
| Path B — drop JSON, rework name_firmware.py | Use `board = ATmega328PB`. PROGNAME derives from RURP_BOARD_NAME flag instead of `board` setting. Amends FW-02. Affects shared script. | ✓ |
| Path A but explicit field-by-field | Hand-author full custom JSON. More lines; drift risk vs. MiniCore upstream. | |

**User's choice:** Path B — drop JSON, rework name_firmware.py.
**Notes:** Significant decision — amends REQUIREMENTS.md FW-02. Collapses two requirements (custom JSON + per-env board entry) into one (per-env -D RURP_BOARD_NAME flag) with a single source of truth. Captured as D-05 + D-09.

### Q3 (Path B follow-up): What's the PROGNAME source?

| Option | Description | Selected |
|--------|-------------|----------|
| Parse RURP_BOARD_NAME from BUILD_FLAGS | Single source of truth: artifact name AND handshake string both derive from the same -D flag. Can't drift. | ✓ |
| Per-env `custom_prog_name` PIO option | Declare `custom_prog_name = uno328pb` in [env:uno328pb] + the existing two envs. Explicit per-env; expands touched-files surface. | |
| New -D RURP_ARTIFACT_NAME flag | Parallel flag. Reintroduces drift risk between handshake-name and artifact-name. | |

**User's choice:** Parse RURP_BOARD_NAME from BUILD_FLAGS.
**Notes:** Cleanest source-of-truth shape. Captured as D-06.

### Q4 (Path B follow-up): GATE-1.5 byte-identity proof rigor?

| Option | Description | Selected |
|--------|-------------|----------|
| Baseline-diff + checked-in hex | Commit pre-v1.5 hex to `.planning/v1.5/baselines/`, `cmp -s` post-change. | ✓ |
| Symbol-table grep + flash-% match | Lighter than checked-in hex; weaker evidence. | |
| Run existing Phase-22 release pipeline locally | Tests full pipeline; overlaps with Phase 22 scope. | |

**User's choice:** Baseline-diff + checked-in hex.
**Notes:** Mirrors v1.4 lockstep-dryrun-fixture precedent. Captured as D-04.

### Q5 (Path B follow-up): What does `[env:uno328pb]` look like under Path B?

| Option | Description | Selected |
|--------|-------------|----------|
| MiniCore stock board, mirror [env:uno] flags | `board = ATmega328PB`; build_flags = ${env.build_flags} + -D RURP_BOARD_NAME=\"uno328pb\" + -D SERIAL_ON_IO. | ✓ |
| Above + explicit board_build.variant | Defensive against MiniCore upstream default changes. PIO syntax not idiomatic. | |
| Above + explicit upload_protocol/baud | Locks bench-flash surface. Overlaps with Phase 23/24. | |

**User's choice:** MiniCore stock board, mirror [env:uno] flags.
**Notes:** Captured as D-07. Reaffirms "stay surgical" milestone guardrail.

### Continuation: Wrap up or more?

**User's choice:** Wrap up — ready for CONTEXT.md.
**Notes:** Remaining areas (default_envs timing, Native-test FW-03 verification) routed to planner/researcher hand-off notes in CONTEXT (D-11, D-13).

---

## Claude's Discretion

- Exact `update_version.py` byte-offset normalization region in the GATE-1.5 `cmp` check — research surface for planner.
- Parsing form for `-D RURP_BOARD_NAME` in `name_firmware.py` (regex vs shlex vs PIO ParseFlags) — planner picks based on PIO's `env['BUILD_FLAGS']` exposure at script time.
- Whether to commit baseline `.hex` files via Git LFS or plain blobs — likely plain (small artifacts, meta-repo otherwise text-only).

## Deferred Ideas

- Per-env `custom_prog_name` PIO option as PROGNAME source fallback if Path B's RURP_BOARD_NAME parser proves brittle.
- Umbrella macro `RURP_BOARD_UNO_FAMILY` — premature abstraction for 4 sites; reconsider in v1.6+.
- Static-assert / .elf-grep CI step for the handshake string literal — deferred from D-13.
- `board_build.variant`, `upload_protocol`, `upload_speed` explicit overrides — Phase 24 (bench) is the venue.
- MiniCore version pinning (`platform = MCUdude/MiniCore@^3.0.0`) — Phase 22 may want it once CI cuts confirm a stable version.
- 328PB extra peripherals (USART1, TWI1, SPI1, Timer3/4, PE0–PE3) — locked out-of-scope at milestone level.
- Resume v1.3 BENCH-01..06 on the 328PB-Uno — locked deferred at milestone level.

## Cross-phase Hand-offs (captured in CONTEXT.md)

- D-10 → Phase 23: Host CLI avrdude profile entry for `uno328pb` ([firestarter_app/firestarter/firmware.py:417-423](firestarter_app/firestarter/firmware.py#L417-L423)).
- D-11 → Phase 22: `default_envs` widening to include `uno328pb`.
- D-12 → Phase 22 ROADMAP touch-up: realign Phase 22 SC#1's `default_envs` literal with this phase's `.ini` section order (`uno, uno328pb, leonardo`).
- D-13 → planner: FW-03 verification surface is build-time `.elf` symbol grep, not a new native test.
- D-09 → planner: REQUIREMENTS.md FW-02 amendment (drop `boards/uno328pb.json` requirement; reframe around `name_firmware.py` rework + `RURP_BOARD_NAME` triple).

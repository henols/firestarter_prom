# Stack Research

**Domain:** Firmware write/program/verify algorithm validation — reusable test harness + chip-family validation matrix, hybrid native (no-hardware) + hardware-in-the-loop (HIL) bench
**Researched:** 2026-06-16
**Confidence:** HIGH

## Headline Finding (read this first)

**v1.13 needs almost no new third-party dependencies.** The two test stacks
this milestone builds on are already installed, version-current, and proven in
this repo:

- **Firmware native side:** PlatformIO `[env:native]` + Unity + ArduinoFake
  `@^0.4.0` — 8 native suites already green (`test_dispatch`, `test_not_implemented`,
  `test_flash_intel_vpp`, `test_eeprom28c_chip_id`, `test_read_timing`, COBS suites,
  `test_messages`). The reuse pattern (`test/native/avr/<name>/` + per-suite
  `host_stubs.cpp` + `avr/pgmspace.h` shim) is documented in `firestarter/CLAUDE.md`.
- **Host side:** pytest `>=8.0` + syrupy `>=5.0` (snapshot) + ruff `>=0.15.14`
  + mypy `>=2.1.0` + pytest-cov `>=7.1.0` + pyserial `>=3.5`, all wired into
  `.github/workflows/ci.yml` and `pre-commit`. The `conftest.py` `make_comm` /
  `fake_serial` fixtures already let host tests drive the full INIT→MAIN→END
  state machine **without a serial port**.

So the genuinely-new work is **patterns + a thin harness layer + a golden-data
convention + a couple of small dev tools**, not a new framework. This document
names the few additions, and is explicit about the much larger "reuse, do not
re-add" set. The native-vs-bench split is called out on every row.

The single most important new piece is a **chip-family validation matrix**
(a declarative data file mapping the 6 algorithm families → representative
chips → which assertions run native vs which require a bench) plus a **harness
that consumes it**. That harness is mostly glue over the two existing stacks.

## Recommended Stack

### Core Technologies (all ALREADY PRESENT — reuse, do not re-add)

| Technology | Version (pinned) | Purpose | Why Recommended | Native / Bench |
|------------|------------------|---------|-----------------|----------------|
| PlatformIO Unit Testing (`[env:native]`, `platform=native`) | PIO core 6.1.x | Cross-compile `src/proms/*.cpp` on host; run Unity suites with no AVR board | Already the firmware test substrate; `test_build_src=yes` + `build_src_filter=+<proms/>` links the real handler TUs into a host binary | **Native** |
| Unity (`test_framework = unity`) | bundled w/ PIO | C test assertions / `RUN_TEST` registration | Standard PIO C test framework; every existing firmware suite uses it | **Native** |
| ArduinoFake | `fabiobatsilva/ArduinoFake@^0.4.0` | Mock `Serial`, `delay`, `delayMicroseconds`, `digitalWrite` etc. so handlers link + run on host | Already pinned; current (tutorials still cite 0.3.1). FakeIt-based `When(Method(...))` mocking is the established pattern in `test_flash_intel_vpp` | **Native** |
| pytest | `>=8.0` (`[test]` extra) | Host CLI + DB + serial-protocol unit/integration tests | First-class in this repo (40+ test modules); `conftest.py` fixtures bypass real serial I/O | Native (host) |
| syrupy | `>=5.0` | Snapshot assertions (`.ambr`) for stable text/JSON outputs | Already used for `info`/characterization golden snapshots; ideal for pinning per-family expected wire dicts + CLI output | Native (host) |
| pyserial | `>=3.5` | Real serial transport to the board | The only path to actual hardware; used by `serial_comm.py` | **Bench** |
| ruff + mypy | `>=0.15.14` / `>=2.1.0` | Lint/format + type gate (strict on 8 modules; watermark on rest) | CI gate already enforced; any new host harness module must pass it | Native (host) |

### Supporting Libraries / Tools (mix of present + NEW-but-tiny)

| Item | Version | Purpose | When to Use | Status |
|------|---------|---------|-------------|--------|
| `jq` | system (already a script dependency) | Pull `size_bytes` / `chip_id_check` / type out of `chip_database.json` in bench shell scripts | Already used by `firestarter_test.sh` / `write_test.sh`; reuse for matrix-driven bench runs | REUSE |
| `dd` / `tr` / `diff -y` / `xxd` | coreutils | Generate test images (random, all-0x00, all-0xFF, split) + byte-compare read-back | Already the `write_test.sh` pattern; the canonical HIL write→verify→read-back→diff loop | REUSE |
| Validation-matrix data file (NEW) | n/a — `.json` or `.toml` in-repo | Declarative map: family → algorithm IDs → representative chip(s) → assertion set → `native`/`bench` tier | The spine of the milestone; consumed by both a native generator and a bench runner | **NEW (data)** |
| Golden wire-vector catalog (NEW) | n/a — `.json` in-repo | Per-family expected JSON command dict (algorithm, vpp_mv, pulse-delay, flags, bus-config) for a fixed chip+image | Pins host-side command-building correctness without a board; syrupy or plain JSON fixtures | **NEW (data)** |
| Golden binary images (NEW, small) | n/a — `.bin` fixtures | Deterministic test patterns (0x00, 0xFF, walking-1s, address-as-data, random-seeded) | Replaces ad-hoc `dd if=/dev/urandom` so native + bench compare against the *same* bytes; seed-pinned for reproducibility | **NEW (data)** |
| `pytest` marker `@pytest.mark.hardware` (NEW marker, existing tool) | pytest config | Tag bench-only host tests so CI auto-skips them (`-m "not hardware"`) and operators opt in (`-m hardware`) | Formalizes the existing informal split (`test_hardware.py` already hand-documents a safety boundary) | **NEW (config)** |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `pio test -e native -f "*test_<family>*"` | Run one family's native suite | Existing invocation; add one suite dir per family under `test/native/avr/` |
| `pytest -m "not hardware"` / `-m hardware` | Split CI (autonomous) from bench (operator) host tests | Requires registering the `hardware` marker in `[tool.pytest.ini_options].markers` to avoid `PytestUnknownMarkWarning` |
| `check_dispatch.py` / `diff_db.py` | Existing DB gates | Reuse as-is; the matrix should reference the same `chip_database.json` they validate, so the matrix can't drift from the shipped DB |
| New bench-runner script (thin) | Drive matrix → `firestarter write/verify/read` per bench-tier chip, log structured results | Generalization of `firestarter_test.sh` + `write_test.sh`; matrix-driven instead of single `$EPROM` arg |

## Installation

**Nothing new to `pip install` or add to `lib_deps`.** The stack is already
declared:

```bash
# Host (firestarter_app/) — already in pyproject.toml [test]/[dev] extras
pip install -e '.[test]'      # pytest>=8, syrupy>=5, pytest-cov>=7.1, ruff, mypy, pyserial

# Firmware (firestarter/) — already in platformio.ini [env:native]
pio test -e native            # PlatformIO pulls fabiobatsilva/ArduinoFake@^0.4.0
```

The only repo changes are **data files + thin scripts + one pytest marker
registration** — no dependency-graph changes, no CI runner changes beyond an
added `-m "not hardware"` filter.

## Reuse vs New — explicit ledger (the core deliverable of this research)

### REUSE (present today — do NOT re-research, do NOT replace)

- **Native dispatch test pattern** — `test/native/avr/test_dispatch/` builds a
  minimal `firestarter_handle_t`, calls `configure_memory()`, asserts on
  `response_code` + `firestarter_operation_main` (NOT register side effects).
  This is the model for **algorithm-shape** native tests.
- **Native safety/behavioral test pattern** — `test_flash_intel_vpp/` and
  `test_eeprom28c_chip_id/` go further: per-suite `host_stubs.cpp` exposes
  `set_mock_vpp_mv()` / `set_mock_hw_rev()` setters and a mock `set_control_register`
  that *records* writes, so tests assert "VPP/P1 driven low on the unsafe path."
  This is the model for **write/program correctness + VPP-safety** native tests
  — the handlers' control-register sequencing is fully testable on host.
- **Host state-machine test pattern** — `conftest.py` `make_comm()` + `fake_serial`
  feed wire frames and drive `serial_comm.py` INIT→MAIN→END with no port. This is
  the model for **host-side write/verify orchestration** tests.
- **HIL integration scripts** — `firestarter_test.sh` (full info/firmware/eprom
  sweep) and `write_test.sh` (write→verify→read-back→`diff -y`). These ARE the
  bench harness today; v1.13 generalizes them to be matrix-driven, not rewrites them.
- **DB correctness gates** — `check_dispatch.py` (VPP-safety, structural +
  type-keyed), `diff_db.py` (per-chip diff vs baseline). The matrix consumes the
  same `chip_database.json` these guard.
- **Codegen drift-gate pattern** — v1.2/v1.10 `messages.toml` → both repos with
  `<regen> && git diff --exit-code`. If golden wire-vectors are codegenerated,
  reuse this exact drift-gate shape.

### NEW (genuinely needed, all thin)

1. **Validation-matrix data file** (`.json`/`.toml`, lives in `firestarter_app/`
   alongside the DB it references; mirror or symlink into firmware test tree if
   the native generator needs it). Rows: `{family, algorithm_ids[], rep_chip,
   image_set[], assertions[], tier: native|bench, blocked_reason?}`.
2. **Per-family native Unity suites** — one new dir per family under
   `test/native/avr/test_<family>_program/` (e.g. `test_eprom_program`,
   `test_flash3_program`, `test_eeprom28c_program`). Asserts pulse-delay defaults,
   retry/mismatch-mask logic (`eprom_write_execute`), SDP sequence (`eeprom_28c`),
   sector/chip-erase command words (`flash_type_3`) — all via recording mocks.
3. **Golden wire-vector fixtures** — expected host→fw JSON command per family
   for a pinned chip+image; assert in pytest (syrupy or plain JSON).
4. **Golden binary image set** — small, deterministic, seed-pinned `.bin` patterns
   shared by native expectation generation and bench `diff`.
5. **Matrix-driven bench runner** — thin generalization of `write_test.sh`:
   iterate the matrix's `tier: bench` rows for chips on hand, run write→verify→
   read-back→diff, emit a structured results table (which family PASS/FAIL/SKIP-no-part).
6. **`hardware` pytest marker** registration + a `not hardware` default in CI.

## Native-testable vs Bench-only (the load-bearing split)

| Concern | Native (no hardware) | Bench (HIL) |
|---------|----------------------|-------------|
| Dispatch routing (algorithm → handler) | ✅ `configure_memory` asserts (existing) | — |
| Pulse-delay defaults per protocol (0x07=1ms, 0x08=100µs, 0x0B=500µs) | ✅ read `handle->pulse_delay` after `configure_eprom` | — |
| Write retry / mismatch-bitmask logic (`eprom_write_execute`) | ✅ recording mock `get_data` returns scripted mismatches; assert retry count + escalating delay | confirm convergence on real silicon |
| VPP-safety sequencing (regulator/P1 low on error path) | ✅ recording `set_control_register` (existing flash_intel pattern) | confirm actual voltage with operator multimeter |
| EEPROM SDP-disable 6-write magic sequence | ✅ assert `set_data` address/value order | confirm chip actually unlocks |
| Flash AMD unlock + sector/chip erase command words | ✅ assert `set_data` command sequence | confirm erase completes |
| Host command-dict correctness (algorithm/vpp_mv/flags/bus-config) | ✅ golden wire-vector (host pytest) | — |
| Host INIT→MAIN→END orchestration + chunking | ✅ `make_comm`/`fake_serial` frames | confirm against real ack timing |
| **Actual data integrity** (write→read-back byte-identical) | ❌ impossible | ✅ `write_test.sh`-style `diff -y` |
| Real VPP voltage / brownout / chip-ID read | ❌ | ✅ Leonardo verify board only |
| adapter-required chip pin remap | ❌ | ✅ requires the physical adapter |

**Rule for the matrix:** every assertion that does NOT require observing real
silicon or real voltage goes `native`; everything that does goes `bench`.
Native rows run in CI with no gate; bench rows gate only on chip+shield
availability (hybrid gating per milestone context).

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Unity + ArduinoFake (existing) | GoogleTest / Catch2 for the C++ handlers | Only if abandoning PIO's `[env:native]` — not worth it; ArduinoFake's FakeIt mocking already covers `delay`/`Serial`/register stubs and is proven here |
| Recording-mock `set_control_register` for VPP-safety native tests | Renode / QEMU / simavr full-MCU emulation | If you needed cycle-accurate AVR + analog VPP simulation — massive overkill; the handlers are pure logic over a register abstraction that mocks cover |
| `@pytest.mark.hardware` + `-m` filter | A separate pytest *suite/dir* for bench tests | If bench tests grow large enough to warrant their own `tests/bench/` tree; a marker is lighter and keeps fixtures shared |
| Declarative matrix data file | Parametrized-pytest-only (no shared data) | If the matrix were host-only; but firmware native suites also need the family→chip map, so a shared data file avoids duplicating it in two languages |
| Golden `.bin` patterns (seed-pinned) | `dd if=/dev/urandom` per run (current `write_test.sh`) | Fine for a smoke read-back, but non-reproducible — a failing byte can't be re-run deterministically. Keep one random case, add pinned patterns |
| syrupy snapshots for wire-vectors | Hand-written `assert cmd == {...}` | Both fine; prefer plain-dict asserts for the *safety-critical* fields (vpp_mv, algorithm, flags) so a snapshot-update can't silently bless a regression |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| A full MCU emulator (Renode/QEMU/simavr) for "hardware-in-the-loop without hardware" | The whole point of bench rows is real silicon + real VPP; emulating the AVR proves nothing about the chip-under-test and adds a heavy, drifting dependency | Native logic tests (mocks) for algorithm shape; real bench for integrity/voltage |
| `pytest-embedded` / external HIL frameworks | Adds a heavyweight dependency for what `firestarter_test.sh` + `pyserial` already do; the project's bench flow is intentionally a shell+CLI loop the operator can read | Generalize the existing shell scripts; drive the `firestarter` CLI |
| `hypothesis` property testing (for now) | Tempting for write-pattern fuzzing, but bench time is the scarce resource and native handler logic is deterministic; not worth the new dep this milestone | Seed-pinned golden patterns; revisit only if a fuzz need emerges |
| Re-running `dd if=/dev/urandom` as the *only* image source | Non-reproducible failures; a flaky byte can't be deterministically replayed | Seed-pinned golden `.bin` set (+ keep one random case for breadth) |
| Snapshotting safety-critical wire fields with auto-update enabled | `pytest --snapshot-update` could silently re-bless a wrong `vpp_mv`/`flags`, defeating the safety check | Explicit `assert` on vpp_mv/algorithm/flags; snapshots only for cosmetic/text output |
| New native `[env:native]` config edits per suite beyond the allowlist | `firestarter/CLAUDE.md` says dropping `test_*.cpp` under `test/native/avr/<dir>/` needs no platformio.ini change — but the `test_filter` uses a **positive allowlist** + per-dir `-I` includes, so a new suite dir must be added there or it silently won't run | Add the new suite dir to the `test_filter` allowlist + an `-I` include line (the one config touch required) |

## Stack Patterns by Variant

**If the assertion can be made by observing handler logic / register writes / host command dicts:**
- Use a **native** test (Unity+ArduinoFake recording mock, or pytest+fake_serial).
- Because it runs in CI with zero hardware gate and gives deterministic, fast feedback — the milestone's "software-first" mandate.

**If the assertion requires real bytes on real silicon or a measured voltage:**
- Use a **bench** row driven by the matrix runner against Leonardo (the trusted verify board).
- Because data-integrity and VPP behavior are physically unobservable on host; per memory, avoid uno328pb (program-brownout) and Rev-0/2.0 (read faults).

**If a family's representative chip / adapter is not on hand:**
- Mark the matrix row `tier: bench, blocked_reason: "no part"` and let the runner emit SKIP.
- Because hybrid gating allows closing the milestone without 100% family bench coverage.

**If a golden wire-vector or message changes the firmware↔host contract:**
- Wire it through the existing codegen drift-gate (`<regen> && git diff --exit-code`) in both repos.
- Because lockstep is a hard project invariant (constants.py ↔ firestarter.h, messages.toml).

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| pytest `>=8.0` | syrupy `>=5.0`, pytest-cov `>=7.1.0` | Already co-installed and green in CI; no change |
| ArduinoFake `^0.4.0` | PIO `platform=native`, Unity | Already pinned; `-std=gnu++17` set in `[env:native]` build_flags |
| ruff `>=0.15.14` / mypy `>=2.1.0` (cfg `python_version=3.9`) | Devcontainer Python 3.12 | ⚠ Known trap (memory `reference_devcontainer_py312_masks_ci_py39`): validate `ruff check` + `ruff format --check` against the **py39** target before claiming CI green; new harness modules must be ruff-clean and respect the mypy watermark (`tools/check_mypy_watermark.py`) |
| `chip_database.json` (744 chips, `support_status` taxonomy) | matrix data file | Matrix must reference only `support_status: supported` chips for bench write/program rows; `adapter-required` rows stay bench-blocked until the adapter exists |
| Coverage floor `--cov-fail-under=70` | new host harness modules | Memory notes near-zero headroom historically; adding host harness code without tests can trip the floor — land tests in the same change |

## Integration Points (where the new pieces live)

- **Firmware native suites:** `firestarter/test/native/avr/test_<family>_program/`
  (one per family) + `host_stubs.cpp` (extend only if a new `rurp_*` symbol is
  referenced) + add dir to `[env:native]` `test_filter` + `-I` lines in `platformio.ini`.
- **Host tests:** `firestarter_app/tests/test_<family>_program.py`; golden fixtures
  under `firestarter_app/tests/golden/` (existing dir) or a new `tests/golden/wire/`.
- **Matrix + images:** `firestarter_app/` (next to the DB) so `jq`-driven shell
  scripts and pytest both read it; deterministic `.bin` fixtures under
  `tests/golden/images/`.
- **Bench runner:** alongside `firestarter_test.sh` / `write_test.sh` in
  `firestarter_app/` (matrix-driven generalization).
- **CI:** `firestarter_app/.github/workflows/ci.yml` runs `pytest -m "not hardware"`;
  register the `hardware` marker in `pyproject.toml [tool.pytest.ini_options].markers`.

## Sources

- `firestarter/CLAUDE.md` — native test reuse pattern, `[env:native]` config, handler/protocol table (HIGH — repo canonical)
- `firestarter/platformio.ini` — `[env:native]` `test_filter`, ArduinoFake `^0.4.0`, build_src_filter (HIGH)
- `firestarter/test/native/avr/test_dispatch|test_flash_intel_vpp` — recording-mock + setter patterns (HIGH)
- `firestarter/src/proms/{memory,eprom,flash_type_3,eeprom_28c}.cpp` — algorithm shapes confirming what is host-observable (HIGH)
- `firestarter_app/pyproject.toml` — pinned pytest>=8, syrupy>=5, ruff>=0.15.14, mypy>=2.1.0, pytest-cov>=7.1.0, pyserial>=3.5 (HIGH)
- `firestarter_app/tests/conftest.py` — `make_comm`/`fake_serial` no-port state-machine fixtures (HIGH)
- `firestarter_app/{firestarter_test.sh,write_test.sh}` — existing HIL write→verify→read-back→diff loop (HIGH)
- PlatformIO Unit Testing docs + ArduinoFake registry — confirmed `^0.4.0` is current vs tutorial-cited 0.3.1 (MEDIUM — version current)
- Project memory: `reference_devcontainer_py312_masks_ci_py39`, `feedback_chip_out_before_sideload`, `feedback_verify_port_identity_each_task`, `project_uno328pb_vpp_recal_and_program_brownout` (HIGH — operator-confirmed bench constraints)

---
*Stack research for: firmware write/program/verify validation harness + matrix (hybrid native/HIL)*
*Researched: 2026-06-16*

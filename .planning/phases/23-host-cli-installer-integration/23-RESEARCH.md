# Phase 23: Host CLI Installer Integration - Research

**Researched:** 2026-05-21
**Domain:** Python host-CLI installer (`firestarter_app/firestarter/`) — adding a 3rd-board (`uno328pb`) AVR-flashing branch + 4 mocked pytest cases
**Confidence:** HIGH (entire surface verified against `v1.5-uno328pb` working-tree HEAD; test invocation green; mock pattern is the established `monkeypatch.setattr(firmware.requests, "get", ...)` shape from v1.4 Phase 18)

## Summary

Phase 23 is a **mocked-only, host-side, narrow extension** of the v1.4 INST-04 substrate. The entire phase is a 1-elif-branch insertion in `firestarter_app/firestarter/firmware.py:_install_with_avrdude` (live working tree line range **417-423**, exactly matching CONTEXT D-01's prediction) plus 4 new pytest methods in `firestarter_app/tests/test_firmware_install.py`. No new files, no protocol changes, no firmware sub-repo edits.

The v1.4 Phase 18 work already shipped board-driven release-resolution (`fetch_release_info(board=...)`, `list_releases(board=...)`, `fetch_latest_release_info(board=...)`). The handshake parser at `firmware.py:101-117` already extracts `board_name` from `"FW: <version>:<board>"` generically — Phase 21's firmware emits `"uno328pb"` and the host already routes it correctly to `_install_with_avrdude(board="uno328pb")`. The ONLY missing piece is the AVR profile mapping `uno328pb → (atmega328pb, arduino, 115200)`.

The avrdude-profile resolution test (D-06) is the most valuable single test because **no existing test mocks `Avrdude(...)`** — this phase introduces a new mock target via `monkeypatch.setattr(firmware, "Avrdude", FakeAvrdude)`. The mock pattern for `firmware.requests.get` is already proven across 17 tests in `TestFirmwareInstallStable / PreRelease / Pinned / List`.

**Primary recommendation:** Two-wave TDD shape — Wave 1 lands 4 new RED tests in `test_firmware_install.py` (3 release-resolution + 1 avrdude-profile); Wave 2 lands the elif branch in `_install_with_avrdude` (Wave 1 turns GREEN). Single sub-repo commit per wave; meta-repo carries CONTEXT/RESEARCH/VALIDATION/PLAN/SUMMARY/VERIFICATION/ROADMAP/STATE on the matching `v1.5-uno328pb` branch.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Avrdude profile for uno328pb (the load-bearing edit):**
- **D-01:** Add a `uno328pb` branch to `firestarter_app/firestarter/firmware.py:_install_with_avrdude` (currently lines 405-423). The branch sits as `elif board.lower() == "uno328pb":` between the existing `if board.lower() == "leonardo":` and the implicit `uno` default. Set `partno, programmer_id, baud_rate = ("atmega328pb", "arduino", 115200)`.
- **D-02:** Programmer_id = `"arduino"`, NOT `"urclock"`. Mirrors uno profile. If Phase 24 bench validation reveals the operator's specific 328PB-Uno needs `urclock`, that's a 1-line follow-up.
- **D-03:** `partno = "atmega328pb"` exactly. The 328PB signature `0x1E 0x95 0x16` differs from 328P's `0x1E 0x95 0x0F`, so `atmega328p` would abort.
- **D-04:** `baud_rate = 115200`. Same as `uno`.

**Test surface:**
- **D-05:** Extend `firestarter_app/tests/test_firmware_install.py` with `uno328pb` cases (3 release-resolution tests). Use existing `mock_releases_factory` helper + `monkeypatch.setattr(firmware.requests, "get", ...)` pattern.
- **D-06:** Add ONE avrdude profile resolution test that mocks `Avrdude(...)` and asserts the elif branch passes `partno="atmega328pb"`, `programmer_id="arduino"`, `baud_rate=115200` to the constructor.
- **D-07:** Do NOT touch existing `uno`/`leonardo` test cases. GATE-01 non-regression enforced by full-suite-green before+after.

**What does NOT need to change (negative scope):**
- **D-08:** `constants.py` requires NO edits. (Verified — no board enum or allowlist exists.)
- **D-09:** `avr_tool.py` requires NO edits. (Verified — thin avrdude subprocess wrapper.)
- **D-10:** `main.py` requires NO edits. (See ⚠ Open Q1 below — code reality has a partial deviation around `--board` choices that the planner must resolve.)
- **D-11:** `serial_comm.py` requires NO edits. Handshake parser is board-string-generic.
- **D-12:** NO firmware sub-repo edits. Phase 23 is HOST-ONLY.
- **D-13:** NO meta-repo edits beyond CONTEXT/RESEARCH/VALIDATION/PLAN/SUMMARY/VERIFICATION/ROADMAP/STATE.

**Verification scope:**
- **D-14:** Full pytest suite green: `cd firestarter_app && python -m pytest tests/ -v` exits 0 with N+M cases passing.
- **D-15:** NO hardware flash in Phase 23. Real-silicon flash deferred to Phase 24 (BENCH-01).
- **D-16:** GATE-01 non-regression command — `cd firestarter_app && python -m pytest tests/test_firmware_install.py -v -k "not uno328pb"` exits 0 with the same case count as pre-Phase-23.

**Edit surface:**
- **D-17:** Exactly 2 files in the host CLI sub-repo: `firestarter_app/firestarter/firmware.py` (1 elif branch) + `firestarter_app/tests/test_firmware_install.py` (4 new test methods).
- **D-18:** NO `setup.py`, `pyproject.toml`, README, or doc edits.

**Branching / commits / push:**
- **D-19:** All commits land on `v1.5-uno328pb` in both `firestarter_app/` sub-repo and meta-repo (`/workspaces/`).
- **D-20:** NO remote push. Branch stays local until milestone close (post-Phase-25 merge-up).

### Claude's Discretion

- Single plan vs two-wave (RED tests Wave 1 then GREEN code Wave 2). **Recommendation: two waves (TDD shape).**
- Whether TDD RED/GREEN is enforced (TDD_MODE currently `false` in `.planning/config.json` — planner can opt in per-phase).
- Test method placement (new `TestUno328pbResolution` class vs sibling methods in existing classes).
- Wording of the elif branch's inline comment (cite Phase 21 D-10 hand-off optional).

### Deferred Ideas (OUT OF SCOPE)

- **Real-silicon flash of `firestarter_uno328pb.hex`** — Phase 24 (BENCH-01) owns this.
- **`urclock` fallback if `arduino` programmer_id fails** — 1-line follow-up commit on `v1.5-uno328pb` if Phase 24 surfaces it.
- **Refactor `_install_with_avrdude` to a dict-based registry** — defer to v1.6+ when a 4th board joins (three branches is below the "abstract me" threshold).
- **CLI documentation update mentioning the third board** — Phase 25 (DOC-01, DOC-02).
- **`setup.py` / `pyproject.toml` metadata bump** — Phase 24 milestone trigger.
- **avrdude.conf shipping with the package** — out of scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INST-01 | `firestarter fw -i` (stable, no flags) on a `uno328pb`-reporting device resolves latest stable `firestarter_uno328pb.hex` and flashes via avrdude with a 328PB-appropriate profile. | `fetch_release_info(channel="stable", board="uno328pb")` already board-driven (line 232 delegates to `fetch_latest_release_info`); D-01 elif branch supplies the avrdude profile. Test D-05 #1 (`test_uno328pb_stable_path_resolves_correct_asset`) covers it. |
| INST-02 | `firestarter fw -i --pre` resolves highest PEP 440 pre-release's `firestarter_uno328pb.hex` and flashes it. | `fetch_release_info(channel="pre", board="uno328pb")` already board-driven (line 261-301, PEP 440 sort via `packaging.version.Version`). Test D-05 #2 (`test_uno328pb_pre_path_resolves_highest_prerelease`) covers it. |
| INST-03 | `firestarter firmware list [--all\|--pre\|--stable]` enumerates `uno328pb` releases when a 328PB device is connected (same plain-text/JSON shape as for `uno`/`leonardo`). | `list_releases(board="uno328pb")` already board-driven (line 307-371). Test D-05 #3 (`test_uno328pb_list_releases_enumerates_correctly`) covers it. ⚠ See Open Q1 — `main.py` `--board` allowlist excludes `uno328pb` today; resolve before planning. |
| GATE-01 | After v1.5 lands, `firestarter fw -i` on uno/leonardo devices flashes byte-identical artifacts and behaves identically. | Verified via full-suite-green before+after (D-14, D-16). The elif insertion preserves the existing `if leonardo: ... else (uno default): ...` structure (D-07). Test D-06 (`test_uno328pb_avrdude_profile_resolution`) pins partno/programmer_id/baud_rate so any future refactor that perturbs uno/leonardo silently triggers a regression. |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Board-string -> AVR-profile mapping | Host CLI (`firmware.py:_install_with_avrdude`) | — | The AVR partno/programmer_id/baud_rate triple is host-side knowledge; firmware doesn't self-describe AVR-target metadata to the host. |
| Board-string -> .hex asset-name resolution | Host CLI (`firmware.py:fetch_release_info` / `fetch_latest_release_info` / `list_releases`) | — | Already implemented as `firestarter_{board}.hex` (v1.4 INST-04). Generic on `board: str`. |
| Board-string source-of-truth | Firmware handshake (`OK: FW: <version>:<board>` text wire) | — | Phase 21 firmware emits `uno328pb` via `-D RURP_BOARD_NAME=\"uno328pb\"` build flag. Host parses at `firmware.py:check_current_firmware` lines 101-117. |
| AVR flash subprocess | `avr_tool.py::Avrdude` | — | Pure subprocess wrapper around `avrdude`; takes partno/programmer_id/baud_rate as constructor args. No board-string knowledge. |
| CLI dispatch (`fw -i`, `fw -i --pre`, `firmware list`) | `main.py::main` | — | Already board-string-generic for the install path (uses `current_board` from handshake). Listing path uses `args.board` directly. |
| Test surface for mocked install | `tests/test_firmware_install.py` | `tests/conftest.py` (shared fixtures — not extended) | Module-local `mock_releases_factory` helper per VALIDATION convention from Phase 18. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.9-3.12 | Host runtime | `pyproject.toml` declares `requires-python = ">=3.9"`; pyproject classifiers list 3.9-3.12 [VERIFIED: `pyproject.toml`]. Test env runs Python 3.12.13 [VERIFIED: pytest output]. |
| pytest | 9.0.3 (installed); `>=7.0` declared | Test framework | `pyproject.toml [project.optional-dependencies] dev = ["pytest>=7.0"]`. Existing 77 tests passing in 0.82s [VERIFIED: `python -m pytest tests/`]. |
| packaging | 26.2 (installed); `>=21.0` declared | PEP 440 version parsing / sorting | `pyproject.toml` dependency. Used by `firmware.py:_compare_versions`, `fetch_release_info(channel='pre')` sort key, and `list_releases` PEP 440 descending sort [VERIFIED: imports at firmware.py:16]. |
| requests | (declared `>=2.20`) | HTTP client for GitHub Releases API | `pyproject.toml` dependency. Used throughout `firmware.py` for `/releases`, `/releases/latest`, `/releases/tags/{tag}` [VERIFIED: imports at firmware.py:13]. |
| unittest.mock | stdlib | Mock objects for tests | `MagicMock` used in 30 existing test methods in `test_firmware_install.py` [VERIFIED]. |
| pyserial | `>=3.5` | Serial I/O (firmware handshake) | `pyproject.toml` dependency. Used by `serial_comm.py`. NOT touched by Phase 23. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `avrdude` (system binary) | 7.x preferred (6.3 still supported) | AVR flash subprocess | Installed by operator via OS package manager. `avr_tool.py:Avrdude._find_avrdude_path` shells out to `which avrdude` or honors `--avrdude-path` CLI override [VERIFIED: avr_tool.py:54-65]. Phase 23 does NOT invoke avrdude — D-06 mocks the `Avrdude` constructor. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `monkeypatch.setattr(firmware, "Avrdude", ...)` | `unittest.mock.patch("firestarter.firmware.Avrdude")` | Both work; `monkeypatch` is the established pattern in the existing 30 tests, so D-06 should follow that convention to avoid mixing styles. |
| New `TestUno328pbResolution` class | Sibling methods in `TestFirmwareInstallStable` / `PreRelease` / `List` | Single class keeps the 4 new tests grep-walkable (`pytest -k uno328pb` selects exactly these tests, supporting D-16's `-k "not uno328pb"` non-regression command). **Recommendation: single new class.** |
| `pytest.mark.parametrize` to fold uno/leonardo/uno328pb | Three separate test methods per scenario | Parametrize would perturb existing test methods → GATE-01 risk (D-07: do NOT touch existing tests). **Avoid parametrize.** |

**Installation (already in place — no new packages needed):**
```bash
cd firestarter_app && pip install -e .  # already installed in the test env
pip install pytest                       # already installed (9.0.3)
```

**Version verification (HIGH confidence — verified against working environment):**
- `python --version` → 3.12.13
- `python -m pytest --version` → pytest 9.0.3
- `python -c "import packaging; print(packaging.__version__)"` → 26.2
- Pyproject `dependencies` block lists exact pins [VERIFIED: `/workspaces/firestarter_app/pyproject.toml:38-45`]

## Architecture Patterns

### System Architecture Diagram

```
Operator runs `firestarter fw -i` (or `fw -i --pre`, or `firmware list`)
       |
       v
  +----------------+
  | main.py        |  argparse: parse args, dispatch on args.command == "fw"
  +----------------+
       |
       | (install path: -i)        (list path: --list)
       v                             v
  +----------------+           +-------------------------+
  | check_current  |  serial   | list_releases(          |
  | _firmware()    |<-------->|     board=args.board)   |
  +----------------+  device   +-------------------------+
       |                             |  (uses args.board, NOT handshake)
       | board="uno328pb"            |
       v                             v
  +-----------------------+    GitHub /releases  (mocked in tests)
  | fetch_release_info(   |
  |     channel=stable|pre,
  |     board="uno328pb") |
  +-----------------------+
       |
       v
  asset_url = "https://.../firestarter_uno328pb.hex"
       |
       v
  +-------------------------+
  | _download_firmware_file |  (writes to ~/.firestarter/)
  +-------------------------+
       |
       v
  +-------------------------+
  | _install_with_avrdude(  |  <-- THE EDIT TARGET (lines 405-423)
  |     board="uno328pb")   |      D-01 adds elif branch
  +-------------------------+
       |
       | partno, programmer_id, baud_rate = (atmega328pb, arduino, 115200)
       v
  +-------------------------+
  | Avrdude(partno=...,     |  <-- D-06 mocks this constructor
  |   programmer_id=...,    |
  |   baud_rate=...,        |
  |   port=...)             |
  +-------------------------+
       |
       v
  subprocess: avrdude -p atmega328pb -c arduino -b 115200 -P /dev/ttyACMx
                       -U flash:w:<file>:i
```

### Recommended Project Structure (existing — no changes)

```
firestarter_app/
├── firestarter/
│   ├── firmware.py         # EDIT TARGET: line 405-423 (_install_with_avrdude)
│   ├── avr_tool.py         # NOT edited (D-09)
│   ├── constants.py        # NOT edited (D-08)
│   ├── main.py             # NOT edited per D-10 (⚠ see Open Q1)
│   ├── serial_comm.py      # NOT edited (D-11)
│   └── config.py           # NOT edited
└── tests/
    ├── test_firmware_install.py   # EDIT TARGET: 4 new test methods
    ├── conftest.py                # NOT edited
    └── ...
```

### Pattern 1: Board-driven asset resolution (existing, v1.4 INST-04)

**What:** Callers pass `board="X"`; resolver computes `f"firestarter_{board}.hex"` and finds the matching asset in the release's `assets[]` list. Source-of-truth for the board string is the firmware handshake `OK: FW: <version>:<board>`.

**When to use:** Phase 23 fits exactly this pattern by adding the missing AVR-side branch in `_install_with_avrdude`.

**Example (existing code, firmware.py:229-232):**
```python
# Source: firestarter_app/firestarter/firmware.py (working tree v1.5-uno328pb @ 5bb1766)
firmware_asset_name = f"firestarter_{board}.hex"

if channel == 'stable':
    return self.fetch_latest_release_info(board=board)
```

### Pattern 2: `_install_with_avrdude` if/elif structure (preserve verbatim, extend in place)

**What:** Existing structure at firmware.py:417-423 is `(uno default) if leonardo override`. D-01 inserts an `elif uno328pb:` clause WITHOUT refactoring the existing branches.

**Example (current code, firmware.py:417-423):**
```python
# Source: firestarter_app/firestarter/firmware.py:417-423 (working tree v1.5-uno328pb)
partno, programmer_id, baud_rate = (
    "atmega328p",
    "arduino",
    115200,
)  # Defaults for uno
if board.lower() == "leonardo":
    partno, programmer_id, baud_rate = ("atmega32u4", "avr109", 57600)
```

**Target shape after D-01 (Wave 2 lands this):**
```python
# Source: planned edit per CONTEXT D-01 + D-02 + D-03 + D-04
partno, programmer_id, baud_rate = (
    "atmega328p",
    "arduino",
    115200,
)  # Defaults for uno
if board.lower() == "leonardo":
    partno, programmer_id, baud_rate = ("atmega32u4", "avr109", 57600)
elif board.lower() == "uno328pb":
    # Phase 21 D-10 hand-off: ATmega328PB signature 0x1E 0x95 0x16 differs from
    # 328P's 0x1E 0x95 0x0F — partno must be "atmega328pb" exactly. programmer_id
    # "arduino" mirrors the uno profile (stk500v1 / optiboot); Phase 24 bench
    # validates against the operator's specific MiniCore bootloader.
    partno, programmer_id, baud_rate = ("atmega328pb", "arduino", 115200)
```

### Pattern 3: Mocked `firmware.requests.get` (the established 30-test pattern)

**What:** `monkeypatch.setattr(firmware.requests, "get", recording_get)` — the test owns the `requests.get` callable inside the `firmware` module namespace.

**When to use:** All 3 release-resolution tests (D-05) use this. Single-page (`/releases/latest`) returns a dict via `mock.json.return_value = <release_dict>`; paginated (`/releases`) returns a list with optional `Link: rel="next"` header.

**Example (existing test, test_firmware_install.py:121-147):**
```python
# Source: firestarter_app/tests/test_firmware_install.py:121-147
calls = []
stable_mock = mock_releases_factory([_STABLE_RELEASE_UNO])
stable_mock.json.return_value = _STABLE_RELEASE_UNO  # /releases/latest returns dict, not list

def recording_get(url, **kw):
    calls.append(url)
    return stable_mock

monkeypatch.setattr(firmware.requests, "get", recording_get)
fm = FirmwareManager(config_manager=MagicMock())
v, url = fm.fetch_release_info(channel="stable", board="uno")
assert v == "3.0.0"
assert "uno_stable.hex" in url
```

### Pattern 4: Mocked `firmware.Avrdude` constructor (NEW — D-06 introduces it)

**What:** `monkeypatch.setattr(firmware, "Avrdude", FakeAvrdude)` — capture constructor kwargs to assert partno/programmer_id/baud_rate. `Avrdude` is imported into the `firmware` module namespace at line 30, so the monkeypatch target is `firmware.Avrdude` (NOT `avr_tool.Avrdude` — that import is already resolved).

**When to use:** D-06 test only. The fake constructor captures kwargs and returns a stub whose `.flash_firmware()` returns `("", 0)` (success) to keep `_install_with_avrdude` happy.

**Example (planned — new pattern, no existing test in the suite uses it):**
```python
# Source: planned per CONTEXT D-06 (new pattern — first Avrdude mock in the suite)
class _FakeAvrdude:
    def __init__(self, partno, programmer_id, baud_rate, port, **kw):
        self.partno = partno
        self.programmer_id = programmer_id
        self.baud_rate = baud_rate
        self.port = port
        self.command = "/fake/avrdude"
        self.config = None  # avrdude>=7 path

    def flash_firmware(self, hex_file_path):
        return ("", 0)  # (stderr, returncode) — 0 = success

def test_uno328pb_avrdude_profile_resolution(self, monkeypatch, tmp_path):
    captured = {}

    def _capture_init(*args, **kwargs):
        captured.update(kwargs)
        return _FakeAvrdude(*args, **kwargs)

    monkeypatch.setattr(firmware, "Avrdude", _capture_init)
    fm = FirmwareManager(config_manager=MagicMock())
    fake_hex = tmp_path / "firestarter_uno328pb.hex"
    fake_hex.write_text(":00000001FF\n")
    ok = fm._install_with_avrdude(
        hex_file_path=str(fake_hex),
        board="uno328pb",
        avrdude_path_override=None,
        avrdude_config_override=None,
        target_port="/dev/ttyACM0",
    )
    assert ok is True
    assert captured["partno"] == "atmega328pb"
    assert captured["programmer_id"] == "arduino"
    assert captured["baud_rate"] == 115200
```

### Anti-Patterns to Avoid

- **Refactoring `_install_with_avrdude` to a dict-registry.** Violates D-07 (do not perturb existing branches). Defer to v1.6+ when a 4th board joins.
- **Extending `mock_releases_factory` to add a `board` kwarg.** The helper is board-agnostic by design — pass per-test release fixtures with the right asset names. Touching the helper would risk silent regressions in the 17 existing tests that use it.
- **Parametrizing existing tests to include `uno328pb`.** Violates D-07 — alters the test methods that GATE-01 relies on for non-regression. Add NEW test methods instead.
- **Putting fixtures in `conftest.py`.** Existing convention (per Phase 18 VALIDATION.md line 60) is module-local helpers in `test_firmware_install.py`. Stay consistent.
- **Mocking `firmware.requests` AND `firmware.Avrdude` in the SAME test.** D-05 tests stay release-resolution-only; D-06 stays avrdude-resolution-only. Keep the contract surface per-test narrow.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PEP 440 version sort | A homegrown tuple-comparison | `packaging.version.Version` (already in deps) | The v1.4 Phase 18 `_compare_versions` refactor proved tuple sort breaks on `3.1.0b10 > 3.1.0b9` (string sort inverts it). [VERIFIED: firmware.py:179] |
| AVR signature -> partno mapping | A homegrown signature lookup | `avrdude -p atmega328pb` (subprocess takes the partno verbatim) | avrdude.conf v7.x already knows the 328PB signature. Host-side hand-rolling would re-implement what avrdude already does correctly. |
| Avr-flash reset trigger for 32u4 | A homegrown 1200-baud DTR-toggle for the 328PB | Nothing — let the stk500v1/arduino programmer handle DTR auto-reset. | `avr_tool.py:_trigger_reset` is gated on `partno == "atmega32u4"` (line 98). The 328PB uses the same stk500v1 auto-reset as the 328P, so no special-casing needed (matches D-09). [VERIFIED: avr_tool.py:98-100] |
| GitHub Releases JSON parsing | A homegrown HTTP+JSON client | `requests.get(...).json()` + existing `mock_releases_factory` helper | The v1.4 INST-04 substrate already does this. Phase 23 tests reuse it. |
| Custom Avrdude mock framework | A homegrown subprocess-mock harness | `monkeypatch.setattr(firmware, "Avrdude", FakeAvrdude)` with a 6-line stub class | The single D-06 test does not justify a reusable harness. Inline `_FakeAvrdude` is the minimum sufficient scaffold. |

**Key insight:** Phase 23's surface is *deliberately* small because v1.4 Phase 18 already did the hard work of making release-resolution board-driven. The phase is a "fill in the missing mapping row" exercise, not a feature addition.

## Common Pitfalls

### Pitfall 1: `_install_with_avrdude` line range drift

**What goes wrong:** CONTEXT D-01 cites lines 405-423; Phase 21 D-10 cites 417-423. The planner uses one of these line ranges and the live file differs.

**Root cause:** Line numbers drift across commits. CONTEXT was written 2026-05-21 against the v1.5-uno328pb tip (5bb1766); Phase 21 D-10 was written earlier.

**Verification (HIGH confidence — checked live):** On `v1.5-uno328pb` @ commit 5bb1766:
- `_install_with_avrdude` definition starts at **line 406** (`def _install_with_avrdude(`)
- The `partno, programmer_id, baud_rate` triple is at **lines 417-421**
- The leonardo override is at **lines 422-423**
- The full mapping block (the elif insertion zone) is **lines 417-423** — exactly matching CONTEXT D-01.
- The function ends at line 514.

**How to avoid:** Plans use anchored substrings (`if board.lower() == "leonardo":`) not raw line numbers. The Edit tool's old_string/new_string contract is anchor-based and immune to drift.

### Pitfall 2: `current_board` from handshake overrides `args.board`

**What goes wrong:** A planner assumes the `--board uno328pb` CLI flag is needed for the install path and tries to widen `main.py`'s `--board` choices.

**Root cause:** `firmware.py:548` sets `board_to_use = current_board or board_override`. The handshake's `current_board` takes precedence; `args.board` (the `-b`/`--board` flag, default `"uno"`) is only the fallback when no device is connected.

**How to avoid:** The Phase 23 install path is exercised by mocked tests that pass `board="uno328pb"` directly to `fetch_release_info(...)`, NOT via argparse. CONTEXT D-10's "no main.py edits" is correct for the install path. (See Open Q1 for the listing-path nuance.)

**Warning sign:** If a draft plan proposes a main.py edit, double-check whether it's truly required for the requirement under test, or whether the handshake path already covers it.

### Pitfall 3: `firmware.requests.get` vs `requests.get` monkeypatch target

**What goes wrong:** Test uses `monkeypatch.setattr("requests.get", ...)` and the production code's already-imported `firmware.requests.get` doesn't see the patch.

**Root cause:** Python imports the `requests` module into the `firmware` namespace at line 13. Monkeypatching the global `requests.get` doesn't help if production code calls `firmware.requests.get`.

**Verification (HIGH confidence):** All 17 existing release-resolution tests use `monkeypatch.setattr(firmware.requests, "get", ...)` — never the global `requests.get`. [VERIFIED via grep on `test_firmware_install.py`]

**How to avoid:** Follow the established pattern verbatim. The D-05 tests are extensions of `TestFirmwareInstallStable / PreRelease / List` — copy a fixture row, swap board names + asset URLs, done.

### Pitfall 4: `mock_releases_factory` returns LIST; `/releases/latest` returns DICT

**What goes wrong:** D-05 #1 test (stable path) passes `mock_releases_factory([_STABLE_RELEASE_UNO328PB])` and gets a list back when `/releases/latest` should return a single release dict.

**Root cause:** `mock_releases_factory` is a generic builder. The `/releases/latest` endpoint returns a single release object, not a list. Existing tests override `mock.json.return_value = _STABLE_RELEASE_UNO` AFTER calling the factory to switch shape.

**Verification (HIGH confidence — test_firmware_install.py:131-134):**
```python
stable_mock = mock_releases_factory([_STABLE_RELEASE_UNO])
stable_mock.json.return_value = _STABLE_RELEASE_UNO  # <-- shape override
```

**How to avoid:** D-05 #1 mirrors this 2-line pattern. D-05 #2 (paginated `/releases`) uses the default list shape (no override).

### Pitfall 5: `Avrdude.__init__` performs `which()` + version probe — must be fully mocked

**What goes wrong:** Test mocks `Avrdude` but the production `_install_with_avrdude` calls `avrdude.flash_firmware(hex_file_path)`, which the mock doesn't implement. Test crashes with `AttributeError`.

**Root cause:** The real `Avrdude.__init__` runs `_find_avrdude_path` + `_get_avrdude_version` + maybe `_configure_avrconf`. The mock must skip all of that AND provide `.flash_firmware(...)` returning `(stderr, returncode)`.

**How to avoid:** D-06's `_FakeAvrdude` class needs: `partno/programmer_id/baud_rate/port` instance attrs (set in `__init__`); `command` attr (path string); `config` attr (None for v7.x path); `flash_firmware(hex_file_path) -> (stderr_str, returncode_int)` method returning `("", 0)`.

Additionally, `_install_with_avrdude` saves `config_manager.set_value("avrdude-path", avrdude.command)` on success (line 492). The mock's `.command` attr must therefore be a string (any value).

### Pitfall 6: `monkeypatch.setattr(firmware.requests, "get", ...)` test isolation

**What goes wrong:** Test 1 monkeypatches `firmware.requests.get`; Test 2 (next in the same class) re-monkeypatches it; behavior leaks across tests due to module-level state.

**Verification (LOW confidence — not directly checked, but the existing 17 tests show no isolation issues):** `monkeypatch` is per-test scoped — pytest's built-in `monkeypatch` fixture automatically undoes the setattr at test teardown. So isolation works for free as long as every test uses `monkeypatch` (not `setattr` on the module globally).

**How to avoid:** All 4 new tests must accept `monkeypatch` (and optionally `tmp_path` for D-06) as fixture args. Never set a module attribute outside `monkeypatch.setattr`.

### Pitfall 7: GATE-01 case-count check is OFF by 4 after the phase

**What goes wrong:** CONTEXT D-16 says `pytest -k "not uno328pb" exits 0 with the same case count as pre-Phase-23`. Pre-Phase-23 baseline: **77 tests**. Post-Phase-23 expectation: **81 tests total**; `-k "not uno328pb"` should still exit with 77.

**Verification (HIGH confidence):**
- Pre-Phase-23: `python -m pytest tests/` → `77 passed in 0.82s` [VERIFIED on v1.5-uno328pb @ 5bb1766]
- `python -m pytest tests/test_firmware_install.py -k "uno328pb" --collect-only` → `30 deselected in 0.16s` (today the filter selects 0 tests, because no test name contains "uno328pb") [VERIFIED]

**How to avoid:** Test method names MUST contain the substring `uno328pb` (case-sensitive — pytest `-k` is case-insensitive substring match, but the convention so far has been lowercase). Recommended names:
- `test_uno328pb_stable_path_resolves_correct_asset`
- `test_uno328pb_pre_path_resolves_highest_prerelease`
- `test_uno328pb_list_releases_enumerates_correctly`
- `test_uno328pb_avrdude_profile_resolution`

The non-regression command then selects exactly the 77 pre-Phase-23 tests:
```bash
cd firestarter_app && python -m pytest tests/test_firmware_install.py -v -k "not uno328pb"
# Expected: 30 - 4 = 26 in test_firmware_install.py to pass (plus other test files give 77 - 30 + 26 = 73 total in -k call when scoped to test_firmware_install.py)
```

⚠ **Correction**: D-16's command is scoped to `test_firmware_install.py` only. With 4 new tests added to that file, post-Phase-23 file count is 34; `-k "not uno328pb"` selects 30 (the pre-Phase-23 count for that file). So the case-count regression check is "**26 of the existing 30 are selected? No — 30 of the existing 30 are selected** because none of them contains `uno328pb` in the name." Verified: pre-Phase-23 `pytest tests/test_firmware_install.py -k "uno328pb"` returns 0 deselected. **Validity confirmed.**

## Runtime State Inventory

> Phase 23 is greenfield (a code+test addition, no rename/refactor/migration). This section is included for completeness but is NOT a rename/refactor phase.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no datastore stores the avrdude profile or `uno328pb` string. Released `.hex` files come from GitHub Releases (Phase 22 substrate) at flash time, not from a local DB. | None |
| Live service config | None — host CLI has no n8n / Datadog / external-service state. GitHub Releases asset name `firestarter_uno328pb.hex` is generated server-side by `softprops/action-gh-release` glob (Phase 22 D-03). | None |
| OS-registered state | None — host CLI is a pip-installed Python package; no Windows Task Scheduler / systemd / pm2 / launchd registrations. | None |
| Secrets / env vars | `FIRESTARTER_DEV_ALLOW_PRE_V12` is cleared in `_isolate_env` fixtures (test-isolation only, not Phase 23 surface). No secret keys reference `uno328pb`. | None |
| Build artifacts / installed packages | `firestarter_app/firestarter.egg-info/` is the only `.egg-info` directory. It tracks the installed package metadata, NOT board-string state. `pip install -e .` is idempotent across the elif insertion. | None — `pip install -e .` re-run is unnecessary; the import surface doesn't change (no new symbols exported). |

**Nothing found in any category.** This phase is a code edit + test addition only.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All host code | ✓ | 3.12.13 | None — no fallback (project requires 3.9+) |
| pytest | Phase 23 test execution | ✓ | 9.0.3 | None — installed via `pip install pytest` |
| packaging | `firmware.py:_compare_versions`, sort keys | ✓ | 26.2 | None — dependency declared in `pyproject.toml` |
| requests | `firmware.py` HTTP client | ✓ (declared `>=2.20`) | (installed via pyproject deps) | None — dependency declared |
| pyserial | `serial_comm.py` (NOT touched by Phase 23) | ✓ (declared `>=3.5`) | — | NOT exercised by Phase 23 (no real serial — `check_current_firmware` is NOT called by D-05 / D-06 tests; they call resolver methods directly) |
| `avrdude` (system) | `avr_tool.py:Avrdude` (NOT called in Phase 23 tests) | ✗ (not installed in repo env) | — | **Fully mocked.** D-06 monkeypatches `firmware.Avrdude` — the real binary is NOT invoked. |
| git | Commit landing | ✓ | (system) | None |

**Missing dependencies with no fallback:** None — every Phase 23 surface is satisfied.

**Missing dependencies with fallback:** `avrdude` (mocked in tests; real binary only matters at Phase 24 bench time).

## Code Examples

### Example 1: D-05 #1 — stable path resolves correct asset (planned test method)

```python
# Source: planned per CONTEXT D-05, modeled on test_firmware_install.py:121-147
# (test_stable_default_hits_releases_latest)

_STABLE_RELEASE_UNO328PB = {
    "tag_name": "3.0.1",
    "prerelease": False,
    "draft": False,
    "published_at": "2026-05-22T11:00:00Z",
    "assets": [
        {
            "name": "firestarter_uno.hex",
            "browser_download_url": "https://example.com/uno_stable.hex",
        },
        {
            "name": "firestarter_uno328pb.hex",
            "browser_download_url": "https://example.com/uno328pb_stable.hex",
        },
        {
            "name": "firestarter_leonardo.hex",
            "browser_download_url": "https://example.com/leonardo_stable.hex",
        },
    ],
}


class TestUno328pbResolution:
    """Phase 23 — INST-01/02/03 board-driven asset + avrdude profile resolution
    for uno328pb-reporting devices.

    Decisions pinned: D-01..D-06 (CONTEXT.md).
    """

    @pytest.fixture(autouse=True)
    def _isolate_env(self, monkeypatch):
        monkeypatch.delenv("FIRESTARTER_DEV_ALLOW_PRE_V12", raising=False)

    def test_uno328pb_stable_path_resolves_correct_asset(self, monkeypatch):
        """INST-01 / D-01 — fetch_release_info(channel='stable', board='uno328pb')
        returns the uno328pb_stable.hex asset URL from a 3-asset release.
        """
        stable_mock = mock_releases_factory([_STABLE_RELEASE_UNO328PB])
        stable_mock.json.return_value = _STABLE_RELEASE_UNO328PB
        monkeypatch.setattr(firmware.requests, "get", lambda url, **kw: stable_mock)
        fm = FirmwareManager(config_manager=MagicMock())
        v, url = fm.fetch_release_info(channel="stable", board="uno328pb")
        assert v == "3.0.1"
        assert "uno328pb_stable.hex" in url
        assert "uno_stable.hex" not in url  # must NOT pick the uno asset
```

### Example 2: D-05 #2 — pre path picks highest PEP 440 pre-release (planned test method)

```python
# Source: planned per CONTEXT D-05 #2, modeled on test_pre_selects_highest_prerelease

def test_uno328pb_pre_path_resolves_highest_prerelease(self, monkeypatch):
    """INST-02 / D-01 — fetch_release_info(channel='pre', board='uno328pb')
    selects highest pre-release with uno328pb asset (rc1 > b10 > b9 by PEP 440).
    """
    releases = [
        {
            "tag_name": "3.0.1b9",
            "prerelease": True,
            "draft": False,
            "published_at": "2026-05-10T10:00:00Z",
            "assets": [
                {"name": "firestarter_uno328pb.hex",
                 "browser_download_url": "https://example.com/uno328pb_b9.hex"},
            ],
        },
        {
            "tag_name": "3.0.1rc1",
            "prerelease": True,
            "draft": False,
            "published_at": "2026-05-20T09:00:00Z",
            "assets": [
                {"name": "firestarter_uno328pb.hex",
                 "browser_download_url": "https://example.com/uno328pb_rc1.hex"},
            ],
        },
        {
            "tag_name": "3.0.1b10",
            "prerelease": True,
            "draft": False,
            "published_at": "2026-05-15T08:00:00Z",
            "assets": [
                {"name": "firestarter_uno328pb.hex",
                 "browser_download_url": "https://example.com/uno328pb_b10.hex"},
            ],
        },
    ]
    mock = mock_releases_factory(releases)
    monkeypatch.setattr(firmware.requests, "get", lambda *a, **kw: mock)
    fm = FirmwareManager(config_manager=MagicMock())
    version, url = fm.fetch_release_info(channel="pre", board="uno328pb")
    assert version == "3.0.1rc1"  # rc > b per PEP 440
    assert "uno328pb_rc1.hex" in url
```

### Example 3: D-05 #3 — list_releases enumerates uno328pb correctly (planned)

```python
# Source: planned per CONTEXT D-05 #3, modeled on test_list_releases_sorted_descending

def test_uno328pb_list_releases_enumerates_correctly(self, monkeypatch):
    """INST-03 / D-01 — list_releases(board='uno328pb') returns ReleaseInfo entries
    in PEP 440 descending order with the same 5-key shape as for uno/leonardo.
    """
    releases = [
        _STABLE_RELEASE_UNO328PB,  # 3.0.1 stable
        {
            "tag_name": "3.0.1b2",
            "prerelease": True,
            "draft": False,
            "published_at": "2026-05-18T10:00:00Z",
            "assets": [
                {"name": "firestarter_uno328pb.hex",
                 "browser_download_url": "https://example.com/uno328pb_b2.hex"},
            ],
        },
    ]
    mock = mock_releases_factory(releases)
    monkeypatch.setattr(firmware.requests, "get", lambda *a, **kw: mock)
    fm = FirmwareManager(config_manager=MagicMock())
    out = fm.list_releases(channel_filter="all", board="uno328pb")
    assert len(out) == 2
    assert out[0]["version"] == "3.0.1"     # stable > pre-release per PEP 440
    assert out[1]["version"] == "3.0.1b2"
    required_keys = {"version", "tag", "channel", "published", "asset_url"}
    for entry in out:
        assert required_keys <= entry.keys()
        assert "uno328pb" in entry["asset_url"]
```

### Example 4: D-06 — avrdude profile resolution (planned, NEW pattern)

```python
# Source: planned per CONTEXT D-06 — first Avrdude mock in the test suite.

class _FakeAvrdude:
    """Captures Avrdude(...) constructor kwargs for D-06 assertions."""

    def __init__(self, partno, programmer_id, baud_rate, port, **kw):
        self.partno = partno
        self.programmer_id = programmer_id
        self.baud_rate = baud_rate
        self.port = port
        self.command = "/fake/avrdude"  # str — _install_with_avrdude saves this
        self.config = None              # avrdude>=7 path (no -C arg)

    def flash_firmware(self, hex_file_path):
        return ("", 0)  # (stderr, returncode) — 0 = success


def test_uno328pb_avrdude_profile_resolution(self, monkeypatch, tmp_path):
    """INST-01 / D-01..D-04 — _install_with_avrdude(board='uno328pb') passes
    (partno='atmega328pb', programmer_id='arduino', baud_rate=115200) to Avrdude().
    """
    captured = {}

    def _capture_init(*args, **kwargs):
        captured.update(kwargs)
        return _FakeAvrdude(*args, **kwargs)

    monkeypatch.setattr(firmware, "Avrdude", _capture_init)
    fake_hex = tmp_path / "firestarter_uno328pb.hex"
    fake_hex.write_text(":00000001FF\n")  # minimal valid Intel HEX EOF record

    fm = FirmwareManager(config_manager=MagicMock())
    ok = fm._install_with_avrdude(
        hex_file_path=str(fake_hex),
        board="uno328pb",
        avrdude_path_override=None,
        avrdude_config_override=None,
        target_port="/dev/ttyACM0",
    )
    assert ok is True
    assert captured["partno"] == "atmega328pb"
    assert captured["programmer_id"] == "arduino"
    assert captured["baud_rate"] == 115200
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hard-coded `board: Literal["uno", "leonardo"]` allowlist | Duck-typed `board: str` plumbed through `fetch_release_info` / `list_releases` / `_install_with_avrdude` | v1.4 INST-04 (Phase 18, shipped 2026-05-20) | Phase 23 fits naturally — no new abstraction needed, just the missing data row. |
| `tuple(map(int, v.split(".")))` version compare | `packaging.version.Version` (PEP 440) | v1.4 Phase 18 (`_compare_versions` refactor) | Pre-release / dev suffix versions now sort correctly. Phase 23 leverages this for pre-release selection. |
| Hand-rolled stk500/avr-dude reset | `avrdude -c arduino` (handles DTR auto-reset via the stk500v1 protocol) | Pre-v1.0 (existing behavior) | Phase 23 inherits this — no special-casing for `atmega328pb` reset. |

**Deprecated/outdated:**
- None — the existing v1.4 substrate is current.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The ATmega328PB stk500v1/optiboot bootloader at 115200 baud will accept `avrdude -p atmega328pb -c arduino`. [ASSUMED — Phase 24 bench-validated] | D-02 / D-04 | Operator's specific 328PB-Uno may have a MiniCore Urclock bootloader instead. Mitigation: 1-line edit on `v1.5-uno328pb` to swap `"arduino"` → `"urclock"` if Phase 24 surfaces the mismatch. |
| A2 | The `_install_with_avrdude` mock pattern via `monkeypatch.setattr(firmware, "Avrdude", FakeAvrdude)` does not perturb the import already resolved at line 30. [ASSUMED — verified by analogy to `firmware.requests.get` pattern, but not yet exercised] | Pitfall 5 | If the production code path internally re-imports `Avrdude` (e.g. via `from .avr_tool import Avrdude` inside the function), the mock won't apply. Mitigation: write D-06 first; if mock doesn't propagate, switch to `unittest.mock.patch("firestarter.firmware.Avrdude")` with autouse semantics. (Inspection of `_install_with_avrdude` confirms it uses the module-level `Avrdude` symbol — no inner re-import.) |
| A3 | Test method names containing `uno328pb` will be selected by `pytest -k "uno328pb"` (case-sensitive substring match). [VERIFIED via dry-run on v1.5-uno328pb HEAD: `pytest -k uno328pb` returns 0 deselected today; will return 4 selected post-Phase-23.] | Pitfall 7 | None — verified. |
| A4 | `mock_releases_factory(releases)` shape works for `uno328pb` releases without modification. [VERIFIED — the helper is board-agnostic; it just wraps a list of release dicts.] | Pattern 3 | None — verified. |
| A5 | Adding 4 tests increases full-suite-time by < 1 second. [ASSUMED — extrapolation from 30 existing tests in test_firmware_install.py running in 0.16s total.] | D-14 | Negligible risk. |
| A6 | `firestarter firmware list` does NOT call `check_current_firmware()` and therefore cannot resolve `board="uno328pb"` from a connected device — it uses `args.board` (operator-supplied, default "uno", choices=["uno","leonardo"]). [VERIFIED via inspection of `main.py:739-757`] | Open Q1 | If INST-03 SC#3 ("when a 328PB device is connected") is read strictly, this is a real gap. Mitigation options listed in Open Q1. |

## Open Questions

### Open Q1: `main.py --board` allowlist excludes `uno328pb` — does INST-03 require resolving this?

- **What we know:** `main.py:288-291` declares `choices=["uno", "leonardo"]` for the `-b/--board` argparse argument. The install path (`fw -i`) uses `current_board` from handshake (overrides `args.board` for the install flow), so a `uno328pb`-reporting connected device flashes correctly without touching `--board`. **However**, the listing path (`firmware list`) passes `args.board` directly to `list_releases(board=args.board)` and never invokes `check_current_firmware()`. So `firestarter firmware list --board uno328pb` is **rejected by argparse today** with `error: argument -b/--board: invalid choice: 'uno328pb'`.
- **What's unclear:** CONTEXT D-10 says "main.py requires NO edits". But INST-03 SC#3 says `firestarter firmware list` enumerates `uno328pb` releases **when a 328PB device is connected**. The current code doesn't auto-detect board for list; it relies on `--board`. Either (a) `--board` choices must widen to include `uno328pb` (1-line edit to main.py), OR (b) the list path must be re-architected to call `check_current_firmware()` (larger main.py edit), OR (c) the operator is expected to use the listing-path with the `--board` flag and INST-03's "when a 328PB device is connected" is interpreted as "when the listing target is uno328pb".
- **Recommendation:** Surface this to the planner in the plan's Open Questions section. The cleanest reading is **(a) — widen `--board` choices in main.py to `["uno", "leonardo", "uno328pb"]`**, treating it as the "allowlist entry" language already in INST ("v1.5 adds (a) any board-allowlist entry needed elsewhere in the host code (`avr_tool.py` upload profile, `constants.py` enum, etc.)"). This contradicts CONTEXT D-10's negative scope but matches the requirements text in `REQUIREMENTS.md:32` verbatim. If the planner proceeds with the strict CONTEXT D-10 interpretation (no main.py edits), then INST-03 SC#3 is partially unsatisfied for the operator-driven listing-by-flag case (handshake-driven listing isn't implemented anywhere). **The planner should escalate to the operator before locking the plan.** If unresolved, the minimum-deviation option is to honor CONTEXT D-10 verbatim and document the gap as a Phase 24 / future-work item.

### Open Q2: TDD shape — single plan with two waves, or single wave?

- **What we know:** TDD_MODE is `false` in `.planning/config.json`, so TDD is not enforced. CONTEXT Claude's Discretion item #1 explicitly leaves this to the planner.
- **What's unclear:** Whether the operator prefers the TDD RED/GREEN cadence (Wave 1: 4 RED tests → Wave 2: 1 elif branch turns them GREEN) or a single atomic wave (1 commit with elif branch + 4 tests together).
- **Recommendation:** **Two-wave TDD shape.** Rationale: (a) the avrdude-profile test (D-06) is a brand-new mock surface — landing it RED first proves the mock pattern works in isolation before the production code change masks any mock-pattern bug; (b) the elif branch is small, so the GREEN wave is a trivial commit; (c) two atomic commits provide cleaner `git bisect` resolution if a future regression bisects into this phase. Single-wave is acceptable if the operator prefers speed.

### Open Q3: Should D-06 use `monkeypatch.setattr(firmware, "Avrdude", ...)` or `unittest.mock.patch("firestarter.firmware.Avrdude")`?

- **What we know:** All existing tests use `monkeypatch.setattr(firmware.requests, "get", ...)`. No existing test mocks `Avrdude`.
- **What's unclear:** Whether the same `monkeypatch.setattr(firmware, "Avrdude", FakeAvrdude)` pattern works for class symbols (vs. callable attributes). Python module attrs are duck-typed, so both should work, but the pattern hasn't been exercised yet.
- **Recommendation:** Use `monkeypatch.setattr(firmware, "Avrdude", _capture_init)` first (matches the established style). If the test fails because production code uses a different import shape, fall back to `unittest.mock.patch`. Verified by inspection: `firmware.py` imports `Avrdude` once at line 30 into the `firmware` module namespace; production code at line 472 uses `Avrdude(...)` (resolved against `firmware.Avrdude`). The `monkeypatch.setattr(firmware, "Avrdude", ...)` shape will work.

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md`:
- Meta-repo tracks only `.planning/` + `.claude/` — neither sub-repo is committed here. ✓ Honored by D-17 (sub-repo edits land in `firestarter_app/`, meta-repo carries planning docs only).
- Sub-repos: `firestarter_app/` is the Python pip package. ✓
- Wire protocol changes must be synced firmware ↔ host. ✓ Phase 23 does NOT touch the wire protocol.
- Constants/flag bits are duplicated `constants.py` ↔ `firestarter.h`. ✓ Phase 23 does NOT touch constants.

From `/workspaces/firestarter_app/CLAUDE.md`:
- Test invocation: pyproject `[tool.pytest.ini_options] testpaths = ["tests"]` — canonical command is `python -m pytest tests/`. ✓ D-14 uses this.
- Hardware integration: `./firestarter_test.sh [EPROM]` — NOT exercised by Phase 23 (mocked-only).
- Database pipeline: `tools/build_db.py` regenerates `chip_database.json`. ✓ NOT touched by Phase 23.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 (declared `>=7.0` in pyproject) |
| Config file | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests"]`, `addopts = "-ra -q"` |
| Quick run command | `cd firestarter_app && python -m pytest tests/test_firmware_install.py -v` |
| Full suite command | `cd firestarter_app && python -m pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INST-01 | `fetch_release_info(channel='stable', board='uno328pb')` resolves correct asset URL | unit | `pytest tests/test_firmware_install.py::TestUno328pbResolution::test_uno328pb_stable_path_resolves_correct_asset -x` | ❌ Wave 1 creates it |
| INST-02 | `fetch_release_info(channel='pre', board='uno328pb')` picks highest PEP 440 pre-release | unit | `pytest tests/test_firmware_install.py::TestUno328pbResolution::test_uno328pb_pre_path_resolves_highest_prerelease -x` | ❌ Wave 1 creates it |
| INST-03 | `list_releases(board='uno328pb')` returns same shape as uno/leonardo | unit | `pytest tests/test_firmware_install.py::TestUno328pbResolution::test_uno328pb_list_releases_enumerates_correctly -x` | ❌ Wave 1 creates it |
| INST-01 (avrdude profile) | `_install_with_avrdude(board='uno328pb')` passes `(atmega328pb, arduino, 115200)` to `Avrdude()` | unit | `pytest tests/test_firmware_install.py::TestUno328pbResolution::test_uno328pb_avrdude_profile_resolution -x` | ❌ Wave 1 creates it |
| GATE-01 (non-regression) | Full suite green; uno/leonardo behaviors unchanged | unit | `pytest tests/test_firmware_install.py -v -k "not uno328pb"` — must match pre-Phase-23 case count (26 — see Pitfall 7 note: existing 30, minus 4 uno328pb-named added) | ✓ existing tests |
| GATE-01 (full suite) | All 77+4 = 81 tests green | unit | `pytest tests/ -v` — must show 81 passed | ✓ existing tests |

### Sampling Rate

- **Per task commit:** `cd firestarter_app && python -m pytest tests/test_firmware_install.py -v -k uno328pb` (selects 4 new tests; runs in < 1s)
- **Per wave merge:** `cd firestarter_app && python -m pytest tests/test_firmware_install.py -v` (full module — 34 cases post-Phase-23)
- **Phase gate:** `cd firestarter_app && python -m pytest tests/ -v` — full suite 81 cases green before `/gsd-verify-work`

### Wave 0 Gaps

None — existing test infrastructure (`conftest.py`, `pyproject.toml [tool.pytest.ini_options]`, `mock_releases_factory` helper in `test_firmware_install.py`) covers all phase requirements. **Phase 23 does NOT need a Wave 0 scaffold.** Wave 1 directly extends `test_firmware_install.py` with the 4 new test methods.

## Security Domain

> `security_enforcement` not explicitly set in `.planning/config.json` — treat as enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Phase 23 does not touch authentication. The avrdude flow is local (operator + USB serial); no network auth boundary. |
| V3 Session Management | no | No sessions — single-shot CLI invocations. |
| V4 Access Control | no | No access control surface. Operator runs CLI under their own UID; avrdude inherits the same. |
| V5 Input Validation | yes (minimal) | `FIRMWARE_VERSION_RE` (firmware.py:43, anchored with `\Z` to defend against trailing-newline smuggling — fixed by v1.4 Phase 18 CR-02). Phase 23 does NOT add new operator-input surfaces. |
| V6 Cryptography | no | No crypto in Phase 23. Firmware `.hex` files are downloaded over HTTPS (GitHub Releases) — TLS is delegated to `requests`. |
| V9 Communications | yes (passive) | HTTPS via `requests` (`https://api.github.com/.../releases/...`). No certificate-pinning, but standard `requests` cert validation is in effect. |
| V10 Malicious Code | no | `.hex` payload trust model: operator trusts the GitHub Releases binary signature implicitly (no GPG verification in v1.5 — out of scope). |

### Known Threat Patterns for Python CLI + GitHub Releases API

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| URL template injection via `--firmware-version` | Tampering | `FIRMWARE_VERSION_RE` anchored with `\Z` to reject embedded newlines (v1.4 Phase 18 CR-02). Phase 23 does not add new url-template surface. |
| Path traversal via downloaded `.hex` filename | Tampering | `_download_firmware_file` extracts filename from URL via `url.split("/")[-1]`. GitHub Releases asset names are server-controlled and constrained to `firestarter_*.hex` glob (Phase 22). Not a Phase 23 surface. |
| Subprocess injection via `avrdude_path_override` | Tampering | `Avrdude._find_avrdude_path` uses `shutil.which(...)` — no shell metacharacter expansion. CLI flag is operator-controlled (trust boundary respected). |
| Malicious `.hex` content | Tampering | Out of scope (Phase 25 docs covers operator guidance; no Phase 23 surface). |

**Net assessment:** Phase 23 is a low-security-risk extension. It adds NO new operator-input surfaces, NO new network endpoints, NO new file-path manipulations. The single elif branch hard-codes string constants (`"atmega328pb"`, `"arduino"`, `115200`) that flow into `Avrdude.build_options(...)` as positional argv elements (no shell concatenation).

## Sources

### Primary (HIGH confidence)
- **Working tree** at `firestarter_app/v1.5-uno328pb @ 5bb1766` — verified line ranges, function signatures, import shapes, test case counts, baseline `pytest tests/` exit 0 / 77 passed in 0.82s.
- `firestarter_app/firestarter/firmware.py` lines 1-636 — read in full, verified `_install_with_avrdude` is at 406-514, the mapping triple is at 417-423, `Avrdude(...)` instantiation is at 472-479.
- `firestarter_app/firestarter/avr_tool.py` lines 1-169 — read in full, confirmed `Avrdude.__init__` signature and `partno == "atmega32u4"` reset-trigger gate at line 98.
- `firestarter_app/firestarter/main.py` lines 245-305, 730-797 — confirmed `--board choices=["uno", "leonardo"]` (line 288-291), confirmed install path uses `args.board` only as fallback (line 777), confirmed list path uses `args.board` directly (line 748).
- `firestarter_app/firestarter/constants.py` — grep confirms no board enum/allowlist (only `LEONARDO_BUFFER_SIZE = 1024`).
- `firestarter_app/tests/test_firmware_install.py` lines 1-1068 — verified class structure (7 classes, 30 tests), verified `mock_releases_factory` shape, verified `monkeypatch.setattr(firmware.requests, "get", ...)` pattern.
- `firestarter_app/tests/conftest.py` lines 1-146 — verified no test_firmware_install-relevant fixtures live there.
- `firestarter_app/pyproject.toml` — verified `[tool.pytest.ini_options] testpaths = ["tests"]`, declared deps, Python version constraint.
- `.planning/phases/23-host-cli-installer-integration/23-CONTEXT.md` — 20 locked decisions D-01..D-20.
- `.planning/phases/23-host-cli-installer-integration/23-DISCUSSION-LOG.md` — auto-resolved gray areas record.
- `.planning/REQUIREMENTS.md` lines 30-42 — INST-01/02/03 + GATE-01 acceptance criteria.
- `.planning/phases/21-firmware-target-uno328pb/21-CONTEXT.md` D-10 — Phase 21 → Phase 23 hand-off with line range (417-423) and signature mismatch warning.
- `.planning/phases/22-release-pipeline-artifacts/22-CONTEXT.md` — Phase 22 substrate confirmation.
- Live verification: `python -m pytest tests/ → 77 passed`; `pytest tests/test_firmware_install.py -k uno328pb → 30 deselected`.
- `/workspaces/CLAUDE.md`, `/workspaces/firestarter_app/CLAUDE.md` — project conventions.

### Secondary (MEDIUM confidence)
- `.planning/STATE.md` — milestone progress (v1.5 40% complete, Phases 21+22 SHIPPED).
- `.planning/ROADMAP.md` Phase 23 details (SC#1-5).
- `.planning/PROJECT.md` GATE-1.5 invariant statement.

### Tertiary (LOW confidence — not used as authoritative)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every package version verified live (`python -m pip show ...` equivalents via direct check).
- Architecture (elif insertion point + import shape): HIGH — `_install_with_avrdude` source read, `Avrdude` import at firmware.py:30 confirmed.
- Test patterns: HIGH — 30 existing tests read; `mock_releases_factory` + `monkeypatch` style verified.
- D-06 mock pattern (`monkeypatch.setattr(firmware, "Avrdude", ...)`): MEDIUM-HIGH — pattern is analogous to `firmware.requests`, but no existing test mocks a class symbol via this surface. Verified by inspection but not yet executed.
- Pitfalls: HIGH — all 7 pitfalls cross-referenced against live source.
- Open Question 1 (main.py `--board` allowlist): HIGH — code reality contradicts CONTEXT D-10 narrow reading; planner must reconcile before locking the plan.
- Bench-validated avrdude profile (`arduino` vs `urclock`): MEDIUM — D-02 reasoning is sound but unverified on real silicon; Phase 24 closes this.

**Research date:** 2026-05-21
**Valid until:** 2026-06-04 (14 days — stable substrate, no fast-moving dependencies; live env baseline at firestarter_app @ 5bb1766)

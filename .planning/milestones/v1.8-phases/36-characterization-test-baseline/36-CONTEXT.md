# Phase 36: Characterization Test Baseline - Context

**Gathered:** 2026-05-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Build a golden-master **safety net** — characterization tests pinning the current CLI command surface, the serial frame-parse path, and the EPROM database layer — plus an extended firmware-contract parity test, and remove the `EpromDatabase` singleton so the DB is independently testable. This is the prerequisite for every later v1.8 phase: the net must be committed **before** any structural change (Phases 37–43).

This phase is **almost entirely additive**. The *only* production-code change is the `EpromDatabase` de-singleton (TEST-03). Bug *fixes* are NOT done here — they are sequenced into later phases (41/42); Phase 36 only *characterizes* them by asserting corrected behavior.

Requirements: TEST-01, TEST-02, TEST-03, TEST-04, TEST-05 (full text in `.planning/REQUIREMENTS.md`).
</domain>

<decisions>
## Implementation Decisions

### CLI Characterization Harness (TEST-01)
- **D-01:** **subprocess black-box** harness for the command-surface golden. Tests invoke the real `firestarter` entry point as a subprocess and snapshot stdout/stderr/exit-code. Rationale: the harness code is **identical before and after the argparse→Click migration** (Phase 41) — only the implementation behind the binary changes — so the same golden *proves GATE-1.8(b) "CLI surface preserved" byte-for-byte*. The CLI is **argparse today** (`main.py:513`); `CliRunner` cannot wrap it, which is why the roadmap's "via CliRunner before migration" phrasing does not literally apply to the subprocess goldens.
- **D-02:** read/write/verify/erase **happy-paths** are characterized **in-process** using the existing `make_comm`/`fake_serial` fixtures (`tests/conftest.py`) fed canned firmware responses — NOT via subprocess (a `BytesIO` fake cannot be injected across the process boundary). **No new production "serial replay" seam is added in Phase 36.** This happy-path in-process subset is re-pointed from `main()` to `CliRunner.invoke()` at Phase 41; the subprocess help/DB/error goldens stay unchanged through the migration.
- **D-03:** Scope is **broad** — pin BOTH the board-independent surface (`--help` for top-level + every subcommand; DB-backed `list`/`info`/`search`; ALL argument-parse/usage errors incl. unknown cmd, bad chip, missing args, `--pre`/`--firmware-version`/`--stable` mutex, `--no-blank-check` polarity, bad `--address`/`--size`; hardware-absent error paths) AND the E2E read/write/verify/erase happy-paths (via D-02's in-process route).

### Snapshot Tooling + Determinism (TEST-01)
- **D-04:** **syrupy** is the snapshot mechanism (`assert result == snapshot`, `--snapshot-update`, `__snapshots__/`). Add to `[project.optional-dependencies].test` in `pyproject.toml`. The existing `tests/golden/` dir holds only ~22-byte placeholder stubs + a coverage matrix — there is no established golden-file harness to preserve.
- **D-05:** Determinism across CI (no board) and the operator's bench (board may be attached) = **(a)** syrupy normalization filters scrubbing package version strings, absolute paths, and enumerated `/dev/tty*` port names; **(b)** **neutralize port auto-discovery** in hardware-touching tests so output is identical with/without a board attached — note `serial_comm.py:_list_potential_ports` *appends* discovered system ports even when `-p` is given, so a bogus port alone is insufficient (planner picks the mechanism: a narrow test-only seam OR mock at the `serial.tools.list_ports.comports` boundary); **(c)** DB pinned to the packaged `chip_database.json` with the `~/.firestarter` user-override merge skipped (see D-06).

### EpromDatabase De-Singleton (TEST-03) — the only production-code change
- **D-06:** **Minimal** de-singleton. Remove the `__new__`/`_initialized` singleton guard (`database.py:165-181`); add a constructor seam — `EpromDatabase(database_path=<packaged JSON default>)` plus the ability to **skip the `get_local_database()` user-override merge** (`database.py:193-195`) for deterministic tests. Keep per-site `EpromDatabase()` construction — call sites already accept an injected instance (`EpromInfo(db_instance)`, `ChipLayout(db_instance)`, `main():589` builds one and threads it down). Defer any Click-context DI wiring to Phase 41. Lowest blast radius consistent with TEST-03.
- **D-07:** `tests/test_eprom_database.py` covers `get_eprom`, `convert_to_programmer`, and DIP→RURP pin translation against **real `chip_database.json` data** — without `find_and_connect` or serial I/O.

### Bug Characterization (TEST-05)
- **D-08:** TEST-05 pins exactly **two genuine bugs**, NEITHER pinned as correct (each test asserts the *corrected* behavior):
  1. `build_arg_flags` `if "force" in args` attribute-vs-truthiness check (`main.py:497`) — fix lands in **Phase 41 (CLI-03)** with an `INTENTIONAL BEHAVIOR CHANGE` commit.
  2. **Hardware-error mislabeled as communication-error** (`eprom_operations.py:265-267`) — `EpromOperationError` (a firmware-reported *operational* error that arrived fine over a healthy link) is bucketed with `SerialError`/`SerialTimeoutError` under one `"Communication error"` log line. Raised at `:282`/`:315`. Fix lands in **Phase 42 (ERR-01)** by splitting the `except` clause. *(Operator-reported: "app always reports that the communication is broken when the hw returns an error.")* This replaces the former `COMMAND_FW_VERSION` item.
- **D-09:** `COMMAND_FW_VERSION` is **NOT missing** — it exists at `constants.py:39` (`= 13`). Drop the "missing constant" framing. Fold the `COMMAND_FW_VERSION` check into the **TEST-04** firmware-parity assertion (verify `== firestarter.h` literal). Phase 39's DATA-04 "add if missing" reduces to "verify present (it is)."
- **D-10:** Bug-test mechanism = `pytest.mark.xfail(strict=True)` asserting corrected behavior, so each test auto-flips to XPASS when the fix lands (and `strict` fails the suite if the behavior is already correct, catching premature/accidental fixes). Each test carries a `# BUG:` marker citing its fix phase.

### Firmware-Contract Parity (TEST-04)
- **D-11:** Extend the existing `tests/test_revision_constants_parity.py` pattern (hard-coded hex literals matching `firestarter/include/firestarter.h`) to also cover all `COMMAND_*`, `FLAG_*`, and `CTRL_*` blocks (currently only `REVISION_*`). Includes the `COMMAND_FW_VERSION` assertion (per D-09). `skipif` when the firmware checkout is absent — this is a **host-only** milestone and the firmware sub-repo may not be present in CI.

### Serial Frame-Parse Characterization (TEST-02)
- **D-12:** Use the existing `BytesIO` `fake_serial`/`make_comm` fixtures (`tests/conftest.py`). Pin the `_read_and_parse_lines` preamble→body→terminator sequence + a delayed-response test asserting the **sliding-window timeout resets on every yield** (invariant documented inline in the test). `_read_and_parse_lines` is **NOT modified** — it is ring-fenced for the v1.9 Read-Bug RCA (GATE-1.8(d); Phase 40 stamps it `DO NOT MODIFY`). Timeout simulation feeds empty reads (`b''`) between yields to exercise the window without real wall-clock delays (exact technique — virtual-time monkeypatch vs trickle-feed — is planner's discretion).

### Claude's Discretion
- Exact test-file naming/organization; the precise port-auto-discovery neutralization mechanism (D-05b); the timeout-simulation technique (D-12); whether to add `click` as a test dep now (only needed once `CliRunner` is used at Phase 41 — syrupy + subprocess do not need it in Phase 36).
- Phase 36 acceptance is: `pytest` exits 0 (existing + new suites), and `ruff`/`mypy` run **without configuration errors** (violations recorded as a baseline watermark, NOT fixed — that's Phase 37).
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & locked milestone decisions
- `.planning/ROADMAP.md` — v1.8 section, Phase 36 detail (lines 47–59): goal + 5 success criteria; also the GATE-1.8 (a–e) standing gate.
- `.planning/REQUIREMENTS.md` — TEST-01…TEST-05 (lines 26–30): locked requirements.
- `.planning/PROJECT.md` — "Current Milestone: v1.8" + "Scope decisions (locked 2026-05-27)": GATE-1.8 = "refactor + fix bugs found", Click target, flat layout, ruff+ruff-format+mypy, tests-first, host-only, the two latent bugs.
- `.planning/STATE.md` — "v1.8 Decisions" block (esp. the two-latent-bugs and spaghetti-hotspots notes).

### App architecture & code (firestarter_app sub-repo)
- `firestarter_app/CLAUDE.md` — app data flow + constants↔firmware sync contract. **NOTE: the "main.py — Click CLI entry point" line is aspirational/target-state; the CLI is `argparse` today.**
- `firestarter_app/firestarter/main.py` — `:495-510` `build_arg_flags` (bug at `:497`) + the 418-line `main()` dispatcher; `:513` argparse; `:589` builds the `db_instance` and threads it.
- `firestarter_app/firestarter/eprom_operations.py` — `:236-267` `_run_state_machine` (comm-error conflation at `:265-267`); `:282`/`:315` `EpromOperationError` raises.
- `firestarter_app/firestarter/serial_comm.py` — `:670-700` `get_response`/`expect_ack` (ERROR handled correctly here); `:760-782` `_list_potential_ports` (auto-discovery appends ports even with `-p`); `_read_and_parse_lines` (RING-FENCED for v1.9 — do not modify).
- `firestarter_app/firestarter/database.py` — `:157-205` `EpromDatabase` singleton (`__new__`/`_initialized` guard `:165-181`; `__init__` + user-override merge `:193-195`); `:613` `get_eprom_details` helper.
- `firestarter_app/firestarter/constants.py` — `:39` `COMMAND_FW_VERSION = 13` (present); `COMMAND_*`/`FLAG_*`/`CTRL_*`/`REVISION_*` blocks (TEST-04 targets).
- `firestarter_app/firestarter/data/chip_database.json` — real DB data for TEST-03.
- `firestarter_app/pyproject.toml` — `[project.optional-dependencies].test` (add syrupy); `[tool.pytest.ini_options]`.

### Existing test infrastructure (the patterns to reuse/extend)
- `firestarter_app/tests/conftest.py` — `fake_serial`, `make_comm`, `build_frame`, `_ref_crc8_ccitt` fixtures (TEST-01 happy-paths + TEST-02).
- `firestarter_app/tests/test_revision_constants_parity.py` — the exact parity pattern TEST-04 extends.
- `firestarter_app/tests/test_decoder.py` — existing decoder tests; must continue to pass unchanged.

### Firmware source-of-truth (other sub-repo; skipif when absent)
- `firestarter/include/firestarter.h` — authoritative `COMMAND_*`/`FLAG_*`/`CTRL_*` literals for the TEST-04 parity assertions.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/conftest.py` fixtures (`fake_serial` BytesIO stand-in, `make_comm` factory that bypasses real serial via `__new__`, `build_frame`, table-free reference CRC) — directly serve TEST-01 happy-paths and TEST-02.
- `tests/test_revision_constants_parity.py` — copy-and-extend template for TEST-04 (hard-coded hex literals + cross-repo invariant docstring).
- A live pytest suite already exists (landed "Phase 6 Plan 03"). **`.planning/codebase/TESTING.md` is STALE** — it claims "no Python tests" because it was generated from an old source path (`/home/henrik/...`); ignore that claim.

### Established Patterns
- `EpromDatabase` is a `__new__`-based singleton, BUT call sites already accept an injected `db_instance` (constructors of `EpromInfo`/`ChipLayout`; `main()` threads one down) — so removing the guard is low-risk (D-06).
- Constants↔firmware sync contract: `constants.py` mirrors `firestarter/include/firestarter.h` / `rurp_pinout.h` / `rurp_shield.h`; parity tests enforce it at pytest time (TEST-04 widens this).
- Three-phase serial state machine (INIT→MAIN→END); ERROR responses are legitimate, parseable, and arrive over a healthy link (key to the D-08.2 bug).

### Integration Points
- `pyproject.toml` test deps + pytest config (add syrupy; add new test modules).
- `tests/` directory (new: `test_characterization.py`, `test_decoder_characterization.py` or equiv, `test_eprom_database.py`; extend the parity test).
- CI workflow is touched in **Phase 37** (the ruff/ruff-format/mypy + coverage gate), NOT Phase 36 — here ruff/mypy only need to *run without config errors*.
</code_context>

<specifics>
## Specific Ideas

- Operator's concrete pain point driving the comm-error work: **"app always reports that the communication is broken when the hw returns an error."** The fix must make a firmware-reported operational error surface as such (with the firmware's own message), distinct from a true transport failure. Confirmed cause: `eprom_operations.py:265` lumping `EpromOperationError` with `SerialError`/`SerialTimeoutError`.
</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

**Sequencing note (not deferrals):** the two bug *fixes* are characterized here but applied later by design — `build_arg_flags` → Phase 41 (CLI-03); comm-error vs operational-error split → Phase 42 (ERR-01). The xfail-strict tests (D-10) bind those phases to this safety net.
</deferred>

---

*Phase: 36-Characterization Test Baseline*
*Context gathered: 2026-05-27*

# Phase 23: Host CLI Installer Integration - Context

**Gathered:** 2026-05-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the host CLI (`firestarter_app/firestarter/`) work end-to-end for `uno328pb`-reporting devices:
- `firestarter fw -i` resolves and flashes `firestarter_uno328pb.hex` from the latest stable release
- `firestarter fw -i --pre` resolves and flashes `firestarter_uno328pb.hex` from the highest PEP 440 pre-release
- `firestarter firmware list` enumerates `uno328pb` releases with the same plain-text/JSON shape as for `uno`/`leonardo`
- Existing `uno`/`leonardo` flash paths remain byte-identical (GATE-01 non-regression)

**What this phase does NOT do:**
- Real-silicon flash verification (Phase 24 bench validation — BENCH-01)
- A first real beta cut from `firestarter/beta` to produce a `uno328pb` asset (Phase 24)
- Documentation updates (Phase 25 — DOC-01, DOC-02)

**Architecture insight (v1.4 already board-parameterized most paths):**
The v1.4 INST-04 work (Phase 18) already generalized `fetch_release_info(board=...)`, `list_releases(board=...)`, the asset-name resolver `firestarter_${board}.hex`, and the CLI's board-driven dispatch. The ONLY place Phase 23 needs to add a `uno328pb` branch is `firmware.py:_install_with_avrdude` (lines 417-423), which still has hard-coded `uno`/`leonardo` branches for AVR partno + programmer_id + baud_rate. Everything else is already generic on `board: str`.

</domain>

<decisions>
## Implementation Decisions

### avrdude profile for uno328pb (the load-bearing edit)
- **D-01: Add a `uno328pb` branch to `firestarter_app/firestarter/firmware.py:_install_with_avrdude` (currently lines 405-423).** The branch sits as `elif board.lower() == "uno328pb":` between the existing `if board.lower() == "leonardo":` and the implicit `uno` default. Set `partno, programmer_id, baud_rate = ("atmega328pb", "arduino", 115200)`.
- **D-02: Programmer_id = `"arduino"`, NOT `"urclock"`.** Rationale: MiniCore's stock bootloader for ATmega328PB CAN be either Urclock OR optiboot/arduino-protocol depending on what the operator's specific board ships with. The `arduino` programmer_id mirrors the existing `uno` profile (which works with optiboot's stk500v1-style protocol) and is the safer default for an "Arduino Uno-compatible pin mapping" board (Phase 21 CONTEXT D-01). If Phase 24 bench validation reveals the operator's specific 328PB-Uno needs `urclock` instead, that's a single-line change — documented as a Phase 24 hand-off finding, not a Phase 23 design uncertainty.
- **D-03: `partno = "atmega328pb"` exactly.** avrdude's `-p` flag accepts `atmega328pb` (case-insensitive) per avrdude.conf v7.x. Test fixtures should NOT use `atmega328p` — that's the 328P, signature `0x1E 0x95 0x0F`, which mismatches the 328PB's `0x1E 0x95 0x16` and would cause avrdude to abort (the failure mode Phase 21 CONTEXT D-10 explicitly called out).
- **D-04: `baud_rate = 115200`.** Same as `uno` (also 115200) — the optiboot/stk500v1 baud on Arduino Uno is 115200; the 328PB's bootloader inherits this unless explicitly reconfigured. Phase 24 bench will validate.

### Test surface
- **D-05: Extend `firestarter_app/tests/test_firmware_install.py` with `uno328pb` cases.** Follow the existing pattern: use `mock_releases_factory` helper + monkeypatch on `firmware.requests.get`. Add at least 3 new test cases:
  1. `test_uno328pb_stable_path_resolves_correct_asset` — mocked stable release with all three `firestarter_*.hex` assets; assert `fetch_release_info(channel="stable", board="uno328pb")` returns the `uno328pb_stable.hex` URL.
  2. `test_uno328pb_pre_path_resolves_highest_prerelease` — mocked pre-release ladder; assert `fetch_release_info(channel="pre", board="uno328pb")` picks the highest PEP 440 pre-release.
  3. `test_uno328pb_list_releases_enumerates_correctly` — assert `list_releases(board="uno328pb")` returns the same shape as for uno/leonardo.
- **D-06: Add ONE avrdude profile resolution test** that mocks `Avrdude(...)` and asserts `_install_with_avrdude(board="uno328pb")` passes `partno="atmega328pb"`, `programmer_id="arduino"`, `baud_rate=115200` to the constructor. This guards D-01..D-04 against silent regression. If `test_firmware_install.py` is the wrong home for this (it's release-resolution-focused), create a sibling test method in the same file.
- **D-07: Do NOT touch existing `uno`/`leonardo` test cases.** GATE-01 non-regression is enforced by running the WHOLE pytest suite before and after — every existing test must remain green with the same assertions. If a refactor of `_install_with_avrdude` would naturally change existing tests, the refactor is too invasive — keep the `if board.lower() == "leonardo": ... elif board.lower() == "uno328pb": ... else (uno default): ...` form so existing branches are syntactically unchanged.

### What does NOT need to change (negative scope)
- **D-08: `constants.py` requires NO edits.** A grep across `firestarter_app/firestarter/constants.py` returns zero references to `uno`/`leonardo`/`board` — there is no board enum or allowlist. The code is duck-typed on the `board: str` parameter, which the v1.4 INST-04 work already plumbed end-to-end. No allowlist add.
- **D-09: `avr_tool.py` requires NO edits.** It's a thin wrapper around the avrdude subprocess; the partno/programmer/baud get passed in by `_install_with_avrdude` (now D-01). avr_tool.py itself doesn't branch on board.
- **D-10 (REVISED 2026-05-21 after research): `main.py` requires ONE narrow allowlist edit.** Research finding: `main.py:288-291` declares `choices=["uno", "leonardo"]` for the `-b/--board` argparse argument. The install path uses the device-handshake `current_board` (overrides `args.board`), so `firestarter fw -i` on a uno328pb-reporting device works without the widening — but `firestarter firmware list --board uno328pb` is rejected by argparse before any handshake runs. Per REQUIREMENTS.md INST language "Any allowlist entry needed (e.g. in `avr_tool.py` upload profile or `constants.py` enum) is added" — the "e.g." is explicitly non-exhaustive; `main.py --board choices` is another allowlist surface. **Resolution:** widen the `choices=` tuple from `["uno", "leonardo"]` to `["uno", "uno328pb", "leonardo"]` (matching Phase 21 D-08 section-order discipline). This is a 1-line edit; no new flag added, no help text rewrite, no architectural change. ROADMAP SC#3 + INST-03 "no new flags" remain honored. The original D-10 prediction (no main.py edits) was too conservative — research revealed the contradiction.
- **D-11: `serial_comm.py` requires NO edits.** Handshake parsing (`FW: <version>:<board>`) is already board-string-generic (line 112: `board_name = parts[1].strip()`). Phase 21 firmware emits `<board> = "uno328pb"`; the host already correctly extracts it.
- **D-12: NO firmware sub-repo edits.** Phase 23 is HOST-ONLY. `firestarter/` (firmware sub-repo) stays untouched at its Phase 22 state (HEAD `897067b` on `v1.5-uno328pb`).
- **D-13: NO meta-repo edits beyond CONTEXT/RESEARCH/VALIDATION/PLAN/SUMMARY/VERIFICATION/ROADMAP/STATE.** No new requirements added, no new files outside `.planning/phases/23-*/`.

### Verification scope
- **D-14: Verification = full pytest suite green.** `cd firestarter_app && python -m pytest tests/ -v` must exit 0 with N+M cases passing (existing N + new M). Plus a confirmation that the new uno328pb cases each FAIL when D-01's branch is reverted (TDD-style sanity — they actually test the branch they claim to test).
- **D-15: NO hardware flash in Phase 23.** Real-silicon flash deferred to Phase 24 (BENCH-01). Phase 23 ships when the mocked-GitHub-API pytest suite is green. The Phase 21 CONTEXT D-10 prediction ("Phase 23 INST-01 SC#1 must add the branch") and Phase 24's BENCH-01 acceptance ("operator runs `firestarter fw -i --pre` connected to the 328PB-Uno + RURP shield") together form the proof chain — Phase 23 lands the code; Phase 24 confirms it works on real silicon.
- **D-16: GATE-01 non-regression command** — `cd firestarter_app && python -m pytest tests/test_firmware_install.py -v -k "not uno328pb"` must exit 0 with the same case count as pre-Phase-23 (the test count is observable via `git diff` against the pre-edit tree).

### Edit surface summary
- **D-17 (REVISED 2026-05-21): Phase 23 edits exactly 3 files in the host CLI sub-repo:**
  - `firestarter_app/firestarter/firmware.py` (1 elif branch in `_install_with_avrdude`)
  - `firestarter_app/firestarter/main.py` (1-line widening of `-b/--board` argparse `choices=` per revised D-10)
  - `firestarter_app/tests/test_firmware_install.py` (4 new test methods: 3 release-resolution + 1 avrdude-profile). Optionally add a 5th test asserting `argparse` accepts `--board uno328pb` without erroring (covers the D-10 widening).
- **D-18: NO `firestarter_app/setup.py`, `firestarter_app/pyproject.toml`, README, or documentation edits.** Phase 25 owns docs.

### Branching / commits / push
- **D-19: All commits land on `v1.5-uno328pb` in the host CLI sub-repo** (`/workspaces/firestarter_app/` — currently on this branch since the Phase 21 branching remediation). Meta-repo commits (CONTEXT/PLAN/SUMMARY/VERIFICATION/STATE/ROADMAP) land on `v1.5-uno328pb` in `/workspaces/`.
- **D-20: No remote push.** Same as Phase 21 + Phase 22 — `v1.5-uno328pb` stays local until milestone close (post-Phase-25 merge-up).

### Claude's Discretion
- Whether to split D-01 (avrdude branch) and D-05/D-06 (tests) into one plan or two (single-edit-surface argues one plan with two waves: tests as RED Wave 1, code as GREEN Wave 2 if TDD discipline desired; or single wave with both atomic if speed preferred).
- Whether the TDD RED/GREEN sequence is enforced (TDD_MODE is currently `false` in config — so no TDD enforcement, but the planner can still choose this shape if helpful).
- Test method placement (new test class vs sibling methods in existing classes in `test_firmware_install.py`).
- Wording of the elif branch's inline comment (cite Phase 21 D-10 hand-off if at all).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` lines 34-36 — INST-01 (stable install), INST-02 (--pre install), INST-03 (firmware list) acceptance criteria.
- `.planning/REQUIREMENTS.md` line 42 — GATE-01 non-regression contract (uno/leonardo flash paths byte-identical post-v1.5).

### Locked decisions from Phase 21 that govern Phase 23
- `.planning/phases/21-firmware-target-uno328pb/21-CONTEXT.md` **D-10** — explicit HAND-OFF to Phase 23 INST-01 with the exact line range (`firestarter_app/firestarter/firmware.py:417-423`) and the explicit warning that the 328P/328PB signature mismatch (`0x1E 0x95 0x0F` vs `0x1E 0x95 0x16`) makes the host-side branch addition mandatory.

### Host CLI v1.4 INST-04 substrate (already board-parameterized)
- `firestarter_app/firestarter/firmware.py` `fetch_release_info(board=...)` line ~216 — board-driven asset resolver (D-15 back-compat shim into `fetch_latest_release_info`).
- `firestarter_app/firestarter/firmware.py` `list_releases(board=...)` line ~307 — board-driven release enumerator.
- `firestarter_app/firestarter/firmware.py` `check_current_firmware()` lines 86-117 — handshake parser that extracts the `board` string from `FW: <version>:<board>`. Already generic.
- `firestarter_app/firestarter/firmware.py:_install_with_avrdude` lines 405-423 — THE edit target. Current implementation hard-codes uno (default) + leonardo branches; Phase 23 adds the uno328pb branch.
- `firestarter_app/firestarter/main.py` — CLI dispatch. Already board-driven. No edits (D-10).

### Test scaffolding (extend, don't refactor)
- `firestarter_app/tests/test_firmware_install.py` — v1.4 Phase 18 RED-gate scaffold for INST-01..04. Uses `mock_releases_factory()` + `monkeypatch.setattr(firmware.requests, "get", ...)`. Existing classes parameterize on board strings; the new uno328pb cases follow the same pattern.
- `firestarter_app/tests/conftest.py` — shared fixtures. NOT edited (D-12 — wait, that says "no firmware sub-repo edits"; conftest is in tests/ and is fair game per D-17 if needed, but D-05's plan uses module-local helpers per the existing test file's convention).

### Project / state
- `.planning/STATE.md` — v1.5 progress; Phases 21 + 22 SHIPPED.
- `.planning/PROJECT.md` — GATE-01 invariant.
- `/workspaces/CLAUDE.md` — repo layout (host CLI at `firestarter_app/`, firmware at `firestarter/`, both submodules of meta-repo).
- Memory `feedback-branching-firestarter-milestones` — all 3 repos on `v1.5-uno328pb`; no remote push from milestone phases.
- Memory `user-firestarter-repo-layout` — `firestarter_app` is the Python pip package; tests use pytest; runs as `python -m pytest tests/`.

### Phase 24 hand-off (BENCH-01)
- `.planning/REQUIREMENTS.md` line 48 — BENCH-01 acceptance: "operator runs `firestarter fw -i --pre` connected to the 328PB-Uno + RURP shield. The host installs `firestarter_uno328pb.hex` from the pre-release asset, `avr_tool.py` reports a clean flash, and the device reboots into the v1.5 firmware." This is the proof Phase 23's D-01 actually works on real hardware; Phase 23 itself is mocked-only.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`mock_releases_factory(releases, next_url=None)`** at `firestarter_app/tests/test_firmware_install.py` line ~38 — MagicMock factory producing GitHub `/releases` response shape with optional pagination link header. Reuse verbatim for new uno328pb cases.
- **`mock_404_response()`** at line ~52 — for negative-path tests (board asset missing from release).
- **Existing parameterized fixtures** for stable + pre-release ladders (e.g. `_STABLE_RELEASE_LEONARDO`, `_PRE_RELEASES_*`) — copy the pattern with uno328pb names.
- **`check_current_firmware()` handshake parser** at `firestarter_app/firestarter/firmware.py:101-117` — already extracts `board_name` from `"FW: <version>:<board>"`. Phase 21 firmware emits `<board>="uno328pb"`; the host receives it without modification.

### Established Patterns
- **Board-driven asset resolver** (v1.4 INST-04, `fetch_release_info`): callers pass `board="X"`; the resolver computes `f"firestarter_{board}.hex"` and finds the matching asset in the release's `assets[]` list. The CLI never hard-codes board names — it gets them from `check_current_firmware()`. Phase 23's D-01 fits this pattern by adding the missing AVR-side branch that maps the board string to avrdude parameters.
- **`if board.lower() == "X": ... elif: ... else (uno default)` structure** in `_install_with_avrdude` — Phase 23 extends this exact structure with a `uno328pb` elif branch. Do NOT refactor to a dict lookup or registry — that's a v1.6+ improvement, not Phase 23's job (would also perturb GATE-01 line-level diff and risk breaking the existing branches).
- **Mocked GitHub API in tests** (`monkeypatch.setattr(firmware.requests, "get", ...)`) — every test in `test_firmware_install.py` follows this pattern. No network in tests.

### Integration Points
- **Phase 22 substrate enables Phase 23 mocked tests today.** The release-asset glob in `build.yml`/`beta-build.yml` (verified by Phase 22) means a real `uno328pb` asset WILL exist after Phase 24's first beta cut. Phase 23's mocked tests use fake URLs (`https://example.com/uno328pb_*.hex`) — they don't require a real GitHub release. So Phase 23 can land before Phase 24 with no chicken-and-egg.
- **Phase 21 firmware emits the `uno328pb` board string in handshake.** Phase 23's host code receives it via `check_current_firmware()` line 112 → routes to `_install_with_avrdude(board="uno328pb")` → hits the new D-01 elif branch → invokes avrdude with `-p atmega328pb -c arduino -b 115200`.
- **Phase 24 proves the wiring on real silicon.** If Phase 24 finds `programmer_id="arduino"` fails on the operator's specific bootloader (e.g., MiniCore-flashed with Urclock), the fix is a one-line edit in `_install_with_avrdude` — swap `"arduino"` → `"urclock"`. Documented as a known contingency; not a Phase 23 risk to over-engineer.

</code_context>

<specifics>
## Specific Ideas

- The TDD RED→GREEN shape (write the 4 new failing tests first, THEN add the elif branch) is appealing because the elif branch is small and a regression in `_install_with_avrdude` would otherwise be silently caught only at Phase 24 bench time. If `TDD_MODE` were enabled in config, the planner would apply it automatically; since it's not, the planner can opt in for THIS phase via task structure (Wave 1 = RED tests, Wave 2 = GREEN code) without flipping the global TDD flag.
- The avrdude profile resolution test (D-06) is the most valuable single test — it pins partno + programmer_id + baud_rate as a contract. If any future refactor changes the dict/branch structure, this test fails loudly.

</specifics>

<deferred>
## Deferred Ideas

- **Real-silicon flash of `firestarter_uno328pb.hex`** — Phase 24 (BENCH-01) owns this. Phase 23 verifies via mocked GitHub API only.
- **`urclock` fallback if `arduino` programmer_id fails** — a Phase 24 finding (if it happens) becomes a 1-line follow-up commit on `v1.5-uno328pb` in `firestarter_app/`. Not a Phase 23 task.
- **Refactor `_install_with_avrdude` to a dict-based registry** — defer to v1.6+ when a fourth board joins. Three branches is below the "abstract me" threshold per Phase 21 D-02 reasoning (same "no umbrella macro" principle).
- **CLI documentation update mentioning the third board** — Phase 25 (DOC-01, DOC-02) owns README updates.
- **`firestarter_app/setup.py` or `pyproject.toml` metadata bump** — Phase 24 bench validation triggers the milestone version bump; Phase 23 leaves package metadata untouched.
- **avrdude.conf shipping with the package** — outside scope. Operators install avrdude via OS package manager.

</deferred>

---

*Phase: 23-host-cli-installer-integration*
*Context gathered: 2026-05-21 via /gsd-discuss-phase --auto (auto-mode single-pass; recommended options applied)*
*Auto-resolved gray areas: avrdude profile values (D-01..D-04), test surface scope (D-05..D-07), negative scope (D-08..D-13), verification gate (D-14..D-16), edit surface (D-17..D-18), branch convention (D-19..D-20)*
*Key contingency: D-02 (`programmer_id="arduino"`) is Phase 24-bench-validated. If wrong, 1-line swap to `"urclock"` on `v1.5-uno328pb` in firestarter_app.*

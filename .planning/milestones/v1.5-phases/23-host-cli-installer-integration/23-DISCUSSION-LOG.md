# Phase 23 Discussion Log

**Mode:** `/gsd-discuss-phase 23 --auto`
**Date:** 2026-05-21
**Pass count:** 1 (single-pass per auto-mode cap)

## Auto-resolved gray areas

The auto-mode flow identified six gray areas. Each was resolved using the recommended option (no AskUserQuestion calls; recommendations grounded in Phase 21 D-10 hand-off, v1.4 INST-04 substrate, and live codebase scout).

### 1. avrdude profile values for uno328pb
- **Question:** What `(partno, programmer_id, baud_rate)` triple should `_install_with_avrdude` use for `board="uno328pb"`?
- **Options surfaced:**
  - Recommended: `("atmega328pb", "arduino", 115200)` — mirrors uno (which uses `"arduino"` + 115200) but with 328PB partno
  - Alternative A: `("atmega328pb", "urclock", 115200)` — MiniCore's default Urclock bootloader programmer_id
  - Alternative B: `("atmega328pb", "stk500", 115200)` — generic stk500v1
- **Selection:** `("atmega328pb", "arduino", 115200)` (D-01..D-04)
- **Reason:** The operator's `uno328pb` board is "Arduino Uno-compatible pin mapping" (Phase 21 CONTEXT D-01). `arduino` programmer_id works with optiboot/stk500v1-style bootloaders — the most likely shipped bootloader. If Phase 24 bench validation reveals the specific board uses Urclock, a 1-line swap on `v1.5-uno328pb` fixes it. The safer default is the one that matches the existing `uno` shape, since the 328PB is an "Uno-compatible" variant.

### 2. Test surface for uno328pb
- **Question:** Should `tests/test_firmware_install.py` get new uno328pb cases as a new test class, sibling methods in existing classes, or a separate `test_firmware_install_uno328pb.py` file?
- **Options surfaced:**
  - Recommended: Extend in-place with sibling methods + 1 new class for the avrdude-profile resolution test (D-05, D-06)
  - Alternative: Separate file for uno328pb
- **Selection:** In-place extension (D-05)
- **Reason:** The v1.4 INST-04 test file (`test_firmware_install.py`) is already board-parameterized via `mock_releases_factory` — adding uno328pb cases is a 1-line factory-call delta per test. A new file would duplicate the fixture-loading machinery and confuse the "where do INST tests live" question.

### 3. GATE-01 non-regression guard
- **Question:** How is "existing uno/leonardo flash paths remain byte-identical" verified in a unit-test-only phase?
- **Options surfaced:**
  - Recommended: Run the full pytest suite before and after the edits; existing uno/leonardo tests must remain green with the same assertions (D-07, D-16)
  - Alternative: Add a separate `tests/test_gate01.py` with explicit byte-comparison fixtures
- **Selection:** Full-suite non-regression (D-07, D-16)
- **Reason:** GATE-01 is a behavioral invariant; the existing test suite already encodes the behavior. Adding a dedicated byte-comparison test would only catch silent regressions in `_install_with_avrdude`'s elif structure — which D-07's "do not refactor existing branches" rule already prevents.

### 4. Constants/allowlist edits
- **Question:** Does `constants.py` need a board enum entry for `uno328pb`?
- **Options surfaced:**
  - Recommended: No edit (D-08) — verified by grep that `constants.py` has NO board enum or allowlist
  - Alternative: Add a `BOARD_UNO328PB` constant defensively
- **Selection:** No edit (D-08)
- **Reason:** `grep -n "uno\|leonardo\|board" firestarter_app/firestarter/constants.py` returns 0 hits. The code is duck-typed on `board: str`. Adding a constant would create dead code.

### 5. Hardware flash in Phase 23
- **Question:** Should Phase 23 attempt a real-silicon flash, or limit verification to mocked-GitHub-API unit tests?
- **Options surfaced:**
  - Recommended: Mocked unit tests only; defer real-silicon to Phase 24 BENCH-01 (D-15)
  - Alternative: Attempt a real flash if the operator's 328PB-Uno is plugged in
- **Selection:** Mocked only (D-15)
- **Reason:** Phase 24's BENCH-01 acceptance explicitly says "operator runs `firestarter fw -i --pre` connected to the 328PB-Uno" — that IS the real-silicon proof. Phase 23 ships when unit tests are green; Phase 24 confirms on hardware. This matches the v1.4 Phase 18 (host-side) → Phase 20 (E2E smoke) split.

### 6. Branch / push behavior
- **Question:** Where do Phase 23 commits land, and do we push to remote?
- **Options surfaced:**
  - Recommended: All commits on `v1.5-uno328pb` in both `firestarter_app/` and meta-repo; NO remote push (D-19, D-20)
  - Alternative: Push `firestarter_app/v1.5-uno328pb` to origin as a backup
- **Selection:** Local-only (D-19, D-20)
- **Reason:** Consistent with Phase 21 + Phase 22 + memory `feedback-branching-firestarter-milestones`. Milestone work stays local until milestone close.

## Folded todos

None — no `.planning/todos/pending/*.md` entries with `resolves_phase: 23`.

## Reviewed but not folded

None.

## Deferred ideas

All captured in CONTEXT.md `<deferred>` block:
- Real-silicon flash → Phase 24 BENCH-01
- `urclock` swap if `arduino` fails → 1-line follow-up if Phase 24 surfaces it
- `_install_with_avrdude` dict-registry refactor → v1.6+ when a 4th board joins
- README updates → Phase 25 DOC-01/DOC-02
- Package metadata bump → Phase 24 milestone trigger
- avrdude.conf shipping → out of scope

## Claude's discretion items

Four items left to the planner's judgment:
1. Single plan vs two-wave (RED tests then GREEN code) — TDD_MODE is off in config but the planner can opt in per-phase
2. Whether to use `pytest.mark.parametrize` to fold uno/leonardo/uno328pb into a single test (less code, but perturbs existing test methods → risk to GATE-01 non-regression) — prefer NOT
3. Test method placement (which existing class to extend)
4. Inline comment wording near the elif branch (cite Phase 21 D-10 hand-off optional)

## Scope creep redirected

None encountered — every gray area resolution stayed inside the Phase 23 boundary (host CLI install + release-resolution + 1 avrdude branch + tests).
